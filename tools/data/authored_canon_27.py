"""
Curieosity's industrial chemistry, part 27 (see authored_canon.py): classes of compounds.

Many canon records are not one molecule but a family: lubricant esters made from a blend of acids,
soaps of mixed fatty acids, lignosulfonates, coagulants of varying basicity. Each family is one
substance here, carrying the IsClass property (the Codex shows a "Class" chip and says the formula
is a typical member's). Its formula is a representative member's, so its reactions still balance,
and every canon record of the family maps onto it. Also the records that are the same product as
something already in the game, and a few the earlier passes had marked wrong, now identified.
"""

from authored_canon import S, R, CANON  # noqa: F401
from authored_content import E3, E4, E5, E6, X  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR, pubchem)

P = {}
CLASS = ("IsClass",)


def PC(cas, key, name, formula, state, ref, desc, smiles=None, props=()):
    """A compound whose page is on PubChem (by CID, or by name)."""
    P[key] = pubchem(ref)
    S(cas, key, name, formula, state, P[key], desc, smiles=smiles, props=props)


def WK(cas, key, name, formula, state, title, desc, smiles=None, props=()):
    """A compound with a Wikipedia article."""
    P[key] = title
    S(cas, key, name, formula, state, title, desc, smiles=smiles, props=props)


def FAMILY(key, name, formula, state, ref, desc, members, smiles=None, props=CLASS):
    """A class of compounds as one substance: formula and SMILES are a typical member's; every
    canon record in `members` maps onto it. `ref` is a Wikipedia title (or a full URL)."""
    P[key] = ref
    X(key, name, formula, state, desc, ref, id=0, smiles=smiles, props=props,
      balance=None if formula != "mixture" else "C")
    for cas in members:
        CANON[cas] = key


# the same products as substances already in the game
CANON.update({"309934-69-8": "DIDP",       # di-C9-11 branched alkyl phthalates, C10-rich: commercial DIDP
              "9003-55-8": "SBR",          # butadiene-styrene copolymer
              "181028-79-5": "BDP",        # POCl3 + bisphenol A + phenol: commercial BDP
              "1300-73-8": "Xylidine24",   # technical xylidine, mostly the 2,4-isomer
              "9003-35-4": "Bakelite",     # phenol-formaldehyde copolymer
              "12645-31-7": "D2EHPA",      # 2-ethylhexyl phosphate, mostly the di-ester
              "11138-11-7": "BaFerrite"})

# --- families -----------------------------------------------------------------------------------
FAMILY("POEsters", "Polyol ester lubricants", "C33H60O8", "Liquid", "Synthetic_oil",
       "Esters of pentaerythritol and its kin with C5 to C10 acids: the oils of jet engines and of refrigerant compressors. "
       "Shown as pentaerythritol tetraheptanoate.",
       ["68130-53-0", "1078142-24-1", "68441-94-1", "118685-29-3", "68130-51-8", "68441-67-8", "70024-75-8",
        "70851-04-6", "71010-76-9", "68130-55-2", "11138-60-6", "68583-52-8"],
       smiles="CCCCCCC(=O)OCC(COC(=O)CCCCCC)(COC(=O)CCCCCC)COC(=O)CCCCCC")
FAMILY("CAN", "Calcium ammonium nitrate", "mixture", "Solid", "Calcium_ammonium_nitrate",
       "Ammonium nitrate granulated with ground limestone: a nitrogen fertiliser that will not detonate.", ["15245-12-2"],
       props=())
FAMILY("PAC", "Polyaluminium chloride", "mixture", "Aqueous", "Polyaluminium_chloride",
       "Partly hydrolysed aluminium chloride: its charged clusters coagulate the mud out of drinking water.", ["1327-41-9"],
       props=CLASS)
FAMILY("SodiumAluminosilicate", "Sodium aluminosilicate", "mixture", "Solid", "Sodium_aluminosilicate",
       "Amorphous E554: keeps salt and powders flowing, and fills paper and paint.", ["1344-00-9"], props=CLASS)
FAMILY("Lignosulfonate", "Lignosulfonates", "mixture", "Solid", "Lignosulfonates",
       "Lignin made water-soluble by sulfite pulping: dispersants for concrete, dyes and pesticides, and binders for animal feed pellets.",
       ["8061-53-8"], props=CLASS)
FAMILY("CocamideDEA", "Cocamide DEA", "C16H33NO3", "Liquid", "Cocamide_DEA",
       "Coconut fatty acids amidated with diethanolamine: a foam booster and thickener for shampoos and dish liquids. "
       "Shown as lauric diethanolamide.", ["120-40-1"], smiles="CCCCCCCCCCCC(=O)N(CCO)CCO")
FAMILY("CocamideMEA", "Cocamide MEA", "C14H29NO2", "Solid", "Cocamide_MEA",
       "Coconut fatty acids amidated with ethanolamine: a thickener and pearliser for shampoos. Shown as lauric monoethanolamide.",
       ["68140-00-1"], smiles="CCCCCCCCCCCC(=O)NCCO")
FAMILY("TXP", "Trixylyl phosphate", "C24H27O4P", "Liquid", pubchem("Trixylenyl phosphate"),
       "Xylenols of mixed isomers phosphated: a fire-resistant hydraulic fluid and PVC plasticiser. Shown as tris(3,4-xylyl) phosphate.",
       ["25155-23-1"], smiles="Cc1ccc(OP(=O)(Oc2ccc(C)c(C)c2)Oc2ccc(C)c(C)c2)cc1C")
FAMILY("TritonX100", "Triton X-100", "C32H58O10", "Liquid", "Triton_X-100",
       "Octylphenol ethoxylate with about nine and a half ethylene oxides: the detergent of the biology lab, which opens cell membranes. "
       "Shown with nine.", ["26027-38-3"],
       smiles="CC(C)(C)CC(C)(C)c1ccc(OCCOCCOCCOCCOCCOCCOCCOCCOCCO)cc1")
FAMILY("VinylND", "Vinyl neodecanoate", "C12H22O2", "Liquid", pubchem("Vinyl neodecanoate"),
       "VeoVa 10: its bulky branched acid shields the vinyl polymers of exterior paints from water and sunlight. "
       "Shown as the 2,2-dimethyloctanoate.", ["51000-52-3"], smiles="CCCCCCC(C)(C)C(=O)OC=C")
FAMILY("HydrophobicSilica", "Hydrophobic fumed silica", "mixture", "Solid", "Fumed_silica",
       "Fumed silica capped with trimethylsilyl groups so that water beads off it: it thickens silicone sealants and keeps toner powders flowing.",
       ["68909-20-6"], props=CLASS)

# --- polymers -----------------------------------------------------------------------------------
P["Ultem"] = "Polyetherimide"
X("Ultem", "Polyetherimide", "(C37H24N2O6)n", "Solid",
  "Ultem: an amber, flame-proof plastic that holds its strength at 200 C, for aircraft interiors and sterilisable medical trays.",
  P["Ultem"], id=0, balance="C37H24N2O6", props=("IsPolymer",))
CANON["61128-46-9"] = "Ultem"
WK("151-56-4", "Aziridine", "Aziridine", "C2H5N", "Liquid", "Aziridine",
   "Ethylenimine, a strained three-membered ring that springs open: the monomer of polyethylenimine.", "C1CN1")
P["PEImine"] = "Polyethylenimine"
X("PEImine", "Polyethylenimine", "(C2H5N)n", "Liquid",
  "A densely charged cationic polymer for paper making, gene delivery into cells, and capturing carbon dioxide.",
  P["PEImine"], id=0, balance="C2H5N", props=("IsPolymer",))
CANON["9002-98-6"] = "PEImine"

# --- records now identified ---------------------------------------------------------------------
PC("140-66-9", "OctylPhenol", "4-tert-Octylphenol", "C14H22O", "Solid", 8814,
   "Phenol alkylated with diisobutylene, for ethoxylates and tackifier resins.", "CC(C)(C)CC(C)(C)c1ccc(O)cc1")
PC("3944-72-7", "OctSulfonicAcid", "1-Octanesulfonic acid", "C8H18O3S", "Liquid", 49939, "The free acid of sodium octanesulfonate.",
   "CCCCCCCCS(O)(=O)=O")
PC("24800-44-0", "TPG", "Tripropylene glycol", "C9H20O4", "Liquid", "Tripropylene glycol",
   "A glycol for UV-curing acrylates and a fragrance solvent.", "CC(O)COC(C)COC(C)CO")
PC("14806-72-5", "TEAAcetate", "Triethanolamine acetate", "C8H19NO5", "Liquid", 159752,
   "A grinding aid for cement and a corrosion inhibitor.", "CC(O)=O.OCCN(CCO)CCO")
PC("563-43-9", "EtAlCl2", "Ethylaluminium dichloride", "C2H5AlCl2", "Liquid", 11237,
   "A Lewis-acid co-catalyst for olefin oligomerisation.", "CC[Al](Cl)Cl")
PC("3999-70-0", "KOBu", "Potassium n-butoxide", "C4H9KO", "Solid", 88652381, "A strong base.", "[K+].CCCC[O-]")
PC("4337-75-1", "SLMT", "Sodium lauroyl methyl taurate", "C15H30NNaO4S", "Solid", 24189848,
   "A mild surfactant for facial cleansers and baby shampoos.", "[Na+].CCCCCCCCCCCC(=O)N(C)CCS([O-])(=O)=O")
PC("27090-63-7", "TBHDA", "N,N,N',N'-Tetrabutylhexanediamine", "C22H48N2", "Liquid", 94377,
   "A tertiary diamine, quaternised into antistatic agents.", "CCCCN(CCCC)CCCCCCN(CCCC)CCCC")

# --- the reactions -------------------------------------------------------------------------------
E4.reactions += [
    R("Calcium Ammonium Nitrate", "NH4NO3 + Limestone -> CAN", MIX,
      "Ammonium nitrate melt mixed with ground limestone and prilled.", wiki=P["CAN"], exact=False),
    R("Polyaluminium Chloride", "AlOH3 + HCl -> PAC", MIX,
      "Aluminium hydroxide dissolved in too little acid, so the aluminium stays partly hydrolysed.", wiki=P["PAC"], exact=False),
    R("Sodium Aluminosilicate", "NaAlOH4 + Sand -> SodiumAluminosilicate", HEAT,
      "Sodium aluminate and silica precipitated together.", wiki=P["SodiumAluminosilicate"], exact=False, T=90),
    R("Ammonium Sulfite Pulping", "Wood + NH4HSO3 -> Lignosulfonate", PRESS,
      "Wood chips cooked in ammonium bisulfite: the cellulose stays, the lignin dissolves as lignosulfonate.",
      wiki=P["Lignosulfonate"], exact=False, T=140),
]
E5.reactions += [
    R("Polyol Ester Lubricant", "Pentaerythritol + 4 HeptanoicAcid -> POEsters + 4 H2O", CAT,
      "Pentaerythritol esterified with the C7 to C10 acids of the blend.", wiki=P["POEsters"], cat="H2SO4", T=220),
    R("Cocamide DEA", "CoconutOil + 3 DEA -> 3 CocamideDEA + Glycerol", HEAT,
      "Coconut oil amidated directly with diethanolamine.", wiki=P["CocamideDEA"], T=150),
    R("Cocamide MEA", "CoconutOil + 3 MEA -> 3 CocamideMEA + Glycerol", HEAT,
      "Coconut oil amidated with ethanolamine.", wiki=P["CocamideMEA"], T=150),
    R("Trixylyl Phosphate", "POCl3 + 3 Xylenol34 -> TXP + 3 HCl", FLASK,
      "Xylenols phosphated with phosphorus oxychloride.", wiki=P["TXP"], T=150),
    R("4-tert-Octylphenol", "Phenol + Diisobutylene -> OctylPhenol", CAT,
      "Phenol alkylated with diisobutylene on an acid resin.", wiki=P["OctylPhenol"], cat="H2SO4", T=100),
    R("Triton X-100", "OctylPhenol + 9 EO -> TritonX100", PRESS,
      "Octylphenol ethoxylated with potash.", wiki=P["TritonX100"], T=150),
    R("Vinyl Neodecanoate", "NDA + Acetylene -> VinylND", CAT,
      "Acetylene added to neodecanoic acid over a zinc salt.", wiki=P["VinylND"], cat="ZnO", T=200),
    R("Hydrophobic Silica", "FumedSilica + HMDS -> HydrophobicSilica", MIX,
      "Fumed silica's surface hydroxyls capped by hexamethyldisilazane; ammonia leaves.", wiki=P["HydrophobicSilica"], exact=False),
    R("Polyetherimide", "BPADA + MPD -> Ultem + 2 H2O", POLY,
      "Bisphenol A dianhydride and m-phenylenediamine condensed in the melt.", wiki=P["Ultem"], T=300),
    R("Aziridine", "MEA + H2SO4 + 2 NaOH -> Aziridine + Na2SO4 + 3 H2O", FLASK,
      "Wenker's synthesis: ethanolamine sulfated, then caustic closes the three-membered ring.", wiki=P["Aziridine"], T=100),
    R("Polyethylenimine", "Aziridine -> PEImine", POLY, "Aziridine opened in acid into a branched polyamine.", wiki=P["PEImine"]),
    R("1-Octanesulfonic Acid", "NaOctSulfonate + HCl -> OctSulfonicAcid + NaCl", MIX,
      "The sodium salt passed through an acid ion exchanger.", wiki=P["OctSulfonicAcid"]),
    R("Tripropylene Glycol", "DPG + PO -> TPG", PRESS, "Dipropylene glycol takes one more propylene oxide.", wiki=P["TPG"], T=130),
    R("Triethanolamine Acetate", "TEA + AcOH -> TEAAcetate", MIX, "Triethanolamine neutralised with acetic acid.", wiki=P["TEAAcetate"]),
    R("Ethylaluminium Dichloride", "TEAL + 4 AlCl3 -> 6 EtAlCl2", FLASK,
      "Triethylaluminium and more aluminium chloride redistribute their groups (with less, diethylaluminium chloride).", wiki=P["EtAlCl2"], T=40),
    R("Potassium Butoxide", "2 Butanol + 2 K -> 2 KOBu + H2", MIX, "Potassium dissolved in 1-butanol.", wiki=P["KOBu"]),
    R("Sodium Lauroyl Methyl Taurate", "LauricAcid + NaNMT -> SLMT + H2O", HEAT,
      "Lauric acid amidated with sodium methyltaurate.", wiki=P["SLMT"], T=200),
    R("Tetrabutylhexanediamine", "2 Dibutylamine + DCH16 + 2 NaOH -> TBHDA + 2 NaCl + 2 H2O", FLASK,
      "Dibutylamine alkylated at both ends of 1,6-dichlorohexane.", wiki=P["TBHDA"], T=150),
]
import authored_canon_28  # noqa: E402,F401
