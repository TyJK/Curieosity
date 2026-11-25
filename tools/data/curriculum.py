"""
Curieosity's chemistry curriculum: the ideas behind the reactions, each one a Wikipedia
article. Laws and rules, concepts, techniques, industrial processes, the apparatus the
vessels stand for, and the events of chemistry's history, grouped into units in the order a
course would teach them.

The game's Library shows the curriculum as its own tab; reaction pages, vessel cards, era
banners and hints link the topics that explain them. tools/data/scrape_wiki.py fetches each
topic's article (its lead becomes the topic's page) and tools/data/gen_pages.py writes them
into assets/data/pages.ron with the links worked out in LINKS below.

A topic is (unit, kind, Wikipedia title). The key is how the rest of the content refers to
it; the title is the article's (redirects are followed, so a common spelling is enough).
"""

UNITS = [
    ("matter", "Matter and change"),
    ("atoms", "Atoms and the elements"),
    ("bonds", "Bonds and structure"),
    ("reactions", "Reactions and equations"),
    ("energy", "Energy and rates"),
    ("equilibrium", "Equilibrium"),
    ("gases", "Gases"),
    ("acids", "Acids, bases and salts"),
    ("redox", "Redox and electrochemistry"),
    ("metals", "Metals and metallurgy"),
    ("industry", "Industrial chemistry"),
    ("organic", "Organic chemistry"),
    ("materials", "Polymers and materials"),
    ("life", "Chemistry of life and medicine"),
    ("nuclear", "Nuclear chemistry"),
    ("lab", "The laboratory"),
    ("history", "History of chemistry"),
]

KINDS = ("Law", "Concept", "Technique", "Process", "Apparatus", "Event")

TOPICS = {}


def T(key, unit, kind, title):
    assert kind in KINDS, kind
    assert unit in {u for u, _ in UNITS}, unit
    assert key not in TOPICS, key
    TOPICS[key] = (unit, kind, title)


# --- Matter and change -----------------------------------------------------------------
T("Matter", "matter", "Concept", "Matter")
T("StateOfMatter", "matter", "Concept", "State of matter")
T("PhaseTransition", "matter", "Concept", "Phase transition")
T("MeltingPoint", "matter", "Concept", "Melting point")
T("BoilingPoint", "matter", "Concept", "Boiling point")
T("Sublimation", "matter", "Concept", "Sublimation (phase transition)")
T("ChemicalSubstance", "matter", "Concept", "Chemical substance")
T("Mixture", "matter", "Concept", "Mixture")
T("ChemicalElement", "matter", "Concept", "Chemical element")
T("ChemicalCompound", "matter", "Concept", "Chemical compound")
T("PhysicalChange", "matter", "Concept", "Physical change")
T("Density", "matter", "Concept", "Density")
T("Solubility", "matter", "Concept", "Solubility")
T("Solution", "matter", "Concept", "Solution (chemistry)")
T("Solvent", "matter", "Concept", "Solvent")
T("Colloid", "matter", "Concept", "Colloid")
T("Combustion", "matter", "Concept", "Combustion")
T("FireTriangle", "matter", "Concept", "Fire triangle")
T("SeparationProcess", "matter", "Technique", "Separation process")
T("Filtration", "matter", "Technique", "Filtration")
T("Evaporation", "matter", "Concept", "Evaporation")
T("Crystallization", "matter", "Technique", "Crystallization")
T("Recrystallization", "matter", "Technique", "Recrystallization (chemistry)")
T("Decantation", "matter", "Technique", "Decantation")
T("Sedimentation", "matter", "Technique", "Sedimentation")
T("Centrifugation", "matter", "Technique", "Centrifugation")
T("Extraction", "matter", "Technique", "Extraction (chemistry)")
T("Purity", "matter", "Concept", "Chemical purity")

# --- Atoms and the elements --------------------------------------------------------------
T("Atom", "atoms", "Concept", "Atom")
T("AtomicTheory", "atoms", "Law", "Atomic theory")
T("Proton", "atoms", "Concept", "Proton")
T("Neutron", "atoms", "Concept", "Neutron")
T("Electron", "atoms", "Concept", "Electron")
T("AtomicNumber", "atoms", "Concept", "Atomic number")
T("Isotope", "atoms", "Concept", "Isotope")
T("RelativeAtomicMass", "atoms", "Concept", "Relative atomic mass")
T("BohrModel", "atoms", "Concept", "Bohr model")
T("AtomicOrbital", "atoms", "Concept", "Atomic orbital")
T("ElectronShell", "atoms", "Concept", "Electron shell")
T("ElectronConfiguration", "atoms", "Concept", "Electron configuration")
T("Aufbau", "atoms", "Law", "Aufbau principle")
T("Pauli", "atoms", "Law", "Pauli exclusion principle")
T("Hund", "atoms", "Law", "Hund's rule of maximum multiplicity")
T("PeriodicTable", "atoms", "Concept", "Periodic table")
T("PeriodicLaw", "atoms", "Law", "Periodic trends")
T("Group", "atoms", "Concept", "Group (periodic table)")
T("Period", "atoms", "Concept", "Period (periodic table)")
T("Block", "atoms", "Concept", "Block (periodic table)")
T("Electronegativity", "atoms", "Concept", "Electronegativity")
T("IonizationEnergy", "atoms", "Concept", "Ionization energy")
T("ElectronAffinity", "atoms", "Concept", "Electron affinity")
T("AtomicRadius", "atoms", "Concept", "Atomic radius")
T("Metal", "atoms", "Concept", "Metal")
T("Nonmetal", "atoms", "Concept", "Nonmetal")
T("Metalloid", "atoms", "Concept", "Metalloid")
T("AlkaliMetal", "atoms", "Concept", "Alkali metal")
T("AlkalineEarth", "atoms", "Concept", "Alkaline earth metal")
T("TransitionMetal", "atoms", "Concept", "Transition metal")
T("Lanthanide", "atoms", "Concept", "Lanthanide")
T("Actinide", "atoms", "Concept", "Actinide")
T("Halogen", "atoms", "Concept", "Halogen")
T("NobleGas", "atoms", "Concept", "Noble gas")
T("NativeMetal", "atoms", "Concept", "Native metal")
T("Allotropy", "atoms", "Concept", "Allotropy")

# --- Bonds and structure -------------------------------------------------------------------
T("ChemicalBond", "bonds", "Concept", "Chemical bond")
T("IonicBond", "bonds", "Concept", "Ionic bonding")
T("CovalentBond", "bonds", "Concept", "Covalent bond")
T("MetallicBond", "bonds", "Concept", "Metallic bonding")
T("HydrogenBond", "bonds", "Concept", "Hydrogen bond")
T("Intermolecular", "bonds", "Concept", "Intermolecular force")
T("VanDerWaals", "bonds", "Concept", "Van der Waals force")
T("OctetRule", "bonds", "Law", "Octet rule")
T("Valence", "bonds", "Concept", "Valence (chemistry)")
T("OxidationState", "bonds", "Concept", "Oxidation state")
T("LewisStructure", "bonds", "Concept", "Lewis structure")
T("VSEPR", "bonds", "Law", "VSEPR theory")
T("MolecularGeometry", "bonds", "Concept", "Molecular geometry")
T("Polarity", "bonds", "Concept", "Chemical polarity")
T("Resonance", "bonds", "Concept", "Resonance (chemistry)")
T("Hybridisation", "bonds", "Concept", "Orbital hybridisation")
T("Molecule", "bonds", "Concept", "Molecule")
T("Ion", "bonds", "Concept", "Ion")
T("CrystalStructure", "bonds", "Concept", "Crystal structure")
T("ChemicalFormula", "bonds", "Concept", "Chemical formula")
T("StructuralFormula", "bonds", "Concept", "Structural formula")
T("Isomer", "bonds", "Concept", "Isomer")
T("Chirality", "bonds", "Concept", "Chirality (chemistry)")
T("CoordinationComplex", "bonds", "Concept", "Coordination complex")
T("Chelation", "bonds", "Concept", "Chelation")
T("Hydrate", "bonds", "Concept", "Hydrate")

# --- Reactions and equations ---------------------------------------------------------------
T("ChemicalReaction", "reactions", "Concept", "Chemical reaction")
T("ChemicalEquation", "reactions", "Concept", "Chemical equation")
T("ConservationOfMass", "reactions", "Law", "Conservation of mass")
T("DefiniteProportions", "reactions", "Law", "Law of definite proportions")
T("MultipleProportions", "reactions", "Law", "Law of multiple proportions")
T("Stoichiometry", "reactions", "Concept", "Stoichiometry")
T("Mole", "reactions", "Concept", "Mole (unit)")
T("Avogadro", "reactions", "Concept", "Avogadro constant")
T("MolarMass", "reactions", "Concept", "Molar mass")
T("LimitingReagent", "reactions", "Concept", "Limiting reagent")
T("Yield", "reactions", "Concept", "Yield (chemistry)")
T("ChemicalSynthesis", "reactions", "Concept", "Chemical synthesis")
T("Decomposition", "reactions", "Concept", "Chemical decomposition")
T("ThermalDecomposition", "reactions", "Concept", "Thermal decomposition")
T("SingleDisplacement", "reactions", "Concept", "Single displacement reaction")
T("Metathesis", "reactions", "Concept", "Salt metathesis reaction")
T("Precipitation", "reactions", "Concept", "Precipitation (chemistry)")
T("Hydrolysis", "reactions", "Concept", "Hydrolysis")
T("Hydration", "reactions", "Concept", "Hydration reaction")
T("Dehydration", "reactions", "Concept", "Dehydration reaction")
T("Condensation", "reactions", "Concept", "Condensation reaction")
T("ReactionIntermediate", "reactions", "Concept", "Reactive intermediate")
T("SideReaction", "reactions", "Concept", "Side reaction")

# --- Energy and rates --------------------------------------------------------------------------
T("Thermochemistry", "energy", "Concept", "Thermochemistry")
T("Enthalpy", "energy", "Concept", "Enthalpy")
T("Exothermic", "energy", "Concept", "Exothermic reaction")
T("Endothermic", "energy", "Concept", "Endothermic process")
T("EnthalpyFormation", "energy", "Concept", "Standard enthalpy of formation")
T("Hess", "energy", "Law", "Hess's law")
T("Entropy", "energy", "Concept", "Entropy")
T("Gibbs", "energy", "Concept", "Gibbs free energy")
T("Thermodynamics", "energy", "Law", "Laws of thermodynamics")
T("HeatCapacity", "energy", "Concept", "Heat capacity")
T("Calorimetry", "energy", "Technique", "Calorimetry")
T("Kinetics", "energy", "Concept", "Chemical kinetics")
T("ReactionRate", "energy", "Concept", "Reaction rate")
T("RateEquation", "energy", "Law", "Rate equation")
T("ActivationEnergy", "energy", "Concept", "Activation energy")
T("Arrhenius", "energy", "Law", "Arrhenius equation")
T("CollisionTheory", "energy", "Law", "Collision theory")
T("TransitionState", "energy", "Concept", "Transition state theory")
T("Catalysis", "energy", "Concept", "Catalysis")
T("HeterogeneousCatalysis", "energy", "Concept", "Heterogeneous catalysis")
T("HomogeneousCatalysis", "energy", "Concept", "Homogeneous catalysis")
T("Photochemistry", "energy", "Concept", "Photochemistry")
T("Explosive", "energy", "Concept", "Explosive")

# --- Equilibrium -----------------------------------------------------------------------------
T("Equilibrium", "equilibrium", "Concept", "Chemical equilibrium")
T("LeChatelier", "equilibrium", "Law", "Le Chatelier's principle")
T("EquilibriumConstant", "equilibrium", "Concept", "Equilibrium constant")
T("Reversible", "equilibrium", "Concept", "Reversible reaction")
T("MassAction", "equilibrium", "Law", "Law of mass action")
T("SolubilityEquilibrium", "equilibrium", "Concept", "Solubility equilibrium")
T("CommonIon", "equilibrium", "Concept", "Common-ion effect")

# --- Gases ------------------------------------------------------------------------------------
T("Gas", "gases", "Concept", "Gas")
T("GasLaws", "gases", "Law", "Gas laws")
T("Boyle", "gases", "Law", "Boyle's law")
T("Charles", "gases", "Law", "Charles's law")
T("GayLussac", "gases", "Law", "Gay-Lussac's law")
T("AvogadroLaw", "gases", "Law", "Avogadro's law")
T("IdealGas", "gases", "Law", "Ideal gas law")
T("Dalton", "gases", "Law", "Dalton's law")
T("Henry", "gases", "Law", "Henry's law")
T("Graham", "gases", "Law", "Graham's law")
T("KineticTheory", "gases", "Law", "Kinetic theory of gases")
T("VaporPressure", "gases", "Concept", "Vapor pressure")
T("Raoult", "gases", "Law", "Raoult's law")
T("Liquefaction", "gases", "Technique", "Liquefaction of gases")
T("STP", "gases", "Concept", "Standard temperature and pressure")

# --- Acids, bases and salts ---------------------------------------------------------------------
T("Acid", "acids", "Concept", "Acid")
T("Base", "acids", "Concept", "Base (chemistry)")
T("AcidBase", "acids", "Concept", "Acid–base reaction")
T("BronstedLowry", "acids", "Law", "Brønsted–Lowry acid–base theory")
T("Lewis", "acids", "Law", "Lewis acids and bases")
T("Neutralization", "acids", "Concept", "Neutralization (chemistry)")
T("pH", "acids", "Concept", "PH")
T("Indicator", "acids", "Technique", "PH indicator")
T("Litmus", "acids", "Technique", "Litmus")
T("Titration", "acids", "Technique", "Titration")
T("Buffer", "acids", "Concept", "Buffer solution")
T("AcidStrength", "acids", "Concept", "Acid strength")
T("Alkali", "acids", "Concept", "Alkali")
T("Salt", "acids", "Concept", "Salt (chemistry)")
T("MineralAcid", "acids", "Concept", "Mineral acid")

# --- Redox and electrochemistry -----------------------------------------------------------------
T("Redox", "redox", "Concept", "Redox")
T("OxidizingAgent", "redox", "Concept", "Oxidizing agent")
T("ReducingAgent", "redox", "Concept", "Reducing agent")
T("Electrochemistry", "redox", "Concept", "Electrochemistry")
T("Electrolysis", "redox", "Technique", "Electrolysis")
T("Faraday", "redox", "Law", "Faraday's laws of electrolysis")
T("Electrode", "redox", "Concept", "Electrode")
T("Electrolyte", "redox", "Concept", "Electrolyte")
T("GalvanicCell", "redox", "Apparatus", "Galvanic cell")
T("ElectrolyticCellTopic", "redox", "Apparatus", "Electrolytic cell")
T("ElectrodePotential", "redox", "Concept", "Standard electrode potential")
T("ReactivitySeries", "redox", "Law", "Reactivity series")
T("Corrosion", "redox", "Concept", "Corrosion")
T("Rust", "redox", "Concept", "Rust")
T("Electroplating", "redox", "Technique", "Electroplating")
T("Battery", "redox", "Apparatus", "Electric battery")
T("VoltaicPile", "redox", "Apparatus", "Voltaic pile")
T("FuelCell", "redox", "Apparatus", "Fuel cell")

# --- Metals and metallurgy -------------------------------------------------------------------
T("Metallurgy", "metals", "Concept", "Metallurgy")
T("Ore", "metals", "Concept", "Ore")
T("Smelting", "metals", "Process", "Smelting")
T("Roasting", "metals", "Process", "Roasting (metallurgy)")
T("Calcination", "metals", "Process", "Calcination")
T("Flux", "metals", "Concept", "Flux (metallurgy)")
T("Slag", "metals", "Concept", "Slag")
T("Bloomery", "metals", "Apparatus", "Bloomery")
T("BlastFurnaceTopic", "metals", "Apparatus", "Blast furnace")
T("PigIron", "metals", "Concept", "Pig iron")
T("Steelmaking", "metals", "Process", "Steelmaking")
T("Bessemer", "metals", "Process", "Bessemer process")
T("BOS", "metals", "Process", "Basic oxygen steelmaking")
T("ArcFurnaceTopic", "metals", "Apparatus", "Electric arc furnace")
T("Alloy", "metals", "Concept", "Alloy")
T("Cupellation", "metals", "Process", "Cupellation")
T("Amalgam", "metals", "Concept", "Amalgam (chemistry)")
T("Cementation", "metals", "Process", "Cementation process")
T("FrothFlotation", "metals", "Process", "Froth flotation")
T("GoldPanning", "metals", "Technique", "Gold panning")
T("GoldExtraction", "metals", "Process", "Gold extraction")
T("Cyanidation", "metals", "Process", "Gold cyanidation")
T("Parkes", "metals", "Process", "Parkes process")
T("Kroll", "metals", "Process", "Kroll process")
T("Bayer", "metals", "Process", "Bayer process")
T("HallHeroult", "metals", "Process", "Hall–Héroult process")
T("Mond", "metals", "Process", "Mond process")
T("Pidgeon", "metals", "Process", "Pidgeon process")
T("ZoneMelting", "metals", "Technique", "Zone melting")
T("Czochralski", "metals", "Technique", "Czochralski method")
T("Thermite", "metals", "Process", "Thermite")

# --- Industrial chemistry ------------------------------------------------------------------------
T("ChemicalIndustry", "industry", "Concept", "Chemical industry")
T("ChemicalEngineering", "industry", "Concept", "Chemical engineering")
T("UnitOperation", "industry", "Concept", "Unit operation")
T("ChemicalReactor", "industry", "Apparatus", "Chemical reactor")
T("Leblanc", "industry", "Process", "Leblanc process")
T("Solvay", "industry", "Process", "Solvay process")
T("LeadChamber", "industry", "Process", "Lead chamber process")
T("Contact", "industry", "Process", "Contact process")
T("Haber", "industry", "Process", "Haber process")
T("Ostwald", "industry", "Process", "Ostwald process")
T("BirkelandEyde", "industry", "Process", "Birkeland–Eyde process")
T("FrankCaro", "industry", "Process", "Frank–Caro process")
T("Chloralkali", "industry", "Process", "Chloralkali process")
T("CastnerKellner", "industry", "Process", "Castner–Kellner process")
T("Castner", "industry", "Process", "Castner process")
T("Deacon", "industry", "Process", "Deacon process")
T("DownsCell", "industry", "Apparatus", "Downs cell")
T("Claus", "industry", "Process", "Claus process")
T("SteamReforming", "industry", "Process", "Steam reforming")
T("WaterGasShift", "industry", "Process", "Water–gas shift reaction")
T("FischerTropsch", "industry", "Process", "Fischer–Tropsch process")
T("Cracking", "industry", "Process", "Cracking (chemistry)")
T("SteamCracking", "industry", "Process", "Steam cracking")
T("FCC", "industry", "Process", "Fluid catalytic cracking")
T("OilRefinery", "industry", "Concept", "Oil refinery")
T("Petrochemical", "industry", "Concept", "Petrochemical")
T("Hydrodesulfurization", "industry", "Process", "Hydrodesulfurization")
T("Hydroformylation", "industry", "Process", "Hydroformylation")
T("ZieglerNatta", "industry", "Process", "Ziegler–Natta catalyst")
T("Cumene", "industry", "Process", "Cumene process")
T("Wacker", "industry", "Process", "Wacker process")
T("Monsanto", "industry", "Process", "Monsanto process")
T("Cativa", "industry", "Process", "Cativa process")
T("AirSeparation", "industry", "Process", "Air separation")
T("HampsonLinde", "industry", "Process", "Hampson–Linde cycle")
T("FractionalDistillation", "industry", "Technique", "Fractional distillation")
T("CoalGas", "industry", "Concept", "Coal gas")
T("CoalTar", "industry", "Concept", "Coal tar")
T("Coking", "industry", "Process", "Coke (fuel)")
T("Fertilizer", "industry", "Concept", "Fertilizer")
T("Bleach", "industry", "Concept", "Bleach")
T("Soap", "industry", "Concept", "Soap")
T("Detergent", "industry", "Concept", "Detergent")
T("Surfactant", "industry", "Concept", "Surfactant")
T("Pesticide", "industry", "Concept", "Pesticide")
T("Refrigerant", "industry", "Concept", "Refrigerant")

# --- Organic chemistry ------------------------------------------------------------------------
T("OrganicChemistry", "organic", "Concept", "Organic chemistry")
T("Vitalism", "organic", "Concept", "Vitalism")
T("Hydrocarbon", "organic", "Concept", "Hydrocarbon")
T("Alkane", "organic", "Concept", "Alkane")
T("Alkene", "organic", "Concept", "Alkene")
T("Alkyne", "organic", "Concept", "Alkyne")
T("Aromaticity", "organic", "Concept", "Aromaticity")
T("FunctionalGroup", "organic", "Concept", "Functional group")
T("Alcohol", "organic", "Concept", "Alcohol (chemistry)")
T("Aldehyde", "organic", "Concept", "Aldehyde")
T("Ketone", "organic", "Concept", "Ketone")
T("CarboxylicAcid", "organic", "Concept", "Carboxylic acid")
T("Ester", "organic", "Concept", "Ester")
T("Ether", "organic", "Concept", "Ether")
T("Amine", "organic", "Concept", "Amine")
T("Amide", "organic", "Concept", "Amide")
T("Nitrile", "organic", "Concept", "Nitrile")
T("Organohalide", "organic", "Concept", "Organohalide")
T("OrganicSynthesis", "organic", "Concept", "Organic synthesis")
T("Esterification", "organic", "Process", "Fischer–Speier esterification")
T("Saponification", "organic", "Process", "Saponification")
T("Nitration", "organic", "Process", "Nitration")
T("Sulfonation", "organic", "Process", "Aromatic sulfonation")
T("Halogenation", "organic", "Process", "Halogenation")
T("FriedelCrafts", "organic", "Process", "Friedel–Crafts reaction")
T("Grignard", "organic", "Process", "Grignard reaction")
T("DielsAlder", "organic", "Process", "Diels–Alder reaction")
T("Aldol", "organic", "Process", "Aldol reaction")
T("Hydrogenation", "organic", "Process", "Hydrogenation")
T("Dehydrogenation", "organic", "Process", "Dehydrogenation")
T("AlcoholOxidation", "organic", "Process", "Alcohol oxidation")
T("Substitution", "organic", "Concept", "Substitution reaction")
T("Addition", "organic", "Concept", "Addition reaction")
T("Elimination", "organic", "Concept", "Elimination reaction")
T("EAS", "organic", "Concept", "Electrophilic aromatic substitution")
T("NucleophilicSubstitution", "organic", "Concept", "Nucleophilic substitution")
T("Diazonium", "organic", "Concept", "Diazonium compound")
T("AzoCoupling", "organic", "Process", "Azo coupling")
T("Dye", "organic", "Concept", "Dye")
T("Pigment", "organic", "Concept", "Pigment")
T("AromaCompound", "organic", "Concept", "Aroma compound")
T("EssentialOil", "organic", "Concept", "Essential oil")
T("SteamDistillation", "organic", "Technique", "Steam distillation")
T("Pyrolysis", "organic", "Process", "Pyrolysis")
T("Organometallic", "organic", "Concept", "Organometallic chemistry")
T("Silane", "organic", "Concept", "Organosilicon chemistry")
T("Fluorocarbon", "organic", "Concept", "Fluorocarbon")

# --- Polymers and materials --------------------------------------------------------------------
T("Polymer", "materials", "Concept", "Polymer")
T("Polymerization", "materials", "Process", "Polymerization")
T("ChainGrowth", "materials", "Process", "Chain-growth polymerization")
T("StepGrowth", "materials", "Process", "Step-growth polymerization")
T("Monomer", "materials", "Concept", "Monomer")
T("Copolymer", "materials", "Concept", "Copolymer")
T("Plastic", "materials", "Concept", "Plastic")
T("Thermoplastic", "materials", "Concept", "Thermoplastic")
T("Thermoset", "materials", "Concept", "Thermosetting polymer")
T("Vulcanization", "materials", "Process", "Vulcanization")
T("NaturalRubber", "materials", "Concept", "Natural rubber")
T("SyntheticRubber", "materials", "Concept", "Synthetic rubber")
T("Silicone", "materials", "Concept", "Silicone")
T("Ceramic", "materials", "Concept", "Ceramic")
T("Glass", "materials", "Concept", "Glass")
T("Pottery", "materials", "Concept", "Pottery")
T("Lime", "materials", "Concept", "Lime (material)")
T("LimeMortar", "materials", "Concept", "Lime mortar")
T("Cement", "materials", "Concept", "Cement")
T("Pozzolan", "materials", "Concept", "Pozzolan")
T("RomanConcrete", "materials", "Concept", "Roman concrete")
T("Concrete", "materials", "Concept", "Concrete")
T("PortlandCement", "materials", "Concept", "Portland cement")
T("Semiconductor", "materials", "Concept", "Semiconductor")
T("Doping", "materials", "Technique", "Doping (semiconductor)")
T("CVD", "materials", "Technique", "Chemical vapor deposition")
T("SyntheticDiamond", "materials", "Process", "Synthetic diamond")
T("Nanomaterials", "materials", "Concept", "Nanomaterials")
T("Fullerene", "materials", "Concept", "Fullerene")
T("Graphene", "materials", "Concept", "Graphene")
T("Superconductivity", "materials", "Concept", "Superconductivity")

# --- Chemistry of life and medicine ------------------------------------------------------------
T("Biochemistry", "life", "Concept", "Biochemistry")
T("Fermentation", "life", "Process", "Fermentation")
T("EthanolFermentation", "life", "Process", "Ethanol fermentation")
T("Yeast", "life", "Concept", "Yeast")
T("Enzyme", "life", "Concept", "Enzyme")
T("Protein", "life", "Concept", "Protein")
T("AminoAcid", "life", "Concept", "Amino acid")
T("Carbohydrate", "life", "Concept", "Carbohydrate")
T("Lipid", "life", "Concept", "Lipid")
T("NucleicAcid", "life", "Concept", "Nucleic acid")
T("Photosynthesis", "life", "Concept", "Photosynthesis")
T("NaturalProduct", "life", "Concept", "Natural product")
T("Alkaloid", "life", "Concept", "Alkaloid")
T("Terpene", "life", "Concept", "Terpene")
T("MedicinalChemistry", "life", "Concept", "Medicinal chemistry")
T("Pharmacology", "life", "Concept", "Pharmacology")
T("Antibiotic", "life", "Concept", "Antibiotic")
T("Biotechnology", "life", "Concept", "Biotechnology")
T("IndustrialFermentation", "life", "Process", "Industrial fermentation")
T("MetabolicEngineering", "life", "Technique", "Metabolic engineering")
T("Vinegar", "life", "Concept", "Vinegar")
T("Brewing", "life", "Process", "Brewing")

# --- Nuclear chemistry -------------------------------------------------------------------------
T("Radioactivity", "nuclear", "Concept", "Radioactive decay")
T("AlphaDecay", "nuclear", "Concept", "Alpha decay")
T("BetaDecay", "nuclear", "Concept", "Beta decay")
T("GammaRay", "nuclear", "Concept", "Gamma ray")
T("HalfLife", "nuclear", "Concept", "Half-life")
T("Fission", "nuclear", "Concept", "Nuclear fission")
T("Fusion", "nuclear", "Concept", "Nuclear fusion")
T("Transmutation", "nuclear", "Concept", "Nuclear transmutation")
T("NuclearReactorTopic", "nuclear", "Apparatus", "Nuclear reactor")
T("CyclotronTopic", "nuclear", "Apparatus", "Cyclotron")
T("Accelerator", "nuclear", "Apparatus", "Particle accelerator")
T("SyntheticElement", "nuclear", "Concept", "Synthetic element")
T("Transuranium", "nuclear", "Concept", "Transuranium element")
T("Radiochemistry", "nuclear", "Concept", "Radiochemistry")
T("IsotopeSeparation", "nuclear", "Technique", "Isotope separation")
T("Enrichment", "nuclear", "Technique", "Enriched uranium")
T("Irradiation", "nuclear", "Technique", "Irradiation")

# --- The laboratory (the vessels and the bench) -------------------------------------------------
T("Laboratory", "lab", "Concept", "Laboratory")
T("Glassware", "lab", "Apparatus", "Laboratory glassware")
T("Flask", "lab", "Apparatus", "Laboratory flask")
T("Beaker", "lab", "Apparatus", "Beaker (laboratory equipment)")
T("TestTube", "lab", "Apparatus", "Test tube")
T("Crucible", "lab", "Apparatus", "Crucible")
T("Retort", "lab", "Apparatus", "Retort")
T("Alembic", "lab", "Apparatus", "Alembic")
T("Distillation", "lab", "Technique", "Distillation")
T("Condenser", "lab", "Apparatus", "Condenser (laboratory)")
T("FractionatingColumn", "lab", "Apparatus", "Fractionating column")
T("BunsenBurner", "lab", "Apparatus", "Bunsen burner")
T("Furnace", "lab", "Apparatus", "Furnace")
T("Kiln", "lab", "Apparatus", "Kiln")
T("MortarPestle", "lab", "Apparatus", "Mortar and pestle")
T("Kipp", "lab", "Apparatus", "Kipp's apparatus")
T("Autoclave", "lab", "Apparatus", "Autoclave")
T("PressureVessel", "lab", "Apparatus", "Pressure vessel")
T("PackedBed", "lab", "Apparatus", "Packed bed")
T("Centrifuge", "lab", "Apparatus", "Centrifuge")
T("Ultracentrifuge", "lab", "Apparatus", "Ultracentrifuge")
T("Bioreactor", "lab", "Apparatus", "Bioreactor")
T("Refrigeration", "lab", "Technique", "Refrigeration")
T("Chromatography", "lab", "Technique", "Chromatography")
T("Spectroscopy", "lab", "Technique", "Spectroscopy")
T("MassSpectrometry", "lab", "Technique", "Mass spectrometry")
T("NMR", "lab", "Technique", "Nuclear magnetic resonance spectroscopy")
T("Balance", "lab", "Apparatus", "Analytical balance")
T("LabSafety", "lab", "Concept", "Laboratory safety")
T("GHS", "lab", "Concept", "Globally Harmonized System of Classification and Labelling of Chemicals")
T("FumeHood", "lab", "Apparatus", "Fume hood")

# --- History of chemistry -----------------------------------------------------------------------
T("HistoryOfChemistry", "history", "Event", "History of chemistry")
T("BronzeAge", "history", "Event", "Bronze Age")
T("Chalcolithic", "history", "Event", "Chalcolithic")
T("IronAge", "history", "Event", "Iron Age")
T("FerrousHistory", "history", "Event", "History of ferrous metallurgy")
T("Alchemy", "history", "Event", "Alchemy")
T("IslamicAlchemy", "history", "Event", "Alchemy in the medieval Islamic world")
T("PhilosophersStone", "history", "Concept", "Philosopher's stone")
T("ClassicalElements", "history", "Concept", "Classical element")
T("Phlogiston", "history", "Concept", "Phlogiston theory")
T("ChemicalRevolution", "history", "Event", "Chemical revolution")
T("PneumaticChemistry", "history", "Event", "Pneumatic chemistry")
T("IndustrialRevolution", "history", "Event", "Industrial Revolution")
T("SecondIndustrialRevolution", "history", "Event", "Second Industrial Revolution")
T("WohlerSynthesis", "history", "Event", "Wöhler synthesis")
T("HistoryPeriodicTable", "history", "Event", "History of the periodic table")
T("Mauveine", "history", "Event", "Mauveine")
T("GoldRush", "history", "Event", "California gold rush")
T("Witwatersrand", "history", "Event", "Witwatersrand Gold Rush")
T("Pompeii", "history", "Event", "Pompeii")
T("Electrification", "history", "Event", "Electrification")
T("GreenRevolution", "history", "Event", "Green Revolution")
T("ManhattanProject", "history", "Event", "Manhattan Project")
T("DiscoveryFission", "history", "Event", "Discovery of nuclear fission")
T("AgeOfPlastics", "history", "Event", "Bakelite")
T("Penicillin", "history", "Event", "History of penicillin")
T("MontrealProtocol", "history", "Event", "Montreal Protocol")
T("SilentSpring", "history", "Event", "Silent Spring")
T("GreenChemistry", "history", "Concept", "Green chemistry")
T("SpaceAge", "history", "Event", "Space Age")
T("InformationAge", "history", "Event", "Information Age")


# --------------------------------------------------------------------------------------
# Links: which topics explain which parts of the game
# --------------------------------------------------------------------------------------
# Each vessel (by its process) and the topics behind it: what it is, then what it does.
VESSEL_TOPICS = {
    "Mix": ["MortarPestle", "Mixture"],
    "Heat": ["Furnace", "Combustion"],
    "Fermenter": ["Fermentation", "Yeast"],
    "Smelting": ["Bloomery", "Smelting"],
    "Distillation": ["Alembic", "Distillation"],
    "Cool": ["Crystallization", "Refrigeration"],
    "Irradiate": ["Irradiation", "Photochemistry"],
    "Flask": ["Flask", "Glassware"],
    "Electrolysis": ["VoltaicPile", "Electrolysis"],
    "Catalysis": ["PackedBed", "HeterogeneousCatalysis"],
    "Polymerize": ["Polymerization", "ChemicalReactor"],
    "BlastFurnace": ["BlastFurnaceTopic", "PigIron"],
    "Column": ["FractionatingColumn", "FractionalDistillation"],
    "ElectrolyticCell": ["ElectrolyticCellTopic", "Electrolysis"],
    "Centrifuge": ["Centrifuge", "Centrifugation"],
    "AirLiquefier": ["HampsonLinde", "AirSeparation"],
    "Pressurize": ["Autoclave", "PressureVessel"],
    "ArcFurnace": ["ArcFurnaceTopic", "Steelmaking"],
    "HighPressure": ["PressureVessel", "LeChatelier"],
    "Cracker": ["FCC", "Cracking"],
    "Bioreactor": ["Bioreactor", "IndustrialFermentation"],
    "Ultracentrifuge": ["Ultracentrifuge", "Centrifugation"],
    "NuclearReactor": ["NuclearReactorTopic", "Fission"],
    "CrystalPuller": ["Czochralski", "Semiconductor"],
    "DiamondPress": ["SyntheticDiamond", "Allotropy"],
    "CvdChamber": ["CVD", "Semiconductor"],
    "Cyclotron": ["CyclotronTopic", "Transmutation"],
}

# The events of each era of the game.
ERA_TOPICS = {
    "Fire & Ore": ["Chalcolithic", "BronzeAge", "FerrousHistory"],
    "Antiquity": ["IronAge", "ClassicalElements", "Pompeii"],
    "Alchemy": ["Alchemy", "IslamicAlchemy", "PhilosophersStone"],
    "Steam & Revolution": ["PneumaticChemistry", "Phlogiston", "ChemicalRevolution", "IndustrialRevolution",
                           "AtomicTheory"],
    "Industry": ["SecondIndustrialRevolution", "WohlerSynthesis", "Mauveine", "HistoryPeriodicTable",
                 "GoldRush", "Witwatersrand", "Electrification"],
    "Modern": ["AgeOfPlastics", "Penicillin", "DiscoveryFission", "ManhattanProject", "GreenRevolution",
               "SilentSpring"],
    "Frontier": ["SpaceAge", "InformationAge", "MontrealProtocol", "GreenChemistry"],
    "The Laboratory": ["Laboratory", "LabSafety", "HistoryOfChemistry"],
}

# (pattern, topics): a reaction whose name (or, for the ones marked, its description) matches
# is explained by these topics. Named processes first, then kinds of reaction. Case-blind.
NAME_RULES = [
    (r"\bHaber\b|Haber.Bosch", ["Haber", "LeChatelier", "Equilibrium"]),
    (r"Contact Process|\bContact\b", ["Contact", "LeChatelier"]),
    (r"Lead.Chamber", ["LeadChamber"]),
    (r"Ostwald", ["Ostwald"]),
    (r"Solvay", ["Solvay"]),
    (r"Leblanc", ["Leblanc"]),
    (r"Birkeland|Eyde", ["BirkelandEyde"]),
    (r"Frank.Caro|Cyanamide", ["FrankCaro"]),
    (r"Castner.Kellner|Chlor.?alkali|Membrane Cell|Mercury Cell|Diaphragm Cell", ["Chloralkali", "Electrolysis"]),
    (r"Castner", ["Castner"]),
    (r"Deacon", ["Deacon"]),
    (r"\bDowns\b", ["DownsCell", "Electrolysis"]),
    (r"\bClaus\b", ["Claus"]),
    (r"Steam Reform|Reforming", ["SteamReforming"]),
    (r"Water.Gas Shift|Shift Reaction", ["WaterGasShift", "Equilibrium"]),
    (r"Water.Gas\b|Producer Gas|Syngas", ["SteamReforming", "CoalGas"]),
    (r"Fischer.Tropsch", ["FischerTropsch"]),
    (r"Hall.H.roult", ["HallHeroult", "Electrolysis"]),
    (r"\bBayer\b", ["Bayer"]),
    (r"\bKroll\b", ["Kroll"]),
    (r"\bMond\b", ["Mond"]),
    (r"Pidgeon", ["Pidgeon"]),
    (r"Parkes", ["Parkes"]),
    (r"Bessemer", ["Bessemer", "Steelmaking"]),
    (r"Basic Oxygen|\bBOS\b|Linz.Donawitz", ["BOS", "Steelmaking"]),
    (r"Open.Hearth|Siemens.Martin|Puddl|Crucible Steel|Steel", ["Steelmaking"]),
    (r"Cumene|Hock", ["Cumene"]),
    (r"Wacker", ["Wacker"]),
    (r"Monsanto", ["Monsanto"]),
    (r"Cativa", ["Cativa"]),
    (r"Hydroformyl|\bOxo\b", ["Hydroformylation"]),
    (r"Ziegler|Natta", ["ZieglerNatta", "ChainGrowth"]),
    (r"Czochralski", ["Czochralski"]),
    (r"Zone (Refin|Melt)", ["ZoneMelting"]),
    (r"Thermite|Goldschmidt", ["Thermite", "ReactivitySeries"]),
    (r"Cyanide Leach|Cyanidation|MacArthur", ["Cyanidation", "GoldExtraction"]),
    (r"Panning", ["GoldPanning", "Density"]),
    (r"Amalgam", ["Amalgam", "GoldExtraction"]),
    (r"Cupel", ["Cupellation"]),
    (r"Cementation", ["Cementation"]),
    (r"Flotation", ["FrothFlotation"]),
    (r"Kipp", ["Kipp"]),
    (r"Roman Concrete", ["RomanConcrete", "Pozzolan", "Pompeii"]),
    (r"Portland", ["PortlandCement", "Cement"]),
    (r"Concrete", ["Concrete"]),
    (r"Lime Burn|Burning Lime|Quicklime|Lime Kiln", ["Lime", "Calcination"]),
    (r"Slak", ["Lime", "Exothermic"]),
    (r"Mortar", ["LimeMortar"]),
    (r"Glass", ["Glass"]),
    (r"Potter|Firing Clay|Fired Clay|Brick|Porcelain|Ceramic", ["Pottery", "Ceramic"]),
    (r"Vulcani", ["Vulcanization", "NaturalRubber"]),
    (r"Saponif|\bSoap", ["Saponification", "Soap"]),
    (r"Esterif|Ester\b|Acetylation", ["Esterification", "Ester"]),
    (r"Nitrat(ion|ing)|Nitration", ["Nitration", "EAS"]),
    (r"Sulfonat|Sulphonat", ["Sulfonation", "EAS"]),
    (r"Friedel|Crafts", ["FriedelCrafts", "EAS"]),
    (r"Grignard", ["Grignard", "Organometallic"]),
    (r"Diels", ["DielsAlder"]),
    (r"Aldol", ["Aldol"]),
    (r"Dehydrogenat", ["Dehydrogenation"]),
    (r"Hydrogenat|Hardening", ["Hydrogenation", "Catalysis"]),
    (r"Diazo|Azo\b|Azo ", ["Diazonium", "AzoCoupling", "Dye"]),
    (r"Chlorinat|Brominat|Fluorinat|Iodinat|Halogenat", ["Halogenation"]),
    (r"Polymeri[sz]|Polymer\b", ["Polymerization"]),
    (r"Nylon|Polyester|Polycondens|Polyamide|Polyurethane|Polycarbonate", ["StepGrowth", "Polymer"]),
    (r"Poly(ethylene|propylene|styrene|vinyl)|PVC|PTFE|Teflon|Acrylic", ["ChainGrowth", "Plastic"]),
    (r"Silicone|Siloxane", ["Silicone", "Silane"]),
    (r"Cider|Wine|Beer|Brew|Mead|Sake", ["EthanolFermentation", "Brewing"]),
    (r"Vinegar", ["Vinegar", "Fermentation"]),
    (r"Ferment", ["Fermentation"]),
    (r"Steam Distil", ["SteamDistillation", "EssentialOil"]),
    (r"Distil", ["Distillation"]),
    (r"Crack", ["Cracking"]),
    (r"Smelt", ["Smelting", "Redox"]),
    (r"Roast", ["Roasting"]),
    (r"Calcin", ["Calcination", "ThermalDecomposition"]),
    (r"Electroplat|Gilding", ["Electroplating"]),
    (r"Electrolys|Electrolytic|Electrowin", ["Electrolysis", "Faraday"]),
    (r"Neutrali", ["Neutralization", "AcidBase"]),
    (r"Precipitat", ["Precipitation", "SolubilityEquilibrium"]),
    (r"Decompos", ["ThermalDecomposition"]),
    (r"Hydroly", ["Hydrolysis"]),
    (r"Dehydrat", ["Dehydration"]),
    (r"Hydrat", ["Hydration"]),
    (r"Pyroly|Dry Distil|Destructive Distil", ["Pyrolysis"]),
    (r"Coking|\bCoke\b", ["Coking", "Pyrolysis"]),
    (r"Coal Gas|Gasworks|Town Gas", ["CoalGas"]),
    (r"Coal Tar", ["CoalTar"]),
    (r"Liquef|Liquid Air|Liquid Nitrogen|Liquid Oxygen", ["Liquefaction", "AirSeparation"]),
    (r"Crystalli", ["Crystallization"]),
    (r"Extract|Leach", ["Extraction"]),
    (r"Centrifug|Separating", ["Centrifugation"]),
    (r"Enrich", ["Enrichment", "IsotopeSeparation"]),
    (r"Fission", ["Fission"]),
    (r"Fusion", ["Fusion"]),
    (r"Decay|Alpha|Beta\b", ["Radioactivity", "HalfLife"]),
    (r"Transmut|Bombard|Synthesi[sz]ing Element", ["Transmutation", "SyntheticElement"]),
    (r"Photograph|Sunlight|Light\b", ["Photochemistry"]),
    (r"Rust|Corrod|Corrosion|Tarnish", ["Corrosion", "Redox"]),
    (r"Burning|Combustion|Burns\b|\bBurn", ["Combustion", "Exothermic"]),
    (r"Reduc", ["Redox", "ReducingAgent"]),
    (r"Oxidi[sz]|Oxidation", ["Redox", "OxidizingAgent"]),
    (r"Isomeri", ["Isomer"]),
    (r"Chelat|EDTA", ["Chelation", "CoordinationComplex"]),
    (r"Vapou?r Deposit|\bCVD\b|Epitax", ["CVD"]),
    (r"Diamond", ["SyntheticDiamond"]),
    (r"Doping|Dopant", ["Doping", "Semiconductor"]),
    (r"Dye|Indigo|Madder|Alizarin|Mauve|Woad", ["Dye"]),
    (r"Pigment|Paint|Ochre|Lake\b", ["Pigment"]),
    (r"Fragrance|Perfume|Musk|Scent", ["AromaCompound"]),
    (r"Alkaloid|Morphine|Quinine|Caffeine|Nicotine|Atropine", ["Alkaloid", "NaturalProduct"]),
    (r"Sugar|Glucose|Starch|Sucrose|Cellulose", ["Carbohydrate"]),
    (r"Amino Acid|Peptide|Protein|Glycine|Alanine|Leucine|Tyrosine|Asparagine|Serine|Cystine|Lysine|Glutamic",
     ["AminoAcid", "Protein"]),
    (r"Enzym", ["Enzyme"]),
    (r"Bleach", ["Bleach"]),
    (r"Fertili[sz]|Superphosphate", ["Fertilizer"]),
    (r"Explosi|Gunpowder|Dynamite|Nitroglycerin|TNT|Cordite", ["Explosive"]),
]

# Rules for these topics read only a reaction's name: in a description their words (light,
# burn, reduce, extract) are too often said in passing.
NAME_ONLY = {"Photochemistry", "Combustion", "Redox", "Extraction", "ThermalDecomposition", "Dye", "Pigment",
             "AromaCompound", "Carbohydrate", "AminoAcid", "Explosive", "Alkaloid", "Enzyme", "Bleach",
             "Fertilizer", "Isomer", "Crystallization", "Corrosion", "Centrifugation", "Glass", "Concrete",
             "LimeMortar", "Steelmaking", "Hydration", "Dehydration", "Hydrolysis", "Fusion", "Radioactivity",
             "Pottery", "SyntheticDiamond", "Polymerization", "Distillation", "Precipitation"}

# Reactions also get topics from what they do (gen_pages.py works these out): an acid with a
# base, a radioactive product, a catalyst in the slot, a medicine made, heat given out or
# taken in.
PROPERTY_TOPICS = {
    "neutralisation": ["Neutralization", "AcidBase"],
    "metal_in_acid": ["SingleDisplacement", "ReactivitySeries"],
    "radioactive": ["Radioactivity"],
    "catalyst": ["Catalysis"],
    "medicine": ["MedicinalChemistry"],
    "polymer": ["Polymer"],
    "exothermic": ["Exothermic"],
    "endothermic": ["Endothermic"],
}

MAX_REACTION_TOPICS = 4


def titles():
    """Every topic's Wikipedia title (for the scraper)."""
    return sorted({t for _, _, t in TOPICS.values()})


if __name__ == "__main__":
    import collections
    print(len(TOPICS), "topics in", len(UNITS), "units")
    print(collections.Counter(u for u, _, _ in TOPICS.values()))
    print(collections.Counter(k for _, k, _ in TOPICS.values()))
