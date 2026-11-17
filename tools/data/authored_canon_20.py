"""
Curieosity's industrial chemistry, part 20 (see authored_canon.py): the canon records whose
scraped formula or structure was garbled, re-identified from their CAS number and name (part 19
did the same for the ones set aside as doubtful). Also two big gaps the canon list itself had:
triethylene glycol and copper phthalocyanine.
"""

from authored_canon import S, R, CANON  # noqa: F401
from authored_content import E3, E4, E5, E6, X  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR, pubchem)

P = {}  # key -> reference, for the reactions that make them


def SR(cas, key, name, formula, state, ref, desc, smiles=None):
    P[key] = pubchem(ref) if isinstance(ref, int) else ref
    S(cas, key, name, formula, state, P[key], desc, smiles=smiles)


CANON.update({"12767-90-7": "ZincBorate"})  # the anhydrous borate; the game has the hydrate

# --- two gaps in the canon list -------------------------------------------------------------
SR("112-27-6", "TEG", "Triethylene glycol", "C6H14O4", "Liquid", "Triethylene_glycol",
   "Three ethylene glycol units in a chain: it wrings the water out of natural gas, and plasticises and fogs (smoke-machine fluid).",
   "OCCOCCOCCO")
SR("147-14-8", "CuPc", "Copper phthalocyanine", "C32H16CuN8", "Solid", "Copper_phthalocyanine",
   "Phthalocyanine blue: a copper atom in a flat ring of four isoindoles. The blue of most blue ink and paint, stable to light, heat and acid.")

# --- re-identified records ------------------------------------------------------------------
SR("1328-53-6", "PG7", "Phthalocyanine green", "C32Cl16CuN8", "Solid", "Phthalocyanine_Green_G",
   "Copper phthalocyanine chlorinated all round: the green of most green paint, ink and plastic.")
SR("112-76-5", "StearoylCl", "Stearoyl chloride", "C18H35ClO", "Liquid", 8212,
   "Stearic acid's acid chloride: it puts the eighteen-carbon chain onto paper-sizing ketene dimers and surfactants.",
   "CCCCCCCCCCCCCCCCCC(Cl)=O")
SR("26523-78-4", "TNPP", "Tris(nonylphenyl) phosphite", "C45H69O3P", "Liquid", 76452,
   "TNPP, a phosphite antioxidant that protects rubber and PVC while they are processed hot.",
   "CCCCCCCCCc1ccc(OP(Oc2ccc(CCCCCCCCC)cc2)Oc2ccc(CCCCCCCCC)cc2)cc1")
SR("94-28-0", "TEGEH", "Triethylene glycol bis(2-ethylhexanoate)", "C22H42O6", "Liquid", 7185,
   "3GO: the plasticiser in the PVB interlayer that holds laminated safety glass together.",
   "CCCCC(CC)C(=O)OCCOCCOCCOC(=O)C(CC)CCCC")
SR("102-83-0", "DBAPA", "3-(Dibutylamino)propylamine", "C11H26N2", "Liquid", 1626,
   "A diamine for epoxy hardeners and the cationic surfactants of fabric softeners.", "CCCCN(CCCC)CCCN")
SR("1195-92-2", "LimoneneOxide", "Limonene oxide", "C10H16O", "Liquid", 91496,
   "Limonene's epoxide: a citrus-woody flavour note, and a bio-based monomer that polymerises with carbon dioxide.",
   "CC(=C)C1CCC2(C)OC2C1")
SR("12018-10-9", "CopperChromite", "Copper chromite", "CuCr2O4", "Solid", "Copper_chromite",
   "Adkins' catalyst: it hydrogenates esters to alcohols, the route from fats to fatty alcohols for detergents.")
SR("12056-51-8", "K2Ti6O13", "Potassium hexatitanate", "K2Ti6O13", "Solid", 170839124,
   "Fine whiskers that reinforce brake pads and clutch facings in place of asbestos.")
SR("15123-80-5", "AlMolybdate", "Aluminium molybdate", "Al2Mo3O12", "Solid", 170848274,
   "A molybdate catalyst for oxidising alcohols to aldehydes.")
SR("26544-38-7", "DDSA", "Tetrapropenylsuccinic anhydride", "C16H26O3", "Liquid", 6438029,
   "An alkenyl succinic anhydride from the propylene tetramer: an epoxy hardener, a corrosion inhibitor, and the parent of lubricating-oil dispersants.",
   "CCCCCCCCCC=CCC1CC(=O)OC1=O")
SR("597-82-0", "TPPT", "Triphenyl phosphorothionate", "C18H15O3PS", "Solid", 69011,
   "An antiwear additive for turbine and hydraulic oils.", "S=P(Oc1ccccc1)(Oc1ccccc1)Oc1ccccc1")
SR("924-88-9", "DiPS", "Diisopropyl succinate", "C10H18O4", "Liquid", 70213,
   "The succinate that, condensed with benzonitriles, builds the diketopyrrolopyrrole reds, among them 'Ferrari red' Pigment Red 254.",
   "CC(C)OC(=O)CCC(=O)OC(C)C")
SR("109-16-0", "TEGDMA", "Triethylene glycol dimethacrylate", "C14H22O6", "Liquid", 7979,
   "The thin crosslinking monomer that dilutes the resin of tooth-coloured dental fillings.",
   "CC(=C)C(=O)OCCOCCOCCOC(=O)C(C)=C")
SR("63500-71-0", "Florol", "Florol", "C10H20O2", "Liquid", 3017432,
   "A lily-of-the-valley fragrance alcohol on a tetrahydropyran ring.", "CC(C)CC1CC(C)(O)CCO1")
SR("136-30-1", "NaDBDTC", "Sodium dibutyldithiocarbamate", "C9H18NNaS2", "Solid", 6331222,
   "A fast vulcanisation accelerator for latex goods.", "[Na+].CCCCN(CCCC)C([S-])=S")
SR("13007-85-7", "NaGlucoheptonate", "Sodium glucoheptonate", "C7H13NaO8", "Solid", 88654666,
   "A sugar-acid chelant that holds iron and calcium in bottle-washing and concrete-retarding mixes.",
   "[Na+].OCC(O)C(O)C(O)C(O)C(O)C([O-])=O")
SR("4482-25-1", "BismarckBrownR", "Bismarck brown R", "C21H24N8", "Solid", 24674,
   "The toluene-based Bismarck brown: a dye for leather and a biological stain.",
   "Cc1ccc(N=Nc2cc(C)c(N)cc2N)cc1N=Nc1cc(C)c(N)cc1N")
SR("64265-57-2", "TMPMAP", "Trimethylolpropane tris(2-methyl-1-aziridinepropionate)", "C24H41N3O6", "Liquid", 94611,
   "A polyaziridine that crosslinks water-based coatings and inks once they dry.",
   "CCC(COC(=O)CCN1CC1C)(COC(=O)CCN1CC1C)COC(=O)CCN1CC1C")
SR("2440-22-4", "Drometrizole", "Drometrizole", "C13H11N3O", "Solid", 17113,
   "The first benzotriazole UV absorber (Tinuvin P): it keeps plastics from yellowing in sunlight.",
   "Cc1ccc(O)c(c1)-n1nc2ccccc2n1")
SR("12018-19-8", "ZnCr2O4", "Zinc chromite", "ZnCr2O4", "Solid", 72668652,
   "The zinc-chromium oxide catalyst of BASF's first methanol plant (1923), which ran at 300 atmospheres.")
SR("13595-85-2", "BiMolybdate", "Bismuth molybdate", "Bi2Mo3O12", "Solid", 170839602,
   "The catalyst of Sohio's acrylonitrile process (1957): propylene, ammonia and air go in, acrylonitrile comes out.")
SR("12065-90-6", "TBLS", "Tetrabasic lead sulfate", "Pb5O4SO4", "Solid", 20215606,
   "4PbO.PbSO4: the needle crystals that cure into the positive plates of lead-acid batteries.")
SR("10102-90-6", "Cu2P2O7", "Copper pyrophosphate", "Cu2P2O7", "Solid", 161024566,
   "The copper salt of cyanide-free plating baths, used for printed circuit boards.")
SR("5892-10-4", "BiSubcarbonate", "Bismuth subcarbonate", "Bi2O2CO3", "Solid", "Bismuth_subcarbonate",
   "(BiO)2CO3: an X-ray-visible filler in catheters, and the bismuth of milk of bismuth.")
SR("2956-12-9", "AllylAmylXanthate", "Allyl amyl xanthate", "C9H16OS2", "Liquid", 76289,
   "A flotation collector: it clings to copper sulfide grains and carries them up on the froth.", "C=CCSC(=S)OCCCCC")
SR("17572-97-3", "K3EDTA", "Tripotassium EDTA", "C10H13K3N2O8", "Solid", 87068754,
   "The anticoagulant in the lavender-topped tubes of blood counts: it holds the calcium blood needs to clot.",
   "[K+].[K+].[K+].OC(=O)CN(CCN(CC([O-])=O)CC([O-])=O)CC([O-])=O")
P["SAN"] = "Styrene-acrylonitrile_resin"
X("SAN", "Styrene-acrylonitrile", "(C11H11N)n", "Solid",
  "SAN: a clear, rigid copolymer for kitchenware and battery cases, and the glassy half of ABS.", P["SAN"], id=0,
  balance="C11H11N", props=["IsPolymer"])
CANON["55844-94-5"] = "SAN"
SR("593-85-1", "GuCarbonate", "Guanidine carbonate", "C3H12N6O3", "Solid", "Guanidine_carbonate",
   "A strong organic base in hair straighteners, and an accelerator in carbon-fibre production.",
   "NC(N)=N.NC(N)=N.OC(O)=O")

# --- the reactions ------------------------------------------------------------------------------
E4.reactions += [
    R("Bismarck Brown R", "3 TDA + 2 NaNO2 + 2 HCl -> BismarckBrownR + 2 NaCl + 4 H2O", COOL,
      "Toluenediamine half diazotised, coupling with itself into a brown trisazo dye.", wiki=P["BismarckBrownR"], T=5),
    R("Bismuth Subcarbonate", "Bi2O3 + CO2 -> BiSubcarbonate", MIX,
      "Bismuth oxide takes up carbon dioxide into the basic carbonate.", wiki=P["BiSubcarbonate"]),
    R("Tetrabasic Lead Sulfate", "4 PbO + PbSO4 -> TBLS", HEAT,
      "Litharge and lead sulfate cured warm and damp, as battery plates are.", wiki=P["TBLS"], T=90),
]
E5.reactions += [
    R("Triethylene Glycol", "DEG + EO -> TEG", PRESS,
      "One more ethylene oxide on diethylene glycol; glycol plants make it alongside the others.", wiki=P["TEG"], T=150),
    R("Copper Phthalocyanine", "4 Phthalonitrile + Cu -> CuPc", HEAT,
      "Four phthalonitriles close round a copper atom (ICI's Monastral blue, 1935).", wiki=P["CuPc"], T=250),
    R("Phthalocyanine Green", "CuPc + 16 Cl2 -> PG7 + 16 HCl", HEAT,
      "Copper phthalocyanine chlorinated in a melt of aluminium chloride and salt.", wiki=P["PG7"], T=200),
    R("Stearoyl Chloride", "StearicAcid + SOCl2 -> StearoylCl + SO2 + HCl", FLASK,
      "Stearic acid on thionyl chloride; the by-products leave as gases.", wiki=P["StearoylCl"], T=70),
    R("TNPP", "3 Nonylphenol + PCl3 -> TNPP + 3 HCl", FLASK,
      "Nonylphenol on phosphorus trichloride, the hydrogen chloride driven off.", wiki=P["TNPP"], T=120),
    R("Triethylene Glycol Bis(2-ethylhexanoate)", "TEG + 2 EHAcid -> TEGEH + 2 H2O", FLASK,
      "Triethylene glycol esterified at both ends with 2-ethylhexanoic acid.", wiki=P["TEGEH"], T=200),
    R("Dibutylaminopropylamine", "Dibutylamine + Acrylonitrile + 2 H2 -> DBAPA", CAT,
      "Dibutylamine added across acrylonitrile, then the nitrile hydrogenated.", wiki=P["DBAPA"], cat="Ni", T=100),
    R("Limonene Oxide", "Limonene + H2O2 -> LimoneneOxide + H2O", FLASK,
      "The ring double bond of limonene epoxidised.", wiki=P["LimoneneOxide"], T=40),
    R("Copper Chromite", "CuO + Cr2O3 -> CopperChromite", HEAT,
      "The two oxides calcined together into a spinel.", wiki=P["CopperChromite"], T=800),
    R("Potassium Hexatitanate", "Potash + 6 TiO2 -> K2Ti6O13 + CO2", SMELT,
      "Potash and titania fused; the melt grows long fine crystals.", wiki=P["K2Ti6O13"], T=1100),
    R("Aluminium Molybdate", "Alumina + 3 MoO3 -> AlMolybdate", HEAT,
      "Alumina and molybdenum trioxide calcined together.", wiki=P["AlMolybdate"], T=600),
    R("Alkenylsuccinic Anhydride", "Dodecene + MaleicAnhydride -> DDSA", HEAT,
      "The olefin adds onto maleic anhydride by the ene reaction, with no catalyst, just heat.", wiki=P["DDSA"], T=220),
    R("Triphenyl Phosphorothionate", "3 Phenol + PSCl3 -> TPPT + 3 HCl", FLASK,
      "Phenol on thiophosphoryl chloride.", wiki=P["TPPT"], T=150),
    R("Diisopropyl Succinate", "Succinic + 2 Isopropanol -> DiPS + 2 H2O", FLASK,
      "Succinic acid esterified with isopropanol.", wiki=P["DiPS"], T=100),
    R("TEG Dimethacrylate", "TEG + 2 MethacrylicAcid -> TEGDMA + 2 H2O", FLASK,
      "Triethylene glycol esterified at both ends with methacrylic acid.", wiki=P["TEGDMA"], T=110),
    R("Sodium Dibutyldithiocarbamate", "Dibutylamine + CS2 + NaOH -> NaDBDTC + H2O", MIX,
      "Dibutylamine and carbon disulfide in caustic soda.", wiki=P["NaDBDTC"]),
    R("Sodium Glucoheptonate", "Glucose + NaCN + 2 H2O -> NaGlucoheptonate + NH3", MIX,
      "Kiliani's chain extension: cyanide adds to glucose, and the nitrile hydrolyses to the acid with ammonia given off.",
      wiki=P["NaGlucoheptonate"]),
    R("Zinc Chromite", "ZnO + Cr2O3 -> ZnCr2O4", HEAT,
      "Zinc and chromium oxides calcined into a spinel.", wiki=P["ZnCr2O4"], T=800),
    R("Bismuth Molybdate", "Bi2O3 + 3 MoO3 -> BiMolybdate", HEAT,
      "Bismuth and molybdenum oxides calcined together.", wiki=P["BiMolybdate"], T=600),
    R("Copper Pyrophosphate", "2 CuSO4 + SAPP + 2 NaOH -> Cu2P2O7 + 2 Na2SO4 + 2 H2O", MIX,
      "Copper sulfate precipitated with sodium pyrophosphate.", wiki=P["Cu2P2O7"]),
    R("Allyl Amyl Xanthate", "Pentanol + CS2 + NaOH + AllylChloride -> AllylAmylXanthate + NaCl + H2O", MIX,
      "Amyl xanthate made from pentanol, carbon disulfide and caustic, then allylated.", wiki=P["AllylAmylXanthate"]),
    R("Tripotassium EDTA", "EDTA + 3 KOH -> K3EDTA + 3 H2O", MIX,
      "EDTA neutralised with potash lye.", wiki=P["K3EDTA"]),
    R("Styrene-Acrylonitrile", "Styrene + Acrylonitrile -> SAN", POLY,
      "Styrene and acrylonitrile copolymerised; the nitrile makes it tougher and solvent-proof.", wiki=P["SAN"], exact=False),
    R("Guanidine Carbonate", "2 GuHCl + SodaAsh -> GuCarbonate + 2 NaCl", MIX,
      "Guanidine hydrochloride converted with soda.", wiki=P["GuCarbonate"]),
]
E6.reactions += [
    R("Florol", "Isovaleraldehyde + Isoprenol -> Florol", FLASK,
      "A Prins cyclisation: the aldehyde and isoprenol close into a hydroxylated tetrahydropyran in acid.", wiki=P["Florol"], T=60),
    R("Polyaziridine Crosslinker", "TMPTA + 3 Propylenimine -> TMPMAP", MIX,
      "Propylenimine adds to each of the three acrylate double bonds.", wiki=P["TMPMAP"]),
    R("Drometrizole", "oNitroaniline + NaNO2 + HCl + pCresol + 2 H2 -> Drometrizole + NaCl + 4 H2O", FLASK,
      "o-Nitroaniline diazotised and coupled to p-cresol; the azo dye reduced and closed into the benzotriazole.",
      wiki=P["Drometrizole"], T=20),
]

import authored_canon_21  # noqa: E402,F401
