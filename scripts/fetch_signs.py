#!/usr/bin/env python3
"""
fetch_signs.py — download high-resolution SVG road-sign figures from Wikimedia
Commons to replace the low-res JPEGs extracted from DomandeB.pdf.

RUN THIS ON A MACHINE WITH INTERNET (it talks to commons.wikimedia.org). It is
kept out of the app; nothing here ships to the server.

Input:  scripts/sign_map.csv  — columns: id, figure, note
        - id     = the DomandeB card id (the image is domandeb_images/<id>.jpeg)
        - figure = the official figure, e.g. "II 4" or "II 30/a"
        - note   = free text (the sign name), for your reference only
Output: sign_svgs_staging/<id>.svg          (downloaded vectors, for review)
        sign_svgs_staging/credits.csv        (id, figure, file, author, license, url)

Workflow:
    1) python3 scripts/fetch_signs.py --list      # resolve matches, download nothing
    2) eyeball the resolved file titles, fix sign_map.csv if any look wrong
    3) python3 scripts/fetch_signs.py             # download the SVGs to staging
    4) open sign_svgs_staging/ and check the images look right
    5) tell Claude to wire the approved ones into the app (updates questions.json,
       review refs, and IMAGE-CREDITS.md, then bumps the version)

Only the SVG "vectorization" carries a license (usually CC BY-SA 4.0); the sign
design itself is public domain (official act of the Italian State). credits.csv
captures the per-file author + license so we can attribute correctly.
"""
import csv, json, os, re, sys, time, html, urllib.parse, urllib.request

API   = "https://commons.wikimedia.org/w/api.php"
# Wikimedia enforces its User-Agent policy: identify the tool + a contact URL, or
# requests get throttled/blocked. https://meta.wikimedia.org/wiki/User-Agent_policy
UA    = "PatenteB-study-tool/1.0 (https://patente.physyapps.com; road-sign image fetch)"
ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP   = os.path.join(ROOT, "scripts", "sign_map.csv")
OUT   = os.path.join(ROOT, "sign_svgs_staging")

GALLERY = "Road signs in Italy"   # authoritative Commons gallery; captions hold figures

def _open(url, tries=6):
    """urlopen with polite backoff on 429/503 (honors Retry-After when given)."""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return urllib.request.urlopen(req, timeout=45)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and i < tries - 1:
                wait = 0
                try:
                    wait = int(e.headers.get("Retry-After", "0"))
                except Exception:
                    wait = 0
                wait = min(90, wait or 3 * (2 ** i))   # cap so we never hang for minutes
                print(f"        {e.code} rate-limited; waiting {wait}s...")
                time.sleep(wait); continue
            raise
        except urllib.error.URLError:
            if i < tries - 1:
                time.sleep(2 * (2 ** i)); continue
            raise

def api(params):
    params = {**params, "format": "json"}
    url = API + "?" + urllib.parse.urlencode(params)
    with _open(url) as r:
        return json.load(r)

def norm_fig(fig):
    # Canonicalize "II 30/a", "(figura II 30-a)", "II  30 a" -> "ii30a" so the CSV
    # figure and the filename's embedded figure compare regardless of punctuation.
    return re.sub(r"[^a-z0-9]", "", fig.lower())

_catalog = None
def build_catalog():
    """figure(normalized) -> exact 'File:...' title, from the gallery's wikitext.
    Commons filenames are inconsistent (many pericolo signs have NO figure number
    in the name), but each gallery entry's CAPTION carries the figure. Inside
    <gallery> blocks entries are 'filename.svg|caption' with no File: prefix, so we
    parse those lines and take the figure from the caption."""
    global _catalog
    if _catalog is not None:
        return _catalog
    res = api({"action": "parse", "page": GALLERY, "prop": "wikitext"})
    wt = res.get("parse", {}).get("wikitext", "")
    if isinstance(wt, dict):
        wt = wt.get("*", "")
    fig_re = re.compile(r"\(figura\s+([IVX]+\s+\d+(?:\s*/\s*[a-z])?)", re.I)
    cat = {}
    for line in wt.splitlines():
        m = re.match(r"\s*([^|\n\[\]]+?\.svg)\s*\|(.*)", line, re.I)
        if not m:
            continue
        fname = re.sub(r"^(File:)?", "", m.group(1).strip(), flags=re.I).strip()
        fm = fig_re.search(m.group(2))
        if not fm:
            continue
        cat.setdefault(norm_fig(fm.group(1)), "File:" + fname)
    _catalog = cat
    lows = {k: cat[k] for k in ("ii1", "ii2", "ii3", "ii13") if k in cat}
    print(f"  (catalog: {len(cat)} figures from '{GALLERY}' captions; low figs: {lows})")
    return cat

def resolve(fig):
    """Return (file_title, reason) for the exact Commons SVG of a figure."""
    cat = build_catalog()
    title = cat.get(norm_fig(fig))
    if title:
        return title, "catalog"
    return None, "not in catalog"

def strip_html(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()

def imageinfo(title):
    res = api({"action": "query", "titles": title, "prop": "imageinfo",
               "iiprop": "url|extmetadata"})
    pages = res.get("query", {}).get("pages", {})
    ii = next(iter(pages.values())).get("imageinfo", [{}])[0]
    ext = ii.get("extmetadata", {})
    return {
        "url": ii.get("url", ""),
        "author": strip_html(ext.get("Artist", {}).get("value", "")),
        "license": strip_html(ext.get("LicenseShortName", {}).get("value", "")),
        "license_url": strip_html(ext.get("LicenseUrl", {}).get("value", "")),
    }

CREDS_FIELDS = ["id", "figure", "file", "author", "license", "license_url", "source_url"]

def main():
    list_only = "--list" in sys.argv
    if not os.path.isfile(MAP):
        sys.exit(f"Missing {MAP}. Create it with columns: id,figure,note")
    os.makedirs(OUT, exist_ok=True)
    rows = list(csv.DictReader(open(MAP, encoding="utf-8")))

    # Previous credits double as a manifest: id -> {file (title), author, ...}. A
    # cached <id>.svg is reused ONLY if it was fetched for the SAME title, so after
    # a sign_map change we re-fetch just the ids whose image actually changed.
    creds_path = os.path.join(OUT, "credits.csv")
    prev = {}
    if os.path.isfile(creds_path):
        prev = {r["id"]: r for r in csv.DictReader(open(creds_path, encoding="utf-8"))}
    out = {}
    fetched = skipped = 0
    for row in rows:
        cid, fig = row["id"].strip(), row["figure"].strip()
        if not cid or not fig:
            continue
        # Optional 'file' column: pin an exact 'File:...' title to override.
        override = (row.get("file") or "").strip()
        if override:
            title = override if override.lower().startswith("file:") else "File:" + override
            why = "override"
        else:
            try:
                title, why = resolve(fig)
            except Exception as e:
                print(f"  {cid}  figura {fig}: RESOLVE ERROR {e}"); continue
        if not title:
            print(f"  {cid}  figura {fig}: NO MATCH — set an exact File: title in sign_map.csv")
            continue
        dest = os.path.join(OUT, f"{cid}.svg")
        if not list_only and os.path.isfile(dest) and prev.get(cid, {}).get("file") == title:
            out[cid] = prev[cid]          # unchanged → keep its credit row
            skipped += 1
            continue
        info = imageinfo(title)
        print(f"  {cid}  figura {fig:7s} [{why}] -> {title}")
        print(f"        author: {info['author'] or '?'} | license: {info['license'] or '?'}")
        out[cid] = {"id": cid, "figure": fig, "file": title, "author": info["author"],
                    "license": info["license"], "license_url": info["license_url"],
                    "source_url": info["url"]}
        if not list_only and info["url"]:
            with _open(info["url"]) as r, open(dest, "wb") as f:
                f.write(r.read())
            print(f"        saved {dest}")
            fetched += 1
            time.sleep(3.0)  # be gentle: pause only between actual downloads
    if out and not list_only:
        with open(creds_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CREDS_FIELDS)
            w.writeheader(); w.writerows(out.values())
        print(f"\nWrote {creds_path} ({len(out)} rows)")
    print(f"Done. fetched {fetched}, reused {skipped}." + ("  (--list)" if list_only else ""))

if __name__ == "__main__":
    main()
