import json
import os
import argparse
import logging
from typing import Dict, Any, Tuple

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("Auditor")

# Keywords for Mixtures/Extracts
MIXTURE_KEYWORDS = [
    " oil", " oil,", " oil)", "wax", "tallow", "resin", "extract",
    "petrolatum", "fatty acids", "glycerides", "rosin", "lecithins",
    "gelatins", "bitumens", "asphalt", "coke (coal)", "molasses"
]

REACTION_KEYWORDS = [
    "reaction products", "compounds with", "derivs.", "branched",
    "linear", "by-products", "fractionation", "distillates",
    "residues", "extracts", "polymers with"
]

SOLUTION_ALLOWLIST = {
    "chloric acid", "hypochlorous acid", "chlorous acid",
    "permanganic acid", "dichromic acid", "carbonic acid",
    "nitrous acid", "sulfurous acid"
}

class LibraryAuditor:
    def __init__(self, library_path: str):
        self.library_path = library_path
        self.stats = {
            "total": 0,
            "svg": 0,
            "model_3d": 0,
            "physics_mp": 0,
            "density": 0,
            "valid_mixtures": 0,
            "valid_solutions": 0,
            "valid_superheavy": 0,
            "parser_failures": [],
            "data_failures": []
        }

    def is_complex_mixture(self, name: str) -> bool:
        if not name: return False
        n = name.lower()
        if any(x in n for x in MIXTURE_KEYWORDS): return True
        if any(x in n for x in REACTION_KEYWORDS): return True
        return False

    def is_solution_only(self, name: str) -> bool:
        if not name: return False
        n = name.lower()
        if n in SOLUTION_ALLOWLIST: return True
        if "solution" in n: return True
        return False

    def check_completeness(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        identity = data.get("compound", {}).get("identity", {})
        game_data = data.get("compound", {}).get("game_data", {})
        raw_props = data.get("compound", {}).get("properties_raw", {})

        name = identity.get("name")
        if not isinstance(name, str): name = "Unknown"

        cas = identity.get("cas_rn", "N/A")
        physics = game_data.get("physics", {})

        # 1. Check Superheavy (Mass > 240)
        mass = physics.get("mass", 0)
        if mass > 240:
            self.stats["valid_superheavy"] += 1
            return True, "Superheavy Element"

        # 2. Check Mixtures
        if self.is_complex_mixture(name):
            self.stats["valid_mixtures"] += 1
            return True, "Valid Mixture"

        # 3. Check Solutions
        if self.is_solution_only(name):
            self.stats["valid_solutions"] += 1
            return True, "Valid Solution"

        # 4. Physics Check
        mp = physics.get("melting_point_k")
        if mp is None:
            raw_mp = raw_props.get("melting_point")
            if raw_mp:
                self.stats["parser_failures"].append((name, cas, raw_mp))
                return False, "Parser Failure"
            else:
                self.stats["data_failures"].append((name, cas))
                return False, "Data Missing"

        return True, "Complete"

    def run(self, verbose: bool = False):
        if not os.path.exists(self.library_path):
            logger.error(f"❌ Path not found: {self.library_path}")
            return

        files = [f for f in os.listdir(self.library_path) if f.endswith(".json")]
        self.stats["total"] = len(files)

        logger.info(f"--- Auditing {len(files)} Compound Records ---\n")

        if self.stats["total"] == 0:
            logger.warning("⚠️  No JSON files found in this directory.")
            return

        for f in files:
            path = os.path.join(self.library_path, f)
            try:
                with open(path, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)

                    visuals = data.get("compound", {}).get("game_data", {}).get("visuals", {})
                    if "images" in data.get("compound", {}).get("media", {}) and \
                            data["compound"]["media"]["images"]:
                        self.stats["svg"] += 1

                    if visuals.get("has_3d_model"): self.stats["model_3d"] += 1

                    physics = data.get("compound", {}).get("game_data", {}).get("physics", {})
                    if physics.get("melting_point_k"): self.stats["physics_mp"] += 1
                    if physics.get("density_g_cm3"): self.stats["density"] += 1

                    self.check_completeness(data)

            except Exception as e:
                logger.error(f"Error reading {f}: {e}")

        self.print_report(verbose)

    def print_report(self, verbose: bool):
        s = self.stats
        total = s['total']

        print("=== 📊 Library Health Report ===")
        print(f"Total Records:      {total}")

        if total > 0:
            print(f"With SVGs (2D):     {s['svg']} ({s['svg']/total*100:.1f}%)")
            print(f"With 3D Models:     {s['model_3d']} ({s['model_3d']/total*100:.1f}%)")
            print("-" * 30)
            print(f"With Physics (MP):  {s['physics_mp']} ({s['physics_mp']/total*100:.1f}%)")
            print(f"With Density:       {s['density']} ({s['density']/total*100:.1f}%)")
        else:
            print("No records to analyze.")

        print("-" * 30)
        print("\n=== 🛡️  Valid Exemptions (Skipped) ===")
        print(f"  Complex Mixtures:     {s['valid_mixtures']}")
        print(f"  Solutions/Unstable:   {s['valid_solutions']}")
        print(f"  Superheavy Elements:  {s['valid_superheavy']}")

        print("\n=== ⚠️  Parser Failures (Raw Data Exists) ===")
        print(f"  Count: {len(s['parser_failures'])}")
        if s['parser_failures']:
            print("  Samples:")
            for name, cas, raw in s['parser_failures'][:10]:
                print(f"  - {name} ({cas}) | Raw: '{raw}'")

        print("\n=== ❌  Data Failures (True Gaps) ===")
        print(f"  Count: {len(s['data_failures'])}")
        if verbose and s['data_failures']:
            print("  Listing all failures:")
            for name, cas in s['data_failures']:
                print(f"  - {name} ({cas})")
        elif s['data_failures']:
            print("  Samples:")
            for name, cas in s['data_failures'][:10]:
                print(f"  - {name} ({cas})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="./tools/data/full_compounds", help="Path to JSON library")
    parser.add_argument("--list", action="store_true", help="List all data failures")
    args = parser.parse_args()

    auditor = LibraryAuditor(args.path)
    auditor.run(verbose=args.list)