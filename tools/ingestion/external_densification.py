import json
import os
import logging
import time
import random
import re
import requests
from tqdm import tqdm

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/10_text_mining")
OUTPUT_DIR = os.path.normpath("./tools/data/11_external_densification")
LOG_DIR = "./tools/logs"

# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/external_scraper.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ExternalScraper")

class ExternalScraper:
    def __init__(self):
        self.stats = {
            "processed": 0,
            "pubchem_hit": 0,
            "nist_hit": 0,
            "recovered_nfpa": 0,
            "recovered_thermo": 0,
            "repaired_joback": 0,
            "errors": 0
        }
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'ResearchBot/1.0 (internal-research; contact@example.com)'})

    def safe_update(self, dictionary, key, value, source_note=""):
        """Updates dictionary if value is missing/estimate, or if source is superior."""
        current = dictionary.get(key)

        # Check if current is an estimate or missing
        is_missing = current in [None, 0, 0.0, ""]
        is_estimate = False
        if isinstance(current, dict):
            if current.get("value_k") in [None, 0]: is_missing = True
            if "Joback" in current.get("notes", ""): is_estimate = True

        # We overwrite if it's missing OR if we are replacing an estimate with Experimental data
        if is_missing or is_estimate:
            # Format nicely
            if isinstance(value, dict):
                dictionary[key] = value
            else:
                # Basic float/string
                if "enthalpy" in key:
                    dictionary[key] = {"value_kj_mol": value, "notes": source_note}
                elif "_k" in key or "point" in key: # Temperatures
                    dictionary[key] = {"value_k": value, "notes": source_note}
                else:
                    dictionary[key] = value
            return True
        return False

    def clean_nist_value(self, text):
        # NIST often returns "123.4 ± 2.1". We want 123.4
        try:
            clean = text.split("±")[0].strip()
            return float(clean)
        except: return None

    def fetch_pubchem_data(self, cid):
        """Fetches experimental properties from PubChem View API."""
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON?heading=Experimental+Properties"
        try:
            # Respect rate limits (Max 5 req/sec is PubChem rule, we go slower)
            time.sleep(0.25)
            resp = self.session.get(url, timeout=5)
            if resp.status_code != 200: return None

            data = resp.json()
            return data
        except: return None

    def parse_pubchem(self, data, phys_dict, safe_dict):
        # Navigate the crazy PubChem JSON structure
        # Record -> Section -> Section -> Information -> Value
        found_data = False

        try:
            sections = data['Record']['Section'][0]['Section']
            for sec in sections:
                heading = sec.get('TOCHeading')

                # --- SAFETY (NFPA) ---
                # Usually in a different API section ("Safety and Hazards"), but sometimes here.
                # Note: For robust NFPA, we often need the "Safety" heading, not "Experimental Properties".
                # To save requests, we'll check what we get.

                # --- PHYSICAL PROPERTIES ---
                if heading in ["Physical Description", "Color", "Odor"]:
                    # These are text fields, good for sensory
                    pass

                info_list = sec.get('Information', [])
                for info in info_list:
                    val_obj = info.get('Value', {})
                    # Usually "StringWithMarkup" or "Number"
                    val_str = val_obj.get('StringWithMarkup', [{}])[0].get('String')
                    if not val_str: val_str = str(val_obj.get('Number', [0])[0])

                    if not val_str: continue

                    # 1. Boiling Point
                    if heading == "Boiling Point":
                        # Parse "100 C", "373 K", "212 F"
                        k = self.parse_temp(val_str)
                        if k and self.safe_update(phys_dict, "boiling_point", k, "Experimental (PubChem)"):
                            self.stats["repaired_joback"] += 1
                            found_data = True

                    # 2. Melting Point
                    if heading == "Melting Point":
                        k = self.parse_temp(val_str)
                        if k and self.safe_update(phys_dict, "melting_point", k, "Experimental (PubChem)"):
                            self.stats["repaired_joback"] += 1
                            found_data = True

                    # 3. Density
                    if heading == "Density":
                        # Regex for number
                        match = re.search(r"([\d\.]+)", val_str)
                        if match:
                            d = float(match.group(1))
                            if d < 30.0: # Sanity check (g/cm3)
                                self.safe_update(phys_dict, "density_g_cm3", d, "Experimental (PubChem)")
                                found_data = True

        except Exception as e:
            pass # Structure mismatch is common in PubChem

        return found_data

    def fetch_nist_thermo(self, cas):
        """Scrapes NIST Webbook for Enthalpy."""
        # URL for Gas Phase Thermochemistry
        url = f"https://webbook.nist.gov/cgi/cbook.cgi?ID=C{cas}&Units=SI&Mask=1"
        try:
            time.sleep(0.3)
            resp = self.session.get(url, timeout=5)
            if resp.status_code != 200: return None

            # Simple Regex Scraping (Robust enough for NIST's static HTML)
            # Look for: "fH&deg;<sub>gas</sub>" followed by table row
            text = resp.text

            results = {}

            # Enthalpy of Formation (Gas)
            # Pattern matches the Value in the first cell after the label
            # <td class="cal">123.4</td>

            if "fH" in text and "gas" in text:
                # Find the row
                # Very rough regex, implies standard table structure
                # "Enthalpy of formation" ... value ... units
                # We specifically look for the deltafH gas row
                match = re.search(r"fH.*gas.*?>\s*(-?[\d\.]+)\s*±?\s*([\d\.]*)", text, re.IGNORECASE)
                if match:
                    results["h_form"] = float(match.group(1))

            # Entropy (S gas)
            if "S&deg;<sub>gas" in text:
                match = re.search(r"S.*gas.*?>\s*(-?[\d\.]+)", text, re.IGNORECASE)
                if match:
                    results["entropy"] = float(match.group(1))

            return results
        except: return None

    def parse_temp(self, text):
        """Standardizes temperature to Kelvin."""
        try:
            text = text.lower().replace(",", "")
            # Find first number
            match = re.search(r"(-?[\d\.]+)", text)
            if not match: return None
            val = float(match.group(1))

            if " c" in text: return val + 273.15
            if " f" in text: return (val - 32) * 5/9 + 273.15
            if " k" in text: return val
            # Default assumption if valid chemistry number? Assume C if small, K if large?
            # Safer to ignore if no unit found to avoid bad data.
            return None
        except: return None

    def process_file(self, filename):
        filepath = os.path.join(INPUT_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: return

        if "identity" in data: root = data
        else: root = data.setdefault("compound", {})

        ident = root.setdefault("identity", {})
        props = root.setdefault("properties", {})
        phys = props.setdefault("physical", {})
        thermo = props.setdefault("thermodynamics", {})
        safe = root.setdefault("safety", {})

        cas = ident.get("cas_rn")
        cid = None
        # Try to get CID from refs
        refs = root.get("cross_references", {}) or root.get("meta", {}).get("cross_references", {})
        # Flatten refs if list
        if isinstance(refs, list):
            # Not handled here for simplicity, assuming standardized dict from previous steps
            pass
        else:
            cid = refs.get("pubchem_cid")

        # --- 1. PUBCHEM (Properties & Safety) ---
        if cid:
            pc_data = self.fetch_pubchem_data(cid)
            if pc_data:
                self.stats["pubchem_hit"] += 1
                self.parse_pubchem(pc_data, phys, safe)

        # --- 2. NIST (Thermodynamics) ---
        # Only query if we have a valid CAS and missing H_form or it's a Joback estimate
        h_curr = thermo.get("enthalpy_formation_kj_mol")
        needs_thermo = (h_curr is None) or (isinstance(h_curr, dict) and "Joback" in h_curr.get("notes", ""))

        if cas and needs_thermo:
            # Clean CAS (remove checksum if needed? NIST usually fine with dashes)
            nist_data = self.fetch_nist_thermo(cas)
            if nist_data:
                self.stats["nist_hit"] += 1
                if "h_form" in nist_data:
                    self.safe_update(thermo, "enthalpy_formation_kj_mol", nist_data["h_form"], "Experimental (NIST)")
                    self.stats["recovered_thermo"] += 1
                if "entropy" in nist_data:
                    self.safe_update(thermo, "molar_entropy_j_mol_k", nist_data["entropy"], "Experimental (NIST)")

        # Save
        with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]

        # Sort files to prioritize missing data? For now, simple loop.
        logger.info(f"🚀 Starting EXTERNAL SCRAPER on {len(files)} files...")
        logger.info("⚠️  This will take time due to rate limiting (approx 2 files/sec).")

        # Limit for demo purposes? Or full run?
        # Let's do full run but with robust exception handling
        for f in tqdm(files, desc="Scraping"):
            self.process_file(f)

        logger.info("DONE. Stats:")
        for k, v in self.stats.items():
            logger.info(f"  {k:<30}: {v}")

if __name__ == "__main__":
    ExternalScraper().run()