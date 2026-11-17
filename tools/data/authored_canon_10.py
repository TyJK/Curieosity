"""
Curieosity's industrial chemistry, part 10 (see authored_canon.py).
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E1, E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)


# --- the canon substances ------------------------------------------------------------------
S("104-50-7", "OctaLactone", "gamma-Octalactone", "C8H14O2", "Liquid", 55169547,
  "The creamy coconut note of flavours and perfumes.", lib=2282)
S("104-87-0", "pTolualdehyde", "4-Methylbenzaldehyde", "C8H8O", "Liquid", 18679470,
  "A sweet, cherry-almond aldehyde for flavours, and a building block for drugs.", lib=2293)
S("104-93-8", "MethylAnisole", "4-Methylanisole", "C8H10O", "Liquid", 57022013,
  "A sweet, floral ylang-ylang note in perfumes.", lib=2295)
S("112-16-3", "LauroylCl", "Lauroyl chloride", "C12H23ClO", "Liquid", 70303463,
  "The acid chloride of lauric acid, for surfactants and lauroyl peroxide.", lib=2707)
S("105-74-8", "LPO", "Lauroyl peroxide", "C24H46O4", "Solid", 70302736,
  "A gentle radical initiator for PVC suspension polymerisation.", lib=2340)
S("105-76-0", "DBMaleate", "Dibutyl maleate", "C12H20O4", "Liquid", 60410609,
  "A comonomer that softens vinyl acetate copolymers in paints and adhesives.", lib=2341)
S("106-47-8", "pChloroaniline", "4-Chloroaniline", "C6H6ClN", "Solid", 13972916,
  "The aniline of the herbicide monuron and the antiseptic chlorhexidine.", lib=2390)
S("106-70-7", "MethylHexanoate", "Methyl hexanoate", "C7H14O2", "Liquid", 64822178,
  "A fruity, pineapple-like ester for flavours.", lib=2398)
S("106-95-6", "AllylBromide", "Allyl bromide", "C3H5Br", "Liquid", 7094325,
  "An allylating agent for drugs and polymers.", lib=2406)
S("107-11-9", "Allylamine", "Allylamine", "C3H7N", "Liquid", 5120958,
  "The simplest unsaturated amine, polymerised into sevelamer, a drug that binds phosphate in kidney patients.", lib=2439)
S("107-43-7", "Betaine", "Betaine", "C5H11NO2", "Solid", 1623599,
  "Trimethylglycine, first found in sugar beet (Beta): an animal feed additive and a cell's protection against salt.", lib=2454)
S("108-16-7", "DMAIPA", "1-Dimethylamino-2-propanol", "C5H13NO", "Liquid", 52970905,
  "A polyurethane catalyst and a building block for drugs.", lib=2504)
S("108-18-9", "iPr2NH", "Diisopropylamine", "C6H15N", "Liquid", 6607062,
  "The amine behind LDA, the bulky base of the organic lab, and the herbicide triallate.", lib=2505)
S("108-48-5", "Lutidine26", "2,6-Lutidine", "C7H9N", "Liquid", 10323570,
  "A hindered pyridine base that mops up acid without reacting itself.", lib=2518)
S("109-87-5", "Methylal", "Dimethoxymethane", "C3H8O2", "Liquid", 5156882,
  "Methylal: a solvent and aerosol propellant, and a clean-burning diesel additive.", lib=2567)
S("109-92-2", "EVE", "Ethyl vinyl ether", "C4H8O", "Liquid", 59665517,
  "A vinyl ether monomer for adhesives, and a protecting group in the lab.", lib=2569)
S("110-01-0", "THT", "Tetrahydrothiophene", "C4H8S", "Liquid", 4648495,
  "The odorant in much of Europe's natural gas: the smell that warns of a leak.", lib=2582)
S("110-38-3", "EthylDecanoate", "Ethyl decanoate", "C12H24O2", "Liquid", 34438204,
  "A grape and brandy note of wine and spirits.", lib=2597)
S("110-87-2", "DHP", "3,4-Dihydro-2H-pyran", "C5H8O", "Liquid", 29770237,
  "The THP protecting group for alcohols in synthesis.", lib=2610)
S("110-93-0", "MHO", "6-Methyl-5-hepten-2-one", "C8H14O", "Liquid", 61430825,
  "A citrusy ketone on the industrial road to citral, linalool, and vitamins A and E.", lib=2614)
S("111-58-0", "OEA", "Oleoylethanolamide", "C20H39NO2", "Solid", 15918153,
  "A lipid messenger that tells the brain the gut is full; also a cosmetic thickener.", lib=2650)
S("1111-67-7", "CuSCN", "Copper(I) thiocyanate", "CuSCN", "Solid", 49015956,
  "An antifouling pigment for ship hulls and the hole conductor of dye-sensitised solar cells.", lib=2666)
S("112-37-8", "Undecanoic", "Undecanoic acid", "C11H22O2", "Solid", 23779446,
  "An antifungal fatty acid.", lib=2711)
S("113-24-6", "NaPyruvate", "Sodium pyruvate", "C3H3NaO3", "Solid", 8953659,
  "Added to cell culture media as an extra energy source.", lib=2753)
S("115-19-5", "MBE", "2-Methyl-3-butyn-2-ol", "C5H8O", "Liquid", 57780242,
  "Acetone and acetylene joined: the first step of the industrial road to vitamins A and E (Roche, BASF).", lib=2779)
S("116-53-0", "MethylButanoic2", "2-Methylbutanoic acid", "C5H10O2", "Liquid", 56657901,
  "A fruity, cheesy acid for flavours and synthetic lubricants.", lib=2807)
S("1163-19-5", "DecaBDE", "Decabromodiphenyl ether", "C12Br10O", "Solid", 9115966,
  "A flame retardant in TV casings until banned under the Stockholm Convention in 2017.", lib=2811)
S("118-48-9", "IsatoicAnhydride", "Isatoic anhydride", "C8H5NO3", "Solid", 56256904,
  "A building block for anthranilate drugs, dyes and fragrances.", lib=2828)
S("118-74-1", "HCB", "Hexachlorobenzene", "C6Cl6", "Solid", 4047871,
  "A seed fungicide that poisoned thousands in Turkey in the 1950s when treated grain was eaten; banned under the Stockholm Convention.", lib=2834)
S("118-75-2", "Chloranil", "Chloranil", "C6Cl4O2", "Solid", 23606776,
  "A quinone oxidiser for dehydrogenation in the lab and for dyes.", lib=2835)
S("1191-15-7", "DIBAL", "Diisobutylaluminium hydride", "C8H19Al", "Liquid", 2229421,
  "DIBAL, the reducing agent that stops at the aldehyde.", lib=2872)
S("121-46-0", "NBD", "Norbornadiene", "C7H8", "Liquid", 2515452,
  "Light turns it into strained quadricyclane, which stores the energy to release it later as heat.", lib=2984)
S("12122-17-7", "Hydrozincite", "Hydrozincite", "Zn5(CO3)2(OH)6", "Solid", 865142,
  "Basic zinc carbonate: a zinc ore, and the pink-free base of calamine lotion and rubber activators.", lib=2997)
S("122-52-1", "TEPite", "Triethyl phosphite", "C6H15O3P", "Liquid", 14236637,
  "The reagent of the Arbuzov reaction, and a ligand and stabiliser.", lib=3027)
S("122-60-1", "PGE", "Phenyl glycidyl ether", "C9H10O2", "Liquid", 70916836,
  "A reactive diluent for epoxy resins.", lib=3028)
S("122-79-2", "PhenylAcetate", "Phenyl acetate", "C8H8O2", "Liquid", 33984502,
  "The ester that the Fries rearrangement turns into hydroxyacetophenone.", lib=3032)
S("123-19-3", "Heptanone4", "4-Heptanone", "C7H14O", "Liquid", 30265777,
  "Dipropyl ketone, made by ketonising butyric acid: a solvent and fruity flavour.", smiles="O=C(CCC)CCC")
S("123-75-1", "Pyrrolidine", "Pyrrolidine", "C4H9N", "Liquid", 2016821,
  "A five-membered cyclic amine, part of drugs from nicotine to procyclidine, and of enamine chemistry.", lib=3083)
S("12397-32-9", "Zn3P2", "Zinc phosphide", "Zn3P2", "Solid", 5119797,
  "A rodenticide that releases phosphine in the stomach, and a solar-cell semiconductor.", lib=3323)
S("124-73-2", "Halon2402", "Dibromotetrafluoroethane", "C2Br2F4", "Liquid", 20201115,
  "Halon 2402, a fire suppressant still kept on Soviet-built ships and aircraft; banned for new uses.", lib=3116)
S("124-76-5", "Isoborneol", "Isoborneol", "C10H18O", "Solid", 3416970,
  "The alcohol oxidised into synthetic camphor.", lib=3117)
S("125-20-2", "Thymolphthalein", "Thymolphthalein", "C28H30O4", "Solid", 1145355,
  "A pH indicator that turns from clear to blue around pH 10, and a disappearing ink.", lib=3129)
S("12751-22-3", "FeP", "Iron phosphide", "FeP", "Solid", 22509369,
  "Ferrophosphorus, a by-product of phosphorus furnaces, added to steel and to anti-slip concrete.", lib=3205)
S("1314-06-3", "Ni2O3", "Nickel(III) oxide", "Ni2O3", "Solid", 4119350,
  "A black oxide for nickel batteries and ceramics.", lib=3318)
S("13252-13-6", "GenX", "HFPO dimer acid", "C6HF11O3", "Liquid", 54626167,
  "GenX, Chemours's replacement (2009) for PFOA in making fluoropolymers; it too was found in drinking water downstream.", lib=3353)
S("13455-36-2", "CoPO4", "Cobalt(II) phosphate", "Co3(PO4)2", "Solid", 41497935,
  "Cobalt violet, an artists' pigment, and a catalyst that splits water.", lib=3438)

E4.reactions += [
    R("Chloranil", "Hydroquinone + 5 Cl2 -> Chloranil + 6 HCl", FLASK,
      "Hydroquinone chlorinated and oxidised.", wiki=23606776, T=60),
    R("Allyl Bromide", "AllylAlcohol + HBr -> AllylBromide + H2O", MIX,
      "Allyl alcohol and hydrobromic acid.", wiki=7094325),
    R("Betaine", "Me3N + ClAcOH -> Betaine + HCl", FLASK,
      "Trimethylamine and chloroacetic acid.", wiki=1623599, T=60),
    R("Hydrozincite", "5 ZnO + 2 CO2 + 3 H2O -> Hydrozincite", MIX,
      "Zinc oxide slurried with carbon dioxide.", wiki=865142),
    R("Zinc Phosphide", "6 Zn + P4 -> 2 Zn3P2", HEAT,
      "Zinc and phosphorus heated together.", wiki=5119797, T=500),
    R("Ferrophosphorus", "4 Fe + P4 -> 4 FeP", HEAT,
      "Iron and phosphorus; in the phosphorus furnace it forms from the iron in the ore.", wiki=22509369, T=1000),
    R("Nickel(III) Oxide", "4 NiCO3 + O2 -> 2 Ni2O3 + 4 CO2", HEAT,
      "Nickel carbonate roasted in air.", wiki=4119350, T=400),
    R("Cobalt Violet", "3 CoCO3 + 2 H3PO4 -> CoPO4 + 3 CO2 + 3 H2O", MIX,
      "Cobalt carbonate and phosphoric acid (Salvetat, 1859).", wiki=41497935),
    R("Thymolphthalein", "PhthalicAnhydride + 2 Thymol -> Thymolphthalein + H2O", CAT,
      "Phthalic anhydride condensed with thymol.", wiki=1145355, cat="ZnCl2", T=120),
    R("Copper(I) Thiocyanate", "2 CuSO4 + 2 KSCN + SO2 + 2 H2O -> 2 CuSCN + K2SO4 + 2 H2SO4", MIX,
      "Copper sulfate and thiocyanate, with sulfur dioxide to reduce the copper.", wiki=49015956),
    R("4-Chloroaniline", "NCB + 3 H2 -> pChloroaniline + 2 H2O", CAT,
      "4-Nitrochlorobenzene hydrogenated over platinum, sparing the chlorine.", wiki=13972916, cat="Pt", T=80),
    R("Phenyl Acetate", "Phenol + AceticAnhydride -> PhenylAcetate + AcOH", FLASK,
      "Phenol acetylated by acetic anhydride.", wiki=33984502, T=100),
]
E5.reactions += [
    R("gamma-Octalactone", "Pentanol + AcrylicAcid -> OctaLactone + H2O", FLASK,
      "A radical adds pentanol across acrylic acid, and the product closes into a lactone.", wiki=55169547, T=150),
    R("p-Tolualdehyde", "Toluene + CO -> pTolualdehyde", CAT,
      "Toluene formylated by carbon monoxide (Gattermann-Koch).", wiki=18679470, cat="AlCl3", T=30),
    R("4-Methylanisole", "pCresol + Methanol -> MethylAnisole + H2O", CAT,
      "p-Cresol methylated over alumina.", wiki=57022013, cat="Alumina", T=300),
    R("Lauroyl Chloride", "3 LauricAcid + PCl3 -> 3 LauroylCl + H3PO3", FLASK,
      "Lauric acid chlorinated with phosphorus trichloride.", wiki=70303463, T=60),
    R("Lauroyl Peroxide", "2 LauroylCl + H2O2 + 2 NaOH -> LPO + 2 NaCl + 2 H2O", FLASK,
      "Lauroyl chloride and alkaline hydrogen peroxide.", wiki=70302736, T=10),
    R("Dibutyl Maleate", "MaleicAnhydride + 2 Butanol -> DBMaleate + H2O", CAT,
      "Maleic anhydride esterified with butanol.", wiki=60410609, cat="H2SO4", T=120),
    R("Methyl Hexanoate", "Hexanoic + Methanol -> MethylHexanoate + H2O", CAT,
      "Hexanoic acid esterified with methanol.", wiki=64822178, cat="H2SO4", T=80),
    R("Allylamine", "AllylChloride + 2 NH3 -> Allylamine + NH4Cl", PRESS,
      "Allyl chloride in a large excess of ammonia under pressure.", wiki=5120958, T=50),
    R("Dimethylaminoisopropanol", "PO + Me2NH -> DMAIPA", PRESS,
      "Propylene oxide opened by dimethylamine.", wiki=52970905, T=100),
    R("Diisopropylamine", "Acetone + Isopropylamine + H2 -> iPr2NH + H2O", CAT,
      "Acetone reductively aminated by isopropylamine over nickel.", wiki=6607062, cat="Ni", T=150),
    R("2,6-Lutidine", "2 Acetone + CH2O + NH3 -> Lutidine26 + 3 H2O + H2", CAT,
      "Acetone, formaldehyde and ammonia close into a pyridine ring over alumina.", wiki=10323570,
      cat="Alumina", T=400),
    R("Methylal", "2 Methanol + CH2O -> Methylal + H2O", CAT,
      "Formaldehyde and methanol over an acid catalyst.", wiki=5156882, cat="H2SO4", T=60),
    R("Ethyl Vinyl Ether", "Acetylene + Ethanol -> EVE", CAT,
      "Reppe vinylation of ethanol.", wiki=59665517, cat="KOH", T=150),
    R("Tetrahydrothiophene", "THF + H2S -> THT + H2O", CAT,
      "Tetrahydrofuran's oxygen swapped for sulfur over alumina.", wiki=4648495, cat="Alumina", T=400),
    R("Ethyl Decanoate", "Decanoic + Ethanol -> EthylDecanoate + H2O", CAT,
      "Decanoic acid esterified with ethanol.", wiki=34438204, cat="H2SO4", T=90),
    R("Dihydropyran", "THFA -> DHP + H2O", CAT,
      "Tetrahydrofurfuryl alcohol dehydrated over alumina; the ring grows by one.", wiki=29770237,
      cat="Alumina", T=350),
    R("Methylheptenone", "Isoprene + Acetone -> MHO", CAT,
      "Prenyl chloride, from isoprene, alkylates acetone in caustic soda.", wiki=61430825, cat="NaOH", T=60),
    R("Oleoylethanolamide", "OleicAcid + MEA -> OEA + H2O", HEAT,
      "Oleic acid heated with ethanolamine.", wiki=15918153, T=170),
    R("Undecanoic Acid", "UndecylenicAcid + H2 -> Undecanoic", CAT,
      "Undecylenic acid hydrogenated over nickel.", wiki=23779446, cat="Ni", T=150),
    R("Sodium Pyruvate", "PyruvicAcid + NaOH -> NaPyruvate + H2O", MIX,
      "Pyruvic acid neutralised.", wiki=8953659),
    R("Methylbutynol", "Acetone + Acetylene -> MBE", CAT,
      "The Favorskii reaction: acetylene adds to acetone in potassium hydroxide.", wiki=57780242, cat="KOH", T=20),
    R("2-Methylbutanoic Acid", "2-Butene + CO + H2O -> MethylButanoic2", HIGHP,
      "The Koch reaction on butenes.", wiki=56657901, cat="HF", T=50),
    R("DecaBDE", "DiphenylEther + 10 Br2 -> DecaBDE + 10 HBr", FLASK,
      "Diphenyl ether brominated all the way round.", wiki=9115966, T=60),
    R("Isatoic Anhydride", "Anthranilic + COCl2 -> IsatoicAnhydride + 2 HCl", FLASK,
      "Anthranilic acid and phosgene.", wiki=56256904, T=40),
    R("Hexachlorobenzene", "TCB124 + 3 Cl2 -> HCB + 3 HCl", CAT,
      "Trichlorobenzene chlorinated to the end.", wiki=4047871, cat="FeCl3", T=200),
    R("DIBAL", "TIBA -> DIBAL + Isobutylene", HEAT,
      "Triisobutylaluminium heated until one isobutyl leaves as isobutylene.", wiki=2229421, T=150),
    R("Norbornadiene", "Cyclopentadiene + Acetylene -> NBD", PRESS,
      "Cyclopentadiene and acetylene in a Diels-Alder reaction.", wiki=2515452, T=200),
    R("Triethyl Phosphite", "PCl3 + 3 Ethanol + 3 NH3 -> TEPite + 3 NH4Cl", FLASK,
      "Phosphorus trichloride and ethanol, with a base to take the hydrogen chloride.", wiki=14236637, T=10),
    R("Phenyl Glycidyl Ether", "Phenol + Epichlorohydrin + NaOH -> PGE + NaCl + H2O", FLASK,
      "Phenol joined to epichlorohydrin.", wiki=70916836, T=60),
    R("4-Heptanone", "2 Butyric -> Heptanone4 + CO2 + H2O", CAT,
      "Butyric acid ketonised over manganese oxide.", wiki=30265777, cat="MnO2", T=400),
    R("Pyrrolidine", "BDO + NH3 -> Pyrrolidine + 2 H2O", CAT,
      "1,4-Butanediol and ammonia close a ring over alumina.", wiki=2016821, cat="Alumina", T=300),
    R("Halon 2402", "TFE + Br2 -> Halon2402", MIX,
      "Bromine adds across tetrafluoroethylene.", wiki=20201115),
    R("Isoborneol", "IsobornylAcetate + NaOH -> Isoborneol + NaC2H3O2", MIX,
      "Isobornyl acetate saponified.", wiki=3416970),
]
E6.reactions += [
    R("GenX", "2 HFPO + H2O -> GenX + HF", FLASK,
      "Hexafluoropropylene oxide dimerised to the acid fluoride, then hydrolysed.", wiki=54626167, T=40),
]

import authored_canon_11  # noqa: E402,F401
