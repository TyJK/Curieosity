#!/usr/bin/env python3
"""
Curieosity image render pass
============================
Produces the PNGs the game shows:
  assets/structures/{id}.png   2D structural diagram for each COMPOUND (RDKit from SMILES)
  assets/bohr/{Z}.png          Bohr-Rutherford diagram for each element Z=1..118 (procedural)

Bevy loads these by path (structures/{id}.png, bohr/{Z}.png) and falls back to a plain
tile if the file isn't there yet, so partial renders are fine. Re-runs skip existing files.

SMILES sources for compounds:
  * registry.json         (from compile_data.py)      -> id -> SMILES for curated + scraped
  * discovered_smiles.json (from resolve_reactions.py) -> id -> full SMILES for minted molecules

Run (structures for the base set + all Bohr diagrams):
    python3 render_structures.py --registry ./scratch/final/registry.json --assets ./assets
Add the discovered molecules too (slower; re-runs skip already-rendered files):
    python3 render_structures.py --registry ./scratch/final/registry.json \
        --discovered-smiles ./scratch/final/discovered_smiles.json --assets ./assets
Quick test (only the first N compounds):
    python3 render_structures.py --registry ./scratch/final/registry.json --assets ./assets --limit 80
"""

import argparse
import json
import math
import re
from pathlib import Path

from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit import RDLogger
from PIL import Image, ImageDraw

RDLogger.DisableLog("rdApp.*")

# curated compound ids (from compile_data's seed) that should get a structure image
CURATED_COMPOUND_IDS = {8, 10, 11, 12, 13}


def render_structure(smiles, path, size=220):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False
    d = rdMolDraw2D.MolDraw2DCairo(size, size)
    o = d.drawOptions()
    # White/bold on a fully transparent background so the diagram reads on the
    # dark UI palette without any card behind it.
    o.setBackgroundColour((0, 0, 0, 0))
    o.bondLineWidth = 3
    white = (1.0, 1.0, 1.0)
    palette = {i: white for i in range(1, 119)}
    palette[-1] = white  # default / unknown atoms
    o.updateAtomPalette(palette)
    d.DrawMolecule(mol)
    d.FinishDrawing()
    path.write_bytes(d.GetDrawingText())
    return True


# --- Bohr diagram (procedural, transparent background) -----------------------------
def shell_counts(z):
    order = [(1, 2), (2, 2), (2, 6), (3, 2), (3, 6), (4, 2), (3, 10), (4, 6), (5, 2),
             (4, 10), (5, 6), (6, 2), (4, 14), (5, 10), (6, 6), (7, 2), (5, 14), (6, 10), (7, 6)]
    rem, sh = z, {}
    for n, cap in order:
        if rem <= 0:
            break
        take = min(rem, cap)
        sh[n] = sh.get(n, 0) + take
        rem -= take
    return [sh[k] for k in sorted(sh)]


def render_bohr(z, path, size=220):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx = cy = size / 2
    dr.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(70, 70, 78, 255))
    counts = shell_counts(z)
    base, span = 28, (size / 2 - 30)
    step = span / max(1, len(counts))
    for i, c in enumerate(counts):
        r = base + i * step
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(170, 175, 190, 200), width=1)
        for e in range(c):
            a = math.radians(e * 360.0 / c - 90)
            ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
            dr.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(90, 160, 240, 255))
    path.write_bytes(_png_bytes(img))


def _png_bytes(img):
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# --- id -> SMILES sources ----------------------------------------------------------
def compound_smiles(registry_path, discovered_smiles_path, authored_smiles_path=None):
    reg = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    id_to_smiles = {}
    for smi, sid in reg["by_smiles"].items():
        if sid >= 2000 or sid in CURATED_COMPOUND_IDS:  # compounds only (skip elements/element-block)
            id_to_smiles[int(sid)] = smi
    # Authored materials (100-599), keyed by id so a common SMILES that also exists in the
    # scrape (SiO2, ZnCO3, ...) can't shadow them out of the registry.
    if authored_smiles_path and Path(authored_smiles_path).exists():
        am = json.loads(Path(authored_smiles_path).read_text(encoding="utf-8"))
        for sid, smi in am.items():
            id_to_smiles[int(sid)] = smi
    # Minted "discovered" molecules: full canonical SMILES from resolve_reactions.py's
    # discovered_smiles.json (their stored *name* is truncated and can't be parsed).
    if discovered_smiles_path and Path(discovered_smiles_path).exists():
        dm = json.loads(Path(discovered_smiles_path).read_text(encoding="utf-8"))
        for sid, smi in dm.items():
            id_to_smiles[int(sid)] = smi
    return id_to_smiles


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--discovered-smiles", dest="discovered_smiles", type=Path,
                    help="discovered_smiles.json from resolve_reactions.py (id -> full SMILES "
                         "for the minted compounds)")
    ap.add_argument("--authored-smiles", dest="authored_smiles", type=Path,
                    help="authored_smiles.json from compile_data.py (id -> SMILES for the "
                         "authored tech-tree materials)")
    ap.add_argument("--assets", type=Path, required=True, help="the game's assets/ dir")
    ap.add_argument("--limit", type=int, help="only render the first N compounds (for testing)")
    ap.add_argument("--no-bohr", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="overwrite existing PNGs (needed to re-render after a style change)")
    args = ap.parse_args()

    structures_dir = args.assets / "structures"
    bohr_dir = args.assets / "bohr"
    structures_dir.mkdir(parents=True, exist_ok=True)
    bohr_dir.mkdir(parents=True, exist_ok=True)

    # 1) Bohr diagrams (fast; 118 files)
    if not args.no_bohr:
        n_bohr = 0
        for z in range(1, 119):
            p = bohr_dir / f"{z}.png"
            if p.exists() and not args.force:
                continue
            render_bohr(z, p)
            n_bohr += 1
        print(f"bohr: {n_bohr} rendered (of 118) -> {bohr_dir}")

    # 2) compound structures
    smiles = compound_smiles(args.registry, args.discovered_smiles, args.authored_smiles)
    ids = sorted(smiles)
    if args.limit:
        ids = ids[:args.limit]
    done = skipped = failed = 0
    for i, sid in enumerate(ids):
        p = structures_dir / f"{sid}.png"
        if p.exists() and not args.force:
            skipped += 1
            continue
        if render_structure(smiles[sid], p):
            done += 1
        else:
            failed += 1
        if (i + 1) % 1000 == 0:
            print(f"  ...{i + 1:,}/{len(ids):,} compounds", flush=True)
    print(f"structures: {done:,} rendered, {skipped:,} already existed, {failed:,} failed "
          f"-> {structures_dir}")


if __name__ == "__main__":
    main()