import json
import os
import re
import logging
import copy
import sys
import argparse
from typing import Dict, Any, List

sys.path.append(os.path.abspath("."))
try:
    from ord_client import OrdClient
    from tools.ingestion.pubchem_client import PubChemClient
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit import RDLogger
except ImportError as e:
    sys.exit(1)

RDLogger.DisableLog('rdApp.*')

OUTPUT_DIR = "./tools/data/reaction_dataset"
LOG_DIR = "./tools/logs"
SCHEMA_PATH = "./tools/data/canon_reaction.json"
TEMPLATES_PATH = "./tools/data/reaction_templates.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("ReactionIngest")

# --- CLASSIFIER ---
class TemplateClassifier:
    def __init__(self, templates_path):
        self.library = []
        try:
            with open(templates_path, 'r') as f:
                raw_templates = json.load(f)

            print(f"📚 Loaded {len(raw_templates)} Templates.")
            for t in raw_templates:
                self.library.append({
                    "name": t["name"],
                    "type": t["type"],
                    "r_pats": [Chem.MolFromSmarts(s) for s in t["reactants"]],
                    "p_pats": [Chem.MolFromSmarts(s) for s in t["products"]]
                })
        except Exception as e:
            print(f"⚠️ Template Init Failed: {e}")

    def classify(self, reaction_smiles: str) -> Dict[str, Any]:
        if not reaction_smiles or ">>" not in reaction_smiles:
            return {"primary_type": "Unclassified", "tags": []}

        try:
            r_smi, p_smi = reaction_smiles.split(">>")
            r_mol = Chem.MolFromSmiles(r_smi)
            p_mol = Chem.MolFromSmiles(p_smi)
            if not r_mol or not p_mol: return {"primary_type": "Unclassified", "tags": []}

            for t in self.library:
                # 1. Reactant Check
                if not all(r_mol.HasSubstructMatch(pat) for pat in t["r_pats"]): continue
                # 2. Product Check
                if not all(p_mol.HasSubstructMatch(pat) for pat in t["p_pats"]): continue

                # 3. Transformation Check (Count Increase)
                for p_pat in t["p_pats"]:
                    r_count = len(r_mol.GetSubstructMatches(p_pat))
                    p_count = len(p_mol.GetSubstructMatches(p_pat))
                    if p_count > r_count or t["type"] in ["Deprotection", "Elimination", "Reduction"]:
                        return {"primary_type": t["type"], "tags": [t["name"]]}

        except: pass
        return {"primary_type": "Unclassified", "tags": []}

# --- TEXT MINER ---
class TextMiner:
    PATTERNS = {
        "time": re.compile(r"(\d+(?:\.\d+)?)\s*-?\s*(\d+(?:\.\d+)?)?\s*(?:h|hr|hours|min|minutes)", re.IGNORECASE),
        "temp_val": re.compile(r"(\d+(?:\.\d+)?)\s*(?:°|deg)?\s*C\b", re.IGNORECASE),
        "temp_kw": re.compile(r"\b(reflux|room temp|ambient)", re.IGNORECASE),
        "percent_val": re.compile(r"(\d+(?:\.\d+)?)\s*%", re.IGNORECASE)
    }
    YIELD_BLOCKLIST = ["acid", "solution", "containing", "purity", "ee", "volume", "weight", "oleum"]

    @staticmethod
    def extract(text):
        res = {}
        if not text: return res
        t = TextMiner.PATTERNS["temp_val"].search(text)
        if t: res["temp_k"] = float(t.group(1)) + 273.15
        else:
            kw = TextMiner.PATTERNS["temp_kw"].search(text)
            if kw and "room" in kw.group(0).lower(): res["temp_k"] = 298.15
            elif kw and "reflux" in kw.group(0).lower(): res["temp_k"] = 373.15

        tm = TextMiner.PATTERNS["time"].search(text)
        if tm:
            val = float(tm.group(1))
            res["time_s"] = val * 3600 if "h" in tm.group(0).lower() else val * 60

        candidates = []
        for match in TextMiner.PATTERNS["percent_val"].finditer(text):
            val = float(match.group(1))
            if not (0 < val <= 100): continue
            context = text[match.end():match.end()+15].lower()
            if any(b in context for b in TextMiner.YIELD_BLOCKLIST): continue
            dist = float('inf')
            for kw in ["yield", "obtain", "afford"]:
                idx = text.lower().find(kw)
                if idx != -1: dist = min(dist, abs(match.start() - idx))
            candidates.append((val, dist))
        if candidates:
            candidates.sort(key=lambda x: x[1])
            res["yield_pct"] = candidates[0][0]
        return res

# --- SAFETY ---
class SafetyAggregator:
    def __init__(self):
        self.pubchem = PubChemClient()
        self.cache = {}
    def get_ghs(self, smiles):
        if smiles in self.cache: return self.cache[smiles]
        try:
            cids = self.pubchem.fetch_cids(smiles, "smiles")
            if cids:
                h = self.pubchem.fetch_compound_context(cids[0]).get("hazard_statements", [])
                self.cache[smiles] = h
                return h
        except: pass
        self.cache[smiles] = []
        return []
    def assess(self, reactants):
        h = set()
        for r in reactants:
            if r.get("smiles"): h.update(self.get_ghs(r["smiles"]))
        sh = sorted(list(h))
        sum_txt = "Standard Safety"
        if any("Fatal" in x or "H330" in x for x in sh): sum_txt = "☠️ DANGER: Fatal components"
        elif any("Explosive" in x for x in sh): sum_txt = "⚠️ HIGH RISK: Explosive"
        elif any("H3" in x for x in sh): sum_txt = "Caution: Toxic/Irritant"
        return {"summary": sum_txt, "ghs_hazard_statements": sh, "primary_hazards": []}

# --- INGESTOR ---
class ReactionIngestor:
    def __init__(self):
        self.ord = OrdClient()
        self.classifier = TemplateClassifier(TEMPLATES_PATH)
        self.safety = SafetyAggregator()
        with open(SCHEMA_PATH, 'r') as f: self.schema = json.load(f)

    def process(self, raw):
        rec = copy.deepcopy(self.schema)
        rec["identity"]["id"] = raw.get("reactionId", "")

        r, p = [], []
        for k, v in raw.get("inputs", {}).items():
            for c in v.get("components", []):
                s = next((i["value"] for i in c["identifiers"] if i["type"] == "SMILES"), None)
                if s:
                    m = Chem.MolFromSmiles(s)
                    if m: m.UpdatePropertyCache(strict=False)
                    r.append({"substance_name": k, "smiles": s, "role": "REACTANT", "formula": AllChem.CalcMolFormula(m) if m else ""})

        oy = 0.0
        for out in raw.get("outcomes", []):
            if "yield_percent" in out: oy = out["yield_percent"]
            for prod in out.get("products", []):
                s = next((i["value"] for i in prod["identifiers"] if i["type"] == "SMILES"), None)
                if s:
                    m = Chem.MolFromSmiles(s)
                    if m: m.UpdatePropertyCache(strict=False)
                    p.append({"substance_name": "Product", "smiles": s, "role": "PRODUCT", "formula": AllChem.CalcMolFormula(m) if m else ""})

        rec["stoichiometry"]["reactants"] = r
        rec["stoichiometry"]["products"] = p
        rxn_smi = ".".join([x["smiles"] for x in r]) + ">>" + ".".join([x["smiles"] for x in p])
        rec["identity"]["reaction_smiles"] = rxn_smi

        mined = {}
        if "notes" in raw and "procedure" in raw["notes"]:
            proc = raw["notes"]["procedure"]
            rec["identity"]["description"] = f"Procedure: {proc}"
            mined = TextMiner.extract(proc)
            if "temp_k" in mined: rec["conditions"]["temperature"]["value_k"] = mined["temp_k"]
            if "time_s" in mined: rec["conditions"]["time"]["value_seconds"] = mined["time_s"]

        rec["yield"]["typical"]["percent"] = oy if oy > 0 else mined.get("yield_pct", 0.0)

        cls = self.classifier.classify(rxn_smi)
        rec["classification"]["primary_type"] = cls["primary_type"]
        rec["classification"]["tags"] = cls["tags"]

        if r:
            s = self.safety.assess(r)
            rec["safety"]["summary"] = s["summary"]
            rec["safety"]["ghs_hazard_statements"] = s["ghs_hazard_statements"]

        return rec, rxn_smi

    def run(self, queries, limit=5, debug=False):
        print(f"⚡ Ingesting {len(queries)} compounds...")
        for q in queries:
            print(f"\n🧪 Query: '{q}'")
            res = self.ord.search_reactions(q, limit)
            print(f"   Found {len(res)} records.")
            for i, raw in enumerate(res):
                try:
                    final, rsmi = self.process(raw)
                    fn = f"rxn_{q.replace('/', '_')}_{i}.json"

                    if debug and final['classification']['primary_type'] == "Unclassified":
                        print(f"   [DEBUG] Unclassified SMILES: {rsmi}")

                    print(f"   [{i+1}] {final['classification']['primary_type']:<15} | Yield: {final['yield']['typical']['percent']:>5.1f}% | {final['safety']['summary'][:30]}")
                    with open(os.path.join(OUTPUT_DIR, fn), 'w') as f: json.dump(final, f, indent=2)
                except Exception as e: print(f"   [{i+1}] ❌ Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("compounds", nargs="+")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--debug", action="store_true", help="Print unclassified reaction SMILES")
    args = parser.parse_args()
    ReactionIngestor().run(args.compounds, args.limit, args.debug)