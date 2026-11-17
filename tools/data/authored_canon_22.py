"""
Curieosity's industrial chemistry, part 22 (see authored_canon.py): more canon compounds with no
Wikipedia article of their own (PubChem pages), around a few new intermediates: the oxo
alcohols (isodecanol, tridecanol) and the glycol ethers, the fatty dimethylamines behind the
quats and amine oxides, and the oxides and ferrites that later stages will build with (ceria,
zirconia, barium and manganese-zinc ferrites).
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


CANON.update({"51580-86-0": "NaDCC", "62037-80-3": "GenX",
              # the same compound already in the game under another entry
              "12168-85-3": "Cement", "298-14-6": "Potash", "25376-45-8": "TDA", "13598-36-2": "H3PO3",
              "112945-52-5": "FumedSilica", "3452-97-9": "Isononanol", "12033-60-2": "Si3N4", "1344-08-7": "Na2S4"})

# --- intermediates ------------------------------------------------------------------------------
PC("112-34-5", "DEGBE", "Diethylene glycol monobutyl ether", "C8H18O3", "Liquid", "2-(2-Butoxyethoxy)ethanol",
   "Butyl carbitol: a slow solvent for paints and household cleaners.", "CCCCOCCOCCO")
PC("112-42-5", "Undecanol", "1-Undecanol", "C11H24O", "Liquid", "1-Undecanol",
   "An eleven-carbon fatty alcohol for plasticisers and flavour.", "CCCCCCCCCCCO")
WK("27215-95-8", "Nonene", "Nonene", "C9H18", "Liquid", "Nonene",
   "Propylene trimer: a branched nine-carbon olefin, the feed for isodecanol and nonylphenol.", "CC=CC(C)CC(C)C")
PC("112-70-9", "Tridecanol", "Tridecanol", "C13H28O", "Liquid", "1-Tridecanol",
   "An oxo alcohol for surfactants and lubricant esters.", "CCCCCCCCCCCCCO")
PC("25339-17-7", "Isodecanol", "Isodecanol", "C10H22O", "Liquid", "Isodecanol",
   "A branched ten-carbon oxo alcohol, the base of the heavy plasticisers.", "CC(C)CCCCCCCO")
WK("110-80-5", "EGEE", "2-Ethoxyethanol", "C4H10O2", "Liquid", "2-Ethoxyethanol",
   "Cellosolve: a glycol ether solvent, now mostly replaced as it harms fertility.", "CCOCCO")
PC("111-90-0", "Carbitol", "Diethylene glycol monoethyl ether", "C6H14O3", "Liquid", "2-(2-Ethoxyethoxy)ethanol",
   "Carbitol: a solvent for dyes and lacquers, and a skin-penetrating carrier in cosmetics.", "CCOCCOCCO")
PC("7214-50-8", "tBuCyclohexanol2", "2-tert-Butylcyclohexanol", "C10H20O", "Liquid", "2-tert-Butylcyclohexanol",
   "The hydrogenated 2-tert-butylphenol, on the way to a woody-fruity fragrance.", "CC(C)(C)C1CCCCC1O")
PC("112-72-1", "Tetradecanol", "1-Tetradecanol", "C14H30O", "Solid", "1-Tetradecanol",
   "Myristyl alcohol, a fatty alcohol for creams and the C14 surfactants.", "CCCCCCCCCCCCCCO")
PC("112-75-4", "DMA14", "N,N-Dimethyltetradecylamine", "C16H35N", "Liquid", "N,N-Dimethyltetradecylamine",
   "A fatty tertiary amine, the core of the C14 quats and amine oxides.", "CCCCCCCCCCCCCCN(C)C")
PC("124-28-7", "DMA18", "N,N-Dimethyloctadecylamine", "C20H43N", "Solid", "N,N-Dimethyloctadecylamine",
   "A fatty tertiary amine for conditioning quats.", "CCCCCCCCCCCCCCCCCCN(C)C")
WK("27176-87-0", "DDBSA", "Dodecylbenzenesulfonic acid", "C18H30O3S", "Liquid", "Dodecylbenzenesulfonic_acid",
   "LAS acid: the world's main detergent acid, neutralised into the sulfonate of washing powders and dish liquids.",
   "CCCCCCCCCCCCc1ccc(cc1)S(O)(=O)=O")
PC("611-70-1", "Isobutyrophenone", "Isobutyrophenone", "C10H12O", "Liquid", "Isobutyrophenone",
   "A phenyl ketone, on the way to the photoinitiators.", "CC(C)C(=O)c1ccccc1")
WK("1306-38-3", "CeO2", "Cerium(IV) oxide", "CeO2", "Solid", "Cerium(IV)_oxide",
   "Ceria: the polishing powder of glass and lenses, and the oxygen store of catalytic converters.")
WK("1314-23-4", "ZrO2", "Zirconium dioxide", "ZrO2", "Solid", "Zirconium_dioxide",
   "Zirconia: a ceramic tough enough for knives and dental crowns; stabilised with yttria it conducts oxygen ions in lambda sensors.")

# --- the canon compounds -------------------------------------------------------------------------
PC("124-17-4", "BCA", "Butyl carbitol acetate", "C10H20O4", "Liquid", 31288,
   "A very slow ester solvent that lets coatings flow out before they dry.", "CCCCOCCOCCOC(C)=O")
PC("3648-20-2", "DUP", "Diundecyl phthalate", "C30H50O4", "Liquid", 19283,
   "A heavy phthalate plasticiser for heat-resistant cable.", "CCCCCCCCCCCOC(=O)c1ccccc1C(=O)OCCCCCCCCCCC")
PC("98-56-6", "PCBTF", "4-Chlorobenzotrifluoride", "C7H4ClF3", "Liquid", 7394,
   "A solvent exempt from smog rules, for paints and cleaners.", "FC(F)(F)c1ccc(Cl)cc1")
PC("103-74-2", "PyEtOH", "2-Pyridineethanol", "C7H9NO", "Liquid", 7675,
   "The alcohol on the way from 2-picoline to 2-vinylpyridine.", "OCCc1ccccn1")
PC("16958-92-2", "DTDA", "Ditridecyl adipate", "C32H62O4", "Liquid", 85653,
   "A lubricant base oil for compressors and gears.", "CCCCCCCCCCCCCOC(=O)CCCCC(=O)OCCCCCCCCCCCCC")
PC("20298-69-5", "Agrumex", "2-tert-Butylcyclohexyl acetate", "C12H22O2", "Liquid", 62334,
   "A woody, fruity fragrance ester for soaps and detergents.", "CC(=O)OC1CCCCC1C(C)(C)C")
PC("3748-13-8", "DIPEB13", "1,3-Diisopropenylbenzene", "C12H14", "Liquid", 77353,
   "A crosslinking monomer, and the start of the isocyanate TMXDI.", "CC(=C)c1cccc(c1)C(C)=C")
PC("4088-22-6", "M2HT", "Dioctadecylmethylamine", "C37H77N", "Solid", 77709,
   "Methyl distearylamine: quaternised, the classic fabric softener.", "CCCCCCCCCCCCCCCCCCN(C)CCCCCCCCCCCCCCCCCC")
PC("111-15-9", "EGEEA", "2-Ethoxyethyl acetate", "C6H12O3", "Liquid", 8095,
   "Cellosolve acetate, a lacquer solvent.", "CCOCCOC(C)=O")
PC("112-15-2", "CarbitolAcetate", "Carbitol acetate", "C8H16O4", "Liquid", 8165,
   "A slow ester solvent for inks and resin coatings.", "CCOCCOCCOC(C)=O")
PC("4568-28-9", "TEAStearate", "Triethanolamine stearate", "C24H51NO5", "Solid", 9867544,
   "The soap that emulsifies vanishing creams and lotions.", "OCCN(CCO)CCO.CCCCCCCCCCCCCCCCCC(O)=O")
PC("52338-87-1", "BDMAPU", "1,3-Bis(3-dimethylaminopropyl)urea", "C11H26N4O", "Liquid", 104163,
   "A low-odour amine catalyst for polyurethane foam.", "CN(C)CCCNC(=O)NCCCN(C)C")
PC("54830-99-8", "VerdylAcetate", "Tricyclodecenyl acetate", "C12H16O2", "Liquid", 108630,
   "Verdyl acetate: a fresh, green-woody fragrance ester, cheap and long-lasting.", "CC(=O)OC1CC2C3CC=CC3C1C2")
PC("7378-99-6", "DMOA", "N,N-Dimethyloctylamine", "C10H23N", "Liquid", 16224,
   "A fatty amine for short-chain quats and amine oxides.", "CCCCCCCCN(C)C")
PC("2605-78-9", "DMOAO", "Octyldimethylamine oxide", "C10H23NO", "Liquid", 62451,
   "A low-foaming surfactant for hard-surface cleaners.", "CCCCCCCC[N+](C)(C)[O-]")
PC("139-08-2", "BAC14", "Myristalkonium chloride", "C23H42ClN", "Solid", 8755,
   "A benzalkonium quat: the disinfectant of wipes, eye drops and surface sprays.", "CCCCCCCCCCCCCC[N+](C)(C)Cc1ccccc1.[Cl-]")
PC("3332-27-2", "TDMAO", "Tetradecyldimethylamine oxide", "C16H35NO", "Liquid", 18739,
   "A foam-boosting amine oxide for dish liquids and shampoos.", "CCCCCCCCCCCCCC[N+](C)(C)[O-]")
PC("4574-04-3", "TTAC", "Myristyltrimethylammonium chloride", "C17H38ClN", "Solid", 20708,
   "A cationic surfactant for hair conditioners and antiseptics.", "CCCCCCCCCCCCCC[N+](C)(C)C.[Cl-]")
PC("122-19-0", "SBAC", "Stearalkonium chloride", "C27H50ClN", "Solid", 31204,
   "A conditioning quat for hair rinses and fabric softeners.", "CCCCCCCCCCCCCCCCCC[N+](C)(C)Cc1ccccc1.[Cl-]")
PC("13597-65-4", "Willemite", "Zinc silicate", "Zn2SiO4", "Solid", 162123742,
   "Willemite: doped with manganese it glows green under electrons and ultraviolet, the green of early television tubes and fluorescent lamps.")
PC("53169-24-7", "CeZrO4", "Ceria-zirconia", "CeZrO4", "Solid", 9964855,
   "It stores and releases oxygen in a three-way catalytic converter as the engine swings between lean and rich.")
PC("2495-39-8", "NaAllylSulfonate", "Sodium allylsulfonate", "C3H5NaO3S", "Solid", 87059513,
   "A comonomer that gives acrylic fibre its dye sites.", "[Na+].C=CCS([O-])(=O)=O")
PC("1561-92-8", "NaMethallylSulfonate", "Sodium methallylsulfonate", "C4H7NaO3S", "Solid", 71650355,
   "A comonomer for acrylic fibre and concrete superplasticisers.", "[Na+].CC(=C)CS([O-])(=O)=O")
PC("56375-79-2", "MTBAC", "Methyltributylammonium chloride", "C13H30ClN", "Liquid", 91822,
   "A cheap phase-transfer catalyst.", "CCCC[N+](C)(CCCC)CCCC.[Cl-]")
PC("3012-65-5", "DiammoniumCitrate", "Diammonium citrate", "C6H14N2O7", "Solid", 6435836,
   "A buffer and food additive, and a cleaner for the inside of boilers.", "[NH4+].[NH4+].OC(=O)CC(O)(CC([O-])=O)C([O-])=O")
PC("3087-39-6", "TiOtBu4", "Titanium tert-butoxide", "C16H36O4Ti", "Liquid", 25200195,
   "A titanium alkoxide for sol-gel coatings and catalysts.", "CC(C)(C)O[Ti](OC(C)(C)C)(OC(C)(C)C)OC(C)(C)C")
PC("4419-11-8", "ABVN", "2,2'-Azobis(2,4-dimethylvaleronitrile)", "C14H24N4", "Solid", 91537,
   "A radical initiator that starts polymerisations at only 50 C.", "CC(C)CC(C)(C#N)N=NC(C)(C#N)CC(C)C")
PC("83411-71-6", "Cyanex272", "Bis(2,4,4-trimethylpentyl)phosphinic acid", "C16H35O2P", "Liquid", 157898,
   "Cyanex 272: the extractant that pulls cobalt away from nickel in battery-metal refining.",
   "CC(CC(C)(C)C)CP(O)(=O)CC(C)CC(C)(C)C")
PC("105-64-6", "DIPPDC", "Diisopropyl peroxydicarbonate", "C8H14O6", "Solid", 7769,
   "A cold initiator for PVC, shipped frozen because it decomposes violently when warm.", "CC(C)OC(=O)OOC(=O)OC(C)C")
PC("16066-38-9", "NPP", "Dipropyl peroxydicarbonate", "C8H14O6", "Liquid", 85264,
   "Another cold peroxide initiator for PVC.", "CCCOC(=O)OOC(=O)OCCC")
PC("106-86-5", "VCHO", "4-Vinylcyclohexene oxide", "C8H12O", "Liquid", 7832,
   "A reactive diluent for epoxies, and the way to the diepoxide.", "C=CC1CCC2OC2C1")
PC("126-71-6", "TiBP", "Triisobutyl phosphate", "C12H27O4P", "Liquid", 31355,
   "A defoamer for concrete, paper and textile baths.", "CC(C)COP(=O)(OCC(C)C)OCC(C)C")
PC("1300-51-2", "NaPhenolsulfonate", "Sodium phenolsulfonate", "C6H5NaO4S", "Solid", 23674503,
   "The bath salt of the electrolytic tinning lines that coat steel for cans.", "[Na+].Oc1ccc(cc1)S([O-])(=O)=O")
PC("1331-61-9", "NH4DDBS", "Ammonium dodecylbenzenesulfonate", "C18H33NO3S", "Liquid", 21881409,
   "A mild ammonium detergent for dish liquids and shampoos.", "[NH4+].CCCCCCCCCCCCc1ccc(cc1)S([O-])(=O)=O")
PC("1860-26-0", "TEHA", "Tris(2-ethylhexyl)amine", "C24H51N", "Liquid", 102705,
   "A bulky amine that extracts acids and metals out of water into oil.", "CCCCC(CC)CN(CC(CC)CCCC)CC(CC)CCCC")
PC("2304-30-5", "TBPC", "Tetrabutylphosphonium chloride", "C16H36ClP", "Solid", 75311,
   "A phase-transfer catalyst and ionic-liquid salt.", "CCCC[P+](CCCC)(CCCC)CCCC.[Cl-]")
PC("3076-63-9", "TLP", "Trilauryl phosphite", "C36H75O3P", "Liquid", 76495,
   "An antioxidant for PVC and polyolefins.", "CCCCCCCCCCCCOP(OCCCCCCCCCCCC)OCCCCCCCCCCCC")
PC("3084-40-0", "DEHMP", "Diethyl (hydroxymethyl)phosphonate", "C5H13O4P", "Liquid", 76513,
   "A building block for phosphorus flame retardants in polyurethane foam.", "CCOP(=O)(CO)OCC")
PC("11070-44-3", "MTHPA", "Methyltetrahydrophthalic anhydride", "C9H10O3", "Liquid", 3033842,
   "The liquid hardener of the epoxies that insulate transformers and motors.", "CC1=CCC2C(=O)OC(=O)C2C1")
PC("17526-94-2", "TDIUrone", "Toluene bis(dimethylurea)", "C13H20N4O2", "Solid", 87146,
   "A latent accelerator that lets dicyandiamide cure epoxy adhesives at a lower heat.", "Cc1ccc(NC(=O)N(C)C)cc1NC(=O)N(C)C")
PC("7473-98-5", "HMPP", "2-Hydroxy-2-methylpropiophenone", "C10H12O2", "Liquid", 81984,
   "A photoinitiator: ultraviolet light splits it into radicals that cure inks, varnishes and 3D-printing resins in a second.",
   "CC(C)(O)C(=O)c1ccccc1")
PC("7360-38-5", "GTEH", "Glyceryl tris(2-ethylhexanoate)", "C27H50O6", "Liquid", 110973,
   "A light, non-greasy emollient oil for cosmetics.", "CCCCC(CC)C(=O)OCC(COC(=O)C(CC)CCCC)OC(=O)C(CC)CCCC")
PC("12645-49-7", "MnZnFerrite", "Manganese-zinc ferrite", "MnZnFe4O8", "Solid", 10397692,
   "The soft magnetic ceramic of transformer and inductor cores in every switching power supply.")
PC("126-97-6", "MEATG", "Monoethanolamine thioglycolate", "C4H11NO3S", "Liquid", 160430,
   "The active of low-odour perms and depilatory creams: it breaks the sulfur bridges in hair.", "OCCN.OC(=O)CS")
PC("26761-40-0", "DIDP", "Diisodecyl phthalate", "C28H46O4", "Liquid", 33599,
   "A heavy plasticiser for cable and car-interior PVC.", "CC(C)CCCCCCCOC(=O)c1ccccc1C(=O)OCCCCCCCC(C)C")
PC("27178-16-1", "DIDA", "Diisodecyl adipate", "C26H50O4", "Liquid", 33733,
   "A plasticiser that keeps PVC flexible in the cold.", "CC(C)CCCCCCCOC(=O)CCCCC(=O)OCCCCCCCC(C)C")
PC("25550-98-5", "PDDP", "Phenyl diisodecyl phosphite", "C26H47O3P", "Liquid", 16212880,
   "A mixed phosphite that keeps PVC from yellowing as it is processed.", "CC(C)CCCCCCCOP(OCCCCCCCC(C)C)Oc1ccccc1")
PC("26544-23-0", "DPDP", "Diphenyl isodecyl phosphite", "C22H31O3P", "Liquid", 9951488,
   "A phosphite stabiliser for PVC and ABS.", "CC(C)CCCCCCCOP(Oc1ccccc1)Oc1ccccc1")
PC("25448-25-3", "TDP", "Triisodecyl phosphite", "C30H63O3P", "Liquid", 117488,
   "An all-alkyl phosphite stabiliser.", "CC(C)CCCCCCCOP(OCCCCCCCC(C)C)OCCCCCCCC(C)C")
WK("12047-11-9", "BaFerrite", "Barium hexaferrite", "BaFe12O19", "Solid", "Barium_ferrite",
   "The ceramic permanent magnet of fridge doors, loudspeakers and small motors.")

# --- the reactions -------------------------------------------------------------------------------
E4.reactions += [
    R("Zinc Silicate", "2 ZnO + Sand -> Willemite", HEAT, "Zinc oxide and silica fired together.", wiki=P["Willemite"], T=1200),
    R("Ceria", "Ce + O2 -> CeO2", HEAT, "Cerium burned in air to the dioxide.", wiki=P["CeO2"], T=300),
    R("Sodium Phenolsulfonate", "Phenol + H2SO4 + NaOH -> NaPhenolsulfonate + 2 H2O", FLASK,
      "Phenol sulfonated and the acid neutralised.", wiki=P["NaPhenolsulfonate"], T=100),
    R("Triethanolamine Stearate", "TEA + StearicAcid -> TEAStearate", MIX,
      "Stearic acid neutralised with triethanolamine.", wiki=P["TEAStearate"]),
    R("Diammonium Citrate", "Citric + 2 NH3 -> DiammoniumCitrate", MIX,
      "Citric acid two-thirds neutralised with ammonia.", wiki=P["DiammoniumCitrate"]),
    R("Monoethanolamine Thioglycolate", "MEA + TGA -> MEATG", MIX,
      "Thioglycolic acid neutralised with ethanolamine.", wiki=P["MEATG"]),
]
E5.reactions += [
    R("Butyl Carbitol", "Butoxyethanol + EO -> DEGBE", PRESS, "Butyl cellosolve takes one more ethylene oxide.", wiki=P["DEGBE"], T=150),
    R("Butyl Carbitol Acetate", "DEGBE + AcOH -> BCA + H2O", FLASK, "Butyl carbitol esterified.", wiki=P["BCA"], T=120),
    R("1-Undecanol", "Undecanal + H2 -> Undecanol", CAT, "Undecanal hydrogenated.", wiki=P["Undecanol"], cat="Ni", T=120),
    R("Diundecyl Phthalate", "PhthalicAnhydride + 2 Undecanol -> DUP + H2O", FLASK,
      "Phthalic anhydride esterified with undecanol.", wiki=P["DUP"], T=200),
    R("Propylene Trimer", "3 Propylene -> Nonene", PRESS,
      "Propylene oligomerised under pressure over solid phosphoric acid; the nine-carbon cut is taken off.", wiki=P["Nonene"], T=200),
    R("Oxo Tridecanol", "Dodecene + CO + 2 H2 -> Tridecanol", HIGHP,
      "Hydroformylation: synthesis gas adds a CHO to the olefin, then the aldehyde is hydrogenated.", wiki=P["Tridecanol"], cat="Co", T=170),
    R("Oxo Isodecanol", "Nonene + CO + 2 H2 -> Isodecanol", HIGHP,
      "Propylene trimer hydroformylated and hydrogenated.", wiki=P["Isodecanol"], cat="Co", T=170),
    R("Ditridecyl Adipate", "Adipic + 2 Tridecanol -> DTDA + 2 H2O", FLASK,
      "Adipic acid esterified with tridecanol.", wiki=P["DTDA"], T=200),
    R("4-Chlorobenzotrifluoride", "pChlorotoluene + 3 Cl2 + 3 HF -> PCBTF + 6 HCl", LIGHT,
      "The methyl group photochlorinated to CCl3, then the chlorines swapped for fluorine with hydrogen fluoride.", wiki=P["PCBTF"]),
    R("2-Pyridineethanol", "Picoline2 + CH2O -> PyEtOH", PRESS,
      "2-Picoline's methyl group adds to formaldehyde.", wiki=P["PyEtOH"], T=150),
    R("2-tert-Butylcyclohexanol", "TBP2 + 3 H2 -> tBuCyclohexanol2", CAT,
      "2-tert-Butylphenol hydrogenated, mostly to the cis alcohol.", wiki=P["tBuCyclohexanol2"], cat="Ni", T=150),
    R("Agrumex", "tBuCyclohexanol2 + AceticAnhydride -> Agrumex + AcOH", FLASK,
      "The cyclohexanol acetylated.", wiki=P["Agrumex"], T=80),
    R("1,3-Diisopropenylbenzene", "DIPB -> DIPEB13 + 2 H2", CAT,
      "Diisopropylbenzene dehydrogenated over iron oxide, as ethylbenzene is to styrene.", wiki=P["DIPEB13"], cat="Hematite", T=600),
    R("Methyl Distearylamine", "2 StearylAlcohol + Methylamine -> M2HT + 2 H2O", CAT,
      "Stearyl alcohol aminated with methylamine over a copper catalyst.", wiki=P["M2HT"], cat="CopperChromite", T=220),
    R("2-Ethoxyethanol", "Ethanol + EO -> EGEE", PRESS, "Ethanol opens ethylene oxide.", wiki=P["EGEE"], T=150),
    R("Carbitol", "EGEE + EO -> Carbitol", PRESS, "Cellosolve takes a second ethylene oxide.", wiki=P["Carbitol"], T=150),
    R("Cellosolve Acetate", "EGEE + AcOH -> EGEEA + H2O", FLASK, "2-Ethoxyethanol esterified.", wiki=P["EGEEA"], T=120),
    R("Carbitol Acetate", "Carbitol + AcOH -> CarbitolAcetate + H2O", FLASK, "Carbitol esterified.", wiki=P["CarbitolAcetate"], T=120),
    R("Bis(dimethylaminopropyl)urea", "2 DMAPA + Urea -> BDMAPU + 2 NH3", FLASK,
      "Urea refluxed in excess amine until both of its nitrogens are swapped, ammonia driven off.", wiki=P["BDMAPU"], T=160),
    R("Verdyl Acetate", "DCPD + AcOH -> VerdylAcetate", CAT,
      "Acetic acid added across a double bond of dicyclopentadiene in acid.", wiki=P["VerdylAcetate"], cat="H2SO4", T=100),
    R("Myristyl Alcohol", "MyristicAcid + 2 H2 -> Tetradecanol + H2O", HIGHP,
      "Myristic acid hydrogenated to the alcohol over Adkins' copper chromite.", wiki=P["Tetradecanol"], cat="CopperChromite", T=250),
    R("Dimethyltetradecylamine", "Tetradecanol + Me2NH -> DMA14 + H2O", CAT,
      "The fatty alcohol aminated with dimethylamine.", wiki=P["DMA14"], cat="CopperChromite", T=220),
    R("Benzalkonium Chloride", "DMA14 + BenzylChloride -> BAC14", MIX, "The fatty amine quaternised with benzyl chloride.", wiki=P["BAC14"]),
    R("Tetradecyldimethylamine Oxide", "DMA14 + H2O2 -> TDMAO + H2O", MIX, "The amine oxidised with hydrogen peroxide.", wiki=P["TDMAO"]),
    R("Myristyltrimethylammonium Chloride", "DMA14 + CH3Cl -> TTAC", MIX, "The amine quaternised with methyl chloride.", wiki=P["TTAC"]),
    R("Dimethyloctadecylamine", "StearylAlcohol + Me2NH -> DMA18 + H2O", CAT,
      "Stearyl alcohol aminated with dimethylamine.", wiki=P["DMA18"], cat="CopperChromite", T=220),
    R("Stearalkonium Chloride", "DMA18 + BenzylChloride -> SBAC", MIX, "Quaternised with benzyl chloride.", wiki=P["SBAC"]),
    R("Dimethyloctylamine", "Octanol + Me2NH -> DMOA + H2O", CAT,
      "Octanol aminated with dimethylamine.", wiki=P["DMOA"], cat="CopperChromite", T=220),
    R("Octyldimethylamine Oxide", "DMOA + H2O2 -> DMOAO + H2O", MIX, "The amine oxidised with hydrogen peroxide.", wiki=P["DMOAO"]),
    R("Zirconia", "Zircon -> ZrO2 + Sand", ARC,
      "Zircon sand dissociated in a plasma arc; the silica is leached away afterwards.", wiki=P["ZrO2"]),
    R("Ceria-Zirconia", "CeO2 + ZrO2 -> CeZrO4", HEAT, "The two oxides co-fired into a solid solution.", wiki=P["CeZrO4"], T=1000),
    R("Sodium Allylsulfonate", "AllylChloride + Na2SO3 -> NaAllylSulfonate + NaCl", MIX,
      "Allyl chloride on sodium sulfite.", wiki=P["NaAllylSulfonate"]),
    R("Sodium Methallylsulfonate", "MethallylCl + Na2SO3 -> NaMethallylSulfonate + NaCl", MIX,
      "Methallyl chloride on sodium sulfite.", wiki=P["NaMethallylSulfonate"]),
    R("Methyltributylammonium Chloride", "Tributylamine + CH3Cl -> MTBAC", MIX,
      "Tributylamine quaternised with methyl chloride.", wiki=P["MTBAC"]),
    R("Titanium tert-Butoxide", "TiCl4 + 4 tBuOH + 4 NH3 -> TiOtBu4 + 4 NH4Cl", FLASK,
      "Titanium tetrachloride on tert-butanol, ammonia taking up the hydrogen chloride.", wiki=P["TiOtBu4"], T=20),
    R("ABVN", "2 MIBK + N2H4 + 2 HCN + Cl2 -> ABVN + 2 H2O + 2 HCl", FLASK,
      "MIBK's ketazine takes up hydrogen cyanide, and chlorine oxidises the hydrazo link to azo.", wiki=P["ABVN"], T=20),
    R("Cyanex 272", "2 Diisobutylene + Phosphine + 2 H2O2 -> Cyanex272 + 2 H2O", CAT,
      "Phosphine added twice across diisobutylene by a radical chain, and the phosphine oxidised to the acid.",
      wiki=P["Cyanex272"], cat="AIBN", T=90),
    R("Diisopropyl Peroxydicarbonate", "2 Isopropanol + 2 COCl2 + H2O2 + 2 NaOH -> DIPPDC + 2 NaCl + 2 HCl + 2 H2O", COOL,
      "Isopropyl chloroformate from isopropanol and phosgene, joined two-to-one by alkaline peroxide in the cold.",
      wiki=P["DIPPDC"], T=0),
    R("Dipropyl Peroxydicarbonate", "2 Propanol + 2 COCl2 + H2O2 + 2 NaOH -> NPP + 2 NaCl + 2 HCl + 2 H2O", COOL,
      "The same with n-propanol.", wiki=P["NPP"], T=0),
    R("Vinylcyclohexene Oxide", "VCH + H2O2 -> VCHO + H2O", FLASK,
      "The ring double bond of vinylcyclohexene epoxidised.", wiki=P["VCHO"], T=40),
    R("Triisobutyl Phosphate", "POCl3 + 3 Isobutanol -> TiBP + 3 HCl", FLASK,
      "Phosphorus oxychloride on isobutanol.", wiki=P["TiBP"], T=40),
    R("LAS Acid", "Dodecylbenzene + SO3 -> DDBSA", FLASK,
      "Dodecylbenzene sulfonated with sulfur trioxide in a falling-film reactor.", wiki=P["DDBSA"], T=50),
    R("Ammonium Dodecylbenzenesulfonate", "DDBSA + NH3 -> NH4DDBS", MIX, "LAS acid neutralised with ammonia.", wiki=P["NH4DDBS"]),
    R("Tris(2-ethylhexyl)amine", "3 2EH + NH3 -> TEHA + 3 H2O", CAT,
      "2-Ethylhexanol aminated three times over.", wiki=P["TEHA"], cat="CopperChromite", T=240),
    R("Tetrabutylphosphonium Chloride", "PBu3 + BuCl -> TBPC", MIX, "Tributylphosphine quaternised with butyl chloride.", wiki=P["TBPC"]),
    R("Trilauryl Phosphite", "TPPite + 3 Dodecanol -> TLP + 3 Phenol", FLASK,
      "Triphenyl phosphite transesterified with lauryl alcohol; phenol distils off.", wiki=P["TLP"], T=160),
    R("Diethyl Hydroxymethylphosphonate", "DEPhosphite + CH2O -> DEHMP", MIX,
      "Diethyl phosphite adds to formaldehyde.", wiki=P["DEHMP"]),
    R("MTHPA", "Isoprene + MaleicAnhydride -> MTHPA", HEAT,
      "Isoprene and maleic anhydride joined by a Diels-Alder reaction.", wiki=P["MTHPA"], T=60),
    R("Toluene Bis(dimethylurea)", "TDI + 2 Me2NH -> TDIUrone", MIX,
      "Both isocyanate groups of TDI capped with dimethylamine.", wiki=P["TDIUrone"]),
    R("Isobutyrophenone", "Benzene + IsobutyrylCl -> Isobutyrophenone + HCl", FLASK,
      "Benzene acylated with isobutyryl chloride on aluminium chloride.", wiki=P["Isobutyrophenone"], T=40),
    R("HMPP Photoinitiator", "Isobutyrophenone + Cl2 + 2 NaOH -> HMPP + 2 NaCl + H2O", FLASK,
      "The ketone chlorinated next to the carbonyl and the chlorine swapped for hydroxyl.", wiki=P["HMPP"], T=40),
    R("Triethylhexanoin", "Glycerol + 3 EHAcid -> GTEH + 3 H2O", FLASK,
      "Glycerol esterified with 2-ethylhexanoic acid.", wiki=P["GTEH"], T=220),
    R("Manganese-Zinc Ferrite", "2 Hematite + MnO + ZnO -> MnZnFerrite", SMELT,
      "Iron, manganese and zinc oxides calcined, pressed and sintered into a spinel.", wiki=P["MnZnFerrite"], T=1300),
    R("Diisodecyl Phthalate", "PhthalicAnhydride + 2 Isodecanol -> DIDP + H2O", FLASK,
      "Phthalic anhydride esterified with isodecanol.", wiki=P["DIDP"], T=220),
    R("Diisodecyl Adipate", "Adipic + 2 Isodecanol -> DIDA + 2 H2O", FLASK,
      "Adipic acid esterified with isodecanol.", wiki=P["DIDA"], T=220),
    R("Phenyl Diisodecyl Phosphite", "TPPite + 2 Isodecanol -> PDDP + 2 Phenol", HEAT,
      "Triphenyl phosphite transesterified with isodecanol, two of three phenols swapped.", wiki=P["PDDP"], T=160),
    R("Diphenyl Isodecyl Phosphite", "TPPite + Isodecanol -> DPDP + Phenol", FLASK,
      "Triphenyl phosphite transesterified once.", wiki=P["DPDP"], T=140),
    R("Triisodecyl Phosphite", "PCl3 + 3 Isodecanol -> TDP + 3 HCl", COOL,
      "Phosphorus trichloride on isodecanol, with base to take up the acid.", wiki=P["TDP"], T=10),
    R("Barium Hexaferrite", "BaCO3 + 6 Hematite -> BaFerrite + CO2", SMELT,
      "Witherite and iron oxide calcined, milled, pressed in a magnetic field and sintered.", wiki=P["BaFerrite"], T=1250),
]

# Milestones for the stretches this part lengthened (messages only).
import authored_content as _C  # noqa: E402
from gen_authored import Milestone  # noqa: E402
_C.MILESTONES += [
    Milestone("BaFerrite", message="Ceramic magnets: Philips' barium ferrite (1952) is cheap, never rusts and holds its field, so it went on every fridge door and into every loudspeaker."),
]
import authored_canon_23  # noqa: E402,F401
