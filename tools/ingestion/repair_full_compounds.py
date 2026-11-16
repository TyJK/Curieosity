import json
import os
import logging
import requests
import re
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict, Counter
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import unquote

# --- CONFIGURATION ---
LIBRARY_DIR = os.path.normpath("./tools/data/full_compounds_backup") # Updated path
LOG_DIR = "./tools/logs"

# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%H:%M:%S')

file_handler = logging.FileHandler(f"{LOG_DIR}/forensic_repair_v12.log", mode='w', encoding='utf-8')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

logger = logging.getLogger("ForensicRepair")
logger.handlers = []
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

class ForensicRepair:
    API_URL = "https://en.wikipedia.org/w/api.php"
    HEADERS = {
        'User-Agent': 'CurieosityBot/12.0 (EducationalGame; +http://github.com/curieosity)'
    }

    # Expanded keys to catch Drugs, Minerals, and Materials
    CHEMICAL_KEYS = [
        # Standard Chemical
        "chemical formula", "formula", "molar mass", "molecular weight",
        "density", "melting point", "boiling point", "solubility",
        "cas number", "iupac name", "systematic name",
        # Mineral / Pigment / Material
        "specific gravity", "crystal system", "refractive index",
        "cleavage", "streak", "mohs scale", "luster", "color index",
        "hex triplet", "pigment",
        # Drug / Bio
        "atc code", "drugbank", "pubchem", "smiles", "inchi", "trade name",
        "routes of administration", "bioavailability", "metabolism",
        "elimination half-life", "excretion", "pregnancy category", "legal status"
    ]

    GARBAGE_FILTERS = [
        "list of", "championship", "season", "orthography", "district",
        "polymer", "plastic", "rubber", "tea", "coffee", "extract",
        "election", "football", "league", "cup", "trophy", "olympics"
    ]

    def __init__(self, library_path: str):
        self.library_path = library_path
        self.session = self._create_robust_session()
        self.stats = defaultdict(int)

    def _create_robust_session(self):
        sess = requests.Session()
        retry_strategy = Retry(
            total=3, backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        sess.mount("https://", adapter)
        sess.headers.update(self.HEADERS)
        return sess

    # --- PARSING ENGINES ---

    def _clean_wiki_number(self, raw_str: str) -> str:
        if not raw_str: return ""
        clean = re.sub(r'\[\w+\]', '', raw_str)
        clean = re.sub(r'<[^>]+>', '', clean)
        clean = clean.replace('−', '-').replace('–', '-').replace('—', '-')
        clean = clean.replace('\xa0', ' ').strip()
        return clean

    def normalize_temperature(self, raw_str: str) -> Optional[float]:
        clean = self._clean_wiki_number(raw_str)
        if not clean: return None

        def get_val(s):
            range_match = re.search(r'(-?\d+\.?\d*)\s*-\s*(-?\d+\.?\d*)', s)
            if range_match:
                return (float(range_match.group(1)) + float(range_match.group(2))) / 2
            num_match = re.search(r'(-?\d+\.?\d*)', s)
            if num_match:
                return float(num_match.group(1))
            return None

        try:
            k_segment = re.search(r'([-\d\.\s]+)\s?K', clean)
            if k_segment:
                val = get_val(k_segment.group(1))
                if val is not None and val >= 0: return round(val, 2)
            c_segment = re.search(r'([-\d\.\s]+)\s?°?C', clean, re.IGNORECASE)
            if c_segment:
                val = get_val(c_segment.group(1))
                if val is not None:
                    k_val = val + 273.15
                    if k_val >= 0: return round(k_val, 2)
            f_segment = re.search(r'([-\d\.\s]+)\s?°?F', clean, re.IGNORECASE)
            if f_segment:
                val = get_val(f_segment.group(1))
                if val is not None:
                    k_val = (val - 32) * 5/9 + 273.15
                    if k_val >= 0: return round(k_val, 2)
        except Exception: pass
        return None

    def calculate_hill_formula(self, smiles: str) -> str:
        if not smiles: return ""
        clean_s = smiles.replace('@@', '').replace('@', '')
        atoms = []
        i = 0
        n = len(clean_s)
        while i < n:
            char = clean_s[i]
            if not char.isalpha(): i += 1; continue
            element = char
            if i + 1 < n and clean_s[i+1].islower():
                element += clean_s[i+1]
                i += 2
            else:
                i += 1
            if len(element) == 1 and element.islower(): element = element.upper()
            atoms.append(element)
        counts = Counter(atoms)
        formula_parts = []
        if 'C' in counts:
            formula_parts.append(f"C{counts['C'] if counts['C'] > 1 else ''}")
            del counts['C']
            if 'H' in counts:
                formula_parts.append(f"H{counts['H'] if counts['H'] > 1 else ''}")
                del counts['H']
        for el in sorted(counts.keys()):
            formula_parts.append(f"{el}{counts[el] if counts[el] > 1 else ''}")
        return "".join(formula_parts)

    def clean_search_term(self, query: str) -> str:
        if not query: return ""
        soup = BeautifulSoup(query, "html.parser")
        text = soup.get_text()
        text = text.replace("′", "'").replace("″", "''")
        return text.strip()

    def normalize_string(self, s: str) -> str:
        if not s: return ""
        s = re.sub(r'<[^>]+>', '', s)
        s = s.lower().replace("sub", "").replace("sup", "")
        return re.sub(r'[\W_]+', '', s)

    # --- RECONCILIATION LOGIC ---

    def reconcile_identity(self, page_title: str, raw_html: str, infobox: Dict[str, str], identity: Dict[str, Any]) -> Tuple[bool, str]:
        # 1. CAS Check
        file_cas = identity.get('cas_rn', '')
        if file_cas and re.match(r'^\d+-\d+-\d+$', file_cas): # STRICT CAS FORMAT
            if file_cas in raw_html or file_cas.replace('-', '') in raw_html.replace('-', ''):
                return True, "CAS Match"

        # 2. Name Check (Exact & Normalized)
        file_name_clean = self.normalize_string(identity.get('name', ''))
        wiki_title_clean = self.normalize_string(page_title)

        if file_name_clean and wiki_title_clean:
            if file_name_clean in wiki_title_clean or wiki_title_clean in file_name_clean:
                # Length safety check
                len_ratio = min(len(file_name_clean), len(wiki_title_clean)) / max(len(file_name_clean), len(wiki_title_clean))
                if len_ratio > 0.5:
                    return True, f"Name Match ({file_name_clean} <-> {wiki_title_clean})"

            synonyms = [self.normalize_string(s) for s in identity.get('synonyms', [])]
            if wiki_title_clean in synonyms:
                return True, "Synonym Match"

        # 3. Token Overlap Check
        if file_name_clean and wiki_title_clean:
            file_tokens = set(re.findall(r'[a-z]+', file_name_clean))
            wiki_tokens = set(re.findall(r'[a-z]+', wiki_title_clean))

            noise = {'acid', 'salt', 'compound', 'cis', 'trans', 'alpha', 'beta', 'drug', 'pharmaceutical'}
            file_tokens -= noise
            wiki_tokens -= noise

            if file_tokens and wiki_tokens:
                intersection = file_tokens.intersection(wiki_tokens)
                if len(intersection) >= 2 or (len(intersection) == 1 and len(file_tokens) == 1):
                    return True, f"Token Match {intersection}"

        # 4. Formula Check
        file_formula = self.normalize_string(identity.get('formula', ''))
        wiki_formula_raw = infobox.get('Chemical formula') or infobox.get('Formula') or ""
        wiki_formula = self.normalize_string(self._clean_wiki_number(wiki_formula_raw))

        if file_formula and wiki_formula and file_formula == wiki_formula:
            if len(file_formula) > 2:
                return True, f"Formula Match ({file_formula})"

        return False, f"Fail. File: '{file_name_clean}' vs Wiki: '{wiki_title_clean}'"

    # --- WIKIPEDIA INTERACTION ---

    def is_garbage_query(self, query: str) -> bool:
        q = query.lower()
        if len(q) < 4 and not q.isdigit(): return True
        if re.search(r'\d{4}', q) and "acid" not in q: return True
        if any(bad in q for bad in self.GARBAGE_FILTERS): return True
        return False

    def search_wikipedia(self, query: str) -> Optional[str]:
        if not query: return None
        if self.is_garbage_query(query): return None

        search_term = self.clean_search_term(query)
        if "-" in search_term: search_term = f'"{search_term}"'

        params = {"action": "query", "list": "search", "srsearch": search_term, "format": "json"}
        try:
            r = self.session.get(self.API_URL, params=params, timeout=5)
            if r.status_code == 200:
                results = r.json().get("query", {}).get("search", [])
                if results: return results[0]["title"]
        except Exception: pass
        return None

    def fetch_summary(self, page_title: str) -> Optional[str]:
        """Fetches the introductory text (summary) of the page."""
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "titles": page_title,
            "exintro": 1,
            "explaintext": 1,
            "redirects": 1
        }
        try:
            r = self.session.get(self.API_URL, params=params, timeout=5)
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            for pid, pdata in pages.items():
                if pid == "-1": return None
                return pdata.get("extract")
        except Exception:
            return None
        return None

    def fetch_and_validate(self, page_title: str, identity: Dict[str, Any]) -> Tuple[Dict[str, str], str, Optional[str]]:
        params = {"action": "parse", "page": page_title, "prop": "text", "section": 0, "format": "json", "redirects": 1}
        try:
            r = self.session.get(self.API_URL, params=params, timeout=10)
            data = r.json()
            raw_html = data.get("parse", {}).get("text", {}).get("*", "")
            page_id = data.get("parse", {}).get("pageid")

            if not raw_html or not page_id:
                return {}, "", "Page content missing"

            wiki_url = f"https://en.wikipedia.org/?curid={page_id}"
            soup = BeautifulSoup(raw_html, "html.parser")
            infobox_node = soup.find("table", class_=re.compile(r"infobox"))

            if not infobox_node:
                return {}, "", "No Infobox found"

            extracted = {}
            for row in infobox_node.find_all("tr"):
                cells = row.find_all(['th', 'td'])
                if len(cells) < 2: continue
                key_text = cells[0].get_text(" ", strip=True)
                for sup in cells[1].find_all("sup"): sup.decompose()
                val_text = cells[1].get_text(" ", strip=True).strip()
                if key_text and val_text:
                    extracted[key_text] = val_text

            # Check for expanded keys (Drugs, Minerals, etc)
            keys_lower = [k.lower() for k in extracted.keys()]
            is_valid_type = any(chem_key in " ".join(keys_lower) for chem_key in self.CHEMICAL_KEYS)
            if not is_valid_type:
                return {}, "", f"Infobox lacks valid keys. Found: {list(extracted.keys())[:3]}..."

            is_match, reason = self.reconcile_identity(page_title, raw_html, extracted, identity)
            if is_match:
                return extracted, wiki_url, None
            else:
                return {}, "", f"Identity Mismatch: {reason}"

        except Exception as e:
            return {}, "", f"Exception: {str(e)}"

    # --- MAIN LOOP ---

    def run(self):
        files = [f for f in os.listdir(self.library_path) if f.endswith(".json")]
        logger.info(f"🚀 Starting Forensic Repair V12 (Description Enricher) on {len(files)} compounds...")

        for filename in tqdm(files, desc="Processing"):
            file_path = os.path.join(self.library_path, filename)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                changed = False
                compound = data['compound']
                identity = compound['identity']
                game_data = compound.setdefault('game_data', {})

                # Sanitize CAS for searching
                raw_cas = identity.get('cas_rn', filename.replace('.json', ''))
                searchable_cas = raw_cas if re.match(r'^\d+-\d+-\d+$', raw_cas) else None

                # SMILES Provenance
                gen_source = data.get('meta', {}).get('generated_from', '')
                current_smiles = identity.get('smiles', '')
                valid_smiles = current_smiles
                if gen_source and len(gen_source) > 1 and " " not in gen_source.strip():
                    if gen_source != current_smiles:
                        identity['smiles'] = gen_source
                        valid_smiles = gen_source
                        changed = True

                # Strategies
                strategies = []
                existing_url = compound.get('additional_context', {}).get('external_links', {}).get('wikipedia')
                if existing_url and "en.wikipedia.org/wiki/" in existing_url:
                    title = unquote(existing_url.split("/")[-1])
                    if title: strategies.append(("URL", title))

                if searchable_cas: strategies.append(("CAS", searchable_cas))
                strategies.append(("Name", identity.get('name')))
                syns = identity.get('synonyms', [])
                for i, s in enumerate(syns[:3]):
                    strategies.append((f"Synonym_{i}", s))

                success = False
                skip_log = []

                for stype, query in strategies:
                    if not query: continue

                    if stype == "URL":
                        page_title = query
                    else:
                        page_title = self.search_wikipedia(query)

                    if not page_title: continue

                    raw_wiki, wiki_url, fail_reason = self.fetch_and_validate(page_title, identity)

                    if raw_wiki:
                        success = True

                        # 1. Update Context Links
                        if 'additional_context' not in compound: compound['additional_context'] = {}
                        if 'external_links' not in compound['additional_context']: compound['additional_context']['external_links'] = {}

                        if compound['additional_context']['external_links'].get('wikipedia') != wiki_url:
                            compound['additional_context']['external_links']['wikipedia'] = wiki_url
                            changed = True

                        # 2. Update Raw Data
                        if compound['additional_context'].get('wikipedia_raw') != raw_wiki:
                            compound['additional_context']['wikipedia_raw'] = raw_wiki
                            changed = True
                            self.stats['raw_dumped'] += 1
                            logger.info(f"   [{filename}] ✅ Updated via {stype}: '{page_title}'")

                        # 3. Enrich Description (New in V12)
                        # Only fetch if we don't have a good description yet
                        current_desc = game_data.get('description', '')
                        if not current_desc or len(current_desc) < 50:
                            summary = self.fetch_summary(page_title)
                            if summary:
                                game_data['description'] = summary
                                changed = True
                                self.stats['desc_added'] += 1

                        # 4. Parse Physics
                        physics = game_data.setdefault('physics', {})

                        if 'Melting point' in raw_wiki:
                            val = self.normalize_temperature(raw_wiki['Melting point'])
                            if val: physics['melting_point_k'] = val; changed = True
                        if 'Boiling point' in raw_wiki:
                            val = self.normalize_temperature(raw_wiki['Boiling point'])
                            if val: physics['boiling_point_k'] = val; changed = True

                        dens_key = next((k for k in raw_wiki if 'density' in k.lower() or 'gravity' in k.lower()), None)
                        if dens_key:
                            clean_dens = self._clean_wiki_number(raw_wiki[dens_key])
                            match = re.search(r'(\d+\.?\d*)', clean_dens)
                            if match:
                                d_val = float(match.group(1))
                                if d_val < 30: physics['density_g_cm3'] = d_val; changed = True

                        wiki_formula = raw_wiki.get('Chemical formula') or raw_wiki.get('Formula')
                        if wiki_formula:
                            clean_form = self._clean_wiki_number(wiki_formula)
                            if identity.get('formula') != clean_form:
                                identity['formula'] = clean_form; changed = True
                        elif not identity.get('formula') and valid_smiles:
                            calc_form = self.calculate_hill_formula(valid_smiles)
                            if calc_form: identity['formula'] = calc_form; changed = True

                        break
                    else:
                        skip_log.append(f"[{stype}] '{page_title}' -> {fail_reason}")

                if not success and not changed:
                    if skip_log:
                        logger.info(f"   [{filename}] ❌ SKIP: {'; '.join(skip_log[-2:])}")

                if changed:
                    with open(file_path, 'w', encoding='utf-8') as f_out:
                        json.dump(data, f_out, indent=2)
                    self.stats['files_saved'] += 1

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"ERROR {filename}: {e}")

        self._print_summary()

    def _print_summary(self):
        print("\n" + "="*50)
        print("🧪 FORENSIC REPAIR V12 SUMMARY")
        print("="*50)
        print(f"Files Modified:      {self.stats['files_saved']}")
        print(f"Raw Wiki Dumps:      {self.stats['raw_dumped']}")
        print(f"Descriptions Added:  {self.stats['desc_added']}")
        print("="*50)

if __name__ == "__main__":
    repair = ForensicRepair(LIBRARY_DIR)
    repair.run()