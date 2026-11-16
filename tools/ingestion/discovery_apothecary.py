import logging
import time
import requests
import pandas as pd
import os
from typing import Set, Dict, List, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger("Apothecary")
logger.handlers = [handler]
logger.setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)

class ApothecarySearcher:
    API_URL = "https://www.wikidata.org/w/api.php"
    HEADERS = {
        'User-Agent': 'CurieosityBot/1.0 (EducationalGame; +http://github.com/curieosity)',
        'Accept': 'application/json'
    }

    def __init__(self, master_path: str, discovery_path: str):
        self.seen_cas = set()
        self.seen_names = set()
        self.candidates = []
        self.session = self._create_robust_session()

        # Load BOTH existing lists to ensure pure novelty
        self._load_existing(master_path, "Master List")
        self._load_existing(discovery_path, "Previous Discovery")

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

    def _load_existing(self, path: str, label: str):
        if not os.path.exists(path):
            logger.warning(f"⚠️ {label} not found at {path}. Skipping load.")
            return

        try:
            df = pd.read_csv(path)
            count = 0
            if 'CAS' in df.columns:
                c = set(df['CAS'].dropna().astype(str).str.strip().unique())
                self.seen_cas.update(c)
            if 'NAME' in df.columns:
                n = set(df['NAME'].dropna().astype(str).str.lower().str.strip().unique())
                self.seen_names.update(n)

            logger.info(f"📂 Loaded {label}: {len(df)} rows. (Total Blocklist: {len(self.seen_names)} names)")
        except Exception as e:
            logger.error(f"❌ Error loading {label}: {e}")

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

    # --- SEARCH ENGINE ---
    def search_wikidata(self, query: str, limit: int = 300) -> List[str]:
        qids = []
        offset = 0
        batch_size = 50
        logger.info(f"🔎 Query: '{query}' (Limit: {limit})")

        while len(qids) < limit:
            params = {
                "action": "query", "list": "search",
                "srsearch": query, "srlimit": batch_size,
                "sroffset": offset, "format": "json"
            }
            try:
                r = self.session.get(self.API_URL, params=params, timeout=30)
                data = r.json()
                results = data.get("query", {}).get("search", [])
                if not results: break

                for item in results: qids.append(item["title"])
                offset += batch_size
                if "continue" not in data: break
                time.sleep(0.5)
            except Exception: break
        return qids

    def resolve_entities(self, qids: List[str], strategy: str):
        if not qids: return
        chunk_size = 50
        total_added = 0
        logger.info(f"📥 Resolving {len(qids)} entities...")

        for i in range(0, len(qids), chunk_size):
            chunk = qids[i:i + chunk_size]
            params = {
                "action": "wbgetentities", "ids": "|".join(chunk),
                "props": "labels|claims", "languages": "en", "format": "json"
            }
            try:
                r = self.session.get(self.API_URL, params=params, timeout=30)
                data = r.json()
                for qid, entity in data.get("entities", {}).items():
                    label = entity.get("labels", {}).get("en", {}).get("value")
                    if not label: continue

                    # Get CAS (P231)
                    cas = None
                    claims = entity.get("claims", {})
                    if "P231" in claims:
                        try: cas = claims["P231"][0]["mainsnak"]["datavalue"]["value"]
                        except: pass

                    if self.is_new(cas, label):
                        self.add_candidate(label, cas, strategy, f"Wikidata: {qid}")
                        total_added += 1
                time.sleep(0.5)
            except Exception: pass

        logger.info(f"   ✅ Added {total_added} new {strategy} compounds.")

    # --- STRATEGIES ---

    def run_spice_rack(self):
        logger.info("🌿 Raiding the Spice Rack (Fragrances & Flavors)...")
        # Esters (Fruity), Terpenes (Plant smells), Aroma Compounds
        queries = [
            ("Sensory/Terpene", "terpene haswbstatement:P662"),
            ("Sensory/Ester", "ester flavor haswbstatement:P662"),
            ("Sensory/Aroma", "aroma compound haswbstatement:P662"),
            ("Sensory/EssentialOil", "essential oil component haswbstatement:P662")
        ]
        for tag, q in queries:
            ids = self.search_wikidata(q, limit=200)
            self.resolve_entities(ids, tag)

    def run_poison_garden(self):
        logger.info("🍄 Entering the Poison Garden...")
        # Alkaloids, Toxins, Venoms
        queries = [
            ("Toxin/Alkaloid", "alkaloid haswbstatement:P662"),
            ("Toxin/Mycotoxin", "mycotoxin haswbstatement:P662"), # Fungal poisons
            ("Toxin/Phytotoxin", "phytotoxin haswbstatement:P662"), # Plant poisons
            ("Toxin/Venom", "venom component haswbstatement:P662")
        ]
        for tag, q in queries:
            ids = self.search_wikidata(q, limit=200)
            self.resolve_entities(ids, tag)

    def run_medicine_cabinet(self):
        logger.info("💊 Opening the Medicine Cabinet...")
        queries = [
            ("Med/Vitamin", "vitamin haswbstatement:P662"),
            ("Med/Antibiotic", "antibiotic haswbstatement:P662"),
            ("Med/Analgesic", "analgesic haswbstatement:P662"),
            ("Med/Antiseptic", "antiseptic haswbstatement:P662")
        ]
        for tag, q in queries:
            ids = self.search_wikidata(q, limit=150)
            self.resolve_entities(ids, tag)

    def run_pantry(self):
        logger.info("🍰 Checking the Pantry...")
        queries = [
            ("Pantry/Acid", "food acid haswbstatement:P662"),
            ("Pantry/Sugar", "sugar chemical haswbstatement:P662"),
            ("Pantry/Preservative", "food preservative haswbstatement:P662")
        ]
        for tag, q in queries:
            ids = self.search_wikidata(q, limit=150)
            self.resolve_entities(ids, tag)

    def save(self, filename="apothecary_candidates.csv"):
        if not self.candidates:
            logger.warning("No new candidates found.")
            return
        df = pd.DataFrame(self.candidates)
        df.to_csv(filename, index=False)
        logger.info(f"💾 Saved {len(df)} apothecary items to {filename}")

if __name__ == "__main__":
    # Path configuration
    master = "./tools/data/master_compound_list.csv"
    aug = "./tools/data/augmented_candidates.csv"

    apothecary = ApothecarySearcher(master, aug)

    apothecary.run_spice_rack()
    apothecary.run_poison_garden()
    apothecary.run_medicine_cabinet()
    apothecary.run_pantry()

    apothecary.save()