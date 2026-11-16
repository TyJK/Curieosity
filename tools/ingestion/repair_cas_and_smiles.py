import json
import os
import re
import logging
import time
from typing import Dict, Any, Optional
from tqdm import tqdm

# Import your existing toolchain
from cas_client import CasClient
from pubchem_client import PubChemClient

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/01_cas_and_smiles_repair")
OUTPUT_DIR = os.path.normpath("./tools/data/01_cas_and_smiles_repair") # New safe destination
LOG_DIR = "./tools/logs"
CAS_REGEX = re.compile(r'^\d{2,7}-\d{2}-\d$')

# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True) # Create the new folder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/enrich_basis.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BasisEnricher")

class BasisEnricher:
    def __init__(self):
        self.cas_client = CasClient()
        self.pubchem_client = PubChemClient()
        self.stats = {
            "processed": 0,
            "cas_fixed_cas_api": 0,
            "cas_fixed_pubchem": 0,
            "smiles_fixed_cas_api": 0,
            "smiles_fixed_pubchem": 0,
            "failed": 0
        }

    def _is_valid_cas(self, val: Any) -> bool:
        if not val or not isinstance(val, str): return False
        return bool(CAS_REGEX.match(val.strip()))

    def _is_valid_smiles(self, val: Any) -> bool:
        if not val or not isinstance(val, str): return False
        return len(val.strip()) > 1

    def resolve_cas_from_pubchem(self, name: str) -> Optional[str]:
        try:
            cids = self.pubchem_client.fetch_cids(name)
            if not cids: return None

            import requests
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cids[0]}/synonyms/JSON"
            resp = requests.get(url, timeout=5)

            if resp.status_code == 200:
                synonyms = resp.json().get('InformationList', {}).get('Information', [])[0].get('Synonym', [])
                for syn in synonyms:
                    if self._is_valid_cas(syn): return syn
        except Exception:
            return None
        return None

    def process_file(self, filename: str):
        in_path = os.path.join(INPUT_DIR, filename)
        out_path = os.path.join(OUTPUT_DIR, filename) # Write to new folder

        try:
            with open(in_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception: return

        # Normalize structure access
        compound = data.get("compound", {})
        if not compound: compound = data

        ident = compound.setdefault("identity", {})
        maint = compound.setdefault("_maintenance", {})

        changed = False
        name = ident.get("name")
        current_cas = ident.get("cas_rn")
        current_smiles = ident.get("smiles")

        # --- 1. REPAIR CAS RN ---
        if not self._is_valid_cas(current_cas):
            if name:
                # Strategy A: CAS API
                hit = self.cas_client.search_substance(name)
                if hit and hit.get("rn"):
                    ident["cas_rn"] = hit["rn"]
                    maint["cas_source"] = "CAS_API"
                    self.stats["cas_fixed_cas_api"] += 1
                    changed = True
                    current_cas = hit["rn"]

                # Strategy B: PubChem
                if not changed:
                    found_cas = self.resolve_cas_from_pubchem(name)
                    if found_cas:
                        ident["cas_rn"] = found_cas
                        maint["cas_source"] = "PubChem_Synonyms"
                        self.stats["cas_fixed_pubchem"] += 1
                        changed = True
                        current_cas = found_cas

        # --- 2. REPAIR SMILES ---
        if not self._is_valid_smiles(current_smiles):
            # Strategy A: CAS API (needs valid CAS)
            if self._is_valid_cas(current_cas):
                details = self.cas_client.get_details(current_cas)
                found_smiles = details.get("canonicalSmile")
                if found_smiles:
                    ident["smiles"] = found_smiles
                    maint["smiles_source"] = "CAS_API"
                    self.stats["smiles_fixed_cas_api"] += 1
                    changed = True

            # Strategy B: PubChem (CAS or Name)
            if not changed and (current_cas or name):
                search_val = current_cas if current_cas else name
                props = self.pubchem_client.fetch_compound_properties([search_val], namespace="name")
                if props:
                    found_smiles = props[0].get("CanonicalSMILES")
                    if found_smiles:
                        ident["smiles"] = found_smiles
                        maint["smiles_source"] = "PubChem"
                        self.stats["smiles_fixed_pubchem"] += 1
                        changed = True

        if changed:
            maint["basis_enriched_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{filename}] ✅ Updated Basis: CAS={ident.get('cas_rn')} SMILES={bool(ident.get('smiles'))}")
            # Politeness delay only if we hit the API
            time.sleep(0.5)

        # WRITE TO NEW LOCATION (Always write, even if unchanged)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["processed"] += 1

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        logger.info(f"🚀 Starting Phase 0: Basis Enrichment on {len(files)} files...")
        logger.info(f"📂 Outputting to: {OUTPUT_DIR}")

        for f in tqdm(files, desc="Enriching Basis"):
            self.process_file(f)

        logger.info("DONE. Stats:")
        for k, v in self.stats.items():
            logger.info(f"  {k}: {v}")

if __name__ == "__main__":
    enricher = BasisEnricher()
    enricher.run()