#!/usr/bin/env python3
"""
fetch_category.py — add every figure from a Commons *category* to the sign library.
The main gallery ('Road signs in Italy') omits many road-marking diagrams — they
live in Category:Diagrams of road markings of Italy and are often PNGs, so the
gallery-based builder never saw them. This walks the category, downloads each file
(SVG *or* raster), reads its figure number, and merges it into sign_library/.

RUN ON A NETWORKED MACHINE. Resumable (skips files already present). Read-only to
the app; nothing here ships to the server.

Usage:
    python3 scripts/fetch_category.py
    python3 scripts/fetch_category.py "Category:Some other category"

Writes: sign_library/<normfig-or-slug>.<ext>
        sign_library/library_index.csv   (adds an 'ext' column; existing rows -> svg)
"""
import csv, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_signs import api, _open, imageinfo   # polite API + download + license

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB  = os.path.join(ROOT, "sign_library")
IDX  = os.path.join(LIB, "library_index.csv")
DEFAULT_CAT = "Category:Diagrams of road markings of Italy"
IMG_EXT = ("svg", "png", "gif", "jpg", "jpeg")

def category_files(cat):
    """All File: titles in the category (follows pagination)."""
    files, cont = [], {}
    while True:
        res = api({"action": "query", "list": "categorymembers", "cmtitle": cat,
                   "cmtype": "file", "cmlimit": "500", **cont})
        files += [m["title"] for m in res.get("query", {}).get("categorymembers", [])]
        if "continue" in res:
            cont = res["continue"]
        else:
            break
    return files

def figure_key(title, desc=""):
    """Derive a normfig like 'ii416' or 'ii441c' ONLY from an explicit '(figura II
    NNN[-/ ]x)' tag in the FILENAME. Free-text descriptions proved unreliable (they
    yielded spurious keys like ii437d and collided unrelated files), so we ignore
    them and slug anything without a clean filename tag. Road markings are family II.
    Handles '-', '/', or space before the sub-letter (Commons uses '441-c')."""
    m = re.search(r"\(figura\s+(?:[IVX]+\s+)?(\d+)\s*[-/ ]?\s*([a-z])?\)", title, re.I)
    if m:
        return "ii" + m.group(1) + (m.group(2).lower() if m.group(2) else "")
    return ""

def slug(title):
    s = re.sub(r"^File:", "", title, flags=re.I)
    s = re.sub(r"\.[a-z0-9]+$", "", s, flags=re.I)
    return "rm-" + re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]

def main():
    cat = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CAT
    os.makedirs(LIB, exist_ok=True)
    # load existing index; ensure every row has an 'ext' (default svg for old rows)
    idx = {}
    if os.path.isfile(IDX):
        for r in csv.DictReader(open(IDX, encoding="utf-8")):
            r.setdefault("ext", "svg")
            if not r.get("ext"):
                r["ext"] = "svg"
            idx[r["normfig"]] = r

    titles = category_files(cat)
    print(f"{cat}: {len(titles)} files")
    got = have = skip = 0
    unmapped = []
    for title in titles:
        info = imageinfo(title)  # url, author, license (+extmetadata)
        url = info.get("url", "")
        if not url:
            print(f"  no url: {title}"); continue
        ext = url.rsplit(".", 1)[-1].lower()
        if ext not in IMG_EXT:
            print(f"  skip non-image: {title}"); skip += 1; continue
        key = figure_key(title)
        if not key:
            key = slug(title); unmapped.append(title)
        dst = os.path.join(LIB, f"{key}.{ext}")
        if os.path.isfile(dst) or os.path.isfile(os.path.join(LIB, f"{key}.svg")):
            have += 1
            idx.setdefault(key, {"normfig": key, "figure": key.upper().replace("II", "II "),
                                 "name": re.sub(r"^File:|\.[a-z]+$", "", title),
                                 "file": title, "author": "", "license": "", "ext": ext})
            continue
        with _open(url) as r, open(dst, "wb") as f:
            f.write(r.read())
        idx[key] = {"normfig": key,
                    "figure": ("II " + key[2:]) if re.match(r"ii\d", key) else key,
                    "name": re.sub(r"^File:|\.[a-z]+$", "", title),
                    "file": title, "author": info.get("author", ""),
                    "license": info.get("license", ""), "ext": ext}
        got += 1
        print(f"  {key:10s} .{ext:4s} <- {title}")
        time.sleep(3.0)

    with open(IDX, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["normfig", "figure", "name", "file",
                                          "author", "license", "ext"])
        w.writeheader()
        for r in idx.values():
            r.setdefault("ext", "svg")
            w.writerow({k: r.get(k, "") for k in w.fieldnames})
    print(f"\nAdded {got}, already had {have}, skipped {skip}. Library index: {IDX}")
    if unmapped:
        print(f"\n{len(unmapped)} file(s) had no figure number in title/description "
              f"(saved with a slug name; may need manual figure mapping):")
        for t in unmapped:
            print("   ", t)

if __name__ == "__main__":
    main()
