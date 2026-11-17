"""
Draws the Steam art in the game's line-art style, into steam/, and the Android app icon:

    steam/achievements/<API_NAME>_ACHIEVED.png   one 256x256 icon per achievement
    steam/store/*.png                            the store and library capsules, the
                                                 library hero and logo, the page background,
                                                 the community icon and the client icon
    android/app/src/main/res/drawable-nodpi/ic_launcher_foreground.png
                                                 the logo layer of the Android icon (its
                                                 background is a colour, in values/colors.xml)

The achievements come from steam/achievements.csv (which `cargo test` keeps in step with
the game's milestones and eras). An icon shows the vessel its milestone unlocks, else the
milestone's substance; eras show their numeral. Steam makes the grey "unachieved" icons
itself (tick "Automatically generate unachieved icons" when uploading).

    python tools/art/gen_steam_art.py

Needs Pillow, and cairosvg (pip install cairosvg) or the rsvg-convert command to draw the
vessel line art, as gen_vessels.py does.
"""
import csv
import io
import math
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from gen_vessels import PROCESS  # noqa: E402  (vessel -> title, process, accent, contents colours)

OUT = ROOT / "steam"
VESSEL_SVG = ROOT / "assets" / "images" / "vessels"
LOGO_SVG = ROOT / "assets" / "images" / "ui" / "logo.svg"
FONT_BOLD = ROOT / "assets" / "fonts" / "NotoSans-Bold.ttf"

# the game's palette (src/ui/theme.rs)
BG = (7, 9, 20)
SURFACE = (17, 22, 43)
LINE = (42, 53, 96)
TEXT = (238, 241, 250)
CYAN = (90, 214, 230)
VIOLET = (160, 112, 255)
GOLD = (242, 193, 78)
GREEN = (91, 227, 154)

# vessels in the order the game unlocks them, for rows of art
PARADE = ["fire", "mortar", "bloomery", "fermenter", "still", "ice_bath", "flask", "irradiator",
          "blast_furnace", "polymer_reactor", "voltaic_cell", "catalyst_bed", "column", "arc_furnace",
          "cracker", "bioreactor", "crystal_puller", "cvd_chamber", "nuclear_reactor", "cyclotron"]


# --- drawing helpers ---------------------------------------------------------------------
def svg_to_image(svg_text, px):
    """Rasterise SVG text to a px x px RGBA image."""
    try:
        import cairosvg
        png = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=px, output_height=px)
    except ImportError:
        exe = shutil.which("rsvg-convert")
        if not exe:
            sys.exit("no SVG rasteriser: pip install cairosvg (or install rsvg-convert)")
        png = subprocess.run([exe, "-w", str(px), "-h", str(px)], input=svg_text.encode(),
                             capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGBA")


def rgb255(c):
    return tuple(int(round(v * 255)) for v in c)


def hexc(c):
    return "#%02x%02x%02x" % c


def vessel(name, px):
    """A vessel in its colours: contents, outline and accent layers."""
    _, pc, ac, fc = PROCESS[name]
    art = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    for layer, colour, alpha in (("fill", fc, 0.92), ("outline", pc, 1.0), ("accent", ac, 0.95)):
        p = VESSEL_SVG / f"{name}_{layer}.svg"
        if not p.exists():
            continue
        svg = p.read_text().replace('"#fff"', f'"{hexc(rgb255(colour))}"').replace('"#ffffff"', f'"{hexc(rgb255(colour))}"')
        im = svg_to_image(svg, px)
        if alpha < 1:
            im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
        art.alpha_composite(im)
    return art


def logo(px):
    return svg_to_image(LOGO_SVG.read_text(), px)


def font(size):
    return ImageFont.truetype(str(FONT_BOLD), size)


def background(w, h, glow=None, grid=True):
    """The bench: deep blue-black, a faint dot grid, and an optional soft glow."""
    img = Image.new("RGBA", (w, h), BG + (255,))
    if glow:
        (gx, gy, r, colour) = glow
        g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([gx - r, gy - r, gx + r, gy + r], fill=colour + (90,))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * 0.6)))
    if grid:
        step = max(18, min(w, h) // 22)
        dots = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(dots)
        rad = max(1, step // 14)
        for y in range(step // 2, h, step):
            for x in range(step // 2, w, step):
                d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=LINE + (150,))
        img.alpha_composite(dots)
    return img


def wordmark(img, cx, cy, height, with_logo=True):
    """The flask logo and "Curieosity", centred on (cx, cy)."""
    f = font(int(height))
    d = ImageDraw.Draw(img)
    l, t, r, b = d.textbbox((0, 0), "Curieosity", font=f)
    tw, th = r - l, b - t
    lp = int(height * 1.25) if with_logo else 0
    gap = int(height * 0.25) if with_logo else 0
    x0 = int(cx - (lp + gap + tw) / 2)
    if with_logo:
        img.alpha_composite(logo(lp), (x0, int(cy - lp / 2)))
    d.text((x0 + lp + gap - l, cy - th / 2 - t), "Curieosity", font=f, fill=TEXT + (255,))


def parade(img, names, cx, cy, size, gap, fade=1.0):
    total = len(names) * size + (len(names) - 1) * gap
    x = int(cx - total / 2)
    for n in names:
        v = vessel(n, size)
        if fade < 1:
            v.putalpha(v.getchannel("A").point(lambda a: int(a * fade)))
        img.alpha_composite(v, (x, int(cy - size / 2)))
        x += size + gap


def grid_of(img, names, x0, y0, cols, size, gap):
    for i, n in enumerate(names):
        img.alpha_composite(vessel(n, size), (x0 + (i % cols) * (size + gap), y0 + (i // cols) * (size + gap)))


# --- achievements ------------------------------------------------------------------------
def formula_text(d, cx, cy, formula, size, colour):
    """A formula with its digits set as subscripts, centred."""
    big, small = font(size), font(int(size * 0.62))
    parts = [(ch, small if ch.isdigit() else big) for ch in formula]
    width = sum(d.textlength(ch, font=f) for ch, f in parts)
    x = cx - width / 2
    for ch, f in parts:
        dy = size * 0.28 if f is small else 0
        bb = d.textbbox((0, 0), "C", font=big)
        d.text((x, cy - (bb[3] + bb[1]) / 2 + dy), ch, font=f, fill=colour + (255,))
        x += d.textlength(ch, font=f)


def fit_words(d, text, max_w, size):
    while size > 18:
        f = font(size)
        words, lines, cur = text.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= max_w:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        if len(lines) <= 2 and all(d.textlength(line, font=f) <= max_w for line in lines):
            return f, [line for line in lines if line]
        size -= 2
    return font(18), [text]


def achievement_icon(row):
    S, K = 256, 4  # drawn at 4x, then scaled down for smooth circles
    big = Image.new("RGBA", (S * K, S * K), SURFACE + (255,))
    d = ImageDraw.Draw(big)
    kind, _, arg = row["art"].partition(":")
    if kind == "vessel":
        accent = rgb255(PROCESS[arg][1])
    elif kind == "era":
        accent = CYAN
    elif kind == "count":
        accent = VIOLET if arg == "25" else GREEN
    else:
        accent = GOLD
    c, r = S * K / 2, 108 * K
    glow = Image.new("RGBA", big.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([c - r, c - r, c + r, c + r], fill=accent + (60,))
    big.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40 * K // 4)))
    d.ellipse([c - r, c - r, c + r, c + r], fill=BG + (255,), outline=accent + (255,), width=8 * K)
    img = big.resize((S, S), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    if kind == "vessel":
        v = vessel(arg, 150)
        img.alpha_composite(v, ((S - 150) // 2, (S - 150) // 2))
    elif kind == "era":
        f = font(26)
        w = d.textlength("ERA", font=f)
        d.text(((S - w) / 2, 66), "ERA", font=f, fill=accent + (255,))
        f = font(88)
        w = d.textlength(arg, font=f)
        d.text(((S - w) / 2, 92), arg, font=f, fill=TEXT + (255,))
    elif kind == "count":
        f = font(96 if len(arg) <= 2 else 64)
        bb = d.textbbox((0, 0), arg, font=f)
        d.text(((S - (bb[2] - bb[0])) / 2 - bb[0], (S - (bb[3] - bb[1])) / 2 - bb[1]), arg, font=f, fill=TEXT + (255,))
    else:
        sid, _, formula = arg.partition(":")
        if formula[:1].isupper() and len(formula) <= 8 and formula.isalnum():
            formula_text(d, S / 2, S / 2, formula, 76 if len(formula) <= 3 else (56 if len(formula) <= 5 else 44), accent)
        else:
            f, lines = fit_words(d, row["name"], 170, 40)
            lh = f.size * 1.15
            y = S / 2 - lh * len(lines) / 2
            for line in lines:
                w = d.textlength(line, font=f)
                d.text(((S - w) / 2, y), line, font=f, fill=accent + (255,))
                y += lh
    return img.convert("RGB")


# --- store and library -------------------------------------------------------------------
def store_art():
    out = {}

    def capsule(w, h, logo_h, row, glow_r=None):
        img = background(w, h, glow=(w // 2, int(h * 0.42), glow_r or h // 2, VIOLET))
        wordmark(img, w / 2, h * 0.36, logo_h)
        if row:
            size = row
            n = max(3, min(len(PARADE), int((w * 0.9) // (size * 1.35))))
            parade(img, PARADE[:: max(1, len(PARADE) // n)][:n], w / 2, h * 0.76, size, int(size * 0.3))
        return img

    out["header_capsule.png"] = capsule(920, 430, 92, 100)
    out["library_header.png"] = capsule(920, 430, 92, 100)
    out["main_capsule.png"] = capsule(1232, 706, 122, 128)
    small = background(462, 174, glow=(231, 87, 120, VIOLET), grid=False)
    wordmark(small, 231, 87, 58)
    out["small_capsule.png"] = small

    def tall(w, h):
        img = background(w, h, glow=(w // 2, int(h * 0.2), w // 2, VIOLET))
        lp = int(w * 0.26)
        img.alpha_composite(logo(lp), ((w - lp) // 2, int(h * 0.08)))
        d = ImageDraw.Draw(img)
        f = font(int(w * 0.135))
        bb = d.textbbox((0, 0), "Curieosity", font=f)
        d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], h * 0.08 + lp + h * 0.03 - bb[1]), "Curieosity", font=f, fill=TEXT + (255,))
        y0 = int(h * 0.5)
        gap = int(w * 0.06)
        size = min(int(w * 0.2), (int(h * 0.95) - y0 - 2 * gap) // 3)
        x0 = (w - (3 * size + 2 * gap)) // 2
        grid_of(img, PARADE[::2][:9], x0, y0, 3, size, gap)
        return img

    out["vertical_capsule.png"] = tall(748, 896)
    out["library_capsule.png"] = tall(600, 900)

    hero = background(3840, 1240, glow=(1920, 620, 700, CYAN))
    parade(hero, PARADE[:13], 1920, 620, 230, 60)
    out["library_hero.png"] = hero

    lg = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    wordmark(lg, 640, 360, 170)
    out["library_logo.png"] = lg

    page = background(1438, 810, glow=(719, 405, 500, VIOLET))
    parade(page, PARADE[1:12], 719, 650, 90, 30, fade=0.35)
    out["page_background.png"] = page

    icon = background(184, 184, glow=(92, 92, 80, VIOLET), grid=False)
    icon.alpha_composite(logo(136), (24, 24))
    out["community_icon.jpg"] = icon
    out["client_icon.ico"] = logo(256)
    return out


def android_icon():
    """The front layer of Android's adaptive icon: 108 dp square, of which launchers show
    the middle 72 dp (cut to a circle or a rounded square). The logo keeps inside 60 dp."""
    px = 432  # 108 dp at the densest screens
    layer = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    glow = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((96, 96, px - 96, px - 96), fill=VIOLET + (90,))
    layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
    size = 240
    layer.alpha_composite(logo(size), ((px - size) // 2, (px - size) // 2))
    return layer


def main():
    rows = list(csv.DictReader((OUT / "achievements.csv").open(encoding="utf-8")))
    (OUT / "achievements").mkdir(parents=True, exist_ok=True)
    for row in rows:
        achievement_icon(row).save(OUT / "achievements" / row["icon"])
    print(f"{len(rows)} achievement icons -> steam/achievements/")
    (OUT / "store").mkdir(parents=True, exist_ok=True)
    for name, img in store_art().items():
        p = OUT / "store" / name
        if name.endswith(".jpg"):
            img.convert("RGB").save(p, quality=92)
        elif name.endswith(".ico"):
            img.save(p, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (256, 256)])
        else:
            img.save(p)
        print(f"  steam/store/{name}  {img.size[0]}x{img.size[1]}")
    icon = ROOT / "android" / "app" / "src" / "main" / "res" / "drawable-nodpi" / "ic_launcher_foreground.png"
    icon.parent.mkdir(parents=True, exist_ok=True)
    android_icon().save(icon)
    print(f"  {icon.relative_to(ROOT).as_posix()}  432x432")


if __name__ == "__main__":
    main()
