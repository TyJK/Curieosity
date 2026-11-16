import json
import os
import argparse
import logging
import csv
import pandas as pd
from typing import Dict, List, Any

from crd_client import CrdClient
from ord_client import OrdClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ReactionInspector")

class ReactionInspector:
    DATA_DIR = "tools/data"

    def __init__(self):
        self.uspto_path = os.path.join(self.DATA_DIR, "USPTO-50k_Reactions.csv")
        self.thermo_path = os.path.join(self.DATA_DIR, "ccsdtf12_dz_individual_heats_of_formation.csv")
        self.solid_state_path = os.path.join(self.DATA_DIR, "solid-state_dataset_2019-06-27_upd.json")
        self.solution_synth_path = os.path.join(self.DATA_DIR, "solutionsynthesis_dataset_202185.json")

        self.crd = CrdClient()
        self.ord = OrdClient()

    def _parse_reaction_smiles(self, rxn_smiles: str) -> Dict[str, List[str]]:
        if not rxn_smiles or ">" not in rxn_smiles: return None
        parts = rxn_smiles.split(">")
        return {
            "reactants": [s for s in parts[0].split(".") if s],
            "agents": [s for s in parts[1].split(".") if s] if len(parts) > 1 else [],
            "products": [s for s in parts[-1].split(".") if s]
        }

    def inspect_uspto(self, target: str, limit: int) -> List[Dict]:
        results = []
        if not os.path.exists(self.uspto_path): return []

        try:
            with open(self.uspto_path, 'r', encoding='utf-8') as f:
                sample = f.read(2048)
                f.seek(0)
                has_header = csv.Sniffer().has_header(sample)

                if has_header:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if len(results) >= limit: break
                        rxn_str = ""
                        # Heuristic search for the column
                        for v in row.values():
                            if v and ">" in str(v) and target in str(v):
                                rxn_str = v; break
                        if rxn_str:
                            results.append({
                                "id": row.get("id", "unknown"),
                                "raw_smiles": rxn_str,
                                "parsed": self._parse_reaction_smiles(rxn_str),
                                "metadata": {"yield": row.get("yield"), "class": row.get("class")}
                            })
                else:
                    reader = csv.reader(f)
                    for idx, row in enumerate(reader):
                        if len(results) >= limit: break
                        row_str = ",".join(row)
                        if target in row_str:
                            rxn_str = next((col for col in row if ">" in col), "")
                            if rxn_str:
                                results.append({
                                    "id": f"uspto_{idx}",
                                    "raw_smiles": rxn_str,
                                    "parsed": self._parse_reaction_smiles(rxn_str)
                                })
        except Exception as e:
            logger.error(f"USPTO scan failed: {e}")
        return results

    def inspect_thermo(self, target: str) -> List[Dict]:
        results = []
        if not os.path.exists(self.thermo_path): return []
        try:
            df = pd.read_csv(self.thermo_path)
            df.columns = [c.strip().lower() for c in df.columns]
            if 'rsmi' not in df.columns: return []

            mask = df['rsmi'].str.contains(target, regex=False) | df['psmi'].str.contains(target, regex=False)
            for _, row in df[mask].iterrows():
                results.append({
                    "source": "CCSD(T) Thermo",
                    "reaction_smiles": f"{row['rsmi']}>>{row['psmi']}",
                    "enthalpy_kj_mol": row.get('dhrxn298'),
                    "raw_row": row.to_dict()
                })
        except Exception: pass
        return results

    def inspect_json_dataset(self, target: str, file_path: str, source_name: str, limit: int) -> List[Dict]:
        results = []
        if not os.path.exists(file_path): return []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for entry in data:
                if len(results) >= limit: break
                if target in json.dumps(entry):
                    # Simplified extraction
                    results.append({
                        "source": source_name,
                        "doi": entry.get("doi"),
                        "raw_entry": entry # Pass full entry to synthesizer to parse
                    })
        except Exception: pass
        return results

    def inspect(self, target: str, limit: int = 5) -> Dict[str, Any]:
        logger.info(f"=== Inspecting Reactions for: '{target}' ===")

        master_log = {
            "meta": {"query": target},
            "dynamic_sources": {
                "uspto_50k": self.inspect_uspto(target, limit),
                "ord_local": [],
                "crd_web": []
            },
            "static_datasets": {
                "thermo_csv": self.inspect_thermo(target),
                "solid_state_json": self.inspect_json_dataset(target, self.solid_state_path, "SolidState", limit),
                "solution_synth_json": self.inspect_json_dataset(target, self.solution_synth_path, "SolutionSynth", limit)
            }
        }

        try:
            master_log["dynamic_sources"]["ord_local"] = self.ord.search_reactions(target, limit=limit)
        except Exception as e:
            logger.warning(f"ORD Search failed: {e}")

        try:
            master_log["dynamic_sources"]["crd_web"] = self.crd.fetch_and_filter(target, limit=limit)
        except Exception as e:
            logger.warning(f"CRD Search failed: {e}")

        return master_log

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("--out", default="tools/data/full_reaction.json")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    inspector = ReactionInspector()
    data = inspector.inspect(args.target, args.limit)

    with open(args.out, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {args.out}")