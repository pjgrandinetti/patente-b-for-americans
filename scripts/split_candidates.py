#!/usr/bin/env python3
"""The packet for the SPLIT step: blocks that may bundle rules, with the
statements that depend on them.

Glossary rule 40 says a review bullet teaches one rule. Step 4 of the claims
rollout is where a bundled bullet gets broken up, and this script builds what a
reader needs to do that in one pass: for every candidate block, its English
text, its Italian twin, why it was flagged, and EVERY statement whose claim
lands on it, with answer, Italian, English and explanation. A split is only
safe with that list in view, because each fragment has to inherit the
statements it actually answers.

A block is a candidate when any of these holds:

  semicolon   it contains a semicolon, which in this house style is two ideas
              welded into one sentence (the style bans it outright)
  labels      two or more bold runs OPEN a sentence ("**No parking** …
              **No stopping** …"), so the bullet announces two subjects
  bundled     it is CLAIMED and its Italian twin runs to three or more
              sentences, so the sentence marker can only guess which one
              answers the statement

The third is a suspicion, not a verdict: a three-sentence bullet that teaches
one rule properly is fine, and the reader is asked to say so. Blocks under a
summary heading are skipped, since a summary is meant to gather.

Output: OUT/candidates.md (the reader's packet) and OUT/index.json (block
hashes and the claimed statements per candidate, for the apply step).

Usage: python3 scripts/split_candidates.py 16 OUTDIR
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public_html"
sys.path.insert(0, str(ROOT / "scripts"))
import md_to_reviews as M          # noqa: E402
import review_landings as RL       # noqa: E402

LABEL_RE = re.compile(r"(?:^|(?<=[.!?:])\s+)\*\*([^*]{3,40}?)\*\*")
SUMMARY = ("summary of key points", "riepilogo dei punti chiave", "the map for this topic",
           "la mappa dell'argomento")

RUBRIC = """# Splitting the bundled bullets of one topic

Each section below is one candidate bullet: the English block, its Italian
twin, why it was flagged, and every statement whose 📖 currently lands on it.

Decide, for each candidate, one of two things.

KEEP. The bullet teaches ONE rule, even if it runs to several sentences,
because the later sentences qualify or explain the same rule. Say so and move
on. Do not split a coherent bullet just because it is long: that is explicitly
allowed.

SPLIT. The bullet welds together rules a learner would look for separately.
Rewrite it as two or more bullets, each stating ONE rule in one to three
complete sentences, and then say which of the listed statements belongs to
each new bullet. Every statement must land somewhere.

Rules for the text you write.
1. English and Italian must match sentence for sentence, and you must supply
   both. The two halves are paired block by block, so the split must be
   identical in each.
2. Complete sentences. No semicolons, no em dashes, no parentheses carrying a
   rule (promote it to its own sentence). American English.
3. State the rule positively, as fact. Never mention the exam, statements,
   traps, or that something is false.
4. Keep the existing wording wherever you can. This is a split, not a rewrite,
   and no rule may be added or dropped.
5. Keep the bold terms and the *italian glosses* as they are.

Output, as JSON:
{
  "decisions": [
    {"block": "B03", "action": "keep", "why": "one rule, the later sentences qualify it"},
    {"block": "B07", "action": "split",
     "bullets": [
       {"en": "- …", "it": "- …", "stmts": ["18446", "18447"]},
       {"en": "- …", "it": "- …", "stmts": ["18452"]}
     ]}
  ]
}
Every statement listed under a SPLIT block must appear in exactly one bullet.
"""


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    prefix, outdir = argv[0], Path(argv[1])
    outdir.mkdir(parents=True, exist_ok=True)
    md_path = next(p for p in sorted((ROOT / "topic_reviews_md").glob(f"{prefix}-*.md")))
    topic, en_raw, it_raw = M.parse_md(md_path.read_text(encoding="utf-8"))
    en_clean, claims, _absent, _complete = M.extract_claims(en_raw)
    reviews = json.loads((PUB / "topic_reviews.json").read_text(encoding="utf-8"))
    questions = json.loads((PUB / "questions.json").read_text(encoding="utf-8"))
    entry = reviews[topic]
    pairs, itb = entry["pairs"], [b for _, b in RL.blocks(entry["it"])]
    stmt = {s["number"]: (c, s) for c in questions for s in c["statements"]}

    claimed = defaultdict(list)                     # EN hash -> [statement numbers]
    for num, h in (entry.get("claims") or {}).items():
        claimed[h].append(num)

    cands, n = [], 0
    for chain, b in RL.blocks(M.strip_markers(en_clean)):
        if not b.strip() or any(h.lower().startswith(SUMMARY) for h in chain):
            continue
        h = M._hash(b)
        j = pairs.get(h)
        twin = itb[j] if j is not None else None
        why = []
        if ";" in b or (twin and ";" in twin):
            why.append("semicolon")
        if len(LABEL_RE.findall(b)) >= 2:
            why.append("labels")
        if claimed.get(h) and twin and len(RL.sentences(twin)) >= 3:
            why.append(f"bundled ({len(RL.sentences(twin))} sentences, {len(claimed[h])} statements)")
        if not why:
            continue
        n += 1
        cands.append({"id": f"B{n:02d}", "hash": h, "chain": chain, "en": b, "it": twin,
                      "why": why, "stmts": sorted(claimed.get(h, []))})

    lines = [f"# Split candidates: {md_path.name}\n", f"Topic: {topic}\n",
             f"{len(cands)} candidate bullets. Read README.md first.\n"]
    for c in cands:
        lines.append(f"\n## {c['id']}  [{' > '.join(c['chain'])}]")
        lines.append(f"Flagged: {', '.join(c['why'])}")
        lines.append(f"\nEN: {c['en']}")
        lines.append(f"IT: {c['it'] if c['it'] else '(no Italian twin: English-only, not claimable)'}")
        if c["stmts"]:
            lines.append(f"\nStatements landing here ({len(c['stmts'])}):")
            for num in c["stmts"]:
                card, s = stmt[num]
                lines.append(f"  - {num} [{s['answer']}] {s['italian_text']}")
                lines.append(f"      EN: {s.get('english_translation','')}")
                if s.get("explanation"):
                    lines.append(f"      WHY: {s['explanation']}")
        else:
            lines.append("\nNo statement claims this bullet.")
    (outdir / "candidates.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (outdir / "README.md").write_text(RUBRIC, encoding="utf-8")
    json.dump({"topic": topic, "file": md_path.name,
               "candidates": [{k: c[k] for k in ("id", "hash", "why", "stmts")} for c in cands]},
              (outdir / "index.json").open("w", encoding="utf-8"), ensure_ascii=False, indent=1)
    flags = Counter(w.split(" ")[0] for c in cands for w in c["why"])
    print(f"{md_path.name}: {len(cands)} candidates -> {outdir}")
    print(f"  by signal: {dict(flags)}; statements involved: "
          f"{len({s for c in cands for s in c['stmts']})}")


if __name__ == "__main__":
    main(sys.argv[1:])
