import json
import os
import argparse
import logging
from typing import Dict, Any, Optional

# Import Clients
from tools.ingestion.pubchem_client import PubChemClient
from tools.ingestion.chebi_client import ChEBIClient
from tools.ingestion.cas_client import CasClient
from tools.ingestion.wikidata_client import WikidataClient
from tools.ingestion.surechembl_client import SureChemblClient

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

    def extract_cas_rn(self, chebi_data: Dict[str, Any]) -> Optional[str]:
        xrefs = chebi_data.get("annotation", {}).get("database_cross_reference", [])
        if not xrefs: return None
        for ref in xrefs:
            if ref.lower().startswith("cas:"):
                return ref.split(":")[1].strip()
        return None

    def inspect(self, input_term: str, known_cas_rn: str = None) -> Dict[str, Any]:
        """
        Main inspection logic.
        :param input_term: SMILES or Name to search PubChem/ChEBI with.
        :param known_cas_rn: Optional CAS RN from source CSV (High Confidence).
        """
        logger.info(f"=== Inspecting Compound: '{input_term}' (CAS: {known_cas_rn}) ===")

        # 1. Identity Resolution
        target_name = None
        target_smiles = None
        is_smiles = any(c in input_term for c in "=#/[]")
        # Heuristic: If it has no spaces and contains typical SMILES chars, treat as SMILES
        # But for very short strings like "O" or "CCC", this can be tricky.
        # Ideally, we rely on the caller (BatchOrchestrator) knowing what it passed.
        # If input_term came from CAS as a SMILES, it is a SMILES.

        resolved_props = {}
        cid = None

        if is_smiles or len(input_term) < 4 and input_term.isupper():
            # Treat short upper strings (O, CCC) as SMILES/Formula context
            target_smiles = input_term
            try:
                props = self.pubchem.fetch_compound_properties([input_term], namespace="smiles")
                if props:
                    resolved_props = props[0]
                    cid = str(resolved_props.get("CID"))
                    target_name = resolved_props.get("Title") or resolved_props.get("IUPACName")
            except Exception:
                target_name = None # Don't set to "Unknown", keep None to trigger fallbacks
        else:
            target_name = input_term
            try:
                props = self.pubchem.fetch_compound_properties([input_term], namespace="name")
                if props:
                    resolved_props = props[0]
                    cid = str(resolved_props.get("CID"))
                    target_smiles = resolved_props.get("CanonicalSMILES")
            except Exception:
                pass

        # 2. Build Record
        master_record = {
            "meta": {
                "input": input_term,
                "resolved_name": target_name,
                "resolved_smiles": target_smiles
            },
            "identity": {
                "pubchem": resolved_props,
                "pubchem_context": {},
                "pubchem_3d_conformer": None,
                "chebi": {},
                "cas": {}
            },
            "context": {
                "history": {},
                "legal": {},
                "patents": []
            }
        }

        # 3. Fetch Details (PubChem)
        if cid:
            master_record["identity"]["pubchem_context"] = self.pubchem.fetch_compound_context(cid)
            sdf = self.pubchem.fetch_3d_sdf(cid)
            if sdf: master_record["identity"]["pubchem_3d_conformer"] = sdf

        # 4. Fetch Details (ChEBI)
        # CRITICAL FIX: Only search ChEBI if we have a valid NAME.
        # Do not search using SMILES (e.g. "CCC") as it yields garbage.
        if target_name and target_name != "Unknown":
            chebi_id = self.chebi.search_entity(target_name)
            if chebi_id:
                chebi_data = self.chebi.get_complete_entity(chebi_id)
                master_record["identity"]["chebi"] = chebi_data
                if not known_cas_rn:
                    known_cas_rn = self.extract_cas_rn(chebi_data)
        else:
            logger.info("Skipping ChEBI search: No valid Target Name resolved.")

        # 5. Fetch Details (CAS)
        if known_cas_rn:
            cas_hit = self.cas.search_substance(known_cas_rn)
            if cas_hit:
                master_record["identity"]["cas"] = cas_hit
                # If we have a CAS hit, we might get a better name for Wikidata later
                if not target_name and cas_hit.get("name"):
                    target_name = cas_hit["name"]
        elif target_smiles:
            cas_hit = self.cas.resolve_smiles(target_smiles)
            if cas_hit:
                master_record["identity"]["cas"] = cas_hit

        # 6. Context (Wikidata & Patents)
        inchikey = resolved_props.get("InChIKey")

        # CRITICAL FIX: Ensure we have a Name or CAS before querying Wikidata history
        if target_name or known_cas_rn:
            search_name = target_name if target_name else "Unknown"
            master_record["context"]["history"] = self.wiki.get_history(search_name, inchikey=inchikey, cas_rn=known_cas_rn)

        if inchikey:
            ids = self.surechembl.get_patent_ids(inchikey)
            master_record["context"]["legal"]["surechembl_ids"] = ids
            if ids:
                master_record["context"]["legal"]["link"] = f"https://www.surechembl.org/chemical/{ids[0]}"

        if target_name and self.uspto_context:
            master_record["context"]["patents"] = self.uspto_context.search_patent_applications(target_name)

        return master_record

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Compound Identifier")
    parser.add_argument("--cas", help="Known CAS RN", default=None)
    parser.add_argument("--out", default="tools/data/full_compound2.json")
    args = parser.parse_args()

    inspector = CompoundInspector()
    data = inspector.inspect(args.target, known_cas_rn=args.cas)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {args.out}")