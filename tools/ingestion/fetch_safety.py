import json
import os
import re
import time
import requests
import logging
from tqdm import tqdm

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/16_deep_recovered")
OUTPUT_DIR = os.path.normpath("./tools/data/17_external_safety")
LOG_DIR = "./tools/logs"
LOG_FILE = os.path.join(LOG_DIR, "external_safety.log")

# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger("ExternalSafety")
file_handler = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
logger.addHandler(file_handler)

class SafetyFetcher:
    def __init__(self):
        self.stats = {
            "processed": 0,
            "pubchem_reqs": 0,
            "wiki_reqs": 0,
            "nfpa_recovered": 0,
            "limits_recovered": 0,
            "errors": 0
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ResearchBot/1.0 (scientific-audit; contact@example.com)'
        })

    def clean_text(self, text):
        return re.sub(r'<[^>]+>', '', str(text)).strip()

    # --- PUBCHEM API ---
    def fetch_pubchem_safety(self, cid):
        """Fetches the Safety and Hazards section from PubChem."""
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON?heading=Safety+and+Hazards"
        try:
            # Rate limit friendly (max 5/sec)
            time.sleep(0.3)
            resp = self.session.get(url, timeout=5)
            if resp.status_code == 200:
                self.stats["pubchem_reqs"] += 1
                return resp.json()
        except: pass
        return None

    def parse_pubchem_nfpa(self, data):
        """Navigates PubChem JSON to find NFPA diamond."""
        try:
            # Traverse: Record -> Section (Safety) -> Section (Hazards ID) -> Section (NFPA)
            sections = data['Record']['Section'][0]['Section']
            for sec in sections:
                if "NFPA" in sec.get('TOCHeading', ''):
                    # Usually contains an image or a text description
                    # Look for Information -> Value -> StringWithMarkup
                    info_list = sec.get('Information', [])
                    for info in info_list:
                        val = info.get('Value', {}).get('StringWithMarkup', [{}])[0].get('String')
                        if val:
                            # Parse "Health: 2, Flammability: 3, Instability: 0"
                            h = re.search(r"Health:?\s*(\d)", val, re.IGNORECASE)
                            f = re.search(r"(?:Fire|Flammability):?\s*(\d)", val, re.IGNORECASE)
                            i = re.search(r"(?:Reactivity|Instability):?\s*(\d)", val, re.IGNORECASE)
                            if h or f:
                                return {
                                    "health": int(h.group(1)) if h else 0,
                                    "flammability": int(f.group(1)) if f else 0,
                                    "instability": int(i.group(1)) if i else 0,
                                    "special": None
                                }
        except: pass
        return None

    # --- WIKIPEDIA SCRAPER ---
    def fetch_wikipedia(self, url):
        try:
            time.sleep(0.3)
            resp = self.session.get(url, timeout=5)
            if resp.status_code == 200:
                self.stats["wiki_reqs"] += 1
                return resp.text
        except: pass
        return None

    def parse_wiki_nfpa(self, html):
        """Parses raw HTML for NFPA table or text."""
        # Wikipedia renders NFPA diamonds often as a table with classes
        # Regex search for the specific visual values in the HTML

        # Look for "Health" cell then the value
        # <th scope="row" style="...">Health</th><td style="...">2</td>
        h = re.search(r"Health.*?<td[^>]*>(\d)</td>", html, re.DOTALL | re.IGNORECASE)
        f = re.search(r"Flammability.*?<td[^>]*>(\d)</td>", html, re.DOTALL | re.IGNORECASE)
        i = re.search(r"(?:Instability|Reactivity).*?<td[^>]*>(\d)</td>", html, re.DOTALL | re.IGNORECASE)

        if h or f:
            return {
                "health": int(h.group(1)) if h else 0,
                "flammability": int(f.group(1)) if f else 0,
                "instability": int(i.group(1)) if i else 0,
                "special": None
            }
        return None

    def process_file(self, filename):
        filepath = os.path.join(INPUT_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: return

        root = data if "identity" in data else data.get("compound", {})

        # Identify Gaps
        safe = root.setdefault("safety", {})
        missing_nfpa = safe.get("nfpa_704", {}).get("health") is None

        # 1. PubChem Recovery (Priority)
        cid = root.get("cross_references", {}).get("pubchem_cid")
        if missing_nfpa and cid:
            pc_data = self.fetch_pubchem_safety(cid)
            if pc_data:
                # Try Extract NFPA
                nfpa = self.parse_pubchem_nfpa(pc_data)
                if nfpa:
                    safe["nfpa_704"] = nfpa
                    self.stats["nfpa_recovered"] += 1
                    missing_nfpa = False
                    logger.info(f"[PubChem] {filename}: Found NFPA {nfpa}")

        # 2. Wikipedia Recovery (Fallback)
        wiki_url = root.get("cross_references", {}).get("wikipedia")
        if missing_nfpa and wiki_url:
            html = self.fetch_wikipedia(wiki_url)
            if html:
                nfpa = self.parse_wiki_nfpa(html)
                if nfpa:
                    safe["nfpa_704"] = nfpa
                    self.stats["nfpa_recovered"] += 1
                    logger.info(f"[Wiki] {filename}: Found NFPA {nfpa}")

        # Save
        out_path = os.path.join(OUTPUT_DIR, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]

        print(f"🌍 Starting EXTERNAL SAFETY RECOVERY on {len(files)} files...")
        print("   Sources: PubChem (Safety API), Wikipedia (Live)")

        # Optimization: Only process files that are MISSING data to save time
        # Pre-scan
        queue = []
        for f in files:
            with open(os.path.join(INPUT_DIR, f), 'r', encoding='utf-8') as fh:
                d = json.load(fh)
                root = d if "identity" in d else d.get("compound", {})
                if root.get("safety", {}).get("nfpa_704", {}).get("health") is None:
                    queue.append(f)

        print(f"   Identified {len(queue)} files missing NFPA data. Processing...")

        for f in tqdm(queue):
            self.process_file(f)

        logger.info("Stats: " + json.dumps(self.stats))
        print("\n------------------------------------------------")
        print(f"RECOVERY REPORT:")
        print(f"  Requests:       {self.stats['pubchem_reqs'] + self.stats['wiki_reqs']}")
        print(f"  NFPA Recovered: {self.stats['nfpa_recovered']}")
        print("------------------------------------------------")

if __name__ == "__main__":
    SafetyFetcher().run()