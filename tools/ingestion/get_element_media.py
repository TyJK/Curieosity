import json
import os
import math
import logging
import re
from tqdm import tqdm

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/01_element_enriched")
OUTPUT_DIR = os.path.normpath("./tools/data/02_element_media")
ASSETS_DIR = os.path.normpath("./assets/elements")
LOG_DIR = "./tools/logs"

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{ASSETS_DIR}/spectra", exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[logging.FileHandler(f"{LOG_DIR}/media_densification.log", mode='w', encoding='utf-8')]
)
logger = logging.getLogger("MediaDensifier")

class MediaDensifier:
    def __init__(self):
        self.stats = {"processed": 0, "svgs_embedded": 0, "errors": 0}

    def minify_svg(self, svg_string):
        """Removes newlines and excess whitespace to keep JSON clean."""
        return re.sub(r'>\s+<', '><', svg_string.strip())

    def get_shell_counts(self, z):
        """
        Calculates electrons per principal shell (K, L, M...) using Aufbau.
        Note: This produces a Bohr-like visualization, ignoring specific exceptions (Cr, Cu)
        for the sake of a consistent visual model.
        """
        shells = {}
        # Filling order (n, orb, capacity)
        # s=2, p=6, d=10, f=14
        order = [
            (1, 2), (2, 2), (2, 6), (3, 2), (3, 6), (4, 2), (3, 10), (4, 6),
            (5, 2), (4, 10), (5, 6), (6, 2), (4, 14), (5, 10), (6, 6), (7, 2),
            (5, 14), (6, 10), (7, 6)
        ]

        remaining = z
        for n, cap in order:
            if remaining <= 0: break
            take = min(remaining, cap)
            shells[n] = shells.get(n, 0) + take
            remaining -= take

        return [shells[k] for k in sorted(shells.keys())]

    def generate_icon_svg(self, z, symbol, name, mass):
        """Generates the Element Card SVG string."""
        # Determine background color by block (optional visual flair)
        # Using subtle CSS-friendly colors
        colors = {
            "s": "#ffadad", "p": "#9bf6ff", "d": "#fdffb6", "f": "#bdb2ff"
        }
        # We don't have block handy in this function args, default to grey
        fill = "#f0f0f0"

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <rect x="5" y="5" width="190" height="190" rx="15" ry="15" fill="#ffffff" stroke="#333" stroke-width="4"/>
  <text x="20" y="40" font-family="Arial, sans-serif" font-size="24" fill="#666">{z}</text>
  <text x="100" y="110" font-family="Arial, sans-serif" font-size="80" font-weight="bold" text-anchor="middle" fill="#000">{symbol}</text>
  <text x="100" y="150" font-family="Arial, sans-serif" font-size="18" text-anchor="middle" fill="#333">{name}</text>
  <text x="100" y="180" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#666">{mass}</text>
</svg>'''
        return self.minify_svg(svg)

    def generate_shell_svg(self, z, symbol):
        """Generates the Bohr Model SVG string."""
        cx, cy = 250, 250
        max_radius = 220
        svg_content = ""

        # Nucleus
        svg_content += f'<circle cx="{cx}" cy="{cy}" r="25" fill="#333" />'
        svg_content += f'<text x="{cx}" y="{cy+6}" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#fff" text-anchor="middle">{symbol}</text>'

        # Shells
        shell_counts = self.get_shell_counts(z)
        num_shells = len(shell_counts)
        base_radius = 50
        # Distribute shells evenly
        step = (max_radius - base_radius) / max(1, num_shells)

        for i, count in enumerate(shell_counts):
            r = base_radius + (i * step)
            # Draw Orbit Ring
            svg_content += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#ccc" stroke-width="2" />'

            # Draw Electrons
            if count > 0:
                angle_step = 360 / count
                for e in range(count):
                    # Start at -90deg (top)
                    angle = math.radians(e * angle_step - 90)
                    ex = cx + r * math.cos(angle)
                    ey = cy + r * math.sin(angle)
                    svg_content += f'<circle cx="{ex}" cy="{ey}" r="6" fill="#3498db" stroke="#fff" stroke-width="1"/>'

        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500">{svg_content}</svg>'
        return self.minify_svg(svg)

    def process_file(self, filename):
        try:
            with open(os.path.join(INPUT_DIR, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)

            ident = data.get("identity", {})
            media = data.get("media", {}).get("images", {})

            z = ident.get("atomic_number", 0)
            symbol = ident.get("symbol", "?")
            name = ident.get("name", "Unknown")
            mass_raw = ident.get("standard_atomic_weight", 0.0)

            # Format mass nicely
            try:
                mass_val = float(mass_raw)
                mass_str = f"{mass_val:.3f}"
            except:
                mass_str = str(mass_raw)

            # 1. Generate & Embed Icon SVG
            media["icon_symbol"] = self.generate_icon_svg(z, symbol, name, mass_str)

            # 2. Generate & Embed Shell SVG
            media["atom_2d_shell"] = self.generate_shell_svg(z, symbol)

            # 3. Ensure Spectrum Path is standardized (Asset Link)
            # We don't embed this, but we ensure the path points to the assets folder structure
            media["emission_spectrum_visible"] = f"assets/elements/spectra/{z}_{symbol}_visible.png"

            # Save back
            with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            self.stats["processed"] += 1
            self.stats["svgs_embedded"] += 2

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error processing {filename}: {e}")

    def run(self):
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        print(f"🎨 Densifying Media for {len(files)} elements...")

        for f in tqdm(files):
            self.process_file(f)

        print("DONE. Stats:")
        for k, v in self.stats.items(): print(f"  {k}: {v}")

if __name__ == "__main__":
    MediaDensifier().run()