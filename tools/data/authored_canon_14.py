"""
Curieosity's industrial chemistry, part 14 (see authored_canon.py).
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E1, E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)


# --- the canon substances ------------------------------------------------------------------
S("75-03-6", "EtI", "Iodoethane", "C2H5I", "Liquid", 14897149,
  "Ethyl iodide, an ethylating agent in the lab.", smiles="ICC")
S("4736-60-1", "ETPPI", "Ethyltriphenylphosphonium iodide", "C20H20IP", "Solid", 519796,
  "A Wittig salt, and a catalyst for curing epoxy resins.", lib=5952)
S("82-71-3", "StyphnicAcid", "Styphnic acid", "C6H3N3O8", "Solid", 1197753,
  "Trinitroresorcinol, picric acid's cousin; its lead salt is the primer in gun cartridges.", lib=8355)
S("77-47-4", "HCCP", "Hexachlorocyclopentadiene", "C5Cl6", "Liquid", 22929574,
  "The diene behind the cyclodiene insecticides (aldrin, dieldrin, chlordane) and the flame retardant chlorendic acid.", lib=8059)
S("7773-06-0", "AmmSulfamate", "Ammonium sulfamate", "H6N2O3S", "Solid", 6991065,
  "A weedkiller for tree stumps and brambles, and a flame retardant.", lib=8114)
S("542-02-9", "Acetoguanamine", "Acetoguanamine", "C4H7N5", "Solid", 23876500,
  "A melamine cousin for resins.", lib=6394)
S("7783-66-6", "IF5", "Iodine pentafluoride", "IF5", "Liquid", 2332188,
  "A fluorinating agent and the start of perfluoroalkyl iodides.", lib=8139)
S("13767-32-3", "ZnMoO4", "Zinc molybdate", "ZnMoO4", "Solid", 5438079,
  "A white pigment that inhibits corrosion and suppresses smoke from burning PVC.", lib=3532)
S("5977-14-0", "Acetoacetamide", "Acetoacetamide", "C4H7NO2", "Solid", 74151581,
  "A building block for pyrazolone pigments and drugs.", lib=6800)
S("88-04-0", "PCMX", "Chloroxylenol", "C8H9ClO", "Solid", 3517740,
  "PCMX, the antiseptic of Dettol (1932).", lib=8561)
S("7486-38-6", "DisodiumAdipate", "Disodium adipate", "C6H8Na2O4", "Solid", 5286993,
  "E356, a buffer and acidity regulator in foods.", lib=7867)
S("10544-72-6", "N2O4", "Dinitrogen tetroxide", "N2O4", "Liquid", 186259,
  "The storable oxidiser of rockets, from the Titan to the Apollo service module: it ignites hydrazine fuels on contact.", lib=2355)
S("149-32-6", "Erythritol", "Erythritol", "C4H10O4", "Solid", 668700,
  "A sugar alcohol made by fermentation: nearly as sweet as sugar with almost no calories.", lib=3800)
S("545-06-2", "TCAN", "Trichloroacetonitrile", "C2Cl3N", "Liquid", 37610142,
  "A reagent for activating alcohols (trichloroacetimidates) in sugar and peptide chemistry.", lib=6419)
S("2052-49-5", "TBAH", "Tetrabutylammonium hydroxide", "C16H37NO", "Liquid", 1484936,
  "A strong organic base soluble in organic solvents, for titrations and phase-transfer reactions.", lib=4382)
S("96-27-5", "Thioglycerol", "Thioglycerol", "C3H8O2S", "Liquid", 11792920,
  "A thiol for hair perms and protein chemistry.", lib=8858)
S("1112-67-0", "TBAC", "Tetrabutylammonium chloride", "C16H36ClN", "Solid", 66991208,
  "A phase-transfer catalyst.", lib=2671)
S("109-67-1", "Pentene", "1-Pentene", "C5H10", "Liquid", 2330696,
  "A five-carbon alpha-olefin, from Fischer-Tropsch fuel plants.", lib=2563)
S("51311-17-2", "CF4", "Tetrafluoromethane", "CF4", "Gas", 5627714,
  "The simplest fluorocarbon: a plasma etch gas, and a greenhouse gas that lasts 50,000 years.", lib=6166)
S("100-46-9", "Benzylamine", "Benzylamine", "C7H9N", "Liquid", 6642794,
  "A building block for drugs and the explosive CL-20.", lib=2013)
S("102-08-9", "DPTU", "Thiocarbanilide", "C13H12N2S", "Solid", 5160040,
  "N,N'-Diphenylthiourea, one of the first rubber accelerators (1906).", lib=2167)
S("149-73-5", "TMOF", "Trimethyl orthoformate", "C4H10O3", "Liquid", 29351741,
  "A reagent that protects aldehydes and dries reaction mixtures.", lib=3804)
S("2550-26-7", "BenzylAcetone", "Benzylacetone", "C10H12O", "Liquid", 18613375,
  "A sweet, floral ketone that attracts melon flies; used in perfumes.", lib=4784)
S("5872-08-2", "CSA", "Camphorsulfonic acid", "C10H16O4S", "Solid", 3234326,
  "A chiral acid for separating amines into their mirror-image forms.", lib=6714)
S("76-16-4", "C2F6", "Hexafluoroethane", "C2F6", "Gas", 11554125,
  "A plasma etch and chamber-cleaning gas in chip fabs.", smiles="FC(F)(F)C(F)(F)F")
S("107-89-1", "Acetaldol", "3-Hydroxybutanal", "C4H8O2", "Liquid", 22366247,
  "Aldol itself: the product that gave the aldol reaction its name (Wurtz, 1872).", lib=2468)
S("101-81-5", "DPMethane", "Diphenylmethane", "C13H12", "Solid", 5697178,
  "A fragrance and a heat-transfer fluid.", lib=2117)
S("7790-28-5", "NaIO4", "Sodium periodate", "NaIO4", "Solid", 2172265,
  "An oxidiser that cleaves sugars between neighbouring OH groups.", lib=8160)
S("10450-60-9", "H5IO6", "Periodic acid", "H5IO6", "Solid", 2134103,
  "The acid of the periodic acid-Schiff stain, which turns sugars magenta in tissue slides.", lib=2308)
S("7790-21-8", "KIO4", "Potassium periodate", "KIO4", "Solid", 2172275,
  "A strong oxidiser for analysis.", lib=8159)
S("676-58-4", "MeMgCl", "Methylmagnesium chloride", "CH3ClMg", "Liquid", 12176617,
  "A Grignard reagent (Victor Grignard, 1900; Nobel 1912), the classic carbon nucleophile.", lib=7311)
S("366-18-7", "Bipyridine", "2,2'-Bipyridine", "C10H8N2", "Solid", 7388191,
  "A chelating ligand, and the start of the herbicide diquat.", lib=5540)
S("55589-62-3", "AceK", "Acesulfame potassium", "C4H4KNO4S", "Solid", 323114,
  "Acesulfame K (Hoechst, 1967), a sweetener 200 times as sweet as sugar, found by accident when a chemist licked his finger.", lib=6487)
S("99-30-9", "Dicloran", "Dicloran", "C6H4Cl2N2O2", "Solid", 77854416,
  "A fungicide for fruit and vegetables in storage.", lib=8950)
S("102-07-8", "Carbanilide", "Carbanilide", "C13H12N2O", "Solid", 51559227,
  "N,N'-Diphenylurea, a stabiliser for smokeless powder.", lib=2166)
S("25395-31-7", "Diacetin", "Diacetin", "C7H12O5", "Liquid", 59284520,
  "Glycerol diacetate, a plasticiser and food additive.", lib=4773)
S("87-89-8", "Inositol", "myo-Inositol", "C6H12O6", "Solid", 866807,
  "A sugar-like ring, once called vitamin B8, made from the phytic acid of corn.", lib=8528)
S("56038-13-2", "Sucralose", "Sucralose", "C12H19Cl3O8", "Solid", 48463,
  "Sucrose with three OH groups swapped for chlorine: 600 times as sweet as sugar (Tate & Lyle, 1976).", lib=6536)
S("147-47-7", "TMQ", "TMQ", "C12H15N", "Solid", 3511848,
  "2,2,4-Trimethyl-1,2-dihydroquinoline, the antioxidant that protects tyre rubber from heat.", lib=3762)

E3.reactions += [
    R("Nitrogen Tetroxide", "2 NO2 -> N2O4", COOL,
      "Brown nitrogen dioxide pairs up into colourless dinitrogen tetroxide when cooled.", wiki=186259, T=-10),
]
E4.reactions += [
    R("Iodoethane", "Ethanol + HI -> EtI + H2O", MIX,
      "Ethanol and hydriodic acid.", wiki=14897149),
    R("Styphnic Acid", "Resorcinol + 3 HNO3 -> StyphnicAcid + 3 H2O", FLASK,
      "Resorcinol nitrated three times.", wiki=1197753, T=40),
    R("Ammonium Sulfamate", "SulfamicAcid + NH3 -> AmmSulfamate", MIX,
      "Sulfamic acid neutralised with ammonia.", wiki=6991065),
    R("Iodine Pentafluoride", "I2 + 5 F2 -> 2 IF5", MIX,
      "Iodine burns in fluorine (Moissan).", wiki=2332188),
    R("Zinc Molybdate", "ZnO + MoO3 -> ZnMoO4", HEAT,
      "Zinc and molybdenum oxides fired together.", wiki=5438079, T=700),
    R("Disodium Adipate", "Adipic + 2 NaOH -> DisodiumAdipate + 2 H2O", MIX,
      "Adipic acid neutralised.", wiki=5286993),
    R("Trichloroacetonitrile", "Acetonitrile + 3 Cl2 -> TCAN + 3 HCl", HEAT,
      "Acetonitrile chlorinated in the gas phase.", wiki=37610142, T=400),
    R("Tetrafluoromethane", "Charcoal + 2 F2 -> CF4", HEAT,
      "Charcoal burns in fluorine.", wiki=5627714, T=500),
    R("Benzylamine", "BenzylChloride + 2 NH3 -> Benzylamine + NH4Cl", PRESS,
      "Benzyl chloride in excess ammonia.", wiki=6642794, T=60),
    R("Thiocarbanilide", "2 Aniline + CS2 -> DPTU + H2S", HEAT,
      "Aniline boiled with carbon disulfide.", wiki=5160040, T=100),
    R("Trimethyl Orthoformate", "CHCl3 + 3 NaOMe -> TMOF + 3 NaCl", FLASK,
      "Chloroform and sodium methoxide.", wiki=29351741, T=60),
    R("Diphenylmethane", "Benzene + BenzylChloride -> DPMethane + HCl", CAT,
      "Benzene benzylated over aluminium chloride (Friedel and Crafts, 1877).", wiki=5697178, cat="AlCl3", T=60),
    R("Sodium Periodate", "NaI + 4 H2O -> NaIO4 + 4 H2", ECELL,
      "Iodide oxidised all the way to periodate at the anode.", wiki=2172265),
    R("Periodic Acid", "NaIO4 + HNO3 + 2 H2O -> H5IO6 + NaNO3", MIX,
      "Sodium periodate acidified.", wiki=2134103),
    R("Potassium Periodate", "NaIO4 + KCl -> KIO4 + NaCl", MIX,
      "The sparingly soluble potassium salt crystallises out.", wiki=2172275),
    R("Grignard Reagent", "CH3Cl + Mg -> MeMgCl", FLASK,
      "Methyl chloride and magnesium turnings in dry ether (Grignard, 1900).", wiki=12176617, T=35),
    R("Dicloran", "Nitroaniline + 2 Cl2 -> Dicloran + 2 HCl", FLASK,
      "4-Nitroaniline chlorinated on both sides of the amine.", wiki=77854416, T=60),
    R("Carbanilide", "2 Aniline + Urea -> Carbanilide + 2 NH3", HEAT,
      "Aniline heated with urea.", wiki=51559227, T=160),
    R("Diacetin", "Glycerol + 2 AcOH -> Diacetin + 2 H2O", HEAT,
      "Glycerol esterified twice with acetic acid.", wiki=59284520, T=130),
    R("Acetaldol", "2 Acetaldehyde -> Acetaldol", COOL,
      "Acetaldehyde dimerised in cold dilute alkali (Wurtz, 1872).", wiki=22366247, T=5),
]
E5.reactions += [
    R("Ethyltriphenylphosphonium Iodide", "PPh3 + EtI -> ETPPI", FLASK,
      "Triphenylphosphine quaternised by ethyl iodide.", wiki=519796, T=80),
    R("Hexachlorocyclopentadiene", "Cyclopentadiene + 6 Cl2 -> HCCP + 6 HCl", LIGHT,
      "Cyclopentadiene chlorinated exhaustively.", wiki=22929574, T=60),
    R("Acetoguanamine", "Acetonitrile + DCD -> Acetoguanamine", CAT,
      "Dicyandiamide adds to acetonitrile with a base.", wiki=23876500, cat="KOH", T=150),
    R("Acetoacetamide", "Diketene + NH3 -> Acetoacetamide", MIX,
      "Ammonia opens the diketene ring.", wiki=74151581),
    R("Chloroxylenol", "Isophorone + Cl2 -> PCMX + Methane + HCl", CAT,
      "Isophorone aromatised to 3,5-xylenol, losing a methyl group, then chlorinated.", wiki=3517740, cat="Alumina",
      T=500),
    R("Erythritol", "Maltose -> Erythritol", BIOR,
      "Yeast-like fungi ferment glucose syrup into erythritol.", wiki=668700, cat="Yeast", T=35, exact=False),
    R("Tetrabutylammonium Hydroxide", "TBAB + KOH -> TBAH + KBr", MIX,
      "Bromide exchanged for hydroxide.", wiki=1484936),
    R("Thioglycerol", "MCPD + H2S -> Thioglycerol + HCl", FLASK,
      "3-Chloropropanediol with sodium hydrosulfide.", wiki=11792920, T=60),
    R("Tetrabutylammonium Chloride", "Tributylamine + Butanol + HCl -> TBAC + H2O", FLASK,
      "Tributylamine quaternised with butyl chloride.", wiki=66991208, T=100),
    R("1-Pentene", "Pentanol -> Pentene + H2O", CAT,
      "1-Pentanol dehydrated over alumina.", wiki=2330696, cat="Alumina", T=350),
    R("Benzylacetone", "Benzaldehyde + Acetone + H2 -> BenzylAcetone + H2O", CAT,
      "Benzaldehyde and acetone condensed, then hydrogenated over palladium.", wiki=18613375, cat="Pd", T=80),
    R("Camphorsulfonic Acid", "Camphor + H2SO4 + AceticAnhydride -> CSA + 2 AcOH", FLASK,
      "Camphor sulfonated in sulfuric acid and acetic anhydride (Reychler).", wiki=3234326, T=20),
    R("Bipyridine", "2 Pyridine -> Bipyridine + H2", CAT,
      "Pyridine coupled to itself over Raney nickel.", wiki=7388191, cat="Ni", T=180),
    R("Acesulfame K", "Diketene + SulfamicAcid + SO3 + KOH -> AceK + H2SO4 + H2O", FLASK,
      "Diketene and sulfamic acid, cyclised by sulfur trioxide, neutralised with potash.", wiki=323114, T=0),
    R("Myo-Inositol", "CornSteep -> Inositol", PRESS,
      "Phytic acid from corn steep liquor hydrolysed under pressure.", wiki=866807, T=180, exact=False),
    R("Sucralose", "Sucrose + 3 HCl -> Sucralose + 3 H2O", FLASK,
      "Sucrose protected at one position, chlorinated selectively at three, and deprotected.", wiki=48463, T=100),
    R("TMQ", "Aniline + 2 Acetone -> TMQ + 2 H2O", CAT,
      "Aniline condensed with acetone in acid.", wiki=3511848, cat="pTsOH", T=140),
]
E6.reactions += [
    R("Hexafluoroethane", "Ethane + 6 HF -> C2F6 + 6 H2", ECELL,
      "Every hydrogen of ethane swapped for fluorine electrochemically.", wiki=11554125),
]

import authored_canon_15  # noqa: E402,F401
