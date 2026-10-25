#!/usr/bin/env python3
"""
Glossary rule 14: a vocabulary gloss translates, it does not teach.

Flags vocabulary glosses that explain a driving concept, give exam advice, or
repeat grammar that belongs in the `gram` field. A short sense disambiguator
("(e.g., speed limit)") is fine and is not flagged.

Usage:  python3 scripts/check_vocab_glosses.py
"""
import json
import re
import sys
from pathlib import Path

VOCAB = Path(__file__).resolve().parent.parent / "public_html" / "vocabulary.json"

# Prose that teaches instead of translating.
TEACH = re.compile(
    r"(which the exam|the exam treats|on the quiz|americans? (?:call|know|read|should)|"
    r"us drivers|you must not|is wrong|remember that|note that|so that it|"
    r"can give way|this is why)", re.I)
# Grammar belongs in `gram`, not in the English gloss.
GRAM = re.compile(
    r"\((?:past participle|participio|subjunctive|congiuntivo|gerund|gerundio|"
    r"infinitive|infinito)[^)]*\)", re.I)
# A word-for-word rendering of an idiom, e.g. "high beams (literally: dazzling
# lights)". This is still translation, not teaching: it shows the learner what
# the individual Italian words say when the phrase as a whole says something
# else. It is exempt from the length test, which exists to catch glosses that
# have turned into driving lessons, and the natural translation in front of it
# is measured on its own.
LITERAL = re.compile(r"\s*\((?:literally|lit\.):[^)]*\)\s*$", re.I)


def main():
    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
    entries = list(vocab["common"])
    for topic in vocab.get("topics", {}).values():
        entries += topic.get("vocabulary", [])

    bad = []
    for e in entries:
        gloss = e.get("en", "")
        if TEACH.search(gloss):
            bad.append((e["term"], gloss, "teaches instead of translating"))
        elif GRAM.search(gloss):
            bad.append((e["term"], gloss, "grammar belongs in the `gram` field"))
        elif len(LITERAL.sub("", gloss)) > 80:
            bad.append((e["term"], gloss, "too long for a translation"))

    if bad:
        print(f"Rule 14 defects: {len(bad)} gloss(es) explain rather than translate:")
        for term, gloss, why in bad[:20]:
            print(f"  - {term}: {gloss[:70]!r}  ({why})")
        if len(bad) > 20:
            print(f"  … and {len(bad) - 20} more")
        return 1
    print(f"✓ rule 14: all {len(entries)} glosses are translations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
