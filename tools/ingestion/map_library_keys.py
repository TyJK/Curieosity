import json
import os
import re
from collections import defaultdict, Counter
from tqdm import tqdm

# --- CONFIGURATION ---
LIBRARY_DIR = "./tools/data/full_compounds_backup"
REPORT_FILE = "./tools/data/library_omniscient_audit.json"
MIN_KEY_THRESHOLD = 1  # Strict filter: Keys must appear in at least 5 files to show up

# --- OVERKILL DEFINITIONS ---
CONCEPTS = {
    # --- IDENTITY ---
    "Identity: CAS": { "existing": ["identity.cas_rn"], "raw_regex": [r"cas.?number", r"cas.?rn", r"cas.?no"], "derivable": [] },
    "Identity: SMILES": { "existing": ["identity.smiles"], "raw_regex": [r"canonical.?smiles", r"^smiles$", r"isomeric.?smiles"], "derivable": [] },
    "Identity: Formula": { "existing": ["identity.formula"], "raw_regex": [r"chemical.?formula", r"^formula$"], "derivable": ["identity.smiles"] },
    "Identity: InChI": { "existing": ["identity.inchi_key"], "raw_regex": [r"^inchi$", r"inchi.?key"], "derivable": ["identity.smiles"] },

    # --- PHYSICS ---
    "Physics: Mass": { "existing": ["game_data.physics.mass"], "raw_regex": [r"molar.?mass", r"molecular.?weight", r"formula.?weight", r"formula.?mass"], "derivable": ["identity.smiles"] },
    "Physics: Density": { "existing": ["game_data.physics.density_g_cm3"], "raw_regex": [r"density", r"specific.?gravity"], "derivable": [] },
    "Physics: Melting Point": { "existing": ["game_data.physics.melting_point_k"], "raw_regex": [r"melting.?point", r"m\.?p\.?"], "derivable": [] },
    "Physics: Boiling Point": { "existing": ["game_data.physics.boiling_point_k"], "raw_regex": [r"boiling.?point", r"b\.?p\.?"], "derivable": [] },
    "Physics: Solubility": { "existing": ["game_data.physics.solubility"], "raw_regex": [r"solubility", r"water.?solubility"], "derivable": [] },
    "Physics: Appearance": { "existing": ["game_data.description"], "raw_regex": [r"appearance", r"physical.?description", r"color", r"form", r"odour", r"^description$"], "derivable": [] },
    "Physics: State": { "existing": ["game_data.physics.standard_state"], "raw_regex": [r"phase", r"state.?of.?matter"], "derivable": ["game_data.physics.melting_point_k"] },
    "Physics: Refractive Index": { "existing": ["game_data.physics.refractive_index"], "raw_regex": [r"refractive.?index"], "derivable": [] },

    # --- VISUALS & MEDIA ---
    "Media: 2D Image": {
        "existing": ["media.images", "game_data.visuals.image"],
        "raw_regex": [r"image", r"structure.2d", r"depiction"],
        "derivable": ["identity.smiles"]
    },
    "Media: 3D Model": {
        "existing": ["game_data.visuals.model_data_sdf", "identity.pubchem_3d_conformer", "game_data.visuals.has_3d_model"],
        "raw_regex": [r"3d.conformer", r"model.3d", r"sdf", r"coordinates"],
        "derivable": ["identity.smiles"]
    },
    "Media: Spectra": { "existing": [], "raw_regex": [r"spectrum", r"nmr", r"ir", r"uv", r"mass.spec"], "derivable": [] },

    # --- CHEMISTRY ---
    "Chem: Complexity": { "existing": ["game_data.physics.complexity_score"], "raw_regex": [r"complexity"], "derivable": ["identity.smiles"] },
    "Chem: Charge": { "existing": ["game_data.physics.charge"], "raw_regex": [r"formal.?charge", r"^charge$"], "derivable": ["identity.smiles"] },
    "Chem: TPSA": { "existing": ["game_data.physics.tpsa"], "raw_regex": [r"tpsa", r"topological.?polar"], "derivable": ["identity.smiles"] },
    "Chem: H-Bonds": { "existing": ["game_data.physics.h_bond_donor_count"], "raw_regex": [r"hydrogen.?bond"], "derivable": ["identity.smiles"] },

    # --- MEDICAL ---
    "Med: Toxicity": { "existing": ["game_data.safety"], "raw_regex": [r"toxicity", r"ld50", r"safety", r"lethal.?dose", r"hazardous", r"toxicology"], "derivable": [] },
    "Med: Mechanism": { "existing": ["context.mechanism_of_action"], "raw_regex": [r"mechanism.?of.?action", r"pharmacodynamics"], "derivable": [] },
    "Med: Indications": { "existing": ["game_data.roles"], "raw_regex": [r"indication", r"usage", r"therapeutic.?uses"], "derivable": [] },
    "Med: Metabolism": { "existing": [], "raw_regex": [r"metabolism", r"bioavailability", r"half.?life", r"excretion", r"clearance", r"protein.?binding"], "derivable": [] },
    "Med: ATC Code": { "existing": [], "raw_regex": [r"atc.?code"], "derivable": [] },

    # --- METADATA & CONTEXT ---
    "Meta: Provenance": { "existing": ["meta.provenance"], "raw_regex": [], "derivable": [] },
    "Meta: Ext. Links": { "existing": ["additional_context.external_links"], "raw_regex": [r"links", r"external"], "derivable": [] },
    "Meta: Discovery": { "existing": ["discovery.year", "discovery.discoverer"], "raw_regex": [r"discovery", r"first.isolat"], "derivable": [] },
    "Context: Patents": { "existing": ["context.patents", "context.legal.surechembl_ids"], "raw_regex": [r"patent"], "derivable": [] },
    "Context: History": { "existing": ["context.history"], "raw_regex": [r"history"], "derivable": [] },

    # --- INDUSTRIAL/ECONOMY ---
    "Econ: Price": { "existing": ["game_data.economy.market_prices"], "raw_regex": [r"cost", r"price"], "derivable": [] },
    "Econ: Production": { "existing": ["game_data.industrial.production_volume_lbs"], "raw_regex": [r"production.?volume"], "derivable": [] },
    "Ind: Uses/Roles": { "existing": ["context_lists.industrial_uses", "context_lists.consumer_uses", "game_data.roles"], "raw_regex": [r"industrial.?uses", r"consumer.?uses", r"applications", r"^uses$"], "derivable": [] },
    "Legal: UN Number": { "existing": [], "raw_regex": [r"un.?number"], "derivable": [] },
    "Legal: GHS": { "existing": ["context_lists.hazard_statements"], "raw_regex": [r"ghs", r"signal.?word", r"hazard.?statements"], "derivable": [] }
}

def flatten_json(y):
    """Flattens JSON to dot-notation paths, RECURSING into lists."""
    out = {}
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x: flatten(x[a], name + a + '.')
        elif type(x) is list:
            if len(x) > 0:
                out[name[:-1]] = x # Count the list itself
                # Peek into the first item if it's a dict to map structure
                if isinstance(x[0], dict):
                    # Use '[]' to denote list items in the key path
                    flatten(x[0], name[:-1] + '[]' + '.')
        elif x not in [None, ""]:
            out[name[:-1]] = x
    flatten(y)
    return out

def get_nested(root, path):
    parts = path.split('.')
    curr = root
    for p in parts:
        if isinstance(curr, dict) and p in curr: curr = curr[p]
        else: return None
    return curr

def has_value(val):
    if val is None: return False
    if isinstance(val, str): return len(val.strip()) > 0 and val.lower() != "unknown"
    if isinstance(val, (int, float)): return True
    if isinstance(val, list): return len(val) > 0
    return False

def scan_raw(raw_dict, regex_list):
    """Returns list of ALL matching keys in the dict."""
    matches = []
    if not raw_dict: return matches
    for k, v in raw_dict.items():
        if not has_value(v): continue
        for r in regex_list:
            if re.search(r, k, re.IGNORECASE):
                matches.append(k)
                break
    return matches

def analyze():
    if not os.path.exists(LIBRARY_DIR):
        print(f"Error: {LIBRARY_DIR} missing.")
        return

    files = [f for f in os.listdir(LIBRARY_DIR) if f.endswith(".json")]
    total_files = len(files)
    print(f"🔬 Auditing & Analyzing {total_files} files (Threshold: {MIN_KEY_THRESHOLD})...")

    # 1. Concept Stats
    concept_stats = defaultdict(lambda: {
        "Processed": 0, "Raw": 0, "Derivable": 0, "Total Potential": 0,
        "Matched_Keys": Counter()
    })

    # 2. Census Stats (Raw Key Counts)
    key_census = Counter()

    for filename in tqdm(files):
        try:
            with open(os.path.join(LIBRARY_DIR, filename), 'r') as f:
                data = json.load(f)

            # --- PART A: FULL KEY CENSUS ---
            flat = flatten_json(data)
            for k in flat: key_census[k] += 1

            # --- PART B: CONCEPT ANALYSIS ---
            comp = data.get("compound", {})

            raw_pools = {
                "Wiki": comp.get("additional_context", {}).get("wikipedia_raw", {}),
                "Legacy": comp.get("properties_raw", {}),
                "PubChem": comp.get("identity", {}).get("pubchem_context", {}).get("experimental_properties", {}),
            }

            for concept, rules in CONCEPTS.items():
                found_proc = False
                found_raw = False
                found_der = False

                # 1. Check Processed
                for path in rules["existing"]:
                    if has_value(get_nested(comp, path)):
                        found_proc = True
                        break

                # 2. Check Raw
                matched_keys = []
                for pool_name, pool in raw_pools.items():
                    matches = scan_raw(pool, rules["raw_regex"])
                    for m in matches:
                        matched_keys.append(f"{pool_name}.{m}")

                if matched_keys: found_raw = True

                # 3. Check Derivable
                if not found_proc and not found_raw:
                    for path in rules["derivable"]:
                        if has_value(get_nested(comp, path)):
                            found_der = True
                            break

                # Update Stats
                if found_proc: concept_stats[concept]["Processed"] += 1
                elif found_raw: concept_stats[concept]["Raw"] += 1
                elif found_der: concept_stats[concept]["Derivable"] += 1

                if found_proc or found_raw or found_der:
                    concept_stats[concept]["Total Potential"] += 1

                for k in matched_keys:
                    concept_stats[concept]["Matched_Keys"][k] += 1

        except Exception as e:
            pass

    # --- REPORT GENERATION ---
    print("\n" + "="*140)
    print(f"{'CONCEPT':<25} | {'CURR':<6} | {'RAW':<6} | {'CALC':<6} | {'TOTAL':<6} | {'TOP RAW KEY'}")
    print("-" * 140)

    for concept in sorted(CONCEPTS.keys()):
        if concept not in concept_stats: continue
        s = concept_stats[concept]
        curr = (s["Processed"]/total_files)*100
        raw = (s["Raw"]/total_files)*100
        calc = (s["Derivable"]/total_files)*100
        tot = (s["Total Potential"]/total_files)*100

        top_key = s["Matched_Keys"].most_common(1)
        top_key_str = top_key[0][0] if top_key else "-"
        if len(top_key_str) > 45: top_key_str = top_key_str[:42] + "..."

        print(f"{concept:<25} | {curr:>5.1f}% | {raw:>5.1f}% | {calc:>5.1f}% | {tot:>5.1f}% | {top_key_str}")

    # --- SAVE COMPLETE JSON ---
    final_output = {
        "meta": {
            "total_files": total_files,
            "threshold": MIN_KEY_THRESHOLD
        },
        "concepts": {},
        "full_key_census": {}
    }

    # 1. Clean up Concept Stats (Applying Filter)
    for k, v in concept_stats.items():
        # FILTER CONTRIBUTING KEYS
        filtered_contrib = {
            ck: cv for ck, cv in v["Matched_Keys"].items()
            if cv >= MIN_KEY_THRESHOLD
        }

        final_output["concepts"][k] = {
            "stats": {x: v[x] for x in ["Processed", "Raw", "Derivable", "Total Potential"]},
            "contributing_raw_keys": filtered_contrib
        }

    # 2. Filter Census
    for k, v in key_census.items():
        if v >= MIN_KEY_THRESHOLD:
            final_output["full_key_census"][k] = v

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, 'w') as f:
        json.dump(final_output, f, indent=2)

    print(f"\n✅ Omniscient Audit saved to: {REPORT_FILE}")
    print(f"   - Contains {len(final_output['full_key_census'])} unique JSON paths (> {MIN_KEY_THRESHOLD} occurrences)")

if __name__ == "__main__":
    analyze()