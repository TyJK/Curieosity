#!/usr/bin/env python3
"""
Curieosity vessel and UI art
============================
Draws the twenty-seven vessels and the interface icons as SVG line art, programmatically: every
shape below is plain geometry, so the set stays consistent (one stroke weight, one corner
style, one light direction) and anything can be tweaked by editing numbers.

Each vessel has up to three layers, all drawn in white so the game can tint them:

  {name}_outline   the vessel itself (tinted with the vessel's process colour or white)
  {name}_fill      what is inside it (tinted with the colour of the contents)
  {name}_accent    flame, frost, rays, bubbles... (tinted per vessel, animated in game)

Output: assets/images/vessels/{name}_{layer}.svg and .png (256 px, 2x the 128 px design
grid; Bevy cannot load SVG). Also writes a preview sheet with --preview PATH.

    python tools/art/gen_vessels.py                     # SVG + PNG
    python tools/art/gen_vessels.py --preview out.png   # plus a tinted preview sheet

The UI icons (gear, search, lock...) go to assets/images/ui/{name}.png at 64 px, also
white for tinting, together with the bench grid texture and the window logo.

PNG export uses cairosvg if it is installed (pip install cairosvg), otherwise the
rsvg-convert command. If neither exists, only the SVGs are written.
"""

import argparse
import math
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / "assets" / "images" / "vessels"

GRID = 128          # design grid
PX = 256            # exported size (2x)
SW = 3.4            # stroke width on the grid
STYLE = (f'fill="none" stroke="#fff" stroke-width="{SW}" stroke-linecap="round" '
         f'stroke-linejoin="round"')
THIN = (f'fill="none" stroke="#fff" stroke-width="{SW * 0.55:.2f}" stroke-linecap="round" '
        f'stroke-linejoin="round"')
SOLID = 'fill="#fff" stroke="none"'


def svg(*parts):
    body = "\n  ".join(p for p in parts if p)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {GRID} {GRID}" '
            f'width="{PX}" height="{PX}">\n  {body}\n</svg>\n')


def path(d, style=STYLE, extra=""):
    return f'<path d="{d}" {style} {extra}/>'


def circle(cx, cy, r, style=STYLE, extra=""):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" {style} {extra}/>'


def ellipse(cx, cy, rx, ry, style=STYLE, extra=""):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" {style} {extra}/>'


def rect(x, y, w, h, r=0, style=STYLE, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" {style} {extra}/>'


def line(x1, y1, x2, y2, style=STYLE, extra=""):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {style} {extra}/>'


def sheen(d):
    """a glass highlight: a short soft stroke on the upper-left of glassware"""
    return path(d, THIN, 'opacity="0.55"')


def flame(cx, base, h, w):
    """a teardrop flame standing on (cx, base)"""
    t = base - h
    return (f"M{cx} {base} C{cx - w} {base} {cx - w * 1.05} {base - h * 0.45} {cx - w * 0.35} {base - h * 0.7} "
            f"C{cx - w * 0.1} {base - h * 0.82} {cx - w * 0.05} {t + h * 0.08} {cx + w * 0.1} {t} "
            f"C{cx + w * 0.25} {base - h * 0.62} {cx + w * 1.05} {base - h * 0.5} {cx + w * 0.9} {base - h * 0.2} "
            f"C{cx + w * 0.8} {base - h * 0.02} {cx + w * 0.4} {base} {cx} {base} Z")


# --------------------------------------------------------------------------------------
# The vessels. Each returns {"outline": [...], "fill": [...], "accent": [...]}.
# --------------------------------------------------------------------------------------
def mortar():
    bowl = "M22 62 C22 88 38 104 56 105 L72 105 C90 104 106 88 106 62"
    outline = [
        # pestle behind the rim
        '<g transform="translate(78 40) rotate(28)">' +
        path("M-4.5 -30 L4.5 -30 C5.5 -10 7.5 6 8.5 16 C9.5 25 -9.5 25 -8.5 16 C-7.5 6 -5.5 -10 -4.5 -30 Z") +
        "</g>",
        path(bowl),
        ellipse(64, 62, 42, 7),
        path("M50 105 L48 113 L80 113 L78 105"),
        path("M30 72 C33 86 42 96 54 98", THIN, 'opacity="0.55"'),
    ]
    fill = [path("M27 70 C30 90 44 101 57 101.5 L71 101.5 C84 101 98 90 101 70 "
                 "C84 76 44 76 27 70 Z", SOLID)]
    # grinding: a motion arc around the pestle head and a few flying grains
    accent = [path("M84 16 C94 20 98 28 96 36", THIN), path("M90 12 C102 18 106 30 102 40", THIN, 'opacity="0.55"'),
              circle(36, 50, 1.7, SOLID), circle(44, 44, 1.3, SOLID), circle(30, 44, 1.1, SOLID, 'opacity="0.7"'),
              circle(98, 52, 1.4, SOLID, 'opacity="0.8"')]
    return dict(outline=outline, fill=fill, accent=accent)


def fire():
    outline = [
        # crucible
        path("M40 34 L88 34 L81 64 C76 69 52 69 47 64 Z"),
        line(37, 34, 91, 34),
        sheen("M47 40 L51 58"),
        # tripod ring and legs
        ellipse(64, 70, 30, 4.5),
        path("M40 72 L28 110"), path("M88 72 L100 110"),
        # logs
        path("M30 116 L82 104", STYLE), path("M98 116 L46 104", STYLE),
        circle(30, 116, 2.4, SOLID), circle(98, 116, 2.4, SOLID),
    ]
    fill = [path("M44.5 42 L83.5 42 L78.6 62 C74 66 54 66 49.4 62 Z", SOLID)]
    accent = [path(flame(64, 104, 30, 13), SOLID),
              path(flame(50, 106, 16, 7), SOLID, 'opacity="0.85"'),
              path(flame(78, 106, 18, 7.5), SOLID, 'opacity="0.85"')]
    return dict(outline=outline, fill=fill, accent=accent)


def ice_bath():
    outline = [
        # beaker
        path("M47 26 L47 98 C47 102 49 104 53 104 L79 104 C83 104 85 102 85 98 L85 26"),
        path("M47 26 C45 26 42 24 41 22"), line(85, 26, 87, 26),
        line(77, 44, 85, 44, THIN), line(79, 58, 85, 58, THIN), line(77, 72, 85, 72, THIN),
        sheen("M52 32 L52 60"),
        # basin
        path("M12 70 L116 70 L108 106 C100 114 28 114 20 106 Z"),
        # ice cubes
        '<g transform="translate(27 70) rotate(-14)">' + rect(-8, -8, 16, 16, 3) + "</g>",
        '<g transform="translate(101 69) rotate(12)">' + rect(-8, -8, 16, 16, 3) + "</g>",
        '<g transform="translate(36 84) rotate(8)">' + rect(-6, -6, 12, 12, 2.5) + "</g>",
        '<g transform="translate(94 85) rotate(-10)">' + rect(-6, -6, 12, 12, 2.5) + "</g>",
    ]
    fill = [path("M50.5 62 L81.5 62 L81.5 97.5 C81.5 99.5 80.5 100.5 78.5 100.5 L53.5 100.5 "
                 "C51.5 100.5 50.5 99.5 50.5 97.5 Z", SOLID)]
    # the bath water, and a little frost above it
    accent = [path("M16 80 L112 80 L106.5 104 C99 110 29 110 21.5 104 Z", SOLID, 'opacity="0.7"'),
              path("M20 46 L20 56 M15 51 L25 51 M16.5 47.5 L23.5 54.5 M23.5 47.5 L16.5 54.5", THIN),
              path("M108 36 L108 44 M104 40 L112 40", THIN, 'opacity="0.7"')]
    return dict(outline=outline, fill=fill, accent=accent)


def bloomery():
    outline = [
        path("M38 110 L46 34 C47 26 52 22 58 22 L70 22 C76 22 81 26 82 34 L90 110"),
        ellipse(64, 22, 6, 1.6, THIN),
        # clay coils
        path("M43 62 C56 66 72 66 85 62", THIN, 'opacity="0.6"'),
        path("M45 44 C57 47 71 47 83 44", THIN, 'opacity="0.6"'),
        # arch opening
        path("M53 110 L53 94 C53 84 75 84 75 94 L75 110"),
        line(30, 110, 98, 110),
        # tuyere and bellows
        path("M87 88 L104 82"),
        path("M104 82 L118 70 C122 78 122 90 118 98 Z"),
        path("M108 79 L114 90", THIN, 'opacity="0.6"'),
    ]
    fill = [path("M56.5 109 L56.5 95.5 C56.5 88 71.5 88 71.5 95.5 L71.5 109 Z", SOLID)]
    accent = [path(flame(64, 20, 12, 5), SOLID),
              circle(54, 12, 1.6, SOLID), circle(72, 8, 1.3, SOLID), circle(62, 5, 1.0, SOLID),
              path("M58 100 C62 96 66 96 70 100", THIN)]
    return dict(outline=outline, fill=fill, accent=accent)


def still():
    outline = [
        # cucurbit (round flask) and its neck
        path("M34 52 L34 63 C22 67 15 76 15 87 C15 101 26 110 40 110 C54 110 65 101 65 87 "
             "C65 76 58 67 46 63 L46 52"),
        sheen("M22 82 C22 76 25 72 29 70"),
        # alembic head
        path("M30 52 L50 52 C54 44 52 34 40 30 C28 34 26 44 30 52 Z"),
        # the beak, sloping down to the receiver
        path("M50 38 L99 70"), path("M48 44 L95 74"),
        # receiver
        path("M93 70 L93 80 C85 84 80 90 80 97 C80 106 87 112 97 112 C107 112 114 106 114 97 "
             "C114 90 109 84 101 80 L101 70"),
        line(10, 116, 70, 116),
    ]
    fill = [path("M17.5 90 C20 101 28 107 40 107 C52 107 60 101 62.5 90 C50 94 30 94 17.5 90 Z", SOLID),
            path("M83 100 C85 106 90 109 97 109 C104 109 109 106 111 100 C102 103 92 103 83 100 Z", SOLID)]
    accent = [path("M36 44 C38 41 42 41 44 44", THIN), path("M34 38 C37 35 41 35 44 38", THIN, 'opacity="0.6"'),
              path("M97 76 C95.5 79 95.5 80.5 97 81.5 C98.5 80.5 98.5 79 97 76 Z", SOLID),
              path("M97 86 C95.8 88.5 95.8 89.8 97 90.6 C98.2 89.8 98.2 88.5 97 86 Z", SOLID, 'opacity="0.7"')]
    return dict(outline=outline, fill=fill, accent=accent)


def voltaic():
    outline = [
        # beaker
        path("M28 52 L28 102 C28 107 31 110 36 110 L92 110 C97 110 100 107 100 102 L100 52"),
        line(25, 52, 103, 52),
        sheen("M33 58 L33 96"),
        # electrodes
        rect(43, 38, 8, 58, 1.5), rect(77, 38, 8, 58, 1.5),
        # wires
        path("M47 38 L47 24 L54 24"), path("M81 38 L81 24 L74 24"),
        # the pile: alternating copper and zinc discs
        rect(54, 12, 20, 24, 3),
        line(58, 18, 70, 18, THIN), line(58, 24, 70, 24, THIN), line(58, 30, 70, 30, THIN),
        path("M58 6 L58 10 M56 8 L60 8", THIN), path("M68 8 L72 8", THIN),
    ]
    fill = [path("M31.5 64 L96.5 64 L96.5 102 C96.5 105 95 106.5 92 106.5 L36 106.5 "
                 "C33 106.5 31.5 105 31.5 102 Z", SOLID)]
    accent = [circle(56, 80, 2.2, THIN), circle(58, 70, 1.6, THIN), circle(55, 90, 1.4, THIN),
              circle(72, 78, 2.2, THIN), circle(70, 68, 1.6, THIN), circle(73, 88, 1.4, THIN),
              path("M92 14 L86 24 L92 24 L86 34", THIN)]
    return dict(outline=outline, fill=fill, accent=accent)


def irradiator():
    outline = [
        # cord and reflector dome
        line(64, 2, 64, 12),
        path("M34 34 C34 20 46 12 64 12 C82 12 94 20 94 34 Z"),
        circle(64, 37, 6),
        # quartz tube in a stand
        path("M56 60 L56 100 C56 105 59 108 64 108 C69 108 72 105 72 100 L72 60"),
        line(53, 60, 75, 60),
        sheen("M59.5 66 L59.5 92"),
        line(40, 114, 88, 114), line(84, 114, 84, 74), line(84, 76, 72, 76),
    ]
    fill = [path("M59 80 L69 80 L69 99.5 C69 102.5 67 104.5 64 104.5 C61 104.5 59 102.5 59 99.5 Z", SOLID)]
    rays = []
    for ang in (-50, -30, -12, 12, 30, 50):
        a = math.radians(90 + ang)
        x1, y1 = 64 + math.cos(a) * 12, 37 + math.sin(a) * 12
        x2, y2 = 64 + math.cos(a) * 26, 37 + math.sin(a) * 26
        rays.append(line(round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1), THIN))
    accent = [circle(64, 37, 3.2, SOLID)] + rays
    return dict(outline=outline, fill=fill, accent=accent)


def catalyst_bed():
    outline = [
        rect(46, 24, 36, 82, 8),
        rect(40, 34, 48, 6, 2), rect(40, 90, 48, 6, 2),
        path("M64 24 L64 12 L94 12"), path("M64 106 L64 116 L34 116"),
        sheen("M50.5 44 L50.5 84"),
    ]
    for row, y in enumerate(range(48, 88, 8)):
        for x in ([56, 64, 72] if row % 2 == 0 else [60, 68]):
            outline.append(circle(x, y, 3.2, THIN))
    fill = [rect(49.5, 42, 29, 46, 2, SOLID)]
    accent = [path("M84 8 L90 12 L84 16", THIN), path("M44 112 L38 116 L44 120", THIN),
              path("M30 54 C34 50 34 46 30 42 M98 54 C94 50 94 46 98 42", THIN, 'opacity="0.7"')]
    return dict(outline=outline, fill=fill, accent=accent)


def autoclave():
    bolts = [circle(x, 40, 1.6, SOLID) for x in (36, 46, 56, 72, 82, 92)]
    outline = [
        path("M36 36 C40 24 52 20 64 20 C76 20 88 24 92 36"),
        rect(30, 36, 68, 8, 2),
        path("M34 44 L34 92 C34 106 46 114 64 114 C82 114 94 106 94 92 L94 44"),
        # sight glass
        rect(54, 54, 20, 44, 6),
        # gauge on its stem
        line(64, 20, 64, 26), circle(64, 12, 9),
        line(64, 12, 64, 6, THIN), line(57, 12, 59, 12, THIN), line(69, 12, 71, 12, THIN),
        # side valve
        path("M94 60 L104 60 M104 54 L104 66"),
    ] + bolts
    fill = [rect(57, 70, 14, 25, 3.5, SOLID)]
    accent = [line(64, 12, 69, 7.5, f'stroke="#fff" stroke-width="{SW * 0.6:.2f}" stroke-linecap="round"'),
              path("M108 50 C112 46 108 42 112 38", THIN), path("M114 54 C118 50 114 46 118 42", THIN, 'opacity="0.6"')]
    return dict(outline=outline, fill=fill, accent=accent)


def polymer_reactor():
    outline = [
        # motor and shaft
        rect(52, 4, 24, 14, 3), line(56, 9, 72, 9, THIN), line(64, 18, 64, 92),
        # jacketed tank
        path("M28 32 L28 90 C28 106 44 114 64 114 C84 114 100 106 100 90 L100 32"),
        path("M33 36 L33 89 C33 102 47 109 64 109 C81 109 95 102 95 89 L95 36", THIN, 'opacity="0.7"'),
        line(24, 32, 104, 32),
        path("M40 32 L40 24 L46 24 L46 32"), path("M82 32 L82 26 L90 26 L90 32"),
        # impeller
        path("M64 92 L50 86 M64 92 L78 98 M64 92 L52 99 M64 92 L76 85"),
        circle(64, 92, 2.4, SOLID),
    ]
    fill = [path("M35.5 58 L92.5 58 L92.5 88.5 C92.5 100 80 106.5 64 106.5 C48 106.5 35.5 100 35.5 88.5 Z", SOLID)]
    # a little chain of linked units being stirred
    accent = [path("M42 70 C46 64 50 76 54 70 C58 64 62 76 66 70 C70 64 74 76 78 70 C82 64 86 76 88 72",
                   THIN),
              path("M44 80 C48 78 52 78 56 80", THIN, 'opacity="0.6"'),
              path("M74 80 C78 78 82 78 86 80", THIN, 'opacity="0.6"')]
    return dict(outline=outline, fill=fill, accent=accent)


# --- tier II and up, and the two newer families ------------------------------------------
def flask():
    outline = [
        path("M56 18 L56 46 L33 97 C31 103 34 107 40 107 L88 107 C94 107 97 103 95 97 L72 46 L72 18"),
        line(52, 18, 76, 18),
        line(62, 60, 66, 60, THIN), line(60, 70, 68, 70, THIN), line(58, 80, 70, 80, THIN),
        sheen("M53 52 L43 76"),
        rect(26, 109, 76, 9, 2.5), circle(40, 113.5, 1.6, SOLID), circle(88, 113.5, 1.6, SOLID),
    ]
    fill = [path("M43 76 L35.5 96 C34 101 36.5 103.5 41 103.5 L87 103.5 C91.5 103.5 94 101 92.5 96 L85 76 "
                 "C72 79 56 79 43 76 Z", SOLID)]
    accent = [rect(56, 97, 16, 4, 2, SOLID),
              path("M46 88 C54 84 74 84 82 88", THIN, 'opacity="0.7"'),
              circle(58, 70, 1.5, SOLID, 'opacity="0.7"'), circle(68, 64, 1.2, SOLID, 'opacity="0.6"')]
    return dict(outline=outline, fill=fill, accent=accent)


def blast_furnace():
    outline = [
        # the stack: throat, shaft, bosh, hearth
        path("M50 12 L78 12 L90 62 L84 90 L84 108 L44 108 L44 90 L38 62 Z"),
        line(46, 12, 82, 12),
        path("M46 30 L82 30", THIN, 'opacity="0.5"'), path("M42 50 L86 50", THIN, 'opacity="0.5"'),
        # the hot-blast stove and its bustle pipe
        path("M100 108 L100 40 C100 30 118 30 118 40 L118 108"),
        path("M100 52 L94 52 L94 80 L87 80"),
        line(28, 112, 124, 112),
        # tap hole and runner
        path("M44 100 L32 100 L26 106"),
    ]
    fill = [path("M47.5 90.5 L80.5 90.5 L80.5 104.5 L47.5 104.5 Z", SOLID)]
    accent = [path(flame(64, 12, 11, 5), SOLID),
              circle(56, 4, 1.5, SOLID, 'opacity="0.7"'), circle(72, 3, 1.2, SOLID, 'opacity="0.6"'),
              path("M32 100 C28 103 26 106 25 112", THIN), circle(24, 116, 2, SOLID)]
    return dict(outline=outline, fill=fill, accent=accent)


def arc_furnace():
    outline = [
        # tilting shell and domed roof
        path("M24 70 L24 100 C24 108 32 112 40 112 L88 112 C96 112 104 108 104 100 L104 70"),
        path("M20 70 C30 54 98 54 108 70 Z"),
        path("M24 88 L12 84"),
        # three graphite electrodes on their arm and mast
        rect(44, 20, 8, 44, 2), rect(60, 14, 8, 50, 2), rect(76, 20, 8, 44, 2),
        path("M44 28 L116 28"), line(116, 28, 116, 112),
        line(10, 116, 120, 116),
    ]
    fill = [path("M28 86 L100 86 L100 100 C100 105 96 108.5 90 108.5 L38 108.5 C32 108.5 28 105 28 100 Z", SOLID)]
    accent = [path("M48 64 L44 71 L50 73 L46 82", THIN), path("M64 64 L60 72 L67 74 L63 83", THIN),
              path("M80 64 L76 71 L82 73 L78 82", THIN),
              circle(38, 78, 1.4, SOLID), circle(92, 76, 1.3, SOLID), circle(70, 80, 1.1, SOLID, 'opacity="0.7"')]
    return dict(outline=outline, fill=fill, accent=accent)


def air_liquefier():
    outline = [
        # compressor with its flywheel
        rect(10, 78, 32, 30, 4), circle(26, 68, 9), line(26, 68, 26, 78, THIN),
        # counter-current coil above the Dewar
        path("M42 88 L50 88 L50 20 L66 20"),
        ellipse(83, 22, 17, 3, THIN), ellipse(83, 28, 17, 3, THIN), ellipse(83, 34, 17, 3, THIN),
        line(83, 37, 83, 44), circle(83, 46, 2.6),
        # the Dewar flask: double wall
        path("M62 50 L62 104 C62 110 66 114 72 114 L94 114 C100 114 104 110 104 104 L104 50"),
        path("M66 52 L66 102 C66 107 69 110 74 110 L92 110 C97 110 100 107 100 102 L100 52", THIN, 'opacity="0.6"'),
        line(58, 50, 108, 50),
        line(6, 116, 120, 116),
    ]
    fill = [path("M66.5 84 L99.5 84 L99.5 101.5 C99.5 105.5 97 107.5 93 107.5 L73 107.5 C69 107.5 66.5 105.5 66.5 101.5 Z", SOLID)]
    accent = [path("M74 48 C70 42 76 38 72 32", THIN), path("M92 48 C96 42 90 38 94 32", THIN, 'opacity="0.6"'),
              path("M116 24 L116 36 M110 30 L122 30 M111.5 25.5 L120.5 34.5 M120.5 25.5 L111.5 34.5", THIN)]
    return dict(outline=outline, fill=fill, accent=accent)


def column():
    outline = [
        rect(50, 8, 28, 94, 10),
        # trays
        line(53, 24, 75, 24, THIN), line(53, 36, 75, 36, THIN), line(53, 48, 75, 48, THIN),
        line(53, 60, 75, 60, THIN), line(53, 72, 75, 72, THIN), line(53, 84, 75, 84, THIN),
        # reboiler
        path("M40 102 L88 102 L88 110 C88 115 84 118 79 118 L49 118 C44 118 40 115 40 110 Z"),
        # condenser and reflux
        path("M78 16 L100 16 L100 26"), rect(94, 26, 12, 20, 3), path("M100 46 L100 52 L78 52", THIN),
        # side draws
        path("M78 66 L96 66 L96 72"), path("M50 42 L32 42 L32 48"), path("M50 78 L32 78 L32 84"),
    ]
    fill = [path("M43.5 104 L84.5 104 L84.5 110 C84.5 112.5 82.5 114.5 79.5 114.5 L48.5 114.5 "
                 "C45.5 114.5 43.5 112.5 43.5 110 Z", SOLID)]
    accent = [circle(60, 92, 1.8, SOLID), circle(68, 80, 1.5, SOLID), circle(58, 66, 1.3, SOLID, 'opacity="0.8"'),
              circle(66, 54, 1.2, SOLID, 'opacity="0.7"'), circle(62, 42, 1.0, SOLID, 'opacity="0.6"'),
              path("M96 74 C95 76.5 95 77.5 96 78.5 C97 77.5 97 76.5 96 74 Z", SOLID),
              path("M32 50 C31 52.5 31 53.5 32 54.5 C33 53.5 33 52.5 32 50 Z", SOLID, 'opacity="0.8"')]
    return dict(outline=outline, fill=fill, accent=accent)


def electrolytic_cell():
    outline = [
        # steel pot with its carbon lining
        path("M14 60 L14 104 C14 110 18 114 24 114 L104 114 C110 114 114 110 114 104 L114 60"),
        path("M19 62 L19 103 C19 107 21 109 25 109 L103 109 C107 109 109 107 109 103 L109 62", THIN, 'opacity="0.55"'),
        line(10, 60, 118, 60),
        # carbon anodes hung from the bus bar
        rect(26, 42, 20, 32, 2), rect(54, 42, 20, 32, 2), rect(82, 42, 20, 32, 2),
        line(36, 42, 36, 24), line(64, 42, 64, 24), line(92, 42, 92, 24),
        rect(20, 16, 88, 8, 2),
    ]
    fill = [path("M19.5 82 L108.5 82 L108.5 103 C108.5 106 107 107.5 104 107.5 L24 107.5 "
                 "C21 107.5 19.5 106 19.5 103 Z", SOLID)]
    accent = [circle(24, 76, 1.7, THIN), circle(50, 77, 1.5, THIN), circle(78, 76, 1.7, THIN), circle(104, 77, 1.5, THIN),
              circle(51, 69, 1.2, THIN), circle(79, 68, 1.2, THIN),
              path("M118 2 L112 10 L118 10 L112 18", THIN)]
    return dict(outline=outline, fill=fill, accent=accent)


def nuclear_reactor():
    rods = [line(x, 78, x, 102, THIN) for x in (46, 52, 58, 64, 70, 76, 82)]
    outline = [
        # pool, bridge, control-rod drives, core
        path("M16 30 L16 104 C16 110 20 114 26 114 L102 114 C108 114 112 110 112 104 L112 30"),
        line(16, 44, 112, 44, THIN),
        rect(10, 22, 108, 8, 2),
        line(50, 30, 50, 74), line(64, 30, 64, 70), line(78, 30, 78, 74),
        rect(40, 74, 48, 32, 3),
    ] + rods
    fill = [rect(43, 77, 42, 26, 2, SOLID)]
    accent = [ellipse(64, 90, 36, 24, SOLID, 'opacity="0.35"'), ellipse(64, 90, 28, 18, SOLID, 'opacity="0.3"'),
              path("M100 12 L104 6 L108 12 Z", SOLID)]
    return dict(outline=outline, fill=fill, accent=accent)


def cyclotron():
    outline = [
        # the magnet's pole (seen from above) and the two dees
        circle(64, 60, 48, THIN, 'opacity="0.55"'),
        path("M60 22 A38 38 0 0 0 60 98 Z"), path("M68 22 A38 38 0 0 1 68 98 Z"),
        # beam pipe out to the target
        path("M100 60 L112 60 L112 96"),
        rect(102, 96, 20, 16, 3),
        line(6, 118, 122, 118),
    ]
    fill = [rect(105, 99, 14, 10, 2, SOLID)]
    accent = [path("M64 60 C64 56 70 56 70 60 C70 66 58 66 58 60 C58 50 76 50 76 60 C76 72 52 72 52 60 "
                   "C52 44 82 44 82 60 C82 78 46 78 46 60 C46 38 88 38 88 60 L100 60", THIN),
              circle(64, 60, 2.2, SOLID)]
    return dict(outline=outline, fill=fill, accent=accent)


def cracker():
    outline = [
        # reactor (with its cyclone) and regenerator, linked by the riser and standpipes
        rect(16, 16, 32, 50, 12), path("M24 26 L40 26 L34 44 L30 44 Z", THIN, 'opacity="0.6"'),
        rect(74, 40, 40, 62, 14),
        path("M32 66 L32 104 C32 110 37 112 43 112 L94 112 L94 102"),
        path("M94 40 L94 28 L48 28"),
        path("M32 16 L32 6 L60 6"),
        path("M114 64 L122 64", THIN),
    ]
    fill = [path("M77.5 74 L110.5 74 L110.5 88 C110.5 95 105 98.5 98 98.5 L90 98.5 C83 98.5 77.5 95 77.5 88 Z", SOLID)]
    accent = [path(flame(94, 70, 14, 6), SOLID, 'opacity="0.85"'),
              path("M56 2 L60 6 L56 10", THIN), path("M37 108 L32 104 L37 100", THIN, 'opacity="0.7"'),
              circle(32, 86, 1.6, SOLID), circle(32, 78, 1.3, SOLID, 'opacity="0.7"')]
    return dict(outline=outline, fill=fill, accent=accent)


def high_pressure():
    bolts = [circle(x, 34, 1.5, SOLID) for x in (40, 50, 78, 88)] + [circle(x, 94, 1.5, SOLID) for x in (40, 50, 78, 88)]
    outline = [
        path("M44 26 C44 14 84 14 84 26 L84 102 C84 114 44 114 44 102 Z"),
        path("M50 28 L50 100 M78 28 L78 100", THIN, 'opacity="0.55"'),
        rect(36, 30, 56, 8, 2), rect(36, 90, 56, 8, 2),
        path("M84 54 L96 54"), circle(106, 54, 9),
        line(106, 54, 106, 47, THIN), line(99, 54, 101, 54, THIN), line(111, 54, 113, 54, THIN),
        path("M44 70 L26 70 L26 116"), path("M84 78 L104 78 L104 116"),
        line(14, 116, 116, 116),
    ] + bolts
    fill = [rect(52, 44, 24, 42, 3, SOLID)]
    accent = [line(106, 54, 111, 49, f'stroke="#fff" stroke-width="{SW * 0.6:.2f}" stroke-linecap="round"'),
              path("M60 8 C56 4 60 0 56 -4", THIN), path("M68 10 C72 6 68 2 72 -2", THIN, 'opacity="0.6"')]
    return dict(outline=outline, fill=fill, accent=accent)


def diamond_press():
    outline = [
        rect(12, 12, 104, 104, 10),
        # four of the six anvils of a cubic press, closing on the cell
        path("M44 18 L84 18 L72 50 L56 50 Z"), path("M44 110 L84 110 L72 78 L56 78 Z"),
        path("M18 44 L18 84 L50 72 L50 56 Z"), path("M110 44 L110 84 L78 72 L78 56 Z"),
        rect(55, 55, 18, 18, 2),
    ]
    fill = [rect(58, 58, 12, 12, 1.5, SOLID)]
    accent = [path("M64 2 L64 10 M60 6 L64 10 L68 6", THIN), path("M64 126 L64 118 M60 122 L64 118 L68 122", THIN),
              path("M2 64 L10 64 M6 60 L10 64 L6 68", THIN), path("M126 64 L118 64 M122 60 L118 64 L122 68", THIN),
              path("M104 18 L104 26 M100 22 L108 22", THIN, 'opacity="0.8"')]
    return dict(outline=outline, fill=fill, accent=accent)


def fermenter():
    outline = [
        # crock with hoops and lid, and its airlock
        path("M30 32 C24 52 24 90 30 110 L98 110 C104 90 104 52 98 32 Z"),
        path("M27 50 C50 54 78 54 101 50", THIN, 'opacity="0.6"'), path("M27 92 C50 96 78 96 101 92", THIN, 'opacity="0.6"'),
        line(26, 32, 102, 32),
        path("M64 32 L64 22 C64 16 72 16 72 22 L72 26 C72 32 80 32 80 26 L80 14"),
        line(20, 114, 108, 114),
    ]
    fill = [path("M29 64 L99 64 C101 78 101 92 98 106 L30 106 C27 92 27 78 29 64 Z", SOLID)]
    accent = [circle(48, 86, 2, THIN), circle(60, 76, 1.6, THIN), circle(76, 90, 2.2, THIN), circle(84, 74, 1.4, THIN),
              circle(80, 8, 1.8, THIN), circle(84, 3, 1.3, THIN, 'opacity="0.7"')]
    return dict(outline=outline, fill=fill, accent=accent)


def bioreactor():
    outline = [
        rect(54, 4, 20, 12, 3), line(64, 16, 64, 98),
        path("M32 28 L32 100 C32 108 38 112 46 112 L82 112 C90 112 96 108 96 100 L96 28"),
        rect(28, 22, 72, 8, 3),
        line(42, 30, 42, 66), line(86, 30, 86, 58),
        path("M52 72 L76 72 M52 92 L76 92"), circle(64, 72, 2, SOLID), circle(64, 92, 2, SOLID),
        path("M48 104 L80 104", THIN),
        sheen("M37 36 L37 64"),
    ]
    fill = [path("M35.5 48 L92.5 48 L92.5 100 C92.5 105 89 108.5 84 108.5 L44 108.5 C39 108.5 35.5 105 35.5 100 Z", SOLID)]
    accent = [circle(50, 60, 3, THIN), circle(50, 60, 0.9, SOLID), circle(80, 82, 3, THIN), circle(80, 82, 0.9, SOLID),
              circle(48, 84, 2.6, THIN), circle(48, 84, 0.8, SOLID),
              circle(58, 100, 1.2, THIN), circle(70, 98, 1.4, THIN), circle(64, 86, 1.0, THIN, 'opacity="0.7"')]
    return dict(outline=outline, fill=fill, accent=accent)


def crystal_puller():
    outline = [
        # pull rod, seed chuck and the growing boule
        line(64, 4, 64, 26), rect(59, 24, 10, 6, 1.5),
        path("M55 30 L73 30 L73 64 C73 72 68 76 64 78 C60 76 55 72 55 64 Z"),
        sheen("M58 36 L58 62"),
        # crucible in its heater
        path("M34 82 L38 106 C39 111 42 113 47 113 L81 113 C86 113 89 111 90 106 L94 82"),
        path("M26 84 L26 112 M102 84 L102 112", THIN), path("M22 88 L30 88 M22 96 L30 96 M22 104 L30 104", THIN),
        path("M98 88 L106 88 M98 96 L106 96 M98 104 L106 104", THIN),
        line(14, 118, 114, 118),
    ]
    fill = [path("M37 92 L91 92 L88.5 106 C88 108.5 86 110 83 110 L45 110 C42 110 40 108.5 39.5 106 Z", SOLID)]
    accent = [path("M48 14 C54 8 74 8 80 14", THIN), path("M80 14 L80 8 L74 10", THIN),
              ellipse(64, 84, 10, 2.5, SOLID, 'opacity="0.6"')]
    return dict(outline=outline, fill=fill, accent=accent)


def cvd_chamber():
    outline = [
        path("M26 100 L26 50 C26 26 44 14 64 14 C84 14 102 26 102 50 L102 100"),
        rect(18, 100, 92, 12, 3),
        rect(42, 84, 44, 6, 2), line(64, 90, 64, 100),
        path("M26 58 L10 58 L10 38"), path("M102 74 L118 74 L118 96"),
        sheen("M34 44 C36 34 42 28 48 24"),
    ]
    fill = [rect(45, 80, 38, 4, 1.2, SOLID)]
    accent = [ellipse(64, 58, 26, 16, SOLID, 'opacity="0.35"'), ellipse(64, 58, 16, 9, SOLID, 'opacity="0.35"'),
              circle(54, 72, 1.4, SOLID), circle(66, 74, 1.2, SOLID), circle(76, 70, 1.4, SOLID, 'opacity="0.8"'),
              path("M10 34 L6 38 L10 42", THIN)]
    return dict(outline=outline, fill=fill, accent=accent)


def centrifuge():
    outline = [
        # bench centrifuge: housing, hinged dome lid, rotor tubes seen through it
        path("M24 66 L24 104 C24 110 28 114 34 114 L94 114 C100 114 104 110 104 104 L104 66"),
        rect(20, 60, 88, 8, 3),
        path("M28 60 C30 42 46 34 64 34 C82 34 98 42 100 60"),
        line(64, 60, 64, 52), circle(64, 50, 3),
        path("M58 48 L40 58"), path("M70 48 L88 58"),
        rect(32, 82, 26, 12, 2.5), circle(84, 88, 6), line(84, 88, 87, 84, THIN),
        line(16, 118, 112, 118),
        sheen("M34 50 C38 44 44 40 50 38"),
    ]
    fill = [path("M44 54.5 L39.5 57 L41 59.5 L45.5 57 Z", SOLID), path("M84 54.5 L88.5 57 L87 59.5 L82.5 57 Z", SOLID),
            rect(35, 85, 12, 6, 1.5, SOLID)]
    accent = [path("M26 28 C36 18 50 14 64 14", THIN), path("M64 14 L58 10 M64 14 L58 18", THIN),
              path("M102 28 C92 18 78 14 64 14", THIN, 'opacity="0.6"'),
              path("M18 40 C20 36 22 33 25 30", THIN, 'opacity="0.5"'), path("M110 40 C108 36 106 33 103 30", THIN, 'opacity="0.5"')]
    return dict(outline=outline, fill=fill, accent=accent)


def ultracentrifuge():
    holes = [circle(64 + 11 * math.cos(a), 74 + 11 * math.sin(a), 2.4, THIN)
             for a in (i * math.pi / 3 for i in range(6))]
    outline = [
        # armoured floor cabinet: vacuum chamber, rotor, control strip, vacuum line
        rect(24, 40, 80, 74, 5),
        rect(20, 30, 88, 10, 3), path("M40 30 L40 24 L88 24 L88 30"),
        circle(64, 74, 24), circle(64, 74, 16), circle(64, 74, 3),
        rect(34, 102, 60, 8, 2),
        path("M104 56 L114 56 L114 96 L104 96"), circle(114, 76, 4, THIN),
        line(16, 118, 112, 118),
        sheen("M30 46 L30 62"),
    ] + holes
    fill = [circle(64 + 11 * math.cos(a), 74 + 11 * math.sin(a), 1.6, SOLID) for a in (i * math.pi / 3 for i in range(6))] + \
        [rect(38, 104, 18, 4, 1, SOLID)]
    accent = [path("M34 74 C34 58 46 46 62 44", THIN), path("M62 44 L56 40 M62 44 L57 49", THIN),
              path("M94 74 C94 90 82 102 66 104", THIN, 'opacity="0.6"'),
              path("M44 12 C54 6 74 6 84 12", THIN, 'opacity="0.5"')]
    return dict(outline=outline, fill=fill, accent=accent)


VESSELS = {
    "mortar": mortar, "fire": fire, "ice_bath": ice_bath, "bloomery": bloomery,
    "still": still, "voltaic_cell": voltaic, "irradiator": irradiator,
    "catalyst_bed": catalyst_bed, "autoclave": autoclave, "polymer_reactor": polymer_reactor,
    "flask": flask, "blast_furnace": blast_furnace, "arc_furnace": arc_furnace,
    "air_liquefier": air_liquefier, "column": column, "electrolytic_cell": electrolytic_cell,
    "nuclear_reactor": nuclear_reactor, "cyclotron": cyclotron, "cracker": cracker,
    "high_pressure": high_pressure, "diamond_press": diamond_press, "fermenter": fermenter,
    "bioreactor": bioreactor, "crystal_puller": crystal_puller, "cvd_chamber": cvd_chamber,
    "centrifuge": centrifuge, "ultracentrifuge": ultracentrifuge,
}


# --------------------------------------------------------------------------------------
# UI icons: a 32 px design grid, exported at 64 px
# --------------------------------------------------------------------------------------
ICON_GRID = 32
ISW = 2.4
I_STYLE = (f'fill="none" stroke="#fff" stroke-width="{ISW}" stroke-linecap="round" '
           f'stroke-linejoin="round"')


def isvg(*parts, px=64):
    body = "\n  ".join(p for p in parts if p)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ICON_GRID} {ICON_GRID}" '
            f'width="{px}" height="{px}">\n  {body}\n</svg>\n')


def ip(d, extra=""):
    return f'<path d="{d}" {I_STYLE} {extra}/>'


def gear():
    pts = []
    for i in range(16):
        a = math.tau * i / 16 - math.pi / 2
        r = 12.5 if (i % 2 == 0) else 9.6
        # each tooth is a short flat top: two points per step
        for da in (-0.13, 0.13):
            pts.append((16 + r * math.cos(a + da), 16 + r * math.sin(a + da)))
    d = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"
    return [ip(d), circle(16, 16, 4.2, I_STYLE)]


ICONS = {
    "gear": gear(),
    "flask": [ip("M12 4 L20 4 M13.5 4 L13.5 12 L6 25 C5 27 6.5 28.5 8.5 28.5 L23.5 28.5 C25.5 28.5 27 27 26 25 "
                 "L18.5 12 L18.5 4"), ip("M9 21 L23 21", 'opacity="0.6"'),
              circle(14, 24.5, 1.3, SOLID), circle(18.5, 23.5, 1.0, SOLID)],
    "book": [ip("M16 7 C12 5 8 5 4 6 L4 26 C8 25 12 25 16 27 C20 25 24 25 28 26 L28 6 C24 5 20 5 16 7 Z"),
             ip("M16 7 L16 27")],
    "reaction": [circle(7, 16, 4, I_STYLE), circle(25, 11, 3.2, I_STYLE), circle(25, 22, 3.2, I_STYLE),
                 ip("M12.5 16 L19 16 M16.5 13 L19.5 16 L16.5 19")],
    "tree": [rect(12, 3, 8, 6, 1.5, I_STYLE), rect(3, 23, 8, 6, 1.5, I_STYLE), rect(21, 23, 8, 6, 1.5, I_STYLE),
             ip("M16 9 L16 15 M7 23 L7 15 L25 15 L25 23")],
    "bench": [ip("M10 5 L10 20 C10 25 13 27 16 27 C19 27 22 25 22 20 L22 5"), ip("M8 5 L24 5"),
              ip("M10.5 15 L21.5 15", 'opacity="0.6"')],
    "close": [ip("M9 9 L23 23 M23 9 L9 23")],
    "search": [circle(14, 14, 8, I_STYLE), ip("M20 20 L27 27")],
    "lock": [rect(7, 14, 18, 14, 3, I_STYLE), ip("M11 14 L11 10 C11 4 21 4 21 10 L21 14"),
             ip("M16 19 L16 23")],
    "check": [ip("M7 16.5 L13 22.5 L25 10")],
    "dot": [circle(16, 16, 5, SOLID)],
    "external": [ip("M18 6 L26 6 L26 14 M26 6 L15 17"), ip("M23 19 L23 26 L6 26 L6 9 L13 9")],
    "clear": [ip("M8 11 A10 10 0 1 1 7 20"), ip("M8 4 L8 11 L15 11")],
    "spark": [ip("M17 3 L7 18 L15 18 L13 29 L25 13 L17 13 Z")],
    "chevron": [ip("M12 7 L21 16 L12 25")],
    "plus": [ip("M16 7 L16 25 M7 16 L25 16")],
    "minus": [ip("M7 16 L25 16")],
    "info": [circle(16, 16, 12, I_STYLE), ip("M16 14 L16 23"), circle(16, 9.5, 1.5, SOLID)],
}


def write_ui(folder):
    folder.mkdir(parents=True, exist_ok=True)
    n = 0
    for name, parts in ICONS.items():
        sp = folder / f"{name}.svg"
        sp.write_text(isvg(*parts), encoding="utf-8")
        if rasterise(sp, folder / f"{name}.png", px=64):
            n += 1
    # the bench: a faint dot every 32 px, tiled across the canvas (tinted in game)
    grid = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">'
            f'<circle cx="16" cy="16" r="1.25" fill="#fff"/></svg>\n')
    (folder / "grid_dot.svg").write_text(grid, encoding="utf-8")
    rasterise(folder / "grid_dot.svg", folder / "grid_dot.png", px=32)
    # the logo: the flask in the brand cyan, with violet contents, for the header
    logo = isvg(ip("M12 4 L20 4 M13.5 4 L13.5 12 L6 25 C5 27 6.5 28.5 8.5 28.5 L23.5 28.5 "
                   "C25.5 28.5 27 27 26 25 L18.5 12 L18.5 4").replace('stroke="#fff"', 'stroke="#5ad6e6"'),
                path("M9.4 20.5 L22.6 20.5 L25.2 25.3 C25.8 26.6 24.9 27.2 23.5 27.2 L8.5 27.2 "
                     "C7.1 27.2 6.2 26.6 6.8 25.3 Z", 'fill="#a070ff" stroke="none"'),
                circle(14.5, 16.5, 1.4, 'fill="#5ad6e6"'), circle(17.5, 13, 1.0, 'fill="#5ad6e6"'), px=128)
    (folder / "logo.svg").write_text(logo, encoding="utf-8")
    rasterise(folder / "logo.svg", folder / "logo.png", px=128)
    return n


# --------------------------------------------------------------------------------------
def rasterise(svg_path, png_path, px=PX):
    try:
        import cairosvg
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=px, output_height=px)
        return True
    except ImportError:
        pass
    exe = shutil.which("rsvg-convert")
    if exe:
        subprocess.run([exe, "-w", str(px), "-h", str(px), "-o", str(png_path), str(svg_path)], check=True)
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--preview", type=Path, help="also write a tinted preview sheet PNG here")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    pngs = 0
    for name, fn in VESSELS.items():
        layers = fn()
        for layer, parts in layers.items():
            if not parts:
                continue
            sp = args.out / f"{name}_{layer}.svg"
            sp.write_text(svg(*parts), encoding="utf-8")
            if rasterise(sp, args.out / f"{name}_{layer}.png"):
                pngs += 1
    print(f"{len(VESSELS)} vessels -> {args.out} ({pngs} PNGs)")
    ui = args.out.parent / "ui"
    print(f"{write_ui(ui)} UI icons + grid + logo -> {ui}")
    if pngs == 0:
        print("no rasteriser found: install cairosvg (pip install cairosvg) to get PNGs")
    if args.preview:
        preview(args.out, args.preview)


# --- preview sheet: the art tinted the way the game tints it ------------------------
# One colour per family of vessels, as the game has it (reaction_check::family_color): every
# vessel of a family wears it, so the colour says what kind of vessel it is.
FAMILY = {
    "Mix": (0.35, 0.85, 0.80),
    "Heat": (1.00, 0.42, 0.20),
    "Cool": (0.50, 0.82, 1.00),
    "Distillation": (0.75, 0.55, 1.00),
    "Electrolysis": (1.00, 0.88, 0.30),
    "Catalysis": (0.45, 0.95, 0.45),
    "Pressure": (0.70, 0.70, 0.74),
    "Polymer": (1.00, 0.50, 0.80),
    "Separation": (1.00, 0.70, 0.38),
    "Biology": (0.75, 0.90, 0.38),
    "Radiation": (0.95, 0.45, 1.00),
    "Fabrication": (0.88, 0.92, 1.00),
}

PROCESS = {  # vessel -> (title, family colour, accent colour, sample contents colour)
    "mortar": ("Mortar", FAMILY["Mix"], (0.85, 0.95, 0.95), (0.12, 0.62, 0.35)),
    "fire": ("Fire", FAMILY["Heat"], (1.00, 0.62, 0.18), (0.69, 0.47, 0.16)),
    "ice_bath": ("Ice Bath", FAMILY["Cool"], (0.55, 0.80, 1.00), (0.12, 0.38, 0.88)),
    "bloomery": ("Bloomery", FAMILY["Heat"], (1.00, 0.55, 0.15), (1.00, 0.70, 0.25)),
    "still": ("Still", FAMILY["Distillation"], (0.85, 0.80, 1.00), (0.48, 0.10, 0.19)),
    "voltaic_cell": ("Voltaic Cell", FAMILY["Electrolysis"], (1.00, 0.95, 0.55), (0.40, 0.75, 0.95)),
    "irradiator": ("Irradiator", FAMILY["Radiation"], (1.00, 0.92, 0.45), (0.94, 0.94, 0.94)),
    "catalyst_bed": ("Catalyst Bed", FAMILY["Catalysis"], (0.65, 1.00, 0.65), (0.66, 0.30, 0.10)),
    "autoclave": ("Autoclave", FAMILY["Pressure"], (1.00, 0.35, 0.30), (0.95, 0.85, 0.40)),
    "polymer_reactor": ("Polymer Reactor", FAMILY["Polymer"], (1.00, 0.75, 0.90), (0.93, 0.93, 0.97)),
    "flask": ("Glass Flask", FAMILY["Mix"], (0.70, 0.96, 0.98), (0.30, 0.55, 0.95)),
    "blast_furnace": ("Blast Furnace", FAMILY["Heat"], (1.00, 0.50, 0.12), (1.00, 0.72, 0.25)),
    "arc_furnace": ("Arc Furnace", FAMILY["Heat"], (0.70, 0.85, 1.00), (1.00, 0.75, 0.30)),
    "air_liquefier": ("Air Liquefier", FAMILY["Cool"], (0.70, 0.95, 1.00), (0.55, 0.75, 1.00)),
    "column": ("Fractionating Column", FAMILY["Distillation"], (0.90, 0.82, 1.00), (0.55, 0.35, 0.15)),
    "electrolytic_cell": ("Electrolytic Cell", FAMILY["Electrolysis"], (1.00, 0.92, 0.55), (0.85, 0.85, 0.90)),
    "nuclear_reactor": ("Nuclear Reactor", FAMILY["Radiation"], (0.35, 0.80, 1.00), (0.55, 0.95, 0.40)),
    "cyclotron": ("Cyclotron", FAMILY["Radiation"], (1.00, 0.55, 1.00), (0.80, 0.80, 0.85)),
    "cracker": ("Catalytic Cracker", FAMILY["Catalysis"], (0.80, 1.00, 0.60), (0.70, 0.50, 0.25)),
    "high_pressure": ("High-Pressure Reactor", FAMILY["Pressure"], (1.00, 0.35, 0.30), (0.45, 0.45, 0.50)),
    "diamond_press": ("Diamond Press", FAMILY["Pressure"], (1.00, 0.35, 0.30), (0.95, 0.97, 1.00)),
    "fermenter": ("Fermenter", FAMILY["Biology"], (0.75, 1.00, 0.55), (0.55, 0.15, 0.25)),
    "bioreactor": ("Bioreactor", FAMILY["Biology"], (0.75, 1.00, 0.55), (0.85, 0.75, 0.35)),
    "crystal_puller": ("Crystal Puller", FAMILY["Fabrication"], (1.00, 0.70, 0.30), (0.75, 0.78, 0.85)),
    "cvd_chamber": ("CVD Chamber", FAMILY["Fabrication"], (1.00, 0.60, 1.00), (0.25, 0.25, 0.28)),
    "centrifuge": ("Centrifuge", FAMILY["Separation"], (1.00, 0.92, 0.65), (0.98, 0.95, 0.85)),
    "ultracentrifuge": ("Ultracentrifuge", FAMILY["Separation"], (1.00, 0.85, 0.60), (0.85, 0.30, 0.30)),
}


def preview(folder, out):
    from PIL import Image, ImageDraw, ImageFont

    def tinted(p, rgb, alpha=1.0):
        im = Image.open(p).convert("RGBA")
        r, g, b, a = im.split()
        col = Image.new("RGBA", im.size, tuple(int(c * 255) for c in rgb) + (255,))
        col.putalpha(a.point(lambda v: int(v * alpha)))
        return col

    try:
        font = ImageFont.truetype(str(ROOT / "assets" / "fonts" / "NotoSans-Regular.ttf"), 22)
        small = ImageFont.truetype(str(ROOT / "assets" / "fonts" / "NotoSans-Regular.ttf"), 15)
    except OSError:
        font = small = ImageFont.load_default()
    cw, ch, pad = 300, 330, 18
    names = list(VESSELS)
    cols = 5
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cw + pad, rows * ch + pad + 50), (10, 13, 28, 255))
    dr = ImageDraw.Draw(sheet)
    dr.text((pad, 12), "Curieosity vessels: outline (process colour) + contents (substance colour) + accent",
            fill=(200, 205, 225), font=small)
    for i, name in enumerate(names):
        title, pc, ac, fc = PROCESS[name]
        x, y = pad + (i % cols) * cw, 50 + (i // cols) * ch
        card = [x, y, x + cw - pad, y + ch - pad]
        dr.rounded_rectangle(card, 14, fill=(26, 18, 34, 255),
                             outline=tuple(int(c * 255) for c in pc) + (255,), width=3)
        art = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
        for layer, rgb, alpha in (("fill", fc, 0.92), ("outline", pc, 1.0), ("accent", ac, 0.95)):
            p = folder / f"{name}_{layer}.png"
            if p.exists():
                art.alpha_composite(tinted(p, rgb, alpha))
        art = art.resize((230, 230), Image.LANCZOS)
        sheet.alpha_composite(art, (x + (cw - pad - 230) // 2, y + 18))
        w = dr.textlength(title, font=font)
        dr.text((x + (cw - pad - w) / 2, y + ch - pad - 62), title, fill=(240, 240, 250), font=font)
        # toolbar-size icon (outline only, white), as it would sit in a vessel button
        icon = tinted(folder / f"{name}_outline.png", (1, 1, 1)).resize((34, 34), Image.LANCZOS)
        sheet.alpha_composite(icon, (x + 14, y + ch - pad - 46))
        dr.text((x + 54, y + ch - pad - 38), "toolbar icon", fill=(150, 150, 175), font=small)
    sheet.convert("RGB").save(out)
    print(f"preview -> {out}")


if __name__ == "__main__":
    main()
