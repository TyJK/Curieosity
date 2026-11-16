import requests
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SureChEMBL")

class SureChemblClient:
    """
    Client for EBI SureChEMBL / UniChem.
    Maps InChIKey to Patent IDs.
    """

    # Using UniChem is often the most stable way to bridge Compound -> Patent
    UNICHEM_URL = "https://www.ebi.ac.uk/unichem/rest"

    def get_patent_ids(self, inchikey: str) -> List[str]:
        """
        Queries UniChem to find SureChEMBL ID, then could map to patents.
        Actually, SureChEMBL has a direct map via UniChem Source ID '28'.
        """
        # Step 1: Get SureChEMBL ID from InChIKey via UniChem
        url = f"{self.UNICHEM_URL}/inchikey/{inchikey}"

        patents = []
        try:
            resp = requests.get(url)
            if resp.status_code != 200: return []

            data = resp.json()
            # Source 28 is SureChEMBL
            for src in data:
                if src.get("src_id") == "28":
                    # This gives us the ID in the SureChEMBL database
                    schembl_id = src.get("src_compound_id")
                    logger.info(f"Found SureChEMBL ID: {schembl_id}")
                    patents.append(schembl_id)

            # In a real Deep Dive, you would now take 'schembl_id'
            # and query www.surechembl.org for the specific patent numbers.
            # But simply having the ID allows us to generate a valid link:
            # https://www.surechembl.org/chemical/{schembl_id}
            return patents

        except Exception as e:
            logger.error(f"UniChem/SureChEMBL lookup failed: {e}")
            return []

if __name__ == "__main__":
    client = SureChemblClient()
    # Sulfuric Acid InChIKey
    ids = client.get_patent_ids("QAOWNCQODCNURD-UHFFFAOYSA-N")
    print(f"SureChEMBL IDs: {ids}")
    if ids:
        print(f"Link: https://www.surechembl.org/chemical/{ids[0]}")