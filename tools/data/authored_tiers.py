"""
Curieosity tier content: the vessel tiers, what moves into them, the recipes only they
can run, the systematic laboratory families, and the milestone ladder.

Imported at the end of authored_content.py (which it extends in place), so gen_authored.py
sees one body of content. Kept apart because authored_content.py is near 4,000 lines.

Vessels come in families (Heat, Mix, Distillation, ...) with tiers. A recipe's process is
its HOME vessel; any vessel of the same family at that tier or higher can also run it. A
recipe that needs a catalyst must live in a vessel with a catalyst slot (and so must every
vessel above it in the family: the generator checks that).
"""

import authored_content as C
from authored_content import X, L, R, RAW, SUBSTANCES, E0, E1, E2, E3, E4, E5, E6, E7
from gen_authored import (Milestone, MIX, HEAT, COOL, SMELT, DISTIL, ELEC, LIGHT, CAT, PRESS,
                          POLY, FLASK, BLAST, ARC, AIRLIQ, COLUMN, ECELL, REACTOR, CYCLO,
                          CRACKER, HIGHP, DPRESS, FERM, BIOR, PULLER, CVD, CENT, ULTRA, CRYO)


def N(key, name, formula, state, desc, wiki, color=None, smiles=None, props=(), balance=None):
    """A new substance with its own description and Wikipedia article."""
    X(key, name, formula, state, desc, wiki, id=0, color=color, smiles=smiles, props=props,
      balance=balance)


def rehome(epoch, name, process, cat=None, desc=None):
    for r in epoch.reactions:
        if r.name == name:
            r.process = process
            if cat:
                r.cat = cat
            if desc:
                r.desc = desc
            return r
    raise SystemExit(f"rehome: no reaction {name!r} in {epoch.name}")


# ======================================================================================
# 1. RE-HOMING: existing chemistry moves into the vessel that actually did it
# ======================================================================================
for ep, names, proc in [
    (E1, ["Fermentation", "Souring Vinegar", "Indigo Vat"], FERM),
    (E3, ["Coke Blast Furnace", "Portland Cement", "Leblanc Soda"], BLAST),
    (E3, ["Liquefying Air"], AIRLIQ),
    (E3, ["Liebig's Chloral", "Chloroform", "Mitscherlich's Nitrobenzene", "Liebig's Benzoic Acid",
          "Pelletier and Caventou's Quinine", "Mein's Atropine", "Withering's Foxglove",
          "Vogel's Coumarin", "Proust's Mannitol", "Wackenroder's Carotene", "Rutin from Buckwheat"], FLASK),
    (E4, ["Bessemer Converter", "Open-Hearth Steel", "Basic Steel"], BLAST),
    (E4, ["Stainless Steel", "High-Speed Steel", "Calcium Carbide", "Acheson's Carborundum",
          "Acheson Graphite", "Electric Furnace Phosphorus", "Birkeland-Eyde Arc"], ARC),
    (E4, ["Hall-Heroult Cell", "Chlor-Alkali Cell", "Moissan's Fluorine", "Electrolytic Refining",
          "Lanthanum Metal", "Cerium Metal", "Praseodymium Metal"], ECELL),
    (E4, ["Fractionating Liquid Air", "Refining Crude Oil"], COLUMN),
    (E4, ["Dewar's Liquid Hydrogen", "Onnes' Liquid Helium"], CRYO),
    (E4, ["Bayer Digestion"], PRESS),
    (E4, ["Glucose Fermentation, Weizmann", "Gluconic Acid"], FERM),
    (E4, ["Perkin's Mauve", "Hofmann Rearrangement", "Hoffmann's Aspirin", "Fahlberg's Saccharin",
          "Grignard Reagent", "Strecker's Alanine", "Antifebrin", "Tiemann's Violets"], FLASK),
    (E5, ["Bergius Hydrogenation", "Bosch-Meiser Urea", "ICI Polyethylene"], HIGHP),
    (E5, ["Downs Cell", "Gallium from Bayer Liquor"], ECELL),
    (E5, ["Catalytic Cracking", "Platforming", "Alkylation", "Sohio Acrylonitrile"], CRACKER),
    (E5, ["Separating Natural Gas"], COLUMN),
    (E5, ["Czochralski Crystal", "The Transistor"], PULLER),
    (E5, ["Fermenting Penicillin"], BIOR),
    (E5, ["Neptunium", "Americium", "Einsteinium and Fermium", "Fermi's Pile"], REACTOR),
    (E5, ["Seaborg's Plutonium", "Segre's Technetium", "Curium", "Berkelium", "Californium",
          "Mendelevium", "Nobelium", "Lawrencium", "Corson's Astatine"], CYCLO),
    (E5, ["Methyl Methacrylate", "Dinitrotoluene", "Nitrating Aniline", "Bisphenol A", "Paracetamol",
          "Muller's DDT", "Reichstein's Vitamin C", "Hexamine", "Kuhn's Lactoflavin", "Vitamin B6",
          "Kogl's Biotin", "Vitamin A", "Sterols of Wool Grease", "Ozonolysis of Oleic Acid"], FLASK),
    (E6, ["Supercritical Decaf"], HIGHP),
    (E6, ["Plasma Diamond", "Gallium Nitride", "The Blue LED", "The Microprocessor"], CVD),
    (E6, ["Lactic Fermentation"], FERM),
    (E6, ["Neodymium Metal"], ECELL),
    (E6, ["Rutherfordium", "Dubnium", "Seaborgium", "Bohrium", "Meitnerium", "Hassium",
          "Darmstadtium", "Roentgenium", "Copernicium", "Nihonium", "Flerovium", "Livermorium",
          "Oganesson", "Moscovium", "Tennessine"], CYCLO),
    (E6, ["Tu Youyou's Extraction", "Cisplatin", "Methylammonium Iodide", "Grubbs Catalyst",
          "Boronic Acid"], FLASK),
    (E7, ["Boron Carbide"], ARC),
]:
    for n in names:
        rehome(ep, n, proc)

rehome(E4, "Haber-Bosch Synthesis", HIGHP, cat="Fe",
       desc="Fritz Haber fixed nitrogen from the air in 1909; Carl Bosch scaled it up by 1913 in "
            "reactors holding 200 atmospheres at 450 C, over Alwin Mittasch's promoted iron "
            "catalyst. Half the nitrogen in your body has passed through this reaction.")
rehome(E5, "Methanol Synthesis", HIGHP, cat="ZnO")
rehome(E5, "Oxo Butanal", HIGHP)
rehome(E5, "Hexamethylenediamine", HIGHP)
rehome(E6, "CO2 to Methanol", HIGHP, cat="Cu")
rehome(E5, "GE Synthetic Diamond", DPRESS, cat="Ni",
       desc="Tracy Hall's belt press at General Electric (16 December 1954) squeezed graphite to "
            "100,000 atmospheres at 1,600 C in molten nickel, which dissolves the carbon and lets it "
            "crystallise out as diamond.")

# ======================================================================================
# 2. NEW RAW MATERIALS AND CULTURES
# ======================================================================================
RAW("Grapes", "Grapes", "Vitis vinifera, domesticated in the Caucasus around 6000 BCE. The bloom on the skin is wild yeast: crush them and they ferment on their own.", "Grape", "#5a2a6a")
RAW("Honey", "Honey", "Nectar concentrated by bees to about 80% sugar, mostly fructose and glucose. Honey hunters appear in Spanish cave paintings 8,000 years old.", "Honey", "#e0a020", state="Liquid")
RAW("Milk", "Milk", "Cow, sheep and goat milk: water, fat, the protein casein and the sugar lactose. Dairying began in the Near East about 9,000 years ago.", "Milk", "#f0ece0", state="Liquid")
RAW("Soybeans", "Soybeans", "Glycine max, domesticated in northern China about 7000 BCE: 40% protein and 20% oil.", "Soybean", "#d8c070")
RAW("Aspergillus", "Aspergillus niger", "The black mould of onions and damp walls. James Currie found in 1917 that it pours out citric acid; it still makes nearly all of the world's supply.", "Aspergillus_niger", "#2a2a2a")
RAW("Streptomyces", "Streptomyces", "Soil bacteria that grow like a fungus and give earth its smell (geosmin). They make two-thirds of all natural antibiotics.", "Streptomyces", "#b8a080")
RAW("Corynebacterium", "Corynebacterium glutamicum", "A soil bacterium found by Kinoshita at Kyowa Hakko in 1956 that leaks glutamic acid; it now makes millions of tonnes of amino acids a year.", "Corynebacterium_glutamicum", "#d0c8a0")
RAW("Ecoli", "Escherichia coli", "The gut bacterium Theodor Escherich described in 1885, and the workhorse of molecular biology: the first organism given a human gene to express (insulin, 1978).", "Escherichia_coli", "#c8a8a0")


# ======================================================================================
# 3. THE ERAS, VESSEL BY VESSEL
# ======================================================================================
# --- E0: the first fermenters ---------------------------------------------------------
N("Beer", "Beer", "mixture", "Liquid", "Sumerian beer was drunk through reed straws from a shared jar; the 'Hymn to Ninkasi' (c. 1800 BCE) is both a prayer and a recipe.", "History_of_beer", color="#c88a20", balance="C")
N("Mead", "Mead", "mixture", "Liquid", "Honey wine, perhaps the oldest fermented drink: residues in Jiahu, China (7000 BCE) mix honey, rice and fruit.", "Mead", color="#e0b040", balance="C")
N("Yogurt", "Yogurt", "mixture", "Solid", "Milk soured and thickened by lactic acid bacteria. Metchnikoff credited Bulgarian yogurt for long lives (1907) and made it fashionable in Europe.", "Yogurt", color="#f4f0e8", balance="C")
E0.reactions += [
    R("Treading Grapes", "Grapes -> Wine", FERM,
      "Crushed grapes ferment on the wild yeasts of their own skins. The oldest wine residues, in jars from Gadachrili Gora in Georgia, are 8,000 years old.",
      wiki="History_of_wine", exact=False),
    R("Brewing Beer", "Barley + H2O -> Beer", FERM,
      "Malted barley mashed in warm water turns its starch to sugar, and the sugar ferments. Beer may be why people settled down to farm grain.",
      wiki="History_of_beer", exact=False),
    R("Brewing Mead", "Honey + H2O -> Mead", FERM,
      "Honey diluted with water ferments readily; undiluted, it is too sugary for any microbe to live in, which is why honey keeps for millennia.",
      wiki="Mead", exact=False),
    R("Souring Milk", "Milk -> Yogurt + LacticAcid", FERM,
      "Lactobacillus turns lactose to lactic acid, which curdles the casein: yogurt keeps for days where milk keeps for hours. Scheele isolated the acid from sour milk in 1780.",
      wiki="Yogurt#History", exact=False),
    R("Making Cheese", "Milk -> Cheese + Whey", MIX,
      "Rennet from a calf's stomach clots milk into curds and whey; the oldest cheese, in Polish sieves, is 7,500 years old.",
      wiki="History_of_cheese", exact=False),
    R("Skimming Cream", "Milk -> Cream + SkimMilk", COOL,
      "Milk set out in shallow pans in a cool dairy overnight: the fat rises as cream and is skimmed off by hand, as farms did until the separator.",
      wiki="Cream", exact=False),
    R("Churning Butter", "Cream -> Butter + Buttermilk", MIX,
      "Cream beaten until its fat globules break and clump into butter, leaving the buttermilk.", wiki="Butter#Production",
      exact=False),
    R("Crystallising Honey", "Honey -> Glucose + Fructose", MIX,
      "Honey is a supersaturated sugar syrup. Left standing, its glucose crystallises out of the runnier fructose.",
      wiki="Honey#Crystallization", exact=False),
]

# --- E1: pigments and glass of antiquity ------------------------------------------------
N("HanPurple", "Han Purple", "BaCuSi2O6", "Solid", "Barium copper silicate, made in China from about 800 BCE and painted on the Terracotta Army. It glows in near-infrared light.", "Han_purple_and_Han_blue", color="#6a4aa0")
N("NaplesYellow", "Naples Yellow", "Pb2Sb2O7", "Solid", "Lead antimonate, an opaque yellow used in Egyptian and Babylonian glass and glazes long before it was a painter's colour.", "Naples_yellow", color="#f0c850")
E1.reactions += [
    R("Pressing Olives", "Olives -> Triolein + Pomace", MIX,
      "Olives crushed under a millstone and the paste squeezed in a beam press; the oil floats off the watery juice. The Greeks and Romans pressed it by the shipload.",
      wiki="Olive_oil#Extraction", exact=False),
    R("Han Purple", "BaCO3 + CuO + 2 Sand -> HanPurple + CO2", HEAT,
      "Barium carbonate, copper oxide and quartz fired near 1,000 C: a synthetic pigment invented in China to imitate jade and lapis.",
      wiki="Han_purple_and_Han_blue", T=1000, dh=60),
    R("Naples Yellow", "4 PbO + 4 Sb + 5 O2 -> 2 NaplesYellow", HEAT,
      "Litharge and antimony oxide roasted together, the yellow of Egyptian glass beads and Renaissance skies.",
      wiki="Naples_yellow", T=900, dh=-200),
]

# --- E2: alchemists' glass, salts and spirits --------------------------------------------
N("LeadCrystal", "Lead Crystal", "mixture", "Solid", "George Ravenscroft's glass (1674): lead oxide in place of lime makes it heavy, soft to cut and brilliant, with a high refractive index.", "Lead_glass", color="#e8f0f8", balance="PbSiO3")
N("CranberryGlass", "Gold Ruby Glass", "mixture", "Solid", "Glass coloured red by gold nanoparticles. Johann Kunckel made it in Potsdam around 1679; Faraday worked out in 1857 that the gold was finely divided metal.", "Cranberry_glass", color="#c02040", balance="C")
N("Smalt", "Smalt", "mixture", "Solid", "Potash glass coloured blue with cobalt and ground to a powder: the cheap blue of 16th-century painters and of Delftware.", "Smalt", color="#3050b0", balance="C")
N("SnCl4", "Tin(IV) Chloride", "SnCl4", "Liquid", "Spiritus fumans Libavii: Andreas Libavius made this fuming liquid in 1605 by distilling tin with corrosive sublimate. It fumes because air's moisture hydrolyses it.", "Tin(IV)_chloride", color="#e8e8e0")
N("SbCl3", "Antimony Trichloride", "SbCl3", "Solid", "Butter of antimony, a soft, fuming, buttery solid known to the alchemists; Glauber made it from stibnite and sea salt.", "Antimony_trichloride", color="#f0f0e0")
E2.reactions += [
    R("Ravenscroft's Lead Crystal", "6 Sand + PbO + Potash -> LeadCrystal", HEAT,
      "Ravenscroft's flint glass: sand, litharge and potash. It was patented in 1674 and made English glassware famous.",
      wiki="George_Ravenscroft", exact=False, T=1200),
    R("Kunckel's Gold Ruby", "Glass + HAuCl4 -> CranberryGlass", HEAT,
      "A pinch of gold dissolved in aqua regia, worked into molten glass and re-heated, strikes a deep ruby red.",
      wiki="Cranberry_glass", exact=False, T=1100),
    R("Making Smalt", "Glass + CoO -> Smalt", HEAT,
      "Cobalt oxide from the Saxon silver mines melted into potash glass, then crushed: the blue of Delft and of Ming export ware.",
      wiki="Smalt", exact=False, T=1100),
    R("Libavius' Fuming Liquor", "Sn + 2 Cl2 -> SnCl4", HEAT,
      "Tin burns in chlorine to the colourless, fuming tetrachloride; Libavius had made it from tin and corrosive sublimate.",
      wiki="Tin(IV)_chloride#History", dh=-511),
    R("Butter of Antimony", "Stibnite + 6 HCl -> 2 SbCl3 + 3 H2S", DISTIL,
      "Stibnite distilled with spirit of salt: the alchemists' butter of antimony comes over and solidifies in the receiver.",
      wiki="Antimony_trichloride#Preparation", T=220, dh=60),
]

# --- E3: porcelain, steam, the first cryogenics and the new organic chemistry -------------
N("Mullite", "Mullite", "Al6Si2O13", "Solid", "The needle-shaped aluminium silicate that forms when clay is fired above 1,100 C; its interlocking crystals make porcelain hard and translucent.", "Mullite", color="#f4f0ec")
N("DryIce", "Dry Ice", "CO2", "Solid", "Solid carbon dioxide at -78.5 C. It sublimes straight to gas without melting, hence 'dry'. Adrien-Jean-Pierre Thilorier first made it in 1835.", "Dry_ice", color="#e8f4ff")
N("LiquidNH3", "Liquid Ammonia", "NH3", "Liquid", "Ammonia boils at -33 C. Liquefied, it was the working fluid of the first refrigerators (Linde, 1876) and dissolves sodium into a deep blue solution of free electrons.", "Ammonia#Liquid_ammonia", color="#e0f0ff")
N("CobaltBlue", "Cobalt Blue", "CoAl2O4", "Solid", "Cobalt aluminate, invented by Louis Jacques Thenard in 1802 for the Sevres porcelain works at the request of the French government.", "Cobalt_blue", color="#0047ab")
N("Ultramarine", "Synthetic Ultramarine", "mixture", "Solid", "Lapis lazuli's blue, once dearer than gold. In 1824 the Societe d'Encouragement offered 6,000 francs for a synthesis; Jean-Baptiste Guimet won it in 1828.", "Ultramarine#Synthetic_ultramarine", color="#1f3fa8", balance="C")
N("UraniumGlass", "Uranium Glass", "mixture", "Solid", "Glass with a little uranium oxide, yellow-green by day and glowing green under ultraviolet. Josef Riedel made it in Bohemia in the 1830s.", "Uranium_glass", color="#b8e830", balance="C")
N("Benzoin", "Benzoin", "C14H12O2", "Solid", "Two benzaldehyde molecules joined head to tail; it has nothing to do with gum benzoin except that both smell faintly of almonds.", "Benzoin_(organic_compound)", smiles="OC(C(=O)c1ccccc1)c1ccccc1")
N("BenzilicAcid", "Benzilic Acid", "C14H12O3", "Solid", "Liebig's 1838 rearrangement product of benzil with potash: the first rearrangement reaction ever described.", "Benzilic_acid", smiles="OC(=O)C(O)(c1ccccc1)c1ccccc1")
L("Benzil", "Benzil", "C14H10O2", "Solid", smiles="O=C(C(=O)c1ccccc1)c1ccccc1")
N("ZeiseSalt", "Zeise's Salt", "KPtCl3C2H4", "Solid", "K[PtCl3(C2H4)]: William Zeise's yellow salt (Copenhagen, 1827), the first organometallic compound. How ethylene could bind to platinum was a puzzle for 120 years.", "Zeise%27s_salt", color="#f0d040", smiles="C=C.Cl[Pt-](Cl)Cl.[K+]")
E3.reactions += [
    R("Bottger's Porcelain", "3 Metakaolin -> Mullite + 4 Sand", BLAST,
      "Johann Bottger, an alchemist imprisoned to make gold, made Europe's first hard-paste porcelain at Meissen in 1708 by firing kaolin to 1,350 C.",
      wiki="Johann_Friedrich_B%C3%B6ttger", T=1350, dh=30),
    R("Papin's Digester", "Horn + H2O -> Gelatin", PRESS,
      "Denis Papin's steam digester (1679) cooked bones under pressure until they fell to jelly, and its safety valve inspired the steam engine.",
      wiki="Denis_Papin", exact=False, T=150, P=2),
    R("Thilorier's Dry Ice", "CO2 -> DryIce", COOL,
      "Thilorier compressed carbon dioxide to a liquid and let it spray out: it froze itself into snow at -78 C (1835).",
      wiki="Dry_ice#History", T=-79, dh=-25),
    R("Liquefying Ammonia", "NH3 -> LiquidNH3", COOL,
      "Faraday liquefied ammonia in 1823 by heating its silver chloride complex in a sealed bent tube with the far end in ice.",
      wiki="Ammonia#History", T=-33, dh=-23),
    R("Thenard's Blue", "CoO + Alumina -> CobaltBlue", HEAT,
      "Cobalt oxide fired with alumina: a stable, lightfast blue that replaced smalt and expensive ultramarine.",
      wiki="Cobalt_blue#History", T=1200, dh=-40),
    R("Guimet's Ultramarine", "Metakaolin + SodaAsh + S + Charcoal -> Ultramarine", HEAT,
      "China clay, soda, sulfur and charcoal fired without air: the sulfur radical anions caged in the aluminosilicate are what is blue.",
      wiki="Ultramarine", exact=False, T=750),
    R("Riedel's Uranium Glass", "Glass + Pitchblende -> UraniumGlass", HEAT,
      "A percent or two of uranium oxide in the glass melt gives a canary yellow that fluoresces green.", wiki="Uranium_glass", exact=False, T=1100),
    R("Conversion Saltpetre", "NaNO3 + KCl -> KNO3 + NaCl", COOL,
      "Chile saltpetre and potash salts swap partners in hot water; the potassium nitrate crystallises on cooling, the salt stays in solution.",
      wiki="Potassium_nitrate#Production", T=10, dh=4),
    R("Pasteur's Butyric Ferment", "2 LacticAcid -> Butyric + 2 CO2 + 2 H2", FERM,
      "Pasteur found in 1861 that the bacteria turning lactate into butyric acid died in air: the discovery of life without oxygen, which he called anaerobic.",
      wiki="Butyric_acid#Production", dh=-250),
    R("Kolbe Electrolysis", "2 AcOH -> Ethane + 2 CO2 + H2", ELEC,
      "Hermann Kolbe electrolysed acetate in 1849: the carboxyl groups leave as CO2 and the methyl radicals pair up into ethane.",
      wiki="Kolbe_electrolysis", dh=60),
    R("Cannizzaro Reaction", "2 Benzaldehyde + KOH -> BenzylAlcohol + KC7H5O2", FLASK,
      "Stanislao Cannizzaro (1853): in strong alkali one aldehyde molecule is reduced while its partner is oxidised to the acid.",
      wiki="Cannizzaro_reaction", dh=-60),
    R("Benzoin Condensation", "2 Benzaldehyde -> Benzoin", FLASK,
      "Liebig and Wohler found benzoin in oil of bitter almonds (1832); Nikolay Zinin showed a trace of cyanide joins two benzaldehydes head to tail.",
      wiki="Benzoin_condensation", dh=-40),
    R("Oxidising Benzoin", "2 Benzoin + O2 -> 2 Benzil + 2 H2O", FLASK,
      "Gentle oxidation of benzoin's alcohol gives the yellow diketone benzil.", wiki="Benzil", dh=-200),
    R("Benzilic Acid Rearrangement", "Benzil + H2O -> BenzilicAcid", FLASK,
      "Benzil in hot potash shifts a phenyl group from one carbon to its neighbour (Liebig, 1838).", wiki="Benzilic_acid_rearrangement", dh=-80),
    R("Liebig's Silver Mirror", "Glucose + 2 AgNO3 + 2 NH3 + H2O -> GluconicAcid + 2 Ag + 2 NH4NO3", FLASK,
      "Ammoniacal silver nitrate warmed with sugar plates a perfect mirror onto glass (Liebig, 1835); Tollens made it a test for aldehydes in 1882.",
      wiki="Tollens%27_reagent", dh=-100),
    R("Zeise's Salt", "K2PtCl4 + Ethylene -> ZeiseSalt + KCl", FLASK,
      "Zeise (1827) boiled platinum chloride in ethanol, which gave up ethylene to the metal: the birth of organometallic chemistry. Today the salt is made from ethylene itself.",
      wiki="Zeise%27s_salt", dh=-50),
]

N("K2MnO4", "Potassium Manganate", "K2MnO4", "Solid", "Glauber's 'mineral chameleon' (1659): its green solution turns violet, then brown, as it changes to permanganate and manganese dioxide.", "Potassium_manganate", color="#2a7a3a")
E2.reactions += [
    R("Glauber's Mineral Chameleon", "2 MnO2 + 4 KOH + O2 -> 2 K2MnO4 + 2 H2O", HEAT,
      "Pyrolusite fused with caustic potash in air gives a green melt; dissolved in water its colour drifts through the rainbow, hence 'chameleon'.",
      wiki="Potassium_manganate#History", T=400, dh=-200),
]

# --- E4: Industry --------------------------------------------------------------------
N("Dynamo", "Dynamo", "mixture", "Solid", "Werner von Siemens' self-exciting dynamo (1866) turned mechanical work into current with no battery at all, and made electricity cheap enough to smelt with.", "Dynamo", color="#b87333", balance="C")
N("Ferromanganese", "Ferromanganese", "FeMn", "Solid", "An iron alloy with up to 80% manganese. Robert Mushet's 1856 discovery that it 'cures' Bessemer steel of its brittleness saved the process.", "Ferromanganese", color="#8a8a90", props=["IsMetal"])
N("CaAl2O4", "Calcium Aluminate Cement", "CaAl2O4", "Solid", "Jules Bied's Ciment Fondu (Lafarge, 1908): sets in hours rather than weeks and shrugs off sulfate water and fire.", "Calcium_aluminate_cements", color="#5a5a58")
N("Cu2S", "Copper(I) Sulfide", "Cu2S", "Solid", "Chalcocite, the copper-rich sulfide of matte: smelters concentrate copper ore into this before blowing it to metal.", "Copper(I)_sulfide", color="#3a3a40")
N("FeO", "Iron(II) Oxide", "FeO", "Solid", "Wustite, the black oxide that sits between iron and magnetite; in a smelter it is slagged off with silica.", "Iron(II)_oxide", color="#2a2a2a")
N("WC", "Tungsten Carbide", "WC", "Solid", "Twice as stiff as steel and nearly as hard as diamond. Henri Moissan made it in his arc furnace in 1896; drill bits and cutting tools have used it since the 1920s.", "Tungsten_carbide", color="#6a6a72")
N("TiC", "Titanium Carbide", "TiC", "Solid", "A hard, refractory carbide melting at 3,160 C, alloyed into cermets for cutting tools and the heat shields of re-entering spacecraft.", "Titanium_carbide", color="#7a7a80")
N("TaC", "Tantalum Carbide", "TaC", "Solid", "One of the highest-melting substances known, about 3,880 C; a golden-brown ceramic.", "Tantalum_carbide", color="#a08040")
N("NbC", "Niobium Carbide", "NbC", "Solid", "A lavender-grey refractory carbide added to steels and cemented carbides as a grain refiner.", "Niobium_carbide", color="#8a80a0")
L("VC", "Vanadium carbide", "VC", "Solid", name="Vanadium Carbide")
N("Mo2C", "Molybdenum Carbide", "Mo2C", "Solid", "A hard carbide that behaves curiously like platinum as a catalyst for hydrogen reactions.", "Molybdenum_carbide", color="#707078")
N("Cr3C2", "Chromium Carbide", "Cr3C2", "Solid", "Sprayed onto turbine parts and valves as a hard coating that resists wear and corrosion at high temperature.", "Chromium(II)_carbide", color="#808088")
N("Al4C3", "Aluminium Carbide", "Al4C3", "Solid", "Pale yellow crystals that Moissan made in the arc furnace; with water they give off methane, an odd source of natural gas in a test tube.", "Aluminium_carbide", color="#e0d080")
N("Be2C", "Beryllium Carbide", "Be2C", "Solid", "A brick-red, very hard carbide that also releases methane with water.", "Beryllium_carbide", color="#b05030")
N("CaB6", "Calcium Hexaboride", "CaB6", "Solid", "A black, lustrous boride of cages of boron atoms, made by Moissan; used to deoxidise copper.", "Calcium_hexaboride", color="#303038")
N("TiB2", "Titanium Diboride", "TiB2", "Solid", "Extremely hard and yet electrically conducting, so it can be shaped by spark machining; it lines aluminium smelting cells.", "Titanium_diboride", color="#606878")
N("CaSi2", "Calcium Silicide", "CaSi2", "Solid", "Calcium silicon alloy used to deoxidise steel; it also heats self-heating food cans.", "Calcium_silicide", color="#8890a0")
N("FeSi", "Ferrosilicon", "FeSi", "Solid", "Iron-silicon alloy, the steelmaker's deoxidiser and the reducing agent of the Pidgeon magnesium process; in WWII it filled hydrogen generators for barrage balloons.", "Ferrosilicon", color="#8a9098", props=["IsMetal"])
N("FeCr2", "Ferrochrome", "FeCr2", "Solid", "Iron with 50-70% chromium, smelted straight from chromite; four-fifths of it goes into stainless steel.", "Ferrochrome", color="#9098a0", props=["IsMetal"])
N("FeV", "Ferrovanadium", "FeV", "Solid", "The vanadium alloy that makes tough, springy steels; Henry Ford built the Model T's chassis from vanadium steel.", "Ferrovanadium", color="#90a0a8", props=["IsMetal"])
N("Alundum", "Fused Alumina", "Al2O3", "Solid", "Alumina melted in the arc furnace and recrystallised as corundum: Norton's 'Alundum' (1900), the grit of grinding wheels and sandpaper.", "Fused_alumina", color="#c8b8a8")
N("NaClO4", "Sodium Perchlorate", "NaClO4", "Solid", "Made by electrolysing sodium chlorate further; the starting point of every other perchlorate.", "Sodium_perchlorate")
N("H2S2O8", "Peroxydisulfuric Acid", "H2S2O8", "Solid", "Marshall's acid (1891), made at a platinum anode from cold sulfuric acid. It was the industrial source of hydrogen peroxide from 1908.", "Peroxydisulfuric_acid")
N("KMnO4", "Potassium Permanganate", "KMnO4", "Solid", "Deep purple crystals, a strong oxidiser. Henry Condy sold it as a disinfectant ('Condy's crystals', 1857); it treats water and was the flash in early photography.", "Potassium_permanganate", color="#7a1a8a")
N("PhN2Cl", "Benzenediazonium Chloride", "C6H5N2Cl", "Aqueous", "Peter Griess's diazonium salt (1858): stable only near 0 C, it couples with phenols and amines into the whole family of azo dyes.", "Benzenediazonium_chloride", smiles="[Cl-].N#[N+]c1ccccc1", props=("IsTransient",))
N("HydroxyAzo", "4-Hydroxyazobenzene", "C12H10N2O", "Solid", "Orange-yellow dye from diazonium and phenol: the simplest azo coupling, the chemistry behind most synthetic dyes and food colours.", "Azo_coupling", color="#f09020", smiles="Oc1ccc(cc1)N=Nc1ccccc1")
L("Dimethylaniline", "N,N-Dimethylaniline", "C8H11N", "Liquid", smiles="CN(C)c1ccccc1")
N("MethylOrange", "Methyl Orange", "C14H14N3NaO3S", "Solid", "The indicator that is red below pH 3.1 and yellow above 4.4; made by coupling diazotised sulfanilic acid onto dimethylaniline.", "Methyl_orange", color="#f07020", smiles="CN(C)c1ccc(cc1)N=Nc1ccc(cc1)S(=O)(=O)[O-].[Na+]")
N("Iodobenzene", "Iodobenzene", "C6H5I", "Liquid", "A dense oily liquid; the iodine makes it the favourite partner in modern palladium cross-couplings.", "Iodobenzene", smiles="Ic1ccccc1")
N("Dibenzalacetone", "Dibenzalacetone", "C17H14O", "Solid", "Yellow crystals from a double aldol condensation (Claisen and Schmidt, 1881); an ingredient of some sunscreens and the ligand of a famous palladium catalyst.", "Dibenzylideneacetone", color="#f0e060", smiles="O=C(/C=C/c1ccccc1)/C=C/c1ccccc1")
N("Chalcone", "Chalcone", "C15H12O", "Solid", "The aromatic ketone at the root of the flavonoids, the pigments of flowers and fruit.", "Chalcone", color="#f0e080", smiles="O=C(/C=C/c1ccccc1)c1ccccc1")
N("Phenolphthalein", "Phenolphthalein", "C20H14O4", "Solid", "Adolf von Baeyer's 1871 indicator: colourless in acid, pink above pH 8.2. For a century it was also the active ingredient of laxatives.", "Phenolphthalein", smiles="O=C1OC(c2ccccc12)(c1ccc(O)cc1)c1ccc(O)cc1")
N("mBDSA", "Benzene-1,3-disulfonic Acid", "C6H6O6S2", "Solid", "Benzene sulfonated twice; fused with caustic soda it gives resorcinol.", "Resorcinol#Production", smiles="OS(=O)(=O)c1cccc(c1)S(=O)(=O)O")
L("Resorcinol", "Resorcinol", "C6H6O2", "Solid", smiles="Oc1cccc(O)c1")
L("Fluorescein", "Fluorescein", "C20H12O5", "Solid", smiles="O=C1OC2(c3ccccc13)c1ccc(O)cc1Oc1cc(O)ccc12")
N("Eosin", "Eosin Y", "C20H8Br4O5", "Solid", "Fluorescein brominated four times (Heinrich Caro, 1874): the pink of red ink and the counterstain of every hospital's tissue slides.", "Eosin", color="#f04080", smiles="O=C1OC2(c3ccccc13)c1cc(Br)c(O)c(Br)c1Oc1c(Br)c(O)c(Br)cc12")
L("MalonicAcid", "Malonic acid", "C3H4O4", "Solid", smiles="OC(=O)CC(=O)O")
L("BarbituricAcid", "Barbituric acid", "C4H4N2O3", "Solid", smiles="O=C1CC(=O)NC(=O)N1")
L("Phenytoin", "Phenytoin", "C15H12N2O2", "Solid", smiles="O=C1NC(=O)C(N1)(c1ccccc1)c1ccccc1")
L("Diethylamine", "Diethylamine", "C4H11N", "Liquid", smiles="CCNCC")
L("Procaine", "Procaine", "C13H20N2O2", "Solid", smiles="CCN(CC)CCOC(=O)c1ccc(N)cc1")
N("DEAE", "2-Diethylaminoethanol", "C6H15NO", "Liquid", "An amino alcohol from diethylamine and ethylene oxide, the half of procaine that makes it soluble.", "Diethylethanolamine", smiles="CCN(CC)CCO")
N("CoAmmine", "Hexamminecobalt(III) Chloride", "Co(NH3)6Cl3", "Solid", "Orange crystals whose structure Alfred Werner explained in 1893 with six ammonias around one cobalt: the founding idea of coordination chemistry (Nobel, 1913).", "Hexamminecobalt(III)_chloride", color="#e07020")
N("Schweizer", "Schweizer's Reagent", "Cu(NH3)4(OH)2", "Aqueous", "Deep blue tetraamminecopper hydroxide (Matthias Schweizer, 1857), the one common solvent that dissolves cellulose; it made 'Bemberg' cuprammonium rayon.", "Schweizer%27s_reagent", color="#1830c0")
N("DryCell", "Dry Cell", "mixture", "Solid", "Leclanche's zinc-carbon cell (1866), made 'dry' by Carl Gassner in 1886 with a paste of ammonium chloride: the first battery you could carry.", "Zinc%E2%80%93carbon_battery", color="#8a8a8a", balance="C")
N("NiCdCell", "Nickel-Cadmium Cell", "mixture", "Solid", "Waldemar Jungner's rechargeable cell (1899): nickel oxyhydroxide against cadmium in potash, reliable for a century of power tools and satellites.", "Nickel%E2%80%93cadmium_battery", color="#6a7a6a", balance="C")
N("CaH2PO42", "Triple Superphosphate", "Ca(H2PO4)2", "Solid", "Phosphate rock treated with phosphoric acid instead of sulfuric: nearly three times the phosphorus of ordinary superphosphate.", "Superphosphate#Triple_superphosphate", color="#d8d0c0")
N("KraftPulp", "Kraft Pulp", "mixture", "Solid", "Carl Dahl's sulfate pulp (Danzig, 1879): the strong brown fibre of paper bags and cardboard. 'Kraft' is German for strength.", "Kraft_process", color="#a87848", balance="C")
N("Lignin", "Lignin", "mixture", "Solid", "The aromatic glue that stiffens wood, a third of its weight. The kraft process dissolves it into black liquor, which the mill burns for power.", "Lignin", color="#5a3a1a", balance="C")
N("Wollastonite", "Calcium Silicate", "CaSiO3", "Solid", "Wollastonite, the binder of autoclaved sand-lime bricks (Michaelis, 1880) and a filler in ceramics and plastics.", "Wollastonite", color="#f0f0ec")
N("LubeOil", "Lubricating Oil", "mixture", "Liquid", "The heavy, viscous cut of crude oil, distilled under vacuum so it does not crack; it ended the age of whale oil for machinery.", "Motor_oil", color="#a07020", balance="C")
N("ParaffinWax", "Paraffin Wax", "C25H52", "Solid", "James Young's paraffin (1850) and the wax of candles, crayons and cheese rinds: long straight-chain alkanes.", "Paraffin_wax", color="#f8f4e8")
N("LiquidN2", "Liquid Nitrogen", "N2", "Liquid", "Boils at -196 C. Wroblewski and Olszewski first held it in a test tube at Krakow in 1883.", "Liquid_nitrogen", color="#e8f0ff")
N("LOX", "Liquid Oxygen", "O2", "Liquid", "Pale blue and attracted to a magnet, boiling at -183 C; the oxidiser of almost every liquid-fuelled rocket since Goddard.", "Liquid_oxygen", color="#a8c8ff")
E4.reactions += [
    R("Siemens' Dynamo", "Cu + Steel + Silk -> Dynamo", MIX,
      "Silk-wound copper coils turning in the field of a steel magnet: Siemens' dynamo-electric principle (1866) fed its own magnets from its own current.",
      wiki="Werner_von_Siemens", exact=False),
    R("Mushet's Spiegeleisen", "MnO2 + Fe + 2 Coke -> Ferromanganese + 2 CO", BLAST,
      "Manganese ore smelted with iron: added to Bessemer steel it soaks up the oxygen and sulfur that made the first batches crumble.",
      wiki="Robert_Forester_Mushet", T=1500, dh=300),
    R("Siemens Tank Furnace", "6 Sand + SodaAsh + Limestone -> Glass + 2 CO2", BLAST,
      "Friedrich Siemens' regenerative tank furnace (1867) melted glass continuously, day and night: bottles and window glass by the ton.",
      wiki="Regenerative_heat_exchanger#History", T=1500, dh=100),
    R("Ciment Fondu", "Limestone + 2 Bauxite -> CaAl2O4 + CO2 + 3 H2O", BLAST,
      "Limestone and bauxite melted right through in a furnace and cast: a cement that hardens in a day.", wiki="Calcium_aluminate_cements", T=1500, dh=200),
    R("Matte Smelting", "2 Chalcopyrite + 4 O2 -> Cu2S + 2 FeO + 3 SO2", BLAST,
      "Chalcopyrite half-roasted in the furnace: the iron burns to oxide and goes off in the slag, leaving a copper-rich matte.",
      wiki="Matte_(metallurgy)", T=1200, dh=-900),
    R("Coke Tin Smelting", "Cassiterite + 2 Coke -> Sn + 2 CO", BLAST,
      "Cornish and Malayan tin smelted with coke in reverberatory and blast furnaces from the 19th century on.", wiki="Tin#Production", T=1200, dh=360),
    R("Mannheim Furnace", "2 KCl + H2SO4 -> K2SO4 + 2 HCl", BLAST,
      "Potash salt roasted with sulfuric acid in a muffle furnace: chloride-free potassium sulfate for crops that dislike chloride, like tobacco.",
      wiki="Potassium_sulfate#Production", T=600, dh=80),
    R("Moissan's Tungsten Carbide", "WO3 + 4 Coke -> WC + 3 CO", ARC,
      "Moissan reduced tungsten oxide with carbon in his electric arc furnace (1896).", wiki="Tungsten_carbide#Synthesis", T=2000, dh=500),
    R("Titanium Carbide", "TiO2 + 3 Coke -> TiC + 2 CO", ARC,
      "Rutile reduced by carbon at 2,000 C.", wiki="Titanium_carbide", T=2000, dh=500),
    R("Tantalum Carbide", "Ta2O5 + 7 Coke -> 2 TaC + 5 CO", ARC,
      "Tantalum oxide and carbon in the arc.", wiki="Tantalum_carbide", T=2000, dh=900),
    R("Niobium Carbide", "Nb2O5 + 7 Coke -> 2 NbC + 5 CO", ARC,
      "Niobium oxide and carbon in the arc.", wiki="Niobium_carbide", T=2000, dh=900),
    R("Vanadium Carbide", "V2O5 + 7 Coke -> 2 VC + 5 CO", ARC,
      "Vanadium pentoxide reduced and carburised in one step.", wiki="Vanadium_carbide", T=2000, dh=800),
    R("Molybdenum Carbide", "2 MoO3 + 7 Coke -> Mo2C + 6 CO", ARC,
      "Molybdenum trioxide and carbon in the arc.", wiki="Molybdenum_carbide", T=1800, dh=700),
    R("Chromium Carbide", "3 Cr2O3 + 13 Coke -> 2 Cr3C2 + 9 CO", ARC,
      "Chromium oxide reduced by carbon at 1,700 C.", wiki="Chromium(II)_carbide", T=1700, dh=1500),
    R("Moissan's Aluminium Carbide", "2 Alumina + 9 Coke -> Al4C3 + 6 CO", ARC,
      "Alumina and carbon at 2,000 C give the yellow carbide that turns water into methane.", wiki="Aluminium_carbide", T=2000, dh=2500),
    R("Beryllium Carbide", "2 BeO + 3 Coke -> Be2C + 2 CO", ARC,
      "Beryllia and carbon in the arc.", wiki="Beryllium_carbide", T=2000, dh=600),
    R("Moissan's Calcium Boride", "CaO + 3 B2O3 + 10 Coke -> CaB6 + 10 CO", ARC,
      "Lime, boron oxide and carbon fused in the arc: one of the borides Moissan catalogued in 'Le Four Electrique' (1897).",
      wiki="Calcium_hexaboride", T=2000, dh=2000),
    R("Titanium Diboride", "TiO2 + B2O3 + 5 Coke -> TiB2 + 5 CO", ARC,
      "Carbothermal reduction of rutile and boron oxide together.", wiki="Titanium_diboride", T=2000, dh=1200),
    R("Calcium Silicide", "CaO + 2 Sand + 5 Coke -> CaSi2 + 5 CO", ARC,
      "Lime, quartz and coke in a submerged-arc furnace.", wiki="Calcium_silicide", T=2000, dh=1500),
    R("Ferrosilicon", "Sand + Fe + 2 Coke -> FeSi + 2 CO", ARC,
      "Quartz reduced by coke in the presence of iron scrap: silicon dissolves in the iron as it forms.", wiki="Ferrosilicon#Production", T=1800, dh=600),
    R("Smelting Ferrochrome", "Chromite + 4 Coke -> FeCr2 + 4 CO", ARC,
      "Chromite ore smelted directly with coke; the iron and chromium in it come out together.", wiki="Ferrochrome#Production", T=1700, dh=900),
    R("Ferrovanadium", "V2O5 + 2 Fe + 5 Coke -> 2 FeV + 5 CO", ARC,
      "Vanadium oxide reduced into molten iron.", wiki="Ferrovanadium", T=1800, dh=700),
    R("Norton's Alundum", "Alumina -> Alundum", ARC,
      "Charles Jacobs fused bauxite in an arc furnace in 1897; the Norton Company sold the crushed result as Alundum.", wiki="Fused_alumina", T=2100, dh=110),
    R("Heroult's Arc Steel", "PigIron + Limestone + O2 -> Steel + Slag + CO2", ARC,
      "Paul Heroult's electric arc furnace (La Praz, 1900): heat with no fuel to dirty the steel. Today it melts most of the world's scrap.",
      wiki="Electric_arc_furnace#History", exact=False, T=1650),
    R("Carbide Methane", "Al4C3 + 12 H2O -> 4 AlOH3 + 3 Methane", MIX,
      "Aluminium carbide in water fizzes out pure methane.", wiki="Aluminium_carbide#Reactions", dh=-1700),
    R("Beryllium Carbide in Water", "Be2C + 4 H2O -> 2 BeOH2 + Methane", MIX,
      "Like aluminium carbide, beryllium carbide is a methanide: water frees methane from it.", wiki="Beryllium_carbide", dh=-400),
    R("Electrowinning Zinc", "2 ZnSO4 + 2 H2O -> 2 Zn + O2 + 2 H2SO4", ECELL,
      "Zinc sulfate electrolysed onto aluminium cathodes (Anaconda, 1915); the sulfuric acid goes back to leach more roasted ore.",
      wiki="Zinc#Production", dh=500),
    R("Chlorate Cell", "KCl + 3 H2O -> KClO3 + 3 H2", ECELL,
      "Potash brine electrolysed without a diaphragm: the chlorine and caustic react in the cell and end as chlorate (Gall and Montlaur, 1886).",
      wiki="Potassium_chlorate#Production", dh=600),
    R("Perchlorate Cell", "NaClO3 + H2O -> NaClO4 + H2", ECELL,
      "Chlorate electrolysed again at a platinum anode is oxidised one step further.", wiki="Sodium_perchlorate", dh=200),
    R("Marshall's Acid", "2 H2SO4 -> H2S2O8 + H2", ECELL,
      "Cold, strong sulfuric acid electrolysed at a platinum anode at high current density.", wiki="Peroxydisulfuric_acid", dh=300),
    R("Weissenstein Peroxide", "H2S2O8 + 2 H2O -> 2 H2SO4 + H2O2", DISTIL,
      "Peroxydisulfuric acid hydrolysed and the hydrogen peroxide distilled off under vacuum (Weissenstein, Austria, 1908).",
      wiki="Hydrogen_peroxide#History", T=60, dh=-20),
    R("Electrolytic Permanganate", "2 K2MnO4 + 2 H2O -> 2 KMnO4 + 2 KOH + H2", ECELL,
      "Green manganate oxidised at a nickel anode to purple permanganate.", wiki="Potassium_permanganate#Preparation", dh=150),
    R("Griess's Diazonium", "Aniline + NaNO2 + 2 HCl -> PhN2Cl + NaCl + 2 H2O", COOL,
      "Peter Griess (1858) treated aniline with nitrous acid in ice: the diazonium salt, which would explode if allowed to dry or warm.",
      wiki="Diazonium_compound", T=2, dh=-100),
    R("Azo Coupling", "PhN2Cl + Phenol -> HydroxyAzo + HCl", FLASK,
      "The diazonium ion attacks the phenol ring opposite its OH group, joining the two rings with -N=N-.", wiki="Azo_coupling", dh=-120),
    R("Dimethylaniline", "Aniline + 2 Methanol -> Dimethylaniline + 2 H2O", CAT,
      "Aniline heated with methanol and sulfuric acid under pressure: both hydrogens on the nitrogen swapped for methyl groups.",
      wiki="Dimethylaniline", cat="H2SO4", T=220, dh=-60),
    R("Methyl Orange", "SulfanilicAcid + NaNO2 + Dimethylaniline -> MethylOrange + 2 H2O", FLASK,
      "Diazotised sulfanilic acid coupled onto dimethylaniline: the orange indicator of every titration bench since 1876.",
      wiki="Methyl_orange", dh=-150),
    R("Gattermann's Chlorobenzene", "PhN2Cl -> Chlorobenzene + N2", CAT,
      "Copper makes the diazonium group leave as nitrogen and puts chlorine in its place (Sandmeyer 1884, Gattermann 1890).",
      wiki="Sandmeyer_reaction", cat="Cu", dh=-150),
    R("Iodobenzene", "PhN2Cl + KI -> Iodobenzene + N2 + KCl", FLASK,
      "Iodide replaces the diazonium group with no catalyst at all.", wiki="Iodobenzene", dh=-150),
    R("Boiling the Diazonium", "PhN2Cl + H2O -> Phenol + N2 + HCl", HEAT,
      "Warmed in water the diazonium salt gives up its nitrogen and becomes phenol.", wiki="Diazonium_compound#Reactions", T=50, dh=-150),
    R("Skraup's Quinoline", "2 Aniline + 3 Glycerol + Nitrobenzene + H2SO4 -> 3 Quinoline + 11 H2O + H2SO4", FLASK,
      "Zdenko Skraup (1880) heated aniline, glycerol and sulfuric acid with nitrobenzene: violently, it gives quinoline, the parent of the antimalarials.",
      wiki="Skraup_reaction", T=150, dh=-100),
    R("Claisen-Schmidt Condensation", "2 Benzaldehyde + Acetone -> Dibenzalacetone + 2 H2O", FLASK,
      "Acetone reacts at both ends with benzaldehyde in alkali (1881); the yellow product drops out of the solution.",
      wiki="Claisen%E2%80%93Schmidt_condensation", dh=-80),
    R("Making Chalcone", "Benzaldehyde + Acetophenone -> Chalcone + H2O", FLASK,
      "An aldol condensation in alkali: two aromatic rings bridged by an unsaturated ketone.", wiki="Chalcone", dh=-50),
    R("Baeyer's Phenolphthalein", "PhthalicAnhydride + 2 Phenol + H2SO4 -> Phenolphthalein + H2O + H2SO4", FLASK,
      "Phthalic anhydride and phenol heated with sulfuric acid (1871).", wiki="Phenolphthalein#Synthesis", T=120, dh=-50),
    R("Disulfonating Benzene", "BSA + H2SO4 -> mBDSA + H2O", HEAT,
      "Benzenesulfonic acid takes a second sulfonic acid group in hot fuming acid, at the meta position.", wiki="Aromatic_sulfonation", T=200, dh=-50),
    R("Resorcinol by Fusion", "mBDSA + 4 NaOH -> Resorcinol + 2 Na2SO3 + 2 H2O", HEAT,
      "Both sulfonic acid groups replaced by OH in molten caustic soda, as in the phenol process.", wiki="Resorcinol#Production", T=300, dh=-100),
    R("Baeyer's Fluorescein", "PhthalicAnhydride + 2 Resorcinol -> Fluorescein + 2 H2O", FLASK,
      "Adolf von Baeyer (1871): a dye so fluorescent that a few kilograms turn the Chicago River green every St Patrick's Day.",
      wiki="Fluorescein#Synthesis", T=180, dh=-80),
    R("Caro's Eosin", "Fluorescein + 4 Br2 -> Eosin + 4 HBr", FLASK,
      "Bromine added to fluorescein in alcohol: Heinrich Caro's red dye for BASF (1874).", wiki="Eosin", dh=-200),
    R("Malonic Acid", "ClAcOH + NaCN + 2 H2O -> MalonicAcid + NaCl + NH3", FLASK,
      "Chloroacetic acid swapped onto cyanide, then the nitrile hydrolysed: Victor Dessaignes' malonic acid, first made from malic acid in 1858.",
      wiki="Malonic_acid#Preparation", T=100, dh=-150),
    R("Baeyer's Barbituric Acid", "MalonicAcid + Urea -> BarbituricAcid + 2 H2O", FLASK,
      "Baeyer condensed malonic acid with urea in 1864, reputedly naming it for a Barbara; its derivatives became the barbiturate sedatives.",
      wiki="Barbituric_acid", T=110, dh=-50),
    R("Biltz's Phenytoin", "Benzil + Urea -> Phenytoin + H2O", FLASK,
      "Heinrich Biltz made it in 1908 and nobody wanted it; in 1938 Merritt and Putnam found it stopped seizures without sedation.",
      wiki="Phenytoin#History", T=100, dh=-50),
    R("Diethylamine", "Ethylamine + Ethanol -> Diethylamine + H2O", CAT,
      "Ethylamine and ethanol over hot alumina: a second ethyl group moves onto the nitrogen.", wiki="Diethylamine", cat="Alumina", T=350, dh=-30),
    R("Einhorn's Procaine", "Benzocaine + DEAE -> Procaine + Ethanol", FLASK,
      "Alfred Einhorn (1905) swapped benzocaine's ethyl ester for diethylaminoethanol: Novocain, the dentist's first safe local anaesthetic.",
      wiki="Procaine#History", T=100, dh=-10),
    R("Werner's Cobalt Complex", "2 CoCl2 + 2 NH4Cl + 10 NH3 + H2O2 -> 2 CoAmmine + 2 H2O", FLASK,
      "Cobalt chloride in ammonia oxidised by peroxide over charcoal: orange crystals with six ammonias round each cobalt.",
      wiki="Hexamminecobalt(III)_chloride", dh=-300),
    R("Schweizer's Reagent", "CuOH2 + 4 NH3 -> Schweizer", MIX,
      "Copper hydroxide dissolves in ammonia to a deep blue solution that can dissolve paper.", wiki="Schweizer%27s_reagent", dh=-60),
    R("Cuprammonium Rayon", "Cellulose + Schweizer -> Rayon", MIX,
      "Cotton dissolved in Schweizer's reagent and spun into acid: Bemberg's silky rayon (1897).", wiki="Cuprammonium_rayon", exact=False),
    R("Leclanche Cell", "Zn + MnO2 + NH4Cl -> DryCell", MIX,
      "A zinc can, a carbon rod packed in manganese dioxide, and sal ammoniac paste: 1.5 volts.", wiki="Leclanch%C3%A9_cell", exact=False),
    R("Jungner's Nickel-Cadmium", "NiOH2 + CdOH2 -> NiCdCell", MIX,
      "Nickel hydroxide plates against cadmium in potash: the first rechargeable alkaline battery.", wiki="Nickel%E2%80%93cadmium_battery#History", exact=False),
    R("Claus Process", "2 H2S + SO2 -> 3 S + 2 H2O", CAT,
      "Carl Friedrich Claus (1883) burned a third of the hydrogen sulfide and passed it with the rest over a catalyst: now the source of most of the world's sulfur.",
      wiki="Claus_process", cat="Alumina", T=300, dh=-150),
    R("Triple Superphosphate", "PhosphateRock + 4 H3PO4 -> 3 CaH2PO42", MIX,
      "Phosphate rock dissolved in phosphoric acid: no gypsum, so far more phosphorus per bag.", wiki="Superphosphate#Triple_superphosphate", dh=-100),
    R("Kraft Pulping", "Wood + NaOH + Na2S -> KraftPulp + Lignin", PRESS,
      "Wood chips cooked under pressure in caustic soda and sodium sulfide: the lignin dissolves and the cellulose fibres stay strong.",
      wiki="Kraft_process", exact=False, T=170, P=8),
    R("Sand-Lime Brick", "Ca(OH)2 + Sand -> Wollastonite + H2O", PRESS,
      "Lime and sand pressed into bricks and steamed in an autoclave: calcium silicate binds them (Michaelis, 1880).",
      wiki="Sand-lime_brick", T=190, P=12, dh=-90),
    R("Vacuum Distillation", "Bitumen -> LubeOil + ParaffinWax", COLUMN,
      "The residue of crude oil distilled again under vacuum, below the temperature at which it would crack: lubricating oils and wax.",
      wiki="Vacuum_distillation#Industrial-scale_application", exact=False, T=400),
    R("Liquid Nitrogen", "N2 -> LiquidN2", AIRLIQ,
      "Nitrogen cooled by boiling ethylene and expanded until it condensed (Wroblewski and Olszewski, 1883).", wiki="Liquid_nitrogen", T=-196, dh=-5.6),
    R("Liquid Oxygen", "O2 -> LOX", AIRLIQ,
      "Raoul Pictet and Louis Cailletet each produced a mist of liquid oxygen in December 1877; a test-tube of it followed in 1883.",
      wiki="Liquid_oxygen", T=-183, dh=-6.8),
    R("Roasting Zinc Blende", "2 Sphalerite + 3 O2 -> 2 ZnO + 2 SO2", HEAT,
      "Zinc sulfide roasted in air to the oxide, the first step of every zinc smelter.", wiki="Zinc_smelting#Roasting", T=900, dh=-880),
]

# --- E5: Modern ----------------------------------------------------------------------
L("Streptomycin", "Streptomycin", "C21H39N7O12", "Solid")
L("Erythromycin", "Erythromycin", "C37H67NO13", "Solid")
L("Tetracycline", "(-)-Tetracycline", "C22H24N2O8", "Solid", name="Tetracycline")
N("Dextran", "Dextran", "(C6H10O5)n", "Solid", "A glucose polymer slimed out by Leuconostoc bacteria in sugar refineries; Swedish chemists made it the first blood-plasma substitute (1947).", "Dextran", balance="C6H10O5", props=["IsPolymer"])
N("VitaminB12", "Vitamin B12", "C63H88CoN14O14P", "Solid", "Cyanocobalamin, the only vitamin built around a metal atom. Dorothy Hodgkin solved its structure by X-ray crystallography in 1956; bacteria are its only makers.", "Vitamin_B12", color="#c02030")
N("6APA", "6-Aminopenicillanic Acid", "C8H12N2O3S", "Solid", "The bare penicillin core, isolated by Beecham's scientists in 1957: hang any side chain on it and you have a new penicillin.", "6-APA", smiles="CC1(C)S[C@@H]2[C@H](N)C(=O)N2[C@H]1C(=O)O")
N("Phenylglycine", "Phenylglycine", "C8H9NO2", "Solid", "An amino acid not found in proteins, made by the Strecker synthesis from benzaldehyde; the side chain of ampicillin.", "Phenylglycine", smiles="NC(C(=O)O)c1ccccc1")
L("Ampicillin", "Ampicillin", "C16H19N3O4S", "Solid", smiles="CC1(C)S[C@@H]2[C@H](NC(=O)[C@H](N)c3ccccc3)C(=O)N2[C@H]1C(=O)O")
L("2EH", "2-Ethylhexanol", "C8H18O", "Liquid", smiles="CCCCC(CC)CO")
L("DEHP", "Dioctyl phthalate", "C24H38O4", "Liquid", smiles="CCCCC(CC)COC(=O)c1ccccc1C(=O)OCC(CC)CCCC")
L("Butynediol", "2-Butyne-1,4-diol", "C4H6O2", "Solid", smiles="OCC#CCO")
N("BDO", "1,4-Butanediol", "C4H10O2", "Liquid", "A four-carbon diol from Reppe's acetylene chemistry; it becomes spandex, PBT plastic and the solvent THF.", "1,4-Butanediol", smiles="OCCCCO")
L("GBL", "γ-Butyrolactone", "C4H6O2", "Liquid", name="gamma-Butyrolactone", smiles="O=C1CCCO1")
N("QuartzCrystal", "Cultured Quartz", "SiO2", "Solid", "Single quartz crystals grown from hot alkaline water in steel autoclaves; Bell Labs' process (1950s) freed radio and clock makers from Brazilian mines.", "Hydrothermal_synthesis#Synthetic_quartz", color="#f4f8ff")
N("ZeoliteA", "Zeolite A", "mixture", "Solid", "Robert Milton's synthetic zeolite (Union Carbide, 1949): a cage of aluminosilicate that swaps sodium for calcium, so it softens water and replaced phosphate in detergents.", "Zeolite#Synthetic", color="#f8f8f4", balance="NaAlSiO4")
N("HeavyWater", "Heavy Water", "D2O", "Liquid", "Water whose hydrogen is deuterium, 11% denser. Norsk Hydro at Vemork concentrated it from 1934; Canada's CANDU reactors use it to run on unenriched uranium.", "Heavy_water", color="#d0e8ff", balance="H2O")
N("LNG", "Liquefied Natural Gas", "mixture", "Liquid", "Natural gas chilled to -162 C shrinks 600-fold; the Methane Pioneer carried the first cargo across the Atlantic in 1959.", "Liquefied_natural_gas", color="#e0f0ff", balance="C")
N("SuperfluidHe", "Superfluid Helium", "He", "Liquid", "Below 2.17 K liquid helium-4 flows with no viscosity at all and climbs out of its beaker: Kapitza, Allen and Misener, 1937.", "Superfluid_helium-4", color="#f0f8ff")
N("EnrichedUF6", "Enriched Uranium Hexafluoride", "UF6", "Solid", "UF6 with its uranium-235 raised from 0.7% to a few percent. Oak Ridge's K-25 plant, a mile-long building, pumped it through porous barriers 3,000 times.", "Enriched_uranium", props=["IsRadioactive"])
N("EnrichedUranium", "Enriched Uranium", "U", "Solid", "Uranium fuel rich in the fissile isotope 235; a few kilograms hold the energy of thousands of tonnes of coal.", "Enriched_uranium", props=["IsMetal", "IsRadioactive"])
N("Cobalt60", "Cobalt-60", "Co", "Solid", "Gamma-emitting cobalt (half-life 5.3 years) made in reactors. The first cobalt-60 cancer treatments were given in Canada, at Saskatoon and London, Ontario, in 1951.", "Cobalt-60", props=["IsMetal", "IsRadioactive"])
N("Molybdenum99", "Molybdenum-99", "Mo", "Solid", "A fission product (half-life 66 hours) that decays to technetium-99m, the tracer of 40 million medical scans a year; Chalk River's NRU reactor once made a third of it.", "Molybdenum-99", props=["IsMetal", "IsRadioactive"])
N("Iodine131", "Iodine-131", "I2", "Solid", "A fission product (half-life 8 days) that the thyroid concentrates, so it both treats thyroid cancer and is the main hazard of reactor accidents.", "Iodine-131", props=["IsRadioactive"])
N("Strontium90", "Strontium-90", "Sr", "Solid", "A fission product (half-life 29 years) that the body files as calcium in bone; its rise in children's teeth helped end atmospheric bomb tests (1963).", "Strontium-90", props=["IsMetal", "IsRadioactive"])
N("Caesium137", "Caesium-137", "Cs", "Solid", "A fission product (half-life 30 years), the long-lived contamination of Chernobyl and Fukushima, and a calibration source for radiation meters.", "Caesium-137", props=["IsMetal", "IsRadioactive"])
N("Tritium", "Tritium", "H2", "Gas", "Hydrogen-3 (half-life 12.3 years), bred from lithium-6 in reactors; it lights exit signs and watch dials and fuels fusion experiments.", "Tritium", props=["IsRadioactive"])
N("Carbon14", "Carbon-14", "C", "Solid", "Made from nitrogen by neutrons, in the upper air and in reactors; Willard Libby used its 5,730-year half-life to date the past (1949).", "Carbon-14", props=["IsRadioactive"])
N("Plutonium238", "Plutonium-238", "Pu", "Solid", "Glows red with its own heat (half-life 88 years): the fuel of the radioisotope generators powering Voyager, Cassini and Perseverance.", "Plutonium-238", props=["IsMetal", "IsRadioactive"])
N("Uranium233", "Uranium-233", "U", "Solid", "Fissile uranium bred from thorium-232, the fuel of the thorium cycle tested at Oak Ridge's Molten-Salt Reactor (1965-69).", "Uranium-233", props=["IsMetal", "IsRadioactive"])
N("Iridium192", "Iridium-192", "Ir", "Solid", "A gamma source (half-life 74 days) used to radiograph welds in pipelines and to treat cancers from inside (brachytherapy).", "Iridium-192", props=["IsMetal", "IsRadioactive"])
N("Technetium99m", "Technetium-99m", "Tc", "Solid", "Metastable technetium (half-life 6 hours) milked from a molybdenum generator at the hospital (Brookhaven, 1958): the most used medical isotope.", "Technetium-99m", props=["IsMetal", "IsRadioactive"])
N("Sodium24", "Sodium-24", "Na", "Solid", "Ernest Lawrence's cyclotron made 'radio-sodium' in 1934, and his brother John used it in some of the first radiotracer medicine.", "Isotopes_of_sodium#Sodium-24", props=["IsMetal", "IsRadioactive"])
N("GeCrystal", "Germanium Crystal", "Ge", "Solid", "Gordon Teal and John Little pulled single crystals of germanium at Bell Labs in 1948; transistors made from them worked far better than from polycrystals.", "Czochralski_method#History")
N("GaAs", "Gallium Arsenide", "GaAs", "Solid", "A semiconductor whose electrons move six times faster than in silicon and which emits light: lasers, LEDs, mobile-phone amplifiers and space solar cells.", "Gallium_arsenide", color="#4a4a58")
N("Sapphire", "Synthetic Sapphire", "Al2O3", "Solid", "Single-crystal alumina grown from the melt by Kyropoulos's method (1926): watch glasses, scanner windows and the substrate of blue LEDs.", "Sapphire#Synthetic_sapphire", color="#d8e8f8")
N("NdYAG", "Nd:YAG Crystal", "Y3Al5O12", "Solid", "Yttrium aluminium garnet doped with neodymium (Geusic, Bell Labs, 1964): the infrared laser of surgery, tattoo removal and range-finders.", "Nd:YAG_laser", color="#e0b0e0")
N("LiNbO3", "Lithium Niobate", "LiNbO3", "Solid", "A crystal that squeezes out voltage when pressed and bends light under voltage: the modulators of fibre-optic networks and green laser pointers.", "Lithium_niobate", color="#f0f0f8")
N("OxidisedWafer", "Oxidised Wafer", "SiO2", "Solid", "Mohamed Atalla found in 1957 that a thin thermal oxide 'passivates' silicon's surface so electrons stop getting trapped there: the trick behind every chip.", "Surface_passivation", balance="SiO2")
N("MOSFET", "MOSFET", "mixture", "Solid", "Atalla and Dawon Kahng's metal-oxide-semiconductor field-effect transistor (1959), the most manufactured device in history, over 10^22 so far.", "MOSFET", balance="Si")
N("LaserDiode", "Laser Diode", "mixture", "Solid", "Robert Hall's GaAs diode laser (GE, 1962); heterostructures of AlGaAs (Alferov, Kroemer, Nobel 2000) made it work at room temperature, and then in every CD player.", "Laser_diode", balance="C")
N("CubicBN", "Cubic Boron Nitride", "BN", "Solid", "Borazon (Robert Wentorf, GE, 1957), second only to diamond in hardness and stable in air to 1,300 C, so it grinds the hardened steels that dissolve diamond.", "Boron_nitride#Cubic_boron_nitride", color="#c8a060")
N("Coesite", "Coesite", "SiO2", "Solid", "A dense form of silica Loring Coes made at 35,000 atmospheres in 1953; found in nature in 1960 at Meteor Crater, it became the fingerprint of an impact.", "Coesite", color="#f0f0f0")
N("Stishovite", "Stishovite", "SiO2", "Solid", "Silica with silicon six-coordinated like in rutile, made by Sergei Stishov at 100,000 atmospheres (1961): the densest silica.", "Stishovite", color="#f8f8f8")
N("BlackP", "Black Phosphorus", "P", "Solid", "Percy Bridgman squeezed white phosphorus to 12,000 atmospheres in 1914 and got a flaky black solid like graphite; peeled to one layer it is phosphorene.", "Allotropes_of_phosphorus#Black_phosphorus", color="#2a2a30")
N("Carboloy", "Cemented Carbide", "WC-Co", "Solid", "Tungsten carbide grains sintered in cobalt (Krupp's Widia, 1926; GE's Carboloy, 1928): 'wie Diamant'. It made the anvils of the diamond press.", "Cemented_carbide", color="#5a5a62", balance="WCCo")
N("Li3N", "Lithium Nitride", "Li3N", "Solid", "Lithium is the only metal that burns in nitrogen at room temperature; the red-purple nitride is the flux of cubic boron nitride synthesis.", "Lithium_nitride", color="#a03050")
L("TMA", "Trimethylaluminum", "Al2(CH3)6", "Liquid", name="Trimethylaluminium")
N("LiAlH4", "Lithium Aluminium Hydride", "LiAlH4", "Solid", "Finholt, Bond and Schlesinger's hydride (1947), the reagent that reduces almost any carbonyl group to an alcohol; it ignites with water.", "Lithium_aluminium_hydride")
L("TMB", "Trimethyl borate", "C3H9BO3", "Liquid", smiles="COB(OC)OC")
L("NaOMe", "Sodium methoxide", "CH3ONa", "Solid", smiles="C[O-].[Na+]")
N("NaBH4", "Sodium Borohydride", "NaBH4", "Solid", "H. C. Brown's gentle reducing agent (1942, with Schlesinger, while looking for volatile uranium compounds for the bomb): it reduces aldehydes and ketones even in water.", "Sodium_borohydride")
N("Ferrocene", "Ferrocene", "Fe(C5H5)2", "Solid", "An iron atom sandwiched between two cyclopentadienyl rings (Kealy and Pauson, 1951). Wilkinson and Fischer, who worked out sandwich compounds, shared the 1973 Nobel.", "Ferrocene", color="#e07020", balance="FeC10H10")
L("NaNH2", "Sodium amide", "NaNH2", "Solid", name="Sodamide")
N("RubyLaser", "Ruby Laser", "mixture", "Solid", "Theodore Maiman's ruby rod in a coiled flash lamp (Hughes, 16 May 1960) gave the first laser light, deep red at 694 nm.", "Ruby_laser", color="#e02040", balance="C")
N("PtF6", "Platinum Hexafluoride", "PtF6", "Gas", "A dark red, astonishingly strong oxidiser that can tear an electron off an oxygen molecule.", "Platinum_hexafluoride", color="#a01818")
N("XePtF6", "Xenon Hexafluoroplatinate", "XePtF6", "Solid", "Neil Bartlett, at the University of British Columbia in 1962, mixed xenon with PtF6 and got an orange-yellow solid: the first noble gas compound.", "Xenon_hexafluoroplatinate", color="#e8b020")
N("XeF4", "Xenon Tetrafluoride", "XeF4", "Solid", "Colourless crystals made weeks after Bartlett's discovery at Argonne by heating xenon and fluorine (1962); the 'inert' gases were inert no more.", "Xenon_tetrafluoride")
N("XeF2", "Xenon Difluoride", "XeF2", "Solid", "Forms when xenon and fluorine are left in sunlight; etches silicon in chip making.", "Xenon_difluoride")
E5.reactions += [
    R("Currie's Citric Acid", "2 Glucose + 3 O2 -> 2 Citric + 4 H2O", BIOR,
      "James Currie (1917) floated Aspergillus niger on sugared water; Pfizer scaled it up and ended Italy's citrus monopoly.",
      wiki="Citric_acid#Production", cat="Aspergillus", T=30, dh=-1500),
    R("Waksman's Streptomycin", "Glucose + CornSteep -> Streptomycin", BIOR,
      "Albert Schatz, in Selman Waksman's lab (1943), found the first drug against tuberculosis in a Streptomyces from a chicken's throat.",
      wiki="Streptomycin#History", cat="Streptomyces", exact=False, T=28),
    R("Erythromycin", "Glucose + Propionic -> Erythromycin", BIOR,
      "Abelardo Aguilar sent Eli Lilly a soil sample from Iloilo in 1949; its Streptomyces made erythromycin from propionate units.",
      wiki="Erythromycin#History", cat="Streptomyces", exact=False, T=30),
    R("Duggar's Tetracycline", "Starch + CornSteep -> Tetracycline", BIOR,
      "Benjamin Duggar's golden Streptomyces aureofaciens (1948) gave the first tetracycline, a broad-spectrum antibiotic.",
      wiki="Tetracycline_antibiotics#History", cat="Streptomyces", exact=False, T=28),
    R("Kinoshita's Glutamate", "2 Glucose + 2 NH3 + 3 O2 -> 2 GlutamicAcid + 2 CO2 + 6 H2O", BIOR,
      "Kyowa Hakko (1956): bacteria fed sugar and ammonia excrete glutamic acid, and MSG no longer needs wheat gluten.",
      wiki="Corynebacterium_glutamicum", cat="Corynebacterium", T=30, dh=-1000),
    R("Fermenting Lysine", "Glucose + NH3 -> Lysine", BIOR,
      "A mutant of the glutamate bacterium makes lysine instead (1958), now added by the million tonnes to animal feed.",
      wiki="Lysine#Production", cat="Corynebacterium", exact=False, T=30),
    R("Dextran", "Sucrose -> Dextran + Fructose", BIOR,
      "Leuconostoc's enzyme strings the glucose halves of sucrose into dextran and lets the fructose go.", wiki="Dextran", dh=-20),
    R("Glucose Isomerase", "Glucose -> Fructose", BIOR,
      "An enzyme from Streptomyces turns glucose into sweeter fructose (Clinton Corn, 1967): high-fructose corn syrup.",
      wiki="Xylose_isomerase", cat="Streptomyces", T=60, dh=3),
    R("Fermenting Vitamin B12", "Glucose + Co + CornSteep -> VitaminB12", BIOR,
      "Only bacteria can build cobalamin; Merck's process (1948) used Streptomyces, today Pseudomonas denitrificans.",
      wiki="Vitamin_B12#Industrial_production", exact=False, T=30),
    R("Penicillin Acylase", "Penicillin + H2O -> 6APA + PhenylaceticAcid", BIOR,
      "An E. coli enzyme snips penicillin G's side chain off cleanly, freeing the 6-APA core for new semi-synthetic penicillins.",
      wiki="Penicillin_amidase", cat="Ecoli", T=37, dh=-20),
    R("Strecker Phenylglycine", "Benzaldehyde + HCN + H2O -> Phenylglycine", FLASK,
      "Benzaldehyde, cyanide and ammonia give an aminonitrile, hydrolysed to the amino acid: Adolph Strecker's 1850 method.",
      wiki="Strecker_amino_acid_synthesis", dh=-100),
    R("Beecham's Ampicillin", "6APA + Phenylglycine -> Ampicillin + H2O", FLASK,
      "Phenylglycine hung on the penicillin core (1961): the first penicillin that works against Gram-negative bacteria too.",
      wiki="Ampicillin#History", dh=-20),
    R("Oxo Alcohol", "2 Butanal + 2 H2 -> 2EH + H2O", HIGHP,
      "Butanal aldol-condensed and hydrogenated: 2-ethylhexanol, the alcohol of the plasticisers that make PVC flexible.",
      wiki="2-Ethylhexanol#Production", cat="Ni", T=150, P=30, dh=-200),
    R("Plasticiser DEHP", "PhthalicAnhydride + 2 2EH -> DEHP + H2O", CAT,
      "Phthalic anhydride esterified with 2-ethylhexanol: the plasticiser in vinyl flooring, cables and, once, medical tubing.",
      wiki="Bis(2-ethylhexyl)_phthalate", cat="H2SO4", T=150, dh=-40),
    R("Reppe's Butynediol", "Acetylene + 2 CH2O -> Butynediol", HIGHP,
      "Walter Reppe at BASF tamed acetylene under pressure (1930s), adding formaldehyde to both ends over copper acetylide.",
      wiki="Walter_Reppe", cat="Cu", T=100, P=5, dh=-200),
    R("Butanediol", "Butynediol + 2 H2 -> BDO", HIGHP,
      "The triple bond hydrogenated over nickel at 250 atmospheres.", wiki="1,4-Butanediol#Production", cat="Ni", T=100, P=250, dh=-280),
    R("Gamma-Butyrolactone", "BDO -> GBL + 2 H2", CAT,
      "Butanediol dehydrogenated over copper closes into a lactone ring.", wiki="Gamma-Butyrolactone#Production", cat="Cu", T=250, dh=60),
    R("Hydrodesulfurisation", "Thiophene + 4 H2 -> Butane + H2S", CRACKER,
      "Sulfur ripped out of fuel as hydrogen sulfide over cobalt-molybdenum sulfide; the sulfur goes to the Claus unit.",
      wiki="Hydrodesulfurization", cat="MoS2", T=350, P=50, dh=-260),
    R("Butane Isomerisation", "Butane -> Isobutane", CRACKER,
      "Straight butane rearranged to branched isobutane (1941), more of the feed the alkylation unit needs.",
      wiki="Isomerization#Petroleum_refining", cat="AlCl3", T=100, dh=-8),
    R("Vanadium Contact Process", "2 SO2 + O2 -> 2 SO3", CRACKER,
      "BASF switched from platinum to vanadium pentoxide in 1915: cheaper and not poisoned by arsenic.", wiki="Contact_process#Catalyst",
      cat="V2O5", T=450, dh=-198),
    R("Hydrocracking", "Hexadecane + H2 -> 2 Octane", CRACKER,
      "Heavy oil cracked in hydrogen over palladium on zeolite (Chevron Isocracking, 1959): jet fuel and diesel with no sulfur.",
      wiki="Cracking_(chemistry)#Hydrocracking", cat="Pd", T=400, P=100, dh=-40),
    R("Hydrothermal Quartz", "Sand -> QuartzCrystal", PRESS,
      "Crushed quartz dissolved in hot caustic water at the bottom of an autoclave recrystallises on seed plates at the cooler top.",
      wiki="Hydrothermal_synthesis", T=350, P=1000, dh=0.1),
    R("Milton's Zeolite A", "NaAlOH4 + Na2SiO3 -> ZeoliteA", PRESS,
      "Sodium aluminate and sodium silicate gels heated in a sealed vessel crystallise into zeolite cages (1949).",
      wiki="Zeolite#Production", exact=False, T=100),
    R("Baizer's Adiponitrile", "4 Acrylonitrile + 2 H2O -> 2 Adiponitrile + O2", ECELL,
      "Manuel Baizer (Monsanto, 1965) joined acrylonitrile molecules tail to tail at a lead cathode: the largest organic electrosynthesis, for nylon.",
      wiki="Adiponitrile#Production", dh=300),
    R("Norsk Hydro's Heavy Water", "H2O -> HeavyWater", ECELL,
      "Heavy water concentrates in the residue of electrolysis cells; Vemork's was the target of the Allied sabotage raids of 1943.",
      wiki="Norsk_Hydro_heavy_water_sabotage", exact=False),
    R("Electrolytic Manganese", "2 MnSO4 + 2 H2O -> 2 Mn + O2 + 2 H2SO4", ECELL,
      "Manganese plated from purified sulfate solution: 99.9% pure, for aluminium alloys and batteries.", wiki="Manganese#Production", dh=500),
    R("Bacon's Fuel Cell", "2 H2 + O2 -> 2 H2O", ECELL,
      "Francis Bacon's alkaline fuel cell (demonstrated in 1959) became the power plant, and the water supply, of the Apollo command modules.",
      wiki="Alkaline_fuel_cell#History", dh=-572),
    R("Liquefied Natural Gas", "NaturalGas -> LNG", AIRLIQ,
      "Natural gas cooled by cascades of propane, ethylene and methane refrigeration until it condenses.", wiki="Liquefied_natural_gas#Production",
      exact=False, T=-162),
    R("Kapitza's Superfluid", "LiquidHe -> SuperfluidHe", CRYO,
      "Liquid helium pumped down below 2.17 K stops boiling, goes still, and leaks through cracks nothing else can pass.",
      wiki="Superfluidity#History", T=-271.0, dh=-0.01),
    R("Gaseous Diffusion", "UF6 -> EnrichedUF6", COLUMN,
      "Lighter 235-UF6 drifts through porous barriers a fraction faster than 238-UF6; thousands of stages in series enrich it (K-25, 1945).",
      wiki="Gaseous_diffusion", exact=False),
    R("Fuel Pellets", "EnrichedUF6 + H2 -> EnrichedUranium + HF", HEAT,
      "Enriched hexafluoride converted back to oxide and pressed into the ceramic pellets stacked in fuel rods.", wiki="Nuclear_fuel#Oxide_fuel",
      exact=False, T=700),
    R("Goddard's Rocket", "2 Kerosene + 37 LOX -> 24 CO2 + 26 H2O", HEAT,
      "Robert Goddard's first liquid-fuelled rocket flew 12 metres high at Auburn, Massachusetts, on 16 March 1926: gasoline and liquid oxygen.",
      wiki="Robert_H._Goddard", dh=-15000),
    R("Hydrolox", "2 LiquidH2 + LOX -> 2 H2O", HEAT,
      "Liquid hydrogen and liquid oxygen, the most efficient chemical rocket fuel: Centaur (1962) and the Saturn V's upper stages.",
      wiki="Liquid_rocket_propellant#Hydrogen", dh=-572),
    R("Lithium Nitride", "6 Li + N2 -> 2 Li3N", HEAT,
      "Lithium tarnishes red-purple in nitrogen, uniquely among metals at room temperature.", wiki="Lithium_nitride", dh=-330),
    R("Chalk River Cobalt-60", "Co + EnrichedUranium -> Cobalt60", REACTOR,
      "Cobalt rods soaked in a reactor's neutrons for a year become intensely gamma-active; Eldorado and AECL built the first therapy units around them.",
      wiki="Cobalt-60#Production", exact=False),
    R("Fission Products", "EnrichedUranium -> Molybdenum99 + Iodine131 + Strontium90 + Caesium137", REACTOR,
      "A uranium-235 nucleus split by a neutron breaks unevenly into two lighter nuclei, with two or three more neutrons to carry on the chain.",
      wiki="Nuclear_fission_product", exact=False),
    R("Breeding Tritium", "Li + EnrichedUranium -> Tritium", REACTOR,
      "Lithium-6 hit by a neutron splits into helium and tritium (Savannah River, 1950s).", wiki="Tritium#Production", exact=False),
    R("Libby's Carbon-14", "N2 + EnrichedUranium -> Carbon14", REACTOR,
      "A neutron knocks a proton out of nitrogen-14 and leaves carbon-14, exactly as cosmic rays do in the upper air.", wiki="Carbon-14#Formation", exact=False),
    R("Plutonium-238", "Np + EnrichedUranium -> Plutonium238", REACTOR,
      "Neptunium-237 targets irradiated in a reactor capture a neutron and decay to plutonium-238.", wiki="Plutonium-238#Production", exact=False),
    R("Breeding Uranium-233", "Th + EnrichedUranium -> Uranium233", REACTOR,
      "Thorium-232 captures a neutron and decays in a month through protactinium to fissile uranium-233.", wiki="Thorium_fuel_cycle", exact=False),
    R("Iridium-192", "Ir + EnrichedUranium -> Iridium192", REACTOR,
      "Iridium pellets activated in a reactor become the gamma cameras of pipeline welders.", wiki="Iridium-192", exact=False),
    R("CANDU", "U + HeavyWater -> Pu", REACTOR,
      "Heavy water slows neutrons without swallowing them, so natural uranium can sustain a chain reaction: Canada's NPD (1962) and CANDU reactors.",
      wiki="CANDU_reactor", exact=False),
    R("Technetium Generator", "Molybdenum99 + NaCl -> Technetium99m", FLASK,
      "Saline washed through an alumina column holding molybdate elutes the technetium its decay leaves behind (Brookhaven, 1958).",
      wiki="Technetium-99m_generator", exact=False),
    R("Lawrence's Radiosodium", "Na -> Sodium24", CYCLO,
      "Sodium bombarded with deuterons in the 27-inch cyclotron (1934).", wiki="Ernest_Lawrence", exact=False),
    R("Teal's Germanium", "Ge -> GeCrystal", PULLER,
      "A seed crystal dipped into molten germanium and drawn slowly upward, rotating, grows into one perfect crystal.", wiki="Gordon_Kidd_Teal", T=938),
    R("Gallium Arsenide", "Ga + As -> GaAs", PULLER,
      "Grown under a cap of molten boron oxide so the arsenic cannot boil away (liquid-encapsulated Czochralski, 1965).",
      wiki="Gallium_arsenide#Preparation_and_chemistry", T=1238, dh=-71),
    R("Kyropoulos Sapphire", "Alumina -> Sapphire", PULLER,
      "Alumina melted and cooled from a seed so slowly that a boule of single crystal half a metre across can grow.", wiki="Kyropoulos_method",
      T=2050, dh=0.1),
    R("Nd:YAG", "3 Y2O3 + 5 Alumina + Nd -> NdYAG", PULLER,
      "Yttria, alumina and a percent of neodymium melted and pulled as a garnet crystal.", wiki="Yttrium_aluminium_garnet", exact=False, T=1970),
    R("Lithium Niobate", "Li2CO3 + Nb2O5 -> 2 LiNbO3 + CO2", PULLER,
      "Lithium carbonate and niobium oxide reacted, melted and pulled (Ballman, Bell Labs, 1965).", wiki="Lithium_niobate", T=1250, dh=-40),
    R("Atalla's Thermal Oxide", "Wafer + O2 -> OxidisedWafer", CVD,
      "Silicon heated in dry oxygen grows a glassy skin of silica a few hundred atoms thick.", wiki="Thermal_oxidation", exact=False, T=1000),
    R("Atalla and Kahng's MOSFET", "OxidisedWafer + Al -> MOSFET", CVD,
      "An aluminium gate over the thin oxide: its voltage opens and closes a channel in the silicon beneath.", wiki="MOSFET#History", exact=False),
    R("Hall's Laser Diode", "GaAs + Al -> LaserDiode", CVD,
      "Layers of aluminium gallium arsenide grown onto GaAs trap electrons and light in a thin stripe.", wiki="Laser_diode#History", exact=False),
    R("Wentorf's Borazon", "BN -> CubicBN", DPRESS,
      "Hexagonal boron nitride pressed to 60,000 atmospheres at 1,700 C in a lithium nitride flux (1957).", wiki="Robert_H._Wentorf_Jr.",
      cat="Li3N", T=1700, P=60000, dh=-15),
    R("Coes' Coesite", "Sand -> Coesite", DPRESS,
      "Quartz squeezed to 35,000 atmospheres at 750 C in a sodium-metasilicate flux (Norton Company, 1953).", wiki="Coesite", T=750, P=35000, dh=3),
    R("Stishov's Stishovite", "Coesite -> Stishovite", DPRESS,
      "Silica pushed past 100,000 atmospheres collapses into a rutile-like lattice.", wiki="Stishovite", T=1200, P=100000, dh=50),
    R("Bridgman's Black Phosphorus", "P4 -> 4 BlackP", DPRESS,
      "White phosphorus held at 12,000 atmospheres and 200 C turns into black, flaky crystals that conduct electricity.",
      wiki="Percy_Williams_Bridgman", T=200, P=12000, dh=-160),
    R("Carboloy", "WC + Co -> Carboloy", ARC,
      "Tungsten carbide powder and cobalt pressed and sintered just below cobalt's melting point.", wiki="Cemented_carbide#History", T=1450, dh=-5),
    R("Ziegler's Aluminium Alkyl", "2 Al + 6 CH3Cl + 6 Na -> TMA + 6 NaCl", FLASK,
      "Aluminium, chloromethane and sodium give trimethylaluminium, which bursts into flame in air; Karl Ziegler's aluminium alkyls made polythene catalysts.",
      wiki="Trimethylaluminium#Preparation", dh=-1200),
    R("Schlesinger's Hydride", "4 LiH + AlCl3 -> LiAlH4 + 3 LiCl", FLASK,
      "Lithium hydride and aluminium chloride stirred in dry ether (Chicago, 1947).", wiki="Lithium_aluminium_hydride#Preparation", dh=-200),
    R("Reducing Acetone", "4 Acetone + LiAlH4 + 4 H2O -> 4 Isopropanol + LiOH + AlOH3", FLASK,
      "Each hydride on the aluminium adds to a carbonyl; water then frees the alcohol.", wiki="Lithium_aluminium_hydride#Applications", dh=-400),
    R("Trimethyl Borate", "H3BO3 + 3 Methanol -> TMB + 3 H2O", CAT,
      "Boric acid esterified with methanol; it burns with a green flame.", wiki="Trimethyl_borate", cat="H2SO4", T=60, dh=-20),
    R("Brown's Borohydride", "4 NaH + TMB -> NaBH4 + 3 NaOMe", FLASK,
      "Sodium hydride stirred into trimethyl borate at 250 C (Schlesinger and Brown, 1942).", wiki="Sodium_borohydride#Synthesis", T=250, dh=-200),
    R("Borohydride Reduction", "4 Benzaldehyde + NaBH4 + 4 H2O -> 4 BenzylAlcohol + NaOH + H3BO3", FLASK,
      "Borohydride reduces the aldehyde to the alcohol and leaves other groups alone.", wiki="Sodium_borohydride#Applications", dh=-300),
    R("Making Ferrocene", "FeCl2 + 2 Cyclopentadiene + 2 KOH -> Ferrocene + 2 KCl + 2 H2O", FLASK,
      "Cyclopentadiene deprotonated by potash wraps around ferrous iron: orange crystals stable to 400 C.", wiki="Ferrocene#Synthesis", dh=-150),
    R("Making Sodamide", "2 Na + 2 LiquidNH3 -> 2 NaNH2 + H2", COOL,
      "Sodium dissolves blue in liquid ammonia; a speck of iron catalyses its slow reaction to grey sodamide.", wiki="Sodium_amide#Preparation", T=-33, dh=-120),
    R("Diethylaminoethanol", "Diethylamine + EO -> DEAE", FLASK,
      "Ethylene oxide's strained ring opens on the amine nitrogen.", wiki="Diethylethanolamine", dh=-100),
    R("Maiman's Laser", "Ruby + Xe -> RubyLaser", LIGHT,
      "A xenon flash lamp coiled round a silvered ruby rod pumps its chromium ions until they emit together.", wiki="Theodore_Maiman", exact=False),
    R("Platinum Hexafluoride", "Pt + 3 F2 -> PtF6", HEAT,
      "Platinum wire burned in fluorine (Weinstock, 1957).", wiki="Platinum_hexafluoride", T=700, dh=-680),
    R("Bartlett's Noble Gas Compound", "Xe + PtF6 -> XePtF6", MIX,
      "Bartlett had seen PtF6 oxidise O2; xenon has almost the same ionisation energy, so he tried it on 23 March 1962. The gases reacted at once.",
      wiki="Neil_Bartlett_(chemist)", dh=-200),
    R("Xenon Tetrafluoride", "Xe + 2 F2 -> XeF4", HEAT,
      "Xenon and fluorine heated in a nickel can at 400 C (Claassen, Selig and Malm, 1962).", wiki="Xenon_tetrafluoride", T=400, dh=-251),
    R("Xenon Difluoride", "Xe + F2 -> XeF2", LIGHT,
      "Xenon and fluorine in a glass bulb on a sunny windowsill slowly grow crystals of the difluoride.", wiki="Xenon_difluoride#Synthesis", dh=-108),
    R("Imperial Smelting", "ZnO + Coke -> Zn + CO", BLAST,
      "The Imperial Smelting furnace (Avonmouth, 1950s) smelts zinc and lead together and catches the zinc vapour in a shower of molten lead.",
      wiki="Zinc_smelting#Imperial_Smelting_Process", T=1100, dh=237),
    R("Midrex Direct Reduction", "Hematite + 3 CO -> 2 Fe + 3 CO2", BLAST,
      "Iron ore pellets reduced in a shaft by reformed natural gas without ever melting (Midrex, 1969): sponge iron for electric furnaces.",
      wiki="Direct_reduced_iron", T=900, dh=-25),
]

# --- E6: Frontier --------------------------------------------------------------------
N("Insulin", "Human Insulin", "C257H383N65O77S6", "Solid", "Banting and Best's hormone (Toronto, 1921) came from pig and cow pancreas until Genentech had E. coli make the human protein (1978).", "Insulin_(medication)#History")
N("Chymosin", "Chymosin", "mixture", "Solid", "The milk-clotting enzyme of calf rennet. Made by microbes since 1990, it now curdles most of the world's cheese.", "Chymosin", balance="C")
N("PDO", "1,3-Propanediol", "C3H8O2", "Liquid", "A diol DuPont and Genencor taught E. coli to make from corn sugar (2006), for the polyester Sorona.", "1,3-Propanediol", smiles="OCCCO")
N("ArtemisinicAcid", "Artemisinic Acid", "C15H22O2", "Solid", "The precursor of artemisinin, made by yeast given wormwood genes (Jay Keasling, 2006; Sanofi production 2013).", "Artemisinic_acid", smiles="CC1=CC2C(CC1)C(C)CCC2C(=C)C(=O)O")
L("Lovastatin", "Lovastatin", "C24H36O5", "Solid")
N("PHB", "Polyhydroxybutyrate", "(C4H6O2)n", "Solid", "A polyester bacteria store as fat (Lemoigne, 1926); ICI sold it as Biopol, a plastic that rots in soil.", "Polyhydroxybutyrate", balance="C4H6O2", props=["IsPolymer"])
N("Avermectin", "Avermectin", "C48H72O14", "Solid", "Satoshi Omura found the microbe at a Japanese golf course; William Campbell found its avermectins killed parasitic worms (Nobel, 2015).", "Avermectin")
N("Ivermectin", "Ivermectin", "C48H74O14", "Solid", "Avermectin with one double bond hydrogenated (Merck, 1981): it has nearly ended river blindness in Africa and the Americas.", "Ivermectin")
N("ZSM5", "ZSM-5", "mixture", "Solid", "Mobil's 1972 zeolite with ten-ring channels just wide enough for benzene rings; it turns methanol into gasoline and sorts xylenes by shape.", "ZSM-5", color="#f4f4f0", balance="SiO2")
N("Si3N4", "Silicon Nitride", "Si3N4", "Solid", "A hard, tough ceramic and the insulating and etch-stop layer of chips, deposited from chlorosilanes and ammonia.", "Silicon_nitride", color="#c0c0c8")
N("WF6", "Tungsten Hexafluoride", "WF6", "Gas", "One of the densest gases known, eleven times heavier than air; it deposits the tungsten plugs that wire transistors together.", "Tungsten_hexafluoride")
N("HfCl4", "Hafnium Tetrachloride", "HfCl4", "Solid", "The precursor of the hafnium oxide gate insulator.", "Hafnium(IV)_chloride")
N("HfO2", "Hafnium Dioxide", "HfO2", "Solid", "A 'high-k' insulator that replaced silica in transistor gates at Intel's 45 nm node (2007), stopping electrons tunnelling through.", "Hafnium(IV)_oxide", color="#f0f0f0")
N("OpticalFibre", "Optical Fibre", "SiO2", "Solid", "Charles Kao (1966) argued pure silica could carry light 100 km; Corning drew such a fibre in 1970. Kao shared the 2009 Nobel.", "Optical_fiber#History", color="#e8f8ff")
N("InP", "Indium Phosphide", "InP", "Solid", "The semiconductor of the lasers and detectors that send internet traffic down fibres at 1.55 micrometres.", "Indium_phosphide", color="#4a4a50")
N("TurbineBlade", "Single-Crystal Turbine Blade", "mixture", "Solid", "A nickel superalloy blade grown as one crystal so no grain boundaries can creep at 1,100 C: the hot heart of every jet engine since the 1980s.", "Superalloy#Single_crystal_superalloys", color="#a0a0a8", balance="Ni")
N("PCD", "Polycrystalline Diamond", "C", "Solid", "Diamond grit sintered with cobalt into a tough compact (GE Compax, 1973), the cutter of oil-well drill bits.", "Polycrystalline_diamond", color="#404048")
N("Fluorine18", "Fluorine-18", "F2", "Gas", "A positron emitter (half-life 110 minutes) made by bombarding oxygen-18 water with protons in a hospital cyclotron.", "Fluorine-18", props=["IsRadioactive"])
N("FDG", "Fludeoxyglucose", "C6H11FO5", "Solid", "Glucose with one OH swapped for fluorine-18 (Ido and Wolf, Brookhaven, 1976): hungry cancer cells take it up and light up a PET scan.", "Fludeoxyglucose_(18F)", smiles="OC[C@H]1OC(O)[C@H](F)[C@@H](O)[C@@H]1O")
E6.reactions += [
    R("Genentech's Insulin", "Ecoli + Glucose -> Insulin", BIOR,
      "Synthetic genes for insulin's two chains put into E. coli (Genentech, 1978); sold as Humulin from 1982, the first biotech medicine.",
      wiki="Genentech#History", exact=False, T=37),
    R("Recombinant Chymosin", "Ecoli + Lactose -> Chymosin", BIOR,
      "The calf gene for chymosin expressed in microbes: the first recombinant food enzyme (FDA, 1990).", wiki="Chymosin#Recombinant_chymosin",
      exact=False, T=37),
    R("Bio-PDO", "Ecoli + Starch -> PDO", BIOR,
      "An E. coli rebuilt with yeast and Klebsiella genes turns corn sugar into 1,3-propanediol.", wiki="1,3-Propanediol#Production", exact=False, T=35),
    R("Keasling's Artemisinic Acid", "Yeast + Sucrose -> ArtemisinicAcid", BIOR,
      "Baker's yeast given wormwood genes and a better metabolic pipeline makes the antimalarial's precursor by the tonne.",
      wiki="Artemisinin#Semi-synthesis", exact=False, T=30),
    R("Semi-Synthetic Artemisinin", "ArtemisinicAcid + O2 -> Artemisinin", LIGHT,
      "Reduced, then oxidised by singlet oxygen in light, the precursor closes into artemisinin's peroxide bridge (Sanofi, 2013).",
      wiki="Artemisinin#Semi-synthesis", exact=False),
    R("Merck's Lovastatin", "Lactose + CornSteep -> Lovastatin", BIOR,
      "The first statin, from Aspergillus terreus (Merck, 1987): it blocks the liver's cholesterol factory.", wiki="Lovastatin#History",
      cat="Aspergillus", exact=False, T=28),
    R("Biopol", "Fructose -> PHB", BIOR,
      "Cupriavidus bacteria fed sugar and starved of nitrogen stuff themselves with polyester granules, up to 90% of their weight.",
      wiki="Polyhydroxybutyrate#Production", exact=False, T=30),
    R("Cellulosic Sugar", "Cellulose + H2O -> Glucose", BIOR,
      "Cellulase enzymes from the jungle-rot fungus Trichoderma reesei unzip cellulose to glucose for fuel ethanol.",
      wiki="Cellulosic_ethanol", T=50, dh=-10),
    R("Omura's Avermectin", "Glucose + Starch -> Avermectin", BIOR,
      "Streptomyces avermitilis fermented in deep tanks; only one strain on Earth was ever found that makes it.", wiki="Avermectin",
      cat="Streptomyces", exact=False, T=28),
    R("Merck's Ivermectin", "Avermectin + H2 -> Ivermectin", HIGHP,
      "One double bond of avermectin hydrogenated selectively with Wilkinson's rhodium catalyst.", wiki="Ivermectin#History", cat="Rh", T=25, P=1, dh=-120),
    R("Mobil's ZSM-5", "Sand + NaAlOH4 -> ZSM5", PRESS,
      "Silica and aluminate crystallised around a tetrapropylammonium template in an autoclave (Argauer and Landolt, 1972).", wiki="ZSM-5",
      exact=False, T=170),
    R("Methanol to Gasoline", "8 Methanol -> Octene + 8 H2O", CRACKER,
      "Mobil's MTG process (1976; New Zealand plant 1985): ZSM-5's channels build methanol up into gasoline-sized molecules and no bigger.",
      wiki="Methanol_to_gasoline", cat="ZSM5", T=400, dh=-400),
    R("Methanol to Olefins", "2 Methanol -> Ethylene + 2 H2O", CAT,
      "Methanol dehydrated over a zeolite into ethylene and propylene: plastics from coal or biomass.", wiki="Methanol-to-olefins", cat="ZSM5", T=450, dh=-30),
    R("Three-Way Catalyst", "2 CO + 2 NO -> 2 CO2 + N2", CRACKER,
      "Platinum and rhodium on a ceramic honeycomb (1975 on): carbon monoxide strips the oxygen from nitric oxide in a car's exhaust.",
      wiki="Catalytic_converter#Three-way", cat="Rh", T=400, dh=-747),
    R("Selective Catalytic Reduction", "4 NH3 + 4 NO + O2 -> 4 N2 + 6 H2O", CRACKER,
      "Ammonia injected into power-station flue gas over vanadia turns nitrogen oxides back into nitrogen.", wiki="Selective_catalytic_reduction",
      cat="V2O5", T=350, dh=-1630),
    R("Xylene Isomerisation", "mXylene -> pXylene", CRACKER,
      "ZSM-5 lets the slim para isomer out of its channels faster than the others, so the equilibrium keeps being pulled toward it.",
      wiki="Xylene#Production", cat="ZSM5", T=400, dh=-1),
    R("Toluene Disproportionation", "2 Toluene -> Benzene + pXylene", CRACKER,
      "Methyl groups shuffled between toluene molecules over shape-selective zeolite.", wiki="Toluene#Production", cat="ZSM5", T=450, dh=1),
    R("Ruoff's Graphene", "Acetylene -> 2 Graphene + H2", CVD,
      "Hydrocarbon gas decomposed on hot copper foil, where carbon spreads into a single atomic layer and stops (Ruoff, 2009).",
      wiki="Graphene#Chemical_vapor_deposition", cat="Cu", T=1000, dh=-227),
    R("CVD Nanotubes", "Ethylene -> 2 CNT + 2 H2", CVD,
      "Iron nanoparticles dissolve carbon from ethylene and extrude it as tubes, forests of them, aligned like grass.", wiki="Synthesis_of_carbon_nanotubes#Chemical_vapor_deposition_(CVD)",
      cat="Fe", T=750, dh=-52),
    R("Silicon Nitride Film", "3 HSiCl3 + 4 NH3 -> Si3N4 + 9 HCl + 3 H2", CVD,
      "Chlorosilane and ammonia at low pressure deposit a dense, even nitride film over every wafer in the furnace.", wiki="Silicon_nitride#Production",
      T=780, dh=-400),
    R("Tungsten Hexafluoride", "W + 3 F2 -> WF6", HEAT,
      "Tungsten burns in fluorine to a colourless, heavy gas.", wiki="Tungsten_hexafluoride#Production", T=350, dh=-1722),
    R("Tungsten Plugs", "WF6 + 3 H2 -> W + 6 HF", CVD,
      "Tungsten deposited from its fluoride fills the narrow holes linking transistors to the wiring above.", wiki="Tungsten_hexafluoride#Applications", T=400, dh=-80),
    R("Suntola's Atomic Layers", "TMA + 3 H2O -> Alumina + 6 Methane", CVD,
      "Tuomo Suntola (Finland, 1974): pulse one precursor, purge, pulse the other. Each cycle lays exactly one atomic layer.",
      wiki="Atomic_layer_deposition#History", T=300, dh=-2000),
    R("Hafnium Tetrachloride", "Hf + 2 Cl2 -> HfCl4", HEAT,
      "Hafnium burns in chlorine to the tetrachloride.", wiki="Hafnium(IV)_chloride", T=400, dh=-990),
    R("High-k Gate", "HfCl4 + 2 H2O -> HfO2 + 4 HCl", CVD,
      "Hafnium oxide grown one atomic layer at a time as the gate insulator of every modern processor.", wiki="High-%CE%BA_dielectric", T=300, dh=-200),
    R("Kao's Optical Fibre", "SiCl4 + O2 -> OpticalFibre + 2 Cl2", CVD,
      "Silicon tetrachloride burnt inside a rotating silica tube (MCVD, Bell Labs, 1974) lays down glass purer than any ever melted.",
      wiki="Optical_fiber#Manufacturing", T=1600, dh=-100),
    R("Indium Phosphide", "4 In + P4 -> 4 InP", PULLER,
      "Indium and phosphorus reacted under high pressure and pulled under a boron oxide cap.", wiki="Indium_phosphide", T=1062, dh=-350),
    R("Single-Crystal Blade", "Ni + Cr + Co + Al -> TurbineBlade", PULLER,
      "The superalloy cast into a mould with a pigtail 'grain selector' that only one crystal can grow through (Pratt and Whitney).",
      wiki="Superalloy#Single_crystal_superalloys", exact=False, T=1450),
    R("GE Compax", "Diamond + Co -> PCD", DPRESS,
      "Diamond grit sintered together under high pressure with cobalt flowing between the grains.", wiki="Polycrystalline_diamond", T=1500, P=55000,
      exact=False),
    R("Fluorine-18", "H2O -> Fluorine18", CYCLO,
      "Protons fired into water enriched in oxygen-18 knock out a neutron: oxygen-18 becomes fluorine-18.", wiki="Fluorine-18#Production", exact=False),
    R("Ido's FDG", "Fluorine18 + Glucose -> FDG", FLASK,
      "Fluoride-18 swapped onto a protected sugar in minutes, against the clock of its two-hour half-life.", wiki="Fludeoxyglucose_(18F)#Synthesis",
      exact=False),
    R("FFC Cambridge Titanium", "TiO2 -> Ti + O2", ECELL,
      "Fray, Farthing and Chen (2000): titanium dioxide as the cathode in molten calcium chloride gives up its oxygen as ions.",
      wiki="FFC_Cambridge_process", dh=944),
    R("Solid Rocket Booster", "6 NH4ClO4 + 10 Al -> 5 Alumina + 6 HCl + 9 H2O + 3 N2", HEAT,
      "Ammonium perchlorate and aluminium powder in a rubber binder: the Space Shuttle's boosters (1981) burned 500 tonnes of it in two minutes.",
      wiki="Ammonium_perchlorate_composite_propellant", dh=-9000),
    R("Fossil-Free Steel", "Hematite + 3 H2 -> 2 Fe + 3 H2O", BLAST,
      "HYBRIT's pilot plant in Lulea (2021) reduced iron ore with hydrogen from wind-powered electrolysis: steel whose exhaust is water.",
      wiki="Hydrogen_steelmaking", T=800, dh=96),
]
N("NH4ClO4", "Ammonium Perchlorate", "NH4ClO4", "Solid", "The oxidiser of solid rocket fuel, made by metathesis from sodium perchlorate; the 1988 PEPCON plant explosion in Nevada was felt 16 km away.", "Ammonium_perchlorate")
E5.reactions += [
    R("Ammonium Perchlorate", "NaClO4 + NH4Cl -> NH4ClO4 + NaCl", COOL,
      "Sodium perchlorate and ammonium chloride swap ions; the less soluble ammonium perchlorate crystallises out on cooling.",
      wiki="Ammonium_perchlorate#Production", T=10, dh=10),
]


# ======================================================================================
# 4. THE LABORATORY: the systematic families every chemistry set teaches
# ======================================================================================
# (key, name, formula, colour, what it is, article)
for _k, _n, _f, _c, _d, _w in [
    ("ZnCl2", "Zinc Chloride", "ZnCl2", "#f4f4f0", "So hungry for water it dissolves in what it pulls from the air; tinsmiths' 'killed spirits' soldering flux.", "Zinc_chloride"),
    ("NiCl2", "Nickel(II) Chloride", "NiCl2", "#7ab060", "Yellow when dry and green as the hexahydrate; a nickel source for electroplating.", "Nickel(II)_chloride"),
    ("CoCl2", "Cobalt(II) Chloride", "CoCl2", "#3050c0", "Blue when dry and pink when damp: the indicator in humidity cards and the 'sympathetic ink' that appears on warming.", "Cobalt(II)_chloride"),
    ("CuCl2", "Copper(II) Chloride", "CuCl2", "#30a0b0", "Brown when dry, blue-green in water; it gives fireworks their blue.", "Copper(II)_chloride"),
    ("CdCl2", "Cadmium Chloride", "CdCl2", "#f4f4f4", "A white salt whose layered crystal is the textbook prototype for dozens of others.", "Cadmium_chloride"),
    ("PbCl2", "Lead(II) Chloride", "PbCl2", "#f8f8f8", "Barely soluble cold, soluble hot: the first precipitate of the classic qualitative analysis scheme.", "Lead(II)_chloride"),
    ("BiCl3", "Bismuth Trichloride", "BiCl3", "#f4f4f4", "Water turns it into milky bismuth oxychloride, the pearly shimmer of nail varnish.", "Bismuth_chloride"),
    ("CrCl3", "Chromium(III) Chloride", "CrCl3", "#6a2a8a", "Violet flakes that dissolve to green solutions; a catalyst for making polyethylene.", "Chromium(III)_chloride"),
    ("CuCl", "Copper(I) Chloride", "CuCl", "#f0f0e8", "White when pure; it catalyses Sandmeyer reactions and absorbs carbon monoxide from gas mixtures.", "Copper(I)_chloride"),
    ("NiSO4", "Nickel(II) Sulfate", "NiSO4", "#4aa060", "Emerald crystals as the hydrate; the main salt of nickel-plating baths.", "Nickel(II)_sulfate"),
    ("MnSO4", "Manganese(II) Sulfate", "MnSO4", "#f0d0d8", "Pale pink; the manganese of fertilisers, animal feed and electrolytic manganese.", "Manganese(II)_sulfate"),
    ("MgSO4", "Magnesium Sulfate", "MgSO4", "#f8f8f8", "Anhydrous Epsom salt, the organic chemist's drying powder.", "Magnesium_sulfate"),
    ("CdSO4", "Cadmium Sulfate", "CdSO4", "#f8f8f8", "The electrolyte of the Weston standard cell, the world's voltage reference from 1911 to 1990.", "Cadmium_sulfate"),
    ("Cr2SO43", "Chromium(III) Sulfate", "Cr2(SO4)3", "#4a6a8a", "The basic chromium sulfate that tans most of the world's leather.", "Chromium(III)_sulfate"),
    ("CoNO32", "Cobalt(II) Nitrate", "Co(NO3)2", "#c03050", "Red crystals; the cobalt of many Fischer-Tropsch catalysts.", "Cobalt(II)_nitrate"),
    ("MnNO32", "Manganese(II) Nitrate", "Mn(NO3)2", "#f0d0d8", "A pink salt that decomposes cleanly to manganese dioxide for batteries.", "Manganese(II)_nitrate"),
    ("BiNO33", "Bismuth(III) Nitrate", "Bi(NO3)3", "#f8f8f8", "The starting salt of most bismuth compounds, from stomach remedies to the 'subnitrate' of old cosmetics.", "Bismuth(III)_nitrate"),
    ("HgNO32", "Mercury(II) Nitrate", "Hg(NO3)2", "#f8f8f8", "Felters brushed it onto rabbit fur for hats; the mercury poisoning that followed is the likely origin of 'mad as a hatter'.", "Mercury(II)_nitrate"),
    ("CuOH2", "Copper(II) Hydroxide", "Cu(OH)2", "#40a0d0", "A pale blue jelly that falls out when alkali meets a copper salt.", "Copper(II)_hydroxide"),
    ("NiOH2", "Nickel(II) Hydroxide", "Ni(OH)2", "#60b070", "Apple-green; the positive plate of nickel-cadmium and nickel-metal hydride cells.", "Nickel(II)_hydroxide"),
    ("CoOH2", "Cobalt(II) Hydroxide", "Co(OH)2", "#e07090", "Blue at first, turning rose-red as it ages; a drying agent in paints.", "Cobalt(II)_hydroxide"),
    ("ZnOH2", "Zinc Hydroxide", "Zn(OH)2", "#f8f8f8", "White and amphoteric: it dissolves in acid and in excess alkali alike.", "Zinc_hydroxide"),
    ("CdOH2", "Cadmium Hydroxide", "Cd(OH)2", "#f8f8f8", "The negative plate of nickel-cadmium cells.", "Cadmium_hydroxide"),
    ("FeOH3", "Iron(III) Hydroxide", "Fe(OH)3", "#a0501a", "Rust-brown and gelatinous: the ochre of mine drainage and the stain of iron-rich springs.", "Iron(III)_oxide-hydroxide"),
    ("CrOH3", "Chromium(III) Hydroxide", "Cr(OH)3", "#4a7a5a", "A grey-green, amphoteric precipitate; heated, it gives chrome green.", "Chromium(III)_hydroxide"),
    ("NiCO3", "Nickel(II) Carbonate", "NiCO3", "#7ac080", "A light green powder used to make nickel catalysts and ceramic glazes.", "Nickel(II)_carbonate"),
    ("CoCO3", "Cobalt(II) Carbonate", "CoCO3", "#e080a0", "Pink, and the potter's way of adding cobalt blue to a glaze.", "Cobalt(II)_carbonate"),
    ("MnCO3", "Manganese(II) Carbonate", "MnCO3", "#f0b0c0", "The rose-pink mineral rhodochrosite, Argentina's national gemstone.", "Manganese(II)_carbonate"),
    ("CdCO3", "Cadmium Carbonate", "CdCO3", "#f8f8f8", "The rare mineral otavite, named for Otavi in Namibia.", "Cadmium_carbonate"),
    ("FeCO3", "Iron(II) Carbonate", "FeCO3", "#b0a080", "Siderite, the 'spathic iron ore' of the Styrian Erzberg, mined since Roman times.", "Siderite"),
    ("CuS", "Copper(II) Sulfide", "CuS", "#1a2050", "Black precipitate, and as a mineral the indigo-blue covellite, named for Niccolo Covelli who found it on Vesuvius.", "Copper_monosulfide"),
    ("CdS", "Cadmium Sulfide", "CdS", "#f8c000", "Cadmium yellow, the brilliant pigment Monet and Van Gogh adopted; also the light-sensitive cell of old camera meters.", "Cadmium_sulfide"),
    ("CoS", "Cobalt(II) Sulfide", "CoS", "#1a1a1a", "A black precipitate, part of the fourth group of classical analysis.", "Cobalt_sulfide"),
    ("MnS", "Manganese(II) Sulfide", "MnS", "#e8a8a0", "The salmon-pink precipitate that tells an analyst manganese is present.", "Manganese(II)_sulfide"),
    ("K2CrO4", "Potassium Chromate", "K2CrO4", "#f0e020", "Lemon-yellow; the indicator of Mohr's chloride titration.", "Potassium_chromate"),
    ("K2Cr2O7", "Potassium Dichromate", "K2Cr2O7", "#f07010", "Orange crystals, a classic oxidant: the breathalyser turned green when it met ethanol.", "Potassium_dichromate"),
    ("Ag2CrO4", "Silver Chromate", "Ag2CrO4", "#a03020", "Brick red; its appearance marks the end point in Mohr's titration (1856).", "Silver_chromate"),
    ("BaCrO4", "Barium Chromate", "BaCrO4", "#f0e040", "Lemon chrome, a yellow pigment and corrosion inhibitor.", "Barium_chromate"),
    ("NH4Cr2O7", "Ammonium Dichromate", "(NH4)2Cr2O7", "#f06010", "Orange crystals that, lit, burn into a 'volcano' of green chromium oxide.", "Ammonium_dichromate"),
    ("MnO", "Manganese(II) Oxide", "MnO", "#3a5a3a", "Green-grey manganosite, a fertiliser and feed additive.", "Manganese(II)_oxide"),
    ("Mn2O3", "Manganese(III) Oxide", "Mn2O3", "#3a2a20", "Black; forms when manganese dioxide is heated above 500 C.", "Manganese(III)_oxide"),
    ("SrO", "Strontium Oxide", "SrO", "#f8f8f8", "Strontia, which Thomas Hope recognised in 1791 by the crimson flame of its salts.", "Strontium_oxide"),
    ("KO2", "Potassium Superoxide", "KO2", "#f0d040", "Potassium burned in air: yellow crystals that absorb exhaled CO2 and release oxygen, in mine rescue sets and Soyuz capsules.", "Potassium_superoxide"),
    ("Na2O2", "Sodium Peroxide", "Na2O2", "#f8f0c0", "A pale yellow oxidiser that turns CO2 back into oxygen; it purified the air of early submarines.", "Sodium_peroxide"),
    ("Mg3N2", "Magnesium Nitride", "Mg3N2", "#e0e080", "The greenish-yellow powder that forms when magnesium burns in air; Rayleigh and Ramsay used it to strip nitrogen and find argon (1894).", "Magnesium_nitride"),
    ("ZnBr2", "Zinc Bromide", "ZnBr2", "#f8f8f8", "Its dense solutions shield the windows of nuclear 'hot cells' and weigh down oil wells.", "Zinc_bromide"),
    ("AlBr3", "Aluminium Bromide", "AlBr3", "#f8f8f8", "Like aluminium chloride, a Lewis acid that catalyses Friedel-Crafts reactions.", "Aluminium_bromide"),
    ("FeBr3", "Iron(III) Bromide", "FeBr3", "#6a2a10", "Red-brown; the catalyst that lets bromine attack a benzene ring.", "Iron(III)_bromide"),
    ("MgBr2", "Magnesium Bromide", "MgBr2", "#f8f8f8", "A sedative in the 19th century and a mild Lewis acid in the lab.", "Magnesium_bromide"),
    ("SnI4", "Tin(IV) Iodide", "SnI4", "#f07010", "Bright orange crystals that sublime easily.", "Tin(IV)_iodide"),
    ("HgI2", "Mercury(II) Iodide", "HgI2", "#f02010", "Scarlet, turning yellow above 126 C and red again on cooling: a thermochromic textbook example.", "Mercury(II)_iodide"),
    ("CuI", "Copper(I) Iodide", "CuI", "#f0f0e0", "Released with iodine when iodide meets a copper(II) salt; the basis of an old copper assay.", "Copper(I)_iodide"),
    ("GeCl4", "Germanium Tetrachloride", "GeCl4", "#f0f8ff", "A colourless fuming liquid; burnt with silicon tetrachloride, it raises the refractive index of an optical fibre's core.", "Germanium_tetrachloride"),
    ("FumedSilica", "Fumed Silica", "SiO2", "#f8f8ff", "Degussa's Aerosil (1942): silica smoke so fine that a gram has the surface of a tennis court; it thickens toothpaste and paint.", "Fumed_silica"),
    ("Hydroxyapatite", "Hydroxyapatite", "Ca10(PO4)6(OH)2", "#f4f0e8", "The mineral of bone and tooth enamel; fluoride hardens teeth by swapping in for its OH.", "Hydroxyapatite"),
    ("Struvite", "Struvite", "MgNH4PO4·6H2O", "#f0f0e0", "Magnesium ammonium phosphate: kidney stones, a crust in sewage pipes, and slow-release fertiliser recovered from wastewater.", "Struvite"),
    ("EpsomSalt", "Epsom Salt", "MgSO4·7H2O", "#f8f8f8", "Found in a bitter spring on Epsom common in 1618; Nehemiah Grew sold it as a purge from 1695.", "Magnesium_sulfate#Epsom_salt"),
    ("WhiteVitriol", "White Vitriol", "ZnSO4·7H2O", "#f8f8f8", "Zinc sulfate heptahydrate, goslarite; an old eye-wash and a source of zinc in feed.", "Zinc_sulfate"),
    ("CoCl2Hex", "Cobalt Chloride Hexahydrate", "CoCl2·6H2O", "#e04070", "Deep pink crystals that turn blue as they lose their water.", "Cobalt(II)_chloride#Properties"),
    ("ChromeAlum", "Chrome Alum", "KCr(SO4)2·12H2O", "#4a2060", "Deep purple octahedra, the most beautiful crystals a school lab can grow.", "Chrome_alum"),
    ("FeSCN3", "Iron(III) Thiocyanate", "Fe(SCN)3", "#900010", "The blood-red colour that reveals even traces of ferric iron.", "Iron(III)_thiocyanate"),
    ("EthylLactate", "Ethyl Lactate", "C5H10O3", "#f8f8f8", "A biodegradable solvent made from corn sugar and ethanol, replacing chlorinated solvents.", "Ethyl_lactate"),
    ("EthylSalicylate", "Ethyl Salicylate", "C9H10O3", "#f8f8f8", "The wintergreen-scented ester of salicylic acid and ethanol, in perfumes and flavours.", "Ethyl_salicylate"),
    ("MethylPropionate", "Methyl Propionate", "C4H8O2", "#f8f8f8", "A rum-like ester and a step toward methyl methacrylate in the Alpha process.", "Methyl_propionate"),
    ("IsoamylButyrate", "Isoamyl Butyrate", "C9H18O2", "#f8f8f8", "Smells of apricot and pear drops.", "Isoamyl_butyrate"),
    ("BenzylFormate", "Benzyl Formate", "C8H8O2", "#f8f8f8", "A fruity, jasmine-like ester.", "Benzyl_formate"),
    ("EthylAnthranilate", "Ethyl Anthranilate", "C9H11NO2", "#f8f8f8", "The grape-and-orange-blossom ester, also used to scare birds off crops.", "Ethyl_anthranilate"),
]:
    N(_k, _n, _f, "Solid", _d, _w, color=_c)
for _k in ("EthylLactate", "EthylSalicylate", "MethylPropionate", "IsoamylButyrate", "BenzylFormate", "EthylAnthranilate", "GeCl4"):
    SUBSTANCES[_k].state = "Liquid"
SUBSTANCES["Struvite"].balance = "MgNH4PO4H12O6"
L("ZnOAc2", "Zinc acetate", "Zn(C2H3O2)2", "Solid", name="Zinc Acetate")
L("CaOAc2", "Calcium acetate", "Ca(C2H3O2)2", "Solid", name="Calcium Acetate")
L("CoSO4", "Cobalt sulfate", "CoSO4", "Solid", name="Cobalt(II) Sulfate")
L("HClO4", "Perchloric acid", "HClO4", "Liquid", name="Perchloric Acid")
L("AlN", "Aluminum nitride", "AlN", "Solid", name="Aluminium Nitride")
L("ButylButyrate", "Butyl butyrate", "C8H16O2", "Liquid", name="Butyl Butyrate", smiles="CCCCOC(=O)CCC")
L("PropylPropionate", "Propyl propionate", "C6H12O2", "Liquid", name="Propyl Propionate", smiles="CCCOC(=O)CC")


def LAB(name, eq, proc, desc, wiki, **kw):
    E7.reactions.append(R(name, eq, proc, desc, wiki=wiki, **kw))


def _nm(k):
    return SUBSTANCES[k].name


# metal oxide or carbonate + acid -> salt  (oxide, acid, salt, equation)
for ox, acid, salt, eq in [
    ("ZnO", "HCl", "ZnCl2", "ZnO + 2 HCl -> ZnCl2 + H2O"),
    ("NiO", "HCl", "NiCl2", "NiO + 2 HCl -> NiCl2 + H2O"),
    ("CoO", "HCl", "CoCl2", "CoO + 2 HCl -> CoCl2 + H2O"),
    ("CuO", "HCl", "CuCl2", "CuO + 2 HCl -> CuCl2 + H2O"),
    ("CdO", "HCl", "CdCl2", "CdO + 2 HCl -> CdCl2 + H2O"),
    ("PbO", "HCl", "PbCl2", "PbO + 2 HCl -> PbCl2 + H2O"),
    ("Bi2O3", "HCl", "BiCl3", "Bi2O3 + 6 HCl -> 2 BiCl3 + 3 H2O"),
    ("Cr2O3", "HCl", "CrCl3", "Cr2O3 + 6 HCl -> 2 CrCl3 + 3 H2O"),
    ("NiO", "H2SO4", "NiSO4", "NiO + H2SO4 -> NiSO4 + H2O"),
    ("CoO", "H2SO4", "CoSO4", "CoO + H2SO4 -> CoSO4 + H2O"),
    ("MgCO3", "H2SO4", "MgSO4", "MgCO3 + H2SO4 -> MgSO4 + CO2 + H2O"),
    ("CdO", "H2SO4", "CdSO4", "CdO + H2SO4 -> CdSO4 + H2O"),
    ("ZnO", "H2SO4", "ZnSO4", "ZnO + H2SO4 -> ZnSO4 + H2O"),
    ("CoO", "HNO3", "CoNO32", "CoO + 2 HNO3 -> CoNO32 + H2O"),
    ("MnCO3", "HNO3", "MnNO32", "MnCO3 + 2 HNO3 -> MnNO32 + CO2 + H2O"),
    ("ZnO", "HNO3", "ZnNO32", "ZnO + 2 HNO3 -> ZnNO32 + H2O"),
    ("ZnO", "AcOH", "ZnOAc2", "ZnO + 2 AcOH -> ZnOAc2 + H2O"),
    ("Limestone", "AcOH", "CaOAc2", "Limestone + 2 AcOH -> CaOAc2 + CO2 + H2O"),
]:
    LAB(f"{_nm(salt)} from {_nm(ox)}", eq, MIX,
        f"{_nm(ox)} dissolves in {_nm(acid).lower()}; evaporated, the solution leaves {_nm(salt).lower()}.",
        SUBSTANCES[salt].wiki or SUBSTANCES[salt].name.replace(" ", "_"), dh=-80)
LAB("Hot Chrome Sulfate", "Cr2O3 + 3 H2SO4 -> Cr2SO43 + 3 H2O", HEAT,
    "Chromium oxide only yields to hot concentrated sulfuric acid.", "Chromium(III)_sulfate", T=200, dh=-150)
LAB("Pyrolusite and Sulfur Dioxide", "MnO2 + SO2 -> MnSO4", MIX,
    "Sulfur dioxide bubbled through a slurry of manganese dioxide reduces and dissolves it.", "Manganese(II)_sulfate#Production", dh=-200)

# metals in acid -> salt + hydrogen
for m, acid, eq, salt in [
    ("Zn", "HCl", "Zn + 2 HCl -> ZnCl2 + H2", "ZnCl2"), ("Mg", "HCl", "Mg + 2 HCl -> MgCl2 + H2", "MgCl2"),
    ("Fe", "HCl", "Fe + 2 HCl -> FeCl2 + H2", "FeCl2"), ("Al", "HCl", "2 Al + 6 HCl -> 2 AlCl3 + 3 H2", "AlCl3"),
    ("Mg", "H2SO4", "Mg + H2SO4 -> MgSO4 + H2", "MgSO4"),
]:
    LAB(f"{_nm(m)} in {_nm(acid)}", eq, MIX,
        f"{_nm(m)} fizzes in {_nm(acid).lower()}, giving off hydrogen and leaving {_nm(salt).lower()} in solution.",
        "Reactivity_series", dh=-150)
LAB("Copper in Nitric Acid", "Cu + 4 HNO3 -> Cu(NO3)2 + 2 NO2 + 2 H2O", MIX,
    "Copper dissolves in strong nitric acid with clouds of brown nitrogen dioxide: the reaction that converted Ira Remsen to chemistry.",
    "Copper(II)_nitrate#Preparation", dh=-200)
LAB("Bismuth in Nitric Acid", "Bi + 4 HNO3 -> BiNO33 + NO + 2 H2O", MIX,
    "Bismuth dissolves in nitric acid as the nitrate.", "Bismuth(III)_nitrate", dh=-200)
LAB("Mercury in Nitric Acid", "Hg + 4 HNO3 -> HgNO32 + 2 NO2 + 2 H2O", MIX,
    "Mercury dissolves in hot nitric acid: the 'carrotting' liquor of the hatters.", "Mercury(II)_nitrate", dh=-150)
LAB("Copper(I) Chloride", "CuCl2 + Cu + HCl -> 2 CuCl + HCl", MIX,
    "Copper metal reduces copper(II) chloride in hot hydrochloric acid to the white copper(I) salt.", "Copper(I)_chloride#Preparation", dh=-30)

# precipitating hydroxides, and baking them to oxides
for salt, base, prod, eq, back in [
    ("CuSO4", "NaOH", "CuOH2", "CuSO4 + 2 NaOH -> CuOH2 + Na2SO4", ("CuOH2 -> CuO + H2O", "CuO")),
    ("ZnSO4", "NaOH", "ZnOH2", "ZnSO4 + 2 NaOH -> ZnOH2 + Na2SO4", ("ZnOH2 -> ZnO + H2O", "ZnO")),
    ("NiSO4", "NaOH", "NiOH2", "NiSO4 + 2 NaOH -> NiOH2 + Na2SO4", ("NiOH2 -> NiO + H2O", "NiO")),
    ("CoCl2", "NaOH", "CoOH2", "CoCl2 + 2 NaOH -> CoOH2 + 2 NaCl", ("CoOH2 -> CoO + H2O", "CoO")),
    ("CdSO4", "NaOH", "CdOH2", "CdSO4 + 2 NaOH -> CdOH2 + Na2SO4", ("CdOH2 -> CdO + H2O", "CdO")),
    ("FeCl3", "NaOH", "FeOH3", "FeCl3 + 3 NaOH -> FeOH3 + 3 NaCl", ("2 FeOH3 -> Hematite + 3 H2O", "Hematite")),
    ("CrCl3", "NaOH", "CrOH3", "CrCl3 + 3 NaOH -> CrOH3 + 3 NaCl", ("2 CrOH3 -> Cr2O3 + 3 H2O", "Cr2O3")),
    ("Al2(SO4)3", "NaOH", "AlOH3", "Al2(SO4)3 + 6 NaOH -> 2 AlOH3 + 3 Na2SO4", None),
    ("MgCl2", "NaOH", "MgOH2", "MgCl2 + 2 NaOH -> MgOH2 + 2 NaCl", None),
]:
    LAB(f"Precipitating {_nm(prod)}", eq, MIX,
        f"Caustic soda added to {_nm(salt).lower()} solution throws down {_nm(prod).lower()}.",
        SUBSTANCES[prod].wiki or "Precipitation_(chemistry)", dh=-50)
    if back:
        LAB(f"Baking {_nm(prod)}", back[0], HEAT,
            f"{_nm(prod)} heated gently loses water and leaves {_nm(back[1]).lower()}.",
            SUBSTANCES[prod].wiki or "Calcination", T=300, dh=40)

# precipitating carbonates with soda, and calcining them
for salt, prod, eq, back in [
    ("NiSO4", "NiCO3", "NiSO4 + SodaAsh -> NiCO3 + Na2SO4", "NiCO3 -> NiO + CO2"),
    ("CoCl2", "CoCO3", "CoCl2 + SodaAsh -> CoCO3 + 2 NaCl", "CoCO3 -> CoO + CO2"),
    ("MnSO4", "MnCO3", "MnSO4 + SodaAsh -> MnCO3 + Na2SO4", "MnCO3 -> MnO + CO2"),
    ("CdSO4", "CdCO3", "CdSO4 + SodaAsh -> CdCO3 + Na2SO4", "CdCO3 -> CdO + CO2"),
    ("FeSO4", "FeCO3", "FeSO4 + SodaAsh -> FeCO3 + Na2SO4", "FeCO3 -> FeO + CO2"),
    ("ZnSO4", "Calamine", "ZnSO4 + SodaAsh -> Calamine + Na2SO4", None),
    ("BaCl2", "BaCO3", "BaCl2 + SodaAsh -> BaCO3 + 2 NaCl", None),
    ("SrCl2", "SrCO3", "SrCl2 + SodaAsh -> SrCO3 + 2 NaCl", "SrCO3 -> SrO + CO2"),
    ("MgCl2", "MgCO3", "MgCl2 + SodaAsh -> MgCO3 + 2 NaCl", None),
]:
    LAB(f"Precipitating {_nm(prod)}", eq, MIX,
        f"Washing soda poured into {_nm(salt).lower()} solution precipitates {_nm(prod).lower()}.",
        SUBSTANCES[prod].wiki or "Precipitation_(chemistry)", dh=-20)
    if back:
        LAB(f"Calcining {_nm(prod)}", back, BLAST if prod == "SrCO3" else HEAT,
            f"{_nm(prod)} heated drives off carbon dioxide.", SUBSTANCES[prod].wiki or "Calcination",
            T=1200 if prod == "SrCO3" else 400, dh=100)
LAB("Verditer", "2 CuSO4 + 2 SodaAsh + H2O -> Malachite + 2 Na2SO4 + CO2", MIX,
    "Blue vitriol and soda make an artificial malachite, the green and blue 'verditer' pigments of 17th-century painters.",
    "Verditer", dh=-30)

# nitrates break down on heating: oxide, brown fumes and oxygen
for nit, ox, eq in [
    ("ZnNO32", "ZnO", "2 ZnNO32 -> 2 ZnO + 4 NO2 + O2"), ("Ni(NO3)2", "NiO", "2 Ni(NO3)2 -> 2 NiO + 4 NO2 + O2"),
    ("Mg(NO3)2", "MgO", "2 Mg(NO3)2 -> 2 MgO + 4 NO2 + O2"), ("Ca(NO3)2", "CaO", "2 Ca(NO3)2 -> 2 CaO + 4 NO2 + O2"),
    ("Sr(NO3)2", "SrO", "2 Sr(NO3)2 -> 2 SrO + 4 NO2 + O2"), ("Al(NO3)3", "Alumina", "4 Al(NO3)3 -> 2 Alumina + 12 NO2 + 3 O2"),
    ("Fe(NO3)3", "Hematite", "4 Fe(NO3)3 -> 2 Hematite + 12 NO2 + 3 O2"), ("Cd(NO3)2", "CdO", "2 Cd(NO3)2 -> 2 CdO + 4 NO2 + O2"),
    ("LiNO3", "Li2O", "4 LiNO3 -> 2 Li2O + 4 NO2 + O2"), ("CoNO32", "CoO", "2 CoNO32 -> 2 CoO + 4 NO2 + O2"),
    ("MnNO32", "MnO2", "MnNO32 -> MnO2 + 2 NO2"),
]:
    LAB(f"Heating {_nm(nit)}", eq, HEAT,
        f"{_nm(nit)} melts, then decomposes into {_nm(ox).lower()} with brown nitrogen dioxide and oxygen.",
        "Nitrate#Thermal_decomposition" if nit != "MnNO32" else "Manganese(II)_nitrate", T=500, dh=300)

# sulfides out of solution: the classic qualitative analysis groups
for salt, prod, eq in [
    ("CuSO4", "CuS", "CuSO4 + H2S -> CuS + H2SO4"), ("ZnSO4", "Sphalerite", "ZnSO4 + H2S -> Sphalerite + H2SO4"),
    ("CdSO4", "CdS", "CdSO4 + H2S -> CdS + H2SO4"), ("PbNO32", "Galena", "PbNO32 + H2S -> Galena + 2 HNO3"),
    ("AgNO3", "Acanthite", "2 AgNO3 + H2S -> Acanthite + 2 HNO3"), ("HgCl2", "Cinnabar", "HgCl2 + H2S -> Cinnabar + 2 HCl"),
    ("As2O3", "Orpiment", "As2O3 + 3 H2S -> Orpiment + 3 H2O"), ("BiCl3", "Bismuthinite", "2 BiCl3 + 3 H2S -> Bismuthinite + 6 HCl"),
    ("SbCl3", "Stibnite", "2 SbCl3 + 3 H2S -> Stibnite + 6 HCl"), ("CoCl2", "CoS", "CoCl2 + H2S -> CoS + 2 HCl"),
    ("MnSO4", "MnS", "MnSO4 + Na2S -> MnS + Na2SO4"),
]:
    LAB(f"{_nm(prod)} from {_nm(salt)}", eq, MIX,
        f"{'Hydrogen sulfide' if 'H2S' in eq else 'Sodium sulfide'} precipitates {_nm(prod).lower()} from {_nm(salt).lower()}: "
        "colours and solubilities like these sorted the metals in Fresenius's analysis scheme (1841).",
        "Qualitative_inorganic_analysis", dh=-60)
LAB("Hydrogen Sulfide Reduces Iron", "2 FeCl3 + H2S -> 2 FeCl2 + S + 2 HCl", MIX,
    "Hydrogen sulfide reduces ferric iron and is itself oxidised to a milky haze of sulfur.", "Hydrogen_sulfide#Reactions", dh=-80)

# halides straight from the elements
for eq, prod, d in [
    ("Zn + Cl2 -> ZnCl2", "ZnCl2", -415), ("Cu + Cl2 -> CuCl2", "CuCl2", -220), ("Ni + Cl2 -> NiCl2", "NiCl2", -305),
    ("Co + Cl2 -> CoCl2", "CoCl2", -312), ("2 Cr + 3 Cl2 -> 2 CrCl3", "CrCl3", -1112), ("2 Bi + 3 Cl2 -> 2 BiCl3", "BiCl3", -758),
    ("Ge + 2 Cl2 -> GeCl4", "GeCl4", -532), ("Mg + Cl2 -> MgCl2", "MgCl2", -641), ("2 Al + 3 Cl2 -> 2 AlCl3", "AlCl3", -1408),
    ("Si + 2 Cl2 -> SiCl4", "SiCl4", -687), ("Zn + Br2 -> ZnBr2", "ZnBr2", -328), ("2 Al + 3 Br2 -> 2 AlBr3", "AlBr3", -1054),
    ("2 Fe + 3 Br2 -> 2 FeBr3", "FeBr3", -536), ("Mg + Br2 -> MgBr2", "MgBr2", -524), ("Sn + 2 I2 -> SnI4", "SnI4", -150),
]:
    el = eq.split(" + ")[0].split()[-1]
    hal = "chlorine" if "Cl2" in eq else ("bromine" if "Br2" in eq else "iodine")
    LAB(f"{_nm(el)} in {hal.title()}", eq, HEAT,
        f"{_nm(el)} heated in {hal} combines directly to {_nm(prod).lower()}.",
        SUBSTANCES[prod].wiki or "Halide", T=300, dh=d)
LAB("Scarlet Mercury Iodide", "HgCl2 + 2 KI -> HgI2 + 2 KCl", MIX,
    "Potassium iodide drops into corrosive sublimate a scarlet precipitate, which redissolves in excess iodide.", "Mercury(II)_iodide", dh=-80)
LAB("Copper(I) Iodide", "2 CuSO4 + 4 KI -> 2 CuI + I2 + 2 K2SO4", MIX,
    "Iodide reduces copper(II): the white copper(I) iodide is hidden by the brown iodine freed alongside it.", "Copper(I)_iodide", dh=-60)

# the chromium colours
LAB("Potassium Dichromate", "Na2Cr2O7 + 2 KCl -> K2Cr2O7 + 2 NaCl", COOL,
    "Sodium dichromate and potash salt swap ions; the far less soluble potassium dichromate crystallises out.", "Potassium_dichromate#Production", T=5, dh=10)
LAB("Dichromate to Chromate", "K2Cr2O7 + 2 KOH -> 2 K2CrO4 + H2O", MIX,
    "Add alkali and orange dichromate turns yellow chromate; add acid and it turns back: an equilibrium you can see.", "Potassium_chromate", dh=-30)
LAB("Mohr's Silver Chromate", "2 AgNO3 + K2CrO4 -> Ag2CrO4 + 2 KNO3", MIX,
    "Brick-red silver chromate only appears once every chloride has been precipitated: Karl Mohr's end point (1856).", "Argentometry#Mohr_method", dh=-60)
LAB("Lemon Chrome", "BaCl2 + K2CrO4 -> BaCrO4 + 2 KCl", MIX,
    "Barium and chromate ions precipitate a pale yellow pigment.", "Barium_chromate", dh=-40)
LAB("Ammonium Dichromate", "Na2Cr2O7 + 2 NH4Cl -> NH4Cr2O7 + 2 NaCl", COOL,
    "Sodium dichromate and sal ammoniac crystallise out the orange ammonium salt.", "Ammonium_dichromate", T=5, dh=10)
LAB("Dichromate Volcano", "NH4Cr2O7 -> Cr2O3 + N2 + 4 H2O", HEAT,
    "Lit at one point, ammonium dichromate smoulders into a growing cone of fluffy green chromium oxide.", "Ammonium_dichromate#Reactions", dh=-315)

# permanganate
LAB("Chlorine from Permanganate", "2 KMnO4 + 16 HCl -> 2 KCl + 2 MnCl2 + 5 Cl2 + 8 H2O", MIX,
    "Hydrochloric acid dripped onto permanganate crystals: the quick laboratory chlorine.", "Potassium_permanganate#Reactions", dh=-300)
LAB("Heating Permanganate", "2 KMnO4 -> K2MnO4 + MnO2 + O2", HEAT,
    "Permanganate crystals crackle when heated and give off oxygen.", "Potassium_permanganate#Reactions", T=250, dh=100)
LAB("Permanganate and Glycerol", "14 KMnO4 + 4 Glycerol -> 7 Potash + 7 Mn2O3 + 5 CO2 + 16 H2O", MIX,
    "A few drops of glycerol on powdered permanganate start to smoke, then burst into purple-white flame on their own.",
    "Potassium_permanganate#Reactions", dh=-12000)

# nitrides and hydrides meet water
LAB("Burning Magnesium in Nitrogen", "3 Mg + N2 -> Mg3N2", HEAT,
    "Magnesium burns even in nitrogen; Ramsay used hot magnesium to soak up nitrogen and found argon left over.", "Magnesium_nitride", T=700, dh=-461)
LAB("Magnesium Nitride in Water", "Mg3N2 + 6 H2O -> 3 MgOH2 + 2 NH3", MIX,
    "The nitride smells of ammonia as soon as it is damp.", "Magnesium_nitride#Reactions", dh=-700)
LAB("Lithium Nitride in Water", "Li3N + 3 H2O -> 3 LiOH + NH3", MIX,
    "Lithium nitride hydrolyses violently to lithium hydroxide and ammonia.", "Lithium_nitride", dh=-580)
LAB("Aluminium Nitride", "2 Al + N2 -> 2 AlN", ARC,
    "Aluminium heated in nitrogen above 1,000 C: a ceramic that conducts heat almost as well as copper but not electricity, for LED and chip packages.",
    "Aluminium_nitride", T=1400, dh=-636)
LAB("Aluminium Nitride in Water", "AlN + 3 H2O -> AlOH3 + NH3", MIX,
    "Damp air slowly turns aluminium nitride powder back to hydroxide and ammonia.", "Aluminium_nitride", dh=-80)
for eq, h in [("CaH2 + 2 H2O -> Ca(OH)2 + 2 H2", "CaH2"), ("LiH + H2O -> LiOH + H2", "LiH"), ("NaH + H2O -> NaOH + H2", "NaH")]:
    LAB(f"{_nm(h)} in Water", eq, MIX, f"{_nm(h)} reacts with water to release hydrogen; calcium hydride inflated weather balloons in the field.",
        "Hydride#Ionic_hydrides", dh=-130)

# oxides, peroxides and superoxides
LAB("Burning Strontium", "2 Sr + O2 -> 2 SrO", HEAT, "Strontium burns with a crimson flame to strontia.", "Strontium_oxide", dh=-1184)
LAB("Burning Potassium", "K + O2 -> KO2", HEAT, "Potassium burning in air makes yellow superoxide rather than the simple oxide.", "Potassium_superoxide#Production", dh=-285)
LAB("Superoxide Rebreather", "4 KO2 + 2 CO2 -> 2 Potash + 3 O2", MIX,
    "Breath passed over potassium superoxide: carbon dioxide out, oxygen back.", "Potassium_superoxide#Applications", dh=-200)
LAB("Sodium Peroxide", "2 Na2O + O2 -> 2 Na2O2", HEAT, "Sodium oxide heated in oxygen takes up more of it.", "Sodium_peroxide#Production", T=400, dh=-180)
LAB("Peroxide Air Scrubber", "2 Na2O2 + 2 CO2 -> 2 SodaAsh + O2", MIX,
    "Sodium peroxide turns exhaled carbon dioxide into soda and oxygen.", "Sodium_peroxide#Uses", dh=-450)
LAB("Peroxide from Peroxide", "Na2O2 + 2 H2O -> 2 NaOH + H2O2", COOL, "Sodium peroxide stirred into ice water gives hydrogen peroxide.", "Sodium_peroxide", T=0, dh=-100)
LAB("Overheating Pyrolusite", "4 MnO2 -> 2 Mn2O3 + O2", HEAT, "Above 500 C manganese dioxide gives up some of its oxygen.", "Manganese(III)_oxide", T=550, dh=160)
LAB("Fumed Silica", "SiCl4 + 2 H2 + O2 -> FumedSilica + 4 HCl", HEAT,
    "Silicon tetrachloride burnt in a hydrogen-oxygen flame makes a smoke of silica nanoparticles.", "Fumed_silica#Production", T=1500, dh=-500)
LAB("Smoke Screen", "TiCl4 + 2 H2O -> TiO2 + 4 HCl", MIX,
    "Titanium tetrachloride fumes into dense white smoke in moist air; navies laid smoke screens with it in WWI.", "Titanium_tetrachloride#Uses", dh=-200)
LAB("Perchloric Acid", "NaClO4 + HCl -> HClO4 + NaCl", DISTIL,
    "Sodium perchlorate and hydrochloric acid; the perchloric acid is distilled off under reduced pressure.", "Perchloric_acid#Production", T=100, dh=10)

# phosphates and hydrates
LAB("Synthetic Bone Mineral", "10 Ca(OH)2 + 6 H3PO4 -> Hydroxyapatite + 18 H2O", MIX,
    "Lime water and phosphoric acid precipitate hydroxyapatite, used to coat hip implants so bone grows onto them.", "Hydroxyapatite#Synthesis", dh=-500)
LAB("Struvite", "MgCl2 + NH3 + H3PO4 + 6 H2O -> Struvite + 2 HCl", MIX,
    "Magnesium, ammonium and phosphate crystallise together as struvite.", "Struvite", dh=-60)
LAB("Calcium Phosphate", "3 CaCl2 + 2 Na3PO4 -> PhosphateRock + 6 NaCl", MIX,
    "Calcium and phosphate ions precipitate tricalcium phosphate, the same compound as phosphate rock.", "Tricalcium_phosphate", dh=-70)
for salt, hyd, eq, note in [
    ("MgSO4", "EpsomSalt", "MgSO4 + 7 H2O -> EpsomSalt", "needle-like crystals"),
    ("ZnSO4", "WhiteVitriol", "ZnSO4 + 7 H2O -> WhiteVitriol", "colourless prisms"),
    ("CoCl2", "CoCl2Hex", "CoCl2 + 6 H2O -> CoCl2Hex", "blue powder turning pink"),
    ("FeSO4", "GreenVitriol", "FeSO4 + 7 H2O -> GreenVitriol", "pale green crystals"),
]:
    LAB(f"Crystallising {_nm(hyd)}", eq, COOL, f"{_nm(salt)} crystallises from cold water with its water of crystallisation: {note}.",
        SUBSTANCES[hyd].wiki or "Water_of_crystallization", T=5, dh=-80)
LAB("Drying Cobalt Chloride", "CoCl2Hex -> CoCl2 + 6 H2O", HEAT,
    "Warm the pink hexahydrate and it turns blue as it dries: the humidity indicator in reverse.", "Cobalt(II)_chloride#Properties", T=120, dh=80)
LAB("Growing Alum", "K2SO4 + Al2(SO4)3 + 24 H2O -> 2 Alum", COOL,
    "Potassium and aluminium sulfates crystallise together as octahedra of alum.", "Alum#Production", T=10, dh=-100)
LAB("Growing Chrome Alum", "K2SO4 + Cr2SO43 + 24 H2O -> 2 ChromeAlum", COOL,
    "The chromium analogue of alum grows deep purple octahedra.", "Chrome_alum", T=10, dh=-100)
LAB("Blood-Red Test", "FeCl3 + 3 KSCN -> FeSCN3 + 3 KCl", MIX,
    "Thiocyanate turns any solution containing ferric iron blood red.", "Iron(III)_thiocyanate", dh=-20)

# displacement: the reactivity series in a test tube
for eq, a, b in [
    ("Mg + CuSO4 -> MgSO4 + Cu", "Mg", "Cu"), ("Zn + 2 AgNO3 -> ZnNO32 + 2 Ag", "Zn", "Ag"),
    ("Cu + HgNO32 -> Cu(NO3)2 + Hg", "Cu", "Hg"), ("Zn + CdSO4 -> ZnSO4 + Cd", "Zn", "Cd"),
    ("Mg + ZnSO4 -> MgSO4 + Zn", "Mg", "Zn"), ("2 Al + 3 CuSO4 -> Al2(SO4)3 + 3 Cu", "Al", "Cu"),
]:
    LAB(f"{_nm(a)} Displaces {_nm(b)}", eq, MIX,
        f"{_nm(a)} is more reactive than {_nm(b).lower()}, so it goes into solution and {_nm(b).lower()} comes out as metal.",
        "Reactivity_series", dh=-150)

# thermite family
for eq, ox, metal in [
    ("3 CuO + 2 Al -> Alumina + 3 Cu", "CuO", "Cu"), ("3 V2O5 + 10 Al -> 6 V + 5 Alumina", "V2O5", "V"),
    ("3 NiO + 2 Al -> Alumina + 3 Ni", "NiO", "Ni"), ("WO3 + 2 Al -> W + Alumina", "WO3", "W"),
    ("3 Sand + 4 Al -> 3 Si + 2 Alumina", "Sand", "Si"),
]:
    LAB(f"Aluminothermic {_nm(metal)}", eq, HEAT,
        f"Aluminium powder rips the oxygen from {_nm(ox).lower()}, leaving molten {_nm(metal).lower()} (Goldschmidt's thermite, 1893).",
        "Aluminothermic_reaction", T=2000, dh=-1000)

# a few more fragrant esters (Fischer esterification)
for acid, alc, ester, note in [
    ("LacticAcid", "Ethanol", "EthylLactate", "a solvent you could drink"),
    ("Salicylic", "Ethanol", "EthylSalicylate", "a wintergreen note"),
    ("Propionic", "Methanol", "MethylPropionate", "a rum note"),
    ("Butyric", "IsoamylAlcohol", "IsoamylButyrate", "apricot and pear drops"),
    ("Formic", "BenzylAlcohol", "BenzylFormate", "a jasmine note"),
    ("Anthranilic", "Ethanol", "EthylAnthranilate", "Concord grape"),
    ("Butyric", "Butanol", "ButylButyrate", "pineapple"),
    ("Propionic", "Propanol", "PropylPropionate", "pear and banana"),
]:
    LAB(f"Making {_nm(ester)}", f"{acid} + {alc} -> {ester} + H2O", CAT,
        f"Acid and alcohol joined by Fischer esterification with sulfuric acid as catalyst: {note}.",
        "Fischer%E2%80%93Speier_esterification", cat="H2SO4", T=80, dh=-5)
E3.reactions.append(R("Acetone from Grey Acetate", "CaOAc2 -> Acetone + CaCO3", DISTIL,
    "Calcium acetate from wood vinegar, dry-distilled: the acetone that made cordite until Weizmann's fermentation took over in 1915.",
    wiki="Calcium_acetate#Uses", T=400, dh=150))


def _to_era(product, epoch):
    """Move the first laboratory reaction making `product` into an era whose chemistry needs it,
    so the tech-tree planner meets it in time rather than in the laboratory epilogue."""
    for r in E7.reactions:
        if r.equation.split(" -> ")[1].split(" + ")[0].split()[-1] == product:
            E7.reactions.remove(r)
            epoch.reactions.append(r)
            return
    raise SystemExit(f"no laboratory reaction makes {product}")


_to_era("CaOAc2", E3)
for _p in ("CoCl2", "CuOH2", "NiSO4", "NiOH2", "CdSO4", "CdOH2"):
    _to_era(_p, E4)
_to_era("MnSO4", E5)


def _early(epoch, name, after=None):
    """Gate reactions go near the front of their era so the tech tree reaches them in time."""
    r = next(x for x in epoch.reactions if x.name == name)
    epoch.reactions.remove(r)
    at = 0 if after is None else 1 + next(i for i, x in enumerate(epoch.reactions) if x.name == after)
    epoch.reactions.insert(at, r)


_early(E3, "Thilorier's Dry Ice", after="Cavendish's Inflammable Air")
_early(E4, "Siemens' Dynamo")
_early(E4, "Moissan's Tungsten Carbide", after="Moissan's Fluorine")
_early(E5, "Carboloy")


# ======================================================================================
# 4b. MORE FOR THE TIER VESSELS
# ======================================================================================
N("oXylene", "o-Xylene", "C8H10", "Liquid", "The ortho isomer of xylene, cut from coal tar and reformate; nearly all of it is oxidised to phthalic anhydride for plasticisers.", "O-Xylene", smiles="Cc1ccccc1C")
N("Hexane", "Hexane", "C6H14", "Liquid", "A light naphtha alkane; the solvent that extracts most of the world's soybean oil.", "Hexane", smiles="CCCCCC")
N("Heptane", "Heptane", "C7H16", "Liquid", "Straight-chain heptane knocks so badly in an engine that it defines zero on the octane scale (isooctane is 100).", "Heptane", smiles="CCCCCCC")
N("LiquidNe", "Liquid Neon", "Ne", "Liquid", "Boils at -246 C with forty times the cooling power of liquid helium per litre; Travers liquefied it in 1898.", "Neon#Production", color="#ffd0c0")
N("LiquidF2", "Liquid Fluorine", "F2", "Liquid", "Pale yellow, condensed by Moissan and Dewar in 1897 with liquid air; fierce enough that rocket engineers tested it as an oxidiser.", "Fluorine#History")
N("NbTi", "Niobium-Titanium", "NbTi", "Solid", "The workhorse superconducting alloy (1962): below 9 K it carries current with no resistance at all. Every MRI scanner and the LHC's magnets are wound from it.", "Niobium%E2%80%93titanium", props=["IsMetal"])
N("SCMagnet", "Superconducting Magnet", "mixture", "Solid", "Coils of niobium-titanium bathed in liquid helium: fields of several tesla with no power used once the current is flowing.", "Superconducting_magnet", balance="NbTi")
N("IceVII", "Ice VII", "H2O", "Solid", "A dense cubic ice that is stable above 20,000 atmospheres even far above 100 C. Bridgman made it in 1937; it has since been found trapped in diamonds.", "Ice_VII", color="#e0f0ff")
N("GemDiamond", "Gem-Quality Diamond", "C", "Solid", "GE grew the first jewel-quality synthetic diamonds in 1970, over a week each, from a seed in a temperature gradient.", "Synthetic_diamond#High_pressure,_high_temperature", color="#f0f8ff")
N("Nanodiamond", "Nano-Polycrystalline Diamond", "C", "Solid", "Tetsuo Irifune's 'hyperdiamond' (Ehime, 2003): graphite or fullerene squeezed straight into nanocrystals, harder than single-crystal diamond.", "Aggregated_diamond_nanorods", color="#e8e8f0")
N("BGO", "Bismuth Germanate", "Bi4Ge3O12", "Solid", "A dense scintillator crystal that flashes when gamma rays hit it: the detector ring of PET scanners and of the L3 experiment at CERN.", "Bismuth_germanate", color="#f4f4e8")
N("SiCCrystal", "Silicon Carbide Crystal", "SiC", "Solid", "Jan Anthony Lely sublimed silicon carbide into clean crystals in 1955; their wafers now switch power in electric cars.", "Silicon_carbide#Electronic_applications", color="#507050")
N("CaF2Crystal", "Fluorite Optics", "CaF2", "Solid", "Calcium fluoride crystal transparent deep into the ultraviolet: the lenses of the 193 nm lithography that prints chips.", "Calcium_fluoride#Uses", color="#f0f0ff")
N("SoySauce", "Soy Sauce", "mixture", "Liquid", "Soybeans and grain fermented with salt for months; its Chinese ancestor, jiang, dates back to the Han dynasty.", "Soy_sauce", color="#3a1a08", balance="C")
N("Kombucha", "Kombucha", "mixture", "Liquid", "Sweet tea fermented by a mat of yeast and acetic bacteria into a tart drink.", "Kombucha", color="#c08040", balance="C")
N("Phosphorus32", "Phosphorus-32", "P", "Solid", "A beta emitter (half-life 14 days) made from sulfur in reactors; John Lawrence treated leukaemia with it in 1936.", "Phosphorus-32", props=["IsRadioactive"])
N("Lutetium177", "Lutetium-177", "Lu", "Solid", "A short-lived radiometal that, bound to a peptide, hunts down neuroendocrine tumours (Lutathera, 2018).", "Lutetium-177", props=["IsMetal", "IsRadioactive"])
L("Cyclohexanol", "Cyclohexanol", "C6H12O", "Liquid", smiles="OC1CCCCC1")
N("AHQ", "Anthrahydroquinone", "C14H10O2", "Solid", "The reduced form of anthraquinone; air oxidises it straight back, handing over hydrogen peroxide.", "Anthraquinone_process", smiles="Oc1c2ccccc2c(O)c2ccccc12")
N("Mg2Si", "Magnesium Silicide", "Mg2Si", "Solid", "Blue-grey crystals that give off silane when acid touches them.", "Magnesium_silicide")
N("SiH4", "Silane", "SiH4", "Gas", "Silicon's hydride, which bursts into flame in air; decomposed on hot glass it lays down the amorphous silicon of thin-film solar panels and screens.", "Silane")
N("AmorphousSi", "Amorphous Silicon", "Si", "Solid", "Hydrogenated, disordered silicon a micrometre thick: the switches behind every pixel of a flat-panel display (Spear and LeComber, 1975).", "Amorphous_silicon", color="#5a4a40")
N("TiN", "Titanium Nitride", "TiN", "Solid", "A golden ceramic coating, a few micrometres thick, that makes drill bits last ten times longer.", "Titanium_nitride", color="#d8b040")
N("Xanthan", "Xanthan Gum", "mixture", "Solid", "A slime made by Xanthomonas bacteria (USDA, 1960s) that thickens sauces and drilling mud.", "Xanthan_gum", balance="C", props=["IsPolymer"])
N("Galactose", "Galactose", "C6H12O6", "Solid", "The other half of milk sugar; people who can't digest lactose can digest the two halves.", "Galactose", smiles="OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@H]1O")

# --- gold as people actually won it, and cider (Nex, 2026-11-19) ------------------------
N("GoldGravel", "Gold-Bearing Gravel", "mixture", "Solid", "River gravel with flakes and nuggets of native gold, washed down from quartz veins upstream.", "Placer_mining", color="#c8a048", balance="SiO2")
N("GoldQuartz", "Gold-Bearing Quartz", "mixture", "Solid", "Vein quartz with gold too fine to see, a few grams in every tonne of rock: the kind of ore most of the world's gold now comes from.", "Gold_mining", color="#d8d0b8", balance="SiO2")
N("GoldAmalgam", "Gold Amalgam", "mixture", "Solid", "Gold dissolved in mercury: a soft, silvery paste. Fire-gilders painted it onto bronze and drove the mercury off with heat.", "Amalgam_(chemistry)", color="#c8c0a8", balance="AuHg")
N("Cider", "Cider", "mixture", "Liquid", "Fermented apple juice, usually 4 to 8% alcohol.", "Cider", color="#e0a838", balance="C")
N("Calaverite", "Calaverite", "AuTe2", "Solid", "Gold telluride, about 40% gold, yet brassy enough to pass for fool's gold. Kalgoorlie's miners threw it on the dumps and paved paths with it until 1896, when it was recognised and the streets were dug up.", "Calaverite", color="#c8b070")
N("TeO2", "Tellurium Dioxide", "TeO2", "Solid", "The white oxide tellurium burns to; in the tellurite glass of some optical fibres.", "Tellurium_dioxide", color="#f0eee0")

E0.reactions += [
    R("Panning for Gold", "GoldGravel + H2O -> Au + Sand", MIX,
      "Swirled in a pan of water, heavy gold sinks while the lighter gravel washes over the rim. Gold lies in streams as the bare metal, so it was the first metal people worked: the Varna graves in Bulgaria (about 4500 BCE) hold some three thousand gold objects.",
      wiki="Gold_panning", exact=False),
]
E1.reactions += [
    R("Mercury Amalgamation", "GoldQuartz + Hg -> GoldAmalgam + Sand", MIX,
      "Crushed ore ground with mercury: the gold dissolves into it as a soft amalgam and the rock does not. Rome used it, and so did the mines of Spanish America; small-scale gold mining still puts more mercury into the world than any other trade.",
      wiki="Gold_extraction#Mercury_process", exact=False),
    R("Roasting the Amalgam", "GoldAmalgam -> Au + Hg", HEAT,
      "Heated, the amalgam gives off its mercury as vapour and leaves spongy gold. In the open the vapour poisons whoever stands over it; a retort catches the mercury to use again.",
      wiki="Amalgam_(chemistry)#Gold_amalgam", exact=False),
    R("Fermenting Cider", "Apples -> Cider", FERM,
      "Crushed apples ferment on their own yeasts into cider. Pliny wrote of wine made from apples, and English farm labourers were once paid partly in cider.",
      wiki="Cider#History", exact=False),
    R("Cider Vinegar", "Cider + O2 -> AcOH", FERM,
      "Left open to the air, cider sours as acetic acid bacteria turn its alcohol into vinegar, just as they do with wine.",
      wiki="Apple_cider_vinegar", exact=False),
    R("Salt Cementation", "Electrum + NaCl -> Au + AgCl", HEAT,
      "Natural gold carries silver. Lydia's refiners at Sardis (about 600 BCE) packed electrum foil in salt and brick dust and kept it hot for days: the silver turned to chloride and soaked into the brick, leaving gold pure enough for Croesus's coins.",
      wiki="Gold_parting", exact=False, T=800),
]
E3.reactions += [
    R("Kipp's Hydrogen Sulfide", "FeS + H2SO4 -> FeSO4 + H2S", MIX,
      "Dilute sulfuric acid on iron sulfide gives the same rotten-egg gas as spirit of salt does. Petrus Kipp's apparatus (1844) let a laboratory turn the supply on and off like a tap.",
      wiki="Kipp%27s_apparatus", dh=-30),
]
E4.reactions += [
    R("Roasting Calaverite", "Calaverite + 2 O2 -> Au + 2 TeO2", HEAT,
      "Gold locked up with tellurium will not dissolve in cyanide. Roasted, the tellurium burns off as its oxide and leaves porous gold the cyanide can reach: the treatment that made Kalgoorlie's Golden Mile pay.",
      wiki="Calaverite", T=600),
]

E1.reactions += [
    R("Orleans Vinegar", "Wine + O2 -> AcOH", FERM,
      "Wine left in half-filled barrels grows a 'mother' of acetic bacteria; the Orleans method has made wine vinegar since the Middle Ages.",
      wiki="Vinegar#Production", exact=False),
    R("Fermenting Soy Sauce", "Soybeans + Barley + NaCl -> SoySauce", FERM,
      "Cooked soybeans and roasted grain inoculated with koji mould and left in brine for months.", wiki="Soy_sauce#Production", exact=False),
]
E3.reactions += [
    R("Coffey's Patent Still", "Beer -> Ethanol + IsoamylAlcohol + H2O", COLUMN,
      "Aeneas Coffey's two-column still (Dublin, 1830) distilled continuously to 95% spirit: the grain neutral spirit of gin and blended whisky.",
      wiki="Column_still#History", exact=False),
    R("Brewing Kombucha", "TeaLeaves + Sucrose -> Kombucha", FERM,
      "Sweetened tea fermented with a symbiotic culture of bacteria and yeast.", wiki="Kombucha", exact=False),
]
E4.reactions += [
    R("Neuberg's Glycerol", "Glucose + NaHSO3 -> Glycerol + Acetaldehyde + CO2", FERM,
      "Carl Neuberg (1918) trapped yeast's acetaldehyde with bisulfite, so the cell made glycerol instead: Germany's wartime glycerol for explosives.",
      wiki="Carl_Neuberg", exact=False),
    R("Biogas Digester", "Cellulose + H2O -> 3 Methane + 3 CO2", FERM,
      "Bacteria in a sealed tank turn plant waste to methane; Exeter lit its street lamps with sewage gas in 1895.", wiki="Anaerobic_digestion#History", dh=-140),
    R("Coal-Tar Light Oil", "CoalTar -> Benzene + Toluene + mXylene + pXylene + oXylene + Naphthalene", COLUMN,
      "Coal tar fractionated in columns into pure benzene, toluene, the three xylenes and naphthalene.", wiki="Coal_tar#Composition", exact=False),
    R("Gasoline Stabiliser", "Gasoline -> Butane + Isopentane", COLUMN,
      "A column strips the light ends out of raw gasoline so it does not boil off in the tank.", wiki="Natural-gas_condensate#Stabilization", exact=False),
    R("Moissan and Dewar's Liquid Fluorine", "F2 -> LiquidF2", AIRLIQ,
      "Fluorine cooled with boiling liquid air condenses to a yellow liquid (1897).", wiki="Fluorine#History", T=-188, dh=-6.5),
    R("Liquid Neon", "Ne -> LiquidNe", CRYO,
      "Neon condensed in a bath of liquid hydrogen.", wiki="Neon#Production", T=-246, dh=-1.7),
]
E5.reactions += [
    R("Phthalic Anhydride from o-Xylene", "oXylene + 3 O2 -> PhthalicAnhydride + 3 H2O", CAT,
      "o-Xylene air-oxidised over vanadium pentoxide replaced naphthalene as the feed in the 1960s.", wiki="Phthalic_anhydride#Production",
      cat="V2O5", T=380, dh=-1100),
    R("Naphtha Splitter", "Naphtha -> Hexane + Heptane", COLUMN,
      "Light naphtha cut into its six- and seven-carbon alkanes.", wiki="Naphtha", exact=False),
    R("Heavy Water by Distillation", "H2O -> HeavyWater", COLUMN,
      "Heavy water boils at 101.4 C, so tall columns of trays enrich it slowly (Manhattan Project P-9 plants, 1944).", wiki="Heavy_water#Production",
      exact=False),
    R("Niobium-Titanium", "Nb + Ti -> NbTi", ARC,
      "Niobium and titanium melted together in a vacuum arc furnace, then drawn into fine filaments in copper.", wiki="Niobium%E2%80%93titanium",
      T=2000, dh=-10),
    R("Superconducting Magnet", "NbTi + LiquidHe -> SCMagnet", CRYO,
      "Niobium-titanium wire wound into a coil and cooled to 4 K: the magnet of an MRI scanner.", wiki="Superconducting_magnet", exact=False),
    R("Bridgman's Ice VII", "H2O -> IceVII", DPRESS,
      "Water squeezed past 20,000 atmospheres freezes into a dense ice even when hot.", wiki="Percy_Williams_Bridgman", T=100, P=25000, dh=-1),
    R("GE Gem Diamonds", "Diamond -> GemDiamond", DPRESS,
      "Diamond grit dissolved in molten metal recrystallises over a week onto a seed held slightly cooler.", wiki="Synthetic_diamond#History",
      cat="Ni", T=1400, P=55000, dh=0.1),
    R("Lely's Silicon Carbide", "SiC -> SiCCrystal", PULLER,
      "Silicon carbide sublimed at 2,500 C recondenses as clean hexagonal crystals.", wiki="Lely_method", T=2500, dh=0.1),
    R("Hydrogenating Phenol", "Phenol + 3 H2 -> Cyclohexanol", HIGHP,
      "Phenol saturated with hydrogen over nickel: cyclohexanol, the first step toward nylon's adipic acid.", wiki="Cyclohexanol#Production",
      cat="Ni", T=150, P=20, dh=-190),
    R("Hydroformylating Ethylene", "Ethylene + CO + H2 -> Propanal", HIGHP,
      "The oxo reaction on ethylene: propanal, the route to propionic acid and n-propanol.", wiki="Hydroformylation", cat="Co", T=150, P=200, dh=-120),
    R("Anthraquinone Hydrogenation", "Anthraquinone + H2 -> AHQ", CAT,
      "Riedl and Pfleiderer's peroxide process (IG Farben, 1939): the quinone hydrogenated over palladium...", wiki="Anthraquinone_process",
      cat="Pd", T=40, dh=-100),
    R("Anthraquinone Peroxide", "AHQ + O2 -> Anthraquinone + H2O2", MIX,
      "...then blown with air, which takes the hydrogen back as hydrogen peroxide. Nearly all the world's peroxide is made this way.",
      wiki="Anthraquinone_process", dh=-100),
    R("Catalytic Reforming", "Methylcyclohexane -> Toluene + 3 H2", CRACKER,
      "Platinum on alumina strips hydrogen from naphthenes into high-octane aromatics, and the hydrogen feeds the hydrotreaters.",
      wiki="Catalytic_reforming", cat="Pt", T=500, dh=205),
    R("Fluid Catalytic Cracking", "Kerosene -> Octene + Butane", CRACKER,
      "A fluidised powder of silica-alumina cracks heavy oil in seconds and is burnt clean in a regenerator (Standard Oil, 1942).",
      wiki="Fluid_catalytic_cracking", cat="Alumina", T=520, dh=80),
    R("Phosphorus-32", "S + EnrichedUranium -> Phosphorus32", REACTOR,
      "Fast neutrons knock a proton out of sulfur-32, leaving phosphorus-32.", wiki="Phosphorus-32", exact=False),
    R("HFIR Californium", "Cm + EnrichedUranium -> Cf", REACTOR,
      "Oak Ridge's High Flux Isotope Reactor (1965) breeds curium up to californium-252, a pocket-sized neutron source.", wiki="High_Flux_Isotope_Reactor",
      exact=False),
    R("Xanthan Gum", "Sucrose + CornSteep -> Xanthan", BIOR,
      "Xanthomonas campestris grown in deep tanks; the gum is precipitated with alcohol.", wiki="Xanthan_gum#Preparation", exact=False, T=28),
    R("Magnesium Silicide", "2 Mg + Si -> Mg2Si", HEAT,
      "Magnesium and silicon heated together.", wiki="Magnesium_silicide", T=700, dh=-78),
    R("Silane", "Mg2Si + 4 HCl -> SiH4 + 2 MgCl2", MIX,
      "Acid on magnesium silicide releases silane, which ignites with a pop as each bubble reaches the air.", wiki="Silane#Production", dh=-200),
]
E6.reactions += [
    R("Irifune's Hyperdiamond", "C60 -> 60 Nanodiamond", DPRESS,
      "Fullerene converted directly to nanocrystalline diamond at 200,000 atmospheres and 2,000 C.", wiki="Aggregated_diamond_nanorods", T=2000,
      P=200000, dh=-40),
    R("Bismuth Germanate", "2 Bi2O3 + 3 GeO2 -> BGO", PULLER,
      "Bismuth and germanium oxides melted and pulled into scintillator crystals.", wiki="Bismuth_germanate", T=1050, dh=-60),
    R("Fluorite Optics", "CaF2 -> CaF2Crystal", PULLER,
      "Calcium fluoride grown by the Bridgman method, so free of flaws it bends ultraviolet light without scattering it.", wiki="Calcium_fluoride#Uses",
      T=1420, dh=0.1),
    R("Propane Dehydrogenation", "Propane -> Propylene + H2", CRACKER,
      "Propane over platinum-tin (UOP Oleflex, 1990): propylene on purpose, from shale gas.", wiki="Propane_dehydrogenation", cat="Pt", T=600, dh=124),
    R("Zeolite Ethylbenzene", "Benzene + Ethylene -> Ethylbenzene", CRACKER,
      "Mobil-Badger (1980): ZSM-5 replaced corrosive aluminium chloride for the styrene feed.", wiki="Ethylbenzene#Production", cat="ZSM5", T=400, dh=-114),
    R("Zeolite Cumene", "Benzene + Propylene -> Cumene", CRACKER,
      "Cumene over zeolite catalysts, for phenol and acetone.", wiki="Cumene_process", cat="ZSM5", T=200, dh=-98),
    R("Lutetium-177", "Lu + EnrichedUranium -> Lutetium177", REACTOR,
      "Lutetium-176 targets capture a neutron to make the cancer-hunting isotope.", wiki="Lutetium-177", exact=False),
    R("Lactase", "Lactose + H2O -> Glucose + Galactose", BIOR,
      "An enzyme from Aspergillus splits milk sugar in two: lactose-free milk.", wiki="Lactase#Industrial_production", cat="Aspergillus", T=40, dh=-20),
    R("Amorphous Silicon Film", "SiH4 -> AmorphousSi + 2 H2", CVD,
      "Silane split in a glow discharge deposits hydrogenated amorphous silicon on glass.", wiki="Amorphous_silicon#Deposition", T=250, dh=34),
    R("Titanium Nitride Coating", "2 TiCl4 + N2 + 4 H2 -> 2 TiN + 8 HCl", CVD,
      "Titanium chloride, nitrogen and hydrogen deposit gold-coloured TiN on tools.", wiki="Titanium_nitride#Production", T=1000, dh=-200),
]

# The line each era's banner shows when the player reaches it.
for _ep, _blurb in [
    (E0, "Fire turns ore into metal. Everything starts with charcoal."),
    (E1, "Glass, soap, steel and spirits: the crafts of the ancient world."),
    (E2, "The alchemists' acids dissolve almost anything, gold included."),
    (E3, "Coal, steam and the new elements: chemistry becomes a science."),
    (E4, "Dynamos, furnaces and fertiliser: chemistry becomes an industry."),
    (E5, "Plastics, antibiotics, the atom and the transistor."),
    (E6, "Chips, genes and materials built one atomic layer at a time."),
]:
    _ep.blurb = _blurb

# ======================================================================================
# 5. THE MILESTONE LADDER
# ======================================================================================
# Each vessel unlocks on a discovery that historically made it possible; grants are kept
# small (gen_authored.MAX_GRANT) and arrive just before the chemistry that needs them.
C.MILESTONES = [
    Milestone("Cu", unlock=(SMELT,), grant=("Galena", "Goethite", "Gypsum", "Azurite"),
              message="Copper! The furnace becomes a smelter, and new ores are found."),
    Milestone("Bronze", unlock=(FERM,), grant=("Grapes", "Honey", "Barley", "Milk"),
              message="The Bronze Age, and the brewers and vintners of Sumer and Egypt: the Fermenter is unlocked."),
    Milestone("Brass", grant=("GoldGravel", "GoldQuartz", "Acanthite", "Cinnabar", "Stibnite", "FeS2", "Natron"),
              message="Bronze and brass buy gold-bearing gravel and quartz, silver ore, cinnabar and kohl from the traders."),
    Milestone("Fe", unlock=(DISTIL,),
              grant=("Tallow", "Potash", "Seawater", "VolcanicAsh", "Alum", "KNO3", "S", "GreenVitriol",
                     "MnO2", "Indican"),
              message="The Iron Age. Distillation is invented, and the markets of antiquity open."),
    Milestone("Glass", unlock=(COOL,),
              message="Glass vessels: you can now chill and crystallise in an ice bath."),
    Milestone("Ethanol", grant=("Lavender", "Peppermint", "Rose", "PineResin", "Cinnamon", "Anise", "Thyme"),
              message="Spirit of wine. The perfumers turn the still on the herb garden."),
    Milestone("AcOH", grant=("OakGalls", "Argol", "Lemons", "Apples", "Amber", "Soybeans", "Olives"),
              message="Vinegar keeps the harvest: the pantry and the apothecary's jars fill up."),
    Milestone("H2SO4", grant=("MicrocosmicSalt", "Orpiment", "Bismuthinite", "NH4Cl", "Sucrose", "Ants",
                             "GumBenzoin", "Spearmint", "OrangePeel", "Jasmine", "Turmeric"),
              message="Oil of vitriol. The alchemists' cabinet fills with strange salts."),
    Milestone("HNO3", unlock=(FLASK,),
              message="Aqua fortis eats metal and stone; only glass can hold it. The Glass Flask is unlocked."),
    Milestone("P4", grant=("Coal", "Air", "BaCO3", "MgCO3", "SrCO3", "Borax", "NaI", "NaBr", "CaF2", "Latex"),
              message="Brand's phosphorus ends the age of alchemy. Coal, air and the mineral cabinets of the new chemists."),
    Milestone("AgCl", unlock=(LIGHT,),
              message="Horn silver darkens in the sun: light itself can drive chemistry."),
    Milestone("Coke", unlock=(BLAST,),
              message="Abraham Darby's coke (1709) burns hot enough to smelt iron by the ton: the Blast Furnace is unlocked."),
    Milestone("PigIron", unlock=(PRESS,),
              grant=("Cobaltite", "Nickeline", "Scheelite", "MoS2", "Chromite", "Spodumene", "Greenockite", "PlatinumOre"),
              message="Coke iron makes boilers: Papin's digester becomes the Autoclave, and the mines go deeper."),
    Milestone("VulcRubber", unlock=(POLY,),
              message="Goodyear's rubber: long chains are a material of their own. Polymerisation unlocked."),
    Milestone("H2", grant=("Pitchblende", "Gadolinite", "Cerite", "Beryl", "Thorite", "Zircon", "Vanadinite", "Columbite"),
              message="Cavendish's inflammable air. The hunt for new elements begins in earnest."),
    Milestone("Cl2", grant=("PhosphateRock", "Cellulose", "DriedBlood", "Starch", "PalmOil", "Silk", "Horn"),
              message="Scheele's chlorine bleaches linen, and chemists start taking apart animal and vegetable matter."),
    Milestone("Battery", unlock=(ELEC,),
              message="Volta's pile: electricity tears compounds apart. Electrolysis unlocked."),
    Milestone("I2", grant=("WillowBark", "Cinchona", "TeaLeaves", "Cocoa", "Tobacco", "Belladonna", "Foxglove",
                          "TonkaBeans", "BitterAlmonds"),
              message="Courtois's iodine came out of seaweed: plants hide elements, and medicines too. The apothecaries send their herbs."),
    Milestone("Pt", unlock=(CAT,),
              message="Platinum makes reactions go without being used up. Catalysis unlocked."),
    Milestone("DryIce", unlock=(AIRLIQ,),
              message="Thilorier's dry ice at -78 C. The race to liquefy every gas has begun: the Air Liquefier is unlocked."),
    Milestone("He", unlock=(CRYO,),
              message="Ramsay's helium is the last gas nobody has liquefied. Dewar in London and Kamerlingh Onnes in Leiden race to reach it, with nested vacuum flasks cooled stage by stage: the Cryostat is unlocked."),
    Milestone("Benzene", unlock=(COLUMN,),
              message="Charles Mansfield fractionates coal tar into pure benzene (1849): the Fractionating Column is unlocked."),
    Milestone("Urea", grant=("Camphor", "Clove", "Asparagus", "Lupin", "Manna", "Carrots", "Eucalyptus", "Cumin"),
              message="Wohler's urea: organic chemistry is just chemistry. The apothecary's shelf opens."),
    Milestone("Quinine", grant=("Tarragon", "Buckwheat", "Lemongrass", "Yeast", "Comfrey", "Rowan", "Valerian",
                               "Nutmeg", "LinseedOil", "CastorBeans", "Cork"),
              message="Quinine from cinchona bark: chemists race to extract every plant's secret."),
    Milestone("Dynamo", unlock=(ECELL,), grant=("CrudeOil", "Bauxite", "Chalcopyrite", "Calaverite"),
              message="Siemens' dynamo makes electricity by the ton: the Electrolytic Cell is unlocked, and oil, bauxite, copper ore and gold telluride are worth digging."),
    Milestone("NaHCO3", grant=("Kieselguhr", "Sphalerite", "Samarskite", "Lepidolite", "MineralWater", "Argyrodite",
                               "Sugarcane"),
              message="Solvay's ammonia soda (1861) founds the heavy chemical industry."),
    Milestone("F2", unlock=(ARC,),
              message="Henri Moissan isolated fluorine (1886); his electric arc furnace (1892) reaches 3,500 C. The Arc Furnace is unlocked."),
    Milestone("Gasoline", unlock=(CRACKER,),
              message="Gasoline for the motor car. Catalytic crackers will make more of it from heavy oil: the Catalytic Cracker is unlocked."),
    Milestone("StainlessSteel", unlock=(HIGHP,),
              message="Alloy steel strong enough to hold 200 atmospheres: the High-Pressure Reactor is unlocked."),
    Milestone("Aspirin", grant=("Kombu", "AdrenalGlands", "CrabShells", "Tomatoes", "Ginger"),
              message="Bayer's aspirin (1899): the pharmaceutical industry is born."),
    Milestone("Bakelite", grant=("NaturalGas", "TiO2", "CoconutOil"),
              message="The age of plastics. Natural gas and rutile arrive."),
    Milestone("Vanillin", message="Tiemann and Haarmann's synthetic vanilla (1874): the flavour industry learns to make what plants make."),
    Milestone("GasMantle", message="Welsbach's thorium mantle (1891) turns a gas flame into brilliant white light: the rare earths find their first use."),
    Milestone("MSG", message="Kikunae Ikeda tastes kombu broth and names a fifth taste, umami (1908)."),
    Milestone("DryCell", message="Gassner's dry cell (1886): electricity you can carry in your pocket."),
    Milestone("WC", message="Moissan's carbides: in the arc furnace almost anything will combine with carbon, and the results are nearly as hard as diamond."),
    Milestone("PE", grant=("Bran", "RiceBran", "EggYolk", "Spinach"),
              message="ICI's polythene (1933), found by accident at 1,400 atmospheres. Meanwhile biochemists hunt the vitamins in bran, egg and spinach."),
    Milestone("Nylon66", message="Carothers' nylon (1935): 'as strong as steel, as fine as a spider's web'. Stockings sold out in a day in 1940."),
    Milestone("Sulfanilamide", unlock=(BIOR,), grant=("Penicillium", "CornSteep", "Aspergillus", "Streptomyces", "Ecoli",
                                                    "Blood"),
              message="The sulfa drugs work, and Florey and Chain need penicillin by the vat: the Bioreactor is unlocked."),
    Milestone("VitaminC", grant=("CodLiverOil", "Lanolin", "SharkLiverOil", "Corynebacterium"),
              message="Szent-Gyorgyi and Reichstein's vitamin C (1933): the hunt for every vitamin is on."),
    Milestone("Carboloy", unlock=(DPRESS,),
              message="Cemented carbide anvils hold 50,000 atmospheres: the Diamond Press is unlocked."),
    Milestone("Polysilicon", unlock=(PULLER,),
              message="Silicon pure to one part in a billion. Teal's Crystal Puller grows it into one flawless crystal."),
    Milestone("Transistor", unlock=(CVD,), grant=("CoffeeBeans", "Wormwood", "Monazite", "Lactose"),
              message="The transistor (1947). The silicon age opens: the CVD Chamber is unlocked."),
    Milestone("U", unlock=(REACTOR,),
              message="Uranium metal for Fermi's pile (Chicago, 2 December 1942): the Nuclear Reactor is unlocked."),
    Milestone("Np", unlock=(CYCLO,),
              message="Neptunium, the first element beyond uranium. Lawrence's cyclotron will reach further: the Cyclotron is unlocked."),
    Milestone("Streptomycin", message="Streptomycin cures tuberculosis (1944): the golden age of antibiotics, dug out of the soil."),
    Milestone("MOSFET", message="Atalla and Kahng's MOSFET (1959). Every chip ever since is built from it."),
    Milestone("Microchip", message="The microprocessor (Intel 4004, 1971): 2,300 transistors on a chip. Today's carry tens of billions."),
    Milestone("BlueLED", message="The blue LED (Akasaki, Amano, Nakamura, 1993; Nobel 2014). White light from a diode at last."),
    Milestone("Insulin", message="Human insulin from bacteria (1978): biology becomes a factory."),
    Milestone("Og", message="Oganesson (Dubna, 2002; named 2016): the seventh row of the periodic table is complete."),
]


# ======================================================================================
# 6. SEPARATION: the Centrifuge and the Ultracentrifuge
# ======================================================================================
# Spinning sorts a mixture by density: cream from milk, crystals from syrup, cells from
# plasma, and at the top grade proteins, plasmids and the isotopes of uranium.
RAW("Sugarcane", "Sugarcane", "Saccharum stalks, up to six metres tall, their pith full of sweet juice. The plantation crop that fed the Atlantic sugar trade.", "Sugarcane", "#8ab048")
RAW("Blood", "Blood", "Whole blood: red and white cells and platelets carried in plasma. Slaughterhouses sold it to chemists; donors fill today's blood banks.", "Blood", "#8a1020", state="Liquid")
N("CaneJuice", "Sugarcane Juice", "mixture", "Liquid", "The juice pressed from sugarcane: water and about a sixth sucrose, with a little glucose, fructose and minerals.", "Sugarcane_juice", color="#c8c070", balance="C")
N("Bagasse", "Bagasse", "mixture", "Solid", "The crushed fibre left once the juice is pressed out. Sugar mills burn it for their own steam; it also makes paper and board.", "Bagasse", color="#c8b080", balance="C")
N("Molasses", "Molasses", "mixture", "Liquid", "The dark syrup spun off the sugar crystals: cattle feed, rum, and the feedstock of much of the world's fermentation industry.", "Molasses", color="#3a2010", balance="C")
N("Cream", "Cream", "mixture", "Liquid", "The fat-rich layer of milk, a third to a half butterfat, which rises on standing and gathers at once in a separator.", "Cream", color="#f8f0d8", balance="C")
N("SkimMilk", "Skimmed Milk", "mixture", "Liquid", "Milk with its fat spun out: the protein and lactose stay, for drinking, cheese and milk powder.", "Skimmed_milk", color="#e8eef4", balance="C")
N("Buttermilk", "Buttermilk", "mixture", "Liquid", "The thin liquid left when cream is churned into butter, sharp with lactic acid; it raises soda bread.", "Buttermilk", color="#f0eedc", balance="C")
N("BloodPlasma", "Blood Plasma", "mixture", "Liquid", "The straw-coloured liquid that carries the blood cells: water, salts and some hundreds of proteins. Dried, it kept the wounded alive in the Second World War.", "Blood_plasma", color="#e8c868", balance="C")
N("RedBloodCells", "Red Blood Cells", "mixture", "Liquid", "Erythrocytes, packed with haemoglobin: the oxygen carriers, which give blood its colour.", "Red_blood_cell", color="#a01828", balance="C")
N("SerumAlbumin", "Serum Albumin", "mixture", "Solid", "The commonest protein in blood plasma, which holds water in the blood vessels. Given by drip for shock and burns.", "Human_serum_albumin", color="#f4ecd0", balance="C")
N("Immunoglobulin", "Immunoglobulin", "mixture", "Solid", "Antibodies gathered from the plasma of many donors, given to people who cannot make enough of their own.", "Immunoglobulin_therapy", color="#e8e0f0", balance="C")
N("LDL", "Low-Density Lipoprotein", "mixture", "Liquid", "The particles that carry cholesterol out to the body's cells; high levels clog arteries ('bad cholesterol').", "Low-density_lipoprotein", color="#e0b850", balance="C")
N("HDL", "High-Density Lipoprotein", "mixture", "Liquid", "The denser particles that carry cholesterol back to the liver ('good cholesterol').", "High-density_lipoprotein", color="#f0d890", balance="C")
RAW("Latex", "Latex", "Hevea latex: a milky emulsion of rubber particles in a watery serum, tapped from cuts in the bark of the rubber tree.", "Latex", "#f4f0e0", state="Liquid")
RAW("Olives", "Olives", "The fruit of Olea europaea, a fifth to a third oil by weight.", "Olive", "#6a7a30")
N("LatexConcentrate", "Latex Concentrate", "mixture", "Liquid", "Latex spun up to about 60% rubber. Moulds dipped in it come out as gloves, balloons and condoms.", "Latex", color="#f8f4e4", balance="C")
N("Pomace", "Olive Pomace", "mixture", "Solid", "What is left when the oil is out: skins, pulp and stones, burned for fuel or extracted again for pomace oil.", "Pomace", color="#5a4a28", balance="C")
N("Haemoglobin", "Haemoglobin", "mixture", "Solid", "The iron-carrying protein that fills red cells and carries oxygen; one of the first proteins weighed in Svedberg's ultracentrifuge.", "Hemoglobin", color="#901020", balance="C")
N("SemiconductingCNT", "Semiconducting Carbon Nanotubes", "C", "Solid", "Carbon nanotubes sorted to the kind that behave as semiconductors: candidates for transistors smaller than silicon allows.", "Carbon_nanotube")
N("PlasmidDNA", "Plasmid DNA", "mixture", "Solid", "Small rings of DNA that bacteria swap between themselves. Cut and pasted, they carry the genes of genetic engineering.", "Plasmid", color="#d0e8f8", balance="C")

E4.reactions += [
    R("Pressing Sugarcane", "Sugarcane -> CaneJuice + Bagasse", MIX,
      "Cane crushed between iron rollers; the juice runs off and the fibre is left.", wiki="Sugarcane_juice", exact=False),
    R("Centrifugal Sugar", "CaneJuice -> Sucrose + Molasses", CENT,
      "Cane juice boiled down to a syrup thick with crystals, then spun in a perforated basket: the molasses flies off and the sugar stays.",
      wiki="Molasses", exact=False),
    R("Rum", "Molasses -> Ethanol + CO2", FERM,
      "Molasses diluted and fermented by yeast, as the sugar islands made rum; today it feeds much of the world's industrial ethanol.",
      wiki="Rum#Manufacturing_process", exact=False),
    R("de Laval's Cream Separator", "Milk -> Cream + SkimMilk", CENT,
      "Spun fast, milk's fat globules crowd to the centre and the cream runs off: Gustaf de Laval's separator replaced skimming by hand.",
      wiki="Separator_(milk)", exact=False),
    R("Coagulating Latex", "Latex + AcOH -> Rubber", MIX,
      "Fresh latex curdled with a little acid into slabs of raw rubber, as the plantations of Malaya and Ceylon did it.",
      wiki="Natural_rubber", exact=False),
]
E5.reactions += [
    R("Separating Blood", "Blood -> BloodPlasma + RedBloodCells", CENT,
      "Whole blood spun down: the red cells pack at the bottom and the plasma floats above. The blood banks of the 1930s kept both.",
      wiki="Blood_plasma", exact=False),
    R("Cohn Fractionation", "BloodPlasma + Ethanol -> SerumAlbumin + Immunoglobulin", CENT,
      "Edwin Cohn's wartime process: cold ethanol at rising strength drops the plasma proteins out one by one, each spun or filtered off.",
      wiki="Cohn_process", exact=False, T=-5),
    R("Concentrating Latex", "Latex -> LatexConcentrate + H2O", CENT,
      "Latex spun to throw off most of its watery serum, so it ships as a cream of rubber instead of a mostly-water milk.",
      wiki="Latex", exact=False),
    R("Svedberg's Haemoglobin", "RedBloodCells + H2O -> Haemoglobin", ULTRA,
      "Red cells burst in water and spun clear of their membranes; in Svedberg's rotor haemoglobin settled as one molecule of definite weight.",
      wiki="Hemoglobin", exact=False),
    R("Lipoproteins", "BloodPlasma -> LDL + HDL", ULTRA,
      "Spun at hundreds of thousands of g, plasma's fat-carrying particles float apart by density into the low- and high-density lipoproteins.",
      wiki="Lipoprotein", exact=False),
    R("Zippe's Gas Centrifuge", "UF6 -> EnrichedUF6", ULTRA,
      "Uranium hexafluoride spun in tall thin rotors: the heavier uranium-238 crowds to the wall, the lighter 235 is drawn off near the axis. Cascades of them replaced gaseous diffusion.",
      wiki="Gas_centrifuge", exact=False),
]
E6.reactions += [
    R("Olive Oil Decanter", "Olives -> Triolein + Pomace", CENT,
      "Olives milled to a paste and spun in a horizontal decanter, which replaced the press from the 1970s: oil, water and solids leave by separate ports.",
      wiki="Olive_oil", exact=False),
    R("Sorting Nanotubes", "CNT -> SemiconductingCNT", ULTRA,
      "Nanotubes coated in surfactant and spun through a density gradient settle by diameter and by whether they conduct like a metal or a semiconductor.",
      wiki="Carbon_nanotube", exact=False),
    R("Plasmid Prep", "Ecoli + CsCl -> PlasmidDNA", ULTRA,
      "Bacteria broken open and their DNA spun for days in a caesium chloride density gradient: the small circular plasmids settle in a band of their own.",
      wiki="Plasmid#Plasmid_DNA_extraction", exact=False),
]

C.MILESTONES += [
    Milestone("CaneJuice", unlock=(CENT,),
              message="Steam sugar mills spin their syrup in perforated baskets to throw off the molasses, and Gustaf de Laval does the same to milk: the Centrifuge is unlocked."),
    Milestone("BloodPlasma", unlock=(ULTRA,),
              message="Theodor Svedberg's ultracentrifuge (1924; Nobel Prize 1926) spins hard enough to weigh a protein molecule: the Ultracentrifuge is unlocked."),
]
