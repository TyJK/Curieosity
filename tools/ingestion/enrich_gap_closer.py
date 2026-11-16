import json
import os
import re
import logging
import time
from typing import Dict, Any, Optional
from tqdm import tqdm

# Clients
from pubchem_client import PubChemClient
from chebi_client import ChEBIClient

# RDKit for Formula Calculation
try:
    from rdkit import Chem
    from rdkit.Chem.rdMolDescriptors import CalcMolFormula
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/02_identity_enrichment")
OUTPUT_DIR = os.path.normpath("./tools/data/03_gap_closer")
LOG_DIR = "./tools/logs"

# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/enrich_gap_closer.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GapCloser")

class GapCloser:
    def __init__(self):
        self.pubchem = PubChemClient()
        self.chebi = ChEBIClient()
        self.stats = {
            "processed": 0,
            "smiles_recovered_chebi": 0,
            "smiles_recovered_pubchem_syn": 0,
            "formula_calculated": 0,
            "still_missing_smiles": 0
        }

        if not RDKIT_AVAILABLE:
            logger.warning("⚠️ RDKit not found. Formula calculation will be disabled.")

    def _is_valid_smiles(self, val: Any) -> bool:
        return isinstance(val, str) and len(val.strip()) > 1

    def calculate_formula(self, smiles: str) -> Optional[str]:
        if not RDKIT_AVAILABLE: return None
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                return CalcMolFormula(mol)
        except:
            return None
        return None

    def find_smiles_via_chebi(self, name: str) -> Optional[str]:
        """Tries to find SMILES via ChEBI OLS lookup."""
        try:
            chebi_id = self.chebi.search_entity(name)
            if chebi_id:
                entity = self.chebi.get_complete_entity(chebi_id)
                # OLS stores SMILES in annotations usually
                annotations = entity.get("annotation", {})
                if "smiles" in annotations:
                    # It returns a list, usually ['C=C...']
                    return annotations["smiles"][0]
        except:
            pass
        return None

    def find_smiles_via_synonyms(self, synonyms: list) -> Optional[str]:
        """Iterates through synonyms to find a PubChem hit."""
        for syn in synonyms[:3]: # Try top 3 synonyms
            if not syn or len(syn) < 3: continue
            try:
                props = self.pubchem.fetch_compound_properties([syn], namespace="name")
                if props:
                    return props[0].get("CanonicalSMILES")
            except:
                pass
            time.sleep(0.2) # Be polite inside the loop
        return None

    def process_file(self, filename: str):
        in_path = os.path.join(INPUT_DIR, filename)
        out_path = os.path.join(OUTPUT_DIR, filename)

        try:
            with open(in_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: return

        compound = data.get("compound", {}) or data
        ident = compound.setdefault("identity", {})
        maint = compound.setdefault("_maintenance", {})

        changed = False
        updates_made = []

        # --- 1. RECOVER SMILES ---
        if not self._is_valid_smiles(ident.get("smiles")):
            name = ident.get("name")

            # Strategy A: ChEBI (Good for bios)
            if name:
                new_smiles = self.find_smiles_via_chebi(name)
                if new_smiles:
                    ident["smiles"] = new_smiles
                    maint["smiles_source"] = "ChEBI_OLS"
                    self.stats["smiles_recovered_chebi"] += 1
                    changed = True
                    updates_made.append("SMILES(ChEBI)")

            # Strategy B: PubChem Synonyms (Deep Search)
            if not self._is_valid_smiles(ident.get("smiles")):
                synonyms = ident.get("synonyms", [])
                if synonyms:
                    new_smiles = self.find_smiles_via_synonyms(synonyms)
                    if new_smiles:
                        ident["smiles"] = new_smiles
                        maint["smiles_source"] = "PubChem_Synonym"
                        self.stats["smiles_recovered_pubchem_syn"] += 1
                        changed = True
                        updates_made.append("SMILES(Synonym)")

            if not self._is_valid_smiles(ident.get("smiles")):
                self.stats["still_missing_smiles"] += 1

        # --- 2. CALCULATE FORMULA ---
        # Run this if we have a SMILES but no Formula
        # OR if we just found a SMILES
        current_smiles = ident.get("smiles")
        current_formula = ident.get("formula")

        if self._is_valid_smiles(current_smiles):
            # If formula is missing OR looks weird (short/empty), calculate it
            if not current_formula or len(current_formula) < 2:
                calc_form = self.calculate_formula(current_smiles)
                if calc_form:
                    ident["formula"] = calc_form
                    # Don't tag source for formula, it's derived
                    self.stats["formula_calculated"] += 1
                    changed = True
                    updates_made.append(f"Formula(RDKit)='{calc_form}'")

        if changed:
            maint["gap_closure_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{filename}] 🔧 Gap Closed: {', '.join(updates_made)}")

        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        logger.info(f"🚀 Starting Phase 0.9: Gap Closer on {len(files)} files...")

        # We process ALL files because we need to calculate formula for everyone
        # But the logic inside skips quickly if data exists
        for f in tqdm(files, desc="Closing Gaps"):
            self.process_file(f)

        logger.info("DONE. Stats:")
        for k, v in self.stats.items():
            logger.info(f"  {k}: {v}")

if __name__ == "__main__":
    closer = GapCloser()
    closer.run()