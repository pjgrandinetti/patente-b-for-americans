#!/usr/bin/env python3
"""Retranslate the verb 'preavvisa/preavvisare' on non-hazard signs.

The blanket translation rendered the Italian verb 'preavvisare' (to give
advance notice of) as "warns of". That reads as a danger warning, which is
wrong for direction and information signs. This script rewrites those English
translations to use "indicates the upcoming ...", leaving:
  - 'Segnali di pericolo' (genuine warning signs) untouched, and
  - the noun form 'preavviso' / 'segnale di preavviso' (correct terminology)
    untouched.
"""
import json
import re
import sys

PATH = 'public_html/questions.json'

# Italian verb form (conjugated / infinitive), not the noun "preavviso".
VERB_RE = re.compile(r'preavvis(?:a|are|ano)\b', re.I)


def fix_english(en: str) -> str:
    out = en

    # Hand-mapped special cases (reordering or clause restructuring).
    special = {
        'The sign shown warns on the right of a level crossing without barriers':
            'The sign shown indicates the upcoming level crossing without barriers on the right',
        'The displayed sign warns trucks to move to the right lane to avoid an obstacle':
            'The displayed sign indicates that trucks should move to the right lane to avoid an obstacle',
    }
    if out in special:
        return special[out]

    # Infinitive constructions: "preavvisa di svoltare/proseguire ..."
    out = re.sub(r'\bwarns to turn (left|right)\b',
                 r'indicates the upcoming \1 turn', out, flags=re.I)
    out = re.sub(r'\bwarns to turn at\b',
                 'indicates the upcoming turn at', out, flags=re.I)
    out = re.sub(r'\bwarns to (?:go|continue) straight\b',
                 'indicates the upcoming straight-ahead route', out, flags=re.I)

    # "that" clauses: "preavvisa che ..." / "preavvisa l'interruzione ..."
    out = re.sub(r'\b(?:pre-warns|warns) that\b', 'indicates that', out, flags=re.I)
    out = re.sub(r'\bgives advance warning that\b', 'indicates that', out, flags=re.I)

    # Infinitive "to provide advance warning of ..." (per preavvisare ...).
    out = re.sub(r'\bto provide advance warning of\s+(?:a |an |the )?',
                 'to indicate the upcoming ', out, flags=re.I)

    # Noun-object constructions: drop the article so "indicates the upcoming"
    # reads correctly.
    out = re.sub(r'\b(?:pre-warns of|warns of|provides advance warning of|'
                 r'provide advance warning of|gives advance warning of|preavises)'
                 r'\s+(?:a |an |the )?',
                 'indicates the upcoming ', out, flags=re.I)

    # "indicates the upcoming two ..." reads awkwardly; move the number out.
    out = re.sub(r'\bthe upcoming (two|three|four) ', r'\1 upcoming ', out)

    return out


def main():
    apply = '--apply' in sys.argv
    with open(PATH, encoding='utf-8') as f:
        data = json.load(f)

    changes = 0
    unchanged = []
    for q in data:
        if q.get('topic') == 'Segnali di pericolo':
            continue
        for s in q.get('statements', []):
            it = s.get('italian_text', '')
            if not VERB_RE.search(it):
                continue
            en = s.get('english_translation', '')
            new = fix_english(en)
            if new != en:
                changes += 1
                print(f"- {en}\n+ {new}\n")
                s['english_translation'] = new
            else:
                unchanged.append((q.get('topic', ''), it, en))

    print(f"\n=== {changes} translations changed ===")
    if unchanged:
        print(f"\n=== {len(unchanged)} verb-form entries left UNCHANGED (review) ===")
        for topic, it, en in unchanged:
            print(f"[{topic[:25]}]\n  IT: {it}\n  EN: {en}\n")

    if apply:
        with open(PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print('WROTE', PATH)


if __name__ == '__main__':
    main()
