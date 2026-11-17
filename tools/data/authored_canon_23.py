"""
Curieosity's industrial chemistry, part 23 (see authored_canon.py): the rest of the canon compounds
whose links pointed at the wrong article, given PubChem pages and a route, with the intermediates they
need: ethephon by way of the Arbuzov rearrangement, the phosphinate flame retardants, the linear
silicone fluids and the divinyl siloxane of platinum catalysts, neodecanoic acid from propylene
trimer, and the fragrance chain from pinene and myrcene.
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


def WK(cas, key, name, formula, state, title, desc, smiles=None):
    """A compound with a Wikipedia article."""
    P[key] = title
    S(cas, key, name, formula, state, title, desc, smiles=smiles)


CANON.update({"11138-11-7": "BaFerrite"})

# --- intermediates ------------------------------------------------------------------------------
WK("16672-87-0", "Ethephon", "Ethephon", "C2H6ClO3P", "Solid", "Ethephon",
   "A plant growth regulator: inside the plant it breaks down to ethylene, which ripens fruit, opens cotton bolls and makes pineapples flower.",
   "OP(O)(=O)CCCl")
PC("140-08-9", "TCEPite", "Tris(2-chloroethyl) phosphite", "C6H12Cl3O3P", "Liquid", 8783,
   "Phosphorus trichloride with three ethylene oxides opened onto it.", "ClCCOP(OCCCl)OCCCl")
PC("6294-34-4", "BCEP", "Bis(2-chloroethyl) 2-chloroethylphosphonate", "C6H12Cl3O3P", "Liquid", 80518,
   "The Arbuzov rearrangement of tris(2-chloroethyl) phosphite, one step from ethephon.", "ClCCOP(=O)(CCCl)OCCCl")
PC("813-76-3", "DEPA", "Diethylphosphinic acid", "C4H11O2P", "Liquid", "Diethylphosphinic acid",
   "Two ethylenes on hypophosphorous acid: the acid of the halogen-free phosphinate flame retardants.", "CCP(O)(=O)CC")
PC("225789-38-8", "AlDEP", "Aluminium diethylphosphinate", "C12H30AlO6P3", "Solid", 87076731,
   "A halogen-free flame retardant for the glass-filled nylons and polyesters of electrical connectors.",
   "[Al+3].CCP([O-])(=O)CC.CCP([O-])(=O)CC.CCP([O-])(=O)CC")
PC("284685-45-6", "ZnDEP", "Zinc diethylphosphinate", "C8H20O4P2Zn", "Solid", 87076569,
   "A phosphinate flame retardant for polyesters and nylons.", "[Zn+2].CCP([O-])(=O)CC.CCP([O-])(=O)CC")
PC("1719-58-0", "VinylMe2SiCl", "Chlorodimethylvinylsilane", "C4H9ClSi", "Liquid", 519368,
   "Acetylene hydrosilylated with chlorodimethylsilane; hydrolysed, it gives divinyltetramethyldisiloxane.", "C=C[Si](C)(C)Cl")
PC("2627-95-4", "DVTMDS", "1,3-Divinyltetramethyldisiloxane", "C8H18OSi2", "Liquid", 75819,
   "The ligand of Karstedt's platinum catalyst, which cures silicone rubber, and an end-capper for vinyl silicones.",
   "C=C[Si](C)(C)O[Si](C)(C)C=C")
PC("1120-36-1", "Tetradecene", "1-Tetradecene", "C14H28", "Liquid", 14260,
   "An alpha-olefin from ethylene growth, for surfactants and lubricants.", "C=CCCCCCCCCCCCC")
WK("26896-20-8", "NDA", "Neodecanoic acid", "C10H20O2", "Liquid", "Neodecanoic_acid",
   "A highly branched acid from propylene trimer: its metal salts dry paints, its vinyl ester makes weather-proof coatings, and its peroxyesters start polymerisations.",
   "CCCCCCC(C)(C)C(O)=O")
PC("111-88-6", "Octanethiol", "1-Octanethiol", "C8H18S", "Liquid", "1-Octanethiol",
   "Octyl mercaptan, a chain-transfer agent and antioxidant building block.", "CCCCCCCCS")
WK("543-39-5", "Myrcenol", "Myrcenol", "C10H18O", "Liquid", "Myrcenol",
   "A fresh, floral terpene alcohol of lavender oil, and a diene for Diels-Alder fragrances.", "CC(C)(O)CCCC(=C)C=C")
PC("1686-14-2", "PineneOxide", "alpha-Pinene oxide", "C10H16O", "Liquid", "alpha-Pinene oxide",
   "Pinene epoxidised; Lewis acids rearrange it to campholenic aldehyde.", "CC12OC1CC1CC2C1(C)C")
PC("4501-58-0", "CampholenicAldehyde", "Campholenic aldehyde", "C10H16O", "Liquid", "Campholenic aldehyde",
   "The starting point of the synthetic sandalwood odourants.", "CC1=CCC(CC=O)C1(C)C")
PC("928-51-8", "ClBuOH", "4-Chloro-1-butanol", "C4H9ClO", "Liquid", "4-Chloro-1-butanol",
   "Tetrahydrofuran opened by hydrogen chloride.", "OCCCCCl")
PC("1569-69-3", "Cyclohexanethiol", "Cyclohexanethiol", "C6H12S", "Liquid", "Cyclohexanethiol",
   "Cyclohexyl mercaptan, on the way to the rubber retarder CTP.", "SC1CCCCC1")
PC("2867-47-2", "DMAEMA", "2-(Dimethylamino)ethyl methacrylate", "C8H15NO2", "Liquid", 17869,
   "An amine methacrylate: quaternised, it makes the cationic polymers that flocculate sewage sludge and paper fines.",
   "CN(C)CCOC(=O)C(C)=C")
PC("1559-35-9", "EGEHE", "2-(2-Ethylhexyloxy)ethanol", "C10H22O2", "Liquid", 15260,
   "A slow glycol ether solvent for coatings.", "CCCCC(CC)COCCO")
PC("2409-55-4", "TBMP", "2-tert-Butyl-4-methylphenol", "C11H16O", "Solid", 17004,
   "p-Cresol with one tert-butyl group: the half of BHT that the methylene-bridged antioxidants are built from.",
   "Cc1ccc(O)c(c1)C(C)(C)C")

# --- the canon compounds -------------------------------------------------------------------------
PC("10124-53-5", "MgS2O3", "Magnesium thiosulfate", "MgS2O3", "Solid", 86597514,
   "A liquid fertiliser that brings magnesium and sulfur to the soil together.")
WK("10061-01-5", "DCP13", "1,3-Dichloropropene", "C3H4Cl2", "Liquid", "1,3-Dichloropropene",
   "Telone: a soil fumigant injected before planting to kill nematodes.", "ClC=CCCl")
PC("10519-96-7", "KOSiMe3", "Potassium trimethylsilanolate", "C3H9KOSi", "Solid", 24201306,
   "A soluble base that starts silicone ring-opening polymerisation and cleaves esters.", "[K+].C[Si](C)(C)[O-]")
PC("12542-30-2", "DCPDAcrylate", "Dicyclopentenyl acrylate", "C13H16O2", "Liquid", 3037072,
   "A low-odour acrylate for tough, weather-proof coatings and adhesives.", "C=CC(=O)OC1CC2C3CC=CC3C1C2")
PC("13752-51-7", "OTOS", "OTOS", "C9H16N2O2S2", "Solid", 83700,
   "A thiocarbamyl sulfenamide that vulcanises tyre rubber without the nitrosamines of older accelerators.",
   "S=C(SN1CCOCC1)N1CCOCC1")
PC("13828-37-0", "Mayol", "Mayol", "C10H20O", "Liquid", 83763,
   "4-Isopropylcyclohexanemethanol: a fresh lily-of-the-valley note for soaps and shampoos.", "OCC1CCC(CC1)C(C)C")
PC("13845-36-8", "KTPP", "Potassium tripolyphosphate", "K5P3O10", "Solid", 156592234,
   "A very soluble phosphate for liquid detergents and fertilisers.")
PC("16251-77-7", "PhenylButanal3", "3-Phenylbutanal", "C10H12O", "Liquid", 85979,
   "Trifernal: a green, floral-hyacinth aldehyde for perfumes.", "CC(CC=O)c1ccccc1")
PC("19035-79-1", "KCetylPhosphate", "Potassium cetyl phosphate", "C16H34KO4P", "Solid", 87063641,
   "An emulsifier for sunscreens and creams.", "[K+].CCCCCCCCCCCCCCCCOP(O)([O-])=O")
PC("2062-98-8", "HFPODAF", "HFPO dimer acid fluoride", "C6F12O2", "Liquid", 102740,
   "Two hexafluoropropylene oxides joined: hydrolysed, it is GenX.", "O=C(F)C(F)(OC(F)(F)C(F)(F)C(F)(F)F)C(F)(F)F")
PC("2110-78-3", "MHIB", "Methyl 2-hydroxyisobutyrate", "C5H10O3", "Liquid", 75024,
   "A clean solvent for photoresists in chip making.", "COC(=O)C(C)(C)O")
PC("22397-31-5", "DEGBisCN", "Diethylene glycol bis(2-cyanoethyl) ether", "C10H16N2O3", "Liquid", 89693,
   "Hydrogenated, it gives a flexible ether diamine for epoxy hardeners.", "N#CCCOCCOCCOCCC#N")
PC("24448-20-2", "BisEMA", "Bisphenol A ethoxylate dimethacrylate", "C27H32O6", "Solid", 90508,
   "Bis-EMA: a crosslinker of dental fillings and anaerobic thread-lockers.",
   "CC(=C)C(=O)OCCOc1ccc(cc1)C(C)(C)c1ccc(OCCOC(=O)C(C)=C)cc1")
PC("27177-77-1", "KDDBS", "Potassium dodecylbenzenesulfonate", "C18H29KO3S", "Solid", "Potassium dodecylbenzenesulfonate",
   "The potassium salt of LAS, for liquid soaps that stay clear in the cold.", "[K+].CCCCCCCCCCCCc1ccc(cc1)S([O-])(=O)=O")
PC("27794-93-0", "KATMP", "Potassium aminotris(methylenephosphonate)", "C3H11KNO9P3", "Solid", 172759680,
   "A scale and corrosion inhibitor for cooling water.", "[K+].OP(O)(=O)CN(CP(O)(O)=O)CP(O)([O-])=O")
PC("28219-61-6", "Bacdanol", "Bacdanol", "C14H24O", "Liquid", 119898,
   "A synthetic sandalwood odourant, standing in for the scarce oil of the sandalwood tree.", "CCC(CO)=CCC1CC=C(C)C1(C)C")
PC("375-72-4", "PBSF", "Perfluorobutanesulfonyl fluoride", "C4F10O2S", "Liquid", 67814,
   "Made by electrochemical fluorination: the short-chain building block that replaced PFOS chemistry.",
   "O=S(=O)(F)C(F)(F)C(F)(F)C(F)(F)C(F)(F)F")
PC("29420-49-3", "KPFBS", "Potassium perfluorobutanesulfonate", "C4F9KO3S", "Solid", 6330773,
   "A trace of it makes clear polycarbonate flame retardant.", "[K+].[O-]S(=O)(=O)C(F)(F)C(F)(F)C(F)(F)C(F)(F)F")
PC("31906-04-4", "Lyral", "Lyral", "C13H22O2", "Liquid", 91604,
   "A lily-of-the-valley aldehyde from myrcenol and acrolein; banned from EU cosmetics since 2021 because it causes contact allergy.",
   "CC(C)(O)CCCC1=CCC(CC1)C=O")
PC("3234-28-4", "EpoxyC14", "1,2-Epoxytetradecane", "C14H28O", "Liquid", 18604,
   "A long-chain epoxide for lubricant additives and surfactants.", "CCCCCCCCCCCCC1CO1")
PC("5518-18-3", "EBP", "Ethylenebis(palmitamide)", "C34H68N2O2", "Solid", 79654,
   "A wax that lets plastics slide out of moulds and kills foam in paints.", "CCCCCCCCCCCCCCCC(=O)NCCNC(=O)CCCCCCCCCCCCCCC")
PC("5862-38-4", "DHQ", "Dihydroquinacridone", "C20H14N2O2", "Solid", 79973,
   "Quinacridone one oxidation short; the pigment is made by oxidising it.", "O=C1C2=C(Cc3[nH]c4ccccc4c(=O)c3C2)Nc2ccccc12")
PC("6891-44-7", "METACMS", "Methacryloyloxyethyltrimethylammonium methyl sulfate", "C10H21NO6S", "Solid", 81318,
   "A cationic monomer for the flocculants of water treatment and papermaking.",
   "COS([O-])(=O)=O.CC(=C)C(=O)OCC[N+](C)(C)C")
PC("1181206-02-9", "pMethylstyrene", "4-Methylstyrene", "C9H10", "Liquid", 12161,
   "The para isomer of vinyltoluene: its polymer is lighter and tougher than polystyrene.", "Cc1ccc(C=C)cc1")
PC("13360-78-6", "NaDIBDTP", "Sodium diisobutyldithiophosphinate", "C8H18NaPS2", "Solid", 131846876,
   "A flotation collector that floats copper, silver and gold sulfides away from pyrite.", "[Na+].CC(C)CP([S-])(=S)CC(C)C")
PC("13893-53-3", "AminoDMBN", "2-Amino-2,3-dimethylbutanenitrile", "C6H12N2", "Liquid", 94355,
   "A Strecker aminonitrile, the start of the imidazolinone herbicides.", "CC(C)C(C)(N)C#N")
PC("141-62-8", "MD2M", "Decamethyltetrasiloxane", "C10H30O3Si4", "Liquid", 8852,
   "A linear silicone fluid: low surface tension, used in cosmetics and as a heat-transfer oil.",
   "C[Si](C)(C)O[Si](C)(C)O[Si](C)(C)O[Si](C)(C)C")
PC("141-63-9", "MD3M", "Dodecamethylpentasiloxane", "C12H36O4Si5", "Liquid", 8853,
   "A linear silicone fluid for cosmetics and precision cleaning.",
   "C[Si](C)(C)O[Si](C)(C)O[Si](C)(C)O[Si](C)(C)O[Si](C)(C)C")
PC("107-52-8", "MD4M", "Tetradecamethylhexasiloxane", "C14H42O5Si6", "Liquid", 7875,
   "A slightly heavier linear silicone fluid.",
   "C[Si](C)(C)O[Si](C)(C)O[Si](C)(C)O[Si](C)(C)O[Si](C)(C)O[Si](C)(C)C")
PC("15647-08-2", "EHDPPite", "2-Ethylhexyl diphenyl phosphite", "C20H27O3P", "Liquid", 85888,
   "A phosphite heat stabiliser for PVC.", "CCCCC(CC)COP(Oc1ccccc1)Oc1ccccc1")
PC("20587-61-5", "DEGMB", "Diethylene glycol monobenzoate", "C11H14O4", "Liquid", 88603,
   "The half-ester on the way to the dibenzoate plasticisers.", "OCCOCCOC(=O)c1ccccc1")
PC("31291-60-8", "DSBP", "2,4-Di-sec-butylphenol", "C14H22O", "Liquid", 15808,
   "An alkylphenol for antioxidants and phosphite stabilisers.", "CCC(C)c1ccc(O)c(c1)C(C)CC")
PC("40292-82-8", "NDC", "Neodecanoyl chloride", "C10H19ClO", "Liquid", 94502,
   "The acid chloride of neodecanoic acid, for the peroxyesters that start PVC and LDPE polymerisation.",
   "CCCCCCC(C)(C)C(Cl)=O")
PC("110553-27-0", "Irganox1520", "Irganox 1520", "C25H44OS2", "Liquid", 113646,
   "A liquid antioxidant that also mops up peroxides, for rubbers and adhesives.", "CCCCCCCCSCc1cc(C)c(O)c(CSCCCCCCCC)c1")
PC("5324-84-5", "NaOctSulfonate", "Sodium 1-octanesulfonate", "C8H17NaO3S", "Solid", 45052255,
   "A hydrotrope for cleaners, and the ion-pair reagent of HPLC.", "[Na+].CCCCCCCCS([O-])(=O)=O")
PC("13031-43-1", "AcetoxyAcetophenone", "4-Acetoxyacetophenone", "C10H10O3", "Solid", 83063,
   "On the way to 4-acetoxystyrene and the poly(hydroxystyrene) of photoresists.", "CC(=O)Oc1ccc(cc1)C(C)=O")
PC("23251-72-1", "DEAAcetate", "Diethanolamine acetate", "C6H15NO4", "Liquid", 159946,
   "A salt that helps cement grind finer.", "CC(O)=O.OCCNCCO")
PC("13701-64-9", "CaB2O4", "Calcium metaborate", "CaB2O4", "Solid", 156591902,
   "A boron source for glass fibre and a flame retardant.")
PC("63316-43-8", "KSS", "Potassium diphenylsulfone sulfonate", "C12H9KO5S2", "Solid", 87391964,
   "A flame retardant for clear polycarbonate.", "[K+].[O-]S(=O)(=O)c1cccc(c1)S(=O)(=O)c1ccccc1")
PC("13319-75-0", "BF3Dihydrate", "Boron trifluoride dihydrate", "H4BF3O2", "Liquid", 61591,
   "A strong acid catalyst for alkylations and polymerisations.", "FB(F)F.O.O")
PC("14974-48-2", "VanadylOxalate", "Vanadyl oxalate", "C2O5V", "Solid", 87074202,
   "Soluble vanadium for the catalysts of sulfuric acid plants and power-station flue gas cleaning.",
   "O=[V+2].[O-]C(=O)C([O-])=O")
PC("1559-36-0", "DEGEHE", "Diethylene glycol mono(2-ethylhexyl) ether", "C12H26O3", "Liquid", 94210,
   "A slow, oily glycol ether solvent for coatings.", "CCCCC(CC)COCCOCCO")
PC("1719-57-9", "ClCH2SiMe2Cl", "Chloro(chloromethyl)dimethylsilane", "C3H8Cl2Si", "Liquid", 74393,
   "A silane with a reactive chloromethyl arm, for silicone coupling agents and drugs.", "C[Si](C)(Cl)CCl")
PC("1888-87-5", "iBuAlCl2", "Isobutylaluminium dichloride", "C4H9AlCl2", "Liquid", 74679,
   "A Lewis-acid co-catalyst for olefin polymerisation.", "CC(C)C[Al](Cl)Cl")
PC("2528-39-4", "THP", "Trihexyl phosphate", "C18H39O4P", "Liquid", 75666,
   "A plasticiser and an extractant for metals.", "CCCCCCOP(=O)(OCCCCCC)OCCCCCC")
PC("35674-56-7", "BzIQCl", "Benzylisoquinolinium chloride", "C16H14ClN", "Solid", 118855,
   "A corrosion inhibitor for the acids that clean out oil wells and boilers.", "[Cl-].C(c1ccccc1)[n+]1ccc2ccccc2c1")
PC("37788-55-9", "HPIm", "1-(2-Hydroxypropyl)imidazole", "C6H10N2O", "Liquid", 109233,
   "A latent accelerator for epoxy cures.", "CC(O)Cn1ccnc1")
PC("32582-32-4", "TDOD", "2-Tetradecyl-1-octadecanol", "C32H66O", "Solid", 94435,
   "A Guerbet alcohol: branched, so it stays liquid-like and slick in drilling fluids and cosmetics.",
   "CCCCCCCCCCCCCCCCC(CO)CCCCCCCCCCCCCC")
PC("17796-82-6", "CTP", "N-(Cyclohexylthio)phthalimide", "C14H15NO2S", "Solid", 28777,
   "A retarder that keeps tyre rubber from scorching (curing too early) while it is mixed.", "O=C1N(SC2CCCCC2)C(=O)c2ccccc12")
PC("3444-17-5", "CrEH3", "Chromium(III) 2-ethylhexanoate", "C24H45CrO6", "Liquid", 110967,
   "The chromium source of the Phillips catalyst that trimerises ethylene into 1-hexene.",
   "[Cr+3].CCCCC(CC)C([O-])=O.CCCCC(CC)C([O-])=O.CCCCC(CC)C([O-])=O")
PC("1633-83-6", "BuSultone", "1,4-Butane sultone", "C4H8O3S", "Liquid", 15411,
   "A sulfobutylating agent: it makes the cyclodextrin that dissolves insoluble drugs, and battery electrolyte additives.",
   "O=S1(=O)CCCCO1")
PC("7722-71-6", "OleylPhosphate", "Oleyl phosphate", "C18H37O4P", "Liquid", 82177,
   "An anionic surfactant and corrosion inhibitor for metalworking fluids.", "CCCCCCCCC=CCCCCCCCCOP(O)(O)=O")
PC("119-47-1", "AO2246", "Antioxidant 2246", "C23H32O2", "Solid", 8398,
   "A methylene-bridged bisphenol antioxidant for rubber and plastics that does not stain.",
   "Cc1cc(Cc2cc(C)cc(c2O)C(C)(C)C)c(O)c(c1)C(C)(C)C")

# --- the reactions -------------------------------------------------------------------------------
E4.reactions += [
    R("Magnesium Thiosulfate", "MgO + SO2 + S -> MgS2O3", MIX,
      "Magnesia slurried with sulfur dioxide, and the sulfite boiled with sulfur.", wiki=P["MgS2O3"]),
    R("1,3-Dichloropropene", "AllylChloride + Cl2 -> DCP13 + HCl", HEAT,
      "A by-product of hot propylene chlorination: allyl chloride chlorinated a second time.", wiki=P["DCP13"], T=500),
    R("Potassium Tripolyphosphate", "5 Potash + 6 H3PO4 -> 2 KTPP + 5 CO2 + 9 H2O", HEAT,
      "Potash and phosphoric acid mixed in the right ratio and calcined until the phosphates link up.", wiki=P["KTPP"], T=400),
    R("Diethanolamine Acetate", "DEA + AcOH -> DEAAcetate", MIX, "Diethanolamine neutralised with acetic acid.", wiki=P["DEAAcetate"]),
    R("Calcium Metaborate", "CaO + B2O3 -> CaB2O4", HEAT, "Lime and boric oxide fused.", wiki=P["CaB2O4"], T=1000),
    R("Boron Trifluoride Dihydrate", "BF3 + 2 H2O -> BF3Dihydrate", MIX,
      "Boron trifluoride absorbed in two equivalents of water.", wiki=P["BF3Dihydrate"]),
    R("Vanadyl Oxalate", "V2O5 + 3 Oxalic -> 2 VanadylOxalate + 2 CO2 + 3 H2O", MIX,
      "Oxalic acid reduces vanadium pentoxide to vanadyl and dissolves it.", wiki=P["VanadylOxalate"]),
]
E5.reactions += [
    R("Tris(2-chloroethyl) Phosphite", "PCl3 + 3 EO -> TCEPite", FLASK,
      "Each P-Cl bond opens an ethylene oxide ring.", wiki=P["TCEPite"], T=20),
    R("Arbuzov Rearrangement", "TCEPite -> BCEP", HEAT,
      "Heated, the phosphite's own chloroethyl groups alkylate its phosphorus: a P-O ester becomes a P-C bond.", wiki=P["BCEP"], T=150),
    R("Ethephon", "BCEP + 2 HCl -> Ethephon + 2 EDC", HEAT,
      "Hydrogen chloride strips the two ester groups off as 1,2-dichloroethane.", wiki=P["Ethephon"], T=150),
    R("Diethylphosphinic Acid", "H3PO2 + 2 Ethylene -> DEPA", CAT,
      "Ethylene added twice to hypophosphorous acid by a radical chain.", wiki=P["DEPA"], cat="AIBN", T=100),
    R("Aluminium Diethylphosphinate", "3 DEPA + AlOH3 -> AlDEP + 3 H2O", MIX,
      "The phosphinic acid neutralised with aluminium hydroxide; the salt precipitates.", wiki=P["AlDEP"]),
    R("Zinc Diethylphosphinate", "2 DEPA + ZnO -> ZnDEP + H2O", MIX, "The phosphinic acid on zinc oxide.", wiki=P["ZnDEP"]),
    R("Chlorodimethylvinylsilane", "Me2SiHCl + Acetylene -> VinylMe2SiCl", CAT,
      "The Si-H bond added across acetylene over platinum (hydrosilylation).", wiki=P["VinylMe2SiCl"], cat="Pt", T=80),
    R("Divinyltetramethyldisiloxane", "2 VinylMe2SiCl + H2O -> DVTMDS + 2 HCl", MIX,
      "The chlorosilane hydrolysed; two silanols condense into the siloxane.", wiki=P["DVTMDS"]),
    R("1-Tetradecene", "Dodecene + Ethylene -> Tetradecene", PRESS,
      "One more ethylene grown onto the chain, under pressure on an aluminium alkyl.", wiki=P["Tetradecene"], T=100),
    R("1,2-Epoxytetradecane", "Tetradecene + PAA -> EpoxyC14 + AcOH", FLASK,
      "The olefin epoxidised with peracetic acid.", wiki=P["EpoxyC14"], T=40),
    R("Koch Neodecanoic Acid", "Nonene + CO + H2O -> NDA", HIGHP,
      "The Koch reaction: in strong acid the olefin becomes a tertiary carbocation that takes up carbon monoxide, then water.",
      wiki=P["NDA"], cat="H2SO4", T=50),
    R("Neodecanoyl Chloride", "3 NDA + PCl3 -> 3 NDC + H3PO3", FLASK, "Neodecanoic acid on phosphorus trichloride.", wiki=P["NDC"], T=60),
    R("1-Octanethiol", "Octene + H2S -> Octanethiol", LIGHT,
      "Hydrogen sulfide added to the end carbon of 1-octene by an ultraviolet-started radical chain.", wiki=P["Octanethiol"]),
    R("Irganox 1520", "oCresol + 2 CH2O + 2 Octanethiol -> Irganox1520 + 2 H2O", FLASK,
      "o-Cresol, formaldehyde and octanethiol joined in one pot.", wiki=P["Irganox1520"], T=120),
    R("Myrcenol", "Myrcene + H2O -> Myrcenol", CAT,
      "The diene masked with diethylamine, the lone double bond hydrated in acid, and the amine removed again over palladium.",
      wiki=P["Myrcenol"], cat="Pd", T=80),
    R("Lyral", "Myrcenol + Acrolein -> Lyral", HEAT, "A Diels-Alder reaction of myrcenol's diene with acrolein.", wiki=P["Lyral"], T=120),
    R("alpha-Pinene Oxide", "Pinene + PAA -> PineneOxide + AcOH", FLASK, "Pinene epoxidised with peracetic acid.", wiki=P["PineneOxide"], T=20),
    R("Campholenic Aldehyde", "PineneOxide -> CampholenicAldehyde", CAT,
      "Zinc bromide opens the epoxide and the four-membered ring breaks open.", wiki=P["CampholenicAldehyde"], cat="ZnBr2", T=80),
    R("Bacdanol", "CampholenicAldehyde + Butanal + H2 -> Bacdanol + H2O", CAT,
      "An aldol condensation with butanal, then the aldehyde reduced to the alcohol, leaving the double bond.",
      wiki=P["Bacdanol"], cat="Ni", T=100),
    R("4-Chlorobutanol", "THF + HCl -> ClBuOH", HEAT, "Tetrahydrofuran opened by hydrogen chloride.", wiki=P["ClBuOH"], T=100),
    R("1,4-Butane Sultone", "ClBuOH + Na2SO3 + HCl -> BuSultone + 2 NaCl + H2O", FLASK,
      "The chloride swapped for a sulfonate, the acid freed and closed into a ring by losing water.", wiki=P["BuSultone"], T=150),
    R("Cyclohexanethiol", "Cyclohexene + H2S -> Cyclohexanethiol", CAT,
      "Hydrogen sulfide added to cyclohexene over an acid catalyst.", wiki=P["Cyclohexanethiol"], cat="H3PO4", T=200),
    R("CTP Retarder", "Cyclohexanethiol + Cl2 + Phthalimide + NaOH -> CTP + HCl + NaCl + H2O", FLASK,
      "The thiol chlorinated to cyclohexylsulfenyl chloride, which then bonds to phthalimide's nitrogen.", wiki=P["CTP"], T=10),
    R("DMAEMA", "MMA + DMAE -> DMAEMA + Methanol", CAT,
      "Methyl methacrylate transesterified with dimethylaminoethanol, methanol distilled off.", wiki=P["DMAEMA"], cat="TiOtBu4", T=110),
    R("METAC Methyl Sulfate", "DMAEMA + DimethylSulfate -> METACMS", MIX,
      "The amine methacrylate quaternised with dimethyl sulfate.", wiki=P["METACMS"]),
    R("2-(2-Ethylhexyloxy)ethanol", "2EH + EO -> EGEHE", PRESS, "2-Ethylhexanol opens ethylene oxide.", wiki=P["EGEHE"], T=150),
    R("DEG 2-Ethylhexyl Ether", "EGEHE + EO -> DEGEHE", PRESS, "One more ethylene oxide.", wiki=P["DEGEHE"], T=150),
    R("2-tert-Butyl-p-cresol", "pCresol + Isobutylene -> TBMP", FLASK,
      "p-Cresol butylated once, in acid, with the isobutylene kept short.", wiki=P["TBMP"], T=70),
    R("Antioxidant 2246", "2 TBMP + CH2O -> AO2246 + H2O", FLASK,
      "Two butylcresols bridged by formaldehyde in acid.", wiki=P["AO2246"], T=90),
    R("Potassium Trimethylsilanolate", "HMDSO + 2 KOH -> 2 KOSiMe3 + H2O", HEAT,
      "Hexamethyldisiloxane split by caustic potash.", wiki=P["KOSiMe3"], T=110),
    R("Dicyclopentenyl Acrylate", "DCPD + AcrylicAcid -> DCPDAcrylate", CAT,
      "Acrylic acid added across a double bond of dicyclopentadiene in acid.", wiki=P["DCPDAcrylate"], cat="H2SO4", T=100),
    R("OTOS", "2 Morpholine + CS2 + H2O2 -> OTOS + 2 H2O", FLASK,
      "Morpholine dithiocarbamate oxidatively coupled to a second morpholine.", wiki=P["OTOS"], T=20),
    R("Mayol", "Cuminaldehyde + 4 H2 -> Mayol", CAT,
      "Cuminaldehyde hydrogenated through, ring and aldehyde both.", wiki=P["Mayol"], cat="Ni", T=150),
    R("Trifernal", "AMS + CO + H2 -> PhenylButanal3", HIGHP,
      "alpha-Methylstyrene hydroformylated at its end carbon.", wiki=P["PhenylButanal3"], cat="Co", T=120),
    R("Potassium Cetyl Phosphate", "CetylAlcohol + H3PO4 + KOH -> KCetylPhosphate + 2 H2O", HEAT,
      "Cetyl alcohol phosphated and half-neutralised with potash.", wiki=P["KCetylPhosphate"], T=120),
    R("HFPO Dimer Acid Fluoride", "2 HFPO -> HFPODAF", CAT,
      "Fluoride ion opens one hexafluoropropylene oxide onto another.", wiki=P["HFPODAF"], cat="KF", T=0),
    R("GenX from the Acid Fluoride", "HFPODAF + H2O -> GenX + HF", MIX, "The acid fluoride hydrolysed.", wiki=P["HFPODAF"]),
    R("Methyl 2-Hydroxyisobutyrate", "ACH + Methanol + H2O -> MHIB + NH3", FLASK,
      "Acetone cyanohydrin's nitrile hydrated and esterified with methanol.", wiki=P["MHIB"], T=80),
    R("Cyanoethylated Diethylene Glycol", "DEG + 2 Acrylonitrile -> DEGBisCN", MIX,
      "Both hydroxyls add to acrylonitrile with a base catalyst.", wiki=P["DEGBisCN"]),
    R("Bis-EMA", "BPA + 2 EO + 2 MethacrylicAcid -> BisEMA + 2 H2O", FLASK,
      "Bisphenol A ethoxylated at each end and then esterified with methacrylic acid.", wiki=P["BisEMA"], T=110),
    R("Potassium Dodecylbenzenesulfonate", "DDBSA + KOH -> KDDBS + H2O", MIX, "LAS acid neutralised with potash.", wiki=P["KDDBS"]),
    R("Potassium ATMP", "ATMP + KOH -> KATMP + H2O", MIX, "ATMP one-third neutralised with potash.", wiki=P["KATMP"]),
    R("Perfluorobutanesulfonyl Fluoride", "Sulfolane + 10 HF -> PBSF + 9 H2", ECELL,
      "Simons electrochemical fluorination: sulfolane in liquid hydrogen fluoride over nickel anodes; the ring opens as every hydrogen is replaced.",
      wiki=P["PBSF"], T=10),
    R("Potassium Perfluorobutanesulfonate", "PBSF + 2 KOH -> KPFBS + KF + H2O", MIX,
      "The sulfonyl fluoride hydrolysed with potash.", wiki=P["KPFBS"]),
    R("Ethylenebis(palmitamide)", "EDA + 2 PalmiticAcid -> EBP + 2 H2O", HEAT,
      "Ethylenediamine amidated at both ends with palmitic acid.", wiki=P["EBP"], T=200),
    R("Dihydroquinacridone", "2 Succinic + 2 Aniline -> DHQ + 6 H2O", HEAT,
      "Succinic ester self-condensed, condensed with aniline and ring-closed in hot oil.", wiki=P["DHQ"], T=250),
    R("Quinacridone by Oxidation", "2 DHQ + O2 -> 2 Quinacridone + 2 H2O", FLASK,
      "Dihydroquinacridone oxidised in alkali to the red-violet pigment.", wiki=P["DHQ"], T=90),
    R("4-Methylstyrene", "pEthyltoluene -> pMethylstyrene + H2", CAT,
      "4-Ethyltoluene dehydrogenated over iron oxide.", wiki=P["pMethylstyrene"], cat="Hematite", T=600),
    R("Aerophine Collector", "2 Isobutylene + Phosphine + 2 S + NaOH -> NaDIBDTP + H2O", CAT,
      "Phosphine added twice across isobutylene, the phosphine sulfurised and neutralised.", wiki=P["NaDIBDTP"], cat="AIBN", T=90),
    R("Strecker Aminonitrile", "MIPK + HCN + NH3 -> AminoDMBN + H2O", MIX,
      "A Strecker synthesis on methyl isopropyl ketone.", wiki=P["AminoDMBN"]),
    R("Decamethyltetrasiloxane", "4 MDM + D4 -> 4 MD2M", CAT,
      "Silicone equilibration: the acid cuts and rejoins Si-O bonds until the chains average out.", wiki=P["MD2M"], cat="H2SO4"),
    R("Dodecamethylpentasiloxane", "4 MD2M + D4 -> 4 MD3M", CAT, "One more equilibration step.", wiki=P["MD3M"], cat="H2SO4"),
    R("Tetradecamethylhexasiloxane", "4 MD3M + D4 -> 4 MD4M", CAT, "And another.", wiki=P["MD4M"], cat="H2SO4"),
    R("2-Ethylhexyl Diphenyl Phosphite", "TPPite + 2EH -> EHDPPite + Phenol", FLASK,
      "Triphenyl phosphite transesterified once with 2-ethylhexanol.", wiki=P["EHDPPite"], T=140),
    R("DEG Monobenzoate", "DEG + BenzoicAcid -> DEGMB + H2O", CAT,
      "Diethylene glycol esterified at one end.", wiki=P["DEGMB"], cat="H2SO4", T=180),
    R("2,4-Di-sec-butylphenol", "Phenol + 2 2-Butene -> DSBP", CAT, "Phenol alkylated twice with 2-butene.", wiki=P["DSBP"], cat="H2SO4", T=120),
    R("Sodium Octanesulfonate", "Octene + NaHSO3 -> NaOctSulfonate", CAT,
      "Bisulfite added to the end carbon of 1-octene by a radical chain.", wiki=P["NaOctSulfonate"], cat="AIBN", T=90),
    R("4-Acetoxyacetophenone", "HAP + AceticAnhydride -> AcetoxyAcetophenone + AcOH", FLASK,
      "4-Hydroxyacetophenone acetylated.", wiki=P["AcetoxyAcetophenone"], T=100),
    R("Potassium Diphenylsulfone Sulfonate", "DPSulfone + SO3 + KOH -> KSS + H2O", FLASK,
      "Diphenyl sulfone sulfonated once, meta to the sulfone, and neutralised.", wiki=P["KSS"], T=100),
    R("Chloromethyl Silane", "Me3SiCl + Cl2 -> ClCH2SiMe2Cl + HCl", LIGHT,
      "One methyl of chlorotrimethylsilane chlorinated in ultraviolet light.", wiki=P["ClCH2SiMe2Cl"]),
    R("Isobutylaluminium Dichloride", "TIBA + 2 AlCl3 -> 3 iBuAlCl2", MIX,
      "Triisobutylaluminium and aluminium chloride trade groups.", wiki=P["iBuAlCl2"]),
    R("Trihexyl Phosphate", "POCl3 + 3 Hexanol -> THP + 3 HCl", FLASK, "Phosphorus oxychloride on hexanol.", wiki=P["THP"], T=40),
    R("Benzylisoquinolinium Chloride", "Isoquinoline + BenzylChloride -> BzIQCl", MIX,
      "Isoquinoline quaternised with benzyl chloride.", wiki=P["BzIQCl"]),
    R("Hydroxypropyl Imidazole", "Imidazole + PO -> HPIm", MIX, "Imidazole opens propylene oxide.", wiki=P["HPIm"]),
    R("Guerbet C32 Alcohol", "2 CetylAlcohol -> TDOD + H2O", CAT,
      "The Guerbet reaction: two alcohols dehydrogenated, aldol-condensed and hydrogenated back to one branched alcohol.",
      wiki=P["TDOD"], cat="KOH", T=230),
    R("Chromium 2-Ethylhexanoate", "CrCl3 + 3 EHAcid + 3 NaOH -> CrEH3 + 3 NaCl + 3 H2O", MIX,
      "Chromium chloride and sodium 2-ethylhexanoate exchange ions; the chromium salt goes into the oil.", wiki=P["CrEH3"]),
    R("Oleyl Phosphate", "OleylAlcohol + H3PO4 -> OleylPhosphate + H2O", HEAT,
      "Oleyl alcohol phosphated.", wiki=P["OleylPhosphate"], T=120),
]

# Milestones for the stretches this part lengthened (messages only).
import authored_content as _C  # noqa: E402
from gen_authored import Milestone  # noqa: E402
_C.MILESTONES += [
    Milestone("NaIO4", message="Periodate cuts a carbon chain wherever two hydroxyls sit side by side (Malaprade, 1928): the cut pieces told chemists how sugars are built."),
    Milestone("Imidazole", message="Imidazole is the ring of histidine, which passes protons back and forth in the active sites of enzymes; in industry it cures epoxies."),
    Milestone("Ethephon", message="A ripening hormone in a bottle: ethephon gives plants ethylene on demand, and cotton fields open all at once for the picker."),
]
import authored_canon_24  # noqa: E402,F401
