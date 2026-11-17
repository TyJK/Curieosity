"""
Curieosity's industrial chemistry, part 30 (see authored_canon.py): the rest of the doubtful and
wrong canon records that can be honestly made, and more classes. Pigment Yellow 83 and Pigment
Orange 16, the carbazole violet PV23, the Stabaxol hydrolysis stabiliser, an antimicrobial silane,
hexamethonium (the first drug for high blood pressure), the IPBC preservative, and the families
PEG, CAB, sulfur black, octylphenol-formaldehyde resin and Irganox 1135.
"""

from authored_canon import S, R, CANON  # noqa: F401
from authored_content import E3, E4, E5, E6, X  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR, pubchem)

P = {}
MED = ("IsMedicine",)
CLASS = ("IsClass",)


def PC(cas, key, name, formula, state, ref, desc, smiles=None, props=()):
    """A compound whose page is on PubChem (by CID, or by name)."""
    P[key] = pubchem(ref)
    S(cas, key, name, formula, state, P[key], desc, smiles=smiles, props=props)


def WK(cas, key, name, formula, state, title, desc, smiles=None, props=()):
    """A compound with a Wikipedia article."""
    P[key] = title
    S(cas, key, name, formula, state, title, desc, smiles=smiles, props=props)


def FAMILY(key, name, formula, state, ref, desc, members, smiles=None, props=CLASS):
    """A class of compounds as one substance (see authored_canon_27.FAMILY)."""
    P[key] = ref
    X(key, name, formula, state, desc, ref, id=0, smiles=smiles, props=props,
      balance=None if formula != "mixture" else "C")
    for cas in members:
        CANON[cas] = key


CANON.update({"1333-73-9": "Borax"})  # "sodium borate": commercial borax

# --- intermediates ------------------------------------------------------------------------------
PC("24544-04-5", "DIPA26", "2,6-Diisopropylaniline", "C12H19N", "Liquid", "2,6-Diisopropylaniline",
   "Aniline alkylated at both ortho positions with propylene over aluminium anilide.", "CC(C)c1cccc(C(C)C)c1N")
WK("150-78-7", "DMB", "1,4-Dimethoxybenzene", "C8H10O2", "Solid", "1,4-Dimethoxybenzene",
   "Hydroquinone dimethyl ether: a sweet, hay-like odourant and an intermediate.", "COc1ccc(OC)cc1")
PC("6358-64-1", "CDMA", "4-Chloro-2,5-dimethoxyaniline", "C8H10ClNO2", "Solid", "4-Chloro-2,5-dimethoxyaniline",
   "The amine of the coupling component of Pigment Yellow 83.", "COc1cc(N)c(OC)cc1Cl")
PC("2530-87-2", "CPTMS", "3-Chloropropyltrimethoxysilane", "C6H15ClO3Si", "Liquid", "3-Chloropropyltrimethoxysilane",
   "A silane coupling agent with a reactive chloropropyl arm.", "CO[Si](CCCCl)(OC)OC")
WK("86-74-8", "Carbazole", "Carbazole", "C12H9N", "Solid", "Carbazole",
   "A coal-tar heterocycle: the start of carbazole violet, and a building block of organic electronics.", "c1ccc2c(c1)[nH]c1ccccc12")
PC("86-28-2", "EtCarbazole", "N-Ethylcarbazole", "C14H13N", "Solid", "9-Ethylcarbazole", "Carbazole ethylated on its nitrogen.",
   "CCn1c2ccccc2c2ccccc21")
PC("132-32-1", "AEC", "3-Amino-9-ethylcarbazole", "C14H14N2", "Solid", "3-Amino-9-ethylcarbazole",
   "N-Ethylcarbazole nitrated and reduced; also a stain for antibodies in pathology labs.", "CCn1c2ccccc2c2cc(N)ccc21")
PC("91-23-6", "oNitroanisole", "2-Nitroanisole", "C7H7NO3", "Liquid", "2-Nitroanisole",
   "o-Nitrochlorobenzene methoxylated.", "COc1ccccc1[N+]([O-])=O")
WK("119-90-4", "Dianisidine", "o-Dianisidine", "C14H16N2O2", "Solid", "O-Dianisidine",
   "3,3'-Dimethoxybenzidine: the bis-diazo component of orange and blue azo dyes; like benzidine, a carcinogen.",
   "COc1cc(ccc1N)-c1ccc(N)c(OC)c1")
PC("115-70-8", "AEPD", "2-Amino-2-ethyl-1,3-propanediol", "C5H13NO2", "Liquid", "2-Amino-2-ethyl-1,3-propanediol",
   "Nitropropane with two formaldehydes, hydrogenated; an amine for paints and oxazolidines.", "CCC(N)(CO)CO")
WK("55406-53-6", "IPBC", "Iodopropynyl butylcarbamate", "C8H12INO2", "Solid", "Iodopropynyl_butylcarbamate",
   "A fungicide that keeps paint films, wood stains and cosmetics from going mouldy.", "CCCCNC(=O)OCC#CI")
FAMILY("PEG", "Polyethylene glycol", "mixture", "Solid", "Polyethylene_glycol",
       "Ethylene oxide grown on water: a laxative, the base of ointments and toothpastes, and the polymer that hides protein drugs from the immune system.",
       ["25322-68-3"], props=("IsPolymer", "IsClass"))

# --- the records -------------------------------------------------------------------------------
PC("2162-74-5", "Stabaxol", "Bis(2,6-diisopropylphenyl)carbodiimide", "C25H34N2", "Solid", 75100,
   "Stabaxol I: it mops up the acid and water that would split polyurethanes and polyesters back apart.",
   "CC(C)c1cccc(C(C)C)c1N=C=Nc1c(cccc1C(C)C)C(C)C")
PC("4433-79-8", "AAOCDMA", "Acetoacet-4-chloro-2,5-dimethoxyanilide", "C12H14ClNO4", "Solid", 78170,
   "The coupling component of Pigment Yellow 83.", "COc1cc(NC(=O)CC(C)=O)c(OC)cc1Cl")
PC("5567-15-7", "PY83", "Pigment Yellow 83", "C36H32Cl4N6O8", "Solid", 21733,
   "A reddish diarylide yellow of great strength, for plastics, inks and car paints.",
   "COc1cc(NC(=O)C(N=Nc2ccc(cc2Cl)-c2ccc(N=NC(C(C)=O)C(=O)Nc3cc(OC)c(Cl)cc3OC)c(Cl)c2)C(C)=O)c(OC)cc1Cl")
PC("7652-64-4", "IPBMA", "1,1'-Isophthaloylbis(2-methylaziridine)", "C14H16N2O2", "Liquid", 24301,
   "A crosslinker that makes waterborne coatings and adhesives tough and solvent-proof.", "CC1CN1C(=O)c1cccc(c1)C(=O)N1CC1C")
PC("78350-78-4", "IPSBPDC", "Isopropyl sec-butyl peroxydicarbonate", "C9H16O6", "Liquid", 174128,
   "A cold initiator for PVC.", "CCC(C)OC(=O)OOC(=O)OC(C)C")
PC("1002-67-1", "DEGMEE", "Diethylene glycol methyl ethyl ether", "C7H16O3", "Liquid", 13847,
   "A mixed glyme solvent for inks and resin syntheses.", "CCOCCOCCOC")
PC("27668-52-6", "Dow5700", "Dimethyloctadecyl(3-trimethoxysilylpropyl)ammonium chloride", "C26H58ClNO3Si", "Liquid", 62827,
   "An antimicrobial that bonds to fabrics and surfaces: its long-chain quat pierces microbes while the silane anchors it.",
   "[Cl-].CCCCCCCCCCCCCCCCCC[N+](C)(C)CCC[Si](OC)(OC)OC")
PC("431-63-0", "HFC236ea", "HFC-236ea", "C3H2F6", "Gas", 79009, "A refrigerant and fire-suppressant gas.", "FC(F)C(F)C(F)(F)F")
PC("6358-30-1", "PV23", "Pigment Violet 23", "C34H22Cl2N4O2", "Solid", 61387,
   "Carbazole dioxazine violet: the strongest violet pigment, for paints, plastics and printing inks.",
   "CCn1c2ccccc2c2cc3nc4c(Cl)c5oc6cc7c(cc6nc5c(Cl)c4oc3cc21)c1ccccc1n7CC")
WK("60-25-3", "HexamethoniumCl", "Hexamethonium chloride", "C12H30Cl2N2", "Solid", "Hexamethonium",
   "A ganglion blocker (1950): the first drug that lowered high blood pressure, since replaced by gentler ones.",
   "[Cl-].[Cl-].C[N+](C)(C)CCCCCC[N+](C)(C)C", props=MED)
PC("55-97-0", "HexamethoniumBr", "Hexamethonium bromide", "C12H30Br2N2", "Solid", 23723027,
   "Hexamethonium as its bromide.", "[Br-].[Br-].C[N+](C)(C)CCCCCC[N+](C)(C)C", props=MED)
PC("30364-51-3", "SMS", "Sodium myristoyl sarcosinate", "C17H32NNaO3", "Solid", 87316825,
   "A mild foaming surfactant for toothpastes and cleansers.", "[Na+].CCCCCCCCCCCCCC(=O)N(C)CC([O-])=O")
PC("20325-40-0", "DianisidineHCl", "o-Dianisidine dihydrochloride", "C14H18Cl2N2O2", "Solid", 12309823,
   "Dianisidine as its salt, the form in which it is stored and diazotised.", "Cl.Cl.COc1cc(ccc1N)-c1ccc(N)c(OC)c1")
PC("6505-28-8", "PO16", "Pigment Orange 16", "C34H32N6O6", "Solid", 110869,
   "Dianisidine orange, a strong orange for printing inks.",
   "COc1cc(ccc1N=NC(C(C)=O)C(=O)Nc1ccccc1)-c1ccc(N=NC(C(C)=O)C(=O)Nc2ccccc2)c(OC)c1")
PC("12068-53-0", "ZnAl2O4", "Zinc aluminate", "Al2O4Zn", "Solid", 11686902,
   "Gahnite spinel: a catalyst support and a hard, clear ceramic.")
PC("12042-92-1", "CuAl2O4", "Copper aluminate", "Al2CuO4", "Solid", 156594526,
   "A copper spinel for catalysts and blue-green ceramic colours.")
PC("12003-13-3", "AATiCl3", "Aluminium-activated titanium trichloride", "AlCl12Ti3", "Solid", 156591911,
   "TiCl3 with aluminium chloride locked in: the first-generation Ziegler-Natta catalyst for polypropylene.")
PC("76114-73-3", "PBC", "Propargyl butylcarbamate", "C8H13NO2", "Liquid", 10877354, "Propargyl alcohol on butyl isocyanate.",
   "CCCCNC(=O)OCC#C")
PC("111-05-7", "OleicIPA", "Oleic acid isopropanolamide", "C21H41NO2", "Solid", 66972,
   "A thickener and foam booster for shampoos.", "CCCCCCCCC=CCCCCCCCC(=O)NCC(C)O")
PC("7747-35-5", "OxazolidineE", "Oxazolidine E", "C7H13NO2", "Liquid", 82190,
   "A bicyclic oxazolidine that releases formaldehyde slowly: a preservative and a moisture scavenger for polyurethane coatings.",
   "CCC12COCN1COC2")
PC("34832-88-7", "DEHTCP", "Bis(2-ethylhexyl) tetrachlorophthalate", "C24H34Cl4O4", "Liquid", 118190,
   "A flame-retardant plasticiser for PVC.", "CCCCC(CC)COC(=O)c1c(Cl)c(Cl)c(Cl)c(Cl)c1C(=O)OCC(CC)CCCC")
PC("21112-37-8", "tBuDMB", "2-tert-Butyl-1,4-dimethoxybenzene", "C12H18O2", "Solid", 88792,
   "A redox shuttle that keeps lithium-ion cells from overcharging.", "COc1ccc(OC)c(c1)C(C)(C)C")
PC("5895-46-5", "Nd2CO33", "Neodymium carbonate", "C3Nd2O9", "Solid", 87070862,
   "The neodymium salt that rare-earth refineries precipitate and calcine to the oxide.")
FAMILY("Irganox1135", "Irganox 1135", "C25H42O3", "Liquid", pubchem("Irganox 1135"),
       "A liquid hindered-phenol antioxidant (C7 to C9 branched esters) for polyurethane foam and lubricants. Shown as the 2-ethylhexyl ester.",
       ["125643-61-0"], smiles="CCCCC(CC)COC(=O)CCc1cc(c(O)c(c1)C(C)(C)C)C(C)(C)C")
FAMILY("CAB", "Cellulose acetate butyrate", "mixture", "Solid", "Cellulose_acetate_butyrate",
       "Cellulose esterified with acetic and butyric acids: a clear, tough plastic for tool handles and spectacle frames, and a flow aid in car paints.",
       ["9004-36-8"], props=("IsPolymer", "IsClass"))
FAMILY("PEGDA", "Polyethylene glycol diacrylate", "mixture", "Liquid", pubchem("Polyethylene glycol diacrylate"),
       "PEG capped with acrylate at both ends: it cures in light into the soft hydrogels of contact lenses and cell scaffolds.",
       ["26570-48-9"])
FAMILY("SulphurBlack", "Sulphur Black 1", "mixture", "Solid", "Sulfur_dye",
       "The cheapest black and the dye made in the largest tonnage: dinitrophenol baked with polysulfide, for denim and workwear.",
       ["1326-82-5"])
FAMILY("OPFResin", "Octylphenol-formaldehyde resin", "mixture", "Solid", pubchem("Octylphenol formaldehyde resin"),
       "A tackifying resin that makes uncured tyre rubber stick to itself while the tyre is built.", ["26678-93-3"],
       props=("IsPolymer", "IsClass"))

# --- the reactions -------------------------------------------------------------------------------
E5.reactions += [
    R("2,6-Diisopropylaniline", "Aniline + 2 Propylene -> DIPA26", HIGHP,
      "Aniline ortho-alkylated with propylene on aluminium anilide.", wiki=P["DIPA26"], T=300),
    R("Stabaxol", "2 DIPA26 + 2 COCl2 -> Stabaxol + CO2 + 4 HCl", FLASK,
      "The aniline phosgenated to its isocyanate; a phospholene oxide then joins two isocyanates, giving off carbon dioxide.",
      wiki=P["Stabaxol"], T=150),
    R("1,4-Dimethoxybenzene", "Hydroquinone + 2 Methanol -> DMB + 2 H2O", FLASK,
      "Hydroquinone methylated at both oxygens, in acid with methanol in excess (with less, it stops at MEHQ).", wiki=P["DMB"], T=150),
    R("4-Chloro-2,5-dimethoxyaniline", "DMB + Cl2 + HNO3 + 3 H2 -> CDMA + HCl + 3 H2O", CAT,
      "Dimethoxybenzene chlorinated once, nitrated, and the nitro group hydrogenated.", wiki=P["CDMA"], cat="Pt", T=80),
    R("Acetoacet-4-chloro-2,5-dimethoxyanilide", "Diketene + CDMA -> AAOCDMA", MIX, "The aniline acetoacetylated.", wiki=P["AAOCDMA"]),
    R("Pigment Yellow 83", "DCB + 2 NaNO2 + 2 HCl + 2 AAOCDMA -> PY83 + 2 NaCl + 4 H2O", COOL,
      "Dichlorobenzidine diazotised and coupled to two acetoacet-chlorodimethoxyanilides.", wiki=P["PY83"], T=5),
    R("Isophthaloylbis(methylaziridine)", "IPC + 2 Propylenimine + 2 NaOH -> IPBMA + 2 NaCl + 2 H2O", COOL,
      "Isophthaloyl chloride amidated with 2-methylaziridine, cold, with the rings kept shut.", wiki=P["IPBMA"], T=0),
    R("Isopropyl sec-Butyl Peroxydicarbonate", "Isopropanol + Butanol2 + 2 COCl2 + H2O2 + 2 NaOH -> IPSBPDC + 2 NaCl + 2 HCl + 2 H2O",
      COOL, "Two chloroformates, one from each alcohol, joined by alkaline peroxide.", wiki=P["IPSBPDC"], T=0),
    R("DEG Methyl Ethyl Ether", "Carbitol + CH3Cl + NaOH -> DEGMEE + NaCl + H2O", FLASK, "Carbitol's free hydroxyl methylated.",
      wiki=P["DEGMEE"], T=100),
    R("3-Chloropropyltrimethoxysilane", "AllylChloride + HSiCl3 + 3 Methanol -> CPTMS + 3 HCl", CAT,
      "Trichlorosilane added to allyl chloride over platinum, then the chlorines on silicon swapped for methoxy.",
      wiki=P["CPTMS"], cat="Pt", T=100),
    R("Antimicrobial Silane Quat", "DMA18 + CPTMS -> Dow5700", HEAT,
      "Dimethyloctadecylamine quaternised with the chloropropyl silane.", wiki=P["Dow5700"], T=120),
    R("HFC-236ea", "HFP + H2 -> HFC236ea", CAT, "Hexafluoropropylene hydrogenated over palladium.", wiki=P["HFC236ea"], cat="Pd", T=150),
    R("Carbazole", "CoalTar -> Carbazole + Anthracene", HEAT,
      "The anthracene-oil cut of coal tar fused with potash, which takes carbazole up as its potassium salt.",
      wiki=P["Carbazole"], exact=False, T=250),
    R("N-Ethylcarbazole", "Carbazole + EtCl + NaOH -> EtCarbazole + NaCl + H2O", FLASK, "Carbazole ethylated.", wiki=P["EtCarbazole"], T=80),
    R("3-Amino-9-ethylcarbazole", "EtCarbazole + HNO3 + 3 H2 -> AEC + 3 H2O", CAT,
      "N-Ethylcarbazole nitrated and the nitro group hydrogenated.", wiki=P["AEC"], cat="Ni", T=80),
    R("Pigment Violet 23", "2 AEC + Chloranil + O2 -> PV23 + 2 HCl + 2 H2O", HEAT,
      "Two aminoethylcarbazoles condensed onto chloranil, then the rings closed by oxidation into the dioxazine.",
      wiki=P["PV23"], T=180),
    R("Hexamethonium Chloride", "HMDA + 6 CH3Cl + 4 NaOH -> HexamethoniumCl + 4 NaCl + 4 H2O", FLASK,
      "Hexamethylenediamine methylated until both nitrogens carry three methyls and a charge.", wiki=P["HexamethoniumCl"], T=80),
    R("Hexamethonium Bromide", "HMDA + 6 MeBr + 4 NaOH -> HexamethoniumBr + 4 NaBr + 4 H2O", FLASK,
      "The same with methyl bromide.", wiki=P["HexamethoniumBr"], T=60),
    R("Sodium Myristoyl Sarcosinate", "MyristicAcid + Sarcosine + NaOH -> SMS + 2 H2O", HEAT,
      "Sarcosine acylated with myristic acid (by way of its chloride) and neutralised.", wiki=P["SMS"], T=150),
    R("2-Nitroanisole", "ONCB + NaOH + Methanol -> oNitroanisole + NaCl + H2O", FLASK,
      "Methoxide displaces the chlorine next to the nitro group.", wiki=P["oNitroanisole"], T=80),
    R("o-Dianisidine", "2 oNitroanisole + 5 H2 -> Dianisidine + 4 H2O", CAT,
      "Nitroanisole reduced to the hydrazo compound, which rearranges in acid to the benzidine.", wiki=P["Dianisidine"], cat="Ni", T=80),
    R("Dianisidine Dihydrochloride", "Dianisidine + 2 HCl -> DianisidineHCl", MIX, "Dianisidine taken up in hydrochloric acid.",
      wiki=P["DianisidineHCl"]),
    R("Pigment Orange 16", "Dianisidine + 2 NaNO2 + 2 HCl + 2 Acetoacetanilide -> PO16 + 2 NaCl + 4 H2O", COOL,
      "Dianisidine diazotised at both ends and coupled to two acetoacetanilides.", wiki=P["PO16"], T=5),
    R("Zinc Aluminate", "ZnO + Alumina -> ZnAl2O4", SMELT, "Zinc oxide and alumina fired into a spinel.", wiki=P["ZnAl2O4"], T=1200),
    R("Copper Aluminate", "CuO + Alumina -> CuAl2O4", SMELT, "Copper oxide and alumina fired into a spinel.", wiki=P["CuAl2O4"], T=1100),
    R("AA-TiCl3 Catalyst", "3 TiCl4 + Al -> AATiCl3", HEAT,
      "Titanium tetrachloride reduced by aluminium; the aluminium chloride formed stays in the crystal.", wiki=P["AATiCl3"], T=200),
    R("Propargyl Butylcarbamate", "PropargylAlcohol + BuNCO -> PBC", MIX, "Propargyl alcohol adds to butyl isocyanate.", wiki=P["PBC"]),
    R("IPBC", "PBC + I2 + NaOH -> IPBC + NaI + H2O", MIX, "The alkyne's end hydrogen swapped for iodine in alkaline iodine.",
      wiki=P["IPBC"]),
    R("Oleic Isopropanolamide", "OleicAcid + MIPA -> OleicIPA + H2O", HEAT, "Oleic acid amidated with isopropanolamine.",
      wiki=P["OleicIPA"], T=160),
    R("AEPD", "NitroPropane1 + 2 CH2O + 3 H2 -> AEPD + 2 H2O", HIGHP,
      "1-Nitropropane takes two formaldehydes, then the nitro group is hydrogenated under pressure.", wiki=P["AEPD"], T=60),
    R("Oxazolidine E", "AEPD + 2 CH2O -> OxazolidineE + 2 H2O", MIX, "The aminodiol closes two oxazolidine rings with formaldehyde.",
      wiki=P["OxazolidineE"]),
    R("Bis(2-ethylhexyl) Tetrachlorophthalate", "TCPA + 2 2EH -> DEHTCP + H2O", CAT,
      "Tetrachlorophthalic anhydride esterified with 2-ethylhexanol.", wiki=P["DEHTCP"], cat="H2SO4", T=200),
    R("tert-Butyldimethoxybenzene", "DMB + Isobutylene -> tBuDMB", CAT, "Dimethoxybenzene butylated once.", wiki=P["tBuDMB"],
      cat="H2SO4", T=40),
    R("Neodymium Carbonate", "2 NdCl3 + 3 SodaAsh -> Nd2CO33 + 6 NaCl", MIX, "Neodymium precipitated from chloride solution by soda.",
      wiki=P["Nd2CO33"]),
    R("Irganox 1135", "Metilox + 2EH -> Irganox1135 + Methanol", CAT,
      "The methyl ester transesterified with branched C7 to C9 alcohols.", wiki=P["Irganox1135"], cat="TiOtBu4", T=180),
    R("Polyethylene Glycol", "EO + H2O -> PEG", POLY, "Ethylene oxide grown on water with a base, to the chain length wanted.",
      wiki=P["PEG"], exact=False),
    R("PEG Diacrylate", "PEG + AcrylicAcid -> PEGDA", FLASK, "PEG esterified with acrylic acid at both ends.", wiki=P["PEGDA"],
      exact=False, T=100),
    R("Cellulose Acetate Butyrate", "Cellulose + AceticAnhydride + ButyricAnhydride -> CAB", FLASK,
      "Cotton linters esterified with acetic and butyric anhydrides in sulfuric acid.", wiki=P["CAB"], exact=False, T=40),
    R("Sulphur Black", "DNP24 + Na2S4 -> SulphurBlack", HEAT,
      "2,4-Dinitrophenol boiled for days with sodium polysulfide.", wiki=P["SulphurBlack"], exact=False, T=110),
    R("Octylphenol-Formaldehyde Resin", "OctylPhenol + CH2O -> OPFResin", POLY,
      "Octylphenol condensed with formaldehyde into a novolac.", wiki=P["OPFResin"], exact=False, T=100),
]
import authored_canon_31  # noqa: E402,F401
