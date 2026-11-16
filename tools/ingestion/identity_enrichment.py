import json
import os
import re
import logging
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, Tuple, List
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/01_cas_and_smiles_repair")
OUTPUT_DIR = os.path.normpath("./tools/data/02_identity_enrichment")
LOG_DIR = "./tools/logs"


# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/enrich_basis_wiki.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WikiBasisEnricher")

class WikiBasisEnricher:
    API_URL = "https://en.wikipedia.org/w/api.php"
    HEADERS = {'User-Agent': 'CurieosityBot/15.5 (BasisRepair+SmartValidation)'}

    # Keys that definitively prove this is a chemical page
    STRONG_CHEMICAL_KEYS = {
        "chemical formula", "formula", "molar mass", "molecular weight",
        "cas number", "iupac name", "systematic name", "drugbank",
        "pubchem", "smiles", "inchi", "density", "melting point",
        "boiling point", "atc code", "ec number"
    }

    def __init__(self):
        self.session = self._create_session()
        self.stats = {
            "processed": 0,
            "smiles_filled": 0,
            "cas_filled": 0,
            "formula_filled": 0,
            "desc_filled": 0,
            "synonyms_added": 0,
            "api_hit": 0,
            "garbage_rejected": 0
        }

    def _create_session(self):
        sess = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        sess.mount("https://", HTTPAdapter(max_retries=retry))
        sess.headers.update(self.HEADERS)
        return sess

    # --- HELPERS ---
    def _is_valid_smiles(self, val: Any) -> bool:
        return isinstance(val, str) and len(val.strip()) > 1

    def _is_valid_cas(self, val: Any) -> bool:
        if not val or not isinstance(val, str): return False
        return bool(re.match(r'^\d{2,7}-\d{2}-\d$', val.strip()))

    def _clean_str(self, s: Any) -> Optional[str]:
        if not s: return None
        clean = re.sub(r'\[\w+\]', '', str(s)) # Remove refs [1]
        clean = re.sub(r'<[^>]+>', '', clean)   # Remove HTML tags
        return clean.strip() or None

    # --- WIKI LOGIC ---
    def search_wiki(self, query: str) -> Optional[str]:
        if not query: return None
        params = {"action": "query", "list": "search", "srsearch": query, "format": "json"}
        try:
            r = self.session.get(self.API_URL, params=params, timeout=5)
            results = r.json().get("query", {}).get("search", [])
            if results: return results[0]["title"]
        except: pass
        return None

    def _validate_chemical_page(self, title: str, infobox: Dict[str, str], target_cas: Optional[str]) -> bool:
        """
        Determines if the page is actually about a chemical.
        Logic:
        1. If it has Strong Keys (Formula, Molar Mass) -> ACCEPT (It's a chemical).
        2. If it lacks keys but matches CAS -> ACCEPT (It's the right page, maybe weird formatting).
        3. Else -> REJECT (It's likely Midtown Manhattan).
        """
        # 1. Title Blacklist (Fast Fail)
        bad_titles = ["list of", "war", "battle", "election", "season", "championship", "district", "county", "album", "disambiguation"]
        if any(b in title.lower() for b in bad_titles):
            return False

        # 2. Strong Key Check
        found_keys = set(k.lower() for k in infobox.keys())
        has_strong_key = not self.STRONG_CHEMICAL_KEYS.isdisjoint(found_keys)

        if has_strong_key:
            return True # It's a chemical page. We trust it even if CAS doesn't perfectly align.

        # 3. Last Ditch CAS Check (Only if keys failed)
        # If we searched by CAS, and the page doesn't look like a chemical,
        # check if the text contains our CAS number anyway (maybe it's a stub).
        if target_cas:
            # We can't check the whole HTML here easily without re-parsing,
            # so we check if the Infobox captured it under a weird key.
            # Realistically, if 'has_strong_key' failed, it probably doesn't have a CAS field either.
            pass

        return False

    def fetch_data(self, title: str, target_cas: Optional[str] = None) -> Tuple[Dict[str, str], str, List[str]]:
        params = {"action": "parse", "page": title, "prop": "text", "format": "json", "redirects": 1}
        summary_params = {"action": "query", "prop": "extracts", "titles": title, "exintro": 1, "explaintext": 1, "format": "json", "redirects": 1}

        infobox_data = {}
        summary_text = ""
        extracted_synonyms = []

        try:
            r = self.session.get(self.API_URL, params=params, timeout=5)
            data = r.json()
            raw_html = data.get("parse", {}).get("text", {}).get("*", "")

            if raw_html:
                soup = BeautifulSoup(raw_html, "html.parser")
                ib = soup.find("table", class_=re.compile(r"infobox"))
                if ib:
                    for row in ib.find_all("tr"):
                        cells = row.find_all(['th', 'td'])
                        if len(cells) >= 2:
                            k = cells[0].get_text(" ", strip=True).strip()

                            # Synonym Logic
                            if k.lower() in ["other names", "synonyms", "other name"]:
                                val_cell = cells[1]
                                for br in val_cell.find_all(["br", "li"]):
                                    br.replace_with("|||")
                                raw_val = val_cell.get_text()
                                clean_val = re.sub(r'\[.*?\]', '', raw_val)
                                parts = re.split(r'\|\|\||;', clean_val)
                                for p in parts:
                                    p_clean = p.strip()
                                    if len(p_clean) > 1: extracted_synonyms.append(p_clean)

                            v = cells[1].get_text(" ", strip=True)
                            if k and v: infobox_data[k] = v

            # VALIDATION STEP
            if not self._validate_chemical_page(title, infobox_data, target_cas):
                self.stats["garbage_rejected"] += 1
                return {}, "", []

            # Only fetch summary if validation passed
            r2 = self.session.get(self.API_URL, params=summary_params, timeout=5)
            pages = r2.json().get("query", {}).get("pages", {})
            for pid in pages:
                if pid != "-1":
                    summary_text = pages[pid].get("extract", "")
                    break

        except Exception: pass

        return infobox_data, summary_text, extracted_synonyms

    def process_file(self, filename: str):
        in_path = os.path.join(INPUT_DIR, filename)
        out_path = os.path.join(OUTPUT_DIR, filename)

        try:
            with open(in_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: return

        compound = data.get("compound", {})
        if not compound: compound = data
        ident = compound.setdefault("identity", {})
        game = compound.setdefault("game_data", {})
        maint = compound.setdefault("_maintenance", {})

        needs_smiles = not self._is_valid_smiles(ident.get("smiles"))
        needs_cas = not self._is_valid_cas(ident.get("cas_rn"))
        needs_formula = not ident.get("formula")
        needs_desc = not ident.get("description") and not game.get("description")

        current_syn_count = len(ident.get("synonyms", []))
        should_enrich = needs_smiles or needs_cas or needs_formula or needs_desc or current_syn_count < 5

        if not should_enrich:
            with open(out_path, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2)
            self.stats["processed"] += 1
            return

        self.stats["api_hit"] += 1

        target_cas = ident.get("cas_rn") if self._is_valid_cas(ident.get("cas_rn")) else None
        search_query = target_cas if target_cas else ident.get("name")

        updates_made = []

        if search_query:
            page_title = self.search_wiki(search_query)
            if page_title:
                infobox, summary, new_synonyms = self.fetch_data(page_title, target_cas)

                if infobox:
                    # --- FILL SMILES ---
                    if needs_smiles:
                        candidates = []
                        for k, v in infobox.items():
                            if "smiles" in k.lower():
                                clean = v.replace("show", "").replace("Interactive image", "").strip()
                                if self._is_valid_smiles(clean): candidates.append(clean)
                        if candidates:
                            best = max(candidates, key=len)
                            ident["smiles"] = best
                            maint["smiles_source"] = f"Wiki_v2 ({page_title})"
                            self.stats["smiles_filled"] += 1
                            updates_made.append(f"SMILES='{best[:20]}...'")

                    # --- FILL CAS ---
                    if needs_cas:
                        cas_val = infobox.get("CAS Number")
                        if cas_val:
                            match = re.search(r'\d{2,7}-\d{2}-\d', cas_val)
                            if match:
                                found_cas = match.group(0)
                                ident["cas_rn"] = found_cas
                                maint["cas_source"] = f"Wiki_v2 ({page_title})"
                                self.stats["cas_filled"] += 1
                                updates_made.append(f"CAS='{found_cas}'")

                    # --- FILL FORMULA ---
                    if needs_formula:
                        form_val = infobox.get("Chemical formula") or infobox.get("Formula")
                        clean_form = self._clean_str(form_val)
                        if clean_form:
                            ident["formula"] = clean_form
                            self.stats["formula_filled"] += 1
                            updates_made.append(f"Form='{clean_form}'")

                    # --- FILL DESCRIPTION ---
                    if needs_desc and summary:
                        if len(summary) > 50:
                            ident["description"] = summary
                            self.stats["desc_filled"] += 1
                            updates_made.append(f"Desc='{summary[:40]}...'")

                    # --- FILL SYNONYMS ---
                    if new_synonyms:
                        current_syns = ident.get("synonyms", [])
                        existing_lower = set(s.lower() for s in current_syns)

                        actually_added = []
                        for syn in new_synonyms:
                            if len(syn) < 2 or "check" in syn.lower() or "verify" in syn.lower(): continue
                            if syn.lower() not in existing_lower:
                                current_syns.append(syn)
                                existing_lower.add(syn.lower())
                                actually_added.append(syn)

                        if actually_added:
                            ident["synonyms"] = current_syns
                            self.stats["synonyms_added"] += len(actually_added)
                            preview_syns = str(actually_added[:3]).replace('[','').replace(']','')
                            if len(actually_added) > 3: preview_syns += "..."
                            updates_made.append(f"Syns(+{len(actually_added)}: {preview_syns})")

                    if updates_made:
                        xrefs = compound.setdefault("cross_references", {})
                        xrefs["wikipedia"] = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"

        if updates_made:
            maint["wiki_sweep_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{filename}] 🩹 {', '.join(updates_made)}")
            time.sleep(0.5)

        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        logger.info(f"🚀 Starting Phase 0.5: Wiki Sweep (Garbage Filtered) on {len(files)} files...")

        for f in tqdm(files, desc="Wiki Sweep"):
            self.process_file(f)

        logger.info("DONE. Stats:")
        for k, v in self.stats.items():
            logger.info(f"  {k}: {v}")

if __name__ == "__main__":
    sweeper = WikiBasisEnricher()
    sweeper.run()