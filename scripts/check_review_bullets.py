#!/usr/bin/env python3
"""Grab-bag bullets in the topic reviews: report, and fail on a regression.

House rule (glossary 40): a review bullet teaches ONE rule. A bullet that
welds several rules together forces the learner to work out which sentence
answers the statement, and it defeats the 📖 landing, which can only scroll to
the block, not to the idea inside it.

"Grab bag" is a judgment a regex cannot make, and the attempt to score it
(sentence count, bold count, length) mostly finds blocks that are long but
coherent: one subject explained properly. So this script checks only the two
signals that ARE mechanical, and leaves the rest to the claim readers, who
report `split` for exactly this reason:

  semicolon   A semicolon in this house style is two ideas welded into one
              sentence. The style bans it outright, so every hit is a defect.
  labels      Two or more bold runs that OPEN a sentence inside one block, as
              in "**No parking** … **No stopping** …": each label announces a
              subject, so two labels are usually two bullets. Summary sections
              are exempt, since a summary is meant to gather.

Neither number may grow. Both are ratcheted against
docs/review-bullet-baseline.json: the script fails if a count rises above the
recorded figure, and prints the command to lower the baseline once a cleanup
pass has brought it down. That stops new grab bags today without demanding the
whole backlog be cleared first.

Usage: python3 scripts/check_review_bullets.py [--list [semicolon|labels]]
       python3 scripts/check_review_bullets.py --save-baseline
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import md_to_reviews as M          # noqa: E402
import review_landings as RL       # noqa: E402

BASELINE = ROOT / "docs" / "review-bullet-baseline.json"
# A bold run that opens a sentence: start of block, or after . ! ? or a colon.
LABEL_RE = re.compile(r"(?:^|(?<=[.!?:])\s+)\*\*([^*]{3,40}?)\*\*")
SUMMARY = ("summary of key points", "riepilogo dei punti chiave")


def blocks_by_lang():
    """(topic file, lang, heading chain, block text) for every review block."""
    for f in sorted((ROOT / "topic_reviews_md").glob("[0-9]*.md")):
        txt = f.read_text(encoding="utf-8")
        _topic, en, it = M.parse_md(txt)
        en = M.extract_claims(en)[0]
        for lang, half in (("en", en), ("it", it)):
            for chain, b in RL.blocks(M.strip_markers(half)):
                if b.strip():
                    yield f.name, lang, chain, b


def findings():
    semis, labels = [], []
    for name, lang, chain, b in blocks_by_lang():
        where = f"{name[:2]} [{lang}] {' > '.join(chain)[:44]}"
        if ";" in b:
            semis.append((where, b))
        if any(h.lower().startswith(SUMMARY) for h in chain):
            continue                      # a summary is allowed to gather
        if len(LABEL_RE.findall(b)) >= 2:
            labels.append((where, b))
    return {"semicolon": semis, "labels": labels}


def main(argv):
    found = findings()
    counts = {k: len(v) for k, v in found.items()}

    if "--save-baseline" in argv:
        BASELINE.write_text(json.dumps(counts, indent=1) + "\n", encoding="utf-8")
        print(f"baseline written: {counts}")
        return 0

    if "--list" in argv:
        which = argv[argv.index("--list") + 1] if len(argv) > argv.index("--list") + 1 else None
        for key in ([which] if which in found else found):
            print(f"\n===== {key}: {counts[key]}")
            for where, b in found[key]:
                print(f"  {where}\n    {b[:150]}")
        return 0

    base = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else {}
    bad = False
    for key, n in sorted(counts.items()):
        was = base.get(key)
        if was is None:
            print(f"? {key}: {n} (no baseline recorded; run --save-baseline)")
        elif n > was:
            print(f"✗ {key}: {n}, up from {was}. A new grab-bag bullet went in. "
                  f"See it with: python3 scripts/check_review_bullets.py --list {key}")
            bad = True
        elif n < was:
            print(f"✓ {key}: {n}, down from {was}. Lower the baseline: "
                  f"python3 scripts/check_review_bullets.py --save-baseline")
        else:
            print(f"✓ {key}: {n}, unchanged")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
