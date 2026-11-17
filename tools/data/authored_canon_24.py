"""
Curieosity's industrial chemistry, part 24 (see authored_canon.py): the canon records that were
flagged as doubtful, checked one by one and given PubChem pages and routes, with the intermediates
they need: 3,4-dichloroaniline for diuron, cyanogen chloride for the guanidine accelerators,
2,4-xylidine for Pigment Yellow 13, isononanoic and isostearic acids for metal soaps and cosmetics,
tolyltriazole, the metal neodecanoates, and the BDP flame retardant.
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


# --- intermediates ------------------------------------------------------------------------------
WK("506-77-4", "CNCl", "Cyanogen chloride", "CClN", "Gas", "Cyanogen_chloride",
   "A toxic gas made from cyanide and chlorine; it trimerises to cyanuric chloride and builds guanidines. Its production is reported under the Chemical Weapons Convention.",
   "ClC#N")
PC("99-54-7", "DCNB34", "3,4-Dichloronitrobenzene", "C6H3Cl2NO2", "Solid", "3,4-Dichloronitrobenzene",
   "o-Dichlorobenzene nitrated.", "O=[N+]([O-])c1ccc(Cl)c(Cl)c1")
WK("95-76-1", "DCA34", "3,4-Dichloroaniline", "C6H5Cl2N", "Solid", "3,4-Dichloroaniline",
   "The amine behind the urea and anilide herbicides: diuron, linuron, propanil.", "Nc1ccc(Cl)c(Cl)c1")
PC("95-68-1", "Xylidine24", "2,4-Xylidine", "C8H11N", "Liquid", "2,4-Dimethylaniline",
   "m-Xylene nitrated and reduced; a coupler amine for yellow pigments.", "Cc1ccc(N)c(C)c1")
PC("97-36-9", "AAMX", "Acetoacet-m-xylidide", "C12H15NO2", "Solid", 222464,
   "The coupling component of Pigment Yellow 13.", "CC(=O)CC(=O)Nc1ccc(C)cc1C")
PC("5435-64-3", "Isononanal", "3,5,5-Trimethylhexanal", "C9H18O", "Liquid", "3,5,5-Trimethylhexanal",
   "Diisobutylene hydroformylated.", "CC(CC=O)CC(C)(C)C")
PC("3302-10-1", "INAcid", "Isononanoic acid", "C9H18O2", "Liquid", "3,5,5-Trimethylhexanoic acid",
   "A branched acid for paint driers, lubricant esters and cosmetic emollients.", "CC(CC(O)=O)CC(C)(C)C")
PC("30399-84-9", "IsostearicAcid", "Isostearic acid", "C18H36O2", "Liquid", "Isostearic acid",
   "A branched C18 acid that stays liquid where stearic acid would set: for cosmetics and lubricants.",
   "CC(C)CCCCCCCCCCCCCCC(O)=O")
PC("496-72-0", "DAT34", "3,4-Diaminotoluene", "C7H10N2", "Solid", "3,4-Diaminotoluene",
   "The ortho-diamine that nitrous acid closes into tolyltriazole.", "Cc1ccc(N)c(N)c1")
PC("29385-43-1", "TTA", "Tolyltriazole", "C7H7N3", "Solid", "Tolyltriazole",
   "The corrosion inhibitor for copper in cooling water, antifreeze and dishwasher tablets.", "Cc1ccc2[nH]nnc2c1")
PC("111-41-1", "AEEA", "Aminoethylethanolamine", "C4H12N2O", "Liquid", "Aminoethylethanolamine",
   "Ethylenediamine with one ethylene oxide on it.", "NCCNCCO")
PC("675-62-7", "TFPMeSiCl2", "(3,3,3-Trifluoropropyl)methyldichlorosilane", "C4H7Cl2F3Si", "Liquid",
   "Dichloro(methyl)(3,3,3-trifluoropropyl)silane", "The monomer of fluorosilicone rubber.", "C[Si](Cl)(Cl)CCC(F)(F)F")
PC("91-68-9", "DEAP", "3-Diethylaminophenol", "C10H15NO", "Solid", "3-Diethylaminophenol",
   "Resorcinol aminated with diethylamine; the half of the rhodamine and coumarin dyes.", "CCN(CC)c1cccc(O)c1")
PC("100-86-7", "DMBC", "Dimethylbenzylcarbinol", "C10H14O", "Solid", "2-Methyl-1-phenyl-2-propanol",
   "A floral, lilac-scented alcohol for perfumes.", "CC(C)(O)Cc1ccccc1")
WK("74-96-4", "EtBr", "Bromoethane", "C2H5Br", "Liquid", "Bromoethane", "Ethyl bromide, an ethylating agent.", "CCBr")
PC("109-83-1", "MMEA", "N-Methylethanolamine", "C3H9NO", "Liquid", "N-Methylethanolamine",
   "Methylamine with one ethylene oxide on it.", "CNCCO")
PC("95-51-2", "oChloroaniline", "2-Chloroaniline", "C6H6ClN", "Liquid", "2-Chloroaniline",
   "o-Nitrochlorobenzene reduced; for pigments and the PU curative MOCA.", "Nc1ccccc1Cl")
PC("102-06-7", "DPhG", "Diphenylguanidine", "C13H13N3", "Solid", 7594,
   "A secondary accelerator that speeds the sulfur cure of tyre treads, especially silica-filled ones.", "N=C(Nc1ccccc1)Nc1ccccc1")

# --- the canon compounds -------------------------------------------------------------------------
WK("330-54-1", "Diuron", "Diuron", "C9H10Cl2N2O", "Solid", "DCMU",
   "A urea herbicide that blocks photosystem II: weed control on railways and in sugarcane, and the tool by which plant scientists stop photosynthesis at a known point.",
   "CN(C)C(=O)Nc1ccc(Cl)c(Cl)c1")
PC("5102-83-0", "PY13", "Pigment Yellow 13", "C36H34Cl2N6O4", "Solid", 73462,
   "A strong diarylide yellow for printing inks.", "CC(=O)C(N=Nc1ccc(cc1Cl)-c1ccc(N=NC(C(C)=O)C(=O)Nc2ccc(C)cc2C)c(Cl)c1)C(=O)Nc1ccc(C)cc1C")
PC("4531-49-1", "PY17", "Pigment Yellow 17", "C34H30Cl2N6O6", "Solid", 91539,
   "A greenish diarylide yellow for packaging inks.", "COc1ccccc1NC(=O)C(N=Nc1ccc(cc1Cl)-c1ccc(N=NC(C(C)=O)C(=O)Nc2ccccc2OC)c(Cl)c1)C(C)=O")
PC("53988-05-9", "CaINA2", "Calcium isononanoate", "C18H34CaO4", "Solid", 62075,
   "An auxiliary paint drier that keeps the film from wrinkling.", "[Ca+2].CC(CC([O-])=O)CC(C)(C)C.CC(CC([O-])=O)CC(C)(C)C")
PC("66085-00-5", "GMIS", "Glyceryl monoisostearate", "C21H42O4", "Liquid", 3016527,
   "An emollient and emulsifier for creams and lipsticks.", "CC(C)CCCCCCCCCCCCCCC(=O)OCC(O)CO")
PC("66469-15-6", "KIsostearate", "Potassium isostearate", "C18H35KO2", "Liquid", 23673612,
   "A soap that stays liquid, for cleansers.", "[K+].CC(C)CCCCCCCCCCCCCCC([O-])=O")
PC("61417-49-0", "KRTTS", "Isopropyl triisostearoyl titanate", "C57H112O7Ti", "Liquid", 162941,
   "A titanate coupling agent that lets mineral fillers mix into plastics like they belong there.",
   "CC(C)O[Ti](OC(=O)CCCCCCCCCCCCCCC(C)C)(OC(=O)CCCCCCCCCCCCCCC(C)C)OC(=O)CCCCCCCCCCCCCCC(C)C")
PC("4297-95-4", "NaPhPinate", "Sodium phenylphosphinate", "C6H6NaO2P", "Solid", 24194119,
   "A heat stabiliser and nucleating agent for nylon.", "[Na+].[O-][PH](=O)c1ccccc1")
PC("64665-57-2", "NaTTA", "Sodium tolyltriazole", "C7H6N3Na", "Solid", 23687327,
   "The water-soluble form of tolyltriazole for cooling towers.", "[Na+].Cc1ccc2nn[n-]c2c1")
PC("5397-34-2", "BPS24", "2,4'-Sulfonyldiphenol", "C12H10O4S", "Solid", 79381,
   "A colour developer for thermal paper.", "Oc1ccc(cc1)S(=O)(=O)c1ccccc1O")
PC("121-93-7", "IPDEA", "N-Isopropyldiethanolamine", "C7H17NO2", "Liquid", 8498,
   "A tertiary alkanolamine for gas treating and polyurethane catalysis.", "CC(C)N(CCO)CCO")
PC("26519-91-5", "MeCp", "Methylcyclopentadiene", "C6H8", "Liquid", 66775,
   "Recovered from cracker oils; the ring of the fuel additive MMT and of high-energy fuels.", "CC1=CC=CC1")
PC("26472-00-4", "MeCpDimer", "Methylcyclopentadiene dimer", "C12H16", "Liquid", 3033878,
   "The form methylcyclopentadiene is stored in; for resins and high-density fuels.", "CC1=CC2CC1C1C=C(C)CC21")
PC("150-39-0", "HEDTA", "HEDTA", "C10H18N2O7", "Solid", 8773,
   "A chelating agent that holds iron in solution in micronutrient fertilisers.", "OCCN(CCN(CC(O)=O)CC(O)=O)CC(O)=O")
PC("101-96-2", "DSBPPD", "N,N'-Di-sec-butyl-p-phenylenediamine", "C14H24N2", "Liquid", 7589,
   "An antioxidant that keeps petrol from gumming in storage.", "CCC(C)Nc1ccc(NC(C)CC)cc1")
PC("2374-14-3", "D3F", "Trifluoropropylmethylcyclotrisiloxane", "C12H21F9O3Si3", "Liquid", 75410,
   "The ring monomer of fluorosilicone, the rubber of fuel-system seals in aircraft.",
   "C[Si]1(CCC(F)(F)F)O[Si](C)(CCC(F)(F)F)O[Si](C)(CCC(F)(F)F)O1")
PC("88-20-0", "oTSA", "o-Toluenesulfonic acid", "C7H8O3S", "Solid", 6925, "The ortho sulfonation product, on the way to saccharin.",
   "Cc1ccccc1S(O)(=O)=O")
PC("3101-60-8", "PTBPGE", "p-tert-Butylphenyl glycidyl ether", "C13H18O2", "Liquid", 18360,
   "A reactive diluent that thins epoxy resins.", "CC(C)(C)c1ccc(OCC2CO2)cc1")
PC("106726-11-8", "NdND3", "Neodymium neodecanoate", "C30H57NdO6", "Liquid", 176033,
   "The neodymium catalyst for high-cis polybutadiene, the rubber of tyre treads that grip and wear well.",
   "[Nd+3].CCCCCCC(C)(C)C([O-])=O.CCCCCCC(C)(C)C([O-])=O.CCCCCCC(C)(C)C([O-])=O")
PC("18600-59-4", "UV3638", "UV-3638", "C22H12N2O4", "Solid", 3098422,
   "A benzoxazinone UV absorber for polyester and polycarbonate.",
   "O=c1oc(-c2ccc(cc2)-c2nc3ccccc3c(=O)o2)nc2ccccc12")
PC("25054-76-6", "OAPB", "Oleamidopropyl betaine", "C25H48N2O3", "Liquid", 90698,
   "A mild amphoteric surfactant that thickens shampoos.", "CCCCCCCCC=CCCCCCCCC(=O)NCCC[N+](C)(C)CC([O-])=O")
PC("36768-62-4", "AminoTMP", "4-Amino-2,2,6,6-tetramethylpiperidine", "C9H20N2", "Liquid", 37524,
   "A hindered amine building block for light stabilisers.", "CC1(C)CC(N)CC(C)(C)N1")
PC("4454-16-4", "NiEH2", "Nickel(II) 2-ethylhexanoate", "C16H30NiO4", "Liquid", 24231,
   "An oil-soluble nickel catalyst precursor for hydrogenation and polybutadiene.",
   "[Ni+2].CCCCC(CC)C([O-])=O.CCCCC(CC)C([O-])=O")
PC("52467-63-7", "TCMAC", "Tricetylmethylammonium chloride", "C49H102ClN", "Solid", 104201,
   "A three-tailed quat for organoclays and hair conditioners.",
   "[Cl-].CCCCCCCCCCCCCCCC[N+](C)(CCCCCCCCCCCCCCCC)CCCCCCCCCCCCCCCC")
PC("53378-51-1", "NaDIBDTPhos", "Sodium diisobutyl dithiophosphate", "C8H18NaO2PS2", "Solid", 129894350,
   "A flotation collector for copper, zinc and gold ores.", "[Na+].CC(C)COP([S-])(=S)OCC(C)C")
PC("583-39-1", "MBI", "2-Mercaptobenzimidazole", "C7H6N2S", "Solid", 707035,
   "An antioxidant that keeps rubber from ageing in heat.", "S=c1[nH]c2ccccc2[nH]1")
PC("58985-18-5", "DHTA", "Dihydroterpinyl acetate", "C12H22O2", "Liquid", 6631,
   "A fresh, piney-citrus ester for soaps and household fragrance.", "CC(=O)OC(C)(C)C1CCC(C)CC1")
PC("63738-22-7", "TGMXDA", "Tetraglycidyl-m-xylylenediamine", "C20H28N2O4", "Liquid", 113842,
   "A four-armed epoxy that crosslinks tightly, for heat-resistant composites.",
   "C(N(CC1CO1)CC1CO1)c1cccc(CN(CC2CO2)CC2CO2)c1")
PC("7047-84-9", "AlMonostearate", "Aluminium monostearate", "C18H37AlO4", "Solid", 16682987,
   "A gelling agent that thickens oils for paints, greases and cosmetics.", "O[Al](O)OC(=O)CCCCCCCCCCCCCCCCC")
PC("7328-22-5", "DEGBEMA", "Diethylene glycol butyl ether methacrylate", "C12H22O4", "Liquid", 81768,
   "A flexible methacrylate monomer for coatings.", "CCCCOCCOCCOC(=O)C(C)=C")
PC("764-99-8", "DEGDVE", "Diethylene glycol divinyl ether", "C8H14O3", "Liquid", 12998,
   "A reactive diluent for ultraviolet-cured inks.", "C=COCCOCCOC=C")
PC("831-52-7", "NaPicramate", "Sodium picramate", "C6H4N3NaO5", "Solid", 45157719,
   "Picric acid half-reduced: a dye intermediate and a hair-colour ingredient.", "[Na+].Nc1cc(cc(c1[O-])[N+]([O-])=O)[N+]([O-])=O")
PC("84-15-1", "oTerphenyl", "o-Terphenyl", "C18H14", "Solid", 6766,
   "A by-product of making biphenyl; with its isomers, a high-temperature heat-transfer fluid.", "c1ccc(cc1)-c1ccccc1-c1ccccc1")
PC("89686-69-1", "DTHFP", "2,2-Di(2-tetrahydrofuryl)propane", "C11H20O2", "Liquid", 551484,
   "A modifier that steers the anionic polymerisation of tyre rubber toward more vinyl units, for wet grip.",
   "CC(C)(C1CCCO1)C1CCCO1")
PC("91-44-1", "Coumarin1", "7-Diethylamino-4-methylcoumarin", "C14H17NO2", "Solid", 7050,
   "Coumarin 1: an optical brightener for textiles and a blue laser dye.", "CCN(CC)c1ccc2c(C)cc(=O)oc2c1")
PC("46830-22-2", "ADBAC", "Acryloyloxyethyldimethylbenzylammonium chloride", "C14H20ClNO2", "Solid", 162073,
   "A cationic monomer for flocculants.", "[Cl-].C=CC(=O)OCC[N+](C)(C)Cc1ccccc1")
PC("151-05-3", "DMBCA", "Dimethylbenzylcarbinyl acetate", "C12H16O2", "Liquid", 9024,
   "A fruity-floral ester for perfumes.", "CC(=O)OC(C)(C)Cc1ccccc1")
PC("27253-29-8", "ZnND2", "Zinc neodecanoate", "C20H38O4Zn", "Liquid", 117959,
   "A catalyst for polyurethane elastomers and a paint drier.", "[Zn+2].CCCCCCC(C)(C)C([O-])=O.CCCCCCC(C)(C)C([O-])=O")
PC("27253-30-1", "LiND", "Lithium neodecanoate", "C10H19LiO2", "Liquid", 121494078,
   "An oil-soluble lithium salt for driers and anionic polymerisation.", "[Li+].CCCCCCC(C)(C)C([O-])=O")
PC("68084-48-0", "CuND2", "Copper(II) neodecanoate", "C20H38CuO4", "Liquid", 163179,
   "An oil-soluble copper salt for wood preservatives and catalysts.", "[Cu+2].CCCCCCC(C)(C)C([O-])=O.CCCCCCC(C)(C)C([O-])=O")
PC("5421-46-5", "NH4TG", "Ammonium thioglycolate", "C2H7NO2S", "Liquid", 16211171,
   "The reducing agent of the classic home perm.", "[NH4+].[O-]C(=O)CS")
PC("98516-30-4", "PGEEA", "Propylene glycol monoethyl ether acetate", "C7H14O3", "Liquid", 14847874,
   "A coatings and photoresist solvent.", "CCOCC(C)OC(C)=O")
PC("21089-06-5", "KHEDP", "Potassium etidronate", "C2H7KO7P2", "Solid", 87311972,
   "A scale inhibitor for water treatment and detergents.", "[K+].CC(O)(P(O)(O)=O)P(O)([O-])=O")
PC("24245-27-0", "DPGHCl", "Diphenylguanidine hydrochloride", "C13H14ClN3", "Solid", 520104,
   "Diphenylguanidine as its salt.", "Cl.N=C(Nc1ccccc1)Nc1ccccc1")
PC("1530-32-1", "ETPPBr", "Ethyltriphenylphosphonium bromide", "C20H20BrP", "Solid", 73727,
   "The catalyst that grows epoxy resins longer, and a Wittig reagent.", "[Br-].CC[P+](c1ccccc1)(c1ccccc1)c1ccccc1")
PC("97-39-2", "DOTG", "Di-o-tolylguanidine", "C15H17N3", "Solid", 7333,
   "A secondary rubber accelerator.", "Cc1ccccc1NC(=N)Nc1ccccc1C")
PC("10017-56-8", "TEAPhosphate", "Triethanolamine phosphate", "C6H18NO7P", "Solid", 61430,
   "A corrosion inhibitor for metalworking fluids.", "OCCN(CCO)CCO.OP(O)(O)=O")
PC("13870-28-5", "Na2Si2O5", "Sodium disilicate", "Na2Si2O5", "Solid", 156595375,
   "A layered silicate that softens water in detergents in place of phosphate.")
PC("29508-45-0", "DEDMAC", "Diethyldimethylammonium chloride", "C6H16ClN", "Solid", 22025857,
   "A quat for electrolytes and as a template for zeolite crystals.", "[Cl-].CC[N+](C)(C)CC")
PC("139-96-8", "TEALS", "Triethanolamine lauryl sulfate", "C18H41NO7S", "Liquid", 8777,
   "A gentle foaming surfactant for shampoos.", "OCC[NH+](CCO)CCO.CCCCCCCCCCCCOS([O-])(=O)=O")
PC("32426-11-2", "ODDMAC", "Octyldecyldimethylammonium chloride", "C20H44ClN", "Solid", 61906,
   "A twin-tailed quat disinfectant for food plants and hospitals.", "[Cl-].CCCCCCCCCC[N+](C)(C)CCCCCCCC")
PC("959-55-7", "BDMOAC", "Benzyldimethyloctylammonium chloride", "C17H30ClN", "Solid", 13740,
   "A short-chain benzalkonium for disinfectants.", "[Cl-].CCCCCCCC[N+](C)(C)Cc1ccccc1")
PC("5945-33-5", "BDP", "Bisphenol A bis(diphenyl phosphate)", "C39H34O8P2", "Liquid", 9874825,
   "A halogen-free flame retardant for the PC/ABS housings of electronics.",
   "CC(C)(c1ccc(OP(=O)(Oc2ccccc2)Oc2ccccc2)cc1)c1ccc(OP(=O)(Oc2ccccc2)Oc2ccccc2)cc1")
PC("1119-97-7", "TTAB", "Myristyltrimethylammonium bromide", "C17H38BrN", "Solid", 14250,
   "A cationic surfactant for antiseptics and DNA extraction.", "[Br-].CCCCCCCCCCCCCC[N+](C)(C)C")
PC("12141-20-7", "DBLP", "Dibasic lead phosphite", "HO5PPb3", "Solid", 170839083,
   "A heat and light stabiliser for PVC cable and window frames, now phased out for lead's toxicity.")
PC("10099-76-0", "PbSiO3", "Lead silicate", "PbSiO3", "Solid", 131864616,
   "The fritted lead of ceramic glazes, which keeps lead from leaching out of the raw oxide.")
PC("1908-87-8", "MTT", "3-Methylthiazolidine-2-thione", "C4H7NS2", "Solid", 74703,
   "An accelerator for chloroprene rubber that replaced the toxic ethylene thiourea.", "CN1CCSC1=S")
PC("12010-77-4", "BiTiO", "Bismuth titanate", "Bi4Ti3O12", "Solid", 156589087,
   "A piezoelectric ceramic that keeps working at high temperature, for sensors in engines.")
PC("20279-69-0", "CaDMDTC", "Calcium dimethyldithiocarbamate", "C6H12CaN2S4", "Solid", 160505234,
   "A biocide for industrial water and a rubber accelerator.", "[Ca+2].CN(C)C([S-])=S.CN(C)C([S-])=S")
PC("93-70-9", "AAOCA", "Acetoacet-o-chloroanilide", "C10H10ClNO2", "Solid", 7156,
   "A coupling component for yellow azo pigments.", "CC(=O)CC(=O)Nc1ccccc1Cl")

# --- the reactions -------------------------------------------------------------------------------
E4.reactions += [
    R("Cyanogen Chloride", "NaCN + Cl2 -> CNCl + NaCl", COOL,
      "Sodium cyanide oxidised by chlorine, by way of cyanogen.", wiki=P["CNCl"], T=0),
    R("Sodium Picramate", "PicricAcid + 3 H2S + NaOH -> NaPicramate + 3 S + 3 H2O", FLASK,
      "Zinin reduction: sulfide turns one of picric acid's three nitro groups into an amine.", wiki=P["NaPicramate"], T=60),
    R("Lead Silicate Frit", "PbO + Sand -> PbSiO3", HEAT, "Litharge and silica fused into a glass and quenched.", wiki=P["PbSiO3"], T=800),
    R("Dibasic Lead Phosphite", "3 PbO + H3PO3 -> DBLP + H2O", MIX,
      "Litharge slurried with phosphorous acid.", wiki=P["DBLP"]),
    R("Sodium Disilicate", "SodaAsh + 2 Sand -> Na2Si2O5 + CO2", SMELT,
      "Soda and sand melted in the ratio for the disilicate, then crystallised into layers.", wiki=P["Na2Si2O5"], T=1100),
    R("Aluminium Monostearate", "StearicAcid + AlOH3 -> AlMonostearate + H2O", MIX,
      "Stearic acid on aluminium hydroxide, one acid per aluminium.", wiki=P["AlMonostearate"]),
    R("Ammonium Thioglycolate", "TGA + NH3 -> NH4TG", MIX, "Thioglycolic acid neutralised with ammonia.", wiki=P["NH4TG"]),
    R("Triethanolamine Phosphate", "TEA + H3PO4 -> TEAPhosphate", MIX, "Triethanolamine neutralised with phosphoric acid.", wiki=P["TEAPhosphate"]),
]
E5.reactions += [
    R("3,4-Dichloronitrobenzene", "oDCB + HNO3 -> DCNB34 + H2O", FLASK,
      "o-Dichlorobenzene nitrated in mixed acid.", wiki=P["DCNB34"], T=50),
    R("3,4-Dichloroaniline", "DCNB34 + 3 H2 -> DCA34 + 2 H2O", CAT,
      "The nitro group hydrogenated, gently enough to keep the chlorines.", wiki=P["DCA34"], cat="Pt", T=80),
    R("Diuron", "DCA34 + COCl2 + Me2NH -> Diuron + 2 HCl", FLASK,
      "Phosgene turns 3,4-dichloroaniline into its isocyanate, and dimethylamine adds to make the urea.", wiki=P["Diuron"], T=60),
    R("2,4-Xylidine", "mXylene + HNO3 + 3 H2 -> Xylidine24 + 3 H2O", CAT,
      "m-Xylene nitrated, then the nitro compound hydrogenated.", wiki=P["Xylidine24"], cat="Ni", T=100),
    R("Acetoacet-m-xylidide", "Diketene + Xylidine24 -> AAMX", MIX, "2,4-Xylidine acetoacetylated with diketene.", wiki=P["AAMX"]),
    R("Pigment Yellow 13", "DCB + 2 NaNO2 + 2 HCl + 2 AAMX -> PY13 + 2 NaCl + 4 H2O", COOL,
      "Dichlorobenzidine diazotised at both ends and coupled to two acetoacet-m-xylidides.", wiki=P["PY13"], T=5),
    R("Pigment Yellow 17", "DCB + 2 NaNO2 + 2 HCl + 2 AAOA -> PY17 + 2 NaCl + 4 H2O", COOL,
      "Dichlorobenzidine diazotised and coupled to two acetoacet-o-anisidides.", wiki=P["PY17"], T=5),
    R("2-Chloroaniline", "ONCB + 3 H2 -> oChloroaniline + 2 H2O", CAT,
      "o-Nitrochlorobenzene hydrogenated.", wiki=P["oChloroaniline"], cat="Pt", T=80),
    R("Acetoacet-o-chloroanilide", "Diketene + oChloroaniline -> AAOCA", MIX,
      "2-Chloroaniline acetoacetylated with diketene.", wiki=P["AAOCA"]),
    R("Isononanal", "Diisobutylene + CO + H2 -> Isononanal", CAT,
      "Diisobutylene hydroformylated over rhodium, stopping at the aldehyde.", wiki=P["Isononanal"], cat="Rh", T=120),
    R("Isononanoic Acid", "2 Isononanal + O2 -> 2 INAcid", MIX, "The aldehyde oxidised by air.", wiki=P["INAcid"]),
    R("Calcium Isononanoate", "2 INAcid + Ca(OH)2 -> CaINA2 + 2 H2O", MIX, "Isononanoic acid on slaked lime.", wiki=P["CaINA2"]),
    R("Isostearic Acid", "OleicAcid + H2 -> IsostearicAcid", HEAT,
      "Oleic acid heated on acid clay, which branches the chain, then hydrogenated; the branched acid is the liquid part.",
      wiki=P["IsostearicAcid"], T=250),
    R("Glyceryl Monoisostearate", "Glycerol + IsostearicAcid -> GMIS + H2O", CAT,
      "Glycerol esterified once.", wiki=P["GMIS"], cat="H2SO4", T=200),
    R("Potassium Isostearate", "IsostearicAcid + KOH -> KIsostearate + H2O", MIX, "Isostearic acid neutralised with potash.", wiki=P["KIsostearate"]),
    R("Titanate Coupling Agent", "TiOiPr4 + 3 IsostearicAcid -> KRTTS + 3 Isopropanol", FLASK,
      "Three of titanium isopropoxide's four groups swapped for isostearate.", wiki=P["KRTTS"], T=80),
    R("Sodium Phenylphosphinate", "Benzene + PCl3 + H2O + NaOH -> NaPhPinate + 3 HCl", FLASK,
      "Benzene and phosphorus trichloride joined by Friedel-Crafts (dichlorophenylphosphine), hydrolysed and neutralised.",
      wiki=P["NaPhPinate"], T=80),
    R("3,4-Diaminotoluene", "pToluidine + HNO3 + 3 H2 -> DAT34 + 3 H2O", CAT,
      "p-Toluidine protected as its acetamide, nitrated next to the nitrogen, freed and hydrogenated.", wiki=P["DAT34"], cat="Ni", T=80),
    R("Tolyltriazole", "DAT34 + NaNO2 + AcOH -> TTA + NaC2H3O2 + 2 H2O", FLASK,
      "Nitrous acid closes the ortho-diamine into a triazole ring.", wiki=P["TTA"], T=20),
    R("Sodium Tolyltriazole", "TTA + NaOH -> NaTTA + H2O", MIX, "Tolyltriazole dissolved in caustic soda.", wiki=P["NaTTA"]),
    R("2,4'-Bisphenol S", "2 Phenol + H2SO4 -> BPS24 + 2 H2O", FLASK,
      "Phenol sulfonated at a lower temperature, where the ortho-para isomer is kept.", wiki=P["BPS24"], T=150),
    R("Isopropyldiethanolamine", "Isopropylamine + 2 EO -> IPDEA", PRESS, "Isopropylamine opens two ethylene oxides.", wiki=P["IPDEA"], T=120),
    R("Methylcyclopentadiene", "Cyclopentadiene + Methanol -> MeCp + H2O", CAT,
      "Cyclopentadiene methylated with methanol in the vapour.", wiki=P["MeCp"], cat="Alumina", T=400),
    R("Methylcyclopentadiene Dimer", "2 MeCp -> MeCpDimer", HEAT,
      "Left standing, the diene dimerises by Diels-Alder.", wiki=P["MeCpDimer"], T=60),
    R("Aminoethylethanolamine", "EDA + EO -> AEEA", PRESS, "Ethylenediamine opens one ethylene oxide.", wiki=P["AEEA"], T=100),
    R("HEDTA", "AEEA + 3 CH2O + 3 HCN + 3 H2O -> HEDTA + 3 NH3", FLASK,
      "The three N-H bonds cyanomethylated with formaldehyde and hydrogen cyanide, and the nitriles hydrolysed.",
      wiki=P["HEDTA"], T=80),
    R("Di-sec-butyl-p-phenylenediamine", "PPD + 2 MEK + 2 H2 -> DSBPPD + 2 H2O", CAT,
      "p-Phenylenediamine reductively alkylated with butanone.", wiki=P["DSBPPD"], cat="Pt", T=150),
    R("Trifluoropropylmethyldichlorosilane", "TFP + MeSiHCl2 -> TFPMeSiCl2", CAT,
      "Methyldichlorosilane added across trifluoropropene over platinum.", wiki=P["TFPMeSiCl2"], cat="Pt", T=100),
    R("Fluorosilicone Cyclic Trimer", "3 TFPMeSiCl2 + 3 H2O -> D3F + 6 HCl", MIX,
      "The dichlorosilane hydrolysed and the siloxane cracked to the three-membered ring.", wiki=P["D3F"]),
    R("o-Toluenesulfonic Acid", "Toluene + H2SO4 -> oTSA + H2O", COOL,
      "Toluene sulfonated cold, where more of the ortho acid forms.", wiki=P["oTSA"], T=0),
    R("p-tert-Butylphenyl Glycidyl Ether", "TBP4 + Epichlorohydrin + NaOH -> PTBPGE + NaCl + H2O", FLASK,
      "The phenol glycidylated with epichlorohydrin and caustic.", wiki=P["PTBPGE"], T=60),
    R("Neodymium Neodecanoate", "Nd2O3 + 6 NDA -> 2 NdND3 + 3 H2O", FLASK,
      "Neodymium oxide dissolved in neodecanoic acid, the water driven off.", wiki=P["NdND3"], T=120),
    R("UV-3638", "2 Anthranilic + TPC -> UV3638 + 2 HCl + 2 H2O", FLASK,
      "Two anthranilic acids amidated with terephthaloyl chloride and ring-closed to benzoxazinones.", wiki=P["UV3638"], T=150),
    R("Oleamidopropyl Betaine", "OleicAcid + DMAPA + ClAcOH + NaOH -> OAPB + NaCl + 2 H2O", FLASK,
      "Oleic acid amidated with DMAPA, and the amine carboxymethylated with chloroacetate.", wiki=P["OAPB"], T=90),
    R("4-Amino-TMP", "TAA + NH3 + H2 -> AminoTMP + H2O", CAT,
      "Triacetonamine reductively aminated.", wiki=P["AminoTMP"], cat="Ni", T=120),
    R("Nickel 2-Ethylhexanoate", "NiSO4 + 2 EHAcid + 2 NaOH -> NiEH2 + Na2SO4 + 2 H2O", MIX,
      "Nickel sulfate and sodium 2-ethylhexanoate exchange ions; the nickel soap goes into the oil.", wiki=P["NiEH2"]),
    R("Tricetylmethylammonium Chloride", "3 CetylAlcohol + NH3 + CH3Cl -> TCMAC + 3 H2O", CAT,
      "Cetyl alcohol aminated three times over, then quaternised with methyl chloride.", wiki=P["TCMAC"], cat="CopperChromite", T=230),
    R("Sodium Diisobutyl Dithiophosphate", "8 Isobutanol + P4S10 + 4 NaOH -> 4 NaDIBDTPhos + 2 H2S + 4 H2O", FLASK,
      "Isobutanol on phosphorus pentasulfide, and the dithiophosphoric acid neutralised.", wiki=P["NaDIBDTPhos"], T=80),
    R("2-Mercaptobenzimidazole", "OPD + CS2 -> MBI + H2S", FLASK, "o-Phenylenediamine closed into a ring by carbon disulfide.", wiki=P["MBI"], T=80),
    R("Dihydroterpinyl Acetate", "aTerpineol + H2 + AceticAnhydride -> DHTA + AcOH", CAT,
      "Terpineol's ring double bond hydrogenated, and the alcohol acetylated.", wiki=P["DHTA"], cat="Ni", T=100),
    R("TGMXDA", "MXDA + 4 Epichlorohydrin + 4 NaOH -> TGMXDA + 4 NaCl + 4 H2O", FLASK,
      "Each N-H of m-xylylenediamine glycidylated.", wiki=P["TGMXDA"], T=60),
    R("DEG Butyl Ether Methacrylate", "DEGBE + MethacrylicAcid -> DEGBEMA + H2O", CAT,
      "Butyl carbitol esterified with methacrylic acid.", wiki=P["DEGBEMA"], cat="H2SO4", T=100),
    R("Diethylene Glycol Divinyl Ether", "DEG + 2 Acetylene -> DEGDVE", PRESS,
      "Reppe vinylation: acetylene under pressure adds to both hydroxyls with potash.", wiki=P["DEGDVE"], T=170),
    R("o-Terphenyl", "3 Benzene -> oTerphenyl + 2 H2", CRACKER,
      "Benzene pyrolysed for biphenyl; the terphenyls are what comes over next.", wiki=P["oTerphenyl"], T=750),
    R("DTHFP", "2 Furan + Acetone + 4 H2 -> DTHFP + H2O", CAT,
      "Two furans condensed onto acetone, then both rings hydrogenated.", wiki=P["DTHFP"], cat="Ni", T=120),
    R("3-Diethylaminophenol", "Resorcinol + Diethylamine -> DEAP + H2O", HEAT,
      "Resorcinol heated with diethylamine under pressure: one hydroxyl swapped for the amine.", wiki=P["DEAP"], T=200),
    R("Coumarin 1", "DEAP + EthylAcetoacetate -> Coumarin1 + Ethanol + H2O", FLASK,
      "A Pechmann condensation: the phenol and the ketoester close the coumarin ring.", wiki=P["Coumarin1"], T=120),
    R("Benzyl Acrylate Quat", "DMAEA + BenzylChloride -> ADBAC", MIX, "The amine acrylate quaternised with benzyl chloride.", wiki=P["ADBAC"]),
    R("Dimethylbenzylcarbinol", "BenzylChloride + Mg + Acetone + HCl -> DMBC + MgCl2", FLASK,
      "Benzylmagnesium chloride (a Grignard reagent) adds to acetone.", wiki=P["DMBC"], T=30),
    R("Dimethylbenzylcarbinyl Acetate", "DMBC + AceticAnhydride -> DMBCA + AcOH", FLASK, "The tertiary alcohol acetylated.", wiki=P["DMBCA"], T=100),
    R("Zinc Neodecanoate", "2 NDA + ZnO -> ZnND2 + H2O", MIX, "Neodecanoic acid on zinc oxide.", wiki=P["ZnND2"]),
    R("Lithium Neodecanoate", "NDA + LiOH -> LiND + H2O", MIX, "Neodecanoic acid on lithium hydroxide.", wiki=P["LiND"]),
    R("Copper Neodecanoate", "4 NDA + Malachite -> 2 CuND2 + CO2 + 3 H2O", MIX,
      "Basic copper carbonate dissolved in neodecanoic acid.", wiki=P["CuND2"]),
    R("1-Ethoxy-2-propyl Acetate", "PGEE + AcOH -> PGEEA + H2O", CAT, "1-Ethoxy-2-propanol esterified.", wiki=P["PGEEA"], cat="H2SO4", T=110),
    R("Potassium Etidronate", "HEDP + KOH -> KHEDP + H2O", MIX, "Etidronic acid partly neutralised with potash.", wiki=P["KHEDP"]),
    R("Diphenylguanidine", "DPTU + NH3 + PbO -> DPhG + Galena + H2O", FLASK,
      "Thiocarbanilide desulfurised with litharge in ammonia; the sulfur leaves as lead sulfide.", wiki=P["DPhG"], T=60),
    R("Diphenylguanidine Hydrochloride", "DPhG + HCl -> DPGHCl", MIX, "Diphenylguanidine taken up in hydrochloric acid.", wiki=P["DPGHCl"]),
    R("Bromoethane", "Ethanol + HBr -> EtBr + H2O", FLASK, "Ethanol on hydrogen bromide.", wiki=P["EtBr"], T=60),
    R("Ethyltriphenylphosphonium Bromide", "PPh3 + EtBr -> ETPPBr", FLASK,
      "Triphenylphosphine alkylated with ethyl bromide.", wiki=P["ETPPBr"], T=80),
    R("Di-o-tolylguanidine", "2 oToluidine + CNCl -> DOTG + HCl", FLASK,
      "Two o-toluidines added to cyanogen chloride.", wiki=P["DOTG"], T=80),
    R("Diethyldimethylammonium Chloride", "Diethylamine + 2 CH3Cl + NaOH -> DEDMAC + NaCl + H2O", MIX,
      "Diethylamine methylated twice.", wiki=P["DEDMAC"]),
    R("TEA Lauryl Sulfate", "Dodecanol + SO3 + TEA -> TEALS", FLASK,
      "Lauryl alcohol sulfated and neutralised with triethanolamine.", wiki=P["TEALS"], T=40),
    R("Octyldecyldimethylammonium Chloride", "Octanol + Decanol + Methylamine + CH3Cl -> ODDMAC + 2 H2O", CAT,
      "Methylamine aminated with an octyl and a decyl group, then quaternised.", wiki=P["ODDMAC"], cat="CopperChromite", T=220),
    R("Benzyldimethyloctylammonium Chloride", "DMOA + BenzylChloride -> BDMOAC", MIX,
      "Dimethyloctylamine quaternised with benzyl chloride.", wiki=P["BDMOAC"]),
    R("BDP Flame Retardant", "BPA + 2 POCl3 + 4 Phenol -> BDP + 6 HCl", FLASK,
      "Bisphenol A and phenol phosphorylated together on phosphorus oxychloride.", wiki=P["BDP"], T=150),
    R("Myristyltrimethylammonium Bromide", "DMA14 + MeBr -> TTAB", MIX,
      "Dimethyltetradecylamine quaternised with methyl bromide.", wiki=P["TTAB"]),
    R("N-Methylethanolamine", "Methylamine + EO -> MMEA", MIX, "Ethylene oxide fed into a large excess of methylamine, so most amines take only one.", wiki=P["MMEA"], T=100),
    R("3-Methylthiazolidine-2-thione", "MMEA + CS2 -> MTT + H2O", FLASK,
      "N-Methylethanolamine closed into a thiazolidine ring by carbon disulfide.", wiki=P["MTT"], T=100),
    R("Bismuth Titanate", "2 Bi2O3 + 3 TiO2 -> BiTiO", SMELT,
      "Bismuth and titanium oxides calcined into a layered perovskite.", wiki=P["BiTiO"], T=1000),
    R("Calcium Dimethyldithiocarbamate", "2 Me2NH + 2 CS2 + Ca(OH)2 -> CaDMDTC + 2 H2O", MIX,
      "Dimethylamine and carbon disulfide in lime water.", wiki=P["CaDMDTC"]),
]

# Milestones for the stretches this part lengthened (messages only).
import authored_content as _C  # noqa: E402
from gen_authored import Milestone  # noqa: E402
_C.MILESTONES += [
    Milestone("IsostearicAcid", message="A branch in the chain keeps a fatty acid liquid: isostearic acid is as stable as stearic acid without setting into wax."),
    Milestone("Diuron", message="Diuron (DCMU) blocks photosystem II at one exact point, so plant scientists use it to switch photosynthesis off where they choose."),
]
import authored_canon_25  # noqa: E402,F401
