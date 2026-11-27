"""
Curieosity's industrial chemistry, part 25 (see authored_canon.py): medicines, first batch.

Each medicine carries the IsMedicine property, which the Codex shows as a "Medicine" chip with a
note that medicines are made under licence and taken only as directed. The routes are the
textbook industrial ones, compressed to a few steps; none runs through a controlled precursor.
This batch takes the World Health Organization's essential medicines that can be reached from
what the game already makes, and tags the medicines that were already in the game.
"""

from authored_canon import S, R, CANON  # noqa: F401
from authored_content import E3, E4, E5, E6, SUBSTANCES, X, RAW  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR, pubchem)

P = {}
MED = ("IsMedicine",)


def PC(cas, key, name, formula, state, ref, desc, smiles=None, props=()):
    """A compound whose page is on PubChem (by CID, or by name)."""
    P[key] = pubchem(ref)
    S(cas, key, name, formula, state, P[key], desc, smiles=smiles, props=props)


def WK(cas, key, name, formula, state, title, desc, smiles=None, props=()):
    """A compound with a Wikipedia article."""
    P[key] = title
    S(cas, key, name, formula, state, title, desc, smiles=smiles, props=props)


# --- intermediates ------------------------------------------------------------------------------
PC("100-48-1", "CyanoPyridine4", "4-Cyanopyridine", "C6H4N2", "Solid", "4-Cyanopyridine",
   "4-Picoline ammoxidised: the start of isoniazid.", "N#Cc1ccncc1")
PC("1934-75-4", "NaDCA", "Sodium dicyanamide", "C2N3Na", "Solid", "Sodium dicyanamide",
   "A building block for biguanides and for ionic liquids.", "[Na+].N#C[N-]C#N")
PC("96-20-8", "AminoButanol2", "2-Amino-1-butanol", "C4H11NO", "Liquid", "2-Amino-1-butanol",
   "Nitropropane, formaldehyde and hydrogen; resolved with tartaric acid, its (S) form becomes ethambutol.", "CCC(N)CO")
WK("66-22-8", "Uracil", "Uracil", "C4H4N2O2", "Solid", "Uracil", "The base of RNA that pairs with adenine.", "O=c1cc[nH]c(=O)[nH]1")
PC("70-55-3", "TsNH2", "p-Toluenesulfonamide", "C7H9NO2S", "Solid", "p-Toluenesulfonamide",
   "Tosyl chloride on ammonia; a plasticiser and the sulfonamide of tolbutamide.", "Cc1ccc(cc1)S(N)(=O)=O")
PC("111-36-4", "BuNCO", "Butyl isocyanate", "C5H9NO", "Liquid", "Butyl isocyanate", "Butylamine on phosgene.", "CCCCN=C=O")
PC("110-78-1", "PrNCO", "Propyl isocyanate", "C4H7NO", "Liquid", "Propyl isocyanate", "Propylamine on phosgene.", "CCCN=C=O")
PC("98-64-6", "ClBzSulfonamide", "4-Chlorobenzenesulfonamide", "C6H6ClNO2S", "Solid", "4-Chlorobenzenesulfonamide",
   "Chlorobenzene chlorosulfonated and aminated.", "NS(=O)(=O)c1ccc(Cl)cc1")
WK("91-57-6", "MeNaphthalene2", "2-Methylnaphthalene", "C11H10", "Solid", "2-Methylnaphthalene",
   "Naphthalene with a methyl group; oxidised, it gives vitamin K3.", "Cc1ccc2ccccc2c1")
WK("106-94-5", "PrBr", "1-Bromopropane", "C3H7Br", "Liquid", "1-Bromopropane", "A propylating agent and degreasing solvent.", "CCCBr")
PC("109-08-0", "MePyrazine", "2-Methylpyrazine", "C5H6N2", "Liquid", "2-Methylpyrazine",
   "A nutty, roasted aroma, and the ring of pyrazinamide.", "Cc1cnccn1")
PC("19847-12-2", "CyanoPyrazine", "Pyrazinecarbonitrile", "C5H3N3", "Liquid", "Pyrazinecarbonitrile",
   "Methylpyrazine ammoxidised.", "N#Cc1cnccn1")
PC("96-13-9", "DBPOH", "2,3-Dibromo-1-propanol", "C3H6Br2O", "Liquid", "2,3-Dibromo-1-propanol",
   "Bromine added across allyl alcohol.", "OCC(Br)CBr")
PC("696-23-1", "NitroMeIm", "2-Methyl-5-nitroimidazole", "C4H5N3O2", "Solid", "2-Methyl-5-nitroimidazole",
   "The nitroimidazole ring of metronidazole and its relatives.", "Cc1ncc([N+]([O-])=O)[nH]1")
WK("90-15-3", "Naphthol1", "1-Naphthol", "C10H8O", "Solid", "1-Naphthol",
   "Naphthol with the hydroxyl at the end position: for the insecticide carbaryl, dyes and propranolol.", "Oc1cccc2ccccc12")
WK("552-89-6", "NitroBenzaldehyde2", "2-Nitrobenzaldehyde", "C7H5NO3", "Solid", "2-Nitrobenzaldehyde",
   "The aldehyde of nifedipine, and of Baeyer's indigo synthesis.", "O=Cc1ccccc1[N+]([O-])=O")
PC("2136-89-2", "OCBTC", "2-Chlorobenzotrichloride", "C7H4Cl4", "Liquid", "2-Chlorobenzotrichloride",
   "2-Chlorotoluene's methyl chlorinated to CCl3.", "Clc1ccccc1C(Cl)(Cl)Cl")
PC("42074-68-0", "ClTritylCl", "2-Chlorotrityl chloride", "C19H14Cl2", "Solid", "2-Chlorotrityl chloride",
   "A trityl chloride that also anchors peptides to resin in solid-phase synthesis.", "Clc1ccccc1C(Cl)(c1ccccc1)c1ccccc1")
PC("1121-60-4", "Py2CHO", "Pyridine-2-carboxaldehyde", "C6H5NO", "Liquid", "Pyridine-2-carboxaldehyde",
   "2-Picoline oxidised to the aldehyde.", "O=Cc1ccccn1")
PC("321-14-2", "ClSalicylic5", "5-Chlorosalicylic acid", "C7H5ClO3", "Solid", "5-Chlorosalicylic acid",
   "Salicylic acid chlorinated para to its hydroxyl.", "OC(=O)c1cc(Cl)ccc1O")
PC("121-87-9", "ClNitroaniline", "2-Chloro-4-nitroaniline", "C6H5ClN2O2", "Solid", "2-Chloro-4-nitroaniline",
   "4-Nitroaniline chlorinated; for niclosamide and disperse dyes.", "Nc1ccc(cc1Cl)[N+]([O-])=O")
PC("3249-68-1", "EBA", "Ethyl butyrylacetate", "C8H14O3", "Liquid", "Ethyl butyrylacetate",
   "A beta-ketoester from a Claisen condensation.", "CCCC(=O)CC(=O)OCC")
WK("120-29-6", "Tropine", "Tropine", "C8H15NO", "Solid", "Tropine", "The bicyclic amino alcohol of atropine.", "CN1C2CCC1CC(O)C2")
WK("529-64-6", "TropicAcid", "Tropic acid", "C9H10O3", "Solid", "Tropic_acid", "The acid half of atropine.", "OCC(C(O)=O)c1ccccc1")

# --- the medicines -------------------------------------------------------------------------------
WK("657-24-9", "Metformin", "Metformin", "C4H11N5", "Solid", "Metformin",
   "The first medicine for type 2 diabetes: it lowers the sugar the liver releases. Descended from the French lilac's guanidines.",
   "CN(C)C(=N)N=C(N)N", props=MED)
WK("54-85-3", "Isoniazid", "Isoniazid", "C6H7N3O", "Solid", "Isoniazid",
   "Since 1952 the backbone of tuberculosis treatment, always given with other drugs so the bacteria cannot escape by mutation.",
   "NNC(=O)c1ccncc1", props=MED)
WK("127-07-1", "Hydroxyurea", "Hydroxyurea", "CH4N2O2", "Solid", "Hydroxycarbamide",
   "Slows DNA synthesis: used for some leukaemias and to prevent the crises of sickle-cell disease.", "NC(=O)NO", props=MED)
WK("616-91-1", "NAC", "Acetylcysteine", "C5H9NO3S", "Solid", "Acetylcysteine",
   "The antidote to paracetamol overdose, refilling the liver's glutathione; also thins mucus.", "CC(=O)NC(CS)C(O)=O", props=MED)
WK("55-56-1", "Chlorhexidine", "Chlorhexidine", "C22H30Cl2N10", "Solid", "Chlorhexidine",
   "The antiseptic of surgical scrubs, mouthwash and newborns' umbilical cords.",
   "Clc1ccc(NC(=N)NC(=N)NCCCCCCNC(=N)NC(=N)Nc2ccc(Cl)cc2)cc1", props=MED)
WK("74-55-5", "Ethambutol", "Ethambutol", "C10H24N2O2", "Solid", "Ethambutol",
   "A tuberculosis drug that blocks the building of the bacterium's cell wall.", "CCC(CO)NCCNC(CC)CO", props=MED)
WK("51-21-8", "Fluorouracil", "Fluorouracil", "C4H3FN2O2", "Solid", "Fluorouracil",
   "5-FU: a fluorine where uracil's methyl-free carbon was jams DNA synthesis in fast-dividing cancer cells.",
   "Fc1c[nH]c(=O)[nH]c1=O", props=MED)
WK("89-57-6", "Mesalazine", "Mesalazine", "C7H7NO3", "Solid", "Mesalazine",
   "5-Aminosalicylic acid, which calms the inflamed bowel in ulcerative colitis.", "Nc1ccc(O)c(c1)C(O)=O", props=MED)
WK("57-66-9", "Probenecid", "Probenecid", "C13H19NO4S", "Solid", "Probenecid",
   "Keeps the kidneys from clearing uric acid's partners: for gout, and once to make wartime penicillin last longer.",
   "CCCN(CCC)S(=O)(=O)c1ccc(cc1)C(O)=O", props=MED)
WK("64-77-7", "Tolbutamide", "Tolbutamide", "C12H18N2O3S", "Solid", "Tolbutamide",
   "The first sulfonylurea (1956): it tells the pancreas to release insulin.", "CCCCNC(=O)NS(=O)(=O)c1ccc(C)cc1", props=MED)
WK("94-20-2", "Chlorpropamide", "Chlorpropamide", "C10H13ClN2O3S", "Solid", "Chlorpropamide",
   "A long-acting sulfonylurea for type 2 diabetes.", "CCCNC(=O)NS(=O)(=O)c1ccc(Cl)cc1", props=MED)
WK("58-27-5", "Menadione", "Menadione", "C11H8O2", "Solid", "Menadione",
   "Vitamin K3: the body turns it into the vitamin K that blood clotting needs; mostly fed to poultry.",
   "CC1=CC(=O)c2ccccc2C1=O", props=MED)
WK("87-33-2", "ISDN", "Isosorbide dinitrate", "C6H8N2O8", "Solid", "Isosorbide_dinitrate",
   "A nitrate that releases nitric oxide to widen blood vessels and relieve angina.",
   "[O-][N+](=O)OC1COC2C(COC12)O[N+]([O-])=O", props=MED)
WK("16051-77-7", "ISMN", "Isosorbide mononitrate", "C6H9NO6", "Solid", "Isosorbide_mononitrate",
   "The longer-lasting half-nitrated isosorbide, for preventing angina.", "OC1COC2C(COC12)O[N+]([O-])=O", props=MED)
WK("99-66-1", "Valproic", "Valproic acid", "C8H16O2", "Liquid", "Valproate",
   "Found to stop seizures by accident in 1963, when it was the solvent for other compounds being tested.",
   "CCCC(CCC)C(O)=O", props=MED)
WK("98-96-4", "Pyrazinamide", "Pyrazinamide", "C5H5N3O", "Solid", "Pyrazinamide",
   "A tuberculosis drug that kills the bacteria hiding in acidic pockets, shortening treatment to six months.",
   "NC(=O)c1cnccn1", props=MED)
WK("59-52-9", "Dimercaprol", "Dimercaprol", "C3H8OS2", "Liquid", "Dimercaprol",
   "British Anti-Lewisite (1940): two thiols grab arsenic, mercury and lead; the first antidote designed for a poison.",
   "OCC(S)CS", props=MED)
WK("443-48-1", "Metronidazole", "Metronidazole", "C6H9N3O3", "Solid", "Metronidazole",
   "Its nitro group is reduced only inside anaerobic microbes, where it shreds their DNA: for giardia, amoebae and anaerobic infections.",
   "Cc1ncc([N+]([O-])=O)n1CCO", props=MED)
WK("525-66-6", "Propranolol", "Propranolol", "C16H21NO2", "Solid", "Propranolol",
   "James Black's beta blocker (1964): it shields the heart from adrenaline. Nobel Prize 1988.",
   "CC(C)NCC(O)COc1cccc2ccccc12", props=MED)
WK("21829-25-4", "Nifedipine", "Nifedipine", "C17H18N2O6", "Solid", "Nifedipine",
   "A calcium-channel blocker that relaxes artery walls, for high blood pressure and angina.",
   "COC(=O)C1=C(C)NC(C)=C(C1c1ccccc1[N+]([O-])=O)C(=O)OC", props=MED)
WK("23593-75-1", "Clotrimazole", "Clotrimazole", "C22H17ClN2", "Solid", "Clotrimazole",
   "An antifungal for athlete's foot and thrush: it blocks the fungus making ergosterol for its membrane.",
   "Clc1ccccc1C(n1ccnc1)(c1ccccc1)c1ccccc1", props=MED)
WK("603-50-9", "Bisacodyl", "Bisacodyl", "C22H19NO4", "Solid", "Bisacodyl", "A stimulant laxative.",
   "CC(=O)Oc1ccc(cc1)C(c1ccc(OC(C)=O)cc1)c1ccccn1", props=MED)
WK("55-98-1", "Busulfan", "Busulfan", "C6H14O6S2", "Solid", "Busulfan",
   "An alkylating drug that clears the bone marrow before a stem-cell transplant.", "CS(=O)(=O)OCCCCOS(C)(=O)=O", props=MED)
WK("50-65-7", "Niclosamide", "Niclosamide", "C13H8Cl2N2O4", "Solid", "Niclosamide",
   "Kills tapeworms by uncoupling their energy supply; also used against the snails that carry schistosomiasis.",
   "OC1=C(C=C(Cl)C=C1)C(=O)Nc1ccc(cc1Cl)[N+]([O-])=O", props=MED)
WK("51-52-5", "PTU", "Propylthiouracil", "C7H10N2OS", "Solid", "Propylthiouracil",
   "Slows the thyroid gland making its hormones, for an overactive thyroid.", "CCCc1cc(=O)[nH]c(=S)[nH]1", props=MED)
WK("126-07-8", "Griseofulvin", "Griseofulvin", "C17H17ClO6", "Solid", "Griseofulvin",
   "An antifungal from Penicillium griseofulvum that builds up in new skin, hair and nails as they grow.",
   "COC1=CC(=O)CC(C)C12Oc1c(Cl)c(OC)cc(OC)c1C2=O", props=MED)
WK("51-41-2", "Norepinephrine", "Norepinephrine", "C8H11NO3", "Solid", "Norepinephrine",
   "Noradrenaline: the nerve messenger of fight or flight, given by drip to raise blood pressure in shock.",
   "NCC(O)c1ccc(O)c(O)c1", props=MED)
WK("87-00-3", "Homatropine", "Homatropine", "C16H21NO3", "Solid", "Homatropine",
   "A shorter-acting cousin of atropine, in eye drops that widen the pupil.", "CN1C2CCC1CC(C2)OC(=O)C(O)c1ccccc1", props=MED)

# povidone and its iodine complex, and curare from the apothecaries' herbs
P["PVP"] = "Polyvinylpyrrolidone"
X("PVP", "Polyvinylpyrrolidone", "(C6H9NO)n", "Solid",
  "Povidone: a water-soluble polymer that binds tablets, thickens eye drops and hair gel, and once stretched blood plasma.",
  P["PVP"], id=0, balance="C6H9NO", props=("IsPolymer",))
CANON["9003-39-8"] = "PVP"
P["PVPI"] = "Povidone-iodine"
X("PVPI", "Povidone-iodine", "mixture", "Solid",
  "Iodine held by povidone and let out slowly: the brown antiseptic painted on skin before surgery.", P["PVPI"], id=0, balance="C",
  props=MED)
CANON["25655-41-8"] = "PVPI"
RAW("Curare", "Curare", "The arrow poison of the Amazon, boiled from Chondodendron vines; it paralyses without harming the heart.",
    "Curare", color="#3a2a18")
WK("57-95-4", "Tubocurarine", "Tubocurarine chloride", "C37H42Cl2N2O6", "Solid", 2472170,
   "Curare's alkaloid: it blocks the signal from nerve to muscle. From 1942 it let surgeons relax muscles under light anaesthesia.",
   "OC1=CC=C2C=C1OC=3C=C4C(=CC3OC)CCN(C)C4CC5=CC=C(OC=6C(O)=C(OC)C=C7C6C(C2)[N+](C)(C)CC7)C=C5.Cl.[Cl-]", props=MED)

# the medicines that were already in the game
for _k in ("Aspirin", "Paracetamol", "Ibuprofen", "Sulfanilamide", "Prontosil", "Quinine", "Penicillin", "Ampicillin",
           "Erythromycin", "Streptomycin", "Tetracycline", "Lovastatin", "Insulin", "Cisplatin", "ChloralHydrate",
           "Nitroglycerin", "Caffeine", "Theophylline", "Benzocaine", "Procaine", "Lidocaine", "Atropine", "Epinephrine",
           "Artemisinin", "Phenacetin", "Li2CO3", "Salicylamide", "Propofol", "Halothane", "Sevoflurane", "Dapsone",
           "Disulfiram", "AmantadineHCl", "Piperazine", "ACA", "DimethylFumarate", "Thalidomide", "FDG", "Docusate"):
    _s = SUBSTANCES[_k]
    if "IsMedicine" not in _s.props:
        _s.props = tuple(_s.props) + MED

# --- the reactions -------------------------------------------------------------------------------
E5.reactions += [
    R("Metformin", "DCD + Me2NH -> Metformin", HEAT,
      "Dicyandiamide and dimethylamine hydrochloride fused together.", wiki=P["Metformin"], T=140),
    R("4-Cyanopyridine", "2 Picoline4 + 2 NH3 + 3 O2 -> 2 CyanoPyridine4 + 6 H2O", CAT,
      "4-Picoline ammoxidised over vanadium oxide.", wiki=P["CyanoPyridine4"], cat="V2O5", T=380),
    R("Isoniazid", "CyanoPyridine4 + N2H4 + H2O -> Isoniazid + NH3", FLASK,
      "The nitrile hydrolysed and taken up by hydrazine as the hydrazide.", wiki=P["Isoniazid"], T=100),
    R("Hydroxyurea", "KOCN + NH2OH + HCl -> Hydroxyurea + KCl", MIX,
      "Cyanate adds to hydroxylamine, as in Wohler's urea.", wiki=P["Hydroxyurea"]),
    R("Acetylcysteine", "Cysteine + AceticAnhydride -> NAC + AcOH", MIX,
      "Cysteine's amine acetylated.", wiki=P["NAC"]),
    R("Sodium Dicyanamide", "Cyanamide + CNCl + 2 NaOH -> NaDCA + NaCl + 2 H2O", COOL,
      "Cyanamide cyanated with cyanogen chloride in caustic.", wiki=P["NaDCA"], T=10),
    R("Chlorhexidine", "HMDA + 2 NaDCA + 2 pChloroaniline + 2 HCl -> Chlorhexidine + 2 NaCl", HEAT,
      "Hexamethylenediamine built into a bis-cyanoguanidine, then each end capped with 4-chloroaniline.",
      wiki=P["Chlorhexidine"], T=140),
    R("2-Amino-1-butanol", "NitroPropane1 + CH2O + 3 H2 -> AminoButanol2 + 2 H2O", CAT,
      "A Henry reaction of 1-nitropropane with formaldehyde, then the nitro group hydrogenated.",
      wiki=P["AminoButanol2"], cat="Ni", T=60),
    R("Ethambutol", "2 AminoButanol2 + EDC -> Ethambutol + 2 HCl", HEAT,
      "Two (S)-aminobutanols joined by 1,2-dichloroethane.", wiki=P["Ethambutol"], T=120),
    R("Uracil", "Malic + Urea + Oleum -> Uracil + CO + 3 H2O + Oleum", FLASK,
      "In fuming sulfuric acid malic acid loses CO to formylacetic acid, which closes onto urea.", wiki=P["Uracil"], T=100),
    R("Fluorouracil", "Uracil + F2 -> Fluorouracil + HF", COOL,
      "Uracil fluorinated directly with dilute fluorine gas.", wiki=P["Fluorouracil"], T=0),
    R("Mesalazine", "Salicylic + HNO3 + 3 H2 -> Mesalazine + 3 H2O", CAT,
      "Salicylic acid nitrated para to its hydroxyl and the nitro group hydrogenated.", wiki=P["Mesalazine"], cat="Pd", T=60),
    R("Probenecid", "2 TsCl + 2 Dipropylamine + 3 O2 -> 2 Probenecid + 2 HCl + 2 H2O", FLASK,
      "Tosyl chloride on dipropylamine, then the methyl group oxidised to the acid.", wiki=P["Probenecid"], T=80),
    R("p-Toluenesulfonamide", "TsCl + 2 NH3 -> TsNH2 + NH4Cl", MIX, "Tosyl chloride on ammonia.", wiki=P["TsNH2"]),
    R("Butyl Isocyanate", "Butylamine + COCl2 -> BuNCO + 2 HCl", FLASK, "Butylamine phosgenated.", wiki=P["BuNCO"], T=100),
    R("Propyl Isocyanate", "Propylamine + COCl2 -> PrNCO + 2 HCl", FLASK, "Propylamine phosgenated.", wiki=P["PrNCO"], T=100),
    R("Tolbutamide", "TsNH2 + BuNCO -> Tolbutamide", FLASK, "The sulfonamide adds to butyl isocyanate.", wiki=P["Tolbutamide"], T=80),
    R("4-Chlorobenzenesulfonamide", "Chlorobenzene + 2 HSO3Cl + 2 NH3 -> ClBzSulfonamide + H2SO4 + NH4Cl + HCl", FLASK,
      "Chlorobenzene chlorosulfonated and the sulfonyl chloride aminated.", wiki=P["ClBzSulfonamide"], T=60),
    R("Chlorpropamide", "ClBzSulfonamide + PrNCO -> Chlorpropamide", FLASK,
      "The sulfonamide adds to propyl isocyanate.", wiki=P["Chlorpropamide"], T=80),
    R("2-Methylnaphthalene", "Naphthalene + Methanol -> MeNaphthalene2 + H2O", CAT,
      "Naphthalene methylated over a zeolite; coal tar's methylnaphthalene oil gives it too.", wiki=P["MeNaphthalene2"],
      cat="Alumina", T=400),
    R("Menadione", "MeNaphthalene2 + 3 H2O2 -> Menadione + 4 H2O", FLASK,
      "The ring that carries the methyl group oxidised to a quinone.", wiki=P["Menadione"], T=60),
    R("Isosorbide Dinitrate", "Isosorbide + 2 HNO3 -> ISDN + 2 H2O", COOL,
      "Both hydroxyls of isosorbide nitrated, cold.", wiki=P["ISDN"], T=0),
    R("Isosorbide Mononitrate", "Isosorbide + HNO3 -> ISMN + H2O", FLASK,
      "One hydroxyl nitrated, the other kept.", wiki=P["ISMN"], T=20),
    R("1-Bromopropane", "Propanol + HBr -> PrBr + H2O", FLASK, "1-Propanol on hydrogen bromide.", wiki=P["PrBr"], T=80),
    R("Valproic Acid", "DEMalonate + 2 PrBr + 2 NaOH -> Valproic + 2 NaBr + 2 Ethanol + CO2", FLASK,
      "A malonic ester synthesis: two propyl groups put on, the esters hydrolysed, one carboxyl boiled off.",
      wiki=P["Valproic"], T=120),
    R("2-Methylpyrazine", "EDA + PG -> MePyrazine + 2 H2O + 3 H2", CAT,
      "Ethylenediamine and propylene glycol cyclised and dehydrogenated.", wiki=P["MePyrazine"], cat="Cu", T=400),
    R("Pyrazinecarbonitrile", "2 MePyrazine + 2 NH3 + 3 O2 -> 2 CyanoPyrazine + 6 H2O", CAT,
      "Methylpyrazine ammoxidised.", wiki=P["CyanoPyrazine"], cat="V2O5", T=380),
    R("Pyrazinamide", "CyanoPyrazine + H2O -> Pyrazinamide", MIX, "The nitrile hydrated to the amide.", wiki=P["Pyrazinamide"]),
    R("2,3-Dibromopropanol", "AllylAlcohol + Br2 -> DBPOH", MIX, "Bromine added across allyl alcohol.", wiki=P["DBPOH"]),
    R("Dimercaprol", "DBPOH + 2 H2S + 2 NaOH -> Dimercaprol + 2 NaBr + 2 H2O", FLASK,
      "Both bromines swapped for thiols with sodium hydrosulfide.", wiki=P["Dimercaprol"], T=60),
    R("2-Methyl-5-nitroimidazole", "MeImidazole2 + HNO3 -> NitroMeIm + H2O", FLASK,
      "2-Methylimidazole nitrated in mixed acid.", wiki=P["NitroMeIm"], T=100),
    R("Metronidazole", "NitroMeIm + EO + Formic -> Metronidazole + Formic", FLASK,
      "The ring nitrogen opens ethylene oxide in formic acid.", wiki=P["Metronidazole"], T=60),
    R("1-Naphthol", "Naphthalene + H2 + O2 -> Naphthol1 + H2O", CAT,
      "Naphthalene hydrogenated to tetralin, air-oxidised to tetralone and dehydrogenated.", wiki=P["Naphthol1"], cat="Pd", T=200),
    R("Propranolol", "Naphthol1 + Epichlorohydrin + Isopropylamine + NaOH -> Propranolol + NaCl + H2O", FLASK,
      "1-Naphthol glycidylated, and isopropylamine opens the epoxide.", wiki=P["Propranolol"], T=80),
    R("2-Nitrobenzaldehyde", "oNitrotoluene + 2 Cl2 + H2O -> NitroBenzaldehyde2 + 4 HCl", LIGHT,
      "The methyl group chlorinated twice in light and the benzal chloride hydrolysed.", wiki=P["NitroBenzaldehyde2"]),
    R("Nifedipine", "NitroBenzaldehyde2 + 2 MAA + NH3 -> Nifedipine + 3 H2O", FLASK,
      "A Hantzsch synthesis: an aldehyde, two ketoesters and ammonia close a dihydropyridine ring in one pot.",
      wiki=P["Nifedipine"], T=80),
    R("2-Chlorobenzotrichloride", "oChlorotoluene + 3 Cl2 -> OCBTC + 3 HCl", LIGHT,
      "2-Chlorotoluene's methyl group chlorinated three times in light.", wiki=P["OCBTC"]),
    R("2-Chlorotrityl Chloride", "OCBTC + 2 Benzene -> ClTritylCl + 2 HCl", FLASK,
      "Two benzenes put on by Friedel-Crafts.", wiki=P["ClTritylCl"], T=40),
    R("Clotrimazole", "ClTritylCl + Imidazole + NaOH -> Clotrimazole + NaCl + H2O", FLASK,
      "Imidazole's nitrogen takes the trityl carbon.", wiki=P["Clotrimazole"], T=60),
    R("Pyridine-2-carboxaldehyde", "Picoline2 + O2 -> Py2CHO + H2O", CAT,
      "2-Picoline's methyl oxidised to the aldehyde.", wiki=P["Py2CHO"], cat="V2O5", T=350),
    R("Bisacodyl", "Py2CHO + 2 Phenol + 2 AceticAnhydride -> Bisacodyl + 2 AcOH + H2O", FLASK,
      "Two phenols condensed onto the aldehyde, then both acetylated.", wiki=P["Bisacodyl"], T=60),
    R("Busulfan", "BDO + 2 MsCl -> Busulfan + 2 HCl", FLASK, "1,4-Butanediol mesylated at both ends.", wiki=P["Busulfan"], T=0),
    R("5-Chlorosalicylic Acid", "Salicylic + Cl2 -> ClSalicylic5 + HCl", FLASK, "Salicylic acid chlorinated.", wiki=P["ClSalicylic5"], T=40),
    R("2-Chloro-4-nitroaniline", "Nitroaniline + Cl2 -> ClNitroaniline + HCl", COOL,
      "4-Nitroaniline chlorinated once, cold, next to its amine (warmer and with more chlorine, both sides go: dicloran).",
      wiki=P["ClNitroaniline"], T=5),
    R("Niclosamide", "3 ClSalicylic5 + 3 ClNitroaniline + PCl3 -> 3 Niclosamide + H3PO3 + 3 HCl", FLASK,
      "The acid and the amine joined to an amide with phosphorus trichloride.", wiki=P["Niclosamide"], T=130),
    R("Ethyl Butyrylacetate", "EthylButyrate + EthylAcetate + NaOEt -> EBA + Ethanol + NaOEt", FLASK,
      "A Claisen condensation with sodium ethoxide.", wiki=P["EBA"], T=80),
    R("Propylthiouracil", "EBA + Thiourea -> PTU + Ethanol + H2O", FLASK,
      "The ketoester closes a ring with thiourea.", wiki=P["PTU"], T=80),
    R("Griseofulvin", "Glucose + CornSteep + KCl -> Griseofulvin", BIOR,
      "Penicillium griseofulvum grown on sugar with chloride, which it builds into the molecule.",
      wiki=P["Griseofulvin"], cat="Penicillium", exact=False, T=25),
    R("Norepinephrine", "Catechol + ClAcCl + 2 NH3 + H2 -> Norepinephrine + HCl + NH4Cl", FLASK,
      "Catechol chloroacetylated, the chlorine swapped for an amine, the ketone reduced, and the left-handed form kept with tartaric acid.",
      wiki=P["Norepinephrine"], T=40),
    R("Povidone", "NVP -> PVP", POLY, "N-Vinylpyrrolidone polymerised in water with a peroxide.", wiki=P["PVP"]),
    R("Povidone-Iodine", "PVP + I2 -> PVPI", MIX, "Povidone soaks up iodine into a loose complex.", wiki=P["PVPI"], exact=False),
    R("Isolating Tubocurarine", "Curare + Ethanol -> Tubocurarine", MIX,
      "Harold King (1935) extracted curare and crystallised its active alkaloid.", wiki=P["Tubocurarine"], exact=False),
    R("Hydrolysing Atropine", "Atropine + H2O -> Tropine + TropicAcid", MIX,
      "Atropine split into its alcohol and its acid.", wiki=P["Tropine"]),
    R("Homatropine", "Tropine + MandelicAcid -> Homatropine + H2O", FLASK,
      "Tropine esterified with mandelic acid in place of tropic acid.", wiki=P["Homatropine"], T=100),
]

# Milestones for the stretches this part lengthened (messages only).
import authored_content as _C  # noqa: E402
from gen_authored import Milestone  # noqa: E402
for _m in _C.MILESTONES:
    if _m.on == "I2":
        _m.grant = tuple(_m.grant) + ("Curare",)
_C.MILESTONES += [
    Milestone("Fluorouracil", message="One fluorine atom where a hydrogen should be: cancer cells mistake fluorouracil for uracil and jam their own DNA synthesis (Heidelberger, 1957)."),
]
import authored_canon_26  # noqa: E402,F401
