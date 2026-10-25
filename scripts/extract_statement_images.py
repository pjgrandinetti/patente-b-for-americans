"""Extract per-statement images from DomandeB.pdf for multi-figure quesiti.

Background
----------
In DomandeB.pdf the "Immagine" column is per-STATEMENT, not per-quesito: within
one quesito different statements can show different figures (e.g. Quesito 4029,
where 18609 shows the striped truck rear-marker panel, 18613 the orange
dangerous-goods panel, 18614 the red/white projecting-loads panel), and some
statements have no figure at all. The original extractor collapsed each quesito
to a single card-level image, which is wrong for any card whose statements show
more than one distinct figure.

What this script does
---------------------
1. Walks the PDF and attributes every image placement to the statement row it
   sits beside (the last statement number whose row starts at or above the
   image top).
2. Finds every card whose statements carry more than one distinct figure (or
   that mix figured and figure-less rows) and SPLITS it, following the
   project's variant-subcard convention (the same one used by the manual A/B
   sign-pair variants, ids 5004+): the base card keeps the statements whose
   figure matches its original card image; every other figure group becomes a
   variant subcard (id 5xxx, base_id, letter, "variant_auto": true) with that
   group's figure as its pinned card image; figure-less statements become a
   final subcard with no image. Subcards are inserted right after their base.
3. Figure files are written to public_html/domandeb_images/ as
   <card>_<statement>.jpeg (project convention: card number, underscore, the
   first statement number using that figure). Unreferenced generated files
   are cleaned up.

The script is idempotent: on each run it first merges previously generated
("variant_auto") subcards back into their bases and re-derives everything
from the PDF. The 20 manual variants are never touched. Cards whose
statements all repeat one identical figure keep their card-level image.

Usage:
    python3 scripts/extract_statement_images.py            # apply
    python3 scripts/extract_statement_images.py --dry-run  # report only
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "sources" / "DomandeB.pdf"
QUESTIONS = ROOT / "public_html" / "questions.json"
ABRIDGED = ROOT / "public_html" / "abridged.json"
IMG_DIR = ROOT / "public_html" / "domandeb_images"
IMG_DIR_NAME = "domandeb_images"

# An image belongs to the last statement row whose number's y-origin is at or
# above the image's top edge (+tolerance: in the PDF the figure starts ~1pt
# below its row's first text line).
Y_TOLERANCE = 2.0
# Two placements within this many points vertically are "the same row"
# (side-by-side figure pairs).
SAME_ROW = 3.0


def collect_statement_rects(doc: fitz.Document) -> dict[str, tuple[int, fitz.Rect]]:
    """statement number -> (page, union rect of its row's figure placements).

    The PDF often paints several byte-different but visually identical copies
    of a figure stacked at the same rect, and some rows show two figures side
    by side. Collapsing identical rects and taking the union bbox of the row's
    placements, then RENDERING that clip, captures exactly what the reader
    sees regardless of duplicate objects or z-order.
    """
    out: dict[str, tuple[int, fitz.Rect]] = {}
    for pno in range(len(doc)):
        page = doc[pno]
        rows = sorted(
            (w[1], w[4])
            for w in page.get_text("words")
            if re.fullmatch(r"\d{5}", w[4]) and w[0] < 100
        )
        if not rows:
            continue
        rects: dict[str, fitz.Rect] = {}
        seen = set()
        for img in page.get_images(full=True):
            xref = img[0]
            for r in page.get_image_rects(xref):
                key = (round(r.y0, 1), round(r.x0, 1), round(r.x1, 1))
                if key in seen:
                    continue
                seen.add(key)
                owner = None
                for ry, num in rows:
                    if ry <= r.y0 + Y_TOLERANCE:
                        owner = num
                    else:
                        break
                if owner is None:
                    continue
                rects[owner] = rects[owner] | r if owner in rects else fitz.Rect(r)
        for num, r in rects.items():
            out[num] = (pno, r)
    return out


def render_figure(doc: fitz.Document, where: tuple[int, fitz.Rect]) -> bytes:
    """Render the figure region as the reader sees it (PNG bytes, 2x scale)."""
    pno, rect = where
    pix = doc[pno].get_pixmap(clip=rect, matrix=fitz.Matrix(2, 2))
    return pix.tobytes("png")


def fig_array(png: bytes):
    """Blurred, downsampled RGB array: blur kills the sub-pixel anti-aliasing
    noise between byte-different renders of the same figure while structural
    differences (a different supplementary panel, dashed vs solid line)
    survive."""
    import numpy as np
    im = Image.open(io.BytesIO(png)).convert("RGB")
    im = im.filter(ImageFilter.GaussianBlur(1.5)).resize((48, 48), Image.LANCZOS)
    return np.asarray(im, dtype=np.float32)


def fig_distance(a, b) -> float:
    """Max 8x8-block mean absolute RGB difference (local, so a small changed
    panel can't hide in a global mean)."""
    import numpy as np
    d = np.abs(a - b).mean(axis=2)
    return float(d.reshape(6, 8, 6, 8).mean(axis=(1, 3)).max())


SAME_BELOW = 9.0    # distance < this  -> same figure
DIFF_ABOVE = 15.0   # distance > this  -> different figures
# distances in [SAME_BELOW, DIFF_ABOVE] are ambiguous and must be settled by
# a human/visual review, recorded here ("smaller|larger statement number").
AMBIGUOUS_OVERRIDES = {
    # solid vs dashed center-line road photos (verified visually 2026-06-11):
    # solid = {20721, 20725, 20894}, dashed = {20724, 20895, 22790, 22793,
    # 22815, 22822, 22826, 22827, 22872} - every cross-group pair differs.
    "20721|20724": "diff",
    "20721|20895": "diff",
    "20721|22790": "diff",
    "20721|22793": "diff",
    "20721|22815": "diff",
    "20721|22822": "diff",
    "20721|22826": "diff",
    "20721|22827": "diff",
    "20721|22872": "diff",
    "20724|20725": "diff",
    "20724|20894": "diff",
    "20725|20895": "diff",
    "20725|22790": "diff",
    "20725|22793": "diff",
    "20725|22815": "diff",
    "20725|22822": "diff",
    "20725|22826": "diff",
    "20725|22827": "diff",
    "20725|22872": "diff",
    "20894|20895": "diff",
    "20894|22790": "diff",
    "20894|22793": "diff",
    "20894|22815": "diff",
    "20894|22822": "diff",
    "20894|22826": "diff",
    "20894|22827": "diff",
    "20894|22872": "diff",
    # no-parking sign with holiday-cross panel vs workday-hammers panel:
    "22038|22050": "diff",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    doc = fitz.open(PDF)
    stmt_rects = collect_statement_rects(doc)
    cards = json.loads(QUESTIONS.read_text(encoding="utf-8"))

    # Idempotency: merge previously generated subcards back into their bases
    # and drop any legacy per-statement image fields, so detection always
    # starts from the original card-level state. Manual variants (no
    # "variant_auto" flag) are never touched.
    abridged = json.loads(ABRIDGED.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cards}
    for c in [c for c in cards if c.get("variant_auto")]:
        base = by_id[c["base_id"]]
        base["statements"].extend(c["statements"])
        base["statements"].sort(key=lambda s: int(s["number"]))
        cards.remove(c)
        # fold the subcard's abridged (Quick-mode) entry back into the base's
        sub_kept = abridged.pop(str(c["id"]), [])
        if sub_kept:
            base_kept = abridged.get(str(c["base_id"]), [])
            abridged[str(c["base_id"])] = sorted(
                set(map(str, base_kept)) | set(map(str, sub_kept)), key=int)
    for card in cards:
        for s in card["statements"]:
            s.pop("image", None)
        if not card.get("variant"):
            orig = IMG_DIR / f"{card['id']}.jpeg"
            card["image"] = f"{IMG_DIR_NAME}/{orig.name}" if orig.is_file() else None

    fig_cache: dict[str, bytes] = {}
    exact: dict[str, str] = {}

    def exact_digest(number: str) -> str | None:
        if number not in stmt_rects:
            return None
        if number not in exact:
            pno, rect = stmt_rects[number]
            png = doc[pno].get_pixmap(clip=rect, matrix=fitz.Matrix(2, 2)).tobytes("png")
            fig_cache[number] = png
            exact[number] = hashlib.md5(png).hexdigest()
        return exact[number]

    # Pass 1 (cheap): exact render digests. A card needs splitting if its
    # statements show >1 distinct figure (verified perceptually in pass 2) OR
    # if it mixes figured and figure-less rows (a figure must not display
    # beside statements the source prints without one). A card with one exact
    # digest covering every statement is uniform for sure; >1 exact digest is
    # only a CANDIDATE (renders of the same figure can differ by sub-pixel
    # noise).
    candidates = []
    mixed_only = set()
    for card in cards:
        if card.get("variant"):
            continue
        digs = {d for s in card["statements"]
                if (d := exact_digest(s["number"])) is not None}
        n_fig = sum(1 for s in card["statements"] if s["number"] in stmt_rects)
        mixed = 0 < n_fig < len(card["statements"])
        if len(digs) > 1 or (digs and mixed):
            candidates.append(card)
            if len(digs) <= 1:
                mixed_only.add(card["id"])

    # Pass 2: perceptual clustering across all candidate statements.
    nums = [s["number"] for c in candidates for s in c["statements"]
            if s["number"] in fig_cache]
    arrs = {n: fig_array(fig_cache[n]) for n in nums}
    parent = {n: n for n in nums}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    ambiguous = []
    for i, a in enumerate(nums):
        for b in nums[i + 1:]:
            dist = fig_distance(arrs[a], arrs[b])
            if SAME_BELOW <= dist <= DIFF_ABOVE:
                key = f"{min(a,b,key=int)}|{max(a,b,key=int)}"
                ruling = AMBIGUOUS_OVERRIDES.get(key)
                if ruling is None:
                    ambiguous.append((key, round(dist, 1)))
                    continue
                if ruling == "diff":
                    continue
            elif dist > DIFF_ABOVE:
                continue
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
    if ambiguous:
        raise SystemExit(
            "Ambiguous figure pairs need visual review; add each to "
            f"AMBIGUOUS_OVERRIDES as 'same' or 'diff': {sorted(set(ambiguous))}")

    affected = [c for c in candidates
                if c["id"] in mixed_only
                or len({find(s["number"]) for s in c["statements"]
                        if s["number"] in fig_cache}) > 1]
    print(f"Cards to split (per-statement figures): {len(affected)}")

    def orig_image_array(card):
        path = IMG_DIR / f"{card['id']}.jpeg"
        return fig_array(path.read_bytes()) if path.is_file() else None

    next_id = max((c["id"] for c in cards if c.get("variant")), default=5003) + 1
    n_sub = n_files = 0
    pending: dict[int, list] = {}
    for card in cards:
        if card not in affected:
            continue
        subs = pending.setdefault(card["id"], [])
        # Group statements: figured groups by cluster (in order of first
        # appearance), then the figure-less rump.
        groups = []          # [cluster_key_or_None, [statements]]
        where = {}
        for s in card["statements"]:
            key = find(s["number"]) if s["number"] in fig_cache else None
            if key not in where:
                where[key] = len(groups)
                groups.append([key, []])
            groups[where[key]][1].append(s)
        figured = [g for g in groups if g[0] is not None]
        rump = [g for g in groups if g[0] is None]
        # The base card keeps the figure group closest to its original image.
        oarr = orig_image_array(card)
        if oarr is not None:
            base_idx = min(range(len(figured)),
                           key=lambda i: fig_distance(oarr, arrs[figured[i][0]]))
        else:
            base_idx = max(range(len(figured)), key=lambda i: len(figured[i][1]))
        # Letters continue after any existing manual variants of this base.
        taken = [v["variant"] for v in cards
                 if v.get("variant") and v.get("base_id") == card["id"]]
        letter = max(taken, default=chr(ord("A") - 1))
        for gi, (key, sts) in enumerate(figured + rump):
            if gi == base_idx:
                card["statements"] = sts          # keeps its original image
                continue
            letter = chr(ord(letter) + 1)
            sub = {
                "id": next_id,
                "base_id": card["id"],
                "variant": letter,
                "variant_auto": True,
                "topic": card["topic"],
                "image": None,
                "statements": sts,
            }
            if key is not None:
                fname = f"{card['id']}_{sts[0]['number']}.jpeg"
                if not args.dry_run:
                    im = Image.open(io.BytesIO(fig_cache[sts[0]["number"]])).convert("RGB")
                    im.save(IMG_DIR / fname, "JPEG", quality=90)
                sub["image"] = f"{IMG_DIR_NAME}/{fname}"
                n_files += 1
            next_id += 1
            n_sub += 1
            subs.append(sub)
        # Re-key the base's frozen abridged (Quick-mode) entry: same kept
        # statement numbers, distributed to whichever card now holds them.
        kept = set(map(str, abridged.get(str(card["id"]), [])))
        if kept:
            for owner in [card] + subs:
                mine = sorted((str(s["number"]) for s in owner["statements"]
                               if str(s["number"]) in kept), key=int)
                key = str(owner["id"])
                if mine:
                    abridged[key] = mine
                elif key in abridged:
                    del abridged[key]
        print(f"  card {card['id']}: split into base ({len(card['statements'])} stmts, "
              f"original image) + {len(figured) + len(rump) - 1} subcards")
    # Insert each base's new subcards after its last existing variant (manual
    # variants keep their position and letters; autos follow them).
    new_list = []
    for card in cards:
        new_list.append(card)
    for base_id, subs in pending.items():
        last = max(i for i, c in enumerate(new_list)
                   if c["id"] == base_id or c.get("base_id") == base_id)
        new_list[last + 1:last + 1] = subs
    cards = new_list

    if not args.dry_run:
        QUESTIONS.write_text(
            json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        ABRIDGED.write_text(
            json.dumps(abridged, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        # Clean up generated figure files nothing references anymore.
        referenced = {c["image"].split("/")[-1] for c in cards if c.get("image")}
        removed = 0
        for p in IMG_DIR.glob("*_*.jpeg"):
            if p.name not in referenced:
                p.unlink()
                removed += 1
        print(f"Split {len(affected)} cards into {n_sub} subcards "
              f"({n_files} figure files; removed {removed} stale); "
              f"{QUESTIONS.name} updated.")
    else:
        print(f"(dry run) would create {n_sub} subcards / {n_files} figure files")


if __name__ == "__main__":
    main()
