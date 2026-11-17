"""
Curieosity's industrial chemistry, part 13 (see authored_canon.py).
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E1, E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)


# --- the canon substances ------------------------------------------------------------------
S("791-28-6", "TPPO", "Triphenylphosphine oxide", "C18H15OP", "Solid", 6857672,
  "The by-product of every Wittig reaction, famously hard to get rid of.", lib=8251)
S("80-70-6", "TMG", "Tetramethylguanidine", "C5H13N3", "Liquid", 19832498,
  "A strong, non-nucleophilic organic base.", lib=8284)
S("81-64-1", "Quinizarin", "Quinizarin", "C14H8O4", "Solid", 26001706,
  "1,4-Dihydroxyanthraquinone, the orange-red base of many anthraquinone dyes.", lib=8327)
S("83-40-9", "CresoticAcid", "3-Methylsalicylic acid", "C8H8O3", "Solid", 58556540,
  "o-Cresotic acid, carboxylated o-cresol, for dyes and drugs.", lib=8390)
S("860-22-0", "IndigoCarmine", "Indigo carmine", "C16H8N2Na2O8S2", "Solid", 5854119,
  "Indigo sulfonated to dissolve in water: the food colour E132, and a dye that shows surgeons the urinary tract.", smiles="[Na+].[Na+].O=C1C(=C2Nc3ccc(cc3C2=O)S([O-])(=O)=O)Nc2ccc(cc12)S([O-])(=O)=O")
S("865-34-9", "LiOMe", "Lithium methoxide", "CH3LiO", "Solid", 31598391,
  "A strong base and transesterification catalyst.", lib=8503)
S("865-48-5", "NaOtBu", "Sodium tert-butoxide", "C4H9NaO", "Solid", 32043063,
  "The base of palladium-catalysed amine couplings (Buchwald-Hartwig).", lib=8505)
S("88-68-6", "Anthranilamide", "Anthranilamide", "C7H8N2O", "Solid", 80898589,
  "A building block for quinazolinone drugs and pesticides.", lib=8575)
S("91-16-7", "Veratrole", "Veratrole", "C8H10O2", "Liquid", 4299865,
  "Catechol's dimethyl ether, a building block for drugs such as papaverine.", lib=8668)
S("91-63-4", "Quinaldine", "Quinaldine", "C10H9N", "Liquid", 12275721,
  "2-Methylquinoline, the start of quinoline yellow and of antimalarials; also an anaesthetic for fish.", lib=8674)
S("91-66-7", "DiethylAniline", "N,N-Diethylaniline", "C10H15N", "Liquid", 38105393,
  "A dye intermediate and a curing promoter for polyester resin.", lib=8677)
S("917-61-3", "NaOCN", "Sodium cyanate", "NaOCN", "Solid", 42793721,
  "Used to harden steel by nitriding and to make herbicides; Wohler's urea came from cyanate.", lib=8698)
S("111-78-4", "COD", "1,5-Cyclooctadiene", "C8H12", "Liquid", 4167607,
  "Two butadienes joined in a ring on nickel: a ligand for organometallic catalysts and the start of cyclooctene.", lib=2656)
S("931-87-3", "Cyclooctene", "cis-Cyclooctene", "C8H14", "Liquid", 15266079,
  "Opened by metathesis into polyoctenamer (Vestenamer), a rubber processing aid.", lib=8757)
S("94-13-3", "Propylparaben", "Propylparaben", "C10H12O3", "Solid", 2994849,
  "A preservative in cosmetics and medicines.", lib=8783)
S("95-50-1", "oDCB", "1,2-Dichlorobenzene", "C6H4Cl2", "Liquid", 5717096,
  "A high-boiling solvent for fullerenes and polymers, and a degreaser.", lib=8820)
S("96-24-2", "MCPD", "3-Chloro-1,2-propanediol", "C3H7ClO2", "Liquid", 19808050,
  "3-MCPD, an intermediate for drugs, and a contaminant that forms when soy sauce and refined oils are made with acid.", lib=8856)
S("96-26-4", "DHA", "Dihydroxyacetone", "C3H6O3", "Solid", 558545,
  "The browning agent of sunless tanning lotion: it reacts with skin proteins like a Maillard reaction.", lib=8857)
S("96-31-1", "DimethylUrea", "N,N'-Dimethylurea", "C3H8N2O", "Solid", 21294294,
  "The start of caffeine and theophylline synthesis.", smiles="O=C(NC)NC")
S("98-79-3", "PyroglutamicAcid", "Pyroglutamic acid", "C5H7NO3", "Solid", 953465,
  "Glutamic acid closed into a lactam; a moisturiser in skin creams.", lib=8928)
S("99-20-7", "Trehalose", "Trehalose", "C12H22O11", "Solid", 1001846,
  "The sugar that lets tardigrades and resurrection plants survive drying out; made cheaply from starch since 1994.", lib=8949)
S("99-76-3", "Methylparaben", "Methylparaben", "C8H8O3", "Solid", 2939751,
  "The most common preservative in cosmetics, also found in blueberries.", lib=8958)
S("993-07-7", "Me3SiH", "Trimethylsilane", "C3H10Si", "Gas", 36213977,
  "A gas for depositing low-k dielectric films in chips.", lib=8972)
S("998-40-3", "PBu3", "Tributylphosphine", "C12H27P", "Liquid", 14087194,
  "A ligand and catalyst, with an overpowering smell.", lib=8985)
S("2402-78-0", "DCPyridine", "2,6-Dichloropyridine", "C5H3Cl2N", "Liquid", 77251884,
  "An intermediate for the antibiotic enoxacin and for pesticides.", lib=4618)
S("84-69-5", "DIBP", "Diisobutyl phthalate", "C16H22O4", "Liquid", 4953420,
  "A plasticiser for nitrocellulose and PVC, restricted in Europe.", lib=8431)
S("140-89-6", "KEX", "Potassium ethyl xanthate", "C3H5KOS2", "Solid", 31368712,
  "A flotation collector that makes copper and zinc sulfide grains cling to bubbles (1920s).", lib=3599)
S("998-30-1", "TEOS_H", "Triethoxysilane", "C6H16O3Si", "Liquid", 37281723,
  "A silane with an Si-H bond for silane coupling agents.", lib=8984)
S("78-86-4", "sBuCl", "2-Chlorobutane", "C4H9Cl", "Liquid", 36193547,
  "An alkylating agent and the start of sec-butyllithium.", lib=8196)
S("3724-43-4", "Vilsmeier", "Vilsmeier reagent", "C3H7Cl2N", "Solid", 58895181,
  "The chloroiminium salt that puts formyl groups onto aromatic rings.", lib=5580)
S("105-53-3", "DEMalonate", "Diethyl malonate", "C7H12O4", "Liquid", 570580,
  "The malonic ester of the textbook synthesis, and the start of barbiturates and vitamins.", lib=2330)
S("112-54-9", "Dodecanal", "Dodecanal", "C12H24O", "Liquid", 36213191,
  "Lauric aldehyde, with a waxy, violet note in perfumes.", lib=2718)
S("123-68-2", "AllylCaproate", "Allyl hexanoate", "C9H16O2", "Liquid", 25398621,
  "The pineapple flavour of sweets and drinks.", lib=3081)
S("1302-81-4", "Al2S3", "Aluminium sulfide", "Al2S3", "Solid", 5022827,
  "A grey solid that reeks of rotten eggs in damp air as it hydrolyses to hydrogen sulfide.", lib=3262)
S("13530-50-2", "AlH2PO43", "Aluminium dihydrogen phosphate", "Al(H2PO4)3", "Solid", 57302917,
  "A binder for refractories and heat-resistant coatings.", lib=3462)
S("1740-19-8", "DehydroabieticAcid", "Dehydroabietic acid", "C20H28O2", "Solid", 80050237,
  "Disproportionated rosin's main acid, used in emulsifiers for synthetic rubber.", lib=4126)
S("26658-19-5", "Span65", "Sorbitan tristearate", "C60H114O8", "Solid", 12249227,
  "Span 65, which keeps chocolate from blooming.", lib=4902)
S("299-27-4", "KGluconate", "Potassium gluconate", "C6H11KO7", "Solid", 13519380,
  "A gentle potassium supplement.", lib=5139)
S("3031-66-1", "HexynDiol", "3-Hexyne-2,5-diol", "C6H10O2", "Liquid", 66917811,
  "A brightener in nickel electroplating.", lib=5185)
S("6284-40-8", "Meglumine", "Meglumine", "C7H17NO5", "Solid", 17079214,
  "A sugar amine that dissolves drugs and X-ray contrast agents as salts.", lib=6998)
S("706-14-9", "GammaDecalactone", "gamma-Decalactone", "C10H18O2", "Liquid", 51522936,
  "The scent of peaches, made by yeast from castor oil's ricinoleic acid: one of the first natural flavours made by biotech.",
  smiles="O=C1OC(CC1)CCCCCC")
S("84-51-5", "EAQ", "2-Ethylanthraquinone", "C16H12O2", "Solid", 17038904,
  "The working molecule of the anthraquinone process that makes nearly all hydrogen peroxide.", lib=8426)
S("89-98-5", "ClBenzaldehyde2", "2-Chlorobenzaldehyde", "C7H5ClO", "Liquid", 59001004,
  "The aldehyde behind CS gas and several drugs.", lib=8605)
S("96-45-7", "ETU", "Ethylenethiourea", "C3H6N2S", "Solid", 33965170,
  "The accelerator for curing neoprene rubber.", lib=8864)
S("2720-73-2", "KAX", "Potassium amyl xanthate", "C6H11KOS2", "Solid", 57001960,
  "A strong flotation collector for copper and gold sulfide ores.", lib=4955)
S("7575-23-7", "PETMP", "Pentaerythritol tetrakis(3-mercaptopropionate)", "C17H28O8S4", "Liquid", 75658705,
  "A four-armed thiol for thiol-ene UV coatings and high-index eyeglass lenses.", lib=7954)
S("103-71-9", "PhNCO", "Phenyl isocyanate", "C7H5NO", "Liquid", 30587067,
  "The simplest aromatic isocyanate, for ureas and urethanes in pesticides and drugs.", lib=2235)
S("5422-34-4", "LactamideMEA", "Lactamide MEA", "C5H11NO3", "Liquid", 36127668,
  "A humectant and foam booster in shampoos.", lib=6402)
S("917-70-4", "LaOAc3", "Lanthanum acetate", "La(C2H3O2)3", "Solid", 73337621,
  "A lanthanum salt for catalysts and ceramics.", lib=8699)
S("75-63-8", "Halon1301", "Bromotrifluoromethane", "CBrF3", "Gas", 294523,
  "Halon 1301, the fire suppressant of aircraft engine bays and computer rooms, phased out for the ozone layer.", lib=7910)

E4.reactions += [
    R("Indigo Carmine", "Indigo + 2 H2SO4 + 2 NaOH -> IndigoCarmine + 4 H2O", MIX,
      "Indigo sulfonated in fuming sulfuric acid, then neutralised (Barth, 1740).", wiki=5854119),
    R("Sodium Cyanate", "2 Urea + SodaAsh -> 2 NaOCN + 2 NH3 + CO2 + H2O", HEAT,
      "Urea fused with soda ash.", wiki=42793721, T=600),
    R("Quinaldine", "Aniline + 2 Acetaldehyde -> Quinaldine + 2 H2O + H2", FLASK,
      "The Doebner-Miller reaction of aniline with acetaldehyde in acid.", wiki=12275721, T=100),
    R("o-Dichlorobenzene", "Chlorobenzene + Cl2 -> oDCB + HCl", FLASK,
      "Chlorobenzene chlorinated again; the ortho isomer is distilled from the para.", wiki=5717096, T=60),
    R("3-MCPD", "Glycerol + HCl -> MCPD + H2O", FLASK,
      "Glycerol chlorinated once by hydrochloric acid.", wiki=19808050, T=100),
    R("Aluminium Sulfide", "2 Al + 3 S -> Al2S3", HEAT,
      "Aluminium and sulfur ignited together.", wiki=5022827, T=1000),
    R("Aluminium Phosphate Binder", "AlOH3 + 3 H3PO4 -> AlH2PO43 + 3 H2O", MIX,
      "Aluminium hydroxide dissolved in phosphoric acid.", wiki=57302917),
    R("Potassium Gluconate", "GluconicAcid + KOH -> KGluconate + H2O", MIX,
      "Gluconic acid neutralised.", wiki=13519380),
    R("Methylparaben", "PHBA + Methanol -> Methylparaben + H2O", CAT,
      "4-Hydroxybenzoic acid esterified with methanol.", wiki=2939751, cat="H2SO4", T=80),
    R("Propylparaben", "PHBA + Propanol -> Propylparaben + H2O", CAT,
      "4-Hydroxybenzoic acid esterified with propanol.", wiki=2994849, cat="H2SO4", T=100),
    R("Phenyl Isocyanate", "Aniline + COCl2 -> PhNCO + 2 HCl", FLASK,
      "Aniline phosgenated.", wiki=30587067, T=120),
    R("Lanthanum Acetate", "La2CO33 + 6 AcOH -> 2 LaOAc3 + 3 CO2 + 3 H2O", MIX,
      "Lanthanum carbonate dissolved in acetic acid.", wiki=73337621),
    R("Pyroglutamic Acid", "GlutamicAcid -> PyroglutamicAcid + H2O", HEAT,
      "Glutamic acid heated until it closes into a lactam (1882).", wiki=953465, T=180),
]
E5.reactions += [
    R("Triphenylphosphine Oxide", "PPh3 + H2O2 -> TPPO + H2O", MIX,
      "Triphenylphosphine oxidised.", wiki=6857672),
    R("Tetramethylguanidine", "2 Me2NH + HCN + Cl2 -> TMG + 2 HCl", FLASK,
      "Dimethylamine and cyanogen chloride.", wiki=19832498, T=60),
    R("Quinizarin", "PhthalicAnhydride + Hydroquinone -> Quinizarin + H2O", CAT,
      "Phthalic anhydride condensed with hydroquinone in sulfuric acid and boric acid.", wiki=26001706,
      cat="H2SO4", T=200),
    R("o-Cresotic Acid", "oCresol + CO2 -> CresoticAcid", PRESS,
      "o-Cresol carboxylated (Kolbe-Schmitt).", wiki=58556540, T=150),
    R("Lithium Methoxide", "2 Li + 2 Methanol -> 2 LiOMe + H2", FLASK,
      "Lithium dissolved in methanol.", wiki=31598391, T=40),
    R("Sodium tert-Butoxide", "2 Na + 2 tBuOH -> 2 NaOtBu + H2", FLASK,
      "Sodium dissolved in hot tert-butanol.", wiki=32043063, T=90),
    R("Anthranilamide", "IsatoicAnhydride + NH3 -> Anthranilamide + CO2", MIX,
      "Ammonia opens isatoic anhydride, releasing carbon dioxide.", wiki=80898589),
    R("Veratrole", "Catechol + 2 DMC -> Veratrole + 2 CO2 + 2 Methanol", CAT,
      "Catechol methylated twice by dimethyl carbonate.", wiki=4299865, cat="KOH", T=160),
    R("N,N-Diethylaniline", "Aniline + 2 Ethanol -> DiethylAniline + 2 H2O", CAT,
      "Aniline ethylated twice in the presence of acid.", wiki=38105393, cat="H3PO4", T=250),
    R("Cyclooctadiene", "2 Butadiene -> COD", HIGHP,
      "Butadiene dimerised on a nickel catalyst.", wiki=4167607, cat="Ni", T=100),
    R("Cyclooctene", "COD + H2 -> Cyclooctene", CAT,
      "Cyclooctadiene half-hydrogenated over palladium.", wiki=15266079, cat="Pd", T=60),
    R("Dihydroxyacetone", "2 Glycerol + O2 -> 2 DHA + 2 H2O", FERM,
      "Gluconobacter bacteria oxidise glycerol's middle carbon.", wiki=558545, T=30),
    R("Dimethylurea", "Urea + 2 Methylamine -> DimethylUrea + 2 NH3", HEAT,
      "Urea heated with methylamine.", wiki=21294294, T=150),
    R("Trimethylsilane", "4 Me3SiCl + LiAlH4 -> 4 Me3SiH + LiCl + AlCl3", FLASK,
      "Chlorotrimethylsilane reduced by lithium aluminium hydride.", wiki=36213977, T=20),
    R("Tributylphosphine", "Phosphine + 3 1-Butene -> PBu3", LIGHT,
      "Phosphine adds to 1-butene three times by a radical chain.", wiki=14087194, T=60),
    R("2,6-Dichloropyridine", "ClPyridine + Cl2 -> DCPyridine + HCl", LIGHT,
      "2-Chloropyridine chlorinated again in light.", wiki=77251884, T=100),
    R("Diisobutyl Phthalate", "PhthalicAnhydride + 2 Isobutanol -> DIBP + H2O", CAT,
      "Phthalic anhydride esterified with isobutanol.", wiki=4953420, cat="H2SO4", T=150),
    R("Ethyl Xanthate", "Ethanol + CS2 + KOH -> KEX + H2O", MIX,
      "Ethanol, carbon disulfide and caustic potash.", wiki=31368712),
    R("Amyl Xanthate", "Pentanol + CS2 + KOH -> KAX + H2O", MIX,
      "Pentanol, carbon disulfide and caustic potash.", wiki=57001960),
    R("Triethoxysilane", "Si + 3 Ethanol -> TEOS_H + H2", CAT,
      "Silicon and ethanol over copper.", wiki=37281723, cat="Cu", T=250),
    R("2-Chlorobutane", "2-Butene + HCl -> sBuCl", MIX,
      "Hydrogen chloride added to 2-butene.", wiki=36193547),
    R("Vilsmeier Reagent", "DMF + COCl2 -> Vilsmeier + CO2", FLASK,
      "Dimethylformamide and phosgene.", wiki=58895181, T=20),
    R("Diethyl Malonate", "ClAcOH + CO + 2 Ethanol -> DEMalonate + HCl + H2O", CAT,
      "Chloroacetate carbonylated in ethanol with cobalt.", wiki=570580, cat="Co", T=60),
    R("Dodecanal", "Dodecanol -> Dodecanal + H2", CAT,
      "Lauryl alcohol dehydrogenated over copper.", wiki=36213191, cat="Cu", T=300),
    R("Allyl Hexanoate", "Hexanoic + AllylAlcohol -> AllylCaproate + H2O", CAT,
      "Hexanoic acid esterified with allyl alcohol.", wiki=25398621, cat="H2SO4", T=100),
    R("Disproportionated Rosin", "Rosin -> DehydroabieticAcid + H2", CAT,
      "Rosin heated over palladium: some rings lose hydrogen, others gain it.", wiki=80050237,
      cat="Pd", T=250),
    R("Span 65", "Sorbitol + 3 StearicAcid -> Span65 + 4 H2O", HEAT,
      "Sorbitan esterified with three stearic acids.", wiki=12249227, T=230),
    R("Hexynediol", "Acetylene + 2 Acetaldehyde -> HexynDiol", PRESS,
      "Acetylene takes an acetaldehyde at each end (Reppe).", wiki=66917811, T=100),
    R("Meglumine", "Glucose + Methylamine + H2 -> Meglumine + H2O", CAT,
      "Glucose reductively aminated with methylamine over nickel.", wiki=17079214, cat="Ni", T=60),
    R("Ethylanthraquinone", "PhthalicAnhydride + Ethylbenzene -> EAQ + H2O", CAT,
      "Phthalic anhydride and ethylbenzene (Friedel-Crafts), the acid then cyclised.", wiki=17038904, cat="AlCl3", T=100),
    R("2-Chlorobenzaldehyde", "oChlorotoluene + 2 Cl2 + H2O -> ClBenzaldehyde2 + 4 HCl", LIGHT,
      "o-Chlorotoluene chlorinated twice on its methyl group, then hydrolysed.", wiki=59001004, T=150),
    R("Ethylenethiourea", "EDA + CS2 -> ETU + H2S", HEAT,
      "Ethylenediamine and carbon disulfide.", wiki=33965170, T=100),
    R("PETMP", "Pentaerythritol + 4 MPA3 -> PETMP + 4 H2O", CAT,
      "Pentaerythritol esterified with mercaptopropionic acid.", wiki=75658705, cat="pTsOH", T=120),
    R("Lactamide MEA", "LacticAcid + MEA -> LactamideMEA + H2O", HEAT,
      "Lactic acid heated with ethanolamine.", wiki=36127668, T=150),
    R("Halon 1301", "HFC23 + Br2 -> Halon1301 + HBr", HEAT,
      "Fluoroform brominated at high temperature.", wiki=294523, T=500),
]
E6.reactions += [
    R("Trehalose", "Maltose -> Trehalose", FERM,
      "An enzyme rearranges maltose's link between its two glucoses (Hayashibara, 1994).", wiki=1001846, T=50),
    R("Peach Lactone", "RicinoleicAcid -> GammaDecalactone", FERM,
      "The yeast Yarrowia lipolytica trims castor oil's acid into the peach lactone.", wiki=51522936,
      T=28, exact=False),
]

import authored_canon_14  # noqa: E402,F401
