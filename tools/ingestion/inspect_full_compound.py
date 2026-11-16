import json
import os
import logging
import re
from typing import Dict, Any, Optional

# Import Clients
from pubchem_client import PubChemClient
from chebi_client import ChEBIClient
from cas_client import CasClient
from wikidata_client import WikidataClient
from surechembl_client import SureChemblClient

try:
    from uspto_odp_client import UsptoOdpClient
except ImportError:
    UsptoOdpClient = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CompoundInspector")

class CompoundInspector:
    def __init__(self):
        self.pubchem = PubChemClient()
        self.chebi = ChEBIClient()
        self.cas = CasClient()
        self.wiki = WikidataClient()
        self.surechembl = SureChemblClient()

        uspto_key = os.getenv("USPTO_API_KEY")
        self.uspto_context = UsptoOdpClient(uspto_key) if uspto_key and UsptoOdpClient else None

    def _merge_context(self, master_ctx: Dict, fallback_ctx: Dict):
        curr_exp = master_ctx.get("experimental_properties", {})
        fallback_exp = fallback_ctx.get("experimental_properties", {})
        for k, v in fallback_exp.items():
            if k not in curr_exp: curr_exp[k] = v
        master_ctx.setdefault("industrial_uses", []).extend(fallback_ctx.get("industrial_uses", []))
        master_ctx.setdefault("hazard_statements", []).extend(fallback_ctx.get("hazard_statements", []))

    def inspect(self, input_term: str, known_cas_rn: str = None) -> Dict[str, Any]:
        if not input_term:
            input_term = "Unknown"

        logger.info(f"=== Inspecting Compound: '{input_term}' (CAS: {known_cas_rn}) ===")

        master_record = {
            "meta": {"input": input_term},
            "identity": { "pubchem": {}, "pubchem_context": {}, "pubchem_3d_conformer": None, "chebi": {}, "cas": {}, "wikidata": {} },
            "context": { "history": {}, "legal": {}, "patents": [] }
        }

        target_name = input_term

        # 1. CAS Lookup
        if known_cas_rn:
            try:
                cas_hit = self.cas.search_substance(known_cas_rn)
                if cas_hit:
                    master_record["identity"]["cas"] = cas_hit
                    if cas_hit.get("name"):
                        target_name = cas_hit["name"]
                        logger.info(f"Adopted CAS Name: '{target_name}'")
            except Exception as e:
                logger.warning(f"CAS Lookup failed: {e}")

        # 2. PubChem Resolution
        cid = None
        is_smiles = any(c in input_term for c in "=#/[]") and len(input_term) > 3

        try:
            if is_smiles:
                props = self.pubchem.fetch_compound_properties([input_term], namespace="smiles")
                if props:
                    master_record["identity"]["pubchem"] = props[0]
                    cid = str(props[0].get("CID"))
                    if not known_cas_rn: # Only override if we don't have CAS confidence
                        target_name = props[0].get("Title") or props[0].get("IUPACName")
            else:
                # Name search
                props = self.pubchem.fetch_compound_properties([target_name], namespace="name")
                if props:
                    master_record["identity"]["pubchem"] = props[0]
                    cid = str(props[0].get("CID"))
                elif target_name != input_term:
                    # Retry with original input if CAS name failed
                    props = self.pubchem.fetch_compound_properties([input_term], namespace="name")
                    if props:
                        master_record["identity"]["pubchem"] = props[0]
                        cid = str(props[0].get("CID"))
        except Exception as e:
            logger.warning(f"PubChem Search Error: {e}")

        # 3. PubChem Details
        if cid:
            try:
                master_record["identity"]["pubchem_context"] = self.pubchem.fetch_compound_context(cid)
                sdf = self.pubchem.fetch_3d_sdf(cid)
                if sdf: master_record["identity"]["pubchem_3d_conformer"] = sdf
            except Exception as e:
                logger.warning(f"PubChem Context Fetch Error: {e}")

        # 4. Wikidata Fallback (Crucial for Recovery)
        # If PubChem failed OR just for enrichment
        try:
            # Search by CAS first
            wiki_hist = {}
            if known_cas_rn:
                wiki_hist = self.wiki.get_history(None, cas_rn=known_cas_rn)

            # If no result, search by name
            if not wiki_hist and target_name:
                wiki_hist = self.wiki.get_history(target_name)

            if wiki_hist:
                master_record["context"]["history"] = wiki_hist
                # If we have no PubChem identity, treat Wiki as source of truth for name/properties
                if not cid:
                    logger.info("PubChem failed. Using Wikidata as primary identity.")
                    master_record["identity"]["wikidata"] = wiki_hist
                    # We will synthesize name from wiki history in the schema synthesizer
        except Exception as e:
            logger.warning(f"Wikidata Lookup Error: {e}")

        # 5. ChEBI
        if target_name and target_name != "Unknown" and not is_smiles:
            try:
                chebi_id = self.chebi.search_entity(target_name)
                if chebi_id:
                    master_record["identity"]["chebi"] = self.chebi.get_complete_entity(chebi_id)
            except Exception as e:
                logger.warning(f"ChEBI Error: {e}")

        return master_record