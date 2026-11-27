"""
Curieosity's industrial chemistry, part 21 (see authored_canon.py): canon compounds with no
Wikipedia article of their own, written up with their PubChem page as the reference. Grouped
here: water treatment and papermaking quats, paint and plastics additives, plasticisers,
silicones, fragrances, arylide and DPP pigments, battery electrolyte chemicals, and the
intermediates they need (4-tert-butyltoluene, triacetonamine, the acetoacetarylides).
"""

from authored_canon import S, R, CANON  # noqa: F401
from authored_content import E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR, pubchem)

P = {}


def PC(cas, key, name, formula, state, ref, desc, smiles=None):
    """A compound whose page is on PubChem (by CID, or by name)."""
    P[key] = pubchem(ref)
    S(cas, key, name, formula, state, P[key], desc, smiles=smiles)


# --- already in play under another name, or as the hydrate/salt we have -------------------------
CANON.update({"612-83-9": "DCB", "10424-65-4": "TMAH", "10026-24-1": "CoSO4"})

# --- intermediates ------------------------------------------------------------------------------
P["pChlorotoluene"] = "Chlorotoluene"
S("106-43-4", "pChlorotoluene", "4-Chlorotoluene", "C7H7Cl", "Liquid", P["pChlorotoluene"],
  "The para chlorotoluene, separated from the ortho by distillation and crystallisation: the start of 4-chlorobenzonitrile and of pesticides.",
  smiles="Cc1ccc(Cl)cc1")
PC("98-51-1", "tBuToluene4", "4-tert-Butyltoluene", "C11H16", "Liquid", "4-tert-Butyltoluene",
   "Toluene with a tert-butyl group opposite the methyl: the base of a family of lily-of-the-valley fragrances.",
   "Cc1ccc(cc1)C(C)(C)C")
PC("939-97-9", "TBBA", "4-tert-Butylbenzaldehyde", "C11H14O", "Liquid", "4-tert-Butylbenzaldehyde",
   "The aldehyde behind Lilial and Bourgeonal; BASF makes it by oxidising the toluene at an electrode.", "CC(C)(C)c1ccc(C=O)cc1")
PC("826-36-8", "TAA", "Triacetonamine", "C9H17NO", "Solid", "Triacetonamine",
   "2,2,6,6-Tetramethyl-4-piperidone, made from acetone and ammonia: the ring of the hindered-amine light stabilisers.",
   "CC1(C)CC(=O)CC(C)(C)N1")
PC("2403-88-5", "TMPol", "4-Hydroxy-2,2,6,6-tetramethylpiperidine", "C9H19NO", "Solid", 75471,
   "The alcohol from which the hindered-amine light stabilisers, and the radical TEMPOL, are made.", "CC1(C)CC(O)CC(C)(C)N1")
PC("93-68-5", "AAOT", "Acetoacet-o-toluidide", "C11H13NO2", "Solid", 7154,
   "The coupling half of Pigment Yellow 14.", "CC(=O)CC(=O)Nc1ccccc1C")
PC("92-15-9", "AAOA", "Acetoacet-o-anisidide", "C11H13NO3", "Solid", 7078,
   "The coupling half of Pigment Yellow 74.", "COc1ccccc1NC(=O)CC(C)=O")

P["NH4F"] = "Ammonium_fluoride"
S("12125-01-8", "NH4F", "Ammonium fluoride", "NH4F", "Solid", P["NH4F"],
  "A salt that etches glass; buffered with hydrofluoric acid it strips oxide from silicon wafers.", smiles="[NH4+].[F-]")

# --- the canon compounds -----------------------------------------------------------------------
PC("10192-30-0", "NH4HSO3", "Ammonium bisulfite", "H5NO3S", "Liquid", 56846439,
   "Sold as a solution: an oxygen scavenger for boiler water, and the cooking liquor of ammonia-base sulfite pulping.",
   "[NH4+].OS([O-])=O")
PC("44992-01-0", "AETAC", "Acryloyloxyethyltrimethylammonium chloride", "C8H16ClNO2", "Liquid", 162071,
   "A cationic monomer: copolymerised with acrylamide it makes the flocculants that settle sludge in water treatment.",
   "C[N+](C)(C)CCOC(=O)C=C.[Cl-]")
PC("25265-77-4", "Texanol", "Texanol", "C12H24O3", "Liquid", 6490,
   "The coalescent of latex paint: it softens the polymer particles so they fuse into a film, then slowly evaporates.",
   "CC(C)C(O)C(C)(C)COC(=O)C(C)C")
PC("4719-04-4", "HHT", "Hexahydro-1,3,5-tris(hydroxyethyl)triazine", "C9H21N3O3", "Liquid", 104556,
   "A triazine that releases formaldehyde slowly: a biocide in metalworking fluids, and a hydrogen sulfide scavenger in oil fields.",
   "OCCN1CN(CCO)CN(CCO)C1")
PC("3327-22-8", "CHPTAC", "(3-Chloro-2-hydroxypropyl)trimethylammonium chloride", "C6H15Cl2NO", "Liquid", 18732,
   "It turns starch cationic for papermaking, so the starch clings to the negatively charged fibres.", "C[N+](C)(C)CC(O)CCl.[Cl-]")
PC("3033-77-0", "GTAC", "Glycidyltrimethylammonium chloride", "C6H14ClNO", "Liquid", 18205,
   "The epoxide form of the same quat: it makes guar gum cationic for conditioning shampoos.", "C[N+](C)(C)CC1CO1.[Cl-]")
PC("6386-38-5", "Metilox", "Methyl 3-(3,5-di-tert-butyl-4-hydroxyphenyl)propionate", "C18H28O3", "Solid", 62603,
   "The ester from which the big phenolic antioxidants are built by transesterification.",
   "COC(=O)CCc1cc(c(O)c(c1)C(C)(C)C)C(C)(C)C")
PC("99-63-8", "IPC", "Isophthaloyl chloride", "C8H4Cl2O2", "Solid", 7451,
   "With m-phenylenediamine it polymerises into Nomex, the fireproof aramid of firefighters' suits.", "ClC(=O)c1cccc(c1)C(Cl)=O")
PC("120-55-8", "DEGDB", "Diethylene glycol dibenzoate", "C18H18O5", "Liquid", 8437,
   "A benzoate plasticiser for adhesives, sealants and vinyl flooring.", "O=C(OCCOCCOC(=O)c1ccccc1)c1ccccc1")
PC("2492-26-4", "NaMBT", "Sodium 2-mercaptobenzothiazole", "C7H4NNaS2", "Solid", 24195611,
   "A corrosion inhibitor for copper in antifreeze and cooling water.", "[Na+].[S-]c1nc2ccccc2s1")
PC("53306-54-0", "DPHP", "Bis(2-propylheptyl) phthalate", "C28H46O4", "Liquid", 92344,
   "A heavy phthalate plasticiser for cable sheathing and car interiors.", "CCCCCC(CCC)COC(=O)c1ccccc1C(=O)OCC(CCC)CCCCC")
PC("632-79-1", "TBPA", "Tetrabromophthalic anhydride", "C8Br4O3", "Solid", 12443,
   "A reactive flame retardant, built into polyesters and polyols.", "O=C1OC(=O)c2c(Br)c(Br)c(Br)c(Br)c12")
PC("104-68-7", "DEGPh", "Diethylene glycol monophenyl ether", "C10H14O3", "Liquid", 7715,
   "A slow-evaporating glycol ether for inks, and a dye carrier in polyester dyeing.", "OCCOCCOc1ccccc1")
PC("105-05-5", "pDEB", "1,4-Diethylbenzene", "C10H14", "Liquid", 7734,
   "The desorbent that washes para-xylene off the molecular sieves of the Parex process.", "CCc1ccc(CC)cc1")
PC("105-62-4", "PGDO", "Propylene glycol dioleate", "C39H72O4", "Liquid", 101579,
   "An emollient ester in cosmetics, and a lubricant.", "CCCCCCCC/C=C\\CCCCCCCC(=O)OCC(C)OC(=O)CCCCCCC/C=C\\CCCCCCCC")
PC("107-51-7", "MDM", "Octamethyltrisiloxane", "C8H24O2Si3", "Liquid", 24705,
   "A short linear silicone: a volatile carrier in cosmetics, and a dry-cleaning fluid.", "C[Si](C)(C)O[Si](C)(C)O[Si](C)(C)C")
PC("108-83-8", "DIBK", "Diisobutyl ketone", "C9H18O", "Liquid", 7958,
   "A slow-evaporating solvent for coatings, made alongside MIBK.", "CC(C)CC(=O)CC(C)C")
PC("31795-24-1", "KMeSiliconate", "Potassium methylsiliconate", "CH5KO3Si", "Liquid", 88304764,
   "Brushed onto brick and stone it reacts with carbon dioxide into a water-repellent silicone skin.", "[K+].C[Si](O)(O)[O-]")
PC("927-07-1", "TBPPI", "tert-Butyl peroxypivalate", "C9H18O3", "Liquid", 61238,
   "A radical initiator that works cool, for PVC and low-density polyethylene.", "CC(C)(C)OOC(=O)C(C)(C)C")
PC("1809-19-4", "DBPhosphite", "Dibutyl phosphite", "C8H19O3P", "Liquid", 6327349,
   "A phosphite for flame retardants and lubricant additives.", "CCCCOP(=O)OCCCC")
PC("677-21-4", "TFP", "3,3,3-Trifluoropropene", "C3H3F3", "Gas", 12672,
   "The monomer of fluorosilicone rubbers, which shrug off fuel and oil.", "C=CC(F)(F)F")
PC("80-26-2", "TerpinylAcetate", "alpha-Terpinyl acetate", "C12H20O2", "Liquid", 111037,
   "A cheap lavender-and-bergamot note for soaps and detergents.", "CC(=O)OC(C)(C)C1CC=C(C)CC1")
PC("924-42-5", "NMA", "N-Methylolacrylamide", "C4H7NO2", "Solid", 13543,
   "A self-crosslinking monomer for nonwoven binders and textile finishes.", "OCNC(=O)C=C")
PC("96-22-0", "DEK", "Diethyl ketone", "C5H10O", "Liquid", 7288,
   "3-Pentanone: a solvent, and a building block for vitamin E.", "CCC(=O)CC")
PC("623-03-0", "pCBN", "4-Chlorobenzonitrile", "C7H4ClN", "Solid", 12163,
   "The nitrile from which Pigment Red 254 is built.", "N#Cc1ccc(Cl)cc1")
PC("84632-65-5", "PR254", "Pigment Red 254", "C18H10Cl2N2O2", "Solid", 174375,
   "Ferrari red: a diketopyrrolopyrrole pigment of extreme fastness, for car paint and plastics.",
   "O=C1NC(c2ccc(Cl)cc2)=C2C1=C(NC2=O)c1ccc(Cl)cc1")
PC("100-40-3", "VCH", "4-Vinylcyclohexene", "C8H12", "Liquid", 7499,
   "The Diels-Alder dimer of butadiene, and a step towards styrene and epoxy diluents.", "C=CC1CCC=CC1")
PC("124-26-5", "Stearamide", "Stearamide", "C18H37NO", "Solid", 31292,
   "A slip agent that keeps polyethylene film from sticking to itself.", "CCCCCCCCCCCCCCCCCC(N)=O")
PC("136-52-7", "CoOctoate", "Cobalt(II) 2-ethylhexanoate", "C16H30CoO4", "Liquid", 8696,
   "The cobalt drier of oil paints, and the accelerator that cures polyester resin.",
   "[Co+2].CCCCC(CC)C([O-])=O.CCCCC(CC)C([O-])=O")
PC("52125-53-8", "PGEE", "1-Ethoxy-2-propanol", "C5H12O2", "Liquid", 93269,
   "A glycol ether solvent for paints and inks.", "CCOCC(C)O")
PC("7320-34-5", "TKPP", "Tetrapotassium pyrophosphate", "K4O7P2", "Solid", 16212030,
   "The very soluble builder of liquid detergents.", "[K+].[K+].[K+].[K+].[O-]P([O-])(=O)OP([O-])([O-])=O")
PC("7381-01-3", "SLI", "Sodium lauroyl isethionate", "C14H27NaO5S", "Solid", 87732187,
   "The gentle surfactant of syndet beauty bars.", "[Na+].CCCCCCCCCCCC(=O)OCCS([O-])(=O)=O")
PC("13822-56-5", "APTMS", "(3-Aminopropyl)trimethoxysilane", "C6H17NO3Si", "Liquid", 83756,
   "A silane coupling agent: one end bonds to glass, the other to resin.", "CO[Si](CCCN)(OC)OC")
PC("52829-07-9", "T770", "Bis(2,2,6,6-tetramethyl-4-piperidyl) sebacate", "C28H52N2O4", "Solid", 164282,
   "A hindered-amine light stabiliser (Tinuvin 770): it mops up the radicals sunlight makes in plastics, over and over.",
   "CC1(C)CC(CC(C)(C)N1)OC(=O)CCCCCCCCC(=O)OC1CC(C)(C)NC(C)(C)C1")
PC("6259-76-3", "HexylSalicylate", "Hexyl salicylate", "C13H18O3", "Liquid", 22629,
   "A green, floral salicylate used by the tonne in detergent perfumes.", "CCCCCCOC(=O)c1ccccc1O")
PC("98-73-7", "PTBBA", "4-tert-Butylbenzoic acid", "C11H14O2", "Solid", 7403,
   "A PVC heat-stabiliser salt, and a nucleating agent for polypropylene.", "CC(C)(C)c1ccc(cc1)C(O)=O")
PC("80-54-6", "Lilial", "Lilial", "C14H20O", "Liquid", 228987,
   "Lily of the valley in one molecule, in everything from soap to fine fragrance until the EU banned it from cosmetics in 2022.",
   "CC(Cc1ccc(cc1)C(C)(C)C)C=O")
PC("18127-01-0", "Bourgeonal", "Bourgeonal", "C13H18O", "Liquid", 64832,
   "A lily-of-the-valley aldehyde that human sperm cells swim towards: they carry a smell receptor for it.",
   "CC(C)(C)c1ccc(CCC=O)cc1")
PC("6358-31-2", "PY74", "Pigment Yellow 74", "C18H18N4O6", "Solid", 22829,
   "An arylide yellow: the bright yellow of printing inks and road-marking paint.",
   "COc1ccccc1NC(=O)C(N=Nc1ccc(cc1OC)[N+]([O-])=O)C(C)=O")
PC("5468-75-7", "PY14", "Pigment Yellow 14", "C34H30Cl2N6O4", "Solid", 93006,
   "A diarylide yellow for packaging inks.",
   "CC(=O)C(N=Nc1ccc(cc1Cl)-c1ccc(N=NC(C(C)=O)C(=O)Nc2ccccc2C)c(Cl)c1)C(=O)Nc1ccccc1C")
PC("10380-29-7", "CaNa2EDTA", "Edetate calcium disodium", "C10H12CaN2Na2O8", "Solid", 156591868,
   "A food preservative, and the drip that draws lead out of a poisoned body.")
PC("51566-62-2", "CitronellylNitrile", "Citronellyl nitrile", "C10H17N", "Liquid", 3033030,
   "A sharp, lemony nitrile that holds up in bleach and soap, where citral would fall apart.", "CC(CCC=C(C)C)CC#N")
PC("84-61-7", "DCHP", "Dicyclohexyl phthalate", "C20H26O4", "Solid", 6777,
   "A solid phthalate plasticiser for heat-seal coatings.", "O=C(OC1CCCCC1)c1ccccc1C(=O)OC1CCCCC1")
PC("3470-98-2", "NBP", "N-Butyl-2-pyrrolidone", "C8H15NO", "Liquid", 18984,
   "A solvent brought in to replace the reprotoxic NMP.", "CCCCN1CCCC1=O")
PC("114435-02-8", "FEC", "Fluoroethylene carbonate", "C3H3FO3", "Liquid", 2769656,
   "A few percent in a lithium-ion battery's electrolyte builds a tougher film on the anode.", "FC1COC(=O)O1")
PC("1185-53-1", "TrisHCl", "Tris hydrochloride", "C4H12ClNO3", "Solid", 93573,
   "Half of the biochemistry lab's pH 7-9 buffer.", "Cl.NC(CO)(CO)CO")
PC("1119-34-2", "ArginineHCl", "Arginine hydrochloride", "C6H15ClN4O2", "Solid", 85880,
   "Arginine as sold for supplements and drips.", "Cl.NC(CCCNC(N)=N)C(O)=O")
PC("131-17-9", "DiallylPhthalate", "Diallyl phthalate", "C14H14O4", "Liquid", 8560,
   "It cures into a hard, stable resin for electrical connectors.", "C=CCOC(=O)c1ccccc1C(=O)OCC=C")
PC("1002-62-6", "NaCaprate", "Sodium caprate", "C10H19NaO2", "Solid", 87061374,
   "Sodium decanoate: it loosens the seals between gut cells just enough to let some drugs through.",
   "[Na+].CCCCCCCCCC([O-])=O")
PC("3296-90-0", "BBMP", "2,2-Bis(bromomethyl)-1,3-propanediol", "C5H10Br2O2", "Solid", 18692,
   "Dibromoneopentyl glycol, a reactive flame retardant for polyurethanes and polyesters.", "OCC(CO)(CBr)CBr")
PC("335-05-7", "TfF", "Trifluoromethanesulfonyl fluoride", "CF4O2S", "Gas", 67631,
   "Triflyl fluoride, made by electrochemical fluorination: the source of the triflyl group.", "FC(F)(F)S(F)(=O)=O")
S("90076-65-6", "LiTFSI", "Lithium bis(trifluoromethanesulfonyl)imide", "C2F6LiNO4S2", "Solid", 53440268,
  "LiTFSI: a lithium salt for battery electrolytes that stands heat better than lithium hexafluorophosphate.",
  smiles="[Li+].FC(F)(F)S(=O)(=O)[N-]S(=O)(=O)C(F)(F)F")
P["LiTFSI"] = "https://en.wikipedia.org/?curid=53440268"
PC("13769-81-8", "FeMolybdate", "Iron(III) molybdate", "Fe2Mo3O12", "Solid", 170841777,
   "The Formox catalyst that turns methanol into formaldehyde.")
PC("12049-50-2", "CaTiO3", "Calcium titanate", "CaTiO3", "Solid", 156594499,
   "The mineral perovskite, which gave its name to a whole crystal structure, and to perovskite solar cells.")
PC("20292-08-4", "EHLaurate", "2-Ethylhexyl laurate", "C20H40O2", "Liquid", 89309,
   "A light emollient ester for skin creams.", "CCCCCCCCCCCC(=O)OCC(CC)CCCC")
PC("2174-16-5", "TEASalicylate", "Trolamine salicylate", "C13H21NO6", "Liquid", 25213,
   "The active of odourless rub-on pain relievers.", "OCCN(CCO)CCO.OC(=O)c1ccccc1O")

# --- the reactions ------------------------------------------------------------------------------
E4.reactions += [
    R("Ammonium Fluoride", "NH3 + HF -> NH4F", MIX,
      "Ammonia neutralised with hydrofluoric acid.", wiki=P["NH4F"]),
    R("4-Chlorotoluene", "Toluene + Cl2 -> pChlorotoluene + HCl", FLASK,
      "Toluene chlorinated on the ring; the para isomer is separated from the ortho.", wiki=P["pChlorotoluene"], T=30),
    R("Ammonium Bisulfite", "NH3 + SO2 + H2O -> NH4HSO3", MIX,
      "Sulfur dioxide absorbed in ammonia water.", wiki=P["NH4HSO3"]),
    R("Stearamide", "StearicAcid + NH3 -> Stearamide + H2O", HEAT,
      "Stearic acid heated in ammonia until it gives up water.", wiki=P["Stearamide"], T=200),
    R("Tetrapotassium Pyrophosphate", "4 KOH + 2 H3PO4 -> TKPP + 5 H2O", HEAT,
      "Dipotassium phosphate made from the lye and acid, then calcined until two phosphates join.", wiki=P["TKPP"], T=400),
    R("Calcium Titanate", "CaO + TiO2 -> CaTiO3", HEAT,
      "Lime and titania fired together into the perovskite.", wiki=P["CaTiO3"], T=1200),
]
E5.reactions += [
    R("4-tert-Butyltoluene", "Toluene + Isobutylene -> tBuToluene4", CAT,
      "Toluene alkylated with isobutylene over an acid catalyst; the bulky group goes para.", wiki=P["tBuToluene4"], cat="H2SO4", T=20),
    R("4-tert-Butylbenzaldehyde", "tBuToluene4 + H2O -> TBBA + 2 H2", ECELL,
      "The methyl group oxidised at an anode (in methanol, as BASF does it), while hydrogen bubbles off the cathode.",
      wiki=P["TBBA"], T=40),
    R("Triacetonamine", "3 Acetone + NH3 -> TAA + 2 H2O", MIX,
      "Three acetones and an ammonia condense into the piperidone ring.", wiki=P["TAA"]),
    R("4-Hydroxy-TMP", "TAA + H2 -> TMPol", CAT,
      "Triacetonamine's ketone hydrogenated.", wiki=P["TMPol"], cat="Ni", T=100),
    R("Acetoacet-o-toluidide", "Diketene + oToluidine -> AAOT", MIX,
      "o-Toluidine acetoacetylated with diketene.", wiki=P["AAOT"]),
    R("Acetoacet-o-anisidide", "Diketene + oAnisidine -> AAOA", MIX,
      "o-Anisidine acetoacetylated with diketene.", wiki=P["AAOA"]),
    R("AETAC", "DMAEA + CH3Cl -> AETAC", MIX,
      "Dimethylaminoethyl acrylate quaternised with methyl chloride.", wiki=P["AETAC"]),
    R("Texanol", "3 Isobutyraldehyde -> Texanol", FLASK,
      "Isobutyraldehyde dimerised by aldol and the aldol esterified by a third aldehyde (Tishchenko), all in base.",
      wiki=P["Texanol"], T=50),
    R("Triazine Biocide", "3 MEA + 3 CH2O -> HHT + 3 H2O", MIX,
      "Ethanolamine and formaldehyde condense into a six-membered triazine ring.", wiki=P["HHT"]),
    R("CHPTAC", "Me3N + Epichlorohydrin + HCl -> CHPTAC", MIX,
      "Trimethylamine hydrochloride opens epichlorohydrin.", wiki=P["CHPTAC"]),
    R("GTAC", "CHPTAC + NaOH -> GTAC + NaCl + H2O", MIX,
      "Caustic closes the chlorohydrin back to an epoxide.", wiki=P["GTAC"]),
    R("Metilox", "DTBP26 + MethylAcrylate -> Metilox", FLASK,
      "2,6-Di-tert-butylphenol adds to methyl acrylate in base, para to the hydroxyl.", wiki=P["Metilox"], T=110),
    R("Isophthaloyl Chloride", "IPA + 2 SOCl2 -> IPC + 2 SO2 + 2 HCl", FLASK,
      "Isophthalic acid on thionyl chloride.", wiki=P["IPC"], T=80),
    R("Diethylene Glycol Dibenzoate", "DEG + 2 BenzoicAcid -> DEGDB + 2 H2O", FLASK,
      "Diethylene glycol esterified with benzoic acid.", wiki=P["DEGDB"], T=200),
    R("Sodium MBT", "MBT + NaOH -> NaMBT + H2O", MIX,
      "Mercaptobenzothiazole dissolved in caustic soda.", wiki=P["NaMBT"]),
    R("DPHP", "PhthalicAnhydride + 2 PropylHeptanol -> DPHP + H2O", FLASK,
      "Phthalic anhydride esterified with 2-propylheptanol.", wiki=P["DPHP"], T=200),
    R("Tetrabromophthalic Anhydride", "PhthalicAnhydride + 4 Br2 + Oleum -> TBPA + 4 HBr + Oleum", FLASK,
      "Phthalic anhydride brominated in oleum.", wiki=P["TBPA"], T=60),
    R("Diethylene Glycol Phenyl Ether", "Phenol + 2 EO -> DEGPh", PRESS,
      "Phenol ethoxylated twice.", wiki=P["DEGPh"], T=150),
    R("p-Diethylbenzene", "DEB -> pDEB", COLUMN,
      "The para isomer taken out of mixed diethylbenzenes by adsorption and distillation.", wiki=P["pDEB"]),
    R("Propylene Glycol Dioleate", "PG + 2 OleicAcid -> PGDO + 2 H2O", FLASK,
      "Propylene glycol esterified with oleic acid.", wiki=P["PGDO"], T=200),
    R("Octamethyltrisiloxane", "2 Me3SiCl + Me2SiCl2 + 2 H2O -> MDM + 4 HCl", MIX,
      "Two end-capping silanes and one chain silane hydrolysed together.", wiki=P["MDM"]),
    R("Diisobutyl Ketone", "3 Acetone + 2 H2 -> DIBK + 2 H2O", HIGHP,
      "Acetone condensed three times and hydrogenated over palladium.", wiki=P["DIBK"], cat="Pd", T=150),
    R("Potassium Methylsiliconate", "MeSiCl3 + 4 KOH -> KMeSiliconate + 3 KCl + H2O", MIX,
      "Methyltrichlorosilane hydrolysed in potash lye.", wiki=P["KMeSiliconate"]),
    R("tert-Butyl Peroxypivalate", "TBHP + PivaloylCl + NaOH -> TBPPI + NaCl + H2O", COOL,
      "tert-Butyl hydroperoxide acylated with pivaloyl chloride, kept cold.", wiki=P["TBPPI"], T=5),
    R("Dibutyl Phosphite", "PCl3 + 3 Butanol -> DBPhosphite + BuCl + 2 HCl", COOL,
      "Phosphorus trichloride and butanol with no base; one butyl leaves as butyl chloride.", wiki=P["DBPhosphite"], T=10),
    R("3,3,3-Trifluoropropene", "CCl4 + Ethylene + 3 HF -> TFP + 4 HCl", CAT,
      "Carbon tetrachloride added to ethylene, and the chlorines swapped for fluorine over chromia.", wiki=P["TFP"], cat="Cr2O3", T=300),
    R("Terpinyl Acetate", "aTerpineol + AceticAnhydride -> TerpinylAcetate + AcOH", FLASK,
      "Terpineol acetylated.", wiki=P["TerpinylAcetate"], T=60),
    R("N-Methylolacrylamide", "Acrylamide + CH2O -> NMA", MIX,
      "Acrylamide and formaldehyde in mild base.", wiki=P["NMA"]),
    R("Diethyl Ketone", "2 Propionic -> DEK + CO2 + H2O", HEAT,
      "Two propionic acids ketonised over a hot oxide, losing carbon dioxide and water.", wiki=P["DEK"], T=400),
    R("4-Chlorobenzonitrile", "2 pChlorotoluene + 2 NH3 + 3 O2 -> 2 pCBN + 6 H2O", CRACKER,
      "4-Chlorotoluene ammoxidised: ammonia and air turn the methyl group into a nitrile.", wiki=P["pCBN"], cat="V2O5", T=400),
    R("4-Vinylcyclohexene", "2 Butadiene -> VCH", HEAT,
      "Butadiene dimerised by a Diels-Alder reaction.", wiki=P["VCH"], T=140),
    R("Cobalt Octoate", "CoOH2 + 2 EHAcid -> CoOctoate + 2 H2O", MIX,
      "Cobalt hydroxide dissolved in 2-ethylhexanoic acid.", wiki=P["CoOctoate"]),
    R("Propylene Glycol Ethyl Ether", "Ethanol + PO -> PGEE", PRESS,
      "Ethanol opens propylene oxide.", wiki=P["PGEE"], T=120),
    R("Sodium Lauroyl Isethionate", "LauricAcid + NaIsethionate -> SLI + H2O", HEAT,
      "Lauric acid esterified directly with sodium isethionate.", wiki=P["SLI"], T=230),
    R("Aminopropyltrimethoxysilane", "TMOS_H + Allylamine -> APTMS", CAT,
      "Trimethoxysilane added across allylamine's double bond on platinum.", wiki=P["APTMS"], cat="Pt", T=100),
    R("Tinuvin 770", "2 TMPol + SebacicAcid -> T770 + 2 H2O", FLASK,
      "The hindered piperidinol esterified at both ends of sebacic acid.", wiki=P["T770"], T=180),
    R("Hexyl Salicylate", "Salicylic + Hexanol -> HexylSalicylate + H2O", FLASK,
      "Salicylic acid esterified with hexanol.", wiki=P["HexylSalicylate"], T=150),
    R("4-tert-Butylbenzoic Acid", "2 tBuToluene4 + 3 O2 -> 2 PTBBA + 2 H2O", CAT,
      "4-tert-Butyltoluene oxidised in air with a cobalt catalyst.", wiki=P["PTBBA"], cat="CoOctoate", T=150),
    R("Pigment Yellow 74", "MethoxyNitroaniline + NaNO2 + HCl + AAOA -> PY74 + NaCl + 2 H2O", COOL,
      "2-Methoxy-4-nitroaniline diazotised and coupled to acetoacet-o-anisidide.", wiki=P["PY74"], T=5),
    R("Pigment Yellow 14", "DCB + 2 NaNO2 + 2 HCl + 2 AAOT -> PY14 + 2 NaCl + 4 H2O", COOL,
      "Dichlorobenzidine diazotised at both ends and coupled to two acetoacet-o-toluidides.", wiki=P["PY14"], T=5),
    R("Edetate Calcium Disodium", "EDTA + 2 NaOH + CaCO3 -> CaNa2EDTA + 3 H2O + CO2", MIX,
      "EDTA half neutralised with caustic and loaded with calcium from chalk.", wiki=P["CaNa2EDTA"]),
    R("Citronellyl Nitrile", "Citronellal + NH2OH -> CitronellylNitrile + 2 H2O", FLASK,
      "Citronellal's oxime dehydrated to the nitrile.", wiki=P["CitronellylNitrile"], T=120),
    R("Dicyclohexyl Phthalate", "PhthalicAnhydride + 2 Cyclohexanol -> DCHP + H2O", FLASK,
      "Phthalic anhydride esterified with cyclohexanol.", wiki=P["DCHP"], T=180),
    R("Tris Hydrochloride", "Tris + HCl -> TrisHCl", MIX,
      "Tris neutralised with hydrochloric acid.", wiki=P["TrisHCl"]),
    R("Arginine Hydrochloride", "Arginine + HCl -> ArginineHCl", MIX,
      "Arginine neutralised with hydrochloric acid.", wiki=P["ArginineHCl"]),
    R("Diallyl Phthalate", "PhthalicAnhydride + 2 AllylAlcohol -> DiallylPhthalate + H2O", FLASK,
      "Phthalic anhydride esterified with allyl alcohol.", wiki=P["DiallylPhthalate"], T=140),
    R("Sodium Caprate", "Decanoic + NaOH -> NaCaprate + H2O", MIX,
      "Decanoic acid neutralised with caustic soda.", wiki=P["NaCaprate"]),
    R("Dibromoneopentyl Glycol", "Pentaerythritol + 2 HBr -> BBMP + 2 H2O", FLASK,
      "Two of pentaerythritol's four hydroxyls swapped for bromine.", wiki=P["BBMP"], T=120),
    R("2-Ethylhexyl Laurate", "LauricAcid + 2EH -> EHLaurate + H2O", FLASK,
      "Lauric acid esterified with 2-ethylhexanol.", wiki=P["EHLaurate"], T=200),
    R("Trolamine Salicylate", "TEA + Salicylic -> TEASalicylate", MIX,
      "Salicylic acid neutralised with triethanolamine.", wiki=P["TEASalicylate"]),
    R("Iron Molybdate", "Hematite + 3 MoO3 -> FeMolybdate", HEAT,
      "Iron and molybdenum oxides calcined together.", wiki=P["FeMolybdate"], T=500),
]
E6.reactions += [
    R("Lilial", "TBBA + Propanal + H2 -> Lilial + H2O", CAT,
      "4-tert-Butylbenzaldehyde condensed with propanal and the double bond hydrogenated.", wiki=P["Lilial"], cat="Pd", T=100),
    R("Bourgeonal", "TBBA + Acetaldehyde + H2 -> Bourgeonal + H2O", CAT,
      "The same aldehyde condensed with acetaldehyde and hydrogenated.", wiki=P["Bourgeonal"], cat="Pd", T=100),
    R("Pigment Red 254", "2 pCBN + DiPS -> PR254 + 2 Isopropanol", FLASK,
      "Two 4-chlorobenzonitriles condensed onto diisopropyl succinate in strong base: the DPP ring closes twice.",
      wiki=P["PR254"], T=100),
    R("N-Butylpyrrolidone", "GBL + Butylamine -> NBP + H2O", HEAT,
      "gamma-Butyrolactone opened by butylamine and closed again as the lactam.", wiki=P["NBP"], T=250),
    R("Fluoroethylene Carbonate", "EthyleneCarbonate + F2 -> FEC + HF", COOL,
      "Ethylene carbonate fluorinated with diluted fluorine.", wiki=P["FEC"], T=20),
    R("Triflyl Fluoride", "MsCl + 4 HF -> TfF + 3 H2 + HCl", ECELL,
      "Simons electrochemical fluorination: in liquid hydrogen fluoride every hydrogen and the chlorine are swapped for fluorine.",
      wiki=P["TfF"], T=10),
    R("LiTFSI", "2 TfF + 3 NH3 + LiOH -> LiTFSI + 2 NH4F + H2O", FLASK,
      "Two triflyl groups joined on one nitrogen with ammonia, and the imide taken up as its lithium salt.",
      wiki=P["LiTFSI"], T=20),
]

# Milestones for the stretches this part lengthened (messages only).
import authored_content as _C  # noqa: E402
from gen_authored import Milestone  # noqa: E402
_C.MILESTONES += [
    Milestone("T770", message="Plastics that survive the sun: hindered amines (1970s) catch the radicals that light makes, and are given back to catch more."),
    Milestone("BuLi", message="Butyllithium starts the 'living' anionic polymerisations Michael Szwarc described in 1956: chains that grow until told to stop, and so the block copolymers of shoe soles and road asphalt."),
]

import authored_canon_22  # noqa: E402,F401
