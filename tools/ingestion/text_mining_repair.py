import json
import os
import logging
import re
import csv
from tqdm import tqdm

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/09_joback_densification")
OUTPUT_DIR = os.path.normpath("./tools/data/10_text_mining")
LOG_DIR = "./tools/logs"
AUDIT_FILE = os.path.join(LOG_DIR, "mining_audit.csv")

# --- LOGGING SETUP ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# General Log (Console + File)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/text_mining.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TextMiner")

# Audit Log (CSV for review)
audit_file = open(AUDIT_FILE, 'w', newline='', encoding='utf-8')
audit_writer = csv.writer(audit_file)
audit_writer.writerow(["Filename", "Field", "Extracted_Value", "Source", "Context_Snippet"])

class TextMiner:
    def __init__(self):
        self.stats = {
            "processed": 0,
            "mined_history": 0,
            "mined_sensory": 0,
            "mined_nfpa": 0,
            "repaired_joback": 0,
            "errors": 0
        }

        # --- REGEX PATTERNS ---
        # "First isolated in 1832 by..."
        self.re_year = re.compile(r"\b(18\d{2}|19\d{2}|20[0-1]\d)\b")

        # Discoverer heuristics
        self.re_discoverer = re.compile(r"(?:discovered|synthesized|isolated|described|prepared)\s+by\s+([A-Z][a-zA-Z\.\s]+?)(?:\s+in|,|\.|\d|and|with)")

        # Sensory Keywords
        self.odor_keywords = ["pungent", "odorless", "aromatic", "sweet", "fruity", "acrid", "unpleasant", "garlic", "fishy", "almond", "ethereal", "musty"]
        self.app_keywords = ["colorless", "white", "yellow", "crystalline", "powder", "viscous", "oil", "crystals", "solid", "liquid", "gas", "needles", "plates", "prisms"]

    def log_change(self, filename, field, value, source, context=""):
        """Writes to the CSV audit log."""
        # Truncate context/value for CSV readability
        val_str = str(value)[:50].replace("\n", " ")
        ctx_str = str(context)[:50].replace("\n", " ")
        audit_writer.writerow([filename, field, val_str, source, ctx_str])

    def clean_text(self, text):
        if not text: return None
        text = re.sub(r"\[\d+\]", "", text) # Remove [1]
        return text.strip()

    def parse_value_k(self, val_str):
        # Tries to parse "100 C", "212 F", "373 K"
        try:
            val_str = val_str.lower().replace("−", "-").replace("&nbsp;", " ").strip()
            # Regex to find the number part
            num_match = re.search(r"(-?[\d\.]+)", val_str)
            if not num_match: return None
            val = float(num_match.group(1))

            if "k" in val_str:
                return val
            elif "c" in val_str:
                return val + 273.15
            elif "f" in val_str:
                return (val - 32) * 5.0/9.0 + 273.15
            # Default to C if no unit but valid number? Risky. Skip.
            return None
        except:
            return None

    def mine_history(self, filename, text, hist_dict):
        if not text: return False
        updated = False

        # Year
        if not hist_dict.get("year"):
            matches = self.re_year.findall(text)
            if matches:
                # Heuristic: Take the earliest year mentioned that looks plausible
                # Sort unique years
                years = sorted(list(set([int(y) for y in matches])))
                # If description contains "discovered", assume earliest year is it
                if "discover" in text.lower() or "isolat" in text.lower():
                    cand = years[0]
                    hist_dict["year"] = cand
                    self.log_change(filename, "history.year", cand, "Description Regex", f"Found years: {years}")
                    updated = True

        # Discoverer
        if not hist_dict.get("discoverer"):
            match = self.re_discoverer.search(text)
            if match:
                name = match.group(1).strip()
                # Basic sanity check on name length
                if 3 < len(name) < 40 and not any(x in name.lower() for x in ["reaction", "method", "temperature"]):
                    hist_dict["discoverer"] = name
                    self.log_change(filename, "history.discoverer", name, "Description Regex", match.group(0))
                    updated = True

        return updated

    def mine_sensory(self, filename, text, wiki_raw, sens_dict):
        updated = False

        # 1. Wiki Raw Priority
        if wiki_raw:
            if "Appearance" in wiki_raw and not sens_dict.get("appearance"):
                val = self.clean_text(wiki_raw["Appearance"])
                if val:
                    sens_dict["appearance"] = val
                    self.log_change(filename, "sensory.appearance", val, "Wiki Infobox")
                    updated = True

            if "Odor" in wiki_raw and not sens_dict.get("odor"):
                val = self.clean_text(wiki_raw["Odor"])
                if val:
                    sens_dict["odor"] = val
                    self.log_change(filename, "sensory.odor", val, "Wiki Infobox")
                    updated = True

        # 2. Description Fallback
        if text:
            text_lower = text.lower()

            # Odor Search
            if not sens_dict.get("odor"):
                found = [w for w in self.odor_keywords if w in text_lower]
                if found:
                    val = ", ".join(found)
                    sens_dict["odor"] = val
                    self.log_change(filename, "sensory.odor", val, "Description Keywords", f"Matched: {found}")
                    updated = True

            # Appearance Search
            if not sens_dict.get("appearance"):
                found = [w for w in self.app_keywords if w in text_lower]
                if found:
                    # Filter: Don't just say "solid" if we have "white crystalline solid"
                    # Ideally we capture the phrase, but keywords are a safe start
                    val = ", ".join(found)
                    sens_dict["appearance"] = val
                    self.log_change(filename, "sensory.appearance", val, "Description Keywords", f"Matched: {found}")
                    updated = True

        return updated

    def mine_safety(self, filename, wiki_raw, safety_dict):
        if not wiki_raw: return False
        updated = False
        nfpa = safety_dict.setdefault("nfpa_704", {})

        # Check if already populated
        if nfpa.get("health") or nfpa.get("flammability"): return False

        # Wiki Keys: "NFPA 704", "NFPA-H", "Health hazard"
        h = wiki_raw.get("NFPA 704", {}).get("h") or wiki_raw.get("NFPA-H")
        f = wiki_raw.get("NFPA 704", {}).get("f") or wiki_raw.get("NFPA-F")
        r = wiki_raw.get("NFPA 704", {}).get("r") or wiki_raw.get("NFPA-R")

        # Sometimes stored as "Health hazard": "2"
        if not h: h = wiki_raw.get("Health hazard")

        if h or f or r:
            try:
                # Often formatted like "2 (moderate)" - take first char
                if h: nfpa["health"] = int(str(h)[0])
                if f: nfpa["flammability"] = int(str(f)[0])
                if r: nfpa["instability"] = int(str(r)[0])
                self.log_change(filename, "safety.nfpa", f"H:{h} F:{f} R:{r}", "Wiki Infobox")
                updated = True
            except: pass

        return updated

    def repair_experimental(self, filename, wiki_raw, phys_dict):
        if not wiki_raw: return False
        repaired = False

        # Helper to check if a value is a Joback Estimate
        def is_joback(field_key):
            val = phys_dict.get(field_key)
            if isinstance(val, dict) and "Joback" in val.get("notes", ""):
                return True
            if val is None: return True # Treat missing as "repairable"
            return False

        # 1. Boiling Point
        if is_joback("boiling_point"):
            raw_bp = wiki_raw.get("Boiling point")
            if raw_bp:
                k = self.parse_value_k(raw_bp)
                if k:
                    old_val = phys_dict.get("boiling_point", {}).get("value_k") if isinstance(phys_dict.get("boiling_point"), dict) else "None"
                    phys_dict["boiling_point"] = {
                        "value_k": round(k, 2),
                        "notes": "Experimental (Wiki)",
                        "original_string": raw_bp
                    }
                    self.log_change(filename, "physical.boiling_point", f"{round(k, 2)} K", "Wiki Overwrite", f"Replaced Joback: {old_val}")
                    repaired = True

        # 2. Melting Point
        if is_joback("melting_point"):
            raw_mp = wiki_raw.get("Melting point")
            if raw_mp:
                k = self.parse_value_k(raw_mp)
                if k:
                    old_val = phys_dict.get("melting_point", {}).get("value_k") if isinstance(phys_dict.get("melting_point"), dict) else "None"
                    phys_dict["melting_point"] = {
                        "value_k": round(k, 2),
                        "notes": "Experimental (Wiki)",
                        "original_string": raw_mp
                    }
                    self.log_change(filename, "physical.melting_point", f"{round(k, 2)} K", "Wiki Overwrite", f"Replaced Joback: {old_val}")
                    repaired = True

        return repaired

    def process_file(self, filename: str):
        filepath = os.path.join(INPUT_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f: data = json.load(f)
        except: return

        if "identity" in data: root = data
        else: root = data.setdefault("compound", {})

        ident = root.setdefault("identity", {})
        hist = root.setdefault("history", {})
        props = root.setdefault("properties", {})
        phys = props.setdefault("physical", {})
        sens = props.setdefault("sensory", {})
        safe = root.setdefault("safety", {})

        desc = ident.get("description", "")
        # Wiki raw is often in 'additional_context' or root
        wiki_raw = root.get("additional_context", {}).get("wikipedia_raw") or root.get("wikipedia_raw", {})

        # --- MINING ---
        if self.mine_history(filename, desc, hist):
            self.stats["mined_history"] += 1

        if self.mine_sensory(filename, desc, wiki_raw, sens):
            self.stats["mined_sensory"] += 1

        if self.mine_safety(filename, wiki_raw, safe):
            self.stats["mined_nfpa"] += 1

        if self.repair_experimental(filename, wiki_raw, phys):
            self.stats["repaired_joback"] += 1

        # Save
        with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        logger.info(f"🚀 Starting AUDITED Text Mining on {len(files)} files...")

        for f in tqdm(files, desc="Mining"):
            self.process_file(f)

        audit_file.close()
        logger.info("DONE. Stats:")
        for k, v in self.stats.items():
            logger.info(f"  {k:<25}: {v}")
        logger.info(f"Audit log saved to: {AUDIT_FILE}")

if __name__ == "__main__":
    TextMiner().run()