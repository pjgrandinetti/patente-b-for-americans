#!/usr/bin/env python3
"""Two things about public_html/domandeb_images/, both read from the files
themselves and both checked for staleness by validate_data.py.

1. ALIASES. Group byte-identical files so the app can treat a card image and
   its twin in a topic review as the same picture. Many Ministry cards reuse
   one drawing under different card numbers (4218.gif and 4225.gif are the
   same yellow-and-black curb). A review shows the picture once, under one
   file name; without this map a card carrying the twin file has no figure to
   jump to. Output: public_html/image_aliases.json, a list of groups (each a
   sorted list of `domandeb_images/<file>` paths, size >= 2).

2. DETAILED FIGURES. Which drawings carry so much inside them that the card's
   default size leaves them unreadable. Reported six times before this was
   measured: a board of place names or a panel of opening hours rendered 100
   to 140 px wide is a grey smudge, and a reviewer read 4292's *polizia,
   ambulanze* line as "a police station" (flag 21488, 2026-09-21).

   The signal is the DRAWING'S NODE COUNT, the number of `path`, `polygon`,
   `polyline`, `text` and `tspan` elements. It separates the two kinds
   cleanly: across the 228 SVG figures the median is 4, a plain pictogram
   being a handful of shapes, while a board with names and panels runs to
   dozens (4290 has 85, 4292 has 261). Only 20 sit at or above the threshold
   of 30, so the app can give those the room without inflating the other 208.

   Why not the declared width. app.js already treats a RASTER source of 1000
   px or more as "redrawn large, therefore a composite", and that works for
   photographs. An SVG's declared width is arbitrary, so the same drawing may
   say 400 or 4000: 4290 declares 400x370 and 4292 declares 600x1260, and
   both slipped through that test. Why not text detection: the bank's SVGs
   have their lettering converted to paths, so `<text>` finds nothing in
   either of them.

   Output: the `IMG_DETAILED` set STAMPED into public_html/app.js, rather than
   a data file. Twenty short strings do not deserve their own fetch, cache
   entry and versioned URL, and a set the app reads synchronously cannot be
   one release out of step with the code that uses it.

Run after adding or replacing bank images. `--check` verifies both outputs.
"""
import hashlib, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "public_html" / "domandeb_images"
OUT = ROOT / "public_html" / "image_aliases.json"
APP = ROOT / "public_html" / "app.js"

# At or above this many drawing nodes, a figure is a board rather than a sign.
DETAIL_NODES = 30
NODE_RE = re.compile(r"<(path|polygon|polyline|text|tspan)\b")
# The stamped block. Anchored to the start of a line so a pattern can never
# match the word somewhere else (the lesson CLAUDE.md records about bumping
# CACHE_VERSION with a loose sed).
STAMP_RE = re.compile(r"^const IMG_DETAILED = new Set\(\[.*?\]\);$", re.M | re.S)


def groups():
    by_hash = {}
    for f in sorted(IMG.iterdir()):
        if not f.is_file(): continue
        h = hashlib.md5(f.read_bytes()).hexdigest()
        by_hash.setdefault(h, []).append(f"domandeb_images/{f.name}")
    return sorted([sorted(v) for v in by_hash.values() if len(v) > 1])


def detailed():
    """Paths of the SVG figures whose drawings are busy enough to need room."""
    out = []
    for f in sorted(IMG.iterdir()):
        if f.suffix != ".svg" or not f.is_file(): continue
        n = len(NODE_RE.findall(f.read_text(encoding="utf8", errors="replace")))
        if n >= DETAIL_NODES:
            out.append(f"domandeb_images/{f.name}")
    return out


def stamp_text(paths):
    inner = ",\n  ".join(json.dumps(p) for p in paths)
    return "const IMG_DETAILED = new Set([\n  " + inner + ",\n]);"


def main():
    g, d = groups(), detailed()
    want = stamp_text(d)
    src = APP.read_text(encoding="utf8")
    have = STAMP_RE.search(src)

    if "--check" in sys.argv:
        cur = json.loads(OUT.read_text()) if OUT.exists() else None
        if cur != g:
            print("image_aliases.json is stale: run scripts/build_image_aliases.py"); return 1
        if not have:
            print("app.js carries no IMG_DETAILED set: run scripts/build_image_aliases.py"); return 1
        if have.group(0) != want:
            print("app.js IMG_DETAILED is stale: run scripts/build_image_aliases.py"); return 1
        print(f"✓ image_aliases.json is fresh ({len(g)} groups), "
              f"IMG_DETAILED is fresh ({len(d)} figures)")
        return 0

    OUT.write_text(json.dumps(g, indent=0, ensure_ascii=False) + "\n")
    if not have:
        print("app.js carries no IMG_DETAILED set to replace; add the line first.")
        return 1
    APP.write_text(STAMP_RE.sub(lambda _: want, src, count=1), encoding="utf8")
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(g)} groups, {sum(len(x) for x in g)} files")
    print(f"Stamped IMG_DETAILED into app.js: {len(d)} figures at {DETAIL_NODES}+ nodes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
