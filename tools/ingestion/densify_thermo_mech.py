import json
import os
import logging
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from tqdm import tqdm

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/07_property_densification")
OUTPUT_DIR = os.path.normpath("./tools/data/08_thermo_mech_densification")
LOG_DIR = "./tools/logs"

# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/thermo_mech_densify.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ThermoMechDensifier")

class AdvancedDensifier:
    def __init__(self):
        self.stats = {
            "processed": 0,
            "calc_thermo": 0,
            "calc_mag_susceptibility": 0,
            "cleaned_mech_na": 0,
            "extracted_econ": 0,
            "errors": 0
        }

        # Pascal's Constants for Magnetic Susceptibility (cm^3/mol * 10^-6)
        # Source: CRC Handbook
        self.pascal_constants = {
            1: -2.93,   # H
            5: -7.0,    # B
            6: -6.0,    # C
            7: -5.55,   # N (Ring?) - using avg
            8: -4.61,   # O
            9: -6.3,    # F
            15: -26.3,  # P
            16: -15.0,  # S
            17: -20.1,  # Cl
            35: -30.6,  # Br
            53: -44.6   # I
        }

        # Kopp's Law Constants for Heat Capacity (J/mol*K) (Standard Conditions, Solid/Liquid)
        self.kopp_constants = {
            1: 9.6,   # H
            5: 11.0,  # B
            6: 7.5,   # C
            7: 25.0,  # N
            8: 16.7,  # O
            9: 21.0,  # F
            14: 15.9, # Si
            15: 23.0, # P
            16: 22.6, # S
            17: 25.0, # Cl
            35: 26.0, # Br
            53: 26.0  # I
        }

    def safe_update(self, dictionary, key, value):
        if value is not None and (dictionary.get(key) in [None, 0, 0.0, ""]):
            dictionary[key] = value
            return True
        return False

    def calculate_thermo(self, mol):
        # 1. Heat Capacity (Cp) using Kopp's Law
        # Cp = Sum(N_i * C_i)
        cp = 0
        for atom in mol.GetAtoms():
            an = atom.GetAtomicNum()
            cp += self.kopp_constants.get(an, 26.0) # Default to 26 for heavier atoms

        # 2. Enthalpy of Combustion (H_comb) - Rough Estimate via Stoichiometry
        # Assume complete combustion: CxHyOz + O2 -> CO2 + H2O
        # H_comb ~= Sum(H_f_products) - Sum(H_f_reactants)
        # Assuming H_f_reactants is small compared to combustion energy for common fuels,
        # or utilizing bond energy approximations.
        # Better heuristic: Thornton's Rule -> E_c = -1.05 * (Stoich_O2_moles) * 418 kJ
        # Stoich O2 = C + H/4 - O/2

        formula_map = {}
        for atom in mol.GetAtoms():
            sym = atom.GetSymbol()
            formula_map[sym] = formula_map.get(sym, 0) + 1

        c = formula_map.get('C', 0)
        h = formula_map.get('H', 0)
        o = formula_map.get('O', 0)
        s = formula_map.get('S', 0)

        if c > 0: # Only organic
            moles_o2 = c + (h/4) + (s) - (o/2)
            # Thornton's rule: ~418 kJ per mole of O2 consumed
            # Result is negative (exothermic)
            h_comb = -1.0 * moles_o2 * 418.0

            return round(cp, 2), round(h_comb, 2)

        return round(cp, 2), None

    def calculate_mag_susceptibility(self, mol):
        # Pascal's constants method (Pascal's Triangle? No, Pascal's Additivity)
        chi_m = 0
        for atom in mol.GetAtoms():
            an = atom.GetAtomicNum()
            chi_m += self.pascal_constants.get(an, -10.0) # Default generic diamagnetic

        # Constitutive corrections (simplified: +5.5 for aromatic rings)
        ri = mol.GetRingInfo()
        # Count aromatic rings
        aromatic_count = 0
        for ring in ri.AtomRings():
            is_aromatic = True
            for idx in ring:
                if not mol.GetAtomWithIdx(idx).GetIsAromatic():
                    is_aromatic = False
                    break
            if is_aromatic: aromatic_count += 1

        chi_m -= (aromatic_count * 5.5) # Ring current diamagnetism adds negative value?
        # Actually Pascal aromatic correction is usually negative (more diamagnetic)

        return round(chi_m, 2)

    def process_file(self, filename: str):
        filepath = os.path.join(INPUT_DIR, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: return

        if "identity" in data: root = data
        else: root = data.setdefault("compound", {})

        ident = root.setdefault("identity", {})
        props = root.setdefault("properties", {})
        thermo = props.setdefault("thermodynamics", {})
        electro = props.setdefault("electromagnetic", {})
        mech = props.setdefault("mechanical", {})
        mat = props.setdefault("material_science", {})
        phys = props.setdefault("physical", {})
        econ = root.setdefault("economics", {})
        meta = root.get("meta", {}) # Check root meta

        smiles = ident.get("smiles")
        mol = None
        if smiles and len(smiles) > 1:
            try: mol = Chem.MolFromSmiles(smiles)
            except: pass

        # --- 1. THERMO CALCULATION ---
        if mol:
            cp, h_comb = self.calculate_thermo(mol)
            t_up = 0
            t_up += self.safe_update(thermo, "heat_capacity_j_mol_k", cp)
            if h_comb:
                t_up += self.safe_update(thermo, "enthalpy_combustion_kj_mol", h_comb)
            if t_up: self.stats["calc_thermo"] += 1

            # --- 2. ELECTRO CALCULATION ---
            chi = self.calculate_mag_susceptibility(mol)
            if self.safe_update(electro, "magnetic_susceptibility_cm3_mol", chi):
                self.stats["calc_mag_susceptibility"] += 1

        # --- 3. MECHANICAL / MAT SCI CLEANING ---
        # If not solid, set Mech/Mat to N/A
        state = phys.get("state_25_k_1_atm", "Unknown")
        if state in ["Liquid", "Gas"]:
            m_up = 0
            # Mechanical
            for k in ["bulk_modulus_gpa", "shear_modulus_gpa", "youngs_modulus_gpa", "mohs_hardness"]:
                m_up += self.safe_update(mech, k, "N/A")
            # Mat Sci
            for k in ["crystal_structure", "space_group"]:
                m_up += self.safe_update(mat, k, "N/A")

            if m_up: self.stats["cleaned_mech_na"] += 1

        # --- 4. ECONOMICS EXTRACTION ---
        # Look in meta -> csv_source_data
        csv_data = meta.get("csv_source_data", {})
        e_up = 0

        # Production Volume
        prod_vol_lbs = csv_data.get("PRODUCTION_VOLUME_LBS")
        if prod_vol_lbs and econ.get("production_volume", {}).get("value_kg_year", 0) == 0:
            try:
                # Basic parsing "500000" or "1000-5000"
                # Take max if range? Or just raw string?
                # Schema expects float.
                clean_vol = prod_vol_lbs.replace(",", "").split("-")[-1].strip() # Take upper bound
                vol_kg = float(clean_vol) * 0.453592 # lbs to kg
                econ["production_volume"] = {
                    "value_kg_year": round(vol_kg, 2),
                    "original_string": prod_vol_lbs
                }
                e_up += 1
            except: pass

        # Uses
        if "INDUSTRIAL_FUNCTIONS" in csv_data and not econ.get("industrial_uses"):
            uses = [u.strip() for u in csv_data["INDUSTRIAL_FUNCTIONS"].split(";")]
            econ["industrial_uses"] = uses
            e_up += 1

        if "CONSUMER_FUNCTIONS" in csv_data and not econ.get("consumer_uses"):
            uses = [u.strip() for u in csv_data["CONSUMER_FUNCTIONS"].split(";")]
            econ["consumer_uses"] = uses
            e_up += 1

        if e_up: self.stats["extracted_econ"] += 1

        # Save
        with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        logger.info(f"🚀 Starting ADVANCED Densification on {len(files)} files...")
        for f in tqdm(files, desc="Densifying"):
            self.process_file(f)
        logger.info("DONE. Stats:")
        for k, v in self.stats.items():
            logger.info(f"  {k:<25}: {v}")

if __name__ == "__main__":
    AdvancedDensifier().run()