"""
Curieosity's industrial chemistry, part 12 (see authored_canon.py).
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E1, E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)


# --- the canon substances ------------------------------------------------------------------
S("4394-85-8", "NFM", "N-Formylmorpholine", "C5H9NO2", "Liquid", 56730134,
  "A solvent that pulls aromatics out of petrol streams and strips CO2 from natural gas.", lib=5855)
S("4432-31-9", "MES", "MES", "C6H13NO4S", "Solid", 8356379,
  "One of Norman Good's buffers (1966), holding biochemistry experiments near pH 6.", lib=5865)
S("4437-85-8", "ButyleneCarbonate", "Butylene carbonate", "C5H8O3", "Liquid", 25679184,
  "A polar solvent for coatings and battery electrolytes.", lib=5868)
S("462-08-8", "AminoPyridine3", "3-Aminopyridine", "C5H6N2", "Solid", 24416852,
  "A building block for drugs and herbicides.", lib=5911)
S("4712-55-4", "DPPite", "Diphenyl phosphite", "C12H11O3P", "Liquid", 54490407,
  "A stabiliser for PVC and a reagent for phosphonate chemistry.", lib=5943)
S("473-55-2", "Pinane", "Pinane", "C10H18", "Liquid", 71161214,
  "Hydrogenated pinene, oxidised to pinane hydroperoxide, an initiator for synthetic rubber, and a route to linalool.", lib=5950)
S("4731-53-7", "TOP", "Trioctylphosphine", "C24H51P", "Liquid", 36496214,
  "With its oxide, the hot solvent and ligand in which quantum dots are grown.", lib=5951)
S("496-46-8", "Glycoluril", "Glycoluril", "C4H6N4O2", "Solid", 44062596,
  "Two fused rings of urea: the building block of cucurbiturils and of slow-release fertilisers and resins.", lib=6011)
S("497-18-7", "Carbohydrazide", "Carbohydrazide", "CH6N4O", "Solid", 16006868,
  "An oxygen scavenger for power-station boiler water, safer than hydrazine.", lib=6019)
S("507-09-5", "ThioaceticAcid", "Thioacetic acid", "C2H4OS", "Liquid", 8908895,
  "A reagent that puts thiol groups into molecules, with a smell like burnt onions.", lib=6101)
S("507-20-0", "tBuCl", "tert-Butyl chloride", "C4H9Cl", "Liquid", 10567624,
  "The textbook example of an SN1 reaction: tert-butanol and hydrochloric acid in a separating funnel.", lib=6102)
S("51-28-5", "DNP24", "2,4-Dinitrophenol", "C6H4N2O5", "Solid", 948020,
  "A dye and wood preservative that was sold as a slimming drug in 1933: it burns fat as heat, and overheated and killed many who took it.", lib=6121)
S("5188-07-8", "NaSMe", "Sodium methanethiolate", "CH3NaS", "Solid", 20325453,
  "A nucleophile for putting methylthio groups into drugs and pesticides.", lib=6198)
S("52-51-7", "Bronopol", "Bronopol", "C3H6BrNO4", "Solid", 2406722,
  "A preservative for cosmetics, paper mills and cooling water.", lib=6205)
S("542-10-9", "EthylideneDiacetate", "Ethylidene diacetate", "C6H10O4", "Liquid", 41803003,
  "Acetaldehyde and acetic anhydride joined; cracked, it once gave vinyl acetate.", lib=6396)
S("542-28-9", "Valerolactone", "delta-Valerolactone", "C5H8O2", "Liquid", 12546557,
  "A lactone polymerised into biodegradable polyesters.", lib=6397)
S("543-49-7", "Heptanol2", "2-Heptanol", "C7H16O", "Liquid", 21218769,
  "A fruity, herbal alcohol, a flavouring and a mining frother.", lib=6403)
S("544-31-0", "PalmitoylEA", "Palmitoylethanolamide", "C18H37NO2", "Solid", 24913186,
  "A lipid the body makes to calm inflammation, sold as a supplement for pain.", lib=6412)
S("5466-77-3", "Octinoxate", "Octinoxate", "C18H26O3", "Liquid", 2308143,
  "2-Ethylhexyl methoxycinnamate, the most used UVB filter in sunscreen.", lib=6429)
S("556-88-7", "Nitroguanidine", "Nitroguanidine", "CH4N4O2", "Solid", 1810132,
  "The third ingredient of triple-base propellant, which cools the gases and spares gun barrels.", lib=6493)
S("563-47-3", "MethallylCl", "Methallyl chloride", "C4H7Cl", "Liquid", 58543152,
  "Isobutylene chlorinated at the methyl group, for sulfonate monomers and the insecticide carbofuran.", lib=6550)
S("569-64-2", "MalachiteGreen", "Malachite green", "C23H25ClN2", "Solid", 1023079,
  "A vivid green dye (1877) once used against fungus on fish eggs, now banned in food fish.", lib=6578)
S("57-06-7", "AITC", "Allyl isothiocyanate", "C4H5NS", "Liquid", 1576787,
  "The pungent oil of mustard, wasabi and horseradish.", lib=6585)
S("584-03-2", "BDO12", "1,2-Butanediol", "C4H10O2", "Liquid", 24155231,
  "A diol for polyester resins and plasticisers.", lib=6692)
S("590-86-3", "Isovaleraldehyde", "3-Methylbutanal", "C5H10O", "Liquid", 40715102,
  "Isovaleraldehyde, with a malty, chocolate smell: a flavour, and the start of isophytol for vitamin E.", lib=6749)
S("593-84-0", "GuSCN", "Guanidinium thiocyanate", "C2H6N4S", "Solid", 2870145,
  "A chaotropic salt that tears proteins apart, used to extract RNA from cells and in COVID-19 test kits.", lib=6780)
S("598-56-1", "DMEA", "Dimethylethylamine", "C4H11N", "Liquid", 42659405,
  "The gas that cures sand cores for metal casting in seconds (the cold-box process).", lib=6804)
S("60-32-2", "ACA", "Aminocaproic acid", "C6H13NO2", "Solid", 2875860,
  "Caprolactam's ring opened: a drug that helps blood clot by stopping fibrin breaking down.", lib=6822)
S("608-93-5", "PeCB", "Pentachlorobenzene", "C6HCl5", "Solid", 25469252,
  "A by-product and fungicide intermediate, listed under the Stockholm Convention.", lib=6866)
S("617-89-0", "Furfurylamine", "Furfurylamine", "C5H7NO", "Liquid", 24208528,
  "The amine of the diuretic furosemide.", lib=6918)
S("617-94-7", "CumylAlcohol", "2-Phenyl-2-propanol", "C9H12O", "Solid", 73970591,
  "Cumyl alcohol, a by-product of the cumene process and a step to dicumyl peroxide.", lib=6919)
S("618-36-0", "PhenylEthylamine1", "1-Phenylethylamine", "C8H11N", "Liquid", 17096374,
  "A chiral amine used to separate the mirror-image forms of acids.", lib=6932)
S("626-55-1", "BromoPyridine3", "3-Bromopyridine", "C5H4BrN", "Liquid", 65585407,
  "A coupling partner for building pyridine drugs.", lib=6987)
S("657-84-1", "NapTs", "Sodium p-toluenesulfonate", "C7H7NaO3S", "Solid", 73307706,
  "A hydrotrope that keeps concentrated detergents clear and pourable.", lib=7210)
S("67-43-6", "DTPA", "Pentetic acid", "C14H23N3O10", "Solid", 4746146,
  "DTPA: a chelating agent for pulp bleaching, and, holding gadolinium, the first MRI contrast agent (1988).", lib=7270)
S("6837-24-7", "CHPyrrolidone", "N-Cyclohexyl-2-pyrrolidone", "C10H17NO", "Liquid", 33304425,
  "A high-boiling solvent for inks and photoresist strippers.", lib=7440)
S("693-98-1", "MeImidazole2", "2-Methylimidazole", "C4H6N2", "Solid", 44787630,
  "An epoxy curing agent, and the linker of ZIF-8, a zinc framework with molecule-sized pores.", lib=7621)
S("6976-37-0", "BisTris", "Bis-tris", "C8H19NO5", "Solid", 5447687,
  "A buffer for electrophoresis gels.", lib=7631)
S("7087-68-5", "DIPEA", "N,N-Diisopropylethylamine", "C8H19N", "Liquid", 2445897,
  "Hunig's base: crowded enough to grab protons but never to attack.", lib=7682)
S("7327-60-8", "NTAN", "Nitrilotriacetonitrile", "C6H6N4", "Solid", 53767947,
  "The trinitrile hydrolysed to NTA.", lib=7792)
S("75-26-3", "iPrBr", "2-Bromopropane", "C3H7Br", "Liquid", 6830950,
  "An alkylating agent for drugs and pesticides.", lib=7890)
S("75-46-7", "HFC23", "Fluoroform", "CHF3", "Gas", 2814674,
  "HFC-23, a by-product of making HCFC-22 and one of the strongest greenhouse gases; also a fire suppressant and chip etchant.", lib=7901)
S("75-85-4", "tAmylOH", "tert-Amyl alcohol", "C5H12O", "Liquid", 17507722,
  "A solvent, and a once-used anaesthetic.", lib=7920)
S("76-19-7", "C3F8", "Octafluoropropane", "C3F8", "Gas", 2456281,
  "Perfluoropropane: a plasma etch gas for chips, and the bubble surgeons leave in the eye to hold a retina in place.", lib=7969)
S("762-75-4", "tBuFormate", "tert-Butyl formate", "C5H10O2", "Liquid", 15215330,
  "A solvent and a formylating reagent.", lib=7998)
S("7787-49-7", "BeF2", "Beryllium fluoride", "BeF2", "Solid", 2184047,
  "Beryllium fluoride glass; mixed with lithium fluoride it is FLiBe, the coolant salt of molten-salt reactors.", lib=8148)
S("78-27-3", "Ethynylcyclohexanol", "1-Ethynylcyclohexanol", "C8H12O", "Liquid", 65147107,
  "Acetylene added to cyclohexanone: a sedative once, now an inhibitor in silicone curing and a building block.", lib=8177)
S("78-85-3", "Methacrolein", "Methacrolein", "C4H6O", "Liquid", 5684046,
  "Isobutylene oxidised: the first step of Japan's route to methyl methacrylate without cyanide.", lib=8195)
S("78-95-5", "Chloroacetone", "Chloroacetone", "C3H5ClO", "Liquid", 17807311,
  "A tear gas of the First World War, now a building block for drugs and dyes.", lib=8202)
S("79-39-0", "Methacrylamide", "Methacrylamide", "C4H7NO", "Solid", 36119332,
  "The amide formed from acetone cyanohydrin in sulfuric acid on the way to methyl methacrylate.", lib=8239)

E4.reactions += [
    R("tert-Butyl Chloride", "tBuOH + HCl -> tBuCl + H2O", MIX,
      "tert-Butanol shaken with concentrated hydrochloric acid.", wiki=10567624),
    R("2,4-Dinitrophenol", "NCB + HNO3 + NaOH -> DNP24 + NaCl + H2O", FLASK,
      "4-Nitrochlorobenzene nitrated again, then its chlorine hydrolysed off.", wiki=948020, T=90),
    R("Sodium Methanethiolate", "Methanethiol + NaOH -> NaSMe + H2O", MIX,
      "Methanethiol neutralised by caustic soda.", wiki=20325453),
    R("Malachite Green", "2 Benzaldehyde + 4 Dimethylaniline + 2 HCl + O2 -> 2 MalachiteGreen + 4 H2O", FLASK,
      "Benzaldehyde condensed with dimethylaniline, then oxidised (Fischer, 1877).", wiki=1023079, T=100),
    R("Mustard Oil", "AllylChloride + KSCN -> AITC + KCl", FLASK,
      "Allyl thiocyanate rearranges into the isothiocyanate on warming.", wiki=1576787, T=80),
    R("Guanidinium Thiocyanate", "Guanidine + NaSCN + HCl -> GuSCN + NaCl", MIX,
      "Guanidine neutralised with thiocyanic acid.", wiki=2870145),
    R("Nitroguanidine", "Guanidine + HNO3 -> Nitroguanidine + H2O", CAT,
      "Guanidine nitrate dehydrated in sulfuric acid.", wiki=1810132, cat="H2SO4", T=10),
    R("3-Bromopyridine", "Pyridine + Br2 + Oleum -> BromoPyridine3 + HBr + Oleum", HEAT,
      "Pyridine brominated in oleum at 130 C.", wiki=65585407, T=130),
    R("Sodium Tosylate", "pTsOH + NaOH -> NapTs + H2O", MIX,
      "p-Toluenesulfonic acid neutralised.", wiki=73307706),
    R("2-Bromopropane", "Isopropanol + HBr -> iPrBr + H2O", MIX,
      "Isopropanol and hydrobromic acid.", wiki=6830950),
    R("Beryllium Fluoride", "BeOH2 + 2 HF -> BeF2 + 2 H2O", MIX,
      "Beryllium hydroxide dissolved in hydrofluoric acid.", wiki=2184047),
    R("Chloroacetone", "Acetone + Cl2 -> Chloroacetone + HCl", FLASK,
      "Acetone chlorinated once.", wiki=17807311, T=30),
]
E5.reactions += [
    R("N-Formylmorpholine", "Morpholine + MethylFormate -> NFM + Methanol", FLASK,
      "Morpholine formylated by methyl formate.", wiki=56730134, T=60),
    R("MES Buffer", "Morpholine + NaVS + HCl -> MES + NaCl", FLASK,
      "Morpholine adds to vinylsulfonate; acid frees the zwitterion.", wiki=8356379, T=80),
    R("Butylene Carbonate", "EpoxyButane + CO2 -> ButyleneCarbonate", CAT,
      "Carbon dioxide adds to butylene oxide.", wiki=25679184, cat="TMACl", T=150),
    R("3-Aminopyridine", "Nicotinamide + NaClO -> AminoPyridine3 + CO2 + NaCl", MIX,
      "The Hofmann rearrangement of nicotinamide with hypochlorite.", wiki=24416852),
    R("Diphenyl Phosphite", "TPPite + H2O -> DPPite + Phenol", MIX,
      "Triphenyl phosphite partly hydrolysed.", wiki=54490407),
    R("Pinane", "Turpentine + H2 -> Pinane", CAT,
      "Pinene hydrogenated over nickel.", wiki=71161214, cat="Ni", T=100),
    R("Trioctylphosphine", "Phosphine + 3 Octene -> TOP", LIGHT,
      "Phosphine adds to 1-octene three times by a radical chain.", wiki=36496214, T=60),
    R("Glycoluril", "Glyoxal + 2 Urea -> Glycoluril + 2 H2O", FLASK,
      "Glyoxal condensed with two ureas in acid.", wiki=44062596, T=80),
    R("Carbohydrazide", "Urea + 2 N2H4 -> Carbohydrazide + 2 NH3", HEAT,
      "Urea heated with hydrazine.", wiki=16006868, T=120),
    R("Thioacetic Acid", "AceticAnhydride + H2S -> ThioaceticAcid + AcOH", FLASK,
      "Acetic anhydride and hydrogen sulfide.", wiki=8908895, T=40),
    R("Bronopol", "Nitromethane + 2 CH2O + Br2 + NaOH -> Bronopol + NaBr + H2O", FLASK,
      "Nitromethane takes two formaldehydes, then bromine.", wiki=2406722, T=20),
    R("Ethylidene Diacetate", "Acetaldehyde + AceticAnhydride -> EthylideneDiacetate", CAT,
      "Acetaldehyde and acetic anhydride over iron chloride.", wiki=41803003, cat="FeCl3", T=40),
    R("Valerolactone", "Cyclopentanone + PAA -> Valerolactone + AcOH", FLASK,
      "Cyclopentanone oxidised by peracetic acid (Baeyer-Villiger).", wiki=12546557, T=50),
    R("2-Heptanol", "Heptanone2 + H2 -> Heptanol2", CAT,
      "2-Heptanone hydrogenated over nickel.", wiki=21218769, cat="Ni", T=100),
    R("Palmitoylethanolamide", "PalmiticAcid + MEA -> PalmitoylEA + H2O", HEAT,
      "Palmitic acid heated with ethanolamine.", wiki=24913186, T=170),
    R("Octinoxate", "Anisaldehyde + EHAc -> Octinoxate + H2O", CAT,
      "Anisaldehyde condensed with an acetate ester (Claisen), as 2-ethylhexyl methoxycinnamate.", wiki=2308143,
      cat="NaOMe", T=60),
    R("Methallyl Chloride", "Isobutylene + Cl2 -> MethallylCl + HCl", HEAT,
      "Isobutylene chlorinated in the gas phase.", wiki=58543152, T=60),
    R("1,2-Butanediol", "EpoxyButane + H2O -> BDO12", PRESS,
      "Butylene oxide opened by water.", wiki=24155231, T=180),
    R("Isovaleraldehyde", "Isobutylene + CO + H2 -> Isovaleraldehyde", CAT,
      "Isobutylene hydroformylated with a rhodium catalyst.", wiki=40715102, cat="Rh", T=100),
    R("Dimethylethylamine", "Me2NH + Ethanol -> DMEA + H2O", CAT,
      "Dimethylamine ethylated by ethanol over nickel.", wiki=42659405, cat="Ni", T=200),
    R("Aminocaproic Acid", "Caprolactam + H2O -> ACA", PRESS,
      "Caprolactam's ring opened by water.", wiki=2875860, T=200),
    R("Pentachlorobenzene", "TCB124 + 2 Cl2 -> PeCB + 2 HCl", FLASK,
      "Trichlorobenzene chlorinated twice more.", wiki=25469252, T=150),
    R("Furfurylamine", "Furfural + NH3 + H2 -> Furfurylamine + H2O", CAT,
      "Furfural reductively aminated over nickel.", wiki=24208528, cat="Ni", T=100),
    R("Cumyl Alcohol", "CHP + H2 -> CumylAlcohol + H2O", CAT,
      "Cumene hydroperoxide reduced over palladium.", wiki=73970591, cat="Pd", T=60),
    R("1-Phenylethylamine", "Acetophenone + NH3 + H2 -> PhenylEthylamine1 + H2O", CAT,
      "Acetophenone reductively aminated over nickel.", wiki=17096374, cat="Ni", T=120),
    R("DTPA", "DETA + 5 Glycolonitrile + 5 H2O -> DTPA + 5 NH3", FLASK,
      "Diethylenetriamine takes five glycolonitriles; the nitriles are hydrolysed.", wiki=4746146, T=100),
    R("Cyclohexylpyrrolidone", "GBL + Cyclohexylamine -> CHPyrrolidone + H2O", PRESS,
      "gamma-Butyrolactone heated with cyclohexylamine.", wiki=33304425, T=250),
    R("2-Methylimidazole", "Glyoxal + Acetaldehyde + 2 NH3 -> MeImidazole2 + 3 H2O", MIX,
      "Glyoxal, acetaldehyde and ammonia close a ring.", wiki=44787630),
    R("Bis-tris", "Tris + 2 EO -> BisTris", PRESS,
      "Tris takes two ethylene oxides on its nitrogen.", wiki=5447687, T=80),
    R("Hunig's Base", "iPr2NH + Ethanol -> DIPEA + H2O", CAT,
      "Diisopropylamine ethylated over nickel.", wiki=2445897, cat="Ni", T=200),
    R("Nitrilotriacetonitrile", "NH3 + 3 Glycolonitrile -> NTAN + 3 H2O", MIX,
      "Ammonia takes three glycolonitriles.", wiki=53767947),
    R("Fluoroform", "CHCl3 + 3 HF -> HFC23 + 3 HCl", HIGHP,
      "Chloroform fluorinated all the way; most HFC-23 is the unwanted tail of HCFC-22 plants.", wiki=2814674,
      cat="SbCl5", T=100),
    R("tert-Amyl Alcohol", "Isoamylene + H2O -> tAmylOH", CAT,
      "2-Methyl-2-butene hydrated in sulfuric acid.", wiki=17507722, cat="H2SO4", T=40),
    R("tert-Butyl Formate", "Isobutylene + Formic -> tBuFormate", CAT,
      "Formic acid adds to isobutylene.", wiki=15215330, cat="H2SO4", T=20),
    R("Ethynylcyclohexanol", "Cyclohexanone + Acetylene -> Ethynylcyclohexanol", CAT,
      "Acetylene adds to cyclohexanone in potassium hydroxide (Favorskii).", wiki=65147107,
      cat="KOH", T=20),
    R("Methacrylamide", "ACH -> Methacrylamide", CAT,
      "Acetone cyanohydrin dehydrated and hydrolysed in concentrated sulfuric acid.", wiki=36119332,
      cat="H2SO4", T=130),
]
E6.reactions += [
    R("Perfluoropropane", "Propane + 8 HF -> C3F8 + 8 H2", ECELL,
      "Every hydrogen of propane swapped for fluorine electrochemically.", wiki=2456281),
    R("Methacrolein", "Isobutylene + O2 -> Methacrolein + H2O", CAT,
      "Isobutylene oxidised over bismuth molybdate (Japan, 1980s).", wiki=5684046, cat="MoO3", T=350),
]

import authored_canon_13  # noqa: E402,F401
