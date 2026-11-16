import json
import os
import math
import logging
import numpy as np
from tqdm import tqdm
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/14_optimized")
OUTPUT_DIR = os.path.normpath("./tools/data/15_inferred")
LOG_DIR = "./tools/logs"
LOG_FILE = os.path.join(LOG_DIR, "property_inference.log")

# Constants
STP_K = 298.15  # 25 degrees C
DEBYE_CONVERSION = 4.803204  # Conversion from e*Angstrom to Debye

# --- SETUP LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Custom formatting for readability
formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%H:%M:%S')

# File Handler
file_handler = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
file_handler.setFormatter(formatter)

# Console Handler (Less verbose)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.WARNING) # Only show warnings/errors in console to keep tqdm clean

logger = logging.getLogger("PropertyInferrer")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class PropertyInferrer:
    def __init__(self):
        self.stats = {
            "processed": 0,
            "state_inferred_solid": 0,
            "state_inferred_liquid": 0,
            "state_inferred_gas": 0,
            "dipole_calc_existing_3d": 0,
            "dipole_calc_smiles_3d": 0,
            "dipole_failed": 0,
            "errors": 0
        }

    def calculate_dipole_moment(self, mol):
        """
        Calculates Dipole Moment in Debye.
        Requires a molecule with a conformer and Computed Gasteiger Charges.
        """
        try:
            # Compute Partial Charges
            AllChem.ComputeGasteigerCharges(mol)
            charges = [float(a.GetDoubleProp('_GasteigerCharge')) for a in mol.GetAtoms()]

            # Get Conformer coordinates
            conf = mol.GetConformer()

            # Dipole Vector (sum of q_i * r_i)
            dipole_vec = np.zeros(3)
            center_of_mass = np.zeros(3) # Technically dipole is independent of origin for neutral molecules, but good practice

            # Calculate Center of Charge (approximate logic, usually origin independence holds for neutral systems)
            # Simplest approach: Sum(q*r)
            for i, charge in enumerate(charges):
                pos = np.array(conf.GetAtomPosition(i))
                dipole_vec += charge * pos

            # Magnitude
            magnitude = np.linalg.norm(dipole_vec)

            # Convert to Debye
            debye = magnitude * DEBYE_CONVERSION
            return round(debye, 3)
        except Exception as e:
            return None

    def process_dipole(self, root):
        """Attempts to calculate dipole moment from existing 3D model, or fallback to SMILES."""
        phys = root.setdefault("properties", {}).setdefault("physical", {})

        # Skip if already present and not zero (unless we want to overwrite '0' placeholders)
        current = phys.get("dipole_moment_debye")
        if current and current > 0:
            return False

        ident = root.get("identity", {})
        media = root.get("media", {})
        name = ident.get("name", "Unknown")

        mol = None
        source = ""

        # Strategy 1: Use Existing 3D Model (Best representation)
        model_data = media.get("model_3d")
        if model_data and isinstance(model_data, str) and len(model_data) > 50:
            try:
                # RDKit often handles MDL MolBlocks
                mol = Chem.MolFromMolBlock(model_data, removeHs=False)
                if mol:
                    source = "Existing 3D"
            except:
                pass

        # Strategy 2: Generate from SMILES (Fallback)
        if not mol:
            smiles = ident.get("smiles")
            if smiles:
                try:
                    mol = Chem.MolFromSmiles(smiles)
                    if mol:
                        mol = Chem.AddHs(mol)
                        # Generate Conformer
                        res = AllChem.EmbedMolecule(mol, AllChem.ETKDG())
                        if res == 0:
                            AllChem.MMFFOptimizeMolecule(mol)
                            source = "SMILES Generated"
                        else:
                            mol = None
                except:
                    pass

        # Calculate
        if mol:
            debye = self.calculate_dipole_moment(mol)
            if debye is not None:
                phys["dipole_moment_debye"] = debye
                logger.info(f"[DIPOLE] {name}: Calculated {debye} D via {source}")

                if source == "Existing 3D":
                    self.stats["dipole_calc_existing_3d"] += 1
                else:
                    self.stats["dipole_calc_smiles_3d"] += 1
                return True
            else:
                self.stats["dipole_failed"] += 1
                logger.warning(f"[DIPOLE] {name}: Calculation failed despite valid mol object.")

        return False

    def process_state(self, root):
        """Infers physical state based on MP and BP relative to 298.15 K."""
        phys = root.setdefault("properties", {}).setdefault("physical", {})

        # Skip if valid state exists
        current = phys.get("state_25_k_1_atm")
        if current and current not in ["N/A", "Unknown", "None", "", None]:
            return False

        mp_obj = phys.get("melting_point")
        bp_obj = phys.get("boiling_point")

        mp = mp_obj.get("value_k") if mp_obj else None
        bp = bp_obj.get("value_k") if bp_obj else None
        name = root.get("identity", {}).get("name", "Unknown")

        inferred_state = None
        reason = ""

        # Logic
        if mp and mp > STP_K:
            inferred_state = "Solid"
            reason = f"MP {mp} K > 298 K"

        elif bp and bp < STP_K:
            inferred_state = "Gas"
            reason = f"BP {bp} K < 298 K"

        elif mp and bp:
            if mp < STP_K and bp > STP_K:
                inferred_state = "Liquid"
                reason = f"298 K between MP {mp} K and BP {bp} K"

        # Loose Logic (If only one point is known and it strongly suggests state)
        elif mp and not bp:
            if mp < (STP_K - 20): # Melts significantly below room temp
                # Weak inference, but likely liquid if organic.
                # skipping to be safe, or mark as liquid?
                # User asked to be "aggressive".
                inferred_state = "Liquid"
                reason = f"MP {mp} K << 298 K (Aggressive)"

        elif bp and not mp:
            if bp > (STP_K + 20): # Boils significantly above room temp
                # Could be liquid or solid. Cannot determine without MP.
                pass

        if inferred_state:
            phys["state_25_k_1_atm"] = inferred_state
            logger.info(f"[STATE]  {name}: Inferred {inferred_state} ({reason})")
            self.stats[f"state_inferred_{inferred_state.lower()}"] += 1
            return True

        return False

    def process_file(self, filename):
        filepath = os.path.join(INPUT_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")
            self.stats["errors"] += 1
            return

        # Handle wrapper structure
        root = data if "identity" in data else data.get("compound", {})

        updated = False

        # 1. Infer State
        if self.process_state(root):
            updated = True

        # 2. Calculate Dipole
        if self.process_dipole(root):
            updated = True

        # Save if changed
        # (We save everything to the new dir regardless to keep the dataset complete)
        out_path = os.path.join(OUTPUT_DIR, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]

        logger.info(f"Starting PROPERTY INFERENCE on {len(files)} files...")
        print(f"⚡ Processing {len(files)} files. Logs: {LOG_FILE}")

        for f in tqdm(files, desc="Inferring"):
            self.process_file(f)

        logger.info("Run Complete. Final Stats:")
        logger.info(json.dumps(self.stats, indent=2))

        print("\n------------------------------------------------")
        print("DONE. Summary:")
        print(f"  Processed:       {self.stats['processed']}")
        print(f"  States Inferred: Solid({self.stats['state_inferred_solid']}) Liquid({self.stats['state_inferred_liquid']}) Gas({self.stats['state_inferred_gas']})")
        print(f"  Dipoles Calc'd:  Existing 3D({self.stats['dipole_calc_existing_3d']}) From SMILES({self.stats['dipole_calc_smiles_3d']})")
        print(f"  Dipoles Failed:  {self.stats['dipole_failed']}")
        print("------------------------------------------------")

if __name__ == "__main__":
    PropertyInferrer().run()