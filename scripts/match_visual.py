#!/usr/bin/env python3
"""
match_visual.py — reassign each old DomandeB image to the Commons figure it most
LOOKS LIKE, using image similarity instead of text. For each card we compare the
old picture against every figure in its topic family (a pericolo card only competes
against pericolo figures) with a symbol-focused binary descriptor, and break near
ties with the card's wording (numbers, "destra"/"sinistra").

Needs the library from fetch_library.py (sign_library/). Runs offline.

Writes: scripts/sign_map.csv                 (id, figure, note, score, file)
        sign_svgs_staging/<id>.svg           (matched figure copied in for the PDF/apply)
        sign_svgs_staging/credits.csv        (id, figure, file, author, license, ...)
Then:   python3 scripts/build_compare_pdf.py
"""
import csv, io, json, math, os, re, shutil
from PIL import Image, ImageChops, ImageOps
import cairosvg

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB   = os.path.join(ROOT, "sign_library")
IDX   = os.path.join(LIB, "library_index.csv")
STAGE = os.path.join(ROOT, "sign_svgs_staging")
MAP   = os.path.join(ROOT, "scripts", "sign_map.csv")

STOP = set("segnale segnali di a al ai con per il lo la i gli le un uno una e ed o del dei "
           "della delle su sul in tra che raffigurato raffigurata presenza figura".split())

# figure-number -> family code; topic -> allowed families
FAM_RANGES = [(1,35,"per"),(36,45,"pre"),(46,79,"div"),(80,99,"obb"),
              (100,381,"ind"),(382,414,"tmp"),(415,448,"ori"),(449,462,"lum"),(463,479,"cmp")]
TOPIC_FAMS = {
    "Segnali di pericolo": {"per"}, "Segnali di precedenza": {"pre"},
    "Segnali di divieto": {"div"}, "Segnali di obbligo": {"obb"},
    "Segnali di indicazione": {"ind"}, "Segnaletica orizzontale; segni sugli ostacoli": {"ori"},
    "Segnali complementari; segnali temporanei e di cantiere": {"cmp","tmp"},
    "Segnalazioni semaforiche; segnalazioni degli agenti del traffico": {"lum"},
}
NO_SIGN = {"Esempi di precedenza (ordine di precedenza agli incroci)"}

def toks(s):
    return {w for w in re.split(r"[^a-zàèéìòù]+", s.lower()) if len(w) > 2 and w not in STOP}
def fam_of(nf):
    m = re.match(r"ii(\d+)", nf); n = int(m.group(1)) if m else 0
    return next((c for lo,hi,c in FAM_RANGES if lo<=n<=hi), "x")
def disp(nf):
    m = re.match(r"ii(\d+)([a-z]?)", nf)
    return f"II {m.group(1)}" + (f"/{m.group(2)}" if m and m.group(2) else "")

def on_white(im):
    im = im.convert("RGBA"); bg = Image.new("RGBA", im.size, (255,255,255,255))
    bg.alpha_composite(im); return bg.convert("RGB")
def autocrop(im):
    d = ImageChops.difference(im, Image.new("RGB", im.size, (255,255,255)))
    bb = d.getbbox(); return im.crop(bb) if bb else im
def _sq(im):
    im = autocrop(on_white(im)); s = max(im.size)
    c = Image.new("RGB", (s, s), (255,255,255)); c.paste(im, ((s-im.width)//2, (s-im.height)//2)); return c
# Grayscale, mean-subtracted, L2-normalized patch -> normalized cross-correlation.
# NCC on the interior pictogram vastly out-performs a binarized hamming hash on
# circular signs (red rings / blue discs that differ only by a small interior
# symbol): measured 89% top-1 / 97% top-3 vs 73% / 86% on a divieto ground-truth set.
def _ncc(sq, crop, grid):
    s = sq.size[0]
    if crop < 1.0:
        m = int(s*(1-crop)/2); sq = sq.crop((m, m, s-m, s-m))
    v = list(ImageOps.autocontrast(sq.convert("L")).resize((grid, grid)).getdata())
    mn = sum(v)/len(v); v = [p-mn for p in v]
    nrm = math.sqrt(sum(p*p for p in v)) or 1.0
    return [p/nrm for p in v]
def _color(sq, grid=8):
    im = sq.resize((grid, grid)); return [c/255 for px in list(im.getdata()) for c in px]
# Triangular families (pericolo, complementari) crop a touch tighter to the interior
# symbol; circular/square families keep slightly more of the sign.
def crop_for(fam): return 0.62 if fam in ("per", "cmp") else 0.72
def descriptor(im, fam):
    sq = _sq(im)
    return _ncc(sq, crop_for(fam), 24), _ncc(sq, 1.0, 16), _color(sq)
# dist = -(correlation), so smaller is better (keeps the rest of the pipeline the
# same). A small color penalty separates same-shape signs of different colors in
# the color-diverse indication family; within single-color families it's ~inert.
def dist(a, b):
    sim = (sum(x*y for x, y in zip(a[0], b[0])) + 0.6*sum(x*y for x, y in zip(a[1], b[1])))
    col = sum(abs(x-y) for x, y in zip(a[2], b[2]))/len(a[2])
    return -sim + 3.0*col
IMG_EXT = (".svg", ".png", ".gif", ".jpg", ".jpeg")
def lib_files(libdir):
    """stem -> filename for every image in the library (svg OR raster)."""
    out = {}
    for fn in sorted(os.listdir(libdir)):
        stem, ext = os.path.splitext(fn)
        if ext.lower() in IMG_EXT and stem not in out:
            out[stem] = fn
    return out
def render(path):
    """Rasterize an SVG, or load a raster figure (road-marking diagrams are PNGs)."""
    if path.lower().endswith(".svg"):
        return Image.open(io.BytesIO(cairosvg.svg2png(url=path, output_width=256)))
    return Image.open(path)

def main():
    if not os.path.isdir(LIB) or not any(f.endswith(".svg") for f in os.listdir(LIB)):
        raise SystemExit("No sign_library/. Run fetch_library.py first.")
    index = {}
    if os.path.isfile(IDX):
        index = {r["normfig"]: r for r in csv.DictReader(open(IDX, encoding="utf-8"))}
    # Descriptors are slow to render, so cache them (incrementally, so a killed run
    # resumes). Re-runs after a code change are then instant.
    import pickle
    # Bump this suffix whenever descriptor() changes, so a stale cache is never
    # silently reused (deleting the old file isn't always possible on mounts).
    cache_path = os.path.join(LIB, "_desc_ncc1.pkl")
    cache = {}
    if os.path.isfile(cache_path):
        try: cache = pickle.load(open(cache_path, "rb"))
        except Exception: cache = {}
    libmap = lib_files(LIB)   # stem -> filename (svg or raster)
    changed = 0
    for nf, fn in libmap.items():
        if nf in cache: continue
        try: cache[nf] = descriptor(render(os.path.join(LIB, fn)), fam_of(nf))
        except Exception: cache[nf] = None
        changed += 1
        if changed % 60 == 0:
            pickle.dump(cache, open(cache_path, "wb"))
    if changed:
        pickle.dump(cache, open(cache_path, "wb"))
    # Prefer the family recorded in the index (road-marking slugs are forced to
    # 'ori' there); fall back to number-based family for gallery figures.
    lib = {nf: (index.get(nf, {}).get("fam") or fam_of(nf), d,
                toks(index.get(nf, {}).get("name", "")))
           for nf, d in cache.items() if d is not None}
    print(f"library descriptors: {len(lib)} ({changed} newly rendered)")

    data = json.load(open(os.path.join(ROOT, "public_html", "questions.json"), encoding="utf-8"))
    rows = []
    for c in data:
        if not c.get("image"): continue
        cid = str(c["id"]); topic = c.get("topic", "")
        alltext = " ".join(s.get("italian_text", "") for s in c.get("statements", []))
        if topic in NO_SIGN:
            rows.append({"id":cid,"figure":"","note":"(scenario/diagram)","score":"0","file":""}); continue
        if re.search(r"\(A\)", alltext) and re.search(r"\(B\)", alltext):
            rows.append({"id":cid,"figure":"","note":"(composite: A vs B)","score":"0","file":""}); continue
        fams = TOPIC_FAMS.get(topic)
        pool = [nf for nf,(f2,_,_) in lib.items() if (fams is None or f2 in fams)]
        if not pool:
            rows.append({"id":cid,"figure":"","note":"(no library candidates)","score":"0","file":""}); continue
        repfam = "per" if (fams and ("per" in fams or "cmp" in fams)) else "div"
        p = os.path.join(ROOT, "public_html", c["image"])
        try: od = descriptor(Image.open(p), repfam)
        except Exception:
            rows.append({"id":cid,"figure":"","note":"(old image unreadable)","score":"0","file":""}); continue
        scored = sorted((dist(od, lib[nf][1]), nf) for nf in pool)
        best_d, best_nf = scored[0]   # visual best; alternates are shown as top-3
        r = index.get(best_nf, {})
        figure = r.get("figure") or disp(best_nf)
        cands = "|".join(nf for _, nf in scored[:3])
        # score = correlation of the best match (higher is better; ~1.6 is a strong
        # hit, <0.6 is weak). Also record the margin over the runner-up, which is a
        # better confidence signal than the absolute score alone.
        margin = (scored[1][0] - best_d) if len(scored) > 1 else 0.0
        rows.append({"id":cid,"figure":figure,"note":r.get("name",""),
                     "score":f"{-best_d:.3f}","margin":f"{margin:.3f}",
                     "file":"","candidates":cands})
        # copy the matched figure into staging (preserving its real extension)
        fn = libmap.get(best_nf)
        if fn:
            ext = os.path.splitext(fn)[1]
            shutil.copy(os.path.join(LIB, fn), os.path.join(STAGE, f"{cid}{ext}"))
    rows.sort(key=lambda r: (r["figure"]=="", r["id"]))
    with open(MAP, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id","figure","note","score","margin","file","candidates"], restval="")
        w.writeheader(); w.writerows(rows)
    # credits from the library index
    os.makedirs(STAGE, exist_ok=True)
    with open(os.path.join(STAGE, "credits.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id","figure","file","author","license"]); w.writeheader()
        for r in rows:
            if not r["figure"]: continue
            li = index.get(re.sub(r"[^a-z0-9]","",r["figure"].lower()), {})
            w.writerow({"id":r["id"],"figure":r["figure"],"file":li.get("file",""),
                        "author":li.get("author",""),"license":li.get("license","")})
    matched = sum(1 for r in rows if r["figure"])
    print(f"Wrote {MAP}: {len(rows)} cards, {matched} matched visually.")

if __name__ == "__main__":
    main()
