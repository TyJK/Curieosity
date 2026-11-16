import requests
import logging
import os
from typing import Dict, Optional, Any

try:
    from rdkit import Chem
except ImportError:
    Chem = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CASClient")

class CasClient:
    """
    Client for CAS Common Chemistry API.
    Docs: https://commonchemistry.cas.org/api-overview
    """

    BASE_URL = "https://commonchemistry.cas.org/api"

    def __init__(self):
        # Prefer Environment Variable, fallback to hardcoded for local testing if needed
        self.api_key = os.getenv("CAS_API_KEY", "BGYiyWwxKaanrC3tcxQYQ4cnuQzEtLlR9F4zZFQp")

        self.headers = {
            "User-Agent": "CurieosityGame/0.1 (Educational; Open Source)",
            "Accept": "application/json",
            "X-API-Key": self.api_key
        }

    def generate_inchikey(self, smiles: str) -> Optional[str]:
        if not Chem:
            logger.error("RDKit not installed. Cannot convert SMILES to InChIKey.")
            return None
        mol = Chem.MolFromSmiles(smiles)
        if not mol: return None
        return Chem.MolToInchiKey(mol)

    def search_substance(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Searches by Name, CAS RN, or InChIKey.
        """
        url = f"{self.BASE_URL}/search"
        params = {"q": query}

        try:
            logger.info(f"Querying CAS for: {query}")
            response = requests.get(url, params=params, headers=self.headers, timeout=10)

            # DEBUG: Print the raw response if it fails or returns weird data
            if response.status_code != 200:
                logger.error(f"CAS Error {response.status_code}: {response.text}")
                return None

            data = response.json()

            if data.get("count", 0) > 0:
                # Success!
                hit = data["results"][0]
                logger.info(f"CAS Match: {hit.get('name')} ({hit.get('rn')})")
                return hit

            logger.warning(f"CAS returned 0 results for '{query}'")
            return None

        except Exception as e:
            logger.error(f"CAS Connection failed: {e}")
            return None

    def resolve_smiles(self, smiles: str) -> Optional[Dict[str, Any]]:
        """
        Strategy: SMILES -> InChIKey -> CAS Search
        """
        inchikey = self.generate_inchikey(smiles)
        if not inchikey:
            logger.warning(f"Invalid SMILES for InChIKey generation: {smiles}")
            return None
        return self.search_substance(inchikey)

    def get_details(self, cas_rn: str) -> Dict[str, Any]:
        """
        Fetches full details for a specific CAS RN.
        """
        url = f"{self.BASE_URL}/detail"
        params = {"cas_rn": cas_rn}
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"CAS Detail fetch failed for {cas_rn}: {e}")
            return {}

if __name__ == "__main__":
    # Quick Test
    client = CasClient()

    # 1. Test with the InChIKey for Sulfuric Acid explicitly
    # InChIKey=QAOWNCQODCNURD-UHFFFAOYSA-N
    print("\n--- Test 1: Search by InChIKey ---")
    client.search_substance("QAOWNCQODCNURD-UHFFFAOYSA-N")

    # 2. Test with CAS RN (from ChEBI)
    print("\n--- Test 2: Search by CAS RN ---")
    client.search_substance("7664-93-9")

    # 3. Test with SMILES (Fixing your typo from "OS" to real SMILES)
    print("\n--- Test 3: Search by SMILES ---")
    client.resolve_smiles("OS(=O)(=O)O")