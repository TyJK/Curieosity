#!/usr/bin/env python3
"""
Curieosity substance compiler  (pipeline stage 1)
=================================================
Builds the game's substance table AND the shared id registry that the reaction
resolver consumes, so both halves of the pipeline agree on what "substance 4021" is.

Outputs
-------
  substances.ron   ->  Substances(HashMap<u32, Substance>)   (curated + elements + scraped)
  registry.json    ->  {"by_smiles": {canonical_smiles: id}, "hf": {id: dHf}}
                       the single source of truth for ids; resolve_reactions.py reads it.

ID BLOCK SCHEME (stable, non-colliding)
--------------------------------------
  1 .. 999      curated / hand-authored  (your existing 1-13; room for the foundational set)
  1000 .. 1199  elements                 (id = 1000 + atomic_number)
  2000 ..       scraped compounds        (deterministic by CAS)
  100000 ..     discovered products      (minted by resolve_reactions.py, not here)

Dedup is by canonical SMILES: an element or scraped compound whose structure already
exists lower in the table is skipped (so curated Carbon [C] wins over element Carbon).

Run:
    python3 compile_data.py --compounds ./tools/data/18_final_canon_compounds \
                            --elements  ./tools/data/03_element_complete \
                            --out assets/data
"""

import argparse
import html
import json
import re
from pathlib import Path

from rdkit import Chem
from rdkit import RDLogger

RDLogger.DisableLog("rdApp.*")

ELEMENT_BASE = 1000
SCRAPED_BASE = 2000
GAS_ELEMENTS = {"H", "He", "N", "O", "F", "Ne", "Cl", "Ar", "Kr", "Xe", "Rn"}
LIQUID_ELEMENTS = {"Br", "Hg"}
VALID_STATES = {"Solid", "Liquid", "Gas", "Plasma", "Aqueous", "SupercriticalFluid"}


def canon(smiles):
    if not smiles:
        return None
    try:
        m = Chem.MolFromSmiles(smiles)
        if m:
            return Chem.MolToSmiles(m, canonical=True, isomericSmiles=False)
    except Exception:
        pass
    return None


# --- cleaners ----------------------------------------------------------------------
_TAG_RE = re.compile(r"<[^>]+>")


def clean_name(raw):
    return html.unescape(_TAG_RE.sub("", raw)).strip() if raw else "Unknown"


def clean_formula(raw):
    return _TAG_RE.sub("", str(raw)).replace(" ", "").strip() if raw else ""


def k_to_c(k):
    return None if k is None else round(k - 273.15, 2)


def parse_formation_enthalpy(val):
    if val is None:
        return None
    if isinstance(val, dict):
        val = val.get("value_kj_mol")
    try:
        return None if val is None else float(val)
    except (TypeError, ValueError):
        return None


def cp_per_gram(cp, mm):
    if cp is None or not mm:
        return None
    try:
        return round(float(cp) / float(mm), 4)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def map_state(raw, default="Solid"):
    if not raw:
        return default
    s = str(raw).strip().capitalize()
    return s if s in VALID_STATES else default


# Placeholder strings that mean "no real value" -- don't surface these in the UI.
_JUNK_TEXT = {
    "no data", "no data available", "n/a", "na", "none", "not available",
    "not determined", "not applicable", "unknown", "-", "--",
}


def clean_text(raw, cap=None):
    """Strip tags/entities/whitespace; return None if empty or a junk placeholder.
    By default keeps the FULL text (no truncation). Pass `cap` only for short label
    fields (synonyms/uses) where a hard limit is wanted."""
    if not raw or not isinstance(raw, str):
        return None
    t = html.unescape(_TAG_RE.sub("", raw)).strip()
    if not t or t.lower() in _JUNK_TEXT:
        return None
    if cap and len(t) > cap:
        t = t[:cap - 1].rstrip() + "…"
    return t


def to_float(v):
    try:
        return None if v is None else float(v)
    except (TypeError, ValueError):
        return None


def collect_uses(econ, limit=6):
    """A few de-duplicated consumer + industrial uses as short strings."""
    out, seen = [], set()
    for u in (econ.get("consumer_uses") or []) + (econ.get("industrial_uses") or []):
        t = clean_text(u, cap=48)
        if t and t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
        if len(out) >= limit:
            break
    return out


# (source dict path, display label) for the external links we surface in the codex.
_REFERENCE_SOURCES = [
    (("cross_references", "wikipedia"), "Wikipedia"),
    (("cross_references", "pubchem"), "PubChem"),
    (("cross_references", "chebi"), "ChEBI"),
    (("cross_references", "wikidata"), "Wikidata"),
    (("media", "external_links", "nist_webbook"), "NIST"),
]


def _dig(doc, path):
    cur = doc
    for k in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def collect_synonyms(ident, limit=8):
    out, seen = [], set()
    for s in (ident.get("synonyms") or []):
        t = clean_text(s, cap=48)
        if t and t.lower() not in seen and t.lower() != str(ident.get("name", "")).lower():
            seen.add(t.lower())
            out.append(t)
        if len(out) >= limit:
            break
    return out


def collect_references(doc):
    """[(label, url)] for the known external links that are present + look like URLs."""
    out = []
    for path, label in _REFERENCE_SOURCES:
        url = _dig(doc, path)
        if isinstance(url, str) and url.strip().startswith("http"):
            out.append((label, url.strip()))
    return out


def enrichment_fields(doc):
    """Detail-panel + codex enrichment pulled from a compound's source JSON."""
    ident = doc.get("identity", {}) or {}
    props = doc.get("properties", {}) or {}
    mol = props.get("molecular", {}) or {}
    phys = props.get("physical", {}) or {}
    sensory = props.get("sensory", {}) or {}
    safety = doc.get("safety", {}) or {}
    ghs = safety.get("ghs", {}) or {}
    econ = doc.get("economics", {}) or {}
    return {
        "description": clean_text(ident.get("description")),
        "hazard_summary": clean_text(safety.get("summary") or ghs.get("summary")),
        "uses": collect_uses(econ),
        "logp": to_float(mol.get("logp")),
        "appearance": clean_text(sensory.get("appearance") or sensory.get("odour")
                                 or sensory.get("odor")),
        "synonyms": collect_synonyms(ident),
        "references": collect_references(doc),
    }


# Structural acid/base detection from SMILES. The classification tags almost never carry
# the literal word "base" (ChEBI classes bases by functional group -- amine, hydroxide,
# ...), so keyword-matching found acids but no bases. These SMARTS catch the real groups.
_ACID_SMARTS = [Chem.MolFromSmarts(s) for s in (
    "[CX3](=O)[OX2H1]",        # carboxylic acid
    "[SX4](=O)(=O)[OX2H1]",    # sulfonic acid
    "[PX4](=O)[OX2H1]",        # phosphonic / phosphoric acid
)]
_BASE_SMARTS = [Chem.MolFromSmarts(s) for s in (
    "[NX3;!$(NC=O);!$(N=*);!$(N#*);!$([N+])]",  # amine (excl. amide/imine/nitrile/charged)
    "[nX2]",                                     # pyridine-type aromatic basic N
    "[NX3]=[CX3][NX3]",                          # amidine / guanidine
)]


def structural_acid_base(smiles):
    """(is_acid, is_base) from functional groups. Safe on missing/invalid SMILES."""
    if not smiles:
        return False, False
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return False, False
    acid = any(m.HasSubstructMatch(p) for p in _ACID_SMARTS if p is not None)
    base = any(m.HasSubstructMatch(p) for p in _BASE_SMARTS if p is not None)
    return acid, base


def derive_properties(classification, smiles=None):
    props = []
    blob = {t.lower() for t in (classification.get("tags") or [])} | \
           {r.lower() for r in (classification.get("roles") or [])}
    if any("metal" in t for t in blob) and not any("nonmetal" in t for t in blob):
        props.append("IsMetal")
    acid, base = structural_acid_base(smiles)
    if acid or any("acid" in t for t in blob):
        props.append("IsAcid")
    if base or any("base" in t for t in blob):
        props.append("IsBase")
    return props


# --- source -> Substance dict ------------------------------------------------------
def substance_from_compound(doc, sid):
    ident = doc.get("identity", {})
    props = doc.get("properties", {})
    mol = props.get("molecular", {})
    phys = props.get("physical", {})
    thermo = props.get("thermodynamics", {})
    mm = mol.get("mass_g_mol")
    state = map_state(phys.get("state_25_k_1_atm"))
    cp = cp_per_gram(thermo.get("heat_capacity_j_mol_k"), mm)
    sol = None
    sw = phys.get("solubility_water") or {}
    if sw.get("value_g_l") is not None:
        try:
            sol = round(float(sw["value_g_l"]) / 10.0, 4)
        except (TypeError, ValueError):
            sol = None
    mp = phys.get("melting_point") or {}
    bp = phys.get("boiling_point") or {}
    return {
        "id": sid, "name": clean_name(ident.get("name")),
        "formula": clean_formula(ident.get("formula")), "state": state,
        "molar_mass_g_mol": float(mm) if mm else 0.0, "color_hex": None,
        "melting_point_c": k_to_c(mp.get("value_k")), "boiling_point_c": k_to_c(bp.get("value_k")),
        "density_g_cm3": phys.get("density_g_cm3"),
        "heat_capacity_solid_j_g_c": cp if state == "Solid" else None,
        "heat_capacity_liquid_j_g_c": cp if state == "Liquid" else None,
        "heat_capacity_gas_j_g_c": cp if state in ("Gas", "Plasma") else None,
        "enthalpy_fusion_kj_mol": None, "enthalpy_vaporization_kj_mol": None,
        "enthalpy_formation_kj_mol": parse_formation_enthalpy(thermo.get("enthalpy_formation_kj_mol")),
        "solubility_g_per_100ml_h2o": sol, "standard_potential_v": None,
        "half_life_seconds": None, "decay_product_id": None, "decay_particle_id": None,
        "properties": derive_properties(doc.get("classification", {}), ident.get("smiles")),
        **enrichment_fields(doc),
        "element_info": None,
    }


def element_isotopes_summary(doc):
    """A short, readable isotope line, e.g.
    '3 known isotopes; stable: 12C (98.9%), 13C (1.1%); 1 radioactive'."""
    iso = ((doc.get("nuclear_data", {}) or {}).get("isotopes")) or []
    if not iso:
        return None
    stable = [i for i in iso if i.get("is_stable")]

    def abundance_pct(i):
        """Normalized 0-100 abundance, or None. Some source rows are scaled x100
        (e.g. 5698.7 -> 56.987), so fold anything above 100 back down."""
        try:
            a = float(i.get("abundance_percent"))
        except (TypeError, ValueError):
            return None
        if a <= 0:
            return None
        while a > 100.0:
            a /= 100.0
        return a

    parts = []
    for i in sorted(stable, key=lambda x: abundance_pct(x) or 0.0, reverse=True)[:4]:
        sym = i.get("symbol") or str(i.get("mass_number", "?"))
        a = abundance_pct(i)
        parts.append(f"{sym} ({a:.1f}%)" if a is not None else sym)
    n_radio = len(iso) - len(stable)
    s = f"{len(iso)} known isotope" + ("s" if len(iso) != 1 else "")
    if parts:
        s += "; stable: " + ", ".join(parts)
    if n_radio > 0:
        s += f"; {n_radio} radioactive"
    return s


def element_references(name, z, doc):
    """Reference links for an element. Wikipedia + PubChem are constructed from the name
    and atomic number (reliable for elements even when the JSON has no link field), plus
    any external links the JSON does carry."""
    refs, labels = [], set()
    nm = (name or "").strip()
    if nm:
        refs.append(("Wikipedia", f"https://en.wikipedia.org/wiki/{nm.replace(' ', '_')}"))
        labels.add("Wikipedia")
    if z:
        refs.append(("PubChem", f"https://pubchem.ncbi.nlm.nih.gov/element/{int(z)}"))
        labels.add("PubChem")
    for path, label in _REFERENCE_SOURCES:
        url = _dig(doc, path)
        if label not in labels and isinstance(url, str) and url.strip().startswith("http"):
            refs.append((label, url.strip()))
            labels.add(label)
    return refs


def substance_from_element(doc):
    ident = doc.get("identity", {})
    symbol = ident.get("symbol", "?")
    z = ident.get("atomic_number")
    state = "Gas" if symbol in GAS_ELEMENTS else ("Liquid" if symbol in LIQUID_ELEMENTS else "Solid")
    props = ["IsMetal"] if (symbol not in GAS_ELEMENTS and symbol != "H"
                            and ident.get("block") in ("s", "d", "f")) else []

    # rich element physics, carried into the game so the detail panel has something to show
    qm = doc.get("quantum_mechanics", {}) or {}
    ions = qm.get("ionization_energies_kj_mol") or []
    radii = qm.get("atomic_radii_pm", {}) or {}
    disc = doc.get("discovery", {}) or {}
    narr = doc.get("narratives", {}) or {}
    name = clean_name(ident.get("name"))
    element_info = {
        "atomic_number": int(z),
        "atomic_weight": float(ident.get("standard_atomic_weight") or 0.0),
        "group": ident.get("group"),
        "period": ident.get("period"),
        "block": ident.get("block"),
        "electron_config": (qm.get("electron_configuration", {}) or {}).get("shorthand"),
        "electronegativity_pauling": (qm.get("electronegativity", {}) or {}).get("pauling"),
        "first_ionization_kj_mol": ions[0] if ions else None,
        "electron_affinity_kj_mol": qm.get("electron_affinity_kj_mol"),
        "atomic_radius_pm": radii.get("calculated") or radii.get("covalent_single")
                            or radii.get("van_der_waals"),
        "discoverer": disc.get("discoverer"),
        "discovery_year": disc.get("year"),
        # narrative + nuclear enrichment
        "overview": clean_text(narr.get("general_overview")),
        "discovery_story": clean_text(narr.get("discovery_story")),
        "isotopes_summary": element_isotopes_summary(doc),
        "magnetic_ordering": clean_text((qm.get("magnetic_properties", {}) or {})
                                        .get("magnetic_ordering")),
    }

    return {
        "id": ELEMENT_BASE + int(z), "name": name, "formula": symbol,
        "state": state, "molar_mass_g_mol": float(ident.get("standard_atomic_weight") or 0.0),
        "color_hex": None, "melting_point_c": None, "boiling_point_c": None, "density_g_cm3": None,
        "heat_capacity_solid_j_g_c": None, "heat_capacity_liquid_j_g_c": None,
        "heat_capacity_gas_j_g_c": None, "enthalpy_fusion_kj_mol": None,
        "enthalpy_vaporization_kj_mol": None, "enthalpy_formation_kj_mol": 0.0,
        "solubility_g_per_100ml_h2o": None, "standard_potential_v": None,
        "half_life_seconds": None, "decay_product_id": None, "decay_particle_id": None,
        "properties": props, "references": element_references(name, z, doc),
        "element_info": element_info,
    }, "[" + symbol + "]"   # elemental SMILES for the registry (e.g. [Fe], [Na], [C])


# --- CURATED SEED  (mirrors your committed substances.ron; SMILES added for matching) ---
def S(id, name, formula, state, mm, hf, smiles, props=None, **extra):
    base = {
        "id": id, "name": name, "formula": formula, "state": state,
        "molar_mass_g_mol": mm, "color_hex": None, "melting_point_c": None,
        "boiling_point_c": None, "density_g_cm3": None, "heat_capacity_solid_j_g_c": None,
        "heat_capacity_liquid_j_g_c": None, "heat_capacity_gas_j_g_c": None,
        "enthalpy_fusion_kj_mol": None, "enthalpy_vaporization_kj_mol": None,
        "enthalpy_formation_kj_mol": hf, "solubility_g_per_100ml_h2o": None,
        "standard_potential_v": None, "half_life_seconds": None,
        "decay_product_id": None, "decay_particle_id": None, "properties": props or [],
        "element_info": None,
    }
    base.update(extra)
    return base, smiles


CURATED_SEED = [
    S(1,  "Hydrogen",           "H2",        "Gas",    2.016,  None,   "[H][H]"),
    S(3,  "Carbon",             "C",         "Solid",  12.011, None,   "[C]"),
    S(4,  "Nitrogen",           "N2",        "Gas",    28.014, None,   "N#N"),
    S(5,  "Oxygen",             "O2",        "Gas",    31.999, None,   "O=O"),
    S(6,  "Sodium",             "Na",        "Solid",  22.990, None,   "[Na]", ["IsMetal"]),
    S(8,  "Water",              "H2O",       "Liquid", 18.015, -285.8, "O"),
    S(10, "Sodium Chloride",    "NaCl",      "Solid",  58.44,  None,   "[Na+].[Cl-]"),
    S(11, "Ammonia",            "NH3",       "Gas",    17.031, -45.9,  "N", ["IsBase"]),
    S(12, "Carbon Dioxide",     "CO2",       "Gas",    44.01,  -393.5, "O=C=O"),
    S(13, "Ammonium Carbonate", "(NH4)2CO3", "Solid",  96.09,  None,   "[NH4+].[NH4+].[O-]C([O-])=O"),
]

# --- EPOCH 0 (Fire & Ore) authored materials (block 100-599) ---------------------------
# Ores, lime, alloys, and the metallurgical gas. Metals (Cu/Sn/Zn/Fe) are element ids and
# come from the element pass; CO2 (12) and Water (8) are curated. smiles is left None: these
# are matched by id in the authored reactions, not via the scraped-SMILES registry.
EPOCH0_SEED = [
    S(100, "Charcoal",        "C",           "Solid", 12.011, None, None),  # element tile
    S(101, "Malachite",       "Cu2(OH)2CO3", "Solid", 221.12, None, "[Cu+2].[Cu+2].[O-]C(=O)[O-].[OH-].[OH-]"),
    S(102, "Cassiterite",     "SnO2",        "Solid", 150.71, None, "O=[Sn]=O"),
    S(103, "Hematite",        "Fe2O3",       "Solid", 159.69, None, "O=[Fe]O[Fe]=O"),
    S(104, "Limestone",       "CaCO3",       "Solid", 100.09, None, "[Ca+2].[O-]C(=O)[O-]"),
    S(105, "Sand",            "SiO2",        "Solid",  60.08, None, "O=[Si]=O"),
    S(106, "Calamine",        "ZnCO3",       "Solid", 125.42, None, "[Zn+2].[O-]C(=O)[O-]"),
    S(107, "Quicklime",       "CaO",         "Solid",  56.08, None, "[Ca]=O", ["IsBase"]),
    S(108, "Slaked Lime",     "Ca(OH)2",     "Solid",  74.09, None, "O[Ca]O", ["IsBase"]),
    S(109, "Carbon Monoxide", "CO",          "Gas",    28.01, -110.5, "[C-]#[O+]"),
    S(110, "Bronze",          "CuSn",        "Solid", 178.68, None, None, ["IsMetal"]),  # alloy: formula tile
    S(111, "Brass",           "CuZn",        "Solid", 128.92, None, None, ["IsMetal"]),  # alloy: formula tile
]

# --- EPOCH 1 (Antiquity & Iron Age) authored materials (block 200-299) -----------------
_TRISTEARIN = "CCCCCCCCCCCCCCCCCC(=O)OCC(OC(=O)CCCCCCCCCCCCCCCCC)COC(=O)CCCCCCCCCCCCCCCCC"
_CA_STEARATE = "CCCCCCCCCCCCCCCCCC(=O)[O-].CCCCCCCCCCCCCCCCCC(=O)[O-].[Ca+2]"
EPOCH1_SEED = [
    S(200, "Steel",        "Fe3C",         "Solid", 179.55, None, None, ["IsMetal"]),  # alloy: formula tile
    S(201, "Glass",        "Na2CaSi6O14",  "Solid", 478.50, None, None),               # amorphous: formula tile
    S(202, "Soda Ash",     "Na2CO3",       "Solid", 105.99, None, "[Na+].[Na+].[O-]C(=O)[O-]", ["IsBase"]),
    S(203, "Sugar",        "C6H12O6",      "Solid", 180.16, None, "OCC1OC(O)C(O)C(O)C1O"),
    S(205, "Ethanol",      "C2H6O",        "Liquid", 46.07, None, "CCO"),
    S(206, "Acetic Acid",  "C2H4O2",       "Liquid", 60.05, None, "CC(=O)O", ["IsAcid"]),
    S(207, "Tallow",       "C57H110O6",    "Solid", 891.50, None, _TRISTEARIN),
    S(208, "Soap",         "Ca(C18H35O2)2","Solid", 607.03, None, _CA_STEARATE, ["IsBase"]),
    S(209, "Glycerol",     "C3H8O3",       "Liquid", 92.09, None, "OCC(O)CO"),
    S(210, "Saltpeter",    "KNO3",         "Solid", 101.10, None, "[K+].[O-][N+](=O)[O-]"),
    S(211, "Black Powder", "C3K2N2O6S",    "Solid", 270.40, None, None),               # mixture: formula tile
]

# --- EPOCH 2 (Steam & Industry, ~1700-1850) authored materials (block 300-329) ---------
# The heavy-chemical era: sulfuric & hydrochloric acid, the Leblanc/Weldon chain, cement,
# and the voltaic pile (the Battery, whose discovery unlocks electrolysis). Several of these
# (sulfuric/hydrochloric acid, sodium sulfate, SO2) are real molecules that bridge to the
# scraped library once compiled -- see the bridge note in the 1b loop.
EPOCH2_SEED = [
    S(300, "Sulfuric Acid",      "H2SO4",   "Liquid",  98.08, -814.0, "OS(=O)(=O)O", ["IsAcid"],
      description="The 'king of chemicals' and for two centuries the single best measure of a nation's industrial might. A powerful, oily strong acid used to make fertilizer, refine metals, and produce almost every other industrial chemical.",
      references=[("Wikipedia", "https://en.wikipedia.org/wiki/Sulfuric_acid")]),
    S(301, "Hydrochloric Acid",  "HCl",     "Liquid",  36.46, -167.2, "Cl", ["IsAcid"],
      description="A strong acid, historically 'muriatic acid' or 'spirit of salt', first obtained as a nuisance byproduct of the Leblanc soda process. Used to pickle steel, acidify wells, and prepare countless chlorides.",
      references=[("Wikipedia", "https://en.wikipedia.org/wiki/Hydrochloric_acid")]),
    S(303, "Manganese Dioxide",  "MnO2",    "Solid",   86.94, None,   "O=[Mn]=O"),
    S(305, "Sulfur Dioxide",     "SO2",     "Gas",     64.07, -296.8, "O=S=O",
      description="A choking, acrid gas made by burning sulfur. The first step toward sulfuric acid and, much later, recognised as a major cause of acid rain."),
    S(306, "Sodium Sulfate",     "Na2SO4",  "Solid",  142.04, None,   "[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
    S(307, "Calcium Sulfide",    "CaS",     "Solid",   72.14, None,   "[Ca+2].[S-2]"),
    S(308, "Manganese Chloride", "MnCl2",   "Solid",  125.84, None,   "[Cl-].[Cl-].[Mn+2]"),
    S(309, "Bleaching Powder",   "CaOCl2",  "Solid",  126.98, None,   "[Ca+2].[Cl-].[O-]Cl",
      description="Chlorine absorbed into slaked lime, giving a stable dry powder that made bleaching (and later water disinfection) practical on an industrial scale."),
    S(310, "Cement",             "Ca3SiO5", "Solid",  228.32, None,   None,
      description="Portland cement: limestone and sand fused and ground to a powder that sets rock-hard when mixed with water. The binder that built the modern world in concrete."),
    S(311, "Battery",            "Zn-Cu",   "Solid",  128.90, None,   None,
      description="The voltaic pile: stacked copper and zinc discs separated by acid-soaked cloth, the first source of steady electric current. It turned electricity from a curiosity into a tool and opened the age of electrochemistry."),
]

# --- EPOCH 3 (Birth of Chemistry, ~1850-1920) authored materials (block 330-369) -------
# Electrolysis, catalysis, and the first synthetic organics. This is the bridge into the
# modern library: benzene, aniline, phenol, ammonia (curated 11), and the mineral acids are
# exactly the feedstocks the scraped reactions consume.
EPOCH3_SEED = [
    S(330, "Alumina",           "Al2O3",     "Solid",  101.96, -1675.7, "O=[Al]O[Al]=O"),
    S(331, "Sodium Hydroxide",  "NaOH",      "Solid",   40.00, -425.6,  "[Na+].[OH-]", ["IsBase"],
      description="Caustic soda: a strong, cheap base won by passing electricity through brine. It makes soap, paper, aluminium, and a huge share of all other chemistry.",
      references=[("Wikipedia", "https://en.wikipedia.org/wiki/Sodium_hydroxide")]),
    S(332, "Nitric Acid",       "HNO3",      "Liquid",  63.01, -174.1,  "O[N+](=O)[O-]", ["IsAcid"],
      description="A strong, oxidising acid. Once scarce, the Ostwald process made it cheap from ammonia, feeding fertilizers and explosives alike.",
      references=[("Wikipedia", "https://en.wikipedia.org/wiki/Nitric_acid")]),
    S(335, "Coal Tar",          "CxHy",      "Liquid", 100.00, None,    None,
      description="The black, sticky residue of making coke and coal gas. Once waste, it proved to be a treasure chest of aromatic molecules -- benzene, phenol, aniline -- that founded the dye and drug industries."),
    S(336, "Benzene",           "C6H6",      "Liquid",  78.11, 49.0,    "c1ccccc1",
      description="The archetypal aromatic ring, isolated by Faraday from coal tar. Its unusually stable six-carbon ring is the skeleton of a vast fraction of all organic chemistry.",
      references=[("Wikipedia", "https://en.wikipedia.org/wiki/Benzene")]),
    S(339, "Nitrobenzene",      "C6H5NO2",   "Liquid", 123.11, 12.5,    "O=[N+]([O-])c1ccccc1",
      description="Benzene with a nitro group bolted on: an almond-smelling oil that is the gateway to aniline and the synthetic-dye industry."),
    S(340, "Aniline",           "C6H7N",     "Liquid",  93.13, 31.0,    "Nc1ccccc1", ["IsBase"],
      description="The parent of synthetic dyes. Perkin's accidental mauveine, made from aniline in 1856, launched the entire coal-tar colour industry and modern organic chemistry with it.",
      references=[("Wikipedia", "https://en.wikipedia.org/wiki/Aniline")]),
    S(341, "Phenol",            "C6H6O",     "Solid",   94.11, -165.0,  "Oc1ccccc1", ["IsAcid"],
      description="Carbolic acid: a weakly acidic aromatic alcohol, the first surgical antiseptic and a building block for resins, plastics, and drugs.",
      references=[("Wikipedia", "https://en.wikipedia.org/wiki/Phenol")]),
    S(342, "Formaldehyde",      "CH2O",      "Gas",     30.03, -108.6,  "C=O",
      description="The simplest aldehyde: a pungent gas that preserves tissue and, cross-linked with phenol, forms the first true synthetic plastic."),
    S(343, "Bakelite",          "(C7H6O)n",  "Solid",  106.12, None,    None,
      description="The first fully synthetic plastic (1907): a hard, heat-proof, electrically insulating resin of phenol and formaldehyde. It gave the 20th century its telephones, radios, and switches.",
      references=[("Wikipedia", "https://en.wikipedia.org/wiki/Bakelite")]),
]

# --- EPOCH 4 (Modern, ~1920-now) signpost materials (block 370-399) ---------------------
# A light-touch set of famous 20th-century products that point into the scraped library
# rather than exhaustively authoring it. Ethylene/aspirin/nylon are real molecules that
# bridge; the polymers are non-molecular tiles.
EPOCH4_SEED = [
    S(370, "Ethylene",             "C2H4",         "Gas",     28.05, 52.4, "C=C",
      description="The workhorse of the petrochemical age: the simplest alkene and the feedstock for polyethylene, the most-produced plastic on Earth.",
      references=[("Wikipedia", "https://en.wikipedia.org/wiki/Ethylene")]),
    S(371, "Polyethylene",         "(C2H4)n",      "Solid",   28.05, None, None,
      description="Long chains of ethylene: the tough, cheap, waxy plastic of bags, bottles, and pipes -- the single most common plastic in the world."),
    S(372, "Salicylic Acid",       "C7H6O3",       "Solid",  138.12, None, "O=C(O)c1ccccc1O", ["IsAcid"]),
    S(373, "Aspirin",              "C9H8O4",       "Solid",  180.16, None, "CC(=O)Oc1ccccc1C(=O)O", ["IsAcid"],
      description="Acetylsalicylic acid: salicylic acid tamed with an acetyl group so it soothes the stomach. The first blockbuster synthetic drug and still one of the most used.",
      references=[("Wikipedia", "https://en.wikipedia.org/wiki/Aspirin")]),
    S(374, "Adipic Acid",          "C6H10O4",      "Solid",  146.14, None, "O=C(O)CCCCC(=O)O", ["IsAcid"]),
    S(375, "Hexamethylenediamine", "C6H16N2",      "Liquid", 116.21, None, "NCCCCCCN", ["IsBase"]),
    S(376, "Nylon",                "(C12H22N2O2)n","Solid",  226.32, None, None,
      description="Nylon-6,6: the first fully synthetic fibre, spun from coal, air, and water. It replaced silk in stockings and parachutes and founded the synthetic-textile industry.",
      references=[("Wikipedia", "https://en.wikipedia.org/wiki/Nylon")]),
]


# --- RON serialisation -------------------------------------------------------------
def ron_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def fmt_num(v):
    return repr(v) if isinstance(v, float) else str(v)


def ron_opt(v, kind="num"):
    if v is None:
        return "None"
    return f"Some({ron_str(v)})" if kind == "str" else f"Some({fmt_num(v)})"


def element_info_to_ron(ei):
    if not ei:
        return "None"
    return (
        "Some((\n"
        f"                atomic_number: {int(ei['atomic_number'])},\n"
        f"                atomic_weight: {fmt_num(float(ei.get('atomic_weight') or 0.0))},\n"
        f"                group: {ron_opt(ei.get('group'))},\n"
        f"                period: {ron_opt(ei.get('period'))},\n"
        f"                block: {ron_opt(ei.get('block'), 'str')},\n"
        f"                electron_config: {ron_opt(ei.get('electron_config'), 'str')},\n"
        f"                electronegativity_pauling: {ron_opt(ei.get('electronegativity_pauling'))},\n"
        f"                first_ionization_kj_mol: {ron_opt(ei.get('first_ionization_kj_mol'))},\n"
        f"                electron_affinity_kj_mol: {ron_opt(ei.get('electron_affinity_kj_mol'))},\n"
        f"                atomic_radius_pm: {ron_opt(ei.get('atomic_radius_pm'))},\n"
        f"                discoverer: {ron_opt(ei.get('discoverer'), 'str')},\n"
        f"                discovery_year: {ron_opt(ei.get('discovery_year'))},\n"
        f"                overview: {ron_opt(ei.get('overview'), 'str')},\n"
        f"                discovery_story: {ron_opt(ei.get('discovery_story'), 'str')},\n"
        f"                isotopes_summary: {ron_opt(ei.get('isotopes_summary'), 'str')},\n"
        f"                magnetic_ordering: {ron_opt(ei.get('magnetic_ordering'), 'str')},\n"
        "            ))"
    )


def ron_str_list(items):
    return "[" + ", ".join(ron_str(str(x)) for x in (items or [])) + "]"


def ron_pair_list(pairs):
    return "[" + ", ".join(f"({ron_str(str(a))}, {ron_str(str(b))})" for a, b in (pairs or [])) + "]"


def substance_to_ron(s):
    f = lambda k, kind="num": ron_opt(s[k], kind)
    # .get-based accessor for the newer enrichment fields, so substances built before
    # these keys existed (curated seed, elements) still serialize as None/[].
    g = lambda k, kind="num": ron_opt(s.get(k), kind)
    return (
        "(\n"
        f"            id: {s['id']},\n"
        f"            name: {ron_str(s['name'])},\n"
        f"            formula: {ron_str(s['formula'])},\n"
        f"            state: {s['state']},\n"
        f"            molar_mass_g_mol: {fmt_num(float(s['molar_mass_g_mol']))},\n"
        f"            color_hex: {f('color_hex','str')},\n"
        f"            melting_point_c: {f('melting_point_c')},\n"
        f"            boiling_point_c: {f('boiling_point_c')},\n"
        f"            density_g_cm3: {f('density_g_cm3')},\n"
        f"            heat_capacity_solid_j_g_c: {f('heat_capacity_solid_j_g_c')},\n"
        f"            heat_capacity_liquid_j_g_c: {f('heat_capacity_liquid_j_g_c')},\n"
        f"            heat_capacity_gas_j_g_c: {f('heat_capacity_gas_j_g_c')},\n"
        f"            enthalpy_fusion_kj_mol: {f('enthalpy_fusion_kj_mol')},\n"
        f"            enthalpy_vaporization_kj_mol: {f('enthalpy_vaporization_kj_mol')},\n"
        f"            enthalpy_formation_kj_mol: {f('enthalpy_formation_kj_mol')},\n"
        f"            solubility_g_per_100ml_h2o: {f('solubility_g_per_100ml_h2o')},\n"
        f"            standard_potential_v: {f('standard_potential_v')},\n"
        f"            half_life_seconds: {f('half_life_seconds')},\n"
        f"            decay_product_id: {f('decay_product_id')},\n"
        f"            decay_particle_id: {f('decay_particle_id')},\n"
        f"            properties: [{', '.join(s['properties'])}],\n"
        f"            description: {g('description','str')},\n"
        f"            hazard_summary: {g('hazard_summary','str')},\n"
        f"            uses: {ron_str_list(s.get('uses'))},\n"
        f"            logp: {g('logp')},\n"
        f"            appearance: {g('appearance','str')},\n"
        f"            synonyms: {ron_str_list(s.get('synonyms'))},\n"
        f"            references: {ron_pair_list(s.get('references'))},\n"
        f"            element_info: {element_info_to_ron(s.get('element_info'))},\n"
        "        )"
    )


def write_substances_ron(subs, path):
    lines = ["({"]
    for sid in sorted(subs):
        lines.append(f"    {sid}: {substance_to_ron(subs[sid])},")
    lines.append("})")
    path.write_text("\n".join(lines), encoding="utf-8")


# --- driver ------------------------------------------------------------------------
def register(registry, smiles, sid, hf=None):
    cs = canon(smiles)
    if cs and cs not in registry["by_smiles"]:
        registry["by_smiles"][cs] = sid
    if hf is not None:
        registry["hf"][str(sid)] = hf
    return cs


_SYM_RE = re.compile(r"[A-Z][a-z]?")


def formula_symbols(formula):
    return set(_SYM_RE.findall(formula or ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compounds", type=Path)
    ap.add_argument("--elements", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--merge-discovered", type=Path,
                    help="a discovered_substances.ron to append -> writes substances_full.ron "
                         "(so you can refresh without re-running the reaction resolver)")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    subs = {}
    registry = {"by_smiles": {}, "hf": {}}
    seen_smiles = set()

    # 1) curated seed (verbatim ids)
    curated_element = {}  # element symbol -> curated substance id (for single-element curated items)
    for s, smi in CURATED_SEED:
        subs[s["id"]] = s
        cs = register(registry, smi, s["id"], s["enthalpy_formation_kj_mol"])
        if cs:
            seen_smiles.add(cs)
        syms = formula_symbols(s["formula"])
        if len(syms) == 1:
            curated_element[next(iter(syms))] = s["id"]

    # 1b) Epoch-0 authored materials. Registered so the renderer can draw the ones with a
    #     SMILES (oxides/carbonates); alloys and Charcoal have None and stay formula/element
    #     tiles. NOT added to curated_element (Charcoal must not shadow Carbon).
    for s, smi in EPOCH0_SEED + EPOCH1_SEED + EPOCH2_SEED + EPOCH3_SEED + EPOCH4_SEED:
        subs[s["id"]] = s
        # Register AND claim the canonical SMILES (add to seen_smiles) so this authored id
        # becomes the ONE id for this molecule. When a scraped compound later has the same
        # canonical SMILES it is deduped (step 3 skips it) and every scraped reaction that
        # uses it resolves to THIS authored id -- that's the automatic bridge from the
        # authored epochs into the ~95k modern library (ethanol, benzene, ammonia, the
        # mineral acids, ...). Alloys/mixtures/polymers have smi=None and are unaffected.
        cs = register(registry, smi, s["id"], s.get("enthalpy_formation_kj_mol"))
        if cs:
            seen_smiles.add(cs)

    # 2) elements. If a curated substance already represents this element (e.g. H2 for H),
    #    enrich THAT one with the atomic data and skip the duplicate atomic tile.
    n_elem = n_elem_merged = 0
    for f in sorted((args.elements.glob("*.json") if args.elements and args.elements.exists() else [])):
        doc = json.loads(f.read_text(encoding="utf-8"))
        sub, smi = substance_from_element(doc)
        sym = doc.get("identity", {}).get("symbol")
        if sym in curated_element:
            cid = curated_element[sym]
            subs[cid]["element_info"] = sub["element_info"]  # enrich, don't duplicate
            subs[cid]["references"] = sub.get("references", [])  # carry element links too
            n_elem_merged += 1
            continue
        cs = canon(smi)
        if cs and cs in seen_smiles:
            n_elem_merged += 1
            continue
        subs[sub["id"]] = sub
        if cs:
            seen_smiles.add(cs)
            registry["by_smiles"][cs] = sub["id"]
        n_elem += 1

    # 2b) Charcoal (100) inherits Carbon's element data -- it *is* carbon. This makes it an
    #     element tile everywhere (no compound-structure lookup) and gives it real atomic
    #     info, per the "let charcoal inherit carbon" call.
    if 100 in subs and subs.get(3, {}).get("element_info"):
        subs[100]["element_info"] = subs[3]["element_info"]
        subs[100]["references"] = subs[3].get("references", [])

    # 3) scraped compounds (2000+, by CAS), dedup by structure
    next_id = SCRAPED_BASE
    n_comp = n_dup = 0
    comp_docs = []
    for f in (sorted(args.compounds.glob("*.json")) if args.compounds and args.compounds.exists() else []):
        doc = json.loads(f.read_text(encoding="utf-8"))
        comp_docs.append((doc.get("identity", {}).get("cas_rn", f.stem), doc))
    for cas, doc in sorted(comp_docs, key=lambda x: str(x[0])):
        cs = canon(doc.get("identity", {}).get("smiles"))
        if cs and cs in seen_smiles:
            n_dup += 1
            continue
        sub = substance_from_compound(doc, next_id)
        subs[next_id] = sub
        if cs:
            seen_smiles.add(cs)
            registry["by_smiles"][cs] = next_id
            if sub["enthalpy_formation_kj_mol"] is not None:
                registry["hf"][str(next_id)] = sub["enthalpy_formation_kj_mol"]
        next_id += 1
        n_comp += 1

    write_substances_ron(subs, args.out / "substances.ron")
    (args.out / "registry.json").write_text(json.dumps(registry), encoding="utf-8")

    # authored_smiles.json: id -> SMILES for authored materials, keyed by id so the renderer
    # can draw them even when a common one (SiO2, ZnCO3, ...) collides with a scraped SMILES
    # in the registry and gets shadowed there.
    authored_smiles = {str(s["id"]): smi for s, smi in
                       EPOCH0_SEED + EPOCH1_SEED + EPOCH2_SEED + EPOCH3_SEED + EPOCH4_SEED if smi}
    (args.out / "authored_smiles.json").write_text(json.dumps(authored_smiles), encoding="utf-8")

    print(f"substances.ron: {len(subs):,} "
          f"(curated {len(CURATED_SEED)} + elements {n_elem} + scraped {n_comp}; "
          f"{n_elem_merged} atomic dupes merged into curated, {n_dup} scraped dup-skipped)")
    print(f"registry.json:  {len(registry['by_smiles']):,} SMILES -> id, "
          f"{len(registry['hf']):,} with formation enthalpy")

    # Optional: fold an existing discovered_substances.ron back in without re-resolving.
    if args.merge_discovered and Path(args.merge_discovered).exists():
        base = (args.out / "substances.ron").read_text(encoding="utf-8").rstrip()
        head = base[:base.rfind("})")].rstrip()
        disc = Path(args.merge_discovered).read_text(encoding="utf-8").strip()
        inner = disc[disc.find("{") + 1: disc.rfind("}")].strip()
        (args.out / "substances_full.ron").write_text(
            head + "\n" + inner + "\n})", encoding="utf-8")
        print(f"substances_full.ron: base + discovered from {args.merge_discovered}")


if __name__ == "__main__":
    main()