#!/usr/bin/env python3
"""Build the verification packet for claiming one topic's statements.

A claim (`<!-- q: N -->` on a block of the English review, see
md_to_reviews.py) says which paragraph answers a statement. This script gives
a reader everything needed to decide every statement of ONE topic:

  OUT/blocks.md      every text block of the English review, numbered B001…
                     in document order with its heading chain, plus the
                     Italian twin (the reader decides on the Italian, since
                     the statements are Italian)
  OUT/statements.jsonl
                     one line per statement filed under the topic: number,
                     answer, Italian, English, explanation, the current
                     proposal (block id or null), and up to three alternative
                     block ids ranked by word overlap, so the common case is a
                     confirm rather than a search
  OUT/README.md      the rubric

The reader answers with decisions.json: { "24094": "B012", "24101": "absent",
… }. claims_apply.py writes those into the markdown.

Usage: python3 scripts/claims_packet.py 21 OUTDIR
       python3 scripts/claims_packet.py 22 OUTDIR --statements 24106 24042
       python3 scripts/claims_packet.py 03 OUTDIR --picture
The second form builds topic 22's blocks against statements filed under OTHER
topics, for claims that live away from the card's topic; claims_apply.py then
writes them into topic 22's file. Every packet also carries toc.md, the
headings of all 25 reviews, so a reader can tell when a subject lives
elsewhere.

The third form is the PICTURE-TOPIC packet (the `claims: rules` pass, see
CLAUDE.md). It adds cards.md, which lists for every card of the topic the
figure the review shows for it and the blocks that sit under that figure, and
README_picture.md, the addendum that lets a reader answer "figure" for a
statement the card's own picture already lands well. The figure is found the
way the app finds it (reviewImageFor): the card's own image, a byte-identical
twin from image_aliases.json, the base card's image, or any review figure
filed under the quesito number. The blocks under a figure are those between
its image line and the next image line or heading.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public_html"
sys.path.insert(0, str(ROOT / "scripts"))
import md_to_reviews as M          # noqa: E402
import review_landings as RL       # noqa: E402

RUBRIC = """# Claiming statements for a topic review

For each statement in statements.jsonl decide which block of blocks.md ANSWERS
it: the paragraph or bullet a learner should read to know why the statement is
true or false. Reply with decisions.json mapping every statement number to a
block id ("B012") or to "absent".

Rules.
1. Decide on the Italian. The statement is Italian and each block shows its
   Italian twin; the English is there to help you, not to match words.
2. For a VERO statement, the block that states the rule it asserts.
3. For a FALSO statement, the block that states the TRUE rule the statement
   distorts. A statement that swaps a figure (50 cm for 30 cm) is answered by
   the block giving the right figure. A statement that inverts a duty is
   answered by the block stating the duty.
4. "absent" ONLY when no block is about the statement's subject at all: the
   statement invents a duty, a ban or a permission the notes never discuss.
   If a block covers the subject but does not settle the statement, still
   choose that block, and add the number to `gaps` (below).
5. When two blocks both fit, prefer the one whose sentence names the rule
   directly over the one that mentions it in passing; prefer a bullet under
   the statement's own picture when the card has one.
5b. Prefer the block that STATES the rule over one that merely DENIES a
   confusion. Notes often carry a contrast line ("a traffic island is not a
   safety island, a median, or a parking area"). It is a memory aid that
   presupposes the definition, so a learner who lands there is told what the
   thing is not and never what it is. Land on the definition or the duty
   instead ("no vehicle may drive, stop, or park on it"). A contrast line is
   the right target only when it is the sole block covering the subject, or
   when the statement's own point IS the confusion between two named things
   and the notes define the other one nowhere.
6. The proposal is a machine guess. Confirm it only if it satisfies rules 2
   to 5; do not confirm it because it is plausible.
7. Every statement gets a decision. A claim may point at a block in THIS
   packet only. toc.md lists the section headings of every topic's review:
   when the rule that decides a statement belongs to another topic (a
   license category, a speed limit, a sign, a penalty), put the number in
   `elsewhere` with that topic's number, and still give the best block here
   if one covers the subject, or "absent" if none does. A second packet is
   then built against that topic's blocks for exactly those statements.

Output, as JSON:
{
  "decisions": { "24094": "B012", "24101": "absent", ... },
  "gaps":      { "24107": "block B040 never says the trailer's mass is irrelevant", ... },
  "elsewhere": { "24106": "22", ... },
  "split":     [ "B010: three unrelated rules in one bullet", ... ]
}
`gaps` lists statements whose chosen block covers the subject but does not
actually decide them (the notes need a sentence). `split` lists blocks that
should be broken up because they bundle unrelated rules.
"""


PICTURE_RUBRIC = """# Picture-topic addendum to README.md (read README.md first)

This topic is a PICTURE topic: every card shows a sign, and the app already
opens the review at that sign's figure when the learner presses 📖. So the
decision for each statement has THREE possible values:

- `"figure"`: the statement is about the pictured sign itself, what it looks
  like, what it warns of, what it means, or what the sign's own figure blocks
  (listed per card in cards.md) already say. A FALSO statement that
  misdescribes the sign ("this sign warns of a level crossing", when it is a
  bend) is `"figure"` too. This is the DEFAULT for a picture topic; most
  statements are `"figure"`.
- a block id (`"B012"`): the statement tests a RULE that the figure blocks do
  NOT state and that another block does: for instance the distance at which
  signs are placed, how a supplementary panel is read, what the whole family
  may never do (forbid, order, assign priority), or a driving rule taught in
  a general block elsewhere in the review. Claim it ONLY when that other
  block decides the statement better than the figure would.
- `"absent"`: the statement invents a rule that no block discusses AND the
  figure blocks do not cover it either. Rare here; prefer `"figure"` when the
  sign's own blocks cover the subject.

A card whose figure blocks are "(none in the review)" has NO figure to land
on, so for its statements `"figure"` is not available: choose a block or
`"absent"`, and report a gap when the sign itself is untaught.

Variant cards (ids 5004 and up, image `NNNN_MMMMM.jpeg`) show the base sign
with a supplementary panel; treat them like their base card (same id prefix).

Report `gaps` only for a claimed block, as README.md describes; do not report
gaps for `"figure"` statements. Do not report `split`.
"""


def image_lines(en_md):
    """(line_no, [image paths]) for every image line of the English review."""
    out = []
    for i, raw in enumerate(en_md.replace("\r\n", "\n").split("\n")):
        line = raw.rstrip()
        if M.BLOCK_IMG_RE.match(line):
            out.append((i, re.findall(r"\]\(([^)]+)\)", line)))
    return out


def figure_blocks(en_md, blocks):
    """{image path: [block ids]} : the blocks between an image line and the
    next image line or heading, which is what a reader sees under the sign."""
    lines = en_md.replace("\r\n", "\n").split("\n")
    imgs = image_lines(en_md)
    out = {}
    for k, (start, paths) in enumerate(imgs):
        # Consecutive image lines (only blank lines between them) stack one
        # figure over another with the text under the last; the text serves
        # them all, so the group shares its blocks.
        end = len(lines)
        for j in range(start + 1, len(lines)):
            line = lines[j].rstrip()
            if not line.strip():
                continue
            if M.BLOCK_IMG_RE.match(line):
                continue
            if M.BLOCK_HEAD_RE.match(line):
                end = j
                break
            # first text line: the group's blocks run to the next image or heading
            for jj in range(j, len(lines)):
                l2 = lines[jj].rstrip()
                if M.BLOCK_HEAD_RE.match(l2) or M.BLOCK_IMG_RE.match(l2):
                    end = jj
                    break
            break
        ids = [b["id"] for b in blocks if start < b["first"] < end]
        for p in paths:
            out.setdefault(p, []).extend(ids)
    return out


def review_image_for(card, cards_by_id, has_image, aliases):
    """Mirror of reviewImageFor in app.js: the figure the review shows for a
    card, or None."""
    img = card.get("image")
    if not img:
        return None
    if has_image(img):
        return img
    for twin in aliases.get(img, []):
        if has_image(twin):
            return twin
    base = card.get("base_id", card["id"])
    base_card = cards_by_id.get(base)
    if base_card is not None and base_card is not card and base_card.get("image") and has_image(base_card["image"]):
        return base_card["image"]
    for p in has_image.paths:
        if re.match(r"domandeb_images/%d[._]" % base, p):
            return p
    if base_card is not None and base_card.get("image"):
        for twin in aliases.get(base_card["image"], []):
            if has_image(twin):
                return twin
    return None


def write_cards(outdir, topic, en_clean, blocks, questions):
    aliases = {}
    for group in json.loads((PUB / "image_aliases.json").read_text(encoding="utf-8")):
        for p in group:
            aliases[p] = [q for q in group if q != p]
    figs = figure_blocks(en_clean, blocks)
    paths = set(figs)
    def has_image(p):
        return p in paths
    has_image.paths = sorted(paths)
    cards = [c for c in questions if c["topic"] == topic]
    by_id = {c["id"]: c for c in questions if not c.get("variant")}
    lines = ["# Cards of this topic: the picture each shows, and the review blocks that sit under that picture\n",
             "A statement whose subject is the pictured sign itself, or its meaning as the figure blocks state it, is answered \"figure\".\n"]
    n_none = 0
    for c in cards:
        live = [s for s in c["statements"] if not s.get("retired")]
        if not live:
            continue
        fig = review_image_for(c, by_id, has_image, aliases)
        ids = figs.get(fig, []) if fig else []
        if not c.get("image"):
            shown = "no picture on the card"
        elif fig and ids:
            shown = " ".join(ids)
        else:
            shown = "(none in the review)"
            n_none += 1
        lines.append(f"- card {c['id']}: image {c.get('image') or '(none)'}, {len(live)} statements, figure blocks: {shown}")
    (outdir / "cards.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (outdir / "README_picture.md").write_text(PICTURE_RUBRIC, encoding="utf-8")
    return len(cards), n_none


def block_line_ranges(en_md):
    """Blocks in document order with (first_line, last_line) into en_md's
    lines, mirroring _text_blocks so the ids line up with review_landings."""
    lines = en_md.replace("\r\n", "\n").split("\n")
    out, para = [], []
    def flush():
        if para:
            out.append((" ".join(t for _, t in para), para[0][0], para[-1][0]))
            para.clear()
    for i, raw in enumerate(lines):
        line = raw.rstrip()
        if M.BLOCK_HEAD_RE.match(line) or not line.strip() or M.BLOCK_IMG_RE.match(line):
            flush(); continue
        m = M.BLOCK_ITEM_RE.match(line)
        if m:
            flush(); out.append((m.group(1).strip(), i, i)); continue
        if line.startswith(">"):
            flush()
            rest = line[1:].strip()
            if rest:
                out.append((rest, i, i))
            continue
        para.append((i, line.strip()))
    flush()
    return out


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    prefix, outdir = argv[0], Path(argv[1])
    picture = "--picture" in argv
    if picture:
        argv = [a for a in argv if a != "--picture"]
    only = set(argv[argv.index("--statements") + 1:]) if "--statements" in argv else None
    outdir.mkdir(parents=True, exist_ok=True)
    md_path = next(p for p in sorted((ROOT / "topic_reviews_md").glob(f"{prefix}-*.md")))
    txt = md_path.read_text(encoding="utf-8")
    topic, en_raw, it_raw = M.parse_md(txt)
    en_clean, claims, absent, complete = M.extract_claims(en_raw)
    reviews = json.loads((PUB / "topic_reviews.json").read_text(encoding="utf-8"))
    questions = json.loads((PUB / "questions.json").read_text(encoding="utf-8"))
    anchors = json.loads((PUB / "review_anchors.json").read_text(encoding="utf-8"))
    R = RL.Reviews(reviews)
    pairs = reviews[topic]["pairs"]
    itb = [b for _, b in RL.blocks(reviews[topic]["it"])]

    # Blocks, numbered in the order review_landings sees them.
    blocks = []
    for (chain, b), (b2, first, last) in zip(RL.blocks(M.strip_markers(en_clean)), block_line_ranges(en_clean)):
        assert b == b2 or M.EN_ONLY_RE.sub("", b2).strip() == b, (b[:40], b2[:40])
        h = M._hash(b)
        j = pairs.get(h)
        blocks.append({"id": f"B{len(blocks)+1:03d}", "hash": h, "chain": chain, "en": b,
                       "it": itb[j] if j is not None else None, "line": last, "first": first})
    by_hash = {b["hash"]: b for b in blocks}
    lines = ["# Blocks of the English review, with Italian twins\n",
             f"Topic: {topic}\n",
             "A block with no Italian twin (English-only scaffolding) cannot be claimed.\n"]
    for b in blocks:
        lines.append(f"\n## {b['id']}  [{' > '.join(b['chain'])}]")
        lines.append(f"EN: {b['en']}")
        lines.append(f"IT: {b['it'] if b['it'] else '(none: English-only, not claimable)'}")
    (outdir / "blocks.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Current landings and ranked alternatives per statement.
    _, rows = RL.landings(reviews, questions, anchors)
    current = {r["number"]: r for r in rows}
    it_tokens = {b["id"]: RL.pick_tokens(b["it"]) for b in blocks if b["it"]}
    n_out = 0
    with (outdir / "statements.jsonl").open("w", encoding="utf-8") as f:
        for c in questions:
            if only is None and c["topic"] != topic:
                continue
            for s in c["statements"]:
                if only is not None and s["number"] not in only:
                    continue
                if s.get("retired"):
                    # The Ministry withdrew it, so no learner meets it and a
                    # claim on it is a promise nobody can collect.
                    # validate_data.py rejects such a claim outright.
                    continue
                r = current.get(s["number"])
                proposal = None
                if r and r["block"] and r["topic"] == topic:
                    proposal = by_hash.get(r["block"]["en"], {}).get("id")
                st = RL.pick_tokens(s["italian_text"])
                ranked = sorted(((len(st & tk), bid) for bid, tk in it_tokens.items()), reverse=True)
                alts = [bid for n, bid in ranked[:4] if n >= 2 and bid != proposal][:3]
                f.write(json.dumps({
                    "number": s["number"], "card": c["id"], "image": bool(c.get("image")),
                    "answer": s["answer"], "italian": s["italian_text"],
                    "english": s.get("english_translation", ""),
                    "explanation": s.get("explanation", ""),
                    "proposal": proposal, "alternatives": alts,
                }, ensure_ascii=False) + "\n")
                n_out += 1
    (outdir / "README.md").write_text(RUBRIC, encoding="utf-8")
    # Table of contents of every review, so a reader can recognize a subject
    # that is filed under another topic.
    toc = ["# Every topic's sections (for the `elsewhere` decision)\n"]
    for p in sorted((ROOT / "topic_reviews_md").glob("*.md")):
        if not p.name[:2].isdigit():
            continue
        t_txt = p.read_text(encoding="utf-8")
        t_topic, t_en, _ = M.parse_md(t_txt)
        t_en = M.extract_claims(t_en)[0]
        toc.append(f"\n## Topic {p.name[:2]}: {t_topic}")
        for lvl, head, _lines in M._sections(t_en):
            if lvl:
                toc.append(("  " * (lvl - 2)) + "- " + M.EN_ONLY_RE.sub("", head).strip())
    (outdir / "toc.md").write_text("\n".join(toc) + "\n", encoding="utf-8")
    json.dump({"topic": topic, "file": md_path.name,
               "blocks": {b["id"]: {"hash": b["hash"], "line": b["line"]} for b in blocks}},
              (outdir / "index.json").open("w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if picture:
        n_cards, n_none = write_cards(outdir, topic, en_clean, blocks, questions)
        print(f"  picture packet: {n_cards} cards in cards.md, {n_none} with no figure in the review")
    print(f"{md_path.name}: {len(blocks)} blocks, {n_out} statements -> {outdir}")
    print(f"  already claimed: {sum(len(v) for v in claims.values())}, absent: {len(absent)}, complete: {complete}")


if __name__ == "__main__":
    main(sys.argv[1:])
