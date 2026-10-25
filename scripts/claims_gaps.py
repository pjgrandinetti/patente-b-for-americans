#!/usr/bin/env python3
"""Build the gap-filling packet for a claimed topic.

A `gap` (from claims_packet.py readers) is a statement whose claimed block
covers the subject but never states the deciding fact. This packet groups the
gaps by the block they sit on TODAY (claims move with the paragraph, so the
block ids in old decision files may be stale) and asks a reader for one
addition per block, in both languages.

  OUT/blocks.md   the topic's current blocks, numbered, with Italian twins
  OUT/gaps.jsonl  one line per gap: number, answer, italian, english,
                  explanation, block (current id), note (the reader's gap note)
  OUT/README.md   the writing rules

The reader answers with additions.json:
  {"additions": [{"block": "B027", "en": "<sentence(s)>", "it": "<same, in Italian>",
                  "covers": ["18357", "18363"]}, ...]}
claims_fill.py appends each addition to its block in both languages.

Usage: python3 scripts/claims_gaps.py 16 GAPS.json [GAPS2.json ...] OUTDIR
  where each GAPS.json is a decisions file carrying a "gaps" object.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public_html"
sys.path.insert(0, str(ROOT / "scripts"))
import md_to_reviews as M          # noqa: E402
import review_landings as RL       # noqa: E402
from claims_packet import block_line_ranges  # noqa: E402

RULES = """# Filling the gaps in a topic review

Each line of gaps.jsonl is an exam statement whose claimed block (blocks.md)
covers its subject but never states the fact that decides it. Write, for each
block that has gaps, ONE addition that closes all of that block's gaps: a
sentence or two in English and the same sentences in Italian.

Rules for the text.
1. State the rule positively, as fact. Never mention the exam, statements,
   traps, or that something "is false": the notes teach the rule, the
   post-answer explanation names the trap.
2. Derive the rule from the statements' answers and explanations. A VERO
   statement asserts the rule; a FALSO statement inverts or distorts it, so
   the rule is the correct version. Do not add anything the bank does not
   establish.
3. Complete sentences only. No semicolons, no em dashes, no parentheses for
   essential content, no verbless fragments. American English.
4. Keep the addition short: it must read as part of the block, not as a
   second paragraph. If a block's gaps are several unrelated rules, you may
   return more than one addition for that block; each becomes its own
   sentence group appended in order.
5. English and Italian must have the SAME number of sentences, sentence for
   sentence, since the notes are paired sentence by sentence.
6. Bold the key term or figure the way the surrounding text does (**110
   km/h**), sparingly.
7. `covers` lists every gap statement the addition settles. A gap you cannot
   settle from the bank goes in `unresolved` with a reason.

Output, as JSON:
{"additions": [{"block": "B027", "en": "...", "it": "...", "covers": ["18357", "18363"]}, ...],
 "unresolved": {"18365": "<why>", ...}}
"""


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    prefix, outdir = argv[0], Path(argv[-1])
    gap_files = argv[1:-1]
    outdir.mkdir(parents=True, exist_ok=True)
    md_path = next(p for p in sorted((ROOT / "topic_reviews_md").glob(f"{prefix}-*.md")))
    topic, en_raw, it_raw = M.parse_md(md_path.read_text(encoding="utf-8"))
    en_clean, claims, absent, complete = M.extract_claims(en_raw)
    reviews = json.loads((PUB / "topic_reviews.json").read_text(encoding="utf-8"))
    questions = json.loads((PUB / "questions.json").read_text(encoding="utf-8"))
    pairs = reviews[topic]["pairs"]
    itb = [b for _, b in RL.blocks(reviews[topic]["it"])]
    blocks, by_hash = [], {}
    for (chain, b), (_b2, _first, last) in zip(RL.blocks(M.strip_markers(en_clean)), block_line_ranges(en_clean)):
        h = M._hash(b)
        j = pairs.get(h)
        blocks.append({"id": f"B{len(blocks)+1:03d}", "hash": h, "chain": chain, "en": b,
                       "it": itb[j] if j is not None else None, "line": last})
        by_hash[h] = blocks[-1]
    lines = [f"# Blocks of the review (topic {prefix}), with Italian twins\n"]
    for b in blocks:
        lines.append(f"\n## {b['id']}  [{' > '.join(b['chain'])}]\nEN: {b['en']}\nIT: {b['it'] or '(none)'}")
    (outdir / "blocks.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    claim_hash = {n: h for h, nums in claims.items() for n in nums}
    stmt = {s["number"]: (c, s) for c in questions for s in c["statements"]}
    notes = {}
    for gf in gap_files:
        d = json.loads(Path(gf).read_text(encoding="utf-8"))
        for n, note in (d.get("gaps") or {}).items():
            notes.setdefault(n, note)
    n_out, skipped = 0, []
    with (outdir / "gaps.jsonl").open("w", encoding="utf-8") as f:
        for n, note in sorted(notes.items()):
            h = claim_hash.get(n)
            if h is None or h not in by_hash or n not in stmt:
                skipped.append(n); continue      # claimed elsewhere now, or moved
            c, s = stmt[n]
            f.write(json.dumps({"number": n, "answer": s["answer"], "italian": s["italian_text"],
                                "english": s.get("english_translation", ""),
                                "explanation": s.get("explanation", ""),
                                "block": by_hash[h]["id"], "note": note}, ensure_ascii=False) + "\n")
            n_out += 1
    (outdir / "README.md").write_text(RULES, encoding="utf-8")
    json.dump({"topic": topic, "file": md_path.name,
               "blocks": {b["id"]: {"hash": b["hash"], "line": b["line"]} for b in blocks}},
              (outdir / "index.json").open("w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{md_path.name}: {n_out} gaps on current blocks -> {outdir}"
          + (f" (skipped {len(skipped)} now claimed elsewhere: {' '.join(skipped[:8])})" if skipped else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
