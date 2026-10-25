#!/usr/bin/env python3
"""
normalize_library.py — one-shot cleanup after pulling the road-marking categories:

  1. Split the ii437d name collision (three unrelated cycle-crossing files had been
     keyed identically); the two raster ones get descriptive slugs.
  2. Rebuild sign_library/library_index.csv from what's actually on disk, adding a
     'fam' column: road-marking slugs (rm-*) are forced to family 'ori' so they
     become candidates for road-marking cards; numbered figures keep number-based
     families.

Idempotent: safe to re-run. Local only (no network).
"""
import csv, os, re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from match_visual import fam_of

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB  = os.path.join(ROOT, "sign_library")
IDX  = os.path.join(LIB, "library_index.csv")
IMG_EXT = (".svg", ".png", ".gif", ".jpg", ".jpeg")

# raster files wrongly collapsed onto ii437d -> give them their own slug + title
COLLISION = {
    "ii437d.png": ("rm-attraversamenti-ciclabili-diretti", "File:Attraversamenti Ciclabili Diretti.png"),
    "ii437d.jpg": ("rm-attraversamenti-ciclabili-obliqui", "File:Attraversamenti Ciclabili Obliqui.jpg"),
}

def main():
    old_idx = {}
    if os.path.isfile(IDX):
        for r in csv.DictReader(open(IDX, encoding="utf-8")):
            old_idx[r["normfig"]] = r
    extra_titles = {}   # newstem -> title, for the reslugged rasters

    # 1) split the collision
    for fname, (newstem, title) in COLLISION.items():
        src = os.path.join(LIB, fname)
        if not os.path.isfile(src):
            continue
        ext = os.path.splitext(fname)[1]
        dst = os.path.join(LIB, newstem + ext)
        if not os.path.isfile(dst):
            os.rename(src, dst)
            print(f"  split collision: {fname} -> {newstem}{ext}")
        extra_titles[newstem] = title

    # 2) rebuild the index from disk
    rows = []
    for fn in sorted(os.listdir(LIB)):
        stem, ext = os.path.splitext(fn)
        if ext.lower() not in IMG_EXT:
            continue
        prev = old_idx.get(stem, {})
        fam = "ori" if stem.startswith("rm-") else fam_of(stem)
        name = prev.get("name", "")
        title = prev.get("file", "") or extra_titles.get(stem, "")
        if not name:
            name = re.sub(r"^File:|\.[a-z0-9]+$", "", title, flags=re.I) if title \
                   else stem
        rows.append({"normfig": stem, "figure": prev.get("figure", "") or _disp(stem),
                     "name": name, "file": title,
                     "author": prev.get("author", ""), "license": prev.get("license", ""),
                     "ext": ext.lstrip("."), "fam": fam})

    with open(IDX, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["normfig", "figure", "name", "file",
                                          "author", "license", "ext", "fam"])
        w.writeheader(); w.writerows(rows)
    fams = {}
    for r in rows:
        fams[r["fam"]] = fams.get(r["fam"], 0) + 1
    print(f"Rebuilt {IDX}: {len(rows)} figures.")
    print("  by family:", dict(sorted(fams.items())))
    print("  road-marking (ori) figures:", fams.get("ori", 0))

def _disp(nf):
    m = re.match(r"ii(\d+)([a-z]?)", nf or "")
    return (f"II {m.group(1)}" + (f"/{m.group(2)}" if m.group(2) else "")) if m else nf

if __name__ == "__main__":
    main()
