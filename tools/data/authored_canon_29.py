"""
Curieosity's industrial chemistry, part 29 (see authored_canon.py): more literature routes for
canon compounds that had none. Avobenzone by a Claisen condensation, maltol and ethyl maltol by
the Achmatowicz ring expansion, EPDM rubber, the Nafion-chain fluorosulfonyl acetyl fluoride,
HFC-236fa, two more benzotriazole UV absorbers, Metanil Yellow and Pigment Red 178, and the
fragrance alcohols Sandalore, Sandela and 2-pinanol.
"""

from authored_canon import S, R, CANON  # noqa: F401
from authored_content import E3, E4, E5, E6, X  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR, pubchem)

P = {}


def PC(cas, key, name, formula, state, ref, desc, smiles=None, props=()):
    """A compound whose page is on PubChem (by CID, or by name)."""
    P[key] = pubchem(ref)
    S(cas, key, name, formula, state, P[key], desc, smiles=smiles, props=props)


def WK(cas, key, name, formula, state, title, desc, smiles=None, props=()):
    """A compound with a Wikipedia article."""
    P[key] = title
    S(cas, key, name, formula, state, title, desc, smiles=smiles, props=props)


# --- intermediates ------------------------------------------------------------------------------
CANON["75-00-3"] = "EtCl"  # chloroethane is in the game already
WK("140-88-5", "EthylAcrylate", "Ethyl acrylate", "C5H8O2", "Liquid", "Ethyl_acrylate",
   "An acrylate monomer for the soft, tacky polymers of paints, textiles and pressure-sensitive adhesives.", "CCOC(=O)C=C")
WK("115-10-6", "DME", "Dimethyl ether", "C2H6O", "Gas", "Dimethyl_ether",
   "The simplest ether: an aerosol propellant, and a clean diesel fuel made from methanol.", "COC")
WK("98-06-6", "tBuBenzene", "tert-Butylbenzene", "C10H14", "Liquid", "Tert-Butylbenzene",
   "Benzene alkylated with isobutylene.", "CC(C)(C)c1ccccc1")
PC("943-27-1", "tBuAcetophenone", "4-tert-Butylacetophenone", "C12H16O", "Liquid", "4'-tert-Butylacetophenone",
   "The ketone half of avobenzone.", "CC(=O)c1ccc(cc1)C(C)(C)C")
WK("100-09-4", "AnisicAcid", "p-Anisic acid", "C8H8O3", "Solid", "P-Anisic_acid",
   "Anisaldehyde oxidised; an antiseptic and the ester half of avobenzone.", "COc1ccc(cc1)C(O)=O")
PC("121-98-2", "MethylAnisate", "Methyl 4-methoxybenzoate", "C9H10O3", "Liquid", "Methyl 4-methoxybenzoate",
   "Anisic acid's methyl ester, with a sweet anise smell.", "COC(=O)c1ccc(OC)cc1")
PC("4208-64-4", "FurylEthanol", "1-(2-Furyl)ethanol", "C6H8O2", "Liquid", "1-(2-Furyl)ethanol",
   "Furfural with a methyl Grignard added: the furan that the Achmatowicz reaction expands into maltol.", "CC(O)c1ccco1")
PC("2386-64-3", "EtMgCl", "Ethylmagnesium chloride", "C2H5ClMg", "Liquid", "Ethylmagnesium chloride",
   "A Grignard reagent: magnesium put between carbon and chlorine.", "CC[Mg]Cl")
PC("4208-61-1", "FurylPropanol", "1-(2-Furyl)propan-1-ol", "C7H10O2", "Liquid", "1-(2-Furyl)-1-propanol",
   "Furfural with an ethyl Grignard added.", "CCC(O)c1ccco1")
PC("150-19-6", "MethoxyPhenol3", "3-Methoxyphenol", "C7H8O2", "Liquid", "3-Methoxyphenol",
   "Resorcinol methylated once.", "COc1cccc(O)c1")
WK("60-09-3", "AminoAzobenzene", "4-Aminoazobenzene", "C12H11N3", "Solid", "Aniline_Yellow",
   "Aniline Yellow (1861), the first azo dye.", "Nc1ccc(cc1)N=Nc1ccccc1")
WK("10049-07-7", "RhCl3", "Rhodium(III) chloride", "Cl3Rh", "Solid", "Rhodium(III)_chloride",
   "The starting point of rhodium catalysts.")
PC("3607-78-1", "HCC230fa", "1,1,1,3,3,3-Hexachloropropane", "C3H2Cl6", "Liquid", "1,1,1,3,3,3-Hexachloropropane",
   "Carbon tetrachloride added to vinylidene chloride: fluorinated, it becomes HFC-236fa.", "ClC(Cl)(Cl)CC(Cl)(Cl)Cl")
PC("88-15-3", "AcetylThiophene", "2-Acetylthiophene", "C6H6OS", "Liquid", "2-Acetylthiophene",
   "Thiophene acetylated.", "CC(=O)c1cccs1")

# --- the canon compounds -------------------------------------------------------------------------
PC("70356-09-1", "Avobenzone", "Avobenzone", "C20H22O3", "Solid", 51040,
   "The main UVA filter of sunscreens: its enol form soaks up the long ultraviolet that ages skin.",
   "COc1ccc(cc1)C(=O)CC(=O)c1ccc(cc1)C(C)(C)C")
WK("118-71-8", "Maltol", "Maltol", "C6H6O3", "Solid", "Maltol",
   "A caramel-sweet flavour enhancer, found in larch bark and roasted malt.", "CC1=C(O)C(=O)C=CO1")
WK("4940-11-8", "EthylMaltol", "Ethyl maltol", "C7H8O3", "Solid", "Ethyl_maltol",
   "Four to six times as sweet-smelling as maltol: the candyfloss note of sweets and perfumes.", "CCC1=C(O)C(=O)C=CO1")
PC("94-91-7", "Salpn", "N,N'-Disalicylidene-1,2-propanediamine", "C17H18N2O2", "Solid", 7210,
   "A metal deactivator: it locks up the copper that would speed fuels and oils into gum.",
   "CC(CN=Cc1ccccc1O)N=Cc1ccccc1O")
PC("56831-62-0", "TridecylPhosphate", "Tridecyl phosphate", "C13H29O4P", "Liquid", 92542,
   "An anionic surfactant and lubricity additive.", "CCCCCCCCCCCCCOP(O)(O)=O")
PC("104-21-2", "AnisylAcetate", "Anisyl acetate", "C10H12O3", "Liquid", 7695,
   "A sweet, fruity-floral ester for perfumes and flavours.", "COc1ccc(COC(C)=O)cc1")
PC("65113-99-7", "Sandalore", "Sandalore", "C14H26O", "Liquid", 103212,
   "A synthetic sandalwood odourant; it also turns out to help skin cells heal.", "CC(O)C(C)CCC1CC=C(C)C1(C)C")
PC("43224-75-5", "AllylOxyTMP", "4-Allyloxy-2,2,6,6-tetramethylpiperidine", "C12H23NO", "Liquid", 11117001,
   "A hindered-amine light stabiliser that can be grafted into polymers.", "CC1(C)CC(OCC=C)CC(C)(C)N1")
PC("14350-97-1", "LauroAmphoDiacetate", "Disodium lauroamphodiacetate", "C20H36N2Na2O6", "Liquid", 162344872,
   "A very mild amphoteric surfactant for baby shampoos.", "[Na+].[Na+].CCCCCCCCCCCC(=O)NCCN(CCOCC([O-])=O)CC([O-])=O")
PC("587-98-4", "MetanilYellow", "Metanil Yellow", "C18H14N3NaO3S", "Solid", 87730678,
   "Acid Yellow 36: an azo dye for wool, paper and leather, and an indicator; banned as a food colour, though it is still found as a spice adulterant.",
   "[Na+].[O-]S(=O)(=O)c1cccc(c1)N=Nc1ccc(Nc2ccccc2)cc1")
PC("617-86-7", "Et3SiH", "Triethylsilane", "C6H16Si", "Liquid", 12052,
   "A mild hydride donor for reductions in organic synthesis.", "CC[SiH](CC)CC")
PC("354-32-5", "TFAC", "Trifluoroacetyl chloride", "C2ClF3O", "Gas", 61106,
   "A reagent that puts trifluoroacetyl groups on drugs and crop chemicals.", "FC(F)(F)C(Cl)=O")
PC("463-49-0", "Allene", "Allene", "C3H4", "Gas", 10037,
   "Propadiene: two double bonds on one carbon; with propyne, the MAPP welding gas.", "C=C=C")
PC("555-10-2", "bPhellandrene", "beta-Phellandrene", "C10H16", "Liquid", 11142,
   "A minty terpene of eucalyptus and water fennel oils.", "C=C1CCC(C=C1)C(C)C")
PC("527-72-0", "ThiopheneCA", "Thiophene-2-carboxylic acid", "C5H4O2S", "Solid", 10700,
   "A building block for drugs, such as the pain reliever suprofen.", "OC(=O)c1cccs1")
PC("3147-75-9", "UV329", "UV-329", "C20H25N3O", "Solid", 62485,
   "A benzotriazole UV absorber for clear plastics and coatings.", "CC(C)(C)CC(C)(C)c1ccc(O)c(c1)-n1nc2ccccc2n1")
PC("103597-45-1", "UV360", "UV-360", "C41H50N6O2", "Solid", 3571576,
   "Two benzotriazole UV absorbers joined: heavy enough not to evaporate from engineering plastics.",
   "CC(C)(C)CC(C)(C)c1cc(Cc2cc(cc(c2O)-n2nc3ccccc3n2)C(C)(C)CC(C)(C)C)c(O)c(c1)-n1nc2ccccc2n1")
PC("110-71-4", "Monoglyme", "1,2-Dimethoxyethane", "C4H10O2", "Liquid", 8071,
   "Glyme: a solvent that holds lithium and sodium ions, for batteries and Grignard chemistry.", "COCCOC")
PC("10139-58-9", "RhNO33", "Rhodium(III) nitrate", "N3O9Rh", "Solid", 150190,
   "The rhodium salt soaked into catalytic converters, where rhodium reduces nitrogen oxides.")
PC("131-53-3", "Dioxybenzone", "Dioxybenzone", "C14H12O4", "Solid", 8569,
   "Benzophenone-8, a UV filter for sunscreens.", "COc1ccc(C(=O)c2ccccc2O)c(O)c1")
PC("3049-71-6", "PR178", "Pigment Red 178", "C48H26N6O4", "Solid", 62476,
   "A perylene red for car paints and plastics, fast to light and heat.",
   "O=C1N(c2ccc(cc2)N=Nc2ccccc2)C(=O)c2ccc3c4ccc5C(=O)N(c6ccc(cc6)N=Nc6ccccc6)C(=O)c6ccc(c7ccc1c2c37)c4c56")
PC("3407-42-9", "Sandela", "Sandela", "C16H28O", "Liquid", 103005,
   "Isocamphyl cyclohexanol: a creamy sandalwood odourant from camphene and guaiacol.", "OC1CCCC(C1)C2CC3CC2C(C)C3(C)C")
PC("473-54-1", "Pinanol2", "2-Pinanol", "C10H18O", "Solid", 10128,
   "Made from pinene by way of pinane hydroperoxide; heated, its ring opens to linalool.", "CC1(O)CCC2CC1C2(C)C")
PC("677-67-8", "FSAF", "Fluorosulfonyldifluoroacetyl fluoride", "C2F4O3S", "Liquid", 69614,
   "Tetrafluoroethylene and sulfur trioxide, rearranged: the start of the sulfonyl vinyl ether of Nafion membranes.",
   "O=C(F)C(F)(F)S(=O)(=O)F")
PC("690-39-1", "HFC236fa", "HFC-236fa", "C3H2F6", "Gas", 12722,
   "A fire suppressant for occupied rooms and aircraft, and a refrigerant.", "FC(F)(F)CC(F)(F)F")
PC("335-36-4", "FC75", "Perfluoro-2-butyltetrahydrofuran", "C8F16O", "Liquid", 78976,
   "FC-75: an inert, dense coolant in which electronics can sit fully immersed.", "FC(F)(F)C(F)(F)C(F)(F)C(F)(F)C1(F)OC(F)(F)C(F)(F)C1(F)F")
PC("589-34-4", "MeHexane3", "3-Methylhexane", "C7H16", "Liquid", 11507,
   "A branched heptane: isomerising straight heptane raises petrol's octane number.", "CCCC(C)CC")

P["EPDM"] = "EPDM_rubber"
X("EPDM", "EPDM rubber", "(C15H22)n", "Solid",
  "Ethylene-propylene-diene rubber: it shrugs off ozone and weather, for car door seals, roofing membranes and radiator hoses.",
  P["EPDM"], id=0, balance="C15H22", props=("IsPolymer",))
CANON["25034-71-3"] = "EPDM"

# --- the reactions -------------------------------------------------------------------------------
E5.reactions += [
    R("Ethyl Acrylate", "AcrylicAcid + Ethanol -> EthylAcrylate + H2O", CAT,
      "Acrylic acid esterified with ethanol.", wiki=P["EthylAcrylate"], cat="H2SO4", T=90),
    R("Dimethyl Ether", "2 Methanol -> DME + H2O", COOL,
      "Methanol dehydrated over acid alumina; the ether is condensed out cold.", wiki=P["DME"], T=-30),
    R("tert-Butylbenzene", "Benzene + Isobutylene -> tBuBenzene", CAT, "Benzene alkylated with isobutylene.", wiki=P["tBuBenzene"],
      cat="H2SO4", T=20),
    R("4-tert-Butylacetophenone", "tBuBenzene + AcetylChloride -> tBuAcetophenone + HCl", FLASK,
      "tert-Butylbenzene acetylated by Friedel-Crafts, para to the bulky group.", wiki=P["tBuAcetophenone"], T=20),
    R("Anisic Acid", "2 Anisaldehyde + O2 -> 2 AnisicAcid", MIX, "Anisaldehyde oxidised by air.", wiki=P["AnisicAcid"]),
    R("Methyl Anisate", "AnisicAcid + Methanol -> MethylAnisate + H2O", CAT, "Anisic acid esterified.", wiki=P["MethylAnisate"],
      cat="H2SO4", T=70),
    R("Avobenzone", "tBuAcetophenone + MethylAnisate -> Avobenzone + Methanol", FLASK,
      "A Claisen condensation with sodium methoxide joins the ketone to the ester as a 1,3-diketone.", wiki=P["Avobenzone"], T=100),
    R("1-(2-Furyl)ethanol", "Furfural + MeMgCl + HCl -> FurylEthanol + MgCl2", FLASK,
      "Methylmagnesium chloride added to furfural.", wiki=P["FurylEthanol"], T=0),
    R("Maltol", "FurylEthanol + 2 Cl2 + H2O -> Maltol + 4 HCl", COOL,
      "The Achmatowicz reaction: chlorine opens the furan and closes a six-membered pyranone, then aromatises it.",
      wiki=P["Maltol"], T=-10),
    R("Ethylmagnesium Chloride", "EtCl + Mg -> EtMgCl", FLASK, "Magnesium turnings in ether with ethyl chloride.", wiki=P["EtMgCl"], T=35),
    R("1-(2-Furyl)propanol", "Furfural + EtMgCl + HCl -> FurylPropanol + MgCl2", FLASK,
      "Ethylmagnesium chloride added to furfural.", wiki=P["FurylPropanol"], T=0),
    R("Ethyl Maltol", "FurylPropanol + 2 Cl2 + H2O -> EthylMaltol + 4 HCl", COOL,
      "The same ring expansion, one carbon longer.", wiki=P["EthylMaltol"], T=-10),
    R("Salpn", "2 Salicylaldehyde + DAP12 -> Salpn + 2 H2O", MIX,
      "Salicylaldehyde condensed onto both amines of 1,2-diaminopropane.", wiki=P["Salpn"]),
    R("Tridecyl Phosphate", "Tridecanol + H3PO4 -> TridecylPhosphate + H2O", HEAT, "Tridecanol phosphated.", wiki=P["TridecylPhosphate"],
      T=120),
    R("Anisyl Acetate", "Anisaldehyde + H2 + AceticAnhydride -> AnisylAcetate + AcOH", CAT,
      "Anisaldehyde hydrogenated to anisyl alcohol and acetylated.", wiki=P["AnisylAcetate"], cat="Ni", T=80),
    R("Sandalore", "CampholenicAldehyde + MEK + 2 H2 -> Sandalore + H2O", CAT,
      "Campholenic aldehyde condensed with butanone, then the ketone and the new double bond hydrogenated.",
      wiki=P["Sandalore"], cat="Ni", T=100),
    R("Allyloxy-TMP", "TMPol + AllylChloride + NaOH -> AllylOxyTMP + NaCl + H2O", FLASK,
      "The piperidinol's hydroxyl allylated.", wiki=P["AllylOxyTMP"], T=60),
    R("Disodium Lauroamphodiacetate", "LauricAcid + AEEA + 2 ClAcOH + 4 NaOH -> LauroAmphoDiacetate + 2 NaCl + 5 H2O", HEAT,
      "Lauric acid closed into an imidazoline with aminoethylethanolamine, then carboxymethylated twice.",
      wiki=P["LauroAmphoDiacetate"], T=180),
    R("Metanil Yellow", "Metanilic + NaNO2 + HCl + Diphenylamine + NaOH -> MetanilYellow + NaCl + 3 H2O", COOL,
      "Diazotised metanilic acid coupled to diphenylamine.", wiki=P["MetanilYellow"], T=5),
    R("Triethylsilane", "HSiCl3 + 3 EtCl + 3 Mg -> Et3SiH + 3 MgCl2", FLASK,
      "Trichlorosilane ethylated three times with a Grignard reagent made in the same pot.", wiki=P["Et3SiH"], T=40),
    R("Trifluoroacetyl Chloride", "TFA + PCl5 -> TFAC + POCl3 + HCl", FLASK,
      "Trifluoroacetic acid on phosphorus pentachloride.", wiki=P["TFAC"], T=40),
    R("Allene", "Propyne -> Allene", CAT,
      "Propyne and allene interconvert over a base; allene is drawn off as it forms.", wiki=P["Allene"], cat="Alumina", T=300),
    R("beta-Phellandrene", "Eucalyptus -> bPhellandrene", COLUMN,
      "Fractionated from the phellandrene-rich eucalyptus oils.", wiki=P["bPhellandrene"], exact=False),
    R("2-Acetylthiophene", "Thiophene + AceticAnhydride + H3PO4 -> AcetylThiophene + AcOH + H3PO4", FLASK,
      "Thiophene acetylated with phosphoric acid.", wiki=P["AcetylThiophene"], T=80),
    R("Thiophene-2-carboxylic Acid", "AcetylThiophene + 3 NaClO + HCl -> ThiopheneCA + CHCl3 + 2 NaOH + NaCl", FLASK,
      "The haloform reaction: hypochlorite cuts the acetyl group down to the acid.", wiki=P["ThiopheneCA"], T=40),
    R("UV-329", "oNitroaniline + NaNO2 + HCl + OctylPhenol + 2 H2 -> UV329 + NaCl + 4 H2O", FLASK,
      "Diazotised o-nitroaniline coupled to octylphenol, and the azo compound reduced shut into a benzotriazole.",
      wiki=P["UV329"], T=20),
    R("UV-360", "2 UV329 + CH2O -> UV360 + H2O", FLASK,
      "Two UV-329s bridged by formaldehyde (by way of a Mannich base).", wiki=P["UV360"], T=150),
    R("Monoglyme", "DME + EO -> Monoglyme", CAT,
      "Ethylene oxide inserted into dimethyl ether with boron trifluoride.", wiki=P["Monoglyme"], cat="BF3", T=60),
    R("Rhodium Chloride", "2 Rh + 3 Cl2 -> 2 RhCl3", HEAT, "Rhodium sponge chlorinated hot.", wiki=P["RhCl3"], T=400),
    R("Rhodium Nitrate", "RhCl3 + 3 NaOH + 3 HNO3 -> RhNO33 + 3 NaCl + 3 H2O", FLASK,
      "Rhodium hydroxide precipitated, washed free of chloride and dissolved in nitric acid.", wiki=P["RhNO33"], T=80),
    R("3-Methoxyphenol", "Resorcinol + Methanol -> MethoxyPhenol3 + H2O", CAT,
      "Resorcinol methylated once.", wiki=P["MethoxyPhenol3"], cat="H2SO4", T=150),
    R("Dioxybenzone", "MethoxyPhenol3 + Salicylic -> Dioxybenzone + H2O", FLASK,
      "3-Methoxyphenol acylated with salicylic acid by Friedel-Crafts.", wiki=P["Dioxybenzone"], T=120),
    R("Aniline Yellow", "2 Aniline + NaNO2 + HCl -> AminoAzobenzene + NaCl + 2 H2O", FLASK,
      "Half the aniline diazotised, and warmed in acid the diazoamino compound rearranges onto the other's ring.", wiki=P["AminoAzobenzene"], T=40),
    R("Pigment Red 178", "PTCDA + 2 AminoAzobenzene -> PR178 + 2 H2O", HEAT,
      "The perylene dianhydride condensed with aminoazobenzene.", wiki=P["PR178"], T=200),
    R("Sandela", "Camphene + Guaiacol + 4 H2 -> Sandela + Methanol", CAT,
      "Guaiacol alkylated with camphene, then hydrogenated until the ring and the methoxy group are gone.", wiki=P["Sandela"],
      cat="Ni", T=200),
    R("2-Pinanol", "Pinene + H2 + O2 + Na2SO3 -> Pinanol2 + Na2SO4", CAT,
      "Pinene hydrogenated to cis-pinane, oxidised by air to its hydroperoxide, and reduced with sulfite.",
      wiki=P["Pinanol2"], cat="Pd", T=80),
    R("Fluorosulfonyl Acetyl Fluoride", "TFE + SO3 -> FSAF", CAT,
      "Tetrafluoroethylene and sulfur trioxide make a sultone, which triethylamine rearranges to the acyl fluoride.",
      wiki=P["FSAF"], cat="Et3N", T=40),
    R("Hexachloropropane", "CCl4 + VDC -> HCC230fa", CAT,
      "Carbon tetrachloride added across vinylidene chloride over iron.", wiki=P["HCC230fa"], cat="Fe", T=100),
    R("HFC-236fa", "HCC230fa + 6 HF -> HFC236fa + 6 HCl", CAT,
      "Every chlorine swapped for fluorine with hydrogen fluoride.", wiki=P["HFC236fa"], cat="SbCl5", T=100),
    R("FC-75", "OctanoylCl + 16 HF -> FC75 + HCl + 15 H2", ECELL,
      "Electrochemical fluorination of octanoyl chloride: the chain fluorinates and part of it curls into a perfluorinated ring.",
      wiki=P["FC75"], T=10),
    R("Heptane Isomerisation", "Heptane -> MeHexane3", CAT, "n-Heptane isomerised over platinum on chlorided alumina.",
      wiki=P["MeHexane3"], cat="Pt", T=150),
    R("EPDM Rubber", "Ethylene + Propylene + DCPD -> EPDM", POLY,
      "Ethylene and propylene copolymerised with a little dicyclopentadiene, which leaves double bonds for vulcanising.",
      wiki=P["EPDM"]),
]

# Milestones for the stretches this part lengthened (messages only).
import authored_content as _C  # noqa: E402
from gen_authored import Milestone  # noqa: E402
_C.MILESTONES += [
    Milestone("Chlorothiazide", message="Merck's chlorothiazide (1958), the first thiazide diuretic: high blood pressure became a thing a daily pill could treat."),
]
import authored_canon_30  # noqa: E402,F401
