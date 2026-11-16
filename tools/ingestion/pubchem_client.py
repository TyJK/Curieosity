import requests
import logging
from typing import List, Dict, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from urllib.parse import quote

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PubChemClient")

class PubChemClient:
    REST_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    VIEW_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound"

    DEFAULT_PROPERTIES = [
        "MolecularFormula", "MolecularWeight", "CanonicalSMILES", "IsomericSMILES",
        "InChI", "InChIKey", "IUPACName", "Title",
        "XLogP", "ExactMass", "Charge", "TPSA", "MonoisotopicMass", "Complexity",
        "HBondDonorCount", "HBondAcceptorCount", "RotatableBondCount"
    ]

    def __init__(self):
        self.session = requests.Session()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
    def fetch_cids(self, identifier: str, namespace: str = "name") -> List[str]:
        safe_id = quote(identifier, safe='')
        url = f"{self.REST_URL}/compound/{namespace}/{safe_id}/cids/JSON"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code in [400, 404]: return []
            response.raise_for_status()
            return response.json().get("IdentifierList", {}).get("CID", [])
        except Exception: return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
    def fetch_compound_properties(self, identifiers: List[str], namespace: str = "name") -> List[Dict[str, Any]]:
        props_str = ",".join(self.DEFAULT_PROPERTIES)
        url = f"{self.REST_URL}/compound/{namespace}/property/{props_str}/JSON"
        payload = {namespace: identifiers}
        try:
            response = self.session.post(url, data=payload)
            if response.status_code == 404: return []
            response.raise_for_status()
            return response.json().get("PropertyTable", {}).get("Properties", [])
        except Exception: return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
    def find_best_related_cid(self, cid: str) -> Optional[str]:
        """
        Finds a better CID (Parent or Major Component) if the current one is sparse.
        Prioritizes: Parent -> Heavy Component (exclude Water/Self).
        """
        ignore_list = {
            str(cid),
            "962",   # Water
            "1038",  # Ammonium (sometimes just an ion record)
            "5462222" # Magnesium (Element record often sparse)
        }

        # 1. Try Parent (Best for Hydrates -> Anhydrous)
        # 2. Try Component (Best for Mixtures -> Main Ingredient)
        for link_type in ["parent", "component"]:
            url = f"{self.REST_URL}/compound/cid/{cid}/cids/JSON?type={link_type}"
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    cids = response.json().get("IdentifierList", {}).get("CID", [])
                    # Filter candidates
                    candidates = [str(c) for c in cids if str(c) not in ignore_list]

                    if candidates:
                        # Return the first valid candidate.
                        # (PubChem usually lists the 'main' component first or heaviest)
                        return candidates[0]
            except Exception: pass
        return None

    def _extract_string_value(self, section: Dict) -> Optional[str]:
        candidates = []
        try:
            info_list = section.get("Information", [])
            for info in info_list:
                val_obj = info.get("Value", {})
                text = None
                if "StringWithMarkup" in val_obj:
                    markup = val_obj["StringWithMarkup"]
                    if markup: text = markup[0].get("String")
                elif "Number" in val_obj:
                    text = str(val_obj["Number"][0])
                elif "String" in val_obj:
                    text = val_obj["String"]

                if text: candidates.append(text)

            # Prioritize values containing digits (data) over text (comments)
            for c in candidates:
                if any(char.isdigit() for char in c): return c
            if candidates: return candidates[0]
        except Exception: pass
        return None

    def _deep_search_property(self, sections: List[Dict], results: Dict[str, str]):
        prop_map = {
            "Melting Point": "melting_point",
            "Boiling Point": "boiling_point",
            "Density": "density",
            "Vapor Pressure": "vapor_pressure",
            "Viscosity": "viscosity",
            "Surface Tension": "surface_tension",
            "Refractive Index": "refractive_index",
            "Color/Form": "appearance",
            "Physical Description": "appearance",
            "Solubility": "solubility",
            "Autoignition Temperature": "autoignition_temperature",
            "Flash Point": "flash_point",
            "Decomposition": "decomposition",
            "Odor": "odor",
            "Dissociation Constants": "pka"
        }
        for section in sections:
            heading = section.get("TOCHeading", "")
            if heading in prop_map:
                target_key = prop_map[heading]
                if target_key not in results:
                    val = self._extract_string_value(section)
                    if val: results[target_key] = val
            if "Section" in section:
                self._deep_search_property(section["Section"], results)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
    def fetch_3d_sdf(self, cid: str) -> Optional[str]:
        url = f"{self.REST_URL}/compound/cid/{cid}/SDF?record_type=3d"
        try:
            response = self.session.get(url)
            if response.status_code == 200: return response.text
        except Exception: pass
        return None

    def _parse_context_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        context = {
            "ghs_codes": [],
            "hazard_statements": [],
            "industrial_uses": [],
            "experimental_properties": {}
        }
        root_sections = data.get("Record", {}).get("Section", [])

        self._deep_search_property(root_sections, context["experimental_properties"])

        # Quick GHS
        def find_ghs(sections):
            for s in sections:
                if s.get("TOCHeading") == "GHS Classification": return s
                if "Section" in s:
                    found = find_ghs(s["Section"])
                    if found: return found
            return None
        ghs = find_ghs(root_sections)
        if ghs:
            for info in ghs.get("Information", []):
                for item in info.get("Value", {}).get("StringWithMarkup", []):
                    txt = item.get("String", "")
                    if txt.startswith("H") and len(txt) >= 4 and txt[1].isdigit():
                        if txt not in context["hazard_statements"]: context["hazard_statements"].append(txt)

        # Quick Uses
        def find_uses(sections):
            for s in sections:
                if s.get("TOCHeading") == "Uses": return s
                if "Section" in s:
                    found = find_uses(s["Section"])
                    if found: return found
            return None
        uses = find_uses(root_sections)
        if uses:
            for info in uses.get("Information", [])[:15]:
                for item in info.get("Value", {}).get("StringWithMarkup", []):
                    use = item.get("String")
                    if use: context["industrial_uses"].append(use)
        return context

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
    def fetch_compound_context(self, cid: str) -> Dict[str, Any]:
        url = f"{self.VIEW_URL}/{cid}/JSON"
        try:
            response = self.session.get(url)
            if response.status_code == 404: return {}
            response.raise_for_status()
            data = response.json()
            context = self._parse_context_json(data)

            # --- PARENT/COMPONENT FALLBACK ---
            props = context["experimental_properties"]
            missing_critical = not (props.get("melting_point") or props.get("density"))

            if missing_critical:
                related_cid = self.find_best_related_cid(cid)
                if related_cid:
                    logger.info(f"Data sparse for {cid}. Fetching Related CID {related_cid}...")
                    try:
                        p_resp = self.session.get(f"{self.VIEW_URL}/{related_cid}/JSON")
                        if p_resp.status_code == 200:
                            p_context = self._parse_context_json(p_resp.json())

                            # Merge Data
                            for k, v in p_context["experimental_properties"].items():
                                if k not in props: props[k] = v
                            context["industrial_uses"].extend(p_context["industrial_uses"])
                            context["hazard_statements"].extend(p_context["hazard_statements"])
                    except Exception: pass

            return context
        except Exception as e:
            return {}