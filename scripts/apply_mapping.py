#!/usr/bin/env python3
"""
apply_mapping.py — apply the human-confirmed image mapping to the app.

For every card the reviewer confirmed (review_verdicts.csv, buckets 1/2/3 with a
chosen figure):
  1. move the ORIGINAL low-res image out of public_html/domandeb_images/ into
     replaced_images_backup/ (so a revert is trivial),
  2. copy the chosen Commons figure into domandeb_images/ under the card's name
     but with the figure's real extension (svg/png/gif/jpg),
  3. rewrite ONLY the image path in questions.json and in the topic-review Markdown
     (text-level replace — Italian text/answers are never parsed or reserialized).

No-match cards and undecided cards are left completely untouched.

Run:  python3 scripts/apply_mapping.py            # dry run: prints the plan
      python3 scripts/apply_mapping.py --apply    # actually do it
Then: python3 scripts/md_to_reviews.py            # rebuild reviews + bump sw.js
      (sync APP_VERSION), python3 scripts/validate_data.py
"""
import csv, glob, json, os, re, shutil, sys

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB    = os.path.join(ROOT, "public_html")
IMGDIR = os.path.join(PUB, "domandeb_images")
LIBDIR = os.path.join(ROOT, "sign_library")
IDX    = os.path.join(LIBDIR, "library_index.csv")
CSV    = os.path.join(ROOT, "review_verdicts.csv")
BACKUP = os.path.join(ROOT, "replaced_images_backup")
QJSON  = os.path.join(PUB, "questions.json")
CREDITS= os.path.join(ROOT, "IMAGE-CREDITS.md")
IMG_EXT= (".svg", ".png", ".gif", ".jpg", ".jpeg")

def libfiles():
    out = {}
    for fn in sorted(os.listdir(LIBDIR)):
        stem, ext = os.path.splitext(fn)
        if ext.lower() in IMG_EXT:
            out.setdefault(stem, fn)
    return out

def main():
    apply = "--apply" in sys.argv
    LIBF = libfiles()
    idx  = {r["normfig"]: r for r in csv.DictReader(open(IDX, encoding="utf-8"))} \
           if os.path.isfile(IDX) else {}
    img_by_id = {str(c["id"]): c.get("image", "")
                 for c in json.load(open(QJSON, encoding="utf-8")) if c.get("image")}

    plan = []   # (cid, old_rel, new_rel, libfile, nf)
    for r in csv.DictReader(open(CSV, encoding="utf-8")):
        if not (r.get("bucket") or "").strip():
            continue
        nf = r.get("chosen_normfig", "")
        if not nf:                      # bucket 4 (no match) -> keep original
            continue
        cid = str(r["id"]); old_rel = img_by_id.get(cid)
        if not old_rel or nf not in LIBF:
            print(f"  ! skip #{cid}: old={old_rel!r} nf={nf!r} (missing)"); continue
        base = os.path.splitext(os.path.basename(old_rel))[0]
        ext  = os.path.splitext(LIBF[nf])[1]
        new_rel = f"domandeb_images/{base}{ext}"
        plan.append((cid, old_rel, new_rel, LIBF[nf], nf))

    print(f"{'APPLYING' if apply else 'DRY RUN'} — {len(plan)} image replacements")
    if not apply:
        for cid, old, new, lf, nf in plan[:8]:
            print(f"   #{cid}: {old}  ->  {new}   (from {lf})")
        print("   ...") if len(plan) > 8 else None
        print("Re-run with --apply to perform it.")
        return

    os.makedirs(BACKUP, exist_ok=True)
    moved = copied = 0
    for cid, old_rel, new_rel, lf, nf in plan:
        src = os.path.join(PUB, old_rel)
        if os.path.isfile(src):
            shutil.move(src, os.path.join(BACKUP, os.path.basename(old_rel)))
            moved += 1
        shutil.copy(os.path.join(LIBDIR, lf), os.path.join(PUB, new_rel))
        copied += 1
    print(f"  moved {moved} originals -> {os.path.relpath(BACKUP, ROOT)}/, copied {copied} figures in")

    # text-level path swap in questions.json (quoted value -> unique, one hit each)
    qt = open(QJSON, encoding="utf-8").read()
    for _, old_rel, new_rel, _, _ in plan:
        qt = qt.replace(f'"{old_rel}"', f'"{new_rel}"')
    open(QJSON, "w", encoding="utf-8").write(qt)
    print("  updated image paths in questions.json")

    # topic-review Markdown refs (bare path, may occur multiple times)
    md_changed = 0
    for md in glob.glob(os.path.join(ROOT, "topic_reviews_md", "*.md")):
        t = open(md, encoding="utf-8").read(); orig = t
        for _, old_rel, new_rel, _, _ in plan:
            t = t.replace(old_rel, new_rel)
        if t != orig:
            open(md, "w", encoding="utf-8").write(t); md_changed += 1
    print(f"  updated {md_changed} topic-review Markdown files")

    # attribution file
    with open(CREDITS, "w", encoding="utf-8") as f:
        f.write("# Image credits\n\n")
        f.write("High-resolution road-sign figures sourced from Wikimedia Commons. The sign\n"
                "*designs* are public domain (official acts of the Italian State); the SVG\n"
                "*vectorizations* may carry a CC BY-SA licence, attributed below where known.\n\n")
        f.write("| Card | Figure | Commons file | Author | Licence |\n")
        f.write("|------|--------|--------------|--------|---------|\n")
        for cid, _, _, _, nf in sorted(plan, key=lambda p: p[0]):
            r = idx.get(nf, {})
            f.write(f"| {cid} | {r.get('figure', nf)} | {r.get('file','')} | "
                    f"{r.get('author','')} | {r.get('license','')} |\n")
    n_missing = sum(1 for _, _, _, _, nf in plan if not idx.get(nf, {}).get("license"))
    print(f"  wrote {os.path.basename(CREDITS)} ({n_missing} figures still missing a licence)")
    print("\nNext: python3 scripts/md_to_reviews.py ; sync APP_VERSION ; python3 scripts/validate_data.py")

if __name__ == "__main__":
    main()
