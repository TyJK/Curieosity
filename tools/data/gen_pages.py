"""
Builds the pages the game shows from Wikipedia and Wikidata: assets/data/pages.ron.

Reads what tools/data/scrape_wiki.py fetched (library/wiki/pages.jsonl.xz) and writes, for
every substance in the game (and every locked preview) whose article it can confirm:

    the article's lead, and up to four of its sections (history, how it is made or where it
    is found, uses, safety), each cut at a sentence so a page stays readable on a phone
    the measured values from the article's infobox, or failing that from Wikidata: melting
    and boiling points (with "decomposes" and "sublimes" kept as a note instead of a false
    number), density, appearance, odour and solubility in water
    the article's title, link and revision date, for the credit under the text

and for the curriculum (tools/data/curriculum.py): each topic's lead and link, and which
topics explain each reaction, each vessel and each era. And the glossary
(tools/data/glossary.py): every term's definition and links, and which terms each substance's
page and each lesson uses.

An article is used for a substance only when it is the substance's own (the link the content
gives it, or the one Wikidata files under its CAS number or PubChem record), or, found by
name, when its Wikidata formula matches. Values that contradict each other (a boiling point
below the melting point) are left out rather than shown.

    python tools/data/gen_pages.py            write assets/data/pages.ron
    python tools/data/gen_pages.py --check    report only
    python tools/data/gen_pages.py --show ID  print one substance's page as it will be written

Without the scrape it still writes the curriculum (titles and links, no text), so the game
builds; run scrape_wiki.py first for the real thing.
"""
import argparse
import html
import json
import lzma
import re
import sys
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import curriculum  # noqa: E402
import glossary  # noqa: E402

SCRAPE = ROOT / "library" / "wiki" / "pages.jsonl.xz"
DATA = ROOT / "assets" / "data"
OUT = DATA / "pages.ron"

LEAD_MAX = 1600          # characters of an article's lead kept
SECTION_MAX = 900        # characters of each section kept
TOPIC_LEAD_MAX = 1400
SECTIONS = [             # (heading on the page, what the article's own headings look like)
    ("History", r"histor|discover|etymolog|naming|name\b|origin"),
    ("Production", r"production|producing|manufactur|synthe|prepar|isolat|extraction|refin|industrial|biosynth"),
    ("Where it's found", r"occurren|natural|abundance|in nature|sources?\b|mineral"),
    ("Uses", r"\buses?\b|applicat|usage|purpose|role|in medicine|medical use|food|cooking"),
    ("Safety", r"safety|toxic|hazard|health|precaution|environment|adverse|side effect"),
]
MAX_SECTIONS = 4
SKIP_HEADINGS = r"references|see also|external links|notes|further reading|bibliography|gallery|citations|sources$"

SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
UNIT_C, UNIT_K, UNIT_F = "Q25267", "Q11579", "Q42289"
DENSITY_UNITS = {"Q13147228": 1.0, "Q844211": 0.001, "Q834105": 0.001, "Q21604951": 1.0}


# --------------------------------------------------------------------------------------
# Reading the game's data
# --------------------------------------------------------------------------------------
TOK = re.compile(r'\s+|//[^\n]*|#!\[[^\]]*\]|"(?:[^"\\]|\\.)*"|-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?'
                 r'|[A-Za-z_][A-Za-z0-9_]*|[(){}\[\]:,]', re.S)


def read_ron(path):
    """A RON file as plain Python values (structs become dicts, enums {name: [args]})."""
    text = path.read_text(encoding="utf-8")
    toks, pos = [], 0
    for m in TOK.finditer(text):
        if m.start() != pos:
            raise ValueError(f"{path.name}: can't read at {pos}")
        pos = m.end()
        t = m.group(0)
        if not (t[0].isspace() or t.startswith("//") or t.startswith("#!")):
            toks.append(t)
    i = 0

    def unq(t):
        s, out, j = t[1:-1], [], 0
        while j < len(s):
            c = s[j]
            if c == "\\":
                n = s[j + 1]
                j += 2
                if n == "u":
                    k = s.index("}", j)
                    out.append(chr(int(s[j + 1:k], 16)))
                    j = k + 1
                else:
                    out.append({"n": "\n", "t": "\t"}.get(n, n))
            else:
                out.append(c)
                j += 1
        return "".join(out)

    def val():
        nonlocal i
        t = toks[i]
        i += 1
        if t[0] == '"':
            return unq(t)
        if t in "([{":
            end = {"(": ")", "[": "]", "{": "}"}[t]
            if t == "(" and re.match(r"[A-Za-z_]", toks[i]) and toks[i + 1] == ":":
                d = {}
                while toks[i] != end:
                    k = toks[i]
                    i += 2
                    d[k] = val()
                    if toks[i] == ",":
                        i += 1
                i += 1
                return d
            if t == "{":
                d = {}
                while toks[i] != end:
                    k = val()
                    i += 1
                    d[k] = val()
                    if toks[i] == ",":
                        i += 1
                i += 1
                return d
            out = []
            while toks[i] != end:
                out.append(val())
                if toks[i] == ",":
                    i += 1
            i += 1
            return out
        if t == "None":
            return None
        if t in ("true", "false"):
            return t == "true"
        if t == "Some":
            i += 1
            v = val()
            if toks[i] == ",":
                i += 1
            i += 1
            return v
        if re.match(r"-?\d", t):
            return float(t) if re.search(r"[.eE]", t) else int(t)
        if i < len(toks) and toks[i] == "(":
            i += 1
            args = []
            while toks[i] != ")":
                args.append(val())
                if toks[i] == ",":
                    i += 1
            i += 1
            return {t: args}
        return t

    v = val()
    return v[0] if isinstance(v, list) and len(v) == 1 else v


def game_substances():
    """id -> {name, formula, props, desc_source, lib_mp, lib_bp, lib_density} for every
    substance the game ships, as the game merges them (library, then the authored layer)."""
    lib = read_ron(DATA / "substances.ron")
    au = read_ron(DATA / "authored_substances.ron")
    out = {}
    for sid in au:
        base = lib.get(sid, {})
        patch = au[sid]
        out[sid] = {
            "name": patch.get("name") or base.get("name") or f"#{sid}",
            "state": patch.get("state") or base.get("state"),
            "formula": patch.get("formula") or base.get("formula") or "",
            "props": patch.get("properties") or base.get("properties") or [],
            "stage": patch.get("stage"),
            "link": next((u for _, u in patch.get("references") or []), None),
            "description": patch.get("description") or base.get("description") or "",
            "element": bool(base.get("element_info")),
            "lib_mp": base.get("melting_point_c"), "lib_bp": base.get("boiling_point_c"),
            "lib_density": base.get("density_g_cm3"),
        }
    return out


def game_reactions():
    r = read_ron(DATA / "authored_reactions.ron")
    return r["reactions"], [e["name"] for e in r["epochs"]]


# --------------------------------------------------------------------------------------
# Text
# --------------------------------------------------------------------------------------
def strip_math(t):
    """Drop the {\\displaystyle ...} blocks the plain-text extracts leave where an article
    has a formula typeset as maths."""
    out, i = [], 0
    while True:
        j = t.find("{\\displaystyle", i)
        if j < 0:
            out.append(t[i:])
            break
        out.append(t[i:j])
        depth, k = 0, j
        while k < len(t):
            if t[k] == "{":
                depth += 1
            elif t[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        i = k + 1
    return "".join(out)


def clean(t):
    t = strip_math(t or "")
    t = re.sub(r"\(\s*[;,]?\s*\)", "", t)                 # pronunciations the extract left empty
    t = re.sub(r"\(\s*[;,]\s*", "(", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r" +([,.;:)])", r"\1", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def split_sections(text):
    """(lead, [(level, heading, body)]) from an extract with == headings ==."""
    parts = re.split(r"^(={2,6})\s*(.*?)\s*\1\s*$", text or "", flags=re.M)
    lead = parts[0]
    out = []
    for k in range(1, len(parts) - 2, 3):
        out.append((len(parts[k]), parts[k + 1], parts[k + 2]))
    return lead, out


def clip(text, limit):
    """Whole paragraphs up to `limit` characters; a first paragraph longer than that is cut
    after its last full sentence that fits."""
    paras = [p.strip() for p in clean(text).split("\n") if p.strip()]
    out, used = [], 0
    for p in paras:
        if used + len(p) <= limit:
            out.append(p)
            used += len(p) + 2
            continue
        if not out:
            cut = p[:limit]
            ends = [m.end() for m in re.finditer(r"[.!?](?=\s+[A-Z(\"'])", cut)]
            if ends and ends[-1] > limit * 0.35:
                out.append(cut[:ends[-1]])
        break
    return "\n\n".join(out)


def pick_sections(sections):
    """Up to MAX_SECTIONS of the article's top-level sections, by what they are about, in the
    order SECTIONS gives; a section's subsections are read as part of it."""
    tops = []
    for level, head, body in sections:
        if level == 2:
            tops.append([head, body])
        elif tops:
            tops[-1][1] += "\n" + body
    chosen, used = [], set()
    for label, pat in SECTIONS:
        for i, (head, body) in enumerate(tops):
            if i in used or re.search(SKIP_HEADINGS, head, re.I) or not re.search(pat, head, re.I):
                continue
            text = clip(body, SECTION_MAX)
            if len(text) >= 80:
                chosen.append((label, text))
                used.add(i)
                break
        if len(chosen) >= MAX_SECTIONS:
            break
    return chosen


# --------------------------------------------------------------------------------------
# Measured values
# --------------------------------------------------------------------------------------
def split_template(t):
    """'{{Name|a=b|c}}' -> ('Name', ['a=b', 'c']): split at the template's own bars, not
    those of the templates and links inside it."""
    inner = t.strip()[2:-2]
    parts, cur, depth, i = [], [], 0, 0
    while i < len(inner):
        two = inner[i:i + 2]
        if two in ("{{", "[["):
            depth += 1
            cur.append(two)
            i += 2
        elif two in ("}}", "]]"):
            depth = max(0, depth - 1)
            cur.append(two)
            i += 2
        elif inner[i] == "|" and depth == 0:
            parts.append("".join(cur))
            cur = []
            i += 1
        else:
            cur.append(inner[i])
            i += 1
    parts.append("".join(cur))
    return parts[0].strip(), parts[1:]


def first_template(v):
    """The first whole {{template}} in v, or None."""
    i = v.find("{{")
    if i < 0:
        return None
    depth, j = 0, i
    while j < len(v):
        if v.startswith("{{", j):
            depth += 1
            j += 2
        elif v.startswith("}}", j):
            depth -= 1
            j += 2
            if depth == 0:
                return v[i:j]
        else:
            j += 1
    return None


def params(box):
    """An infobox's parameters, keys lowercased with spaces and underscores dropped; a value
    is taken whole, however many lines its templates run over. Chembox sections (a value that
    is itself a Chembox template) are read into the same map."""
    # references and comments say all sorts (a cited source's own figures, a value
    # commented out): only what the infobox shows counts
    box = re.sub(r"<!--.*?-->", "", box or "", flags=re.S)
    box = re.sub(r"<ref[^>/]*/>|<ref[^>]*>.*?</ref>", "", box, flags=re.S)
    # a nowiki'd IUPAC name is full of brackets that aren't links
    box = re.sub(r"<nowiki>.*?</nowiki>", "", box, flags=re.S)
    out = {}

    def walk(t, depth=0):
        if depth > 3:
            return
        _, parts = split_template(t)
        for part in parts:
            if "=" not in part:
                continue
            k, v = part.split("=", 1)
            k = re.sub(r"[ _\n]", "", k.lower())
            v = v.strip()
            inner = first_template(v)
            if inner and re.match(r"^\{\{\s*(Chembox|Infobox)", inner, re.I):
                walk(inner, depth + 1)
            elif k and re.match(r"^[a-z][a-z0-9]*$", k):
                out.setdefault(k, v)

    tpl = first_template(box)
    if tpl:
        walk(tpl)
    return out


LIST_TEMPLATES = r"ubl|unbulleted list|plainlist|plain list|flatlist|hlist|bulleted list|ubil"


def unwiki(v):
    """Wikitext to plain words: links to their text, lists joined, number templates read,
    anything else dropped. None when markup would be left over."""
    v = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>|<!--.*?-->", "", v or "", flags=re.S)
    v = re.sub(r"<br\s*/?>", "; ", v)
    v = re.sub(r"<su[bp]>(.*?)</su[bp]>", r"\1", v)
    v = re.sub(r"<[^>]+>", "", v)
    v = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", v)
    for _ in range(200):
        # the innermost template first
        t = re.search(r"\{\{([^{}]*)\}\}", v)
        if not t:
            break
        name, args = split_template(t.group(0))
        n = name.lower().strip()
        plain = [a.strip() for a in args if "=" not in a or re.match(r"^\s*\d", a)]
        named = dict(a.split("=", 1) for a in args if "=" in a and not re.match(r"^\s*\d", a))
        if re.fullmatch(LIST_TEMPLATES, n):
            rep = "; ".join(a.lstrip("* ").strip() for a in plain if a.strip())
        elif n in ("nowrap", "nobr", "chem", "chem2", "ce", "small", "abbr", "lang", "nowrap begin"):
            rep = "".join(plain[:1] if n in ("abbr", "lang") else plain)
        elif n in ("val", "convert", "cvt"):
            unit = named.get("u") or named.get("ul") or (plain[1] if len(plain) > 1 and n != "val" else "")
            unit = "°" + unit if unit.strip() in ("C", "F") else unit
            exp = named.get("e", "").strip()
            rep = (plain[0] if plain else "") + ("×10^" + exp if exp else "") + (" " + unit.strip() if unit else "")
        elif n in ("nbsp", "nnbsp", "thinsp", "spaces", "nbhyph"):
            rep = " "
        elif n == "e":
            rep = "×10^" + (plain[0] if plain else "")
        elif n in ("sup", "sub"):
            rep = plain[0] if plain else ""
        else:
            rep = ""
        v = v[:t.start()] + rep + v[t.end():]
    v = html.unescape(v.replace("&minus;", "-")).replace("\xa0", " ").replace("''", "")
    v = re.sub(r"\(\s*[^()]*=\s*\)", "", v)        # "(Ksp at 25 °C = )": a value that was a template
    v = re.sub(r"\(\s*\)", "", v)
    v = re.sub(r"\s+", " ", v)
    v = re.sub(r"\s*,?\s*;\s*", "; ", v)      # list items, however they were separated
    v = re.sub(r":;\s*", ": ", v).strip(" ,;")
    # markup left over (a template we don't read, a parameter that leaked in)
    if re.search(r"\{\{|\}\}|\[\[|\]\]|\||^\s*\w+\s*=|\w=", v):
        return None
    return v or None


def one_end(v):
    """'175-176 °C' / '175 to 176 °C' -> '175 °C': a range reads as its low end, and its
    dash is not a minus sign."""
    v = (v or "").replace("−", "-").replace("&minus;", "-").replace("&ndash;", "–")
    return re.sub(r"(-?\d+(?:\.\d+)?)\s*(?:-|–|to)\s*-?\d+(?:\.\d+)?", r"\1", v)


def first_number(v):
    v = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>|<!--.*?-->", "", v or "", flags=re.S)
    v = v.replace("−", "-").replace("&minus;", "-").replace("–", " ").replace(",", "")
    m = re.search(r"\{\{\s*(?:val|convert|cvt)\s*\|\s*(-?\d+(?:\.\d+)?)", v, re.I)
    if m:
        return float(m.group(1))
    m = re.search(r"(?<![\w.])(-?\d+(?:\.\d+)?)", v)
    return float(m.group(1)) if m else None


def infobox_temp(p, what):
    """(°C or None, note) for 'melting' or 'boiling' from an infobox's parameters."""
    key = {"melting": "meltingpt", "boiling": "boilingpt"}[what]
    alt = {"melting": "meltingpoint", "boiling": "boilingpoint"}[what]
    notes = " ".join(p.get(k, "") for k in (key + "notes", alt + "notes", what + "notes", key, alt, key + "c",
                                            alt + "c", what + "high"))
    note = None
    if re.search(r"decompos", notes, re.I):
        note = "decomposes"
    elif re.search(r"sublim", notes, re.I):
        note = "sublimes"
    for suffix, conv in (("c", lambda x: x), ("k", lambda x: x - 273.15), ("f", lambda x: (x - 32) * 5 / 9)):
        for k in (key + suffix, alt + suffix, f"{alt}{suffix}"):
            if p.get(k):
                n = first_number(p[k])
                if n is not None:
                    return conv(n), note
    raw = p.get(key) or ""
    if raw:
        m = re.search(r"(-?\d+(?:\.\d+)?)\s*(?:°|&deg;)?\s*([CFK])\b", one_end(raw).replace(",", ""))
        if m:
            n, u = float(m.group(1)), m.group(2)
            return (n if u == "C" else n - 273.15 if u == "K" else (n - 32) * 5 / 9), note
    # a drug's infobox gives melting_point / boiling_point as bare numbers in °C
    raw = p.get(alt) or ""
    if raw:
        n = first_number(raw)
        m = re.search(r"(-?\d+(?:\.\d+)?)\s*(?:°|&deg;)?\s*([CFK])\b", one_end(raw).replace(",", ""))
        if m:
            n, u = float(m.group(1)), m.group(2)
            return (n if u == "C" else n - 273.15 if u == "K" else (n - 32) * 5 / 9), note
        if n is not None and not re.search(r"[A-Za-z]{3,}", unwiki(raw) or ""):
            return n, note
    return None, note


def infobox_density(p):
    for k in ("density", "densitygpcm3nrt", "densitygpcm3", "densitygplstp"):
        v = p.get(k)
        if not v:
            continue
        n = first_number(v)
        if n is None:
            continue
        if k == "densitygplstp" or re.search(r"g\s*/\s*(?:L|l|dm)\b|kg\s*/\s*m", v):
            n /= 1000.0
        if 0 < n < 30:
            return n
    return None


def wd_temp(entity, name):
    """°C from Wikidata's melting or boiling point (preferred rank first; at normal pressure)."""
    sts = (entity or {}).get("claims", {}).get(name, [])
    sts = sorted(sts, key=lambda s: not s.get("preferred"))
    for s in sts:
        v = s["value"]
        if not isinstance(v, dict):
            continue
        press = (s.get("q") or {}).get("P2077")
        if press and isinstance(press[0], dict) and abs(press[0]["amount"] - 1) > 0.05 and press[0].get("unit") == "Q177974":
            continue
        a, u = v["amount"], v.get("unit")
        if u == UNIT_C:
            return a
        if u == UNIT_K:
            return a - 273.15
        if u == UNIT_F:
            return (a - 32) * 5 / 9
    return None


def wd_density(entity):
    for s in (entity or {}).get("claims", {}).get("density", []):
        v = s["value"]
        if isinstance(v, dict) and v.get("unit") in DENSITY_UNITS:
            n = v["amount"] * DENSITY_UNITS[v["unit"]]
            if 0 < n < 30:
                return n
    return None


def facts(page, entity, templates):
    """Measured values for a substance, the infobox first and Wikidata where it has none."""
    boxes = list(page.get("infobox") or [])
    for b in list(boxes):
        m = re.match(r"^\{\{\s*(Infobox [^|{}]+?)\s*\}\}$", b.strip(), re.I)
        if m:
            t = templates.get("Template:" + m.group(1)[0].upper() + m.group(1)[1:])
            if t:
                boxes.append(t)
    p = {}
    for b in boxes:
        for k, v in params(b).items():
            p.setdefault(k, v)
    mp, mnote = infobox_temp(p, "melting")
    bp, bnote = infobox_temp(p, "boiling")
    src = {"mp": "Wikipedia" if mp is not None else None, "bp": "Wikipedia" if bp is not None else None}
    if mp is None and mnote is None:
        mp = wd_temp(entity, "melting_point")
        src["mp"] = "Wikidata" if mp is not None else None
    if bp is None and bnote is None:
        bp = wd_temp(entity, "boiling_point")
        src["bp"] = "Wikidata" if bp is not None else None
    out = {"melting_c": mp, "boiling_c": bp, "mnote": mnote, "bnote": bnote, "temp_source": src}
    d = infobox_density(p)
    out["density"] = d if d is not None else wd_density(entity)
    for k, key in (("appearance", "appearance"), ("odor", "odor"), ("odor", "odour")):
        v = fit(unwiki(p.get(key, "")), 120)
        if v and not out.get(k):
            out[k] = v[0].upper() + v[1:]
    sol = unwiki(p.get("solubility", "") or p.get("solubilityinwater", "")) or ""
    if re.fullmatch(r"[\d.]+", sol or ""):
        sol += " mg/mL"   # a drug's infobox gives the number alone, in mg/mL
    sol = fit(sol, 80)
    if sol and re.fullmatch(r"[<>≤≥~]?\s*[\d.,]+", sol):
        sol = None        # a bare number with no unit says nothing
    if sol:
        out["solubility"] = sol
    return out


def fit(v, limit):
    """v if it fits in limit characters; for a list ('a; b; c'), as many of its first items
    as fit. None when not even the first does."""
    if not v:
        return None
    if len(v) <= limit:
        return v
    kept = []
    for item in v.split("; "):
        if len("; ".join(kept + [item])) > limit:
            break
        kept.append(item)
    return "; ".join(kept) or None


# Whether a library melting or boiling point the article doesn't confirm is kept (when it
# doesn't contradict anything). gen_pages.py --check reports how often the library agrees
# with the articles where both have a value.
KEEP_LIBRARY_TEMPS = True


def checked_values(sub, f):
    """The values the game shows for a substance: the article's (or Wikidata's) first, the
    library's where those have none and it is consistent; "decomposes" and "sublimes" said
    as a note; a boiling point below the melting point never. f: facts(), or None."""
    f = f or {}
    mnote, bnote = f.get("mnote"), f.get("bnote")
    mp, bp = f.get("melting_c"), f.get("boiling_c")
    lmp, lbp = sub.get("lib_mp"), sub.get("lib_bp")
    lib_ok = KEEP_LIBRARY_TEMPS and not (lmp is not None and lbp is not None and lmp > lbp)
    if mp is None and mnote is None and lib_ok:
        mp = lmp
    if bp is None and bnote is None and lib_ok:
        bp = lbp
    note = None
    if "sublimes" in (mnote, bnote):
        # no liquid at normal pressure: the one temperature worth giving is the sublimation's
        t = f.get("boiling_c") if f.get("boiling_c") is not None else f.get("melting_c")
        note = f"Sublimes at {fmt_c(t)}" if t is not None else "Sublimes"
        mp = bp = None
    elif "decomposes" in (mnote, bnote):
        t = f.get("boiling_c") if bnote == "decomposes" else f.get("melting_c")
        note = f"Decomposes at {fmt_c(t)}" if t is not None else "Decomposes on heating"
        bp = None
        if mnote == "decomposes":
            mp = None
    if mp is not None and bp is not None and mp > bp + 0.5:
        # the sources disagree: keep the article's, drop what came from the library
        if f.get("melting_c") is not None and f.get("boiling_c") is None:
            bp = None
        elif f.get("boiling_c") is not None and f.get("melting_c") is None:
            mp = None
        else:
            mp = bp = None
    # a value far from the state the game gives it at room temperature is a slip in one of
    # the sources (or the article is about the pure compound of a solution the game uses):
    # better unsaid. Liquefied gases ("Liquid Nitrogen") are liquid on purpose.
    state, cryo = sub.get("state"), (sub.get("name") or "").startswith("Liquid ")
    if state == "Liquid" and mp is not None and mp > 60:
        mp = None
    if state == "Liquid" and bp is not None and bp < -30 and not cryo:
        bp = None
    if state == "Solid" and mp is not None and mp < -30:
        mp = None
    if state == "Gas" and bp is not None and bp > 80:
        bp = None
    density = f.get("density") if f.get("density") is not None else sub.get("lib_density")
    return {"melting_c": mp, "boiling_c": bp, "density": density, "phase_note": note}


def fmt_c(t):
    v = f"{t:.0f}" if abs(t) >= 10 else f"{t:.1f}"
    return v.replace("-", "\u2212") + " °C"


# --------------------------------------------------------------------------------------
# Choosing a substance's article
# --------------------------------------------------------------------------------------
def hill(formula):
    try:
        from gen_authored import atoms
        f = (formula or "").translate(SUB).replace(" ", "")
        f = re.sub(r"[⁺⁻⁰¹²³⁴⁵⁶⁷⁸⁹+−-]+$", "", f)
        # a polymer's repeat unit: (C2H3Cl)n -> C2H3Cl
        f = re.sub(r"^\((.+)\)[nₙ]$", r"\1", f)
        a = atoms(f)
        return tuple(sorted(a.items())) if a else None
    except Exception:
        return None


def same_formula(ours, entity):
    """True when the article's Wikidata formula is ours (or a whole multiple of it, as a
    polymer's repeat unit or a dimer is, or ours with water or a counter-ion the other
    records leave out); False when it is another compound's; None when either is unknown."""
    want = hill(ours)
    if not want:
        return None
    got = [hill(s["value"]) for s in (entity or {}).get("claims", {}).get("formula", []) if isinstance(s["value"], str)]
    got = [g for g in got if g]
    if not got:
        return None
    w = dict(want)
    for g in got:
        g = dict(g)
        if g == w:
            return True
        if set(g) == set(w):
            # whole multiples, element by element
            r = {e: g[e] / w[e] for e in w}
            if len({round(x, 3) for x in r.values()}) == 1:
                return True
        # the same skeleton with water, or a salt against its acid: carbon, nitrogen and the
        # heavy atoms agree, hydrogen and oxygen may not
        core = lambda d: {e: n for e, n in d.items() if e not in ("H", "O", "Na", "K", "Cl", "Li")}  # noqa: E731
        if core(g) and core(g) == core(w):
            return True
    return False


def plain(name):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\s*\([^)]*\)", "", (name or "").lower()))


def choose(rec, pages, entities):
    """(article, how, about) for a substance: `about` is None when the article is the
    substance's own, else the article's title, for one the content links on purpose for a
    related subject (an oxide to its element, an intermediate to the drug it makes, a crop to
    what is made from it): its text is shown under that title, and its values not used.
    (None, reason, None) when no article is confirmed."""
    for c in rec["candidates"]:
        page = pages.get(c["pageid"])
        if not page or page.get("missing") or c.get("disambiguation") or page.get("disambiguation"):
            continue
        if not page.get("full"):
            continue
        ent = entities.get(page.get("wikibase"))
        how = c["how"]
        match = same_formula(rec["formula"], ent)
        t, n = plain(page["title"]), plain(rec["name"])
        named = t in (n, n.rstrip("s"), n + "s", n + "es") or (len(t) > 3 and t == plain(re.sub(r".*\((.*)\).*", r"\1", rec["name"])))
        if match or named:
            return page, how, None
        if how.startswith("own"):
            # the content's own link: a related subject when the formulas differ or can't be
            # told (an oxide's element, the drug an intermediate makes, a crop's plant)
            return page, how, page["title"]
        if match is None and how in ("own-curid", "cas", "pubchem"):
            return page, how, None
        # anything else is another compound's article (a wrong link in the records): next
    return None, "no article confirmed", None


def current(rec, sub):
    """The scrape's record with its own-link candidates dropped when the content has changed
    that link since the scrape (a wrong link fixed): the fixed one is fetched next time."""
    from scrape_wiki import parse_link
    old = [tuple(l[1:]) for l in rec["links"] if l[0] == "own"]
    now = parse_link(sub.get("link"))
    if not old or (now and old[0] == now):
        return rec
    return dict(rec, candidates=[c for c in rec["candidates"] if not c["how"].startswith("own")])


def wrong_links(subs, scrape):
    """Links the content gives that lead to another compound's article (for fixing)."""
    out = []
    for sid, rec in scrape["subs"].items():
        for c in rec["candidates"]:
            if c["how"] not in ("own-curid", "cas", "pubchem"):
                continue
            page = scrape["pages"].get(c["pageid"]) or {}
            ent = scrape["entities"].get(page.get("wikibase"))
            if page.get("title") and same_formula(rec["formula"], ent) is False and plain(page["title"]) != plain(rec["name"]):
                out.append(f"{sid} {rec['name']} ({rec['formula']}): {c['how']} -> {page['title']}")
    return out


# --------------------------------------------------------------------------------------
# The curriculum's links
# --------------------------------------------------------------------------------------
def reaction_topics(r, subs, title_topic):
    text = r.get("name", "")
    desc = r.get("description") or ""
    found = []

    def add(keys):
        for k in keys:
            if k not in found:
                found.append(k)

    for _, url in r.get("references") or []:
        if "wikipedia.org/wiki/" in url:
            t = urllib.parse.unquote(url.split("/wiki/", 1)[1]).replace("_", " ").split("#")[0]
            if t.lower() in title_topic:
                add([title_topic[t.lower()]])
    for pat, keys in curriculum.NAME_RULES:
        if re.search(pat, text, re.I):
            add(keys)
    if len(found) < 2:
        for pat, keys in curriculum.NAME_RULES:
            if keys[0] not in curriculum.NAME_ONLY and re.search(pat, desc, re.I):
                add(keys[:1])
                if len(found) >= 2:
                    break
    rs = [subs.get(x["substance_id"], {}) for x in r.get("reactants", [])]
    ps = [subs.get(x["substance_id"], {}) for x in r.get("products", [])]
    props = lambda xs, p: any(p in (x.get("props") or []) for x in xs)  # noqa: E731
    P = curriculum.PROPERTY_TOPICS
    if props(rs, "IsAcid") and props(rs, "IsBase"):
        add(P["neutralisation"])
    elif props(rs, "IsAcid") and props(rs, "IsMetal"):
        add(P["metal_in_acid"])
    if props(ps, "IsRadioactive"):
        add(P["radioactive"])
    if any("RequiresCatalyst" in c for c in r.get("conditions", []) if isinstance(c, dict)):
        add(P["catalyst"])
    if props(ps, "IsMedicine"):
        add(P["medicine"])
    if props(ps, "IsPolymer"):
        add(P["polymer"])
    found = found[:curriculum.MAX_REACTION_TOPICS]
    dh = r.get("enthalpy_change_kj_mol") or 0
    if len(found) < curriculum.MAX_REACTION_TOPICS and abs(dh) >= 1:
        add(P["exothermic"] if dh < 0 else P["endothermic"])
    return found[:curriculum.MAX_REACTION_TOPICS]


# --------------------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------------------
def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def opt_num(v, digits=4):
    return "None" if v is None else f"Some({round(float(v), digits)!r})"


def opt_str(v):
    return "None" if not v else f"Some({q(v)})"


def wiki_url(title):
    return "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe="(),'_-.:")


def load_scrape(path):
    if not path.exists():
        return None
    S = defaultdict(dict)
    with lzma.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            t = r["type"]
            if t == "substance":
                S["subs"][r["id"]] = r
            elif t == "page":
                S["pages"][r["pageid"]] = r
            elif t == "entity":
                S["entities"][r["qid"]] = r
            elif t == "topic":
                S["topics"][r["key"]] = r
            elif t == "template":
                S["templates"][r["title"]] = r.get("wikitext")
            elif t == "meta":
                S["meta"] = r
    return S


# --------------------------------------------------------------------------------------
# Glossary
# --------------------------------------------------------------------------------------
# Most terms a page lists; past this, the row under the page stops helping.
TERMS_MAX = 12


def term_matcher():
    """A regex finding every glossary form as a whole word (not after a hyphen: 'non-toxic'
    isn't the glossary's 'toxic'), longest first, and a map from a match back to its term.
    The game finds the same words with the same rules (src/ui/glossary.rs)."""
    owner, alts = {}, []
    for key, t in glossary.TERMS.items():
        for f in t["forms"]:
            k = f if not f.islower() else f.lower()
            assert k not in owner, f"glossary form {f!r} belongs to {owner.get(k)} and {key}"
            owner[k] = key
            alts.append(f)
    alts.sort(key=lambda f: (-len(f), f))
    pat = "|".join(re.escape(f) if not f.islower() else "(?i:" + re.escape(f) + ")" for f in alts)
    rx = re.compile(r"(?<![\w-])(?:" + pat + r")(?!\w)")

    def key_of(m):
        w = m.group(0)
        return owner.get(w) or owner.get(w.lower())
    return rx, key_of


def terms_in(texts, rx, key_of, skip=()):
    """The glossary terms the texts use, in order of first use, each followed by the terms
    it brings along; at most TERMS_MAX."""
    out = []
    for text in texts:
        for m in rx.finditer(text or ""):
            k = key_of(m)
            for k2 in [k] + glossary.TERMS[k]["also"]:
                if k2 not in out and k2 not in skip:
                    out.append(k2)
    return out[:TERMS_MAX]


def build(args):
    subs = game_substances()
    reactions, eras = game_reactions()
    scrape = load_scrape(Path(args.scrape) if args.scrape else SCRAPE)
    pages = scrape["pages"] if scrape else {}
    entities = scrape["entities"] if scrape else {}
    report = Counter()
    lines = ["// assets/data/pages.ron",
             "// GENERATED by tools/data/gen_pages.py from Wikipedia and Wikidata (fetched by",
             "// tools/data/scrape_wiki.py) and tools/data/curriculum.py. Article text is CC BY-SA 4.0",
             "// (credited on each page); Wikidata's values are CC0.",
             "(",
             "    units: [" + ", ".join(f"({q(k)}, {q(n)})" for k, n in curriculum.UNITS) + "],",
             "    topics: {"]
    title_topic = {}
    topic_text = {}
    by_title = {p.get("title", "").lower(): p for p in pages.values() if p.get("full") and not p.get("missing")}
    for key, (unit, kind, title) in curriculum.TOPICS.items():
        rec = (scrape or {}).get("topics", {}).get(key) if scrape else None
        page = pages.get(rec.get("pageid")) if rec and rec.get("pageid") and rec.get("asked") == title else None
        # a topic renamed since the scrape: its article may have been fetched for a substance
        page = page or by_title.get(title.lower())
        real = (page or {}).get("title") or (rec or {}).get("title") or title
        title_topic[title.lower()] = key
        title_topic[real.lower()] = key
        lead = clip(split_sections(page.get("text", ""))[0], TOPIC_LEAD_MAX) if page else ""
        report["topics with text" if lead else "topics without text"] += 1
        topic_text[key] = lead
        lines.append(f"        {q(key)}: (unit: {q(unit)}, kind: {kind}, title: {q(real)}, url: {q(wiki_url(real))}, "
                     f"lead: {q(lead)}),")
    lines.append("    },")

    # which topics explain what
    lines.append("    reactions: {")
    for r in reactions:
        ts = reaction_topics(r, subs, title_topic)
        report["reactions with topics" if ts else "reactions without topics"] += 1
        if ts:
            lines.append(f"        {r['id']}: [" + ", ".join(q(t) for t in ts) + "],")
    lines.append("    },")
    lines.append("    vessels: {")
    for p, ts in curriculum.VESSEL_TOPICS.items():
        lines.append(f"        {p}: [" + ", ".join(q(t) for t in ts) + "],")
    lines.append("    },")
    lines.append("    eras: {")
    for e, ts in curriculum.ERA_TOPICS.items():
        assert e in eras, f"era {e!r} isn't one of the game's"
        lines.append(f"        {q(e)}: [" + ", ".join(q(t) for t in ts) + "],")
    lines.append("    },")

    # the substances' pages
    lines.append("    substances: {")
    contradictions, unconfirmed = [], []
    found_values = {}
    shown_text = {sid: [sub.get("description") or ""] for sid, sub in subs.items()}
    for sid in sorted(subs):
        rec = (scrape or {}).get("subs", {}).get(sid) if scrape else None
        if not rec:
            report["substances not in the scrape"] += 1
            continue
        page, how, about = choose(current(rec, subs[sid]), pages, entities)
        if not page:
            unconfirmed.append(f"{sid} {subs[sid]['name']}: {how} ({len(rec['candidates'])} candidates)")
            report["substances without a confirmed article"] += 1
            continue
        report[f"article found by {how}"] += 1
        lead, sections = split_sections(page.get("text", ""))
        lead = clip(lead, LEAD_MAX)
        chosen = pick_sections(sections)
        f = facts(page, entities.get(page.get("wikibase")), scrape["templates"])
        if about:
            # the related subject's values aren't this substance's
            report["pages on a related subject"] += 1
            f = {}
        else:
            found_values[sid] = f
        report["sections"] += len(chosen)
        shown_text[sid] += [lead] + [t for _, t in chosen]
        revised = (page.get("timestamp") or "")[:10]
        secs = ", ".join(f"({q(h)}, {q(t)})" for h, t in chosen)
        lines.append(
            f"        {sid}: (title: {q(page['title'])}, url: {q(wiki_url(page['title']))}, revised: {q(revised)}, "
            f"about: {opt_str(about)}, summary: {opt_str(page.get('shortdesc'))}, lead: {q(lead)}, sections: [{secs}], "
            f"appearance: {opt_str(f.get('appearance'))}, odor: {opt_str(f.get('odor'))}, "
            f"solubility: {opt_str(f.get('solubility'))}),")
        if args.show and sid == args.show:
            print(json.dumps({"page": page["title"], "how": how, "about": about, "lead": lead, "sections": chosen, "facts": f,
                              "shown": checked_values(subs[sid], f)}, ensure_ascii=False, indent=1))
    lines.append("    },")

    # the measured values, checked: every substance whose values change from the library's
    lines.append("    values: {")
    agree = Counter()
    for sid in sorted(subs):
        sub, f = subs[sid], found_values.get(sid)
        for k, lk in (("melting_c", "lib_mp"), ("boiling_c", "lib_bp")):
            if f and f.get(k) is not None and sub.get(lk) is not None:
                agree["agree" if abs(f[k] - sub[lk]) <= 3 else "differ"] += 1
        v = checked_values(sub, f)
        if f and f.get("melting_c") is not None and f.get("boiling_c") is not None and f["melting_c"] > f["boiling_c"] + 0.5:
            contradictions.append(f"{sid} {sub['name']}: melts {f['melting_c']:.1f}, boils {f['boiling_c']:.1f}")
        same = (v["melting_c"] == sub.get("lib_mp") and v["boiling_c"] == sub.get("lib_bp")
                and v["density"] == sub.get("lib_density") and not v["phase_note"])
        if same:
            continue
        for k in ("melting_c", "boiling_c", "density", "phase_note"):
            if v[k] is not None:
                report[f"shows {k}"] += 1
        lines.append(f"        {sid}: (melting_c: {opt_num(v['melting_c'], 2)}, boiling_c: {opt_num(v['boiling_c'], 2)}, "
                     f"density: {opt_num(v['density'], 5)}, phase_note: {opt_str(v['phase_note'])}),")
    lines.append("    },")

    # the glossary, and which terms each page uses
    rx, key_of = term_matcher()
    lines.append("    glossary: {")
    for key, t in glossary.TERMS.items():
        lesson = t["lesson"] or title_topic.get(t["wiki"].lower())
        assert lesson is None or lesson in curriculum.TOPICS, f"glossary {key}: no lesson {lesson!r}"
        forms = ", ".join(q(f) for f in t["forms"])
        lines.append(f"        {q(key)}: (term: {q(t['term'])}, text: {q(t['text'])}, url: {q(wiki_url(t['wiki']))}, "
                     f"lesson: {opt_str(lesson)}, forms: [{forms}]),")
    lines.append("    },")
    used = Counter()
    lines.append("    substance_terms: {")
    for sid in sorted(subs):
        ks = terms_in(shown_text[sid], rx, key_of)
        used.update(ks)
        report["substances with glossary terms"] += bool(ks)
        if ks:
            lines.append(f"        {sid}: [" + ", ".join(q(k) for k in ks) + "],")
    lines.append("    },")
    lines.append("    topic_terms: {")
    for key in curriculum.TOPICS:
        # a lesson doesn't define its own subject back to itself
        own = {k for k, t in glossary.TERMS.items() if t["lesson"] == key}
        ks = terms_in([topic_text.get(key, "")], rx, key_of, skip=own)
        used.update(ks)
        if ks:
            lines.append(f"        {q(key)}: [" + ", ".join(q(k) for k in ks) + "],")
    lines.append("    },")
    unused = [k for k in glossary.TERMS if not used[k]]
    report["glossary terms"] = len(glossary.TERMS)
    report["glossary terms no page uses"] = len(unused)
    lines += [")", ""]
    if unused and args.verbose:
        print("Glossary terms no page uses:", ", ".join(unused))
    if agree:
        print(f"library temperatures vs the articles: {agree['agree']} agree within 3 °C, {agree['differ']} differ")
    text = "\n".join(lines)

    for k in sorted(report):
        print(f"{k:40s} {report[k]}")
    if not scrape:
        print("No scrape found (library/wiki/pages.jsonl.xz): the curriculum is written without text.")
    if contradictions:
        print(f"{len(contradictions)} with a boiling point below the melting point, left out:")
        for c in contradictions[:20]:
            print("  ", c)
    if scrape and args.verbose:
        wl = wrong_links(subs, scrape)
        print(f"{len(wl)} links in the content lead to another compound's article:")
        for w in wl:
            print("  ", w)
    if unconfirmed and args.verbose:
        print("Without a confirmed article:")
        for u in unconfirmed:
            print("  ", u)
    print(f"pages.ron                                {len(text.encode()) / 1e6:.1f} MB")
    if not args.check:
        OUT.write_text(text, encoding="utf-8")
        print(f"wrote {OUT}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    ap.add_argument("--show", type=int, help="print one substance's page")
    ap.add_argument("--verbose", action="store_true", help="list the substances without a confirmed article")
    ap.add_argument("--scrape", help="read this export instead of library/wiki/pages.jsonl.xz")
    build(ap.parse_args())


if __name__ == "__main__":
    main()
