#!/usr/bin/env python3
"""
Curieosity authored layer generator
===================================
The canon content of the game -- the tech-tree chains, the substances they move through,
the epochs, the starting kit, and the milestones -- lives in `authored_content.py` and
`authored_tiers.py` (the vessel tiers, the laboratory families and the milestone ladder)
as plain Python data. This script validates it and writes the two files the game loads:

  assets/data/authored_reactions.ron    epochs, start set, milestones, reactions
  assets/data/authored_substances.ron   patches over the scraped library + new substances

and then packs the game's substances (pack_library.py): from the full scraped library in
library/ it keeps the substances in play and their pictures, in assets/.

Every substance is referred to by a short KEY ("H2O", "Limestone", "ZnCl2"). A key is
either BOUND to an existing library entry (lib=True: the scraped entry keeps its
narrative; we only clean its name/formula) or NEW (it carries its own description and
Wikipedia link). Equations are written like a textbook:

    R("Iron Bloomery", "2 Hematite + 3 Charcoal -> 4 Fe + 3 CO2", SMELT, "...")

Validation (any failure stops the build):
  * every key resolves and every equation balances atom-for-atom (unless exact=False,
    used only for mixtures such as glass, black powder, crude oil)
  * no two reactions share the same (vessel, reactant set) -- the game matches on that
  * every new substance has a description and a reference link: its Wikipedia article, or
    its PubChem page (gen_authored.pubchem) when it has no article of its own
  * every reaction can actually be performed from the starting kit, through the
    milestones, in the order the game's own planner takes (the review run follows it)
  * a recipe that needs a catalyst lives in a vessel with a catalyst slot, and the tiers
    of each vessel family unlock bottom-up
  * pacing: no milestone hands over more than MAX_GRANT materials (an error), and no
    stretch of the eras goes MAX_MILESTONE_GAP steps without a milestone (a warning)

Run from the project root:
    python tools/data/gen_authored.py                 # validate + write both RON files
    python tools/data/gen_authored.py --check         # validate only
    python tools/data/gen_authored.py --render        # also draw library/structures/{id}.png
                                                      # for new substances (RDKit + Pillow)
    python tools/data/gen_authored.py --rebind        # retry library binding for keys that
                                                      # were given a fresh id earlier
    python tools/data/gen_authored.py --pacing        # list the milestone ladder by step
    python tools/data/gen_authored.py --check --check-links   # verify every Wikipedia link
                                                      # exists (needs the network)

Ids. A substance written with id=0 is resolved once and remembered in authored_ids.json
(next to this script), so ids never shift when content is added or reordered and saved
games stay valid. Resolution tries an exact, case-insensitive name match against the
library entries that have a description and a Wikipedia link (LIBNAME[key] first, then
the display name), with the formula agreeing; failing that it allocates a fresh id from
the gaps in the library's id space.
"""

import argparse
import collections
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LIBRARY = ROOT / "library"   # the full scrape (not in the repository); see pack_library.py

# --------------------------------------------------------------------------------------
# Vessels (ProcessType in the game)
# --------------------------------------------------------------------------------------
MIX, HEAT, COOL, SMELT, DISTIL = "Mix", "Heat", "Cool", "Smelting", "Distillation"
ELEC, LIGHT, CAT, PRESS, POLY = "Electrolysis", "Irradiate", "Catalysis", "Pressurize", "Polymerize"
FLASK, BLAST, ARC, AIRLIQ, COLUMN = "Flask", "BlastFurnace", "ArcFurnace", "AirLiquefier", "Column"
ECELL, REACTOR, CYCLO, CRACKER, HIGHP = ("ElectrolyticCell", "NuclearReactor", "Cyclotron",
                                         "Cracker", "HighPressure")
DPRESS, FERM, BIOR, PULLER, CVD = "DiamondPress", "Fermenter", "Bioreactor", "CrystalPuller", "CvdChamber"
CENT, ULTRA = "Centrifuge", "Ultracentrifuge"

# process -> (vessel name, family, tier, catalyst slot). Mirrors VESSEL_SPECS in
# src/data/common.rs: a vessel runs its family's recipes at its tier or below, and a
# recipe's process is its home vessel.
VESSELS = {
    MIX: ("Mortar", "Mix", 1, False),            FLASK: ("Glass Flask", "Mix", 2, False),
    HEAT: ("Fire", "Heat", 1, False),            SMELT: ("Bloomery", "Heat", 2, False),
    BLAST: ("Blast Furnace", "Heat", 3, False),  ARC: ("Arc Furnace", "Heat", 4, False),
    DISTIL: ("Still", "Distillation", 1, False), COLUMN: ("Fractionating Column", "Distillation", 2, False),
    COOL: ("Ice Bath", "Cool", 1, False),        AIRLIQ: ("Air Liquefier", "Cool", 2, False),
    ELEC: ("Voltaic Cell", "Electrolysis", 1, False),
    ECELL: ("Electrolytic Cell", "Electrolysis", 2, False),
    CAT: ("Catalyst Bed", "Catalysis", 1, True), CRACKER: ("Catalytic Cracker", "Catalysis", 2, True),
    PRESS: ("Autoclave", "Pressure", 1, False),  HIGHP: ("High-Pressure Reactor", "Pressure", 2, True),
    DPRESS: ("Diamond Press", "Pressure", 3, True),
    LIGHT: ("Irradiator", "Radiation", 1, False), REACTOR: ("Nuclear Reactor", "Radiation", 2, False),
    CYCLO: ("Cyclotron", "Radiation", 3, False),
    POLY: ("Polymer Reactor", "Polymer", 1, False),
    FERM: ("Fermenter", "Biology", 1, False),    BIOR: ("Bioreactor", "Biology", 2, True),
    PULLER: ("Crystal Puller", "Fabrication", 1, False), CVD: ("CVD Chamber", "Fabrication", 2, True),
    CENT: ("Centrifuge", "Separation", 1, False), ULTRA: ("Ultracentrifuge", "Separation", 2, False),
}
PROCESSES = set(VESSELS)
START_PROCESSES = {MIX, HEAT}

# Authored reaction ids start here (clear of the ids the scraped library's reactions used,
# up to about 205,000); mirrored by tests/content.rs.
AUTHORED_REACTION_BASE = 1_000_000

# Pacing limits, also enforced by tests/content.rs on the generated RON.
MAX_GRANT = 12          # materials handed over by one milestone
MAX_MILESTONE_GAP = 90  # planner steps (era reactions) between two milestones

STATES = {"Solid", "Liquid", "Gas", "Aqueous"}
PROPS = {"IsAcid", "IsBase", "IsMetal", "IsRadioactive", "IsMonomer", "IsPolymer", "IsMedicine", "IsClass",
         "IsElectrolyte", "IsPhotochromic"}

# --------------------------------------------------------------------------------------
# Content records
# --------------------------------------------------------------------------------------
@dataclass
class Sub:
    key: str
    name: str
    formula: str            # display formula (ASCII; the game subscripts digits)
    state: str
    id: int
    lib: bool = False       # bound to an existing library entry
    desc: str = None
    wiki: str = None        # article title ("Zinc_chloride") or full URL
    props: tuple = ()
    color: str = None       # "#rrggbb", tints the vessel contents
    smiles: str = None      # new molecular substances: drawn into structures/{id}.png
    balance: str = None     # formula used for atom balance when `formula` is a polymer/alloy
    rename: bool = False    # for lib entries: also patch the display name
    stage: str = None       # a later stage: a locked preview with a page but no reaction yet


@dataclass
class Rx:
    name: str
    equation: str
    process: str
    desc: str
    wiki: str = None
    cat: str = None         # catalyst key (must sit in the Catalyst Bed's slot)
    T: float = None         # temperature, deg C (shown, not enforced)
    P: float = None         # pressure, atm (shown, not enforced)
    dh: float = 0.0         # reaction enthalpy, kJ/mol
    ea: float = None        # activation energy, kJ/mol
    exact: bool = True      # False: mixture chemistry, skip the atom balance
    epoch: int = None       # set by the epoch section
    id: int = None          # assigned on output


@dataclass
class Milestone:
    on: str
    unlock: tuple = ()
    grant: tuple = ()
    message: str = None


@dataclass
class Epoch:
    name: str
    era: str
    reactions: list = field(default_factory=list)
    blurb: str = None       # one line for the banner when the player reaches the era


def R(name, equation, process, desc, **kw):
    return Rx(name, equation, process, desc, **kw)


# --------------------------------------------------------------------------------------
# Formula handling
# --------------------------------------------------------------------------------------
def atoms(formula):
    """Element counts of a formula. Handles (groups)n, [groups]n and hydrate dots."""
    total = collections.Counter()
    for part in re.split(r"[·*]", formula.replace(" ", "")):
        m = re.match(r"^(\d+)(.+)$", part)
        mult = 1
        if m:
            mult, part = int(m.group(1)), m.group(2)
        stack = [collections.Counter()]
        i = 0
        while i < len(part):
            c = part[i]
            if c in "([":
                stack.append(collections.Counter())
                i += 1
            elif c in ")]":
                i += 1
                n = ""
                while i < len(part) and part[i].isdigit():
                    n += part[i]
                    i += 1
                top = stack.pop()
                for k, v in top.items():
                    stack[-1][k] += v * (int(n) if n else 1)
            elif c.isupper():
                sym = c
                i += 1
                while i < len(part) and part[i].islower():
                    sym += part[i]
                    i += 1
                n = ""
                while i < len(part) and part[i].isdigit():
                    n += part[i]
                    i += 1
                stack[-1][sym] += int(n) if n else 1
            else:
                raise ValueError(f"unparseable formula {formula!r} at {c!r}")
        if len(stack) != 1:
            raise ValueError(f"unbalanced brackets in {formula!r}")
        for k, v in stack[0].items():
            total[k] += v * mult
    return total


ATOMIC_MASS = {
    "H": 1.008, "He": 4.0026, "Li": 6.94, "Be": 9.0122, "B": 10.81, "C": 12.011, "N": 14.007,
    "O": 15.999, "F": 18.998, "Ne": 20.180, "Na": 22.990, "Mg": 24.305, "Al": 26.982,
    "Si": 28.085, "P": 30.974, "S": 32.06, "Cl": 35.45, "Ar": 39.948, "K": 39.098,
    "Ca": 40.078, "Sc": 44.956, "Ti": 47.867, "V": 50.942, "Cr": 51.996, "Mn": 54.938,
    "Fe": 55.845, "Co": 58.933, "Ni": 58.693, "Cu": 63.546, "Zn": 65.38, "Ga": 69.723,
    "Ge": 72.630, "As": 74.922, "Se": 78.971, "Br": 79.904, "Kr": 83.798, "Rb": 85.468,
    "Sr": 87.62, "Y": 88.906, "Zr": 91.224, "Nb": 92.906, "Mo": 95.95, "Tc": 98.0,
    "Ru": 101.07, "Rh": 102.91, "Pd": 106.42, "Ag": 107.87, "Cd": 112.41, "In": 114.82,
    "Sn": 118.71, "Sb": 121.76, "Te": 127.60, "I": 126.90, "Xe": 131.29, "Cs": 132.91,
    "Ba": 137.33, "La": 138.91, "Ce": 140.12, "Pr": 140.91, "Nd": 144.24, "Pm": 145.0,
    "Sm": 150.36, "Eu": 151.96, "Gd": 157.25, "Tb": 158.93, "Dy": 162.50, "Ho": 164.93,
    "Er": 167.26, "Tm": 168.93, "Yb": 173.05, "Lu": 174.97, "Hf": 178.49, "Ta": 180.95,
    "W": 183.84, "Re": 186.21, "Os": 190.23, "Ir": 192.22, "Pt": 195.08, "Au": 196.97,
    "Hg": 200.59, "Tl": 204.38, "Pb": 207.2, "Bi": 208.98, "Po": 209.0, "At": 210.0,
    "Rn": 222.0, "Fr": 223.0, "Ra": 226.0, "Ac": 227.0, "Th": 232.04, "Pa": 231.04,
    "U": 238.03, "Np": 237.0, "Pu": 244.0, "Am": 243.0, "Cm": 247.0,
}


def molar_mass(formula):
    try:
        return round(sum(ATOMIC_MASS[k] * v for k, v in atoms(formula).items()), 3)
    except (KeyError, ValueError):
        return None


def wiki_url(w):
    if w is None:
        return None
    if w.startswith("http"):
        return w
    return "https://en.wikipedia.org/wiki/" + w.replace(" ", "_")


def pubchem(cid):
    """The PubChem page of a compound, for one with no Wikipedia article of its own: by CID,
    or by name where no CAS-sourced CID is to hand (PubChem resolves names to the record)."""
    if isinstance(cid, str):
        import urllib.parse
        return "https://pubchem.ncbi.nlm.nih.gov/compound/" + urllib.parse.quote(cid)
    return f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"


def ref_entry(w):
    """A `references` entry for a substance's or reaction's link: labelled Wikipedia for an
    article title or URL, PubChem for a PubChem page, else by the site's name."""
    url = wiki_url(w)
    if "wikipedia.org" in url:
        label = "Wikipedia"
    elif "pubchem.ncbi.nlm.nih.gov" in url:
        label = "PubChem"
    else:
        label = url.split("//", 1)[-1].split("/", 1)[0].removeprefix("www.")
    return f"[({q(label)}, {q(url)})]"


# --------------------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------------------
TERM = re.compile(r"^(?:(\d+)\s+)?(\S+)$")


class ContentError(Exception):
    pass


def parse_side(side, subs, where):
    out, bad = [], []
    for term in side.split(" + "):
        term = term.strip()
        m = TERM.match(term)
        if not m:
            raise ContentError(f"[{where}] bad term {term!r}")
        n, key = int(m.group(1) or 1), m.group(2)
        if key not in subs:
            bad.append(key)
        out.append((n, key))
    if bad:
        raise ContentError(f"[{where}] unknown substance key(s) {bad}")
    return out


def parse_equation(rx, subs):
    if rx.equation.count(" -> ") != 1:
        raise ContentError(f"[{rx.name}] equation needs exactly one ' -> ': {rx.equation!r}")
    lhs, rhs = rx.equation.split(" -> ")
    return parse_side(lhs, subs, rx.name), parse_side(rhs, subs, rx.name)


# --------------------------------------------------------------------------------------
# Id resolution
# --------------------------------------------------------------------------------------
IDMAP_PATH = HERE / "authored_ids.json"
# ids the substance library leaves unused; 1001-1118 are the elements, so the last pool starts after them
FREE_POOLS = [(14, 99), (120, 199), (217, 299), (388, 999), (1119, 1999)]


def library_index(path):
    """Scan substances.ron without a RON parser: id, name, formula, and whether the entry
    carries a description and a Wikipedia reference."""
    idx = {}
    cur = None
    rx_id = re.compile(r"^ {12}id: (\d+),")
    rx_name = re.compile(r'^ {12}name: "(.*)",$')
    rx_formula = re.compile(r'^ {12}formula: "(.*)",$')
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("            id: "):
                m = rx_id.match(line)
                cur = {"id": int(m.group(1)), "name": "", "formula": "", "desc": False, "wiki": False}
                idx[cur["id"]] = cur
            elif cur is None:
                continue
            elif line.startswith("            name: "):
                m = rx_name.match(line)
                cur["name"] = m.group(1) if m else ""
            elif line.startswith("            formula: "):
                m = rx_formula.match(line)
                cur["formula"] = m.group(1) if m else ""
            elif line.startswith("            description: Some("):
                cur["desc"] = True
            elif line.startswith("            references: ") and "wikipedia.org" in line:
                cur["wiki"] = True
    return idx


def atoms_or_none(formula):
    try:
        return atoms(formula)
    except Exception:
        return None


def _hill(formula):
    try:
        return tuple(sorted(atoms(formula).items()))
    except Exception:
        return None


def resolve_ids(content, library_path, rebind=False):
    subs = content.SUBSTANCES
    libname = getattr(content, "LIBNAME", {})
    idmap = json.loads(IDMAP_PATH.read_text()) if IDMAP_PATH.exists() else {}
    if rebind:
        idmap = {k: v for k, v in idmap.items() if v.get("lib")}
    pending = [s for s in subs.values() if s.id == 0 and s.key not in idmap]
    taken = {s.id for s in subs.values() if s.id} | {v["id"] for v in idmap.values()}
    bound = allocated = 0
    if pending:
        print(f"resolving {len(pending)} new substance id(s) against {library_path.name} ...")
        lib = library_index(library_path)
        by_name = collections.defaultdict(list)
        for e in lib.values():
            if e["desc"] and e["wiki"]:
                by_name[e["name"].lower()].append(e)
        pools = (i for a, b in FREE_POOLS for i in range(a, b + 1))
        for s in pending:
            want = _hill(s.balance or s.formula)
            hit = None
            for n in (libname.get(s.key), s.name):
                if not n:
                    continue
                cands = [e for e in by_name.get(n.lower(), []) if e["id"] not in taken
                         and (_hill(e["formula"]) in (want, None))]
                if cands:
                    hit = min(cands, key=lambda e: e["id"])
                    break
            if hit:
                idmap[s.key] = {"id": hit["id"], "lib": True, "name": hit["name"]}
                taken.add(hit["id"])
                bound += 1
                continue
            nid = next(i for i in pools if i not in taken and i not in lib)
            taken.add(nid)
            entry = {"id": nid, "lib": False}
            if s.desc and s.wiki:      # remember only ids that will be kept
                idmap[s.key] = entry
            else:
                s._transient = entry
            allocated += 1
    for s in subs.values():
        if s.id:
            continue
        e = idmap.get(s.key) or getattr(s, "_transient")
        s.id = e["id"]
        if e["lib"]:
            s.lib = True
            # an X() with its own display name keeps it; an L()/LIBNAME key shows the
            # library's name unless rename=True
            if s.key not in libname and s.name.lower() != e.get("name", "").lower():
                s.rename = True
    live = {s.key for s in subs.values()}
    idmap = {k: v for k, v in idmap.items() if k in live}
    IDMAP_PATH.write_text(json.dumps(dict(sorted(idmap.items())), indent=1) + "\n")
    if pending:
        print(f"  {bound} bound to library entries, {allocated} given fresh ids")


def side_atoms(side, subs):
    total = collections.Counter()
    for n, key in side:
        s = subs[key]
        for k, v in atoms(s.balance or s.formula).items():
            total[k] += n * v
    return total


def validate(content, strict=True):
    subs = content.SUBSTANCES
    errors, warnings = [], []

    ids = collections.Counter(s.id for s in subs.values())
    for i, c in ids.items():
        if c > 1:
            errors.append(f"substance id {i} used by {c} keys: "
                          + ", ".join(k for k, s in subs.items() if s.id == i))
    for k, s in subs.items():
        if k != s.key:
            errors.append(f"key mismatch {k} vs {s.key}")
        if s.state not in STATES:
            errors.append(f"{k}: bad state {s.state}")
        for p in s.props:
            if p not in PROPS:
                errors.append(f"{k}: bad property {p}")
        try:
            atoms(s.balance or s.formula)
        except ValueError as e:
            errors.append(f"{k}: {e}")
        if not s.lib and (not s.desc or not s.wiki):
            errors.append(f"{k} ({s.name}): new substance needs desc and wiki")

    rxns = [r for e in content.EPOCHS for r in e.reactions]
    for k in list(content.START) + [x for m in content.MILESTONES for x in (m.on, *m.grant)]:
        if k not in subs:
            errors.append(f"start/milestone key {k!r} is not a substance")
    if errors:
        return errors, warnings, {}, {}, set()
    seen = {}
    parsed = {}
    for r in rxns:
        if r.process not in PROCESSES:
            errors.append(f"[{r.name}] unknown process {r.process}")
        if not r.desc or not r.wiki:
            errors.append(f"[{r.name}] needs desc and wiki")
        try:
            lhs, rhs = parse_equation(r, subs)
        except ContentError as e:
            errors.append(str(e))
            continue
        parsed[id(r)] = (lhs, rhs)
        if r.exact:
            a, b = side_atoms(lhs, subs), side_atoms(rhs, subs)
            if a != b:
                diff = {k: a.get(k, 0) - b.get(k, 0) for k in set(a) | set(b) if a.get(k, 0) != b.get(k, 0)}
                errors.append(f"[{r.name}] unbalanced {r.equation}  (lhs-rhs {diff})")
        rset = frozenset(subs[k].id for _, k in lhs)
        sig = (r.process, rset)
        if sig in seen:
            errors.append(f"[{r.name}] same vessel + reactants as [{seen[sig]}]")
        seen[sig] = r.name
        if r.cat and r.cat not in subs:
            errors.append(f"[{r.name}] unknown catalyst {r.cat}")
        if r.cat and r.process in VESSELS and not VESSELS[r.process][3]:
            errors.append(f"[{r.name}] needs a catalyst but the {VESSELS[r.process][0]} has no "
                          f"catalyst slot")
        if set(k for _, k in lhs) & set(k for _, k in rhs):
            warnings.append(f"[{r.name}] a substance appears on both sides")

    if any(id(r) not in parsed for r in rxns):
        return errors, warnings, {}, parsed, set()

    # --- the vessel table itself: a catalyst recipe must run in every vessel above it ---
    for p, (vname, fam, tier, slot) in VESSELS.items():
        for q2, (v2, f2, t2, s2) in VESSELS.items():
            if f2 == fam and t2 > tier and slot and not s2:
                errors.append(f"the {v2} outranks the {vname} but has no catalyst slot")

    # --- reachability and pacing: RecipeDatabase::playthrough, step for step ---
    # Milestones fire first; then the first performable reaction in tech-tree order
    # (era, then id) is taken. The same planner drives the in-game review run.
    plan, pacing = playthrough(content, parsed)
    fired = {id(r) for r in plan}
    have = pacing["known"]
    unreachable = [r for r in rxns if id(r) not in fired]
    for p, when in pacing["unlocked_at"].items():
        fam, tier = VESSELS[p][1], VESSELS[p][2]
        for q2, (v2, f2, t2, _) in VESSELS.items():
            if f2 == fam and t2 < tier and pacing["unlocked_at"].get(q2, 10**9) > when:
                errors.append(f"the {VESSELS[p][0]} unlocks before the {v2}, a lower tier of "
                              f"the same family")
    for p in PROCESSES - set(pacing["unlocked_at"]):
        errors.append(f"no milestone unlocks the {VESSELS[p][0]}")
    for m in content.MILESTONES:
        if len(m.grant) > MAX_GRANT:
            errors.append(f"milestone on {m.on} grants {len(m.grant)} materials (limit {MAX_GRANT})")
    for a, b, gap in pacing["gaps"]:
        if gap > MAX_MILESTONE_GAP:
            warnings.append(f"{gap} era steps between the {a} and {b} milestones "
                            f"(limit {MAX_MILESTONE_GAP})")
    for r in unreachable:
        lhs, _ = parsed[id(r)]
        missing = [k for _, k in lhs if subs[k].id not in have]
        if r.cat and subs[r.cat].id not in have:
            missing.append(f"catalyst {r.cat}")
        why = f"missing {missing}" if missing else f"vessel {r.process} never unlocked"
        errors.append(f"[{r.name}] can never be performed: {why}")

    used_keys = set(content.START)
    for m in content.MILESTONES:
        used_keys |= {m.on, *m.grant}
    for r in rxns:
        lhs, rhs = parsed[id(r)]
        used_keys |= {k for _, k in lhs + rhs}
        if r.cat:
            used_keys.add(r.cat)
    for k in sorted(used_keys):
        if subs[k].stage:
            errors.append(f"{k} ({subs[k].name}) is a locked preview of the {subs[k].stage} stage but a reaction, "
                          "milestone or the start kit uses it: give it no stage")
    unused = sorted(k for k in subs if k not in used_keys and not subs[k].stage)
    if unused:
        warnings.append(f"{len(unused)} defined substances are never used: {unused[:20]}")

    report = {
        "reactions": len(rxns),
        "reachable_reactions": len(rxns) - len(unreachable),
        "substances_in_play": len({subs[k].id for k in used_keys}),
        "obtainable": len(have),
        "new_substances": sum(1 for k in used_keys if not subs[k].lib),
        "library_bound": sum(1 for k in used_keys if subs[k].lib),
        "inexact": sum(1 for r in rxns if not r.exact),
        "previews": sum(1 for s in subs.values() if s.stage),
        "by_epoch": [(e.name, len(e.reactions)) for e in content.EPOCHS],
        "by_vessel": collections.Counter(r.process for r in rxns),
        "pacing": pacing,
    }
    return errors, warnings, report, parsed, used_keys


def playthrough(content, parsed):
    """The game's planner: returns (reactions in order, pacing facts)."""
    subs = content.SUBSTANCES
    rxns = sorted((r for e in content.EPOCHS for r in e.reactions), key=lambda r: (r.epoch, r.id))
    lab = len(content.EPOCHS) - 1          # "The Laboratory": side content, every age
    known = {subs[k].id for k in content.START}
    vessels = set(START_PROCESSES)
    unlocked_at = {p: 0 for p in START_PROCESSES}
    fired = [False] * len(content.MILESTONES)
    done = [False] * len(rxns)
    plan, events = [], []        # events: (step, era steps so far, milestone)
    era_steps = 0
    while True:
        changed = True
        while changed:
            changed = False
            for i, m in enumerate(content.MILESTONES):
                if not fired[i] and subs[m.on].id in known:
                    fired[i] = True
                    for p in m.unlock:
                        if p not in vessels:
                            vessels.add(p)
                            unlocked_at[p] = len(plan)
                    known |= {subs[g].id for g in m.grant}
                    events.append((len(plan), era_steps, m))
                    changed = True
        nxt = None
        for j, r in enumerate(rxns):
            if done[j] or r.process not in vessels:
                continue
            lhs, _ = parsed[id(r)]
            need = {subs[k].id for _, k in lhs} | ({subs[r.cat].id} if r.cat else set())
            if need <= known:
                nxt = j
                break
        if nxt is None:
            break
        done[nxt] = True
        r = rxns[nxt]
        known |= {subs[k].id for _, k in parsed[id(r)][1]}
        plan.append(r)
        if r.epoch != lab:
            era_steps += 1
    gaps = []
    prev_name, prev_at = "start", 0
    for _, at, m in events:
        gaps.append((prev_name, m.on, at - prev_at))
        prev_name, prev_at = m.on, at
    gaps.append((prev_name, "end", era_steps - prev_at))
    return plan, {"known": known, "unlocked_at": unlocked_at, "events": events, "gaps": gaps,
                  "era_steps": era_steps}


# --------------------------------------------------------------------------------------
# RON output
# --------------------------------------------------------------------------------------
def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def num(v):
    return repr(float(v))


def write_reactions(content, parsed, out_path):
    subs = content.SUBSTANCES
    lines = [
        "// assets/data/authored_reactions.ron",
        "// GENERATED by tools/data/gen_authored.py from tools/data/authored_content.py and",
        "// authored_tiers.py -- edit the content there and re-run the generator rather than",
        "// editing this file.",
        "(",
        "    epochs: [",
    ]
    for e in content.EPOCHS:
        blurb = f", blurb: {q(e.blurb)}" if e.blurb else ""
        lines.append(f"        (name: {q(e.name)}, era: {q(e.era)}{blurb}),")
    lines.append("    ],")
    lines.append("    start: [" + ", ".join(str(subs[k].id) for k in content.START) + "],")
    lines.append("    milestones: [")
    for m in content.MILESTONES:
        parts = [f"on: {subs[m.on].id}"]
        if m.unlock:
            parts.append("unlock: [" + ", ".join(m.unlock) + "]")
        if m.grant:
            parts.append("grant: [" + ", ".join(str(subs[g].id) for g in m.grant) + "]")
        if m.message:
            parts.append(f"message: Some({q(m.message)})")
        lines.append("        (" + ", ".join(parts) + "),")
    lines.append("    ],")
    lines.append("    reactions: [")
    for ei, e in enumerate(content.EPOCHS):
        lines.append(f"        // --- {ei}. {e.name} ({e.era}) ---")
        for r in e.reactions:
            lhs, rhs = parsed[id(r)]
            def sp(side):
                return ", ".join(f"(substance_id: {subs[k].id}, moles: {n})" for n, k in side)
            conds = []
            if r.T is not None:      # the game stores kelvin, like the scraped set
                conds.append(f"Temperature({num(round(r.T + 273.15, 2))})")
            if r.P is not None:      # atmospheres
                conds.append(f"Pressure({num(r.P)})")
            if r.cat:
                conds.append(f"RequiresCatalyst({subs[r.cat].id})")
            ea = r.ea if r.ea is not None else {MIX: 15.0, FLASK: 20.0, HEAT: 40.0, SMELT: 50.0,
                                                BLAST: 60.0, ARC: 80.0}.get(r.process, 30.0)
            lines += [
                "        (",
                f"            id: {r.id},",
                f"            name: {q(r.name)},",
                f"            reactants: [{sp(lhs)}],",
                f"            products: [{sp(rhs)}],",
                f"            process: {r.process},",
                f"            conditions: [{', '.join(conds)}],",
                f"            enthalpy_change_kj_mol: {num(r.dh)},",
                f"            activation_energy_kj: {num(ea)},",
                f"            description: Some({q(r.desc)}),",
                f"            references: {ref_entry(r.wiki)},",
                f"            epoch: {ei},",
                "        ),",
            ]
    lines += ["    ],", ")", ""]
    out_path.write_text("\n".join(lines), encoding="utf-8")


# properties that mark what a substance is for, rather than what it is chemically
TAGS = {"IsMedicine", "IsClass"}


def library_properties(path):
    """(id -> the library entry's properties, ids whose entry has a density): to keep the
    library's properties under an added tag, and its densities where it has them."""
    out, dense, cur = {}, set(), None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^ {12}id: (\d+),", line)
        if m:
            cur = int(m.group(1))
            continue
        m = re.match(r"^ {12}properties: \[(.*)\],", line)
        if m and cur is not None:
            out[cur] = [p.strip() for p in m.group(1).split(",") if p.strip() and "(" not in p]
        elif cur is not None and line.startswith("            density_g_cm3: Some("):
            dense.add(cur)
    return out, dense


def factory_facts():
    """authored_facts.py: production, transport class, density, grades and the rough world figures
    for the big commodities (absent: none)."""
    try:
        import authored_facts as f
    except ImportError:
        return {}, set(), set(), {}
    return f.FACTS, set(f.ELECTRONIC), set(f.FOOD), getattr(f, "WORLD", {})


def write_substances(content, used_keys, out_path):
    subs = content.SUBSTANCES
    lib_props, lib_dense = library_properties(LIBRARY / "substances.ron")
    facts, electronic, food, world = factory_facts()
    lines = [
        "#![enable(implicit_some)]",
        "// assets/data/authored_substances.ron",
        "// GENERATED by tools/data/gen_authored.py from tools/data/authored_content.py.",
        "// Each entry patches the library substance with the same id (or creates it).",
        "({",
    ]
    for s in sorted((subs[k] for k in used_keys), key=lambda s: s.id):
        f = []
        if not s.lib or s.rename:
            f.append(f"name: {q(s.name)}")
        f.append(f"formula: {q(s.formula)}")
        f.append(f"state: {s.state}")
        if not s.lib:
            mm = molar_mass(s.balance or s.formula)
            if mm:
                f.append(f"molar_mass_g_mol: {num(mm)}")
        props = list(s.props)
        if s.lib and props and all(p in TAGS for p in props):
            # tags (Medicine, Class) add to the library's properties instead of replacing them
            props = [p for p in lib_props.get(s.id, []) if p not in props] + props
        if props:
            f.append("properties: [" + ", ".join(props) + "]")
        if s.color:
            f.append(f"color_hex: {q(s.color)}")
        if s.desc:
            f.append(f"description: {q(s.desc)}")
        if s.wiki:
            f.append(f"references: {ref_entry(s.wiki)}")
        if s.stage:
            f.append(f"stage: {q(s.stage)}")
        # foundations for the factory stages: how much is made, how it travels, what it is sold as
        tons, un, dens = facts.get(s.key, (None, None, None))
        if tons:
            f.append(f"production_t_year: {num(tons)}")
        if s.key in world:
            f.append(f"world_t_year: {num(world[s.key])}")
        if un:
            f.append(f"transport_class: {q(un)}")
        if dens and not (s.lib and s.id in lib_dense):
            f.append(f"density_g_cm3: {num(dens)}")
        grades = [g for g, on in (("Food", s.key in food), ("Pharmaceutical", "IsMedicine" in s.props),
                                  ("Electronic", s.key in electronic)) if on]
        if grades:
            f.append("grades: [" + ", ".join(grades) + "]")
        lines.append(f"    {s.id}: (" + ", ".join(f) + "),")
    lines += ["})", ""]
    out_path.write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------------------
# Structure images for new substances
# --------------------------------------------------------------------------------------
def render_structures(content, used_keys, assets, force=False):
    from PIL import Image, ImageDraw, ImageFont
    try:
        from rdkit import Chem, RDLogger
        from rdkit.Chem.Draw import rdMolDraw2D
        RDLogger.DisableLog("rdApp.*")
    except ImportError:
        Chem = None
    out = LIBRARY / "structures"   # the pack copies the ones in play into assets/structures
    out.mkdir(parents=True, exist_ok=True)
    drawn = tiles = 0
    font_path = None
    for path in ("DejaVuSans-Bold.ttf", str(assets / "fonts" / "DejaVuSans.ttf"),
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/segoeuib.ttf",
                 "C:/Windows/Fonts/arialbd.ttf"):
        try:
            ImageFont.truetype(path, 30)
            font_path = path
            break
        except OSError:
            pass
    for k in sorted(used_keys):
        s = content.SUBSTANCES[k]
        p = out / f"{s.id}.png"
        # library entries usually ship a drawn structure; newly bound ones may not
        if s.lib and (p.exists() or 1000 < s.id <= 1118 or is_element(s.formula)):
            continue
        if p.exists() and not force:
            continue
        mol = Chem.MolFromSmiles(s.smiles) if (Chem and s.smiles) else None
        if mol is not None:
            d = rdMolDraw2D.MolDraw2DCairo(220, 220)
            o = d.drawOptions()
            o.setBackgroundColour((0, 0, 0, 0))
            o.bondLineWidth = 3
            o.updateAtomPalette({i: (1.0, 1.0, 1.0) for i in range(-1, 119)})
            d.DrawMolecule(mol)
            d.FinishDrawing()
            p.write_bytes(d.GetDrawingText())
            drawn += 1
            continue
        # Non-molecular (minerals, alloys, mixtures): a rounded tile in the substance's
        # colour with its name (the game prints the formula under the tile already).
        img = _tile(s, font_path)
        p.write_bytes(_png(img))
        tiles += 1
    print(f"structures: {drawn} molecules drawn, {tiles} formula tiles -> {out}")


def pages_needed(content, used, library_path):
    """In-play library substances with no text of their own whose library description the
    licence audit (audit_library.py) removed. Each needs a page in authored_pages.py."""
    lib = library_index(library_path)
    out = []
    for k in sorted(used):
        s = content.SUBSTANCES[k]
        if s.lib and not s.desc and s.id in lib and not lib[s.id]["desc"] and not is_element(s.formula):
            out.append(f"{k} ({s.name}, id {s.id})")
    return out


def is_element(formula):
    """Formulas the game shows as an element card instead of a structure picture."""
    return re.fullmatch(r"[A-Z][a-z]?[0-9]*", formula or "") is not None and len(atoms(formula)) == 1


def render_fallbacks(content, used_keys, assets, folder):
    """Name tiles for library substances in play. assets/structures usually already has a
    drawn structure for these; the installer only copies a tile where one is missing."""
    from PIL import ImageFont
    folder.mkdir(parents=True, exist_ok=True)
    font_path = None
    for path in ("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 str(assets / "fonts" / "DejaVuSans.ttf"), "C:/Windows/Fonts/arialbd.ttf"):
        try:
            ImageFont.truetype(path, 30)
            font_path = path
            break
        except OSError:
            pass
    n = 0
    for k in sorted(used_keys):
        s = content.SUBSTANCES[k]
        if not s.lib or 1000 < s.id <= 1118:     # elements get the periodic-table card
            continue
        (folder / f"{s.id}.png").write_bytes(_png(_tile(s, font_path)))
        n += 1
    print(f"fallback tiles: {n} -> {folder}")


def _tile(s, font_path):
    from PIL import Image, ImageDraw, ImageFont
    S = 220
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    col = s.color or "#9fb4d8"
    rgb = tuple(int(col[i:i + 2], 16) for i in (1, 3, 5))
    dr.rounded_rectangle([26, 26, S - 26, S - 26], radius=28, outline=(255, 255, 255, 235), width=5,
                         fill=rgb + (165,))
    box = S - 26 * 2 - 24
    mixture = True   # name tiles read better; the formula is printed under the tile in-game
    if not font_path:
        return img
    if mixture:
        # the name, word-wrapped, as large as fits
        words = s.name.split()
        for size in range(34, 12, -2):
            f = ImageFont.truetype(font_path, size)
            lines, cur = [], ""
            for w in words:
                t = (cur + " " + w).strip()
                if dr.textlength(t, font=f) <= box or not cur:
                    cur = t
                else:
                    lines.append(cur)
                    cur = w
            lines.append(cur)
            if len(lines) <= 3 and all(dr.textlength(l, font=f) <= box for l in lines):
                break
        lh = size * 1.15
        y = S / 2 - lh * len(lines) / 2
        for l in lines:
            w = dr.textlength(l, font=f)
            dr.text(((S - w) / 2, y), l, fill=(255, 255, 255, 255), font=f)
            y += lh
        return img
    # formula with subscript digits
    runs = re.findall(r"\d+|[^\d]+", s.formula)
    for size in range(40, 12, -2):
        big = ImageFont.truetype(font_path, size)
        small = ImageFont.truetype(font_path, int(size * 0.66))
        width = sum(dr.textlength(r, font=small if r.isdigit() else big) for r in runs)
        if width <= box:
            break
    x = (S - width) / 2
    y = S / 2 - size * 0.62
    for r in runs:
        f = small if r.isdigit() else big
        dr.text((x, y + (size * 0.42 if r.isdigit() else 0)), r, fill=(255, 255, 255, 255), font=f)
        x += dr.textlength(r, font=f)
    return img


def _png(img):
    import io
    b = io.BytesIO()
    img.save(b, format="PNG")
    return b.getvalue()


# --------------------------------------------------------------------------------------
def check_links(content, used_keys):
    """Batch-query the Wikipedia API for every article title we link to, following
    redirects, and list the ones that do not exist. Section anchors are not checked."""
    import json as _json
    import urllib.parse
    import urllib.request
    titles = {}
    for k in used_keys:
        s = content.SUBSTANCES[k]
        if s.wiki and not s.lib:
            titles.setdefault(_title(s.wiki), []).append(f"substance {k}")
    for e in content.EPOCHS:
        for r in e.reactions:
            if r.wiki:
                titles.setdefault(_title(r.wiki), []).append(f"reaction [{r.name}]")
    titles.pop(None, None)
    missing = []
    names = sorted(titles)
    for i in range(0, len(names), 50):
        batch = names[i:i + 50]
        q = urllib.parse.urlencode({"action": "query", "format": "json", "redirects": 1,
                                    "titles": "|".join(batch)})
        req = urllib.request.Request("https://en.wikipedia.org/w/api.php?" + q,
                                     headers={"User-Agent": "Curieosity-content-check/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as f:
                data = _json.load(f)["query"]
        except OSError as e:
            print(f"links: could not reach Wikipedia ({e}); nothing checked")
            return
        norm = {n["from"]: n["to"] for n in data.get("normalized", [])}
        for p in data.get("pages", {}).values():
            if "missing" in p or "invalid" in p:
                back = [t for t in batch if norm.get(t, t) == p.get("title")] or [p.get("title")]
                missing += back
        print(f"  checked {min(i + 50, len(names))}/{len(names)} titles", end="\r")
    print()
    for t in sorted(missing):
        print(f"MISSING ARTICLE  {t}  <- {', '.join(titles.get(t, ['?'])[:3])}")
    print(f"links: {len(names)} articles checked, {len(missing)} missing")
    check_pubchem(content, used_keys)


def check_pubchem(content, used_keys):
    """Ask PubChem for the title and formula of every compound page we link to, and list
    the ones whose formula is not the substance's (a link to the wrong compound)."""
    import json as _json
    import urllib.request
    cids = {}
    for k in used_keys:
        s = content.SUBSTANCES[k]
        m = re.search(r"pubchem\.ncbi\.nlm\.nih\.gov/compound/(\d+)", s.wiki or "")
        if m and not s.lib:
            cids[int(m.group(1))] = s
    if not cids:
        return
    wrong = []
    ids = sorted(cids)
    for i in range(0, len(ids), 100):
        batch = ",".join(map(str, ids[i:i + 100]))
        req = urllib.request.Request(
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{batch}/property/Title,MolecularFormula/JSON",
            headers={"User-Agent": "Curieosity-content-check/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as f:
                props = _json.load(f)["PropertyTable"]["Properties"]
        except OSError as e:
            print(f"pubchem: could not reach PubChem ({e}); nothing checked")
            return
        for pr in props:
            s = cids[pr["CID"]]
            # PubChem keeps many salts and mixed oxides as fragment sets ("[O].[Cr].[Cu]", or a
            # metal beside one free acid), so compare the elements other than hydrogen and the
            # carbon count, allowing whole multiples (one acid fragment against three ligands);
            # a wrong compound rarely shares both
            theirs = atoms_or_none(pr.get("MolecularFormula", ""))
            ours = atoms_or_none(s.balance or s.formula)
            if (theirs is None or ours is None or set(theirs) - {"H"} != set(ours) - {"H"}
                    or not _carbon_match(theirs.get("C", 0), ours.get("C", 0))):
                wrong.append(f"{s.key} ({s.name}, {s.formula}) -> CID {pr['CID']} is {pr.get('Title')} ({pr.get('MolecularFormula')})")
    for w in wrong:
        print("PUBCHEM MISMATCH  " + w)
    print(f"pubchem: {len(ids)} compound pages checked, {len(wrong)} with another formula")


def _carbon_match(a, b):
    """Equal carbon counts, or one a whole multiple of the other (a salt's ligands counted once)."""
    if a == b:
        return True
    return a > 0 and b > 0 and max(a, b) % min(a, b) == 0


def _title(wiki):
    """'Zinc_chloride#Uses' or a full article URL -> 'Zinc chloride'; curid links -> None."""
    if not wiki or "curid=" in wiki or (wiki.startswith("http") and "wikipedia.org" not in wiki):
        return None
    t = wiki.split("/wiki/", 1)[-1] if wiki.startswith("http") else wiki
    t = urllib_unquote(t.split("#", 1)[0]).replace("_", " ").strip()
    return t or None


def urllib_unquote(t):
    import urllib.parse
    return urllib.parse.unquote(t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate only, write nothing")
    ap.add_argument("--render", action="store_true", help="also draw structure PNGs for new substances")
    ap.add_argument("--force", action="store_true", help="with --render: redraw PNGs that already exist")
    ap.add_argument("--fallback", type=Path, help="with --render: also draw name tiles for the library "
                    "substances in play into this folder (to fill gaps in assets/structures)")
    ap.add_argument("--assets", type=Path, default=ROOT / "assets")
    ap.add_argument("--rebind", action="store_true", help="retry library binding for fresh ids")
    ap.add_argument("--pacing", action="store_true", help="print every milestone with its planner step")
    ap.add_argument("--check-links", action="store_true",
                    help="ask Wikipedia whether every article we link to exists (needs the network)")
    args = ap.parse_args()

    sys.path.insert(0, str(HERE))
    import authored_content as content
    library = LIBRARY / "substances.ron"
    if not library.exists():
        raise SystemExit(f"{library} is missing: the full scraped library lives in library/ (see pack_library.py)")
    resolve_ids(content, library, rebind=args.rebind)

    # reaction ids: numbered in order from AUTHORED_REACTION_BASE.
    # Saves hold substance ids, never reaction ids, so renumbering is harmless.
    i = AUTHORED_REACTION_BASE
    for ei, e in enumerate(content.EPOCHS):
        for r in e.reactions:
            r.epoch, r.id = ei, i
            i += 1

    errors, warnings, report, parsed, used = validate(content)
    # what gets a page: the substances in play, and the locked previews of later stages
    paged = set(used) | {k for k, s in content.SUBSTANCES.items() if s.stage}
    if not errors:
        errors += [f"{p}: no description (its library text was removed by the licence audit); "
                   "write one in authored_pages.py" for p in pages_needed(content, paged, library)]
    for w in warnings:
        print("warning:", w)
    if errors:
        for e in errors:
            print("ERROR:", e)
        raise SystemExit(f"\n{len(errors)} error(s); nothing written.")

    print(f"reactions            {report['reactions']} (all performable from the start kit)")
    for name, n in report["by_epoch"]:
        print(f"  {name:<28} {n}")
    print("by vessel            " + ", ".join(f"{k} {v}" for k, v in sorted(report["by_vessel"].items())))
    print(f"substances in play   {report['substances_in_play']}  "
          f"({report['library_bound']} from the library, {report['new_substances']} authored here)")
    print(f"mixture reactions    {report['inexact']} (not atom-balanced by design)")
    print(f"locked previews      {report['previews']} (pages for substances of later stages)")
    pacing = report["pacing"]
    print(f"pacing               {len(content.MILESTONES)} milestones over {pacing['era_steps']} era steps; "
          f"largest grant {max(len(m.grant) for m in content.MILESTONES)} (limit {MAX_GRANT}), "
          f"largest gap {max(g for _, _, g in pacing['gaps'])} (limit {MAX_MILESTONE_GAP})")
    if args.pacing:
        for step, at, m in pacing["events"]:
            what = ", ".join(VESSELS[p][0] for p in m.unlock)
            print(f"  step {step:5d}  era step {at:5d}  {m.on:<18} grant {len(m.grant):2d}"
                  + (f"  unlocks {what}" if what else ""))
    if args.check_links:
        check_links(content, paged)
    if args.check:
        return

    data = args.assets / "data"
    write_reactions(content, parsed, data / "authored_reactions.ron")
    write_substances(content, paged, data / "authored_substances.ron")
    print(f"wrote {data / 'authored_reactions.ron'}")
    print(f"wrote {data / 'authored_substances.ron'}")
    if args.render:
        render_structures(content, paged, args.assets, force=args.force)
        if args.fallback:
            render_fallbacks(content, paged, args.assets, args.fallback)
    # what the game ships follows from what the authored layer now uses
    import pack_library
    pack_library.pack()


if __name__ == "__main__":
    main()
