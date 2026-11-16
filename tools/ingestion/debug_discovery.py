import logging
import time
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- 1. HYPER-VERBOSE LOGGING ---
logging.basicConfig(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger("DebugDiscovery")
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class DebugTraverser:
    HEADERS = {
        'User-Agent': 'CurieosityBot/1.0 (EducationalGame; +http://github.com/curieosity)',
        'Accept': 'application/json'
    }
    SPARQL_URL = "https://query.wikidata.org/sparql"

    def __init__(self):
        self.session = self._create_robust_session()

    def _create_robust_session(self):
        sess = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        sess.mount("https://", adapter)
        sess.headers.update(self.HEADERS)
        return sess

    # --- TEST 1: SPECIFIC PAGES ---
    def test_specific_entities(self):
        """
        Goal: Verify we can fetch data for specific, known items.
        Targets: Benzene (Q2270), TNT (Q178964), Prussian Blue (Q412840)
        """
        logger.info("\n=== TEST 1: FETCHING SPECIFIC PAGES ===")
        targets = [
            ("Benzene", "Q2270"),
            ("TNT", "Q178964"),
            ("Prussian Blue", "Q412840")
        ]

        # Simple query: Get the label and CAS number for a specific ID
        query_template = """
        SELECT ?label ?cas WHERE {{
          wd:{QID} rdfs:label ?label .
          FILTER(LANG(?label) = "en")
          OPTIONAL {{ wd:{QID} wdt:P231 ?cas . }}
        }}
        LIMIT 1
        """

        for name, qid in targets:
            logger.info(f"👉 Target: {name} ({qid})")
            query = query_template.format(QID=qid)

            start_time = time.time()
            try:
                r = self.session.get(self.SPARQL_URL, params={'format': 'json', 'query': query}, timeout=10)
                duration = time.time() - start_time

                if r.status_code == 200:
                    data = r.json()
                    bindings = data.get('results', {}).get('bindings', [])
                    if bindings:
                        res = bindings[0]
                        label = res.get('label', {}).get('value')
                        cas = res.get('cas', {}).get('value', 'N/A')
                        logger.info(f"   ✅ SUCCESS ({duration:.2f}s) | Label: {label} | CAS: {cas}")
                    else:
                        logger.warning(f"   ⚠️ Query worked, but no data found for {qid}")
                else:
                    logger.error(f"   ❌ FAILED: Status {r.status_code} | {r.text[:100]}")

            except Exception as e:
                logger.error(f"   ❌ EXCEPTION: {e}")

            time.sleep(1) # Be polite

    # --- TEST 2: SMALL SUBSET (OPTIMIZED QUERY) ---
    def test_small_subset_history(self):
        """
        Goal: Run the optimized 'History' query for just 5 items.
        Verifies that the new query structure (no SERVICE call) prevents timeouts.
        """
        logger.info("\n=== TEST 2: SMALL SUBSET (HISTORY STRATEGY) ===")

        # This is the NEW, FAST query from the proposed discovery.py
        # It puts the rarest filter (Discoverer) first and uses rdfs:label directly.
        query = """
        SELECT ?itemLabel ?cas
        WHERE {
          ?item wdt:P61 ?discoverer .        # Primary Filter
          ?item wdt:P662 ?pubchem .          # Secondary Filter
          OPTIONAL { ?item wdt:P231 ?cas . } 
          
          ?item rdfs:label ?itemLabel .
          FILTER(LANG(?itemLabel) = "en")
        }
        LIMIT 5
        """

        logger.info("👉 Sending Query (Limit 5)...")
        start_time = time.time()

        try:
            r = self.session.get(self.SPARQL_URL, params={'format': 'json', 'query': query}, timeout=30)
            duration = time.time() - start_time

            if r.status_code == 200:
                data = r.json()
                items = data.get('results', {}).get('bindings', [])
                logger.info(f"✅ SUCCESS ({duration:.2f}s) | Retrieved {len(items)} items.")

                for i, item in enumerate(items):
                    name = item.get('itemLabel', {}).get('value')
                    cas = item.get('cas', {}).get('value', 'N/A')
                    logger.info(f"   {i+1}. {name} (CAS: {cas})")
            else:
                logger.error(f"❌ FAILED: Status {r.status_code}")
                logger.error(f"Response: {r.text[:200]}")

        except Exception as e:
            logger.error(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    debugger = DebugTraverser()
    debugger.test_specific_entities()
    debugger.test_small_subset_history()