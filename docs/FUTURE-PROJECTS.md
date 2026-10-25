# Future projects

Ideas parked until the Patente B app reaches golden master. Not commitments.

## AM-license (moped) edition — filed 2026-08-17

**Audience.** Americans moving to Italy who want to ride a scooter rather than
drive a car, plus B candidates wanting a gentler Italian on-ramp while they
study (the current app could cross-link to it).

**Why it is plausible.** The AM theory exam has the identical format to B
(30 true/false, 25 minutes, max 3 errors) but a much smaller, simpler official
bank aimed at 14-year-olds. The minimum age is 14, and B absorbs AM — so the
edition targets people who want two wheels *before* (or instead of) the B.

**What transfers unchanged.** Three-level pedagogy (English / Italian /
Italiano), vocabulary tooltips (heavy overlap with the ~1,900-term B
vocabulary), TTS, the frequently-missed-questions drill, mock-exam engine,
sync, PWA/offline infrastructure.

**What transfers partially.** Topic reviews: signs, precedence, speed, and
definitions material can be adapted; moped-specific content written fresh.

**The real work.** Sourcing the official ministerial AM bank (a separate bank
from B), then the extract → translate → explain → review pipeline. `scripts/`
tooling and `docs/review-glossary.md` carry over.

**Open design decision.** Separate deployment sharing the codebase (sibling
site, e.g. am.physyapps.com) vs. a bank switcher in the current app. Separate
is likely cleaner: progress, reviews, and vocabulary are all bank-keyed.

**First concrete step.** Check whether the official AM bank is publicly
available in the same form the B bank was obtained.
