"""
Curieosity's industrial chemistry, part 32 (see authored_canon.py): the residue of the canon
records, done where the game's chemistry can honestly reach them. Tartrazine (E102) and the food
lakes, Ambrox from clary sage, the vat dyes violanthrone and Jade Green, pyranine, DDQ, TBD, the
chlorpyrifos pyridinol, trimethylhexamethylenediamine, fluorenone, benzothiazole and δ-damascone,
plus corrected records for a handful of simple inorganics and organics whose canon data was wrong.
"""

from authored_canon import S, R, CANON  # noqa: F401
from authored_content import E3, E4, E5, E6, X, RAW, EPOCHS  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR, pubchem)

P = {}


def PC(cas, key, name, formula, state, ref, desc, smiles=None, props=()):
    """A compound whose page is on PubChem (by CID, or by name)."""
    P[key] = pubchem(ref)
    S(cas, key, name, formula, state, P[key], desc, smiles=smiles, props=props)


def WK(cas, key, name, formula, state, title, desc, smiles=None, props=()):
    """A compound with a Wikipedia article (a title, or a curid number)."""
    P[key] = title if isinstance(title, str) else f"https://en.wikipedia.org/?curid={title}"
    S(cas, key, name, formula, state, title, desc, smiles=smiles, props=props)


def FAMILY(key, name, formula, state, ref, desc, members, smiles=None, props=("IsClass",)):
    """A class or mixture of compounds as one substance (see authored_canon_27.FAMILY)."""
    P[key] = ref
    X(key, name, formula, state, desc, ref, id=0, smiles=smiles, props=props,
      balance=None if formula != "mixture" else "C")
    for cas in members:
        CANON[cas] = key


def extend(name, products):
    """Add products to a reaction already written (in any era)."""
    for e in EPOCHS:
        for r in e.reactions:
            if r.name == name:
                lhs, rhs = r.equation.split(" -> ")
                r.equation = lhs + " -> " + " + ".join([rhs] + products)
                return
    raise SystemExit(f"no reaction {name!r} to extend")


# Acid Blue 9 is Brilliant Blue FCF as its ammonium salt
CANON["2650-18-2"] = "BrilliantBlue"

RAW("ClarySage", "Clary Sage", "Salvia sclarea, grown in the south of France and Bulgaria. The waxy residue left after its oil "
    "is distilled holds sclareol, the starting point for synthetic ambergris.", "Salvia_sclarea", color="#8a7aa8")

# --- intermediates ------------------------------------------------------------------------------
WK("86-73-7", "Fluorene", "Fluorene", "C13H10", "Solid", "Fluorene",
   "A white coal-tar hydrocarbon from the wash oil; its name comes from its violet fluorescence.", "C1c2ccccc2-c2ccccc12")
PC("98-71-5", "PHSA", "4-Hydrazinobenzenesulfonic acid", "C6H8N2O3S", "Solid", "4-Hydrazinobenzenesulfonic acid",
   "Sulfanilic acid diazotised and reduced: the hydrazine half of tartrazine.", "NNc1ccc(cc1)S(O)(=O)=O")
PC("108-56-5", "DEOA", "Diethyl oxaloacetate", "C8H12O5", "Liquid", "Diethyl oxalacetate",
   "Diethyl oxalate and ethyl acetate joined by a Claisen condensation.", "CCOC(=O)CC(=O)C(=O)OCC")
PC("118-47-8", "SPCP", "1-(4-Sulfophenyl)-3-carboxy-5-pyrazolone", "C10H8N2O6S", "Solid",
   "1-(4-Sulfophenyl)-3-carboxy-5-pyrazolone", "The coupling component of tartrazine.",
   "OC(=O)C1=NN(C(=O)C1)c1ccc(cc1)S(O)(=O)=O")
PC("137-07-5", "ATP2", "2-Aminothiophenol", "C6H7NS", "Liquid", "2-Aminothiophenol",
   "Mercaptobenzothiazole hydrolysed open by alkali.", "Nc1ccccc1S")
PC("495-40-9", "Butyrophenone", "Butyrophenone", "C10H12O", "Liquid", "Butyrophenone",
   "Benzene acylated with butyryl chloride.", "CCCC(=O)c1ccccc1")
WK("106-51-4", "Benzoquinone", "1,4-Benzoquinone", "C6H4O2", "Solid", "1,4-Benzoquinone",
   "Quinone: hydroquinone oxidised. A yellow solid with a sharp chlorine-like smell.", "O=C1C=CC(=O)C=C1")
PC("4733-50-0", "DCHQ", "2,3-Dicyanohydroquinone", "C8H4N2O2", "Solid", "2,3-Dicyanohydroquinone",
   "Hydrogen cyanide added twice to benzoquinone.", "N#Cc1c(O)ccc(O)c1C#N")
WK("515-03-7", "Sclareol", "Sclareol", "C20H36O2", "Solid", "Sclareol",
   "A diterpene diol extracted from clary sage: the raw material of synthetic ambergris.",
   "CC1(C)CCCC2(C)C1CCC(C)(O)C2CCC(C)(O)C=C")
WK("564-20-5", "Sclareolide", "Sclareolide", "C16H26O2", "Solid", "Sclareolide",
   "Sclareol's side chain oxidised away, leaving a lactone.", "CC1(C)CCCC2(C)C1CCC1(C)OC(=O)CC21")
PC("38419-75-9", "Ambradiol", "Ambradiol", "C16H30O2", "Solid", "Ambradiol",
   "Sclareolide reduced to the diol.", "CC1(C)CCCC2(C)C1CCC(C)(O)C2CCO")
PC("56-18-8", "DPTA", "Dipropylenetriamine", "C6H17N3", "Liquid", "Bis(3-aminopropyl)amine",
   "Two acrylonitriles on ammonia, hydrogenated.", "NCCCNCCCN")
WK("76-02-8", "TCAC", "Trichloroacetyl chloride", "C2Cl4O", "Liquid", "Trichloroacetyl_chloride",
   "Acetyl chloride chlorinated to the end.", "ClC(Cl)(Cl)C(Cl)=O")
PC("3937-59-5", "TMAA", "Trimethyladipic acid", "C9H16O4", "Solid", "2,2,4-Trimethyladipic acid",
   "Trimethylcyclohexanol cut open by nitric acid, as adipic acid is from cyclohexanol.", "CC(CC(C)(C)C(O)=O)CC(O)=O")
PC("3937-62-0", "TMADN", "Trimethyladiponitrile", "C9H14N2", "Liquid", "2,2,4-Trimethyladiponitrile",
   "The diacid's nitrile, made over a dehydrating catalyst with ammonia.", "CC(CC(C)(C)C#N)CC#N")
WK("82-05-3", "Benzanthrone", "Benzanthrone", "C17H10O", "Solid", "Benzanthrone",
   "Anthraquinone reduced and built out with glycerol: the starting point of the violanthrone vat dyes.",
   "O=C1c2ccccc2-c2cccc3cccc1c23")
PC("128-59-6", "DHV", "16,17-Dihydroxyviolanthrone", "C34H16O4", "Solid", 31411,
   "Violanthrone oxidised at the bay positions.",
   "O=C1C=2C=CC=CC2C=3C=C(O)C=4C5=C(O)C=C6C=7C=CC=CC7C(=O)C=8C=CC(C9=CC=C1C3C94)=C5C86")
PC("6528-53-6", "PTSA4", "Pyrene-1,3,6,8-tetrasulfonic acid", "C16H10O12S4", "Solid", "Pyrene-1,3,6,8-tetrasulfonic acid",
   "Pyrene sulfonated at all four of its reactive corners.",
   "OS(=O)(=O)C=1C=C(S(=O)(=O)O)C2=CC=C3C(=CC(=C4C=CC1C2=C34)S(=O)(=O)O)S(=O)(=O)O")
WK("141-79-7", "MesitylOxide", "Mesityl oxide", "C6H10O", "Liquid", "Mesityl_oxide",
   "Acetone condensed with itself, losing water: the step on the way to MIBK.", "CC(C)=CC(C)=O")
PC(None, "TMCHAc", "1-(2,6,6-Trimethylcyclohex-3-en-1-yl)ethanone", "C11H18O", "Liquid",
   "1-(2,6,6-Trimethylcyclohex-3-en-1-yl)ethanone", "Piperylene and mesityl oxide joined in a Diels-Alder reaction.",
   "CC1C=CCC(C)(C)C1C(C)=O")
WK("13755-29-8", "NaBF4", "Sodium tetrafluoroborate", "NaBF4", "Solid", "Sodium_tetrafluoroborate",
   "A white salt; a flux for brazing and a source of the tetrafluoroborate ion.", "[Na+].F[B-](F)(F)F")
PC("625-36-5", "CPC3", "3-Chloropropionyl chloride", "C3H4Cl2O", "Liquid", "3-Chloropropionyl chloride",
   "Acrylic acid on thionyl chloride: the acid chloride forms and hydrogen chloride adds across the double bond.",
   "ClCCC(Cl)=O")
PC("1187-03-7", "TEU", "Tetraethylurea", "C9H20N2O", "Liquid", "Tetraethylurea",
   "Phosgene on diethylamine.", "CCN(CC)C(=O)N(CC)CC")
PC("99-75-2", "MeToluate", "Methyl p-toluate", "C9H10O2", "Solid", "Methyl p-toluate",
   "p-Toluic acid's methyl ester: the halfway point of the Witten process for dimethyl terephthalate.",
   "COC(=O)c1ccc(C)cc1")
PC("708-06-5", "HNA", "2-Hydroxy-1-naphthaldehyde", "C11H8O2", "Solid", "2-Hydroxy-1-naphthaldehyde",
   "2-Naphthol formylated with chloroform (the Reimer-Tiemann reaction).", "O=Cc1c(O)ccc2ccccc12")
PC("135-61-5", "NaphtholASD", "Naphthol AS-D", "C18H15NO2", "Solid", "Naphthol AS-D",
   "BON acid's o-toluidide: the coupling component of a family of naphthol reds.", "Cc1ccccc1NC(=O)c1cc2ccccc2cc1O")
PC("636-30-6", "TCA245", "2,4,5-Trichloroaniline", "C6H4Cl3N", "Solid", "2,4,5-Trichloroaniline",
   "1,2,4-Trichlorobenzene nitrated and reduced.", "Nc1cc(Cl)c(Cl)cc1Cl")

# --- the records -------------------------------------------------------------------------------
WK("486-25-9", "Fluorenone", "Fluorenone", "C13H8O", "Solid", 7258420,
   "Fluorene's bridge oxidised by air to a ketone: a bright yellow solid, and a building block for drugs and dyes.",
   "O=C1c2ccccc2-c2ccccc12")
WK("1934-21-0", "Tartrazine", "Tartrazine", "C16H9N4Na3O9S2", "Solid", 458008,
   "FD&C Yellow 5 (E102): the lemon yellow of soft drinks, custard powder and sweets, and with a blue, every food green.",
   "[Na+].[Na+].[Na+].[O-]C(=O)C1=NN(C(=O)C1N=Nc1ccc(cc1)S([O-])(=O)=O)c1ccc(cc1)S([O-])(=O)=O")
WK("95-16-9", "Benzothiazole", "Benzothiazole", "C7H5NS", "Liquid", 2022329,
   "Benzene fused to a thiazole ring: the core of rubber accelerators, and the smell of cranberries and roasted nuts.",
   "c1ccc2scnc2c1")
WK("104-51-8", "Butylbenzene", "n-Butylbenzene", "C10H14", "Liquid", 60102939,
   "Benzene with a straight four-carbon chain. Friedel-Crafts alkylation scrambles the chain, so it is made through the ketone.",
   "CCCCc1ccccc1")
WK("84-58-2", "DDQ", "DDQ", "C8Cl2N2O2", "Solid", 24644141,
   "2,3-Dichloro-5,6-dicyano-1,4-benzoquinone: a powerful oxidant that strips hydrogen from molecules to make them aromatic.",
   "N#CC1=C(C#N)C(=O)C(Cl)=C(Cl)C1=O")
WK("3738-00-9", "Ambroxide", "Ambroxide", "C16H28O", "Solid", "Ambroxide",
   "Ambrox: the woody, musky heart of ambergris, made from clary sage instead of sperm whales. It is in a great many perfumes.",
   "CC1(C)CCCC2(C)C1CCC1(C)OCCC21")
WK("95962-14-4", "Nectaryl", "Nectaryl", "C15H24O", "Liquid", 64913219,
   "A fruity apricot and peach fragrance: limonene and cyclopentanone joined by a radical chain.",
   "O=C1CCCC1CC(C)C1CC=C(C)CC1")
WK("5807-14-7", "TBD", "1,5,7-Triazabicyclo[4.4.0]dec-5-ene", "C7H13N3", "Solid", 4784160,
   "TBD: a guanidine superbase that catalyses transesterification and ring-opening polymerisation.", "C1CN=C2NCCCN2C1")
WK("6515-38-4", "TCP", "3,5,6-Trichloro-2-pyridinol", "C5H2Cl3NO", "Solid", 20858019,
   "The pyridinol half of the insecticide chlorpyrifos and the herbicide triclopyr, and what both break down to.",
   "Oc1nc(Cl)c(Cl)cc1Cl")
WK("25513-64-8", "TMD", "Trimethylhexamethylenediamine", "C9H22N2", "Liquid", 46454746,
   "TMD: a branched diamine that cures epoxy floors and makes a clear amorphous nylon.", "CC(CCN)CC(C)(C)CN")
WK("116-71-2", "Violanthrone", "Violanthrone", "C34H16O2", "Solid", 42245644,
   "Vat Blue 20: two benzanthrones fused in molten potash. A navy vat dye for cotton.",
   "O=C1C=2C=CC=CC2C=3C=CC=4C5=CC=C6C=7C=CC=CC7C(=O)C=8C=CC(C9=CC=C1C3C94)=C5C86")
WK("128-58-5", "JadeGreen", "Jade Green", "C36H20O4", "Solid", 42208547,
   "Vat Green 1 (1920): dimethoxyviolanthrone, a brilliant green vat dye of exceptional fastness for cotton.",
   "O=C1C=2C=CC=CC2C=3C=C(OC)C=4C5=C(OC)C=C6C=7C=CC=CC7C(=O)C=8C=CC(C9=CC=C1C3C94)=C5C86")
WK("6358-69-6", "Pyranine", "Pyranine", "C16H7Na3O10S3", "Solid", 14975426,
   "Solvent Green 7: the glowing yellow-green of highlighter pens, and a pH indicator that fluoresces.",
   "[Na+].[Na+].[Na+].[O-]S(=O)(=O)C=1C=C(O)C2=CC=C3C(=CC(=C4C=CC1C2=C34)S(=O)(=O)[O-])S(=O)(=O)[O-]")
WK("57378-68-4", "DeltaDamascone", "δ-Damascone", "C13H20O", "Liquid", "Damascone",
   "A rose ketone with a fruity plum note, made from piperylene and mesityl oxide.", "CC=CC(=O)C1C(C)C=CCC1(C)C")
PC("2624-17-1", "NaCyanurate", "Monosodium cyanurate", "C3H2N3NaO3", "Solid", 67544527,
   "Cyanuric acid half-neutralised: the salt that steadies the chlorine of swimming pools.", "[Na+].O=C1NC(=O)NC(=O)[N-]1")
PC("11128-29-3", "KPentaborate", "Potassium pentaborate", "KB5O8", "Solid", "Potassium pentaborate",
   "Sold as the tetrahydrate: a flux for welding and brazing, and a boron source for glass.")
PC("42797-18-2", "BBBA", "2-(4-Biphenylylcarbonyl)benzoic acid", "C20H14O3", "Solid", 39302,
   "Biphenyl acylated with phthalic anhydride: an intermediate of anthraquinone dyes.",
   "OC(=O)c1ccccc1C(=O)c1ccc(cc1)-c1ccccc1")
PC("62449-33-6", "OleylHEI", "Oleyl hydroxyethyl imidazoline", "C22H42N2O", "Liquid", 62205,
   "Oleic acid ring-closed with aminoethylethanolamine: a corrosion inhibitor for oil pipelines and a fabric softener base.",
   "OCCN1CCN=C1CCCCCCC/C=C\\CCCCCCCC")
PC("2387-03-3", "PY101", "Pigment Yellow 101", "C22H16N2O2", "Solid", 75433,
   "An aldazine of hydroxynaphthaldehyde: a pigment that fluoresces yellow-green.",
   "OC=1C=CC=2C=CC=CC2C1C=NN=CC3=C(O)C=CC=4C=CC=CC43")
PC("6535-46-2", "PR112", "Pigment Red 112", "C24H16Cl3N3O2", "Solid", 23034,
   "A naphthol red from trichloroaniline and Naphthol AS-D, for paints and inks.",
   "O=C(NC=1C=CC=CC1C)C2=CC=3C=CC=CC3C(N=NC4=CC(Cl)=C(Cl)C=C4Cl)=C2O")
WK("12007-56-6", "CaB4O7", "Calcium tetraborate", "CaB4O7", "Solid", 8646255,
   "A calcium borate for glass fibre and ceramic glazes.")
PC("13450-99-2", "SrHPO4", "Strontium hydrogen phosphate", "HO4PSr", "Solid", "Strontium hydrogen phosphate",
   "A phosphor host and a strontium-releasing bone-cement filler.", "[Sr+2].OP([O-])([O-])=O")
PC("13454-70-1", "CeMolybdate", "Cerium molybdate", "Ce2Mo3O12", "Solid", "Cerium molybdate",
   "A pale yellow pigment that protects steel from corrosion without chromate.")
WK("1113-78-6", "TSBB", "Tri-sec-butylborane", "C12H27B", "Liquid", 40622668,
   "Diborane added to three 2-butenes: a radical initiator that starts polymerisation with traces of air.",
   "CCC(C)B(C(C)CC)C(C)CC")
WK("1678-93-9", "Butylcyclohexane", "Butylcyclohexane", "C10H20", "Liquid", 7726945,
   "Butylbenzene fully hydrogenated: a jet-fuel and diesel model compound.", "CCCCC1CCCCC1")
PC("42348-86-7", "ClIndanone", "5-Chloro-1-indanone", "C9H7ClO", "Solid", 142599,
   "The building block of the insecticide indoxacarb.", "O=C1CCc2cc(Cl)ccc12")
WK("12053-27-9", "Cr2N", "Chromium nitride", "Cr2N", "Solid", "Chromium_nitride",
   "A hard, wear-resistant ceramic coating on cutting tools and piston rings.")
PC("3698-89-3", "MeSDodecane", "1-(Methylthio)dodecane", "C13H28S", "Liquid", 77287,
   "Methyl dodecyl sulfide, a sulfur antioxidant for lubricants.", "CCCCCCCCCCCCSC")
PC("4109-20-0", "DETA3HCl", "Diethylenetriamine trihydrochloride", "C4H16Cl3N3", "Solid", 19904564,
   "DETA fully neutralised by hydrochloric acid.", "Cl.Cl.Cl.NCCNCCN")
PC("69082-76-4", "HEGCl", "Hexaethylguanidinium chloride", "C13H30ClN3", "Solid", 9795249,
   "A heat-stable phase-transfer catalyst: it carries phenoxide into the solvent to make polyetherimide plastic.",
   "[Cl-].CCN(CC)C(N(CC)CC)=[N+](CC)CC")
PC("51181-40-9", "MeMCHC", "Methyl 4-methylcyclohexanecarboxylate", "C9H16O2", "Liquid", 170993,
   "Methyl p-toluate with its ring hydrogenated: a fruity, minty fragrance ester.", "COC(=O)C1CCC(C)CC1")
FAMILY("PG36", "Pigment Green 36", "mixture", "Solid", pubchem("C.I. Pigment Green 36"),
       "Phthalocyanine green YS: copper phthalocyanine brominated as well as chlorinated, a yellower green than PG7.",
       ["14302-13-7"], props=())
FAMILY("TartrazineLake", "Tartrazine aluminium lake", "mixture", "Solid", pubchem(22833487),
       "Pigment Yellow 100: tartrazine fixed on alumina, so it colours fat-based foods, coatings and cosmetics without bleeding.",
       ["12001-99-9"], props=())
FAMILY("BlueLake", "Brilliant Blue aluminium lake", "mixture", "Solid", pubchem(56841154),
       "Brilliant Blue FCF fixed on alumina: the insoluble blue of tablet coatings and candy shells.", ["68921-42-6"], props=())

# --- the reactions -------------------------------------------------------------------------------
extend("Acenaphthene from Wash Oil", ["Fluorene"])
E5.reactions += [
    R("Fluorenone", "Fluorene + O2 -> Fluorenone + H2O", CAT, "Fluorene oxidised by air in alkali.", wiki=P["Fluorenone"],
      cat="NaOH", T=80),
    R("Hydrazinobenzenesulfonic Acid", "SulfanilicAcid + NaNO2 + HCl + 2 H2 -> PHSA + NaCl + 2 H2O", FLASK,
      "Sulfanilic acid diazotised and the diazonium reduced (with sulfite) to the hydrazine.", wiki=P["PHSA"], T=10),
    R("Diethyl Oxaloacetate", "DiethylOxalate + EthylAcetate -> DEOA + Ethanol", CAT,
      "A Claisen condensation in sodium ethoxide.", wiki=P["DEOA"], cat="NaOEt", T=40),
    R("Tartrazine Pyrazolone", "PHSA + DEOA -> SPCP + 2 Ethanol", FLASK,
      "The hydrazine closes a pyrazolone ring on the keto ester, which is then saponified.", wiki=P["SPCP"], T=90),
    R("Tartrazine", "SulfanilicAcid + NaNO2 + HCl + SPCP + 3 NaOH -> Tartrazine + NaCl + 5 H2O", COOL,
      "Diazotised sulfanilic acid coupled to the pyrazolone in alkali.", wiki=P["Tartrazine"], T=5),
    R("Tartrazine Lake", "Tartrazine + AlCl3 + AlOH3 -> TartrazineLake", MIX,
      "The dye precipitated onto fresh alumina with aluminium chloride.", wiki=P["TartrazineLake"], exact=False),
    R("Brilliant Blue Lake", "BrilliantBlue + AlCl3 + AlOH3 -> BlueLake", MIX,
      "The dye precipitated onto fresh alumina with aluminium chloride.", wiki=P["BlueLake"], exact=False),
    R("2-Aminothiophenol", "MBT + 4 NaOH -> ATP2 + SodaAsh + Na2S + H2O", HIGHP,
      "Mercaptobenzothiazole hydrolysed by hot alkali under pressure.", wiki=P["ATP2"], T=200),
    R("Benzothiazole", "ATP2 + Formic -> Benzothiazole + 2 H2O", FLASK, "2-Aminothiophenol ring-closed with formic acid.",
      wiki=P["Benzothiazole"], T=100),
    R("Butyrophenone", "Benzene + ButyrylCl -> Butyrophenone + HCl", CAT, "Friedel-Crafts acylation.",
      wiki=P["Butyrophenone"], cat="AlCl3", T=40),
    R("n-Butylbenzene", "Butyrophenone + 2 H2 -> Butylbenzene + H2O", CAT, "The ketone hydrogenated away to a CH2.",
      wiki=P["Butylbenzene"], cat="Pd", T=150),
    R("Butylcyclohexane", "Butylbenzene + 3 H2 -> Butylcyclohexane", CAT, "The ring hydrogenated.",
      wiki=P["Butylcyclohexane"], cat="Ni", T=180),
    R("Benzoquinone", "2 Hydroquinone + O2 -> 2 Benzoquinone + 2 H2O", FLASK, "Hydroquinone oxidised.", wiki=P["Benzoquinone"], T=40),
    R("Dicyanohydroquinone", "2 Benzoquinone + 2 HCN -> DCHQ + Hydroquinone", FLASK,
      "Cyanide adds to quinone; a second quinone takes the hydrogen.", wiki=P["DCHQ"], T=20),
    R("DDQ", "3 DCHQ + 6 Cl2 + 2 HNO3 -> 3 DDQ + 6 HCl + 2 NO + 4 H2O", FLASK,
      "Dicyanohydroquinone chlorinated, then oxidised by nitric acid to the quinone.", wiki=P["DDQ"], T=30),
    R("Clary Sage Extraction", "ClarySage + Hexane -> Sclareol", MIX,
      "The distillation residue of clary sage extracted with hexane.", wiki=P["Sclareol"], exact=False),
    R("Sclareolide", "2 Sclareol + 5 O2 -> 2 Sclareolide + 2 Acetone + 2 CO2 + 4 H2O", FLASK,
      "Sclareol's side chain oxidatively degraded (permanganate or ozone in industry) to the lactone.",
      wiki=P["Sclareolide"], T=30),
    R("Ambradiol", "Sclareolide + 2 H2 -> Ambradiol", CAT, "The lactone reduced to the diol.", wiki=P["Ambradiol"],
      cat="Ru", T=150),
    R("Ambroxide", "Ambradiol -> Ambroxide + H2O", CAT, "The diol closed into a cyclic ether in acid.", wiki=P["Ambroxide"],
      cat="H2SO4", T=60),
    R("Nectaryl", "Limonene + Cyclopentanone -> Nectaryl", HEAT,
      "Cyclopentanone added across limonene's ring-outer double bond by a peroxide-started radical chain.",
      wiki=P["Nectaryl"], T=150),
    R("Dipropylenetriamine", "2 Acrylonitrile + NH3 + 4 H2 -> DPTA", CAT,
      "Ammonia adds to two acrylonitriles; the dinitrile is hydrogenated.", wiki=P["DPTA"], cat="Ni", T=100),
    R("TBD", "DPTA + CS2 -> TBD + 2 H2S", HEAT, "Dipropylenetriamine ring-closed twice on carbon disulfide.",
      wiki=P["TBD"], T=170),
    R("Trichloroacetyl Chloride", "AcetylChloride + 3 Cl2 -> TCAC + 3 HCl", LIGHT, "Acetyl chloride chlorinated in light.",
      wiki=P["TCAC"], T=80),
    R("Trichloropyridinol", "TCAC + Acrylonitrile -> TCP + HCl", CAT,
      "Trichloroacetyl chloride adds to acrylonitrile; the adduct closes into a ring and loses hydrogen chloride.",
      wiki=P["TCP"], cat="CuCl", T=150),
    R("Trimethyladipic Acid", "TMCHol + 2 HNO3 -> TMAA + N2O + 2 H2O", FLASK,
      "Trimethylcyclohexanol cut open by nitric acid.", wiki=P["TMAA"], T=70),
    R("Trimethyladiponitrile", "TMAA + 2 NH3 -> TMADN + 4 H2O", HEAT, "The diacid dehydrated with ammonia to the dinitrile.",
      wiki=P["TMADN"], T=300),
    R("Trimethylhexamethylenediamine", "TMADN + 4 H2 -> TMD", CAT, "Both nitriles hydrogenated.", wiki=P["TMD"],
      cat="Ni", T=110),
    R("Benzanthrone", "Anthraquinone + Glycerol + H2 -> Benzanthrone + 4 H2O", FLASK,
      "Anthraquinone reduced by iron in sulfuric acid while glycerol, turning to acrolein, builds the extra ring.",
      wiki=P["Benzanthrone"], T=120),
    R("Violanthrone", "2 Benzanthrone + O2 -> Violanthrone + 2 H2O", CAT,
      "Two benzanthrones fused in molten potash; air oxidises the leuco form to the dye.", wiki=P["Violanthrone"],
      cat="KOH", T=230),
    R("Dihydroxyviolanthrone", "Violanthrone + O2 -> DHV", FLASK,
      "Oxidised with manganese dioxide in sulfuric acid and reduced back to the diol.", wiki=P["DHV"], T=40),
    R("Jade Green", "DHV + DimethylSulfate + 2 NaOH -> JadeGreen + Na2SO4 + 2 H2O", FLASK,
      "Both hydroxyls methylated with dimethyl sulfate.", wiki=P["JadeGreen"], T=150),
    R("Pyrenetetrasulfonic Acid", "Pyrene + 4 SO3 -> PTSA4", FLASK, "Pyrene sulfonated in oleum.", wiki=P["PTSA4"], T=60),
    R("Pyranine", "PTSA4 + 5 NaOH -> Pyranine + Na2SO3 + 4 H2O", HEAT,
      "One sulfonate swapped for a hydroxyl by hot caustic soda.", wiki=P["Pyranine"], T=100),
    R("Mesityl Oxide", "2 Acetone -> MesitylOxide + H2O", FLASK,
      "Acetone's aldol condensation (to diacetone alcohol), dehydrated in acid.", wiki=P["MesitylOxide"], T=120),
    R("Trimethylcyclohexenyl Methyl Ketone", "Piperylene + MesitylOxide -> TMCHAc", CAT,
      "A Lewis-acid Diels-Alder reaction.", wiki=P["TMCHAc"], cat="AlCl3", T=20),
    R("δ-Damascone", "TMCHAc + Acetaldehyde -> DeltaDamascone + H2O", FLASK,
      "An aldol condensation with acetaldehyde extends the side chain.", wiki=P["DeltaDamascone"], T=0),
    R("Monosodium Cyanurate", "CyanuricAcid + NaOH -> NaCyanurate + H2O", MIX, "Cyanuric acid half-neutralised.",
      wiki=P["NaCyanurate"]),
    R("Potassium Pentaborate", "5 H3BO3 + KOH -> KPentaborate + 8 H2O", HEAT, "Boric acid and potash crystallised together.",
      wiki=P["KPentaborate"], T=90),
    R("Biphenylylcarbonylbenzoic Acid", "Biphenyl + PhthalicAnhydride -> BBBA", CAT, "A Friedel-Crafts acylation.",
      wiki=P["BBBA"], cat="AlCl3", T=50),
    R("Oleyl Hydroxyethyl Imidazoline", "OleicAcid + AEEA -> OleylHEI + 2 H2O", HEAT,
      "The amide formed, then ring-closed with the loss of a second water under vacuum.", wiki=P["OleylHEI"], T=230),
    R("2-Hydroxy-1-naphthaldehyde", "Naphthol2 + CHCl3 + 3 NaOH -> HNA + 3 NaCl + 2 H2O", FLASK,
      "The Reimer-Tiemann reaction: dichlorocarbene from chloroform attacks the naphthoxide.", wiki=P["HNA"], T=70),
    R("Pigment Yellow 101", "2 HNA + N2H4 -> PY101 + 2 H2O", MIX, "Two aldehydes condensed onto one hydrazine.",
      wiki=P["PY101"]),
    R("Naphthol AS-D", "BONAcid + oToluidine -> NaphtholASD + H2O", HEAT,
      "BON acid condensed with o-toluidine (phosphorus trichloride in industry).", wiki=P["NaphtholASD"], T=130),
    R("2,4,5-Trichloroaniline", "TCB124 + HNO3 + 3 H2 -> TCA245 + 3 H2O", CAT, "Nitrated, then the nitro group hydrogenated.",
      wiki=P["TCA245"], cat="Pd", T=80),
    R("Pigment Red 112", "TCA245 + NaNO2 + HCl + NaphtholASD -> PR112 + NaCl + 2 H2O", COOL,
      "Diazotised trichloroaniline coupled to Naphthol AS-D.", wiki=P["PR112"], T=5),
    R("Calcium Tetraborate", "CaO + 2 B2O3 -> CaB4O7", SMELT, "Lime and boron oxide fused.", wiki=P["CaB4O7"], T=1000),
    R("Strontium Hydrogen Phosphate", "SrO + H3PO4 -> SrHPO4 + H2O", MIX, "Strontia neutralised by phosphoric acid.",
      wiki=P["SrHPO4"]),
    R("Cerium Molybdate", "Ce2CO33 + 3 MoO3 -> CeMolybdate + 3 CO2", HEAT, "Cerium carbonate fired with molybdenum trioxide.",
      wiki=P["CeMolybdate"], T=700),
    R("Tri-sec-butylborane", "3 NaBH4 + 4 BF3 + 12 2-Butene -> 4 TSBB + 3 NaBF4", FLASK,
      "Diborane, released from borohydride by boron trifluoride, adds to 2-butene (hydroboration).", wiki=P["TSBB"], T=25),
    R("3-Chloropropionyl Chloride", "AcrylicAcid + SOCl2 -> CPC3 + SO2", FLASK,
      "Acrylic acid on thionyl chloride; the hydrogen chloride released adds across the double bond.", wiki=P["CPC3"], T=60),
    R("5-Chloro-1-indanone", "Chlorobenzene + CPC3 -> ClIndanone + 2 HCl", CAT,
      "Friedel-Crafts acylation, then ring closure in hot sulfuric acid.", wiki=P["ClIndanone"], cat="AlCl3", T=90),
    R("Chromium Nitride", "4 Cr + N2 -> 2 Cr2N", ARC, "Chromium heated in nitrogen.", wiki=P["Cr2N"], T=1200),
    R("Methyl Dodecyl Sulfide", "Dodecene + Methanethiol -> MeSDodecane", LIGHT,
      "Methanethiol added to dodecene by a light-started radical chain.", wiki=P["MeSDodecane"]),
    R("DETA Trihydrochloride", "DETA + 3 HCl -> DETA3HCl", MIX, "All three amines protonated.", wiki=P["DETA3HCl"]),
    R("Tetraethylurea", "COCl2 + 2 Diethylamine + 2 NaOH -> TEU + 2 NaCl + 2 H2O", FLASK,
      "Phosgene on diethylamine.", wiki=P["TEU"], T=20),
    R("Hexaethylguanidinium Chloride", "TEU + COCl2 + Diethylamine + NaOH -> HEGCl + CO2 + NaCl + H2O", FLASK,
      "Phosgene turns the urea into a chloroformamidinium salt, and diethylamine completes the guanidinium.",
      wiki=P["HEGCl"], T=60),
    R("Methyl p-Toluate", "pToluic + Methanol -> MeToluate + H2O", CAT, "p-Toluic acid esterified.", wiki=P["MeToluate"],
      cat="H2SO4", T=150),
    R("Methyl 4-Methylcyclohexanecarboxylate", "MeToluate + 3 H2 -> MeMCHC", CAT, "The aromatic ring hydrogenated.",
      wiki=P["MeMCHC"], cat="Ru", T=120),
    R("Pigment Green 36", "CuPc + Br2 + Cl2 -> PG36", HEAT,
      "Copper phthalocyanine halogenated in a molten aluminium chloride salt bath.", wiki=P["PG36"], exact=False, T=180),
]

# the apothecaries' herbs (iodine milestone) now include clary sage
import authored_content as _C  # noqa: E402
from gen_authored import Milestone  # noqa: E402
for _m in _C.MILESTONES:
    if _m.on == "I2":
        _m.grant = tuple(_m.grant) + ("ClarySage",)

_C.MILESTONES += [
    Milestone("Tartrazine", message="Tartrazine (1884): a coal-tar yellow that became the most familiar food colour in the world."),
    Milestone("Ambroxide", message="Ambrox (Firmenich, 1950): the scent of ambergris, which sperm whales make, rebuilt from a herb."),
]
