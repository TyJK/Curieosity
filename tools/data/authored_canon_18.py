"""
Curieosity's industrial chemistry, part 18 (see authored_canon.py): small-volume compounds worth
having. The last of the canon list below ten tonnes a year, and picks from the compounds the list
gives no volume for: the glow-stick oxalate, the anaesthetics, the first sulfa drug, the azo reds
of the 1880s and the magenta of printing ink, and a handful of laboratory classics.
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)

# --- intermediates -----------------------------------------------------------------------
S(None, "OxalylCl", "Oxalyl chloride", "C2Cl2O2", "Liquid", "Oxalyl_chloride",
  "Oxalic acid with both OH groups swapped for chlorine; it falls apart into CO, CO2 and HCl when it works.",
  smiles="O=C(Cl)C(=O)Cl")
S(None, "TsCl", "4-Toluenesulfonyl chloride", "C7H7ClO2S", "Solid", "4-Toluenesulfonyl_chloride",
  "Tosyl chloride: it turns an alcohol's OH into a group that leaves easily.", smiles="Cc1ccc(cc1)S(Cl)(=O)=O")
S(None, "Naphthol2", "2-Naphthol", "C10H8O", "Solid", "2-Naphthol",
  "beta-Naphthol, the coupling partner behind a century of red and orange azo dyes.", smiles="Oc1ccc2ccccc2c1")
S(None, "BONAcid", "3-Hydroxy-2-naphthoic acid", "C11H8O3", "Solid", "3-Hydroxy-2-naphthoic_acid",
  "BON acid, 2-naphthol carboxylated: the coupling half of the lithol rubines and naphthol AS dyes.",
  smiles="OC(=O)c1cc2ccccc2cc1O")
S(None, "Xylidine26", "2,6-Xylidine", "C8H11N", "Liquid", "2,6-Xylidine",
  "The ring of lidocaine and its family of local anaesthetics.", lib=8526)

# --- the canon substances ------------------------------------------------------------------
S("30431-54-0", "CPPO", "CPPO", "C26H24Cl6O8", "Solid", 5518657,
  "The oxalate in glow sticks: peroxide splits it, and the energy lights up a dye.", lib=5197)
S("373-68-2", "TMAF", "Tetramethylammonium fluoride", "C4H12FN", "Solid", 58033746,
  "Fluoride with no metal, soluble in organic solvents: 'naked' fluoride for fluorinating molecules.", lib=5587)
S("7681-55-2", "NaIO3", "Sodium iodate", "NaIO3", "Solid", 5064081,
  "Chile saltpetre carries it; one of the forms in which iodine is added to salt.", lib=8037)
S("7782-78-7", "NOHSO4", "Nitrosylsulfuric acid", "HNO5S", "Solid", 2463012,
  "The nitrosating agent of the lead-chamber process, now used to diazotise weakly basic amines for dyes.",
  lib=8131)
S("520-45-6", "DehydroaceticAcid", "Dehydroacetic acid", "C8H8O4", "Solid", 14263615,
  "A preservative for cheese and cosmetics, made from two diketenes.", lib=6212)
S("87061-04-9", "MPDiol", "Menthoxypropanediol", "C13H26O3", "Solid", 17940309,
  "A cooling agent: cold like menthol, without its minty smell.", lib=8534)
S("26172-55-4", "MCI", "Methylchloroisothiazolinone", "C4H4ClNOS", "Solid", 49284,
  "With methylisothiazolinone it makes Kathon, a preservative for shampoos and paints, and an allergen.",
  lib=4848)
S("1576-35-8", "Tosylhydrazine", "Tosylhydrazine", "C7H10N2O2S", "Solid", "P-Toluenesulfonyl_hydrazide",
  "A blowing agent for foams, and the reagent of the Shapiro reaction.", lib=3950)
S("67-51-6", "DMPz", "3,5-Dimethylpyrazole", "C5H8N2", "Solid", 62216036,
  "Blocks isocyanates in one-pack coatings until baking frees them.", lib=7273)
S("105-13-5", "AnisylAlcohol", "Anisyl alcohol", "C8H10O2", "Liquid", 43037548,
  "A soft floral, powdery note for perfumes; also found in vanilla.", lib=2323)
S("540-18-1", "AmylButyrate", "Amyl butyrate", "C9H18O2", "Liquid", 1106871,
  "An ester that smells of apricots and pears.", lib=6371)
S("107-35-7", "Taurine", "Taurine", "C2H7NO3S", "Solid", 61162,
  "An amino sulfonic acid first found in ox bile (1827); added to cat food and energy drinks.", lib=2451)
S("151-67-7", "Halothane", "Halothane", "C2HBrClF3", "Liquid", 142523,
  "Charles Suckling's anaesthetic (ICI, 1951), not flammable unlike the ether it replaced.", lib=3842)
S("28523-86-6", "Sevoflurane", "Sevoflurane", "C4H3F7O", "Liquid", 327896,
  "A sweet-smelling anaesthetic gentle enough to put children to sleep by mask.", lib=5047)
S("2078-54-8", "Propofol", "Propofol", "C12H18O", "Liquid", 496540,
  "The milky intravenous anaesthetic: 2,6-diisopropylphenol in a soybean-oil emulsion.", lib=4412)
S("137-58-6", "Lidocaine", "Lidocaine", "C14H22N2O", "Solid", 298762,
  "Nils Lofgren's local anaesthetic (1943), the dentist's injection and a heart drug.", lib=3516)
S("103-12-8", "Prontosil", "Prontosil", "C12H13N5O2S", "Solid", 2153700,
  "A red dye that cured streptococcal infections in mice (Domagk, 1932): the first sulfa drug.", lib=2219)
S("22839-47-0", "Aspartame", "Aspartame", "C14H18N2O5", "Solid", 2752,
  "Two amino acids and a methanol, 200 times as sweet as sugar; found by licking a finger in 1965.", lib=4549)
S("121-75-5", "Malathion", "Malathion", "C10H19O6PS2", "Liquid", 745387,
  "An organophosphate insecticide that insects activate into a poison and mammals break down.", lib=2991)
S("10045-89-3", "MohrSalt", "Mohr's salt", "Fe(NH4)2(SO4)2·6H2O", "Solid", 9436847,
  "Ferrous ammonium sulfate: iron(II) that keeps in air, the analyst's standard.", lib=2074)
S("12298-68-9", "KI3", "Potassium triiodide", "KI3", "Solid", 1541301,
  "Iodine dissolved by iodide, the brown of Lugol's solution and the starch test.", lib=3057)
S("124-43-6", "CarbamidePeroxide", "Carbamide peroxide", "CH6N2O3", "Solid", 709796,
  "Urea holding hydrogen peroxide in a crystal: the active part of tooth-whitening gels.", lib=3111)
S("110-83-8", "Cyclohexene", "Cyclohexene", "C6H10", "Liquid", 908356,
  "Cyclohexanol with its water taken out: a classic first distillation in student labs.", lib=2607)
S("136-77-6", "Hexylresorcinol", "Hexylresorcinol", "C12H18O2", "Solid", 5636574,
  "An antiseptic in throat lozenges, and a shrimp preservative that stops black spots.", lib=3487)
S("134-03-2", "NaAscorbate", "Sodium ascorbate", "C6H7NaO6", "Solid", 4251626,
  "Vitamin C as its sodium salt (E301), an antioxidant that keeps cured meat pink.", lib=3412)
S("624-49-7", "DimethylFumarate", "Dimethyl fumarate", "C6H8O4", "Solid", 17102293,
  "A drug for multiple sclerosis; once a mould inhibitor in sachets, until it burned the skin of sofa owners.",
  lib=6973)
S("6410-10-2", "ParaRed", "Para red", "C16H11N3O3", "Solid", 1775578,
  "One of the first azo pigments (1880): diazotised 4-nitroaniline coupled on 2-naphthol.", lib=7099)
S("5281-04-9", "PR57", "Lithol Rubine BK", "C18H12CaN2O6S", "Solid", 3251788,
  "Pigment Red 57:1, the magenta of four-colour printing.", lib=6265)
S("50-35-1", "Thalidomide", "Thalidomide", "C13H10N2O4", "Solid", 51078,
  "Sold as a sleeping pill (1957); its mirror image caused birth defects in thousands of children, and drug "
  "testing changed for good. Now a cancer drug.", lib=6046)
S("57-57-8", "BPL", "beta-Propiolactone", "C3H4O2", "Liquid", 5141147,
  "A four-membered lactone that sterilises vaccines and grafts; also a carcinogen.", lib=6600)
S("7693-26-7", "KH", "Potassium hydride", "KH", "Solid", 3922869,
  "A salt of hydride, H-: a fierce base that bursts into flame in moist air.", lib=8043)

# --- the three true reactions among the library's scraped ones, written properly ------------
S("1111-78-0", "AmmoniumCarbamate", "Ammonium carbamate", "CH6N2O2", "Solid", "Ammonium_carbamate",
  "The salt ammonia and carbon dioxide make together: every urea plant passes through it on the way to fertiliser.",
  lib=101435, smiles="NC(=O)[O-].[NH4+]")
S("585-88-6", "Maltitol", "Maltitol", "C12H24O11", "Solid", "Maltitol",
  "A sugar alcohol with most of the sweetness of table sugar: the sweetener of sugar-free chocolate, and a laxative if you overdo it.",
  lib=108942, smiles="OCC(O)C(O)C(OC1OC(CO)C(O)C(O)C1O)C(O)CO")
S("132-64-9", "Dibenzofuran", "Dibenzofuran", "C12H8O", "Solid", "Dibenzofuran",
  "Two benzene rings bridged by a furan, about one percent of coal tar. Stable and liquid over a wide range, it carries heat in industrial heating loops.",
  lib=127145, smiles="c1ccc2c(c1)oc1ccccc12")


# --- the reactions -------------------------------------------------------------------------
E3.reactions += [
    R("Mohr's Salt", "FeSO4 + NH42SO4 + 6 H2O -> MohrSalt", MIX,
      "Ferrous and ammonium sulfates crystallised together as a double salt that resists the air.",
      wiki=9436847),
    R("Lugol's Iodine", "KI + I2 -> KI3", MIX,
      "Iodine, barely soluble in water, dissolves in potassium iodide as triiodide.", wiki=1541301),
    R("Sodium Iodate", "I2 + 2 NaClO3 -> 2 NaIO3 + Cl2", FLASK,
      "Iodine displaces chlorine from sodium chlorate.", wiki=5064081, T=80),
    R("Nitrosylsulfuric Acid", "SO2 + HNO3 -> NOHSO4", COOL,
      "Sulfur dioxide passed into cold fuming nitric acid.", wiki=2463012, T=10),
]
E5.reactions += [
    R("Ammonium Carbamate", "2 NH3 + CO2 -> AmmoniumCarbamate", COOL,
      "Liquid ammonia poured over dry ice: the two combine at once into a white salt.",
      wiki="Ammonium_carbamate", T=-40),
    R("Carbamate to Urea", "AmmoniumCarbamate -> Urea + H2O", HEAT,
      "Heated, the carbamate gives up a water and becomes urea: the second half of every urea plant.",
      wiki="Urea#Industrial_production", T=190),
    R("Hydrogenating Maltose", "Maltose + H2 -> Maltitol", CAT,
      "Maltose from starch hydrogenated over nickel, as glucose is to sorbitol.",
      wiki="Maltitol", cat="Ni", T=120, P=50),
]
E4.reactions += [
    R("2-Naphthol", "Naphthalene + H2SO4 + 2 NaOH -> Naphthol2 + Na2SO3 + 2 H2O", HEAT,
      "Naphthalene sulfonated hot (at the beta position), then fused with caustic soda.", wiki="2-Naphthol",
      T=300),
    R("Para Red", "Nitroaniline + NaNO2 + HCl + Naphthol2 -> ParaRed + NaCl + 2 H2O", COOL,
      "4-Nitroaniline diazotised in ice and coupled onto 2-naphthol.", wiki=1775578, T=5),
    R("BON Acid", "Naphthol2 + CO2 -> BONAcid", PRESS,
      "A Kolbe-Schmitt carboxylation: sodium 2-naphthoxide and carbon dioxide under pressure.",
      wiki="3-Hydroxy-2-naphthoic_acid", T=250),
    R("Domagk's Prontosil", "Sulfanilamide + NaNO2 + HCl + MPD -> Prontosil + NaCl + 2 H2O", COOL,
      "Sulfanilamide diazotised and coupled onto m-phenylenediamine (Bayer, 1932).", wiki=2153700, T=5),
    R("Cyclohexene", "Cyclohexanol + H3PO4 -> Cyclohexene + H2O + H3PO4", DISTIL,
      "Cyclohexanol heated with phosphoric acid; cyclohexene distils off as it forms.", wiki=908356,
      T=90),
    R("Carbamide Peroxide", "Urea + H2O2 -> CarbamidePeroxide", MIX,
      "Urea crystallised from hydrogen peroxide.", wiki=709796),
    R("Taurine", "EO + NaHSO3 + NH3 + HCl -> Taurine + NaCl + H2O", PRESS,
      "Ethylene oxide and sodium bisulfite give isethionate, which ammonia turns into taurine under "
      "pressure.", wiki=61162, T=250),
    R("Oxalyl Chloride", "Oxalic + 2 PCl5 -> OxalylCl + 2 POCl3 + 2 HCl", FLASK,
      "Phosphorus pentachloride swaps both OH groups of oxalic acid for chlorine.", wiki="Oxalyl_chloride",
      T=60),
    R("Tosyl Chloride", "Toluene + SO2Cl2 -> TsCl + HCl", FLASK,
      "Toluene chlorosulfonated.", wiki="4-Toluenesulfonyl_chloride", T=25),
    R("Amyl Butyrate", "Pentanol + Butyric -> AmylButyrate + H2O", CAT,
      "1-Pentanol esterified with butyric acid.", wiki=1106871, cat="H2SO4", T=110),
]
E5.reactions += [
    R("Lithol Rubine", "pToluidine + H2SO4 + NaNO2 + BONAcid + CaCl2 -> PR57 + NaCl + 3 H2O + HCl", COOL,
      "p-Toluidine sulfonated (4B acid), diazotised, coupled onto BON acid and laked with calcium.",
      wiki=3251788, T=5),
    R("Halothane", "TCE + 3 HF + Br2 -> Halothane + 2 HCl + HBr", HEAT,
      "Trichloroethylene fluorinated to 2-chloro-1,1,1-trifluoroethane, then brominated at 450 C (Suckling, "
      "1951).", wiki=142523, T=450),
    R("Sevoflurane", "HFIP + CH2O + HF -> Sevoflurane + H2O", FLASK,
      "Hexafluoroisopropanol, formaldehyde and hydrogen fluoride in one pot.", wiki=327896, T=65),
    R("Propofol", "Phenol + 2 Propylene -> Propofol", HIGHP,
      "Phenol alkylated twice beside its OH, steered by an aluminium phenoxide catalyst.", wiki=496540,
      cat="Al", T=280),
    R("2,6-Xylidine", "DMP26 + NH3 -> Xylidine26 + H2O", CAT,
      "2,6-Xylenol and ammonia over an oxide catalyst.", wiki="2,6-Xylidine", cat="Alumina", T=350),
    R("Lofgren's Lidocaine", "Xylidine26 + ClAcCl + Diethylamine -> Lidocaine + 2 HCl", FLASK,
      "2,6-Xylidine acylated with chloroacetyl chloride; diethylamine then displaces the chlorine.",
      wiki=298762, T=80),
    R("Aspartame", "AsparticAcid + Phenylalanine + Methanol -> Aspartame + 2 H2O", FLASK,
      "Aspartic acid (protected, as its anhydride) coupled to phenylalanine methyl ester.", wiki=2752,
      T=40),
    R("Malathion", "P4S10 + 8 Methanol + 4 DEM -> 4 Malathion + 2 H2S", FLASK,
      "Phosphorus pentasulfide and methanol give dimethyl dithiophosphoric acid, which adds to diethyl "
      "maleate.", wiki=745387, T=70),
    R("Hexylresorcinol", "Resorcinol + Hexanoic + 2 H2 -> Hexylresorcinol + 2 H2O", HIGHP,
      "Resorcinol acylated with hexanoic acid, then the ketone reduced to a hexyl chain.",
      wiki=5636574, cat="Ni", T=150),
    R("Sodium Ascorbate", "VitaminC + NaHCO3 -> NaAscorbate + CO2 + H2O", MIX,
      "Vitamin C neutralised with baking soda.", wiki=4251626),
    R("Dimethyl Fumarate", "MaleicAnhydride + 2 Methanol -> DimethylFumarate + H2O", FLASK,
      "Maleic anhydride esterified, and the cis ester isomerised to the trans.", wiki=17102293,
      T=65),
    R("CPPO", "2 Salicylic + 6 Cl2 + 2 Pentanol + OxalylCl -> CPPO + 8 HCl + 2 H2O", FLASK,
      "Salicylic acid trichlorinated and esterified with pentanol; two of these phenols on oxalyl chloride.",
      wiki=5518657, T=40),
    R("Tetramethylammonium Fluoride", "TMACl + KF -> TMAF + KCl", MIX,
      "Chloride swapped for fluoride; potassium chloride drops out of methanol.", wiki=58033746),
    R("Dehydroacetic Acid", "2 Diketene -> DehydroaceticAcid", FLASK,
      "Diketene dimerised with a base.", wiki=14263615, T=60),
    R("Menthoxypropanediol", "Menthol + Epichlorohydrin + NaOH -> MPDiol + NaCl", FLASK,
      "Menthol takes a glycidyl group from epichlorohydrin, whose epoxide is opened to the diol.",
      wiki=17940309, T=80),
    R("Methylchloroisothiazolinone", "MIT + Cl2 -> MCI + HCl", FLASK,
      "More chlorine puts a chlorine on the ring of methylisothiazolinone.", wiki=49284, T=10),
    R("Tosylhydrazine", "TsCl + N2H4 + NaOH -> Tosylhydrazine + NaCl + H2O", FLASK,
      "Tosyl chloride on hydrazine.", wiki="P-Toluenesulfonyl_hydrazide", T=10),
    R("3,5-Dimethylpyrazole", "AcAc + N2H4 -> DMPz + 2 H2O", FLASK,
      "Acetylacetone condensed with hydrazine.", wiki=62216036, T=30),
    R("Thalidomide", "PhthalicAnhydride + Glutamine -> Thalidomide + 2 H2O", HEAT,
      "Phthalic anhydride fused with glutamine, and the amide closed into the second ring.",
      wiki=51078, T=150),
    R("beta-Propiolactone", "Ketene + CH2O -> BPL", COOL,
      "Ketene and formaldehyde join over a Lewis acid in the cold.", wiki=5141147, T=10),
    R("Potassium Hydride", "2 K + H2 -> 2 KH", HEAT,
      "Potassium metal heated in hydrogen.", wiki=3922869, T=350),
    R("Anisyl Alcohol", "Anisaldehyde + H2 -> AnisylAlcohol", CAT,
      "Anisaldehyde hydrogenated.", wiki=43037548, cat="Ni", T=100),
]

import authored_canon_19  # noqa: E402,F401
