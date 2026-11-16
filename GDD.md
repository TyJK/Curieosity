

# **Game Design Document: Chem-Alchemy**

## **The Alchemical Vision: Core Principles and Player Journey**

This document outlines the complete design for "Chem-Alchemy," an educational game that merges the addictive discovery loop of alchemy-style games with the scientific rigor of chemistry. It is intended to serve as a comprehensive blueprint for development, covering game mechanics, content progression, player engagement strategies, and technical implementation using Rust and the Bevy game engine.

### **High-Concept Pitch & Design Philosophy**

Pitch: "Chem-Alchemy is a mobile-first educational game where players explore the universe of chemistry, from combining basic elements to mastering complex industrial processes. It merges the addictive discovery loop of Little Alchemy with the rigor of a chemistry textbook, creating a sandbox for experimentation, learning, and creation."

The game's design is built upon a foundation of core pillars that guide every mechanical and content-related decision. These pillars ensure a cohesive and effective educational experience that is both engaging and scientifically sound.

Design Pillars:

1. 	  
   Scientific 	Authenticity: The bedrock of the game is its commitment to 	real-world chemistry. Every reaction, ingredient, and process is 	based on established scientific principles. While simplifications 	are occasionally necessary to facilitate gameplay—for instance, 	representing reaction rates or abstracting complex purification 	steps—these will be made with clear pedagogical intent and will 	not violate fundamental chemical laws. The goal is to build a 	correct mental model of chemical interactions, not a fantasy 	approximation.1  
2. 	  
   Guided 	Discovery: The game must navigate the fine line between the joy of 	unguided experimentation and the potential for overwhelming 	frustration. It achieves this by balancing a freeform sandbox 	environment with a structured progression system. This system, 	centered on a "Technology Tree," provides players with a 	roadmap of possibilities, preventing them from becoming hopelessly 	stuck while still encouraging them to form and test their own 	hypotheses.2  
3. 	  
   Intrinsic 	Motivation: The primary reward in Chem-Alchemy is the act of 	learning itself. The game is designed to celebrate the "aha\!" 	moment of understanding a new chemical principle or successfully 	synthesizing a complex compound. External rewards like points and 	badges serve to reinforce and recognize this intrinsic satisfaction, 	rather than replacing it. The core gameplay loop is engineered to 	generate a consistent dopamine response tied to creativity and 	revelation, leveraging this feedback loop in a positive, educational 	manner.1  
4. 	  
   From 	Atoms to Industry: The player's progression is designed to mirror 	the historical and conceptual development of chemistry. The journey 	begins with the fundamental building blocks of matter and culminates 	in the large-scale industrial syntheses that define the modern 	world. This narrative arc provides a powerful sense of scale and 	accomplishment, transforming the player from a novice experimenting 	with elements into a master industrial chemist capable of 	manipulating matter on a grand scale.4

### **Deconstructing the Addictive Loop: Creativity, Surprise, and Escalation**

The enduring appeal of games like Little Alchemy or match 3 puzzle games stems from their masterful manipulation of three key psychological drivers: creativity, surprise, and escalation.1 Chem-Alchemy will adapt these principles, grounding them in a scientifically accurate framework to create a uniquely compelling educational experience.

Creativity: Players are active participants in the scientific process, not passive recipients of facts. The game provides a digital laboratory, a sandbox where they can formulate and test hypotheses. This active engagement is critical for cognitive development and deep learning. The player is constantly asking "What if?"—What if I combine salt and water? What happens if I then apply heat? What if I try to pass electricity through it? This process of inquiry, experimentation, and observation places the player in the role of a scientist, making learning an act of creation rather than memorization. This active role is a core component of satisfying gameplay mechanics, as it gives player actions meaningful consequences within the game world.1

Surprise: A key element of the discovery loop is the "moment of revelation," the satisfying payoff that comes from a successful experiment.1 This is most powerful when the outcome is both unexpected and logical. While some reactions will be intuitive (e.g., combining an acid and a base leads to neutralization), many will introduce new concepts. For example, discovering that mixing zinc metal with hydrochloric acid produces hydrogen gas is a surprising outcome that teaches the principle of single displacement reactions. The game's design will focus on curating these moments of revelation, ensuring that each new discovery not only expands the player's inventory but also deepens their understanding of the underlying chemical rules.

Escalation: The game feeds the natural human desire for growth and progress by continuously expanding the player's capabilities.1 Each new substance discovered becomes a new tool, a new reactant that exponentially increases the number of possible combinations. This progression is not merely linear; it is compositional. Early discoveries are the building blocks for more complex ones. Water is not just an endpoint; it is a reactant for electrolysis, a solvent, and a key component in hydration reactions. This sense of escalating complexity is formally managed by the game's Technology Tree and Milestone Unlock system, which ensures that the player's growing knowledge is matched by a growing set of tools and challenges.2

A significant design challenge lies in adapting this model to the rigors of real chemistry. The intuitive, often metaphorical combinations of Little Alchemy (e.g., Sun \+ Mud \= Brick) are not directly translatable to a scientific context.7 A player cannot be expected to intuit the specific temperature, pressure, and catalytic conditions required for the Haber-Bosch process.8 Therefore, the game's core design must shift away from simple ingredient combination and toward process simulation. The fundamental verbs of the game—heating, cooling, applying pressure—are not just additional ingredients; they are the tools the player must learn to use. The game's structure is thus built around teaching the player how and when to apply these processes, transforming the gameplay from a simple matching puzzle into a series of interactive experiments.

### **The Player Journey: From Novice to Industrial Chemist**

The player's journey through Chem-Alchemy is structured as a progression through distinct phases of chemical understanding, mirroring the historical evolution of the science.

Phase 1: The Elements. The player begins with a sparse inventory containing a handful of the most fundamental and abundant elements, such as Hydrogen, Oxygen, Carbon, Sodium, and Chlorine.9 Their toolkit of processes is equally limited, consisting only of Mix, Heat, and Cool. In this initial phase, the player's primary goal is to discover basic chemical principles: the formation of simple binary compounds (synthesis), the concept of state changes (solid, liquid, gas), and the breaking of compounds back into their constituent elements (decomposition). Discoveries in this phase include foundational substances like Water ($H\_2O$), Table Salt ($NaCl$), Carbon Dioxide ($CO\_2$), and Methane ($CH\_4$). This phase establishes the core gameplay loop and introduces the fundamental "rules" of chemical combination.

Phase 2: The Alchemist's Lab. As the player makes more discoveries, they enter a phase of broader exploration. Milestone unlocks grant them access to new processes like Electrolysis and Distillation, and their inventory of known elements expands to include key metals and non-metals like Iron, Copper, Sulfur, and Phosphorus. This phase focuses on exploring a wider variety of reaction types. The player will discover single and double displacement reactions, acid-base neutralizations, and the basics of organic chemistry. They will synthesize their first acids and bases, precipitate salts from solutions, and build simple carbon chains. This phase represents the transition from elemental chemistry to the more complex and varied world of compound chemistry.

Phase 3: The Industrial Revolution. Having mastered laboratory-scale chemistry, the player graduates to the world of industrial synthesis. This final phase is structured around a series of capstone "projects" or "quests," where the goal is to replicate major industrial chemical processes. Unlocking these quests requires significant progress through the Technology Tree, ensuring the player has the necessary prerequisite knowledge and equipment (e.g., high-pressure reactors, catalytic converters). These multi-step processes, such as the Haber-Bosch process for ammonia and the Contact process for sulfuric acid, will challenge the player to apply everything they have learned about stoichiometry, catalysts, temperature, and pressure to produce key industrial chemicals on a simulated large scale.4 Success in this phase marks the culmination of the player's journey, transforming them from a curious experimenter into a master of applied chemistry.

## **The Alchemical Workbench: A Simple and Satisfying Core Loop**

The core gameplay experience is designed for simplicity and satisfaction, prioritizing the joy of discovery over complex logistical management. The interaction model is a refined version of the classic alchemy game, enhanced with scientific processes and offering an optional layer of complexity for advanced players.

### **The Core Loop: Discovery Through Combination**

The primary interaction is direct and intuitive, centered on a clean, free-form "Reaction Canvas." This moves away from building persistent production lines and focuses on the immediate, satisfying act of experimentation.1

1. 	  
   Selection: 	The player drags icons for Ingredients (elements and compounds, 	represented with molecular diagrams) from their inventory onto the 	Reaction Canvas.  
2. 	  
   Combination: 	The player then drags an icon for a Process (e.g., Heat, Cool, 	Electrolysis) from a static toolbar and drops it onto the collection 	of ingredients on the canvas. This "clicking together" of 	chemicals and processes is the fundamental action of the game.  
3. 	  
   Revelation: 	If the combination of ingredients and the applied process matches a 	valid recipe in the game's vast database, a reaction occurs. This is 	accompanied by a satisfying visual effect (e.g., bubbling, a flash 	of light, a color change).  
4. 	  
   Discovery: 	The newly created substance appears on the canvas. A notification 	announces the discovery, and the new ingredient is permanently added 	to the player's inventory. Crucially, a detailed entry for the new 	substance is unlocked in the Alchemical Codex, complete with its 	2D/3D model, chemical properties, and the recipe used to create it.  
5. 	  
   Experimentation: 	If the combination is not valid, a simple, non-punitive sound or 	visual cue indicates that no reaction occurred, encouraging the 	player to try a different combination without penalty.

This loop is designed to be rapid and rewarding, tapping into the core psychological drivers of creativity and surprise that make discovery games so compelling.1 The primary reward is not the item itself, but the unlocking of knowledge within the Codex.

### **From Puzzle to Blueprint: Optional Automation**

While the core loop is about one-off discoveries, the game acknowledges the intellectual and visual appeal of complex, multi-step syntheses. Instead of forcing players to build and maintain physical production chains, these are treated as puzzles to be solved once and then saved as "Blueprints."

* 	  
  Chained 	Reactions on the Canvas: For a multi-step process, the product of 	one reaction can remain on the Reaction Canvas to be used as the 	reactant for the next step. This allows players to work through a 	complex synthesis sequentially, like solving a multi-part puzzle.  
* 	  
  Saving 	a Blueprint: Upon successfully completing a significant multi-step 	synthesis (e.g., the Contact Process for sulfuric acid), the entire 	sequence of steps is automatically saved as an interactive flowchart 	or "Blueprint" in the Alchemical Codex.  
* 	  
  Using 	and Modifying Blueprints:  
* 	  
  Automation: 	A player can "run" a saved Blueprint. As long as they 	possess the necessary base ingredients, the final product is created 	without needing to manually perform each step again. This respects 	the player's time and treats the solved puzzle as mastered 	knowledge.  
* 	  
  Modification 	and Experimentation: This is the key to encouraging guided, 	intelligent experimentation. A player can duplicate any Blueprint 	and edit it. For example, after discovering a specific 	esterification process, they can copy the blueprint, swap the 	initial alcohol with a different one from their inventory, and see 	if a new, related ester can be synthesized. This transforms the 	Blueprint system from a simple automation tool into a powerful 	platform for exploring entire families of related chemical 	reactions, directly addressing the goal of encouraging guided 	experimentation.

This hybrid system provides the best of both worlds: the simple, satisfying "click-and-discover" gameplay of Little Alchemy for the core experience, and an optional, intellectually engaging layer of process design inspired by the clarity of games like Opus Magnum.55

## **The Path of Discovery: Progression, Unlocks, and the Technology Tree**

A central design challenge is to guide the player through the vast landscape of chemistry without resorting to simple recipe lists, which would undermine the core loop of discovery. The progression system must provide structure and direction while preserving the player's sense of agency and experimentation. This is achieved through a dual-system of a visual Technology Tree and milestone-based process unlocks.

### **The Technology Tree: A Map of Scientific Progress**

The primary progression mechanic will be a visual Technology Tree, a feature common in strategy games that is exceptionally well-suited for mapping scientific and technological advancement.11 This tree will serve as the player's comprehensive map of discovered knowledge and future possibilities.

* 	  
  Structure 	and Nodes: The tree will consist of interconnected nodes, where each 	node represents a significant discovery. These can be specific 	substances (e.g., "Ammonia"), classes of substances (e.g., 	"Alcohols"), or new processes and equipment (e.g., 	"Electrolysis Apparatus"). When a player first discovers a 	corresponding item, its node on the tree becomes unlocked and fully 	visible.  
* 	  
  Unlocking 	and Dependencies: Nodes are unlocked by successfully performing the 	relevant synthesis or experiment in the main game interface. The 	connections between nodes represent scientific and logical 	dependencies. For example, the node for "Sulfuric Acid" 	($H\_2SO\_4$) cannot be unlocked until the player has first discovered 	its precursor, "Sulfur Trioxide" ($SO\_3$). Similarly, the 	"Electrolysis" process node will be dependent on the prior 	discovery of both "Water" ($H\_2O$) and a source of 	"Electricity."  
* 	  
  Function 	as a Guide: The Technology Tree is more than just a record of 	achievements; it is a dynamic guide for future experimentation. A 	player can view the tree and see locked nodes for substances they 	wish to create. By examining the visible prerequisite nodes leading 	to a locked target, the player can deduce the necessary ingredients 	or processes they need to discover first. For instance, seeing that 	"Iron," "Hydrogen," "Nitrogen," and 	"High Pressure Reactor" are all prerequisites for the 	locked "Haber-Bosch Process" node provides strong clues 	about the necessary components for that synthesis, encouraging 	targeted experimentation rather than random guessing.

This structure transforms the Technology Tree into a powerful pedagogical tool. Its very shape and the branching paths of its dependencies visually represent the interconnectedness of chemical knowledge. Players will implicitly learn that major industrial breakthroughs are not isolated events but are the culmination of many different lines of foundational research. This allows a player to pose a question like, "How is soap made?" and trace the dependencies backward through the tree—from soap to fats/oils and lye, and from lye to sodium hydroxide—creating a self-directed learning path that directly addresses the goal of guiding players toward what they are aiming for.

### **Milestone Unlocks: Gating Complexity**

To ensure a smooth learning curve and prevent players from being overwhelmed by too many options, a parallel progression system will automatically unlock new core Processes based on the total number of unique discoveries made. This system gates complexity, ensuring that the player's experimental toolkit expands in lockstep with their growing knowledge base.

* 	  
  Mechanism: 	The game will maintain a simple counter for the number of unique 	ingredients and reactions the player has discovered. When this 	counter reaches predefined thresholds, a new piece of equipment, 	representing a new fundamental process, is automatically awarded to 	the player.  
* 	  
  Example 	Progression:  
* 	  
  Start: 	The player begins with the most basic processes: Mix, Heat, and 	Cool.  
* 	  
  150 	Discoveries: The player is awarded the "Electrolysis 	Apparatus," permanently adding the Electrolysis process to 	their toolbar. This major unlock opens up the entire field of 	electrochemistry, allowing the decomposition of stable compounds 	like water ($2H\_2O \\rightarrow 2H\_2 \+ O\_2$) and molten salt ($2NaCl 	\\rightarrow 2Na \+ Cl\_2$).  
* 	  
  400 	Discoveries: The player unlocks the "Blast Furnace," 	granting them the Smelting (or High Temperature) process. This is 	the key to metallurgy, enabling the extraction of metals from their 	ores (e.g., iron from iron oxide).  
* 	  
  750 	Discoveries: The player unlocks the "High-Pressure Reactor," 	granting the Pressurize process. This is a critical piece of 	late-game equipment, essential for industrial syntheses like the 	Haber-Bosch process that require high atmospheric pressures.

This milestone system serves as the primary pacing mechanism of the game. It breaks the vast field of chemistry into manageable chapters, each centered around the exploration of a new core capability. It ensures that players have a solid grasp of basic synthesis and decomposition before they are introduced to electrolysis, and that they understand basic compound chemistry before they tackle the complexities of industrial-scale reactions.

### **Balancing Guidance and Experimentation**

The combination of the Technology Tree and the Milestone Unlock system creates a balanced learning environment. The Milestone system provides a structured, linear path of increasing mechanical complexity, ensuring the player is never overwhelmed. The Technology Tree, in contrast, offers a non-linear web of possibilities, encouraging player-driven goals and targeted exploration. The game will not provide explicit recipes by default. The primary mode of discovery remains hands-on experimentation. The guidance systems are designed to make that experimentation more educated and less random, empowering the player to make logical inferences based on their accumulated knowledge and the clues provided by the game's structure.

## **A Universe of Reactions: Content Framework and Chemical Accuracy**

The core of Chem-Alchemy is its extensive and scientifically accurate database of chemical reactions. This content is structured into progressive tiers, aligning with the player's journey from novice to expert. Each tier introduces new elements, new classes of compounds, and new types of reactions, creating a scaffolded curriculum that builds upon previously learned concepts.

### **Tier 1: Foundational Chemistry (Discoveries 1-100)**

This initial tier serves as the game's tutorial, introducing the most fundamental concepts of chemistry in an accessible way.

* 	  
  Focus: 	The primary educational goals of this tier are to teach the concepts 	of elements as building blocks, the formation of simple compounds 	through synthesis reactions ($A \+ B \\rightarrow AB$), the breaking 	of compounds through decomposition reactions ($AB \\rightarrow A \+ 	B$), and the physical concept of states of matter.12  
* 	  
  Starting 	Ingredients: The player begins with a curated list of the most 	common and reactive elements, ensuring early success and rapid 	discovery. This list includes: Hydrogen (H), Helium (He), Carbon 	(C), Nitrogen (N), Oxygen (O), Sodium (Na), and Chlorine (Cl).9  
* 	  
  Starting 	Processes: Mix, Heat, Cool.  
* 	  
  Example 	Discoveries:  
* 	  
  Synthesis 	of Water: $2H\_2 \+ O\_2 \\xrightarrow{Mix} 2H\_2O$  
* 	  
  Synthesis 	of Table Salt: $2Na \+ Cl\_2 \\xrightarrow{Mix} 2NaCl$  
* 	  
  Synthesis 	of Carbon Dioxide: $C \+ O\_2 \\xrightarrow{Heat} CO\_2$  
* 	  
  State 	Change (Vaporization): $H\_2O (liquid) \\xrightarrow{Heat} H\_2O (gas)$ 	(Product: Steam)  
* 	  
  State 	Change (Fusion): $H\_2O (liquid) \\xrightarrow{Cool} H\_2O (solid)$ 	(Product: Ice)  
* 	  
  Decomposition 	of Calcium Carbonate: $CaCO\_3 \\xrightarrow{Heat} CaO \+ CO\_2$ (This 	reaction would be discoverable after Calcium and Carbonate are 	found).14

### **Tier 2: Intermediate Chemistry (Discoveries 101-500)**

After mastering the basics, the player moves into a more complex chemical landscape, exploring new reaction types and a wider range of elements.

* 	  
  Focus: 	This tier introduces single displacement ($A \+ BC \\rightarrow AC \+ 	B$) and double displacement ($AB \+ CD \\rightarrow AD \+ CB$) 	reactions, the concepts of acids and bases, and the formation of 	simple organic molecules.15  
* 	  
  Unlocked 	Ingredients: The periodic table expands to include Sulfur (S), 	Phosphorus (P), Potassium (K), Calcium (Ca), Iron (Fe), Copper (Cu), 	and Zinc (Zn), among others.9  
* 	  
  Unlocked 	Processes: Electrolysis, Combustion.  
* 	  
  Example 	Discoveries:  
* 	  
  Acid-Base 	Chemistry: The synthesis of a strong acid like Sulfuric Acid ($SO\_3 	\+ H\_2O \\rightarrow H\_2SO\_4$) and a strong base like Sodium Hydroxide 	($2Na \+ 2H\_2O \\rightarrow 2NaOH \+ H\_2$).  
* 	  
  Single 	Displacement Reaction: The classic reaction of a metal with an acid: 	$Zn(s) \+ 2HCl(aq) \\rightarrow ZnCl\_2(aq) \+ H\_2(g)$.15  
* 	  
  Double 	Displacement (Precipitation): The formation of an insoluble salt 	from two soluble ones: $AgNO\_3(aq) \+ NaCl(aq) \\rightarrow AgCl(s) \+ 	NaNO\_3(aq)$.16  
* 	  
  Baking 	Soda Volcano: A fun and iconic reaction demonstrating acid-base 	chemistry and gas production: $NaHCO\_3 \+ CH\_3COOH \\rightarrow 	CH\_3COONa \+ H\_2O \+ CO\_2$.14  
* 	  
  Simple 	Organic Molecules: The formation of the first alkanes, such as 	Methane ($CH\_4$) and Ethane ($C\_2H\_6$), and simple alcohols like 	Methanol ($CH\_3OH$).

### **Tier 3: Organic & Industrial Primer (Discoveries 501-1000)**

This tier serves as a bridge to the game's endgame, deepening the player's understanding of organic chemistry and introducing the key components and precursors for large-scale industrial processes.

* 	  
  Focus: 	Exploring fundamental organic reactions like esterification and 	introducing the concepts of metallurgy and chemical feedstock 	production.20  
* 	  
  Unlocked 	Ingredients: Players will discover more complex organic molecules 	(e.g., acetic acid, ethanol), common metal ores (e.g., Bauxite 	$Al\_2O\_3$, Pyrite $FeS\_2$), and key catalysts.  
* 	  
  Unlocked 	Processes: Smelting (High Heat), Distillation, Catalysis.  
* 	  
  Example 	Discoveries:  
* 	  
  Esterification: 	The reaction of a carboxylic acid and an alcohol to form an ester, 	which are often responsible for fruity smells: $CH\_3COOH 	(Acetic\\;Acid) \+ CH\_3CH\_2OH (Ethanol) \\rightleftharpoons 	CH\_3COOCH\_2CH\_3 (Ethyl\\;Acetate) \+ H\_2O$.20  
* 	  
  Smelting 	of Iron: The reduction of iron ore in a blast furnace: $2Fe\_2O\_3 \+ 	3C \\xrightarrow{High\\;Heat} 4Fe \+ 3CO\_2$.4  
* 	  
  Hydrogen 	Production (Steam Reforming): A crucial first step for many 	industrial processes, particularly ammonia synthesis: $CH\_4 \+ H\_2O 	\\xrightarrow\[Ni\\;catalyst\]{Heat} CO \+ 3H\_2$.22

### **Tier 4: Industrial Synthesis (1000 – 10,000+ Capstone "Projects")**

The pinnacle of the player's journey involves recreating some of the most important chemical engineering achievements in history. These are presented as multi-step, guided "quests" that require the application of knowledge and processes from all previous tiers. This stage moves beyond simple success/failure to introduce concepts of optimization. For these processes, a "Yield Meter" could be introduced. Using the correct conditions (temperature, pressure, catalyst) results in a realistic yield, teaching the player about chemical equilibrium and the economic necessity of techniques like recycling unreacted gases. Furthermore, failing to use purified reactants could lead to "catalyst poisoning," a negative status effect that reduces efficiency until the catalyst is regenerated, teaching a real-world engineering challenge.24

Case Study 1: The Haber-Bosch Process (Ammonia Synthesis)

This process is arguably one of the most significant inventions of the 20th century, enabling the mass production of fertilizers and feeding billions.26

* 	  
  Objective: 	Produce Ammonia ($NH\_3$).  
* 	  
  Detailed 	Steps: The process is broken down into a clear, sequential 	questline.8

| 			Step \# 		 | 			Action/Goal 		 | 			Required Ingredients 		 | 			Required Process/Equipment 		 | 			Chemical Reaction 		 | 			In-Game Outcome 		 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| 			1 		 | 			Produce Hydrogen Feedstock 		 | 			Methane ($CH\_4$), Water 			($H\_2O$) 		 | 			"Reformer" (Heat, 			Ni Catalyst) 		 | 			$CH\_4 \+ H\_2O \\rightarrow CO 			\+ 3H\_2$ 		 | 			Hydrogen ($H\_2$) 		 |
| 			2 		 | 			Isolate Nitrogen 		 | 			Air 		 | 			"Air Separation Unit" 		 | 			(Simplified Separation) 		 | 			Nitrogen ($N\_2$) 		 |
| 			3 		 | 			Synthesize Ammonia 		 | 			Nitrogen ($N\_2$), Hydrogen 			($H\_2$) (1:3 ratio) 		 | 			"Haber Reactor" 			(High Pressure, High Temperature, Fe Catalyst) 		 | 			$N\_2(g) \+ 3H\_2(g) 			\\rightleftharpoons 2NH\_3(g)$ 		 | 			Mixture of $NH\_3$, $N\_2$, 			$H\_2$ 		 |
| 			4 		 | 			Separate Product 		 | 			Mixture from Step 3 		 | 			"Condenser" (Cool) 		 | 			(Physical Separation) 		 | 			Liquid Ammonia ($NH\_3$), 			unreacted $N\_2, H\_2$ 		 |
| 			5 		 | 			Increase Efficiency 		 | 			Unreacted $N\_2, H\_2$ 		 | 			"Recycling Pump" 		 | 			(Process Loop) 		 | 			Gases returned to Step 3 		 |

Case Study 2: The Contact Process (Sulfuric Acid Production)

This process is the primary method for producing sulfuric acid, a cornerstone chemical of the industrial world.24

* 	  
  Objective: 	Produce Sulfuric Acid ($H\_2SO\_4$).  
* 	  
  Detailed 	Steps: This quest emphasizes the importance of intermediate steps 	and safety, as direct hydration of $SO\_3$ is dangerously 	explosive.24

Case Study 3: Saponification (Soap Making)

This process introduces players to biochemistry and the origins of common household products.33

* 	  
  Objective: 	Produce Soap.  
* 	  
  Detailed 	Steps: This process involves the hydrolysis of fats (triglycerides) 	using a strong base.35

---

## **A Wider World of Chemistry: Advanced Topics**

To provide the requested depth and breadth, the game will extend beyond foundational and industrial chemistry into more specialized and advanced fields. These topics will be introduced as new branches of the Technology Tree, each unlocking unique ingredients and processes that open up new avenues for discovery.

### **Electrochemistry: The Power of Ions**

Beyond the simple decomposition of water, this branch allows players to explore the principles of galvanic cells and electroplating.

* 	  
  New 	Process: Apply Current.  
* 	  
  New 	Mechanics: Players can construct a galvanic cell (a battery) by 	combining two different metals and an electrolyte on the Reaction 	Canvas. This creates a "Charged Battery" item. This item 	can then be used as a required component for the Electrolysis 	process, creating a satisfying and scientifically sound gameplay 	loop where players must first generate electrical potential to use 	it.  
* 	  
  Example 	Discoveries:  
* 	  
  Daniell 	Cell: Zinc \+ Copper \+ Sulfate Solution → Charged Battery  
* 	  
  Electroplating: 	Copper \+ Charged Battery \+ Apply Current → Copper-Plated Object

### **Photochemistry: Reactions Driven by Light**

This branch introduces reactions that are initiated by light energy, adding a visually interesting and conceptually distinct set of puzzles.57

* 	  
  New 	Process: Irradiate (represented by a sun or UV lamp icon).  
* 	  
  Mechanics: 	Applying the Irradiate process to certain compounds will trigger a 	transformation. This can be used to model everything from color 	changes to the synthesis of new materials.  
* 	  
  Example 	Discoveries:  
* 	  
  Photochromism: 	A simple, visually rewarding reaction where a substance changes 	color under light. For example: Spiropyrane (colorless) \+ Irradiate 	→ Merocyanine (colored).58 The product could then revert to its 	original form with the Cool or Wait process, demonstrating 	reversibility.  
* 	  
  Vitamin 	D Synthesis: A simplified biochemical reaction: 7-dehydrocholesterol 	\+ Irradiate → Vitamin D3.

### **Polymer Chemistry: Building the Chains of Modern Life**

This advanced topic introduces the concept of creating long-chain molecules (polymers) from smaller building blocks (monomers).

* 	  
  New 	Ingredient Class: Monomers (e.g., Styrene, Ethylene).  
* 	  
  New 	Process: Polymerize.  
* 	  
  Mechanics: 	The core mechanic involves combining one or more types of monomers 	with a catalyst and applying the Polymerize process. The game can 	visually represent this by showing the individual monomer icons 	linking together to form a long, chain-like icon for the resulting 	polymer.59 The process can be simplified into three conceptual 	stages: Initiation (activating the first monomer), Growth (chaining 	them together), and Termination (ending the reaction).60  
* 	  
  Example 	Discoveries:  
* 	  
  Polystyrene: 	Styrene (Monomer) \+ Catalyst \+ Polymerize → Polystyrene  
* 	  
  Teflon 	(PTFE): The accidental discovery of Teflon can be recreated. The 	player might try to store the Tetrafluoroethylene gas, and after 	applying pressure or a catalyst, it spontaneously polymerizes into 	the inert, waxy solid PTFE.61

### **Radiochemistry: The Science of Unstable Nuclei**

This branch introduces the fascinating and counter-intuitive world of radioactive decay, modeled as a probabilistic process.

* 	  
  New 	Property: Radioactive. Certain elements (e.g., Uranium, Radium) will 	have this property.  
* 	  
  New 	Process: Wait (or Observe over Time).  
* 	  
  Mechanics: 	Radioactive decay is a random process.63 This can be simulated 	in-game using a chance-based mechanic. When the player applies the 	Wait process to a radioactive element, there is a certain 	probability that it will decay into its daughter isotope. This can 	be visualized as a "dice roll" or "coin flip" 	occurring behind the scenes, a common and effective method for 	teaching the concept of half-life.63  
* 	  
  Example 	Discoveries:  
* 	  
  Alpha 	Decay of Uranium-238: Uranium-238 \+ Wait → (Chance of) Thorium-234 	\+ Alpha Particle  
* 	  
  Decay 	Chains: Players could discover that the product of one decay (e.g., 	Thorium-234) is itself radioactive, leading them to uncover entire 	decay chains by repeatedly applying the Wait process.

## **Guiding the Modern Alchemist: Motivation and Support Systems**

To create a compelling educational game, it is not enough to simply present accurate content. The design must actively manage player motivation, providing encouragement through challenges and offering support to prevent frustration. This is achieved through a carefully designed system of achievements and a novel, economy-based hint system that reframes "getting help" as an act of "research."

### **Achievements as Milestones: The Badge System**

A robust achievement system, centered on earning collectible badges, provides players with clear goals and tangible recognition for their progress. This system leverages gamification principles to enhance motivation, track learning, and build player confidence.38

* 	  
  Purpose 	and Motivation: Badges serve as a powerful form of positive 	reinforcement. By offering a visual acknowledgment of success, they 	provide a sense of accomplishment that inspires continued 	engagement. Earning a badge activates the brain's reward centers, 	encouraging players to repeat the behaviors that led to the 	achievement.38  
* 	  
  Badge 	Categories: To reward various aspects of gameplay and learning, 	badges will be organized into several categories:  
* 	  
  Discovery 	Milestones: These badges are awarded for reaching quantitative 	milestones in the number of unique substances discovered. Examples 	include "Junior Chemist" (10 discoveries), "Graduate 	Researcher" (50 discoveries), and "Nobel Laureate" 	(all discoveries).  
* 	  
  Conceptual 	Mastery: These badges recognize a player's understanding and 	application of specific chemical principles. For example, the 	"Synthesizer" badge could be awarded for performing 10 	different synthesis reactions, while the "Precipitator" 	badge is earned by successfully executing 5 different precipitation 	reactions.  
* 	  
  Process 	Unlocks: A unique badge will be awarded each time the player unlocks 	a major new process through the milestone system (e.g., "Master 	of Electrolysis," "Furnace Operator").  
* 	  
  Industrial 	Triumphs: The most prestigious badges are reserved for the 	successful completion of the capstone industrial synthesis quests. 	These might be designed to look like historical medals, such as "The 	Haber-Bosch Medal" or "The Phillips Medallion" (for 	the Contact Process), connecting the player's in-game achievement to 	real-world scientific history.24  
* 	  
  Visual 	Design: The design of the badges themselves is critical to their 	desirability. Each badge will be a unique, visually appealing icon 	relevant to the achievement. They might incorporate imagery from 	chemistry, such as molecular structures, laboratory equipment, or 	stylized elemental symbols, and use metallic sheens like bronze, 	silver, and gold to denote tiers of achievement.38

### **The Economy of Knowledge: Discovery Points (DP)**

Traditional hint buttons in educational games can be problematic. Research indicates they can carry a negative stigma, with players viewing their use as a form of failure, which can lead to avoidance even when stuck. Paradoxically, if hints are too freely available, they can be abused, negatively impacting actual learning and performance.41 To circumvent these issues, Chem-Alchemy will implement an in-game economy centered on a currency called Discovery Points (DP).

* 	  
  Earning 	Discovery Points: Players earn DP through the core gameplay loop. A 	small number of points are awarded for every new substance 	discovered. Larger lump-sum bonuses are granted upon earning an 	achievement badge. This directly links the ability to gain knowledge 	(spending DP) to the act of creating knowledge (making discoveries).  
* 	  
  Spending 	Discovery Points: DP can be spent in a section of the UI themed as 	the "University Library" or "Research Department." 	This reframes the act of getting help as a strategic decision to 	"conduct research." Players can spend their DP on several 	tiers of assistance:  
1. 	  
   Purchase 	Tiered Hints: Instead of a single button that reveals the answer, 	players can purchase progressively more explicit clues for a 	specific target substance.  
* 	  
  Tier 1 	Hint (Low DP Cost): A vague conceptual clue. (e.g., for Ammonia: 	"This vital compound is synthesized from the two most abundant 	gases in our atmosphere.")  
* 	  
  Tier 2 	Hint (Medium DP Cost): A more direct clue about reactants or 	process. (e.g., "Ammonia synthesis requires reacting Nitrogen 	and Hydrogen under extreme conditions.")  
* 	  
  Tier 3 	Hint (High DP Cost): The full, explicit recipe and conditions.  
2. 	  
   Reveal 	Technology Tree Paths: A player can spend DP to reveal the 	immediate, undiscovered prerequisites for a locked node on the 	Technology Tree, helping them focus their experimentation.  
3. 	  
   Unlock 	"Research Papers": Access to the guided, multi-step quests 	for the Tier 4 industrial processes is not automatic. The player 	must spend a significant amount of DP to "fund the research," 	which unlocks the step-by-step objectives for that process.

### **Avoiding the "Hint Button" Stigma**

This economy-based system is designed to fundamentally alter the psychology of seeking help. By transforming hints into a resource that is earned through achievement and spent strategically, the game aligns with successful models seen in commercial games like Professor Layton.42 It is no longer an admission of failure but a calculated investment of earned resources. This creates a meaningful choice for the player: "Should I spend my DP to get the answer for this one reaction, or should I persist and save them to unlock the entire Haber-Bosch project?"

This design creates a positive feedback loop. It incentivizes players to experiment and solve problems on their own to conserve their valuable DP. When they do choose to spend points, the act feels empowering and strategic, not remedial. The very terminology used in the UI will reinforce this, using words like "Research" and "Consult" instead of "Hint," a technique shown to reverse the negative connotations associated with help systems.42 This creates a robust support structure that guides players without undermining their sense of accomplishment or intrinsic motivation.

## **Implementation Blueprint: Data Structures and Bevy Architecture**

This section provides a high-level technical blueprint for developing Chem-Alchemy, focusing on the implementation details within the Rust programming language and the Bevy game engine. The design leverages Rust's strong type system for data integrity and Bevy's Entity-Component-System (ECS) architecture for a flexible and performant simulation.

### **Core Data Structures in Rust**

Rust's emphasis on type safety and data-oriented design makes it an excellent choice for modeling a rule-based system like chemistry. The core data of the game will be represented using structs and enums to ensure that all chemical entities are well-defined and their properties are explicit.44

Ingredient Data Structure: This struct will define a single chemical substance.

Rust

// Represents a unique chemical substance, like Water or Sodium Chloride.  
 \#\[derive(Component, Clone, PartialEq, Eq, Hash)\]  
 pub struct Ingredient {  
     pub id: u32, // A unique identifier for this ingredient type  
     pub name: String,  
     pub formula: String,  
     pub state: MatterState,  
     pub properties: Vec\<Property\>,  
 }

 \#\[derive(Clone, PartialEq, Eq, Hash)\]  
 pub enum MatterState {  
     Solid,  
     Liquid,  
     Gas,  
 }

 // Defines specific chemical characteristics or roles.  
 \#\[derive(Clone, PartialEq, Eq, Hash)\]  
 pub enum Property {  
     IsAcid,  
     IsBase,  
     IsMetal,  
     IsCatalystFor(u32), // The ID of the Reaction this catalyzes  
 }

Reaction Data Structure: This struct will define a single valid "recipe" in the game.

Rust

// Represents a single chemical reaction recipe.  
 pub struct Reaction {  
     pub id: u32, // A unique identifier for this reaction  
     pub reactants: Vec\<(u32, u32)\>, // Vec of (Ingredient ID, stoichiometric coefficient)  
     pub products: Vec\<(u32, u32)\>,  
     pub process: ProcessType,  
     pub conditions: Vec\<Condition\>, // Optional specific conditions like temperature  
 }

 \#\[derive(PartialEq, Eq, Hash)\]  
 pub enum ProcessType {  
     Mix,  
     Heat,  
     Cool,  
     Electrolysis,  
     Catalysis,  
     HighPressure,  
 }

 pub enum Condition {  
     Temperature(f32), // In degrees Celsius  
     Pressure(f32),    // In atmospheres  
 }

Recipe Storage and Lookup: The full set of all possible Reaction structs will form the game's "recipe book." For efficient gameplay, a fast lookup mechanism is required. A HashMap is a suitable data structure for this purpose. The key for the map could be a composite struct that includes a sorted list of reactant IDs and the applied ProcessType. This allows the reaction\_check\_system to quickly determine if a valid reaction exists for the current contents of the Reaction Vessel.45

### **Leveraging the Bevy Engine (ECS)**

Bevy's data-driven ECS architecture is not merely a performance optimization; its paradigm of composing entities from components is a near-perfect conceptual match for the compositional nature of chemistry.47

* 	  
  Entities: 	Every discrete object in the game world will be an Entity. This 	includes the ingredient icons in the inventory, the ingredients 	currently in the Reaction Vessel, and all UI elements like buttons 	and panels.  
* 	  
  Components: 	The properties and state of each entity are defined by the 	Components attached to it.  
* 	  
  An 	Ingredient component (as defined above) will be attached to entities 	representing chemical substances.  
* 	  
  Standard 	Bevy components like Style, BackgroundColor, and UiImage will 	control the visual appearance of entities.  
* 	  
  Custom 	marker components like InInventory or OnReactionCanvas will be used 	to tag entities, allowing systems to easily query for them (e.g., 	"find all entities with the OnReactionCanvas component").  
* 	  
  Interaction 	components, such as those from bevy\_mod\_picking or a custom 	solution, will manage drag-and-drop state.  
* 	  
  Systems: 	The game's logic is implemented as Systems—Rust functions that run 	each frame and query for entities with specific combinations of 	components.  
* 	  
  A 	drag\_and\_drop\_system will handle user input, moving ingredient 	entities between the inventory and the reaction canvas. This system 	would modify marker components (e.g., removing InInventory and 	adding OnReactionCanvas) and update the entity's Style component to 	change its position on screen.49  
* 	  
  A 	central reaction\_check\_system will be triggered whenever a process 	is applied. This system will query for all entities with the 	OnReactionCanvas component, collect their Ingredient data, and 	perform a lookup against the recipe HashMap. If a match is found, it 	will despawn the reactant entities, spawn new entities for the 	products, and send a DiscoveryEvent to notify other systems.  
* 	  
  A 	discovery\_event\_handler\_system will listen for DiscoveryEvents. When 	one is received, it will update the player's progression data, add 	the new ingredient to the permanent list of discoverable items, and 	trigger UI animations to celebrate the discovery.

This ECS structure provides immense flexibility. Adding a new chemical property, like radioactivity, is as simple as defining a new Radioactive component. Adding a new class of reactions, like photochemistry, involves writing a new photochemical\_reaction\_system that queries for reactants and a "Light" process trigger. This deep structural alignment between Bevy's architecture and the domain of chemistry will make the codebase more intuitive, robust, and extensible.

### **UI Implementation**

The user interface is a critical component for a drag-and-drop focused game. Bevy offers a flexible foundation for building the UI directly within its ECS.

* 	  
  Native 	Bevy UI: Bevy's built-in UI framework uses the same ECS principles. 	UI elements are entities with NodeBundles, and their layout is 	controlled via Style components that implement a subset of the CSS 	Flexbox model.47 This approach is powerful because it seamlessly 	integrates the UI with the rest of the game's state. For example, 	the inventory panel can be a system that queries the player's 	discovered ingredients and dynamically spawns a child UI entity for 	each one. This is the recommended approach for the core game 	interface, as it keeps the entire application within a single, 	consistent data model. Bevy's official examples include a 	ui\_drag\_and\_drop demonstration that provides a strong starting point 	for implementing the core mechanic.49  
* 	  
  bevy\_egui 	Integration: For more complex or data-heavy UI elements, such as the 	Technology Tree view or the "University Library," 	integrating the bevy\_egui crate is a highly effective strategy.52 	egui is an immediate-mode GUI library that is very popular in the 	Rust ecosystem for its ease of use and flexibility. It can be 	rendered as an overlay on top of the Bevy application, making it 	ideal for creating complex, interactive windows and debugging tools 	without interfering with the main ECS-driven UI. The final 	application will likely use a hybrid approach: native Bevy UI for 	the core in-game elements (inventory, reaction vessel) and bevy\_egui 	for the more complex, menu-like screens.

By combining Rust's robust data modeling with Bevy's powerful ECS, this technical blueprint provides a solid and scalable foundation for building Chem-Alchemy, ensuring the final product is as well-engineered as it is educational.

#### **Works cited**

1. 	  
   The 	science of fun: Little Alchemy's addictive gameplay explained ..., 	accessed November 2, 2025, 	[https://londonlovestech.com/the-science-of-fun-little-alchemys-addictive-gameplay-explained/](https://londonlovestech.com/the-science-of-fun-little-alchemys-addictive-gameplay-explained/)  
2. 	  
   Advanced 	Game Mechanics: Crafting Complex Gameplay Systems \- LearningMole, 	accessed November 2, 2025, 	[https://learningmole.com/advanced-game-mechanics/](https://learningmole.com/advanced-game-mechanics/)  
3. 	  
   How to 	Design Learning Games for Kids That Teach Real-World Skills \- 	Game-Ace, accessed November 2, 2025, 	[https://game-ace.com/blog/how-to-design-learning-games/](https://game-ace.com/blog/how-to-design-learning-games/)  
4. 	  
   Industrial 	processes \- Wikipedia, accessed November 2, 2025, 	[https://en.wikipedia.org/wiki/Industrial\_processes](https://en.wikipedia.org/wiki/Industrial_processes)  
5. 	  
   List of 	important Chemical Processes, accessed November 2, 2025, 	[https://www.jagranjosh.com/general-knowledge/list-of-important-chemical-processes-1513680339-1](https://www.jagranjosh.com/general-knowledge/list-of-important-chemical-processes-1513680339-1)  
6. 	  
   Video 	Game Mechanics: A Beginner's Guide (with Examples) \- Game Design 	Skills, accessed November 2, 2025, 	[https://gamedesignskills.com/game-design/video-game-mechanics/](https://gamedesignskills.com/game-design/video-game-mechanics/)  
7. 	  
   Little 	Alchemy Elements Combinations & Cheats | Full List of Elements 	for Little Alchemy, accessed November 2, 2025, 	[https://littlealchemycheats.wordpress.com/](https://littlealchemycheats.wordpress.com/)  
8. 	  
   Haber-Bosch 	process | Research Starters | EBSCO Research, accessed November 2, 	2025, 	[https://www.ebsco.com/research-starters/earth-and-atmospheric-sciences/haber-bosch-process](https://www.ebsco.com/research-starters/earth-and-atmospheric-sciences/haber-bosch-process)  
9. 	  
   First 	20 Elements of Periodic Table: Names, Symbols & Numbers, 	accessed November 2, 2025, 	[https://www.vedantu.com/chemistry/first-20-elements-of-periodic-table](https://www.vedantu.com/chemistry/first-20-elements-of-periodic-table)  
10. 	  
    The 	essential elements \- Science Learning Hub, accessed November 2, 	2025, 	[https://www.sciencelearn.org.nz/resources/1728-the-essential-elements](https://www.sciencelearn.org.nz/resources/1728-the-essential-elements)  
11. 	  
    Technology 	Trees and Tools: Constructing Development Graphs for Digital Games \- 	Tampere University Research Portal, accessed November 2, 2025, 	[https://researchportal.tuni.fi/files/4265122/heinimaki\_1349.pdf](https://researchportal.tuni.fi/files/4265122/heinimaki_1349.pdf)  
12. 	  
    Types 	of Chemical Reactions: Synthesis and Decomposition, accessed 	November 2, 2025, 	[https://www.elephango.com/index.cfm/pg/k12learning/lcid/12908/Types\_of\_Chemical\_Reactions:\_Synthesis\_and\_Decomposition](https://www.elephango.com/index.cfm/pg/k12learning/lcid/12908/Types_of_Chemical_Reactions:_Synthesis_and_Decomposition)  
13. 	  
    Decomposition 	& Synthesis Reactions | Chemistry Tutorial at The Physics 	Classroom, accessed November 2, 2025, 	[https://www.physicsclassroom.com/Chemistry-Tutorial/Chemical-Reactions/Decomposition-and-Synthesis-Reactions](https://www.physicsclassroom.com/Chemistry-Tutorial/Chemical-Reactions/Decomposition-and-Synthesis-Reactions)  
14. 	  
    TOP 10 	chemical reactions that you can repeat at home | MEL ..., accessed 	November 2, 2025, 	[https://melscience.com/US-en/articles/top-10-chemical-reactions-you-can-repeat-home/](https://melscience.com/US-en/articles/top-10-chemical-reactions-you-can-repeat-home/)  
15. 	  
    Displacement 	Reactions | Research Starters \- EBSCO, accessed November 2, 2025, 	[https://www.ebsco.com/research-starters/chemistry/displacement-reactions](https://www.ebsco.com/research-starters/chemistry/displacement-reactions)  
16. 	  
    Double 	replacement reactions (double displacement) (article) | Khan 	Academy, accessed November 2, 2025, 	[https://www.khanacademy.org/science/hs-chemistry/x2613d8165d88df5e:solutions-acids-and-bases/x2613d8165d88df5e:solubility/a/double-replacement-reactions](https://www.khanacademy.org/science/hs-chemistry/x2613d8165d88df5e:solutions-acids-and-bases/x2613d8165d88df5e:solubility/a/double-replacement-reactions)  
17. 	  
    Common 	Elements, accessed November 2, 2025, 	[https://preparatorychemistry.com/Common\_Elements.htm](https://preparatorychemistry.com/Common_Elements.htm)  
18. 	  
    4.3 	Classes of Chemical Reactions: Single and Double Displacement 	Reactions \- RMIT Open Press, accessed November 2, 2025, 	[https://rmit.pressbooks.pub/rmitchemistrybridgingcourse/chapter/types-of-chemical-reactions-single-and-double-displacement-reactions/](https://rmit.pressbooks.pub/rmitchemistrybridgingcourse/chapter/types-of-chemical-reactions-single-and-double-displacement-reactions/)  
19. 	  
    www.polygence.org, 	accessed November 2, 2025, 	[https://www.polygence.org/blog/chemistry-experiments-for-kids\#:\~:text=Explanation%3A%20When%20vinegar%20is%20added,look%20like%20lava%20flowing%20down.](https://www.polygence.org/blog/chemistry-experiments-for-kids#:~:text=Explanation%3A%20When%20vinegar%20is%20added,look%20like%20lava%20flowing%20down.)  
20. 	  
    Organic 	reaction \- Wikipedia, accessed November 2, 2025, 	[https://en.wikipedia.org/wiki/Organic\_reaction](https://en.wikipedia.org/wiki/Organic_reaction)  
21. 	  
    6.1 	Kinds of Organic Reactions \- Organic Chemistry | OpenStax, accessed 	November 2, 2025, 	[https://openstax.org/books/organic-chemistry/pages/6-1-kinds-of-organic-reactions](https://openstax.org/books/organic-chemistry/pages/6-1-kinds-of-organic-reactions)  
22. 	  
    Making 	ammonia \- the Haber process \- Creative Chemistry, accessed November 	2, 2025, 	[https://www.creative-chemistry.org.uk/documents/N-m07-03.pdf](https://www.creative-chemistry.org.uk/documents/N-m07-03.pdf)  
23. 	  
    Haber 	process \- BYJU'S, accessed November 2, 2025, 	[https://byjus.com/chemistry/haber-process/](https://byjus.com/chemistry/haber-process/)  
24. 	  
    Contact 	process \- Wikipedia, accessed November 2, 2025, 	[https://en.wikipedia.org/wiki/Contact\_process](https://en.wikipedia.org/wiki/Contact_process)  
25. 	  
    Explain 	contact process for the manufacturing of sulphuric acid. \- Steps & 	Properties \- CK-12, accessed November 2, 2025, 	[https://www.ck12.org/flexi/cbse-science/compounds-of-sulphur/explain-contact-process-for-the-manufacturing-of-sulphuric-acid/](https://www.ck12.org/flexi/cbse-science/compounds-of-sulphur/explain-contact-process-for-the-manufacturing-of-sulphuric-acid/)  
26. 	  
    www.britannica.com, 	accessed November 2, 2025, 	[https://www.britannica.com/technology/Haber-Bosch-process\#:\~:text=Haber%2DBosch%20process%2C%20method%20of,manufacture%20of%20ammonia%20economically%20feasible.](https://www.britannica.com/technology/Haber-Bosch-process#:~:text=Haber-Bosch%20process%2C%20method%20of,manufacture%20of%20ammonia%20economically%20feasible.)  
27. 	  
    Haber-Bosch 	Process \- Stanford University, accessed November 2, 2025, 	[http://large.stanford.edu/courses/2022/ph240/jimenez2/](http://large.stanford.edu/courses/2022/ph240/jimenez2/)  
28. 	  
    Haber 	process \- Wikipedia, accessed November 2, 2025, 	[https://en.wikipedia.org/wiki/Haber\_process](https://en.wikipedia.org/wiki/Haber_process)  
29. 	  
    Haber's 	Process \- GeeksforGeeks, accessed November 2, 2025, 	[https://www.geeksforgeeks.org/chemistry/habers-process/](https://www.geeksforgeeks.org/chemistry/habers-process/)  
30. 	  
    Contact 	process | Reaction, Conditions, Types, & Facts \- Britannica, 	accessed November 2, 2025, 	[https://www.britannica.com/technology/contact-process](https://www.britannica.com/technology/contact-process)  
31. 	  
    The 	Contact Process | PDF | Sulfuric Acid | Chemical Elements \- Scribd, 	accessed November 2, 2025, 	[https://www.scribd.com/presentation/242631636/The-Contact-Process](https://www.scribd.com/presentation/242631636/The-Contact-Process)  
32. 	  
    The 	Contact Process \- Chemistry LibreTexts, accessed November 2, 2025, 	[https://chem.libretexts.org/Bookshelves/Physical\_and\_Theoretical\_Chemistry\_Textbook\_Maps/Supplemental\_Modules\_(Physical\_and\_Theoretical\_Chemistry)/Equilibria/Le\_Chateliers\_Principle/The\_Contact\_Process](https://chem.libretexts.org/Bookshelves/Physical_and_Theoretical_Chemistry_Textbook_Maps/Supplemental_Modules_\(Physical_and_Theoretical_Chemistry\)/Equilibria/Le_Chateliers_Principle/The_Contact_Process)  
33. 	  
    potagersoap.com, 	accessed November 2, 2025, 	[https://potagersoap.com/blogs/news/what-is-saponification\#:\~:text=Saponification%20is%20a%20process%20that,and%20the%20base%20are%20neutralized.](https://potagersoap.com/blogs/news/what-is-saponification#:~:text=Saponification%20is%20a%20process%20that,and%20the%20base%20are%20neutralized.)  
34. 	  
    What Is 	Saponification? | How Saponification Works | Potager ..., accessed 	November 2, 2025, 	[https://potagersoap.com/blogs/news/what-is-saponification](https://potagersoap.com/blogs/news/what-is-saponification)  
35. 	  
    The 	Magic of Saponification: How Soap is Made – Bearsville Soap ..., 	accessed November 2, 2025, 	[https://bearsvillesoaps.com/blogs/bearsville-soap-company-natural-soap-blog/the-magic-of-saponification-how-soap-is-made](https://bearsvillesoaps.com/blogs/bearsville-soap-company-natural-soap-blog/the-magic-of-saponification-how-soap-is-made)  
36. 	  
    Soap 	Lab, accessed November 2, 2025, 	[https://www.engineering.iastate.edu/brl/files/2011/10/brl\_soaplab.pdf](https://www.engineering.iastate.edu/brl/files/2011/10/brl_soaplab.pdf)  
37. 	  
    Saponification 	is the hydrolysis of an ester with NaOH or KOH to give alcohol and 	sodium or potassium salt of the acid. \- BYJU'S, accessed November 2, 	2025, [https://byjus.com/chemistry/saponification/](https://byjus.com/chemistry/saponification/)  
38. 	  
    Using 	Gamification Badges for Motivation and Learning \- Nudge, accessed 	November 2, 2025, 	[https://nudgenow.com/blogs/badges-for-gamification-motivation-learning](https://nudgenow.com/blogs/badges-for-gamification-motivation-learning)  
39. 	  
    Gamification 	Badges | TPT, accessed November 2, 2025, 	[https://www.teacherspayteachers.com/browse?search=gamification%20badges](https://www.teacherspayteachers.com/browse?search=gamification+badges)  
40. 	  
    Game 	Achievement Badges royalty-free images \- Shutterstock, accessed 	November 2, 2025, 	[https://www.shutterstock.com/search/game-achievement-badges](https://www.shutterstock.com/search/game-achievement-badges)  
41. 	  
    Hint 	systems may negatively impact performance in educational games, 	accessed November 2, 2025, 	[https://www.scholars.northwestern.edu/en/publications/hint-systems-may-negatively-impact-performance-in-educational-gam](https://www.scholars.northwestern.edu/en/publications/hint-systems-may-negatively-impact-performance-in-educational-gam)  
42. 	  
    Hint 	Systems May Negatively Impact Performance in Educational ..., 	accessed November 2, 2025, 	[https://grail.cs.washington.edu/wp-content/uploads/2015/08/orourke2014hsm.pdf](https://grail.cs.washington.edu/wp-content/uploads/2015/08/orourke2014hsm.pdf)  
43. 	  
    The 	Heart of Educational Game Design \- EdTech Digest, accessed November 	2, 2025, 	[https://edtechdigest.blog/2018/02/22/the-heart-of-educational-game-design/](https://edtechdigest.blog/2018/02/22/the-heart-of-educational-game-design/)  
44. 	  
    Ultimate 	Rust Game Development Guide 2024: From Beginner to Pro, accessed 	November 2, 2025, 	[https://www.rapidinnovation.io/post/rust-game-programming-technical-guide](https://www.rapidinnovation.io/post/rust-game-programming-technical-guide)  
45. 	  
    Exploring 	Data Structures in Rust: A Beginner's Guide | by Ruben Lazarus \- 	Medium, accessed November 2, 2025, 	[https://medium.com/@robssthe/exploring-data-structures-in-rust-a-beginners-guide-44fc9d03f019](https://medium.com/@robssthe/exploring-data-structures-in-rust-a-beginners-guide-44fc9d03f019)  
46. 	  
    Data 	structures — list of Rust libraries/crates // Lib.rs, accessed 	November 2, 2025, [https://lib.rs/data-structures](https://lib.rs/data-structures)  
47. 	  
    Bevy 	Engine, accessed November 2, 2025, [https://bevy.org/](https://bevy.org/)  
48. 	  
    Trait 	objects with data-oriented / ECS style? \- help \- Rust Users Forum, 	accessed November 2, 2025, 	[https://users.rust-lang.org/t/trait-objects-with-data-oriented-ecs-style/123675](https://users.rust-lang.org/t/trait-objects-with-data-oriented-ecs-style/123675)  
49. 	  
    UI Drag 	and Drop \- Bevy Engine, accessed November 3, 2025, 	[https://bevy.org/examples-webgpu/ui-user-interface/ui-drag-and-drop/](https://bevy.org/examples-webgpu/ui-user-interface/ui-drag-and-drop/)  
50. 	  
    cadyn/bevy\_dragndrop: 	A simple plugin for Bevy to allow dragging and dropping of 2D world 	objects or UI elements. \- GitHub, accessed November 2, 2025, 	[https://github.com/cadyn/bevy\_dragndrop](https://github.com/cadyn/bevy_dragndrop)  
51. 	  
    Bevy UI 	| Tainted Coders, accessed November 2, 2025, 	[https://taintedcoders.com/bevy/ui](https://taintedcoders.com/bevy/ui)  
52. 	  
    bevy\_egui 	\- Rust \- Docs.rs, accessed November 2, 2025, 	[https://docs.rs/bevy\_egui](https://docs.rs/bevy_egui)  
53. 	  
    Getting 	started with egui in Rust \- Ryosuke, accessed November 2, 2025, 	[https://whoisryosuke.com/blog/2023/getting-started-with-egui-in-rust](https://whoisryosuke.com/blog/2023/getting-started-with-egui-in-rust)  
54. 	  
    Little 	Alchemy, accessed November 2, 2025, [https://littlealchemy.com/](https://littlealchemy.com/)  
55. 	  
    What 	Works And Why: Optimising in Opus Magnum | Rock Paper Shotgun, 	accessed November 3, 2025, 	[https://www.rockpapershotgun.com/what-works-and-why-opus-magnum](https://www.rockpapershotgun.com/what-works-and-why-opus-magnum)  
56. 	  
    Opus 	Magnum Perfectly Fills Its Little Niche : r/patientgamers \- Reddit, 	accessed November 3, 2025, 	[https://www.reddit.com/r/patientgamers/comments/ocrh6z/opus\_magnum\_perfectly\_fills\_its\_little\_niche/](https://www.reddit.com/r/patientgamers/comments/ocrh6z/opus_magnum_perfectly_fills_its_little_niche/)  
57. 	  
    ChemChallenge: 	A Video Game for Teaching and Studying Thermodynamics Featuring 	In-game Currency, Shopping, Customization of Laboratory and 	Photochemistry | Chemical Education | ChemRxiv | Cambridge Open 	Engage, accessed November 3, 2025, 	[https://chemrxiv.org/engage/chemrxiv/article-details/683467e21a8f9bdab5f8f0bb](https://chemrxiv.org/engage/chemrxiv/article-details/683467e21a8f9bdab5f8f0bb)  
58. 	  
    Teaching 	Photochemistry with Microscale ... \- Revistas UNAM, accessed 	November 3, 2025, 	[https://revistas.unam.mx/index.php/req/article/download/66090/58002/192810](https://revistas.unam.mx/index.php/req/article/download/66090/58002/192810)  
59. 	  
    Introduction 	| Etomica, accessed November 3, 2025, 	[https://www.etomica.org/modules/polymerization/](https://www.etomica.org/modules/polymerization/)  
60. 	  
    Polymerization 	and polycondensation reactions | MEL Chemistry, accessed November 3, 	2025, 	[https://melscience.com/US-en/articles/polymerization-and-polycondensation-reactions/](https://melscience.com/US-en/articles/polymerization-and-polycondensation-reactions/)  
61. 	  
    Polytetrafluoroethylene 	\- Wikipedia, accessed November 3, 2025, 	[https://en.wikipedia.org/wiki/Polytetrafluoroethylene](https://en.wikipedia.org/wiki/Polytetrafluoroethylene)  
62. 	  
    The 	Long, Strange History of Teflon, the Indestructible Product ..., 	accessed November 3, 2025, 	[https://www.smithsonianmag.com/science-nature/the-long-strange-history-of-teflon-the-indestructible-product-nothing-seems-to-stick-to-180984920/](https://www.smithsonianmag.com/science-nature/the-long-strange-history-of-teflon-the-indestructible-product-nothing-seems-to-stick-to-180984920/)  
63. 	  
    Half-Life 	with Coins | STEM Activity \- Science Buddies, accessed November 3, 	2025, 	[https://www.sciencebuddies.org/stem-activities/radioactive-coins](https://www.sciencebuddies.org/stem-activities/radioactive-coins)  
64. 	  
    Radioactive 	Dating: Looking at Half-Lives Using M\&Ms \- SERC (Carleton), 	accessed November 3, 2025, 	[https://serc.carleton.edu/sp/mnstep/activities/34884.html](https://serc.carleton.edu/sp/mnstep/activities/34884.html)  
65. 	  
    Radioactive-Decay 	Model: Math and Chemistry Science Activity \- Exploratorium, accessed 	November 3, 2025, 	[https://www.exploratorium.edu/snacks/radioactive-decay-model](https://www.exploratorium.edu/snacks/radioactive-decay-model)

DEVELOPMENT PROGRESS NOTES

Got the first 5 steps done, up to and including being able to drag and drop incredients into the ‘reaction canvas’. We’re now on step 6, where we get our first actual reaction. Other steps included for posterity.

## **Next Steps (Steps 1 \- 6 Complete)**

Step 7:I like the idea of the processes being dragged and dropped like substances, but being containers themselves as well. So we’ll have a heating container, cooling container, electrolysis, mixing, etc etc, which would each have their own start reaction button. We could then hook them together to feed the product of one into the input for another and rework the execution phase to respect this order.

 Step 8: I fully agree with the idea, but I think rather than futzing with PNGs like we have been, we should simply use a Bohr Rutherford representation for elements, and chemical diagrams for compounds, even things as simple as water. Then the background can be any color attribute we want. I think this will make things extremely clean, and we can render these using established things like SMILES or their subsequent iterations (I think it was called SMARTS or something, makes them more expressive and less ambiguous). We should also probably more effectively organize the ingredients tab so users can find the elements or compounds more easily, with sorting based on name, composition, type or other data for ease of retrieval as the numbers balloon

 Step 9: I'm going to move the data phase to later for now and for 9 I'm going to say I would like to set up the 'window dressing' of the game. I would like to add a main menu that contains a Play button, as well as options and pages for the Codex, where users can browse discovered elements, reactions and compounds that they have unlocked, an achievements page that includes the users progress, stats, and crafted achievements and milestone tracking. Finally settings should have all the normal settings, accessibility options, and I think at this point it would make sense to add a little bit of sound design. Some very basic open source tracks and feedback sounds for when reactions happen or compounds snap together.

Step 10: Here we should actually implement these different milestones, progress, unlock structure and any scoring we want to include. This should basically be a schedule for when things unlock that we can define almost entirely in data. We can get really creative here with the things and discoveries we want to reward and encourage. We should also spend some time here thinking about how we strike the balance between encouraging unstructured experimentation, and guiding the user educationally towards specific (possibly user marked, as in "oh, I would like to progress towards the Haber Bosche process") results. We want to do this in a way that does not just give the answer to the player, but helps guide them through learning towards the right answer.

Step 11: This is now the data and content phase, and will be where we really take this modestly broad systems foundation and expand it vertically by many orders of magnitude very quickly simply by populating it with data retrieved from existing sources. What I really love about ECS and Bevy is we could make entire "expansion packs" purely from data with just a few extra systems, reaction types, or frankly, some foresight in earlier stages. This is where we turn this from a little game to something that can genuinely teach me and help me learn about Chemistry

Step 12: Once this is all working and the core vision is in place, I have an idea for a new game mode: A reaction chaining mode where the user is presented with a grid of processes and substances, and must chain them together to score points. The more complex a chain they make (either all at once, or across consecutive moves feeding outputs for one reaction into inputs for the next), the higher the score. This relies on the same components as the alchemy mode so should be comparatively easy to implement once everything’s working for that. However, the imposition of the constraint of the randomly generated sets of reaction and process tiles would force users to rely on their knowledge in order to score higher (though we will of course allow them to brows the codex to check their moves ahead of time, as there is nothing about that that harms learning, quite the opposite. For an extreme challenge, we could have a timer that ticks down and is refilled by points meaning you have to be both fast AND accurate with your synthesis knowledge.

## **How steps 7 – 12 fit into the project**

Very briefly tying what you wrote into the architecture:

* 	  
  **Step 7 (multiple process containers):**  
   	  
  * 		  
    Each “process container” becomes its own `ReactionVessel` entity:  
     		  
    * `ReactionVessel {	process: ProcessType }`, `DropTarget`.  
  * 		 		  
  * Inputs on each vessel are `Ingredient + InVessel(VesselId)`.  
  * 		  
    Reaction check loops over vessels instead of one global canvas.  
  * Chaining: product from vessel A is automatically fed as input ingredient into vessel B (data-driven 	pipeline). 	  
* **Step 8 (Bohr/diagram renderers, 	better inventory UI):**  
   	  
  * Replace PNG icons with procedural renderers:  
     		  
    * `ElementRender` system: draws Bohr–Rutherford from Z.  
    * `CompoundRender` system: draw from SMILES/SMARTS or precomputed graph.  
  * Inventory UI gets filters/sorts		  
    * Components for `Element` vs `Compound`, `Metal`, 			`Nonmetal`, etc.  
    * Simple sort state in a resource, buttons to change it, system to rebuild or reorder the list.	 	  
* **Step 9 (main menu, codex, 	achievements, settings, audio):**  
   	  
  * Introduce app `State`: `MainMenu`, `Playing`, `CodexView`, `Achievements`, `Settings`.  
  * Each view spawns/despawns its own UI tree on state enter/exit.  
  * Audio resource \+ simple event-driven SFX (reaction success/fizzle, button clicks, etc).  
* **Step 10 (milestones, unlocks, guidance):**  
   	  
  * Data-driven unlock table: 	  
    * `UnlockDefinition` assets keyed by reaction / substance / achievement.		 		  
  * `PlayerProgress` \+ `DiscoveryEvent` feed unlock logic.  
  * “Goals” system	  
    * Optional goals like “work towards Haber–Bosch” with hint chains:  
      * Show next hint when the player does 				related reactions, not by dumping the answer.	  
* **Step 11 (big data/content phase):**  
  * Substances, reactions, unlocks all as assets.  
  * “Expansion packs” just more data files \+ maybe one or two new systems per big mechanic (e.g. new process type).  
* **Step 12 (reaction chaining mode):**  
   	  
  * Separate game state / mode reusing:  
    * `Substance`, 	`ProcessType`, `RecipeDatabase`, 			`Codex`.	  
  * New board generator \+ scoring system:  
    * Chains as sequences of valid reactions,  
    * Timer/score resource,  
    * Uses the same `reaction_check` core but driven by a different UI front-end.

