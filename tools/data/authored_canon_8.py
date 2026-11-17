"""
Curieosity's industrial chemistry, part 8 (see authored_canon.py).
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E1, E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)


# --- intermediates the canon set lacks ---------------------------------------------------
S(None, "Durene", "Durene", "C10H14", "Solid", "Durene",
  "1,2,4,5-Tetramethylbenzene, an oddly high-melting aromatic, oxidised to pyromellitic dianhydride for Kapton.",
  smiles="Cc1cc(C)c(C)cc1C")

# --- the canon substances ------------------------------------------------------------------
S("149-44-0", "Rongalite", "Rongalite", "CH3NaO3S", "Solid", 4932031,
  "Sodium formaldehyde sulfoxylate: the reducing agent of textile discharge printing and of redox-started rubber polymerisation.", lib=3801)
S("150-76-5", "MEHQ", "4-Methoxyphenol", "C7H8O2", "Solid", 12938750,
  "MEHQ, the few parts per million that keep acrylic monomers from polymerising in the drum.", lib=3827)
S("15520-10-2", "MPMD", "2-Methylpentamethylenediamine", "C6H16N2", "Liquid", 67327667,
  "Dytek A, made from nylon's by-product methylglutaronitrile, for epoxy hardeners and special nylons.", lib=3905)
S("15827-60-8", "DTPMP", "DTPMP", "C9H28N3O15P5", "Solid", 22759975,
  "Diethylenetriamine penta(methylenephosphonic acid), a scale inhibitor and peroxide stabiliser.", lib=3953)
S("164462-16-2", "Na3MGDA", "Trisodium methylglycinediacetate", "C7H8NNa3O6", "Solid", 60029651,
  "MGDA (BASF's Trilon M), a readily biodegradable chelant that replaced phosphates in dishwasher tablets.", lib=4032)
S("17557-23-2", "NPGDGE", "Neopentyl glycol diglycidyl ether", "C11H20O4", "Liquid", 70423946,
  "A reactive diluent that thins epoxy resin without leaving solvent behind.", lib=4145)
S("2226-96-2", "Tempol", "Tempol", "C9H18NO2", "Solid", 32122780,
  "A stable nitroxide radical: a polymerisation inhibitor for monomer plants.", lib=4512)
S("2425-79-8", "BDDGE", "1,4-Butanediol diglycidyl ether", "C10H18O4", "Liquid", 70452100,
  "A reactive diluent for epoxy resins and a crosslinker of hyaluronic acid fillers.", lib=4635)
S("280-57-9", "DABCO", "DABCO", "C6H12N2", "Solid", 1777049,
  "1,4-Diazabicyclo[2.2.2]octane, the cage-shaped amine that catalyses polyurethane foam.", lib=5024)
S("287-92-3", "Cyclopentane", "Cyclopentane", "C5H10", "Liquid", 1478144,
  "The blowing agent in the insulating foam of most refrigerators since the 1990s ozone-layer phase-outs.", lib=5057)
S("288-88-0", "Triazole124", "1,2,4-Triazole", "C2H3N3", "Solid", 3054679,
  "The ring at the heart of the triazole fungicides and antifungal drugs such as fluconazole.", lib=5070)
S("298-07-7", "D2EHPA", "Di(2-ethylhexyl)phosphoric acid", "C16H35O4P", "Liquid", 31605902,
  "D2EHPA, the solvent-extraction reagent that separates rare earths and recovers uranium from ore leach.", lib=5131)
S("3033-62-3", "BDMAEE", "Bis(2-dimethylaminoethyl) ether", "C8H20N2O", "Liquid", 13007260,
  "The classic blowing catalyst of flexible polyurethane foam.", lib=5186)
S("3039-83-6", "NaVS", "Sodium vinylsulfonate", "C2H3NaO3S", "Aqueous", 42343006,
  "A sulfonate monomer for electroplating, ion-exchange membranes and acrylic fibres.", lib=5190)
S("306-83-2", "HCFC123", "2,2-Dichloro-1,1,1-trifluoroethane", "C2HCl2F3", "Liquid", 5716871,
  "HCFC-123, a refrigerant for large chillers and a clean fire-extinguishing agent, phasing out under the Montreal Protocol.", lib=5213)
S("31566-31-1", "Monostearin", "Glycerol monostearate", "C21H42O4", "Solid", 18929417,
  "E471, the emulsifier that keeps bread soft and ice cream smooth.", lib=5270)
S("4109-96-0", "H2SiCl2", "Dichlorosilane", "H2Cl2Si", "Gas", 9563449,
  "A silicon gas for depositing silicon nitride and epitaxial silicon films in chip fabs.", lib=5752)
S("461-58-5", "DCD", "Dicyandiamide", "C2H4N4", "Solid", 12251858,
  "Cyanamide dimerised: an epoxy hardener, the start of melamine and of metformin, and a fertiliser nitrification inhibitor.", lib=5908)
S("502-44-3", "Caprolactone", "epsilon-Caprolactone", "C6H10O2", "Liquid", 4151704,
  "The ring-opened monomer of polycaprolactone, a biodegradable plastic for sutures and hand-mouldable plastic pellets.", lib=6070)
S("546-68-9", "TiOiPr4", "Titanium isopropoxide", "C12H28O4Ti", "Liquid", 9564261,
  "The catalyst of the Sharpless epoxidation and of polyester making, and a sol-gel route to titanium dioxide.", lib=6424)
S("603-35-0", "PPh3", "Triphenylphosphine", "C18H15P", "Solid", 1798259,
  "The ligand of Wilkinson's catalyst and rhodium hydroformylation, and the reagent of the Wittig reaction.", lib=6843)
S("614-45-9", "TBPB", "tert-Butyl peroxybenzoate", "C11H14O3", "Liquid", 52311322,
  "A peroxide initiator that cures polyester moulding compounds and makes low-density polyethylene.", lib=6897)
S("627-83-8", "EGDS", "Glycol distearate", "C38H74O4", "Solid", 20921109,
  "The pearliser of shampoos and body washes: its flat crystals shimmer in the liquid.", lib=6991)
S("629-25-4", "NaLaurate", "Sodium laurate", "C12H23NaO2", "Solid", 33042280,
  "The coconut soap: it lathers well even in cold and salty water.", lib=7004)
S("64-67-5", "DES", "Diethyl sulfate", "C4H10O4S", "Liquid", 2348001,
  "A strong ethylating agent for dyes and drugs, and the intermediate of the old sulfuric acid route to ethanol.", lib=7085)
S("68-11-1", "TGA", "Thioglycolic acid", "C2H4O2S", "Liquid", 2131951,
  "The active ingredient of permanent waves and of depilatory creams: it breaks the disulfide bonds of keratin.", lib=7365)
S("693-23-2", "DDDA", "Dodecanedioic acid", "C12H22O4", "Solid", 23975641,
  "A twelve-carbon diacid for nylon 6,12 (toothbrush bristles) and powder coatings.", lib=7618)
S("7173-62-8", "OleylPDA", "N-Oleyl-1,3-propanediamine", "C21H44N2", "Liquid", 52678570,
  "A fatty diamine for asphalt emulsions and corrosion inhibitors.", lib=7716)
S("75-76-3", "TMSi", "Tetramethylsilane", "C4H12Si", "Liquid", 1948276,
  "TMS, the zero point of NMR spectroscopy: every chemical shift is measured from its single sharp peak.", lib=7917)
S("77-90-7", "ATBC", "Acetyl tributyl citrate", "C20H34O8", "Liquid", 21589446,
  "A plasticiser for toys and food films made from citric acid, replacing phthalates.", lib=8071)
S("77-93-0", "TEC", "Triethyl citrate", "C12H20O7", "Liquid", 17076391,
  "E1505: a plasticiser for pill coatings and a foam stabiliser in egg whites.", smiles="O=C(OCC)CC(O)(C(=O)OCC)CC(=O)OCC")
S("7722-88-5", "SAPP", "Disodium pyrophosphate", "Na2H2P2O7", "Solid", 8899136,
  "Sodium acid pyrophosphate, the slow-acting leavening acid of baking powder and the antioxidant of chips.", lib=8101)
S("78-40-0", "TEP", "Triethyl phosphate", "C6H15O4P", "Liquid", 2852688,
  "A flame retardant, plasticiser and solvent, and the catalyst for making ketene.", lib=8179)
S("78-67-1", "AIBN", "Azobisisobutyronitrile", "C8H12N4", "Solid", 2231865,
  "AIBN, the radical initiator of the lab, which falls apart on warming into nitrogen and two carbon radicals.", lib=8187)
S("80-09-1", "BPS", "Bisphenol S", "C12H10O4S", "Solid", 15996046,
  "BPA's sulfone cousin, used in thermal receipt paper and polyethersulfone; it turns out to be hormonally active too.", lib=8271)
S("826-62-0", "NadicAnhydride", "Nadic anhydride", "C9H8O3", "Solid", 72797661,
  "Cyclopentadiene and maleic anhydride's adduct: an epoxy hardener and the end-cap of high-temperature polyimides.", lib=8375)
S("89-32-7", "PMDA", "Pyromellitic dianhydride", "C10H2O6", "Solid", 43338421,
  "The dianhydride of Kapton polyimide (DuPont, 1960s), which flew on the Apollo spacecraft.", lib=8597)
S("94-36-0", "BPO", "Benzoyl peroxide", "C14H10O4", "Solid", 850859,
  "The acne cream that kills skin bacteria, the flour bleach, and the radical initiator of acrylic dental and bone cements.", lib=8788)
S("96-10-6", "DEAC", "Diethylaluminium chloride", "C4H10AlCl", "Liquid", 23899896,
  "A Ziegler-Natta co-catalyst for polypropylene and synthetic rubber.", lib=8849)
S("97-90-5", "EGDMA", "Ethylene glycol dimethacrylate", "C10H14O4", "Liquid", 3051419,
  "A crosslinker for acrylic resins, dental composites and chromatography beads.", lib=8898)
S("98-29-3", "TBC", "4-tert-Butylcatechol", "C10H14O2", "Solid", 9906219,
  "The inhibitor added to styrene and butadiene so they don't polymerise in storage.", lib=8919)
S("99-04-7", "mToluic", "m-Toluic acid", "C8H8O2", "Solid", 3298405,
  "The acid behind the insect repellent DEET.", lib=8948)
S("99-94-5", "pToluic", "p-Toluic acid", "C8H8O2", "Solid", 1923613,
  "The half-oxidised p-xylene on the way to terephthalic acid.", lib=8965)
S("999-97-3", "HMDS", "Hexamethyldisilazane", "C6H19NSi2", "Liquid", 6606771,
  "Primes silicon wafers so photoresist sticks, and silylates alcohols in the lab.", smiles="N([Si](C)(C)C)[Si](C)(C)C")
S("18794-84-8", "Farnesene", "beta-Farnesene", "C15H24", "Liquid", 3254425,
  "A terpene that Amyris made from sugar with engineered yeast (2010s), for jet fuel, squalane and rubber.", lib=4271)
S("110-18-9", "TMEDA", "Tetramethylethylenediamine", "C6H16N2", "Liquid", 5053014,
  "A ligand that supercharges butyllithium, and a catalyst for polyacrylamide gels.", lib=2588)
S("298-06-6", "DEDTP", "O,O-Diethyl dithiophosphoric acid", "C4H11O2PS2", "Liquid", 34211022,
  "The acid behind the zinc dithiophosphates of motor oil and the insecticide phorate.", lib=5130)
S("11138-47-9", "Perborate", "Sodium perborate", "NaBO3·H2O", "Solid", 2920327,
  "The oxygen bleach of Persil (1907: perborate and silicate), releasing hydrogen peroxide in hot water.", smiles="B(O)(O)[O-].[Na+]")
S("90-80-2", "GDL", "Glucono-delta-lactone", "C6H10O6", "Solid", 1000005,
  "A slow acidifier that sets silken tofu and leavens baking.", lib=8629)
S("10543-57-4", "TAED", "Tetraacetylethylenediamine", "C10H16N2O4", "Solid", 2920661,
  "The bleach activator that lets perborate and percarbonate bleach at 40 C instead of 90.", lib=2353)
S("25383-99-7", "SSL", "Sodium stearoyl lactylate", "C24H43NaO6", "Solid", 340356,
  "E481, the dough conditioner of sliced bread.", lib=4772)
S("106-49-0", "pToluidine", "p-Toluidine", "C7H9N", "Solid", 2081885,
  "The para amine of toluene, for dyes and pigments; Hofmann's mauveine partly came from it.", lib=2392)
S("77-85-0", "TME", "Trimethylolethane", "C5H12O3", "Solid", 20952284,
  "A triol for weather-resistant alkyd and polyester coatings.", lib=8068)
S("95-49-8", "oChlorotoluene", "2-Chlorotoluene", "C7H7Cl", "Liquid", 3372186,
  "A chlorinated toluene for dyes, drugs and pesticides.", lib=8819)

E4.reactions += [
    R("Persil Bleach", "Borax + 2 NaOH + 4 H2O2 -> 4 Perborate + 11 H2O", MIX,
      "Borax dissolved with caustic soda and hydrogen peroxide; perborate crystallises.", wiki=2920327),
    R("Sodium Laurate", "LauricAcid + NaOH -> NaLaurate + H2O", MIX,
      "Coconut's lauric acid saponified.", wiki=33042280, dh=-60),
    R("Diethyl Sulfate", "2 Ethylene + H2SO4 -> DES", CAT,
      "Ethylene absorbed in concentrated sulfuric acid.", wiki=2348001, cat="H2SO4", T=80),
    R("Thioglycolic Acid", "ClAcOH + H2S -> TGA + HCl", FLASK,
      "Chloroacetic acid with sodium hydrosulfide.", wiki=2131951, T=40),
    R("Triphenylphosphine", "PCl3 + 3 Chlorobenzene + 6 Na -> PPh3 + 6 NaCl", FLASK,
      "Phosphorus trichloride, chlorobenzene and sodium.", wiki=1798259, T=60),
    R("Benzoyl Peroxide", "2 BenzoylChloride + H2O2 + 2 NaOH -> BPO + 2 NaCl + 2 H2O", FLASK,
      "Benzoyl chloride and alkaline hydrogen peroxide.", wiki=850859, T=10),
    R("Sodium Acid Pyrophosphate", "SodaAsh + 2 H3PO4 -> SAPP + CO2 + 2 H2O", HEAT,
      "Monosodium phosphate heated until two condense into one pyrophosphate.", wiki=8899136, T=250),
    R("Dicyandiamide", "2 Cyanamide -> DCD", HEAT,
      "Cyanamide dimerised in warm alkaline water.", wiki=12251858, T=80),
    R("o-Chlorotoluene", "Toluene + Cl2 -> oChlorotoluene + HCl", CAT,
      "Toluene chlorinated on the ring with iron chloride.", wiki=3372186, cat="FeCl3", T=40),
    R("p-Toluidine", "Nitrotoluene + 3 H2 -> pToluidine + 2 H2O", CAT,
      "p-Nitrotoluene hydrogenated over nickel.", wiki=2081885, cat="Ni", T=100),
    R("Triethyl Phosphate", "POCl3 + 3 Ethanol -> TEP + 3 HCl", FLASK,
      "Phosphorus oxychloride esterified with ethanol.", wiki=2852688, T=20),
]
E5.reactions += [
    R("Rongalite", "Na2S2O4 + CH2O + H2O -> Rongalite + NaHSO3", MIX,
      "Sodium dithionite and formaldehyde.", wiki=4932031),
    R("MEHQ", "Hydroquinone + Methanol -> MEHQ + H2O", CAT,
      "Hydroquinone methylated once.", wiki=12938750, cat="H2SO4", T=100),
    R("Dytek A", "MGN + 4 H2 -> MPMD", HIGHP,
      "Methylglutaronitrile hydrogenated over nickel.", wiki=67327667, cat="Ni", T=100),
    R("DTPMP", "DETA + 5 CH2O + 5 H3PO3 -> DTPMP + 5 H2O", FLASK,
      "The Moedritzer-Irani reaction on diethylenetriamine.", wiki=22759975, T=100),
    R("MGDA", "Alanine + 2 Glycolonitrile + 3 NaOH -> Na3MGDA + 2 NH3 + H2O", FLASK,
      "Alanine takes two glycolonitriles; the nitriles are saponified.", wiki=60029651, T=100),
    R("NPG Diglycidyl Ether", "NPG + 2 Epichlorohydrin + 2 NaOH -> NPGDGE + 2 NaCl + 2 H2O", FLASK,
      "Neopentyl glycol joined to two epichlorohydrins, the epoxides reclosed.", wiki=70423946, T=60),
    R("Tempol", "6 Acetone + 2 NH3 + 2 H2 + 3 H2O2 -> 2 Tempol + 8 H2O", FLASK,
      "Acetone and ammonia make triacetonamine; reduced and oxidised, it becomes the nitroxide.", wiki=32122780, T=60),
    R("Butanediol Diglycidyl Ether", "BDO + 2 Epichlorohydrin + 2 NaOH -> BDDGE + 2 NaCl + 2 H2O", FLASK,
      "1,4-Butanediol joined to two epichlorohydrins.", wiki=70452100, T=60),
    R("DABCO", "AEP -> DABCO + NH3", CAT,
      "Aminoethylpiperazine cyclised over a zeolite.", wiki=1777049, cat="ZSM5", T=350),
    R("Cyclopentane", "Cyclopentene + H2 -> Cyclopentane", CAT,
      "Cyclopentene hydrogenated over nickel.", wiki=1478144, cat="Ni", T=100),
    R("1,2,4-Triazole", "N2H4 + 2 Formamide -> Triazole124 + 2 H2O + NH3", HEAT,
      "Hydrazine heated with formamide.", wiki=3054679, T=170),
    R("D2EHPA", "POCl3 + 2 2EH + H2O -> D2EHPA + 3 HCl", FLASK,
      "Phosphorus oxychloride esterified twice with 2-ethylhexanol, the last chlorine hydrolysed.", wiki=31605902, T=60),
    R("BDMAEE", "2 DMAE -> BDMAEE + H2O", CAT,
      "Two dimethylaminoethanols joined into an ether.", wiki=13007260, cat="Alumina", T=300),
    R("Sodium Vinylsulfonate", "NaIsethionate -> NaVS + H2O", HEAT,
      "Sodium isethionate dehydrated.", wiki=42343006, T=300),
    R("HCFC-123", "PCE + 3 HF -> HCFC123 + 2 HCl", HIGHP,
      "Perchloroethylene fluorinated in the liquid phase.", wiki=5716871, cat="SbCl5", T=100),
    R("Glycerol Monostearate", "Glycerol + StearicAcid -> Monostearin + H2O", CAT,
      "Glycerol esterified once with stearic acid.", wiki=18929417, cat="NaOH", T=220),
    R("Dichlorosilane", "2 HSiCl3 -> H2SiCl2 + SiCl4", CAT,
      "Trichlorosilane redistributed over an amine resin.", wiki=9563449, cat="AlCl3", T=80),
    R("Caprolactone", "Cyclohexanone + PAA -> Caprolactone + AcOH", FLASK,
      "Cyclohexanone oxidised by peracetic acid (Baeyer-Villiger).", wiki=4151704, T=50),
    R("Titanium Isopropoxide", "TiCl4 + 4 Isopropanol + 4 NH3 -> TiOiPr4 + 4 NH4Cl", FLASK,
      "Titanium tetrachloride and isopropanol, with ammonia to take the hydrogen chloride.", wiki=9564261, T=20),
    R("tert-Butyl Perbenzoate", "TBHP + BenzoylChloride + NaOH -> TBPB + NaCl + H2O", FLASK,
      "tert-Butyl hydroperoxide acylated by benzoyl chloride.", wiki=52311322, T=10),
    R("Glycol Distearate", "EG + 2 StearicAcid -> EGDS + 2 H2O", HEAT,
      "Ethylene glycol esterified twice with stearic acid.", wiki=20921109, T=220),
    R("Dodecanedioic Acid", "2 CDT + 6 H2 + 5 O2 -> 2 DDDA + 2 H2O", FLASK,
      "Cyclododecatriene hydrogenated to cyclododecane, oxidised to the alcohol and ketone, and cut by nitric acid.",
      wiki=23975641, T=80),
    R("Oleyl Propylenediamine", "Oleylamine + Acrylonitrile + 2 H2 -> OleylPDA", CAT,
      "Oleylamine adds to acrylonitrile; the nitrile is hydrogenated.", wiki=52678570, cat="Ni", T=100),
    R("Tetramethylsilane", "2 Me3SiCl -> TMSi + Me2SiCl2", CAT,
      "Chlorotrimethylsilane redistributed over aluminium chloride.", wiki=1948276, cat="AlCl3", T=300),
    R("Acetyl Tributyl Citrate", "Citric + 3 Butanol + AceticAnhydride -> ATBC + 3 H2O + AcOH", CAT,
      "Citric acid esterified with butanol, then acetylated.", wiki=21589446, cat="H2SO4", T=130),
    R("Triethyl Citrate", "Citric + 3 Ethanol -> TEC + 3 H2O", CAT,
      "Citric acid esterified with ethanol.", wiki=17076391, cat="H2SO4", T=100),
    R("AIBN", "2 ACH + N2H4 + Cl2 -> AIBN + 2 H2O + 2 HCl", FLASK,
      "Acetone cyanohydrin and hydrazine make the hydrazo compound, which chlorine oxidises to the azo.",
      wiki=2231865, T=20),
    R("Bisphenol S", "2 Phenol + H2SO4 -> BPS + 2 H2O", HEAT,
      "Phenol sulfonated and condensed with a second phenol.", wiki=15996046, T=180),
    R("Nadic Anhydride", "Cyclopentadiene + MaleicAnhydride -> NadicAnhydride", PRESS,
      "A Diels-Alder reaction.", wiki=72797661, T=60),
    R("Durene", "TMB124 + Methanol -> Durene + H2O", CAT,
      "Pseudocumene methylated over a zeolite; durene's high melting point lets it crystallise out.", wiki="Durene",
      cat="ZSM5", T=400),
    R("Pyromellitic Dianhydride", "Durene + 6 O2 -> PMDA + 6 H2O", CAT,
      "Durene oxidised in the gas phase over vanadium oxide.", wiki=43338421, cat="V2O5", T=420),
    R("Diethylaluminium Chloride", "TEAL + AlCl3 -> 3 DEAC", MIX,
      "Triethylaluminium and aluminium chloride exchange ethyls and chlorines.", wiki=23899896),
    R("EGDMA", "EG + 2 MethacrylicAcid -> EGDMA + 2 H2O", CAT,
      "Ethylene glycol esterified with methacrylic acid.", wiki=3051419, cat="pTsOH", T=90),
    R("tert-Butylcatechol", "Catechol + Isobutylene -> TBC", CAT,
      "Catechol alkylated with isobutylene.", wiki=9906219, cat="H2SO4", T=80),
    R("m-Toluic Acid", "2 mXylene + 3 O2 -> 2 mToluic + 2 H2O", PRESS,
      "m-Xylene oxidised halfway by air.", wiki=3298405, T=150),
    R("p-Toluic Acid", "2 pXylene + 3 O2 -> 2 pToluic + 2 H2O", PRESS,
      "p-Xylene oxidised halfway by air.", wiki=1923613, T=150),
    R("Hexamethyldisilazane", "2 Me3SiCl + 3 NH3 -> HMDS + 2 NH4Cl", FLASK,
      "Chlorotrimethylsilane and ammonia.", wiki=6606771, T=20),
    R("TMEDA", "EDA + 4 CH2O + 4 H2 -> TMEDA + 4 H2O", CAT,
      "Ethylenediamine methylated four times by formaldehyde and hydrogen.", wiki=5053014, cat="Ni", T=120),
    R("Diethyl Dithiophosphoric Acid", "P4S10 + 8 Ethanol -> 4 DEDTP + 2 H2S", FLASK,
      "Phosphorus pentasulfide and ethanol.", wiki=34211022, T=80),
    R("Glucono-delta-lactone", "GluconicAcid -> GDL + H2O", HEAT,
      "Gluconic acid crystallised from a hot, concentrated solution as its lactone.", wiki=1000005, T=70),
    R("TAED", "EDA + 4 AceticAnhydride -> TAED + 4 AcOH", FLASK,
      "Ethylenediamine acetylated four times.", wiki=2920661, T=140),
    R("Sodium Stearoyl Lactylate", "StearicAcid + 2 LacticAcid + NaOH -> SSL + 3 H2O", HEAT,
      "Stearic acid, lactic acid and caustic soda heated together.", wiki=340356, T=200),
    R("Trimethylolethane", "Propanal + 3 CH2O + NaOH -> TME + HCOONa", FLASK,
      "Propanal takes two formaldehydes; a third reduces it.", wiki=20952284, T=50),
]
E6.reactions += [
    R("Farnesene", "Sucrose -> Farnesene", FERM,
      "Engineered yeast turns cane sugar into farnesene (Amyris, Brazil, 2012).", wiki=3254425,
      T=30, exact=False),
]

import authored_canon_9  # noqa: E402,F401
