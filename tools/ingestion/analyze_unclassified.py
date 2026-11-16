import os
import json
import logging
from collections import Counter
from rdkit import Chem
from rdkit.Chem import rdChemReactions
from tqdm import tqdm
from rdkit import RDLogger

RDLogger.DisableLog('rdApp.*')

INPUT_DIR = "./tools/data/reaction_dataset"
LOG_DIR = "./tools/logs"
REPORT_FILE = os.path.join(LOG_DIR, "unclassified_analysis.txt")

def get_reaction_core(rsmi):
    try:
        # Simple cleanup: remove solvents/salts to find the "Core" transformation
        r, p = rsmi.split(">>")
        def filter_trivial(s):
            mols = s.split(".")
            # Keep molecules with Carbon, exclude simple salts/solvents
            return sorted([m for m in mols if "C" in m and len(m) > 3])

        r_core = filter_trivial(r)
        p_core = filter_trivial(p)
        return ".".join(r_core) + ">>" + ".".join(p_core)
    except:
        return rsmi

def analyze_unclassified():
    print(f"🔍 Scanning {INPUT_DIR} for Unclassified reactions...")
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    unclassified_cores = []
    sample_map = {}

    for f in tqdm(files):
        try:
            with open(os.path.join(INPUT_DIR, f), 'r', encoding='utf-8') as handle:
                data = json.load(handle)

            if data.get("classification", {}).get("primary_type") != "Unclassified": continue

            rsmi = data.get("identity", {}).get("reaction_smiles")
            if not rsmi: continue

            core = get_reaction_core(rsmi)
            unclassified_cores.append(core)

            if core not in sample_map: sample_map[core] = []
            if len(sample_map[core]) < 3: sample_map[core].append(f)
        except: pass

    counts = Counter(unclassified_cores)
    print(f"\n📊 Found {len(unclassified_cores)} Unclassified Reactions.")

    lines = []
    lines.append("🧪 UNCLASSIFIED REACTION ANALYSIS")
    lines.append("========================================\n")

    for i, (core, count) in enumerate(counts.most_common(50)):
        pct = (count / len(unclassified_cores)) * 100
        header = f"#{i+1}: {count} occurrences ({pct:.1f}%)"
        lines.append(header)
        lines.append(f"Core: {core}")
        lines.append(f"Files: {', '.join(sample_map[core])}")
        lines.append("-" * 40)

    # FIX: Explicit UTF-8 encoding
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"\n📄 Full analysis saved to {REPORT_FILE}")

if __name__ == "__main__":
    analyze_unclassified()