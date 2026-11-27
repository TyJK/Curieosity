"""
Curieosity's industrial chemistry, part 6 (see authored_canon.py).
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E1, E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)


# --- intermediates the canon set lacks ---------------------------------------------------
S(None, "HFP", "Hexafluoropropylene", "C3F6", "Gas", "Hexafluoropropylene",
  "The fluorinated propylene that copolymerises with TFE into FEP, the meltable Teflon of cable jackets.",
  smiles="FC(F)=C(F)C(F)(F)F")
S(None, "Pentanol", "1-Pentanol", "C5H12O", "Liquid", "1-Pentanol",
  "Amyl alcohol, from hydrogenating pentanal: a solvent, and the alcohol of fruity amyl esters.", smiles="CCCCCO")

# --- the canon substances ------------------------------------------------------------------
S("34885-03-5", "MCHM", "4-Methylcyclohexanemethanol", "C8H16O", "Liquid", 41603115,
  "A frother for cleaning coal. In January 2014 it leaked from a tank into West Virginia's Elk River and left 300,000 people without tap water.", lib=5443)
S("359-35-3", "HFC134", "1,1,2,2-Tetrafluoroethane", "C2H2F4", "Gas", 75750707,
  "HFC-134, the symmetrical isomer of the car refrigerant HFC-134a.", lib=5500)
S("3710-84-7", "DEHAm", "Diethylhydroxylamine", "C4H11NO", "Liquid", 656638,
  "An oxygen scavenger for boiler water, and the short-stop that halts synthetic rubber polymerisation at the right moment.", lib=5566)
S("3926-62-3", "NaClAc", "Sodium chloroacetate", "C2H2ClNaO2", "Solid", 31630228,
  "The salt that carboxymethylates cellulose into CMC, the thickener of toothpaste and ice cream.", lib=5679)
S("428-59-1", "HFPO", "Hexafluoropropylene oxide", "C3F6O", "Gas", 16621593,
  "The epoxide that DuPont polymerised into Krytox oils (1960s), and the starting point of GenX.", lib=5826)
S("431-89-0", "HFC227ea", "1,1,1,2,3,3,3-Heptafluoropropane", "C3HF7", "Gas", 3146692,
  "HFC-227ea (FM-200), the gas that floods data centres and museum vaults to put out fires without harming what's inside.", lib=5834)
S("463-40-1", "Linolenic", "alpha-Linolenic acid", "C18H30O2", "Liquid", 153316,
  "The omega-3 fatty acid of linseed: its three double bonds let linseed oil dry to a hard film in paint and linoleum.", lib=5915)
S("4767-03-7", "DMPA", "Dimethylolpropionic acid", "C5H10O4", "Solid", 61294445,
  "A diol with a carboxylic acid, built into polyurethanes so they disperse in water: waterborne floor and wood finishes.", lib=5965)
S("4861-19-2", "UreaPhosphate", "Urea phosphate", "CH7N2O5P", "Solid", 4468819,
  "A water-soluble fertiliser and drip-line cleaner of urea and phosphoric acid.", lib=6000)
S("517-23-7", "ABL", "2-Acetylbutyrolactone", "C6H8O3", "Liquid", 70430725,
  "An intermediate for vitamin B1 (thiamine) and some drugs.", lib=6190)
S("52628-25-8", "ZAC", "Zinc ammonium chloride", "(NH4)2ZnCl4", "Solid", 19342419,
  "The flux of hot-dip galvanising, which cleans steel so molten zinc wets it.", lib=6253)
S("527-60-6", "TMPhenol246", "2,4,6-Trimethylphenol", "C9H12O", "Solid", 57726133,
  "Mesitol, a building block for antioxidants.", lib=6257)
S("534-22-5", "MethylFuran2", "2-Methylfuran", "C5H6O", "Liquid", 19045052,
  "Sylvan, made from furfural: a solvent and a candidate biofuel.", lib=6317)
S("541-05-9", "D3", "Hexamethylcyclotrisiloxane", "C6H18O3Si3", "Solid", 57931361,
  "D3, the strained three-unit silicone ring that opens readily to build silicones of exact length.", lib=6386)
S("555-31-7", "AlOiPr3", "Aluminium isopropoxide", "C9H21AlO3", "Solid", 3268054,
  "The reagent of the Meerwein-Ponndorf-Verley reduction (1925), and a precursor of high-purity alumina.", lib=6482)
S("563-80-4", "MIPK", "Methyl isopropyl ketone", "C5H10O", "Liquid", 10577287,
  "A ketone solvent and building block for pesticides.", lib=6553)
S("565-62-8", "MPO", "3-Methyl-3-penten-2-one", "C6H10O", "Liquid", 41887699,
  "The unsaturated ketone from which Iso E Super, the cedarwood note of many perfumes, is built.", lib=6563)
S("583-78-8", "DCP25", "2,5-Dichlorophenol", "C6H4Cl2O", "Solid", 74146100,
  "The phenol on the way to the herbicide dicamba.", lib=6687)
S("590-01-2", "ButylPropionate", "Butyl propionate", "C7H14O2", "Liquid", 72866313,
  "A solvent for lacquers and coatings, with an apple-like smell.", lib=6744)
S("598-55-0", "MethylCarbamate", "Methyl carbamate", "C2H5NO2", "Solid", 4429975,
  "Made from urea and methanol, for textile finishes and the insecticide carbaryl.", lib=6803)
S("6132-04-3", "Na3Citrate", "Sodium citrate", "Na3C6H5O7·2H2O", "Solid", 683065,
  "E331: the sour-salty flavour of soft drinks, the emulsifying salt of processed cheese, and the anticoagulant in blood bags.", lib=6894)
S("624-54-4", "PentylPropionate", "Pentyl propionate", "C8H16O2", "Liquid", 3124904,
  "A fruity solvent for coatings and inks.", lib=6974)
S("625-45-6", "MethoxyaceticAcid", "Methoxyacetic acid", "C3H6O3", "Liquid", 75489550,
  "An intermediate for pharmaceuticals and pesticides.", lib=6979)
S("628-63-7", "AmylAcetate", "Amyl acetate", "C7H14O2", "Liquid", 1829128,
  "Banana oil: the smell of pear drops and bananas, and a solvent for nitrocellulose lacquers.", smiles="O=C(OCCCCC)C")
S("638-38-0", "MnOAc2", "Manganese(II) acetate", "Mn(C2H3O2)2", "Solid", 22635270,
  "A catalyst for making PET and terephthalic acid, and a drier for paints.", lib=7076)
S("77-71-4", "DMH", "5,5-Dimethylhydantoin", "C5H8N2O2", "Solid", 1244933,
  "The hydantoin from acetone, chlorinated or brominated into pool sanitisers, or loaded with formaldehyde as a preservative.", lib=8063)
S("6440-58-0", "DMDMH", "DMDM hydantoin", "C7H12N2O4", "Solid", 19328033,
  "A preservative in shampoos and cosmetics that slowly releases formaldehyde.", lib=7125)
S("646-06-0", "Dioxolane", "1,3-Dioxolane", "C3H6O2", "Liquid", 2974322,
  "A solvent, and a comonomer that makes acetal plastic more stable.", lib=7139)
S("67-72-1", "C2Cl6", "Hexachloroethane", "C2Cl6", "Solid", 7997230,
  "Burned with zinc it makes the dense white smoke of military smoke grenades; it also degasses molten aluminium.", lib=7281)
S("684-16-2", "HFA", "Hexafluoroacetone", "C3F6O", "Gas", 3939550,
  "A fierce electrophile, the start of the fluorinated bisphenol AF and of the anaesthetic sevoflurane.", lib=7446)
S("75-02-5", "VinylFluoride", "Vinyl fluoride", "C2H3F", "Gas", 11029056,
  "The monomer of Tedlar, the weatherproof film on the backs of solar panels and aircraft cabin walls.", lib=7877)
S("75-33-2", "iPrSH", "2-Propanethiol", "C3H8S", "Liquid", 74830114,
  "A skunky thiol added to gas as an odorant, and used to make pesticides.", lib=7893)
S("75-64-9", "tBuNH2", "tert-Butylamine", "C4H11N", "Liquid", 10676696,
  "An amine for rubber accelerators and the drug salbutamol.", lib=7911)
S("75-66-1", "tBuSH", "tert-Butyl mercaptan", "C4H10S", "Liquid", 31346205,
  "The rotten-cabbage smell added to odourless natural gas so leaks can be noticed.", lib=7913)
S("7585-39-9", "BetaCD", "beta-Cyclodextrin", "C42H70O35", "Solid", 26573819,
  "Seven glucoses in a ring, a bucket that holds smell molecules: the active part of Febreze.", smiles="OCC1OC2OC3C(O)C(O)C(OC3CO)OC4C(O)C(O)C(OC4CO)OC5C(O)C(O)C(OC5CO)OC6C(O)C(O)C(OC6CO)OC7C(O)C(O)C(OC7CO)OC8C(O)C(O)C(OC8CO)OC1C(O)C2O")
S("76-01-7", "PentachloroEthane", "Pentachloroethane", "C2HCl5", "Liquid", 36184409,
  "A solvent and an intermediate on the way to perchloroethylene.", lib=7963)
S("76-05-1", "TFA", "Trifluoroacetic acid", "C2HF3O2", "Liquid", 3019112,
  "A strong, volatile acid that cleaves peptides from their resin in solid-phase synthesis.", smiles="O=C(O)C(F)(F)F")
S("76-14-2", "CFC114", "1,2-Dichlorotetrafluoroethane", "C2Cl2F4", "Gas", 3719339,
  "CFC-114, once the refrigerant of large chillers and of uranium enrichment plants; phased out under the Montreal Protocol.", lib=7967)
S("77-48-5", "DBDMH", "1,3-Dibromo-5,5-dimethylhydantoin", "C5H6Br2N2O2", "Solid", 4251151,
  "A slow-release bromine tablet for hot tubs and cooling towers.", lib=8060)
S("77-79-2", "Sulfolene", "3-Sulfolene", "C4H6O2S", "Solid", 11057402,
  "Butadiene and sulfur dioxide joined in a ring, which gives butadiene back when heated.", lib=8066)
S("77-86-1", "Tris", "Tris(hydroxymethyl)aminomethane", "C4H11NO3", "Solid", 496251,
  "Tris, the biochemist's buffer: it holds a solution near pH 8, as in the gels that sort DNA.", lib=8069)
S("7719-09-7", "SOCl2", "Thionyl chloride", "SOCl2", "Liquid", 1642767,
  "It turns acids into acid chlorides and leaves only gases behind, and is the cathode liquid of lithium-thionyl chloride batteries.", lib=8079)
S("7783-54-2", "NF3", "Nitrogen trifluoride", "NF3", "Gas", 2719832,
  "The gas that cleans chip and flat-screen deposition chambers: 17,000 times as warming as carbon dioxide.", lib=8138)
S("7785-84-4", "STMP", "Sodium trimetaphosphate", "Na3P3O9", "Solid", 3048850,
  "A ring of three phosphates that crosslinks food starches so they hold up in sauces and fillings.", lib=8144)
S("7789-21-1", "HSO3F", "Fluorosulfuric acid", "HSO3F", "Liquid", 2840068,
  "One of the strongest acids that can be bottled; with antimony pentafluoride it is magic acid.", lib=8149, props=("IsAcid",))
S("78-62-6", "DMDES", "Dimethyldiethoxysilane", "C6H16O2Si", "Liquid", 22635047,
  "A silane for water-repellent coatings and silicone resins.", lib=8184)
S("78-82-0", "IBN", "Isobutyronitrile", "C4H7N", "Liquid", 48102075,
  "A nitrile for the insecticide diazinon.", lib=8192)
S("78-96-6", "MIPA", "1-Amino-2-propanol", "C3H9NO", "Liquid", 13353024,
  "Monoisopropanolamine, for metalworking fluids and cosmetic surfactants.", lib=8203)
S("78491-02-8", "DiazolidinylUrea", "Diazolidinyl urea", "C8H14N4O7", "Solid", 9990477,
  "A cosmetic preservative built from allantoin and formaldehyde.", lib=8216)
S("79-34-5", "TeCA", "1,1,2,2-Tetrachloroethane", "C2H2Cl4", "Liquid", 12328732,
  "Once made by the thousand tonnes to become trichloroethylene; a dense, toxic solvent.", smiles="ClC(Cl)C(Cl)Cl")
S("79-36-7", "DCAC", "Dichloroacetyl chloride", "C2HCl3O", "Liquid", 54437685,
  "An acid chloride for herbicide safeners and drugs.", lib=8236)
S("79-38-9", "CTFE", "Chlorotrifluoroethylene", "C2ClF3", "Gas", 11092665,
  "The monomer of Kel-F (PCTFE), a clear fluoroplastic for cryogenic seals and pill blister packs.", lib=8238, props=("IsMonomer",))

E3.reactions += [
    R("Thionyl Chloride", "SO2 + PCl5 -> SOCl2 + POCl3", MIX,
      "Sulfur dioxide and phosphorus pentachloride (Persoz, 1849).", wiki=1642767),
]
E4.reactions += [
    R("Fluorosulfuric Acid", "SO3 + HF -> HSO3F", MIX,
      "Sulfur trioxide and hydrogen fluoride.", wiki=2840068),
    R("Manganese Acetate", "MnCO3 + 2 AcOH -> MnOAc2 + CO2 + H2O", MIX,
      "Manganese carbonate dissolved in acetic acid.", wiki=22635270),
    R("Zinc Ammonium Chloride", "ZnCl2 + 2 NH4Cl -> ZAC", MIX,
      "Zinc chloride and sal ammoniac crystallised together.", wiki=19342419),
    R("Hexachloroethane", "PCE + Cl2 -> C2Cl6", LIGHT,
      "Chlorine adds to perchloroethylene in the light.", wiki=7997230),
    R("Sodium Citrate", "Citric + 3 NaOH -> Na3Citrate + H2O", MIX,
      "Citric acid neutralised by caustic soda; the dihydrate crystallises.", wiki=683065),
    R("Amyl Acetate", "Pentanol + AcOH -> AmylAcetate + H2O", CAT,
      "1-Pentanol esterified with acetic acid.", wiki=1829128, cat="H2SO4", T=110),
    R("Tetrachloroethane", "Acetylene + 2 Cl2 + SbCl5 -> TeCA + SbCl5", FLASK,
      "Chlorine adds twice to acetylene in liquid antimony pentachloride.", wiki=12328732, T=80),
]
E5.reactions += [
    R("Hexafluoropropylene", "3 TFE -> 2 HFP", HEAT,
      "Tetrafluoroethylene pyrolysed at 800 C.", wiki="Hexafluoropropylene", T=800),
    R("1-Pentanol", "Pentanal + H2 -> Pentanol", CAT,
      "Pentanal hydrogenated over nickel.", wiki="1-Pentanol", cat="Ni", T=120),
    R("MCHM", "CHDM + H2 -> MCHM + H2O", HIGHP,
      "Over-hydrogenation of cyclohexanedimethanol strips one OH.", wiki=41603115, cat="Cu", T=250),
    R("HFC-134", "TFE + H2 -> HFC134", CAT,
      "Hydrogen added across tetrafluoroethylene over palladium.", wiki=75750707, cat="Pd", T=100),
    R("Diethylhydroxylamine", "Diethylamine + H2O2 -> DEHAm + H2O", FLASK,
      "Diethylamine oxidised by hydrogen peroxide.", wiki=656638, T=60),
    R("Sodium Chloroacetate", "2 ClAcOH + SodaAsh -> 2 NaClAc + H2O + CO2", MIX,
      "Chloroacetic acid neutralised with soda ash.", wiki=31630228),
    R("HFPO", "2 HFP + O2 -> 2 HFPO", PRESS,
      "Hexafluoropropylene oxidised under pressure.", wiki=16621593, T=150),
    R("Linseed Hydrolysis", "LinseedOil + H2O -> Linolenic + Glycerol", PRESS,
      "Linseed oil split by steam under pressure; the linolenic acid is distilled from the other fatty acids.",
      wiki=153316, T=250, exact=False),
    R("DMPA", "Propanal + 2 CH2O + H2O2 -> DMPA + H2O", FLASK,
      "Propanal takes two formaldehydes; the aldehyde is oxidised by hydrogen peroxide.", wiki=61294445, T=50),
    R("Urea Phosphate", "Urea + H3PO4 -> UreaPhosphate", MIX,
      "Urea crystallised from phosphoric acid.", wiki=4468819),
    R("Acetylbutyrolactone", "EO + MAA -> ABL + Methanol", FLASK,
      "Methyl acetoacetate's anion opens ethylene oxide and closes a lactone.", wiki=70430725, T=60),
    R("Mesitol", "DMP26 + Methanol -> TMPhenol246 + H2O", CAT,
      "A third methyl on the phenol ring.", wiki=57726133, cat="MgO", T=450),
    R("2-Methylfuran", "Furfural + 2 H2 -> MethylFuran2 + H2O", HIGHP,
      "Furfural hydrogenated over copper chromite.", wiki=19045052, cat="Cu", T=200),
    R("Cracking D4", "3 D4 -> 4 D3", HEAT,
      "D4 cracked with a trace of base; the strained three-ring is distilled off.", wiki=57931361, T=300),
    R("Aluminium Isopropoxide", "2 Al + 6 Isopropanol -> 2 AlOiPr3 + 3 H2", FLASK,
      "Aluminium dissolved in isopropanol with a trace of mercury chloride.", wiki=3268054, T=80),
    R("Methyl Isopropyl Ketone", "IsobutyricAcid + AcOH -> MIPK + CO2 + H2O", CAT,
      "Two acids cross-ketonised over manganese oxide.", wiki=10577287, cat="MnO2", T=400),
    R("Methylpentenone", "MEK + Acetaldehyde -> MPO + H2O", CAT,
      "Methyl ethyl ketone condensed with acetaldehyde.", wiki=41887699, cat="H2SO4", T=60),
    R("2,5-Dichlorophenol", "TCB124 + NaOH -> DCP25 + NaCl", PRESS,
      "Trichlorobenzene hydrolysed by caustic soda under pressure.", wiki=74146100, T=200),
    R("Butyl Propionate", "Propionic + Butanol -> ButylPropionate + H2O", CAT,
      "Propionic acid esterified with butanol.", wiki=72866313, cat="H2SO4", T=110),
    R("Methyl Carbamate", "Urea + Methanol -> MethylCarbamate + NH3", HEAT,
      "Urea heated with methanol.", wiki=4429975, T=150),
    R("Pentyl Propionate", "Propionic + Pentanol -> PentylPropionate + H2O", CAT,
      "Propionic acid esterified with pentanol.", wiki=3124904, cat="H2SO4", T=120),
    R("Methoxyacetic Acid", "ClAcOH + NaOMe -> MethoxyaceticAcid + NaCl", FLASK,
      "Chloroacetic acid with sodium methoxide.", wiki=75489550, T=60),
    R("Dimethylhydantoin", "Acetone + HCN + NH3 + CO2 -> DMH + H2O", PRESS,
      "The Bucherer-Bergs reaction: acetone, cyanide and ammonium carbonate.", wiki=1244933, T=70),
    R("DMDM Hydantoin", "DMH + 2 CH2O -> DMDMH", MIX,
      "Dimethylhydantoin takes two formaldehydes.", wiki=19328033),
    R("Dioxolane", "EG + CH2O -> Dioxolane + H2O", CAT,
      "Ethylene glycol and formaldehyde close into a ring.", wiki=2974322, cat="H2SO4", T=80),
    R("Hexafluoroacetone", "HexachloroAcetone + 6 HF -> HFA + 6 HCl", CAT,
      "Every chlorine of hexachloroacetone swapped for fluorine.", wiki=3939550, cat="Cr2O3", T=300),
    R("Vinyl Fluoride", "HFC152a -> VinylFluoride + HF", HEAT,
      "HFC-152a cracked to vinyl fluoride.", wiki=11029056, T=500),
    R("2-Propanethiol", "Propylene + H2S -> iPrSH", CAT,
      "Hydrogen sulfide added to propylene over alumina.", wiki=74830114, cat="Alumina", T=200),
    R("tert-Butylamine", "Isobutylene + NH3 -> tBuNH2", CAT,
      "Ammonia added directly to isobutylene over a zeolite (BASF).", wiki=10676696, cat="ZSM5", T=250),
    R("tert-Butyl Mercaptan", "Isobutylene + H2S -> tBuSH", CAT,
      "Hydrogen sulfide added to isobutylene over an acid catalyst.", wiki=31346205, cat="Alumina", T=100),
    R("Cyclodextrin", "Starch -> BetaCD", BIOR,
      "A bacterial enzyme (cyclodextrin glucanotransferase), made by engineered bacteria, curls starch chains into rings.", wiki=26573819, T=50,
      cat="Ecoli", exact=False),
    R("Pentachloroethane", "TCE + Cl2 -> PentachloroEthane", CAT,
      "Chlorine added across trichloroethylene.", wiki=36184409, cat="FeCl3", T=60),
    R("CFC-114", "CFC113 + HF -> CFC114 + HCl", CAT,
      "Freon 113 fluorinated once more.", wiki=3719339, cat="SbCl5", T=100),
    R("DBDMH", "DMH + 2 Br2 + 2 NaOH -> DBDMH + 2 NaBr + 2 H2O", FLASK,
      "Dimethylhydantoin brominated in caustic soda.", wiki=4251151, T=20),
    R("3-Sulfolene", "Butadiene + SO2 -> Sulfolene", PRESS,
      "Butadiene and sulfur dioxide join in a cheletropic reaction.", wiki=11057402, T=80),
    R("Tris", "Nitromethane + 3 CH2O + 3 H2 -> Tris + 2 H2O", CAT,
      "Nitromethane takes three formaldehydes; the nitro group is hydrogenated to an amine.", wiki=496251,
      cat="Ni", T=60),
    R("Sodium Trimetaphosphate", "3 NaPO3 -> STMP", HEAT,
      "Sodium metaphosphate glass annealed until it crystallises as three-membered rings.", wiki=3048850, T=500),
    R("Dimethyldiethoxysilane", "Me2SiCl2 + 2 Ethanol -> DMDES + 2 HCl", FLASK,
      "Dimethyldichlorosilane esterified with ethanol.", wiki=22635047, T=60),
    R("Isobutyronitrile", "Isobutanol + NH3 -> IBN + H2O + 2 H2", CRACKER,
      "Isobutanol dehydrogenated and aminated over nickel.", wiki=48102075, cat="Ni", T=350),
    R("Isopropanolamine", "PO + NH3 -> MIPA", HEAT,
      "Propylene oxide opened by excess aqueous ammonia.", wiki=13353024, T=100),
    R("Diazolidinyl Urea", "Allantoin + 4 CH2O -> DiazolidinylUrea", MIX,
      "Allantoin takes four formaldehydes.", wiki=9990477),
    R("Dichloroacetyl Chloride", "2 TCE + O2 -> 2 DCAC", LIGHT,
      "Trichloroethylene oxidised by air in the light.", wiki=54437685, T=80),
    R("Chlorotrifluoroethylene", "CFC113 + Zn -> CTFE + ZnCl2", FLASK,
      "Zinc pulls two chlorines off Freon 113.", wiki=11092665, T=60),
]
E6.reactions += [
    R("FM-200", "HFP + HF -> HFC227ea", CAT,
      "Hydrogen fluoride added across hexafluoropropylene.", wiki=3146692, cat="Cr2O3", T=300),
    R("Trifluoroacetic Acid", "AcetylChloride + 3 HF + H2O -> TFA + HCl + 3 H2", ECELL,
      "Simons electrochemical fluorination of acetyl chloride, then hydrolysis.", wiki=3019112),
    R("Nitrogen Trifluoride", "NH3 + 3 F2 -> NF3 + 3 HF", CAT,
      "Ammonia fluorinated over copper.", wiki=2719832, cat="Cu", T=100),
]

import authored_canon_7  # noqa: E402,F401
