# Reaction Dataset Construction Methodology

## Data Acquisition Modes

### Mode A: Compound Backtrace
Starting set: 7k compounds with CAS/SMILES identifiers.

Process:
1. Flag terminal compounds (industrially/pedagogically significant)
2. Query ORD/CRD for reactions producing each terminal compound
3. Extract reactants from results; recurse until reaching elements or common feedstocks
4. Score reactions by pedagogical value (foundational chemistry weighted higher)
5. Deduplicate by canonical reaction SMILES

Output: Directed acyclic graph of synthesis routes with scraped metadata.

### Mode B: Database Forward Scrape
Sources: ORD, CRD, Rhea, KEGG, NIST, Wikipedia chemical reaction categories.

Process:
1. Bulk query each database for reactions involving compounds in the 7k set
2. Filter for reactions where all reactants AND products exist in compound set (closed system)
3. Normalize to canonical reaction SMILES
4. Merge metadata from multiple sources per reaction
5. Flag conflicts between sources

Output: Flat reaction set with provenance tracking.

### Mode C: Template Generation
Input: Reaction class templates defined as SMARTS patterns.

Templates encode:
- Functional group transformations (esterification, amide formation, oxidation, reduction)
- Inorganic reaction types (acid-base, precipitation, redox, displacement)
- Stoichiometric rules (conservation of mass, charge balance)

Process:
1. For each template, enumerate all valid substrate combinations from compound set
2. Generate product SMILES via SMARTS transform
3. Validate products exist in compound set OR flag as potential new compound discoveries
4. Assign `is_canon: false`, mark as template-generated

Output: Expanded reaction set covering combinatorial space.

### Mode D: Thermodynamic Feasibility
Input: Compound thermodynamic data (ΔHf, S°, Cp).

Process:
1. For any proposed reaction (from templates or user experimentation), compute ΔG
2. ΔG = Σ(ΔGf products) - Σ(ΔGf reactants)
3. Apply temperature/pressure corrections via van't Hoff and ideal gas adjustments
4. Reactions with ΔG < 0 under specified conditions are feasible
5. Reactions with ΔG > 50 kJ/mol are blocked (thermodynamically forbidden)
6. Intermediate cases flagged as kinetically limited (require catalyst/activation)

Output: Feasibility verdict for arbitrary combinations.

---

## Cross-Validation Architecture

### Canon vs. Simulation
Every canon reaction (Modes A, B) serves as a test case for the simulation layer (Modes C, D).

Validation checks:
1. Given canon reactants + conditions, does template engine produce canon products?
2. Given canon reactants + conditions, does thermodynamic check return feasible?
3. If mismatch: either canon data is wrong, template is missing, or thermo data is incomplete

Discrepancy categories:
- **MATCH**: Simulation reproduces canon exactly
- **PARTIAL**: Simulation produces subset of canon products (missing template)
- **OVERSHOOT**: Simulation produces superset (side reaction templates too permissive)
- **MISMATCH**: Simulation produces different products (error in either layer)
- **BLOCKED**: Thermodynamics says infeasible but canon says it happens (kinetic override needed)

### Graph Connectivity Validation
The compound set defines nodes; reactions define edges.

Checks:
1. Every non-elemental compound must be reachable from elements via some reaction path
2. Orphan compounds indicate missing reactions (gap in Modes A/B scraping)
3. Unreachable clusters indicate missing hub reactions
4. Compare shortest-path-from-elements against known industrial synthesis depth

### Source Agreement
When multiple databases provide data for the same reaction:

1. Compare stoichiometry (must match exactly)
2. Compare conditions (flag significant disagreements: >50K temp, >10x pressure)
3. Compare yield data (use weighted average, flag outliers)
4. Compute source confidence as agreement ratio

### Template Coverage Audit
For each reaction class (synthesis, decomposition, displacement, etc.):

1. Count canon reactions of that class
2. Count template-generated reactions of that class
3. Ratio indicates template coverage
4. Low canon + high template = undertested template (may generate invalid reactions)
5. High canon + low template = template gap (valid reactions not captured by rules)

---

## Pipeline Stages

### Stage 1: Scrape
Run Modes A and B. Output: raw reaction records with full provenance.

### Stage 2: Normalize
Canonicalize all SMILES. Merge duplicate reactions. Resolve conflicts. Output: deduplicated canon set.

### Stage 3: Expand
Run Mode C against compound set. Output: template-generated reactions marked non-canon.

### Stage 4: Validate
Run all canon reactions through Mode D thermodynamic check. Flag failures for review. Run simulation validation. Output: validation status per reaction.

### Stage 5: Graph Analysis
Build reaction network. Compute hub scores, centrality, reachability. Identify orphans and bottlenecks. Output: graph_position metadata.

### Stage 6: Gap Fill
For orphan compounds: targeted scraping or manual authoring.
For missing reaction classes: template authoring or literature search.
For thermodynamic failures: verify compound thermo data or add kinetic override flags.

### Stage 7: Curate
Human review of Tier 1 (hub) and Tier 4 (capstone) reactions. Add narrative, pedagogy, hints. Verify mechanism and safety data. Output: publication-ready canon reactions.

---

## Feedback Loops

### Loop 1: Compound Discovery
Template generation may predict products not in compound set. Validate prediction via:
1. Check if product SMILES exists in PubChem/ChEBI
2. If exists: add to compound set, re-run pipeline
3. If not exists: likely invalid template output, flag template for review

### Loop 2: Thermodynamic Data Improvement
Feasibility checks fail when compound thermo data is missing. Track:
1. Which compounds most frequently cause feasibility check failures
2. Prioritize those compounds for thermo data scraping/computation
3. Re-run feasibility after data acquisition

### Loop 3: Template Refinement
When canon reactions are not reproduced by templates:
1. Analyze what structural feature the template misses
2. Generalize existing template or author new template
3. Re-run expansion, verify new template captures canon case
4. Audit for overshoot (template too broad)

### Loop 4: Canon Correction
When simulation consistently disagrees with canon:
1. Check canon source reliability
2. Cross-reference additional literature
3. If canon is wrong: correct or remove
4. If simulation is wrong: fix template or thermo data

---

## Coverage Metrics

### Reaction Space Coverage
- Total valid reactions (canon + template-generated)
- Reactions per compound (distribution)
- Reactions per reaction class (balance)
- Tier distribution (should pyramid: many T1, fewer T4)

### Graph Metrics
- Compounds reachable from elements (target: 100%)
- Average path length from elements
- Hub reaction count (target: sufficient to avoid bottlenecks)
- Strongly connected components (target: 1 main component)

### Validation Metrics
- Canon reactions reproducible by simulation (target: >95%)
- Template reactions thermodynamically feasible (target: >99%)
- Source agreement rate for multi-source reactions
- Human validation completion rate for Tier 1/4

### Data Completeness
Per-field population rates (like compound audit):
- Identity fields (target: 100%)
- Stoichiometry fields (target: 100%)
- Conditions fields (target: >80%)
- Thermodynamics fields (target: >60%)
- Narrative fields (Tier 1 only, target: 100%)

---

## Inorganic Gap Strategy

Organic reaction databases (ORD, CRD) underrepresent:
- Elemental synthesis (Na + Cl₂ → NaCl)
- Metal oxide reductions
- Simple acid-base
- Electrochemistry
- High-temperature metallurgy

Mitigation:
1. Educational resource scraping (LibreTexts, Wikipedia reaction categories)
2. NIST thermodynamic database for feasibility-based generation
3. Manual authoring of ~100-150 foundational reactions
4. Template encoding of inorganic reaction classes (activity series, solubility rules)

Validation for inorganic:
- Cross-check against textbook reaction tables
- Verify via NIST thermodynamic feasibility
- Educational peer review

---

## Simulation Engine Requirements

The simulation engine must support:

1. **Exact lookup**: Hash(sorted reactant IDs + process type) → reaction
2. **Template matching**: SMARTS pattern match against reactant structures
3. **Thermodynamic computation**: ΔG calculation from compound data
4. **Condition filtering**: Temperature/pressure/catalyst requirements
5. **Yield estimation**: Based on equilibrium constant and conditions

Priority order for reaction resolution:
1. Exact canon match → return canon reaction
2. Template match + thermo feasible → return generated reaction
3. No template + thermo feasible → return generic "unknown product" placeholder
4. Thermo infeasible → return fizzle

---

## Deliverables

1. **Canon reaction dataset**: ~1000 curated reactions with full metadata
2. **Template library**: SMARTS-based rules covering major reaction classes
3. **Validation report**: Per-reaction reproducibility status
4. **Graph analysis**: Hub identification, reachability maps, bottleneck list
5. **Gap report**: Missing reactions, incomplete data, unresolved conflicts
6. **Audit tooling**: Scripts paralleling compound audit for reaction coverage