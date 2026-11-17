"""
Curieosity's industrial chemistry, part 26 (see authored_canon.py): literature routes for canon
compounds that had none, with the intermediates they need. Polyimide monomers (BPADA for Ultem,
BPDA, BTDA), the perylene pigments from acenaphthene, Allura Red from cresidine, the zeolite
template TPAOH, Novec 1230, DCC, benzisothiazolinone, and the polymers PVOH, EVA and the poloxamers.
"""

from authored_canon import S, R, CANON  # noqa: F401
from authored_content import E3, E4, E5, E6, X  # noqa: F401
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


def POLYMER(cas, key, name, formula, unit, title, desc):
    P[key] = title
    X(key, name, formula, "Solid", desc, title, id=0, balance=unit, props=("IsPolymer",))
    CANON[cas] = key


# --- polyimide and polyetherimide monomers -----------------------------------------------------
PC("550-44-7", "NMPI", "N-Methylphthalimide", "C9H7NO2", "Solid", 11074,
   "Phthalic anhydride on methylamine; nitrated, it carries bisphenol A into Ultem.", "CN1C(=O)c2ccccc2C1=O")
PC("41663-84-2", "NitroNMPI", "4-Nitro-N-methylphthalimide", "C9H6N2O4", "Solid", "4-Nitro-N-methylphthalimide",
   "Its nitro group is pushed out by phenoxide: the ether-forming step of polyetherimide.", "CN1C(=O)c2ccc(cc2C1=O)[N+]([O-])=O")
PC("38103-06-9", "BPADA", "Bisphenol A dianhydride", "C31H20O8", "Solid", 94483,
   "The dianhydride of Ultem polyetherimide, the amber plastic of aircraft interiors and sterilisable medical trays.",
   "CC(C)(c1ccc(Oc2ccc3C(=O)OC(=O)c3c2)cc1)c1ccc(Oc2ccc3C(=O)OC(=O)c3c2)cc1")
PC("2420-87-3", "BPDA", "Biphenyltetracarboxylic dianhydride", "C16H6O6", "Solid", 75494,
   "The rigid dianhydride of Upilex polyimide film, for flexible circuits.", "O=C1OC(=O)c2cc(ccc12)-c1ccc2C(=O)OC(=O)c2c1")
PC("1742-14-9", "DXE", "1,1-Bis(3,4-dimethylphenyl)ethane", "C18H22", "Liquid", 74448,
   "Two o-xylenes joined by acetaldehyde.", "CC(c1ccc(C)c(C)c1)c1ccc(C)c(C)c1")
PC("2421-28-5", "BTDA", "Benzophenonetetracarboxylic dianhydride", "C17H6O7", "Solid", 75498,
   "A polyimide dianhydride and an epoxy hardener for high-temperature adhesives.", "O=C(c1ccc2C(=O)OC(=O)c2c1)c1ccc2C(=O)OC(=O)c2c1")
WK("75-13-8", "HNCO", "Isocyanic acid", "CHNO", "Gas", "Isocyanic_acid",
   "Urea's cracking product; it adds to olefins and alcohols to make isocyanates and carbamates.", "N=C=O")
PC("2778-42-9", "TMXDI", "TMXDI", "C14H16N2O2", "Liquid", 17719,
   "A non-yellowing isocyanate whose groups sit on tertiary carbons, for light-stable polyurethane coatings.",
   "CC(C)(N=C=O)c1cccc(c1)C(C)(C)N=C=O")

# --- stabilisers and fluorochemicals -----------------------------------------------------------
PC("26741-53-7", "Irgafos126", "Bis(2,4-di-tert-butylphenyl) pentaerythritol diphosphite", "C33H50O6P2", "Solid", 93101,
   "A phosphite stabiliser that protects polyolefins while they are melted and moulded.",
   "CC(C)(C)c1ccc(OP2OCC3(CO2)COP(Oc2ccc(cc2C(C)(C)C)C(C)(C)C)OC3)c(c1)C(C)(C)C")
PC("120-95-6", "DTAP", "2,4-Di-tert-amylphenol", "C16H26O", "Liquid", 8455, "Phenol alkylated twice with isoamylene.",
   "CCC(C)(C)c1ccc(O)c(c1)C(C)(C)CC")
PC("25973-55-1", "UV328", "UV-328", "C22H29N3O", "Solid", 33263,
   "A benzotriazole UV absorber for car coatings and plastics.", "CCC(C)(C)c1cc(c(O)c(c1)-n1nc2ccccc2n1)C(C)(C)CC")
PC("27676-62-6", "Irganox3114", "Irganox 3114", "C48H69N3O6", "Solid", 93115,
   "Three hindered phenols on an isocyanurate core: an antioxidant for polypropylene that does not stain.",
   "CC(C)(C)c1cc(CN2C(=O)N(Cc3cc(c(O)c(c3)C(C)(C)C)C(C)(C)C)C(=O)N(Cc3cc(c(O)c(c3)C(C)(C)C)C(C)(C)C)C2=O)cc(c1O)C(C)(C)C")
PC("79-03-8", "PropionylCl", "Propionyl chloride", "C3H5ClO", "Liquid", "Propionyl chloride", "Propionic acid's acid chloride.", "CCC(Cl)=O")
PC("422-61-7", "PFPF", "Perfluoropropionyl fluoride", "C3F6O", "Gas", 67912,
   "Propionyl chloride electrochemically fluorinated.", "O=C(F)C(F)(F)C(F)(F)F")
WK("756-13-8", "Novec1230", "Perfluoro(2-methyl-3-pentanone)", "C6F12O", "Liquid", "Novec_1230",
   "Novec 1230: a fire suppressant that boils off without wetting, for server rooms and museums, and an immersion coolant.",
   "O=C(C(F)(F)C(F)(F)F)C(F)(C(F)(F)F)C(F)(F)F")
PC("1941-30-6", "TPABr", "Tetrapropylammonium bromide", "C12H28BrN", "Solid", 74745,
   "Tripropylamine quaternised with propyl bromide.", "[Br-].CCC[N+](CCC)(CCC)CCC")
PC("4499-86-9", "TPAOH", "Tetrapropylammonium hydroxide", "C12H29NO", "Liquid", 20586,
   "The template around which ZSM-5 zeolite crystallises, the catalyst that turns methanol into petrol.",
   "[OH-].CCC[N+](CCC)(CCC)CCC")
PC("1590-87-0", "Si2H6", "Disilane", "Si2H6", "Gas", 74123,
   "A silicon hydride that deposits silicon films at lower temperature than silane.", "[SiH3][SiH3]")

# --- biocides, medicines, imidazoles -----------------------------------------------------------
PC("119-80-2", "DTDBA", "2,2'-Dithiodibenzoic acid", "C14H10O4S2", "Solid", "2,2'-Dithiodibenzoic acid",
   "Diazotised anthranilic acid caught by disulfide.", "OC(=O)c1ccccc1SSc1ccccc1C(O)=O")
WK("2634-33-5", "BIT", "Benzisothiazolinone", "C7H5NOS", "Solid", "Benzisothiazolinone",
   "A preservative that keeps paints, glues and detergents from rotting in the can.", "O=C1NSc2ccccc12")
PC("554-00-7", "DCA24", "2,4-Dichloroaniline", "C6H5Cl2N", "Solid", 11123, "An intermediate for dyes and fungicides.", "Nc1ccc(Cl)cc1Cl")
PC("608-31-1", "DCA26", "2,6-Dichloroaniline", "C6H5Cl2N", "Solid", 11846,
   "The aniline of diclofenac and of the blood-pressure drug clonidine.", "Nc1c(Cl)cccc1Cl")
WK("57-56-7", "Semicarbazide", "Semicarbazide", "CH5N3O", "Solid", "Semicarbazide", "Urea with one hydrazine in it.", "NNC(N)=O")
PC("698-63-5", "NitroFurfural", "5-Nitrofurfural", "C5H3NO4", "Solid", "5-Nitrofurfural",
   "The aldehyde of the nitrofuran antibacterials.", "O=Cc1ccc(o1)[N+]([O-])=O")
WK("59-87-0", "Nitrofurazone", "Nitrofurazone", "C6H6N4O4", "Solid", "Nitrofurazone",
   "A nitrofuran antibacterial for wound dressings and burns.", "NC(=O)NN=Cc1ccc(o1)[N+]([O-])=O", props=MED)
PC("91125-43-8", "NOBS", "Sodium nonanoyloxybenzenesulfonate", "C15H21NaO5S", "Solid", 23665774,
   "A bleach activator: in the wash it meets perborate and makes peracid, which bleaches at lower temperatures.",
   "CCCCCCCCC(=O)Oc1ccc(cc1)S([O-])(=O)=O.[Na+]")
WK("78-90-0", "DAP12", "1,2-Diaminopropane", "C3H10N2", "Liquid", "1,2-Diaminopropane",
   "1,2-Dichloropropane on ammonia; for chelators and imidazoles.", "CC(N)CN")
PC("931-36-2", "EMI24", "2-Ethyl-4-methylimidazole", "C6H10N2", "Liquid", 70262,
   "An accelerator for epoxy cures.", "CCc1nc(C)c[nH]1")
PC("1212-29-9", "DCTU", "1,3-Dicyclohexylthiourea", "C13H24N2S", "Solid", "1,3-Dicyclohexylthiourea",
   "Cyclohexylamine on carbon disulfide.", "S=C(NC1CCCCC1)NC1CCCCC1")
WK("538-75-0", "DCC", "N,N'-Dicyclohexylcarbodiimide", "C13H22N2", "Solid", "N,N'-Dicyclohexylcarbodiimide",
   "Sheehan's coupling reagent (1955): it takes up water to join acids to amines, and made peptide synthesis routine.",
   "C1CCC(CC1)N=C=NC1CCCCC1")

# --- perylene pigments --------------------------------------------------------------------------
WK("83-32-9", "Acenaphthene", "Acenaphthene", "C12H10", "Solid", "Acenaphthene",
   "A coal-tar hydrocarbon: naphthalene with an ethylene bridge.", "C1Cc2cccc3cccc1c23")
PC("81-84-5", "NaphthalicAnhydride", "1,8-Naphthalic anhydride", "C12H6O3", "Solid", 6693,
   "Acenaphthene oxidised; the start of the perylene pigments and naphthalimide brighteners.", "O=C1OC(=O)c2cccc3cccc1c23")
PC("81-83-4", "Naphthalimide", "1,8-Naphthalimide", "C12H7NO2", "Solid", 66491,
   "Naphthalic anhydride on ammonia.", "O=C1NC(=O)c2cccc3cccc1c23")
PC("81-33-4", "PV29", "Pigment Violet 29", "C24H10N2O4", "Solid", 66475,
   "Perylene diimide, a deep maroon pigment of car paints that will not fade in the sun.",
   "O=C1NC(=O)c2ccc3c4ccc5C(=O)NC(=O)c6ccc(c7ccc1c2c37)c4c56")
WK("128-69-8", "PTCDA", "Perylenetetracarboxylic dianhydride", "C24H8O6", "Solid", "Perylenetetracarboxylic_dianhydride",
   "The parent of the rylene dyes, and an organic semiconductor.", "O=C1OC(=O)c2ccc3c4ccc5C(=O)OC(=O)c6ccc(c7ccc1c2c37)c4c56")
PC("5521-31-3", "PR179", "Pigment Red 179", "C26H14N2O4", "Solid", 79657,
   "N,N'-Dimethylperylene diimide: a maroon of luxury car finishes.", "CN1C(=O)c2ccc3c4ccc5C(=O)N(C)C(=O)c6ccc(c7ccc(C1=O)c2c37)c4c56")

# --- azo pigments and Allura Red ----------------------------------------------------------------
PC("89-61-2", "DCNB25", "2,5-Dichloronitrobenzene", "C6H3Cl2NO2", "Solid", "2,5-Dichloronitrobenzene",
   "p-Dichlorobenzene nitrated.", "[O-][N+](=O)c1cc(Cl)ccc1Cl")
PC("89-63-4", "ClNA42", "4-Chloro-2-nitroaniline", "C6H5ClN2O2", "Solid", "4-Chloro-2-nitroaniline",
   "The diazo component of the Hansa yellows.", "Nc1ccc(Cl)cc1[N+]([O-])=O")
PC("6486-23-3", "PY3", "Pigment Yellow 3", "C16H12Cl2N4O4", "Solid", 94326,
   "Hansa Yellow 10G: a greenish yellow for paints and inks.", "CC(=O)C(N=Nc1ccc(Cl)cc1[N+]([O-])=O)C(=O)Nc1ccccc1Cl")
PC("13515-40-7", "PY73", "Pigment Yellow 73", "C17H15ClN4O5", "Solid", 61637,
   "A clean monoazo yellow for decorative paints.", "COc1ccccc1NC(=O)C(N=Nc1ccc(Cl)cc1[N+]([O-])=O)C(C)=O")
PC("120-71-8", "Cresidine", "p-Cresidine", "C8H11NO", "Solid", 8445,
   "4-Methylanisole nitrated and reduced; the amine of Allura Red.", "COc1ccc(C)cc1N")
PC("6471-78-9", "CresidineSA", "Cresidinesulfonic acid", "C8H11NO4S", "Solid", 80961,
   "Cresidine sulfonated.", "COc1cc(C)c(cc1N)S(O)(=O)=O")
PC("135-76-2", "SchaefferSalt", "Schaeffer's salt", "C10H7NaO4S", "Solid", "Sodium 6-hydroxynaphthalene-2-sulfonate",
   "2-Naphthol-6-sulfonate, a coupling component for red food dyes.", "[Na+].Oc1ccc2cc(ccc2c1)S([O-])(=O)=O")
WK("25956-17-6", "AlluraRed", "Allura Red AC", "C18H14N2Na2O8S2", "Solid", "Allura_Red_AC",
   "FD&C Red 40 (E129): the red of sweets, soft drinks and children's medicines.",
   "[Na+].[Na+].COc1cc(C)c(cc1N=Nc1c(O)ccc2cc(ccc12)S([O-])(=O)=O)S([O-])(=O)=O")

# --- terpenes and fragrance --------------------------------------------------------------------
PC("1632-73-1", "Fenchol", "Fenchol", "C10H18O", "Solid", 15406, "A camphor-earthy terpene alcohol for perfumes and flavours.",
   "CC1(C)C2CCC(C)(C2)C1O")
PC("475-20-7", "Longifolene", "Longifolene", "C15H24", "Liquid", 289151,
   "A sesquiterpene of the turpentine of the chir pine, the start of woody fragrances.", "C=C1C2CCC3C2C(C)(C)CCCC13C")
PC("6728-26-3", "Hexenal2", "trans-2-Hexenal", "C6H10O", "Liquid", 10460, "Leaf aldehyde: the smell of cut grass.", "CCCC=CC=O")

# --- polymers -----------------------------------------------------------------------------------
POLYMER("9002-89-5", "PVOH", "Polyvinyl alcohol", "(C2H4O)n", "C2H4O", "Polyvinyl_alcohol",
        "A polymer that dissolves in water: dishwasher-tab film, paper sizing, and the base of slime.")
POLYMER("24937-78-8", "EVA", "Ethylene-vinyl acetate", "(C6H10O2)n", "C6H10O2", "Ethylene-vinyl_acetate",
        "A soft, rubbery copolymer (here one-to-one; in practice 10 to 40% vinyl acetate) for shoe soles, hot-melt glue and solar-panel encapsulant.")
P["Poloxamer"] = "Poloxamer"
X("Poloxamer", "Poloxamer", "mixture", "Liquid",
  "Block copolymers of ethylene and propylene oxides: surfactants for medicines, cosmetics and cell culture.", P["Poloxamer"],
  id=0, balance="C")
CANON["9003-11-6"] = "Poloxamer"

# --- small salts -------------------------------------------------------------------------------
PC("68427-32-7", "KDecylPhosphate", "Potassium decyl phosphate", "C10H22KO4P", "Solid", 87523744,
   "An anionic surfactant for alkaline cleaners.", "[K+].CCCCCCCCCCOP(O)([O-])=O")
PC("13776-88-0", "AlMetaphosphate", "Aluminium metaphosphate", "AlO9P3", "Solid", 156591903,
   "A binder for refractories and a component of special glasses.")

# --- intermediates for records that were wrong (their real compounds, now reachable) ------------
PC("110-03-2", "DMHD", "2,5-Dimethyl-2,5-hexanediol", "C8H18O2", "Solid", 8031,
   "Acetylene ethynylated with two acetones and hydrogenated: the diol of the DBPH peroxide.", "CC(C)(O)CCC(C)(C)O")
PC("78-63-7", "DBPH", "2,5-Dimethyl-2,5-di(tert-butylperoxy)hexane", "C16H34O4", "Liquid", 6545,
   "A peroxide that crosslinks polyethylene cable insulation and silicone rubber in the hot mould.",
   "CC(C)(C)OOC(C)(C)CCC(C)(C)OOC(C)(C)C")
PC("131-56-6", "DHBP", "2,4-Dihydroxybenzophenone", "C13H10O3", "Solid", "2,4-Dihydroxybenzophenone",
   "Benzophenone-1, a UV absorber, and the core of octabenzone.", "Oc1ccc(C(=O)c2ccccc2)c(O)c1")
PC("111-85-3", "OctylCl", "1-Chlorooctane", "C8H17Cl", "Liquid", "1-Chlorooctane", "Octanol on hydrogen chloride.", "CCCCCCCCCl")
PC("1843-05-6", "Octabenzone", "Octabenzone", "C21H26O3", "Solid", 15797,
   "A benzophenone UV absorber that keeps polyolefin garden furniture and films from going brittle.",
   "CCCCCCCCOc1ccc(C(=O)c2ccccc2)c(O)c1")
PC("2163-00-0", "DCH16", "1,6-Dichlorohexane", "C6H12Cl2", "Liquid", "1,6-Dichlorohexane", "1,6-Hexanediol on hydrogen chloride.", "ClCCCCCCCl")
PC("5719-73-3", "HTS", "Sodium hexamethylene-1,6-bisthiosulfate", "C6H12Na2O6S4", "Solid", 156595141,
   "A post-vulcanisation stabiliser that keeps tyre rubber's crosslinks from breaking down in the heat.",
   "[Na+].[Na+].[O-]S(=O)(=O)SCCCCCCSS([O-])(=O)=O")
PC("4316-74-8", "NaNMT", "Sodium N-methyltaurate", "C3H8NNaO3S", "Solid", "Sodium N-methyltaurate",
   "Sodium isethionate on methylamine; the head group of the taurate surfactants.", "[Na+].CNCCS([O-])(=O)=O")
PC("137-20-2", "IgeponT", "Sodium methyl oleoyl taurate", "C21H40NNaO4S", "Solid", "Sodium methyl oleoyl taurate",
   "Igepon T (1930s): a mild, hard-water-tolerant surfactant, one of the first synthetic detergents.",
   "[Na+].CCCCCCCCC=CCCCCCCCC(=O)N(C)CCS([O-])(=O)=O")
PC("117-08-8", "TCPA", "Tetrachlorophthalic anhydride", "C8Cl4O3", "Solid", 8326,
   "Phthalic anhydride fully chlorinated: for flame-retardant resins and the phloxine dyes.", "O=C1OC(=O)c2c(Cl)c(Cl)c(Cl)c(Cl)c12")
WK("18472-87-2", "PhloxineB", "Phloxine B", "C20H2Br4Cl4Na2O5", "Solid", "Phloxine_B",
   "A pink dye for drugs and cosmetics (D&C Red 28), and a stain that marks dead cells.",
   "[Na+].[Na+].[O-]C(=O)c1c(Cl)c(Cl)c(Cl)c(Cl)c1-c1c2cc(Br)c([O-])c(Br)c2oc2c(Br)c(=O)c(Br)cc12")

# --- the reactions -------------------------------------------------------------------------------
E5.reactions += [
    R("N-Methylphthalimide", "PhthalicAnhydride + Methylamine -> NMPI + H2O", HEAT,
      "Phthalic anhydride on methylamine.", wiki=P["NMPI"], T=200),
    R("4-Nitro-N-methylphthalimide", "NMPI + HNO3 -> NitroNMPI + H2O", FLASK, "N-Methylphthalimide nitrated.", wiki=P["NitroNMPI"], T=20),
    R("Bisphenol A Dianhydride", "2 NitroNMPI + BPA + 2 NaOH + 2 PhthalicAnhydride -> BPADA + 2 NMPI + 2 NaNO2 + 2 H2O", FLASK,
      "Bisphenol A's phenoxides push out the nitro groups, then an exchange with phthalic anhydride frees the dianhydride and gives back the N-methylphthalimide.",
      wiki=P["BPADA"], T=150),
    R("Biphenyltetracarboxylic Dianhydride", "4 PhthalicAnhydride + O2 -> 2 BPDA + 2 H2O", CAT,
      "Dimethyl phthalate coupled in oxygen over palladium, hydrolysed and closed back to the anhydride.", wiki=P["BPDA"], cat="Pd", T=150),
    R("Bis(dimethylphenyl)ethane", "2 oXylene + Acetaldehyde -> DXE + H2O", FLASK,
      "Two o-xylenes condensed onto acetaldehyde in sulfuric acid.", wiki=P["DXE"], T=20),
    R("BTDA", "2 DXE + 17 O2 -> 2 BTDA + 2 CO2 + 16 H2O", CAT,
      "The four methyls oxidised to acids and the bridge to a ketone, then the anhydrides closed.", wiki=P["BTDA"], cat="Co", T=200),
    R("Cracking Urea", "Urea -> HNCO + NH3", CRACKER, "Urea vapour cracked hot into isocyanic acid and ammonia.", wiki=P["HNCO"], T=400),
    R("TMXDI", "DIPEB13 + 2 HNCO -> TMXDI", CAT,
      "Isocyanic acid added across both isopropenyl groups.", wiki=P["TMXDI"], cat="H2SO4", T=40),
    R("Irgafos 126", "Pentaerythritol + 2 PCl3 + 2 DTBP24 -> Irgafos126 + 6 HCl", FLASK,
      "Pentaerythritol makes a spiro diphosphite with phosphorus trichloride, capped by two hindered phenols.",
      wiki=P["Irgafos126"], T=100),
    R("2,4-Di-tert-amylphenol", "Phenol + 2 Isoamylene -> DTAP", CAT, "Phenol alkylated twice with isoamylene.", wiki=P["DTAP"],
      cat="H2SO4", T=80),
    R("UV-328", "oNitroaniline + NaNO2 + HCl + DTAP + 2 H2 -> UV328 + NaCl + 4 H2O", FLASK,
      "Diazotised o-nitroaniline coupled to the phenol, then the nitro group reduced until it closes the triazole ring.",
      wiki=P["UV328"], T=20),
    R("Irganox 3114", "3 DTBP26 + 3 CH2O + CyanuricAcid -> Irganox3114 + 3 H2O", FLASK,
      "Three hindered phenols bridged by formaldehyde onto cyanuric acid's nitrogens.", wiki=P["Irganox3114"], T=120),
    R("Propionyl Chloride", "3 Propionic + PCl3 -> 3 PropionylCl + H3PO3", FLASK, "Propionic acid on phosphorus trichloride.",
      wiki=P["PropionylCl"], T=50),
    R("Perfluoropropionyl Fluoride", "PropionylCl + 6 HF -> PFPF + HCl + 5 H2", ECELL,
      "Simons electrochemical fluorination: every hydrogen and the chlorine replaced by fluorine.", wiki=P["PFPF"], T=10),
    R("Novec 1230", "PFPF + HFP -> Novec1230", CAT,
      "Fluoride ion adds hexafluoropropylene to the acyl fluoride.", wiki=P["Novec1230"], cat="KF", T=60),
    R("Tetrapropylammonium Bromide", "TPrA + PrBr -> TPABr", MIX, "Tripropylamine quaternised.", wiki=P["TPABr"]),
    R("Tetrapropylammonium Hydroxide", "2 TPABr + 2 H2O -> 2 TPAOH + Br2 + H2", ECELL,
      "The bromide electrolysed through a membrane: bromine at the anode, the quaternary hydroxide at the cathode.",
      wiki=P["TPAOH"], T=30),
    R("Disilane", "2 Mg2Si + 8 HCl -> Si2H6 + 4 MgCl2 + H2", COOL,
      "Magnesium silicide in acid gives silane and some disilane, condensed apart in the cold.", wiki=P["Si2H6"], T=-20),
    R("Dithiodibenzoic Acid", "2 Anthranilic + 2 NaNO2 + 4 HCl + Na2S + S -> DTDBA + 2 N2 + 4 NaCl + 4 H2O", COOL,
      "Anthranilic acid diazotised, and the diazonium caught by sodium disulfide.", wiki=P["DTDBA"], T=5),
    R("Benzisothiazolinone", "DTDBA + 2 SOCl2 + 2 NH3 + Cl2 -> 2 BIT + 2 SO2 + 6 HCl", FLASK,
      "The acid chloride made and aminated, and chlorine closes each half into an isothiazolinone ring.", wiki=P["BIT"], T=40),
    R("2,4-Dichloroaniline", "Acetanilide + 2 Cl2 + H2O -> DCA24 + AcOH + 2 HCl", FLASK,
      "Acetanilide chlorinated at both open activated positions, then the acetyl group taken off.", wiki=P["DCA24"], T=40),
    R("2,6-Dichloroaniline", "Sulfanilamide + 2 Cl2 + 2 H2O -> DCA26 + 2 HCl + NH4HSO4", FLASK,
      "Sulfanilamide's sulfonamide blocks the para position while both ortho positions are chlorinated; then it is hydrolysed off.",
      wiki=P["DCA26"], T=100),
    R("Semicarbazide", "Urea + N2H4 -> Semicarbazide + NH3", FLASK, "Urea refluxed with one hydrazine (with two it goes on to carbohydrazide).", wiki=P["Semicarbazide"], T=110),
    R("5-Nitrofurfural", "Furfural + HNO3 -> NitroFurfural + H2O", COOL,
      "Furfural, protected as its diacetate, nitrated in acetic anhydride.", wiki=P["NitroFurfural"], T=-5),
    R("Nitrofurazone", "NitroFurfural + Semicarbazide -> Nitrofurazone + H2O", MIX,
      "The aldehyde condensed with semicarbazide.", wiki=P["Nitrofurazone"]),
    R("NOBS Bleach Activator", "NonanoicAcid + NaPhenolsulfonate -> NOBS + H2O", HEAT,
      "Sodium phenolsulfonate esterified with nonanoic acid (by way of its acetate).", wiki=P["NOBS"], T=200),
    R("1,2-Diaminopropane", "DCP12 + 4 NH3 -> DAP12 + 2 NH4Cl", PRESS,
      "Propylene dichloride ammonolysed under pressure.", wiki=P["DAP12"], T=150),
    R("2-Ethyl-4-methylimidazole", "DAP12 + Propionic -> EMI24 + 2 H2O + H2", CAT,
      "Diaminopropane and propionic acid close an imidazoline, dehydrogenated to the imidazole.", wiki=P["EMI24"], cat="Ni", T=300),
    R("Dicyclohexylthiourea", "2 Cyclohexylamine + CS2 -> DCTU + H2S", FLASK, "Cyclohexylamine on carbon disulfide.", wiki=P["DCTU"], T=60),
    R("DCC", "DCTU + PbO -> DCC + Galena + H2O", FLASK,
      "Litharge strips the thiourea's sulfur, leaving the carbodiimide.", wiki=P["DCC"], T=80),
    R("Acenaphthene from Wash Oil", "CoalTar -> Acenaphthene + Naphthalene", COOL,
      "The wash-oil cut of coal tar, chilled until acenaphthene crystallises out.", wiki=P["Acenaphthene"], exact=False),
    R("Naphthalic Anhydride", "2 Acenaphthene + 5 O2 -> 2 NaphthalicAnhydride + 4 H2O", CAT,
      "Acenaphthene oxidised in the vapour over vanadium oxide.", wiki=P["NaphthalicAnhydride"], cat="V2O5", T=400),
    R("Naphthalimide", "NaphthalicAnhydride + NH3 -> Naphthalimide + H2O", HEAT, "The anhydride on ammonia.", wiki=P["Naphthalimide"], T=150),
    R("Perylene Diimide", "2 Naphthalimide -> PV29 + 2 H2", HEAT,
      "Two naphthalimides fused in molten potash, joining into perylene.", wiki=P["PV29"], T=220),
    R("PTCDA", "PV29 + 2 H2O -> PTCDA + 2 NH3", FLASK, "The diimide hydrolysed in hot sulfuric acid.", wiki=P["PTCDA"], T=200),
    R("Pigment Red 179", "PTCDA + 2 Methylamine -> PR179 + 2 H2O", HEAT, "The dianhydride condensed with methylamine.", wiki=P["PR179"], T=150),
    R("2,5-Dichloronitrobenzene", "pDCB + HNO3 -> DCNB25 + H2O", FLASK, "p-Dichlorobenzene nitrated.", wiki=P["DCNB25"], T=50),
    R("4-Chloro-2-nitroaniline", "DCNB25 + 2 NH3 -> ClNA42 + NH4Cl", PRESS,
      "Ammonia replaces the chlorine next to the nitro group.", wiki=P["ClNA42"], T=150),
    R("Pigment Yellow 3", "ClNA42 + NaNO2 + HCl + AAOCA -> PY3 + NaCl + 2 H2O", COOL,
      "4-Chloro-2-nitroaniline diazotised and coupled to acetoacet-o-chloroanilide.", wiki=P["PY3"], T=5),
    R("Pigment Yellow 73", "ClNA42 + NaNO2 + HCl + AAOA -> PY73 + NaCl + 2 H2O", COOL,
      "The same diazonium coupled to acetoacet-o-anisidide.", wiki=P["PY73"], T=5),
    R("p-Cresidine", "MethylAnisole + HNO3 + 3 H2 -> Cresidine + 3 H2O", CAT,
      "4-Methylanisole nitrated next to its methoxy group and the nitro group hydrogenated.", wiki=P["Cresidine"], cat="Ni", T=80),
    R("Cresidinesulfonic Acid", "Cresidine + H2SO4 -> CresidineSA + H2O", HEAT, "p-Cresidine baked with sulfuric acid.", wiki=P["CresidineSA"], T=180),
    R("Schaeffer's Salt", "Naphthol2 + H2SO4 + NaOH -> SchaefferSalt + 2 H2O", FLASK,
      "2-Naphthol sulfonated at the far ring and salted out.", wiki=P["SchaefferSalt"], T=100),
    R("Allura Red AC", "CresidineSA + NaNO2 + HCl + SchaefferSalt + NaOH -> AlluraRed + NaCl + 3 H2O", COOL,
      "Diazotised cresidinesulfonic acid coupled with 2-naphthol-6-sulfonate.", wiki=P["AlluraRed"], T=5),
    R("Fenchol", "Pinene + H2O -> Fenchol", FLASK,
      "Pinene hydrated in acid: the ring rearranges, and fenchol is one of the alcohols that come out.", wiki=P["Fenchol"], T=60),
    R("Longifolene", "Turpentine -> Longifolene", HEAT,
      "What stays behind when Indian turpentine, from the chir pine, is boiled down: its high-boiling sesquiterpene part.", wiki=P["Longifolene"], exact=False),
    R("trans-2-Hexenal", "Butanal + Acetaldehyde -> Hexenal2 + H2O", FLASK,
      "Butanal and acetaldehyde in a crossed aldol condensation.", wiki=P["Hexenal2"], T=40),
    R("Polyvinyl Alcohol", "PVAc + Methanol -> PVOH + MethylAcetate", MIX,
      "Polyvinyl acetate transesterified with methanol: vinyl alcohol itself does not exist, so this is the only way in.",
      wiki=P["PVOH"]),
    R("Ethylene-Vinyl Acetate", "Ethylene + VinylAcetate -> EVA", POLY,
      "Ethylene and vinyl acetate copolymerised under high pressure.", wiki=P["EVA"]),
    R("Poloxamer", "EO + PO -> Poloxamer", POLY,
      "Propylene oxide grown into a block, then capped at both ends with ethylene oxide blocks.", wiki=P["Poloxamer"], exact=False),
    R("Potassium Decyl Phosphate", "Decanol + H3PO4 + KOH -> KDecylPhosphate + 2 H2O", HEAT,
      "Decanol phosphated and half-neutralised.", wiki=P["KDecylPhosphate"], T=120),
    R("Aluminium Metaphosphate", "AlOH3 + 3 H3PO4 -> AlMetaphosphate + 6 H2O", SMELT,
      "Aluminium hydroxide and phosphoric acid dried and calcined until the phosphates link into chains.",
      wiki=P["AlMetaphosphate"], T=800),
    R("2,5-Dimethylhexanediol", "Acetylene + 2 Acetone + 2 H2 -> DMHD", CAT,
      "Acetylene ethynylated at both ends with acetone in potash, then the triple bond hydrogenated.", wiki=P["DMHD"], cat="Ni", T=60),
    R("DBPH Peroxide", "DMHD + 2 TBHP -> DBPH + 2 H2O", FLASK,
      "The diol's tertiary hydroxyls swapped for tert-butylperoxy groups in sulfuric acid.", wiki=P["DBPH"], T=20),
    R("2,4-Dihydroxybenzophenone", "Resorcinol + BenzoicAcid -> DHBP + H2O", FLASK,
      "Resorcinol benzoylated by Friedel-Crafts with zinc chloride.", wiki=P["DHBP"], T=150),
    R("1-Chlorooctane", "Octanol + HCl -> OctylCl + H2O", HEAT, "Octanol on hydrogen chloride.", wiki=P["OctylCl"], T=120),
    R("Octabenzone", "DHBP + OctylCl + NaOH -> Octabenzone + NaCl + H2O", FLASK,
      "The 4-hydroxyl octylated; the 2-hydroxyl, held by a hydrogen bond to the ketone, stays free and does the UV work.",
      wiki=P["Octabenzone"], T=120),
    R("1,6-Dichlorohexane", "Hexanediol + 2 HCl -> DCH16 + 2 H2O", HEAT, "1,6-Hexanediol on hydrogen chloride.", wiki=P["DCH16"], T=120),
    R("HTS Stabiliser", "DCH16 + 2 Na2S2O3 -> HTS + 2 NaCl", HEAT, "Both chlorines swapped for thiosulfate (Bunte salts).", wiki=P["HTS"], T=100),
    R("Sodium N-Methyltaurate", "NaIsethionate + Methylamine -> NaNMT + H2O", PRESS,
      "Sodium isethionate aminated with methylamine under pressure.", wiki=P["NaNMT"], T=250),
    R("Igepon T", "OleicAcid + NaNMT -> IgeponT + H2O", HEAT, "Oleic acid amidated with sodium methyltaurate.", wiki=P["IgeponT"], T=200),
    R("Tetrachlorophthalic Anhydride", "PhthalicAnhydride + 4 Cl2 -> TCPA + 4 HCl", FLASK,
      "Phthalic anhydride chlorinated in oleum with iodine.", wiki=P["TCPA"], T=200),
    R("Phloxine B", "TCPA + 2 Resorcinol + 4 Br2 + 2 NaOH -> PhloxineB + 4 H2O + 4 HBr", FLASK,
      "A tetrachlorofluorescein from the anhydride and resorcinol, brominated four times and taken up in soda.",
      wiki=P["PhloxineB"], T=180),
]

# Milestones for the stretches this part lengthened (messages only).
import authored_content as _C  # noqa: E402
from gen_authored import Milestone  # noqa: E402
_C.MILESTONES += [
    Milestone("TPAOH", message="Mobil's ZSM-5 zeolite (1972) crystallises around tetrapropylammonium ions; the channels they leave later turned methanol into petrol in New Zealand."),
]
import authored_canon_27  # noqa: E402,F401
