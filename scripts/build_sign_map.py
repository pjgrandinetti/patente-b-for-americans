#!/usr/bin/env python3
"""
build_sign_map.py — generate a CANDIDATE domandeB-image -> figure mapping for
every card that has an image, by matching the card's sign description against the
official figure names on Wikimedia Commons, CONSTRAINED to the figure family that
matches the card's topic (a pericolo card only matches pericolo figures, etc.).

RUN ON A NETWORKED MACHINE (reads the Commons gallery once). Output is a best
guess per card — the comparison PDF is what verifies it.

Output: scripts/sign_map.csv  (id, figure, note, score, file)
Then:   python3 scripts/fetch_signs.py --list   # sanity-check
        python3 scripts/fetch_signs.py          # download the candidates
"""
import csv, json, os, re, urllib.parse, urllib.request

API     = "https://commons.wikimedia.org/w/api.php"
UA      = "PatenteB-study-tool/1.0 (https://patente.physyapps.com; sign map builder)"
GALLERY = "Road signs in Italy"
ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT     = os.path.join(ROOT, "scripts", "sign_map.csv")

STOP = set("segnale segnali di a al ai con per il lo la i gli le un uno una e ed o "
           "del dei della delle su sul in tra fra che è d dell art figura tabella "
           "modello degli sugli alla raffigurato raffigurata presenza".split())

# DomandeB topic -> gallery section keywords (substring match, lowercase). Topics
# not listed match against ALL figures (rule topics that reference many families).
TOPIC_SECTIONS = {
    "Segnali di pericolo": ["pericolo"],
    "Segnali di divieto": ["divieto"],
    "Segnali di obbligo": ["obbligo"],
    "Segnali di precedenza": ["precedenza"],
    "Segnali di indicazione": ["indicazione", "simboli", "preavviso", "intersezione",
        "preselezione", "direzione", "identificazione", "itinerario", "localit",
        "conferma", "nome-strada", "turistic", "alberghiera", "utili per la guida",
        "servizi"],
    "Segnaletica orizzontale; segni sugli ostacoli": ["orizzontal"],
    "Segnali complementari; segnali temporanei e di cantiere": ["complementari", "temporanei"],
    "Segnalazioni semaforiche; segnalazioni degli agenti del traffico": ["luminosi"],
    "Pannelli integrativi dei segnali": ["pannelli integrativi", "tabelle"],
}

# Topics whose images are scenario/diagram drawings, not single signs: never try
# to match them to a figure (they have no Commons single-figure equivalent).
NO_SIGN_TOPICS = {
    "Esempi di precedenza (ordine di precedenza agli incroci)",
}

def api(params):
    params = {**params, "format": "json"}
    with urllib.request.urlopen(
            urllib.request.Request(API + "?" + urllib.parse.urlencode(params),
                                   headers={"User-Agent": UA}), timeout=45) as r:
        return json.load(r)

def norm_fig(fig):
    return re.sub(r"[^a-z0-9]", "", fig.lower())

def toks(s):
    return {w for w in re.split(r"[^a-zàèéìòù]+", s.lower()) if len(w) > 2 and w not in STOP}

def clean_name(s):
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]", r"\1", s)   # [[x|y]] / [[y]] -> y
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def build_catalog():
    """list of dicts: {figure, name, file, section} from the gallery wikitext,
    tracking the current == section == header above each gallery entry."""
    res = api({"action": "parse", "page": GALLERY, "prop": "wikitext"})
    wt = res.get("parse", {}).get("wikitext", "")
    if isinstance(wt, dict):
        wt = wt.get("*", "")
    entries, section = [], ""
    for line in wt.splitlines():
        h = re.match(r"\s*={2,}\s*(.+?)\s*={2,}\s*$", line)
        if h:
            section = h.group(1).strip().lower()
            continue
        m = re.match(r"\s*([^|\n\[\]]+?\.svg)\s*\|(.*)", line, re.I)
        if not m:
            continue
        fm = re.search(r"\(figura\s+([IVX]+\s+\d+(?:\s*/\s*[a-z])?)", m.group(2), re.I)
        if not fm:
            continue
        fname = re.sub(r"^(File:)?", "", m.group(1).strip(), flags=re.I).strip()
        name = clean_name(m.group(2).split("(figura")[0])
        entries.append({"figure": re.sub(r"\s+", " ", fm.group(1).strip()),
                        "name": name, "file": "File:" + fname, "section": section})
    return entries

def main():
    print(f"Reading figure catalog from '{GALLERY}' ...")
    cat = build_catalog()
    for e in cat:
        e["nt"] = toks(e["name"])
    print(f"  {len(cat)} figures across {len(set(e['section'] for e in cat))} sections.")

    data = json.load(open(os.path.join(ROOT, "public_html", "questions.json"), encoding="utf-8"))
    rows = []
    for c in data:
        if not c.get("image"):
            continue
        cid = str(c.get("id"))
        topic = c.get("topic", "")
        alltext = " ".join(s.get("italian_text", "") for s in c.get("statements", []))
        if topic in NO_SIGN_TOPICS:
            rows.append({"id": cid, "figure": "", "note": "(scenario/diagram — not a single sign)",
                         "score": "0", "file": ""})
            continue
        # Skip only genuine A-vs-B comparison images (two signs in one picture).
        # The '_<n>' per-question images are single signs and must NOT be skipped —
        # they carry a filename like 4029_18610.jpeg but still show one sign.
        if re.search(r"\(A\)", alltext) and re.search(r"\(B\)", alltext):
            rows.append({"id": cid, "figure": "", "note": "(composite: compares sign A vs B — keep original)",
                         "score": "0", "file": ""})
            continue
        keys = TOPIC_SECTIONS.get(topic)
        pool = [e for e in cat if (keys is None or any(k in e["section"] for k in keys))] or cat
        # Match against EACH statement separately and keep the best figure: this
        # isolates the sign-naming sentence from the card's rule/behavior sentences.
        stmt_toks = [toks(s.get("italian_text", "")) for s in c.get("statements", [])]
        best, best_key = None, (-1.0, -1)
        for st in stmt_toks:
            for e in pool:
                nt = e["nt"]
                if not nt:
                    continue
                matched = len(nt & st)
                if not matched:
                    continue
                key = (matched / len(nt), matched)     # coverage first, then hit count
                if key > best_key:
                    best, best_key = e, key
        if best:
            rows.append({"id": cid, "figure": best["figure"], "note": best["name"],
                         "score": f"{best_key[0]*100 + best_key[1]:.1f}", "file": ""})
        else:
            rows.append({"id": cid, "figure": "", "note": "(no match — composite/scenario?)",
                         "score": "0", "file": ""})
    rows.sort(key=lambda r: (r["figure"] == "", r["id"]))
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "figure", "note", "score", "file"])
        w.writeheader(); w.writerows(rows)
    matched = sum(1 for r in rows if r["figure"])
    print(f"Wrote {OUT}: {len(rows)} image-cards, {matched} matched, {len(rows)-matched} unmatched.")

if __name__ == "__main__":
    main()
