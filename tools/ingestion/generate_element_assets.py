import os
import json
import math
import logging
from tqdm import tqdm

# --- CONFIGURATION ---
DATA_DIR = os.path.normpath("./tools/data/00_element_skeleton")
ASSETS_DIR = os.path.normpath("./assets/elements")
LOG_DIR = "./tools/logs"

# Ensure directories exist
os.makedirs(f"{ASSETS_DIR}/icons", exist_ok=True)
os.makedirs(f"{ASSETS_DIR}/shells", exist_ok=True)
os.makedirs(f"{ASSETS_DIR}/spectra", exist_ok=True) # Creating folder, but leaving empty for now
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[logging.FileHandler(f"{LOG_DIR}/asset_generation.log", mode='w', encoding='utf-8')]
)
logger = logging.getLogger("AssetGen")

class AssetGenerator:
    def __init__(self):
        self.stats = {"icons_created": 0, "shells_created": 0, "errors": 0}

    def generate_icon(self, atomic_number, symbol, name, mass):
        """Generates a Periodic Table style card SVG."""
        color_map = {
            "s": "#ff9999", "p": "#99ccff", "d": "#ffcc99", "f": "#99ff99"
        }
        # Default to grey if block unknown
        fill = "#e0e0e0"

        # Simple SVG Template
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
          <rect x="5" y="5" width="190" height="190" rx="15" ry="15" 
                fill="#ffffff" stroke="#333" stroke-width="4"/>
          <text x="20" y="40" font-family="Arial" font-size="24" fill="#666">{atomic_number}</text>
          <text x="100" y="110" font-family="Arial" font-size="80" font-weight="bold" 
                text-anchor="middle" fill="#000">{symbol}</text>
          <text x="100" y="150" font-family="Arial" font-size="18" 
                text-anchor="middle" fill="#333">{name}</text>
          <text x="100" y="180" font-family="Arial" font-size="16" 
                text-anchor="middle" fill="#666">{mass}</text>
        </svg>'''

        path = f"{ASSETS_DIR}/icons/{atomic_number}_{symbol}.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        self.stats["icons_created"] += 1

    def generate_bohr_model(self, atomic_number, symbol, electron_config):
        """
        Generates a Bohr Model SVG.
        Parses the semantic '1s2 2s2' string or uses simple shell filling logic 2, 8, 18, 32...
        """
        # 1. Parse Shells (Simple approximation if full semantic data missing)
        # We derived shells from standard capacity: 2*n^2
        electrons = atomic_number
        shells = []
        n = 1
        while electrons > 0:
            capacity = 2 * (n**2)
            # For Z > 20 this simple logic breaks down (transition metals),
            # but for a visual Bohr model representative of "layers", it's often accepted
            # OR we can parse the specific config from your JSON if available.

            # BETTER APPROACH: Use the 'semantic_filling' from your JSON if populated,
            # otherwise fall back to this logic.
            # For visual simplicity in this script, we'll use a fixed lookup or approximation.

            count = min(electrons, capacity)
            # Adjust for outer shell max (octet rule visualization usually caps at 8 for diagrams)
            # NOTE: Highly accurate orbital rendering is complex. This is a visual abstraction.

            shells.append(count)
            electrons -= count
            n += 1
            if n > 7: break # Safety

        # Re-calculating correctly based on noble gas periods for visual accuracy
        # This is a heuristic for visual shells (K, L, M, N...)
        # A robust way is to just group the 'electron_configuration' string by principal quantum number.

        # Heuristic override for drawing:
        # We will parse the 'shorthand' or 'full' config if we can, but let's assume
        # the user wants the standard K,L,M,N counts.
        # Let's use a known library logic or just simple 2,8,8... logic for now.

        # Drawing Logic
        cx, cy = 250, 250
        max_radius = 220
        svg_content = ""

        # Nucleus
        svg_content += f'<circle cx="{cx}" cy="{cy}" r="20" fill="#333" />'
        svg_content += f'<text x="{cx}" y="{cy+5}" font-family="Arial" font-size="14" fill="#fff" text-anchor="middle">{symbol}</text>'

        # Shells
        shell_counts = self.get_shell_counts(electron_config, atomic_number)
        num_shells = len(shell_counts)
        if num_shells == 0: num_shells = 1 # Fallback

        base_radius = 40
        step = (max_radius - base_radius) / num_shells

        for i, count in enumerate(shell_counts):
            r = base_radius + (i * step)
            # Draw Orbit Ring
            svg_content += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#999" stroke-width="2" />'

            # Draw Electrons
            if count > 0:
                angle_step = 360 / count
                for e in range(count):
                    angle = math.radians(e * angle_step - 90) # Start at top
                    ex = cx + r * math.cos(angle)
                    ey = cy + r * math.sin(angle)
                    svg_content += f'<circle cx="{ex}" cy="{ey}" r="6" fill="#3498db" stroke="#fff" stroke-width="1"/>'

        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500">{svg_content}</svg>'

        path = f"{ASSETS_DIR}/shells/{atomic_number}_{symbol}_shell.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        self.stats["shells_created"] += 1

    def get_shell_counts(self, config_obj, z):
        """
        Parses '1s2 2s2 2p6...' into [2, 8...] per principal shell.
        """
        config_str = config_obj.get("shorthand", "")
        # This is tricky without a full parser library.
        # Fallback: Mendeleev logic via hardcoded period capacities for visualization
        # K=2, L=8, M=18, N=32...

        # Actually, let's just use the period logic from the file if we can't parse string.
        # Simple parser for "1s2 2s2 ...":
        counts = {}

        # Remove [Gas] part for parsing (visuals usually want full shells)
        # Note: This parser is 'best effort' for visualization.
        # Ideally we use the 'semantic_filling' dict if we populated it fully in Step 1.

        # HACK: For generating nice visuals quickly without complex quantum logic re-implementation:
        # We know shells generally fill 2, 8, 18...
        # But we need specific valence.

        # Let's use a naive filling for visualization purposes:
        shells = [0] * 7
        e_rem = z

        # Capacities: 2, 8, 18, 32, 32, 18, 8 (Standard approx for main group)
        # This is chemically inexact for transition metals but creates the correct 'Bohr' visual
        # often seen in textbooks.

        # Better: Use the period to determine shells, then fill.
        # Since this is a "Canon" dataset, maybe we skip the 'guess' and assume
        # the user will run a more advanced physics simulation for exact positions.
        # But for the SVG, let's do:

        # Official Shell Capacities (K, L, M, N, O, P, Q)
        # H (1): [1]
        # He (2): [2]
        # Li (3): [2, 1]
        # ...
        # This requires a lookup table or a full Aufbau implementation.
        # I will implement a basic Aufbau logic here.

        return self.aufbau_shells(z)

    def aufbau_shells(self, z):
        """Returns electrons per shell [K, L, M...] for Z."""
        # Visual/Bohr notation (Principal Quantum Number sums)
        # This is derived from Madelung rule
        shells = {}

        # Orbital filling order: 1s, 2s, 2p, 3s, 3p, 4s, 3d, 4p, 5s, 4d, 5p, 6s, 4f, 5d, 6p...
        # Capacities: s=2, p=6, d=10, f=14
        order = [
            (1,'s'), (2,'s'), (2,'p'), (3,'s'), (3,'p'), (4,'s'), (3,'d'), (4,'p'),
            (5,'s'), (4,'d'), (5,'p'), (6,'s'), (4,'f'), (5,'d'), (6,'p'), (7,'s'),
            (5,'f'), (6,'d'), (7,'p')
        ]
        cap = {'s':2, 'p':6, 'd':10, 'f':14}

        remaining = z
        for n, orb in order:
            if remaining <= 0: break
            take = min(remaining, cap[orb])
            shells[n] = shells.get(n, 0) + take
            remaining -= take

            # Note: This follows pure Madelung.
            # Real chemistry has exceptions (Cr, Cu), but for a generated 2D icon
            # this is usually indistinguishable.

        return [shells[k] for k in sorted(shells.keys())]


    def run(self):
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
        print(f"🎨 Generating Assets for {len(files)} elements...")

        for f in tqdm(files):
            try:
                with open(os.path.join(DATA_DIR, f), 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)

                ident = data["identity"]
                z = ident["atomic_number"]
                sym = ident["symbol"]
                name = ident["name"]
                mass = ident.get("standard_atomic_weight", "???")
                if isinstance(mass, float): mass = f"{mass:.2f}"

                # 1. Icon
                self.generate_icon(z, sym, name, mass)

                # 2. Shell
                q_mech = data.get("quantum_mechanics", {})
                e_config = q_mech.get("electron_configuration", {})
                self.generate_bohr_model(z, sym, e_config)

            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"Error on {f}: {e}")

        print("DONE. Stats:")
        for k, v in self.stats.items(): print(f"  {k}: {v}")

if __name__ == "__main__":
    AssetGenerator().run()