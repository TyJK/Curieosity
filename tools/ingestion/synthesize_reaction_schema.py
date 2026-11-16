import json
import logging
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from rdkit import Chem
from rdkit.Chem import rdChemReactions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ReactionSynthesizer")

# --- HEURISTICS & CONSTANTS ---
BOND_ENERGIES = {
    "H-H": 436, "C-H": 413, "C-C": 348, "C=C": 614, "C#C": 839,
    "C-O": 358, "C=O": 799, "O-H": 463, "O=O": 495, "N#N": 941,
    "Cl-Cl": 242, "H-Cl": 431, "S=O": 523, "S-O": 265, "N-H": 391
}

class TextMiner:
    def extract_temperature(self, text: str) -> Optional[float]:
        if not text: return None
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:-|to)?\s*(?:\d+)?\s*°?\s*C', text, re.IGNORECASE)
        if match: return round(float(match.group(1)) + 273.15, 2)
        if "reflux" in text.lower(): return 373.15
        if "ice" in text.lower() and "bath" in text.lower(): return 273.15
        return None

    def extract_time(self, text: str) -> Optional[float]:
        if not text: return None
        h_match = re.search(r'(\d+(?:\.\d+)?)\s*h(?:ours?)?', text, re.IGNORECASE)
        if h_match: return float(h_match.group(1)) * 3600.0
        m_match = re.search(r'(\d+(?:\.\d+)?)\s*min(?:utes?)?', text, re.IGNORECASE)
        if m_match: return float(m_match.group(1)) * 60.0
        if "overnight" in text.lower(): return 43200.0
        return None

    def extract_yield(self, text: str) -> Optional[float]:
        if not text: return None
        match = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
        if match: return round(float(match.group(1)) / 100.0, 2)
        return None

    def check_keywords(self, text: str) -> List[str]:
        tags = []
        if not text: return tags
        t = text.lower()
        if "exotherm" in t or "heat evolution" in t: tags.append("Exothermic")
        if "vigorous" in t or "violent" in t: tags.append("Violent")
        if "gas" in t or "effervesc" in t: tags.append("Gas Evolution")
        if "precipitate" in t or "solid" in t: tags.append("Precipitation")
        return tags

class BondEnergyCalculator:
    def get_molecule_energy(self, mol) -> float:
        if not mol: return 0.0
        total_energy = 0.0
        try:
            for bond in mol.GetBonds():
                btype = bond.GetBondTypeAsDouble()
                begin = bond.GetBeginAtom().GetSymbol()
                end = bond.GetEndAtom().GetSymbol()
                key = f"{begin}-{end}" if begin < end else f"{end}-{begin}"
                if btype == 2.0: key = key.replace("-", "=")
                if btype == 3.0: key = key.replace("-", "#")
                total_energy += BOND_ENERGIES.get(key, 300.0)
        except: pass
        return total_energy

    def estimate_enthalpy(self, reactants_smiles: List[str], products_smiles: List[str]) -> float:
        energy_in = 0.0
        for s in reactants_smiles:
            mol = Chem.MolFromSmiles(s)
            if mol: energy_in += self.get_molecule_energy(mol)
        energy_out = 0.0
        for s in products_smiles:
            mol = Chem.MolFromSmiles(s)
            if mol: energy_out += self.get_molecule_energy(mol)
        return energy_in - energy_out

class ReactionSynthesizer:
    def __init__(self, inspection_path: str):
        with open(inspection_path, 'r') as f:
            self.raw = json.load(f)

        self.bond_calc = BondEnergyCalculator()
        self.text_miner = TextMiner()
        self.final_record = {}

        # The Hash Map for Merging
        self.reaction_map = {}

    def _generate_hash(self, reactants: List[str], products: List[str]) -> str:
        """
        Creates a canonical fingerprint: SortedReactants>>SortedProducts
        Using Canonical SMILES from RDKit ensures A.B == B.A
        """
        def canonicalize(s_list):
            canon = []
            for s in s_list:
                try:
                    m = Chem.MolFromSmiles(s)
                    if m: canon.append(Chem.MolToSmiles(m, isomericSmiles=True))
                    else: canon.append(s) # Fallback
                except: canon.append(s)
            return ".".join(sorted(canon))

        r_hash = canonicalize(reactants)
        p_hash = canonicalize(products)
        return f"{r_hash}>>{p_hash}"

    def _parse_smiles_parts(self, rxn_smiles: str) -> Dict:
        parts = rxn_smiles.split(">")
        return {
            "reactants": [s for s in parts[0].split(".") if s],
            "agents": [s for s in parts[1].split(".") if s] if len(parts) > 1 else [],
            "products": [s for s in parts[-1].split(".") if s]
        }

    def _process_ord_entry(self, entry: Dict):
        try:
            # 1. Extract Reactants/Products/Agents (Using Advanced Heuristic from before)
            reactants_found = []
            agents_found = []

            # EXTENDED AGENT LIST
            COMMON_AGENTS = {
                "O", "OS(=O)(=O)O", "ClCCl", "C1CCOC1", "CCO", "CO",
                "CS(=O)C", "Cc1ccccc1", "C(Cl)Cl", "C(C)O",
                "CN(C)C=O", "C#N", "C1=CC=CC=C1",
                "[OH-]", "[H+]", "[Na+]", "[K+]", "[Cl-]",
                "O=[V](=O)O[V](=O)=O"
            }
            TRANSITION_METALS = {"Fe", "Ni", "Pd", "Pt", "Au", "Cu", "Zn", "Rh", "Ir", "Ru", "V", "Ti"}

            for k, v in entry.get("inputs", {}).items():
                for c in v.get("components", []):
                    role = c.get("reactionRole", "UNKNOWN")
                    smiles = None
                    for i in c.get("identifiers", []):
                        if i["type"] == "SMILES":
                            smiles = i["value"]; break

                    if not smiles: continue

                    is_explicit_agent = role in ["CATALYST", "SOLVENT", "REAGENT", "WORKUP"]
                    is_common_agent = role == "UNKNOWN" and smiles in COMMON_AGENTS
                    has_metal = any(m in smiles for m in TRANSITION_METALS)
                    is_metal_catalyst = role == "UNKNOWN" and has_metal

                    if is_explicit_agent or is_common_agent or is_metal_catalyst:
                        agents_found.append({"smiles": smiles, "role": "Agent", "optional": False})
                    else:
                        reactants_found.append({"smiles": smiles, "role": "Reactant", "ratio": 1})

            # Fallback
            if not reactants_found and agents_found:
                for i, ag in enumerate(agents_found):
                    if ag["smiles"] not in COMMON_AGENTS:
                        reactants_found.append({"smiles": ag["smiles"], "role": "Reactant", "ratio": 1})
                        agents_found.pop(i); break

            p_smiles = []
            for o in entry.get("outcomes", []):
                for p in o.get("products", []):
                    for i in p.get("identifiers", []):
                        if i["type"] == "SMILES": p_smiles.append(i["value"])

            if not reactants_found or not p_smiles: return

            # 2. Generate Hash
            r_list = [r["smiles"] for r in reactants_found]
            rxn_hash = self._generate_hash(r_list, p_smiles)

            # 3. Mine Data
            notes = entry.get("notes", {}).get("procedure", "")
            temp_k = self.text_miner.extract_temperature(notes)
            time_s = self.text_miner.extract_time(notes)
            yield_val = self.text_miner.extract_yield(notes)
            tags = self.text_miner.check_keywords(notes)
            enthalpy = self.bond_calc.estimate_enthalpy(r_list, p_smiles)

            # 4. Construct Record
            record = {
                "identity": {
                    "id": entry.get("reactionId"),
                    "source": "ORD",
                    "hash": rxn_hash,
                    "classification": "Synthesis"
                },
                "inputs": {
                    "stoichiometry": reactants_found,
                    "agents": agents_found
                },
                "outcomes": [{"smiles": s, "role": "Product"} for s in p_smiles],
                "game_data": {
                    "conditions": {
                        "temperature_k": temp_k,
                        "duration_seconds": time_s,
                        "pressure_atm": 1.0
                    },
                    "metrics": {
                        "yield_base": yield_val if yield_val else 0.85,
                        "enthalpy_change": enthalpy
                    },
                    "tags": tags
                },
                "pedagogy": {
                    "procedure": notes[:300] + "..." if len(notes) > 300 else notes
                }
            }

            # 5. MERGE LOGIC: ORD is "High Quality" base
            self.reaction_map[rxn_hash] = record

        except Exception as e:
            logging.warning(f"Skipping ORD entry: {e}")

    def _process_crd_entry(self, entry: Dict):
        smiles = entry.get("reaction_smiles")
        if not smiles: return

        parsed = self._parse_smiles_parts(smiles)
        r_list = parsed["reactants"]
        p_list = parsed["products"]
        rxn_hash = self._generate_hash(r_list, p_list)

        # MERGE CHECK: Do we already have this from ORD?
        if rxn_hash in self.reaction_map:
            # YES: We have an ORD record.
            # Strategy: CRD has better structural parsing (Reactant vs Agent).
            # Let's trust CRD's AGENT list if ORD's was heuristic-based.
            existing = self.reaction_map[rxn_hash]

            # Overwrite agents with the cleaner CRD list
            new_agents = [{"smiles": s, "role": "Agent"} for s in parsed["agents"]]
            if new_agents:
                existing["inputs"]["agents"] = new_agents
                existing["meta_merge"] = "CRD Structure + ORD Physics"
                logger.info(f"Merged CRD structure into ORD record: {rxn_hash}")

        else:
            # NO: Create new record from CRD
            enthalpy = self.bond_calc.estimate_enthalpy(r_list, p_list)
            record = {
                "identity": {
                    "id": entry.get("reactionId"),
                    "source": "CRD",
                    "hash": rxn_hash,
                    "classification": "Generic"
                },
                "inputs": {
                    "stoichiometry": [{"smiles": s, "role": "Reactant"} for s in r_list],
                    "agents": [{"smiles": s, "role": "Agent"} for s in parsed["agents"]]
                },
                "outcomes": [{"smiles": s, "role": "Product"} for s in p_list],
                "game_data": {
                    "conditions": {
                        "temperature_k": 298.15,
                        "duration_seconds": 60.0
                    },
                    "metrics": {
                        "enthalpy_change": enthalpy,
                        "yield_base": 0.8
                    },
                    "tags": ["Generic"]
                }
            }
            self.reaction_map[rxn_hash] = record

    def synthesize(self):
        # 1. Load ORD first (Rich Data)
        ord_matches = self.raw.get("dynamic_sources", {}).get("ord_local", [])
        for entry in ord_matches:
            self._process_ord_entry(entry)

        # 2. Load CRD second (Volume + Structure)
        crd_matches = self.raw.get("dynamic_sources", {}).get("crd_web", [])
        for entry in crd_matches:
            self._process_crd_entry(entry)

        self.final_record = {
            "meta": self.raw.get("meta"),
            "reactions": list(self.reaction_map.values())
        }

    def save(self, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.final_record, f, indent=2)
        logger.info(f"Saved {len(self.final_record['reactions'])} unique reactions to {output_path}")

if __name__ == "__main__":
    syn = ReactionSynthesizer("tools/data/full_reaction.json")
    syn.synthesize()
    syn.save("tools/data/canonical_reaction_chain.json")