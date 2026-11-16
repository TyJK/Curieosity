import json
import os
import argparse
from collections import defaultdict, Counter
from typing import Dict, Any, List
from tqdm import tqdm

# --- DEFAULTS ---
DEFAULT_INPUT_DIR = os.path.normpath("./tools/data/15_inferred")
LOG_DIR = "./tools/logs"
REPORT_FILE = os.path.join(LOG_DIR, "audit_report_full.txt")

class CompleteAuditor:
    def __init__(self, input_dir):
        self.input_dir = input_dir
        self.total_files = 0
        self.profiles = Counter()

        # Stats storage: path -> {present: int, recoverable: int}
        self.stats = defaultdict(lambda: {"present": 0, "recoverable": 0})
        self.missing_registry = defaultdict(list)

        # Explicit null values considered "Missing"
        # REMOVED "N/A" so that explicit "N/A" strings count as present data
        self.nulls = [None, "", "Unknown", "NKRA", "No Data", "Generic", [], {}]

    def is_valid(self, val: Any, allow_zero: bool = False) -> bool:
        if val in self.nulls: return False
        if isinstance(val, str) and len(val.strip()) < 1: return False
        if isinstance(val, (int, float)):
            if not allow_zero and val == 0: return False
            return True
        return True

    def check(self, path: str, value: Any, maintenance_source: Any = None, critical: bool = False, allow_zero: bool = False):
        """
        Checks for presence of data.
        If missing, checks 'maintenance_source' to see if it's recoverable.
        """
        has_val = self.is_valid(value, allow_zero)

        if has_val:
            self.stats[path]["present"] += 1
        else:
            # Check for buried treasure if maintenance source provided
            if maintenance_source and self.is_valid(maintenance_source, allow_zero):
                self.stats[path]["recoverable"] += 1

            # Log missing critical files (limit 5 per field to keep report readable)
            if critical and len(self.missing_registry[path]) < 5:
                self.missing_registry[path].append(self.current_filename)

    def determine_profiles(self, data: Dict[str, Any]) -> None:
        # Just for summary stats
        self.profiles["Universal"] += 1

        cls = data.get("classification", {})
        tags = set(cls.get("tags", []) or [])
        roles = set(cls.get("roles", []) or [])

        if cls.get("is_polymer") or "polymer" in tags: self.profiles["Polymer"] += 1
        elif cls.get("is_mixture") or "mixture" in tags: self.profiles["Mixture"] += 1
        else: self.profiles["Standard Molecule"] += 1

        if "pharmaceutical" in tags or "drug" in tags or data.get("pharmacology", {}).get("atc_codes"):
            self.profiles["Pharmaceutical"] += 1

    def audit_file(self, filename: str):
        self.current_filename = filename
        filepath = os.path.join(self.input_dir, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: return

        # Normalize Root
        root = data if "identity" in data else data.get("compound", {})
        maint = data.get("_maintenance", {})

        # Unwrap raw context for recovery checks
        raw_props = maint.get("ungrouped_context", {}).get("properties_raw", {})
        raw_wiki = maint.get("ungrouped_context", {}).get("wikipedia_raw", {})

        self.total_files += 1
        self.determine_profiles(root)

        # --- 1. IDENTITY ---
        ident = root.get("identity", {})
        self.check("identity.name", ident.get("name"), critical=True)
        self.check("identity.cas_rn", ident.get("cas_rn"), critical=True)
        self.check("identity.smiles", ident.get("smiles"), critical=True)
        self.check("identity.formula", ident.get("formula"), critical=True)
        self.check("identity.synonyms", ident.get("synonyms"), critical=True)
        self.check("identity.description", ident.get("description"), critical=True)
        self.check("identity.parent_id", ident.get("direct_parent_id"))
        self.check("identity.parent_label", ident.get("direct_parent_label"))

        # --- 2. CLASSIFICATION ---
        cls = root.get("classification", {})
        self.check("class.is_polymer", cls.get("is_polymer"))
        self.check("class.is_mixture", cls.get("is_mixture"))
        self.check("class.tags", cls.get("tags"), critical=True)
        self.check("class.roles", cls.get("roles"), critical=True)

        # --- 3. MOLECULAR ---
        mol = root.get("properties", {}).get("molecular", {})
        self.check("molecular.mass", mol.get("mass_g_mol"), critical=True)
        self.check("molecular.logp", mol.get("logp"), allow_zero=True)
        self.check("molecular.charge", mol.get("charge"), allow_zero=True)
        self.check("molecular.complexity", mol.get("complexity"))
        self.check("molecular.tpsa", mol.get("tpsa"), allow_zero=True)
        self.check("molecular.h_donors", mol.get("h_bond_donor_count"), allow_zero=True)
        self.check("molecular.h_acceptors", mol.get("h_bond_acceptor_count"), allow_zero=True)
        self.check("molecular.rotatable_bonds", mol.get("rotatable_bond_count"), allow_zero=True)

        # --- 4. PHYSICAL ---
        phys = root.get("properties", {}).get("physical", {})
        self.check("physical.state", phys.get("state_25_k_1_atm"), critical=True)
        self.check("physical.density", phys.get("density_g_cm3"), critical=True)
        self.check("physical.melting_point", (phys.get("melting_point") or {}).get("value_k"), critical=True)
        self.check("physical.boiling_point", (phys.get("boiling_point") or {}).get("value_k"), critical=True)
        self.check("physical.solubility_water", (phys.get("solubility_water") or {}).get("qualitative"))
        self.check("physical.solubility_profile", phys.get("solubility_profile"))
        self.check("physical.vapor_pressure", (phys.get("vapor_pressure") or {}).get("value_atm"))
        self.check("physical.pka", phys.get("pka_values"))
        self.check("physical.viscosity", phys.get("viscosity_pa_s"))
        self.check("physical.surface_tension", phys.get("surface_tension_n_m"))
        self.check("physical.refractive_index", phys.get("refractive_index"))
        self.check("physical.dipole_moment", phys.get("dipole_moment_debye"), raw_wiki.get("Dipole moment"))
        self.check("physical.autoignition", phys.get("autoignition_k"))
        self.check("physical.flash_point", phys.get("flash_point_k"))
        self.check("physical.decomposition", phys.get("decomposition_k"))

        # --- 5. MECHANICAL ---
        mech = root.get("properties", {}).get("mechanical", {})
        self.check("mech.bulk_modulus", mech.get("bulk_modulus_gpa"))
        self.check("mech.shear_modulus", mech.get("shear_modulus_gpa"))
        self.check("mech.youngs_modulus", mech.get("youngs_modulus_gpa"))
        self.check("mech.mohs_hardness", mech.get("mohs_hardness"))
        self.check("mech.brinell_hardness", mech.get("brinell_hardness"))
        self.check("mech.vickers_hardness", mech.get("vickers_hardness"))

        # --- 6. ELECTROMAGNETIC ---
        el = root.get("properties", {}).get("electromagnetic", {})
        self.check("electro.magnetic_susceptibility", el.get("magnetic_susceptibility_cm3_mol"))

        # --- 7. MATERIAL SCIENCE ---
        mat = root.get("properties", {}).get("material_science", {})
        self.check("mat_sci.crystal_structure", mat.get("crystal_structure"))
        self.check("mat_sci.space_group", mat.get("space_group"))

        # --- 8. THERMODYNAMICS ---
        thermo = root.get("properties", {}).get("thermodynamics", {})
        self.check("thermo.enthalpy_formation", (thermo.get("enthalpy_formation_kj_mol") or {}).get("value_kj_mol"), allow_zero=True)
        self.check("thermo.enthalpy_combustion", thermo.get("enthalpy_combustion_kj_mol"), allow_zero=True)
        self.check("thermo.entropy", thermo.get("molar_entropy_j_mol_k"))
        self.check("thermo.heat_capacity", thermo.get("heat_capacity_j_mol_k"))

        # --- 9. SENSORY ---
        sens = root.get("properties", {}).get("sensory", {})
        self.check("sensory.appearance", sens.get("appearance"), critical=True)
        self.check("sensory.odor", sens.get("odour") or sens.get("odor"), critical=True)
        self.check("sensory.opacity", sens.get("opacity"), allow_zero=True)
        self.check("sensory.texture", sens.get("texture"))

        # --- 10. SAFETY ---
        safe = root.get("safety", {})
        ghs = safe.get("ghs", {})
        nfpa = safe.get("nfpa_704", {})
        occ = safe.get("occupational_limits", {})

        # Buried checks for safety
        buried_nfpa = raw_wiki.get("NFPA 704")
        buried_limits = raw_wiki.get("Explosive limits")

        self.check("safety.summary", safe.get("summary"), critical=True)
        self.check("safety.signal_word", ghs.get("signal_word"), critical=True)
        self.check("safety.hazard_statements", ghs.get("hazard_statements"), critical=True)
        self.check("safety.precautionary", ghs.get("precautionary_statements"))
        self.check("safety.nfpa", nfpa.get("health") or nfpa.get("flammability"), buried_nfpa, allow_zero=True)
        self.check("safety.explosive_limits", (safe.get("explosive_limits") or {}).get("lower_percent"), buried_limits)
        self.check("safety.occupational_limits", occ.get("osha_pel_ppm") or occ.get("niosh_rel_ppm"))

        # --- 11. ECONOMICS ---
        econ = root.get("economics", {})
        # Buried check for price (could be in various raw fields, simplified here)
        self.check("econ.market_price", (econ.get("market_price") or {}).get("value_usd"))
        self.check("econ.production_volume", (econ.get("production_volume") or {}).get("value_kg_year"), critical=True)
        self.check("econ.trade_names", econ.get("trade_names"))
        self.check("econ.industrial_uses", econ.get("industrial_uses"), critical=True)
        self.check("econ.consumer_uses", econ.get("consumer_uses"))
        self.check("econ.sectors", econ.get("industrial_sectors"))
        self.check("econ.is_recycled", econ.get("is_recycled"))

        # --- 12. PHARMACOLOGY ---
        pharma = root.get("pharmacology", {})
        self.check("pharma.mechanism", pharma.get("mechanism_of_action"))
        self.check("pharma.metabolism", pharma.get("metabolism"))
        self.check("pharma.metabolites", pharma.get("metabolites"))
        self.check("pharma.protein_binding", pharma.get("protein_binding"))
        self.check("pharma.routes", pharma.get("route_of_administration"))
        self.check("pharma.atc_codes", pharma.get("atc_codes"))
        self.check("pharma.pregnancy", pharma.get("pregnancy_category"))
        self.check("pharma.bioavailability", pharma.get("bioavailability"))
        self.check("pharma.half_life", pharma.get("pharma_half_life"))
        self.check("pharma.toxicity_ld50", (pharma.get("toxicity") or {}).get("ld50_rat_oral_mg_kg"))

        # --- 13. HISTORY ---
        hist = root.get("history", {})
        self.check("history.discoverer", hist.get("discoverer"), critical=True)
        self.check("history.year", hist.get("year"), critical=True, allow_zero=True)
        self.check("history.story", hist.get("discovery_story"), critical=True)

        # --- 14. MEDIA ---
        med = root.get("media", {})
        spectra = med.get("spectra", {})
        self.check("media.image_2d", med.get("image_2d"), critical=True)
        self.check("media.model_3d", med.get("model_3d"), critical=True)
        self.check("media.spectra_nmr", spectra.get("nmr"))
        self.check("media.spectra_ir", spectra.get("ir"))
        self.check("media.spectra_uv", spectra.get("uv"))

        # --- 15. CROSS REF ---
        refs = root.get("cross_references", {})
        self.check("refs.wikipedia", refs.get("wikipedia"), critical=True)
        self.check("refs.pubchem", refs.get("pubchem_cid"), critical=True)
        self.check("refs.chebi", refs.get("chebi_id") or refs.get("chebi"))
        self.check("refs.drugbank", refs.get("drugbank_id") or refs.get("drugbank"))

    def get_coverage_icon(self, pres):
        """
        Returns a high-contrast gradation using the full Unicode spectrum.
        Sequence: Void -> Mud -> Critical -> Poor -> Warn -> Drab -> Good -> Great -> Excellent -> Perfect
        """
        if self.total_files == 0: return "⚫"
        pct = (pres / self.total_files) * 100

        if pct == 0:     return "⚫"  # Void (Black)
        if pct < 10:     return "🟤"  # Mud (Brown)
        if pct < 20:     return "🟤"  # Mud (Brown)
        if pct < 30:     return "🔴"  # Critical (Red)
        if pct < 40:     return "🔴"  # Critical (Red)
        if pct < 50:     return "🟠"  # Poor (Orange)
        if pct < 60:     return "🟡"  # Warning (Yellow)
        if pct < 70:     return "🫒"  # Drab/Sickly (Olive) - Perfect bridge between Yellow/Green
        if pct < 80:     return "🟢"  # Good (Green)
        if pct < 90:     return "🔵"  # Great (Blue)
        if pct < 99.9:   return "🟣"  # Excellent (Purple) - As requested
        return "🌟"                   # Perfect

    def generate_report(self):
        lines = []
        lines.append(f"🧪 COMPLETE CANON DATASET AUDIT REPORT")
        lines.append(f"========================================")
        lines.append(f"Source: {self.input_dir}")
        lines.append(f"Total Files: {self.total_files}")
        lines.append(f"Profile Breakdown:")
        for p, count in self.profiles.items():
            pct = (count / self.total_files) * 100 if self.total_files > 0 else 0
            lines.append(f"  - {p:<20}: {count:>5} ({pct:.1f}%)")
        lines.append(f"========================================")

        # Group by category
        categories = defaultdict(list)
        for field in self.stats:
            cat = field.split('.')[0].upper()
            categories[cat].append(field)

        for cat in sorted(categories.keys()):
            lines.append(f"\n--- {cat} ---")
            lines.append(f"{'FIELD':<32} | {'FOUND':<6} | {'%':<6} | {'STAT':<4} ")
            lines.append("-" * 75)

            for field in sorted(categories[cat]):
                stats = self.stats[field]
                pres = stats["present"]

                pct = (pres / self.total_files) * 100 if self.total_files > 0 else 0
                icon = self.get_coverage_icon(pres)


                lines.append(f"{field:<32} | {pres:<6} | {pct:.1f}% | {icon:<4}")

        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        print("\n".join(lines[:60]))
        print(f"\n... Full report saved to {REPORT_FILE}")

    def run(self):
        if not os.path.exists(self.input_dir):
            print(f"Error: Directory '{self.input_dir}' not found.")
            return

        files = [f for f in os.listdir(self.input_dir) if f.endswith(".json")]
        print(f"Auditing {len(files)} files in {self.input_dir}...")

        for f in tqdm(files):
            self.audit_file(f)
        self.generate_report()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", nargs="?", default=DEFAULT_INPUT_DIR)
    args = parser.parse_args()
    CompleteAuditor(args.input_dir).run()