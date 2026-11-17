"""
Curieosity's industrial chemistry, part 5 (see authored_canon.py).
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E1, E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)


# --- intermediates the canon set lacks ---------------------------------------------------
S(None, "DETA", "Diethylenetriamine", "C4H13N3", "Liquid", "Diethylenetriamine",
  "Three amines on an ethylene chain: an epoxy hardener, and the backbone of the chelating agent DTPA.",
  smiles="NCCNCCN")

# --- the canon substances ------------------------------------------------------------------
S("111-60-4", "GMS", "Glycol stearate", "C20H40O3", "Solid", 960882,
  "The ingredient that gives pearly shampoos and soaps their shimmer: tiny plate crystals that catch the light.", lib=2651)
S("112-44-7", "Undecanal", "Undecanal", "C11H22O", "Liquid", 36213139,
  "An aldehyde with a waxy, floral, orange-peel smell, part of the 'aldehydic' note made famous by Chanel No. 5.", lib=2715)
S("115-25-3", "C4F8", "Octafluorocyclobutane", "C4F8", "Gas", 2882491,
  "A ring of four CF2 groups: the gas that etches deep, straight trenches into silicon wafers, and a food-safe propellant.", lib=2781)
S("116-02-9", "TMCHol", "3,3,5-Trimethylcyclohexanol", "C9H18O", "Solid", 58185910,
  "Hydrogenated isophorone, esterified with salicylic acid into homosalate, a sunscreen.", lib=2802)
S("116-16-5", "HexachloroAcetone", "Hexachloroacetone", "C3Cl6O", "Liquid", 3939523,
  "Acetone with every hydrogen replaced by chlorine: a reagent and pesticide intermediate.", lib=2804)
S("118-60-5", "Octisalate", "2-Ethylhexyl salicylate", "C15H22O3", "Liquid", 4345823,
  "Octisalate, a UVB filter in sunscreens since the 1940s.", lib=2832)
S("1184-58-3", "DMAC", "Dimethylaluminium chloride", "C2H6AlCl", "Liquid", 75918232,
  "A pyrophoric organoaluminium co-catalyst for polymerising dienes into synthetic rubber.", lib=2846)
S("1185-55-3", "MTMS", "Methyltrimethoxysilane", "C4H12O3Si", "Liquid", 44271235,
  "A silane that crosslinks room-temperature-curing silicone sealants and makes water-repellent coatings.", lib=2852)
S("120-80-9", "Catechol", "Catechol", "C6H6O2", "Solid", 1629349,
  "1,2-Dihydroxybenzene: the start of vanillin, of the insecticide carbofuran, and of adrenaline's catechol ring.", lib=2897)
S("120-82-1", "TCB124", "1,2,4-Trichlorobenzene", "C6H3Cl3", "Liquid", 9666869,
  "A high-boiling solvent, once a dielectric fluid and termite killer.", lib=2898)
S("12159-07-8", "Cu5Si", "Copper silicide", "Cu5Si", "Solid", 9421020,
  "The copper-silicon alloy that forms in the silicone process's contact mass, where silicon meets methyl chloride.", lib=3005)
S("123-07-9", "EthylPhenol4", "4-Ethylphenol", "C8H10O", "Solid", 4330316,
  "The 'barnyard' or 'horse sweat' smell that Brettanomyces yeast leaves in red wine.", lib=3061)
S("123-41-1", "CholineOH", "Choline hydroxide", "C5H15NO2", "Aqueous", 73000026,
  "A strong organic base, used to strip photoresist from chips and as a feed and supplement form of choline.", lib=3074)
S("124-63-0", "MsCl", "Methanesulfonyl chloride", "CH3ClO2S", "Liquid", 13830669,
  "Mesyl chloride, which turns alcohols into mesylates, good leaving groups for drug synthesis.", lib=3112)
S("1241-94-7", "EHDPP", "2-Ethylhexyl diphenyl phosphate", "C20H27O4P", "Liquid", 65319776,
  "A flame-retardant plasticiser for PVC.", lib=3119)
S("127-19-5", "DMAc", "Dimethylacetamide", "C4H9NO", "Liquid", 2258395,
  "A polar solvent for spinning spandex and acrylic fibres, and for making polyimide film.", lib=3186)
S("1338-23-4", "MEKP", "Methyl ethyl ketone peroxide", "C8H18O6", "Liquid", 653060,
  "The hardener squeezed into polyester resin to cure fibreglass boats and car-body filler.", lib=3400)
S("134-62-3", "DEET", "DEET", "C12H17NO", "Liquid", 345526,
  "N,N-Diethyl-meta-toluamide, the insect repellent developed by the US Army after jungle warfare in the Second World War (1946).", lib=3415)
S("13674-87-8", "TDCPP", "Tris(1,3-dichloro-2-propyl) phosphate", "C9H15Cl6O4P", "Liquid", 31810959,
  "A flame retardant in furniture foam, once in children's pyjamas until it was found to cause mutations.", lib=3500)
S("13709-94-9", "KBO2", "Potassium metaborate", "KBO2", "Solid", 38626007,
  "A flux for welding and a buffer in photographic developers.", lib=3522)
S("141-05-9", "DEM", "Diethyl maleate", "C8H12O4", "Liquid", 63944402,
  "A diester for making the insecticide malathion.", lib=3614)
S("141-24-2", "MeRicinoleate", "Methyl ricinoleate", "C19H36O3", "Liquid", 55859820,
  "The methyl ester of castor oil's acid, cracked into undecylenic acid on the way to Rilsan, nylon 11.", lib=3621)
S("142-29-0", "Cyclopentene", "Cyclopentene", "C5H8", "Liquid", 2560778,
  "A five-membered ring with a double bond, opened by metathesis into polypentenamer rubber.", lib=3649)
S("142-84-7", "Dipropylamine", "Dipropylamine", "C6H15N", "Liquid", 22323465,
  "An amine for making the herbicides trifluralin and vernolate.", lib=3660)
S("142-96-1", "DBE", "Dibutyl ether", "C8H18O", "Liquid", 3199533,
  "A water-shy ether solvent, safer than diethyl ether for Grignard reactions.", lib=3665)
S("144538-83-0", "Na4IDS", "Tetrasodium iminodisuccinate", "C8H7NNa4O8", "Solid", 57160580,
  "A biodegradable chelating agent that replaces EDTA in detergents and fertilisers.", lib=3721)
S("156-60-5", "tDCE", "trans-1,2-Dichloroethylene", "C2H2Cl2", "Liquid", 4027298,
  "A degreasing solvent for electronics and a blowing agent.", lib=3922)
S("16731-55-8", "K2S2O5", "Potassium metabisulfite", "K2S2O5", "Solid", 2883343,
  "The Campden tablet of home brewers and winemakers: it releases sulfur dioxide to kill wild yeasts and bacteria.", lib=4063)
S("182636-01-7", "Hexadecene", "1-Hexadecene", "C16H32", "Liquid", 54487875,
  "A sixteen-carbon alpha-olefin for drilling muds and surfactants.", lib=4218)
S("1929-82-4", "Nitrapyrin", "Nitrapyrin", "C6H3Cl4N", "Solid", 44305733,
  "A nitrogen stabiliser: it slows the soil bacteria that turn fertiliser ammonium into nitrate, which washes away.", lib=4300)
S("20654-88-0", "BF3", "Boron trifluoride", "BF3", "Gas", 1647344,
  "A pungent gas and powerful Lewis acid, the catalyst for many polymerisations and alkylations.", lib=8010)
S("2272-11-9", "MEAOleate", "Ethanolamine oleate", "C20H41NO3", "Solid", 13574246,
  "A soap of ethanolamine and oleic acid: an emulsifier and, injected, a drug that shrinks varicose veins.", lib=4545)
S("2452-01-9", "ZnLaurate", "Zinc laurate", "C24H46O4Zn", "Solid", 72894674,
  "A zinc soap used as a lubricant and release agent in rubber and plastics.", lib=4659)
S("2487-90-3", "TMOS_H", "Trimethoxysilane", "C3H10O3Si", "Liquid", 73212942,
  "A silane with an Si-H bond, the start of silane coupling agents that bond glass fibre to resin.", lib=4693)
S("2524-64-3", "DPCP", "Diphenyl chlorophosphate", "C12H10ClO3P", "Solid", 7352676,
  "A phosphorylating agent for making flame retardants and drugs.", lib=4743)
S("29118-24-9", "HFO1234ze", "trans-1,3,3,3-Tetrafluoropropene", "C3H2F4", "Gas", 34066865,
  "HFO-1234ze(E), a low-warming refrigerant for chillers and a foam blowing agent.", lib=5090)
S("3030-47-5", "PMDETA", "Pentamethyldiethylenetriamine", "C9H23N3", "Liquid", 17155023,
  "A catalyst that makes polyurethane foam blow, and a ligand that tames organolithium reagents.", lib=5183)
S("31506-43-1", "DMAPU", "Dimethylaminopropylurea", "C6H15N3O", "Solid", 78909914,
  "A low-odour, reactive catalyst for polyurethane foam that is built into the polymer.", lib=5267)
S("75-98-9", "PivalicAcid", "Pivalic acid", "C5H10O2", "Solid", 6811852,
  "Trimethylacetic acid, made by the Koch reaction: its bulky esters resist hydrolysis.", lib=7927)
S("3282-30-2", "PivaloylCl", "Pivaloyl chloride", "C5H9ClO", "Liquid", 54437604,
  "The acid chloride of pivalic acid, for drugs, pesticides and peroxide initiators.", lib=5332)
S("128-37-0", "BHT", "Butylated hydroxytoluene", "C15H24O", "Solid", 84808,
  "BHT (E321): the antioxidant in cereals, chewing gum, rubber, fuels and cosmetics.", lib=3217)

E4.reactions += [
    R("Boron Trifluoride", "H3BO3 + 3 HF -> BF3 + 3 H2O", FLASK,
      "Boric acid and hydrogen fluoride (Gay-Lussac and Thenard, 1808).", wiki=1647344, T=50),
    R("Catechol from Phenol", "Phenol + H2O2 -> Catechol + H2O", CAT,
      "Phenol hydroxylated by hydrogen peroxide over titanium silicalite, a zeolite with titanium in its framework.",
      wiki=1629349, cat="ZSM5", T=90),
    R("Trichlorobenzene", "pDCB + Cl2 -> TCB124 + HCl", CAT,
      "p-Dichlorobenzene chlorinated once more.", wiki=9666869, cat="FeCl3", T=60),
    R("Potassium Metabisulfite", "Potash + 2 SO2 -> K2S2O5 + CO2", MIX,
      "Sulfur dioxide bubbled through potash solution.", wiki=2883343),
    R("Potassium Metaborate", "H3BO3 + KOH -> KBO2 + 2 H2O", MIX,
      "Boric acid neutralised by caustic potash.", wiki=38626007),
]
E5.reactions += [
    R("Glycol Stearate", "EG + StearicAcid -> GMS + H2O", CAT,
      "Stearic acid esterified with ethylene glycol.", wiki=960882, cat="H2SO4", T=180),
    R("Undecanal", "Decene + CO + H2 -> Undecanal", CAT,
      "1-Decene hydroformylated with a rhodium catalyst.", wiki=36213139, cat="Rh", T=100),
    R("Octafluorocyclobutane", "2 TFE -> C4F8", PRESS,
      "Tetrafluoroethylene dimerises on heating; it is also a by-product of making it.", wiki=2882491, T=600),
    R("Trimethylcyclohexanol", "Isophorone + 2 H2 -> TMCHol", CAT,
      "Isophorone hydrogenated over nickel.", wiki=58185910, cat="Ni", T=120),
    R("Hexachloroacetone", "Acetone + 6 Cl2 -> HexachloroAcetone + 6 HCl", LIGHT,
      "Acetone chlorinated exhaustively.", wiki=3939523, T=100),
    R("Octisalate", "Salicylic + 2EH -> Octisalate + H2O", CAT,
      "Salicylic acid esterified with 2-ethylhexanol.", wiki=4345823, cat="H2SO4", T=150),
    R("Dimethylaluminium Chloride", "TMA + AlCl3 -> 3 DMAC", MIX,
      "Trimethylaluminium and aluminium chloride swap methyls and chlorines.", wiki=75918232),
    R("Methyltrimethoxysilane", "MeSiCl3 + 3 Methanol -> MTMS + 3 HCl", FLASK,
      "Methyltrichlorosilane esterified with methanol.", wiki=44271235, T=60),
    R("Copper Silicide", "5 Cu + Si -> Cu5Si", ARC,
      "Copper and silicon fused together.", wiki=9421020, T=1100),
    R("4-Ethylphenol", "Phenol + Ethylene -> EthylPhenol4", CAT,
      "Phenol ethylated over aluminium chloride.", wiki=4330316, cat="AlCl3", T=100),
    R("Choline Hydroxide", "Me3N + EO + H2O -> CholineOH", FLASK,
      "Trimethylamine and ethylene oxide in water.", wiki=73000026, T=40),
    R("Mesyl Chloride", "Methane + SO2 + Cl2 -> MsCl + HCl", LIGHT,
      "The Reed reaction: methane sulfochlorinated by sulfur dioxide and chlorine under light.", wiki=13830669, T=40),
    R("2-Ethylhexyl Diphenyl Phosphate", "POCl3 + 2 Phenol + 2EH -> EHDPP + 3 HCl", FLASK,
      "Phosphorus oxychloride esterified with phenol and 2-ethylhexanol.", wiki=65319776, T=120),
    R("Dimethylacetamide", "Me2NH + AcOH -> DMAc + H2O", HEAT,
      "Dimethylamine and acetic acid heated together.", wiki=2258395, T=200),
    R("MEK Peroxide", "2 MEK + 3 H2O2 -> MEKP + 2 H2O", FLASK,
      "Methyl ethyl ketone and hydrogen peroxide with an acid catalyst, kept cold.", wiki=653060, T=20),
    R("DEET", "2 mXylene + 3 O2 + 2 Diethylamine -> 2 DEET + 4 H2O", CAT,
      "m-Xylene oxidised to m-toluic acid, whose acid chloride is aminated with diethylamine (US Army, 1946).",
      wiki=345526, cat="Co", T=150),
    R("TDCPP", "3 Epichlorohydrin + POCl3 -> TDCPP", CAT,
      "Phosphorus oxychloride opens three epichlorohydrins.", wiki=31810959, cat="AlCl3", T=80),
    R("Diethyl Maleate", "MaleicAnhydride + 2 Ethanol -> DEM + H2O", CAT,
      "Maleic anhydride esterified with ethanol.", wiki=63944402, cat="H2SO4", T=90),
    R("Methyl Ricinoleate", "CastorOil + 3 Methanol -> 3 MeRicinoleate + Glycerol", CAT,
      "Castor oil transesterified with methanol.", wiki=55859820, cat="NaOMe", T=60),
    R("Cyclopentene", "Cyclopentadiene + H2 -> Cyclopentene", CAT,
      "Cyclopentadiene half-hydrogenated over palladium.", wiki=2560778, cat="Pd", T=50),
    R("Dipropylamine", "Propylamine + Propanol -> Dipropylamine + H2O", CAT,
      "Propylamine aminated again by 1-propanol over nickel.", wiki=22323465, cat="Ni", T=200),
    R("Dibutyl Ether", "2 Butanol -> DBE + H2O", CAT,
      "Butanol dehydrated by sulfuric acid.", wiki=3199533, cat="H2SO4", T=135),
    R("Iminodisuccinate", "2 MaleicAnhydride + NH3 + 4 NaOH -> Na4IDS + 2 H2O", FLASK,
      "Ammonia adds to two maleates in caustic soda (Bayer, 1990s).", wiki=57160580, T=100),
    R("trans-Dichloroethylene", "Acetylene + Cl2 -> tDCE", CAT,
      "Chlorine adds once to acetylene.", wiki=4027298, cat="FeCl3", T=40),
    R("Nitrapyrin", "Picoline2 + 4 Cl2 -> Nitrapyrin + 4 HCl", LIGHT,
      "2-Picoline chlorinated on its methyl group and once on the ring (Dow, 1960s).", wiki=44305733, T=150),
    R("Ethanolamine Oleate", "MEA + OleicAcid -> MEAOleate", MIX,
      "Ethanolamine neutralised by oleic acid.", wiki=13574246),
    R("Zinc Laurate", "ZnO + 2 LauricAcid -> ZnLaurate + H2O", MIX,
      "Zinc oxide stirred into molten lauric acid.", wiki=72894674),
    R("Trimethoxysilane", "Si + 3 Methanol -> TMOS_H + H2", CAT,
      "Silicon reacted directly with methanol over copper.", wiki=73212942, cat="Cu", T=250),
    R("Diphenyl Chlorophosphate", "POCl3 + 2 Phenol -> DPCP + 2 HCl", FLASK,
      "Phosphorus oxychloride with two phenols.", wiki=7352676, T=120),
    R("Diethylenetriamine", "MEA + EDA -> DETA + H2O", CAT,
      "Ethanolamine aminated by ethylenediamine over nickel.", wiki="Diethylenetriamine", cat="Ni", T=200),
    R("PMDETA", "DETA + 5 CH2O + 5 H2 -> PMDETA + 5 H2O", CAT,
      "Diethylenetriamine methylated five times by formaldehyde and hydrogen.", wiki=17155023, cat="Ni", T=120),
    R("Dimethylaminopropylurea", "DMAPA + Urea -> DMAPU + NH3", HEAT,
      "DMAPA heated with urea.", wiki=78909914, T=150),
    R("Koch Pivalic Acid", "Isobutylene + CO + H2O -> PivalicAcid", HIGHP,
      "The Koch reaction: isobutylene and carbon monoxide in strong acid.", wiki=6811852, cat="HF", T=50),
    R("Pivaloyl Chloride", "3 PivalicAcid + PCl3 -> 3 PivaloylCl + H3PO3", FLASK,
      "Pivalic acid chlorinated with phosphorus trichloride.", wiki=54437604, T=60),
    R("BHT", "pCresol + 2 Isobutylene -> BHT", CAT,
      "p-Cresol alkylated twice with isobutylene.", wiki=84808, cat="H2SO4", T=80),
]
E6.reactions += [
    R("Hexadecene", "Dodecene + 2 Ethylene -> Hexadecene", CAT,
      "Two more ethylenes on the growing chain.", wiki=54487875, cat="Ni", T=100),
    R("HFO-1234ze", "HFC245fa -> HFO1234ze + HF", CAT,
      "HFC-245fa stripped of hydrogen fluoride over chromia.", wiki=34066865, cat="Cr2O3", T=350),
]

import authored_canon_6  # noqa: E402,F401
