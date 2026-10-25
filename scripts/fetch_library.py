#!/usr/bin/env python3
"""
fetch_library.py — download ONE SVG per official figure into sign_library/, so the
visual matcher (match_visual.py) has the full candidate set to compare each old
image against. Reuses anything already in sign_svgs_staging/ (keyed by figure) and
downloads only what's missing. RUN ON A NETWORKED MACHINE. Resumable.

Output: sign_library/<normfig>.svg           (e.g. ii30a.svg)
        sign_library/library_index.csv        (normfig, figure, name, file, author, license)
"""
import csv, os, re, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_sign_map import build_catalog, TOPIC_SECTIONS, norm_fig   # catalog + families
from fetch_signs import _open, imageinfo                              # polite download + license

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB   = os.path.join(ROOT, "sign_library")
STAGE = os.path.join(ROOT, "sign_svgs_staging")
IDX   = os.path.join(LIB, "library_index.csv")

# Set True to restore the old behavior (only download families that have image-cards).
# Default False = download the complete catalog so the picker is exhaustive.
ALL_FAMILIES_ONLY_WITH_CARDS = False

def seed_from_staging():
    """Copy already-downloaded staging SVGs into the library by figure (no net)."""
    creds = os.path.join(STAGE, "credits.csv")
    if not os.path.isfile(creds):
        return 0
    n = 0
    for r in csv.DictReader(open(creds, encoding="utf-8")):
        src = os.path.join(STAGE, f"{r['id']}.svg")
        dst = os.path.join(LIB, norm_fig(r["figure"]) + ".svg")
        if os.path.isfile(src) and not os.path.isfile(dst):
            shutil.copy(src, dst); n += 1
    return n

def main():
    os.makedirs(LIB, exist_ok=True)
    print(f"seeded {seed_from_staging()} figures from staging")
    cat = build_catalog()
    # Download EVERY figure in the catalog that has a real file. The library is the
    # candidate pool the matcher AND the human reviewer's picker draw from, so it must
    # be complete: a figure absent here can never be assigned, even if it exists on
    # Commons. (Earlier this was restricted to families with image-cards, which left
    # ~37 figure numbers undownloaded and thus invisible in the picker.)
    need = [e for e in cat if "No image available" not in e["file"]]
    if ALL_FAMILIES_ONLY_WITH_CARDS:   # opt-out kept for reference; default is full
        want = set()
        for keys in TOPIC_SECTIONS.values():
            want |= set(keys)
        need = [e for e in need if any(k in e["section"] for k in want)]
    # de-dup by figure (first wins)
    seen, uniq = set(), []
    for e in need:
        k = norm_fig(e["figure"])
        if k not in seen:
            seen.add(k); uniq.append((k, e))
    idx = {}
    if os.path.isfile(IDX):
        idx = {r["normfig"]: r for r in csv.DictReader(open(IDX, encoding="utf-8"))}
    got = have = 0
    for k, e in uniq:
        dst = os.path.join(LIB, k + ".svg")
        if os.path.isfile(dst):
            have += 1
            idx.setdefault(k, {"normfig": k, "figure": e["figure"], "name": e["name"],
                               "file": e["file"], "author": "", "license": ""})
            continue
        info = imageinfo(e["file"])
        if not info["url"]:
            print(f"  {e['figure']}: no url for {e['file']}"); continue
        with _open(info["url"]) as r, open(dst, "wb") as f:
            f.write(r.read())
        idx[k] = {"normfig": k, "figure": e["figure"], "name": e["name"], "file": e["file"],
                  "author": info["author"], "license": info["license"]}
        got += 1
        print(f"  {e['figure']:9s} -> {e['file']}")
        time.sleep(3.0)
    with open(IDX, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["normfig", "figure", "name", "file", "author", "license"])
        w.writeheader(); w.writerows(idx.values())
    print(f"\nLibrary: {len(idx)} figures ({got} downloaded, {have} already present). Index: {IDX}")

if __name__ == "__main__":
    main()
