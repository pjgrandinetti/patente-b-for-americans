#!/usr/bin/env python3
"""What the misses at one level have in common, from an exported progress file.

    python3 scripts/weak_spot_analysis.py ~/Downloads/patente-progress-2026-09-19.patente
    python3 scripts/weak_spot_analysis.py FILE --level 2
    python3 scripts/weak_spot_analysis.py FILE --list "Segnali di precedenza"

The export (Settings -> "Export progress") is JSON despite its extension, and
carries the per-level progress maps, so the whole analysis runs offline against
`questions.json` and `topic_reviews.json`. Nothing is sent anywhere and the app
needs no instrumentation: this is a reading of data the app already keeps.

WHAT A RECORD HOLDS, and what it does not. Per level, per statement:
`{seen, correct, streak, given}`. So a miss is `seen > correct`, and that is
the definition of "missed" used throughout. There is NO per-answer history: the
order of answers, the date of an individual miss, and the time taken are not
stored, so nothing here can speak to "I answered too fast".

TWO TRAPS IN THE ARITHMETIC, both of which have bitten:

1. `liftCredit` writes SYNTHETIC records into the lower levels. A correct
   answer at L3 copies `correct` and `streak` down to L2 and L1 and sets
   `seen = max(seen, correct)`, so a lower-level record can describe a
   statement never answered there. `seen > correct` at a lower level is still
   trustworthy (the lift only ever adds correct answers, never misses), which
   is why the ladder section below asks only that question and never treats
   "clean at L2" as proof the learner answered it at L2.

2. Base rates decide everything. "You missed 43 statements in Segnali di
   pericolo" means nothing next to its 662 statements. Every section here
   reports its own denominator, and the comparison group is always the
   statements the learner REACHED at the same level, never the whole bank.

Counts get small fast. With one learner a lift computed over a few hundred
candidate vocabulary terms will throw up large ratios by chance, so the word
section prints the raw counts beside every lift and applies a floor. Read it as
a shortlist to eyeball, not as a result.
"""
import json
import re
import sys
import collections
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public_html"
sys.path.insert(0, str(ROOT / "scripts"))

# The app's own trap-word list (TRAP_IT_RE in app.js), which bolds the words
# that flip an answer at L1 and L2 and leaves them plain at L3. Kept in step by
# hand; if app.js gains a word, add it here or this section silently drifts.
TRAP_RE = re.compile(
    r'(?<![\wÀ-ɏ])('
    r'vietat[oaei]|consentit[oaei]|permess[oaei]|obbligator[ioaei]+|obblig[oaei]|'
    r'viet[ao]no|viet[ao]|consent[ao]no|consente|permett[ao]no|permette|'
    r'sempre|mai|sol[oa]|soltanto|esclusivamente|unicamente|limitarsi|limitandosi|'
    r'si limita|basta|anche|salvo|purché|tranne|eccetto|almeno|entro|'
    r'semplicemente|unico obbligo|facoltativ[oaei]|'
    r'di mezzo|central[ei]|di sinistra|di destra|a sinistra|a destra'
    r')(?![\wÀ-ɏ])', re.I)


def binom_tail(k, n, p=0.5):
    """P(X >= k) for n fair trials: is a split worth reading at all?"""
    return sum(comb(n, i) * p ** n for i in range(k, n + 1))


def load_bank():
    q = json.loads((PUB / "questions.json").read_text(encoding="utf-8"))
    bank = {}
    for c in q:
        for s in c["statements"]:
            if s.get("retired"):
                continue
            bank[str(s["number"])] = {
                "answer": s["answer"], "topic": c["topic"], "card": c["id"],
                "it": s["italian_text"], "en": s.get("english_translation", ""),
            }
    return bank


def level_records(bundle, lvl, bank):
    out = {}
    for _cid, v in (bundle["progress"].get("L%d" % lvl) or {}).items():
        for n, r in (v.get("st") or {}).items():
            if n in bank:
                out[n] = r
    return out


def missed(r):
    return (r.get("seen") or 0) > (r.get("correct") or 0)


def main(argv):
    if not argv:
        sys.exit(__doc__)
    path = Path(argv[0])
    lvl = int(argv[argv.index("--level") + 1]) if "--level" in argv else 3
    bundle = json.loads(path.read_text(encoding="utf-8"))
    bank = load_bank()
    R = {l: level_records(bundle, l, bank) for l in (1, 2, 3)}
    cur = R[lvl]
    reached = [n for n, r in cur.items() if (r.get("seen") or 0) > 0]
    if not reached:
        sys.exit(f"no answers recorded at L{lvl} in {path.name}")
    miss = [n for n in reached if missed(cur[n])]
    clean = [n for n in reached if not missed(cur[n])]
    seen = sum(cur[n].get("seen") or 0 for n in reached)
    corr = sum(cur[n].get("correct") or 0 for n in reached)

    print(f"{path.name}  exported {bundle.get('exportedAt')}\n")
    print(f"LEVEL {lvl}: {len(reached)} statements reached, {len(miss)} ever missed "
          f"({100*len(miss)/len(reached):.1f}%), {seen} answers at {100*corr/max(seen,1):.1f}% accuracy")
    for other in (1, 2, 3):
        if other == lvl:
            continue
        rs = [r for r in R[other].values() if (r.get("seen") or 0) > 0]
        if rs:
            s = sum(r.get("seen") or 0 for r in rs); c = sum(r.get("correct") or 0 for r in rs)
            print(f"  (L{other}: {len(rs)} reached, {100*c/max(s,1):.1f}% accuracy)")

    # ── 1. The ladder: did the scaffolded levels already know about this? ──
    # Only "missed at L1/L2" is trusted; see trap 1 in the docstring.
    def was_shaky(n):
        return any(R[l].get(n) and missed(R[l][n]) for l in (1, 2) if l < lvl)

    new = [n for n in miss if not was_shaky(n)]
    old = [n for n in miss if was_shaky(n)]
    base = sum(1 for n in reached if was_shaky(n))

    # The lift ERASES a lower miss when it raises `correct` as high as `seen`
    # (liftStatement: correct = max(...), seen = max(seen, correct)). The scar
    # it leaves is a lower record answered twice or more that now shows no
    # miss at all, so "clean lower" is an over-count by up to that many. The
    # control line says how often the same signature appears among statements
    # NOT missed here: if the two are close, the signature is innocent.
    def erased(n):
        for l in (1, 2):
            if l >= lvl:
                continue
            r = R[l].get(n) or {}
            if (r.get("seen") or 0) >= 2 and (r.get("correct") or 0) == (r.get("seen") or 0):
                return True
        return False

    if lvl > 1:
        susp = sum(1 for n in new if erased(n))
        ctrl = sum(1 for n in clean if erased(n))
        print(f"\nTHE LADDER (was this already shaky when the English was there?)")
        print(f"  already missed at a lower level : {len(old):4} of {len(miss)} misses "
              f"({100*len(old)/len(miss):.0f}%)")
        print(f"  clean at every lower level      : {len(new):4} ({100*len(new)/len(miss):.0f}%)")
        print(f"  base rate among all reached     : {base} of {len(reached)} ({100*base/len(reached):.0f}%)"
              f"  ->  lift {(len(old)/len(miss))/max(base/len(reached),1e-9):.1f}x")
        print(f"  LIFT BIAS: {susp} of those {len(new)} carry the erased-miss signature "
              f"(vs {100*ctrl/max(len(clean),1):.0f}% of your clean statements),")
        print(f"             so 'already shaky' is really between "
              f"{100*len(old)/len(miss):.0f}% and {100*(len(old)+susp)/len(miss):.0f}%.")

    # ── 2. Direction of error ──
    print(f"\nDIRECTION OF ERROR (the statement's true answer)")
    for name, ns in (("clean", clean), ("missed", miss), ("  already shaky", old), ("  knew it lower", new)):
        if not ns:
            continue
        v = sum(1 for n in ns if bank[n]["answer"] == "VERO")
        f = len(ns) - v
        note = ""
        if name.strip() != "clean" and len(ns) >= 20:
            k = max(v, f)
            note = f"   p={binom_tail(k, len(ns)):.3f}"
        print(f"  {name:16} true VERO {100*v/len(ns):3.0f}%  true FALSO {100*f/len(ns):3.0f}%   (n={len(ns)}){note}")

    # ── 3. Trap words ──
    print(f"\nTRAP WORDS (the app bolds these at L1/L2 and leaves them plain at L3)")
    for name, ns in (("clean", clean), ("missed", miss), ("  already shaky", old), ("  knew it lower", new)):
        if not ns:
            continue
        h = sum(1 for n in ns if TRAP_RE.search(bank[n]["it"]))
        print(f"  {name:16} {h:4}/{len(ns):<5} = {100*h/len(ns):3.0f}%")

    # ── 4. Topics, normalised ──
    print(f"\nTOPICS REACHED AT THIS LEVEL (20+ statements), by miss rate")
    tot = collections.Counter(bank[n]["topic"] for n in reached)
    bad = collections.Counter(bank[n]["topic"] for n in miss)
    for t in sorted(tot, key=lambda t: -bad[t] / tot[t]):
        if tot[t] < 20:
            continue
        print(f"  {100*bad[t]/tot[t]:5.1f}%  {bad[t]:3}/{tot[t]:<4}  {t[:60]}")
    print(f"  {100*len(miss)/len(reached):5.1f}%  overall")

    # ── 5. Rule blocks (the claims) ──
    tr = json.loads((PUB / "topic_reviews.json").read_text(encoding="utf-8"))
    claim = {}
    for t, v in tr.items():
        for n, h in (v.get("claims") or {}).items():
            claim[n] = (t, h)
    grp = collections.defaultdict(list)
    for n in reached:
        if n in claim:
            grp[claim[n]].append(n)
    hits = []
    for k, ns in grp.items():
        mm = [n for n in ns if n in set(miss)]
        if len(mm) >= 2:
            hits.append((len(mm) / len(ns), len(mm), len(ns), k, mm))
    print(f"\nRULE BLOCKS with 2+ misses  (one claimed paragraph each; the 📖 goes straight there)")
    for _r, mc, tc, k, mm in sorted(hits, reverse=True)[:12]:
        print(f"  {mc}/{tc}  {k[0][:44]:44}  {' '.join(sorted(mm)[:6])}")
    cov = sum(1 for n in reached if n in claim)
    print(f"  ({cov} of {len(reached)} reached statements are claimed, {sum(1 for n in miss if n in claim)} of {len(miss)} misses)")

    # ── 6. Words over-represented in the misses ──
    from consolidate_vocab import entry_regex
    V = json.loads((PUB / "vocabulary.json").read_text(encoding="utf-8"))["common"]
    gloss = {e["term"]: e.get("en", "") for e in V}
    pats = {e["term"]: entry_regex(e["term"]) for e in V}
    mlow = [bank[n]["it"].lower() for n in miss]
    clow = [bank[n]["it"].lower() for n in clean]
    rows = []
    for term, p in pats.items():
        mc = sum(1 for t in mlow if p.search(t))
        if mc < max(4, len(miss) // 25):
            continue
        cc = sum(1 for t in clow if p.search(t))
        mr, cr = mc / len(miss), cc / max(len(clean), 1)
        rows.append((mr / cr if cr else 999, mc, cc, term))
    rows.sort(reverse=True)
    print(f"\nWORDS over-represented in your misses (floor: {max(4, len(miss)//25)} missed statements)")
    print(f"  {'lift':>5}  {'missed':>10} {'clean':>11}   term")
    for lift, mc, cc, term in rows[:20]:
        print(f"  {lift:5.1f}  {mc:4}/{len(miss):<5} {cc:5}/{len(clean):<5}  {term}  —  {gloss[term][:46]}")

    # ── optional: list one topic's misses in full ──
    if "--list" in argv:
        want = argv[argv.index("--list") + 1]
        print(f"\nMISSES IN {want!r}")
        for n in sorted(n for n in miss if want.lower() in bank[n]["topic"].lower()):
            tag = "shaky before" if n in set(old) else "knew it lower"
            print(f"  {n} {bank[n]['answer']:5} [{tag}] {bank[n]['it'][:92]}")


if __name__ == "__main__":
    main(sys.argv[1:])
