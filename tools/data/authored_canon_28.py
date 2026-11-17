"""
Curieosity's industrial chemistry, part 28 (see authored_canon.py): medicines, second batch.

More of the World Health Organization's essential medicines, each now made in the game (so its
locked preview in authored_placeholders.py drops out): the thiazide and loop diuretics,
acetazolamide, simvastatin from lovastatin, the artemisinin family, diclofenac and naproxen,
the penicillin salts, aminophylline, and the alkaloids the apothecaries' plants give: morphine,
codeine and papaverine from opium (natural isolations only), pilocarpine, physostigmine and
colchicine. Medicines already in the game that the first batch missed are tagged too.
"""

from authored_canon import S, R, CANON  # noqa: F401
from authored_content import E3, E4, E5, E6, SUBSTANCES, RAW  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR, pubchem)

P = {}
MED = ("IsMedicine",)


def PC(cas, key, name, formula, state, ref, desc, smiles=None, props=(), lib=0):
    """A compound whose page is on PubChem (by CID, or by name)."""
    P[key] = pubchem(ref)
    S(cas, key, name, formula, state, P[key], desc, smiles=smiles, props=props, lib=lib)


def WK(cas, key, name, formula, state, title, desc, smiles=None, props=(), lib=0):
    """A compound with a Wikipedia article."""
    P[key] = title
    S(cas, key, name, formula, state, title, desc, smiles=smiles, props=props, lib=lib)


# --- the apothecaries' plants -------------------------------------------------------------------
RAW("Opium", "Opium", "The dried latex of the opium poppy's seed pods, the source of morphine and codeine since antiquity.",
    "Opium", color="#5a3a1a")
RAW("Jaborandi", "Jaborandi Leaves", "Leaves of the Brazilian Pilocarpus shrub, chewed to make the mouth water.", "Pilocarpus",
    color="#4a7a3a")
RAW("CalabarBean", "Calabar Beans", "The ordeal bean of the Efik people of Nigeria: a poison that slows the heart and the gut.",
    "Physostigma_venenosum", color="#6a3a2a")
RAW("AutumnCrocus", "Autumn Crocus", "Colchicum corms, poisonous; known since ancient Egypt as a remedy for gout.",
    "Colchicum_autumnale", color="#b07ac0")

# --- intermediates ------------------------------------------------------------------------------
WK("79-19-6", "Thiosemicarbazide", "Thiosemicarbazide", "CH5N3S", "Solid", "Thiosemicarbazide",
   "Hydrazine on thiocyanate: the start of thiadiazoles and of some photographic chemicals.", "NNC(N)=S")
PC("2349-67-9", "AMT", "2-Amino-5-mercapto-1,3,4-thiadiazole", "C2H3N3S2", "Solid", "2-Amino-5-mercapto-1,3,4-thiadiazole",
   "Thiosemicarbazide closed into a ring with carbon disulfide.", "Nc1nnc(S)s1")
PC("32873-56-6", "AcAMT", "2-Acetamido-5-mercapto-1,3,4-thiadiazole", "C4H5N3OS2", "Solid",
   "2-Acetamido-5-mercapto-1,3,4-thiadiazole", "The acetylated thiadiazole on the way to acetazolamide.", "CC(=O)Nc1nnc(S)s1")
PC("121-73-3", "mCNB", "3-Chloronitrobenzene", "C6H4ClNO2", "Solid", "1-Chloro-3-nitrobenzene",
   "Nitrobenzene chlorinated: the nitro group sends chlorine to the meta position.", "[O-][N+](=O)c1cccc(Cl)c1")
PC("108-42-9", "mChloroaniline", "3-Chloroaniline", "C6H6ClN", "Liquid", "3-Chloroaniline",
   "3-Chloronitrobenzene reduced; for the thiazide diuretics and herbicides.", "Nc1cccc(Cl)c1")
PC("121-30-2", "ACBDS", "4-Amino-6-chloro-1,3-benzenedisulfonamide", "C6H8ClN3O4S2", "Solid",
   "4-Amino-6-chloro-1,3-benzenedisulfonamide", "Two sulfonamides on 3-chloroaniline: one step from the thiazides.",
   "Nc1cc(Cl)c(cc1S(N)(=O)=O)S(N)(=O)=O")
PC("95-73-8", "DCT24", "2,4-Dichlorotoluene", "C7H6Cl2", "Liquid", "2,4-Dichlorotoluene", "Toluene chlorinated twice on the ring.",
   "Cc1ccc(Cl)cc1Cl")
PC("50-84-0", "DCBA24", "2,4-Dichlorobenzoic acid", "C7H4Cl2O2", "Solid", "2,4-Dichlorobenzoic acid",
   "2,4-Dichlorotoluene oxidised.", "OC(=O)c1ccc(Cl)cc1Cl")
PC("2736-23-4", "Lasamide", "2,4-Dichloro-5-sulfamoylbenzoic acid", "C7H5Cl2NO4S", "Solid", "Lasamide",
   "The sulfonamide acid that furfurylamine turns into furosemide.", "NS(=O)(=O)c1cc(C(O)=O)c(Cl)cc1Cl")
PC("15307-93-4", "DCDPA", "2,6-Dichlorodiphenylamine", "C12H9Cl2N", "Solid", "2,6-Dichlorodiphenylamine",
   "2,6-Dichloroaniline arylated with iodobenzene: the backbone of diclofenac.", "Clc1cccc(Cl)c1Nc1ccccc1")
PC("93-04-9", "Nerolin", "2-Methoxynaphthalene", "C11H10O", "Solid", "2-Methoxynaphthalene",
   "Nerolin (yara yara): an orange-blossom scent for soaps, and the ring of naproxen.", "COc1ccc2ccccc2c1")
PC("140-28-3", "Benzathine", "Benzathine", "C16H20N2", "Liquid", "N,N'-Dibenzylethylenediamine",
   "A diamine whose penicillin salt dissolves so slowly that one injection lasts weeks.", "C(NCCNCc1ccccc1)c1ccccc1")

# --- the medicines -------------------------------------------------------------------------------
WK("59-66-5", "Acetazolamide", "Acetazolamide", "C4H6N4O3S2", "Solid", "Acetazolamide",
   "Blocks carbonic anhydrase: for glaucoma, altitude sickness and some epilepsies.", "CC(=O)Nc1nnc(s1)S(N)(=O)=O",
   props=MED, lib=6737)
WK("58-94-6", "Chlorothiazide", "Chlorothiazide", "C7H6ClN3O4S2", "Solid", "Chlorothiazide",
   "The first thiazide diuretic (Merck, 1957): it makes the kidneys pass salt and water, lowering blood pressure.",
   "NS(=O)(=O)c1cc2c(cc1Cl)NC=NS2(=O)=O", props=MED, lib=6672)
WK("58-93-5", "HCTZ", "Hydrochlorothiazide", "C7H8ClN3O4S2", "Solid", "Hydrochlorothiazide",
   "The most prescribed thiazide, for high blood pressure and swelling.", "NS(=O)(=O)c1cc2c(cc1Cl)NCNS2(=O)=O",
   props=MED, lib=6671)
WK("54-31-9", "Furosemide", "Furosemide", "C12H11ClN2O5S", "Solid", "Furosemide",
   "A loop diuretic, strong enough to clear fluid from the lungs in heart failure within the hour.",
   "NS(=O)(=O)c1cc(C(O)=O)c(NCc2ccco2)cc1Cl", props=MED, lib=6360)
WK("79902-63-9", "Simvastatin", "Simvastatin", "C25H38O5", "Solid", "Simvastatin",
   "A statin: it blocks the liver's cholesterol factory (HMG-CoA reductase).",
   "CCC(C)(C)C(=O)OC1CC(C)C=C2C=CC(C)C(CCC3CC(O)CC(=O)O3)C12", props=MED, lib=8266)
WK("71939-50-9", "Artenimol", "Dihydroartemisinin", "C15H24O5", "Solid", "Dihydroartemisinin",
   "Artemisinin's lactone reduced to a lactol: the active form all the artemisinin drugs become in the body.",
   "CC1CCC2C(C)C(O)OC3OC4(C)CCC1C32OO4", props=MED, lib=7729)
WK("71963-77-4", "Artemether", "Artemether", "C16H26O5", "Solid", "Artemether",
   "The methyl ether of dihydroartemisinin; with lumefantrine, the standard cure for malaria.",
   "COC1OC2OC3(C)CCC4C(C)CCC(C1C)C42OO3", props=MED, lib=7730)
WK("88495-63-0", "Artesunate", "Artesunate", "C19H28O8", "Solid", "Artesunate",
   "A water-soluble artemisinin given by injection for severe malaria.",
   "CC1CCC2C(C)C(OC(=O)CCC(O)=O)OC3OC4(C)CCC1C32OO4", props=MED, lib=8589)
WK("15307-86-5", "Diclofenac", "Diclofenac", "C14H11Cl2NO2", "Solid", "Diclofenac",
   "A strong NSAID for arthritis and pain, in tablets and in gels rubbed on joints.", "OC(=O)Cc1ccccc1Nc1c(Cl)cccc1Cl",
   props=MED, lib=3876)
WK("22204-53-1", "Naproxen", "Naproxen", "C14H14O3", "Solid", "Naproxen",
   "A long-acting NSAID; only its (S) form works, so the other is separated away.", "COc1ccc2cc(ccc2c1)C(C)C(O)=O",
   props=MED, lib=4505)
WK("317-34-0", "Aminophylline", "Aminophylline", "C16H24N10O4", "Solid", "Aminophylline",
   "Two theophyllines held by ethylenediamine, which makes them dissolve for injection in asthma attacks.",
   "Cn1c2nc[nH]c2c(=O)n(C)c1=O.Cn1c2nc[nH]c2c(=O)n(C)c1=O.NCCN", props=MED, lib=5280)
WK("54-35-3", "ProcainePenG", "Procaine benzylpenicillin", "C29H38N4O6S", "Solid", "Procaine_benzylpenicillin",
   "Penicillin as its procaine salt: a deep injection that releases it over a day, and numbs as it goes.",
   "CCN(CC)CCOC(=O)c1ccc(N)cc1.CC1(C)SC2C(NC(=O)Cc3ccccc3)C(=O)N2C1C(O)=O", props=MED, lib=6362)
WK("1538-09-6", "BenzathinePenG", "Benzathine benzylpenicillin", "C48H56N6O8S2", "Solid", "Benzathine_benzylpenicillin",
   "One injection holds penicillin in the blood for weeks: the treatment for syphilis and for preventing rheumatic fever.",
   "C(NCCNCc1ccccc1)c1ccccc1.CC1(C)SC2C(NC(=O)Cc3ccccc3)C(=O)N2C1C(O)=O.CC1(C)SC2C(NC(=O)Cc3ccccc3)C(=O)N2C1C(O)=O",
   props=MED, lib=3880)
WK("57-27-2", "Morphine", "Morphine", "C17H19NO3", "Solid", "Morphine",
   "The first alkaloid ever isolated (Serturner, 1804) and still the standard for severe pain.",
   "CN1CCC23C4Oc5c3c(CC1C2C=CC4O)ccc5O", props=MED, lib=6591)
WK("76-57-3", "Codeine", "Codeine", "C18H21NO3", "Solid", "Codeine",
   "Morphine's methyl ether, a minor alkaloid of opium; a milder painkiller and cough suppressant.",
   "COc1ccc2CC3N(C)CCC45C(Oc1c24)C(O)C=CC35", props=MED, lib=7976)
WK("58-74-2", "Papaverine", "Papaverine", "C20H21NO4", "Solid", "Papaverine",
   "An opium alkaloid that is not a narcotic: it relaxes smooth muscle, opening spasmed blood vessels.",
   "COc1ccc(Cc2nccc3cc(OC)c(OC)cc23)cc1OC", props=MED, lib=6667)
WK("92-13-7", "Pilocarpine", "Pilocarpine", "C11H16N2O2", "Solid", "Pilocarpine",
   "Eye drops that narrow the pupil and drain the eye in glaucoma, and a tablet for dry mouth.",
   "CCC1C(=O)OCC1Cc1cncn1C", props=MED, lib=8712)
WK("57-47-6", "Physostigmine", "Physostigmine", "C15H21N3O2", "Solid", "Physostigmine",
   "The Calabar bean's alkaloid: it stops acetylcholine being broken down, an antidote to atropine poisoning.",
   "CNC(=O)Oc1ccc2N(C)C3N(C)CCC3(C)c2c1", props=MED, lib=6595)
WK("64-86-8", "Colchicine", "Colchicine", "C22H25NO6", "Solid", "Colchicine",
   "It stops cells dividing by binding tubulin: a remedy for gout attacks, and the tool that doubles plant chromosomes.",
   "COc1cc2CCC(NC(C)=O)C3=CC(=O)C(OC)=CC=C3c2c(OC)c1OC", props=MED, lib=7087)

# medicines already in the game that the first batch did not tag
for _k in ("Digoxin", "Digitoxin", "Phenytoin", "TEASalicylate", "Hexylresorcinol"):
    _s = SUBSTANCES[_k]
    if "IsMedicine" not in _s.props:
        _s.props = tuple(_s.props) + MED

# --- the reactions -------------------------------------------------------------------------------
E5.reactions += [
    R("Thiosemicarbazide", "N2H4 + KSCN + HCl -> Thiosemicarbazide + KCl", FLASK,
      "Hydrazine hydrochloride boiled with thiocyanate.", wiki=P["Thiosemicarbazide"], T=100),
    R("Aminomercaptothiadiazole", "Thiosemicarbazide + CS2 -> AMT + H2S", FLASK,
      "Carbon disulfide closes thiosemicarbazide into a thiadiazole ring.", wiki=P["AMT"], T=80),
    R("Acetylated Thiadiazole", "AMT + AceticAnhydride -> AcAMT + AcOH", FLASK, "The amine acetylated.", wiki=P["AcAMT"], T=100),
    R("Acetazolamide", "AcAMT + 3 Cl2 + 2 H2O + 2 NH3 -> Acetazolamide + 5 HCl + NH4Cl", COOL,
      "The thiol chlorinated in water to the sulfonyl chloride, then aminated.", wiki=P["Acetazolamide"], T=0),
    R("3-Chloronitrobenzene", "Nitrobenzene + Cl2 -> mCNB + HCl", FLASK,
      "Nitrobenzene chlorinated over iron chloride.", wiki=P["mCNB"], T=40),
    R("3-Chloroaniline", "mCNB + 3 H2 -> mChloroaniline + 2 H2O", CAT, "The nitro group hydrogenated.", wiki=P["mChloroaniline"],
      cat="Pt", T=80),
    R("Aminochlorobenzenedisulfonamide", "mChloroaniline + 4 HSO3Cl + 4 NH3 -> ACBDS + 2 H2SO4 + 2 HCl + 2 NH4Cl", FLASK,
      "3-Chloroaniline chlorosulfonated twice and both sulfonyl chlorides aminated.", wiki=P["ACBDS"], T=130),
    R("Chlorothiazide", "ACBDS + Formic -> Chlorothiazide + 2 H2O", HEAT,
      "Formic acid closes the amine and a sulfonamide into the benzothiadiazine ring.", wiki=P["Chlorothiazide"], T=150),
    R("Hydrochlorothiazide", "ACBDS + CH2O -> HCTZ + H2O", FLASK,
      "Formaldehyde closes the ring one oxidation level lower.", wiki=P["HCTZ"], T=90),
    R("2,4-Dichlorotoluene", "pChlorotoluene + Cl2 -> DCT24 + HCl", FLASK, "4-Chlorotoluene chlorinated once more on iron chloride, next to the methyl.",
      wiki=P["DCT24"], T=40),
    R("2,4-Dichlorobenzoic Acid", "2 DCT24 + 3 O2 -> 2 DCBA24 + 2 H2O", CAT, "The methyl group oxidised in air.",
      wiki=P["DCBA24"], cat="Co", T=150),
    R("Lasamide", "DCBA24 + 2 HSO3Cl + 2 NH3 -> Lasamide + H2SO4 + HCl + NH4Cl", FLASK,
      "The acid chlorosulfonated and aminated.", wiki=P["Lasamide"], T=140),
    R("Furosemide", "Lasamide + Furfurylamine -> Furosemide + HCl", HEAT,
      "Furfurylamine pushes out the chlorine next to the carboxyl.", wiki=P["Furosemide"], T=130),
    R("Simvastatin", "Lovastatin + MeI -> Simvastatin + HI", FLASK,
      "One more methyl put on lovastatin's side chain, at the carbon beside its ester.", wiki=P["Simvastatin"], T=-30),
    R("Dihydroartemisinin", "4 Artemisinin + NaBH4 + 2 H2O -> 4 Artenimol + NaBO2", COOL,
      "Sodium borohydride reduces the lactone to a lactol without touching the peroxide bridge.", wiki=P["Artenimol"], T=0),
    R("Artemether", "Artenimol + Methanol -> Artemether + H2O", FLASK, "The lactol etherified with methanol in acid.",
      wiki=P["Artemether"], T=20),
    R("Artesunate", "Artenimol + SuccinicAnhydride -> Artesunate", FLASK, "The lactol esterified with succinic anhydride.",
      wiki=P["Artesunate"], T=20),
    R("2,6-Dichlorodiphenylamine", "DCA26 + Iodobenzene -> DCDPA + HI", CAT,
      "A Goldberg coupling over copper.", wiki=P["DCDPA"], cat="Cu", T=200),
    R("Diclofenac", "DCDPA + ClAcCl + H2O -> Diclofenac + 2 HCl", FLASK,
      "The amine chloroacetylated, closed onto the ring by Friedel-Crafts to an oxindole, and the oxindole opened.",
      wiki=P["Diclofenac"], T=160),
    R("Nerolin", "Naphthol2 + Methanol -> Nerolin + H2O", CAT, "2-Naphthol etherified with methanol in acid.",
      wiki=P["Nerolin"], cat="H2SO4", T=100),
    R("Naproxen", "Nerolin + PropionylCl + H2O2 -> Naproxen + HCl + H2O", FLASK,
      "Nerolin propionylated, the ketone rearranged to the propionic acid by a 1,2-aryl shift, and the (S) form kept.",
      wiki=P["Naproxen"], T=60),
    R("Aminophylline", "2 Theophylline + EDA -> Aminophylline", MIX, "Theophylline dissolved in ethylenediamine.",
      wiki=P["Aminophylline"]),
    R("Procaine Penicillin", "Penicillin + Procaine -> ProcainePenG", MIX, "Penicillin crystallised with procaine.",
      wiki=P["ProcainePenG"]),
    R("Benzathine", "2 Benzaldehyde + EDA + 2 H2 -> Benzathine + 2 H2O", CAT,
      "Ethylenediamine condensed with benzaldehyde and the imine hydrogenated.", wiki=P["Benzathine"], cat="Ni", T=80),
    R("Benzathine Penicillin", "2 Penicillin + Benzathine -> BenzathinePenG", MIX,
      "Two penicillins crystallised with one benzathine, an almost insoluble salt.", wiki=P["BenzathinePenG"]),
    R("Morphine from Opium", "Opium + Ca(OH)2 -> Morphine", MIX,
      "Opium extracted with lime water, which keeps morphine dissolved, and the morphine precipitated with ammonium chloride.",
      wiki=P["Morphine"], exact=False),
    R("Codeine from Opium", "Opium + Ethanol -> Codeine", MIX,
      "Codeine, about a tenth as plentiful as morphine, separated from the alcoholic extract.", wiki=P["Codeine"], exact=False),
    R("Papaverine from Opium", "Opium + Benzene -> Papaverine", MIX,
      "Papaverine taken from the opium bases into benzene.", wiki=P["Papaverine"], exact=False),
    R("Pilocarpine", "Jaborandi + Ethanol -> Pilocarpine", MIX, "Jaborandi leaves extracted and the alkaloid crystallised.",
      wiki=P["Pilocarpine"], exact=False),
    R("Physostigmine", "CalabarBean + Ethanol -> Physostigmine", MIX, "The bean's alkaloid extracted (Jobst and Hesse, 1864).",
      wiki=P["Physostigmine"], exact=False),
    R("Colchicine", "AutumnCrocus + Ethanol -> Colchicine", MIX, "Colchicum corms extracted and the alkaloid crystallised.",
      wiki=P["Colchicine"], exact=False),
]

# the four plants arrive with the others the apothecaries send
import authored_content as _C  # noqa: E402
for _m in _C.MILESTONES:
    if _m.on == "Aspirin":
        _m.grant = tuple(_m.grant) + ("Opium", "Jaborandi", "CalabarBean", "AutumnCrocus")
import authored_canon_29  # noqa: E402,F401
