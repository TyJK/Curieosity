"""
Curieosity's industrial chemistry: the substances the world makes by the tonne, each with
the route that makes it.

The list comes from the canon set (tools/data/18_final_canon_compounds): US EPA Chemical
Data Reporting production volumes, taken in order from the largest down to about 10
tonnes a year, keeping the single substances that have a Wikipedia article and aren't in
the game yet. Every entry here is written for Curieosity: its own description and a named,
balanced reaction that is the real industrial route (or the classic one), in the era it
belongs to.

Imported at the end of authored_content.py, after the tiers, so every vessel and every
earlier key is in place. Kept in its own files because authored_content.py is near 4,000
lines: authored_canon.py, then authored_canon_2.py and on, each importing the next.

Library binding. S(..., lib=N) binds to library entry N only when that entry is this very
compound (same PubChem record and formula, checked when the entry was written): the game
then uses its measured data and structure picture, under the name, formula, description
and Wikipedia page given here. lib=0 gives a fresh id; pass the SMILES so gen_authored.py
--render can draw the structure.
"""

from authored_content import X, E3, E4, E5, E6
from authored_content import R as _R
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST,
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)

CANON = {}    # CAS number -> key, for every substance taken from the canon set


def S(cas, key, name, formula, state, wiki, desc, *, lib=0, smiles=None, props=(), color=None):
    """A substance. wiki: a Wikipedia curid number or an article title."""
    if isinstance(wiki, int):
        wiki = f"https://en.wikipedia.org/?curid={wiki}"
    X(key, name, formula, state, desc, wiki, id=lib, lib=bool(lib), smiles=smiles, props=props,
      color=color, rename=bool(lib))
    if cas:
        CANON[cas] = key


OURS = []    # every reaction written in these files, for settle_eras()

# Milestones for the industrial chemistry above: messages only (no grants, no vessels), placed
# so no stretch of the eras goes MAX_MILESTONE_GAP planner steps without one.
import authored_content as _C  # noqa: E402
from gen_authored import Milestone  # noqa: E402
_C.MILESTONES += [
    Milestone("Perborate", message="Henkel's Persil (1907): perborate and silicate, the first washing powder that bleached by itself."),
    Milestone("MDI", message="Otto Bayer's polyurethanes (1937): two isocyanate groups meet a polyol, and foam rises in the mould."),
    Milestone("TwoFourD", message="2,4-D (1946), the first selective weedkiller: it kills the weeds and spares the wheat."),
    Milestone("NVP", message="Walter Reppe's acetylene chemistry under pressure opens the vinyl monomers. Polyvinylpyrrolidone even stood in for blood plasma in the war."),
    Milestone("EDTA", message="EDTA (Ferdinand Munz, 1935): a molecule that wraps around a metal ion and won't let go."),
    Milestone("DEET", message="DEET (1946): the US Army's answer to jungle mosquitoes, still the standard insect repellent."),
    Milestone("RDX", message="RDX, a medicine in 1898, became Britain's 'Research Department Explosive' in the Second World War."),
    Milestone("TMSi", message="Tetramethylsilane becomes the zero of the NMR scale (1958): chemists read molecules by their nuclei."),
    Milestone("ECA", message="Harry Coover's cyanoacrylate (1951) was rejected for sticking to everything; in 1958 it went on sale as superglue."),
    Milestone("DTPA", message="Gadolinium held tight in DTPA (1988): the first MRI contrast agent lights up blood vessels and tumours."),
    Milestone("Sucralose", message="Sucralose (1976): a student told to 'test' a chlorinated sugar thought he had been told to taste it."),
    Milestone("Galaxolide", message="Perfume goes synthetic: Galaxolide (1965), Hedione (1962) and their kin are now the backbone of every fragrance, from fine perfume to washing powder."),
    Milestone("Prontosil", message="Gerhard Domagk's red dye Prontosil (1932) cured streptococcal infections; the dye half turned out not to matter. The sulfa drugs were the first antibacterials."),
    Milestone("MTBE", message="Unleaded petrol (1975 on) needs its octane from somewhere: the refinery ethers fill the gap."),
    Milestone("Farnesene", message="Synthetic biology: engineered yeast turns cane sugar into farnesene, a jet fuel and a rubber monomer."),
    Milestone("PMDA", message="Kapton (DuPont, 1960s): polyimide film from pyromellitic dianhydride shrugs off 400 C and near absolute zero, and flew on Apollo."),
    Milestone("R134a", message="The Montreal Protocol (1987) phases out the ozone-eating CFCs; HFC-134a cools the world's cars and fridges instead."),
]


def R(name, equation, process, desc, *, wiki=None, **kw):
    """A reaction. wiki: a Wikipedia curid number or an article title."""
    if isinstance(wiki, int):
        wiki = f"https://en.wikipedia.org/?curid={wiki}"
    r = _R(name, equation, process, desc, wiki=wiki, **kw)
    OURS.append(r)
    return r


def settle_eras():
    """Move any reaction written here into the era where all its inputs first exist, so the
    tech tree never shows a step in an era before the one that makes what it needs. The era
    each route is written in is when the process began; this only ever moves it later.
    Laboratory reactions count as available in the era of their own inputs."""
    import re as _re
    from authored_content import EPOCHS, START, MILESTONES
    from gen_authored import VESSELS, START_PROCESSES
    lab = len(EPOCHS) - 1
    term = _re.compile(r"^(?:\d+\s+)?(\S+)$")

    def keys(side):
        return [term.match(t.strip()).group(1) for t in side.split(" + ")]
    sides = {}
    for e in EPOCHS:
        for r in e.reactions:
            lhs, rhs = r.equation.split(" -> ")
            sides[id(r)] = (keys(lhs) + ([r.cat] if r.cat else []), keys(rhs))
    ours = {id(r) for r in OURS}
    moved = 0
    def runs(process, vessels):
        """Earliest era any vessel that can run this process is unlocked."""
        _, fam, tier, _ = VESSELS[process]
        ts = [vessels[p] for p, (_, f, t, _) in VESSELS.items() if f == fam and t >= tier and p in vessels]
        return min(ts) if ts else None

    while True:
        avail = {k: 0 for k in START}
        vessels = {p: 0 for p in START_PROCESSES}
        changed = True
        while changed:
            changed = False
            for m in MILESTONES:
                if m.on in avail:
                    for g in m.grant:
                        if avail.get(g, 99) > avail[m.on]:
                            avail[g] = avail[m.on]
                            changed = True
                    for p in m.unlock:
                        if vessels.get(p, 99) > avail[m.on]:
                            vessels[p] = avail[m.on]
                            changed = True
            for ei, e in enumerate(EPOCHS):
                for r in e.reactions:
                    ins, outs = sides[id(r)]
                    v = runs(r.process, vessels)
                    if v is not None and all(k in avail for k in ins):
                        t = max([0 if ei == lab else ei, v] + [avail[k] for k in ins])
                        for k in outs:
                            if avail.get(k, 99) > t:
                                avail[k] = t
                                changed = True
        moves = []
        for ei, e in enumerate(EPOCHS[:lab]):
            for r in e.reactions:
                if id(r) in ours:
                    need = max([runs(r.process, vessels) or ei] + [avail.get(k, ei) for k in sides[id(r)][0]])
                    if need > ei:
                        moves.append((r, e, EPOCHS[need]))
        if not moves:
            return moved
        for r, src, dst in moves:
            src.reactions.remove(r)
            dst.reactions.append(r)
            moved += 1


# ======================================================================================
# 1. Over 10,000 tonnes a year
# ======================================================================================
# --- intermediates the canon set lacks, needed by the routes below ---------------------
S(None, "Isobutylene", "Isobutylene", "C4H8", "Gas", "Isobutylene",
  "The branched four-carbon alkene: the building block of butyl rubber, of antioxidants, and of the petrol additives MTBE and ETBE.",
  smiles="C=C(C)C")
S(None, "AcrylicAcid", "Acrylic acid", "C3H4O2", "Liquid", "Acrylic_acid",
  "The simplest unsaturated carboxylic acid, with an acrid smell. Most of it becomes acrylate esters for paints and adhesives, or the superabsorbent polymer in nappies.",
  smiles="C=CC(=O)O", props=("IsAcid", "IsMonomer"))
S(None, "PG", "Propylene glycol", "C3H8O2", "Liquid", "Propylene_glycol",
  "A sweetish, harmless diol: antifreeze for food plants and aircraft de-icing, the base of stage fog and e-cigarette liquid, and a food additive (E1520).",
  smiles="CC(O)CO")
S(None, "Isoamylene", "2-Methyl-2-butene", "C5H10", "Liquid", 22111939,
  "A branched five-carbon alkene from the cracker's C5 cut, etherified with methanol for petrol.",
  lib=6160)

# --- the canon substances ------------------------------------------------------------
S("12004-88-5", "C3A", "Tricalcium aluminate", "Ca3Al2O6", "Solid", 9270912,
  "The clinker phase that makes fresh cement flash-set, which is why gypsum is ground in with it. It is also the part of hardened concrete that sulfate water attacks.",
  lib=2946)
S("1634-04-4", "MTBE", "Methyl tert-butyl ether", "C5H12O", "Liquid", 391568,
  "MTBE was blended into petrol from 1979 to raise its octane once lead was phased out. It leaked from tanks into groundwater, and much of the US had banned it by 2006.",
  lib=4014)
S("10049-04-4", "ClO2", "Chlorine dioxide", "ClO2", "Gas", 458673,
  "A yellow-green gas too explosive to ship, so it is made where it is used. It bleaches most of the world's wood pulp without the dioxins chlorine left behind, and disinfects drinking water.",
  lib=2077, props=("IsTransient",))
S("141-32-2", "ButylAcrylate", "Butyl acrylate", "C7H12O2", "Liquid", 48823927,
  "The soft partner in acrylic paints, adhesives and caulks: copolymerised with methyl methacrylate, it decides how flexible the film is.",
  lib=3623)
S("592-41-6", "Hexene", "1-Hexene", "C6H12", "Liquid", 2669449,
  "A linear alpha-olefin. A few percent copolymerised into polyethylene makes the tough, stretchy linear low-density film of bags and wraps.",
  lib=6768)
S("75-56-9", "PO", "Propylene oxide", "C3H6O", "Liquid", 600925,
  "A volatile three-membered ring. Opened with glycerol or sugar it builds the polyether polyols of polyurethane foam; opened with water, propylene glycol.",
  lib=7907)
S("75-91-2", "TBHP", "tert-Butyl hydroperoxide", "C4H10O2", "Liquid", 19492220,
  "A hydroperoxide that keeps far better than most: the oxygen donor of propylene oxide plants, and of Sharpless's Nobel-winning asymmetric epoxidation.",
  lib=5408)
S("75-65-0", "tBuOH", "tert-Butanol", "C4H10O", "Liquid", 2006095,
  "The simplest tertiary alcohol, a solid just below room temperature: a solvent, a petrol additive, and a clean source of isobutylene.",
  lib=7912)
S("75-86-5", "ACH", "Acetone cyanohydrin", "C4H7NO", "Liquid", 9861171,
  "Acetone joined to hydrogen cyanide: the start of most methyl methacrylate, and so of Perspex and Plexiglas. It gives its cyanide back readily, which makes it treacherous to handle.",
  smiles="CC(C)(O)C#N")
S("7783-18-8", "ATS", "Ammonium thiosulfate", "(NH4)2S2O3", "Solid", 32581528,
  "The rapid fixer of photography, dissolving the unexposed silver halide. Most now goes onto fields as a clear liquid fertiliser of nitrogen and sulfur.",
  lib=8135)
S("101-77-9", "MDA", "4,4'-Methylenedianiline", "C13H14N2", "Solid", 31504551,
  "Two anilines bridged by a single carbon from formaldehyde. Nearly all of it is phosgenated into MDI.",
  lib=2115)
S("101-68-8", "MDI", "Methylene diphenyl diisocyanate", "C15H10N2O2", "Solid", 1727620,
  "MDI, the isocyanate made in the largest amounts. With polyols it makes rigid foam insulation, shoe soles, car parts and spray coatings.",
  lib=2113)
S("141-43-5", "MEA", "Ethanolamine", "C2H7NO", "Liquid", 1001091,
  "The gas sweetener. Its solution soaks carbon dioxide and hydrogen sulfide out of natural gas and flue gas, then gives them up again when heated.",
  lib=3625)
S("105-59-9", "MDEA", "N-Methyldiethanolamine", "C5H13NO2", "Liquid", 17403365,
  "The gas-treating amine that grabs hydrogen sulfide faster than carbon dioxide, so a refinery can strip one and leave the other.",
  lib=2335)
S("108-01-0", "DMAE", "2-(Dimethylamino)ethanol", "C4H11NO", "Liquid", 1918853,
  "A building block for acrylate monomers, a catalyst for epoxy and polyurethane, and a corrosion inhibitor for boilers.",
  lib=2499)
S("17438-89-0", "Decene", "1-Decene", "C10H20", "Liquid", 14039665,
  "Ten carbons with a double bond at the end. Joined three at a time it makes polyalphaolefin, the base oil of synthetic motor oils.",
  lib=8542)
S("112-41-4", "Dodecene", "1-Dodecene", "C12H24", "Liquid", 37386074,
  "A twelve-carbon alpha-olefin, turned into the alcohols and sulfonates of detergents.",
  lib=2714)
S("112-88-9", "Octadecene", "1-Octadecene", "C18H36", "Liquid", 4663377,
  "An eighteen-carbon alpha-olefin for oil-field chemicals and paper sizing, and the high-boiling solvent in which quantum dots are grown.",
  lib=2732)
S("3268-49-3", "Methional", "Methional", "C4H8OS", "Liquid", 41145502,
  "The smell of boiled potatoes, and the industrial step on the way to methionine, the amino acid added to animal feed.",
  lib=5327)
S("994-05-8", "TAME", "tert-Amyl methyl ether", "C6H14O", "Liquid", 24767728,
  "MTBE's five-carbon cousin, blended into petrol to raise its octane.",
  lib=8974)
S("10294-66-3", "K2S2O3", "Potassium thiosulfate", "K2S2O3", "Aqueous", 68911744,
  "A clear liquid fertiliser that feeds potassium and sulfur, and slows the soil's conversion of ammonium into nitrate.",
  lib=2215)
S("120-61-6", "DMT", "Dimethyl terephthalate", "C10H10O4", "Solid", 2004090,
  "Easier to purify than terephthalic acid itself, it was the original feed for polyester: ICI's Terylene and DuPont's Dacron.",
  lib=2894)
S("105-08-8", "CHDM", "1,4-Cyclohexanedimethanol", "C8H16O2", "Solid", 31632219,
  "Eastman's diol. Put in place of some ethylene glycol it makes PETG and the clear, tough copolyesters of water bottles and medical trays.",
  lib=2321)
S("107-15-3", "EDA", "Ethylenediamine", "C2H8N2", "Liquid", 2955396,
  "The simplest diamine: the backbone of EDTA and other chelating agents, and a hardener for epoxy.",
  lib=2442)
S("107-39-1", "Diisobutylene", "2,4,4-Trimethyl-1-pentene", "C8H16", "Liquid", 78195155,
  "Isobutylene dimerised (diisobutylene). Hydrogenated it gives isooctane, the 100-octane reference fuel, and it is the start of octylphenol.",
  lib=2452)
S("108-77-0", "CyanuricChloride", "Cyanuric chloride", "C3Cl3N3", "Solid", 2484579,
  "Three reactive chlorines on a triazine ring, swapped one at a time to build atrazine, reactive dyes and optical brighteners.",
  lib=2526)
S("110-88-3", "Trioxane", "1,3,5-Trioxane", "C3H6O3", "Solid", 3056960,
  "Three formaldehydes joined in a ring: the monomer of acetal plastic (polyoxymethylene), and the solid fuel of military ration heaters.",
  lib=2611)
S("128-39-2", "DTBP26", "2,6-Di-tert-butylphenol", "C14H22O", "Solid", 3656926,
  "Two bulky groups guard the OH, making a radical trap that keeps fuels, oils and plastics from oxidising.",
  lib=3218)
S("96-33-3", "MethylAcrylate", "Methyl acrylate", "C4H6O2", "Liquid", 12406414,
  "The smallest acrylate ester: copolymerised into acrylic fibres, and the starting point for other acrylates.",
  lib=8861)
S("2439-35-2", "DMAEA", "2-(Dimethylamino)ethyl acrylate", "C7H13NO2", "Liquid", 57188455,
  "Quaternised with methyl chloride, it becomes the cationic monomer of the flocculants that clear water and dewater sewage sludge.",
  lib=4648)
S("76-13-1", "CFC113", "1,1,2-Trichlorotrifluoroethane", "C2Cl3F3", "Liquid", 17206806,
  "Freon 113, a non-flammable solvent that cleaned circuit boards until the 1987 Montreal Protocol phased it out for destroying stratospheric ozone.",
  smiles="FC(F)(Cl)C(F)(Cl)Cl")
S("354-58-5", "CFC113a", "1,1,1-Trichloro-2,2,2-trifluoroethane", "C2Cl3F3", "Liquid", 42166815,
  "CFC-113's isomer, made on the way to refrigerants and pesticides. Its unexpected rise in the atmosphere was spotted in 2014.",
  lib=5472)
S("576-26-1", "DMP26", "2,6-Dimethylphenol", "C8H10O", "Solid", 3411364,
  "2,6-Xylenol. Coupled by oxidation it makes polyphenylene oxide, which GE blended with polystyrene as Noryl (1966).",
  smiles="Cc1cccc(C)c1O")
S("75-34-3", "DCE11", "1,1-Dichloroethane", "C2H4Cl2", "Liquid", 3122764,
  "Made mostly to be chlorinated on to methyl chloroform.",
  lib=7894)
S("71-55-6", "TCA111", "1,1,1-Trichloroethane", "C2H3Cl3", "Liquid", 302493,
  "Methyl chloroform: the solvent of correction fluid and metal degreasers, phased out under the Montreal Protocol.",
  lib=7692)
S("7791-25-5", "SO2Cl2", "Sulfuryl chloride", "SO2Cl2", "Liquid", 2682431,
  "A fuming liquid that hands out chlorine on demand, for chlorinating organic compounds in the lab and the plant.",
  lib=8169)
S("78-87-5", "DCP12", "1,2-Dichloropropane", "C3H6Cl2", "Liquid", 27731849,
  "A by-product of making propylene oxide: once a soil fumigant, now mostly a feed for perchloroethylene.",
  lib=8197)
S("79-00-5", "TCE112", "1,1,2-Trichloroethane", "C2H3Cl3", "Liquid", 4029717,
  "Made on the way to vinylidene chloride, the monomer of Saran wrap.",
  lib=8222)
S("80-15-9", "CHP", "Cumene hydroperoxide", "C9H12O2", "Liquid", 22785818,
  "The intermediate of the cumene process, split by acid into phenol and acetone; also a radical initiator for making polymers.",
  lib=8273)
S("120-83-2", "DCP24", "2,4-Dichlorophenol", "C6H4Cl2O", "Solid", 17290392,
  "Phenol chlorinated twice, made almost entirely for the herbicide 2,4-D.",
  lib=2899)
S("94-75-7", "TwoFourD", "2,4-Dichlorophenoxyacetic acid", "C8H6Cl2O3", "Solid", 33084611,
  "2,4-D (1946), a synthetic plant hormone that makes broadleaf weeds grow themselves to death and leaves grass and grain alone. Half of Agent Orange.",
  lib=8793)
S("103-11-7", "EHA2", "2-Ethylhexyl acrylate", "C11H20O2", "Liquid", 51838951,
  "Its branched tail keeps the polymer soft and tacky: the stickiness of pressure-sensitive tape and labels.",
  lib=2218)
S("12042-91-0", "ACHyd", "Aluminium chlorohydrate", "Al2(OH)5Cl", "Solid", "Aluminium_chlorohydrate",
  "The active ingredient of most antiperspirants, which plugs sweat ducts with a gel, and a coagulant that clears drinking water.",
  lib=2947)
S("121-91-5", "IPA", "Isophthalic acid", "C8H6O4", "Solid", 1592061,
  "Terephthalic acid's bent isomer. A little in PET keeps bottles clear, and it makes tough unsaturated polyester resins.",
  lib=2993)
S("124-40-3", "Me2NH", "Dimethylamine", "C2H7N", "Gas", 2421141,
  "A fishy-smelling gas: the start of the solvent DMF, of rubber accelerators, and of many pesticides and drugs.",
  lib=3109)
S("75-50-3", "Me3N", "Trimethylamine", "C3H9N", "Gas", 1620404,
  "The smell of rotting fish. Made for choline, a feed supplement, and for quaternary ammonium salts.",
  smiles="CN(C)C")
S("1318-23-6", "Boehmite", "Boehmite", "AlO(OH)", "Solid", 1089245,
  "AlO(OH), a mineral of bauxite. Made pure, it is calcined into the gamma-alumina that carries most refinery catalysts.",
  lib=3331)
S("556-67-2", "D4", "Octamethylcyclotetrasiloxane", "C8H24O4Si4", "Liquid", 46351737,
  "D4: four dimethylsiloxane units in a ring, opened and chained to make silicone oils and rubbers.",
  lib=6492)
S("541-02-6", "D5", "Decamethylcyclopentasiloxane", "C10H30O5Si5", "Liquid", 6298659,
  "D5, the five-unit silicone ring: a silky, quickly evaporating carrier in deodorants, hair products and dry cleaning.",
  lib=6385)
S("6422-86-2", "DOTP", "Dioctyl terephthalate", "C24H38O4", "Liquid", 31464006,
  "The phthalate-free plasticiser, made from the terephthalic acid of PET instead of phthalic anhydride.",
  lib=7115)
S("7782-99-2", "H2SO3", "Sulfurous acid", "H2SO3", "Aqueous", 231141,
  "Sulfur dioxide dissolved in water: a mild acid never isolated pure, used to bleach and to keep wine.",
  lib=8133, props=("IsAcid",))
S("106-46-7", "pDCB", "1,4-Dichlorobenzene", "C6H4Cl2", "Solid", 241062,
  "The smell of mothballs and toilet blocks, and the monomer of polyphenylene sulfide plastic.",
  lib=2389)
S("107-98-2", "PGME", "1-Methoxy-2-propanol", "C4H10O2", "Liquid", 46757213,
  "PGME, a glycol ether solvent for paints, inks and cleaners, gentler than the ethylene glycol ethers it replaced.",
  lib=2471)
S("108-10-1", "MIBK", "Methyl isobutyl ketone", "C6H12O", "Liquid", 2254792,
  "A solvent for paints and gums, and the extractant that separates hafnium from zirconium for nuclear reactors.",
  lib=2502)
S("126-30-7", "NPG", "Neopentyl glycol", "C5H12O2", "Solid", 22635490,
  "No hydrogens next to its alcohol groups, so its polyesters shrug off heat, light and water: powder coatings and lubricants.",
  lib=3156)
S("123-05-7", "EthylHexanal", "2-Ethylhexanal", "C8H16O", "Liquid", 78111226,
  "Butanal's aldol dimer with the double bond hydrogenated, oxidised in turn to 2-ethylhexanoic acid.",
  lib=3060)
S("149-57-5", "EHAcid", "2-Ethylhexanoic acid", "C8H16O2", "Liquid", 13348874,
  "Its cobalt and manganese salts are the driers that make oil paint and varnish set; it also makes synthetic lubricants.",
  lib=3803)
S("25265-71-8", "DPG", "Dipropylene glycol", "C6H14O3", "Liquid", 22322716,
  "A by-product of propylene glycol: the carrier of fragrances, and a part of unsaturated polyester resins.",
  lib=4746)

E4.reactions += [
    R("Clinker Aluminate", "3 CaO + Alumina -> C3A", BLAST,
      "Lime and the alumina in clay fuse in the cement kiln at about 1,450 C.", wiki=9270912, T=1450),
    R("Sulfuryl Chloride", "SO2 + Cl2 -> SO2Cl2", CAT,
      "Regnault (1838): sulfur dioxide and chlorine combine over activated charcoal.", wiki=2682431,
      cat="Charcoal", T=30, dh=-67),
    R("p-Dichlorobenzene", "Chlorobenzene + Cl2 -> pDCB + HCl", CAT,
      "Chlorobenzene chlorinated again over iron chloride: the para isomer crystallises out.", wiki=241062,
      cat="FeCl3", T=60, dh=-120),
]
E5.reactions += [
    R("Isobutane Dehydrogenation", "Isobutane -> Isobutylene + H2", CAT,
      "Houdry's Catofin process: hydrogen stripped from isobutane over chromia on alumina at about 600 C.",
      wiki="Isobutylene", cat="Cr2O3", T=590, dh=117),
    R("Isopentane Dehydrogenation", "Isopentane -> Isoamylene + H2", CAT,
      "The same chromia catalyst takes hydrogen from isopentane.", wiki=22111939, cat="Cr2O3", T=580, dh=115),
    R("Acrolein Oxidation", "2 Acrolein + O2 -> 2 AcrylicAcid", CAT,
      "The second stage of propylene oxidation: acrolein to acrylic acid over molybdenum oxides.",
      wiki="Acrylic_acid", cat="MoO3", T=260, dh=-254),
    R("Methyl Acrylate", "AcrylicAcid + Methanol -> MethylAcrylate + H2O", CAT,
      "Acrylic acid esterified with methanol.", wiki=12406414, cat="H2SO4", T=90, dh=-10),
    R("Butyl Acrylate", "AcrylicAcid + Butanol -> ButylAcrylate + H2O", CAT,
      "Acrylic acid esterified with butanol.", wiki=48823927, cat="H2SO4", T=100, dh=-10),
    R("2-Ethylhexyl Acrylate", "AcrylicAcid + 2EH -> EHA2 + H2O", CAT,
      "Acrylic acid esterified with 2-ethylhexanol.", wiki=51838951, cat="H2SO4", T=110, dh=-10),
    R("Chlorine Dioxide", "2 NaClO3 + H2O2 + H2SO4 -> 2 ClO2 + O2 + Na2SO4 + 2 H2O", FLASK,
      "Sodium chlorate reduced by hydrogen peroxide in sulfuric acid, right at the pulp mill.", wiki=458673, T=60),
    R("Isobutane Oxidation", "Isobutane + O2 -> TBHP", PRESS,
      "Isobutane oxidised by air in the liquid phase, under pressure at about 130 C.", wiki=19492220, T=130, dh=-170),
    R("Oxirane Process", "Propylene + TBHP -> PO + tBuOH", CAT,
      "Halcon and ARCO (1969): tert-butyl hydroperoxide hands its spare oxygen to propylene over a molybdenum catalyst, leaving tert-butanol to sell.",
      wiki=600925, cat="MoO3", T=110, dh=-200),
    R("Propylene Glycol", "PO + H2O -> PG", PRESS,
      "Propylene oxide opened by water at about 200 C.", wiki="Propylene_glycol", T=200, dh=-90),
    R("Dipropylene Glycol", "PO + PG -> DPG", PRESS,
      "A second propylene oxide opened by propylene glycol.", wiki=22322716, T=200, dh=-90),
    R("Methoxypropanol", "PO + Methanol -> PGME", CAT,
      "Propylene oxide opened by methanol with a base catalyst.", wiki=46757213, cat="NaOH", T=120, dh=-90),
    R("Acetone Cyanohydrin", "Acetone + HCN -> ACH", FLASK,
      "Acetone and hydrogen cyanide with a trace of alkali: ICI's route to acrylic glass (1933).", wiki=9861171,
      T=20, dh=-45),
    R("Ammonium Thiosulfate", "2 NH3 + SO2 + S + H2O -> ATS", MIX,
      "Ammonia, sulfur dioxide and sulfur combined in water.", wiki=32581528),
    R("Potassium Thiosulfate", "2 KOH + SO2 + S -> K2S2O3 + H2O", MIX,
      "Caustic potash, sulfur dioxide and sulfur.", wiki=68911744),
    R("Methylenedianiline", "2 Aniline + CH2O -> MDA + H2O", FLASK,
      "Aniline condensed with formaldehyde in hydrochloric acid.", wiki=31504551, T=80),
    R("MDI Phosgenation", "MDA + 2 COCl2 -> MDI + 4 HCl", FLASK,
      "Methylenedianiline and phosgene in hot chlorobenzene (Bayer, 1950s).", wiki=1727620, T=150),
    R("Ethanolamine", "EO + NH3 -> MEA", PRESS,
      "Ethylene oxide opened by aqueous ammonia.", wiki=1001091, T=100, dh=-125),
    R("Methyldiethanolamine", "2 EO + Methylamine -> MDEA", PRESS,
      "Two ethylene oxides opened by methylamine.", wiki=17403365, T=100, dh=-250),
    R("Dimethylaminoethanol", "EO + Me2NH -> DMAE", PRESS,
      "Ethylene oxide opened by dimethylamine.", wiki=1918853, T=100, dh=-125),
    R("Dimethylamine", "Methylamine + Methanol -> Me2NH + H2O", CAT,
      "Methylamine methylated again over alumina.", wiki=2421141, cat="Alumina", T=400),
    R("Trimethylamine", "Me2NH + Methanol -> Me3N + H2O", CAT,
      "A third methyl over the same alumina; the plant balances all three amines.", wiki=1620404, cat="Alumina", T=400),
    R("Methional", "Acrolein + Methanethiol -> Methional", FLASK,
      "Methanethiol adds across acrolein's double bond, on the way to methionine.", wiki=41145502, T=40),
    R("TAME", "Isoamylene + Methanol -> TAME", CAT,
      "Methanol added to the C5 olefin over an acid catalyst.", wiki=24767728, cat="H2SO4", T=70),
    R("Dimethyl Terephthalate", "TPA + 2 Methanol -> DMT + 2 H2O", CAT,
      "Terephthalic acid esterified with methanol, then distilled pure.", wiki=2004090, cat="H2SO4", T=250),
    R("Cyclohexanedimethanol", "DMT + 7 H2 -> CHDM + 2 Methanol", HIGHP,
      "Dimethyl terephthalate hydrogenated twice over: first the ring, then the ester groups.", wiki=31632219,
      cat="Cu", T=200),
    R("Ethylenediamine", "EDC + 4 NH3 -> EDA + 2 NH4Cl", PRESS,
      "Ethylene dichloride heated with aqueous ammonia.", wiki=2955396, T=180),
    R("Diisobutylene", "2 Isobutylene -> Diisobutylene", CAT,
      "Isobutylene dimerised by cold sulfuric acid.", wiki=78195155, cat="H2SO4", T=20, dh=-80),
    R("Cyanuric Chloride", "3 HCN + 3 Cl2 -> CyanuricChloride + 3 HCl", CAT,
      "Cyanogen chloride, from hydrogen cyanide and chlorine, trimerised over activated carbon.", wiki=2484579,
      cat="Charcoal", T=350),
    R("Trioxane", "3 CH2O -> Trioxane", CAT,
      "Formaldehyde trimerised in strong acid and distilled off.", wiki=3056960, cat="H2SO4", T=100),
    R("Ortho-Alkylation", "Phenol + 2 Isobutylene -> DTBP26", CAT,
      "Ethyl Corporation's process: aluminium phenoxide steers isobutylene to both sides of the OH.",
      wiki=3656926, cat="Al", T=110),
    R("Dimethylaminoethyl Acrylate", "MethylAcrylate + DMAE -> DMAEA + Methanol", CAT,
      "Methyl acrylate transesterified with dimethylaminoethanol.", wiki=57188455, cat="NaOMe", T=100),
    R("Freon 113", "PCE + Cl2 + 3 HF -> CFC113 + 3 HCl", CAT,
      "Swarts fluorination: perchloroethylene chlorinated and fluorinated over antimony pentachloride.",
      wiki=17206806, cat="SbCl5", T=100),
    R("Ortho-Methylation", "Phenol + 2 Methanol -> DMP26 + 2 H2O", CRACKER,
      "Phenol methylated at both ortho positions over magnesium oxide (GE, for Noryl).", wiki=3411364,
      cat="MgO", T=450),
    R("Hydrochlorinating Vinyl Chloride", "VinylChloride + HCl -> DCE11", CAT,
      "Hydrogen chloride added across vinyl chloride with an iron chloride catalyst.", wiki=3122764,
      cat="FeCl3", T=40),
    R("Methyl Chloroform", "DCE11 + Cl2 -> TCA111 + HCl", LIGHT,
      "1,1-Dichloroethane chlorinated by light.", wiki=302493, T=50),
    R("Propylene Dichloride", "Propylene + Cl2 -> DCP12", CAT,
      "Chlorine added across propylene's double bond with an iron chloride catalyst.", wiki=27731849,
      cat="FeCl3", T=40, dh=-185),
    R("Trichloroethane", "VinylChloride + Cl2 -> TCE112", CAT,
      "Chlorine added across vinyl chloride.", wiki=4029717, cat="FeCl3", T=40),
    R("Cumene Hydroperoxide", "Cumene + O2 -> CHP", PRESS,
      "Cumene oxidised by air under pressure: the first half of the cumene process.", wiki=22785818, T=100, dh=-120),
    R("Hock Cleavage", "CHP -> Phenol + Acetone", CAT,
      "A drop of sulfuric acid splits cumene hydroperoxide into phenol and acetone (Hock, 1944).",
      wiki="Cumene_process", cat="H2SO4", T=60, dh=-252),
    R("2,4-Dichlorophenol", "Phenol + 2 Cl2 -> DCP24 + 2 HCl", FLASK,
      "Molten phenol chlorinated twice, ortho and para.", wiki=17290392, T=60),
    R("2,4-D", "DCP24 + ClAcOH -> TwoFourD + HCl", FLASK,
      "The dichlorophenol joined to chloroacetic acid in alkali (1941, Pokorny).", wiki=33084611, T=100),
    R("Aluminium Chlorohydrate", "4 Al + 2 HCl + 10 H2O -> 2 ACHyd + 6 H2", FLASK,
      "Aluminium metal dissolved in too little hydrochloric acid.", wiki="Aluminium_chlorohydrate", T=90),
    R("Isophthalic Acid", "mXylene + 3 O2 -> IPA + 2 H2O", CAT,
      "m-Xylene oxidised by air with cobalt and manganese salts.", wiki=1592061, cat="Co", T=200),
    R("Boehmite", "AlOH3 -> Boehmite + H2O", PRESS,
      "Aluminium hydroxide heated in water under pressure loses half its water.", wiki=1089245, T=200),
    R("Silicone Cyclics", "4 Me2SiCl2 + 4 H2O -> D4 + 8 HCl", FLASK,
      "Dimethyldichlorosilane hydrolysed: the rings are distilled out of the oily hydrolysate.", wiki=46351737),
    R("Ring Equilibration", "5 D4 -> 4 D5", CAT,
      "A trace of base opens and recloses the silicone rings until the five-membered one can be distilled off.",
      wiki=6298659, cat="KOH", T=150),
    R("Sulfurous Acid", "SO2 + H2O -> H2SO3", MIX,
      "Sulfur dioxide dissolved in water.", wiki=231141, dh=-20),
    R("MIBK", "DiacetoneAlcohol + H2 -> MIBK + H2O", CAT,
      "Diacetone alcohol dehydrated and hydrogenated over palladium.", wiki=2254792, cat="Pd", T=130),
    R("Neopentyl Glycol", "Isobutyraldehyde + CH2O + H2 -> NPG", CAT,
      "Isobutyraldehyde and formaldehyde condensed, then hydrogenated over nickel.", wiki=22635490,
      cat="Ni", T=120),
    R("2-Ethylhexanal", "2 Butanal + H2 -> EthylHexanal + H2O", PRESS,
      "Butanal's aldol dimer, hydrogenated at the double bond only (palladium keeps the aldehyde intact).",
      wiki=78111226, T=120),
    R("2-Ethylhexanoic Acid", "2 EthylHexanal + O2 -> 2 EHAcid", HEAT,
      "2-Ethylhexanal oxidised by air.", wiki=13348874, T=50, dh=-260),
]
E6.reactions += [
    R("MTBE", "Isobutylene + Methanol -> MTBE", CAT,
      "Methanol added to isobutylene over an acid catalyst (a sulfonated resin in the plant). The first plant opened in Italy in 1973.",
      wiki=391568, cat="H2SO4", T=70, dh=-37),
    R("Ethylene Trimerisation", "3 Ethylene -> Hexene", CRACKER,
      "A chromium catalyst that joins exactly three ethylenes (Chevron Phillips, 2003).", wiki=2669449,
      cat="Cr2O3", T=115, dh=-250),
    R("Shell Higher Olefins", "Hexene + 2 Ethylene -> Decene", CAT,
      "The Shell Higher Olefin Process (1977): ethylene chains grow two carbons at a time on a nickel catalyst.",
      wiki="Shell_higher_olefin_process", cat="Ni", T=100),
    R("Dodecene", "Decene + Ethylene -> Dodecene", CAT,
      "One more ethylene on the growing chain.", wiki=37386074, cat="Ni", T=100),
    R("Octadecene", "Hexadecene + Ethylene -> Octadecene", CAT,
      "One more ethylene: the long alpha-olefins.", wiki=4663377, cat="Ni", T=100),
    R("CFC-113a", "CFC113 -> CFC113a", CAT,
      "Freon 113 rearranged over aluminium chloride.", wiki=42166815, cat="AlCl3", T=80),
    R("Dioctyl Terephthalate", "DMT + 2 2EH -> DOTP + 2 Methanol", CAT,
      "Dimethyl terephthalate transesterified with 2-ethylhexanol over a titanium catalyst.", wiki=31464006,
      cat="TiCl4", T=200),
]

# the next part of the list (each part imports the one after it)
import authored_canon_2  # noqa: E402,F401

settle_eras()
