import pandas as pd
import logging
import re
import requests
import time
import os
import sys

# Ensure we can import the clients
sys.path.append(os.path.dirname(__file__))
from pubchem_client import PubChemClient
from cas_client import CasClient

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("Augmenter")

class CandidateAugmenter:
    def __init__(self, input_file: str, output_file: str):
        self.input_file = input_file
        self.output_file = output_file
        self.pubchem = PubChemClient()
        self.cas = CasClient()
        self.cas_pattern = re.compile(r'^\d{2,7}-\d{2}-\d$')

    def get_cas_from_pubchem(self, name: str) -> str:
        """
        Flow: Name -> CID -> Synonyms -> Filter for CAS
        """
        try:
            # 1. Name to CID
            cids = self.pubchem.fetch_cids(name)
            if not cids: return None

            cid = cids[0] # Take best match

            # 2. CID to Synonyms (Direct PUG REST call for speed)
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
            resp = requests.get(url, timeout=10)

            if resp.status_code == 200:
                data = resp.json()
                synonyms = data.get('InformationList', {}).get('Information', [])[0].get('Synonym', [])

                # 3. Filter for CAS pattern
                for syn in synonyms:
                    if self.cas_pattern.match(syn):
                        return syn
            return None
        except Exception:
            return None

    def get_cas_from_cas_api(self, name: str) -> str:
        """
        Flow: Name -> CAS Search -> Hit -> RN
        """
        hit = self.cas.search_substance(name)
        if hit:
            return hit.get('rn')
        return None

    def run(self):
        # 1. Load Data
        if not os.path.exists(self.input_file):
            logger.error(f"❌ Input file not found: {self.input_file}")
            return

        df = pd.read_csv(self.input_file)
        logger.info(f"📂 Loaded {len(df)} candidates.")

        # 2. Identify Targets (Missing CAS)
        # Handle various forms of 'empty': NaN, None, "nan", ""
        if 'CAS' not in df.columns:
            df['CAS'] = None

        mask = df['CAS'].isna() | (df['CAS'].astype(str).str.strip() == '') | (df['CAS'].astype(str).str.lower() == 'nan')
        missing_count = mask.sum()

        logger.info(f"🔍 Found {missing_count} compounds missing CAS RNs. Starting augmentation...")

        # 3. Iterate and Solve
        updates = 0

        # We iterate over the *indices* of the missing rows to update 'df' in place
        for idx in df[mask].index:
            name = str(df.at[idx, 'NAME']).strip()

            # Strategy A: PubChem (Broad, Free)
            cas = self.get_cas_from_pubchem(name)
            source = "PubChem"

            # Strategy B: CAS API (Authoritative)
            if not cas:
                cas = self.get_cas_from_cas_api(name)
                source = "CAS_API"

            if cas:
                logger.info(f"✅ [{source}] Resolved '{name}' -> {cas}")
                df.at[idx, 'CAS'] = cas
                updates += 1
            else:
                logger.warning(f"❌ Failed to resolve '{name}'")

            # Rate limit respect
            time.sleep(0.5)

        # 4. Cleanup and Save
        # Remove any that STILL don't have a CAS (Dead candidates)
        final_df = df.dropna(subset=['CAS'])
        final_df = final_df[final_df['CAS'].astype(str).str.match(r'^\d{2,7}-\d{2}-\d$')]

        dropped = len(df) - len(final_df)

        final_df.to_csv(self.output_file, index=False)
        logger.info("-" * 30)
        logger.info(f"🎉 Augmentation Complete!")
        logger.info(f"   - Originally Missing: {missing_count}")
        logger.info(f"   - Successfully Resolved: {updates}")
        logger.info(f"   - Dropped (Unresolvable): {dropped}")
        logger.info(f"   - Final Count: {len(final_df)}")
        logger.info(f"💾 Saved to: {self.output_file}")

if __name__ == "__main__":
    # Point this to your merged list
    augmenter = CandidateAugmenter("./tools/data/apothecary_candidates.csv", "./tools/data/augmented_apothecary.csv")
    augmenter.run()