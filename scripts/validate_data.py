#!/usr/bin/env python3
"""
Data-integrity checks for the Patente B app, run in CI (and locally).

Verifies the shipped data files are internally consistent and that the two
version markers stay in lockstep. Exits non-zero with a list of problems.

Run:  python3 scripts/validate_data.py
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB  = ROOT / "public_html"
errors = []
US_IT_RE = re.compile(r"Stati Uniti|\bUSA\b|[Aa]meric|statunitens|California|\bU\.S\.")
def err(msg): errors.append(msg)

def load(name):
    p = PUB / name
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        err(f"{name}: invalid JSON ({e})")
        return None

# ── JSON validity ────────────────────────────────────────────────────
questions = load("questions.json")
vocab     = load("vocabulary.json")
abridged  = load("abridged.json")
reviews   = load("topic_reviews.json")
refdata   = load("reference.json")
load("manifest.json")

# ── questions.json ───────────────────────────────────────────────────
seen_numbers = {}
topics = set()
if isinstance(questions, list):
    for c in questions:
        cid = str(c.get("id", "?"))
        topics.add(c.get("topic"))
        img = c.get("image")
        if img and not (PUB / img).is_file():
            err(f"card {cid}: image not found: {img}")
        sts = c.get("statements") or []
        if not sts:
            err(f"card {cid}: no statements")
        for s in sts:
            n = str(s.get("number", ""))
            if not n:
                err(f"card {cid}: statement missing number")
                continue
            if n in seen_numbers:
                err(f"duplicate statement number {n} (cards {seen_numbers[n]} and {cid})")
            else:
                seen_numbers[n] = cid
            if s.get("answer") not in ("VERO", "FALSO"):
                err(f"#{n}: answer must be VERO/FALSO, got {s.get('answer')!r}")
            for field in ("italian_text", "english_translation", "explanation"):
                if not (s.get(field) or "").strip():
                    err(f"#{n}: empty {field}")
            # Audience asymmetry: the Italian explanation assumes a novice
            # and never compares with the US (glossary 2026-07-13, rule 12).
            for field in ("explanation_it", "warn_it"):
                if US_IT_RE.search(s.get(field) or ""):
                    err(f"#{n}: {field} compares with the US (IT text never does)")
else:
    err("questions.json: expected a list of cards")

print(f"questions: {len(questions or [])} cards, {len(seen_numbers)} statements, {len(topics)} topics")

# ── withdrawn statements ─────────────────────────────────────────────
# The Ministry withdrew 41 statements between the January 2023 listato we
# extracted and the April 2025 one. They keep their entry in questions.json,
# marked `"retired": "YYYY-MM-DD"` with the date of the publication that
# dropped them, because that file is our archive of the bank. Everything
# downstream treats them as out of scope: the app filters them at load, and
# so does every check below, which is why `questions` is rebound here. See
# docs/BANK-2025-DIFF.md.
RETIRED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
questions_all = questions if isinstance(questions, list) else []
retired = set()
for c in questions_all:
    for s in (c.get("statements") or []):
        mark = s.get("retired")
        if mark is None:
            continue
        if not (isinstance(mark, str) and RETIRED_RE.match(mark)):
            err(f"#{s.get('number')}: retired must be a YYYY-MM-DD date, got {mark!r}")
        retired.add(str(s.get("number")))
if retired:
    emptied = [str(c.get("id")) for c in questions_all
               if (c.get("statements") or [])
               and all(str(s.get("number")) in retired for s in c["statements"])]
    questions = [c if all(str(s.get("number")) not in retired for s in (c.get("statements") or []))
                 else dict(c, statements=[s for s in c["statements"]
                                          if str(s.get("number")) not in retired])
                 for c in questions_all]
    questions = [c for c in questions if c.get("statements")]
    seen_numbers = {n: cid for n, cid in seen_numbers.items() if n not in retired}
    topics = {c.get("topic") for c in questions}
    print(f"retired: {len(retired)} statements withdrawn by the Ministry, "
          f"{len(questions)} cards and {len(seen_numbers)} statements reach the learner"
          + (f" (cards emptied: {', '.join(emptied)})" if emptied else ""))

# ── the added-clause trap ────────────────────────────────────────────
# A FALSO statement may carry `clause: {text, kind}`: the words the Ministry
# added to a claim it marks VERO elsewhere, which are the only reason the
# statement is false (the maintainer's request of 2026-09-26; 240 found by a
# reader pass over every FALSO statement, docs/review-glossary.md rule 62).
# The text must sit verbatim in the statement, the statement must be a live
# FALSO, and both explanations must carry the fixed warning sentence, so a
# reworded explanation cannot drop the warning in silence.
CLAUSE_EN = "Read the whole sentence:"
CLAUSE_IT = "Leggi tutta la frase:"
n_clause = 0
for c in questions:
    for s in (c.get("statements") or []):
        cl = s.get("clause")
        if cl is None:
            continue
        n = s.get("number")
        n_clause += 1
        if not (isinstance(cl, dict) and cl.get("text") and cl.get("kind") in ("a", "b", "c", "d")):
            err(f"#{n}: clause must be {{text, kind a-d}}")
            continue
        if s.get("answer") != "FALSO":
            err(f"#{n}: clause on a VERO statement")
        if cl["text"] not in (s.get("italian_text") or ""):
            err(f"#{n}: clause text is not in the statement: {cl['text']!r}")
        if CLAUSE_EN not in (s.get("explanation") or ""):
            err(f"#{n}: clause statement whose explanation lacks the warning sentence")
        if CLAUSE_IT not in (s.get("explanation_it") or ""):
            err(f"#{n}: clause statement whose explanation_it lacks the warning sentence")
print(f"clause traps: {n_clause} FALSO statements carry the added-clause warning")

# ── the sentence taken apart ─────────────────────────────────────────
# A statement may carry `reading: {rows: [{lab, it, en, main?}], note}`, the
# Italian sentence in labelled parts, drawn after the English explanation.
# The parts must join to the statement itself, so a breakdown can never
# drift from the Ministry's wording.
n_reading = 0
for q in questions:
    for s in q["statements"]:
        rd = s.get("reading")
        if rd is None:
            continue
        n = s["number"]
        n_reading += 1
        rows = rd.get("rows") if isinstance(rd, dict) else None
        if not rows or any(not isinstance(r, dict) or not all(r.get(k) for k in ("lab", "it", "en")) for r in rows):
            err(f"#{n}: reading must be {{rows: [{{lab, it, en}}], note}}")
            continue
        if " ".join(" ".join(r["it"] for r in rows).split()) != " ".join(s["italian_text"].split()):
            err(f"#{n}: reading rows do not join to the statement")
        if sum(1 for r in rows if r.get("main")) != 1:
            err(f"#{n}: reading needs exactly one main row")
        note = rd.get("note", "")
        if note and (not note.endswith(".") or note.count("*") % 2 or "\u2014" in note):
            err(f"#{n}: reading note must end with a period, pair its asterisks and carry no em dash")
print(f"readings: {n_reading} statements carry a part-by-part reading")

# Links from an explanation into the notes, [words](notes:path): every target
# must be a figure in some topic review, in both halves, and the English and
# Italian explanations must link to the same figures (20261010n).
NOTES_RE = re.compile(r"\[([^\]]+)\]\(notes:([^)\s]+)\)")
n_links = 0
for q in questions:
    for s in q["statements"]:
        en = NOTES_RE.findall(s.get("explanation") or "")
        it = NOTES_RE.findall(s.get("explanation_it") or "")
        if not en and not it:
            continue
        n = s["number"]
        n_links += len(en)
        if sorted(t for _, t in en) != sorted(t for _, t in it):
            err(f"#{n}: the English and Italian explanations link to different figures")
        for _, tgt in en + it:
            if not any(f"({tgt})" in (r.get("en") or "") and f"({tgt})" in (r.get("it") or "") for r in reviews.values() if isinstance(r, dict)):
                err(f"#{n}: explanation links to {tgt}, which no topic review shows in both halves")
print(f"notes links: {n_links} links from explanations into the notes")

# "If you had to guess" (Statistics page, 20261007p): every cue in the
# GUESS_CUES block of app.js must still lean its way by 70% or more over at
# least 50 live statements, words read as the app reads them.
_app = (PUB / "app.js").read_text(encoding="utf-8")
_m = re.search(r"const GUESS_CUES = /\*json\*/(.*?)/\*end\*/;", _app, re.S)
if not _m:
    err("app.js: GUESS_CUES block not found")
else:
    _cues = json.loads(_m.group(1))
    _stats = {c["cue"]: [0, 0] for c in _cues}
    for c in questions:
        for s in (c.get("statements") or []):
            words = re.findall(r"[a-zàèéìòù']+", (s.get("italian_text") or "").lower())
            feats = set(words) | {a + " " + b for a, b in zip(words, words[1:])}
            for cue in _cues:
                if cue["cue"] in feats:
                    _stats[cue["cue"]][0] += 1
                    _stats[cue["cue"]][1] += s.get("answer") == cue["lean"]
    _weak = 0
    for cue in _cues:
        n, k = _stats[cue["cue"]]
        if n < 50 or k / n < 0.70:
            _weak += 1
            err(f"guess cue {cue['cue']!r}: {k}/{n} lean {cue['lean']}, under 70% or 50 statements")
        if not (cue.get("en") and cue.get("it")):
            err(f"guess cue {cue['cue']!r}: needs en and it")
    print(f"guess cues: {len(_cues)} cues, " + ("all at 70% or more" if not _weak else f"{_weak} below 70%"))

# Nothing may point at a withdrawn statement. A dangling citation would leave
# a Reference figure with no source, a study list with a hole, or a review
# paragraph claimed by a statement no learner can meet.
for label, blob in (("abridged.json", abridged),
                    ("review_anchors.json", load("review_anchors.json")),
                    ("reference.json", refdata)):
    text = json.dumps(blob, ensure_ascii=False)
    dangling = sorted(n for n in retired if f'"{n}"' in text)
    if dangling:
        err(f"{label}: cites retired statement(s) {', '.join(dangling)}")

# ── review figures: every ![..](path) in topic_reviews_md must resolve ─
import glob as _glob
import re as _re
for _md in _glob.glob(str(ROOT / "topic_reviews_md" / "*.md")):
    if _md.endswith("README.md"):
        continue
    for _m in _re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", open(_md, encoding="utf-8").read()):
        if _m.group(1).startswith("widget:"):
            continue  # interactive widget marker, not an image (rendered by app.js)
        if not (PUB / _m.group(1)).is_file():
            err(f"{_md.split('/')[-1]}: review image not found: {_m.group(1)}")

# ── abridged.json: refs must resolve ─────────────────────────────────
if isinstance(abridged, dict) and isinstance(questions, list):
    by_id = {str(c.get("id")): c for c in questions}
    for cid, kept in abridged.items():
        card = by_id.get(str(cid))
        if not card:
            err(f"abridged.json references unknown card {cid}")
            continue
        nums = {str(s.get("number")) for s in (card.get("statements") or [])}
        if not isinstance(kept, list) or not kept:
            err(f"abridged.json card {cid}: kept set must be a non-empty list")
            continue
        for k in kept:
            if str(k) not in nums:
                err(f"abridged.json card {cid}: kept #{k} not in that card")

# ── topic_reviews.json covers every topic ────────────────────────────
if isinstance(reviews, dict):
    missing = [t for t in topics if t and t not in reviews]
    if missing:
        err(f"topic_reviews.json missing reviews for {len(missing)} topic(s): {missing}")

# ── topic reviews: English and Italian in sync, and the shipped build current ──
# The IT reveal pills come from a block-by-block pairing of the two languages,
# which means a paragraph nobody translated now shows up as a missing pill
# rather than as an error. So the pairing is rebuilt here FROM THE MARKDOWN
# SOURCES and checked three ways: no English block without an Italian one, no
# Italian block without an English one, and the shipped JSON equal to what the
# sources produce. English-only scaffolding (the "For US drivers" notes and the
# comparisons with American practice) must be DECLARED with a trailing
# "<!-- en-only -->"; inferring it from the wording would let a genuinely
# missing translation hide behind the exemption.
if isinstance(reviews, dict):
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("mdrev", ROOT / "scripts" / "md_to_reviews.py")
    _m = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_m)
    md_dir = ROOT / "topic_reviews_md"
    pairs_n = en_only_n = 0
    checked = 0
    # Claims (see md_to_reviews.py): statement -> (topic, block hash), and the
    # per-topic accounting needed for the coverage report below.
    claim_of = {}                 # statement number -> (topic, hash, file)
    absent_of = {}                # topic -> set of statements declared absent
    complete_topics = set()
    rules_topics = set()          # picture topics: rule statements claimed, the rest land on the image
    for path in sorted(md_dir.glob("*.md")):
        if path.name.lower() in ("readme.md", "_manifest.json"):
            continue
        try:
            topic, en_raw, it_raw = _m.parse_md(path.read_text(encoding="utf-8"))
        except Exception as e:
            err(f"{path.name}: cannot parse ({e})"); continue
        if topic not in reviews:
            err(f"{path.name}: topic not in topic_reviews.json: {topic[:50]}"); continue
        checked += 1
        en_raw, claims, absent, complete = _m.extract_claims(en_raw)
        absent_of[topic] = absent
        if complete == "complete":
            complete_topics.add(topic)
        elif complete == "rules":
            rules_topics.add(topic)
        for h, nums in claims.items():
            for n in nums:
                if n in claim_of:
                    err(f"{path.name}: statement {n} is claimed twice (also in {claim_of[n][2]})")
                claim_of[n] = (topic, h, path.name)
        sync = _m.review_sync(en_raw, it_raw)
        for h, nums in claims.items():
            if h not in sync["pairs"]:
                err(f"{path.name}: <!-- q: {' '.join(nums)} --> sits on a block with no Italian twin")
        shipped_claims = {n: h for h, nums in claims.items() for n in nums}
        if (reviews[topic].get("claims") or {}) != shipped_claims:
            err(f"{path.name}: shipped `claims` map is stale (re-run scripts/md_to_reviews.py)")
        if bool(reviews[topic].get("complete")) != (complete == "complete"):
            err(f"{path.name}: shipped `complete` flag is stale (re-run scripts/md_to_reviews.py)")
        if bool(reviews[topic].get("rules")) != (complete == "rules"):
            err(f"{path.name}: shipped `rules` flag is stale (re-run scripts/md_to_reviews.py)")
        pairs_n += len(sync["pairs"])
        for head, blk in sync["en_gap"]:
            err(f"{path.name}: English has no Italian, under {head!r}: {blk[:60]}")
        for head, blk in sync["it_gap"]:
            err(f"{path.name}: Italian has no English, under {head!r}: {blk[:60]}")
        for lang, head in sync["sec_gap"]:
            err(f"{path.name}: {lang.upper()}-only section, undeclared: {head!r}")
        shipped = reviews[topic]
        if shipped.get("en") != _m.strip_markers(en_raw).strip("\n"):
            err(f"{path.name}: shipped English differs from the source (re-run scripts/md_to_reviews.py)")
        if shipped.get("it") != it_raw.strip("\n"):
            err(f"{path.name}: shipped Italian differs from the source (re-run scripts/md_to_reviews.py)")
        if shipped.get("pairs") != sync["pairs"]:
            err(f"{path.name}: shipped `pairs` map is stale (re-run scripts/md_to_reviews.py)")
        for _l, _h, _lines in _m._sections(en_raw):
            en_only_n += sum(1 for x in _m._text_blocks(_lines) if _m._marked(x))
    if not errors:
        print(f"topic reviews: {checked} files in sync, {pairs_n} EN/IT block pairs, "
              f"{en_only_n} blocks declared English-only")

    # ── Claim coverage: every statement, by the topic its card is filed under.
    # A claim may live in another topic's review (24106 sits in topic 22);
    # what matters is that each statement is claimed somewhere, or declared
    # absent. For a topic marked complete, an unclaimed statement fails the
    # build: that is the guarantee that no learner presses 📖 and lands nowhere
    # useful. The VERO/FALSO split is printed because a landing that only true
    # statements get would be an answer key.
    all_stmts = {}
    pictured = set()              # statements whose card carries a picture
    for q in questions:
        for st in (q.get("statements") or []):
            all_stmts[str(st.get("number"))] = (q["topic"], st.get("answer"))
            if q.get("image"):
                pictured.add(str(st.get("number")))
    for n, (t, h, fname) in claim_of.items():
        if n not in all_stmts:
            err(f"{fname}: <!-- q: {n} --> claims a statement that does not exist")
    for t, absent in absent_of.items():
        for n in absent:
            if n not in all_stmts:
                err(f"{t[:30]}: <!-- absent: {n} --> names a statement that does not exist")
            elif n in claim_of:
                err(f"{t[:30]}: statement {n} is both claimed and declared absent")
    by_topic = {}
    for n, (t, ans) in all_stmts.items():
        by_topic.setdefault(t, []).append(n)
    claimed_total = sum(1 for n in all_stmts if n in claim_of)
    if claimed_total:
        v = sum(1 for n in all_stmts if n in claim_of and all_stmts[n][1] == "VERO")
        nv = sum(1 for n, (t, a) in all_stmts.items() if a == "VERO")
        f = claimed_total - v
        print(f"claims: {claimed_total} of {len(all_stmts)} statements claimed by a paragraph "
              f"(VERO {100*v/max(nv,1):.0f}%, FALSO {100*f/max(len(all_stmts)-nv,1):.0f}%)")
    for t in sorted(complete_topics):
        nums = by_topic.get(t, [])
        unclaimed = [n for n in nums if n not in claim_of and n not in absent_of.get(t, set())]
        absent_n = sum(1 for n in nums if n in absent_of.get(t, set()))
        if unclaimed:
            err(f"{t[:40]}: marked <!-- claims: complete --> but {len(unclaimed)} statement(s) "
                f"neither claimed nor absent: {' '.join(unclaimed[:12])}{' ...' if len(unclaimed) > 12 else ''}")
        else:
            print(f"  complete: {t[:44]}: {len(nums) - absent_n} claimed, {absent_n} absent")
    # A picture topic marked `rules` leaves sign identification to the card's
    # image, so an unclaimed statement is acceptable only where there IS an
    # image; on a card with none, nothing but the picker's guess is left, and
    # that is exactly the case the lighter pass promised to cover.
    for t in sorted(rules_topics):
        nums = by_topic.get(t, [])
        absent_s = absent_of.get(t, set())
        unclaimed = [n for n in nums if n not in claim_of and n not in absent_s]
        blind = [n for n in unclaimed if n not in pictured]
        if blind:
            err(f"{t[:40]}: marked <!-- claims: rules --> but {len(blind)} unclaimed statement(s) "
                f"sit on a card with no picture: {' '.join(blind[:12])}{' ...' if len(blind) > 12 else ''}")
        else:
            print(f"  rules: {t[:44]}: {len(nums) - len(unclaimed) - len(absent_s)} claimed, "
                  f"{len(absent_s)} absent, {len(unclaimed)} left to the picture")

# ── review_anchors.json: every card exists, every heading exists in both languages ──
anchors_path = PUB / "review_anchors.json"
if anchors_path.exists():
    anchors = json.loads(anchors_path.read_text(encoding="utf-8"))
    card_topic = {}
    for q in questions:
        card_topic[str(q["id"])] = q["topic"]
    # "## " sections AND "### " sub-sections are both targetable: the precise
    # spot is often the sub-section (trailer insurance sits under "Hooking up").
    heads = {}
    for t, v in reviews.items():
        heads[t] = (set(re.findall(r"^###? (.*)$", v.get("en", ""), re.M)),
                    set(re.findall(r"^###? (.*)$", v.get("it", ""), re.M)))
    card_stmts = {}
    for q in questions:
        card_stmts[str(q["id"])] = {str(st.get("number")) for st in (q.get("statements") or [])}
    bad = 0

    def section_hashes(t, heading):
        """Hashes of the EN blocks under `heading` (sub-sections included),
        the same walk as reviewBlocks / pickReviewBlock in app.js: a block
        belongs to every heading it sits under, since a "## " section may open
        straight into a "### " one and hold no text of its own."""
        want = (heading or "").strip()
        stack, out = [], set()
        for l, h, lines in _m._sections(reviews[t].get("en", "")):
            if l:
                while stack and stack[-1][0] >= l: stack.pop()
                stack.append((l, h.strip()))
            if want in [x[1] for x in stack]:
                out.update(_m._hash(b) for b in _m._text_blocks(lines))
        return out

    def check_anchor(where, a, topic):
        """One anchor: a figure, or a heading that exists in BOTH languages of
        `topic`'s review. An anchor may name another topic (a statement whose
        subject is filed elsewhere); the heading is then checked over there."""
        global bad
        t = a.get("topic", topic)
        if t not in reviews:
            err(f"review_anchors.json: {where}: unknown topic {t!r}"); bad += 1; return
        if "img" in a:
            v = reviews.get(t, {})
            if "(" + a["img"] + ")" not in (v.get("en", "") + v.get("it", "")):
                err(f"review_anchors.json: {where}: figure not in review: {a['img']}"); bad += 1
            return
        he, hi = heads.get(t, (set(), set()))
        if a.get("en") not in he: err(f"review_anchors.json: {where}: EN heading not in review: {a.get('en')!r}"); bad += 1
        if a.get("it") not in hi: err(f"review_anchors.json: {where}: IT heading not in review: {a.get('it')!r}"); bad += 1
        # An explicit paragraph: the hash of an EN block (as the pairs map keys
        # them, so it has an Italian twin), and it must sit under the anchored
        # heading, or the app would flash a paragraph outside the section it
        # scrolled to. A reworded block changes its hash, so a stale override
        # fails here instead of silently landing on the heading.
        if "block" in a:
            v = reviews.get(t, {})
            if a["block"] not in (v.get("pairs") or {}):
                err(f"review_anchors.json: {where}: block {a['block']!r} is not a translated EN block of the review"); bad += 1
            elif a["block"] not in section_hashes(t, a.get("en")):
                err(f"review_anchors.json: {where}: block {a['block']!r} is not under heading {a.get('en')!r}"); bad += 1

    for cid, a in anchors.items():
        t = card_topic.get(cid)
        if not t: err(f"review_anchors.json: unknown card {cid}"); bad += 1; continue
        check_anchor(f"card {cid}", a, t)
        # Per-statement overrides: the statement must be on that card.
        for num, sa in (a.get("stmts") or {}).items():
            if num not in card_stmts.get(cid, set()):
                err(f"review_anchors.json: card {cid}: statement {num} is not on this card"); bad += 1
                continue
            # Mirrors reviewAnchorFor in app.js: an entry naming neither a
            # section nor a figure refines the card's anchor with a paragraph.
            if not sa.get("en") and not sa.get("img"):
                merged = {k: v for k, v in a.items() if k != "stmts"}
                merged.update(sa)
                sa = merged
            check_anchor(f"card {cid} statement {num}", sa, t)
    if not bad:
        per_stmt = sum(len(a.get("stmts") or {}) for a in anchors.values())
        print(f"review_anchors.json: {len(anchors)} cards anchored to existing sections"
              + (f", plus {per_stmt} per-statement anchors" if per_stmt else ""))

# ── reference.json: the Review page's numbers and lists ──────────────
# Every number must still be traceable: the figure it teaches has to appear
# either in one of the statements it cites or in that topic's proofed review.
# This is what stops the Review page from drifting away from the bank.
if isinstance(refdata, dict):
    cat_ids = {c.get("id") for c in refdata.get("categories", [])}
    group_ids = {g.get("id") for g in refdata.get("groups", [])}
    topics_in_bank = topics if isinstance(questions, list) else set()
    md_dir = ROOT / "topic_reviews_md"
    md_cache = {}

    def review_text(n):
        if n not in md_cache:
            hits = sorted(md_dir.glob(f"{n:02d}-*.md"))
            md_cache[n] = hits[0].read_text(encoding="utf-8") if hits else ""
        return md_cache[n]

    # The bank spells some units in words; treat these as the same kind.
    UNIT_WORDS = {
        "kg": ["kg", "chilogrammi", "chili"],
        "t": ["t", "tonnellate"],
        "km/h": ["km/h", "chilometri orari"],
        "m": ["m ", "metri"],
        "punti": ["punti"],
        "g/l": ["g/l", "grammi per litro"],
        "cm³": ["cm³", "cc", "centimetri cubi"],
        "kW": ["kw"],
        "anni": ["anni"],
        "mm": ["mm", "millimetri"],
        "cm": ["cm", "centimetri"],
        "ore": ["ore"],
        "posti": ["posti"],
        "persone": ["persone"],
    }

    NUM_WORDS = {
        "0": ["zero"],
        "1": ["un ", "uno", "una "], "2": ["due"], "3": ["tre"], "4": ["quattro"],
        "5": ["cinque"], "6": ["sei"], "7": ["sette"], "8": ["otto"], "9": ["nove"],
        "10": ["dieci"], "12": ["dodici"], "14": ["quattordici"], "15": ["quindici"],
        "16": ["sedici"], "18": ["diciotto"], "20": ["venti"], "21": ["ventuno"],
        "24": ["ventiquattro"], "30": ["trenta"], "40": ["quaranta"],
        "45": ["quarantacinque"], "50": ["cinquanta"], "70": ["settanta"],
        "90": ["novanta"], "100": ["cento"], "750": ["settecentocinquanta"],
    }

    def tests_value(text, value):
        """Does this statement test that quantity?"""
        if not text:
            return False
        low = text.lower()
        figs = figures(value)
        if figs:
            if any(f in text for f in figs):
                return True
            for f in figs:
                base = f.split(",")[0].split(".")[0]
                if any(w in low for w in NUM_WORDS.get(base, [])):
                    return True
            return False
        # A value with no digits at all ("il doppio", "da mezz'ora dopo il
        # tramonto"): look for its own words instead.
        words = [w for w in re.findall(r"[a-zàèéìòù']{4,}", value.lower())
                 if w not in ("della", "delle", "oltre", "fino")]
        return bool(words) and all(w in low for w in words[:2])

    def figures(value):
        out = set()
        for m in re.finditer(r"\d+(?:[.,]\d+)?", value):
            x = m.group(0)
            out |= {x, x.replace(",", "."), x.replace(".", ",")}
        return out

    stmt_rows = []          # (number, answer, italian_text, topic) for the checks below
    stmt_text = {}
    stmt_answer = {}
    if isinstance(questions, list):
        for c in questions:
            for st in (c.get("statements") or []):
                stmt_text[str(st.get("number"))] = st.get("italian_text") or ""
                stmt_answer[str(st.get("number"))] = st.get("answer")
                stmt_rows.append((str(st.get("number")), st.get("answer"),
                                  st.get("italian_text") or "", c.get("topic")))

    for i, n in enumerate(refdata.get("numbers", [])):
        where = f"reference.json number {i} ({n.get('value','?')})"
        if n.get("cat") not in cat_ids:
            err(f"{where}: unknown category {n.get('cat')!r}")
        if n.get("noWrong") and n.get("trap"):
            err(f"{where}: cannot be both a trap and never faked")
        # The strong mark claims the figure is only ever asked as true. That is
        # a property of the bank, so it is re-checked here on every run: within
        # the row's own topic, every statement carrying the figure must be VERO,
        # and the row must cite them. A future bank that adds one FALSO with
        # this number fails the build instead of quietly misleading a learner.
        if n.get("alwaysTrue"):
            if not n.get("noWrong"):
                err(f"{where}: marked only-ever-true without being marked never faked")
            # Match the quantity WITH its unit and on word boundaries, or "50"
            # would also fire on 150 km/h and on 50 metri.
            m_num = re.search(r"\d+(?:[.,]\d+)?", n.get("value", ""))
            unit = re.sub(r"^[^A-Za-z\u00C0-\u024F]+", "", n.get("value", "")).strip().split()[0] if m_num else ""
            # An unknown "unit" (the towing ratio's "×") means the figure is
            # bare: match it on word boundaries alone rather than demanding a
            # unit that never appears in the text.
            forms = UNIT_WORDS.get(unit, [])
            variants = "|".join(sorted({re.escape(v) for v in (
                (m_num.group(0), m_num.group(0).replace(",", "."), m_num.group(0).replace(".", ","))
                if m_num else ())}, key=len, reverse=True))
            tail = ("\\s*(?:" + "|".join(re.escape(f.strip()) for f in forms) + ")") if forms else ""
            pat = re.compile(r"(?<![\d.,])(?:" + variants + r")(?![\d.,])" + tail, re.I) if variants else None
            carriers = [(num, ans) for num, ans, tx, tp in stmt_rows
                        if pat and tp == n.get("topicKey") and pat.search(tx)]
            if not carriers:
                err(f"{where}: marked only-ever-true, but no statement in its topic carries the quantity")
            wrong = [num for num, ans in carriers if ans != "VERO"]
            if wrong:
                err(f"{where}: marked only-ever-true, but these statements are FALSO: {', '.join(sorted(wrong))}")
            uncited = [num for num, ans in carriers if num not in n.get("src", [])]
            if uncited:
                err(f"{where}: marked only-ever-true, but does not cite {', '.join(sorted(uncited))}")
        # `asked` lists every question that turns on this figure (20261010z):
        # all live, at least one, none on a row whose number is never tested.
        # The consistently-missed chip draws the row as one short line
        # (20261026c): every figure that can reach it carries a short phrase
        # in both languages, with no parenthetical and no metadata, since the
        # line is all the learner reads there.
        if "asked" in n:
            for k in ("shortEn", "shortIt"):
                s = n.get(k)
                if not isinstance(s, str) or not s.strip():
                    err(f"{where}: a row with an asked list needs {k}")
                elif "(" in s or len(s) > 90:
                    err(f"{where}: {k} must be short and carry no parenthetical: {s!r}")
        if "asked" in n:
            if n.get("untested"):
                err(f"{where}: an untested row carries an asked list")
            elif not n["asked"]:
                err(f"{where}: empty asked list")
            else:
                gone = [x for x in n["asked"] if x not in stmt_answer]
                if gone:
                    err(f"{where}: asked lists statements that are not live: {', '.join(gone)}")
        elif not n.get("untested"):
            err(f"{where}: no asked list")
        for g in ([n["group"]] if isinstance(n.get("group"), str) else n.get("group") or []):
            if g not in group_ids:
                err(f"{where}: unknown group {g!r}")
        if n.get("topicKey") not in topics_in_bank:
            err(f"{where}: topicKey not a topic in questions.json")
        # valueEn is the American rendering of the same quantity: it may differ
        # in separators and unit words, but it must carry the same digits.
        if n.get("valueEn"):
            digits = lambda t: re.sub(r"[^0-9]", "", t)
            if digits(n["valueEn"]) != digits(n["value"]):
                err(f"{where}: valueEn does not carry the same digits as value")
        # us is the rounded US equivalent of a length, shown to an English
        # reader only (reviewer flag 24104, 2026-09-30).
        if n.get("us") is not None:
            if n.get("cat") not in ("distance", "size") or not re.fullmatch(r"[0-9/ ]+ (in|ft|mi)( [0-9]+ in)?", n["us"]):
                err(f"{where}: us must be a length in in, ft or mi on a distance or size row")
        for f in ("en", "it", "value"):
            if not (n.get(f) or "").strip():
                err(f"{where}: empty {f}")
        for sid in n.get("src", []):
            if sid not in stmt_text:
                err(f"{where}: cites statement {sid}, which does not exist")
        # The Review page holds only what the exam actually asks, so a number
        # must be tested by one of the statements it cites: the figure appears
        # there in digits, or spelled out in words ("otto persone", "mezz'ora").
        # Being taught in the topic review is NOT enough on its own.
        if not n.get("src"):
            err(f"{where}: no statement cited, so nothing shows the exam tests it")
        elif any(tests_value(stmt_text.get(sid, ""), n.get("value", "")) for sid in n.get("src", [])):
            pass
        elif n.get("measure"):
            # The withdrawal / suspension / revocation / revision table
            # (maintainer, 2026-09-26): the value is a measure, not a figure.
            # It must be one of the four, and every cited statement must be
            # VERO, since a FALSO statement naming a measure is a trap.
            if (n.get("valueEn"), n.get("value")) not in {("Withdrawal", "Ritiro"), ("Suspension", "Sospensione"),
                                                        ("Revocation", "Revoca"), ("Revision", "Revisione")}:
                err(f"{where}: a measure row must name withdrawal, suspension, revocation or revision")
            bad = [sid for sid in n.get("src", []) if stmt_answer.get(sid) != "VERO"]
            if bad:
                err(f"{where}: a measure row must cite only VERO statements ({', '.join(bad)})")
        elif n.get("tested") and re.match(r"^0\b", n.get("value", "")):
            pass   # a zero-points row: checked below, against FALSO statements claiming a loss
        elif n.get("rule"):
            # A derived rule ("km/h ÷ 3,6") prints no figure of its own. It is
            # sound only if the values it derives ARE tested, so every figure
            # named in its group's note must appear in one of its statements.
            note = ""
            for g in refdata.get("groups", []):
                ids = n["group"] if isinstance(n.get("group"), list) else [n.get("group")]
                if g.get("id") in ids:
                    note += " " + (g.get("noteEn") or "")
            wanted = {m.group(0) for m in re.finditer(r"\b\d{1,3}\b", note)}
            texts = " ".join(stmt_text.get(sid, "") for sid in n.get("src", []))
            missing = sorted(f for f in wanted if f not in texts)
            if not wanted:
                err(f"{where}: marked as a rule, but its group states no figures to check")
            elif missing:
                err(f"{where}: marked as a rule, but these derived values are untested: {', '.join(missing)}")
        elif n.get("untested"):
            # The points table (maintainer, 2026-09-26): the bank asks WHICH
            # violations cost points and names a figure for exactly one, so
            # the other rows carry the Code's figure (art. 126-bis) marked as
            # never tested. The row names the article, and the statements it
            # cites must be the ones that test the point LOSS, since that is
            # what the row is on the page for.
            if not re.match(r"^art\. \d+", str(n["untested"])):
                err(f"{where}: untested must name the Code article (art. N ...)")
            if not all("punti" in stmt_text.get(sid, "").lower() for sid in n.get("src", [])):
                err(f"{where}: marked untested, but a cited statement does not test the point loss")
            if n.get("tested") or n.get("noWrong") or n.get("trap"):
                err(f"{where}: untested cannot carry another mark")
        elif n.get("trap"):
            # The exam probes this quantity with a WRONG figure ("work machines
            # may exceed 50 km/h", FALSO), so the learner still has to know the
            # right one. Such a row is allowed, on two conditions: a cited
            # statement must talk about the same kind of quantity, and the true
            # figure must come from the proofed topic review.
            unit = re.sub(r"^[^A-Za-z\u00C0-\u024F]+", "", n.get("value", "")).strip()
            forms = UNIT_WORDS.get(unit, [unit]) if unit else []
            same_kind = any(any(f.lower() in stmt_text.get(sid, "").lower() for f in forms)
                            for sid in n.get("src", []))
            in_review = any(f in review_text(n.get("topic", 0)) for f in figures(n.get("value", "")))
            if not same_kind:
                err(f"{where}: marked as a trap, but no cited statement measures {unit or 'that quantity'}")
            if not in_review:
                err(f"{where}: marked as a trap, but the true quantity is not taught in the topic review")
        else:
            err(f"{where}: none of its statements test this value (mark it \"trap\": true "
                f"if the exam only ever names a wrong value for it)")

    # A fine is shown under a violation row (maintainer, 2026-09-26). The bank
    # tests no fine amount, so it must name the Code article it comes from, and
    # its two faces must carry the same digits.
    for i, n in enumerate(refdata.get("numbers", [])):
        f = n.get("fine")
        if not f:
            continue
        where = f"reference.json number {i} ({n.get('value','?')}) fine"
        if not re.match(r"^art\. \d+", str(f.get("art", ""))):
            err(f"{where}: must name the Code article (art. N ...)")
        if not (f.get("value") and f.get("valueEn")):
            err(f"{where}: needs value and valueEn")
        elif re.sub(r"[^0-9]", "", f["value"]) != re.sub(r"[^0-9]", "", f["valueEn"]):
            err(f"{where}: value and valueEn do not carry the same digits")
        if bool(f.get("noteEn")) != bool(f.get("noteIt")):
            err(f"{where}: a note needs both languages")

    # A row may say that the bank ALSO asks the figure with a wrong value
    # (maintainer, 2026-09-30, on emergency towing: 2 points VERO in 23956,
    # 4 points FALSO in 23960). Every statement it cites must be FALSO and
    # must carry the wrong figure, and the row must be one that is tested.
    for i, n in enumerate(refdata.get("numbers", [])):
        w = n.get("wrong")
        if not w:
            continue
        where = f"reference.json number {i} ({n.get('value','?')}) wrong"
        if not (w.get("value") and w.get("valueEn") and w.get("src")):
            err(f"{where}: needs value, valueEn and src")
            continue
        if not (n.get("tested") or n.get("src")) or n.get("untested") or n.get("noWrong") or n.get("alwaysTrue"):
            err(f"{where}: only a tested row without a never-faked mark may name a wrong value")
        digits = re.sub(r"[^0-9]", "", w["value"])
        for sid in w["src"]:
            if stmt_answer.get(sid) != "FALSO":
                err(f"{where}: {sid} is not a live FALSO statement")
            elif digits and digits not in re.sub(r"[^0-9 ]", " ", stmt_text.get(sid, "")).split():
                err(f"{where}: {sid} does not carry the wrong figure {w['value']}")

    # The "tested" highlight is the counterpart of "untested": it says the
    # figure IS asked for, so it is allowed only on a row whose statements test
    # its value, and a group holding untested rows must hold exactly one of it,
    # or the contrast the marks draw has nothing to point at.
    by_group = {}
    for i, n in enumerate(refdata.get("numbers", [])):
        where = f"reference.json number {i} ({n.get('value','?')})"
        gids = n["group"] if isinstance(n.get("group"), list) else [n.get("group")]
        for gid in gids:
            by_group.setdefault(gid, []).append(n)
        if n.get("tested"):
            # A ZERO row says the violation costs no points, which the bank
            # tests with a FALSO statement claiming a loss: the figure never
            # appears, so the check is that every cited statement is a FALSO
            # about points.
            if re.match(r"^0\b", n.get("value", "")):
                bad = [sid for sid in n.get("src", []) if "punti" not in stmt_text.get(sid, "").lower()
                       or stmt_answer.get(sid) != "FALSO"]
                if bad or not n.get("src"):
                    err(f"{where}: a zero-points row must cite only FALSO statements that claim a point loss ({', '.join(bad)})")
            elif not any(tests_value(stmt_text.get(sid, ""), n.get("value", "")) for sid in n.get("src", [])):
                err(f"{where}: marked tested, but none of its statements test the value")
    for gid, rows in by_group.items():
        if any(r.get("untested") for r in rows) and not any(r.get("tested") for r in rows):
            err(f"reference.json group {gid!r}: holds untested figures, so at least one row must be marked tested")

    # A group may close with a "foot": a list that carries no quantity but
    # belongs with the group (the vehicles banned from the autostrada under the
    # autostrada speeds). It is still exam content, so every item has to cite a
    # statement that exists, and both languages have to be written.
    for g in refdata.get("groups", []):
        foot = g.get("foot")
        if not foot:
            continue
        where = f"reference.json group {g.get('id')!r} foot"
        # A group can hold rows in several categories; the footer shows in one.
        if foot.get("cat") and foot["cat"] not in cat_ids:
            err(f"{where}: unknown category {foot['cat']!r}")
        for f in ("en", "it"):
            if not (foot.get(f) or "").strip():
                err(f"{where}: empty {f}")
        # A footer is either a list of cases or a single closing note (the
        # secondary roads bar no vehicle, which is itself worth saying).
        if not foot.get("items") and not (foot.get("noteEn") or foot.get("noteIt")):
            err(f"{where}: neither items nor a note")
        for j, item in enumerate(foot.get("items") or []):
            for f in ("en", "it"):
                if not (item.get(f) or "").strip():
                    err(f"{where} item {j}: empty {f}")
            if not item.get("src"):
                err(f"{where} item {j}: no statement cited")
            for sid in item.get("src", []):
                if sid not in stmt_text:
                    err(f"{where} item {j}: cites statement {sid}, which does not exist")
        # The closing note names cases the exam gets wrong, so it cites too.
        if (foot.get("noteEn") or foot.get("noteIt")) and not foot.get("noteSrc"):
            err(f"{where}: has a note but cites no statement for it")
        for sid in foot.get("noteSrc", []):
            if sid not in stmt_text:
                err(f"{where}: note cites statement {sid}, which does not exist")

    if not [e for e in errors if e.startswith("reference.json")]:
        print(f"✓ reference.json: {len(refdata.get('numbers', []))} numbers, all traceable")
else:
    err("reference.json: expected an object")

# ── questions.json: digits glued to letters ──────────────────────────
# A character the source file got wrong reads as a word the vocabulary matcher
# cannot reach: 23949 printed "riprodott0" with a digit zero and the tooltip
# simply skipped the word (2026-09-11). That one is corrected in the data under
# the sanctioned exception in CLAUDE.md rule 1; this reports any other, so a
# re-extraction of the bank cannot reintroduce the class unnoticed. Not an
# error: "cm3" and "0,1kW/kg" are how the Ministry writes those units.
if isinstance(questions_all, list):
    LEGIT_DIGIT_TOKEN = re.compile(r"^(?:\d+(?:[.,]\d+)?(?:cm3|kW/kg|kW|km/h|t|kg|m|cm|mm)|cm3|kW/kg)[.,;:]?$", re.I)
    odd = []
    for c in questions_all:
        for st in (c.get("statements") or []):
            for tok in re.findall(r"\S*(?:[A-Za-zÀ-ɏ]{2,}[0-9]|[0-9][A-Za-zÀ-ɏ]{2,})\S*",
                                  st.get("italian_text") or ""):
                if not LEGIT_DIGIT_TOKEN.match(tok):
                    odd.append(f"{st.get('number')}: {tok}")
    if odd:
        print(f"note: {len(odd)} statement(s) mix digits into a word "
              f"(check against DomandeB.pdf): {', '.join(odd[:8])}")

# ── vocabulary.json: every entry carries its frequency ───────────────
# `f` (statements the entry fires in) is stamped by consolidate_vocab.py
# --apply, and the Vocabulary screen sorts and bands by it. A hand-added entry
# ships with f = 0 until that script runs, and then sorts to the bottom under
# a frequency of 0 that is plainly false (2026-09-11: five phrases added for a
# flag went out that way). An entry the script keeps always fires at least
# once, since it drops the ones that never do, so 0 can only mean unstamped.
if isinstance(vocab, dict):
    unstamped = [e.get("term") for e in vocab.get("common", []) if not e.get("f")]
    if unstamped:
        err(f"vocabulary.json: {len(unstamped)} entries with no frequency stamp "
            f"(run scripts/consolidate_vocab.py --apply): {', '.join(map(str, unstamped[:6]))}")
    else:
        print(f"✓ vocabulary.json: all {len(vocab.get('common', []))} entries carry a frequency")

# ── vocabulary.json: `aids`, memory aids for single words (2026-09-27) ──
# Keyed by the word as the bank writes it; `k` is "ff" (false friend) or
# "new" (unfamiliar) or "rel" (an English look-alike that HELPS: shared origin
# and a close meaning, or the Italian also carries the English sense). The aid
# is LANGUAGE, never a driving rule: one or two sentences, ending with a
# period, no digits, no em dash. Only a false friend may open "Not ...", and it
# must; a "rel" aid never does, and no aid says "Not only" (a word that also
# means X is not a false friend of X).
if isinstance(vocab, dict):
    _aid_bad = []
    for _w, _a in (vocab.get("aids") or {}).items():
        _t = _a.get("t") if isinstance(_a, dict) else None
        if (not isinstance(_t, str) or _a.get("k") not in ("ff", "new", "rel") or not _t.endswith(".")
                or re.search(r"\d|\u2014|!", _t) or (_a.get("k") == "ff") != _t.startswith("Not ")
                or _t.startswith("Not only")
                or _w != _w.lower()):
            _aid_bad.append(_w)
    if _aid_bad:
        err(f"vocabulary.json aids: malformed entries: {', '.join(_aid_bad[:6])}")
    else:
        print(f"✓ vocabulary.json: {len(vocab.get('aids') or {})} memory aids, all well formed")

# ── vocab_sets.json: the "Same in English" tab ─────────────────────
# Each set lists vocabulary entries that share one English word. A term that
# is not an entry would silently drop out of its set (the tab reads rows off
# the dictionary), and a vocabulary cleanup can remove one, so every term is
# checked here. A set needs two terms to say anything, and a note (the words
# are NOT interchangeable) names the topic that teaches the difference.
_vs_path = ROOT / "public_html" / "vocab_sets.json"
if _vs_path.exists() and isinstance(vocab, dict):
    _vs = json.loads(_vs_path.read_text(encoding="utf-8"))
    _terms = {e.get("term") for e in vocab.get("common", [])}
    _seen = set()
    for _i, _s in enumerate(_vs.get("sets", [])):
        _where = f"vocab_sets.json set {_i} ({_s.get('en', '?')!r})"
        if not (_s.get("en") or "").strip():
            err(f"{_where}: empty English word")
        if _s.get("en") in _seen:
            err(f"{_where}: English word listed twice")
        _seen.add(_s.get("en"))
        _ts = _s.get("terms") or []
        if len(_ts) < 2:
            err(f"{_where}: fewer than two terms")
        if len(set(_ts)) != len(_ts):
            err(f"{_where}: a term listed twice")
        _missing = [t for t in _ts if t not in _terms]
        if _missing:
            err(f"{_where}: not in vocabulary.json: {', '.join(_missing)}")
        if "topic" in _s and not (isinstance(_s["topic"], int) and 1 <= _s["topic"] <= 25):
            err(f"{_where}: topic must be 1 to 25")
    if not [e for e in errors if e.startswith("vocab_sets.json")]:
        print(f"✓ vocab_sets.json: {len(_vs.get('sets', []))} sets, every term a vocabulary entry")

# ── grammar.json: the Grammar tab ───────────────────────────────────
# Every example is a statement quoted by number. It must exist, be live, be
# VERO (an example sentence that states a false rule teaches the false rule),
# and contain the run of words the app marks; a topic needs an id, a title
# and at least one section; no digit-free rule here since it is prose.
_gr_path = ROOT / "public_html" / "grammar.json"
if _gr_path.exists():
    _gr = json.loads(_gr_path.read_text(encoding="utf-8"))
    _by_num = {str(s["number"]): s for q in questions for s in q["statements"]}
    _ids = set()
    _nex = 0
    for _ti, _tp in enumerate(_gr.get("topics", [])):
        _where = f"grammar.json topic {_ti} ({_tp.get('id', '?')!r})"
        if not _tp.get("id") or not _tp.get("title"):
            err(f"{_where}: needs id and title")
        if _tp.get("id") in _ids:
            err(f"{_where}: id listed twice")
        _ids.add(_tp.get("id"))
        if not _tp.get("sections"):
            err(f"{_where}: no sections")
        for _si, _sec in enumerate(_tp.get("sections", [])):
            if not _sec.get("h"):
                err(f"{_where} section {_si}: no heading")
            for _ex in _sec.get("ex", []):
                _nex += 1
                _n = str(_ex.get("n", ""))
                _s = _by_num.get(_n)
                if not _s:
                    err(f"{_where} section {_si}: statement {_n} is not a live statement"); continue
                if _s.get("answer") != "VERO":
                    err(f"{_where} section {_si}: statement {_n} is FALSO; only a VERO statement may be an example")
                _hl = (_ex.get("hl") or "").lower()
                if _hl and _hl not in _s["italian_text"].lower():
                    err(f"{_where} section {_si}: {_hl!r} does not occur in statement {_n}")
    if not [e for e in errors if e.startswith("grammar.json")]:
        print(f"✓ grammar.json: {len(_gr.get('topics', []))} topic(s), {_nex} examples, every one a live VERO statement")

# ── image_aliases.json in step with the image folder ─────────────────
import subprocess
r = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_image_aliases.py"), "--check"],
                   capture_output=True, text=True)
if r.returncode != 0:
    err(r.stdout.strip() or "image_aliases.json is stale")
else:
    print(r.stdout.strip())

# ── DATA_HASH in app.js and sw.js in step with the three data files ──
# The data URLs carry each file's content hash; a file edited without the
# stamp being rerun would ship under a URL naming the OLD bytes, which the
# worker would serve cache-first for as long as the hash stayed put.
r = subprocess.run([sys.executable, str(ROOT / "scripts" / "stamp_data_hashes.py"), "--check"],
                   capture_output=True, text=True)
if r.returncode != 0:
    err(r.stdout.strip() or "DATA_HASH is stale")
else:
    print(r.stdout.strip())

# ── public_html/about/ in step with topic_reviews_md/ ────────────────
# The 25 guide pages are generated from the same Markdown the app reads, so a
# review edited without re-running the generator leaves them describing the
# old rule to every search visitor, silently and for as long as nobody looks.
# Same shape as the check above: the script rebuilds in memory and compares.
r = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_topic_pages.py"), "--check"],
                   capture_output=True, text=True)
if r.returncode != 0:
    err(r.stdout.strip() or "public_html/about/ is stale")
else:
    print(r.stdout.strip())

# ── glossary.json: the Italian glossary on the Reference page ───────
#
# Three rules, each with a failure this catches.
#   * A term nobody meets is dead weight, so every headword must appear in the
#     live bank or in a topic review. SIDA's own list carried 17 words our bank
#     does not use.
#   * A FIGURE belongs in reference.json, where it is checked against the
#     statements that test it. A number written here would be unverified and
#     would go stale silently.
#   * `src` names the Code, which is the authority and is outside copyright.
#     It must look like an article reference, so a note cannot drift into it.
gloss = load("glossary.json")
gentries = gloss.get("entries", []) if isinstance(gloss, dict) else []
if not gentries:
    err("glossary.json: no entries")
else:
    bank_text = " ".join(s["italian_text"].lower() for q in questions
                         for s in q["statements"]).lower()
    rev_text  = json.dumps(load("topic_reviews.json"), ensure_ascii=False).lower()
    seen = set()
    for e in gentries:
        t = (e.get("t") or "").strip()
        d = (e.get("d") or "").strip()
        where = f"glossary.json {t!r}"
        if not t or not d:
            err(f"{where}: needs both a term and a definition"); continue
        if t.lower() in seen:
            err(f"{where}: duplicate term")
        seen.add(t.lower())
        # Every word of the headword has to be met somewhere, matched on a stem
        # so an inflected form in the bank still counts (corsia / corsie).
        for w in t.lower().split():
            stem = re.escape(w[:max(4, len(w) - 1)])
            if not (re.search(r"\b" + stem, bank_text) or re.search(r"\b" + stem, rev_text)):
                err(f"{where}: {w!r} appears neither in the live bank nor in the reviews")
        # Every entry needs its English translation, or the EN pill is missing
        # on some rows and present on others for no reason the reader can see.
        if not (e.get("en") or "").strip():
            err(f"{where}: no `en` translation")
        if re.search(r"\d", d):
            err(f"{where}: definitions carry no figures — a number belongs in reference.json")
        src = e.get("src")
        if src is not None and not re.match(r"^art\. \d+", src):
            err(f"{where}: src {src!r} should name a Code article, e.g. 'art. 3 c. 1 n. 7'")
    # `f` is recomputed here rather than trusted. It is the number the
    # "Piu frequenti" order sorts by, and it goes stale in silence: retiring a
    # statement lowers a count with nothing to show for it, and the list would
    # keep pointing a reader at a word the Ministry no longer asks about.
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from glossary_freq import counts as gloss_counts
        fresh = gloss_counts({"entries": gentries}, questions_all)
        stale = sorted(e["t"] for e in gentries if e.get("f") != fresh.get(e["t"]))
        if stale:
            err("glossary.json: stale `f` counts for " + ", ".join(stale[:6]) +
                (" ..." if len(stale) > 6 else "") +
                " - run: python3 scripts/glossary_freq.py --apply")
    except Exception as exc:                      # noqa: BLE001
        err(f"glossary.json: could not recompute frequencies ({exc})")
    if not [x for x in errors if x.startswith("glossary.json")]:
        sourced = sum(1 for e in gentries if e.get("src"))
        top = max(gentries, key=lambda e: e.get("f", 0))
        print(f"✓ glossary.json: {len(gentries)} entries, {sourced} sourced to the Code, "
              f"counts fresh (most frequent: {top['t']}, {top.get('f')} statements)")

# ── version lockstep: APP_VERSION (app.js) == CACHE_VERSION (sw.js) ───
app_js = (PUB / "app.js").read_text(encoding="utf-8")
sw_js  = (PUB / "sw.js").read_text(encoding="utf-8")
m_app = re.search(r"APP_VERSION\s*=\s*'([^']+)'", app_js)
m_sw  = re.search(r"CACHE_VERSION\s*=\s*'patente-netfirst-([^']+)'", sw_js)
if not m_app:  err("could not find APP_VERSION in app.js")
if not m_sw:   err("could not find CACHE_VERSION in sw.js")
if m_app and m_sw and m_app.group(1) != m_sw.group(1):
    err(f"version mismatch: APP_VERSION={m_app.group(1)} vs CACHE_VERSION={m_sw.group(1)}")
elif m_app and m_sw:
    print(f"version: {m_app.group(1)} (app.js and sw.js in sync)")

# ── result ───────────────────────────────────────────────────────────
if errors:
    print(f"\n✗ {len(errors)} problem(s):", file=sys.stderr)
    for e in errors:
        print("  - " + e, file=sys.stderr)
    sys.exit(1)
print("\n✓ all data checks passed")
