#!/usr/bin/env python3
"""Write claim decisions into a topic review's markdown.

Reads PACKET/index.json (from claims_packet.py) and PACKET/decisions.json
({ "24094": "B012", "24101": "absent", ... }) and appends `<!-- q: … -->` to
the claiming block's last line, merging with any marker already there. Absent
statements go into one `<!-- absent: … -->` line under the English LANG
marker. With --complete, adds `<!-- claims: complete -->` as well; with
--rules, the picture-topic marker `<!-- claims: rules -->` (see md_to_reviews.py).

Then run scripts/md_to_reviews.py and scripts/validate_data.py: the build is
what checks that every block has an Italian twin, that no statement is
claimed twice, and (for a complete topic) that nothing is left unplaced.

Usage: python3 scripts/claims_apply.py PACKET [--complete | --rules]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import md_to_reviews as M  # noqa: E402


def main(argv):
    if not argv:
        sys.exit(__doc__)
    packet = Path(argv[0])
    complete = "--complete" in argv
    rules = "--rules" in argv
    index = json.loads((packet / "index.json").read_text(encoding="utf-8"))
    decisions = json.loads((packet / "decisions.json").read_text(encoding="utf-8"))
    if "decisions" in decisions:
        decisions = decisions["decisions"]
    path = ROOT / "topic_reviews_md" / index["file"]
    txt = path.read_text(encoding="utf-8")
    en_m, it_m = M.EN_RE.search(txt), M.IT_RE.search(txt)
    head, section, tail = txt[:en_m.end()], txt[en_m.end():it_m.start()], txt[it_m.start():]
    # parse_md strips the newlines around the English section, and the packet's
    # line numbers count from that stripped text; keep the same basis here and
    # put the surrounding newlines back on the way out.
    en = section.strip("\n")
    lead = section[:len(section) - len(section.lstrip("\n"))]
    trail = section[len(section.rstrip("\n")):]

    # Strip existing claim/absent/complete markers, then rebuild them from the
    # union of old claims and new decisions (a decision wins over an old claim).
    en_clean, old_claims, old_absent, old_complete = M.extract_claims(en)
    old_by_num = {n: h for h, nums in old_claims.items() for n in nums}
    hash_of = {bid: v["hash"] for bid, v in index["blocks"].items()}
    line_of = {v["hash"]: v["line"] for v in index["blocks"].values()}
    want = {}          # hash -> [nums]
    absent = set(old_absent)
    for n, h in old_by_num.items():
        want.setdefault(h, []).append(n)
    bad = []
    for n, d in decisions.items():
        n = str(n)
        for h, nums in want.items():
            if n in nums:
                nums.remove(n)
        absent.discard(n)
        if d == "absent":
            absent.add(n)
        elif d == "figure":
            # Picture topics: the statement identifies the pictured sign and
            # lands on the card's image; it is released from any claim.
            pass
        elif d in hash_of:
            want.setdefault(hash_of[d], []).append(n)
        else:
            bad.append((n, d))
    if bad:
        sys.exit(f"unknown block ids in decisions: {bad[:10]}")

    lines = en_clean.split("\n")
    # The packet's line numbers refer to the clean English exactly as
    # extract_claims returns it, so they index `lines` directly.
    for h, nums in want.items():
        if not nums:
            continue
        if h not in line_of:
            sys.exit(f"claim for {nums} points at a block not in the packet (review edited since? rebuild the packet)")
        i = line_of[h]
        lines[i] = lines[i].rstrip() + " <!-- q: " + " ".join(sorted(set(nums), key=int)) + " -->"
    marker_lines = []
    if complete or (old_complete == "complete" and not rules):
        marker_lines.append("<!-- claims: complete -->")
    elif rules or old_complete == "rules":
        marker_lines.append("<!-- claims: rules -->")
    if absent:
        marker_lines.append("<!-- absent: " + " ".join(sorted(absent, key=int)) + " -->")
    out = "\n".join(marker_lines + lines)
    path.write_text(head + lead + out + trail + tail, encoding="utf-8")

    # A claim MOVES: a statement decided here is released from any other
    # topic's file, or the build would report it claimed twice.
    moved = {str(n) for n in decisions}
    for other in sorted((ROOT / "topic_reviews_md").glob("*.md")):
        if other == path or not other.name[:2].isdigit():
            continue
        o_txt = other.read_text(encoding="utf-8")
        def drop(m):
            keep = [n for n in M._nums(m.group(1)) if n not in moved]
            return (" <!-- q: " + " ".join(keep) + " -->") if keep else ""
        new_txt = M.Q_RE.sub(drop, o_txt)
        def drop_absent(m):
            keep = [n for n in M._nums(m.group(1)) if n not in moved]
            return ("<!-- absent: " + " ".join(keep) + " -->\n") if keep else ""
        new_txt = re.sub(r"^\s*<!--\s*absent:\s*([0-9][0-9\s,]*)-->\s*\n", drop_absent, new_txt, flags=re.M)
        if new_txt != o_txt:
            other.write_text(new_txt, encoding="utf-8")
            print(f"  released moved claims from {other.name}")
    n_claims = sum(len(v) for v in want.values())
    print(f"{path.name}: {n_claims} claims on {sum(1 for v in want.values() if v)} blocks, "
          f"{len(absent)} absent{', marked complete' if complete or old_complete else ''}")


if __name__ == "__main__":
    main(sys.argv[1:])
