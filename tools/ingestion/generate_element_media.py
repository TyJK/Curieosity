import json
import math
import os
import re
import time
import logging
import requests
import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sp
from skimage import measure
from mendeleev import element as get_element_by_id
from tqdm import tqdm
from io import StringIO
import pandas as pd

# --- CONFIGURATION ---
INPUT_DIR = os.path.normpath("./tools/data/02_element_media")
OUTPUT_DIR = os.path.normpath("./tools/data/03_element_complete")
ASSETS_DIR = os.path.normpath("./assets/elements")
LOG_DIR = "./tools/logs"

# Asset Subdirectories
SPECTRA_DIR = os.path.join(ASSETS_DIR, "spectra")
MODELS_DIR = os.path.join(ASSETS_DIR, "models")
os.makedirs(SPECTRA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[logging.FileHandler(f"{LOG_DIR}/real_media_gen.log", mode='w', encoding='utf-8')]
)
logger = logging.getLogger("RealMedia")

# --- UTILITIES ---

def wavelength_to_rgb(wavelength, gamma=0.8):
    '''This converts a given wavelength of light to an approximate RGB color value.'''
    wavelength = float(wavelength)
    if wavelength >= 380 and wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = (-(wavelength - 440) / (440 - 380)) * attenuation
        G = 0.0
        B = 1.0 * attenuation
    elif wavelength >= 440 and wavelength <= 490:
        R = 0.0
        G = (wavelength - 440) / (490 - 440)
        B = 1.0
    elif wavelength >= 490 and wavelength <= 510:
        R = 0.0
        G = 1.0
        B = (-(wavelength - 510) / (510 - 490))
    elif wavelength >= 510 and wavelength <= 580:
        R = (wavelength - 510) / (580 - 510)
        G = 1.0
        B = 0.0
    elif wavelength >= 580 and wavelength <= 645:
        R = 1.0
        G = (-(wavelength - 645) / (645 - 580))
        B = 0.0
    elif wavelength >= 645 and wavelength <= 750:
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = 1.0 * attenuation
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0
    return (R, G, B)

# --- GENERATORS ---

class SpectraGenerator:
    NIST_URL = "https://physics.nist.gov/cgi-bin/ASD/lines1.pl"

    def generate(self, atomic_number, symbol, save_path):
        if os.path.exists(save_path): return True # Skip if exists

        # Query NIST for Neutral Atom (I) lines in visible range
        params = {
            'spectra': f"{symbol} I",
            'low_w': 380, 'upp_w': 750, 'unit': 1, # nm
            'format': 3, # CSV-like with quotes
            'line_out': 0, 'en_unit': 1, 'output_type': 0, 'bibrefs': 0, 'show_av': 3
        }

        try:
            # Polite delay
            time.sleep(0.5)
            resp = requests.get(self.NIST_URL, params=params, timeout=10)

            if resp.status_code != 200: return False

            # Simple parsing: Find lines starting with numbers
            lines = []
            content = resp.text
            # NIST "CSV" is messy. Robust parse:
            # Look for: "wavelength","ritz_wl","rel_int"

            # Use Pandas for robustness if possible, or regex
            # Regex for lines:  388.905,   1000, ...
            matches = re.findall(r'^\s*([0-9.]+),"\s*([0-9.]+)?",\s*"([A-Za-z0-9]+)"', content, re.MULTILINE)
            # Fallback regex for simpler format
            if not matches:
                matches = re.findall(r'^\s*([0-9.]+)\s+([0-9.]+)?\s+([A-Za-z0-9]+)', content, re.MULTILINE)

            spectral_data = []
            for m in matches:
                try:
                    wl = float(m[0])
                    # Intensity often has chars like '1000' or '500*'
                    inten_raw = re.sub(r'[^0-9]', '', m[2])
                    inten = float(inten_raw) if inten_raw else 10.0
                    spectral_data.append((wl, inten))
                except: continue

            if not spectral_data:
                # Create empty black placeholder if no lines (e.g. some actinides)
                self._render_plot([], save_path)
                return True

            self._render_plot(spectral_data, save_path)
            return True

        except Exception as e:
            logger.error(f"Spectra error {symbol}: {e}")
            return False

    def _render_plot(self, lines, path):
        fig, ax = plt.subplots(figsize=(8, 1), dpi=100)
        ax.set_facecolor('black')
        ax.set_xlim(380, 750)
        ax.set_ylim(0, 1)
        ax.axis('off')

        # Max intensity for normalization
        max_i = max([l[1] for l in lines]) if lines else 1.0

        for wl, inten in lines:
            color = wavelength_to_rgb(wl)
            # Logarithmic scaling for better visibility of weak lines
            alpha = min(1.0, 0.2 + 0.8 * (math.log(inten+1) / math.log(max_i+1)))
            ax.axvline(x=wl, color=color, linewidth=1.5, alpha=alpha)
            # Add a "glow"
            ax.axvline(x=wl, color=color, linewidth=4.0, alpha=alpha*0.3)

        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        plt.savefig(path, facecolor='black')
        plt.close(fig)

class OrbitalGenerator:
    def generate(self, block, save_path):
        if os.path.exists(save_path): return True

        # Quantum Numbers
        if block == 's': n, l, m = 1, 0, 0
        elif block == 'p': n, l, m = 2, 1, 0
        elif block == 'd': n, l, m = 3, 2, 0
        elif block == 'f': n, l, m = 4, 3, 0
        else: return False

        # Grid
        grid_size = 50
        L = 10 if n < 4 else 16
        x, y, z = np.mgrid[-L:L:grid_size*1j, -L:L:grid_size*1j, -L:L:grid_size*1j]

        # Coordinates
        r = np.sqrt(x**2 + y**2 + z**2)
        theta = np.arccos(z / (r + 1e-9))
        phi = np.arctan2(y, x)

        # Wavefunction (Hydrogen-like Angular part + Simplified Radial)
        # We focus on angular shape Y_lm for visualization
        Y_lm = sp.sph_harm(m, l, phi, theta)

        # Simplified Radial decay
        R_nl = np.exp(-r/n) * (r**l)

        psi = R_nl * Y_lm.real # Real part for iso-surface

        # Isosurface
        try:
            verts, faces, _, _ = measure.marching_cubes(np.abs(psi), 0.02)
            self._save_obj(verts, faces, save_path)
            return True
        except: return False

    def _save_obj(self, verts, faces, path):
        with open(path, 'w') as f:
            f.write(f"# Orbital Model\n")
            for v in verts:
                f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
            for face in faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

class LatticeGenerator:
    def generate(self, structure, param, save_path):
        # We generate a simple Unit Cell representation
        if os.path.exists(save_path): return True
        if not structure or structure == "Unknown": return False

        # Define Basis Atoms
        atoms = [] # (x,y,z)

        s = str(structure).upper()

        # Scale: param is in Angstroms. We stick to that scale.
        a = param if param else 3.5

        if "FCC" in s:
            atoms = [(0,0,0), (0.5,0.5,0), (0.5,0,0.5), (0,0.5,0.5)]
        elif "BCC" in s:
            atoms = [(0,0,0), (0.5,0.5,0.5)]
        elif "SC" in s or "CUBIC" in s:
            atoms = [(0,0,0)]
        elif "HCP" in s:
            # Simplified Hexagonal
            atoms = [(0,0,0), (0.333, 0.666, 0.5)]
        elif "DIAMOND" in s:
            atoms = [(0,0,0), (0.5,0.5,0), (0.5,0,0.5), (0,0.5,0.5),
                     (0.25,0.25,0.25), (0.75,0.75,0.25), (0.75,0.25,0.75), (0.25,0.75,0.75)]
        else:
            # Default to simple representation
            atoms = [(0,0,0)]

        # Generate OBJ (Spheres at positions)
        self._write_atoms_obj(atoms, a, save_path)
        return True

    def _write_atoms_obj(self, atoms, scale, path):
        # Generate a low-poly sphere for each atom
        # Sphere prototype (Icosahedron-ish)
        phi = (1 + np.sqrt(5)) / 2
        base_verts = [
            (-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
            (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
            (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1)
        ]
        # Just use points for atomic positions if we want efficient files
        # Or simplistic cubes.
        # Let's write simple cubes for "lattice points" to save space/time,
        # as drawing full spheres in python without a library is verbose.

        with open(path, 'w') as f:
            f.write(f"# Lattice {scale}\n")
            v_offset = 1
            r = 0.2 * scale # Atom radius relative to cell

            # Simple Cube Mesh for Atom
            cube_v = [(r,r,r),(r,r,-r),(r,-r,r),(r,-r,-r),(-r,r,r),(-r,r,-r),(-r,-r,r),(-r,-r,-r)]
            cube_f = [(1,2,4,3), (3,4,8,7), (7,8,6,5), (5,6,2,1), (3,7,5,1), (8,4,2,6)]

            for (ax, ay, az) in atoms:
                # Scaled position
                px, py, pz = ax*scale, ay*scale, az*scale

                for (vx, vy, vz) in cube_v:
                    f.write(f"v {px+vx:.3f} {py+vy:.3f} {pz+vz:.3f}\n")

                for face in cube_f:
                    # OBJ is 1-indexed
                    f.write(f"f {face[0]+v_offset-1} {face[1]+v_offset-1} {face[2]+v_offset-1} {face[3]+v_offset-1}\n")

                v_offset += 8

# --- MAIN ---

def run():
    spectra_gen = SpectraGenerator()
    orbital_gen = OrbitalGenerator()
    lattice_gen = LatticeGenerator()

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    print(f"🏭 Manufacturing Real Assets for {len(files)} elements...")

    for filename in tqdm(files):
        try:
            with open(os.path.join(INPUT_DIR, filename), 'r') as f:
                data = json.load(f)

            ident = data["identity"]
            media = data["media"]
            q_mech = data.get("quantum_mechanics", {})

            z = ident["atomic_number"]
            sym = ident["symbol"]
            block = ident.get("block", "s")

            # 1. Spectra
            spec_path = os.path.join(SPECTRA_DIR, f"{z}_{sym}_visible.png")
            if spectra_gen.generate(z, sym, spec_path):
                media["images"]["emission_spectrum_visible"] = f"assets/elements/spectra/{z}_{sym}_visible.png"

            # 2. Orbital (Generic per block)
            orb_path = os.path.join(MODELS_DIR, f"orbital_{block}.obj")
            if orbital_gen.generate(block, orb_path):
                media["models_3d"]["orbital_visualization"] = f"assets/elements/models/orbital_{block}.obj"

            # 3. Lattice
            # Fetch structure info from Mendeleev
            el = get_element_by_id(z)
            struct = el.lattice_structure
            const = el.lattice_constant

            if struct:
                lat_filename = f"lattice_{struct.lower()}.obj"
                lat_path = os.path.join(MODELS_DIR, lat_filename)
                # We use a generic name so FCC elements share the FCC model file if parameter is generic,
                # BUT if we want accuracy we should name it by element.
                # Let's do generic to save space for now, or per element?
                # User said "actually download". Let's do per-element scaled.
                lat_filename = f"{z}_{sym}_lattice_{struct.lower()}.obj"
                lat_path = os.path.join(MODELS_DIR, lat_filename)

                if lattice_gen.generate(struct, const, lat_path):
                    media["models_3d"]["standard_state_lattice"] = f"assets/elements/models/{lat_filename}"

            # Save
            with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed {filename}: {e}")

if __name__ == "__main__":
    run()