#!/usr/bin/env python3
"""Build the packets for the explanation pass (docs/explanation-pass/RUBRIC.md).

  python3 scripts/explanation_pass_packets.py EPDIR

Writes EPDIR/packets/NN-k.json (a topic in chunks of about 250 live
statements, cards kept whole), EPDIR/figures.json (every figure the topic
reviews show in both halves, with its captions) and EPDIR/chunks.json.
A statement whose explanation ends with a fixed sentence (the added-clause
warning, the horn list) carries keep_tail_en / keep_tail_it; one that must
not be touched (warn, reading, already linked) carries skip.
"""
import json, re, os, glob, sys, collections, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
os.chdir(ROOT)
S = sys.argv[1]
os.makedirs(S + "/packets", exist_ok=True); os.makedirs(S + "/out", exist_ok=True); os.makedirs(S + "/ver", exist_ok=True)
qs = json.load(open("public_html/questions.json"))
tr = json.load(open("public_html/topic_reviews.json"))
mdfiles = {}
for f in sorted(glob.glob("topic_reviews_md/[0-9][0-9]-*.md")):
    m = re.search(r"<!-- TOPIC: (.*?) -->", open(f, encoding="utf8").read())
    mdfiles[m.group(1).strip()] = f
IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
strip = lambda a: re.sub(r"^!(xl|big|small)\s+", "", a)
figs = []
for topic, e in tr.items():
    if not isinstance(e, dict) or "en" not in e: continue
    it = {m.group(2): m.group(1) for m in IMG.finditer(e["it"])}
    for m in IMG.finditer(e["en"]):
        if m.group(2) in it:
            figs.append({"path": m.group(2), "caption_en": strip(m.group(1)), "caption_it": strip(it[m.group(2)]), "topic": topic[:60]})
json.dump(figs, open(S + "/figures.json", "w"), ensure_ascii=False, indent=1)

def tail(s, pats):
    for p in pats:
        i = s.find(p)
        if i >= 0:
            j = s.rfind(". ", 0, i)
            return s[j + 2:] if j >= 0 else s
    return None

bytopic = collections.OrderedDict()
for q in qs: bytopic.setdefault(q["topic"], []).append(q)
chunks = []
for topic in sorted(bytopic, key=lambda t: mdfiles[t]):
    cards = bytopic[topic]
    live = sum(1 for q in cards for s in q["statements"] if not s.get("retired"))
    nparts = max(1, round(live / 250)); target = live / nparts
    cur, n, part = [], 0, 0
    def flush():
        global cur, n, part
        if not cur: return
        part += 1
        cid = os.path.basename(mdfiles[topic])[:2] + "-" + str(part)
        json.dump({"chunk": cid, "topic": topic, "review_md": mdfiles[topic], "cards": cur}, open(f"{S}/packets/{cid}.json", "w"), ensure_ascii=False, indent=1)
        chunks.append({"id": cid, "n": n, "review": mdfiles[topic]})
        cur, n = [], 0
    for q in cards:
        st = []
        for s in q["statements"]:
            if s.get("retired"): continue
            d = {"number": str(s["number"]), "answer": s["answer"], "italian": s["italian_text"], "english": s["english_translation"],
                 "explanation": s.get("explanation", ""), "explanation_it": s.get("explanation_it", "")}
            if s.get("clause") or "(c) when carrying" in d["explanation"]:
                te = tail(d["explanation"], ["Read the whole sentence:", "(c) when carrying"])
                ti = tail(d["explanation_it"], ["Leggi tutta la frase:", "(c) trasportando"])
                if te: d["keep_tail_en"] = te
                if ti: d["keep_tail_it"] = ti
            if s.get("warn") or s.get("reading") or "notes:" in d["explanation"]: d["skip"] = True
            st.append(d)
        if not st: continue
        cur.append({"card": q["id"], "image": q.get("image"), "statements": st}); n += len(st)
        if n >= target - 5 and part < nparts - 1: flush()
    flush()
json.dump(chunks, open(S + "/chunks.json", "w"))
print(len(chunks), "chunks,", sum(c["n"] for c in chunks), "statements")
