#!/usr/bin/env python3
"""
Stamp `f`, the bank frequency, onto every entry of public_html/glossary.json.

`f` is the number of LIVE statements the term appears in, which is what the
Glossario's "Più frequenti" order sorts by. It is the same quantity, counted
the same way, as vocabulary.json's own `f`: `entry_regex` is imported from
consolidate_vocab.py rather than reimplemented, so the glossary cannot drift
away from the matcher the app uses. That regex wildcards the final unaccented
vowel of each word longer than three letters, so one entry covers its inflected
family (`corsia` counts `corsie` too), and it drops a vowel that would turn the
term into ANOTHER entry of the same file, so two glossary headwords cannot
swallow each other.

Retired statements are excluded. A withdrawal therefore lowers a count, which
is the point: the number tells a reader how often they will actually meet the
word, not how often the Ministry once used it.

Run after editing glossary.json, then bump the version. validate_data.py
recomputes the counts and FAILS if the shipped file is stale, so a forgotten
run is caught rather than shipped.

Usage:
    python3 scripts/glossary_freq.py            # report only
    python3 scripts/glossary_freq.py --apply    # write the counts
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from consolidate_vocab import entry_regex          # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GLOSS = ROOT / "public_html" / "glossary.json"
BANK = ROOT / "public_html" / "questions.json"


def live_statements(bank):
    """Every statement a learner can still meet, LOWERCASED.

    The case fold is not cosmetic. `entry_regex` builds its pattern from the
    lowercased term and compiles it WITHOUT re.I, while the app compiles the
    same pattern with the 'gi' flags, so only a lowercased haystack counts what
    the learner actually sees underlined. consolidate_vocab.py has always
    lowercased here and this script did not, which reported f = 0 for a word the
    bank only ever writes capitalised (Motorizzazione, ABS) and undercounted
    every term a statement happens to open with.
    """
    return [s["italian_text"].lower() for q in bank
            for s in q.get("statements", []) if not s.get("retired")]


def counts(gloss, bank):
    """{term: statements it appears in}, by the app's own matching rule."""
    texts = live_statements(bank)
    known = {e["t"].lower().strip() for e in gloss["entries"]}
    out = {}
    for e in gloss["entries"]:
        rx = entry_regex(e["t"], known)
        out[e["t"]] = sum(1 for t in texts if rx.search(t))
    return out


def main():
    apply = "--apply" in sys.argv
    gloss = json.loads(GLOSS.read_text(encoding="utf-8"))
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    f = counts(gloss, bank)

    changed = [e["t"] for e in gloss["entries"] if e.get("f") != f[e["t"]]]
    zero = sorted(t for t, n in f.items() if n == 0)

    for t, n in sorted(f.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"{n:5}  {t}")
    print(f"\n{len(f)} entries, {len(changed)} with a new count")
    # A zero means the headword is never met in the shape the matcher looks
    # for. That is either a word the bank does not use (it should not be in
    # the glossary at all) or a form mismatch worth seeing.
    if zero:
        print(f"NEVER MET in the live bank: {', '.join(zero)}")

    if not apply:
        if changed:
            print("\n(report only; re-run with --apply to write)")
        return
    for e in gloss["entries"]:
        e["f"] = f[e["t"]]
        # Keep a stable key order so a re-run produces no spurious diff.
        for k in ("d", "src", "f"):
            if k in e:
                e[k] = e.pop(k)
    GLOSS.write_text(json.dumps(gloss, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"\nwrote {GLOSS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
