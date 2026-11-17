"""
Curieosity's industrial chemistry, part 7 (see authored_canon.py).
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E1, E3, E4, E5, E6  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)


# --- intermediates the canon set lacks ---------------------------------------------------
S(None, "CDT", "Cyclododecatriene", "C12H18", "Liquid", "Cyclododecatriene",
  "Three butadienes joined into a twelve-membered ring on a nickel or titanium catalyst (Wilke, 1950s): the start of nylon 12.",
  smiles="C1=CCCC=CCCC=CCC1")
S(None, "BuCl", "1-Chlorobutane", "C4H9Cl", "Liquid", "1-Chlorobutane",
  "Butyl chloride, made from butanol and hydrogen chloride, the start of butyllithium.", smiles="CCCCCl")

# --- the canon substances ------------------------------------------------------------------
S("80-08-0", "Dapsone", "Dapsone", "C12H12N2O2S", "Solid", 660116,
  "The drug that, with rifampicin and clofazimine, cures leprosy. First made in 1908, used against it from the 1940s.", lib=8270)
S("80-43-3", "DiCumylPeroxide", "Dicumyl peroxide", "C18H22O2", "Solid", 72125412,
  "The peroxide that crosslinks polyethylene cable insulation and EPDM rubber when heated.", lib=8276)
S("827-52-1", "CHB", "Cyclohexylbenzene", "C12H16", "Liquid", 62414403,
  "An overcharge-protection additive in lithium-ion batteries, and a route to phenol without acetone.", lib=8379)
S("85-43-8", "THPA", "Tetrahydrophthalic anhydride", "C8H8O3", "Solid", 56748630,
  "Butadiene and maleic anhydride's Diels-Alder adduct: an epoxy hardener and the start of the fungicide captan.", lib=8460)
S("85-68-7", "BBP", "Benzyl butyl phthalate", "C19H20O4", "Liquid", 3007126,
  "A plasticiser for vinyl flooring, now restricted in Europe.", lib=8462)
S("865-33-8", "KOMe", "Potassium methoxide", "CH3KO", "Solid", 31598376,
  "A strong base and the catalyst of biodiesel transesterification.", lib=8502)
S("865-47-4", "KOtBu", "Potassium tert-butoxide", "C4H9KO", "Solid", 3314453,
  "A strong, bulky base that pulls protons without adding itself: the organic chemist's favourite for eliminations.", lib=8504)
S("868-85-9", "DMPite", "Dimethyl phosphite", "C2H7O3P", "Liquid", 54488885,
  "A phosphorus building block for glyphosate and flame retardants.", lib=8516)
S("872-36-6", "VinyleneCarbonate", "Vinylene carbonate", "C3H2O3", "Liquid", 57466302,
  "A few percent in lithium-ion electrolyte builds a sturdier protective film on the anode and lengthens battery life.", lib=8543)
S("89-72-5", "sBP2", "2-sec-Butylphenol", "C10H14O", "Liquid", 51491730,
  "A phenol on the way to the herbicide dinoseb and to resins.", lib=8602)
S("88-85-7", "Dinoseb", "Dinoseb", "C10H12N2O5", "Solid", 19505215,
  "A dinitrophenol herbicide banned in the US in 1986 for causing birth defects.", lib=8578)
S("90-72-2", "DMP30", "2,4,6-Tris(dimethylaminomethyl)phenol", "C15H27N3O", "Liquid", 77091094,
  "DMP-30, the accelerator that makes epoxy glue set fast.", lib=8628)
S("92-84-2", "Phenothiazine", "Phenothiazine", "C12H9NS", "Solid", 24857,
  "Bernthsen's 1883 ring, once a livestock dewormer: the parent of chlorpromazine, the first antipsychotic, and an inhibitor that stops acrylic acid polymerising.", lib=8717)
S("92-88-6", "Biphenol", "4,4'-Biphenol", "C12H10O2", "Solid", 6781382,
  "The rigid diol of liquid-crystal polymers and high-heat polysulfones.", lib=8718)
S("920-66-1", "HFIP", "Hexafluoroisopropanol", "C3H2F6O", "Liquid", 1619291,
  "A strongly hydrogen-bonding solvent that dissolves nylons and polyesters, and the core of the anaesthetic sevoflurane.", lib=8719)
S("947-04-6", "Laurolactam", "Laurolactam", "C12H23NO", "Solid", 35551062,
  "A twelve-carbon lactam polymerised into nylon 12, for fuel lines, ski boots and 3D-printing powder.", lib=8808)
S("96-18-4", "TCP123", "1,2,3-Trichloropropane", "C3H5Cl3", "Liquid", 31632161,
  "A by-product of epichlorohydrin, used to make polysulfide sealants; a stubborn groundwater pollutant.", lib=8853)
S("96-23-1", "DCH13", "1,3-Dichloro-2-propanol", "C3H6Cl2O", "Liquid", 56828423,
  "Glycerol's dichlorohydrin, closed with caustic soda into epichlorohydrin (Solvay's Epicerol, 2007).", lib=8855)
S("96-29-7", "MEKO", "Methyl ethyl ketoxime", "C4H9NO", "Liquid", 28168749,
  "The anti-skinning agent that keeps oil paint from forming a crust in the can.", lib=8859)
S("96-47-9", "MeTHF", "2-Methyltetrahydrofuran", "C5H10O", "Liquid", 26970606,
  "A greener, water-immiscible replacement for THF, made from furfural.", lib=8865)
S("960-71-4", "BPh3", "Triphenylborane", "C18H15B", "Solid", 22624569,
  "A Lewis acid promoter in DuPont's hydrocyanation of butadiene to nylon's adiponitrile.", lib=8873)
S("97-63-2", "EMA", "Ethyl methacrylate", "C6H10O2", "Liquid", 61698613,
  "The monomer of acrylic nails, and the sweet, sharp smell of nail salons.", lib=8890)
S("97-72-3", "IsobutyricAnhydride", "Isobutyric anhydride", "C8H14O3", "Liquid", 77694615,
  "An acylating agent for flavours and drugs.", lib=8892)
S("97-99-4", "THFA", "Tetrahydrofurfuryl alcohol", "C5H10O2", "Liquid", 59687464,
  "A solvent made from furfural, for agricultural sprays and cleaners.", lib=8902)
S("98-09-9", "BsCl", "Benzenesulfonyl chloride", "C6H5ClO2S", "Liquid", 43264803,
  "The reagent of the Hinsberg test, and a building block for sulfonamides.", lib=8917)
S("98-13-5", "PhSiCl3", "Phenyltrichlorosilane", "C6H5Cl3Si", "Liquid", 13037086,
  "Phenyl groups in silicone resins make them stand heat.", lib=8918)
S("98-92-0", "Nicotinamide", "Nicotinamide", "C6H6N2O", "Solid", 21968,
  "Vitamin B3 in its amide form, in fortified foods and skin creams.", lib=8933)
S("99-93-4", "HAP", "4'-Hydroxyacetophenone", "C8H8O2", "Solid", 35537702,
  "Celanese's route to paracetamol goes through it (1980s); it is also a skin-care antioxidant.", lib=8964)
S("109-09-1", "ClPyridine", "2-Chloropyridine", "C5H4ClN", "Liquid", 27233882,
  "A building block for antihistamines and the fungicide zinc pyrithione.", lib=2547)
S("111-64-8", "OctanoylCl", "Octanoyl chloride", "C8H15ClO", "Liquid", 54438896,
  "The acid chloride of caprylic acid, for peroxide initiators and surfactants.", lib=2652)
S("12034-39-8", "Na2S4", "Sodium tetrasulfide", "Na2S4", "Solid", 37345312,
  "With ethylene dichloride it made Thiokol (1926), the first American synthetic rubber, later the binder of rocket fuel.", lib=2938)
S("79-24-3", "Nitroethane", "Nitroethane", "C2H5NO2", "Liquid", 6391934,
  "A solvent and building block, nitrated from ethane in the gas phase.", lib=8231)
S("121-82-4", "RDX", "RDX", "C3H6N6O6", "Solid", 7499,
  "Research Department Explosive (Britain, 1940s): more powerful than TNT and the main ingredient of C-4.", lib=2992)
S("100-79-8", "Solketal", "Solketal", "C6H12O3", "Liquid", 4390618,
  "Glycerol protected with acetone: a solvent and fuel additive made from biodiesel's glycerol.", lib=2024)
S("101-83-7", "DCHA", "Dicyclohexylamine", "C12H23N", "Liquid", 44112420,
  "A corrosion inhibitor for steam lines and a rubber accelerator.", lib=2118)
S("102-69-2", "TPrA", "Tripropylamine", "C9H21N", "Liquid", 73626945,
  "A catalyst and corrosion inhibitor, and the start of the zeolite template tetrapropylammonium.", lib=2171)
S("103-09-3", "EHAc", "2-Ethylhexyl acetate", "C10H20O2", "Liquid", 4084502,
  "A slow-evaporating solvent for baking enamels.", lib=2217)
S("106-92-3", "AGE", "Allyl glycidyl ether", "C6H10O2", "Liquid", 46815783,
  "A monomer with both an allyl group and an epoxide, for silane coupling agents and rubbers.", lib=2405)
S("109-72-8", "BuLi", "n-Butyllithium", "C4H9Li", "Liquid", 2057516,
  "The organolithium base that starts solution polymerisation of rubbers, and the strongest base most chemists ever handle.", lib=2564)
S("110-05-4", "DTBPeroxide", "Di-tert-butyl peroxide", "C8H18O2", "Liquid", 3997462,
  "One of the most stable organic peroxides: an initiator for polymerisation and a diesel cetane improver.", lib=2585)
S("110-41-8", "MNA", "2-Methylundecanal", "C12H24O", "Liquid", 22542034,
  "Aldehyde C-12 MNA, the fizzy, metallic top note of Chanel No. 5 (1921).", lib=2598)
S("111-49-9", "Azepane", "Azepane", "C6H13N", "Liquid", 23755808,
  "Hexamethyleneimine, a by-product of nylon's diamine, used for drugs and rubber chemicals.", lib=2647)
S("111-57-9", "SEA", "Stearoyl ethanolamide", "C20H41NO2", "Solid", 40333152,
  "A wax and thickener in creams, and a lipid messenger the body makes itself.", lib=2649)
S("111-96-6", "Diglyme", "Diglyme", "C6H14O3", "Liquid", 5259465,
  "A high-boiling ether solvent that wraps around metal cations, for Grignard and hydride reactions.", lib=2659)
S("1117-86-8", "Octanediol12", "1,2-Octanediol", "C8H18O2", "Liquid", 51597359,
  "Caprylyl glycol, a moisturiser and preservative booster in cosmetics.", lib=2689)
S("112-90-3", "Oleylamine", "Oleylamine", "C18H37N", "Liquid", 32457852,
  "A fatty amine for flotation and corrosion inhibition, and the capping ligand of nanocrystal synthesis.", lib=2733)
S("115-86-6", "TPhP", "Triphenyl phosphate", "C18H15O4P", "Solid", 12938564,
  "A flame retardant for electronics casings and a plasticiser; also in some nail polishes.", lib=2792)
S("120-46-7", "DBM", "Dibenzoylmethane", "C15H12O2", "Solid", 33535660,
  "A beta-diketone that stabilises PVC with zinc and calcium soaps; its relative avobenzone is a UVA filter.", lib=2888)
S("122-62-3", "DEHS", "Bis(2-ethylhexyl) sebacate", "C26H50O4", "Liquid", 4214695,
  "A plasticiser for cold-flexible PVC and a jet-engine lubricant base.", lib=3029)
S("123-11-5", "Anisaldehyde", "Anisaldehyde", "C8H8O2", "Liquid", 3407537,
  "The sweet hay and hawthorn smell of anise and fennel, used in perfumes and flavours.", lib=3062)
S("123-54-6", "AcAc", "Acetylacetone", "C5H8O2", "Liquid", 1558266,
  "A diketone whose enolate grips metals: metal acetylacetonates are catalysts and paint driers.", lib=3077)
S("123-77-3", "ADA", "Azodicarbonamide", "C2H4N4O2", "Solid", 2904705,
  "The blowing agent that foams yoga mats and vinyl wallpaper, once also a flour improver in American bread.", lib=3085)
S("125-12-2", "IsobornylAcetate", "Isobornyl acetate", "C12H20O2", "Liquid", 72377771,
  "The pine-forest smell of bath products, made from turpentine's camphene; hydrolysed it gives isoborneol on the way to camphor.", lib=3128)
S("126-58-9", "DiPE", "Dipentaerythritol", "C10H22O7", "Solid", 78367159,
  "Two pentaerythritols joined by an ether: six alcohol groups for acrylate crosslinkers and fire-retardant coatings.", lib=3161)
S("126-73-8", "TBPhos", "Tributyl phosphate", "C12H27O4P", "Liquid", 1859100,
  "The extractant of the PUREX process that separates uranium and plutonium from spent nuclear fuel.", lib=3163)
S("128-04-1", "NaDMDTC", "Sodium dimethyldithiocarbamate", "C3H6NNaS2", "Solid", 8117552,
  "A biocide and the chelant that precipitates heavy metals from wastewater; also a rubber accelerator.", lib=3215)
S("1330-78-5", "TCPhos", "Tricresyl phosphate", "C21H21O4P", "Liquid", 8700475,
  "An anti-wear additive and flame retardant. Ortho-cresyl contamination caused the 1930 'Ginger Jake' paralysis epidemic.", lib=3376)
S("1338-41-6", "Span60", "Sorbitan monostearate", "C24H46O6", "Solid", 5170103,
  "Span 60 (E491), the emulsifier in dried yeast and cake mixes.", lib=3402)
S("13548-38-4", "CrNO33", "Chromium(III) nitrate", "Cr(NO3)3", "Solid", 14603357,
  "A chromium salt for making catalysts and dyeing textiles.", lib=3468)
S("13598-37-3", "Zn3PO42", "Zinc phosphate", "Zn3(PO4)2", "Solid", 5438215,
  "The corrosion-inhibiting pigment of primers, the conversion coat on steel car bodies, and a dental cement.", lib=8127)
S("140-31-8", "AEP", "Aminoethylpiperazine", "C6H15N3", "Liquid", 10600898,
  "An epoxy hardener that gives tough, flexible cures.", lib=3595)
S("14059-33-7", "BiVO4", "Bismuth vanadate", "BiVO4", "Solid", 37948481,
  "Pigment Yellow 184, a bright, non-toxic yellow that replaced lead and cadmium yellows; also a photocatalyst for splitting water.", lib=3609)
S("149-30-4", "MBT", "2-Mercaptobenzothiazole", "C7H5NS2", "Solid", 49598939,
  "The accelerator that made rubber vulcanisation fast (1920s), still in tyres and gloves.", lib=3799)

E4.reactions += [
    R("Butyl Chloride", "Butanol + HCl -> BuCl + H2O", CAT,
      "Butanol and hydrogen chloride with zinc chloride.", wiki="1-Chlorobutane", cat="ZnCl2", T=100),
    R("Phenothiazine", "Diphenylamine + 2 S -> Phenothiazine + H2S", HEAT,
      "Diphenylamine fused with sulfur (Bernthsen, 1883).", wiki=24857, T=250),
    R("Potassium tert-Butoxide", "2 K + 2 tBuOH -> 2 KOtBu + H2", FLASK,
      "Potassium dissolved in tert-butanol.", wiki=3314453, T=80),
    R("Potassium Methoxide", "KOH + Methanol -> KOMe + H2O", MIX,
      "Caustic potash dissolved in methanol, the water driven off.", wiki=31598376),
    R("Dimethyl Phosphite", "PCl3 + 3 Methanol -> DMPite + CH3Cl + 2 HCl", FLASK,
      "Phosphorus trichloride with methanol.", wiki=54488885, T=20),
    R("Sodium Tetrasulfide", "Na2S + 3 S -> Na2S4", MIX,
      "Sodium sulfide boiled with sulfur.", wiki=37345312),
    R("Nitroethane", "Ethane + HNO3 -> Nitroethane + H2O", HEAT,
      "Ethane nitrated in the gas phase.", wiki=6391934, T=400),
    R("Benzenesulfonyl Chloride", "Benzene + 2 HSO3Cl -> BsCl + H2SO4 + HCl", FLASK,
      "Benzene with excess chlorosulfonic acid.", wiki=43264803, T=30),
    R("Tributyl Phosphate", "POCl3 + 3 Butanol -> TBPhos + 3 HCl", FLASK,
      "Phosphorus oxychloride esterified with butanol.", wiki=1859100, T=40),
    R("Tricresyl Phosphate", "POCl3 + 3 pCresol -> TCPhos + 3 HCl", FLASK,
      "Phosphorus oxychloride esterified with cresol.", wiki=8700475, T=150),
    R("Triphenyl Phosphate", "POCl3 + 3 Phenol -> TPhP + 3 HCl", HEAT,
      "Phosphorus oxychloride esterified with phenol.", wiki=12938564, T=180),
    R("Chromium Nitrate", "Cr2O3 + 6 HNO3 -> 2 CrNO33 + 3 H2O", MIX,
      "Chromium oxide dissolved in nitric acid.", wiki=14603357),
    R("Zinc Phosphate", "3 ZnO + 2 H3PO4 -> Zn3PO42 + 3 H2O", MIX,
      "Zinc oxide and phosphoric acid.", wiki=5438215),
    R("Anisaldehyde", "Anisole + CO -> Anisaldehyde", CAT,
      "Anisole formylated by carbon monoxide (Gattermann-Koch).", wiki=3407537, cat="AlCl3", T=30),
    R("Bismuth Vanadate", "Bi2O3 + V2O5 -> 2 BiVO4", HEAT,
      "Bismuth and vanadium oxides calcined together.", wiki=37948481, T=700),
]
E5.reactions += [
    R("Dapsone", "2 NCB + Na2S + 2 H2O2 + 6 H2 -> Dapsone + 2 NaCl + 6 H2O", CAT,
      "Nitrochlorobenzene joined by sulfide, oxidised to the sulfone, and hydrogenated.", wiki=660116,
      cat="Pd", T=100),
    R("Dicumyl Peroxide", "2 CHP + H2 -> DiCumylPeroxide + 2 H2O", FLASK,
      "Half the cumene hydroperoxide is reduced to cumyl alcohol, which condenses with the rest.", wiki=72125412,
      T=50),
    R("Cyclohexylbenzene", "2 Benzene + 2 H2 -> CHB", HIGHP,
      "Hydroalkylation: benzene half-hydrogenated alkylates more benzene over palladium on a zeolite.", wiki=62414403,
      cat="Pd", T=150),
    R("Tetrahydrophthalic Anhydride", "Butadiene + MaleicAnhydride -> THPA", PRESS,
      "The textbook Diels-Alder reaction.", wiki=56748630, T=100),
    R("Benzyl Butyl Phthalate", "PhthalicAnhydride + Butanol + BenzylChloride + NaOH -> BBP + NaCl + H2O", FLASK,
      "Phthalic anhydride half-esterified with butanol; the sodium salt is benzylated.", wiki=3007126, T=120),
    R("Vinylene Carbonate", "EthyleneCarbonate + Cl2 -> VinyleneCarbonate + 2 HCl", LIGHT,
      "Ethylene carbonate chlorinated in light, then hydrogen chloride removed.", wiki=57466302, T=60),
    R("2-sec-Butylphenol", "Phenol + 1-Butene -> sBP2", CAT,
      "Phenol alkylated at the ortho position with aluminium phenoxide.", wiki=51491730, cat="Al", T=250),
    R("Dinoseb", "sBP2 + 2 HNO3 -> Dinoseb + 2 H2O", FLASK,
      "sec-Butylphenol nitrated twice.", wiki=19505215, T=40),
    R("DMP-30", "Phenol + 3 CH2O + 3 Me2NH -> DMP30 + 3 H2O", MIX,
      "A triple Mannich reaction on phenol.", wiki=77091094),
    R("4,4'-Biphenol", "4 DTBP26 + O2 -> 2 Biphenol + 8 Isobutylene + 2 H2O", CAT,
      "Di-tert-butylphenol coupled by air into a biphenyl; heating with acid knocks the tert-butyl groups off again.",
      wiki=6781382, cat="KOH", T=200),
    R("Hexafluoroisopropanol", "HFA + H2 -> HFIP", CAT,
      "Hexafluoroacetone hydrogenated over palladium.", wiki=1619291, cat="Pd", T=100),
    R("Cyclododecatriene", "3 Butadiene -> CDT", CAT,
      "Wilke's trimerisation of butadiene on a titanium or nickel catalyst.", wiki="Cyclododecatriene",
      cat="TiCl4", T=60),
    R("Laurolactam", "CDT + 3 H2 + O2 + NH2OH -> Laurolactam + 2 H2O", FLASK,
      "Cyclododecatriene hydrogenated, oxidised to the ketone, made into the oxime and rearranged (Beckmann).",
      wiki=35551062, T=100),
    R("Trichloropropane", "AllylChloride + Cl2 -> TCP123", CAT,
      "Chlorine added across allyl chloride.", wiki=31632161, cat="FeCl3", T=40),
    R("Glycerol Dichlorohydrin", "Glycerol + 2 HCl -> DCH13 + 2 H2O", CAT,
      "Glycerol chlorinated by hydrogen chloride with a carboxylic acid catalyst (Epicerol).", wiki=56828423,
      cat="AcOH", T=110),
    R("MEK Oxime", "MEK + NH2OH -> MEKO + H2O", MIX,
      "Methyl ethyl ketone and hydroxylamine.", wiki=28168749),
    R("Methyltetrahydrofuran", "MethylFuran2 + 2 H2 -> MeTHF", CAT,
      "2-Methylfuran hydrogenated over nickel.", wiki=26970606, cat="Ni", T=150),
    R("Triphenylborane", "2 BF3 + 6 PhMgBr -> 2 BPh3 + 3 MgF2 + 3 MgBr2", FLASK,
      "Boron trifluoride with phenylmagnesium bromide.", wiki=22624569, T=20),
    R("Ethyl Methacrylate", "MethacrylicAcid + Ethanol -> EMA + H2O", CAT,
      "Methacrylic acid esterified with ethanol.", wiki=61698613, cat="H2SO4", T=90),
    R("Isobutyric Anhydride", "2 IsobutyricAcid + AceticAnhydride -> IsobutyricAnhydride + 2 AcOH", FLASK,
      "Isobutyric acid swaps partners with acetic anhydride.", wiki=77694615, T=140),
    R("Tetrahydrofurfuryl Alcohol", "FurfurylAlcohol + 2 H2 -> THFA", CAT,
      "Furfuryl alcohol's ring hydrogenated over nickel.", wiki=59687464, cat="Ni", T=120),
    R("Phenyltrichlorosilane", "Benzene + HSiCl3 -> PhSiCl3 + H2", HEAT,
      "Benzene and trichlorosilane condensed at 600 C.", wiki=13037086, T=600),
    R("Nicotinamide", "NicotinicAcid + NH3 -> Nicotinamide + H2O", HEAT,
      "Nicotinic acid heated with ammonia.", wiki=21968, T=230),
    R("Fries Rearrangement", "Phenol + AceticAnhydride -> HAP + AcOH", CAT,
      "Phenol acetylated in hydrogen fluoride, which moves the acetyl group to the para position.", wiki=35537702,
      cat="HF", T=80),
    R("2-Chloropyridine", "Pyridine + Cl2 -> ClPyridine + HCl", HEAT,
      "Pyridine chlorinated in the gas phase.", wiki=27233882, T=400),
    R("Octanoyl Chloride", "3 Octanoic + PCl3 -> 3 OctanoylCl + H3PO3", FLASK,
      "Octanoic acid chlorinated with phosphorus trichloride.", wiki=54438896, T=60),
    R("RDX", "Hexamine + 4 HNO3 -> RDX + 3 CH2O + NH4NO3", FLASK,
      "Hexamine nitrated by strong nitric acid (the Woolwich process).", wiki=7499, T=20),
    R("Solketal", "Glycerol + Acetone -> Solketal + H2O", CAT,
      "Glycerol and acetone over an acid catalyst.", wiki=4390618, cat="H2SO4", T=50),
    R("Dicyclohexylamine", "2 Cyclohexylamine -> DCHA + NH3", CAT,
      "Cyclohexylamine disproportionated over palladium.", wiki=44112420, cat="Pd", T=200),
    R("Tripropylamine", "Dipropylamine + Propanol -> TPrA + H2O", CAT,
      "Dipropylamine alkylated with propanol over nickel.", wiki=73626945, cat="Ni", T=200),
    R("2-Ethylhexyl Acetate", "2EH + AcOH -> EHAc + H2O", CAT,
      "2-Ethylhexanol esterified with acetic acid.", wiki=4084502, cat="H2SO4", T=120),
    R("Allyl Glycidyl Ether", "AllylAlcohol + Epichlorohydrin + NaOH -> AGE + NaCl + H2O", FLASK,
      "Allyl alcohol joined to epichlorohydrin, the epoxide reclosed by caustic soda.", wiki=46815783, T=60),
    R("Butyllithium", "BuCl + 2 Li -> BuLi + LiCl", FLASK,
      "Butyl chloride and lithium metal in hexane.", wiki=2057516, T=40),
    R("Di-tert-butyl Peroxide", "2 tBuOH + H2O2 -> DTBPeroxide + 2 H2O", CAT,
      "tert-Butanol and hydrogen peroxide in sulfuric acid.", wiki=3997462, cat="H2SO4", T=30),
    R("Aldehyde C-12 MNA", "Undecanal + CH2O + H2 -> MNA + H2O", CAT,
      "Undecanal condensed with formaldehyde, then the double bond hydrogenated.", wiki=22542034, cat="Pd", T=100),
    R("Azepane", "HMDA -> Azepane + NH3", CAT,
      "Hexamethylenediamine cyclised over nickel, losing ammonia.", wiki=23755808, cat="Ni", T=200),
    R("Stearoyl Ethanolamide", "StearicAcid + MEA -> SEA + H2O", HEAT,
      "Stearic acid heated with ethanolamine.", wiki=40333152, T=170),
    R("Diglyme", "2 Methanol + 2 EO -> Diglyme + H2O", CAT,
      "Ethylene oxide opened by methanol twice over, then the end methylated.", wiki=5259465, cat="BF3", T=100),
    R("Caprylyl Glycol", "Octene + H2O2 -> Octanediol12", FLASK,
      "1-Octene epoxidised by performic acid and the epoxide hydrolysed.", wiki=51597359, T=60),
    R("Oleylamine", "OleicAcid + NH3 + 2 H2 -> Oleylamine + 2 H2O", HIGHP,
      "Oleic acid turned into its nitrile with ammonia, then hydrogenated.", wiki=32457852, cat="Ni", T=150),
    R("Dibenzoylmethane", "Acetophenone + MethylBenzoate -> DBM + Methanol", CAT,
      "A Claisen condensation with sodium methoxide.", wiki=33535660, cat="NaOMe", T=100),
    R("Bis(2-ethylhexyl) Sebacate", "SebacicAcid + 2 2EH -> DEHS + 2 H2O", CAT,
      "Sebacic acid esterified with 2-ethylhexanol.", wiki=4214695, cat="H2SO4", T=180),
    R("Acetylacetone", "Acetone + Ketene -> AcAc", CAT,
      "Ketene and acetone make isopropenyl acetate, which rearranges to acetylacetone.", wiki=1558266,
      cat="pTsOH", T=500),
    R("Azodicarbonamide", "N2H4 + 2 Urea + Cl2 -> ADA + 2 NH3 + 2 HCl", FLASK,
      "Hydrazine and urea make biurea, which chlorine oxidises.", wiki=2904705, T=60),
    R("Isobornyl Acetate", "Camphene + AcOH -> IsobornylAcetate", CAT,
      "Acetic acid adds to camphene, which rearranges to the bornyl skeleton.", wiki=72377771,
      cat="H2SO4", T=40),
    R("Dipentaerythritol", "2 Pentaerythritol -> DiPE + H2O", CAT,
      "Two pentaerythritols joined by an ether bridge.", wiki=78367159, cat="H2SO4", T=200),
    R("Dithiocarbamate", "Me2NH + CS2 + NaOH -> NaDMDTC + H2O", MIX,
      "Dimethylamine and carbon disulfide in caustic soda.", wiki=8117552),
    R("Span 60", "Sorbitol + StearicAcid -> Span60 + 2 H2O", CAT,
      "Sorbitol closes into sorbitan and is esterified with stearic acid.", wiki=5170103, cat="NaOH", T=210),
    R("Aminoethylpiperazine", "Piperazine + MEA -> AEP + H2O", CAT,
      "Piperazine aminoethylated by ethanolamine over nickel.", wiki=10600898, cat="Ni", T=200),
    R("Mercaptobenzothiazole", "Aniline + CS2 + S -> MBT + H2S", PRESS,
      "Aniline, carbon disulfide and sulfur heated under pressure (the Kelly process).", wiki=49598939, T=250),
]

import authored_canon_8  # noqa: E402,F401
