#!/usr/bin/env python3
"""Fill author/licence data in IMAGE-CREDITS.md.

Two sources, in order:

1. `sign_library/library_index.csv` — metadata already captured by the earlier
   Commons fetches. Always used; needs no network.
2. The Commons API — only for files still missing data, and only when run with
   `--online`. Results are written back into library_index.csv so the next run
   needs no network for them.

    python3 scripts/fill_credits.py            # offline: local index only
    python3 scripts/fill_credits.py --online   # also query Commons for the rest

Author strings from Commons often carry HTML boilerplate ("This vector image
includes elements that have been taken or adapted from this file:"); those are
cleaned to a usable name or blanked.
"""
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "sign_library", "library_index.csv")
CREDITS = os.path.join(ROOT, "IMAGE-CREDITS.md")
API = "https://commons.wikimedia.org/w/api.php"
UA = "PatenteB-credits/1.0 (https://patente.physyapps.com; credits compilation)"

JUNK = re.compile(
    r"this vector image includes elements that have been taken or adapted from",
    re.I)


def clean_author(s):
    """Reduce a Commons Artist field to a usable attribution, or ''."""
    s = re.sub(r"\s+", " ", (s or "")).strip()
    if not s or JUNK.search(s):
        return ""
    # "Original: X Vectorization: Y" -> keep both, tidied
    s = re.sub(r"\s*Original:\s*", "Original: ", s)
    s = re.sub(r"\s*Vectorization:\s*", "; vectorization: ", s)
    return s.strip(" ;")


def load_index():
    with open(INDEX, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return rows


def save_index(rows):
    if not rows:
        return
    with open(INDEX, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def commons_meta(title):
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "titles": title,
        "prop": "imageinfo", "iiprop": "extmetadata",
    })
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    ii = (page.get("imageinfo") or [{}])[0]
    ext = ii.get("extmetadata", {})

    def field(k):
        v = ext.get(k, {}).get("value", "")
        return re.sub(r"<[^>]+>", " ", v or "")

    return clean_author(field("Artist")), re.sub(
        r"\s+", " ", field("LicenseShortName")).strip()


def main():
    online = "--online" in sys.argv
    rows = load_index()
    meta = {}
    for r in rows:
        f = (r.get("file") or "").strip()
        if f:
            meta[f] = (clean_author(r.get("author")), (r.get("license") or "").strip())

    # Which files does the credits table reference?
    lines = open(CREDITS, encoding="utf-8").read().split("\n")
    wanted = []
    for ln in lines:
        if ln.startswith("| ") and not ln.startswith("| Card") and "---" not in ln:
            p = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(p) >= 5 and p[2].startswith("File:"):
                wanted.append(p[2])
    todo = sorted({f for f in wanted
                   if not (meta.get(f, ("", ""))[0] and meta.get(f, ("", ""))[1])})
    print(f"{len(set(wanted))} distinct files referenced; {len(todo)} lack complete data")

    if online and todo:
        by_file = {(r.get("file") or "").strip(): r for r in rows}
        for i, f in enumerate(todo, 1):
            try:
                a, lic = commons_meta(f)
            except Exception as e:                      # noqa: BLE001
                print(f"  [{i}/{len(todo)}] {f}: {type(e).__name__}")
                continue
            if a or lic:
                meta[f] = (a or meta.get(f, ("", ""))[0],
                           lic or meta.get(f, ("", ""))[1])
                if f in by_file:
                    by_file[f]["author"] = meta[f][0]
                    by_file[f]["license"] = meta[f][1]
                print(f"  [{i}/{len(todo)}] {f} -> {meta[f][1]}")
            time.sleep(0.2)
        save_index(rows)
        print(f"wrote {INDEX}")

    # Rewrite the credits table
    out, filled = [], 0
    for ln in lines:
        if ln.startswith("| ") and not ln.startswith("| Card") and "---" not in ln:
            p = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(p) >= 5 and p[2].startswith("File:"):
                a, lic = meta.get(p[2], ("", ""))
                # clean_author also scrubs junk already sitting in the table
                new_a = clean_author(p[3]) or a
                new_l = p[4] or lic
                if (new_a, new_l) != (p[3], p[4]):
                    filled += 1
                out.append(f"| {p[0]} | {p[1]} | {p[2]} | {new_a} | {new_l} |")
                continue
        out.append(ln)
    open(CREDITS, "w", encoding="utf-8").write("\n".join(out))
    print(f"filled {filled} rows in {CREDITS}")

    still = sum(1 for ln in out
                if ln.startswith("| ") and "---" not in ln
                and not ln.startswith("| Card")
                and len([c for c in ln.strip().strip("|").split("|")]) >= 5
                and not all(c.strip() for c in ln.strip().strip("|").split("|")[3:5]))
    print(f"{still} rows still incomplete"
          + ("" if online else "; re-run with --online to query Commons"))


if __name__ == "__main__":
    main()
