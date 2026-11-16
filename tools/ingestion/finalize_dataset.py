import json
import os
import logging
from tqdm import tqdm

# --- CONFIGURATION ---
# We assume 17 was the last step. If it's empty, change to 16_deep_recovered
INPUT_DIR = os.path.normpath("./tools/data/17_external_safety")
OUTPUT_DIR = os.path.normpath("./tools/data/18_final_canon")
LOG_DIR = "./tools/logs"
LOG_FILE = os.path.join(LOG_DIR, "finalization.log")

# --- LOGGING ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger("Finalizer")
file_handler = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
logger.addHandler(file_handler)

class DatasetFinalizer:
    def __init__(self):
        self.stats = {
            "total_input": 0,
            "kept": 0,
            "dropped_missing_cas": 0,
            "dropped_missing_2d": 0,
            "dropped_missing_3d": 0,
            "fields_pruned": 0,
            "links_generated": 0
        }

        # Fields to explicitly remove (Dot notation for nested)
        self.prune_list = [
            "history.significance",
            "pharmacology.indication",
            "properties.material_science.lattice_geometry", # Contains lattice_a
            "properties.mechanical.speed_of_sound_m_s",
            "safety.un_number",
            "properties.electromagnetic.electrical_resistivity_ohm_m",
            "properties.electromagnetic.thermal_conductivity_w_m_k",
            "media.spectra" # Replacing with links
        ]

    def get_nested(self, data, path):
        """Helper to safely get nested values."""
        keys = path.split('.')
        curr = data
        for k in keys:
            if isinstance(curr, dict):
                curr = curr.get(k)
            else:
                return None
        return curr

    def delete_nested(self, data, path):
        """Helper to safely delete nested keys."""
        keys = path.split('.')
        curr = data
        for i, k in enumerate(keys[:-1]):
            if isinstance(curr, dict) and k in curr:
                curr = curr[k]
            else:
                return # Path doesn't exist

        last_key = keys[-1]
        if isinstance(curr, dict) and last_key in curr:
            del curr[last_key]
            self.stats["fields_pruned"] += 1

    def generate_links(self, cas_rn):
        """Generates deep links to NIST and other spectral DBs."""
        if not cas_rn: return None

        # NIST uses "C" + CAS without dashes (e.g., C50817)
        clean_cas = cas_rn.replace("-", "")

        return {
            "nist_webbook": f"https://webbook.nist.gov/cgi/cbook.cgi?ID=C{clean_cas}&Units=SI",
            "pubchem_compound": f"https://pubchem.ncbi.nlm.nih.gov/#query={cas_rn}",
            "google_scholar": f"https://scholar.google.com/scholar?q={cas_rn}"
        }

    def process_file(self, filename):
        self.stats["total_input"] += 1
        filepath = os.path.join(INPUT_DIR, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: return

        root = data if "identity" in data else data.get("compound", {})
        ident = root.get("identity", {})
        media = root.get("media", {})

        # --- 1. THE CULL (Quality Control) ---
        # Must have CAS
        cas = ident.get("cas_rn")
        if not cas or cas in ["", "N/A", None]:
            self.stats["dropped_missing_cas"] += 1
            return # DROP

        # Must have 2D Image (SVG string)
        img_2d = media.get("image_2d")
        if not img_2d or len(str(img_2d)) < 50: # Basic length check for valid SVG
            self.stats["dropped_missing_2d"] += 1
            return # DROP

        # Must have 3D Model (MolBlock/SDF string)
        model_3d = media.get("model_3d")
        if not model_3d or len(str(model_3d)) < 50:
            self.stats["dropped_missing_3d"] += 1
            return # DROP

        # --- 2. TRANSFORMATION (Spectra Links) ---
        links = self.generate_links(cas)
        if links:
            media["external_links"] = links
            self.stats["links_generated"] += 1

        # --- 3. THE PRUNE (Schema Cleanup) ---
        for field_path in self.prune_list:
            self.delete_nested(root, field_path)

        # --- 4. SAVE ---
        out_path = os.path.join(OUTPUT_DIR, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.stats["kept"] += 1

    def run(self):
        if not os.path.exists(INPUT_DIR):
            print(f"❌ Input directory not found: {INPUT_DIR}")
            return

        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        print(f"💎 Starting FINAL DATASET CONSTRUCTION on {len(files)} files...")
        print("   Criteria: Must have CAS, 2D Image, 3D Model.")
        print("   Actions:  Pruning schema, Generating external links.")

        for f in tqdm(files):
            self.process_file(f)

        print("\n------------------------------------------------")
        print("FINAL DATASET STATS:")
        print(f"  Input Files:       {self.stats['total_input']}")
        print(f"  Final Count:       {self.stats['kept']} (💎 Gold Standard)")
        print(f"  Dropped (No CAS):  {self.stats['dropped_missing_cas']}")
        print(f"  Dropped (No 2D):   {self.stats['dropped_missing_2d']}")
        print(f"  Dropped (No 3D):   {self.stats['dropped_missing_3d']}")
        print(f"  Links Generated:   {self.stats['links_generated']}")
        print(f"  Output Dir:        {OUTPUT_DIR}")
        print("------------------------------------------------")

if __name__ == "__main__":
    DatasetFinalizer().run()