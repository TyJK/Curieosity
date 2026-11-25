"""
Curieosity canon content: substances, epochs, milestones, and the tech-tree chains.
Read by gen_authored.py, which validates it and writes the game's authored RON files.

Conventions
-----------
* A substance KEY is what equations use. Keys are formula-like where unambiguous
  ("H2O", "ZnCl2") and names where a formula would be ambiguous ("Limestone", "Tallow").
* X(...) defines a substance. `lib=True` means the id already exists in the scraped
  library (substances.ron) with its own Wikipedia-sourced description, so we only clean
  its formula/state (and name when rename=True). New substances carry desc + wiki.
* E(symbol) defines an element; elements are library entries 1000 + Z (with curated ids
  for H2, C, N2, O2 and Na).
* Equations are textbook style: "2 Hematite + 3 Charcoal -> 4 Fe + 3 CO2".
"""

from gen_authored import (Sub, R, Milestone, Epoch, MIX, HEAT, COOL, SMELT, DISTIL, ELEC,
                          LIGHT, CAT, PRESS, POLY)

SUBSTANCES = {}


def L(key, libname, formula, state, **kw):
    """A substance bound to the library entry with exactly this name (its description and
    Wikipedia link come from there). The binder resolves the id and records it."""
    LIBNAME[key] = libname
    X(key, kw.pop("name", libname), formula, state, id=kw.pop("id", 0), **kw)


LIBNAME = {}


def X(key, name, formula, state, desc=None, wiki=None, *, id, lib=False, props=(),
      color=None, smiles=None, balance=None, rename=False, stage=None):
    if key in SUBSTANCES:
        raise SystemExit(f"duplicate substance key {key}")
    SUBSTANCES[key] = Sub(key, name, formula, state, id, lib, desc, wiki, tuple(props),
                          color, smiles, balance, rename, stage)


# --------------------------------------------------------------------------------------
# Elements (library ids 1000 + Z; a few curated ids for the common molecular forms)
# --------------------------------------------------------------------------------------
_ELEMENTS = """H Hydrogen;He Helium;Li Lithium;Be Beryllium;B Boron;C Carbon;N Nitrogen;O Oxygen;
F Fluorine;Ne Neon;Na Sodium;Mg Magnesium;Al Aluminium;Si Silicon;P Phosphorus;S Sulfur;
Cl Chlorine;Ar Argon;K Potassium;Ca Calcium;Sc Scandium;Ti Titanium;V Vanadium;Cr Chromium;
Mn Manganese;Fe Iron;Co Cobalt;Ni Nickel;Cu Copper;Zn Zinc;Ga Gallium;Ge Germanium;As Arsenic;
Se Selenium;Br Bromine;Kr Krypton;Rb Rubidium;Sr Strontium;Y Yttrium;Zr Zirconium;Nb Niobium;
Mo Molybdenum;Tc Technetium;Ru Ruthenium;Rh Rhodium;Pd Palladium;Ag Silver;Cd Cadmium;
In Indium;Sn Tin;Sb Antimony;Te Tellurium;I Iodine;Xe Xenon;Cs Caesium;Ba Barium;La Lanthanum;
Ce Cerium;Pr Praseodymium;Nd Neodymium;Pm Promethium;Sm Samarium;Eu Europium;Gd Gadolinium;
Tb Terbium;Dy Dysprosium;Ho Holmium;Er Erbium;Tm Thulium;Yb Ytterbium;Lu Lutetium;Hf Hafnium;
Ta Tantalum;W Tungsten;Re Rhenium;Os Osmium;Ir Iridium;Pt Platinum;Au Gold;Hg Mercury;
Tl Thallium;Pb Lead;Bi Bismuth;Po Polonium;At Astatine;Rn Radon;Fr Francium;Ra Radium;
Ac Actinium;Th Thorium;Pa Protactinium;U Uranium;Np Neptunium;Pu Plutonium;Am Americium;Cm Curium;
Bk Berkelium;Cf Californium;Es Einsteinium;Fm Fermium;Md Mendelevium;No Nobelium;Lr Lawrencium;
Rf Rutherfordium;Db Dubnium;Sg Seaborgium;Bh Bohrium;Hs Hassium;Mt Meitnerium;Ds Darmstadtium;
Rg Roentgenium;Cn Copernicium;Nh Nihonium;Fl Flerovium;Mc Moscovium;Lv Livermorium;Ts Tennessine;
Og Oganesson"""
Z = {}
for _z, _item in enumerate(_ELEMENTS.replace("\n", "").split(";"), start=1):
    _sym, _name = _item.split()
    Z[_sym] = (_z, _name)

GASES = {"He", "Ne", "Ar", "Kr", "Xe", "Rn"}
METALS = {"Li", "Be", "Na", "Mg", "Al", "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co",
          "Ni", "Cu", "Zn", "Ga", "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd",
          "Ag", "Cd", "In", "Sn", "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd",
          "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt",
          "Au", "Hg", "Tl", "Pb", "Bi", "Po", "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu",
          "Am", "Cm"}
RADIOACTIVE = {"Tc", "Pm", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu",
               "Am", "Cm"}
SUPERHEAVY = set("Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og".split())
METALS |= SUPERHEAVY - {"Og", "Ts"}
RADIOACTIVE |= SUPERHEAVY


def E(sym):
    z, name = Z[sym]
    props = []
    if sym in METALS:
        props.append("IsMetal")
    if sym in RADIOACTIVE:
        props.append("IsRadioactive")
    state = "Gas" if sym in GASES else ("Liquid" if sym == "Hg" else "Solid")
    X(sym, name, sym, state, id=1000 + z, lib=True, props=props)


# Molecular / curated forms first.
X("H2", "Hydrogen", "H2", "Gas", "The lightest element, two protons sharing two electrons. Cavendish called it inflammable air (1766); Lavoisier named it hydrogen, 'water-former', because it burns to water.", "Hydrogen", id=1, lib=True)
X("C", "Carbon", "C", "Solid", id=3, lib=True)
X("N2", "Nitrogen", "N2", "Gas", "Four-fifths of the air, held together by one of the strongest bonds in chemistry. Breaking it to make fertilizer took Haber and Bosch until 1913.", "Nitrogen", id=4, lib=True)
X("O2", "Oxygen", "O2", "Gas", "A fifth of the air, and the gas every fire and every breath consumes. Scheele and Priestley found it independently in the 1770s; Lavoisier explained what it does.", "Oxygen", id=5, lib=True)
X("Na", "Sodium", "Na", "Solid", "A soft, silvery metal that can be cut with a knife and fizzes violently in water. Davy isolated it in 1807 by electrolysing molten caustic soda.", "Sodium", id=6, lib=True, props=["IsMetal"])
X("F2", "Fluorine", "F2", "Gas", "The most reactive element of all: a pale yellow gas that sets glass, water and even asbestos alight. It killed or injured several chemists before Moissan isolated it in 1886 by electrolysing hydrogen fluoride at -50 degrees.", "Fluorine", id=1009, lib=True)
X("Cl2", "Chlorine", "Cl2", "Gas", id=1017, lib=True)
X("Br2", "Bromine", "Br2", "Liquid", id=1035, lib=True)
X("I2", "Iodine", "I2", "Solid", id=1053, lib=True)
X("P4", "White phosphorus", "P4", "Solid", id=1015, lib=True, rename=True)
X("Hg", "Mercury", "Hg", "Liquid", "Quicksilver: the only metal that is liquid at room temperature. Alchemists roasted it out of cinnabar and believed it a root of every metal; its vapour is a slow, cumulative poison.", "Mercury_(element)", id=1080, lib=True, props=["IsMetal"])
for _sym in Z:
    if _sym not in {"H", "C", "N", "O", "Na", "F", "Cl", "Br", "I", "P", "Hg"}:
        E(_sym)

# ======================================================================================
# SUBSTANCES
# id=0 means "not yet assigned"; tools bind it to a library entry or allocate a new id.
# ======================================================================================
W = "https://en.wikipedia.org/wiki/"

# --- curated core (ids from the original seed) ---
X("H2O", "Water", "H2O", "Liquid", "The universal solvent: two hydrogens on an oxygen, bent at 104.5 degrees. It covers 71% of Earth, dissolves more substances than any other liquid, and takes part in more of the reactions in this game than anything else.", "Water", id=8, lib=True, color="#4aa8ff")
X("NaCl", "Sodium Chloride", "NaCl", "Solid", "Common salt. Once so precious it paid Roman soldiers (hence 'salary'), it is the starting point of the chlor-alkali, Leblanc and Solvay industries.", "Sodium_chloride", id=10, lib=True)
X("NH3", "Ammonia", "NH3", "Gas", "A pungent, alkaline gas: one nitrogen and three hydrogens. Fixed from the air by the Haber-Bosch process, it feeds roughly half of humanity through fertilizer.", "Ammonia", id=11, lib=True, props=["IsBase"])
X("CO2", "Carbon Dioxide", "CO2", "Gas", "Joseph Black's 'fixed air' (1754), the first gas recognised as distinct from ordinary air. The end point of every combustion of carbon, and the gas plants breathe in.", "Carbon_dioxide", id=12, lib=True)
X("(NH4)2CO3", "Ammonium Carbonate", "(NH4)2CO3", "Solid", "Sal volatile, the 'smelling salts' of fainting Victorians and the raising agent 'baker's ammonia'. It slowly gives off ammonia and carbon dioxide at room temperature.", "Ammonium_carbonate", id=13, lib=True)
X("Charcoal", "Charcoal", "C", "Solid", "Wood baked in a smothered pile until only carbon is left: light, black and porous. It burned hotter than wood and fuelled every smelter until coke replaced it.", "Charcoal", id=100, lib=True, color="#2a2420")
X("Malachite", "Malachite", "Cu2(OH)2CO3", "Solid", "A banded green copper carbonate mineral. Ground as eye paint in Egypt and smelted into the first copper around 5000 BCE.", "Malachite", id=101, lib=True, color="#1f9e5a")
X("Cassiterite", "Cassiterite", "SnO2", "Solid", "Tin stone, the chief ore of tin. Its scarcity made Bronze Age tin a prized trade good shipped across the Mediterranean from Cornwall and Afghanistan.", "Cassiterite", id=102, lib=True, color="#5a3a2a")
X("Hematite", "Hematite", "Fe2O3", "Solid", "Iron(III) oxide: the red-grey ore that colours rust, red ochre, and the surface of Mars. The most important ore of iron.", "Hematite", id=103, lib=True, color="#8b2a1a")
X("Limestone", "Limestone", "CaCO3", "Solid", "Rock made from the shells of ancient sea creatures. Burned for lime, fluxed into furnaces, and ground into cement, it is the most-used chemical raw material after water and salt.", "Limestone", id=104, lib=True, color="#d8d2c0")
X("Sand", "Sand", "SiO2", "Solid", "Quartz sand, silicon dioxide. Melted with soda and lime it becomes glass; reduced with carbon it gives silicon, the heart of every chip.", "Silicon_dioxide", id=105, lib=True, color="#e3c88a")
X("Calamine", "Calamine", "ZnCO3", "Solid", "Smithsonite, zinc carbonate. Heated with copper and charcoal it made brass long before zinc itself was isolated.", "Smithsonite", id=106, lib=True, color="#c9d8d0")
X("CaO", "Quicklime", "CaO", "Solid", "Calcium oxide, made by burning limestone. It reacts with water so violently it can boil it. Roman builders blended it dry with volcanic ash and added the water last, hot mixing, which left the self-healing lime clasts in their concrete.", "Calcium_oxide", id=107, lib=True, props=["IsBase"], color="#f4f1e8")
X("Ca(OH)2", "Slaked Lime", "Ca(OH)2", "Solid", "Calcium hydroxide. The binder in lime mortar and whitewash, and a cheap strong base used to soften water, treat sewage and make bleach.", "Calcium_hydroxide", id=108, lib=True, props=["IsBase"], color="#f8f8f4")
X("CO", "Carbon Monoxide", "CO", "Gas", "A colourless, odourless, poisonous gas from burning carbon in too little air. It is the real reducing agent inside a furnace, stripping oxygen from ores.", "Carbon_monoxide", id=109, lib=True)
X("Bronze", "Bronze", "CuSn", "Solid", "Copper hardened with about one part tin in ten. Harder and easier to cast than copper, it gave its name to an age of weapons, tools and bells.", "Bronze", id=110, lib=True, props=["IsMetal"], color="#b0782a")
X("Brass", "Brass", "CuZn", "Solid", "Copper alloyed with zinc: golden, workable and corrosion resistant. Romans made it by cementation of copper with calamine for coins and armour.", "Brass", id=111, lib=True, props=["IsMetal"], color="#d4b040")
X("Steel", "Steel", "Fe(C)", "Solid", "Iron with a fraction of a percent of carbon dissolved in it, enough to make it far harder and tougher than pure iron. Quenched and tempered, it holds an edge.", "Steel", id=200, lib=True, props=["IsMetal"], balance="Fe", color="#8a96a8")
X("Glass", "Glass", "Na2CaSi6O14", "Solid", "Soda-lime glass: sand melted with soda ash and lime. Its atoms freeze in a disordered network rather than a crystal, which is why it is transparent.", "Soda-lime_glass", id=201, lib=True, color="#bfe8f0")
X("SodaAsh", "Soda Ash", "Na2CO3", "Solid", "Sodium carbonate, once leached from plant ashes and natron. The bulk alkali of glassmaking and soapmaking; the Leblanc and Solvay processes were invented to make it.", "Sodium_carbonate", id=202, lib=True, props=["IsBase"], color="#f4f4f4")
X("Glucose", "Sugar (glucose)", "C6H12O6", "Solid", "Grape sugar, the fuel of almost every living cell. Yeast ferments it to alcohol and carbon dioxide.", "Glucose", id=203, lib=True, rename=True, color="#fff6e0")
X("Ethanol", "Ethanol", "C2H6O", "Liquid", "Drinking alcohol, made by yeast from sugar since prehistory. A solvent, a fuel, a disinfectant, and the starting point for vinegar, ether and ethylene.", "Ethanol", id=205, lib=True)
X("AcOH", "Acetic Acid", "C2H4O2", "Liquid", "The acid of vinegar, formed when bacteria oxidise wine. The first acid known to humans, and today a feedstock for plastics, solvents and aspirin.", "Acetic_acid", id=206, lib=True, props=["IsAcid"])
X("Tallow", "Tallow", "C57H110O6", "Solid", "Rendered animal fat, mostly tristearin: three stearic acid chains on a glycerol backbone. Boiled with lye, it becomes soap and glycerol.", "Tallow", id=207, lib=True, color="#f0e6c8")
X("Glycerol", "Glycerol", "C3H8O3", "Liquid", "A sweet, syrupy triple alcohol freed from fats when soap is made. Nitrated, it becomes nitroglycerin.", "Glycerol", id=209, lib=True)
X("KNO3", "Saltpeter", "KNO3", "Solid", "Potassium nitrate, scraped from cave walls and nitre beds. The oxidiser in black powder and a key source of nitric acid before the 20th century.", "Potassium_nitrate", id=210, lib=True)
X("BlackPowder", "Black Powder", "KNO3+S+C", "Solid", "Gunpowder: about 75% saltpeter, 15% charcoal and 10% sulfur, ground together. Invented in 9th-century China, it reshaped warfare and mining.", "Gunpowder", id=211, lib=True, balance="K2N2O6SC3", color="#2a2a2a")
X("H2SO4", "Sulfuric Acid", "H2SO4", "Liquid", id=300, lib=True, props=["IsAcid"])
X("HCl", "Hydrochloric Acid", "HCl", "Liquid", id=301, lib=True, props=["IsAcid"])
X("MnO2", "Manganese Dioxide", "MnO2", "Solid", "Pyrolusite, a black mineral used since cave painting. Scheele heated it with hydrochloric acid in 1774 and discovered chlorine.", "Manganese_dioxide", id=303, lib=True, color="#3a3030")
X("SO2", "Sulfur Dioxide", "SO2", "Gas", None, "Sulfur_dioxide", id=305, lib=True)
X("Na2SO4", "Sodium Sulfate", "Na2SO4", "Solid", "Glauber's 'sal mirabilis' (1625), made from salt and sulfuric acid. The Leblanc process turned it into soda ash; today it fills powdered detergents.", "Sodium_sulfate", id=306, lib=True)
X("CaS", "Calcium Sulfide", "CaS", "Solid", "The foul-smelling waste of the Leblanc process ('galligu'), heaped in mountains around 19th-century alkali works.", "Calcium_sulfide", id=307, lib=True)
X("MnCl2", "Manganese(II) Chloride", "MnCl2", "Solid", "The pink salt left over after making chlorine from pyrolusite. Walter Weldon's 1866 process recycled it back to manganese dioxide.", "Manganese(II)_chloride", id=308, lib=True, rename=True, color="#f2c8d8")
X("CaOCl2", "Bleaching Powder", "CaOCl2", "Solid", None, "Bleaching_powder", id=309, lib=True)
X("Cement", "Portland Cement", "Ca3SiO5", "Solid", None, "Portland_cement", id=310, lib=True, rename=True)
X("Battery", "Voltaic Pile", "Zn|Cu", "Solid", None, "Voltaic_pile", id=311, lib=True, rename=True, balance="ZnCu")
X("Alumina", "Alumina", "Al2O3", "Solid", "Aluminium oxide. Ruby and sapphire are alumina with traces of chromium and titanium; refined from bauxite, it is the feed of every aluminium smelter.", "Aluminium_oxide", id=330, lib=True)
X("NaOH", "Sodium Hydroxide", "NaOH", "Solid", id=331, lib=True, props=["IsBase"])
X("HNO3", "Nitric Acid", "HNO3", "Liquid", id=332, lib=True, props=["IsAcid"])
X("CoalTar", "Coal Tar", "mixture", "Liquid", None, "Coal_tar", id=335, lib=True, balance="C")
X("Benzene", "Benzene", "C6H6", "Liquid", id=336, lib=True)
X("Nitrobenzene", "Nitrobenzene", "C6H5NO2", "Liquid", None, "Nitrobenzene", id=339, lib=True)
X("Aniline", "Aniline", "C6H7N", "Liquid", id=340, lib=True, props=["IsBase"])
X("Phenol", "Phenol", "C6H6O", "Solid", id=341, lib=True, props=["IsAcid"])
X("CH2O", "Formaldehyde", "CH2O", "Gas", None, "Formaldehyde", id=342, lib=True)
X("Bakelite", "Bakelite", "(C7H6O)n", "Solid", id=343, lib=True, balance="C7H6O")
X("Ethylene", "Ethylene", "C2H4", "Gas", id=370, lib=True, props=["IsMonomer"])
X("PE", "Polyethylene", "(C2H4)n", "Solid", None, "Polyethylene", id=371, lib=True, props=["IsPolymer"], balance="C2H4")
X("Salicylic", "Salicylic Acid", "C7H6O3", "Solid", "The pain-relieving principle of willow bark, made from phenol and carbon dioxide by the Kolbe-Schmitt reaction. Too harsh on the stomach to swallow, it was tamed into aspirin.", "Salicylic_acid", id=372, lib=True, props=["IsAcid"])
X("Aspirin", "Aspirin", "C9H8O4", "Solid", id=373, lib=True, props=["IsAcid"])
X("Adipic", "Adipic Acid", "C6H10O4", "Solid", "A six-carbon diacid, made by oxidising cyclohexane. Half of the nylon-6,6 molecule; most of the world's supply goes into nylon.", "Adipic_acid", id=374, lib=True, props=["IsAcid"])
X("HMDA", "Hexamethylenediamine", "C6H16N2", "Liquid", "A six-carbon chain with an amine at each end, the other half of nylon-6,6.", "Hexamethylenediamine", id=375, lib=True, props=["IsBase"])
X("Nylon66", "Nylon 6,6", "(C12H22N2O2)n", "Solid", id=376, lib=True, rename=True, props=["IsPolymer"], balance="C12H22N2O2")

# --- Epoch 0-1 raw materials and products ---
X("Wood", "Wood", "(C6H10O5)n", "Solid", "Mostly cellulose: long chains of glucose that trees lay down as their skeleton. Humanity's first fuel; charred in a smothered pile it becomes charcoal.", "Wood", id=0, balance="C6H10O5", color="#8a5a32")
X("Clay", "Clay (kaolinite)", "Al2Si2O5(OH)4", "Solid", "Kaolinite, the fine weathering product of feldspar. Wet, it can be shaped; fired, it becomes pottery, the oldest synthetic material.", "Kaolinite", id=0, color="#c8a888")
X("Metakaolin", "Fired Clay", "Al2Si2O7", "Solid", "What kaolinite becomes above about 550 C, when its bound water is driven out: the hard, porous body of terracotta.", "Metakaolin", id=0, color="#b5603a")
X("CuO", "Copper(II) Oxide", "CuO", "Solid", "Tenorite: the black scale that forms on copper heated in air. Potters used it to colour glazes green and blue.", "Copper(II)_oxide", id=0, color="#1c1c1c")
X("Cu2O", "Copper(I) Oxide", "Cu2O", "Solid", "Cuprite, a red copper oxide. It colours red glass and is the reason old copper roofs pass through a reddish stage before turning green.", "Copper(I)_oxide", id=0, color="#a02818")
X("Galena", "Galena", "PbS", "Solid", "Lead sulfide, heavy and metallic grey, often carrying silver. The main ore of lead since antiquity; early radios used its crystals as detectors.", "Galena", id=0, color="#6a6e78")
X("PbO", "Litharge", "PbO", "Solid", "Lead(II) oxide, a yellow-orange powder. Used in glazes and crystal glass, and the oxide that cupellation skims off to free silver.", "Lead(II)_oxide", id=0, color="#e8a830")
X("Cinnabar", "Cinnabar (vermilion)", "HgS", "Solid", "Mercury sulfide: scarlet ore of mercury and, ground fine, the pigment vermilion that coloured Roman walls and Chinese lacquer.", "Cinnabar", id=0, color="#d02818")
X("Stibnite", "Stibnite", "Sb2S3", "Solid", "Antimony sulfide in long grey needles. Ancient Egyptians used it as kohl eyeliner.", "Stibnite", id=0, color="#5c6068")
X("FeS", "Iron(II) Sulfide", "FeS", "Solid", "A black solid formed when iron and sulfur are heated together. Hydrochloric or sulfuric acid on it releases rotten-egg hydrogen sulfide.", "Iron(II)_sulfide", id=0, color="#2a2420")
X("Pb3O4", "Red Lead", "Pb3O4", "Solid", "Minium, a brilliant red lead oxide: the original 'miniature' paint for manuscripts and the rust-proof primer on old ironwork.", "Lead(II,IV)_oxide", id=0, color="#e8381c")
X("Solder", "Tin-Lead Solder", "Sn3Pb", "Solid", "About two parts tin to one of lead: the mix that melts lowest of all, at 183 C, below either metal alone. Roman plumbers joined lead water pipes with tin-lead solder; electronics were soldered with it until lead-free tin, silver and copper replaced it in the 2000s.", "Solder", id=0, props=["IsMetal"], color="#b8bcc0")
X("TypeMetal", "Type Metal", "Pb6Sb2Sn", "Solid", "Lead hardened with antimony and a little tin, for casting printing type: antimony stiffens the letters so they survive the press, and keeps the metal from shrinking as it sets, so even fine serifs cast sharp.", "Type_metal", id=0, props=["IsMetal"], color="#8c9096")
X("AntimonialLead", "Antimonial Lead", "Pb12Sb", "Solid", "Hard lead: lead with a few percent of antimony, stiff enough to hold its shape. Musket balls and shot were cast from it, and the grids of lead-acid batteries still are, since pure lead would sag under its own weight.", "Lead#Alloys", id=0, props=["IsMetal"], color="#7c8088")
X("BabbittMetal", "Babbitt Metal", "Sn13SbCu", "Solid", "Isaac Babbitt's 1839 bearing metal: tin with a little antimony and copper. Hard tin-antimony crystals carry the shaft while the soft tin around them wears into a perfect bed for it.", "Babbitt_(alloy)", id=0, props=["IsMetal"], color="#c4c6c8")
X("Pewter", "Pewter", "Sn4Pb", "Solid", "A soft, silvery alloy of mostly tin. Medieval plates, tankards and spoons were pewter; modern pewter replaces the lead with antimony and copper.", "Pewter", id=0, props=["IsMetal"], color="#a8acb0")
X("EgyptianBlue", "Egyptian Blue", "CaCuSi4O10", "Solid", "Calcium copper silicate, the first synthetic pigment (around 2500 BCE). It glows in infrared, which lets archaeologists find traces of it on ancient statues.", "Egyptian_blue", id=0, color="#2850c8")
X("Goethite", "Yellow Ochre", "FeO(OH)", "Solid", "Goethite, hydrated iron oxide: the yellow-brown earth pigment of cave painters for 40,000 years, and the main ingredient of rust.", "Ochre", id=0, color="#c8962a")
X("Acanthite", "Acanthite", "Ag2S", "Solid", "Silver sulfide, the principal ore of silver; also the black tarnish that forms on silverware.", "Acanthite", id=0, color="#3a3a3e")
X("Electrum", "Electrum", "AuAg", "Solid", "A natural pale-gold alloy of gold and silver. The first coins, struck in Lydia around 600 BCE, were electrum.", "Electrum", id=0, props=["IsMetal"], color="#e0c860")
X("Gypsum", "Gypsum", "CaSO4·2H2O", "Solid", "Hydrated calcium sulfate, a soft white mineral. Gently heated it loses water and becomes plaster of Paris.", "Gypsum", id=0, color="#f2f0ea")
X("Plaster", "Plaster of Paris", "CaSO4·½H2O", "Solid", "Calcium sulfate hemihydrate. Mixed with water it re-forms interlocking gypsum crystals and sets hard within minutes: casts, mouldings, and broken-bone splints.", "Plaster", id=0, balance="Ca2S2O9H2", color="#fafaf6")
X("CaCO3", "Calcium Carbonate", "CaCO3", "Solid", id=0)
X("FeS2", "Pyrite", "FeS2", "Solid", "Fool's gold: brassy cubes of iron disulfide. Struck against flint it sparks; roasted, it was a major source of sulfuric acid.", "Pyrite", id=0, color="#c8b048")
X("Natron", "Natron", "Na2CO3·10H2O", "Solid", "Natural soda from dried salt lakes. Egyptians used it to dry mummies, wash, and make faience and the first glass.", "Natron", id=0, color="#f6f2e4")
X("Potash", "Potash", "K2CO3", "Solid", "Potassium carbonate leached from wood ashes in pots, hence the name. It gave its name to potassium.", "Potassium_carbonate", id=0, props=["IsBase"])
X("KOH", "Caustic Potash", "KOH", "Solid", None, None, id=0, props=["IsBase"])
X("SoftSoap", "Soft Soap", "C18H35KO2", "Solid", "Potassium stearate: the soft, jelly-like soap made from fat and potash lye, used for washing since Babylon.", "Soap", id=0, color="#e8dca0")
X("NaStearate", "Sodium Stearate", "C18H35NaO2", "Solid", None, None, id=0, color="#f6f0d8")
X("KCl", "Potassium Chloride", "KCl", "Solid", None, None, id=0)
X("K2S", "Potassium Sulfide", "K2S", "Solid", "The main solid left after black powder burns, together with carbonate and sulfate; the rotten-egg smell of old gun barrels.", "Potassium_sulfide", id=0)
X("CuOAc2", "Copper(II) Acetate", "C4H6CuO4", "Solid", "Verdigris, the blue-green crust that forms on copper exposed to vinegar fumes. A prized and poisonous pigment in medieval and Renaissance painting.", "Copper(II)_acetate", id=0, color="#2aa088")
X("PbCO3", "White Lead", "PbCO3", "Solid", "Lead carbonate (cerussite), the dense, opaque white of painters from Greece to the 20th century, and a slow poison to those who made it.", "Lead(II)_carbonate", id=0, color="#f8f8f0")
X("PbOAc2", "Sugar of Lead", "C4H6O4Pb", "Solid", "Lead(II) acetate. It tastes sweet; Romans boiled grape juice in lead pots to make sapa, a sweetener that slowly poisoned them.", "Lead(II)_acetate", id=0)
X("Alum", "Alum", "KAl(SO4)2·12H2O", "Solid", "Potassium alum, the classic mordant: it binds dyes to wool and cloth. Mined and traded across the ancient world.", "Potassium_alum", id=0, color="#f4f4fa")
X("BurntAlum", "Burnt Alum", "KAl(SO4)2", "Solid", "Anhydrous alum, a light powder left when alum's water of crystallisation is driven off; an astringent and styptic.", "Potassium_alum", id=0)
X("Indican", "Indican", "C14H17NO6", "Solid", "The colourless glucoside in the leaves of woad and the indigo plant. Fermented in a vat, it releases the precursor of indigo.", "Indican", id=0)
X("Indigo", "Indigo", "C16H10N2O2", "Solid", "The blue of denim and of royal robes. Once the most valuable plant dye in the world, it has been made synthetically since 1897.", "Indigo_dye", id=0, color="#203080")
X("Seawater", "Seawater", "NaCl(aq)", "Aqueous", "About 3.5% dissolved salts, mostly sodium chloride. Evaporated in pans, it gave salt to every coastal civilisation.", "Seawater", id=0, balance="NaClH2O", color="#2a78b8")
X("VolcanicAsh", "Pozzolana", "SiO2·Al2O3", "Solid", "Volcanic ash from Pozzuoli near Naples. Hot-mixed with quicklime it sets even under water, and goes on reacting for centuries: the secret of Roman concrete.", "Pozzolana", id=0, balance="SiAl2O5")
X("RomanConcrete", "Roman Concrete", "CaO·SiO2·Al2O3", "Solid", "Opus caementicium: quicklime and volcanic ash, hot-mixed and packed around rubble. Unlike modern Portland concrete it mends itself: water seeping into a crack dissolves calcium from the lime clasts, which recrystallises as calcite and seals it. In seawater its ash grows aluminous tobermorite and phillipsite, so Roman harbour walls have grown stronger for two thousand years, where modern marine concrete crumbles in decades. Modern concrete's sand and gravel are meant to stay inert, its steel reinforcement rusts and splits it from inside, and its clinker is fired at 1,450 C against about 900 C for Roman lime. Roman concrete is not as strong, but the Pantheon's unreinforced dome has stood for nineteen centuries.", "Roman_concrete", id=0, color="#b8b0a0")

# --- Epoch 2 (alchemy) ---
X("GreenVitriol", "Green Vitriol", "FeSO4·7H2O", "Solid", "Melanterite, iron(II) sulfate heptahydrate: pale green crystals that, distilled, gave alchemists 'oil of vitriol' (sulfuric acid). Also the base of iron gall ink.", "Iron(II)_sulfate", id=0, color="#8ad0a0")
X("SO3", "Sulfur Trioxide", "SO3", "Gas", id=0)
X("K2SO4", "Potassium Sulfate", "K2SO4", "Solid", "Arcanum duplicatum of the alchemists: the salt left after making aqua fortis from saltpeter. Today a chloride-free potash fertilizer.", "Potassium_sulfate", id=0)
X("HAuCl4", "Chloroauric Acid", "HAuCl4", "Solid", "Gold dissolved in aqua regia: golden-yellow crystals of tetrachloroauric acid, the starting point for gold nanoparticles and ruby glass.", "Chloroauric_acid", id=0, color="#e8c020")
X("NO", "Nitric Oxide", "NO", "Gas", id=0)
X("AgNO3", "Silver Nitrate", "AgNO3", "Solid", id=0)
X("NH4Cl", "Sal Ammoniac", "NH4Cl", "Solid", "Ammonium chloride, found around volcanic vents and first imported from Egypt near the temple of Ammon. Used in soldering, dry cells, and licorice.", "Ammonium_chloride", id=0)
X("CaCl2", "Calcium Chloride", "CaCl2", "Solid", id=0)
X("GlauberSalt", "Glauber's Salt", "Na2SO4·10H2O", "Solid", "Sodium sulfate decahydrate, Glauber's 'wonderful salt', sold as a laxative. It melts at 32 C and stores heat, so it has been tried in solar heating.", "Sodium_sulfate", id=0)
X("CuSO4", "Copper Sulfate", "CuSO4", "Solid", id=0, color="#e6ecec")
X("BlueVitriol", "Blue Vitriol", "CuSO4·5H2O", "Solid", "Copper(II) sulfate pentahydrate: vivid blue crystals. Heated, they lose their water and turn white; add water back and the blue returns.", "Copper(II)_sulfate", id=0, color="#1060e0")
X("HgO", "Mercury(II) Oxide", "HgO", "Solid", "Red calx of mercury. Priestley heated it with a burning lens in 1774 and collected a gas that made a candle burn fiercely: oxygen.", "Mercury(II)_oxide", id=0, color="#d03010")
X("HgCl2", "Corrosive Sublimate", "HgCl2", "Solid", "Mercury(II) chloride, a violent poison once used against syphilis and to preserve wood and specimens.", "Mercury(II)_chloride", id=0)
X("Hg2Cl2", "Calomel", "Hg2Cl2", "Solid", "Mercury(I) chloride, a heavy white powder taken for centuries as a purgative; today the reference standard in the calomel electrode.", "Mercury(I)_chloride", id=0)
X("MicrocosmicSalt", "Microcosmic Salt", "NaNH4HPO4·4H2O", "Solid", "Sodium ammonium phosphate, crystallised from evaporated urine. Hennig Brand boiled down 1,500 gallons of urine in 1669 hunting for the philosophers' stone.", "Sodium_ammonium_phosphate", id=0)
X("NaPO3", "Sodium Metaphosphate", "NaPO3", "Solid", "A glassy phosphate formed when microcosmic salt is fused; it dissolves metal oxides into coloured beads, a classic blowpipe test.", "Sodium_metaphosphate", id=0)
X("Na2SiO3", "Water Glass", "Na2SiO3", "Solid", "Sodium silicate, glassy yet soluble in water. Used to preserve eggs, seal engines, make silica gel, and fireproof wood.", "Sodium_silicate", id=0)
X("P4O10", "Phosphorus Pentoxide", "P4O10", "Solid", "The white smoke of burning phosphorus. It snatches water from almost anything, which makes it one of the strongest drying agents known.", "Phosphorus_pentoxide", id=0)
X("H3PO4", "Phosphoric Acid", "H3PO4", "Liquid", "A mild, non-toxic acid that gives cola its tang and fertilizer its phosphorus.", "Phosphoric_acid", id=0, props=["IsAcid"])
X("Ether", "Diethyl Ether", "C4H10O", "Liquid", id=0)
X("SnS2", "Mosaic Gold", "SnS2", "Solid", "Tin(IV) sulfide in golden flakes, an alchemists' imitation gold used to gild picture frames.", "Tin(IV)_sulfide", id=0, color="#d8a830")
X("Orpiment", "Orpiment", "As2S3", "Solid", "Arsenic sulfide, a glowing golden-yellow mineral. Painters prized it and feared it: it is deadly poisonous.", "Orpiment", id=0, color="#f0b020")
X("As2O3", "White Arsenic", "As2O3", "Solid", "Arsenic trioxide, the classic poison of history and, today, a leukemia treatment.", "Arsenic_trioxide", id=0)
X("Bismuthinite", "Bismuthinite", "Bi2S3", "Solid", "Bismuth sulfide, the chief ore of bismuth, a metal 15th-century miners confused with lead and tin.", "Bismuthinite", id=0, color="#7a7e88")
X("Bi2O3", "Bismuth Oxide", "Bi2O3", "Solid", "Bismite, a yellow oxide. Bismuth compounds settle stomachs and colour cosmetics with pearly lustre.", "Bismuth(III)_oxide", id=0, color="#f0e060")
X("Sucrose", "Sucrose", "C12H22O11", "Solid", id=0)
X("Fructose", "Fructose", "C6H12O6", "Solid", "Fruit sugar, the sweetest natural sugar. Together with glucose it makes up invert sugar and honey.", "Fructose", id=0, balance="C6H12O6")
X("ZnO", "Zinc Oxide", "ZnO", "Solid", "Philosophers' wool: the white, fluffy smoke of burning zinc. A sunscreen, a white pigment, and a catalyst for methanol synthesis.", "Zinc_oxide", id=0, color="#fafafa")
X("AgCl", "Silver Chloride", "AgCl", "Solid", "Horn silver: a white precipitate that darkens in light as silver metal forms, the observation that led to photography.", "Silver_chloride", id=0, color="#f0f0f0")
X("NaNO3", "Sodium Nitrate", "NaNO3", "Solid", id=0)

# Library names to bind by when the display name differs (used by the id binder only).
LIBNAME.update({
    "KOH": "Potassium hydroxide", "NaStearate": "Sodium stearate", "KCl": "Potassium chloride",
    "CaCO3": "Calcium carbonate", "SO3": "Sulfur trioxide", "NO": "Nitric oxide",
    "AgNO3": "Silver nitrate", "CaCl2": "Calcium chloride", "CuSO4": "Copper sulfate",
    "Ether": "Diethyl ether", "Sucrose": "Sucrose", "NaNO3": "Sodium nitrate",
})

# ======================================================================================
# EPOCHS AND CHAINS
# ======================================================================================
E0 = Epoch("Fire & Ore", "to 1200 BCE", [
    R("Charcoal Burning", "Wood -> 6 Charcoal + 5 H2O", HEAT,
      "Wood smothered under earth and slowly charred drives off its water and volatiles, leaving almost pure carbon. Charcoal burns hotter and cleaner than wood: the fuel that made metallurgy possible.",
      wiki="Charcoal", T=400, dh=-30),
    R("Burning Charcoal", "Charcoal + O2 -> CO2", HEAT,
      "Carbon burning in plenty of air: the hottest of the ancient fires, and the source of the heat in every early furnace.",
      wiki="Combustion", dh=-393.5),
    R("Smouldering Charcoal", "2 Charcoal + O2 -> 2 CO", SMELT,
      "Starved of air in a tall bloomery shaft, burning charcoal makes carbon monoxide instead of carbon dioxide. That gas, not the charcoal itself, pulls oxygen out of ore.",
      wiki="Carbon_monoxide", T=1100, dh=-221),
    R("Firing Pottery", "Clay -> Metakaolin + 2 H2O", HEAT,
      "Above about 550 C kaolinite loses its bound water for good. The clay can no longer be softened: it has become ceramic, the oldest material humans made by chemistry.",
      wiki="Pottery", T=600, dh=150),
    R("Calcination of Limestone", "Limestone -> CaO + CO2", HEAT,
      "Heating limestone drives off carbon dioxide, leaving quicklime. One of humanity's oldest chemical transformations, used since antiquity for mortar and plaster.",
      wiki="Calcination", T=900, dh=178.3),
    R("Slaking Lime", "CaO + H2O -> Ca(OH)2", MIX,
      "Water on quicklime hisses and steams as slaked lime forms, releasing enough heat to boil the water.",
      wiki="Calcium_hydroxide", dh=-65.2),
    R("Setting Lime Mortar", "Ca(OH)2 + CO2 -> CaCO3 + H2O", MIX,
      "Lime mortar hardens by slowly breathing in carbon dioxide from the air, turning back into calcium carbonate: limestone, burned and remade between the stones.",
      wiki="Lime_mortar", dh=-113),
    R("Roasting Malachite", "Malachite -> 2 CuO + CO2 + H2O", HEAT,
      "Green malachite blackens in the fire as it gives up carbon dioxide and water, leaving copper oxide ready for smelting.",
      wiki="Malachite", T=400, dh=50),
    R("Copper Smelting", "Malachite + Charcoal -> 2 Cu + 2 CO2 + H2O", HEAT,
      "Malachite roasted with charcoal frees metallic copper: humanity's first true metallurgy, beginning the Copper Age around 5000 BCE.",
      wiki="Smelting", T=1100, dh=50),
    R("Reducing Copper Oxide", "CuO + CO -> Cu + CO2", SMELT,
      "Carbon monoxide strips the oxygen from black copper oxide, leaving bright copper: the reaction actually at work inside every copper furnace.",
      wiki="Smelting", T=800, dh=-126),
    R("Tarnishing Copper", "2 Cu + O2 -> 2 CuO", HEAT,
      "Heated in air, copper grows a black skin of copper(II) oxide. Smiths learned to scale it off, and potters ground it to tint glazes.",
      wiki="Copper(II)_oxide", T=500, dh=-314),
    R("Red Copper Oxide", "4 CuO -> 2 Cu2O + O2", HEAT,
      "Above about 1000 C black copper oxide gives up some of its oxygen and turns red: cuprite, the colour of copper-ruby glass.",
      wiki="Copper(I)_oxide", T=1030, dh=290),
    R("Tin Smelting", "Cassiterite + Charcoal -> Sn + CO2", HEAT,
      "Cassiterite reduced with charcoal gives tin, a soft, low-melting metal. Nearly useless alone, it makes bronze when alloyed with copper.",
      wiki="Cassiterite", T=1100, dh=180),
    R("Zinc Smelting", "Calamine + Charcoal -> Zn + CO2 + CO", HEAT,
      "Zinc boils away as it is reduced, so it must be caught in a sealed retort. Medieval Indian metallurgists at Zawar mastered this centuries before Europe.",
      wiki="Zinc#History", T=1100, dh=230),
    R("Bronze Alloying", "Cu + Sn -> Bronze", HEAT,
      "Copper and tin melted together make bronze, harder than either. It gave its name to an age.",
      wiki="Bronze", T=1000, dh=-5),
    R("Brass Alloying", "Cu + Zn -> Brass", HEAT,
      "Copper and zinc make brass, golden and easily worked. Romans made it by cementation, heating copper with calamine and charcoal.",
      wiki="Brass", T=950, dh=-10),
    R("Iron Bloomery", "2 Hematite + 3 Charcoal -> 4 Fe + 3 CO2", SMELT,
      "In a clay bloomery the ore never melts: carbon monoxide reduces it to a spongy 'bloom' of iron and slag, hammered out by the smith. The start of the Iron Age.",
      wiki="Bloomery", T=1200, dh=467),
    R("Roasting Galena", "2 Galena + 3 O2 -> 2 PbO + 2 SO2", HEAT,
      "Roasting lead sulfide in air burns off its sulfur as choking sulfur dioxide, leaving yellow litharge.",
      wiki="Galena", T=800, dh=-830),
    R("Smelting Lead", "PbO + Charcoal -> Pb + CO", SMELT,
      "Litharge reduces easily with charcoal, giving soft, heavy lead: Roman pipes ('plumbum'), roofs and sling bullets.",
      wiki="Lead_smelting", T=800, dh=108),
    R("Roasting Cinnabar", "Cinnabar + O2 -> Hg + SO2", HEAT,
      "Heated in air, scarlet cinnabar gives up mercury vapour, which condenses to the liquid metal: quicksilver, the alchemists' favourite.",
      wiki="Mercury_(element)#Production", T=600, dh=-238),
    R("Smelting Antimony", "Stibnite + 3 Fe -> 2 Sb + 3 FeS", SMELT,
      "Iron steals the sulfur from stibnite, leaving antimony metal. The alchemists' 'regulus of antimony' grew star-shaped crystals as it cooled.",
      wiki="Antimony", T=900, dh=-80),
    R("Making Red Lead", "6 PbO + O2 -> 2 Pb3O4", HEAT,
      "Litharge roasted gently in air takes up more oxygen and turns scarlet: minium, the red of medieval manuscripts.",
      wiki="Lead(II,IV)_oxide", T=450, dh=-150),
    R("Casting Pewter", "4 Sn + Pb -> Pewter", HEAT,
      "Tin softened with a little lead casts into plates, tankards and spoons. Pewter was the tableware of everyone who could not afford silver.",
      wiki="Pewter", T=300, dh=-2),
    R("Egyptian Blue", "2 Limestone + Malachite + 8 Sand -> 2 EgyptianBlue + 3 CO2 + H2O", HEAT,
      "Lime, copper ore and sand fired together at about 850 C crystallise into calcium copper silicate: the first synthetic pigment, made in Egypt by 2500 BCE.",
      wiki="Egyptian_blue", T=850, dh=120),
    R("Burning Ochre", "2 Goethite -> Hematite + H2O", HEAT,
      "Yellow ochre turns red when heated as goethite loses water and becomes hematite. Paleolithic painters used this trick to widen their palette.",
      wiki="Ochre", T=300, dh=40),
    R("Rusting Iron", "4 Fe + 3 O2 + 2 H2O -> 4 Goethite", MIX,
      "Iron left in damp air slowly turns back into the hydrated oxide it came from: rust is just iron returning to ore.",
      wiki="Rust", dh=-1100),
    R("Smelting Silver", "Acanthite + O2 -> 2 Ag + SO2", HEAT,
      "Roasting silver sulfide burns away the sulfur and leaves the white metal behind, the source of the silver that minted the first coins.",
      wiki="Silver#Production", T=900, dh=-264),
    R("Electrum", "Au + Ag -> Electrum", HEAT,
      "Gold and silver melt together into pale-gold electrum, the metal of the first coins of Lydia.",
      wiki="Electrum", T=1050, dh=-4),
    R("Calcining Gypsum", "2 Gypsum -> Plaster + 3 H2O", HEAT,
      "Gypsum heated to about 150 C loses three-quarters of its water and becomes plaster of Paris, named for the gypsum quarries of Montmartre.",
      wiki="Plaster", T=150, dh=170),
    R("Setting Plaster", "Plaster + 3 H2O -> 2 Gypsum", MIX,
      "Wet plaster re-forms needles of gypsum that interlock and set rock-hard in minutes, warm to the touch as they grow.",
      wiki="Plaster", dh=-17),
])

E1 = Epoch("Antiquity", "1200 BCE to 500 CE", [
    R("Making Steel", "Fe + Charcoal -> Steel", SMELT,
      "Iron held hot in charcoal absorbs a little carbon and becomes steel, which can be hardened by quenching. Wootz and Damascus smiths were masters of it.",
      wiki="Steel#History", T=1200, exact=False, dh=10),
    R("Drying Natron", "Natron -> SodaAsh + 10 H2O", HEAT,
      "Natron crystals lose their water of crystallisation in gentle heat, leaving soda ash: the alkali of Egyptian glass and faience.",
      wiki="Natron", T=100, dh=150),
    R("Making Glass", "6 Sand + SodaAsh + Ca(OH)2 -> Glass + CO2 + H2O", HEAT,
      "Sand, soda and lime melt together into soda-lime glass. Mesopotamian glassmakers first managed it around 2500 BCE; Roman glassblowers made it everyday.",
      wiki="Glass#History", T=1400, dh=60),
    R("Fermentation", "Glucose -> 2 Ethanol + 2 CO2", MIX,
      "Yeast turns sugar into alcohol and carbon dioxide. Brewing and winemaking are at least 9,000 years old: the oldest biotechnology.",
      wiki="Ethanol_fermentation", T=25, dh=-67),
    R("Souring Vinegar", "Ethanol + O2 -> AcOH + H2O", MIX,
      "Acetobacter bacteria oxidise wine to vinegar. Vinegar was the first acid humans knew and the strongest they had until the alchemists.",
      wiki="Vinegar", T=25, dh=-493),
    R("Causticizing Potash", "Potash + Ca(OH)2 -> 2 KOH + CaCO3", MIX,
      "Slaked lime turns potash into caustic potash, a far stronger lye; chalk settles out.",
      wiki="Potassium_hydroxide", dh=-5),
    R("Causticizing Soda", "SodaAsh + Ca(OH)2 -> 2 NaOH + CaCO3", MIX,
      "The same lime trick turns soda ash into caustic soda. Until electrolysis, this was how lye was made.",
      wiki="Sodium_hydroxide#History", dh=-5),
    R("Boiling Soft Soap", "Tallow + 3 KOH -> 3 SoftSoap + Glycerol", HEAT,
      "Fat boiled with potash lye splits into soap and glycerol: saponification, described on Babylonian clay tablets from 2800 BCE.",
      wiki="Saponification", T=100, dh=-50),
    R("Making Hard Soap", "Tallow + 3 NaOH -> 3 NaStearate + Glycerol", HEAT,
      "With soda lye, fat gives a hard bar soap. The soapmakers of Aleppo and Castile made it with olive oil.",
      wiki="Soap#History", T=100, dh=-50),
    R("Salting Out Soap", "SoftSoap + NaCl -> NaStearate + KCl", MIX,
      "Throwing salt into the soap kettle swaps potassium for sodium, turning soft soap into hard soap that floats up as curds.",
      wiki="Salting_out", dh=0),
    R("Grinding Black Powder", "3 Charcoal + S + 2 KNO3 -> BlackPowder", MIX,
      "Saltpeter, sulfur and charcoal ground together make black powder. Chinese alchemists seeking an elixir of life found it in the 9th century.",
      wiki="Gunpowder", dh=0),
    R("Firing Black Powder", "BlackPowder -> K2S + N2 + 3 CO2", HEAT,
      "Saltpeter's oxygen burns the charcoal and sulfur in an instant, turning a pinch of solid into a large volume of hot gas.",
      wiki="Gunpowder#Chemistry", dh=-560),
    R("Growing Verdigris", "2 Cu + 4 AcOH + O2 -> 2 CuOAc2 + 2 H2O", MIX,
      "Copper hung over vinegar grows a blue-green crust of copper acetate. Pliny described the method; Renaissance painters used it for vivid greens.",
      wiki="Verdigris", dh=-300),
    R("Making White Lead", "PbO + CO2 -> PbCO3", MIX,
      "Lead oxide takes up carbon dioxide to become lead white, the opaque white of painters for 2,500 years.",
      wiki="Lead_white", dh=-88),
    R("Sugar of Lead", "PbO + 2 AcOH -> PbOAc2 + H2O", MIX,
      "Litharge dissolves in vinegar to make lead acetate, which tastes sweet. Romans sweetened wine with it.",
      wiki="Lead(II)_acetate", dh=-60),
    R("Making Vermilion", "Hg + S -> Cinnabar", MIX,
      "Mercury and sulfur ground together become red mercury sulfide: synthetic vermilion, made in China and medieval Europe.",
      wiki="Vermilion", dh=-58),
    R("Burning Alum", "Alum -> BurntAlum + 12 H2O", HEAT,
      "Alum crystals melt in their own water when heated and puff up into light, anhydrous burnt alum.",
      wiki="Potassium_alum", T=200, dh=200),
    R("Indigo Vat", "2 Indican + O2 -> Indigo + 2 Glucose", MIX,
      "Woad or indigo leaves steeped in a fermenting vat release indoxyl, which turns blue in air. Cloth dipped yellow-green comes out blue as it oxidises.",
      wiki="Indigo_dye#Natural_extraction", dh=-100),
    R("Evaporating Seawater", "Seawater -> NaCl + H2O", HEAT,
      "Sun and fire boil seawater down to salt: the oldest chemical industry on every coast.",
      wiki="Sea_salt", exact=False, dh=40),
    R("Roasting Pyrite", "4 FeS2 + 11 O2 -> 2 Hematite + 8 SO2", HEAT,
      "Fool's gold roasted in air burns to iron oxide and sulfur dioxide: a source of iron, and later of sulfuric acid.",
      wiki="Pyrite", T=600, dh=-3310),
    R("Hot-Mixed Roman Concrete", "CaO + VolcanicAsh + H2O -> RomanConcrete", MIX,
      "Hot mixing: quicklime is ground and blended dry with volcanic ash, and the water goes in last. The lime slakes in the mix itself, the heat cooks it, and white lumps of lime, lime clasts, are left through the set concrete. Admir Masic's MIT team proposed it in 2023 from a city wall at Privernum, and confirmed it in 2025 at a Pompeii building site that Vesuvius buried mid-job in 79 CE: its dry piles of premixed quicklime and ash were still waiting for water. Vitruvius had written that the lime was slaked into a paste first.",
      wiki="Roman_concrete", exact=False, dh=-65),
])

E2 = Epoch("Alchemy", "500 to 1700", [
    R("Oil of Vitriol", "2 GreenVitriol -> Hematite + SO2 + SO3 + 14 H2O", DISTIL,
      "Alchemists distilled green vitriol and collected an oily, burning liquid in the receiver: sulfuric acid, the 'oil of vitriol'.",
      wiki="Sulfuric_acid#History", T=500, dh=400),
    R("Absorbing Sulfur Trioxide", "SO3 + H2O -> H2SO4", MIX,
      "Sulfur trioxide dissolves in water with a violent release of heat to make sulfuric acid.",
      wiki="Sulfur_trioxide", dh=-132),
    R("Aqua Fortis", "2 KNO3 + H2SO4 -> K2SO4 + 2 HNO3", DISTIL,
      "Saltpeter distilled with oil of vitriol gives 'strong water', nitric acid, which dissolves silver but not gold. Glauber described the method in 1648.",
      wiki="Nitric_acid#History", T=120, dh=30),
    R("Spirit of Salt", "2 NaCl + H2SO4 -> Na2SO4 + 2 HCl", DISTIL,
      "Salt distilled with sulfuric acid gives hydrogen chloride, 'spirit of salt', and leaves Glauber's sal mirabilis behind (1625).",
      wiki="Hydrochloric_acid#History", T=150, dh=65),
    R("Dissolving Gold", "Au + HNO3 + 4 HCl -> HAuCl4 + NO + 2 H2O", MIX,
      "Aqua regia, the 'royal water' of nitric and hydrochloric acids, dissolves even gold. In 1940 George de Hevesy dissolved two Nobel medals in it to hide them from the Nazis.",
      wiki="Aqua_regia", dh=-50),
    R("Dissolving Silver", "3 Ag + 4 HNO3 -> 3 AgNO3 + NO + 2 H2O", MIX,
      "Silver dissolves in aqua fortis, leaving gold behind: the 'parting' of precious metals, and the source of lunar caustic.",
      wiki="Silver_nitrate", dh=-100),
    R("Spirit of Hartshorn", "2 NH4Cl + Ca(OH)2 -> CaCl2 + 2 NH3 + 2 H2O", HEAT,
      "Sal ammoniac warmed with lime releases ammonia gas, the pungent 'volatile alkali'. The Solvay process later recycled ammonia the same way.",
      wiki="Ammonia#History", T=100, dh=60),
    R("Crystallising Glauber's Salt", "Na2SO4 + 10 H2O -> GlauberSalt", COOL,
      "Sodium sulfate dissolved in hot water crystallises as the decahydrate on cooling: Glauber's wonderful salt.",
      wiki="Sodium_sulfate#History", T=10, dh=-80),
    R("Copper in Vitriol", "CuO + H2SO4 -> CuSO4 + H2O", MIX,
      "Black copper oxide dissolves in sulfuric acid to a sky-blue solution of copper sulfate.",
      wiki="Copper(II)_sulfate", dh=-60),
    R("Blue Vitriol Crystals", "CuSO4 + 5 H2O -> BlueVitriol", COOL,
      "Copper sulfate solution, cooled slowly, grows deep blue triclinic crystals of the pentahydrate.",
      wiki="Copper(II)_sulfate", T=10, dh=-78),
    R("Corrosive Sublimate", "HgO + 2 HCl -> HgCl2 + H2O", MIX,
      "Red mercury calx dissolves in spirit of salt to form mercury(II) chloride, which sublimes as a heavy white poison.",
      wiki="Mercury(II)_chloride", dh=-60),
    R("Calomel", "HgCl2 + Hg -> Hg2Cl2", HEAT,
      "Corrosive sublimate heated with more mercury becomes calomel, 'beautiful black' to the alchemists because it blackens with ammonia.",
      wiki="Mercury(I)_chloride", T=300, dh=-40),
    R("Fusing Microcosmic Salt", "MicrocosmicSalt -> NaPO3 + NH3 + 5 H2O", HEAT,
      "Heated, microcosmic salt gives off ammonia and steam and melts into a clear phosphate glass.",
      wiki="Sodium_ammonium_phosphate", T=400, dh=150),
    R("Brand's Phosphorus", "4 NaPO3 + 2 Sand + 10 Charcoal -> 2 Na2SiO3 + 10 CO + P4", SMELT,
      "Hennig Brand's urine residue, fired white-hot with sand and charcoal, yielded a waxy substance that glowed in the dark. Phosphorus (1669) was the first element discovered by a known person.",
      wiki="Phosphorus#History", T=1200, dh=1500),
    R("Burning Phosphorus", "P4 + 5 O2 -> P4O10", HEAT,
      "White phosphorus bursts into flame in air, giving dense white smoke of phosphorus pentoxide.",
      wiki="Phosphorus_pentoxide", dh=-2984),
    R("Phosphoric Acid", "P4O10 + 6 H2O -> 4 H3PO4", MIX,
      "Phosphorus pentoxide drinks up water greedily to make phosphoric acid.",
      wiki="Phosphoric_acid", dh=-450),
    R("Sweet Oil of Vitriol", "2 Ethanol -> Ether + H2O", DISTIL,
      "Valerius Cordus (1540) distilled alcohol with sulfuric acid and collected a sweet, volatile liquid: ether, later the first surgical anaesthetic.",
      wiki="Diethyl_ether#History", T=140, dh=-25),
    R("Mosaic Gold", "Sn + 2 S -> SnS2", HEAT,
      "Tin and sulfur heated together form glittering golden flakes of tin disulfide, an alchemical imitation of gold leaf.",
      wiki="Tin(IV)_sulfide", T=500, dh=-150),
    R("Roasting Orpiment", "2 Orpiment + 9 O2 -> 2 As2O3 + 6 SO2", HEAT,
      "Orpiment burned in air sublimes as white arsenic, the infamous 'inheritance powder'.",
      wiki="Arsenic_trioxide", T=500, dh=-1800),
    R("Isolating Arsenic", "2 As2O3 + 3 Charcoal -> 4 As + 3 CO2", SMELT,
      "Albertus Magnus is credited with isolating arsenic around 1250 by heating its oxide with charcoal; grey arsenic condenses as a metalloid.",
      wiki="Arsenic#History", T=700, dh=300),
    R("Roasting Bismuthinite", "2 Bismuthinite + 9 O2 -> 2 Bi2O3 + 6 SO2", HEAT,
      "Bismuth sulfide roasted in air gives yellow bismuth oxide.",
      wiki="Bismuthinite", T=600, dh=-1500),
    R("Smelting Bismuth", "Bi2O3 + 3 Charcoal -> 2 Bi + 3 CO", SMELT,
      "Bismuth oxide reduces readily with charcoal. Bismuth crystals cool into iridescent, stair-stepped 'hopper' shapes.",
      wiki="Bismuth#History", T=700, dh=250),
    R("Inverting Sugar", "Sucrose + H2O -> Glucose + Fructose", MIX,
      "Cane sugar splits into glucose and fructose, a sweeter syrup. Arab confectioners prized it; bees do the same to make honey.",
      wiki="Inverted_sugar_syrup", dh=-15),
    R("Philosophers' Wool", "2 Zn + O2 -> 2 ZnO", HEAT,
      "Zinc burns with a blue-green flame, throwing off white fluff the alchemists called philosophers' wool or nix alba, 'white snow'.",
      wiki="Zinc_oxide#History", dh=-700),
    R("Sal Volatile", "2 NH3 + CO2 + H2O -> (NH4)2CO3", MIX,
      "Ammonia, carbon dioxide and water combine into smelling salts, sniffed to revive the faint.",
      wiki="Ammonium_carbonate", dh=-140),
    R("Horn Silver", "AgNO3 + NaCl -> AgCl + NaNO3", MIX,
      "Salt water in silver nitrate throws down a curdy white precipitate of silver chloride. The test for chloride ever since.",
      wiki="Silver_chloride", dh=-65),
])

# --- Epoch 3 (Steam & the Chemical Revolution) ---
X("H2O2", "Hydrogen Peroxide", "H2O2", "Liquid", id=0)
X("BaCO3", "Witherite", "BaCO3", "Solid", "Barium carbonate, named for William Withering who described it in 1784 (he also introduced digitalis to medicine).", "Witherite", id=0)
X("BaO", "Baryta", "BaO", "Solid", "Barium oxide, a strong base. Heated in air it takes up extra oxygen to become the peroxide, the basis of the Brin process for oxygen.", "Barium_oxide", id=0)
X("BaO2", "Barium Peroxide", "BaO2", "Solid", "Barium peroxide: Thénard treated it with acid in 1818 and discovered hydrogen peroxide.", "Barium_peroxide", id=0)
X("BaCl2", "Barium Chloride", "BaCl2", "Solid", "A soluble barium salt that throws down white barium sulfate with any sulfate: the classic sulfate test. It colours fireworks green.", "Barium_chloride", id=0)
X("ZnSO4", "White Vitriol", "ZnSO4", "Solid", "Zinc sulfate, 'white vitriol'. Cavendish dissolved zinc in acid to make his inflammable air and left this behind.", "Zinc_sulfate", id=0)
X("FeCl2", "Iron(II) Chloride", "FeCl2", "Solid", "A pale green salt, the waste 'pickle liquor' left when steel is cleaned in hydrochloric acid.", "Iron(II)_chloride", id=0, color="#a8d8a0")
X("H2S", "Hydrogen Sulfide", "H2S", "Gas", "The rotten-egg gas. Poisonous, flammable, and the workhorse reagent of 19th-century qualitative analysis.", "Hydrogen_sulfide", id=0)
X("N2O", "Nitrous Oxide", "N2O", "Gas", id=0)
X("NH4NO3", "Ammonium Nitrate", "NH4NO3", "Solid", id=0)
X("FeCl3", "Iron(III) Chloride", "FeCl3", "Solid", "Ferric chloride: dark crystals that dissolve to a rust-brown solution. Etches copper circuit boards and clarifies drinking water.", "Iron(III)_chloride", id=0, color="#6a3810")
X("Prussiate", "Yellow Prussiate of Potash", "K4[Fe(CN)6]", "Solid", "Potassium ferrocyanide, made in the 18th century by fusing dried blood with potash and iron. Despite the cyanide groups it is not very toxic.", "Potassium_ferrocyanide", id=0, color="#f0d040")
X("PrussianBlue", "Prussian Blue", "Fe4[Fe(CN)6]3", "Solid", "Discovered by accident in Berlin around 1706: the first modern synthetic pigment, the blue of Hokusai's Great Wave and of architects' blueprints. Today it also treats radioactive caesium poisoning.", "Prussian_blue", id=0, color="#103a7a")
X("KCN", "Potassium Cyanide", "KCN", "Solid", "A deadly poison and an indispensable reagent: gold mining, electroplating, and the start of Wöhler's road to urea.", "Potassium_cyanide", id=0)
X("KOCN", "Potassium Cyanate", "KOCN", "Solid", "The cyanate ion is cyanide with one extra oxygen, and far less toxic. Liebig and Wöhler's quarrel over cyanates and fulminates gave chemistry the idea of isomers.", "Potassium_cyanate", id=0)
X("AgOCN", "Silver Cyanate", "AgOCN", "Solid", "Wöhler's starting material in 1828: same formula as Liebig's explosive silver fulminate, utterly different behaviour. Isomerism, discovered.", "Silver_cyanate", id=0)
X("NH4OCN", "Ammonium Cyanate", "NH4OCN", "Solid", "An inorganic salt that, gently heated, rearranges into urea: the experiment that began to dissolve the wall between living and non-living chemistry.", "Ammonium_cyanate", id=0)
X("Urea", "Urea", "CH4N2O", "Solid", id=0)
X("KClO", "Potassium Hypochlorite", "KClO", "Aqueous", "Eau de Javel (1789), Berthollet's chlorine bleach dissolved in potash lye: the first liquid bleach.", "Potassium_hypochlorite", id=0)
X("KClO3", "Potassium Chlorate", "KClO3", "Solid", "Berthollet's salt, a powerful oxidiser. The heads of safety matches, the oxygen in emergency candles, and the source of many accidents.", "Potassium_chlorate", id=0)
X("MgCO3", "Magnesite", "MgCO3", "Solid", "Magnesium carbonate. Black's experiments on 'magnesia alba' in 1754 led him to fixed air.", "Magnesite", id=0)
X("MgCl2", "Magnesium Chloride", "MgCl2", "Solid", id=0)
X("SrCO3", "Strontianite", "SrCO3", "Solid", "Strontium carbonate from the lead mines of Strontian, Scotland, which gave its name to the element.", "Strontianite", id=0)
X("SrCl2", "Strontium Chloride", "SrCl2", "Solid", "A salt that colours flames crimson; Davy electrolysed it to isolate strontium in 1808.", "Strontium_chloride", id=0)
X("Borax", "Borax", "Na2B4O7·10H2O", "Solid", "Tincal, from the dry lakes of Tibet and later Death Valley's twenty-mule teams. A flux for gold-smithing and the source of boron.", "Borax", id=0)
X("H3BO3", "Boric Acid", "H3BO3", "Solid", "A weak acid of boron, an antiseptic and insecticide, and the feed for boron oxide.", "Boric_acid", id=0, props=["IsAcid"])
X("B2O3", "Boron Trioxide", "B2O3", "Solid", "Glassy boron oxide, the ingredient that turns ordinary glass into heat-resistant borosilicate.", "Boron_trioxide", id=0)
X("K2O", "Potassium Oxide", "K2O", "Solid", "A pale yellow, violently basic oxide.", "Potassium_oxide", id=0)
X("NaI", "Kelp Ash", "NaI", "Solid", "Burned seaweed, rich in sodium iodide. Napoleon's saltpeter makers used it, and Bernard Courtois found iodine in the residue in 1811.", "Sodium_iodide", id=0, rename=True)
X("NaBr", "Bittern Salts", "NaBr", "Solid", "Sodium bromide from the bitter brine left after salt crystallises from seawater; Balard found bromine in it in 1826.", "Sodium_bromide", id=0)
X("CaF2", "Fluorite", "CaF2", "Solid", "Calcium fluoride: glowing violet and green crystals that gave fluorescence its name. A flux for smelting and the source of all fluorine chemistry.", "Fluorite", id=0, color="#a070e0")
X("HF", "Hydrofluoric Acid", "HF", "Liquid", "Hydrogen fluoride, the only common acid that eats glass. Scheele made it from fluorspar in 1771. It is deceptively dangerous: it seeps through skin and attacks bone.", "Hydrofluoric_acid", id=0, props=["IsAcid"])
X("H2SiF6", "Fluorosilicic Acid", "H2SiF6", "Aqueous", "Formed when hydrofluoric acid attacks silica. Today it fluoridates drinking water.", "Hexafluorosilicic_acid", id=0, props=["IsAcid"])
X("K2SiF6", "Potassium Fluorosilicate", "K2SiF6", "Solid", "The salt Berzelius reduced with potassium in 1823 to obtain the first silicon.", "Potassium_fluorosilicate", id=0)
X("KF", "Potassium Fluoride", "KF", "Solid", "Potassium fluoride, the source of fluoride ions in Moissan's electrolysis.", "Potassium_fluoride", id=0)
L("AlCl3", "Aluminum chloride", "AlCl3", "Solid", name="Aluminium Chloride", rename=True)
X("Cobaltite", "Cobaltite", "CoAsS", "Solid", "Cobalt arsenic sulfide. Miners blamed the poisonous ore on goblins, 'kobolds'; Georg Brandt showed in 1735 it held a new metal.", "Cobaltite", id=0)
X("CoO", "Cobalt(II) Oxide", "CoO", "Solid", "Cobalt oxide fused into glass makes the deep cobalt blue of Ming porcelain and medieval stained glass.", "Cobalt(II)_oxide", id=0, color="#203890")
X("Nickeline", "Nickeline", "NiAs", "Solid", "Copper-coloured nickel arsenide. Saxon miners called it Kupfernickel, 'copper demon', because it yielded no copper; Cronstedt found nickel in it in 1751.", "Nickeline", id=0)
X("NiO", "Nickel(II) Oxide", "NiO", "Solid", "Green-black nickel oxide, the feed for nickel smelting and a component of nickel batteries.", "Nickel(II)_oxide", id=0)
X("Scheelite", "Scheelite", "CaWO4", "Solid", "Calcium tungstate, which glows blue under UV. Scheele found a new acid in it in 1781; the Elhuyar brothers made tungsten from it.", "Scheelite", id=0)
X("H2WO4", "Tungstic Acid", "H2WO4", "Solid", "A yellow acid of tungsten, precipitated from scheelite with acid.", "Tungstic_acid", id=0)
X("WO3", "Tungsten Trioxide", "WO3", "Solid", "Yellow tungsten oxide, reduced with hydrogen to make tungsten powder for lamp filaments.", "Tungsten(VI)_oxide", id=0, color="#e0d040")
X("MoS2", "Molybdenite", "MoS2", "Solid", "Molybdenum disulfide, so soft and greasy it was mistaken for graphite and lead. Today a dry lubricant.", "Molybdenite", id=0)
X("MoO3", "Molybdenum Trioxide", "MoO3", "Solid", "The oxide Hjelm reduced with carbon in 1781 to obtain molybdenum.", "Molybdenum_trioxide", id=0)
X("Chromite", "Chromite", "FeCr2O4", "Solid", "Iron chromium oxide, the only ore of chromium.", "Chromite", id=0)
X("Na2CrO4", "Sodium Chromate", "Na2CrO4", "Solid", "A bright yellow salt made by roasting chromite with soda: the gateway to every chromium chemical.", "Sodium_chromate", id=0, color="#f0d000")
X("Na2Cr2O7", "Sodium Dichromate", "Na2Cr2O7", "Solid", "An orange oxidiser used to tan leather, plate chrome and, in the 1850s, by Perkin to make mauve.", "Sodium_dichromate", id=0, color="#f07010")
X("PbNO32", "Lead Nitrate", "Pb(NO3)2", "Solid", id=0)
X("PbCrO4", "Chrome Yellow", "PbCrO4", "Solid", "Lead chromate, the brilliant yellow of Van Gogh's sunflowers (1809). It darkens over time, which is why some of those sunflowers are turning brown.", "Chrome_yellow", id=0, color="#f8c800")
X("Cr2O3", "Chromium(III) Oxide", "Cr2O3", "Solid", "Chrome green, a tough, stable green pigment; the colour of banknotes and camouflage paint.", "Chromium(III)_oxide", id=0, color="#2a7a30")
X("Pitchblende", "Pitchblende", "UO2", "Solid", "Uraninite, a black, heavy uranium oxide. Klaproth found uranium in it in 1789; a century later the Curies found polonium and radium.", "Uraninite", id=0, props=["IsRadioactive"])
X("Spodumene", "Spodumene", "LiAlSi2O6", "Solid", "A lithium pyroxene in giant crystals; Arfwedson found lithium in its cousin petalite in 1817.", "Spodumene", id=0)
X("HSpodumene", "Leached Spodumene", "HAlSi2O6", "Solid", "Spodumene with its lithium swapped for hydrogen by hot sulfuric acid.", "Spodumene", id=0)
X("Li2SO4", "Lithium Sulfate", "Li2SO4", "Solid", "The soluble lithium salt leached from roasted spodumene.", "Lithium_sulfate", id=0)
X("Li2CO3", "Lithium Carbonate", "Li2CO3", "Solid", "The commodity form of lithium: battery cathodes, ceramics and, since 1949, a mood stabiliser for bipolar disorder.", "Lithium_carbonate", id=0)
X("LiCl", "Lithium Chloride", "LiCl", "Solid", "A salt so hygroscopic it pulls water from air. Electrolysed molten, it yields lithium metal (Bunsen and Matthiessen, 1855).", "Lithium_chloride", id=0)
X("Greenockite", "Cadmium Sulfide", "CdS", "Solid", "Greenockite, and the pigment cadmium yellow, beloved of Monet and Matisse.", "Cadmium_sulfide", id=0, color="#f8d018")
X("CdO", "Cadmium Oxide", "CdO", "Solid", "The brown oxide Stromeyer reduced in 1817 to discover cadmium.", "Cadmium_oxide", id=0)
X("AgI", "Silver Iodide", "AgI", "Solid", "The light-sensitive coating of Daguerre's silvered plates (1839). Today it is sprayed into clouds to seed rain.", "Silver_iodide", id=0)
X("Chloral", "Chloral", "C2HCl3O", "Liquid", "Trichloroacetaldehyde, made by Liebig in 1832 by passing chlorine through alcohol.", "Chloral", id=0)
X("CHCl3", "Chloroform", "CHCl3", "Liquid", id=0)
X("HCOONa", "Sodium Formate", "CHNaO2", "Solid", "The sodium salt of formic acid, the simplest carboxylic acid.", "Sodium_formate", id=0)
X("ChloralHydrate", "Chloral Hydrate", "C2H3Cl3O2", "Solid", "The first synthetic sleeping drug (1869), the 'knockout drops' of Victorian crime fiction.", "Chloral_hydrate", id=0)
X("Cellulose", "Cotton", "(C6H10O5)n", "Solid", "Nearly pure cellulose, the most abundant organic polymer on Earth.", "Cellulose", id=0, balance="C6H10O5", props=["IsPolymer"], color="#f8f8f4")
X("Guncotton", "Guncotton", "C6H7N3O11", "Solid", "Nitrocellulose, discovered by Schönbein in 1846 when he wiped spilled acid with his wife's cotton apron and it vanished in a flash.", "Nitrocellulose", id=0)
X("Nitroglycerin", "Nitroglycerin", "C3H5N3O9", "Liquid", id=0)
X("O3", "Ozone", "O3", "Gas", "Three-atom oxygen with a sharp electric smell, named by Schönbein in 1840 from the Greek for 'to smell'. High in the stratosphere it shields life from UV.", "Ozone", id=0, props=("IsTransient",))
X("Fe3O4", "Magnetite", "Fe3O4", "Solid", "Lodestone, naturally magnetic iron oxide: the first compass. Also the black oxide on blued steel and the iron sludge of the Béchamp reduction.", "Magnetite", id=0, color="#202020")
X("Coal", "Coal", "C", "Solid", "Fossilised plant matter, mostly carbon. The fuel of the Industrial Revolution and the source of coke, coal gas and coal tar.", "Coal", id=312, balance="C", color="#181818")
X("Coke", "Coke", "C", "Solid", "Coal baked to drive off its volatiles: nearly pure, strong, porous carbon. Abraham Darby used it in place of charcoal at Coalbrookdale in 1709, unchaining iron from the forests.", "Coke_(fuel)", id=313, color="#3a3a3a")
X("CoalGas", "Coal Gas", "H2+CH4+CO", "Gas", "Town gas: hydrogen, methane and carbon monoxide distilled from coal. It lit the streets of 19th-century cities.", "Coal_gas", id=314, balance="CH4")
X("PigIron", "Pig Iron", "Fe(C)", "Solid", "Iron straight from the blast furnace, carrying about 4% carbon: hard, brittle, and cast in sand channels that looked like piglets suckling a sow.", "Pig_iron", id=316, balance="Fe", props=["IsMetal"], color="#5a5e66")
X("Slag", "Blast-Furnace Slag", "CaSiO3", "Solid", "The molten rock that floats on iron in the furnace, carrying away the ore's sand as calcium silicate. Today it is ground into cement.", "Slag", id=0, color="#8a8478")
X("NaHCO3", "Sodium Bicarbonate", "NaHCO3", "Solid", id=0)
X("PhosphateRock", "Phosphate Rock", "Ca3(PO4)2", "Solid", "Calcium phosphate, mined from ancient seabeds or burned from bones. Almost all the phosphorus in fertilizer starts here.", "Phosphorite", id=319, color="#d8c8a8")
X("Superphosphate", "Superphosphate", "Ca(H2PO4)2", "Solid", "John Bennet Lawes patented it in 1842: phosphate rock treated with sulfuric acid so plants can take up its phosphorus. The first manufactured fertilizer.", "Superphosphate", id=320)
X("Rubber", "Natural Rubber", "(C5H8)n", "Solid", "Polyisoprene from the latex of the rubber tree. Sticky in summer and brittle in winter until Goodyear vulcanised it.", "Natural_rubber", id=321, balance="C5H8", props=["IsPolymer"], color="#c8a050")
X("VulcRubber", "Vulcanised Rubber", "(C5H8)nS", "Solid", "Rubber cross-linked by sulfur bridges: elastic in heat and cold. Goodyear stumbled on it in 1839 by dropping rubber and sulfur on a hot stove.", "Vulcanization", id=322, balance="C5H8S", props=["IsPolymer"], color="#2a2a2a")
L("CaSO4", "Calcium sulfate", "CaSO4", "Solid", name="Anhydrite", rename=True)
X("Air", "Air", "N2+O2+Ar", "Gas", "Roughly 78% nitrogen, 21% oxygen and 1% argon, with a trace of everything else. Lavoisier showed it was a mixture, not an element.", "Atmosphere_of_Earth", id=0, balance="N8O2")
X("LiquidAir", "Liquid Air", "N2+O2+Ar", "Liquid", "Air cooled to about -194 C. Carl von Linde liquefied it on an industrial scale in 1895, then separated it by distillation.", "Liquid_air", id=0, balance="N8O2", color="#a8d0ff")
X("SbCl5", "Antimony Pentachloride", "SbCl5", "Liquid", "A fuming liquid and Swarts' catalyst for swapping chlorine for fluorine, the chemistry behind the Freons.", "Antimony_pentachloride", id=0)

E3 = Epoch("Steam & Revolution", "1700 to 1850", [
    # --- coal and iron ---
    R("Coking Coal", "Coal -> Coke + CoalGas + CoalTar", HEAT,
      "Baking coal without air drives off gas and tar, leaving coke. Gas lit the cities; the tar, at first a nuisance, became the treasure chest of organic chemistry.",
      wiki="Coke_(fuel)", T=1000, exact=False, dh=50),
    R("Coke Blast Furnace", "Hematite + 3 Coke + Limestone -> 2 PigIron + 3 CO2 + Slag", SMELT,
      "Abraham Darby's coke-fired blast furnace (1709) melted iron fully for the first time in Europe. Limestone flux carries the ore's silica away as slag.",
      wiki="Blast_furnace", T=1500, exact=False, dh=500),
    R("Puddling Wrought Iron", "PigIron + O2 -> Fe + CO2", HEAT,
      "Henry Cort's puddling furnace (1784) stirred molten pig iron in air until its carbon burned out, leaving tough wrought iron for rails and ships.",
      wiki="Puddling_(metallurgy)", T=1400, exact=False, dh=-200),
    R("Portland Cement", "3 Limestone + Sand -> Cement + 3 CO2", HEAT,
      "Joseph Aspdin's 1824 patent: limestone and clay burned to clinker and ground. Named for its likeness to Portland stone, it became the binder of concrete.",
      wiki="Portland_cement", T=1450, dh=420),
    R("Vulcanising Rubber", "Rubber + S -> VulcRubber", HEAT,
      "Charles Goodyear's 1839 discovery: sulfur cross-links rubber into a tough elastic solid. Tyres, hoses and seals followed.",
      wiki="Vulcanization", T=140, dh=-20),
    # --- the gas chemists ---
    R("Black's Fixed Air", "Limestone + 2 HCl -> CaCl2 + CO2 + H2O", MIX,
      "Joseph Black (1754) showed that chalk and limestone give off a gas he called fixed air, unlike ordinary air. The first gas to be identified as a distinct substance.",
      wiki="Carbon_dioxide#History_of_discovery", dh=-15),
    R("Cavendish's Inflammable Air", "Zn + H2SO4 -> ZnSO4 + H2", MIX,
      "Henry Cavendish (1766) dissolved zinc in acid, collected the light, burnable gas that bubbled off, and weighed it: hydrogen.",
      wiki="Hydrogen#History", dh=-230),
    R("Making Mercury Calx", "2 Hg + O2 -> 2 HgO", HEAT,
      "Mercury heated for days just below boiling slowly turns into red calx, absorbing part of the air. Lavoisier used this to show combustion takes something from air.",
      wiki="Mercury(II)_oxide", T=350, dh=-181),
    R("Priestley's Oxygen", "2 HgO -> 2 Hg + O2", HEAT,
      "Joseph Priestley (1774) focused sunlight on red mercury calx and collected a gas in which a candle blazed and a mouse lived longer. Lavoisier named it oxygen.",
      wiki="Oxygen#Discovery", T=450, dh=181),
    R("Scheele's Chlorine", "MnO2 + 4 HCl -> MnCl2 + Cl2 + 2 H2O", HEAT,
      "Carl Wilhelm Scheele (1774) warmed pyrolusite with spirit of salt and got a choking yellow-green gas that bleached flowers. Davy later proved it an element: chlorine.",
      wiki="Chlorine#History", T=80, dh=-50),
    R("Rutherford's Nitrogen", "5 Air + P4 -> 20 N2 + P4O10", HEAT,
      "Daniel Rutherford (1772) burned phosphorus in a closed volume of air. What remained would not support flame or life: 'noxious air', nitrogen.",
      wiki="Nitrogen#History", dh=-2984),
    R("Hydrogen Sulfide", "FeS + 2 HCl -> FeCl2 + H2S", MIX,
      "Iron sulfide and acid release the rotten-egg gas: the reagent every Victorian analysis laboratory reeked of.",
      wiki="Hydrogen_sulfide", dh=-10),
    R("Making Ammonium Nitrate", "NH3 + HNO3 -> NH4NO3", MIX,
      "Ammonia neutralises nitric acid to ammonium nitrate, the most concentrated common nitrogen fertilizer and the oxidiser in ANFO explosive.",
      wiki="Ammonium_nitrate", dh=-146),
    R("Laughing Gas", "NH4NO3 -> N2O + 2 H2O", HEAT,
      "Gently heated ammonium nitrate gives nitrous oxide. Humphry Davy (1799) breathed it, laughed, and noted it relieved pain; dentists took 45 years to notice.",
      wiki="Nitrous_oxide#History", T=200, dh=-37),
    R("Burning Sulfur", "S + O2 -> SO2", HEAT,
      "Sulfur burns with a blue flame to choking sulfur dioxide: the first step to sulfuric acid.",
      wiki="Sulfur_dioxide", dh=-297),
    R("Lead Chamber Process", "2 SO2 + O2 + 2 H2O -> 2 H2SO4", HEAT,
      "John Roebuck (1746) burned sulfur with saltpeter inside lead-lined rooms, making sulfuric acid by the ton. Nitrogen oxides carry the oxygen.",
      wiki="Lead_chamber_process", T=60, dh=-460),
    R("Leblanc Soda", "Na2SO4 + 2 Charcoal + Limestone -> SodaAsh + CaS + 2 CO2", HEAT,
      "Nicolas Leblanc (1791) fused salt cake, coal and limestone to make soda ash from salt. The first great chemical industry, and one of the dirtiest.",
      wiki="Leblanc_process", T=1000, dh=230),
    R("Bleaching Powder", "Cl2 + Ca(OH)2 -> CaOCl2 + H2O", MIX,
      "Charles Tennant (1799) absorbed chlorine into slaked lime, making bleach a dry powder that could be shipped. Linen bleaching fell from months to days.",
      wiki="Bleaching_powder", dh=-100),
    R("Eau de Javel", "Cl2 + 2 KOH -> KCl + KClO + H2O", MIX,
      "Berthollet bubbled chlorine through cold potash lye at Javel near Paris (1789): the first liquid bleach.",
      wiki="Potassium_hypochlorite", dh=-100),
    R("Berthollet's Salt", "3 Cl2 + 6 KOH -> 5 KCl + KClO3 + 3 H2O", HEAT,
      "In hot lye, chlorine gives potassium chlorate. Berthollet hoped to replace saltpeter in gunpowder; the trial batch blew up the works.",
      wiki="Potassium_chlorate", T=80, dh=-200),
    R("Oxygen from Chlorate", "2 KClO3 -> 2 KCl + 3 O2", HEAT,
      "Heated potassium chlorate releases its oxygen: the classic school-lab source of oxygen.",
      wiki="Potassium_chlorate", T=400, dh=-89),
    R("Thénard's Peroxide: Baryta", "BaCO3 -> BaO + CO2", HEAT,
      "Witherite strongly heated gives up carbon dioxide and leaves baryta, barium oxide.",
      wiki="Barium_oxide", T=1300, dh=270),
    R("Barium Peroxide", "2 BaO + O2 -> 2 BaO2", HEAT,
      "Baryta heated in air takes up extra oxygen; heated harder it releases it again. The Brin brothers sold oxygen made this way in 1886.",
      wiki="Barium_peroxide", T=500, dh=-160),
    R("Hydrogen Peroxide", "BaO2 + 2 HCl -> BaCl2 + H2O2", MIX,
      "Louis Jacques Thénard (1818) treated barium peroxide with acid and found 'oxygenated water', hydrogen peroxide.",
      wiki="Hydrogen_peroxide#History", dh=-40),
    R("Silent Discharge Ozone", "3 O2 -> 2 O3", ELEC,
      "Christian Schönbein (1840) traced the sharp smell near electrical machines to a new form of oxygen: ozone.",
      wiki="Ozone#History", dh=285),
    R("Electrolysis of Water", "2 H2O -> 2 H2 + O2", ELEC,
      "Nicholson and Carlisle (1800) dipped wires from a fresh voltaic pile into water and watched it split into two volumes of hydrogen to one of oxygen.",
      wiki="Electrolysis_of_water", dh=572),
    R("The Voltaic Pile", "Cu + Zn + NaCl -> Battery", MIX,
      "Alessandro Volta (1800) stacked copper and zinc discs with brine-soaked cloth and got a steady electric current: the first battery.",
      wiki="Voltaic_pile", exact=False, dh=0),
    # --- Davy's elements ---
    R("Davy's Potassium", "4 KOH -> 4 K + O2 + 2 H2O", ELEC,
      "Humphry Davy (1807) passed current through molten potash and saw globules of metal shoot out and burst into lilac flame: potassium, the first metal isolated by electricity.",
      wiki="Potassium#History", T=400, dh=1100),
    R("Davy's Sodium", "4 NaOH -> 4 Na + O2 + 2 H2O", ELEC,
      "A few days after potassium, Davy electrolysed molten caustic soda for sodium.",
      wiki="Sodium#History", T=330, dh=1100),
    R("Magnesium Chloride", "MgCO3 + 2 HCl -> MgCl2 + CO2 + H2O", MIX,
      "Magnesite fizzes in hydrochloric acid, leaving magnesium chloride.",
      wiki="Magnesium_chloride", dh=-40),
    R("Davy's Magnesium", "MgCl2 -> Mg + Cl2", ELEC,
      "Electrolysis of molten magnesium chloride gives magnesium, the light metal that burns with a blinding white flame.",
      wiki="Magnesium#History", T=700, dh=641),
    R("Davy's Calcium", "CaCl2 -> Ca + Cl2", ELEC,
      "Davy (1808) isolated calcium from its chloride; it took a century before calcium metal was made in useful quantities.",
      wiki="Calcium#History", T=800, dh=796),
    R("Strontium Chloride", "SrCO3 + 2 HCl -> SrCl2 + CO2 + H2O", MIX,
      "Strontianite dissolves in acid to the chloride, which colours a flame crimson.",
      wiki="Strontium_chloride", dh=-40),
    R("Davy's Strontium", "SrCl2 -> Sr + Cl2", ELEC,
      "Davy electrolysed strontium chloride in 1808 to isolate the metal named for a Scottish village.",
      wiki="Strontium#History", T=900, dh=829),
    R("Barium Chloride", "BaCO3 + 2 HCl -> BaCl2 + CO2 + H2O", MIX,
      "Witherite dissolves in hydrochloric acid to barium chloride.",
      wiki="Barium_chloride", dh=-40),
    R("Davy's Barium", "BaCl2 -> Ba + Cl2", ELEC,
      "Barium, from the Greek barys, heavy, was isolated by Davy in 1808.",
      wiki="Barium#History", T=1000, dh=858),
    R("Boric Acid from Borax", "Borax + H2SO4 -> 4 H3BO3 + Na2SO4 + 5 H2O", MIX,
      "Sulfuric acid frees boric acid from borax; it crystallises in pearly flakes on cooling.",
      wiki="Boric_acid", dh=-10),
    R("Boron Trioxide", "2 H3BO3 -> B2O3 + 3 H2O", HEAT,
      "Boric acid heated loses water and melts into a clear glass of boron trioxide.",
      wiki="Boron_trioxide", T=300, dh=190),
    R("Isolating Boron", "B2O3 + 6 K -> 2 B + 3 K2O", SMELT,
      "Gay-Lussac and Thénard, and Davy, all reduced boric oxide with potassium in 1808, isolating boron within days of each other.",
      wiki="Boron#History", T=800, dh=-500),
    # --- halogens and silicon ---
    R("Courtois' Iodine", "2 NaI + 2 H2SO4 -> I2 + SO2 + Na2SO4 + 2 H2O", HEAT,
      "Bernard Courtois (1811) poured sulfuric acid on seaweed ash and saw clouds of violet vapour condense to black crystals: iodine.",
      wiki="Iodine#History", T=100, dh=-50),
    R("Balard's Bromine", "2 NaBr + Cl2 -> 2 NaCl + Br2", MIX,
      "Antoine Balard (1826) bubbled chlorine through bittern and a red-brown liquid separated: bromine, from the Greek for 'stench'.",
      wiki="Bromine#History", dh=-80),
    R("Scheele's Fluoric Acid", "CaF2 + H2SO4 -> CaSO4 + 2 HF", DISTIL,
      "Scheele (1771) distilled fluorspar with sulfuric acid; the fumes etched his glass retort. Hydrofluoric acid.",
      wiki="Hydrofluoric_acid#History", T=200, dh=60),
    R("Fluorosilicic Acid", "Sand + 6 HF -> H2SiF6 + 2 H2O", MIX,
      "Hydrofluoric acid attacks silica, carrying silicon away as fluorosilicic acid.",
      wiki="Hexafluorosilicic_acid", dh=-150),
    R("Potassium Fluorosilicate", "H2SiF6 + 2 KCl -> K2SiF6 + 2 HCl", MIX,
      "Potassium salts throw down sparingly soluble potassium fluorosilicate.",
      wiki="Potassium_fluorosilicate", dh=-20),
    R("Berzelius' Silicon", "K2SiF6 + 4 K -> Si + 6 KF", SMELT,
      "Jöns Jacob Berzelius (1823) reduced potassium fluorosilicate with potassium and washed out a brown powder: amorphous silicon.",
      wiki="Silicon#History", T=600, dh=-700),
    R("Ørsted's Aluminium Chloride", "Alumina + 3 Charcoal + 3 Cl2 -> 2 AlCl3 + 3 CO", HEAT,
      "Alumina heated with carbon in chlorine gives anhydrous aluminium chloride (Ørsted, 1825).",
      wiki="Aluminium_chloride", T=900, dh=-200),
    R("Wöhler's Aluminium", "AlCl3 + 3 K -> Al + 3 KCl", SMELT,
      "Friedrich Wöhler (1827) reduced aluminium chloride with potassium for grey aluminium powder. For decades aluminium was dearer than gold; Napoleon III served guests on it.",
      wiki="Aluminium#History", T=600, dh=-600),
    # --- new metals from Swedish mines ---
    R("Roasting Cobaltite", "4 Cobaltite + 9 O2 -> 4 CoO + 2 As2O3 + 4 SO2", HEAT,
      "Roasting drives off the arsenic and sulfur of cobalt ore as poisonous fumes, leaving cobalt oxide.",
      wiki="Cobaltite", T=700, dh=-2500),
    R("Brandt's Cobalt", "CoO + Charcoal -> Co + CO", SMELT,
      "Georg Brandt (1735) showed that the blue colour of cobalt glass came from a new metal, not from bismuth: cobalt, the first metal discovered since antiquity.",
      wiki="Cobalt#History", T=1000, dh=130),
    R("Roasting Nickeline", "4 Nickeline + 5 O2 -> 4 NiO + 2 As2O3", HEAT,
      "Roasting the 'copper demon' drives off its arsenic as white fumes.",
      wiki="Nickeline", T=700, dh=-1600),
    R("Cronstedt's Nickel", "NiO + Charcoal -> Ni + CO", SMELT,
      "Axel Cronstedt (1751) reduced the oxide and got a hard, white, magnetic metal: nickel.",
      wiki="Nickel#History", T=1000, dh=130),
    R("Gahn's Manganese", "MnO2 + 2 Charcoal -> Mn + 2 CO", SMELT,
      "Johan Gottlieb Gahn (1774) reduced pyrolusite with charcoal in a crucible and obtained manganese.",
      wiki="Manganese#History", T=1300, dh=300),
    R("Tungstic Acid", "Scheelite + 2 HCl -> H2WO4 + CaCl2", MIX,
      "Scheele found that acid releases a new yellow acid from 'tungsten' ('heavy stone'), now scheelite.",
      wiki="Tungstic_acid", dh=-20),
    R("Calcining Tungstic Acid", "H2WO4 -> WO3 + H2O", HEAT,
      "Tungstic acid heated loses water to the yellow trioxide.",
      wiki="Tungsten(VI)_oxide", T=400, dh=60),
    R("Elhuyar Tungsten", "WO3 + 3 H2 -> W + 3 H2O", HEAT,
      "The Elhuyar brothers (1783) reduced the oxide to the metal with the highest melting point of all, 3422 C.",
      wiki="Tungsten#History", T=900, dh=120),
    R("Roasting Molybdenite", "2 MoS2 + 7 O2 -> 2 MoO3 + 4 SO2", HEAT,
      "Molybdenite burns to white molybdenum trioxide.",
      wiki="Molybdenite", T=600, dh=-2100),
    R("Hjelm's Molybdenum", "MoO3 + 3 Charcoal -> Mo + 3 CO", SMELT,
      "Peter Hjelm (1781) reduced the oxide with carbon and linseed oil to isolate molybdenum.",
      wiki="Molybdenum#History", T=1200, dh=420),
    R("Chromate Roast", "4 Chromite + 8 SodaAsh + 7 O2 -> 8 Na2CrO4 + 2 Hematite + 8 CO2", HEAT,
      "Chromite roasted with soda ash in air turns its chromium into soluble yellow sodium chromate, still the first step in chromium chemistry.",
      wiki="Sodium_chromate", T=1100, dh=-1000),
    R("Sodium Dichromate", "2 Na2CrO4 + H2SO4 -> Na2Cr2O7 + Na2SO4 + H2O", MIX,
      "Acid turns yellow chromate into orange dichromate.",
      wiki="Sodium_dichromate", dh=-30),
    R("Chrome Yellow", "Na2CrO4 + PbNO32 -> PbCrO4 + 2 NaNO3", MIX,
      "Lead and chromate meet and a brilliant yellow precipitates: chrome yellow (1809), the colour of school buses.",
      wiki="Chrome_yellow", dh=-50),
    R("Chrome Green", "Na2Cr2O7 + 2 Charcoal -> Cr2O3 + SodaAsh + CO", HEAT,
      "Dichromate heated with carbon is reduced to green chromium(III) oxide.",
      wiki="Chromium(III)_oxide", T=800, dh=-300),
    R("Lead Nitrate", "PbO + 2 HNO3 -> PbNO32 + H2O", MIX,
      "Litharge dissolves in nitric acid to soluble lead nitrate.",
      wiki="Lead(II)_nitrate", dh=-60),
    R("Spodumene Roast", "2 Spodumene + H2SO4 -> Li2SO4 + 2 HSpodumene", HEAT,
      "Hot sulfuric acid swaps hydrogen for the lithium in spodumene, leaching lithium sulfate.",
      wiki="Spodumene", T=250, dh=-20),
    R("Lithium Carbonate", "Li2SO4 + SodaAsh -> Li2CO3 + Na2SO4", MIX,
      "Soda ash precipitates sparingly soluble lithium carbonate from the leach.",
      wiki="Lithium_carbonate", dh=-10),
    R("Lithium Chloride", "Li2CO3 + 2 HCl -> 2 LiCl + CO2 + H2O", MIX,
      "Lithium carbonate dissolves in hydrochloric acid.",
      wiki="Lithium_chloride", dh=-30),
    R("Lithium Metal", "2 LiCl -> 2 Li + Cl2", ELEC,
      "Bunsen and Matthiessen (1855) electrolysed molten lithium chloride for the lightest metal, which floats on oil.",
      wiki="Lithium#History", T=610, dh=816),
    R("Roasting Greenockite", "2 Greenockite + 3 O2 -> 2 CdO + 2 SO2", HEAT,
      "Cadmium sulfide burns to brown cadmium oxide.",
      wiki="Cadmium_oxide", T=700, dh=-800),
    R("Stromeyer's Cadmium", "CdO + Charcoal -> Cd + CO", SMELT,
      "Friedrich Stromeyer (1817) traced a yellow tint in zinc carbonate to a new metal and isolated cadmium.",
      wiki="Cadmium#History", T=800, dh=150),
    R("Wollaston's Platinum Metals", "PlatinumOre + HNO3 + 4 HCl -> Pt + Pd + Rh + Ir + Os + Ru", MIX,
      "Wollaston dissolved South American platinum in aqua regia and found palladium and rhodium in the solution (1803); Tennant found iridium and osmium in the black residue, and Karl Klaus found ruthenium in it in 1844.",
      wiki="Platinum_group#History", exact=False, dh=0),
    # --- photography and organic chemistry ---
    R("Daguerre's Plate", "2 Ag + I2 -> 2 AgI", MIX,
      "Daguerre fumed a polished silver plate with iodine vapour to make a light-sensitive silver iodide film (1839).",
      wiki="Daguerreotype", dh=-124),
    R("Exposing Silver Iodide", "2 AgI -> 2 Ag + I2", LIGHT,
      "Light splits silver iodide, leaving specks of silver that mercury vapour later developed into an image.",
      wiki="Daguerreotype#Process", dh=124),
    R("Darkening Horn Silver", "2 AgCl -> 2 Ag + Cl2", LIGHT,
      "Johann Heinrich Schulze (1717) noticed silver salts darken in sunlight, not in heat: the founding observation of photography.",
      wiki="Johann_Heinrich_Schulze", dh=254),
    R("Iron Chloride", "2 Fe + 3 Cl2 -> 2 FeCl3", HEAT,
      "Hot iron burns in chlorine to dark iron(III) chloride.",
      wiki="Iron(III)_chloride", T=300, dh=-800),
    R("Prussian Blue", "3 Prussiate + 4 FeCl3 -> PrussianBlue + 12 KCl", MIX,
      "Ferrocyanide and ferric iron combine to an intense blue. Diesbach got it by accident in Berlin around 1706 while making red lake.",
      wiki="Prussian_blue", dh=-100),
    R("Fusing Prussiate", "Prussiate -> 4 KCN + Fe3C + N2", HEAT,
      "Heating yellow prussiate breaks it into potassium cyanide, nitrogen, and iron carbide.",
      wiki="Potassium_cyanide", T=650, exact=False, dh=100),
    R("Liebig's Cyanate", "KCN + PbO -> KOCN + Pb", HEAT,
      "Fused with litharge, cyanide picks up an oxygen and becomes cyanate.",
      wiki="Potassium_cyanate", T=500, dh=-200),
    R("Silver Cyanate", "KOCN + AgNO3 -> AgOCN + KNO3", MIX,
      "Silver nitrate throws down silver cyanate, Wöhler's starting material.",
      wiki="Silver_cyanate", dh=-40),
    R("Ammonium Cyanate", "AgOCN + NH4Cl -> NH4OCN + AgCl", MIX,
      "Swapping partners with sal ammoniac gives ammonium cyanate, still a 'mineral' salt.",
      wiki="Ammonium_cyanate", dh=-30),
    R("Wöhler's Urea", "NH4OCN -> Urea", HEAT,
      "Friedrich Wöhler (1828) warmed ammonium cyanate and got crystals of urea, a substance of the kidneys, 'without the use of kidneys, either man or dog'.",
      wiki="Wöhler_synthesis", T=60, dh=-25),
    R("Liebig's Chloral", "Ethanol + 4 Cl2 -> Chloral + 5 HCl", MIX,
      "Justus von Liebig (1832) passed chlorine through alcohol for days and obtained chloral.",
      wiki="Chloral", dh=-400),
    R("Chloroform", "Chloral + NaOH -> CHCl3 + HCOONa", MIX,
      "Alkali splits chloral into chloroform, which Simpson used in 1847 to put patients to sleep.",
      wiki="Chloroform#History", dh=-60),
    R("Chloral Hydrate", "Chloral + H2O -> ChloralHydrate", MIX,
      "Chloral takes up water to form crystalline chloral hydrate, the first synthetic sleeping drug (1869).",
      wiki="Chloral_hydrate", dh=-40),
    R("Schönbein's Guncotton", "Cellulose + 3 HNO3 -> Guncotton + 3 H2O", MIX,
      "Cotton soaked in nitric acid becomes nitrocellulose, which burns without smoke. Schönbein (1846).",
      wiki="Nitrocellulose#History", dh=-150),
    R("Sobrero's Nitroglycerin", "Glycerol + 3 HNO3 -> Nitroglycerin + 3 H2O", MIX,
      "Ascanio Sobrero (1847) nitrated glycerol and nearly lost his face to the result. He kept it quiet; Nobel did not.",
      wiki="Nitroglycerin#History", dh=-200),
    R("Mitscherlich's Nitrobenzene", "Benzene + HNO3 -> Nitrobenzene + H2O", MIX,
      "Eilhard Mitscherlich (1834) nitrated benzene into an almond-scented oil, sold as 'essence of mirbane' for soap.",
      wiki="Nitrobenzene", dh=-117),
    R("Superphosphate", "PhosphateRock + 2 H2SO4 -> Superphosphate + 2 CaSO4", MIX,
      "Lawes treated phosphate rock with sulfuric acid at Deptford (1842): the first manufactured fertilizer.",
      wiki="Superphosphate", dh=-100),
    R("Liquefying Air", "Air -> LiquidAir", COOL,
      "Linde compressed air, cooled it, and let it expand through a valve over and over until it fell as a pale blue liquid.",
      wiki="Hampson-Linde_cycle", T=-194, dh=-6),
])

# --- late Epoch 3: coal tar and wood chemistry ---
L("Methanol", "Methanol", "CH4O", "Liquid")
L("Acetone", "Acetone", "C3H6O", "Liquid")
L("Toluene", "Toluene", "C7H8", "Liquid")
L("Naphthalene", "Naphthalene", "C10H8", "Solid")
L("Anthracene", "Anthracene", "C14H10", "Solid")
L("COCl2", "Phosgene", "COCl2", "Gas")
L("Fe3C", "Iron carbide (Fe3C)", "Fe3C", "Solid", name="Cementite", rename=True)
L("HBr", "Hydrogen bromide", "HBr", "Gas", props=["IsAcid"])
L("KI", "Potassium iodide", "KI", "Solid")
L("ZnNO32", "Zinc nitrate", "Zn(NO3)2", "Solid")

E3.reactions += [
    R("Distilling Wood", "Wood -> Methanol + AcOH + Acetone + Charcoal + H2O", DISTIL,
      "Heating wood in a closed retort drives off pyroligneous acid: wood spirit (methanol), wood vinegar and acetone, with charcoal left behind. Robert Boyle first collected wood spirit in 1661.",
      wiki="Destructive_distillation", T=400, exact=False, dh=100),
    R("Distilling Coal Tar", "CoalTar -> Benzene + Toluene + Phenol + Naphthalene + Anthracene + Dibenzofuran", DISTIL,
      "Fractional distillation of the black, stinking tar left by gasworks: Faraday found benzene in 1825, Runge found phenol in 1834. Every synthetic dye and drug of the next century came out of these fractions.",
      wiki="Coal_tar", T=350, exact=False, dh=50),
    R("Davy's Phosgene", "CO + Cl2 -> COCl2", LIGHT,
      "John Davy (1812) exposed carbon monoxide and chlorine to sunlight and they combined. He named the gas phosgene, 'born of light'. Today it is a key building block of polycarbonates and polyurethanes.",
      wiki="Phosgene#History", dh=-108),
]

# --- the antimony alloys: solder, type and bearings ---
E1.reactions += [
    R("Tin-Lead Solder", "3 Sn + Pb -> Solder", SMELT,
      "Tin and lead melted together run at a lower heat than either: Roman plumbers sealed the seams of lead water pipes with it.",
      wiki="Solder", T=250, dh=-2),
]
E2.reactions += [
    R("Casting Type Metal", "6 Pb + 2 Sb + Sn -> TypeMetal", HEAT,
      "Printers from Gutenberg's time on cast movable type from lead stiffened with antimony and tin: hard enough to print thousands of pages, and setting sharp in the mould.",
      wiki="Type_metal", T=350, dh=-3),
    R("Hardening Lead", "12 Pb + Sb -> AntimonialLead", HEAT,
      "A pinch of antimony stirred into molten lead makes it hard enough for shot that keeps its shape and, later, for battery grids that don't sag.",
      wiki="Lead#Alloys", T=340, dh=-2),
]
E3.reactions += [
    R("Babbitt Metal", "13 Sn + Sb + Cu -> BabbittMetal", HEAT,
      "Tin with a little antimony and copper, poured into a bearing shell: Isaac Babbitt's 1839 alloy, hard crystals in a soft bed, kept steam engines' shafts turning.",
      wiki="Babbitt_(alloy)", T=420, dh=-4),
]

# --- Epoch 4 (Second Industrial Revolution) ---
X("Oleum", "Oleum", "H2S2O7", "Liquid", "Fuming sulfuric acid: sulfur trioxide dissolved in sulfuric acid. Shipped as oleum because SO3 dissolves badly in water but readily in acid.", "Oleum", id=0, props=["IsAcid"])
L("NO2", "Nitrogen dioxide", "NO2", "Gas", color="#a04018")
X("CaC2", "Calcium Carbide", "CaC2", "Solid", "Grey lumps made in an electric arc furnace from lime and coke (Willson, 1892). Drop it in water and it fizzes out acetylene, the fuel of miners' and cyclists' lamps.", "Calcium_carbide", id=0, color="#4a4a50")
X("CaCN2", "Calcium Cyanamide", "CaCN2", "Solid", "Nitrolime, the first synthetic nitrogen fertilizer (Frank and Caro, 1898): calcium carbide heated in nitrogen. It releases ammonia slowly in moist soil.", "Calcium_cyanamide", id=0)
L("Acetylene", "Acetylene", "C2H2", "Gas")
X("Bauxite", "Bauxite", "Al(OH)3", "Solid", "A reddish laterite rich in aluminium hydroxides, named for Les Baux in Provence. Nearly all the world's aluminium starts as bauxite.", "Bauxite", id=0, color="#b0502a")
L("AlOH3", "Aluminum hydroxide", "Al(OH)3", "Solid", name="Aluminium Hydroxide", rename=True)
X("NaAlOH4", "Sodium Aluminate", "NaAl(OH)4", "Aqueous", "The hot caustic liquor of the Bayer process (1888): bauxite's alumina dissolves in it, the iron-red mud does not.", "Sodium_aluminate", id=0)
X("NiCO4", "Nickel Carbonyl", "Ni(CO)4", "Gas", "A volatile, extremely toxic nickel compound. Ludwig Mond found (1890) that carbon monoxide carries nickel away from impure metal at 50 C and drops it again, pure, at 230 C.", "Nickel_tetracarbonyl", id=0)
X("SiC", "Carborundum", "SiC", "Solid", "Silicon carbide, which Edward Acheson made in 1891 trying to make diamonds. Nearly as hard as diamond, it became the grinding wheel of the machine age.", "Silicon_carbide", id=0, color="#2a5a50")
X("Graphite", "Graphite", "C", "Solid", "Carbon in flat hexagonal sheets that slide over each other: soft, black, slippery, and electrically conductive. Acheson made it synthetically from coke in 1896.", "Graphite", id=0, color="#303034")
L("NaCN", "Sodium cyanide", "NaCN", "Solid")
X("NaAuCN2", "Sodium Dicyanoaurate", "NaAu(CN)2", "Aqueous", "Gold dissolved by cyanide and air. The MacArthur-Forrest process (1887) saved the gold fields of the Witwatersrand, whose ore was too poor to work any other way.", "Gold_cyanidation", id=0)
X("Na2ZnCN4", "Sodium Tetracyanozincate", "Na2Zn(CN)4", "Aqueous", "The spent cyanide left after zinc dust has thrown down the gold.", "Gold_cyanidation", id=0)
X("PbO2", "Lead Dioxide", "PbO2", "Solid", "Dark brown lead(IV) oxide, the positive plate of every lead-acid battery since Gaston Planté (1859).", "Lead_dioxide", id=0, color="#3a2418")
X("PbSO4", "Lead(II) Sulfate", "PbSO4", "Solid", "Anglesite, white lead sulfate. It coats both plates of a lead-acid battery as it discharges.", "Lead(II)_sulfate", id=0)
X("RaCl2", "Radium Chloride", "RaCl2", "Solid", "The salt Marie Curie concentrated from tonnes of pitchblende residue. A tenth of a gram of it, in 1902, glowed faintly blue in the dark.", "Radium_chloride", id=0, props=["IsRadioactive"])
X("Mauveine", "Mauveine", "C26H23N4", "Solid", "The first synthetic dye. William Perkin, 18 and trying to make quinine in his home lab (1856), got a black sludge that dyed silk a brilliant purple. Mauve became the colour of the decade.", "Mauveine", id=0, color="#8a2a9a")
L("Anthraquinone", "Anthraquinone", "C14H8O2", "Solid")
X("Alizarin", "Alizarin", "C14H8O4", "Solid", "The red of madder root, the dye of British redcoats. Graebe and Liebermann synthesised it from coal-tar anthracene in 1868, the first natural dye made in a factory, and the madder fields of France were ruined within a decade.", "Alizarin", id=0, color="#c82818")
X("PhthalicAnhydride", "Phthalic Anhydride", "C8H4O3", "Solid", "Made by oxidising naphthalene. A BASF worker broke a thermometer into the reaction in 1896 and the mercury turned out to be the catalyst that made synthetic indigo pay.", "Phthalic_anhydride", id=0)
L("Phthalimide", "Phthalimide", "C8H5NO2", "Solid")
L("Anthranilic", "Anthranilic acid", "C7H7NO2", "Solid")
L("ClAcOH", "Chloroacetic acid", "C2H3ClO2", "Solid", props=["IsAcid"])
L("NaClO", "Sodium hypochlorite", "NaClO", "Aqueous")
L("Camphor", "Camphor", "C10H16O", "Solid")
X("Celluloid", "Celluloid", "C6H8N2O9+C10H16O", "Solid", "Nitrocellulose plasticised with camphor (Hyatt, 1870), the first thermoplastic: billiard balls, combs, collars, and the film the cinema was born on.", "Celluloid", id=0, balance="C16H24N2O10")
L("CS2", "Carbon disulfide", "CS2", "Liquid")
X("Viscose", "Viscose", "C7H9NaO5S2", "Aqueous", "Cellulose dissolved as its xanthate in caustic soda and carbon disulfide (Cross, Bevan and Beadle, 1892): a honey-thick orange syrup.", "Viscose", id=0)
X("Rayon", "Rayon", "(C6H10O5)n", "Solid", "Viscose squirted through a spinneret into an acid bath, which turns it back into cellulose as a glossy thread: 'artificial silk'.", "Rayon", id=0, balance="C6H10O5", props=["IsPolymer"])
X("Kieselguhr", "Diatomaceous Earth", "SiO2", "Solid", "A chalky rock made of the glassy shells of diatoms. Nobel found it soaked up three times its weight of nitroglycerin and made it safe to handle.", "Diatomaceous_earth", id=0, color="#e8e4d8")
X("Dynamite", "Dynamite", "C3H5N3O9+SiO2", "Solid", "Alfred Nobel's 1867 patent: nitroglycerin absorbed into kieselguhr. It built railways and canals, and its fortune funded the Nobel Prizes.", "Dynamite", id=0, balance="C3H5N3O11Si")
L("TNT", "2,4,6-Trinitrotoluene", "C7H5N3O6", "Solid", name="TNT (trinitrotoluene)", rename=True)
L("PicricAcid", "Picric acid", "C6H3N3O7", "Solid", props=["IsAcid"])
L("Saccharin", "Saccharin", "C7H5NO3S", "Solid")
L("Eugenol", "Eugenol", "C10H12O2", "Liquid")
L("Vanillin", "Vanillin", "C8H8O3", "Solid")
L("Acetaldehyde", "Acetaldehyde", "C2H4O", "Liquid")
L("Triolein", "Triolein", "C57H104O6", "Liquid", name="Olive Oil (triolein)", rename=True)
X("Methane", "Methane", "CH4", "Gas", "The simplest hydrocarbon, one carbon and four hydrogens. Marsh gas, firedamp, and the main part of natural gas; Volta collected it bubbling up from Lake Maggiore in 1776.", "Methane", id=0)
L("Cyclohexane", "Cyclohexane", "C6H12", "Liquid")
X("AgBr", "Silver Bromide", "AgBr", "Solid", "The pale yellow, light-sensitive salt in the gelatin of photographic film and paper (Maddox, 1871). Each crystal grain that catches a few photons becomes a speck of the image.", "Silver_bromide", id=0, color="#f0eab8")
L("KBr", "Potassium bromide", "KBr", "Solid")
L("Na2S2O3", "Sodium thiosulfate", "Na2S2O3", "Solid", name="Hypo (sodium thiosulfate)", rename=True)
X("Na2SO3", "Sodium Sulfite", "Na2SO3", "Solid", "A mild reducing agent used to preserve food and wine and, in photography, to keep developer from oxidising.", "Sodium_sulfite", id=0)
X("Na3AgS2O32", "Sodium Argentothiosulfate", "Na3Ag(S2O3)2", "Aqueous", "The soluble complex that 'hypo' forms with unexposed silver bromide. Washing it away fixes a photograph: Herschel's discovery of 1819.", "Photographic_fixer", id=0)
X("BSA", "Benzenesulfonic Acid", "C6H6O3S", "Solid", "Benzene with a sulfonic acid group attached. Fused with caustic soda it gave the first synthetic phenol (1890s).", "Benzenesulfonic_acid", id=0, props=["IsAcid"])
X("Ruby", "Synthetic Ruby", "Al2O3(Cr)", "Solid", "Alumina with a trace of chromium, grown drop by drop in an oxy-hydrogen flame by Auguste Verneuil (1902). In 1960 a ruby rod became the first laser.", "Verneuil_method", id=0, balance="Al2O3", color="#c8102e")
L("Chalcopyrite", "Chalcopyrite (CuFeS2)", "CuFeS2", "Solid", name="Chalcopyrite", rename=True, color="#c8a028")
X("BlisterCopper", "Blister Copper", "Cu", "Solid", "Converter copper about 98% pure, its surface pocked with blisters where sulfur dioxide escaped as it cooled.", "Blister_copper", id=0, props=["IsMetal"], color="#b05830")
X("FeSiO3", "Iron Silicate Slag", "FeSiO3", "Solid", "The iron of copper ore, carried off as a glassy silicate slag in the converter.", "Slag", id=0, color="#2a2a2a")
X("AnodeSlime", "Anode Slime", "Ag+Au+Se+Te", "Solid", "The black mud that collects under the anodes when copper is refined electrolytically: rich in silver, gold, selenium and tellurium.", "Anode_slime", id=0, balance="AgAuSeTe")
X("CrudeOil", "Crude Oil", "mixture", "Liquid", "Petroleum: a dark mixture of hydrocarbons from ancient plankton. Edwin Drake drilled the first commercial oil well in Pennsylvania in 1859, to make kerosene for lamps.", "Petroleum", id=0, balance="C", color="#201810")
X("Gasoline", "Gasoline", "C8H18", "Liquid", "The light, volatile fraction of petroleum, at first a dangerous waste product of kerosene refining, until the motor car made it the main one.", "Gasoline", id=0, color="#f0d890")
X("Kerosene", "Kerosene", "C12H26", "Liquid", "Paraffin oil, the middle distillate of petroleum. It replaced whale oil in lamps in the 1860s, and now fuels jet aircraft.", "Kerosene", id=0)
X("Naphtha", "Naphtha", "C6H14", "Liquid", "Light distillate between gasoline and kerosene. Cracked with steam, it is the source of most of the world's ethylene and propylene.", "Naphtha", id=0)
X("Bitumen", "Bitumen", "mixture", "Solid", "The black, sticky residue left when the volatile parts of petroleum are distilled away: asphalt for roads and roofs.", "Bitumen", id=0, balance="C", color="#101010")
X("LiquidH2", "Liquid Hydrogen", "H2", "Liquid", "Hydrogen below -253 C. James Dewar liquefied it in 1898, using the vacuum flask he invented for the purpose.", "Liquid_hydrogen", id=0)
X("LiquidHe", "Liquid Helium", "He", "Liquid", "Helium below -269 C, first liquefied by Heike Kamerlingh Onnes in 1908. Cooling mercury with it, he discovered superconductivity three years later.", "Liquid_helium", id=0)
X("NH42SO4", "Ammonium Sulfate", "(NH4)2SO4", "Solid", "The fertilizer gasworks made from the ammonia in coal gas, and later the main outlet for Haber-Bosch ammonia.", "Ammonium_sulfate", id=0)
X("ThomasSlag", "Thomas Slag", "Ca3(PO4)2", "Solid", "Gilchrist and Thomas's basic lining (1878) let steelmakers burn the phosphorus out of iron ore into the slag, which farmers then bought as fertilizer.", "Gilchrist-Thomas_process", id=0, balance="Ca3P2O8")
X("StainlessSteel", "Stainless Steel", "Fe(Cr,Ni)", "Solid", "Steel with at least 10.5% chromium, which forms an invisible self-healing oxide film. Harry Brearley noticed in 1913 that his chromium gun-barrel steel would not etch.", "Stainless_steel", id=0, balance="FeCrNi", props=["IsMetal"], color="#c0c8d0")
X("HSS", "High-Speed Steel", "Fe(W,Cr)", "Solid", "Tool steel with tungsten and chromium (Taylor and White, 1900) that stays hard red-hot, letting lathes cut several times faster.", "High-speed_steel", id=0, balance="FeW", props=["IsMetal"], color="#707a88")
L("AceticAnhydride", "Acetic anhydride", "C4H6O3", "Liquid")
L("NaHSO4", "Sodium bisulfate", "NaHSO4", "Solid")

E4 = Epoch("Industry", "1850 to 1920", [
    # --- steel ---
    R("Bessemer Converter", "PigIron + O2 -> Steel + CO2", SMELT,
      "Henry Bessemer (1856) blew air through molten pig iron. The carbon burned in a roaring shower of sparks and heated the charge further: steel in twenty minutes instead of a day, at a sixth of the price.",
      wiki="Bessemer_process", T=1600, exact=False, dh=-300),
    R("Open-Hearth Steel", "PigIron + Hematite -> Steel + CO", SMELT,
      "The Siemens-Martin furnace (1865) burned the carbon out of pig iron with iron ore, slowly enough to sample and correct the melt. It made most of the world's steel for a century.",
      wiki="Open-hearth_furnace", T=1650, exact=False, dh=-100),
    R("Basic Steel", "PigIron + CaO + O2 -> Steel + ThomasSlag", SMELT,
      "Sidney Gilchrist Thomas (1878) lined the converter with limestone so it could burn phosphorus out of iron. Europe's vast phosphoric ores became usable overnight.",
      wiki="Gilchrist-Thomas_process", T=1600, exact=False, dh=-200),
    R("Stainless Steel", "Steel + Cr + Ni -> StainlessSteel", SMELT,
      "Chromium and nickel melted into steel make it rustproof: cutlery, sinks, surgical tools, the Chrysler Building's spire.",
      wiki="Stainless_steel#History", T=1600, exact=False, dh=0),
    R("High-Speed Steel", "Steel + W + Cr -> HSS", SMELT,
      "Tungsten-chromium tool steel, heat-treated close to its melting point, cut metal so fast its chips glowed blue.",
      wiki="High-speed_steel", T=1550, exact=False, dh=0),
    # --- alkali ---
    R("Solvay Tower", "NaCl + NH3 + CO2 + H2O -> NaHCO3 + NH4Cl", MIX,
      "Ernest Solvay (1861) bubbled ammonia and carbon dioxide through brine in a tall tower. Sparingly soluble baking soda drops out; no stinking waste, unlike Leblanc's.",
      wiki="Solvay_process", dh=-75),
    R("Calcining Bicarbonate", "2 NaHCO3 -> SodaAsh + CO2 + H2O", HEAT,
      "Heating the Solvay bicarbonate gives soda ash and returns half its carbon dioxide to the tower.",
      wiki="Solvay_process", T=200, dh=135),
    R("Chlor-Alkali Cell", "2 NaCl + 2 H2O -> 2 NaOH + Cl2 + H2", ELEC,
      "Castner and Kellner (1892) electrolysed brine over a flowing mercury cathode: caustic soda, chlorine and hydrogen from salt and power. Still one of the largest electrochemical industries.",
      wiki="Chloralkali_process", dh=450),
    R("Deacon Process", "4 HCl + O2 -> 2 Cl2 + 2 H2O", CAT,
      "Henry Deacon (1868) recovered chlorine from waste hydrogen chloride by passing it with air over a hot copper chloride catalyst.",
      wiki="Deacon_process", cat="Cu", T=400, dh=-114),
    R("Weldon Process", "2 MnCl2 + 2 Ca(OH)2 + O2 -> 2 MnO2 + 2 CaCl2 + 2 H2O", MIX,
      "Walter Weldon (1866) regenerated manganese dioxide from chlorine-still waste with lime and air, cutting the cost of bleach by a third.",
      wiki="Weldon_process", dh=-100),
    R("Labarraque's Solution", "Cl2 + 2 NaOH -> NaCl + NaClO + H2O", MIX,
      "Chlorine in cold caustic soda: sodium hypochlorite, household bleach and the disinfectant Labarraque used to clean Paris' morgues and hospitals.",
      wiki="Sodium_hypochlorite#History", dh=-100),
    # --- acids and nitrogen ---
    R("Contact Process", "2 SO2 + O2 -> 2 SO3", CAT,
      "Sulfur dioxide and air over hot platinum (Phillips, 1831; industrial from 1875) give sulfur trioxide directly. It made the strong acid the dye industry needed.",
      wiki="Contact_process", cat="Pt", T=450, dh=-198),
    R("Oleum", "SO3 + H2SO4 -> Oleum", MIX,
      "Sulfur trioxide is absorbed into sulfuric acid rather than water, which would make a fog of acid droplets.",
      wiki="Oleum", dh=-80),
    R("Diluting Oleum", "Oleum + H2O -> 2 H2SO4", MIX,
      "Water added carefully to oleum gives twice the sulfuric acid.",
      wiki="Oleum", dh=-100),
    R("Ostwald Process", "4 NH3 + 5 O2 -> 4 NO + 6 H2O", CAT,
      "Wilhelm Ostwald (1902) burned ammonia over a white-hot platinum gauze for a fraction of a second, making nitric oxide. Nearly all nitric acid is still made this way.",
      wiki="Ostwald_process", cat="Pt", T=850, dh=-905),
    R("Nitric Oxide Turns Brown", "2 NO + O2 -> 2 NO2", MIX,
      "Colourless nitric oxide meets air and turns into choking red-brown nitrogen dioxide.",
      wiki="Nitrogen_dioxide", dh=-114),
    R("Absorption Tower", "3 NO2 + H2O -> 2 HNO3 + NO", MIX,
      "Nitrogen dioxide dissolved in water gives nitric acid; the nitric oxide given back goes round again.",
      wiki="Ostwald_process", dh=-138),
    R("Birkeland-Eyde Arc", "N2 + O2 -> 2 NO", ELEC,
      "Kristian Birkeland (1903) spread an electric arc into a disc of flame with magnets and fixed the nitrogen of the air, using Norway's cheap hydropower.",
      wiki="Birkeland-Eyde_process", T=3000, dh=180),
    R("Haber-Bosch Synthesis", "N2 + 3 H2 -> 2 NH3", PRESS,
      "Fritz Haber (1909) and Carl Bosch (1913) combined nitrogen and hydrogen over an iron catalyst at 200 atmospheres. Bread from air: the fertilizer it makes feeds about half of humanity.",
      wiki="Haber_process", T=450, P=200, dh=-92),
    R("Calcium Carbide", "CaO + 3 Coke -> CaC2 + CO", SMELT,
      "Thomas Willson (1892) was trying to make aluminium in an arc furnace and got a grey slag that fizzed in water: calcium carbide.",
      wiki="Calcium_carbide#Production", T=2200, dh=465),
    R("Acetylene Lamp", "CaC2 + 2 H2O -> Acetylene + Ca(OH)2", MIX,
      "Water drips onto carbide and acetylene bubbles off, burning with a brilliant white flame. Miners' lamps, bicycle lamps, and lighthouses used it.",
      wiki="Carbide_lamp", dh=-128),
    R("Frank-Caro Process", "CaC2 + N2 -> CaCN2 + Graphite", HEAT,
      "Carbide heated in nitrogen at 1100 C absorbs it as calcium cyanamide, the first way to fix atmospheric nitrogen into fertilizer (1898).",
      wiki="Frank-Caro_process", T=1100, dh=-290),
    R("Cyanamide in the Soil", "CaCN2 + 3 H2O -> CaCO3 + 2 NH3", MIX,
      "In moist soil cyanamide slowly breaks down to ammonia, feeding the crop.",
      wiki="Calcium_cyanamide", dh=-90),
    R("Fertilizer from Gasworks", "2 NH3 + H2SO4 -> NH42SO4", MIX,
      "The ammonia scrubbed from coal gas was caught in sulfuric acid as ammonium sulfate fertilizer.",
      wiki="Ammonium_sulfate", dh=-270),
    R("Water Gas", "Coke + H2O -> CO + H2", HEAT,
      "Steam blown through white-hot coke gives water gas, a fuel and the cheapest source of hydrogen until natural gas.",
      wiki="Water_gas", T=1000, dh=131),
    R("Water-Gas Shift", "CO + H2O -> CO2 + H2", CAT,
      "Carbon monoxide and steam over an iron oxide catalyst (Bosch, 1915) trade the CO for more hydrogen, the feed for Haber's ammonia.",
      wiki="Water-gas_shift_reaction", cat="Fe3O4", T=400, dh=-41),
    # --- electric furnace and light metals ---
    R("Bayer Digestion", "Bauxite + NaOH -> NaAlOH4", HEAT,
      "Carl Josef Bayer (1888) dissolved bauxite in hot caustic soda; the red mud of iron oxide settles out.",
      wiki="Bayer_process", T=200, P=10, dh=-30),
    R("Bayer Precipitation", "NaAlOH4 -> AlOH3 + NaOH", COOL,
      "The cooled liquor is seeded with crystals and pure aluminium hydroxide grows out over days.",
      wiki="Bayer_process", T=50, dh=30),
    R("Calcining Alumina", "2 AlOH3 -> Alumina + 3 H2O", HEAT,
      "Aluminium hydroxide roasted at 1000 C becomes white alumina powder, ready for the smelter.",
      wiki="Bayer_process", T=1100, dh=180),
    R("Hall-Heroult Cell", "2 Alumina + 3 Coke -> 4 Al + 3 CO2", ELEC,
      "Charles Hall and Paul Heroult, both 22, both in 1886: alumina dissolved in molten cryolite and electrolysed between carbon anodes. Aluminium fell from luxury metal to pots and pans.",
      wiki="Hall-Heroult_process", T=960, dh=2200),
    R("Thermite", "Hematite + 2 Al -> 2 Fe + Alumina", HEAT,
      "Hans Goldschmidt (1893): aluminium snatches oxygen from iron oxide so violently that the iron runs white-hot. Still used to weld railway tracks in the field.",
      wiki="Thermite", T=2500, dh=-852),
    R("Aluminothermic Chromium", "Cr2O3 + 2 Al -> 2 Cr + Alumina", HEAT,
      "Goldschmidt's process makes carbon-free chromium for alloys.",
      wiki="Aluminothermic_reaction", T=2000, dh=-540),
    R("Aluminothermic Manganese", "3 MnO2 + 4 Al -> 3 Mn + 2 Alumina", HEAT,
      "The same thermite trick frees manganese from pyrolusite.",
      wiki="Aluminothermic_reaction", T=2000, dh=-1790),
    R("Acheson's Carborundum", "Sand + 3 Coke -> SiC + 2 CO", HEAT,
      "Acheson (1891) passed a huge current through clay and coke hoping for diamonds; the glittering blue-black crystals around the core were silicon carbide.",
      wiki="Silicon_carbide#History", T=2500, dh=625),
    R("Acheson Graphite", "Coke -> Graphite", HEAT,
      "Heated far beyond the carborundum temperature, carbon rearranges into graphite (Acheson, 1896): electrodes, pencils, and later reactor moderators.",
      wiki="Graphite#Synthetic_graphite", T=3000, dh=-2),
    R("Electric Furnace Phosphorus", "2 PhosphateRock + 6 Sand + 10 Coke -> P4 + 6 Slag + 10 CO", SMELT,
      "James Readman (1888) smelted phosphate rock with sand and coke in an electric furnace. Phosphorus vapour distils out; far better than boiling urine.",
      wiki="Phosphorus#Production", T=1500, dh=3000),
    R("Mond's Nickel Carbonyl", "Ni + 4 CO -> NiCO4", HEAT,
      "Carbon monoxide at 50 C picks nickel out of impure metal as a volatile gas, leaving everything else behind.",
      wiki="Mond_process", T=50, dh=-160),
    R("Mond's Pure Nickel", "NiCO4 -> Ni + 4 CO", HEAT,
      "At 230 C the carbonyl falls apart, depositing 99.99% pure nickel and releasing the carbon monoxide to go round again.",
      wiki="Mond_process", T=230, dh=160),
    R("Moissan's Fluorine", "2 HF -> H2 + F2", ELEC,
      "Henri Moissan (1886) electrolysed liquid hydrogen fluoride with potassium fluoride in a platinum apparatus at -50 C and isolated fluorine, which had injured or killed several earlier chemists. Nobel Prize, 1906.",
      wiki="Fluorine#History", T=-50, dh=546),
    R("Verneuil Ruby", "Alumina + Cr2O3 -> Ruby", HEAT,
      "Powdered alumina with a pinch of chromium oxide trickled through an oxy-hydrogen flame and built up drop by drop into a ruby boule (1902).",
      wiki="Verneuil_method", T=2050, exact=False, dh=0),
    # --- copper and precious metals ---
    R("Copper Converter", "2 Chalcopyrite + 5 O2 + 2 Sand -> 2 BlisterCopper + 2 FeSiO3 + 4 SO2", SMELT,
      "Manhes and David (1880) adapted Bessemer's converter to copper matte: air burns off the sulfur, sand takes the iron into slag.",
      wiki="Copper_extraction#Converting", T=1200, dh=-1000),
    R("Electrolytic Refining", "BlisterCopper -> Cu + AnodeSlime", ELEC,
      "Blister copper anodes dissolve into a sulfate bath and pure copper plates out on the cathodes. Electrical wiring needs 99.99% copper; this is how it gets it.",
      wiki="Copper_extraction#Electrorefining", exact=False, dh=0),
    R("Treating Anode Slime", "AnodeSlime + HNO3 -> Se + Te + Ag + Au", MIX,
      "The slime under the copper anodes is worked up for silver, gold, selenium and tellurium. Most of the world's selenium comes from here.",
      wiki="Anode_slime", exact=False, dh=0),
    R("Castner's Cyanide", "2 Na + 2 Graphite + 2 NH3 -> 2 NaCN + 3 H2", HEAT,
      "Hamilton Castner (1894) made sodium cyanide from sodium, carbon and ammonia, for the new gold fields.",
      wiki="Sodium_cyanide#Production", T=600, dh=-200),
    R("Cyanide Leaching", "GoldQuartz + NaCN + O2 + H2O -> NaAuCN2 + NaOH + Sand", MIX,
      "MacArthur and the Forrest brothers (1887): dilute cyanide and air dissolve the fine gold out of crushed ore too poor to pan or amalgamate. It made the Witwatersrand the world's great goldfield, and most gold mined today is still won this way.",
      wiki="Gold_cyanidation", exact=False, dh=-200),
    R("Zinc Dust Precipitation", "2 NaAuCN2 + Zn -> 2 Au + Na2ZnCN4", MIX,
      "Zinc dust swapped for gold in the cyanide liquor (Merrill-Crowe), throwing down a black gold sludge.",
      wiki="Merrill-Crowe_process", dh=-80),
    # --- electrochemistry ---
    R("Plante's Red Lead Plate", "Pb3O4 + 4 HNO3 -> PbO2 + 2 PbNO32 + 2 H2O", MIX,
      "Nitric acid dissolves the lead(II) out of red lead and leaves brown lead dioxide.",
      wiki="Lead_dioxide#Production", dh=-80),
    R("Lead-Acid Discharge", "Pb + PbO2 + 2 H2SO4 -> 2 PbSO4 + 2 H2O", MIX,
      "Gaston Plante (1859) found lead and lead dioxide in sulfuric acid deliver current, and can be recharged: the first rechargeable battery, still starting most cars.",
      wiki="Lead-acid_battery", dh=-315),
    R("Lead-Acid Charging", "2 PbSO4 + 2 H2O -> Pb + PbO2 + 2 H2SO4", ELEC,
      "Driving current backwards turns lead sulfate on the plates back into lead and lead dioxide.",
      wiki="Lead-acid_battery#Charging", dh=315),
    # --- radioactivity and the noble gases ---
    R("The Curies' Radium", "Pitchblende + 2 HCl -> RaCl2 + Ac + Pa", MIX,
      "Marie and Pierre Curie (1898-1902) dissolved tonnes of pitchblende residue and crystallised it thousands of times to concentrate a tenth of a gram of radium chloride. The same residues later gave up actinium (Debierne, 1899) and protactinium (Hahn and Meitner, 1917).",
      wiki="Radium#History", exact=False, dh=0),
    R("Radium Metal", "RaCl2 -> Ra + Cl2", ELEC,
      "Marie Curie and Andre-Louis Debierne electrolysed radium chloride into mercury in 1910 and distilled off the mercury: a white metal that glows and blackens in air.",
      wiki="Radium#History", dh=880),
    R("Polonium", "Pitchblende + HNO3 -> Po", MIX,
      "The Curies' first new element (July 1898), traced by its radioactivity through bismuth fractions of pitchblende and named for Marie's partitioned Poland.",
      wiki="Polonium#History", exact=False, dh=0),
    R("Helium from Cleveite", "Pitchblende + H2SO4 -> He", MIX,
      "William Ramsay (1895) treated a uranium mineral with acid and found a gas whose yellow spectral line matched one seen in the Sun in 1868: helium, until then thought to exist only there.",
      wiki="Helium#History", exact=False, dh=0),
    R("Fractionating Liquid Air", "LiquidAir -> N2 + O2 + Ar + Ne + Kr + Xe", DISTIL,
      "Ramsay and Travers (1898) let liquid air boil away fraction by fraction and found krypton ('hidden'), neon ('new') and xenon ('stranger') in a few weeks. Linde's columns now make oxygen by the tonne this way.",
      wiki="Air_separation", T=-190, exact=False, dh=0),
    R("Dewar's Liquid Hydrogen", "H2 -> LiquidH2", COOL,
      "James Dewar (1898), cooling hydrogen with liquid air and expanding it, collected 20 cc of liquid hydrogen in his double-walled vacuum flask.",
      wiki="Liquid_hydrogen#History", T=-253, dh=-1),
    R("Onnes' Liquid Helium", "He -> LiquidHe", COOL,
      "Kamerlingh Onnes (1908) precooled helium with liquid hydrogen and reached 4 degrees above absolute zero.",
      wiki="Liquid_helium#History", T=-269, dh=0),
    # --- petroleum ---
    R("Refining Crude Oil", "CrudeOil -> Gasoline + Kerosene + Naphtha + Hexadecane + Bitumen", DISTIL,
      "Benjamin Silliman (1855) showed petroleum could be distilled into lamp oil. Fractionating columns now split crude oil into fuels by boiling point.",
      wiki="Oil_refinery", T=400, exact=False, dh=0),
    R("Kerosene Lamp", "2 Kerosene + 37 O2 -> 24 CO2 + 26 H2O", HEAT,
      "Kerosene in Ignacy Lukasiewicz's lamp (1853) gave bright, cheap light and saved the whales hunted for their oil.",
      wiki="Kerosene_lamp", dh=-15000),
    # --- dyes, drugs and coal-tar chemistry ---
    R("Bechamp Reduction", "4 Nitrobenzene + 9 Fe + 4 H2O -> 4 Aniline + 3 Fe3O4", HEAT,
      "Antoine Bechamp (1854) reduced nitrobenzene with iron filings and acid, making aniline cheaply enough for a dye industry.",
      wiki="Bechamp_reduction", T=100, dh=-2000),
    R("Perkin's Mauve", "Aniline + Na2Cr2O7 -> Mauveine", MIX,
      "Perkin oxidised impure aniline with dichromate and extracted a purple dye with alcohol (1856). He left school, built a factory, and retired rich at 36.",
      wiki="Mauveine#History", exact=False, dh=0),
    R("Oxidising Anthracene", "2 Anthracene + 3 O2 -> 2 Anthraquinone + 2 H2O", HEAT,
      "Anthracene from coal tar oxidises to yellow anthraquinone.",
      wiki="Anthraquinone#Synthesis", T=300, dh=-500),
    R("Synthetic Alizarin", "Anthraquinone + O2 -> Alizarin", HEAT,
      "Sulfonated anthraquinone fused with caustic soda gives alizarin (Graebe, Liebermann and Perkin, 1869). Germany and Perkin patented it within a day of each other.",
      wiki="Alizarin#History", T=200, dh=-200),
    R("Phthalic Anhydride", "2 Naphthalene + 9 O2 -> 2 PhthalicAnhydride + 4 CO2 + 4 H2O", CAT,
      "Naphthalene oxidised in hot sulfuric acid, catalysed by the mercury from a broken thermometer (BASF, 1896).",
      wiki="Phthalic_anhydride#Production", cat="Hg", T=300, dh=-1800),
    R("Phthalimide", "PhthalicAnhydride + NH3 -> Phthalimide + H2O", HEAT,
      "Phthalic anhydride and ammonia close into phthalimide.",
      wiki="Phthalimide", T=250, dh=-100),
    R("Hofmann Rearrangement", "Phthalimide + NaClO + 2 NaOH -> Anthranilic + NaCl + SodaAsh", MIX,
      "Hypochlorite and alkali snip a carbon out of phthalimide, leaving anthranilic acid (Hofmann, 1881).",
      wiki="Hofmann_rearrangement", dh=-200),
    R("Chloroacetic Acid", "AcOH + Cl2 -> ClAcOH + HCl", LIGHT,
      "Chlorine replaces one hydrogen of acetic acid under light, giving chloroacetic acid.",
      wiki="Chloroacetic_acid", dh=-100),
    R("BASF Indigo", "2 Anthranilic + 2 ClAcOH + O2 -> Indigo + 2 CO2 + 2 HCl + 4 H2O", HEAT,
      "Heumann's route, run by BASF from 1897 after seventeen years and 18 million marks: synthetic indigo. Within fifteen years India's indigo plantations had collapsed.",
      wiki="Indigo_dye#Chemical_synthesis", T=200, dh=-400),
    R("Kolbe-Schmitt Reaction", "Phenol + CO2 -> Salicylic", PRESS,
      "Hermann Kolbe (1860), improved by Rudolf Schmitt (1885): sodium phenoxide and carbon dioxide under pressure give salicylic acid, the willow-bark painkiller, by the tonne.",
      wiki="Kolbe-Schmitt_reaction", T=125, P=100, dh=-50),
    R("Acetic Anhydride", "2 AcOH -> AceticAnhydride + H2O", DISTIL,
      "Two molecules of acetic acid, dehydrated, give the anhydride: a powerful acetylating agent.",
      wiki="Acetic_anhydride", T=700, dh=60),
    R("Hoffmann's Aspirin", "Salicylic + AceticAnhydride -> Aspirin + AcOH", MIX,
      "Felix Hoffmann at Bayer (1897) acetylated salicylic acid, taming its harshness on the stomach. Aspirin is still taken by the billion tablets.",
      wiki="Aspirin#History", T=90, dh=-30),
    R("Bakelite", "Phenol + CH2O -> Bakelite + H2O", POLY,
      "Leo Baekeland (1907) cooked phenol with formaldehyde under pressure into a hard, mouldable resin that would not melt: the first fully synthetic plastic.",
      wiki="Bakelite", T=150, dh=-100),
    R("Formaldehyde", "2 Methanol + O2 -> 2 CH2O + 2 H2O", CAT,
      "August Wilhelm von Hofmann (1867) passed methanol vapour and air over a hot metal spiral and made formaldehyde, the pungent gas of embalming fluid and of Bakelite. Industry uses a silver catalyst.",
      wiki="Formaldehyde#Production", cat="Ag", T=650, dh=-310),
    R("Carbon Disulfide", "Charcoal + 2 S -> CS2", HEAT,
      "Sulfur vapour over red-hot charcoal gives volatile, foul-smelling carbon disulfide, the solvent of rubber and viscose.",
      wiki="Carbon_disulfide#Production", T=850, dh=117),
    R("Viscose", "Cellulose + NaOH + CS2 -> Viscose + H2O", MIX,
      "Cellulose soaked in caustic soda and treated with carbon disulfide dissolves into viscose (1892).",
      wiki="Viscose", dh=-50),
    R("Spinning Rayon", "Viscose + H2SO4 -> Rayon + CS2 + NaHSO4", MIX,
      "Viscose forced through a spinneret into acid regenerates cellulose as shining artificial silk.",
      wiki="Rayon#Viscose", exact=False, dh=-50),
    R("Celluloid", "Guncotton + Camphor -> Celluloid", MIX,
      "John Wesley Hyatt (1870), chasing a prize for a substitute for ivory billiard balls, kneaded nitrocellulose with camphor into the first commercial plastic.",
      wiki="Celluloid", exact=False, dh=0),
    R("Nobel's Dynamite", "Nitroglycerin + Kieselguhr -> Dynamite", MIX,
      "After his brother died in a nitroglycerin explosion, Alfred Nobel (1867) found that diatomaceous earth soaked it up into a stable paste.",
      wiki="Dynamite#History", dh=0),
    R("Wilbrand's TNT", "Toluene + 3 HNO3 -> TNT + 3 H2O", HEAT,
      "Julius Wilbrand (1863) nitrated toluene to a yellow dye. It was thirty years before anyone noticed it could be made to explode, and it was hard to set off, which made it safe to fill shells with.",
      wiki="TNT#History", T=100, dh=-200),
    R("Picric Acid", "Phenol + 3 HNO3 -> PicricAcid + 3 H2O", MIX,
      "Triply nitrated phenol: a yellow dye for silk (1849), an antiseptic for burns, and lyddite for shells.",
      wiki="Picric_acid", dh=-250),
    R("Fahlberg's Saccharin", "2 Toluene + 2 H2SO4 + 2 NH3 + 3 O2 -> 2 Saccharin + 8 H2O", MIX,
      "Constantin Fahlberg (1879) forgot to wash his hands after work on coal-tar derivatives and found his bread tasted sweet: the first artificial sweetener.",
      wiki="Saccharin#History", exact=True, dh=-500),
    R("Vanillin from Cloves", "Eugenol + O2 -> Vanillin + Acetaldehyde", HEAT,
      "Clove oil's eugenol, isomerised and oxidised, gives vanillin (Tiemann and Haarmann, 1870s): the first synthetic flavour.",
      wiki="Vanillin#History", T=100, dh=-200),
    R("Sabatier Hydrogenation", "Triolein + 3 H2 -> Tallow", CAT,
      "Paul Sabatier (1897) found finely divided nickel adds hydrogen to unsaturated molecules; Wilhelm Normann (1901) used it to harden oils into margarine and soap fats.",
      wiki="Hydrogenation#History", cat="Ni", T=180, dh=-360),
    R("Sabatier Reaction", "CO2 + 4 H2 -> Methane + 2 H2O", CAT,
      "Carbon dioxide and hydrogen over nickel make methane and water. The International Space Station recycles its astronauts' breath this way.",
      wiki="Sabatier_reaction", cat="Ni", T=350, dh=-165),
    R("Hydrogenating Benzene", "Benzene + 3 H2 -> Cyclohexane", PRESS,
      "Sabatier and Senderens (1901) saturated benzene's ring with hydrogen. Cyclohexane is now the first step to nylon.",
      wiki="Cyclohexane#Production", T=200, P=30, dh=-206),
    R("Sulfonating Benzene", "Benzene + H2SO4 -> BSA + H2O", HEAT,
      "Hot concentrated sulfuric acid attaches a sulfonic acid group to benzene.",
      wiki="Benzenesulfonic_acid", T=100, dh=-50),
    R("Phenol by Fusion", "BSA + 2 NaOH -> Phenol + Na2SO3 + H2O", HEAT,
      "Sodium benzenesulfonate fused with caustic soda gives phenol: how phenol was made for the explosive and plastic industries before 1950.",
      wiki="Phenol#Production", T=330, dh=-100),
    # --- photography ---
    R("Gelatin Silver Bromide", "AgNO3 + KBr -> AgBr + KNO3", MIX,
      "Silver nitrate and potassium bromide mixed in warm gelatin precipitate fine silver bromide grains: Maddox's dry plate (1871), and every roll of film since.",
      wiki="Silver_bromide", dh=-80),
    R("Exposing the Plate", "2 AgBr -> 2 Ag + Br2", LIGHT,
      "Light frees specks of silver in the bromide grains, a latent image a developer can grow into a picture.",
      wiki="Latent_image", dh=200),
    R("Sodium Sulfite", "SO2 + 2 NaOH -> Na2SO3 + H2O", MIX,
      "Sulfur dioxide absorbed into caustic soda gives sodium sulfite.",
      wiki="Sodium_sulfite", dh=-160),
    R("Making Hypo", "Na2SO3 + S -> Na2S2O3", HEAT,
      "Sodium sulfite boiled with sulfur takes up another sulfur atom as thiosulfate, photographers' 'hypo'.",
      wiki="Sodium_thiosulfate#Production", T=100, dh=-20),
    R("Fixing the Image", "AgBr + 2 Na2S2O3 -> Na3AgS2O32 + NaBr", MIX,
      "John Herschel (1819) found hypo dissolves silver salts. Washing out the unexposed bromide makes the picture permanent.",
      wiki="Photographic_fixer", dh=-60),
])

# --- Epoch 5 (the Modern age: oil, plastics, drugs, the atom) ---
X("Octane", "n-Octane", "C8H18", "Liquid", "A straight eight-carbon alkane, a typical molecule of gasoline. Fischer and Tropsch made fuels like it from coal gas in the 1920s.", "Octane", id=0)
X("Hexadecane", "Hexadecane", "C16H34", "Liquid", "Cetane, a sixteen-carbon alkane: the reference fuel for diesel ignition quality and a typical molecule of heavy gas oil.", "Hexadecane", id=0)
X("Octene", "1-Octene", "C8H16", "Liquid", "An eight-carbon alkene. Cracking heavy oil gives a gasoline rich in alkenes like it, which knock less than straight alkanes.", "1-Octene", id=0)
X("NaturalGas", "Natural Gas", "CH4+C2H6+C3H8", "Gas", "Mostly methane, with ethane, propane and butane. Once flared off as a nuisance at oil wells, it now heats homes and feeds the chemical industry.", "Natural_gas", id=0, balance="C")
X("Ethane", "Ethane", "C2H6", "Gas", "The two-carbon alkane. Steam cracked, it gives ethylene more cleanly than any other feed.", "Ethane", id=0)
X("Propane", "Propane", "C3H8", "Gas", "A three-carbon alkane, liquefied under modest pressure as bottled gas for camping stoves and barbecues.", "Propane", id=0)
L("Propylene", "Propylene", "C3H6", "Gas", props=["IsMonomer"])
L("Butane", "Butane", "C4H10", "Gas")
L("Butadiene", "1,3-Butadiene", "C4H6", "Gas", props=["IsMonomer"])
L("Styrene", "Styrene", "C8H8", "Liquid", props=["IsMonomer"])
L("Ethylbenzene", "Ethylbenzene", "C8H10", "Liquid")
L("VinylChloride", "Vinyl chloride", "C2H3Cl", "Gas", props=["IsMonomer"])
X("EDC", "1,2-Dichloroethane", "C2H4Cl2", "Liquid", "Ethylene dichloride, the 'oil of the Dutch chemists' (1795). Cracked hot, it gives vinyl chloride for PVC; it is made in larger volume than almost any other organochlorine.", "1,2-Dichloroethane", id=0)
X("PVC", "PVC", "(C2H3Cl)n", "Solid", "Polyvinyl chloride. Waldo Semon at B.F. Goodrich (1926) found how to plasticise it; now pipes, window frames, cable insulation and vinyl records.", "Polyvinyl_chloride", id=0, balance="C2H3Cl", props=["IsPolymer"], color="#e8ecf0")
X("PS", "Polystyrene", "(C8H8)n", "Solid", "Clear, rigid and brittle; foamed with gas it becomes Styrofoam. BASF began making it in 1931.", "Polystyrene", id=0, balance="C8H8", props=["IsPolymer"], color="#f4f4f8")
L("TFE", "Tetrafluoroethylene", "C2F4", "Gas", props=["IsMonomer"])
X("PTFE", "Teflon (PTFE)", "(C2F4)n", "Solid", "Roy Plunkett (1938) opened a cylinder of tetrafluoroethylene that should have been full and found it empty, its inside coated with a slippery white wax. Nothing sticks to it, and almost nothing attacks it.", "Polytetrafluoroethylene", id=0, balance="C2F4", props=["IsPolymer"], color="#f8f8f8")
L("CHClF2", "Chlorodifluoromethane", "CHClF2", "Gas", name="Freon-22", rename=True)
L("CCl2F2", "Dichlorodifluoromethane", "CCl2F2", "Gas", name="Freon-12", rename=True)
L("CCl4", "Carbon tetrachloride", "CCl4", "Liquid")
L("Adiponitrile", "Adiponitrile", "C6H8N2", "Liquid")
L("Cyclohexanone", "Cyclohexanone", "C6H10O", "Liquid")
L("Caprolactam", "Caprolactam", "C6H11NO", "Solid", props=["IsMonomer"])
X("Nylon6", "Nylon 6", "(C6H11NO)n", "Solid", "Paul Schlack at IG Farben (1938) polymerised caprolactam into a nylon that dodged DuPont's patents: Perlon.", "Nylon_6", id=0, balance="C6H11NO", props=["IsPolymer"])
L("EO", "Ethylene oxide", "C2H4O", "Gas")
L("EG", "Ethylene glycol", "C2H6O2", "Liquid")
L("pXylene", "p-Xylene", "C8H10", "Liquid")
L("TPA", "Terephthalic acid", "C8H6O4", "Solid", props=["IsAcid"])
X("PET", "PET (polyester)", "(C10H8O4)n", "Solid", "Polyethylene terephthalate (Whinfield and Dickson, 1941): Terylene and Dacron fibres, then the clear plastic of drinks bottles.", "Polyethylene_terephthalate", id=0, balance="C10H8O4", props=["IsPolymer"])
L("HCN", "Hydrogen cyanide", "HCN", "Gas")
X("MMA", "Methyl Methacrylate", "C5H8O2", "Liquid", "The monomer of Perspex and Plexiglas, made since 1933 from acetone and hydrogen cyanide.", "Methyl_methacrylate", id=0, props=["IsMonomer"])
X("PMMA", "Acrylic Glass (PMMA)", "(C5H8O2)n", "Solid", "Polymethyl methacrylate: clear, shatter-resistant 'organic glass' for Spitfire canopies, aquarium walls and contact lenses.", "Poly(methyl_methacrylate)", id=0, balance="C5H8O2", props=["IsPolymer"], color="#e8f4ff")
X("Vinylacetylene", "Vinylacetylene", "C4H4", "Gas", "Two acetylenes joined: Julius Nieuwland's copper-catalysed dimer (1920s), the route to neoprene.", "Vinylacetylene", id=0)
X("Chloroprene", "Chloroprene", "C4H5Cl", "Liquid", "2-Chlorobutadiene, the monomer of neoprene.", "Chloroprene", id=0, props=["IsMonomer"])
X("Neoprene", "Neoprene", "(C4H5Cl)n", "Solid", "DuPont's synthetic rubber (1931): oil- and weatherproof, the stuff of wetsuits and laptop sleeves.", "Neoprene", id=0, balance="C4H5Cl", props=["IsPolymer"], color="#202020")
X("SBR", "Styrene-Butadiene Rubber", "(C12H14)n", "Solid", "Buna-S (1929), and the American GR-S that replaced lost natural rubber in the Second World War. Most car tyres are still made of it.", "Styrene-butadiene", id=0, balance="C12H14", props=["IsPolymer"], color="#2a2a2a")
X("PP", "Polypropylene", "(C3H6)n", "Solid", "Giulio Natta (1954) used Ziegler's titanium catalysts to line up propylene units the same way round, making a tough, heat-resistant plastic: car bumpers, ropes, food tubs.", "Polypropylene", id=0, balance="C3H6", props=["IsPolymer"])
X("HDPE", "High-Density Polyethylene", "(C2H4)n", "Solid", "Karl Ziegler (1953) made linear polyethylene at low pressure with a titanium catalyst: stiffer and stronger than ICI's branched kind. Milk jugs and Hula Hoops.", "High-density_polyethylene", id=0, balance="C2H4", props=["IsPolymer"])
X("TiO2", "Rutile", "TiO2", "Solid", "Titanium dioxide, the brilliant white pigment in paint, paper and toothpaste, and the ore of titanium metal.", "Rutile", id=0, color="#f8f8f8")
X("TiCl4", "Titanium Tetrachloride", "TiCl4", "Liquid", "A colourless liquid that fumes into a dense white smoke in moist air. The intermediate in both titanium metal and the Ziegler-Natta catalyst.", "Titanium_tetrachloride", id=0)
L("CH3Cl", "Methyl chloride", "CH3Cl", "Gas")
X("Me2SiCl2", "Dimethyldichlorosilane", "C2H6Cl2Si", "Liquid", "The main product of Rochow's direct process (1945), and the building block of silicones.", "Dimethyldichlorosilane", id=0)
X("PDMS", "Silicone (PDMS)", "(C2H6OSi)n", "Solid", "Polydimethylsiloxane: a backbone of silicon and oxygen, like quartz, dressed in methyl groups. Sealants, breast implants, Silly Putty.", "Polydimethylsiloxane", id=0, balance="C2H6OSi", props=["IsPolymer"])
L("DNT", "2,4-Dinitrotoluene", "C7H6N2O4", "Solid")
L("TDA", "2,4-Diaminotoluene", "C7H10N2", "Solid")
L("TDI", "Toluene diisocyanate", "C9H6N2O2", "Liquid")
X("PU", "Polyurethane", "(C11H12N2O4)n", "Solid", "Otto Bayer (1937) joined diisocyanates to diols. Foamed, it fills mattresses and car seats; as a coating, it varnishes floors.", "Polyurethane", id=0, balance="C11H12N2O4", props=["IsPolymer"])
L("Nitroaniline", "4-Nitroaniline", "C6H6N2O2", "Solid")
L("PPD", "p-Phenylenediamine", "C6H8N2", "Solid")
L("TPC", "Terephthaloyl chloride", "C8H4Cl2O2", "Solid")
X("Kevlar", "Kevlar", "(C14H10N2O2)n", "Solid", "Stephanie Kwolek (1965) spun a cloudy liquid-crystal solution her colleagues thought should be thrown away: a fibre five times stronger than steel by weight. Bulletproof vests, tyres, fibre-optic cables.", "Kevlar", id=0, balance="C14H10N2O2", props=["IsPolymer"], color="#e8c040")
X("BPA", "Bisphenol A", "C15H16O2", "Solid", "Two phenols bridged by acetone (Dianin, 1891). The monomer of polycarbonate and epoxy resin.", "Bisphenol_A", id=0)
L("Epichlorohydrin", "Epichlorohydrin", "C3H5ClO", "Liquid")
X("Epoxy", "Epoxy Resin", "(C21H24O4)n", "Solid", "Bisphenol A and epichlorohydrin, cured with a hardener into one of the toughest adhesives known (Castan and Greenlee, 1940s).", "Epoxy", id=0, balance="C18H21ClO3", props=["IsPolymer"])
X("PC", "Polycarbonate", "(C16H14O3)n", "Solid", "Hermann Schnell at Bayer (1953): a clear plastic tough enough for riot shields, spectacle lenses and CDs.", "Polycarbonate", id=0, balance="C16H14O3", props=["IsPolymer"])
L("Acrylonitrile", "Acrylonitrile", "C3H3N", "Liquid", props=["IsMonomer"])
X("PAN", "Acrylic Fibre (PAN)", "(C3H3N)n", "Solid", "Polyacrylonitrile, DuPont's Orlon (1950): a wool substitute, and when charred under tension, the precursor of carbon fibre.", "Polyacrylonitrile", id=0, balance="C3H3N", props=["IsPolymer"])
L("VinylAcetate", "Vinyl acetate", "C4H6O2", "Liquid", props=["IsMonomer"])
X("PVAc", "Polyvinyl Acetate", "(C4H6O2)n", "Solid", "Fritz Klatte's 1912 polymer, sold as white wood glue and school glue.", "Polyvinyl_acetate", id=0, balance="C4H6O2", props=["IsPolymer"])
L("SulfanilicAcid", "Sulfanilic acid", "C6H7NO3S", "Solid", props=["IsAcid"])
L("Sulfanilamide", "Sulfanilamide", "C6H8N2O2S", "Solid")
L("Aminophenol", "4-Aminophenol", "C6H7NO", "Solid")
L("Paracetamol", "Acetaminophen", "C8H9NO2", "Solid", name="Paracetamol", rename=True)
X("Nitrotoluene", "4-Nitrotoluene", "C7H7NO2", "Solid", "Toluene with a nitro group opposite its methyl: pale yellow crystals, the start of the route to PABA and benzocaine.", "4-Nitrotoluene", id=0)
L("NitrobenzoicAcid", "4-Nitrobenzoic acid", "C7H5NO4", "Solid", props=["IsAcid"])
X("PABA", "4-Aminobenzoic Acid", "C7H7NO2", "Solid", "PABA: a vitamin for bacteria (which sulfa drugs block), the first sunscreen ingredient, and the backbone of benzocaine.", "4-Aminobenzoic_acid", id=0)
L("Benzocaine", "Benzocaine", "C9H11NO2", "Solid")
L("Chlorobenzene", "Chlorobenzene", "C6H5Cl", "Liquid")
X("DDT", "DDT", "C14H9Cl5", "Solid", "First made in 1874, its insect-killing power found by Paul Muller in 1939 (Nobel Prize, 1948). It all but ended malaria in Europe, then thinned eagles' eggshells; Rachel Carson's Silent Spring (1962) led to its ban on farms.", "DDT", id=0)
X("Sorbitol", "Sorbitol", "C6H14O6", "Solid", "A sugar alcohol made by hydrogenating glucose: sugar-free sweets, and the first step in Reichstein's vitamin C synthesis.", "Sorbitol", id=0)
L("VitaminC", "L-Ascorbic acid", "C6H8O6", "Solid", name="Vitamin C", rename=True, props=["IsAcid"])
X("Penicillium", "Penicillium Culture", "mixture", "Solid", "A blue-green mould. A strain from a mouldy cantaloupe in a Peoria market (1943) yielded 200 times more penicillin than Fleming's original.", "Penicillium", id=0, balance="C")
X("Penicillin", "Penicillin G", "C16H18N2O4S", "Solid", "Benzylpenicillin. Alexander Fleming saw mould killing bacteria on a culture plate in 1928; Florey, Chain and Heatley made it a drug in 1940-41. By D-Day there was enough for every Allied soldier.", "Penicillin", id=0)
X("CornSteep", "Corn Steep Liquor", "mixture", "Aqueous", "The syrupy by-product of starch milling. Added to the fermentation broth in Peoria, it multiplied penicillin yields.", "Corn_steep_liquor", id=0, balance="C")
L("HSiCl3", "Trichlorosilane", "HSiCl3", "Liquid")
X("Polysilicon", "Polysilicon", "Si", "Solid", "Silicon purified to 99.9999999%, nine nines, by decomposing trichlorosilane on hot rods (the Siemens process, 1950s).", "Polycrystalline_silicon", id=0, color="#5a6070")
X("Wafer", "Silicon Wafer", "Si", "Solid", "A slice of a single crystal of silicon, pulled from the melt by the Czochralski method. Every chip starts as one.", "Wafer_(electronics)", id=0, color="#6a7488")
X("PSi", "p-Type Silicon", "Si(B)", "Solid", "Silicon doped with a trace of boron: each boron leaves a 'hole' that carries current.", "Extrinsic_semiconductor", id=0, balance="Si")
X("NSi", "n-Type Silicon", "Si(P)", "Solid", "Silicon doped with a trace of phosphorus, each of which donates a spare electron.", "Extrinsic_semiconductor", id=0, balance="Si")
X("Transistor", "Transistor", "Si", "Solid", "Bardeen, Brattain and Shockley at Bell Labs (1947): a sandwich of doped semiconductor that switches and amplifies. Billions sit in every phone.", "Transistor", id=0, balance="Si2")
X("Diamond", "Diamond", "C", "Solid", "Carbon in a three-dimensional lattice, the hardest natural material. General Electric made the first reproducible synthetic diamonds in 1954 at 50,000 atmospheres.", "Diamond", id=0, color="#e8f8ff")
X("UF4", "Uranium Tetrafluoride", "UF4", "Solid", "Green salt, the intermediate between uranium oxide and the metal or the hexafluoride.", "Uranium_tetrafluoride", id=0, props=["IsRadioactive"], color="#40a040")
X("UF6", "Uranium Hexafluoride", "UF6", "Solid", "A white solid that sublimes at 57 C, the only uranium compound volatile enough to be separated by gaseous diffusion.", "Uranium_hexafluoride", id=0, props=["IsRadioactive"])
L("Melamine", "Melamine", "C3H6N6", "Solid")
X("Dodecanol", "Lauryl Alcohol", "C12H26O", "Liquid", "1-Dodecanol, made from coconut and palm-kernel oil. Sulfated, it becomes the foaming agent in shampoo.", "Dodecanol", id=0)
L("SDS", "Sodium dodecyl sulfate", "C12H25NaO4S", "Solid")
X("CoconutOil", "Coconut Oil", "C39H74O6", "Solid", "A fat rich in twelve-carbon lauric acid, pressed from dried coconut meat.", "Coconut_oil", id=0, balance="C39H74O6")
X("SilicaGel", "Silica Gel", "SiO2", "Solid", "A porous form of silica with an enormous internal surface. Those 'do not eat' sachets are full of it.", "Silica_gel", id=0)
X("Aerogel", "Silica Aerogel", "SiO2", "Solid", "Samuel Kistler (1931) dried a gel without letting it collapse: a solid that is 99% air, so light it looks like frozen smoke.", "Aerogel", id=0, color="#c8e0f8")
L("Cumene", "Cumene", "C9H12", "Liquid")
L("MgOH2", "Magnesium hydroxide", "Mg(OH)2", "Solid", props=["IsBase"])
L("MgF2", "Magnesium fluoride", "MgF2", "Solid")

E5 = Epoch("Modern", "1920 to 1970", [
    # --- fuels ---
    R("Fischer-Tropsch Synthesis", "8 CO + 17 H2 -> Octane + 8 H2O", CAT,
      "Franz Fischer and Hans Tropsch (1925) turned coal-derived syngas into liquid fuel over cobalt. Germany ran its wartime vehicles on it; South Africa still does.",
      wiki="Fischer-Tropsch_process", cat="Co", T=220, P=20, dh=-1300),
    R("Bergius Hydrogenation", "Coal + H2 -> Gasoline", PRESS,
      "Friedrich Bergius (1913, Nobel 1931) hammered hydrogen into powdered coal at 200 atmospheres, liquefying it into oil.",
      wiki="Bergius_process", T=450, P=200, exact=False, dh=-200),
    R("Catalytic Cracking", "Hexadecane -> Octane + Octene", CAT,
      "Eugene Houdry (1937) cracked heavy oil over clay catalysts into high-octane gasoline. His process fuelled the Allied air forces' 100-octane aviation spirit.",
      wiki="Fluid_catalytic_cracking", cat="Clay", T=500, dh=80),
    R("Separating Natural Gas", "NaturalGas -> Methane + Ethane + Propane + Butane", DISTIL,
      "Chilling and distilling natural gas splits off the liquids that become fuel gas and chemical feedstock.",
      wiki="Natural-gas_processing", T=-100, exact=False, dh=0),
    R("Steam Cracking Ethane", "Ethane -> Ethylene + H2", HEAT,
      "A fraction of a second at 850 C strips hydrogen from ethane. Ethylene is the world's most-produced organic chemical.",
      wiki="Steam_cracking", T=850, dh=137),
    R("Steam Cracking Naphtha", "Naphtha -> Ethylene + Propylene + Butadiene", HEAT,
      "Naphtha cracked with steam gives a whole family of small alkenes for polymers.",
      wiki="Steam_cracking", T=850, exact=False, dh=200),
    R("Dehydrogenating Butane", "Butane -> Butadiene + 2 H2", CAT,
      "Butane passed over hot chromium oxide loses hydrogen and becomes butadiene, synthetic rubber's monomer (Houdry, 1940s).",
      wiki="1,3-Butadiene#Production", cat="Cr2O3", T=600, dh=235),
    R("Propane Torch", "Propane + 5 O2 -> 3 CO2 + 4 H2O", HEAT,
      "Propane burns hot and clean; bottled, it brought gas cooking to places with no gas main.",
      wiki="Propane", dh=-2220),
    R("Methanol Synthesis", "CO + 2 H2 -> Methanol", PRESS,
      "BASF (1923) made methanol from syngas over zinc and chromium oxides at 200 atmospheres, ending wood distillation as its source.",
      wiki="Methanol#Production", T=300, P=200, dh=-91),
    R("Steam Reforming", "Methane + H2O -> CO + 3 H2", CAT,
      "Natural gas and steam over nickel give syngas: the source of most of the world's hydrogen and ammonia since the 1930s.",
      wiki="Steam_reforming", cat="Ni", T=850, dh=206),
    R("Downs Cell", "2 NaCl -> 2 Na + Cl2", ELEC,
      "James Downs (1924) electrolysed molten salt with calcium chloride to lower its melting point. Cheaper sodium made tetraethyl lead and titanium possible.",
      wiki="Downs_cell", T=600, dh=822),
    # --- plastics ---
    R("ICI Polyethylene", "Ethylene -> PE", POLY,
      "Fawcett and Gibson at ICI (1933) heated ethylene at 1400 atmospheres and found a waxy white solid. It insulated wartime radar cables; now it is the world's commonest plastic.",
      wiki="Polyethylene#History", T=200, P=1500, dh=-93),
    R("Ziegler Polyethylene", "Ethylene -> HDPE", CAT,
      "Karl Ziegler (1953) polymerised ethylene at room pressure with titanium chloride and aluminium alkyls. Nobel Prize, 1963, shared with Natta.",
      wiki="Ziegler-Natta_catalyst", cat="TiCl4", T=70, dh=-93),
    R("Natta Polypropylene", "Propylene -> PP", CAT,
      "Natta's isotactic polypropylene (1954): every methyl group on the same side of the chain, which lets it crystallise.",
      wiki="Polypropylene#History", cat="TiCl4", T=70, dh=-85),
    R("Chlorinating Ethylene", "Ethylene + Cl2 -> EDC", MIX,
      "Chlorine adds across ethylene's double bond to give the Dutch chemists' oil.",
      wiki="1,2-Dichloroethane#Production", dh=-180),
    R("Cracking EDC", "EDC -> VinylChloride + HCl", HEAT,
      "Ethylene dichloride heated to 500 C sheds hydrogen chloride and becomes vinyl chloride.",
      wiki="Vinyl_chloride#Production", T=500, dh=70),
    R("Acetylene Vinyl Chloride", "Acetylene + HCl -> VinylChloride", CAT,
      "The older route, over mercury chloride: still used in China, where coal-based carbide is cheap.",
      wiki="Vinyl_chloride#Production", cat="HgCl2", T=150, dh=-100),
    R("Polymerising PVC", "VinylChloride -> PVC", POLY,
      "Vinyl chloride polymerises in water suspension into a white powder that is compounded into everything from pipes to credit cards.",
      wiki="Polyvinyl_chloride#Production", T=60, dh=-96),
    R("Ethylbenzene", "Benzene + Ethylene -> Ethylbenzene", CAT,
      "Friedel-Crafts alkylation: ethylene attaches to benzene over aluminium chloride (now zeolites).",
      wiki="Ethylbenzene#Production", cat="AlCl3", T=100, dh=-105),
    R("Dehydrogenating Ethylbenzene", "Ethylbenzene -> Styrene + H2", CAT,
      "Superheated steam and iron oxide catalyst pull hydrogen from ethylbenzene: styrene.",
      wiki="Styrene#Production", cat="Hematite", T=600, dh=124),
    R("Polystyrene", "Styrene -> PS", POLY,
      "Styrene polymerises on gentle heating; Eduard Simon noticed it turning to jelly in 1839, BASF made it a product in 1931.",
      wiki="Polystyrene#History", T=100, dh=-70),
    R("Swarts Fluorination", "CHCl3 + 2 HF -> CHClF2 + 2 HCl", CAT,
      "Frederic Swarts' antimony catalyst swaps chlorine for fluorine: chloroform becomes Freon-22.",
      wiki="Swarts_fluorination", cat="SbCl5", T=100, dh=-50),
    R("Pyrolysing Freon-22", "2 CHClF2 -> TFE + 2 HCl", HEAT,
      "At 700 C two Freon-22 molecules lose HCl and join into tetrafluoroethylene.",
      wiki="Tetrafluoroethylene#Production", T=700, dh=130),
    R("Plunkett's Teflon", "TFE -> PTFE", POLY,
      "Tetrafluoroethylene polymerises on its own under pressure, as Plunkett's empty cylinder showed (1938). PTFE seals were used in the Manhattan Project's uranium plant because UF6 ate everything else.",
      wiki="Polytetrafluoroethylene#History", T=50, P=20, dh=-170),
    R("Chlorinating Methane", "Methane + 4 Cl2 -> CCl4 + 4 HCl", LIGHT,
      "Under light, chlorine replaces methane's hydrogens one by one, ending at carbon tetrachloride.",
      wiki="Carbon_tetrachloride#Production", dh=-400),
    R("Midgley's Freon", "CCl4 + 2 HF -> CCl2F2 + 2 HCl", CAT,
      "Thomas Midgley (1928) chose dichlorodifluoromethane as a safe refrigerant and inhaled it on stage to prove it. Fifty years later it was found to be destroying the ozone layer.",
      wiki="Dichlorodifluoromethane#History", cat="SbCl5", T=100, dh=-40),
    R("Oxidising Cyclohexane", "2 Cyclohexane + 5 O2 -> 2 Adipic + 2 H2O", HEAT,
      "Cyclohexane is oxidised by air, then nitric acid, into adipic acid.",
      wiki="Adipic_acid#Production", T=150, dh=-1600),
    R("Adiponitrile", "Adipic + 2 NH3 -> Adiponitrile + 4 H2O", HEAT,
      "Adipic acid and ammonia, dehydrated, give adiponitrile.",
      wiki="Adiponitrile#Production", T=300, dh=150),
    R("Hexamethylenediamine", "Adiponitrile + 4 H2 -> HMDA", CAT,
      "Hydrogenating both nitrile ends gives the diamine for nylon.",
      wiki="Hexamethylenediamine#Production", cat="Ni", T=100, P=30, dh=-300),
    R("Carothers' Nylon", "Adipic + HMDA -> Nylon66 + 2 H2O", POLY,
      "Wallace Carothers at DuPont (1935) joined adipic acid and hexamethylenediamine into the first wholly synthetic fibre. Nylon stockings sold 4 million pairs in four days in 1940.",
      wiki="Nylon#History", T=270, dh=-30),
    R("Phenol to Cyclohexanone", "Phenol + 2 H2 -> Cyclohexanone", CAT,
      "Phenol hydrogenated over palladium stops at the ketone.",
      wiki="Cyclohexanone#Production", cat="Pd", T=150, dh=-140),
    R("Making Caprolactam", "Cyclohexanone + NH3 + H2O2 -> Caprolactam + 2 H2O", HEAT,
      "Cyclohexanone becomes its oxime with ammonia and peroxide, and the oxime rearranges in acid (the Beckmann rearrangement) into the seven-membered caprolactam ring.",
      wiki="Caprolactam#Production", T=100, dh=-300),
    R("Schlack's Nylon 6", "Caprolactam -> Nylon6", POLY,
      "Heated with a little water, caprolactam rings open and link into nylon 6.",
      wiki="Nylon_6", T=260, dh=-15),
    R("Ethylene Oxide", "2 Ethylene + O2 -> 2 EO", CAT,
      "Theodore Lefort (1931) oxidised ethylene directly over silver. Ethylene oxide sterilises medical equipment and makes glycols and detergents.",
      wiki="Ethylene_oxide#Production", cat="Ag", T=250, dh=-210),
    R("Ethylene Glycol", "EO + H2O -> EG", HEAT,
      "Ethylene oxide opens with water into ethylene glycol: antifreeze, and half of polyester.",
      wiki="Ethylene_glycol#Production", T=200, dh=-95),
    R("Oxidising p-Xylene", "pXylene + 3 O2 -> TPA + 2 H2O", CAT,
      "The Amoco process (1955): p-xylene oxidised by air with cobalt, manganese and bromide gives terephthalic acid.",
      wiki="Terephthalic_acid#Production", cat="Co", T=200, dh=-1360),
    R("Whinfield's Polyester", "TPA + EG -> PET + 2 H2O", POLY,
      "John Whinfield and James Dickson (1941) found Carothers had missed aromatic polyesters: PET, now in a sixth of all plastic.",
      wiki="Polyethylene_terephthalate#History", T=280, dh=-20),
    R("Andrussow Process", "2 Methane + 2 NH3 + 3 O2 -> 2 HCN + 6 H2O", CAT,
      "Leonid Andrussow (1927): methane, ammonia and air over platinum gauze give hydrogen cyanide.",
      wiki="Andrussow_process", cat="Pt", T=1100, dh=-940),
    R("Methyl Methacrylate", "Acetone + HCN + Methanol -> MMA + NH3", MIX,
      "Acetone and hydrogen cyanide form a cyanohydrin that sulfuric acid and methanol convert to methyl methacrylate (ICI, 1933).",
      wiki="Methyl_methacrylate#Production", dh=-100),
    R("Perspex", "MMA -> PMMA", POLY,
      "Cast in sheets, polymethyl methacrylate became Perspex (1933). Shards in pilots' eyes caused no inflammation, which led to the first plastic intraocular lenses.",
      wiki="Poly(methyl_methacrylate)#History", T=80, dh=-55),
    R("Nieuwland Dimerisation", "2 Acetylene -> Vinylacetylene", CAT,
      "Father Julius Nieuwland at Notre Dame dimerised acetylene over copper(I) chloride.",
      wiki="Vinylacetylene", cat="Cu", T=80, dh=-200),
    R("Chloroprene", "Vinylacetylene + HCl -> Chloroprene", MIX,
      "Hydrogen chloride adds to vinylacetylene: chloroprene, which polymerises far faster than isoprene.",
      wiki="Chloroprene", dh=-80),
    R("DuPont Neoprene", "Chloroprene -> Neoprene", POLY,
      "Arnold Collins at DuPont (1930) found chloroprene sitting in a jar had set into rubber.",
      wiki="Neoprene#History", T=40, dh=-70),
    R("Buna-S Rubber", "Butadiene + Styrene -> SBR", POLY,
      "Emulsion copolymerisation of butadiene and styrene (IG Farben, 1929). The US built 51 plants in two years when Japan cut off natural rubber in 1942.",
      wiki="Styrene-butadiene#History", T=50, dh=-150),
    R("Sohio Acrylonitrile", "2 Propylene + 2 NH3 + 3 O2 -> 2 Acrylonitrile + 6 H2O", CAT,
      "Sohio (1957) reacted propylene, ammonia and air over bismuth molybdate in one step.",
      wiki="Ammoxidation", cat="Bi2O3", T=450, dh=-1030),
    R("Orlon", "Acrylonitrile -> PAN", POLY,
      "Polyacrylonitrile, spun into DuPont's Orlon (1950).",
      wiki="Polyacrylonitrile", T=60, dh=-75),
    R("Vinyl Acetate", "2 Ethylene + 2 AcOH + O2 -> 2 VinylAcetate + 2 H2O", CAT,
      "Ethylene, acetic acid and oxygen combine over palladium.",
      wiki="Vinyl_acetate#Production", cat="Pd", T=175, dh=-350),
    R("PVA Glue", "VinylAcetate -> PVAc", POLY,
      "Vinyl acetate polymerised in water: white glue.",
      wiki="Polyvinyl_acetate", T=70, dh=-88),
    R("Kroll Chlorination", "TiO2 + 2 Cl2 + 2 Coke -> TiCl4 + 2 CO", HEAT,
      "Rutile and coke heated in chlorine give titanium tetrachloride, purified by distillation.",
      wiki="Kroll_process", T=1000, dh=-80),
    R("Kroll Titanium", "TiCl4 + 2 Mg -> Ti + 2 MgCl2", SMELT,
      "William Kroll (1940) reduced titanium tetrachloride with molten magnesium under argon. Titanium sponge became the light, strong metal of jet engines and spy planes.",
      wiki="Kroll_process", T=850, dh=-480),
    R("Rochow Direct Process", "Si + 2 CH3Cl -> Me2SiCl2", CAT,
      "Eugene Rochow (1945) passed methyl chloride over silicon with a copper catalyst, opening the way to cheap silicones.",
      wiki="Direct_process", cat="Cu", T=300, dh=-300),
    R("Methyl Chloride", "Methanol + HCl -> CH3Cl + H2O", HEAT,
      "Methanol and hydrogen chloride over alumina give methyl chloride.",
      wiki="Chloromethane#Production", T=350, dh=-30),
    R("Silicone", "Me2SiCl2 + H2O -> PDMS + 2 HCl", POLY,
      "Water hydrolyses the chlorosilane and the silanols condense into long silicon-oxygen chains.",
      wiki="Polydimethylsiloxane#Synthesis", dh=-50),
    R("Dinitrotoluene", "Toluene + 2 HNO3 -> DNT + 2 H2O", MIX,
      "At room temperature toluene takes two nitro groups, stopping short of TNT.",
      wiki="2,4-Dinitrotoluene", dh=-150),
    R("Toluenediamine", "DNT + 6 H2 -> TDA + 4 H2O", CAT,
      "Both nitro groups hydrogenated to amines over nickel.",
      wiki="2,4-Diaminotoluene", cat="Ni", T=100, dh=-1000),
    R("Toluene Diisocyanate", "TDA + 2 COCl2 -> TDI + 4 HCl", HEAT,
      "Phosgene turns both amines into reactive isocyanates.",
      wiki="Toluene_diisocyanate#Production", T=150, dh=-100),
    R("Bayer's Polyurethane", "TDI + EG -> PU", POLY,
      "Otto Bayer (1937): each isocyanate grabs an alcohol, chaining diisocyanate and diol together.",
      wiki="Polyurethane#History", T=80, dh=-200),
    R("Nitrating Aniline", "Aniline + HNO3 -> Nitroaniline + H2O", MIX,
      "Aniline nitrated (via its acetyl derivative) at the position opposite its amine.",
      wiki="4-Nitroaniline", dh=-120),
    R("p-Phenylenediamine", "Nitroaniline + 3 H2 -> PPD + 2 H2O", CAT,
      "The nitro group hydrogenated over palladium leaves two amines.",
      wiki="p-Phenylenediamine", cat="Pd", T=100, dh=-500),
    R("Terephthaloyl Chloride", "TPA + 2 COCl2 -> TPC + 2 CO2 + 2 HCl", HEAT,
      "Phosgene converts terephthalic acid into its reactive acid chloride.",
      wiki="Terephthaloyl_chloride", T=100, dh=-50),
    R("Kwolek's Kevlar", "PPD + TPC -> Kevlar + 2 HCl", POLY,
      "Para-phenylenediamine and terephthaloyl chloride form rigid rod-like chains that line up as liquid crystals (DuPont, 1965).",
      wiki="Kevlar#History", T=10, dh=-100),
    R("Bisphenol A", "2 Phenol + Acetone -> BPA + H2O", MIX,
      "Two phenols condense on acetone with an acid catalyst.",
      wiki="Bisphenol_A#Production", dh=-80),
    R("Epoxy Resin", "BPA + Epichlorohydrin -> Epoxy", POLY,
      "Bisphenol A and epichlorohydrin, with alkali, give the glycidyl ether that hardeners cure into epoxy.",
      wiki="Epoxy#Chemistry", T=80, exact=False, dh=-100),
    R("Polycarbonate", "BPA + COCl2 -> PC + 2 HCl", POLY,
      "Bisphenol A joined by phosgene into long carbonate chains (Bayer and GE, 1953, independently).",
      wiki="Polycarbonate#Production", T=30, dh=-100),
    R("Epichlorohydrin", "Glycerol + 2 HCl + NaOH -> Epichlorohydrin + NaCl + 3 H2O", HEAT,
      "Glycerol, the by-product of biodiesel and soap, chlorinated and cyclised into epichlorohydrin.",
      wiki="Epichlorohydrin#Production", T=120, exact=True, dh=-50),
    R("Melamine", "6 Urea -> Melamine + 6 NH3 + 3 CO2", CAT,
      "Urea passed over an alumina catalyst at 400 C trimerises to melamine. With formaldehyde it makes Formica and unbreakable plates.",
      wiki="Melamine#Production", cat="Alumina", T=400, dh=470),
    R("Bosch-Meiser Urea", "2 NH3 + CO2 -> Urea + H2O", PRESS,
      "BASF (1922) combined ammonia and carbon dioxide under pressure. Urea is now the world's most-used nitrogen fertilizer.",
      wiki="Urea#Industrial_production", T=190, P=150, dh=-100),
    # --- drugs ---
    R("Sulfanilic Acid", "Aniline + H2SO4 -> SulfanilicAcid + H2O", HEAT,
      "Aniline baked with sulfuric acid rearranges into sulfanilic acid.",
      wiki="Sulfanilic_acid", T=180, dh=-50),
    R("Sulfa Drugs", "SulfanilicAcid + NH3 -> Sulfanilamide + H2O", HEAT,
      "Gerhard Domagk (1932) found the red dye Prontosil cured streptococcal infections in mice; at the Pasteur Institute it was found to release sulfanilamide in the body. The first broad antibacterial drug.",
      wiki="Sulfanilamide#History", T=100, dh=-30),
    R("Fermenting Penicillin", "Glucose + CornSteep + Penicillium -> Penicillin", MIX,
      "Deep-tank fermentation of Penicillium in corn steep liquor and sugar, developed at Peoria and by Pfizer (1943), turned a laboratory curiosity into a mass-produced drug.",
      wiki="History_of_penicillin", exact=False, dh=0),
    R("Bamberger Rearrangement", "Nitrobenzene + 2 H2 -> Aminophenol + H2O", CAT,
      "Nitrobenzene partly hydrogenated over platinum in acid rearranges to 4-aminophenol.",
      wiki="Bamberger_rearrangement", cat="Pt", T=80, dh=-400),
    R("Paracetamol", "Aminophenol + AceticAnhydride -> Paracetamol + AcOH", MIX,
      "Acetylating 4-aminophenol. Made in 1878, dismissed, and rediscovered in 1948 as the active metabolite of phenacetin.",
      wiki="Paracetamol#History", T=100, dh=-50),
    R("Nitrotoluene", "Toluene + HNO3 -> Nitrotoluene + H2O", COOL,
      "Kept cold, toluene takes only one nitro group; warmer it takes two, and hot with oleum three.",
      wiki="Nitrotoluene", dh=-110),
    R("Oxidising Nitrotoluene", "2 Nitrotoluene + 3 O2 -> 2 NitrobenzoicAcid + 2 H2O", HEAT,
      "The methyl group oxidised to a carboxylic acid.",
      wiki="4-Nitrobenzoic_acid", T=150, dh=-700),
    R("PABA", "NitrobenzoicAcid + 3 H2 -> PABA + 2 H2O", CAT,
      "Hydrogenating the nitro group gives para-aminobenzoic acid.",
      wiki="4-Aminobenzoic_acid", cat="Pd", T=80, dh=-500),
    R("Benzocaine", "PABA + Ethanol -> Benzocaine + H2O", HEAT,
      "Esterified with ethanol, PABA becomes benzocaine (Ritsert, 1890), the numbing agent in sore-throat lozenges.",
      wiki="Benzocaine", T=80, dh=-20),
    R("Chlorobenzene", "Benzene + Cl2 -> Chlorobenzene + HCl", CAT,
      "Chlorine substitutes onto benzene over iron(III) chloride.",
      wiki="Chlorobenzene#Production", cat="FeCl3", T=40, dh=-130),
    R("Muller's DDT", "Chloral + 2 Chlorobenzene -> DDT + H2O", MIX,
      "Chloral condenses with two chlorobenzenes in sulfuric acid.",
      wiki="DDT#History", dh=-100),
    R("Hydrogenating Glucose", "Glucose + H2 -> Sorbitol", CAT,
      "Glucose's aldehyde reduced over nickel gives sorbitol.",
      wiki="Sorbitol#Production", cat="Ni", T=120, P=50, dh=-60),
    R("Reichstein's Vitamin C", "2 Sorbitol + 3 O2 -> 2 VitaminC + 6 H2O", MIX,
      "Tadeus Reichstein (1933) combined a bacterial oxidation with chemical steps to make ascorbic acid from sorbitol. Roche made most of the world's vitamin C this way for sixty years.",
      wiki="Reichstein_process", exact=True, dh=-500),
    R("Lauryl Alcohol", "CoconutOil + 6 H2 -> 3 Dodecanol + Glycerol", CAT,
      "Coconut oil hydrogenolysed over copper chromite splits into fatty alcohols and glycerol.",
      wiki="Dodecanol#Production", cat="Cu", T=250, P=200, exact=False, dh=-200),
    R("Synthetic Detergent", "Dodecanol + H2SO4 + NaOH -> SDS + 2 H2O", MIX,
      "Sulfated and neutralised, lauryl alcohol becomes sodium dodecyl sulfate: a detergent that works in hard water, where soap scums.",
      wiki="Sodium_dodecyl_sulfate", dh=-150),
    # --- electronics and materials ---
    R("Metallurgical Silicon", "Sand + 2 Coke -> Si + 2 CO", SMELT,
      "Quartz reduced with carbon in an arc furnace gives 98% silicon for aluminium alloys and silicones.",
      wiki="Silicon#Production", T=1900, dh=690),
    R("Trichlorosilane", "Si + 3 HCl -> HSiCl3 + H2", HEAT,
      "Crude silicon and hydrogen chloride give trichlorosilane, which can be distilled extremely pure.",
      wiki="Trichlorosilane", T=300, dh=-140),
    R("Siemens Process", "HSiCl3 + H2 -> Polysilicon + 3 HCl", HEAT,
      "Trichlorosilane and hydrogen decompose on silicon rods heated to 1100 C, growing them into hyper-pure polysilicon.",
      wiki="Polycrystalline_silicon#Siemens_process", T=1100, dh=200),
    R("Czochralski Crystal", "Polysilicon -> Wafer", COOL,
      "A seed crystal dipped in molten silicon and drawn slowly upward grows a single perfect crystal ingot, sliced into wafers (Teal and Little, 1950).",
      wiki="Czochralski_method", T=1414, dh=-50),
    R("Boron Doping", "Wafer + B -> PSi", HEAT,
      "A few boron atoms per million diffused into silicon make p-type semiconductor.",
      wiki="Doping_(semiconductor)", T=1000, exact=False, dh=0),
    R("Phosphorus Doping", "Wafer + P4 -> NSi", HEAT,
      "Phosphorus diffused into silicon makes n-type semiconductor.",
      wiki="Doping_(semiconductor)", T=1000, exact=False, dh=0),
    R("The Transistor", "PSi + NSi -> Transistor", HEAT,
      "Junctions of p- and n-type silicon (Teal at Texas Instruments, 1954: the first silicon transistor).",
      wiki="Transistor#History", exact=False, dh=0),
    R("GE Synthetic Diamond", "Graphite -> Diamond", PRESS,
      "Tracy Hall at General Electric (1954) squeezed graphite with molten iron at 50,000 atmospheres and 1600 C in his belt press, and diamonds grew.",
      wiki="Synthetic_diamond#History", T=1600, P=50000, dh=2),
    R("Silica Gel", "Na2SiO3 + H2SO4 -> SilicaGel + Na2SO4 + H2O", MIX,
      "Acid sets water glass into a gel; washed and dried, it becomes the desiccant silica gel (Patrick, 1918).",
      wiki="Silica_gel#History", dh=-60),
    R("Kistler's Aerogel", "SilicaGel -> Aerogel", PRESS,
      "Kistler (1931) replaced the liquid in a gel with a supercritical fluid, which has no surface tension, so it left without collapsing the pores.",
      wiki="Aerogel#History", T=250, P=80, exact=False, dh=0),
    R("Dow Magnesium", "Seawater + Ca(OH)2 -> MgOH2 + NaCl", MIX,
      "Dow Chemical (1941) precipitated magnesium hydroxide from seawater with lime, then electrolysed the chloride, for the light metal of wartime aircraft.",
      wiki="Dow_process", exact=False, dh=0),
    R("Gallium from Bayer Liquor", "NaAlOH4 -> Ga", ELEC,
      "Gallium hides in bauxite at a few parts per million. Electrolysing Bayer liquor recovers it for LEDs and solar cells.",
      wiki="Gallium#Production", exact=False, dh=0),
    R("Cumene", "Benzene + Propylene -> Cumene", CAT,
      "Benzene alkylated with propylene: isopropylbenzene.",
      wiki="Cumene#Production", cat="H3PO4", T=250, dh=-100),
    R("Cumene Process", "Cumene + O2 -> Phenol + Acetone", HEAT,
      "Hock (1944): cumene oxidised by air to a hydroperoxide that acid cleaves into phenol and acetone. Most phenol is now made this way.",
      wiki="Cumene_process", T=100, dh=-250),
    # --- the atom ---
    R("Green Salt", "Pitchblende + 4 HF -> UF4 + 2 H2O", HEAT,
      "Uranium dioxide and hydrogen fluoride give green uranium tetrafluoride.",
      wiki="Uranium_tetrafluoride", T=550, dh=-180),
    R("Uranium Metal", "UF4 + 2 Mg -> U + 2 MgF2", SMELT,
      "The Ames process (1942): green salt reduced by magnesium in a sealed bomb gave the uranium for Fermi's pile.",
      wiki="Ames_process", T=1200, dh=-300),
    R("Uranium Hexafluoride", "UF4 + F2 -> UF6", HEAT,
      "Fluorine takes the tetrafluoride to the volatile hexafluoride.",
      wiki="Uranium_hexafluoride#Preparation", T=300, dh=-250),
    R("Neptunium", "U -> Np", LIGHT,
      "McMillan and Abelson (1940): uranium struck by neutrons gave an element with a 2.3-day half-life. The first transuranium element, named for the next planet out.",
      wiki="Neptunium#History", exact=False, dh=0),
    R("Seaborg's Plutonium", "U + H2 -> Pu", LIGHT,
      "Glenn Seaborg's team (1940) bombarded uranium with deuterons (heavy hydrogen) in Berkeley's cyclotron and identified element 94 by its chemistry. Reactors make it from uranium-238 by neutron capture.",
      wiki="Plutonium#History", exact=False, dh=0),
    R("Segre's Technetium", "Mo -> Tc", LIGHT,
      "Emilio Segre (1937) found element 43 in a molybdenum foil Lawrence had mailed him from the Berkeley cyclotron: the first element made artificially.",
      wiki="Technetium#History", exact=False, dh=0),
    R("Americium", "Pu -> Am", LIGHT,
      "Seaborg's group (1944) made element 95 by neutron capture in plutonium. A speck of it sits in every ionisation smoke detector.",
      wiki="Americium#History", exact=False, dh=0),
    R("Curium", "Pu + He -> Cm", LIGHT,
      "Plutonium bombarded with alpha particles gave element 96 (1944), named for the Curies. Seaborg announced it on a children's radio quiz show.",
      wiki="Curium#History", exact=False, dh=0),
    R("Berkelium", "Am + He -> Bk", LIGHT,
      "Thompson, Ghiorso and Seaborg (1949): alpha particles on americium.",
      wiki="Berkelium#History", exact=False, dh=0),
    R("Californium", "Cm + He -> Cf", LIGHT,
      "Element 98 (1950), made from a few micrograms of curium.",
      wiki="Californium#History", exact=False, dh=0),
    R("Einsteinium and Fermium", "Cf -> Es + Fm", LIGHT,
      "Found in the debris of the first hydrogen bomb test (1952), where uranium had swallowed many neutrons at once; now made in high-flux reactors.",
      wiki="Einsteinium#History", exact=False, dh=0),
    R("Mendelevium", "Es + He -> Md", LIGHT,
      "Ghiorso's team (1955) identified element 101 one atom at a time, 17 atoms in all.",
      wiki="Mendelevium#History", exact=False, dh=0),
    R("Nobelium", "Cm + Graphite -> No", LIGHT,
      "Carbon ions fired at curium (Dubna and Berkeley, 1958-66, after a famously disputed claim).",
      wiki="Nobelium#History", exact=False, dh=0),
    R("Lawrencium", "Cf + B -> Lr", LIGHT,
      "Boron ions on californium (Berkeley, 1961): the last actinide.",
      wiki="Lawrencium#History", exact=False, dh=0),
])

# Grignard reagents belong to 1900.
X("Bromobenzene", "Bromobenzene", "C6H5Br", "Liquid", "Benzene with one bromine: a heavy, pleasant-smelling liquid and the classic starting point for Grignard and Suzuki chemistry.", "Bromobenzene", id=0)
X("PhMgBr", "Phenylmagnesium Bromide", "C6H5BrMg", "Liquid", "A Grignard reagent: magnesium inserted between carbon and bromine makes the carbon act like a carbanion, ready to attack almost any carbonyl. Victor Grignard, Nobel Prize 1912.", "Phenylmagnesium_bromide", id=0)
E4.reactions += [
    R("Brominating Benzene", "Benzene + Br2 -> Bromobenzene + HBr", CAT,
      "Bromine substitutes onto benzene with an iron catalyst.",
      wiki="Bromobenzene#Preparation", cat="Fe", T=40, dh=-50),
    R("Grignard Reagent", "Bromobenzene + Mg -> PhMgBr", MIX,
      "Victor Grignard (1900) stirred magnesium turnings with an organic bromide in dry ether and got a reagent that could build almost any carbon skeleton.",
      wiki="Grignard_reagent#History", dh=-250),
]

# --- Epoch 6 (the Frontier: 1970 to today) ---
X("C60", "Buckminsterfullerene", "C60", "Solid", "Sixty carbon atoms in a hollow football. Kroto, Curl and Smalley (1985) found it in laser-blasted graphite vapour and named it for Buckminster Fuller's geodesic domes. Nobel Prize, 1996.", "Buckminsterfullerene", id=0, color="#4a3a5a")
X("CNT", "Carbon Nanotubes", "C", "Solid", "Graphite sheets rolled into seamless tubes a nanometre across. Sumio Iijima's 1991 images set off a rush; they are stronger than any steel and conduct like copper.", "Carbon_nanotube", id=0, color="#202020")
X("Graphene", "Graphene", "C", "Solid", "A single sheet of graphite one atom thick. Geim and Novoselov (2004) peeled it off with sticky tape on a Friday-evening experiment. Nobel Prize, 2010.", "Graphene", id=0, color="#404048")
X("CVDDiamond", "CVD Diamond", "C", "Solid", "Diamond grown atom by atom from a methane-hydrogen plasma (1980s). Lab-grown gems and the diamond windows of high-power lasers.", "Chemical_vapor_deposition_of_diamond", id=0, color="#f0faff")
L("Y2O3", "Yttrium oxide", "Y2O3", "Solid", id=2678, lib=True)
X("YBCO", "YBCO Superconductor", "YBa2Cu3O7", "Solid", "Yttrium barium copper oxide (Wu and Chu, 1987): superconducting at 93 K, above the boiling point of liquid nitrogen. A black ceramic that levitates magnets.", "Yttrium_barium_copper_oxide", id=0, color="#1a1a1a")
X("LiCoO2", "Lithium Cobalt Oxide", "LiCoO2", "Solid", "John Goodenough's 1980 cathode: lithium ions slip in and out between layers of cobalt oxide. Nobel Prize, 2019, at 97.", "Lithium_cobalt_oxide", id=0)
X("LiIonCell", "Lithium-Ion Cell", "LiCoO2+C6", "Solid", "Goodenough's cathode plus Akira Yoshino's carbon anode (1985), sold by Sony from 1991. It made phones, laptops and electric cars possible.", "Lithium-ion_battery", id=0, balance="LiCoO2C6")
L("FePO4", "Ferric phosphate", "FePO4", "Solid")
X("LiFePO4", "Lithium Iron Phosphate", "LiFePO4", "Solid", "John Goodenough's second great cathode (Padhi, 1997): cheaper and safer than cobalt, with no fire risk. Most electric buses and many cars use it.", "Lithium_iron_phosphate", id=0)
X("Monazite", "Monazite", "NdPO4", "Solid", "A heavy reddish phosphate sand carrying the light rare earths: cerium, lanthanum, neodymium, and some thorium. We follow its neodymium.", "Monazite", id=0, color="#a06030")
X("NdCl3", "Neodymium Chloride", "NdCl3", "Solid", "A mauve salt; electrolysed molten, it yields neodymium metal.", "Neodymium(III)_chloride", id=0, color="#c8a8d0")
X("NdFeB", "Neodymium Magnet", "Nd2Fe14B", "Solid", "Masato Sagawa (1982): the strongest permanent magnets known. In every hard drive, wind turbine and electric car motor.", "Neodymium_magnet", id=0, color="#909aa8")
X("GaN", "Gallium Nitride", "GaN", "Solid", "A hard, wide-bandgap semiconductor. Akasaki, Amano and Nakamura grew good enough crystals of it in the early 1990s to make the blue LED. Nobel Prize, 2014.", "Gallium_nitride", id=0)
X("BlueLED", "Blue LED", "InGaN", "Solid", "Indium gallium nitride layers on sapphire, glowing blue. With a yellow phosphor it makes the white LED, which uses a tenth of the power of a bulb.", "Light-emitting_diode#Blue_and_white_LEDs", id=0, balance="InGaN")
X("PbI2", "Lead(II) Iodide", "PbI2", "Solid", "Golden flakes that crystallise from hot water: the 'golden rain' demonstration, and half of a perovskite solar cell.", "Lead(II)_iodide", id=0, color="#f8d020")
X("HI", "Hydroiodic Acid", "HI", "Gas", "Hydrogen iodide, the strongest of the hydrohalic acids.", "Hydrogen_iodide", id=0, props=["IsAcid"])
L("Methylamine", "Methylamine", "CH5N", "Gas", props=["IsBase"])
X("MAI", "Methylammonium Iodide", "CH6IN", "Solid", "The organic salt that goes into perovskite solar cells.", "Methylammonium_lead_halide", id=0)
X("Perovskite", "Perovskite Solar Film", "CH6NPbI3", "Solid", "Methylammonium lead iodide (Kojima and Miyasaka, 2009). In a decade perovskite cells went from 4% to over 25% efficient, faster than any solar material before.", "Perovskite_solar_cell", id=0, color="#2a1a10")
X("CdSe", "Cadmium Selenide Quantum Dots", "CdSe", "Solid", "Nanocrystals a few nanometres across whose colour depends only on their size (Brus, Ekimov; Bawendi's hot-injection synthesis, 1993). Nobel Prize, 2023. They colour QLED televisions.", "Quantum_dot", id=0, color="#e85020")
X("MOF5", "MOF-5", "Zn4O(C8H4O4)3", "Solid", "Omar Yaghi's metal-organic framework (1999): zinc clusters linked by terephthalate struts into a crystal sponge with the surface area of a football pitch per gram. Nobel Prize, 2025.", "Metal-organic_framework", id=0)
X("RuCl3", "Ruthenium(III) Chloride", "RuCl3", "Solid", "The usual starting point for ruthenium chemistry.", "Ruthenium(III)_chloride", id=0)
X("Grubbs", "Grubbs Catalyst", "C43H72Cl2P2Ru", "Solid", "Robert Grubbs' ruthenium carbene (1992-95), stable in air, that swaps the ends of carbon-carbon double bonds. Nobel Prize, 2005, with Chauvin and Schrock.", "Grubbs_catalyst", id=0, color="#8a3a8a")
L("2-Butene", "2-Butene", "C4H8", "Gas")
X("PhB(OH)2", "Phenylboronic Acid", "C6H7BO2", "Solid", "A benzene ring on a boron. The partner in the Suzuki coupling.", "Phenylboronic_acid", id=0)
L("Biphenyl", "Biphenyl", "C12H10", "Solid")
L("Isobutylbenzene", "Isobutylbenzene", "C10H14", "Liquid")
X("IBAP", "4-Isobutylacetophenone", "C12H16O", "Liquid", "The first intermediate of the BHC ibuprofen process.", "Ibuprofen#Synthesis", id=0)
X("IBPE", "1-(4-Isobutylphenyl)ethanol", "C12H18O", "Liquid", "The alcohol that palladium carbonylates into ibuprofen.", "Ibuprofen#Synthesis", id=0)
L("Ibuprofen", "Ibuprofen", "C13H18O2", "Solid")
X("Lactose", "Lactose", "C12H22O11", "Solid", "Milk sugar, a disaccharide of glucose and galactose. Lactic bacteria ferment it to lactic acid.", "Lactose", id=0)
L("LacticAcid", "Lactic acid", "C3H6O3", "Liquid", props=["IsAcid"])
L("Lactide", "Lactide", "C6H8O4", "Solid", props=["IsMonomer"])
X("PLA", "Polylactic Acid", "(C3H4O2)n", "Solid", "A compostable plastic made from plant sugar (NatureWorks, 2002): 3D-printer filament, cups, and dissolving surgical stitches.", "Polylactic_acid", id=0, balance="C3H4O2", props=["IsPolymer"])
X("Wormwood", "Sweet Wormwood", "mixture", "Solid", "Artemisia annua, a Chinese herbal fever remedy for 1,600 years.", "Artemisia_annua", id=0, balance="C")
X("Artemisinin", "Artemisinin", "C15H22O5", "Solid", "Tu Youyou (1972) read a 4th-century recipe that said to soak wormwood in cold water, not boil it, extracted it with cold ether, and found the most important antimalarial of modern times. Nobel Prize, 2015.", "Artemisinin", id=0)
X("K2PtCl4", "Potassium Tetrachloroplatinate", "K2PtCl4", "Solid", "A red salt, the usual source of platinum for platinum complexes.", "Potassium_tetrachloroplatinate", id=0, color="#c84028")
X("Cisplatin", "Cisplatin", "PtCl2(NH3)2", "Solid", "Barnett Rosenberg (1965) saw bacteria stop dividing near platinum electrodes and traced it to this compound. Approved in 1978, it turned testicular cancer from a killer into a curable disease.", "Cisplatin", id=0, color="#f0e040")
X("CoffeeBeans", "Green Coffee Beans", "mixture", "Solid", "Raw coffee, about 1% caffeine by weight.", "Coffee_bean", id=0, balance="C")
L("Caffeine", "Caffeine", "C8H10N4O2", "Solid")
X("ClO", "Chlorine Monoxide", "ClO", "Gas", "The radical that eats the ozone layer. Rowland and Molina (1974) showed CFCs release chlorine high in the stratosphere; each atom destroys thousands of ozone molecules. Nobel Prize, 1995.", "Chlorine_monoxide", id=0)
X("SolarCell", "Silicon Solar Cell", "Si", "Solid", "A p-n junction that turns light into current: Chapin, Fuller and Pearson at Bell Labs (1954). Solar is now the cheapest electricity in history.", "Solar_cell", id=0, balance="Si2", color="#203060")
X("Microchip", "Microprocessor", "Si", "Solid", "Kilby and Noyce invented the integrated circuit in 1958-59; the Intel 4004 (1971) put a whole computer's processor on one chip, with 2,300 transistors. Today's chips have tens of billions.", "Microprocessor", id=0, balance="Si3Cu", color="#3a6a40")
X("GoreTex", "Gore-Tex", "(C2F4)n", "Solid", "Bob Gore (1969) yanked a heated rod of PTFE in frustration and it stretched 800% into a porous membrane that lets vapour out and keeps rain off.", "Gore-Tex", id=0, balance="C2F4")

E6 = Epoch("Frontier", "1970 to today", [
    R("Supercritical Decaf", "CoffeeBeans + CO2 -> Caffeine", PRESS,
      "Kurt Zosel (1970) found carbon dioxide above its critical point dissolves caffeine but not flavour. No toxic solvent: the beans are simply depressurised.",
      wiki="Decaffeination#Supercritical_carbon_dioxide_process", T=60, P=250, exact=False, dh=0),
    R("Gore-Tex", "PTFE -> GoreTex", HEAT,
      "Heated PTFE, stretched fast, becomes a web of fibrils with nine billion pores per square inch.",
      wiki="Gore-Tex#History", T=300, exact=False, dh=0),
    R("Ozone Hole Chemistry", "CCl2F2 + O3 -> ClO + O2", LIGHT,
      "Hard ultraviolet splits CFCs in the stratosphere; the chlorine attacks ozone. The Montreal Protocol (1987) banned them, and the Antarctic ozone hole is slowly healing.",
      wiki="Ozone_depletion", exact=False, dh=0),
    R("Tu Youyou's Extraction", "Wormwood + Ether -> Artemisinin", MIX,
      "A cold ether extract of sweet wormwood cured malaria in mice and monkeys in 1971. Artemisinin combination therapies have saved millions of lives.",
      wiki="Artemisinin#History", exact=False, dh=0),
    R("Platinum Salt", "Pt + Cl2 + 2 KCl -> K2PtCl4", HEAT,
      "Platinum chlorinated in the presence of potassium chloride.",
      wiki="Potassium_tetrachloroplatinate", T=300, dh=-500),
    R("Cisplatin", "K2PtCl4 + 2 NH3 -> Cisplatin + 2 KCl", MIX,
      "Two ammonias swap in for two chlorides, on the same side of the platinum.",
      wiki="Cisplatin#Synthesis", dh=-50),
    R("Laser-Blasted Fullerenes", "60 Graphite -> C60", LIGHT,
      "A pulsed laser vaporising graphite into helium (Rice University, 1985) made carbon clusters that peaked sharply at 60 atoms.",
      wiki="Buckminsterfullerene#History", exact=True, dh=2500),
    R("Growing Nanotubes", "Methane -> CNT + 2 H2", CAT,
      "Methane cracked over iron nanoparticles grows forests of carbon nanotubes.",
      wiki="Synthesis_of_carbon_nanotubes", cat="Fe", T=900, dh=75),
    R("Scotch Tape Graphene", "Graphite -> Graphene", MIX,
      "Press sticky tape on graphite, peel, fold, peel again until a flake is one atom thick.",
      wiki="Graphene#History", dh=0),
    R("Plasma Diamond", "Methane -> CVDDiamond + 2 H2", ELEC,
      "Methane in hydrogen, broken up in a microwave plasma, deposits diamond on a substrate.",
      wiki="Chemical_vapor_deposition_of_diamond", T=900, dh=75),
    R("YBCO Ceramic", "2 Y2O3 + 8 BaCO3 + 12 CuO + O2 -> 4 YBCO + 8 CO2", HEAT,
      "The oxides ground together and fired at 950 C, then annealed in oxygen.",
      wiki="Yttrium_barium_copper_oxide#Synthesis", T=950, dh=500),
    R("Goodenough's Cathode", "2 Li2CO3 + 4 CoO + O2 -> 4 LiCoO2 + 2 CO2", HEAT,
      "Lithium carbonate and cobalt oxide fired in air.",
      wiki="Lithium_cobalt_oxide#Preparation", T=900, dh=-100),
    R("Lithium-Ion Cell", "LiCoO2 + Graphite -> LiIonCell", MIX,
      "A cobalt oxide cathode and a graphite anode with a lithium salt electrolyte between them.",
      wiki="Lithium-ion_battery#History", exact=False, dh=0),
    R("Iron Phosphate Cathode", "Li2CO3 + 2 FePO4 + Charcoal -> 2 LiFePO4 + 2 CO2", HEAT,
      "Carbothermal reduction: carbon reduces the iron to iron(II) as lithium moves in, and leaves a conductive coat.",
      wiki="Lithium_iron_phosphate#Synthesis", T=700, exact=False, dh=100),
    R("Opening Monazite", "Monazite + 3 HCl -> NdCl3 + H3PO4", HEAT,
      "The rare earths are leached out of monazite sand with acid; solvent extraction then separates them, which takes hundreds of stages.",
      wiki="Monazite#Rare_earth_extraction", T=150, dh=-50),
    R("Neodymium Metal", "2 NdCl3 -> 2 Nd + 3 Cl2", ELEC,
      "Molten-salt electrolysis frees neodymium metal.",
      wiki="Neodymium#Production", T=1000, dh=2000),
    R("Sagawa's Magnet", "2 Nd + 14 Fe + B -> NdFeB", SMELT,
      "Neodymium, iron and boron melted, powdered, aligned in a magnetic field and sintered.",
      wiki="Neodymium_magnet#History", T=1100, dh=-100),
    R("Gallium Nitride", "2 Ga + 2 NH3 -> 2 GaN + 3 H2", HEAT,
      "Gallium and ammonia at 1000 C; Amano and Akasaki's trick was a low-temperature buffer layer on sapphire.",
      wiki="Gallium_nitride#Synthesis", T=1000, dh=-200),
    R("The Blue LED", "GaN + In -> BlueLED", HEAT,
      "Nakamura's InGaN quantum wells (Nichia, 1993) glowed bright blue at last, after thirty years of failed attempts.",
      wiki="Light-emitting_diode#Blue_and_white_LEDs", exact=False, dh=0),
    R("Golden Rain", "PbNO32 + 2 KI -> PbI2 + 2 KNO3", MIX,
      "Two clear solutions mix into a bright yellow precipitate; dissolved hot and cooled, it falls as glittering golden flakes.",
      wiki="Lead(II)_iodide#Preparation", dh=-50),
    R("Hydrogen Iodide", "H2 + I2 -> 2 HI", HEAT,
      "Hydrogen and iodine vapour combine at 400 C, a classic equilibrium that Bodenstein studied in 1894.",
      wiki="Hydrogen_iodide#Synthesis", T=400, dh=53),
    R("Methylamine", "Methanol + NH3 -> Methylamine + H2O", CAT,
      "Methanol and ammonia over an alumina catalyst.",
      wiki="Methylamine#Production", cat="Alumina", T=400, dh=-20),
    R("Methylammonium Iodide", "Methylamine + HI -> MAI", MIX,
      "Methylamine neutralised with hydroiodic acid.",
      wiki="Methylammonium_lead_halide", dh=-80),
    R("Perovskite Film", "PbI2 + MAI -> Perovskite", MIX,
      "Lead iodide and methylammonium iodide spin-coated from solution crystallise into a perovskite film at room temperature.",
      wiki="Perovskite_solar_cell#History", dh=-20),
    R("Quantum Dots", "Cd + Se -> CdSe", HEAT,
      "Bawendi's hot injection (1993): cadmium and selenium precursors shot into a hot solvent nucleate all at once, giving dots of one size.",
      wiki="Quantum_dot#Production", T=300, dh=-145),
    R("Yaghi's MOF-5", "4 ZnNO32 + 3 TPA + H2O -> MOF5 + 8 HNO3", HEAT,
      "Zinc nitrate and terephthalic acid heated in a solvent self-assemble into cubic crystals of MOF-5.",
      wiki="MOF-5", T=100, dh=-50),
    R("Ruthenium Chloride", "2 Ru + 3 Cl2 -> 2 RuCl3", HEAT,
      "Ruthenium burns in chlorine at 700 C.",
      wiki="Ruthenium(III)_chloride", T=700, dh=-400),
    R("Grubbs Catalyst", "RuCl3 + Styrene -> Grubbs", MIX,
      "Ruthenium chloride, phosphine ligands and a carbene source give the air-stable metathesis catalyst.",
      wiki="Grubbs_catalyst#First-generation_Grubbs_catalyst", exact=False, dh=0),
    R("Olefin Metathesis", "Ethylene + 2-Butene -> 2 Propylene", CAT,
      "The catalyst swaps the partners of two double bonds, like dancers changing partners (Chauvin's mechanism). Run this way it turns ethylene and butene into propylene, as the Lummus OCT plants do.",
      wiki="Olefin_metathesis", cat="Grubbs", T=40, dh=5),
    R("Boronic Acid", "PhMgBr + H3BO3 -> PhB(OH)2", MIX,
      "A Grignard reagent attacks a borate ester; hydrolysis leaves phenylboronic acid.",
      wiki="Phenylboronic_acid#Synthesis", exact=False, dh=-100),
    R("Suzuki Coupling", "Bromobenzene + PhB(OH)2 + NaOH -> Biphenyl + NaBr + H3BO3", CAT,
      "Akira Suzuki (1979) joined an aryl halide to a boronic acid with palladium. The workhorse carbon-carbon bond of drug chemistry. Nobel Prize, 2010.",
      wiki="Suzuki_reaction", cat="Pd", T=80, dh=-200),
    R("Isobutylbenzene", "Toluene + Propylene -> Isobutylbenzene", CAT,
      "Side-chain alkylation of toluene with propylene over a sodium catalyst.",
      wiki="Isobutylbenzene", cat="Na", T=150, dh=-100),
    R("BHC Acylation", "Isobutylbenzene + AceticAnhydride -> IBAP + AcOH", CAT,
      "The BHC process (1992) acylates with hydrogen fluoride as catalyst and solvent, recycled almost completely.",
      wiki="Ibuprofen#Synthesis", cat="HF", T=80, dh=-80),
    R("BHC Hydrogenation", "IBAP + H2 -> IBPE", CAT,
      "The ketone hydrogenated to an alcohol over nickel.",
      wiki="Ibuprofen#Synthesis", cat="Ni", T=70, dh=-60),
    R("BHC Ibuprofen", "IBPE + CO -> Ibuprofen", CAT,
      "Palladium-catalysed carbonylation finishes ibuprofen in three steps instead of the original six, with almost no waste: a landmark of green chemistry.",
      wiki="Green_chemistry#Examples", cat="Pd", T=130, P=50, dh=-120),
    R("Lactic Fermentation", "Lactose + H2O -> 4 LacticAcid", MIX,
      "Lactic acid bacteria ferment milk sugar: the sourness of yoghurt, and the feedstock of PLA.",
      wiki="Lactic_acid_fermentation", dh=-200),
    R("Lactide", "2 LacticAcid -> Lactide + 2 H2O", HEAT,
      "Lactic acid condensed and cracked into its cyclic dimer, lactide.",
      wiki="Lactide", T=200, dh=50),
    R("PLA", "Lactide -> 2 PLA", POLY,
      "Tin-catalysed ring-opening polymerisation turns lactide into polylactic acid.",
      wiki="Polylactic_acid#Production", T=180, dh=-20),
    R("CO2 to Methanol", "CO2 + 3 H2 -> Methanol + H2O", PRESS,
      "Carbon Recycling International (2012) turns captured CO2 and green hydrogen into methanol over copper-zinc oxide: George Olah's 'methanol economy'.",
      wiki="Methanol_economy", T=250, P=50, dh=-49),
    R("Silicon Solar Cell", "PSi + NSi -> SolarCell", LIGHT,
      "A p-n junction in sunlight: the Bell Labs solar battery of 1954 was 6% efficient. Panels now pass 22% and cost a hundredth as much.",
      wiki="Solar_cell#History", exact=False, dh=0),
    R("The Microprocessor", "Transistor + Wafer + Cu -> Microchip", LIGHT,
      "Photolithography prints billions of transistors and their copper wiring onto a wafer in hundreds of light, etch and deposit steps.",
      wiki="Photolithography", exact=False, dh=0),
    # --- the superheavy elements ---
    R("Rutherfordium", "Cf + Graphite -> Rf", LIGHT,
      "Carbon ions on californium (Ghiorso, Berkeley, 1969); Dubna claimed it in 1964. The two labs argued over names for thirty years.",
      wiki="Rutherfordium#History", exact=False, dh=0),
    R("Dubnium", "Cf + N2 -> Db", LIGHT,
      "Nitrogen ions on californium (Berkeley, 1970), named for Dubna in the truce of 1997.",
      wiki="Dubnium#History", exact=False, dh=0),
    R("Seaborgium", "Cf + O2 -> Sg", LIGHT,
      "Oxygen-18 ions on californium (1974). Glenn Seaborg became the first person to have an element named after him while alive.",
      wiki="Seaborgium#History", exact=False, dh=0),
    R("Bohrium", "Bi + Cr -> Bh", LIGHT,
      "Chromium on bismuth at GSI Darmstadt (1981): cold fusion of heavy ions, one atom at a time.",
      wiki="Bohrium#History", exact=False, dh=0),
    R("Meitnerium", "Bi + Fe -> Mt", LIGHT,
      "Iron on bismuth (GSI, 1982): a single atom. Named for Lise Meitner, who explained nuclear fission.",
      wiki="Meitnerium#History", exact=False, dh=0),
    R("Hassium", "Pb + Fe -> Hs", LIGHT,
      "Iron on lead (GSI, 1984), named for the state of Hesse.",
      wiki="Hassium#History", exact=False, dh=0),
    R("Darmstadtium", "Pb + Ni -> Ds", LIGHT,
      "Nickel on lead (GSI, 1994).",
      wiki="Darmstadtium#History", exact=False, dh=0),
    R("Roentgenium", "Bi + Ni -> Rg", LIGHT,
      "Nickel on bismuth (GSI, 1994), named for the discoverer of X-rays.",
      wiki="Roentgenium#History", exact=False, dh=0),
    R("Copernicium", "Pb + Zn -> Cn", LIGHT,
      "Zinc on lead (GSI, 1996). Relativistic effects may make it a volatile liquid metal.",
      wiki="Copernicium#History", exact=False, dh=0),
    R("Nihonium", "Bi + Zn -> Nh", LIGHT,
      "Zinc on bismuth at RIKEN (2004-2012): three atoms in nine years of beam time. The first element discovered in Asia.",
      wiki="Nihonium#History", exact=False, dh=0),
    R("Flerovium", "Pu + Ca -> Fl", LIGHT,
      "Calcium-48 on plutonium (Dubna, 1998), the first of the 'island of stability' hunts.",
      wiki="Flerovium#History", exact=False, dh=0),
    R("Livermorium", "Cm + Ca -> Lv", LIGHT,
      "Calcium-48 on curium (Dubna and Livermore, 2000).",
      wiki="Livermorium#History", exact=False, dh=0),
    R("Oganesson", "Cf + Ca -> Og", LIGHT,
      "Calcium-48 on californium (Dubna, 2002-2005): five atoms so far. Element 118 completes the seventh row of the periodic table.",
      wiki="Oganesson#History", exact=False, dh=0),
    R("Moscovium", "Am + Ca -> Mc", LIGHT,
      "Calcium-48 on americium (Dubna, 2003).",
      wiki="Moscovium#History", exact=False, dh=0),
    R("Tennessine", "Bk + Ca -> Ts", LIGHT,
      "Calcium-48 on berkelium made at Oak Ridge (Dubna, 2010): the last element discovered so far.",
      wiki="Tennessine#History", exact=False, dh=0),
])

# --- loose ends: raw materials and the reactions that make catalysts ---
X("PlatinumOre", "Platina", "Pt(Pd,Rh,Ir,Os,Ru)", "Solid", "Native platinum grains from the rivers of Colombia, which Spanish miners called platina, 'little silver', and threw back. It carries all six platinum-group metals.", "Platinum#History", id=0, balance="Pt", color="#b8bcc0")
X("Sphalerite", "Zinc Blende", "ZnS", "Solid", "Zinc sulfide, the main ore of zinc. Reich and Richter (1863) found a brilliant indigo line in the spectrum of a Freiberg blende: indium.", "Sphalerite", id=0, color="#6a4a2a")
X("Clove", "Clove Oil", "mixture", "Liquid", "Oil distilled from the dried flower buds of the clove tree, about 85% eugenol.", "Clove", id=0, balance="C")
E3.reactions += [
    R("Antimony Pentachloride", "2 Sb + 5 Cl2 -> 2 SbCl5", HEAT,
      "Antimony burns in chlorine to a fuming liquid, later Frederic Swarts' fluorination catalyst.",
      wiki="Antimony_pentachloride", T=200, dh=-880),
]
E4.reactions += [
    R("Reich and Richter's Indium", "Sphalerite + HCl -> In", MIX,
      "Searching zinc blende for thallium with a spectroscope (1863), Reich and Richter saw an indigo line no element had shown before. Richter, unlike the colour-blind Reich, could see it.",
      wiki="Indium#History", exact=False, dh=0),
    R("Distilling Clove Oil", "Clove -> Eugenol", DISTIL,
      "Steam distillation of clove oil gives nearly pure eugenol, the smell of the dentist's surgery.",
      wiki="Eugenol", exact=False, dh=0),
]

X("DriedBlood", "Dried Blood", "mixture", "Solid", "Slaughterhouse blood, dried: the nitrogen and carbon source from which 18th-century chemists fused yellow prussiate with potash and iron.", "Potassium_ferrocyanide#History", id=0, balance="C")
L("KBrO3", "Potassium bromate", "KBrO3", "Solid")
L("KIO3", "Potassium iodate", "KIO3", "Solid")
E3.reactions += [
    R("Fusing Blood Lye", "DriedBlood + Potash + Fe -> Prussiate", HEAT,
      "Dried blood fused with potash in an iron pot, then leached with water: yellow crystals of potassium ferrocyanide, the source of Prussian blue for a century.",
      wiki="Potassium_ferrocyanide#History", T=800, exact=False, dh=0),
    R("Bromine in Potash", "3 Br2 + 6 KOH -> 5 KBr + KBrO3 + 3 H2O", HEAT,
      "Bromine dissolved in hot potash lye gives potassium bromide (and a little bromate). Victorian doctors prescribed the bromide as a sedative.",
      wiki="Potassium_bromide#History", T=80, dh=-300),
    R("Iodine in Potash", "3 I2 + 6 KOH -> 5 KI + KIO3 + 3 H2O", HEAT,
      "Iodine in hot potash lye gives potassium iodide, the salt added to table salt against goitre.",
      wiki="Potassium_iodide#Production", T=80, dh=-200),
]
E5.reactions += [
    R("Platforming", "Naphtha -> Benzene + Toluene + pXylene + H2", CAT,
      "Vladimir Haensel's platinum reforming (UOP, 1949) turns straight-chain naphtha into high-octane aromatics and hydrogen. It is where most benzene, toluene and xylenes now come from.",
      wiki="Catalytic_reforming", cat="Pt", T=500, exact=False, dh=200),
    R("Cracking Butane", "Butane -> 2-Butene + H2", HEAT,
      "Butane dehydrogenated by heat gives butenes.",
      wiki="Butene", T=650, dh=115),
    R("Iron Phosphate", "FeCl3 + H3PO4 -> FePO4 + 3 HCl", MIX,
      "Phosphoric acid precipitates pale iron(III) phosphate from ferric chloride solution.",
      wiki="Iron(III)_phosphate", dh=-30),
]

# ======================================================================================
# NATURE'S CHEMISTRY: plants, animals and minerals the chemists took apart
# ======================================================================================
def RAW(key, name, desc, wiki, color=None, formula="mixture", state="Solid"):
    X(key, name, formula, state, desc, wiki, id=0, balance="C" if formula == "mixture" else None,
      color=color)

RAW("Wine", "Wine", "Fermented grape juice, about 12% alcohol. Distilled in the alembics of 12th-century Salerno it gave aqua vitae, the 'water of life'.", "Wine", "#7a1830", state="Liquid")
RAW("Lavender", "Lavender", "Lavandula flowers, steam-distilled since Roman bath-houses for an oil rich in linalool and linalyl acetate.", "Lavandula", "#9a80c8")
RAW("Peppermint", "Peppermint", "Mentha x piperita, a natural hybrid of watermint and spearmint, whose oil is about 40% menthol.", "Peppermint", "#3a9a50")
RAW("Spearmint", "Spearmint", "Mentha spicata. Its oil is mostly (R)-carvone; the mirror-image molecule smells of caraway instead.", "Spearmint", "#4aaa5a")
RAW("OrangePeel", "Orange Peel", "The rind of the sweet orange, whose oil glands burst with limonene when squeezed.", "Orange_oil", "#f08020")
RAW("Cinnamon", "Cinnamon Bark", "The inner bark of Cinnamomum trees, once worth more than gold by weight; its warmth is cinnamaldehyde.", "Cinnamon", "#a0582a")
RAW("Rose", "Rose Petals", "Damask rose petals: it takes about four tonnes of them to distil a kilogram of attar of roses.", "Rose_oil", "#d84868")
RAW("PineResin", "Pine Resin", "The sticky sap that oozes from wounded pine bark. Distilled, it splits into turpentine and rosin.", "Resin", "#d8a840")
RAW("Anise", "Aniseed", "Seeds of Pimpinella anisum, flavour of ouzo, pastis and sambuca, all from anethole.", "Anise", "#a89060")
RAW("Thyme", "Thyme", "Thymus vulgaris; its oil's thymol was the antiseptic of 19th-century hospitals and is still in mouthwash.", "Thyme", "#6a8a50")
RAW("Jasmine", "Jasmine Flowers", "Picked at night when their scent peaks; the absolute is rich in benzyl acetate.", "Jasmine", "#f8f4e0")
RAW("OakGalls", "Oak Galls", "Hard swellings that oaks grow around wasp larvae, packed with tannins. Crushed with green vitriol they made the black ink of a thousand years of manuscripts.", "Oak_apple", "#8a6a40")
RAW("Argol", "Wine Lees", "The crust that crystallises inside wine casks, mostly potassium bitartrate: cream of tartar.", "Potassium_bitartrate", "#c8b0b0")
RAW("Lemons", "Lemon Juice", "About 6% citric acid. The Royal Navy's lemon rations, from 1795, ended scurvy aboard its ships.", "Lemon", "#f0e040", state="Liquid")
RAW("Apples", "Apple Juice", "Sour with malic acid, named from the Latin malum, apple.", "Apple", "#c8d040", state="Liquid")
RAW("Amber", "Amber", "Fossilised tree resin. Georgius Agricola (1546) distilled it and collected 'salt of amber', succinic acid.", "Amber", "#e8a020")
RAW("Ants", "Red Ants", "Wood ants spray formic acid in defence. John Ray distilled a mass of dead ants in 1671 and isolated it.", "Formica_rufa", "#802018")
RAW("Butter", "Butter", "Mostly milk fat, whose short-chain acids (butyric, caproic) give rancid butter its smell.", "Butter", "#f8e080")
RAW("Gelatin", "Gelatin", "Boiled-down collagen from bones and skin. Henri Braconnot (1820) boiled it with sulfuric acid and got a sweet crystalline substance: glycine.", "Gelatin", "#f0e0b0")
RAW("Cheese", "Cheese", "Concentrated milk protein, casein. Proust found leucine in it (1818); Liebig found tyrosine, from the Greek tyros, cheese (1846).", "Cheese", "#f0c850")
RAW("Asparagus", "Asparagus Juice", "Vauquelin and Robiquet (1806) crystallised asparagine from it: the first amino acid ever isolated.", "Asparagus", "#78a048", state="Liquid")
RAW("WillowBark", "Willow Bark", "Chewed for pain and fever since ancient Sumer and Egypt; Edward Stone reported its effect on agues to the Royal Society in 1763.", "Willow#Medicinal_uses", "#8a7050")
RAW("Cinchona", "Cinchona Bark", "Jesuits' bark from the Andes, the only remedy for malaria for three centuries.", "Cinchona", "#a0502a")
RAW("TeaLeaves", "Tea Leaves", "Camellia sinensis; about 3% caffeine by dry weight, more than coffee beans.", "Tea", "#4a6a30")
RAW("Cocoa", "Cocoa Beans", "The seeds of Theobroma cacao, 'food of the gods'; their stimulant is theobromine.", "Cocoa_bean", "#5a3020")
RAW("Tobacco", "Tobacco Leaves", "Nicotiana tabacum, named for Jean Nicot who sent it to the French court in 1560.", "Tobacco", "#8a6a30")
RAW("Turmeric", "Turmeric Root", "The golden rhizome of Curcuma longa, a dye and spice for four thousand years.", "Turmeric", "#e8a010")
RAW("Belladonna", "Deadly Nightshade", "Atropa belladonna: Venetian women dropped its juice in their eyes to dilate the pupils, hence 'beautiful lady'.", "Atropa_belladonna", "#3a2040")
RAW("Foxglove", "Foxglove Leaves", "Digitalis purpurea. William Withering (1785) learned from a folk remedy that it treated dropsy, and described how to dose it.", "Digitalis", "#c060a0")
RAW("TonkaBeans", "Tonka Beans", "Black, wrinkled seeds that smell of vanilla and new-mown hay: coumarin, isolated by Vogel in 1820.", "Tonka_bean", "#2a1a10")
RAW("BitterAlmonds", "Bitter Almonds", "Their oil, mostly benzaldehyde, led Liebig and Wohler (1832) to the benzoyl radical, a group of atoms that passes intact through reactions.", "Bitter_almond", "#d8c0a0")
RAW("GumBenzoin", "Gum Benzoin", "A balsamic resin from Styrax trees. Sublimed, it gives flowers of benzoin, benzoic acid (Nostradamus described it in 1556).", "Benzoin_(resin)", "#c89060")
RAW("Starch", "Potato Starch", "Long chains of glucose. Konstantin Kirchhoff (1811) boiled starch with dilute acid and got glucose syrup.", "Starch", "#f8f8f0")
RAW("PalmOil", "Palm Oil", "Pressed from the fruit of the oil palm; rich in tripalmitin.", "Palm_oil", "#e86020", formula="C51H98O6")
RAW("Gadolinite", "Gadolinite", "A black mineral from Ytterby, Sweden, a village that gave its name to four elements. Johan Gadolin found a new earth, yttria, in it in 1794.", "Gadolinite", "#2a2a2a")
RAW("Cerite", "Cerite", "A reddish silicate from Bastnas, Sweden, in which Berzelius and Hisinger found ceria (1803), named for the new asteroid Ceres.", "Cerite", "#a05050")
RAW("Samarskite", "Samarskite", "A black rare-earth mineral named for a Russian mine official, Colonel Samarsky: the first person to have an element (samarium) named after him, indirectly.", "Samarskite", "#202020")
RAW("Beryl", "Beryl", "Beryllium aluminium silicate: emerald and aquamarine are beryl. Vauquelin found a new earth in it in 1798.", "Beryl", "#60c0a0")
RAW("Thorite", "Thorite", "A thorium silicate from Norway in which Berzelius found thorium (1829), named for Thor.", "Thorite", "#3a3020")
RAW("Lepidolite", "Lepidolite", "A lilac lithium mica. Bunsen and Kirchhoff (1861) saw two new deep-red lines in its spectrum: rubidium, from rubidus, deep red.", "Lepidolite", "#b090c0")
RAW("MineralWater", "Durkheim Mineral Water", "Bunsen evaporated 44,000 litres of it (1860) and found two blue spectral lines no known element made: caesium, from caesius, sky blue.", "Caesium#History", "#90c0e0", state="Liquid")
RAW("Argyrodite", "Argyrodite", "A silver germanium sulfide from Freiberg in which Clemens Winkler (1886) found germanium, the 'eka-silicon' Mendeleev had predicted.", "Argyrodite", "#505058")
RAW("Vanadinite", "Vanadinite", "Bright red-orange lead vanadate crystals. Del Rio found vanadium in it in 1801, was talked out of it, and Sefstrom rediscovered it in 1830.", "Vanadinite", "#d04020")
RAW("Zircon", "Zircon", "Zirconium silicate, among the oldest minerals on Earth (4.4 billion years). Klaproth found zirconia in it in 1789.", "Zircon", "#c08040", formula="ZrSiO4")
RAW("Columbite", "Columbite", "An iron niobium-tantalum oxide. Hatchett found 'columbium' in a sample from Connecticut (1801); Ekeberg found tantalum in a similar ore (1802).", "Columbite", "#2a2a30")

L("Linalool", "(±)-Linalool", "C10H18O", "Liquid", name="Linalool", rename=True)
L("LinalylAcetate", "Linalyl acetate", "C12H20O2", "Liquid")
L("Menthol", "Menthol", "C10H20O", "Solid")
L("Menthone", "(-)-Menthone", "C10H18O", "Liquid", name="Menthone", rename=True)
L("Carvone", "(-)-Carvone", "C10H14O", "Liquid", name="Carvone", rename=True)
L("Limonene", "Limonene", "C10H16", "Liquid")
L("Cinnamaldehyde", "Cinnamaldehyde", "C9H8O", "Liquid")
L("Citronellol", "Citronellol", "C10H20O", "Liquid")
L("Pinene", "(-)-α-Pinene", "C10H16", "Liquid", name="alpha-Pinene", rename=True)
L("Anethole", "Anethole", "C10H12O", "Solid")
L("Thymol", "Thymol", "C10H14O", "Solid")
L("BenzylAcetate", "Benzyl acetate", "C9H10O2", "Liquid")
L("GallicAcid", "Gallic acid", "C7H6O5", "Solid", props=["IsAcid"])
X("IronGallInk", "Iron Gall Ink", "mixture", "Liquid", "Gallic acid and tannins with iron(II) sulfate: pale when written, darkening to permanent black as it oxidises in air. The Dead Sea Scrolls, Leonardo's notebooks and the US Constitution are written in it.", "Iron_gall_ink", id=0, balance="C", color="#101018")
L("Bitartrate", "Potassium bitartrate", "KC4H5O6", "Solid", name="Cream of Tartar", rename=True)
X("Tartaric", "Tartaric Acid", "C4H6O6", "Solid", "The acid of grapes. Scheele isolated it in 1769; Pasteur (1848) sorted its salt's crystals by hand with tweezers into left- and right-handed forms, discovering molecular chirality.", "Tartaric_acid", id=0, props=["IsAcid"])
L("Citric", "Citric acid", "C6H8O7", "Solid", props=["IsAcid"])
L("Malic", "Malic acid", "C4H6O5", "Solid", props=["IsAcid"])
L("Succinic", "Succinic acid", "C4H6O4", "Solid", props=["IsAcid"])
L("Formic", "Formic acid", "CH2O2", "Liquid", props=["IsAcid"])
L("Oxalic", "Oxalic acid", "C2H2O4", "Solid", props=["IsAcid"])
L("Butyric", "Butyric acid", "C4H8O2", "Liquid", props=["IsAcid"])
L("Hexanoic", "Hexanoic acid", "C6H12O2", "Liquid", props=["IsAcid"])
L("Glycine", "Glycine", "C2H5NO2", "Solid")
L("Leucine", "L-Leucine", "C6H13NO2", "Solid", name="Leucine", rename=True)
L("Tyrosine", "L-Tyrosine", "C9H11NO3", "Solid", name="Tyrosine", rename=True)
L("Asparagine", "Asparagine", "C4H8N2O3", "Solid")
L("Quinine", "Quinine", "C20H24N2O2", "Solid")
L("Theobromine", "Theobromine", "C7H8N4O2", "Solid")
L("Nicotine", "Nicotine", "C10H14N2", "Liquid")
L("Curcumin", "Curcumin", "C21H20O6", "Solid")
L("Atropine", "(-)-Atropine", "C17H23NO3", "Solid", name="Atropine", rename=True)
L("Digitoxin", "Digitoxin", "C41H64O13", "Solid")
L("Coumarin", "Coumarin", "C9H6O2", "Solid")
L("Benzaldehyde", "Benzaldehyde", "C7H6O", "Liquid")
X("BenzoicAcid", "Benzoic Acid", "C7H6O2", "Solid", "The simplest aromatic acid, sublimed from gum benzoin since the 16th century. A food preservative (E210) and the acid of the benzoyl radical.", "Benzoic_acid", id=0, props=["IsAcid"])
L("BenzylAlcohol", "Benzyl alcohol", "C7H8O", "Liquid")
L("BenzylChloride", "Benzyl chloride", "C7H7Cl", "Liquid")
X("CinnamicAcid", "Cinnamic Acid", "C9H8O2", "Solid", "The acid of cinnamon and storax, made by Perkin's reaction (1868) from benzaldehyde and acetic anhydride.", "Cinnamic_acid", id=0, props=["IsAcid"])
X("Turpentine", "Turpentine", "C10H16", "Liquid", "Spirit of turpentine, mostly pinenes: the painters' solvent and, in the 19th century, a remedy for almost everything.", "Turpentine", id=0)
X("Rosin", "Rosin", "C20H30O2", "Solid", "Colophony, the glassy residue of distilled pine resin, mostly abietic acid. Violinists rub it on their bows.", "Rosin", id=0, color="#c87820")
X("Salicin", "Salicin", "C13H18O7", "Solid", "The bitter glucoside of willow bark (Leroux, 1828). Raffaele Piria (1838) split it and oxidised the fragment to salicylic acid.", "Salicin", id=0)
X("StearicAcid", "Stearic Acid", "C18H36O2", "Solid", "Chevreul's 'stearin', the hard waxy acid of tallow. Stearin candles (1825) burned brighter and without the stink of tallow.", "Stearic_acid", id=0, props=["IsAcid"])
L("OleicAcid", "Oleic acid", "C18H34O2", "Liquid", props=["IsAcid"])
L("LauricAcid", "Lauric acid", "C12H24O2", "Solid", props=["IsAcid"])
L("PalmiticAcid", "Palmitic acid", "C16H32O2", "Solid", props=["IsAcid"])
L("IsoamylAlcohol", "Isoamyl alcohol", "C5H12O", "Liquid")
L("Isopropanol", "Isopropanol", "C3H8O", "Liquid")
L("Propanol", "1-Propanol", "C3H8O", "Liquid")
L("Isobutanol", "Isobutanol", "C4H10O", "Liquid")
L("Propanal", "Propanal", "C3H6O", "Liquid")
L("Butanal", "Butanal", "C4H8O", "Liquid")
L("Isobutyraldehyde", "Isobutyraldehyde", "C4H8O", "Liquid")
X("Butanol", "1-Butanol", "C4H10O", "Liquid", "Butyl alcohol. Chaim Weizmann's bacterial fermentation (1916) made acetone for British cordite and butanol as the by-product; his reward helped bring about the Balfour Declaration.", "1-Butanol", id=0)
L("Propionic", "Propionic acid", "C3H6O2", "Liquid", props=["IsAcid"])
L("Propylamine", "Propylamine", "C3H9N", "Liquid", props=["IsBase"])
L("Ethylamine", "Ethylamine", "C2H7N", "Gas", props=["IsBase"])
L("Acetanilide", "Acetanilide", "C8H9NO", "Solid")
L("Phenacetin", "Phenacetin", "C10H13NO2", "Solid")
L("PhenylSalicylate", "Phenyl salicylate", "C13H10O3", "Solid")
X("Salicylaldehyde", "Salicylaldehyde", "C7H6O2", "Liquid", "2-Hydroxybenzaldehyde, the scent of meadowsweet. Reimer and Tiemann made it from phenol and chloroform (1876).", "Salicylaldehyde", id=0)
L("MethylAnthranilate", "Methyl anthranilate", "C8H9NO2", "Liquid")
L("Hexamine", "Hexamethylenetetramine", "C6H12N4", "Solid")
L("Furfural", "Furfural", "C5H4O2", "Liquid")
X("Bran", "Oat Hulls", "mixture", "Solid", "The husks of oats, full of pentose sugars. Quaker Oats made furfural from them from 1921.", "Furfural#Production", id=0, balance="C")
L("Furan", "Furan", "C4H4O", "Liquid")
L("Acrolein", "Acrolein", "C3H4O", "Liquid")
L("Pyridine", "Pyridine", "C5H5N", "Liquid")
X("Alanine", "Alanine", "C3H7NO2", "Solid", "The simplest chiral amino acid. Adolph Strecker made it from acetaldehyde, ammonia and hydrogen cyanide in 1850: the first laboratory synthesis of an amino acid.", "Alanine", id=0)
L("Hydroquinone", "Hydroquinone", "C6H6O2", "Solid")
L("2-Nitrophenol", "2-Nitrophenol", "C6H5NO3", "Solid")
L("Triacetin", "Triacetin", "C9H14O6", "Liquid")
L("EthylAcetate", "Ethyl acetate", "C4H8O2", "Liquid")
L("MethylAcetate", "Methyl acetate", "C3H6O2", "Liquid")
L("PropylAcetate", "Propyl acetate", "C5H10O2", "Liquid")
L("IsopropylAcetate", "Isopropyl acetate", "C5H10O2", "Liquid")
L("IsoamylAcetate", "Isoamyl acetate", "C7H14O2", "Liquid")
L("IsobutylAcetate", "Isobutyl acetate", "C6H12O2", "Liquid")
L("ButylAcetate", "Butyl acetate", "C6H12O2", "Liquid")
L("MenthylAcetate", "(±)-Menthyl acetate", "C12H22O2", "Liquid", name="Menthyl Acetate", rename=True)
L("MethylFormate", "Methyl formate", "C2H4O2", "Liquid")
L("EthylFormate", "Ethyl formate", "C3H6O2", "Liquid")
L("EthylPropionate", "Ethyl propionate", "C5H10O2", "Liquid")
L("MethylButyrate", "Methyl butyrate", "C5H10O2", "Liquid")
L("EthylButyrate", "Ethyl butyrate", "C6H12O2", "Liquid")
L("EthylHexanoate", "Ethyl hexanoate", "C8H16O2", "Liquid")
L("MethylBenzoate", "Methyl benzoate", "C8H8O2", "Liquid")
L("EthylBenzoate", "Ethyl benzoate", "C9H10O2", "Liquid")
L("BenzylBenzoate", "Benzyl benzoate", "C14H12O2", "Liquid")
L("EthylCinnamate", "Ethyl cinnamate", "C11H12O2", "Liquid")
L("MethylCinnamate", "Methyl cinnamate", "C10H10O2", "Solid")
L("MethylSalicylate", "Methyl salicylate", "C8H8O3", "Liquid", name="Oil of Wintergreen (methyl salicylate)", rename=True)
L("DiethylOxalate", "Diethyl oxalate", "C6H10O4", "Liquid")
L("DiethylPhthalate", "Diethyl phthalate", "C12H14O4", "Liquid")
L("DibutylPhthalate", "Dibutyl phthalate", "C16H22O4", "Liquid")
L("EthylAcetoacetate", "Ethyl acetoacetate", "C6H10O3", "Liquid")
L("GeranylAcetate", "Geranyl acetate", "C12H20O2", "Liquid")
L("YNO33", "Yttrium nitrate", "Y(NO3)3", "Solid")
L("LaNO33", "Lanthanum nitrate", "La(NO3)3", "Solid")
L("CeNO33", "Cerium trinitrate", "Ce(NO3)3", "Solid", name="Cerium(III) Nitrate", rename=True)
L("PrNO33", "Praseodymium nitrate", "Pr(NO3)3", "Solid")
L("NdNO33", "Neodymium nitrate", "Nd(NO3)3", "Solid")
L("La2CO33", "Lanthanum carbonate", "La2(CO3)3", "Solid")
L("Ce2CO33", "Cerium carbonate", "Ce2(CO3)3", "Solid")
L("Pr6O11", "Praseodymium oxide (Pr6O11)", "Pr6O11", "Solid", name="Praseodymium Oxide", rename=True)
X("Didymium", "Didymium", "(Pr,Nd)(NO3)3", "Solid", "Mosander's 'twin' of lanthanum (1841), accepted as an element for 44 years, until Carl Auer von Welsbach split it into praseodymium ('green twin') and neodymium ('new twin').", "Didymium", id=0, balance="PrN3O9", color="#b0a0c0")
X("Erbia", "Erbia", "Er2O3", "Solid", "Mosander's rose-pink earth from yttria (1843), which itself hid holmium and thulium.", "Erbium#History", id=0, color="#f0b0c0")
X("Terbia", "Terbia", "Tb4O7", "Solid", "A dark earth Mosander separated from yttria (1843); Lecoq de Boisbaudran later pulled dysprosium ('hard to get at') out of it with 32 precipitations.", "Terbium#History", id=0, color="#5a4030")
X("Ytterbia", "Ytterbia", "Yb2O3", "Solid", "Marignac's earth (1878) from erbia, which Urbain (1907) showed still hid lutetium.", "Ytterbium#History", id=0)
X("Samaria", "Samaria", "Sm2O3", "Solid", "Lecoq de Boisbaudran's earth from samarskite (1879), which held samarium, gadolinium and europium.", "Samarium#History", id=0)
L("BeSO4", "Beryllium sulfate", "BeSO4", "Solid")
L("BeOH2", "Beryllium hydroxide", "Be(OH)2", "Solid")
L("BeO", "Beryllium oxide", "BeO", "Solid")
X("BeCl2", "Beryllium Chloride", "BeCl2", "Solid", "The salt Wohler and Bussy independently reduced with potassium in 1828 to isolate beryllium.", "Beryllium_chloride", id=0)
X("ThO2", "Thoria", "ThO2", "Solid", "Thorium dioxide, with the highest melting point of any oxide (3350 C). Glowing in a gas flame, it lit Victorian streets.", "Thorium_dioxide", id=0)
X("GasMantle", "Welsbach Gas Mantle", "ThO2(Ce)", "Solid", "Auer von Welsbach's 1891 mantle: 99% thoria, 1% ceria, glowing brilliant white over a gas flame. It saved gas lighting from the electric bulb for decades.", "Gas_mantle", id=0, balance="ThO2", color="#f8f8e8")
X("RbCl", "Rubidium Chloride", "RbCl", "Solid", "The salt Bunsen and Kirchhoff concentrated from lepidolite (1861).", "Rubidium_chloride", id=0)
X("CsCl", "Caesium Chloride", "CsCl", "Solid", "Bunsen's 17 grams of caesium chloride from 44 tonnes of mineral water (1860). Its crystal structure is the textbook simple cubic lattice.", "Caesium_chloride", id=0)
X("GeO2", "Germanium Dioxide", "GeO2", "Solid", "The oxide Winkler reduced in 1886. Its measured properties matched Mendeleev's 1871 predictions for eka-silicon almost exactly.", "Germanium_dioxide", id=0)
X("V2O5", "Vanadium Pentoxide", "V2O5", "Solid", "An orange oxide that has catalysed the Contact process for sulfuric acid since 1915.", "Vanadium(V)_oxide", id=0, color="#e88020")
L("SiCl4", "Silicon tetrachloride", "SiCl4", "Liquid")
X("ZrCl4", "Zirconium Tetrachloride", "ZrCl4", "Solid", "The volatile chloride Kroll reduced with magnesium for nuclear-grade zirconium, transparent to neutrons.", "Zirconium(IV)_chloride", id=0)
L("Nb2O5", "Niobium pentoxide", "Nb2O5", "Solid")
L("Ta2O5", "Tantalum pentoxide", "Ta2O5", "Solid")

E1.reactions += [
    R("Distilling Lavender", "Lavender -> Linalool + LinalylAcetate", DISTIL,
      "Steam carries the volatile oil out of the flowers and it separates from the water on cooling.",
      wiki="Lavender_oil", exact=False),
    R("Distilling Peppermint", "Peppermint -> Menthol + Menthone", DISTIL,
      "Peppermint oil, steam-distilled; menthol crystallises from it on chilling and feels cold because it triggers the skin's cold receptor.",
      wiki="Peppermint#Constituents", exact=False),
    R("Distilling Rose", "Rose -> Citronellol + Linalool + GeranylAcetate", DISTIL,
      "Attar of roses, distilled in copper stills since Avicenna in the 10th century.",
      wiki="Rose_oil", exact=False),
    R("Tapping Pine Resin", "PineResin -> Turpentine + Rosin", DISTIL,
      "Pine resin heated in a still: spirit of turpentine comes over, and rosin stays behind. Naval stores for caulking wooden ships.",
      wiki="Naval_stores", exact=False),
    R("Rectifying Turpentine", "Turpentine -> Pinene", DISTIL,
      "Redistilled turpentine is mostly alpha-pinene, the resinous smell of a pine forest.",
      wiki="Alpha-Pinene", exact=False),
    R("Distilling Cinnamon", "Cinnamon -> Cinnamaldehyde", DISTIL,
      "Cinnamon bark oil is about 90% cinnamaldehyde.",
      wiki="Cinnamaldehyde", exact=False),
    R("Distilling Aniseed", "Anise -> Anethole", DISTIL,
      "Anise oil is about 90% anethole, which clouds a glass of ouzo when water is added.",
      wiki="Anethole", exact=False),
    R("Distilling Thyme", "Thyme -> Thymol", DISTIL,
      "Thyme oil; Caspar Neumann crystallised its thymol in 1719.",
      wiki="Thymol", exact=False),
    R("Gall Ink", "OakGalls + GreenVitriol -> IronGallInk", MIX,
      "Crushed galls steeped in rainwater, mixed with green vitriol and gum arabic: the standard ink of Europe from the 5th to the 19th century.",
      wiki="Iron_gall_ink#Preparation", exact=False),
    R("Scraping the Casks", "Argol + H2O -> Bitartrate", COOL,
      "Wine lees dissolved in hot water and recrystallised give white cream of tartar.",
      wiki="Potassium_bitartrate#History", exact=False),
]
E2.reactions += [
    R("Aqua Vitae", "Wine -> Ethanol + IsoamylAlcohol + H2O", DISTIL,
      "The alembics of Salerno (around 1100) distilled wine into 'burning water'. The oily tail of the distillate, fusel oil, is mostly isoamyl alcohol.",
      wiki="Distilled_beverage#History", exact=False),
    R("Distilling Ants", "Ants -> Formic + H2O", DISTIL,
      "John Ray (1671) distilled red ants and collected the acid they sting with, named from formica, ant.",
      wiki="Formic_acid#History", exact=False),
    R("Salt of Amber", "Amber -> Succinic", DISTIL,
      "Dry distillation of amber gives white crystals of succinic acid, named from succinum, amber (Agricola, 1546).",
      wiki="Succinic_acid#History", exact=False),
    R("Flowers of Benzoin", "GumBenzoin -> BenzoicAcid", HEAT,
      "Gentle heat sublimes benzoic acid out of the resin as feathery white crystals.",
      wiki="Benzoic_acid#History", exact=False),
    R("Distilling Spearmint", "Spearmint -> Carvone", DISTIL,
      "Spearmint oil is mostly (R)-carvone. Its mirror image is the smell of caraway: the nose can tell left from right.",
      wiki="Carvone", exact=False),
    R("Pressing Orange Peel", "OrangePeel -> Limonene", DISTIL,
      "Cold-pressed or steam-distilled, orange oil is about 95% limonene, now a citrus-scented solvent.",
      wiki="Limonene", exact=False),
    R("Enfleurage", "Jasmine + Tallow -> BenzylAcetate", MIX,
      "Grasse perfumers laid jasmine flowers on trays of purified fat, which soaks up their scent, then washed the fat with alcohol.",
      wiki="Enfleurage", exact=False),
    R("Turmeric Dye", "Turmeric + Ethanol -> Curcumin", MIX,
      "Alcohol extracts the golden pigment curcumin (Vogel and Pelletier, 1815).",
      wiki="Curcumin", exact=False),
]
E3.reactions += [
    R("Scheele's Tartaric Acid", "2 Bitartrate + Ca(OH)2 + H2SO4 -> 2 Tartaric + K2SO4 + CaO", MIX,
      "Carl Wilhelm Scheele (1769) precipitated calcium tartrate from cream of tartar and freed the acid with sulfuric acid.",
      wiki="Tartaric_acid#History", exact=False),
    R("Scheele's Citric Acid", "Lemons + Ca(OH)2 + H2SO4 -> Citric", MIX,
      "Scheele (1784) precipitated calcium citrate from lemon juice and liberated citric acid. Most citric acid is now made by Aspergillus mould from sugar.",
      wiki="Citric_acid#History", exact=False),
    R("Scheele's Malic Acid", "Apples + Ca(OH)2 + H2SO4 -> Malic", MIX,
      "Scheele again (1785), this time from apple juice.",
      wiki="Malic_acid#History", exact=False),
    R("Scheele's Gallic Acid", "OakGalls + H2O -> GallicAcid", HEAT,
      "Scheele (1786) let an infusion of galls go mouldy and found crystals of gallic acid in it.",
      wiki="Gallic_acid#History", exact=False),
    R("Scheele's Oxalic Acid", "Sucrose + 36 HNO3 -> 6 Oxalic + 36 NO2 + 23 H2O", HEAT,
      "Scheele (1776) boiled sugar with nitric acid and got 'acid of sugar', which turned out to be the same acid as in sorrel and rhubarb leaves.",
      wiki="Oxalic_acid#History", T=80, dh=-500),
    R("Chevreul's Butyric Acid", "Butter + H2O -> Butyric + Hexanoic + Glycerol", HEAT,
      "Michel Chevreul (1814-23) saponified butter and separated its volatile acids: butyric, from butyrum, butter, and caproic, from capra, goat.",
      wiki="Butyric_acid#History", exact=False),
    R("Stearin Candles", "Tallow + 3 H2O -> 3 StearicAcid + Glycerol", HEAT,
      "Chevreul and Gay-Lussac (1825) split tallow into glycerol and hard stearic acid, which made odourless, bright-burning candles.",
      wiki="Stearic_acid#History", T=200, dh=50),
    R("Splitting Olive Oil", "Triolein + 3 H2O -> 3 OleicAcid + Glycerol", HEAT,
      "Olive oil hydrolysed by superheated steam into oleic acid and glycerol.",
      wiki="Oleic_acid", T=250, dh=50),
    R("Splitting Coconut Oil", "CoconutOil + 3 H2O -> 3 LauricAcid + Glycerol", HEAT,
      "Coconut oil splits into lauric acid, the base of most soaps' lather.",
      wiki="Lauric_acid", T=250, dh=50),
    R("Splitting Palm Oil", "PalmOil + 3 H2O -> 3 PalmiticAcid + Glycerol", HEAT,
      "Palm oil gives palmitic acid, the commonest saturated fatty acid in nature.",
      wiki="Palmitic_acid", T=250, dh=50),
    R("Braconnot's Glycine", "Gelatin + H2SO4 -> Glycine", HEAT,
      "Henri Braconnot (1820) boiled gelatin with sulfuric acid and got 'sugar of gelatin', sweet crystals of glycine.",
      wiki="Glycine#History", exact=False),
    R("Leucine and Tyrosine", "Cheese + H2SO4 -> Leucine + Tyrosine", HEAT,
      "Proust (1818) found leucine in fermenting cheese; Liebig (1846) found tyrosine by melting casein with potash.",
      wiki="Tyrosine#History", exact=False),
    R("The First Amino Acid", "Asparagus -> Asparagine", COOL,
      "Vauquelin and Robiquet (1806) evaporated asparagus juice and crystals of asparagine grew out: the first amino acid discovered.",
      wiki="Asparagine#History", exact=False),
    R("Leroux's Salicin", "WillowBark + H2O -> Salicin", HEAT,
      "Henri Leroux (1828) boiled willow bark and crystallised its bitter principle.",
      wiki="Salicin", exact=False),
    R("Piria's Salicylic Acid", "Salicin + O2 -> Salicylic", HEAT,
      "Raffaele Piria (1838) split salicin and oxidised the fragment into salicylic acid.",
      wiki="Salicylic_acid#History", exact=False),
    R("Pelletier and Caventou's Quinine", "Cinchona + Ethanol -> Quinine", MIX,
      "Pelletier and Caventou (1820) extracted the bark with alcohol and isolated quinine. They did not patent it; they wanted it made everywhere.",
      wiki="Quinine#History", exact=False),
    R("Runge's Caffeine", "TeaLeaves + H2O -> Caffeine", HEAT,
      "Friedlieb Runge (1819) isolated caffeine at Goethe's suggestion; it was found in tea in 1827.",
      wiki="Caffeine#History", exact=False),
    R("Theobromine", "Cocoa + H2O -> Theobromine", HEAT,
      "Alexander Woskresensky (1841) isolated the bitter alkaloid of cocoa.",
      wiki="Theobromine", exact=False),
    R("Nicotine", "Tobacco + NaOH -> Nicotine", DISTIL,
      "Posselt and Reimann (1828) steam-distilled tobacco leaves with alkali and collected nicotine.",
      wiki="Nicotine#History", exact=False),
    R("Mein's Atropine", "Belladonna + Ethanol -> Atropine", MIX,
      "Heinrich Mein (1831) isolated atropine, still used to dilate pupils and to restart slow hearts.",
      wiki="Atropine#History", exact=False),
    R("Withering's Foxglove", "Foxglove + Ethanol -> Digitoxin", MIX,
      "The active glycoside of foxglove, isolated by Nativelle (1869) and still used to treat heart failure.",
      wiki="Digitoxin", exact=False),
    R("Vogel's Coumarin", "TonkaBeans + Ethanol -> Coumarin", MIX,
      "August Vogel (1820) extracted the sweet-smelling crystals from tonka beans.",
      wiki="Coumarin#History", exact=False),
    R("Oil of Bitter Almonds", "BitterAlmonds + H2O -> Benzaldehyde + HCN", DISTIL,
      "Water and enzymes release benzaldehyde, and prussic acid with it, from bitter almonds.",
      wiki="Benzaldehyde#History", exact=False),
    R("Liebig's Benzoic Acid", "2 Benzaldehyde + O2 -> 2 BenzoicAcid", MIX,
      "Liebig and Wohler (1832) noticed oil of bitter almonds left in air slowly turned to crystals of benzoic acid.",
      wiki="Benzoyl_group", dh=-500),
    R("Kirchhoff's Glucose", "Starch + H2O -> Glucose", HEAT,
      "Konstantin Kirchhoff (1811) boiled potato starch with dilute sulfuric acid into a sweet syrup when Napoleon's blockade cut off cane sugar.",
      wiki="Glucose_syrup#History", exact=False),
    R("Gadolin's Yttria", "Gadolinite + HNO3 -> YNO33", MIX,
      "Johan Gadolin (1794) dissolved the black Ytterby mineral and found a new earth: the first rare earth.",
      wiki="Yttrium#History", exact=False),
    R("Calcining Yttria", "4 YNO33 -> 2 Y2O3 + 12 NO2 + 3 O2", HEAT,
      "Yttrium nitrate decomposes to white yttria.",
      wiki="Yttrium(III)_oxide", T=600, dh=900),
    R("Wohler's Yttrium", "YNO33 -> Y", ELEC,
      "Friedrich Wohler (1828) first made impure yttrium metal; electrolysis of the fused salt gives it pure.",
      wiki="Yttrium#History", exact=False),
    R("Mosander's Earths", "YNO33 -> Erbia + Terbia + Ytterbia", COOL,
      "Carl Gustaf Mosander (1843) crystallised yttria's nitrate fraction by fraction and found it hid other earths. Rare-earth chemists would crystallise for decades.",
      wiki="Erbium#History", exact=False),
    R("Berzelius' Ceria", "Cerite + HNO3 -> CeNO33 + LaNO33 + Didymium", MIX,
      "Berzelius and Hisinger found ceria (1803); Mosander found lanthanum ('hidden') in it in 1839 and didymium in 1841.",
      wiki="Cerium#History", exact=False),
    R("Vauquelin's Beryllia", "Beryl + H2SO4 -> BeSO4", MIX,
      "Louis Vauquelin (1798) found a new earth in beryl and emerald whose salts tasted sweet; it was first called glucinium.",
      wiki="Beryllium#History", exact=False),
    R("Beryllium Hydroxide", "BeSO4 + 2 NaOH -> BeOH2 + Na2SO4", MIX,
      "Alkali throws down beryllium hydroxide from the sulfate.",
      wiki="Beryllium_hydroxide", dh=-50),
    R("Beryllia", "BeOH2 -> BeO + H2O", HEAT,
      "Heated, the hydroxide gives beryllia, a ceramic that conducts heat almost as well as metal.",
      wiki="Beryllium_oxide", T=400, dh=50),
    R("Beryllium Chloride", "BeO + Charcoal + Cl2 -> BeCl2 + CO", HEAT,
      "Beryllia heated with carbon in chlorine.",
      wiki="Beryllium_chloride", T=800, dh=-100),
    R("Wohler's Beryllium", "BeCl2 + 2 K -> Be + 2 KCl", SMELT,
      "Wohler and Bussy (1828) reduced the chloride with potassium in a platinum crucible.",
      wiki="Beryllium#History", T=600, dh=-300),
    R("Berzelius' Thoria", "Thorite + HCl -> ThO2", MIX,
      "Berzelius (1829) found a new earth in a black Norwegian mineral and named it for Thor.",
      wiki="Thorium#History", exact=False),
    R("Thorium Metal", "ThO2 + 2 Ca -> Th + 2 CaO", SMELT,
      "Calcium strips the oxygen from thoria.",
      wiki="Thorium#Production", T=1000, dh=-100),
    R("Klaproth's Zirconia", "Zircon + 4 Cl2 + 4 Coke -> ZrCl4 + SiCl4 + 4 CO", HEAT,
      "Zircon chlorinated with carbon gives zirconium and silicon tetrachlorides, separated by distillation. Klaproth found zirconia in zircon in 1789.",
      wiki="Zirconium#History", T=1000, dh=-200),
    R("Vanadium Pentoxide", "Vanadinite + SodaAsh -> V2O5", HEAT,
      "Roasting vanadinite with soda and leaching gives vanadium pentoxide.",
      wiki="Vanadium(V)_oxide", exact=False),
    R("Winkler's Germanium Oxide", "Argyrodite + O2 -> GeO2", HEAT,
      "Clemens Winkler (1886) found 7% of an unaccounted element in argyrodite and isolated its oxide.",
      wiki="Germanium#History", exact=False),
    R("Columbium and Tantalum", "Columbite + HF -> Nb2O5 + Ta2O5", MIX,
      "Marignac (1866) separated niobium from tantalum through their fluoride salts, ending a 60-year argument over whether they were one element.",
      wiki="Niobium#History", exact=False),
]
E4.reactions += [
    R("Glucose Fermentation, Weizmann", "Starch -> Butanol + Acetone + Ethanol", MIX,
      "Chaim Weizmann's Clostridium acetobutylicum (1916) fermented maize starch into acetone, butanol and ethanol for the British war effort.",
      wiki="Acetone-butanol-ethanol_fermentation", exact=False),
    R("Bunsen's Caesium", "MineralWater -> CsCl", HEAT,
      "Evaporating 44,000 litres of Durkheim water, Bunsen (1860) collected caesium chloride, the first element found by spectroscopy.",
      wiki="Caesium#History", exact=False),
    R("Bunsen's Rubidium", "Lepidolite + HCl -> RbCl", MIX,
      "Bunsen and Kirchhoff (1861) extracted rubidium chloride from lepidolite.",
      wiki="Rubidium#History", exact=False),
    R("Caesium Metal", "2 CsCl -> 2 Cs + Cl2", ELEC,
      "Carl Setterberg (1882) first obtained caesium metal by electrolysis. It melts at 28 C, in your hand.",
      wiki="Caesium#History", T=650, dh=880),
    R("Rubidium Metal", "2 RbCl -> 2 Rb + Cl2", ELEC,
      "Bunsen electrolysed molten rubidium chloride (1863).",
      wiki="Rubidium#History", T=720, dh=870),
    R("Winkler's Germanium", "GeO2 + 2 H2 -> Ge + 2 H2O", HEAT,
      "Hydrogen reduces germanium dioxide to the metalloid. The first transistor (1947) was germanium.",
      wiki="Germanium#History", T=650, dh=50),
    R("Vanadium Metal", "V2O5 + 5 Ca -> 2 V + 5 CaO", SMELT,
      "Calcium reduces vanadium pentoxide; vanadium toughens tool steel and Henry Ford's Model T axles.",
      wiki="Vanadium#Production", T=1000, dh=-1500),
    R("Niobium Metal", "Nb2O5 + 5 Ca -> 2 Nb + 5 CaO", SMELT,
      "Calcium reduction of niobium oxide. Niobium-titanium wire wound the magnets of every MRI scanner and the LHC.",
      wiki="Niobium#Production", T=1100, dh=-800),
    R("Tantalum Metal", "Ta2O5 + 5 Ca -> 2 Ta + 5 CaO", SMELT,
      "Tantalum, named for Tantalus who stood in water he could never drink, because it does not dissolve in acids. Every phone has tantalum capacitors.",
      wiki="Tantalum#Production", T=1100, dh=-700),
    R("Kroll Zirconium", "ZrCl4 + 2 Mg -> Zr + 2 MgCl2", SMELT,
      "Zirconium tetrachloride reduced with magnesium; zirconium alloy tubes clad the uranium fuel of nuclear reactors.",
      wiki="Zirconium#Production", T=850, dh=-300),
    R("Coster and Hevesy's Hafnium", "Zircon -> Hf", LIGHT,
      "Coster and Hevesy (1923) found element 72 hiding in zircon by its X-ray spectrum, in Copenhagen (Hafnia), as Bohr's theory predicted.",
      wiki="Hafnium#History", exact=False),
    R("Noddack's Rhenium", "MoS2 -> Re", HEAT,
      "Ida and Walter Noddack (1925) found the last stable element in molybdenite and platinum ores by X-ray spectroscopy.",
      wiki="Rhenium#History", exact=False),
    R("Auer's Twins", "Didymium -> PrNO33 + NdNO33", COOL,
      "Carl Auer von Welsbach (1885) fractionally crystallised didymium ammonium nitrate a hundred times and split it into praseodymium and neodymium.",
      wiki="Praseodymium#History", exact=False),
    R("Praseodymium Oxide", "12 PrNO33 -> 2 Pr6O11 + 36 NO2 + 7 O2", HEAT,
      "Praseodymium nitrate calcines to a dark brown mixed oxide.",
      wiki="Praseodymium(III,IV)_oxide", T=700, dh=1000),
    R("Welsbach Mantle", "ThO2 + CeNO33 -> GasMantle", HEAT,
      "A cotton sock soaked in thorium and cerium nitrates, burned away to leave a fragile ceramic net.",
      wiki="Gas_mantle#History", exact=False),
    R("Lanthanum Carbonate", "2 LaNO33 + 3 SodaAsh -> La2CO33 + 6 NaNO3", MIX,
      "Soda precipitates lanthanum carbonate, now a drug that binds phosphate in kidney patients.",
      wiki="Lanthanum_carbonate", dh=-50),
    R("Cerium Carbonate", "2 CeNO33 + 3 SodaAsh -> Ce2CO33 + 6 NaNO3", MIX,
      "Cerium carbonate, the usual starting point for cerium oxide polishing powders.",
      wiki="Cerium(III)_carbonate", dh=-50),
    R("Lanthanum Metal", "LaNO33 -> La", ELEC,
      "Hillebrand and Norton (1875) electrolysed fused rare-earth chlorides for the first rare-earth metals.",
      wiki="Lanthanum#History", exact=False),
    R("Cerium Metal", "CeNO33 -> Ce", ELEC,
      "Cerium metal, pyrophoric when scratched: alloyed with iron it is the flint in every lighter.",
      wiki="Cerium#Applications", exact=False),
    R("Praseodymium Metal", "PrNO33 -> Pr", ELEC,
      "Praseodymium, the 'green twin', colours yellow glass and the goggles of glassblowers.",
      wiki="Praseodymium", exact=False),
    R("Cleve's Holmium and Thulium", "Erbia + Ca -> Er + Ho + Tm", SMELT,
      "Per Teodor Cleve (1879) split two more earths from erbia: holmia (for Stockholm) and thulia (for Thule).",
      wiki="Holmium#History", exact=False),
    R("Lecoq's Dysprosium", "Terbia + Ca -> Tb + Dy", SMELT,
      "Lecoq de Boisbaudran (1886) separated dysprosium after 32 precipitations; the name means 'hard to get at'.",
      wiki="Dysprosium#History", exact=False),
    R("Urbain's Lutetium", "Ytterbia + Ca -> Yb + Lu", SMELT,
      "Georges Urbain (1907) split ytterbia and named the new element for Lutetia, Roman Paris.",
      wiki="Lutetium#History", exact=False),
    R("Samaria", "Samarskite + HNO3 -> Samaria", MIX,
      "Lecoq de Boisbaudran (1879) found samaria in samarskite.",
      wiki="Samarium#History", exact=False),
    R("Samarium, Gadolinium, Europium", "Samaria + Ca -> Sm + Gd + Eu", SMELT,
      "Samaria held three elements: samarium, gadolinium (Marignac, 1880) and europium (Demarcay, 1901), which makes the red glow in banknotes under UV.",
      wiki="Europium#History", exact=False),
    R("Nilson's Scandium", "Gadolinite + H2SO4 -> Sc", MIX,
      "Lars Nilson (1879) found scandium, Mendeleev's predicted eka-boron, in gadolinite and euxenite.",
      wiki="Scandium#History", exact=False),
    R("Radium Emanation", "Ra -> Rn", LIGHT,
      "Friedrich Dorn (1900) found radium gives off a radioactive gas: radon, the heaviest noble gas.",
      wiki="Radon#History", exact=False),
    R("Perey's Francium", "Ac -> Fr", LIGHT,
      "Marguerite Perey (1939), the Curies' former lab assistant, found a decay branch of actinium: element 87, the last element found in nature.",
      wiki="Francium#History", exact=False),
]
E5.reactions += [
    R("Fermi's Pile", "U + Graphite -> Pm", LIGHT,
      "Uranium lumps in a graphite pile went critical in a Chicago squash court on 2 December 1942. Fission products from such reactors gave up promethium in 1945.",
      wiki="Promethium#History", exact=False),
    R("Corson's Astatine", "Bi + He -> At", LIGHT,
      "Alpha particles on bismuth in Berkeley's cyclotron (1940): element 85, from astatos, unstable.",
      wiki="Astatine#History", exact=False),
    R("Miller-Urey Experiment", "Methane + NH3 + H2 + H2O -> Glycine + Alanine", ELEC,
      "Stanley Miller (1953) sparked a flask of methane, ammonia, hydrogen and water for a week and the water turned brown with amino acids.",
      wiki="Miller-Urey_experiment", exact=False),
    R("Oxo Process", "Ethylene + CO + H2 -> Propanal", CAT,
      "Otto Roelen (1938) found cobalt adds carbon monoxide and hydrogen across a double bond: hydroformylation, now ten million tonnes a year.",
      wiki="Hydroformylation", cat="Co", T=150, P=200, dh=-120),
    R("Oxo Butanal", "Propylene + CO + H2 -> Butanal + Isobutyraldehyde", CAT,
      "Propylene gives both straight and branched aldehydes.",
      wiki="Hydroformylation", cat="Co", T=150, P=200, exact=False, dh=-120),
    R("Propanol", "Propanal + H2 -> Propanol", CAT,
      "The aldehyde hydrogenated over nickel.",
      wiki="1-Propanol#Production", cat="Ni", T=120, dh=-70),
    R("Butanol", "Butanal + H2 -> Butanol", CAT,
      "Butanal hydrogenated to butanol, a solvent for paints and lacquers.",
      wiki="1-Butanol#Production", cat="Ni", T=120, dh=-70),
    R("Isobutanol", "Isobutyraldehyde + H2 -> Isobutanol", CAT,
      "The branched aldehyde hydrogenated.",
      wiki="Isobutanol#Production", cat="Ni", T=120, dh=-70),
    R("Propionic Acid", "2 Propanal + O2 -> 2 Propionic", MIX,
      "Propanal oxidises in air to propionic acid, a mould inhibitor in bread.",
      wiki="Propionic_acid#Production", dh=-500),
    R("First Petrochemical", "Propylene + H2O -> Isopropanol", CAT,
      "Standard Oil (1920) hydrated refinery propylene with sulfuric acid: isopropyl alcohol, the first chemical made from petroleum.",
      wiki="Isopropyl_alcohol#History", cat="H3PO4", T=200, dh=-52),
    R("Ethanol from Ethylene", "Ethylene + H2O -> Ethanol", CAT,
      "Shell (1947) hydrated ethylene over phosphoric acid; most industrial ethanol was made this way until bioethanol.",
      wiki="Ethanol#Production", cat="H3PO4", T=300, P=70, dh=-45),
    R("Acetone from Isopropanol", "Isopropanol -> Acetone + H2", CAT,
      "Isopropanol dehydrogenated over copper.",
      wiki="Acetone#Production", cat="Cu", T=350, dh=66),
    R("Propylamine", "Propanol + NH3 -> Propylamine + H2O", CAT,
      "Alcohol and ammonia over alumina give the amine.",
      wiki="Propylamine", cat="Alumina", T=350, dh=-30),
    R("Ethylamine", "Ethanol + NH3 -> Ethylamine + H2O", CAT,
      "Ethanol and ammonia over alumina.",
      wiki="Ethylamine#Production", cat="Alumina", T=350, dh=-30),
    R("Hexamine", "6 CH2O + 4 NH3 -> Hexamine + 6 H2O", MIX,
      "Butlerov (1859) mixed formaldehyde and ammonia and got a cage-shaped molecule: camping-stove fuel tablets, and a urinary antiseptic.",
      wiki="Hexamethylenetetramine", dh=-300),
    R("Furfural from Oat Hulls", "Bran + H2SO4 -> Furfural", DISTIL,
      "Oat hulls steam-distilled with acid give furfural, the bran-scented solvent that refined Quaker's lubricating oils (1921).",
      wiki="Furfural#History", exact=False),
    R("Decarbonylating Furfural", "Furfural -> Furan + CO", CAT,
      "Furfural loses carbon monoxide over palladium to give furan.",
      wiki="Furan#Production", cat="Pd", T=300, dh=30),
    R("Acrolein", "Glycerol -> Acrolein + 2 H2O", HEAT,
      "Glycerol dehydrated by heat gives acrolein, the acrid smell of burnt fat.",
      wiki="Acrolein#Production", T=300, dh=100),
    R("Chichibabin Pyridine", "3 Acetaldehyde + NH3 + CH2O -> Pyridine + 3 H2O + H2", CAT,
      "Aldehydes and ammonia condensed over alumina (Chichibabin, 1924) give pyridine.",
      wiki="Chichibabin_pyridine_synthesis", cat="Alumina", T=400, exact=False, dh=-100),
]
E4.reactions += [
    R("Strecker's Alanine", "Acetaldehyde + HCN + H2O -> Alanine", MIX,
      "Adolph Strecker (1850) combined acetaldehyde, ammonia and hydrogen cyanide, then hydrolysed: the first amino acid made in a flask.",
      wiki="Strecker_amino_acid_synthesis", dh=-100),
    R("Ethylene from Alcohol", "Ethanol -> Ethylene + H2O", CAT,
      "The Dutch chemists (1795) dripped alcohol onto hot acid and got olefiant gas. Over hot alumina, it is clean and simple.",
      wiki="Ethylene#History", cat="Alumina", T=350, dh=45),
    R("Oxidising Alcohol", "Ethanol + CuO -> Acetaldehyde + Cu + H2O", HEAT,
      "A glowing copper oxide wire plunged into alcohol vapour turns bright copper and the vapour becomes acetaldehyde.",
      wiki="Acetaldehyde#Production", T=300, dh=-50),
    R("Benzyl Chloride", "Toluene + Cl2 -> BenzylChloride + HCl", LIGHT,
      "Under light, chlorine attacks toluene's methyl group, not its ring.",
      wiki="Benzyl_chloride#Production", dh=-100),
    R("Benzyl Alcohol", "BenzylChloride + H2O -> BenzylAlcohol + HCl", HEAT,
      "Benzyl chloride boiled with water.",
      wiki="Benzyl_alcohol#Production", T=100, dh=-20),
    R("Benzaldehyde", "2 BenzylAlcohol + O2 -> 2 Benzaldehyde + 2 H2O", CAT,
      "Benzyl alcohol oxidised over copper.",
      wiki="Benzaldehyde#Production", cat="Cu", T=300, dh=-300),
    R("Perkin's Cinnamic Acid", "Benzaldehyde + AceticAnhydride -> CinnamicAcid + AcOH", HEAT,
      "The Perkin reaction (1868): benzaldehyde condensed with acetic anhydride and sodium acetate.",
      wiki="Perkin_reaction", T=180, dh=-50),
    R("Reimer-Tiemann Reaction", "Phenol + CHCl3 + 3 NaOH -> Salicylaldehyde + 3 NaCl + 2 H2O", HEAT,
      "Chloroform and alkali attach an aldehyde group next to phenol's OH (Reimer and Tiemann, 1876).",
      wiki="Reimer-Tiemann_reaction", T=70, dh=-200),
    R("Perkin's Coumarin", "Salicylaldehyde + AceticAnhydride -> Coumarin + AcOH + H2O", HEAT,
      "William Perkin (1868) made coumarin from salicylaldehyde: the first synthetic perfume molecule. Fougere Royale (1882) was built on it.",
      wiki="Coumarin#Synthesis", T=180, dh=-50),
    R("Antifebrin", "Aniline + AceticAnhydride -> Acetanilide + AcOH", MIX,
      "Cahn and Hepp (1886) were given acetanilide by mistake instead of naphthalene and found it brought down fever: Antifebrin.",
      wiki="Acetanilide#History", dh=-100),
    R("Phenacetin", "Paracetamol + Ethanol -> Phenacetin + H2O", HEAT,
      "Bayer's Phenacetin (1887), an ether of paracetamol; the body turns it back into paracetamol.",
      wiki="Phenacetin", exact=True, dh=-20),
    R("Salol", "Salicylic + Phenol -> PhenylSalicylate + H2O", HEAT,
      "Marceli Nencki (1886) esterified salicylic acid with phenol: Salol, which passes the stomach and splits in the gut.",
      wiki="Phenyl_salicylate", T=150, dh=-20),
    R("Grape Flavour", "Anthranilic + Methanol -> MethylAnthranilate + H2O", CAT,
      "Methyl anthranilate, the 'grape' of grape soda, a Concord grape aroma.",
      wiki="Methyl_anthranilate", cat="H2SO4", T=70, dh=-20),
    R("Nitrating Phenol", "Phenol + HNO3 -> 2-Nitrophenol + H2O", COOL,
      "Cold dilute nitric acid nitrates phenol once.",
      wiki="2-Nitrophenol", T=20, dh=-120),
    R("Hydroquinone Developer", "Aniline + Na2Cr2O7 + H2SO4 -> Hydroquinone", HEAT,
      "Aniline oxidised to quinone and reduced gives hydroquinone, the photographic developer (Abney, 1880).",
      wiki="Hydroquinone#Production", exact=False),
]

# Fischer esterification (Emil Fischer and Arthur Speier, 1895): acid + alcohol over a
# sulfuric acid catalyst. Most of the fruit flavours of the sweet shop are esters.
ESTERS = [
    ("AcOH", "Methanol", "MethylAcetate", "a fast-evaporating solvent that smells of glue"),
    ("AcOH", "Ethanol", "EthylAcetate", "nail-varnish remover and the solvent that decaffeinates 'naturally' decaf coffee"),
    ("AcOH", "Propanol", "PropylAcetate", "the scent of pears"),
    ("AcOH", "Isopropanol", "IsopropylAcetate", "a fruity solvent for printing inks"),
    ("AcOH", "IsoamylAlcohol", "IsoamylAcetate", "banana oil, and the alarm pheromone of honeybees"),
    ("AcOH", "Isobutanol", "IsobutylAcetate", "a raspberry-and-pear note in flavourings"),
    ("AcOH", "Butanol", "ButylAcetate", "the apple-scented solvent of car lacquers"),
    ("AcOH", "BenzylAlcohol", "BenzylAcetate", "the main scent of jasmine, made rather than picked"),
    ("AcOH", "Menthol", "MenthylAcetate", "the sweet, minty note of peppermint oil"),
    ("AcOH", "Linalool", "LinalylAcetate", "the fresh note of lavender and bergamot"),
    ("Formic", "Methanol", "MethylFormate", "a refrigerant and fumigant"),
    ("Formic", "Ethanol", "EthylFormate", "the smell of rum and the taste of raspberries; astronomers found it in a dust cloud at the centre of the galaxy in 2009"),
    ("Propionic", "Ethanol", "EthylPropionate", "a pineapple and rum note"),
    ("Butyric", "Methanol", "MethylButyrate", "the smell of apples"),
    ("Butyric", "Ethanol", "EthylButyrate", "the smell of pineapple and orange juice"),
    ("Hexanoic", "Ethanol", "EthylHexanoate", "a green-apple and aniseed note found in wine and beer"),
    ("BenzoicAcid", "Methanol", "MethylBenzoate", "the scent of feijoa fruit, and a lure for orchid bees"),
    ("BenzoicAcid", "Ethanol", "EthylBenzoate", "a sweet, wintergreen-like solvent in fruit flavours"),
    ("BenzoicAcid", "BenzylAlcohol", "BenzylBenzoate", "the oldest treatment for scabies, still on the WHO list of essential medicines"),
    ("CinnamicAcid", "Ethanol", "EthylCinnamate", "the warm, fruity balsam of storax"),
    ("CinnamicAcid", "Methanol", "MethylCinnamate", "the strawberry note of Thai basil"),
    ("Salicylic", "Methanol", "MethylSalicylate", "oil of wintergreen, the smell of muscle rubs"),
]
E4.reactions += [
    R(f"Making {SUBSTANCES[e].name}", f"{a} + {al} -> {e} + H2O", CAT,
      f"Acid and alcohol joined by Fischer esterification, with sulfuric acid as catalyst: {note}.",
      wiki="Fischer-Speier_esterification", cat="H2SO4", T=80, dh=-5)
    for a, al, e, note in ESTERS
]
E4.reactions += [
    R("Triacetin", "3 AcOH + Glycerol -> Triacetin + 3 H2O", CAT,
      "Glycerol esterified with acetic acid three times over: a food additive and cigarette-filter plasticiser.",
      wiki="Triacetin", cat="H2SO4", T=120, dh=-15),
    R("Diethyl Oxalate", "Oxalic + 2 Ethanol -> DiethylOxalate + 2 H2O", CAT,
      "Both acid groups of oxalic acid esterified with ethanol.",
      wiki="Diethyl_oxalate", cat="H2SO4", T=80, dh=-10),
    R("Diethyl Phthalate", "PhthalicAnhydride + 2 Ethanol -> DiethylPhthalate + H2O", CAT,
      "A plasticiser and the fixative that makes perfume last.",
      wiki="Diethyl_phthalate", cat="H2SO4", T=150, dh=-30),
    R("Dibutyl Phthalate", "PhthalicAnhydride + 2 Butanol -> DibutylPhthalate + H2O", CAT,
      "A plasticiser for PVC and nitrocellulose lacquer.",
      wiki="Dibutyl_phthalate", cat="H2SO4", T=150, dh=-30),
    R("Claisen Condensation", "2 EthylAcetate -> EthylAcetoacetate + Ethanol", CAT,
      "Ludwig Claisen (1887): sodium makes one ester molecule attack another, building a carbon chain.",
      wiki="Claisen_condensation", cat="Na", T=80, dh=-20),
]



# ======================================================================================
# THE LABORATORY: the everyday reactions of a working chemist, in no particular age.
# Salts, precipitates, displacements and the organic reagents' shelf. Generated rows from
# tools/data (see the comment above LAB_INORGANIC) plus hand-written organic chemistry.
# ======================================================================================
for _k, _n, _f, _s in [  # library-bound reagents and biochemicals
    ("AcetylChloride", "Acetyl chloride", "C2H3ClO", "Liquid"), ("BenzoylChloride", "Benzoyl chloride", "C7H5ClO", "Liquid"),
    ("Acetamide", "Acetamide", "C2H5NO", "Solid"), ("Formamide", "Formamide", "CH3NO", "Liquid"),
    ("Acetonitrile", "Acetonitrile", "C2H3N", "Liquid"), ("Propionitrile", "Propionitrile", "C3H5N", "Liquid"),
    ("MeI", "Methyl iodide", "CH3I", "Liquid"), ("MeBr", "Methyl bromide", "CH3Br", "Gas"),
    ("TCE", "Trichloroethylene", "C2HCl3", "Liquid"), ("PCE", "Tetrachloroethylene", "C2Cl4", "Liquid"),
    ("AllylChloride", "Allyl chloride", "C3H5Cl", "Liquid"), ("AllylAlcohol", "Allyl alcohol", "C3H6O", "Liquid"),
    ("DimethylSulfate", "Dimethyl sulfate", "C2H6O4S", "Liquid"), ("DMS", "Dimethyl sulfide", "C2H6S", "Liquid"),
    ("DMSO", "Dimethyl sulfoxide", "C2H6OS", "Liquid"), ("Methanethiol", "Methanethiol", "CH4S", "Gas"),
    ("Ethanethiol", "Ethanethiol", "C2H6S", "Liquid"), ("Thiourea", "Thiourea", "CH4N2S", "Solid"),
    ("Cyanamide", "Cyanamide", "CH2N2", "Solid"), ("Guanidine", "Guanidine", "CH5N3", "Solid"),
    ("Biuret", "Biuret", "C2H5N3O2", "Solid"), ("CyanuricAcid", "Cyanuric acid", "C3H3N3O3", "Solid"),
    ("GlycolicAcid", "Glycolic acid", "C2H4O3", "Solid"), ("GlyoxylicAcid", "Glyoxylic acid", "C2H2O3", "Solid"),
    ("PyruvicAcid", "Pyruvic acid", "C3H4O3", "Liquid"), ("THF", "Tetrahydrofuran", "C4H8O", "Liquid"),
    ("Dioxane", "1,4-Dioxane", "C4H8O2", "Liquid"), ("MethacrylicAcid", "Methacrylic acid", "C4H6O2", "Liquid"),
    ("MaleicAnhydride", "Maleic anhydride", "C4H2O3", "Solid"), ("Crotonaldehyde", "Crotonaldehyde", "C4H6O", "Liquid"),
    ("DiacetoneAlcohol", "Diacetone alcohol", "C6H12O2", "Liquid"), ("MEK", "Methyl ethyl ketone", "C4H8O", "Liquid"),
    ("Cyclopentanone", "Cyclopentanone", "C5H8O", "Liquid"), ("Acetophenone", "Acetophenone", "C8H8O", "Liquid"),
    ("Benzophenone", "Benzophenone", "C13H10O", "Solid"), ("PhenylaceticAcid", "Phenylacetic acid", "C8H8O2", "Solid"),
    ("MandelicAcid", "Mandelic acid", "C8H8O3", "Solid"), ("Anisole", "Anisole", "C7H8O", "Liquid"),
    ("Diphenylamine", "Diphenylamine", "C12H11N", "Solid"), ("Salicylamide", "Salicylamide", "C7H7NO2", "Solid"),
    ("DMC", "Dimethyl carbonate", "C3H6O3", "Liquid"), ("DEC", "Diethyl carbonate", "C5H10O3", "Liquid"),
    ("EtChloroformate", "Ethyl chloroformate", "C3H5ClO2", "Liquid"),
    # biochemistry
    ("Valine", "L-Valine", "C5H11NO2", "Solid"), ("Threonine", "L-Threonine", "C4H9NO3", "Solid"),
    ("Cysteine", "L-Cysteine", "C3H7NO2S", "Solid"), ("Lysine", "L-Lysine", "C6H14N2O2", "Solid"),
    ("Arginine", "L-Arginine", "C6H14N4O2", "Solid"), ("Proline", "L-Proline", "C5H9NO2", "Solid"),
    ("GlutamicAcid", "L-Glutamic acid", "C5H9NO4", "Solid"), ("Glutamine", "L-Glutamine", "C5H10N2O3", "Solid"),
    ("AsparticAcid", "L-Aspartic acid", "C4H7NO4", "Solid"), ("Isoleucine", "L-Isoleucine", "C6H13NO2", "Solid"),
    ("Phenylalanine", "L-Phenylalanine", "C9H11NO2", "Solid"), ("Serine", "Serine", "C3H7NO3", "Solid"),
    ("Maltose", "Maltose", "C12H22O11", "Solid"), ("Xylose", "(+)-Xylose", "C5H10O5", "Solid"),
    ("Xylitol", "Xylitol", "C5H12O5", "Solid"), ("Mannitol", "Mannitol", "C6H14O6", "Solid"),
    ("Riboflavin", "Riboflavin", "C17H20N4O6", "Solid"), ("NicotinicAcid", "Nicotinic acid", "C6H5NO2", "Solid"),
    ("Pyridoxine", "Pyridoxine", "C8H11NO3", "Solid"), ("Biotin", "Biotin", "C10H16N2O3S", "Solid"),
    ("FolicAcid", "Folic acid", "C19H19N7O6", "Solid"), ("Retinol", "Retinol", "C20H30O", "Solid"),
    ("DHC", "7-Dehydrocholesterol", "C27H44O", "Solid"), ("Epinephrine", "Epinephrine", "C9H13NO3", "Solid"),
    ("Lycopene", "Lycopene", "C40H56", "Solid"), ("Carotene", "β-Carotene", "C40H56", "Solid"),
    ("Cineole", "1,8-Cineole", "C10H18O", "Liquid"), ("Geranial", "Geranial", "C10H16O", "Liquid"),
    ("Cuminaldehyde", "Cuminaldehyde", "C10H12O", "Liquid"), ("Estragole", "Estragole", "C10H12O", "Liquid"),
    ("Zingerone", "Zingerone", "C11H14O3", "Solid"), ("Squalane", "Squalane", "C30H62", "Liquid"),
    ("Rutin", "Rutin", "C27H30O16", "Solid"), ("Glucosamine", "Glucosamine", "C6H13NO5", "Solid"),
]:
    L(_k, _n, _f, _s)
SUBSTANCES["Carotene"].name = "beta-Carotene"; SUBSTANCES["Carotene"].rename = True
for _k in ("Valine", "Threonine", "Cysteine", "Lysine", "Arginine", "Proline", "GlutamicAcid", "Glutamine",
           "AsparticAcid", "Isoleucine", "Phenylalanine"):
    SUBSTANCES[_k].name = LIBNAME[_k][2:]
    SUBSTANCES[_k].rename = True
X("MSG", "Monosodium Glutamate", "C5H8NNaO4", "Solid", id=3652, lib=True)
X("VitaminD3", "Vitamin D3", "C27H44O", "Solid", "Cholecalciferol, made in the skin when sunlight's UVB opens a ring of 7-dehydrocholesterol. Windaus (Nobel 1928) found it by irradiating sterols.", "Cholecalciferol", id=0)
for _k, _name, _desc, _wiki, _col in [
    ("Silk", "Raw Silk", "Fibroin from silkworm cocoons, rich in glycine, alanine and serine (named from sericum, silk, by Cramer, 1865).", "Silk", "#f8f0e0"),
    ("Horn", "Horn Shavings", "Keratin, the protein of horn, hair and hooves, cross-linked by the sulfur of cysteine.", "Keratin", "#806040"),
    ("Lupin", "Lupin Seedlings", "Ernst Schulze (1879-86) found phenylalanine and arginine in sprouting lupins.", "Lupinus", "#a0b060"),
    ("Kombu", "Kombu Seaweed", "The kelp of Japanese dashi stock. Kikunae Ikeda (1908) traced its savoury taste to glutamate and named it umami.", "Kombu", "#304020"),
    ("Barley", "Malted Barley", "Sprouted, dried barley. Payen and Persoz (1833) found the substance in it that turns starch into sugar, diastase: the first enzyme discovered.", "Malt", "#c8a060"),
    ("Manna", "Manna Ash Sap", "The dried sweet sap of the Mediterranean manna ash, from which Proust crystallised mannitol (1806).", "Fraxinus_ornus", "#e8e0c0"),
    ("Whey", "Whey", "The yellow-green liquid left after cheese-making; its colour is riboflavin, 'lactoflavin' (Kuhn, 1933).", "Whey", "#e0e880"),
    ("RiceBran", "Rice Bran", "The outer layers polished off rice. Their loss caused beriberi, which led Funk to coin the word 'vitamine' (1912).", "Rice_bran", "#c0a070"),
    ("EggYolk", "Egg Yolk", "Kogl (1936) extracted a milligram of biotin from 250 kg of dried duck egg yolk.", "Yolk", "#f0c020"),
    ("Spinach", "Spinach", "Folic acid was isolated from four tonnes of spinach leaves in 1941 (Latin folium, leaf).", "Spinach", "#2a6a20"),
    ("CodLiverOil", "Cod Liver Oil", "A Victorian cure for rickets long before anyone knew it was rich in vitamins A and D.", "Cod_liver_oil", "#e8c040"),
    ("Lanolin", "Lanolin", "Wool grease, rich in sterols such as 7-dehydrocholesterol, which ultraviolet light turns into vitamin D3.", "Lanolin", "#f0e0a0"),
    ("Carrots", "Carrots", "Wackenroder (1831) crystallised their orange pigment and named it carotene.", "Carrot", "#f07010"),
    ("Tomatoes", "Tomatoes", "Their red is lycopene, named by Schunck (1903).", "Tomato", "#e02010"),
    ("AdrenalGlands", "Adrenal Glands", "Jokichi Takamine (1901) crystallised adrenaline from them, the first hormone isolated pure.", "Adrenal_gland", "#a04030"),
    ("Eucalyptus", "Eucalyptus Leaves", "Their oil is up to 90% 1,8-cineole, the smell of cough drops.", "Eucalyptus_oil", "#5a8a70"),
    ("Lemongrass", "Lemongrass", "Its oil is rich in citral, a lemon scent with no lemons.", "Cymbopogon", "#a0c050"),
    ("Cumin", "Cumin Seeds", "Their warm, earthy smell is cuminaldehyde.", "Cumin", "#906030"),
    ("Tarragon", "Tarragon", "Its aniseed note is estragole, named for the plant's French name, estragon.", "Tarragon", "#5a8040"),
    ("Ginger", "Ginger Root", "Cooking turns fresh ginger's pungent gingerol into sweeter zingerone.", "Ginger", "#d0a050"),
    ("Buckwheat", "Buckwheat", "Rich in rutin, a flavonoid named for rue (Ruta), in which it was first found (1842).", "Buckwheat", "#806040"),
    ("CrabShells", "Crab Shells", "Chitin, the shell polymer of crustaceans and insects. Ledderhose (1876) hydrolysed it to glucosamine.", "Chitin", "#d06040"),
    ("SharkLiverOil", "Shark Liver Oil", "Mitsumaru Tsujimoto (1916) found it full of a hydrocarbon he named squalene, after the shark genus Squalus.", "Squalene", "#c0a060"),
]:
    RAW(_k, _name, _desc, _wiki, _col)

E7_ORGANIC = [
    R("Acetyl Chloride", "AcOH + PCl5 -> AcetylChloride + POCl3 + HCl", MIX,
      "Phosphorus pentachloride swaps acetic acid's OH for chlorine: a fuming reagent that acetylates almost anything.",
      wiki="Acetyl_chloride#Synthesis", dh=-50),
    R("Benzoyl Chloride", "BenzoicAcid + PCl5 -> BenzoylChloride + POCl3 + HCl", MIX,
      "Benzoic acid converted to its acid chloride, Liebig and Wohler's benzoyl radical with a chlorine attached (1832).",
      wiki="Benzoyl_chloride", dh=-50),
    R("Acetamide", "AcOH + NH3 -> Acetamide + H2O", HEAT,
      "Ammonium acetate heated loses water to acetamide, which smells of mice.", wiki="Acetamide", T=200, dh=30),
    R("Formamide", "Formic + NH3 -> Formamide + H2O", HEAT,
      "Formic acid and ammonia give formamide, a possible starting point for life's chemistry.", wiki="Formamide", T=180, dh=30),
    R("Acetonitrile", "Acetamide -> Acetonitrile + H2O", HEAT,
      "Dehydrating acetamide gives acetonitrile, the solvent of HPLC machines.", wiki="Acetonitrile", T=300, dh=80),
    R("Propionitrile", "Acrylonitrile + H2 -> Propionitrile", CAT,
      "Acrylonitrile's double bond hydrogenated over nickel.", wiki="Propionitrile", cat="Ni", T=100, dh=-130),
    R("Methyl Iodide", "Methanol + HI -> MeI + H2O", HEAT,
      "Methanol and hydroiodic acid give methyl iodide, the classic methylating agent.", wiki="Iodomethane", T=60, dh=-20),
    R("Methyl Bromide", "Methanol + HBr -> MeBr + H2O", HEAT,
      "Methyl bromide, once the world's main soil fumigant, banned for harming the ozone layer.", wiki="Bromomethane", T=60, dh=-20),
    R("Trichloroethylene", "Acetylene + 2 Cl2 -> TCE + HCl", MIX,
      "Chlorine adds to acetylene and the product loses hydrogen chloride: trichloroethylene, the degreaser and early anaesthetic.",
      wiki="Trichloroethylene", dh=-400),
    R("Dry-Cleaning Fluid", "TCE + Cl2 -> PCE + HCl", HEAT,
      "One more chlorine gives tetrachloroethylene, 'perc', the dry-cleaners' solvent.", wiki="Tetrachloroethylene", T=400, dh=-100),
    R("Allyl Chloride", "Propylene + Cl2 -> AllylChloride + HCl", HEAT,
      "At 500 C chlorine attacks propylene's methyl group rather than its double bond (Shell, 1945).",
      wiki="Allyl_chloride#Production", T=500, dh=-110),
    R("Allyl Alcohol", "AllylChloride + NaOH -> AllylAlcohol + NaCl", MIX,
      "Allyl chloride hydrolysed with alkali.", wiki="Allyl_alcohol", dh=-50),
    R("Dimethyl Sulfate", "2 Methanol + H2SO4 -> DimethylSulfate + 2 H2O", HEAT,
      "A powerful, very toxic methylating agent.", wiki="Dimethyl_sulfate", T=100, dh=-30),
    R("Dimethyl Sulfide", "2 Methanol + H2S -> DMS + 2 H2O", HEAT,
      "The smell of cooked cabbage and of the sea, where plankton release it.", wiki="Dimethyl_sulfide", T=350, dh=-60),
    R("DMSO", "DMS + NO2 -> DMSO + NO", MIX,
      "Dimethyl sulfide oxidised to dimethyl sulfoxide, a solvent that passes straight through skin.", wiki="Dimethyl_sulfoxide", dh=-100),
    R("Methanethiol", "Methanol + H2S -> Methanethiol + H2O", CAT,
      "The smell of bad breath and asparagus urine.", wiki="Methanethiol", cat="Alumina", T=350, dh=-30),
    R("Ethanethiol", "Ethanol + H2S -> Ethanethiol + H2O", CAT,
      "The smell added to odourless natural gas, detectable at one part in a billion.", wiki="Ethanethiol", cat="Alumina", T=350, dh=-30),
    R("Thiourea", "CaCN2 + 2 H2S -> Thiourea + CaS", MIX,
      "Calcium cyanamide and hydrogen sulfide give thiourea, a photographic toner and gold-leaching agent.", wiki="Thiourea", dh=-50),
    R("Cyanamide", "CaCN2 + H2SO4 -> Cyanamide + CaSO4", MIX,
      "Acid frees cyanamide from nitrolime.", wiki="Cyanamide", dh=-50),
    R("Guanidine", "Cyanamide + NH3 -> Guanidine", HEAT,
      "Ammonia adds to cyanamide.", wiki="Guanidine", T=150, dh=-50),
    R("Biuret", "2 Urea -> Biuret + NH3", HEAT,
      "Urea heated just above its melting point condenses to biuret, which gives proteins their violet colour test.", wiki="Biuret", T=150, dh=20),
    R("Cyanuric Acid", "3 Biuret -> 2 CyanuricAcid + 3 NH3", HEAT,
      "Further heating closes biuret into the cyanuric acid ring, the chlorine stabiliser of swimming pools.", wiki="Cyanuric_acid", T=250, dh=50),
    R("Glycolic Acid", "ClAcOH + NaOH -> GlycolicAcid + NaCl", HEAT,
      "Chloroacetic acid hydrolysed; glycolic acid is the skin peel of cosmetics counters.", wiki="Glycolic_acid", T=100, dh=-50),
    R("Glyoxylic Acid", "2 GlycolicAcid + O2 -> 2 GlyoxylicAcid + 2 H2O", HEAT,
      "Glycolic acid oxidised.", wiki="Glyoxylic_acid", T=80, dh=-200),
    R("Berzelius' Pyruvic Acid", "Tartaric -> PyruvicAcid + CO2 + H2O", DISTIL,
      "Berzelius (1835) distilled tartaric acid and got 'pyro-racemic acid'; it is the hub of every cell's metabolism.", wiki="Pyruvic_acid", T=200, dh=50),
    R("Tetrahydrofuran", "Furan + 2 H2 -> THF", CAT,
      "Furan hydrogenated over nickel to THF, the solvent of Grignard reactions.", wiki="Tetrahydrofuran", cat="Ni", T=100, dh=-150),
    R("Dioxane", "2 EO -> Dioxane", CAT,
      "Ethylene oxide dimerised with an acid catalyst.", wiki="1,4-Dioxane", cat="H2SO4", T=100, dh=-200),
    R("Methacrylic Acid", "MMA + H2O -> MethacrylicAcid + Methanol", HEAT,
      "The ester hydrolysed back to the acid.", wiki="Methacrylic_acid", T=100, dh=5),
    R("Maleic Anhydride", "2 Benzene + 9 O2 -> 2 MaleicAnhydride + 4 CO2 + 4 H2O", CAT,
      "Benzene vapour and air over vanadium oxide (Weiss and Downs, 1920).", wiki="Maleic_anhydride", cat="V2O5", T=400, dh=-3700),
    R("Aldol Condensation", "2 Acetaldehyde -> Crotonaldehyde + H2O", MIX,
      "Charles-Adolphe Wurtz (1872) found two acetaldehydes join in base: the aldol reaction, a staple of carbon-carbon bond making.", wiki="Aldol_condensation", dh=-30),
    R("Diacetone Alcohol", "2 Acetone -> DiacetoneAlcohol", MIX,
      "Two acetones joined by an aldol addition with a base.", wiki="Diacetone_alcohol", dh=-30),
    R("Wacker Process", "2 Ethylene + O2 -> 2 Acetaldehyde", MIX,
      "Hoechst and Wacker (1959): ethylene bubbled with air through a solution of palladium and copper chlorides; the copper keeps regenerating the palladium. The first industrial organopalladium reaction.", wiki="Wacker_process", T=120, dh=-440),
    R("Butanone", "2 2-Butene + O2 -> 2 MEK", CAT,
      "Wacker oxidation of butene gives methyl ethyl ketone.", wiki="Butanone", cat="Pd", T=100, dh=-400),
    R("Cyclopentanone", "Adipic -> Cyclopentanone + CO2 + H2O", HEAT,
      "Adipic acid heated with barium hydroxide loses carbon dioxide and closes into a five-membered ring.", wiki="Cyclopentanone", T=300, dh=80),
    R("Friedel-Crafts Acylation", "Benzene + AceticAnhydride -> Acetophenone + AcOH", CAT,
      "Charles Friedel and James Crafts (1877) found aluminium chloride lets acyl groups attack benzene.", wiki="Friedel-Crafts_reaction", cat="AlCl3", T=50, dh=-100),
    R("Benzophenone", "Benzene + BenzoylChloride -> Benzophenone + HCl", CAT,
      "Friedel-Crafts benzoylation: benzophenone, the UV blocker in plastics and sunscreen.", wiki="Benzophenone", cat="AlCl3", T=50, dh=-100),
    R("Phenylacetic Acid", "BenzylChloride + NaCN + 2 H2O -> PhenylaceticAcid + NaCl + NH3", HEAT,
      "Benzyl cyanide, made from benzyl chloride and cyanide, hydrolysed to phenylacetic acid, which smells of honey.", wiki="Phenylacetic_acid", T=100, dh=-150),
    R("Winckler's Mandelic Acid", "Benzaldehyde + HCN + 2 H2O -> MandelicAcid + NH3", MIX,
      "Ferdinand Winckler (1831) heated bitter almond extract with acid; mandel is German for almond.", wiki="Mandelic_acid", dh=-100),
    R("Anisole", "Phenol + Methanol -> Anisole + H2O", CAT,
      "Phenol methylated over alumina: anisole, the aniseed-scented ether.", wiki="Anisole", cat="Alumina", T=350, dh=-20),
    R("Diphenylamine", "2 Aniline -> Diphenylamine + NH3", HEAT,
      "Aniline heated with its hydrochloride; diphenylamine stabilises smokeless powder.", wiki="Diphenylamine", T=250, dh=10),
    R("Salicylamide", "MethylSalicylate + NH3 -> Salicylamide + Methanol", MIX,
      "Ammonia converts oil of wintergreen into salicylamide, a mild painkiller.", wiki="Salicylamide", dh=-20),
    R("Dimethyl Carbonate", "2 Methanol + COCl2 -> DMC + 2 HCl", MIX,
      "Methanol and phosgene; DMC is now made without phosgene as a green solvent.", wiki="Dimethyl_carbonate", dh=-100),
    R("Diethyl Carbonate", "2 Ethanol + COCl2 -> DEC + 2 HCl", MIX,
      "Ethanol and phosgene; diethyl carbonate is an electrolyte solvent in lithium batteries.", wiki="Diethyl_carbonate", dh=-100),
    R("Ethyl Chloroformate", "Ethanol + COCl2 -> EtChloroformate + HCl", COOL,
      "With phosgene in excess and kept cold, only one chlorine is replaced.", wiki="Ethyl_chloroformate", T=0, dh=-60),
    R("Monsanto Acetic Acid", "Methanol + CO -> AcOH", CAT,
      "Monsanto (1966) carbonylated methanol with a rhodium iodide catalyst: most acetic acid since has been made this way.", wiki="Monsanto_process", cat="Rh", T=180, P=30, dh=-135),
    R("Melamine Catalysed", "3 Cyanamide -> Melamine", CAT,
      "Three cyanamides trimerise into the melamine ring.", wiki="Melamine#Production", cat="Alumina", T=300, dh=-300),
]
E3.reactions += [
    R("Plisson's Aspartic Acid", "Asparagine + H2O -> AsparticAcid + NH3", HEAT,
      "Auguste Plisson (1827) boiled asparagine with alkali and got aspartic acid.", wiki="Aspartic_acid#History", T=100, dh=-20),
    R("Payen's Diastase", "Barley + Starch -> Maltose", MIX,
      "Payen and Persoz (1833) precipitated the starch-digesting principle of malt with alcohol: diastase, the first enzyme.", wiki="Amylase#History", exact=False),
    R("Proust's Mannitol", "Manna + Ethanol -> Mannitol", MIX,
      "Joseph Proust (1806) extracted mannitol from manna with hot alcohol.", wiki="Mannitol#History", exact=False),
    R("Wackenroder's Carotene", "Carrots + Ether -> Carotene", MIX,
      "Heinrich Wackenroder (1831) crystallised the orange pigment of carrot roots.", wiki="Beta-Carotene#History", exact=False),
    R("Schulze's Lupins", "Lupin + H2O -> Phenylalanine + Arginine", HEAT,
      "Ernst Schulze found phenylalanine (1879) and arginine (1886) in sprouting lupins.", wiki="Arginine#History", exact=False),
    R("Cramer's Serine", "Silk + H2SO4 -> Serine + Alanine", HEAT,
      "Emil Cramer (1865) boiled silk with sulfuric acid and found serine.", wiki="Serine#History", exact=False),
    R("Steam-Distilling Eucalyptus", "Eucalyptus -> Cineole", DISTIL,
      "Joseph Bosisto's Victorian distilleries (1852) sent eucalyptus oil around the world.", wiki="Eucalyptol", exact=False),
    R("Distilling Cumin", "Cumin -> Cuminaldehyde", DISTIL,
      "Cumin seed oil, rich in cuminaldehyde.", wiki="Cuminaldehyde", exact=False),
    R("Distilling Tarragon", "Tarragon -> Estragole", DISTIL,
      "Tarragon oil, mostly estragole.", wiki="Estragole", exact=False),
    R("Rutin from Buckwheat", "Buckwheat + Ethanol -> Rutin", MIX,
      "Rutin extracted from buckwheat leaves.", wiki="Rutin", exact=False),
    R("Distilling Lemongrass", "Lemongrass -> Geranial", DISTIL,
      "Lemongrass oil is up to 80% citral, mostly geranial.", wiki="Citral", exact=False),
]
E4.reactions += [
    R("Huber's Nicotinic Acid", "Nicotine + HNO3 -> NicotinicAcid", HEAT,
      "Hugo Weidel and C. Huber (1867-73) oxidised nicotine to nicotinic acid. Seventy years later it was found to be vitamin B3 and to cure pellagra.", wiki="Niacin#History", exact=False),
    R("Fischer's Casein Hydrolysis", "Cheese + HCl -> Valine + Proline + Lysine + Isoleucine + GlutamicAcid", HEAT,
      "Emil Fischer (1901) hydrolysed casein with acid and separated its amino acids as esters by distillation, finding proline and valine.", wiki="Proline#History", exact=False),
    R("Morner's Cysteine", "Horn + HCl -> Cysteine + Threonine", HEAT,
      "Karl Morner (1899) found cystine, two cysteines linked by sulfur, in hydrolysed horn.", wiki="Cysteine#History", exact=False),
    R("Ikeda's Umami", "Kombu + H2O -> MSG", HEAT,
      "Kikunae Ikeda (1908) boiled down kelp stock, crystallised glutamic acid from it, and patented its sodium salt as a seasoning.", wiki="Monosodium_glutamate#History", exact=False),
    R("Glutamic Acid to MSG", "GlutamicAcid + NaOH -> MSG + H2O", MIX,
      "Glutamic acid neutralised by caustic soda.", wiki="Monosodium_glutamate", dh=-50),
    R("Glutamine", "GlutamicAcid + NH3 -> Glutamine + H2O", HEAT,
      "Glutamic acid's side-chain acid turned into an amide.", wiki="Glutamine", T=100, dh=10),
    R("Takamine's Adrenaline", "AdrenalGlands + H2O -> Epinephrine", MIX,
      "Jokichi Takamine (1901) crystallised adrenaline from beef adrenal glands.", wiki="Adrenaline#History", exact=False),
    R("Koch's Wood Sugar", "Bran + H2O -> Xylose", HEAT,
      "Boiling oat hulls or wood with dilute acid gives xylose, 'wood sugar' (Koch, 1886).", wiki="Xylose", exact=False),
    R("Fischer's Xylitol", "Xylose + H2 -> Xylitol", CAT,
      "Emil Fischer (1891) reduced xylose; xylitol is the sugar-free sweetener that bacteria cannot eat.", wiki="Xylitol#History", cat="Ni", T=120, dh=-50),
    R("Ledderhose's Glucosamine", "CrabShells + HCl -> Glucosamine", HEAT,
      "Georg Ledderhose (1876) hydrolysed chitin from lobster shells into glucosamine.", wiki="Glucosamine#History", exact=False),
    R("Tomato Red", "Tomatoes + Ether -> Lycopene", MIX,
      "Lycopene extracted from tomato paste.", wiki="Lycopene", exact=False),
    R("Cooking Ginger", "Ginger -> Zingerone", HEAT,
      "Heat turns fresh ginger's gingerol into zingerone by a retro-aldol reaction.", wiki="Zingerone", exact=False),
]
E5.reactions += [
    R("Kuhn's Lactoflavin", "Whey + Ethanol -> Riboflavin", MIX,
      "Richard Kuhn (1933) extracted the yellow pigment of whey: riboflavin, vitamin B2.", wiki="Riboflavin#History", exact=False),
    R("Vitamin B6", "RiceBran + Ethanol -> Pyridoxine", MIX,
      "Pyridoxine isolated from rice bran (1938).", wiki="Pyridoxine#History", exact=False),
    R("Kogl's Biotin", "EggYolk + Ethanol -> Biotin", MIX,
      "Fritz Kogl (1936) isolated biotin from egg yolk.", wiki="Biotin#History", exact=False),
    R("Folic Acid from Spinach", "Spinach + H2O -> FolicAcid", MIX,
      "Mitchell, Snell and Williams (1941) concentrated folic acid from four tonnes of spinach.", wiki="Folate#History", exact=False),
    R("Vitamin A", "CodLiverOil + Ether -> Retinol", MIX,
      "Retinol separated from fish liver oil (Karrer, 1931; Nobel Prize 1937).", wiki="Retinol#History", exact=False),
    R("Splitting Carotene", "Carotene + 2 H2O -> 2 Retinol", MIX,
      "The body splits one beta-carotene into two vitamin A molecules; that is why carrots help night vision.", wiki="Beta-Carotene#Vitamin_A", dh=0),
    R("Sterols of Wool Grease", "Lanolin + Ethanol -> DHC", MIX,
      "7-Dehydrocholesterol extracted from lanolin.", wiki="7-Dehydrocholesterol", exact=False),
    R("Sunshine Vitamin", "DHC -> VitaminD3", LIGHT,
      "Ultraviolet light breaks a ring of 7-dehydrocholesterol and it rearranges into vitamin D3, as it does in sunlit skin (Windaus, 1936).", wiki="Cholecalciferol#Biosynthesis", dh=0),
    R("Tsujimoto's Squalane", "SharkLiverOil + H2 -> Squalane", CAT,
      "Shark liver squalene hydrogenated to squalane, a moisturiser that does not go rancid.", wiki="Squalane", cat="Ni", exact=False),
]

# --- generated inorganic families (rows were produced once by a helper that matched
# --- products against library entries with a description and Wikipedia link; edit freely)
L("(NH4)2C2O4", "Ammonium oxalate", "(NH4)2C2O4", "Solid")
L("(NH4)2HPO4", "Diammonium hydrogen phosphate", "(NH4)2HPO4", "Solid")
L("Ag2CO3", "Silver carbonate", "Ag2CO3", "Solid")
L("Ag2SO4", "Silver sulfate", "Ag2SO4", "Solid")
L("AgC2H3O2", "Silver acetate", "AgC2H3O2", "Solid")
L("AgSCN", "Silver thiocyanate", "AgSCN", "Solid")
L("Al(NO3)3", "Aluminum nitrate", "Al(NO3)3", "Solid")
L("Al2(SO4)3", "Aluminum sulfate", "Al2(SO4)3", "Solid")
L("AlF3", "Aluminum fluoride", "AlF3", "Solid")
L("B4C", "Boron carbide", "B4C", "Solid")
L("BCl3", "Boron trichloride", "BCl3", "Gas")
L("BN", "Boron nitride", "BN", "Solid")
L("Ba(C2H3O2)2", "Barium acetate", "Ba(C2H3O2)2", "Solid")
L("Ba(NO3)2", "Barium nitrate", "Ba(NO3)2", "Solid")
L("BaC2O4", "Barium oxalate", "BaC2O4", "Solid")
L("BaSO4", "Barium sulfate", "BaSO4", "Solid")
L("Ca(C18H35O2)2", "Calcium stearate", "Ca(C18H35O2)2", "Solid")
L("Ca(C3H5O2)2", "Calcium propionate", "Ca(C3H5O2)2", "Solid")
L("Ca(C3H5O3)2", "Calcium lactate", "Ca(C3H5O3)2", "Solid")
L("Ca(C7H5O2)2", "Calcium benzoate", "Ca(C7H5O2)2", "Solid")
L("Ca(CHO2)2", "Calcium formate", "Ca(CHO2)2", "Solid")
L("Ca(ClO)2", "Calcium hypochlorite", "Ca(ClO)2", "Solid")
L("Ca(NO3)2", "Calcium nitrate", "Ca(NO3)2", "Solid")
L("Ca3(C6H5O7)2", "Calcium Citrate", "Ca3(C6H5O7)2", "Solid")
L("CaBr2", "Calcium bromide", "CaBr2", "Solid")
L("CaH2", "Calcium hydride", "CaH2", "Solid")
L("CaI2", "Calcium iodide", "CaI2", "Solid")
L("CaO2", "Calcium peroxide", "CaO2", "Solid")
L("Cd(NO3)2", "Cadmium nitrate", "Cd(NO3)2", "Solid")
L("Co(C18H35O2)2", "Cobalt stearate", "Co(C18H35O2)2", "Solid")
L("Co(C2H3O2)2", "Cobalt diacetate", "Co(C2H3O2)2", "Solid")
L("Cu(NO3)2", "Cupric nitrate", "Cu(NO3)2", "Solid")
L("Fe(C2H3O2)2", "Ferrous acetate", "Fe(C2H3O2)2", "Solid")
L("Fe(NO3)3", "Ferric nitrate", "Fe(NO3)3", "Solid")
L("FeSO4", "Ferrous sulfate", "FeSO4", "Solid")
L("K2SiO3", "Potassium silicate", "K2SiO3", "Solid")
L("K3C6H5O7", "Tripotassium citrate", "K3C6H5O7", "Solid")
L("KC2H3O2", "Potassium acetate", "KC2H3O2", "Solid")
L("KC3H5O3", "Potassium lactate", "KC3H5O3", "Solid")
L("KC7H5O2", "Potassium benzoate", "KC7H5O2", "Solid")
L("KCHO2", "Potassium formate", "KCHO2", "Solid")
L("KNO2", "Potassium nitrite", "KNO2", "Solid")
L("KSCN", "Potassium thiocyanate", "KSCN", "Solid")
L("Li2C2O4", "Lithium oxalate", "Li2C2O4", "Solid")
L("Li2O", "Lithium oxide", "Li2O", "Solid")
L("Li2S", "Lithium sulfide", "Li2S", "Solid")
L("Li3C6H5O7", "Lithium citrate", "Li3C6H5O7", "Solid")
L("Li3PO4", "Trilithium phosphate", "Li3PO4", "Solid")
L("LiBr", "Lithium bromide", "LiBr", "Solid")
L("LiC18H35O2", "Lithium stearate", "LiC18H35O2", "Solid")
L("LiC2H3O2", "Lithium acetate", "LiC2H3O2", "Solid")
L("LiCHO2", "Lithium formate", "LiCHO2", "Solid")
L("LiF", "Lithium fluoride", "LiF", "Solid")
L("LiH", "Lithium hydride", "LiH", "Solid")
L("LiI", "Lithium iodide", "LiI", "Solid")
L("LiNO3", "Lithium nitrate", "LiNO3", "Solid")
L("LiOH", "Lithium hydroxide", "LiOH", "Solid")
L("Mg(C18H35O2)2", "Magnesium stearate", "Mg(C18H35O2)2", "Solid")
L("Mg(C2H3O2)2", "Magnesium acetate", "Mg(C2H3O2)2", "Solid")
L("Mg(NO3)2", "Magnesium nitrate", "Mg(NO3)2", "Solid")
L("MgO", "Magnesium oxide", "MgO", "Solid")
L("N2H4", "Hydrazine", "N2H4", "Liquid")
L("NH2OH", "Hydroxylamine", "NH2OH", "Solid")
L("NH4C18H33O2", "Ammonium oleate", "NH4C18H33O2", "Solid")
L("NH4C18H35O2", "Ammonium stearate", "NH4C18H35O2", "Solid")
L("NH4C2H3O2", "Ammonium acetate", "NH4C2H3O2", "Solid")
L("NH4C3H5O2", "Ammonium propionate", "NH4C3H5O2", "Solid")
L("NH4C3H5O3", "Ammonium lactate", "NH4C3H5O3", "Solid")
L("NH4CHO2", "Ammonium formate", "NH4CHO2", "Solid")
L("Na2C2O4", "Sodium oxalate", "Na2C2O4", "Solid")
L("Na2O", "Sodium oxide", "Na2O", "Solid")
L("Na2S", "Disodium sulfide", "Na2S", "Solid")
L("Na3PO4", "Trisodium phosphate", "Na3PO4", "Solid")
L("NaC2H3O2", "Sodium acetate", "NaC2H3O2", "Solid")
L("NaC3H5O2", "Sodium propionate", "NaC3H5O2", "Solid")
L("NaC3H5O3", "Sodium lactate", "NaC3H5O3", "Solid")
L("NaC7H5O2", "Sodium benzoate", "NaC7H5O2", "Solid")
L("NaClO3", "Sodium chlorate", "NaClO3", "Solid")
L("NaF", "Sodium fluoride", "NaF", "Solid")
L("NaH", "Sodium hydride", "NaH", "Solid")
L("NaHSO3", "Sodium bisulfite", "NaHSO3", "Solid")
L("NaNO2", "Sodium nitrite", "NaNO2", "Solid")
L("NaSCN", "Sodium thiocyanate", "NaSCN", "Solid")
L("Ni(C2H3O2)2", "Nickel acetate", "Ni(C2H3O2)2", "Solid")
L("Ni(NO3)2", "Nickel nitrate", "Ni(NO3)2", "Solid")
L("NiS", "Nickel sulfide", "NiS", "Solid")
L("PCl3", "Phosphorus trichloride", "PCl3", "Liquid")
L("PCl5", "Phosphorus pentachloride", "PCl5", "Solid")
L("POCl3", "Phosphorus oxychloride", "POCl3", "Liquid")
L("S2Cl2", "Sulfur monochloride", "S2Cl2", "Liquid")
L("SF6", "Sulfur hexafluoride", "SF6", "Gas")
L("Sb2O3", "Antimony trioxide", "Sb2O3", "Solid")
L("SnSO4", "Stannous sulfate", "SnSO4", "Solid")
L("Sr(NO3)2", "Strontium nitrate", "Sr(NO3)2", "Solid")
L("SrSO4", "Strontium sulfate", "SrSO4", "Solid")
L("Zn(C18H35O2)2", "Zinc stearate", "Zn(C18H35O2)2", "Solid")
LAB_INORGANIC = [
    R('Lithium in Water', '2 Li + 2 H2O -> 2 LiOH + H2', MIX,
      'Lithium reacts with water, fizzing out hydrogen and leaving a solution of lithium hydroxide.',
      wiki='https://en.wikipedia.org/?curid=548771'),
    R('Sodium in Water', '2 Na + 2 H2O -> 2 NaOH + H2', MIX,
      'Sodium reacts with water, fizzing out hydrogen and leaving a solution of sodium Hydroxide.',
      wiki='https://en.wikipedia.org/wiki/Alkali_metal#Reaction_with_water'),
    R('Potassium in Water', '2 K + 2 H2O -> 2 KOH + H2', MIX,
      'Potassium reacts with water, fizzing out hydrogen and leaving a solution of caustic Potash.',
      wiki='https://en.wikipedia.org/wiki/Alkali_metal#Reaction_with_water'),
    R('Calcium in Water', 'Ca + 2 H2O -> Ca(OH)2 + H2', MIX,
      'Calcium reacts with water, fizzing out hydrogen and leaving a solution of slaked Lime.',
      wiki='https://en.wikipedia.org/wiki/Alkali_metal#Reaction_with_water'),
    R('Burning Magnesium', '2 Mg + O2 -> 2 MgO', HEAT,
      'Magnesium burns with a blinding white light, the flash of early photography, giving magnesium oxide.',
      wiki='https://en.wikipedia.org/?curid=162269'),
    R('Burning Lithium', '4 Li + O2 -> 2 Li2O', HEAT,
      'Lithium burns with a crimson flame, giving lithium oxide.',
      wiki='https://en.wikipedia.org/?curid=5292611'),
    R('Burning Sodium', '4 Na + O2 -> 2 Na2O', HEAT,
      'Sodium burns with a yellow flame, giving sodium oxide.',
      wiki='https://en.wikipedia.org/?curid=2010826'),
    R('Burning Calcium', '2 Ca + O2 -> 2 CaO', HEAT,
      'Calcium burns with an orange-red flame, giving quicklime.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Barium', '2 Ba + O2 -> 2 BaO', HEAT,
      'Barium burns with a pale green flame, giving baryta.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Iron', '3 Fe + 2 O2 -> Fe3O4', HEAT,
      'Iron burns in pure oxygen in a shower of sparks, giving magnetite.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Nickel', '2 Ni + O2 -> 2 NiO', HEAT,
      'Nickel oxidises when heated, giving nickel(II) Oxide.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Cobalt', '2 Co + O2 -> 2 CoO', HEAT,
      'Cobalt oxidises when heated, giving cobalt(II) Oxide.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Titanium', 'Ti + O2 -> TiO2', HEAT,
      'Titanium burns with a brilliant white light, giving rutile.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Aluminium', '4 Al + 3 O2 -> 2 Alumina', HEAT,
      'Aluminium burns with a dazzling white light as powder, giving alumina.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Beryllium', '2 Be + O2 -> 2 BeO', HEAT,
      'Beryllium burns when finely divided, giving beryllium oxide.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Bismuth', '4 Bi + 3 O2 -> 2 Bi2O3', HEAT,
      'Bismuth burns with a blue flame, giving bismuth Oxide.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Antimony', '4 Sb + 3 O2 -> 2 Sb2O3', HEAT,
      'Antimony burns to white fumes, giving antimony trioxide.',
      wiki='https://en.wikipedia.org/?curid=2067882'),
    R('Burning Cadmium', '2 Cd + O2 -> 2 CdO', HEAT,
      'Cadmium burns to brown fumes, giving cadmium Oxide.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Yttrium', '4 Y + 3 O2 -> 2 Y2O3', HEAT,
      'Yttrium burns when heated, giving yttrium oxide.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Uranium', 'U + O2 -> Pitchblende', HEAT,
      'Uranium burns when finely divided, giving pitchblende.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Germanium', 'Ge + O2 -> GeO2', HEAT,
      'Germanium oxidises when heated, giving germanium Dioxide.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Vanadium', '4 V + 5 O2 -> 2 V2O5', HEAT,
      'Vanadium burns to an orange oxide, giving vanadium Pentoxide.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Molybdenum', '2 Mo + 3 O2 -> 2 MoO3', HEAT,
      'Molybdenum burns to white smoke, giving molybdenum Trioxide.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Tungsten', '2 W + 3 O2 -> 2 WO3', HEAT,
      'Tungsten burns when red-hot, giving tungsten Trioxide.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Chromium', '4 Cr + 3 O2 -> 2 Cr2O3', HEAT,
      'Chromium burns when strongly heated, giving chromium(III) Oxide.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Lead', '2 Pb + O2 -> 2 PbO', HEAT,
      'Lead melts and oxidises to litharge, giving litharge.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Tin', 'Sn + O2 -> Cassiterite', HEAT,
      'Tin burns when strongly heated, giving cassiterite.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Burning Thorium', 'Th + O2 -> ThO2', HEAT,
      'Thorium burns brilliantly, giving thoria.',
      wiki='https://en.wikipedia.org/wiki/Combustion'),
    R('Calcining Magnesite', 'MgCO3 -> MgO + CO2', HEAT,
      'Heated, magnesite gives off carbon dioxide and leaves magnesium oxide.',
      wiki='https://en.wikipedia.org/?curid=162269'),
    R('Calcining Lithium Carbonate', 'Li2CO3 -> Li2O + CO2', HEAT,
      'Heated, lithium Carbonate gives off carbon dioxide and leaves lithium oxide.',
      wiki='https://en.wikipedia.org/?curid=5292611'),
    R('Calcining White Lead', 'PbCO3 -> PbO + CO2', HEAT,
      'Heated, white Lead gives off carbon dioxide and leaves litharge.',
      wiki='https://en.wikipedia.org/wiki/Thermal_decomposition'),
    R('Calcining Calamine', 'Calamine -> ZnO + CO2', HEAT,
      'Heated, calamine gives off carbon dioxide and leaves zinc Oxide.',
      wiki='https://en.wikipedia.org/wiki/Thermal_decomposition'),
    R('Calcining Magnesium hydroxide', 'MgOH2 -> MgO + H2O', HEAT,
      'Heated, magnesium hydroxide gives off water and leaves magnesium oxide.',
      wiki='https://en.wikipedia.org/?curid=162269'),
    R('Calcining Lithium hydroxide', '2 LiOH -> Li2O + H2O', HEAT,
      'Heated, lithium hydroxide gives off water and leaves lithium oxide.',
      wiki='https://en.wikipedia.org/?curid=5292611'),
    R('Calcining Slaked Lime', 'Ca(OH)2 -> CaO + H2O', HEAT,
      'Heated, slaked Lime gives off water and leaves quicklime.',
      wiki='https://en.wikipedia.org/wiki/Thermal_decomposition'),
    R('Lithium nitrate', 'Li2CO3 + 2 HNO3 -> 2 LiNO3 + CO2 + H2O', MIX,
      'Lithium Carbonate fizzes in nitric acid, giving off carbon dioxide and leaving lithium nitrate.',
      wiki='https://en.wikipedia.org/?curid=934819'),
    R('Lithium acetate', 'Li2CO3 + 2 AcOH -> 2 LiC2H3O2 + CO2 + H2O', MIX,
      'Lithium Carbonate fizzes in acetic acid, giving off carbon dioxide and leaving lithium acetate.',
      wiki='https://en.wikipedia.org/?curid=2009410'),
    R('Trilithium phosphate', '3 Li2CO3 + 2 H3PO4 -> 2 Li3PO4 + 3 CO2 + 3 H2O', MIX,
      'Lithium Carbonate fizzes in phosphoric acid, giving off carbon dioxide and leaving trilithium phosphate.',
      wiki='https://en.wikipedia.org/?curid=79982165'),
    R('Lithium bromide', 'Li2CO3 + 2 HBr -> 2 LiBr + CO2 + H2O', MIX,
      'Lithium Carbonate fizzes in hydrobromic acid, giving off carbon dioxide and leaving lithium bromide.',
      wiki='https://en.wikipedia.org/?curid=2686966'),
    R('Lithium iodide', 'Li2CO3 + 2 HI -> 2 LiI + CO2 + H2O', MIX,
      'Lithium Carbonate fizzes in hydroiodic acid, giving off carbon dioxide and leaving lithium iodide.',
      wiki='https://en.wikipedia.org/?curid=2687248'),
    R('Lithium fluoride', 'Li2CO3 + 2 HF -> 2 LiF + CO2 + H2O', MIX,
      'Lithium Carbonate fizzes in hydrofluoric acid, giving off carbon dioxide and leaving lithium fluoride.',
      wiki='https://en.wikipedia.org/?curid=2687105'),
    R('Lithium formate', 'Li2CO3 + 2 Formic -> 2 LiCHO2 + CO2 + H2O', MIX,
      'Lithium Carbonate fizzes in formic acid, giving off carbon dioxide and leaving lithium formate.',
      wiki='https://en.wikipedia.org/?curid=81002375'),
    R('Lithium oxalate', 'Li2CO3 + Oxalic -> Li2C2O4 + CO2 + H2O', MIX,
      'Lithium Carbonate fizzes in oxalic acid, giving off carbon dioxide and leaving lithium oxalate.',
      wiki='https://en.wikipedia.org/?curid=67956151'),
    R('Lithium citrate', '3 Li2CO3 + 2 Citric -> 2 Li3C6H5O7 + 3 CO2 + 3 H2O', MIX,
      'Lithium Carbonate fizzes in citric acid, giving off carbon dioxide and leaving lithium citrate.',
      wiki='https://en.wikipedia.org/?curid=18236'),
    R('Lithium stearate', 'Li2CO3 + 2 StearicAcid -> 2 LiC18H35O2 + CO2 + H2O', MIX,
      'Lithium Carbonate fizzes in stearic acid, giving off carbon dioxide and leaving lithium stearate.',
      wiki='https://en.wikipedia.org/?curid=31331953'),
    R('Sodium acetate', 'SodaAsh + 2 AcOH -> 2 NaC2H3O2 + CO2 + H2O', MIX,
      'Soda Ash fizzes in acetic acid, giving off carbon dioxide and leaving sodium acetate.',
      wiki='https://en.wikipedia.org/?curid=1488243'),
    R('Trisodium phosphate', '3 SodaAsh + 2 H3PO4 -> 2 Na3PO4 + 3 CO2 + 3 H2O', MIX,
      'Soda Ash fizzes in phosphoric acid, giving off carbon dioxide and leaving trisodium phosphate.',
      wiki='https://en.wikipedia.org/?curid=309620'),
    R('Sodium fluoride', 'SodaAsh + 2 HF -> 2 NaF + CO2 + H2O', MIX,
      'Soda Ash fizzes in hydrofluoric acid, giving off carbon dioxide and leaving sodium fluoride.',
      wiki='https://en.wikipedia.org/?curid=1224339'),
    R('Sodium oxalate', 'SodaAsh + Oxalic -> Na2C2O4 + CO2 + H2O', MIX,
      'Soda Ash fizzes in oxalic acid, giving off carbon dioxide and leaving sodium oxalate.',
      wiki='https://en.wikipedia.org/?curid=2869867'),
    R('Sodium lactate', 'SodaAsh + 2 LacticAcid -> 2 NaC3H5O3 + CO2 + H2O', MIX,
      'Soda Ash fizzes in lactic acid, giving off carbon dioxide and leaving sodium lactate.',
      wiki='https://en.wikipedia.org/?curid=14263740'),
    R('Sodium benzoate', 'SodaAsh + 2 BenzoicAcid -> 2 NaC7H5O2 + CO2 + H2O', MIX,
      'Soda Ash fizzes in benzoic acid, giving off carbon dioxide and leaving sodium benzoate.',
      wiki='https://en.wikipedia.org/?curid=901291'),
    R('Sodium propionate', 'SodaAsh + 2 Propionic -> 2 NaC3H5O2 + CO2 + H2O', MIX,
      'Soda Ash fizzes in propionic acid, giving off carbon dioxide and leaving sodium propionate.',
      wiki='https://en.wikipedia.org/?curid=2249324'),
    R('Potassium acetate', 'Potash + 2 AcOH -> 2 KC2H3O2 + CO2 + H2O', MIX,
      'Potash fizzes in acetic acid, giving off carbon dioxide and leaving potassium acetate.',
      wiki='https://en.wikipedia.org/?curid=5063242'),
    R('Potassium formate', 'Potash + 2 Formic -> 2 KCHO2 + CO2 + H2O', MIX,
      'Potash fizzes in formic acid, giving off carbon dioxide and leaving potassium formate.',
      wiki='https://en.wikipedia.org/?curid=19623921'),
    R('Tripotassium citrate', '3 Potash + 2 Citric -> 2 K3C6H5O7 + 3 CO2 + 3 H2O', MIX,
      'Potash fizzes in citric acid, giving off carbon dioxide and leaving tripotassium citrate.',
      wiki='https://en.wikipedia.org/?curid=2044863'),
    R('Potassium lactate', 'Potash + 2 LacticAcid -> 2 KC3H5O3 + CO2 + H2O', MIX,
      'Potash fizzes in lactic acid, giving off carbon dioxide and leaving potassium lactate.',
      wiki='https://en.wikipedia.org/?curid=14263742'),
    R('Potassium benzoate', 'Potash + 2 BenzoicAcid -> 2 KC7H5O2 + CO2 + H2O', MIX,
      'Potash fizzes in benzoic acid, giving off carbon dioxide and leaving potassium benzoate.',
      wiki='https://en.wikipedia.org/?curid=703788'),
    R('Ammonium acetate', 'NH3 + AcOH -> NH4C2H3O2', MIX,
      'Ammonia neutralises acetic acid, leaving ammonium acetate.',
      wiki='https://en.wikipedia.org/?curid=3167641'),
    R('Ammonium formate', 'NH3 + Formic -> NH4CHO2', MIX,
      'Ammonia neutralises formic acid, leaving ammonium formate.',
      wiki='https://en.wikipedia.org/?curid=12618411'),
    R('Ammonium oxalate', '2 NH3 + Oxalic -> (NH4)2C2O4', MIX,
      'Ammonia neutralises oxalic acid, leaving ammonium oxalate.',
      wiki='https://en.wikipedia.org/?curid=31084710'),
    R('Ammonium lactate', 'NH3 + LacticAcid -> NH4C3H5O3', MIX,
      'Ammonia neutralises lactic acid, leaving ammonium lactate.',
      wiki='https://en.wikipedia.org/?curid=14263744'),
    R('Ammonium stearate', 'NH3 + StearicAcid -> NH4C18H35O2', MIX,
      'Ammonia neutralises stearic acid, leaving ammonium stearate.',
      wiki='https://en.wikipedia.org/?curid=79493513'),
    R('Ammonium propionate', 'NH3 + Propionic -> NH4C3H5O2', MIX,
      'Ammonia neutralises propionic acid, leaving ammonium propionate.',
      wiki='https://en.wikipedia.org/?curid=66856352'),
    R('Ammonium oleate', 'NH3 + OleicAcid -> NH4C18H33O2', MIX,
      'Ammonia neutralises oleic acid, leaving ammonium oleate.',
      wiki='https://en.wikipedia.org/?curid=79394812'),
    R('Magnesium nitrate', 'MgCO3 + 2 HNO3 -> Mg(NO3)2 + CO2 + H2O', MIX,
      'Magnesite fizzes in nitric acid, giving off carbon dioxide and leaving magnesium nitrate.',
      wiki='https://en.wikipedia.org/?curid=1753167'),
    R('Magnesium acetate', 'MgCO3 + 2 AcOH -> Mg(C2H3O2)2 + CO2 + H2O', MIX,
      'Magnesite fizzes in acetic acid, giving off carbon dioxide and leaving magnesium acetate.',
      wiki='https://en.wikipedia.org/?curid=23204429'),
    R('Magnesium stearate', 'MgCO3 + 2 StearicAcid -> Mg(C18H35O2)2 + CO2 + H2O', MIX,
      'Magnesite fizzes in stearic acid, giving off carbon dioxide and leaving magnesium stearate.',
      wiki='https://en.wikipedia.org/?curid=3137085'),
    R('Calcium nitrate', 'Limestone + 2 HNO3 -> Ca(NO3)2 + CO2 + H2O', MIX,
      'Limestone fizzes in nitric acid, giving off carbon dioxide and leaving calcium nitrate.',
      wiki='https://en.wikipedia.org/?curid=1737419'),
    R('Calcium bromide', 'Limestone + 2 HBr -> CaBr2 + CO2 + H2O', MIX,
      'Limestone fizzes in hydrobromic acid, giving off carbon dioxide and leaving calcium bromide.',
      wiki='https://en.wikipedia.org/?curid=5995665'),
    R('Calcium iodide', 'Limestone + 2 HI -> CaI2 + CO2 + H2O', MIX,
      'Limestone fizzes in hydroiodic acid, giving off carbon dioxide and leaving calcium iodide.',
      wiki='https://en.wikipedia.org/?curid=14623180'),
    R('Calcium formate', 'Limestone + 2 Formic -> Ca(CHO2)2 + CO2 + H2O', MIX,
      'Limestone fizzes in formic acid, giving off carbon dioxide and leaving calcium formate.',
      wiki='https://en.wikipedia.org/?curid=10107063'),
    R('Calcium Citrate', '3 Limestone + 2 Citric -> Ca3(C6H5O7)2 + 3 CO2 + 3 H2O', MIX,
      'Limestone fizzes in citric acid, giving off carbon dioxide and leaving calcium Citrate.',
      wiki='https://en.wikipedia.org/?curid=683071'),
    R('Calcium lactate', 'Limestone + 2 LacticAcid -> Ca(C3H5O3)2 + CO2 + H2O', MIX,
      'Limestone fizzes in lactic acid, giving off carbon dioxide and leaving calcium lactate.',
      wiki='https://en.wikipedia.org/?curid=2598849'),
    R('Calcium benzoate', 'Limestone + 2 BenzoicAcid -> Ca(C7H5O2)2 + CO2 + H2O', MIX,
      'Limestone fizzes in benzoic acid, giving off carbon dioxide and leaving calcium benzoate.',
      wiki='https://en.wikipedia.org/?curid=3773148'),
    R('Calcium stearate', 'Limestone + 2 StearicAcid -> Ca(C18H35O2)2 + CO2 + H2O', MIX,
      'Limestone fizzes in stearic acid, giving off carbon dioxide and leaving calcium stearate.',
      wiki='https://en.wikipedia.org/?curid=10933369'),
    R('Calcium propionate', 'Limestone + 2 Propionic -> Ca(C3H5O2)2 + CO2 + H2O', MIX,
      'Limestone fizzes in propionic acid, giving off carbon dioxide and leaving calcium propionate.',
      wiki='https://en.wikipedia.org/?curid=3556577'),
    R('Strontium sulfate', 'SrCO3 + H2SO4 -> SrSO4 + CO2 + H2O', MIX,
      'Strontianite fizzes in sulfuric acid, giving off carbon dioxide and leaving strontium sulfate.',
      wiki='https://en.wikipedia.org/?curid=8342547'),
    R('Strontium nitrate', 'SrCO3 + 2 HNO3 -> Sr(NO3)2 + CO2 + H2O', MIX,
      'Strontianite fizzes in nitric acid, giving off carbon dioxide and leaving strontium nitrate.',
      wiki='https://en.wikipedia.org/?curid=5297150'),
    R('Barium sulfate', 'BaCO3 + H2SO4 -> BaSO4 + CO2 + H2O', MIX,
      'Witherite fizzes in sulfuric acid, giving off carbon dioxide and leaving barium sulfate.',
      wiki='https://en.wikipedia.org/?curid=740874'),
    R('Barium nitrate', 'BaCO3 + 2 HNO3 -> Ba(NO3)2 + CO2 + H2O', MIX,
      'Witherite fizzes in nitric acid, giving off carbon dioxide and leaving barium nitrate.',
      wiki='https://en.wikipedia.org/?curid=1112725'),
    R('Barium acetate', 'BaCO3 + 2 AcOH -> Ba(C2H3O2)2 + CO2 + H2O', MIX,
      'Witherite fizzes in acetic acid, giving off carbon dioxide and leaving barium acetate.',
      wiki='https://en.wikipedia.org/?curid=23424772'),
    R('Barium oxalate', 'BaCO3 + Oxalic -> BaC2O4 + CO2 + H2O', MIX,
      'Witherite fizzes in oxalic acid, giving off carbon dioxide and leaving barium oxalate.',
      wiki='https://en.wikipedia.org/?curid=7495625'),
    R('Zinc stearate', 'Calamine + 2 StearicAcid -> Zn(C18H35O2)2 + CO2 + H2O', MIX,
      'Calamine fizzes in stearic acid, giving off carbon dioxide and leaving zinc stearate.',
      wiki='https://en.wikipedia.org/?curid=5024939'),
    R('Cadmium nitrate', 'CdO + 2 HNO3 -> Cd(NO3)2 + H2O', MIX,
      'Cadmium Oxide dissolves in nitric acid, and the solution leaves cadmium nitrate as it evaporates.',
      wiki='https://en.wikipedia.org/?curid=5401424'),
    R('Cupric nitrate', 'CuO + 2 HNO3 -> Cu(NO3)2 + H2O', MIX,
      'Copper(II) Oxide dissolves in nitric acid, and the solution leaves cupric nitrate as it evaporates.',
      wiki='https://en.wikipedia.org/?curid=556263'),
    R('Ferrous sulfate', 'Fe + H2SO4 -> FeSO4 + H2', MIX,
      'Iron dissolves in sulfuric acid with a stream of hydrogen bubbles, leaving ferrous sulfate.',
      wiki='https://en.wikipedia.org/?curid=158405'),
    R('Ferrous acetate', 'Fe + 2 AcOH -> Fe(C2H3O2)2 + H2', MIX,
      'Iron dissolves in acetic acid with a stream of hydrogen bubbles, leaving ferrous acetate.',
      wiki='https://en.wikipedia.org/?curid=3059513'),
    R('Ferric nitrate', 'Hematite + 6 HNO3 -> 2 Fe(NO3)3 + 3 H2O', MIX,
      'Hematite dissolves in nitric acid, and the solution leaves ferric nitrate as it evaporates.',
      wiki='https://en.wikipedia.org/?curid=5401557'),
    R('Nickel nitrate', 'NiO + 2 HNO3 -> Ni(NO3)2 + H2O', MIX,
      'Nickel(II) Oxide dissolves in nitric acid, and the solution leaves nickel nitrate as it evaporates.',
      wiki='https://en.wikipedia.org/?curid=5901542'),
    R('Nickel acetate', 'NiO + 2 AcOH -> Ni(C2H3O2)2 + H2O', MIX,
      'Nickel(II) Oxide dissolves in acetic acid, and the solution leaves nickel acetate as it evaporates.',
      wiki='https://en.wikipedia.org/wiki/2C-iBu'),
    R('Cobalt diacetate', 'CoO + 2 AcOH -> Co(C2H3O2)2 + H2O', MIX,
      'Cobalt(II) Oxide dissolves in acetic acid, and the solution leaves cobalt diacetate as it evaporates.',
      wiki='https://en.wikipedia.org/?curid=19624360'),
    R('Cobalt stearate', 'CoO + 2 StearicAcid -> Co(C18H35O2)2 + H2O', MIX,
      'Cobalt(II) Oxide dissolves in stearic acid, and the solution leaves cobalt stearate as it evaporates.',
      wiki='https://en.wikipedia.org/?curid=73047762'),
    R('Aluminum sulfate', '2 AlOH3 + 3 H2SO4 -> Al2(SO4)3 + 6 H2O', MIX,
      'Aluminium Hydroxide dissolves in sulfuric acid, and the solution leaves aluminum sulfate as it evaporates.',
      wiki='https://en.wikipedia.org/?curid=2035853'),
    R('Aluminum nitrate', 'AlOH3 + 3 HNO3 -> Al(NO3)3 + 3 H2O', MIX,
      'Aluminium Hydroxide dissolves in nitric acid, and the solution leaves aluminum nitrate as it evaporates.',
      wiki='https://en.wikipedia.org/?curid=3809994'),
    R('Aluminum fluoride', 'AlOH3 + 3 HF -> AlF3 + 3 H2O', MIX,
      'Aluminium Hydroxide dissolves in hydrofluoric acid, and the solution leaves aluminum fluoride as it evaporates.',
      wiki='https://en.wikipedia.org/?curid=5021571'),
    R('Stannous sulfate', 'Sn + H2SO4 -> SnSO4 + H2', MIX,
      'Tin dissolves in sulfuric acid with a stream of hydrogen bubbles, leaving stannous sulfate.',
      wiki='https://en.wikipedia.org/?curid=5302143'),
    R('Copper on an Iron Nail', 'Fe + CuSO4 -> FeSO4 + Cu', MIX,
      'An iron nail dipped in copper sulfate turns pink with copper as iron goes into solution. Paracelsus thought the iron had turned into copper.',
      wiki='https://en.wikipedia.org/wiki/Single_displacement_reaction'),
    R('Zinc in Copper Sulfate', 'Zn + CuSO4 -> ZnSO4 + Cu', MIX,
      'Zinc displaces copper from solution; the blue colour fades as copper settles out. The same reaction powers the Daniell cell (1836).',
      wiki='https://en.wikipedia.org/wiki/Daniell_cell'),
    R('Silver Tree', 'Cu + 2 AgNO3 -> Cu(NO3)2 + 2 Ag', MIX,
      "A copper wire in silver nitrate grows glittering silver crystals while the solution turns blue: the alchemists' Arbor Dianae.",
      wiki='https://en.wikipedia.org/wiki/Silver_nitrate#Reactions'),
    R('Lead Tree', 'Zn + PbNO32 -> ZnNO32 + Pb', MIX,
      'Zinc in lead nitrate solution sprouts a feathery tree of lead crystals, the Arbor Saturni.',
      wiki='https://en.wikipedia.org/wiki/Lead(II)_nitrate#Reactions'),
    R('Chlorine Frees Bromine', 'Cl2 + 2 KBr -> 2 KCl + Br2', MIX,
      'Chlorine water turns potassium bromide solution orange as bromine is released: chlorine is the stronger oxidiser.',
      wiki='https://en.wikipedia.org/wiki/Halogen#Reactivity'),
    R('Chlorine Frees Iodine', 'Cl2 + 2 KI -> 2 KCl + I2', MIX,
      'Chlorine turns potassium iodide solution brown with iodine.',
      wiki='https://en.wikipedia.org/wiki/Halogen#Reactivity'),
    R('Bromine Frees Iodine', 'Br2 + 2 KI -> 2 KBr + I2', MIX,
      "Bromine displaces iodine, but not chlorine: the halogens' order of reactivity.",
      wiki='https://en.wikipedia.org/wiki/Halogen#Reactivity'),
    R('Smoke Rings of Sal Ammoniac', 'NH3 + HCl -> NH4Cl', MIX,
      'Ammonia and hydrogen chloride meet in air and form a white cloud of ammonium chloride.',
      wiki='https://en.wikipedia.org/wiki/Ammonium_chloride'),
    R('Sodium in Chlorine', '2 Na + Cl2 -> 2 NaCl', HEAT,
      'Molten sodium plunged into chlorine burns with a yellow flare and becomes ordinary table salt.',
      wiki='https://en.wikipedia.org/wiki/Sodium_chloride#Chemistry'),
    R('Lithium and Sulfur', '2 Li + S -> Li2S', HEAT,
      'Heated together, lithium and sulfur combine with a glow into the sulfide.',
      wiki='https://en.wikipedia.org/?curid=2687467'),
    R('Sodium and Sulfur', '2 Na + S -> Na2S', HEAT,
      'Heated together, sodium and sulfur combine with a glow into the sulfide.',
      wiki='https://en.wikipedia.org/?curid=2916631'),
    R('Nickel and Sulfur', 'Ni + S -> NiS', HEAT,
      'Heated together, nickel and sulfur combine with a glow into the sulfide.',
      wiki='https://en.wikipedia.org/?curid=37325862'),
    R('Sodium Nitrite', '2 NaNO3 -> 2 NaNO2 + O2', HEAT,
      'Saltpetre of soda melts and gives off oxygen, leaving sodium nitrite, the curing salt of bacon and ham.',
      wiki='https://en.wikipedia.org/?curid=407615'),
    R('Potassium Nitrite', '2 KNO3 -> 2 KNO2 + O2', HEAT,
      'Saltpetre heated alone gives off oxygen and leaves potassium nitrite.',
      wiki='https://en.wikipedia.org/?curid=2106024'),
    R('Lead Nitrate Decrepitates', '2 PbNO32 -> 2 PbO + 4 NO2 + O2', HEAT,
      'Lead nitrate crackles in the flame and gives off brown nitrogen dioxide: the classic lab source of NO2.',
      wiki='https://en.wikipedia.org/wiki/Lead(II)_nitrate#Thermal_decomposition'),
    R('Silver from Lunar Caustic', '2 AgNO3 -> 2 Ag + 2 NO2 + O2', HEAT,
      'Silver nitrate, heated, leaves bright metallic silver.',
      wiki='https://en.wikipedia.org/wiki/Silver_nitrate'),
    R('Copper Nitrate Calcined', '2 Cu(NO3)2 -> 2 CuO + 4 NO2 + O2', HEAT,
      'Blue copper nitrate decomposes to black copper oxide.',
      wiki='https://en.wikipedia.org/wiki/Copper(II)_nitrate'),
    R('Sodium Chlorate', '3 NaClO -> NaClO3 + 2 NaCl', HEAT,
      'Hypochlorite disproportionates when warmed into chlorate and chloride.',
      wiki='https://en.wikipedia.org/?curid=1397202'),
    R('Calcium Peroxide', 'Ca(OH)2 + H2O2 -> CaO2 + 2 H2O', MIX,
      'Lime and hydrogen peroxide give calcium peroxide, which slowly releases oxygen in soil and fish tanks.',
      wiki='https://en.wikipedia.org/?curid=763076'),
    R('Potassium Thiocyanate', 'KCN + S -> KSCN', HEAT,
      'Fusing cyanide with sulfur makes thiocyanate, far less poisonous.',
      wiki='https://en.wikipedia.org/?curid=5063539'),
    R("Volhard's Precipitate", 'AgNO3 + KSCN -> AgSCN + KNO3', MIX,
      "Silver thiocyanate precipitates white: the endpoint of Volhard's titration (1874).",
      wiki='https://en.wikipedia.org/?curid=35211828'),
    R('Sodium Thiocyanate', 'NaCN + S -> NaSCN', HEAT,
      'Sodium cyanide fused with sulfur.',
      wiki='https://en.wikipedia.org/?curid=5064230'),
    R('Silver Carbonate', '2 AgNO3 + SodaAsh -> Ag2CO3 + 2 NaNO3', MIX,
      'Soda throws down pale yellow silver carbonate.',
      wiki='https://en.wikipedia.org/?curid=4602956'),
    R('Silver Sulfate', '2 Ag + 2 H2SO4 -> Ag2SO4 + SO2 + 2 H2O', HEAT,
      'Hot concentrated sulfuric acid dissolves silver.',
      wiki='https://en.wikipedia.org/?curid=4662815'),
    R('Silver Acetate', 'AgNO3 + NaC2H3O2 -> AgC2H3O2 + NaNO3', MIX,
      'Silver acetate crystallises from mixed silver nitrate and sodium acetate.',
      wiki='https://en.wikipedia.org/?curid=5020778'),
    R('Chalk from Two Solutions', 'CaCl2 + SodaAsh -> Limestone + 2 NaCl', MIX,
      'Two clear solutions mix into a milky white precipitate of calcium carbonate.',
      wiki='https://en.wikipedia.org/wiki/Precipitated_calcium_carbonate'),
    R('Silver Iodide Precipitate', 'AgNO3 + KI -> AgI + KNO3', MIX,
      'Yellow silver iodide: the iodide test.',
      wiki='https://en.wikipedia.org/wiki/Silver_iodide'),
    R('Ammonium Phosphate', 'H3PO4 + 2 NH3 -> (NH4)2HPO4', MIX,
      'Ammonia and phosphoric acid: fertilizer, and the flame retardant of fire-extinguisher powder.',
      wiki='https://en.wikipedia.org/?curid=1722958'),
    R('Sodium Sulfide', 'Na2SO4 + 4 Coke -> Na2S + 4 CO', SMELT,
      'Salt cake reduced with coke gives sodium sulfide, which unhairs hides in tanneries.',
      wiki='https://en.wikipedia.org/?curid=2916631'),
    R('Sodium Silicate Glass', 'Sand + 2 NaOH -> Na2SiO3 + H2O', HEAT,
      'Sand dissolves in hot caustic soda to water glass.',
      wiki='https://en.wikipedia.org/wiki/Sodium_silicate#Production'),
    R('Amphoteric Alumina', 'AlOH3 + NaOH -> NaAlOH4', MIX,
      'Aluminium hydroxide dissolves in alkali as well as acid: it is amphoteric.',
      wiki='https://en.wikipedia.org/wiki/Amphoterism'),
    R('Potassium Silicate', 'Sand + 2 KOH -> K2SiO3 + H2O', HEAT,
      'Sand in hot potash lye: potassium water glass, a binder for mineral paints.',
      wiki='https://en.wikipedia.org/?curid=2642633'),
    R('Calcium Hypochlorite', 'Ca(OH)2 + 2 NaClO -> Ca(ClO)2 + 2 NaOH', MIX,
      "Calcium hypochlorite, the 'chlorine' of swimming pools.",
      wiki='https://en.wikipedia.org/?curid=2898453'),
    R('Sodium Bisulfite', 'SO2 + NaOH -> NaHSO3', COOL,
      'Sulfur dioxide in cold caustic soda gives sodium bisulfite, a wine preservative.',
      wiki='https://en.wikipedia.org/?curid=30844503'),
    R('Lithium Hydride', '2 Li + H2 -> 2 LiH', HEAT,
      'Lithium absorbs hydrogen at red heat.',
      wiki='https://en.wikipedia.org/?curid=2196648'),
    R('Sodium Hydride', '2 Na + H2 -> 2 NaH', HEAT,
      'Sodium and hydrogen at 300 C give sodium hydride, a fierce base.',
      wiki='https://en.wikipedia.org/?curid=521877'),
    R('Calcium Hydride', 'Ca + H2 -> CaH2', HEAT,
      'Calcium hydride, a portable source of hydrogen for weather balloons.',
      wiki='https://en.wikipedia.org/?curid=4623969'),
    R('Boron Nitride', 'B2O3 + 2 NH3 -> 2 BN + 3 H2O', HEAT,
      "Boron oxide and ammonia at 1000 C give white boron nitride, 'white graphite'.",
      wiki='https://en.wikipedia.org/?curid=3370'),
    R('Boron Carbide', '2 B2O3 + 7 Coke -> B4C + 6 CO', SMELT,
      'Boron oxide and carbon in an arc furnace give boron carbide, hard enough for tank armour.',
      wiki='https://en.wikipedia.org/?curid=1095210'),
    R('Sulfur Hexafluoride', 'S + 3 F2 -> SF6', HEAT,
      'Sulfur burns in fluorine to an inert, heavy gas that insulates high-voltage switchgear.',
      wiki='https://en.wikipedia.org/?curid=457036'),
    R('Phosphorus Trichloride', 'P4 + 6 Cl2 -> 4 PCl3', HEAT,
      'Phosphorus burns in chlorine to phosphorus trichloride.',
      wiki='https://en.wikipedia.org/?curid=1758819'),
    R('Phosphorus Pentachloride', 'PCl3 + Cl2 -> PCl5', MIX,
      'More chlorine turns the trichloride into the pentachloride.',
      wiki='https://en.wikipedia.org/?curid=1758788'),
    R('Phosphoryl Chloride', '2 PCl3 + O2 -> 2 POCl3', MIX,
      'Phosphorus trichloride oxidised to phosphoryl chloride, a reagent for flame retardants.',
      wiki='https://en.wikipedia.org/?curid=2782231'),
    R('Boron Trichloride', 'B2O3 + 3 Coke + 3 Cl2 -> 2 BCl3 + 3 CO', HEAT,
      'Boron oxide chlorinated with carbon.',
      wiki='https://en.wikipedia.org/?curid=3873319'),
    R('Sulfur Chloride', '2 S + Cl2 -> S2Cl2', HEAT,
      'Sulfur and chlorine give the golden, fuming liquid used to vulcanise rubber in the cold.',
      wiki='https://en.wikipedia.org/?curid=4762467'),
    R('Hydrazine', '2 NH3 + NaClO -> N2H4 + NaCl + H2O', MIX,
      "Raschig's process (1907): ammonia oxidised by hypochlorite. Hydrazine fuels spacecraft thrusters.",
      wiki='https://en.wikipedia.org/?curid=69955'),
    R('Hydroxylamine', '2 NO + 3 H2 -> 2 NH2OH', CAT,
      'Nitric oxide hydrogenated over platinum gives hydroxylamine, the key to caprolactam.',
      wiki='https://en.wikipedia.org/?curid=314983', cat="Pt"),
    R('Sulfur Trioxide Hydrate', 'SO2 + H2O2 -> H2SO4', MIX,
      'Hydrogen peroxide oxidises sulfur dioxide straight to sulfuric acid.',
      wiki='https://en.wikipedia.org/wiki/Sulfuric_acid'),
]


# --- coal tar, petroleum and essential oils are mixtures of dozens of compounds ---
for _k, _n, _f, _s in [
    ("Quinoline", "Quinoline", "C9H7N", "Liquid"), ("Isoquinoline", "Isoquinoline", "C9H7N", "Liquid"),
    ("pCresol", "p-Cresol", "C7H8O", "Solid"), ("mCresol", "m-Cresol", "C7H8O", "Liquid"),
    ("oCresol", "o-Cresol", "C7H8O", "Solid"), ("Thiophene", "Thiophene", "C4H4S", "Liquid"),
    ("Phenanthrene", "Phenanthrene", "C14H10", "Solid"), ("Pyrene", "Pyrene", "C16H10", "Solid"),
    ("mXylene", "m-Xylene", "C8H10", "Liquid"), ("Isobutane", "Isobutane", "C4H10", "Gas"),
    ("Isopentane", "Isopentane", "C5H12", "Liquid"), ("Methylcyclohexane", "Methylcyclohexane", "C7H14", "Liquid"),
    ("2-Methylpentane", "2-Methylpentane", "C6H14", "Liquid"), ("Isooctane", "2,2,4-Trimethylpentane", "C8H18", "Liquid"),
    ("1-Butene", "1-Butene", "C4H8", "Gas"), ("Propyne", "Propyne", "C3H4", "Gas"), ("1-Butyne", "1-Butyne", "C4H6", "Gas"),
    ("Isoprene", "Isoprene", "C5H8", "Liquid"), ("Cyclopentadiene", "Cyclopentadiene", "C5H6", "Liquid"),
    ("DCPD", "Dicyclopentadiene", "C10H12", "Liquid"), ("Mesitylene", "Mesitylene", "C9H12", "Liquid"),
    ("Myrcene", "Myrcene", "C10H16", "Liquid"), ("Decanal", "Decanal", "C10H20O", "Liquid"), ("Octanal", "Octanal", "C8H16O", "Liquid"),
    ("bPinene", "β-Pinene", "C10H16", "Liquid"), ("Camphene", "(±)-Camphene", "C10H16", "Solid"),
    ("Terpinolene", "Terpinolene", "C10H16", "Liquid"), ("aTerpineol", "α-Terpineol", "C10H18O", "Liquid"),
    ("gTerpinene", "γ-Terpinene", "C10H16", "Liquid"), ("aTerpinene", "α-Terpinene", "C10H16", "Liquid"),
    ("pCymene", "p-Cymene", "C10H14", "Liquid"), ("Nerol", "Nerol", "C10H18O", "Liquid"),
    ("Phenylethanol", "2-Phenylethanol", "C8H10O", "Liquid"), ("CinnamylAcetate", "Cinnamyl acetate", "C11H12O2", "Liquid"),
    ("CinnamylAlcohol", "Cinnamyl alcohol", "C9H10O", "Solid"), ("Theophylline", "Theophylline", "C7H8N4O2", "Solid"),
    ("Digoxin", "Digoxin", "C41H64O14", "Solid"), ("ActiveAmyl", "2-Methyl-1-butanol", "C5H12O", "Liquid"),
    ("FurfurylAlcohol", "Furfuryl alcohol", "C5H6O2", "Liquid"), ("BenzylSalicylate", "Benzyl salicylate", "C14H12O3", "Liquid"),
    ("Guaiacol", "Guaiacol", "C7H8O2", "Liquid"), ("Isoeugenol", "Isoeugenol", "C10H12O2", "Liquid"),
    ("aIonone", "α-Ionone", "C13H20O", "Liquid"), ("bIonone", "β-Ionone", "C13H20O", "Liquid"),
    ("Adenine", "Adenine", "C5H5N5", "Solid"), ("Xanthine", "Xanthine", "C5H4N4O2", "Solid"),
    ("Allantoin", "Allantoin", "C4H6N4O3", "Solid"), ("AconiticAcid", "Aconitic acid", "C6H6O6", "Solid"),
    ("ItaconicAcid", "Itaconic acid", "C5H6O4", "Solid"), ("LevulinicAcid", "Levulinic acid", "C5H8O3", "Solid"),
    ("SorbicAcid", "Sorbic acid", "C6H8O2", "Solid"), ("Pentanoic", "Pentanoic acid", "C5H10O2", "Liquid"),
    ("Octanoic", "Octanoic acid", "C8H16O2", "Liquid"), ("Decanoic", "Decanoic acid", "C10H20O2", "Solid"),
    ("MyristicAcid", "Myristic acid", "C14H28O2", "Solid"), ("LinoleicAcid", "Linoleic acid", "C18H32O2", "Liquid"),
    ("RicinoleicAcid", "Ricinoleic acid", "C18H34O3", "Liquid"), ("Ricinine", "Ricinine", "C8H8N2O2", "Solid"),
    ("SebacicAcid", "Sebacic acid", "C10H18O4", "Solid"), ("UndecylenicAcid", "Undecylenic acid", "C11H20O2", "Liquid"),
    ("Heptanal", "Heptanal", "C7H14O", "Liquid"), ("AzelaicAcid", "Azelaic acid", "C9H16O4", "Solid"),
    ("NonanoicAcid", "Nonanoic acid", "C9H18O2", "Liquid"), ("SubericAcid", "Suberic acid", "C8H14O4", "Solid"),
    ("GlutaricAcid", "Glutaric acid", "C5H8O4", "Solid"), ("Azurite", "Azurite", "Cu3(CO3)2(OH)2", "Solid"),
    ("EthylValerate", "Ethyl valerate", "C7H14O2", "Liquid"), ("EthylOctanoate", "Ethyl octanoate", "C10H20O2", "Liquid"),
    ("MethylMyristate", "Methyl myristate", "C15H30O2", "Liquid"), ("IPM", "Isopropyl myristate", "C17H34O2", "Liquid"),
    ("IsovalericAcid", "Isovaleric acid", "C5H10O2", "Liquid"), ("EthylIsovalerate", "Ethyl isovalerate", "C7H14O2", "Liquid"),
    ("MethylLaurate", "Methyl laurate", "C13H26O2", "Liquid"), ("MethylPalmitate", "Methyl palmitate", "C17H34O2", "Solid"),
    ("IPP", "Isopropyl palmitate", "C19H38O2", "Liquid"), ("DibutylSebacate", "Dibutyl sebacate", "C18H34O4", "Liquid"),
    ("PotassiumSorbate", "Potassium sorbate", "C6H7KO2", "Solid"), ("GluconicAcid", "Gluconic acid", "C6H12O7", "Solid"),
    ("CaGluconate", "Calcium gluconate", "C12H22CaO14", "Solid"), ("NaGluconate", "Sodium gluconate", "C6H11NaO7", "Solid"),
]:
    L(_k, _n, _f, _s)
L("NaTartrate", "Sodium tartrate", "C4H4Na2O6", "Solid")
SUBSTANCES["Azurite"].color = "#2050c0"
for _k, _name, _desc, _wiki, _col in [
    ("Yeast", "Brewer's Yeast", "Saccharomyces, rich in nucleic acid. Albrecht Kossel (1885-1901) took yeast and thymus nucleic acids apart into their bases. Nobel Prize, 1910.", "Nucleobase#History", "#d8c090"),
    ("Comfrey", "Comfrey Root", "Knitbone, a folk remedy for wounds, rich in allantoin.", "Symphytum", "#405030"),
    ("Rowan", "Rowan Berries", "Mountain ash berries, from which A. W. Hofmann (1859) distilled parasorbic acid; boiled, it becomes sorbic acid, the preservative E200.", "Sorbus_aucuparia", "#e04010"),
    ("Valerian", "Valerian Root", "A sedative herb whose foot-sock smell is isovaleric acid.", "Valerian_(herb)", "#806040"),
    ("Nutmeg", "Nutmeg Butter", "Pressed from nutmegs; Lyon Playfair (1841) found myristic acid in it, named for Myristica.", "Nutmeg", "#a06030"),
    ("LinseedOil", "Linseed Oil", "Pressed from flax seed. Its linoleic and linolenic acids soak up oxygen and set hard: the binder of oil paint since the 15th century.", "Linseed_oil", "#d8b040"),
    ("CastorBeans", "Castor Beans", "Seeds of Ricinus communis, pressed for castor oil. The press cake is toxic and must be treated.", "Castor_oil_plant", "#5a4030"),
    ("Cork", "Cork", "The bark of the cork oak. Brugnatelli (1787) oxidised it with nitric acid to suberic acid, from suber, cork.", "Cork_(material)", "#c09060"),
]:
    RAW(_k, _name, _desc, _wiki, _col)
X("CastorOil", "Castor Oil", "C57H104O9", "Liquid", "About 90% ricinolein, an unusual fatty acid with an OH group. A purgative, a lubricant for early aero engines (hence Castrol), and a feedstock for nylon 11.", "Castor_oil", id=0)
X("Linoxyn", "Linoxyn", "mixture", "Solid", "The tough, rubbery film linseed oil becomes as it oxidises: dried oil paint.", "Drying_oil", id=0, balance="C")
X("Linoleum", "Linoleum", "mixture", "Solid", "Frederick Walton's 1860 floor covering: linoxyn, cork dust and rosin on jute. He named it from linum (flax) and oleum (oil).", "Linoleum", id=0, balance="C", color="#b07040")
X("Nylon610", "Nylon 6,10", "(C16H30N2O2)n", "Solid", "Hexamethylenediamine and sebacic acid from castor oil: a nylon that absorbs less water, used for bristles. The 'nylon rope trick' demonstration makes it.", "Nylon", id=0, balance="C16H30N2O2", props=["IsPolymer"])
X("Nylon11", "Nylon 11", "(C11H21NO)n", "Solid", "Rilsan (1955), the first bio-based nylon, made from castor oil via undecylenic acid.", "Nylon_11", id=0, balance="C11H21NO", props=["IsPolymer"])
X("Alkyd", "Alkyd Resin", "mixture", "Solid", "Glyptal (General Electric, 1927): glycerol and phthalic anhydride, the binder of most gloss paints.", "Alkyd", id=0, balance="C", props=["IsPolymer"])
X("Polyisoprene", "Synthetic Polyisoprene", "(C5H8)n", "Solid", "Goodrich (1954) polymerised isoprene with a Ziegler catalyst into a rubber chemically identical to the natural kind.", "Polyisoprene", id=0, balance="C5H8", props=["IsPolymer"])

def _more(epoch, name, products):
    for r in epoch.reactions:
        if r.name == name:
            lhs, rhs = r.equation.split(" -> ")
            r.equation = lhs + " -> " + " + ".join([rhs] + products)
            return
    raise SystemExit(f"no reaction {name!r} to extend")

_more(E3, "Distilling Coal Tar", ["Quinoline", "Isoquinoline", "pCresol", "mCresol", "oCresol", "Thiophene", "Phenanthrene", "Pyrene", "mXylene"])
_more(E3, "Distilling Wood", ["Guaiacol"])
_more(E4, "Refining Crude Oil", ["Methylcyclohexane", "2-Methylpentane"])
_more(E5, "Separating Natural Gas", ["Isobutane", "Isopentane"])
_more(E5, "Steam Cracking Naphtha", ["1-Butene", "Propyne", "1-Butyne", "Isoprene", "Cyclopentadiene"])
_more(E5, "Platforming", ["Mesitylene"])
_more(E2, "Pressing Orange Peel", ["Myrcene", "Decanal", "Octanal"])
_more(E1, "Rectifying Turpentine", ["bPinene", "Camphene", "Terpinolene"])
_more(E3, "Distilling Cumin", ["gTerpinene", "pCymene"])
_more(E1, "Distilling Thyme", ["aTerpinene"])
_more(E1, "Distilling Rose", ["Nerol", "Phenylethanol"])
_more(E1, "Distilling Cinnamon", ["CinnamylAcetate", "CinnamylAlcohol"])
_more(E3, "Runge's Caffeine", ["Theophylline"])
_more(E3, "Withering's Foxglove", ["Digoxin"])
_more(E2, "Aqua Vitae", ["ActiveAmyl"])
_more(E3, "Chevreul's Butyric Acid", ["Octanoic", "Decanoic"])
for _r in E3.reactions:
    if _r.name == "Runge's Caffeine":
        _r.desc += " Albrecht Kossel found theophylline in tea in 1888."

E0.reactions += [
    R("Roasting Azurite", "Azurite -> 3 CuO + 2 CO2 + H2O", HEAT,
      "Azurite, the deep blue copper carbonate ground for ultramarine-like blue paint since Egypt, roasts to black copper oxide.",
      wiki="Azurite", T=300, dh=150),
]
E3.reactions += [
    R("Kossel's Nucleobases", "Yeast + H2SO4 -> Adenine + Xanthine", HEAT,
      "Albrecht Kossel hydrolysed nucleic acid from yeast and thymus glands into its bases: adenine (1885), then guanine, cytosine, thymine and the deaminated xanthine.",
      wiki="Albrecht_Kossel", exact=False),
    R("Allantoin from Comfrey", "Comfrey + H2O -> Allantoin", HEAT,
      "Allantoin, first found in amniotic fluid (Vauquelin, 1800) and later in comfrey root: the soothing ingredient of skin creams.",
      wiki="Allantoin", exact=False),
    R("Baup's Aconitic Acid", "Citric -> AconiticAcid + H2O", HEAT,
      "Samuel Baup (1836) heated citric acid and it lost water to aconitic acid, the acid also found in monkshood (Aconitum).",
      wiki="Aconitic_acid", T=175, dh=30),
    R("Baup's Itaconic Acid", "AconiticAcid -> ItaconicAcid + CO2", DISTIL,
      "Distilled further, aconitic acid loses carbon dioxide: itaconic acid, an anagram of aconitic.",
      wiki="Itaconic_acid", T=200, dh=20),
    R("Mulder's Levulinic Acid", "Glucose -> LevulinicAcid + Formic + H2O", HEAT,
      "Gerardus Mulder (1840) boiled sugar with hydrochloric acid and got levulinic acid, now a promising biomass platform chemical.",
      wiki="Levulinic_acid", T=150, dh=-100),
    R("Hofmann's Sorbic Acid", "Rowan -> SorbicAcid", DISTIL,
      "Distilled rowan-berry oil gives parasorbic acid, which hydrolyses to sorbic acid (Hofmann, 1859).",
      wiki="Sorbic_acid#History", exact=False),
    R("Valerian Acid", "Valerian + H2O -> IsovalericAcid", DISTIL,
      "Steam distillation of valerian root.", wiki="Isovaleric_acid", exact=False),
    R("Playfair's Myristic Acid", "Nutmeg + H2O -> MyristicAcid + Glycerol", HEAT,
      "Nutmeg butter's trimyristin split into myristic acid and glycerol (Playfair, 1841).", wiki="Myristic_acid", exact=False),
    R("Splitting Linseed Oil", "LinseedOil + H2O -> LinoleicAcid + Glycerol", HEAT,
      "Linseed oil hydrolysed into its unsaturated fatty acids.", wiki="Linoleic_acid", exact=False),
    R("Oil Paint Drying", "LinseedOil + O2 -> Linoxyn", MIX,
      "Spread thin, linseed oil takes up oxygen from the air over days and cross-links into a solid film.", wiki="Drying_oil", exact=False),
    R("Pressing Castor Beans", "CastorBeans -> CastorOil + Ricinine", MIX,
      "The beans are pressed for oil; the alkaloid ricinine stays in the press cake.", wiki="Castor_oil#Production", exact=False),
    R("Splitting Castor Oil", "CastorOil + 3 H2O -> 3 RicinoleicAcid + Glycerol", HEAT,
      "Castor oil hydrolysed to ricinoleic acid.", wiki="Ricinoleic_acid", T=250, dh=50),
    R("Brugnatelli's Suberic Acid", "Cork + HNO3 -> SubericAcid", HEAT,
      "Luigi Brugnatelli (1787) boiled cork in nitric acid.", wiki="Suberic_acid", exact=False),
]
E4.reactions += [
    R("Walton's Linoleum", "Linoxyn + Cork + Rosin -> Linoleum", HEAT,
      "Oxidised linseed oil, ground cork and rosin pressed onto jute canvas.", wiki="Linoleum#History", exact=False),
    R("Caustic Fusion of Castor Oil", "RicinoleicAcid + NaOH -> SebacicAcid + Octanol2", HEAT,
      "Ricinoleic acid fused with caustic soda at 250 C splits into sebacic acid and 2-octanol.", wiki="Sebacic_acid#Production", T=250, exact=False),
    R("Krafft Pyrolysis", "RicinoleicAcid -> UndecylenicAcid + Heptanal", HEAT,
      "Friedrich Krafft (1877) cracked ricinoleic acid in a vacuum into undecylenic acid and heptanal.", wiki="Undecylenic_acid", T=500, dh=50),
    R("Tiemann's Violets", "Geranial + Acetone -> aIonone + H2O", MIX,
      "Tiemann and Kruger (1893) condensed citral with acetone and cyclised it with dilute acid: alpha-ionone, the scent of violets, with no violets.",
      wiki="Ionone#History", dh=-50),
    R("Beta-Ionone", "Geranial + Acetone -> bIonone + H2O", HEAT,
      "With concentrated sulfuric acid the ring closes the other way: beta-ionone, the starting point for synthetic vitamin A.",
      wiki="Ionone", T=50, dh=-50),
    R("Isomerising Eugenol", "Eugenol -> Isoeugenol", HEAT,
      "Hot potash shifts eugenol's double bond into conjugation: isoeugenol, the carnation scent and the route to vanillin.",
      wiki="Isoeugenol", T=200, dh=-10),
    R("Pine Oil", "Pinene + H2O -> aTerpineol", CAT,
      "Pinene hydrated with acid gives terpineol, the lilac scent of pine-oil cleaners.", wiki="Terpineol", cat="H2SO4", T=60, dh=-40),
    R("Gluconic Acid", "2 Glucose + O2 -> 2 GluconicAcid", MIX,
      "Boutroux (1880) saw bacteria oxidise glucose to gluconic acid; Aspergillus niger now does it industrially.", wiki="Gluconic_acid", dh=-500),
]
E5.reactions += [
    R("Alkylation", "Isobutane + 1-Butene -> Isooctane", CAT,
      "Hydrofluoric acid catalyses isobutane onto butene (1938), giving the branched isooctane that defines 100 on the octane scale.",
      wiki="Alkylation_unit", cat="HF", T=30, dh=-80),
    R("Reppe Carbonylation", "1-Butene + CO + H2O -> Pentanoic", CAT,
      "Walter Reppe's nickel carbonyl chemistry (1938) adds CO and water across a double bond.", wiki="Valeric_acid", cat="Ni", T=250, P=200, dh=-100),
    R("Cyclopentadiene Dimer", "2 Cyclopentadiene -> DCPD", MIX,
      "Left standing, cyclopentadiene joins with itself by a Diels-Alder reaction (Diels and Alder, 1928, Nobel 1950).", wiki="Diels-Alder_reaction", dh=-80),
    R("Furfuryl Alcohol", "Furfural + H2 -> FurfurylAlcohol", CAT,
      "Furfural hydrogenated over copper chromite; it sets into foundry resins with acid.", wiki="Furfuryl_alcohol", cat="Cu", T=150, dh=-60),
    R("Ozonolysis of Oleic Acid", "3 OleicAcid + 4 O3 -> 3 AzelaicAcid + 3 NonanoicAcid", MIX,
      "Ozone cuts oleic acid's double bond in two (Emery Industries, 1950s): azelaic acid for plastics, pelargonic acid for herbicides.",
      wiki="Ozonolysis", dh=-1000),
    R("Glutaric Acid", "2 Cyclopentanone + 3 O2 -> 2 GlutaricAcid", HEAT,
      "Cyclopentanone oxidised opens to glutaric acid.", wiki="Glutaric_acid", T=100, dh=-800),
    R("Nylon 6,10", "HMDA + SebacicAcid -> Nylon610 + 2 H2O", POLY,
      "Layer sebacoyl chloride over hexamethylenediamine and pull: a rope of nylon draws out of the interface.", wiki="Nylon#Nylon_6,10", T=250, dh=-30),
    R("Nylon 11", "UndecylenicAcid + NH3 -> Nylon11", POLY,
      "Undecylenic acid turned into 11-aminoundecanoic acid and polymerised: Rilsan, for fuel lines.", wiki="Nylon_11", exact=False),
    R("Glyptal", "Glycerol + PhthalicAnhydride -> Alkyd", POLY,
      "Glycerol and phthalic anhydride heated together set into a hard resin.", wiki="Alkyd#History", exact=False),
    R("Synthetic Natural Rubber", "Isoprene -> Polyisoprene", CAT,
      "Isoprene polymerised all cis, like the tree's rubber (Goodrich and Firestone, 1954).", wiki="Polyisoprene#Synthetic_polyisoprene", cat="TiCl4", T=50, dh=-75),
    R("Biodiesel from Coconut", "CoconutOil + 3 Methanol -> 3 MethylLaurate + Glycerol", CAT,
      "Transesterification with methanol and caustic soda: the fatty acid methyl esters of biodiesel.", wiki="Biodiesel#Production", cat="NaOH", T=60, dh=-10),
    R("Biodiesel from Palm", "PalmOil + 3 Methanol -> 3 MethylPalmitate + Glycerol", CAT,
      "Palm oil transesterified to methyl palmitate.", wiki="Biodiesel#Production", cat="NaOH", T=60, dh=-10),
]
ESTERS2 = [
    ("Pentanoic", "Ethanol", "EthylValerate", "a fruity apple note"),
    ("Octanoic", "Ethanol", "EthylOctanoate", "the pear-drop and apricot note of wine"),
    ("MyristicAcid", "Methanol", "MethylMyristate", "a waxy, orris-like perfume ingredient"),
    ("MyristicAcid", "Isopropanol", "IPM", "the light, non-greasy oil of skin creams"),
    ("IsovalericAcid", "Ethanol", "EthylIsovalerate", "the smell of blueberries and apples"),
    ("PalmiticAcid", "Isopropanol", "IPP", "an emollient in cosmetics"),
    ("Salicylic", "BenzylAlcohol", "BenzylSalicylate", "a sunscreen ingredient and fixative in perfumes"),
]
E4.reactions += [
    R(f"Making {SUBSTANCES[e].name}", f"{a} + {al} -> {e} + H2O", CAT,
      f"Acid and alcohol joined by Fischer esterification, with sulfuric acid as catalyst: {note}.",
      wiki="Fischer-Speier_esterification", cat="H2SO4", T=80, dh=-5)
    for a, al, e, note in ESTERS2
]
E4.reactions += [
    R("Dibutyl Sebacate", "SebacicAcid + 2 Butanol -> DibutylSebacate + 2 H2O", CAT,
      "A plasticiser for food-contact plastics.", wiki="Dibutyl_sebacate", cat="H2SO4", T=120, dh=-10),
]
E7_ORGANIC += [
    R("Potassium Sorbate", "SorbicAcid + KOH -> PotassiumSorbate + H2O", MIX,
      "The preservative E202 in wine, cheese and bread.", wiki="Potassium_sorbate", dh=-50),
    R("Sodium Tartrate", "Tartaric + 2 NaOH -> NaTartrate + 2 H2O", MIX,
      "Tartaric acid neutralised by caustic soda.", wiki="Sodium_tartrate", dh=-100),
    R("Sodium Gluconate", "GluconicAcid + NaOH -> NaGluconate + H2O", MIX,
      "A chelating agent that keeps concrete workable and cleans bottles.", wiki="Sodium_gluconate", dh=-50),
    R("Calcium Gluconate", "2 GluconicAcid + Limestone -> CaGluconate + CO2 + H2O", MIX,
      "The calcium given intravenously for low blood calcium and hydrofluoric acid burns.", wiki="Calcium_gluconate", dh=-50),
]

E7 = Epoch("The Laboratory", "every age", LAB_INORGANIC + E7_ORGANIC)

# ======================================================================================
# THE STARTING KIT
# ======================================================================================
START = ["Wood", "H2O", "O2", "Clay", "Malachite", "Cassiterite", "Hematite", "Limestone",
         "Sand", "Calamine"]

# MILESTONES, the ladder of unlocks and grants, is set in authored_tiers.py next to the
# tier vessels it unlocks.

EPOCHS = [E0, E1, E2, E3, E4, E5, E6, E7]

# ======================================================================================
# STRUCTURES: SMILES for the new molecules, drawn into assets/structures/{id}.png by
# `gen_authored.py --render`. Polymers are drawn as one repeat unit between * bonds.
# Minerals, alloys and mixtures get a formula tile instead.
# ======================================================================================
SMILES = {
    "SoftSoap": "CCCCCCCCCCCCCCCCCC(=O)[O-].[K+]", "CuOAc2": "CC(=O)[O-].CC(=O)[O-].[Cu+2]",
    "PbOAc2": "CC(=O)[O-].CC(=O)[O-].[Pb+2]", "NH4OCN": "[NH4+].[O-]C#N",
    "Indican": "OC[C@H]1O[C@@H](Oc2c[nH]c3ccccc23)[C@H](O)[C@@H](O)[C@@H]1O",
    "Indigo": "O=C1C(=C2Nc3ccccc3C2=O)Nc2ccccc12",
    "Alizarin": "O=C1c2ccccc2C(=O)c2c1ccc(O)c2O", "PhthalicAnhydride": "O=C1OC(=O)c2ccccc12",
    "Methane": "C", "Ethane": "CC", "Propane": "CCC", "Octane": "CCCCCCCC", "Hexadecane": "CCCCCCCCCCCCCCCC",
    "BSA": "OS(=O)(=O)c1ccccc1", "EDC": "ClCCCl", "MMA": "C=C(C)C(=O)OC", "Vinylacetylene": "C=CC#C",
    "Chloroprene": "C=CC(Cl)=C", "Me2SiCl2": "C[Si](C)(Cl)Cl", "BPA": "CC(C)(c1ccc(O)cc1)c1ccc(O)cc1",
    "Nitrotoluene": "Cc1ccc(cc1)[N+](=O)[O-]", "PABA": "Nc1ccc(cc1)C(=O)O",
    "DDT": "Clc1ccc(cc1)C(c1ccc(Cl)cc1)C(Cl)(Cl)Cl", "Sorbitol": "OC[C@H](O)[C@@H](O)[C@H](O)[C@H](O)CO",
    "Penicillin": "CC1(C)S[C@@H]2[C@H](NC(=O)Cc3ccccc3)C(=O)N2[C@H]1C(=O)O", "Dodecanol": "CCCCCCCCCCCCO",
    "Bromobenzene": "Brc1ccccc1", "PhMgBr": "Br[Mg]c1ccccc1", "MAI": "C[NH3+].[I-]", "PhB(OH)2": "OB(O)c1ccccc1",
    "IBAP": "CC(C)Cc1ccc(cc1)C(C)=O", "IBPE": "CC(C)Cc1ccc(cc1)C(C)O",
    "Lactose": "OC[C@H]1O[C@@H](O[C@H]2[C@H](O)[C@@H](O)C(O)O[C@@H]2CO)[C@H](O)[C@@H](O)[C@H]1O",
    "Artemisinin": "C[C@@H]1CC[C@H]2[C@@H](C)C(=O)O[C@@H]3O[C@@]4(C)CC[C@@H]1[C@]32OO4",
    "Tartaric": "OC(C(O)C(=O)O)C(=O)O", "BenzoicAcid": "OC(=O)c1ccccc1", "CinnamicAcid": "OC(=O)/C=C/c1ccccc1",
    "Turpentine": "CC1=CCC2CC1C2(C)C", "Rosin": "CC(C)C1=CC2=CCC3C(C)(CCCC3(C)C(=O)O)C2CC1",
    "Salicin": "OC[C@H]1O[C@@H](Oc2ccccc2CO)[C@H](O)[C@@H](O)[C@@H]1O", "StearicAcid": "CCCCCCCCCCCCCCCCCC(=O)O",
    "Butanol": "CCCCO", "Salicylaldehyde": "O=Cc1ccccc1O", "Alanine": "CC(N)C(=O)O",
    "Guncotton": "*OC1C(O[N+](=O)[O-])C(O[N+](=O)[O-])C(CO[N+](=O)[O-])OC1*",
    # polymers (repeat units)
    "PVC": "*CC(Cl)*", "PS": "*CC(c1ccccc1)*", "PTFE": "*C(F)(F)C(F)(F)*", "GoreTex": "*C(F)(F)C(F)(F)*",
    "PET": "*OCCOC(=O)c1ccc(cc1)C(=O)*", "PMMA": "*CC(C)(C(=O)OC)*", "Nylon6": "*NCCCCCC(=O)*",
    "Neoprene": "*CC(Cl)=CC*", "PP": "*CC(C)*", "HDPE": "*CC*", "PDMS": "*O[Si](C)(C)*",
    "Kevlar": "*Nc1ccc(cc1)NC(=O)c1ccc(cc1)C(=O)*", "PC": "*Oc1ccc(cc1)C(C)(C)c1ccc(cc1)OC(=O)*",
    "PAN": "*CC(C#N)*", "PVAc": "*CC(OC(C)=O)*", "PLA": "*OC(C)C(=O)*", "Nylon610": "*NCCCCCCNC(=O)CCCCCCCCC(=O)*",
    "Nylon11": "*NCCCCCCCCCCC(=O)*", "Polyisoprene": "*C/C(C)=C\\C*", "PU": "*C(=O)Nc1ccc(C)c(c1)NC(=O)OCCO*",
    "SBR": "*CC=CCCC(c1ccccc1)*", "Rayon": "*OC1C(O)C(O)C(CO)OC1*", "Cellulose": "*OC1C(O)C(O)C(CO)OC1*",
    "Rubber": "*C/C(C)=C\\C*", "Epoxy": "*OCC(O)COc1ccc(cc1)C(C)(C)c1ccc(cc1)*",
}
for _k, _sm in SMILES.items():
    SUBSTANCES[_k].smiles = _sm

# The tier vessels, their recipes, the laboratory families and the milestone ladder.
import authored_tiers  # noqa: E402,F401  (extends the epochs above and sets MILESTONES)
# Pages for in-play substances whose library text the licence audit removed.
import authored_pages  # noqa: E402,F401
# Industrial chemistry from the canon production list, largest first.
import authored_canon  # noqa: E402,F401
# Locked previews of later stages (medicines without a route yet); always last, after every route.
import authored_placeholders  # noqa: E402,F401
