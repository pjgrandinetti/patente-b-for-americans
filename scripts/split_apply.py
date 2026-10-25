#!/usr/bin/env python3
"""Apply a reader's split decisions to a topic review, moving the claims.

Reads OUT/index.json (from split_candidates.py) and OUT/decisions.json (from
the reader) and rewrites `topic_reviews_md/NN-*.md`: each SPLIT block's English
line is replaced by the reader's new English bullets and its Italian twin by
the matching Italian ones, with every claim that pointed at the old block
redistributed to the bullet that now answers it.

The claim redistribution is the point. A plain split would leave every claim on
the first fragment (md_to_reviews keeps the marker where it finds it), which is
how topic 13 ended up needing a full re-read. Here the reader has already said
which statement belongs to which fragment, so the markers are rewritten from
that and no second pass is needed.

Guards, because this edits the source of the notes:
  * a block must be a SINGLE line in the markdown (every paragraph and bullet
    in these files is written on one line); anything else aborts
  * the English and Italian replacements must have the same number of bullets
  * every claim on the old block must be assigned exactly once, and no
    statement may be introduced that was not claimed there
  * nothing is written unless every decision passes

Usage: python3 scripts/split_apply.py OUTDIR [--dry-run]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public_html"
sys.path.insert(0, str(ROOT / "scripts"))
import md_to_reviews as M          # noqa: E402
import review_landings as RL       # noqa: E402

Q_RE = re.compile(r"\s*<!--\s*q:\s*([0-9\s]+?)\s*-->")


def strip_q(line):
    return Q_RE.sub("", line).rstrip()


def main(argv):
    if not argv:
        sys.exit(__doc__)
    out = Path(argv[0])
    dry = "--dry-run" in argv
    index = json.loads((out / "index.json").read_text(encoding="utf-8"))
    decisions = json.loads((out / "decisions.json").read_text(encoding="utf-8"))["decisions"]
    md_path = ROOT / "topic_reviews_md" / index["file"]
    topic = index["topic"]
    by_id = {c["id"]: c for c in index["candidates"]}

    reviews = json.loads((PUB / "topic_reviews.json").read_text(encoding="utf-8"))
    entry = reviews[topic]
    pairs, itb = entry["pairs"], [b for _, b in RL.blocks(entry["it"])]

    text = md_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    # Where the Italian half starts, so an English hash never matches an
    # Italian line and vice versa.
    it_start = next(i for i, l in enumerate(lines) if l.strip() == "<!-- LANG: it -->")

    edits = []          # (line_index, [replacement lines])
    kept = splits = 0
    for d in decisions:
        cand = by_id.get(d["block"])
        if not cand:
            sys.exit(f"decision names unknown block {d['block']!r}")
        if d.get("action") != "split":
            kept += 1
            continue
        splits += 1
        bullets = d.get("bullets") or []
        if len(bullets) < 2:
            sys.exit(f"{d['block']}: a split needs at least two bullets")
        claimed = set(cand["stmts"])
        assigned = [n for b in bullets for n in (b.get("stmts") or [])]
        if len(assigned) != len(set(assigned)):
            sys.exit(f"{d['block']}: a statement is assigned twice")
        if set(assigned) != claimed:
            sys.exit(f"{d['block']}: assigned {sorted(set(assigned))} but the block "
                     f"claims {sorted(claimed)}")

        # Locate the English line by hash, and the Italian twin by exact text.
        h = cand["hash"]
        en_idx = [i for i, l in enumerate(lines[:it_start])
                  if l.strip() and M._hash(M.BLOCK_ITEM_RE.match(strip_q(l)).group(1).strip()
                                           if M.BLOCK_ITEM_RE.match(strip_q(l))
                                           else strip_q(l).strip()) == h]
        if len(en_idx) != 1:
            sys.exit(f"{d['block']}: found {len(en_idx)} English lines for hash {h}, need exactly 1")
        j = pairs.get(h)
        twin = itb[j] if j is not None else None
        if twin is None:
            sys.exit(f"{d['block']}: no Italian twin, cannot split")
        it_idx = [i for i, l in enumerate(lines[it_start:], start=it_start)
                  if l.strip() and (M.BLOCK_ITEM_RE.match(l).group(1).strip()
                                    if M.BLOCK_ITEM_RE.match(l) else l.strip()) == twin]
        if len(it_idx) != 1:
            sys.exit(f"{d['block']}: found {len(it_idx)} Italian lines for the twin, need exactly 1")

        en_new, it_new = [], []
        for b in bullets:
            en, it = b.get("en", "").rstrip(), b.get("it", "").rstrip()
            if not en or not it:
                sys.exit(f"{d['block']}: a bullet is missing en or it")
            if ";" in en or ";" in it:
                sys.exit(f"{d['block']}: a replacement bullet still contains a semicolon")
            nums = b.get("stmts") or []
            en_new.append(en + (f"  <!-- q: {' '.join(nums)} -->" if nums else ""))
            it_new.append(it)
        edits.append((en_idx[0], en_new))
        edits.append((it_idx[0], it_new))

    for i, repl in sorted(edits, key=lambda e: -e[0]):
        lines[i:i + 1] = repl
    print(f"{md_path.name}: {splits} split, {kept} kept, {len(edits)//2} blocks rewritten")
    if dry:
        print("(dry run, nothing written)")
        return
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print("written; now run md_to_reviews.py and validate_data.py")


if __name__ == "__main__":
    main(sys.argv[1:])
