# Trusted reviewers — who they are and how to onboard them

The content of this app (questions, answers, translations, explanations, concept
reviews) is AI-assisted and **must be verified by humans before/through beta**. The
*Reviewer mode* and *trusted reviewer code* exist to support that. This note records
who the ideal reviewers are and how the trust mechanism works.

## Who is qualified to vet driving-theory content in Italy

The authoritative experts are the certified staff of an **autoscuola** (driving
school). Italy recognizes two distinct certified roles:

- **Insegnante (di teoria)** — the **theory teacher**. Teaches the classroom material
  the written exam is drawn from. **This is the role most relevant to this app**, since
  our content is pure theory (the *quesiti*).
- **Istruttore (di guida)** — the **driving instructor** (behind-the-wheel). Less
  relevant to vetting written questions, though still knowledgeable.

A school also has a **responsabile didattico** (teaching director), who typically holds
both qualifications.

### The credential

Both roles require an **abilitazione / attestato di idoneità professionale** — a
professional-fitness qualification earned by completing a required training course and
passing a **state exam**, then kept current with a periodic refresher (~8 hours every
2 years).

- **Certifying authority:** Ministero delle Infrastrutture e dei Trasporti (**MIT**),
  through the **Motorizzazione Civile**; exams are administered locally by the
  **province / città metropolitane**.
- **Entry requirements** include a 5-year upper-secondary diploma and a valid license
  (at least category B; broader categories for *istruttore*).
- **Legal basis:** **D.M. 26 gennaio 2011, n. 17** (training and qualification of
  autoscuola teachers/instructors), updated by **D.M. 1 febbraio 2024, n. 34**;
  alongside the older **D.M. 317/1995** governing autoscuola activity.

**Recruiting takeaway:** a certified **insegnante di teoria** is the gold-standard
vetter for our questions/answers/explanations — they teach this exact material for a
living and are state-qualified to do so. That's the pool to recruit a small set of
high-credibility reviewers from for the pre-beta content pass. Native-Italian fluency
also means they can check the `italian_text` and `explanation_it` fields and the
concept reviews, not just the English.

## How the trust mechanism works in the app

Trust is **assertion-based**, not verified — there is no way to check an Italian
qualification programmatically. The code simply distinguishes people we *decide* to
trust so their submissions sort to the top.

1. **Issue a code.** Add an entry to the `reviewers` map in `public_html/secrets.php`
   (gitignored; see `secrets.example.php`), e.g. `'friend-xxxxxxxx' => ['name' => 'Name',
   'email' => 'them@example.com']`. Use a long, unguessable string. Never put a code in
   a tracked file.
2. **Hand it to the reviewer.** They paste it into **Settings → Trusted reviewer code**.
3. **Effect.** Their flagged questions and bug reports are tagged `trusted` and sorted
   first in `admin.php`. Everyone else's submissions are still
   collected, just marked unverified.
4. **Revoke** by removing the line. The code is not a secret in the security sense —
   it's an anti-noise/prioritization tag, so leaking it only lets someone mark their
   own reports "trusted," nothing more.

When handing out a code, it's worth asking the reviewer to state their **abilitazione**
(insegnante di teoria / istruttore) and their school, recorded informally on your side —
again, trust-on-assertion, but it sets expectations.

## Open source & positioning (reassuring instructor-reviewers)

A real concern when recruiting instructors: they may see a free study app as a threat
to their customers. Being **free *and* open source** actually defuses most of that, and
reframes the relationship.

- **Not a rival — shared infrastructure they can adopt.** Open source means an
  instructor can **fork, rebrand, translate, and point the app at their own students**
  (e.g. an Italian-language, school-branded version as a lead magnet or an enrolled-student
  perk). They get a tool they'd otherwise have to build or buy, rather than a competitor
  hoarding a market.
- **The law already protects their core.** The app only touches *theory self-study*. The
  mandatory certified driving lessons (6–8 h, increased by the 2024 reform), enrollment,
  paperwork (TT2112), medical, foglio rosa, and practical exam stay with the autoscuola.
  A student who aces theory still comes back for all of that.
- **The audience is one they usually can't serve** — English-speaking expats — so it's
  incremental, not cannibalizing, and the app can **funnel** those learners *to* schools
  for the lessons (optionally linking participating reviewers' schools).
- **Transparency builds reviewer trust.** Open source lets a contributor *verify* there's
  no hidden monetization of their work (no ads, no data sale) and that their attribution
  is intact — far easier to lend your name to than a black box.

### License recommendation

Pick the license deliberately, because it controls exactly this dynamic. Recommended:

- **Code → AGPL-3.0.** Instructors can fully use and rebrand it, but any forked or hosted
  derivative must also publish its source, so the commons stays open and nobody can quietly
  privatize the work. (A *permissive* MIT/Apache license is even more fork-friendly — it
  allows closed, commercial rebrands — at the cost of that guarantee.)
- **Content (explanations, concept reviews, translations) → CC-BY-SA.** Keeps reviewers'
  contributions credited and open, and prevents the vetted content being taken closed for a
  paid product.
- **Question bank itself** is the Ministry's publicly published material — note it
  separately from the code/content licenses; we don't relicense it.

The instructor-facing pitch in one line: *"It helps English speakers pass the part they'd
study alone anyway, points them to you for everything that legally requires a school, and
you're free to take it, brand it, and run your own version — with your name on the content
you helped vet."*

**Honest caveat:** open source won't convince an instructor who objects to free theory
tools *in principle*. But the official bank is already public and free apps already exist,
so this joins an existing landscape rather than creating the threat — and you only need a
small handful of trusted reviewers.

## Sources

- MIT — Istruttore di autoscuola: https://www.mit.gov.it/documentazione/riconoscimento-qualifiche-professionali-istruttore-di-autoscuola
- MIT — Insegnante di autoscuola: https://www.mit.gov.it/documentazione/riconoscimento-qualifiche-professionali-insegnante-di-autoscuola
- D.M. 1/2/2024 n. 34 — abilitazione insegnanti e istruttori: http://www.patente.it/normativa/decreto-ministero-trasporti-01-02-2024-n-34-abilitazione-insegnanti-istruttori?idc=4846
