import requests
import logging
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChEBIClient")

class ChEBIClient:
    """
    Client for ChEBI data via the EBI OLS (Ontology Lookup Service) API.
    """

    OLS_BASE_URL = "https://www.ebi.ac.uk/ols/api"

    def search_entity(self, name: str) -> Optional[str]:
        """
        Searches for a chemical name.
        Strategy:
        1. Exact Label Match.
        2. Exact Synonym Match.
        3. Fallback to top result.
        """
        url = f"{self.OLS_BASE_URL}/search"
        params = {
            "q": name,
            "ontology": "chebi",
            "exact": "false",
            "rows": 10  # Fetch more rows to increase chance of finding synonym match
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            docs = data.get("response", {}).get("docs", [])
            if not docs:
                return None

            name_lower = name.lower()

            # Priority 1: Exact Label Match
            for doc in docs:
                if doc.get("label", "").lower() == name_lower:
                    return doc.get("short_form")

            # Priority 2: Exact Synonym Match
            for doc in docs:
                synonyms = doc.get("synonym", [])
                if synonyms:
                    # OLS returns synonyms as a list of strings
                    for syn in synonyms:
                        if syn.lower() == name_lower:
                            logger.info(f"Matched synonym '{syn}' to {doc.get('short_form')}")
                            return doc.get("short_form")

            # Priority 3: Fallback (First Result)
            # We log a warning because this is often where mismatches happen
            best_guess = docs[0].get("short_form")
            logger.warning(f"No exact match for '{name}'. Falling back to top result: {best_guess} ({docs[0].get('label')})")
            return best_guess

        except Exception as e:
            logger.error(f"ChEBI OLS Search failed for '{name}': {e}")
            return None

    def get_complete_entity(self, chebi_id: str) -> Dict[str, Any]:
        """
        Fetches the complete ontology term data.
        """
        safe_id = chebi_id.replace(":", "_")
        ols_url = f"{self.OLS_BASE_URL}/ontologies/chebi/terms?iri=http://purl.obolibrary.org/obo/{safe_id}"

        logger.info(f"Fetching Ontology Data for {chebi_id}...")

        try:
            response = requests.get(ols_url)
            if response.status_code == 404:
                logger.warning(f"Term not found in OLS: {chebi_id}")
                return {}
            response.raise_for_status()

            data = response.json()
            if "_embedded" not in data or "terms" not in data["_embedded"]:
                return {}

            term_data = data["_embedded"]["terms"][0]

            return {
                "id": chebi_id,
                "label": term_data.get("label"),
                "description": term_data.get("description", []),
                "annotation": term_data.get("annotation", {}),
                "links": term_data.get("_links", {})
            }
        except Exception as e:
            logger.error(f"ChEBI Lookup failed: {e}")
            return {}

if __name__ == "__main__":
    client = ChEBIClient()
    # Test with "Penicillin G" (should match synonym of Benzylpenicillin CHEBI:18208)
    cid = client.search_entity("Penicillin G")
    print(f"Found ID: {cid}")
    if cid:
        data = client.get_complete_entity(cid)
        print(f"Label: {data.get('label')}")