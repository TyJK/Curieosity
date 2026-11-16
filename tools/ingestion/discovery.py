import logging
import time
import requests
import pandas as pd
import itertools
from typing import Set, Dict, List, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- 1. CONFIGURATION ---
logging.basicConfig(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger("DiscoveryV2")
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logging.getLogger("urllib3").setLevel(logging.WARNING)

class DiscoverySearcherV2:
    API_URL = "https://www.wikidata.org/w/api.php"

    HEADERS = {
        'User-Agent': 'CurieosityBot/1.0 (EducationalGame; +http://github.com/curieosity)',
        'Accept': 'application/json'
    }

    def __init__(self, master_csv_path: str):
        self.seen_cas = set()
        self.seen_names = set()
        self.candidates = []
        self.session = self._create_robust_session()
        self._load_existing(master_csv_path)

    def _create_robust_session(self):
        sess = requests.Session()
        retry_strategy = Retry(
            total=5, backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        sess.mount("https://", adapter)
        sess.headers.update(self.HEADERS)
        return sess

    def _load_existing(self, path: str):
        try:
            logger.info(f"📂 Loading master list: {path}")
            df = pd.read_csv(path)
            if 'CAS' in df.columns:
                self.seen_cas = set(df['CAS'].dropna().astype(str).str.strip().unique())
            if 'NAME' in df.columns:
                self.seen_names = set(df['NAME'].dropna().astype(str).str.lower().str.strip().unique())
            logger.info(f"✅ Memory: {len(self.seen_cas)} CAS RNs, {len(self.seen_names)} Names loaded.")
        except Exception:
            logger.warning("⚠️ Master file not found or unreadable. Discovery will contain duplicates.")

    def is_new(self, cas: Optional[str], name: Optional[str]) -> bool:
        if cas and cas.strip() in self.seen_cas: return False
        if name and name.strip().lower() in self.seen_names: return False
        return True

    def add_candidate(self, name: str, cas: str, strategy: str, notes: str):
        if self.is_new(cas, name):
            self.candidates.append({
                "NAME": name, "CAS": cas,
                "STRATEGY": strategy, "NOTES": notes
            })
            if cas: self.seen_cas.add(cas)
            if name: self.seen_names.add(name.strip().lower())

    # --- CORE SEARCH ENGINE ---
    def search_wikidata(self, search_query: str, limit: int = 500) -> List[str]:
        qids = []
        offset = 0
        batch_size = 50

        logger.info(f"🔎 Searching: '{search_query}' (Target: {limit})")

        while len(qids) < limit:
            params = {
                "action": "query", "list": "search",
                "srsearch": search_query, "srlimit": batch_size,
                "sroffset": offset, "format": "json"
            }
            try:
                r = self.session.get(self.API_URL, params=params, timeout=30)
                data = r.json()
                search_results = data.get("query", {}).get("search", [])

                if not search_results: break

                for item in search_results:
                    qids.append(item["title"])

                offset += batch_size
                if "continue" not in data: break
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"   ❌ Search failed: {e}")
                break

        logger.info(f"   ✅ Found {len(qids)} matching entities.")
        return qids

    def resolve_entities(self, qids: List[str], strategy_label: str):
        if not qids: return
        chunk_size = 50
        total_resolved = 0
        logger.info(f"📥 Resolving {len(qids)} entities for '{strategy_label}'...")

        for i in range(0, len(qids), chunk_size):
            chunk = qids[i:i + chunk_size]
            ids_str = "|".join(chunk)
            params = {
                "action": "wbgetentities", "ids": ids_str,
                "props": "labels|claims", "languages": "en", "format": "json"
            }
            try:
                r = self.session.get(self.API_URL, params=params, timeout=30)
                data = r.json()
                entities = data.get("entities", {})

                for qid, entity in entities.items():
                    label = entity.get("labels", {}).get("en", {}).get("value")
                    if not label: continue

                    # Extract CAS (P231)
                    claims = entity.get("claims", {})
                    cas = None
                    if "P231" in claims:
                        try: cas = claims["P231"][0]["mainsnak"]["datavalue"]["value"]
                        except: pass

                    self.add_candidate(label, cas, strategy_label, f"Wikidata ID: {qid}")
                    total_resolved += 1
                time.sleep(0.5)
            except Exception: pass

        logger.info(f"   ✅ Resolved {total_resolved} new candidates.")

    # --- STRATEGIES V2 ---

    def run_sensory_search(self):
        # P393 (Odor) + P662 (Is Chemical)
        logger.info("👃 Running Odor Search...")
        qids = self.search_wikidata("haswbstatement:P393 haswbstatement:P662", limit=300)
        self.resolve_entities(qids, "Sensory (Odor)")

    def run_keyword_roles(self):
        # We use Keywords + P662 instead of specific Role IDs.
        # This catches "TNT" because the text "explosive" is in its description/aliases.
        logger.info("🧨 Running Role Keyword Search...")

        roles = {
            "Explosive": "explosive haswbstatement:P662",
            "Neurotoxin": "neurotoxin haswbstatement:P662",
            "Pigment": "pigment haswbstatement:P662",
            "Gemstone": "gemstone haswbstatement:P662", # Often oxides/silicates
            "Alchemical": "alchemy haswbstatement:P662"  # Historical fun
        }

        for label, query in roles.items():
            qids = self.search_wikidata(query, limit=200)
            self.resolve_entities(qids, f"Role ({label})")

    def run_expanded_permutations(self):
        logger.info("🧪 Generating Expanded Inorganic Salts...")

        cations = [
            ("Ammonium", "NH4"), ("Potassium", "K"), ("Sodium", "Na"),
            ("Lithium", "Li"), ("Silver", "Ag"), ("Gold(III)", "Au"),
            ("Copper(II)", "Cu"), ("Iron(III)", "Fe"), ("Cobalt(II)", "Co"),
            ("Nickel(II)", "Ni"), ("Barium", "Ba"), ("Lead(II)", "Pb")
        ]

        anions = [
            "Nitrate", "Sulfate", "Carbonate", "Chloride",
            "Cyanide", "Thiocyanate", "Oxalate", "Citrate",
            "Permanganate", "Chromate", "Dichromate", "Iodide",
            "Hydroxide", "Acetate", "Benzoate"
        ]

        count = 0
        for (cat_name, cat_sym), anion in itertools.product(cations, anions):
            full_name = f"{cat_name} {anion}"
            self.add_candidate(full_name, None, "InorganicPermuterV2", f"Target: {cat_sym}-{anion}")
            count += 1
        logger.info(f"✅ Generated {count} expanded salt candidates.")

    def save_candidates(self, filename="candidates_v2.csv"):
        if not self.candidates:
            logger.warning("⚠️ No candidates found.")
            return
        df = pd.DataFrame(self.candidates)
        df.to_csv(filename, index=False)
        logger.info(f"💾 Success! Saved {len(self.candidates)} candidates to {filename}")

if __name__ == "__main__":
    master_path = "./tools/data/master_compound_list.csv"
    searcher = DiscoverySearcherV2(master_path)

    # Run the new "V2" strategies
    searcher.run_sensory_search()    # Smells (Putrescine, etc)
    searcher.run_keyword_roles()     # Explosives, Poisons, Alchemy
    searcher.run_expanded_permutations() # Cyanides, Oxalates, etc.

    searcher.save_candidates()