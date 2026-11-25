"""
Draws the Bohr-model pictures the Substance Library shows for elements: assets/bohr/<Z>.png,
220 x 220, transparent; a dark nucleus, one thin ring per shell, and the shell's electrons as
blue dots spread evenly round it from the top. Shell occupancies come from each element's
electron configuration in library/substances.ron.

    python tools/art/gen_bohr.py           # draw the pictures that are missing
    python tools/art/gen_bohr.py --force   # redraw all 118
"""
import argparse
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "bohr"
SIZE = 220
C = SIZE / 2
NUCLEUS, NUCLEUS_R = (70, 70, 78, 255), 15.5
RING = (170, 175, 190, 200)
ELECTRON, ELECTRON_R = (90, 160, 240, 255), 4.5
FIRST, LAST, MAX_STEP = 28.0, 95.0, 40.0
CORES = {"He": 2, "Ne": 10, "Ar": 18, "Kr": 36, "Xe": 54, "Rn": 86}


def configs():
    """Z -> electron configuration ("[Ar] 3d5 4s"), read from the library's element entries."""
    text = (ROOT / "library" / "substances.ron").read_text(encoding="utf-8")
    out = {}
    for block in re.findall(r"element_info: Some\(\((.*?)\)\)", text, re.S):
        z = re.search(r"atomic_number: (\d+)", block)
        cfg = re.search(r'electron_config: (?:Some\()?"([^"]*)"', block)
        if z and cfg:
            out[int(z.group(1))] = cfg.group(1)
    return out


def shells(z, cfg):
    """Electrons per shell (n = 1, 2, ...) for a configuration, expanding the noble-gas core."""
    by_n = {}
    for tok in cfg.split():
        core = re.fullmatch(r"\[(\w+)\]", tok)
        if core:
            for n, k in enumerate(shells(CORES[core.group(1)], CFG[CORES[core.group(1)]]), start=1):
                by_n[n] = by_n.get(n, 0) + k
            continue
        m = re.fullmatch(r"(\d)([spdf])(\d*)", tok)
        if not m:
            raise ValueError(f"Z={z}: can't read {tok!r} in {cfg!r}")
        n, k = int(m.group(1)), int(m.group(3) or 1)
        by_n[n] = by_n.get(n, 0) + k
    counts = [by_n.get(n, 0) for n in range(1, max(by_n) + 1)]
    if sum(counts) != z:
        raise ValueError(f"Z={z}: {cfg!r} holds {sum(counts)} electrons")
    return counts


def draw(counts):
    im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    n = len(counts)
    step = min(MAX_STEP, (LAST - FIRST) / (n - 1)) if n > 1 else 0.0
    for i, k in enumerate(counts):
        r = FIRST + i * step
        d.ellipse((C - r, C - r, C + r, C + r), outline=RING, width=1)
        for j in range(k):
            a = -math.pi / 2 + 2 * math.pi * j / k
            x, y = C + r * math.cos(a), C + r * math.sin(a)
            d.ellipse((x - ELECTRON_R, y - ELECTRON_R, x + ELECTRON_R, y + ELECTRON_R), fill=ELECTRON)
    d.ellipse((C - NUCLEUS_R, C - NUCLEUS_R, C + NUCLEUS_R, C + NUCLEUS_R), fill=NUCLEUS)
    return im


CFG = {}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="redraw the pictures that exist too")
    args = ap.parse_args()
    CFG.update(configs())
    OUT.mkdir(parents=True, exist_ok=True)
    drawn = kept = 0
    for z in range(1, 119):
        p = OUT / f"{z}.png"
        if p.exists() and not args.force:
            kept += 1
            continue
        draw(shells(z, CFG[z])).save(p)
        drawn += 1
    print(f"bohr: {drawn} drawn, {kept} kept -> {OUT}")


if __name__ == "__main__":
    main()
