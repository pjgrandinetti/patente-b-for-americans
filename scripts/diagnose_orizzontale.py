#!/usr/bin/env python3
"""
diagnose_orizzontale.py — figure out WHY some road-marking (segnaletica orizzontale)
figures never got downloaded. The library builder only keeps gallery lines that are
'<file>.svg | ... (figura N ...)', so it silently drops:
  - figures uploaded as .png/.gif instead of .svg
  - entries whose caption has no '(figura N)' tag
  - figures that simply aren't in the gallery at all

This reads the 'Road signs in Italy' gallery wikitext and prints EVERY entry whose
section looks like horizontal marking, with its extension and whether it has a
figura tag, so we can see the gaps. RUN ON A NETWORKED MACHINE. Read-only.
"""
import json, re, urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA  = "PatenteB-study-tool/1.0 (https://patente.physyapps.com; catalog diagnostic)"
GALLERY = "Road signs in Italy"

def api(params):
    params = {**params, "format": "json"}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params),
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)

def main():
    wt = api({"action": "parse", "page": GALLERY, "prop": "wikitext"})["parse"]["wikitext"]
    if isinstance(wt, dict):
        wt = wt.get("*", "")
    section, rows, sect_seen = "", [], set()
    for line in wt.splitlines():
        h = re.match(r"\s*={2,}\s*(.+?)\s*={2,}\s*$", line)
        if h:
            section = h.group(1).strip()
            continue
        m = re.match(r"\s*([^|\n\[\]]+?\.(svg|png|gif|jpg|jpeg))\s*\|(.*)", line, re.I)
        if not m:
            continue
        if "orizzont" not in section.lower():
            continue
        sect_seen.add(section)
        fname, ext, cap = m.group(1).strip(), m.group(2).lower(), m.group(3)
        fig = re.search(r"\(figura\s+([IVX]+\s+\d+(?:\s*/\s*[a-z])?)", cap, re.I)
        rows.append((fig.group(1).strip() if fig else "—NO FIGURE TAG—", ext, fname, cap.strip()[:70]))

    print(f"Horizontal-marking sections found: {sorted(sect_seen)}\n")
    print(f"{'figure':14s} {'ext':5s} file / caption")
    print("-" * 90)
    svg = png = notag = 0
    for fig, ext, fname, cap in sorted(rows, key=lambda r: r[0]):
        flag = "  <-- not .svg" if ext != "svg" else ""
        if ext == "svg": svg += 1
        else: png += 1
        if fig.startswith("—"): notag += 1
        print(f"{fig:14s} {ext:5s} {fname}{flag}")
    print(f"\nTotals in horizontal section: {len(rows)} entries — "
          f"{svg} svg, {png} non-svg, {notag} with no figure tag.")
    print("The non-svg and no-figure-tag rows are exactly what the current builder drops.")

if __name__ == "__main__":
    main()
