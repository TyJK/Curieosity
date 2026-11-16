import json
import os
import shutil
import logging
from collections import defaultdict
from typing import Dict, List, Any
from tqdm import tqdm

# Try to import RDKit for robust InChIKey generation
try:
    from rdkit import Chem
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/05_media_densification")
OUTPUT_DIR = os.path.normpath("./tools/data/06_deduplicated")
LOG_DIR = "./tools/logs"

# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/deduplication.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Deduplicator")

class LibraryDeduplicator:
    def __init__(self):
        self.registry = defaultdict(list)
        self.stats = {
            "total_files": 0,
            "unique_compounds": 0,
            "duplicates_merged": 0,
            "collisions_cas": 0,
            "collisions_inchikey": 0
        }

    def get_fingerprint(self, smiles: str) -> str:
        """
        Generates a unique structural fingerprint.
        Prefers InChIKey via RDKit. Fallback to stripped SMILES string.
        """
        if not smiles: return "MISSING_STRUCTURE"

        if RDKIT_AVAILABLE:
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol:
                    # InChIKey is the gold standard for uniqueness
                    return Chem.MolToInchiKey(mol)
            except: pass

        # Fallback: Simple string normalization
        return smiles.strip()

    def scan_library(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        self.stats["total_files"] = len(files)
        logger.info(f"🔎 Scanning {len(files)} files for duplicates...")

        for filename in tqdm(files, desc="Indexing"):
            filepath = os.path.join(INPUT_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                compound = data.get("compound", {}) or data
                ident = compound.get("identity", {})

                cas = ident.get("cas_rn")
                smiles = ident.get("smiles")

                # We group by a tuple of identifiers to catch overlaps
                # Primary Key: InChIKey (Structure)
                # Secondary Key: CAS (Identity)

                fingerprint = self.get_fingerprint(smiles)

                # We prioritize CAS grouping first, then Structure
                # Actually, let's map file_data to a list, then we process the list

                record = {
                    "filename": filename,
                    "data": data,
                    "cas": cas,
                    "fingerprint": fingerprint,
                    "desc_len": len(ident.get("description", "") or "")
                }

                # The Registry Key strategy:
                # If we have a CAS, use it. If not, use Fingerprint.
                # Note: This might miss cases where CAS differs but Structure is same.
                # We will do a two-pass check.

                key = cas if cas else f"STRUCT_{fingerprint}"
                self.registry[key].append(record)

            except Exception as e:
                logger.error(f"Error reading {filename}: {e}")

    def merge_records(self, records: List[Dict]) -> Dict:
        """
        Merges a list of duplicate records into one Master Record.
        """
        # 1. Determine Master File (Prefer 'CAS.json' filename format)
        # Rank by: 1. Is CAS filename? 2. Longest Description?
        def sort_key(rec):
            is_cas_name = 1 if rec["cas"] and rec["filename"].startswith(rec["cas"]) else 0
            return (is_cas_name, rec["desc_len"])

        sorted_records = sorted(records, key=sort_key, reverse=True)
        master = sorted_records[0]
        duplicates = sorted_records[1:]

        master_data = master["data"]
        m_compound = master_data.get("compound", {}) or master_data
        m_ident = m_compound.setdefault("identity", {})
        m_maint = m_compound.setdefault("_maintenance", {})

        merges_log = []

        for dup in duplicates:
            d_data = dup["data"]
            d_compound = d_data.get("compound", {}) or d_data
            d_ident = d_compound.get("identity", {})

            # A. Merge Synonyms
            curr_syns = set(s.lower() for s in m_ident.get("synonyms", []))
            new_syns = d_ident.get("synonyms", [])
            for s in new_syns:
                if s.lower() not in curr_syns:
                    m_ident["synonyms"].append(s)
                    curr_syns.add(s.lower())

            # B. Merge Description (If duplicate has one and master is short/empty? No, we sorted by length)
            # But if master desc is missing, take duplicate
            if not m_ident.get("description") and d_ident.get("description"):
                m_ident["description"] = d_ident.get("description")

            # C. Merge Tags/Roles
            # (Assuming simple list merge logic here if needed)

            merges_log.append(dup["filename"])

        if merges_log:
            m_maint["deduplicated_from"] = merges_log
            # logger.info(f"Collapsed {len(merges_log)} files into {master['filename']}")
            self.stats["duplicates_merged"] += len(merges_log)

        return master_data

    def execute_deduplication(self):
        # First Pass: Resolve by Registry Key (mostly CAS)
        logger.info("✨ Resolving conflicts...")

        # We need to be careful: different CAS numbers might have the same Structure (InChIKey).
        # So we should invert the registry to check for Structural Collisions across CAS keys.

        structure_map = defaultdict(list)

        # Flatten the first registry
        all_groups = []
        for key, group in self.registry.items():
            all_groups.append(group)

        # Now regroup by Structure (InChIKey) to find cross-CAS duplicates
        for group in all_groups:
            # Merge the CAS group first
            if len(group) > 1:
                self.stats["collisions_cas"] += (len(group) - 1)
                merged = self.merge_records(group)
                # Update the first record to hold the merged data, discard rest
                group = [ {**group[0], "data": merged} ]

            # Add the resulting unique CAS-record to the Structure Map
            rec = group[0]
            if rec["fingerprint"] != "MISSING_STRUCTURE":
                structure_map[rec["fingerprint"]].append(rec)
            else:
                # If no structure, just save it (orphans)
                self._save(rec)

        # Second Pass: Resolve by Structure
        for inchikey, group in structure_map.items():
            if len(group) > 1:
                self.stats["collisions_inchikey"] += (len(group) - 1)
                logger.info(f"Structural Collision ({inchikey}): {[r['filename'] for r in group]}")

                # These files have different CAS (maybe) but same Structure.
                # We merge them.
                final_data = self.merge_records(group)
                self._save({**group[0], "data": final_data})
            else:
                self._save(group[0])

    def _save(self, record):
        filename = record["filename"]
        out_path = os.path.join(OUTPUT_DIR, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(record["data"], f, indent=2)
        self.stats["unique_compounds"] += 1

    def run(self):
        logger.info("🚀 Starting Library Deduplication...")
        self.scan_library()
        self.execute_deduplication()

        logger.info("DONE. Stats:")
        for k, v in self.stats.items():
            logger.info(f"  {k}: {v}")
        logger.info(f"Final library size: {self.stats['unique_compounds']}")

if __name__ == "__main__":
    deduper = LibraryDeduplicator()
    deduper.run()