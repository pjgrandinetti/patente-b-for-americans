#!/usr/bin/env python3
"""
build_compare_pdf.py — build a side-by-side OLD vs NEW comparison PDF so a human
can verify the domandeB-image -> Commons-SVG mapping before any app image changes.

Reads:  scripts/sign_map.csv           (id, figure, note, score, file)
        public_html/domandeb_images/<id>.jpeg   (OLD, low-res)
        sign_svgs_staging/<id>.svg              (NEW, downloaded by fetch_signs.py)
Writes: sign_svgs_staging/compare_signs.pdf

Each row shows the old image on the left, the new vector on the right, with the
card id, guessed figure, its name, and the match score. Low-score rows are tinted
so they're easy to scrutinize. Rows whose SVG wasn't downloaded show a note.

Needs: pip install pillow cairosvg
"""
import csv, io, json, os, re
from PIL import Image, ImageDraw, ImageFont
import cairosvg

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV    = os.path.join(ROOT, "scripts", "sign_map.csv")
PUB    = os.path.join(ROOT, "public_html")
OLDDIR = os.path.join(PUB, "domandeb_images")
LIBDIR = os.path.join(ROOT, "sign_library")   # for top-3 candidate rendering

# card id -> its ACTUAL image path (many variant/composite cards use a filename
# that is NOT <id>.jpeg, e.g. 4061_18980.jpeg), so read it from questions.json.
_qs = json.load(open(os.path.join(PUB, "questions.json"), encoding="utf-8"))
IMG_BY_ID = {str(c["id"]): c.get("image", "") for c in _qs if c.get("image")}
NEWDIRS = [os.path.join(ROOT, "sign_svgs_staging"),
           os.path.join(ROOT, "sign_svgs_staging", "svgs")]
OUT    = os.path.join(ROOT, "sign_svgs_staging", "compare_signs.pdf")

# Page geometry (A4 @ ~150 dpi)
PW, PH = 1240, 1754
MARGIN = 40
IMG_H  = 150            # both images scaled to this height
ROW_H  = 210
COL_GAP = 30

def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/Library/Fonts/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.isfile(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

F, FB = font(20), font(24)

def on_white(im):
    im = im.convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")

def load_old(cid):
    rel = IMG_BY_ID.get(cid)
    p = os.path.join(PUB, rel) if rel else os.path.join(OLDDIR, f"{cid}.jpeg")
    return on_white(Image.open(p)) if os.path.isfile(p) else None

def load_new(cid):
    for d in NEWDIRS:
        p = os.path.join(d, f"{cid}.svg")
        if os.path.isfile(p):
            png = cairosvg.svg2png(url=p, output_height=IMG_H * 2)
            return on_white(Image.open(io.BytesIO(png)))
    return None

_IMG_EXT = (".svg", ".png", ".gif", ".jpg", ".jpeg")
_LIBFILES = {}
if os.path.isdir(LIBDIR):
    for _fn in sorted(os.listdir(LIBDIR)):
        _stem, _ext = os.path.splitext(_fn)
        if _ext.lower() in _IMG_EXT:
            _LIBFILES.setdefault(_stem, _fn)
_LIBCACHE = {}
def load_lib(nf):
    if nf in _LIBCACHE:
        return _LIBCACHE[nf]
    fn = _LIBFILES.get(nf)
    im = None
    if fn:
        p = os.path.join(LIBDIR, fn)
        if fn.lower().endswith(".svg"):
            im = on_white(Image.open(io.BytesIO(cairosvg.svg2png(url=p, output_height=IMG_H * 2))))
        else:
            im = on_white(Image.open(p))
    _LIBCACHE[nf] = im
    return im

def disp(nf):
    m = re.match(r"ii(\d+)([a-z]?)", nf)
    return f"II {m.group(1)}" + (f"/{m.group(2)}" if m and m.group(2) else "") if m else nf

def scaled(im, h):
    if im is None:
        return None
    w = max(1, int(im.width * h / im.height))
    return im.resize((w, h), Image.LANCZOS)

def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    pages, page, draw = [], None, None
    y = PH
    new_page = lambda: None

    def start_page():
        nonlocal page, draw, y
        page = Image.new("RGB", (PW, PH), "white")
        draw = ImageDraw.Draw(page)
        draw.text((MARGIN, 18), "Sign check — OLD (left)  vs  top-3 look-alike figures (best first)",
                  fill="black", font=FB)
        draw.line((MARGIN, 56, PW - MARGIN, 56), fill=(180, 180, 180), width=2)
        y = 72
        pages.append(page)

    start_page()
    midx = PW // 2
    for r in rows:
        cid, fig, note, score = r["id"], r.get("figure", ""), r.get("note", ""), r.get("score", "0")
        try:
            sc = float(score)
        except ValueError:
            sc = 0.0
        try:
            mg = float(r.get("margin", "") or 0.0)
        except ValueError:
            mg = 0.0
        if y + ROW_H > PH - MARGIN:
            start_page()
        # Tint low-confidence rows so they're easy to scrutinize: a weak absolute
        # correlation (score < 0.55) OR a near-tie with the runner-up (margin < 0.05).
        if fig and (sc < 0.55 or mg < 0.05):
            draw.rectangle((MARGIN - 6, y - 4, PW - MARGIN + 6, y + ROW_H - 12), fill=(255, 244, 244))
        cands = [c for c in (r.get("candidates", "") or "").split("|") if c]
        # OLD on the left
        old = scaled(load_old(cid), IMG_H)
        if old: page.paste(old, (MARGIN, y))
        else:   draw.text((MARGIN, y + 60), "(no old image)", fill=(150, 0, 0), font=F)
        draw.text((MARGIN, y + IMG_H + 6), f"#{cid}", fill="black", font=FB)
        draw.text((PW - MARGIN - 200, y + 2), f"score {score}  gap {r.get('margin','')}",
                  fill=(150, 150, 150), font=F)
        # RIGHT: top-3 look-alike candidates (best first), or a single new / keep-original
        if cands and os.path.isdir(LIBDIR):
            x0, step = 360, (PW - MARGIN - 360) // 3
            for i, nf in enumerate(cands[:3]):
                im = scaled(load_lib(nf), IMG_H); x = x0 + i * step
                if im: page.paste(im, (x, y))
                lbl = disp(nf) + ("  (best)" if i == 0 else "")
                draw.text((x, y + IMG_H + 10), lbl, fill=(20, 20, 20) if i == 0 else (120, 120, 120), font=F)
        elif fig:
            new = scaled(load_new(cid), IMG_H)
            if new: page.paste(new, (midx + COL_GAP, y))
            else:   draw.text((midx + COL_GAP, y + 60), "SVG not downloaded", fill=(150, 0, 0), font=F)
            draw.text((midx + COL_GAP, y + IMG_H + 10), f"figura {fig}   {note}"[:60], fill=(40, 40, 40), font=F)
        else:
            draw.text((360, y + 60), "no candidate — keep original", fill=(120, 120, 120), font=F)
        y += ROW_H

    pages[0].save(OUT, "PDF", save_all=True, append_images=pages[1:], resolution=150)
    print(f"Wrote {OUT}  ({len(pages)} pages, {len(rows)} cards)")

if __name__ == "__main__":
    main()
