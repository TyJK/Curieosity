"""
Curieosity's industrial chemistry, part 2 (see authored_canon.py): the rest of the
10,000-tonne list.
"""

from authored_canon import S, R
from authored_content import E4, E5, E6
from gen_authored import MIX, HEAT, CAT, PRESS, FLASK, ECELL, CRACKER, HIGHP

# --- intermediates the canon set lacks ---------------------------------------------------
S(None, "CH2Cl2", "Dichloromethane", "CH2Cl2", "Liquid", "Dichloromethane",
  "Methylene chloride: a dense, volatile solvent that strips paint, degreases metal and once decaffeinated coffee.",
  smiles="ClCCl")
S(None, "Isononanol", "Isononyl alcohol", "C9H20O", "Liquid", "Isononyl_alcohol",
  "A branched nine-carbon alcohol made by the oxo process, almost all of it turned into plasticisers.",
  smiles="CC(CCO)CC(C)(C)C")
S(None, "Butoxyethanol", "2-Butoxyethanol", "C6H14O2", "Liquid", "2-Butoxyethanol",
  "Butyl glycol: the grease-cutting solvent of glass and floor cleaners, and a solvent for paints and inks.",
  smiles="CCCCOCCO")
S(None, "StearylAlcohol", "Stearyl alcohol", "C18H38O", "Solid", "Stearyl_alcohol",
  "A waxy eighteen-carbon alcohol from stearic acid: it thickens creams and lotions and keeps them from separating.",
  smiles="CCCCCCCCCCCCCCCCCCO")
S(None, "TMACl", "Tetramethylammonium chloride", "C4H12ClN", "Solid", 22623885,
  "The simplest quaternary ammonium salt, made from trimethylamine and methyl chloride.",
  lib=7908)
S(None, "oNitrotoluene", "2-Nitrotoluene", "C7H7NO2", "Liquid", "2-Nitrotoluene",
  "The ortho product of nitrating toluene, a pale yellow oil on the way to o-toluidine, dyes and herbicides.",
  smiles="Cc1ccccc1[N+](=O)[O-]")

# --- the canon substances ------------------------------------------------------------------
S("75-31-0", "Isopropylamine", "Isopropylamine", "C3H9N", "Liquid", 9874824,
  "A volatile amine whose salt with glyphosate is the form in Roundup; also a start for atrazine and other herbicides.",
  lib=7892)
S("75-88-7", "HCFC133a", "2-Chloro-1,1,1-trifluoroethane", "C2H2ClF3", "Gas", 52830815,
  "HCFC-133a, made on the way to the refrigerant HFC-134a.",
  lib=7923)
S("811-97-2", "R134a", "1,1,1,2-Tetrafluoroethane", "C2H2F4", "Gas", 1735557,
  "HFC-134a, the refrigerant that replaced Freon 12 in car air conditioners and fridges in the 1990s: harmless to ozone, but a strong greenhouse gas now being phased down in turn.",
  lib=8334)
S("7775-14-6", "Na2S2O4", "Sodium dithionite", "Na2S2O4", "Solid", 2467302,
  "A powerful reducing agent: it turns indigo into the soluble leuco form that dyes denim, and bleaches wood pulp and clay.",
  lib=8118)
S("79-04-9", "ClAcCl", "Chloroacetyl chloride", "C2H2Cl2O", "Liquid", 20591657,
  "A doubly reactive building block for the herbicides alachlor and metolachlor, and for lidocaine.",
  lib=8224)
S("84852-15-3", "Nonylphenol", "Nonylphenol", "C15H24O", "Liquid", 1475625,
  "Phenol with a branched nine-carbon tail, made for detergents. It breaks down into a substance that mimics oestrogen in fish, and Europe banned most uses in 2003.",
  lib=8454)
S("872-50-4", "NMP", "N-Methyl-2-pyrrolidone", "C5H9NO", "Liquid", 3339289,
  "A powerful, high-boiling solvent for polymers: it casts the electrode slurry of lithium-ion batteries and strips paint.",
  lib=8544)
S("95-63-6", "TMB124", "1,2,4-Trimethylbenzene", "C9H12", "Liquid", 4547829,
  "Pseudocumene, from the C9 cut of petrol: oxidised to trimellitic anhydride for heat-proof plasticisers.",
  lib=8823)
S("96-14-0", "MethylPentane3", "3-Methylpentane", "C6H14", "Liquid", 20692146,
  "A branched hexane with a higher octane than the straight chain, made by isomerising light naphtha for petrol.",
  lib=8850)
S("96-37-7", "MCP", "Methylcyclopentane", "C6H12", "Liquid", 28411896,
  "A five-membered ring with a methyl group, found in naphtha and in equilibrium with cyclohexane over acid catalysts.",
  lib=8863)
S("101-84-8", "DiphenylEther", "Diphenyl ether", "C12H10O", "Solid", 17140219,
  "With biphenyl it makes Dowtherm A, the heat-transfer fluid of solar and chemical plants; on its own it smells of geraniums.",
  lib=2119)
S("108-11-2", "MIBC", "4-Methyl-2-pentanol", "C6H14O", "Liquid", 25907840,
  "Methyl isobutyl carbinol, the frother of mineral flotation: its bubbles carry copper and lead ores up out of the slurry.",
  lib=2503)
S("108-20-3", "DIPE", "Diisopropyl ether", "C6H14O", "Liquid", 1572820,
  "A solvent and petrol additive, notorious for growing explosive peroxides in old bottles.",
  lib=2507)
S("109-55-7", "DMAPA", "Dimethylaminopropylamine", "C5H14N2", "Liquid", 39596102,
  "The amine that builds cocamidopropyl betaine, the mild foaming surfactant of shampoos and body washes.",
  lib=2559)
S("112-18-5", "LDAO", "Lauryldimethylamine oxide", "C14H31NO", "Liquid", 21872492,
  "A foaming, grease-cutting surfactant in dish soaps and shampoos; biochemists use it to coax proteins out of membranes.",
  lib=2708)
S("1312-81-8", "La2O3", "Lanthanum oxide", "La2O3", "Solid", 2700960,
  "Lanthanum oxide gives camera and telescope glass a high refractive index with little dispersion, and goes into catalytic cracking catalysts.",
  lib=3308)
S("1338-43-8", "Span80", "Sorbitan monooleate", "C24H44O6", "Liquid", 59228796,
  "Span 80, a sorbitol-based emulsifier that holds water droplets in oil: margarine, cosmetics, and explosives.",
  lib=3403)
S("14887-42-4", "K2HPO4", "Dipotassium phosphate", "K2HPO4", "Solid", 5390895,
  "A buffer and source of potassium: it keeps coffee creamer from curdling and feeds microbes in fermenters.",
  lib=8100)
S("16219-75-3", "ENB", "Ethylidene norbornene", "C9H12", "Liquid", 56150440,
  "The third monomer of EPDM rubber: its spare double bond gives the sulfur something to crosslink.",
  lib=3991)
S("28553-12-0", "DINP", "Diisononyl phthalate", "C26H42O4", "Liquid", 19866185,
  "A plasticiser for PVC cables, flooring and car interiors, replacing DEHP since the 2000s.",
  lib=5050)
S("34590-94-8", "DPM", "Dipropylene glycol methyl ether", "C7H16O3", "Liquid", 46757344,
  "A slow-evaporating glycol ether solvent in cleaners, inks and paints.",
  lib=5431)
S("354-33-6", "HFC125", "Pentafluoroethane", "C2HF5", "Gas", 30864980,
  "HFC-125, half of the R-410A refrigerant of air conditioners, and a fire suppressant.",
  lib=5471)
S("2837-89-0", "HCFC124", "2-Chloro-1,1,1,2-tetrafluoroethane", "C2HClF4", "Gas", 2711031,
  "HCFC-124, a refrigerant and fire suppressant, and a step on the way to HFC-125.",
  lib=5039)
S("374-07-2", "CFC114a", "1,1-Dichlorotetrafluoroethane", "C2Cl2F4", "Gas", 73537332,
  "CFC-114a, made on the way to HFC-134a by one route; restricted under the Montreal Protocol.",
  lib=5598)
S("115-77-5", "Pentaerythritol", "Pentaerythritol", "C5H12O4", "Solid", 57069,
  "Four alcohol groups on one carbon (Tollens, 1891): the core of alkyd paints and Irganox antioxidants, and nitrated, of the explosive PETN.",
  lib=2789)
S("6683-19-8", "Irganox1010", "Irganox 1010", "C73H108O12", "Solid", 56947013,
  "The most used antioxidant in plastics: four hindered phenols on a pentaerythritol core keep polyolefins from going brittle.",
  lib=7267)
S("2082-79-3", "Irganox1076", "Irganox 1076", "C35H62O3", "Solid", 76552019,
  "A hindered phenol with an eighteen-carbon tail that dissolves in polyethylene and keeps it from oxidising.",
  lib=4417)
S("68-12-2", "DMF", "Dimethylformamide", "C3H7NO", "Liquid", 1415135,
  "A polar solvent that dissolves almost anything: acrylic and spandex fibres are spun from it.",
  lib=7366)
S("75-10-5", "HFC32", "Difluoromethane", "CH2F2", "Gas", 1426766,
  "HFC-32, the other half of R-410A, now used alone in air conditioners for its lower warming potential.",
  lib=7883)
S("75-79-6", "MeSiCl3", "Methyltrichlorosilane", "CH3Cl3Si", "Liquid", 13037339,
  "A by-product of the silicone process that crosslinks silicones into resins, and waterproofs masonry.",
  lib=7919)
S("75-77-4", "Me3SiCl", "Chlorotrimethylsilane", "C3H9ClSi", "Liquid", 3333005,
  "The chemist's trimethylsilyl group in a bottle, used to cap alcohols and amines; it caps silicone chains too.",
  smiles="C[Si](C)(C)Cl")
S("107-46-0", "HMDSO", "Hexamethyldisiloxane", "C6H18OSi2", "Liquid", 6870773,
  "The smallest silicone: an end-cap that sets the chain length of silicone oils, and a cleaning solvent.",
  lib=2456)
S("7681-57-4", "Na2S2O5", "Sodium metabisulfite", "Na2S2O5", "Solid", 979272,
  "A preservative and antioxidant (E223) for wine, dried fruit and beer, which releases sulfur dioxide in water.",
  lib=8038)
S("101-54-2", "ADPA4", "4-Aminodiphenylamine", "C12H12N2", "Solid", 57733027,
  "The core of the antiozonants that keep tyres from cracking.",
  lib=2110)
S("793-24-8", "SixPPD", "6PPD", "C18H24N2", "Solid", 66017164,
  "The antiozonant in nearly every tyre. In 2020 its ozone product, washed off roads, was found to be what kills coho salmon in Seattle's creeks.",
  lib=8255)
S("95-53-4", "oToluidine", "o-Toluidine", "C7H9N", "Liquid", 12310347,
  "The amine of toluene's ortho position, used for rubber chemicals, the herbicide metolachlor and dyes.",
  lib=8821)
S("98-83-9", "AMS", "alpha-Methylstyrene", "C9H10", "Liquid", 20995816,
  "A by-product of the cumene process, copolymerised to make plastics stand more heat.",
  lib=8930)
S("75-59-2", "TMAH", "Tetramethylammonium hydroxide", "C4H13NO", "Solid", 5162703,
  "A strong, metal-free base: the developer that washes exposed photoresist off silicon wafers, and an etchant for silicon.",
  lib=7909)
S("79-46-9", "NitroPropane2", "2-Nitropropane", "C3H7NO2", "Liquid", 36130214,
  "A solvent for inks, coatings and adhesives, made by nitrating propane in the gas phase.",
  lib=8242)
S("100-18-5", "DIPB", "1,4-Diisopropylbenzene", "C12H18", "Liquid", 59302935,
  "Benzene with two isopropyl groups: through a double cumene process it becomes hydroquinone.",
  lib=2003)
S("110-62-3", "Pentanal", "Pentanal", "C5H10O", "Liquid", 10289292,
  "Valeraldehyde, made by the oxo process from butenes, on the way to 2-propylheptanol.",
  lib=2602)
S("10042-59-8", "PropylHeptanol", "2-Propylheptanol", "C10H22O", "Liquid", 31438264,
  "The oxo alcohol of a larger plasticiser, DPHP, used for cables and car interiors.",
  lib=2063)
S("10117-38-1", "KHSO3", "Potassium bisulfite", "KHSO3", "Aqueous", 13294667,
  "A preservative (E228) that releases sulfur dioxide, used in winemaking.",
  lib=8113)
S("10124-41-1", "CaS2O3", "Calcium thiosulfate", "CaS2O3", "Aqueous", 4693311,
  "A liquid fertiliser of calcium and sulfur that also loosens sodic soils.",
  lib=2142)
S("102687-65-0", "HCFO1233zd", "trans-1-Chloro-3,3,3-trifluoropropene", "C3H2ClF3", "Liquid", 52070082,
  "HCFO-1233zd(E), an insulating-foam blowing agent and chiller refrigerant whose double bond lets it break down in days rather than decades.",
  lib=2204)
S("460-73-1", "HFC245fa", "1,1,1,3,3-Pentafluoropropane", "C3H3F5", "Gas", 6231117,
  "HFC-245fa, the blowing agent of rigid insulating foam after HCFC-141b was banned.",
  lib=5907)
S("106-31-0", "ButyricAnhydride", "Butyric anhydride", "C8H14O3", "Liquid", 30240135,
  "The anhydride of butyric acid, used to make cellulose acetate butyrate, a tough plastic for tool handles and lacquers.",
  lib=2382)
S("106-88-7", "EpoxyButane", "1,2-Epoxybutane", "C4H8O", "Liquid", 59088105,
  "Butylene oxide: an acid scavenger that stabilises chlorinated solvents.",
  lib=2402)
S("107-16-4", "Glycolonitrile", "Glycolonitrile", "C2H3NO", "Liquid", 27447333,
  "Formaldehyde cyanohydrin, on the way to glycine and the chelating agents EDTA and NTA.",
  lib=2443)
S("107-25-5", "MVE", "Methyl vinyl ether", "C3H6O", "Gas", 30624428,
  "Copolymerised with maleic anhydride (Gantrez), it makes the polymer that holds dentures in and toothpaste flavour on teeth.",
  lib=2448)
S("107-88-0", "BDO13", "1,3-Butanediol", "C4H10O2", "Liquid", 14188289,
  "A diol for polyester plasticisers and cosmetics; in the body it becomes the ketone beta-hydroxybutyrate.",
  lib=2467)
S("108-99-6", "Picoline3", "3-Methylpyridine", "C6H7N", "Liquid", 17103072,
  "3-Picoline: oxidised, it becomes niacin, vitamin B3, added to flour and animal feed.",
  lib=2538)
S("110-43-0", "Heptanone2", "2-Heptanone", "C7H14O", "Liquid", 15250836,
  "Methyl amyl ketone, a solvent for coatings, with the smell of blue cheese and of honeybee alarm.",
  lib=2600)
S("111-30-8", "Glutaraldehyde", "Glutaraldehyde", "C5H8O2", "Liquid", 192070,
  "A cold sterilant for endoscopes and a tanning agent: its two aldehyde ends crosslink proteins, fixing cells for the electron microscope.",
  lib=2645)
S("112-07-2", "BGA", "2-Butoxyethyl acetate", "C8H16O3", "Liquid", 47759167,
  "Butyl glycol acetate, a slow-drying solvent for lacquers and inks that helps paint flow out smoothly.",
  lib=2704)
S("118-79-6", "TBP246", "2,4,6-Tribromophenol", "C6H3Br3O", "Solid", 25854081,
  "A flame retardant and fungicide for timber; it is what makes cork taint smell musty in wine.",
  lib=2836)
S("121-44-8", "Et3N", "Triethylamine", "C6H15N", "Liquid", 1806886,
  "The organic chemist's go-to base for mopping up acid: it smells of fish and ammonia.",
  lib=2982)
S("122-20-3", "TIPA", "Triisopropanolamine", "C9H21NO3", "Solid", 37431798,
  "An additive that makes cement grind finer and gain strength.",
  lib=3021)
S("122-99-6", "Phenoxyethanol", "Phenoxyethanol", "C8H10O2", "Liquid", 5808466,
  "A gentle preservative in cosmetics and vaccines, and the fixative of perfumes.",
  lib=3035)
S("124-19-6", "Nonanal", "Nonanal", "C9H18O", "Liquid", 14575416,
  "An aldehyde that smells of rose and citrus peel; mosquitoes find people partly by the nonanal on our skin.",
  lib=3106)
S("13472-45-2", "Na2WO4", "Sodium tungstate", "Na2WO4", "Solid", 2845376,
  "The water-soluble form tungsten takes on its way out of its ores, and a catalyst for oxidising with hydrogen peroxide.",
  lib=3447)
S("13674-84-5", "TCPP", "Tris(2-chloroisopropyl) phosphate", "C9H18Cl3O4P", "Liquid", 76213261,
  "The main flame retardant of polyurethane insulating foam.",
  lib=3499)
S("1562-00-1", "NaIsethionate", "Sodium isethionate", "C2H5NaO4S", "Solid", 51510868,
  "The salt that, joined to coconut fatty acid, makes the mild syndet bars such as Dove.",
  lib=3930)
S("15630-89-4", "Percarbonate", "Sodium percarbonate", "2Na2CO3·3H2O2", "Solid", 388198,
  "Hydrogen peroxide locked into soda crystals: the oxygen bleach of washing powders and 'oxy' stain removers.",
  lib=3933)
S("1761-71-3", "PACM", "4,4'-Diaminodicyclohexylmethane", "C13H26N2", "Solid", 54979439,
  "Methylenedianiline with both rings hydrogenated, for light-stable polyurethanes and clear nylons.",
  lib=4154)
S("25013-15-4", "Vinyltoluene", "Vinyltoluene", "C9H10", "Liquid", 51317436,
  "A methylated styrene used in place of styrene in polyester resins and paints.",
  lib=4712)
S("2782-57-2", "NaDCC", "Sodium dichloroisocyanurate", "C3Cl2N3NaO3", "Solid", 8359810,
  "The chlorine tablets of swimming pools and emergency water purification.",
  lib=5014)
S("28182-81-2", "HDI", "Hexamethylene diisocyanate", "C8H12N2O2", "Liquid", 4183464,
  "The isocyanate of car paints and other polyurethane coatings that must not yellow in sunlight.",
  lib=8366)
S("78-59-1", "Isophorone", "Isophorone", "C9H14O", "Liquid", 9193504,
  "A cyclic ketone made from three acetones: a solvent for coatings and inks, and the start of isophorone diisocyanate.",
  lib=8183)
S("2855-13-2", "IPDA", "Isophorone diamine", "C10H22N2", "Liquid", 58157026,
  "An epoxy hardener, and the amine of isophorone diisocyanate for weatherproof coatings.",
  lib=5048)
S("79-31-2", "IsobutyricAcid", "Isobutyric acid", "C4H8O2", "Liquid", 859006,
  "A branched butyric acid with a rancid smell, made into esters for flavours and plastics.",
  lib=8234)
S("3010-96-6", "TMCD", "2,2,4,4-Tetramethyl-1,3-cyclobutanediol", "C8H16O2", "Solid", 22695288,
  "A stiff, square diol that Eastman built into Tritan copolyester (2007), a clear, tough plastic free of bisphenol A.",
  lib=5164)

E4.reactions += [
    R("Pentaerythritol", "Acetaldehyde + 4 CH2O + NaOH -> Pentaerythritol + HCOONa", FLASK,
      "Acetaldehyde condensed with formaldehyde three times, then a fourth reduces it (Tollens, 1891).",
      wiki=57069, T=50),
    R("Sodium Metabisulfite", "SodaAsh + 2 SO2 -> Na2S2O5 + CO2", MIX,
      "Sulfur dioxide bubbled through soda solution until the salt crystallises.", wiki=979272),
    R("Tribromophenol", "Phenol + 3 Br2 -> TBP246 + 3 HBr", MIX,
      "Bromine water on phenol: the white precipitate is the classic test for phenols.", wiki=25854081),
    R("Lanthanum Oxide", "La2CO33 -> La2O3 + 3 CO2", HEAT,
      "Lanthanum carbonate calcined.", wiki=2700960, T=900),
    R("Sodium Tungstate", "WO3 + 2 NaOH -> Na2WO4 + H2O", MIX,
      "Tungsten trioxide dissolved in caustic soda.", wiki=2845376),
    R("Diphenyl Ether", "Chlorobenzene + Phenol + NaOH -> DiphenylEther + NaCl + H2O", CAT,
      "The Ullmann condensation: phenoxide displaces chlorine from chlorobenzene with a copper catalyst.",
      wiki=17140219, cat="Cu", T=200),
    R("o-Toluidine", "oNitrotoluene + 3 H2 -> oToluidine + 2 H2O", CAT,
      "o-Nitrotoluene hydrogenated over nickel.", wiki=12310347, cat="Ni", T=100),
]
E5.reactions += [
    R("Dichloromethane", "CH3Cl + Cl2 -> CH2Cl2 + HCl", HEAT,
      "Methyl chloride chlorinated again at about 400 C.", wiki="Dichloromethane", T=400, dh=-100),
    R("Isononanol", "Diisobutylene + CO + 2 H2 -> Isononanol", HIGHP,
      "Diisobutylene hydroformylated with a cobalt catalyst, then hydrogenated.", wiki="Isononyl_alcohol",
      cat="Co", T=170),
    R("Diisononyl Phthalate", "PhthalicAnhydride + 2 Isononanol -> DINP + H2O", CAT,
      "Phthalic anhydride esterified with isononanol.", wiki=19866185, cat="H2SO4", T=200),
    R("Butyl Glycol", "EO + Butanol -> Butoxyethanol", CAT,
      "Ethylene oxide opened by butanol with a base catalyst.", wiki="2-Butoxyethanol", cat="NaOH", T=150),
    R("Butyl Glycol Acetate", "Butoxyethanol + AcOH -> BGA + H2O", CAT,
      "Butyl glycol esterified with acetic acid.", wiki=47759167, cat="H2SO4", T=110),
    R("Stearyl Alcohol", "StearicAcid + 2 H2 -> StearylAlcohol + H2O", HIGHP,
      "Stearic acid hydrogenated over copper chromite at 250 atmospheres.", wiki="Stearyl_alcohol", cat="Cu", T=280),
    R("Isopropylamine", "Isopropanol + NH3 -> Isopropylamine + H2O", CAT,
      "Isopropanol aminated with ammonia over nickel.", wiki=9874824, cat="Ni", T=180),
    R("Sodium Dithionite", "HCOONa + 2 SO2 + NaOH -> Na2S2O4 + CO2 + H2O", FLASK,
      "The formate process: sodium formate reduces sulfur dioxide in aqueous methanol.", wiki=2467302, T=80),
    R("Chloroacetyl Chloride", "ClAcOH + COCl2 -> ClAcCl + CO2 + HCl", FLASK,
      "Chloroacetic acid turned into its acid chloride by phosgene.", wiki=20591657, T=100),
    R("Nonylphenol", "Phenol + 3 Propylene -> Nonylphenol", CAT,
      "Propylene trimer (nonene) alkylates phenol over an acid catalyst.", wiki=1475625, cat="H3PO4", T=120),
    R("N-Methylpyrrolidone", "GBL + Methylamine -> NMP + H2O", PRESS,
      "gamma-Butyrolactone heated with methylamine.", wiki=3339289, T=250),
    R("Xylene Disproportionation", "2 mXylene -> Toluene + TMB124", CAT,
      "Methyl groups hop between xylenes over a zeolite, giving toluene and trimethylbenzenes.", wiki=4547829,
      cat="ZSM5", T=400),
    R("Isomerising Hexane", "Hexane -> MethylPentane3", CRACKER,
      "Light naphtha isomerised over platinum on chlorided alumina, for octane.", wiki=20692146, cat="Pt", T=150),
    R("Ring Contraction", "Cyclohexane -> MCP", CAT,
      "Cyclohexane isomerised by aluminium chloride: the six-ring and the five-ring come to equilibrium.",
      wiki=28411896, cat="AlCl3", T=80),
    R("MIBC", "MIBK + H2 -> MIBC", CAT,
      "Methyl isobutyl ketone hydrogenated over nickel.", wiki=25907840, cat="Ni", T=120),
    R("Diisopropyl Ether", "Propylene + Isopropanol -> DIPE", CAT,
      "Propylene adds to isopropanol over an acid catalyst; it is also a by-product of making isopropanol.",
      wiki=1572820, cat="H2SO4", T=100),
    R("DMAPA", "Acrylonitrile + Me2NH + 2 H2 -> DMAPA", CAT,
      "Dimethylamine adds to acrylonitrile, then the nitrile is hydrogenated.", wiki=39596102, cat="Ni", T=100),
    R("Amine Oxide", "Dodecanol + Me2NH + H2O2 -> LDAO + 2 H2O", FLASK,
      "Dodecanol aminated with dimethylamine, then the amine oxidised by hydrogen peroxide.", wiki=21872492, T=70),
    R("Span 80", "Sorbitol + OleicAcid -> Span80 + 2 H2O", CAT,
      "Sorbitol closes into sorbitan and is esterified with oleic acid at 200 C.", wiki=59228796, cat="NaOH", T=210),
    R("Dipotassium Phosphate", "H3PO4 + 2 KOH -> K2HPO4 + 2 H2O", FLASK,
      "Phosphoric acid two-thirds neutralised with caustic potash.", wiki=5390895, dh=-100),
    R("Ethylidene Norbornene", "VNB -> ENB", CAT,
      "Vinylnorbornene's double bond shifted into the ring's side by a sodium catalyst.",
      wiki=56150440, cat="Na", T=30),
    R("Dipropylene Glycol Methyl Ether", "PGME + PO -> DPM", CAT,
      "Methoxypropanol opened onto a second propylene oxide.", wiki=46757344, cat="NaOH", T=120),
    R("Irganox 1010", "Pentaerythritol + 4 DTBP26 + 4 MethylAcrylate -> Irganox1010 + 4 Methanol", CAT,
      "Di-tert-butylphenol adds to methyl acrylate; four of the esters are transesterified onto pentaerythritol (Geigy).",
      wiki=56947013, cat="NaOMe", T=150),
    R("Irganox 1076", "DTBP26 + MethylAcrylate + StearylAlcohol -> Irganox1076 + Methanol", FLASK,
      "The same hindered-phenol ester, transesterified with stearyl alcohol.", wiki=76552019, T=150),
    R("Dimethylformamide", "Me2NH + CO -> DMF", CAT,
      "Dimethylamine carbonylated with sodium methoxide as catalyst.", wiki=1415135, cat="NaOMe", T=100),
    R("Redistributing Silanes", "Me2SiCl2 + SiCl4 -> 2 MeSiCl3", CAT,
      "Methyl groups and chlorines swap between silicon atoms over aluminium chloride.", wiki=13037339,
      cat="AlCl3", T=300),
    R("Chlorotrimethylsilane", "2 Me2SiCl2 -> Me3SiCl + MeSiCl3", CAT,
      "Dimethyldichlorosilane disproportionated over aluminium chloride.", wiki=3333005, cat="AlCl3", T=350),
    R("Hexamethyldisiloxane", "2 Me3SiCl + H2O -> HMDSO + 2 HCl", MIX,
      "Chlorotrimethylsilane hydrolysed: two silyl groups share one oxygen.", wiki=6870773),
    R("4-Aminodiphenylamine", "Aniline + Nitrobenzene + 2 H2 -> ADPA4 + 2 H2O", CAT,
      "Aniline couples to nitrobenzene in base; the product is hydrogenated over platinum (Flexsys, 1990s).",
      wiki=57733027, cat="Pt", T=80),
    R("6PPD", "ADPA4 + MIBK + H2 -> SixPPD + H2O", CAT,
      "4-Aminodiphenylamine reductively aminated with methyl isobutyl ketone.", wiki=66017164, cat="Pt", T=150),
    R("Ortho Nitration", "Toluene + HNO3 -> oNitrotoluene + H2O", CAT,
      "Toluene nitrated once in mixed acid; the ortho isomer, the larger part, is distilled from the para.",
      wiki="2-Nitrotoluene", cat="H2SO4", T=40),
    R("alpha-Methylstyrene", "Cumene -> AMS + H2", CAT,
      "Cumene dehydrogenated over iron oxide, like ethylbenzene to styrene.", wiki=20995816, cat="Fe3O4", T=600),
    R("Tetramethylammonium Chloride", "Me3N + CH3Cl -> TMACl", FLASK,
      "Trimethylamine quaternised by methyl chloride.", wiki=22623885, T=60),
    R("TMAH", "2 TMACl + 2 H2O -> 2 TMAH + Cl2 + H2", ECELL,
      "Electrolysis across a membrane swaps chloride for hydroxide, metal-free for the chip fabs.",
      wiki=5162703),
    R("Nitropropane", "Propane + HNO3 -> NitroPropane2 + H2O", HEAT,
      "Propane nitrated in the gas phase at 400 C (Hass, 1930s).", wiki=36130214, T=400),
    R("Diisopropylbenzene", "Cumene + Propylene -> DIPB", CAT,
      "Cumene alkylated again with propylene.", wiki=59302935, cat="AlCl3", T=80),
    R("Pentanal", "1-Butene + CO + H2 -> Pentanal", CAT,
      "1-Butene hydroformylated with a rhodium catalyst.", wiki=10289292, cat="Rh", T=100),
    R("2-Propylheptanol", "2 Pentanal + 2 H2 -> PropylHeptanol + H2O", HIGHP,
      "Pentanal's aldol dimer hydrogenated, as butanal's makes 2-ethylhexanol.", wiki=31438264, cat="Ni", T=150),
    R("Potassium Bisulfite", "KOH + SO2 -> KHSO3", MIX,
      "Sulfur dioxide absorbed in caustic potash.", wiki=13294667),
    R("Calcium Thiosulfate", "Ca(OH)2 + SO2 + S -> CaS2O3 + H2O", MIX,
      "Lime, sulfur dioxide and sulfur.", wiki=4693311),
    R("Butyric Anhydride", "2 Butyric + AceticAnhydride -> ButyricAnhydride + 2 AcOH", FLASK,
      "Butyric acid swaps partners with acetic anhydride; acetic acid is distilled off.", wiki=30240135, T=140),
    R("Butylene Oxide", "1-Butene + TBHP -> EpoxyButane + tBuOH", CAT,
      "1-Butene epoxidised by tert-butyl hydroperoxide.", wiki=59088105, cat="MoO3", T=110),
    R("Glycolonitrile", "CH2O + HCN -> Glycolonitrile", FLASK,
      "Formaldehyde and hydrogen cyanide.", wiki=27447333, T=20),
    R("Methyl Vinyl Ether", "Acetylene + Methanol -> MVE", CAT,
      "Reppe's vinylation (1930s): methanol adds to acetylene with potassium methoxide.", wiki=30624428,
      cat="KOH", T=150),
    R("1,3-Butanediol", "2 Acetaldehyde + H2 -> BDO13", CAT,
      "Acetaldehyde's aldol dimer hydrogenated over nickel.", wiki=14188289, cat="Ni", T=100),
    R("3-Picoline", "2 Acrolein + NH3 -> Picoline3 + 2 H2O", CAT,
      "Acrolein and ammonia close into a pyridine ring over silica-alumina.", wiki=17103072, cat="Alumina", T=400),
    R("Niacin", "2 Picoline3 + 3 O2 -> 2 NicotinicAcid + 2 H2O", CAT,
      "3-Picoline oxidised at its methyl group (via the nitrile, at Lonza).", wiki="Nicotinic_acid", cat="V2O5", T=350),
    R("2-Heptanone", "Acetone + Butanal + H2 -> Heptanone2 + H2O", CAT,
      "Acetone and butanal condensed, then hydrogenated over palladium.", wiki=15250836, cat="Pd", T=120),
    R("Glutaraldehyde", "Acrolein + MVE + H2O -> Glutaraldehyde + Methanol", FLASK,
      "Acrolein and methyl vinyl ether make a dihydropyran, which water opens.", wiki=192070, T=100),
    R("Triethylamine", "Diethylamine + Ethanol -> Et3N + H2O", CAT,
      "Diethylamine ethylated once more by ethanol over nickel.", wiki=1806886, cat="Ni", T=190),
    R("Triisopropanolamine", "3 PO + NH3 -> TIPA", PRESS,
      "Three propylene oxides opened by ammonia.", wiki=37431798, T=120),
    R("Phenoxyethanol", "Phenol + EO -> Phenoxyethanol", CAT,
      "Phenol opened onto ethylene oxide with a base catalyst.", wiki=5808466, cat="NaOH", T=150),
    R("Nonanal", "Octene + CO + H2 -> Nonanal", CAT,
      "1-Octene hydroformylated with a rhodium catalyst.", wiki=14575416, cat="Rh", T=100),
    R("TCPP", "3 PO + POCl3 -> TCPP", CAT,
      "Phosphorus oxychloride opens three propylene oxides.", wiki=76213261, cat="AlCl3", T=80),
    R("Sodium Isethionate", "EO + NaHSO3 -> NaIsethionate", MIX,
      "Ethylene oxide opened by sodium bisulfite.", wiki=51510868),
    R("Sodium Percarbonate", "2 SodaAsh + 3 H2O2 -> Percarbonate", MIX,
      "Soda crystallised from hydrogen peroxide solution.", wiki=388198),
    R("PACM", "MDA + 6 H2 -> PACM", HIGHP,
      "Methylenedianiline's rings hydrogenated over rhodium.", wiki=54979439, cat="Rh", T=150),
    R("Vinyltoluene", "Toluene + Ethylene -> Vinyltoluene + H2", CAT,
      "Toluene ethylated, then dehydrogenated over iron oxide.", wiki=51317436, cat="Fe3O4", T=600),
    R("Dichloroisocyanurate", "CyanuricAcid + 2 Cl2 + 3 NaOH -> NaDCC + 2 NaCl + 3 H2O", FLASK,
      "Cyanuric acid chlorinated in caustic soda.", wiki=8359810, T=20),
    R("HDI Phosgenation", "HMDA + 2 COCl2 -> HDI + 4 HCl", FLASK,
      "Hexamethylenediamine phosgenated.", wiki=4183464, T=150),
    R("Isophorone", "3 Acetone -> Isophorone + 2 H2O", CAT,
      "Three acetones condensed by caustic potash at 200 C.", wiki=9193504, cat="KOH", T=200),
    R("Isophorone Diamine", "Isophorone + HCN + NH3 + 3 H2 -> IPDA + H2O", HIGHP,
      "Hydrogen cyanide adds to isophorone; the keto-nitrile is aminated and hydrogenated over cobalt.",
      wiki=58157026, cat="Co", T=120),
    R("Isobutyric Acid", "2 Isobutyraldehyde + O2 -> 2 IsobutyricAcid", HEAT,
      "Isobutyraldehyde oxidised by air.", wiki=859006, T=50, dh=-260),
    R("TMCD", "2 IsobutyricAcid + 2 H2 -> TMCD + 2 H2O", HIGHP,
      "Isobutyric acid cracked to dimethylketene, which dimerises to a square diketone, then hydrogenated (Eastman).",
      wiki=22695288, cat="Rh", T=150),
]
E6.reactions += [
    R("HCFC-133a", "TCE + 3 HF -> HCFC133a + 2 HCl", CAT,
      "Trichloroethylene fluorinated with hydrogen fluoride.", wiki=52830815, cat="Cr2O3", T=250),
    R("HFC-134a", "HCFC133a + HF -> R134a + HCl", CAT,
      "The last chlorine swapped for fluorine over chromia at 350 C.", wiki=1735557, cat="Cr2O3", T=350),
    R("HCFC-124", "PCE + 4 HF -> HCFC124 + 3 HCl", CAT,
      "Perchloroethylene adds hydrogen fluoride and swaps three chlorines.", wiki=2711031, cat="Cr2O3", T=300),
    R("HFC-125", "HCFC124 + HF -> HFC125 + HCl", CAT,
      "The last chlorine swapped for fluorine.", wiki=30864980, cat="Cr2O3", T=350),
    R("CFC-114a", "CFC113a + HF -> CFC114a + HCl", CAT,
      "CFC-113a fluorinated once more over antimony pentachloride.", wiki=73537332, cat="SbCl5", T=100),
    R("HFC-32", "CH2Cl2 + 2 HF -> HFC32 + 2 HCl", CAT,
      "Dichloromethane fluorinated over antimony pentachloride.", wiki=1426766, cat="SbCl5", T=100),
    R("HFC-245fa", "CCl4 + VinylChloride + 5 HF -> HFC245fa + 5 HCl", HIGHP,
      "Carbon tetrachloride adds to vinyl chloride; the five chlorines are swapped for fluorine.",
      wiki=6231117, cat="SbCl5", T=120),
    R("HCFO-1233zd", "CCl4 + VinylChloride + 3 HF -> HCFO1233zd + 4 HCl", CAT,
      "The same pentachloropropane, fluorinated three times in the gas phase and dehydrochlorinated.",
      wiki=52070082, cat="Cr2O3", T=300),
]

# the next part of the list
import authored_canon_3  # noqa: E402,F401
