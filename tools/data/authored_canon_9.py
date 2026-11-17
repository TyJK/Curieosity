"""
Curieosity's industrial chemistry, part 9 (see authored_canon.py).
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E1, E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)


# --- the canon substances ------------------------------------------------------------------
S("71-91-0", "TEAB", "Tetraethylammonium bromide", "C8H20BrN", "Solid", 14104510,
  "A quaternary ammonium salt: a phase-transfer catalyst and the classic blocker of potassium channels in nerve research.", lib=7696)
S("56-34-8", "TEAC", "Tetraethylammonium chloride", "C8H20ClN", "Solid", 37108522,
  "A quaternary ammonium salt for electrolytes and phase-transfer catalysis.", lib=6521)
S("13701-59-2", "BaBO2", "Barium metaborate", "BaB2O4", "Solid", 20935882,
  "A pigment that inhibits corrosion and mould in paints; its beta crystal form doubles the frequency of laser light.", lib=3518)
S("95-74-9", "CMA", "3-Chloro-4-methylaniline", "C7H8ClN", "Solid", 21308201,
  "An aniline for the herbicide chlorotoluron, and a bird poison (Starlicide) that targets starlings.", lib=8826)
S("79-30-1", "IsobutyrylCl", "Isobutyryl chloride", "C4H7ClO", "Liquid", 54437591,
  "An acylating agent for drugs and pesticides.", lib=8233)
S("26266-57-9", "Span40", "Sorbitan monopalmitate", "C22H42O6", "Solid", 59233502,
  "Span 40, a palm-based sorbitan emulsifier for foods and cosmetics.", lib=4856)
S("12047-27-7", "BaTiO3", "Barium titanate", "BaTiO3", "Solid", 3219865,
  "A ferroelectric ceramic: the dielectric inside nearly every ceramic capacitor, billions of them in each year's phones.", lib=2951)
S("7783-20-2", "NH4HSO4", "Ammonium bisulfate", "NH4HSO4", "Solid", 13535173,
  "The acid salt that forms when ammonia meets sulfuric acid in excess; a by-product of making methyl methacrylate.", lib=8206)
S("652-67-5", "Isosorbide", "Isosorbide", "C6H10O4", "Solid", 2252299,
  "Sorbitol twice dehydrated into a bent pair of rings: a bio-based monomer for clear polycarbonate, and, nitrated, a heart drug.", lib=6283)
S("501-53-1", "CbzCl", "Benzyl chloroformate", "C8H7ClO2", "Liquid", 1884720,
  "Bergmann and Zervas's reagent (1932) for protecting amines, the first step in making peptides by design.", lib=6068)
S("79-22-1", "MCF", "Methyl chloroformate", "C2H3ClO2", "Liquid", 25852146,
  "An acylating agent for carbamate pesticides and drugs.", lib=8230)
S("1333-39-7", "PSA", "Phenolsulfonic acid", "C6H6O4S", "Liquid", 14729288,
  "The acid electrolyte of tin plating on steel.", lib=3393)
S("119-27-7", "DNAN", "2,4-Dinitroanisole", "C7H6N2O5", "Solid", 40773811,
  "DNAN, the insensitive melt-cast explosive replacing TNT: it doesn't go off when a shell is dropped or set on fire.", lib=2862)
S("109-77-3", "Malononitrile", "Malononitrile", "C3H2N2", "Solid", 3076562,
  "A doubly activated building block for drugs and dyes, and for the CS tear gas.", lib=2566)
S("7789-29-9", "KHF2", "Potassium bifluoride", "KHF2", "Solid", 19703218,
  "Melted with hydrogen fluoride it is the electrolyte from which all fluorine gas is made; it also etches glass.", lib=8152)
S("103-76-4", "HEP", "Hydroxyethylpiperazine", "C6H14N2O", "Liquid", 18611497,
  "The start of HEPES, the buffer that keeps cell cultures at pH 7.4.", lib=2237)
S("103-83-3", "BDMA", "N,N-Dimethylbenzylamine", "C9H13N", "Liquid", 10619313,
  "An accelerator for epoxy cures and a catalyst for polyurethane foam.", lib=2239)
S("112-36-7", "EtDiglyme", "Diethylene glycol diethyl ether", "C8H18O3", "Liquid", 33844129,
  "A high-boiling ether solvent for reactions and coatings.", lib=2710)
S("127-63-9", "DPSulfone", "Diphenyl sulfone", "C12H10O2S", "Solid", 35850573,
  "A high-boiling solvent in which PEEK, the strongest thermoplastic, is made.", lib=3197)
S("1313-97-9", "Nd2O3", "Neodymium oxide", "Nd2O3", "Solid", 22031024,
  "It colours glass a lilac that shifts with the light, filters welders' goggles, and is reduced to the metal for magnets.", lib=3316)
S("137-26-8", "Thiram", "Thiram", "C6H12N2S4", "Solid", 23294837,
  "A rubber accelerator and a fungicide for seeds and fruit.", lib=3513)
S("141-52-6", "NaOEt", "Sodium ethoxide", "C2H5NaO", "Solid", 2702964,
  "A strong base for condensation reactions, such as the Claisen and the Darzens.", lib=3626)
S("142-77-8", "ButylOleate", "Butyl oleate", "C22H42O2", "Liquid", 75279541,
  "A plasticiser for PVC and a lubricant.", lib=3658)
S("14228-73-0", "CHDMDGE", "1,4-Cyclohexanedimethanol diglycidyl ether", "C14H24O4", "Liquid", 70518437,
  "A low-viscosity epoxy diluent that keeps cured resin tough.", lib=3671)
S("2210-79-9", "CGE", "o-Cresyl glycidyl ether", "C10H12O2", "Liquid", 70391707,
  "A reactive diluent for epoxy floors and coatings.", lib=4499)
S("2426-08-6", "BGE", "Butyl glycidyl ether", "C7H14O2", "Liquid", 50884130,
  "A reactive diluent that thins epoxy resins.", lib=4636)
S("2461-15-6", "EHGE", "2-Ethylhexyl glycidyl ether", "C11H22O2", "Liquid", 70375767,
  "A reactive diluent and flexibiliser for epoxy resins.", lib=4668)
S("37640-57-6", "MelamineCyanurate", "Melamine cyanurate", "C6H9N9O3", "Solid", 16643661,
  "A hydrogen-bonded flame retardant for nylon. The same pair formed the kidney stones of the 2007 pet food recalls.", smiles="O=C1NC(=O)NC(=O)N1.N=1C(=NC(=NC1N)N)N")
S("555-43-1", "Tristearin", "Tristearin", "C57H110O6", "Solid", 268460,
  "Glycerol carrying three stearic acids: the hard fat of shortening, candles and soap.", smiles="O=C(OCC(OC(=O)CCCCCCCCCCCCCCCCC)COC(=O)CCCCCCCCCCCCCCCCC)CCCCCCCCCCCCCCCCC")
S("5593-70-4", "TiOBu4", "Titanium butoxide", "C16H36O4Ti", "Liquid", 48329891,
  "A catalyst for polyester and a binder for heat-resistant paints.", lib=6513)
S("585-07-9", "tBMA", "tert-Butyl methacrylate", "C8H14O2", "Liquid", 77978272,
  "A methacrylate whose bulky group gives hard, water-shy polymers for coatings and photoresists.", lib=6698)
S("6413-10-1", "Fructone", "Fructone", "C8H14O4", "Liquid", 16147952,
  "A fruity, apple-like fragrance in shampoos and air fresheners.", lib=7107)
S("105-56-6", "EthylCyanoacetate", "Ethyl cyanoacetate", "C5H7NO2", "Liquid", 50816525,
  "A building block for superglue, caffeine and many drugs.", lib=2333)
S("7085-85-0", "ECA", "Ethyl cyanoacrylate", "C6H7NO2", "Liquid", 3185844,
  "Superglue (Harry Coover, Eastman Kodak, 1951): a trace of water polymerises it in seconds.", lib=7680)
S("77-83-8", "EMPG", "Ethyl methylphenylglycidate", "C12H14O3", "Liquid", 5447890,
  "'Strawberry aldehyde', the strawberry flavour of sweets and lip balm; it isn't an aldehyde at all.", lib=8067)
S("7778-74-7", "KClO4", "Potassium perchlorate", "KClO4", "Solid", 1024033,
  "The oxidiser of fireworks, flares and airbag starters.", lib=8124)
S("97-77-8", "Disulfiram", "Disulfiram", "C10H20N2S4", "Solid", 243387,
  "A rubber accelerator that, workers noticed, made alcohol unbearable: as Antabuse (1948) it treats alcoholism.", lib=8894)
S("1643-19-2", "TBAB", "Tetrabutylammonium bromide", "C16H36BrN", "Solid", 13226458,
  "The phase-transfer catalyst that ferries anions from water into organic solvent.", lib=4030)
S("502-97-6", "Glycolide", "Glycolide", "C4H4O4", "Solid", 30405724,
  "Two glycolic acids in a ring, polymerised into PGA, the first synthetic dissolving suture (Dexon, 1970).", lib=6074)
S("7775-19-1", "NaBO2", "Sodium metaborate", "NaBO2", "Solid", 19218592,
  "A borate for adhesives, textile finishing and herbicides; hydrogenated, it becomes sodium borohydride.", lib=8119)
S("29797-40-8", "BenzalChloride", "Benzal chloride", "C7H6Cl2", "Liquid", 6649481,
  "Toluene chlorinated twice on its methyl group, hydrolysed to benzaldehyde.", lib=5129)
S("100-10-7", "DMAB", "4-Dimethylaminobenzaldehyde", "C9H11NO", "Solid", 15803524,
  "Ehrlich's reagent, which turns pink with indoles and urobilinogen.", lib=2001)
S("100-43-6", "VinylPyridine4", "4-Vinylpyridine", "C7H7N", "Liquid", 58639717,
  "A monomer for ion-exchange resins and polymers that bind metals.", lib=2011)
S("100-54-9", "CyanoPyridine3", "3-Cyanopyridine", "C6H4N2", "Solid", 57554526,
  "Nicotinonitrile, hydrolysed by an enzyme to niacinamide (Lonza).", lib=2017)
S("1000-82-4", "Methylolurea", "Methylolurea", "C2H6N2O2", "Solid", 66254033,
  "Urea's first formaldehyde: the building block of urea-formaldehyde resin.", lib=2028)
S("1009-93-4", "HMCTS", "Hexamethylcyclotrisilazane", "C6H21N3Si3", "Liquid", 62738783,
  "A silicon-nitrogen ring for silylating surfaces and making silicon nitride ceramics.", lib=2087)
S("101-90-6", "RDGE", "Resorcinol diglycidyl ether", "C12H14O4", "Liquid", 70877331,
  "A reactive epoxy diluent.", lib=2121)
S("102-70-5", "TriallylAmine", "Triallylamine", "C9H15N", "Liquid", 70269597,
  "A crosslinker for ion-exchange resins and superabsorbents.", lib=2172)
S("103-45-7", "PhenethylAcetate", "2-Phenylethyl acetate", "C10H12O2", "Liquid", 49398262,
  "A rose and honey scent in perfumes, and a flavour of beer and wine.", lib=2228)
S("103-65-1", "Propylbenzene", "Propylbenzene", "C9H12", "Liquid", 54282159,
  "n-Propylbenzene, a solvent and textile dye carrier.", lib=2233)

E4.reactions += [
    R("Barium Metaborate", "BaCO3 + 2 H3BO3 -> BaBO2 + CO2 + 3 H2O", HEAT,
      "Witherite and boric acid fired together.", wiki=20935882, T=800),
    R("Ammonium Bisulfate", "NH42SO4 + H2SO4 -> 2 NH4HSO4", MIX,
      "Ammonium sulfate dissolved in sulfuric acid.", wiki=13535173),
    R("Potassium Bifluoride", "KOH + 2 HF -> KHF2 + H2O", MIX,
      "Caustic potash in excess hydrofluoric acid (Fremy).", wiki=19703218),
    R("Methyl Chloroformate", "Methanol + COCl2 -> MCF + HCl", FLASK,
      "Methanol and phosgene, cold.", wiki=25852146, T=0),
    R("Phenolsulfonic Acid", "Phenol + H2SO4 -> PSA + H2O", MIX,
      "Phenol sulfonated by sulfuric acid.", wiki=14729288),
    R("Sodium Ethoxide", "2 Na + 2 Ethanol -> 2 NaOEt + H2", FLASK,
      "Sodium dissolved in dry ethanol.", wiki=2702964, T=60),
    R("Potassium Perchlorate", "NaClO4 + KCl -> KClO4 + NaCl", MIX,
      "Sodium perchlorate swapped with potassium chloride; the potassium salt, barely soluble, crystallises.", wiki=1024033),
    R("Sodium Metaborate", "Borax + 2 NaOH -> 4 NaBO2 + 11 H2O", MIX,
      "Borax and caustic soda.", wiki=19218592),
    R("Benzal Chloride", "BenzylChloride + Cl2 -> BenzalChloride + HCl", LIGHT,
      "Benzyl chloride chlorinated again in light.", wiki=6649481, T=100),
    R("Diphenyl Sulfone", "2 Benzene + SO3 -> DPSulfone + H2O", FLASK,
      "Benzene sulfonated, and the acid condensed with more benzene.", wiki=35850573, T=150),
    R("Neodymium Oxide", "4 NdNO33 -> 2 Nd2O3 + 12 NO2 + 3 O2", HEAT,
      "Neodymium nitrate calcined.", wiki=22031024, T=800),
    R("Methylolurea", "Urea + CH2O -> Methylolurea", MIX,
      "Urea and formaldehyde in mild alkali.", wiki=66254033),
]
E5.reactions += [
    R("Tetraethylammonium Bromide", "Et3N + Ethanol + HBr -> TEAB + H2O", FLASK,
      "Triethylamine quaternised with ethyl bromide.", wiki=14104510, T=80),
    R("Tetraethylammonium Chloride", "Et3N + Ethanol + HCl -> TEAC + H2O", FLASK,
      "Triethylamine quaternised with ethyl chloride.", wiki=37108522, T=80),
    R("Chlorotoluidine", "Nitrotoluene + Cl2 + 3 H2 -> CMA + HCl + 2 H2O", FLASK,
      "p-Nitrotoluene chlorinated beside the methyl group, then hydrogenated.", wiki=21308201, T=60),
    R("Isobutyryl Chloride", "3 IsobutyricAcid + PCl3 -> 3 IsobutyrylCl + H3PO3", FLASK,
      "Isobutyric acid chlorinated with phosphorus trichloride.", wiki=54437591, T=60),
    R("Span 40", "Sorbitol + PalmiticAcid -> Span40 + 2 H2O", CAT,
      "Sorbitol closes into sorbitan and is esterified with palmitic acid.", wiki=59233502, cat="NaOH", T=210),
    R("Barium Titanate", "BaCO3 + TiO2 -> BaTiO3 + CO2", HEAT,
      "Witherite and rutile calcined together (found in 1941 in the US, Japan and Russia).", wiki=3219865, T=1100),
    R("Isosorbide", "Sorbitol -> Isosorbide + 2 H2O", CAT,
      "Sorbitol dehydrated twice in acid.", wiki=2252299, cat="H2SO4", T=150),
    R("Benzyl Chloroformate", "BenzylAlcohol + COCl2 -> CbzCl + HCl", FLASK,
      "Benzyl alcohol and phosgene, cold.", wiki=1884720, T=0),
    R("DNAN", "NCB + HNO3 + NaOMe -> DNAN + NaCl + H2O", FLASK,
      "4-Nitrochlorobenzene nitrated again, then its chlorine swapped for methoxide.", wiki=40773811, T=60),
    R("Malononitrile", "Acetonitrile + HCN + Cl2 -> Malononitrile + 2 HCl", HEAT,
      "Acetonitrile and cyanogen chloride at 750 C.", wiki=3076562, T=750),
    R("Hydroxyethylpiperazine", "Piperazine + EO -> HEP", PRESS,
      "Piperazine opens one ethylene oxide.", wiki=18611497, T=100),
    R("Dimethylbenzylamine", "BenzylChloride + Me2NH -> BDMA + HCl", FLASK,
      "Benzyl chloride aminated with dimethylamine.", wiki=10619313, T=40),
    R("Ethyl Diglyme", "2 Ethanol + 2 EO -> EtDiglyme + H2O", CAT,
      "Ethylene oxide opened by ethanol twice over, the end etherified.", wiki=33844129, cat="BF3", T=100),
    R("Thiram", "2 Me2NH + 2 CS2 + H2O2 -> Thiram + 2 H2O", FLASK,
      "Dimethyldithiocarbamate oxidised by hydrogen peroxide into the disulfide.", wiki=23294837, T=30),
    R("Butyl Oleate", "OleicAcid + Butanol -> ButylOleate + H2O", CAT,
      "Oleic acid esterified with butanol.", wiki=75279541, cat="H2SO4", T=120),
    R("CHDM Diglycidyl Ether", "CHDM + 2 Epichlorohydrin + 2 NaOH -> CHDMDGE + 2 NaCl + 2 H2O", FLASK,
      "Cyclohexanedimethanol joined to two epichlorohydrins.", wiki=70518437, T=60),
    R("Cresyl Glycidyl Ether", "oCresol + Epichlorohydrin + NaOH -> CGE + NaCl + H2O", FLASK,
      "o-Cresol joined to epichlorohydrin.", wiki=70391707, T=60),
    R("Butyl Glycidyl Ether", "Butanol + Epichlorohydrin + NaOH -> BGE + NaCl + H2O", FLASK,
      "Butanol joined to epichlorohydrin.", wiki=50884130, T=60),
    R("Ethylhexyl Glycidyl Ether", "2EH + Epichlorohydrin + NaOH -> EHGE + NaCl + H2O", FLASK,
      "2-Ethylhexanol joined to epichlorohydrin.", wiki=70375767, T=60),
    R("Melamine Cyanurate", "Melamine + CyanuricAcid -> MelamineCyanurate", MIX,
      "Melamine and cyanuric acid lock together through hydrogen bonds.", wiki=16643661),
    R("Hardening Fat", "Triolein + 3 H2 -> Tristearin", HIGHP,
      "Every double bond of olive oil hydrogenated over nickel (Normann's fat hardening, 1902, taken all the way).",
      wiki=268460, cat="Ni", T=200),
    R("Titanium Butoxide", "TiCl4 + 4 Butanol + 4 NH3 -> TiOBu4 + 4 NH4Cl", FLASK,
      "Titanium tetrachloride and butanol, with ammonia to take the hydrogen chloride.", wiki=48329891, T=20),
    R("tert-Butyl Methacrylate", "MethacrylicAcid + Isobutylene -> tBMA", CAT,
      "Methacrylic acid adds to isobutylene over an acid catalyst.", wiki=77978272, cat="H2SO4", T=20),
    R("Fructone", "EthylAcetoacetate + EG -> Fructone + H2O", CAT,
      "Ethyl acetoacetate's ketone protected as a dioxolane with ethylene glycol.", wiki=16147952, cat="pTsOH", T=110),
    R("Ethyl Cyanoacetate", "ClAcOH + NaCN + Ethanol -> EthylCyanoacetate + NaCl + H2O", FLASK,
      "Chloroacetate swapped for cyanide (Kolbe nitrile synthesis), then esterified.", wiki=50816525, T=80),
    R("Superglue", "EthylCyanoacetate + CH2O -> ECA + H2O", FLASK,
      "Ethyl cyanoacetate condensed with formaldehyde into a polymer, which is cracked back to the monomer.",
      wiki=3185844, T=180),
    R("Strawberry Aldehyde", "Acetophenone + EtClAc + NaOEt -> EMPG + NaCl + Ethanol", FLASK,
      "The Darzens condensation of acetophenone with ethyl chloroacetate.", wiki=5447890, T=20),
    R("Disulfiram", "2 Diethylamine + 2 CS2 + H2O2 -> Disulfiram + 2 H2O", FLASK,
      "Diethyldithiocarbamate oxidised into the disulfide.", wiki=243387, T=30),
    R("Tetrabutylammonium Bromide", "Tributylamine + Butanol + HBr -> TBAB + H2O", FLASK,
      "Tributylamine quaternised with butyl bromide.", wiki=13226458, T=100),
    R("Glycolide", "2 GlycolicAcid -> Glycolide + 2 H2O", HEAT,
      "Glycolic acid condensed into an oligomer and cracked into the ring under vacuum.", wiki=30405724, T=250),
    R("Ehrlich's Reagent", "Dimethylaniline + DMF -> DMAB + Me2NH", CAT,
      "The Vilsmeier reaction: DMF and phosphorus oxychloride formylate dimethylaniline.", wiki=15803524, cat="POCl3", T=90),
    R("4-Vinylpyridine", "Picoline4 + CH2O -> VinylPyridine4 + H2O", CAT,
      "4-Picoline condensed with formaldehyde and dehydrated.", wiki=58639717, cat="NaOH", T=250),
    R("3-Cyanopyridine", "2 Picoline3 + 2 NH3 + 3 O2 -> 2 CyanoPyridine3 + 6 H2O", CAT,
      "3-Picoline ammoxidised over vanadium oxide.", wiki=57554526, cat="V2O5", T=380),
    R("Hexamethylcyclotrisilazane", "3 Me2SiCl2 + 9 NH3 -> HMCTS + 6 NH4Cl", FLASK,
      "Dimethyldichlorosilane and ammonia close a silicon-nitrogen ring.", wiki=62738783, T=20),
    R("Resorcinol Diglycidyl Ether", "Resorcinol + 2 Epichlorohydrin + 2 NaOH -> RDGE + 2 NaCl + 2 H2O", FLASK,
      "Resorcinol joined to two epichlorohydrins.", wiki=70877331, T=60),
    R("Triallylamine", "3 AllylChloride + 4 NH3 -> TriallylAmine + 3 NH4Cl", FLASK,
      "Allyl chloride and ammonia.", wiki=70269597, T=60),
    R("Phenethyl Acetate", "Phenylethanol + AcOH -> PhenethylAcetate + H2O", CAT,
      "2-Phenylethanol esterified with acetic acid.", wiki=49398262, cat="H2SO4", T=110),
    R("Propylbenzene", "Toluene + Ethylene -> Propylbenzene", FLASK,
      "Ethylene adds to toluene's methyl group with a sodium-potassium alloy.", wiki=54282159, T=150),
]

import authored_canon_10  # noqa: E402,F401
