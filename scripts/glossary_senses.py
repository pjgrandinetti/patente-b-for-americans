#!/usr/bin/env python3
"""
Show how the BANK actually uses each Glossario headword, so an entry that
misses a sense is caught by reading rather than by luck.

This exists because `raccordo` shipped defined only as a stretch of road
linking two roads, while three statements use it for the curb ramp between
sidewalk and roadway, in the rule about where parking is forbidden. The entry
was not wrong, it was incomplete, and nothing in the build could see that.

For every entry it collects the live statements the app's own matcher would
underline, groups them by the words on either side of the hit, and prints the
distinct collocations. An entry whose hits all share one collocation is almost
certainly single-sense; one with several unrelated ones is worth reading.

    python3 scripts/glossary_senses.py              # only the entries to look at
    python3 scripts/glossary_senses.py --all        # every entry
    python3 scripts/glossary_senses.py carreggiata  # one entry, with statements
"""
import json
import re
import sys
import collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from consolidate_vocab import entry_regex          # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GLOSS = ROOT / "public_html" / "glossary.json"
BANK = ROOT / "public_html" / "questions.json"

# Words that say nothing about which sense is meant, so they are stripped from
# a collocation before it is compared. Without this every hit looks distinct.
STOP = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "l", "un'",
    "di", "del", "dello", "della", "dei", "degli", "delle", "d",
    "a", "al", "allo", "alla", "ai", "agli", "alle",
    "da", "dal", "dalla", "dai", "dalle", "in", "nel", "nella", "nei", "nelle",
    "con", "su", "sul", "sulla", "sui", "sulle", "per", "tra", "fra",
    "e", "o", "che", "non", "si", "e'", "è", "ed", "se", "come",
}


def live_statements(bank):
    return [(q["topic"], s["italian_text"]) for q in bank
            for s in q.get("statements", []) if not s.get("retired")]


def collocation(text, m):
    """The nearest meaningful word on each side of the hit."""
    before = [w for w in re.findall(r"[a-zà-ù']+", text[:m.start()].lower())
              if w not in STOP]
    after = [w for w in re.findall(r"[a-zà-ù']+", text[m.end():].lower())
             if w not in STOP]
    return (before[-1] if before else "^", after[0] if after else "$")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    show_all = "--all" in sys.argv
    gloss = json.loads(GLOSS.read_text(encoding="utf-8"))
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    stmts = live_statements(bank)
    known = {e["t"].lower() for e in gloss["entries"]}

    flagged = 0
    for e in gloss["entries"]:
        if args and e["t"] not in args:
            continue
        rx = entry_regex(e["t"], known)
        hits = []
        for topic, text in stmts:
            for m in rx.finditer(text):
                hits.append((collocation(text, m), topic, text))
        if not hits:
            continue
        cols = collections.Counter(c for c, _, _ in hits)
        topics = {t for _, t, _ in hits}
        # Worth a read when the word keeps different company REPEATEDLY. A
        # first attempt flagged 141 of 151 by counting distinct collocations,
        # which is just the natural variety of prose; a second sense shows up
        # as two or more collocations that each recur, with different words
        # after the term. Singletons are noise and are ignored.
        repeated = [c for c, n in cols.items() if n >= 2]
        afters = {a for _, a in repeated}
        interesting = len(repeated) >= 2 and len(afters) >= 2
        if not (interesting or show_all or args):
            continue
        flagged += 1
        print(f"\n=== {e['t']}  ({len(hits)} hits, {len(topics)} topics)")
        print(f"    {e['d'][:96]}")
        for (b, a), n in cols.most_common(6):
            print(f"      {n:3}  ...{b} [{e['t']}] {a}...")
        if args:
            for _, topic, text in hits[:12]:
                print(f"      [{topic[:24]}] {text[:112]}")
    if not args:
        print(f"\n{flagged} entries worth reading"
              f" of {len(gloss['entries'])}")


if __name__ == "__main__":
    main()
