import json
import os
import re
import logging
import csv
from tqdm import tqdm

# --- CONFIGURATION ---
CURRENT_DIR = os.path.normpath("./tools/data/12_wiki_enrichment")
RAW_DIR = os.path.normpath("./tools/data/full_compounds")
OUTPUT_DIR = os.path.normpath("./tools/data/13_internal_mining")
LOG_DIR = "./tools/logs"

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[logging.FileHandler(f"{LOG_DIR}/internal_mining.log", mode='w', encoding='utf-8')]
)
logger = logging.getLogger("InternalMiner")

class InternalMiner:
    def __init__(self):
        self.stats = {
            "processed": 0,
            "raw_found": 0,
            "missing_raw": 0,
            "fields_mined": 0
        }

        self.csv_file = open(f"{LOG_DIR}/internal_mining_details.csv", "w", newline="", encoding="utf-8")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Filename", "Compound", "Field", "Raw_Value", "Parsed_Value"])

    # --- PARSING HELPERS ---
    def clean_val(self, text):
        if not text: return ""
        text = re.sub(r'\[\d+\]', '', str(text)) # Remove [1]
        text = re.sub(r'<[^>]+>', '', text) # Remove HTML
        return text.strip()

    def parse_float(self, text):
        match = re.search(r"(-?[\d\.]+)", str(text).replace(",", ""))
        if match:
            try: return float(match.group(1))
            except: pass
        return None

    def parse_viscosity(self, text):
        """Converts cP, mPa.s to Pa·s"""
        text = self.clean_val(text).lower()
        val = self.parse_float(text)
        if val is None: return None
        if "cp" in text or "mpa" in text: return val / 1000.0
        if "pa" in text: return val
        if "poise" in text: return val / 10.0
        return None

    def parse_pressure(self, text):
        """Converts mmHg, kPa, Pa, bar to atm"""
        text = self.clean_val(text).lower()
        val = self.parse_float(text)
        if val is None: return None

        if "mmhg" in text or "torr" in text: return val / 760.0
        if "kpa" in text: return val / 101.325
        if "mpa" in text: return val * 9.86923
        if "hpa" in text: return val / 1013.25
        if "bar" in text: return val * 0.986923
        if "atm" in text: return val
        return None

    def parse_solubility(self, text):
        """Returns string representation of solubility"""
        text = self.clean_val(text)
        # Often "1.5 g/100 ml" or "Soluble"
        if len(text) > 50: return text[:50] + "..." # Truncate long notes
        return text

    def parse_ld50(self, text):
        """Prioritizes Rat Oral, falls back to generic"""
        text = self.clean_val(text).lower()
        if "rat" in text and "oral" in text:
            return self.parse_float(text)
        if "mg/kg" in text and "dermal" not in text and "rabbit" not in text:
            return self.parse_float(text)
        return None

    def find_wiki_data(self, raw_data):
        if not raw_data: return None
        try:
            res = raw_data.get("compound", {}).get("additional_context", {}).get("wikipedia_raw")
            if res: return res
        except: pass
        try:
            res = raw_data.get("_maintenance", {}).get("rejected_source_context", {}).get("wikipedia_raw")
            if res: return res
        except: pass
        if "wikipedia_raw" in raw_data: return raw_data["wikipedia_raw"]
        return None

    def process_file(self, filename, pbar):
        # 1. Load Current
        current_path = os.path.join(CURRENT_DIR, filename)
        try:
            with open(current_path, 'r', encoding='utf-8') as f: data = json.load(f)
        except: return

        # 2. Side-Load Raw
        raw_path = os.path.join(RAW_DIR, filename)
        wiki = None
        if os.path.exists(raw_path):
            try:
                with open(raw_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                    wiki = self.find_wiki_data(raw_data)
            except: pass

        if wiki: self.stats["raw_found"] += 1
        else: self.stats["missing_raw"] += 1

        # 3. MINE DATA
        if not wiki: # Save and skip if no raw data found
            with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            self.stats["processed"] += 1
            return

        # Schema Pointers
        root = data if "identity" in data else data.get("compound", {})
        props = root.setdefault("properties", {})
        phys = props.setdefault("physical", {})
        thermo = props.setdefault("thermodynamics", {})
        electro = props.setdefault("electromagnetic", {})
        sens = props.setdefault("sensory", {})
        safe = root.setdefault("safety", {})
        econ = root.setdefault("economics", {})
        pharma = root.setdefault("pharmacology", {})
        tox = pharma.setdefault("toxicity", {})

        added_fields = []
        name = root.get("identity", {}).get("name", filename)

        # --- PHYSICAL ---
        if not phys.get("viscosity_pa_s"):
            val = self.parse_viscosity(wiki.get("Viscosity"))
            if val:
                phys["viscosity_pa_s"] = val
                added_fields.append("Visc")

        if not phys.get("vapor_pressure", {}).get("value_atm"):
            raw = wiki.get("Vapor pressure")
            val = self.parse_pressure(raw)
            if val:
                phys["vapor_pressure"] = {"value_atm": val, "temperature_k": 298.15} # Assume RTP if not parsed
                added_fields.append("VapPress")

        if not phys.get("solubility_water", {}).get("qualitative"):
            raw = wiki.get("Solubility in water")
            val = self.parse_solubility(raw)
            if val:
                phys["solubility_water"] = {"qualitative": val}
                added_fields.append("SolWater")

        if not phys.get("refractive_index"):
            raw = wiki.get("Refractive index ( n D )") or wiki.get("Refractive index")
            val = self.parse_float(raw)
            if val and 1.0 < val < 3.0: # Sanity check
                phys["refractive_index"] = val
                added_fields.append("RI")

        # --- SENSORY (Odor/Appearance) ---
        if not sens.get("odor"):
            raw = self.clean_val(wiki.get("Odor"))
            if raw:
                sens["odor"] = raw
                added_fields.append("Odor")

        if not sens.get("appearance"):
            raw = self.clean_val(wiki.get("Appearance"))
            if raw:
                sens["appearance"] = raw
                added_fields.append("Appr")

        # --- THERMO & ELECTRO ---
        if not thermo.get("heat_capacity_j_mol_k"):
            val = self.parse_float(wiki.get("Heat capacity ( C )") or wiki.get("Heat capacity"))
            if val:
                thermo["heat_capacity_j_mol_k"] = val
                added_fields.append("Cp")

        if not thermo.get("molar_entropy_j_mol_k"):
            val = self.parse_float(wiki.get("Standard molar entropy ( S o 298 )") or wiki.get("Entropy"))
            if val:
                thermo["molar_entropy_j_mol_k"] = val
                added_fields.append("Entropy")

        if not electro.get("magnetic_susceptibility_cm3_mol"):
            val = self.parse_float(wiki.get("Magnetic susceptibility (\u03c7)"))
            if val:
                electro["magnetic_susceptibility_cm3_mol"] = val
                added_fields.append("MagSus")

        # --- PHARMACOLOGY ---
        if not pharma.get("bioavailability"):
            raw = self.clean_val(wiki.get("Bioavailability"))
            if raw:
                pharma["bioavailability"] = raw
                added_fields.append("BioAvail")

        if not pharma.get("protein_binding"):
            raw = self.clean_val(wiki.get("Protein binding"))
            if raw:
                pharma["protein_binding"] = raw
                added_fields.append("ProtBind")

        if not pharma.get("metabolism"):
            raw = self.clean_val(wiki.get("Metabolism"))
            if raw:
                pharma["metabolism"] = raw
                added_fields.append("Metab")

        if not pharma.get("pharma_half_life"):
            raw = self.clean_val(wiki.get("Elimination half-life"))
            if raw:
                pharma["pharma_half_life"] = raw
                added_fields.append("HalfLife")

        if not pharma.get("pregnancy_category"):
            raw = self.clean_val(wiki.get("Pregnancy category"))
            if raw:
                pharma["pregnancy_category"] = raw
                added_fields.append("PregCat")

        # --- SAFETY / TOXICITY ---
        if not tox.get("ld50_rat_oral_mg_kg"):
            val = self.parse_ld50(wiki.get("LD 50 ( median dose )") or wiki.get("LD50"))
            if val:
                tox["ld50_rat_oral_mg_kg"] = val
                added_fields.append("LD50")

        if not safe.get("un_number"):
            raw = wiki.get("UN number")
            match = re.search(r"\b(1\d{3}|2\d{3}|3\d{3})\b", str(raw))
            if match:
                safe["un_number"] = match.group(1)
                added_fields.append("UN")

        # --- ECONOMICS (Price) ---
        if not econ.get("market_price", {}).get("value_usd"):
            # Very rare in Wiki, but requested
            raw = wiki.get("Cost") or wiki.get("Price")
            val = self.parse_float(raw)
            if val:
                econ["market_price"] = {"value_usd": val, "unit_basis": "Unknown (Wiki)"}
                added_fields.append("Price")

        # --- FEEDBACK ---
        if added_fields:
            self.stats["fields_mined"] += len(added_fields)
            safe_name = name if len(name) <= 20 else name[:20]
            # Log specific changes to CSV
            for f in added_fields:
                self.csv_writer.writerow([filename, name, f, "Wiki Raw", "Mined"])

            tqdm.write(f"⛏️  {safe_name:<22} | {' '.join(added_fields)}")

        # Save
        with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        files = [f for f in os.listdir(CURRENT_DIR) if f.endswith(".json")]

        print(f"\n⚙️  Starting INTERNAL MINING on {len(files)} files")
        print(f"   Sources: {CURRENT_DIR} + {RAW_DIR}")
        print("---------------------------------------------------------------")

        with tqdm(files, unit="file") as pbar:
            for f in pbar:
                self.process_file(f, pbar)

        self.csv_file.close()
        print("\n---------------------------------------------------------------")
        print("DONE. Stats:")
        for k, v in self.stats.items():
            print(f"  {k:<20}: {v}")
        print(f"  Details saved to: {LOG_DIR}/internal_mining_details.csv")

if __name__ == "__main__":
    InternalMiner().run()