import requests
import logging
import os
import json
import gzip
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ORDClient")

# --- ORD LIBRARY CHECK ---
try:
    from ord_schema.proto import dataset_pb2, reaction_pb2
    from ord_schema import message_helpers
    ORD_LIB_AVAILABLE = True
except ImportError:
    ORD_LIB_AVAILABLE = False
    logger.warning("ORD-SCHEMA library not found. Please run 'pip install ord-schema' to use real data.")

class OrdClient:
    """
    Client for the Open Reaction Database (ORD).
    Deep Extraction Mode: Pulls Conditions, Yields, and Notes.
    """

    CACHE_DIR = "tools/data/ord_cache"
    CACHE_FILE = os.path.join(CACHE_DIR, "ord_slice_uspto.pb.gz")
    GITHUB_API_CONTENTS = "https://api.github.com/repos/open-reaction-database/ord-data/contents/data/01"

    def __init__(self):
        self._ensure_cache()

    def _get_candidate_urls(self) -> List[str]:
        """Generates a list of potential download URLs."""
        candidates = []
        try:
            logger.info("Querying GitHub API for file list...")
            resp = requests.get(self.GITHUB_API_CONTENTS)
            resp.raise_for_status()
            files = resp.json()

            target_file = None
            for f in files:
                if f["name"].endswith(".pb.gz"):
                    target_file = f
                    break

            if target_file:
                raw_url = target_file.get("download_url", "")
                if "raw.githubusercontent.com" in raw_url:
                    media_url = raw_url.replace("raw.githubusercontent.com", "media.githubusercontent.com/media")
                    candidates.append(media_url)
                if raw_url: candidates.append(raw_url)

        except Exception as e:
            logger.error(f"Failed to resolve dynamic URLs: {e}")

        return candidates

    def _ensure_cache(self):
        """Downloads the data slice if it doesn't exist locally."""
        if os.path.exists(self.CACHE_FILE):
            try:
                with gzip.open(self.CACHE_FILE, 'rb') as f:
                    f.read(1)
            except Exception:
                logger.warning("Existing cache file is corrupt. Re-downloading...")
                os.remove(self.CACHE_FILE)
            else:
                return

        os.makedirs(self.CACHE_DIR, exist_ok=True)
        urls = self._get_candidate_urls()

        if not urls:
            logger.error("No download URLs found.")
            return

        for url in urls:
            logger.info(f"Attempting download from: {url}")
            try:
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    first_chunk = next(r.iter_content(chunk_size=1024), b"")
                    if first_chunk.startswith(b"version https://git-lfs"):
                        logger.warning("Detected Git LFS Pointer. Skipping.")
                        continue
                    with open(self.CACHE_FILE, 'wb') as f:
                        f.write(first_chunk)
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                logger.info(f"Download complete. Saved to {self.CACHE_FILE}")
                return
            except Exception as e:
                logger.error(f"Download failed: {e}")
                if os.path.exists(self.CACHE_FILE): os.remove(self.CACHE_FILE)

        logger.error("ALL DOWNLOADS FAILED. Please download manually.")

    def _extract_temperature(self, conds) -> Optional[Dict]:
        if not conds.HasField("temperature"): return None
        t = conds.temperature
        if t.HasField("setpoint"):
            val = t.setpoint.value
            try:
                unit = reaction_pb2.Temperature.TemperatureUnit.Name(t.setpoint.units)
            except: unit = "CELSIUS"
            return {"setpoint": val, "unit": unit}
        return None

    def _extract_yield(self, outcome) -> Optional[float]:
        """Digs for yield percentage in product measurements."""
        for prod in outcome.products:
            for meas in prod.measurements:
                # Robustly check for YIELD type
                try:
                    type_name = reaction_pb2.ProductMeasurement.MeasurementType.Name(meas.type)
                    if "YIELD" in type_name and meas.HasField("percentage"):
                        return meas.percentage.value
                except:
                    pass
        return None

    def search_reactions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Parses the local protobuf file and searches for the query string."""
        if not ORD_LIB_AVAILABLE:
            logger.error("Cannot search: 'ord-schema' not installed.")
            return []

        if not os.path.exists(self.CACHE_FILE):
            logger.error("ORD Cache file missing.")
            return []

        results = []
        query_clean = query.strip()
        logger.info(f"Scanning local ORD slice for '{query_clean}'...")

        try:
            dataset = message_helpers.load_message(self.CACHE_FILE, dataset_pb2.Dataset)

            try:
                SMILES_TYPE = reaction_pb2.CompoundIdentifier.SMILES
            except AttributeError:
                SMILES_TYPE = reaction_pb2.CompoundIdentifier.IdentifierType.SMILES

            for reaction in dataset.reactions:
                if len(results) >= limit: break

                match_found = False
                # Search Inputs
                for input_obj in reaction.inputs.values():
                    for c in input_obj.components:
                        for i in c.identifiers:
                            if i.type == SMILES_TYPE and query_clean in i.value:
                                match_found = True; break
                    if match_found: break

                # Search Outcomes
                if not match_found:
                    for outcome in reaction.outcomes:
                        for prod in outcome.products:
                            for i in prod.identifiers:
                                if i.type == SMILES_TYPE and query_clean in i.value:
                                    match_found = True; break
                        if match_found: break

                if match_found:
                    # --- DEEP EXTRACTION ---
                    rxn_dict = {
                        "reactionId": reaction.reaction_id,
                        "inputs": {},
                        "outcomes": [],
                        "conditions": {},
                        "notes": {}
                    }

                    # 1. Conditions
                    conds = reaction.conditions
                    temp = self._extract_temperature(conds)
                    if temp: rxn_dict["conditions"]["temperature"] = temp

                    if conds.HasField("pressure"):
                        p = conds.pressure
                        if p.HasField("atmosphere"):
                            try:
                                a_type = reaction_pb2.Pressure.Atmosphere.Type.Name(p.atmosphere.type)
                                rxn_dict["conditions"]["pressure"] = {"type": "Atmosphere", "details": a_type}
                            except: pass
                        elif p.HasField("setpoint"):
                            rxn_dict["conditions"]["pressure"] = {"value": p.setpoint.value}

                    if conds.HasField("stirring"):
                        s = conds.stirring
                        if s.HasField("rate"):
                            rxn_dict["conditions"]["stirring"] = {"rpm": s.rate.value}

                    # 2. Notes
                    if reaction.notes.procedure_details:
                        rxn_dict["notes"]["procedure"] = reaction.notes.procedure_details

                    # 3. Inputs
                    for key, input_obj in reaction.inputs.items():
                        comps = []
                        for c in input_obj.components:
                            idents = [{"type": "SMILES", "value": i.value}
                                      for i in c.identifiers if i.type == SMILES_TYPE]
                            if idents:
                                try:
                                    role_name = reaction_pb2.ReactionRole.Name(c.reaction_role)
                                except: role_name = "UNKNOWN"

                                comps.append({
                                    "reactionRole": role_name,
                                    "identifiers": idents,
                                    "amount": c.amount.mass.value if c.amount.HasField("mass") else None
                                })
                        if comps:
                            rxn_dict["inputs"][key] = {"components": comps}

                    # 4. Outcomes & Yields
                    for outcome in reaction.outcomes:
                        prods = []
                        outcome_yield = self._extract_yield(outcome)

                        for p in outcome.products:
                            idents = [{"type": "SMILES", "value": i.value}
                                      for i in p.identifiers if i.type == SMILES_TYPE]
                            if idents:
                                prods.append({"identifiers": idents})

                        outcome_dict = {"products": prods}
                        if outcome_yield is not None:
                            outcome_dict["yield_percent"] = outcome_yield

                        # FIX: Correctly parse Analysis Map (No 'analysis_identity' attribute)
                        analyses_list = []
                        for analysis in outcome.analyses.values():
                            try:
                                a_type = reaction_pb2.ReactionAnalysis.AnalysisType.Name(analysis.type)
                                analyses_list.append(a_type)
                            except: pass

                        if analyses_list:
                            outcome_dict["analyses"] = analyses_list

                        rxn_dict["outcomes"].append(outcome_dict)

                    results.append(rxn_dict)

            logger.info(f"Found {len(results)} reactions in local slice.")
            return results

        except Exception as e:
            logger.error(f"Error parsing ORD protobuf: {e}")
            return []

if __name__ == "__main__":
    if ORD_LIB_AVAILABLE:
        client = OrdClient()
        results = client.search_reactions("OS(=O)(=O)O", limit=1)
        if results:
            print("Deep Extraction Successful. Sample Keys:", results[0].keys())
            if "conditions" in results[0]:
                print("Conditions found:", results[0]["conditions"])