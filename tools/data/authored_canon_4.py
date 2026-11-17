"""
Curieosity's industrial chemistry, part 4 (see authored_canon.py).
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E1, E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)


# --- intermediates the canon set lacks ---------------------------------------------------
S(None, "Phosphine", "Phosphine", "PH3", "Gas", "Phosphine",
  "PH3, a very toxic gas smelling of garlic or rotten fish: a grain fumigant, and the source of phosphorus in silicon chips.",
  smiles="P")
S(None, "NCB", "4-Nitrochlorobenzene", "C6H4ClNO2", "Solid", "4-Nitrochlorobenzene",
  "Chlorobenzene nitrated at the para position: the start of paracetamol, of antioxidants and of dyes.",
  smiles="O=[N+]([O-])c1ccc(Cl)cc1")

# --- the canon substances ------------------------------------------------------------------
S("626-17-5", "IPN", "Isophthalonitrile", "C8H4N2", "Solid", 63544943,
  "m-Xylene's two methyl groups turned into nitriles by ammoxidation, on the way to MXDA and the fungicide chlorothalonil.",
  lib=6985)
S("1477-55-0", "MXDA", "m-Xylylenediamine", "C8H12N2", "Liquid", 50748263,
  "A diamine for epoxy hardeners and for MXD6 nylon, the oxygen barrier layer in beer bottles.",
  lib=3777)
S("27247-96-7", "EHN", "2-Ethylhexyl nitrate", "C8H17NO3", "Liquid", 44254216,
  "The cetane improver of diesel fuel: it falls apart in the cylinder and helps the fuel light sooner.",
  lib=4960)
S("27546-07-2", "ADM", "Ammonium dimolybdate", "(NH4)2Mo2O7", "Solid", 46721957,
  "The form molybdenum is sold in for making catalysts, pigments and molybdenum metal.",
  lib=4990)
S("2809-21-4", "HEDP", "Etidronic acid", "C2H8O7P2", "Solid", 4498212,
  "A bisphosphonate: a scale inhibitor in cooling water and detergents, and a drug for Paget's bone disease.",
  lib=5031)
S("301-02-0", "Oleamide", "Oleamide", "C18H35NO", "Solid", 11730667,
  "The slip agent that keeps polyethylene bags from sticking together; the body also makes it, as a sleep signal.",
  smiles="CCCCCCCC/C=C\\CCCCCCCC(N)=O")
S("3164-85-0", "KEH", "Potassium 2-ethylhexanoate", "C8H15KO2", "Solid", 4091942,
  "A catalyst for polyisocyanurate foam and a drier for paints.",
  lib=5277)
S("4098-71-9", "IPDI", "Isophorone diisocyanate", "C12H18N2O2", "Liquid", 4183474,
  "An aliphatic isocyanate for coatings that must not yellow outdoors.",
  lib=5746)
S("420-46-2", "HFC143a", "1,1,1-Trifluoroethane", "C2H3F3", "Gas", 8100089,
  "HFC-143a, part of the refrigerant blends R-404A and R-507 in supermarket freezers.",
  lib=5790)
S("4553-62-2", "MGN", "2-Methylglutaronitrile", "C6H8N2", "Liquid", 52318730,
  "A by-product of making adiponitrile for nylon, hydrogenated to a diamine for polyamides.",
  lib=5899)
S("526-73-8", "TMB123", "1,2,3-Trimethylbenzene", "C9H12", "Liquid", 31272359,
  "Hemimellitene, from the C9 aromatics of reformed petrol.",
  lib=6248)
S("5329-14-6", "SulfamicAcid", "Sulfamic acid", "H3NSO3", "Solid", 1945917,
  "A solid acid that is safe to handle: the descaler of kettles and coffee machines.",
  smiles="NS(=O)(=O)O", props=("IsAcid",))
S("577-11-7", "Docusate", "Docusate sodium", "C20H37NaO7S", "Solid", 18923422,
  "A wetting agent strong enough to break up oil slicks, and the stool softener in pharmacies.",
  lib=6633)
S("60-00-4", "EDTA", "Ethylenediaminetetraacetic acid", "C10H16N2O8", "Solid", 182451,
  "EDTA grips metal ions with six arms: it softens water, keeps food and cosmetics from spoiling, and treats lead poisoning.",
  lib=6817)
S("624-92-0", "DMDS", "Dimethyl disulfide", "C2H6S2", "Liquid", 32561502,
  "A garlic-smelling liquid that sulfides refinery catalysts and fumigates soil.",
  lib=6976)
S("627-93-0", "DimethylAdipate", "Dimethyl adipate", "C8H14O4", "Liquid", 46624598,
  "A mild, biodegradable solvent for paint stripping and cleaning.",
  lib=6993)
S("6419-19-8", "ATMP", "Aminotris(methylenephosphonic acid)", "C3H12NO9P3", "Solid", 22715062,
  "A phosphonate scale inhibitor for cooling towers and boilers.",
  lib=7110)
S("67-48-1", "CholineCl", "Choline chloride", "C5H14ClNO", "Solid", 2779443,
  "Added by the hundred thousand tonnes to chicken feed: choline is a nutrient birds can't make enough of.",
  lib=7272)
S("75-38-7", "VDF", "Vinylidene fluoride", "C2H2F2", "Gas", 371942,
  "The monomer of PVDF, a fluoropolymer for chemical piping, lithium-battery binders and long-life architectural paint.",
  lib=7898, props=("IsMonomer",))
S("75-75-2", "MSA", "Methanesulfonic acid", "CH4O3S", "Liquid", 18595151,
  "A strong acid that doesn't oxidise: used in electroplating tin, in cleaners, and in making drugs.",
  lib=7916, props=("IsAcid",))
S("7620-77-1", "LiHSt", "Lithium 12-hydroxystearate", "C18H35LiO3", "Solid", 31629447,
  "The thickener of lithium grease, the most common grease in the world (1940s).",
  lib=7999)
S("7681-53-0", "NaH2PO2", "Sodium hypophosphite", "NaH2PO2", "Solid", 6567557,
  "The reducing agent of electroless nickel plating, which coats parts evenly without electricity.",
  lib=8036)
S("7758-19-2", "NaClO2", "Sodium chlorite", "NaClO2", "Solid", 1906074,
  "The stable salt from which chlorine dioxide is made on demand, for water treatment and bleaching textiles.",
  lib=8102)
S("7758-29-4", "STPP", "Sodium tripolyphosphate", "Na5P3O10", "Solid", 901091,
  "Once the builder of almost every laundry powder; the phosphate it released fed algal blooms, and most countries have banned it from detergents.",
  lib=8103)
S("79-21-0", "PAA", "Peracetic acid", "C2H4O3", "Liquid", 3512041,
  "A sharp-smelling disinfectant that breaks down to vinegar and oxygen, used in food plants, hospitals and sewage works.",
  lib=8229)
S("818-61-1", "HEA", "2-Hydroxyethyl acrylate", "C5H8O3", "Liquid", 73060426,
  "An acrylate with a spare OH group that crosslinks paints and adhesives.",
  lib=8351)
S("96-49-1", "EthyleneCarbonate", "Ethylene carbonate", "C3H4O3", "Solid", 8565759,
  "The solvent of lithium-ion battery electrolyte: it forms the protective film on the graphite anode.",
  lib=8867)
S("97-93-8", "TEAL", "Triethylaluminium", "C12H30Al2", "Liquid", 10320021,
  "It bursts into flame in air. Ziegler's co-catalyst for polyethylene and polypropylene.",
  lib=8899)
S("99-96-7", "PHBA", "4-Hydroxybenzoic acid", "C7H6O3", "Solid", 3626498,
  "The acid of the parabens, and of the liquid-crystal polymers of electronics connectors.",
  lib=8966)
S("75-52-5", "Nitromethane", "Nitromethane", "CH3NO2", "Liquid", 245564,
  "The fuel of drag racers and model engines, which carries its own oxygen.",
  smiles="C[N+](=O)[O-]")
S("592-76-7", "Heptene", "1-Heptene", "C7H14", "Liquid", 14039448,
  "A seven-carbon alpha-olefin for plasticiser alcohols.",
  lib=6771)
S("87-86-5", "PCP", "Pentachlorophenol", "C6HCl5O", "Solid", 1250286,
  "A wood preservative for telephone poles and railway sleepers since the 1930s; banned under the Stockholm Convention in 2015.",
  lib=8527)
S("108-03-2", "NitroPropane1", "1-Nitropropane", "C3H7NO2", "Liquid", 41442973,
  "A solvent for vinyl and epoxy coatings, one of the nitroparaffins of propane nitration.",
  lib=2500)
S("78-11-5", "PETN", "Pentaerythritol tetranitrate", "C5H8N4O12", "Solid", 42451,
  "One of the most powerful conventional explosives, the core of detonating cord, and also a heart medicine that widens blood vessels.",
  lib=8173)
S("100-61-8", "NMethylaniline", "N-Methylaniline", "C7H9N", "Liquid", 31636534,
  "An octane booster and a building block for dyes and agrochemicals.",
  lib=2019)
S("109-06-8", "Picoline2", "2-Methylpyridine", "C6H7N", "Liquid", 16009170,
  "2-Picoline, made from acetaldehyde and ammonia, on the way to 2-vinylpyridine.",
  lib=2546)
S("108-89-4", "Picoline4", "4-Methylpyridine", "C6H7N", "Liquid", 20833296,
  "4-Picoline, the start of the tuberculosis drug isoniazid.",
  lib=2533)
S("100-69-6", "VinylPyridine2", "2-Vinylpyridine", "C7H7N", "Liquid", 37748394,
  "Copolymerised into the latex that bonds tyre cords to rubber.",
  lib=2021)
S("100-99-2", "TIBA", "Triisobutylaluminium", "C12H27Al", "Liquid", 31619845,
  "A pyrophoric co-catalyst for Ziegler-Natta polymerisation.",
  lib=2027)
S("101-80-4", "ODA", "4,4'-Oxydianiline", "C12H12N2O", "Solid", 15995797,
  "The diamine of Kapton (DuPont, 1960s), the amber polyimide film that survives from cryogenic cold to 400 C.",
  lib=2116)
S("101-86-0", "HexylCinnamal", "alpha-Hexylcinnamaldehyde", "C15H20O", "Liquid", 12850234,
  "A jasmine-like scent in a great many soaps and detergents.",
  lib=2120)
S("102-01-2", "Acetoacetanilide", "Acetoacetanilide", "C10H11NO2", "Solid", 41888591,
  "Coupled with diazonium salts, it makes the arylide yellows, the pigments of yellow road markings and pencils.",
  lib=2164)
S("102-82-9", "Tributylamine", "Tributylamine", "C12H27N", "Liquid", 36816534,
  "A base and catalyst, and an extractant for metals.",
  lib=2177)
S("103-63-9", "PhenethylBromide", "Phenethyl bromide", "C8H9Br", "Liquid", 24438170,
  "A building block for drugs and fragrances that carry the phenethyl group.",
  lib=2232)
S("105-39-5", "EtClAc", "Ethyl chloroacetate", "C4H7ClO2", "Liquid", 36668180,
  "An ester used in the Darzens reaction and to make drugs and pesticides.",
  lib=2328)
S("105-45-3", "MAA", "Methyl acetoacetate", "C5H8O3", "Liquid", 38655966,
  "A beta-keto ester for pesticides, dyes and drugs such as the dihydropyridine heart medicines.",
  lib=2329)
S("105-83-9", "BAPMA", "Bis(3-aminopropyl)methylamine", "C7H19N3", "Liquid", 12268384,
  "A triamine for epoxy hardeners and polyurethane catalysts.",
  lib=2342)
S("106-91-2", "GMA", "Glycidyl methacrylate", "C7H10O3", "Liquid", 22736343,
  "A monomer with an epoxide on the side, for powder coatings and dental composites.",
  lib=2404)
S("1066-35-9", "Me2SiHCl", "Chlorodimethylsilane", "C2H7ClSi", "Liquid", 15655243,
  "A silane with an Si-H bond, for hydrosilylation chemistry and silicone end-caps.",
  lib=2421)
S("107-03-9", "PropaneThiol", "1-Propanethiol", "C3H8S", "Liquid", 38480878,
  "A thiol with the smell of cabbage, used to make the insecticide ethoprophos.",
  lib=2436)
S("107-19-7", "PropargylAlcohol", "Propargyl alcohol", "C3H4O", "Liquid", 6260284,
  "The simplest alcohol with a triple bond: a corrosion inhibitor in acid pickling and a building block for vitamin A.",
  lib=2445)
S("107-29-9", "Acetaldoxime", "Acetaldoxime", "C2H5NO", "Solid", 37698796,
  "An oxygen scavenger for boiler water, and a pesticide intermediate.",
  lib=2449)
S("107-64-2", "DSDMAC", "Distearyldimethylammonium chloride", "C38H80ClN", "Solid", 4478267,
  "The fabric softener of the 1960s to 1990s, which clings to fibres and makes them feel soft.",
  lib=2461)
S("107-87-9", "Pentanone2", "2-Pentanone", "C5H10O", "Liquid", 1191748,
  "Methyl propyl ketone, a solvent with a fruity smell.",
  lib=2466)
S("107-96-0", "MPA3", "3-Mercaptopropionic acid", "C3H6O2S", "Liquid", 57408474,
  "The thiol of tin stabilisers for PVC, and of hair-perm chemicals.",
  lib=2470)
S("1076-97-7", "CHDA", "1,4-Cyclohexanedicarboxylic acid", "C8H12O4", "Solid", 73160493,
  "Terephthalic acid with its ring hydrogenated, for weather-resistant polyester coatings.",
  lib=2484)
S("1078715-59-9", "DIPA", "Diisopropanolamine", "C6H15NO2", "Solid", 37431806,
  "An amine for removing hydrogen sulfide from gas (the ADIP process) and for cosmetics.",
  lib=2616)
S("108-59-8", "DimethylMalonate", "Dimethyl malonate", "C5H8O4", "Liquid", 10346518,
  "The malonic ester of the barbiturates and vitamins B1 and B6.",
  lib=2519)
S("110-91-8", "Morpholine", "Morpholine", "C4H9NO", "Liquid", 1733679,
  "An amine that boils with steam, so it guards the whole boiler circuit against corrosion; also a fruit-wax emulsifier.",
  smiles="C1COCCN1")
S("109-02-4", "NMM", "4-Methylmorpholine", "C5H11NO", "Liquid", 19849527,
  "A catalyst for polyurethane foam, and, oxidised, NMMO, the solvent that spins lyocell fibre.",
  lib=2545)
S("109-74-0", "Butyronitrile", "Butyronitrile", "C4H7N", "Liquid", 2237274,
  "A nitrile for making the poultry drug amprolium.",
  lib=2565)
S("110-89-4", "Piperidine", "Piperidine", "C5H11N", "Liquid", 24739,
  "The saturated ring of pyridine, named for black pepper's piperine: a base, a solvent, and a part of many drugs.",
  lib=2612)

E4.reactions += [
    R("PETN", "Pentaerythritol + 4 HNO3 -> PETN + 4 H2O", FLASK,
      "Pentaerythritol nitrated in cold concentrated nitric acid (1894).", wiki=42451, T=20),
    R("4-Nitrochlorobenzene", "Chlorobenzene + HNO3 -> NCB + H2O", CAT,
      "Chlorobenzene nitrated in mixed acid; the para isomer is crystallised out.", wiki="4-Nitrochlorobenzene",
      cat="H2SO4", T=50),
    R("Phosphine and Hypophosphite", "P4 + 3 NaOH + 3 H2O -> 3 NaH2PO2 + Phosphine", FLASK,
      "White phosphorus boiled in caustic soda: phosphine bubbles off and hypophosphite stays behind.",
      wiki=6567557, T=90),
    R("Ammonium Dimolybdate", "2 MoO3 + 2 NH3 + H2O -> ADM", MIX,
      "Molybdenum trioxide dissolved in ammonia water and crystallised.", wiki=46721957),
]
E5.reactions += [
    R("Nitromethane", "Methane + HNO3 -> Nitromethane + H2O", HEAT,
      "Methane nitrated in the gas phase at 400 C.", wiki=245564, T=400),
    R("Isophthalonitrile", "mXylene + 2 NH3 + 3 O2 -> IPN + 6 H2O", CAT,
      "m-Xylene ammoxidised over vanadium oxide.", wiki=63544943, cat="V2O5", T=400),
    R("m-Xylylenediamine", "IPN + 4 H2 -> MXDA", HIGHP,
      "Isophthalonitrile hydrogenated over nickel.", wiki=50748263, cat="Ni", T=100),
    R("2-Ethylhexyl Nitrate", "2EH + HNO3 -> EHN + H2O", FLASK,
      "2-Ethylhexanol esterified with nitric acid in mixed acid.", wiki=44254216, T=20),
    R("Etidronic Acid", "2 H3PO3 + AceticAnhydride -> HEDP + AcOH", FLASK,
      "Phosphorous acid and acetic anhydride.", wiki=4498212, T=120),
    R("Oleamide", "OleicAcid + NH3 -> Oleamide + H2O", PRESS,
      "Oleic acid heated with ammonia.", wiki=11730667, T=200),
    R("Potassium Octoate", "EHAcid + KOH -> KEH + H2O", MIX,
      "2-Ethylhexanoic acid neutralised by caustic potash.", wiki=4091942, dh=-55),
    R("IPDI Phosgenation", "IPDA + 2 COCl2 -> IPDI + 4 HCl", FLASK,
      "Isophorone diamine phosgenated.", wiki=4183474, T=150),
    R("Methylglutaronitrile", "Butadiene + 2 HCN -> MGN", HIGHP,
      "Butadiene hydrocyanated with a nickel catalyst; the branched dinitrile is the side product.",
      wiki=52318730, cat="Ni", T=100),
    R("Hemimellitene", "2 oXylene -> Toluene + TMB123", CAT,
      "o-Xylene disproportionated over a zeolite.", wiki=31272359, cat="ZSM5", T=400),
    R("Sulfamic Acid", "Urea + SO3 + H2SO4 -> 2 SulfamicAcid + CO2", MIX,
      "Urea treated with oleum.", wiki=1945917),
    R("Docusate", "DEHM + NaHSO3 -> Docusate", MIX,
      "Sodium bisulfite adds across the maleate's double bond.", wiki=18923422),
    R("EDTA", "EDA + 4 Glycolonitrile + 4 H2O -> EDTA + 4 NH3", FLASK,
      "Ethylenediamine takes four glycolonitriles; the nitriles are hydrolysed to acids (Bersworth, 1940s).",
      wiki=182451, T=100),
    R("Dimethyl Disulfide", "2 Methanethiol + S -> DMDS + H2S", CAT,
      "Methanethiol oxidised by sulfur over alumina.", wiki=32561502, cat="Alumina", T=60),
    R("Dimethyl Adipate", "Adipic + 2 Methanol -> DimethylAdipate + 2 H2O", CAT,
      "Adipic acid esterified with methanol.", wiki=46624598, cat="H2SO4", T=120),
    R("ATMP", "NH3 + 3 CH2O + 3 H3PO3 -> ATMP + 3 H2O", FLASK,
      "The Moedritzer-Irani reaction: ammonia, formaldehyde and phosphorous acid.", wiki=22715062, T=100),
    R("Choline Chloride", "Me3N + EO + HCl -> CholineCl", FLASK,
      "Trimethylamine, ethylene oxide and hydrochloric acid.", wiki=2779443, T=40),
    R("Vinylidene Fluoride", "HCFC142b -> VDF + HCl", HEAT,
      "HCFC-142b cracked at 600 C.", wiki=371942, T=600),
    R("Lithium Grease Soap", "RicinoleicAcid + H2 + LiOH -> LiHSt + H2O", HIGHP,
      "Castor oil's ricinoleic acid hydrogenated, then saponified with lithium hydroxide.", wiki=31629447,
      cat="Ni", T=150),
    R("Sodium Chlorite", "2 ClO2 + 2 NaOH + H2O2 -> 2 NaClO2 + O2 + 2 H2O", MIX,
      "Chlorine dioxide reduced by hydrogen peroxide in caustic soda.", wiki=1906074),
    R("Sodium Tripolyphosphate", "5 NaOH + 3 H3PO4 -> STPP + 7 H2O", HEAT,
      "Phosphoric acid neutralised to the right ratio and calcined at 400 C.", wiki=901091, T=400),
    R("Peracetic Acid", "AcOH + H2O2 -> PAA + H2O", CAT,
      "Acetic acid and hydrogen peroxide come to equilibrium over a sulfuric acid catalyst.", wiki=3512041,
      cat="H2SO4", T=40),
    R("Hydroxyethyl Acrylate", "AcrylicAcid + EO -> HEA", CAT,
      "Ethylene oxide opened by acrylic acid.", wiki=73060426, cat="FeCl3", T=80),
    R("Ethylene Carbonate", "EO + CO2 -> EthyleneCarbonate", CAT,
      "Carbon dioxide adds to ethylene oxide over a quaternary ammonium salt.", wiki=8565759, cat="TMACl", T=150),
    R("Triethylaluminium", "2 Al + 3 H2 + 6 Ethylene -> TEAL", HIGHP,
      "Ziegler's direct synthesis (1955): aluminium, hydrogen and ethylene combine.", wiki=10320021, T=120),
    R("Triisobutylaluminium", "2 Al + 3 H2 + 6 Isobutylene -> 2 TIBA", HIGHP,
      "The same direct synthesis with isobutylene.", wiki=31619845, T=120),
    R("4-Hydroxybenzoic Acid", "Phenol + CO2 -> PHBA", HIGHP,
      "Kolbe-Schmitt with potassium phenoxide, hotter: the carboxyl group goes para.", wiki=3626498,
      cat="KOH", T=240),
    R("Pentachlorophenol", "Phenol + 5 Cl2 -> PCP + 5 HCl", CAT,
      "Phenol chlorinated all the way round over aluminium chloride.", wiki=1250286, cat="AlCl3", T=150),
    R("Nitropropanes", "Propane + HNO3 -> NitroPropane1 + H2O", PRESS,
      "Propane nitrated in the gas phase; 1-nitropropane is distilled from the mixture.", wiki=41442973, T=400),
    R("N-Methylaniline", "Aniline + Methanol -> NMethylaniline + H2O", CRACKER,
      "Aniline methylated once over copper.", wiki=31636534, cat="Cu", T=250),
    R("Picolines", "6 Acetaldehyde + 2 NH3 -> Picoline2 + Picoline4 + 6 H2O + 2 H2", CAT,
      "The Chichibabin synthesis: acetaldehyde and ammonia close into pyridine rings over alumina.",
      wiki=16009170, cat="Alumina", T=400),
    R("2-Vinylpyridine", "Picoline2 + CH2O -> VinylPyridine2 + H2O", CAT,
      "2-Picoline condensed with formaldehyde and dehydrated.", wiki=37748394, cat="NaOH", T=250),
    R("4,4'-Oxydianiline", "2 NCB + 2 NaOH + 6 H2 -> ODA + 2 NaCl + 5 H2O", CAT,
      "Nitrochlorobenzene joins nitrophenoxide into a dinitrodiphenyl ether, then hydrogenated.", wiki=15995797,
      cat="Pd", T=120),
    R("Hexyl Cinnamaldehyde", "Benzaldehyde + Octanal -> HexylCinnamal + H2O", CAT,
      "Benzaldehyde and octanal condensed with a base.", wiki=12850234, cat="NaOH", T=50),
    R("Acetoacetanilide", "Diketene + Aniline -> Acetoacetanilide", FLASK,
      "Aniline opens the diketene ring.", wiki=41888591, T=30),
    R("Tributylamine", "Dibutylamine + Butanol -> Tributylamine + H2O", CAT,
      "Dibutylamine alkylated with butanol over nickel.", wiki=36816534, cat="Ni", T=200),
    R("Phenethyl Bromide", "Styrene + HBr -> PhenethylBromide", LIGHT,
      "Hydrogen bromide adds to styrene the 'wrong' way round under light (anti-Markovnikov).", wiki=24438170, T=20),
    R("Ethyl Chloroacetate", "ClAcOH + Ethanol -> EtClAc + H2O", CAT,
      "Chloroacetic acid esterified with ethanol.", wiki=36668180, cat="H2SO4", T=90),
    R("Methyl Acetoacetate", "Diketene + Methanol -> MAA", FLASK,
      "Methanol opens the diketene ring.", wiki=38655966, T=40),
    R("Bis(aminopropyl)methylamine", "Methylamine + 2 Acrylonitrile + 4 H2 -> BAPMA", CAT,
      "Methylamine adds to two acrylonitriles; the nitriles are hydrogenated.", wiki=12268384, cat="Ni", T=100),
    R("Glycidyl Methacrylate", "MethacrylicAcid + Epichlorohydrin + NaOH -> GMA + NaCl + H2O", FLASK,
      "Methacrylic acid joined to epichlorohydrin, the epoxide reclosed by caustic soda.", wiki=22736343, T=90),
    R("Chlorodimethylsilane", "Me2SiCl2 + MeSiHCl2 -> Me2SiHCl + MeSiCl3", CAT,
      "Methyl, hydrogen and chlorine swap between silicons over aluminium chloride.", wiki=15655243,
      cat="AlCl3", T=200),
    R("Propanethiol", "Propanol + H2S -> PropaneThiol + H2O", CAT,
      "1-Propanol and hydrogen sulfide over alumina.", wiki=38480878, cat="Alumina", T=350),
    R("Propargyl Alcohol", "Acetylene + CH2O -> PropargylAlcohol", PRESS,
      "Reppe's ethynylation: one formaldehyde on acetylene, with a copper acetylide catalyst.", wiki=6260284, T=100),
    R("Acetaldoxime", "Acetaldehyde + NH2OH -> Acetaldoxime + H2O", MIX,
      "Acetaldehyde and hydroxylamine.", wiki=37698796),
    R("Fabric Softener", "2 StearylAlcohol + Methylamine + CH3Cl -> DSDMAC + 2 H2O", FLASK,
      "Stearyl alcohol aminated with methylamine, then quaternised with methyl chloride.", wiki=4478267, T=150),
    R("2-Pentanone", "Acetone + Acetaldehyde + H2 -> Pentanone2 + H2O", CAT,
      "Acetone and acetaldehyde condensed, then hydrogenated over palladium.", wiki=1191748, cat="Pd", T=120),
    R("3-Mercaptopropionic Acid", "AcrylicAcid + H2S -> MPA3", CAT,
      "Hydrogen sulfide adds to acrylic acid.", wiki=57408474, cat="NaOH", T=50),
    R("Cyclohexanedicarboxylic Acid", "TPA + 3 H2 -> CHDA", HIGHP,
      "Terephthalic acid's ring hydrogenated over palladium.", wiki=73160493, cat="Pd", T=200),
    R("Diisopropanolamine", "2 PO + NH3 -> DIPA", FLASK,
      "Two propylene oxides opened by ammonia.", wiki=37431806, T=100),
    R("Dimethyl Malonate", "ClAcOH + CO + 2 Methanol -> DimethylMalonate + HCl + H2O", CAT,
      "Chloroacetate carbonylated in methanol with a cobalt catalyst.", wiki=10346518, cat="Co", T=60),
    R("Morpholine", "2 EO + NH3 -> Morpholine + H2O", CAT,
      "Diethanolamine, from ethylene oxide and ammonia, dehydrated by sulfuric acid.", wiki=1733679,
      cat="H2SO4", T=180),
    R("N-Methylmorpholine", "Morpholine + Methanol -> NMM + H2O", CAT,
      "Morpholine methylated over copper.", wiki=19849527, cat="Cu", T=220),
    R("Butyronitrile", "Butanol + NH3 -> Butyronitrile + H2O + 2 H2", CRACKER,
      "Butanol dehydrogenated and aminated over nickel.", wiki=2237274, cat="Ni", T=300),
    R("Piperidine", "Pyridine + 3 H2 -> Piperidine", CAT,
      "Pyridine hydrogenated over molybdenum sulfide.", wiki=24739, cat="MoS2", T=200),
]
E6.reactions += [
    R("HFC-143a", "HCFC142b + HF -> HFC143a + HCl", CAT,
      "The last chlorine of HCFC-142b swapped for fluorine.", wiki=8100089, cat="SbCl5", T=100),
    R("Methanesulfonic Acid", "Methane + SO3 -> MSA", PRESS,
      "Grillo's direct process (BASF, 2019): methane and sulfur trioxide, started by a peroxide.", wiki=18595151, T=50),
    R("Heptene", "Propylene + 1-Butene -> Heptene", CAT,
      "Propylene and butene codimerised on a nickel catalyst.", wiki=14039448, cat="Ni", T=50),
]

import authored_canon_5  # noqa: E402,F401
