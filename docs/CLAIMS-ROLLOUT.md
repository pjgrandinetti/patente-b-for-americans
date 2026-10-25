# Claims rollout: tracker for the remaining topics

A **claim** is the `<!-- q: 24094 24095 -->` marker on a block of a topic
review's English half. It says: these statements' 📖 button opens THIS
paragraph. Claims replace the heuristic picker, which was wrong or silent for
roughly one statement in six. `CLAUDE.md` holds the mechanism, the tooling and
the rubric. This file is only the schedule: which topics are done, which are
next, and why in that order.

Plan agreed with the maintainer on 2026-09-12.

## Where the work stands

| | topics | statements |
|---|---|---|
| Complete (text topics) | 15 | 3,309 |
| Rules pass done (picture topics) | 7 | 2,717 |
| Picture topics remaining | 0 | 0 |

Complete so far, in the order they were done:

| topic | statements | claimed | absent | blind check |
|---|---|---|---|---|
| 21 Ingombro della carreggiata | 332 | 327 | 5 | 38 of 40 |
| 16 Definizioni stradali | 531 | 521 | 10 | 39 of 40 |
| 13 Norme sulla circolazione | 379 | 375 | 4 | 37 of 40 |
| 24 Consumi e ambiente | 103 | 101 | 2 | 29 of 30 |
| 20 Elementi costitutivi | 284 | 284 | 0 | 39 of 40 |
| 23 Responsabilità e RCA | 146 | 146 | 0 | 32 of 40 |
| 11 Limiti di velocità | 256 | 256 | 0 | 36 of 40 |
| 22 Patenti e documenti | 222 | 220 | 2 | 37 of 40 |
| 14 Uso delle luci | 176 | 176 | 0 | 40 of 40 |
| 12 Fermata, sosta, arresto | 190 | 190 | 0 | 40 of 40 |
| 17 Qualità e condizioni del conducente | 141 | 141 | 0 | 40 of 40 |
| 10 Norme sul sorpasso | 156 | 155 | 1 | 40 of 40 |
| 18 Comportamenti per prevenire incidenti | 126 | 126 | 0 | 39 of 40 |
| 19 Dispositivi di equipaggiamento | 133 | 133 | 0 | 133 of 133 |
| 09 Distanza di sicurezza | 134 | 134 | 0 | 128 of 134 |
| 03 Segnali di pericolo (rules pass) | 662 | 141 | 0 | 35 of 40 |
| 01 Segnali di indicazione (rules pass) | 603 | 62 | 0 | 36 of 40 |
| 04 Segnali di divieto (rules pass) | 502 | 58 | 0 | 29 of 40 |
| 06 Segnali complementari (rules pass) | 179 | 10 | 0 | 40 of 40 |
| 05 Segnali di precedenza (rules pass) | 243 | 81 | 0 | 40 of 40 |
| 15 Segnalazioni semaforiche (rules pass) | 252 | 40 | 0 | 38 of 40 |
| 07 Segnaletica orizzontale (rules pass) | 259 | 61 | 0 | 36 of 40 |

"Claimed" counts every statement of the topic that has a claim, including the
ones whose claim sits in another topic's review. A topic's own file therefore
shows a smaller number, because it also holds claims serving other topics.

### The blind check is a diagnostic, not a grade

Topic 23 returned **32 of 40**, well below the 37-to-39 the earlier topics
returned, and the useful part was not the number but WHERE the eight
disagreements sat: six of them on a single card, 4716 (attention and
distraction), and the two readers split there between `absent` and a block they
plainly did not believe in. Both readers said the same thing in their notes,
independently: the section was four short bullets carrying **54 statements**,
so there was nothing precise for either of them to land on and they guessed
differently. Every gap either reader reported fell on that card too.

So read a low blind score as a map. A disagreement cluster on one card means
that card's teaching is missing, not that a reader was careless, and the fix is
to write the content before arguing about the claims: once the attention
section became fourteen one-rule bullets, six of the eight disagreements
dissolved because both candidate answers had been replaced by a bullet that
states the rule. Two genuine adjudications remained (24972 stayed on the block
that denies the invented alternative, per rule 5b's exception; 24973 moved to
the new "not excluded by anything done after the crash" bullet, which is what
both readers were reaching for).

A second finding from the same pass, now fixed in the script: **the packet was
including statements the Ministry has withdrawn.** Three of topic 23's 149
(25008, 25019, 25020) are retired, so readers spent effort on them and one was
reported as a VERO content gap. Worse, 25008 would have reintroduced the
"areas open to the public" limit that the 2024 reform removed and that the
retirement pass had deliberately taken out of this very topic. `validate_data.py`
catches the claim, but only after the reading is done, so `claims_packet.py`
now skips retired statements outright.

## The pipeline for one topic

The full sequence, as run on 13. Details and script flags are in `CLAUDE.md`
under "CLAIMS are the robust mechanism".

1. `claims_packet.py NN OUTDIR`, then split `statements.jsonl` into slices of
   about 95 and give each slice to a reader with `README.md`, `blocks.md` and
   `toc.md`.
2. Merge the readers' `decisions.json` files and apply them.
3. Build an `xNN` packet for every topic named in `elsewhere`, have a reader
   decide those against the other topic's blocks, and apply the moves. A
   reader who finds nothing better there answers `keep`, which leaves the
   claim where it was.
4. **Split the bundled blocks before trusting the claims.** See the lesson
   below. Re-run `claims_packet.py` against the split file and have every
   statement re-read, since a claim that pointed at a paragraph now points at
   its first fragment only.
5. Mark the topic complete with an empty `decisions.json` and `--complete`.
6. Blind second opinion: sample 40 claimed statements, strip the proposals,
   and have a fresh reader decide them cold. Investigate every disagreement.
7. `claims_gaps.py` for the gaps the readers reported, readers return
   `additions.json`, then `claims_fill.py`. Gaps in other topics get their own
   small packets.
8. **Cross-check against the SIDA manual.** `python3 scripts/sida_extract.py
   NN OUTDIR` writes the manual's chapter(s) for the topic; hand it and the
   review to a reader who reports CONTRADICTIONS (review and manual state a
   rule differently), UNSUPPORTED (review states what the manual never
   mentions) and MISSING (manual teaches what the review lacks). Resolve each
   contradiction by precedence, bank over Code over manual: check the
   statement the sentence is claimed by before touching it. Added 2026-09-18
   after the maintainer asked; the first pass over the eleven completed
   topics found 27 contradictions, of which 13 were real (see below).
9. Rebuild with `md_to_reviews.py`, set `APP_VERSION` to the new
   `CACHE_VERSION`, then `validate_data.py`, `check_review_placement.py`,
   `node --check` and eslint. Commit.

### Grab-bag bullets are cleared here, not in a separate pass

Decided 2026-09-15: the maintainer's standing rule is one rule per bullet, and
a welded bullet is cleared when its topic is claimed, at step 4, rather than in
a sweep of its own. The reason is evidence. At step 4 a reader is already
reading every bullet against every statement of the topic, so a split is made
knowing which bullet has to answer which question, where a blind pass would be
guessing. Two mechanical signals stand at 416 blocks with a semicolon and 49
that open two subjects with a bold label, counted over both language halves;
`scripts/check_review_bullets.py` holds those counts from rising while the
backlog comes down topic by topic. Lower the baseline whenever a topic's pass
reduces them. Glossary rule 40 has the full reasoning, including why scoring
grab-bagginess by sentence and bold count was rejected.

### The lesson from topic 13

Topic 13 was 379 statements against 46 blocks, so the average block held eight
statements' worth of material and a learner landed on a paragraph bundling four
unrelated rules. Claiming such a review precisely is impossible, because there
is no paragraph that states only the tested rule. The file was split into 115
one-rule bullets and every statement re-read, which is why step 4 sits where it
does. A claim marker stays on the FIRST fragment when a block is split, so the
re-read is what actually moves each claim to the right bullet.

The corollary is that the statements-per-block ratio predicts how much of the
work is editing rather than claiming. Above roughly five, expect to split
first.

### The manual cross-check of 2026-09-18

Every completed topic was read against its SIDA chapter (extracts by
`scripts/sida_extract.py`, one reader per topic). Twenty-seven contradictions
were reported; each was settled by precedence, and thirteen changed the notes:

- **12**: the disc arrival time may also be written on a sheet of paper
  (the notes had said the opposite; the FALSO statements turn on the END time
  and on the missing minutes, not on the paper); the left-margin sosta is an
  URBAN one-way rule and the 3 m condition is the sosta's, a halt there being
  allowed outright.
- **16**: children's and disabled persons' machines are not vehicles (art.
  46), where the notes said only pedestrians are not; and the 2021 exception
  admitting motorcycles from 120 cm³ (6 kW electric) to the autostrada with an
  adult rider (art. 175 c. 2-bis, confirmed in the Code on disk). The same
  exception went into **21**.
- **21**: one vest on board is enough, and the notes said one per occupant
  against the very statement they claimed (24014 is FALSO); the 100 m triangle
  distance on the autostrada is the manual's rule, not "course-book advice".
- **22**: a B1 holder reaching B takes the driving test, not a theory-only
  supplement and not a full theory-and-practical exam; A1 held two years
  opens A2 at 18 by graduated access; loss of the MORAL requirements is a
  revocation ground; categories are "applied for on their own", since the
  graduated route can replace the exam with a course.
- **17**: "asking how the crash happened is not first aid" overstated a FALSO
  about the GOAL of first aid; "do not wait for the police before touching
  them" now distinguishes giving aid (do not wait) from moving the person (do
  wait, unless danger forces it); an open fracture is covered, not handled;
  118 still connects beside 112.
- **23**: withdrawal on the spot added to the license measures, which the
  notes had called "the whole list".
- **24**: the horn line now carries the built-up-area condition and "as
  briefly as possible" instead of "only some roads restrict it".
- **13**: reversing before a procession is banned when it obstructs traffic,
  not outright.

Fourteen reported contradictions were NOT applied, because the bank or the
Code decides against the manual: the horn with an injured passenger past a
no-horn sign (19621 is VERO); firm pressure on a severe wound (24878 is VERO);
the breathing check with a hand on the chest (24906 is VERO); the light
quadricycle's 4 kW electric limit (art. 53, the manual's 6 kW is the EU
class); the 15-day-to-2-month phone suspension (2024 reform, manual predates
it); in-town intersection bans limited to 5 m (art. 158); B obtained before
1988 covering A (too old to teach); the recovery position and arterial
compression (manual detail the bank never tests, left as MISSING).

The UNSUPPORTED and MISSING lists sit in the findings files of that run and
were not acted on: unsupported is mostly bank-derived negatives the manual
never states, and missing is mostly other topics' material.

## Text topics, in order

Every card in these topics is text only or mostly text, so the notes are the
only route to the rule and a weak landing costs the learner directly. The order
is by measured weak landings, not by size.

"Heading" counts statements that get no paragraph at all and land on the
section heading. "Bundled" counts statements that do land on a paragraph, but
one holding three or more sentences, so the deciding rule may be any of them.

| # | topic | statements | blocks | per block | heading | bundled | weak |
|---|---|---|---|---|---|---|---|
| 1 | 20 Elementi costitutivi del veicolo | 284 | 32 | 8.9 | 62 | 201 | 263 |
| 2 | 11 Limiti di velocità | 256 | 39 | 6.6 | 128 | 103 | 231 |
| 3 | 22 Patenti di guida e documenti | 230 | 47 | 4.9 | 93 | 93 | 186 |
| 4 | 14 Uso delle luci e dispositivi acustici | 176 | 49 | 3.6 | 121 | 17 | 138 |
| 5 | 12 Fermata, sosta, arresto e partenza | 190 | 40 | 4.8 | 87 | 44 | 131 |
| 6 | 17 Qualità e condizioni del conducente | 141 | 31 | 4.5 | 45 | 76 | 121 |
| 7 | 10 Norme sul sorpasso | 156 | 52 | 3.0 | 56 | 63 | 119 |
| 8 | 23 Responsabilità e assicurazione | 149 | 26 | 5.7 | 64 | 48 | 112 |
| 9 | 18 Comportamenti per prevenire incidenti | 126 | 21 | 6.0 | 29 | 79 | 108 |
| 10 | 19 Dispositivi di equipaggiamento | 135 | 25 | 5.4 | 42 | 53 | 95 |
| 11 | 09 Distanza di sicurezza | 134 | 37 | 3.6 | 55 | 18 | 73 |

Notes on individual topics.

- **20** is the worst review in the bank by ratio. Split first.
- **11** done 2026-09-18. Split first, as predicted: 39 blocks became 86,
  the golden-rule paragraph (eight claims from 13 and 16 on one block) became
  nine one-rule bullets, and the slow-down list became sixteen. Three readers,
  0 absent, 0 elsewhere. The blind check's four disagreements were one
  choice made three times: a statement naming a vehicle class (motorcycle,
  motorhome, truck up to 3.5 t) landed on the line that says those classes
  share the car figures, where the blind reader took the per-road line; the
  class line stays, because the class is the doubt the statement tests. The
  13 gaps reported were all FALSO statements inventing a trigger to slow
  (bus stops, driveways, overpasses, any sign, a climb, the half hour after
  sunset); they sit on the one existing contrast line under rule 5b and no
  denial was added for them. One real gap was filled: a *rimorchio leggero*
  is still a *rimorchio*. A reader also caught 22380's explanation giving a
  carrello appendice the 80 km/h trailer figure; corrected to the car's own
  rain figure.
- **22** done 2026-09-18. Split rule by rule, as predicted: 57 blocks became
  123, and each category bullet (AM, A1, A2, A, B1, B, B96, BE) became four
  or five one-rule bullets. Three readers, 2 absent (racing on a private
  track, a loaded truck on a holiday), 0 elsewhere; 24551 moved here from
  16, where it had been claimed on the C1 line, because the B bullet names
  the non-exceptional operating machine directly. Blind check 37 of 40, and
  one of the three disagreements was right: the bank's "B covers trucks over
  3.5 t" family had been claimed on the denial line, and rule 5b puts it on
  the bullet that states the 3.5 t limit. Moved. The five gaps were all
  FALSO statements inventing a ground for withdrawal, suspension or
  revision; they sit on the list blocks, which open with "for example", and
  no closing sentence was added, because withdrawal's real list is longer
  than the notes' and a false closure would teach a wrong rule. A reader
  asked for two further splits (new-driver paragraph, withdrawal list) and
  both were made, so 24551's move and the withdrawal claims sit on one-rule
  bullets. Anchors 4618 and 4619 lost their `block` keys, which pointed at
  the paragraphs that were split; the claims outrank them now.
- **14** done 2026-09-18. The pictured cards are the nine dashboard symbols,
  and the review already carries each symbol's image with one paragraph
  under it naming its color, its meaning and the wrong readings the bank
  tests, so every symbol statement was claimed to its paragraph rather than
  left to the image: the image alone shows the symbol, the paragraph is what
  says the battery light means the alternator and not a flat battery. 49
  blocks became 79 (the horn paragraph, the turn-signal bullets, the
  parking bullet and the reflector paragraph split), two readers, 0 absent,
  blind check 40 of 40. Two gaps were the invented-trigger kind (low beams
  when passing a police car, a fog-light telltale in red) and one clause
  was added for the second: the front fog lights show green. The rule 13
  placement check bit twice on the way: it treats every BULLET in a section
  that holds an image as naming a pictured subject, so turning the hazard
  paragraph and the color paragraph into bullets made "low beams" and
  "high beams" count as pictured and flagged the Seeing section. Those two
  stay as paragraphs; a paragraph is a block like any other.
- **12** done 2026-09-18. 40 blocks became 85: the sosta-only paragraph,
  which would have taken some forty claims on one block, is now one bullet
  per place, and each states both halves ("no sosta, but a halt is
  allowed"), because the first readers landed every "la fermata è
  consentita" statement on the one summary sentence that said so. The
  always-forbidden paragraph split too, and its seven claims from 16 were
  placed by hand. 22962 is claimed here now, on a new arresto line: at a
  red light you stop before the crosswalk, never on it; its absent marker
  in 13 is gone. 23685 (no fermata on the autostrada even in an emergency)
  went `elsewhere` to 21's emergency-lane bullet, and `claims_apply.py`
  released its absent marker from 12 on its own. Two readers, blind check
  40 of 40. Two gaps filled in a clause each: precautions during the sosta,
  and placing the vehicle as the signs prescribe in a designated zone.
- **17** done 2026-09-18. 31 blocks became 66, one per alcohol effect and
  one per first-aid action. A reader caught a real error, not a gap: the
  notes carried a blanket "do not give an injured person anything to
  drink", and the Ministry marks 24883 ("non si può assolutamente dargli da
  bere acqua", severe bleeding) FALSO, so the line would have taught the
  wrong answer. The rule is now the bank's: never alcohol, nothing at all to
  an unconscious person, water to a conscious person not forbidden; the
  explanation on 24883 had said so all along. Two readers, blind check
  40 of 40. Figures unchanged, so `reference.json` needed nothing.
- **23** carries figures that also appear in `reference.json`. Keep the
  two consistent.
- **18** done 2026-09-19. 21 blocks became 71: every condition (rain, snow,
  ice, fog, tunnel) is one bullet per action, and the crash-scene paragraph
  is ten. The three waiting gaps (18573, 18576, 18577, the light
  quadricycle's engine and exhaust) are claimed on the tuning bullet. Two
  readers, 0 absent, 0 elsewhere; one gap filled (sudden acceleration on
  ice). Blind check 39 of 40, the one disagreement a tie between the list
  of slippery features and the "when wet" bullet. The manual check reported
  three contradictions and all three were the bank's own wording (fog lights
  first, then low beams, 24754 VERO; a higher gear when first fails, 24785
  VERO; two-wheelers banned where chains are required, 24808), so only the
  gear line was reworded to say "if first does not do it".
- **09** done 2026-09-19, the last text topic, by the topic-19 method: the
  review was rewritten from 38 blocks into 112 (the factor list became one
  bullet per factor, the distances one bullet per speed) with the claims
  placed while writing, and two readers decided all 134 statements blind.
  They agreed on 128 of 134, and all six disagreements were the readers
  applying rule 5b correctly where the writer had not: the three "at least
  the braking distance" distortions (22552, 22571, 22656) belong on the
  bullet that STATES the minimum equals the reaction distance, not on the
  contrast line beneath it, and the two "total equals one part" statements
  (22624, 22625) belong on the definition of the sum. Their choice was
  applied. One trap found on the way: two bullets with IDENTICAL English
  ("It lengthens on a snowy road", once for braking distance and once for
  total stopping distance) share one hash, so the second silently took the
  first's claims and pairs entry. `validate_data.py` does not catch it; the
  fix was to word them apart. The manual check found no contradiction, and
  two of its omissions were added (the 20 m rule also binds oncoming
  vehicles, which stop if needed; gravel spreaders count; drugs lengthen the
  reaction time).
- **19** done 2026-09-19, the other way round: SPLIT FIRST, then claim.
  With the statements in hand the review was rewritten from 30 blocks into
  120 one-rule bullets and every claim placed while writing, so the machine
  proposals were skipped and the two readers instead decided all 133
  statements blind, with no proposals in the packet. They agreed with the
  written claims on 133 of 133, which is what one rule per bullet buys: there
  is nothing left to choose between. Their two gaps were real (24366 wants
  the airbag switch condition for any child seat, not only a rear-facing
  one; 24440's seasonal padding sat under Approval rather than Gloves), and
  their one split was the e-scooter paragraph. The manual check found two
  contradictions. One was settled AGAINST the manual by the Code: art. 172
  c. 3 lets a child over three ride in the rear of a car with no restraint,
  which the manual says is never allowed and which 24364 does not test. The
  other was settled against the review: the taxi and hire-car exception is
  for any child under 1.50 m, in a rear seat, with a companion of at least
  sixteen (art. 172 c. 4), where the notes had "over three, with an adult",
  copied from the manual's prose while its own figure had the Code's
  version. The manual's five-year helmet life and its hand-painting ban
  went into the notes as teaching. `sida_extract.py` had topic 19 pointed
  at the seatbelt chapter only; the helmet and clothing sections are ch. 23
  (lines 10992 to 11128) and are now in its range list.
- **10** done 2026-09-19, the first topic to run with the manual check in
  the pipeline. Splitting was light, as predicted (52 blocks to 68). The
  readers' gaps changed two rules: passing in a curve or over a crest is
  allowed with at least two lanes in your direction, separate carriageways
  or not (23558 is VERO for two lanes alone, and the notes had required
  separate carriageways), and the intersection ban is lifted by four cases,
  not three. New bullets took the motorcycle statements (left only, no
  reserved lanes) and the autostrada danger family (23606 to 23613,
  including the side wind), which the readers had sent elsewhere or absent.
  The manual check then found one real contradiction: at an unguarded
  railroad crossing with no traffic light the ban holds even within your
  own half, where the notes' "stay in your own half" line read as a general
  escape. One absent (23596, a caravan on a steep descent). Blind check
  40 of 40.

## Picture topics: the lighter pass

These 10 topics are 3,825 statements, and on nearly every card the review
already carries the pictured sign, which `reviewTargetFor` prefers over any
paragraph. A statement naming a *figura* never gets a paragraph at all, because
its subject is the drawing. So the full pipeline would spend two thirds of the
remaining effort on cards that already land well.

**The lighter pass**, as agreed: claim only the statements that test a RULE
rather than identify the sign, leave sign identification to the card image, and
do no block splitting and no gap filling.

**Settled 2026-09-19: the marker `<!-- claims: rules -->`.** It records that
the topic's rule statements are claimed or absent and that the rest identify
the pictured sign. It does NOT retire the picker, so an unclaimed statement
behaves exactly as before the pass, and `validate_data.py` FAILS if an
unclaimed statement sits on a card with no picture. The packet gains a
`cards.md` (which figure blocks sit under each card's image, via the alias
groups) and a `README_picture.md`, and readers answer each statement with a
block, `"figure"` or `"absent"`; `claims_apply.py --rules` writes the marker
and releases `"figure"` statements from any claim. The reader instruction that
matters is the strict one: claim a block only when it decides the statement
and the card's own figure blocks do not. Since topic 01 (2026-09-19) the
packet is built by `claims_packet.py NN OUTDIR --picture`, which writes
`cards.md` and `README_picture.md` itself: the figure for a card is found the
way `reviewImageFor` finds it in the app, and two image lines stacked with
only blank lines between them share the blocks under the second (that is how
4281 and 4284 sit in topic 01; the first version reported 4281 as having no
figure at all).

| # | topic | statements | pictured | blocks |
|---|---|---|---|---|
| 1 | 03 Segnali di pericolo | 662 | 100% | 49 |
| 2 | 01 Segnali di indicazione | 603 | 100% | 73 |
| 3 | 04 Segnali di divieto | 519 | 100% | 61 |
| 4 | 02 Segnali di obbligo | 431 | 100% | 51 |
| 5 | 25 Esempi di precedenza | 415 | 100% | 49 |
| 6 | 08 Pannelli integrativi | 261 | 100% | 41 |
| 7 | 07 Segnaletica orizzontale | 259 | 93% | 51 |
| 8 | 15 Segnalazioni semaforiche e degli agenti | 252 | 88% | 53 |
| 9 | 05 Segnali di precedenza | 243 | 100% | 34 |
| 10 | 06 Segnali complementari e temporanei | 180 | 100% | 32 |

Notes.

- **03** done 2026-09-19 as the pilot of the rules pass. Six readers over 662
  statements: 521 figure, 141 claimed on 14 blocks, 0 absent. The claims
  concentrate where expected: the family rule that a warning sign forbids and
  orders nothing (28), the driving rules for a single bend that only the
  double-bend bullet states (30), placement and panels (14 on 150 m, 8 on the
  countdown panels), the crossing behaviour (14), the yellow road-work
  background (9). Two VERO gaps were filled despite the no-gap-filling rule,
  because an unfilled VERO gap misleads: the cross may be mounted
  horizontally or vertically and paired with STOP (19083, 19097, which the
  readers had marked absent), a wet road on a descent (19204), and moderating
  speed for cyclists (19174). The FALSO gaps the readers reported are settled
  by the general rule and were left. Blind check 35 of 40, every
  disagreement a figure-or-claim boundary call and none a wrong block. The
  manual check found one contradiction, in the block 28 statements are
  claimed on: "impose no obligation" was too strong, since the manual (2.1.2)
  and 19237 VERO have a warning sign impose the general duty of prudence;
  reworded to "no specific maneuver ban, order or precedence", which keeps
  every claimed FALSO. Added from the manual: backing up on a crest, the
  barrier symbol covering half-barriers on any number of tracks.
- **25** is 415 intersection diagrams, and every one of its statements lands on
  a heading today because the drawing is the subject. The lighter pass may
  reduce to nothing here. Decide that before commissioning readers.
- **15** done 2026-09-19. Three readers over 252 statements: 212 figure, 40
  claimed on 17 blocks, 0 absent. The four PICTURELESS cards are the whole
  reason this topic needed the pass, and they behaved as predicted: every one
  of their 29 statements is claimed (the officer's whistle 8, the level
  crossing with the half-barrier still up 8, the documents to show 8 on three
  blocks, how an officer is recognized 5), because `figure` is not available
  to them and `validate_data.py` would fail on any left unclaimed. Readers
  were told which cards those were, in the prompt, since `cards.md` marks
  them "no picture on the card" but `README_picture.md` only describes the
  "(none in the review)" case. Two gaps filled on the crossing block: the
  stop is owed whatever the crossing holds, one track or several, and whether
  or not other vehicles are already waiting. The manual check found five
  contradictions, three of them real and corrected: with arms at a right
  angle the officer stops everyone except the traffic on his left, where the
  notes had let the traffic behind him turn (21190 is FALSO, so the bank
  agrees with the manual) and said nothing at all about traffic facing him;
  the flashing reds guard a crossing WITHOUT barriers or with HALF-barriers,
  not "with or without barriers" (21017 and 21018 are the bank's two VERO
  cases); and the flashing yellow B or C is about yielding in a TURN, which
  the summary had narrowed to a right turn. One omission both the manual and
  a reader reached independently was added and claimed: the standard light
  governs every vehicle, bicycles and scheduled public-transport vehicles
  included (21064, 21078, 21079, all FALSO). Left alone for want of any live
  statement: two short whistle blasts meaning go, the police car's
  illuminated display, the *foglio rosa* standing in for the licence, and the
  triangle's exemptions.
  PROCESS TRAP, cost a blind check: build the packet only AFTER
  `md_to_reviews.py` has run. `claims_packet.py` takes the BLOCKS from the
  markdown but the `pairs` map from the shipped `topic_reviews.json`, so a
  block edited since the last rebuild has a hash the map does not know and
  `blocks.md` prints "(none: English-only, not claimable)" for it. The blind
  reader believed the crossing block was unclaimable and sent all eight of
  its statements to a passing mention instead, which read as 30 of 40 until
  the cause was found; re-read against a correct packet, all eight agreed.
- **07** done 2026-09-19. Three readers over 259 statements: 198 figure, 61
  claimed on 15 blocks, 0 absent, and all 18 statements of the four
  pictureless cards claimed. The heavy block is the one-way versus two-way
  contrast (B015, 14 claims): the dashed centre line looks identical on both
  roads and its figure block says only that the line may be crossed, so every
  statement about what that line permits needs the prose.
  A REAL CONTENT ERROR was found by a reader and confirmed independently by
  the manual check: the guide-lines bullet told the learner to keep the guide
  lines "and the center of the junction" on the LEFT in a left turn, where
  20737 is VERO that they are found where the left turn leaves the junction's
  centre on the RIGHT. Corrected, and the positive rule for a right turn
  (the lines stay immediately on your left there too) now states what 20740
  denies. Three other fills, each claimed: the left lane of a one-way road is
  also the lane a left turn is taken from, and on a two-way road the same
  broken line licenses no overtaking in a curve or at a crest (that pair
  released two `elsewhere` flags to 13 and one to 10); an inscription either
  completes a sign or marks a reserved zone, so an announced service is not
  one; the broken side line may be crossed whenever needed, emergency or not,
  which is what 20938 FALSO turns on, and it also delimits a DECELERATION
  lane. From the manual, two accuracy fixes: the emergency lane admits
  emergency vehicles, and the continuous edge line is crossed only in an
  emergency. Its other findings were settled FOR the bank: 20807 is VERO that
  vehicle A "può andare in qualsiasi direzione", so the manual's extra yield
  duties in that figure are not taught here. Blind check 36 of 40, three of
  the four a stop-line boundary call between the block that names the halt
  point and the one that names what completes it.
  Card 5073 is worth knowing about: its image is `4236_20935.jpeg`, a variant
  of 4236, so `reviewImageFor` falls back to the base figure, which shows a
  pull-off side line while the card shows guide lines at an intersection.
  Both readers noticed. The claims override the figure, so it is handled, but
  a variant whose subject differs from its base is what the `{"img": …}` form
  in `review_anchors.json` exists for.
- **05** done 2026-09-19. Three readers over 243 statements: 162 figure, 81
  claimed on 20 blocks, 0 absent. This is the highest claim rate of any
  picture topic so far (a third of the statements), and the reason is that
  half its cards are TRIANGLES whose picture says which junction is coming
  and nothing about who yields: the rules live in prose, so B002 took every
  family-classification statement (13), B010 the priority-never-excuses-care
  ones (9), B027 the officer hierarchy (8), B014 which family precedes which
  (7), B020 the autostrada exclusion, B015 the placement distances, B025 and
  B026 the sign-versus-light matrix. Five VERO gaps were filled: the junction
  triangles are right-of-way signs despite their warning-sign shape (three
  statements had no block saying so), a right-of-way sign is not an
  information sign either, the yield duty covers BOTH directions and is not
  the priority-to-the-right rule, the yield and STOP signs stand on urban and
  extra-urban roads alike, and the crossroads triangles appear neither on an
  autostrada nor on its access ramps. Blind check 40 of 40. The manual check
  found three contradictions, all corrected: the blue square of the
  alternating one-way pair IS a regulatory sign (the notes had called it an
  information sign, which also contradicted their own paragraph saying that
  calling one of these an information sign is false), the merge versions
  stand on one-way carriageways generally rather than the left-merge one
  alone, and STOP is NORMALLY used at dangerous or blind junctions rather
  than reserved for them. Two of its omissions were added as teaching, with
  claims: the priority-crossroads triangle gives priority over vehicles from
  both sides and leaves the duty of slowing to check that they yield
  (20605, 20607, 20608, 20612), and the side-road versions carry the same
  duty of care and may likewise be preceded by the diamond (20619, 20631).
  A claim added BY HAND to a new sentence must be REMOVED from wherever the
  readers had put it: three statements ended up claimed twice, which
  `validate_data.py` catches and which I committed anyway by grepping its
  output for a success line instead of reading its exit code.
  PROCESS NOTE: edit the review BEFORE running `claims_apply.py`, and rebuild
  the packet afterwards. Editing between the packet and the apply changes the
  block hashes, and the apply refuses the whole file with "points at a block
  not in the packet"; block IDs are positional, so rebuilding the packet over
  the edited review and re-applying the same decisions.json is the recovery.
- **06** done 2026-09-19, chosen as the smallest remaining topic and the
  cheapest confirmation that the lighter pass is right for a picture topic
  whose review already carries every device's figure. Two readers over 179
  statements: 169 figure, 10 claimed on 2 blocks, 0 absent, no gaps. Both
  blocks are family-wide facts no figure states: what makes a device
  *complementare* (5) and what every delineator does and does not do,
  reflective by day, no light of its own, never dividing the carriageway into
  lanes (5). Blind check 40 of 40 on a sample of all 10 claims plus 30 figure
  decisions, which is the shape to expect when a topic needs almost no claims.
  The pass paid for itself elsewhere: both readers independently found that
  **B002 and B003 were crossed between the languages**, the English half
  ordering the US colour note before the definition of *complementari* and the
  Italian half the reverse, so `pairs` mated each block with the wrong twin and
  an IT pill on either showed the other paragraph. Nothing catches this:
  `validate_data.py` checks that every block HAS a twin, not that the twin says
  the same thing. The Italian order was corrected. The manual check found four
  imprecisions, all corrected: yellow is for temporary WARNING and INFORMATION
  signs, not every temporary sign (the bank's nine yellow-background statements
  are all on warning signs, so it agrees); at the LUCCA detour board lighter
  vehicles MAY go straight, either route being open to them; delineator spacing
  is variable with no minimum, where the notes had invented "at most 50 m on a
  straight"; and the chevron panel MAY be preceded by the DANGEROUS BEND sign
  rather than normally being so. Its longer MISSING list (barriera direzionale,
  the deviation-length board, dossi artificiali, delineatori di accesso) was
  left: none of those words appears in this topic's live statements.
- **04** done 2026-09-19. Five readers over 502 live statements: 444
  figure, 58 claimed on 18 blocks, 0 absent. The claims are the family rules
  (a prohibition sign never warns or yields, B001; it is a regulatory sign,
  B003), the size-and-weight scope (every vehicle, load included, exactly at
  the figure passes: B026 and B030, 15), the hours rule (B048, B045) and the
  end-sign form (B051). Two readers reported the same gap from opposite
  sides, that nothing said a prohibition WITHOUT a panel holds at every hour
  and every day, and six statements now claim that sentence on B048. Other
  fills: the no-passing sign is used on urban and extra-urban roads alike
  (19546 VERO had been marked absent), height is measured from the road
  surface, a limit binds tractor and trailer alike, the passo carrabile sign
  holds in town and out, by day and by night, and allows a brief halt
  (19985), the bus ban includes buses under 3.5 t (19720). A reader also
  caught the review contradicting the bank: B019 let special-use vehicles
  over the figure pass the truck sign, where 19743 is FALSO; corrected. The
  blind check returned 29 of 40, and the map reads cleanly: seven of the
  eleven disagreements are statements whose rule was filled INTO the card's
  own figure block during this pass, so the blind reader, working from the
  refreshed blocks, answered "figure" where the claim lands on that block's
  new sentence; the rest are the usual family-rule-or-figure boundary. The
  manual check found one real contradiction: the no-trailer sign bans
  tractor-trailers too (a semi-trailer is a trailer), where the review had
  said it does not; the manual's other disagreement, special-use vehicles
  passing the truck sign, is settled against it by 19743. `sida_extract.py`
  gained the ranges for ch. 3, 4 and 5 (topics 05, 04, 02).
- **01** done 2026-09-19 by the same pass. Six readers over 603 statements:
  542 figure, 61 claimed on 17 blocks, 0 absent. The claims concentrate on
  the rules the figure blocks do not state: the road-code number is not a
  distance, a speed or an exit number (B015, 14), lane preselection (B025,
  9), the exit advance sign (B018, 9), the colour-by-road rule for the
  "installed on urban/extra-urban/autostrada" statements (B009, B004, B005,
  B007), the one-way U-turn ban (B033). Three VERO gaps were filled as a
  sentence each on the figure block and claimed there: a main extra-urban
  road has separate carriageways (21523), the motor-vehicles-only sign is
  cancelled by a red stripe (21640), the advised-speed sign may carry an
  extent panel (21626). Blind check 36 of 40; the four disagreements were
  one on the unfilled gap (blind said absent, now filled) and three
  boundary calls between the colour rule and a figure block, kept as
  claimed. The manual check found two contradictions, both settled for the
  manual since the bank does not decide them: the heavy-vehicle route sign
  also addresses trucks over 3.5 t, and the plain dead-end sign says nothing
  about pedestrians (the review had let them pass; the bank's 21623 FALSO is
  on the advance sign). One tested omission added: chains go on the driving
  wheels only (21509, now claimed). `sida_extract.py` gained the range for
  ch. 6 (lines 2511 to 3302).

## Open items carried over

- **One rule per block in 21, 16 and 13.** 16 and 21 were claimed before the
  splitting lesson. Measured on 2026-09-12, the statements landing on a claimed
  paragraph of three or more sentences are 255 in topic 16, 113 in 21 and 74 in
  13, where the last group is mostly blocks that grew a sentence from a gap
  addition. Inside such a block the deciding sentence is picked by the marker,
  which is still a guess, and 18358 is the known bad case. Not every one is a
  defect, so the pass is to read them and split only where the sentences state
  different rules. Worth doing once the text topics are done.
- About 10 parentheticals carrying a tested rule remain outside topic 21. House
  style promotes each to its own sentence.

## Refreshing the numbers

The two tables above come from the shipped data, so they can be regenerated
after any review edit. `scripts/review_landings.py` mirrors the app's picker,
and its `sentences` function is the same splitter the sentence marker uses.

```python
import json, sys, glob, collections
sys.path.insert(0, 'scripts')
import review_landings as RL, md_to_reviews as M

r = json.load(open('public_html/topic_reviews.json'))
q = json.load(open('public_html/questions.json'))
a = json.load(open('public_html/review_anchors.json'))
num = {}
for f in sorted(glob.glob('topic_reviews_md/[0-9]*.md')):
    num[M.parse_md(open(f, encoding='utf-8').read())[0]] = f.split('/')[-1][:2]
by = {x['number']: x for x in RL.landings(r, q, a)[1]}
out = {}
for c in q:
    rv = r[c['topic']]
    itb = [b for _, b in RL.blocks(rv['it'])]
    d = out.setdefault(num[c['topic']], collections.Counter())
    for s in c['statements']:
        x = by.get(s['number'])
        d['tot'] += 1
        if not x or not x['block']:
            d['heading'] += 1
            continue
        j = rv['pairs'].get(x['block']['en'])
        n = len(RL.sentences(itb[j])) if j is not None else 1
        d['bundled' if n >= 3 else 'ok'] += 1
for t in sorted(out):
    d = out[t]
    print(t, d['tot'], d['heading'], d['bundled'], d['heading'] + d['bundled'])
```

A completed topic's heading count equals its `absent` count exactly, because an
absent statement is deliberately treated like an unclaimed one: a landing that
only absent statements could produce would leak the answer. As of 2026-09-12
the snippet prints 4 for topic 13, 10 for 16 and 5 for 21, which is the
accounting check that the topic really is complete.

The bundled count is a proxy and not a defect list. A three-sentence bullet is
fine when all three sentences serve the one rule the bullet states, which is
often the case after a gap addition is appended. Read the block before deciding
it needs splitting.

- **08** done 2026-09-20, and it is the OUTLIER of the rules pass: three readers
  over 260 statements returned 252 `figure` and only 8 claims on 5 blocks, 0
  absent, against 40 of 252 on topic 15 and 61 of 259 on topic 07. That looked
  like readers leaning on "figure is the default", so it was checked twice
  before being accepted. It holds, for a structural reason worth recording: in
  this topic the general reading rules ARE figure blocks. Each panel type gets
  its own bullet under its own picture, so the bullet that says a bare number
  is the distance to the start, or that arrows at both ends give the length, or
  that † means holidays, is the very block the card's 📖 already opens. There is
  almost nothing left for a general block to decide. Only 8 of the 260
  statements do not name the pictured panel at all, and 7 of those are still
  about it ("il pannello integrativo di figura B…"). The blind check agreed
  **40 of 40**, the highest of any topic so far, and its notes name the same
  cause card by card.
  The manual cross-check (ch. 8, lines 3622 to 3950, now in `sida_extract.py`)
  raised 20 items and three were acted on. A REAL ERROR: the *limitazione*
  silhouette bullet claimed the same silhouette covers the **autotreno** as
  well as the *autoarticolato*. The bank names only *autoarticolati* on that
  card (22061 VERO, 22067 and 22068 FALSO), the manual names only the
  *autoarticolato*, and the two vehicles are not the same thing, so the clause
  is gone. A CONTRADICTION WITH THE BANK: the trucks-slowing bullet ended "it
  says nothing about the road's grade as such", where 22202 is VERO that the
  stretch is *in ripida salita*; the denial belonged to the distance panel on
  another card (22012) and was misfiled. It is replaced by what the bank does
  test there, no ban on passing (22207 FALSO) and no shorter following distance
  (22209 FALSO). An OMISSION: the extent panel now says the stretch starts at
  the sign, which the manual states (8.1.3) and our bullet gave only as "how
  long it continues".
  Two manual findings were CHECKED AND REJECTED, which is the point of doing
  this against the bank: the flooding panel says "heavy rain", the manual says
  "prolonged rain", and the bank writes *forte pioggia* (22145 VERO), so ours
  stands; and the course panels "never on autostrade" is bank-sourced (22257
  FALSO), not an invention, although the manual is silent. Left alone and
  recorded rather than acted on: the manual has *tornante* and *numero del
  tornante* as two panels where we have one bullet (22236 VERO covers both),
  and it teaches not slowing to look at an accident from the opposite
  carriageway, which no live statement tests.
  One landing was moved by hand after the readers: 22134 ("il pannello è
  abbinato al segnale ALTRI PERICOLI") had been claimed to the recap line about
  snowplows and queues. The block that states the pairing is the teaching one,
  so it went there. A recap bullet answers a statement only when nothing else
  does.

- **02** done 2026-09-20. Four readers over 426 statements: 367 figure, 58
  claimed on 12 blocks, 1 absent, which is the ordinary shape of a rules pass
  (14%, against 16% on 15 and 24% on 07). The blind check agreed **38 of 40**,
  and both disagreements sat on the figure/block boundary rather than on a
  rule. Settled against the packet's own rule 5, which prefers the bullet under
  the statement's own picture: 20127 ("indica una curva pericolosa") went to
  the figure, whose bullet already says the curved arrows announce a TURN,
  rather than to the general "a blue circle never warns of danger" line; 20292
  ("non vale per i ciclomotori") went the other way, to the block about
  supplementary panels, because the rule it distorts is that only a panel
  narrows an obligation.
  The manual cross-check (ch. 5) raised 14 items and three were acted on, all
  three checked against the bank first. The heading rule "a red-bordered circle
  means you must not" was contradicted by our own ALT and DOGANA bullets forty
  lines below, so it now carries the exception; the manual's generico/specifico
  classification, which is the tidier way to say it, was NOT adopted because
  the bank never uses either word. The Italian name of the shared path was
  *percorso promiscuo*, which the bank never writes: it writes *percorso unico
  pedonale e ciclabile* and *viale misto* (20385, 20386, 20402), and the notes
  now use those, so a learner meets the same words in both places. And the rule
  the blind reader had found missing was added from manual 5.1.1: a mandatory
  sign binds every road user, and only a supplementary panel narrows it to a
  category. That sentence also took 20292's claim, which is a better landing
  than the trucks composite that only implied it.
  Rejected after checking the bank: the *transitabilità* pairing and the
  inizio/proseguimento panel reading (no live statement uses either word), and
  the manual's "compresi i ciclisti" on the pedestrian path, which our general
  "prohibited to everyone else" rule already covers.
- **25 is now the only topic left, and the rules pass does not fit it.**
  Measured 2026-09-20 before commissioning any reader, which is what the note
  above asked for: the lighter pass rests on the card's own drawing being in
  the review, and only **9 of the 49** junction cards have theirs there. The
  review carries 7 worked-example figures in all. For the other 40 cards, about
  340 statements, answering `"figure"` would leave them exactly where they are
  now, on a section heading. So 25 needs either a full claim pass onto the rule
  bullets (honest cost: "vehicle M waits for O" is answered by the right-hand
  rule only once the reader has also solved the diagram, so many claims would
  carry a gap) or, better, worked examples written for the cards that lack one,
  after which the ordinary pass would work. The maintainer chose 02 first and
  left this open.

- **25** done 2026-09-20, as a FULL claim pass rather than the rules pass, for
  the reason measured above: only 9 of its 49 junction cards have their drawing
  in the review, so `figure` was not available to 40 of them. Five readers over
  414 statements, every one claimed, 0 absent, `claims: complete`.
  The distribution is the honest shape of this topic: **231 of the 414 land on
  the right-hand rule**, 37 on priority signs, 34 on the new "crossing
  together" rule, 16 on rail vehicles. One bullet carrying more than half the
  topic is a weak landing in the ordinary sense, and it is still far better
  than the section heading all 414 landed on before.
  FOUR RULES WERE ADDED, each from a gap the readers found and each checked
  against the bank first: two vehicles cross together only when their paths
  never meet AND neither still owes the way to a third (23181, 23298, 23386);
  only a left-turner waits at the centre, everyone else clears in one movement
  and a vehicle held by a sign waits AT the sign (23044, 23192, 23216, 23259,
  23402); a ring in which everyone has someone on their right is broken by the
  vehicle whose path crosses nobody's (23110, 23113); and every driver
  moderates speed at a junction, the one with precedence included (23408).
  The blind check ran BEFORE the last of those was fully applied and returned
  29 of 40, which read as a bad result and was not one: seven of the eleven
  disagreements were statements the first pass could not have claimed to the
  new rules because the readers never saw them. Sweeping every
  *contemporaneamente* statement off worked example 5 and onto the new rule,
  which is what the blind reader had done independently, took it to **33 of
  40**. The seven that remain are mostly FULL-ORDER statements ("i veicoli
  transitano nell'ordine: E, R, S, A"), where several rules stack and no single
  block decides: that is the residual weakness of claiming this topic and no
  amount of re-reading fixes it.
  The manual cross-check was the strongest of the whole rollout: **no
  contradiction anywhere**, and all seven worked examples match the Ministry's
  own solution list in the manual figure for figure (607, 631, 634, 633, 637,
  638, 669). The speed rule is sourced directly (14.1.2). The other three
  additions are unsourced in that chapter but contradicted nowhere and
  consistent with all five of its simultaneous-passage solutions; they stand on
  the bank. One omission recorded and NOT acted on: the manual's 14.1.3 list of
  when you give way both right and left (moving off, reversing, U-turn, leaving
  a driveway, where pedestrians are owed the way too). Topic 25's live
  statements contain no *pedone*, *passo carrabile*, *retromarcia* or
  *inversione* at all, so that material belongs to the manoeuvre topics rather
  than here.
- **The rollout is finished.** Every one of the 25 topics is claimed: 15 text
  topics and 25 as `complete`, 9 picture topics as `rules`.
