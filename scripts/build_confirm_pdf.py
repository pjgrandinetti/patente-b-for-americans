#!/usr/bin/env python3
"""
build_confirm_pdf.py — final human check of the CONFIRMED mapping before we touch
the app. Reads the reviewer's export (review_verdicts.csv) and, for every card the
human decided, renders the OLD image beside the figure THEY chose. The corrected
picks (bucket 2/3, where the human overrode the matcher) and no-match rows are put
first and tinted so they get the closest look.

Reads:  review_verdicts.csv        (id, bucket, chosen_figure, chosen_normfig, ...)
        public_html/questions.json  (real old-image path per card)
        sign_library/<normfig>.<ext> + library_index.csv (chosen figure + its name)
Writes: sign_svgs_staging/confirm_signs.pdf
"""
import csv, io, json, os, re
from PIL import Image, ImageDraw, ImageFont
import cairosvg

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV    = os.path.join(ROOT, "review_verdicts.csv")
PUB    = os.path.join(ROOT, "public_html")
OLDDIR = os.path.join(PUB, "domandeb_images")
LIBDIR = os.path.join(ROOT, "sign_library")
IDX    = os.path.join(LIBDIR, "library_index.csv")
OUT    = os.path.join(ROOT, "sign_svgs_staging", "confirm_signs.pdf")

PW, PH = 1240, 1754
MARGIN, IMG_H, ROW_H = 40, 170, 230

def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/Library/Fonts/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.isfile(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()
F, FB, FS = font(20), font(24), font(17)

def on_white(im):
    im = im.convert("RGBA"); bg = Image.new("RGBA", im.size, (255,255,255,255))
    bg.alpha_composite(im); return bg.convert("RGB")

_qs = json.load(open(os.path.join(PUB, "questions.json"), encoding="utf-8"))
IMG_BY_ID = {str(c["id"]): c.get("image", "") for c in _qs if c.get("image")}
NAME = {r["normfig"]: r.get("name", "") for r in csv.DictReader(open(IDX, encoding="utf-8"))} \
       if os.path.isfile(IDX) else {}

IMG_EXT = (".svg", ".png", ".gif", ".jpg", ".jpeg")
LIBFILES = {}
for fn in sorted(os.listdir(LIBDIR)):
    stem, ext = os.path.splitext(fn)
    if ext.lower() in IMG_EXT:
        LIBFILES.setdefault(stem, fn)

def load_old(cid):
    rel = IMG_BY_ID.get(cid)
    p = os.path.join(PUB, rel) if rel else os.path.join(OLDDIR, f"{cid}.jpeg")
    return on_white(Image.open(p)) if os.path.isfile(p) else None

_LC = {}
def load_fig(nf):
    if nf in _LC: return _LC[nf]
    fn = LIBFILES.get(nf); im = None
    if fn:
        p = os.path.join(LIBDIR, fn)
        im = on_white(Image.open(io.BytesIO(cairosvg.svg2png(url=p, output_height=IMG_H*2)))) \
             if fn.lower().endswith(".svg") else on_white(Image.open(p))
    _LC[nf] = im; return im

def scaled(im, h):
    if im is None: return None
    return im.resize((max(1, int(im.width*h/im.height)), h), Image.LANCZOS)

def main():
    rows = [r for r in csv.DictReader(open(CSV, encoding="utf-8")) if (r.get("bucket") or "").strip()]
    # corrected picks + no-match first (most worth scrutiny), then the auto-confirmed
    order = {"2_top3_fix": 0, "3_picked_other": 0, "4_no_match": 1, "1_best_ok": 2}
    rows.sort(key=lambda r: (order.get(r["bucket"], 3), r["id"]))
    n_conf = sum(1 for r in rows if r.get("chosen_normfig"))
    n_none = sum(1 for r in rows if r["bucket"] == "4_no_match")

    pages, page, draw, y = [], None, None, PH
    def start_page():
        nonlocal page, draw, y
        page = Image.new("RGB", (PW, PH), "white"); draw = ImageDraw.Draw(page)
        draw.text((MARGIN, 16), "Confirmed mapping — OLD (left)  vs  CHOSEN figure (right)",
                  fill="black", font=FB)
        draw.line((MARGIN, 54, PW-MARGIN, 54), fill=(180,180,180), width=2)
        y = 70; pages.append(page)
    start_page()

    for r in rows:
        cid, bucket, nf = r["id"], r["bucket"], r.get("chosen_normfig", "")
        fig, name = r.get("chosen_figure", ""), NAME.get(nf, "")
        if y + ROW_H > PH - MARGIN: start_page()
        if bucket != "1_best_ok":   # tint the human-overridden / no-match rows
            draw.rectangle((MARGIN-6, y-4, PW-MARGIN+6, y+ROW_H-16), fill=(255,247,232))
        old = scaled(load_old(cid), IMG_H)
        if old: page.paste(old, (MARGIN, y))
        else:   draw.text((MARGIN, y+70), "(no old image)", fill=(150,0,0), font=F)
        draw.text((MARGIN, y+IMG_H+8), f"#{cid}", fill="black", font=FB)
        tag = {"1_best_ok":"auto-confirmed", "2_top3_fix":"you corrected (2/3)",
               "3_picked_other":"you picked", "4_no_match":"NO MATCH — keep original"}.get(bucket, bucket)
        draw.text((MARGIN, y+IMG_H+34), tag, fill=(120,120,120), font=FS)
        if bucket == "4_no_match":
            draw.text((460, y+70), "no figure — original image kept", fill=(120,120,120), font=F)
        else:
            new = scaled(load_fig(nf), IMG_H)
            if new: page.paste(new, (460, y))
            else:   draw.text((460, y+70), f"(missing figure {nf})", fill=(150,0,0), font=F)
            draw.text((460, y+IMG_H+8), f"{fig}   {name}"[:70], fill=(20,20,20), font=F)
        y += ROW_H

    pages[0].save(OUT, "PDF", save_all=True, append_images=pages[1:], resolution=150)
    print(f"Wrote {OUT}  ({len(pages)} pages)")
    print(f"  {len(rows)} decided: {n_conf} with a chosen figure, {n_none} kept as no-match.")

if __name__ == "__main__":
    main()
