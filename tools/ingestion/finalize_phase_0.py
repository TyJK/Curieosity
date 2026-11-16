import json
import os
import re
import time
import logging
import requests
import difflib
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List, Set
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Client Imports
from pubchem_client import PubChemClient
from chebi_client import ChEBIClient

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/03_gap_closer")
OUTPUT_DIR = os.path.normpath("./tools/data/04_finalize_phase_0")
LOG_DIR = "./tools/logs"

# Quality Control
MIN_DESC_WORDS = 40  # Filter out "White powder" entries
MAX_SYNS_PER_SOURCE = 50 # Prevent synonym bloat

# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/finalize_phase_0.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Phase0Finalizer")

# --- HELPER SCRAPERS ---

class NISTScraper:
    """Scrapes NIST Webbook for Synonyms."""
    BASE_URL = "https://webbook.nist.gov/cgi/cbook.cgi"
    HEADERS = {'User-Agent': 'CurieosityBot/16.0 (Narrative)'}

    def __init__(self):
        sess = requests.Session()
        retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502])
        sess.mount("https://", HTTPAdapter(max_retries=retry))
        sess.headers.update(self.HEADERS)
        self.session = sess

    def get_synonyms(self, cas_rn: str) -> List[str]:
        if not cas_rn or not re.match(r'^\d+-\d+-\d+$', cas_rn): return []
        # NIST expects "C" prefix for CAS search
        url = f"{self.BASE_URL}?ID=C{cas_rn}&Units=SI"
        synonyms = []
        try:
            r = self.session.get(url, timeout=5)
            if r.status_code != 200: return []
            soup = BeautifulSoup(r.text, 'html.parser')
            # NIST usually lists synonyms in the main content area
            main_content = soup.find('main')
            if main_content:
                ul = main_content.find('ul')
                if ul:
                    for li in ul.find_all('li'):
                        text = li.get_text().strip()
                        # Simple heuristic: Synonyms are relatively short
                        if text and len(text) < 100 and not "href" in str(li):
                            synonyms.append(text)
        except: pass
        return synonyms

class WikiScraper:
    """Wiki Scraper with 'Duck Typing' Validation."""
    API_URL = "https://en.wikipedia.org/w/api.php"
    HEADERS = {'User-Agent': 'CurieosityBot/16.0 (Narrative)'}

    STRONG_KEYS = {
        "chemical formula", "formula", "molar mass", "molecular weight",
        "cas number", "iupac name", "systematic name", "drugbank",
        "pubchem", "smiles", "inchi", "density", "melting point",
        "boiling point", "atc code", "ec number"
    }

    def __init__(self):
        sess = requests.Session()
        retry = Retry(total=2, backoff_factor=1)
        sess.mount("https://", HTTPAdapter(max_retries=retry))
        sess.headers.update(self.HEADERS)
        self.session = sess

    def search(self, query: str) -> Optional[str]:
        if not query: return None
        params = {"action": "query", "list": "search", "srsearch": query, "format": "json"}
        try:
            r = self.session.get(self.API_URL, params=params, timeout=5)
            res = r.json().get("query", {}).get("search", [])
            if res: return res[0]["title"]
        except: pass
        return None

    def _is_chemical_page(self, title: str, infobox_keys: List[str]) -> bool:
        """Ensures we aren't scraping 'Midtown Manhattan'."""
        bad_titles = ["list of", "war", "battle", "election", "season", "district", "album", "disambiguation"]
        if any(b in title.lower() for b in bad_titles): return False

        # Duck Typing: If it has chemical keys, it's a chemical
        found = set(k.lower() for k in infobox_keys)
        return not self.STRONG_KEYS.isdisjoint(found)

    def get_data(self, title: str) -> Dict[str, Any]:
        out = {"desc": None, "syns": []}
        try:
            # 1. Parse Infobox (Validation + Synonyms)
            p_p = {"action": "parse", "page": title, "prop": "text", "format": "json", "redirects": 1}
            r = self.session.get(self.API_URL, params=p_p, timeout=5)
            html = r.json().get("parse", {}).get("text", {}).get("*", "")

            keys = []
            if html:
                soup = BeautifulSoup(html, "html.parser")
                # Find the Infobox
                ib = soup.find("table", class_=re.compile(r"infobox"))
                if ib:
                    for row in ib.find_all("tr"):
                        cells = row.find_all(['th', 'td'])
                        if len(cells) >= 2:
                            k = cells[0].get_text(" ", strip=True).lower()
                            keys.append(k)

                            # Extract Synonyms
                            if "synonyms" in k or "other names" in k:
                                val_cell = cells[1]
                                # Replace breaks with separator to handle lists
                                for br in val_cell.find_all(["br", "li"]): br.replace_with("|||")
                                cln = re.sub(r'\[.*?\]', '', val_cell.get_text())
                                for p in re.split(r'\|\|\||;', cln):
                                    if len(p.strip()) > 2: out["syns"].append(p.strip())

            # Validation
            if not self._is_chemical_page(title, keys): return out

            # 2. Get Summary (Description)
            s_p = {"action": "query", "prop": "extracts", "titles": title, "exintro": 1, "explaintext": 1, "format": "json"}
            r2 = self.session.get(self.API_URL, params=s_p, timeout=5)
            pgs = r2.json().get("query", {}).get("pages", {})
            for pid in pgs:
                if pid != "-1": out["desc"] = pgs[pid].get("extract")
        except: pass
        return out

class PubChemDeepDive:
    """Fetches Encyclopedic text from PubChem View."""
    def __init__(self, client):
        self.client = client

    def get_text_data(self, cid: str) -> Dict[str, Any]:
        out = {"desc": None}
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
        try:
            r = self.client.session.get(url, timeout=5)
            if r.status_code != 200: return out
            data = r.json()

            candidates = []
            # Recursive search for text sections
            def search_sections(nodes):
                for node in nodes:
                    head = node.get("TOCHeading", "")
                    # Look in specific narrative sections
                    if head in ["Record Description", "Abstract", "Description", "Pharmacology", "Uses", "Mechanism of Action"]:
                        for info in node.get("Information", []):
                            val = info.get("Value", {}).get("StringWithMarkup", [])
                            if val: candidates.append(val[0].get("String"))

                    if "Section" in node: search_sections(node["Section"])

            search_sections(data.get("Record", {}).get("Section", []))

            # Select best description > MIN words
            valid = [c for c in candidates if len(c.split()) >= MIN_DESC_WORDS]
            if valid:
                # Prefer the longest one as it's likely the most encyclopedic
                out["desc"] = max(valid, key=len)
        except: pass
        return out

# --- MAIN CONTROLLER ---

class Phase0Finalizer:
    def __init__(self):
        self.pubchem = PubChemClient()
        self.pubchem_deep = PubChemDeepDive(self.pubchem)
        self.wiki = WikiScraper()
        self.nist = NISTScraper()
        self.chebi = ChEBIClient()

        self.stats = {
            "total": 0, "dropped": 0, "kept": 0,
            "desc_wiki": 0, "desc_chebi": 0, "desc_pubchem": 0,
            "syns_added": 0, "api_hits": 0, "bad_chebi": 0
        }

    def _is_valid_smiles(self, val):
        return isinstance(val, str) and len(val.strip()) > 1

    def _is_good_desc(self, desc):
        if not desc: return False
        return len(desc.split()) >= MIN_DESC_WORDS

    def _safe_chebi_match(self, search_name: str, chebi_label: str) -> bool:
        """Prevents 'Lead' matching 'Calcium' via fuzzy search."""
        if not search_name or not chebi_label: return False
        s_norm = search_name.lower()
        c_norm = chebi_label.lower()
        # Direct containment is usually safe
        if s_norm in c_norm or c_norm in s_norm: return True
        # Sequence Matcher for typos (threshold 0.8)
        return difflib.SequenceMatcher(None, s_norm, c_norm).ratio() > 0.8

    def process_file(self, filename: str):
        in_path = os.path.join(INPUT_DIR, filename)
        out_path = os.path.join(OUTPUT_DIR, filename)

        try:
            with open(in_path, 'r', encoding='utf-8') as f: data = json.load(f)
        except: return

        self.stats["total"] += 1
        compound = data.get("compound", {}) or data
        ident = compound.setdefault("identity", {})
        maint = compound.setdefault("_maintenance", {})

        # ==========================
        # 1. PURGE (SMILES Check)
        # ==========================
        if not self._is_valid_smiles(ident.get("smiles")):
            self.stats["dropped"] += 1
            return
        self.stats["kept"] += 1

        # ==========================
        # 2. NARRATIVE ENRICHMENT
        # ==========================
        curr_desc = ident.get("description", "")
        needs_desc = not self._is_good_desc(curr_desc)
        curr_syns = ident.get("synonyms", [])
        # We cap our check to save API calls on already-rich files
        needs_syns = len(curr_syns) < 20

        cas = ident.get("cas_rn")
        name = ident.get("name")
        # Search strategy: Prefer CAS if valid, else Name
        search_term = cas if (cas and re.match(r'^\d+-\d+-\d+$', cas)) else name

        changed = False
        updates = []

        if search_term and (needs_desc or needs_syns):
            self.stats["api_hits"] += 1

            # --- SOURCE 1: WIKIPEDIA (Gold) ---
            wiki_title = self.wiki.search(search_term)
            if wiki_title:
                wiki_data = self.wiki.get_data(wiki_title)

                if needs_desc and self._is_good_desc(wiki_data["desc"]):
                    ident["description"] = wiki_data["desc"]
                    self.stats["desc_wiki"] += 1
                    trunc_desc = wiki_data["desc"][:30].replace("\n", "")
                    updates.append(f"Desc(Wiki)='{trunc_desc}...'")
                    needs_desc = False
                    changed = True

                if wiki_data["syns"]:
                    added = self._merge_synonyms(curr_syns, wiki_data["syns"])
                    if added:
                        changed = True
                        self.stats["syns_added"] += added

            # --- SOURCE 2: ChEBI (Silver - Bio Context) ---
            if needs_desc and name:
                try:
                    cid = self.chebi.search_entity(name)
                    if cid:
                        ent = self.chebi.get_complete_entity(cid)
                        label = ent.get("label", "")

                        # Validate match
                        if self._safe_chebi_match(name, label):
                            defs = ent.get("description", [])
                            if defs:
                                best = max(defs, key=len)
                                if self._is_good_desc(best):
                                    ident["description"] = best
                                    self.stats["desc_chebi"] += 1
                                    trunc_desc = best[:30].replace("\n", "")
                                    updates.append(f"Desc(ChEBI)='{trunc_desc}...'")
                                    needs_desc = False
                                    changed = True
                        else:
                            self.stats["bad_chebi"] += 1
                except: pass

            # --- SOURCE 3: PUBCHEM DEEP DIVE ---
            cids = self.pubchem.fetch_cids(search_term)
            if cids:
                cid = cids[0]

                # A. Deep Text
                if needs_desc:
                    pc_data = self.pubchem_deep.get_text_data(cid)
                    if pc_data["desc"] and self._is_good_desc(pc_data["desc"]):
                        ident["description"] = pc_data["desc"]
                        self.stats["desc_pubchem"] += 1
                        trunc_desc = pc_data["desc"][:30].replace("\n", "")
                        updates.append(f"Desc(PubChemDeep)='{trunc_desc}...'")
                        needs_desc = False
                        changed = True

                # B. Synonyms
                if needs_syns:
                    try:
                        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
                        r = requests.get(url, timeout=5)
                        if r.status_code == 200:
                            syns = r.json().get('InformationList', {}).get('Information', [])[0].get('Synonym', [])
                            short = [s for s in syns if len(s)<50]
                            added = self._merge_synonyms(curr_syns, short[:MAX_SYNS_PER_SOURCE])
                            if added:
                                changed = True
                                self.stats["syns_added"] += added
                    except: pass

                # Link CID
                if changed:
                    x = compound.setdefault("cross_references", {})
                    if not x.get("pubchem_cid"): x["pubchem_cid"] = str(cid)

            # --- SOURCE 4: NIST (Synonyms) ---
            if cas and needs_syns:
                nist_syns = self.nist.get_synonyms(cas)
                if nist_syns:
                    added = self._merge_synonyms(curr_syns, nist_syns)
                    if added:
                        changed = True
                        self.stats["syns_added"] += added

        # SAVE
        if changed:
            maint["final_phase0_enriched_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            log_parts = []
            if updates: log_parts.extend(updates)
            # Log total syns if changed
            if len(curr_syns) > 5: log_parts.append(f"+{len(curr_syns)} Syns")

            logger.info(f"[{filename}] 🖋️ {', '.join(log_parts)}")
            time.sleep(0.2)

        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _merge_synonyms(self, current_list: List[str], new_list: List[str]) -> int:
        existing_lower = set(s.lower() for s in current_list)
        added_count = 0
        if len(current_list) > 150: return 0

        for s in new_list:
            if added_count >= MAX_SYNS_PER_SOURCE: break
            s_clean = s.strip()
            if len(s_clean) < 2 or "check" in s_clean.lower(): continue
            if s_clean.lower() not in existing_lower:
                current_list.append(s_clean)
                existing_lower.add(s_clean.lower())
                added_count += 1
        return added_count

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        logger.info(f"🚀 Starting Final Phase 0 (Purge + Secure Narrative) on {len(files)} files...")
        for f in tqdm(files, desc="Finalizing"):
            self.process_file(f)
        logger.info("DONE. Stats:")
        for k, v in self.stats.items(): logger.info(f"  {k}: {v}")

if __name__ == "__main__":
    finisher = Phase0Finalizer()
    finisher.run()