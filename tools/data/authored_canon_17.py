"""
Curieosity's industrial chemistry, part 17 (see authored_canon.py): colour and scent. Pigments
and dyes from the coal-tar amines, the fragrance chemicals of modern perfumery, and a handful of
specialty chemicals set aside for their long routes. A dye is made in several steps; each is
written here as one balanced reaction whose description names the steps. One new raw material:
citronella oil.
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E4, E5, E6, RAW  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)
import authored_content as _C

# --- a new raw material: citronella oil, granted with the other essential oils ----------------
RAW("CitronellaOil", "Citronella Oil", "Steam-distilled from Cymbopogon grasses; its lemony citronellal keeps "
    "mosquitoes away.", "Citronella_oil", "#b8c040", state="Liquid")
for _m in _C.MILESTONES:
    if _m.on == "Ethanol" and "CitronellaOil" not in _m.grant:
        _m.grant = tuple(_m.grant) + ("CitronellaOil",)

# --- intermediates -----------------------------------------------------------------------
S(None, "Phenylhydrazine", "Phenylhydrazine", "C6H8N2", "Liquid", "Phenylhydrazine",
  "Emil Fischer's reagent (1875), with which he sorted out the sugars; the start of pyrazolone dyes and drugs.",
  smiles="NNc1ccccc1")
S(None, "Edaravone", "1-Phenyl-3-methyl-5-pyrazolone", "C10H10N2O", "Solid", "Edaravone",
  "Knorr's pyrazolone (1883): a coupling component for yellow and orange dyes, and the stroke drug edaravone.",
  smiles="CC1=NN(C(=O)C1)c1ccccc1")
S(None, "Benzodioxole", "1,3-Benzodioxole", "C7H6O2", "Liquid", "1,3-Benzodioxole",
  "Catechol with its two oxygens tied by one carbon; the core of safrole, piperonal and many natural scents.",
  smiles="C1Oc2ccccc2O1")
S(None, "Citronellal", "Citronellal", "C10H18O", "Liquid", "Citronellal",
  "The lemony aldehyde of citronella oil; ring-closed, it becomes isopulegol and then menthol.",
  smiles="CC(C)=CCCC(C)CC=O")

# --- the canon substances ------------------------------------------------------------------
S("3520-72-7", "PO13", "Pigment Orange 13", "C32H24Cl2N8O2", "Solid", 64310771,
  "Pyrazolone orange: dichlorobenzidine coupled with two pyrazolones, for inks, plastics and rubber.", lib=5454)
S("36888-99-0", "PY139", "Pigment Yellow 139", "C16H9N5O6", "Solid", 45594795,
  "An isoindoline yellow, reddish and opaque, that stands up to weather on cars and in paints.", lib=5557)
S("1047-16-1", "Quinacridone", "Quinacridone", "C20H12N2O2", "Solid", 1548303,
  "Pigment Violet 19, the bright magenta-red of car paints and artists' 'quinacridone rose'.", lib=2314)
S("10101-66-3", "ManganeseViolet", "Manganese violet", "NH4MnP2O7", "Solid", 41467423,
  "An artists' violet first made in 1868: manganese(III) in ammonium pyrophosphate.", lib=2125)
S("8004-92-0", "QuinolineYellowWS", "Quinoline Yellow WS", "C18H9NNa2O8S2", "Solid", 219340,
  "Food yellow E104: a sulfonated quinophthalone that colours drinks, sweets and medicines.", lib=8291)
S("92-43-3", "Phenidone", "Phenidone", "C9H10N2O", "Solid", 15374963,
  "Ilford's photographic developer (1940s), five to ten times stronger than metol.", lib=8714)
S("24851-98-7", "Hedione", "Hedione", "C13H22O3", "Liquid", 20668735,
  "Methyl dihydrojasmonate (Firmenich, 1962): a soft jasmine glow, first worn in Dior's Eau Sauvage (1966).",
  lib=4691)
S("1222-05-5", "Galaxolide", "Galaxolide", "C18H26O", "Solid", 34659902,
  "A clean polycyclic musk (IFF, 1965), the smell of laundry detergent.", lib=3037)
S("33704-61-9", "Cashmeran", "Cashmeran", "C14H22O", "Solid", 43798141,
  "A musky, spicy, woody note meant to smell like cashmere wool.", lib=5383)
S("120-57-0", "Piperonal", "Piperonal", "C8H6O3", "Solid", 1751880,
  "Heliotropin: the cherry-almond smell of heliotrope flowers.", lib=2893)
S("1205-17-0", "Helional", "Helional", "C11H12O3", "Liquid", 31389323,
  "A fresh, watery-green floral aldehyde, the 'ozone' of 1990s perfumes.", lib=2953)
S("107-75-5", "Hydroxycitronellal", "Hydroxycitronellal", "C10H20O2", "Liquid", 48952167,
  "The scent of lily of the valley; the flower itself yields no oil.", lib=2464)
S("928-96-1", "LeafAlcohol", "cis-3-Hexen-1-ol", "C6H12O", "Liquid", 1585875,
  "Leaf alcohol: the smell of freshly cut grass, released by torn leaves.", lib=8744)
S("70693-62-8", "Oxone", "Oxone", "K5H3S4O18", "Solid", "Potassium_peroxymonosulfate",
  "The triple salt 2KHSO5.KHSO4.K2SO4: a stable, dry oxidiser for pools, dentures and organic chemists.",
  lib=7671)
S("2386-87-0", "ERL4221", "3,4-Epoxycyclohexylmethyl 3,4-epoxycyclohexanecarboxylate", "C14H20O4", "Liquid",
  46261390, "A cycloaliphatic epoxy resin, cured by light or acid for coatings and electronics.", lib=4608)
S("10254-57-6", "Vanlube7723", "Methylenebis(dibutyldithiocarbamate)", "C19H38N2S4", "Liquid", 56056679,
  "An antioxidant and anti-wear additive for lubricating oils.", lib=2195)
S("29806-73-3", "OctylPalmitate", "Ethylhexyl palmitate", "C24H48O2", "Liquid", 4829062,
  "A light, dry-feeling oil for creams, used where spermaceti once was.", lib=5137)
S("21245-02-3", "PadimateO", "Padimate O", "C17H27NO2", "Liquid", 4297266,
  "A UVB filter from the PABA family, common in sunscreens of the 1980s.", lib=4448)
S("2682-20-4", "MIT", "Methylisothiazolinone", "C4H5NOS", "Solid", 368356,
  "A preservative in shampoos and paints; the cause of a wave of contact allergies in the 2010s.", lib=4920)
S("2997-92-4", "AAPH", "AAPH", "C8H20Cl2N6", "Solid", 35625740,
  "2,2'-Azobis(2-amidinopropane) dihydrochloride, a water-soluble radical initiator.", lib=5147)
S("12007-92-0", "NaPentaborate", "Sodium pentaborate", "NaB5O8", "Solid", 71174336,
  "A borate richer in boron than borax, for fire retardants and fertiliser.", lib=2917)
S("1653-19-6", "DCBD", "2,3-Dichloro-1,3-butadiene", "C4H4Cl2", "Liquid", 60110175,
  "Copolymerised with chloroprene, it keeps neoprene from crystallising in the cold.", lib=4041)
S("5384-21-4", "BXM", "Bis(3,5-dimethyl-4-hydroxyphenyl)methane", "C17H20O2", "Solid", 62913193,
  "A bisphenol for heat-resistant polymers.", lib=6338)
S("1446-61-3", "DHAA", "Dehydroabietylamine", "C20H31N", "Solid", 39441867,
  "An amine made from pine rosin, used to separate mirror-image acids.", lib=3723)


# --- the reactions -------------------------------------------------------------------------
E4.reactions += [
    R("Fischer's Phenylhydrazine", "Aniline + NaNO2 + HCl + 2 Na2SO3 -> Phenylhydrazine + NaCl + 2 Na2SO4", FLASK,
      "Emil Fischer (1875): aniline diazotised, and the diazonium salt reduced with sodium sulfite.",
      wiki="Phenylhydrazine", T=5),
    R("Knorr's Pyrazolone", "Phenylhydrazine + EthylAcetoacetate -> Edaravone + Ethanol + H2O", FLASK,
      "Ludwig Knorr (1883) condensed phenylhydrazine with ethyl acetoacetate into a pyrazolone ring.",
      wiki="Edaravone", T=80),
    R("Pigment Orange 13", "DCB + 2 NaNO2 + 2 HCl + 2 Edaravone -> PO13 + 2 NaCl + 4 H2O", COOL,
      "Dichlorobenzidine tetrazotised in the cold, then each end coupled with a pyrazolone.", wiki=64310771, T=5),
    R("Quinoline Yellow", "Quinaldine + PhthalicAnhydride + 2 SO3 + 2 NaOH -> QuinolineYellowWS + 3 H2O",
      HEAT, "Quinaldine fused with phthalic anhydride to quinophthalone, sulfonated in oleum and neutralised.",
      wiki=219340, T=200),
    R("Manganese Violet", "4 MnO2 + 4 NH3 + 8 H3PO4 -> 4 ManganeseViolet + 10 H2O + O2", HEAT,
      "Manganese dioxide baked with ammonium phosphate and phosphoric acid until violet.",
      wiki=41467423, T=300),
    R("1,3-Benzodioxole", "Catechol + CH2Cl2 + 2 NaOH -> Benzodioxole + 2 NaCl + 2 H2O", FLASK,
      "Catechol's two oxygens tied together by dichloromethane.", wiki="1,3-Benzodioxole", T=110),
    R("Citronellal", "CitronellaOil -> Citronellal", DISTIL,
      "Citronellal fractionated from citronella oil.", wiki="Citronellal", exact=False),
    R("Leaf Alcohol", "1-Butyne + EO + H2 -> LeafAlcohol", CAT,
      "1-Butyne opens ethylene oxide to hexynol; a poisoned Lindlar catalyst then adds hydrogen to give "
      "only the cis double bond.", wiki=1585875, cat="Pd", T=25),
    R("Caro's Acid Triple Salt", "2 H2O2 + 4 H2SO4 + 5 KOH -> Oxone + 7 H2O", COOL,
      "Hydrogen peroxide and oleum make Caro's acid, partly neutralised with potash and crystallised.",
      wiki="Potassium_peroxymonosulfate", T=10),
    R("Sodium Pentaborate", "Borax + 6 H3BO3 -> 2 NaPentaborate + 19 H2O", HEAT,
      "Borax and boric acid dissolved together and dried.", wiki=71174336, T=150),
    R("Octyl Palmitate", "PalmiticAcid + 2EH -> OctylPalmitate + H2O", CAT,
      "Palmitic acid esterified with 2-ethylhexanol.", wiki=4829062, cat="H2SO4", T=180),
    R("Dehydroabietylamine", "Rosin + NH3 + H2 -> DHAA + 2 H2O", HIGHP,
      "Rosin's acid made into a nitrile with ammonia and hydrogenated; its ring loses hydrogen on the way "
      "and turns aromatic.", wiki=39441867, cat="Ni", T=300),
]
E5.reactions += [
    R("Phenidone", "Phenylhydrazine + AcrylicAcid -> Phenidone + H2O", FLASK,
      "Phenylhydrazine adds to acrylic acid and closes into a pyrazolidinone.", wiki=15374963, T=100),
    R("Pigment Yellow 139", "Phthalonitrile + 2 BarbituricAcid -> PY139 + NH3", FLASK,
      "Ammonia turns phthalonitrile into diiminoisoindoline, whose two imines condense with barbituric acid.",
      wiki=45594795, T=90),
    R("Quinacridone", "4 Succinic + 4 Aniline + O2 -> 2 Quinacridone + 14 H2O", HEAT,
      "Succinic ester self-condenses into a ring, takes two anilines, is oxidised to the terephthalic acid "
      "and closed twice in polyphosphoric acid.", wiki=1548303, T=250),
    R("Hedione", "Cyclopentanone + Pentanal + DimethylMalonate -> Hedione + Methanol + CO2", FLASK,
      "Cyclopentanone and pentanal give pentylcyclopentenone; dimethyl malonate adds to it and one ester "
      "falls off (Firmenich, 1962).", wiki=20668735, T=150),
    R("Galaxolide", "AMS + Isoamylene + PO + CH2O -> Galaxolide + H2O", FLASK,
      "alpha-Methylstyrene and isoamylene close into pentamethylindane, which takes propylene oxide and is "
      "ring-closed by formaldehyde.", wiki=34659902, T=60),
    R("Cashmeran", "AMS + Isoamylene + 2 H2 + O2 -> Cashmeran + H2O", HIGHP,
      "The same pentamethylindane, half hydrogenated, then oxidised to the ketone.", wiki=43798141,
      cat="Pd", T=150),
    R("Piperonal", "2 Benzodioxole + 2 GlyoxylicAcid + O2 -> 2 Piperonal + 2 CO2 + 2 H2O", FLASK,
      "Benzodioxole condensed with glyoxylic acid, then oxidised and decarboxylated, as for vanillin.",
      wiki=1751880, T=60),
    R("Helional", "Piperonal + Propanal + H2 -> Helional + H2O", CAT,
      "Piperonal condensed with propanal, then the double bond hydrogenated.", wiki=31389323, cat="Pd", T=80),
    R("Hydroxycitronellal", "Citronellal + H2O -> Hydroxycitronellal", FLASK,
      "The aldehyde protected as its bisulfite adduct while acid adds water across the double bond.",
      wiki=48952167, T=20),
    R("Cycloaliphatic Epoxy", "2 Butadiene + 2 Acrolein + 2 PAA -> ERL4221 + 2 AcOH", FLASK,
      "Butadiene and acrolein give tetrahydrobenzaldehyde; two of these join into an ester (Tishchenko); "
      "peracetic acid epoxidises both rings.", wiki=46261390, T=40),
    R("Vanlube 7723", "2 Dibutylamine + 2 CS2 + CH2Cl2 + 2 NaOH -> Vanlube7723 + 2 NaCl + 2 H2O", FLASK,
      "Two dithiocarbamates, from dibutylamine and carbon disulfide, bridged by dichloromethane.",
      wiki=56056679, T=50),
    R("Padimate O", "Dimethylaniline + COCl2 + 2EH -> PadimateO + 2 HCl", FLASK,
      "Phosgene acylates dimethylaniline at the para position; 2-ethylhexanol makes the ester.",
      wiki=4297266, T=50),
    R("Methylisothiazolinone", "MPA3 + Methylamine + 2 Cl2 -> MIT + H2O + 4 HCl", FLASK,
      "Mercaptopropionic acid made into its methylamide; chlorine closes the S-N ring.", wiki=368356, T=10),
    R("AAPH", "AIBN + 2 NH3 + 2 HCl -> AAPH", FLASK,
      "A Pinner reaction turns both nitriles of AIBN into amidine hydrochlorides.", wiki=35625740, T=20),
    R("2,3-Dichlorobutadiene", "Chloroprene + Cl2 -> DCBD + HCl", FLASK,
      "Chloroprene chlorinated, then dehydrochlorinated.", wiki=60110175, T=40),
    R("Xylenol Methylene Bisphenol", "2 DMP26 + CH2O -> BXM + H2O", FLASK,
      "Two 2,6-xylenols joined at their free para positions by formaldehyde.", wiki=62913193, T=80),
]

import authored_canon_18  # noqa: E402,F401
