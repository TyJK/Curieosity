"""
Curieosity's glossary: the chemistry words the game's pages use, each with a short
definition written for a newcomer, the Wikipedia article that explains it, and (where the
curriculum has one) the lesson that teaches it.

tools/data/gen_pages.py reads TERMS, finds which terms each substance's page and each
lesson actually uses, and writes the glossary into assets/data/pages.ron. The game marks
those words in the text and lists them under the page, where a tap shows the definition.

G(key, term, forms, wiki, text, lesson=None, also=())
  key     how the rest of the data refers to the term
  term    the word as a heading
  forms   the words in running text that mean it, lowercase (a form with a capital letter,
          like "pH", matches only as written); a plain noun also matches its plural (forms
          ending in "y", "s", "x", "ch" or "sh" get "ies"/"es"). Only senses the game's text
          uses in the chemical meaning: "reduction" alone is left out because medicine
          pages speak of a reduction in symptoms.
  wiki    the Wikipedia article (redirects are followed, so a common spelling is enough)
  text    the definition, a sentence or two
  lesson  a curriculum topic key; left out, it is found from the article title
  also    terms that come along whenever this one is on a page: nitrite brings the rule
          behind -ate and -ite
"""

import re

TERMS = {}


def G(key, term, forms, wiki, text, lesson=None, plural=True, also=()):
    assert key not in TERMS, f"glossary key {key!r} twice"
    assert len(text) <= 330, f"{key}: definition is {len(text)} characters (330 at most)"
    out = []
    for f in forms:
        out.append(f)
        if plural and f[-1:].isalpha() and f.islower() and not f.endswith(("ic", "ous", "al", "ive", "ble", "ed", "ing", "ent", "ant", "ar")):
            if f.endswith("y") and f[-2:-1] not in "aeiou":
                out.append(f[:-1] + "ies")
            elif f.endswith(("s", "x", "ch", "sh")):
                out.append(f + "es")
            else:
                out.append(f + "s")
    TERMS[key] = {"term": term, "forms": sorted(set(out), key=lambda s: (-len(s), s)), "wiki": wiki, "text": text,
                  "lesson": lesson, "also": list(also)}


def prefixed(root, prefixes=("mono", "di", "tri", "tetra", "penta", "hexa", "sesqui")):
    """oxide -> oxide, monoxide, dioxide, trioxide, tetroxide, pentoxide, ... (a prefix ending
    in a vowel drops it before one)."""
    out = [root]
    for p in prefixes:
        out.append((p[:-1] if p[-1] in "ao" and root[0] in "aeiou" else p) + root)
    return out


# --------------------------------------------------------------------------------------
# Naming ions and salts: what the endings mean
# --------------------------------------------------------------------------------------
G("Ion", "Ion", ["ion"], "Ion",
  "An atom or group of atoms with an electric charge, because it has gained or lost electrons. "
  "Salts are built from ions held together by their opposite charges.", lesson="Ion")
G("Anion", "Anion", ["anion"], "Ion",
  "A negatively charged ion: it has gained electrons. Chloride (Cl⁻), sulfate (SO₄²⁻) and "
  "hydroxide (OH⁻) are anions.", lesson="Ion")
G("Cation", "Cation", ["cation"], "Ion",
  "A positively charged ion: it has lost electrons. Metals form cations, such as sodium (Na⁺) "
  "and calcium (Ca²⁺); ammonium (NH₄⁺) is one made of several atoms.", lesson="Ion")
G("PolyatomicIon", "Polyatomic ion", ["polyatomic ion"], "Polyatomic ion",
  "An ion made of several atoms bonded together that moves through reactions as one unit, "
  "like nitrate (NO₃⁻), sulfate (SO₄²⁻) or ammonium (NH₄⁺).")
G("Salt", "Salt", ["salt"], "Salt (chemistry)",
  "A compound of cations and anions, the product of an acid meeting a base. Table salt is one "
  "(sodium chloride); so are chalk, saltpetre and alum.", lesson="Salt")
G("IdeEnding", "-ide", ["selenide", "telluride", "phosphide", "arsenide", "antimonide", "boride", "silicide"],
  "Binary compound",
  "The ending of an anion made from a single element: chloride (Cl⁻) from chlorine, oxide "
  "(O²⁻) from oxygen, sulfide (S²⁻) from sulfur. A few groups keep it too: hydroxide (OH⁻) "
  "and cyanide (CN⁻).", plural=False)
G("Chloride", "Chloride", prefixed("chloride"), "Chloride",
  "The chloride ion, Cl⁻: a chlorine atom that has gained one electron, or a compound "
  "containing it. Sodium chloride is table salt. Not to be confused with chlorate (ClO₃⁻) or "
  "chlorite (ClO₂⁻), which carry oxygen.", also=["IdeEnding"])
G("Bromide", "Bromide", prefixed("bromide"), "Bromide",
  "The bromide ion, Br⁻, or a compound containing it. Silver bromide's sensitivity to light "
  "made photographic film possible.", also=["IdeEnding"])
G("Iodide", "Iodide", prefixed("iodide"), "Iodide",
  "The iodide ion, I⁻, or a compound containing it. Potassium iodide is the iodine added to "
  "table salt.", also=["IdeEnding"])
G("Fluoride", "Fluoride", prefixed("fluoride"), "Fluoride",
  "The fluoride ion, F⁻, or a compound containing it. Small amounts harden tooth enamel; "
  "fluorine's compounds range from toothpaste to Teflon.", also=["IdeEnding"])
G("Oxide", "Oxide", prefixed("oxide") + ["suboxide"], "Oxide",
  "A compound of oxygen with another element. A prefix counts the oxygens: carbon monoxide "
  "(CO) has one, carbon dioxide (CO₂) two, sulfur trioxide (SO₃) three. Rust and quicklime "
  "are oxides.", also=["IdeEnding"])
G("Peroxide", "Peroxide", ["peroxide"], "Peroxide",
  "A compound with two oxygen atoms bonded to each other (O–O), like hydrogen peroxide "
  "(H₂O₂). That weak bond breaks easily, which makes peroxides bleaches and oxidizers.")
G("Hydroxide", "Hydroxide", prefixed("hydroxide"), "Hydroxide",
  "The hydroxide ion, OH⁻: one oxygen and one hydrogen. Metal hydroxides such as lye (NaOH) "
  "and slaked lime (Ca(OH)₂) are bases.", also=["IdeEnding"])
G("Sulfide", "Sulfide", prefixed("sulfide") + prefixed("sulphide"), "Sulfide",
  "The sulfide ion, S²⁻, or a compound of sulfur with another element and no oxygen. Many "
  "metal ores are sulfides, like galena (lead sulfide) and pyrite. Compare sulfite and "
  "sulfate, which carry oxygen.", also=["IdeEnding"])
G("Nitride", "Nitride", prefixed("nitride"), "Nitride",
  "A compound of nitrogen with a less electronegative element and no oxygen, such as "
  "silicon nitride or gallium nitride, the blue LED's material.", also=["IdeEnding"])
G("Carbide", "Carbide", prefixed("carbide"), "Carbide",
  "A compound of carbon with a metal or metalloid. Calcium carbide fizzes acetylene in "
  "water; tungsten carbide is hard enough to cut steel.", also=["IdeEnding"])
G("Hydride", "Hydride", prefixed("hydride"), "Hydride",
  "A compound of hydrogen with another element in which hydrogen carries a negative charge, "
  "H⁻, as in sodium hydride or lithium aluminium hydride, strong reducing agents.", also=["IdeEnding"])
G("Cyanide", "Cyanide", ["cyanide"], "Cyanide",
  "The cyanide group, C≡N, one carbon triple-bonded to nitrogen. As the ion CN⁻ it is a deadly "
  "poison that blocks cells from using oxygen; it also dissolves gold from ore.", also=["IdeEnding"])
G("AteIte", "-ate and -ite", [], "Polyatomic ion",
  "Endings of anions that carry oxygen. The -ate ion has more oxygen, the -ite one less: "
  "nitrate is NO₃⁻ and nitrite NO₂⁻; sulfate is SO₄²⁻ and sulfite SO₃²⁻. Per- adds one "
  "oxygen more (perchlorate) and hypo- takes one more away (hypochlorite).", plural=False)
G("Nitrate", "Nitrate", ["nitrate"], "Nitrate",
  "The nitrate ion, NO₃⁻: one nitrogen and three oxygens, or a salt containing it, such as "
  "saltpetre (potassium nitrate). It has one oxygen more than nitrite (NO₂⁻), and gives that "
  "oxygen up readily, which is why nitrates feed gunpowder and plants.", also=["AteIte"])
G("Nitrite", "Nitrite", ["nitrite"], "Nitrite",
  "The nitrite ion, NO₂⁻: one nitrogen and two oxygens, one oxygen fewer than nitrate (NO₃⁻). "
  "Sodium nitrite cures meat pink; nitrites are made by taking oxygen away from nitrates.", also=["AteIte"])
G("Sulfate", "Sulfate", ["sulfate", "sulphate", "bisulfate", "bisulphate", "hydrogen sulfate"], "Sulfate",
  "The sulfate ion, SO₄²⁻: one sulfur and four oxygens, or a salt containing it, such as "
  "gypsum (calcium sulfate) or blue vitriol (copper sulfate). Sulfite (SO₃²⁻) has one oxygen "
  "fewer; sulfide has none.", also=["AteIte"])
G("Sulfite", "Sulfite", ["sulfite", "sulphite", "bisulfite", "bisulphite"], "Sulfite",
  "The sulfite ion, SO₃²⁻: one sulfur and three oxygens, one fewer than sulfate. Sulfites "
  "take up oxygen readily, which is why they preserve wine and dried fruit.", also=["AteIte"])
G("Thiosulfate", "Thiosulfate", ["thiosulfate", "thiosulphate"], "Thiosulfate",
  "S₂O₃²⁻: a sulfate with one oxygen swapped for sulfur (thio- means sulfur). Sodium "
  "thiosulfate is the photographer's 'hypo' that fixes an image.", also=["AteIte"])
G("Chlorate", "Chlorate", ["chlorate"], "Chlorate",
  "The chlorate ion, ClO₃⁻: chlorine with three oxygens, or a salt containing it. A powerful "
  "oxidizer used in matches and fireworks. Perchlorate has four oxygens, chlorite two, "
  "hypochlorite one, chloride none.", also=["AteIte"])
G("Perchlorate", "Perchlorate", ["perchlorate"], "Perchlorate",
  "The perchlorate ion, ClO₄⁻: chlorine with four oxygens, the most of the chlorine series "
  "(per- means 'beyond' the -ate). Ammonium perchlorate is the oxidizer in solid rocket fuel.", also=["AteIte"])
G("Chlorite", "Chlorite", ["chlorite"], "Chlorite",
  "The chlorite ion, ClO₂⁻: chlorine with two oxygens, one fewer than chlorate. (Chlorite is "
  "also the name of an unrelated green mineral.)", also=["AteIte"])
G("Hypochlorite", "Hypochlorite", ["hypochlorite"], "Hypochlorite",
  "The hypochlorite ion, ClO⁻: chlorine with a single oxygen, the fewest of the series (hypo- "
  "means 'under' the -ite). Sodium hypochlorite in water is household bleach.", also=["AteIte"])
G("Carbonate", "Carbonate", ["carbonate"], "Carbonate",
  "The carbonate ion, CO₃²⁻, or a salt containing it: chalk, limestone and marble are "
  "calcium carbonate, and washing soda is sodium carbonate. Acids fizz carbon dioxide out of "
  "carbonates.")
G("Bicarbonate", "Bicarbonate", ["bicarbonate", "hydrogen carbonate", "hydrogencarbonate"], "Bicarbonate",
  "The hydrogen carbonate ion, HCO₃⁻: a carbonate that still holds one hydrogen. Baking soda "
  "is sodium bicarbonate, and the bicarbonate in your blood keeps its pH steady.")
G("Phosphate", "Phosphate", ["phosphate", "hydrogen phosphate", "dihydrogen phosphate", "orthophosphate"], "Phosphate",
  "The phosphate ion, PO₄³⁻, or a salt or ester containing it. Bones and teeth are calcium "
  "phosphate, and phosphate links the backbone of DNA. Fertilizers supply it to crops.")
G("Silicate", "Silicate", ["silicate"], "Silicate",
  "A compound built from silicon and oxygen, SiO₄ units linked into chains, sheets or "
  "frameworks. Most rocks, clays, sand and glass are silicates.")
G("Borate", "Borate", ["borate", "tetraborate"], "Borate",
  "A compound of boron and oxygen, or a salt of boric acid, such as borax. Borates make "
  "heat-proof borosilicate glass and act as fluxes for welding.")
G("Acetate", "Acetate", ["acetate", "ethanoate"], "Acetate",
  "The acetate ion, CH₃COO⁻, from acetic acid (vinegar), or a salt or ester of it. Cellulose "
  "acetate was the safety film of cinema; ethyl acetate is nail-polish remover.")
G("Formate", "Formate", ["formate", "methanoate"], "Formate",
  "The formate ion, HCOO⁻, from formic acid (the sting of ants), or a salt or ester of it.")
G("Oxalate", "Oxalate", ["oxalate"], "Oxalate",
  "The oxalate ion, C₂O₄²⁻, from oxalic acid, found in rhubarb leaves. Calcium oxalate is the "
  "stuff of most kidney stones.")
G("Citrate", "Citrate", ["citrate"], "Citrate",
  "The ion or a salt of citric acid, the sourness of lemons. Citrates keep drinks tart and "
  "stop stored blood from clotting.")
G("Lactate", "Lactate", ["lactate"], "Lactate",
  "The ion or a salt of lactic acid, which sours milk and builds up in working muscles.")
G("Permanganate", "Permanganate", ["permanganate"], "Permanganate",
  "The permanganate ion, MnO₄⁻, deep purple and a strong oxidizer. Potassium permanganate "
  "disinfects water and turns colourless as it oxidizes what it meets.")
G("Chromate", "Chromate", ["chromate", "dichromate"], "Chromate and dichromate",
  "CrO₄²⁻ (yellow) and its doubled form dichromate, Cr₂O₇²⁻ (orange): chromium with oxygen, "
  "strong oxidizers and pigments. Chromates are toxic and cause cancer.")
G("Thiocyanate", "Thiocyanate", ["thiocyanate"], "Thiocyanate",
  "SCN⁻: a cyanide with a sulfur added. With iron(III) it turns blood-red, a classic test.")
G("Ammonium", "Ammonium", ["ammonium"], "Ammonium",
  "The ammonium ion, NH₄⁺: ammonia that has taken on a hydrogen ion. It behaves like a metal "
  "ion in salts such as sal ammoniac (ammonium chloride).")
G("Hydrate", "Hydrate", ["hydrate", "monohydrate", "dihydrate", "trihydrate", "pentahydrate", "hexahydrate",
                         "heptahydrate", "decahydrate"], "Hydrate",
  "A crystal that holds water molecules in its structure. Blue vitriol is copper sulfate "
  "pentahydrate (five waters); heat drives the water off and leaves the anhydrous salt.",
  lesson="Hydrate")
G("Anhydrous", "Anhydrous", ["anhydrous"], "Anhydrous",
  "Containing no water. Anhydrous salts are often a different colour from their hydrates and "
  "pull water from the air.", lesson="Hydrate")
G("Anhydride", "Anhydride", ["anhydride"], "Acid anhydride",
  "A compound that becomes an acid when it takes up water: sulfur trioxide is sulfuric acid's "
  "anhydride, and acetic anhydride gives acetic acid.")
G("Hydrochloride", "Hydrochloride", ["hydrochloride", "dihydrochloride"], "Hydrochloride",
  "A salt of an amine with hydrochloric acid. Medicines are often sold as hydrochlorides "
  "because the salt dissolves in water and keeps better than the free base.")
G("OxidationState", "Oxidation state", ["oxidation state", "oxidation number"], "Oxidation state",
  "The charge an atom would carry if all its bonds were ionic. Roman numerals in names give "
  "it: iron(II) chloride is FeCl₂ and iron(III) chloride FeCl₃.", lesson="OxidationState")
G("Ferrous", "Ferrous and ferric", ["ferrous", "ferric", "cuprous", "cupric", "stannous", "stannic", "mercurous",
                                    "mercuric", "plumbous", "plumbic", "cobaltous", "manganous", "chromous", "chromic"],
  "Ferrous",
  "Old names for a metal's two oxidation states: -ous is the lower, -ic the higher. Ferrous "
  "is iron(II), ferric iron(III); cuprous is copper(I), cupric copper(II).", plural=False)

# --------------------------------------------------------------------------------------
# Naming: what the parts of a name say (name_parts() below finds them in a substance's name)
# --------------------------------------------------------------------------------------
G("IcOus", "-ic and -ous acids", [], "Oxyacid",
  "An acid's ending says how much oxygen it has: the -ic acid more (sulfuric, H₂SO₄), the "
  "-ous acid less (sulfurous, H₂SO₃). Their salts are the -ates and the -ites. Hydro-…-ic "
  "acids, such as hydrochloric, have no oxygen at all.", plural=False, also=["AteIte"])
G("Multiplier", "di-, tri-, tetra-…", [], "Numeral prefix",
  "Number prefixes, mostly Greek: mono- 1, di- 2, tri- 3, tetra- 4, penta- 5, hexa- 6. Each "
  "counts the part after it (dimethyl: two methyl groups; carbon dioxide: two oxygens). Bis- "
  "and tris- count larger groups written in brackets.", plural=False)
G("ChainRoot", "meth-, eth-, prop-, but-…", [], "IUPAC nomenclature of organic chemistry",
  "How many carbons the main chain has: meth- 1, eth- 2, prop- 3 and but- 4 come from older "
  "names (methyl, ether, propionic and butyric acids); pent- 5, hex- 6, hept- 7, oct- 8 and "
  "on are Greek numbers. The ending then gives the kind of compound: -ane, -ene, -ol, -one.",
  plural=False)
G("BranchPrefix", "iso-, sec-, tert-, cyclo-", [], "Structural isomer",
  "Shape prefixes: iso- marks a chain that forks at its end (isopropyl, isobutyl); sec- and "
  "tert- say the group joins through a carbon bonded to two or three others (tert-butyl); "
  "cyclo- closes the chain into a ring (cyclohexane).", plural=False, also=["Isomer"])
G("HaloPrefix", "chloro-, bromo-, fluoro-, iodo-", [], "Organohalogen compound",
  "A halogen atom standing in for a hydrogen on carbon: chlorobenzene is benzene with one "
  "chlorine, dichloromethane is methane with two.", plural=False, also=["Halogen"])
G("Methyl", "Methyl", ["methyl"], "Methyl group",
  "–CH₃, one carbon with three hydrogens. The name comes from methylene, coined in 1834 from "
  "Greek methy (wine) and hylē (wood), after methanol, the spirit of wood.", also=["Alkyl"])
G("Ethyl", "Ethyl", ["ethyl"], "Ethyl group",
  "–C₂H₅, two carbons. Liebig named it in 1834 from ether, which he took to be its oxide, with "
  "-yl from Greek hylē (stuff, matter).", also=["Alkyl"])
G("Propyl", "Propyl", ["propyl", "isopropyl"], "Propyl group",
  "–C₃H₇, three carbons; isopropyl is its forked form. From propionic acid: Greek prōtos "
  "(first) and piōn (fat), the smallest acid that behaves like one from fat.", also=["Alkyl"])
G("Butyl", "Butyl", ["butyl", "isobutyl"], "Butyl group",
  "–C₄H₉, four carbons, in four shapes (n-, iso-, sec- and tert-butyl). From butyric acid, "
  "the smell of rancid butter (Latin butyrum).", also=["Alkyl"])
G("Amyl", "Amyl (pentyl)", ["amyl", "isoamyl", "pentyl"], "Pentyl group",
  "–C₅H₁₁, five carbons, now called pentyl. Amyl is from Latin amylum (starch): amyl alcohol "
  "was found in fusel oil, distilled from fermented starch.", also=["Alkyl"])
G("Phenyl", "Phenyl", ["phenyl"], "Phenyl group",
  "C₆H₅–, a benzene ring with one hydrogen taken off to make a bond. From phène, Laurent's "
  "name for benzene, after Greek phainein (to shine): it came from the coal gas that lit "
  "cities.", also=["Aromatic"])
G("Benzyl", "Benzyl", ["benzyl"], "Benzyl group",
  "C₆H₅CH₂–, a benzene ring on a CH₂. Named, like benzene and benzoic acid, after gum benzoin, "
  "the Southeast Asian resin benzoic acid was first distilled from.", also=["Aromatic"])
G("Vinyl", "Vinyl", ["vinyl"], "Vinyl group",
  "CH₂=CH–, ethylene with one hydrogen taken off, two fewer than ethyl. From Latin vinum "
  "(wine), through ethyl alcohol. Vinyl chloride links into PVC.", also=["Alkene"])
G("Acetyl", "Acetyl", ["acetyl"], "Acetyl group",
  "CH₃CO–, the part of acetic acid that carries over into acetates, aspirin and "
  "acetylcholine. From Latin acetum (vinegar).", also=["Carbonyl"])
G("Allyl", "Allyl", ["allyl"], "Allyl group",
  "CH₂=CH–CH₂–, named from Allium, the garlic genus, by Theodor Wertheim, who found it in "
  "garlic oil in 1844.", also=["Alkene"])
G("Alkoxy", "Alkoxy", ["alkoxy", "methoxy", "ethoxy", "butoxy", "propoxy"], "Alkoxy group",
  "An alkyl group joined on through an oxygen, –O–R: methoxy (–OCH₃), ethoxy, butoxy. It is "
  "an ether link on a molecule.", also=["Ether"])
G("Alkoxide", "Alkoxide", ["alkoxide", "methoxide", "ethoxide", "butoxide", "propoxide", "isopropoxide"],
  "Alkoxide",
  "An alcohol that has given up the hydrogen of its –OH, leaving O⁻: sodium methoxide, "
  "aluminium isopropoxide. Strong bases, made by dissolving a reactive metal in the alcohol.",
  also=["Alcohol"])
G("Nitro", "Nitro group", ["nitro group", "nitro compound"], "Nitro compound",
  "–NO₂ on a carbon, as in nitrobenzene, picric acid and TNT. It carries oxygen right beside "
  "the fuel, which is why many nitro compounds burn or explode so fast.")
G("Thiol", "Thio- and thiols", ["thiol", "mercaptan"], "Thiol",
  "Thio- (Greek theion, sulfur) puts a sulfur where an oxygen would be: thiosulfate, thiourea, "
  "and the thiols (–SH), behind the smells of skunks and garlic.")
G("Azide", "Azide", ["azide"], "Azide",
  "The azide ion, N₃⁻: three nitrogens in a row. From azote, Lavoisier's name for nitrogen "
  "(Greek a- zōē, no life: animals die in it). Sodium azide, set off by a spark, filled early "
  "car airbags with nitrogen.", also=["IdeEnding"])
G("Cyanate", "Cyanate", ["cyanate", "isocyanate", "diisocyanate"], "Cyanate",
  "OCN⁻, cyanide with an oxygen added (the -ate of cyanic acid); its twin isocyanate, –N=C=O "
  "on carbon, makes polyurethane. Wöhler's ammonium cyanate turned into urea in 1828, an "
  "organic compound from inorganic ones.", also=["AteIte"])
G("Iodate", "Iodate and bromate", ["iodate", "periodate", "bromate"], "Iodate",
  "IO₃⁻ and BrO₃⁻, iodine or bromine with three oxygens, named like chlorate; periodate (IO₄⁻) "
  "has four. Potassium iodate is the iodine in much iodized salt.", also=["AteIte"])
G("PeroxySalt", "Persulfate and perborate", ["persulfate", "persulphate", "peroxydisulfate",
                                              "peroxymonosulfate", "perborate", "percarbonate"],
  "Peroxydisulfate",
  "Salts with a peroxide link (O–O) inside the ion: persulfate, perborate, percarbonate. In "
  "water they release active oxygen, so they bleach in laundry powders and hair lighteners.",
  also=["Peroxide"])
G("Superoxide", "Superoxide", ["superoxide", "ozonide"], "Superoxide",
  "O₂⁻, an oxygen molecule with one extra electron. Potassium superoxide in rebreathers takes "
  "in breathed-out carbon dioxide and gives back oxygen.", also=["Peroxide"])
G("Manganate", "Manganate", ["manganate"], "Manganate",
  "MnO₄²⁻, green, one charge more than purple permanganate. Manganese dioxide fused with "
  "potash in air makes it, the first step to permanganate.", also=["Permanganate"])
G("Arsenate", "Arsenate and arsenite", ["arsenate", "arsenite"], "Arsenate",
  "AsO₄³⁻ and AsO₃³⁻, arsenic with four or three oxygens. Lead and calcium arsenate were early "
  "insecticides; arsenite pigments such as Scheele's green poisoned the Victorians.",
  also=["AteIte"])
G("Phosphite", "Phosphite", ["phosphite", "hypophosphite"], "Phosphite anion",
  "PO₃³⁻, phosphorus with three oxygens, one fewer than phosphate (hypophosphite has two). "
  "Organic phosphites guard plastics against oxidation; hypophosphite plates nickel without "
  "electricity.", also=["AteIte"])
G("Pyrophosphate", "Pyrophosphate", ["pyrophosphate", "diphosphate", "polyphosphate", "tripolyphosphate",
                                     "metaphosphate", "hexametaphosphate"], "Pyrophosphate",
  "Two phosphates joined through an oxygen, made by heating (pyro-, fire) until they lose "
  "water; longer chains and rings are polyphosphates and metaphosphates. ATP stores its energy "
  "in such links.", also=["Phosphate"])
G("Metalate", "Metal -ates", ["aluminate", "titanate", "molybdate", "tungstate", "vanadate", "stannate",
                              "zincate", "plumbate", "ferrate", "zirconate", "niobate", "tantalate",
                              "germanate", "metaborate"], "Oxyanion",
  "A metal's name with -ate: the metal bound up with oxygen in an anion, as in an acid's salt. "
  "Aluminate, titanate, molybdate, tungstate and stannate form when the metal's oxide meets a "
  "strong base.", also=["AteIte"])
G("Ferrocyanide", "Ferrocyanide", ["ferrocyanide", "ferricyanide", "hexacyanoferrate"], "Ferrocyanide",
  "[Fe(CN)₆]⁴⁻ and its oxidized form ferricyanide, [Fe(CN)₆]³⁻: iron gripped so tightly by six "
  "cyanides that they are far less poisonous than free cyanide. With more iron they make "
  "Prussian blue.", also=["Complex"])
G("Sulfonate", "Sulfonic acid", ["sulfonate", "sulphonate", "sulfonic", "sulphonic", "sulfonyl"], "Sulfonic acid",
  "–SO₃H on carbon, a sulfonic acid, and its salts the sulfonates: strong acids that dissolve "
  "well in water. They make most detergents and the water-soluble dyes.", also=["Surfactant"])
G("Carbamate", "Carbamate", ["carbamate", "dithiocarbamate", "urethane"], "Carbamate",
  "H₂N–CO–O–, half amide and half ester, from carbamic acid. Polyurethanes are held together "
  "by carbamate links, and many pesticides are carbamates.", also=["Ester"])
G("FattyNames", "Stearate, oleate, laurate…", ["stearate", "stearic", "palmitate", "palmitic", "oleate", "oleic",
                                               "laurate", "lauric", "myristate", "myristic", "linoleate",
                                               "linoleic", "ricinoleate", "ricinoleic"], "Fatty acid",
  "Fatty acids are named for where they were first found: stearic in tallow (Greek stear), "
  "palmitic in palm oil, oleic in olive oil (Latin oleum), lauric in laurel berries, myristic "
  "in nutmeg (Myristica). Their -ate salts are soaps.", also=["CarboxylicAcid"])
G("Benzoate", "Benzoate", ["benzoate", "benzoic"], "Benzoic acid",
  "From benzoic acid, distilled from gum benzoin resin in the 1500s. Sodium benzoate keeps "
  "soft drinks and pickles from spoiling.", also=["CarboxylicAcid"])
G("Salicylate", "Salicylate", ["salicylate", "salicylic"], "Salicylic acid",
  "From salicylic acid, first got from willow bark (Latin salix), an old remedy for pain and "
  "fever that led to aspirin, acetylsalicylic acid.", also=["CarboxylicAcid"])
G("Phthalate", "Phthalate", ["phthalate", "phthalic"], "Phthalic acid",
  "From phthalic acid, which Laurent made by oxidizing naphthalene in 1836 and named by "
  "clipping that word. Phthalate esters soften PVC.", also=["CarboxylicAcid"])
G("Tartrate", "Tartrate", ["tartrate", "bitartrate", "tartaric"], "Tartaric acid",
  "From tartaric acid, the acid of tartar, the crust grape juice leaves in wine barrels. Cream "
  "of tartar is potassium bitartrate; Pasteur found mirror-image molecules in its crystals.",
  also=["CarboxylicAcid"])
G("Butyrate", "Butyrate", ["butyrate", "butyric"], "Butyric acid",
  "From butyric acid, which gives rancid butter its smell (Latin butyrum, butter). Its esters, "
  "by contrast, smell of pineapple and apricot.", also=["CarboxylicAcid"])
G("Propionate", "Propionate", ["propionate", "propionic"], "Propionic acid",
  "From propionic acid: Greek prōtos (first) and piōn (fat), the smallest acid with the "
  "properties of the fatty acids. Its salts keep bread from going mouldy.", also=["CarboxylicAcid"])
G("Acrylate", "Acrylate", ["acrylate", "methacrylate", "acrylic"], "Acrylic acid",
  "From acrolein, the sharp vapour of burnt fat (Latin acer, sharp, and oleum, oil). "
  "Acrylates and methacrylates link into acrylic plastics, paints and superglue.",
  also=["Polymer"])
G("Adipate", "Adipate", ["adipate", "adipic"], "Adipic acid",
  "From adipic acid, first made by oxidizing fats (Latin adeps, fat). It is one half of "
  "nylon 6,6.", also=["CarboxylicAcid"])

# --------------------------------------------------------------------------------------
# Matter, mixtures and solutions
# --------------------------------------------------------------------------------------
G("Element", "Element", ["chemical element"], "Chemical element",
  "A substance made of only one kind of atom, set by the number of protons in its nucleus. "
  "There are 118; everything else is built from them.", lesson="ChemicalElement")
G("Compound", "Compound", ["chemical compound"], "Chemical compound",
  "A substance of two or more elements bonded in fixed proportions. Water is always two "
  "hydrogens to one oxygen.", lesson="ChemicalCompound")
G("Mixture", "Mixture", ["mixture"], "Mixture",
  "Substances mingled without bonding to each other, in any proportion, and separable by "
  "physical means: air, seawater, brass.", lesson="Mixture")
G("Alloy", "Alloy", ["alloy"], "Alloy",
  "A metal mixed with other elements to improve it: bronze is copper with tin, steel is iron "
  "with a little carbon.", lesson="Alloy")
G("Solution", "Solution", ["aqueous solution", "solution"], "Solution (chemistry)",
  "A mixture in which one substance (the solute) is spread evenly, molecule by molecule, "
  "through another (the solvent). In an aqueous solution, the solvent is water.",
  lesson="Solution")
G("Aqueous", "Aqueous", ["aqueous"], "Aqueous solution",
  "In water, or dissolved in water. Written (aq) after a formula.", lesson="Solution")
G("Solvent", "Solvent", ["solvent"], "Solvent",
  "A substance, usually a liquid, that dissolves others. Water is the most common; organic "
  "solvents like ethanol, acetone and hexane dissolve oils, fats and resins that water won't.",
  lesson="Solvent")
G("Solubility", "Solubility", ["solubility", "soluble", "insoluble", "slightly soluble", "sparingly soluble"],
  "Solubility",
  "How much of a substance will dissolve in a given amount of a solvent, often given in grams "
  "per litre of water at a stated temperature. Insoluble means almost none does.",
  lesson="Solubility", plural=False)
G("Miscible", "Miscible", ["miscible", "immiscible"], "Miscibility",
  "Able to mix in any proportion. Alcohol and water are miscible; oil and water are "
  "immiscible and separate into layers.", plural=False)
G("Concentration", "Concentration", ["concentration"], "Concentration",
  "How much of a substance is in a given volume of a mixture, as grams per litre, a "
  "percentage, or moles per litre (molarity).")
G("Precipitate", "Precipitate", ["precipitate", "precipitation"], "Precipitation (chemistry)",
  "A solid that forms out of a solution when two dissolved substances react to make one that "
  "won't stay dissolved. It clouds the liquid and settles.", lesson="Precipitation")
G("Suspension", "Colloid", ["colloid", "colloidal", "suspension"], "Colloid",
  "Particles too small to settle but much larger than molecules, spread through another "
  "substance: milk, fog, smoke and gelatin are colloids.", lesson="Colloid")
G("Emulsion", "Emulsion", ["emulsion", "emulsifier"], "Emulsion",
  "Droplets of one liquid held suspended in another it won't mix with, like oil in water. "
  "Mayonnaise and milk are emulsions; an emulsifier keeps them from separating.")
G("Crystal", "Crystal", ["crystal", "crystalline"], "Crystal",
  "A solid whose atoms are arranged in a repeating pattern, which shows as flat faces and "
  "sharp angles. Salt, quartz and sugar are crystalline.", lesson="CrystalStructure")
G("Amorphous", "Amorphous", ["amorphous"], "Amorphous solid",
  "A solid without a repeating order to its atoms, like glass or many plastics. It softens "
  "over a range of temperatures instead of melting sharply.", plural=False)
G("Hygroscopic", "Hygroscopic", ["hygroscopic", "deliquescent", "deliquesces"], "Hygroscopy",
  "Pulling water vapour out of the air. A deliquescent substance takes up so much that it "
  "dissolves in it, as calcium chloride and lye do left open.", plural=False)
G("Volatile", "Volatile", ["volatile"], "Volatility (chemistry)",
  "Evaporating easily at ordinary temperatures. Volatile liquids, like ether or acetone, "
  "smell strongly because so many molecules leave them.", plural=False)
G("Viscous", "Viscous", ["viscous", "viscosity"], "Viscosity",
  "Thick and slow to flow. Viscosity measures a fluid's resistance to flowing: honey is far "
  "more viscous than water.", plural=False)
G("Sublimation", "Sublimation", ["sublimation", "sublimes", "sublime"], "Sublimation (phase transition)",
  "A solid turning straight into a gas without melting first, as dry ice and iodine do. "
  "Such a substance has no boiling point at ordinary pressure.", lesson="Sublimation", plural=False)
G("MeltingPoint", "Melting point", ["melting point"], "Melting point",
  "The temperature at which a solid turns to liquid. A pure substance melts sharply at its "
  "melting point; an impure one melts lower, over a range.", lesson="MeltingPoint")
G("BoilingPoint", "Boiling point", ["boiling point"], "Boiling point",
  "The temperature at which a liquid's vapour pressure equals the pressure around it, so it "
  "boils. Water boils at 100 °C at sea level but lower up a mountain.", lesson="BoilingPoint")
G("Density", "Density", ["density"], "Density",
  "Mass per volume, in grams per cubic centimetre (g/cm³). Water's is 1: anything denser "
  "sinks in it, anything less dense floats.", lesson="Density")
G("MolarMass", "Molar mass", ["molar mass", "molecular weight"], "Molar mass",
  "The mass of one mole of a substance, in grams per mole: the sum of its atoms' atomic "
  "masses. Water's is 18 g/mol.", lesson="MolarMass")
G("Mole", "Mole", ["mole", "moles"], "Mole (unit)",
  "Chemistry's counting unit: 6.022 × 10²³ particles. A mole of any substance weighs its "
  "molar mass in grams, which lets chemists weigh out atoms by the count.", lesson="Mole",
  plural=False)
G("Vapor", "Vapour pressure", ["vapor pressure", "vapour pressure"], "Vapor pressure",
  "The pressure of a substance's own vapour above it. It rises with temperature; when it "
  "matches the air's pressure, the liquid boils.", lesson="VaporPressure")
G("Purity", "Purity", ["purity", "impurities", "impurity"], "Chemical purity",
  "How much of a sample is the substance itself rather than something else. Reagent-grade "
  "chemicals are often 99.9 % pure; refining semiconductors needs far better.",
  lesson="Purity", plural=False)

# --------------------------------------------------------------------------------------
# Atoms and the periodic table
# --------------------------------------------------------------------------------------
G("Isotope", "Isotope", ["isotope"], "Isotope",
  "Atoms of the same element with different numbers of neutrons, and so different masses. "
  "Carbon-12 and carbon-14 are isotopes; some isotopes are radioactive.", lesson="Isotope")
G("Allotrope", "Allotrope", ["allotrope", "allotropy"], "Allotropy",
  "One of the different forms an element takes, its atoms bonded in different ways: diamond, "
  "graphite and fullerenes are all pure carbon.", lesson="Allotropy")
G("Metalloid", "Metalloid", ["metalloid", "semimetal"], "Metalloid",
  "An element between metals and nonmetals in its behaviour, such as boron, silicon, "
  "germanium, arsenic, antimony and tellurium. Several are semiconductors.", lesson="Metalloid")
G("Halogen", "Halogen", ["halogen"], "Halogen",
  "The elements of group 17: fluorine, chlorine, bromine, iodine and astatine. Each is one "
  "electron short of a full shell, so they react fiercely and form salts with metals "
  "(halogen means 'salt-maker').", lesson="Halogen")
G("NobleGas", "Noble gas", ["noble gas", "inert gas"], "Noble gas",
  "The elements of group 18: helium, neon, argon, krypton, xenon and radon. Their full "
  "electron shells make them barely react at all.", lesson="NobleGas")
G("AlkaliMetal", "Alkali metal", ["alkali metal"], "Alkali metal",
  "The soft, reactive metals of group 1: lithium, sodium, potassium, rubidium, caesium. Each "
  "gives up one electron easily, and they react with water to make hydrogen and an alkali.",
  lesson="AlkaliMetal")
G("AlkalineEarth", "Alkaline earth metal", ["alkaline earth metal", "alkaline earth"], "Alkaline earth metal",
  "The metals of group 2: beryllium, magnesium, calcium, strontium, barium and radium. They "
  "give up two electrons and form oxides that make water alkaline.", lesson="AlkalineEarth")
G("TransitionMetal", "Transition metal", ["transition metal"], "Transition metal",
  "The metals of the periodic table's middle block, such as iron, copper and gold. They take "
  "several oxidation states, form coloured compounds and make good catalysts.",
  lesson="TransitionMetal")
G("RareEarth", "Rare-earth element", ["rare-earth element", "rare earth element", "rare-earth", "rare earth",
                                      "lanthanide"], "Rare-earth element",
  "The lanthanides plus scandium and yttrium: chemically alike metals that occur together "
  "and are hard to separate. Neodymium's magnets and europium's red phosphor are two uses.",
  lesson="Lanthanide")
G("Actinide", "Actinide", ["actinide"], "Actinide",
  "The fifteen radioactive elements from actinium to lawrencium, including uranium and "
  "plutonium.", lesson="Actinide")
G("Radioactive", "Radioactive", ["radioactive", "radioactivity", "radioisotope"], "Radioactive decay",
  "Having an unstable nucleus that breaks down on its own, giving off radiation (alpha, beta "
  "or gamma) and turning into another element or isotope.", lesson="Radioactivity", plural=False)
G("HalfLife", "Half-life", ["half-life", "half-lives"], "Half-life",
  "The time it takes for half of a radioactive sample to decay. It never changes for a given "
  "isotope: a second half-life leaves a quarter.", lesson="HalfLife", plural=False)
G("Electronegativity", "Electronegativity", ["electronegativity", "electronegative"], "Electronegativity",
  "How strongly an atom pulls shared electrons toward itself. Fluorine pulls hardest; a big "
  "difference between two atoms makes their bond ionic.", lesson="Electronegativity", plural=False)

# --------------------------------------------------------------------------------------
# Bonds and structure
# --------------------------------------------------------------------------------------
G("CovalentBond", "Covalent bond", ["covalent bond", "covalent", "covalently"], "Covalent bond",
  "A bond in which two atoms share a pair of electrons. Molecules such as water, methane and "
  "sugar are held together by covalent bonds.", lesson="CovalentBond")
G("IonicBond", "Ionic bond", ["ionic bond", "ionic bonding", "ionic compound", "ionic"], "Ionic bonding",
  "The attraction between oppositely charged ions, formed when one atom hands electrons to "
  "another. Salts are ionic: hard, high-melting, and conducting electricity when molten or "
  "dissolved.", lesson="IonicBond")
G("HydrogenBond", "Hydrogen bond", ["hydrogen bond", "hydrogen bonding"], "Hydrogen bond",
  "A weak attraction between a hydrogen on one molecule and an oxygen, nitrogen or fluorine "
  "on another. It makes water boil so high and holds DNA's two strands together.",
  lesson="HydrogenBond")
G("Molecule", "Molecule", ["molecule", "molecular"], "Molecule",
  "A group of atoms bonded together, the smallest unit of a covalent substance: O₂, H₂O, "
  "C₆H₁₂O₆.", lesson="Molecule")
G("Isomer", "Isomer", ["isomer", "isomeric", "isomerism"], "Isomer",
  "Compounds with the same formula but atoms arranged differently, and so different "
  "properties. Ethanol and dimethyl ether are both C₂H₆O.", lesson="Isomer")
G("Chiral", "Chiral", ["chiral", "chirality", "enantiomer", "racemic", "racemate"], "Chirality (chemistry)",
  "A molecule that can't be laid over its mirror image, like a left and a right hand. The two "
  "mirror forms are enantiomers; a racemic mix holds equal amounts of both.",
  lesson="Chirality", plural=False)
G("Complex", "Coordination complex", ["coordination complex", "complex ion", "coordination compound", "ligand"],
  "Coordination complex",
  "A metal atom or ion surrounded by molecules or ions (ligands) that each lend it a pair of "
  "electrons. Haemoglobin, chlorophyll and the deep blue of copper in ammonia are complexes.",
  lesson="CoordinationComplex")
G("Chelate", "Chelate", ["chelate", "chelating", "chelation", "chelator"], "Chelation",
  "A ligand that grips a metal ion at two or more points, like a claw. EDTA chelates calcium "
  "to soften water and lead to treat poisoning.", lesson="Chelation")
G("Radical", "Radical", ["free radical", "radicals", "radical polymerization", "radical chain"], "Radical (chemistry)",
  "A molecule or atom with an unpaired electron, which makes it very reactive. Radicals drive "
  "combustion, chain polymerization and the ageing of plastics and cells.")

# --------------------------------------------------------------------------------------
# Reactions
# --------------------------------------------------------------------------------------
G("Reagent", "Reagent", ["reagent", "reactant"], "Reagent",
  "A substance put into a reaction to make it happen, or used to test for something.",
  lesson="ChemicalReaction")
G("Intermediate", "Intermediate", ["intermediate"], "Reaction intermediate",
  "A substance made on the way from starting materials to a product, then used up. In "
  "industry, an intermediate is a chemical made to be turned into others.",
  lesson="ReactionIntermediate")
G("Byproduct", "By-product", ["by-product", "byproduct", "side product"], "By-product",
  "A substance a reaction or process makes besides the one wanted. Some, like the chlorine "
  "from making lye, became industries of their own.", lesson="SideReaction")
G("Yield", "Yield", ["percent yield", "percentage yield", "yield of"], "Yield (chemistry)",
  "How much product a reaction actually gives, often as a percentage of the most it could in "
  "theory.", lesson="Yield", plural=False)
G("Catalyst", "Catalyst", ["catalyst", "catalysis", "catalytic", "catalyzed", "catalysed", "catalyses",
                           "catalyzes"], "Catalysis",
  "A substance that speeds a reaction up without being used up itself, by offering an easier "
  "path. Platinum, iron, acids and enzymes are catalysts.", lesson="Catalysis")
G("Enzyme", "Enzyme", ["enzyme"], "Enzyme",
  "A protein that catalyses a reaction in a living thing. Yeast's enzymes turn sugar into "
  "alcohol; your saliva's start breaking down starch.", lesson="Enzyme")
G("Oxidation", "Oxidation", ["oxidation", "oxidized", "oxidised", "oxidizes", "oxidises", "oxidize", "oxidise"],
  "Redox",
  "Losing electrons, which often means gaining oxygen or losing hydrogen. Rusting, burning "
  "and the browning of a cut apple are oxidations. It always comes paired with a reduction.",
  lesson="Redox", plural=False)
G("Reduction", "Reduction", ["reduction reaction", "reduced to the metal", "reductive", "chemical reduction"], "Redox",
  "Gaining electrons, which often means losing oxygen or gaining hydrogen. Smelting reduces a "
  "metal oxide to the metal. It always comes paired with an oxidation.", lesson="Redox",
  plural=False)
G("Redox", "Redox", ["redox"], "Redox",
  "A reaction in which electrons move from one substance (oxidized) to another (reduced). "
  "Burning, rusting, batteries and smelting are all redox reactions.", lesson="Redox",
  plural=False)
G("Oxidizer", "Oxidizing agent", ["oxidizing agent", "oxidising agent", "oxidizer", "oxidiser", "oxidant"],
  "Oxidizing agent",
  "A substance that takes electrons from others, oxidizing them, and is reduced itself: "
  "oxygen, chlorine, nitrates, permanganate. Oxidizers make fuels burn fiercely.",
  lesson="OxidizingAgent")
G("Reducer", "Reducing agent", ["reducing agent", "reductant"], "Reducing agent",
  "A substance that gives electrons to others, reducing them, and is oxidized itself. Carbon "
  "(as coke) is the reducing agent that frees iron from its ore.", lesson="ReducingAgent")
G("Combustion", "Combustion", ["combustion"], "Combustion",
  "Burning: a fast reaction of a fuel with an oxidizer, usually oxygen, giving off heat and "
  "light. Hydrocarbons burn to carbon dioxide and water.", lesson="Combustion", plural=False)
G("Decomposition", "Decomposition", ["decomposition", "decomposes", "decompose", "decomposed"],
  "Chemical decomposition",
  "A substance breaking down into simpler ones. Many compounds decompose when heated instead "
  "of melting or boiling, so they have no boiling point.", lesson="Decomposition", plural=False)
G("Hydrolysis", "Hydrolysis", ["hydrolysis", "hydrolyzed", "hydrolysed", "hydrolyzes", "hydrolyses"], "Hydrolysis",
  "Splitting a compound by reaction with water. Digestion hydrolyses food; esters hydrolyse "
  "back into an acid and an alcohol.", lesson="Hydrolysis", plural=False)
G("Dehydration", "Dehydration", ["dehydration reaction", "dehydrating agent", "dehydrated"], "Dehydration reaction",
  "A reaction that removes water, either from a hydrate or from within molecules, as "
  "sulfuric acid chars sugar to carbon.", lesson="Dehydration", plural=False)
G("Condensation", "Condensation reaction", ["condensation reaction", "condensation polymer"], "Condensation reaction",
  "Two molecules joining and giving off a small one, usually water. Esters, proteins and "
  "nylon are made by condensation.", lesson="Condensation")
G("Neutralization", "Neutralization", ["neutralization", "neutralisation", "neutralizes", "neutralises",
                                       "neutralize", "neutralise"], "Neutralization (chemistry)",
  "An acid and a base reacting to make a salt and water, cancelling each other out.",
  lesson="Neutralization", plural=False)
G("Exothermic", "Exothermic", ["exothermic"], "Exothermic reaction",
  "Giving off heat. Burning, rusting and mixing quicklime with water are exothermic; the "
  "game shows a negative enthalpy change (ΔH) for them.", lesson="Exothermic", plural=False)
G("Endothermic", "Endothermic", ["endothermic"], "Endothermic process",
  "Taking in heat, so it needs heating to go, or cools its surroundings, like an instant cold "
  "pack. Its enthalpy change (ΔH) is positive.", lesson="Endothermic", plural=False)
G("Enthalpy", "Enthalpy", ["enthalpy", "heat of formation", "enthalpy of formation"], "Enthalpy",
  "A substance's heat content. The enthalpy change of a reaction (ΔH, in kJ/mol) is the heat "
  "it gives off (negative) or takes in (positive).", lesson="Enthalpy", plural=False)
G("Equilibrium", "Equilibrium", ["equilibrium", "reversible reaction"], "Chemical equilibrium",
  "The point at which a reversible reaction runs forward and back at the same rate, so the "
  "amounts stop changing. Pressure, temperature and concentration shift it.",
  lesson="Equilibrium", plural=False)
G("Stoichiometry", "Stoichiometry", ["stoichiometry", "stoichiometric"], "Stoichiometry",
  "The arithmetic of reactions: how many of each molecule react and form, from the balanced "
  "equation, and so how many grams of each.", lesson="Stoichiometry", plural=False)
G("Polymerization", "Polymerization", ["polymerization", "polymerisation", "polymerizes", "polymerises",
                                       "polymerized", "polymerised"], "Polymerization",
  "Joining many small molecules (monomers) into long chains (polymers), by adding them end to "
  "end or by condensation.", lesson="Polymerization", plural=False)
G("Hydrogenation", "Hydrogenation", ["hydrogenation", "hydrogenated"], "Hydrogenation",
  "Adding hydrogen to a molecule, usually across a double bond, with a metal catalyst. It "
  "turns vegetable oils into margarine.", lesson="Hydrogenation", plural=False)
G("Esterification", "Esterification", ["esterification", "esterified"], "Fischer–Speier esterification",
  "Making an ester from an acid and an alcohol, giving off water.", lesson="Esterification",
  plural=False)
G("Saponification", "Saponification", ["saponification", "saponified"], "Saponification",
  "Breaking fats apart with a strong base such as lye, making soap and glycerol. The word "
  "means 'soap-making'.", lesson="Saponification", plural=False)
G("Fermentation", "Fermentation", ["fermentation", "fermented", "fermenting"], "Fermentation",
  "Microbes such as yeast or bacteria breaking down sugars without air, making alcohol, "
  "lactic acid or gas: bread, beer, wine, yogurt.", lesson="Fermentation", plural=False)
G("Electrolysis", "Electrolysis", ["electrolysis", "electrolytic", "electrolysed", "electrolyzed"], "Electrolysis",
  "Driving a reaction with an electric current: splitting water into hydrogen and oxygen, or "
  "freeing reactive metals like aluminium and sodium from their compounds.",
  lesson="Electrolysis", plural=False)
G("Electrolyte", "Electrolyte", ["electrolyte"], "Electrolyte",
  "A substance that conducts electricity when molten or dissolved, because it splits into "
  "ions. Batteries and electrolysis need one.", lesson="Electrolyte")
G("Corrosion", "Corrosion", ["corrosion", "corrodes", "corrode", "corroded"], "Corrosion",
  "A metal slowly destroyed by reacting with its surroundings, as iron rusts in damp air.",
  lesson="Corrosion", plural=False)

# --------------------------------------------------------------------------------------
# Acids and bases
# --------------------------------------------------------------------------------------
G("Acid", "Acid", ["acid", "acidic", "acidity"], "Acid",
  "A substance that gives up hydrogen ions (H⁺) in water, tastes sour and turns litmus red. "
  "Acids dissolve many metals and carbonates and neutralize bases.", lesson="Acid")
G("Base", "Base", ["base", "free base", "strong base", "weak base"], "Base (chemistry)",
  "A substance that accepts hydrogen ions, such as a hydroxide, ammonia or a carbonate. Bases "
  "feel slippery, turn litmus blue and neutralize acids.", lesson="Base")
G("Alkali", "Alkali", ["alkali", "alkaline", "alkalinity", "caustic"], "Alkali",
  "A base that dissolves in water, such as lye (sodium hydroxide) or potash. Strong alkalis "
  "are caustic: they burn skin and dissolve fats.", lesson="Alkali")
G("pH", "pH", ["pH"], "PH",
  "A scale of how acidic or alkaline a water solution is: 7 is neutral, lower is acidic, "
  "higher is alkaline. Each step is ten times stronger.", lesson="pH", plural=False)
G("Buffer", "Buffer", ["buffer solution", "buffer"], "Buffer solution",
  "A solution that holds its pH steady when acid or base is added, made from a weak acid and "
  "its salt. Blood is buffered near pH 7.4.", lesson="Buffer")
G("MineralAcid", "Mineral acid", ["mineral acid"], "Mineral acid",
  "An acid made from minerals rather than living things: sulfuric, nitric, hydrochloric and "
  "phosphoric acid.", lesson="MineralAcid")

# --------------------------------------------------------------------------------------
# Organic chemistry
# --------------------------------------------------------------------------------------
G("Organic", "Organic compound", ["organic compound", "organic"], "Organic compound",
  "A compound built on carbon, usually with hydrogen: fuels, plastics, drugs, dyes and the "
  "molecules of life. (Organic food is a different meaning.)", lesson="OrganicChemistry")
G("Inorganic", "Inorganic compound", ["inorganic compound", "inorganic"], "Inorganic compound",
  "A compound not built on carbon–hydrogen bonds: salts, minerals, metals' oxides, acids "
  "like sulfuric acid.")
G("Hydrocarbon", "Hydrocarbon", ["hydrocarbon"], "Hydrocarbon",
  "A compound of only carbon and hydrogen: methane, petrol, paraffin wax. Crude oil and "
  "natural gas are mostly hydrocarbons.", lesson="Hydrocarbon")
G("Alkane", "Alkane", ["alkane", "paraffin"], "Alkane",
  "A hydrocarbon with only single bonds, CₙH₂ₙ₊₂: methane, propane, octane. Alkanes burn well "
  "but otherwise react little.", lesson="Alkane")
G("Alkene", "Alkene", ["alkene", "olefin"], "Alkene",
  "A hydrocarbon with a carbon–carbon double bond, such as ethylene. The double bond opens "
  "up to add other atoms or to link into polymers.", lesson="Alkene")
G("Alkyne", "Alkyne", ["alkyne"], "Alkyne",
  "A hydrocarbon with a carbon–carbon triple bond, such as acetylene, whose flame cuts steel.",
  lesson="Alkyne")
G("Aromatic", "Aromatic", ["aromatic compound", "aromatic ring", "aromatic hydrocarbon", "aromatic amine", "aromaticity",
                           "arene"], "Aromaticity",
  "Built on a ring like benzene's, six carbons sharing their electrons all round, which makes "
  "the ring unusually stable. (Many first ones found did smell strongly.)",
  lesson="Aromaticity")
G("FunctionalGroup", "Functional group", ["functional group"], "Functional group",
  "A particular cluster of atoms in a molecule that gives it its typical reactions, such as "
  "an alcohol's –OH or an acid's –COOH.", lesson="FunctionalGroup")
G("Alkyl", "Alkyl group", ["alkyl group", "alkyl", "methyl group", "ethyl group"], "Alkyl",
  "A fragment of an alkane attached to a molecule: methyl is –CH₃, ethyl –C₂H₅, propyl "
  "–C₃H₇, butyl –C₄H₉.", lesson="FunctionalGroup")
G("Hydroxyl", "Hydroxyl group", ["hydroxyl group", "hydroxyl"], "Hydroxy group",
  "An –OH group attached to a molecule. It makes alcohols and sugars dissolve in water.",
  lesson="FunctionalGroup")
G("Carbonyl", "Carbonyl group", ["carbonyl group", "carbonyl"], "Carbonyl group",
  "A carbon double-bonded to an oxygen, C=O, the reactive heart of aldehydes, ketones, acids "
  "and esters. (A metal carbonyl is a metal bonded to carbon monoxide.)", lesson="FunctionalGroup")
G("Alcohol", "Alcohol", ["alcohol"], "Alcohol (chemistry)",
  "An organic compound with an –OH group on a carbon. Ethanol is the one in drinks; methanol, "
  "glycerol and cholesterol are alcohols too.", lesson="Alcohol")
G("Aldehyde", "Aldehyde", ["aldehyde"], "Aldehyde",
  "An organic compound with a –CHO group at the end of a chain. Formaldehyde, vanillin and "
  "cinnamaldehyde are aldehydes.", lesson="Aldehyde")
G("Ketone", "Ketone", ["ketone"], "Ketone",
  "An organic compound with a C=O group between two carbons, such as acetone.",
  lesson="Ketone")
G("CarboxylicAcid", "Carboxylic acid", ["carboxylic acid", "carboxylic", "carboxylate", "fatty acid"],
  "Carboxylic acid",
  "An organic acid with a –COOH group: acetic acid in vinegar, citric acid in lemons, the "
  "fatty acids in fats.", lesson="CarboxylicAcid")
G("Ester", "Ester", ["ester"], "Ester",
  "A compound made from an acid and an alcohol. Small esters smell of fruit (pear drops, "
  "bananas); fats and polyester are esters too.", lesson="Ester")
G("Ether", "Ether", ["ether"], "Ether",
  "An organic compound with an oxygen between two carbon groups, C–O–C. Diethyl ether was "
  "the first surgical anaesthetic.", lesson="Ether")
G("Amine", "Amine", ["amine"], "Amine",
  "An organic compound derived from ammonia, with carbon groups in place of hydrogens. "
  "Amines smell fishy and are bases; many drugs and dyes are amines.", lesson="Amine")
G("Amide", "Amide", ["amide"], "Amide",
  "A compound with a nitrogen bonded to a C=O group. The bonds that link amino acids in "
  "proteins, and the units of nylon, are amides.", lesson="Amide")
G("Nitrile", "Nitrile", ["nitrile"], "Nitrile",
  "An organic compound with a –C≡N group. Acrylonitrile makes acrylic fibres and nitrile "
  "gloves.", lesson="Nitrile")
G("Phenol", "Phenol", ["phenol", "phenolic"], "Phenols",
  "An –OH group on a benzene ring, or the compound C₆H₅OH itself, Lister's carbolic acid "
  "antiseptic. Phenols are weak acids.", lesson="FunctionalGroup")
G("Glycol", "Glycol", ["glycol", "diol"], "Diol",
  "An alcohol with two –OH groups, such as ethylene glycol, the main ingredient of antifreeze.",
  lesson="Alcohol")
G("Monomer", "Monomer", ["monomer"], "Monomer",
  "A small molecule that links with others like it to build a polymer: ethylene makes "
  "polyethylene, styrene polystyrene.", lesson="Monomer")
G("Polymer", "Polymer", ["polymer", "copolymer", "macromolecule"], "Polymer",
  "A giant molecule of many repeating units linked in a chain or network. Plastics, rubber, "
  "proteins, starch and DNA are polymers.", lesson="Polymer")
G("Resin", "Resin", ["resin"], "Resin",
  "A thick, sticky substance that hardens: natural ones ooze from trees (amber is fossil "
  "resin); synthetic ones such as epoxy set into hard plastics.", lesson="Thermoset")
G("Plasticizer", "Plasticizer", ["plasticizer", "plasticiser"], "Plasticizer",
  "A substance added to a plastic to make it soft and flexible, like the phthalates in PVC "
  "hoses.", lesson="Plastic")
G("Surfactant", "Surfactant", ["surfactant", "detergent", "wetting agent"], "Surfactant",
  "A molecule with a water-loving head and an oil-loving tail, so it gathers at surfaces and "
  "lifts grease into water. Soaps and detergents are surfactants.", lesson="Surfactant")
G("Alkaloid", "Alkaloid", ["alkaloid"], "Alkaloid",
  "A nitrogen-containing base made by plants, often bitter and acting strongly on the body: "
  "caffeine, nicotine, quinine.", lesson="Alkaloid")
G("Terpene", "Terpene", ["terpene", "terpenoid"], "Terpene",
  "A compound built from five-carbon isoprene units, made by plants: the scents of pine, "
  "citrus and mint, and natural rubber.", lesson="Terpene")
G("Steroid", "Steroid", ["steroid", "corticosteroid"], "Steroid",
  "A compound with four fused carbon rings. Cholesterol, the sex hormones and cortisone are "
  "steroids.")

# --------------------------------------------------------------------------------------
# Materials, metallurgy and industry
# --------------------------------------------------------------------------------------
G("Ore", "Ore", ["ore"], "Ore",
  "Rock with enough of a metal or mineral in it to be worth mining.", lesson="Ore")
G("Mineral", "Mineral", ["mineral"], "Mineral",
  "A naturally formed solid with a definite composition and crystal structure, such as "
  "quartz, calcite or galena. Rocks are made of minerals.", lesson="Ore")
G("Smelting", "Smelting", ["smelting", "smelted", "smelt"], "Smelting",
  "Getting a metal out of its ore by heating it with a reducing agent, usually carbon, and a "
  "flux to carry off the rock.", lesson="Smelting", plural=False)
G("Flux", "Flux", ["flux"], "Flux (metallurgy)",
  "A substance added in smelting or soldering that combines with impurities so they melt off "
  "as slag, or that keeps metal surfaces clean.", lesson="Flux")
G("Slag", "Slag", ["slag"], "Slag",
  "The glassy waste that floats on molten metal in smelting, made of the ore's rock and the "
  "flux.", lesson="Slag", plural=False)
G("Calcination", "Calcination", ["calcination", "calcined", "calcining"], "Calcination",
  "Heating a solid hard to drive off water or carbon dioxide, as limestone is burned to "
  "quicklime.", lesson="Calcination", plural=False)
G("Roasting", "Roasting", ["roasting", "roasted"], "Roasting (metallurgy)",
  "Heating a sulfide ore in air, which burns off the sulfur and leaves an oxide ready for "
  "smelting.", lesson="Roasting", plural=False)
G("Pyrolysis", "Pyrolysis", ["pyrolysis", "destructive distillation"], "Pyrolysis",
  "Breaking a substance down by heat without air: wood turns to charcoal, coal to coke and "
  "coal tar.", lesson="Pyrolysis", plural=False)
G("Distillation", "Distillation", ["distillation", "distilled", "distilling", "fractional distillation"],
  "Distillation",
  "Separating liquids by boiling and condensing them: the one that boils lower comes over "
  "first. It purifies water and makes spirits and petrol.", lesson="Distillation", plural=False)
G("Extraction", "Extraction", ["extraction", "extracted"], "Extraction (chemistry)",
  "Pulling a substance out of a mixture with a solvent it prefers, as coffee is extracted "
  "with hot water or oils with hexane.", lesson="Extraction", plural=False)
G("Cracking", "Cracking", ["cracking", "steam cracking"], "Cracking (chemistry)",
  "Breaking large hydrocarbon molecules into smaller ones with heat and catalysts: how "
  "refineries turn heavy oil into petrol and ethylene.", lesson="Cracking", plural=False)
G("Ceramic", "Ceramic", ["ceramic"], "Ceramic",
  "A hard, heat-proof material made by firing clay or other inorganic powders: pottery, "
  "brick, porcelain, and modern ones in engines and armour.", lesson="Ceramic")
G("Pigment", "Pigment", ["pigment"], "Pigment",
  "A coloured powder that doesn't dissolve in what carries it, so it colours by covering: "
  "the ochres, lead white and Prussian blue of paints.", lesson="Pigment")
G("Dye", "Dye", ["dye", "dyestuff"], "Dye",
  "A coloured substance that dissolves and binds into what it colours, such as cloth. Indigo "
  "and mauveine are dyes.", lesson="Dye")
G("Mordant", "Mordant", ["mordant"], "Mordant",
  "A substance, usually a metal salt such as alum, that fixes a dye to cloth by binding to "
  "both.", lesson="Dye")
G("Fertilizer", "Fertilizer", ["fertilizer", "fertiliser"], "Fertilizer",
  "A substance that supplies plants with nutrients, chiefly nitrogen, phosphorus and "
  "potassium.", lesson="Fertilizer")
G("Pesticide", "Pesticide", ["pesticide", "insecticide", "herbicide", "fungicide", "rodenticide"], "Pesticide",
  "A substance that kills pests: insecticides kill insects, herbicides weeds, fungicides "
  "moulds and fungi.", lesson="Pesticide")
G("Refrigerant", "Refrigerant", ["refrigerant"], "Refrigerant",
  "A fluid that boils at a low temperature, carrying heat out of a fridge as it evaporates "
  "and condenses again.", lesson="Refrigerant")
G("Semiconductor", "Semiconductor", ["semiconductor"], "Semiconductor",
  "A material that conducts electricity better than an insulator but worse than a metal, and "
  "can be tuned by adding traces of other elements: silicon, germanium, gallium arsenide.",
  lesson="Semiconductor")

# --------------------------------------------------------------------------------------
# Safety
# --------------------------------------------------------------------------------------
G("Toxic", "Toxic", ["toxic", "toxicity", "poisonous"], "Toxicity",
  "Harmful to living things. How harmful depends on the dose: 'the dose makes the poison'.",
  lesson="LabSafety", plural=False)
G("Corrosive", "Corrosive", ["corrosive"], "Corrosive substance",
  "Destroying what it touches, such as skin, eyes or metal, by chemical reaction. Strong "
  "acids and alkalis are corrosive.", lesson="LabSafety", plural=False)
G("Irritant", "Irritant", ["irritant"], "Irritation",
  "Causing redness, itching or inflammation of skin, eyes or airways on contact, without "
  "lasting damage.", lesson="LabSafety")
G("Carcinogen", "Carcinogen", ["carcinogen", "carcinogenic"], "Carcinogen",
  "A substance that can cause cancer, such as asbestos, benzene or tobacco smoke.",
  lesson="LabSafety")
G("Flammable", "Flammable", ["flammable", "inflammable", "flammability", "pyrophoric"], "Flammability",
  "Catching fire easily. (Inflammable means the same thing.) A pyrophoric substance ignites "
  "on its own in air.", lesson="LabSafety", plural=False)
G("Explosive", "Explosive", ["explosive"], "Explosive",
  "A substance that reacts so fast it releases its energy as a sudden blast of hot gas.",
  lesson="Explosive")

# --------------------------------------------------------------------------------------
# Medicine
# --------------------------------------------------------------------------------------
G("Analgesic", "Analgesic", ["analgesic", "painkiller", "pain reliever"], "Analgesic",
  "A medicine that relieves pain, such as aspirin, paracetamol or ibuprofen.",
  lesson="Pharmacology")
G("NSAID", "NSAID", ["nonsteroidal anti-inflammatory drug", "nsaid", "anti-inflammatory"],
  "Nonsteroidal anti-inflammatory drug",
  "A non-steroidal anti-inflammatory drug, such as aspirin, ibuprofen or naproxen: it eases "
  "pain, fever and swelling by blocking the enzymes that make prostaglandins.",
  lesson="Pharmacology")
G("Anesthetic", "Anaesthetic", ["anesthetic", "anaesthetic", "anesthesia", "anaesthesia"], "Anesthetic",
  "A drug that blocks feeling, either in one place (local anaesthetic) or by putting the "
  "patient to sleep (general anaesthetic).", lesson="Pharmacology")
G("Antibiotic", "Antibiotic", ["antibiotic", "antibacterial"], "Antibiotic",
  "A medicine that kills bacteria or stops them growing. Penicillin was the first; "
  "antibiotics do nothing against viruses.", lesson="Antibiotic")
G("Antiseptic", "Antiseptic", ["antiseptic", "disinfectant"], "Antiseptic",
  "A substance that kills germs on skin or in wounds (an antiseptic) or on surfaces (a "
  "disinfectant), such as iodine, alcohol or bleach.", lesson="Antibiotic")
G("Antiviral", "Antiviral", ["antiviral", "antiretroviral"], "Antiviral drug",
  "A medicine against viruses, which works by stopping them copying themselves inside cells.",
  lesson="Pharmacology")
G("Antifungal", "Antifungal", ["antifungal"], "Antifungal",
  "A medicine against fungal infections such as athlete's foot or thrush.",
  lesson="Pharmacology")
G("Antihistamine", "Antihistamine", ["antihistamine"], "Antihistamine",
  "A medicine that blocks histamine, the body's messenger of allergy, easing hay fever and "
  "itching. Older ones also cause drowsiness.", lesson="Pharmacology")
G("Antidepressant", "Antidepressant", ["antidepressant"], "Antidepressant",
  "A medicine for depression and often anxiety, which acts on messengers in the brain such "
  "as serotonin and noradrenaline.", lesson="Pharmacology")
G("Antipsychotic", "Antipsychotic", ["antipsychotic"], "Antipsychotic",
  "A medicine for psychosis, schizophrenia and bipolar disorder, usually by blocking dopamine "
  "receptors.", lesson="Pharmacology")
G("Anticonvulsant", "Anticonvulsant", ["anticonvulsant", "antiepileptic"], "Anticonvulsant",
  "A medicine that prevents or stops seizures, used for epilepsy.", lesson="Pharmacology")
G("Sedative", "Sedative", ["sedative", "sedation", "hypnotic", "anxiolytic"], "Sedative",
  "A medicine that calms (a sedative or, against anxiety, an anxiolytic) or brings on sleep "
  "(a hypnotic).", lesson="Pharmacology")
G("Diuretic", "Diuretic", ["diuretic"], "Diuretic",
  "A medicine that makes the kidneys pass more water and salt, lowering blood pressure and "
  "swelling.", lesson="Pharmacology")
G("Hormone", "Hormone", ["hormone"], "Hormone",
  "A chemical messenger made by a gland and carried in the blood to act elsewhere in the "
  "body: insulin, adrenaline, oestrogen, thyroxine.", lesson="Biochemistry")
G("Neurotransmitter", "Neurotransmitter", ["neurotransmitter"], "Neurotransmitter",
  "A chemical a nerve cell releases to signal the next one: dopamine, serotonin, "
  "acetylcholine, noradrenaline.", lesson="Biochemistry")
G("Receptor", "Receptor", ["receptor", "agonist", "antagonist"], "Receptor (biochemistry)",
  "A protein on or in a cell that a particular molecule fits like a key, triggering a "
  "response. A drug that switches a receptor on is an agonist; one that blocks it, an "
  "antagonist.", lesson="Pharmacology")
G("Metabolite", "Metabolite", ["metabolite", "metabolism", "metabolized", "metabolised"], "Metabolite",
  "A substance the body makes while processing another. Many drugs act through, or are "
  "cleared as, their metabolites.", lesson="Biochemistry")
G("Prodrug", "Prodrug", ["prodrug"], "Prodrug",
  "A medicine given in an inactive form that the body converts into the active drug.",
  lesson="Pharmacology")
G("Vitamin", "Vitamin", ["vitamin"], "Vitamin",
  "A substance the body needs in small amounts but can't make enough of, so it must come "
  "from food, such as vitamin C, whose lack causes scurvy.", lesson="Biochemistry")
G("AminoAcid", "Amino acid", ["amino acid"], "Amino acid",
  "A molecule with both an amine and a carboxylic acid group; twenty kinds chain together to "
  "build every protein.", lesson="AminoAcid")


# --------------------------------------------------------------------------------------
# Reading a name: which of the terms above its parts are
# --------------------------------------------------------------------------------------
# pieces that can begin a word of a name, and their term (longest tried first)
PREFIX_PARTS = sorted([
    ("tetrakis", "Multiplier"), ("tris", "Multiplier"), ("bis", "Multiplier"), ("mono", "Multiplier"),
    ("penta", "Multiplier"), ("hexa", "Multiplier"), ("hepta", "Multiplier"), ("octa", "Multiplier"),
    ("tetra", "Multiplier"), ("tri", "Multiplier"), ("di", "Multiplier"), ("poly", "Polymer"),
    ("cyclo", "BranchPrefix"), ("iso", "BranchPrefix"), ("tert", "BranchPrefix"), ("sec", "BranchPrefix"),
    ("neo", "BranchPrefix"),
    ("chloro", "HaloPrefix"), ("bromo", "HaloPrefix"), ("fluoro", "HaloPrefix"), ("iodo", "HaloPrefix"),
    ("hydroxy", "Hydroxyl"), ("amino", "Amine"), ("nitro", "Nitro"), ("cyano", "Nitrile"), ("thio", "Thiol"),
    ("methoxy", "Alkoxy"), ("ethoxy", "Alkoxy"), ("propoxy", "Alkoxy"), ("butoxy", "Alkoxy"),
    ("methyl", "Methyl"), ("ethyl", "Ethyl"), ("propyl", "Propyl"), ("butyl", "Butyl"), ("pentyl", "Amyl"),
    ("amyl", "Amyl"), ("phenyl", "Phenyl"), ("benzyl", "Benzyl"), ("vinyl", "Vinyl"), ("acetyl", "Acetyl"),
    ("allyl", "Allyl"),
], key=lambda p: -len(p[0]))
# prefixes that only count when what follows them is a known part too ("diamond" is no di-)
NEEDS_KNOWN_REST = {"Multiplier", "BranchPrefix", "Polymer", "Amine", "Nitro", "Nitrile", "Thiol", "Hydroxyl"}
# whole words whose parts the rules would misread
WORD_PARTS = {
    "ethylene": ["ChainRoot", "Alkene"], "propylene": ["ChainRoot", "Alkene"], "butylene": ["ChainRoot", "Alkene"],
    "methylene": ["Methyl"], "acetylene": ["Alkyne"], "benzene": ["Aromatic"], "toluene": ["Aromatic"],
    "xylene": ["Aromatic"], "styrene": ["Aromatic"], "naphthalene": ["Aromatic"],
    "tert": ["BranchPrefix"], "sec": ["BranchPrefix"], "iso": ["BranchPrefix"], "neo": ["BranchPrefix"],
}
# a carbon-chain root, then an ending that says what kind of compound (benzene has no root, so
# it is no alkene; vitriol none, so it is no alcohol)
CHAIN_ROOTS = ("dodec", "undec", "dec", "non", "oct", "hept", "hex", "pent", "but", "prop", "eth", "meth")
CHAIN_ENDINGS = [("anediol", "Glycol"), ("anoate", "CarboxylicAcid"), ("anoic", "CarboxylicAcid"),
                 ("anamide", "Amide"), ("anamine", "Amine"), ("ylamine", "Amine"), ("anol", "Alcohol"),
                 ("anone", "Ketone"), ("anal", "Aldehyde"), ("ane", "Alkane"), ("ene", "Alkene"), ("yne", "Alkyne")]
# -ic and -ous before "acid" mean more or less oxygen only for these mineral acids
OXYACIDS = {"sulfuric", "sulphuric", "sulfurous", "sulphurous", "nitric", "nitrous", "phosphoric", "phosphorous",
            "hypophosphorous", "chloric", "chlorous", "perchloric", "hypochlorous", "bromic", "iodic", "periodic",
            "carbonic", "boric", "arsenous", "selenic", "selenous", "chromic", "silicic", "telluric",
            "hydrochloric", "hydrofluoric", "hydrobromic", "hydroiodic", "hydriodic"}


def _forms():
    owner = {}
    for key, t in TERMS.items():
        for f in t["forms"]:
            owner.setdefault(f.lower(), key)
    return owner


def _chain(word):
    for root in CHAIN_ROOTS:
        if word.startswith(root):
            rest = word[len(root):]
            for end, key in CHAIN_ENDINGS:
                if rest == end:
                    return ["ChainRoot", key]
    return None


def _word_parts(word, owner):
    """The terms a single lowercase word of a name is built from, in order."""
    keys = []

    def known(rest):
        return bool(rest) and (rest in owner or rest in WORD_PARTS or _chain(rest) is not None
                               or any(rest.startswith(p) and k not in NEEDS_KNOWN_REST for p, k in PREFIX_PARTS))
    while word:
        if word in owner:
            return keys + [owner[word]]
        if word in WORD_PARTS:
            return keys + WORD_PARTS[word]
        # a prefix first (methylamine is methyl + amine), then a chain and its ending
        for p, k in PREFIX_PARTS:
            if word.startswith(p) and len(word) > len(p):
                rest = word[len(p):]
                if k in NEEDS_KNOWN_REST and not known(rest):
                    continue
                keys.append(k)
                word = rest
                break
        else:
            return keys + (_chain(word) or [])
    return keys


def name_parts(name, limit=6):
    """The glossary terms a substance's name is built from, in the name's order: whole words
    and phrases the glossary knows (hypochlorite, hydrogen carbonate), then the parts of
    organic names (di- + methyl, eth- + -anol), an oxidation state's Roman numeral, and the
    -ic/-ous of a mineral acid."""
    owner = _forms()
    found = []
    taken = []
    low = name.lower()
    # phrases and whole words first, longest first, as the page text is read
    for f in sorted(owner, key=len, reverse=True):
        for m in re.finditer(r"(?<![a-z])" + re.escape(f) + r"(?![a-z])", low):
            if not any(a < m.end() and m.start() < b for a, b in taken):
                taken.append((m.start(), m.end()))
                found.append((m.start(), owner[f]))
    words = list(re.finditer(r"[a-z]+", low))
    for i, m in enumerate(words):
        if any(a <= m.start() < b for a, b in taken):
            continue
        w = m.group(0)
        nxt = words[i + 1].group(0) if i + 1 < len(words) else ""
        if w in OXYACIDS and nxt == "acid":
            found.append((m.start(), "IcOus"))
            continue
        for k in _word_parts(w, owner):
            found.append((m.start(), k))
    roman = re.search(r"\((?:i|ii|iii|iv|v|vi|vii|viii)\)", low)
    if roman:
        found.append((roman.start(), "OxidationState"))
    out = []
    for _, k in sorted(found, key=lambda x: x[0]):
        if k not in out:
            out.append(k)
    return out[:limit]
