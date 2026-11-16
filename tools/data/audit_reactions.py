import json
import os
import argparse
from collections import defaultdict, Counter
from tqdm import tqdm

# --- CONFIGURATION ---
DEFAULT_INPUT_DIR = os.path.normpath("./tools/data/reaction_dataset")
LOG_DIR = "./tools/logs"
REPORT_FILE = os.path.join(LOG_DIR, "reaction_audit_report.txt")

class ReactionAuditor:
    def __init__(self, input_dir):
        self.input_dir = input_dir
        self.total_reactions = 0
        self.stats = defaultdict(int)
        self.classification_counts = Counter()
        self.safety_counts = Counter()
        self.yield_values = [] # For histogram/stats

    def analyze_yield(self, record):
        """Tracks yield distribution and outliers."""
        y_obj = record.get("yield", {}).get("typical", {})
        val = y_obj.get("percent", 0.0)

        if val > 0:
            self.stats["has_yield"] += 1
            self.yield_values.append(val)
            if val > 100: self.stats["yield_abnormal_high"] += 1
        else:
            self.stats["missing_yield"] += 1

    def analyze_safety(self, record):
        """Tracks safety flags."""
        s = record.get("safety", {})
        summary = s.get("summary", "Unknown")
        self.safety_counts[summary] += 1

        if "Fatal" in summary or "DANGER" in summary:
            self.stats["safety_critical"] += 1
        elif "Explosive" in summary:
            self.stats["safety_explosive"] += 1

    def analyze_classification(self, record):
        """Tracks reaction types."""
        c = record.get("classification", {})
        prim = c.get("primary_type", "Unclassified")
        self.classification_counts[prim] += 1

        if prim != "Unclassified":
            self.stats["classified"] += 1

    def audit_file(self, filename):
        filepath = os.path.join(self.input_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: return

        self.total_reactions += 1

        # Core Checks
        if data.get("identity", {}).get("reaction_smiles"): self.stats["has_smiles"] += 1
        if data.get("stoichiometry", {}).get("reactants"): self.stats["has_reactants"] += 1
        if data.get("stoichiometry", {}).get("products"): self.stats["has_products"] += 1

        # Mining Checks
        conds = data.get("conditions", {})
        if conds.get("temperature", {}).get("value_k"): self.stats["has_temp"] += 1
        if conds.get("time", {}).get("value_seconds"): self.stats["has_time"] += 1

        self.analyze_yield(data)
        self.analyze_classification(data)
        self.analyze_safety(data)

    def generate_report(self):
        lines = []
        lines.append(f"🧪 REACTION DATASET AUDIT REPORT")
        lines.append(f"========================================")
        lines.append(f"Source: {self.input_dir}")
        lines.append(f"Total Reactions: {self.total_reactions}")

        if self.total_reactions == 0:
            lines.append("\n❌ No reaction files found to audit.")
            print("\n".join(lines))
            return

        # Coverage
        lines.append(f"\n--- DATA COVERAGE ---")

        def coverage_line(label, key):
            count = self.stats[key]
            pct = (count / self.total_reactions) * 100
            icon = "🟢" if pct > 80 else "🟡" if pct > 50 else "🔴"
            return f"{label:<25} {count:>5} ({pct:.1f}%) {icon}"

        lines.append(coverage_line("Identity (SMILES):", "has_smiles"))
        lines.append(coverage_line("Stoichiometry:", "has_reactants"))
        lines.append(coverage_line("Yield Data:", "has_yield"))
        lines.append(coverage_line("Temperature:", "has_temp"))
        lines.append(coverage_line("Reaction Time:", "has_time"))

        # Classification
        lines.append(f"\n--- CLASSIFICATION ---")
        class_rate = (self.stats['classified']/self.total_reactions*100)
        lines.append(f"Classified: {self.stats['classified']} ({class_rate:.1f}%)")
        lines.append(f"Top Types:")
        for k, v in self.classification_counts.most_common(10):
            lines.append(f"  - {k:<30}: {v}")

        # Safety
        lines.append(f"\n--- SAFETY PROFILE ---")
        lines.append(f"Critical (Fatal/Toxic): {self.stats['safety_critical']}")
        lines.append(f"High Risk (Explosive):  {self.stats['safety_explosive']}")
        lines.append(f"Breakdown:")
        for k, v in self.safety_counts.most_common(5):
            # Truncate long safety summaries
            safe_sum = (k[:60] + '..') if len(k) > 60 else k
            lines.append(f"  - {safe_sum:<62}: {v}")

        # Yield Stats
        if self.yield_values:
            avg_yield = sum(self.yield_values) / len(self.yield_values)
            lines.append(f"\n--- YIELD STATISTICS ---")
            lines.append(f"Average Yield: {avg_yield:.1f}%")
            lines.append(f"Abnormal (>100%): {self.stats['yield_abnormal_high']}")

        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        print("\n".join(lines))
        print(f"\n📄 Report saved to {REPORT_FILE}")

    def run(self):
        if not os.path.exists(self.input_dir):
            print(f"❌ Error: {self.input_dir} not found.")
            return

        files = [f for f in os.listdir(self.input_dir) if f.endswith(".json")]
        print(f"🔍 Auditing {len(files)} reaction records...")

        for f in tqdm(files):
            self.audit_file(f)
        self.generate_report()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", nargs="?", default=DEFAULT_INPUT_DIR)
    args = parser.parse_args()
    ReactionAuditor(args.input_dir).run()