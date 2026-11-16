import json
import os
import logging
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import rdBase
from rdkit.Chem.Draw import rdMolDraw2D
from tqdm import tqdm

# --- SILENCE RDKIT ---
rdBase.LogToPythonLogger()
rd_logger = logging.getLogger("rdkit")
rd_logger.setLevel(logging.CRITICAL)

# --- CONFIGURATION ---
TARGET_DIR = os.path.normpath("./tools/data/05_media_densification")
OUTPUT_DIR = os.path.normpath("./tools/data/06_media_densification")
LOG_DIR = "./tools/logs"

# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/media_gap_closer.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GapCloser")

class GapCloser:
    def __init__(self):
        self.stats = {
            "processed": 0,
            "2d_filled": 0,
            "3d_forced_metal": 0,
            "3d_filled_standard": 0,
            "still_missing_no_smiles": 0,
            "still_missing_error": 0
        }

    def is_valid_smiles(self, text):
        if not text or len(text) < 2: return False
        if " " in text or ("-" in text and "[" not in text) or text.isalpha(): return False
        return True

    def get_largest_fragment(self, mol):
        try:
            frags = Chem.GetMolFrags(mol, asMols=True, sanitizeFrags=True)
            if len(frags) == 1: return mol
            return max(frags, key=lambda m: m.GetNumHeavyAtoms())
        except: return mol

    def generate_2d_svg(self, mol) -> str:
        try:
            drawer = rdMolDraw2D.MolDraw2DSVG(400, 400)
            opts = drawer.drawOptions()
            opts.clearBackground = False
            mol = Chem.Draw.PrepareMolForDrawing(mol)
            drawer.DrawMolecule(mol)
            drawer.FinishDrawing()
            return drawer.GetDrawingText()
        except: return None

    def generate_rough_3d(self, mol) -> str:
        """
        Generates 3D coordinates WITHOUT Force Field optimization.
        Useful for metals/salts where MMFF crashes.
        """
        try:
            mol = self.get_largest_fragment(mol)
            mol = Chem.AddHs(mol)

            # Embed using Random Coordinates (most robust for weird structures)
            # We skip MMFFOptimizeMolecule entirely here.
            res = AllChem.EmbedMolecule(mol, useRandomCoords=True)

            if res == -1:
                # Last resort: ETKDG with very loose constraints
                params = AllChem.ETKDGv3()
                params.useRandomCoords = True
                params.maxIterations = 500
                res = AllChem.EmbedMolecule(mol, params)

            if res != -1:
                return Chem.MolToMolBlock(mol)
        except: pass
        return None

    def process_file(self, filename: str):
        filepath = os.path.join(TARGET_DIR, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: return

        t_media = data.setdefault("compound", {}).setdefault("media", {}) # Ensure path exists
        # Fix for flattened structure if needed (handle both schema variations)
        if "identity" in data:
            # It's the canonical format
            t_media = data.setdefault("media", {})
            t_ident = data.setdefault("identity", {})
        else:
            # It's the nested format
            t_compound = data.setdefault("compound", {})
            t_media = t_compound.setdefault("media", {})
            t_ident = t_compound.setdefault("identity", {})

        smiles = t_ident.get("smiles")
        mol = None

        # Only parse molecule if we actually have gaps to fill
        missing_2d = not (t_media.get("image_2d") and len(t_media["image_2d"]) > 50)
        missing_3d = not (t_media.get("model_3d") and len(t_media["model_3d"]) > 50)

        if not missing_2d and not missing_3d:
            return # Skip file entirely if full

        # Load Molecule
        if self.is_valid_smiles(smiles):
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol: Chem.SanitizeMol(mol)
            except: mol = None

        if not mol:
            self.stats["still_missing_no_smiles"] += 1
            return

        # --- FILL 2D GAP ---
        if missing_2d:
            svg = self.generate_2d_svg(mol)
            if svg:
                t_media["image_2d"] = svg
                self.stats["2d_filled"] += 1

        # --- FILL 3D GAP (FORCE MODE) ---
        if missing_3d:
            # Try standard generation first
            sdf = self.generate_rough_3d(mol)
            # Note: We use "rough" generator for everything here as a fallback
            # because these are the files that failed the "nice" generator.

            if sdf:
                t_media["model_3d"] = sdf
                self.stats["3d_filled_standard"] += 1
            else:
                self.stats["still_missing_error"] += 1

        # Save
        with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        files = [f for f in os.listdir(TARGET_DIR) if f.endswith(".json")]
        logger.info(f"🚀 Starting GAP CLOSER on {len(files)} files...")

        for f in tqdm(files, desc="Closing Gaps"):
            self.process_file(f)

        logger.info("DONE. Stats:")
        for k, v in self.stats.items():
            logger.info(f"  {k:<25}: {v}")

if __name__ == "__main__":
    GapCloser().run()