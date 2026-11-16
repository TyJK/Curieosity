import json
import logging
from rdkit import Chem
from rdkit.Chem import rdChemReactions
from rdkit import RDLogger

RDLogger.DisableLog('rdApp.*')
OUTPUT_FILE = "./tools/data/reaction_templates.json"

# --- SMART GENERATOR UTILS ---
# Helper to create safe Recursive SMARTS lists: [$(A),$(B),$(C)]
def make_list(smarts_list):
    parts = [f"$({s})" for s in smarts_list]
    return f"[{','.join(parts)}]"

# --- BUILDING BLOCKS (THE LEGOS) ---
GROUPS = {
    "Alkyl": "[CX4]",
    "Aryl": "[c]",
    "Acyl": "[CX3](=[OX1])",
    "Carboxyl": "[CX3](=[OX1])[OX2H]",
    "Ester": "[CX3](=[OX1])[OX2][#6]",
    "Amide": "[CX3](=[OX1])[NX3]",
    "Amine": "[NX3;H2,H1]",
    "Alcohol": "[OX2H]",
    "Aldehyde": "[CH1](=[OX1])",
    "Ketone": "[CX3](=[OX1])[#6]",
    "Nitro": "[N+](=O)[O-]",
    "Azide": "[N]=[N+]=[N-]",
    "Alkyne": "[C]#[C]",
    "Boronic": "[B]([O])[O]",
    "Sulfonate": "[S](=[O])(=[O])[O]",
    "Epoxide": "[C]1[O][C]1",
    "Isocyanate": "[N]=[C]=[O]",
    "Anhydride": "[CX3](=[OX1])[OX2][CX3](=[OX1])",

    # ATOMIC LISTS (Fixed for RDKit Compliance)
    "Halogen": "[F,Cl,Br,I]", # Simple list is safer for atoms
    "LeavingGroup": make_list(["Cl", "Br", "I", "OS(=O)(=O)"]),
    # Metals must be in brackets for SMARTS
    "Metal": "[Mg,Li,Zn,Na,K]",
    # Bases: O- (alkoxide/hydroxide) or N (amine)
    "Base": "[O-,N]",
    "SandmeyerOut": make_list(["Cl", "Br", "I", "C#N"])
}

# --- THE EXPANDED LIBRARY (75+ Templates) ---
RAW_TEMPLATES = [
    # === 1. TARGETED CLUSTER BUSTERS (NEW) ===
    # Matches Cluster #1, #8: THP Protection of Alcohols (DHP + Alcohol)
    {"name": "THP Protection", "type": "Protection",
     "reactants": ["[#6]1[#6][#6][#6][#6]=[#8]1", GROUPS["Alcohol"]],
     "products": ["[#6]1[#6][#6][#6][#6][#8]1[#8][#6]"]},

    # Matches Cluster #2: Alkyne Addition to Carbonyl
    {"name": "Alkyne Addition", "type": "C-C Bond Formation",
     "reactants": [GROUPS["Alkyne"], "[C]=[O]"],
     "products": ["[C]#[C][C]([OH])"]},

    # Matches Cluster #3: Anhydride Esterification/Amidation
    {"name": "Anhydride Acylation", "type": "Acylation",
     "reactants": [GROUPS["Anhydride"], make_list(["[OX2H]", "[NX3;H2,H1]"])],
     "products": [make_list([GROUPS["Ester"], GROUPS["Amide"]])]},

    # Matches Cluster #5-7: Amide N-Alkylation (Strict N-Alkylation missed amides)
    {"name": "Amide N-Alkylation", "type": "Alkylation",
     "reactants": ["[#6](=[O])[NX3H1]", f"[C]{GROUPS['LeavingGroup']}"],
     "products": ["[#6](=[O])[NX3][C]"]},

    # Matches Cluster #9: Epoxide Ring Opening (Aminolysis)
    {"name": "Epoxide Opening (Amine)", "type": "Ring Opening",
     "reactants": [GROUPS["Epoxide"], GROUPS["Amine"]],
     "products": ["[C]([O])[C][N]"]},

    # Matches Cluster #16: Intramolecular Friedel-Crafts
    {"name": "Friedel-Crafts Cyclization", "type": "Cyclization",
     "reactants": [f"{GROUPS['Aryl']}.{GROUPS['Acyl']}[Cl,OH]"], # Dot allows loose mapping
     "products": [f"{GROUPS['Aryl']}{GROUPS['Acyl']}"]},

    # Matches Cluster #18: Pyrimidine/Heterocycle Synthesis (Urea + 1,3-dicarbonyl equivalent)
    {"name": "Heterocycle Formation", "type": "Heterocycle Formation",
     "reactants": ["[NX3][CX3](=[OX1])[NX3]", "[C]=[C]"], # Broad match for Urea + Enone
     "products": ["[n]1[c][n][c][c][c]1"]},

    # Matches Cluster #19: Thionation (Lawesson's Reagent)
    {"name": "Thionation", "type": "Functional Group Interconversion",
     "reactants": ["[C]=[O]", "P(=S)"],
     "products": ["[C]=[S]"]},

    # Urea Formation (Isocyanate + Amine)
    {"name": "Urea Formation", "type": "Condensation",
     "reactants": [GROUPS["Isocyanate"], GROUPS["Amine"]],
     "products": ["[NX3][CX3](=[OX1])[NX3]"]},

    # Sulfonamide Formation (Sulfonyl Chloride + Amine)
    {"name": "Sulfonamide Formation", "type": "Condensation",
     "reactants": ["[S](=[O])(=[O])[Cl]", GROUPS["Amine"]],
     "products": ["[S](=[O])(=[O])[NX3]"]},

    # === 2. STANDARD LIBRARY (EXISTING) ===
    # --- CONDENSATIONS ---
    {"name": "Fischer Esterification", "type": "Condensation",
     "reactants": [GROUPS["Carboxyl"], GROUPS["Alcohol"]], "products": [GROUPS["Ester"]]},
    {"name": "Amide Coupling", "type": "Acylation",
     "reactants": [GROUPS["Carboxyl"], GROUPS["Amine"]], "products": [GROUPS["Amide"]]},
    {"name": "Schotten-Baumann (Chloride)", "type": "Acylation",
     "reactants": [f"{GROUPS['Acyl']}[Cl]", GROUPS["Amine"]], "products": [GROUPS["Amide"]]},
    {"name": "Aldol Condensation", "type": "Condensation",
     "reactants": [GROUPS["Ketone"], GROUPS["Ketone"]], "products": ["[C]=[C][C](=[O])"]},
    {"name": "Knoevenagel Condensation", "type": "Condensation",
     "reactants": [GROUPS["Aldehyde"], "[CH2]"], "products": ["[C]=[C]"]},
    {"name": "Imine Formation", "type": "Condensation",
     "reactants": [GROUPS["Ketone"], GROUPS["Amine"]], "products": ["[C]=[N]"]},

    # --- ALKYLATIONS ---
    {"name": "N-Alkylation", "type": "Alkylation",
     "reactants": [GROUPS["Amine"], f"[C]{GROUPS['LeavingGroup']}"], "products": ["[NX3][C]"]},
    {"name": "Williamson Ether Synthesis", "type": "Alkylation",
     "reactants": [GROUPS["Alcohol"], f"[C]{GROUPS['LeavingGroup']}"], "products": ["[OX2][C]"]},
    {"name": "Friedel-Crafts Alkylation", "type": "Alkylation",
     "reactants": [GROUPS["Aryl"], f"[C]{GROUPS['Halogen']}"], "products": ["[c][C]"]},
    {"name": "S-Alkylation", "type": "Alkylation",
     "reactants": ["[SX2H]", f"[C]{GROUPS['LeavingGroup']}"], "products": ["[SX2][C]"]},

    # --- ELECTROPHILIC SUBSTITUTION ---
    {"name": "Friedel-Crafts Acylation", "type": "Acylation",
     "reactants": [GROUPS["Aryl"], f"{GROUPS['Acyl']}[Cl]"], "products": [f"[c]{GROUPS['Acyl']}"]},
    {"name": "Aromatic Sulfonation", "type": "Electrophilic Substitution",
     "reactants": [GROUPS["Aryl"], GROUPS["Sulfonate"]], "products": [f"[c]{GROUPS['Sulfonate']}"]},
    {"name": "Aromatic Nitration", "type": "Electrophilic Substitution",
     "reactants": [GROUPS["Aryl"], GROUPS["Nitro"]], "products": [f"[c]{GROUPS['Nitro']}"]},
    {"name": "Sandmeyer Reaction", "type": "Substitution",
     "reactants": ["[c][N+]#N"], "products": [f"[c]{GROUPS['SandmeyerOut']}"]},

    # --- OXIDATIONS ---
    {"name": "Jones Oxidation", "type": "Oxidation",
     "reactants": ["[CH2][OH]"], "products": [GROUPS["Carboxyl"]]},
    {"name": "Swern Oxidation", "type": "Oxidation",
     "reactants": ["[CH][OH]"], "products": [GROUPS["Ketone"]]},
    {"name": "Epoxidation", "type": "Oxidation",
     "reactants": ["[C]=[C]"], "products": ["[C]1[O][C]1"]},
    {"name": "Baeyer-Villiger Oxidation", "type": "Oxidation",
     "reactants": [GROUPS["Ketone"]], "products": [GROUPS["Ester"]]},
    {"name": "Alcohol to Aldehyde", "type": "Oxidation",
     "reactants": ["[CH2][OH]"], "products": [GROUPS["Aldehyde"]]},

    # --- REDUCTIONS ---
    {"name": "Nitro Reduction", "type": "Reduction",
     "reactants": [GROUPS["Nitro"]], "products": ["[NH2]"]},
    {"name": "Carbonyl Reduction", "type": "Reduction",
     "reactants": [GROUPS["Ketone"]], "products": ["[CH][OH]"]},
    {"name": "Dehalogenation (Zinc/Elimination)", "type": "Elimination",
     "reactants": [f"[C]{GROUPS['Halogen']}", f"[C]{GROUPS['Halogen']}"], "products": ["[C]=[C]"]},
    {"name": "Hydrogenation", "type": "Reduction",
     "reactants": ["[C]=[C]"], "products": ["[CH][CH]"]},
    {"name": "Nitrile Reduction", "type": "Reduction",
     "reactants": ["[C]#[N]"], "products": ["[CH2][NH2]"]},
    {"name": "Ester to Alcohol", "type": "Reduction",
     "reactants": [GROUPS["Ester"]], "products": [GROUPS["Alcohol"]]},
    {"name": "Amide to Amine", "type": "Reduction",
     "reactants": [GROUPS["Amide"]], "products": ["[CH2][NX3]"]},

    # --- COUPLINGS ---
    {"name": "Suzuki Coupling", "type": "C-C Coupling",
     "reactants": [f"[c]{GROUPS['Halogen']}", GROUPS["Boronic"]], "products": ["[c][c]"]},
    {"name": "Sonogashira Coupling", "type": "C-C Coupling",
     "reactants": [f"[c]{GROUPS['Halogen']}", GROUPS["Alkyne"]], "products": [f"[c]{GROUPS['Alkyne']}"]},
    {"name": "Heck Reaction", "type": "C-C Coupling",
     "reactants": [f"[c]{GROUPS['Halogen']}", "[C]=[C]"], "products": ["[c][C]=[C]"]},
    {"name": "Click Chemistry", "type": "Heterocycle Formation",
     "reactants": [GROUPS["Azide"], GROUPS["Alkyne"]], "products": ["[n]1[n][n][c][c]1"]},

    # --- PROTECTIONS / DEPROTECTIONS ---
    {"name": "Boc Protection", "type": "Protection",
     "reactants": [GROUPS["Amine"]], "products": ["[NX3][C](=[O])[O][C]([C])([C])[C]"]},
    {"name": "Boc Deprotection", "type": "Deprotection",
     "reactants": ["[NX3][C](=[O])[O][C]([C])([C])[C]"], "products": [GROUPS["Amine"]]},
    {"name": "Fmoc Protection", "type": "Protection",
     "reactants": [GROUPS["Amine"]], "products": ["[NX3][C](=[O])[O][CH2][c]"]},
    {"name": "Fmoc Deprotection", "type": "Deprotection",
     "reactants": ["[NX3][C](=[O])[O][CH2][c]"], "products": [GROUPS["Amine"]]},
    {"name": "TBDMS Protection", "type": "Protection",
     "reactants": [GROUPS["Alcohol"]], "products": ["[OX2][Si]([C])([C])([C])"]},
    {"name": "TBDMS Deprotection", "type": "Deprotection",
     "reactants": ["[OX2][Si]([C])([C])([C])"], "products": [GROUPS["Alcohol"]]},
    {"name": "Acetal Formation", "type": "Protection",
     "reactants": [GROUPS["Ketone"], GROUPS["Alcohol"]], "products": ["[C]([O])([O])"]},

    # --- FUNCTIONAL GROUP INTERCONVERSION ---
    {"name": "Acid to Acid Chloride", "type": "Functional Group Interconversion",
     "reactants": [GROUPS["Carboxyl"]], "products": [f"{GROUPS['Acyl']}[Cl]"]},
    {"name": "Alcohol to Alkyl Halide", "type": "Functional Group Interconversion",
     "reactants": [GROUPS["Alcohol"]], "products": [f"[C]{GROUPS['Halogen']}"]},
    {"name": "Nitrile Hydrolysis", "type": "Hydrolysis",
     "reactants": ["[C]#[N]"], "products": [GROUPS["Carboxyl"]]},
    {"name": "Ester Hydrolysis", "type": "Hydrolysis",
     "reactants": [GROUPS["Ester"]], "products": [GROUPS["Carboxyl"]]},
    {"name": "Anhydride Formation", "type": "Dehydration",
     "reactants": [GROUPS["Carboxyl"], GROUPS["Carboxyl"]], "products": [f"{GROUPS['Acyl']}[O]{GROUPS['Acyl']}"]},

    # --- SPECIALTY / INDUSTRIAL ---
    {"name": "Sultone Formation", "type": "Cyclization",
     "reactants": ["[C]=[C]", GROUPS["Sulfonate"]], "products": ["[C]1[C][S](=[O])(=[O])[O]1"]},
    {"name": "Grignard Reaction", "type": "C-C Bond Formation",
     "reactants": [GROUPS["Ketone"], GROUPS["Metal"]], "products": ["[C]([OH])[#6]"]},
    {"name": "Neutralization (Salt Formation)", "type": "Neutralization",
     "reactants": [GROUPS["Carboxyl"], GROUPS["Base"]], "products": [f"{GROUPS['Acyl']}[O-]"]}
]

def compile_and_validate():
    valid_templates = []
    print(f"⚙️  Compiling {len(RAW_TEMPLATES)} template definitions...")

    for t in RAW_TEMPLATES:
        try:
            # Construct Pseudo-SMARTS for metadata
            r_str = ".".join(t["reactants"])
            p_str = ".".join(t["products"])
            t["smarts_visual"] = f"{r_str}>>{p_str}"

            # Validate Components (Individual parsing is safer)
            r_mols = [Chem.MolFromSmarts(s) for s in t["reactants"]]
            p_mols = [Chem.MolFromSmarts(s) for s in t["products"]]

            if all(r_mols) and all(p_mols):
                valid_templates.append(t)
            else:
                print(f"❌ Syntax Error in '{t['name']}': RDKit rejected component.")
        except Exception as e:
            print(f"❌ Exception in '{t['name']}': {e}")

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(valid_templates, f, indent=2)

    print(f"\n✅ Successfully compiled {len(valid_templates)}/{len(RAW_TEMPLATES)} templates.")
    print(f"📁 Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    compile_and_validate()