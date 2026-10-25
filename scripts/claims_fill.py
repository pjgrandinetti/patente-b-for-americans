#!/usr/bin/env python3
"""Write gap additions (from claims_gaps.py readers) into a topic review.

Each addition is appended to its block in both languages, OR becomes a new
block of its own right after it. A new block is used when the addition has
two or more sentences, or when the block already received one, so that a
paragraph does not swell into a dozen sentences and each rule keeps its own
landing. When a new block is made, the statements the addition `covers` are
re-claimed by it (their `<!-- q -->` numbers move from the original block).

Usage: python3 scripts/claims_fill.py PACKET [additions.json ...]
  PACKET is the folder claims_gaps.py wrote (index.json). Additions default
  to every additions*.json in it.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import md_to_reviews as M          # noqa: E402
import review_landings as RL       # noqa: E402


def main(argv):
    if not argv:
        sys.exit(__doc__)
    packet = Path(argv[0])
    files = [Path(a) for a in argv[1:]] or sorted(packet.glob("additions*.json"))
    index = json.loads((packet / "index.json").read_text(encoding="utf-8"))
    adds = []
    for f in files:
        adds += json.loads(f.read_text(encoding="utf-8")).get("additions", [])
    path = ROOT / "topic_reviews_md" / index["file"]
    txt = path.read_text(encoding="utf-8")
    en_m, it_m = M.EN_RE.search(txt), M.IT_RE.search(txt)
    head, en_sec, it_sec = txt[:en_m.end()], txt[en_m.end():it_m.start()], txt[it_m.start():]
    en_lines = en_sec.split("\n")
    it_lines = it_sec.split("\n")

    # Locate each block's EN line by hash (the packet's line numbers count from
    # the stripped section; we re-derive here to be robust to markers) and its
    # IT twin line by matching the twin's text.
    reviews = json.loads((ROOT / "public_html" / "topic_reviews.json").read_text(encoding="utf-8"))
    topic = index["topic"]
    pairs = reviews[topic]["pairs"]
    itb = [b for _, b in RL.blocks(reviews[topic]["it"])]

    def line_of(lines, text):
        want = text.strip()
        hits = [i for i, l in enumerate(lines)
                if M.EN_ONLY_RE.sub("", M.Q_RE.sub("", l)).strip().lstrip("- ").strip() == want.lstrip("- ").strip()
                or M.Q_RE.sub("", l).strip() == want]
        if len(hits) != 1:
            # a paragraph spanning several lines: match its LAST line
            hits = [i for i, l in enumerate(lines) if want.endswith(M.Q_RE.sub("", l).strip()) and l.strip()]
        if len(hits) != 1:
            sys.exit(f"cannot locate block line for: {want[:60]!r} ({len(hits)} hits)")
        return hits[0]

    # hash -> EN source text, from the shipped review (same text as the file).
    en_text = {M._hash(b): b for _, b in RL.blocks(reviews[topic]["en"])}

    per_block = {}
    for a in adds:
        per_block.setdefault(a["block"], []).append(a)
    # Process in reverse document order so inserted lines do not shift the
    # lines still to be edited.
    order = sorted(per_block, key=lambda bid: index["blocks"][bid]["line"], reverse=True)
    n_append = n_new = 0
    for bid in order:
        h = index["blocks"][bid]["hash"]
        en_src = en_text[h]
        it_src = itb[pairs[h]]
        ei = line_of(en_lines, en_src)
        ii = line_of(it_lines, it_src)
        bullet = en_lines[ei].lstrip().startswith("- ")
        bullet_it = it_lines[ii].lstrip().startswith("- ")
        first = True
        new_en, new_it = [], []
        for a in per_block[bid]:
            en_add, it_add = a["en"].strip(), a["it"].strip()
            standalone = len(RL.sentences(en_add)) >= 2 or not first
            if not standalone:
                # append to the block's last line, keeping its claim marker last
                m = M.Q_RE.search(en_lines[ei])
                marker = m.group(0) if m else ""
                base = M.Q_RE.sub("", en_lines[ei]).rstrip()
                en_lines[ei] = base + " " + en_add + marker
                it_lines[ii] = it_lines[ii].rstrip() + " " + it_add
                n_append += 1
            else:
                covers = [str(n) for n in a.get("covers", [])]
                # move the covered claims from the original block to the new one
                m = M.Q_RE.search(en_lines[ei])
                if m:
                    keep = [n for n in M._nums(m.group(1)) if n not in covers]
                    en_lines[ei] = M.Q_RE.sub("", en_lines[ei]).rstrip() + (" <!-- q: " + " ".join(keep) + " -->" if keep else "")
                mark = (" <!-- q: " + " ".join(covers) + " -->") if covers else ""
                new_en.append(("- " if bullet else "") + en_add + mark)
                new_it.append(("- " if bullet_it else "") + it_add)
                n_new += 1
            first = False
        if new_en:
            ins_en = []
            ins_it = []
            for k, l in enumerate(new_en):
                if not bullet:
                    ins_en.append("")
                ins_en.append(l)
            for k, l in enumerate(new_it):
                if not bullet_it:
                    ins_it.append("")
                ins_it.append(l)
            en_lines[ei + 1:ei + 1] = ins_en
            it_lines[ii + 1:ii + 1] = ins_it
    path.write_text(head + "\n".join(en_lines) + "\n".join(it_lines), encoding="utf-8")
    print(f"{path.name}: {n_append} additions appended, {n_new} new blocks")


if __name__ == "__main__":
    main(sys.argv[1:])
