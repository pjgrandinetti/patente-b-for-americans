#!/usr/bin/env python3
"""Write docs/explanation-pass/results/NN-proposed.md for the maintainer.

  python3 scripts/explanation_pass_report.py EPDIR NN "Topic name" CHUNK...

Every proposed rewrite of the topic, before and after, as the checker left
it. Link words are shown in [brackets]. Link-only changes are listed last.
"""
import json, re, sys, pathlib
ep, nn, name, chunks = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
N = re.compile(r"\[([^\]]+)\]\(notes:[^)]+\)")
show = lambda t: N.sub(lambda m: "[" + m.group(1) + "]", t)
plain = lambda t: N.sub(lambda m: m.group(1), t)
full, links, rejected = [], [], []
for cid in chunks:
    o = json.load(open(f"{ep}/out/{cid}.json"))["rewrites"]
    v = json.load(open(f"{ep}/ver/{cid}.json"))["verdicts"]
    for c in json.load(open(f"{ep}/packets/{cid}.json"))["cards"]:
        for s in c["statements"]:
            n = s["number"]
            if n not in o: continue
            vd = v.get(n, {"v": "none"})
            if vd["v"] == "reject":
                rejected.append(f"- **{n}**: {vd.get('why', '')}"); continue
            en, it = (vd["en"], vd["it"]) if vd["v"] == "correct" else (o[n]["en"], o[n]["it"])
            tag = ", corrected by the checker" if vd["v"] == "correct" else ""
            head = [f"## {n} ({s['answer']}){tag}", "", f"*{s['italian']}*", "", s["english"], ""]
            if plain(en).strip() == s["explanation"].strip():
                links += head + [f"**Link added:** {show(en)}", ""]
            else:
                full += head + [f"**Now:** {s['explanation']}", "", f"**Proposed:** {show(en)}", "", f"**Proposta:** {show(it)}", ""]
out = [f"# Explanation pass, topic {nn} ({name}): proposed changes", "",
       "Not applied yet. Words that become links into the notes are shown in [brackets].", "",
       f"# Rewrites ({sum(1 for l in full if l.startswith('## '))})", ""] + full
if links: out += [f"# Link only, wording unchanged ({sum(1 for l in links if l.startswith('## '))})", ""] + links
if rejected: out += ["# Rejected by the checker (old explanation kept)", ""] + rejected
p = pathlib.Path(__file__).resolve().parent.parent / "docs" / "explanation-pass" / "results" / f"{nn}-proposed.md"
p.write_text("\n".join(out), encoding="utf-8")
print(p, "rewrites", sum(1 for l in full if l.startswith("## ")), "link-only", sum(1 for l in links if l.startswith("## ")), "rejected", len(rejected))
