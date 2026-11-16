import json
import os
import re
import logging
import copy
import sys
from typing import Dict, Any, List

# --- DEPENDENCIES ---
sys.path.append(os.path.abspath("."))
try:
    from ord_client import OrdClient
    from tools.ingestion.pubchem_client import PubChemClient
    from rdkit import Chem
    from rdkit.Chem import AllChem, rdChemReactions
    from rdkit import RDLogger
except ImportError as e:
    print(f"⚠️ Critical Dependency Missing: {e}")
    sys.exit(1)

# --- SILENCE RDKIT NOISE ---
RDLogger.DisableLog('rdApp.*')

# --- CONFIGURATION ---
OUTPUT_DIR = "./tools/data/reaction_dataset"
LOG_DIR = "./tools/logs"
SCHEMA_PATH = "./tools/data/canon_reaction.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("EnrichedBuilder")

# --- HELPER CLASSES ---
class ReactionClassifier:
    """
    Uses RDKit Substructure Matching (Robust) instead of string matching (Fragile).
    """
    def __init__(self):
        # Define SMARTS queries for functional groups
        self.groups = {
            "ester": Chem.MolFromSmarts("[CX3](=[OX1])[OX2][#6]"),      # Ester group
            "amide": Chem.MolFromSmarts("[CX3](=[OX1])[#7]"),           # Amide group
            "acyl_cl": Chem.MolFromSmarts("[CX3](=[OX1])[Cl]"),         # Acyl Chloride
            "sulfone": Chem.MolFromSmarts("[#6][SX4](=[OX1])(=[OX1])[#6]"), # Sulfone (C-S(=O)(=O)-C)
            "sulfonic_acid": Chem.MolFromSmarts("[SX4](=[OX1])(=[OX1])[OX2H]"), # Sulfonic Acid
            "nitro": Chem.MolFromSmarts("[N+](=O)[O-]")                  # Nitro
        }

    def classify(self, reaction_smiles: str) -> Dict[str, Any]:
        tags = []
        primary = "Unclassified"

        if not reaction_smiles or ">>" not in reaction_smiles:
            return {"primary_type": primary, "tags": tags}

        try:
            # Parse Reactants/Products into Mols
            r_smi, p_smi = reaction_smiles.split(">>")
            # Create a "bag of reactants" and "bag of products" for matching
            # (We join with dot to treat as one big disconnected molecule for easier searching)
            r_mol = Chem.MolFromSmiles(r_smi)
            p_mol = Chem.MolFromSmiles(p_smi)

            if not r_mol or not p_mol: return {"primary_type": primary, "tags": tags}

            # 1. ESTERIFICATION
            # Reactant has Acid/AcylCl, Product has Ester, Reactant did NOT have Ester (or had fewer)
            p_esters = len(p_mol.GetSubstructMatches(self.groups["ester"]))
            r_esters = len(r_mol.GetSubstructMatches(self.groups["ester"]))

            if p_esters > r_esters:
                primary = "Condensation"
                tags.append("Esterification")

            # 2. AMIDATION
            p_amides = len(p_mol.GetSubstructMatches(self.groups["amide"]))
            r_amides = len(r_mol.GetSubstructMatches(self.groups["amide"]))

            if p_amides > r_amides:
                primary = "Acylation"
                tags.append("Amide Formation")

            # 3. SULFONATION
            # Check for appearance of Sulfone or Sulfonic Acid group
            if (p_mol.HasSubstructMatch(self.groups["sulfone"]) and not r_mol.HasSubstructMatch(self.groups["sulfone"])) or \
                    (p_mol.HasSubstructMatch(self.groups["sulfonic_acid"]) and not r_mol.HasSubstructMatch(self.groups["sulfonic_acid"])):
                primary = "Electrophilic Substitution"
                tags.append("Sulfonation")

        except Exception:
            pass

        return {"primary_type": primary, "tags": tags}

class TextMiner:
    PATTERNS = {
        "time": re.compile(r"(\d+(?:\.\d+)?)\s*-?\s*(\d+(?:\.\d+)?)?\s*(?:h|hr|hours|min|minutes)", re.IGNORECASE),
        "temp_val": re.compile(r"(\d+(?:\.\d+)?)\s*(?:°|deg)?\s*C\b", re.IGNORECASE),
        "temp_kw": re.compile(r"\b(reflux|room temp|ambient)", re.IGNORECASE),
        # Catch broad percentages
        "percent_val": re.compile(r"(\d+(?:\.\d+)?)\s*%", re.IGNORECASE)
    }

    # Blocklist to prevent "0.5% acetic acid" being read as yield
    YIELD_BLOCKLIST = ["acid", "solution", "containing", "purity", "ee", "volume", "weight"]

    @staticmethod
    def extract(text):
        res = {}
        if not text: return res

        # Temp & Time (Unchanged)
        t = TextMiner.PATTERNS["temp_val"].search(text)
        if t: res["temp_k"] = float(t.group(1)) + 273.15
        else:
            kw = TextMiner.PATTERNS["temp_kw"].search(text)
            if kw:
                word = kw.group(1).lower()
                if "room" in word or "ambient" in word: res["temp_k"] = 298.15
                elif "reflux" in word: res["temp_k"] = 373.15

        tm = TextMiner.PATTERNS["time"].search(text)
        if tm:
            val = float(tm.group(1))
            res["time_s"] = val * 3600 if "h" in tm.group(0).lower() else val * 60

        # ROBUST YIELD MINING
        # Strategy: Find all % values, pick the one closest to the word "yield"
        # that ISN'T followed by a blocklisted word.

        candidates = []
        for match in TextMiner.PATTERNS["percent_val"].finditer(text):
            val = float(match.group(1))
            if not (0 < val <= 100): continue

            # Check immediate context (next 15 chars)
            start, end = match.span()
            context = text[end:end+15].lower()

            if any(bad in context for bad in TextMiner.YIELD_BLOCKLIST):
                continue # Skip "0.5% acetic acid"

            # Score by distance to "yield" or "obtain"
            # Find nearest "yield" keyword
            dist = float('inf')
            for kw in ["yield", "obtain", "afford"]:
                idx = text.lower().find(kw)
                if idx != -1:
                    d = abs(start - idx)
                    if d < dist: dist = d

            candidates.append((val, dist))

        if candidates:
            # Sort by distance to keyword (closest wins)
            candidates.sort(key=lambda x: x[1])
            res["yield_pct"] = candidates[0][0]

        return res

class EnrichedReactionBuilder:
    def __init__(self):
        self.ord = OrdClient()
        self.classifier = ReactionClassifier()
        self.safety = None # Lazy load to prevent spam if not needed
        self.stats = {"processed": 0, "mined_yield": 0, "mined_temp": 0, "classified": 0}

        try:
            with open(SCHEMA_PATH, 'r') as f:
                self.schema_template = json.load(f)
        except:
            logger.error("❌ Schema not found.")
            sys.exit(1)

    def process(self, raw_data):
        record = copy.deepcopy(self.schema_template)

        # 1. CORE
        record["identity"]["id"] = raw_data.get("reactionId", "")

        # 2. STOICHIOMETRY
        inputs = raw_data.get("inputs", {})
        outcomes = raw_data.get("outcomes", [])
        reactants = []
        products = []

        for key, val in inputs.items():
            for comp in val.get("components", []):
                smi = next((i["value"] for i in comp["identifiers"] if i["type"] == "SMILES"), None)
                if smi:
                    mol = Chem.MolFromSmiles(smi)
                    if mol: mol.UpdatePropertyCache(strict=False)
                    reactants.append({
                        "substance_name": key, "smiles": smi, "role": "REACTANT",
                        "formula": AllChem.CalcMolFormula(mol) if mol else ""
                    })

        ord_yield = 0.0
        for out in outcomes:
            if "yield_percent" in out: ord_yield = out["yield_percent"]
            for prod in out.get("products", []):
                smi = next((i["value"] for i in prod["identifiers"] if i["type"] == "SMILES"), None)
                if smi:
                    mol = Chem.MolFromSmiles(smi)
                    if mol: mol.UpdatePropertyCache(strict=False)
                    products.append({
                        "substance_name": "Product", "smiles": smi, "role": "PRODUCT", "is_major": True,
                        "formula": AllChem.CalcMolFormula(mol) if mol else ""
                    })

        record["stoichiometry"]["reactants"] = reactants
        record["stoichiometry"]["products"] = products

        r_str = ".".join([x["smiles"] for x in reactants])
        p_str = ".".join([x["smiles"] for x in products])
        rxn_smiles = f"{r_str}>>{p_str}"
        record["identity"]["reaction_smiles"] = rxn_smiles

        # 3. TEXT MINING
        proc_text = ""
        mined_data = {}
        if "notes" in raw_data and "procedure" in raw_data["notes"]:
            proc_text = raw_data["notes"]["procedure"]
            record["identity"]["description"] = f"Procedure: {proc_text}"
            mined_data = TextMiner.extract(proc_text)

            if "temp_k" in mined_data:
                record["conditions"]["temperature"]["value_k"] = mined_data["temp_k"]
                record["conditions"]["temperature"]["source"] = "Text Mining"
                self.stats["mined_temp"] += 1
            if "time_s" in mined_data:
                record["conditions"]["time"]["value_seconds"] = mined_data["time_s"]

        # 4. YIELD STRATEGY
        final_yield = 0.0
        # If ORD has valid yield (>0), use it. Else use mined.
        if ord_yield > 0:
            final_yield = ord_yield
        elif "yield_pct" in mined_data:
            final_yield = mined_data["yield_pct"]
            self.stats["mined_yield"] += 1

        if "typical" in record["yield"]:
            record["yield"]["typical"]["percent"] = final_yield

        # 5. CLASSIFICATION
        cls_data = self.classifier.classify(rxn_smiles)
        record["classification"]["primary_type"] = cls_data["primary_type"]
        record["classification"]["tags"] = cls_data["tags"]
        if cls_data["primary_type"] != "Unclassified": self.stats["classified"] += 1

        # 6. SAFETY (Skipped in this fast probe loop, use v2 if needed)

        return record, mined_data, cls_data

    def run(self, query):
        print(f"\n🧪 SEARCHING: '{query}'")
        print("-" * 60)
        results = self.ord.search_reactions(query, limit=5)
        print(f"   Found {len(results)} raw records. Processing...")

        self.stats = {"processed": 0, "mined_yield": 0, "mined_temp": 0, "classified": 0}

        for i, raw in enumerate(results):
            try:
                final, mined, cls = self.process(raw)

                # TERMINAL FEEDBACK
                rid = final["identity"]["id"][:8] + "..."
                y_val = final["yield"]["typical"]["percent"]
                t_val = final["conditions"]["temperature"]["value_k"]
                c_type = final["classification"]["primary_type"]

                # Formatting
                yield_src = "(Struct)"
                if "yield_pct" in mined and (y_val == mined["yield_pct"]): yield_src = "(Mined)"
                elif y_val == 0.0: yield_src = "(None)"

                temp_str = f"{t_val:.1f} K" if t_val else "--"
                temp_src = "(Mined)" if "temp_k" in mined else ""

                print(f"   [{i+1}] ID: {rid} | Type: {c_type}")
                print(f"       Yield: {y_val}% {yield_src}")
                print(f"       Temp : {temp_str} {temp_src}")

                # Save
                fname = f"enriched_{query.replace('/', '')}_{i}.json"
                with open(os.path.join(OUTPUT_DIR, fname), 'w') as f:
                    json.dump(final, f, indent=2)
                self.stats["processed"] += 1
            except Exception as e:
                logger.error(f"Error on {i}: {e}")
                print(f"   [{i+1}] ❌ Error: {e}")

        # SUMMARY
        print("-" * 60)
        print(f"✅ BATCH COMPLETE: {self.stats['processed']}/{len(results)} saved.")
        print(f"   Mined Yields: {self.stats['mined_yield']}")
        print(f"   Mined Temps:  {self.stats['mined_temp']}")
        print(f"   Classified:   {self.stats['classified']}")
        print("=" * 60)

if __name__ == "__main__":
    builder = EnrichedReactionBuilder()
    builder.run("OS(=O)(=O)O")
    builder.run("CC(=O)O")