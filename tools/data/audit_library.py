"""
Licence audit of the scraped substance library (library/substances.ron): where each
piece of text came from, and whether its licence lets the game ship it.

Kept, and tagged with its source so the game can credit it under the text:
  description     Wikipedia article leads (CC BY-SA 4.0); NOAA CAMEO Chemicals ("X
                  appears as ...", US government work, public domain); ChEBI definitions
                  (CC BY 4.0); LOTUS natural-product records (CC0); and Curieosity's own
                  text (the hand-written entries below id 2000).
  appearance      physical-form words ("Liquid; Dry Powder"), NOAA/NTP/USCG descriptions
                  (public domain).
  uses            EPA Chemical Data Reporting use categories (public domain).
  hazard_summary  GHS hazard statements (the ECHA C&L Inventory, via PubChem; credited).
Removed: everything else. That is text from Haz-Map, HMDB, DrugBank, NCI/MeSH and
abstracts, whose terms are unclear or don't allow redistribution, and fragments the
scrape cut off mid-word. An in-play substance that loses its description gets one
written for it in tools/data/authored_pages.py (gen_authored.py checks this).

Identifying the source is pattern-based (each source writes in its own recognisable
style). --verify-wikipedia confirms every "Wikipedia" description against the live
article's summary, and needs network access:

    python tools/data/audit_library.py                         report only
    python tools/data/audit_library.py --write                 rewrite substances.ron
    python tools/data/audit_library.py --source OLD.ron --write    audit an original scrape
    python tools/data/audit_library.py --verify-wikipedia      check against Wikipedia
    python tools/data/audit_library.py --list unsure           print the ids of one kind

The rewrite is idempotent: running it on an audited file changes nothing. After writing,
run pack_library.py (or gen_authored.py, which runs it) so the game's packed copy follows.
"""
import argparse
import collections
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "library" / "substances.ron"

# --- telling the sources apart ---------------------------------------------------------
# Text other databases write, which the scrape sometimes picked up instead of Wikipedia's.
FOREIGN = [
    r"\[(?:IUCLID|HSDB|Merck|ACGIH|NIOSH|ICSC|CHRIS|EPA|HMDB|DrugBank|Wikipedia|Reference|ILO|ATSDR"
    r"|IARC|Hawley|NTP|CAMEO|MSDS|Alfa|Sigma|AIHA|Calbiochem|ChemIDplus)[^\]]*\]",
    r"only found in individuals that have used or taken",
    r"belongs to the class of organic compounds known as",
    r"is a metabolite found in or produced by",
    r"Based on a literature review",
    r"has been detected, but not quantified",
    r"has been found in human",
    r"can be found in a number of food items",
    r"is a potentially toxic compound",
    r"Outside of the human body",
    r"uremic toxin",
    r"biomarker for the consumption",
    r"is a primary metabolite",
    r"is indicated for",
    r"was approved by the (?:US )?FDA",
    r"is an? (?:FDA|approved) drug",
    r"Pharmacodynamics",
    r"Mechanism of action",
    r"^Used ",
    r"^Has been used",
    r"is a (?:drug|small molecule)\b",
    r"induces? .{0,40}tumou?rs in rats",
    r"\(NCI(?: Thesaurus)?\)",
    r"\(MeSH\)",
    r"is the (?:anhydrous|hydrate|dihydrate|monohydrate)?,? ?(?:sodium|potassium|calcium) salt form of",
]
LOTUS = [r"is a natural product found in"]
CHEBI = [r"It has a role as", r"It is a conjugate (?:acid|base) of", r"It is functionally related to",
         r"It derives from a", r"It is a tautomer of", r"It is an enantiomer of"]
# Wikipedia's article leads: "X is an organic compound with the formula ...", "X, sold under
# the brand name Y, is a medication ...", "X is a colourless liquid ...".
WIKIPEDIA = [
    r"is an? (?:\w+ )?compound", r"with the (?:chemical |molecular )?formula", r"sold under the brand name",
    r"\(IUPAC", r"also known as", r"is a chemical element", r"is the (?:organic|inorganic|chemical) compound",
    r"is an? (?:colou?rless|white|yellow|pale|clear|black|red|brown|green|blue|grey|gray|orange|violet|purple)\b",
    r"is an? (?:\w+ )?(?:salt|ester|alkaloid|amino acid|polymer|mineral|alcohol|ketone|aldehyde|acid|base|gas"
    r"|liquid|solid|dye|pigment|alkane|alkene|alkyne|ether|amine|amide|isomer|derivative|oxide|halide|hydride"
    r"|nitrate|sulfate|chloride|carbonate|phenol|terpene|monoterpene|sugar|alloy|anion|cation|ion|oxyanion"
    r"|hydrocarbon|lactone|glycoside|flavonoid|steroid|hormone|vitamin|enzyme|protein)s?\b",
]

# The source tag written into the library, and what the game shows for it.
SOURCES = {
    "wikipedia": "Wikipedia",
    "cameo": "CAMEO Chemicals",
    "chebi": "ChEBI",
    "lotus": "LOTUS",
    "ours": "Curieosity",
}


def classify(sid, text):
    """The source of a description: one of SOURCES' keys, or 'foreign', 'uncertain'."""
    if any(re.search(p, text) for p in FOREIGN):
        return "foreign"
    if any(re.search(p, text) for p in LOTUS):
        return "lotus"
    if any(re.search(p, text) for p in CHEBI):
        return "chebi"
    if sid < 2000:
        return "ours"
    if re.match(r"^[^.]{0,90}\bappears as\b", text):
        return "cameo"
    if re.match(r"^(A|An) [a-z]", text):
        return "uncertain"  # a MeSH, NCIt or ChEBI definition: can't tell which
    if any(re.search(p, text[:500]) for p in WIKIPEDIA):
        return "wikipedia"
    return "uncertain"


def appearance_ok(text):
    if "[" in text:
        return False  # Haz-Map's tagged snippets
    if re.search(r"\((?:USCG|NTP|EPA|NIOSH|NOAA), ?\d{4}\)", text):
        return True  # US government records, public domain
    if re.match(r"^[^.]{0,90}\bappears as\b", text):
        return True  # NOAA CAMEO Chemicals
    return bool(re.fullmatch(r"[A-Za-z ,/()-]+(; ?[A-Za-z ,/()-]+)*", text)) and len(text) < 160


def use_ok(text):
    return "[" not in text and "…" not in text and not text.startswith(("For more", "...")) and len(text) < 90


# --- reading and rewriting the RON ----------------------------------------------------
STR = r'"((?:[^"\\]|\\.)*)"'
ENTRY = re.compile(r"\n    (\d+): \(")


def unescape(s):
    return s.replace('\\"', '"').replace("\\\\", "\\")


def audit_entry(sid, body, stats, kinds, verified):
    """Return the entry's text with unlicensed text removed and the source tagged."""
    m = re.search(r"\n( +)description: (None|Some\(" + STR + r"\)),", body, re.S)
    indent = m.group(1) if m else " " * 12
    # the source tag goes right after the description; drop any old one first
    body = re.sub(r"\n +text_source: (?:None|Some\(" + STR + r"\)),", "", body, flags=re.S)
    m = re.search(r"\n( +)description: (None|Some\(" + STR + r"\)),", body, re.S)
    if m and m.group(3) is not None:
        text = unescape(m.group(3))
        kind = classify(sid, text)
        if kind == "wikipedia" and verified is not None and sid in verified and not verified[sid]:
            kind = "uncertain"
        kinds[kind].append(sid)
        stats["description " + ("kept" if kind in SOURCES else "removed")] += 1
        if kind in SOURCES:
            tag = f'\n{indent}text_source: Some("{SOURCES[kind]}"),'
            body = body[: m.end()] + tag + body[m.end():]
        else:
            body = body[: m.start()] + f"\n{indent}description: None," + body[m.end():]
    # appearance
    m = re.search(r"\n( +)appearance: Some\(" + STR + r"\),", body, re.S)
    if m:
        if appearance_ok(unescape(m.group(2))):
            stats["appearance kept"] += 1
        else:
            stats["appearance removed"] += 1
            body = body[: m.start()] + f"\n{m.group(1)}appearance: None," + body[m.end():]
    # uses
    m = re.search(r"\n( +)uses: \[(.*?)\],\n", body, re.S)
    if m and m.group(2).strip():
        items = re.findall(STR, m.group(2))
        keep = [u for u in items if use_ok(unescape(u))]
        stats["uses kept"] += len(keep)
        stats["uses removed"] += len(items) - len(keep)
        if len(keep) != len(items):
            new = ", ".join(f'"{u}"' for u in keep)
            body = body[: m.start()] + f"\n{m.group(1)}uses: [{new}],\n" + body[m.end():]
    return body


def audit(text, verified=None):
    parts = ENTRY.split(text)
    out = [parts[0]]
    stats = collections.Counter()
    kinds = collections.defaultdict(list)
    for i in range(1, len(parts), 2):
        sid = int(parts[i])
        out.append(f"\n    {sid}: (")
        out.append(audit_entry(sid, parts[i + 1], stats, kinds, verified))
    return "".join(out), stats, kinds


# --- checking against Wikipedia ---------------------------------------------------------
def wikipedia_titles(text):
    titles = {}
    for i, part in enumerate(ENTRY.split(text)[1:]):
        if i % 2 == 0:
            sid = int(part)
            continue
        m = re.search(r'\("Wikipedia", "https?://en\.wikipedia\.org/wiki/([^"]+)"\)', part)
        if m:
            titles[sid] = urllib.parse.unquote(m.group(1))
    return titles


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def verify_wikipedia(text, ids):
    """{id: True/False} for each id whose description is checked against its article."""
    titles = wikipedia_titles(text)
    descs = {}
    for i, part in enumerate(ENTRY.split(text)[1:]):
        if i % 2 == 0:
            sid = int(part)
            continue
        m = re.search(r"\n +description: Some\(" + STR + r"\),", part, re.S)
        if m:
            descs[sid] = unescape(m.group(1))
    out = {}
    todo = [i for i in ids if i in titles and i in descs]
    for n, sid in enumerate(todo, 1):
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(titles[sid], safe="")
        req = urllib.request.Request(url, headers={"User-Agent": "Curieosity licence audit (educational game)"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                extract = json.load(r).get("extract", "")
        except OSError as e:
            if n == 1:
                sys.exit(f"could not reach Wikipedia ({e}); run this where the network is open")
            extract = ""
        # the scraped text starts with the article's lead: compare the first sentence or so
        a, b = norm(descs[sid])[:120], norm(extract)[:400]
        out[sid] = bool(a) and (a[:80] in b or b[:80] in norm(descs[sid]))
        if n % 100 == 0:
            print(f"  checked {n} of {len(todo)}")
        time.sleep(0.05)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", type=Path, default=LIBRARY, help="library to read (default: library/substances.ron)")
    ap.add_argument("--write", action="store_true", help="write the audited library to library/substances.ron")
    ap.add_argument("--verify-wikipedia", action="store_true", help="confirm Wikipedia text against the articles")
    ap.add_argument("--list", metavar="KIND", help="print the ids of one kind (wikipedia, foreign, uncertain, ...)")
    args = ap.parse_args()

    raw = args.source.read_bytes().decode("utf-8")
    eol = "\r\n" if "\r\n" in raw else "\n"  # the scrape is written on Windows: keep its line ends
    text = raw.replace("\r\n", "\n")
    verified = None
    if args.verify_wikipedia:
        _, _, kinds = audit(text)
        print(f"Checking {len(kinds['wikipedia'])} descriptions against Wikipedia...")
        verified = verify_wikipedia(text, kinds["wikipedia"])
        bad = [i for i, ok in verified.items() if not ok]
        print(f"  {len(verified) - len(bad)} match their article; {len(bad)} don't and will be removed: {bad[:40]}")
    audited, stats, kinds = audit(text, verified)
    print("Library text by source:")
    for k in list(SOURCES) + ["foreign", "uncertain"]:
        print(f"  {k:<10} {len(kinds[k]):>6}  {'kept as ' + SOURCES[k] if k in SOURCES else 'removed'}")
    for k in sorted(stats):
        print(f"  {k:<20} {stats[k]:>6}")
    if args.list:
        print(" ".join(str(i) for i in sorted(kinds.get(args.list, []))))
    if args.write:
        out = audited.replace("\n", eol).encode("utf-8")
        if LIBRARY.exists() and LIBRARY.read_bytes() == out:
            print(f"{LIBRARY.relative_to(ROOT)} is already audited: nothing to change.")
        else:
            LIBRARY.write_bytes(out)
            print(f"Wrote {LIBRARY.relative_to(ROOT)}. Now run: python tools/data/pack_library.py")


if __name__ == "__main__":
    main()
