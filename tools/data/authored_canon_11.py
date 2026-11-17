"""
Curieosity's industrial chemistry, part 11 (see authored_canon.py).
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E1, E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)


# --- the canon substances ------------------------------------------------------------------
S("13466-78-9", "Carene", "3-Carene", "C10H16", "Liquid", 3229334,
  "A sweet, pungent terpene that makes up much of Indian and Scots pine turpentine.", lib=3442)
S("13770-61-1", "InNO33", "Indium(III) nitrate", "In(NO3)3", "Solid", 65771592,
  "The indium salt from which indium tin oxide, the transparent conductor of touchscreens, is made.", lib=3535)
S("139-13-9", "NTA", "Nitrilotriacetic acid", "C6H9NO6", "Solid", 4497595,
  "The free acid of NTA, a chelating agent.", lib=3569)
S("140-95-4", "DMU", "Dimethylolurea", "C3H8N2O3", "Solid", 52107894,
  "Urea with two formaldehydes: the resin precursor of crease-resistant cotton finishes.", lib=3601)
S("142-18-7", "Monolaurin", "Monolaurin", "C15H30O4", "Solid", 17696820,
  "Glycerol monolaurate, an emulsifier with antimicrobial power, found naturally in coconut oil and breast milk.", lib=3645)
S("1493-13-6", "TfOH", "Triflic acid", "CHF3O3S", "Liquid", 4141488,
  "Trifluoromethanesulfonic acid, one of the strongest acids that can be bottled, used as a catalyst for alkylations and polymerisations.",
  lib=3810, props=("IsAcid",))
S("150-46-9", "TEB", "Triethyl borate", "C6H15BO3", "Liquid", 2237903,
  "Burns with a vivid green flame, the classic flame test for boron; also a welding flux.", lib=3824)
S("156-43-4", "Phenetidine", "p-Phenetidine", "C8H11NO", "Liquid", 60303387,
  "The aniline of phenacetin, the 1887 painkiller, and of the antioxidant ethoxyquin.", lib=3921)
S("16096-31-4", "HDDGE", "1,6-Hexanediol diglycidyl ether", "C12H22O4", "Liquid", 70503379,
  "A flexibilising reactive diluent for epoxy resins.", lib=3985)
S("16423-68-0", "Erythrosine", "Erythrosine", "C20H6I4Na2O5", "Solid", 2119576,
  "Red No. 3, the cherry-pink dye of glacé cherries and dental disclosing tablets; the US banned it from food in 2025.", smiles="[Na+].[Na+].[O-]C(=O)c1ccccc1-c1c2cc(I)c([O-])c(I)c2oc2c(I)c(=O)c(I)cc12")
S("1678-82-6", "pMenthane", "p-Menthane", "C10H20", "Liquid", 55241687,
  "Hydrogenated p-cymene, oxidised to p-menthane hydroperoxide, the initiator of cold synthetic rubber.", lib=8960)
S("1717-00-6", "HCFC141b", "1,1-Dichloro-1-fluoroethane", "C2H3Cl2F", "Liquid", 23605014,
  "HCFC-141b, the blowing agent of insulating foam in the 1990s and 2000s, now phased out.", lib=4103)
S("1948-33-0", "TBHQ", "tert-Butylhydroquinone", "C10H14O2", "Solid", 5316962,
  "E319, the antioxidant that keeps frying oils and snack foods from going rancid.", lib=4313)
S("2224-15-9", "EGDGE", "Ethylene glycol diglycidyl ether", "C8H14O4", "Liquid", 20362427,
  "A water-soluble epoxy crosslinker for paper, textiles and protein gels.", lib=4509)
S("23128-74-7", "Irganox1098", "Irganox 1098", "C40H64N2O4", "Solid", 47129145,
  "A hindered-phenol antioxidant for nylon fibres and parts.", lib=4564)
S("23519-77-9", "ZrOPr4", "Zirconium propoxide", "C12H28O4Zr", "Liquid", 2524890,
  "A sol-gel precursor for zirconia coatings and a crosslinker for inks.", lib=4582)
S("2380-91-8", "HPE", "1-(4-Hydroxyphenyl)ethanol", "C8H10O2", "Solid", 10733441,
  "Reduced hydroxyacetophenone, dehydrated to 4-vinylphenol for photoresist polymers.", lib=4604)
S("25013-16-5", "BHA", "Butylated hydroxyanisole", "C11H16O2", "Solid", 84809,
  "E320, an antioxidant in fats, cereals, chewing gum and cosmetics.", lib=4713)
S("25340-18-5", "Triethylbenzene", "Triethylbenzene", "C12H18", "Liquid", 60235970,
  "Benzene with three ethyl groups, a by-product of making ethylbenzene.", lib=4767)
S("2568-90-3", "Butylal", "Dibutoxymethane", "C9H20O2", "Liquid", 62822188,
  "Butylal, a gentle solvent for cleaners and cosmetics.", lib=4804)
S("2579-20-6", "BAC13", "1,3-Bis(aminomethyl)cyclohexane", "C8H18N2", "Liquid", 61497626,
  "A cycloaliphatic diamine for epoxy hardeners and light-stable polyurethanes.", lib=4815)
S("2582-30-1", "AGB", "Aminoguanidine bicarbonate", "C2H8N4O3", "Solid", 23086505,
  "A building block for triazole drugs, herbicides and blowing agents.", lib=4819)
S("26628-22-8", "NaN3", "Sodium azide", "NaN3", "Solid", 1172932,
  "Set off by a spark, it turns into nitrogen in milliseconds: the gas of the first car airbags. Also a lab preservative, and very toxic.", lib=4897)
S("288-32-4", "Imidazole", "Imidazole", "C3H4N2", "Solid", 1117286,
  "The five-membered ring of histidine and histamine, and the core of the azole antifungals.", lib=5068)
S("3194-55-6", "HBCD", "Hexabromocyclododecane", "C12H18Br6", "Solid", 7146636,
  "The flame retardant of polystyrene insulation boards, listed under the Stockholm Convention in 2013.", lib=5298)
S("33454-82-9", "LiOTf", "Lithium triflate", "CF3LiO3S", "Solid", 61042055,
  "A lithium salt for polymer electrolytes and a mild Lewis acid catalyst.", lib=5372)
S("3385-41-9", "AmmoniumAdipate", "Ammonium adipate", "C6H16N2O4", "Solid", 14263768,
  "The electrolyte salt of aluminium electrolytic capacitors.", lib=5391)
S("355-42-0", "PFHx", "Perfluorohexane", "C6F14", "Liquid", 5762363,
  "A dense, inert fluorocarbon for electronics cooling and as an ultrasound contrast agent.", lib=5477)
S("359-11-5", "TrFE", "Trifluoroethylene", "C2HF3", "Gas", 76746049,
  "Copolymerised with vinylidene fluoride, it makes the ferroelectric polymer of flexible sensors.", lib=5499)
S("383-63-1", "EtTFA", "Ethyl trifluoroacetate", "C4H5F3O2", "Liquid", 71564812,
  "A reagent that adds trifluoroacetyl groups in drug synthesis.", lib=5640)
S("4111-54-0", "LDA", "Lithium diisopropylamide", "C6H14LiN", "Solid", 1379618,
  "LDA, the strong, bulky base that pulls protons without adding itself: the key to making enolates.", lib=5754)

E3.reactions += [
    R("Carene", "Turpentine -> Carene", COLUMN,
      "3-Carene distilled out of pine turpentine.", wiki=3229334, T=170),
]
E4.reactions += [
    R("Indium Nitrate", "In + 4 HNO3 -> InNO33 + NO + 2 H2O", MIX,
      "Indium dissolved in nitric acid.", wiki=65771592),
    R("Nitrilotriacetic Acid", "Na3NTA + 3 HCl -> NTA + 3 NaCl", MIX,
      "The sodium salt acidified; the free acid crystallises.", wiki=4497595),
    R("Triethyl Borate", "H3BO3 + 3 Ethanol -> TEB + 3 H2O", CAT,
      "Boric acid esterified with ethanol.", wiki=2237903, cat="H2SO4", T=80),
    R("Fluorescein Red", "Fluorescein + 4 I2 + 2 NaOH -> Erythrosine + 4 HI + 2 H2O", MIX,
      "Fluorescein iodinated four times (1876).", wiki=2119576),
    R("Sodium Azide", "2 NaNH2 + N2O -> NaN3 + NaOH + NH3", HEAT,
      "Sodamide and nitrous oxide (Wislicenus).", wiki=1172932, T=190),
    R("Imidazole", "Glyoxal + CH2O + 2 NH3 -> Imidazole + 3 H2O", MIX,
      "Glyoxal, formaldehyde and ammonia close into a ring (Debus, 1858).", wiki=1117286),
    R("Ammonium Adipate", "Adipic + 2 NH3 -> AmmoniumAdipate", MIX,
      "Adipic acid neutralised with ammonia.", wiki=14263768),
]
E5.reactions += [
    R("Dimethylolurea", "Urea + 2 CH2O -> DMU", FLASK,
      "Urea takes two formaldehydes in mild alkali.", wiki=52107894, T=40),
    R("Monolaurin", "Glycerol + LauricAcid -> Monolaurin + H2O", CAT,
      "Glycerol esterified once with lauric acid.", wiki=17696820, cat="NaOH", T=200),
    R("Phenetidine", "NCB + NaOEt + 3 H2 -> Phenetidine + NaCl + 2 H2O", CAT,
      "Nitrochlorobenzene's chlorine swapped for ethoxide, then the nitro group hydrogenated.", wiki=60303387,
      cat="Pd", T=100),
    R("Hexanediol Diglycidyl Ether", "Hexanediol + 2 Epichlorohydrin + 2 NaOH -> HDDGE + 2 NaCl + 2 H2O", FLASK,
      "1,6-Hexanediol joined to two epichlorohydrins.", wiki=70503379, T=60),
    R("p-Menthane", "pCymene + 3 H2 -> pMenthane", CAT,
      "p-Cymene's ring hydrogenated over nickel.", wiki=55241687, cat="Ni", T=150),
    R("TBHQ", "Hydroquinone + Isobutylene -> TBHQ", CAT,
      "Hydroquinone alkylated with isobutylene.", wiki=5316962, cat="H3PO4", T=90),
    R("Glycol Diglycidyl Ether", "EG + 2 Epichlorohydrin + 2 NaOH -> EGDGE + 2 NaCl + 2 H2O", FLASK,
      "Ethylene glycol joined to two epichlorohydrins.", wiki=20362427, T=60),
    R("Irganox 1098", "HMDA + 2 DTBP26 + 2 MethylAcrylate -> Irganox1098 + 2 Methanol", FLASK,
      "The hindered-phenol ester amidated with hexamethylenediamine.", wiki=47129145, T=150),
    R("Zirconium Propoxide", "ZrCl4 + 4 Propanol + 4 NH3 -> ZrOPr4 + 4 NH4Cl", FLASK,
      "Zirconium tetrachloride and propanol, with ammonia to take the hydrogen chloride.", wiki=2524890, T=20),
    R("Hydroxyphenylethanol", "HAP + H2 -> HPE", CAT,
      "4-Hydroxyacetophenone hydrogenated over palladium.", wiki=10733441, cat="Pd", T=80),
    R("BHA", "MEHQ + Isobutylene -> BHA", CAT,
      "4-Methoxyphenol alkylated with isobutylene.", wiki=84809, cat="H3PO4", T=80),
    R("Triethylbenzene", "DEB + Ethylene -> Triethylbenzene", CAT,
      "Diethylbenzene ethylated once more.", wiki=60235970, cat="AlCl3", T=90),
    R("Butylal", "2 Butanol + CH2O -> Butylal + H2O", CAT,
      "Formaldehyde and butanol over an acid catalyst.", wiki=62822188, cat="H2SO4", T=90),
    R("1,3-BAC", "MXDA + 3 H2 -> BAC13", HIGHP,
      "m-Xylylenediamine's ring hydrogenated over rhodium.", wiki=61497626, cat="Rh", T=120),
    R("Aminoguanidine Bicarbonate", "Cyanamide + N2H4 + CO2 + H2O -> AGB", MIX,
      "Hydrazine adds to cyanamide; carbon dioxide precipitates the bicarbonate.", wiki=23086505),
    R("HBCD", "CDT + 3 Br2 -> HBCD", FLASK,
      "Bromine adds across all three double bonds of cyclododecatriene.", wiki=7146636, T=20),
    R("Ethyl Trifluoroacetate", "TFA + Ethanol -> EtTFA + H2O", CAT,
      "Trifluoroacetic acid esterified with ethanol.", wiki=71564812, cat="H2SO4", T=60),
    R("LDA", "iPr2NH + BuLi -> LDA + Butane", FLASK,
      "Diisopropylamine deprotonated by butyllithium.", wiki=1379618, T=-78),
    R("Trifluoroethylene", "CTFE + H2 -> TrFE + HCl", CAT,
      "Chlorotrifluoroethylene's chlorine swapped for hydrogen over palladium.", wiki=76746049, cat="Pd", T=200),
]
E6.reactions += [
    R("Triflic Acid", "MsCl + 3 HF + H2O -> TfOH + HCl + 3 H2", ECELL,
      "Methanesulfonyl chloride fluorinated electrochemically (Simons process), then hydrolysed.", wiki=4141488),
    R("Lithium Triflate", "TfOH + LiOH -> LiOTf + H2O", MIX,
      "Triflic acid neutralised with lithium hydroxide.", wiki=61042055),
    R("HCFC-141b", "VDC + HF -> HCFC141b", CAT,
      "Hydrogen fluoride added to vinylidene chloride.", wiki=23605014, cat="SbCl5", T=60),
    R("Perfluorohexane", "Hexane + 14 HF -> PFHx + 14 H2", ECELL,
      "Every hydrogen of hexane swapped for fluorine by Simons electrochemical fluorination.", wiki=5762363),
]

import authored_canon_12  # noqa: E402,F401
