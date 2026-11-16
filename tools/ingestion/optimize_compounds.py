import json
import os
import re
import logging
from tqdm import tqdm
from rdkit import Chem
from rdkit.Chem import Descriptors

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/13_internal_mining")
# We still side-load from RAW to catch things we might have missed in step 13
RAW_DIR = os.path.normpath("./tools/data/full_compounds")
OUTPUT_DIR = os.path.normpath("./tools/data/14_optimized")
LOG_DIR = "./tools/logs"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[logging.FileHandler(f"{LOG_DIR}/optimization.log", mode='w', encoding='utf-8')]
)
logger = logging.getLogger("Optimizer")

class ChemicalOptimizer:
    def __init__(self):
        self.stats = {
            "processed": 0,
            "state_inferred": 0,
            "entropy_calculated": 0,
            "nfpa_recovered": 0,
            "limits_recovered": 0,
            "price_recovered": 0,
            "dipole_recovered": 0,
            "density_recovered": 0
        }

    def clean_text(self, text):
        if not text: return ""
        text = re.sub(r'\[\d+\]', '', str(text))
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    def parse_float(self, text):
        # Aggressive float parser: takes the first valid number it sees
        # Handles "1.2 (gas)" -> 1.2
        match = re.search(r"(-?[\d\.]+)", str(text).replace(",", ""))
        if match:
            try: return float(match.group(1))
            except: pass
        return None

    # --- 1. STATE INFERENCE (Aggressive) ---
    def infer_state(self, phys):
        current = phys.get("state_25_k_1_atm")
        # Overwrite if missing or generic placeholder
        if current and current not in ["N/A", "Unknown", "None", ""]: return False

        mp = phys.get("melting_point", {}).get("value_k")
        bp = phys.get("boiling_point", {}).get("value_k")

        # STP = 298.15 K
        state = None

        # Priority 1: Boiling Point (Gas vs Liquid/Solid)
        if bp and bp < 293.15:
            state = "Gas"

        # Priority 2: Melting Point (Solid vs Liquid)
        elif mp:
            if mp > 303.15: # Safety margin above 25C
                state = "Solid"
            elif mp < 283.15 and (not bp or bp > 323.15):
                # Melts well below room temp, boils well above (or unknown BP)
                state = "Liquid"

        # Priority 3: Combined
        if not state and mp and bp:
            if mp < 298.15 < bp:
                state = "Liquid"

        if state:
            phys["state_25_k_1_atm"] = state
            return True
        return False

    # --- 2. ENTROPY CALCULATION (Joback) ---
    def calculate_entropy(self, root):
        thermo = root.setdefault("properties", {}).setdefault("thermodynamics", {})
        if thermo.get("molar_entropy_j_mol_k"): return False

        smiles = root.get("identity", {}).get("smiles")
        if not smiles: return False

        try:
            mol = Chem.MolFromSmiles(smiles)
            if not mol: return False

            # S_est = Base + (Heavy * 10) + (Rotatable * 20)
            # Refined coefficients for organic compounds
            num_heavy = mol.GetNumHeavyAtoms()
            num_rot = Descriptors.NumRotatableBonds(mol)
            num_rings = Descriptors.RingCount(mol)

            # Base S approx 190 J/mol K
            s_est = 190.0 + (39.0 * num_heavy) + (10.0 * num_rot) - (20.0 * num_rings)
            # Normalize for large molecules (dampening)
            if s_est > 1000: s_est *= 0.9

            thermo["molar_entropy_j_mol_k"] = round(s_est, 2)
            thermo["entropy_method"] = "Estimated (Joback/RDKit)"
            return True
        except: return False

    # --- 3. RECURSIVE PRICE CRAWLER ---
    def find_price(self, data):
        """Scans every string in the JSON tree for price signals"""
        if isinstance(data, dict):
            for k, v in data.items():
                res = self.find_price(v)
                if res: return res
        elif isinstance(data, list):
            for item in data:
                res = self.find_price(item)
                if res: return res
        elif isinstance(data, str):
            # Price Signals: "$", "USD", "EUR" combined with number
            if any(s in data for s in ["$", "USD", "EUR", "£", "€"]):
                # Look for "$100" or "100 USD" or "50/kg"
                # Regex: Currency symbol OR code, optional space, number, optional /unit
                match = re.search(r"(?:[\$€£¥]|USD|EUR)\s?([\d,\.]+)", data, re.IGNORECASE)
                if match:
                    try:
                        return float(match.group(1).replace(",", ""))
                    except: pass
        return None

    # --- 4. SURGICAL MINING (Regex++ ) ---
    def mine_missing(self, root, wiki_raw):
        if not wiki_raw: return False
        updated = False

        phys = root.setdefault("properties", {}).setdefault("physical", {})
        safe = root.setdefault("safety", {})
        econ = root.setdefault("economics", {})

        # A. Explosive Limits (Range Parser)
        if not safe.get("explosive_limits", {}).get("lower_percent"):
            raw = self.clean_text(wiki_raw.get("Explosive limits"))
            if raw:
                # Matches: "1.2-8%", "1.2 to 8.0", "1.2%"
                matches = re.findall(r"([\d\.]+)", raw)
                if len(matches) >= 2:
                    try:
                        vals = sorted([float(m) for m in matches])
                        safe["explosive_limits"] = {"lower_percent": vals[0], "upper_percent": vals[-1]}
                        self.stats["limits_recovered"] += 1
                        updated = True
                    except: pass
                elif len(matches) == 1:
                    # Assume single value is Lower Limit (safety conservative)
                    try:
                        safe["explosive_limits"] = {"lower_percent": float(matches[0]), "upper_percent": None}
                        self.stats["limits_recovered"] += 1
                        updated = True
                    except: pass

        # B. NFPA 704 (Template Parser)
        if not safe.get("nfpa_704", {}).get("health"):
            raw = str(wiki_raw)
            # 1. Wiki Template: H=2 | F=3
            h = re.search(r"H\s*[=:]\s*(\d)", raw, re.IGNORECASE)
            f = re.search(r"F\s*[=:]\s*(\d)", raw, re.IGNORECASE)
            i = re.search(r"[RI]\s*[=:]\s*(\d)", raw, re.IGNORECASE) # Instability or Reactivity

            if h and f:
                safe["nfpa_704"] = {
                    "health": int(h.group(1)),
                    "flammability": int(f.group(1)),
                    "instability": int(i.group(1)) if i else 0
                }
                self.stats["nfpa_recovered"] += 1
                updated = True
            else:
                # 2. Sequential: "2 3 0"
                seq = re.search(r"NFPA.*?(\d)\s+[-–,]\s+(\d)\s+[-–,]\s+(\d)", raw)
                if seq:
                    safe["nfpa_704"] = {
                        "health": int(seq.group(1)),
                        "flammability": int(seq.group(2)),
                        "instability": int(seq.group(3))
                    }
                    self.stats["nfpa_recovered"] += 1
                    updated = True

        # C. Dipole Moment (Relaxed)
        if not phys.get("dipole_moment_debye"):
            raw = wiki_raw.get("Dipole moment")
            if raw:
                # Just get the number, ignore unit "D" requirement
                val = self.parse_float(raw)
                if val is not None:
                    phys["dipole_moment_debye"] = val
                    self.stats["dipole_recovered"] += 1
                    updated = True

        # D. Density (Unit relaxed)
        if not phys.get("density_g_cm3"):
            raw = wiki_raw.get("Density")
            if raw:
                # Accept g/cm3, g/mL, kg/m3 (divide by 1000)
                val = self.parse_float(raw)
                if val:
                    if "kg/m" in str(raw).lower(): val /= 1000.0
                    phys["density_g_cm3"] = val
                    self.stats["density_recovered"] += 1
                    updated = True

        return updated

    def process_file(self, filename):
        filepath = os.path.join(INPUT_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f: data = json.load(f)
        except: return

        # Load Raw for side-loading
        wiki_raw = None
        raw_path = os.path.join(RAW_DIR, filename)
        if os.path.exists(raw_path):
            try:
                with open(raw_path, 'r') as f:
                    rd = json.load(f)
                    wiki_raw = rd.get("compound", {}).get("additional_context", {}).get("wikipedia_raw")
                    if not wiki_raw:
                        wiki_raw = rd.get("_maintenance", {}).get("rejected_source_context", {}).get("wikipedia_raw")
            except: pass

        root = data if "identity" in data else data.get("compound", {})

        # 1. State Inference
        if self.infer_state(root.get("properties", {}).get("physical", {})):
            self.stats["state_inferred"] += 1

        # 2. Entropy
        if self.calculate_entropy(root):
            self.stats["entropy_calculated"] += 1

        # 3. Surgical Mining
        if wiki_raw:
            self.mine_missing(root, wiki_raw)

        # 4. Deep Price Crawl (Whole File)
        if not root.get("economics", {}).get("market_price", {}).get("value_usd"):
            price = self.find_price(data) # Scan EVERYTHING
            if price:
                root.setdefault("economics", {})["market_price"] = {
                    "value_usd": price,
                    "unit_basis": "Unknown (Deep Crawl)"
                }
                self.stats["price_recovered"] += 1

        # 5. Pruning
        if "history" in root: root["history"].pop("significance", None)
        if "pharmacology" in root: root["pharmacology"].pop("indication", None)
        if "properties" in root:
            root["properties"].get("mechanical", {}).pop("speed_of_sound_m_s", None)
            root["properties"].get("material_science", {}).pop("lattice_geometry", None)

        # Save
        with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        print(f"\n⚡ Starting AGGRESSIVE OPTIMIZATION on {len(files)} files")
        print("   Tasks: Overwrite State, Deep Price Crawl, Relaxed Regex")
        print("---------------------------------------------------------------")

        for f in tqdm(files):
            self.process_file(f)

        print("\n---------------------------------------------------------------")
        print("DONE. Stats:")
        for k, v in self.stats.items():
            print(f"  {k:<25}: {v}")

if __name__ == "__main__":
    ChemicalOptimizer().run()