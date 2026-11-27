"""
Curieosity's industrial chemistry, part 31 (see authored_canon.py): the last of the canon records
that can be honestly made from what the game has. Brilliant Blue FCF (E133) and Rhodamine B,
Pigment Orange 34, Tinuvin 234, the alkyl ketene dimers that size paper, a biomass route from
hydroxymethylfurfural to 2,5-hexanediol, patchouli oil, and the classes urea-formaldehyde resin,
vinyl-acrylic latex, Selexol and bismuth subnitrate.
"""

from authored_canon import S, R, CANON  # noqa: F401
from authored_content import E3, E4, E5, E6, X, RAW  # noqa: F401
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


# the same products as substances already in the game
CANON.update({"215247-95-3": "PV23", "1326-83-6": "SulphurBlack", "35657-77-3": "DTPMP"})

# --- intermediates ------------------------------------------------------------------------------
PC("1008-72-6", "BSA2Na", "Sodium benzaldehyde-2-sulfonate", "C7H5NaO4S", "Solid", "Sodium 2-formylbenzenesulfonate",
   "The aldehyde of the triarylmethane food blues.", "[Na+].O=Cc1ccccc1S([O-])(=O)=O")
PC("103-69-5", "NEthylaniline", "N-Ethylaniline", "C8H11N", "Liquid", "N-Ethylaniline", "Aniline ethylated once.", "CCNc1ccccc1")
PC("101-11-1", "EBASA", "N-Ethyl-N-(3-sulfobenzyl)aniline", "C15H17NO3S", "Solid", "N-Ethyl-N-benzylaniline-3'-sulfonic acid",
   "The amine half of Brilliant Blue FCF.", "CCN(Cc1cccc(c1)S(O)(=O)=O)c1ccccc1")
PC("622-07-3", "TolylHydrazine", "p-Tolylhydrazine", "C7H10N2", "Solid", "4-Methylphenylhydrazine",
   "p-Toluidine diazotised and reduced.", "Cc1ccc(NN)cc1")
PC("86-89-5", "PTMP", "3-Methyl-1-(p-tolyl)-5-pyrazolone", "C11H12N2O", "Solid", "3-Methyl-1-(p-tolyl)-5-pyrazolone",
   "The coupling component of Pigment Orange 34.", "Cc1ccc(cc1)N1N=C(C)CC1=O")
PC("2772-45-4", "DicumylPhenol", "2,4-Dicumylphenol", "C24H26O", "Solid", "2,4-Bis(alpha,alpha-dimethylbenzyl)phenol",
   "Phenol alkylated twice with alpha-methylstyrene.", "CC(C)(c1ccccc1)c1ccc(O)c(c1)C(C)(C)c1ccccc1")
WK("110-13-4", "Hexanedione25", "2,5-Hexanedione", "C6H10O2", "Liquid", "Hexane-2,5-dione",
   "Acetonylacetone: dimethylfuran hydrolysed open. It is the metabolite through which hexane damages nerves.", "CC(=O)CCC(C)=O")
PC("97-61-0", "MePentanoicAcid", "2-Methylpentanoic acid", "C6H12O2", "Liquid", "2-Methylpentanoic acid",
   "From propanal: aldol condensation, hydrogenation and oxidation.", "CCCC(C)C(O)=O")
PC("141-75-3", "ButyrylCl", "Butyryl chloride", "C4H7ClO", "Liquid", "Butyryl chloride", "Butyric acid's acid chloride.", "CCCC(Cl)=O")
RAW("Patchouli", "Patchouli Leaves", "Dried leaves of Pogostemon cablin from Indonesia; the oil grows richer as it ages.",
    "Patchouli", color="#4a5a2a")

# --- the records -------------------------------------------------------------------------------
WK("3844-45-9", "BrilliantBlue", "Brilliant Blue FCF", "C37H34N2Na2O9S3", "Solid", "Brilliant_Blue_FCF",
   "FD&C Blue 1 (E133): the blue of sports drinks, sweets and mouthwash, and with tartrazine, the green of mint ice cream.",
   "[Na+].[Na+].CCN(Cc1cccc(c1)S([O-])(=O)=O)c1ccc(cc1)C(=C1C=CC(C=C1)=[N+](CC)Cc1cccc(c1)S([O-])(=O)=O)c1ccccc1S([O-])(=O)=O")
WK("81-88-9", "RhodamineB", "Rhodamine B", "C28H31ClN2O3", "Solid", "Rhodamine_B",
   "A brilliant pink fluorescent dye: a tracer that shows where water flows, and a laser and microscope dye.",
   "[Cl-].CCN(CC)c1ccc2c(c1)oc1cc(=[N+](CC)CC)ccc1=c2-c1ccccc1C(O)=O")
PC("15793-73-4", "PO34", "Pigment Orange 34", "C34H28Cl2N8O2", "Solid", 85908,
   "Diarylide pyrazolone orange, for packaging inks and plastics.",
   "CC1=NN(c2ccc(C)cc2)C(=O)C1N=Nc1ccc(cc1Cl)-c1ccc(N=NC2C(C)=NN(c3ccc(C)cc3)C2=O)c(Cl)c1")
PC("70693-50-4", "T234Azo", "Tinuvin 234 azo intermediate", "C30H29N3O3", "Solid", 116810,
   "Diazotised o-nitroaniline coupled to dicumylphenol, ready to be reduced shut.",
   "CC(C)(c1ccccc1)c1cc(N=Nc2ccccc2[N+]([O-])=O)c(O)c(c1)C(C)(C)c1ccccc1")
PC("70321-86-7", "Tinuvin234", "Tinuvin 234", "C30H29N3O", "Solid", "UV-234",
   "A benzotriazole UV absorber that survives the heat of polycarbonate and polyester moulding.",
   "CC(C)(c1ccccc1)c1cc(c(O)c(c1)C(C)(C)c1ccccc1)-n1nc2ccccc2n1")
PC("2202-98-4", "DEGPhthalate", "Diethylene glycol phthalate", "C12H14O6", "Solid", 75149,
   "Phthalic anhydride opened by diethylene glycol: the start of the polyester polyols of rigid foam.",
   "OCCOCCOC(=O)c1ccccc1C(O)=O")
PC("35835-94-0", "ETPPAc", "Ethyltriphenylphosphonium acetate", "C22H23O2P", "Solid", 94470,
   "The catalyst that grows liquid epoxy resin into the solid grades of powder coatings.",
   "CC([O-])=O.CC[P+](c1ccccc1)(c1ccccc1)c1ccccc1")
PC("2469-45-6", "DodecylSulfide", "Didodecyl sulfide", "C24H50S", "Solid", 72875,
   "A sulfur antioxidant that breaks down peroxides in plastics.", "CCCCCCCCCCCCSCCCCCCCCCCCC")
PC("2935-44-6", "Hexanediol25", "2,5-Hexanediol", "C6H14O2", "Liquid", 18049, "A diol for polyesters and fragrances.",
   "CC(O)CCC(C)O")
PC("39255-32-8", "EtMePentanoate", "Ethyl 2-methylpentanoate", "C8H16O2", "Liquid", 62902,
   "Manzanate: a crisp green-apple fruit ester.", "CCCC(C)C(=O)OCC")
PC("335-42-2", "HFBF", "Heptafluorobutyryl fluoride", "C4F8O", "Gas", 67632,
   "Butyryl chloride electrochemically fluorinated; it hydrolyses to perfluorobutyric acid.", "O=C(F)C(F)(F)C(F)(F)C(F)(F)F")
FAMILY("AKD", "Alkyl ketene dimer", "C36H68O2", "Solid", "Alkyl_ketene_dimer",
       "A wax that reacts with paper's cellulose so that ink and water stop soaking in: the sizing of milk cartons and printing paper. "
       "Shown as the stearic acid dimer.", ["83708-14-9"], smiles="CCCCCCCCCCCCCCCCC=C1OC(=O)C1CCCCCCCCCCCCCCCC")
FAMILY("UFResin", "Urea-formaldehyde resin", "mixture", "Solid", "Urea-formaldehyde",
       "The glue of particleboard and MDF: cheap and strong, though it gives off traces of formaldehyde.", ["68611-64-3"],
       props=("IsPolymer", "IsClass"))
FAMILY("VinylAcrylic", "Vinyl-acrylic latex", "mixture", "Aqueous", pubchem("Vinyl acetate-butyl acrylate copolymer"),
       "Vinyl acetate copolymerised with butyl acrylate in water: the binder of most interior emulsion paints.",
       ["26428-41-1"], props=("IsPolymer", "IsClass"))
FAMILY("Selexol", "Polyethylene glycol dimethyl ether", "mixture", "Liquid", "Selexol",
       "Selexol: a solvent that scrubs carbon dioxide and hydrogen sulfide out of natural gas and synthesis gas.",
       ["111109-77-4"])
FAMILY("BiSubnitrate", "Bismuth subnitrate", "mixture", "Solid", "Bismuth_subnitrate",
       "A basic bismuth nitrate of variable make-up: an old remedy for stomach upsets, and a pearl pigment.", ["1304-85-4"],
       props=("IsMedicine", "IsClass"))
FAMILY("PatchouliOil", "Patchouli oil", "mixture", "Liquid", "Patchouli",
       "The earthy, woody essential oil that fixes perfumes: steam-distilled from dried patchouli leaves.", ["8014-09-3"])

# --- the reactions -------------------------------------------------------------------------------
E5.reactions += [
    R("Sodium Benzaldehyde-2-sulfonate", "ClBenzaldehyde2 + Na2SO3 -> BSA2Na + NaCl", HEAT,
      "Sulfite displaces the chlorine under pressure with a copper catalyst.", wiki=P["BSA2Na"], T=170),
    R("N-Ethylaniline", "Aniline + Acetaldehyde + H2 -> NEthylaniline + H2O", CAT,
      "Aniline reductively aminated with acetaldehyde: the imine hydrogenated as it forms.", wiki=P["NEthylaniline"], cat="Ni", T=80),
    R("Ethylbenzylanilinesulfonic Acid", "NEthylaniline + BenzylChloride + SO3 -> EBASA + HCl", FLASK,
      "N-Ethylaniline benzylated, then the benzyl ring sulfonated.", wiki=P["EBASA"], T=40),
    R("Brilliant Blue FCF", "2 BSA2Na + 4 EBASA + O2 + 2 NaOH -> 2 BrilliantBlue + 6 H2O", FLASK,
      "The aldehyde condensed with two of the amine into the colourless leuco base, then oxidised to the blue dye.",
      wiki=P["BrilliantBlue"], T=90),
    R("Rhodamine B", "2 DEAP + PhthalicAnhydride + HCl -> RhodamineB + 2 H2O", HEAT,
      "Two diethylaminophenols condensed with phthalic anhydride into the xanthene dye.", wiki=P["RhodamineB"], T=180),
    R("p-Tolylhydrazine", "pToluidine + NaNO2 + HCl + 2 H2 -> TolylHydrazine + NaCl + 2 H2O", FLASK,
      "p-Toluidine diazotised and the diazonium reduced (with sulfite) to the hydrazine.", wiki=P["TolylHydrazine"], T=10),
    R("Tolylmethylpyrazolone", "TolylHydrazine + EthylAcetoacetate -> PTMP + Ethanol + H2O", FLASK,
      "The hydrazine closes a pyrazolone ring on ethyl acetoacetate.", wiki=P["PTMP"], T=100),
    R("Pigment Orange 34", "DCB + 2 NaNO2 + 2 HCl + 2 PTMP -> PO34 + 2 NaCl + 4 H2O", COOL,
      "Dichlorobenzidine diazotised and coupled to two pyrazolones.", wiki=P["PO34"], T=5),
    R("2,4-Dicumylphenol", "Phenol + 2 AMS -> DicumylPhenol", CAT, "Phenol alkylated twice with alpha-methylstyrene.",
      wiki=P["DicumylPhenol"], cat="H2SO4", T=100),
    R("Tinuvin 234 Azo Dye", "oNitroaniline + NaNO2 + HCl + DicumylPhenol -> T234Azo + NaCl + 2 H2O", COOL,
      "Diazotised o-nitroaniline coupled to dicumylphenol.", wiki=P["T234Azo"], T=5),
    R("Tinuvin 234", "T234Azo + 2 H2 -> Tinuvin234 + 2 H2O", CAT,
      "The nitro azo compound reduced until it closes into a benzotriazole.", wiki=P["Tinuvin234"], cat="Pd", T=60),
    R("DEG Phthalate", "PhthalicAnhydride + DEG -> DEGPhthalate", MIX, "Diethylene glycol opens the anhydride ring.",
      wiki=P["DEGPhthalate"]),
    R("Ethyltriphenylphosphonium Acetate", "ETPPBr + NaC2H3O2 -> ETPPAc + NaBr", MIX, "The bromide swapped for acetate.",
      wiki=P["ETPPAc"]),
    R("Didodecyl Sulfide", "2 Dodecene + H2S -> DodecylSulfide", LIGHT,
      "Hydrogen sulfide added to two dodecenes by a light-started radical chain.", wiki=P["DodecylSulfide"]),
    R("2,5-Hexanedione", "DMF25 + H2O -> Hexanedione25", FLASK, "Dimethylfuran hydrolysed open in acid.", wiki=P["Hexanedione25"], T=150),
    R("2,5-Hexanediol", "Hexanedione25 + 2 H2 -> Hexanediol25", CAT, "Both ketones hydrogenated.", wiki=P["Hexanediol25"], cat="Ni", T=100),
    R("2-Methylpentanoic Acid", "4 Propanal + 2 H2 + O2 -> 2 MePentanoicAcid + 2 H2O", CAT,
      "Propanal self-condensed to 2-methylpentenal, hydrogenated to the saturated aldehyde, and oxidised by air.",
      wiki=P["MePentanoicAcid"], cat="Ni", T=100),
    R("Ethyl 2-Methylpentanoate", "MePentanoicAcid + Ethanol -> EtMePentanoate + H2O", CAT, "The acid esterified with ethanol.",
      wiki=P["EtMePentanoate"], cat="H2SO4", T=90),
    R("Butyryl Chloride", "3 Butyric + PCl3 -> 3 ButyrylCl + H3PO3", FLASK, "Butyric acid on phosphorus trichloride.",
      wiki=P["ButyrylCl"], T=50),
    R("Heptafluorobutyryl Fluoride", "ButyrylCl + 8 HF -> HFBF + HCl + 7 H2", ECELL,
      "Electrochemical fluorination of butyryl chloride.", wiki=P["HFBF"], T=10),
    R("Alkyl Ketene Dimer", "2 StearoylCl + Et3N -> AKD + 2 HCl + Et3N", HEAT,
      "Triethylamine pulls hydrogen chloride from the acid chloride; the ketene formed dimerises.", wiki=P["AKD"], T=60),
    R("Urea-Formaldehyde Resin", "Urea + CH2O -> UFResin", POLY,
      "Urea methylolated with formaldehyde in alkali, then condensed in acid.", wiki=P["UFResin"], exact=False, T=90),
    R("Vinyl-Acrylic Latex", "VinylAcetate + ButylAcrylate -> VinylAcrylic", POLY,
      "Vinyl acetate and butyl acrylate emulsion-polymerised in water.", wiki=P["VinylAcrylic"], exact=False, T=75),
    R("Selexol", "PEG + CH3Cl + NaOH -> Selexol", FLASK,
      "Polyethylene glycol's end hydroxyls methylated (a Williamson synthesis).", wiki=P["Selexol"], exact=False, T=100),
    R("Bismuth Subnitrate", "Bi2O3 + HNO3 + H2O -> BiSubnitrate", MIX,
      "Bismuth nitrate hydrolysed in water: the basic salt precipitates.", wiki=P["BiSubnitrate"], exact=False),
    R("Patchouli Oil", "Patchouli + H2O -> PatchouliOil", DISTIL, "Dried patchouli leaves steam-distilled.", wiki=P["PatchouliOil"],
      exact=False),
]

# the apothecaries' herbs (iodine milestone) now include patchouli
import authored_content as _C  # noqa: E402
from gen_authored import Milestone  # noqa: E402
for _m in _C.MILESTONES:
    if _m.on == "I2":
        _m.grant = tuple(_m.grant) + ("Patchouli",)

# Milestones for the stretches parts 30 and 31 lengthened (messages only).
_C.MILESTONES += [
    Milestone("PV23", message="Carbazole dioxazine violet: so strong that a pinch tints a can of paint, and the base of nearly every purple you see."),
]
import authored_canon_32  # noqa: E402,F401
