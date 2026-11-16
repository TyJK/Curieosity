import json
import os
import logging
from rdkit import Chem
from tqdm import tqdm

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/08_thermo_mech_densification")
OUTPUT_DIR = os.path.normpath("./tools/data/09_joback_densification")
LOG_DIR = "./tools/logs"

# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/joback_densify_fixed.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("JobackFixed")

class JobackCalculator:
    def __init__(self):
        self.stats = {
            "processed": 0,
            "calc_bp": 0,
            "calc_mp": 0,
            "calc_hform": 0,
            "skipped_unsupported_element": 0,
            "errors": 0
        }

        # JOBACK VALID ELEMENTS
        # H, C, N, O, F, S, Cl, Br, I
        self.allowed_atoms = {1, 6, 7, 8, 9, 16, 17, 35, 53}

        # Raw Group Definitions (Smarts, Tb, Tm, Hform, Gform)
        self.raw_groups = [
            # NON-RING
            ("[CH3;!R]", 23.58, -5.10, -76.45, -43.96),
            ("[CH2;!R]", 22.88, 11.27, -20.64, 8.42),
            ("[CH1;!R]", 21.74, 12.64, 29.89, 58.36),
            ("[CH0;!R]", 18.25, 46.43, 82.23, 116.02),
            ("[CH2]=*", 18.18, -4.32, -9.630, 3.77),
            ("[CH1]=*", 24.96, 8.73, 37.97, 48.53),
            ("[CH0]=*", 24.14, 11.14, 83.99, 92.36),
            ("[$([CH0]=*)=*]", 26.15, 17.78, 142.14, 136.70),
            ("[CH1]#[*]", 9.20, -11.18, 79.30, 77.71),
            ("[CH0]#[*]", 27.38, 64.32, 115.51, 109.82),
            # RING
            ("[CH2;R]", 27.15, 7.75, -26.80, -3.68),
            ("[CH1;R]", 21.78, 19.88, 8.67, 40.99),
            ("[CH0;R]", 21.32, 60.15, 79.72, 87.88),
            ("[CH1;R]=*", 26.73, 8.13, 2.09, 11.30),
            ("[CH0;R]=*", 31.01, 37.02, 46.43, 54.05),
            # HALOGENS
            ("[F]", -0.03, -15.78, -251.92, -247.19),
            ("[Cl]", 38.13, 13.55, -71.55, -64.30),
            ("[Br]", 66.86, 43.43, -29.48, -38.01),
            ("[I]", 93.84, 41.69, 21.06, 5.74),
            # OXYGEN
            ("[OD1]-[C;!$(C=[O,N,S])]", 92.88, 44.45, -208.04, -189.20),
            ("[OD1]-c", 76.34, -1.58, -221.65, -197.37),
            ("[OD2](-[C])-[C]", 22.42, 22.23, -132.22, -105.00),
            ("[OD2;R]", 31.22, 23.05, -138.16, -119.1),
            ("[CD3](=[OD1])(-[C])-[C]", 76.75, 61.27, -133.22, -120.50),
            ("[CD3;R](=[OD1])", 94.97, 75.97, -148.28, -144.96),
            ("[CH1D2](=O)-[C]", 72.24, 36.90, -162.19, -143.48),
            ("[CD3](=[OD1])-[OD1]", 169.09, 155.50, -426.72, -387.87),
            ("[CD3](=[OD1])-[OD2]-[C]", 81.10, 53.60, -337.92, -301.95),
            ("[OD1]=*", -10.0, 0.0, 0.0, 0.0),
            # NITROGEN
            ("[NH2]", 73.23, 66.89, 26.93, 35.88),
            ("[NH1;!R]", 50.17, 52.66, 67.19, 69.15),
            ("[NH1;R]", 52.82, 101.51, 31.46, 30.59),
            ("[NH0;!R]", 11.74, 48.84, 66.53, 26.98),
            ("[nH0,NH0;R]", 57.55, 68.40, 55.60, 36.25),
            ("[C]#[N]", 125.66, 59.89, 88.43, 89.22),
            ("[N+](=O)[O-]", 152.54, 127.24, -66.57, -16.83),
            # SULFUR
            ("[SH1]", 63.56, 20.09, -17.33, -22.99),
            ("[SH0;!R]", 68.78, 34.40, 41.87, 33.12),
            ("[SH0;R]", 52.10, 79.93, 39.10, 27.76)
        ]

        # Compile patterns
        self.groups = [(Chem.MolFromSmarts(x[0]), x[1], x[2], x[3], x[4]) for x in self.raw_groups]

    def calculate(self, mol):
        # 1. STRICT ELEMENT CHECK
        for atom in mol.GetAtoms():
            if atom.GetAtomicNum() not in self.allowed_atoms:
                return "SKIP_UNSUPPORTED_ELEMENT"

        # 2. Count Groups
        total_tb = 0
        total_tm = 0
        total_hf = 0
        matches_found = 0

        for pattern, dtb, dtm, dhf, dgf in self.groups:
            if pattern:
                matches = mol.GetSubstructMatches(pattern)
                count = len(matches)
                if count > 0:
                    total_tb += (count * dtb)
                    total_tm += (count * dtm)
                    total_hf += (count * dhf)
                    matches_found += count

        if matches_found == 0:
            return None

        # 3. Apply Equations
        bp_k = 198 + total_tb
        mp_k = 122.5 + total_tm
        hform_kj = 68.29 + total_hf

        return {
            "boiling_point": round(bp_k, 2),
            "melting_point": round(mp_k, 2),
            "enthalpy_formation": round(hform_kj, 2)
        }

    def safe_update(self, dictionary, key, value, note=None):
        current = dictionary.get(key)

        # 1. Determine if Valid Data Exists
        # A dictionary with "value_k": 0 is considered MISSING for our purposes.
        data_exists = False

        if isinstance(current, dict):
            # Check internal value
            val = current.get("value_k") or current.get("value_kj_mol")
            # We treat 0 and 0.0 as missing data
            if val not in [None, 0, 0.0, ""]:
                data_exists = True
        else:
            # Check direct value
            if current not in [None, 0, 0.0, ""]:
                data_exists = True

        # If valid data exists, DO NOT OVERWRITE
        if data_exists:
            return False

        # 2. Construct New Value
        if note:
            val_key = "value_kj_mol" if "enthalpy" in key else "value_k"
            new_entry = {val_key: value, "notes": note}

            if isinstance(current, dict):
                # Update in place to preserve other keys (like 'sublimes' or 'units' if they exist)
                current.update(new_entry)
            else:
                # Create new dict
                dictionary[key] = new_entry
        else:
            dictionary[key] = value

        return True

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

        smiles = ident.get("smiles")
        if not smiles: return

        try:
            mol = Chem.MolFromSmiles(smiles)
            if not mol: return
        except: return

        results = self.calculate(mol)

        if results == "SKIP_UNSUPPORTED_ELEMENT":
            self.stats["skipped_unsupported_element"] += 1
        elif results:
            note = "Estimated via Joback Method"

            if self.safe_update(phys, "boiling_point", results["boiling_point"], note):
                self.stats["calc_bp"] += 1

            if self.safe_update(phys, "melting_point", results["melting_point"], note):
                self.stats["calc_mp"] += 1

            h_note = "Estimated via Joback Method (Gas Phase)"
            if self.safe_update(thermo, "enthalpy_formation_kj_mol", results["enthalpy_formation"], h_note):
                self.stats["calc_hform"] += 1

        with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        logger.info(f"🚀 Starting JOBACK FIXED Densification on {len(files)} files...")
        for f in tqdm(files, desc="Calculating"):
            self.process_file(f)
        logger.info("DONE. Stats:")
        for k, v in self.stats.items():
            logger.info(f"  {k:<30}: {v}")

if __name__ == "__main__":
    JobackCalculator().run()