#!/usr/bin/env python3
"""
Curieosity progression analyzer
================================
Reads the game's real `reactions.ron` (and optionally `substances.ron` for names)
and works out the *reachability structure* of the reaction graph: starting from a
small set of "discovered" substances, which reactions can the player perform, what
do they unlock, and how deep does the tree go before it dead-ends.

This is the grounding step for the tech tree. It answers, from your ACTUAL data:
  * If the player starts with substances {A, B, C, ...}, how many reactions can they
    do immediately, and what do those make?
  * Generation by generation (a "tier"), how does the reachable set grow?
  * How many substances / reactions are *never* reachable from that start (orphans)
    -> these are exactly the things a tech-tree UNLOCK needs to hand the player.
  * Which processes dominate each tier.

Nothing here changes any game data. It only reads and reports.

Run (start from the 5 curated starter elements H2,C,N2,O2,Na = ids 1,3,4,5,6):
    python3 analyze_progression.py --reactions ./assets/data/reactions.ron \
        --substances ./assets/data/substances.ron

Compare "start with every element unlocked" (seeds all element-block ids that appear
anywhere as a reactant):
    python3 analyze_progression.py --reactions ./assets/data/reactions.ron \
        --substances ./assets/data/substances.ron --add-all-elements

Custom starter set:
    python3 analyze_progression.py --reactions ... --starter 1,3,4,5,6,8
"""

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path

# --- parsing ----------------------------------------------------------------------

# One reaction block: id, name, then reactants:[...] products:[...] process: X
_REACTION_RE = re.compile(
    r"id:\s*(\d+)\s*,\s*"
    r'name:\s*"((?:[^"\\]|\\.)*)"\s*,\s*'
    r"reactants:\s*\[(.*?)\]\s*,\s*"
    r"products:\s*\[(.*?)\]\s*,\s*"
    r"process:\s*(\w+)",
    re.DOTALL,
)
_SID_RE = re.compile(r"substance_id:\s*(\d+)")


def parse_reactions(path):
    """-> list of dicts: {id, name, reactants:set[int], products:set[int], process:str}."""
    text = Path(path).read_text(encoding="utf-8")
    out = []
    for m in _REACTION_RE.finditer(text):
        rid, name, r_blob, p_blob, process = m.groups()
        reactants = {int(x) for x in _SID_RE.findall(r_blob)}
        products = {int(x) for x in _SID_RE.findall(p_blob)}
        out.append({
            "id": int(rid),
            "name": name,
            "reactants": reactants,
            "products": products,
            "process": process,
        })
    return out


def parse_substance_names(path):
    """Best-effort id -> name from substances.ron. Tolerant: finds `<id>: ( ... name: "X"`
    within each top-level entry. Returns {} if the file is absent."""
    names = {}
    if not path or not Path(path).exists():
        return names
    text = Path(path).read_text(encoding="utf-8")
    # Each entry looks like:  123: ( ... name: "Foo", ... ),
    # Grab an id that opens a paren, then the first name:"..." that follows it.
    for m in re.finditer(r"(\d+)\s*:\s*\(", text):
        sid = int(m.group(1))
        tail = text[m.end():m.end() + 400]
        nm = re.search(r'name:\s*"((?:[^"\\]|\\.)*)"', tail)
        if nm:
            names[sid] = nm.group(1)
    return names


def name_of(names, sid):
    return names.get(sid, f"#{sid}")


# --- reachability -----------------------------------------------------------------

def reachability(reactions, starter):
    """BFS over the reaction graph. Returns (generations, performable, orphan_reactions).

    generations: list where generations[k] is the set of substance ids NEWLY reachable
    at tier k (gen 0 = starter). A reaction fires once ALL its reactants are known.
    """
    known = set(starter)
    generations = [set(starter)]
    fired = set()
    fired_by_gen = []  # reactions that first became performable at each gen

    while True:
        newly_fired = [r for r in reactions
                       if r["id"] not in fired and r["reactants"] <= known]
        if not newly_fired:
            break
        gen_new_subs = set()
        for r in newly_fired:
            fired.add(r["id"])
            gen_new_subs |= (r["products"] - known)
        fired_by_gen.append(newly_fired)
        if not gen_new_subs:
            # reactions fired but produced nothing new -> closure reached
            break
        known |= gen_new_subs
        generations.append(gen_new_subs)

    orphan_reactions = [r for r in reactions if r["id"] not in fired]
    return generations, fired, fired_by_gen, orphan_reactions, known


# --- report -----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reactions", type=Path, required=True)
    ap.add_argument("--substances", type=Path, help="optional, for readable names")
    ap.add_argument("--starter", type=str, default="1,3,4,5,6",
                    help="comma-separated substance ids the player starts with "
                         "(default = curated elements H2,C,N2,O2,Na)")
    ap.add_argument("--add-all-elements", action="store_true",
                    help="also seed every element-block id (1000..1199) that appears "
                         "as a reactant anywhere -- simulates 'all elements unlocked'")
    ap.add_argument("--show-first", type=int, default=30,
                    help="how many immediate (tier-1) reactions to list")
    ap.add_argument("--show-orphan-products", type=int, default=25,
                    help="how many unreachable products to list (tech-tree unlock candidates)")
    args = ap.parse_args()

    reactions = parse_reactions(args.reactions)
    names = parse_substance_names(args.substances)
    if not reactions:
        raise SystemExit(f"No reactions parsed from {args.reactions} -- wrong path or format?")

    all_reactant_ids = set().union(*(r["reactants"] for r in reactions)) if reactions else set()
    all_product_ids = set().union(*(r["products"] for r in reactions)) if reactions else set()
    all_ids = all_reactant_ids | all_product_ids

    starter = {int(x) for x in args.starter.split(",") if x.strip()}
    if args.add_all_elements:
        starter |= {i for i in all_reactant_ids if 1000 <= i < 1200}

    generations, fired, fired_by_gen, orphans, known = reachability(reactions, starter)

    print("=" * 70)
    print("CURIEOSITY PROGRESSION ANALYSIS")
    print("=" * 70)
    print(f"reactions in file        : {len(reactions):,}")
    print(f"distinct substances used : {len(all_ids):,} "
          f"({len(all_reactant_ids):,} as reactant, {len(all_product_ids):,} as product)")
    print(f"starter set              : {len(starter)} ids -> "
          + ", ".join(name_of(names, s) for s in sorted(starter)[:12])
          + (" ..." if len(starter) > 12 else ""))
    print()

    print("-" * 70)
    print("REACHABILITY BY TIER (generation)")
    print("-" * 70)
    cumulative = len(generations[0])
    for k, gen in enumerate(generations):
        n_fired = len(fired_by_gen[k]) if k < len(fired_by_gen) else 0
        if k == 0:
            print(f"  tier 0 (start) : {len(gen):>5} substances")
        else:
            cumulative += len(gen)
            procs = Counter(r["process"] for r in fired_by_gen[k - 1]) if k - 1 < len(fired_by_gen) else Counter()
            top = ", ".join(f"{p}:{c}" for p, c in procs.most_common(4))
            sample = ", ".join(name_of(names, s) for s in sorted(gen)[:6])
            print(f"  tier {k:<2}       : +{len(gen):>4} new (cum {cumulative:>5}) "
                  f"via {top}")
            print(f"                   e.g. {sample}")
    print()
    print(f"  TOTAL reachable substances : {len(known):,} of {len(all_ids):,}")
    print(f"  TOTAL performable reactions: {len(fired):,} of {len(reactions):,}")
    print()

    print("-" * 70)
    print(f"IMMEDIATE FRONTIER  (what the player can do on turn 1, up to {args.show_first})")
    print("-" * 70)
    tier1 = fired_by_gen[0] if fired_by_gen else []
    if not tier1:
        print("  (nothing performable from this starter set -- the start is too small;")
        print("   widen --starter or use --add-all-elements)")
    for r in tier1[:args.show_first]:
        reac = " + ".join(name_of(names, s) for s in sorted(r["reactants"]))
        prod = " + ".join(name_of(names, s) for s in sorted(r["products"]))
        print(f"  [{r['process']:<12}] {reac}  ->  {prod}")
    if len(tier1) > args.show_first:
        print(f"  ... and {len(tier1) - args.show_first:,} more immediately performable")
    print()

    print("-" * 70)
    print("ORPHANS  (never reachable from this start -> need a tech-tree UNLOCK)")
    print("-" * 70)
    orphan_products = set().union(*(r["products"] for r in orphans)) - known if orphans else set()
    print(f"  unreachable reactions : {len(orphans):,}")
    print(f"  unreachable products  : {len(orphan_products):,}")
    for sid in sorted(orphan_products)[:args.show_orphan_products]:
        print(f"    - {name_of(names, sid)}")
    if len(orphan_products) > args.show_orphan_products:
        print(f"    ... and {len(orphan_products) - args.show_orphan_products:,} more")
    print()

    print("-" * 70)
    print("PROCESS MIX  (across all reactions in the file)")
    print("-" * 70)
    pc = Counter(r["process"] for r in reactions)
    for p, c in pc.most_common():
        print(f"  {p:<14} {c:>6,}")


if __name__ == "__main__":
    main()