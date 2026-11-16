import json
import os
import re
import logging
from tqdm import tqdm

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/15_inferred") # Using the inferred set as base
OUTPUT_DIR = os.path.normpath("./tools/data/16_deep_recovered")
LOG_DIR = "./tools/logs"
DEBUG_LOG = os.path.join(LOG_DIR, "deep_recovery_debug.txt")

# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("DeepRecover")
# File handler for detailed debug output
file_handler = logging.FileHandler(DEBUG_LOG, mode='w', encoding='utf-8')
logger.addHandler(file_handler)

class DeepRecoverer:
    def __init__(self):
        self.stats = {
            "processed": 0,
            "nfpa_found": 0,
            "limits_found": 0,
            "price_found": 0
        }

    def extract_nfpa_from_text(self, text):
        """
        Scans a text blob for NFPA patterns.
        Handles:
        - {{NFPA 704 | H=2 | F=3 | R=0 }}
        - Health: 2, Flammability: 3
        """
        # 1. Wiki Template Pattern (Most robust)
        # Matches {{NFPA 704 ... }} or {{Chembox NFPA ... }}
        if "NFPA" in text:
            # Extract H/F/I values regardless of order
            h = re.search(r"[\|<]\s*(?:Health|H)\s*=\s*(\d)", text, re.IGNORECASE)
            f = re.search(r"[\|<]\s*(?:Flammability|Fire|F)\s*=\s*(\d)", text, re.IGNORECASE)
            i = re.search(r"[\|<]\s*(?:Instability|Reactivity|R|I)\s*=\s*(\d)", text, re.IGNORECASE)
            s = re.search(r"[\|<]\s*(?:Special|S)\s*=\s*([A-Z]+)", text, re.IGNORECASE)

            if h or f or i:
                return {
                    "health": int(h.group(1)) if h else 0,
                    "flammability": int(f.group(1)) if f else 0,
                    "instability": int(i.group(1)) if i else 0,
                    "special": s.group(1) if s else None
                }

        # 2. Plain Text Pattern
        # "Health 2, Fire 3"
        h = re.search(r"Health\s*[:=]?\s*(\d)", text, re.IGNORECASE)
        f = re.search(r"(?:Flammability|Fire)\s*[:=]?\s*(\d)", text, re.IGNORECASE)

        if h and f:
            return {
                "health": int(h.group(1)),
                "flammability": int(f.group(1)),
                "instability": 0, # Default
                "special": None
            }
        return None

    def extract_limits_from_text(self, text):
        """
        Scans for explosive limits.
        Matches: 1.5-10%, LEL 1.5%, Lower 1.5%
        """
        # Look for percent ranges first
        # "1.5-10.0%" or "1.5 to 10%"
        range_match = re.search(r"(\d+\.?\d*)\s*[-to]+\s*(\d+\.?\d*)\s*%", text)
        if range_match:
            try:
                v1, v2 = float(range_match.group(1)), float(range_match.group(2))
                return {"lower_percent": min(v1, v2), "upper_percent": max(v1, v2)}
            except: pass

        # Look for explicit LEL/UEL
        lel = re.search(r"(?:LEL|Lower|LFL).*?(\d+\.?\d*)", text, re.IGNORECASE)
        uel = re.search(r"(?:UEL|Upper|UFL).*?(\d+\.?\d*)", text, re.IGNORECASE)

        if lel:
            return {
                "lower_percent": float(lel.group(1)),
                "upper_percent": float(uel.group(1)) if uel else None
            }

        return None

    def extract_price_from_text(self, text):
        """
        Scans for bulk pricing indicators.
        Strict requirement: Must have a unit (/kg, /g, /lb, /ton).
        """
        # Regex: Currency symbol + number + space + /unit
        # e.g. $50/kg, $ 100 per gram
        price_pattern = re.search(r"([$€£¥]|USD)\s?([\d,]+\.?\d*)\s*[/p](?:er)?\s*(kg|g|lb|ton|mol|gram|kilo)", text, re.IGNORECASE)

        if price_pattern:
            try:
                val = float(price_pattern.group(2).replace(",", ""))
                unit = price_pattern.group(3).lower()

                # Normalize typical scientific units to "per kg" basis if possible?
                # For now, just capturing is enough.
                original_str = f"{price_pattern.group(1)}{val}/{unit}"

                return {
                    "value_usd": val, # Assuming USD for simplicity if symbol is generic
                    "unit_basis": unit,
                    "original_string": original_str
                }
            except: pass

        return None

    def process_file(self, filename):
        filepath = os.path.join(INPUT_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: return

        root = data if "identity" in data else data.get("compound", {})
        maint = data.get("_maintenance", {})

        # --- THE DRAGNET ---
        # Convert the entire maintenance block to a single searchable string
        # This catches keys we didn't expect ("properties_raw", "infobox", "rejects")
        raw_blob = json.dumps(maint)

        updated = False

        # 1. NFPA Recovery
        if not root.get("safety", {}).get("nfpa_704", {}).get("health"):
            nfpa = self.extract_nfpa_from_text(raw_blob)
            if nfpa:
                root.setdefault("safety", {})["nfpa_704"] = nfpa
                self.stats["nfpa_found"] += 1
                logger.info(f"[NFPA] {filename}: Found {nfpa}")
                updated = True

        # 2. Explosive Limits Recovery
        if not root.get("safety", {}).get("explosive_limits", {}).get("lower_percent"):
            limits = self.extract_limits_from_text(raw_blob)
            if limits:
                root.setdefault("safety", {})["explosive_limits"] = limits
                self.stats["limits_found"] += 1
                logger.info(f"[LIMITS] {filename}: Found {limits}")
                updated = True

        # 3. Price Recovery
        if not root.get("economics", {}).get("market_price", {}).get("value_usd"):
            price = self.extract_price_from_text(raw_blob)
            if price:
                root.setdefault("economics", {})["market_price"] = price
                self.stats["price_found"] += 1
                logger.info(f"[PRICE] {filename}: Found {price}")
                updated = True

        # Save only if we actually found something?
        # No, save all to preserve pipeline integrity.
        out_path = os.path.join(OUTPUT_DIR, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        print(f"🕵️  Starting DEEP RECOVERY on {len(files)} files...")
        print(f"    Scanning raw JSON blobs for patterns...")

        for f in tqdm(files):
            self.process_file(f)

        print("\n------------------------------------------------")
        print("DEEP SCAN RESULTS:")
        print(f"  NFPA Ratings:   {self.stats['nfpa_found']}")
        print(f"  Exp. Limits:    {self.stats['limits_found']}")
        print(f"  Prices:         {self.stats['price_found']}")
        print(f"  Debug Log:      {DEBUG_LOG}")
        print("------------------------------------------------")

if __name__ == "__main__":
    DeepRecoverer().run()