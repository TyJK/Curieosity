import os
import json
import csv
import logging
import statistics
import sys
from collections import defaultdict, Counter
from tqdm import tqdm
from rdkit import Chem

# --- CONFIGURATION ---
INPUT_DIR = "./tools/data/reaction_dataset"
OUTPUT_DIR = "./tools/data/00_canon_reactions"
MAP_FILE = "./tools/data/reaction_map.csv"
SCHEMA_PATH = "./tools/data/canon_reaction.json"

# Strict Quality Controls
DROP_BAD_YIELDS = True
MAX_VALID_YIELD = 102.0 # Allow slight experimental error, kill anything absurd
MIN_VALID_YIELD = 0.01

os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger("Condenser")

def get_robust_hash(data):
    """
    Generates a chemically invariant hash to grouping 'A.B>>C' and 'B.A>>C' together.
    Removes atom maps to ensure identical molecules match.
    """
    raw_smi = data.get("identity", {}).get("reaction_smiles", "")
    if not raw_smi or ">>" not in raw_smi: return None

    try:
        # Fast string manipulation first (99% of cases)
        # If it's already canonical, splitting and sorting is enough
        r, p = raw_smi.split(">>")
        r_parts = sorted(r.split("."))
        p_parts = sorted(p.split("."))
        return ".".join(r_parts) + ">>" + ".".join(p_parts)
    except:
        return raw_smi

# --- PHASE 1: MAP ---
def map_dataset():
    print("🗺️  PHASE 1: Mapping & Pre-Filtering...")
    if not os.path.exists(INPUT_DIR): return False

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]

    valid_count = 0
    dropped_yield = 0

    with open(MAP_FILE, 'w', newline='', encoding='utf-8') as out:
        writer = csv.writer(out)
        writer.writerow(["hash", "filename"])

        for f in tqdm(files, desc="Indexing"):
            try:
                with open(os.path.join(INPUT_DIR, f), 'r', encoding='utf-8') as h:
                    data = json.load(h)

                # 1. Quality Check: Yield
                if DROP_BAD_YIELDS:
                    y = data.get("yield", {}).get("typical", {}).get("percent", 0)
                    # If yield exists but is absurd, DROP the file entirely from the map
                    if y > MAX_VALID_YIELD:
                        dropped_yield += 1
                        continue

                # 2. Hash Generation
                r_hash = get_robust_hash(data)
                if r_hash:
                    writer.writerow([r_hash, f])
                    valid_count += 1
            except: pass

    print(f"✅ Map created: {MAP_FILE}")
    print(f"   Indexed: {valid_count}")
    print(f"   Dropped (Bad Yields): {dropped_yield}")
    return True

# --- PHASE 2: REDUCE ---
def merge_records(filenames, canon_template):
    """Merges N raw records into 1 Canon Record."""
    merged = canon_template.copy()

    yields = []
    temps = []
    times = []
    safety_codes = set()
    safety_summaries = Counter()
    ord_ids = []
    class_types = Counter()

    # Track source reliability
    best_record = None
    best_score = -1

    for fname in filenames:
        try:
            with open(os.path.join(INPUT_DIR, fname), 'r', encoding='utf-8') as f:
                rec = json.load(f)

            # Score record quality to pick the "Face" of the reaction
            # Points for: Classified, High Info Density, Valid Yield
            score = 0
            if rec.get("classification", {}).get("primary_type") != "Unclassified": score += 10
            if rec.get("yield", {}).get("typical", {}).get("percent", 0) > 0: score += 5
            if rec.get("conditions", {}).get("temperature", {}).get("value_k"): score += 2

            if score > best_score:
                best_score = score
                best_record = rec

            # --- AGGREGATION ---

            # IDs
            rid = rec.get("identity", {}).get("id")
            if rid: ord_ids.append(rid)

            # Yield (Safe Zone Filter applied again just in case)
            y = rec.get("yield", {}).get("typical", {}).get("percent", 0)
            if MIN_VALID_YIELD < y <= MAX_VALID_YIELD: yields.append(y)

            # Conditions
            t = rec.get("conditions", {}).get("temperature", {}).get("value_k")
            if t: temps.append(t)

            tm = rec.get("conditions", {}).get("time", {}).get("value_seconds")
            if tm: times.append(tm)

            # Classification
            c_type = rec.get("classification", {}).get("primary_type")
            if c_type and c_type != "Unclassified": class_types[c_type] += 1

            # Safety
            s = rec.get("safety", {})
            for code in s.get("ghs_hazard_statements", []):
                safety_codes.add(code)
            if s.get("summary"): safety_summaries[s["summary"]] += 1

        except: pass

    if not best_record: return None

    # --- POPULATE CANON ---
    # Use the highest quality record as the base
    merged["identity"] = best_record["identity"]
    merged["stoichiometry"] = best_record["stoichiometry"]

    # 2. Cross Refs
    merged["cross_references"]["internal_refs"]["related_reaction_ids"] = ord_ids
    # Generate deterministic ID based on the cleaned hash
    # Note: We use the hash of the SMILES to keep filenames consistent across runs
    clean_hash = get_robust_hash(best_record)
    merged["identity"]["id"] = f"rxn-{abs(hash(clean_hash))}"
    merged["identity"]["is_canon"] = True

    # 3. Yield Statistics (Median is safer for outliers)
    if yields:
        merged["yield"]["typical"]["percent"] = round(statistics.median(yields), 2)
        merged["yield"]["optimal"]["percent"] = max(yields)
        merged["yield"]["typical"]["description"] = f"Median of {len(yields)} sources."

    # 4. Conditions (Averages)
    if temps:
        avg_temp = statistics.mean(temps)
        merged["conditions"]["temperature"]["value_k"] = round(avg_temp, 1)

    if times:
        merged["conditions"]["time"]["value_seconds"] = round(statistics.mean(times), 0)

    # 5. Classification (Democracy)
    if class_types:
        # If we have conflicting classifications, pick the most common one
        # Exception: "Unclassified" never wins if *any* valid class exists (handled by logic above)
        best_class = class_types.most_common(1)[0][0]
        merged["classification"]["primary_type"] = best_class
        # Attempt to recover tags from a record that matched this class
        if best_record.get("classification", {}).get("primary_type") == best_class:
            merged["classification"]["tags"] = best_record["classification"]["tags"]

    # 6. Safety (Aggregate Worst Case)
    # If any source flagged DANGER, we keep DANGER.
    severe = [k for k in safety_summaries.keys() if "DANGER" in k or "Fatal" in k or "Explosive" in k]
    if severe:
        merged["safety"]["summary"] = severe[0]
    elif safety_summaries:
        merged["safety"]["summary"] = safety_summaries.most_common(1)[0][0]

    merged["safety"]["ghs_hazard_statements"] = sorted(list(safety_codes))

    return merged

def reduce_dataset():
    print("\n🏭 PHASE 2: Reducing (Stacking & Refining)...")

    try:
        with open(SCHEMA_PATH, 'r') as f:
            template = json.load(f)
    except:
        print("❌ Schema missing!")
        return

    groups = defaultdict(list)
    with open(MAP_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) == 2:
                groups[row[0]].append(row[1])

    print(f"📊 Processing {len(groups)} unique reaction clusters...")

    count = 0
    for r_hash, files in tqdm(groups.items(), desc="Synthesizing"):
        canon_record = merge_records(files, template)

        if canon_record:
            fname = f"{canon_record['identity']['id']}.json"
            with open(os.path.join(OUTPUT_DIR, fname), 'w') as f:
                json.dump(canon_record, f, indent=2)
            count += 1

    print(f"\n✅ Cleaned Dataset Generated: {count} Canon Reactions.")
    print(f"📁 Location: {OUTPUT_DIR}")

if __name__ == "__main__":
    if map_dataset():
        reduce_dataset()