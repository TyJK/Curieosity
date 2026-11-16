"""
Packs the game's content: from the full scraped library in library/ (about 110,000
substances, 95,000 reactions and a picture for each substance, too big for the repository
or a download) it keeps only what a player can ever reach, and writes it where the game
loads it:

    library/substances.ron   ->  assets/data/substances.ron   (the reachable substances)
    library/reactions.ron    ->  assets/data/reactions.ron    (the reachable reactions)
    library/structures/*.png ->  assets/structures/*.png      (their pictures)

Reachable means: every substance the authored game uses (the start kit, milestone grants,
and everything the authored reactions use, make or need as a catalyst), then everything a
library reaction makes from reachable substances, repeated until nothing new appears. The
library reactions kept are exactly those whose reactants are all reachable, so the packed
game plays identically to the full library: anything left out could never be made.

gen_authored.py runs this after writing the authored layer; run it yourself after changing
the library (a new scrape, or audit_library.py --write):

    python tools/data/pack_library.py            pack
    python tools/data/pack_library.py --check    report what would change, write nothing

The library's line endings are kept, so the packed files diff cleanly.
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
RXN_ENTRY = re.compile(r"\n        \(\n            id: (\d+),")


def read_text(path):
    raw = path.read_bytes().decode("utf-8")
    eol = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), eol


def ids_in(text, field):
    return {int(x) for x in re.findall(field + r": (\d+)", text)}


def authored_ids():
    """Every substance id the authored game refers to."""
    ar, _ = read_text(DATA / "authored_reactions.ron")
    ids = ids_in(ar, "substance_id") | {int(x) for x in re.findall(r"Catalyst\((\d+)\)", ar)}
    for block in re.findall(r"(?:start|grant): \[([^\]]*)\]", ar):
        ids |= {int(x) for x in re.findall(r"\d+", block)}
    ids |= ids_in(ar, "on")
    return ids


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


def reaction_sides(block):
    m = re.search(r"reactants: \[(.*?)\],\s*\n\s*products: \[(.*?)\],", block, re.S)
    if not m:
        return set(), set()
    return ids_in(m.group(1), "substance_id"), ids_in(m.group(2), "substance_id")


def pack(check=False):
    for p in (LIBRARY / "substances.ron", LIBRARY / "reactions.ron"):
        if not p.exists():
            sys.exit(f"{p.relative_to(ROOT)} is missing: the full library lives in library/ (see the module docstring)")
    subs_text, sub_eol = read_text(LIBRARY / "substances.ron")
    rxn_text, rxn_eol = read_text(LIBRARY / "reactions.ron")
    s_head, subs, s_tail = split_entries(subs_text, SUB_ENTRY, r"\n\}\)\s*$")
    r_head, rxns, r_tail = split_entries(rxn_text, RXN_ENTRY, r"\n    \],\n\)\s*$")
    sides = [(rid, *reaction_sides(b)) for rid, b in rxns]

    reach = set(authored_ids())
    while True:
        grew = False
        for _, ins, outs in sides:
            if ins and ins <= reach and not outs <= reach:
                reach |= outs
                grew = True
        if not grew:
            break
    keep_rxn = {rid for rid, ins, _ in sides if ins and ins <= reach}
    library_ids = {sid for sid, _ in subs}
    keep_sub = reach & library_ids

    sub_out = s_head + "".join(b for sid, b in subs if sid in keep_sub) + s_tail
    rxn_out = r_head + "".join(b for rid, b in rxns if rid in keep_rxn) + r_tail
    pictures = sorted(i for i in reach if (LIBRARY / "structures" / f"{i}.png").exists())

    print(f"library   {len(subs):>7} substances, {len(rxns):>6} reactions")
    print(f"reachable {len(reach):>7} substances ({len(keep_sub)} from the library), {len(keep_rxn)} library reactions")
    print(f"pictures  {len(pictures):>7} of {len(reach)} reachable substances have one in library/structures")
    if check:
        return
    DATA.mkdir(parents=True, exist_ok=True)
    changed = 0
    for path, text, eol in ((DATA / "substances.ron", sub_out, sub_eol), (DATA / "reactions.ron", rxn_out, rxn_eol)):
        data = text.replace("\n", eol).encode("utf-8")
        if not path.exists() or path.read_bytes() != data:
            path.write_bytes(data)
            changed += 1
            print(f"wrote     {path.relative_to(ROOT)} ({len(data) // 1024} KB)")
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
