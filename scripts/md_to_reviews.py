#!/usr/bin/env python3
"""
Fold the edited Markdown files back into public_html/topic_reviews.json.

Run from the repo root after editing files in ./topic_reviews_md/ :
    python3 scripts/md_to_reviews.py

It reads every <slug>.md, parses the TOPIC line and the en/it sections, and
rewrites topic_reviews.json preserving the original topic order (from
_manifest.json). The existing JSON is backed up to topic_reviews.json.bak at the repo root,
outside public_html so it is never uploaded.
The service-worker cache version in public_html/sw.js is bumped automatically
so the new content ships.
"""
import json, re, pathlib, sys, datetime

# This script lives in scripts/; the project root is its parent.
ROOT   = pathlib.Path(__file__).resolve().parent.parent
MDDIR  = ROOT / "topic_reviews_md"
DEST   = ROOT / "public_html" / "topic_reviews.json"
BACKUP = ROOT / "topic_reviews.json.bak"
SW     = ROOT / "public_html" / "sw.js"

TOPIC_RE  = re.compile(r"<!--\s*TOPIC:\s*(.*?)\s*-->")
SOURCE_RE = re.compile(r"<!--\s*SOURCE:\s*([a-z]{2})\s*-->", re.I)
EN_RE     = re.compile(r"<!--\s*LANG:\s*en\s*-->")
IT_RE     = re.compile(r"<!--\s*LANG:\s*it\s*-->")

def load_manifest(path):
    """Return (default_source, entries). Supports the current object shape
    {"source": "en", "topics": [...]}  and the legacy bare-list shape."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data.get("source", "en"), data.get("topics", [])
    return "en", data            # legacy: a plain list of {file, topic}

def parse_md(text: str):
    m = TOPIC_RE.search(text)
    if not m:
        raise ValueError("missing <!-- TOPIC: ... --> line")
    topic = m.group(1).strip()
    en_m = EN_RE.search(text)
    it_m = IT_RE.search(text)
    if not en_m or not it_m:
        raise ValueError("missing <!-- LANG: en --> or <!-- LANG: it --> marker")
    en = text[en_m.end():it_m.start()].strip("\n")
    it = text[it_m.end():].strip("\n")
    # drop a trailing instruction comment if it slipped into a section
    return topic, en, it

# ── EN/IT block pairing, for the "IT" reveal pills ───────────────────────
# The English review carries a pill on each paragraph, bullet and numbered item
# that opens its Italian counterpart. The pairing is computed HERE, once, and
# shipped in topic_reviews.json, so the app only has to look a string up.
#
# The two languages are parallel but not identical: the English carries a
# "> **For US drivers.**" note the Italian deliberately omits (rule 12: the
# Italian text never compares with the US), and here and there a bullet in one
# is a paragraph in the other. So pairing by position over the whole file
# drifts. Headings anchor it instead: they are the same shape in 24 of the 25
# topics, so the files are cut at every heading and each section is paired on
# its own, which keeps any drift inside one short section.
BLOCK_IMG_RE = re.compile(r"^(?:\s*!\[[^\]]*\]\([^)]+\)\s*)+$")
BLOCK_HEAD_RE = re.compile(r"^(#{1,6}) ")
BLOCK_ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+\.) (.*)$")

def _text_blocks(lines):
    """Paragraphs, bullets, numbered items and quotes, in order, as the app
    assembles them (a paragraph is its lines joined by a space). Headings and
    image rows are not blocks: they are the anchors between them."""
    out, para = [], []
    def flush():
        if para:
            out.append(" ".join(para)); para.clear()
    for raw in lines:
        line = raw.rstrip()
        if not line.strip() or BLOCK_IMG_RE.match(line):
            flush(); continue
        m = BLOCK_ITEM_RE.match(line)
        if m:
            flush(); out.append(m.group(1).strip()); continue
        if line.startswith(">"):
            flush()
            rest = line[1:].strip()
            if rest:
                out.append(rest)
            continue
        para.append(line.strip())
    flush()
    return [b for b in out if b.strip()]

# Blocks that exist in English ONLY, so they can never pair. The reviews carry
# a "For US drivers" note in most topics, and the Italian deliberately has no
# counterpart (glossary rule 12: the Italian text never compares with the US).
# Excluding them by rule beats hoping a similarity score notices: two blocks
# with no shared digits and no shared terms score on length alone, which once
# paired a US note to an Italian intro paragraph.
# Blocks and sections that exist in English ONLY, DECLARED by the author with
# a trailing "<!-- en-only -->" marker. They are the audience scaffolding: the
# "For US drivers" notes and the comparisons with American practice, which the
# Italian deliberately has no counterpart for (glossary rule 12).
#
# The marker is a declaration, not a guess. Inferring it from the wording
# (anything mentioning the US) would let a genuinely missing translation hide
# behind the exemption, which is the one failure this whole mechanism exists to
# catch: since the IT pills come from the pairing, a paragraph nobody
# translated now shows up as a missing pill rather than as an error.
#
# The marker never reaches the app: it is stripped from the shipped English.
EN_ONLY_RE = re.compile(r"\s*<!--\s*en-only\s*-->\s*$")

def _marked(text):
    return bool(EN_ONLY_RE.search(text))

def strip_markers(md):
    """The English as the app should render it, with the markers removed."""
    return "\n".join(EN_ONLY_RE.sub("", line) for line in md.split("\n"))

# ── Claims: which exam statements a paragraph answers ──────────────────
# A block in the ENGLISH review may end with `<!-- q: 24094 24095 -->`. That
# claims those statements: the 📖 button on their card opens this paragraph
# (its Italian twin follows through the pairs map). The claim lives next to
# the paragraph, so rewording the paragraph carries it along and an editor
# sees which statements depend on the line being changed; a content hash in a
# side file, the previous design, went stale on every edit.
# Two file-level markers, each on a line of its own:
#   <!-- absent: 24101 24108 -->   statements whose rule the notes deliberately
#                                  do not state (an invented duty). Build-side
#                                  accounting only: the app treats them exactly
#                                  like unclaimed ones, or the landing would
#                                  give the answer away.
#   <!-- claims: complete -->      every statement of this topic is claimed or
#                                  absent; validate_data.py fails otherwise,
#                                  and the app stops guessing for this topic.
#   <!-- claims: rules -->         the PICTURE-topic form (decided 2026-09-19):
#                                  every statement that tests a rule is claimed
#                                  or absent, and the rest identify the pictured
#                                  sign and land on the card's image. The app
#                                  keeps the picker running for the unclaimed
#                                  ones, so nothing is worse off than before;
#                                  validate_data.py fails if an unclaimed
#                                  statement sits on a card with NO picture,
#                                  since then nothing but a guess is left.
# extract_claims returns the marker as a string: "complete", "rules" or "".
Q_RE = re.compile(r"\s*<!--\s*q:\s*([0-9][0-9\s,]*)-->")
ABSENT_LINE_RE = re.compile(r"^\s*<!--\s*absent:\s*([0-9][0-9\s,]*)-->\s*$")
COMPLETE_LINE_RE = re.compile(r"^\s*<!--\s*claims:\s*(complete|rules)\s*-->\s*$")

def _nums(s):
    return [n for n in re.split(r"[\s,]+", s.strip()) if n]

def extract_claims(en):
    """Split the English into (clean markdown, claims, absent, complete).

    `claims` maps the hash of each claiming block, exactly as the pairs map
    keys it, to the statement numbers it claims. The clean markdown is what
    review_sync and the shipped file see; the markers never render."""
    kept, absent, complete = [], set(), ""
    for line in en.replace("\r\n", "\n").split("\n"):
        m = ABSENT_LINE_RE.match(line)
        if m:
            absent.update(_nums(m.group(1))); continue
        m = COMPLETE_LINE_RE.match(line)
        if m:
            complete = m.group(1); continue
        kept.append(line)
    raw = "\n".join(kept)
    claims = {}
    for _lvl, _head, lines in _sections(raw):
        for b in _text_blocks(lines):
            nums = []
            for m in Q_RE.finditer(b):
                nums += _nums(m.group(1))
            if nums:
                clean = EN_ONLY_RE.sub("", Q_RE.sub("", b)).strip()
                claims.setdefault(_hash(clean), []).extend(nums)
    clean_md = "\n".join(Q_RE.sub("", l).rstrip() for l in kept)
    return clean_md, claims, absent, complete

def _sections(md):
    """The file cut at every heading: a list of (level, heading, lines).
    The first entry is whatever precedes the first heading."""
    secs, cur, lvl, head = [], [], 0, ""
    for raw in md.replace("\r\n", "\n").split("\n"):
        m = BLOCK_HEAD_RE.match(raw)
        if m:
            secs.append((lvl, head, cur))
            cur, lvl, head = [], len(m.group(1)), raw[m.end():].strip()
        else:
            cur.append(raw)
    secs.append((lvl, head, cur))
    return secs

def _markers(en):
    """The parts of an English block that survive into Italian unchanged, and
    so identify its counterpart: the digits, the acronyms (ZTL, STOP, ABS), and
    the Italian terms the English notes carry in italics (*zona a traffico
    limitato*). The last is by design, which makes it the strongest signal
    available, and far better than counting shared words: the two languages
    share so few that length ratio would otherwise decide, and once did, pairing
    a paragraph about parking garages to the Italian definition of a ZTL."""
    out = set(re.findall(r"\d[\d.,]*", en))
    out |= set(re.findall(r"\b[A-Z]{2,6}\b", en))
    for m in re.finditer(r"(?<!\*)\*([^*]+)\*(?!\*)", en):
        out |= {w for w in re.findall(r"[a-zà-ú]{4,}", m.group(1).lower())}
    return out

def _kin(a, b):
    """How alike two blocks are across the language barrier. Used only where
    the counts differ; equal counts pair straight across without scoring."""
    bl = b.lower()
    bw = set(re.findall(r"[a-zà-ú]{4,}", bl)) | set(re.findall(r"\d[\d.,]*", b)) | set(re.findall(r"\b[A-Z]{2,6}\b", b))
    hits = len(_markers(a) & bw)
    aw = set(re.findall(r"[a-zà-ú]{5,}", a.lower()))
    bw5 = set(re.findall(r"[a-zà-ú]{5,}", bl))
    overlap = len(aw & bw5) / max(min(len(aw), len(bw5)), 1)
    return 0.15 * hits + 0.6 * overlap + 0.05 * (min(len(a), len(b)) / max(len(a), len(b), 1))

def _align(xs, ys, text=lambda v: v, can_pair=lambda x, y: True):
    """Pair two sequences that are parallel but may have extra items on either
    side. Equal lengths pair straight across, which is the ordinary case and
    needs no guessing at all.

    Otherwise a small dynamic program maximises the total likeness. It carries
    a DIAGONAL PRIOR: the two languages are written in the same order, so the
    extras are few and the true pairing stays near the diagonal. Without it a
    block could pair with something far away that happened to share a word.
    A pairing that scores too low is dropped rather than forced, because a
    pill showing the wrong Italian is worse than a block with no pill."""
    if len(xs) == len(ys) and all(can_pair(x, y) for x, y in zip(xs, ys)):
        return list(zip(xs, ys))
    n, m = len(xs), len(ys)
    NEG = float("-inf")

    def score(i, j):
        if not can_pair(xs[i], ys[j]):
            return NEG
        drift = abs((i - j) - (n - m) / 2)
        return _kin(text(xs[i]), text(ys[j])) + 0.25 * max(0.0, 1 - drift / 3)

    best = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            sc = score(i - 1, j - 1)
            pair = best[i - 1][j - 1] + sc if sc != NEG else NEG
            best[i][j] = max(pair, best[i - 1][j], best[i][j - 1])
    out, i, j = [], n, m
    while i and j:
        sc = score(i - 1, j - 1)
        if sc != NEG and abs(best[i][j] - (best[i - 1][j - 1] + sc)) < 1e-9:
            if sc > 0.2:
                out.append((xs[i - 1], ys[j - 1]))
            i, j = i - 1, j - 1
        elif best[i][j] == best[i - 1][j]:
            i -= 1
        else:
            j -= 1
    return list(reversed(out))

def _hash(text):
    """FNV-1a, 32-bit, base36. Mirrored in app.js (reviewBlockHash). Short
    enough that the pairing costs a few bytes a block instead of a copy of the
    whole Italian text, which would double a file every offline install
    downloads."""
    h = 0x811C9DC5
    for ch in text:
        h = ((h ^ ord(ch)) * 0x01000193) & 0xFFFFFFFF
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    if not h:
        return "0"
    out = ""
    while h:
        out = digits[h % 36] + out
        h //= 36
    return out

def review_sync(en, it):
    """Check the two languages block for block, and return the pairing.

    Returns {pairs, en_gap, it_gap, sec_gap}. A gap is content that exists in
    one language and not the other, WITHOUT being declared English-only; it is
    a translation that was never written, or one that was written and then
    orphaned when its English was reworded. Either way the build should stop."""
    se, si = _sections(en), _sections(it)
    sec_al = _align(se, si, text=lambda s: " ".join(s[2]), can_pair=lambda x, y: x[0] == y[0])
    paired_e = {id(a) for a, _ in sec_al}
    paired_i = {id(b) for _, b in sec_al}
    out = {"pairs": {}, "en_gap": [], "it_gap": [], "sec_gap": []}

    it_blocks = []
    for _l, _h, lines in si:
        it_blocks += _text_blocks(lines)
    index_of = {}
    for i, b in enumerate(it_blocks):
        index_of.setdefault(b, i)

    for s in se:
        if id(s) not in paired_e and not _marked(s[1]):
            out["sec_gap"].append(("en", s[1]))
    for s in si:
        if id(s) not in paired_i:
            out["sec_gap"].append(("it", s[1]))

    for a, b in sec_al:
        if _marked(a[1]):
            continue
        ea_all = _text_blocks(a[2])
        ea = [x for x in ea_all if not _marked(x)]
        eb = _text_blocks(b[2])
        pr = _align([EN_ONLY_RE.sub("", x) for x in ea], eb)
        got_en = {x for x, _ in pr}
        got_it = {y for _, y in pr}
        for k, v in pr:
            out["pairs"].setdefault(_hash(k), index_of[v])
        for x in ea:
            if EN_ONLY_RE.sub("", x) not in got_en:
                out["en_gap"].append((a[1], x))
        for y in eb:
            if y not in got_it:
                out["it_gap"].append((b[1], y))
    return out

def build_pairs(en, it):
    """{ hash of English block: index of its Italian block } for one topic.

    Sections are aligned first, so any drift stays inside one short section.
    The value is an INDEX into the Italian blocks, in document order, which the
    app recomputes from the Italian markdown it already ships: storing the
    Italian text here instead would put every word of it in the file twice."""
    it_blocks = []
    for _lvl, _head, lines in _sections(it):
        it_blocks += _text_blocks(lines)
    index_of = {}
    for i, b in enumerate(it_blocks):
        index_of.setdefault(b, i)
    out = {}
    same_level = lambda x, y: x[0] == y[0]
    for a, b in _align(_sections(en), _sections(it),
                       text=lambda s: " ".join(s[2]), can_pair=same_level):
        en_blocks = [x for x in _text_blocks(a[2]) if not EN_ONLY_RE.match(x)]
        for k, v in _align(en_blocks, _text_blocks(b[2])):
            out.setdefault(_hash(k), index_of[v])
    return out

def bump_cache():
    s = SW.read_text(encoding="utf-8")
    m = re.search(r"patente-netfirst-(\d{8})([a-z])", s)
    if not m:
        print("  (could not find cache version to bump; do it manually)")
        return
    old = m.group(0)
    cur_date, cur_letter = m.group(1), m.group(2)
    today = datetime.date.today().strftime("%Y%m%d")
    # Never move the version backwards: keep the later of (current date, today).
    # YYYYMMDD compares chronologically as a string.
    new_date = max(cur_date, today)
    if new_date == cur_date:
        if cur_letter < "z":
            new_letter = chr(ord(cur_letter) + 1)
        else:
            # letters exhausted for this date: advance the date by one day, reset to 'a'
            nd = datetime.datetime.strptime(new_date, "%Y%m%d").date() + datetime.timedelta(days=1)
            new_date, new_letter = nd.strftime("%Y%m%d"), "a"
    else:
        new_letter = "a"
    new = f"patente-netfirst-{new_date}{new_letter}"
    SW.write_text(s.replace(old, new, 1), encoding="utf-8")
    print(f"  cache bumped: {old} -> {new}")

def main():
    if not MDDIR.exists():
        sys.exit("No topic_reviews_md/ folder. Run reviews_to_md.py first.")

    # Preferred order from the manifest; fall back to sorted filenames.
    manifest_path = MDDIR / "_manifest.json"
    default_source = "en"
    if manifest_path.exists():
        default_source, entries = load_manifest(manifest_path)
        order = [e["topic"] for e in entries]
        files = [MDDIR / e["file"] for e in entries]
    else:
        # No manifest: process the numbered NN-*.md files (skip README, which
        # intentionally contains example <!-- TOPIC --> markers).
        order = None
        files = [p for p in sorted(MDDIR.glob("*.md"))
                 if re.match(r"\d+-", p.name) and p.name.lower() != "readme.md"]

    parsed = {}
    sync_gaps = []
    src_overrides = {}            # topic -> source lang, when a file overrides the default
    for path in files:
        if not path.exists():
            sys.exit(f"Manifest references missing file: {path.name}")
        txt = path.read_text(encoding="utf-8")
        try:
            topic, en, it = parse_md(txt)
        except ValueError as e:
            sys.exit(f"Error in {path.name}: {e}")
        if topic in parsed:
            sys.exit(f"Duplicate topic '{topic}' (in {path.name})")
        en, claims, _absent, complete = extract_claims(en)
        sync = review_sync(en, it)
        # A claim must point at a translated block, or the Italian side would
        # have nowhere to land.
        for h, nums in claims.items():
            if h not in sync["pairs"]:
                sys.exit(f"Error in {path.name}: <!-- q: {' '.join(nums)} --> sits on a block "
                         f"with no Italian twin (English-only blocks cannot claim statements)")
        gaps = ([f"EN has no Italian, under {h!r}: {x[:70]}" for h, x in sync["en_gap"]]
                + [f"IT has no English, under {h!r}: {x[:70]}" for h, x in sync["it_gap"]]
                + [f"{lang.upper()}-only section: {h!r}" for lang, h in sync["sec_gap"]])
        if gaps:
            print(f"  SYNC GAP in {path.name} ({topic[:40]}):")
            for g in gaps:
                print(f"    {g}")
            sync_gaps.append(path.name)
        # claims ship as { statement: hash of its English block }; the app
        # finds the element by that hash and the Italian twin through pairs.
        entry = {"en": strip_markers(en), "it": it, "pairs": sync["pairs"]}
        if claims:
            entry["claims"] = {n: h for h, nums in claims.items() for n in nums}
        if complete == "complete":
            entry["complete"] = True
        elif complete == "rules":
            entry["rules"] = True
        parsed[topic] = entry
        # Per-file source override: a <!-- SOURCE: xx --> line in the header
        # (before the first LANG marker) wins over the manifest default. The
        # source language is metadata for translation tooling; the build packs
        # both languages regardless.
        en_m = EN_RE.search(txt)
        header = txt[:en_m.start()] if en_m else txt
        sm = SOURCE_RE.search(header)
        if sm and sm.group(1).lower() != default_source:
            src_overrides[topic] = sm.group(1).lower()

    if order:
        missing = [t for t in order if t not in parsed]
        extra   = [t for t in parsed if t not in order]
        if missing:
            sys.exit(f"Missing .md files for: {missing}")
        if extra:
            print(f"  note: new topics not in manifest, appended: {extra}")
        ordered = {t: parsed[t] for t in order}
        for t in extra:
            ordered[t] = parsed[t]
    else:
        ordered = parsed

    # The backup goes OUTSIDE public_html (2026-10-04): the maintainer uploads
    # that folder whole, so a backup written beside the JSON reached the server.
    if DEST.exists():
        BACKUP.write_text(DEST.read_text(encoding="utf-8"), encoding="utf-8")

    DEST.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")
    # sanity: valid JSON round-trips
    json.loads(DEST.read_text(encoding="utf-8"))
    print(f"Wrote {len(ordered)} topics -> {DEST}  (backup: {BACKUP.relative_to(ROOT)})")
    note = f"; per-file overrides: {src_overrides}" if src_overrides else ""
    print(f"  source language: {default_source}{note}")
    if sync_gaps:
        sys.exit(f"\nEnglish and Italian are out of sync in {len(sync_gaps)} file(s): "
                 f"{', '.join(sync_gaps)}\nWrite the missing translation, or mark the "
                 f"block English-only with a trailing <!-- en-only --> if it is "
                 f"scaffolding for the American reader.")
    bump_cache()
    # topic_reviews.json changed, so its content hash in app.js and sw.js
    # must follow, or the app would go on asking for the old bytes.
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "scripts" / "stamp_data_hashes.py")], check=True)

if __name__ == "__main__":
    main()
