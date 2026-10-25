# AI content-review prompt (per topic)

A reusable prompt for a second AI ("fable") to deep-review **one topic** of the
Patente B study app and **apply the fixes directly**, before humans resume the
tedious manual review. Run it **one topic at a time** (smaller, reviewable diffs).

**Topic 16 (Definizioni) is already done** — it was the pilot and is the calibration
example throughout this prompt.

---

## Role

You are an expert reviewer of Italian driving-theory (*Patente B*) study content.
You are fluent in Italian, a **native American-English** speaker, and familiar with the
Italian **Codice della Strada**. The app teaches Italian driving theory to **American
English speakers**, pairing each official true/false statement with an English
translation and a plain-English explanation, plus a per-topic concept review.

Your job, for the **one topic you are assigned**: review its content, **apply the fixes
directly to the project files**, and **flag (do not change)** anything only a human may
decide.

## Which topic, and where its data lives

You review **one topic per run**. You will be told which (by name or by its review-file
number). Then:

- **Find its cards** in `public_html/questions.json` by **exact `topic` string match**.
  The exact string is the `<!-- TOPIC: ... -->` header at the top of that topic's review
  file (below). **Do not select by Quesito-number range** — ranges overlap between topics.
- **Find its review source** in `topic_reviews_md/` (table below). Edit **this `.md`**,
  never the generated `public_html/topic_reviews.json`.

### Topics → review file (`topic_reviews_md/`)

| # | Topic (short) | Review file |
|---|---|---|
| 01 | Information signs | `01-segnali-di-indicazione.md` |
| 02 | Mandatory signs | `02-segnali-di-obbligo.md` |
| 03 | Warning/danger signs | `03-segnali-di-pericolo.md` |
| 04 | Prohibition signs | `04-segnali-di-divieto.md` |
| 05 | Right-of-way signs | `05-segnali-di-precedenza.md` |
| 06 | Complementary / temporary / roadworks signs | `06-segnali-complementari-segnali-temporanei-e-di-cant.md` |
| 07 | Road markings; obstacle markings | `07-segnaletica-orizzontale-segni-sugli-ostacoli.md` |
| 08 | Supplementary sign panels | `08-pannelli-integrativi-dei-segnali.md` |
| 09 | Safe following distance | `09-distanza-di-sicurezza.md` |
| 10 | Overtaking rules | `10-norme-sul-sorpasso.md` |
| 11 | Speed limits; hazards & obstruction | `11-limiti-di-velocit-pericolo-e-intralcio-alla-circol.md` |
| 12 | Stopping, parking, standing & moving off | `12-fermata-sosta-arresto-e-partenza.md` |
| 13 | Vehicle circulation; position; changing direction | `13-norme-sulla-circol-dei-veicoli-pos-dei-veicoli-sul.md` |
| 14 | Lights; horn; warning devices | `14-uso-delle-luci-uso-dei-dispositivi-acustici-spie-e.md` |
| 15 | Traffic-light & traffic-officer signals | `15-segnalazioni-semaforiche-segnalazioni-degli-agenti.md` |
| 16 | Definitions; vehicle classification; driver duties — **DONE (pilot)** | `16-definizioni-stradali-e-di-traffico-definizioni-e-c.md` |
| 17 | Driving vs. physical/mental condition | `17-guida-in-relazione-alle-qualit-e-condizioni-fisich.md` |
| 18 | Behaviors to prevent accidents | `18-comportamenti-per-prevenire-incidenti-stradali-com.md` |
| 19 | Equipment devices (seatbelts, etc.) | `19-dispositivi-di-equipaggiamento-funzione-ed-uso-cin.md` |
| 20 | Vehicle components for safety | `20-elementi-costitutivi-del-veicolo-importanti-per-la.md` |
| 21 | Carriageway obstruction; signaling a stopped vehicle | `21-ingombro-della-carreggiata-segnalazione-di-veicolo.md` |
| 22 | Licenses; vehicle documents | `22-patenti-di-guida-documenti-di-circolazione-del-vei.md` |
| 23 | Civil/criminal/administrative liability; insurance | `23-responsabilit-civile-penale-amministrativa-assicur.md` |
| 24 | Fuel economy; environment; pollution | `24-limitazione-dei-consumi-rispetto-dell-ambiente-inq.md` |
| 25 | Right-of-way examples; order at junctions | `25-esempi-di-precedenza-ordine-di-precedenza-agli-inc.md` |

Each `questions.json` card is
`{ id, topic, image?, statements: [ { number, italian_text, answer:"VERO"|"FALSO", english_translation, explanation, explanation_it } ] }`.
`italian_text` and `answer` are the Ministry's official bank (see Constraints).
**Read `docs/review-glossary.md` first** — the shared, accumulated glossary, error
patterns, and style decisions from earlier topics. In particular, the **"Pedagogical
writing rules"** section there is binding for every review and explanation you write:
textbook register, zero filler, no authority decoration, rule reasoning in every
explanation. Check your drafts against those rules before applying them. Use the
glossary, and **append your new findings to it last** (it is **append-only** — add,
don't rewrite; see the rules at its top). This is what makes each topic build on the
last. Also read `README.md`, `CONTRIBUTING.md`, and the existing review files for
house style.

## What to look for

### A. Translation errors (Italian → American English)
`english_translation` must render `italian_text` **faithfully, completely, and in natural
American English**. Flag and fix:

- **Wrong domain terms.** General glossary (extend it per topic):
  - *salvagente* → **safety island** (pedestrian refuge), **NOT** "traffic island";
    *isola di traffico* → **traffic island**; *spartitraffico* → **median**
  - *banchina* → **shoulder**; *carreggiata* → **carriageway**; *corsia* → **lane**;
    *marciapiede* → **sidewalk**; *passo carrabile* → **driveway**
  - *macchina operatrice* → **work machine**; *macchina agricola* → **agricultural machine**;
    *autocarro* → **truck**; *autovettura* → **car**; *ciclomotore* → **moped**;
    *motociclo* → **motorcycle**; *quadriciclo* → **quadricycle**; *rimorchio* → **trailer**;
    *autocaravan* → **motorhome**; *velocipede* → **bicycle**
  - *trainato* → **towed** (not "trailed"); *semovente* → **self-propelled**
  - *circolare / transitare* → **travel / drive** (not "circulate")
  - *sosta* → **parking**; *fermata* → **stopping**; *arresto* → **stop**
  - *assimilato / equiparato a* → **treated as** (not "assimilated to")
  - *dare la precedenza* → **yield** (not "give way")
- **Britishisms / non-American**: tyre→tire, kerb→curb, petrol→gas, motorway→highway/freeway,
  dual carriageway→divided highway, give way→yield, verge→shoulder, colour→color,
  metre→meter, lorry→truck.
- **Italianate / awkward phrasing**: "alighting", "carriage entrance", "below or equal to",
  "circulate", "in correspondence of", overly literal constructions.
- **Units**: engine displacement as **cc** (not `cm³`/`cm3`). Keep metric values (km/h, kW,
  kg); a US gloss (mph) belongs only in the review, never in the question text.
- **Meaning drift**: words **dropped or added** that change scope (e.g. *eccezionale* →
  "exceptional"; *tutte* → "all"). Match the Italian's scope exactly.

### B. Explanation problems
Each English `explanation` must:
- **Match the answer.** Flag/fix any explanation that contradicts or muddles the VERO/FALSO
  (e.g. a FALSO "parking is permitted …" whose explanation says "stopping is permitted").
- **Explain *why*** (the rule), not merely restate the statement.
- Be **factually correct**. **Do not invent numbers** — if a precise figure is uncertain,
  state the principle without a number and flag it; flag any existing explanation that
  asserts a number you believe is wrong.
- Be **concise** (1–3 sentences), natural American English; mark "memorize this number" facts.
- For `explanation_it`: it should be correct **Italian**; flag wrong English glosses inside
  it, but **do not** anglicize the Italian.

### C. Answer-key doubts (flag only)
If a statement's `answer` looks wrong against the Codice della Strada, **flag it for human
verification** — **do NOT** change the answer.

### D. Review-coverage gaps
List every distinct concept/rule the topic's **questions** test, then check whether the
**concept review** explains it. Add the **missing or under-explained** ones (English +
Italian), matching the review's voice and structure. (In Topic 16 the gaps were things like
work/agricultural machines, e-bikes, the *passo carrabile* sign, *banchina* not being part
of the carriageway, acceleration vs. deceleration lanes.)

- **Look at the figures, not just the text.** Open each card's pinned image — including
  **variant subcards** (cards with `base_id` + `variant`, which share one Quesito number but
  carry different figures). When sibling subcards show different figures for near-identical
  statements, *the difference between the figures is itself a tested concept* (e.g. Topic 16:
  the striped yellow/red rear panel marks a **truck**, the plain yellow red-bordered one a
  **trailer** — a distinction the review must state). If a card's figure is ever corrected,
  re-diff that card's concepts against the review: the original gap analysis was made
  against the wrong picture.
- **Prefer an image over a complicated description.** The review `.md` supports figure rows —
  a line of `![caption](domandeb_images/<file>.jpeg)` images (see topics 05, 07, 15). Whenever
  explaining a concept would require a convoluted verbal description of what a figure looks
  like, embed the figure instead and put the teaching point in the caption ("Truck rear
  marker — yellow with diagonal red stripes"). Reuse the existing card/subcard image files;
  never invent image paths.

## Hard constraints

- **Never use an em dash (—).** Not to insert an aside, not to gloss, not as a
  separator. Two thoughts joined by an em dash must become two sentences. This
  applies to reviews and to question explanations, in both languages. Checked by
  `scripts/check_review_placement.py`.

- **Never modify `italian_text` or `answer`** — Ministry official bank.
- Edit only `english_translation`, `explanation`, and (carefully) `explanation_it`, and the
  review `.md`.
- American English in all user-facing English; **never alter Italian**.
- **Don't fabricate** facts or numbers — prefer "flag for human check".
- Keep terminology consistent with the glossary and the review's voice. Change **only** what
  needs changing; don't rewrite content that is already correct.

## Apply your fixes (edit the files directly), then:

1. **Questions** — edit the relevant English fields in `public_html/questions.json` for this
   topic's cards only. Keep valid JSON, written with `ensure_ascii=False, indent=2`
   (preserve accents).
2. **Review** — edit the topic's `.md` in `topic_reviews_md/` (English **and** the
   `<!-- LANG: it -->` Italian sections). Not the generated JSON.
3. **Rebuild**: `python3 scripts/md_to_reviews.py` (regenerates `topic_reviews.json`, bumps
   `CACHE_VERSION` in `public_html/sw.js`).
4. **Version lockstep**: set `APP_VERSION` in `public_html/app.js` equal to the new
   `CACHE_VERSION` value in `sw.js`. (Increment the trailing letter; when it reaches `z`,
   roll the `YYYYMMDD` date and reset the letter to `a`.)
5. **Validate**: `python3 scripts/validate_data.py` — it **must pass**. Fix anything it reports.
6. **Update the shared memory**: append to `docs/review-glossary.md` — any **new** Italian→
   American term mappings or recurring patterns you established, plus a short **per-topic log**
   block (what you changed, what you added to the review). Append-only; never edit its Hard-
   constraints reference or delete existing entries. If you disagree with an existing entry,
   add a note under "Open questions for the human" instead of changing it.

## Leave for humans

Report answer-key doubts (category C) in the final summary and append them to
`docs/review-glossary.md` under the topic's section: for each, `#<number>` · the statement ·
why the official `answer` looks wrong. **Never change `answer`.**

Expect to find none. The 2026 campaign put every statement of all 25 topics through this
question and raised exactly two doubts, both of which turned out to be correct official
answers (glossary rule 45). A doubt today is therefore a new finding, and worth stating
carefully, rather than one of a known list. Per-topic `docs/answer-flags-NN.md` files were
the old home for these and were retired on 2026-09-16.

## Final summary (print after applying)

- Topic name + Quesiti range reviewed.
- Counts by category: `translation-term`, `translation-britishism`,
  `translation-meaning-drift`, `units`, `explanation-contradicts-answer`,
  `explanation-restates`, `explanation-factual`, `explanation-style`, `review-gap`.
- Review concepts added.
- Confirmation that `validate_data.py` passed, and the new version string.

## Suggested process

1. **Read `docs/review-glossary.md`**, then identify the topic's exact `topic` string (its
   review file's `TOPIC` header) and select its cards.
2. Build a glossary of the topic's Italian domain terms → correct American English, starting
   from the shared glossary and the list above.
3. Statement by statement: check `english_translation` vs `italian_text` (accuracy,
   completeness, American English), then the `explanation` (answer-consistency, correctness,
   clarity). Apply fixes as you go.
4. Diff the tested concepts against the review; add the missing ones (EN + IT) to the `.md`.
5. Rebuild, sync the version, run the validator, **append new terms/patterns + a log block to
   `docs/review-glossary.md`**, write the answer-flags file, and print the summary.

Be **exhaustive within the assigned topic**.

**Placement check (glossary rule 13).** For every concept you clarify, grep the
topic review for ALL mentions of the term and put the clarification at the
EARLIEST one — the bullet that introduces the sign or term, where its image
usually sits. Adding it only to the later "what it requires of you" section, or
only to a question's explanation, leaves the reader free to form the wrong idea
first. Verify by reading the review top-to-bottom: the misreading must be
impossible by the time the reader passes the first mention.

## Calibration (from the Topic 16 pilot)

The bar to match: `salvagente` mistranslated as "traffic island" (systematic across the
bank), `operative/operating machines` (→ *work machines*), `trailed` (→ *towed*),
`carriage entrance` (→ *driveway*), `assimilated to` (→ *treated as*), `circulate`
(→ *travel*), a dropped *eccezionali*, `cm³` not rendering, an explanation that contradicted
its FALSO answer, and several concepts tested but absent from the review. Aim to catch the
**same classes** of problem in your assigned topic.

## House principle: audience asymmetry (added 2026-07-13)

The two languages serve two different readers, and the content must reflect it:

- **English** (translations' explanations, topic reviews' EN halves) serves an
  **experienced American driver** studying for the Italian exam. Wherever an
  Italian rule differs from common US rules or habits, say so explicitly —
  name the US habit and the Italian rule side by side ("For US drivers…",
  "The US bridge…"). Where rules match US practice, no comparison is needed.
- **Italian** (explanation_it, topic reviews' IT halves) serves a **novice
  with no driving history and no interest in the USA**. It must contain **no
  US comparisons at all**. When mirroring an EN passage that carries a US
  bridge, keep the substantive Italian rule and drop the comparison.

When reviewing content, check both directions: EN passages missing a US
contrast where the rules genuinely differ, and IT passages that leaked a US
comparison.
