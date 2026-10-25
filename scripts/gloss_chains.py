#!/usr/bin/env python3
"""
Write, per topic, every statement with the gloss chain the app would show and
the full English translation, for a reading audit of whether the glosses lead
to the translation's meaning (glossary note of 2026-09-11).

The chain is assembled exactly as app.js does it: longest term first, no
overlapping spans, final-vowel wildcard narrowed away from any form that is an
entry in its own right (entry_regex in consolidate_vocab.py).

Usage:  python3 scripts/gloss_chains.py OUTDIR
Then hand each OUTDIR/topicNN.txt to a reader with docs/GLOSS-AUDIT-RUBRIC.md.
Files over ~130 KB are split in two at a statement boundary.
"""
import json, os, re, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from consolidate_vocab import entry_regex, all_entries

ROOT = Path(__file__).resolve().parent.parent
out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/gloss-audit")
out.mkdir(parents=True, exist_ok=True)
v = json.loads((ROOT / "public_html" / "vocabulary.json").read_text(encoding="utf-8"))
q = json.loads((ROOT / "public_html" / "questions.json").read_text(encoding="utf-8"))
entries = sorted(all_entries(v), key=lambda e: -len(e["term"]))
known = frozenset(" ".join(e["term"].lower().split()) for e in entries)
pats = [(e, entry_regex(e["term"], known)) for e in entries]

def chain(text):
    cov = [False] * len(text); hits = []
    for e, p in pats:
        for m in p.finditer(text):
            if any(cov[m.start():m.end()]):
                continue
            for i in range(m.start(), m.end()):
                cov[i] = True
            hits.append((m.start(), m.group(0), e["en"]))
    return sorted(hits)

bytopic = collections.defaultdict(list)
for c in q:
    for s in c["statements"]:
        bytopic[c["topic"]].append(s)
for i, (topic, sts) in enumerate(sorted(bytopic.items(), key=lambda kv: min(int(s["number"]) for s in kv[1])), 1):
    blocks = []
    for s in sts:
        blocks.append(f"#{s['number']}\nIT: {s['italian_text']}\nGLOSSES: "
                      + " | ".join(f"{surf} = {g}" for _, surf, g in chain(s["italian_text"]))
                      + f"\nEN: {s['english_translation']}\n")
    head = f"TOPIC: {topic}\n"
    body = "\n".join(blocks)
    if len(body) > 130_000:
        mid = len(blocks) // 2
        (out / f"topic{i:02}_a.txt").write_text(head + "\n" + "\n".join(blocks[:mid]), encoding="utf-8")
        (out / f"topic{i:02}_b.txt").write_text(head + "\n" + "\n".join(blocks[mid:]), encoding="utf-8")
    else:
        (out / f"topic{i:02}.txt").write_text(head + "\n" + body, encoding="utf-8")
    print(f"topic{i:02}  {len(sts):4} statements  {topic[:60]}")
