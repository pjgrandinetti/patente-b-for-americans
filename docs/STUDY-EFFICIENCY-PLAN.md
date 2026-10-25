# Why the study loop works the way it does

The loop itself is described in `README.md` under "The study loop", and in the
app under "How this app works". **This file is the reasoning, not the
behavior**: the measurements that settled the design, and the one refinement
still open. Everything it originally planned has shipped.

## The problem it was solving

The bank is **7,147 statements** on 851 study cards, of which 41 are retired,
so **7,106 on 849 cards** reach a learner. Seeing each once at about 15 seconds
is roughly **30 hours**, a month at an hour a day for a single pass. For this
app's audience, English speakers at about A2 or B1 Italian, the natural path
studies each concept in English and then in Italian, which doubles it.

## The bank is not shrunk, and here is the measurement

**6,848 of the 7,147 statements are distinct**, after normalizing the Italian
and ignoring the sign reference. Only about **6%** share wording. There is not
enough literal redundancy to justify a de-duplication effort, and grouping by
meaning would risk merging rules that are genuinely different. So the bank
stays whole and the *process* is what gets cheaper.

Abridged mode, added later, is the one qualification: an AI-curated set about
20% smaller that hides near-duplicate statements **within a card**, with the
full set one tap away and a mock miss restoring it automatically. That is a
narrower claim than de-duplicating the bank, and it is reversible per card.

## What the design gave up, and why that was right

**No spaced-repetition scheduler.** The mock exam samples the whole bank and a
miss reopens the card at every level, so forgetting is caught reactively. That
was judged enough to start, and it still is: the finish line is the mock
average, not coverage.

**Carry credit UP the levels was rejected.** The original plan proposed that a
card mastered in English should come back lighter in Italian, to trim the
language doubling. What shipped is the opposite direction, `liftStatement`,
which credits a correct answer at a higher level DOWN to every level below.
That is the defensible direction: a learner who has answered under exam
conditions has proven more than the English level asks, whereas knowing a rule
in English says nothing about whether they can read the Italian, which is the
whole purpose of the second and third rungs. The downward lift also captures
most of the saving the original idea was chasing, since clearing the bank no
longer means clearing it three times.

## The one thing still open

**Time-based review near the exam.** Nothing in the app brings a card back
because days have passed. The weak-spot drill returns a card because it was
**missed**, and the mock catches forgetting only when it happens to sample the
statement.

If this is ever built, keep it narrow: **Italiano only**, in the run-up to the
projected ready date, resurfacing cards cleared more than a few days ago. It
belongs inside the reserve days the readiness estimate already holds back at
the end, not as a general scheduler bolted onto every level. Build it only if
testing shows retention actually failing, since the mock already measures
exactly that.

## Targets

| Learner | Path | Target | Before this work |
|---|---|---|---|
| Native-equivalent | Italiano only | ~15–30 h | ~50–100 h |
| English speaker, A2/B1 | EN → IT → Italiano | **~40–60 h** | ~150–300 h |

Honest note: the first exposure to the bank is still substantial and this
approach does not pretend otherwise. What it removes is the **re-work**. After
the first pass a learner only re-sees cards they missed, or that a mock proved
they did not know.

## Guardrails that still bind

- Offline-first, no backend, degrade gracefully.
- Keep `.patente` export and import working; version and migrate the schema on
  any change.
- Every `public_html/` change bumps the version. See `CLAUDE.md`, which is the
  current operational guide.
