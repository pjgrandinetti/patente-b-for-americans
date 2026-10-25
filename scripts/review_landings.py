#!/usr/bin/env python3
"""Where each statement's 📖 button lands in the concept review.

Mirrors the app: the card's (or statement's) anchor in review_anchors.json
names a section; inside it, pick_review_block chooses the one paragraph or
bullet the statement is about, when one stands clearly above the rest. This
script exists so the landings can be audited offline without clicking
through the app, and so the two implementations can be compared
(`--json` writes one row per statement; the node harness in the repo's
history did the comparison on 2026-09-12 and found them identical).

The token rules here MUST match pickTokens / pickReviewBlock in app.js.

Usage:
  python3 scripts/review_landings.py              # summary counts
  python3 scripts/review_landings.py --json OUT   # one row per statement
  python3 scripts/review_landings.py --topic 22   # print landings for a topic
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public_html"
sys.path.insert(0, str(ROOT / "scripts"))
import md_to_reviews as M  # noqa: E402

PICK_STOP = set((
    "della delle dello degli del dei alla alle allo agli nel nella nelle nei nello sul sulla "
    "sulle sui sullo con per che non una uno gli anche come sono essere deve devono può possono viene stato stata "
    "quando dove solo sempre mai dell nell sull dall dalla dalle dagli dallo ogni tutti tutte tutto tutta essa esso "
    "esse essi loro quale quali questo questa questi queste quello quella quelli quelle cioè oppure invece senza dopo "
    "prima tra fra verso circa tale tali caso casi modo parte sia siano stesso stessa altro altra altri altre proprio "
    "propria molto poco piu meno ancora quindi perche perché vale valere conducente conducenti veicolo veicoli strada "
    "strade segnale segnali").split(" "))


def pick_tokens(text):
    t = text.lower().replace("’", "'")
    out = {w[:6] for w in re.findall(r"[a-zà-ú]{4,}", t) if w not in PICK_STOP}
    out |= set(re.findall(r"\d[\d.,]*", t))
    return out


def blocks(md):
    """(ancestor headings, block text) for every text block, as the app's
    reviewBlocks builds them. The whole chain, not just the nearest heading:
    "## Towing a trailer" opens straight into "### Hooking up", so nothing
    sits directly under it."""
    out, stack = [], []
    for lvl, head, lines in M._sections(md):
        if lvl:
            while stack and stack[-1][0] >= lvl:
                stack.pop()
            stack.append((lvl, head.strip()))
        chain = [h for _, h in stack]
        for b in M._text_blocks(lines):
            out.append((chain, b))
    return out


class Reviews:
    def __init__(self, reviews):
        self.rev = reviews
        self.en = {t: blocks(v["en"]) for t, v in reviews.items()}
        self.it = {t: [b for _, b in blocks(v["it"])] for t, v in reviews.items()}
        self.hash_en = {t: [M._hash(b) for _, b in bl] for t, bl in self.en.items()}

    def section(self, topic, heading):
        """Indices of the EN blocks under `heading`, sub-sections included."""
        want = heading.strip()
        return [i for i, (chain, _) in enumerate(self.en[topic]) if want in chain]

    def pick(self, topic, heading, italian_text):
        """{'en': hash, 'it': hash} or None. Mirrors pickReviewBlock."""
        if not heading or not italian_text or "figura" in italian_text:
            return None
        v = self.rev.get(topic)
        if not v or not v.get("pairs"):
            return None
        cands = []
        for i in self.section(topic, heading):
            j = v["pairs"].get(self.hash_en[topic][i])
            if j is None or j >= len(self.it[topic]) or not self.it[topic][j]:
                continue
            it = self.it[topic][j]
            cands.append((self.hash_en[topic][i], M._hash(it), pick_tokens(it)))
        if not cands:
            return None
        st = pick_tokens(italian_text)
        df = Counter()
        for _, _, toks in cands:
            for w in st:
                if w in toks:
                    df[w] += 1
        n = len(cands)
        live = [w for w in st if not (n >= 4 and df[w] > n / 2)]
        denom = len(live) or 1
        scored = []
        for k, (hen, hit, toks) in enumerate(cands):
            shared = sum(1 for w in live if w in toks)
            scored.append((shared / denom, shared, k, hen, hit))
        # JS sorts by frac only and keeps document order for ties (stable sort).
        scored.sort(key=lambda s: -s[0])
        best = scored[0]
        second = scored[1][0] if len(scored) > 1 else 0
        # Mirrors pickReviewBlock: a wide enough gap OR a two-to-one win, since
        # the gap is a share of the statement's words and a long statement
        # divides every gap down.
        def clear(need):
            return best[0] - second >= need or (second > 0 and best[0] >= 2 * second)
        ok = (best[1] >= 3 and best[0] >= 0.2 and clear(0.1)) or \
             (best[1] == 2 and best[0] >= 0.25 and clear(0.15))
        return {"en": best[3], "it": best[4]} if ok else None

    def sentence(self, topic, hashes, italian_text):
        """Which sentence of the landed block carries the rule, or None.
        Mirrors reviewSentenceIndex in app.js: chosen on the Italian, reused
        for the English, and only when both split the same number of ways."""
        if not hashes or not hashes.get("it") or not italian_text:
            return None
        src = {M._hash(b): b for _, b in self.en[topic]}
        it_src = {M._hash(b): b for _, b in blocks(self.rev[topic]["it"])}
        en_b, it_b = src.get(hashes["en"]), it_src.get(hashes["it"])
        if en_b is None or it_b is None:
            return None
        its, ens = sentences(it_b), sentences(en_b)
        if len(its) < 2 or len(its) != len(ens):
            return None
        st = list(pick_words(italian_text))
        per = [pick_words(s) for s in its]
        n = len(per)
        live = []
        for w in st:
            df = sum(1 for words in per if word_hit(w, words))
            if df >= 1 and not (n >= 3 and df > n / 2):
                live.append(w)
        best, best_n, second_n = -1, 0, 0
        for i, words in enumerate(per):
            hits = sum(1 for w in live if word_hit(w, words))
            if hits > best_n:
                best_n, second_n, best = hits, best_n, i
            elif hits > second_n:
                second_n = hits
        return best if best_n >= 1 and best_n > second_n else None


SENT_ABBR = {"art", "artt", "es", "ecc", "ca", "pag", "fig", "sig", "dott",
             "prof", "lett", "cfr", "n", "nn", "e.g", "i.e", "st", "vs"}


def pick_words(text):
    """Whole words, for the sentence step. Mirrors pickWords in app.js."""
    t = text.lower().replace("’", "'")
    out = {w for w in re.findall(r"[a-zà-ú]{4,}", t) if w not in PICK_STOP}
    out |= set(re.findall(r"\d[\d.,]*", t))
    return out


def word_hit(word, words):
    """Mirrors wordHit in app.js: equal, or one a prefix of the other with at
    least five letters shared."""
    if word in words:
        return True
    if len(word) < 5:
        return False
    for w in words:
        if len(w) < 5:
            continue
        if (w.startswith(word) if len(w) > len(word) else word.startswith(w)):
            return True
    return False


def plain_text(src):
    """The block as it reads on screen: the renderer only strips inline
    markup. Mirrors reviewPlainText in app.js."""
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", src).replace("*", "")


def sentences(src):
    """Mirrors reviewSentences in app.js: split at .!? plus space plus a
    capital, but never inside an initial (T.A.T.S.), an abbreviation (art.,
    e.g.) or a decimal (3.5 t)."""
    t = plain_text(src)
    out, start = [], 0
    for m in re.finditer(r"[.!?][\"')\]]*\s+(?=[A-ZÀ-Ú0-9«\"])", t):
        before = t[:m.start()]
        w = re.split(r"[\s(]", before)[-1]
        if (len(w) <= 1 or w.lower().rstrip(".") in SENT_ABBR
                or re.search(r"\d$", before) or re.search(r"(?:\b[A-Z]\.)+$", before)):
            continue
        out.append(t[start:m.end()].strip())
        start = m.end()
    tail = t[start:].strip()
    if tail:
        out.append(tail)
    return [s for s in out if s]


def anchor_for(anchors, card, number):
    a = anchors.get(str(card["id"]))
    if a is None and card.get("base_id") is not None:
        a = anchors.get(str(card["base_id"]))
    if not a:
        return None
    own = (a.get("stmts") or {}).get(str(number))
    if not own:
        return a
    # Mirrors reviewAnchorFor in app.js: an entry naming neither a section nor
    # a figure refines the card's anchor with a paragraph inside it.
    if not own.get("en") and not own.get("img"):
        merged = {k: v for k, v in a.items() if k != "stmts"}
        merged.update(own)
        return merged
    return own


def landings(reviews, questions, anchors):
    """Mirrors the app's target choice: a CLAIM in the review markdown first
    (`<!-- q: N -->`, any topic), then an explicit `block` anchor, then the
    picker, and the picker only for a topic not yet marked complete."""
    R = Reviews(reviews)
    claims = {}
    for t, v in reviews.items():
        for n, h in (v.get("claims") or {}).items():
            claims[n] = (t, h)
    heads = {t: {M._hash(b): (chain[-1] if chain else "") for chain, b in R.en[t]} for t in reviews}
    rows = []
    for c in questions:
        for s in c["statements"]:
            an = anchor_for(anchors, c, s["number"])
            block, topic, heading = None, None, None
            if s["number"] in claims:
                topic, h = claims[s["number"]]
                j = reviews[topic]["pairs"].get(h)
                block = {"en": h, "it": M._hash(R.it[topic][j]) if j is not None else None, "explicit": True, "claim": True}
                heading = heads[topic].get(h, "")
            elif an and an.get("en"):
                topic = an.get("topic", c["topic"])
                if topic not in reviews:
                    continue
                heading = an["en"]
                if an.get("block"):
                    j = reviews[topic]["pairs"].get(an["block"])
                    block = {"en": an["block"], "it": M._hash(R.it[topic][j]) if j is not None else None, "explicit": True}
                elif not reviews[topic].get("complete"):
                    block = R.pick(topic, an["en"], s["italian_text"])
            else:
                continue
            if block:
                block["sent"] = R.sentence(topic, block, s["italian_text"])
            rows.append({"number": s["number"], "card": c["id"], "answer": s["answer"], "topic": topic,
                         "heading": heading, "block": block, "italian_text": s["italian_text"]})
    return R, rows


def main(argv):
    reviews = json.loads((PUB / "topic_reviews.json").read_text(encoding="utf-8"))
    questions = json.loads((PUB / "questions.json").read_text(encoding="utf-8"))
    anchors = json.loads((PUB / "review_anchors.json").read_text(encoding="utf-8"))
    R, rows = landings(reviews, questions, anchors)
    if "--json" in argv:
        out = Path(argv[argv.index("--json") + 1])
        out.write_text(json.dumps(rows, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"wrote {len(rows)} rows to {out}")
        return
    if "--topic" in argv:
        want = argv[argv.index("--topic") + 1]
        by_hash = {t: {M._hash(b): b for _, b in R.en[t]} for t in R.en}
        for r in rows:
            if not (r["topic"].startswith(want) or want in r["topic"]):
                continue
            where = by_hash[r["topic"]].get(r["block"]["en"], "?")[:110] if r["block"] else "(heading)"
            print(f"#{r['number']} {r['answer']}  {r['italian_text'][:90]}\n    -> {r['heading']} | {where}")
        return
    picked = [r for r in rows if r["block"]]
    claimed = sum(1 for r in picked if r["block"].get("claim"))
    print(f"{len(rows)} statements on anchored sections; {len(picked)} land on a paragraph "
          f"({claimed} claimed in the review, "
          f"{sum(1 for r in picked if r['block'].get('explicit')) - claimed} explicit anchors, "
          f"{len(picked) - sum(1 for r in picked if r['block'].get('explicit'))} picked)")
    for ans in ("VERO", "FALSO"):
        n = sum(1 for r in rows if r["answer"] == ans)
        p = sum(1 for r in picked if r["answer"] == ans)
        print(f"  {ans}: {p}/{n} = {100 * p / max(n, 1):.1f}%")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except BrokenPipeError:
        # `--topic` output is long and normally read through `head`.
        sys.stderr.close()
