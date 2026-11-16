import json
import os
import logging
import math
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski, GraphDescriptors, rdMolDescriptors
from rdkit import rdBase
from tqdm import tqdm

# --- SILENCE RDKIT C++ LOGS ---
rdBase.LogToPythonLogger()
rd_logger = logging.getLogger("rdkit")
rd_logger.setLevel(logging.CRITICAL)

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/06_deduplicated")
OUTPUT_DIR = os.path.normpath("./tools/data/07_property_densification")
LOG_DIR = "./tools/logs"

# --- LOGGING SETUP ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/property_densification_full.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Densifier")

class PropertyDensifier:
    def __init__(self):
        self.stats = {
            "files_processed": 0,
            "calc_molecular": 0,
            "calc_refractive_index": 0,
            "inferred_state": 0,
            "inferred_na_safety": 0,
            "inferred_na_boiling": 0,
            "corrected_formula": 0,
            "errors": 0
        }

    # --- HELPERS ---
    def is_valid_smiles(self, text):
        if not text or len(text) < 2: return False
        if " " in text or ("-" in text and "[" not in text) or text.isalpha(): return False
        return True

    def safe_update(self, dictionary, key, value, check_zero=True):
        """Updates dictionary only if value is currently missing or zero."""
        current = dictionary.get(key)
        # Never overwrite an existing "N/A"
        if isinstance(current, str) and "N/A" in current: return False

        is_missing = current in [None, ""]
        if check_zero and (current == 0 or current == 0.0): is_missing = True

        if is_missing and value is not None:
            dictionary[key] = value
            return True
        return False

    def get_value_from_prop(self, prop_obj):
        """Extracts raw value from complex property object (value/unit/notes) or simple value."""
        if isinstance(prop_obj, dict):
            return prop_obj.get("value_k") or prop_obj.get("value_g_cm3") or prop_obj.get("value")
        return prop_obj

    # --- LOGIC ENGINES ---
    def determine_flammability(self, mol):
        """Returns False if molecule is chemically non-flammable (Inorganic, Fully Halogenated)."""
        # 1. Check for Carbon (Inorganic check)
        has_carbon = any(atom.GetAtomicNum() == 6 for atom in mol.GetAtoms())
        if not has_carbon: return False # Inorganic (mostly)

        # 2. Check for Hydrogens (if C exists but H doesn't, e.g. CCl4, it's often non-flammable)
        has_hydrogen = any(atom.GetAtomicNum() == 1 for atom in mol.GetAtoms())
        if not has_hydrogen:
            # Exception: CS2 is flammable, but CCl4, CO2 are not.
            # Heuristic: If Halogen count > Carbon count and H=0 -> Non-flammable solvent
            return False

        return True # Default to assuming flammable/combustible if Organic

    def calculate_refractive_index(self, mol, density_g_cm3):
        """
        Calculates nD using the Lorentz-Lorenz equation:
        (n^2 - 1) / (n^2 + 2) = (R_m * rho) / MW
        Where R_m is Molar Refractivity (Crippen).
        """
        if not density_g_cm3 or density_g_cm3 <= 0: return None
        try:
            mr = Crippen.MolMR(mol) # Molar Refractivity
            mw = Descriptors.ExactMolWt(mol)

            # Molar Volume
            vol_m = mw / density_g_cm3

            # The "X" term in the equation
            x = mr / vol_m

            # Physical limit: X must be < 1 for real refractive index
            if x >= 1 or x <= 0: return None

            # Solve for n
            # n = sqrt( (1 + 2X) / (1 - X) )
            n_squared = (1 + 2*x) / (1 - x)
            n = math.sqrt(n_squared)
            return round(n, 4)
        except:
            return None

    def process_file(self, filename: str):
        filepath = os.path.join(INPUT_DIR, filename)
        outpath = os.path.join(OUTPUT_DIR, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read {filename}: {e}")
            self.stats["errors"] += 1
            return

        # --- DATA STRUCTURE NAVIGATION ---
        # Handle both root-level and compound-wrapped structures
        if "identity" in data:
            root = data
        else:
            root = data.setdefault("compound", {})

        ident = root.setdefault("identity", {})
        props = root.setdefault("properties", {})

        mol_props = props.setdefault("molecular", {})
        phys_props = props.setdefault("physical", {})
        safe_props = root.setdefault("safety", {})

        smiles = ident.get("smiles")
        mol = None

        if self.is_valid_smiles(smiles):
            try:
                mol = Chem.MolFromSmiles(smiles)
                # No sanitization here to allow calculation on messy but valid SMILES
            except: pass

        if mol:
            # ==========================================
            # 1. MOLECULAR DESCRIPTORS (High Confidence)
            # ==========================================
            m_up = 0
            m_up += self.safe_update(mol_props, "mass_g_mol", round(Descriptors.ExactMolWt(mol), 4))
            m_up += self.safe_update(mol_props, "logp", round(Descriptors.MolLogP(mol), 3), check_zero=False)
            m_up += self.safe_update(mol_props, "complexity", round(GraphDescriptors.BertzCT(mol), 1))
            m_up += self.safe_update(mol_props, "charge", Chem.GetFormalCharge(mol), check_zero=False)
            m_up += self.safe_update(mol_props, "tpsa", round(Descriptors.TPSA(mol), 2), check_zero=False)

            # Counts
            m_up += self.safe_update(mol_props, "h_bond_donor_count", Descriptors.NumHDonors(mol), check_zero=False)
            m_up += self.safe_update(mol_props, "h_bond_acceptor_count", Descriptors.NumHAcceptors(mol), check_zero=False)
            m_up += self.safe_update(mol_props, "rotatable_bond_count", Descriptors.NumRotatableBonds(mol), check_zero=False)
            m_up += self.safe_update(mol_props, "atom_count", mol.GetNumAtoms(), check_zero=False)
            m_up += self.safe_update(mol_props, "ring_count", Descriptors.RingCount(mol), check_zero=False)

            # Formula Correction
            calc_formula = rdMolDescriptors.CalcMolFormula(mol)
            if self.safe_update(ident, "formula", calc_formula):
                self.stats["corrected_formula"] += 1

            if m_up > 0: self.stats["calc_molecular"] += 1

            # ==========================================
            # 2. PHYSICAL CALCULATIONS & INFERENCE
            # ==========================================

            # A. Refractive Index Calculation
            # Only if we have Density but missing Refractive Index
            curr_ri = phys_props.get("refractive_index")
            curr_density = self.get_value_from_prop(phys_props.get("density_g_cm3"))

            if (curr_ri is None or curr_ri == 0) and (curr_density and isinstance(curr_density, (int, float))):
                calc_ri = self.calculate_refractive_index(mol, curr_density)
                if calc_ri:
                    phys_props["refractive_index"] = calc_ri
                    self.stats["calc_refractive_index"] += 1

            # B. State of Matter Inference
            # If MP/BP exist, we can determine state at STP (298.15 K)
            curr_state = phys_props.get("state_25_k_1_atm")
            mp = self.get_value_from_prop(phys_props.get("melting_point"))
            bp = self.get_value_from_prop(phys_props.get("boiling_point"))

            if not curr_state or curr_state == "Unknown":
                new_state = None
                # Standard Logic
                if isinstance(mp, (int, float)):
                    if mp > 298.15: new_state = "Solid"
                    elif isinstance(bp, (int, float)) and bp > 298.15 and mp < 298.15: new_state = "Liquid"
                    elif isinstance(bp, (int, float)) and bp < 298.15: new_state = "Gas"
                elif isinstance(bp, (int, float)):
                    # Fallback if only BP known
                    if bp < 298.15: new_state = "Gas"
                    elif bp > 298.15: new_state = "Liquid" # Assumption, but safer than null

                if new_state:
                    phys_props["state_25_k_1_atm"] = new_state
                    self.stats["inferred_state"] += 1

            # ==========================================
            # 3. SAFETY / N/A ENFORCEMENT
            # ==========================================

            # A. Non-Flammable Logic
            is_flammable = self.determine_flammability(mol)
            if not is_flammable:
                # If chemically non-flammable, set Flash Point / Autoignition to N/A
                s_up = 0
                s_up += self.safe_update(phys_props, "flash_point_k", "N/A", check_zero=False)
                s_up += self.safe_update(phys_props, "autoignition_k", "N/A", check_zero=False)
                s_up += self.safe_update(safe_props, "explosive_limits", "N/A", check_zero=False)
                if s_up > 0: self.stats["inferred_na_safety"] += 1

            # B. Decomposition Logic (Salts/Metals don't usually boil cleanly)
            # Check for salt fragments or metals
            frags = Chem.GetMolFrags(mol)
            has_metal = any(atom.GetAtomicNum() not in {1,6,7,8,9,15,16,17,35,53} for atom in mol.GetAtoms())

            if (len(frags) > 1 or has_metal) and not phys_props.get("boiling_point"):
                # Complex salt or metal with no BP -> Assume decomposition
                phys_props["boiling_point"] = {
                    "value_k": "N/A",
                    "notes": "Ionic solid or metal; likely decomposes before boiling."
                }
                self.stats["inferred_na_boiling"] += 1

        # Write Output
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["files_processed"] += 1

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        logger.info(f"🚀 Starting COMPREHENSIVE Property Densification on {len(files)} files...")

        for f in tqdm(files, desc="Densifying"):
            self.process_file(f)

        logger.info("DONE. Stats:")
        for k, v in self.stats.items():
            logger.info(f"  {k:<25}: {v}")

if __name__ == "__main__":
    PropertyDensifier().run()