#!/usr/bin/env python3
"""
Curieosity reaction resolver  (pipeline stage 2)
================================================
Connects the compound set to the reaction corpus: turns raw scraped reactions into
game `Reaction` records keyed on the SAME substance-id registry that compile_data.py
produced, and emits reactions.ron.

Core idea
---------
A reaction is "gameable" when EVERY real species (reactants AND products, minus spectator
ions) is a substance the game knows about. We:
  1. canonicalize every species' SMILES (RDKit, isomericSmiles=False -- matches the scrape)
  2. resolve each to a substance id via the compound index
  3. drop `agents` (solvents/reagents/catalysts) and spectator counterions
  4. keep reactions ONLY when ALL reactants AND ALL products map -- "closed on both sides".
     This is the correctness fix: previously a reaction was kept if just >=1 reactant
     mapped, so a real "BigA + BigB + H2 -> P" (only H2 known) was PROJECTED down to the
     false recipe "H2 -> P", and many such projections then collapsed onto the same coarse
     key. Requiring full closure means the reactant set the game sees is the REAL set.
  5. assign a *player* ProcessType from the reaction's mechanism class (editable table)
  6. compute dH from compound formation enthalpies when available; record temperature as a
     Condition so it survives into the game data
  7. key on the engine's RecipeKey = (process, {full reactant ids}). Because the reactant
     set is now complete, this key is specific: genuine collisions are rare and mean "same
     reactants, same process, different reported outcome" -> keep the best (yield, then id).

To make closure-on-both-sides actually keep a rich library (rather than dropping almost
everything for unknown reactants), run with --discover-species: recurrent unknown species
on EITHER side are minted as new substances first. This is now safe because the in-game
inventory is discovery-gated -- a large substance table no longer floods the UI.

Input formats handled
---------------------
  * flat/condensed  : {reactants:[smi], agents:[smi], products:[smi], id, source}
  * rich ORD schema : {identity:{reaction_smiles, id}, stoichiometry:{reactants:[{smiles}],
                       products:[{smiles}]}, classification:{primary_type}, conditions:{...},
                       yield:{typical:{percent}}}

Run (real):
    python3 resolve_reactions.py \
        --compounds ./tools/data/18_final_canon \
        --reactions ./tools/data/reaction_dataset \
        --seed-substances assets/data/substances.ron \
        --out assets/data

Run (mechanics demo, universe harvested from the reactions themselves):
    python3 resolve_reactions.py --demo existing2/master_reactions.json --out out
"""

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, Descriptors
from rdkit import RDLogger

RDLogger.DisableLog("rdApp.*")

# structural acid/base detection for minted compounds (mirrors compile_data.py)
_ACID_SMARTS = [Chem.MolFromSmarts(s) for s in (
    "[CX3](=O)[OX2H1]", "[SX4](=O)(=O)[OX2H1]", "[PX4](=O)[OX2H1]")]
_BASE_SMARTS = [Chem.MolFromSmarts(s) for s in (
    "[NX3;!$(NC=O);!$(N=*);!$(N#*);!$([N+])]", "[nX2]", "[NX3]=[CX3][NX3]")]


def _discovered_props(m):
    props = []
    if any(m.HasSubstructMatch(p) for p in _ACID_SMARTS if p is not None):
        props.append("IsAcid")
    if any(m.HasSubstructMatch(p) for p in _BASE_SMARTS if p is not None):
        props.append("IsBase")
    return props

try:
    from tqdm import tqdm
except ImportError:  # graceful fallback: identity wrapper
    def tqdm(it, **kw):
        return it

SCRAPED_ID_BASE = 1000
DISCOVER_ID_BASE = 100000   # auto-minted "discovered" products live above the curated block
MAX_VALID_YIELD = 102.0

# --- mechanism class -> PLAYER process (the key design table; edit freely) ---------
# The game's ProcessType is what the *player applies*, not the reaction mechanism.
# This is the deliberate, lossy bridge between the two. Temperature overrides below.
PROCESS_MAP = {
    "Oxidation": "Heat",
    "Reduction": "Mix",
    "Condensation": "Heat",
    "Acylation": "Mix",
    "Alkylation": "Mix",
    "Elimination": "Heat",
    "Cyclization": "Heat",
    "Deprotection": "Mix",
    "C-C Coupling": "Catalysis",
    "Electrophilic Substitution": "Mix",
    "Substitution": "Mix",
    "Hydrolysis": "Mix",
    "Neutralization": "Mix",
    "Unclassified": "Mix",
    "": "Mix",
}
# temperature bands (K) -> which *tier* of thermal process the player applies.
# ORD procedure temps top out around bench reflux, so Smelting/plasma effectively never
# fire from the scrape -- they belong to the curated inorganic/industrial pack.
COOL_MAX_K = 275.0        # ice bath / dry ice / cryo
HEAT_THRESHOLD_K = 350.0  # above room temp -> Heat
SMELTING_MIN_K = 1000.0   # arc-furnace / metallurgy tier

# procedure-text signals for the *distinct* (non-thermal) processes. Kept specific on
# purpose -- generic words like "catalyst" or "distill" are too noisy (workup steps).
# Edit these freely; they're the second half of the mechanism->process bridge.
ELECTROLYSIS_KW = ("electroly", "electrochemical", " anode", " cathode", "galvanic")
PHOTO_KW = ("irradiat", "photochem", "photolys", "uv light", "ultraviolet", "under uv", "hνc")
POLYMER_KW = ("polymeriz", "polymerisation", "polymerization")
CATALYSIS_KW = ("hydrogenat", "pd/c", "pd-c", "pd/al", "palladium", "raney",
                "platinum", "pt/c", "pto2", "wilkinson", "under h2", "h2 (", "hydrogen atmosphere")

# spectator ions / counterions that should never count as reactants or products
_SPECTATOR_RAW = [
    "[Na+]", "[K+]", "[Li+]", "[Cl-]", "[Br-]", "[I-]", "[F-]", "[OH-]", "[H+]",
    "[Mg+2]", "[Ca+2]", "[NH4+]", "[H-]", "[Al+3]", "[Na]", "[K]", "[Li]",
]


_CANON_CACHE = {}


def canon(smiles):
    if not smiles:
        return None
    if smiles in _CANON_CACHE:            # solvents/reagents repeat 100k+ times; cache pays off
        return _CANON_CACHE[smiles]
    result = None
    try:
        m = Chem.MolFromSmiles(smiles)
        if m:
            result = Chem.MolToSmiles(m, canonical=True, isomericSmiles=False)
    except Exception:
        pass
    _CANON_CACHE[smiles] = result
    return result


SPECTATORS = {c for c in (canon(s) for s in _SPECTATOR_RAW) if c}


def is_spectator(cs):
    if cs is None:
        return True
    if cs in SPECTATORS:
        return True
    m = Chem.MolFromSmiles(cs)
    if m is None:
        return True
    # single-atom ionic fragment (bare counterion)
    if m.GetNumHeavyAtoms() <= 1 and any(a.GetFormalCharge() != 0 for a in m.GetAtoms()):
        return True
    return False


# --- input adapters ----------------------------------------------------------------
def normalize(record):
    """-> dict(reactants=[canon], agents=[canon], products=[canon], meta=...)."""
    if "stoichiometry" in record:  # rich ORD schema
        st = record["stoichiometry"]
        reactants = [c.get("smiles") for c in st.get("reactants", [])]
        products = [c.get("smiles") for c in st.get("products", [])]
        cats = [c.get("smiles") for c in st.get("catalysts", []) if c.get("smiles")]
        agents = cats + [c.get("smiles") for c in st.get("solvents", [])] + \
                 [c.get("smiles") for c in st.get("reagents", [])]
        prim = record.get("classification", {}).get("primary_type", "")
        cond = record.get("conditions", {})
        temp = (cond.get("temperature", {}) or {}).get("value_k")
        y = (record.get("yield", {}).get("typical", {}) or {}).get("percent", 0.0)
        rid = record.get("identity", {}).get("id", "")
        text = record.get("identity", {}).get("description", "") or ""
        electro = bool((cond.get("electrochemical", {}) or {}).get("required"))
        photo = bool((cond.get("irradiation", {}) or {}).get("required"))
        has_cat = len(cats) > 0
    else:  # flat/condensed schema
        reactants = record.get("reactants", [])
        products = record.get("products", [])
        agents = record.get("agents", [])
        prim = record.get("primary_type", "")
        temp = record.get("temperature_k")
        y = record.get("yield_percent", 0.0)
        rid = record.get("id", "")
        text = record.get("description", "") or ""
        electro = photo = has_cat = False
    return {
        "reactants": [canon(s) for s in reactants],
        "agents": [canon(s) for s in agents],
        "products": [canon(s) for s in products],
        "primary_type": prim, "temp_k": temp, "yield": y or 0.0, "rid": rid,
        "text": text.lower(), "electro": electro, "photo": photo, "has_cat": has_cat,
    }


def pick_process(norm):
    """The mechanism->player-process bridge. Priority: distinct energy-input processes
    (from structured flags or specific procedure-text keywords) first, then thermal tier
    from temperature, then the mechanism-class fallback."""
    text = norm["text"]

    def has(words):
        return any(w in text for w in words)

    # 1) distinct, non-thermal processes -- strong structured signal or specific keyword
    if norm["electro"] or has(ELECTROLYSIS_KW):
        return "Electrolysis"
    if norm["photo"] or has(PHOTO_KW):
        return "Irradiate"
    if has(POLYMER_KW):
        return "Polymerize"
    if norm["has_cat"] or has(CATALYSIS_KW):
        return "Catalysis"

    # 2) thermal tier from recorded temperature
    t = norm["temp_k"]
    if t is not None:
        if t <= COOL_MAX_K:
            return "Cool"
        if t >= SMELTING_MIN_K:
            return "Smelting"
        if t >= HEAT_THRESHOLD_K:
            return "Heat"
        return "Mix"

    # 3) no temperature recorded -> fall back to the mechanism-class table
    return PROCESS_MAP.get(norm["primary_type"], "Mix")


# --- resolution --------------------------------------------------------------------
def resolve(records, index, hf_by_id=None):
    hf_by_id = hf_by_id or {}
    stats = Counter()
    by_key = {}          # RecipeKey -> (game_reaction, yield)
    process_hist = Counter()

    for rec in records:
        stats["total"] += 1
        n = normalize(rec)
        if n["yield"] and n["yield"] > MAX_VALID_YIELD:
            stats["dropped_bad_yield"] += 1
            continue

        # PRODUCTS: every non-spectator product must map (closed).
        prod_ids, prod_ok = [], True
        for cs in n["products"]:
            if cs is None or is_spectator(cs):
                continue
            sid = index.get(cs)
            if sid is None:
                prod_ok = False        # a real product we don't know -> not closed
                break
            prod_ids.append(sid)
        if not prod_ok or not prod_ids:
            stats["dropped_open_products"] += 1
            continue

        # REACTANTS: every non-spectator reactant must ALSO map now (closed on both sides).
        # This is the fix: no more silent projection onto whatever few reactants happened
        # to be known.
        react_ids, react_ok = [], True
        for cs in n["reactants"]:
            if cs is None or is_spectator(cs):
                continue
            sid = index.get(cs)
            if sid is None:
                react_ok = False       # a real reactant we don't know -> not closed
                break
            react_ids.append(sid)
        if not react_ok:
            stats["dropped_open_reactants"] += 1
            continue
        if not react_ids:
            stats["dropped_no_mapped_reactants"] += 1
            continue

        process = pick_process(n)
        react_set = frozenset(react_ids)
        prod_set = sorted(set(prod_ids))

        # Drop reactions with no NET product (everything produced was already a reactant).
        # These are pointless as recipes -- you'd get back only what you put in.
        if set(prod_set) <= react_set:
            stats["dropped_no_net_product"] += 1
            continue

        key = (process, react_set)

        # dH from formation enthalpies, if we have them for every species
        dH = 0.0
        rp = list(react_set) + prod_set
        if hf_by_id and all(hf_by_id.get(i) is not None for i in rp):
            dH = round(sum(hf_by_id[i] for i in prod_set) - sum(hf_by_id[i] for i in react_set), 1)

        game_rxn = {
            "reactants": sorted(react_set), "products": prod_set,
            "process": process, "dH": dH, "yield": n["yield"], "rid": n["rid"],
            "temp_k": n["temp_k"],
        }

        prev = by_key.get(key)
        if prev is None:
            by_key[key] = game_rxn
            stats["kept_unique"] += 1
            process_hist[process] += 1
        else:
            stats["collisions"] += 1
            # Deterministic best-pick: higher yield wins; tie -> lower raw id (stable).
            better = (game_rxn["yield"] > prev["yield"] or
                      (game_rxn["yield"] == prev["yield"] and
                       str(game_rxn["rid"]) < str(prev["rid"])))
            if better:
                by_key[key] = game_rxn

    return by_key, stats, process_hist


# --- compound index ----------------------------------------------------------------
def list_dir(path, what):
    """List .json files (fine for the ~7k compound dir)."""
    p = Path(path) if path else None
    if not p or not p.exists():
        raise SystemExit(f"ERROR: {what} directory not found: {path}")
    files = list(p.glob("*.json"))
    if not files:
        raise SystemExit(f"ERROR: {what} directory has no .json files: {path}")
    return files


def validate_dir(path, what):
    """Cheap existence + peek check WITHOUT enumerating the whole folder
    (the reaction dir can hold 500k+ files; a full glob there is the 'hang')."""
    p = Path(path) if path else None
    if not p or not p.exists():
        raise SystemExit(f"ERROR: {what} directory not found: {path}")
    with os.scandir(p) as it:
        for entry in it:
            if entry.name.endswith(".json"):
                return  # found at least one; good enough
    raise SystemExit(f"ERROR: {what} directory has no .json files: {path}")


def iter_reaction_dir(path):
    """Stream reactions one file at a time via scandir (starts immediately, low memory)."""
    with os.scandir(path) as it:
        for entry in it:
            if not entry.name.endswith(".json"):
                continue
            try:
                with open(entry.path, "r", encoding="utf-8") as fh:
                    yield json.load(fh)
            except Exception:
                continue


def build_index_from_compounds(compound_files):
    index, hf = {}, {}
    nid = SCRAPED_ID_BASE
    for f in tqdm(sorted(compound_files), desc="indexing compounds", unit="cmpd"):
        doc = json.loads(f.read_text(encoding="utf-8"))
        ident = doc.get("identity", {})
        cs = canon(ident.get("smiles"))
        if not cs or cs in index:
            continue
        index[cs] = nid
        thermo = doc.get("properties", {}).get("thermodynamics", {})
        v = thermo.get("enthalpy_formation_kj_mol")
        if isinstance(v, dict):
            v = v.get("value_kj_mol")
        hf[nid] = v
        nid += 1
    return index, hf


def discover_products(reactions_dir, base_index, min_occ):
    """Pass 1 of discovery mode: count unknown SMILES on BOTH sides (reactants and
    products), then mint the ones seen >= min_occ times as new lightweight substances
    (formula only). Minting reactants too is what lets closure-on-both-sides keep a rich
    library instead of dropping every reaction with an unfamiliar reactant."""
    counts = Counter()
    for rec in tqdm(iter_reaction_dir(reactions_dir), desc="scanning species", unit="rxn"):
        n = normalize(rec)
        for cs in n["reactants"] + n["products"]:
            if cs and cs not in base_index and not is_spectator(cs):
                counts[cs] += 1
    discovered, meta = {}, {}
    nid = DISCOVER_ID_BASE
    for cs, c in counts.items():
        if c >= min_occ:
            discovered[cs] = nid
            m = Chem.MolFromSmiles(cs)
            if m is not None:
                meta[nid] = {
                    "smiles": cs,
                    "formula": rdMolDescriptors.CalcMolFormula(m),
                    "mw": round(Descriptors.MolWt(m), 3),
                    "logp": round(Descriptors.MolLogP(m), 3),
                    "props": _discovered_props(m),
                }
            else:
                meta[nid] = {"smiles": cs, "formula": "?", "mw": 0.0, "logp": None, "props": []}
            nid += 1
    print(f"  {len(counts):,} distinct unknown species; "
          f"{len(discovered):,} recur >= {min_occ}x (minted with formula/mass/logP)", flush=True)
    return discovered, meta


def _ron_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _discovered_entry(cs, sid, meta):
    md = meta.get(sid, {})
    name = cs if len(cs) <= 40 else cs[:37] + "..."
    mw = md.get("mw") or 0.0
    logp = md.get("logp")
    logp_ron = "None" if logp is None else f"Some({float(logp)})"
    props_ron = "[" + ", ".join(md.get("props") or []) + "]"
    return (f"    {sid}: (id: {sid}, name: {_ron_str(name)}, formula: {_ron_str(md.get('formula','?'))}, "
            f"state: Liquid, molar_mass_g_mol: {float(mw)}, logp: {logp_ron}, "
            f"properties: {props_ron}),")


def write_substances_delta_ron(discovered, meta, path):
    lines = ["({"]
    for cs, sid in sorted(discovered.items(), key=lambda kv: kv[1]):
        lines.append(_discovered_entry(cs, sid, meta))
    lines.append("})")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def write_discovered_smiles(meta, path):
    """id -> full canonical SMILES, so the renderer can draw the minted molecules
    (their stored name is truncated and can't be used for RDKit)."""
    mapping = {str(sid): md["smiles"] for sid, md in meta.items()}
    Path(path).write_text(json.dumps(mapping), encoding="utf-8")


def merge_substances(base_path, discovered, meta, out_path):
    """Append discovered substances into the base substances.ron map -> one file the game loads."""
    text = base_path.read_text(encoding="utf-8").rstrip()
    idx = text.rfind("})")               # the closing of the ({ ... }) map
    head = text[:idx].rstrip()
    lines = [head]
    for cs, sid in sorted(discovered.items(), key=lambda kv: kv[1]):
        lines.append(_discovered_entry(cs, sid, meta))
    lines.append("})")
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")


def build_index_from_reactions(records):
    """DEMO ONLY: harvest the compound universe from the reactions' own species."""
    index = {}
    nid = SCRAPED_ID_BASE
    for rec in records:
        n = normalize(rec)
        for cs in n["reactants"] + n["products"]:
            if cs and not is_spectator(cs) and cs not in index:
                index[cs] = nid
                nid += 1
    return index, {}


# --- RON out -----------------------------------------------------------------------
def stoich(ids):
    return "[" + ", ".join(f"(substance_id: {i}, moles: 1)" for i in ids) + "]"


def conditions_ron(r):
    """Emit a `conditions: [...]` list. Records the reaction's temperature as a
    Temperature(K) Condition when present. The game's matcher ignores conditions today,
    so this is safe additive data (detail panel / future disambiguation)."""
    conds = []
    t = r.get("temp_k")
    if t is not None:
        try:
            conds.append(f"Temperature({float(t)})")
        except (TypeError, ValueError):
            pass
    return "[" + ", ".join(conds) + "]"


def write_reactions_ron(by_key, path, id_start=2000):
    lines = ["(", "    reactions: ["]
    rid = id_start
    for (process, _), r in sorted(by_key.items(), key=lambda kv: (kv[1]["process"], kv[1]["reactants"])):
        name = f"{process} of #{r['reactants'][0]}"
        lines.append("        (")
        lines.append(f"            id: {rid},")
        lines.append(f'            name: "{name}",')
        lines.append(f"            reactants: {stoich(r['reactants'])},")
        lines.append(f"            products: {stoich(r['products'])},")
        lines.append(f"            process: {process},")
        lines.append(f"            conditions: {conditions_ron(r)},")
        lines.append(f"            enthalpy_change_kj_mol: {float(r['dH'])},")
        lines.append(f"            activation_energy_kj: 30.0,")
        lines.append("        ),")
        rid += 1
    lines += ["    ],", ")"]
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def write_demo_substances_ron(index, path):
    """emit a self-consistent substances.ron for the harvested demo universe so the
    demo reactions.ron actually loads against the real Rust struct."""
    lines = ["({"]
    for cs, sid in sorted(index.items(), key=lambda kv: kv[1]):
        m = Chem.MolFromSmiles(cs)
        formula = rdMolDescriptors.CalcMolFormula(m) if m else "?"
        name = cs if len(cs) <= 32 else cs[:29] + "..."
        lines.append(f"    {sid}: (")
        lines.append(f"        id: {sid}, name: \"{name}\", formula: \"{formula}\",")
        lines.append(f"        state: Liquid, molar_mass_g_mol: 0.0, properties: [],")
        lines.append(f"    ),")
    lines.append("})")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", type=Path, help="a reactions JSON (list) to run mechanics on")
    ap.add_argument("--compounds", type=Path)
    ap.add_argument("--reactions", type=Path, help="dir of per-file reaction JSONs")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--registry", type=Path,
                    help="registry.json from compile_data.py (shared SMILES->id numbering)")
    ap.add_argument("--substances-base", type=Path,
                    help="compile_data's substances.ron; if set, writes a merged substances_full.ron "
                         "= base + discovered, so the game loads one file")
    ap.add_argument("--discover-species", "--discover-products", dest="discover_products",
                    action="store_true",
                    help="mint recurrent unknown species on BOTH sides (reactants and "
                         "products) as new substances, so closure-on-both-sides keeps a rich "
                         "library. (--discover-products is kept as an alias.)")
    ap.add_argument("--min-occurrence", type=int, default=1,
                    help="with --discover-species: only mint species seen this many times. "
                         "Higher = smaller, tighter substance table + reactions.ron; "
                         "lower = richer but larger. Try 2-3 first.")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    if args.demo:
        records = json.loads(args.demo.read_text(encoding="utf-8"))
        index, hf = build_index_from_reactions(records)
        by_key, stats, phist = resolve(records, index, hf)
        write_demo_substances_ron(index, args.out / "demo_substances.ron")
        write_reactions_ron(by_key, args.out / "demo_reactions.ron")
    else:
        validate_dir(args.reactions, "reactions")
        if args.registry:                       # preferred: shared numbering from compile_data
            reg = json.loads(args.registry.read_text(encoding="utf-8"))
            index = {smi: int(i) for smi, i in reg["by_smiles"].items()}
            hf = {int(k): v for k, v in reg.get("hf", {}).items()}
            print(f"registry: {len(index):,} substances (shared ids from compile_data).", flush=True)
        else:                                    # fallback: number our own from the compound dir
            compound_files = list_dir(args.compounds, "compounds")
            print(f"compounds: {len(compound_files):,} json files. building index...", flush=True)
            index, hf = build_index_from_compounds(compound_files)
            print(f"compound index: {len(index):,} substances.", flush=True)
        if not index:
            raise SystemExit("ERROR: substance index is empty (no usable SMILES found).")

        discovered, meta = {}, {}
        if args.discover_products:
            print("discovery mode: minting recurrent unknown species (both sides)...", flush=True)
            discovered, meta = discover_products(args.reactions, index, args.min_occurrence)
            index = {**index, **discovered}
            write_substances_delta_ron(discovered, meta, args.out / "discovered_substances.ron")
            write_discovered_smiles(meta, args.out / "discovered_smiles.json")
            print(f"expanded index: {len(index):,} substances "
                  f"({len(discovered):,} discovered, full SMILES -> discovered_smiles.json). "
                  f"resolving...", flush=True)

        stream = tqdm(iter_reaction_dir(args.reactions), desc="resolving", unit="rxn")
        by_key, stats, phist = resolve(stream, index, hf)
        write_reactions_ron(by_key, args.out / "reactions.ron")

        if args.substances_base:
            merge_substances(args.substances_base, discovered, meta, args.out / "substances_full.ron")
            print(f"merged: substances_full.ron = base + {len(discovered):,} discovered", flush=True)

    print("=== resolve stats ===")
    for k in ["total", "dropped_bad_yield", "dropped_open_products",
              "dropped_open_reactants", "dropped_no_mapped_reactants",
              "dropped_no_net_product", "collisions", "kept_unique"]:
        print(f"  {k:28} {stats[k]}")
    print(f"  compound universe size       {len(index)}")
    print("=== player-process distribution of kept recipes ===")
    for p, c in phist.most_common():
        print(f"  {p:14} {c}")


if __name__ == "__main__":
    main()