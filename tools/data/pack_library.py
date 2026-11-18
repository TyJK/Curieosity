"""
Packs the game's substances: from the full scraped library in library/ (about 110,000
substances and a picture for many of them, too big for the repository or a download) it
keeps the ones the game uses, and writes them where the game loads them:

    library/substances.ron   ->  assets/data/substances.ron   (the substances in play)
    library/structures/*.png ->  assets/structures/*.png      (their pictures)

In play means every substance the authored game refers to: the start kit, milestone
grants, and everything the authored reactions use, make or need as a catalyst. Every
reaction in the game is authored (assets/data/authored_reactions.ron). The library's own
reactions (library/reactions.ron) are not used: their substance ids are mis-mapped in the
scrape, so even the ones that balance mostly describe the wrong chemistry. The few true
ones were written up as authored reactions instead.

gen_authored.py runs this after writing the authored layer; run it yourself after changing
the library (a new scrape, or audit_library.py --write):

    python tools/data/pack_library.py            pack
    python tools/data/pack_library.py --check    report what would change, write nothing

Values the library only estimates (authored_facts.ESTIMATED: Joback group-contribution
melting and boiling points and enthalpies of formation) are left out of the packed file, so
a page shows measured values or none.

Slips in the scraped text (TEXT_FIXES: "a inhalational anesthetic") are corrected as it is
packed; --check lists any article that looks wrong ("a" before a vowel, "an" before a
consonant) so a new scrape's can be added there.

The library's line endings are kept, so the packed file diffs cleanly.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "library"
DATA = ROOT / "assets" / "data"
STRUCTURES = ROOT / "assets" / "structures"

SUB_ENTRY = re.compile(r"\n    (\d+): \(")

# id -> [(as scraped, as shown)]
TEXT_FIXES = {
    2758: [("identified as a inhibitor", "identified as an inhibitor")],
    3205: [("takes on an helimagnetic", "takes on a helimagnetic")],
    3299: [("appears as an clear aqueous", "appears as a clear aqueous")],
    3764: [("as a aliphatic", "as an aliphatic")],
    3768: [("given as an drops in the eye", "given as drops in the eye")],
    4904: [("is a inhalational", "is an inhalational")],
    6358: [("as a antiherbivore", "as an antiherbivore")],
    7368: [("Vitamin a appears", "Vitamin A appears")],
    8836: [("is an naphthoquinone", "is a naphthoquinone")],
}

# an article that doesn't suit the word after it; a capital, a symbol or a letter's name
# after it ("a II-V semiconductor", "factor Xa", "vitamin A and") is not looked at
SUSPECT_ARTICLE = re.compile(
    r"(?<![\w-])(a (?!uni|use|usu|uti|ure|uri|uro|ubiq|eu|one|once)[aeiou][a-z]+"
    r"|an (?!hour|honest|hono|heir|herb)[b-df-hj-np-tv-z][a-z]+)"
)


def fix_text(sid, block):
    for old, new in TEXT_FIXES.get(sid, []):
        block = block.replace(old, new)
    return block


def suspect_articles(blocks):
    """(id, phrase) for each article in the packed text that looks wrong."""
    out = []
    for sid, b in blocks:
        for m in SUSPECT_ARTICLE.finditer(b):
            out.append((sid, b[max(0, m.start() - 30): m.end() + 20].replace("\n", " ")))
    return out


def read_text(path):
    raw = path.read_bytes().decode("utf-8")
    eol = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), eol


def ids_in(text, field):
    return {int(x) for x in re.findall(field + r": (\d+)", text)}


def authored_ids():
    """Every substance id the authored game refers to, and the locked previews of later
    stages (substances with a page but no reaction yet)."""
    ar, _ = read_text(DATA / "authored_reactions.ron")
    ids = ids_in(ar, "substance_id") | {int(x) for x in re.findall(r"Catalyst\((\d+)\)", ar)}
    for block in re.findall(r"(?:start|grant): \[([^\]]*)\]", ar):
        ids |= {int(x) for x in re.findall(r"\d+", block)}
    ids |= ids_in(ar, "on")
    au_path = DATA / "authored_substances.ron"
    if au_path.exists():
        au, _ = read_text(au_path)
        ids |= {int(m.group(1)) for m in re.finditer(r"^ {4}(\d+): \(.*\bstage: ", au, re.M)}
    return ids


def estimated_values():
    """field -> library ids whose value for it is only an estimate (absent: none known)."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from authored_facts import ESTIMATED
    except ImportError:
        return {}
    return ESTIMATED


def drop_estimates(sid, block, estimated):
    """The block with its estimated values set to None."""
    for field, ids in estimated.items():
        if sid in ids:
            block = re.sub(rf"(\n {{12}}{field}: )Some\([^)]*\),", r"\1None,", block)
    return block


def split_entries(text, pattern, closing):
    """(head, [(id, block)], tail) with each block exactly as it stands in the file; `closing`
    matches the file's closing brackets after the last entry."""
    starts = [(m.start(), int(m.group(1))) for m in pattern.finditer(text)]
    if not starts:
        sys.exit("no entries found: is this a library file?")
    end = re.search(closing, text)
    if not end:
        sys.exit("the file doesn't end the way a library file does")
    head, tail = text[: starts[0][0]], text[end.start():]
    blocks = []
    for (a, sid), nxt in zip(starts, starts[1:] + [(end.start(), None)]):
        blocks.append((sid, text[a: nxt[0]]))
    return head, blocks, tail


def pack(check=False):
    library = LIBRARY / "substances.ron"
    if not library.exists():
        sys.exit(f"{library.relative_to(ROOT)} is missing: the full library lives in library/ (see the module docstring)")
    subs_text, sub_eol = read_text(library)
    s_head, subs, s_tail = split_entries(subs_text, SUB_ENTRY, r"\n\}\)\s*$")

    in_play = authored_ids()
    keep = in_play & {sid for sid, _ in subs}
    estimated = estimated_values()
    packed = [(sid, fix_text(sid, drop_estimates(sid, b, estimated))) for sid, b in subs if sid in keep]
    sub_out = s_head + "".join(b for _, b in packed) + s_tail
    pictures = sorted(i for i in in_play if (LIBRARY / "structures" / f"{i}.png").exists())
    retired = DATA / "reactions.ron"  # the library reactions the game used to load

    print(f"library   {len(subs):>7} substances")
    print(f"in play   {len(in_play):>7} substances ({len(keep)} from the library, the rest authored)")
    print(f"pictures  {len(pictures):>7} of {len(in_play)} in play have one in library/structures")
    if check:
        for sid, phrase in suspect_articles(packed):
            print(f"article?  {sid}: ...{phrase}...")
        if retired.exists():
            print(f"would remove {retired.relative_to(ROOT)}: the game no longer loads library reactions")
        return
    DATA.mkdir(parents=True, exist_ok=True)
    changed = 0
    path = DATA / "substances.ron"
    data = sub_out.replace("\n", sub_eol).encode("utf-8")
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)
        changed += 1
        print(f"wrote     {path.relative_to(ROOT)} ({len(data) // 1024} KB)")
    if retired.exists():
        retired.unlink()
        changed += 1
        print(f"removed   {retired.relative_to(ROOT)}: the game no longer loads library reactions")
    STRUCTURES.mkdir(parents=True, exist_ok=True)
    want = {f"{i}.png" for i in pictures}
    copied = removed = 0
    for name in sorted(want):
        src, dst = LIBRARY / "structures" / name, STRUCTURES / name
        if not dst.exists() or dst.stat().st_size != src.stat().st_size or dst.read_bytes() != src.read_bytes():
            shutil.copyfile(src, dst)
            copied += 1
    for p in STRUCTURES.glob("*.png"):
        if p.name not in want:
            p.unlink()
            removed += 1
    print(f"pictures  {copied} copied, {removed} no longer needed removed, {len(want)} in assets/structures")
    if not changed and not copied and not removed:
        print("the pack was already up to date")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    pack(ap.parse_args().check)


if __name__ == "__main__":
    main()
