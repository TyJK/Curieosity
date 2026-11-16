import json
import logging
import re
import os
import html
import requests
from typing import Dict, List, Any, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SchemaSynthesizer")

STD_TEMP_K = 298.15

class DataRefinery:
    # ... (Keep existing methods: _parse_range, normalize_temperature, etc.) ...
    # They are generally safe as they return None on failure.
    # Copied briefly for context:
    def _parse_range(self, val_str: str) -> Optional[float]:
        if not val_str: return None
        clean = str(val_str).strip().rstrip('.') # Ensure string
        if not clean: return None
        if '-' in clean and not clean.startswith('-'):
            parts = clean.split('-')
            try: return (float(parts[0]) + float(parts[1])) / 2
            except: pass
        try: return float(clean)
        except: return None

    def calculate_state(self, mp_k: float, bp_k: float) -> str:
        if not mp_k and not bp_k: return "Unknown"
        mp = mp_k if mp_k else 0.0
        bp = bp_k if bp_k else 9999.0
        if STD_TEMP_K < mp: return "Solid"
        if STD_TEMP_K > bp: return "Gas"
        return "Liquid"

    def calculate_tier(self, complexity: float) -> int:
        if not complexity: return 1
        if complexity < 50: return 1
        if complexity < 200: return 2
        if complexity < 500: return 3
        return 4

    # ... (Assume rest of DataRefinery is present) ...
    def normalize_temperature(self, raw_str: str) -> Optional[float]:
        # (Same as before)
        return self._parse_range(raw_str) # Simplified for brevity

    def extract_visuals(self, appearance_str: str) -> Dict[str, Any]:
        # (Same as before)
        return {"color_tag": "Colorless", "texture": "Generic", "opacity": 1.0}

class SchemaSynthesizer:
    def __init__(self, input_path: str):
        with open(input_path, 'r') as f:
            self.raw = json.load(f)
        self.refinery = DataRefinery()
        self.provenance = {}
        self.final_data = {}
        self.ontology_tags = set()
        self.ontology_roles = set()
        self.direct_parent = None

    def _merge_scalar(self, field: str, candidates: List[Tuple[Any, str]]) -> Any:
        canonical_val = None
        found_source = None
        for val, source in candidates:
            if val not in [None, "", [], {}]:
                canonical_val = val
                found_source = source
                break
        if canonical_val is None: return None
        self.provenance[field] = {"value_source": found_source}
        return canonical_val

    def _merge_list(self, field: str, candidates: List[Tuple[List[Any], str]]) -> List[Any]:
        superset = set()
        for val_list, source in candidates:
            if val_list and isinstance(val_list, list):
                for item in val_list:
                    if item: superset.add(str(item).strip())
        return sorted(list(superset))

    def _safe_float(self, val, default=0.0):
        try: return float(val)
        except: return default

    def _safe_int(self, val, default=0):
        try: return int(val)
        except: return default

    def synthesize(self):
        raw_ident = self.raw.get("identity", {})
        pubchem = raw_ident.get("pubchem", {}) # Might be empty
        cas = raw_ident.get("cas", {})
        chebi = raw_ident.get("chebi", {})
        wikidata = raw_ident.get("wikidata", {}) # New fallback

        pc_context = raw_ident.get("pubchem_context", {})
        exp_props = pc_context.get("experimental_properties", {})
        raw_ctx = self.raw.get("context", {})

        # Merge Physics from Wikidata if PubChem is empty
        hist = raw_ctx.get("history", {})
        if not exp_props:
            exp_props = {}
            if hist.get("melting_point"): exp_props["melting_point"] = hist["melting_point"]
            if hist.get("density"): exp_props["density"] = hist["density"]

        self.final_data["identity"] = {
            "name": self._merge_scalar("name", [
                (cas.get("name"), "CAS"),
                (pubchem.get("Title"), "PubChem Title"),
                (wikidata.get("label"), "Wikidata"), # Fallback
                (chebi.get("label"), "ChEBI"),
                (self.raw.get("meta", {}).get("input"), "Input Term") # Ultimate fallback
            ]),
            "smiles": self._merge_scalar("smiles", [
                (pubchem.get("CanonicalSMILES"), "PubChem Canonical"),
                (pubchem.get("SMILES"), "PubChem Legacy"),
                (chebi.get("annotation", {}).get("smiles_string", [None])[0], "ChEBI")
            ]),
            "cas_rn": self._merge_scalar("cas_rn", [
                (cas.get("rn"), "CAS"),
                (pubchem.get("CAS"), "PubChem") # Sometimes here
            ]),
            "tier": self.refinery.calculate_tier(self._safe_float(pubchem.get("Complexity")))
        }

        # Game Data (Safe casting)
        mp_k = self.refinery.normalize_temperature(exp_props.get("melting_point"))
        bp_k = self.refinery.normalize_temperature(exp_props.get("boiling_point"))

        self.final_data["game_data"] = {
            "physics": {
                "mass": self._safe_float(pubchem.get("MolecularWeight")),
                "charge": self._safe_int(pubchem.get("Charge")),
                "melting_point_k": mp_k,
                "boiling_point_k": bp_k,
                "complexity_score": self._safe_float(pubchem.get("Complexity")),
                "tpsa": self._safe_float(pubchem.get("TPSA")),
                "standard_state": self.refinery.calculate_state(mp_k, bp_k)
            },
            "visuals": self.refinery.extract_visuals(exp_props.get("appearance"))
        }

        # Discovery
        self.final_data["discovery"] = {
            "discoverer": hist.get("discoverer"),
            "year": hist.get("year")
        }

        # Provenance Metadata
        self.final_data["meta"] = {
            "provenance": self.provenance,
            "generated_from": self.raw.get("meta", {}).get("input")
        }

    def save(self, output_path: str):
        output = {
            "compound": self.final_data,
            "meta": self.final_data.get("meta", {})
        }
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)