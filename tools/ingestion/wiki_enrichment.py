import json
import os
import logging
import time
import re
import requests
import csv
from tqdm import tqdm

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/11_external_densification")
OUTPUT_DIR = os.path.normpath("./tools/data/12_wiki_enrichment")
LOG_DIR = "./tools/logs"

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[logging.FileHandler(f"{LOG_DIR}/wiki_enrichment.log", mode='a', encoding='utf-8')]
)
logger = logging.getLogger("WikiEnricher")

class WikiEnricher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChemicalDataBot/2.2 (internal-research; contact@example.com)'
        })
        self.api_url = "https://en.wikipedia.org/w/api.php"

        self.stats = {
            "processed": 0, "hits": 0, "desc_added": 0,
            "history_added": 0, "synonym_rescues": 0, "rejected": 0, "errors": 0
        }

        # Open CSV in append mode ('a') so we don't wipe previous logs on resume
        file_exists = os.path.isfile(f"{LOG_DIR}/wiki_enrichment_details.csv")
        self.csv_file = open(f"{LOG_DIR}/wiki_enrichment_details.csv", "a", newline="", encoding="utf-8")
        self.csv_writer = csv.writer(self.csv_file)
        if not file_exists:
            self.csv_writer.writerow(["Filename", "Compound", "Search_Method", "Page_Title", "Status", "Desc_Added", "Story_Len"])

    def clean_text(self, text):
        if not text: return None
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def get_wiki_page(self, query):
        params = {"action": "query", "list": "search", "srsearch": query, "format": "json", "srlimit": 1}
        try:
            time.sleep(0.2)
            resp = self.session.get(self.api_url, params=params, timeout=5)
            data = resp.json()
            if data.get("query", {}).get("search"):
                return data["query"]["search"][0]["title"]
        except: return None
        return None

    def get_page_content(self, title):
        params = {
            "action": "query", "prop": "extracts|revisions", "exintro": True,
            "rvprop": "content", "rvslots": "main", "titles": title,
            "format": "json", "redirects": 1
        }
        try:
            resp = self.session.get(self.api_url, params=params, timeout=5)
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            page_id = next(iter(pages))
            if page_id == "-1": return None

            page_data = pages[page_id]
            summary = self.clean_text(page_data.get("extract", ""))

            full_text = ""
            revisions = page_data.get("revisions", [])
            if revisions:
                full_text = revisions[0].get("slots", {}).get("main", {}).get("*", "")

            return {
                "title": page_data["title"], "summary": summary,
                "full_text": full_text, "url": f"https://en.wikipedia.org/?curid={page_id}"
            }
        except: return None

    def validate_page(self, page_data, target_cas):
        title = (page_data["title"] or "").lower()
        summary = (page_data["summary"] or "").lower()
        full_text = page_data["full_text"] or ""

        # 1. Ban Lists/Categories
        if title.startswith("list of") or title.startswith("category:") or "disambiguation" in title:
            return False, "Is_List"

        # 2. Context Keywords
        CHEM_KEYWORDS = ["compound", "chemical", "formula", "substance", "acid", "drug", "medication", "protein", "enzyme", "polymer", "organic", "inorganic", "molecule"]
        if not any(kw in summary for kw in CHEM_KEYWORDS):
            return False, "No_Context"

        # 3. CAS Verification
        if target_cas:
            cas_simple = target_cas.replace("-", "")
            if target_cas not in full_text and cas_simple not in full_text:
                return False, "CAS_Mismatch"

        return True, "Valid"

    def mine_history(self, full_text):
        info = {"discoverer": None, "year": None, "story": None}
        if not full_text: return info

        history_match = re.search(r'==\s*(History|Discovery|Synthesis|Background).*?==\n(.*?)(?===)', full_text, re.DOTALL | re.IGNORECASE)
        section_text = ""

        if history_match:
            section_text = history_match.group(2)
            clean_section = re.sub(r"''+", "", section_text)
            clean_section = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", clean_section)
            clean_section = self.clean_text(clean_section)

            if clean_section:
                paragraphs = [p for p in clean_section.split('\n') if len(p) > 50]
                if paragraphs:
                    info["story"] = paragraphs[0]

        search_blob = section_text if section_text else full_text[:2500]

        who_match = re.search(r'discovered by (?:the )?(?:\[\[)?([A-Z][a-z\.]+ [A-Z][a-z\.]+)', search_blob)
        if who_match:
            name = who_match.group(1)
            if "French" not in name and "German" not in name:
                info["discoverer"] = name

        year_match = re.search(r'(first|was) (isolated|discovered|synthesized|prepared).*?(\d{4})', search_blob, re.IGNORECASE)
        if year_match:
            info["year"] = int(year_match.group(3))

        return info

    def process_file(self, filename, pbar):
        try:
            filepath = os.path.join(INPUT_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            root = data if "identity" in data else data.get("compound", {})
            ident = root.setdefault("identity", {})
            history = root.setdefault("history", {})
            refs = root.setdefault("cross_references", {})

            # --- FIX: SAFE GETTERS ---
            # Ensure these are strings/lists, never None
            compound_name = ident.get("name") or "Unknown"
            target_cas = ident.get("cas_rn") or ""
            synonyms = ident.get("synonyms") or []

            page_data = None
            search_method = "None"

            # --- STRATEGY ---
            if refs.get("wikipedia") and "wiki" in refs.get("wikipedia", ""):
                match = re.search(r"wiki/(.+)$", refs["wikipedia"])
                if match:
                    title = match.group(1).replace("_", " ")
                    page_data = self.get_page_content(title)
                    search_method = "URL"

            if not page_data and compound_name != "Unknown":
                title = self.get_wiki_page(compound_name)
                if title:
                    page_data = self.get_page_content(title)
                    search_method = "Name"

            if not page_data and synonyms:
                for syn in synonyms[:4]:
                    if len(syn) < 4: continue
                    title = self.get_wiki_page(syn)
                    if title:
                        page_data = self.get_page_content(title)
                        if page_data:
                            search_method = f"Syn: {syn}"
                            self.stats["synonym_rescues"] += 1
                            break

            # --- VALIDATE & UPDATE ---
            excerpts = []
            status = "No_Page"

            if page_data:
                is_valid, reason = self.validate_page(page_data, target_cas)
                status = reason

                if is_valid:
                    self.stats["hits"] += 1
                    refs["wikipedia"] = page_data["url"]

                    # Desc
                    current_desc = ident.get("description", "")
                    if (not current_desc or len(current_desc) < 50) and page_data["summary"]:
                        ident["description"] = page_data["summary"]
                        self.stats["desc_added"] += 1
                        snippet = (page_data["summary"][:75] + '...') if len(page_data["summary"]) > 75 else page_data["summary"]
                        excerpts.append(f"   + Desc:  {snippet}")

                    # History
                    hist_info = self.mine_history(page_data["full_text"])

                    if hist_info["year"] and not history.get("year"):
                        history["year"] = hist_info["year"]
                        excerpts.append(f"   + Year:  {hist_info['year']}")
                        self.stats["history_added"] += 1

                    if hist_info["discoverer"] and not history.get("discoverer"):
                        history["discoverer"] = hist_info["discoverer"]
                        excerpts.append(f"   + Who:   {hist_info['discoverer']}")

                    if hist_info["story"] and not history.get("discovery_story"):
                        history["discovery_story"] = hist_info["story"]
                        snippet = (hist_info["story"][:75] + '...') if len(hist_info["story"]) > 75 else hist_info["story"]
                        excerpts.append(f"   + Story: {snippet}")

                    if excerpts or search_method.startswith("Syn"):
                        # Safe slicing even if name is short
                        safe_name = compound_name if len(compound_name) <= 25 else compound_name[:25]
                        tqdm.write(f"✅ {safe_name:<25} | {search_method:<15}")
                        for line in excerpts:
                            tqdm.write(line)
                else:
                    self.stats["rejected"] += 1

            self.csv_writer.writerow([
                filename, compound_name, search_method,
                page_data["title"] if page_data else "N/A", status,
                "Yes" if "Desc" in str(excerpts) else "No",
                "N/A"
            ])

            pbar.set_postfix({
                "Hits": self.stats["hits"],
                "Syns": self.stats["synonym_rescues"],
                "Rej": self.stats["rejected"],
                "Err": self.stats["errors"]
            })

            with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            self.stats["processed"] += 1

        except Exception as e:
            self.stats["errors"] += 1
            # Log error but don't stop
            tqdm.write(f"❌ Error processing {filename}: {str(e)}")

    def run(self):
        all_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]

        # --- RESUME LOGIC ---
        existing_files = set(os.listdir(OUTPUT_DIR))
        files_to_process = [f for f in all_files if f not in existing_files]

        print(f"\n🚀 WIKI ENRICHMENT")
        print(f"   Total Files:   {len(all_files)}")
        print(f"   Already Done:  {len(existing_files)}")
        print(f"   To Process:    {len(files_to_process)}")
        print("---------------------------------------------------------------")

        if not files_to_process:
            print("All files processed! Exiting.")
            return

        with tqdm(files_to_process, unit="file") as pbar:
            for f in pbar:
                self.process_file(f, pbar)

        self.csv_file.close()
        print("\n---------------------------------------------------------------")
        print("DONE. Session Stats:")
        print(f"  Processed: {self.stats['processed']}")
        print(f"  Valid Pages Found: {self.stats['hits']}")
        print(f"  Pages Rejected: {self.stats['rejected']}")
        print(f"  Errors: {self.stats['errors']}")

if __name__ == "__main__":
    WikiEnricher().run()