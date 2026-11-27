"""
Curieosity's multi-step processes. Where a recipe's description tells of two operations (fat soaks
up jasmine, then alcohol washes the scent out of it; a hydrocarbon is sulfonated, then the sulfonic
acid is fused with caustic soda), the recipe now takes the two, usually in two vessels, through the
intermediate between them. Some intermediates are real articles of commerce; others exist only on
the way, like jasmine pomade, whose one use is to be washed with alcohol.

split(original, *steps) takes a recipe out of its era and puts the steps where it was. A step that
needs an intermediate another recipe already makes simply starts from it. settle_eras() then moves
any step whose inputs arrive later into the era where they do.

Left as one step: one-pot chemistry (Tollens' pentaerythritol, the Koch reaction), purification
("then distilled pure"), histories (Kossel's nucleobases), and the salts that melt before they
decompose; and, by design, nothing that adds route detail toward explosives or watched precursors.
"""

from authored_canon import S, R, OURS, settle_eras  # noqa: F401
from authored_content import EPOCHS, SUBSTANCES
from gen_authored import (MIX, HEAT, COOL, DISTIL, LIGHT, CAT, PRESS, POLY, FLASK, SMELT,  # noqa: F401
                          ECELL, HIGHP, CENT)


def _find(name):
    for e in EPOCHS:
        for i, r in enumerate(e.reactions):
            if r.name == name:
                return e, i, r
    raise SystemExit(f"authored_steps: no recipe called {name!r} to split")


def wiki_of(name):
    """The article the recipe links (its intermediates link it too, where they have none)."""
    return _find(name)[2].wiki


def split(original, *steps):
    """Replace a recipe with its steps, in its era and place (with none: its steps are already
    written elsewhere, so the one-step recipe simply goes)."""
    e, i, _ = _find(original)
    e.reactions[i:i + 1] = list(steps)


def W(name):
    return wiki_of(name)


# --------------------------------------------------------------------------------------------------
# Alchemy and the early trades
# --------------------------------------------------------------------------------------------------
S(None, "EtHSO4", "Ethyl Hydrogen Sulfate", "C2H6O4S", "Liquid", "Ethyl_sulfate",
  "Ethanol joined to sulfuric acid: the 'sulfovinic acid' of the 1800s, the step between alcohol and "
  "ether.", smiles="CCOS(=O)(=O)O")
split("Sweet Oil of Vitriol",
      R("Sulfovinic Acid", "Ethanol + H2SO4 -> EtHSO4 + H2O", MIX,
        "Alcohol poured into oil of vitriol grows hot: the acid takes up the ethanol as ethyl hydrogen "
        "sulfate.", wiki="Ethyl_sulfate", dh=-20),
      R("Sweet Oil of Vitriol", "EtHSO4 + Ethanol -> Ether + H2SO4", DISTIL,
        "Valerius Cordus (1540) distilled alcohol with sulfuric acid and collected a sweet, volatile "
        "liquid: ether, later the first surgical anaesthetic. Williamson (1850) showed why the acid is "
        "never used up: its ethyl sulfate meets more alcohol, gives ether and is sulfuric acid again.",
        wiki="Diethyl_ether#History", T=140, dh=-5))

_w = W("Enfleurage")
S(None, "JasminePomade", "Jasmine Pomade", "mixture", "Solid", _w,
  "Fat that has lain under fresh jasmine for weeks, the flowers changed every day, until it is "
  "saturated with their scent. Its one use: to be washed with alcohol.")
SUBSTANCES["JasminePomade"].balance = "C"
split("Enfleurage",
      R("Enfleurage", "Jasmine + Tallow -> JasminePomade", MIX,
        "Grasse perfumers laid jasmine flowers on trays of purified fat, which soaks up their scent: "
        "a pomade.", wiki=_w, exact=False),
      R("Jasmine Absolute", "JasminePomade + Ethanol -> BenzylAcetate + Tallow", DISTIL,
        "The pomade washed with alcohol gives up its scent and keeps its fat; the alcohol distilled off "
        "leaves the absolute, rich in benzyl acetate.", wiki=_w, exact=False))

_w = W("Making Smalt")
S(None, "CobaltGlass", "Cobalt Glass", "mixture", "Solid", _w,
  "Potash glass coloured deep blue by cobalt: cast in cakes in Saxony from the 1500s, to be ground "
  "into the pigment smalt.", color="#1f3fbf")
SUBSTANCES["CobaltGlass"].balance = "SiO2"
split("Making Smalt",
      R("Cobalt Glass", "Glass + CoO -> CobaltGlass", HEAT,
        "Cobalt oxide from the Saxon silver mines melted into potash glass turns it sapphire blue.",
        wiki=_w, exact=False),
      R("Making Smalt", "CobaltGlass -> Smalt", MIX,
        "The blue glass crushed and ground fine under water: smalt, the blue of Delft and of Ming export "
        "ware.", wiki=_w, exact=False))

_w = W("Fusing Blood Lye")
S(None, "BloodLyeMelt", "Blood-Lye Melt", "mixture", "Solid", _w,
  "The black cake left when dried blood is fused with potash and iron: worthless until water leaches "
  "the yellow prussiate out of it.")
SUBSTANCES["BloodLyeMelt"].balance = "K"
split("Fusing Blood Lye",
      R("Fusing Blood Lye", "DriedBlood + Potash + Fe -> BloodLyeMelt", HEAT,
        "Dried blood fused with potash in an iron pot: a black melt that holds the cyanide the blood's "
        "nitrogen became.", wiki=_w, exact=False),
      R("Leaching Blood Lye", "BloodLyeMelt + H2O -> Prussiate", MIX,
        "The melt leached with water: yellow crystals of potassium ferrocyanide, the source of Prussian "
        "blue for a century.", wiki=_w, exact=False))

# --------------------------------------------------------------------------------------------------
# Industry
# --------------------------------------------------------------------------------------------------
_w = W("Strecker's Alanine")
S(None, "Aminopropionitrile", "2-Aminopropionitrile", "C3H6N2", "Liquid", _w,
  "The aminonitrile of Strecker's synthesis: acetaldehyde with ammonia and hydrogen cyanide, one "
  "hydrolysis away from alanine.", smiles="CC(N)C#N")
split("Strecker's Alanine",
      R("Strecker's Aminonitrile", "Acetaldehyde + NH3 + HCN -> Aminopropionitrile + H2O", FLASK,
        "Adolph Strecker (1850) combined acetaldehyde, ammonia and hydrogen cyanide into an aminonitrile.",
        wiki=_w),
      R("Strecker's Alanine", "Aminopropionitrile + 2 H2O -> Alanine + NH3", HEAT,
        "Boiled with acid, the nitrile becomes a carboxylic acid: alanine, the first amino acid made in a "
        "flask.", wiki=_w))

_w = W("Malonic Acid")
S(None, "CyanoaceticAcid", "Cyanoacetic Acid", "C3H3NO2", "Solid", "Cyanoacetic_acid",
  "Chloroacetic acid with its chlorine swapped for cyanide (Kolbe's nitrile synthesis): the root of "
  "malonic acid and of the cyanoacrylate glues.", smiles="N#CCC(=O)O")
split("Malonic Acid",
      R("Kolbe's Cyanoacetic Acid", "ClAcOH + NaCN -> CyanoaceticAcid + NaCl", FLASK,
        "Chloroacetic acid's chlorine swapped for cyanide.", wiki="Cyanoacetic_acid"),
      R("Malonic Acid", "CyanoaceticAcid + 2 H2O -> MalonicAcid + NH3", HEAT,
        "The nitrile hydrolysed: Victor Dessaignes' malonic acid, first made from malic acid in 1858.",
        wiki=_w))
split("Ethyl Cyanoacetate",
      R("Ethyl Cyanoacetate", "CyanoaceticAcid + Ethanol -> EthylCyanoacetate + H2O", CAT,
        "Cyanoacetic acid esterified with ethanol over sulfuric acid.", wiki=W("Ethyl Cyanoacetate"),
        cat="H2SO4", T=80))

_w = W("Centrifugal Sugar")
S(None, "Massecuite", "Massecuite", "mixture", "Solid", _w,
  "Cane syrup boiled down until it is thick with sugar crystals: French for 'cooked mass', and the "
  "stuff the centrifuge spins.", color="#a0703a")
SUBSTANCES["Massecuite"].balance = "C12H22O11"
split("Centrifugal Sugar",
      R("Boiling Massecuite", "CaneJuice -> Massecuite + H2O", HEAT,
        "Cane juice boiled down, in vacuum pans since Rillieux (1840s), to a syrup thick with crystals.",
        wiki=_w, exact=False),
      R("Centrifugal Sugar", "Massecuite -> Sucrose + Molasses", CENT,
        "The massecuite spun in a perforated basket: the molasses flies off and the sugar stays.",
        wiki=_w, exact=False))

_w = W("Malachite Green")
S(None, "LeucoMG", "Leucomalachite Green", "C23H26N2", "Solid", "Leucomalachite_green",
  "The colourless 'leuco' form of malachite green: the dye before oxidation gives it its colour.",
  smiles="CN(C)c1ccc(cc1)C(c1ccccc1)c1ccc(cc1)N(C)C")
split("Malachite Green",
      R("Leucomalachite Green", "Benzaldehyde + 2 Dimethylaniline -> LeucoMG + H2O", FLASK,
        "Benzaldehyde condensed with two dimethylanilines (Fischer, 1877): colourless, so far.",
        wiki="Leucomalachite_green"),
      R("Malachite Green", "2 LeucoMG + O2 + 2 HCl -> 2 MalachiteGreen + 2 H2O", MIX,
        "The leuco base oxidised in acid: the deep green dye.", wiki=_w))

_w = W("Indigo Carmine")
S("483-20-5", "SaxonBlue", "Saxon Blue", "C16H10N2O8S2", "Solid", _w,
  "Indigotindisulfonic acid: indigo dissolved in fuming sulfuric acid, two sulfonic acid groups on "
  "it. Barth's Saxon blue (1740), the first indigo that dyed straight from a solution.", lib=5988,
  smiles="O=C1C(=C2Nc3ccc(cc3C2=O)S(=O)(=O)O)Nc2ccc(cc12)S(=O)(=O)O", color="#1a2a9a")
split("Indigo Carmine",
      R("Saxon Blue", "Indigo + 2 H2SO4 -> SaxonBlue + 2 H2O", FLASK,
        "Indigo sulfonated in fuming sulfuric acid (Barth, 1740).", wiki=_w),
      R("Indigo Carmine", "SaxonBlue + 2 NaOH -> IndigoCarmine + 2 H2O", MIX,
        "Saxon blue neutralised with caustic soda: indigo carmine, the food dye E132.", wiki=_w))

_w = W("3,3'-Dichlorobenzidine")
S(None, "DCHB", "2,2'-Dichlorohydrazobenzene", "C12H10Cl2N2", "Solid", _w,
  "Two chloronitrobenzenes reduced and joined at their nitrogens: the hydrazo compound that acid "
  "turns into dichlorobenzidine.", smiles="Clc1ccccc1NNc1ccccc1Cl")
split("3,3'-Dichlorobenzidine",
      R("2,2'-Dichlorohydrazobenzene", "2 ONCB + 5 Zn + H2O -> DCHB + 5 ZnO", FLASK,
        "Zinc in caustic soda reduces two molecules of o-chloronitrobenzene to a hydrazobenzene.", wiki=_w),
      R("3,3'-Dichlorobenzidine", "DCHB -> DCB", CAT,
        "In acid the hydrazobenzene rearranges, its rings swinging round to join: the benzidine "
        "rearrangement.", wiki=_w, cat="H2SO4", T=30))

split("o-Anisidine",
      R("o-Anisidine", "oNitroanisole + 3 H2 -> oAnisidine + 2 H2O", HIGHP,
        "2-Nitroanisole's nitro group hydrogenated over nickel to the amine.", wiki=W("o-Anisidine"),
        cat="Ni", T=100, P=20))

for _orig, _src, _key, _name, _sm in [
        ("Xylenol by Caustic Fusion", "oXylene", "XSA34", "3,4-Dimethylbenzenesulfonic Acid", "Cc1ccc(cc1C)S(=O)(=O)O"),
        ("2,5-Xylenol by Caustic Fusion", "pXylene", "XSA25", "2,5-Dimethylbenzenesulfonic Acid", "Cc1ccc(C)c(c1)S(=O)(=O)O")]:
    _w = W(_orig)
    _xyl = "Xylenol34" if _key == "XSA34" else "Xylenol25"
    S(None, _key, _name, "C8H10O3S", "Solid", _w,
      "A xylene sulfonated: a strong acid that dissolves in water, fused with caustic soda into a "
      "xylenol.", smiles=_sm)
    split(_orig,
          R(f"Sulfonating {'o' if _src == 'oXylene' else 'p'}-Xylene", f"{_src} + H2SO4 -> {_key} + H2O", FLASK,
            "The xylene sulfonated in hot sulfuric acid.", wiki=_w, T=120),
          R(_orig, f"{_key} + 2 NaOH -> {_xyl} + Na2SO3 + H2O", HEAT,
            "The sulfonate fused with caustic soda: the sulfur leaves as sulfite and an -OH takes its "
            "place.", wiki=_w, T=320))

_w = W("Metanilic Acid")
S(None, "NBSA3", "3-Nitrobenzenesulfonic Acid", "C6H5NO5S", "Solid", _w,
  "Nitrobenzene sulfonated: both groups pull on the ring, so the sulfonic acid goes to the meta "
  "position.", smiles="O=[N+]([O-])c1cccc(c1)S(=O)(=O)O")
split("Metanilic Acid",
      R("3-Nitrobenzenesulfonic Acid", "Nitrobenzene + SO3 -> NBSA3", FLASK,
        "Nitrobenzene sulfonated in the meta position.", wiki=_w, T=100),
      R("Metanilic Acid", "NBSA3 + 3 H2 -> Metanilic + 2 H2O", HIGHP,
        "The nitro group reduced to an amine: metanilic acid, for the yellow azo dyes.", wiki=_w,
        cat="Ni", T=100, P=20))

S(None, "CaHPO4", "Dicalcium Phosphate", "CaHPO4", "Solid", "Dicalcium_phosphate",
  "Calcium hydrogen phosphate: a mineral feed for livestock, a polish in toothpaste, and calcined, "
  "calcium pyrophosphate.")
split("Calcium Pyrophosphate",
      R("Dicalcium Phosphate", "CaCO3 + H3PO4 -> CaHPO4 + CO2 + H2O", MIX,
        "Chalk dissolved in phosphoric acid, fizzing.", wiki="Dicalcium_phosphate"),
      R("Calcium Pyrophosphate", "2 CaHPO4 -> Ca2P2O7 + H2O", HEAT,
        "Dicalcium phosphate calcined until two phosphates join and give off water.",
        wiki=W("Calcium Pyrophosphate"), T=450))

S(None, "NaH2PO4", "Monosodium Phosphate", "NaH2PO4", "Solid", "Monosodium_phosphate",
  "Sodium dihydrogen phosphate: a food acid and buffer, and melted, the start of the sodium "
  "polyphosphates.")
split("Calgon",
      R("Monosodium Phosphate", "H3PO4 + NaOH -> NaH2PO4 + H2O", MIX,
        "Caustic soda neutralises a third of phosphoric acid's acidity.", wiki="Monosodium_phosphate"),
      R("Calgon", "6 NaH2PO4 -> SHMP + 6 H2O", SMELT,
        "Monosodium phosphate melted until the phosphates link into rings, then quenched to a glass: "
        "Calgon, which softens water by holding its calcium.", wiki=W("Calgon"), T=700))

_w = W("2-Naphthol")
S(None, "NSA2", "Naphthalene-2-sulfonic Acid", "C10H8O3S", "Solid", "Naphthalene-2-sulfonic_acid",
  "Naphthalene sulfonated hot, at the beta position: the sulfonic acid that caustic fusion turns into "
  "2-naphthol.", smiles="O=S(=O)(O)c1ccc2ccccc2c1")
split("2-Naphthol",
      R("Naphthalene-2-sulfonic Acid", "Naphthalene + H2SO4 -> NSA2 + H2O", FLASK,
        "Naphthalene sulfonated at 160 C, hot enough that the acid settles at the beta position.",
        wiki="Naphthalene-2-sulfonic_acid", T=160),
      R("2-Naphthol", "NSA2 + 2 NaOH -> Naphthol2 + Na2SO3 + H2O", HEAT,
        "The sulfonate fused with caustic soda: 2-naphthol, the coupling partner of countless azo dyes.",
        wiki=_w, T=300))

split("Tetrapotassium Pyrophosphate",
      R("Tetrapotassium Pyrophosphate", "2 K2HPO4 -> TKPP + H2O", HEAT,
        "Dipotassium phosphate calcined until two phosphates join.", wiki=W("Tetrapotassium Pyrophosphate"),
        T=500))

_w = W("Beta-Ionone")
S(None, "Pseudoionone", "Pseudoionone", "C13H20O", "Liquid", _w,
  "Citral condensed with acetone: an open-chain ketone of faint scent, one acid bath away from the "
  "ionones. Which acid it meets decides which ionone it becomes.", smiles="CC(C)=CCCC(C)=CC=CC(C)=O")
split("Tiemann's Violets",
      R("Pseudoionone", "Geranial + Acetone + NaOH -> Pseudoionone + H2O + NaOH", MIX,
        "Citral and acetone condensed in dilute caustic soda: pseudoionone, the open chain both ionones "
        "close from.", wiki=_w, dh=-30),
      R("Tiemann's Violets", "Pseudoionone + H3PO4 -> aIonone + H3PO4", FLASK,
        "Tiemann and Kruger (1893) closed pseudoionone's ring with dilute acid: alpha-ionone, the scent "
        "of violets, with no violets.", wiki="Ionone#History", dh=-20))
split("Beta-Ionone",
      R("Beta-Ionone", "Pseudoionone + H2SO4 -> bIonone + H2SO4", FLASK,
        "In concentrated sulfuric acid the ring closes the other way: beta-ionone, the starting point "
        "for synthetic vitamin A.", wiki=_w, T=50, dh=-20))

# --------------------------------------------------------------------------------------------------
# Modern
# --------------------------------------------------------------------------------------------------
_w = W("Oxidising Cyclohexane")
split("Oxidising Cyclohexane",
      R("Air-Oxidising Cyclohexane", "Cyclohexane + O2 -> Cyclohexanone + H2O", HEAT,
        "Cyclohexane oxidised by air at 150 C to 'KA oil', mostly cyclohexanone.", wiki=_w, T=150),
      R("Oxidising Cyclohexane", "Cyclohexanone + 2 HNO3 -> Adipic + 2 NO + H2O", FLASK,
        "Nitric acid splits the ring: adipic acid, for nylon 6,6.", wiki=_w, T=70))

_w = W("Cyclohexanedimethanol")
S(None, "DMCD", "Dimethyl 1,4-Cyclohexanedicarboxylate", "C10H16O4", "Liquid", _w,
  "Dimethyl terephthalate with its ring hydrogenated: the first of the two hydrogenations to "
  "cyclohexanedimethanol.", lib=5395, smiles="COC(=O)C1CCC(CC1)C(=O)OC")
split("Cyclohexanedimethanol",
      R("Hydrogenating DMT's Ring", "DMT + 3 H2 -> DMCD", HIGHP,
        "Dimethyl terephthalate's ring hydrogenated over palladium.", wiki=_w, cat="Pd", T=160, P=300),
      R("Cyclohexanedimethanol", "DMCD + 4 H2 -> CHDM + 2 Methanol", HIGHP,
        "Then the ester groups, over copper: cyclohexanedimethanol, for Eastman's clear polyesters.",
        wiki=_w, cat="Cu", T=200, P=300))

_w = W("Neopentyl Glycol")
S(None, "HPA", "Hydroxypivaldehyde", "C5H10O2", "Solid", "Hydroxypivaldehyde",
  "Isobutyraldehyde and formaldehyde joined by an aldol reaction: one hydrogenation from neopentyl "
  "glycol.", smiles="CC(C)(CO)C=O")
split("Neopentyl Glycol",
      R("Hydroxypivaldehyde", "Isobutyraldehyde + CH2O -> HPA", FLASK,
        "Isobutyraldehyde and formaldehyde condensed with a little amine.", wiki=_w, T=70),
      R("Neopentyl Glycol", "HPA + H2 -> NPG", CAT,
        "Hydroxypivaldehyde hydrogenated over nickel: neopentyl glycol, for powder coatings.", wiki=_w,
        cat="Ni", T=120))

split("Isononanol",
      R("Isononanol", "Isononanal + H2 -> Isononanol", CAT,
        "The oxo aldehyde hydrogenated over nickel.", wiki=W("Isononanol"), cat="Ni", T=150))

for _orig, _ald, _key, _name, _formula, _sm, _prod in [
        ("2-Heptanone", "Butanal", "Heptenone", "3-Hepten-2-one", "C7H12O", "CCC/C=C/C(C)=O", "Heptanone2"),
        ("2-Pentanone", "Acetaldehyde", "Pentenone", "3-Penten-2-one", "C5H8O", "C/C=C/C(C)=O", "Pentanone2")]:
    _w = W(_orig)
    S(None, _key, _name, _formula, "Liquid", _w,
      f"Acetone and {_ald.lower()} condensed, losing water: an unsaturated ketone, one hydrogenation from "
      f"{_orig.lower()}.", smiles=_sm)
    split(_orig,
          R(_name, f"Acetone + {_ald} -> {_key} + H2O", FLASK,
            f"Acetone and {_ald.lower()} condensed in base.", wiki=_w, T=60),
          R(_orig, f"{_key} + H2 -> {_prod}", CAT,
            "The double bond hydrogenated over palladium.", wiki=_w, cat="Pd", T=80))


_w = W("TMCD")
S(None, "TMCBD", "Tetramethylcyclobutanedione", "C8H12O2", "Solid", _w,
  "Two dimethylketenes joined into a square ring with two ketones: Eastman's route to a BPA-free "
  "polyester diol.", smiles="CC1(C)C(=O)C(C)(C)C1=O")
split("TMCD",
      R("Tetramethylcyclobutanedione", "2 IsobutyricAcid -> TMCBD + 2 H2O", HEAT,
        "Isobutyric acid cracked to dimethylketene, which dimerises to a square diketone.", wiki=_w, T=700),
      R("TMCD", "TMCBD + 2 H2 -> TMCD", HIGHP,
        "The diketone hydrogenated to the diol (Eastman, Tritan).", wiki=_w, cat="Rh", T=140, P=50))

S(None, "HSA", "12-Hydroxystearic Acid", "C18H36O3", "Solid", W("Lithium Grease Soap"),
  "Castor oil's ricinoleic acid hydrogenated: a waxy acid whose lithium soap thickens grease.",
  lib=2372, smiles="CCCCCCC(O)CCCCCCCCCCC(=O)O")
split("Lithium Grease Soap",
      R("12-Hydroxystearic Acid", "RicinoleicAcid + H2 -> HSA", HIGHP,
        "Ricinoleic acid's double bond hydrogenated over nickel.", wiki=W("Lithium Grease Soap"), cat="Ni", T=150, P=10),
      R("Lithium Grease Soap", "HSA + LiOH -> LiHSt + H2O", HEAT,
        "12-Hydroxystearic acid saponified with lithium hydroxide: the soap that thickens most of the "
        "world's grease.", wiki=W("Lithium Grease Soap"), T=200))

_w = W("4,4'-Oxydianiline")
S(None, "DNDPE", "4,4'-Dinitrodiphenyl Ether", "C12H8N2O5", "Solid", _w,
  "Two nitrobenzene rings joined through an oxygen: hydrogenated, the diamine of Kapton.",
  smiles="O=[N+]([O-])c1ccc(Oc2ccc(cc2)[N+](=O)[O-])cc1")
split("4,4'-Oxydianiline",
      R("4,4'-Dinitrodiphenyl Ether", "2 NCB + 2 NaOH -> DNDPE + 2 NaCl + H2O", FLASK,
        "Nitrochlorobenzene joins nitrophenoxide into a dinitrodiphenyl ether.", wiki=_w, T=150),
      R("4,4'-Oxydianiline", "DNDPE + 6 H2 -> ODA + 4 H2O", CAT,
        "Both nitro groups hydrogenated over palladium.", wiki=_w, cat="Pd", T=100))

_w = W("Diglyme")
S(None, "DEGME", "Diethylene Glycol Monomethyl Ether", "C5H12O3", "Liquid", _w,
  "Methanol with two ethylene oxides opened onto it: a solvent ('methyl carbitol') and jet-fuel "
  "de-icer, one methyl short of diglyme.", smiles="COCCOCCO")
split("Diglyme",
      R("Methyl Carbitol", "Methanol + 2 EO -> DEGME", CAT,
        "Ethylene oxide opened by methanol twice over.", wiki=_w, cat="BF3", T=100),
      R("Diglyme", "DEGME + NaOH + CH3Cl -> Diglyme + NaCl + H2O", FLASK,
        "Then the end methylated, a Williamson ether synthesis.", wiki=_w, T=80))

S(None, "Oleonitrile", "Oleonitrile", "C18H33N", "Liquid", W("Oleylamine"),
  "Oleic acid with its acid group turned into a nitrile: the step between the fatty acid and the "
  "fatty amine.", lib=2734, smiles="CCCCCCCC/C=C\\CCCCCCCC#N")
split("Oleylamine",
      R("Oleonitrile", "OleicAcid + NH3 -> Oleonitrile + 2 H2O", CAT,
        "Oleic acid and ammonia over alumina at 300 C: the amide forms and loses water again.",
        wiki=W("Oleylamine"), cat="Alumina", T=300),
      R("Oleylamine", "Oleonitrile + 2 H2 -> Oleylamine", HIGHP,
        "The nitrile hydrogenated over nickel.", wiki=W("Oleylamine"), cat="Ni", T=130, P=20))

S(None, "TributylCitrate", "Tributyl Citrate", "C18H32O7", "Liquid", W("Acetyl Tributyl Citrate"),
  "Citric acid with all three acids esterified with butanol: a plasticiser in its own right.",
  lib=8074, smiles="CCCCOC(=O)CC(O)(CC(=O)OCCCC)C(=O)OCCCC")
split("Acetyl Tributyl Citrate",
      R("Tributyl Citrate", "Citric + 3 Butanol -> TributylCitrate + 3 H2O", CAT,
        "Citric acid esterified with butanol over sulfuric acid.", wiki=W("Acetyl Tributyl Citrate"),
        cat="H2SO4", T=130),
      R("Acetyl Tributyl Citrate", "TributylCitrate + AceticAnhydride -> ATBC + AcOH", FLASK,
        "Then its last -OH acetylated: a plasticiser for toys and food wrap.", wiki=W("Acetyl Tributyl Citrate"),
        T=100))

_w = W("Chlorotoluidine")
S(None, "ClNitrotoluene", "2-Chloro-4-nitrotoluene", "C7H6ClNO2", "Solid", _w,
  "p-Nitrotoluene chlorinated beside its methyl group.", smiles="Cc1ccc(cc1Cl)[N+](=O)[O-]")
split("Chlorotoluidine",
      R("2-Chloro-4-nitrotoluene", "Nitrotoluene + Cl2 -> ClNitrotoluene + HCl", FLASK,
        "p-Nitrotoluene chlorinated beside the methyl group, with an iron catalyst.", wiki=_w, T=70),
      R("Chlorotoluidine", "ClNitrotoluene + 3 H2 -> CMA + 2 H2O", HIGHP,
        "The nitro group hydrogenated.", wiki=_w, cat="Ni", T=100, P=20))

_w = W("Phenetidine")
S(None, "NPhenetole", "4-Nitrophenetole", "C8H9NO3", "Solid", _w,
  "Nitrochlorobenzene with ethoxide in place of its chlorine.", smiles="CCOc1ccc(cc1)[N+](=O)[O-]")
split("Phenetidine",
      R("4-Nitrophenetole", "NCB + NaOEt -> NPhenetole + NaCl", FLASK,
        "Nitrochlorobenzene's chlorine swapped for ethoxide.", wiki=_w, T=90),
      R("Phenetidine", "NPhenetole + 3 H2 -> Phenetidine + 2 H2O", CAT,
        "The nitro group hydrogenated over palladium.", wiki=_w, cat="Pd", T=90))

_w = W("Bronopol")
S(None, "NPD", "2-Nitropropane-1,3-diol", "C3H7NO4", "Solid", _w,
  "Nitromethane with two formaldehydes added: brominated, the preservative bronopol.",
  smiles="OCC(CO)[N+](=O)[O-]")
split("Bronopol",
      R("2-Nitropropane-1,3-diol", "Nitromethane + 2 CH2O -> NPD", MIX,
        "Nitromethane takes two formaldehydes in a little base (Henry reactions).", wiki=_w),
      R("Bronopol", "NPD + Br2 + NaOH -> Bronopol + NaBr + H2O", FLASK,
        "Then bromine, at the carbon between the two -OH groups.", wiki=_w, T=10))

_w = W("Ethylanthraquinone")
S(None, "EBBA", "2-(4-Ethylbenzoyl)benzoic Acid", "C16H14O3", "Solid", _w,
  "Phthalic anhydride acylating ethylbenzene: the open keto acid that closes into ethylanthraquinone.",
  smiles="CCc1ccc(cc1)C(=O)c1ccccc1C(=O)O")
split("Ethylanthraquinone",
      R("Ethylbenzoylbenzoic Acid", "PhthalicAnhydride + Ethylbenzene -> EBBA", CAT,
        "Phthalic anhydride and ethylbenzene (Friedel-Crafts).", wiki=_w, cat="AlCl3", T=60),
      R("Ethylanthraquinone", "EBBA -> EAQ + H2O", CAT,
        "The keto acid cyclised in hot sulfuric acid: the anthraquinone that carries hydrogen in the "
        "peroxide process.", wiki=_w, cat="H2SO4", T=120))

_w = W("2-Chlorobenzaldehyde")
S(None, "CBC", "2-Chlorobenzal Chloride", "C7H5Cl3", "Liquid", _w,
  "o-Chlorotoluene with two chlorines on its methyl group: hydrolysed, an aldehyde.",
  smiles="ClC(Cl)c1ccccc1Cl")
split("2-Chlorobenzaldehyde",
      R("2-Chlorobenzal Chloride", "oChlorotoluene + 2 Cl2 -> CBC + 2 HCl", HEAT,
        "o-Chlorotoluene chlorinated twice on its methyl group at its boiling point, where the chlorine "
        "attacks the side chain and not the ring.", wiki=_w, T=160),
      R("2-Chlorobenzaldehyde", "CBC + H2O -> ClBenzaldehyde2 + 2 HCl", FLASK,
        "The benzal chloride hydrolysed to the aldehyde.", wiki=_w, T=100))

_w = W("Chloroxylenol")
S(None, "Xylenol35", "3,5-Xylenol", "C8H10O", "Solid", "3,5-Xylenol",
  "Phenol with two methyl groups, made by aromatising isophorone: chlorinated, the antiseptic in "
  "Dettol.", smiles="Cc1cc(C)cc(O)c1")
split("Chloroxylenol",
      R("3,5-Xylenol", "Isophorone -> Xylenol35 + Methane", CAT,
        "Isophorone aromatised over alumina, losing a methyl group.", wiki="3,5-Xylenol", cat="Alumina", T=550),
      R("Chloroxylenol", "Xylenol35 + Cl2 -> PCMX + HCl", FLASK,
        "3,5-Xylenol chlorinated: chloroxylenol, the antiseptic of Dettol (1932).", wiki=_w, T=40))

_w = W("Benzylacetone")
S(None, "Benzalacetone", "Benzylideneacetone", "C10H10O", "Solid", "Benzylideneacetone",
  "Benzaldehyde and acetone condensed (the Claisen-Schmidt reaction): sweet-smelling, and one "
  "hydrogenation from benzylacetone.", smiles="CC(=O)/C=C/c1ccccc1")
split("Benzylacetone",
      R("Benzylideneacetone", "Benzaldehyde + Acetone -> Benzalacetone + H2O", MIX,
        "Benzaldehyde and acetone condensed with caustic soda.", wiki="Benzylideneacetone"),
      R("Benzylacetone", "Benzalacetone + H2 -> BenzylAcetone", CAT,
        "The double bond hydrogenated over palladium.", wiki=_w, cat="Pd", T=60))

S(None, "VTCS", "Vinyltrichlorosilane", "C2H3Cl3Si", "Liquid", W("Vinyltriethoxysilane"),
  "Trichlorosilane added across acetylene: a vinyl group on silicon, three chlorines to replace.",
  lib=7926, smiles="C=C[Si](Cl)(Cl)Cl")
split("Vinyltriethoxysilane",
      R("Vinyltrichlorosilane", "HSiCl3 + Acetylene -> VTCS", CAT,
        "Trichlorosilane adds to acetylene over platinum.", wiki=W("Vinyltriethoxysilane"), cat="Pt", T=120),
      R("Vinyltriethoxysilane", "VTCS + 3 Ethanol -> VTEO + 3 HCl", FLASK,
        "Ethanol replaces the chlorines: a coupling agent that ties glass fibres to plastic.",
        wiki=W("Vinyltriethoxysilane"), T=60))

_w = W("Octocrylene")
S(None, "EHCA", "2-Ethylhexyl Cyanoacetate", "C11H19NO2", "Liquid", _w,
  "Cyanoacetate transesterified with 2-ethylhexanol.", smiles="CCCCC(CC)COC(=O)CC#N")
split("Octocrylene",
      R("2-Ethylhexyl Cyanoacetate", "EthylCyanoacetate + 2EH -> EHCA + Ethanol", FLASK,
        "Ethyl cyanoacetate transesterified with 2-ethylhexanol.", wiki=_w, T=140),
      R("Octocrylene", "EHCA + Benzophenone -> Octocrylene + H2O", HEAT,
        "Then a Knoevenagel condensation with benzophenone: a UV filter in sunscreens.", wiki=_w, T=180))

_w = W("Adamantane")
S(None, "THDCPD", "Tetrahydrodicyclopentadiene", "C10H16", "Liquid", _w,
  "Dicyclopentadiene hydrogenated: the strained cage that aluminium chloride reshuffles into "
  "adamantane (and, as its exo form, the missile fuel JP-10).", smiles="C1CC2C3CCC(C3)C2C1")
split("Adamantane",
      R("Tetrahydrodicyclopentadiene", "DCPD + 2 H2 -> THDCPD", HIGHP,
        "Dicyclopentadiene hydrogenated.", wiki=_w, cat="Ni", T=150, P=20),
      R("Adamantane", "THDCPD -> Adamantane", CAT,
        "Schleyer's route (1957): aluminium chloride shuffles the cage into adamantane.", wiki=_w,
        cat="AlCl3", T=150))

_w = W("Raspberry Ketone")
S(None, "HBAc", "4-Hydroxybenzalacetone", "C10H10O2", "Solid", _w,
  "4-Hydroxybenzaldehyde and acetone condensed: raspberry ketone with a double bond still in it.",
  smiles="CC(=O)/C=C/c1ccc(O)cc1")
split("Raspberry Ketone",
      R("4-Hydroxybenzalacetone", "HBA4 + Acetone -> HBAc + H2O", MIX,
        "An aldol condensation with acetone.", wiki=_w),
      R("Raspberry Ketone", "HBAc + H2 -> RaspberryKetone", CAT,
        "The double bond hydrogenated.", wiki=_w, cat="Pd", T=60))

_w = W("Allyl Diglycol Carbonate")
S(None, "DEGBCF", "Diethylene Glycol Bis(chloroformate)", "C6H8Cl2O5", "Liquid", _w,
  "Diethylene glycol capped at both ends with phosgene.", smiles="ClC(=O)OCCOCCOC(Cl)=O")
split("Allyl Diglycol Carbonate",
      R("Diethylene Glycol Bis(chloroformate)", "DEG + 2 COCl2 -> DEGBCF + 2 HCl", COOL,
        "Diethylene glycol made into its bis(chloroformate) with phosgene, kept cold.", wiki=_w),
      R("Allyl Diglycol Carbonate", "DEGBCF + 2 AllylAlcohol -> ADC + 2 HCl", FLASK,
        "Then capped with allyl alcohol: CR-39, the monomer of light plastic spectacle lenses.", wiki=_w, T=20))

S(None, "NOX4", "4-Nitro-o-xylene", "C8H9NO2", "Solid", W("3,4-Dimethylaniline"),
  "o-Xylene nitrated: one hydrogenation from 3,4-dimethylaniline, the start of vitamin B2.",
  lib=8952, smiles="Cc1ccc(cc1C)[N+](=O)[O-]")
split("3,4-Dimethylaniline",
      R("4-Nitro-o-xylene", "oXylene + HNO3 -> NOX4 + H2O", FLASK,
        "o-Xylene nitrated in mixed acid.", wiki=W("3,4-Dimethylaniline"), T=30),
      R("3,4-Dimethylaniline", "NOX4 + 3 H2 -> DMA34 + 2 H2O", HIGHP,
        "The nitro group hydrogenated.", wiki=W("3,4-Dimethylaniline"), cat="Ni", T=100, P=20))

split("Oxybenzone",
      R("Oxybenzone", "DHBP + DimethylSulfate + NaOH -> Oxybenzone + NaMeSO4 + H2O", FLASK,
        "One of 2,4-dihydroxybenzophenone's -OH groups methylated: a UV filter.", wiki=W("Oxybenzone"), T=60))

split("Tetrabromophthalate Ester",
      R("Tetrabromophthalate Ester", "TBPA + 2 2EH -> TBPH + H2O", FLASK,
        "Tetrabromophthalic anhydride esterified with 2-ethylhexanol: a flame retardant plasticiser.",
        wiki=W("Tetrabromophthalate Ester"), T=200))

_w = W("2,3-Dichlorobutadiene")
S(None, "TCBE", "2,3,4-Trichloro-1-butene", "C4H5Cl3", "Liquid", _w,
  "Chloroprene with chlorine added across it.", smiles="C=C(Cl)C(Cl)CCl")
split("2,3-Dichlorobutadiene",
      R("2,3,4-Trichloro-1-butene", "Chloroprene + Cl2 -> TCBE", FLASK,
        "Chloroprene chlorinated.", wiki=_w, T=20),
      R("2,3-Dichlorobutadiene", "2 TCBE + Ca(OH)2 -> 2 DCBD + CaCl2 + 2 H2O", MIX,
        "Lime takes hydrogen chloride back off: a comonomer that keeps neoprene from crystallising.",
        wiki=_w))

split("Halothane",
      R("Halothane", "HCFC133a + Br2 -> Halothane + HBr", HEAT,
        "2-Chloro-1,1,1-trifluoroethane brominated at 450 C (Suckling, 1951): the anaesthetic halothane.",
        wiki=W("Halothane"), T=450))

_w = W("Lofgren's Lidocaine")
S(None, "CAX", "2-Chloro-2',6'-acetoxylidide", "C10H12ClNO", "Solid", _w,
  "2,6-Xylidine acylated with chloroacetyl chloride: the half of lidocaine that holds the ring.",
  smiles="Cc1cccc(C)c1NC(=O)CCl")
split("Lofgren's Lidocaine",
      R("Chloroacetoxylidide", "Xylidine26 + ClAcCl -> CAX + HCl", FLASK,
        "2,6-Xylidine acylated with chloroacetyl chloride.", wiki=_w, T=10),
      R("Lofgren's Lidocaine", "CAX + Diethylamine -> Lidocaine + HCl", HEAT,
        "Diethylamine displaces the chlorine: Nils Löfgren's lidocaine (1943), the local anaesthetic.",
        wiki=_w, T=100))

_w = W("Hexylresorcinol")
S(None, "HexanoylRes", "4-Hexanoylresorcinol", "C12H16O3", "Solid", _w,
  "Resorcinol acylated with hexanoic acid: a ketone, reduced to the hexyl chain.",
  smiles="CCCCCC(=O)c1ccc(O)cc1O")
split("Hexylresorcinol",
      R("4-Hexanoylresorcinol", "Resorcinol + Hexanoic + ZnCl2 -> HexanoylRes + H2O + ZnCl2", FLASK,
        "Resorcinol acylated with hexanoic acid and zinc chloride.", wiki=_w, T=140),
      R("Hexylresorcinol", "HexanoylRes + 2 H2 -> Hexylresorcinol + H2O", HIGHP,
        "The ketone reduced to a hexyl chain: an antiseptic in throat lozenges.", wiki=_w, cat="Ni", T=150, P=30))

_w = W("Dibutylaminopropylamine")
S(None, "DBAPN", "3-(Dibutylamino)propionitrile", "C11H22N2", "Liquid", _w,
  "Dibutylamine added across acrylonitrile.", smiles="CCCCN(CCCC)CCC#N")
split("Dibutylaminopropylamine",
      R("3-(Dibutylamino)propionitrile", "Dibutylamine + Acrylonitrile -> DBAPN", MIX,
        "Dibutylamine adds across acrylonitrile on its own.", wiki=_w),
      R("Dibutylaminopropylamine", "DBAPN + 2 H2 -> DBAPA", CAT,
        "The nitrile hydrogenated over nickel.", wiki=_w, cat="Ni", T=100))

S(None, "DMAPN", "Dimethylaminopropionitrile", "C5H10N2", "Liquid", W("DMAPA"),
  "Dimethylamine added across acrylonitrile.", lib=4119, smiles="CN(C)CCC#N")
split("DMAPA",
      R("Dimethylaminopropionitrile", "Acrylonitrile + Me2NH -> DMAPN", MIX,
        "Dimethylamine adds to acrylonitrile.", wiki=W("DMAPA")),
      R("DMAPA", "DMAPN + 2 H2 -> DMAPA", CAT,
        "The nitrile hydrogenated: DMAPA, the amine behind the mild surfactant cocamidopropyl betaine.",
        wiki=W("DMAPA"), cat="Ni", T=90))

split("Allyl Amyl Xanthate",
      R("Allyl Amyl Xanthate", "KAX + AllylChloride -> AllylAmylXanthate + KCl", MIX,
        "Potassium amyl xanthate allylated: a collector that floats copper ore.", wiki=W("Allyl Amyl Xanthate")))

_w = W("4-Chlorobenzotrifluoride")
S(None, "PCBTC", "4-Chlorobenzotrichloride", "C7H4Cl4", "Liquid", _w,
  "p-Chlorotoluene with its methyl group photochlorinated to CCl3.", smiles="ClC(Cl)(Cl)c1ccc(Cl)cc1")
split("4-Chlorobenzotrifluoride",
      R("4-Chlorobenzotrichloride", "pChlorotoluene + 3 Cl2 -> PCBTC + 3 HCl", LIGHT,
        "The methyl group photochlorinated to CCl3.", wiki=_w),
      R("4-Chlorobenzotrifluoride", "PCBTC + 3 HF -> PCBTF + 3 HCl", PRESS,
        "The chlorines swapped for fluorine with hydrogen fluoride: a solvent that escapes smog rules.",
        wiki=_w, T=100))

_w = W("Bis-EMA")
S(None, "BPAEO", "Bisphenol A Ethoxylate", "C19H24O4", "Liquid", _w,
  "Bisphenol A with an ethylene oxide on each end.", smiles="CC(C)(c1ccc(OCCO)cc1)c1ccc(OCCO)cc1")
split("Bis-EMA",
      R("Bisphenol A Ethoxylate", "BPA + 2 EO -> BPAEO", PRESS,
        "Bisphenol A ethoxylated at each end.", wiki=_w, T=150),
      R("Bis-EMA", "BPAEO + 2 MethacrylicAcid -> BisEMA + 2 H2O", FLASK,
        "Then esterified with methacrylic acid: a dental-filling resin.", wiki=_w, T=110))

_w = W("2,4-Xylidine")
S(None, "NMX", "4-Nitro-m-xylene", "C8H9NO2", "Liquid", _w,
  "m-Xylene nitrated.", smiles="Cc1ccc(c(C)c1)[N+](=O)[O-]")
split("2,4-Xylidine",
      R("4-Nitro-m-xylene", "mXylene + HNO3 -> NMX + H2O", FLASK,
        "m-Xylene nitrated in mixed acid.", wiki=_w, T=30),
      R("2,4-Xylidine", "NMX + 3 H2 -> Xylidine24 + 2 H2O", CAT,
        "The nitro compound hydrogenated over nickel.", wiki=_w, cat="Ni", T=100))

_w = W("Tricetylmethylammonium Chloride")
S(None, "Tricetylamine", "Tricetylamine", "C48H99N", "Solid", _w,
  "Ammonia with all three hydrogens replaced by cetyl chains.",
  smiles="CCCCCCCCCCCCCCCCN(CCCCCCCCCCCCCCCC)CCCCCCCCCCCCCCCC")
split("Tricetylmethylammonium Chloride",
      R("Tricetylamine", "3 CetylAlcohol + NH3 -> Tricetylamine + 3 H2O", CAT,
        "Cetyl alcohol aminated three times over.", wiki=_w, cat="CopperChromite", T=220),
      R("Tricetylmethylammonium Chloride", "Tricetylamine + CH3Cl -> TCMAC", PRESS,
        "Then quaternised with methyl chloride.", wiki=_w, T=90))

_w = W("DTHFP")
split("DTHFP",
      R("DTHFP", "DFP + 4 H2 -> DTHFP", CAT,
        "Both rings hydrogenated: a polymerisation modifier for rubber.", wiki=_w, cat="Ni", T=150))

_w = W("Chlorhexidine")
S(None, "HMBCG", "Hexamethylenebis(cyanoguanidine)", "C10H18N8", "Solid", _w,
  "Hexamethylenediamine built into a cyanoguanidine at each end.",
  smiles="N#CN=C(N)NCCCCCCNC(N)=NC#N")
split("Chlorhexidine",
      R("Hexamethylenebis(cyanoguanidine)", "HMDA + 2 NaDCA + 2 HCl -> HMBCG + 2 NaCl", HEAT,
        "Hexamethylenediamine built into a bis-cyanoguanidine with sodium dicyanamide.", wiki=_w, T=150),
      R("Chlorhexidine", "HMBCG + 2 pChloroaniline -> Chlorhexidine", HEAT,
        "Each end capped with 4-chloroaniline: chlorhexidine, the surgeon's antiseptic.", wiki=_w, T=160))

_w = W("2-Amino-1-butanol")
S(None, "NB2", "2-Nitro-1-butanol", "C4H9NO3", "Liquid", _w,
  "1-Nitropropane with one formaldehyde added (a Henry reaction).", smiles="CCC(CO)[N+](=O)[O-]")
split("2-Amino-1-butanol",
      R("2-Nitro-1-butanol", "NitroPropane1 + CH2O -> NB2", MIX,
        "A Henry reaction of 1-nitropropane with formaldehyde.", wiki=_w),
      R("2-Amino-1-butanol", "NB2 + 3 H2 -> AminoButanol2 + 2 H2O", CAT,
        "The nitro group hydrogenated: the amino alcohol of the tuberculosis drug ethambutol.", wiki=_w,
        cat="Ni", T=80))

_w = W("AEPD")
S(None, "ENPD", "2-Ethyl-2-nitro-1,3-propanediol", "C5H11NO4", "Solid", _w,
  "1-Nitropropane with two formaldehydes added.", smiles="CCC(CO)(CO)[N+](=O)[O-]")
split("AEPD",
      R("2-Ethyl-2-nitro-1,3-propanediol", "NitroPropane1 + 2 CH2O -> ENPD", FLASK,
        "1-Nitropropane takes two formaldehydes, warmed with a little base.", wiki=_w, T=40),
      R("AEPD", "ENPD + 3 H2 -> AEPD + 2 H2O", HIGHP,
        "The nitro group hydrogenated under pressure.", wiki=_w, cat="Ni", T=80, P=30))

_w = W("Probenecid")
S(None, "DPTS", "N,N-Dipropyl-p-toluenesulfonamide", "C13H21NO2S", "Solid", _w,
  "Tosyl chloride on dipropylamine.", smiles="CCCN(CCC)S(=O)(=O)c1ccc(C)cc1")
split("Probenecid",
      R("Dipropyltoluenesulfonamide", "TsCl + Dipropylamine -> DPTS + HCl", MIX,
        "Tosyl chloride on dipropylamine.", wiki=_w),
      R("Probenecid", "2 DPTS + 3 O2 -> 2 Probenecid + 2 H2O", FLASK,
        "The methyl group oxidised to the acid: probenecid, which keeps penicillin in the blood longer.",
        wiki=_w, T=90))

_w = W("Bisacodyl")
S(None, "DesAcBis", "Desacetylbisacodyl", "C18H15NO2", "Solid", _w,
  "Two phenols condensed onto pyridine-2-carbaldehyde.", smiles="Oc1ccc(cc1)C(c1ccc(O)cc1)c1ccccn1")
split("Bisacodyl",
      R("Desacetylbisacodyl", "Py2CHO + 2 Phenol -> DesAcBis + H2O", FLASK,
        "Two phenols condensed onto the aldehyde in acid.", wiki=_w, T=30),
      R("Bisacodyl", "DesAcBis + 2 AceticAnhydride -> Bisacodyl + 2 AcOH", FLASK,
        "Both phenols acetylated: the laxative bisacodyl.", wiki=_w, T=90))

S(None, "BTCA", "Benzophenonetetracarboxylic Acid", "C17H10O9", "Solid", W("BTDA"),
  "Four acids on a benzophenone: dehydrated, the dianhydride of heat-proof polyimides.", lib=4683,
  smiles="OC(=O)c1ccc(cc1C(O)=O)C(=O)c1ccc(C(O)=O)c(c1)C(O)=O")
split("BTDA",
      R("Benzophenonetetracarboxylic Acid", "2 DXE + 17 O2 -> 2 BTCA + 2 CO2 + 12 H2O", CAT,
        "The four methyls oxidised to acids and the bridge to a ketone.", wiki=W("BTDA"), cat="Co", T=200),
      R("BTDA", "BTCA -> BTDA + 2 H2O", HEAT,
        "Heated until both anhydrides close.", wiki=W("BTDA"), T=250))

_w = W("2,4-Dichloroaniline")
S(None, "DCAA", "2,4-Dichloroacetanilide", "C8H7Cl2NO", "Solid", _w,
  "Acetanilide chlorinated at both open activated positions.", smiles="CC(=O)Nc1ccc(Cl)cc1Cl")
split("2,4-Dichloroaniline",
      R("2,4-Dichloroacetanilide", "Acetanilide + 2 Cl2 -> DCAA + 2 HCl", FLASK,
        "Acetanilide chlorinated; the acetyl group keeps the amine from being oxidised.", wiki=_w, T=40),
      R("2,4-Dichloroaniline", "DCAA + H2O -> DCA24 + AcOH", HEAT,
        "Then the acetyl group hydrolysed off.", wiki=_w, T=100))

_w = W("2,6-Dichloroaniline")
S(None, "DCSA", "3,5-Dichlorosulfanilamide", "C6H6Cl2N2O2S", "Solid", _w,
  "Sulfanilamide chlorinated at both places beside its amine.", smiles="NS(=O)(=O)c1cc(Cl)c(N)c(Cl)c1")
split("2,6-Dichloroaniline",
      R("3,5-Dichlorosulfanilamide", "Sulfanilamide + 2 Cl2 -> DCSA + 2 HCl", FLASK,
        "The sulfonamide blocks the para position while both ortho positions are chlorinated.", wiki=_w, T=30),
      R("2,6-Dichloroaniline", "DCSA + 2 H2O -> DCA26 + NH4HSO4", HEAT,
        "Then the sulfonamide hydrolysed off: the aniline of diclofenac.", wiki=_w, T=160))

_w = W("2,5-Dimethylhexanediol")
S(None, "DMHYD", "2,5-Dimethyl-3-hexyne-2,5-diol", "C8H14O2", "Solid", _w,
  "Acetylene ethynylated at both ends with acetone: an alkyne diol.", lib=3650, smiles="CC(C)(O)C#CC(C)(C)O")
split("2,5-Dimethylhexanediol",
      R("Dimethylhexynediol", "Acetylene + 2 Acetone + KOH -> DMHYD + KOH", PRESS,
        "Acetylene ethynylated at both ends with acetone in caustic potash (Favorsky).", wiki=_w, T=40),
      R("2,5-Dimethylhexanediol", "DMHYD + 2 H2 -> DMHD", CAT,
        "The triple bond hydrogenated.", wiki=_w, cat="Ni", T=100))

_w = W("Aziridine")
S(None, "AEHS", "2-Aminoethyl Hydrogen Sulfate", "C2H7NO4S", "Solid", _w,
  "Ethanolamine sulfated: Wenker's intermediate.", smiles="NCCOS(=O)(=O)O")
split("Aziridine",
      R("2-Aminoethyl Hydrogen Sulfate", "MEA + H2SO4 -> AEHS + H2O", HEAT,
        "Ethanolamine sulfated, the water driven off.", wiki=_w, T=200),
      R("Aziridine", "AEHS + 2 NaOH -> Aziridine + Na2SO4 + 2 H2O", MIX,
        "Wenker's synthesis (1935): caustic closes the three-membered ring.", wiki=_w))

_w = W("Acetazolamide")
S(None, "AZSC", "Acetamidothiadiazolesulfonyl Chloride", "C4H4ClN3O3S2", "Solid", _w,
  "The thiol chlorinated in water to a sulfonyl chloride.", smiles="CC(=O)Nc1nnc(s1)S(Cl)(=O)=O")
split("Acetazolamide",
      R("Acetazolamide Sulfonyl Chloride", "AcAMT + 3 Cl2 + 2 H2O -> AZSC + 5 HCl", COOL,
        "The thiol chlorinated in cold water to the sulfonyl chloride.", wiki=_w),
      R("Acetazolamide", "AZSC + 2 NH3 -> Acetazolamide + NH4Cl", MIX,
        "Then aminated: acetazolamide, for glaucoma and mountain sickness.", wiki=_w))

_w = W("Rhodium Nitrate")
S(None, "RhOH3", "Rhodium(III) Hydroxide", "RhH3O3", "Solid", _w,
  "Rhodium hydroxide precipitated from the chloride: washed free of chlorine, it dissolves in nitric "
  "acid.")
split("Rhodium Nitrate",
      R("Rhodium(III) Hydroxide", "RhCl3 + 3 NaOH -> RhOH3 + 3 NaCl", MIX,
        "Rhodium hydroxide precipitated and washed free of chloride.", wiki=_w),
      R("Rhodium Nitrate", "RhOH3 + 3 HNO3 -> RhNO33 + 3 H2O", FLASK,
        "Dissolved in nitric acid: the rhodium salt for catalytic converters.", wiki=_w, T=60))

_w = W("Stabaxol")
S(None, "DIPPI", "2,6-Diisopropylphenyl Isocyanate", "C13H17NO", "Liquid", _w,
  "The aniline phosgenated: an isocyanate crowded by its two isopropyl groups.",
  smiles="CC(C)c1cccc(C(C)C)c1N=C=O")
split("Stabaxol",
      R("2,6-Diisopropylphenyl Isocyanate", "DIPA26 + COCl2 -> DIPPI + 2 HCl", FLASK,
        "The aniline phosgenated to its isocyanate.", wiki=_w, T=120),
      R("Stabaxol", "2 DIPPI -> Stabaxol + CO2", HEAT,
        "A phospholene oxide joins two isocyanates into a carbodiimide, giving off carbon dioxide: it "
        "protects polyester plastics from water.", wiki=_w, T=150))

_w = W("3-Chloropropyltrimethoxysilane")
S(None, "CPTCS", "3-Chloropropyltrichlorosilane", "C3H6Cl4Si", "Liquid", _w,
  "Trichlorosilane added to allyl chloride.", smiles="ClCCC[Si](Cl)(Cl)Cl")
split("3-Chloropropyltrimethoxysilane",
      R("3-Chloropropyltrichlorosilane", "AllylChloride + HSiCl3 -> CPTCS", CAT,
        "Trichlorosilane added to allyl chloride over platinum.", wiki=_w, cat="Pt", T=100),
      R("3-Chloropropyltrimethoxysilane", "CPTCS + 3 Methanol -> CPTMS + 3 HCl", FLASK,
        "The chlorines on silicon swapped for methoxy groups.", wiki=_w, T=60))

_w = W("Ethylbenzylanilinesulfonic Acid")
S(None, "NEBA", "N-Ethyl-N-benzylaniline", "C15H17N", "Liquid", _w,
  "N-Ethylaniline benzylated.", smiles="CCN(Cc1ccccc1)c1ccccc1")
split("Ethylbenzylanilinesulfonic Acid",
      R("N-Ethyl-N-benzylaniline", "NEthylaniline + BenzylChloride -> NEBA + HCl", HEAT,
        "N-Ethylaniline benzylated.", wiki=_w, T=100),
      R("Ethylbenzylanilinesulfonic Acid", "NEBA + SO3 -> EBASA", FLASK,
        "Then the benzyl ring sulfonated: the amine half of Brilliant Blue.", wiki=_w, T=40))

_w = W("Urea-Formaldehyde Resin")
split("Urea-Formaldehyde Resin",
      R("Urea-Formaldehyde Resin", "Methylolurea -> UFResin", POLY,
        "Methylolurea condensed in acid into the hard resin of particleboard glue and electrical fittings.", wiki=_w,
        exact=False))

_w = W("DDQ")
S(None, "DDHQ", "Dichlorodicyanohydroquinone", "C8H2Cl2N2O2", "Solid", _w,
  "Dicyanohydroquinone chlorinated: one oxidation from DDQ.", smiles="N#Cc1c(O)c(Cl)c(Cl)c(O)c1C#N")
split("DDQ",
      R("Dichlorodicyanohydroquinone", "DCHQ + 2 Cl2 -> DDHQ + 2 HCl", FLASK,
        "Dicyanohydroquinone chlorinated.", wiki=_w, T=40),
      R("DDQ", "3 DDHQ + 2 HNO3 -> 3 DDQ + 2 NO + 4 H2O", MIX,
        "Then oxidised by nitric acid to the quinone: DDQ, which strips hydrogen from molecules.", wiki=_w))

_w = W("2,4,5-Trichloroaniline")
S(None, "TCNB", "2,4,5-Trichloronitrobenzene", "C6H2Cl3NO2", "Solid", _w,
  "1,2,4-Trichlorobenzene nitrated.", smiles="O=[N+]([O-])c1cc(Cl)c(Cl)cc1Cl")
split("2,4,5-Trichloroaniline",
      R("2,4,5-Trichloronitrobenzene", "TCB124 + HNO3 -> TCNB + H2O", FLASK,
        "Trichlorobenzene nitrated in mixed acid.", wiki=_w, T=50),
      R("2,4,5-Trichloroaniline", "TCNB + 3 H2 -> TCA245 + 2 H2O", CAT,
        "The nitro group hydrogenated.", wiki=_w, cat="Pd", T=80))

_w = W("5-Chloro-1-indanone")
S(None, "CCPP", "3,4'-Dichloropropiophenone", "C9H8Cl2O", "Solid", _w,
  "Chlorobenzene acylated with 3-chloropropionyl chloride.", smiles="ClCCC(=O)c1ccc(Cl)cc1")
split("5-Chloro-1-indanone",
      R("3,4'-Dichloropropiophenone", "Chlorobenzene + CPC3 -> CCPP + HCl", CAT,
        "Friedel-Crafts acylation.", wiki=_w, cat="AlCl3", T=40),
      R("5-Chloro-1-indanone", "CCPP -> ClIndanone + HCl", CAT,
        "Then the ring closed in hot sulfuric acid.", wiki=_w, cat="H2SO4", T=100))

# two pigments from one transient: dichlorobenzidine's tetrazonium salt
S(None, "DCBT", "Dichlorobenzidine Tetrazonium Chloride", "C12H6Cl4N4", "Aqueous", W("Pigment Yellow 12"),
  "Dichlorobenzidine with both amines diazotised in the cold: it couples at once, or falls apart.",
  smiles="Clc1cc(ccc1[N+]#N)-c1ccc([N+]#N)c(Cl)c1.[Cl-].[Cl-]", props=("IsTransient",))
split("Pigment Yellow 12",
      R("Tetrazotising Dichlorobenzidine", "DCB + 2 NaNO2 + 4 HCl -> DCBT + 2 NaCl + 4 H2O", COOL,
        "Both amines of dichlorobenzidine diazotised in the cold.", wiki=W("Pigment Yellow 12")),
      R("Pigment Yellow 12", "DCBT + 2 Acetoacetanilide -> PY12 + 2 HCl", MIX,
        "Each end coupled with acetoacetanilide: the diarylide yellow of printing inks.",
        wiki=W("Pigment Yellow 12")))
split("Pigment Orange 13",
      R("Pigment Orange 13", "DCBT + 2 Edaravone -> PO13 + 2 HCl", MIX,
        "The tetrazonium salt coupled at each end with a pyrazolone: an orange for inks and plastics.",
        wiki=W("Pigment Orange 13")))

_w = W("Leaf Alcohol")
S(None, "Hexynol3", "3-Hexyn-1-ol", "C6H10O", "Liquid", _w,
  "1-Butyne opening ethylene oxide: an alkyne alcohol.", smiles="CCC#CCCO")
split("Leaf Alcohol",
      R("3-Hexyn-1-ol", "1-Butyne + EO -> Hexynol3", PRESS,
        "1-Butyne's acetylenic end opens ethylene oxide, adding a two-carbon alcohol arm.", wiki=_w, T=30),
      R("Leaf Alcohol", "Hexynol3 + H2 -> LeafAlcohol", CAT,
        "A poisoned Lindlar catalyst adds hydrogen to give only the cis double bond: the smell of cut "
        "grass.", wiki=_w, cat="Pd", T=25))

# --------------------------------------------------------------------------------------------------
# Frontier
# --------------------------------------------------------------------------------------------------
_w = W("Trifluoroacetic Acid")
S(None, "TFAF", "Trifluoroacetyl Fluoride", "C2F4O", "Gas", _w,
  "Acetyl chloride with every hydrogen and the chlorine replaced by fluorine.", smiles="O=C(F)C(F)(F)F")
split("Trifluoroacetic Acid",
      R("Trifluoroacetyl Fluoride", "AcetylChloride + 4 HF -> TFAF + HCl + 3 H2", ECELL,
        "Simons electrochemical fluorination of acetyl chloride in liquid hydrogen fluoride.", wiki=_w),
      R("Trifluoroacetic Acid", "TFAF + H2O -> TFA + HF", MIX,
        "The acid fluoride hydrolysed: a strong organic acid that peptide chemists use by the litre.",
        wiki=_w))

# GenX: its two steps (the acid fluoride, then its hydrolysis) are already written (canon part 23)
split("GenX")

_w = W("Triflic Acid")
split("Triflic Acid",
      R("Triflic Acid", "TfF + H2O -> TfOH + HF", MIX,
        "Triflyl fluoride hydrolysed: triflic acid, a thousand times stronger than sulfuric.", wiki=_w))

S(None, "Guaethol", "Guaethol", "C8H10O2", "Liquid", W("Ethylvanillin"),
  "Catechol with one -OH ethylated: 2-ethoxyphenol.", lib=8792, smiles="CCOc1ccccc1O")
split("Ethylvanillin",
      R("Guaethol", "Catechol + EtCl -> Guaethol + HCl", FLASK,
        "Catechol ethylated once.", wiki=W("Ethylvanillin"), T=120),
      R("Ethylvanillin", "2 Guaethol + 2 GlyoxylicAcid + O2 -> 2 Ethylvanillin + 2 CO2 + 2 H2O", HEAT,
        "Guaethol condensed with glyoxylic acid, then oxidised and decarboxylated: a vanilla three times "
        "stronger than vanillin.", wiki=W("Ethylvanillin"), T=90))

S(None, "DMDA", "Dimethyldodecylamine", "C14H31N", "Liquid", W("Amine Oxide"),
  "Lauryl alcohol aminated with dimethylamine: the tertiary amine behind several surfactants.",
  smiles="CCCCCCCCCCCCN(C)C")
split("Amine Oxide",
      R("Dimethyldodecylamine", "Dodecanol + Me2NH -> DMDA + H2O", CAT,
        "Dodecanol aminated with dimethylamine over copper chromite.", wiki=W("Amine Oxide"),
        cat="CopperChromite", T=220),
      R("Amine Oxide", "DMDA + H2O2 -> LDAO + H2O", FLASK,
        "The amine oxidised by hydrogen peroxide: a foam booster in dishwashing liquid.", wiki=W("Amine Oxide"),
        T=60))
split("Dodecyltrimethylammonium Bromide",
      R("Dodecyltrimethylammonium Bromide", "DMDA + MeBr -> DTAB", PRESS,
        "Dimethyldodecylamine quaternised with methyl bromide.", wiki=W("Dodecyltrimethylammonium Bromide"), T=60))

split("Alkylbenzene Sulfonate",
      R("Alkylbenzene Sulfonate", "DDBSA + NaOH -> SDBS + H2O", MIX,
        "LAS acid neutralised with caustic soda: the main detergent in washing powder.",
        wiki=W("Alkylbenzene Sulfonate")))

_w = W("Fabric Softener")
split("Fabric Softener",
      R("Fabric Softener", "M2HT + CH3Cl -> DSDMAC", PRESS,
        "Methyl distearylamine quaternised with methyl chloride: the softener's cationic surfactant.", wiki=_w,
        T=90))

_w = W("Vinylene Carbonate")
S(None, "CEC", "Chloroethylene Carbonate", "C3H3ClO3", "Liquid", _w,
  "Ethylene carbonate chlorinated in light.", smiles="ClC1COC(=O)O1")
split("Vinylene Carbonate",
      R("Chloroethylene Carbonate", "EthyleneCarbonate + Cl2 -> CEC + HCl", LIGHT,
        "Ethylene carbonate chlorinated in light.", wiki=_w),
      R("Vinylene Carbonate", "CEC + Et3N -> VinyleneCarbonate + HCl + Et3N", MIX,
        "Triethylamine takes hydrogen chloride off: an additive that lets lithium-ion cells last.", wiki=_w))

_w = W("Aldehyde C-12 MNA")
S(None, "MethyleneUndecanal", "2-Methyleneundecanal", "C12H22O", "Liquid", _w,
  "Undecanal condensed with formaldehyde.", smiles="CCCCCCCCCC(=C)C=O")
split("Aldehyde C-12 MNA",
      R("2-Methyleneundecanal", "Undecanal + CH2O -> MethyleneUndecanal + H2O", FLASK,
        "Undecanal condensed with formaldehyde.", wiki=_w, T=90),
      R("Aldehyde C-12 MNA", "MethyleneUndecanal + H2 -> MNA", CAT,
        "Then the double bond hydrogenated: the ambergris-and-incense aldehyde of Chanel No. 5's era.",
        wiki=_w, cat="Pd", T=60))

_w = W("Didecyldimethylammonium Chloride")
S(None, "MDDA", "Methyldidecylamine", "C21H45N", "Liquid", _w,
  "Methylamine with two decyl chains.", smiles="CCCCCCCCCCN(C)CCCCCCCCCC")
split("Didecyldimethylammonium Chloride",
      R("Methyldidecylamine", "2 Decanol + Methylamine -> MDDA + 2 H2O", CAT,
        "Methylamine takes two decyl chains.", wiki=_w, cat="CopperChromite", T=220),
      R("Didecyldimethylammonium Chloride", "MDDA + CH3Cl -> DDAC", PRESS,
        "Methyl chloride then quaternises the amine: a disinfectant and wood preservative.", wiki=_w, T=90))

_w = W("Cetrimonium Chloride")
S(None, "DMHDA", "Dimethylhexadecylamine", "C18H39N", "Liquid", _w,
  "Cetyl alcohol aminated with dimethylamine.", smiles="CCCCCCCCCCCCCCCCN(C)C")
split("Cetrimonium Chloride",
      R("Dimethylhexadecylamine", "CetylAlcohol + Me2NH -> DMHDA + H2O", CAT,
        "Cetyl alcohol aminated with dimethylamine.", wiki=_w, cat="CopperChromite", T=220),
      R("Cetrimonium Chloride", "DMHDA + CH3Cl -> CTAC", PRESS,
        "Then quaternised with methyl chloride: the conditioner in hair conditioner.", wiki=_w, T=90))

_w = W("Cetrimonium Bromide")
S(None, "CetylBromide", "Cetyl Bromide", "C16H33Br", "Liquid", _w,
  "Cetyl alcohol with hydrobromic acid: 1-bromohexadecane.", smiles="CCCCCCCCCCCCCCCCBr")
split("Cetrimonium Bromide",
      R("Cetyl Bromide", "CetylAlcohol + HBr -> CetylBromide + H2O", FLASK,
        "Cetyl bromide from the alcohol and hydrobromic acid.", wiki=_w, T=100),
      R("Cetrimonium Bromide", "CetylBromide + Me3N -> CTAB", MIX,
        "Then trimethylamine: CTAB, the surfactant that shapes gold nanorods.", wiki=_w))

_w = W("Oxo Tridecanol")
S(None, "Tridecanal", "Tridecanal", "C13H26O", "Liquid", _w,
  "Dodecene with a CHO added by synthesis gas.", smiles="CCCCCCCCCCCCC=O")
split("Oxo Tridecanol",
      R("Tridecanal", "Dodecene + CO + H2 -> Tridecanal", HIGHP,
        "Hydroformylation: synthesis gas adds a CHO to the olefin.", wiki=_w, cat="Co", T=160, P=200),
      R("Oxo Tridecanol", "Tridecanal + H2 -> Tridecanol", CAT,
        "Then the aldehyde hydrogenated: the alcohol of detergent ethoxylates.", wiki=_w, cat="Ni", T=150))

# every step above was written with the canon's R, so settling moves it, and only it, into the era
# where its inputs first exist
settle_eras()

# a milestone among the new steps, so no stretch of the eras goes too long without one
import authored_content as _C  # noqa: E402
from gen_authored import Milestone  # noqa: E402
_C.MILESTONES += [
    Milestone("Isoniazid", message="Isoniazid (1952): with streptomycin, tuberculosis, the great killer of the 1800s, "
              "becomes curable."),
]
