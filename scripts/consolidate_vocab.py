#!/usr/bin/env python3
"""
Consolidate the look-up vocabulary: phrases over single words.

Run this after adding a batch of phrase entries to public_html/vocabulary.json.
It simulates the app's matcher (longest-first, final-vowel wildcard) over every
statement in the question bank and then:

  1. finds entries that NEVER fire, because a longer entry always covers them;
  2. inverts the bad cases, where a determiner-led phrase ("un sinistro
     stradale") shadows the better bare term ("sinistro stradale") — the bare
     term is kept and the determiner-led variant dropped;
  3. removes the remaining dead entries;
  4. APPENDS a rule to vocabulary.json's `replaced_by` map for each removed
     entry that a phrase took over.

`replaced_by` drives the in-app migration of each user's saved vocabulary
(app.js -> migrateLookupsToPhrases): the old row is replaced by the phrase,
carrying its look-up and deletion clocks so nothing is lost and the change
syncs across devices.

RULES FOR MAINTAINERS
  - `replaced_by` is APPEND-ONLY. A user who skips several releases must still
    find their rule when they finally update, so never delete or rewrite an
    existing rule. This script only adds.
  - Chained rules are fine (word -> phrase A, later phrase A -> phrase B); the
    app follows the chain to its end, with a cycle guard.
  - Always re-run scripts/validate_data.py afterwards, and bump the version.

Usage:
    python3 scripts/consolidate_vocab.py            # report only
    python3 scripts/consolidate_vocab.py --apply    # write the changes
"""
import json
import re
import sys
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOCAB = ROOT / "public_html" / "vocabulary.json"
BANK = ROOT / "public_html" / "questions.json"

DET = (r"^(?:il|lo|la|i|gli|le|un|uno|una|l'|un'|nel|nella|nei|negli|nelle|"
       r"del|della|dei|degli|delle|al|alla|ai|agli|alle|dal|dalla|sul|sulla)\s+")


def entry_regex(term, known=frozenset()):
    """Mirror app.js (highlightVocabInEscaped): word boundaries, and the final
    unaccented vowel of EVERY word longer than three letters wildcarded, so one
    entry covers the whole inflected family ("centro abitato" also matches
    "centri abitati").

    `known` is the set of ALL terms (lowercase, single-spaced). For each word,
    the wildcard drops any vowel that would turn the whole term into another
    existing entry, so "obbligo" no longer captures "obbliga" once "obbliga"
    is an entry of its own, and "prima dei" no longer captures "primo dei"
    (the noun/verb and near-form collisions the 2026-09-11 gloss audit found)."""
    words = term.lower().split()
    parts = re.split(r"(\s+)", term.lower())
    out = []
    for part in parts:
        if re.fullmatch(r"\s+", part):
            out.append(r"\s+")
            continue
        p = re.escape(part)
        if len(part) > 3 and re.search(r"[oaei]$", part):
            wi = words.index(part)
            cls = ""
            for v in "oaei":
                if v == part[-1]:
                    cls += v
                    continue
                alt = list(words); alt[wi] = part[:-1] + v
                if " ".join(alt) not in known:
                    cls += v
            p = p[:-1] + "[" + cls + "]"
            # An -io noun makes its plural by DROPPING the vowel, not by
            # swapping it: rimorchio -> rimorchi, incrocio -> incroci. The
            # class above cannot express that, so the vowel becomes optional
            # for those words only. Without this, 25 vocabulary entries missed
            # their own plural over 266 statements (binari, incroci, specchi,
            # spazi), and the learner tapping one was shown nothing at all.
            # Guarded the same way as the class: if the bare stem is itself an
            # entry, the option is refused so the two cannot capture each other.
            if part.endswith("io"):
                alt = list(words); alt[wi] = part[:-1]
                if " ".join(alt) not in known:
                    p += "?"
        out.append(p)
    return re.compile(r"(?<![\wÀ-ɏ])(" + "".join(out) + r")(?![\wÀ-ɏ])")


def all_entries(vocab):
    out = list(vocab["common"])
    for topic in vocab.get("topics", {}).values():
        out += topic.get("vocabulary", [])
    return out


def main():
    apply = "--apply" in sys.argv
    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    # A statement the Ministry has withdrawn carries `retired` and never
    # reaches the learner, so a gloss that fires only there glosses nothing and
    # its `f` count would overstate how often the word is really met. Counting
    # over the live statements only is what found the nine dead entries on
    # 2026-09-15. See CLAUDE.md, "Withdrawn statements".
    texts = [s["italian_text"].lower() for q in bank for s in q["statements"]
             if not s.get("retired")]

    entries = sorted(all_entries(vocab), key=lambda e: -len(e["term"]))
    known = frozenset(" ".join(e["term"].lower().split()) for e in entries)
    pats = [(e, entry_regex(e["term"], known)) for e in entries]

    fires = collections.Counter()   # per STATEMENT: in how many statements does
    shadow = collections.defaultdict(collections.Counter)   # the entry fire?
    for text in texts:
        cover = [None] * len(text)
        fired_here = set()
        for e, p in pats:                       # longest-first, as the app does
            for m in p.finditer(text):
                span = range(m.start(), m.end())
                if any(cover[i] is not None for i in span):
                    continue
                for i in span:
                    cover[i] = e["term"]
                fired_here.add(e["term"])
        for t in fired_here:
            fires[t] += 1
        for e, p in pats:                       # who covered the losers' spans
            if fires[e["term"]]:
                continue
            for m in p.finditer(text):
                for w in {cover[i] for i in range(m.start(), m.end()) if cover[i]}:
                    if w != e["term"]:
                        shadow[e["term"]][w] += 1

    dead = [e["term"] for e, _ in pats if fires[e["term"]] == 0]

    # (2) invert determiner-led shadowing: keep the bare term, drop the variant
    invert = {}
    for term in dead:
        if not shadow[term]:
            continue
        winner = shadow[term].most_common(1)[0][0]
        core = re.sub(DET, "", winner, flags=re.I).strip()
        if core == term:
            invert[term] = winner

    drop = set(dead) - set(invert) | set(invert.values())
    rules = {t: shadow[t].most_common(1)[0][0]
             for t in dead if t not in invert and shadow[t]}

    print(f"entries            : {len(entries)}")
    print(f"never fire (dead)  : {len(dead)}")
    print(f"determiner inverts : {len(invert)} (bare term kept, variant dropped)")
    print(f"to remove          : {len(drop)}")
    print(f"new replace rules  : {len(rules)}")
    for k, v in list(rules.items())[:10]:
        print(f"    {k}  ->  {v}")
    if not apply:
        print("\n(report only — re-run with --apply to write)")
        return

    existing = vocab.get("replaced_by", {})
    added = 0
    for k, v in rules.items():
        if k not in existing:            # APPEND-ONLY: never overwrite a rule
            existing[k] = v
            added += 1
    vocab["replaced_by"] = existing
    vocab["common"] = [e for e in vocab["common"] if e["term"] not in drop]
    for topic in vocab.get("topics", {}).values():
        topic["vocabulary"] = [e for e in topic.get("vocabulary", [])
                               if e["term"] not in drop]
    # Stamp each entry's effective frequency: the number of statements in which
    # this entry actually matches (longest-first, like the app). The
    # vocabulary screen sorts by it in "Most frequent" order.
    for e in all_entries(vocab):
        e["f"] = fires.get(e["term"], 0)
    VOCAB.write_text(json.dumps(vocab, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    total = len(all_entries(vocab))
    phrases = sum(1 for e in all_entries(vocab) if " " in e["term"])
    print(f"\nwrote {VOCAB.relative_to(ROOT)}: {total} entries ({phrases} phrases), "
          f"{added} new rules, {len(existing)} rules total")
    print("next: python3 scripts/validate_data.py, then bump the version")


if __name__ == "__main__":
    main()
