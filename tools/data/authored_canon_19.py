"""
Curieosity's industrial chemistry, part 19 (see authored_canon.py): the canon records that were
set aside as doubtful, repaired. Their identity is taken from the CAS-sourced structure (SMILES
and PubChem CID), not from the scraped formula or article link, which pointed elsewhere; where a
compound has no Wikipedia article of its own its page links PubChem. Also the two ethanolamines
the canon list missed, and the doubtful records that turned out to be compounds already in play.
"""

from authored_canon import S, R, CANON  # noqa: F401
from authored_content import E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR, pubchem)

# --- doubtful records that are compounds already in play (or their hydrates) ---------------
CANON.update({"87-62-7": "Xylidine26", "482-89-3": "Indigo", "3333-67-3": "NiCO3", "7446-20-0": "ZnSO4",
              "7632-04-4": "Perborate", "6153-56-6": "Oxalic",
              "3486-35-9": "Calamine"})

# --- the ethanolamines ------------------------------------------------------------------------
S("111-42-2", "DEA", "Diethanolamine", "C4H11NO2", "Liquid", "Diethanolamine",
  "Ethanolamine with a second hydroxyethyl arm: a gas-scrubbing amine and the base of the coconut diethanolamides in shampoo.",
  smiles="OCCNCCO")
S("102-71-6", "TEA", "Triethanolamine", "C6H15NO3", "Liquid", "Triethanolamine",
  "Three hydroxyethyl arms on one nitrogen: the base of cosmetic creams and soaps, a cement grinding aid and a gas scrubber.",
  smiles="OCCN(CCO)CCO")

# --- the repaired records ---------------------------------------------------------------------
P = {}  # key -> PubChem page, for the reactions that make them


def SP(cas, key, name, formula, state, cid, desc, smiles):
    P[key] = pubchem(cid)
    S(cas, key, name, formula, state, P[key], desc, smiles=smiles)


SP("50-01-1", "GuHCl", "Guanidine hydrochloride", "CH6ClN3", "Solid", 5742,
   "Guanidinium chloride, which unfolds proteins in solution: biochemists denature them with it, and it eases one rare nerve-muscle disease.",
   "Cl.NC(N)=N")
SP("108-30-5", "SuccinicAnhydride", "Succinic anhydride", "C4H4O3", "Solid", 7922,
   "The ring-closed anhydride of succinic acid: it puts succinyl groups on starch, proteins and drugs.", "O=C1CCC(=O)O1")
SP("591-27-5", "Aminophenol3", "3-Aminophenol", "C6H7NO", "Solid", 11568,
   "m-Aminophenol: a coupler in hair dyes, and the starting point of the tuberculosis drug PAS.", "Nc1cccc(O)c1")
SP("87-90-1", "TCCA", "Trichloroisocyanuric acid", "C3Cl3N3O3", "Solid", 6909,
   "The slow-dissolving chlorine tablets of swimming pools.", "ClN1C(=O)N(Cl)C(=O)N(Cl)C1=O")
SP("123-03-5", "CPC", "Cetylpyridinium chloride", "C21H38ClN", "Solid", 31239,
   "The antiseptic of many mouthwashes and throat lozenges.", "CCCCCCCCCCCCCCCC[n+]1ccccc1.[Cl-]")
SP("57-09-0", "CTAB", "Cetrimonium bromide", "C19H42BrN", "Solid", 5974,
   "A cationic surfactant and antiseptic, and the template that shapes gold nanorods and mesoporous silica.",
   "CCCCCCCCCCCCCCCC[N+](C)(C)C.[Br-]")
SP("92-06-8", "mTerphenyl", "m-Terphenyl", "C18H14", "Solid", 7076,
   "Three benzene rings joined in a bent row; with its isomers, a heat-transfer fluid stable to 400 C.",
   "c1ccc(cc1)-c1cccc(c1)-c1ccccc1")
SP("6303-21-5", "H3PO2", "Hypophosphorous acid", "H3PO2", "Liquid", 6326996,
   "A strong reducing acid: it plates nickel onto plastics without electricity.", "O[PH2]=O")
SP("1762-95-4", "NH4SCN", "Ammonium thiocyanate", "CH4N2S", "Solid", 13417437,
   "A salt that chills water as it dissolves; used in weedkillers, photography and electroplating.", "[NH4+].[S-]C#N")
SP("1863-63-4", "NH4Benzoate", "Ammonium benzoate", "C7H9NO2", "Solid", 10920587,
   "A preservative, and a corrosion inhibitor in antifreeze and packaging.", "[NH4+].[O-]C(=O)c1ccccc1")
SP("10124-65-9", "KLaurate", "Potassium laurate", "C12H23KO2", "Solid", 131864670,
   "A soft potassium soap, the backbone of liquid soaps.", "CCCCCCCCCCCC(=O)[O-].[K+]")
SP("593-29-3", "KStearate", "Potassium stearate", "C18H35KO2", "Solid", 87059166,
   "A potassium soap that gives shaving cream its body.", "CCCCCCCCCCCCCCCCCC(=O)[O-].[K+]")
SP("120-93-4", "Imidazolidinone", "2-Imidazolidinone", "C3H6N2O", "Solid", 8453,
   "Ethyleneurea: it mops up formaldehyde in resins and keeps cotton from creasing.", "O=C1NCCN1")
SP("80-73-9", "DMI", "1,3-Dimethyl-2-imidazolidinone", "C5H10N2O", "Liquid", 6661,
   "A polar, high-boiling solvent, a safer stand-in for the carcinogen HMPA.", "CN1CCN(C)C1=O")
SP("616-47-7", "MeImidazole1", "1-Methylimidazole", "C4H6N2", "Liquid", 1390,
   "A base and catalyst, and the parent of the imidazolium ionic liquids.", "Cn1ccnc1")
SP("763-32-6", "Isoprenol", "Isoprenol", "C5H10O", "Liquid", 12988,
   "3-Methyl-3-buten-1-ol, BASF's building block for citral and from it vitamin A, menthol and the ionones.", "CC(=C)CCO")
SP("97-95-0", "EthylButanol", "2-Ethyl-1-butanol", "C6H14O", "Liquid", 7358,
   "A branched six-carbon alcohol for plasticiser esters and solvents.", "CCC(CC)CO")
SP("592-42-7", "Hexadiene15", "1,5-Hexadiene", "C6H10", "Liquid", 11598,
   "Biallyl: a comonomer and crosslinker for polyolefins.", "C=CCCC=C")
SP("558-30-5", "IBO", "Isobutylene oxide", "C4H8O", "Liquid", 11208,
   "2,2-Dimethyloxirane, an epoxide for speciality glycols and resins.", "CC1(C)CO1")
SP("75-55-8", "Propylenimine", "2-Methylaziridine", "C3H7N", "Liquid", 6377,
   "Propylenimine, a strained three-membered ring that crosslinks coatings, inks and textile finishes.", "CC1CN1")
SP("30424-08-9", "DVBDO", "Divinylbenzene dioxide", "C10H10O2", "Liquid", 86071,
   "A thin diepoxide that cures into hard, heat-resistant resins.", "C1OC1c1ccc(cc1)C1CO1")
SP("623-84-7", "PGDA", "Propylene glycol diacetate", "C7H12O4", "Liquid", 12198,
   "A mild ester solvent for inks, coatings and flavours.", "CC(COC(C)=O)OC(C)=O")
SP("2358-84-1", "DEGDMA", "Diethylene glycol dimethacrylate", "C12H18O5", "Liquid", 16891,
   "A crosslinking monomer of dental composites and hard acrylics.", "CC(=C)C(=O)OCCOCCOC(=O)C(C)=C")
SP("26447-10-9", "NH4XS", "Ammonium xylenesulfonate", "C8H13NO3S", "Solid", 33512,
   "A hydrotrope: it keeps the other ingredients of liquid detergents dissolved.", "Cc1ccc(c(C)c1)S(=O)(=O)[O-].[NH4+]")
SP("57352-34-8", "EBSA", "4-Ethylbenzenesulfonic acid", "C8H10O3S", "Liquid", 7402,
   "A strong organic acid: a resin-curing catalyst, and as its sodium salt a hydrotrope.", "CCc1ccc(cc1)S(O)(=O)=O")
SP("128-44-9", "NaSaccharin", "Sodium saccharin", "C7H4NNaO3S", "Solid", 24181110,
   "Saccharin as sold: the sodium salt dissolves readily, and it is what sweetens a tabletop packet.",
   "[Na+].O=C1[N-]S(=O)(=O)c2ccccc12")
SP("1478-61-1", "BPAF", "Bisphenol AF", "C15H10F6O2", "Solid", 73864,
   "Bisphenol A's fluorinated cousin: the crosslinker that cures fluoroelastomer seals.",
   "OC1=CC=C(C=C1)C(C1=CC=C(O)C=C1)(C(F)(F)F)C(F)(F)F")
SP("4620-70-6", "TBAE", "2-(tert-Butylamino)ethanol", "C6H15NO", "Liquid", 78361,
   "A hindered amine that pulls hydrogen sulfide out of gas streams while letting carbon dioxide through.", "CC(C)(C)NCCO")
SP("4985-85-7", "APDEA", "N-(3-Aminopropyl)diethanolamine", "C7H18N2O2", "Liquid", 21088,
   "A diamine-diol for polyurethane catalysts and epoxy hardeners.", "NCCCN(CCO)CCO")
SP("693-05-0", "MAPN", "3-(Methylamino)propionitrile", "C4H8N2", "Liquid", 69656,
   "An intermediate for amine catalysts and drugs built on a three-carbon chain.", "CNCCC#N")
SP("116-17-6", "TIPP", "Triisopropyl phosphite", "C9H21O3P", "Liquid", 8304,
   "A phosphite ester for flame retardants and the Michaelis-Arbuzov reaction.", "CC(C)OP(OC(C)C)OC(C)C")
SP("762-04-9", "DEPhosphite", "Diethyl phosphite", "C4H11O3P", "Liquid", 6327654,
   "A starting point for organophosphorus flame retardants and herbicides.", "CCOP(=O)OCC")
SP("122-40-7", "AmylCinnamal", "Amylcinnamaldehyde", "C14H18O", "Liquid", 31209,
   "Jasmine aldehyde: the cheap backbone of jasmine notes in soaps and detergents.", "CCCCC/C(=C/c1ccccc1)C=O")
SP("16409-43-1", "RoseOxide", "Rose oxide", "C10H18O", "Liquid", 27866,
   "The rose and lychee note of Bulgarian rose oil and Gewurztraminer wine.", "CC1CCOC(C1)C=C(C)C")
SP("104-67-6", "Undecalactone", "gamma-Undecalactone", "C11H20O2", "Liquid", 7714,
   "'Aldehyde C-14', the peach lactone that gave Guerlain's Mitsouko (1919) its skin-like fruitiness.", "CCCCCCCC1CCC(=O)O1")
SP("137-03-1", "HeptylCyclopentanone", "2-Heptylcyclopentanone", "C12H22O", "Liquid", 8710,
   "A fruity, jasmine-like fragrance ketone.", "CCCCCCCC1CCCC1=O")
SP("97-52-9", "MethoxyNitroaniline", "2-Methoxy-4-nitroaniline", "C7H8N2O3", "Solid", 7337,
   "The diazo half of Pigment Yellow 74, the yellow of much printing ink.", "COc1cc(ccc1N)[N+](=O)[O-]")
SP("611-92-7", "Centralite2", "Centralite II", "C15H16N2O", "Solid", 11917,
   "1,3-Dimethyl-1,3-diphenylurea: it soaks up the acids that would otherwise decompose smokeless powder in storage.",
   "CN(C(=O)N(C)c1ccccc1)c1ccccc1")
SP("5700-49-2", "EDDI", "Ethylenediamine dihydroiodide", "C2H10I2N2", "Solid", 21921,
   "EDDI: iodine for cattle feed, against goitre and foot rot.", "NCCN.I.I")
SP("13492-26-7", "KH2PO3", "Potassium phosphite", "H2KO3P", "Solid", 6331884,
   "A systemic fungicide against downy mildews and Phytophthora, sprayed on crops like a fertiliser.", "[K+].OP([O-])=O")
SP("56-37-1", "TEBA", "Benzyltriethylammonium chloride", "C13H22ClN", "Solid", 66133,
   "The phase-transfer catalyst that ferries anions from water into organic solvents.", "CC[N+](CC)(CC)Cc1ccccc1.[Cl-]")
SP("1100-88-5", "BTPPC", "Benzyltriphenylphosphonium chloride", "C25H22ClP", "Solid", 70671,
   "The Wittig salt that turns aldehydes into stilbenes.", "C(c1ccccc1)[P+](c1ccccc1)(c1ccccc1)c1ccccc1.[Cl-]")
SP("2094-98-6", "ACHN", "1,1'-Azobis(cyclohexanecarbonitrile)", "C14H20N4", "Solid", 74978,
   "A radical initiator that holds out to higher temperatures than AIBN, for polymerisations in hot solvents.",
   "N#CC1(CCCCC1)N=NC1(C#N)CCCCC1")
SP("4065-45-6", "BP4", "Sulisobenzone", "C14H12O6S", "Solid", 19988,
   "Benzophenone-4, a water-soluble UV filter for sunscreens and for keeping shampoo colours from fading.",
   "COc1cc(O)c(cc1S(O)(=O)=O)C(=O)c1ccccc1")
SP("2717-15-9", "TEAOleate", "Triethanolamine oleate", "C24H49NO5", "Liquid", 17619,
   "A soap of oleic acid and triethanolamine: the emulsifier in creams, polishes and cutting oils.",
   "OCCN(CCO)CCO.CCCCCCCC/C=C\\CCCCCCCC(O)=O")
SP("693-04-9", "BuMgCl", "Butylmagnesium chloride", "C4H9ClMg", "Liquid", 101837,
   "A Grignard reagent, sold in solution: a butyl group ready to add to carbonyls.", "CCCC[Mg]Cl")

# --- the reactions ------------------------------------------------------------------------------
E5.reactions += [
    R("Diethanolamine", "MEA + EO -> DEA", PRESS,
      "Ethylene oxide added to ethanolamine; the plant sets the ammonia ratio to make more of the second and third adducts.",
      wiki="Diethanolamine", T=100),
    R("Triethanolamine", "DEA + EO -> TEA", PRESS,
      "A third ethylene oxide caps the amine.", wiki="Triethanolamine", T=100),
    R("Guanidine Hydrochloride", "Guanidine + HCl -> GuHCl", MIX,
      "Guanidine neutralised with hydrochloric acid.", wiki=P["GuHCl"]),
    R("Succinic Anhydride", "Succinic -> SuccinicAnhydride + H2O", HEAT,
      "Succinic acid heated until it gives up water and closes into a ring.", wiki=P["SuccinicAnhydride"], T=250),
    R("3-Aminophenol", "Resorcinol + NH3 -> Aminophenol3 + H2O", PRESS,
      "Resorcinol heated with ammonia under pressure trades one hydroxyl for an amino group.", wiki=P["Aminophenol3"], T=200),
    R("Trichloroisocyanuric Acid", "CyanuricAcid + 3 Cl2 + 3 NaOH -> TCCA + 3 NaCl + 3 H2O", COOL,
      "Cyanuric acid in caustic soda, chlorinated at all three nitrogens in the cold.", wiki=P["TCCA"], T=10),
    R("Cetylpyridinium Chloride", "Pyridine + CetylAlcohol + HCl -> CPC + H2O", FLASK,
      "Cetyl chloride, made in the pot from cetyl alcohol, quaternises pyridine.", wiki=P["CPC"], T=120),
    R("Cetrimonium Bromide", "CetylAlcohol + HBr + Me3N -> CTAB + H2O", FLASK,
      "Cetyl bromide from the alcohol and hydrobromic acid, then trimethylamine.", wiki=P["CTAB"], T=100),
    R("m-Terphenyl", "Biphenyl + Benzene -> mTerphenyl + H2", HEAT,
      "Benzene and biphenyl pyrolysed together: the terphenyls are the heavy by-product of making biphenyl.", wiki=P["mTerphenyl"], T=750),
    R("Hypophosphorous Acid", "2 NaH2PO2 + H2SO4 -> 2 H3PO2 + Na2SO4", FLASK,
      "Sodium hypophosphite acidified, and the free acid concentrated under vacuum.", wiki=P["H3PO2"]),
    R("Ammonium Thiocyanate", "CS2 + 2 NH3 -> NH4SCN + H2S", PRESS,
      "Carbon disulfide and ammonia heated under pressure, by way of ammonium dithiocarbamate.", wiki=P["NH4SCN"], T=110),
    R("Ammonium Benzoate", "BenzoicAcid + NH3 -> NH4Benzoate", MIX,
      "Benzoic acid neutralised with ammonia.", wiki=P["NH4Benzoate"]),
    R("Potassium Laurate", "LauricAcid + KOH -> KLaurate + H2O", MIX,
      "Lauric acid saponified with potash lye.", wiki=P["KLaurate"]),
    R("Potassium Stearate", "StearicAcid + KOH -> KStearate + H2O", MIX,
      "Stearic acid saponified with potash lye.", wiki=P["KStearate"]),
    R("Ethyleneurea", "EDA + Urea -> Imidazolidinone + 2 NH3", HEAT,
      "Ethylenediamine and urea heated together; ammonia leaves as the ring closes.", wiki=P["Imidazolidinone"], T=200),
    R("DMI", "Imidazolidinone + 2 CH2O + 2 Formic -> DMI + 2 CO2 + 2 H2O", FLASK,
      "Ethyleneurea methylated on both nitrogens by formaldehyde and formic acid (Eschweiler-Clarke).", wiki=P["DMI"], T=100),
    R("1-Methylimidazole", "Glyoxal + CH2O + NH3 + Methylamine -> MeImidazole1 + 3 H2O", MIX,
      "Radziszewski's ring-forming condensation, with methylamine in place of one ammonia.", wiki=P["MeImidazole1"]),
    R("Isoprenol", "Isobutylene + CH2O -> Isoprenol", PRESS,
      "Isobutylene and formaldehyde joined by a heat-driven Prins (ene) reaction.", wiki=P["Isoprenol"], T=250),
    R("2-Ethylbutanol", "Butanal + Acetaldehyde + 2 H2 -> EthylButanol + H2O", CAT,
      "Butanal and acetaldehyde condensed, and the unsaturated aldehyde hydrogenated.", wiki=P["EthylButanol"], cat="Ni", T=120),
    R("1,5-Hexadiene", "2 AllylChloride + Mg -> Hexadiene15 + MgCl2", FLASK,
      "Allyl chloride coupled by magnesium: the allyl Grignard attacks a second allyl chloride.", wiki=P["Hexadiene15"]),
    R("Isobutylene Oxide", "Isobutylene + Cl2 + 2 NaOH -> IBO + 2 NaCl + H2O", FLASK,
      "Isobutylene chlorohydrin, closed to the epoxide with caustic.", wiki=P["IBO"], T=30),
    R("Propylenimine", "MIPA + H2SO4 + 2 NaOH -> Propylenimine + Na2SO4 + 3 H2O", FLASK,
      "Wenker's method: the amino alcohol's sulfate ester closed into the ring by caustic.", wiki=P["Propylenimine"], T=100),
    R("Divinylbenzene Dioxide", "DVB + 2 H2O2 -> DVBDO + 2 H2O", FLASK,
      "Both vinyl groups epoxidised with hydrogen peroxide.", wiki=P["DVBDO"], T=40),
    R("Propylene Glycol Diacetate", "PG + 2 AcOH -> PGDA + 2 H2O", FLASK,
      "Propylene glycol esterified twice with acetic acid.", wiki=P["PGDA"], T=120),
    R("DEG Dimethacrylate", "DEG + 2 MethacrylicAcid -> DEGDMA + 2 H2O", FLASK,
      "Diethylene glycol esterified at both ends with methacrylic acid.", wiki=P["DEGDMA"], T=110),
    R("Ammonium Xylenesulfonate", "mXylene + H2SO4 + NH3 -> NH4XS + H2O", FLASK,
      "Xylene sulfonated and neutralised with ammonia.", wiki=P["NH4XS"], T=100),
    R("Ethylbenzenesulfonic Acid", "Ethylbenzene + H2SO4 -> EBSA + H2O", FLASK,
      "Ethylbenzene sulfonated, para to the ethyl group.", wiki=P["EBSA"], T=100),
    R("Sodium Saccharin", "Saccharin + NaOH -> NaSaccharin + H2O", MIX,
      "Saccharin neutralised with caustic soda.", wiki=P["NaSaccharin"]),
    R("Bisphenol AF", "2 Phenol + HFA -> BPAF + H2O", FLASK,
      "Phenol condensed with hexafluoroacetone, as bisphenol A is with acetone.", wiki=P["BPAF"], T=100),
    R("tert-Butylaminoethanol", "tBuNH2 + EO -> TBAE", PRESS,
      "tert-Butylamine opens ethylene oxide.", wiki=P["TBAE"], T=80),
    R("Aminopropyldiethanolamine", "DEA + Acrylonitrile + 2 H2 -> APDEA", CAT,
      "Diethanolamine added across acrylonitrile, and the nitrile hydrogenated to the amine.", wiki=P["APDEA"], cat="Ni", T=100),
    R("Methylaminopropionitrile", "Methylamine + Acrylonitrile -> MAPN", MIX,
      "Methylamine adds across acrylonitrile's double bond.", wiki=P["MAPN"]),
    R("Triisopropyl Phosphite", "PCl3 + 3 Isopropanol -> TIPP + 3 HCl", FLASK,
      "Phosphorus trichloride and isopropanol, with an amine to take up the hydrogen chloride.", wiki=P["TIPP"], T=10),
    R("Diethyl Phosphite", "PCl3 + 3 Ethanol -> DEPhosphite + EtCl + 2 HCl", COOL,
      "Phosphorus trichloride and ethanol with no base: the third ethyl group leaves as ethyl chloride.", wiki=P["DEPhosphite"], T=10),
    R("Jasminaldehyde", "Benzaldehyde + Heptanal -> AmylCinnamal + H2O", FLASK,
      "Benzaldehyde and heptanal joined by an aldol condensation.", wiki=P["AmylCinnamal"], T=40),
    R("Rose Oxide", "2 Citronellol + O2 -> 2 RoseOxide + 2 H2O", LIGHT,
      "Citronellol photo-oxygenated with singlet oxygen; the hydroperoxide is reduced and closed into the ring.", wiki=P["RoseOxide"]),
    R("Peach Lactone", "UndecylenicAcid -> Undecalactone", HEAT,
      "Undecylenic acid in hot sulfuric acid: the double bond walks down the chain until the acid can close onto it.",
      wiki=P["Undecalactone"], T=80),
    R("2-Heptylcyclopentanone", "Cyclopentanone + Heptanal + H2 -> HeptylCyclopentanone + H2O", CAT,
      "Cyclopentanone condensed with heptanal and the double bond hydrogenated.", wiki=P["HeptylCyclopentanone"], cat="Pd", T=120),
    R("2-Methoxy-4-nitroaniline", "oAnisidine + HNO3 -> MethoxyNitroaniline + H2O", FLASK,
      "o-Anisidine acetylated, nitrated para to the amine, and the acetyl taken off again.", wiki=P["MethoxyNitroaniline"], T=10),
    R("Centralite II", "2 NMethylaniline + COCl2 -> Centralite2 + 2 HCl", FLASK,
      "Two N-methylanilines on one phosgene.", wiki=P["Centralite2"], T=60),
    R("EDDI", "EDA + 2 HI -> EDDI", MIX,
      "Ethylenediamine neutralised with hydroiodic acid.", wiki=P["EDDI"]),
    R("Potassium Phosphite", "H3PO3 + KOH -> KH2PO3 + H2O", MIX,
      "Phosphorous acid half-neutralised with potash.", wiki=P["KH2PO3"]),
    R("TEBA", "BenzylChloride + Et3N -> TEBA", MIX,
      "Triethylamine quaternised by benzyl chloride.", wiki=P["TEBA"]),
    R("Benzyltriphenylphosphonium Chloride", "BenzylChloride + PPh3 -> BTPPC", FLASK,
      "Triphenylphosphine quaternised by benzyl chloride.", wiki=P["BTPPC"], T=110),
    R("ACHN", "2 Cyclohexanone + N2H4 + 2 HCN + Cl2 -> ACHN + 2 H2O + 2 HCl", FLASK,
      "Cyclohexanone's ketazine takes up hydrogen cyanide, and chlorine oxidises the hydrazo link to an azo group.",
      wiki=P["ACHN"], T=20),
    R("Sulisobenzone", "Oxybenzone + H2SO4 -> BP4 + H2O", FLASK,
      "Oxybenzone sulfonated on the methoxy-bearing ring.", wiki=P["BP4"], T=60),
    R("Triethanolamine Oleate", "TEA + OleicAcid -> TEAOleate", MIX,
      "Oleic acid neutralised with triethanolamine.", wiki=P["TEAOleate"]),
    R("Butylmagnesium Chloride", "BuCl + Mg -> BuMgCl", FLASK,
      "1-Chlorobutane on magnesium turnings in dry ether.", wiki=P["BuMgCl"]),
]

# Milestones for the stretches this part lengthened (messages only).
import authored_content as _C  # noqa: E402
from gen_authored import Milestone  # noqa: E402
_C.MILESTONES += [
    Milestone("Undecalactone", message="Guerlain's Mitsouko (1919) wrapped a synthetic peach lactone in oakmoss; two years later Chanel No. 5 did the same with aldehydes. Perfume becomes chemistry."),
    Milestone("HEMA", message="Otto Wichterle's soft contact lens (1961): a gel of poly-HEMA that drinks water, cast on a machine he built from a children's construction set."),
]

import authored_canon_20  # noqa: E402,F401
