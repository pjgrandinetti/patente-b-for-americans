# CLAUDE.md — working guide for this repo

Operational guide for an AI agent working on the **Patente B** study app. For the
full product/architecture description, read `README.md`. This file is the
short list of rules, workflows, and gotchas so you're productive immediately.

## What this is
A static, offline-first PWA for the Italian Patente B theory exam. It is BUILT
FOR American English speakers, and it is ALSO USED BY native Italian speakers —
`uiLang()` switches the interface to Italian on its own for an Italian browser,
every topic review has a full Italian half, and every statement carries an
`explanation_it`, so Solo italiano is a complete study path with no English in
it. **One deliberate exception, 2026-09-19**: for a NON-Italian browser, a
statement answered WRONG at Solo italiano shows the English of the statement
and of the explanation underneath them, with no pill to press
(`enOnWrong` in `showStatementAnswered`). It is L2's wrong-answer auto-open
carried up a level: a miss is as likely to be a misread word as a gap in the
rule, and nothing else tells the learner which. **Extended 2026-09-23 at the
maintainer's request (`enOnWhy`)**: after a RIGHT answer at Solo italiano, the
English of the statement and of the explanation appear together WITH the
explanation, that is, when the learner taps "Why?" or has the "show the
explanation after a correct answer" setting on, and at no other time. Asking
why is the moment a misread word matters, and the answer is already given.
Nothing appears before an answer, a right answer shows no English unasked, and
an Italian browser sees none of it. Do not add an EN pill at L3 to "match" L2:
a control on a right answer is an invitation to lean on it, and the maintainer
asked for the translations without one. Do not reason as though everyone here is translating out of Italian. That
premise sat in this file's first line until 2026-09-17 and it is load-bearing:
it is what made the vocabulary abort below look general when its argument
("select the word, Look Up, the OS answers better than we can") only ever
covered the English-speaking half. A native speaker does not need the word
translated. Check which audience a decision is about before making it.

No framework, no build step for the core — the deployable
app is the `public_html/` directory (HTML/CSS/JS + JSON data + optional PHP
endpoints). Live at https://patente.physyapps.com. Content is still being reviewed
topic by topic; the "Work in progress" banner on the dashboard was removed at
the maintainer's request on 2026-09-24 (`hideWipBanner` strips it from a
stale cached index.html).

Scale: **25 topics**, **7,147 statements** in the file of which **41 are
retired**, so **7,106** reach the learner (see "Withdrawn statements").

Three card counts are all correct and mean different things, so say which one
you mean:
- **716 Ministry cards** (715 live), the *quesiti* the Ministry publishes. Ours
  matches its April 2025 file exactly, the one extra being the withdrawn 4143.
- **851 study cards** (849 live), which is what `validate_data.py` prints and
  what the learner steps through, since `studyCardCounts` counts every entry.
  That is 716 Ministry cards, plus **115 `variant_auto` subcards** that
  `extract_statement_images.py` splits off when one card's statements carry
  different figures, plus the **20 manual** A/B variants (ids 5004+).
- **736**, which is 716 plus the 20 manual variants. It was the study-card
  total before the automatic image split added the other 115, and it survived
  in this file, in README.md and in the in-app help until 2026-09-15. It is
  not wrong, it is just stale, and it matches nothing the learner sees. Use
  851 or 849 for anything learner-facing.

## The stages of the learner's path (internal model, not shown in the app)

Agreed with the maintainer on 2026-10-04 as the way to think about the app.
The learner never sees the word "stage"; the screens stay as they are. Use
these names in code comments, commits and this file, and say "in stage N"
rather than re-deriving when a feature applies.

| Stage | Who | The work | Opens when | Code today |
|---|---|---|---|---|
| 1. English | non-Italian browser | one pass through the bank in English | start | `currentLevel === 1` |
| 2. English with Italian | non-Italian browser | the same, Italian shown | stage 1 cleared | `currentLevel === 2` |
| 3. Italiano | everyone; an Italian browser starts here | the same, Italian only | stage 2 cleared, or at once for an Italian browser | `currentLevel === 3` |
| 4. Weak spots | everyone | clear the questions missed in stages 1 to 3 | Italiano cleared | `italianoComplete()`, `difficultCards()`, the drill |
| 5. Mock exams | everyone | mocks until the chance of failing is 5% or less over 15 or more | Italiano cleared, or earlier by the Settings option | `mockEarlyOn()`, `examReady()` |
| 6. Review | everyone | one mock and the day's review each day until the exam | an exam date entered, offered once stage 5 is met | `inReviewPhase()`, `examDate()` |

- **Stages 1 to 3 are LEVELS**: each is a full pass over the bank under a
  language setting, with its own progress map (`patente_progress_L1` to
  `L3`) and the level picker. Stages 4 to 6 are not levels and must not be
  made into them: they are measured differently (questions left, chance of
  failing, days to the exam) and have no progress map of their own.
- **Stages 4 and 5 overlap.** The weak spots refill from every mock miss,
  so stage 4 never closes for good; stage 5 begins when Italiano is
  cleared and the weak spots run alongside it. Their release rule is the
  fast one (two right in a row) by the maintainer's choice, so a learner
  reaches the mocks quickly.
- **Stage 6 replaces stage 4's drill** as the daily work: the weak spots
  are folded into the review set, their card is hidden, and the nav's
  Begin/Resume starts the review. A slip below 5% does not leave stage 6
  (the exam date stays; the banner warns).
- **What each stage shows**, so a change to one place can be checked
  against the others: the nav Begin/Resume (topic in 1 to 3, drill in 4
  and 5, review in 6), the dashboard (levels and topics in 1 to 3, the
  compact dashboard with the weak-spots and mock cards from 4, the exam
  date box from the end of 5), the banner (from the first mock), the
  Statistics page (every stage), and **Settings, grouped by stage since
  20261011f** (`SETTINGS_GROUPS`, `ensureSettingsGroups`, built in JS by
  moving the existing rows): Your data FIRST since 20261013b (maintainer,
  2026-10-14: sync is the first act on a new device, applies at every
  stage, and is where the backup banner sends people), then While you
  answer, Studying the levels (Abridged mode first; the topic-notes note
  row moved here from While you answer, since it governs the Concepts),
  Weak spots and mock exams (hidden until Italiano is cleared or the
  early-mock option is on), Before your exam (hidden until an exam date),
  Reviewers. Rows take the order of `SETTINGS_GROUPS`, not index.html's. A future stage's group is hidden; past ones stay. A new
  Settings row goes into its stage's group. `check_settings_groups.js`.
- **The list is OPEN-ENDED.** The maintainer is going through the licensing
  process himself while the app is built, and each step he reaches has
  added a stage (the mocks, then the review). Expect more: the theory exam
  itself, the driving lessons and test, the time after the license. A new
  stage goes into the table with what opens it and what it changes, and
  every place listed above is checked against it. Stages are referred to
  by NAME in code and comments, not by number alone, so one inserted in
  the middle does not renumber the rest.
- **Planned, not built:** one `appStage()` returning the current stage by name, which the
  places above would ask instead of each testing its own conditions.
  Several bugs of 2026-10-04 came from one part not knowing what another
  had decided (the nav button still starting the weak-spots drill in
  stage 6). Move the checks onto it one at a time, with the tests
  showing no behavior changes.

## How to write to the maintainer
Plain English, no colloquialisms. "Fair", "circle back", "reach out", "good
catch", "nice", "let's dive in" and their relatives are all banned, in replies
as well as in the app. State the finding, name the file or the statement, stop.
No flattery at the start of a reply and no summary of what was just said at the
end. This instruction is also in the maintainer's own settings and did not
reach the session on 2026-09-20, which is why it is recorded here.

## Hard rules — do not violate
1. **Never edit `italian_text` or `answer`** in `public_html/questions.json`. That
   is the official Ministry bank; only `english_translation`, `explanation`, and
   `explanation_it` may be corrected.
   - **One sanctioned exception, granted by the maintainer on 2026-09-11**: a
     *typographic* defect in the source file, where a character is plainly not
     the letter it should be. So far exactly one: 23949 printed `riprodott0`
     with a digit zero, in `sources/DomandeB.pdf` itself, and is stored as
     `riprodotto`. This covers nothing else. Wording, grammar, punctuation and
     anything arguable stay exactly as the Ministry wrote them, however wrong
     they look; ambiguity is handled with `warn`/`warn_it`, never by rewriting.
     Confirmed still present in the **April 2025** publication, so it is a
     defect in the Ministry's own file and not an artifact of an old
     extraction.
   - **A second sanctioned class, granted 2026-09-15**: a word the PDF broke
     across two lines and our extraction rejoined as hyphen plus a space.
     Three exist and all three are corrected: 21574 `turistico- alberghiere`,
     24356 `air- bag`, 24923 `anti- shock`. Both source PDFs produce the same
     artifact, which is what proves it is ours rather than the Ministry's. The
     class is closed: `re.search(r"\w- \w", italian_text)` now finds nothing,
     and the four hits in the fields we author ("two- or", "front- or",
     "three- or", "eight- or") are ordinary suspended hyphens.
     Before making such a fix, verify the character against `DomandeB.pdf`,
     record it here, and re-apply it if the bank is ever re-extracted.
     `scripts/validate_data.py` prints any digit glued to letters so a new one
     cannot slip in unnoticed (`cm3` and `0,1kW/kg` are legitimate).
2. **Never hand-edit `public_html/topic_reviews.json`.** It is generated from
   `topic_reviews_md/*.md` by `scripts/md_to_reviews.py`. Edit the Markdown, then
   rebuild.
3. **Keep the two version markers in lockstep**: `APP_VERSION` in
   `public_html/app.js` must equal `CACHE_VERSION` in `public_html/sw.js` (minus
   the `patente-netfirst-` prefix). `validate_data.py` fails if they differ.
4. **Never commit `public_html/secrets.php`** (gitignored; holds admin keys /
   reviewer codes). Put **no secret values in committed files** — this repo is
   going public. Template is `public_html/secrets.example.php`.

## Versioning
- Format: `YYYYMMDD<letter>` (e.g. `20260620y`). **Every change under
  `public_html/` bumps the version.**
- Bump = increment the trailing letter (`y` → `z`); at `z`, roll the date forward
  and reset to `a`.
- Set **both** `APP_VERSION` (app.js) and `CACHE_VERSION` (sw.js) to the same value.
- The service worker is network-first for code and prompts the user to "Restart
  now" to apply an update.
- **The three big data files carry THEIR OWN CONTENT HASH in their URL**
  (`topic_reviews.json?v=f083d4f05efe`, likewise questions and vocabulary;
  `DATA_HASH` in app.js and sw.js, stamped by `scripts/stamp_data_hashes.py`,
  which `md_to_reviews.py` runs and `validate_data.py` checks), and the
  worker serves them cache-first. **Until 20260930q the stamp was
  APP_VERSION**, so every release re-downloaded all three files on every
  device, and the worker's install fetched them a second time after the page
  had: one day of releases (2026-09-23) showed one person pulling
  questions.json 34 times, 30 MB. A file edited without the stamp being rerun
  now fails validation; `scripts/check_data_hash.js` (10 checks) runs sw.js in
  a fake worker and proves a cached file is not refetched at install and a
  release with unchanged data downloads none. **In the same release the
  worker's network-first path went from `cache: 'reload'` to
  `'no-cache'`**: both always ask the server, but `'reload'` never sends the
  conditional request, so app.js answered 200 on all fifty launches that day
  (10.7 MB for one file) while `.htaccess` had been written for "cheap 304s
  via ETag". Upload order still matters, since the hash stamped in app.js and
  sw.js must name the bytes on the server: data files first. They used to be stale-while-revalidate on
  an unversioned URL in a version-independent cache, so a new APP_VERSION could
  read data cached several releases earlier. That is not cosmetic: CLAIMS live
  inside `topic_reviews.json`, so old notes silently drop a statement's claim
  and its 📖 falls back to the picker and lands on the section heading. It was
  reported twice as a landing bug (24097 and 24092 on 2026-09-13) whose claims
  were correct all along, and it is the likeliest explanation for the IT pills
  that "did not work" on 2026-09-12 and could not be reproduced. `dataUrl` in
  app.js and in sw.js must stay in step, and anything that looks a data file up
  in the cache must use it (the image precache reads `questions.json` from
  there). Cache-first makes a bad copy STICKY, so a data file is cached only
  once `isWholeJson` has proved it parses (a file caught mid-upload still
  arrives as 200 OK), `loadDataFile` in app.js deletes the entry and refetches
  if what comes back will not parse, and the Reload button on the load-error
  screen empties the data cache first. Without those three a single truncated
  fetch left the app dead on "Couldn't load the questions" for good.
- **Do not bump the version in sw.js with
  `sed s/patente-netfirst-[0-9a-z]*/.../`.** It also rewrites the prefix
  literal inside `CACHE_VERSION.replace('patente-' + 'netfirst-', '')`, which
  silently empties `DATA_VERSION` and stamps every data URL `?v=`. That is why
  the literal is written in two pieces. Set `CACHE_VERSION` by editing the
  line, or anchor the pattern to `^const CACHE_VERSION`.

## Common workflows

**UI / code change** (`app.js`, `style.css`, `index.html`, `sw.js`):
1. Make the edit.
2. Bump `APP_VERSION` (app.js) and `CACHE_VERSION` (sw.js) to the same new value.
3. `node --check public_html/app.js`
4. `python3 scripts/validate_data.py`
5. Commit. (You cannot deploy — see Environment.)

**Concept-review change** (the per-topic study notes):
1. Edit `topic_reviews_md/NN-*.md`. English lives under `<!-- LANG: en -->`,
   Italian under `<!-- LANG: it -->`. **Do not change** the `<!-- TOPIC: … -->`,
   `<!-- SOURCE: … -->`, or `<!-- LANG: … -->` markers.
2. `python3 scripts/md_to_reviews.py` — regenerates `topic_reviews.json` and
   bumps **only** `sw.js` `CACHE_VERSION`.
2b. `python3 scripts/build_topic_pages.py` — regenerates the 25 public guide
   pages and `sitemap.xml` from the same Markdown. `validate_data.py` fails if
   you skip it. See "The guide" below.
3. **GOTCHA: the script does not touch `app.js`.** Manually set `APP_VERSION`
   (app.js) to the new `CACHE_VERSION`, or `validate_data.py` will report a
   version mismatch.
4. `python3 scripts/validate_data.py`
5. Commit `app.js`, `sw.js`, `topic_reviews.json`, and the edited `.md`. (The
   `.bak` is gitignored, and since 2026-10-04 it is written at the repo root,
   not in `public_html/`, which the maintainer uploads whole.)
   - **Equations are DISPLAYED, never run into a sentence** (maintainer,
     2026-09-25: "like a scientific paper"). Write one as its own paragraph,
     a line `$$ safe distance ≈ (speed ÷ 10) × 2.8 $$` with a blank line above and
     below; the sentence before it ends with a colon and states the units.
     The app renders it centered and unbroken (`REVIEW_EQ_RE`, `.rb-eq`), the
     guide as `<p class="eq">`, and `check_review_english.py` lets an `=`
     stand there. It is still an ordinary block for hashing and pairing, so
     the Italian half needs its own `$$` line in the same place. Topics 09
     (the safe distance) and 21 (the towing ratio) carry them. Topic 09's
     two course-book rules of thumb, for the reaction and the stopping
     distance, were REMOVED on 2026-09-25 at the maintainer's word: no
     statement tests either figure, and the reaction rule gave 15 m at
     50 km/h against the 14 m that 22579 marks VERO. Teach only what the
     bank tests when a second method would give a different number. Each SIDE is kept
     unbroken, and the line may break only after the first ≈ or =
     (`reviewEqHtml` in app.js, the span split in `build_topic_pages.py`),
     so on a phone a long one shows as two lines. Write no squares or other
     exponents: the maintainer asked on 2026-09-25 for `(speed ÷ 10) ×
     (speed ÷ 10)` in place of `(speed ÷ 10)²`, since not every learner
     reads the superscript. **The safe distance is `(speed ÷ 10) × 3`
     since 20261002j** (maintainer, flag on 22581, 2026-09-25: "easier to
     remember and the error is minor"), replacing `× 2.8`, which had
     replaced `speed ÷ 3.6` the same morning. The rule is stated as NOT
     exact wherever it appears: it gives 45 at 150 km/h against the bank's
     42 and 15 at 50 against 14, and the notes, the Reference row and all
     seventeen explanations (22578 to 22601) say so and say why it still
     serves, which is that the FALSO figures on those cards (2, 5, 15, 20,
     25) are nowhere near either number. Measured before the change: ×3
     flips no answer. This is the one sanctioned exception to "teach only
     what the bank tests when a second method gives a different number";
     the reaction rule of thumb removed that morning is not, since it was a
     second method beside the exact one. A change to the method is a change
     in all three places.
   - Image syntax in reviews: `![alt](domandeb_images/NNNN.jpeg)`. A line with a
     **single** image renders large; multiple images on one line render as a
     thumbnail row.
   - **The `pairs` map is generated too.** `md_to_reviews.py` aligns the English
     and Italian block by block and writes `{ hash of an EN block: index of its
     IT block }`, which drives the **IT reveal pills** in the English notes. It
     stores an index, not the Italian text, or the file would carry every
     Italian word twice (that cost 573 KB before it was fixed). Two mirrored
     pieces of code must stay in step: `_hash` / `_text_blocks` in the script
     and `reviewBlockHash` / `reviewItBlocks` in `app.js`. `validate_data.py`
     rebuilds the map and fails if the shipped one differs, so editing a
     review without re-running the script is caught.
   - **English and Italian must stay in sync, block for block.** The pairing
     is what the pills rest on, so a paragraph nobody translated shows up as a
     missing pill rather than as an error. Both `md_to_reviews.py` and
     `validate_data.py` therefore FAIL on any English block with no Italian,
     any Italian block with no English, and any section present in one
     language only. `validate_data.py` rebuilds everything from the `.md`
     sources and compares it to the shipped JSON, so an edited review that was
     not rebuilt is caught too.
   - **Image captions carry the pill too (20261010j, maintainer,
     2026-10-04).** A caption is not a block, so `pairs` never reached it.
     Captions pair by IMAGE FILE instead (`reviewCaptionTwins`): the same
     `domandeb_images/...` path in the other half, in order of appearance
     when a file is shown twice. All 324 captions pair today; a caption
     whose image appears in one half only gets no pill, silently, so keep
     every figure in both halves. `scripts/check_review_captions.js`.
   - **English-only scaffolding is DECLARED, never inferred.** End the line
     with `<!-- en-only -->` (on a heading, it exempts the whole section). The
     13 current ones are the `> **For US drivers.**` notes, topic 11's "US
     bridge" section, the two ZTL practical notes, and one blue-circle
     comparison. Inferring the exemption from the wording was the first
     attempt and is worse: a genuinely missing translation hides behind it.
     The marker is stripped from the shipped English and never renders.

**Vocabulary consolidation** (phrases replacing single-word look-ups):
1. Add the new phrase entries to `public_html/vocabulary.json` (`common`).
2. `python3 scripts/consolidate_vocab.py` — report: which entries never fire
   because a longer phrase covers them, and which determiner-led variants
   ("un sinistro stradale") are shadowing a better bare term.
3. `python3 scripts/consolidate_vocab.py --apply` — removes the dead entries
   and APPENDS rules to `vocabulary.json`'s `replaced_by` map.
4. **The final-vowel wildcard stops at other entries.** The matcher lets one
   entry cover an inflected family (`veicolo` matches `veicoli`), and that
   same wildcard used to let *different words* capture each other: `obbligo`
   swallowed `obbliga`, `transito` swallowed `transita`, `fine` swallowed
   `fino`, `prima dei` swallowed `primo dei`. Since 2026-09-11 a vowel is
   dropped from a word's class whenever it would turn the whole term into
   another existing entry, in both `app.js` and `consolidate_vocab.py`
   (`entry_regex`). So the fix for "the noun is glossing the verb" is simply
   to ADD the verb form as its own entry; never broaden the gloss to cover
   both senses.
5. **`replaced_by` is append-only.** It migrates each user's saved vocabulary
   (`migrateLookupsToPhrases` in app.js): the old row is replaced by the
   phrase, carrying its look-up/deletion clocks, and the change syncs. A user
   who skips releases must still find their rule, so never delete or rewrite
   an existing rule — chains (word → phrase A → phrase B) are resolved in the
   app, with a cycle guard.
6. Bump the version, `python3 scripts/validate_data.py`, commit.
7. **Gloss-chain audit** (do this after any large vocabulary change):
   `python3 scripts/gloss_chains.py OUTDIR` writes every statement with the
   glosses the app would show and the English translation, one file per
   topic; hand each file to a reader with `docs/GLOSS-AUDIT-RUBRIC.md`. The
   2026-09-11 run over all 7,147 statements flagged 351.

**Content fix** (`questions.json` translations/explanations):
1. Edit only `english_translation` / `explanation` / `explanation_it` (see Rule 1).
   - A statement may also carry `warn` / `warn_it`: a short note that the
     Ministry's wording is ambiguous and the official reading must be
     memorized. Reviewers feed this list via the 'Ambiguous wording' flag
     category. It surfaces in two places, and they follow DIFFERENT rules on
     purpose: the 🤔 **badge** on a study card appears at L1/L2 only, never at
     L3 or in the mock exam, because it arrives unasked and before the answer,
     where those two mirror real exam conditions; the **Ambiguous list** on the
     Reference screen appears at every level, because a question judged
     ambiguous is ambiguous at every level and that page is one the learner
     opens deliberately to memorize things. The list was briefly gated at L1/L2
     too, by copying the badge's rule, which withheld it from the learner
     closest to sitting the exam (corrected 2026-09-17). Its tab is hidden only
     when the bank holds nothing marked, which today is one statement.
2. Bump version (both markers).
3. `python3 scripts/validate_data.py`, then commit.

## Verify before every commit
- `python3 scripts/check_review_placement.py` — glossary rules 13 (no sign
  explained away from its image) and 10 (no em dashes in review prose). Run
  after any topic-review edit.
- `python3 scripts/check_review_english.py` — glossary rule 41, **plain
  English**. Fails on slang, on an idiom only part of the English-speaking
  world would know (baseball, cricket), on a figure of speech standing in for
  a rule (a category that *owns*, a family that *lives* on a road, a rule that
  *bites*, a vehicle that *wins* at a junction), on the notes naming the exam
  or the quiz, and on conversational filler. It checks the Italian half too,
  where the same figures were written (*vive sulla strada*, *il quiz adora*).
  66 phrase patterns, and it **must stay at zero hits**: a pattern that fires
  on ordinary English is a bug in the pattern, so tighten it rather than
  reword good prose. Single words do not work here and were tried first (201
  hits, a dozen real), which is why "kind of" and "sort of" are deliberately
  absent. Add a pattern whenever a new offender is found. A fourth family,
  `reader`, was added on 2026-09-16: the English half is written FOR
  Americans, so "what Americans call X" hands the reader a foreign term and
  translates their own word back to them. Name the part the way they name it
  and gloss the ITALIAN word instead. See glossary rule 42. The `exam` family
  was rewritten on 2026-09-16 to match the NOUN rather than a list of verbs,
  after a sweep found 60 mentions that the verb patterns had missed. It bans
  "the exam", the attributive uses ("exam figures", "exam bank"), "quiz"
  outright, "the bank tests/marks/uses", and on the Italian side the elided
  article (*l'esame*, *d'esame*, *all'esame*). Italian keeps bare *esame* in
  its real sense, the test you sit for a license, which topic 22 needs.
  **One exemption**: a block that opens with the fixed string
  `**How the exam phrases it.**` / `**Come lo chiede l'esame.**` may name the
  exam, because its subject IS how the Ministry words its statements. Four
  topics carry it (02, 03, 04, 05). The exemption is keyed to that literal, so
  it cannot spread, and the other families still apply inside the block. See
  glossary rule 48. **Two more signals were added on 2026-09-23**, after the
  reading pass described in the next bullet: a `fragment` family that bans
  the equals-sign legend (`yellow = special`, `A = your lane`) and the arrow
  (`130→110`) in both halves, and a British-word list in the `reader` family
  (centre, tyre, give way, dual carriageway, turn indicator, dipped beam,
  towards, and so on). Words this corpus uses legitimately are left out on
  purpose: *carriageway* is the app's term for *carreggiata*, *gearbox* is
  ordinary US automotive English, *queue* names a panel, and "give way" is
  exempt before "under" (a shoulder that gives way under a wheel, topic 03).
- **COMPLETE SENTENCES, in the reviews and in the explanations alike.** The
  maintainer has now raised this twice, the second time on 2026-09-21 about
  *"the short halt you make with the driver still there"*. No regex catches
  it, so it is a writing rule and it is on whoever writes the line. **A
  reading pass over all 25 topics was made on 2026-09-23** for exactly this,
  one commit per topic, after the maintainer asked whether many small edits
  had drifted the reviews away from the rule. They had, in three shapes that
  a regex does not see: a NOUN LIST under a heading that supplies the verb
  ("What it depends on: / Your own speed."), which topics 09, 10, 11, 12, 15
  and 22 all had and which now reads "It depends on your own speed"; a bold
  LABEL with a colon and a fragment after it ("**Secondary extra-urban road**:
  **90 km/h**"), now "On a secondary extra-urban road the limit is 90 km/h";
  and the summary written as a legend ("Yellow = special; blue = paid
  parking"), which is the one shape the script now catches. The summaries
  were the worst of it, because a summary invites compression. The pass also
  found real errors under the fragments: topic 11's summary said every limit
  drops in rain when only the two highest do, and topic 12's fermata rule
  outside town omitted the shoulder that art. 157 c. 3 names. Read a topic's
  English half as a column of numbered lines (`awk '/LANG: en/{p=1} /LANG:
  it/{p=0} p' FILE | grep -v '^$' | grep -v '^!\[' | nl -ba`) and the
  fragments show up by shape before they are read. Edit both halves to the
  same sentence count, and keep the claim markers on the line they were on.
  The
  failure is always the same shape: a definition stuffed into an appositive
  rather than given its own sentence. *the short halt you make with the driver
  still there*, *mopeds and motorcycles under 150 cm³ among them*, *a bay
  beside the carriageway for a fermata, the short halt made with the driver
  still at the vehicle*. Each names a thing and then leans a clause on it, and
  the clause is where the meaning went, so the reader has to reassemble the
  sentence to find out what was said. "With the driver still there" does not
  even say where *there* is. Write it out: **a fermata is a brief interruption
  of the journey, and the driver does not leave the vehicle.** Longer, and it
  is the only version a learner can read once. The same applies to the
  explanations: a sentence carrying two appositives and a subordinate clause
  is not terse, it is compressed, which the UI-prose section already
  distinguishes.
- `python3 scripts/check_review_bullets.py` — glossary rule 40, **one rule per
  bullet**. A grab-bag bullet cannot be claimed precisely and leaves the
  learner guessing which sentence answers the statement, so the two mechanical
  signals (a semicolon, and two or more sentences opened by a bold label) are
  ratcheted against `docs/review-bullet-baseline.json` and may never grow.
  When a cleanup lowers a count, re-run with `--save-baseline`; `--list
  semicolon` or `--list labels` prints the offenders. Judging the rest is the
  claim readers' job (`split`), not a regex's: scoring by sentence and bold
  count was tried and flagged coherent teaching.
- `python3 scripts/check_vocab_glosses.py` — glossary rule 14: a vocabulary
  gloss translates, it never teaches a driving concept. Run after vocabulary
  edits. (Glosses are revealed by CLICK, not hover: the click is what records
  the look-up. See glossary rule 25.)
- `node --check public_html/app.js` — JS syntax.
- `npx --yes eslint@8.57.0 --no-eslintrc --config .eslintrc.json public_html/app.js public_html/sw.js`
  — no-undef, no-redeclare, no-dupe-keys. **Run this after every app.js edit**:
  `node --check` does not catch a call to a function that an edit deleted (it
  happened on 2026-09-05). `no-redeclare` was added on 2026-09-17 after a
  SECOND `firstUnansweredIndex` sat in the file for five days: JavaScript keeps
  the last declaration, so the drill silently resumed by the other function's
  rule while the comment above the first one described what it used to do.
  Nothing flagged it, because `node --check` accepts a duplicate declaration
  and `no-undef` has nothing to say about one. If two call sites want different
  answers, give them two names.
- `public_html/reference.json` feeds the **Reference** screen (the numbers; the nav
  button was "Review" until 2026-09-11, and its element ids still say `vocab`).
  Every number must be traceable to a statement it cites or to its topic's
  review, or `validate_data.py` fails; never add a figure that is only read off
  a pictured sign, and never one whose only source is a FALSO statement (that
  is a trap, not a fact). Rows may carry `"noWrong"` (the exam never prints a
  different figure) or the stronger `"alwaysTrue"` (every statement in that
  topic carrying the figure is VERO); both are re-verified by
  `validate_data.py`, so a bank revision breaks the build rather than
  misleading a learner. See `docs/review-glossary.md` rules 34 to 38.
  **Speeds appear twice on purpose** (2026-09-24, maintainer's request):
  category `speed` groups them by road type, category `speedveh` by vehicle
  (`by_car`, `by_new`, `by_tow`, `by_truck`, `by_quad`, `by_moped`,
  `by_farm`). The two are separate rows with the same sources, so a change to
  a limit is two edits; only figures a statement tests are listed, which is
  why the autotreno's autostrada 80 and a new driver's unchanged limits are
  not rows. **Points and penalties (20261003g).** The maintainer asked on
  2026-09-26 for a table of points lost per violation, then, on seeing it
  built from the Code's art. 126-bis table, asked which of those numbers the
  bank tests: one, the 2 points for emergency towing (23956). His
  decision, after a release that had dropped the figures altogether: SHOW
  the Code's figures, be clear which numbers are tested, and list the
  violations tested as costing NO points as rows at zero. So group `points`
  holds the system figures (20 to start, 15 at most at once, double in the
  first three years, 6 from a course, three 5-point losses in a year, over
  10 km/h, over 40 km/h), and group `lost` holds twenty-four violation
  rows: the towing row and the nine zero rows (24666, 24668, 24669,
  24676, 24670, 24674, 24673, 24675, 24665) carry `"tested": true` and a
  violet pill "number tested" (removed in 20261011b, maintainer: the "Asked in N
  questions" count under the value says it) (the zero values drawn muted and at normal weight, `.is-zero`, maintainer 2026-09-26: there is no figure to remember, only that no points are taken; the pill still marks them tested); the fourteen others carry `"untested":
  "art. N …"` (the Code article, doubling as the flag), a muted pill
  "number not tested", and a muted value. The group note says the same;
  its foot keeps the two facts that are not violations (points not doubled
  for a powerful vehicle, 24671 and 24672; no withdrawal on the spot,
  24586). `validate_data.py`: an `untested` row names an article and cites
  only statements that test the point loss; a `tested` row must pass the
  ordinary source check, except a ZERO row, whose figure never appears in a
  statement and which must cite only FALSO statements claiming a loss; a
  group holding untested rows must hold at least one tested row (all three
  proved by sabotage). **23000 was wrongly a zero row for one release
  (20261003g to j)**: it is FALSO because stopping at the right edge
  without signaling costs 2 points (art. 154 c. 8), not 4, and its own
  explanation said so. It is now an untested 2-point row. Read the
  explanation of a FALSO statement before calling its figure zero.
  **A tested row may also name the WRONG figure the bank uses (20261006f,
  maintainer, 2026-09-30).** The towing row is asked twice: 2 points VERO
  (23956) and 4 points FALSO (23960). It carries `wrong: {value, valueEn,
  src}`, drawn as a muted line under the label in the maintainer's wording
  (20261006g): "Asked in two questions: once with the correct value (true)
  and once with the incorrect value of 4 points (false)", with no question
  number, and hidden while the values are hidden. `validate_data.py` requires every cited statement to be
  a live FALSO one carrying the wrong figure, and refuses the field on an
  untested or never-faked row (proved by sabotage).
  `check_points_table.js` asserts the line, 19 checks in each face.
  **Fines (20261003k, maintainer's request).** Eighteen violation rows carry
  `fine: {value, valueEn, art, noteEn?, noteIt?}`, drawn as a muted line
  under the label ("Fine: €87 to €344"). No fine amount is tested. The
  amounts are the Code's as in force for 2026: art. 195 c. 3 revises them
  every two years by ISTAT, the update was suspended for 2024, 2025 and
  2026, and the next may take effect from January 2027, when every fine
  here must be re-checked. The six lawful or not-required rows (ownership
  certificate, another owner's vehicle, new driver on the autostrada,
  eight-seat car on C, light truck on a holiday, racing on a private track)
  carry no fine. The validator requires an article and matching digits.
  Topic 22 gained "## Fines, cameras and the owner" in both halves
  (art. 126-bis c. 2, 196, 202): the owner owes the fine jointly, points
  come only off the driver, a camera ticket goes to the owner, who must
  name the driver within 60 days or pay €291 to €1,166 with no points
  lost, and paying within 5 days takes 30% off. No statement tests it, so
  it carries no claims. `scripts/check_points_table.js`, 18 checks in each
  face.
  **The category is "Penalties" / "Sanzioni" since 20261003l** (it was
  "Points and penalties"), and it holds a third group, `measures`,
  "Suspension, withdrawal, revision and revocation": 23 rows, each a
  violation with `"measure": true` and the measure as its value (Ritiro,
  Sospensione, Revisione, Revoca), in that order since 20261004v: the time
  sequence that leads to the worst outcome (maintainer, 2026-09-29). The
  police withdraw on the spot, the Prefect then suspends, a revision may
  follow, and failing it revokes. 20261003m had put suspension first on the
  belief that a withdrawal follows a suspension, which is backwards; the
  group note always said the police act first. Topic 22's section heading
  and bullet order follow the same sequence. Every row is cited to VERO
  statements of topic 22 (24577 to 24627, 24589 to 24610, 24641). The
  validator requires one of the four measures and VERO sources only
  (proved by sabotage). The group note says who orders each measure; its
  foot lists what the bank tests as bringing none of them, cited to the
  FALSO statements. The handheld phone suspension of the 2024 reform is in
  topic 22's notes but tested by no statement, so it is not a row. Every
  row is tested and the list is NOT the Code's complete one; the note says
  both, so no per-row pill is needed here.
  **Each measure is DEFINED on the page (20261004w, maintainer,
  2026-09-29: "otherwise those are just words")**: the group carries
  `defs`, keyed by the stored value, one short definition per measure
  (who orders it and what it means for the driver). With the values
  showing, each run of rows opens under its measure's name and definition
  (`.review-def`); with the values HIDDEN a heading over a run would give
  every answer away, so the four stand together above the rows
  (`.review-defs`). The group note lost its two sentences on who orders
  what, which the definitions now carry. `check_points_table.js` asserts
  both modes.
  **One measure row is not topic 22's (20261004n, flag 25126)**: the
  withdrawal of the REGISTRATION document for a vehicle emitting too many
  pollutants, cited to 25126 (topic 24), labelled "not license" so it is not
  read as a license withdrawal. It is the only statement in the bank that
  ties a measure to the carta di circolazione.
  **Row labels carry NO ARTICLES (20261003h).** The maintainer's rule from
  his own slides, 2026-09-26: drop every definite and indefinite article and
  the meaning survives, with the rare exception where one is needed. Both
  faces of every `numbers` row were stripped by regex and then read; the
  keeps are the Italian relative *la quale*, the numeral *una barra*, the
  pronouns *un altro* and *lo* (*se veicolo non lo è*), the fixed phrase
  *dare la precedenza*, and the article that marks a noun in *un tre ruote*
  / *un due ruote*. A capital A at the start of a label was the trap: the
  regex read the A license as an article. Group notes and foot items are
  sentences and keep theirs. Write a new row the same way.
- **Each Reference figure says how many questions turn on it (20261010z,
  maintainer's bug report, 2026-10-04).** `asked` on a `numbers` row lists
  every live question you need that figure, in that context, to answer,
  VERO or FALSO, including a FALSO one that offers a different figure for
  the same context. It is a full list, unlike `src`, which cites examples.
  Drawn as "Asked in N questions" (`.review-asked`, accent color) right
  under the value, right-aligned in `.review-valcol` (20261011a,
  maintainer: it says which figures must be learned, so it should stand
  out), with the values hidden too; absent on `untested` rows and on the
  row carrying `wrong`, whose line already says how often. Counts run from
  1 to 20. The lists came from readers over every candidate (statements
  carrying the digits, plus their card siblings), recorded in
  `docs/reference-counts/` with their doubts; the speed rows that appear by
  road and by vehicle share one merged list. `validate_data.py` fails on an
  untested row with a list, a tested row without one, or a listed
  statement that is no longer live. Three citations were corrected from
  the same reading: 23921 moved from the rider's age to the passenger's,
  24651 and 23903 dropped from the 20-point and 24-hour rows they did not
  test. A new statement or a bank revision needs its row's list redone.
  `scripts/check_ref_asked.js`, 4 checks in each face.
- **Engine sizes and power share one category since 20261014b**
  (maintainer, 2026-10-14: they are closely related, and the two figures
  of a limit should be read together). Category `power` is now "Engines
  and power (cilindrata e potenza)" and comes before `size`, which is now
  "Sizes and seats (dimensioni e posti)". The rows stay separate, so each
  figure keeps its own "Asked in N" count and its own hidden value, but
  they are GROUPED so the figures of one limit sit together: `vehicledef`
  (moped 50 cm³, over 50 cm³, 15 kW, 0.25 kW), `lic_a1` (125 cm³, 11 kW,
  0.1 kW/kg, with a note that all apply at once), `lic_a2` (35 kW,
  0.2 kW/kg), `moto_auto` (150 cm³ on the autostrada). Groups render in
  the order of the shared `groups` list, so `vehicledef` moved ahead of
  `license` and the autostrada row has its own group rather than the
  speeds' `autostrada`, which must stay first. The over-50 row's Italian
  label said *motocarrozzetta* (a sidecar combination) for the motor
  tricycle and now says *triciclo*.
  **A group may keep its file order (`keepOrder`, 20261014c,
  maintainer).** Rows in a group are otherwise sorted largest first, which
  is right for the speeds. `vehicledef` mixes cm³ and kW, so it keeps the
  order written in reference.json, from the smallest vehicle up: the
  pedal-assist bicycle, the moped, the motorcycle and tricycle, the
  non-light quadricycle.
- **Lengths on the Reference page carry US equivalents (20261006h, reviewer
  flag 24104, 2026-09-30).** A `distance` or `size` row may carry `us`, the
  rounded equivalent in in, ft or mi ("8 in", "4 ft 11 in"), appended in
  parentheses to the value for a non-Italian browser only; the two categories
  carry `noteEn`, one line on converting (divide cm by 2.5, multiply m by
  3.3), drawn under the category title in English only. `us` cannot go in
  `valueEn`, which must carry the same digits as `value`. Speeds and the two
  tread depths carry none. **Road distances are in YARDS since 20261028t** (maintainer,
  2026-10-28, on "500 m (1/3 mi)"), the house standard of
  docs/review-glossary.md that the notes already followed: every
  `distance` row of 9 m or more gives yards (500 m is 550 yd, 150 m 165 yd,
  14 m 15 yd), the short ones keep feet (5 m 16 ft, 1 m 3 ft), and the
  `size` rows keep inches and feet. The category note now says to multiply
  meters by 1.1 for yards. `validate_data.py` fails on a distance of 9 m
  or more not in yards (proved by sabotage); `check_us_units.js` asserts
  550 yd, 22 yd and 3 ft. **Widened the same day (20261028v, maintainer):
  every length in meters is given in yards and every length in centimeters
  in inches, throughout the app, never feet or miles.** Under 10 m the yards
  carry one decimal (1 m is 1.1 yd, 5 m 5.5 yd, the child-restraint 1.50 m
  1.6 yd), 10 to 99 m whole yards, 100 m and up to the nearest 5 (500 m is
  545 yd). Applied to the Reference page, the English notes (topics 04, 09,
  12, 13, 19, 21) and the explanations; the category notes say to multiply
  meters by 1.1 and divide centimeters by 2.5. `validate_data.py` refuses
  a `us` that breaks it, and `check_us_units.js` sweeps every English note
  and explanation for a meter given in feet or miles (the previous release
  fails three of its checks). **Heights keep feet and inches (20261028x,
  maintainer)**: the vehicle height limit 4 m (13 ft), the child-restraint
  1.50 m (4 ft 11 in) and the mirror's 1 meter (3 ft) mounting height. The
  validator allows feet on a Reference row whose English label says
  "height"; the check allows them where "height", "high", "higher" or
  "tall" sits near the figure. The same pass caught spelled-out forms the
  first one missed: the cyclist gap 1.5 meters (1.6 yd) in topic 10 and
  23472, and 5 meters (5.5 yd) in topic 12 and 23686. The explanations of 24104 and 24105 give the
  inches in English only, and topic 21's English half writes 30 cm as
  "30 cm (12 in)", the way it already wrote 50 cm and 20 cm. The mirror row
  names 24104's 50 cm through `wrong`, and the 30 cm row now names the
  T.A.T.S. boat and cites 24105. `scripts/check_us_units.js`, 7 checks in
  each face; the previous build fails 6.
- `public_html/review_anchors.json` maps a card (base id) to the review
  section its 📖 button and image open when the review has no figure for it.
  A heading may be a `## ` section or a `### ` sub-section, named in EN and IT.
  Hand-maintained; `validate_data.py` fails if a card, heading or topic does
  not exist. When renaming a heading, update the map. An entry may instead
  name a figure (`{"img": "domandeb_images/…"}`) when a variant card shows a
  different subject from its base card.
  - **Per-statement anchors.** An entry may carry
    `"stmts": {"24090": {"en": …, "it": …}}`, and such an override may also
    carry `"topic"` (the full topic string) to open ANOTHER topic's review.
    The card-level 📖 button anchors to the first statement on the card
    still unanswered, then to the first standing wrong, then to the card,
    and decides at CLICK time. That guess fails at the most natural moment,
    right after answering (the first unanswered is then the next
    statement), so since 2026-09-12 every statement row carries its own 📖
    (`.stmt-book`), which opens the notes at that statement's landing
    (`reviewTargetFor(q, number)`, the one function behind both buttons and
    the pinned image). It sits at the **top right of the statement box**, on
    the number line (`.stmt-head` / `.stmt-head-aids`), where the IT pill also
    lives. **Keep the answer row to three controls** (🔊, V, F) with its wide
    anti-mistap gap: the 📖 was briefly a fourth one there and the row stopped
    fitting a 320 px phone, where `justify-content: flex-end` pushes an
    overflow off the LEFT edge, so the 📖 sat outside the card with half of it
    past the screen (2026-09-13). Narrowing that gap instead made the row fit
    but looked wrong, so the placement, not the spacing, is the fix. One CSS
    trap found on the way: a SECOND `#card-statements .stmt-btns` block
    further down style.css sets the gap, and being later with equal
    specificity it silently beats the first. Grep for every rule on a
    selector before concluding a value is unused. This exists because a
    card is a bundle: card 4567 is 26 trailer statements, so its card-level
    anchor is a compromise, while 24090 (insurance) wants a sub-section and
    24106 (BE, C, CE) wants topic 22 entirely. Add one whenever a statement's
    subject is not where the card's anchor lands.
  - **CLAIMS are the robust mechanism; everything below this bullet is the
    fallback for topics not yet claimed.** A block of the ENGLISH review may
    end with `<!-- q: 24094 24095 -->`: those statements' 📖 opens that
    paragraph (Italian twin via `pairs`), outranking the card's anchor. **The
    card's OWN drawing, when the review carries it, outranks a same-topic
    claim since 20260930p** (maintainer's decision, 2026-09-24, flag 23161,
    chosen over two narrower options with the cost stated: in the sign topics
    about 400 statements were claimed onto a RULE the figure's caption does
    not state, and those now open at the figure instead). 705 statements
    changed landing. A claim or anchor in ANOTHER topic still wins, and a card
    whose drawing is not in the review keeps its claim
    (`scripts/check_book_landing.js`, 3 checks, fails on the old build). The
    claims still matter: they drive the Final Stretch rule rows and the landing
    of every card without its drawing, and a claim may sit in another topic's review (24106 sits in
    topic 22). The claim lives next to the paragraph, so rewording carries it
    along and an editor sees which statements depend on the line. Two
    file-level markers on their own line under `<!-- LANG: en -->`:
    `<!-- absent: N N -->` (the notes deliberately state no rule for these;
    build-side accounting only, the app treats them like unclaimed ones or
    the landing would leak the answer) and `<!-- claims: complete -->`
    (every statement of the topic is claimed or absent; `validate_data.py`
    FAILS otherwise, and the app stops running the picker for that topic).
    **A third marker, `<!-- claims: rules -->`, is the picture-topic form**,
    decided by the maintainer on 2026-09-19 on this recommendation: in a
    topic where nearly every card carries its sign, the statements that
    IDENTIFY the pictured sign already land on that figure, so the pass
    claims only the statements that test a RULE the figure's own block does
    not state (placement distances, panel arrows, what a whole family may
    never do) and leaves the rest to the image. `rules` does NOT retire the
    picker: an unclaimed statement there behaves exactly as before the pass,
    which is what stretching `complete` would have broken. What it enforces
    instead is the promise the lighter pass rests on: `validate_data.py`
    FAILS if an unclaimed statement sits on a card with NO picture, because
    nothing but a guess is left for it. Readers of a picture packet answer
    each statement with a block, `"figure"` (the pictured sign or its
    meaning, which the figure's caption states) or `"absent"`;
    `claims_apply.py --rules` writes the marker.
    The build strips all three markers; `md_to_reviews.py` ships
    `claims: {statement: EN hash}` and `complete`, and refuses a claim on an
    English-only block. `validate_data.py` checks existence, one claim per
    statement, stale maps, and prints coverage with the VERO/FALSO split.
    Workflow for a topic: `python3 scripts/claims_packet.py NN OUTDIR`
    (numbered blocks with Italian twins, every statement with a machine
    proposal, and the rubric in README.md), have readers return
    `decisions.json`, `python3 scripts/claims_apply.py OUTDIR [--complete]`,
    rebuild, validate. Topic 21 was the pilot (2026-09-12): 320 claimed, 12
    absent, 133 of 147 machine proposals confirmed, two blind readers agreed
    on 38 of 40. Done so far: 21, 16, 13, 24, 20, 23, 11, 22, 14, 12, 17, 10, 18, 19, 09 (every text topic); rules pass: 03, 01, 04, 06, 05, 15, 07, 08, 02. **The rollout is FINISHED as of 2026-09-20**: all 25 topics are claimed. Topic 25 was the one the rules pass could not serve, because that pass rests on the card's drawing being in the review and only 9 of its 49 junction cards have theirs there, so it was done as a full `complete` claim onto the rule bullets instead: 414 claimed, 0 absent, of which 231 land on the right-hand rule alone. That concentration is the honest shape of a topic whose subject is the drawing, and four rules were added to close the gaps the readers found (when two vehicles cross together, who waits at the centre, how a locked ring is broken, moderating speed at a junction). Its manual cross-check was the strongest of the rollout: no contradiction anywhere, and all seven worked examples match the Ministry's own solution list figure for figure. Topic 08's lesson (2026-09-20): a rules pass that comes back almost entirely `figure` may be RIGHT, and the test is structural rather than statistical. There it returned 252 of 260 as figure against 16% and 24% claimed on topics 15 and 07, because each panel type has its own bullet under its own picture, so the general reading rules ARE the figure blocks and nothing is left for another block to decide; the blind check agreed 40 of 40. Check what the figure blocks actually contain before calling a lopsided result lazy. Build the packet only AFTER `md_to_reviews.py`: `claims_packet.py` reads the blocks from the markdown but `pairs` from the shipped JSON, so a block edited since the last rebuild prints as "(none: English-only, not claimable)" and a reader will route its statements elsewhere (cost a blind check on topic 15, 2026-09-19). Edit the review BEFORE `claims_apply.py` and rebuild the packet after: an edit between packet and apply changes the block hashes and the apply refuses the file, though the IDs are positional so the same decisions.json applies again over a rebuilt packet. A block's twin is checked for EXISTENCE, never for meaning, so two blocks whose order differs between the language halves pair with each other's twin and the IT pill shows the wrong paragraph, silently (topic 06, found by both readers on 2026-09-19); keep the two halves in the same order, section by section. The picture packet is `claims_packet.py NN OUTDIR --picture`, which writes `cards.md` and `README_picture.md`. Two bullets with identical English share one HASH, so the second silently takes the first's claims and IT pairing and nothing flags it; word them apart (found in topic 09, 2026-09-19). `claims_packet.py`
    SKIPS retired statements, added 2026-09-16 after topic 23's packet
    offered readers three withdrawn ones and a gap was reported on 25008,
    whose rule the retirement pass had deliberately removed from that very
    topic. Topic 23's lesson: read the blind check as a MAP, not a grade. It
    returned 32 of 40 against the usual 37 to 39, and six of the eight
    disagreements sat on one card whose section was four bullets carrying 54
    statements, so both readers were guessing in the same empty place. Write
    the missing teaching first and most disagreements dissolve, because the
    two blocks the readers were choosing between are both replaced by a
    bullet that states the rule. Topic 13's lesson:
    a review written as long paragraphs (46 blocks for 379 statements) must
    be SPLIT into one-rule bullets BEFORE the claims are worth anything, so
    the order there was claim, split (46 to 115 blocks, the claim marker
    stays on the first fragment), re-read every statement against the
    fragments, then gaps. Readers also report `gaps` (block covers the subject but
    does not decide the statement), `split` (bullets bundling unrelated
    rules) and `elsewhere` (the rule is another topic's material; build a
    packet for that topic with `--statements N N`, and `claims_apply.py`
    moves the claim, releasing it from the file it was in). Gaps are then
    filled: `python3 scripts/claims_gaps.py NN DECISIONS.json... OUTDIR`
    groups them by their CURRENT block, readers return `additions.json`
    (one addition per block, EN and IT with the same sentence count, the
    rule stated positively, no mention of the exam), and
    `python3 scripts/claims_fill.py OUTDIR` appends a one-sentence addition
    to its block or makes a two-or-more-sentence one a new block right after
    it, re-claiming the statements it covers. A gap on a VERO statement is
    dangerous, not just weak: the standing line tells the learner that an
    absent rule is absent because it is not a rule, so an unfilled gap on a
    true statement misleads. Fill gaps before declaring a topic done.
  - **Paragraph landings** (fallback). Inside the anchored section the app picks the
    one paragraph or bullet the statement is about (`pickReviewBlock` in
    app.js: Italian word overlap between the statement and each block's
    Italian twin from the `pairs` map; it abstains unless one block stands
    clearly above the rest, so the heading remains the floor). Just over half
    the statements get a paragraph. "Clearly above" means a wide enough gap OR
    a two-to-one win: the gap is a share of the statement's own words, so a
    long statement divides every gap down, and a block winning two-to-one
    could still miss a fixed threshold (that kept 24116 on the heading). A
    statement mentioning a *figura* never gets a paragraph, since its subject
    is the drawing. The rule is deliberately the same for VERO and FALSO
    (56% vs 48%): a landing that differed by answer would be an answer key. When the picker is wrong or silent, add `"block": "<hash>"`
    to the card or statement entry: the EN block's hash as the `pairs` map
    keys it (`python3 scripts/review_landings.py --topic NN` prints the
    landings; the hashes are in `topic_reviews.json`). A statement entry that
    names neither a section nor a figure REFINES the card's anchor instead of
    replacing it, so pointing one statement at a paragraph of the card's own
    section is just `"24091": {"block": "1uv9qq1"}` (`reviewAnchorFor` in
    app.js, mirrored in `validate_data.py` and `review_landings.py`).
    `validate_data.py` fails if the hash is not a translated block under the
    effective heading,
    so a reworded paragraph breaks the build instead of landing on the
    heading unnoticed. `scripts/review_landings.py` mirrors the picker in
    Python; keep its token rules identical to the app's.
    - **Inside the paragraph, one SENTENCE is marked.** A bullet is often a
      short list of related rules and the tested one can sit third, so the
      reader lands on a line about something else (24094's hitch rule sat
      behind the electrical connection). 778 statements land past their
      block's first sentence, and splitting every such bullet would be wrong
      because many are one membership list. So `reviewSentenceIndex` picks
      the sentence on the ITALIAN block and reuses the index for the English,
      only when both split the same number of ways, and
      `markReviewSentence` wraps it in `<mark class="rb-hit">` at scroll
      time. 1,284 of the 1,588 multi-sentence landings get a mark; a tie
      marks nothing. The sentence step matches WHOLE WORDS by shared prefix
      (five letters), not the block picker's six-letter stems, which split
      *alcol* from *alcolica* and sent 24623 to the 2024 phone rule; it also
      drops words spread over most of the paragraph's sentences. Keep
      `reviewSentences` / `pickWords` / `wordHit` in step with
      `sentences` / `pick_words` / `word_hit` in review_landings.py. The
      sentence splitter must not cut at an initial (T.A.T.S.), an
      abbreviation (`SENT_ABBR`) or a decimal (3.5 t). That last guard has a
      cost worth knowing: the splitter never breaks after a DIGIT, so a
      sentence ending "at 24." or "outside A1." or "two years of A2." welds
      itself to the next one. When one language ends such a sentence with a
      number and the other adds a word ("24 anni"), the halves split a
      different number of ways, `reviewSentenceIndex` returns nothing, and the
      learner lands on the right paragraph with NOTHING marked inside it. The
      build passes and the pairing is intact, so only
      `python3 scripts/check_review_sentences.py [NN]` finds it. 60 blocks
      across 18 topics are in this state and predate the check; the fix is
      always in the prose, which is to end the sentence with a word.
    - **A block belongs to every heading it sits under.** `## Towing a
      trailer` opens straight into `### Hooking up` and holds no text of its
      own, so a walk that matched a block's NEAREST heading found no
      candidates and silently fell back to the heading: that was 113 of the
      anchors, and it is why the first version looked like it did nothing on
      trailer cards. The walk uses the heading chain, in `reviewBlocks`
      (app.js), `section_hashes` (validate_data.py) and `blocks`
      (review_landings.py) alike.
  - **The standing line.** Opened from a card, the notes show one sticky
    line: a duty, ban or permission you cannot find here is absent because
    it is not a rule. That is how a FALSO statement whose subject appears
    nowhere in the notes is handled. Do NOT add per-statement notices,
    a different icon, or review paragraphs denying invented rules: any
    signal shown before the answer that only FALSO statements can trigger
    leaks the answer, and denial paragraphs are noise in the notes (the
    post-answer `explanation` is where the invented rule gets named).
- **The two progress lines are drawn by one function.** `drawCardSegments`
  (app.js) renders both the sticky line on the nav's bottom border and the
  wider bar in the study header, as ONE SEGMENT PER CARD with a hairline gap,
  so the learner can count the cards left instead of reading a fraction. The
  gap is the CONTAINER's background showing through `gap`, which is why the
  container carries `background: var(--bg)` and the track color sits on the
  segments (`.nav-progress-seg` / `.study-progress-seg`); put the track on the
  wrap instead and the gaps vanish into it. The gap shrinks to 1 px and then
  to 0 as the segments get thin, where the line degrades to a plain two-part
  fill. The two bars were written separately at first and only the nav one got
  the gaps, which a reviewer spotted on 2026-09-16; keep them on the one
  function so they cannot drift again. The dashboard's **topic tiles** use it
  too (`.topic-bar`), drawn after the tiles are appended because a segment's
  width is unknown until the tile is laid out, and redrawn on resize by
  `redrawTopicBars` from counts stashed on the element. The dashboard's
  **overall** bar deliberately does NOT: it spans 849 cards, where a segment
  is under two pixels and the gap heuristic would drop to zero anyway.
  **A cleared segment is always GREEN (20261004g, maintainer, 2026-09-27).**
  Both bars used to color the cleared segments by the topic-wide share of
  answered statements ever answered right, which counted mock exam misses on
  cards not yet studied, so two cleared cards drew in red. The dashboard's
  topic tile keeps the accuracy color; the study bars do not.
- **Replacing an existing image file** (same name, new content): add its path
  to `IMG_REFRESH` in `public_html/sw.js`, or installed apps keep the old
  picture forever (the image cache is keyed by path and never expires).
- `python3 scripts/build_image_aliases.py` after adding or replacing any file in
  `domandeb_images/`. It writes TWO things and `--check` (which
  `validate_data.py` runs) fails on either going stale: `image_aliases.json`,
  which groups byte-identical images so a card can open the review at its twin
  figure, and the **`IMG_DETAILED` set stamped into app.js**.
  - **`IMG_DETAILED` is how the card knows a figure needs room**, and the
    signal is the drawing's NODE COUNT, the number of `path`, `polygon`,
    `polyline`, `text` and `tspan` elements, at or above 30. It separates the
    two kinds cleanly: across the 228 SVG figures the median is 4, a plain
    pictogram being a handful of shapes, while a board of place names or a
    panel of opening hours runs to dozens (4290 has 85, 4292 has 261). Twenty
    figures qualify, so the app gives those the wide path with a 340 px
    ceiling and leaves the other 208 alone.
  - **Two tests were tried first and both fail on this bank.** The declared
    WIDTH, which is what the older `naturalWidth >= 1000` rule reads: that
    works on a photograph, but an SVG's declared size is arbitrary, and 4290
    says 400x370 while 4292 says 600x1260, so both slipped through and
    rendered 141 px and 100 px wide. And TEXT DETECTION: the bank's SVGs have
    their lettering converted to paths, so `<text>` finds nothing in either.
  - **The topic-wide escape hatch is wrong here and was measured.** Topic 01
    holds 12 of the 20 busy figures, but 35 of its 52 SVGs are plain
    pictograms under 15 nodes, so treating the whole topic as diagrams (the
    way `Segnaletica orizzontale` and `Esempi di precedenza` are treated)
    would inflate those 35.
  - **The property to re-check if the 340 ceiling ever moves: no figure may
    get SMALLER.** The detailed path replaces whatever the old rule gave, and
    for a wide figure the old rule's own 240 ceiling could in principle be the
    larger. `/tmp/imgsize.js` mirrors the arithmetic against the real stamped
    set and the real file dimensions and asserts it over all 509 figures; 18
    grow, 491 are untouched, none shrinks.
  - **The 2x ceiling does not apply to an SVG.** It is about RESOLUTION, so a
    vector drawing, which scales for nothing, is exempt.
  - This exists because "the image is too small" was reported six times before
    anyone measured it (4283 and 4291 on 2026-09-21, 20827 earlier, 21396,
    then 21469 and 21488). The reviewer on 21488 read 4292's *polizia,
    ambulanze* exception line as "a police station", which is what a 100 px
    board looks like.
- **Read `validate_data.py`'s EXIT CODE, or grep for the literal `✓ all data
  checks passed`.** It prints a long report and its failures sit near the END,
  under `✗ N problem(s)`, so a grep for a success pattern that simply is not
  there reads as silence and looks like success. That shipped a commit with
  three double-claimed statements on 2026-09-19.
- `python3 scripts/validate_data.py` — answers are VERO/FALSO, no empty English
  fields, no duplicate statement numbers, image/abridged refs resolve, all 25
  topics have reviews, review images resolve, **and version lockstep**.
- CI (`.github/workflows/ci.yml`) additionally runs eslint (no-undef), `php -l`,
  and gitleaks. Keep PHP balanced; there is **no PHP runtime here**, so check
  brace/paren balance manually instead of running `php -l` locally.

## Vocabulary help at the Italian-only level

- **Do not ship hand-written Italian definitions.** Tried and reverted on
  2026-09-17 (commits d8bc277 and its revert). The reviewer compared thirty of
  them against Apple's built-in Italian dictionary and preferred the dictionary,
  correctly: an entry confined to a frozen defining vocabulary can only
  paraphrase, where a real lexicon gives the part of speech, the senses in
  order, the register and an example. Licensed dictionaries cannot be copied and
  the open ones are uneven on technical road vocabulary, so writing them was the
  only route, and writing them is not good enough.
- **The platform already does it, and the app does not obstruct it.** Select a
  word, Look Up, and the OS answers from a proper lexicon, offline, in Italian,
  with no answer-leak risk. At Italian only the statement is rendered as plain
  text, because `highlightVocabInEscaped` runs only when `currentLevel < 3`, so
  no span swallows a long press; the three `user-select: none` rules sit on
  disclosure summaries and the sync code, nowhere near a statement. Keep it that
  way: anything that makes statement text unselectable at Italian only would
  take away the best vocabulary help the app has, without appearing to.
- **The analysis was sound even though the feature was not**, so it is recorded
  rather than lost. Bank frequency alone picks the wrong words: of the 1,833
  entries met once or twice, 1,338 are ordinary Italian where a definition helps
  nobody. Crossing bank frequency with general Italian frequency leaves about
  410 that are rare in both. And the answer-leak risk sits outside any such set
  for a structural reason: a term the bank defines is a term the bank repeats,
  so every art. 3 term carries a high bank frequency (*carreggiata* 207,
  *corsia* 106) and none survives a "met at most twice" filter.
- **The open dictionaries were measured too, and abandoned 2026-09-17.** Italian
  has no open authoritative dictionary: Zingarelli, Treccani, De Mauro and the
  rest are copyrighted (free to READ, so linking is fine and copying is not),
  and what is openly licensed is Wiktionary plus morphological lexicons with no
  definitions at all. Italian Wiktionary via kaikki.org measures better than it
  first looks, if `"femminile di X"` glosses are FOLLOWED rather than discarded:
  138,258 real definitions, 74% of the 5,240 distinct words in the live bank,
  0.13 MB gzipped. It still cannot ship. `banchina` returns the harbour quay,
  `pneumatico` the adjective "che si gonfia con aria", `sorpassare` nothing at
  all, and `carreggiata` a definition that decides the statement. Wrong senses
  in a driving app are worse than no entry, so it needs a per-word sense check,
  which is where the maintainer stopped it.
- **Ask what the person already does before building them something.** The
  report was "I still need to translate words to finish a statement". That was
  a description of a workflow that was already working, not a gap, and hearing
  it as a gap cost a day and produced a worse copy of a tool already on the
  device.
- **That abort covers the ENGLISH-speaking half only, and was written as
  though it covered everyone.** Reopened 2026-09-17 by the maintainer: the app
  is also for native Italian speakers, and every argument above is about
  somebody translating out of Italian. A native speaker studies at Solo
  italiano, where `highlightVocabInEscaped` does not run at all, and the
  Reference vocabulary tabs point Italian to English, so today they have no
  vocabulary aid of any kind. What they need is not a definition of an ordinary
  word, which they know, but which of the bank's words are bureaucratic-
  technical and what those mean IN THAT REGISTER. The SIDA manual is direct
  evidence that the need is real: it is written for Italians and still prints a
  297-entry *Glossario (Vocabolario)* of "alcune parole difficili usate nei
  quiz", median five words each, 230 of whose headwords appear in our live bank.
  Its audience is ordinary Italian candidates, most of them eighteen: the
  preface mentions no non-native reader and explains the German and French
  editions of the exam as serving *le esigenze linguistiche delle comunità
  dell'Alto Adige e della Val d'Aosta*, who are Italian citizens. That matters
  because it is easy to explain away the simple headwords (*posteriore: di
  dietro*, *flusso: corso*) by inventing a reader with poor Italian and then to
  leave them out, which is what happened on 2026-09-17 until the maintainer
  questioned it. A professional editor writing FOR native speakers judged those
  words worth a line, and half his headwords are ordinary-frequency Italian
  (median Zipf 3.08). Do not thin the list on a guess about who needs it.
- **Source a definition from the CODE, not from a textbook.** Art. 3 (58
  numbered definitions) and art. 47 (vehicle classes) are the authority the bank
  is built on, and Italian law (L. 633/1941 art. 5) puts official state acts
  outside copyright, so quoting them is both safer and better sourced than
  paraphrasing a publisher. Use SIDA for the SELECTION signal, which word a
  professional judged hard, and write our own line for anything the Code does
  not define. The maintainer's position, recorded 2026-09-17, is that these
  definitions are common knowledge rather than SIDA's property, and for the
  art. 3 terms that is plainly right. The residual care is narrow: this repo
  ships content under CC-BY-SA, so anything copied in would be relicensed under
  our name, which is a different act from quoting a fact.

## The Reference page (one search, and the folded prose)

- **ONE search field, above the tabs, and it searches all three lists.** The
  maintainer asked for this on 2026-09-20, and the reason it is not three
  scoped boxes is `casello`, reported missing the day before: a learner knows
  the word and not which list holds it, so a scoped box makes them guess the
  tab before they can ask the question. That search now answers Vocabulary 3,
  Glossario 1 in one go. The query lives in `refQuery`, read by all three
  renderers, and it is deliberately NOT saved with the rest of the view state:
  a search is something you are doing, not how you left the page.
- **A search reuses the panes; it does not build result rows.**
  `renderReviewSearch` shows every pane that matched, stacked in the TAB order,
  each under a `.ref-result-head` carrying its count, and calls the SAME
  renderers the tabs call. So every row keeps its own behaviour: + and − still
  move an entry between the study lists, 🔊 still reads it, a hidden number is
  still a button that reveals only itself. The three renderers therefore RETURN
  how many entries they drew, which is the only thing the headings need. The
  panes sit in tab order in index.html so that the DOM order is the reading
  order; do not reorder them.
- **While searching, a search ignores every scope control, because they are
  hidden.** The list tabs go to "All entries", the entry-type filter to "all",
  the Numbers category chips to "all". A filter still biting while the reader
  cannot see it answers a different question from the one they asked. Each
  pane's own empty line is silenced too, since the page prints one
  `#review-search-empty` for a search that found nothing anywhere.
- **A tab tapped DURING a search narrows that search to the list it names, and
  keeps the query.** The first behaviour threw the query away, on the reasoning
  that the tabs were the way out of a search; the maintainer reported it the
  same day (2026-09-20), and he is right: someone who has just typed a word and
  then picks a list has not finished with the word. So the tab goes on meaning
  what it always means, which list you are looking at. Editing the query widens
  it back to all three, so the narrow view is never a state to escape, and
  clearing the box leaves you browsing the list you narrowed to.
- **Every list is still SEARCHED while only one is SHOWN, because the counts go
  on the tabs** (`.review-section-btn[data-count]`, styled to appear only while
  a count is stamped). Narrowing that also hid the other counts would take back
  the thing this search exists for: a reader who taps Glossary, finds nothing
  and concludes the word is nowhere, while Vocabulary holds three. For the same
  reason the empty line has two faces, `review.searchNone` and
  `review.searchElsewhere`: "Nothing matches that search" is a FALSE statement
  when the word sits in a list the reader has narrowed away from. That element
  therefore carries no `data-i18n`; `renderReviewSearch` owns it.
- **The Ambiguous tab is not searched.** It holds whole official questions to
  memorize, not entries to look up, so it is the one tab a search cannot narrow
  to. The query is therefore PARKED in `_refParked` while the reader is there,
  the box is emptied, and the next list tapped gets the search back, narrowed
  to it. Ending the search outright was the first behaviour and the maintainer
  asked for this the same day (2026-09-20): emptying the box on that tab makes
  sense, losing the word does not, because the detour is usually a look and not
  a change of subject. Typing anything, or clearing the box by hand, discards
  the park, so a search the reader has finished with never comes back.
- **A PHRASE also searches the words inside it.** Asked for on 2026-09-20.
  `refNeedles` breaks the query into every contiguous run of its words, longest
  first, so "distanza di sicurezza" asks for the phrase itself, then `distanza
  di`, `di sicurezza`, `distanza` and `sicurezza`. What is DONE with those
  needles changed later the same day, and the exactness bullet below is the
  current rule; this one is only about how the query is cut up.
- **FUNCTION WORDS are dropped from the needles, not merely short ones.** The
  first rule was a three-letter floor, and it is not enough, because Italian
  carries its grammar in words of three and four letters. "per l'accesso dei
  veicoli alle proprietà laterali" was still searching for `per`, `alle` and
  `dei`, and the reader got most of the dictionary back (reported 2026-09-20:
  404 vocabulary rows and 110 glossary definitions, against 68 and 26 once the
  stopwords went). `per` alone matches 271 vocabulary rows and 74 glossary
  definitions, so one preposition was doing more damage than the whole rest of
  the query. `REF_STOPWORDS` holds the prepositions simple and articulated, the
  articles, the basic conjunctions and relatives, and the English function
  words the glosses need. A run of two or more words is dropped too when EVERY
  word in it is a stopword, so "di un" goes and "dei veicoli" stays.
  Two things the list must not break, both covered by the harness. A query
  that IS one of these words still searches for it, because `refNeedles`
  returns early on a single word and never consults the set, which is the same
  reasoning the three-letter floor already carried. And an ELIDED form is not
  listed: the query is split on whitespace, so `l'accesso` is one token, and
  listing `l'` would do nothing anyway.
- **An elided token also searches for its TAIL** (`refElidedTail`). Splitting
  on whitespace leaves the article glued to the noun, so `l'accesso` reached
  nothing at all and the one-word entry `accesso` was missing from the results
  (reported 2026-09-20, the last of four rounds on that one query). A single
  word carrying an apostrophe now yields two needles. Both forms are KEPT,
  never swapped: 53 vocabulary entries begin with an elided word of their own
  (`l'inversione di marcia`, `all'occorrenza`), and dropping the article would
  stop the query reaching those. The prefix test is a LENGTH test rather than a
  list of articles, since every elidable one is short; `e'`, the bank's
  spelling of *è*, has an empty tail and is left alone.
- **A PHRASE query is EXACT: the entry must BE a needle, not contain one.**
  The maintainer set this on 2026-09-20 in his own words, after four rounds in
  which I loosened a looser rule instead of replacing it: "I would expect the
  exact phrase if it is matched. Then I expect any multi-word subphrase, if it
  is matched, and then any word, if it is matched. But nothing else." So an
  entry is shown only when it IS the whole query, a contiguous run of two or
  more of its words, or one of its words, compared through `refTermKey`, which
  folds accents and strips a final vowel from each word of five letters or
  more, so `veicoli` is the entry `veicolo` and `laterali` is `laterale`.
  "per l'accesso dei veicoli alle proprietà laterali" returns five vocabulary
  rows, `veicolo`, `laterale`, `accesso`, `proprietà` and `proprietà laterali`,
  against 144 when that day began, and one Glossario row.
- **ONE exception to the equality rule, added 2026-09-21: an entry also matches
  when it CONTAINS THE WHOLE QUERY as a contiguous run of its own words.**
  Searching `poligono di tiro` returned nothing at all while the single word
  `poligono` returned `poligono di tiro a segno`, so typing MORE of the phrase
  lost the entry. Equality cannot serve a query that is the head or the tail of
  a longer entry, which is the ordinary way somebody half-remembers one.
  `refKeyHasRun` does the test, on `refTermKey` keys, so the inflection folding
  still applies.
- **It is the WHOLE QUERY only, and that restriction is what keeps the
  exception from undoing the rule above.** Measured before shipping: letting
  EVERY needle match by containment takes `distanza di sicurezza` from 2 rows
  to 25 and "per l'accesso dei veicoli alle proprietà laterali" from 5 to 12,
  which is the blow-up the equality rule was written to stop. At the whole
  query alone the long one adds NOTHING, since no entry contains it, and
  `distanza di sicurezza` adds eight entries that each literally contain the
  phrase typed. Measure a loosening on both queries before believing it is
  contained.
- **The rule needs two or more words to run.** A single elided token is a
  SINGLE word and takes the browsing path. `refKeyHasRun` refuses a one-word
  run anyway, since that would be a plain contains match on every entry
  holding the word.
- **A single elided word ALSO searches its tail, and the browsing path is
  chosen by the QUERY's word count, not the needle count** (fixed 20260928i).
  Until then `refNeedles` returned early on one word BEFORE the tail rule ran,
  so `l'andamento` and `un'autorimessa` found nothing although `andamento della
  strada` and `autorimessa` are both entries (flags 22253, 21924, 21861,
  2026-09-22). The comment above `refKeyHasRun` had always said a single
  elided token yields two needles; the code did not. Now it does, and
  `refFilterRank` filters by EITHER needle on the browsing path; deciding that
  path by `needles.length === 1` would have sent the two-needle case down the
  exact-phrase path, where `l'accesso` matches only an entry equal to one of
  them.
- **A typographic apostrophe is folded to the plain one in `refNeedles`.** iOS
  types ’ for ' by default (smart punctuation), and every entry is written
  with the plain one, so a query typed on an iPhone missed even the FULL
  elided form, `l’inversione` finding no `l'inversione di marcia`, while the
  same query typed on a Mac worked. The reviewer's own note was typed with a
  ’, which is how it was spotted. Any new string comparison against a typed
  query needs the same fold.
- **Four more holes, closed in 20261007n (reported 2026-10-01: "sull'impresa
  assicuratrice" found nothing)**, found by a sweep that cuts 2- to 4-word
  phrases out of the live statements and asks the search for each one in
  which the app's own gloss highlighter finds an entry. Before: 198 of 7,037
  such phrases returned no vocabulary row. (1) An elided first word kept its
  article inside a longer run, so `impresa assicuratrice` was never a
  needle; a run of two or more words opening with an elided word now also
  yields the run without that article, and the whole query in that form
  ranks as the whole query. (2) Punctuation glued to a word (`nell'ordine:`,
  `veicolo,`, quotes, parentheses) is stripped; letters, digits, the
  apostrophe, the hyphen, the slash (`km/h`) and a decimal separator
  between digits (3,5) stay, and a trailing apostrophe stays (`E'`, the
  bank's spelling of è). (3) A run of two or more function words is tried
  (`in cui`); only a lone function word is still skipped, which keeps the
  long query at its five rows. (4) `refTermKey` folds a final vowel from
  four letters up, not five (`aree`/`area pedonale`, `essa`/`esso`). After:
  0 of 7,036, plus the one phrase made only of function words ("cui la"),
  left alone on purpose. `scripts/check_ref_search.js` asserts the recorded
  cases (the long query's five rows and one Glossario row, `poligono di
  tiro`, single-word browsing) and runs the sweep; the previous build fails 7.
- **`/tmp/rs/refsearch.js` checks both, 13 cases**, by lifting the search
  functions out of app.js with a brace matcher and running them against the
  real `vocabulary.json` and `glossary.json`, no DOM needed. It re-asserts the
  recorded regressions too (the long query's five rows and one glossary row,
  `veicoli` at 124, `prescrizione` finding its family, `poligono di tiro`).
  Proved to bite: restoring the old early return fails 7 of 13.
- **The ordering is no longer imposed, it falls out**, and it reads off the
  maintainer's own list of what he expects: the entry that IS the whole query,
  then an entry containing the whole query, then an entry equal to a shorter
  needle, and within each band by entry length, so single words come before
  two-word phrases.
- **THREE earlier rules were deleted, not layered.** A three-word cap on what
  one word of a phrase could reach (`REF_FRAGMENT_MAX_WORDS`), a head-word test
  for multi-word entries (`refHeadMatch`), and a ban on fragments searching
  definitions (`refDeepNeedles`). Every one was a way to limit a CONTAINS
  match, and equality leaves nothing to limit. They are in git at 20260926v
  through y with their reasoning, and the lesson worth keeping is the shape of
  the mistake: four rounds of narrowing a rule the maintainer had never asked
  for, when one question about what he expected would have replaced it. When a
  report says a result "shouldn't be there", ask what the rule IS before
  tightening the one in place.
- **A SINGLE-WORD query is a different thing and was left alone.** It filters
  through the caller's own matcher, substring and stem, across the term, the
  definition and the English gloss, and leaves the list in the order the
  learner chose. That is the browsing case, and it is what the sign-families
  fix rests on: searching *prescrizione* must find `segnale di prescrizione`,
  and searching *veicoli* still returns 124 vocabulary rows. `refFilterRank`
  returns before the equality path on those, and the harness asserts it.
- **The search must run AFTER the list's own sort, not before.** It re-orders
  by rank, so a sort applied afterwards throws the ranking away. That is
  exactly what happened in `renderVocabScreen`, where the filter had always sat
  above the A–Z sort: the phrase entries were found and then scattered back
  into alphabetical order, and the top of the list was *a breve distanza*.
  Numbers is the exception and filters WITHOUT re-ordering, because its rows
  stay grouped by category and a rank order would have to break the groups to
  show itself.
- **`setReviewSearchBox` writes the box WITHOUT dispatching `input`.** The
  input handler clears the parked query and widens the search again, which is
  the opposite of what restoring one wants, so that helper syncs the ✕ itself.
  Dispatching a synthetic event to reuse a handler is usually right here (it is
  how `wireSearchClear` works); it is wrong when the handler's side effects are
  what you are trying to avoid.
- **The per-list prose folds into `<details class="ref-about">`, closed.** It is
  read once and is then in the way of the list, which is what the page is for.
  The paragraphs are named ONE BY ONE in `ensureReviewChrome`, never swept up by
  class: `#gloss-empty` and `#exam-practice-empty` are `.review-hint` too, and
  folding an empty-state line the renderer owns would hide the message it
  writes.
- **The page opens at the TOP and with no search.** The screens are siblings in
  one scrolling document, so arriving from halfway down a study card used to
  open Reference at that height, which here is the middle of a word list.
- **One exception to "no search": a word SELECTED in a statement is carried
  into the box** (`noteStatementSelection` / `takeStatementSelection`, asked
  for 2026-09-20, silent at the maintainer's choice rather than offered as a
  line to tap). No clipboard is involved and none is needed, since reading a
  selection asks no permission. The selection must be RECORDED as it happens,
  through `selectionchange`, never read when Reference opens: tapping the nav
  collapses it before the click handler runs, so asking at that moment returns
  nothing. Four guards, all in the harness. Only a selection inside
  `.stmt-italian` or `.stmt-english-primary` counts, so a heading or a button
  label never fills the box. Anything over `SELECTION_MAX` characters (200
  since 20261002y; it was 60, and a phrase wrapping onto a second line on a
  phone was over it, reported 2026-09-25) is a dragged statement rather than
  a phrase and is ignored; line breaks inside the selection are folded to
  spaces. It EXPIRES after two minutes,
  because a stash with no expiry puts this morning's word in tonight's box.
  And it is taken ONCE, since it is the query the learner was about to type
  and not a setting they chose. On iOS the same long press opens the Look Up
  callout, which is the best vocabulary help the app has; this rides along
  with that gesture and must never obstruct it, so nothing here cancels a
  default or adds a `user-select` rule.
- **`ensureReviewChrome` BUILDS what it cannot find.** index.html is cached
  separately from app.js, and `wireSearchClear` learned twice on 2026-09-17
  what that costs, so the search field, the empty line, the result headings and
  the disclosures are all created when a stale page does not carry them, and
  adopted when it does. It runs once per session (`scr._refChrome`).
- **It was verified in jsdom, against the real index.html.** `/tmp/ref_dom.js`
  in that session loaded the page, ran app.js as a real `<script>` (a direct
  `window.eval` keeps every top-level function inside the eval's own scope,
  because app.js opens with `'use strict'`), stubbed `fetch` onto the disk and
  `scrollTo` onto an array, and asserted the 43 behaviours above; a second pass
  with `navigator.language = 'it-IT'` checked the Italian face, where the
  Vocabulary group must not appear at all. Reach for that when the browser
  cannot help: the deployed site only ever carries the LAST release.
  `/tmp/ref_run.js` covers the whole-query exception, 14 checks, and it asserts
  the long query's five rows in the same file so a future loosening cannot pass
  without facing the case that set the rule. Two traps for a harness here: the
  Glossario's label is `e.t`, not `e.term`, and `refTermKey` folds a final
  vowel, so `segnali di prescrizione` and `segnale di prescrizione` are ONE
  key. Compare keys, never the raw strings.

- **A study-list row's `en` is the GLOSS ALONE, never the tooltip (fixed
  20260929y).** `logLookup` stored `data-tooltip` whole, which is `en\ngram`,
  so every subjunctive verb the learner had tapped carried "congiuntivo
  presente" inside its English. Two symptoms, reported together on
  2026-09-23: a search for *giunti* returned 33 vocabulary rows, 29 of them
  matching on *congiuntivo* through `vocabMatches`'s English-gloss substring
  test, and every such row printed the grammar twice, once inside the gloss
  and once in `.lookups-gram`. `lookupGloss` cuts at the newline and prefers
  the dictionary's current `en` for a term that is an entry; `logLookup`
  writes through it, `collapseInflections` reads through it, and
  `migrateLookupGlosses` rewrites stored rows once, at render and after a sync
  merge, so an old device's push is cleaned on arrival. Search the FILE first
  when the list looks wrong: the four true matches were in `vocabulary.json`,
  and the other 29 came from the learner's own log.
  `scripts/check_lookup_gloss.js`, 8 checks, seeds rows the old way and fails
  7 of 8 against the previous build (`SRC=` a directory holding that app.js).

## Vocabulary retention (the plan of 2026-09-25)

- **The maintainer's finding, from his own export.** At Solo italiano he had
  missed 327 statements, and 185 of them he had answered correctly in
  English at both lower levels: the larger cause of a miss at that level is
  the vocabulary, not the rule. Two things the data said against the first
  instinct. The rare words in those misses DO NOT REPEAT (125 distinct words
  met five times or fewer in the bank, each in exactly one missed statement),
  so there is no short list of rare words to drill; and the words that DO
  recur across his misses are common ones he has seen dozens of times
  (*senso* in 12 of the 185, *obbligatorio* and *caso* in 8, *superiore*,
  *striscia*, *vieta*, *bordo* in 6). His study list held 3,252 words, 1,767
  of them met once or twice in the bank, so reviewing the whole list would
  spend the effort on words that decide one statement each. Of 719 removals,
  41 words were removed twice or more and nearly all are ultra-common
  (*veicolo*, *quando*, *sono*): accidental taps, which the return-on-third-
  tap rule already handles (only 3 removed words ever came back as misses).
- **The log could not count encounters until 20261001t.** Each entry stored
  only the time of its LAST tap, so "how many times must a word be met before
  it sticks" was unanswerable from it. `noteLookupEncounter` now keeps `n`
  (encounters, not taps: a tap within `LOOKUP_RETURN_GAP_MS` of the last
  counted one is the same encounter) and `h`, the stamps of the last
  `LOOKUP_HISTORY` encounters. Counted on EVERY path of `logLookup`,
  including a removed and a settled word, because a settled word still being
  tapped is exactly the evidence the count exists for. The sync merge takes
  the larger `n` and unions `h`; the phrase migration ADDS the two counts,
  since two words became one. `collapseInflections` sums `n` over spellings
  for the list row.
- **A wrong answer at Solo italiano names the statement's words worth
  knowing** (`lookedUpWordsIn`, under the English translation,
  `.stmt-lookedup`, heading "Words in this question:"): the words of that
  statement that sit in the study list, AND since 20261001x the words the
  bank uses at most `RARE_WORD_MAX` (5) times whether looked up or not
  (maintainer, 2026-09-25: the rare word never tapped is the one that cost
  the answer, and naming it there saves the look-up). Each with its gloss,
  one per line. It runs the statement through `highlightVocabInEscaped` and
  reads the lemmas back, so an inflected form finds its entry exactly as a
  tap would. Since 20261001y the same list also follows "Why?" on a RIGHT
  answer (`whyWords`, folded and unfolded with the English, the maintainer's
  question the same day), so it appears only when asked for; nothing for a
  removed word, nothing for an Italian browser, and never before the answer.
  `lookedUpWordsEl` is the one builder both paths use. The vocabulary review
  draws from the same function, so a rare word never looked up is reviewed
  too (393 records on the maintainer's file, from 300); its queue excludes
  only a REMOVED word, not a word absent from the log.
- **REMOVED in 20261006n at the maintainer's word (2026-10-01): the spaced
  vocabulary review below no longer exists.** Its code, store
  (`patente-vocab-review`, deleted at load), sync field and test are gone; a
  bundle's `vocabReview` is ignored. "Words in this question"
  (`lookedUpWordsIn`) stays. The record of what it was follows.
- **The spaced vocabulary review (20261001u)** sat on the Final Stretch
  page under "Right in English, missed in Italian" (`vocabReviewHtml`,
  `#vocab-review`, store `patente-vocab-review`, synced as `vocabReview`, one
  record per word, last write by `t` wins). `vocabReviewRefresh` builds the
  records from the language-miss statements (`missStatsFor(3).langRows`,
  each row now carrying its `num`) through `lookedUpWordsIn`, so a word is
  in the review only if it is in the study list AND in a statement missed
  that way; a word the learner removes from the list stays recorded but is
  never asked. The queue (`vocabReviewQueue`) is what is due, not done and
  still in the list, ordered RAREST IN THE BANK FIRST (20261001v: the first
  build put the words in several misses first and handed the maintainer
  *segnale di indicazione*, which he knows; his words: the focus is the
  low-frequency words in the questions he missed), then by how many misses
  the word sits in (`k`), capped at `VR_PER_DAY` (20). The card prints the
  bank count ("in 3 questions"). A word is shown ALONE first,
  then Show reveals the gloss, the missed statement with the word marked
  (`.vr-hit`, through the entry's own `_re`) and its English; never the
  VERO/FALSO. "I knew it" advances the stage and sets `due` to
  `VR_DAYS[stage]` days (1, 3, 7, 21, 21); the fifth in a row stamps `done`.
  "I didn't" resets to stage 0 and `due` ten minutes on, so it returns in
  the same sitting. Two costs worth knowing: the refresh runs the
  highlighter over every missed statement, so it is keyed on the row
  signature and runs once per set (`_vrSig`), and a tap in the review
  redraws ONLY the panel (`vocabReviewClick`), since the whole breakdown is
  the expensive render on the page (300 records, 20 due on the maintainer's
  file). NOT a review of the whole study list, and nothing
  shown before an answer at Solo italiano changed.
- `scripts/check_lookup_count.js`, 14 checks in each face;
  `scripts/check_vocab_review.js`, 21 checks (the Italian face asserts the
  panel is absent).

## The Grammar tab (Reference page, 20261002a)

- **Asked for by the maintainer on 2026-09-25**: he gets stuck on grammar
  even when he knows the words, and the recurring case in the bank is the
  verb in front of a past participle. One topic so far, `aux` in
  `public_html/grammar.json`, "The verb in front of a past participle": the
  concept in English first, then eight sections, essere (state or passive),
  deve/può essere, venire, andare, avere, essere as a past tense, essere
  stato, rimanere/restare. The counts that chose the order: essere +
  participle 1,561 hits in the live bank (è consentito 196, è vietata 81, è
  vietato 69), a modal + essere + participle 382, avere 133, venire 80
  (`viene immediatamente ritirata` 12), andare 42, rimanere/restare 17.
  More topics are to be decided later, one at a time.
  **Two more in 20261002b** (maintainer: "add the first, pick the more
  frequent next"): `si`, the impersonal and passive si (about 1,000
  occurrences in 634 statements: si + verb as "you/one", si + noun as a
  passive with the verb agreeing, `ci si` before a reflexive, the plural
  participle after si in `si è usciti` and `si rimane bloccati`, and `non si
  può`); and `duty`, the strength words that open about a thousand
  statements, in four bands: duty (è obbligatorio 133, bisogna 291, occorre
  128, è necessario 105, si deve 107), advice (è opportuno 86, è
  consigliabile 18, conviene 14), permission (è consentito 296, si può 122),
  ban (è vietato 195, non è consentito 50). No VERO/FALSO skew is claimed for
  any of them, because there is none worth stating (obbligatorio 40% VERO,
  opportuno 66%, the rest near half). Still to add, by weight: the
  subjunctive after purché/qualora/nel caso in cui (about 150 statements,
  247 forms), the gerund as a condition (409), pronouns attached to the verb
  (about 570, mostly fermarsi/arrestarsi/immettersi), fare + infinitive (54),
  cui/il quale (148). The bank has no imperfetto, 28 conditionals and 15
  futures, so those need no topic.
- **The shape was REWRITTEN in 20261002d after the maintainer read the first
  version and called it not very pedagogical.** He was right, and the faults
  were the ones the `italiano` repo's CLAUDE.md lists as hard-won: the prose
  crammed four or five inline Italian phrases with glosses into one
  paragraph, three examples were stacked at the END of each section instead
  of one right after each point, nothing pointed at the form in the example
  just shown, counts ("nearly four hundred statements") spoke in the
  analyst's voice, and there was no recap. Now each topic is: an English
  `intro` that explains the concept on DISPLAYED sentence PAIRS, Italian
  then English on one line (`.gr-enx`, `.gr-exit`; the maintainer asked on
  2026-09-25 for the Italian beside each English line so the points build on
  them, which is the one place a grammar intro carries Italian); one point per section with ONE or TWO
  examples immediately after it and an `after` sentence that names the form
  in that example ("*Il segnale* is masculine singular, so *installato*");
  and a `recap` table LAST (`review.grammarRecap`, "In one table"), never
  first, since at the top the terms have no referent. A "Hide the English"
  toggle (`GRAMMAR_EN_KEY`, remembered on the device) turns the examples
  into a self-test: the reader decides what the marked construction says and
  taps the row to check. Keep new topics to this shape; the harness asserts
  the intro lines, one-or-two examples per point, the `after` on every
  point, and the recap last.
- **The `aux` topic was CUT to B1 material in 20261002e** at the maintainer's
  word: the passato prossimo with avere and with essere, the plain passive
  and its past with *stato*, and the participle's agreement are A2, and a
  reader at this level has them. What is left is the three verbs that take
  essere's place in front of the same participle, venire, andare and
  rimanere, with essere named once in the intro as the baseline. **Rimanere
  was cut too in 20261002n** (maintainer, 2026-09-25): *rimane chiuso* is
  *stays closed* word for word, so it confuses nobody, while *viene chiuso*
  and *va chiuso* do not translate literally and are the whole point. The
  topic holds only those two now, ANDARE FIRST (20261002o, maintainer: it
  is the clear-cut one), and venire is explained by what it removes: *è
  chiuso* can be a state or an act, *viene chiuso* is only the act, done to
  the subject by somebody else. A second andare point (20261002p, at the
  maintainer's question) sets it against dovere: *va rispettato* and *deve
  essere rispettato* are the same duty with nobody named, and *dovere* +
  infinitive is the form that names the person who must act. **The duty
  topic is ONE WORD PER POINT since 20261002q** (maintainer, 2026-09-25):
  thirteen points, each showing the ways its word is used in the bank
  (obbligatorio, consentito and vietato fixed before an infinitive and
  agreeing before a noun; bisogna and occorre with no subject ever; ci si
  deve; è opportuno che + subjunctive; si possono with a plural thing; non
  before the infinitive after consigliabile). **In 20261002r the four
  strength bands became FOUR TOPICS of their own**, `duty`, `advice`,
  `permission`, `ban`, each with its own disclosure, intro pairs and recap
  (maintainer: "the four types have their own disclosures"). Six topics
  in the file now. **Andare moved into `duty` in 20261002s** (maintainer:
  it is a duty word), as its first two points. **And it is ALSO in `aux`
  (20261002t)**, at the maintainer's word: the participle topic shows it as
  the FIRST auxiliary, ahead of venire (20261002u, the clear-cut one goes
  first), the duty topic shows it as a duty word
  beside dovere; the same construction, two behaviours, taught in both
  places on purpose. **A seventh topic, `who`, in 20261002v** (maintainer,
  2026-09-25: he reads a statement backwards, the one passing for the one
  being passed), second in the list: the one acting is *che* + an active
  verb (che sorpassa, che intende sorpassare), the one acted on is the bare
  participle, *da* + infinitive or *che viene* + participle (sorpassato, da
  sorpassare), *si viene sorpassati* and *essere tamponati* put YOU on the
  receiving end with *da/dal* naming the actor, *che (lo) precede* is ahead
  and *che (lo) segue* behind with *lo* being the reader's own vehicle,
  *dare la precedenza a* against *avere la precedenza su*, and *da parte
  di* for the actor when the action is a noun. Counts behind it: *che
  precede* 32, *da sorpassare* 20, *che intende sorpassare* 16, *dare la
  precedenza* 167, *avere la precedenza* 31. Pitch every
  grammar topic at what a B1 reader does NOT have; do not re-teach the
  tenses.
- **An eighth topic, `parse`, FIRST in the list (20261003v)**, now "Taking
  a statement apart" (first titled "Finding the main verb when there are no
  commas") (maintainer, 2026-09-27: statements are
  hard to parse because the Ministry omits the commas that would mark a
  clause). A scan of the live bank chose its ten points: an opening phrase
  with no comma after it (about 940 statements; 838 statements have no comma
  where the English translation needed one), a quando/se condition, an
  opening gerund, the subject after the verb (è vietato il…, possono
  circolare i…), a subject carrying a che clause, the two kinds of che,
  descriptions after a noun (provenienti da, adibiti al), chains of di, an
  infinitive as subject, and the words that point back (ciò, esso, vi, ne).
  The counts came from regular expressions, not a parser (the sandbox could
  not install one), so treat them as estimates. It is first because it is
  the reading skill the other topics assume; its intro bolds the main verb in
  each pair.
  **Its intro opens on the comma difference (20261003w)**, at the
  maintainer's request and only after he asked that the claim be checked.
  The general claim "Italian uses fewer commas than English" was NOT
  supported by any source found. The narrower one is: after an opening
  if/when clause both languages expect a comma (Purdue OWL; Treccani,
  Ferrari 2019), so the bank's 75 comma-free se/quando statements are the
  Ministry's habit; after a long opening phrase or an opening participial
  phrase English style guides call for a comma (Purdue) while Italian
  leaves it to the writer (Crusca: recommended, not required; Treccani: the
  Italian comma is communicative, not syntactic). About 71% of the
  statements opening with such a phrase have no comma before the main
  verb, so the intro says "most", not "almost always". No source says this
  is a COMMON stumbling block for Americans, so the intro does not claim it.
  **The intro then takes ONE statement apart (20261003z)**, at the
  maintainer's request after he judged a breakdown under every example too
  much for the section: 23853 (VERO, no figure, no comma), chosen by scoring
  the comma-free VERO statements for stacked patterns. Four labelled rows,
  setting / main verb / subject / which cars, each Italian over its English
  (`.gr-parse`, `.gr-parse-row`, `.gr-parse-main`), then one paragraph naming
  the three things that hide the structure (no comma after the setting, the
  subject after the verb with only the agreement of *vietata* to find it, and
  *per costruzione* between *sviluppare* and its object). The Italian in the
  intro is typed, not quoted by number, so if 23853's text ever changes the
  intro must be checked by hand; the build script asserted the four parts
  join to the bank's text.
  **"The subject after the verb" is the SECOND point since 20261004a**
  (maintainer, 2026-09-27: he reads statements far better when the subject
  comes first, and English almost never puts it after). Its text now says
  why an English reader misses it (English inverts only in fixed forms, so
  the first noun is taken as the subject) and gives three checks: nouns
  inside an opening setting or condition are not the subject of the main
  verb; an article and noun after the main verb is probably the subject;
  agreement (a plural verb, a feminine *vietata*) picks the noun that fits.
  The recap row moved with it.
  **A third point, "No subject written", since 20261004b** (maintainer,
  same day: Italian drops subject pronouns, which compounds the problem).
  In the bank the missing subject is nearly always the driver: *-iamo* verbs
  (about 58 statements: dobbiamo, abbiamo la precedenza, possiamo) and *ci*
  as *us*; *bisogna*, *occorre* and *è vietato* + infinitive (about 390 with
  bisogna/occorre alone) with no subject at all; and a second verb after *e*
  or *ma* keeping the first one's subject. Examples 20689 and 18719, both
  VERO. The duty and si topics teach bisogna, occorre and si in depth; this
  point only says where the subject went.
  **Renamed "Taking a statement apart" in 20261004c, and the intro
  reordered** (maintainer, 2026-09-27: commas are what got us here, but
  they are one symptom of a bigger challenge). The intro now opens on that
  challenge: an English reader finds a sentence's parts by position
  (subject, verb, commas around the rest) and the statements keep none of
  those habits; three differences cause most of the trouble (subject after
  the verb or unwritten, phrases piled before the main verb with nothing to
  mark their end, descriptions after the noun). Then the 23853 breakdown,
  then the comma paragraph as the difference noticed first, then the
  find-the-main-verb method and its three pairs. The `id` is still
  `parse`.
  **The worked example is now TWO statements (20261004d)**, replacing
  23853 (maintainer, 2026-09-27: 23853 was long for an unusual reason, the
  rare *per costruzione* placement, and hid the commonest trap). First
  24843 (14 words: setting, verb, subject after it, che clause; the point is
  that the first noun, after *nei*, cannot be the subject), then 24007 (32
  words, chosen from the longest VERO statements without a figure because
  it stacks six of the topic's points: main verb as the fifteenth word, two
  descriptions after nouns, a di chain, the adjective before its noun in
  *rende pericolosa la fermata*, *tali* pointing back, and the subject
  after the verb in the *qualora* clause). The maintainer wanted the harder
  one in so the learner sees why the section matters. Both are typed in the
  intro; the build asserted each breakdown joins to the bank's text.
- **`parse` gained a fourth point, "A pronoun on the end of the verb"
  (20261004n, flag 25259)**: the reviewer read *evitare di mettersi sotto il
  veicolo* as a rule about the jack. Examples 25259 (*mettersi*) and 24921
  (*bloccarglieli* = bloccare + gli + li). The explanation of 25259 now says
  the same in both halves.
- **`parse` gained a fifth point, "Two negative words, one negation: non
  ... mai, non ... né" (20261004p, flag 25301)**: in Italian *non* plus a
  second negative word is ONE negation, where English reads two negatives as
  cancelling. Examples 31024 and 18765; 25301's explanation says the same.
- **A ninth topic, `link`, second in the list (20261004l)**, "Linking words:
  qualora, purché, allorché, in attesa che, in quanto" (flag 23825,
  2026-09-28: the reviewer missed *in attesa che*). Eleven points, one word
  or small group each: qualora, purché, nel caso in cui, salvo che (a *non*
  after it is not a negation, 22978), ove (formal *where*, not a misspelling
  of *dove*), allorché, in attesa che, prima che / finché, in modo da / in
  modo che / affinché, in quanto / poiché (*in quanto* is not *in how
  much*), anche se. The intro names the two difficulties (formal words a B1
  reader has not met, and the subjunctive after most of them, read as the
  signal that the clause is a condition, not a fact). Counts in the live
  bank: perché 63, purché 61, anche se 54, in modo da 48, qualora 32, nel
  caso in cui 21, in quanto 19, mentre 17, ove 14, allorché 12.
- **A tenth topic, `eggiare`, last in the list (20261026f, maintainer,
  2026-10-27)**, "Words built on -eggiare: lampeggiante, tratteggiata": a
  noun or adjective plus *-eggiare* makes a verb, and the bank meets it as
  the *-eggiante* adjective (lampeggiante 63, pianeggiante 2), the
  *-eggiato* participle (tratteggiata, fiancheggiati) and the infinitive
  (gareggiare, danneggiare, fronteggiare). The maintainer's source text
  also named *ondeggiante*, *serpeggiante*, *verdeggiante*, *galleggiante*
  and *tondeggiante*; none is in the bank, so none is taught. The intro
  says *carreggiata* and *parcheggio* are best learned as words of their
  own, rather than claim an etymology for them. The endings in the intro,
  prose and recap use a non-breaking hyphen (U+2011), since a plain one
  broke the ending onto its own line on a phone; the headings keep the
  plain hyphen, which the search reads.
- **Every example is a statement QUOTED BY NUMBER**, never written out. The
  app prints the bank's own `italian_text` and `english_translation` and
  marks the run of words named in `hl`; `validate_data.py` FAILS on a number
  that is not a live statement, on a FALSO statement (an example that states
  a false rule teaches the false rule; all 24 are VERO), and on an `hl` that
  does not occur in the statement. The prose is ours: the `italiano` repo's
  topic "Choosing the verb before a past participle" was the model for the
  shape (English concept first, one construction per block, an example right
  after each), and its examples were NOT copied, since the maintainer asked
  that the examples be restricted to the bank.
- **English-only, like Vocabulary**, hidden for an Italian browser in
  `reviewSectionsAvailable`; sits right after Vocabulary. **SEARCHED since
  20261002x** (maintainer's decision, 2026-09-25), on the same reasoning as
  the single search field: a learner who meets *si viene sorpassati* in a
  statement knows the phrase and not which tab explains it, and the
  selected-word carry-over put such a phrase in the box with nothing to
  answer it. It was parked like Ambiguous until then. **The search reads the
  PHRASES a point names, never its prose** (`grammarSearchRows`): the tail
  of each section heading after the colon, split on commas, the `hl` of
  each example (the bank's own form, *viene sorpassato*, *va diminuita*),
  and the recap's left column, which lands on the recap. Those are entries
  in all but name, so the exact-phrase rule holds; matching the paragraphs
  would return a topic for *veicolo* or *strada*, the blow-up that rule was
  written to stop. A single word matches at the start of any word of a
  phrase or by its stem (`grammarPhraseHit`). A hit renders only the points
  that matched, under their topic's title, open, with no intro and no tools
  row (`renderGrammar` on a non-empty `refQuery`), and returns the count
  for the tab. Tapping the tab during a search narrows to it like the
  other lists; Ambiguous is the one parked tab now. The harness asserts
  *sorpassati* reaches the `who` topic, *viene sorpassato* reaches its marked
  example, and *chiuso* (intro and prose only) reaches nothing. `ensureGrammarPane` builds the tab and
  the pane on a stale cached index.html and is called from both
  `bindVocabScreen` (so the tab gets the click listener bound there) and
  `ensureReviewChrome`. Topics render as `<details class="gr-topic">`, a
  single topic open, several closed (`_grammarOpen`, not persisted).
  **Expand all / Collapse all (20261002w)**, at the maintainer's request:
  two buttons left of "Hide the English" (`data-gr-fold`), which set `open`
  on every `details.gr-topic`; that fires `toggle`, so the session set
  follows without a second write. In the same release an OPEN topic became
  visibly a box: its summary is a tinted bar with an accent rule under it
  (`.gr-topic[open] > summary`), the frame takes the accent border, the gap
  below it grows, and every section carries a top rule. He reported that
  with all topics open he could not see where one ended and the next began.
- **No grammar lesson at the end of a question.** The maintainer said so the
  same day about a vocabulary gloss that carried a literal translation of the
  andare passive: the gloss says "must not be performed" and its `gram` line
  names the construction in six words (`andare + participio passato = must
  be, a duty`, on all six such entries). The teaching lives here.
- `scripts/check_grammar_tab.js`, 35 checks in the English face, 2 in the
  Italian, and `STALE=1` strips the tab and pane from index.html first to
  prove the builder. The utterance stub must extend `EventTarget`, since
  `ttsSpeak` adds listeners to it.

## Memory aids for false friends and unfamiliar words (`aids`, 20261003s)

- **Asked for by the maintainer on 2026-09-27**, after flag 24278
  (*tergicristalli*) and a bug report on *sbocco*: to a B1 American, a word in
  the bank is (1) familiar, because it looks or sounds like its English
  meaning, (2) a FALSE FRIEND (*pretendere*, *eventuale*, *occorre*), or (3)
  UNFAMILIAR. Cases 2 and 3 need help making the word stick; case 1 does not.
- **`vocabulary.json` → `aids`**, keyed by the single word as the bank writes
  it: `{k: "ff" | "rel" | "new", t: "..."}`. A false-friend aid opens "Not" and names
  the English look-alike; a `rel` aid names an English look-alike that HELPS
  and never opens "Not"; an unfamiliar word's aid gives its parts or origin,
  or a hook labelled "Sounds like" / "Picture" that makes no historical claim.
  1,192 words carry one (125 ff, 155 rel, 912 new). The app shows them through `entryAids(term)`: every
  word of an entry's term that has an aid, at most two, as the tooltip's last
  lines, under the gloss in the Vocabulary rows (`.lookups-ety`), in "Words in
  this question" and on the vocabulary review's reveal. A form with no key of
  its own falls back to a key with the same stem, but ONLY when the form is
  not a vocabulary entry itself, since every entry was classified on its own
  and no key means no aid was wanted.
- **How it was made, in `docs/word-aids/`.** All 3,211 single-word entries
  were classified by thirteen readers against `RUBRIC.md` (b1 767, cognate
  1,209, false 282, new 953) and the drafts reviewed once against
  `VERIFY.md`. **That was not enough, and the maintainer said so on
  2026-09-27: "we should definitely check against a dictionary ... saying
  explanations were drafted with AI help does not exempt us from accuracy."**
  So every aid text (839) was then checked against DICTIONARIES FETCHED IN
  THE TASK, never memory, under `DICTCHECK.md`: English Wiktionary through
  kaikki.org's per-word HTML pages, Treccani's vocabolario for Italian
  etymology, Etymonline for English. Result: 407 verified, 431 revised, 1
  dropped. Half needed revising, which is the measure of what an unchecked
  model etymology is worth: wrong sources (*gasolio* is from English
  "gasoil", *tornante* from French *tournant*, *marciapiede* from French
  *marchepied*), invented English cognates (*sangue* is not the root of
  "sanguine"; both come from *sanguis*), and above all false-friend aids that
  DENIED a sense the Italian word really has (*circolazione*, *assumere*,
  *consentire*, *rilasciare*, *realizzare*, *sollecitare*).
- **"Not X" is kept ONLY where reading X gives a wrong sentence**
  (20261003u, maintainer, 2026-09-27, on *marcia*: "Not march" was wrong,
  since the two share an origin and a march is a forward movement). The model
  is *pretendere*: it shares its Latin source with "pretend", yet reading one
  for the other gives a wrong meaning, so a shared ORIGIN alone never makes a
  false friend. All 206 "Not" aids were re-judged against fetched dictionaries
  (`FFCHECK` note under each word in `sources.json`): 71 became `rel` bridges
  ("Related to the English ..."), one was dropped, and the 46 texts that had
  said "Not only X" were recast as `rel` too ("Besides X, ..."), because a
  word that also means X is not a false friend of X. `validate_data.py` fails
  on a "Not only", on an `ff` aid not opening "Not", and on a `rel` aid that
  does. The URLs behind every shipped aid are in `sources.json`, keyed by
  word, with the verdict and what changed. **An aid with no dictionary source
  is not shipped**; a new aid goes through the same check before it enters
  `aids`. Practical notes for the next run: kaikki's `.jsonl` files arrive
  as binary through the fetch tool and en.wiktionary.org returns empty pages,
  so use kaikki's `.html`; the sites rate-limit (HTTP 429), so fetch one page
  at a time and wait rather than stop; the sandbox's own network cannot reach
  kaikki.org, so the bulk dump is not an option from here.
- **Every false-friend aid carries an etymology (20261004k)**, at the
  maintainer's request of 2026-09-28 (flag 23958): the "Not X" warning, then
  one sentence on where the word comes from and why the English look-alike
  drifted, all checked against dictionary pages fetched in the task and
  recorded as `etymcheck` in `sources.json`. 99 texts, 123 keys;
  *difficilmente* moved to `rel`. The same batch revised *incombente* (ff to
  rel), *gomito*, *articolazioni*, *denunzia* and added *stagna*, *fornire*,
  *impennata*, *inquinare*. An aid must state the LINK (a cubit is measured
  from the elbow), not merely name a cognate.
- **The cognates were re-judged (20261005d, maintainer, 2026-09-29, flag
  31041 on *ininfluente*).** The first pass gave no aid to the 1,209 words
  classed `cognate`. Twelve readers re-judged all 1,046 cognate lemmas
  against a strict test (does an American with B1 Italian get the meaning
  from the LOOK alone?) under `outputs/cg/TASK.md`: 918 kept, 127 given a
  `rel` aid naming the English relative and the link (a hidden prefix, a
  shifted spelling such as es- for ex-, sost- for subst-, or a rare English
  relative), one moved to `ff` (*motoveicoli*). 150 word forms gained an
  aid, each checked against pages fetched in the task and recorded in
  `sources.json`; `classification.json` marks them `cognate-rel`. Totals
  now 916 new, 311 rel, 124 ff.
- **Flags 24124, 24724, 24919 (20261006i).** *sbandamenti* and *sbandi*
  moved to `ff` ("Not abandonment"): Treccani derives *sbandare* from
  *banda* (side), Etymonline "abandon" from Old French *à bandon*, a
  Germanic root. *ruotino*'s aid now names its second sense, the trailer's
  nose wheel, so it does not read as "spare wheel" inside *ruotino
  pivottante di manovra*, which also got a Glossario entry. Topic 17 gained
  "## First aid: which position for which injury" in both halves, BEFORE
  the common situations, naming the Italian words for standing (*in piedi*,
  *alzato*), sitting, half-sitting and lying down, and which injury takes
  which. It carries no claims.
- **An aid is language, never a driving rule.** `validate_data.py` checks each
  one ends with a period, carries no digit, em dash or exclamation mark, and
  that exactly the false friends open "Not". It replaced the per-entry `ety` field of
  20261003r, whose eight texts were superseded by the word-level aids.

## The Questions tab: the bank searched, and a way back to cleared cards (20261004y)

- **Asked for by the maintainer on 2026-09-29** in two bug reports on the same
  day: can the whole bank be searched for a word, and why can a card he had
  cleared no longer be reached (he wanted to flag a statement on it). The
  study queue drops cleared cards by design (`buildQueue`), so the answer was
  one feature for both: a fifth list in the Reference search, `bank`, placed
  before Ambiguous, offered to every browser.
- **What it shows.** Every live statement whose Italian (or, for a
  non-Italian browser, English) contains the query, marked where it stands,
  with its number and topic and NO answer. At most `BANK_MAX` (50) rows, with
  a line saying how many there are; *veicolo* alone is in about 1,900.
- **How it matches.** Word start, on text folded for case, accents and the
  typographic apostrophe (`bankFold`, character by character so the mark
  lands at the same index in the original); a phrase must appear as typed;
  a word of five letters or more ending in a vowel matches with any final
  vowel (*veicolo* finds *veicoli*). This is deliberately NOT the vocabulary
  lists' exact-entry rule: a statement is prose, and the question is whether
  it contains the words.
- **No English at Solo italiano (20261005a, maintainer, 2026-09-29).** The
  search lists the very questions the learner is working on, so below Solo
  italiano the translation shows and is searched, and at it neither happens
  (`bankShowsEnglish`). An Italian browser never gets English at any level.
- **Open card** (`openCardFromSearch`) starts a session of ONE card,
  `buildMode: 'card'`, cleared or not, peeks the full card when the statement
  sits outside the abridged set, and aims `cardWorkTarget` at the statement
  found (`_focusStmt`). Finishing it returns to the Reference page with the
  query restored (`returnToBankSearch`), which `finishStudyPass` checks first.
- **A question number finds that question, and any row can go into the
  weak spots (20261011r, maintainer, 2026-10-04: to add questions missed
  in another app's mock).** `bankHits` returns the one statement for a
  query of 4 to 6 digits, with or without `#`; each row carries "+ Add to
  weak spots" (`toggleWeakPin`, the mock review's own pin, labels through
  `weakPinLabelV` in the reader's language), and a second tap takes it
  back. In the review stage a pinned question is part of the day's review.
- `scripts/check_bank_search.js`, 20 checks in each face, and `STALE=1`
  strips the tab and pane from index.html to prove `ensureBankPane`.

## "Same in English" (fourth Vocabulary tab, 20261001e)

- **One American English word, several Italian ones**, asked for by the
  maintainer on 2026-09-24 as a study tool. `public_html/vocab_sets.json`
  holds 147 hand-curated sets, each an English word and the vocabulary
  entries that share it; the tab renders them as folding groups of ordinary
  vocabulary rows, so 🔊 and +/- behave as on the other tabs.
- **Eleven sets carry a `note`**: the Italian words are NOT interchangeable
  (fermata / sosta / arresto; strada / carreggiata; banchina / corsia di
  emergenza; autoveicolo / autovettura / autocarro; è obbligatorio against è
  opportuno; reato against infrazione, and so on). They come first, under
  their own heading, with the note above the rows; `topic` names the review
  that teaches the difference. The other sets are true synonyms.
- **Curated, not generated.** Grouping the glosses mechanically gives 935
  groups, most of them verb forms of one word or filler (is, are, make). The
  maintainer chose a curated list of about 100 to 150. To extend it, add a
  set by hand; `validate_data.py` fails on a term that is not an exact
  vocabulary entry, a set of fewer than two, or a duplicate English word, so
  a vocabulary cleanup that removes an entry breaks the build rather than
  thinning a set in silence.
- The tab is English-only chrome like the rest of Vocabulary, which an
  Italian browser never sees. `ensureSameTab` builds the button on a stale
  cached index.html. The type filter and the sort are hidden on this tab.

## The Glossario (Reference page, and the planned L3 underline)

- **It is not the vocabulary list and must not drift into one.**
  `vocabulary.json` translates a term for an English speaker and, by glossary
  rule 14, never teaches; `glossary.json` says what a word means IN THE BANK'S
  REGISTER, in Italian, for a reader who already speaks the language. The
  Vocabulary tab is hidden outright for an Italian browser, which is why the
  Glossario becomes their leftmost tab and the one the page opens on.
- **The CHROME follows the browser, the ENTRIES are always Italian.** An
  Italian browser sees no English anywhere; any other browser sees English
  interface around Italian definitions. The trap is the direction: the default
  text in `index.html` IS the English face, because `paintVocabChrome` captures
  `el.textContent` as `el._en` and substitutes `STATIC_IT` for an Italian
  browser. Writing the Italian into the markup, which is what happened on
  2026-09-17, therefore shows Italian to English readers and nothing changes
  for Italian ones. Seven strings shipped that way. Put ENGLISH in the markup
  and the Italian in `STATIC_IT`, and give every key a `T` entry with both
  faces for the strings the render sets itself.
- **A paragraph with markup needs `data-i18n-html`, not `data-i18n`.**
  `paintVocabChrome` sets `textContent` for `data-i18n`, and captures `_en`
  from `textContent` too, so a paragraph carrying `<strong>` is FLATTENED on
  the first paint and the emphasis never comes back, in either language. The
  Vocabulary intro shipped that way; `paintSettingsLang` had the HTML branch
  all along and `paintVocabChrome` did not, which is why it showed up on one
  screen only. Both painters have it now.
- **An element whose message depends on state carries no `data-i18n`.** The
  empty line says a different thing for a search, for an empty study list and
  for a full one, so `renderGlossary` owns it with `vt()`; a `data-i18n` would
  fight the render for the same element and whichever ran last would win.
- **The rows ARE the Vocabulary list's rows** (`.lookups-list` and its
  classes), deliberately, so a change to that list's look reaches both tabs.
  There is no parallel `gloss-*` styling left; the article reference rides in
  `.lookups-gram`. Open groups have their OWN set, since the two lists hold
  different entries.
- **`f` is stamped, never hand-written.** `scripts/glossary_freq.py` imports
  `entry_regex` from `consolidate_vocab.py` rather than reimplementing the
  matcher, counts over the LIVE statements only, and `validate_data.py`
  recomputes and fails on a stale count. A retirement lowers a count with no
  other symptom, so nothing else would catch it.
- **No figures in a definition.** A quantity belongs in `reference.json`, where
  it is traceable to the statements that test it; `validate_data.py` rejects a
  digit in an entry.
- **Source from the CODE where the Code defines the term** (`src`), and write
  our own line otherwise. Two entries exist because the obvious source was
  wrong or thin: *cilindrata* is a volume and not the engine's power, and
  *caravan* needs the fact that it is towed while the *autocaravan* drives
  itself.
- **Every entry carries an `en`, revealed by an EN pill, for a browser that is
  not Italian.** The entry itself stays Italian for everyone: the pill is the
  review overlay's own (`rb-it` / `rb-itxt`, driven by `toggleItBlock`), so the
  translation is one tap away rather than in the way, and an Italian browser
  never sees it because there is nothing to reveal. `validate_data.py` fails on
  an entry with no `en`, since a pill that appears on some rows and not others,
  for no reason the reader can see, is worse than none.
- **`src` is PROVENANCE and is never shown.** It shipped for one release as a
  second line under the definition, in the list and in the tooltip, and the
  maintainer cut it on 2026-09-17: the learner needs to know what the word
  means, not which comma of art. 3 says so. It stays in the file, because it is
  how an entry gets checked against the law and how the next editor knows which
  wording is not ours to improve. `glossaryMap` therefore does NOT copy it into
  `gram`, which is the field the highlighter prints.
- **The SIGN FAMILIES are ours, not SIDA's, and they were missing until
  2026-09-20.** The maintainer asked whether the Glossario defined *segnale di
  indicazione* and the rest; it defined none of them, and it had no entry for
  *delineatore* either, which the live bank uses 78 times. That gap simply
  followed SIDA, whose list is hard words in the questions and treats the
  families as chapter-one material. Eighteen entries were added, all sourced to
  the Code where it defines them: art. 38 c. 1 for *segnaletica stradale* and
  *segnale stradale*, art. 39 c. 1 for the vertical families (*pericolo*,
  *prescrizione* and its three kinds, *indicazione*, *preavviso*, *direzione*),
  art. 40 for the horizontal ones, art. 41 for *luminoso*, art. 42 for
  *complementare*, art. 38 c. 3 for *temporaneo*; *fine prescrizione* and
  *delineatore* are our own lines, the Code not defining either. The umbrella
  is the one that earns its place twice over: *segnale di prescrizione* covers
  precedence, prohibition and obligation but NOT indication, and 26 statements
  turn on that.
- **A glossary TERM matches at the start of any of its WORDS**, not only at
  position 0. That distinction is the whole reason the sign families were
  reported missing the day after they shipped (2026-09-20): `segnale di
  prescrizione` was in the file, on the server and in the app, and a search for
  *prescrizione* returned `segnale di divieto`, `di obbligo` and `di
  precedenza`, whose DEFINITIONS contain the word, while the entry named after
  it stayed hidden. The start-only rule was written for single words ("car"
  finds carreggiata and caravan rather than every definition mentioning a
  carriageway) and it is right for those; for a multi-word term it buries the
  entry behind its least distinguishing word, since five entries here open with
  *segnale di*. It is still a PREFIX test on each word, never a substring one,
  so the reason the original rule existed is kept. When an entry is reported
  missing, search the FILE before believing the app: `glossary_freq.py` and
  `validate_data.py` both prove the entry exists, so the fault is in reaching
  it.
- **An umbrella entry names each kind by its FULL headword, plus an example or
  two of each, and stops there.** `segnale di prescrizione` had listed its
  three sub-families elliptically from the start, as *i segnali di precedenza,
  quelli di divieto e quelli di obbligo*, and the maintainer asked three times
  before it was right (2026-09-20): first whether the kinds were listed at all,
  then whether the individual signs were, and finally "no, it should be
  explicit, i.e., segnale di divieto, segnale di obbligo". The elision reads
  as ordinary Italian, which is why it survived two passes, and it is wrong
  here for two reasons that have nothing to do with style. Each of those kinds
  is **its own Glossario headword**, so a reader who wants the next definition
  needs the name to look up; and `refNeedles` searches the DEFINITIONS too, so
  *quelli di divieto* means a search for `segnale di divieto` never reaches the
  umbrella that contains it. The same fix went to the other three umbrellas the
  same day (`segnaletica stradale`, `segnale verticale`, `segnale di
  indicazione`, the last of which now names *segnale di preavviso* and
  *segnale di direzione*). The examples are the other half of the line: STOP
  and dare precedenza, the transito, sosta and sorpasso bans, direzione
  obbligatoria and velocità minima make the umbrella concrete, while a
  catalogue of every sign in the three families would be a list rather than a
  definition, and the TOPIC REVIEWS (05, 04, 02) already teach those sign by
  sign with their pictures. A glossary entry says what a word means.
- **An entry may carry the RULE when the word's whole difficulty is the rule.**
  `clacson` and `tromba` set the line (2026-09-20). The word is easy; what the
  learner cannot hold is when the horn may be sounded, so both entries say that
  sounding it is almost always wrong and no manoeuvre requires it, then list
  the only three exceptions, ENUMERATED as (a), (b), (c): outside town to avoid
  a crash, especially before passing cyclists or pedestrians; in town only in
  real and immediate danger; carrying injured or seriously ill people, even
  under a no-horn sign. That shape came from the maintainer, who rejected a
  first version as verbose and a second for running the three together in
  prose: lead with the rarity, then enumerate, and enumerate visibly. The
  labels are LETTERS because `validate_data.py` rejects a digit in a
  definition, so a numbered list is not available here. The "no manoeuvre requires it" line is the
  fact the bank tests most, and it is safe to state: of the fifty-seven live
  statements naming the horn not one makes sounding a duty, and art. 156 only
  permits (art. 177's *dispositivo acustico supplementare di allarme* is the
  emergency siren, not this). Both entries carry the full list rather than
  cross-referring, because at Solo italiano the tooltip shows one entry's `d`
  and a reader who taps *tromba* cannot follow a pointer. Topic 14's
  `### The horn` teaches the same three; correct them together. **Since
  20260930j every live statement in which the DRIVER sounds the horn carries
  the same list at the end of its explanation**, 42 statements in both
  languages, asked for by the maintainer on 2026-09-23 after flag 22910
  ("another opportunity to remind the learner of all the cases"). The eight
  statements that name a horn without the driver sounding it are left alone:
  the level-crossing and flashing-light devices (19031, 19048, 18418, 21049),
  the belt chime (24314), the sign's identity (19627), the hours panel
  (22031) and the ban on fitting two-tone horns (22689). The list is one
  fixed sentence pair, so a change to the three cases is a search for `(c)
  when carrying` across `questions.json`, `glossary.json` and topic 14, in
  that order.
- **An empty pane is a question worth asking, not always a bug.** The exact
  rule left the Glossario blank for that query, and the maintainer asked
  whether none of those words was a headword. None was: `veicolare`,
  `autoveicolo`, `motoveicolo`, `complesso di veicoli`, `barriera laterale`
  and `sanzione accessoria` all CONTAIN one of them and none IS one. Check the
  file before answering that, and name the near misses, because the answer
  divides into two very different cases: the search cannot reach the entry
  (the sign-families bug), or the entry does not exist. This was the second.
- **`proprietà laterali` was added on that showing (2026-09-20).** It is the
  Code's own phrase for the land a *passo carrabile* serves, it is not
  transparent the way *veicolo* is, and no headword covered it: `carrabile`
  defines the adjective and would never be found by searching *proprietà*.
  Our own line, since art. 3 uses the phrase inside other definitions (the
  *strada di servizio* and *strada extraurbana principale* entries) without
  ever defining it; art. 3 c. 1 n. 37 defines only the *passo carrabile*, as
  access to a lateral area fit for parking. It fires twice in the live bank,
  which is thin, and the recorded line holds: the count is not the test.
- **`dare la precedenza` was considered and left out.** It is met 167 times and
  it is ordinary Italian, not a word whose bank register is hard, which is the
  line this file draws. The count is not the test.
- **A family definition names the shape and the color, and that settles the
  identification statements.** Accepted by the maintainer on 2026-09-20 on the
  `carreggiata` precedent: a definition reachable before the answer is fine
  because every glossary word behaves alike, and an entry must not be written
  so as to dodge the point. Worth knowing that this is a LARGER class than
  `carreggiata` was, since the bank asks which family a pictured sign belongs
  to many times over. Do not quietly rewrite these into function-only
  definitions later; that decision was taken with the cost in view.
- **The list is FINISHED against SIDA's, and the shortfall is accounted for.**
  SIDA prints **287** headwords and we ship **255** of them (274 entries in all, the other 19 being ours), every one of which fires at
  least once in the live bank (`glossary_freq.py` prints `NEVER MET` otherwise,
  and it now prints nothing). The gap is not a backlog:
  - **Fifteen are the same word under another form**, already covered by an
    entry whose matcher reaches the bank's spelling: *raso* → `a raso`,
    *sfalsati* → `a livelli sfalsati`, *carrello-appendice* → `carrello
    appendice`, *psicofisiche* → `psicofisico`, *gemellate* → `ruote
    gemellate`, *simmetrico* → `ruote simmetriche`, *squilibratì* (SIDA's own
    typo) → `squilibrato`, *sconnesso* → `sconnessione`, *ovalizzato* →
    `ovalizzazione`, *riflettenti* → `rifrangente` and `retroriflettente`,
    *antibloccaggio* → `ABS`, *ganascia* → `ganasce`, *guardrails* → `barriera
    laterale`, *accelerate* → `accelerazione`, *opportunamente integrato* →
    `pannello integrativo`.
  - **Seventeen are words our bank never uses**, in the statements or in the
    reviews: *contraente, constatazione amichevole, constatazioni di rito,
    diramazione, dinamica di un incidente, filoveicoli, ganascia (singular),
    graniglia, invalicabile, istanza, lubrificare, manto, motocarrozzette,
    quadrupedi, smistamento, strombazzare, stupefacenti, tendonati*. An entry
    for a word nobody meets is dead weight, and `validate_data.py` rejects it.
  - **The rest cannot be reached by the matcher and are left out knowingly.**
    The final-vowel wildcard covers `-o/-a/-e/-i`, so a verb the bank writes
    only as *oltrepassi / oltrepassata / occultarne* is unreachable from the
    infinitive, and `portata` is worse than unreachable: the wildcard catches
    the participle *portato/portati* four times against three real uses of the
    noun, so the entry would mostly underline the wrong word. Do not "fix"
    these by broadening a gloss; add the form the bank uses as its own entry,
    which is the rule already recorded for vocabulary.
- **`glossary_freq.py` must lowercase the statements.** `entry_regex` builds
  its pattern from the lowercased term and compiles it WITHOUT `re.I`, while
  the app compiles the same pattern with `'gi'`. consolidate_vocab.py has always
  folded case in its own counting loop and this script did not, so it reported
  `f = 0` for a word the bank only ever capitalises (*Motorizzazione*, *ABS*)
  and undercounted every term a statement happens to open with. Fixed
  2026-09-17; it moved 8 of the then 208 counts. A count that disagrees with
  what the learner sees underlined is the symptom to watch for.

**SHIPPED (maintainer's design, 2026-09-17): glossary terms are underlined at
Solo italiano, and a tap shows the definition and adds the word to the My
Study List, with the Vocabulary tab's +/- move behaviour.** `renderStudyCard`
runs `highlightVocabInEscaped(italianHtml, glossaryMap(), true)` at L3, and
`glossaryMap` maps `d`, the ITALIAN definition, into the tooltip, so the entry
a learner meets there is Italian whatever their browser. The consequence to
remember: a word missing from `glossary.json` has NO help at Solo italiano,
even when `vocabulary.json` glosses it, because the vocabulary pass does not
run at that level (that is how *casello* was reported missing on 2026-09-19
although the phrase *casello autostradale* has had a gloss all along). It was
reported three more times on 2026-09-20, for *asini*, *a meno di* and
*serbatoio*, and all three are glossed and underline at the first two levels.
Four reports in two days is a pattern, not a gap in the word list, so check
which LEVEL a missing-gloss report comes from before adding an entry: the
answer is either the OS Look Up (the recorded position), a glossary entry
(only if the word is hard in the bank's register, which none of these four
are), or a decision to run the vocabulary pass at Solo italiano too. That last
one is now arguable, because the underline-costs-Look-Up objection lost its
force the day the glossary pass put spans in that text anyway; what is left
against it is DENSITY, a median of twelve terms underlined in a 15-word
statement, which would make Solo italiano look like the level below it. The
first point below is still OUTSTANDING and the rest is kept as the reasoning
behind what shipped:

- **It must not cost the OS Look Up.** The recorded rule is that statement text
  stays plain at Solo italiano so a long press can select a word and the
  platform dictionary can answer, which is the best vocabulary help the app
  has. Underlining puts spans in that text. The spans themselves look safe:
  `.vocab-term` carries no `user-select: none` (the only three in style.css sit
  on a disclosure summary, a caption and the sync code) and the tap handler
  does not cancel the default, so selection should survive. SHOULD, not does:
  verify a long press on an underlined word on a real iPhone before shipping,
  because losing Look Up would be invisible in every automated check and would
  take away more than the feature adds.
- **Underline density is NOT a problem, and the numbers say so.** The worry
  that three hundred entries would clutter a statement was raised on
  2026-09-17 and measured the same day: a finished glossary of 290 entries
  underlines a MEDIAN OF ZERO terms per statement, mean 0.8, 90th percentile 2,
  at most 6, and leaves 52% of statements with nothing marked. The yardstick is
  the vocabulary highlighting that already ships at L1/L2, which underlines a
  median of TWELVE terms in a 15-word statement. The two do not scale alike:
  glossary terms are technical and concentrated, while the 6,162 vocabulary
  entries cover ordinary words and hit almost everything. So there is no need
  to choose which entries underline, and at that sparseness the underline is a
  signal rather than decoration. Measure a density worry against the shipped
  list before arguing from the entry count.
- **A TAP SHOWS THE DEFINITION AND ADDS THE WORD**, decided by the maintainer
  on 2026-09-17, which is exactly what the vocabulary highlighting does at
  L1/L2. The alternative considered and rejected was a silent add, with the
  entry readable only later on the Reference page.
- **So a definition IS reachable before the answer at Solo italiano, and that
  was accepted knowingly.** Some entries carry the fact that settles the
  statement: ours for *carreggiata* ends by listing what is not part of it,
  which answers anything asking whether the banchina is. This is not the
  forbidden kind of leak, which is a signal only FALSO statements can trigger,
  because every glossary word behaves the same way; and the Reference page
  already hands over figures mid-study by design. Do not "fix" it later by
  hiding definitions at L3, and do not write an entry so as to dodge the point
  either: an entry that omits the deciding fact to avoid helping is a worse
  entry. The learner still has to know the rule at the exam, where none of this
  is on screen.

## The progress record, and the `miss` counter

- A statement's record is `{seen, correct, streak, given, gAt, sAt, miss}` per
  level, plus two flags that exist only where they apply: `lft` (credit-only,
  never answered here) and `und` (an answer erased by "Answer again"). **`miss` was added 2026-09-19 and is the only trustworthy count of
  wrong answers.** `seen - correct` looks equivalent and is not: `liftCredit`
  raises `correct` when a HIGHER level masters the statement and `seen` follows
  it up, so a lower level's miss is silently erased. On a real export that had
  already happened to sixteen statements reading clean at L1/L2, against a 3%
  background rate, which biased "did I know this when the English was there?"
  in the flattering direction.
- **Read it through `missCount(rec)`, never as `seen - correct`.** The helper
  falls back to the old arithmetic for a record written before the field
  existed, so both kinds of record answer correctly.
- **Four places touch it**, and the last is the one with no symptom: the study
  answer path, `recordExamMisses`, `mergeCardRecord` (max, like `seen` and
  `correct`), and `liftStatement`, which freezes the pre-lift value before
  overwriting the arithmetic it used to be read from. Miss that fourth one and
  the counter is merely a slower version of the bug.
- **Absent rather than zero on a clean record**, deliberately: there are about
  21,000 stored records and a field that says nothing on most of them is pure
  storage.
- **`lft` marks a record the learner never answered at that level**, written by
  `liftStatement` when credit from a higher level CREATES the record, cleared
  by a real answer, and surviving a sync merge only when both sides carry it.
  It exists because the lift raises `seen` to keep `correct <= seen`, so a
  credit-only record is otherwise identical to "answered here and got it
  right". That cost a real bug (2026-09-19): the Final Stretch diagnosis read
  those phantom English answers as evidence and told an Italian-browser
  learner, who is put on Solo italiano at launch and never answers in English
  at all, that their ITALIAN needed review. **Never read a lower level's record
  as evidence that the learner answered there without checking `lft`.**
- **The two diagnosis groups on the Final Stretch page take DIFFERENT
  remedies, and each lives where its remedy is.** "Missed in English and
  Italian" is a rule gap, so its rows are the claimed paragraphs and link to
  the notes. "Right in English, missed in Italian" is a reading failure, and
  the maintainer pointed out on 2026-09-19 that a topic link is useless for it
  (nobody misreads *fino* differently by topic): the learner needs to re-read
  the statement against its English. That happens IN THE WEAK SPOTS DRILL,
  not on the page: a list of the statements there, each opening to a glossed
  Italian/English pair, was built the same day and cut the same day as
  unwieldy. So `renderStudyCard` marks each drill statement with its kind
  (`drillMissKind`, the same reading as `missStatsFor`): a language miss gets
  a note and, the FIRST time round, an EN pill before the answer; after one
  correct answer the pill goes and the note stays; a rule miss gets its note
  only, since the 📖 beside it is the remedy. "First time round" is read from
  the Italiano record (missed there, streak 0), NOT from the governing streak:
  a statement missed at L2 only needs ONE clean Italiano answer to leave the
  drill, so a pill on it would let an answer read with the English open
  release it, while an Italiano miss needs two, which guarantees the second
  round is taken without the pill. The page keeps the count, the pointer to
  the drill, and the vocabulary review (see "Vocabulary retention"). **The
  "Words that keep appearing in these" line (`recurringWords`) was REMOVED
  in 20261001w** at the maintainer's word: it ranked by recurrence, which put
  the common phrases he knows at the front (*il segnale raffigurato si
  trova*, *segnale di indicazione*), and it was the third-of-a-second cost of
  every render of the section (26 ms without it). The review covers the same
  misses word by word, rarest first.
- **The rule list's topic headings are DISCLOSURES, all closed** (maintainer's
  request, 2026-09-21; `_missOpenTopics`, not persisted). What they replaced
  was a cut at the eighth row plus a "Show N more", and the reason that was
  wrong is the page's own first question: the reader wants to know WHERE their
  misses are before reading any of them, and a truncated list hid whole topics
  behind a button. One tap opens a topic, and several may be open at once.
- **ALL 25 TOPICS are listed, not only the ones holding a miss**, asked for the
  same day after the maintainer read the list and asked what it was organised
  by. That question is the symptom worth remembering: a list that shows only
  what is wrong cannot be read as a per-topic report, because a topic answered
  cleanly and a topic never opened are both simply ABSENT and neither absence
  can be told from the other. The list is now built from
  `topicsInStudyOrder()`, and a topic appears in one of three states:
  - misses at this level → a disclosure, percentage and ratio;
  - answered with none → `0%` and `0 of N`, muted, a `div` rather than a
    button, since a control that does nothing when pressed is worse than text;
  - nothing answered yet → `fs.weakNone` in words. NOT `0%`, which would read
    as a perfect topic when it means an untouched one. This matters here
    because the section is gated on the two lower levels being finished while
    Italian only is usually part-way through, so several topics legitimately
    have an empty denominator.
- **The order is misses first, then answered-clean, then untouched**, with the
  app's own topic order (`compareTopics`) breaking ties, so the work is at the
  top and the report tails off into what needs nothing. The sort is done in the
  RENDER here rather than in `missStatsFor`, because it orders topics and that
  function orders rows.
- **A "0" here means no RULE misses, not a clean topic.** The list sits under
  "Missed in English and Italian", so a topic with plenty of language misses
  shows zero on this line, which is correct for the heading it sits under and
  would be wrong if this block were ever moved or retitled.
- **Beside a topic: the PERCENTAGE (`.weak-pct`), then the ratio it came from
  (`.weak-num`, `fs.weakOf`).** This took two rounds on 2026-09-21. A bare
  count came first and says nothing about how the topic went, since 13 is heavy
  in a topic of 95 and light in one of 280; the ratio came second and the
  maintainer asked whether a percentage would read better. It does, and BOTH
  are kept rather than swapped: the percentage is the only part that can be
  compared across topics, and the ratio behind it is what says whether the
  percentage rests on twenty answers or four hundred. So the percentage carries
  the weight and the ratio is muted and smaller.
- **The denominator is statements ANSWERED at this level, not the topic's full
  size**, so it counts the way the stat line at the top of the section counts.
  At 29% through a level those two differ by a factor of three, and a reader
  comparing the topic line with the section line must not be reading two
  different measures.
- **The order is still by how many misses a topic holds, not by rate.** The
  list is a reading plan and the topic with the most to read comes first. A
  percentage on screen does invite comparing topics; changing to a rate order
  would put a topic with two misses out of nine answered above one with sixty,
  so it needs a floor on the denominator first.
- **A "Memorize these" list was built and REVERTED the same day (20260930k,
  reverted in 20260930l).** It printed every statement missed three times or
  more across the levels and the mocks, with its answer in front. The
  maintainer asked for it about 22934, then read the result and called it a
  bad idea: a page of statements with their answers is a list to memorize,
  and the app's position is that the RULE is what gets learned. 22934 itself
  is already on the Ambiguous tab with `warn`/`warn_it`. Do not rebuild it
  from the per-level `miss` counters, which still make it a one-function job.
  **What replaced it (20260930m): the drill prints the count.** Every
  statement in the Weak spots drill carries "missed N times" on its number
  line (`missTotal`, the three levels and the mocks added, `lft` records
  excluded), and at `DRILL_ATTENTION` (four) or more it turns the wrong color
  and gains a ⚠️. The count is the learner's own history and reads alike for
  VERO and FALSO, so it leaks nothing. `scripts/check_drill_misses.js`, 6
  checks in each face. **The count wraps under the number on a narrow card
  (20261005h, maintainer's screenshot, 2026-09-30)**: with the ↺ and the 📖
  both on the number line, a nowrap "missed 3 times" ran on underneath the
  ↺. `.stmt-head-left` now carries `flex-wrap: wrap`, so the count takes a
  second line instead; measured with Playwright at 260 px, the count's right
  edge moved from 24 px past the ↺ to 34 px short of it.
- **The numerator counts STATEMENTS, not rows**, so a topic showing 13 may open
  to fewer than 13 paragraphs when two of its statements share a claim. That is
  deliberate: those numerators must add up to the group total above them, which
  is also a count of statements. Verified in `/tmp/miss_dom.js`, 26 checks; its
  seed deliberately leaves two topics unanswered at L3 and two answered clean,
  or the three states never all appear on screen.

## Recent form: the chance of passing the next sitting (`mockRecentForm`)

- **One line under the readiness ring, and it names the REAL EXAM.** Worked
  example: *"Chance of passing the real exam: 77%. From your last 5 mock
  exams, which you all passed."*
- **NONE of the statistics reaches the screen**, and the maintainer had to say
  so on 2026-09-21 after the first wording shipped as *"On that form, you would
  pass a single sitting about 77% of the time."* Two faults in one sentence.
  "On that form" is sporting register, which the colloquialism ban covers, and
  "a single sitting" is a careful distinction the learner never asked for: they
  want the chance of passing the exam they are going to sit. No mean, no
  spread, no degrees of freedom, no interval, no mention of a t. The arithmetic
  is the app's problem and the number is the learner's.
- **It is a STUDENT-T PREDICTION INTERVAL, and that was the maintainer's call
  on 2026-09-21 over my objection.** Worth recording as a mistake, because the
  shape of it will recur. He said a high average AND a low spread are what
  decide readiness. I answered that the spread is not a free parameter, since
  30 statements at a per-statement rate p score with SD `sqrt(30·p·(1−p))`,
  1.40 wrong at 93%, and built a plain binomial estimate. That reasoning holds
  only under the assumption I never examined, that **p is CONSTANT across
  sheets**. A learner whose sheets scatter is not the same as one whose sheets
  cluster, and the difference is real, measurable and exactly what he meant.
  He then named the right tool himself and asked why not use it. He was right
  on both counts. When a suggestion is refused on a model's own terms, check
  whether the model is the thing in question.
- **What the binomial could not see.** Two windows, same average of 2.4 wrong:
  `1, 2, 6, 1, 2` and `0, 5, 1, 6, 0`. The binomial gives **78% to both**. The
  t-prediction gives **67%** and **63%**. It was also blind to the size of the
  window: three sheets and thirty produced equally confident answers.
- **The arithmetic.** Mean and sample SD of the window's wrong-counts, then
  `t = (3.5 − mean) / (s·sqrt(1 + 1/n))`, chance `= P(T_{n−1} ≤ t)`. The `1 +`
  is the new sheet's own variation and the `1/n` the uncertainty in the mean,
  which is the whole difference between PREDICTING an observation and
  estimating an average; a confidence interval would have used `1/n` alone and
  been far too narrow. The `3.5` is a continuity correction, since scores are
  whole numbers and the mark is "3 or fewer".
- **The spread has a FLOOR and it is the binomial one**, `max(observed,
  sqrt(30·p·(1−p)))`. Five sheets can land closer together than the sheet's own
  sampling noise by luck, and five identical scores give `s = 0`, which would
  predict with false certainty; the harness checks that case. So the old
  reasoning survives in the right place, as a lower bound rather than as the
  whole model, and the observed spread takes over the moment the learner is
  genuinely more erratic than the draw itself.
- **`studentT` is exact, not an approximation**: Lanczos `logGamma`, a Lentz
  continued fraction for the incomplete beta, and the standard identity. It
  agrees with `scipy.stats.t.cdf` to **1e-12** over sixteen `(t, df)` pairs,
  and the harness reads that table from a file scipy generated, since the
  sandbox has scipy and the browser does not.
- **Below `READY_MIN_MOCKS` the line SAYS WHAT IS MISSING**, "Take one more
  mock exam for your chance of passing the real one", rather than not being
  drawn. The maintainer sat two mocks on 2026-09-21, looked for the percentage
  and reported it gone. An absent measure and a broken one look alike, so a
  line that hides itself makes the reader debug the app. Nothing is said before
  the FIRST mock, where the note above it already says there are none. Note
  that `renderExamHistory` returns early on an empty history and hides the
  whole `#exam-history` wrap, so this element is not touched at all in that
  case; a harness must read visibility through the ancestors.
- **The floor stayed at three, and it was a choice.** The arithmetic runs at
  two: his 5 and 3 wrong give 43%, and with one degree of freedom the t is at
  its heaviest-tailed, so the thinness is priced rather than hidden. He kept
  three anyway, because the line is a claim about the exam he is going to sit
  and two sheets set both a mean and a spread from two numbers. One is
  impossible whatever is decided, there being no spread to measure.
- **The window is still `READY_WINDOW` and must not be widened to buy
  precision.** The thing being measured is MOVING, since a learner improves
  while they drill, so a long window averages in sheets from a week ago and
  understates today. The t prices that thinness rather than hiding it: the same
  scores over three sheets read lower than over five, which is the honest
  direction.
- **A sheet cut short by the timer counts its unreached statements as WRONG**
  (`sheetWrong`). `finishExam` stores only the statements ANSWERED, so a sheet
  that timed out at 20 answered with 1 wrong was stored as a PASS. At the real
  exam the ten never reached are ten wrong. The ring above still averages
  `correct/total` and is left alone; this is the one place that is strict, and
  it is why the harness seeds a short sheet.
- **The rest of the line says where the number came from**, in plain facts: how
  many recent mocks, how many of them passed, and the worst score. It is not a
  hedge on the percentage, which already prices the scatter; it is the evidence
  in the learner's own terms, and it is the only thing on screen that could be
  mistaken for method.
- **Verified in jsdom**, `/tmp/form_dom.js`, 33 checks: `studentT` against the
  scipy table, its symmetry, its tails, its saturation at infinity, heavier
  tails on fewer degrees of freedom, then eight seeded windows whose end-to-end
  percentage is compared with the SAME figure computed in scipy, the two
  same-average windows priced apart, the zero-variance floor, three sheets
  priced below five, and the wording in each state. `/tmp/show_form.js` prints
  the line for four realistic runs, which is the quickest way to judge it.
- **The t was checked against KNOWN TRUTH on 2026-10-28, and it is the best
  calibrated of four models.** The maintainer asked whether a symmetric t is
  right when the scores are bounded at 30 and skewed near a perfect sheet.
  Comparing the t with a binomial on his own export suggested it was about
  one point optimistic near 5%, and that was WRONG: it measured one model
  against another. The test that settles it is a simulation in which the
  truth is set by hand. A learner is given a true error rate and a true
  day-to-day variation of that rate (none, or a beta-binomial with
  intra-sheet correlation 0.01 or 0.03). Their exact chance of failing then
  follows from that distribution, and 15 or 30 mock sheets are drawn from it,
  300 histories per case. Over true chances from 0.8% to 15.5%, the t's
  average prediction stayed within about 1.5 points of the truth, leaning
  cautious. A binomial with an uncertain rate (bounded and skewed) was as
  good with no day-to-day variation and optimistic with it (a true 6.8% read
  3.5%, banner shown 76% of the time). Beta-binomials that put a prior on
  the variation overstated by 2 to 8 points, and with a flat prior almost
  never showed the banner. The skew does not matter because the app needs
  one tail probability, 4 or more wrong, about 1.5 to 2 standard deviations
  out, where the t's heavier tails and the binomial floor make up for it.
  The truth is only as good as the generating model. It assumes the sheets
  are independent and the learner is not improving within the window. It
  ignores the spread-reducing effect of drawing by topic, which would make
  the binomial floor, and so the t, more cautious still. Do not replace the t
  on a model-to-model comparison; rerun this simulation (rebuild it from this
  description, since it lived in a session scratchpad) against any
  candidate.

## "Why?" in the weak spots (20261007m)

- **Why? opens the drill's own English line** (reported 2026-10-01). A
  language miss in the drill carries the statement's English behind the
  drill's EN pill (`.stmt-drill-en`), and `showStatementAnswered` adds no
  twin for `enOnWhy` when that line exists, but it never opened it either,
  so Why? showed the explanation and left the English hidden. Now Why?
  (and the "show the explanation after a correct answer" setting) opens
  `.stmt-drill-en`, marks its pill, adds "Words in this question" under it,
  and a second tap folds them, unless the learner had opened the line
  before answering. `scripts/check_drill_why_en.js`, 7 checks in English,
  2 in Italian.

## Adding a right answer to the weak spots (20261007f)

- **Asked for by the maintainer on 2026-10-01**: a right answer in a mock
  can still be a guess. Each right row of the review (live and past) has
  "+ Add to weak spots"; a second tap takes it back. `toggleWeakPin` sets
  `pin` on the Italiano record and the run to zero, keeping the old run in
  `pinPrev` for the take-back; NO miss is recorded, so the miss counts, the
  keep-missing list and the statistics stay as they were. `difficultCards`
  admits a pinned statement without a miss, `drillCleanRun` makes it owe two
  right answers in a row, and `drillMissKind` gives it no language-miss note
  (it was never missed in Italian). The merge keeps the latest `pin`.
  "Cleared" reads `correct >= 1`, so the reset never un-clears a card or
  brings back the full dashboard. `scripts/check_weak_pin.js`, 11 checks in
  each face.

## One readiness figure on Statistics (20261007i)

- **The ring shows the chance of passing, not the average** (maintainer,
  2026-10-01, after reading 95% "mock avg", "exam-ready at 93% or better"
  and "Chance of passing: 82%" side by side). The ring is the Student-t
  prediction from the last `READY_WINDOW` sheets, labelled "chance of
  passing", amber below `READY_BANNER_CHANCE` (95%) and green at or above.
  The note beside it is the evidence alone ("From your last 5 mock exams:
  you passed 4, and your worst had 4 wrong"), the second note
  (`#exam-form-note`) is hidden, and `mockReadiness` with its 93% average is
  deleted, which supersedes the line in the paperwork section saying the
  ring "sits at 93%". The pace line uses timed mocks when there are any
  (`exam.mockPace`, mean of time used over questions, last 5 sheets), and
  the study pace otherwise. **Past Results closes with two rows (20261007j,
  maintainer's request)**: the mean and the sample standard deviation (n − 1,
  as the prediction uses) of the score and of the time over every result
  listed; the time only over the mocks that carry one, and a dash where
  fewer than two values exist. Numbers follow the reader's locale (28,4 in
  Italian). The table's cells are tighter below 440 px so "Standard
  deviation" fits a 320-px screen. `scripts/check_stats_ring.js`, 17 checks
  in each face. **Every column sorts (20261008b, maintainer,
  2026-10-02)**: each heading is a button (`.exam-sort`); a tap orders by
  that column, descending first, and a second tap reverses, with an arrow on
  the active one. The order is `_examSort`, kept for the session, newest
  first at launch. Rows keep `data-idx`, their index in the stored history,
  so a sorted row opens its own exam; a mock with no time sorts last in
  either direction; the two closing rows stay in the foot.
  The row whose exam is open below the table is highlighted
  (`tr.is-open`, `markOpenExamRow`, 20261008c), and only while it is open.
  `scripts/check_exam_sort.js`, 18 checks in each face.

## "If you had to guess" (Statistics page, 20261007p)

- **Thirteen words and phrases whose statements lean true or false by 70%
  or more**, asked for by the maintainer on 2026-10-01, placed on the
  Statistics page (his choice, as statistics) and shown to every user. The
  list came from a scan of every word and two-word phrase in the live bank:
  at least 50 statements, 70% or more overall, and 65% or more in each of
  two halves split by CARD so siblings cannot prop each other up. He kept
  all thirteen, including three with no linguistic reason (`indica una`,
  `trovare`, `modo`), whose reason line says so. Lean false: riservata,
  indica una, solo se, ma, solo, purché, consentita, è obbligatorio. Lean
  true: raffigurato può, attenzione, prudenza, trovare, modo.
- **The list is `GUESS_CUES` in app.js, a JSON block between `/*json*/` and
  `/*end*/`**; the page computes each count and rate live
  (`guessCueStats`, words as `[a-zàèéìòù']+`, a two-word cue as two
  consecutive words), and `validate_data.py` parses the same block and fails
  if a cue drops under 70% or 50 statements. Proved by flipping one cue.
- **No example statements**, so it cannot become an answer list to memorize;
  the intro says to use it only for a question that cannot be worked out.
  `scripts/check_guess_cues.js`, 11 checks in each face.
- **Both Statistics sections sit in closed disclosures since 20261007q**
  (maintainer's request): "Questions you keep missing" and "If you had to
  guess" are each a `details.rules-note.stats-box`, the dashboard panels'
  look, closed at first; the open state lasts the session (`_kmOpen`,
  `_guessOpen`), since a change of a control redraws the section. `#exam-weak`
  and `#exam-guess` carry `width: 100%`, because a grid item with auto side
  margins shrinks to its content and drew the closed boxes as narrow pills.

- **The section is "Statistical strategies" since 20261007u (maintainer,
  2026-10-02)**, *Strategie statistiche*, and holds two parts. First "Which
  topics to review first": a table of the 25 topics with their size, their
  places on a sheet ("1" or "1 or 2" for the eight `SAFETY_TOPICS`) and the
  chance that one given statement appears on a sheet, places divided by size
  (`topicOddsRows`, 1.3% for the smallest safety topic down to 0.15% for
  *Segnali di pericolo*), highest first, then three sentences of advice.
  Then "If you had to guess" as a heading over the cue tables. Each topic name
  in the table is a link that opens that topic's notes (`.topic-odds-link`,
  `openReview`, 20261008a, maintainer's request). **The
  per-topic draw is NOT official.** The decree of 27 October 2021 and
  circular n. 38460 of 14 December 2021 say only that the draw is random
  and the method is "confirmed"; the SIDA preface says the highlighted
  safety topics get two questions instead of one, and its contents highlight
  sections covering exactly our eight topics, which would make 33, so which
  five take a second place is unknown (the app picks five of the eight at
  random per sheet, each at most once more). The text on the page says the
  Ministry does not publish the rule; keep that sentence. Measured on the
  maintainer's record: the plausible rules span about nine points of pass
  rate and the app's sits near the hard end. Reweighting the weak-spots
  drill by these odds was offered and NOT decided; do not do it unasked.

- **Advice from the learner's own mocks, and the trend (20261008g,
  maintainer, 2026-10-02).** He reported that most of his mock mistakes are
  the Italian, not the rule; his 25 mistakes over 15 mocks were 17 false
  statements marked true. Four additions, all on Statistics:
  - **The lean line** (`#exam-lean-note`, `mockLean`): "Of your 25 mock exam
    mistakes, 17 were false statements you marked true", either direction,
    shown only with `MOCK_LEAN_MIN` (10) mistakes split two to one or more.
  - **The spare-time sentence**, appended to the timed pace line when the
    mocks average 20 seconds a question or less.
  - **"When you do not fully understand the Italian"**, a third part of
    Statistical strategies, five steps and a link that opens the Grammar tab
    at "Taking a statement apart" (`openGrammarTopic`). Never for an Italian
    browser. Under the cue tables, for everyone, one line on length computed
    from the bank (12 words or fewer 58% false, 23 or more 58% true).
  - **"Mock exam trend"** (`#exam-trend`, `renderMockTrend`), since
    20261009i near the top of the page, open and NOT in a disclosure
    (maintainer, 2026-10-03). Since 20261009s the readiness ring and its
    notes come FIRST, above the trend, in a wrapper of their own
    (`#exam-readiness-top`, moved out of `#exam-history` in
    `renderExamHistory`); the past-results table, its
    hint, its two buttons and the opened past exam moved into a closed
    disclosure "Past results (N)" (`#exam-history-box`, built in
    `renderExamHistory`, so a stale cached page gets it too). Since
    20261009k "Take another mock exam" has its own row right below the
    trend (`#stats-mock-row`), outside that disclosure, and each mock's dot
    is colored by result: green a pass, amber a pass at the limit (27
    correct), red a fail (`--tc-pass`, `--tc-edge`, `--tc-fail`, run
    through the dataviz validator for color-blind separation in both
    themes; the dot's height relative to the pass line carries the same
    information, so color is never the only signal). Shown from
    the FOURTH mock on
    (`TREND_MIN_MOCKS`, 20261008q, maintainer; it was the second). The
    chart's axis starts at mock 3 (`TREND_FIRST`, 20261008r), the first
    count with a band; the figures at each count still use every earlier
    mock. He asked
    for the EFFORT instead of a date, with the scores and the standard
    deviation plotted against the count. First line: the effort in mocks
    from `mockPlan()`. Chart one: each mock's CORRECT answers as dots (he
    asked for correct, not wrong, in 20261008j; the effort line and the
    dashboard's no-date line speak in correct answers too), the average of
    the last fifteen as a line, the pass mark (27) and the average the 5%
    target needs (about 28.7, `mockTrendNeed`) as levels whose
    values sit in the right gutter. Chart two: the standard deviation over
    the same window against what chance alone gives, the prediction's own
    floor, with a note saying what that line is. Neither scale starts at
    zero (same release): the scores run from just under the lowest to 30,
    the spread from the half step under its lowest value. Its
    y ticks are half steps (0.0, 0.5, ...), the counts' are whole
    (20261008h, maintainer). **The comparison line is NOT drawn since
    20261008k**: he asked what "From chance alone", then "Expected from
    the random draw of questions", told the user, and it told them
    nothing they could act on. The chart shows the learner's spread alone,
    and the comparison only chooses one of two sentences under it: steady
    (raise the average), or, at more than `TREND_UNSTEADY` (1.25) times the
    draw's spread, varying more than the draw explains. Give the learner
    the conclusion, not the statistic it came from. **The spread is drawn
    as a RANGE since 20261008l** (maintainer: a standard deviation is itself
    uncertain): from the third mock on, a thin bar per count spans the
    range the true value lies in with 2 chances in 3 (`sdRange`, the
    chi-square interval, `SD_RANGE_P` 0.68, checked against scipy to 1e-6;
    `gammaP` and `chiSquareQuantile` were added for it), with the measured
    value as a dot on it. The range is NOT symmetric, so the dot sits nearer
    its low end; he had asked for a bar centered on the value, and was told
    why it is not. The bars shorten up to the fifteen the window holds and
    no further. The scale is capped at 4, clipping an early tall bar. The
    unsteady sentence now needs the LOW end of the range above the draw's
    spread, which replaced the 1.25 factor. **The average carries its
    range too (20261008m, his next request)**: a shaded band around the
    average line on the first chart, mean ± t·s/√n at the same 2 chances in
    3 (`meanRange`, `tQuantile`), from the second mock on, with s the
    prediction's own spread (the larger of the measured one and the
    draw's). This one IS symmetric. A band, not bars, because that chart
    already holds a dot per mock. The legend and tooltip give the range; on
    his fifteen it is 28.0 to 28.7, which reaches the 28.7 needed. **That band was
    the wrong quantity and was REPLACED in 20261008n.** He asked whether a
    learner who is not ready should not see the uncertainty reach below 27,
    and he was right: the range of the average says where the true mean
    lies, while readiness is about where the NEXT SINGLE score falls. The
    band is now the prediction interval, mean ± t(0.95, n−1)·s·√(1 + 1/n)
    (`nextRange`, 9 chances in 10 two-sided, from the third mock; **the legend gives the range in WHOLE scores with the chance of that range** since 20261028e, maintainer. Each band edge is rounded to the nearest score, the prediction's own continuity correction, so a lower edge at or above 26.5 shows as 27, exactly the banner's test ("26.8–30" read as though 26.8 were a score, 20261028d). The chance quoted is computed from the same t for the range of whole scores shown, not the band's nominal 90: a range ending at 30 has nothing above it, so "27–30" carries exactly the chance of passing and its complement is rounded as the chance of failing is, so the two add to 100 on screen (96.9 beside 3.1%). Since 20261028h it reads "96.9% chance your next score is 27 to 30" (Italian "96,9% di probabilità che il prossimo punteggio sia tra 27 e 30"), a percentage like the chance of failing beside it; "chances in 100" fitted only the fixed whole figures before. Two releases quoted a fixed 90, then 95, and the maintainer saw that "27–30, 95 chances in 100" beside "3.1% chance of failing" did not add up. `nextRange` returns `mean`, `se` and `df` for this; the tooltip's "Next score" is in whole scores too; `check_mock_trend.js` asserts the sum to 100 and prices two other ranges independently; the note under the chart speaks in whole scores too since 20261028f: "You are ready when every score in the range is 27 or more. The range now starts at 26.", drawn only while the range starts below 27, which is the banner's test; the ready sentence was removed in 20261028g as a repeat of the legend), and its
    lower edge is the banner's own test: the chance of passing is 95%
    exactly when the edge clears the pass line, which is drawn at 26.5,
    between a failing 26 and a passing 27. A sentence under the chart says
    "You are ready when the whole band is above the pass line. Its lower
    edge is at 26.1." or that the whole band is above it. The "average
    needed" level left the chart (the effort line still names it), and the
    scale reaches down to the band's edge, at most to 22. When a learner
    asks whether a chart should show something, check whether the quantity
    drawn is the one the decision rests on. **The standard deviation chart was
    REMOVED in 20261008o** at his question ("do we really need it?"): the
    band already carries the spread. Its one use stays as a sentence under
    the chart (steady, raise the average; or varying more than the draw
    explains), so `sdRange` and its helpers remain. The box holds ONE chart
    now, and its scale reaches down to the lowest edge the band has had
    (at most to 15), so the band's whole bottom shows. **The sentence under it
    names no statistics (20261008p)**: "all this comparison to randomly
    drawn questions is NOT going to make any sense to the casual user." It
    reads "To move the band up, raise your average score." or "Your scores
    vary a lot from one mock exam to the next. Steadier scores would narrow
    the band.", and shows only while the band is short of the line. This is
    the third time on this chart that the analyst's vocabulary reached the
    screen; see "Write for the LEARNER" under UI prose. One
    y scale per chart, a legend each, a hairline and tooltip on hover or
    tap. Drawn as inline SVG at the box's real width (text keeps its size on
    a phone), redrawn on open and on resize.
  **A tap or click on a dot opens that mock's exam below (20261010k,
  maintainer, 2026-10-04)**, as a row of the Past results table does:
  `openPastExamReview` runs on the sheet's index in the
  stored history (`h` on each row of `mockTrendData`), the row is marked and
  the dot ringed (`.tc-dot.is-open`, in `markOpenExamRow`), and a second
  tap closes it. The nearest mock to the tap is taken, as for the tooltip,
  which now ends "Tap or click to see this exam below." The table stays closed
  (20261010l, maintainer): the opened exam (`#exam-history-review`) now sits
  just AFTER the Past results disclosure, not inside it, so it shows with
  the box shut; opened from a row it still lands right under the buttons. A mock saved
  without its questions opens nothing.
  **A trend-based date was considered and NOT built**: on his nine mocks
  the slope was +0.02 ± 0.18 wrong per mock, and a simulated learner
  improving from 2.5 to 1.0 wrong over thirty mocks showed no trend 37% of
  the time at ten mocks. A trend needs about thirty mocks or an improvement
  near 3 wrong to be visible. A version gated on a statistical test was
  offered; do not build it unasked.
  `scripts/check_mock_trend.js`, 21 checks in English, 19 in Italian.
  **The axis is LINEAR IN TIME since 20261024e** (maintainer, 2026-10-24,
  asked for the date on the axis and then rejected 20261024d's one slot per
  mock with date labels as not linear). `trendXScale(W, cfg)` is the one
  horizontal scale, used by the drawing and by the hover and tap: with
  `cfg.xs` (each mock's timestamp, indexed by count, from `mockTrendData`'s
  `date`) a count maps to its moment between the first drawn mock and the
  last; without it, one slot per count as before. The band, the average
  line and the dots are drawn at those moments, so six mocks on one day sit
  close together and a gap of days is an empty stretch. Labels: the first
  mock's date at the left edge, then local midnights every d days with d
  chosen so labels sit 44 px apart, skipping one that would crowd the last.
  The hover picks the nearest mock by pixel. The caption reads "Date of
  each mock exam"; the tooltip adds the date. `check_mock_trend.js` asserts
  the scale's linearity (an hour in a three-hour span sits a third of the
  way) and even spacing on its hour-apart seed, 24 checks in English, 22
  in Italian. Screenshotted at 390 and 800 px.
  **By date or by count (20261024f, maintainer: on the time axis the mocks
  of one day overlap).** Two pill buttons above the chart (`.trend-axis-btn`,
  `data-axis` time or count), the choice in `patente-trend-axis` on the
  device like the grammar toggle, not synced; By date is the default. By
  count passes no `xs`, so the scale is one slot per mock and the caption
  "Mock exam number" returns. The check clicks both.

## The figure shown is the chance of FAILING (20261007o)

- **Maintainer, 2026-10-01: the chance of failing is more meaningful to a
  learner deciding whether to book.** The calculation is unchanged (the
  Student-t chance of passing the next sheet); what is shown is
  `failPct(chance)`, rounded UP so it never reads better than the
  prediction. The ring's arc grows with the chance of failing, so a short
  arc is good; it is green at 5% or less (the banner's bar, still
  `chance >= READY_BANNER_CHANCE`) and amber above. Changed with it: the
  ring label, the banner ("Chance of failing the real exam: 3%, from your
  last 15 mock exams"), the take-more-mocks note, the Clear all results
  warning, and the How-to paragraph on the Statistics page, which until
  then still described the 93% average ring. Read every older bullet here
  that says "chance of passing" as the quantity computed, not the one
  displayed.

## Variety across mocks (20261009v)

- **No statement met in the last 20 mocks is drawn again (maintainer,
  2026-10-03)**, and neither is one whose wording matches it word for word
  (`EXAM_FRESH_MOCKS`, `recentExamKeys`, `examTextKey`). He had checked
  twice whether the draw repeated questions more than chance; it did not
  (25 mocks: 47 statements met twice against 49.9 by chance), but he judged
  the repeats a lost teaching opportunity. The composition is untouched:
  one statement per topic and five more from the safety topics, chosen as
  before; only the pool inside each topic leaves out the recent ones, with
  a fallback to the whole topic that cannot fire in practice (the smallest
  topic has 103 statements, twenty mocks take at most 40). No two
  statements with the same wording appear on one sheet either. The flat
  random mix in Settings filters the same way. `check_mock_variety.js`
  simulates thirty mocks: the composition holds on every one, and nothing
  repeats within any twenty in a row; the previous build gives 65 repeats.

## Which mocks the readiness figure reads (20261009a)

- **Every mock on record, with no cap, unless the scores have clearly
  changed level (maintainer, 2026-10-02: "I don't like the idea of forcing
  N to 15 max if the user keeps taking mock exams").** Fifteen had no
  derivation: it was the banner's minimum reused as a maximum. A cap exists
  only because a learner improves and old mocks then describe a weaker one,
  so the rule keeps every mock by default and leaves out the older ones
  only on evidence. `mockRecentSheets()` (no argument) is the one place
  that decides, and the ring, its note, the pace line, the banner
  (`examReady`), the effort estimate (`mockPlan`) and the trend chart all
  read it. Read every older bullet that says "the last fifteen" or
  `READY_WINDOW` as superseded by this.
- **The test (`mockWindowStart`).** For each split of the history into an
  older part (at least `WINDOW_MIN_OLD`, 5) and a recent part (at least
  `WINDOW_MIN_RECENT`, 15), the errors in the recent part are compared with
  what an unchanged error rate would give, Binomial(all errors, recent
  share of the sheets), two-sided (`binomCdf`, checked against scipy). The
  split with the smallest p is taken when p is under `WINDOW_ALPHA` (0.02).
  A change for the worse cuts as well. So nothing is cut before twenty
  mocks, and the window is never under fifteen.
- **Measured before choosing 0.02.** A steady learner loses old sheets
  wrongly in 4% of histories at 30 mocks and 9% at 50. A steady learner at
  1.5 wrong (true 6.1%) reads 5.9% +- 2.4 at 60 mocks with every mock,
  against 8.0% +- 5.0 with the last fifteen: the cap was both biased high
  and twice as noisy. A learner improving from 2.5 to 1.2 wrong (true 3.1%)
  reads 4.5% at mock 40 under this rule, against 8.6% with every mock and
  4.1% with the last fifteen.
- **The banner still needs fifteen mocks**, and the lucky-run weakness of a
  rolling fifteen (a learner at 1.7 wrong saw the banner within 30 mocks
  42% of the time) is gone, since the window no longer slides.
- **When a cut is made the note says so**: "Earlier mock exams are left out
  because your scores have changed since." (`fs.formCut`).
- **The effort estimate adds its projected mocks to the window** rather
  than sliding it (`mockReadyAt`, up to `MOCK_PLAN_MAX` 60), so it is longer
  than under the cap: his nine mocks of that morning went from 13 more to
  26. `mockNeedAverage(n)` gives the average the bar needs at n mocks. The
  trend chart draws each count with the window as it stood then.
- The stored history holds at most `EXAM_HISTORY_LIMIT` (50) mocks, so
  "every mock" means the latest fifty.
- **Student-t was kept over a Poisson or binomial model** (his question the
  same day). A binomial with an uncertain rate gives 10.3% where the t gives
  10.1% on his data and tracks it within a point across levels, but it
  assumes a steady learner and cannot see erratic scores, which is why he
  chose the t on 2026-09-21. The area is taken below 26.5 correct.
- `scripts/check_mock_window.js`, 12 checks in each face.

- **Two significant figures below 10% (20261009u, maintainer).** The ring
  and the banner show `failPctText(chance)`: 8.7, 0.44 under 10%, whole
  numbers from 10 up, still rounded UP, with the reader's decimal separator
  (8,7 in Italian). `failPct` stays the integer for anything that compares.

## The "ready for the exam" banner (20261007e)

- **It needs fifteen mocks and a 95% prediction, at the maintainer's word
  (2026-10-01).** It had shown at three mocks averaging 93% (his 30, 28 and
  28 of a single afternoon), said "your last 5" whatever the count, ignored
  the open weak spots beside it, and disagreed with the Statistics page's
  88%. `examReady()` now runs `mockRecentForm(15, 15)`, the same Student-t
  prediction as the Statistics line but over the last 15 sheets, and shows
  the banner only at a chance of 95% or more with no weak spot open. The
  text is drawn in JS with the real figures ("Ready for the exam. Chance of
  passing the real exam: 97%, from your last 15 mock exams."), so the static
  `banner.ready` markup's `data-i18n-html` is removed. The study projection's
  mock allowance drops to zero on the same test.
- **The same banner says when the learner is NOT ready (20261007x,
  maintainer, 2026-10-02).** Once one mock is on record, `#exam-ready-banner`
  shows in the warning color (`banner-warn`) with what is missing, the first
  that applies: fewer than fifteen mocks (the maintainer's wording, 20261007z: "We need
  you to take at least 15 mock exams before we can make any recommendations
  on whether you are ready for the official exam. You have taken 3."), a chance of failing over the target (the figure, the count and
  "The target is 5% or less"), or weak spots still open (their count). With
  no result on record, or after Clear all results, it is hidden; when
  `examReady().ready` it turns back to the green text. `examReady` now also
  returns `taken` and `weak`. `check_ready_banner.js` is 17 checks in each
  face; the previous build fails 6.
- **Open weak spots no longer make the banner a warning (20261009x,
  maintainer, 2026-10-03: "I wouldn't be so bleak").** At fifteen mocks and
  a 95% chance the banner is green and reads "Ready for the exam", and open
  weak spots are a suggestion in the same line (`banner.weakOpen`). Every
  ready banner then says what comes next (`banner.readyNext`): a learner
  enrolled at a driving school takes the mock exams in the school's app,
  since the school decides from those, and until the exam keeps taking
  mock exams here. `examReady().ready` still requires no weak spot and
  still drives the dashboard's "ready now" line; the banner uses the chance
  alone. The phase AFTER ready, staying prepared while waiting for the
  exam date, has no feature of its own yet; it was raised the same day and
  is undecided.
- **The exam date (20261009y, maintainer, 2026-10-03).** Once the learner
  is at the bar (fifteen mocks, 95%), a box right under the banner
  (`#exam-date-box`, `renderExamDate`, built in JS) asks "When is your
  exam?". With a date set it reads "Your exam is in N days, on Monday,
  October 12", then the pace, at least one mock exam a day until then, and
  whether today's has been taken (the count of mocks dated today). The
  date is a SETTING (`EXAM_DATE_KEY`, `examDate` in the bundle, stamped,
  guarded with `!== undefined` in the merge). A date in the past is
  refused on entry and dropped once it passes, so the question returns. A
  date once set stays on screen if the mocks slip below the bar. The day
  itself reads "Your exam is today" with no pacing. One a day is a floor
  chosen for simplicity, not derived. **With a date entered the green
  ready banner is hidden (20261009z, maintainer)**; a warning banner still
  shows, and removing the date brings the ready banner back.
  **And the dashboard's done block projects no ready date (20261010a)**:
  the "you could be ready around" and "ready now" lines are left out; the
  cleared line and the average stay. **The "What remains" line goes too
  since 20261011k** (maintainer): in the review stage the weak spots are
  part of the day's review, which the exam date box describes.
  **The pace is ONE mock a day and its misses, not "at least one"
  (20261010b, maintainer, 2026-10-03, after he took six in a day and asked
  whether research supports the advice).** Practice testing and distributed
  practice are the two techniques rated high utility (Dunlosky et al. 2013;
  Roediger and Karpicke 2006), spaced practice beats the same practice
  massed (Cepeda et al. 2006, 2008), and feedback adds to a test's benefit
  (Butler and Roediger 2008). So a floor with no upper limit was wrong: the
  box now says to take one a day and clear the weak spots it leaves, shows
  today's mock as not taken or done, names the weak spots open once it is
  done, and at two or more says one a day is enough. Any finer schedule
  (a mock every two or three days) is an extrapolation from studies of
  spaced restudy of facts, not a tested result, so none is claimed. The
  screen cites no research.
  **One a day is the floor, not the ceiling, since 20261021c** (maintainer,
  2026-10-21: a sheet samples 30 of 7,106 statements, so a second one
  gives the review twice as much to work with). The box says "at least
  one mock exam, two if you have the time"; the mock card after today's
  first says "A second one today is fine if you have the time" instead of
  "One a day is enough"; the count line no longer adds that one is
  enough. The review's size is unchanged.
  **Reversed in 20261023f** (maintainer, 2026-10-23, on my recommendation):
  one mock a day stays the floor, for the estimate, the rehearsal and the
  check on forgotten cleared questions, and time left over goes to
  Continue the review, not to a second mock. A mock teaches three or four
  things an hour while the review spends the hour on questions actually
  missed, and by this stage the estimate rests on fifteen or more sheets and
  moves little per mock. The box says "then one mock exam. Time left over is
  best spent continuing the review"; the mock card after today's reads
  "Time left over is best spent on the review" (`dash.mockDoneSub`).
  **Within seven days of the exam the hour goes (20261023g, maintainer,
  2026-10-23, asked whether an hour was still good advice).** `EXAM_NEAR_DAYS`
  (7): at that distance `examdate.paceNear` replaces `examdate.pace`: do as
  much of the review as you can, in two or three sittings a day, one mock a
  day, go lightly on the day before. The hour was a sustainable pace for
  weeks, not a ceiling; spacing wants gaps of a fraction of the time to the
  test, which a day already gives. `check_exam_date.js` asserts seven days
  against eight.
  **The day before the exam has its own advice (20261028a, maintainer,
  2026-10-28: "today is the day before my exam, but the app doesn't seem
  to know that").** It had shown the near-exam advice, which asks for as
  much review as possible, with the Still waiting count and the table of
  questions needing correct answers on days that no longer come. At one
  day out `examdate.paceLast` reads: go lightly today, do the day's review
  once, look over the figures you keep missing, sleep a full night, a mock
  today is optional. The Still waiting row, Continue the review and the
  pool table are left out; the figures link stays, outside the table
  (`examFiguresLinkHtml`).
  **The day before and the day itself say *In bocca al lupo!*
  (20261028b, maintainer)**, a line of its own under the advice
  (`examdate.wish`, `.exam-date-wish`), in Italian for every browser and
  with no English gloss: it is the phrase the learner will hear from the
  school, and a translation would flatten it.
  **The box is three parts since 20261023h** (maintainer, 2026-10-23: one
  paragraph had grown, with numbers scattered through it): the date as a
  line of its own, the advice paragraph (`examdate.pace` or `paceNear`,
  no longer carrying the three-day rule), then a `dl.exam-date-today` of
  rows with the figure at the right edge: Review today (N left, done, none
  left), Still waiting (the pool beyond today's set, row absent at zero),
  Mock exam today (not taken yet, done, N taken). The three-day rule now
  opens the "What is waiting in the review" disclosure (`examdate.poolRule`).
  The old sentence strings (`examdate.reviewN`, `reviewDone`, `reviewNone`,
  `reviewMore`, `todayNone`, `todayDone`, `todayMany`) are gone; checks read
  `[data-row=…] dd`. Screenshotted at 390 and 800 px.
  `scripts/check_exam_date.js`, 19 checks in each face.
- **The daily review while waiting for the exam (20261010c, maintainer,
  2026-10-03: "the best strategy ... based on scholarly works").** With an
  exam date entered, the box says to take one mock exam a day and answer
  the questions set for review, and carries "Questions to review today: N"
  with a Start button. This closes the open item on the weak spots and
  "Questions you keep missing" for this phase: both feed ONE daily set.
  - **The day run.** `noteDayRun` keeps `dr` and `dd` on the Italiano
    record: correct answers on different days in a row since the last miss.
    A second correct answer the same day adds nothing; a wrong answer (a
    mock miss included) starts it over. Written by `handleAnswer` at
    Italiano, `answerFromList` and `recordExamMisses`; the merge takes the
    later day's count, the lower on the same day. A record with no `dr` is
    judged by its old streak (`dayRunDone`), so what had left the list
    stays out. Its first answer after the change carries the old run
    over (`dr` starts from the streak, 20261010d), so earlier correct
    answers are not thrown away.
  - **The set** (`dailyReviewPool`, `dailyReviewSet`): open weak spots
    first, then EVERY statement missed in Italian and not yet correct on
    `REVIEW_DAYS` (3) different days, most-missed first; nothing answered
    today. The Statistics page's two selects do NOT apply (20261010e): the
    first build read them, and with "Missed at least 6 times" chosen there
    the maintainer's review held one question;
    `reviewPerDay()` a day. **The day's count is read from the records
    since 20261011c** (maintainer: the review did not sync): an answer in
    the review stamps `rv`, the day, on its Italiano record, the merge keeps
    the later `rv`, and `reviewDoneToday` counts today's stamps, so a second
    device offers only what is left. **Since 20261011d the device counter
    `patente_review_day` is not read at all**: it kept the desktop at 13 left
    while the iPhone, with identical records, showed the full set. A
    question also counts when it was answered in Italian today (`dd`) and
    it is one the review serves (missed at L2 or L3), which covers answers
    given before `rv` existed and weak-spot work on the same questions.
    Both of the maintainer's exports of 2026-10-04 now give 77 done, 23
    left. `check_review_sync.js`. **The pool is ordered least recently reviewed
    first (20261016f, maintainer, 2026-10-16: the next day's review began
    again with the questions done the day before).** The set was the top
    slice of a most-missed-first list, and a question answered right
    yesterday still needs more days, so it stayed at the top and the
    questions below it were never reached. `dailyReviewPool` now orders by
    the later of `rv` and `dd` on the Italiano record, never reviewed
    first, then by misses; open weak spots still lead, ordered the same
    way. A question therefore returns after the rest of the pool has had
    its turn, which is the gap successive relearning wants.
    `scripts/check_review_order.js`, 5 checks in each face; the previous
    build fails 3. **The day's set is a floor, not a ceiling (20261021d,
    maintainer, 2026-10-21).** Once it is done and the pool still holds
    questions not yet answered today, the box says "{N} more questions are
    waiting, if you have the time" and offers a secondary "Continue the
    review" (`data-ed="more"`, `startDailyReview(true)`): a session over
    the next slice of the pool, up to another day's worth, with
    `session.reviewExtra` set, counted on its own ("Extra review: 0 of
    N", `study.reviewExtraProgress`, `reviewDoneBefore` 0) rather than
    against the day's set. Its answers stamp the day as usual, so they
    count toward the three days and are not offered again today. The
    pool now also skips a record with `rv` stamped today, not only `dd`,
    so a question reviewed on another device today is not re-offered.
    **An extra session remembers itself (20261023p, maintainer,
    2026-10-23).** Continue the review a second time used to build a fresh
    block of fifty and start the header at zero. The extra answers given
    today, `reviewDoneToday() - reviewPerDay()`, taken modulo the day's
    size, are now `reviewDoneBefore` for the extra session, and the slice
    is shortened by the same count, so leaving and continuing again
    resumes the same block ("Extra review: 20 of 50"); a finished block
    starts the next one at zero. `check_review_extra.js` is 10 checks.
    **Consistently missed figures (20261023q, maintainer, 2026-10-23: a
    short list of the numbers to study in the week before the exam).**
    `missedFigureRows()` crosses each Numbers row's `asked` list with the
    records: a figure is consistently missed when one of its questions was
    missed in Italian (L2 or L3, mocks included) and is still open by the
    weak spots' test (`drillNeed > 0`). A "Consistently missed" chip on the
    Numbers tab (`reviewCat === 'missed'`, shown only with a count or while
    selected) filters to those rows, keeping the page's category order, and
    each row carries "N questions missed and still open" (`.review-missed`)
    under its Asked count. The exam-date disclosure ends with a link
    "Figures consistently missed: N" (`data-ed="figures"`,
    `openMissedFigures`). One question can turn on two figures (21538 on
    130 and 110), so the rows are not a count of questions. Group notes and
    footers are left out on the chip, so the list stays short (the first
    screenshot showed the autostrada vehicle lists under each speed). On his export
    of that day: 44 rows, about 36 figures. `scripts/check_missed_figures.js`,
    8 checks in each face; the previous build fails.
    **Two or more missed questions per figure since 20261023r** (maintainer,
    asked how many misses make the list, and chose the figure-level rule
    over a per-question threshold): `MISSED_FIGURE_MIN` (2). A single slip
    on one question no longer lists the figure. **"Still open" is the
    review's test since 20261023s**, not yet correct on three different
    days (`dayRunDone`): the weak spots' test, one right answer at
    Italiano, had emptied the chip on his export, since nearly every missed
    question had one right answer since its miss, and he reported the chip
    gone. On his export: 19 rows, about 14 figures. `missed_export.js` in
    the scratchpad ran the real function over the export, which is how the
    zero was found; an approximation in Python had said 14.
    **One flat list, most missed first, since 20261023t** (maintainer): on
    the chip the rows are one section with no category or group headings,
    sorted by open misses, and the speed twins (same value, same merged
    asked list) are shown once, deduplicated in `missedFigureRows`. On his
    export: 15 figures. The check asserts the single heading.
    **Each row names its category and group above its label (20261023u,
    maintainer: outside its category the number was unclear)**: `.review-ctx`,
    through `rowContext`, on this chip only. **The category alone since
    20261024a** (maintainer: with the groups and the Italian parentheticals
    the line was too long to read the number by): "Speeds by road type",
    in the accent color, normal case. **The group is back since 20261026b**
    (maintainer, 2026-10-27: "Speeds by road type" without the road type,
    "Speeds by vehicle" without the vehicle): the line reads category, a
    middle dot, then the row's group name(s), with every parenthetical
    dropped ("Speeds by road type · On the autostrada"), since the group
    is where the road or the vehicle sits and the parentheticals were what
    made the first line long. `check_missed_figures.js` asserts the group
    and the absence of a parenthesis. **One short line per figure since
    20261026c** (maintainer, 2026-10-27: the metadata was put together
    correctly and the entry was still hard to read, and the list is a quick
    study list for the last days). Every row with an asked list carries
    `shortEn` and `shortIt` in reference.json, a phrase of a few words that
    stands on its own ("Autostrada, new driver", "Safe distance at 130
    km/h", "Car tire, minimum tread depth"), 149 rows, written by hand in
    both languages; `validate_data.py` requires both, under 90 characters,
    with no parenthetical. On the chip the row (`.review-row.is-short`) is
    that phrase, the value (or the tap-to-see button) and the open-miss
    count, nothing else: no category or group line, no second language, no
    fine, no wrong value, no Asked count. The `rowContext` line of 20261026b
    is no longer drawn there. A new numbers row with an asked list needs its
    two short phrases or the build fails. **Since 20261026d** the count under
    the value reads "2 questions missed" (the long form is its tooltip), and
    a row whose asked list sits inside another listed row's with the same
    value is dropped as the same figure split finer: the by-vehicle towing
    rows (car with trailer 70, autotreno 70) against the by-road row that
    holds both questions. The check mirrors the subset rule. **Every phrase names the QUANTITY since 20261026e** (maintainer's
    screenshot, 2026-10-27: "Extra-urban road, towing a trailer or
    autotreno" did not say it was a speed limit): "Speed limit on an
    extra-urban road, towing a trailer or autotreno", "Distance of the
    two-bar panel from the railroad crossing", "Measure for driving drunk",
    "Points lost for parking in front of a driveway". A new short phrase
    opens with what the figure is, then the case.
    `scripts/check_review_extra.js`, 9 checks in each face; the previous
    build fails 6. **The box carries a closed disclosure, "What is waiting in
    the review" (20261023c, maintainer, 2026-10-23: he asked how many of
    the waiting questions leave with one more correct answer).**
    `reviewPoolNeeds` counts the pool by the correct days each question
    still needs (`REVIEW_DAYS` less its `dr`, or its old streak, never under
    one) and sums the minimum answers left; `examPoolHtml` draws a table
    of those rows and a line "At least N more correct answers before the
    review is empty", shown whenever the pool holds anything, open state
    kept for the session (`_examPoolOpen`). On his export of that day: 768
    waiting, 278 needing one more correct day, 490 two, none three, 1,258
    answers at least. `scripts/check_review_needs.js`, 7 checks in each
    face; the previous build fails. **The size is an hour's work less the mock (20261010f,
    maintainer)**: forty minutes at the learner's own measured seconds per
    question, doubled for looking up words and topics
    (`drillSecondsPerAnswer`), rounded down to a five, between 10 and 50
    (`REVIEW_MAX`; the ceiling was 100 until 20261021a, maintainer,
    2026-10-21: more than 50 a day is too much, and a review the learner
    cannot finish leaves no time for the mock exam).
    The box says "plan on about an hour a day". The review comes BEFORE
    the mock exam (20261010g, maintainer): the sentence names it first,
    its count precedes the mock's status, and the box sits above the row
    holding the mock exam card. It was a flat 20 for three
    releases.
  - **The session** (`startDailyReview`, `buildMode: 'daily'`): study cards
    narrowed to the set through `_drillStmts`, one pass, Finish returns to
    the dashboard. What was missed comes back another day. Leaving
    mid-way is allowed; Start then offers what is left of the day's set.
  - **The weak-spots card is hidden while a date is set**, since its
    statements are in the set. **The nav's Begin/Resume starts the review
    in this phase (20261010u, maintainer, 2026-10-04)**, not the weak-spots
    drill, which it opened until then: Begin before the day's first answer,
    Resume after it (back to the open card when the session is still in
    memory, `liveDailySession`), and hidden once the day's set is done.
    `inReviewPhase()` is the one test. With no date nothing changes.
  - **"Questions you keep missing" now releases on the same day run**: its
    select reads "N correct answers on different days". Its rows are still
    answerable, and an answer there counts for the day like any other.
  - **The mock card after today's mock (20261011i, maintainer).** In the
    review stage, once a mock is taken today, the dashboard's mock card
    reads "Today's mock exam: done. One mock exam a day is enough. The next
    one is tomorrow." and its button becomes a secondary "Take
    another". Before the review stage it is unchanged.
  - **The progress bar counts the whole day (20261011g, maintainer).**
    Starting the review again builds a new session from what is left, so
    the bar went back to empty. `session.reviewDoneBefore`, today's count
    at the start, is added in front as done in `studyCardCounts`, and the
    header reads "Today's review: 2 of 20 cards done".
  - **In the review, a correct answer opens its explanation and English
    (20261011e, maintainer, 2026-10-04).** A setting of its own,
    `REVIEW_EXPL_KEY`, ON by default, separate from the general
    "show the explanation after a correct answer", synced, and its Settings
    row (built by `ensureDashFullRow`, after that general row) is hidden
    until the review phase (`inReviewPhase`). `showStatementAnswered` reads
    it when `session.buildMode === 'daily'`.
  - **The weak spots do NOT use the day run, and must not (maintainer,
    2026-10-03).** Before an exam date is entered they clear as fast as the
    learner can manage, two correct answers in a row in one sitting, so the
    learner can move on to the mock exams. Offered and refused.
  - **Why.** Successive relearning (Rawson and Dunlosky 2011; Rawson,
    Dunlosky and Sciartelli 2013): relearn to correct in sessions spaced
    apart. Massed extra practice fades within weeks (Rohrer et al. 2005);
    equal gaps serve as well as growing ones (Karpicke and Roediger 2007).
    None of these studied a learner already at criterion on a true/false
    exam, and the 20 a day and the three days are choices, not findings.
    The screen cites none of it.
  `scripts/check_daily_review.js`, 20 checks in each face.
- **Why fifteen.** The t already prices a short run, so the minimum is about
  knowing the spread: the 95% interval for the true SD runs to 2.9 times the
  measured one at 5 sheets, 1.8 at 10, 1.6 at 15, 1.5 at 20. At the floor
  SD a learner averaging 1 wrong reaches 95% at 5 sheets, 1.25 wrong at 8,
  1.5 wrong at about 79, and 2 wrong never (the limit is 86%), which puts
  95% well above the instructor's bar of under 3 mistakes.
- **The Statistics figures read the same sheets since 20261007l**
  (`READY_WINDOW` = 15): every mock until there are fifteen, then the latest
  fifteen. They read the last 5 until then, and the maintainer asked why
  sheets were thrown away below the fifteen that the spread needs; with
  seven mocks the 5-sheet window said 76% and all seven say 83%. The ring,
  its note, the timed pace line and the banner now agree on their sheets. `scripts/check_ready_banner.js`, 9 checks in
  each face; the previous build fails 8.

## The mock sheet (it behaves like the Ministry's terminal, 20260930b)

- **Thirty statements in any order, answers editable until the sheet is
  closed, a Riepilogo before closing, no feedback until then.** Rebuilt on
  2026-09-23 after the maintainer showed SIDA's fac-simile of the Ministry's
  exam screen and asked whether ours should follow it. The mock had been
  LINEAR: an answer locked after 400 ms and the next statement arrived, with
  no way back, which trained the opposite habit from the one the real sheet
  allows (answer the sure ones first, give the doubtful ones the time left).
  `ensureExamSheet` builds the whole sheet inside `#exam-in-progress` in JS,
  so a stale index.html still gets it; `examState.answers` is now an array of
  thirty slots aligned with `items`, null until answered, and never a list
  that grows.
- **Answering does NOT advance.** The sheet moves only on Successiva. **On
  the last statement Successiva is INACTIVE (20261008u)**, as on SIDA's
  facsimile of the terminal, which the maintainer screenshotted on
  2026-10-02 (question 30: Successiva greyed, Precedente active). It opened
  the Riepilogo until 20261008t and wrapped to the first statement for one
  release; neither is what the terminal does. From the same screenshots:
  the Riepilogo is titled "Riepilogo risposte" and keeps the clock running
  at its top right (`#exam-timer-summary`); its two buttons are Indietro
  and a red Termina esame; Termina esame ALWAYS asks "Confermi di voler
  concludere l'esame in corso?" (ours adds the count of blanks when there
  are any); the result then shows Esatte, Errate and Idoneo. The start
  dialog has a second paragraph (`mock.introTip`) recommending a second
  pass through the questions if time allows.
- **The sheet matches the terminal's look and feel (20261008v, maintainer,
  2026-10-02: "I want our app to match the look and feel of the ministry
  app, which I assume is what the SIDA app does").** From his screenshots of
  SIDA's facsimile:
  - **Its labels are ITALIAN for every browser** (`xt()`, which is `t()`
    pinned to Italian): Domanda N di 30, Risposta, Tempo a disposizione,
    Riepilogo, Precedente, Successiva, Riepilogo risposte, Indietro, Termina
    esame, the confirmation on ending and the result. **NO English anywhere
    in the mock exam (20261008w, maintainer: "It must reproduce as best as
    we can, the actual exam conditions").** An English line under the
    confirmation and beside the result lasted one release. The dialog BEFORE
    the mock starts and the app-icon exit question are the app's own and
    stay in the reader's language.
  - **The chosen answer is a CROSSED-OUT letter** on a white square, not a
    filled blue one, on the sheet and in the Riepilogo.
  - **An answered chip carries a tick, and a group tab a double tick once
    all ten of its questions are answered** (above the number on a phone,
    where ten chips leave no room beside it).
  - **A bookmark at the top right of the question marks it to come back
    to** (`#exam-mark`, `examState.marks`); it sits on the counter's line,
    out of the flow, so it adds no height. The Riepilogo shows a flag on
    each row, filled when marked, and a tap on the flag toggles it.
  - **Both arrows are blue when they lead somewhere and pale when they do
    not** (question 1, question 30). On a phone held upright they show the short
    labels **Prec.** and **Succ.** in a narrow column, so the number chips
    get the width (20261009j, maintainer's screenshot).
  - **The Riepilogo lists each question in full**: number, figure,
    statement, the V and F squares, the flag. On a phone the figure goes
    under the statement.
  - **The result reads Esatte N, Errate N, Esito esame: Idoneo or Non
    idoneo**, in Italian for every browser.
  Not copied: the crest, the candidate's photo and codice fiscale, and the
  flag-and-speaker button (whether the real exam reads questions aloud is
  an open question). `check_exam_sheet.js` covers all of this. Thirty taps are part
  of the rehearsal; do not put the auto-advance back for convenience.
- **The NAVIGATION is the terminal's, copied outright; the chrome is not.**
  The maintainer decided this on 2026-09-23, on seeing the first version:
  the learner must meet nothing unfamiliar in the room, and a similar look
  and feel is no problem. So the bottom bar is the terminal's: three group
  tabs (1-10, 11-20, 21-30) over a row of ten chips for the open group, with
  Precedente and Successiva as arrow blocks either side, and the open
  statement underlined. A tab opens a group WITHOUT leaving the statement;
  moving to a statement opens its group (`_examGroup`, set in
  `goExamStatement`). What is still not copied is the Ministry's crest, the
  candidate block and the exact blue, which are the Ministry's, and four
  regions (Sicily, Trentino-Alto Adige, Valle d'Aosta, Friuli-Venezia Giulia)
  run their own systems, so even SIDA's fac-simile is not the screen everyone
  meets. In landscape at 760 px and up the answer sits at the lower right,
  where the terminal puts it; portrait stacks.
- **The whole sheet is the terminal's (20260930e).** The first copy took the
  navigation only and the maintainer said it was "not as similar as I had
  hoped", so the sheet now reproduces the screen: a WHITE surface whatever
  the app's theme (the room is what is rehearsed), a blue left column holding
  a sheet box and the clock box "Tempo a disposizione" with Riepilogo under
  it, "Domanda N di 30" and the statement at the top right, the V/F pair as
  neutral white squares outlined in the terminal's blue at the lower right
  (the chosen one fills blue; the green/red of the study card is deliberately
  NOT used here), and the bottom bar with Precedente in grey, the tabs and
  chips in the terminal's pale blue, Successiva in solid blue. The header's
  timer pill stays hidden during a sheet, since the clock is in the box. On a
  phone the left column collapses to one row (clock and Riepilogo) above the
  statement. What is still not copied: the crest and the candidate's data.
- **The controls are PINNED to the bottom of the viewport** (20260930c).
  Stacked under the card they moved with every statement, a figure or a long
  sentence pushing them a hundred pixels, and the maintainer reported it as
  disconcerting. `#exam-sheet` fills the viewport below the header with the
  card in a `1fr` row, so the answer pair and the strip stay where the hand
  expects them; a fixed card height was the alternative and it fails the
  moment a statement runs longer than the reserved space.
  **A 4:3 FRAME since 20260930g** (a 36rem cap for one release before it):
  on a tall desktop window the full-viewport sheet put the controls under a
  screen of empty space, which the maintainer reported the same day, and he
  asked whether the window could be sized to the terminal's screen. A page
  cannot resize its own window (`resizeTo` works only on a popup it opened,
  and popups are blocked on phones and in an installed app), so the sheet
  draws the terminal's proportion INSIDE the window instead: `aspect-ratio:
  4 / 3`, width `min(100%, viewport-height × 4/3)`, centered. Phones keep the
  full-height stacked layout. The frame still grows for a statement longer
  than the space, **and it did not in `g`** (20260930h): `.exam-terminal`
  carries `overflow: hidden` for its rounded corners, which makes the frame a
  scroll container, and CSS Sizing 4 switches off the aspect ratio's
  content-based minimum height on a scroll container. So the sheet stopped
  at 4:3 whatever it held and the chip row was cut off at the bottom on the
  first window it met. `#exam-sheet` now sets `overflow: visible` and the
  three children that touch the corners carry the radius. An `aspect-ratio`
  box that must grow with its content cannot also clip.
- **A tall figure no longer pushes the controls out of the window**
  (20260930s, reported 2026-09-24 as "the bottom got clipped"). Nothing was
  clipped: 4214 and 4292 grew the sheet 300 to 400 px, so the V/F squares and
  the strip sat below the fold. Two changes. At 760 px and up the figure sits
  to the LEFT of the question (`#exam-card.exam-card-fig`), as on the
  Ministry's terminal, so its height no longer adds to the text's. And
  `fitExamImage` caps the figure's height at the room the rest of the sheet
  leaves in the window, on load and on resize, with a floor of 200 px
  (`EXAM_IMG_FLOOR`) and 400 px for the twenty `IMG_DETAILED` boards, which
  at 140 px went to 69 px wide and unreadable. Below the floor the page
  scrolls, deliberately. Measured with Playwright: 4214 fits at 1440x900,
  1280x720 and 390x844; 4292 fits at 1440x900 and scrolls on shorter
  windows; a 1024x600 window still scrolls by about 30 px.
- **Landscape phones (20261006x, reported 2026-10-01).** About 390 px high,
  the 4:3 frame was sized from the height to 285 px wide and the answer
  squares and the strip fell off the screen. A media query `(orientation:
  landscape) and (max-height: 560px)`, last in style.css, makes the sheet
  fill the width and the height below the app bar: the clock and Riepilogo
  in a narrow left column, the question with V and F at its right (V over F
  below 760 px wide), the figure at most 42% of the question area, a compact
  strip at the bottom. `fitExamImage` lets the figure's floor drop to 36% of
  the window height below 560 px. During a mock the whole `.exam-header` is
  hidden, not just its heading. `scripts/check_exam_landscape.js`
  (Playwright, `CHROME=` a Chromium binary) loads the longest statement and
  the busiest board at 667x375, 844x390, 932x430, 390x844 and 1280x800 and
  fails on any page scroll, except a detailed board in a tall window, whose
  400 px floor scrolls by design; the previous build fails 6 of 10.
  **Short portrait screens followed the same day (20261006y)**: the
  reporting iPhone used Display Zoom, which makes the viewport 320 px
  wide and about 693 high (text a quarter larger than in a 390-px test),
  and the figure's 200 px floor pushed V/F off the screen. A query
  `(orientation: portrait) and (max-height: 760px) and (max-width: 759px)`
  draws the stacked sheet smaller, the floor drops to 22% of the height
  below 760 px, and `body.exam-locked` drops the page's 2 rem bottom padding
  to the safe-area inset (that padding alone made a fitting sheet scroll
  30 px). The check now also runs 320x650, 320x693 and 375x667; its
  detailed-board exemption applies only at 760 px and taller, and nothing
  currently needs it. The previous build fails 6 of 16.
- **No screen may be wider than a narrow phone (20261006z, reported
  2026-10-01 under iOS Display Zoom, 320 px wide).** Four rows could not
  wrap and widened the page: the readiness ring with its three notes
  (Statistics), each vocabulary row (word column of 8 rem, an unbreakable
  gloss, count, +/-), the How-to's six-column time table, and a Settings
  row with its select. At 560 px and below the notes go under the ring; at
  440 px and below a vocabulary row puts its gloss on its own line, the
  table is drawn tighter, and the Settings text column may shrink.
  `scripts/check_narrow.js` (Playwright) visits the dashboard with its
  panels open, Statistics, every Reference tab, a study card, the notes and
  Settings at 320x693 and 375x667 and fails on any sideways scroll;
  `EXPORT=` a .patente file fills the lists like a real learner's (the
  vocabulary overflow needed a full study list). The previous build fails 8.
- **Mock timings (20261007d, maintainer, 2026-10-01).** `examState.dwell`
  holds the milliseconds each statement is on screen, summed over visits
  (`examDwellStart` in `goExamStatement`, `examDwellStop` on the Riepilogo,
  on `visibilitychange` to hidden and at finish), so time away from the app
  and time on the Riepilogo are not charged to a statement. `finishExam`
  takes the seconds used from the fixed end time and saves `time` on the
  result and `s` per item. The result shows "Time used: m:ss of 20:00,
  about N seconds per question" (or that time ran out; `#exam-time-used`,
  built when a stale page lacks it); Past Results has a Time column, a dash
  for mocks saved before; the review shows each statement's seconds and
  marks the three slowest. The time used counts time away, since the clock
  cannot be paused; the per-question times do not.
  `scripts/check_exam_timing.js`, 9 checks in each face, with a controlled
  clock.
- **`total` is now always thirty**, and an unanswered statement is a wrong
  one, in the stored record as in the room. Before this `total` was the
  count ANSWERED, which is why `sheetWrong` exists; it still corrects records
  of the old shape and agrees with the new ones. Closing with blanks asks
  once, naming the count.
- **A chip and the Riepilogo show WHETHER a statement has an answer, never
  which or whether it is right.** `aria-pressed` on the V/F pair is the whole
  state; there is no `.right`/`.wrong` anywhere on the sheet, and the harness
  asserts it.
- **`scripts/check_exam_sheet.js`, 30 checks in each language face**
  (`UILANG=it-IT`): the empty sheet, answering without advancing, changing an
  answer, the chips, both arrows, a jump from a chip, the Riepilogo with one
  blank, returning from a row, the confirm on close, the stored 27/30 with the
  blank counted wrong, `sheetWrong` agreeing, and a clean second sheet. The
  second-sheet check is the one that bit: `startExam` has to put the sheet
  back when the previous one ended on its Riepilogo, which is why it calls
  `goExamStatement(0)` and not `renderExamCard()`.

## After a mock exam (the score is ON the page, not instead of it)

- **A finished mock shows its score at the top of the Final Stretch page, with
  the page still under it** (`showResultOnFinalStretch`, 2026-09-21). It used
  to REPLACE the page: `#exam-results` showed while `#exam-start` (the drill,
  the mock panel, the weak spots, the past results) stayed hidden, so the only
  way out was a button labelled **New Exam** that started no exam and merely
  put the page back. The maintainer reported it, and it was wrong twice over: a
  learner who has just sat a mock wants the weak spots that mock just fed, and
  a control has to be named for what it does.
- **The button is gone, not renamed.** `Start Exam` in the mock panel is now
  directly below the score, so a second control for the same thing would be
  two buttons with different words for one action. `exam.new` and the
  `#btn-new-exam` tooltip went with it.
- **The result block is MOVED in front of `#exam-start` in JS**, not only in
  index.html, because index.html is cached separately from app.js: on a stale
  page the markup order would print the score below the drill, where nobody
  would see it. The move is idempotent and `#btn-new-exam` is removed at the
  same moment, so a stale page cannot show it either.
- **`updateExamAvailability()` is the page's one render entry point**, and the
  result path calls it: the mock's misses are written by `recordExamMisses`
  just before, so the drill's effort line, the weak spots, the readiness ring
  and the history are all one exam stale until it runs.
- **Arriving at the screen clears the last score** (`clearExamResultPanel`, in
  the nav handler). Without it, leaving the page and coming back greeted the
  learner with the score of an exam they had already read.
- **Review Answers SHOWS the English, with no pill to press** (2026-09-21,
  `buildExamReviewHtml`). A mock runs only at `EXAM_LEVEL`, which is Solo
  italiano, so an EN pill there was not an edge case: it was every mock review
  an English speaker ever opened, thirty taps to read one sheet back. The
  Italian statement and the Italian explanation stay, and underneath them a
  non-Italian browser now gets the translation and the English explanation,
  open. An Italian browser sees neither, there being nothing to translate.
  Two reasons this is not the forbidden kind of reveal. The answers are
  ALREADY on the page, so nothing here can leak one; and it is the rule
  already recorded for a wrong answer at Solo italiano (`enOnWrong`), where
  the maintainer asked for the translations without a control. `.exam-rev-enbtn`
  and `.exam-rev-enblock` are gone, along with the click branch that toggled
  them; the `.exam-rev-revbtn` link into the notes stays, since that is the
  row's real remedy. Both entry points share this function, the live review
  and the past-results panel, so the change reaches both.
- **Verified in jsdom**, `/tmp/exam_dom.js`, 21 checks plus 7 on the review's
  English, run in BOTH language faces (`UILANG=it-IT node exam_dom.js`): a
  whole mock answered through to the end, the page under the score, no New
  Exam button, the DOM order, the scroll to the top, Review Answers opening
  and closing in place, the history carrying the exam just taken, a clean
  second visit and a clean second exam, then no pill and no hidden block, one
  Italian explanation per row, and the two English blocks present on every row
  for an English browser and on none for an Italian one. One trap: the answer
  buttons are built inside `#exam-card` by `renderExamCard`, not in
  `#exam-answer-btns`, and `handleExamAnswer` waits 400 ms before the next
  question, so a loop that taps faster than that answers one question and
  stops. A second: `navigator.language` must be defined on the window BEFORE
  app.js is appended, or the Italian pass runs the English face.

## "Answer again" (undoing a mistapped answer)

- **What it undoes.** `handleAnswer` takes `snapshotBeforeAnswer` at the top,
  a deep copy of the statement's record at EVERY level from 1 to the current
  one, because a correct answer lifts credit downward and the undo has to take
  that back too. `undoAnswer` restores those records exactly (plus the `und`
  stamp described below) and SUBTRACTS this answer's contribution from the
  daily log and the session counters rather than restoring their old values,
  so an answer given after it keeps its own.
- **It is SESSION-SCOPED, and that is not a shortcut.** The state before an
  answer given yesterday is gone: nothing records the streak it replaced. So
  the ↺ appears only on a statement answered since the app was opened, which
  is also the only case that can be a mistap.
- **The sync merge broke it in BOTH directions, and one bug hid the other
  (fixed 20260927c).** The report was that pressing "Erase and answer again"
  returned to the card with the wrong answer still marked (2026-09-20).
  - FORWARD: a merge could have rewritten the record a snapshot restores, so
    `mergeProgressData` dropped EVERY snapshot. `saveProgress()` marks the
    state dirty and the sync tick fires about **thirty seconds** later
    (`SYNC_DIRTY_MS`), which is how long it takes to read the explanation, so
    the ↺ died half a minute after the answer, on every device with sync on.
    The button stayed on screen and `undoAnswer` returned false in silence.
    Only a snapshot whose record the merge ACTUALLY changed is dropped now:
    `undoFingerprints()` before the merge, `dropStaleUndoSnapshots()` after
    `propagateLevelCredit`, comparing every level the snapshot covers. The
    blanket clear in `afterSyncRefresh` is gone; `forgetUndoSnapshots()` now
    belongs to `setLevel` alone, which swaps the whole progress map.
  - BACKWARD: the same sync PUSHES the mistaken answer, and `mergeCardRecord`
    maxes `seen`, `correct` and `miss`, so the next pull handed it straight
    back. `und` is the per-statement tombstone this file said was missing: the
    undo stamps the restored record with the moment of the rollback, and
    `undoneCopy` treats a copy that knows nothing of it (`und` older) and
    whose own `gAt`/`sAt` both predate it as the erased answer rather than as
    evidence, taking the other side's values wholesale. At most one side can
    be stale, so the merge stays commutative. A device that answers the
    statement again stamps `gAt` past `und` and merges normally, which is why
    `und` is NEVER deleted the way `lft` is: it suppresses one specific
    answer, not a statement, and deleting it would let the phantom miss back
    in on the next pull.
  - The tombstone has to live somewhere, so an undo that used to DELETE the
    record (the answer created it) now writes `{seen:0, correct:0, streak:0,
    und}` instead, which is `stmtRecord`'s own shape. A level the answer never
    reached keeps nothing: a wrong answer lifts no credit, so the levels below
    are left exactly as they were rather than gaining an empty card.
- **A dead ↺ now says so.** `addUndoControl` runs when the answer is given and
  nothing takes the button away, so a snapshot dropped in between left a
  control that did nothing at all when pressed, which is what made this hard to
  report. `undoAnswer` returning false shows `undo.gone` and re-renders, which
  also removes the button.
- **Verified in jsdom**, `/tmp/undo_dom.js` in that session, 18 checks: the
  tombstone in both merge directions and its commutativity, an ordinary merge
  unchanged, an unstamped legacy record still counting, the snapshot surviving
  an unrelated merge and dying on a relevant one, the undo itself, no phantom
  records at the levels below, and the message on a snapshot that really is
  gone. Note the harness trap for this file: app.js opens with `'use strict'`,
  so its top-level `let`/`const` (`questions`, `session`, `progress`,
  `currentLevel`) live in the global LEXICAL environment and are NOT on
  `window`; read them with `window.eval('questions')`. Function declarations
  are on `window` as usual.
- **The run is restored only when the undone answer was the LATEST one**
  (`snap.seq === _answerSeq`). It is a position in a sequence, not a total, and
  lowering it after later answers would cost the learner a streak they are
  still on. `bestRun` and the day's `r` are high-water marks and are left
  alone.
- **The button lives on the NUMBER line** (`.stmt-head-aids`), with the 📖 and
  the IT pill, never in the answer row: that row is kept to three controls for
  the anti-mistap gap, which is the very thing this feature exists to forgive.
- **`addUndoControl` is called from TWO places and needs both.**
  `showStatementAnswered` covers a card re-rendered with answers already
  given, but on a FRESH answer that function runs before the snapshot is
  stored, since the snapshot is taken last so its counter diffs catch
  everything the answer moved. So `handleAnswer` adds the button itself
  afterwards. Calling it only from the render is what shipped in 20260925u's
  predecessor, where the ↺ appeared on nothing until the card was left and
  reopened, and the maintainer reported it the same day. A control whose
  condition is written by the same function that renders it: check the ORDER
  of the two, not just the condition.
- **The dialog puts "Keep my answer" first**, as the primary button, so the
  erase is never the control under the thumb.
- **It carries the 📖's weight, and a quieter first attempt is what "I don't
  see it" meant.** The ↺ shipped as a muted glyph at .55 opacity, on the
  reasoning that a rescue control should not compete with a study aid. It was
  reported missing twice. The second report was investigated by driving the
  LIVE site rather than reasoning about the code: the button was in the DOM,
  42x36, visible, on every answer right and wrong, on the last statement of a
  card as well as the first. It was simply a thin outline glyph next to a
  full-color 📖, which reads as empty space. A control nobody can find is
  worth what one that was never added is worth.
- **Reach for the deployed site when a UI report will not reproduce.**
  `patente.physyapps.com` is public, so the browser tools can load it, call
  `startStudySession(...)`, click a V/F button and read the DOM back. That
  turned a second round of guesses (stale build? detached `li`? a re-render
  eating the node?) into a measurement in three calls, and it also reads
  `APP_VERSION` off the served file, which settles "is the fix even up there"
  without asking. A fake-DOM harness had already passed on the same code: it
  proves the node is created, and says nothing about whether a person can see
  it.

## The export file's name (20261009c)

- `exportProgress` names the file `patente-progress-YYYY-MM-DD-HHMMSS.patente`
  in local time (`exportStamp`), at the maintainer's request of 2026-10-02:
  the name carried the date only, so a second export the same day collided
  with the first. The `exportedAt` field inside the file is unchanged.

## Settings sync

- **Every preference syncs. The THEME is the only exception.** Agreed long ago
  and restated on 2026-09-17, when six Settings rows turned out never to have
  been added: the answer tone, vibration, the silent-switch option, the
  explanation after a correct answer, the mock exam mix and the speech rate,
  plus the language the dialog is read in. The ACTIVE LEVEL joined them the
  same day.
- **The level travels in `settings`, not in the bundle's top-level `level`.**
  That top-level field is the EXPORT field, and `mergeProgressData` applies it
  unconditionally, which is right for a file the person chose to import. Sync
  still deletes it on pull (`delete remote.level`) because it carries no
  timestamp: with two devices, each pull would apply whichever copy reached the
  server last rather than the choice made most recently. Inside `settings` it
  obeys the same stamp as everything else. `setLevel` therefore calls
  `stampSettings()`.
- **The live switch waits for a safe moment.** Changing level swaps the whole
  progress map, and a sync runs on launch AND on backgrounding, so a pull could
  otherwise change the level under someone mid-card. `midActivity()` is true on
  the study screen and during a mock, and while it is, the merge records the
  new level for the next launch instead of applying it. The choice is never
  lost, only deferred.
- **Adding a Settings row means editing THREE places.** `buildProgressBundle`
  (collect), `mergeSyncSettings` (apply), and the setter, which must call
  `stampSettings()`. The stamp is the one that gets forgotten and the one with
  no symptom of its own: without it the key rides in the bundle and still loses
  every last-write-wins merge, so the preference silently never travels. None
  of the six missing setters had it.
- **Guard each key with `!== undefined` in the merge.** A bundle written before
  the key existed carries no value for it, and a plain `set()` would read that
  absence as "off" and wipe a choice the other device never spoke about.
- **The merge must repeat the setter's SIDE EFFECTS, not just its write.**
  Being told the silent-switch option is on is not the same as asking the
  platform for the audio session, so `mergeSyncSettings` calls
  `applyAudioSession()`; it calls `paintSettingsLang()` for the same reason.
  `afterSyncRefresh` then calls `syncSettings()`, which repaints the controls,
  so an open dialog shows what arrived.
- **Two devices disagreeing is how a missing key gets reported**, and it never
  looks like a sync bug. Auto-scroll sat off on an iPad and on on a Mac, and
  since that switch also gates the arrival placement, it was reported as Resume
  being broken and cost two releases in the wrong function. When a feature
  works on one device and not another, compare the SETTINGS before the code.

## What sync COSTS (the conditional pull, added 20260928a)

- **The blob is the whole bundle, and it used to be downloaded on every tick.**
  `syncNow` pulls, merges and pushes, and before 2026-09-21 both halves were
  unconditional. Measured on one real session from the server's own access log:
  **126 GETs and 123 POSTs in 97 minutes**, a cycle roughly every 45 seconds,
  **32.4 MB pulled down** by a single device, and every one of those pulls
  returned the copy that same device had just uploaded. The uploads cost the
  same again on the learner's data, which the server log cannot see.
- **The pull is now conditional on an ETag.** `sync.php` stores `etag`, a hash
  of the ciphertext, when it writes a bucket; the GET sends it and honours
  `If-None-Match` with a bodiless **304**. The client keeps the etag of the
  blob it last merged in `patente_sync_etag`, **keyed by bucket**, since
  changing the sync code changes the bucket and an etag from the old one means
  nothing.
- **The POST returns the new etag, and that is what makes the scheme pay.**
  Without it the pushing device would know the remote had changed (it had, to
  its own copy) and would pull it straight back. `setSyncEtag` is therefore
  called on the push path as well as the pull path; the harness proves it by
  sabotage, and dropping it costs five checks.
- **A cycle with nothing to do now does nothing.** The push is skipped when all
  three hold: the pull was a 304, `_syncDirty` was false when the cycle STARTED,
  and the merge changed nothing. `wasDirty` is read before the round trip on
  purpose, because work done while the request is in flight belongs to the next
  push. This is what the five-minute idle poll is for, which used to upload the
  entire bundle simply to confirm it had not changed.
- **304 is not `ok`.** `resp.ok` is false for it, so the `else if (resp.status
  !== 404)` server-error branch had to learn about it too, or every quiet cycle
  would have reported a server failure.
- **`SYNC_DIRTY_MS` went from 30 seconds to 3 minutes.** The push carries the
  whole bundle and an hour of study differed from the previous upload by a
  handful of records. The only cost of waiting is how stale the OTHER device
  looks, and a device being LEFT already syncs at once through
  `visibilitychange`, `pagehide` and `online`. So the 30-second timer was
  paying its full price in exactly the case where it bought nothing, which is
  one person studying on one device.
- **An old server still works.** A `sync.php` that returns no `etag` simply
  never produces a 304, and the client falls back to the old full-pull
  behaviour. The harness runs that case, because the data files and `sync.php`
  reach the server at different moments.
- **Verified in jsdom**, `/tmp/sync_dom.js`, 22 checks: a faithful model of
  `sync.php` including the 304, then the first cycle on an empty bucket, a
  quiet cycle that makes one request and no upload, a dirty cycle that 304s and
  still pushes, another device's write pulling in full and merging, the cycle
  after it going quiet again, a changed sync code refusing to reuse the old
  etag, and the etag-less server. Two traps. The code lives under
  `patente_sync_code`, not `patente_sync`. And jsdom's `window.crypto` has no
  `subtle`, so it must be replaced with `require('crypto').webcrypto` through
  `Object.defineProperty`, since a plain assignment does not take.
- **Read the access log before optimising anything here.** None of this was
  visible from the code, which looks perfectly reasonable; it took counting
  `sync.php` requests in `patente.physyapps.com-ssl_log` to see that a single
  device had spent an hour and a half re-downloading itself.

## Loading the data files (the ten-fetch cold start, fixed 20260928f)

- **Two real visitors downloaded `questions.json` ELEVEN and TEN times on their
  first load**, 12.1 MB and 10.4 MB on a phone, before the app drew anything
  (access log, 2026-09-22). The first response in each case was TRUNCATED,
  786,072 and 524,072 bytes against the full 1,018,522, which is a mobile
  connection dropping it. Everything after that was the app's own doing. The
  counts read "ten and ten" here until the visitors were identified by IP on
  2026-09-22: one visitor at 06:07 made eleven, another at 06:31 made
  ten. The arithmetic below predicts ten, so one fetch is still unaccounted
  for; do not read the model as complete.
- **Neither of them got past it.** Both left within eight seconds and neither
  made a single `sync.php` call, so both saw "Couldn't load the questions" and
  nothing else. They were two of the FIVE real people who had reached the app
  at that point, so this bug was turning away 40% of the audience.
- **The ten was an exact product, not a coincidence.** `boot()` retried
  `loadQuestions()` four times while `questions.length` was zero, and
  `loadDataFile` itself fetches TWICE on a parse failure, one plus four calls
  at two fetches each. The harness reproduces exactly 10 with the old loop
  restored, which is what turned this from a theory into a finding.
- **A retry that does not know what the layer beneath it already tried is a
  multiplier, not a safety net.** The budget is now on FETCHES, counted inside
  `loadDataFile` (`_dataFileTries`, per file, per page), so the loop cannot
  silently become ten again by someone changing either layer. Four fetches
  total, with the wait doubling. Measured: all responses bad costs 4, one bad
  then good costs 2 and loads all 849 cards, a clean load costs 1.
- **The worker held THREE live copies of a 5.5 MB file.** The old data-file
  handler read a clone to prove the JSON parsed, cloned AGAIN for the cache,
  and handed the original to the page. Measured in node at the moment all three
  are live: **+14.8 MB of heap**, inside a service worker, on a phone. It now
  does `cache.put(req, resp)`, which consumes the response outright, and serves
  the page the copy read back out of the cache: one body, measured at +0.0 MB.
  A model of both shapes confirms the page receives identical data.
- **`isWholeJson` is GONE from the fetch handler and that is deliberate.**
  `loadDataFile` already parses what it gets, deletes the cache entry and
  refetches when it will not parse, which is the same un-sticking the check was
  written to provide. Two layers were doing one job and the expensive one sat
  on the device with the least memory. The INSTALL step keeps its own check,
  where nothing has to be handed on and the cost is one extra copy rather than
  two.
- **The server log cannot see a client-side failure.** It recorded 1,018,522
  bytes SENT nine times over, all complete; the failures were all on the phone.
  Read "bytes sent" as what left the server and nothing more.
- **Verified in jsdom**, `/tmp/dataload_dom.js`, 6 checks over three seeded
  worlds: every response truncated, only the first truncated, and nothing
  wrong. It counts FETCHES rather than calls, because counting calls is exactly
  the mistake the old loop made. Proved to bite by restoring the old loop,
  which prints 10 and fails the budget check.

## Scrolling (iOS lays out and scrolls asynchronously)

- **Check `autoScrollOn()` BEFORE anything else when a scroll does not happen.**
  It is the first line of `settleOnFirstUnanswered`, and while it is off nothing
  in that function runs, so no fix inside it can have any effect. Two releases
  were spent rewriting code below that line on 2026-09-17 for an iPad where the
  switch was simply off. The screenshot that solved it showed the "N unanswered"
  pill working on the same device, and `jumpToUnansweredStmt` shares
  `cardWorkTarget()` with the settle and has no such gate: one path working and
  the other not, on the same target, points straight at what differs between
  them. Read the whole function before rewriting part of it.
- **The switch is synced, since 2026-09-17.** It sat off on one device and on on
  another, and because it also gates the arrival placement, Resume looked broken
  on the device where it was off. `setAutoScrollOn` now calls `stampSettings()`,
  without which a change could never win a merge or leave the device at all.
  `mergeSyncSettings` guards it with `!== undefined`, so a bundle written before
  the key existed leaves the local choice alone instead of reading a missing
  value as "off".
- **It still governs two behaviours and is named for one.** "↓ Scroll on after
  answering" also decides whether arriving at a card places you at your first
  unanswered question, which is what Resume and the Final Stretch level links
  promise. Left as one switch at the maintainer's direction (he asked for
  syncing instead), so anyone turning it off should expect Resume to leave them
  at the top of the card.
- **One `requestAnimationFrame` is not enough on an iPad.** Resume put the
  right card on screen and left the first unanswered question below the fold,
  on iPad only, reported 2026-09-17. `renderStudyCard` does
  `window.scrollTo(0, 0)` and then `settleOnFirstUnanswered` a frame later, and
  on iOS that reset and the relayout of a freshly built card are both still in
  flight when the frame fires, so `scrollIntoView` aims at a stale box and the
  scroll to the top is what survives. A Mac settles inside that one frame,
  which is why it looked fixed.
- **Measure the result and re-apply.** `settleOnFirstUnanswered` now checks how
  far the target is from where it belongs, under the pinned sign for a
  statement or centred for the retry button, and scrolls again until it is
  within 4 px on two consecutive frames. Two frames, because a value read
  mid-layout can be right by accident. It stops on the reader's first touch,
  wheel or key, and it stops unconditionally after 800 ms, so a page that never
  settles cannot spin. A newer card cancels an older settle through
  `_settleToken`, since answering re-renders the card.
- **The same pattern already existed for the review overlay** (`scrollReviewTo`
  pins the final position after Safari cuts a smooth scroll short). When a
  scroll lands wrong on iOS, reach for the settle pattern rather than a longer
  delay: a delay that is long enough on one device is a guess on every other.

## Speech (the 🔊 buttons)

- **iOS silences a web page's audio with the side switch**, because Safari puts
  the page in the AMBIENT audio session category. Speech used to be exempt, so
  the app read statements aloud for months with the ringer off and then stopped
  after an OS update (reported 2026-09-17). Nothing in the app had changed.
- **The Settings switch frees the ANSWER TONE, and it is the USER's to throw.**
  "Play the answer tone even when the phone is silenced" sets
  `navigator.audioSession.type` (Safari 16.4+); off restores `'auto'`. Confirmed
  working 2026-09-17: tone audible on a silenced phone, speech not. Someone who
  silenced their phone meant it, so the app does not decide this for them. The
  first attempt at the fix set `'playback'` from inside the speech path, which
  overruled a maintainer who had left that switch off and did it with the one
  type that stops their music. It was committed and reverted the same day.
- **Our own `Permissions-Policy` header was blocking the API.** WebKit gates
  `navigator.audioSession` on the MICROPHONE feature (`DOMAudioSession::setType`
  returns early when it is disallowed) and refuses SILENTLY: the assignment does
  nothing and the getter keeps answering `'auto'`. `.htaccess` sent
  `microphone=()`, correctly for an app that never records, so the setting could
  not work whatever the app set it to. It is now `microphone=(self)`, which only
  lets same-origin code ASK (the browser still prompts), and no code here asks.
  Do not tighten it back while that Settings option exists. The general lesson:
  **read the value back**. Three fixes were shipped on assignments nobody
  verified; `audioSessionReport()` now compares asked-for against actual and the
  self-test prints `REFUSED` with the cause.
- **Only `'playback'` survives the side switch.** WebKit's
  `fromDOMAudioSessionType` (`Source/WebCore/Modules/audiosession/DOMAudioSession.cpp`)
  maps `transient` AND `ambient` to `AVAudioSessionCategoryAmbient`, and
  `transient-solo` to `SoloAmbient`; all three are silenced. The setting shipped
  with `'transient'`, chosen from the spec's prose about notification pings, so
  it never did what it promised. The spec's descriptions are about MIXING, not
  about the switch: check that function before picking a type.
  `'playback'` is exclusive, so it pauses the person's music while the app is
  making a sound. `ttsHush` hands the category back when the app is
  backgrounded and `applyAudioSession` re-takes it on return, so leaving the
  app gives them their audio immediately.
- **The setting row stays disabled when the answer tone is off**, because the
  tone is the only thing it governs. That gate was removed for one day on the
  belief that it also freed the 🔊 buttons, which left a control that could be
  switched on to no effect whatever. When a belief about scope turns out to be
  wrong, hunt down everything that was changed BECAUSE of it; this gate and two
  UI strings all moved on that one wrong idea.
- **Two engine failures look identical and are each other's cure.** WEDGED: the
  engine sits at `speaking === true` with nothing playing and a later `speak()`
  queues behind a ghost forever; only `cancel()` clears it. SWALLOWED: a
  `speak()` issued straight after a `cancel()` is sometimes dropped by WebKit;
  only a retry clears that. Guarding either one re-opens the other, so
  `ttsSpeak` does both every time, and `speak()` stays SYNCHRONOUS inside the
  click because iOS requires the user gesture.
- **The self-test used to break its own second stage.** It spoke a direct
  utterance, then ran the button path on a fixed 3-second timer, and
  `speakItalian` opens with `cancel()`, so it killed the utterance it was
  measuring. The box then reported `error:canceled` and `swallowed after
  cancel, retried` on a phone where everything worked, and never printed its
  verdict. Stage two now waits for stage one to fall silent, with a 12-second
  cap that says so. A diagnostic that manufactures the fault it is looking for
  costs more than no diagnostic: read its output as evidence only after
  checking that the instrument is not the cause.
- **SPEECH IS NOT IN THE AUDIO SESSION, so no page can play it through the
  side switch.** This is the answer, established 2026-09-17 by the one
  experiment worth running: ringer on, everything audible; ringer off, silence,
  with the setting ON and the session reading `playback`. WebKit's
  `PlatformSpeechSynthesizerCocoa.mm` creates a bare `AVSpeechSynthesizer` and
  calls `speakUtterance:`; it never touches `AudioSession`, never sets a
  category, never registers with the media session manager. The W3C spec's
  integration section lists exactly three session elements, `AudioContext`,
  `HTMLMediaElement` and a microphone track, and speech is not one of them. So
  `navigator.audioSession.type` governs the ANSWER TONE and nothing else, and
  the Settings option must never again be worded as though it covers the 🔊
  buttons. It was, for one day, and that promise is the reason this went four
  more rounds.
- **What actually changed in the OS** is `AVSpeechSynthesizer`'s own default
  session, which is Apple's to choose and invisible to us. Speech was exempt
  from the switch for years and now is not. There is no web API that reaches
  it, so the only route to audible speech on a silenced phone is to stop using
  `speechSynthesis` and play PRE-RENDERED audio through an element the session
  does govern. The maintainer's `italiano` repo already has that pipeline
  (macOS `say` plus ffmpeg, deterministic voice per key, per-section offline
  caching). **SHELVED 2026-09-17**, on size: 7,106 live statements, 724,457
  characters of Italian, about 14.4 hours of speech, which is roughly 99 MB at
  16 kbps mono, 148 MB at 24 and 197 MB at 32. Measure before reopening, since
  those are the numbers the decision turns on, and consider the partial
  versions first: the abridged set only, or one topic at a time downloaded on
  demand the way `italiano` does it by section. Nothing is to be built here
  without agreeing the size question first.
- **Two theories were wrong on the way, and both looked strong.** The side
  switch being merely misconfigured (it was not: the app should have worked and
  the maintainer said so). And the iOS 26/27 fault where audio dies in an
  INSTALLED web app while Safari still speaks: real, widely reported, matched
  the symptoms, and was disproved in one line by "unsilence the phone and it
  plays". A theory that explains the evidence is not the same as the cause. Ask
  for the experiment that SPLITS the theories, which here was one switch.
- **Diagnose before patching.** Settings has a self-test that prints the build,
  a timestamped trail of what the real speaker buttons did, the voices, the
  audio session category and whether the setting above is on, and the utterance
  events. Four releases were spent patching the speech engine on this bug
  before the trail showed `started ... finished` on a real tap, which proved
  the app was fine and the sound was simply inaudible. If a speech report
  arrives, this is the box to reach for. Since 2026-09-17 it has NO way in
  from the interface (`#selftest-wrap`, hidden): call **`patenteSelfTest()`**
  from a console, which reveals it in Settings and runs it. Safari's Web
  Inspector reaches an installed app on a phone or iPad over the cable. It
  carries the scroll trail too, the second debug button having been removed, so
  one box answers both a sound report and a placement one. Speech may report
  nothing when started from a console, since iOS wants a gesture to speak;
  press the button in the box for that stage.
- **A diagnostic has no user-facing door at all.** This took four placements to
  get right on 2026-09-17, and the reasoning failed the same way each time, by
  asking who *deserves* to see it instead of whether anyone should. It shipped
  plainly visible under the reading-speed control (a learner adjusting the
  speed met it, and the second debug button beside it printed its own
  translation key in English). Then it was tied to reviewer mode, which the
  maintainer rejected in one line: they are content reviewers, not code
  debuggers, and reviewer mode gates CONTENT tools and nothing else. Then a
  five-tap gesture on the version line, which he rejected too, correctly: a
  hidden door is still a door, and the people who can use this can also open a
  console. Ship the CODE, not the entry point.
- **Before adding a control, grep for the one that exists.** This whole episode
  ran past a shipped, documented setting for the exact problem. The question
  "don't we already have a setting for this?" came from the maintainer, not
  from me, and it should have been the first thing checked.

## The answer tone (Web Audio, and it fails differently from speech)

- **A tone is scheduled at `ctx.currentTime`, and that clock stands still while
  the context does.** Anything scheduled against a stopped context is discarded
  with nothing thrown, nothing logged and no failed promise, which is why a
  silent tone produces no evidence at all unless the code goes looking.
- **WebKit has a fourth context state the spec does not list, `'interrupted'`,**
  entered when the system takes the audio device away. `answerAudioCtx` resumed
  only from `'suspended'`, so a context that reached `'interrupted'` stayed
  there for the life of the page and every later tone was dropped. It now
  resumes from any state that is not `'running'`.
- **`resume()` is a PROMISE, so asking for it and scheduling in the same breath
  still drops the tone that asked.** `whenAudioRuns` plays in the callback.
  Skipping this leaves "the first answer after coming back is silent", which
  nobody reports because it reads as a missed tap.
- **Quit-and-relaunch restoring the sound is the signature of this whole
  family**, and it is worth asking for: it says the context is healthy when
  created and enters a state it never leaves, which rules out the setting, the
  volume and the side switch in one question (macOS, 2026-09-17).
- **Every write to `navigator.audioSession.type` reconfigures the system audio
  session and can interrupt a live context, so only write when it changes
  something.** `hush` used to hand the category back on every background even
  when the app had never taken it, giving two needless reconfigurations per
  round trip out of the app; it now checks `ignoreSilentOn()` first.
- **On a Mac the trigger is not the side switch, it is leaving and returning.**
  Same code, different event. A fix aimed only at silenced phones would have
  missed it, and the two devices that failed were the two the maintainer
  backgrounds constantly.
- **An OS update is a plausible cause and still deserves the diff.** The report
  was "this started after macOS 27 and iOS 27 last night", which was true and
  was not the whole story: the audio-session code had been INERT on every
  device until our own `Permissions-Policy` header was fixed that same day, so
  the Mac was running that path for the first time. When a platform change and
  our own changes land together, read the diff before accepting either.

## UI prose

- **Terse and declarative, never conversational.** The reviewer's standing
  complaint about this app's screens is verbosity, raised again on 2026-09-17
  about the Final Stretch page. Give the reader the verdict and the numbers and
  stop. Cut the sentence that explains why a page exists, the reassurance
  ("Nothing here is locked"), the comparison to the real thing ("just like the
  real exam"), and the second sentence that restates the first. The Final
  Stretch note went from 85 words to 21 and lost no fact.
- **Terse is not the same as compressed.** The same block first read "Missed
  in English too / The rule, not the language." Every word was doing work and
  it was still too compressed: the heading leaned on the reader remembering
  that the section was about Italian misses, and the sub-line hinted at an
  inference instead of stating it. The maintainer replaced both with the
  reasoning spelled out ("Missed in English and Italian" / "Likely the driving
  rules that need review, not your Italian"), which is longer and better. The
  verbosity rule above bans words that carry NOTHING: the reassurance, the
  restatement, the explanation of why a page exists. It does not license
  telegraphing a conclusion the reader then has to reconstruct. When the extra
  words ARE the inference, spend them.
- **Write for the LEARNER, never for the person who watched you build it.**
  Caught on 2026-09-19: a statistics block shipped with "Where they cluster"
  under a list of topics. That phrase names the operation the code performed;
  it tells a learner nothing to do and nothing to think. The same review found
  "Too few answers to say where yet" and "Counted even where you have since
  answered correctly", both of which explain a METHOD decision rather than
  telling the reader about their own work. The failure mode is specific to an
  agent that has just done the analysis, because the analyst's vocabulary is
  the freshest thing in its head: cluster, base rate, denominator, sample,
  signal. Read every string back as somebody who has never seen the work, and
  ask what it asks them to DO or to KNOW. If the answer is "appreciate how the
  number was computed", rewrite it. A second instance the next day, in the
  drill: "Missed on the Italian before. Read it carefully." The maintainer had
  to ask what it meant. It named the CONCLUSION ("the Italian was the problem")
  and never stated the fact underneath it, which is that the learner answered
  that statement right in English and missed it in Italian. A note that reports
  the learner's own history must say what they DID, not what it implies. The
  drill notes now open with the fact, in the same words the Final Stretch
  headings use, so the two screens plainly describe one thing.
- **Name a level the way the level picker names it.** L1/L2/L3 left the UI, and
  the weak-spot text still said "Italiano", which is not a name the learner sees
  anywhere. Pass `t('lvl.N.name')` in rather than writing a level name into a
  sentence, so a rename reaches every string that mentions it.
- **The banner on the Final Stretch page is `renderFinalStretchStatus`.** Ready
  means every card cleared at the Italian-only level, exactly; the maintainer
  set that bar on 2026-09-17 and it is not a percentage near 100. Do not gate
  the page on it: nothing in this app is ever locked, and the drill and the mock
  stay usable whatever the banner says.
- **Invite, do not grade.** The not-ready half was first written as a verdict
  ("Not ready yet.") with the shortfall counted out underneath. The maintainer
  replaced it with an invitation to look around plus a recommendation to come
  back later, and that is the register to keep: this page is reached by choice,
  and a learner who opens it early is curious rather than wrong. The
  percentages below carry the numbers, so do not restate them in the prose.
- **A level with work left is a way back into it.** Its percentage is a button
  that runs `setDrillOpen(false)`, `setLevel(n)`, `resumeStudy()`, which is the
  level picker's action followed by ▶ Resume's, so the shortcut cannot drift
  from either. A level at 100% stays plain text: there is nowhere to send
  anyone. The click handler is delegated and bound ONCE when the element is
  created, because the contents are rewritten on every render and a listener on
  the buttons would leak one per visit.
- **The nav's Begin/Resume button never vanishes while weak spots remain**
  (20261005e, maintainer, 2026-09-29). With every card cleared at the level
  and no drill round open, `resumableTopic()` is null and the button used to
  hide, although the drill was the only work left. It now reads Begin with
  `nav.beginDrillTip` and `resumeStudy` calls `startDrill()`; an open round
  still reads Resume, and a topic with work still outranks a new round. A
  finished drill pass closes its round (`setDrillOpen(false)`), which is the
  moment this case arises. `scripts/check_resume_drill.js`, 10 checks in
  each face; the previous build fails 6.
  **It came and went until 20261005j** (maintainer, 2026-09-30), for two
  reasons. `drillEffort()` is memoized and the memo was cleared only when an
  answer was recorded, so a list read before a sync pull, an import or a
  level switch stayed in force, and a stale EMPTY list hid the button until
  the next answer. And the button was refreshed only when the dashboard
  drew. `updateResumeButton` now clears the memo itself, `setLevel` and
  `afterSyncRefresh` clear it too, and `showScreen` refreshes the button on
  every screen change. `scripts/check_resume_fresh.js`, 3 checks in each
  face; the previous build fails 2.
  **Nav hover is for pointers only (20261005k, maintainer's screenshot,
  2026-09-30).** iOS leaves `:hover` stuck on a tapped element, so after ▶
  was pressed it stayed tinted and outlined through the whole session and
  read as a selected tab. Both `.nav-btn:hover` rules now sit inside
  `@media (hover: hover)`; `.nav-btn.active` is untouched. Measured in
  Playwright: a touch tap leaves the button transparent, a mouse hover
  still tints it, and the previous CSS stays tinted after a tap.
- **The dashboard once every level is cleared (20261006l, maintainer,
  2026-10-01).** When `italianoComplete()` and the Settings row "Show the
  levels and topic progress" (`DASH_FULL_KEY`, default off, synced) is off,
  `renderDashboard` sets `_dashCompact`, puts the level on Italiano, and adds
  `dash-compact` to `#screen-dashboard`. CSS then hides the level buttons
  and `#cards-progress`; the topics render as plain buttons holding only the
  name in the reader's language (`topicShortUi`, 20261006m: English for a
  non-Italian browser even at Italiano), which open the Concepts
  (`.topic-card-concepts`), under a heading
  "Concepts by topic" built in JS (`paintTopicHeading`). A row `#dash-next`,
  built in JS (`ensureDashNext`) and placed before the level selector, holds
  the weak-spots card and a mock exam card (`#dash-mock`, Start goes to the
  Final Stretch screen and starts the sheet). The weak-spots card no longer
  hides when empty once the levels are cleared: it reads "Weak spots: none
  right now" with no button (`.is-empty`), since mock misses refill it. The
  daily block, How-to, flags and footer are unchanged.
  **The mock card can show before the levels are cleared** (20261006n): a
  Settings row "Show the mock exam before the levels are cleared"
  (`MOCK_EARLY_KEY`, default off, synced) adds it alone (`.is-single`).
- **"Questions you keep missing" replaced the diagnosis on the Statistics
  page (20261006p, maintainer, 2026-10-01).** Both groups went, "Missed in
  English and Italian" with its 25-topic breakdown and "Right in English,
  missed in Italian", and with them the stat line. In their place, one list
  (`renderMissBreakdown`, still in `#exam-weak`; `keepMissingRows`) of every
  live statement missed at least N times in total, the three levels added
  (mock misses are recorded at Italiano, and the page says so), most misses
  first, ties in topic order. N is a select on the page ("Missed at least
  [3] times", 1 to 6, `MISS_MIN_KEY`, default 3, synced). A closed row shows
  the figure, the Italian and the misses by level; an Italian browser sees
  the Italiano count only. Opened: the English (non-Italian browser), "Words
  in this question", a Show answer button over the answer and both
  explanations, and the 📖, which opens the notes at that statement's
  landing (`reviewTargetFor`). The answer stays behind the button on
  purpose: the list of 2026-09-30 with answers in front was reverted as a
  list to memorize. **A second select splits the Italian misses by remedy (20261006q,
  reworked in 20261006s at the maintainer's request to offer only what helps
  a learner who must pass in Italian).** Every choice lists questions missed
  at an Italian level (mock exams included), since only those can cost
  points at the exam: "missed in Italian" (default), "right in English,
  missed in Italian" (answered at the English level, never missed there;
  the wording is the likely problem) and "missed in English and Italian"
  (the rule is). A question missed only in English is not listed at all.
  A line under the filter (`km.h.*`) says what to do with the chosen list.
  **A question fixed since its last miss is not listed (20261006t,
  maintainer, 2026-10-01)**: the record keeps a per-level `streak` (correct
  in a row since the last miss) but no full answer history, and the list
  applies the weak spots' own release test, `drillNeed(...) === 0` (two in a
  row, or one at Italiano after a lower-level miss), after the threshold
  and the language filter. The note line counts those left out (`km.fixed`),
  so an empty list after the weak spots are worked through says why rather
  than claiming nothing was missed. It is a RUN, never a rate (maintainer,
  2026-10-01): any wrong answer resets it, a mock miss included
  (`recordExamMisses` sets the Italiano streak to 0), and the question is
  back on the list at once. The run read is the highest level's
  (`governingStreak`), so a later miss at a LOWER level does not reset it;
  after the levels are cleared the app studies at Italiano, where every new
  answer lands.
  **The run is the learner's choice (20261006u, maintainer, 2026-10-01: the
  list should show more than the drill).** A third select, "Leave the list
  after [2 / 3 / 4 / 5 correct in a row at Italiano / the weak spots' rule]"
  (`MISS_RUN_KEY`, default 3, synced). A number reads the Italiano streak
  alone; `ws` is `drillNeed === 0`, which lets one Italiano answer release a
  question missed only lower. Measured on the maintainer's export of
  2026-10-01 at threshold 3: 0 listed under the weak spots' rule, 23 at two
  in a row, 260 at three. Cleared cards are not asked again in study, so the
  run grows only through a mock that draws the question.
  **So every row is answerable (20261006v, maintainer, 2026-10-01).** An
  opened row shows the figure at the study card's own size (the sizing was
  pulled out of `renderStudyCard` into `applyCardImageSize`, and the CSS
  rules for `#card-image-wrap img` also cover `.km-figure img`), then VERO
  and FALSO. Nothing else shows before the answer: the English, the answer
  and both explanations sit in the hidden `.km-ans`, the Show answer button
  is gone. `answerFromList` records a real answer at Italiano whatever level
  is active (seen, correct or miss, streak, `given`, lift, the daily log as
  a drill answer, the drill memo cleared), one answer per opening; the row
  shows the result in place and the list is redrawn on the next visit.
  `MISS_FILTER_KEY`, synced, hidden for an Italian browser; values from
  20261006q/r map across (`both` to `rule`, the rest to the default).
  `scripts/check_keep_missing.js`, 35 checks in the English face, 29 in the
  Italian.
- **A mock exam is a full simulation of the exam room (20261006o,
  maintainer, 2026-10-01).** Start a mock exam opens the sheet BLANK
  (`#exam-in-progress.is-veiled`) under a dialog (`ensureMockIntro`, built
  in JS): 20 minutes, cannot be paused, find a quiet place and silence
  notifications, leaving through the app icon or closing the app loses the
  answers. "Start the exam" starts the clock; "Not now" returns to the main
  page. From the dialog on, `exam-locked` on the body hides every nav
  button, the theme toggle, Settings and the page heading, so nothing can be
  looked up. The app icon is the one way out: during a running sheet it asks
  `mock.abandon` first, and `abandonExam` saves nothing and feeds nothing to
  the weak spots. The clock counts to a fixed `examState.deadline` (iOS
  suspends interval timers, which used to pause a mock when the phone
  locked); `examTick` runs on `visibilitychange`, so a sheet whose time ran
  out while away is closed and scored on return. A desktop browser asks
  before closing (`beforeunload`). `finishExam` now nulls `timerHandle`,
  which had stayed set after a mock and kept `midActivity()` true.
  `scripts/check_mock_intro.js`, 12 checks in each face. **Statistics carries a
  small "Take another mock exam" button under Past Results (20261007h,
  maintainer's request)**, `#btn-stats-mock`, built in `renderExamHistory`,
  beside Clear all results. Both stay directly under the table when a past
  exam is opened, which opens below them (20261007t; `renderExamHistory`
  moves the row on a stale page; `scripts/check_stats_buttons.js`, 4 checks
  in each face, the previous build fails 3); it calls `startMockFromDashboard`, so the same
  dialog and lock apply. The one exception to the page's numbers-only rule.
- **"Final Stretch" is now "Statistics" (📊, *Statistiche*), numbers only
  (20261006n, maintainer, 2026-10-01).** `updateExamAvailability` hides the
  Start button, the drill section and the switch to Italiano at every level,
  shows the past results at every level, and orders the page: the result of
  a mock just taken, readiness and past results, "Cards cleared by level" as
  plain figures (no links, no ready / come-back-later wording), then the
  diagnosis. "Cards cleared by level" is hidden once every level the
  learner has to clear is at 100% (`countedLevels`, 20261008s, maintainer):
  three 100% figures say nothing. `ensureStatsChrome` renames the nav and the heading on a stale
  page. The How-to step on weak spots and mocks, the Ambiguous tab's hint and
  the language-miss sub-line now point to the main page.
  `scripts/check_dash_compact.js`, 29 checks in
  each face, `STALE=1` proves the Settings row builder.
- **The drill has its own progress line (20261005f, maintainer, 2026-09-29).**
  `studyCardCounts` counted every card of the bank when a session had no
  topic, so a drill drew 849 cleared cards and a line that never moved. In
  drill mode it now counts the round's queue, one segment per card, a card
  done once every drill question on it has an answer in this round; both bars
  follow, since both read that function. The label reads `study.drillProgress`,
  cards done this round plus the questions still to clear
  (`drillEffort().questions`), which is the number that falls as statements
  are released across rounds. `scripts/check_drill_progress.js`, 7 checks in
  each face; the previous build fails 5.
- **Home PARKS the drill, it no longer ends it (20261005g, maintainer,
  2026-09-29).** The icon used to call `setDrillOpen(false)`, so with every
  level cleared the drill began again at its first card after every trip
  home. It now sets `_drillParked` (in memory, one page load): the round
  stays open, its answers are kept, and `startDrill` resumes at the first
  unanswered card whichever way it is started. A parked drill yields ▶ Resume
  to a topic that still has work, which keeps the old intent for a learner
  drilling early; with no topic left, Resume goes back into the drill.
  `scripts/check_drill_resume.js`, 9 checks in each face; the previous build
  fails 4.
- **The dashboard's weak-spots card sits ABOVE the level buttons, with an
  even border (20261005i, maintainer, 2026-09-30).** It appears only once
  Italiano is complete, when the drill is the work left, so it leads the
  dashboard. It was below the progress bar with a 4 px accent rule on the
  left only, which read as a lopsided frame; it now has a 2 px
  `--accent-border` all round. `renderWeakSpots` moves the box in front of
  `#level-selector` itself, since a stale cached index.html has the old
  order. `scripts/check_weak_card.js`, 3 checks in each face.
- **In the drill, Next skips cards already answered this round (20261005l,
  maintainer, 2026-09-30).** Next used to step one card, so a resumed round,
  a jump from the menu or answers synced from another device led to a card
  whose questions were already answered. `nextDrillCardIndex` picks the next
  card with a drill question unanswered this round, then any skipped card
  before it; with none, the button reads Finish and closes the pass. Other
  modes still step one card. `scripts/check_drill_next.js`, 3 checks in each
  face; the previous build fails 2.
- **Resume goes back to the drill card that was open (20261005x,
  maintainer, 2026-09-30).** Resume used to call `startDrill()`, which
  rebuilds the round and opens at the FIRST card with an unanswered drill
  question, while the ranking itself shifts as answers come in, so a learner
  who left for the Reference page mid-card was sometimes put on another
  card. `liveDrillSession()` now recognizes the drill still in memory and
  `resumeStudy` re-shows it at `session.index`. Two things leaving the
  study screen undoes have to be put back: `showScreen` sets `_drillStmts`
  to null (so the filter is kept on `session.drillStmts`), and the nav
  restores a lower level for a drill begun there (so Resume switches back
  to `session.level`). A fresh round, or a drill started from the Final
  Stretch page, still opens at the first unanswered card.
  `scripts/check_drill_return.js`, 7 checks in each face; the previous
  build fails 2. `check_drill_resume.js` now expects the Home trip to
  return to the same card too.
- **Correct drill answers count in Today (20261005z, maintainer,
  2026-09-30).** The dashboard's Today number, the dots and the rate count
  statements newly cleared at a level (`m1` to `m3`). A drill statement is
  usually cleared already, so a day of drilling read "Today 0". The daily
  log now keeps `w`, correct answers given in the drill that cleared no
  level, and `dailyProgress` adds it; the sync merge and the undo diff carry
  it like the other fields. Days before this release have no `w` and are
  not back-filled, since `c` minus the clears also holds correct re-answers
  given in topics. The pace therefore rises on drill days, which is the
  same unit the drill's own time estimate divides by.
  `scripts/check_daily_drill.js`, 4 checks in each face; the previous
  build fails 3.
- **Correct mock answers count in Today (20261008d, maintainer,
  2026-10-02: Today read 0 on a day of mocks).** Since 20261008e `x` is
  DERIVED from the mock history rather than counted as a mock ends, so the
  mocks taken before the change count too (the maintainer asked for that
  backfill). `syncMockDaily` sums each local day's correct answers over the
  saved results into ONE shared slot, `dv._mocks`, never a device's own
  share: every device computes the same figure from the same synced
  history, and the merge takes the larger per slot, so two devices cannot
  count one mock twice. The slot only rises, so Clear all results and the
  50-result limit take nothing back. It runs at launch, after `finishExam`
  and at the end of `mergeExamHistory`, and it deletes any `x` that
  20261008d wrote into a device's own share. An abandoned mock is never
  saved, so it adds nothing. `dailyProgress(d)` includes `x`, so the
  ring, the study pill and the 14-day dots show it. The PACE does not:
  `studyRate` and `workLeftAtAnchor` call `dailyProgress(d, false)`,
  because a mock answer clears no level and takes a fraction of a study
  answer's time, so counting it would bring the ready date closer for no
  work toward it. `a` and `c` are untouched, so `rateWindow` does not read a
  mocks-only day as a study day. `scripts/check_daily_mock.js`, 14 checks in
  each face; the previous build fails.
- **The daily log is kept PER DEVICE and summed (20261006a, maintainer,
  2026-09-30: Today did not add up across devices).** `mergeDaily` used to
  take the larger of two devices' totals for each field, so a day split
  between an iPhone and a Mac counted only the bigger half. Each day now
  carries `dv`, one counter set per device (`deviceId()`, a random id in
  `patente_device_id`, never synced as a setting), merged by max per device
  and field, and the top-level `a`, `c`, `m1` to `m3`, `w`, `ms`, `tn` that
  every reader uses are their sum (`dailyTotals`). All writes go through
  `dailyDay` / `dailyBump`; the undo subtracts from this device's share. A
  day written before this keeps its totals as the `_legacy` share, and a
  day arriving from an older build (no `dv`) only raises a floor `fl`, since
  its total may already hold this device's answers. `r`, the best run,
  stays a max. **In the same release the average line stays on screen once
  every level is cleared** (`dailyRateLine`, shown second in the done
  block), at the maintainer's request. `scripts/check_daily_sync.js`, 10
  checks over two jsdom devices; the previous build fails 6.
- **A floating count of the weak spots left (20261005t, maintainer,
  2026-09-30).** In the drill a fixed pill reads "Weak spots left: N"
  ("N left" on a phone) (`updateFloatDrill`, `#float-drill`, `.drill-float`),
  at the TOP LEFT since 20261005u, mirroring the unanswered pill at the top
  right and placed by the same rule (below the jump row while the header is
  on screen), because at the bottom left it covered card text. Checked in
  Playwright at 390 and 1280 px: the two pills sit either side of the sign,
  N being `drillEffort().questions`, the same number as the header label.
  It is built in JS, reports only (no control, `pointer-events: none`),
  and is refreshed with the per-card pill, the header label and every
  screen change, so it hides off the study screen and outside the drill.
  The per-card "N unanswered" pill at the top right is unchanged.
  **Once the header scrolls away it merges into Today's pill (20261006d,
  maintainer's screenshot, 2026-09-30)**: `#float-daily` floats at the top
  left then too, and the two overlapped. While Today's pill shows, the drill
  pill hides and the count rides inside it as `.daily-float-drill`
  ("Today 106 · 190 left", accent color); `updateStudyDailyPill`, which
  rewrites that pill, calls `updateFloatDrill` so the count survives a
  redraw. `scripts/check_drill_float.js`, 10 checks in each face; the
  previous build fails 3. jsdom lays nothing out, so there the header always
  reads as scrolled away; the harness hides Today's pill by hand first.
- **Weak-spot time is charged double (20261005v, maintainer, 2026-09-30).**
  The drill's share of the ready date is `answers × DRILL_TIME_FACTOR (2) ÷
  the learner's per-study-day pace`, since the weak spots are the missed and
  trick statements and take longer to read. The count of answers shown is
  the real one; only the time doubles. **The weak-spots card text is two
  short lines since 20261005w** (maintainer: "this summary needs to be
  concise"): "Mostly {topics}." and "{N} correct answers to clear them,
  about {time}." The round rules and the doubling are not explained there. **The time is
  in minutes or hours while the work fits in a day (20261009d, maintainer,
  2026-10-02)**: three questions read "about one day" when they are six
  minutes' work, because `days` rounds up to whole days of study.
  `drillEffort` now also returns `minutes`, at the learner's own measured
  seconds per question doubled (`drillSecondsPerAnswer`, 20261009e: a flat
  minute lasted one release and he judged it too high; 30 seconds doubled
  stands in when nothing is measured), and `drillSpanWords` says "6 minutes", "25
  minutes", "one hour" or "3 hours" when `days` is 1, and whole days from 2
  up. The card and the dashboard's "What remains is the weak spots" line
  both use it. **Weak spots under two hours add no day of their own to the
  ready date when mock days are already counted (`DRILL_FITS_MIN`,
  20261009f)**; six minutes of them had made a four-day estimate read
  five. The mocks-per-day pace briefly took today's count when it beat the
  earlier days' average; since 20261009r today does NOT count (maintainer:
  "i wouldn't count today"), except when there is no earlier day of mocks. `scripts/check_drill_time.js`,
  6 checks in each face.

## The ready date, and the paperwork that has to come first

- **The date the app computes is not the date the learner may sit the exam.**
  It is when their own study would be finished, and the gap showed on
  2026-09-20: a medical appointment can sit further out than the projected
  date, with the eyesight check still to arrange. The medical certificate has
  to be inside the FILED application before the theory exam can be booked at
  all, and it is valid three months, so the appointments run weeks ahead of the
  date and on somebody else's calendar.
- **That warning lived in the daily block for one day and now lives in the
  How-to** (`daily.paperwork` and `.exam-plan-doc`, both deleted 2026-09-21).
  It was printed as a fourth projection line with every real date. The
  maintainer cut it in one line: the process of getting a license belongs in
  the How-to panel, and the daily block projects a study date. He is right,
  and the reason it was ever written there is the bullet above, which is a
  reason to teach the timing rather than a reason to teach it in that block.
- **STEPS 2 AND 3 CAN COME IN EITHER ORDER, and the panel said otherwise until
  2026-09-21.** A school's actual sequence, as reported to the maintainer:
  the candidate enrolls FIRST, the school then asks for the *certificato
  anamnestico* from the *medico di base*, and only then arranges the
  eyesight visit, at the school. The panel's step 2 ended "You need this
  certificate (under 3 months old) to enroll", which is true for a
  *privatista*, who must file it with the TT2112, and false for the school
  route, where enrolling is what starts the process. Numbered steps imply an
  order, so the intro says the two can swap and points at step 3, which is
  where both routes are described (see the next bullet). The certificate's
  real deadline is unchanged for both: under three months old WHEN THE
  APPLICATION IS FILED. `docs/american-guide.md`'s table row carries the same
  correction.
  Two lessons. A step list is read as a sequence whether or not it is one, so
  a stage whose position depends on the route has to say so. And the
  maintainer is walking this process while the panel describes it, which makes
  him the best source it has: prefer his account of what a school actually did
  over a tidy reading of the rules.
- **STEP 2 NAMES THE TWO VISITS IN THE ORDER THEY HAPPEN**, and it did not
  until the maintainer said so twice on 2026-09-21. The step opened with the
  *medico autorizzato*, because that is the doctor who issues the thing the
  step is named after, and only then said that the *medico di base* writes the
  note "which comes first". He asked why the first visit was mentioned second,
  and added "Make it simple!". It now reads: two visits, and the order
  matters; FIRST your own doctor writes the *certificato anamnestico*; THEN
  you take that note to the Ministry-authorized doctor, who checks fitness and
  eyesight and issues the certificate. The rewrite also cut the step from ten
  sentences to seven.
  The lesson generalises past this panel: **a procedure is written in the
  order the reader will do it**, not in the order of importance. Naming the
  authoritative actor first is the natural instinct and it is wrong for
  anything a reader has to carry out. `/tmp/howto_dom.js` asserts the position
  of *medico di base* is before the authorized doctor's, in both halves, so
  the order cannot silently invert again; proved to bite by swapping them.
- **"Your own doctor (medico di base)", not "your GP".** Corrected in the same
  pass. *GP* is British, and glossary rule 42 says to name the part the way
  the American reader names it and gloss the ITALIAN word, which is what the
  learner will hear at the school.
- **THE ROUTE IS DESCRIBED IN ONE STEP, AND IT IS STEP 3.** Until 2026-09-21
  the autoscuola and the privatista were each named three times over, in the
  intro, in step 2 and again in step 3, which is the step called *Enroll*. The
  maintainer asked "in Step 2 you mention enrolling in a driving school, and
  then in step 3 you mention enrolling in a driving school. Can't we organize
  all this a little better?" So step 2 is now the medical alone and names
  neither route, step 3 opens by saying that the two routes differ in who
  files the paperwork and in WHEN step 2 happens, and the intro says only that
  the two steps can swap and that step 3 describes both. The one fact that
  moved with it is that the school usually arranges the authorized doctor's
  visit on its own premises, which is a property of the route rather than of
  the medical. The harness asserts that step 2 names neither route and that
  step 3 names both, so the duplication cannot come back.
  The general rule: **a fact that depends on a choice belongs in the step
  where the choice is made**, stated once. Repeating it in every step it
  touches is what makes a short list read as a long one.
- **Step 2 also carries the TIMING**: both visits are by appointment, so book
  the first one as soon as you decide to apply; the certificate must be under
  three months old when the application is filed; and no theory exam can be
  booked until the application is in. That last dependency was the one fact
  the panel never stated, being only implied by the step order.
- **"Start early, since both visits are on somebody else's calendar" is the
  kind of sentence this app does not write.** The maintainer cut it on
  2026-09-21 as conversational, and he is right on the UI-prose rule: it is a
  figure of speech standing in for the fact, in the same family as the
  *reader* and *figure* patterns `check_review_english.py` rejects in the
  reviews. Nothing scans the app's own strings, so this is on whoever writes
  the line. The replacement states the fact and the action in one sentence,
  "Both visits are by appointment, so book the first one as soon as you decide
  to apply", and the deadline sentence before it already supplies the reason,
  so no second sentence explains the first.
- **The DATE SENTENCE says what the date is for, and the link is one word
  inside it.** The block said "ready" and never said ready for what; the
  reader supplies "ready for the next step", and which step that is depends on
  where they are. It now reads *"you would be **ready** for the exam around
  Oct 8"*, with that one word opening the How-to at STEP 4. He chose step 4
  over the panel's top. The cost, accepted: step 4 assumes the medical and the
  filing are already done, so a reader who has not started them lands after
  the part they needed, which is what step 2's "start this early" paragraph is
  for. Do not put a process paragraph back into `renderDaily`; add it to the
  How-to and let this link point at it.
- **A separate line explaining the word was the first version and was
  replaced**, both on 2026-09-21. It read *"Ready means ready to take the
  theory exam"* under the dates, and the maintainer's correction is worth
  keeping as a rule: when a sentence can simply SAY the thing, do not write a
  second sentence defining a word in the first. The block is back to three
  lines.
- **The word is `{0}` in all THREE date templates**, `daily.ready`,
  `daily.readyDaily` and `daily.readyRest`, which renumbered every other slot
  in them; "for the exam" stays in the template rather than in the slot, so a
  translator moves it with the sentence. Only ONE of those three is exercised
  by a seeded projection (the others need rest days, or a five-day date past
  the year), so a renumbering mistake in the other two would ship in silence.
  `/tmp/ready_strings.js` substitutes all three directly in both languages and
  checks for a leftover `{n}`, the filled word slot, every date and span
  present, and the phrase following the word; it also checks that
  `daily.readyAfterDay` and `daily.readyFar`, which promise no date, gained no
  slot. Proved to bite by sabotaging one index.
- **With every level cleared, the block STILL gives a date (20261005b,
  maintainer, 2026-09-29).** It used to stop at "Every question is cleared"
  and a line naming the reserve, with no date, which is the moment the date
  matters most. The date is today plus the weak spots at the learner's pace
  (`reserveParts`) plus `MOCK_EXAM_DAYS`, the mock allowance dropping to
  zero once `mockReadiness().ready`; with nothing left the line says the
  recent mocks put the learner at ready now. Both keep the linked "ready".
  `scripts/check_done_date.js`, 6 checks in each face.
- **The count of further mock exams was REMOVED in 20261009w (maintainer,
  2026-10-03), and every later mention of `mockPlan`, `mockReadyAt`,
  `mockNeedAverage`, `trend.effortN` and a mock-phase date in this file
  describes code that no longer exists.** Replayed over his 26 mocks the
  count read 32, 8, never, 27, 23, 7, 15, 1 while the chance of failing fell
  steadily from 8.9% to 5.1%: near the bar it is hypersensitive to the last
  few scores. His rule: what cannot be predicted well is not mentioned, and
  a table of "average X gives N" was rejected as too much. Now: with mocks
  on record and the bar not met, the dashboard's done block gives NO date
  and says to keep taking mock exams until the chance of failing is 5% or
  less (`daily.doneMocksOpen`, `daily.doneLeftOpen`); with no mock on
  record the flat `MOCK_EXAM_DAYS` stands; the trend prints a line only
  once the bar is met; `reserveParts` uses the flat allowance. Do not bring
  a count or a date back without a predictor that is stable on a replay.
  `scripts/check_mock_plan.js`, 9 checks in each face.
- **The mock part of the date comes from the mocks on record (20261008f,
  maintainer, 2026-10-02).** `MOCK_EXAM_DAYS` (3) stands only while no mock
  has been taken. After that `mockPlan()` projects the coming sheets at the
  average of the last five (`MOCK_PLAN_RECENT`), runs the banner's own
  fifteen-sheet prediction after each projected sheet (`mockReadyAt`,
  `mockFormFrom`), and returns how many more are needed for a 95% chance;
  days are that count over the learner's own mocks per day (earlier days
  when there are any, since today is still running; at least one a day).
  The done block says "about N more if they score like your last 5 (28.6
  correct on average), about D days" and dates it; the trend's effort line
  reads "If your next mock exams score like your last 5, an average of 28.6
  correct, about N more would bring the chance of failing to 5% or less"
  (20261009m, maintainer: "at your recent scores" did not say which
  average, and the projection is from the last FIVE, not the overall one).
  **The projection holds the SPREAD too (20261009n, maintainer: "maintaining
  an average says nothing about maintaining a standard deviation").** The
  projected sheets are identical, which alone shrinks the measured spread
  and flatters the learner, so `mockReadyAt` and `mockNeedAverage` keep the
  spread at least at what the learner's own mocks have shown (`mockSpread`,
  passed to `mockFormFrom` as `sMin`), and never below the draw's floor.
  For a steady learner (his own spread, 1.03, is under the floor) nothing
  changes; a scattered learner with the same average now needs many more
  mocks, or a lower average. The sentence states it plainly (20261009o; the
  version naming the average, the five mocks and the spread lasted one
  release and he judged it correct and unreadable): "Keep scoring as you
  have recently, and about N more mock exams will bring your chance of
  failing down to 5%." The maintainer then gave his own wording, adopted
  as written in 20261009p: "At your current pace, you could reach a 5%
  or less chance of failing after another N mock exams." (20261009q, his
  revision of his own wording) The method is recorded here, not on
  the screen. When fifteen projected sheets still fall short, the recent
  scores cannot reach the bar: the block gives the recent average and the
  average needed (about 1.3 wrong) and NO date, the one exception to the
  bullet above. `reserveParts` uses the same days before the levels are
  cleared. On the maintainer's nine mocks of that day (1.4 wrong over the
  last five): 13 more. The projection is at a flat average, so it is
  optimistic about the spread; it uses the prediction's own floor.
  `scripts/check_mock_plan.js`, 12 checks in each face.
- **`lines` in `renderDaily` now holds HTML, not text.** One branch
  interpolates an anchor, so the join at the bottom cannot escape for them and
  EVERY branch escapes its own pieces, including the two that have nothing to
  interpolate. A line added to that block must escape itself too.
- **"TAKE an exam", never "sit" one.** The English face is written for
  Americans and *sit an exam* is British; the maintainer corrected it in the
  same message that asked for the link (glossary rule 42, the `reader` family
  of `check_review_english.py`, which covers the reviews but NOT the app's own
  strings). Nothing tests the interface for register, so it is on whoever
  writes the string. A sweep of the whole `T` table and of index.html for
  twenty common Britishisms found zero others, so this was the only one. The
  phrase left the interface entirely when the line was replaced, but the rule
  stands for the next string, and several COMMENTS in this file and in app.js
  still say "sit the exam": correct those as they are touched.
- **The link is found by the SUMMARY's key and the step by POSITION**, and
  both of those are deliberate. There are two `details.rules-note` on the
  dashboard and "How to use this app" is the first, so a `querySelector` on
  the class opens the wrong panel; the handler looks for
  `[data-i18n="next.summary"]` and climbs to its `details`. The steps carry no
  ids because the whole panel is ONE `data-i18n-html` block repainted per
  language, so an id written into the English markup would not survive the
  Italian paint. `ol > li:nth-child(4)` is what is left, and the harness
  asserts the element scrolled to is step 4 rather than merely that something
  was scrolled to. It was checked by sabotage: pointing the handler at step 1
  makes it fail.
- **Open the disclosure, then wait a FRAME before scrolling.** The browser
  lays the panel out only once `open` is set, so a `scrollIntoView` in the
  same tick aims at a zero-height box.
- **THE SCHOOL'S OWN GATE is a third date-moving fact, added 2026-09-21**,
  reported to the maintainer by a driving school. The school
  sees only its own app, and before putting a candidate forward it wants a
  good average on its own facsimile sheets: the
  school reads ITS OWN app, decides when to put the candidate forward, and
  wants a good average on its own sheets first. Work done in this app is
  invisible to it. That gap matters because the How-to names the hybrid route
  (school handles the paperwork, theory studied here) as what most immigrants
  pick, which is exactly the route where a learner finishes here and is then
  told to go and sit the school's sheets. It is now in step 4 of the How-to,
  in the hybrid bullet and in `docs/american-guide.md` (it was in
  `daily.paperwork` too until that line was removed the same day),
  and it is written as what schools commonly do rather than as a rule, because
  it is the school's condition and not the Ministry's.
  The same school confirmed the order the How-to already taught (the
  certificate from your own doctor comes before the school's visit) and
  gave its readiness bar: an average under three mistakes on its sheets,
  with no fixed number of attempts. Our ring sits at 93%, about two mistakes over the last five, so it
  is that floor plus a margin; leave it there.
- **The How-to is ONE `data-i18n-html` block per language**, English in
  index.html and Italian in `STATIC_IT['next.body']`, so every edit is two
  edits. `data-i18n` would flatten the markup (see the Glossario section);
  `/tmp/howto_dom.js` renders both faces and checks the new text, the ten list
  items and that the markup survived the paint.
- **Verified in jsdom, `/tmp/howto_dom.js`, 24 checks in each language face**
  (`UILANG=it-IT node /tmp/howto_dom.js`): seven steps with the markup and the
  links intact after the paint, the conversational line absent in both halves,
  the *medico di base* before the authorized doctor inside step 2, step 2
  naming neither route while step 3 names both and says when step 2 happens,
  the intro not repeating them, step 2 keeping the three-month deadline and
  the booking dependency, the "needed to enroll" wording gone, and STEP 4
  STILL THE THEORY EXAM, which is what the projection's link points at by
  position. Proved to bite by putting the old sentence and the school mention
  back into step 2, which fails four checks. The `/tmp` harnesses do not
  survive a sandbox restart and this one was rebuilt from scratch on
  2026-09-21; `npm install jsdom` into `/tmp` first, and load it by absolute
  path.
- **SEEDING THE DAILY LOG is where that harness goes wrong, three ways, and
  every one of them passes the test for the wrong reason.** With no usable
  seed the projection prints "Answer some questions and this will estimate
  when you could be ready", which contains no medical either, so a "the
  paperwork is gone" assertion passes against a block that was never drawn.
  `/tmp/show_proj.js` prints the block, and it is the honest probe: look for
  three lines and a date before believing the checks.
  - The key is **`patente_daily`**, not `patente_daily_log`.
  - `dayKey` builds its key from the LOCAL date, so a seed keyed by
    `toISOString()` lands on the wrong day whenever the two disagree.
  - `rateWindow` reads **`a`**, the answers, and returns null without it, so a
    log carrying only the per-level `m` fields yields no rate and no date.
    `dailyProgress` then reads `m1`/`m2`/`m3` and ignores `a` and `c`, so both
    are needed. Seed the window at offsets 1 to 13: offset 0 alone is the
    `partial` case, which deliberately prints no date.
  - An Italian browser counts only the Italiano level (`countedLevels`), so
    seed `m3` as well as `m1`.

- **The licensing How-to is two route tabs since 20261007c (maintainer,
  2026-10-01), and the step-numbered bullets above describe the layout
  before it.** A shared opening (eligibility, the two routes, the theory
  course is optional), then tabs "Through a driving school" (default) and
  "As a private candidate" (`.route-tab` / `.route-pane`, choice in
  `patente_howto_route` on the device, applied after every `applyI18n`
  paint by `applyRouteTab`, click delegated). Each route is eight steps in
  the order the learner does them, with its own Cost paragraph, and the
  theory-exam step carries `class="step-theory"`, which the projection's
  "ready" link now finds in the tab showing (position 4 is the fallback for
  a stale English page). Below the tabs: how long, the US-license note, the
  English-speaking school tip, and a disclaimer that procedures vary by
  region and office, asking the reader to report a different experience
  through Report a problem. The Options-for-English-speakers block went;
  the opening and the tabs cover it. Facts checked on 2026-10-01: payments
  are pagoPA since 14 February 2022 (the old text still named two postal
  slips), N067 is €26.40 plus €16 to enroll (a Motorizzazione's instruction
  sheet on the Portale dell'Automobilista), N019 €16 for the driving test
  (a search snippet of the Ministry page, which would not load), and the
  TT2112 asks for one 33 x 40 mm photo. The authorized doctor's fee and a
  school's charge for its car at a private candidate's test are named but
  not priced, for lack of a source. The draft and its sources are in
  `docs/license-process-draft.md`. `build_topic_pages.py` renders both
  routes on `about/license-process.html`, each an h2 with its steps as h3.
  **Compared with an outside guide on 2026-10-04** (Expats Living in
  Rome, "How to get an Italian driving license", updated September 2026):
  it agrees on fees, the 8 hours in four modules, the 12-month foglio
  rosa, 30 questions and 3 errors, and 12 months on a US license. Added
  from it (20261011n): no interpreter or dictionary is allowed in the
  theory exam room; the school usually takes the application photo; some
  offices ask for two photos. Kept
  against it: our 3 to 6 months (the article says 6 to 12; the maintainer
  reached the 5% target inside ours and will report how the rest goes),
  and French as a third exam language (the article omits the Aosta
  Valley). Its €200 to €400 enrollment against our €150 to €300 is left.
  `scripts/check_howto_tabs.js`, 13 checks in each face.
  **Read the certificato anamnestico before it is used (20261012r).** A
  family doctor can mark "yes" on a line of
  the note for a condition that is in fact mild, and the authorized doctor
  then refers the candidate to the Commissione Medica Locale, where the
  wait can be months. The medical-history step of both
  routes now says to read the note, that a yes can mean the commission
  and a wait of months, and to ask the doctor about a line that looks
  wrong before the note is used. It says "can", since not every yes goes
  to the commission.
  **The note's conditions sit in each route's "Get the medical-history
  note" step since 20261012w** (maintainer: the note is where they are
  asked; the authorized doctor only checks the eyesight and reviews the
  note, which the medical step now says). Since 20261012x the note step
  holds the list and the advice to have a wrong line corrected, and the
  medical step holds "If the note has a yes": that doctor reviews it and
  decides whether to send you to the commission, which cases go there,
  and the specialist's report to bring (maintainer: it is the step 2
  doctor who reviews and refers). For one release (20261012t to v)
  they sat in the "Pass the medical" step,
  under "What the note asks", and since 20261012v the eleven lines are a
  bulleted list matching the form (English with the form's Italian
  heading; the Italian face uses the form's own wording).
  `process_page` reads top-level steps with `_top_items` and keeps a
  nested `<ul>` as a list; `.rules-body ol li li` gives it its indent. It was first
  **a section after the route tabs listing what the note asks (20261012s,
  maintainer: "let the users know everything on that form that could
  trigger a medical commission visit")**, "What the medical-history
  note asks", in both languages and as an h2 on the licensing page: the
  eleven lines of the certificato anamnestico, then which answers go to
  the commission, from Annex III of D.Lgs. 59/2011 and art. 119 c. 4 of
  the Code: epilepsy unless certified cured (D), past alcohol dependence
  (E), habitual medicines affecting driving (F.2), serious psychiatric
  (G) and neurological (H.1) conditions, kidney failure on dialysis or a
  transplant (Appendix II, art. 320 Reg.), physical impairment (art. 119
  c. 4 a), and any doubt of the authorized doctor (c. 4 d). Heart
  conditions (B.2) and diabetes for B (art. 119 c. 2-bis, C.1) need a
  specialist's report and may stay with the authorized doctor. The two
  route steps now point to this section instead of naming conditions.
  **Three facts added on 2026-10-17 (20261017i)**, after a comparison with
  the Ready Set Italia guide for Americans: at least a month must pass
  between a failed exam attempt and the next, theory or driving test
  (art. 121 c. 10); the medical certificate carries a €16 marca da bollo
  on top of the authorized doctor's fee; and driving on a US license after
  the 12 months brings a fine and the license taken on the spot and sent
  to the Motorizzazione (art. 135 c. 14), or, if that license has also
  expired, the penalties for driving without a license, with the vehicle
  impounded for three months (art. 116 c. 15 and 17), stated without euro
  amounts. The rest of that guide was either already here or outdated (a
  6-month foglio rosa, learners barred from the autostrada, 55 kW/t, a
  fine figure from an old art. 116); do not take those.

## The `<head>` (what the app looks like before anyone opens it)

- **iOS does NOT read `manifest.json` for the home-screen icon.** It wants
  `<link rel="apple-touch-icon">`, and without one it probes the SITE ROOT for
  `/apple-touch-icon.png`, fails, and uses a screenshot of the page as the
  icon. `icons/apple-touch-icon.png` had existed all along with nothing
  pointing at it, so every Add to Home Screen on an iPhone got a screenshot.
  That matters more here than it sounds, because installing to the home screen
  is part of what the app offers and every visitor so far has been on an
  iPhone.
- **It was found in the access log, not by looking at the code.** The only two
  404s among 2,078 requests on 2026-09-21 were `/apple-touch-icon.png` and
  `/apple-touch-icon-precomposed.png`, both from one iPhone visitor. A missing
  head tag produces no error anywhere else: the page renders, the app works,
  and the only symptom is on the person's home screen where nobody can see it.
  **Read the 404s in a new log before assuming they are noise.**
- **`<meta name="description">` is kept under 160 characters**, which is about
  where Google truncates. The harness enforces the bound, and it bit twice
  while the line was being written.
- **The Open Graph tags exist so a shared link is not a guess.** Facebook's
  scraper had been deriving the card from the title and whatever image it
  found, which happened to work; `og:title`, `og:description`, `og:image` and
  the rest now say what it should show. `og:image` must be an ABSOLUTE URL, so
  the harness checks both that and that the file it names exists.
- **Verified in jsdom**, `/tmp/head_dom.js`, 21 checks: every tag present, the
  two icon links and `og:image` pointing at files that are really on disk, the
  description inside its length bound, and the pre-existing viewport,
  theme-color, title and page body undisturbed. Proved to bite by deleting the
  apple-touch-icon link and by pointing `og:image` at a missing file.
- **The `/tmp` harnesses do not survive a sandbox restart**, and one happened
  mid-session on 2026-09-21: `order_dom.js`, `howto_dom.js` and `sync_dom.js`
  were all gone, along with `node_modules`. `npm install jsdom` into `/tmp`
  again and rebuild the one you need. Anything that must not be lost belongs
  in `scripts/`, not in `/tmp`.

## The guide (`public_html/about/`, 25 generated pages for search)

- **The folder was `guide/` until 2026-09-24 and is now `about/`**, at the
  maintainer's request. `.htaccess` sends every `/guide/...` URL on to
  `/about/...` with a 301, because Googlebot had already crawled the old
  addresses. Keep those two `RedirectMatch` lines.

- **Why it exists.** The app is one page, and everything in it reaches the
  reader as JSON fetched by JavaScript, so a crawler finds data rather than
  prose and one page can rank for a handful of queries however good it is.
  These 25 pages are real English articles on Italian road rules, which is
  what somebody searching "italian warning signs meaning" is looking for.
  65,800 words and 324 figures across 26 pages.
- **`robots.txt` DISALLOWS NOTHING, and that is deliberate as of 20260928g.**
  The four data files were disallowed from the start, on the reasoning that a
  crawler has no use for a 1 MB JSON. The cost was invisible and larger.
  Googlebot RENDERS a page to see what a visitor sees, its rendering fetches
  obey robots.txt, so its render of `/` could not load `questions.json`,
  `loadDataFile` threw and `showLoadError()` ran: what Google saw may have
  been "Couldn't load the questions" rather than the app. `index.html` does
  carry 4,135 words of static text (the How-to panels) that Google may have
  fallen back to, so this is a risk rather than a proven loss, but it was a
  coin flip taken for nothing, since crawl budget is not a constraint on a
  site of 27 URLs. Do not re-add those lines.
- **Every heading carries a slug `id`, and each page opens with a contents
  list** (`slugify`, `toc_html`, added 20260928g). A page of anonymous `<h2>`s
  cannot be linked into, so a section cannot rank for its own query ("italian
  double bend sign") and Google cannot offer a jump link inside a result. 298
  ids and 221 contents links across the 25 pages. Three details that were
  decided rather than defaulted: the slug is built from the RAW markdown with
  emphasis, link and image syntax stripped and the result folded to ASCII,
  because these headings carry Italian terms and an accented or asterisked
  character in an id is a link nobody can type; only `h2` reaches the contents
  list, though `h3` and `h4` still get ids, because listing them would make
  the list longer than some of the sections it indexes; and the list sits
  BELOW the call to action, which keeps that link where it has always been
  rather than pushing it under eight items on a phone. `TOC_MIN` is 3, so a
  page shorter than its own heading list does not get one (no page is).
- **The generator proves the anchors resolve, reading its own finished HTML.**
  Ids and contents list are built from one list and so agree by construction;
  the pass exists because that is exactly what a future change to `render`
  would break silently, since a duplicate id sends one contents link to the
  wrong section and nothing about the page looks wrong. Proved to bite twice:
  forcing `slugify` to return a constant, and prefixing every fragment.
- **Per-QUESTION pages were considered and rejected.** Seven thousand
  near-identical pages is thin content, the thing search engines penalise.
  Per-TOPIC pages stand up as articles on their own.
- **It does not touch the app, and that was the maintainer's condition**
  (2026-09-22: "I don't want to change the content or look and feel of the
  app"). The pages carry their own `guide.css` and reference nothing from
  `index.html`, `app.js` or `style.css`; they share only the sign images, in
  place. The harness asserts that no page pulls in the app's stylesheet or
  script, so the coupling cannot creep back. The commit's diff to the app's
  own files is the version bump and nothing else.
- **`scripts/build_topic_pages.py` generates all of it**, from the same
  Markdown `md_to_reviews.py` reads, English half only, all markers stripped.
  It also regenerates `sitemap.xml`. Run it after any topic-review edit;
  `validate_data.py` now runs `--check` and FAILS if the pages are stale,
  because a review edited without rebuilding would otherwise go on describing
  the old rule to every search visitor, silently.
- **The English titles are in `topic_reviews_md/_guide_titles.json`**, not
  derived. The Ministry's topic strings are bureaucratic Italian and make poor
  page titles; each needs a name phrased the way an American would say it. The
  generator refuses to build a topic with no entry, so none can ship untitled.
  Keep `title` plus the 23-character suffix under 65 characters, which is
  roughly what a search result shows; three were over on the first pass.
- **EMPHASIS NEEDS THREE PASSES, innermost last.** The reviews use
  `***bold italic***` for an Italian term inside a bold label, and nest a
  single `*italic*` inside `**bold**` constantly (`**Moped (*ciclomotore*).**`).
  A plain `\*\*([^*]+)\*\*` matches neither, because the content carries an
  asterisk, and it leaves the markup on the page as literal text. That shipped
  in four pages on the first run. Triple first, then bold with italic applied
  to the captured content, then italic.
- **Two sabotage attempts of mine failed for reasons that were MINE, not the
  code's**, and both are the same lesson. Breaking an image path in
  `09-distanza-di-sicurezza.html` proved nothing because that page has no
  images; appending a line to a `.md` proved nothing because the end of the
  file is the ITALIAN half, which the guide does not read. A sabotage that
  does not fail is not evidence the check works until you have confirmed the
  sabotage actually changed what the check reads.
- **Verified over all 26 pages, 1,514 checks** (1,491 before the anchors): no
  review markers or unrendered markdown left, one `h1` each, head tags with
  the description inside its bound, every `img` resolving to a file on disk and
  carrying alt text, every internal link resolving, every `#fragment` matching
  a heading id, no duplicate id, every page with three or more `h2`s carrying a
  contents list that covers all of them, the sitemap listing 27 URLs, no
  `Disallow` left in robots.txt, and no page referencing the app's CSS or JS.
  These pages are static HTML with no script, so the check is Python against
  the files rather than jsdom; the anchor half of it also lives inside
  `build_topic_pages.py`, where it cannot be lost to a sandbox restart.
- **`about/license-process.html` is the How-to panel as its own page**
  (added 2026-09-24 at the maintainer's request), titled "How to Get an
  Italian Driver's License, Step by Step" with the h1 "How Americans Get an
  Italian Driver's License". **The index and this page target DIFFERENT
  searches on purpose**: the index is the hub and carries the expat search
  ("Italian Driver's License for American Expats — Patente B Guide", h1 "The
  Italian Driver's License: A Guide for American Expats"), this page carries
  "how to get". Giving both titles the same words would make them compete, and
  Google usually shows only one. Americans say "written test" and "driver's
  license", never "theory exam", so neither title uses it. The licensing process is the
  most-searched subject the site covers, and it had no URL: it sat collapsed
  inside `/`, under a title about the theory app, with its seven steps as list
  items. The page is GENERATED from the panel's English block in index.html
  (`process_page` in `build_topic_pages.py`), each step an h2 "Step N:
  <label>" and each bold-labelled paragraph after the list ("Cost.", "How long
  does it take?") an h2 of its own, 11 sections in all. Editing the panel
  without rebuilding fails `validate_data.py`, which was checked by sabotage.
  Every guide page's footer and the guide index link to it, and the sitemap
  lists it (28 URLs). **The app's footer links to `/about/`** since 20260930r
  (maintainer's request, 2026-09-24; before that the app linked to none of the
  guide). The link sits above the copyright line, `ensureAboutLink` builds it
  when a stale cached index.html lacks it, and the Italian label says the page
  is in English.
- **The landing page's WORDING lives in `pages/about.md`** (2026-09-24, so the
  maintainer can edit it as plain text). Title and description lines, a `---`,
  then one `#` heading, paragraphs, and one `##` heading that opens the closed
  box listing the topic pages. `[text](app)` and `[text](process)` are the two
  internal links, `{LIVE}` and `{PROCESS_TITLE}` the two placeholders.
  `about_page()` in `build_topic_pages.py` renders it and RAISES on anything
  else, so a typo fails the build rather than shipping stray symbols. The file
  is outside `topic_reviews_md/` on purpose: `apply_mapping.py` globs every
  `.md` there. Edit it, run `build_topic_pages.py`, then `validate_data.py`.
- **`about/how-it-works.html` describes the app feature by feature
  (20261012c, maintainer, 2026-10-05: search engines should see the full
  capabilities, and that the app is written for Americans).** Its wording
  is `pages/how-it-works.md`, in about.md's format except that every `## `
  is a section (h2 with an id, in the contents list) and there is no box;
  `[text](about)` links the landing page and `[text](features)` this page.
  It is linked from the landing page's box and listed in the sitemap and
  the CollectionPage data. The landing page's opening was left exactly as
  it was, at the maintainer's word. Every claim on the page is checked
  against the app; correct it there when a feature changes. In the same
  release the app's `<title>` became "Italian Driver's License Written
  Test in English | Patente B" (Americans say written test, not theory
  exam), the description and Open Graph tags followed, and the
  `WebApplication` data gained an audience, a subject and a feature list.
  `applyI18n` used to overwrite the title at runtime, and Google renders
  the page, so the English face now keeps index.html's own title.
  **The title is "Patente B Study App for Americans | Italian Driver's
  License" since 20261017f** (maintainer, 2026-10-17: the tab title
  should say, for a non-Italian browser, that this is a Patente B study
  app written for Americans). The og:title and the JSON-LD `name` follow;
  the written-test phrase stays in `alternateName` and the description.
  The Italian browser's title is unchanged.
  **The manifest's full name follows (20261017g, maintainer):**
  `manifest.json` is "Patente B Study App for Americans", shown in install
  prompts and the app switcher, and `applyI18n` points an Italian browser
  at `manifest-it.json` ("Patente B — App per la patente"), which sw.js
  precaches too. Both keep the short name "Patente B", the home-screen
  label, since an icon label is truncated past about twelve characters.
  `scripts/check_manifest.js`, 5 checks in each face; the previous build
  fails the Italian one.
  **The dashboard tagline says the same (20261017h):** "The Patente B
  study app written for Americans. Every official question in English and
  Italian, with the rule behind each answer, online or offline." The
  Italian tagline (`app.tagline` in STATIC_IT) is unchanged.
- **The guide INDEX is a SHORT LANDING PAGE for people, and it says openly
  that the topic pages are for search engines** (maintainer, 2026-09-24,
  after three rounds: a landing-page look, then a long first-person guide,
  both rejected). It holds only: who he is, why he built the app, the AI
  disclosure, one prominent link to the app, a link to the licensing page,
  and a CLOSED disclosure, "The other pages on this site (mainly for search
  engines)", that says those pages are here mainly so search engines can find
  the site (a closed `<details>` still carries its links in the HTML, and the
  sitemap lists every page anyway), followed by the 25 topic
  titles as plain links. The honesty is the point: do not grow it back into a
  guide, do not add a quiz, stats or selling, and do not present the topic
  pages as something written for readers. The sample-question quiz
  (`guide/quiz.js`) and the extraction of the How-to panel's text into the
  index were REMOVED the same day.
- **The guide LOOKS LIKE THE APP** (maintainer, 2026-09-24, replacing a
  serif personal-blog look he had asked for that morning). `guide.css` copies
  the app's color tokens from `style.css`, its system sans font, a white bar
  with the 2px violet rule holding only the app icon (a link to the app), the
  content on a white card, and the app link drawn as the app's `.btn-primary`.
  It still REFERENCES nothing of the app's, so a change to the app's palette
  has to be copied into `CSS` in `build_topic_pages.py` by hand. Dark mode
  follows the system, since these pages run no script to read the app's own
  theme toggle. Still no footer, no stats strip, no pricing language, no
  testimonials. The earlier landing-page look modelled on autoviatest.com was
  rejected as reading like a commercial product; do not bring that back.
- **SUPERSEDED 2026-10-05 for every page but the landing page**: the
  maintainer asked that the guide pages be written professionally, like a
  textbook, with no reference to him. Only the landing page
  (`pages/about.md`) keeps his first-person story. The topic pages' call to
  action, the licensing page's opening and `pages/how-it-works.md` were
  rewritten without "I", "my" or contractions; address the reader as
  "you" where needed, never speak as the author. The bullet below is the
  history.
- **The guide's VOICE is the OPPOSITE of the app's** (maintainer, same day):
  first person and CONVERSATIONAL, with contractions, direct address and a
  personal story, because a real expat's blog reads that way. The app's
  terse-and-declarative rule and the ban on conversational filler do NOT
  apply to the guide's own framing prose (the index, the licensing page's
  opening, the aside, the footer); they still apply to the topic articles,
  which are the reviews rendered. Every personal detail must be one the
  maintainer has actually told: enrolling at the autoscuola first, the
  *medico di base* then the school's fitness visit, the school's bar of
  fewer than three mistakes on its own sheets, building
  the app for his own study, and the ORIGIN STORY he gave on 2026-09-24 (he
  needed the license, no existing app worked for him, thirty-plus years as a
  professor told him there were better ways to learn this, and he built it
  with the latest AI tools for writing software). What put him off the other
  apps, in his words: they were English translations of Italian driving apps,
  not written for American English speakers who are established US drivers. The landing page says so,
  and also says plainly that the English translations and explanations were
  drafted with AI help and are still being checked topic by topic. Keep that honesty: do not remove the AI disclosure
  or claim the content is finished. Add no anecdote, feeling or date he has not
  given. No stats strip, no pricing language, no
  testimonials, no emoji icons. The question count is still read from
  `questions.json` as `LIVE`, never typed. **The app was not touched.**
- **Screenshots in the sandbox work** with the installed Playwright
  Chromium once `libXdamage.so.1` exists: apt is blocked, so compile a stub
  (six no-op functions, `gcc -shared -fPIC -Wl,-soname,libXdamage.so.1`) and
  run with `LD_LIBRARY_PATH` pointing at it. Headless rendering never calls
  it. Emoji render as boxes there for lack of a font; they are fine on a
  real device.
- **One quirk worth knowing.** The service worker's scope is `/`, so it
  controls `/about/*` too. `.html` matches `NETWORK_FIRST`, so a visitor gets
  the live page; offline, the navigation fallback serves the APP shell rather
  than the guide page. Crawlers run no service worker, so search is unaffected.
- **A source typo the generator rendered correctly, fixed 2026-09-23**: topic
  16 had `**Work machine (*macchina operatrice*). ** ` and `**Autostrada. **`
  with a space before the closing marker, in both halves. Corrected in the
  reading pass; a new one would show as literal asterisks in the app.

## Who actually reaches the app (read the log, not the theory)

- **The first five outside visitors, all from Facebook, all on iPhones**
  (2026-09-21 and 22). Three loaded cleanly, two hit the ten-fetch failure and
  saw nothing. Two of the three asked for `/icons/apple-touch-icon.png`, which
  is what iOS requests when adding to the home screen, and one of those ran the
  service worker's image precache to completion: 516 sign images, 6.5 MB. So
  the install path works end to end and somebody used it. **The whole channel
  was Facebook**; nothing arrived from search, and nobody has visited `/about/`
  except Googlebot and the maintainer.
- **The two root-level `apple-touch-icon` 404s are permanent and harmless.**
  iOS asks for the declared icon AND probes the root for the plain and
  `-precomposed` names, in the same second. The declared one now answers 200.
  Do not chase those 404s again; they are not the bug that was fixed.
- **Googlebot took the sitemap and started on the guide within hours.**
  Googlebot fetched `/sitemap.xml` 200 on 22 Sep and then
  fetched two guide pages, 07:24 and 07:28. Crawled is not indexed, but the
  estimate given beforehand (about a week) was wrong in the slow direction.
- **THE HOST BLOCKS THE AI SEARCH CRAWLERS, and it is not us.** On 1 Sep
  `GPTBot/1.4` and `OAI-SearchBot/1.4` each tried twice and got **403**,
  including on `/robots.txt` itself; by 22 Sep neither comes at all, which is
  what a crawler does once refused. Nothing in `.htaccess` or `robots.txt`
  mentions a user agent and robots.txt says `Allow: /`, so this is GreenGeeks
  above the app. It matters because ranking in Google is gated on inbound
  links this project does not have, while an answer engine weighs topical fit,
  which it has in abundance. Worth separating the two if it is ever addressed:
  GPTBot is the TRAINING crawler and blocking it costs no discovery, while
  OAI-SearchBot feeds ChatGPT's live citations and blocking it removes the app
  from them. **Unresolved**: the maintainer has to find the setting.
- **`/BingSiteAuth.xml` 404s**, so bingbot came looking for a verification that
  does not exist. Bing Webmaster Tools imports from Google Search Console and
  feeds Copilot. Not set up.
- **The host rate-limits Facebook's scraper**: 129 requests from
  `facebookexternalhit` and four **429**s. That can make a link preview fail to
  render, which matters while Facebook is the only channel sending anyone.
- **The archives are named for the month the STATS RUN happened, not the month
  of the traffic.** `...-ssl_log-Sep-2026` holds 31 Aug to 1 Sep; September's
  own traffic lands in a file called `Oct-2026`. Two empty files turned up on
  22 Sep at 19:20:12, both zero bytes with identical mtimes, which is a
  rotation and not a quiet day. **cPanel discards raw logs at the end of each
  stats run unless archiving is switched on** (Metrics → Raw Access): turn on
  the archive checkbox and turn off "remove the previous month's archives", or
  this data keeps evaporating on a schedule nobody here controls.
- **Read a file's LAST ENTRY, not its mtime.** `-4` was described as ending at
  09:36 because that was the modification time; its last line is 07:31.

## Engagement per synced user (admin.php, 20261003n)

- **The admin page lists every sync bucket, newest first** (maintainer,
  2026-09-27: "I want to see if our users stay engaged"): the first eight hex
  of the bucket hash as the ID, the last sync (the blob file's mtime) with
  "N d ago", first sync, days active, uploads and size. Rows older than seven
  days are grayed.
- **Last sync is the last UPLOAD.** A launch with nothing new to push is a 304
  and writes nothing, so the column means the last time the person answered
  something, which is the engagement signal wanted.
- **`sync.php` writes a sidecar, `<bucket>.meta.json`**, on every POST: `first`,
  `last`, `pushes`, and `days`, the distinct UTC dates of upload (last 120).
  Dates and counts only, and a failure there never fails the sync. Buckets
  written before this release show "before tracking" until their next upload.
  The admin page's glob matches `[a-f0-9]{64}\.json$`, so the sidecar
  is never counted as a bucket; keep that anchor if either glob changes.
- **The privacy note does not describe the upload dates** (20261003o,
  maintainer's wording, 2026-09-27): it says the app sets no cookies and
  needs no account, so use is anonymous, and that synced progress is
  end-to-end encrypted. It no longer claims "no tracking or analytics",
  which the sidecar would contradict. Do not put either claim back.

## Reviewer flags across devices (comments lost, fixed 20260928p)

- **Comments were being deleted without ever being sent** (reported
  2026-09-23: "some of my comments were missing"). Two bugs made it.
  A Send stamped `FLAGS_CLEARED_KEY` with the current time, and every device
  then dropped every flag written BEFORE that time, including a flag written
  on another device and not yet uploaded. And nothing uploaded it: saving a
  flag never called `markSyncDirty`, so after the conditional-push change of
  20260928a a flag on its own stayed on its device until something else was
  answered. Flag on the iPhone, Send on the Mac, and the iPhone's comment was
  gone at its next sync. A third, smaller one: a flag saved while the POST was
  in flight was wiped by `saveFlags([])`.
- **Sent and discarded flags are now RETIRED ONE BY ONE** (`retireFlags`,
  keyed `number@ts`, in `patente_flags_retired`, carried as `flagsRetired` in
  the sync bundle and unioned on merge, capped at 3,000 keys). Send retires
  exactly the snapshot it posted; Clear retires the flags shown; the two
  delete buttons retire the one flag, which also stops a sync from
  resurrecting a flag deleted on one device. Re-flagging a sent statement
  gives a new `ts`, so it is a new comment and survives. The old time stamp is
  still honoured when a bundle carries one, but nothing advances it.
- **A SENT flag is KEPT, not retired (20260930t, maintainer's request,
  2026-09-24).** Sending used to delete every flag it posted, so a reviewer
  kept no record of their comments unless they had exported first. `submitFlags`
  now posts only the unsent flags and stamps each with `sentAt`; `flagSent(f)`
  is `sentAt >= ts`, so ANY edit (a new `ts`) puts the flag back among the
  unsent and it goes out with the next Send. The review overlay shows two
  groups, "Not sent yet" and "Sent", each sent row with its date and a Send
  again button (which just stamps a new `ts`), and a Delete all sent button.
  Discard now drops the UNSENT flags only; Export writes all of them. Deletion
  still goes through `retireFlags`, so it still syncs. The merge keeps the
  later `sentAt` when both sides hold the same `ts`, or a send on one device
  would go out again from the other. The dashboard's Send count is the unsent
  count. An older app on another device knows nothing of `sentAt` and would
  offer a synced sent flag for sending again; that ends when it updates.
  `scripts/check_flags_sync.js` is now 23 checks and fails on the old build.
- **The sent flags fold into a CLOSED disclosure** (`details.flags-sent`,
  20261003p, maintainer's request, 2026-09-27): they are a record, and the
  unsent ones are the work. "Delete all sent" sits inside the box. The open
  state is kept for the session (`_flagsSentOpen`), so the redraw after an
  edit does not snap it shut. `check_flags_sync.js` is 28 checks.
- **An unsaved comment is kept as a DRAFT (20261004n, bug report
  2026-09-28)**: a reviewer left the card for the Reference page mid-comment
  and lost it. `patente_flag_drafts` holds `{cat, note, t}` per statement on
  this device (not synced); every keystroke writes it, rebuilding the control
  restores it and opens the form, Save / Cancel / Remove clear it, and a draft
  older than `FLAG_DRAFT_DAYS` (14) is dropped. `scripts/check_flag_draft.js`,
  7 checks.
- **A sent comment never shows on the study card (20261010x, maintainer's
  bug report, 2026-10-04).** It replaces the "⚑ Sent" state of 20261010h,
  which still showed the old note on the card. A statement may now hold
  any number of SENT flags (a record, read-only in the Review and Send
  panel) and at most one UNSENT flag, which is all the card shows: "⚑ Flag
  issue" and an empty form once the comment has gone. `flagFor` returns the
  unsent flag only; `addOrUpdateFlag` and the card's Remove touch the
  unsent one only; panel rows are keyed by `flagKey` (number@ts) and carry
  the new key after each keystroke. The merge keys by `flagKey` (later
  sentAt wins), then keeps only the newest unsent flag per statement and
  every sent one. "Send again" is hidden while a newer comment waits.
  `check_flags_sync.js` 34 checks, `check_flag_draft.js` 11.
- **Reviewers can comment on Reference entries (20261011z, maintainer's
  bug report, 2026-10-05).** In reviewer mode every Vocabulary, Glossario
  and Numbers row carries a small ⚑ (`entryFlagHtml`, written into the row
  markup; one delegated listener per list, `bindEntryFlags`, since a
  button bound per row cost a minute in jsdom on the 6,211-row Vocabulary
  list). It opens the statement's comment form under the row
  (`buildFlagForm`, which `buildFlagControl` now calls too), with the
  categories "Entry is wrong or unclear", Translation, Question, Other.
  The flag's `number` is a string naming the list and the entry, `vocab:
  veicolo`, `gloss: carreggiata`, `num: ` and the row's English label, so
  it travels through the same store, sync, Review and Send panel and
  `submit-flags.php` (whose `number` limit went from 12 to 120 characters,
  and whose batch instructions say such a flag is fixed in
  vocabulary.json, glossary.json or reference.json). The panel lists
  statements first, then entries (`flagOrder`). A Numbers row is named by
  its English label, so renaming a label orphans an old comment's name,
  not the comment. `scripts/check_entry_flags.js`, 13 checks in English,
  12 in Italian; the previous build fails.
- **The backup banner's buttons open Settings AT their block (20261013a,
  maintainer, 2026-10-14: "it takes it to the settings but not where the
  sync button is").** Both called `openSettings()`, which opens at the top,
  and since the groups by stage (20261011f) the sync and backup blocks sit
  in "Your data" near the bottom. `openSettingsAt` now finds a target
  inside `.settings-sync` or `.settings-backup` as well as a `.settings-row`;
  "Back up now" targets `btn-export`, "View my sync code" targets
  `sync-code-value`. `scripts/check_backup_banner.js`, 6 checks in each
  face; the previous build fails 2. A new Settings block that a banner or
  link should land on needs one of those classes, or `openSettingsAt` opens
  at the top in silence.
- **`saveFlags` marks dirty; `storeFlags` does not.** Every reviewer edit goes
  through `saveFlags`. The merge writes through `storeFlags`, because marking
  dirty on a pull would force a push on every quiet cycle.
- **One flag per statement is still the model.** A second flag on the same
  statement replaces the first, and if two devices flag the same statement
  before syncing, the newer wins. That is a design limit, not this bug.
- **`submit-flags.php` truncates a note at 800 characters** and rejects a
  batch over 64 KB (about sixty flags) with an error, keeping the flags. A
  truncated note looks like a short comment, not a missing one.
- **`scripts/check_flags_sync.js`, 14 checks**, two jsdom windows as two
  devices, sync modelled by passing one `buildProgressBundle()` to the other's
  `mergeDeviceState`, which is what the real sync and import call. It is kept
  here rather than in `/tmp`, which a sandbox restart emptied the same day.
  Run with `SRC=` pointing at the previous release to see it fail: the old
  code fails "B's unsent flag SURVIVES A's send", which is the report.

## Replying to people (added 20260930v, 2026-09-24)

- **The first outside bug report arrived with no way to answer it** (an iPhone
  user on Firefox who could not find the Share button). The Report a problem
  form now has an OPTIONAL email field (`#bug-email`, built by
  `ensureBugEmail` when a stale index.html lacks it). `report-bug.php` keeps it
  only if `FILTER_VALIDATE_EMAIL` accepts it, and `admin.php`
  prints it as a mailto link. The last address used is remembered on the device
  (`patente_bug_email`), never synced, and prefilled only when the form OPENS:
  prefilling at send put back an address the user had just cleared.
- **No automatic acknowledgment email, deliberately.** Mail from the shared
  host would need SPF/DKIM to avoid spam folders, and a public form that
  mails whatever address is typed into it can be used to send mail to
  strangers. The form says on screen that the report was received and, when
  an address was given, that the maintainer will reply to it. He replies from
  his own mail.
- **The maintainer is emailed a copy of every bug report and reviewer batch**
  (20260930y) when `secrets.php` sets `'notify_email'`; `notify.php` holds the
  one function both endpoints call AFTER the record is written, so a mail
  failure never loses a submission. The recipient comes only from
  `secrets.php`, never from the request, so the form cannot mail strangers.
  The submitter's address (the bug form's optional field, or a trusted
  reviewer's from `secrets.php`) goes into Reply-To only. A global cap of 30
  mails an hour, across all visitors, stops a flood of submissions becoming a
  flood of mail; over the cap the submission is still stored. The sender is
  `'notify_from'`, default `noreply@<domain>`, and must be on the site's own
  domain or iCloud and Gmail will file it as junk (cPanel, Email
  Deliverability, has to show SPF and DKIM valid).
- **`flags-admin.php` and `bugs-admin.php` are GONE (20261025o).** `admin.php`
  replaced them on 2026-08-16 and they stayed in the tree, each refusing
  every request for want of a key in `secrets.php`. Removed before the
  public release; delete them on the server as well. `sync-admin.php`, the
  same case, went with them at the maintainer's word (20261025p).
- **Reviewer emails live in `secrets.php` only**: `'code' => ['name' => …,
  'email' => …]` beside the old `'code' => 'Name'` form, which still works.
  Neither submissions file ever stores the address; the admin pages look it up
  by display name for trusted reviewers and draw a reply link. Flags gained a
  `question` category ("Question for the developer"), badged QUESTION in
  admin.php, and the batch instructions tell whoever processes it to answer
  the question and change content only if the answer shows it is wrong.
- **The privacy note says so**, in both languages: an email is sent only if
  typed into the bug report form, and used only to reply.
- **The install hint names the browser on iOS.** Every iOS browser can add to
  the Home Screen, but only Safari keeps Share on its toolbar: Firefox has it
  under ☰, Chrome in the address bar (`install.iosFirefox`,
  `install.iosChrome`, `install.iosOther` for the rest, which points to Safari).
  **Desktop and Android followed the same day (20260930w)**, after the
  maintainer saw the Safari "Add to Dock" hint in DuckDuckGo on a Mac.
  Chromium browsers get `install.chromeDesktop` (address-bar install icon),
  Android gets `install.android`, and Firefox or DuckDuckGo on a desktop get
  `install.macOther` / `install.desktopOther`, which say plainly that the
  browser cannot install web apps and name one that can. DuckDuckGo's desktop
  browser is WebKit, not a Firefox fork, and says "Safari" in its user agent;
  the `Ddg/` token it appends is the only tell, so if that token ever
  disappears DuckDuckGo users fall back to the Safari hint.

## The update check (and the app icon)

- **Four things ask for an update, and only one of them is visible.** The
  worker is asked at registration, again on every return to the foreground
  (`visibilitychange`), by the "Check for updates" button in Settings, and
  since 2026-09-20 by the APP ICON in the nav, at the maintainer's request.
  The icon already parks a drill and returns to the dashboard, which is the
  moment a restart costs the learner nothing, so the check rides along there.
- **The icon's check is SILENT** (`checkForUpdateQuietly`). It has nowhere to
  print a status line, so it shows nothing unless a new version is genuinely
  ready, and then it raises the same banner every other path raises. The
  footer button keeps its own wording because it has a status line to fill.
- **It has to cover two cases, and they are not the same one.** A worker that
  finishes installing while the app is open is caught by the `updatefound`
  listener bound once in `registerServiceWorker`, so the icon only has to ASK.
  A worker ALREADY waiting fires nothing further, which is the case after the
  learner dismissed the banner or the install finished in a previous session,
  so `checkForUpdateQuietly` offers `reg.waiting` itself. `showUpdateBanner`
  returns early when the banner is on screen, so the two cannot double it.
- **Verified in jsdom, seven checks, and the harness has three traps.**
  `runScripts` must be `'dangerously'`, not `'outside-only'`, or an appended
  `<script>` never executes and every assertion passes for the wrong reason
  (the dashboard is the default screen, so "the icon shows the dashboard"
  passes with no code running at all; `window.__patenteBooted` is the honest
  probe). Strip the `<script src="app.js">` tag from the HTML before
  constructing the DOM, or app.js runs twice, once from the page and once from
  the injection. And do NOT dispatch `DOMContentLoaded` by hand: the JSDOM
  constructor returns before it fires, so an injected script still catches the
  real one, and the manual dispatch makes the whole boot run twice, which
  doubles every counter the test is reading.

## Environment constraints
- You can read, edit, and **commit**, but you **cannot push or deploy**. The user
  pushes and uploads `public_html/` to the server.
- **Upload order: the three DATA files first, then `app.js`, then `sw.js` last.**
  Since 20260930q the data URLs carry each file's content hash, so a code-only
  release leaves them untouched and only a CHANGED data file needs uploading;
  the order rule stands for exactly those.
  Getting this backwards silently ships new code against old notes, and the
  damage lasts the whole release. The installing worker precaches
  `questions.json`, `vocabulary.json` and `topic_reviews.json` at the NEW
  `?v=` URLs the moment `sw.js` arrives (`sw.js` install step), and those URLs
  are served cache-first. So if `sw.js` lands before the new
  `topic_reviews.json`, the worker fetches the OLD file, `isWholeJson` sees
  valid JSON and caches it under the new key, and it is STICKY: every claim
  added in that release is missing until the next version bump. "sw.js last"
  alone is not enough, because it protects the code and says nothing about the
  data. This is the likeliest cause whenever a reviewer reports that review
  content you just wrote "is not there" or that a 📖 lands on the heading, and
  it was reported that way for 24097 and 24092 (2026-09-13) and again for
  25007, 25010 and 25040 (2026-09-16, flag batch 20260916-2218), all with
  correct claims in the repository. The cheap check is to open the notes and
  look for one exact sentence the new release added.
- No PHP runtime locally. No network except approved fetch/search tools.
- `domandeb_images/` are pre-trimmed sign images (uniform small white margin).
  The study card sizes them by aspect ratio: tall composites (h/w > 1.2) get a
  `img-tall` class (taller cap); single signs use the default cap.

## Repo map (see README for detail)
```
public_html/      ← the deployable app (bump version on any change here)
  app.js          ← APP_VERSION at top; all app logic
  sw.js           ← CACHE_VERSION at top; service worker
  questions.json  ← the bank (don't touch italian_text/answer)
  topic_reviews.json   ← GENERATED — never hand-edit
  abridged.json   ← frozen abridged set
  vocabulary.json ← tooltip terms
  *.php           ← optional endpoints; read secrets via secrets.php
  secrets.example.php  ← template (secrets.php is gitignored)
topic_reviews_md/ ← SOURCE of the concept reviews (edit these)
scripts/          ← md_to_reviews.py, validate_data.py, extract/translate tools
docs/             ← guides & prompts (below)
```

## Withdrawn statements
The Ministry withdrew **41 statements** between the January 2023 listato we
extracted and the **23 April 2025** one it publishes now. Nothing else
changed: no answer, no wording, and nothing was added. `docs/BANK-2025-DIFF.md`
records the full comparison, lists all 41 with a reason for each, and carries
the parser trap that cost 5,030 phantom differences on the first pass.

How a withdrawal is handled:
- The statement **keeps its entry** in `questions.json` and gains
  `"retired": "YYYY-MM-DD"`, the date of the publication that dropped it.
  That file is our archive of the bank, so a withdrawal should be visible
  rather than erased.
- `dropRetiredStatements` in app.js filters them **once, at load**, and drops
  any card left with nothing. One place, so every count, the study cards, the
  drills and the mock exam stay consistent. Cards 4143 and the variant 5034
  vanish that way.
- `validate_data.py` checks the date format, rebinds `questions` to the live
  view so every later check ignores them, prints the live counts, and **fails
  if `abridged.json`, `review_anchors.json` or `reference.json` still cites a
  retired statement**. That last check is the valuable one: a dangling
  citation leaves a Reference figure with no source or a review paragraph
  claimed by a statement nobody can meet, and it caught six on the first run.
- A claim marker on a withdrawn statement must go too, since a claim is a
  promise that the paragraph answers that statement.
- **Re-run `consolidate_vocab.py` after a retirement.** It counts over the
  live statements only, so a gloss whose word survived nowhere else shows up
  as dead and its `f` frequency stops overstating how often the word is met.
  The 41 withdrawn statements killed 12 entries that way, 9 outright and 3
  migrated to the phrase that covers them, and left 304 counts stale.
- **Check the Reference page.** A figure sourced only by a withdrawn statement
  has to go. 24550 took the 75 kW/t and 105 kW rows with it, leaving 98
  numbers where there were 100.
- **Do not delete the statement and do not reword it.** Retiring is reversible
  and the Ministry has restored statements before.

Ten of the 41 are worse than unaskable, because the 2024 reform changed the
law underneath them. Where the notes existed to serve one of those, the notes
were corrected too: the child-restraint bullet no longer tells the learner
that restraints are grouped by weight, topic 22 no longer prints the
superseded 55 kW/t and one-year figures, topic 23 no longer limits insurance
to areas open to the public, and the two Reference rows whose only source was
24550 are gone.

## Reference sources on disk
- `sources/` also holds the three files the Ministry publishes today:
  `domande AB italiano 23 04 2025.pdf` (the current bank, 590 pages),
  `domande revisione AB italiano 23 04 2025.pdf` (the published subset used
  for licence-revision exams) and `Domande Superiori italiano 04 04 2025.pdf`.
  They arrived on 2026-09-15 from the Portale dell'Automobilista notice "QUIZ
  PER LE PATENTI AM, B, SUPERIORI E CQC", which publishes the AM bank too.
  The sandbox network refuses that host, so the maintainer downloads them.
- `sources/` holds the Ministry bank (`DomandeB.pdf`) and the **Code**
  (`285_1992.pdf` is the full Codice della Strada, with articles in full;
  `nuovo-codice-strada-2024.pdf` is only the 2024 amending law and mostly
  cites article numbers rather than quoting them). `pdftotext -layout` then
  grep is the fastest way in: art. 171 settles helmet questions, art. 172 the
  seatbelt and child-restraint ones.
- **The SIDA manual is at `private/Manuale.pdf`**, with `Manuale-reduced.pdf`
  and a ready text extraction, `private/Manuale-text.txt`, beside it. That
  folder is GITIGNORED and untracked, which is why it is easy to miss when
  looking only in `sources/` (this cost a "no access to the manual" answer on
  2026-09-15). It is a copyrighted textbook: consult it, never paste its
  wording into the app, and keep it out of git.
- Precedence when they disagree: the Ministry bank decides the answer, the
  Code decides the rule, the manual is the teaching gloss.
- **`Può` said of a DRIVER is permission, not capability.** Flagged as ambiguous
  on 2026-09-17 (18737, "il conducente di un veicolo pesante *può* tenere un
  comportamento che è causa di insofferenza"): the reviewer read it as "is able
  to", which would make it trivially true. The flag was defeated rather than
  marked, on the topic's own usage. Topic 16 has 60 statements containing
  *può*, and the split is clean: with a PERSON as subject it is always
  permission and the answer turns on whether the conduct is allowed (18723
  throwing objects, 18725 weaving past a queue, 18736 using the vehicle's
  power, 18739 skipping caution, 18749 slaloming, 18750 and 18751 the
  sidewalk, 18716 and 18829 granting a permission); with a THING or a
  situation as subject it is possibility (18688 priority *può cambiare*, 18698
  moving a sign *può comportare pericolo*). Check the sibling statements on the
  card before calling a modal ambiguous: they settle the register.
- **A claimed topic is not done until its review has been read against the
  manual.** Asked for by the maintainer on 2026-09-18, after five topics had
  been claimed on the bank alone. The claims pipeline checks that a paragraph
  ANSWERS a statement the way the Ministry marks it; it says nothing about
  whether the paragraph is TRUE, and the split passes add sentences that were
  inferred from a FALSO answer, which is the exact guess the bullet above
  warns against. The first cross-check of the eleven completed topics found
  thirteen real errors, three of them contradicting the very statement the
  sentence was claimed by (one vest per occupant, 24014 FALSO; paper slip no
  substitute for the disc, 23621 FALSO on the minutes; B1 to B a full exam,
  24536 FALSO on a theory supplement). `python3 scripts/sida_extract.py NN
  OUTDIR` writes the manual's chapter for the topic; give it and the review to
  a reader for contradictions; settle each by precedence, bank over Code over
  manual, and CHECK THE CLAIMED STATEMENT before changing a line. The
  procedure and the first pass's results are in `docs/CLAIMS-ROLLOUT.md`.
- **Chains are never a standing duty, and the notes now say so** (flag 21519,
  2026-09-21). The reviewer asked "I thought all cars were required to have
  chains available?", which is a belief an Italian holds as readily as an
  American, so the correction went into BOTH halves of topic 01 rather than
  into a US-only note. Art. 6 c. 4 lett. e) lets the road authority prescribe
  by ordinance that vehicles fit winter tires or carry chains on board, and
  art. 192 gives police the power to stop a vehicle without them only *quando
  questi siano prescritti*. So the duty exists where an ordinance creates it
  and a blue circular sign announces it, and nowhere else. The pass board of
  card 4295 is an INDICATION sign: it reports and advises. That is the whole
  card, since 21517 (winter tires compulsory) and 21518 (a ban on vehicles
  without chains) are FALSO for the same reason.
- **A sign's own test and the ROAD's rule are two different things** (flag
  21635, 2026-09-21). The reviewer read *strada riservata ai soli veicoli a
  motore* and expected motorcycles to be excluded, because topic 01's bullet
  stopped at "bicycles and other engineless vehicles are barred". The sign
  asks one thing, whether there is an engine, and the car in the symbol stands
  for the whole class rather than for cars alone, which is what card 4309
  tests from both sides (buses allowed, a truck not banned, not reserved to
  taxis, not a car park). The size limit is real and comes from art. 175 c. 2
  a), which bars mopeds, motorcycles under 150 cm³ and motorcycle combinations
  under 250 cm³ from these roads: topics 16 and 21 already teach that list, so
  topic 01 names the limit and says where it comes from rather than repeating
  it. When a reviewer is confused about what a sign covers, check whether the
  restriction they have in mind belongs to the sign or to the road.
- **Name the figure the trap BORROWED, not just the one it is not** (flag
  21698, same day). The lay-by sign sets no time limit and the statement
  invents a three-hour one, but three hours is a real autostrada figure, for
  an emergency stop in the emergency lane (art. 176 c. 6), beside the
  twenty-four hours for leaving a vehicle in a service area (art. 175 c. 9).
  Both were already taught, in topics 07 and 21, and both are on the Reference
  page; what was missing was the connection at the point the reader meets the
  trap. The reviewer asked for exactly that contrast. The same pass fixed a
  real error underneath it: the Italian explanation called the bay a *sosta*,
  where the card's own VERO statements say *fermata*. Read the sibling
  statements before writing an explanation, since they define the terms the
  card is using.
- **When the official answer is legally right and bad driving advice, say
  both** (maintainer, 2026-09-25). 22547 and 22650 are FALSO because
  art. 149 measures the safe distance only to the vehicle AHEAD, so the Code
  makes nobody answerable for the follower's gap. The notes had turned that
  into "you are not required to check the vehicle behind", which the
  maintainer rejected as untrue on the road: watch the mirrors, and if
  tailgated keep to the limit, leave more room ahead and let the vehicle pass.
  Topic 09 now has one `**How the exam phrases it.**` block, which carries
  both claims and opens "According to the answers to the Ministry's exam questions, ...",
  then says plainly that this is bad driving advice but the answer to give,
  then the safe practice (do not exceed the limit, you may drive a little
  slower, let the vehicle pass), in both halves. The two bullets that stated
  the Code's definition were removed at the maintainer's word as not to the
  point, and the two statements carry
  the same caution at the end of both explanations and as `warn`/`warn_it`, so
  they appear on the Ambiguous tab at every level and with the 🤔 at the first
  two. 22561 ("commisurata anche al tipo di veicolo che segue") was
  included at first and taken out the same day at the maintainer's word: the
  follower's TYPE changes your gap neither in law nor in practice, so its
  FALSO needs no caution. The pattern for the next such case: keep the official answer
  unmistakable, narrow the claim to what the Code actually says, and never
  let a legal technicality read as driving advice, for either audience.
- **The added-clause trap is MARKED on 241 FALSO statements** (`clause:
  {text, kind}` in questions.json, 20261003c, maintainer's request of
  2026-09-26 after flags 23773 and 23774: "a classic trick question with a
  true statement invalidated by a clause... warn the user about each
  question that is part of this pattern"). A reader pass over all 3,564 live
  FALSO statements, rubric in `docs/clause-trap/RUBRIC.md`, decisions in
  `docs/clause-trap/decisions.json`; four shapes, an extension (*ed anche la
  fermata*), an absolutizer (*sempre*, *in ogni caso*), a false condition
  (*purché*, *ma non*), a false restriction or reason (*solo*, *in quanto*).
  Both explanations end with one fixed sentence pair naming the clause, and
  `validate_data.py` checks the text is verbatim in the statement and the
  sentences are present. Readers disagreed on *solo* until shape (d) was
  written down; the rule is that a narrowing word on a true claim counts, a
  swapped condition or subject does not, two faults at once does not. **The
  clause is NEVER marked visually, at any level, before or after the answer**
  (maintainer, 2026-09-26). The warning lives in the explanation sentence
  only; the field exists so the validator can check the sentence and so the
  set can be listed, and nothing in the app reads it. Glossary rule 62.
- **An explanation must argue about ITS OWN statement (reading pass,
  20261004j).** Flag 24441 found an explanation ending "and why 'useless in
  summer' marks the false variant", words from a sibling on the same card.
  Thirteen readers then read all 7,106 live statements against
  `/outputs/rp/RUBRIC.md` (sibling wording or "the false variant" / "this
  card's traps"; a wrong verdict or rule; EN and IT teaching different
  content) and 199 explanations were rewritten in both halves. Real errors
  surfaced with them: 24014 still said one vest per occupant, 23858 and
  23860 said mopeds under 150 cc, 23489 allowed passing a stopped tram
  "where safe", 20797 called the bus-stop marking yellow and black, 25024's
  Italian said *sequestro* where the English said confiscation (art. 193:
  the vehicle is seized and can end up confiscated; both halves now say
  that). Do not write an explanation that refers to "the false version",
  "the trap answer" or "this card": the learner reads one statement.
- **Explanations render `*italics*` and `**bold**` (20261010h).** Every
  explanation path (study card, the EN pill and twin, the mock review, the
  keep-missing rows) goes through `explHtml`; until then eleven
  explanations had printed their asterisks literally. The 63 explanations
  in topic 22 that list the four license measures now give each its
  Italian name in English (withdrawal, *ritiro*; suspension,
  *sospensione*; revision, *revisione*; revocation, *revoca*), at the
  reviewer's request on 24611. `scripts/check_expl_markup.js`, 4 checks.
- **An explanation may LINK INTO THE NOTES (20261010n, maintainer,
  2026-10-04, flags 18625 and 19088).** `[words](notes:domandeb_images/X)`
  in `explanation` or `explanation_it` is drawn as a link (`explHtml`,
  `a.expl-notes`) that opens the topic review at that figure
  (`openNotesAtImage`: the card's own topic when it holds the figure,
  otherwise the first topic that does). Use it where an explanation names a
  sign or panel other than the one pictured, since the explanation cannot
  show it: 18625 links the trailer panel, 19088 the locomotive triangle,
  the countdown panels and the gate triangle. `validate_data.py` fails on a
  target that is not a figure in both halves of some review, and on English
  and Italian explanations linking to different figures (proved by
  sabotage). The look-alike open item below should use these links.
  `scripts/check_expl_markup.js`, 6 checks.
- **The explanation pass (started 2026-10-04, flag 19125: "our explanations
  NOT being pedagogical").** Every explanation is read against
  `docs/explanation-pass/RUBRIC.md` (bare negation, swapped element not
  explained, undefined key term, penalty with no real consequence,
  one-directional membership list, wrong or off the point) and the failures
  are rewritten in both languages, with links into the notes for a sign
  other than the one pictured. One rewriter and one independent checker per
  chunk; `scripts/explanation_pass_apply.py EPDIR CHUNK...` applies only
  what the checker accepted or corrected and what passes its mechanical
  checks. **ONE TOPIC AT A TIME, at the maintainer's word**: run a topic,
  write `docs/explanation-pass/results/NN-proposed.md` with every before
  and after, show him the counts, examples and the readers' problems, and
  apply and commit only on his "apply". A fan-out over all topics was
  started and stopped. Done: 01 to 03 (602 rewrites, 20261010p, applied
  before the rule), 04 (80, 20261010q), 05 (124, of which 57 link-only,
  20261010v), 06 (31 rewrites from the draft plus a links-only reading of
  the rest, 14 links, 20261011p), 07 (75, of which 34 link-only,
  20261011s), 08 (66, 20261011t), 09 (13 draft rewrites re-checked, plus 4 links,
  20261011u), 10 (24 draft rewrites re-checked, 3 corrected by the
  checker, plus 12 links from a links-only reading of the rest, and two
  more fixes by hand: 23473 no longer names the exam, 23491's autostrada
  example was impossible there; 20261011w). 11 (70, of which 2 link-only, 7 corrected by
  the checker; four name the untested autostrada 100 km/h for a truck or
  motorhome over 3.5 t and up to 12 t, art. 142 c. 3 g, at the maintainer's
  word; 20261012a). 12 (31 draft rewrites, 2 corrected by the
  checker, 17 links, and 23792, 23718 and 23702 rewritten by hand;
  23618 and 23621 had said a time on paper is not valid, which the notes
  and the manual contradict; 20261012g). 13 (85, of which 13 link-only, 2 corrected by the
  checker; 22823, 22836, 22889, 22778 and 22794 had been wrong; 22689 no
  longer claims a ban on two-tone horns, which no source states, and
  23015 and 22942 were reworded by hand; 20261012n). 14 (17, of which 6 link-only, 4 corrected by the
  checker, and 24166's daytime-running-light exceptions added by hand;
  20261012o). 15 (37, of which 13 link-only, none corrected or
  rejected; 21218, 21219 and 21222 had listed a "distinctive badge" as a
  third recognition mark, where art. 12 c. 5 gives the uniform and the
  paddle; 21069 and 21055 corrected; 20261013c). 16 (90, of which 14 link-only, 2 corrected by the
  checkers; work machines carry up to three people including the driver
  (art. 58), the helmet duty on a quadricycle follows the open body
  (art. 171 c. 1-bis), the autostrada admits motorcycles of at least 150
  cm³; 18835 rewritten by hand to the 1.5 m rule for cyclists of art. 148
  c. 9-bis, which the notes already stated; 20261013d). 17 (16, none link-only, 4 corrected by the checker; 24859 had
  misstated art. 189, whose c. 3 asks to avoid obstructing traffic only in
  a damage-only crash; 24911 and 24934 left alone, no source giving the
  reason behind the rule; 20261016e). 18 (36, none link-only, 1 corrected by the checker: 24783
  had claimed a left-parked vehicle's right door opens toward traffic;
  nine statements on card 4623 argued from "this series" and now state
  the defect-or-protection rule itself; 24785's full-throttle sentence
  dropped at the maintainer's word as unsourced; 20261016g). 19 (21, none link-only, 2 corrected by the checker; the
  seatbelt exemption list given in full, the child-restraint conditions
  each given their reason, the boot and glove features in both
  directions; 20261016h). 20 (62, none link-only, 2 corrected by the checker; the eight
  "not caused by X" brake statements now define the named part; 25357
  no longer names suspension adjustments as a remedy for overloading;
  25443 says "in general" no automatic tensioner, as the old text had;
  20261016i). 21 (101, none link-only, 4 corrected by the checker; the
  panel cards describe and link the panel each statement confused with
  the pictured one; 24098 and 24012 state facts no source confirms
  (trailer stripes over 3.5 t, the vest's colors), left as they are;
  24089 and 24094 have no reason in any source; 20261017a). 22 (34, none link-only, 2 corrected by the checker; 24639,
  24645 and 24647 had denied the 2-point bonus per two clean years up
  to 30 of art. 126-bis c. 5, which the review states (a course still
  stops at 20); 24675 left alone, the holiday-ban threshold for heavy
  trucks being in no source; 20261017b). 23 (34, none link-only, 3 corrected by the checker; 31056 had
  called any alcohol before driving illegal and 31045 had called
  yielding to a passenger a traffic violation; 24986's force majeure
  example is now the review's earthquake or flood, not a mechanical
  failure; 20261017c). 24 (16, of which 1 link-only, 1 corrected by the checker;
  25085 had denied that flashing the high beams may replace the horn,
  which art. 156 allows outside built-up areas day and night and
  inside them at night; 25164 had called practice forbidden on the
  autostrada, which art. 122 c. 5-bis requires; 20261017d). 25 (61 of the drafts' 62 rewrites, 23050 refused as much
  shorter than its original, 2 corrected by the checker; a links-only
  reading added 20 yield-sign links and 13 more went into the drafted
  rewrites that name it; the review's worked example 2 called D a bus
  where figure 4483 labels it AUTOCARRO, corrected to truck in both
  halves; 20261017e). **The explanation pass is FINISHED over all 25
  topics as of 2026-10-17.** Open from it: the pilot-report problems
  for 01 to 03, 20597's missing end-of-autostrada figure, 24098 and
  24012 in topic 21 (facts no source confirms), and the figures the
  notes lack listed above. **A missing link is a failure of its own since topic 05**
  (rubric test 7, maintainer, 2026-10-04): an explanation naming a figure
  other than the card's own must link it. Topics 01 to 04 and the saved
  drafts were read before that rule and need a links-only reading
  (`explanation_pass_apply.py --links-only` refuses any change of wording).
  Links-only done: 01 (31 links, 20261010w), 02 (62, 20261010y), 03 (59,
  20261011m), 04 (45, 20261011o). The links-only readings are FINISHED;
  the full pass resumes at topic 06. Figures the notes lack, found
  by that reading: the autostrada entrance sign and its green symbol, the
  end signs crossed by a red stripe, the green SOS pull-off, the pharmacy
  cross, the T-junction triangle, the bus disc of a lane sign, a dashed
  line running beside a continuous one (23568).
  `scripts/explanation_pass_report.py` writes the NN-proposed.md file. Drafts written before the stop and
  to be reused: 12, 25 (06, 09 and 10 are applied) (09 and 25-1 also checked), saved in
  `docs/explanation-pass/drafts/`. `scripts/explanation_pass_packets.py
  EPDIR` rebuilds the packets (same chunks, verified), so copy the drafts
  into EPDIR's `out/` and `ver/` and carry on. **PAUSED at the maintainer's
  word on 2026-10-04**; see "To do" below. Problems the readers reported for 01 to 03 are in
  `results/pilot-report.json` and are NOT yet resolved (19131 and three
  siblings on passing a moving tram, 21305, 21715, 21719, 21533, 21538,
  21749 to 21759, 19083).
- **The car-symbol ban is NOT "the autoveicoli class" (20261010r, flag
  19712).** Card 4120's explanations and topic 04 said motor tricycles and
  quadricycles "belong to the autoveicoli class", which contradicts art. 53
  and 54 and topic 16 (they are motoveicoli). The sign bans every
  autoveicolo AND motor tricycles and quadricycles; the manual (4.1.15)
  lists them separately. The test now taught is "a motor and more than two
  wheels". Topic 04 also gained a bullet: no sign bans mopeds alone; they
  are stopped only by the empty red ring and DO NOT ENTER, and a two-wheeled
  moped passes the bicycle, motorcycle and motor-vehicle bans (19670,
  19688, 19706, 19519, 19537).
- **The bank repeats statements across cards, and that is the Ministry's
  doing (flag 20571).** 20555 and 20571 are the same sentence on cards 4196
  and 4197, which carry the same figure (4198 is a third); both are in the
  April 2025 publication. Not an extraction error.
- **Tons and kilograms (20261011v, flag 24572).** The bank writes one
  mass as 3,5 t or 3.500 kg. Topic 16 says so where masses first appear
  (with the US pound equivalent, in English) and topic 22 says it again at
  the license categories; the Reference page's mass category carries an
  English note. Explanations that turn on a mass may give both units.
- **There is no "light tricycle" (20261010i, flag 18556).** Art. 52 makes a
  three-wheeler within the moped limits a moped (*ciclomotore a tre
  ruote*), and art. 52 c. 4 makes one over any limit a motoveicolo. So the
  three-wheelers split the way the quadricycles do, and topic 16 now says
  so in a bullet after the motor tricycle, in both halves.
- **The bank's SILENCE is not evidence that a rule does not exist.** The bank
  tests a rule's misapplications far more often than it states the rule, so a
  sweep that finds only FALSO statements on a subject proves nothing on its
  own. This cost a wrong answer on 2026-09-17: all three live statements
  linking a U-turn to a line are FALSO (22934, 22935, 22942), from which I
  concluded the centre line does not govern a U-turn and proposed deleting
  that clause from topic 13 and from 22934's explanation. The manual settles
  it the other way in one sentence, section 10.1.3: a continuous centre line
  may in no case be crossed, `nemmeno per l'inversione di marcia se la strada
  e a doppio senso`, and 10.1.4 repeats it for the double line. The review was
  right and the deletion would have removed a real rule. Read the manual
  BEFORE concluding that a rule the notes teach is unsupported; that is what
  it is there for, and grepping `private/Manuale-text.txt` takes seconds.

## Useful docs
- `docs/AI-CONTENT-REVIEW-PROMPT.md` — the reusable per-topic content-review prompt
  run by a second agent ("fable"). It edits `questions.json` + the topic review,
  rebuilds, validates, and appends learnings to `docs/review-glossary.md`
  (shared, append-only). Topic 16 was the pilot; topics are reviewed one at a time.
- `docs/BANK-2025-DIFF.md` — our bank compared against the April 2025
  publication: what changed, the 41 withdrawn statements with a reason for
  each, and how to repeat the comparison. Read it before re-extracting the
  bank or wondering whether a figure is still tested.
- `docs/CLAIMS-ROLLOUT.md` — the schedule for claiming the remaining 22 topics:
  which are done, the measured weak-landing count that sets the order, the
  lighter pass agreed for the 10 picture topics, and the snippet that
  regenerates the numbers. Read it before starting a new topic.
- `docs/review-glossary.md` — agreed IT→American-English term mappings, recurring
  patterns, and style decisions. Read before content/translation work.
- `docs/LEARNER-REPORTS.md` — what people who have actually taken the exam say
  about preparing for it, and what each account changes here. The first entry
  (2026-09-21) is a self-taught non-native speaker who passed 29 of 30, and it
  is the closest thing to an outside test the study loop has had: his own
  method sorts every miss into a language problem and a rules problem, which
  is the Final Stretch page's two groups arrived at independently. The source
  posts are copyrighted and live in `private/learner-reports/`, gitignored, for
  the reason the SIDA manual does. **Measure a claim against the bank before
  acting on it**: his eighteen "trap words" turned out to be nine real ones and
  five that point the other way, and *salvo* leans VERO at 29% FALSO against a
  bank that is 50.2% FALSO.
- `docs/PRE-PUBLIC-CHECKLIST.md` — remaining steps before making the repo public.
- `docs/american-guide.md` — background and language preparation for an American
  learner. The PROCESS lives in the app's own How-to panel, which is the
  authority and is more current; this file is corrected against it, never the
  other way round (it claimed a six-month foglio rosa until 2026-09-16, where
  the app has said twelve since 2021).
- `docs/STUDY-EFFICIENCY-PLAN.md` — WHY the study loop is shaped as it is: the
  redundancy measurement behind not shrinking the bank (6,848 of 7,147
  distinct), why credit flows DOWN the levels and not up, and the one open
  idea, time-based review near the exam. The loop's BEHAVIOR is described in
  README.md and in the app's own How-to, not here.
- `docs/ABRIDGE-PROMPT.md` — background/rationale.
- `docs/SYNC-AND-STATS-TODO.md` — the anonymous most-missed analytics, which
  is **not built**: no `stats.php`, no `sendBeacon` anywhere. Encrypted sync,
  planned alongside it, shipped in June, and what it became is recorded at the
  foot of that file. The one open decision is D5, SQLite or JSON with `flock`
  for the counter store.

- **Reviewer flags of 2026-10-23 (20261023a).** 25030: *premio* means both
  a reward and an insurance premium, and the fund is neither; the explanation
  names the double meaning, says the fund is financed by a levy on every RCA
  premium (SIDA 19.6.5), and topic 23's fund bullet says the same. 25040:
  the limits cap what the insurer pays, never what the driver owes; the
  explanation and topic 23's limits bullet say personal liability has no
  ceiling, so the excess is the responsible driver's. 18520: a sidewalk with
  parking stripes is still a sidewalk (art. 3 n. 33); art. 158 c. 1 h) bans
  parking on it *salvo diversa segnalazione*, so the authority may mark bays
  along part of a wide one and the rest stays for pedestrians. Said in the
  explanation, in topic 16's sidewalk bullet and in the vocabulary note.
  22860 (unsent flag in his export of the same day): the explanation now
  opens on the key word *continua*, says the same sentence with
  *discontinua* would be true (20714 VERO), then gives the manner of the
  turn (20261023i).
  20588 (flag batch 2026-10-23, second file): the explanation opens on
  "this sign imposes no duty to stop", you stop only when yielding requires
  it, and an unconditional stop is the STOP sign's alone (20261023j).
  Third file of the day (20261023k): 19549 opens on the black car
  standing for every motor vehicle with more than two wheels, as the single
  car does in the ban on all motor vehicles (linked), the difference being
  the two-wheeler exception; 19859 says no sign ends a danger, a danger's
  reach being the extent panel's job (linked), and topic 04's via libera
  bullet says the same; 20253 says *passaggio* means passing by an
  obstacle, not turning, as does topic 02's bullet; 21239 says the E 55
  panel appears inside advance and direction signs and along the route as
  confirmation, as does topic 01's bullet.
  Fourth file (20261023l): 21509 had said chains are never required on
  all four wheels, which contradicted 25253 (a 4x4 takes them on all four);
  both now say the drive wheels, two on most cars, four on a 4x4, and topic
  01's pass-board paragraph says the same. 21397 describes the green
  entrance sign in words and links the same symbol on blue (4296), the
  bank having no picture of the green one. 21668 and topic 01's principle
  paragraph say an indication sign excludes a vehicle only by reserving a
  road. 20884 contrasts moving toward the center (true with any line) with
  crossing it (broken only, 22860). 20958 says there is no emergency
  parking zone, only a sosta di emergenza of art. 157 capped at three
  hours by art. 176 c. 6.
  **Flags of 2026-10-24 (20261024c).** 21056: the lights come on before the
  half-barriers lower and flash through the train's passage; the error is
  *si accendono* in the opening phase, which ends the alert. 22364 and
  22424 lost their "the figure X is ..." sentences (maintainer: not helpful)
  and teach the new-driver limits and the moped's 45 everywhere. 24090 lost
  "once you see what a trailer is". 24350 separates situations (none
  exempt) from persons (art. 172 c. 8, listed). 24573 and topic 22's BE
  bullet say a minibus is a small bus over nine seats, and a nine-seat van
  is an *autovettura* that BE covers.
  **Flags and a bug report of 2026-10-25 (20261025a).** 24915: *panno*
  (cloth) was underlined at Solo italiano by the Glossario entry *panne*,
  whose final-vowel wildcard reached it; the bank never writes *panne* (its
  three counted hits were *panno* and *panni*), so the entry was removed as
  the dead-weight rule requires. Do not add vocabulary terms to the
  glossary matcher's `known` set to fix such a case: measured, it would
  drop *ammortizzatore* from 24 hits to 0, since the vocabulary holds
  inflected forms as entries of their own. 24729 no longer calls the swap
  "the classic error". 24686 says the BS is issued after the local medical
  commission's assessment (art. 116 c. 4, 119 c. 4), which is why its term
  is shorter. 24124 unchanged: the Glossario already explains the
  tongue-jack wheel. How-to (bug report): a "Study the theory first"
  paragraph in the shared opening (the medical certificate is valid three
  months and the application gives six for the theory, while the levels
  can take longer, so see the doctors once at the weak spots and mocks),
  and both routes' note step says to get the note only when ready to file
  within three months. The note's own validity is stated by no source
  found, so the step ties the timing to the certificate's three months.
  **"Study the theory" is step 1 of both routes since 20261025h** (after
  five rewordings the same day: the maintainer rejected the app's internal
  names, then a tour of the stages as too verbose, then the 7,000 count
  since abridged is the default, and gave the closing sentences himself).
  It reads: the certificate is valid 3 months and the application gives 6
  for the theory; the questions here, in English and then in Italian,
  usually take longer, so do them first; once you can answer them all
  correctly in Italian without English you should be ready to book the
  medical, and certainly by the time the app suggests mock exams. Each
  route now has NINE steps; `check_howto_tabs.js` counts nine.
  **Enroll warns about schools with no language support (20261025k,
  maintainer, 2026-10-25)**: a school can be expensive and of little value
  to a student with limited Italian, so shop around and ask for a textbook
  in English as well as Italian and an instructor who speaks English well
  enough to answer questions. School route only. **English face only**
  (20261025m, maintainer's question): the Italian face is for native
  speakers, and the Italian Enroll step is unchanged from before: the
  teenagers sentence was dropped too (20261025n, maintainer: a native
  Italian already knows it).
  **Flags of 2026-10-25, evening (20261025u).** 18427: a bicycle may ride
  through a pedestrian area (art. 3 n. 2 names velocipedi) but not along a
  pedestrian path, the blue round sign, where it is pushed; said in the
  explanation (linking 4176), topic 16's pedestrian-area bullet and topic
  02's pedestrian-path bullet. 18593 defines the work machine (art. 58:
  self-propelled or towed, road or site work, 40 km/h, three people) and
  the exceptional one (art. 114 c. 3: over the general size or mass
  limits), B for the first and C1 for the second (art. 124 c. 1). 18821:
  the Code has no stop-for-school-bus rule (confirmed: the Code's only
  scuolabus lines are exemptions from bans; the manual's is a sign), so
  the English explanation and a For US drivers note in topic 16 contrast
  the American stop-arm rule. 19150 says the crossing sign speaks of
  pedestrians of any age and does not single out children.
  **Flags of 2026-10-26 (20261026a).** 20341: every mandatory sign is a
  blue circle with a white symbol, without exception (the end-of-obligation
  signs are the same circle with a red stripe), and the reverse does not
  hold, since prohibition signs are round too, white with a red ring; said
  in the explanation and in topic 02's first bullet. 20910 opens on the
  statement contradicting itself: a one-way road has no second direction
  to divide. 20989 says what the invented condition is: the green light
  allows the turn on any carriageway, and lane lines only govern where the
  vehicle is placed before it. 21626: the advised speed is a ceiling in
  good conditions (21624 VERO, 21633 FALSO: slower is allowed), so the
  reviewer's reading, that it also advises against going slower, was
  defeated; the device that recommends a speed to HOLD is the green-wave
  lantern (4257, linked). **Three figures replaced by vectors (flags
  21450, 21461, 21523: "the image is small").** 4288, 4289 and 4296 were
  186x114, 187x119 and 104x171 jpegs from the PDF, which embeds every
  figure at 200x200, so no sharper raster exists; at the 2x resolution
  ceiling they rendered blurred at 372 px or, for the tall 4296, 128 px
  wide. 4296 is now the Commons II 345 vector (Gigillo83, PD); 4288 and
  4289 are drawn for this app as SVGs with `<text>` after the Ministry's
  II 235 and II 233 layouts, carrying the bank's own place names (Bologna
  and Linate, Milano and centro), which is why the Commons vectorizations
  of those figures (Napoli and Bari, Sora and Napoli, with lettering as
  outlines) could not be adopted; the airport glyph is Commons II 116
  (Gigillo83, CC BY-SA 3.0), credited in IMAGE-CREDITS.md. A tall VECTOR
  figure now reaches 260 px (`img-vector`, `.img-tall.img-vector` in
  style.css): the 210 cap serves the low-resolution composites, and 4296
  rendered 119 px wide under it beside 400 px boards. Thirty tall SVGs
  grow, none shrinks. Measured with Playwright at 390 and 1280 px: 4288
  392x240, 4289 378x240, 4296 147x260. A drawn figure is an SVG with text,
  so a later edit of a name is a text edit, not a redraw.
  **Flags of 2026-10-28 (20261028i).** 20341's explanation was cut to the
  rule (a blue circle with a white symbol is mandatory; round alone is not,
  since prohibition signs are round too). 22314 reads "empty", not
  "unloaded". 23089: *alcun* after *non* or *senza* means any, one
  negation, while the plural *alcuni* means some; all 18 live statements
  with *alcun* or *alcuna* now carry ONE English sentence, "After *non*,
  *alcun* means any, so *non ... ad alcun veicolo* means to no vehicle at
  all" (before the clause-trap pair on 20302), and the 27 with the plural
  *alcuni* or *alcune* carry "The plural *alcuni* means some. Only the
  singular *alcun*, after *non*, means any." (20261028y, maintainer: not
  verbose, and for American learners; the Italian halves carry nothing,
  since a native reader needs no note on it), and "Words in this question" now lists
  every alcun entry even unlooked-up and common: a vocabulary entry may
  carry `"always": true` (20261028z, maintainer: *alcuni* was missing under
  a statement that turns on it). The nine entries built on alcun carry it,
  including the phrases *dare la precedenza ad alcun veicolo* and *senza
  alcun limite*, which the highlighter matches in place of the single word;
  the plural glosses read "some (plural, not any)". `validate_data.py`
  fails an alcun entry without the flag (proved by sabotage);
  `scripts/check_always_words.js`, 3 checks, the
  `parse` grammar point "Two negative words, one negation" gained *non ...
  alcun*, and the vocabulary gloss of *alcun* says so. 23344: *impegnare
  l'incrocio* is entering, not getting through; its explanation says so,
  the Glossario entry *impegnare* names the opposite (*sgombrare*,
  *liberare*, *disimpegnare*), and topic 25's opening gained a paragraph in
  both halves on *impegnare*, *concludere la manovra* and *sgombrare*.
  **Topic 11's "How to remember the numbers" is a rule, not a list
  (20261028k, maintainer, 2026-10-28: the limits are odd tens, and a
  condition tends to lower them 20 km/h).** The section now gives the
  series 150, 130, 110, 90, 70, 50, the four standard limits, a sign raising
  one step (150, urban 70), rain lowering one step on the two fastest roads
  only, fog at 50, towing at 70 on every extra-urban road, then the figures
  outside the series to memorize: the new driver's 100 on the autostrada
  (the 90 on the principale fits), 80 for towing on the autostrada and for a
  non-light quadricycle, and the vehicle limits 45, 40 and 15. Both halves.
  The words "ladder" and "learn by heart" were tried first and are banned by
  `check_review_english.py`; the section says "series" and "step".
  **The same summary is on the Reference page (20261028l, maintainer)**:
  `remember` on the `speed` category in reference.json (`en`, `it`,
  `linesEn`, `linesIt`), drawn by `refRememberHtml` as a CLOSED disclosure
  "How to remember the speeds" under the first speed category on screen,
  so the by-vehicle chip alone still shows it; never while searching or on
  the missed-figures chip. Closed because it names every figure and the
  values may be hidden for a self-test. A change to the rule is two edits,
  topic 11 and reference.json. `scripts/check_speed_remember.js`, 9 checks
  in each face, including that every figure it names is a speed row.
  **A grid figure leads both (20261028m, maintainer: "some kind of
  graphic")**: `review_media/speed-limits-en.svg` and `-it.svg`, road types
  against conditions (where signed, standard, rain, dense fog, new driver,
  towing) with the vehicle limits below, each cell colored by how the figure
  is found (green by the one-step rule, gray unchanged, orange outside the
  series and to memorize, dashed where it does not apply). Both files are
  drawn by `scripts/draw_speed_limits.py` from one table; edit there and
  rerun. It opens topic 11's "How to remember the numbers" in each half and
  the Reference box. A figure with words on it is two files, so caption
  pairing now keys a file by `captionKey`, which treats NAME-en.svg and
  NAME-it.svg as one figure. Both files are in the worker's precache. The
  SIDA manual's own table (fig. 3038) lists the limits and was not used:
  it is copyrighted and shows no pattern. At 390 px the figure fits with
  no sideways scroll, but its legend text renders small.
  **Fog is two rules, not one figure (20261028n, maintainer, 2026-10-28:
  "strange that dense fog only applies to autostrade and extraurban").**
  On every road art. 141 obliges you to slow to what you can see; only on
  the autostrada and the principale may a figure be posted, a temporary cap
  of 50 with visibility under 100 m (22454: *possono essere imposti*). The
  figure's fog row first marked the secondaria and town "does not apply" and
  colored the 50 as the one-step rule; the 50 is now purple ("Cap that may
  be posted") and those two cells read "Slow to visibility", with the
  legend on two rows. The fog bullet in topic 11 and in the Reference box
  says both rules. The 50 is not in art. 142's text, which has the rain
  rule only.
  **A tap on a concept figure opens it full screen (20261028o, maintainer,
  2026-10-28: the grid's labels are small on a phone, and the vehicle
  limits stay in the one figure).** `openFigureViewer`, for every
  `review_media/` figure in the notes and for the Reference box's figure
  (`FIG_ZOOM_SEL`): a dark overlay with the image at no less than 680 px
  wide, so on a phone it is larger than the screen and pans, and up to
  1100 px on a desktop. Any tap, the ✕ or Esc closes it; Esc is caught in
  the capture phase so it does not also close the notes. The sign drawings
  are not included. A "Tap to enlarge" tooltip marks the figures.
  `check_speed_remember.js` covers open, Esc and tap to close; measured in
  Chromium at 390 px (image 680 px, pans) and 1280 px (1100 px).
  **It zooms by its own gestures since 20261028p** (maintainer's iPhone
  screenshot: it opened larger than the screen, he had to slide it around,
  and could not pinch it smaller). The figure now opens FITTED to the
  screen, and the overlay (`touch-action: none`) handles pointer events
  itself: pinch or the wheel zooms between 1x and `FIG_MAX_ZOOM` (4x)
  around the fingers, a drag pans a zoomed figure (clamped to its edges),
  a double tap toggles 2.5x at that point, and a single tap on the backdrop
  closes after the double-tap window. Safari's `gesturestart` is cancelled
  so the page beneath does not zoom. A hint line says "Pinch or double-tap
  to zoom". Do not rely on the browser's page zoom for a fixed overlay; an
  installed iOS app does not give it. Measured in Chromium with CDP touch
  events at 390 px: fitted 366 px wide, pinch out to 2.8x, pinch back to
  1x, double tap 2.5x and back, backdrop tap closes with the notes still
  open.
  **The distances have the same kind of box (20261028q, maintainer)**:
  "How to remember the distances" on the `distance` category, with
  `review_media/distances-en.svg` and `-it.svg` drawn by
  `scripts/draw_distances.py`. Three panels: the multiples of 50 m, each
  under a drawing of the railroad countdown panel with that many bars
  (150 for danger signs outside towns and the three-bar panel; 100 for the
  two-bar panel, the triangle's visibility, the gap between trucks over
  3.5 t and the fog cap; 50 for the one-bar panel, the triangle behind the
  vehicle and the rear fog light); the safe distance at each tested speed
  against (speed ÷ 10) × 3; and the short ones (1, 1, 3, 5, 15) with the
  outliers 20 and 500. Any category may now carry `remember` with a `fig`;
  the speeds' box still shows once across its two categories. The figure
  is on the Reference page only, since the distances belong to six topics.
  `check_speed_remember.js` asserts the box, its figure and that every
  distance it names is a row on the page.
  **The distances' figure was REMOVED in 20261028r** at the maintainer's
  word: the formula serves the safe distances better than bars, and the
  other distances gained nothing from a drawing. The two SVGs and
  `draw_distances.py` are deleted; the box stays, text only (`fig` is now
  optional on `remember`). Do not draw it again unasked.
  **The distances' text box was removed too, in 20261028s** (maintainer).
  Only the speeds carry a `remember` box now.
  **An emergency halt is never parking (20261023m, maintainer, 2026-10-23).**
  Topic 21's emergency-lane bullet, 20955 and 23903 now say the three hours
  are the ceiling of a *sosta di emergenza*, not an allowance, as topic 07's
  edge-line bullet and 20958 already did; 23903 no longer names "the quiz".
  **The carriageway and parking (20261023b, maintainer's question the
  same day).** 18467 and 18468 (the carriageway is not meant for parking,
  FALSO) and 23710 (in town, park at its right edge, VERO) look
  contradictory to an American who treats the curb lane as a parking lane.
  Both hold: the carriageway is for driving, and in town you park on it
  anyway, at its right edge (art. 157 c. 2). Said in topic 16's carriageway
  bullet and in those three explanations, in both languages. The side
  parking strip (art. 3 n. 23), marked bays and US hours-based parking
  lanes are tested by nothing and were deliberately left out.
- **"The trick is 'anche'" is wrong where the VERO siblings carry the same
  word (20261007w, flag 22555, 2026-10-02).** In topic 09 nine VERO
  statements read "deve essere stabilito anche in base a ..." exactly as the
  eight FALSO ones do (22542 to 22545, 22555, 22559 to 22561), so the factor
  named decides the answer, not *anche*. Those eight explanations now say so
  in both halves. Twenty other live explanations open "The trick is
  'anche'"; in those the word does add the false clause, and they were left.
  Before naming a trap word, check that the true statements on the card do
  not use it too. The same batch: 20495's explanation and topic 05's STOP
  bullet now say the road with the right of way is the OTHER road, and
  31036 carries a part-by-part reading of the Italian, English only, since
  an Italian reader needs none.
- **`reading` on a statement (20261007y, maintainer, 2026-10-02: "organized
  more pedagogically, like we do in the grammar section").** The reading of
  31036 was first written as prose at the end of the English explanation and
  he rejected that shape. A statement may now carry `reading: {rows: [{lab,
  it, en, main?}], note}`; `readingHtml(stmt)` draws it with the Grammar
  tab's own breakdown (`.gr-parse` rows, the main verb row accented, then
  the note, `*word*` in italics) after the ENGLISH explanation wherever
  that shows (the three levels, the mock review, the keep-missing rows), and
  never for an Italian browser. `validate_data.py` fails unless the rows'
  Italian joins to the statement, exactly one row is `main`, and the note
  ends with a period. This is the sanctioned form for a sentence diagram in
  an explanation; "no grammar lesson at the end of a question" still holds
  for prose. Only 31036 carries one. `scripts/check_reading.js`, 10 checks
  in English, 2 in Italian.

- **Topic 08's arrow panels were reorganized around ONE idea (20261009g,
  maintainer, 2026-10-02: he mixed up the left and right arrows and found
  the section not pedagogical).** The section "Start, continuation, and end
  of a rule" now runs: the one idea (the arrow points toward the part of
  the road where the rule applies), the two forms A and B (upright when the
  sign faces the driver, flat when it stands parallel to the road, which
  the SIDA manual confirms at 8.1.9), how to READ form B (picture the sign
  on the wall to your right and turn to face it: ahead is now on your
  left), a memory aid in a quote block (Left, the rule lies ahead; Right,
  the rule is to the rear; *Sinistra, si inizia; Destra, la regola è
  dietro*), then each figure with two bullets, what it means and what it is
  not. The explanations of 22078 and 22100, the two statements on form B,
  carry the face-the-sign reading. A mnemonic in the notes is labelled as
  one ("To remember ...") and makes no claim beyond the rule it restates.

- **A FALSO statement of the shape "penalty X follows situation Y" must say
  what Y ACTUALLY brings (20261009h, flag 24611, maintainer, 2026-10-02).**
  24611's explanation said when a revocation is ordered and never said what
  driving with an expired license does bring (a fine and the withdrawal of
  the license on the spot, art. 126 c. 11, returned after renewal). The 54
  live FALSO statements naming a measure, points or a sanction in topics 22
  and 23 were then read for the same gap, and 23 explanations gained the
  actual consequence in both languages: a fine and showing the document
  later (art. 180: 24587, 24603, 24612, 24633, 24668), nothing at all
  because the conduct is lawful (24583, 24588, 24602, 24616, 24669, 24670),
  a fine and points (24614 lenses, 24637 disabled space), a fine (24635,
  24666), the registration document withdrawn (24585, art. 78), an
  open-ended suspension (24613, art. 129), a fine and no driving until
  inspected (24676, art. 80), a duplicate (24634), a tax surcharge (24638),
  and for 24598 the real rule, three violations of five points or more in
  twelve months (art. 126-bis). Each fact was read in `sources/285_1992.pdf`
  (`pdftotext` works now that poppler is installed). **No euro amounts were
  written into explanations**: the fines are revised every two years and
  live in `reference.json`, the one place to update. The 49 keyword matches
  in other topics were NOT read; most are *arresto* in the sense of
  stopping.

## To do (the maintainer's list of larger work set aside)

1. **The explanation pass is complete** (all 25 topics, 2026-10-17). What
   it left open: 20597 needs a figure of the end-of-autostrada sign, which
   the notes do not have; the other figures the notes lack are listed under
   "The explanation pass" above; 24098 and 24012 (topic 21) state facts no
   source confirms. The look-alike sign item below is largely absorbed by
   the pass, since the rubric required the other sign to be described and
   linked; a dedicated reading of topics 01 to 08 for it has not been made.
2. **22548** calls 10 m "the classic wrong number", which alludes to the
   bank; drop the phrase.
3. **The problems the readers reported for topics 01 to 03**, unresolved,
   in `docs/explanation-pass/results/pilot-report.json`.
4. **Licensing costs and the private route** (maintainer, 2026-10-14).
   A school's 2026 price sheet is summarized in
   `docs/license-process-draft.md`, notes 5 and 6: about €900 for the theory
   part alone, against the
   How-to's €800 to €1,500 for the whole license. Update the Cost
   paragraphs of both routes once the final total is known, and fill the
   private route's unsourced figures. Add, in the same release, the paragraph on
   choosing a school as an experienced driver (note 7 there).

## Open item: look-alike sign traps in the explanations (maintainer, 2026-09-30)

Review every explanation in the sign topics (01 to 08) for statements that
name a DIFFERENT sign that looks like the pictured one (bike crossing vs bike
path, straight-ahead circle vs lane sign). For each such statement the
explanation must describe BOTH signs in words by what the learner can see
(shape, color, symbol, rider or no rider), say that the resemblance is the
trap, and give a one-line way to tell them apart. An explanation cannot show
a picture, so the words carry it. Do NOT add the look-alike's figure to the
topic review: the maintainer does not want sign shapes mixed inside a topic
unless the topic's own teaching needs it, and a trap question is not such a
need (the bike-path circle added to topic 01 in 20261005p was removed in
20261005q for this reason). The model is 21670 and 20061. The maintainer's wider rule from the same flag:
an explanation teaches why the wrong answer was tempting, not only why the
right one is right. **The same pattern covers look-alike MARKINGS**
(maintainer, 2026-09-30, flag 22942): a true rule attached to the wrong
line. 22942 says a continuous EDGE line (*linea di margine*) forbids a
U-turn, which is FALSO because the line that forbids it is the continuous
CENTER line (*linea di mezzeria*); a reader who knows the rule but not which
line it belongs to answers VERO. So the pass also covers topic 07 and the
line-related statements in topic 13 (edge against center line, broken
against continuous, single against double, white against yellow), and each
explanation names both markings and says which one the rule belongs to, as
22942's now does. Not started; do it topic by topic with readers, as the
reading pass of 20261004j was done.

## Open item: weak spots and "Questions you keep missing" overlap (2026-10-01)

**Settled for the waiting phase in 20261010c** (see "The daily review while
waiting for the exam"): with an exam date entered both feed one daily set.
Outside that phase the two remain as described below.

Since 20261006v both are answerable lists of unfixed misses recorded at
Italiano. They differ in scope (every miss against N or more misses, Italian
only), release rule (2 in a row or 1 at Italiano, against the learner's
choice, default 3) and place (a drill on study cards against rows on the
Statistics page, which was meant to hold numbers only). The recommendation
given was one practice tool and one view: a Settings choice of the weak
spots' release run, and the list made read-only again, hiding what the drill
has released. The maintainer chose to keep both as they are and decide after
using them. Do not merge or change either without asking.

## The public-release check (2026-10-25)

Three independent readers swept the tracked tree before the first public
commit, for personal data, for secrets and infrastructure details, and for
copyright and licensing. What they found and what was done:
- **Personal data.** Two visitors' IP addresses in the access-log notes,
  the maintainer's own itemised school fees in the licensing draft, a dated
  medical appointment, his medical-paperwork sequence, three practices
  attributed to "the maintainer's own school", the attribution and date on
  the anamnestic-note rule, a narrow description of the Facebook poster in
  `docs/LEARNER-REPORTS.md` and his device details were all generalised or
  removed. His study scores and mock results stay as design evidence.
- **Secrets.** Nothing live in any tracked file, every endpoint fails
  closed. `notify.php` now builds the admin link from `SERVER_NAME`, never
  from the client's Host header. `docs/TRUSTED-REVIEWERS.md` no longer tells
  a reader to hardcode a code into a tracked PHP file. `scripts/
  .fixbare_progress.json` is untracked and ignored.
- **Licensing.** About half of `domandeb_images/` are Wikimedia Commons
  vectorizations, some CC BY-SA, which LICENSING.md had described as the
  Ministry's unmodified figures. LICENSING.md now states the three regimes,
  the legal basis for the Ministry bank (L. 633/1941 art. 5) and an
  "everything else we wrote" clause. `IMAGE-CREDITS.md` was filled from the
  Commons API (`scripts/fill_credits.py --online`), its split rows joined,
  `disco-orario.svg` credited (CC BY 3.0, Bouwe Brouwer, derivative Pav03),
  and a note added on the split variants. The attribution now reaches the
  distributed work: `about/credits.html` is generated from
  `IMAGE-CREDITS.md` by `build_topic_pages.py` (`credits_page`), the app
  footer links it beside "About this app" (`ensureCreditsLink`, Italian
  label in STATIC_IT), the topic pages' call to action names it, and the
  landing page's list ends with it. The guide pages have no footer by the
  maintainer's design, which is why the link sits in the call to action.
- **Open source is said in the app (20261025s, maintainer).** A third
  footer link, "Open source on GitHub" (`footer.source`, Italian "Codice
  sorgente su GitHub", `ensureSourceLink` for a stale page), and one
  sentence on the landing page after "free and has no ads", with the
  repository link, saying the code is open source under the AGPL.
- **Numerical Recipes.** `logGamma`, `betacf` and `betaInc` had the shape,
  constants and variable names of NR's `gammln`, `betacf` and `betai`,
  whose licence forbids redistribution. All three and `gammaP` were
  rewritten from the published formulas: Lanczos with the g = 7, n = 9
  coefficients, the continued fractions of DLMF 8.17.22 and 8.9.2 by
  forward recurrence of convergents with rescaling.
  `scripts/check_special_functions.js` compares them with 30 mpmath
  reference values (`scripts/special_functions_ref.json`, 30 digits) to
  1e-12 and with the t and chi-square figures the other checks use.
- **Checks.** `check_lookup_gloss.js` carried a hardcoded sandbox path and
  crashed everywhere else; it resolves the project root like the others.
  macOS has no `timeout` command, so a loop over the checks must not use it.

## Open items (pre-public)
Done, 2026-10-25. The repository was recreated with one commit for the
public release (see `docs/PRE-PUBLIC-CHECKLIST.md`), so every commit hash
quoted in this file before that date names a commit that no longer exists;
the version markers (YYYYMMDD + letter) still identify each change.
