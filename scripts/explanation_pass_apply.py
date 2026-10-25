#!/usr/bin/env python3
"""Apply the explanation pass (docs/explanation-pass/RUBRIC.md).

  python3 scripts/explanation_pass_apply.py EPDIR [CHUNK ...] [--dry]

EPDIR holds packets/, out/ (the writers' rewrites) and ver/ (the checkers'
verdicts). A rewrite is applied only when its checker accepted or corrected
it AND it passes the mechanical checks below; everything refused is listed
with its reason, and the old explanation stays.
"""
import json, re, sys, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
QP = ROOT / "public_html" / "questions.json"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
dry = "--dry" in sys.argv
links_only = "--links-only" in sys.argv   # the wording must be unchanged apart from the links
ep = pathlib.Path(args[0])
only = set(args[1:])

figs = {f["path"] for f in json.load(open(ep / "figures.json"))}
NOTES = re.compile(r"\[([^\]]+)\]\(notes:([^)\s]+)\)")
BAD_EN = re.compile(r"this card|the card|other statements?|sibling|false variant|false version|trap answer|\bthe exam\b|\bquiz\b|the bank|—|€|\beuros?\b|!", re.I)
BAD_IT = re.compile(r"questa scheda|la scheda|altre affermazioni|variante falsa|versione falsa|\bquiz\b|—|€|\beuro\b|!", re.I)

def sentences(t):
    t = NOTES.sub(lambda m: m.group(1), t)
    return len(re.findall(r"[.?](?:\s|$)", t))

def check(num, st, card_img, en, it):
    v = "True." if st["answer"] == "VERO" else "False."
    vi = "Vero." if st["answer"] == "VERO" else "Falso."
    if not en.startswith(v[:-1]) or not it.startswith(vi[:-1]):
        return "verdict word does not match the answer"
    if st.get("skip"):
        return "statement is marked skip"
    for k, txt in (("keep_tail_en", en), ("keep_tail_it", it)):
        if st.get(k) and not txt.rstrip().endswith(st[k].rstrip()):
            return f"{k} is not the closing text"
    le, li = NOTES.findall(en), NOTES.findall(it)
    if sorted(t for _, t in le) != sorted(t for _, t in li):
        return "English and Italian link different figures"
    for _, t in le:
        if t not in figs:
            return f"link to a figure not in the reviews: {t}"
        if t == card_img:
            return "links the card's own figure"
    if len(le) > 3:
        return "more than three links"
    body_en = en[: len(en) - len(st.get("keep_tail_en", ""))] if st.get("keep_tail_en") else en
    body_it = it[: len(it) - len(st.get("keep_tail_it", ""))] if st.get("keep_tail_it") else it
    m = BAD_EN.search(NOTES.sub(lambda m: m.group(1), body_en))
    if m: return f"English contains '{m.group(0)}'"
    m = BAD_IT.search(NOTES.sub(lambda m: m.group(1), body_it))
    if m: return f"Italian contains '{m.group(0)}'"
    if en.count("*") % 2 or it.count("*") % 2:
        return "unpaired asterisk"
    if abs(sentences(en) - sentences(it)) > 1:
        return f"sentence counts differ ({sentences(en)} EN, {sentences(it)} IT)"
    if len(en) < len(st["explanation"]) * 0.6 and not st.get("keep_tail_en"):
        return "rewrite is much shorter than the original"
    return None

raw = QP.read_text(encoding="utf-8")
applied, refused, problems = {}, [], []
stats = collections.Counter()
for pk in sorted((ep / "packets").glob("*.json")):
    cid = pk.stem
    if only and cid not in only: continue
    out, ver = ep / "out" / f"{cid}.json", ep / "ver" / f"{cid}.json"
    if not out.exists():
        print(f"{cid}: no writer output"); continue
    packet = json.load(open(pk))
    o = json.load(open(out))
    v = json.load(open(ver)).get("verdicts", {}) if ver.exists() else None
    by = {s["number"]: (s, c.get("image")) for c in packet["cards"] for s in c["statements"]}
    for p in o.get("problems", []): problems.append((cid, p))
    for num, rw in o.get("rewrites", {}).items():
        stats["rewrites"] += 1
        if num not in by: refused.append((cid, num, "not in the packet")); continue
        st, img = by[num]
        if v is None: refused.append((cid, num, "no checker verdict")); continue
        vd = v.get(num)
        if not vd: refused.append((cid, num, "checker gave no verdict")); continue
        if vd["v"] == "reject": refused.append((cid, num, "checker: " + vd.get("why", ""))); stats["rejected"] += 1; continue
        en, it = (vd["en"], vd["it"]) if vd["v"] == "correct" else (rw["en"], rw["it"])
        if vd["v"] == "correct": stats["corrected"] += 1
        why = check(num, st, img, en.strip(), it.strip())
        if not why and links_only:
            strip = lambda t: NOTES.sub(lambda m: m.group(1), t).strip()
            if strip(en) != st["explanation"].strip() or strip(it) != st["explanation_it"].strip():
                why = "wording changed in a links-only pass"
            elif not NOTES.search(en):
                why = "no link added"
        if why: refused.append((cid, num, "mechanical: " + why)); continue
        applied[num] = (st["explanation"], st["explanation_it"], en.strip(), it.strip())

n = 0
for num, (oe, oi, ne, ni) in applied.items():
    for old, new in ((oe, ne), (oi, ni)):
        o_ = json.dumps(old, ensure_ascii=False)
        if raw.count(o_) < 1:
            refused.append(("?", num, "original text not found in questions.json")); break
    else:
        # replace inside this statement's own object only
        i = raw.find(f'"number": {num},')
        if i < 0: i = raw.find(f'"number": "{num}"')
        j = raw.find('"number":', i + 10)
        seg = raw[i: j if j > 0 else len(raw)]
        seg2 = seg.replace(json.dumps(oe, ensure_ascii=False), json.dumps(ne, ensure_ascii=False), 1).replace(json.dumps(oi, ensure_ascii=False), json.dumps(ni, ensure_ascii=False), 1)
        if seg2 == seg: refused.append(("?", num, "statement object not matched")); continue
        raw = raw[:i] + seg2 + raw[(j if j > 0 else len(raw)):]
        n += 1
if not dry: QP.write_text(raw, encoding="utf-8")
print(f"rewrites proposed {stats['rewrites']}, applied {n}{' (dry run)' if dry else ''}, checker-corrected {stats['corrected']}, checker-rejected {stats['rejected']}, refused in all {len(refused)}, problems reported {len(problems)}")
rep = ep / "report.json"
json.dump({"refused": refused, "problems": problems}, open(rep, "w"), ensure_ascii=False, indent=1)
print(f"details: {rep}")
