"""
Curieosity's industrial chemistry, part 3 (see authored_canon.py).
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E1, E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)

# --- intermediates the canon set lacks ---------------------------------------------------
S(None, "Ketene", "Ketene", "C2H2O", "Gas", "Ketene",
  "H2C=C=O, a toxic, fleeting gas made by cracking acetic acid. It is too reactive to store: it is used at once to make acetic anhydride, or dimerised to diketene.",
  smiles="C=C=O")
S(None, "Bibenzyl", "Bibenzyl", "C14H14", "Solid", "Bibenzyl",
  "Two benzyl groups joined: 1,2-diphenylethane.", smiles="c1ccc(CCc2ccccc2)cc1")
S(None, "Dodecylbenzene", "Dodecylbenzene", "C18H30", "Liquid", "Dodecylbenzene",
  "Linear alkylbenzene: benzene with a twelve-carbon tail, made only to be sulfonated into detergent.",
  smiles="CCCCCCCCCCCCc1ccccc1")
S(None, "mDNB", "1,3-Dinitrobenzene", "C6H4N2O4", "Solid", "1,3-Dinitrobenzene",
  "Benzene nitrated twice: the second nitro group goes meta to the first.", smiles="O=[N+]([O-])c1cccc(c1)[N+](=O)[O-]")
S(None, "Hexanediol", "1,6-Hexanediol", "C6H14O2", "Solid", "1,6-Hexanediol",
  "A six-carbon diol for polyurethanes, polyesters and acrylate monomers.", smiles="OCCCCCCO")

# --- the canon substances ------------------------------------------------------------------
S("421-73-8", "HCFC244bb", "2-Chloro-1,1,1,2-tetrafluoropropane", "C3H3ClF4", "Liquid", 12328746,
  "HCFC-244bb, made only as the last step before the car refrigerant HFO-1234yf.",
  lib=5794)
S("754-12-1", "HFO1234yf", "2,3,3,3-Tetrafluoropropene", "C3H2F4", "Gas", 21292036,
  "HFO-1234yf, the refrigerant of new car air conditioners since 2017: it breaks down in the air within days, with almost no warming effect.",
  lib=7935)
S("5064-31-3", "Na3NTA", "Trisodium nitrilotriacetate", "C6H6NNa3O6", "Solid", 4497595,
  "NTA, a chelating agent that replaced phosphates in some detergents: it grips calcium and magnesium so they can't spoil the wash.",
  lib=6099)
S("5124-30-1", "HMDI", "Hydrogenated MDI", "C15H22N2O2", "Liquid", 66422842,
  "MDI with both rings hydrogenated: polyurethanes from it never yellow in sunlight.",
  lib=3889)
S("540-88-5", "tBuOAc", "tert-Butyl acetate", "C6H12O2", "Liquid", 3756616,
  "A solvent for coatings and inks exempt from smog rules in the US, because it barely forms ozone.",
  lib=6376)
S("616-45-5", "Pyrrolidone", "2-Pyrrolidone", "C4H7NO", "Liquid", 3877183,
  "The simplest lactam with a five-membered ring, the start of N-vinylpyrrolidone and the drug piracetam.",
  lib=6906)
S("674-82-8", "Diketene", "Diketene", "C4H4O2", "Liquid", 14708522,
  "Ketene dimerised: the start of acetoacetates for pigments, of the sweetener acesulfame, and of many drugs and pesticides.",
  lib=7304)
S("68541-50-4", "TMP", "Trimethylolpropane", "C6H14O3", "Solid", 20969787,
  "Three alcohol groups on one branch point: the crosslinker of alkyd resins, polyurethanes and acrylate inks.",
  smiles="CCC(CO)(CO)CO")
S("732-26-3", "TTBP", "2,4,6-Tri-tert-butylphenol", "C18H30O", "Solid", 53080100,
  "Phenol crowded on every side with tert-butyl groups: an antioxidant for fuels and lubricants.",
  lib=7787)
S("75-35-4", "VDC", "Vinylidene chloride", "C2H2Cl2", "Liquid", 4027782,
  "The monomer of Saran (Dow, 1940s): its film keeps oxygen and smells in better than any other plastic.",
  lib=7895, props=("IsMonomer",))
S("75-37-6", "HFC152a", "1,1-Difluoroethane", "C2H4F2", "Gas", 1777994,
  "HFC-152a, the propellant of keyboard 'air dusters', and the start of vinyl fluoride.",
  lib=7897)
S("75-54-7", "MeSiHCl2", "Methyldichlorosilane", "CH4Cl2Si", "Liquid", 2477685,
  "A silane with a silicon-hydrogen bond, the basis of silicone fluids that cure on contact and waterproof fabrics.",
  lib=7905)
S("75-68-3", "HCFC142b", "1-Chloro-1,1-difluoroethane", "C2H3ClF2", "Gas", 31899711,
  "HCFC-142b, cracked to vinylidene fluoride, the monomer of the fluoropolymer PVDF.",
  lib=7914)
S("7727-54-0", "APS", "Ammonium persulfate", "(NH4)2S2O8", "Solid", 2088194,
  "A strong oxidiser: it starts the polymerisation of latex rubbers and acrylics, etches copper off circuit boards, and bleaches hair.",
  smiles="[NH4+].[NH4+].[O-]S(=O)(=O)OOS([O-])(=O)=O")
S("7775-27-1", "Na2S2O8", "Sodium persulfate", "Na2S2O8", "Solid", 5064160,
  "A persulfate for etching circuit boards, starting polymerisations and soil remediation.",
  lib=8120)
S("7790-94-5", "HSO3Cl", "Chlorosulfonic acid", "HSO3Cl", "Liquid", 4368850,
  "A fuming, violent liquid that sulfonates anything aromatic: the start of saccharin and the sulfa drugs.",
  lib=8165, props=("IsAcid",))
S("78-10-4", "TEOS", "Tetraethyl orthosilicate", "C8H20O4Si", "Liquid", 10942079,
  "Silicon with four ethoxy groups: water turns it into silica, the sol-gel route to aerogels and the insulating layers of chips.",
  lib=8172)
S("78-92-2", "Butanol2", "2-Butanol", "C4H10O", "Liquid", 1704762,
  "sec-Butanol, made from butenes and nearly all dehydrogenated to methyl ethyl ketone.",
  lib=8200)
S("79-29-8", "DMB23", "2,3-Dimethylbutane", "C6H14", "Liquid", 17562889,
  "A compact, high-octane hexane made by alkylating isobutane with ethylene.",
  lib=8232)
S("79-94-7", "TBBPA", "Tetrabromobisphenol A", "C15H12Br4O2", "Solid", 11855137,
  "The most used brominated flame retardant, built into the epoxy of almost every circuit board.",
  lib=8249)
S("80-07-9", "DCDPS", "4,4'-Dichlorodiphenyl sulfone", "C12H8Cl2O2S", "Solid", 15978248,
  "The monomer of the polysulfone plastics, clear and tough enough for baby bottles and kidney-dialysis membranes.",
  lib=8269)
S("84852-53-9", "DBDPE", "Decabromodiphenylethane", "C14H4Br10", "Solid", 72692264,
  "A flame retardant that replaced decabromodiphenyl ether in electronics housings.",
  lib=8455)
S("88-12-0", "NVP", "N-Vinylpyrrolidone", "C6H9NO", "Liquid", 18967796,
  "The monomer of polyvinylpyrrolidone (Reppe, 1930s): the binder of tablets, the film of hairspray, and a wartime blood-plasma substitute.",
  lib=8562, props=("IsMonomer",))
S("88-18-6", "TBP2", "2-tert-Butylphenol", "C10H14O", "Liquid", 69479896,
  "Phenol with one tert-butyl group beside the OH, on the way to antioxidants and fragrances.",
  lib=8563)
S("98-54-4", "TBP4", "4-tert-Butylphenol", "C10H14O", "Solid", 67408322,
  "A chain stopper for polycarbonate and the phenol of tough, oil-soluble phenolic resins.",
  lib=8922)
S("96-76-4", "DTBP24", "2,4-Di-tert-butylphenol", "C14H22O", "Solid", 77763081,
  "Esterified with phosphorus trichloride it becomes Irgafos 168, the phosphite stabiliser in almost every polyolefin.",
  smiles="CC(C)(C)c1ccc(O)c(c1)C(C)(C)C")
S("97-88-1", "BMA", "Butyl methacrylate", "C8H14O2", "Liquid", 61698382,
  "A methacrylate ester that softens acrylic coatings and dental resins.",
  lib=8897)
S("3048-64-4", "VNB", "5-Vinyl-2-norbornene", "C9H12", "Liquid", 56163880,
  "Butadiene and cyclopentadiene's Diels-Alder adduct, isomerised to ethylidene norbornene for EPDM rubber.",
  lib=5199)
S("13918-37-1", "Fayalite", "Fayalite", "Fe2SiO4", "Solid", 1245859,
  "Iron silicate, the glassy black slag of the bloomery. Ancient smelters threw away nearly half their iron in it.",
  lib=3578)
S("101-02-0", "TPPite", "Triphenyl phosphite", "C18H15O3P", "Liquid", 12937605,
  "A stabiliser for PVC and other plastics, mopping up the peroxides that start their decay.",
  lib=2097)
S("10294-56-1", "H3PO3", "Phosphorous acid", "H3PO3", "Solid", 1966205,
  "Phosphorus acid with one oxygen fewer than phosphoric: the start of the phosphonate water-treatment chemicals and of fungicides.",
  lib=2214, props=("IsAcid",))
S("103-23-1", "DEHA", "Bis(2-ethylhexyl) adipate", "C22H42O4", "Liquid", 30856584,
  "The plasticiser that keeps PVC cling film soft.",
  lib=2221)
S("104-15-4", "pTsOH", "p-Toluenesulfonic acid", "C7H8O3S", "Solid", 5207969,
  "A strong acid that dissolves in organic solvents: the organic chemist's solid sulfuric acid.",
  lib=2274, props=("IsAcid",))
S("107-22-2", "Glyoxal", "Glyoxal", "C2H2O2", "Liquid", 3200095,
  "The smallest dialdehyde: it crosslinks cotton for permanent-press shirts and strengthens paper.",
  lib=2447)
S("107-41-5", "HexyleneGlycol", "Hexylene glycol", "C6H14O2", "Liquid", 27383541,
  "A diol solvent for hydraulic fluids, inks and cosmetics.",
  lib=2453)
S("108-32-7", "PropyleneCarbonate", "Propylene carbonate", "C4H6O3", "Liquid", 5617916,
  "A polar, high-boiling solvent from propylene oxide and carbon dioxide, used in lithium battery electrolytes.",
  lib=2513)
S("108-45-2", "MPD", "m-Phenylenediamine", "C6H8N2", "Solid", 3068087,
  "The amine of Nomex fibre and of the reverse-osmosis membranes that desalinate seawater.",
  lib=2516)
S("108-74-7", "TMTriazine", "1,3,5-Trimethylhexahydro-1,3,5-triazine", "C6H15N3", "Liquid", 51222940,
  "Methylamine and formaldehyde in a ring: a biocide that slowly releases formaldehyde.",
  lib=2525)
S("108-91-8", "Cyclohexylamine", "Cyclohexylamine", "C6H13N", "Liquid", 8290478,
  "A corrosion inhibitor for boiler steam, and the start of the sweetener cyclamate and rubber accelerators.",
  lib=2535)
S("110-30-5", "EBS", "Ethylene bis(stearamide)", "C38H76N2O2", "Solid", "Ethylene_bis(stearamide)",
  "A wax that helps plastics flow and keeps them from sticking to moulds.",
  lib=2594)
S("110-85-0", "Piperazine", "Piperazine", "C4H10N2", "Solid", 1455098,
  "A six-membered ring with two nitrogens: a dewormer since 1953, and a building block of drugs such as Viagra and ciprofloxacin.",
  lib=2608)
S("111-92-2", "Dibutylamine", "Dibutylamine", "C8H19N", "Liquid", 25183424,
  "An amine for rubber accelerators, corrosion inhibitors and flotation agents.",
  lib=2658)
S("124-68-5", "AMP", "2-Amino-2-methyl-1-propanol", "C4H11NO", "Solid", 41098559,
  "A hindered amine for capturing carbon dioxide, and a pH buffer for paints and cosmetics.",
  lib=3114)
S("126-33-0", "Sulfolane", "Sulfolane", "C4H8O2S", "Liquid", 3835271,
  "A polar solvent (Shell, 1960s) that pulls benzene, toluene and xylenes out of reformed petrol.",
  lib=3157)
S("13048-33-4", "HDDA", "1,6-Hexanediol diacrylate", "C12H18O4", "Liquid", 63095268,
  "A diacrylate that crosslinks in a flash under UV light: inks, varnishes and nail gels that cure in seconds.",
  lib=3273)
S("131-11-3", "DimethylPhthalate", "Dimethyl phthalate", "C10H10O4", "Liquid", 5421735,
  "An insect repellent of the Second World War, and a plasticiser for cellulose acetate.",
  lib=3293)
S("1314-80-3", "P4S10", "Phosphorus pentasulfide", "P4S10", "Solid", 3157369,
  "The start of the zinc dithiophosphates in motor oil and of organophosphate insecticides.",
  lib=3322)
S("25340-17-4", "DEB", "Diethylbenzene", "C10H14", "Liquid", 50846884,
  "Ethylbenzene ethylated once more, dehydrogenated to divinylbenzene.",
  lib=4766)
S("1321-74-0", "DVB", "Divinylbenzene", "C10H10", "Liquid", 8087667,
  "Copolymerised with styrene, it ties the chains together: the crosslinked beads of ion-exchange resins.",
  lib=3341, props=("IsMonomer",))
S("1332-07-6", "ZincBorate", "Zinc borate", "Zn2B6O11·5H2O", "Solid", 26092288,
  "A flame retardant and smoke suppressant for plastics and rubber, and a fungicide for wood composites.",
  lib=3386)
S("1338-39-2", "Span20", "Sorbitan monolaurate", "C18H34O6", "Liquid", 39940098,
  "Span 20, a sorbitol emulsifier from coconut lauric acid, for foods, cosmetics and drugs.",
  lib=3401)
S("141-02-6", "DEHM", "Bis(2-ethylhexyl) maleate", "C20H36O4", "Liquid", 58203640,
  "Sulfonated, it becomes docusate, the wetting agent and stool softener.",
  lib=3644)
S("143-28-2", "OleylAlcohol", "Oleyl alcohol", "C18H36O", "Liquid", 1590018,
  "An unsaturated fatty alcohol, a softener and emulsifier in creams and hair conditioners.",
  lib=3686)
S("15214-89-8", "AMPS", "2-Acrylamido-2-methylpropanesulfonic acid", "C7H13NO4S", "Solid", 22439870,
  "AMPS (Lubrizol): a sulfonic acid monomer whose polymers resist salt and hard water in oil wells, water treatment and hydrogels.",
  lib=3859)
S("15625-89-5", "TMPTA", "Trimethylolpropane triacrylate", "C15H20O6", "Liquid", 3028468,
  "Three acrylates on one core: UV-cured inks, coatings and the resins of 3D printing.",
  lib=3931)
S("1675-54-3", "BADGE", "Bisphenol A diglycidyl ether", "C21H24O4", "Liquid", 24884697,
  "The liquid epoxy resin: mixed with an amine hardener, it sets into glue, coatings and composite matrix.",
  lib=4065)
S("1704-62-7", "DMAEE", "2-(2-Dimethylaminoethoxy)ethanol", "C6H15NO2", "Liquid", 75501216,
  "A catalyst that makes polyurethane foam rise and set.",
  lib=4092)
S("203743-03-7", "HEMA", "2-Hydroxyethyl methacrylate", "C6H10O3", "Liquid", 9806334,
  "The monomer of soft contact lenses (Wichterle, Prague, 1961): its polymer swells with water into a clear gel.",
  lib=8515, props=("IsMonomer",))
S("25155-30-0", "SDBS", "Sodium dodecylbenzenesulfonate", "C18H29NaO3S", "Solid", "Sodium_dodecylbenzenesulfonate",
  "The workhorse detergent: linear alkylbenzene sulfonate, the biodegradable surfactant that replaced the foaming branched kind in the 1960s.",
  lib=4734)

E1.reactions += [
    R("Bloomery Slag", "2 FeO + Sand -> Fayalite", SMELT,
      "Iron oxide fluxes the sand in the ore into a runny slag, which the smith taps off.", wiki=1245859, T=1200),
]
E3.reactions += [
    R("Ethyl Silicate", "SiCl4 + 4 Ethanol -> TEOS + 4 HCl", FLASK,
      "Silicon tetrachloride and ethanol (Ebelmen, 1846).", wiki=10942079, T=40),
    R("Phosphorous Acid", "PCl3 + 3 H2O -> H3PO3 + 3 HCl", MIX,
      "Phosphorus trichloride hydrolysed.", wiki=1966205, dh=-300),
    R("Phosphorus Pentasulfide", "P4 + 10 S -> P4S10", HEAT,
      "White phosphorus and sulfur fused together (Berzelius).", wiki=3157369, T=300),
]
E4.reactions += [
    R("Chlorosulfonic Acid", "SO3 + HCl -> HSO3Cl", MIX,
      "Sulfur trioxide and dry hydrogen chloride.", wiki=4368850),
    R("p-Toluenesulfonic Acid", "Toluene + H2SO4 -> pTsOH + H2O", HEAT,
      "Toluene sulfonated with hot sulfuric acid.", wiki=5207969, T=110),
    R("Triphenyl Phosphite", "PCl3 + 3 Phenol -> TPPite + 3 HCl", FLASK,
      "Phosphorus trichloride esterified with phenol.", wiki=12937605, T=150),
    R("m-Dinitrobenzene", "Nitrobenzene + HNO3 -> mDNB + H2O", FLASK,
      "Nitrobenzene nitrated again, in hotter mixed acid.", wiki="1,3-Dinitrobenzene", T=90),
    R("m-Phenylenediamine", "mDNB + 6 H2 -> MPD + 4 H2O", CAT,
      "Dinitrobenzene hydrogenated over nickel.", wiki=3068087, cat="Ni", T=100),
    R("Tetrabromobisphenol A", "BPA + 4 Br2 -> TBBPA + 4 HBr", MIX,
      "Bisphenol A brominated in methanol.", wiki=11855137),
    R("Dimethyl Phthalate", "PhthalicAnhydride + 2 Methanol -> DimethylPhthalate + H2O", CAT,
      "Phthalic anhydride esterified with methanol.", wiki=5421735, cat="H2SO4", T=150),
]
E5.reactions += [
    R("Ketene", "AcOH -> Ketene + H2O", HEAT,
      "Acetic acid cracked at 750 C with a trace of triethyl phosphate (Wacker).", wiki="Ketene", T=750, dh=147),
    R("Diketene", "2 Ketene -> Diketene", COOL,
      "Ketene dimerises as it is cooled.", wiki=14708522, T=10),
    R("Bibenzyl", "2 Benzene + EDC -> Bibenzyl + 2 HCl", CAT,
      "Benzene alkylated twice by ethylene dichloride (Friedel-Crafts).", wiki="Bibenzyl", cat="AlCl3", T=60),
    R("Decabromodiphenylethane", "Bibenzyl + 10 Br2 -> DBDPE + 10 HBr", FLASK,
      "Every ring hydrogen of bibenzyl swapped for bromine.", wiki=72692264, T=50),
    R("Alkylbenzene", "Benzene + Dodecene -> Dodecylbenzene", CAT,
      "Benzene alkylated with dodecene over hydrogen fluoride.", wiki="Dodecylbenzene", cat="HF", T=50),
    R("Alkylbenzene Sulfonate", "Dodecylbenzene + SO3 + NaOH -> SDBS + H2O", FLASK,
      "Sulfonated with sulfur trioxide in a falling film, then neutralised.", wiki="Sodium_dodecylbenzenesulfonate", T=50),
    R("1,6-Hexanediol", "Adipic + 4 H2 -> Hexanediol + 2 H2O", HIGHP,
      "Adipic acid hydrogenated over copper.", wiki="1,6-Hexanediol", cat="Cu", T=250),
    R("Nitrilotriacetate", "3 Glycolonitrile + 3 NaOH -> Na3NTA + 2 NH3", FLASK,
      "Ammonia joins three glycolonitriles into one amine; caustic soda turns the nitriles into carboxylates and frees their nitrogen as ammonia, so on balance two ammonia come out.",
      wiki=4497595, T=100),
    R("HMDI Phosgenation", "PACM + 2 COCl2 -> HMDI + 4 HCl", FLASK,
      "PACM phosgenated.", wiki=66422842, T=150),
    R("tert-Butyl Acetate", "Isobutylene + AcOH -> tBuOAc", CAT,
      "Acetic acid adds to isobutylene over an acid catalyst.", wiki=3756616, cat="H2SO4", T=20),
    R("2-Pyrrolidone", "GBL + NH3 -> Pyrrolidone + H2O", PRESS,
      "gamma-Butyrolactone heated with ammonia.", wiki=3877183, T=250),
    R("N-Vinylpyrrolidone", "Pyrrolidone + Acetylene -> NVP", CAT,
      "Reppe vinylation of 2-pyrrolidone with acetylene and potassium hydroxide.", wiki=18967796,
      cat="KOH", T=150),
    R("Trimethylolpropane", "Butanal + 3 CH2O + NaOH -> TMP + HCOONa", FLASK,
      "Butanal takes two formaldehydes; a third reduces it.", wiki=20969787, T=50),
    R("TMPTA", "TMP + 3 AcrylicAcid -> TMPTA + 3 H2O", CAT,
      "Trimethylolpropane esterified with acrylic acid.", wiki=3028468, cat="pTsOH", T=90),
    R("Ortho tert-Butylphenol", "Phenol + Isobutylene -> TBP2", PRESS,
      "Isobutylene under pressure with aluminium phenoxide goes to the ortho position.", wiki=69479896, T=100),
    R("Para tert-Butylphenol", "Phenol + Isobutylene -> TBP4", FLASK,
      "Isobutylene with an acid resin goes to the para position.", wiki=67408322, T=80),
    R("2,4-Di-tert-butylphenol", "TBP4 + Isobutylene -> DTBP24", CAT,
      "A second tert-butyl goes beside the OH.", wiki=77763081, cat="H2SO4", T=80),
    R("Tri-tert-butylphenol", "DTBP24 + Isobutylene -> TTBP", CAT,
      "A third, filling both ortho positions.", wiki=53080100, cat="AlCl3", T=80),
    R("Vinylidene Chloride", "TCE112 + NaOH -> VDC + NaCl + H2O", FLASK,
      "1,1,2-Trichloroethane stripped of hydrogen chloride by caustic soda.", wiki=4027782, T=90),
    R("HFC-152a", "Acetylene + 2 HF -> HFC152a", CAT,
      "Hydrogen fluoride adds twice to acetylene.", wiki=1777994, cat="SbCl5", T=50),
    R("Methyldichlorosilane", "Si + CH3Cl + HCl -> MeSiHCl2", CAT,
      "The direct process with hydrogen chloride added to the methyl chloride.", wiki=2477685, cat="Cu", T=300),
    R("HCFC-142b", "TCA111 + 2 HF -> HCFC142b + 2 HCl", CAT,
      "Methyl chloroform fluorinated twice.", wiki=31899711, cat="SbCl5", T=100),
    R("Ammonium Persulfate", "NH42SO4 + H2SO4 -> APS + H2", ECELL,
      "Ammonium bisulfate solution electrolysed at a platinum anode.", wiki=2088194),
    R("Sodium Persulfate", "APS + 2 NaOH -> Na2S2O8 + 2 NH3 + 2 H2O", MIX,
      "Ammonium persulfate swapped for sodium with caustic soda.", wiki=5064160),
    R("2-Butanol", "2-Butene + H2O -> Butanol2", CAT,
      "2-Butene hydrated in sulfuric acid.", wiki=1704762, cat="H2SO4", T=60),
    R("2,3-Dimethylbutane", "Isobutane + Ethylene -> DMB23", CAT,
      "Isobutane alkylated with ethylene over aluminium chloride.", wiki=17562889, cat="AlCl3", T=50),
    R("Dichlorodiphenyl Sulfone", "2 Chlorobenzene + SO3 -> DCDPS + H2O", FLASK,
      "Chlorobenzene sulfonated, and the sulfonic acid joins a second chlorobenzene.", wiki=15978248, T=200),
    R("Butyl Methacrylate", "MethacrylicAcid + Butanol -> BMA + H2O", CAT,
      "Methacrylic acid esterified with butanol.", wiki=61698382, cat="H2SO4", T=100),
    R("Vinylnorbornene", "Cyclopentadiene + Butadiene -> VNB", PRESS,
      "Cyclopentadiene and butadiene heated together: a Diels-Alder reaction.", wiki=56163880, T=150),
    R("Bis(2-ethylhexyl) Adipate", "Adipic + 2 2EH -> DEHA + 2 H2O", CAT,
      "Adipic acid esterified with 2-ethylhexanol.", wiki=30856584, cat="H2SO4", T=180),
    R("Glyoxal", "EG + O2 -> Glyoxal + 2 H2O", CAT,
      "Ethylene glycol oxidised over silver.", wiki=3200095, cat="Ag", T=550),
    R("Hexylene Glycol", "DiacetoneAlcohol + H2 -> HexyleneGlycol", HIGHP,
      "Diacetone alcohol hydrogenated over nickel.", wiki=27383541, cat="Ni", T=120),
    R("Propylene Carbonate", "PO + CO2 -> PropyleneCarbonate", CAT,
      "Carbon dioxide adds to propylene oxide, with a quaternary ammonium salt as catalyst.", wiki=5617916,
      cat="TMACl", T=150),
    R("Trimethyltriazine", "3 Methylamine + 3 CH2O -> TMTriazine + 3 H2O", MIX,
      "Methylamine and formaldehyde close into a ring.", wiki=51222940),
    R("Cyclohexylamine", "Aniline + 3 H2 -> Cyclohexylamine", CAT,
      "Aniline's ring hydrogenated over cobalt.", wiki=8290478, cat="Co", T=200),
    R("Ethylene Bis-Stearamide", "2 StearicAcid + EDA -> EBS + 2 H2O", HEAT,
      "Stearic acid heated with ethylenediamine.", wiki="Ethylene_bis(stearamide)", T=200),
    R("Piperazine", "2 MEA -> Piperazine + 2 H2O", CAT,
      "Ethanolamine cyclised over nickel; piperazine also falls out of making ethyleneamines.", wiki=1455098,
      cat="Ni", T=200),
    R("Dibutylamine", "2 Butanol + NH3 -> Dibutylamine + 2 H2O", CAT,
      "Butanol aminated with ammonia over nickel.", wiki=25183424, cat="Ni", T=200),
    R("Aminomethylpropanol", "NitroPropane2 + CH2O + 3 H2 -> AMP + 2 H2O", CAT,
      "2-Nitropropane takes a formaldehyde; the nitro group is hydrogenated to an amine.", wiki=41098559,
      cat="Ni", T=80),
    R("Sulfolane", "Butadiene + SO2 + H2 -> Sulfolane", CAT,
      "Butadiene and sulfur dioxide make sulfolene, which is hydrogenated over nickel.", wiki=3835271,
      cat="Ni", T=60),
    R("Hexanediol Diacrylate", "Hexanediol + 2 AcrylicAcid -> HDDA + 2 H2O", CAT,
      "1,6-Hexanediol esterified with acrylic acid.", wiki=63095268, cat="pTsOH", T=90),
    R("Diethylbenzene", "Ethylbenzene + Ethylene -> DEB", CAT,
      "Ethylbenzene ethylated again.", wiki=50846884, cat="AlCl3", T=90),
    R("Divinylbenzene", "DEB -> DVB + 2 H2", CAT,
      "Diethylbenzene dehydrogenated over iron oxide.", wiki=8087667, cat="Fe3O4", T=600),
    R("Zinc Borate", "2 ZnO + 6 H3BO3 -> ZincBorate + 4 H2O", MIX,
      "Zinc oxide stirred into hot boric acid solution.", wiki=26092288),
    R("Span 20", "Sorbitol + LauricAcid -> Span20 + 2 H2O", CAT,
      "Sorbitol closes into sorbitan and is esterified with lauric acid.", wiki=39940098, cat="NaOH", T=210),
    R("Bis(2-ethylhexyl) Maleate", "MaleicAnhydride + 2 2EH -> DEHM + H2O", CAT,
      "Maleic anhydride esterified with 2-ethylhexanol.", wiki=58203640, cat="H2SO4", T=150),
    R("Oleyl Alcohol", "OleicAcid + 2 H2 -> OleylAlcohol + H2O", HIGHP,
      "Oleic acid hydrogenated over zinc chromite, which spares the double bond.", wiki=1590018, cat="ZnO", T=300),
    R("AMPS", "Acrylonitrile + Isobutylene + SO3 + H2O -> AMPS", FLASK,
      "A Ritter reaction: acrylonitrile, isobutylene and oleum (Lubrizol).", wiki=22439870, T=40),
    R("Liquid Epoxy Resin", "BPA + 2 Epichlorohydrin + 2 NaOH -> BADGE + 2 NaCl + 2 H2O", FLASK,
      "Bisphenol A joined to two epichlorohydrins, the ring closed again by caustic soda.", wiki=24884697, T=80),
    R("Dimethylaminoethoxyethanol", "DMAE + EO -> DMAEE", PRESS,
      "A second ethylene oxide on dimethylaminoethanol.", wiki=75501216, T=110),
    R("HEMA", "MethacrylicAcid + EO -> HEMA", CAT,
      "Ethylene oxide opened by methacrylic acid.", wiki=9806334, cat="FeCl3", T=80),
]
E6.reactions += [
    R("HCFC-244bb", "CCl4 + Ethylene + Cl2 + 4 HF -> HCFC244bb + 5 HCl", CAT,
      "Carbon tetrachloride adds to ethylene; chlorinated and fluorinated in steps, it ends as 244bb.",
      wiki=12328746, cat="SbCl5", T=100),
    R("HFO-1234yf", "HCFC244bb -> HFO1234yf + HCl", CAT,
      "Hydrogen chloride stripped off at 450 C (Honeywell and DuPont, 2010s).", wiki=21292036,
      cat="Charcoal", T=450),
]

import authored_canon_4  # noqa: E402,F401
