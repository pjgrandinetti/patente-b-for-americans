# Shared review glossary & conventions

A **shared, append-only memory** for the per-topic AI content review (see
`AI-CONTENT-REVIEW-PROMPT.md`). Each topic run **reads this first** and **appends to it
last**, so later topics stay consistent with earlier ones.

**Rules for editing this file**
- **Append only.** Add new entries; don't delete or rewrite existing ones (a human curates).
- Only add things that are **reusable across topics** (a term mapping, a recurring pattern,
  a style decision) — not one-off fixes.
- If you find an entry here is **wrong**, do **not** edit it — note your disagreement under
  "Open questions for the human" at the bottom.
- This file never overrides the prompt's **Hard constraints**.

---

## Italian → American English glossary

Confirmed term mappings (extend as new topics surface more):

| Italian | American English | Notes |
|---|---|---|
| salvagente | safety island | pedestrian refuge — **NOT** "traffic island" |
| isola di traffico | traffic island | channels vehicles |
| spartitraffico | median | |
| banchina | shoulder | not part of the carriageway |
| carreggiata | carriageway | keep this term |
| corsia | lane | |
| marciapiede | sidewalk | |
| passo carrabile | driveway | |
| macchina operatrice | work machine | not "operative/operating machine" |
| macchina agricola | agricultural machine | |
| autocarro | truck | |
| autovettura | car | |
| ciclomotore | moped | |
| motociclo | motorcycle | |
| quadriciclo | quadricycle | leggero = light; non leggero = non-light/heavy |
| rimorchio | trailer | |
| autocaravan | motorhome | |
| velocipede | bicycle | incl. pedal-assist e-bikes ≤ 0.25 kW |
| trainato | towed | not "trailed" |
| semovente | self-propelled | |
| circolare / transitare | travel / drive | not "circulate" |
| sosta | parking | |
| fermata | stopping | |
| arresto | stop | |
| assimilato / equiparato a | treated as | not "assimilated to" |
| dare la precedenza | yield | not "give way" |

### Britishisms → American (always convert)
tyre→tire · kerb→curb · petrol→gas · motorway→highway/freeway · dual carriageway→divided
highway · give way→yield · verge→shoulder · colour→color · metre→meter · lorry→truck ·
manoeuvre→maneuver · -ise→-ize.

### Units
- Engine displacement: **cc** (not `cm³`/`cm3`).
- Keep metric (km/h, kW, kg); a US gloss (mph) may appear only in the **review**, not in a
  question's text.

---

## Recurring error patterns to check (from completed topics)

- **Systematic mistranslation of a single term** across many statements — once you find one,
  search the whole topic for it (e.g. `salvagente` was "traffic island" bank-wide).
- **Explanation contradicts its VERO/FALSO** (e.g. a FALSO "parking is permitted …" whose
  explanation said "stopping is permitted").
- **Meaning drift**: a word dropped/added that changes scope (*eccezionale*, *tutte*, *solo*,
  *sempre*, *mai*).
- **Explanation that only restates the statement** without giving the rule/why.
- **Asserted numbers that may be wrong** — flag rather than guess.
- **Concepts tested in questions but missing from the review** — add them (EN + IT).

---

## Style decisions

- Explanations: 1–3 sentences, start with "True."/"False.", give the rule/why, American English.
- Reviews: keep the existing per-topic structure and voice; bullets with **bold** key terms,
  Italian term in *(parentheses, italics)* on first mention.

---

## Per-topic log

Append one short block per topic after you finish it.

### Topic 16 — Definizioni (pilot, done by the human + first AI pass)
- Established the vehicle/road-feature glossary above.
- Fixed `salvagente` → safety island bank-wide; added work machines, agricultural machines,
  pedal-assist e-bikes, `passo carrabile` sign + no-parking, `banchina` not part of
  carriageway, acceleration vs. deceleration lanes to the review.

---

## Open questions for the human
- *(none yet — add anything you're unsure about here instead of guessing)*
- Note for the curator (2026-06-10): two rows in the Topic-16 addenda (caravan, a cingoli) were amended **same-session** by the same reviewer after live user feedback, rather than left to contradict their later addenda. No human-curated entries were touched. The chain of supersessions is recorded in addenda one→four.

---

## Additions from Topic 16 — full exhaustive pass (2026-06-10)

### New Italian → American English term mappings

| Italian | American English | Notes |
|---|---|---|
| incrocio a raso / intersezione a raso | at-grade intersection | NOT "grade-level" |
| incrocio a livelli sfalsati | grade-separated intersection | NOT "staggered-level" (calque) |
| autoveicolo | motor vehicle (autoveicoli class) | ≥4 wheels, excl. quadricycles; gloss the Italian where the contrast with "veicolo a motore" matters |
| carrello-appendice | small utility trailer | registered as part of the towing car; NOT "semi-trailer" |
| autosnodato | articulated bus | NOT "articulated truck" (that's autoarticolato) |
| caravan (roulotte) | travel trailer | a TRAILER — never "motorhome" (that's autocaravan); ~~earlier this row read "caravan (travel trailer)"~~ superseded same-session: lead with the American term (see fourth addendum) |
| carrozzina per bambini | stroller | not "pram"/"baby carriage" |
| marciare per file parallele | drive/travel in parallel lines | file = lines of vehicles, NOT "lanes" |
| zebrature | chevron (zebra) markings | not "crosshatch" |
| ferrovia / binari | railroad / railroad tracks | "railway" reads British |
| silenziatore | muffler | not "silencer" |
| posteggio dei taxi | taxi stand | not "taxi rank" |
| vigili del fuoco | fire department | not "fire brigade" |
| parcheggio scambiatore | park-and-ride facility | avoid "car park" |
| sosta / fermata in EN fields | parking / stopping | watch silent drift: several EN fields said "stopping" where the Italian was *sosta* |

### New recurring patterns
- **Class-term swaps inside one card family**: "caravan" rendered as "motorhome" across an entire card (4027) — exactly the distinction the topic tests. When a card contrasts two vehicle classes, verify the EN keeps them distinct.
- **`sosta`→"stopping" drift** is widespread and silent; grep the topic for "stopping/stop" wherever the Italian has *sosta* (and vice versa for *fermata*).
- **"circulate/circulation"** survives in bulk even after a pilot pass (37 hits in Topic 16) — sweep mechanically, then re-read for naturalness.
- **British spellings hide in explanations**, not just translations (unauthorised, armoured, pram, fire brigade, taxi rank, car park).
- **Term consistency between EN translation and its own explanation** (e.g., EX said "at-grade"/"chevron" while EN said "grade-level"/"crosshatch") — align to the glossary term.
- **Self-contradicting explanation**: an EX that mislabels the very term it is contrasting (18530 said channeling is the job of a "safety island" when it meant *traffic island*).

### Style decisions
- Times of day in question text: 24-hour with a colon ("from 20:00 to 8:00"), no "hours" suffix.
- "white-and-red cane" (hyphenated, with "and") for *bastone bianco-rosso*.
- "people/persons with disabilities" rather than "disabled persons".

---

### Topic 16 — Definizioni (second pass: full exhaustive AI review, 2026-06-10)
- Reviewed all 50 cards / 531 statements (the pilot had only covered human-flagged items). 227 field updates.
- Biggest finds: 4027's card-wide caravan→"motorhome" mistranslation; 18446 "incroci a raso" rendered as "railroad crossings"; 18655 carrello-appendice→"semi-trailers"; 18664 autosnodato→"articulated truck"; sosta→"stopping" drift (18508, 18515, 18517, 18520, 18524–18525); systematic "staggered-level"/"grade-level" → grade-separated/at-grade (4007–4008, 4013); 37 "circulate" removals; explanation fixes incl. the 18530 traffic-island/safety-island swap, garbled 18661 inspection intervals, duplicated "shoulder or shoulder" (18723), and weak no-rule explanations (18676, 18800).
- Review additions (EN+IT): autoveicolo definition; heavy-vehicle retroreflective marker panels; lane types (reserved/specialized/minimum-speed); passo carrabile fermata-allowed contrast; trailers expanded (caravan never while towed, motorhome seating, semi-trailer brakes, autosnodato); racing imprisonment + betting; oil/fuel-leak duty; pet-cage 50 cm rule; wait-for-pedestrians-after-green; taxi-stand no-priority point; "taxi rank"→"taxi stand" fix in the EN review.
- Answer flags: docs/answer-flags-16.md (2 mild image-dependent doubts on card 4029).

### Addendum (Topic 16, user feedback 2026-06-10)
| Italian | American English | Notes |
|---|---|---|
| colonnina (luminosa) | short (lighted) post | "bollard" reads British/unfamiliar to American readers — avoid it |

Applied at #18528 and in the Topic-16 review; also fixed the one other instance bank-wide (#20289, Topic 02).

### Addendum (Topic 16, user feedback 2026-06-10, second)
| Italian | American English | Notes |
|---|---|---|
| a cingoli | on tracks / tracked | gloss on first use — superseded same-session by the fuller wording in the third addendum ("continuous belts that loop around the wheels…, like a tank or a bulldozer") |

### Addendum (Topic 16, user feedback 2026-06-10, third)
Refined the *a cingoli* gloss after reader testing: define tracks concretely on first use —
"the continuous belts that loop around the wheels so the machine crawls on them, like a tank or a
bulldozer." Bare "tracked," and even "crawler treads," still confused an American reader (one
guessed it meant "tractor"). Pattern for all topics: when a domain term names hardware unfamiliar
to everyday American readers, define the mechanism in plain words on first use rather than relying
on the technical Americanism.

### Addendum (Topic 16, user feedback 2026-06-10, fourth)
| Italian | American English | Notes |
|---|---|---|
| caravan / roulotte | travel trailer | "caravan" is BrE (AmE caravan = convoy of cars); head word must be the American term, Italian tie-back in parentheses on first/definitional use only |
| camper (Italian) | motorhome / RV | FALSE FRIEND: Italian "camper" = the self-propelled autocaravan, not a towed camper — never translate caravan as "camper" |

Applied across Topic 16 and swept bank-wide (21 fields in 7 other topics; their own topic runs may refine the glossing). Pattern reinforced: a parenthetical gloss does not rescue a British head word — lead with the American term.

### Addendum (Topic 16, user flags batch @20260619r, 2026-06-10)
| Italian | American English | Notes |
|---|---|---|
| carrozzeria | body | "bodywork" reads British/odd to Americans (AmE bodywork = body repair); "a special body" |
| in corrispondenza del passo carrabile (sosta vietata) | parking in front of a driveway | frame prohibitions the American way: "you may not park in front of / block the driveway" |

Also added a cross-topic pointer in the Topic-16 review: license-category coverage lives in Topic 22 (Patenti).
App-structure note (not a data fix): card-level images display beside every statement of the card, including
statements that are not about the figure (flag on #18621, card 4029) — possible app refinement: only show the
image when the statement references the figure.

### Topic 16 — third pass (verification re-run under the upgraded glossary, 2026-06-11)

New term mappings:

| Italian | American English | Notes |
|---|---|---|
| centro abitato | town | ~~earlier this row read "built-up area"~~ superseded same-session by reader feedback: "built-up area" is BrE road-sign vocabulary, unfamiliar to Americans — lead with "town" ("in town", "outside of town"); the review defines the legal term once |
| tonnellata | metric ton | "tonne(s)" is BrE; swept bank-wide (126 fields) as a pure token swap |
| coda (di veicoli) | backup / line of traffic / "when traffic backs up" | "queue/queueing" reads British; reword, don't token-swap |
| fare retromarcia | back up | not "reverse" (verb) |
| diritto di precedenza (noun) | right of way | open form as a noun; hyphenate only attributively ("right-of-way sign") |

New patterns:
- **"è vietato il transito di X"** → "X may not pass" / "closed to X traffic" — not "the passage of X is prohibited" (Italianate residue survives even an exhaustive pass).
- **"segnalato con/da"** → "marked with/by", not "signaled with/by".
- **"in caso di traffico intenso / di code"** → "in heavy traffic" / "when traffic backs up" — drop the "in case of" calque.
- **A verification re-run pays off**: this third pass over already-twice-reviewed content still found ~55 fields — mostly classes the session itself had only just defined (queue, tonnes, right-of-way hyphenation). After any mid-run standard upgrade, re-read the whole topic, not just the statements that triggered the upgrade.
- Britishisms still in OTHER topics for their own runs: "queue" (~10 statements: 22155-22165 region, 20129, 22893, 24242, 24792, 24803, 31053); these need contextual rewording.

Log: third pass changed 55 Topic-16 fields + 126 bank-wide tonne fields + 2 review-EN touches (cm³→cc, tonnes→metric tons). No new answer doubts (answer-flags-16.md unchanged). Versions → 20260619t.

### Addendum (Topic 16 → bank-wide, per-statement figures, 2026-06-11)
The #18621 "wrong image" flag exposed a data-model bug, now fixed properly (supersedes the
2026-06-10 app-structure note): in DomandeB.pdf the Immagine column is per-STATEMENT, and 38
cards bank-wide mix several different figures (or figures + no figure) within one card. These
now carry per-statement images (`statements[].image`, files `domandeb_images/stmt_*.png`,
extracted by `scripts/extract_statement_images.py`); the app shows a statement's own figure
beside it, and these cards have no card-level image. Reviewers of other topics: when a
statement's explanation talks about "the figure", check whether its card is one of the 38
(card image == null) — the figure to describe is the statement's own. The two Topic-16
answer flags (#18613, #18614) dissolved once the true figures surfaced — both VERO are correct.

### Correction (per-statement figures, 2026-06-11, second note)
The fix described in the previous addendum was restructured to follow the app's existing
convention instead of a new `statements[].image` field: multi-figure cards are now SPLIT into
**variant subcards** (like the manual A/B sign-pair variants, ids 5004+) — base card keeps the
statements matching its original figure; each other figure group becomes a subcard (id 5xxx,
`base_id`, letter, `variant_auto: true`) with its figure as the normal pinned card image;
figure-less statements get an image-less subcard. 46 cards → 115 subcards (851 cards total).
`abridged.json` was re-keyed mechanically (same kept statement numbers, distributed to the new
containing cards — no re-tagging). Figure files: `<card>_<statement>.jpeg`. The full bank was
audited statement-by-statement against the PDF: 0 mismatches / 0 gaps / 0 extras (8 flagged
pairs all verified visually as crop/layout false positives). Reviewers: a statement's figure is
now always its (sub)card's pinned image.

### Topic 16 — flag @20260619u (2026-06-11)
Review gap closed: the truck-vs-trailer rear-marker distinction (striped yellow/red panel =
truck; plain yellow panel with red border = trailer/semi-trailer) is now explicit in the
Topic-16 review (EN+IT) and in #18617's explanation. Lesson for the review-gap step: when a
card's figures get corrected (per-statement split), re-diff its tested concepts against the
review — the original gap analysis was done against the wrong figure.

### Policy (all topics, 2026-06-11): figures in reviews + figure-aware gap analysis
Two additions to AI-CONTENT-REVIEW-PROMPT.md (section D), prompted by flags @20260619u:
1. The review-gap step must LOOK AT the cards' figures (incl. variant subcards) — when sibling
   subcards show different figures for near-identical statements, the figure difference is
   itself a tested concept; re-diff a card after its figure is corrected.
2. Prefer embedding a figure row (`![caption](domandeb_images/…)`) in the review over a
   complicated verbal description of what the figure shows — teaching point goes in the
   caption (existing pattern in topics 05/07/15). Applied retroactively to the Topic-16
   marker-panels paragraph (all four panel types now shown as images, EN+IT).

### Topic 16 — figure-aware re-run under the updated prompt (2026-06-11)
Re-ran the review for Topic 16 after the figure correction, exercising the new section-D steps.
Findings: small delta — the 4029 family was already fixed this session; the 4001–4003 road
diagrams were verified against their statements, explanations, and the review (all consistent:
count-carriageways-by-medians, driver-viewpoint left/right, U-turn rules; the review already
embeds all three diagrams with captions). All 84 review figure references resolve.
validate_data.py now also verifies every `![..](path)` in topic_reviews_md (broken review
figures previously failed silently in the app). No content changes required → no version bump.

### Addendum (Topic 16, user flags @20260619w, 2026-06-11)
| Italian | American English | Notes |
|---|---|---|
| centro abitato | town | supersedes "built-up area" (BrE; an American reader did not know what it meant). "in town", "outside of town", "entering a town". Review glosses the legal definition once. ~208 fields in OTHER topics still say "built-up area" — convert during each topic's own run |
| autosnodato | articulated bus — gloss on first use | plain-words mechanism per the *a cingoli* pattern: "the extra-long two-section bus joined by an accordion-style bend in the middle" |

Review gaps closed (EN+IT): transmission never matters for vehicle classification (a moped need
not be manual — #18552; motorcycles may be automatic — #18629); articulated-bus gloss in the
trailers bullet. Topic-16 statements unified on "town" (incl. two stragglers that still said
"urban centers": #18553, #18683). Versions → 20260619x.

### Addendum (Topic 16, user flags @20260619x, 2026-06-12)
| Italian | American English | Notes |
|---|---|---|
| può / possono (permission, in FALSO statements) | is/are allowed to · is permitted | NEVER bare "may"/"can" when the epistemic reading ("might/could happen") would make the FALSO statement true — e.g. "a heavy-vehicle driver may behave in a way that causes frustration" reads true epistemically. 14 Topic-16 statements fixed; OTHER TOPICS surely have the same trap — check every FALSO "may/can" during their runs |
| montanti (interni) | roof pillars | gloss on first use: "the posts framing the windshield and windows"; "internal pillars" is a calque Americans don't use |

Also: #18797's explanation now teaches the cane code itself (white = blind, white-and-red =
deaf-blind, STOP for both); review gained the overtaking-cyclists bullet (adequate lateral
distance, no fixed 2 m, horn outside town, expect slight swerving) EN+IT — the no-fixed-number
trap (#18835) was tested but unexplained. Versions → 20260619z.

---

## Additions from Topic 03 — Segnali di pericolo (2026-06-12)

### New Italian → American English term mappings

| Italian | American English | Notes |
|---|---|---|
| cunetta (road profile) | dip | was mistranslated "rut" topic-wide; MUTCD sign name is DIP. But cunetta laterale = roadside **ditch** — context decides |
| dosso | bump | MUTCD: BUMP; dossi artificiali = speed bumps; "hump" reads British |
| strada deformata | rough road | not "deformed road" (calque); strada dissestata = broken-up road |
| segnale di prescrizione | regulatory sign | NOT "mandatory sign" (that's segnale di obbligo) — the bank tests this class distinction directly |
| strettoia | narrow stretch | restringimento = narrowing |
| confluenza | merge | not "junction"/"confluence" |
| vento laterale | crosswind | not "lateral wind"/"sidewind" |
| veicoli telonati | tarp-sided vehicles | |
| cavalletti | barricades | not "trestles" |
| pannello distanziometrico | distance (countdown) panel | |
| pannelli integrativi | supplementary panels | not "integrative" |
| luce fissa | steady light | not "fixed light" (steady vs flashing is the US pairing) |
| dispositivo acustico | audible warning device | |
| binari di manovra | switching tracks | industrial sidings |
| pendenza | grade | not "gradient" (BrE) |
| salita/discesa | uphill/downhill stretch · climb/descent | |
| abbagliamento | glare | not "dazzling" |
| viale (pedonale) | (pedestrian) walkway | not "precinct" (BrE) |
| orario di uscita (scuole) | school dismissal time | not "closing time" |
| tenuta di strada | (road) grip | not "roadholding" |
| preannuncia | warns of / warns that | not "announces"; presegnala = gives advance warning of |
| Il segnale raffigurato | The sign shown | one rendering — "illustrated/depicted/in the figure/the signal shown" all unified |
| In presenza del segnale raffigurato | Where this sign is posted, | not "In the presence of…" (calque); obligations hold in the signed stretch |

### New patterns
- **Class-term collision**: prescrizione and obbligo were BOTH rendered "mandatory sign", destroying the
  tested distinction on cards carrying both (e.g. 4059). When two Italian class terms appear in one
  card family, verify the EN keeps them distinct (same lesson as caravan/motorhome).
- **Stem drift**: one Italian stem ("Il segnale raffigurato…", "In presenza del segnale…") had 5+ EN
  renderings scattered across cards. Unify the stem first (mechanically), then read for content.
- **Panel text is Italian**: supplementary panels read "TORNANTE", "TRAM" — keep the Italian word and
  gloss it; don't translate the panel's inscription as if the sign were American.
- **Layered regex fixes can collide** — after mechanical passes, ALWAYS grep for artifacts
  ("railway railroad", "warns of that", double spaces) and re-run the leftovers scan to zero.

### Topic 03 log
Reviewed all 71 cards (54 quesiti + 17 figure subcards), 662 statements; ~700 field edits
(translations + explanations) across 8 mechanical layers + per-statement fixes. All 71 figures
visually verified against their card families (incl. 4082/4083 narrowing sides, 4099 windsock) —
none misassigned. Review additions (EN+IT): crossing-group figure row (gate/locomotive/double cross),
behavior-by-hazard section (curves right-edge/no-pass/no-stopping, descent engine-braking and brake
overheating, crossing conduct, tram island rule, crosswind victims, chains-not-required,
traffic-light-ahead mandatory on extra-urban roads), roundabout-ahead sign, TORNANTE panels,
"other dangers" emergency-without-panel point, town wording. Class-statement explanations upgraded
(red-bordered triangle rationale). Answer doubts: none (docs/answer-flags-03.md). Versions → 20260620a.

### Addendum (Topic 03, user feedback 2026-06-12): color-convention bridge
| Convention | Italy | USA | Note |
|---|---|---|---|
| temporary / construction signs | YELLOW background | ORANGE | bridge it explicitly for American readers wherever yellow-background variants come up (done in the Topic-03 review); Italy's permanent warnings are white triangles, not US-style yellow diamonds |

Pattern (generalizes the *camper* false-friend rule): when an Italian COLOR or SHAPE convention
collides with the American one the reader grew up with, state the mapping explicitly ("Italy's
yellow is the US's orange") rather than just describing the Italian rule. Candidate spots in
later topics: Topic 06 (temporary/roadwork signs — the main home for this), Topic 01
(blue = mandatory circles vs US black-on-white rectangles), Topic 15 (signal conventions).

### Addendum (Topic 03, user feedback 2026-06-12, second): illustrate sign topics generously
For sign-class topics the figures ARE the content: show every sign the review names, and show
look-alike pairs side by side (bend directions, descent vs climb, the three narrowings) rather
than describing the contrast in words. Topic 03 now embeds 27 captioned figures per language
(was 8), including a Topic-06 yellow road-work sign anchoring the yellow-is-Italy's-orange
bridge. Apply the same standard from the start in Topics 01, 02, 04, 05, 06, 08.

### Addendum (Topic 03, user flags @20260620r, 2026-06-12)
| Italian | American English | Notes |
|---|---|---|
| la distanza di frenatura diminuisce | braking distance DECREASES | meaning inversion found (#19289: rendered "increases", flipping the FALSO). New check: scan diminuisce/aumenta vs decrease/increase bank-wide after every pass (script pattern in this session's log; the 19289 fix left zero suspects) |
| dossi artificiali | speed bumps | lead with the everyday US term |
| brusche sterzate | abrupt steering movements | not "sudden steering" |
| viale pedonale | pedestrian-only street | gloss the Italian; keep it distinct from… |
| isola pedonale | pedestrian zone (area closed to traffic) | …and from crosswalk/path/overpass — card 4074's traps are all near-synonyms in lazy English; render each pedestrian facility DISTINCTLY |

Style decisions:
- **No stranded prepositions** in statement translations ("the curves this sign warns of," →
  "the curves announced by this sign").
- For "placed at X" traps (warning sign placed AT the crossing, F), make the trap visible:
  "stands at the crossing itself".
- Extent vs distance panels: teach the visual cue (arrows at both ends = LENGTH of stretch;
  plain figure = DISTANCE to start) — now in the Topic-03 review with the 380 m figure.

### Addendum (Topic 03, user flags @20260620s, 2026-06-12)
- **"circulate" exception (refines the bank-wide ban)**: in ROUNDABOUT contexts "traffic
  circulates" is the natural American phrasing — keep it there (#19469); the ban stands
  everywhere else (circolare = travel/drive).
- Windsock-sign logic now taught in #19432's explanation: the sign is POSTED at exposed spots
  (viaducts, embankments, tunnel exits), which is why a statement tying it to a viaduct is VERO.
- Tunnel trap (#19449) explained properly: gust danger is at the EXIT (you leave the shelter),
  not the entrance — pattern: when a FALSO hinges on one swapped word (entrata/uscita), the
  explanation must name that word, same as the 'solo' trick convention.

---

## Additions from Topic 04 — Segnali di divieto (2026-06-12)

### New Italian → American English term mappings

| Italian | American English | Notes |
|---|---|---|
| DIVIETO DI TRANSITO (sign name) | ROAD CLOSED | NOT "no entry" — that collided with… |
| SENSO VIETATO (sign name) | DO NOT ENTER | …this one; both were "NO ENTRY sign", destroying card 4106's trap |
| autotreno | truck-and-trailer combination | was "motor train"(!) and "articulated vehicle" |
| autoarticolato | tractor-trailer | |
| (the trio together) | truck-and-trailer combinations, tractor-trailers, articulated buses | keyed off the Italian — a blanket regex clobbered the trio into "articulated buses, articulated buses, articulated buses" before being keyed |
| veicoli merci | cargo vehicles | "goods vehicle" reads British (HGV) |
| trattrici agricole | agricultural tractors | trattori stradali per semirimorchi = truck tractors for semi-trailers |
| quintale | 1 quintale = 100 kg | gloss it: "8 metric tons (80 quintali)" |
| disco orario | parking disc (disco orario) | gloss: the cardboard clock you set to your arrival time |
| sosta in seconda fila / in doppia fila | double parking | not "parking in the second row" |
| rimozione forzata / ZONA RIMOZIONE | tow-away / TOW-AWAY ZONE | |
| carri agricoli | farm wagons | |
| innaffiatrici stradali | street-washing (water) trucks | not "road sprinklers" |
| persone invalide / contrassegno | people with disabilities / disability placard | "badge" → placard (US term) |
| fine prescrizione | end-of-restriction sign | via libera = "all clear" |
| pesa pubblica | public weigh station | |
| salita e discesa dei passeggeri | letting passengers on and off | reuse of the T03 ruling |

### New patterns
- **Sign-NAME collisions are the deadliest class**: after prescrizione/obbligo (T03) and
  caravan/camper (T16), Topic 04 had DIVIETO DI TRANSITO and SENSO VIETATO both as "NO ENTRY".
  When a card's FALSO quotes another sign's official name, check the two names render differently.
- **AM/PM crept into some cards** — bank style is 24-hour with a colon; sweep `\d AM|PM`.
- **sosta→"stopping" drift struck again** (#19970 "stopping permitted for max one hour" for
  sosta) — the T16 pattern, still alive; grep every topic.
- **Regex-layer artifacts to grep for after every mechanical pass**: "shownal", ", al,",
  "an truck", doubled words ("traffic traffic"), tripled categories.

### Topic 04 log
Reviewed all 53 cards (45 quesiti + 8 figure subcards), 519 statements; ~1,000 replacements
across 7 mechanical layers + ~60 targeted fixes. All 53 figures visually verified — none
misassigned. Review additions (EN+IT): "what each ban does and does not cover" section
(no-passing exceptions, no-horn exceptions, minimum-distance sign, category-ban edges,
dangerous-load trio, size/weight sign distinctions incl. actual-mass vs goods-3.5 t vs per-axle),
"parking signs in practice" section (urban 8:00–20:00 default, side-of-road, next-intersection,
tow-away, P family, passo carrabile, disability placard, street cleaning), end-signs figure row,
DO-NOT-ENTER naming; figures 4 → 30 per language. Answer doubts: none (docs/answer-flags-04.md).
Versions → 20260620u.

### Addendum (Topic 04, user flags @20260630c, 2026-07-01)

**Bank-wide style decision — `transito` verb.** Reader confusion (#20025): American English "to pass"
reads as *overtake* (sorpasso), so "a vehicle is allowed to pass" was ambiguous. Ruling:

| Italian | American English | Notes |
|---|---|---|
| transito (a vehicle travelling along the road, VERB) | **proceed** | "may proceed / may not proceed"; reserve **pass / overtake** strictly for *sorpasso* |

Swept bank-wide: modal + intransitive "pass/passes" → "proceed/proceeds" (168 fields across 10
topics). **Kept unchanged** (transitive/overtake): "pass a tram/vehicle on the right/left" (sorpasso —
#19133/#19142/#23505), "pass the obstacle / the safety island / over it" (go *past* an object — proceed
is intransitive), and all "overtake/overtaking/passing" (sorpasso). Precedence-order "pass first/before/
after" → "proceed …" (clearer, in scope). Exclusion rule used: skip when the token after the verb is
`a|an|the|on the right|on the left|over`. **The intransitive/transitive split is the safe discriminator
for future topics** — do not blanket-replace "pass".

**Broken number-split translations** (pre-existing): "autotreni larghi 2,30 metri" had been rendered
"…combination 2 may pass.30 meters wide" — a period inside the figure split the sentence. Found and
fixed #19798 and #19809 (3,50 m). Pattern to grep after any pass-sweep: `(pass|proceed)\.\d`.

**Sign-class taxonomy trap** (#19927, #19993): the bank asks whether a no-parking / disability-parking
sign "is a segnale di prescrizione" (VERO) while the topic is titled *Segnali di divieto*. Prohibition
signs are a **sub-family of regulatory (prescrizione) signs** (with precedenza and obbligo). Now stated
at the top of the Topic-04 review and in both explanations. Reuse of the T03 prescrizione≠obbligo note.

**Explanations that were factually wrong (fixed):**
- #19639 (no-passing-for-trucks-3.5t): old EXP said the sign "prohibits overtaking of motor vehicles, so
  cars may not overtake trucks" — false; 4114 binds only goods vehicles >3.5 t. New EXP leads with the
  real error (overtaking is on the LEFT; no passing on the right) and corrects the scope.
- #19925 (sosta + horizontal double-arrow panel): old EXP called panel B a tow-away marker. It is the
  **continuation/extent** panel (ban continues along the stretch), which is exactly why "permanent
  no-parking" is FALSO. Panel meanings now taught: **↑ start · ↓ end · double-arrow (H or V) = continues
  · cross (†) = holidays (giorni festivi)**.

**Term/gloss reaffirmations applied in questions (not new, but were still wrong here):**
- `carrello-appendice` → **small utility trailer** (was "semi-trailer" at #19748) — registered as part of
  the towing car; that is why the no-trailer sign lets it proceed.
- `autosnodato` → **articulated bus**, glossed on first use ("extra-long two-section bus joined by an
  accordion-style bend") — user did not know "articulated bus" (#19640).
- `complessi di veicoli` → **combination vehicles (a towing unit and its trailer)** — "vehicle
  combinations" read oddly to the user (#19822).

**Review pedagogy added (EN+IT), driven by repeated user misses:** single-car sign = **all autoveicoli**
(cars/trucks/buses; only two-wheelers exempt — #19714); size/weight limits must be **strictly exceeded**,
not met (#19818); **total mass vs mass-per-axle** are different signs (#19840/#19846); one-vehicle-at-a-
time bridge panel (#19831); overtaking-always-on-the-left + no-passing lapses at each intersection
(#19547); urban vs extra-urban vs no-stopping **hours** table; tow-away **not automatic** (#19907);
places where no-parking is the **general rule** so no sign is posted (#19928); **solo/sempre** absolute-
word trap cue (#19838). Answer doubts: none. Versions → 20260701a.

---

## Topic 02 — Segnali di obbligo: review-only touch-up (2026-07-01)

Scope note: this was a **review (study-notes) upgrade only**, applying the standards accumulated
in Topics 16/03/04 to the Topic-02 review ahead of its full content pass. `questions.json` was
not touched; the topic still needs its exhaustive per-statement run (translations, explanations,
gap analysis against all 59 cards / 661 statements, incl. the figure-less cards 4605–4622).

### Style decisions (reusable)

| Term | Ruling | Notes |
|---|---|---|
| obbligatorio (in review prose) | **mandatory** | "compulsory" leans British; also matches the topic's own EN title "Mandatory signs". Sweep other reviews during their runs |
| percorso riservato agli animali da sella | bridle path — gloss on first use | plain-words gloss per the *a cingoli* pattern: "a path for riders on horseback"; the sign shows horse WITH rider |
| preavviso (curved-arrow obligation signs) | advance notice / "announces … ahead" | the now-vs-ahead contrast (straight arrow orders HERE; curved arrow announces at the coming junction) is tested across 4150/4156/4157/4189 — teach it explicitly |

### Applied to the Topic-02 review (EN+IT)
- Full visual treatment per the T03 "illustrate sign topics generously" addendum: 3 → 27 embedded
  figures per language, all visually verified against their cards (direction arrows at-junction vs
  preavviso; direzioni consentite; passaggio obbligatorio L/R/both; rotatoria A/B obligation-vs-warning
  composite 4171; min-speed 30 + end sign + Topic-04 speed-limit look-alike 4111 as cross-topic anchor;
  path family incl. separated-vs-shared contrast 4180/4181 and all five end signs; chains; DOGANA /
  ALT POLIZIA / ALT STAZIONE; truck-panel composite 4189).
- Taxonomy paragraph (reuse of T04 @20260630c): obbligo signs are a sub-family of **regulatory**
  (*prescrizione*) signs; "is a regulatory sign" is VERO for a blue circle (tested at 4150/4151/4156).
- US convention bridge (T03 color-bridge pattern): the US has **no blue-circle family**; blue circle ≈
  white US regulatory rectangle; blue number = MINIMUM SPEED plate, never a limit.
- Trap callout: now-vs-ahead (*preannuncia/preavviso*) + solo/sempre/mai absolutes.
- Corrections to prior review text: end-of-obligation bar described as **red** (was colorless
  "diagonal line"); min-speed sign also **bars vehicles that cannot hold the speed** (4172); after the
  end sign the road's normal maximum limits apply (4174); ALT signs expanded with the
  stop-even-with-nothing-to-declare and stop-not-just-slow points (4186/4187).

---

### Addendum (Topic 02, user flags 2026-07-02) — two bank-wide sweeps + flagged fixes

| Italian | American English | Notes |
|---|---|---|
| segnale di prescrizione | **regulatory sign** — one rendering, bank-wide | "prescriptive sign", "prescription sign", "mandatory instruction sign" all swept (was drifting across 4 renderings). EN explanations of "è un segnale di prescrizione" statements now TEACH the taxonomy (obbligo ⊂ prescrizione, with divieto and precedenza); the Italian explanation carries the same rule WITHOUT US-bridge content |
| circolare / circolazione (bank-wide sweep) | travel / drive · traffic | 380+ fields swept per the reviewer's request; **kept**: roundabout contexts ("traffic circulates", per the T03 exception), **blood circulation**, air **recirculation**, coolant/oil **circulating in the engine**. Verb map used: vehicles travel; drivers drive; two-wheeler riders ride; "in order to circulate" = "in order to be driven"; "la circolazione di X è vietata" = "X are barred" |
| piazza (roundabout contexts) | **piazza** — keep the Italian word | "square" is ambiguous in AmE; Americans know "piazza" (user ruling, #20283; also applied at #20275, #18542) |
| fascia/luce gialla "amber" | (flashing) **yellow** | "amber" is BrE traffic vocabulary (#20484 explanation) |
| prescrizione (police illuminated text, #22963) | instructions | not "prescriptions" |
| valore prescrittivo (#25288) | regulatory force | not "prescriptive value" |

Other patterns applied:
- **"What it does require" convention** (reviewer request, #20091/#20236): when a VERO statement is
  phrased negatively ("does not permit X"), the explanation must name the sign and state the
  POSITIVE obligation that makes X impossible. Apply in all sign topics.
- **Preavviso placement taught** (#20035): curved-arrow = advance form posted BEFORE the
  intersection; straight-arrow form stands at the intersection. Both EN and IT explanations.
- **Stems unified in Topic 02** ("The signal shown"/"The depicted sign"/"The illustrated sign" →
  "The sign shown") per the T03 ruling; other topics still pending their own runs.
- **fine prescrizione** family: "end-of-prescription" → **end-of-restriction** swept (T04 glossary
  term, was still un-applied in ~10 divieto/obbligo explanations).
- vocabulary.json: `circolare` hover now "to flow / to circulate (= to travel, drive)" with a
  usage note; `circolazione` (Norme topic) → "traffic / traffic flow" (reviewer request, #20296).
- Artifact greps run to zero: "at at least" (3 fixed), doubled words, `(pass|proceed|travel)\.\d`.
- App-structure answer for the reviewer's L3 question (#20050): yes — every statement has a separate
  `explanation_it`, shown when the app is in Italian; US-bridge teaching lives only in the EN field.

Log: 66 override fields (9 flagged numbers + their boilerplate siblings) + ~380 mechanical fields
across 15 topics. Answers untouched. Versions → 20260701e.

---

### Addendum (Topic 02, user flags @20260701e batch 2026-07-02T10:37) — follow-up sweeps

Five of the six flagged strings were already fixed at v20260701e (the reviewer's device was still
showing cached pre-sweep text — the quoted English no longer existed in the bank). The batch still
surfaced real, un-swept classes:

| Italian | American English | Notes |
|---|---|---|
| prescrivere (a sign, VERB) | require / impose / order | never "prescribe" for signs ("The sign shown requires stopping…", "imposes a ban on…"). Participle "prescritto" for rules/cases/inspections → required / permitted / standard; KEEP "prescribed" only for corrective lenses (medical, #24614/#24662) |
| In presenza del segnale raffigurato | Where this sign is posted, | T03 ruling finally swept bank-wide (34 fields incl. the "…and a three-light traffic light" family → "Where this sign is posted together with a three-light traffic light,") |
| In presenza della segnaletica (orizzontale) | Where the road markings shown in the figure are present, | |
| luce gialla (traffic light) | yellow | "amber" is BrE for signals — swept (~25 fields, incl. arm-signal equivalences). KEEP "amber" for dashboard tell-tales where the Italian is *giallo ambra* / *spia* (#24296, #24195): amber is the standard American automotive term there |
| autoarticolati | tractor-trailers | still leaking as "articulated vehicles" (#22068) |
| autovetture | cars | "motor cars" is BrE (#20288, #23853) |

Also: chains-vs-winter-tires taught (#20337 reviewer request) — the two are ALTERNATIVES and either
alone satisfies the sign; added to the explanation (EN+IT) and to the Topic-02 review (EN+IT).
Explanation and stem stragglers fixed (#20287 "Signal (A)"/"extraurban", #20439, #18637
"Motor cars (autoveicoli)" leftover from T16, #23721 "manner prescribed by the signage").

Verification: leftover scans at zero for prescrib* (non-lens), "in the presence of the sign*",
amber (non-dashboard), circulat* (non-exempt), "motor cars". ~105 fields. Answers untouched.
Versions → 20260702a.

---

## Topic 05 — Segnali di precedenza: review-only touch-up (2026-07-02)

Scope note: **review (study-notes) upgrade only**, ahead of the topic's full content pass
(21 cards / 243 statements still need their per-statement run). Same treatment as Topic 02.

Applied to the Topic-05 review (EN+IT):
- Full visual treatment: 5 → 15 embedded figures per language, all visually verified against
  their cards (yield/STOP; both advance-notice panels 4193 "320 m" vs 4194 "STOP 320 m";
  priority-road diamond + small-format/course-panel composite 4207 A/B + end sign; the
  narrow-section pair 4196/4208 side by side; junction triangles 4195/4201/4202/4203 and the
  two confluenza merges 4204/4205).
- Taxonomy paragraph: precedenza ⊂ prescrizione ("is a regulatory sign" is VERO —
  tested at 4191/4193/4197).
- US bridge (T03 color-collision pattern): yield and STOP are identical to the US; the
  **yellow diamond is the false friend** — US warning shape vs Italy's priority road, a sign
  class the US does not have.
- Trap callout: priority never excuses caution (4208 FALSO trap); working light overrides the
  sign (off/flashing yellow = sign rules — drilled on 4198/4209); triangles only announce.
- Narrow-section pair now taught by **color grammar** (red-bordered circle restricts YOU →
  you yield; blue square = indication family → you have priority) — replaces the previous
  "your black arrow yields to the red arrow" sentence, which asserted an arrow identity the
  bank never tests and which contradicted the figure.
- Corrections: "flashing amber" → "flashing yellow" (review had survived the bank sweep);
  priority-road facts grounded in 5047 (never marks an autostrada; repeated small before/after
  junctions; cross streets carry YIELD/STOP; moderate speed anyway); end-of-priority may be
  followed by yield/STOP; merge signs: ramp carries YIELD, left-merge on one-way carriageways.

---

## Topic 05 — Segnali di precedenza: FULL content pass (2026-07-02)

All 21 cards / 243 statements reviewed (translations + EN and IT explanations); ~330 field
edits. All 21 figures had been visually verified in the same-day review touch-up.

### New Italian → American English term mappings

| Italian | American English | Notes |
|---|---|---|
| rampa (di raccordo/svincolo) | ramp | "slip road" is BrE |
| confluenza (sign name context) | merge | not "confluence" |
| strettoia | narrow section / narrowing | reaffirmed; "bottleneck" replaced for consistency |
| binario morto | dead-end rail siding | not "dead railway line" |
| piazzola di sosta | pull-off area | not "rest area" (that's area di servizio/sosta) |
| segnale di indicazione | information sign | not "informative sign" |
| diritto di precedenza (noun) | the right of way | open form + article enforced topic-wide; hyphenate only attributively (right-of-way sign/rules) |
| dare la precedenza | yield | "give right-of-way / give-way" tokens purged topic-wide |
| sensi unici alternati | alternating one-way traffic | "alternating single-way" purged |

### Patterns (reusable)
- **Italian explanations can carry their own calques**: this topic's `explanation_it` fields had
  "cartello" (for segnale), "priorità" (for precedenza), "ambra" (BrE amber leaked INTO the
  Italian), "Contrassegna" (calque of "marks"), "filare" (wrong word for fila), a literal
  English "whether", an invented sign name "CEDERE IL PASSO", and "(exclusively)" glosses.
  Review EXI with the same rigor as EN — sweep list now established.
- **Wrong sign-class in EN despite correct IT** (20560/20670 said "mandatory sign" for
  prescrizione): the classification statements deserve a targeted grep in every topic.
- **Officer > light > sign** precedence chain is heavily drilled (4198/4209): the review must
  state all three levels, not just light-vs-sign.
- Class-statement explanations upgraded to the T02 teaching template (precedenza ⊂ prescrizione)
  at 20482/20509/20527/20560/20670.

### Review additions (EN+IT)
Yield/STOP stand AT the junction (150 m belongs to the advance versions); autostrada yield at
ramp end; STOP for poor-visibility/dangerous junctions and railroad crossings; junction
triangles posted well back (never 25–50 m) and crossroads versions never on autostrade;
officer overrides light and sign alike.

### Answer flags
docs/answer-flags-05.md — **none** (all 243 answers consistent with the CdS).

---

## Topic 07 — Segnaletica orizzontale; segni sugli ostacoli: FULL pass + review rewrite (2026-07-02)

All 47 cards / 259 statements reviewed; ~280 field edits. All 40 figures visually verified.
Review rebuilt to house standards: 4 → 20 captioned figures per language, incl. the tested
island-vs-guide-lines contrast (4220/4221, same junction shown both ways) and the
continuous-vs-broken placement pair (4216/4217).

### New Italian → American English term mappings

| Italian | American English | Notes |
|---|---|---|
| pavimentazione | road surface | FALSE FRIEND: was "sidewalk" in ~14 statements (incl. the whole 5066 inscriptions card) — "pavement" is BrE for roadway, and the machine translation went one worse. Also leaked INTO explanation_it as "sul marciapiede" |
| striscia discontinua | broken (dashed) line | "discontinuous" purged topic-wide |
| striscia di mezzeria / di mezzo | center line | "central stripe", "median line" variants unified; EXI "linea mediana" → "striscia di mezzeria" |
| striscia laterale discontinua | broken white side line | "lateral stripe" purged |
| strisce di guida | guide lines | "guide stripes" purged |
| rallentatore | speed-reducing device | dosso artificiale = speed bump (obstacle, yellow-black); EXI had "gobba artificiale" and "riduci velocità"(!) |
| servizio pubblico di linea | scheduled public service | "public line service" calque purged |
| segnaletica (in figura) | road markings (shown in the figure) | "signage" purged; verb agreement fixed after the swap |
| iscrizione | inscription / wording painted on the road | |

### Patterns (reusable)
- **Figure-mismatched explanation on variant subcards** (20927: base-card statement got the
  SIBLING subcard's explanation — a speed bump — instead of its own figure, the "50"
  inscription). After the variant split, check that each statement's explanation matches ITS
  card's figure, not a sibling's.
- **explanation_it contradicting its own answer** (20887: EXI said a U-turn does NOT require
  the other lane while EXP correctly said it does; 20889: EXI said "senso unico" for a
  doppio-senso statement). The EXI sweep must include answer-consistency, not just terminology.
- **sosta/fermata drift inside EXI** (20783/20791 used "sosta" for the brief stop and
  "parcheggio" for sosta — the exact distinction the card tests).
- US bridge for this topic: **US yellow-center-line ≠ Italy** — Italian center lines are white
  even between opposing flows; yellow = special/temporary. Stated explicitly in the review.

### Review additions (EN+IT)
Studs supplement-never-replace; one-wheel crossing counts as crossing; straddling banned even
on broken lines; continuous-line placement logic (before junctions/crosswalks/curves, uphill on
bumps) vs broken after; one-way vs two-way center-line meaning (left lane = overtaking; U-turn
banned on one-way regardless); broken side lines (pull-off / driveway / acceleration lane /
secondary-road edge) vs continuous edge line and autostrada emergency lane (3-hour breakdown
limit, barred to motorcycles too); stop line completed by STOP inscription (never with YIELD);
zebra rules (secondary extra-urban warning sign, yellow zigzag precursor); arrows always white;
island-vs-guide-lines contrast; regulation inscriptions list (BUS/TAXI yellow, PL + cross,
place names; no advertising); "50" = recommended speed; obstacle markings section (yellow-black
curbs and speed bumps) finally covering the topic title's second half.

### Answer flags
docs/answer-flags-07.md — **none** (all 259 answers consistent with the CdS).

---

## Topic 15 — Segnalazioni semaforiche; segnalazioni degli agenti: FULL pass + review upgrade (2026-07-02)

All 28 cards / 252 statements reviewed; ~130 field edits. All 22 figures visually verified.
Review upgraded in place (it was already close to house standards): 8 → 13 figures per language.

### New Italian → American English term mappings

| Italian | American English | Notes |
|---|---|---|
| paletta | signal paddle (paletta) | NOT "baton" (that's the truncheon) — was in questions AND the review |
| semibarriere | half-barriers | "semi-barrier" purged; EXI had "semicatene" and "semicarra"(!) for semibarriere |
| pannelli distanziometrici | countdown panels | "distance marker panels" unified to the T03 term |
| stazione ferroviaria | train station | not "railway station" |
| metropolitana | subway | not "the underground railway" |
| a richiesta degli agenti | at an officer's request | "upon request by agents" calque purged; agenti = officers |
| bollo | vehicle ownership tax (bollo) | not "road tax sticker" |
| semaforo (in explanations) | signal / light | "semaphore" anglicism purged |
| in servizio di linea per trasporto di persone | on scheduled passenger service | |

### Patterns (reusable)
- **"amber" hides in explanation_it as Italian**: the EN amber→yellow sweep had left ~25 EXI
  fields saying "ambra/l'ambra fissa" — not Italian usage (semaforo lights are *gialle*).
  Gender-aware swap needed (l'ambra fissa → il giallo fisso). Grep EXI for "ambra" in any
  topic that mentions traffic lights.
- **Figure-family mixups in explanations**: 21133 answered about types B/C when the statement
  is about type A; 21014/21015 explained the yellow light without naming the red-light pair
  that actually guards movable bridges/ferries. When a card names a lettered variant (A/B/C),
  check the explanation addresses THAT letter.
- **21100-style scope error**: "not only rail vehicles" was explained as "applies to vehicles
  in general" — the white-bar light applies to scheduled public-transport vehicles, not
  everyone. When correcting a 'solo' trick, state the true scope, not just the negation.
- US bridge for this topic: **no right turn on red** (tested at 20975); single flashing red
  does not exist (pair of alternating reds = absolute stop); arrows come in red/yellow too.

### Review additions (EN+IT)
US-bridge paragraph (right-on-red, flashing-light grammar, red X); trap callout; lane-signal
vs reversible-lane distinction + reversible figure; bicycle light cyclists-only; white-bar
light applies to ALL scheduled transport (horizontal=stop, vertical=go, yellow triangle);
type A vs B/C flashing yellows + figure row (4255/4246/4256/4257); green wave urban-only and
advisory-only; red-light pair: at the crossing itself, vehicles AND pedestrians, on until the
train has passed; paletta fix ("baton" → signal paddle); the may-not-demand list (first-aid
kit, ownership certificate, codice fiscale, bollo).

### Answer flags
docs/answer-flags-15.md — **none** (all 252 answers consistent with the CdS).

---

### Addendum (Topic 05, user flags @20260702l "prioritySignsReview", 2026-07-02)

Six flags, all addressed. Rulings and patterns worth keeping:

- **Do NOT translate contrastive "ma" in exam scenarios as "unless"** (#20578): "abbiamo la
  precedenza se il semaforo è verde, ma l'agente ci ordina di fermarci" is a FALSO whose truth
  value flips if rendered "…unless the officer orders us to stop" (that reading is TRUE). Keep
  "but" and use the **progressive** ("but the officer **is ordering** us to stop") so the clause
  reads as a scenario description, not an exception clause. Applied across the whole
  officer/light drill family (20574/78/79, 20702/03/07/08).
- **Deliberately contorted exam Italian deserves a review note**, not silent smoothing
  (#20702): the Topic-05 review now has a "How the exam words these" callout teaching the
  scenario-description reading + officer-outranks-everything rule.
- **Priority to the right is a first-class US bridge** (#20581, reviewer-drafted): where nothing
  decides, Italy defaults to yielding to the right, and road size counts for nothing. Added as
  its own US-bridge paragraph (EN+IT) and to #20581's explanation. Candidate reuse: Topics 13
  (norme di precedenza) and 25 (esempi di precedenza) MUST carry this bridge too.
- **Sign+light coexistence needs US context** (#20506): American junctions have either a stop
  sign or a light; Italian junctions keep the sign posted permanently as the fallback for
  light-off/flashing-yellow. Added to the explanation and the review's lights section.
- **"One road, one story"** (#20474): the yield/STOP family and the diamond/priority-triangle
  family never precede one another — a road either has priority or it doesn't. Now a review
  callout; #20474's explanation names what DOES precede the yield sign (its advance notice).
- **comporta la presenza di X** → "Where the sign is posted, the roads that cross it carry X"
  (#20680) — not "entails the presence of X" (calque).

---

## Topic 01 — Segnali di indicazione: FULL content pass + review rewrite (2026-07-02)

All 63 cards / 603 statements reviewed; ~370 field edits. All 63 figures visually verified.
Review rebuilt to house standards: 0 → 30+ captioned figures per language, now covering the
whole tested inventory (the old review covered barely half the concepts).

### New Italian → American English term mappings

| Italian | American English | Notes |
|---|---|---|
| senso unico frontale / parallelo | head-on / parallel one-way sign | frontale had been rendered "one-way road ahead" — the two FORMS are what the cards test |
| stazione ferroviaria | train station | reaffirmed (was "railway station" here) |
| pronto soccorso (facility) | emergency room / first-aid post | "medical emergency department" purged |
| chiave inglese | wrench | "spanner" purged |
| pesa / impianto di pesatura | weigh station | not "weighbridge" |
| parcheggio (in EXP prose) | parking lot | "car park" purged again — it keeps reappearing |
| autobus extraurbano | extra-urban public-transport bus | not "long-distance bus" |
| autotreni ed autoarticolati | truck-and-trailer combinations and tractor-trailers | was "articulated vehicles and truck-trailers" / "articulated trucks and semi-trailers" (both wrong mappings) on 4321/4329 |
| scendere (dai mezzi) | get off | "alighted" resurfaced (banned since T16) |
| tabaccheria | tobacco shop | not "tobacconist's shop" |

### Patterns (reusable)
- **21691-class mistranslation**: "incrocio a raso" rendered "railroad crossing" — the same
  swap as T16's #18446. Grep "a raso" against "railroad" in every remaining topic.
- **The autotreno/autoarticolato mis-mapping keeps recurring** (T04 glossary entry, still
  violated here twice). When a card names the pair, check both words individually.
- **EXI typo class**: "preselzione" ×8, "cartello" again, "linee parallele" for file parallele,
  "ciclopedonale" for ciclabile, "commissariato" for Stazione dei Carabinieri.
- US bridge for this topic: **US green = any guide sign; Italian green = autostrada
  specifically** — color encodes road type (white/blue/green/brown/yellow).

### Review rewrite (EN+IT) — concepts newly covered
Number-trap callout; progressive-distance sign read left/right; junction preavviso inserted
symbols (no-entry branch, warning-triangle branch, brown/green patches); preselection while
lines still broken; senso unico frontale vs parallelo + U-turn ban; lane-use family (trucks
barred from left lane, autostrada rising minimums, urban bus lane, lane increase/reduction);
"start of" family (blue vs green autostrada symbol, motor-vehicles-only, tunnel rules, bridge
crosswind); crossings + SCUOLABUS dual use; dead end + advance version; U-turn structure;
indirect left turn; pull-off; ITALIA national-limits board; EU border no-stop (+ advance);
mountain-pass boards (open-with-chains = condition, closed = recommendation); advisory speed
and advisory truck route vs the yellow mandatory work-zone version; service pictograms incl.
pharmacy-green-cross contrast, park-and-ride numbers = bus lines, car-on-train, camper
discharge, SOS ≠ public phone, police contact board ≠ checkpoint; detour figure = LENGTH.

### Answer flags
docs/answer-flags-01.md — **none** (all 603 answers consistent with the CdS).

---

## Topic 06 — Segnali complementari; segnali temporanei e di cantiere: FULL pass + review rewrite (2026-07-02)

All 19 cards / 180 statements reviewed; ~135 field edits. All 19 figures visually verified.
Review rebuilt: 0 → 16 captioned figures per language; this topic is the designated home of
the yellow-is-Italy's-orange US bridge (T03 addendum), now stated in the intro.

### New Italian → American English term mappings

| Italian | American English | Notes |
|---|---|---|
| segnale complementare | complementary sign | not "supplementary sign" (that's pannelli integrativi, Topic 08) — the EXI even labeled one "pannello integrativo" (21982) |
| ponte mobile | movable bridge | "drawbridge" purged |
| discarica | landfill | EXP said "tip" (BrE) |
| a senso unico (tunnels etc.) | one-way | "single-direction" purged |
| autorimessa | garage / vehicle storage facility | EXI had "officina" (workshop) for it |

### Patterns (reusable)
- **EXI inversions continue**: 21926 swapped the two halves of its own contrast ("they mark the
  crossing approach, not the road edges" — backwards); same class as 20887 (T07). Always read
  the EXI's contrast direction against the EXP.
- **EXI howler class**: "usato per marcire un ostacolo" (to ROT an obstacle, for segnalare) —
  one-letter typos that change the verb entirely; read EXI aloud.
- "ambra" again in EXI (21888, 21993) despite two sweeps — it keeps being reintroduced wherever
  "flashing yellow" gets translated; permanent grep candidate.

### Review rewrite (EN+IT) — concepts newly covered
US bridge (yellow = US orange) in the intro; trap callout (temporary overrides permanent;
advisory routes advise; 7 t = mass); temporary light triangle with flashing-yellow center;
advised truck direction vs 7 t detour board; lane-closure vs category-assignment vs mobile
composite panels; barrier extras (broken crossing gates, steady red lamp); cones =
short-duration only; work-vehicle passing-side panel; delineator family (one-way vs two-way
versions, one-way tunnels, snow roads; reflective, never self-lit, never lane dividers);
chevrons in the bend itself (white-red = temporary), T-junction double version, obstacle
bollard on the carriageway (traffic-island start, flexible base), hairpin counter.

### Answer flags
docs/answer-flags-06.md — **none** (all 180 answers consistent with the CdS).

---

## Topic 08 — Pannelli integrativi dei segnali: FULL pass (2026-07-03)

All 74 cards / 261 statements reviewed; only ~25 field edits — the cleanest topic yet, because
its content and review were substantially rebuilt during the Topic-04 flag sessions. All 53
figures (base + variant) visually verified against the review's captions; review already at
house standards (US bridge on †/⚒, trap callout, 26 figures per language) — no review changes.

### Findings
- **One figure-mismatched explanation** (22056: described the sibling subcard's truck ban while
  its own figure is PARKING + working-days panel) — the 20927 defect class again; now found on
  three topics. The check "does the explanation match THIS subcard's figure" stays mandatory.
- pala meccanica → **loader** (was "mechanical shovel", calque) — EN/EXP on the 4364 family.
- EXI polish: "giorni feriali" → "giorni lavorativi" (align with the statements' term),
  "PERICOLI DIVERSI/VARI" → ALTRI PERICOLI (official name), "un depositeria" → "una depositeria",
  "incrocio di binari" → "attraversamento di binari".

### Answer flags
docs/answer-flags-08.md — **none** (all 261 answers consistent with the CdS).

## Topic 11 pass — Limiti di velocità; pericolo e intralcio; passaggi a livello (2026-07-03)

- Full pass: 21 cards / 256 statements; ~185 field edits. Answer flags: none.
- **Meaning-inverting fixes (EN):** 22363 "clutch pedal released" → **pressed down**
  (frizione abbassato); 22466 "low-beam" → **high-beam** headlights (proiettori a luce
  abbagliante). Both had flipped the tested claim.
- **Meaning-inverting fixes (EXI):** 22341 "quadricicli leggeri" → **non leggeri**;
  22332/22334 "motoveicolo" → **autoveicolo**.
- **incrocio-vs-sorpasso class again** (see Topics 01/06): EXIs 22300/22316/22441 said
  "il sorpasso dei veicoli" for IT "l'incrocio con i veicoli" (meeting, not overtaking) —
  rewritten; EN/EXP "passing oncoming vehicles" → "meeting oncoming vehicles".
- **carrello appendice** (glossary term "small utility trailer") mistranslated two new
  ways in this topic: "cars with trailer" and "motor vehicles with trailer coupling"
  (22366/72/22417/19/30). EXPs "luggage trailer" aligned to "small utility trailer".
- **autotreni** "articulated trucks"/"Road trains" → truck-and-trailer combinations
  (autotreni) per glossary (22412/22423); EXI calques "treni stradali" / "treni di
  strade"(!) → "autotreni".
- **US-English sweeps (topic-scoped):** extraurban → extra-urban; rural → extra-urban;
  built-up area(s) → town(s); railway → railroad (with "sede ferroviaria" → "railroad
  track area", "stazione ferroviaria" → "train station"); "the rails" → "the tracks"
  (binari); channelling/channelled → channeling/channeled; pram → stroller; "have got
  out" → "have gotten out"; roadworks → road work; line bus → scheduled bus.
- **Right of way (noun, open form)** enforced: "having/with/without right-of-way" →
  "…the right of way"; "allow right-of-way to vehicles entitled to it" → "yield to
  vehicles that have the right of way".
- **autovettura → cars** (was "motor vehicles") in seven towing stems (22415/20/27/28/58/59/71).
- **macchine operatrici → work machines** (was "operating machines"/"work vehicles"),
  22401/22472.
- **file parallele → parallel lines** (was "parallel lanes/files"), 22462.
- EXI cleanups: roulotta→roulotte; passo carraio→passo carrabile; aree/zone
  urbanizzate→centri abitati; "un'eccesso"→"un eccesso"; "servo freno"→"servofreno";
  "spie di pericolo"→"luci di emergenza" (hazard lights); English glosses inside EXI
  trap callouts removed ("(solely)", "(advisable)", …).
- Bank consistency: 22341 "heavy quadricycles" → "non-light quadricycles" (matches
  22407/22425 and the review).
- Review upgraded: figure 4385 (rear speed-marker discs) embedded with caption;
  new sections for towing vs carrello appendice, coasting-in-neutral, right-of-way
  contributory negligence; fog 50 km/h, hail=rain note, no-night-bonus traps;
  level-crossing wording aligned to bank (tracks, train station).

## Topic 12 pass — Distanza di sicurezza (2026-07-03)

- Full pass: 15 cards / 134 statements; ~35 field edits (this topic was cleaner than most).
  Answer flags: none. No figures in this topic.
- **Answer-contradicting explanations fixed:** 22561 EXP/EXI argued the safe distance
  DOES depend on the following vehicle (statement is FALSO — it doesn't; the driver
  behind keeps their own distance). 22656 EXP/EXI said the distance "must be at least
  equal to the braking distance" — wrong doctrine; it is at least the REACTION distance
  (matches 22552/22655). Both rewritten.
- **Statement-mismatch EXIs:** 22536/22548 said "spargisale" where the statement is the
  sgombraneve (snowplow). 22569 EXI was circular ("dipende dal freno di stazionamento…
  non dal freno di stazionamento") → brakes + tire grip.
- **New EXI calque class:** "La manovra dipende da 'anche/solo/sempre'" (nonsense) →
  "Il trucco è '…'" (22560/61/62, 22651, 22656). Watch for it in later topics.
- autotreni "road trains" → truck-and-trailer combinations (autotreni) (22550).
- US-English: mobile phone → cell phone (22589/22592); extraurban → extra-urban;
  "driving in a column" → "driving in a line of traffic" (22647).
- EXI orthography: "dei pneumatici" → "degli pneumatici"; "gobba" → "dosso" (22615).
- Translation accuracy: 22531 "andamento planoaltimetrico" → "layout and gradient";
  22653 "conducente che precede" → driver (not vehicle) ahead.
- Review upgraded: added the square-of-speed law (×4/×9/×16 — card 4401 tests it
  directly), braking-distance factor list (downhill/crest, locked wheels, rough
  asphalt, reflexes→reaction not braking), and a "when to increase the gap" section
  (line of traffic/chain collisions, tunnels, trucks, unstable loads, autostrada,
  before a pass).

### Answer flags
docs/answer-flags-09.md — **none** (all 134 answers consistent with the CdS).

## House standard — imperial bridges for distances (2026-07-03)

- Just as EN review text gives km/h with **mph in parentheses**, metric distances in
  EN review prose now carry a parenthetical conversion: **yards for road distances**
  (user's ruling: Americans know the yard and it is close to a meter — 20 m (22 yd),
  100 m (110 yd), 150 m (165 yd), 320 m (about 350 yd)).
- **SUPERSEDED 2026-10-28 (maintainer): every length in meters is given in YARDS,
  short ones with one decimal (1 m (1.1 yd), 5 m (5.5 yd)), and every length in
  centimeters in INCHES. Never feet or miles.** The line below is the old rule.
- **Feet for small dimensions** where fractional yards would be useless: 1 m (3 ft),
  1.5 m (5 ft), 2 m (6.5 ft), 2.30 m (7.5 ft), 5 m (16 ft), 10 m vehicle length (33 ft);
  child-seat height threshold 1.50 m (4 ft 11 in) — the exact US booster-rule phrasing.
- Scope: **review EN sections only** (body prose; summaries stay bare, image alt text
  untouched). Official `english_translation`/`explanation` fields stay metric.
- Applied across all 25 review files where meter values appear (03, 04, 05, 06, 08,
  09, 10, 11, 12, 14, 15, 16, 19, 21). Future topic passes must add these bridges.

## Topic 13 pass — Norme sulla circolazione; posizione; svolta; incroci (2026-07-03)

- Full pass: 68 cards / 379 statements (largest single topic so far); ~125 field edits.
  Answer flags: none. All 31 figures viewed (lane-letter diagrams, dual-carriageway
  variants, left-turn trajectory diagrams, preselection lanes, STOP/YIELD/priority signs).
- **Figure-mismatch class again (4th topic):** 22853 EXP/EXI was generic boilerplate
  with no connection to its figure (car in the LEFT preselection lane → cannot turn
  right). Rewritten from the figure.
- **Meaning-inverting/wrong-term fixes:** 22743 "luci di profondità" (= high beams)
  was translated "parking lights" in EN and "luci di posizione" in EXI — both wrong;
  22921 EXI said the autotreno "svolta a sinistra" (it swings wide, doesn't turn);
  22950/22957 EXI rendered "passaggio tra veicoli" as "sorpasso" (it's meeting/
  crossing) and "strada a forte pendenza" as "in salita"; 22958 EXI invented "posto
  di sorpasso" for piazzola di scambio; 22973 EXI "veicoli in sorpasso" for "in
  transito"; 23021 EN "Travel trailers" for autocaravan (= motorhomes); 23025
  EXP/EXI "side" for "coda" (tail); 23001 EXI overclaimed "visione a 360 gradi".
- **Doctrine fixes:** 22886 (ROUNDABOUT sign alone = default yield-to-right, not
  yield-both-ways) and 22887 (flashing yellow = caution + normal priority rules)
  had muddled explanations; 23000 EXP now states the real penalty (2 points, not 4).
- **Recurring classes:** "La manovra dipende da '…'" calque (5 more hits — sweep is
  now standard); "Nessun inversione" → "Nessuna" (gender, 4 hits); autotreni →
  truck-and-trailer combinations (7 stems); file parallele EN renderings unified to
  "parallel lines"/"parallel-line driving" (a dozen variants: parallel files/lanes/
  file traffic); EXI "circolazione su corsie parallele" → "marcia per file parallele".
- **Right-of-way noun sweep:** has/have/giving/give right-of-way → open forms or
  "yield to"; attributive "right-of-way rules" kept.
- Misc: sostare=park not stop (22673); "acoustic signal"→horn; "signaled
  intersection"→traffic-light-controlled; "transited"→passed; Distogui→Distogli;
  sopragiunga→sopraggiunga; "un inversione"→"un'inversione"; extraurban→extra-urban.
- Review upgraded to full house standards: 4 figures embedded with teaching captions
  (4422 lane letters, 4424 left-turn trajectories, 4427 preselection lanes, 4409
  reversing out of angled space); new "wrong preselection lane" section; U-turn adds
  (never on autostrada, broken line ≠ poor-visibility override, multi-maneuver OK);
  load adds (no 10% tolerances, 30 cm/12 in beyond position lights, red-and-white
  rear panel, front overhang never); police messages expanded (ACCOSTARE / ALT
  POLIZIA only-you / INCIDENTE ≠ risk zone / RALLENTARE = everyone); pedestrian-off-
  crosswalk and mirrors additions (adjust stationary, tail in right third, mandatory
  equipment). in/ft bridges included (50 cm→20 in, 30 cm→12 in, 4 m→13 ft).

### Answer flags
docs/answer-flags-13.md — **none** (all 379 answers consistent with the CdS; 23000
resolved in-place with the 2-point figure).

## Topic 14 pass — Esempi di precedenza (2026-07-03)

- Full pass: 49 cards / 415 statements; ~60 field edits. Answer flags: none.
  All 49 intersection diagrams viewed and every stated crossing order re-derived
  from the figure — the cleanest large topic so far (the fable-era explanations
  with embedded orders held up against the geometry).
- **Wrong-reasoning fix:** 23053 EXP/EXI claimed B "is on the priority road" at an
  unsigned T-junction — no sign exists in the figure; rewritten to the real reason
  (straight ahead, right clear; order B, H, C).
- **indifferentemente** in order stems = "in either order", NOT "indifferently"
  (23122). New glossary ruling for later topics.
- **Right of way noun sweep** (has/give right-of-way → open form or "yield to");
  "has the right side clear/occupied" → "has its right clear/occupied" (the house
  idiom for destra libera/occupata); EN "transits" → "passes".
- **EXI style sweep (regex):** "passa primo/secondo/terzo/ultimo" → "passa per …";
  "per X, non Y" → "per X, non per Y"; feminine "per seconda/terza" → masculine
  (subjects are veicoli); plus garbled 23331/23332, "dà la precedenza a nessun
  veicolo" → "non dà … ad alcun veicolo" (23096), "dopo che L/N ha passato" →
  "è passato".
- Review upgraded: added "The traps: what never decides the order" section (type/
  size/speed/service never matter; only trams on rails and sirens jump the queue;
  everyone moderates speed) and the impegnare/transitare/disimpegnare wording
  nuance (left-turner enters first, finishes last; never enter just to stop in the
  middle). Both worked-example captions (4485 N-A-R, 4495 A-C-L) verified against
  their figures.

### Answer flags
docs/answer-flags-25.md — **none** (all 415 orders consistent with the diagrams).

## Topic 15 pass — Norme sul sorpasso (2026-07-03)

- Full pass: 10 cards / 156 statements (incl. one 50-statement card, 4500);
  ~25 field edits. Answer flags: none. No figures.
- **Answer-contradicting EXI:** 23538 stated the FALSE claim as its own explanation
  ("lo spazio non dipende dalla lunghezza") → inverted to "dipende invece".
- **Scope-drift EXI:** 23498 said "autostrade" where the statement says "strade a
  due carreggiate separate".
- **Wrong-word EXIs:** "asserragliarlo" (= barricade!) → "stringerlo" (23577);
  "accendendo/si accendono gli abbaglianti" for lampeggiare → "lampeggiando"
  (23525/23544); "curva a destra" → "svolta a destra" (23551); "provenga da fronte"
  → "in senso opposto" (23467); "L'inattensione" → "La disattenzione" (23606).
- **Doctrine tightened:** 23586 EXP/EXI ("specific channelled conditions", vague) →
  one-way alone is not enough; right-passing needs the ahead-vehicle pulling left or
  parallel-line traffic. 23594/23595 dropped the invented "must maintain a constant
  speed" duty (the duty is: don't accelerate, keep right).
- **indifferentemente → "on either side"** (23535) — second hit for the Topic-14
  ruling. "acoustic signal" → horn (23478); "queuing behind" → "tucking in behind"
  (23560); "race in speed" → "race" (23481); 23513 EN restored "single or double"
  continuous line; 23480 EN rebuilt (the "cuts off" clause read backwards).
- Review upgraded: descending-side-of-crest exception (23519 tests it), the
  ambulance tuck-in ban, very-slow-vehicle stop duty, being-passed-with-oncoming
  behavior + shared liability, speed-limits-apply-while-passing, right-signal/
  right-edge vehicles still passable, dashed-next-to-solid nearer-line rule, and
  the no-ban list (snow, hospitals, service stations, driveways).

### Answer flags
docs/answer-flags-10.md — **none** (all 156 answers consistent with the CdS).

## Topic 16 pass — Fermata, sosta, arresto e partenza (2026-07-03)

- Full pass: 24 cards / 190 statements; ~50 field edits. Answer flags: none
  (answers all correct — the explanations were the problem).
- **Worst topic yet for answer-contradicting explanations — SEVEN rewritten:**
  23663 (no-raised-sidewalk rule is "leave 1 m", not "hug the right edge"),
  23675 (stated the false claim as its own reasoning), 23676 and 23773 (garbled,
  asserting fermata banned where only sosta is), 23682 and 23778 (both had the
  fuel-station rule backwards — the 5 m sosta ban applies ONLY during operating
  hours; 23778's EXP asserted the exact opposite of its FALSO answer), 23765
  (claimed sosta permitted on loading areas during set hours — contradicts 23760).
  Root cause is always the same: fermata/sosta conflation. Watch for it in Topics
  17+ wherever sosta rules appear.
- **23696 double-file fix:** the real reason the "sempre" claim fails is the
  two-wheeler exception in the sosta ban (art. 158), now stated.
- **Terminology:** passo carrabile was "vialetto"/"entrata carraie" in four EXIs →
  "sbocco di un passo carrabile"; banchine was calqued as "spalle"(!) → banchine;
  "sosta di emergenza" restored as the term in card 4528's EXIs (were "fermata di
  emergenza"/"sosta ordinaria"); "eccetto i ciclomotori" → "veicoli a due ruote"
  (23753); appogiacapo → poggiatesta; "negli sottopassaggi" → "nei".
- **EN sweeps:** raised curb → raised sidewalk; bumps → crests; urban traffic/main
  roads → urban through-roads (strade urbane di scorrimento); "on sidewalk" →
  "on sidewalks"; "entrance of gated driveways" → "outlet of driveways".
- Review upgraded: new "Bans that hit only the sosta" section (the exam's favorite
  trap), sosta di emergenza definition, figure 4514 embedded (NO PARKING = sosta
  only; double slash = both), one-way left-margin 3 m (10 ft) condition, 15 m
  (16 yd) bus-stop rule, double-file two-wheeler exception, marked-stall rule,
  license-points and no-sign-needed notes.

### Answer flags
docs/answer-flags-12.md — **none** (all 190 answers consistent with the CdS).

## Topic 17 pass — Ingombro; veicolo fermo; autostrade e strade extraurbane (2026-07-03)

- Full pass: 47 cards / 332 statements; ~90 field edits. Answer flags: none —
  including resolving the two pre-existing "image-substitution artifact" caveats
  (23943/23945): the variant figures genuinely show the yellow heavy-vehicle and
  long-vehicle panels, so FALSO is right; explanations rewritten from the figures.
- **Figure-mismatch class (5th topic):** besides 23943/23945, 23944's EXP described
  the load panel but its figure is the chevron work-vehicle panel with the
  pass-this-side arrow, and 23951's EXP described the ORANGE dangerous-goods plate
  while its figure is the plain yellow long-vehicle panel. All rewritten.
- **EXI inversion:** 24103 said the right mirror is NOT required when towing a
  caravan/T.A.T.S. trailer — its FALSO answer says it is. Fixed.
- **banchina calque:** seven EXIs rendered "corsia di emergenza" as "banchina"
  (and one hi-vis EXI as "sulla spalla"!) — all corrected; EXP "shoulder" aligned
  to "emergency lane".
- **bretelle = suspenders,** not "armbands"/"braces" (EN sweep, 6 statements).
- **Anglicism/garble EXIs:** "misjudichi", "scansionare", "zona di sweep", "Lo
  sloscio di liquido", "cambii", "il massimo cautela", "freno di inerzia (di
  soccorso)" — all repaired; 23971 EXI rebuilt (said "colonne di senso contrario"
  for same-direction columns); 23978 "motociclista" → ciclomotorista; 24114
  "(furgoni)" → (van); 24051 restored "fascia di ingombro".
- **autoarticolati → tractor-trailers** (23996/23997, EN+EXP); 23948 autotreno/
  autoarticolato EN+EXP+EXI aligned to glossary; EXI "convoglio stradale" removed.
- 23851 vest doctrine rewritten (obligation applies OUTSIDE built-up areas —
  EXP/EXI had it garbled); 23903 "fermata di emergenza" → sosta di emergenza.
- Review upgraded: four-panel figure gallery embedded with tell-them-apart captions
  (incl. 33/1203 = gasoline); triangle placement extras (occupied lane, junction
  within 50 m, never on the load, no in-town obligation); vest scope/limits; jam
  exit-only-from-500 m rule; no lifts/reversing/private towing on autostrada; and a
  much fuller towing section (trailer = separate vehicle, ratios 1/0.5, 20 cm
  mirrors, 7 m two-right-lanes, zero alcohol >3.5 t, inertia-brake behavior, load
  shift physics, liquid surge, no riding in caravans, jockey wheel, hitch care).

### Answer flags
docs/answer-flags-21.md — **none** (all 332 answers consistent with the CdS).

## Topic 18 pass — Uso delle luci; dispositivi acustici; spie e simboli (2026-07-03)

- Full pass: 22 cards / 176 statements; ~47 field edits. Answer flags: none.
  All 9 symbol figures viewed.
- **Systematic EXI inversion on card 4579 (high-beam symbol):** all six EXIs called
  it "anabbaglianti" — switch, tell-tale color, everything. Same inversion at 24248
  ("Gli anabbaglianti sono normalmente vietati" for the high-beam ban). Seven
  inversions fixed. English EXPs were right; only the Italian glosses flipped.
- **Answer-contradicting EXP/EXI:** 24236 asserted the left indicator IS used through
  a hairpin — its FALSO answer rests on a hairpin being road course, not a turn.
  Rewritten both languages.
- **Doctrine slip:** 24255 EXP/EXI claimed "position lights are sufficient" by day on
  the autostrada — low beams (or DRLs) are compulsory there. Fixed.
- **EXP garbles:** 24147/24154 said "high beams, not main beams" (same thing!) —
  rebuilt; "main beam" (British) swept to "high beam" across the topic; sentence-
  initial lowercase "low beams…" capitalized; 24203 "(low) beam" duplication.
- **EXI nonsense:** "L'abbagliamento degli abbaglianti" (5×) → "Il lampeggio degli
  abbaglianti"; "il freccia destra" → "l'indicatore di direzione destro";
  "in un'entrata" → passo carrabile; "zone urbane" → centri abitati.
- **carrelli-appendice ≠ semi-trailers** (card 4575, EN×3 + EXP×3 + EXI×3) →
  "small utility trailers (carrelli-appendice)" per glossary. (Card 4576's
  "semirimorchi" really are semi-trailers — left alone.)
- parallel queues → parallel lines (24242).
- Review upgraded: two symbol galleries embedded (beam-pair mnemonic: horizontal
  lines = high/blue, slanted = low/green; arrows; hazard double-triangle red and
  driver-activated) and the five red warnings with their precise meanings vs the
  tested distractors (temperature not level; not charging not flat; pressure not
  level/temperature; brake fault not ECU/service; seatbelt chime not switchable).
  Also added position-light colors, plate light not night-only, and headlamp
  aim/approved-bulb rules.

### Answer flags
docs/answer-flags-14.md — **none** (all 176 answers consistent with the CdS).

## Topic 19 pass — Dispositivi di equipaggiamento; cinture; seggiolini; casco (2026-07-03)

- Full pass: 12 cards / 135 statements; only 8 field edits — the cleanest topic of
  the project. Answer flags: none. No figures.
- Fixes: "L'appogiatesta" → poggiatesta (24326); quad "senza cabina" → "privi di
  carrozzeria" and the exemption phrased as "carrozzeria chiusa e cinture"
  (24404/24414, EN+EXI); "distortions" → sprains (distorsioni, 24425); pedivelle →
  "foot controls" not "pedals" (24426); 24429 EXI rebuilt (footwear, not generic
  "equipaggiamento"); 24449 EXI "non il riscaldamento" → "non il riparo dal freddo".
- Review upgraded lightly: protective-gear paragraph now carries the tested details
  (approval = cut/impact-abrasion tests, not washing, no color rule; glove
  fastenings; boot specifics — no loose laces, don't come off, ankle not knee, no
  steel soles).

### Answer flags
docs/answer-flags-19.md — **none** (all 135 answers consistent with the CdS).

## Topic 20 pass — Patenti; documenti di circolazione; sistema sanzionatorio (2026-07-03)

- Full pass: 18 cards / 230 statements; ~19 field edits. Answer flags: none.
- **Outdated-reform explanation:** 24550 EXP/EXI justified its FALSO with the
  pre-2024 rule ("applies in the first year") — rewritten: duration is now right
  (3 years), the quoted 55 kW/t / 70 kW figures are what make it false (current:
  75 kW/t tara, 105 kW for M1). Watch for stale pre-reform reasoning in Topics 21+.
- **EN inversion:** 24613 translated "perde temporaneamente" as "permanently loses".
- **Garbled/incomplete EXP-EXI rewritten:** 24552 (the 'solo' trick is that B covers
  more than cars — trucks/motorhomes/agricultural machines, not a seat-count quibble);
  24562 (B96 gives no entitlement to autosnodati of any mass); 24695 (validity bands:
  10 years is up to 50, NOT "under 70"); 24651 now states the recovery-course figures
  (6 points A/B, 9 higher, 20 cap).
- **EXI fixes:** carta di circolazione confused with certificato di proprietà
  (24461); "limiti di cilindrata e massa" for sagoma (24490/24505); "motoveicoli
  agricoli" → macchine agricole (24505/24540); "neop atentato ... limiti di velocità
  e carico" (24618); "due visita separate", "dopo i 80 anni", "mancata superazione".
- Review upgraded: recovery-course line (6/9 points, 20 cap; zero points ≠ revoca);
  withdrawal grounds expanded (unfixed load, missed revision deadline, not for
  paperwork lapses); suspension list extras (emergency lane, seized vehicle, forged
  insurance docs); revocation nuances (temporary loss ≠ revoca, foreign-license
  swap, ordered by Motorizzazione/Prefetto not police); revision authorities and
  no-special-permit rule; renewal details (no driving test, one visit covers A+B,
  Ministry confirmation, renewable past 80, no grace days, BS = 5 years to 70).

### Answer flags
docs/answer-flags-22.md — **none** (all 230 answers consistent with the CdS).

## Topic 21 pass — Comportamenti per prevenire incidenti; incidente (2026-07-03)

- Full pass: 13 cards / 126 statements; 15 field edits. Answer flags: none.
- All fixes were EXI precision: "ciclomotori" used for "veicoli a due ruote"
  (9 hits in the slippery-elements card — the statements cover ALL two-wheelers);
  "segnaletica stradale" for orizzontale (24699); "Gli restringimenti" (24702);
  24740 rebuilt (kept the wrong meaning of "distanziarsi dalla traiettoria");
  "fanalini" → proiettori fendinebbia / luce posteriore per nebbia (24754/24755);
  "lama d'acqua" → velo d'acqua (24720).
- Review upgraded: chains-required-roads ban for two-wheelers when snowing (24808
  tests it) and a new "Vehicle care — no do-it-yourself tuning" paragraph covering
  card 4629's grab-bag items (unbalanced brakes serviced, injection pump =
  specialist, no displacement increase, no ECU remap, oil light constantly on =
  fault).

### Answer flags
docs/answer-flags-18.md — **none** (all 126 answers consistent with the CdS).

## Topic 22 pass — Condizioni psicofisiche; alcol, droga, farmaci; primo soccorso (2026-07-03)

- Full pass: 21 cards / 141 statements; only 6 field edits. Answer flags: none.
- All fixes were EXI slips: "Fascenda" → Fasciare (24884); "consapevole" → cosciente
  for chest-trauma victims (24918/24919); "routinariamente" → "di norma" (24912);
  "comprometteranno" → compromettono (24845); "altri manovre" → altre (24926).
- 24883 kept its hedged explanation (the 'assolutamente' absolute is what fails;
  priority is stopping the bleeding) — noted in the flags file.
- Review touch: severe-bleeding bullet now includes sit-or-lie-down and never-walk
  (24880/24882 test it). Everything else tested was already covered.

### Answer flags
docs/answer-flags-17.md — **none** (all 141 answers consistent with the CdS).

## Topic 23 pass — Responsabilità; assicurazione RCA (2026-07-03)

- Full pass: 15 cards / 149 statements (incl. the 54-statement attention card 4716);
  8 field edits. Answer flags: none.
- Fixes: 31060 EXP/EXI opened with an irrelevant anxiety sentence (copy-paste from
  31016) → rebuilt on the actual claim (0.5 g/l never improves concentration);
  31058 EXP/EXI garbled ("rende la guida sicura inaffidabile") → rebuilt;
  "compensando il danneggiato" → risarcendo (24968/24972); "examination of the
  driving license" → revision/re-test (24979); "intasamento del traffico" →
  intralcio alla circolazione (31027).
- Review upgraded: added the tested items it lacked — direct compensation
  (risarcimento diretto: ≤2 vehicles, vehicle damage + minor driver injury,
  motorcycles included, no photo duty), certificate-only issuance duty, bonus-malus
  extras (motorcycles too, insurer-set, never auto-cancelled), theft-abroad
  re-report rule, no-device-needed for theft/fire policies, and the expired-RCA
  myth list (no short trips / Italy-only / pay-it-yourself; reinstatement needs
  insurance, not an inspection).

### Answer flags
docs/answer-flags-23.md — **none** (all 149 answers consistent with the CdS).

## Topic 24 pass — Limitazione dei consumi; ambiente; inquinamento (2026-07-03)

- Full pass: 15 cards / 103 statements; 46 field edits. Answer flags: none. No figures.
- Terminology rulings: marmitta catalitica → **catalytic converter** (never
  "catalytic muffler"); silenziatore (marmitta) → the gloss form "silencer device
  (muffler)"/"silencer (muffler)" is kept in EN translations, but free-standing
  "silencer" in explanations → muffler; "efficiente" (of the muffler) → "in good
  working order", not "efficient"; tettuccio scorrevole → **sunroof**; luci ad
  intermittenza → flashing lights; avvisatori/segnalazioni acustiche →
  **audible warning devices (horns)** — no "trumpets"; strisciamento dei
  pneumatici → **tire scrub**; filtro antipolline → pollen (cabin air) filter;
  colpo di acceleratore → blip of the throttle; marcia inserita → gear
  **engaged**; comando del ricircolo → recirculation **control**; opere stradali →
  road **structures**; carta di circolazione → registration document (was
  "registration card" in 25126); metano → natural gas (methane).
- EN spelling sweep: authorised→authorized, penalised→penalized.
- Calques fixed: "more fluid roads"→free-flowing roads (25070); "brake
  energetically"→brake hard (25077); "exhaust fume has a dark color"→exhaust
  smoke is dark in color (25117).
- EXI garbles fixed: "meno ristruttiva"→restrittiva (25114); "I bagagliai sul
  tetto"→I bagagli (25127); "se sibilano"→se fanno rumore in frenata (25092);
  "La ricircolazione"→Il ricircolo (25147); "Lasciare acceso l'aria
  condizionata"→accesa (25113); "e evitando"→ed evitando (25129/25130);
  duplicated parenthetical in 25138; "tetto panoramico"→tettuccio scorrevole
  (25073); "turbolenza della cabina"→nell'abitacolo (25143); "di tipo
  approvato"→omologato (25096).
- Review upgraded: added the two trap items (pollen/cabin filter protects the
  cabin, not the outside air; tunnel recirculation is GOOD for health) and
  aligned tire-scrub/strisciamento wording. The "accelerare = press the gas
  pedal" teaching note was already in place and untouched.

### Answer flags
docs/answer-flags-24.md — **none** (all 103 answers consistent with the CdS).

## Topic 25 pass — Elementi costitutivi; manutenzione; stabilità (2026-07-03)

- Full pass: 30 cards / 284 statements; 80 field edits. Answer flags: none. No figures.
- Answer-consistency catch: 25254 EXI asserted the OPPOSITE of the key ("usare
  catene su tratti privi di neve NON danneggia la sospensione") → rewritten to
  match the FALSO answer (chains on bare roads DO damage the suspension).
- Terminology rulings: servofreno a depressione → **vacuum brake booster** (never
  "vacuum servo brake"); ruote motrici → **drive wheels**; pattinare → **spin**
  (not "skid") for drive wheels; strisciamento → scrub; vento laterale →
  **crosswind**; convergenza → **toe-in (convergence)**; razze del volante →
  **spokes** (EXI had "raggi"); pignone/corona → **front/rear sprocket** (never
  "crown"); marmitta deteriorata → deteriorated **muffler**; inquinamento
  acustico → noise pollution; freno di stazionamento "bloccare" → **hold** the
  vehicle (not "block"/"lock"); marcia inserita → gear **selected/engaged**;
  tenuta di strada → road holding (EXIs had "aderenza stradale").
- EN sweeps: towards→toward; authorised→authorized; penalised→penalized;
  mobile phone→cell phone (25283/25286).
- EXI garbles fixed: "servofrenantismo" (25311); "sottogoflatura" (25300/25304);
  "premere il pedale fermamente" (25267); "un due-ruote" (25419); "corona
  motore" for pignone (25434); "Finestre chiare" for vetri (25291); "freno di
  parcheggio" (25308); "sotto i raggi" (25399); "e evitare"→ed (25275);
  English glosses inside EXIs removed (25346 "(stiffen)", 25384 "(or)",
  25413/25415); carico "elevato"/"leggero" mistranslating posto in alto/in
  basso (25208/25213).
- Review upgraded: added the untested-in-review areas — vehicle fire (key off,
  sand/earth/wet blanket, never touch the tank, inertial switch), visibility
  (wipers, washer fluid, cracked windshield replaced, AC as winter defroster),
  cabin habits (nothing under the seat, child locks, navigator before moving,
  hands-free only), tire extras (rotation, age replacement, nitrogen, space-
  saver limits, chains on drive wheels / bare-road damage), brake extras (test
  after washing, electric/pedal parking brakes, workshop-only pads, never
  reverse in an emergency), steering grip position and height adjustment, and
  kill-switch/chain details. Added summary point 7 (EN+IT).

### Answer flags
docs/answer-flags-20.md — **none** (all 284 answers consistent with the CdS).

## Ruling change — accelerare in stationary contexts (2026-07-03)

- Supersedes the 2026-06-07 approach (literal "accelerate" + explanatory review
  note). New ruling: where the vehicle is stationary, EN translations render
  *accelerare* as **"press the accelerator"** so the statement no longer reads as
  a physical contradiction. Applied to 25081, 25083 (EN+EXP), 25091, 25106,
  25129, 25130. In-motion uses keep "accelerate".
- The "A note on the wording 'accelerate'" section was removed from review 24
  (EN+IT); summary point 1 rewritten to keep the substantive rule (revving a
  cold/stationary engine wastes fuel, pollutes, never helps) without the
  linguistic essay.

## Consistency audit — accelerare + bank-wide EN sweeps (2026-07-03)

- Audited all 60 statements containing *acceler*: the six stationary-engine items
  correctly say "press the accelerator"; the three literal pedal items (25140-42)
  already did; all "corsia di accelerazione" items uniformly say "acceleration
  lane"; in-motion uses keep "accelerate".
- Fixes from the audit: partenza/alla partenza mistranslated as "start-ups"/
  "when starting" (engine-start ambiguity) → "when moving off" (25100, 24735
  EN+EXP; also wheels "slip"→spin there).
- Bank-wide sweeps (77 replacements, all topics): presignals→announces
  ("preannuncia" calque, 17×); towards→toward (23×); authorised→authorized
  (35×); forwards→forward; backwards→backward.

## Reviewer-flag batch — Segnali di obbligo, 2026-07-02 flags (processed 2026-07-03)

- 15 flags from v20260701d/e; 13 were already resolved by the Topic 4 completion
  pass and bank-wide sweeps (regulatory sign + terminology EXPs on the
  prescrizione cards, preavviso explanation on 20035, one-way traffic on 20056,
  what-the-sign-requires EXPs on 20091/20236, "piazza" retained on 20283,
  travel/traveling on the circolare items). The chains-vs-winter-tires teaching
  requested for 20337 was already in review 02, and the circolare vocabulary
  popup already reads "to flow / to circulate (= to travel, drive)".
- New fixes: 5 leftover "mandatory sign" renderings of *segnale di prescrizione*
  → "regulatory sign" (20094, 20120, 20164, 20186, 20207); 22229 "end of a
  regulation" → "end of a restriction" to match the six other *fine
  prescrizione* items.
- Ruling recorded: *segnale di prescrizione* → **regulatory sign** (family
  name); *fine (di una) prescrizione* → **end of a restriction**.
- Circulate audit: all remaining "circulat-" uses are roundabout/piazza traffic
  (the agreed exception) or non-traffic senses (coolant, oil, blood, air
  recirculation) — compliant.

## Reviewer-flag batch — Segnaletica orizzontale, 2026-07-04 flags (13 flags)

- IMAGE flags (20736, 20739, 20790, 20791, 20816, 20828): the image files are
  already trimmed (uniform 6px margin, none are 1:1-padded) — the white space
  the reviewer saw is the card background around figures rendered at tiny
  natural size (e.g. 4224 is 185x112, 4218 is 199x43). Fix is in rendering:
  app.js now upscales roadway diagrams to at most 2x natural size (capped
  400px wide / 240px tall) via a new img-wide class — applied to wide figures
  (w/h >= 1.3, 129 images bank-wide) and to ALL figures of the
  Segnaletica-orizzontale topic (its near-square figures, like the 4213
  guide-lines diagram, are diagrams too). Click-to-zoom remains for detail.
- Ruling: chiodi per segnaletica → **raised pavement markers (road studs)**;
  doctrine added to 20718 EXP/EXI (studs may only supplement painted lines,
  never replace them).
- 20737 EN+EXP+EXI rewritten to explain the geometry: guide lines mark the
  'early' left turn cutting in front of the intersection center (center stays
  on your RIGHT); the default turn goes around the center (on your left).
- Frecce direzionali card 4214 polish per reviewer: "of the combined
  straight-right type" (20747); completate → **supplemented** by wording
  painted on the road surface (20748 EN+EXP); dropped "in color" wordiness and
  "a paid parking" (20753, 20754).
- Review 07: added that yellow-black no-parking stripes are painted on the
  **vertical face of the curb** (EN+IT) — requested via 20781.

### Follow-up (same flag batch): review figures too
The reviewer's screenshot showed the letterboxing in the TOPIC REVIEW figures,
a separate renderer from the study card: .review-fig-img draws every figure in
a fixed square white box (100x100 / 150x130, object-fit contain), so wide
strips (curb 199x43, zigzag 183x57) sat as thin lines between white bands.
app.js now tags wide review figures (w/h >= 1.3) with .review-fig-wide on
load, and CSS gives those an adaptive box: width min(100%, 320px), height
auto. Square sign figures keep the uniform grid boxes.

## Archive-flag verification — all 8 reviewer batches re-checked (2026-07-04)

- Re-verified every flag from the archive (2026-06-12 through 2026-07-02, 50
  flagged statements across Definizioni, Pericolo, Divieto, Obbligo,
  Precedenza). All statement-level translation/explanation requests confirmed
  addressed in the current bank, including the previously unseen batches of
  07-02 11:41 (obbligo: 20342/20343/20347/20363) and 07-02 18:31 (precedenza:
  20474/20506/20578/20581/20680/20702 — US-context notes present in EXPs and
  review 05).
- Remaining gaps found and fixed now:
  - Review 02 (obbligo): pedestrian PATH vs pedestrian CROSSING contrast
    (20343); mopeds are motor vehicles and may NOT use the bike path (20363);
    regulatory signs apply day and night (20342). EN+IT.
  - Review 04 (divieto): named the end-of-all-restrictions sign "via libera
    (all clear)" so the quiz's term is recognizable (19852). EN+IT.
  - 19932 image legibility (holiday-cross panel, 104x129 natural): the study
    card now upscales tall sign-over-panel composites to at most 2x natural
    height within the 210px img-tall cap (app.js).

## Reviewer-flag batch — Segnaletica orizzontale, 2026-07-04 21:09 (5 flags)

- Transverse-line doctrine clarified everywhere (20964/20966 EXP/EXI + review
  07): the line marks WHERE to stop, the STOP sign / red light / officer decide
  WHEN; an uncontrolled intersection has NO stop line; a YIELD junction gets
  the BROKEN line (or shark teeth), crossable without stopping when clear.
- 20884 EXP/EXI: left-turn preparation on two-way roads — move up to the
  center line WITHOUT crossing it, signal early, cross the opposing lane only
  at the moment of the turn (answers the "isn't this a trick?" doubt).
- 20846 EXP/EXI + review 07: named and explained the speed-reduction bars
  (strisce trasversali di rallentamento — progressively wider, closer bars);
  figure 4226 added to the review.
- Ruling: distributore di carburante → **gas station** (20850 EN/EXP).

## Reviewer-flag batch — Semaforiche + Indicazione, 2026-07-07 17:02 (20 flags)

- Semaforiche: "veicoli che provengono di fronte" → **oncoming vehicles**
  (20980/20988); 21042 EN denaturalized-literal rewrite; 20991 EXP/EXI + review
  15 (EN+IT): going STRAIGHT on green you owe pedestrians no yield (their
  parallel signal is red; let those already crossing finish) — the yield duty
  belongs to TURNS; US-contrast note included for the American learner.
- Indicazione EXP/EXI rewrites: 21305 progressive-marker logic (54 = km from
  autostrada origin; green panel = km to next exit); 21482 blue = ordinary
  out-of-town color scheme, not a road classification; 21509 chains on the
  DRIVE wheels, never all four; 21518 panel doctrine (round blue disc =
  condition of transit, white rectangle on the 'closed' board = recommendation
  for the reachable stretch); 21531 ITALIA border board (50/90/110/130); 21581
  unregulated = no lights/officer; 21624 why advisory speeds exist; 21753 US
  'TRUCK ROUTE' analogy.
- Rulings: corsie di canalizzazione → **channelizing lanes** (lanes that sort
  traffic by destination); tangenziale → **ring road** (glossed in review 01);
  "the places that follow" for località successive (21474).
- Review 01 additions (EN+IT): tangenziale gloss, channelizing-lanes gloss on
  the preselection bullet, "unregulated" on the crosswalk-sign bullet.
- Image flags 21381/21401/21491/21489: cards 4282/4284/4292 already carry SVG
  replacements (done in the parallel image-quality session) — no further action.

## Review layout restructure — figures interleaved with their explanations (2026-07-07)

- Per the reviewer's pedagogical request (flag 21666): grouped figure rows that
  followed whole bullet lists have been split, and each figure now sits
  immediately after the bullet or paragraph that explains it, in both language
  halves of all reviews. Look-alike sets and variant pairs discussed in a
  single bullet stay together on one line; section-level galleries (e.g. the
  pannelli "other dangers" gallery, the officer-poses set, and rows referenced
  positionally as "first/second/…") were deliberately left grouped.
- 12 files restructured (01–08, 13, 15, 16 touched; 14 and 21 examined and
  correctly left as-is). Image counts verified unchanged per file, and EN/IT
  figure sequences verified identical.

## Reviewer-flag batch — Complementari + Pannelli + Limiti, 2026-07-10 (15 flags)

- Ruling: abbagliare/abbagliato → **blind / blinded by glare** (never "dazzle",
  a Britishism). Bank-wide sweep, 27 replacements, plus reviews 11 and 14.
  Forms: "being dazzled"→being blinded by the glare; "dazzled by the sun"→
  blinded by sun glare; "dazzling others"→blinding others; "anti-dazzle"→
  anti-glare; noun "dazzle"→glare.
- Ruling on "segnali complementari": KEPT as **complementary signs** — the
  reviewer suggested "supplementary", but that name already belongs to the
  pannelli integrativi (supplementary panels), and merging the two would
  conflate two distinct exam families. Instead the term is now explained
  wherever it appears (21922/21932/21941 EXP/EXI + review 06): complementary =
  they COMPLETE the main signs/markings by physically marking the road's
  course; explicitly contrasted with supplementary panels.
- Delineator spacing doctrine added (21936 + review 06): close regular
  intervals, tighter in curves — no "at least 100 m" rule.
- Italian ordinal ° explained (21829 + review 06): 1° = 1st, not degrees.
- transito on access panels → **passage** (22037/22039/22040) — bare "traffic"
  read as vehicles-only.
- 22060: no-stopping X + vehicle panel — EXP now states fermata ban includes
  sosta. 22075/22084: arrow panels give EXTENT not slope; horizontal double
  arrow = continuation on parallel-mounted signs. 22108: brush panel =
  markings being repainted; OTHER-DANGERS pattern explained. 22124 + review
  08: shunting tracks glossed. 22238: "lanes that make up the road".

## Complementary vs supplementary — pedagogical pass (2026-07-10)

- Full audit: "complementare" appears in exactly 6 bank statements (all in the
  Segnali complementari topic); no cross-contamination anywhere ("supplementary
  sign" 0 hits; no stray "complementary" outside those statements or review 06).
- The three remaining bare explanations (21943 tunnel delineator, 21951 snow
  pole, 21982 curve chevron) rewritten EXP+EXI: family doctrine + what each
  specific device does.
- Review 06: contrast promoted from a buried clause to a dedicated call-out
  right after the intro — complementary devices = hardware tracing the road's
  course (US: delineators, object markers, chevrons); supplementary panels =
  rider plaques under a sign; "a delineator never hangs under a sign, and a
  panel never stands alone." EN+IT.
- Review 08: mirror note added to its intro paragraph (EN+IT).
- vocabulary.json: added "complementare" tooltip entry alongside the existing
  "integrativo" one.

### Follow-up: TOPIC_EN titles (app.js) — the conflation lived in the topic list
The English topic-list titles translated "Segnali complementari" as
"Supplementary signs" — the exact complementary/supplementary conflation, shown
to the learner before any review. Fixed: → "Complementary devices; temporary &
work-zone signs" (also retiring British "roadworks"). "Pannelli integrativi dei
segnali" → "Supplementary panels (under signs)". Same audit fixed two more
titles: "Rules on vehicle circulation" → "Rules of the road", and "highway" →
"autostrada" in the Ingombro title.

### Reevaluation after the title fix (2026-07-10)
The complementary/supplementary confusion traced back to the mistranslated
TOPIC_EN titles, not to the reviews. With the titles fixed, the compensating
cross-references were removed again: review 06's call-out now defines the
family on its own terms with no mention of panels; review 08's mirror note is
gone; the two "not to be confused" clauses were dropped from 21922/21943
EXP+EXI. Principle recorded: definitions live in the reviews; disambiguation
between look-alike terms lives in ONE place, the vocabulary tooltip
("complementare" entry, phrased neutrally). Explanations stay as simple as the
corrected terminology allows.

### Sweep-defect fix: "blindd" garbles (2026-07-10)
The dazzle sweep ordered "dazzle→blind" before "dazzled→blinded", so two
occurrences of "dazzled" missed by the specific patterns (one wrapped in bold
markers in review 11, one in "to be dazzled", 22757) became "blindd". Both
fixed; full re-audit of bank + all reviews clean. Process note for future
sweeps: order replacement pairs longest-first (or use word-boundary regexes),
and scan for the RESULT side of replacements, not just leftovers of the source
term — bold markers (**word**) can defeat phrase-level patterns.

## Reviewer-flag batch — Speed limits pedagogy, 2026-07-13 (5 flags)

- Review 11 gains three teaching aids per the reviewer's request:
  (1) "The US bridge — match the road types before the numbers": strada
  extraurbana principale = the US Interstate analog (divided highway, 110 =
  68 mph); the autostrada has NO US equivalent (130 = 81 mph, 150 = 93 mph);
  secondaria = a rural two-lane (90 ≈ 56 mph); town 50 = 31 mph. EN only —
  the IT half gets the ladder but not the US mapping (not useful to Italian
  readers).
  (2) "How to remember the numbers": the odd-tens ladder 130-110-90-50 with
  the missing 70 rung; rain lowers the top two rungs one step; everything
  else as a short exceptions list (70/150 where signed, 100/90 novice, 80/70
  towing, 45/80/40 special vehicles). EN+IT.
  (3) The golden-rule conditions now include the driver's own psychophysical
  state (22393). EN+IT.
- 22337 EXP/EXI: why "70 urban" needs both the signs and the road
  characteristics. 22336 EXP/EXI: the mysterious "special sign" for 150 is
  the ordinary round limit sign reading 150; three lanes + emergency lane;
  rarely used in practice. 22405/22409 EXP: ladder pointer and the
  Interstate association (EXP only; EXI kept plain).

### Follow-up (same batch): warning + per-question recap
Review 11 now opens with a candid warning that this is the hardest topic to
memorize, pointing to the ladder and exceptions list. And all 93 numeric-limit
statements in the topic now end their EXP and EXI with a bracketed one-line
recap of the full table (defaults, rain steps, signed exceptions, novice,
towing, mopeds/farm machines) — spaced repetition through the explanations
themselves.

## Reviewer-flag batch — Limiti + Distanza + Norme, 2026-07-13 18:22 (14 flags)

- Rulings: "veicolo che precede" → **the vehicle ahead**; "veicolo che segue" →
  **the vehicle behind** (never "preceding/following vehicle" — ambiguous to
  American readers; "safe following distance" as a term stays). Bank-wide
  sweep, 20 replacements. "impegnare la carreggiata" → **occupy the roadway**
  (22711).
- Speed-limit recap (all 93 statements) now includes non-light quadricycles
  (80 outside town) — the reviewer caught the omission (22341).
- Review 11: speed-marker discs properly scoped (vehicles bound by lower
  limits — some buses, trucks OVER 3.5 t; never motorcycles, never ≤3.5 t
  trucks/motorhomes, and no sticker exists for new drivers) + EU note (limits
  are national; the ITALIA border board exists for that). EN+IT, mirrored in
  22438/22474 EXP/EXI.
- Review 09 + physics explanations: divide-by-3.6 rule was already there with
  the table; added the "every 10 km/h ≈ 2.8 m/s" trick (review + 22594/22598),
  reaction-vs-braking-distance decomposition (22602/22655), and the 30-km/h
  arithmetic (22583).
- NEW: interactive **stopping-distance widget** embedded in review 09 (EN+IT):
  speed and reaction-time sliders + wet-road toggle, showing reaction (yellow)
  and braking (red) distance bars, total in meters and car lengths. Plumbing:
  `![caption](widget:name:lang)` marker in review md → renderer emits a
  .review-widget container → initReviewWidgets() builds it on open;
  validate_data.py skips widget: pseudo-images. (Reviewer 22583; scoped by
  the maintainer to the plot only; game deferred.)
- Review 13: procession examples added (funeral cortege, religious procession,
  parade/demonstration, military column), EN+IT + 22745 EXP/EXI. Load-height
  rule (no 10% tolerance, 4 m cap) verified already present in review 13.

## Vocabulary tooltip expansion (2026-07-13)

- Coverage analysis over all 7,147 statements: tokenized italian_text, removed
  stopwords and stems already covered (the app wildcards the final vowel, so
  one base form covers plurals/gender; elided forms like l'incrocio match the
  bare noun). The 400 most frequent uncovered stems were reviewed by hand.
- Added 170 entries (414 → 584): core frame words that had no tooltip
  (segnale, velocità, semaforo, incrocio, pericolo, distanza, curva...),
  domain nouns, high-frequency verb forms (preavvisa, si trova/si trovano,
  attraversa/attraversano, passano, impone, prescrive...), and idiom-bearing
  phrases chosen to avoid wildcard collisions (file parallele — not bare
  "file", which would swallow "filo"; passa per — not bare "passa", which
  would hit "passo"; rispetto a; in base a; in grado di; all'occorrenza).
  Pure cognates (possibile, totale, temperatura...) deliberately skipped to
  keep highlight noise down. Notes carry the American bridges (giorni
  festivi/†, superare's double meaning, efficiente = in good working order,
  sosta vs fermata, posto di blocco...).

### Vocabulary deep expansion (2026-07-13, second pass)
Reviewer found remaining gaps (sopraggiungono, mezzeria, contromano...). The
first pass had covered only a hand-picked top slice; this pass covers ALL
stems appearing 4+ times across the bank: 1,541 entries total (584 → 1,541).
Includes trap adverbs (solo, soltanto, esclusivamente, unicamente,
solamente — flagged as trap words in their notes), verb forms, cognates (now
included for completeness), and domain terms. Matcher gap found and patched:
the final-vowel wildcard cannot reach -io/-cia plurals (rimorchio→rimorchi,
freccia→frecce), so those plurals carry explicit entries. Performance: with
1,500+ entries the highlighter now caches sorted entries and compiled regexes
and prefilters by substring, so most entries cost one indexOf per render.

## House principle codified — audience asymmetry (2026-07-13)

EN content assumes an experienced US driver: elaborate wherever Italian rules
differ from US rules. IT content assumes a novice, no US comparisons ever.
Actions taken: EXIs audited — zero US references (clean); the "Il ponte con
gli USA" sections that had been mirrored into the IT halves of reviews 01, 02,
03, 05, 06, 07, 08, 09, 13, 15 were rewritten in place keeping the Italian
substance and dropping the comparison (agents' per-file reports in the
commits); one IT alt text in review 03 reworded. NEW "For US drivers" notes
added to the EN halves that had none where rules genuinely differ: 10 (no
passing on the right; overtaking = oncoming lane), 12 (right-edge parking, no
colored curbs), 14 (daytime low beams outside town), 17 (0.5 g/l ≈ 0.05% BAC,
zero for novices), 19 (helmet for all riders everywhere; belts all seats;
child restraints by height), 21 (triangle + vest; emergency lane is not a
shoulder), 22 (points count DOWN from 20; medical check at renewal). Principle
recorded in AI-CONTENT-REVIEW-PROMPT.md for all future passes.

## Reviewer-flag batch — Norme circolazione, 2026-07-19 (17 flags)

- Reviewer's meta-point acknowledged and codified: explanations must state WHY
  an answer is true/false, not only flag the trap word. All 17 explanations
  rewritten to that standard (EN+IT).
- Left-turn geometry reconciled against the answer key (22805/22850/22854/
  22858): the DEFAULT left turn — two-way roads included — keeps the
  intersection's center ON YOUR RIGHT, turning in front of it; going around
  the center belongs to signed roundabouts/central islands. Review 13's
  diagram caption had it backwards ("pass to the right of the center point")
  — fixed EN+IT; 22809 EXP rewritten accordingly.
- Roundabout doctrine expanded (22886/22945/22946 + review 13, EN+IT): the
  ROTATORIA sign alone gives the ring NO priority; unsigned = right-hand rule,
  which at a ring means CIRCULATING traffic yields to ENTERING traffic; the
  YIELD sign at the entries (near-universal in practice) is what gives the
  ring priority. This resolves the reviewer's "traffic never comes from the
  right at a roundabout" confusion.
- 22885: figure was misidentified in the EXP (called a priority-road diamond);
  it is the YIELD-TO-ONCOMING sign (white disc, black+red arrows) at
  alternating narrow sections — EXP/EXI rewritten.
- marciare vs sorpassare clarified (22831): crossing a broken line is
  momentary (overtake/lane change); 'marciare' = cruising, never on/beyond
  the line.
- New review-13 call-out (EN+IT): the "required vs sensible" trap — when a
  statement turns good practice into a legal duty, it is usually FALSE
  (reviewer 23015). Police-display section expanded (order binds like a
  personal command; ALT POLIZIA addresses one vehicle). Points note: conduct
  violations here typically cost 2 points (23000). Translation fixes:
  continuous center line (22860), go-through-ahead phrasing (22896), urban
  indicator (22907), two-way steep-road meeting (22950), mirror+direct-glance
  (23037). 22903 (no fermata at extra-urban intersections) and 23025 (left
  mirror right-third) verified already present in reviews 13/12.

## Generic-advice consolidation (2026-07-19)

The "General exam advice" section in How to use this app is now the single
home for cross-topic advice (absolute trap words; required-vs-sensible;
answer the exact words). Reviews swept accordingly: review 13's
required-vs-sensible call-out removed (fully duplicated by the general
section); the bolted-on generic "usual absolutes" sentences trimmed from
reviews 01, 02, and 07; review 04's absolutes block rewritten to lead with
its topic-specific examples (7 t / tow-away) instead of restating the general
principle. Kept in place as genuinely topic-anchored: 01's numbers-trap, 06's
temporary-overrides/figure-games block, 07's color falsities, 12's
fermata-vs-sosta trap, 15's green-is-no-free-pass block, 25's
enter-first-finish-last wording note, 11's memorization warning. Principle:
reviews teach the topic's own traps; the how-to teaches the exam's.

## Pedagogical writing rules (2026-07-27) — read before writing ANY review or explanation

Established with the maintainer during the Topic 25 rewrite, after many correction
cycles. These are binding for all topic reviews and explanation fields.

1. **Textbook register, not conversational.** No filler or color phrases ("at home",
   "honestly", "of course", "the thing is"). Every word must carry information the
   learner needs; if a word or sentence can be deleted without losing exam-relevant
   content, delete it at writing time, not in a later editing pass.
2. **No authority decoration.** No statute citations (e.g. "art. 145 CdS"), years,
   agency names, or Latin unless the fact itself is tested by the exam.
3. **Rules are complete sentences**, stated plainly, one idea each. No bold fragment
   headlines that restate the sentence that follows them.
4. **No privileged rule.** Present rule sets as flat ordered lists checked in order;
   never frame one rule as "the" rule with the others as exceptions (this framing
   generated repeated contradictions in Topic 25).
5. **Consistent terminology.** Use the project's established language (a vehicle's
   "path", paths that "cross") everywhere; do not introduce synonyms ("corridor",
   "line", "trajectory" in EN) for an already-named concept.
6. **Explanations give the rule reasoning, not just the order.** "False. C passes
   first" is insufficient; say WHY by naming the rule and the crossing that decides it.
7. **Preserve maintainer-provided wording verbatim**, including through later
   restructurings. Edit around it, never re-paraphrase it.
8. **Verify factual/legal claims before writing them** (both Italian and any US
   contrasts), and prefer dropping a contestable claim to hedging it.
9. **Prefer teaching through worked examples** over abstract sections; delete an
   abstract section when a worked example covers the same ground.
10. **Em-dash-free prose** in all review markdown.
11. **No slang or idiom, even American** ("left-lane camper"); use plain descriptive
    language ("a driver who lingers in the left lane").

---

### Addendum (Topic 21, user flags batch @20260729b, 2026-08-11)

| Italian | American English | Notes |
|---|---|---|
| ente proprietario della strada | road authority | NOT "road('s) owner" — swept bank-wide |
| svincolo | interchange | NOT "slip road" (BrE); *raccordo/rampa* → ramp |
| bretelle retroriflettenti | (high-visibility) shoulder straps | NOT "suspenders" (AmE = trouser suspenders) — swept bank-wide |
| fascia di ingombro | swept path | trailer/combination cornering |
| particolarmente indicata | particularly well-suited | NOT "particularly indicated" (calque) |
| cunei di arresto | wheel chocks | "chocks" alone is thin for lay readers |
| rimorchio T.A.T.S. | T.A.T.S. trailer — spell out *Trasporto Attrezzature Turistiche e Sportive* + gloss (boat/glider/sport-gear trailers) on first use | |
| retroriflettente | retroreflective — define the mechanism on first use ("bounces headlight beams straight back at their source") | same pattern as the *a cingoli* rule |
| sosta di emergenza | emergency stop | not "emergency parking" |

New recurring patterns
- **Explanations should teach the mechanism, not restate the verdict**: inertia
  (overrun) brake = the trailer's push applies its own brakes; towing ratio =
  trailer mass ÷ towing-vehicle mass; speed/mass homogeneity = why uniformity is
  safer. A learner who understands doesn't need to memorize.
- **Towed vehicle signaling**: hazard flashers (all four turn signals), NOT mere
  rear lights (#23959) — quiz trap.
- **L1 polarity emphasis** (app-side): bolded words now include
  mandatory/compulsory/optional/advisable/not; positive verdict words
  (permitted/allowed) stay unbolded when prohibited/forbidden appears in the same
  statement (misleading-emphasis flag #23881).

Style decisions
- **Name the number: 112.** Wherever content tells the reader to call for help, say **112** explicitly and gloss it at first mention in each review/app surface as "the European equivalent of the US 911" — phrase it so no reader can mistake 911 for the number to dial in Italy (EN only; Italian text just says 112). Never leave it at "call emergency services."
- **Journey structure for composite ("grab-bag") topics.** When a ministry topic
  lumps several subjects, do NOT mirror the lump. Open with a short "map"
  paragraph naming the parts, then order sections as a narrative the learner can
  hold — typically preparation → normal operation → when something goes wrong →
  recognition → risk awareness. Keep bullets to one idea each (split any bullet
  carrying more than ~3 facts), put physics/mechanism explanations beside their
  facts, group scenario content by scenario (e.g. emergency towing belongs with
  breakdowns, not with trailer ownership), and make the summary mirror the same
  arc. Reference implementation: topic 21 review (autostrada/loads/towing),
  v20260811i.
- **Cross-review references cite the displayed short title verbatim** (the
  `TOPIC_SHORT` values in app.js, e.g. "Licenses, documents & penalties" /
  "Patente, documenti e sanzioni") — never topic numbers (internal only) and
  never paraphrases of the official long name. If the referenced review comes
  later in the dashboard list, say so ("comes later, in the … review") so the
  learner reads it as a parked pointer, not a prerequisite.
- **Figures sit beside the text that explains them** — never a front-loaded image
  row explained later by ordinals ("the first…, the second…"). Topic 21's marker
  panels were restructured to image-then-paragraph; verified topics 03/14
  galleries already sit adjacent to their text.
- **EN translations and explanations end with a period** (decision reversed
  2026-08-11 at the curator's request; swept bank-wide at v20260811x). The
  ministry's own `italian_text` stays untouched and unpunctuated — hard rule,
  and at L2/L3 statements must look exactly as the real exam shows them.


---

### Addendum (Topic 14/21 flags batch @20260812b, 2026-08-12)

| Italian | American English | Notes |
|---|---|---|
| spia | dashboard light (red ones: warning light) | NOT "tell-tale" (unfamiliar to Americans) and NOT "light indicator" — swept bank-wide |
| uso intermittente dei proiettori di profondità | flashing the high beams | NOT "intermittent use of high beam headlights" (opaque calque) |
| segnale mobile di pericolo | portable warning triangle | one term everywhere — NOT "mobile warning signal/device" |
| ruotino (pivottante) di manovra | tongue-jack wheel — gloss the mechanism on first use | "jockey wheel" is BrE |
| assetto (del veicolo) | stance / ride height ("squat the rear") | NOT "attitude" |
| luci di posizione | position lights, never "parking lights" (that is *luci di stazionamento* / *luci di sosta*, a different set); the US comparison lives in topic 14's For US drivers note (2026-09-27) | |
| ovalizzazione (pneumatici) | flat spots | NOT "ovalisation" |
| pretensionatore | pretensioner — gloss on first use ("yanks the belt snug in the first instant of a crash") | |
| necessario (in quiz statements) | explain in EX: "necessary" = required by law | reviewer read it as ambiguous (#24253) |

Patterns
- **Dashboard symbols are taught one image at a time**: color rule first, then each
  symbol image immediately followed by its meaning (Topic 14 rewritten to this
  pattern after a repeat front-loading complaint — the figure-adjacency rule
  applies to symbol galleries too, not just sign panels).


---

### Addendum (flags batch @20260812d, 2026-08-13)

| Italian | American English | Notes |
|---|---|---|
| aquaplaning | hydroplaning | gloss "(Europeans say aquaplaning)" once per review |
| omologazione / omologato | type-approval / type-approved | NOT "homologation" (opaque to Americans); gloss the concept on first use |
| disappannamento / dispositivo di disappannamento | defogger | NOT "demister"; define: warm air clearing inside condensation |
| frenatura di servizio | normal braking (the foot brake) | avoid "service brake/braking" — an American reviewer read it as the emergency brake, i.e. the OPPOSITE; freno di stazionamento = parking brake, glossed "emergency brake" |
| servofreno | brake booster — gloss "(power brakes)" | |
| polizza kasko | 'kasko' (collision-type) coverage | ≈ American collision coverage; optional, unlike RCA |
| targa prova | test plate — gloss (dealer/manufacturer road-test plate) | |
| trauma della gabbia toracica | chest (rib-cage) trauma | "thoracic cage" needs the rib-cage gloss |
| ha compiuto N anni | has turned N | NOT "has completed N years" |
| munito di (documento) | must carry (its document) | NOT "fitted with" for paperwork |
| sterzo "pesante" | steering becomes stiff (hard to turn) | keep "heavy" only with a gloss |
| impennata | wheelie ("perform a wheelie") | NOT "wheelying" |

Patterns
- **Do not bold "advisable"** in the L1 polarity emphasis: it invites false
  suspicion of an advisable-vs-mandatory trick (#24738) and double-bolding
  drowns the real cue (#24746). Bold the flippers: not, prohibited/forbidden,
  permitted/allowed, mandatory/compulsory, optional.
- **License-ladder teaching**: state WHICH cap belongs to WHICH rung (cc→A1,
  kW→A2); the A2 double-power no-detuning rule needs its why (detuned big
  bikes); under-18 A1 = no passengers; B1 = quadricycles only; B's 125 rule is
  Italy-only; no age turns B into a motorcycle license.

- **Automatic-transmission blind spot**: the bank assumes manuals (2 of 7,147
  statements mention automatics). Securing a parked car = parking brake + lowest
  gear + wheels to curb; "Park" (the automatic's P pawl) is never what the
  ministry means — US-driver callout lives in the stopping/parking review. Also:
  "engage a gear", never "insert a gear" (calque).

- **"Circulate" sense guide** (2026-08-13 audit): the calque to remove is
  *circolare* = to drive/operate ("to circulate, a vehicle must…" → "to be
  driven on the road…"). LEGITIMATE and kept: roundabout contexts ("circulating
  traffic", the standard US traffic-engineering term), fluids ("oil circulating
  in the engine"), blood circulation (first aid), and cabin-air recirculation.

12. **Explanation parity (2026-08-17).** The EN and IT explanations of a statement
    must teach the same content — same rule, same reasoning, same trap warning.
    The IT version omits material useful only to American drivers (911/112
    comparisons, "what Americans call…" glosses); everything else carries over.
    A much shorter IT explanation is a defect, not a translation choice.
    Check: length ratio < 0.45 with EN > 90 chars flags a pair for review.

13. **One subject, one place — at its image (2026-08-18, restated 2026-08-19).**
    A sign, marking, or device is explained COMPLETELY where its picture
    appears: what it means, what it requires of you, and the trap the quiz sets
    on it. Never split a subject across sections — no "recognition" section
    with the images and a later "what it requires in practice" list holding the
    rules. The reader studies the picture, forms an understanding, and moves
    on; a rules list further down arrives too late and is read as a separate
    topic. The same applies to a correction after a reviewer flags confusion:
    it goes with the image, not only in a later section or in a question's
    explanation.
    (An earlier version of this rule allowed "one sentence at first contact,
    detail below". That was wrong and produced exactly the split it was meant
    to prevent. There is no acceptable split.)
    Check, mechanical: in every review, any section with three or more rule
    bullets must also contain at least one image, unless it is the intro or the
    summary. A rule bullet naming a sign that is pictured elsewhere is a defect.

14. **A hover gloss translates; it does not teach (2026-08-20).** The tooltip
    vocabulary answers one question: *what does this Italian word or phrase
    mean in English?* It is not a place for driving concepts, exam tactics, or
    background an American reader already has. "banchina cedevole" is
    "soft shoulder", not "soft shoulder (unpaved edge that can give way under a
    wheel)". If a concept needs teaching, it belongs in the question's
    `explanation` or in the topic review, where the learner can be given the
    reasoning properly.
    Entries exist mainly for phrases that are IDIOMATIC or whose meaning is not
    the sum of their words. What a parenthetical MAY carry: a sense
    disambiguator when the English word is ambiguous ("limite" = "limit (e.g.,
    speed limit)"), or which of two senses applies. What it may NOT carry:
    grammar (that is the `gram` field), exam advice, or an explanation of the
    rule behind the term.
    Check: `python3 scripts/check_vocab_glosses.py`.

15. **Frequency alone earns a phrase entry (2026-08-23).** The phrase
    vocabulary is not limited to idioms. Any word combination that recurs
    across the bank (threshold: about eight statements) gets its own entry,
    even when its meaning is the plain sum of its words ("altri veicoli",
    "due corsie", "strade pubbliche", "può essere"): the goal is that the
    learner recognizes the bank's recurring formulas as units instead of
    reassembling them word by word. This supersedes the sentence in rule 14
    that said entries exist "mainly for phrases that are idiomatic"; rule 14's
    actual point, that a GLOSS translates and never teaches, is unchanged.
    Two exclusions: reference tokens are not phrases ("veicolo B", "categoria
    BE"), and an n-gram that glues words across a clause boundary is not a
    phrase ("carreggiata bisogna", "disposta quando il titolare"); cut at the
    boundary and take the true constituent ("sono vietate", "quando il
    titolare"). Mining and pruning: add candidates, then
    `python3 scripts/consolidate_vocab.py` (report, then `--apply`), which
    also migrates users' saved words into the phrases that replace them.

16. **Image first, explanation after (2026-08-24).** In a topic review the
    sign's picture comes BEFORE the prose that explains it: the reader sees
    the sign, then reads what it means, in both languages. This is the
    complement of rule 13 (one subject, one place, at its image): rule 13
    fixes WHERE the explanation lives, rule 16 fixes the ORDER within that
    place. A multi-sign thumbnail row obeys the same rule when the following
    prose discusses exactly those signs. An image line carries images ONLY:
    prose on the same line as an image renders as literal Markdown and also
    puts the text beside the picture instead of after it, so it goes in its
    own paragraph below. Every heading is followed by a blank line
    (CommonMark).
    Check: `python3 scripts/check_review_placement.py` (rules 13, 10, 16).

17. **No forward references (2026-08-30).** A sentence may not lean on a sign,
    term, or rule the reader has not yet met at that point in the review.
    The recurring offender is the intro "watch the traps" note that negates a
    rule ("yellow does not force a stop in every case") before the rule itself
    has been taught: the negation has nothing to attach to. Traps, contrasts,
    and US-comparison warnings live at the LATER of the subjects they connect
    (the false-friend warning about the yellow diamond belongs at the diamond's
    bullet, not in the intro; a note contrasting two families follows the
    second family). What remains legitimate earlier: backward references,
    pure navigation pointers ("covered in its own section below"), general
    concepts that depend on no specific sign, self-contained mentions of
    signs another topic owns, and summaries at the end. When a term must
    appear early (a vehicle class in a list), gloss it on the spot.

18. **The ambiguity bar: try to defeat the flag first (2026-08-30).** A
    statement earns the 🤔 marker (`warn`/`warn_it`) only after an honest
    attempt to PROVE the official answer fails. The adversarial test, in
    order:
    (a) Argue the official answer from the statement's own words, read with
        their ordinary meaning. A trap word (*solo*, *sempre*, a swapped
        number, a sign's official name) that decides the answer makes the
        question a TRAP, not ambiguous: teach the decisive word in the
        explanation and do not mark it.
    (b) Check the bank's own definitions and the sibling statements on the
        same card. The bank often fixes a term's meaning elsewhere; if the
        official reading is derivable from the bank, cite that statement in
        the explanation and do not mark it.
    (c) Only if, after (a) and (b), a competent reader applying ordinary
        meaning could still justify the OPPOSITE answer is the question
        ambiguous. The warn note must then state both readings in one or two
        sentences and say which one the exam uses, so the learner memorizes
        the official reading.
    The list must stay short: every entry is a confession that reasoning
    cannot decide the question, and each one costs the learner a
    memorization. When in doubt, strengthen the explanation instead.
    Worked example: 20697 ("la circolazione si svolge a doppio senso" in a
    strettoia) passes the test, because the road genuinely carries traffic
    in both directions over time, so FALSO is defensible only under the
    'simultaneously' reading the exam intends; no bank definition settles it.

19. **An explanation teaches the WHY; it never merely asserts the conclusion
    (2026-08-31).** When the answer is revealed, "True. Overtaking mopeds is
    still allowed." teaches nothing the reveal did not. The explanation must
    carry the reason drawn from the proofed topic review: the underlying
    rule, the mechanism, the exception list, the distinguishing feature, or
    the trap word that decides the answer. The topic reviews are the
    pedagogical source of truth, so an explanation quotes their teaching in
    miniature (1-3 sentences), in both languages, with equivalent content.
    Restating the statement with "correctly"/"indeed" added, or asserting
    the verdict plus a synonym of the statement, fails this rule. Enforced
    bank-wide on 2026-08-31 (2,848 explanations enriched from the reviews).

20. **List questions must drill the list, every time (2026-09-01).** A card
    whose statements probe membership ("who may still pass", "who is
    banned", "who may be overtaken") is a memorization task, not a
    reasoning task. Each explanation on such a card therefore (a) gives the
    verdict, (b) names the decisive membership rule for the vehicle in that
    statement, and (c) repeats the list in BOTH directions, allowed and
    banned. The repetition is the point: the learner meets the same list
    a dozen times across the card and leaves knowing it. Vary the phrasing
    so the card does not read as one sentence copied twelve times, but never
    drop the list to save words. Applied on 2026-09-01 to the prohibition
    family (no-passing signs and the category bans, 207 statements).

21. **"Consente" means "does not forbid" (2026-09-02).** The bank's "il
    segnale consente X" is VERO whenever the sign's own rule leaves X open,
    and FALSO only when that rule forbids X. Only the sign's own rule counts:
    the no-passing sign "permits" transit, the end-of-minimum-speed sign
    "permits" driving faster, the no-parking sign does not "permit" residents.
    An explanation for a "consente" statement must state which rule the sign
    carries and that it does (or does not) reach X; "the sign is about speed,
    not X" is not an answer. The How-to lists this under general exam advice.

22. **Permits/forbids patterns, from a bank-wide scan (2026-09-02).** 776
    sign statements use consente/vieta/obbliga; VERO rates 47/49/38%, so
    no guessing bias. The false families: (a) the sign's own rule forbids X;
    (b) an INVENTED exception (safety cell, at night, with tires, during
    fairs, tourist/school buses, "after checking" at closed gates); (c) an
    ADDED absolute changing the scope (solo/soltanto/unicamente/tutti/
    qualsiasi); (d) an obligation's alternative, or "without any limit"
    (general rules never suspended), or a softened condition ("as long as
    you stay in your lane"); (e) swapped pairs (fermata/sosta; red light
    permits nothing). WARNING SIGNS are their own family: "consente X" is
    false 29/30; "non è consentito X" is VERO only when the Code's general
    rule forbids X at that hazard AND the statement carries the rule's
    condition (two-way, one lane per direction); the unconditioned ban is
    FALSO (18877 vs 18895). Guidance lives in the How-to (general advice)
    and in reviews 02, 03, 04 ("How the exam phrases it"). Explanations for
    these statements name the family.

23. **Read "consente" as "leaves allowed", never as "grants" (2026-09-02).**
    The root of the recurring "the sign is not about that" confusion: in
    everyday English "the sign permits X" is an act of granting, so a silent
    sign seems not to permit; the bank reads "consente X" as the resulting
    state, "with this sign, X is allowed". The verbs are asymmetric: vieta
    and obbliga are the sign's own acts (a silent sign forbids/orders
    nothing, FALSO), consente is the state (silence leaves X allowed, VERO,
    unless the general rules forbid X). Explanations for "consente"
    statements about an unmentioned behavior should say this in one line.

24. **"Il segnale consente X" → "With this sign, [subject] may X" (2026-09-03).**
    The sign is no longer the grammatical actor in English, which removes the
    "grants" reading (rule 23). 127 translations converted. "pass" stays
    reserved for overtaking (use "proceed" for transito); "pass to the right
    of an obstacle" is fine. Physical "allows" (an exit that allows a U-turn)
    is left alone.

25. **Vocabulary glosses open on CLICK, not on hover (2026-09-04).**
    The reveal and the record are the same act: clicking a dotted-underlined
    term shows its gloss AND logs the look-up, which is how a term reaches
    the learner's vocabulary study list. Revealing on hover taught the word
    and recorded nothing, so the list never reflected what the reader
    actually needed. In older entries above, "hover" means this gloss;
    prefer "look-up" or "gloss" in new prose and in code comments, and
    reserve "hover" for genuine mouse-over behavior (title tooltips on topic
    names, CSS :hover styling).

26. **At most two figures side by side; explain before showing more (2026-09-04).**
    A row of three, four or five signs followed by one bullet explaining them
    all breaks the show-then-explain rhythm: the reader holds several
    pictures in mind before any is explained, and the explanation then
    reads as a list to match back to the row. Show one figure, or a pair
    when the comparison IS the lesson (left/right bend, the two one-sided
    narrows, red/green officer stances), and explain it immediately; then
    the next figure or pair. Pairs render large in the app, so nothing is
    lost. The 40 rows of three or more that existed (topics 01, 02, 03, 04,
    08, 15, 16, both languages) were split on this date, and
    `check_review_placement.py` now fails on any line with three or more
    images (rule 26 check). Amended 2026-09-05: the limit is two images
    **before an explanation**, stacked rows included, since the renderer
    groups consecutive figure rows into one block; the check now counts
    across consecutive image lines (four stacked triples in topic 07 were
    missed by the per-line check and have been split).

27. **A figure block is self-contained: name the subject, never "it" (2026-09-05).**
    A figure and its explanation render as one box, and a learner can land
    on that box directly (the study card's image opens the review at its own
    figure). So the first sentence under a picture must name what the
    picture shows ("The yellow work-zone version of the heavy-vehicle route
    sign ..."), never open with "It", "Contrast it", "Both", "The same" that
    point back to a previous box. Within the box, "the sign above", "(A)",
    "this diagram" are fine because the referent is in the same box.
    When a box compares its figure with one in ANOTHER box, say where that
    one is ("the white advisory panel shown in the previous box", "the
    diamond from the previous section"), so the reader knows where to look
    instead of guessing which sign is meant. Swept again 2026-09-05 across
    all 25 reviews, both languages: 8 more cross-box references located
    ("in the box above", "in the boxes above", "shown further down", "not
    pictured here", "at the top of this review"), and the no-trailer facts
    that sat in the 3.5 t box moved to the no-trailer sign's own box
    (rule 13). Swept 2026-09-05:
    three blocks fixed (topics 01 and 05, both languages).

28. **dosso = crest; superare = get past (cross a line, exceed a limit) (2026-09-05).**
    *Dosso* is the top of a rise in the road that hides what lies beyond:
    translate it **crest**, never "bump" (a bump is a small jolt; the danger
    of a dosso is the hidden far side). Only *dosso artificiale* is a
    **speed bump**. Swept the bank (25 fields on 14 statements) and topics
    03 and 07. *Superare* is a general "get past": with *la striscia* it is
    **cross**, with a limit **exceed**, with a vehicle it can be overtake
    (the bank does use *superare un veicolo*, 19567, 23532). *Sorpassare* /
    *sorpasso* is only overtaking. Translations already said "cross" for
    every line statement (35/35); the vocabulary glosses for the *superare*
    forms now lead with "cross (a line)" and say so in the note, and topic
    07 opens its longitudinal-lines section with the distinction.

29. **The "true fact, wrong condition" trap (2026-09-06).** 169 of the
    3,576 FALSO statements (about one in twenty) are a correct rule followed
    by a comma and a *se / quando / purché / qualora / salvo* clause that
    applies it to the wrong case (20966: the stop line marks where to stop,
    "se non è regolato"). The reader agrees with the first half and answers
    true. Named in the exam-advice list of "How to use this app" (EN and IT);
    explanations of such statements should say "the first half is right,
    the condition ruins it" and give the correct condition (as 20966 does).
    Companion of the absolute-word rule: there the extra word widens the
    claim, here the extra clause misplaces it.

30. **Family rules in the section intro, figure facts under the figure (2026-09-06).**
    Rule 13 pulled everything toward the picture, and family-wide rules
    ended up inside the first figure block of a section (the stop line
    "never stands alone" was written under one stop-line figure). The split
    is: a rule that holds for every member of the family (all transverse
    lines, all arrow figures, all size signs) goes in the section's opening
    paragraph, BEFORE the first figure; what this figure shows, and the
    traps set on it, goes under the figure. A section that opens directly
    with a figure is the tell: check whether its first block carries the
    family's rules. Restructured on this date: topic 07 (transverse lines,
    arrows, guide lines vs islands, painted words), topic 04 (size and
    weight, the no-entry pair), topic 05 (priority road), topic 08
    (validity by vehicle), topic 16 (types of road), EN and IT.

31. **Never cite "the manual" in user-facing text; teach purpose before mechanics (2026-09-06).**
    The SIDA manual is our internal cross-check source. It is meaningless to
    the learner, so a review or explanation never says "the manual's example
    is", "the manual says", or "il manuale". State the fact as our own.
    Same-day lesson from the reversible-lane box: listing what each light
    means is not enough when the learner has never met the device. A block
    about an unfamiliar device leads with the situation it solves (why would
    a lane change direction?), then where the device sits, then how to read
    it, then the trap the bank sets on it. One idea per bullet, each opened
    with a short bold label, so the reader can see the sequence.

32. **Reading-order audit of every review (2026-09-06).** Two misplacements
    found by the user (a pedestrian note under the public-transport figure;
    the green-wave sign explained before the green-wave section began)
    prompted a full read of all 25 reviews, both halves, for blocks sitting
    in the wrong section, bullets under the wrong figure, and concepts used
    before introduction. Fixed: 04 (P+arrow advance sign was under
    end-of-restriction; three no-parking bullets sat under the P figures),
    06 (chevrons used before introduced: glossed), 07 (speed-bar figure sat
    above the yield-line bullet), 12 (bullet stranded after a blockquote),
    14 (brake/reversing lights listed under retroreflectors; amber dashboard
    color in the hazard-light block), 16 (town-entry figure between two
    extra-urban bullets), 22 (paragraph splitting the AM-A list), 24 and 25
    (summary items with no body source: now body points). The mechanical
    checks cannot see these; a reading pass is the tool, and the tell is a
    figure or bullet whose subject is named by the NEXT heading.

33. **Every explanation is checked against its own figure (2026-09-07).** A
    reviewer found an explanation describing a different sign from the one on
    the card. All 516 image cards were then read picture in hand, statement by
    statement: 85 explanations described a different sign or scene. Two
    families. (a) Sign identity: the END OF NO OVERTAKING disc explained as a
    supplementary panel (22103), the priority-to-the-right triangle explained
    as a yield-to-oncoming disc (22885), the other-dangers triangle called the
    slippery-road sign (19476), horizontal start/end arrows called up and down
    arrows (5102, 5111, 5113), a double continuous center line described as
    broken (18316). (b) Precedence diagrams, where the reasoning quietly
    swapped scenes: the right-hand rule invoked where give-way signs or tram
    rails decide, "its right is free" where a vehicle is plainly drawn in the
    right-hand arm, and "their paths cross" for vehicles travelling parallel
    or in opposite lanes of one road. The second family was re-verified by an
    independent reader before any edit. Lesson: an explanation must name what
    the figure shows before reasoning from it, and a variant card is written
    from ITS own picture, never from the base card's.

34. **The Review page and reference.json (2026-09-09).** The learner asked for
    one place holding the quantities the exam tests, since numbers are what
    memory drops first. `public_html/reference.json` now carries 139 numbers
    (grouped by what they measure: speeds, distances, masses, sizes, power,
    times, ages, alcohol, points) and 106 membership lists, each with what
    belongs and what is commonly assumed to belong but does not. Two rules
    govern it. First, TRACEABILITY: every figure must appear either in a
    statement the row cites or in that topic's proofed review, and
    `validate_data.py` fails otherwise, so the page cannot drift from the bank.
    Second, NO FIGURE READINGS: a number printed on a pictured sign (the 80 on
    a speed disc, the 320 m on an advance panel) is not a fact to memorize and
    was dropped; what stays is the rule behind it. Curation caught three
    inversions worth remembering: a value tested only inside a FALSO statement
    is usually a trap, not a fact (work machines are 40 km/h on tires and 15 on
    tracks, not the 50 and 45 the false statements name), and the same applies
    to the 5 m at fuel pumps, which belongs to intersections. The Vocabulary
    screen became the third section of this page, and the per-topic notes are
    now called Concepts everywhere, so "review" names one thing.

35. **A false statement still tests the quantity (2026-09-09).** Pruning the
    Review page to "tested content only" first removed every number whose true
    figure the bank never prints, which was wrong: when the exam asserts "work
    machines may travel above 50 km/h" and marks it FALSO, the learner has to
    know the real ceiling (40 km/h on tires, 15 on tracks) to answer it. Those
    rows are back, carrying the TRUE value from the proofed review, flagged
    `"trap": true`, and shown with a tag saying the exam prints a different
    figure. `validate_data.py` allows such a row only when a cited statement
    measures the same kind of quantity AND the true figure is taught in the
    topic review. The rule to remember: the test for inclusion is whether the
    exam probes the quantity, not whether it prints the right answer.

36. **The membership lists were removed (2026-09-09).** The Review page shipped
    with 105 "what belongs and what does not" sets alongside the numbers. In
    use they did not earn their place: the same material is taught in context
    in the Concepts notes, where the picture and the rule sit together, and a
    bare list of members is hard to learn from and long to scroll. Review now
    holds Numbers, Weak spots and Vocabulary. The lists and their curation are
    in git history (commit cc57de5) if they are ever wanted back; reference.json
    shrank from 166 KB to 43 KB, which every offline install downloads.

37. **State the rule, keep the table (2026-09-09).** The five safe-following
    distances the bank tests (9, 14, 28, 36, 42 m at 30, 50, 100, 130, 150 km/h)
    all follow one rule: the metres covered in one second, speed in km/h divided
    by 3.6. First attempt replaced the five rows with the rule alone; the user
    corrected it, and rightly: the exam prints those pairs, so the learner wants
    to recognize them instantly, while the rule is what makes them memorable.
    The form that works is BOTH, with the rule as one short line above the
    table (the group note) and the values as rows. Generalize: a formula earns
    a line, never the deletion of the figures the exam actually asks about.
    The group-note mechanism and the `"rule": true` validator branch remain
    available for a case where no figures are printed at all.

38. **Two marks on a number, and what each may claim (2026-09-09).** Learners
    asked which figures the exam ever fakes. Two flags now answer that, and
    both are re-derived by validate_data.py on every run so a bank revision
    cannot leave a stale claim on screen. `"noWrong"` (tag: "figure never
    faked") means no statement gives a DIFFERENT figure for that quantity: 29
    rows, confirmed one by one by readers searching the whole bank, not by the
    keyword heuristic that proposed them. It does NOT mean the statement is
    true: the traps then flip the rule around the same number ("a più di 5
    metri" for 23686) or attach it to the wrong vehicle (23951), and the
    tooltip says so. `"alwaysTrue"` (tag: "only ever asked as true") is the
    strong claim: within the row's own topic every statement carrying that
    figure WITH ITS UNIT is VERO, so meeting the number means the answer is
    true. Only 5 rows qualify. The candidate that had to be dropped is
    instructive: 50 km/h in dense fog is a true statement, but "50 km/h"
    appears in FALSO statements of the same topic on other subjects, so the
    figure alone decides nothing. Never scope such a claim by subject when the
    learner will apply it by figure.

39. **Idioms get a word-for-word rendering, transparent phrases do not
    (2026-09-11).** A reader flagged 24270: he could read "high beams" off the
    gloss for *proiettori di profondità* but had no idea what the Italian
    words themselves said, so the phrase taught him nothing about Italian.
    A gloss on a multi-word term now ends with "(literally: ...)" whenever
    the word-for-word reading differs from the natural translation:
    *passaggio a livello* "railroad crossing (literally: passage at level)",
    *sinistro stradale* "road accident (literally: road mishap; sinistro also
    means left)", *in folle*, *carta di circolazione*, *luci abbaglianti*.
    The condition is real difference, not merely being a phrase. Where the two
    languages run parallel (*veicoli a motore*, *corsia di destra*, *limite
    massimo di velocità*, and most of the *il segnale raffigurato indica*
    boilerplate) the literal line just repeats the gloss, and it is clutter;
    215 of the 2,767 multi-word entries qualified, not all of them. When the
    entry is a longer phrase that merely CONTAINS the idiom, the literal names
    the idiom it is explaining ("literally: dare la precedenza = to give
    precedence"), so the reader knows which words are being unpacked. The map
    of idiom to literal lives in `scripts/add_literal_glosses.py`, which is
    idempotent: it skips any gloss that already says "literally", so adding a
    new idiom and re-running only touches the new matches.
    `check_vocab_glosses.py` exempts the trailing "(literally: ...)" from the
    80-character limit and measures the natural translation on its own, since
    that limit exists to catch glosses that have turned into driving lessons,
    and a word-for-word rendering is still translation.

### Ages checked against the manual and the Code (2026-09-11)
The Review page's Ages section was checked line by line against SIDA §20.1
and art. 115 and 170 of the Code. Seven of eight rows were right. The eighth,
"18 for an A1 rider to carry a passenger", was our own invention: the Code
puts the rider's minimum at **16** for mopeds (art. 170 c. 2) and sets no
extra age for motorcycles, and the manual says the same in one sentence,
"su ciclomotori e motocicli è possibile trasportare un passeggero solo se il
conducente ha almeno 16 anni ... sempre vietato il trasporto di bambini che
hanno meno di cinque anni". The 18 came from misreading 24498, whose trap is
the passenger's adulthood, not the rider's age. Topic 21 had it right all
along (23917, 23921), so the app contradicted itself across two topics.
Lesson: when two topics state one rule, diff them. Ages the manual teaches
but the bank never tests (65 for the accompanying driver, 17 for guida
accompagnata, 21 for the zero-alcohol rule, 4 for the anti-abandonment
device) stay off the page by its own rule.

### The other 89 numbers checked against the manual (2026-09-11)
Same sweep as the Ages, over speed, distance, mass, size, power, time,
alcohol and points, against SIDA §12 (limits, stopping distances), §17
(autostrada), §20 (licenses, points), §21 and §24 (loads, trailers) and the
articles of the Code behind them. Every figure matched. Two rows were wrong
in framing rather than in number. "9 points, what a recovery course
restores for the higher categories", marked never faked, was the exam's
FAKE figure for an A or B holder (24651): the manual says 6, and 9 is what
C and D get, so the row now shows 6 as a trap row. And 24598 tests a rule
the page and the review both lacked: after one violation of at least 5
points, two more within 12 months, three in all, send the license back to
the exam; the statement says two. Row and review bullet added. A figure the
manual teaches that the bank never prints, the triangle at 100 m on the
autostrada, was already a parenthesis in the topic 21 review and stays off
the page. Cross-checking is cheap now: dump the rows, grep the manual text
for each figure, read the paragraph.

### Manual-only quantities stay off the Numbers page (2026-09-11)
Decided after listing them: the manual teaches about fifteen figures the
bank never prints (alcohol tiers and the zero limit for new drivers, the
triangle at 100 m on the autostrada, 120 cm3 / 6 kW motorcycles on the
autostrada, 425 kg minicars, the 7-hour course, 15-month rear-facing seats,
the 65-year accompanying driver, the good-conduct bonus, the seatbelt and
pedestrian point losses, bus speeds, foreign-license withdrawal days). They
are NOT added, flagged or hidden behind a toggle. The page's contract is
"what the exam asks", the exam is drawn from this bank, and a flag on every
row would make each line a two-step read for everyone to serve a few. What
matters for driving rather than for the exam already sits in Concepts with
its context (alcohol tiers in topic 17, the triangle note in topic 21). The
listing did expose one genuine gap: 24550 probes the new-driver power cap
with the OLD figures (55 kW/t, 70 kW), so the true 75 kW/t and 105 kW are
tested in the rule-35 sense and are now trap rows.

### The Review page is now the Reference page (2026-09-11)
Renamed at the maintainer's request: the learner goes to it the way one
goes to a reference book, to look a number or a word up, not to "review" in
the sense of going over material again, and "Review" also collided with the
per-topic Concepts (once called the topic review) and with the exam-answer
review. Italian: **Prontuario**, the ordinary word for a handy compendium of
figures and rules, rather than a stiff calque. Element ids (`nav-vocab`,
`screen-vocab`) and the i18n keys (`review.*`, `vocab.*`) are unchanged.
Earlier glossary entries that say "Review page" mean this page.

### The weak-spot release rule, and the drill runs in Italiano (2026-09-11)
Asked what clears a weak spot, and verified against the code rather than the
comment beside it. A statement's streak is read at the HIGHEST level holding
any record for it, and two clean answers in a row release it. So clearing
UPWARD works and clearing DOWNWARD does not: a miss at Italian-with-hints is
released by two clean answers at Italiano, while a miss at Italiano is not
released by anything done below it. That is the intent, since an Italiano
miss must be confirmed in Italiano.

It also exposed a dead end. An answer is written at the CURRENT level and
credit flows downward only, so drilling at Italian-with-hints could never
release a statement carrying an Italiano record. The weak-spot card appears
only once Italiano is complete, which means every statement has such a
record, so a learner who dropped a level and drilled would answer correctly
forever and watch the list refuse to move. startDrill() now switches to
Italiano, and both entry points say so before the switch.

The rule also fixes the drill's cost, which the ready date now uses: two
answers per question is the floor, so the reserve is that plus three days of
mock exams (five is the readiness ring's window, retries are likely, two a
day suits a 20-minute exam).

### Drilling weak spots early is supported (2026-09-11)
The drill was written for the reserve week, and two things assumed that. Its
answers were discarded from the daily log, on the reasoning that in the
reserve week everything is cleared already so nothing could be newly
cleared; and it left the learner at the exam level it switches to. A learner
drilling EARLY, to shrink the pile before the end, was therefore told they
had done nothing that day, and then carried on studying at Italiano without
meaning to. Both are fixed: a drill clear counts like any other clear, since
the drill runs at the exam level and genuinely advances the levels, and the
level is restored on every exit from the session. A day with answers but no
new clears is no longer drawn as a rest day; it gets a hollow dot and says
so. Early drilling also shortens the ready date's reserve by itself, since
that is computed from the current list.

### The drill now runs until the weak spots are actually released (2026-09-11)
Asked whether the second clean answer comes straight after the first or
after the rest of the queue, and the answer was neither: the retry pass kept
only the cards answered WRONG, so one correct answer dropped a card for
good. A statement at a streak of zero, which is most of them, went to one
and stayed in the list. The learner answered all 203 questions, was told
"Weak spots cleared: every question you kept missing answered correctly",
and found 203 still waiting; the second answer needed a second press of a
button that had just declared victory.

The pass now keeps every card holding a statement below two clean answers in
a row, and narrows the card filter each pass so a released statement stops
appearing while its neighbours finish. The second showing therefore comes
after the rest of the queue, which is the spacing worth having. It
terminates because the streak advances even though the historical wrong
counts that built the queue never reset, and the release rule now lives in
one function, governingStreak(), shared by the list and the session so they
cannot drift apart.

### Which obligation words earn bold, decided by counting (2026-09-11)
A reviewer asked for *consigliabile* and *facoltativo* to be emphasised as
traps (flags 23834, 23836). Counted the bank before answering, and the two
words behave oppositely. *Facoltativo* appears in 6 statements and ALL SIX
are FALSO: the exam only ever uses it to downgrade a duty, so it was added
to TRAP_IT_RE. *Consigliabile* appears in 20 and 16 are VERO, because the
bank also uses it for genuine advice ("è consigliabile evitare lunghe
soste"), so bolding it would teach a cue that misleads four times in five.
It stays out, which is also what the same reviewer concluded earlier from
the English side (flags 24738, 24746). *Opportuno* is worse still, 62 VERO
to 31 FALSO, and stays out for the same reason. The rule to carry forward:
a word earns emphasis only if it is near-always the flipper, and the way to
know is to count, not to reason from the one statement in front of you.

### "riprodott0": the one sanctioned edit to italian_text (2026-09-11)
A reviewer spotted "riprodott0" in 23949 and assumed our extraction had
misread the PDF. It had not: sources/DomandeB.pdf itself contains U+0030, the
digit zero, in that word. First response was to leave the text alone under
hard rule 1 and add a vocabulary entry for the literal token, so the tooltip
would at least fire. The maintainer overruled it: the defect is obviously a
typo, and carrying a workaround in the data for the rest of the project's
life costs more than the edit. So italian_text now reads "riprodotto", the
workaround entry is gone, and CLAUDE.md rule 1 carries the exception in
writing, scoped as narrowly as it can be: a character that is plainly not the
letter it should be, verified against DomandeB.pdf, recorded, and re-applied
after any re-extraction. Wording, grammar and anything arguable are still
untouchable, and ambiguity is still handled with warn/warn_it.

Scanned the whole bank for the same defect class, a digit glued to letters,
and this was the only one; the other 21 hits are legitimate (cm3, 0,1kW/kg).
validate_data.py now prints any such token, so a re-extraction cannot quietly
bring it back. The check was tested by reintroducing the zero and watching it
fire.

### "fattore di sicurezza" is not a safety factor (2026-09-11)
A reviewer read "constitutes a safety factor" (23982) as "a factor you must
consider in order to stay safe", which is how an American engineer reads the
phrase: a margin built into a design. The Italian pair is simpler and
opposite in shape. A *fattore di sicurezza* is anything that makes traffic
SAFER, a *fattore di pericolo* anything that makes it MORE DANGEROUS, and a
statement is true or false according to which group the thing belongs in.
The English translation now says "makes traffic safer" rather than
"constitutes a safety factor", the gloss says "something that makes traffic
safer (not a design margin)", and the topic 21 bullet that first introduces
the danger side now names both halves of the pair. Add "particolarmente
indicata" to the same class of trap: the bare gloss on *indicata* gave
"indicated/shown", the calque the glossary already warns against, which
inverts the sentence for a reader who assembles it word by word.

### Gloss-chain audit of the whole bank, and the wildcard collision (2026-09-11)
The maintainer asked whether the glosses a learner taps at the Italian level
actually lead to the meaning of the full English translation. Every one of
the 7,147 statements was read against its gloss chain by a reader working to
docs/GLOSS-AUDIT-RUBRIC.md (scripts/gloss_chains.py writes the batches).
351 statements failed, about 5%, and the failures were of three kinds.

The largest was a MATCHER flaw, not bad glosses. The final-vowel wildcard
that lets one entry cover an inflected family (veicolo/veicoli) also let
different words capture each other when they differ only in that vowel:
obbligo (noun) swallowed obbliga (verb), transito swallowed transita, fine
swallowed fino, subito swallowed subiti, colore swallowed coloro, fare
swallowed fari, entro swallowed entra, primo swallowed prima (208 times), and
"prima dei" swallowed "primo dei". The verb form was shown the noun's gloss
in 103 statements. The reader's proposals were to broaden each gloss to carry
both senses; that would have made every one of them worse. The fix is in the
matcher: a vowel is dropped from a word's wildcard class whenever it would
turn the whole term into another existing entry, so adding the colliding
form as its own entry is now enough, and 61 such forms were added.

The second kind was spans that gloss word by word but do not assemble
("mantenere accese le luci posteriori", "nel tratto successivo al suo
inizio", "non deve essere rispettata", which with its bare "non" read as a
prohibition). 176 phrases were added, 72 of which were immediately dead
because an existing longer phrase already covered the span, and those were
dropped rather than kept as rules.

The third was a handful of genuinely wrong glosses, including two that had
been carrying exam commentary inside the translation ("consente: allows; in
the exam read it as leaves allowed"), which rule 14 forbids and the checker
had not caught because its pattern list lacked that phrasing. Twenty glosses
were corrected. Yield by topic ranged from 1.5% (distanza di sicurezza) to
21% (guida in relazione: alcohol, fitness, first aid), so the idiomatic
topics are where the next pass should start if only part of the bank can be
read.

### Per-statement review anchors, and cross-topic ones (2026-09-12)
Two flags on card 4567 (26 trailer statements) turned out to be one problem:
a card-level anchor cannot serve a bundle. 24090 is about insurance, whose
line sits a sub-section below where the anchor lands, and 24106 is about BE,
C and CE, which is topic 22 and not this topic at all. The reviewer's own
proposal was the right one: anchor to the statement the learner is ON.

review_anchors.json entries may now carry a `stmts` map of per-statement
overrides, and an override may name a `topic`, so the overlay opens another
topic's review. The 📖 button picks the first statement still unanswered,
then the first standing wrong, then falls back to the card. A statement
anchor that names another topic outranks the card's own picture, which would
otherwise open the wrong review. Sub-sections became targetable at the same
time: scrollReviewToHeading searched h3 only, so every `### ` heading was
unreachable and anchors could only ever point at the top of a `## ` section.

The mechanism is bank-wide; the anchors are not. Only the two flagged
statements have overrides so far. Adding one is cheap and validate_data.py
checks the statement is on that card and the heading exists in both languages
of the named topic, so the right time to add them is whenever a reviewer says
"this is not covered here".

### Anchor pass over every imageless card (2026-09-12)
All 335 imageless cards carry an anchor, and all 335 were read statement by
statement against the heading their 📖 button lands on, using a catalogue of
every "## " and "### " heading in all 25 topics so a reader could name a
target in ANY topic. 433 statements were proposed for an override.

The cross-topic proposals were then verified a second time, by a different
reader shown the FULL TEXT of the section the statement would be moved away
from, with one instruction: reject if that text already answers the
statement. 42 of 179 were rejected on exactly that ground, which is the
failure mode to expect from this kind of pass. The clearest example: 18449
(motorcycles of at least 150 cm3 on the autostrada) was proposed for the
autostrada topic's "Who may not enter", but the definitions topic's own road
bullet already lists which vehicles the autostrada admits. Travelling to a
longer treatment of a subject is worse than landing on a short line that
answers the question.

391 overrides went in, 254 within the card's own topic and 137 pointing at
another, over 107 cards. Landing accuracy is now a per-statement property,
so a card of 26 or 54 statements no longer has to compromise. The batches,
rubrics and verdicts are in the session outputs if the pass is ever repeated;
scripts/gloss_chains.py has a sibling shape for building them.

### IT reveal pills in the English concept notes (2026-09-12)
Each paragraph, bullet and numbered item in an English review now carries a
small "IT" pill that opens that one block's Italian underneath it, plus a
show-all control in the overlay header. The Italian review has none: it is
already the Italian.

The pairing is the whole problem, and it is solved at BUILD time, not in the
app. The two languages are parallel but not identical: the English carries a
"For US drivers" note the Italian omits by rule 12, topic 11 has an entire
English-only section, and here and there a bullet in one is a paragraph in
the other. Positional pairing drifted. What works, in order: cut both files at
every heading and pair sections first, allowing only same-level headings to
match, which skips the English-only section cleanly; drop the US-comparison
notes by pattern before aligning, because they can never pair; then pair
blocks inside each section, straight across when the counts match (they do in
almost every section) and by a small dynamic program when they do not.

The scoring for that program is worth remembering. Shared words are a weak
signal across languages, and weighting length at all let a paragraph about
parking garages pair with the Italian definition of a ZTL. What works is the
markers that survive translation: the digits, the acronyms, and the Italian
terms the English notes carry in *italics* by design. Plus a diagonal prior,
since the extras are few and the true pairing stays near the diagonal. A pair
scoring below the floor is dropped rather than forced: a pill showing the
wrong Italian is worse than a block with no pill. Result: 1,074 of 1,078
blocks paired, and the 4 left out are all genuinely English-only.

The map stores an INDEX into the Italian blocks, not their text. Storing the
text doubled topic_reviews.json, 573 KB that every offline install downloads.
That means two mirrored implementations, the hash and the block splitter, one
in Python and one in JS; they were verified equal over all 1,074 blocks and
1,088 hashes, and validate_data.py now rebuilds the map on every run so a
review edited without re-running the build script fails the check.

### Keeping the two languages in sync, now that the pills depend on it (2026-09-12)
The IT pills made translation drift invisible in a new way: a paragraph
nobody translated no longer looks wrong, it just quietly has no pill. So the
build now checks the two languages block for block and FAILS on any English
block with no Italian, any Italian block with no English, and any section
present in one language only. validate_data.py rebuilds the whole thing from
the .md sources and compares against the shipped JSON, so a review edited
without re-running md_to_reviews.py is caught as well.

The exemption for audience scaffolding is DECLARED, with a trailing
`<!-- en-only -->`. The first version inferred it from the wording, exempting
anything that mentioned the US, and that is the wrong shape: it makes the
exemption a hiding place for real gaps, and it cannot cover a block like
"Parking garages work the same way" which is scaffolding without saying so.
13 blocks carry the marker today.

Turning inference into declaration also repaired two pairings. While the US
notes were being skipped by pattern they still sat in the alignment, and the
block counts they threw off caused "This topic has two halves" and "Remember
that these colors apply only to the direction signs" to go unpaired or worse.
Excluding them properly let the counts line up and both paired straight
across. The current state is 1,074 pairs, 13 declared English-only blocks,
and no Italian content without an English counterpart at all.

40. **No grab-bag bullets; one rule per bullet (2026-09-15).** The
    maintainer's standing rule, after flagging three of them in a week: a
    bullet that welds several rules together creates ambiguity. The learner
    cannot tell which sentence answers the statement, and the 📖 landing
    cannot help, because a claim scrolls to the BLOCK and the marker's guess
    at the sentence inside it is only that. The tubeless rules were the last
    example: they sat on the end of a bullet that already carried winter
    tires, studded tires, where chains go and when they may be used, joined
    by a semicolon. Split into nine bullets, each claimable.
    Measured across the 25 reviews on 2026-09-15: 416 blocks carry a
    semicolon and 49 open two or more sentences with a bold label, the two
    signals that are mechanical. Scoring the rest (sentence count, bold
    count, length) was tried and rejected: at three sentences and five bold
    runs it flags 161 blocks, and a hand sample showed most are long but
    COHERENT, one subject explained properly, so the score punishes thorough
    teaching rather than bundling. The judgment stays with the claim readers,
    who already report `split` for it. The two mechanical signals are
    ratcheted by `scripts/check_review_bullets.py` against
    `docs/review-bullet-baseline.json`: neither count may grow, so a new
    grab bag fails the check even while the backlog is worked down topic by
    topic through the rollout's split step.

41. **Plain English, and no figure of speech doing a rule's work
    (2026-09-15).** The maintainer flagged "A1 is the rung that owns the
    displacement cap" and asked what "owns" was supposed to mean. It meant
    nothing a learner could use: the rule is that A1 is the motorcycle
    category defined by a displacement limit, 125 cm3, and that is now what
    the line says. The register to avoid is the one that gives a rule, a sign
    or an exam a personality: a sign that *says* or *speaks*, a category that
    *owns* or *earns*, a family that *lives* on a road, a rule that *bites*,
    a vehicle that *wins* or *loses* at a junction, a *rung* of a *ladder*,
    a *sibling* sign, the exam that *loves* or has *favorites*. Fourteen such
    lines were rewritten across topics 02, 04, 05, 06, 09, 11, 12, 19, 22 and
    25, in both languages, including the Italian equivalents (*vive*,
    *morde*, *vince*, *l'esame gradisce*, *il quiz adora*, *battere il
    passaggio*). Note that a word list cannot police this: scanning the 25
    reviews for thirty suspect words returned 201 hits of which about a dozen
    were real, since "its own lane", "with particular care", "lose grip",
    "twin circuit" and "a pet in a cage" are all ordinary English. So this
    is why `scripts/check_review_english.py` matches PHRASES instead, 47 of
    them across four families (idiom, persona, exam, chat), in both languages,
    and is wired into CI. It must stay at zero hits: a pattern that fires on
    ordinary English is a bug in the pattern. Seeding it turned up seven more
    lines nobody had flagged, all of the form "the exam tests", "the exam
    asks", "the quiz probes", now rewritten so the fact stands on its own.
    Two related
    habits the same pass removed: naming the exam or the quiz in the notes
    (the notes teach the rule, the post-answer explanation names the trap),
    and the chatty aside, such as telling the reader that Italy's roundabout
    logic "startles American drivers".

### Rule 18 follow-up: 20697 defeated by the manual (2026-09-04)
The worked example under rule 18 (20697, "la circolazione si svolge a
doppio senso" in a strettoia) no longer carries the 🤔 badge. Two things
settled it. The course manual describes the narrows behind the
right-of-way disc as a stretch that "può essere percorsa solamente a
senso unico alternato" and glosses the yield disc as announcing that
traffic "non può svolgersi contemporaneamente nei due sensi": in the
Code's vocabulary a stretch is *a doppio senso* or *a senso unico
alternato*, never both. And the sibling statement on the same card,
20696 "inizia il doppio senso di circolazione", is already FALSO, which is
the bank fixing the term's meaning as rule 18(b) requires. The explanation
now states the two-term vocabulary and cites 20696. Principle: when the
bank is silent, the manual's terminology may decide a flag, provided a
sibling statement or a bank definition is consistent with it; cite both.
The `warn` list is now empty, which is the intended resting state.

### Paragraph landings and the standing line (2026-09-12)
Two complaints about the 📖 button, both from the maintainer's own study.
A section is often long, so landing on its heading still leaves the reader
hunting; and a FALSO statement can describe a duty that appears nowhere in
the notes, so any landing looks wrong.

The first is handled by a picker rather than by hand-placed anchors. The
`pairs` map already gives the app the Italian text of every review block,
and the statement is Italian too, so word overlap in one language is a
strong signal that needs no curation and does not rot when a paragraph is
reworded (a hand-placed block anchor would). Within the anchored section
the picker scores each translated block against the statement (stems of
words of four letters or more, digits kept, a stop list of function words
and exam boilerplate, and a word shared by more than half the section's
blocks carries no weight) and lands only when one block stands clearly
above the second: at least three shared stems covering a fifth of the
statement with a 0.1 margin, or two stems covering a quarter with a 0.15
margin. Statements about a figure ("in figura") abstain, since text cannot
place a drawing. A sample of about fifty picks put a wrong paragraph, still
inside the right section, at roughly one in six; the heading remains the
floor for the rest. Where the picker cannot know (cards 4618 and 4619, all
"La revoca..." and "La sospensione..." statements, whose section's four
paragraphs cross-reference one another) a `block` override on the entry
names the paragraph, checked by the build.

The second is a trap that shapes the first. Any signal shown before the
answer that only FALSO statements can trigger is an answer key: a notice,
a different icon, a landing that behaves differently. So the routing is
uniform (the picker lands 43% of VERO and 37% of FALSO statements, the
same floor for both) and the honesty comes from one sticky line shown
whenever the notes open from a card: these notes cover what the topic
regulates, and a duty, ban or permission you cannot find here is absent
because it is not a rule. That turns "nothing here answers this" into
evidence, which is how an instructor would answer, and it needs no
per-statement curation. The post-answer explanation then names the
invented rule and the real one it distorts, as the flag batches already
require. Do not add review paragraphs that deny inventions one by one;
they are noise in the notes and would never be complete.

### The section walk must follow the heading chain (2026-09-12)
The paragraph picker shipped looking like it did nothing on exactly the cards
the maintainer was studying. The cause was the section walk, not the scoring:
each block remembered only its NEAREST heading, and `## Towing a trailer`
opens straight into `### Hooking up`, so no block's nearest heading was
"Towing a trailer". The walk never started, found no candidates, and fell
back to the heading without a word. Twelve headings in the reviews hold no
text of their own, and 113 anchor entries across 101 cards pointed at one of
them. Fixed by giving every block the whole chain of headings it sits under,
in the app and in both Python mirrors. Paragraph coverage went from 1,441 to
1,792 of the 3,615 anchored statements.

Worth noting for the next heuristic: a silent fallback hid this. The picker
abstaining and the picker having nothing to choose from looked identical from
the outside. `scripts/review_landings.py` now makes both visible per topic,
which is how the trailer card was checked statement by statement.

The audit of that card also produced the first hand-placed paragraphs. Eleven
statements needed one: the two mirror statements (24091, 24104) tie exactly
with the T.A.T.S. bullet, since both blocks talk about something projecting;
24095 and 24105 want the T.A.T.S. bullet; 24099, 24100, 24102 and 24111 all
turn on "a trailer is a separate vehicle" (own plate, own inspection); and
24096, 24097 and 24107 were anchored to sections that do not contain the rule
that decides them, so they now name the numbers section and the exact bullet.
24096 also stopped jumping to the alcohol topic: topic 21 states the
over-3.5 t zero limit outright, while the alcohol section only says
"professional drivers", so the learner had to infer the very thing being
tested. A statement entry carrying only a `block` inherits the card's
section, which keeps this kind of pass to one field per statement.

### Mark the sentence, not just the paragraph (2026-09-12)
The maintainer reported that 24094 (the unused tow hitch must be withdrawn,
removed or folded back) did not reach the right place. The picker was in fact
landing on the right bullet, but that bullet opened with the electrical
connection, so the highlighted line read as unrelated and the button looked
broken. Measuring it over the bank: 121 blocks, covering 778 statements, hold
the tested rule past their first sentence.

Splitting all of them is the wrong remedy. Many are a single membership list
("These include curves, stretches of limited visibility, intersections...")
where separate bullets would scatter one idea. A prose scan for grab-bag
bullets was also useless: it returned 99 candidates, nearly all legitimate
glossary entries developing one subject. So the app now marks the SENTENCE
inside the landed paragraph, which fixes all 778 at once and needs no prose
edits. The hitch bullet was still split, because its three sentences were
three unrelated rules.

Two lessons about the token rules. First, the six-letter stems that work for
choosing a paragraph are too blunt for choosing a sentence inside one: they
treat *alcol* and *alcolica* as different words, which is precisely the word
that decides 24623, so that statement was marked on the sentence about the
2024 phone reform instead. The sentence step therefore matches whole words by
shared prefix. Second, within one paragraph the recurring words of the topic
(*guida*, *patente*, *sospensione* in a licensing paragraph) appear in nearly
every sentence and swamp the distinctive one, so they are dropped by the same
document-frequency rule the paragraph picker uses. With both, 24623 now marks
nothing rather than the wrong line, which is the honest outcome of a tie.

Verification worth repeating: a minimal DOM shim exercised markReviewSentence
over all 1,284 marked statements in both languages, 2,568 cases, checking
that the wrapped text equals the intended sentence exactly and that the
paragraph's visible text is unchanged by the wrapping. The walk has to skip
the IT pill and its hidden Italian, which live inside the same element and
would otherwise shift every offset.

### A fixed margin penalizes long statements (2026-09-12)
24116 ("nelle curve la fascia di ingombro è maggiore") did not reach the
paragraph that says exactly that. The scoring was right: the correct block
scored 0.29 against 0.14 for the runner-up, a two-to-one win. It failed on the
acceptance test, which demanded a gap of 0.15 and got 0.143. The gap is
measured as a share of the statement's own words, so a long statement divides
every gap down and a decisive win can miss a fixed threshold. Accepting either
a wide gap or a factor-of-two win adds 88 landings, including this one, and by
construction removes none.

Four other approaches were measured and rejected, which is worth recording so
they are not tried again. Weighting words by rarity WITHIN the section raises
coverage to 2,344 but sends speed-limit statements to a paragraph about speed
discs, because that paragraph happens to phrase things as the statements do
("velocità massime consentite") while the correct paragraphs state bare
figures; section-rarity actively penalizes the road-type words that identify
the right paragraph. Rarity across the bank fixes that case but loses 420
correct landings to gain 260. An absolute floor on rare-word mass costs
coverage and still admits the bad case. And requiring the paragraph to repeat
one of the statement's figures looks attractive until you notice that a FALSO
numeric statement prints the WRONG figure by design: it disqualified 24105
(whose trap is 50 cm against the notes' 30 cm) and cut FALSO coverage far more
than VERO, which leaks the answer.

The last point is the general lesson. Any rule that keys on agreement between
the statement and the notes will fire more often on true statements, so its
effect on the VERO/FALSO split has to be measured before it ships. The figures
to watch are in `scripts/review_landings.py`: P(VERO | paragraph) is 56% here
against a 52% base rate, weak enough to be uninformative and worth keeping
that way.

### Claims: the paragraph that answers a statement is declared, not guessed (2026-09-12)
After two days of tuning a word-overlap picker, the maintainer asked for a
robust solution: the 📖 button is something a learner presses hundreds of
times over months, and a landing that is right five times in six, with the
sixth found by the learner, is the wrong shape for a selling point.

The design puts the mapping in the review markdown, next to the paragraph:
`<!-- q: 24094 -->` on a block claims that statement. Four properties follow.
The claim moves with the text when the paragraph is reworded, where a content
hash in a side file went stale on every edit (three times in one afternoon).
An editor sees which exam statements depend on the line being changed. The
build validates every claim (statement exists, claimed once anywhere, block
has an Italian twin) and reports coverage per topic. And a topic marked
`<!-- claims: complete -->` guarantees the property the maintainer wanted:
every statement is claimed or declared absent, or the build fails, and the
app stops guessing for that topic. Unclaimed and absent land identically (the
card's section heading), because a landing that only invented-rule
statements get would give the answer away.

Topic 21 was the pilot, 332 statements. The machine picker's landings were
offered as proposals; three readers, each with a third of the statements, the
numbered blocks in both languages, and a rubric (scripts/claims_packet.py),
confirmed 133 of the 147 proposals and overturned 14, placed the other 185,
and declared 12 absent (trailer width, hazard lights when towing live
animals, parking sensors, matching tire pressures, and the like: subjects the
notes never discuss). A fourth reader, blind to all of that, re-decided a
random 40 and matched 38 exactly, listing the first choice as an acceptable
alternative on the other two. Compare the picker's one-in-six.

The pass also produced two lists the picker could never have. Fifty-one
statements land on a block that covers their subject but never states the
deciding fact (B043 on cyclists says they are hard to judge, but not that an
elderly cyclist turns slowly to look behind, which 23966 tests). And seven
blocks bundle several unrelated rules, so that a landing is right at the
bullet and wrong at the line. Both are content work, and both are exactly
what a maintainer needs to know to make the notes complete.

### Gaps on true statements are not a weakness but a hazard (2026-09-12)
18357 ("le strade extraurbane principali sono provviste di corsie di
accelerazione", VERO) landed on the right paragraph, the definition of the
main extra-urban road, which never mentions acceleration lanes. With the
standing line in place that is worse than a poor landing: the line tells the
learner that a rule they cannot find is absent because it is not a rule, so an
unfilled gap on a true statement pushes them toward the wrong answer. The
claim readers had already listed 51 such gaps in topic 21 and 114 in topic 16.

They were filled in one pass. For each block with gaps a reader wrote the
missing fact in both languages, derived from the statements' answers and
explanations and stated positively (the notes teach the rule; the post-answer
explanation names the trap). Fifty-seven additions: a one-sentence addition
joins its block, a longer one becomes a new block right after it and takes
over the claims it covers, so the landing stays a sentence, not a swollen
paragraph. 18357 now marks "Like the autostrada, it has acceleration lanes
for entering and at least two lanes in each direction." Two gaps stayed open
by design: a pictured work-vehicle panel the notes have no figure for, and
an invented 3 m towing gap that has no positive rule to state.

Rule 13's checker flagged one addition, the definition of the acceleration and
deceleration lanes under "Parts of the road", because "deceleration lane" is
bold and the autostrada figure sits in another section. The bullet is a
definition, not a sign explanation, so the fix was to un-bold the term, which
the writing rules ask for anyway.

### A claim lands on the rule, not on the denial of a confusion (2026-09-12)
18385 ("l'isola di traffico è una zona destinata al parcheggio dei veicoli",
FALSO) landed on "A traffic island is not a safety island, a median, or a
parking, pull-off, or U-turn area." The claim refutes the statement, so it
passed the rubric, and it is still the wrong place: that line is a memory aid
which presupposes the definition, so the learner is told what the thing is not
and never what it is. The section states the rule two bullets earlier, "No
vehicle may drive, stop, or park on it", and that is where the statement now
lands. Three neighbours moved too: the parking-bay statement to the same rule,
the U-turn one to the definition, and the boarding-passengers one to the
salvagente's own definition, which is the function it misattributes.

The rubric now carries the distinction (claims_packet.py, rule 5b), and it is
worth stating precisely, because a denial is often the right target. Land on a
negative sentence when it answers the statement ("il salvagente serve a
dividere i sensi di marcia" is answered by "it does not divide traffic
directions, that is a median"). Do not land on one that merely enumerates what
the thing is not, when the notes state what it is.

A scan of both finished topics for the pattern found ten candidates and only
this group was the fault: the rest deny exactly what their statement asserts.
Three of the ten (18573, 18576, 18577, on replacing a light quadricycle's
exhaust or engine) sit on a real content gap in topic 18, which has not been
claimed or gap-filled yet, so they are expected to be imperfect.

### 42. The English half is written FOR Americans, so the American word IS the word (2026-09-16)

"The **brake booster** (what Americans call **power brakes**) uses engine
vacuum..." hands the reader a term they do not use, then translates their own
everyday word back to them as if it were the foreign one. The app exists to
teach Italian rules to American drivers, so in the English half the American
name is simply the name, and the ITALIAN word is the one that gets glossed:
"**Power brakes** (*servofreno*) multiply the force of your foot..."

The same line also said "the **parking brake**, what Americans call the
**emergency brake**". Two faults. Americans use both names for that lever, so
neither is a translation of the other. And Italy has a THIRD brake whose name
collides with ours: the *freno di soccorso* is the back-up that works on the
surviving circuit when the service brake fails. Calling the parking brake "the
emergency brake" in an Italian context therefore invites exactly the confusion
the notes should prevent, which is why the point now lives in a
`> **For US drivers.**` note instead, where a comparison belongs.

Where a US comparison genuinely helps, it goes in one of those notes, marked
`<!-- en-only -->`, not inside a rule bullet. Where it carries nothing, drop
it: topic 14 called position lights "what Americans call parking lights", and
the comparison was not merely patronizing but wrong, since US parking lights
are amber at the front and Italian *luci di posizione* are white.

`scripts/check_review_english.py` now fails the build on the construction (the
`reader` family, three patterns). Seeding it turned up a third instance nobody
had flagged, in topic 16's motorhome bullet.

### 43. A reference text has no author on the page: no first person (2026-09-16)

"We call the parking brake the emergency brake too" reads as a conversation,
and it also smuggles in a point of view: whose "we"? The notes are a reference
text. The register is the third person, with the imperative for rules ("use a
low gear") and "a driver" or "in American usage" where a subject is needed.
The one exemption is quoted statement wording, since the Ministry writes many
statements in the first person ("we have the right of way"), and those are
quoted, not spoken.

The same note also failed as teaching, and the two faults are related. It
compressed the point into a clever line ("three jobs done by two things you
touch") instead of stating it. The reader's confusion was concrete: an
American knows two brakes, the Italian code names three, and the American
name for the second one, "emergency brake", sounds like the Italian name for
a different one, *freno di soccorso*. A pedagogical note names that collision,
says what the *freno di soccorso* actually is (the braking the intact circuit
still provides after a partial failure, with no control of its own), draws the
count (three brakes in the legal sense, two controls), and ends by telling the
reader what each Italian term means when a statement uses it. Every sentence
carries a fact. `check_review_english.py` now fails on the first person in
English prose outside quotation marks (the `reader` family).

### 44. The test is not "would an American say this" but "would a reference text print it" (2026-09-16)

Rule 41 removed slang and figures of speech, rule 43 removed the first person.
This is the rule they were both reaching for, and it was named by the
maintainer after "you never grab reverse gear" was corrected to "never use
reverse gear".

The first diagnosis of that line was wrong and worth recording. It was called
conversational, as though it were something an American would say and the
notes were merely too formal to print it. That is not the case: no American
says "grab a gear" in any register. A driver uses or engages a gear. "Grab"
reaches for a control with the hand, so the only place it even collocates is
the parking brake, and there it is conversational and still wrong here.

So a word can fail this rule two ways, and they need different fixes. Either
it is not the word American English uses for the thing, which is an error of
fact about the language and is corrected by naming the thing properly, or it
is the right word in the wrong register, which is corrected by choosing the
plainer one. Asking only "is this too casual?" catches the second and misses
the first.

The register to hold is a reference text: the third person, the imperative for
rules, the ordinary technical name for each part, and no sentence whose work
is to sound friendly.

### 45. The answer-key pass: 25 topics, two doubts, both closed (2026-09-16)

Between 2026-06-11 and 2026-07-03 every topic received a full per-statement
pass whose one job was to question the Ministry's official VERO/FALSO. The
reviewing agent could not change `answer` (hard rule 1), so it wrote its
doubts to a per-topic file, `docs/answer-flags-NN.md`, for a human to
adjudicate.

**The whole campaign raised two doubts, and both are closed.** 18613 and 18614,
on card 4029, asked whether the official VERO could be right when the panel in
the figure looked like the wrong one. It could: the source PDF carries a
separate figure per STATEMENT, and the app was showing one card-level image
for the whole card. Once `extract_statement_images.py` split them out, 18613
showed the orange ADR dangerous-goods panel and 18614 the red and white
projecting-loads panel, so both official answers were correct all along. That
finding is why per-statement figures exist at all. Both statements are still
VERO today, on variant cards 5060 and 5061.

Every other topic returned "no answer-key doubts". So the standing position is
that the Ministry's key has been checked statement by statement across the
whole bank and found sound, and a future doubt is a new finding rather than
one of a known list.

The 24 files are retired into this paragraph. They were write-once receipts,
one commit each, none revisited after 2026-07-03, and 23 of them said only
that nothing was wrong. They were also numbered by REVIEW FILE rather than by
app topic, so half of them appeared to concern a different topic than they
did. The outcome of each pass is in the data and the narrative is in the
per-topic sections of this file, which are longer and better.

### 46. The SIDA manual cross-check, per-topic notes (moved here 2026-09-16)

`docs/MANUAL-CROSSCHECK-PLAN.md` instructed its own reader to "move the
per-topic notes into `docs/review-glossary.md`" once the pass was complete.
The pass finished on 2026-09-04 and the notes follow, verbatim, one section
per topic, recording what the manual changed in each review and why. The plan
file keeps only what is still open.

#### Per-topic notes, as applied 2026-09-04

(Add a heading per topic as it is worked: report, decisions, image wishes.)

### Topic 03, Segnali di pericolo (chapter 2), applied 2026-09-04

Applied, each checked against the bank's own statements first (no conflict
found): urban placement down to 50 m; curve rules with the two-way condition
on keep-right (18970 marks it false on a one-way road) and the three cases
where overtaking is allowed; countdown panels at 150/100/50 m, before the
cross, also with the movable bridge; barrier vs half-barrier lights, trestles,
heavy traffic, stop line, resume when the light goes out, no obligatory stop
when signals are off, second train at the double cross; braking distance up
on descents and down on climbs; dosso/cunetta are not "strada deformata",
cunetta collects water/mud/debris; new bullet for strada deformata (card
4051/4052, overtaking allowed, 18877); tram priority, overtaking a moving tram
on either side, less grip on rails, not a trolleybus; two-way sign = end of
one-way, overtaking allowed; children on the sidewalk, no school-hours
meaning; fire sign always with extent panel, cigarettes, no ban on flammable
cargo; crosswind lateral distance; gravel reduces grip; no stopping on the
stripes; narrowing gives no priority and is not an alternating one-way;
movable bridge hours panel and flashing lights (19267: the sign itself does
not order a stop).

Left alone: the manual's opening on the hierarchy of signals (topic 15);
"-8 points" for failing to yield to pedestrians (bank statement 19160 does
not quantify; verify the current Code before adding a figure).

Image wishes: none. The manual's sequence drawing of a crossing approach
(triangle, three panels, cross) would help, but 4071.jpeg already shows the
panels; consider an SVG of the whole approach later.

### Topic 05, Segnali di precedenza (chapter 3), applied 2026-09-04

The review already matched the manual on every rule; four additions, each
backed by a bank statement: the X junction sign stands on a road of equal
standing, never on the priority road, and precedes neither a yield nor a
STOP (20540, 20542, 20543), with the manual's behavior (slow particularly,
check that traffic from the left yields); at a merge, ease the ramp
traffic's entry despite having priority (20656, 20646); on the priority road
you still yield to emergency vehicles with blue light and siren (20667) and
check that side roads yield (20669); the alternating one-way yield disc also
stands where part of the carriageway is closed for road work (20548, 20561),
and it announces neither a work site (20676 on the diamond, same trap) nor a
two-way section (20556, 20557). No disagreements. Image wishes: none.

### Topic 04, Segnali di divieto (chapter 4), applied 2026-09-04

One correction: the no-motor-vehicles sign was described as exempting only
two-wheeled mopeds and motorcycles; the bank also lets non-motorized
vehicles and pedestrians through (19708, 19518-style) and bans motor
tricycles and quadricycles (19704, 19707). Additions, each bank-backed: no
through traffic bans bicycles, mopeds, quadricycles and electric cars,
stands at both ends, can be time-limited, lets pedestrians pass, and is not
an invitation to enter for parking (19513-19526); do-not-enter binds
non-motor vehicles, mopeds, motorcycles, quadricycles and taxis, at night
too, exit still allowed (19529-19537); speed limit also on autostrade,
slower allowed (19594, 19610, 19864); minimum distance at any speed
(19584); motorcycle ban leaves tricycles/quadricycles free (19680); bicycle
ban covers pedal quadricycles (19671); agricultural ban lets snowplows and
quadricycles pass (19757, 19762); trailer ban panel up to a mass (19746);
water pollutants on a trailer banned, water tankers and sprinklers pass
(19787-19789); fuel tanker caught by the dangerous-goods sign (19771); 3.5 t
truck ban by registered mass, panel may set another figure, motorhomes
over 3.5 t pass (19729, 19730, 19740); height incl. load, under bridges
(19807, 19811); width binds all vehicles (19799); end of no-passing valid
24 h, urban and extra-urban, solid line still bars overtaking (19873,
19876, 19878); new bullet for the hours-regulated parking sign, card 4147
(20003-20013: parking only, no disc, no towing).

Left alone: the manual's 100 m spacing for autotreni under the 3.5 t
no-overtaking sign (a general rule, not tested on that card; 19754 marks
it false on the width card).

### Topic 02, Segnali di obbligo (chapter 5), applied 2026-09-04

No disagreements. Additions, each bank-backed: the direction signs say
nothing about a one-way street (20056, 20065, 20039, 20139 all false) and
the advance versions may carry a distance panel (20123, 20150); the
roundabout sign is preceded on extra-urban roads by the triangular warning
(20287) and never sits on the central bollard (20280, 20289); the bridle
path shuts out all vehicles, electric ones and bicycles included
(20409-20411), and its end sign is not a stretch closed to horses (20424);
an end sign ends exactly its own path (20406, 20408) and forbids nothing to
its users (20355); the chains sign stands on roads that can be snowy or icy
and bars vehicles without the equipment (20329-20334); DOGANA is a border
with a non-EU country (20433: 'only with an EU country' is false); ALT
POLIZIA announces neither a state border nor a customs check (20440,
20443). Left alone: the manual's generic/specific split of mandatory signs
by color (not tested).

### Topic 01, Segnali di indicazione (chapter 6), applied 2026-09-04

No disagreements. Additions, each bank-backed: autostrada symbol with an
arrow points to a toll station (21543); new bullet for the exit advance
sign 'itinerario extraurbano', card 4290 (21462-21470: distance to the
exit, not to the town or every listed place, road continues); the
end-of-town sign is not a main-road sign (21482); the dead-end signs do not
forbid a U-turn (21612, 21619) and hold for motorcycles (21606, 21617);
pull-off bay for a stop, distance panel (21693-21696); bus-stop sign is not
a parking area for buses/trolleybuses (21765); camper service area serves
any vehicle with sanitary fittings and is not a toilet (21786, 21788).
Left alone: the manual's extra background colors (black industrial, red
SOS) and the lane-minimum 'move right' rule, not tested here.

### Topic 06, Segnali complementari; temporanei e di cantiere (chapter 7), applied 2026-09-04

Small bank (180 statements, 19 cards). No disagreements. Additions: cones
for at most a couple of days (21866; 21871 marks a ten-day site false);
two-way delineators red on the right, white on the left, reflectors on
walls where a post cannot stand, same colors in a two-way tunnel (manual,
no bank statement contradicts); the mountain delineator may stand with a
guardrail and is not reserved for roads without barriers (21958 false);
the T-junction chevron barrier also has a white-and-red temporary version
(manual); the obstacle delineator is always paired with a passage sign and
has no light of its own (21949, 22002). Left alone: the flagman's paddle
(red stop / green go) and artificial speed bumps at 50 km/h or less, both
tested in other topics.

### Topic 08, Pannelli integrativi (chapter 8), applied 2026-09-04

No disagreements. The review showed the 'other dangers' panel gallery but
described only four of them; a paragraph now covers the rest in the bank's
own terms: accident (22114-22123), queue (22158, 22159), shunting tracks
not a level crossing (22132), work machinery (22166-22176), flooding
(22145-22148), slippery in rain (22189-22194), slippery from ice
(22177-22182), trucks slowing on a climb (22201, 22202, 22205; 22012 and
22075 mark 'indicates the grade / an uphill road' false).

### Topic 15, Segnalazioni semaforiche e degli agenti (chapter 9), applied 2026-09-04

No disagreements; the review already carried every officer signal and light
the bank tests (252 statements). Additions: a light that is off or broken
lets you cross with the utmost caution (21038, 21039) and the default
priority-to-the-right rule then applies (manual); switched-off lane
signals let you pass with particular caution (21086). Left alone: the
manual's police-car display messages (ACCOSTARE / ALT POLIZIA /
INCIDENTE) and the agents' inspection powers, not tested in this topic.

### Topic 07, Segnaletica orizzontale (chapter 10), applied 2026-09-04

No disagreements. Additions: the mixed double line rule stated in words
(the stroke immediately to your left decides; cards 4216/4217, 20762-20773);
double continuous also bars the left turn (20730) and overtaking must fit
on your side (20728); studs may supplement a continuous line but never
replace a broken one (20718, 20724); bike crossing behavior and its
extra-urban warning triangle (manual). Left alone: the 15 m no-parking rule
around a bus-stop sign without markings and the cyclists' advance stop box,
not tested here.

### Topic 11, Limiti di velocità (manual 12.1), applied 2026-09-04

No disagreements; every number in the review matches the manual and the
bank (256 statements). Additions: what makes a 150 km/h stretch (three
lanes, emergency lane, average-speed enforcement; 22336, 22397, with 'any
autostrada' and a day-time bonus false in 22342, 22408, 22468); light
quadricycles share the mopeds' 45 (manual; bank tests only mopeds 22340,
22400 and non-light quadricycles 22341); tracked machines 15 km/h and
heavy-bus caps 80/100 (manual, untested, consistent with the speed-disc
statements 22433). The slow-down list already matched 22299-22461.

### Topic 09, Distanza di sicurezza (manual 12.2), applied 2026-09-04

No disagreements; the review's definitions and the five one-second figures
match the manual and the bank (134 statements; 22618-22633 on total
stopping distance, 22611-22617 on grade). Added the course-book rules of
thumb (reaction = V/10 x 3; total stopping = (V/10) squared) marked as
estimates, and the manual's 'prudent' vs 'minimum' distinction. Left
alone: the braking formula V^2/(250 f), not tested.

### Topic 22, Patenti e documenti (chapter 20), applied 2026-09-04

One correction: the review said 'no bonus ever reaches 30'; the Code and
the manual give +2 points per clean biennium up to a maximum of 30. The
bank does not test the 30 ceiling directly but is consistent with it
(24645: two clean years restore 20; 24653: 'to 30' false only as the
result of two clean years; 24651: the recovery course reaching 30 false).
Rewritten in EN and IT. Addition: the bank's no-points offenses (24666,
24668, 24669, 24676). Everything else (ladder ages, A2 no-detuning, B96/BE,
75 kW/t and 105 kW, 20/15/2-year rules, validity 10/5/3/2, BS 5 years,
ritiro/sospensione/revoca/revisione cases) matched the manual and the
bank (230 statements). Left alone: foglio rosa details, accompanying
driver (<=65, license >=10 years), plates and the DU, none tested here.

### Topic 16, Definizioni e classificazione dei veicoli (chapter 1), applied 2026-09-04

Two corrections on the work machine: it may carry up to three people
including the driver (manual; the review said 'no passengers'; bank 18588
marks 'four passengers' false, consistent), and its speed cap is 40 km/h on
tires and 15 on tracks (manual, matching topic 11; the review said 'not
faster than 50', which the bank's 18586 phrases as a false statement about
exceeding 50, so both readings agree with the bank but 40/15 is the rule).
Additions: agricultural machines' permitted road use and the same
three-person / no-standing rule (18579-18591); trucks also carry the
people handling the goods; the other autoveicoli (road tractor, specific
transport, special use, mezzi d'opera) named; trailers have their own
lights and plate (18596), and the carrello appendice cannot be towed by a
road train, articulated truck or bus (manual). Left alone: the 2021
'120 cm3 / 6 kW with an adult rider' autostrada rule, since the bank still
tests 150 cm3 (18449) and the review already says so; the 25-building
definition of a built-up area, not tested here.

### Topic 14, Uso delle luci, dispositivi acustici, spie (manual 11.1-11.4, 22.2), applied 2026-09-04

No disagreements (176 statements; every beam rule, horn case and dashboard
color matched). Additions from the manual, consistent with the bank: when
to use the hazard lights and that they do not replace the triangle (24216-
24222); amber side reflectors on vehicles over 6 m and on trailers; brake
and reversing lights; parking lights only in town, traffic side, colors,
optional (24153, 24156); amber as the dashboard's third color for the rear
fog light and defrosters (24296, 24316 mark amber/yellow false for the oil
and belt lights, i.e. amber belongs to the minor functions).

### Topic 19, Dispositivi di equipaggiamento (manual 11.5-11.8), applied 2026-09-04

No disagreements (135 statements on 12 cards; belts, child seats, airbag,
headrest, helmet, clothing all matched). Additions from the manual: the
Code's further belt exemptions (refuse collectors, emergency crews) and the
driver's responsibility for minors only; the E approval mark, i-Size
sizing by height and rear-facing to 15 months, kept subordinate to the
bank's 'groups by weight' (24367); the taxi/NCC exception for children
over 3 in the rear seat; headrest geometry (top of head, 10 cm). Left
alone: mirrors, window films, triangle and vest, posture, which the manual
puts in this chapter but the bank tests under other topics.

### Topic 13, Norme sulla circolazione e posizione (chapter 13), applied 2026-09-04

No disagreements (379 statements). Additions: the parallel-lines fine
print (never on two- or three-lane two-way roads 22793, 22819, 22872;
definition of heavy traffic; lane change only to turn or stop 22864,
22870; no indicator held 22876; no bus lanes 22823; not obligatory 22875;
single carriageway allowed 22877; mopeds and non-motor vehicles excluded,
manual); three separate carriageways, right or central (22814); U-turns
also banned in tunnels, on one-way roads and across a solid center line
(manual; 20920 in topic 07 agrees; note 22934/22942 phrase the 'check the
line' duty as false, so the review states the ban, not a checking duty);
tram rails, city gates and safety islands (manual, untested here).

### Topic 25, Esempi di precedenza (chapter 14), applied 2026-09-04

The manual prints the Ministry's answer key for the 44 intersection figures
(letter orders). I matched our 49 cards to the key by their vehicle letters
and machine-checked 131 order statements (first/last/before/after/full
order) against it: all agree with the bank's VERO/FALSO. Seven apparent
mismatches were checker artefacts (yield-to owed only where paths cross,
'subito dopo', and three cards sharing the letters A-N-R that map to
different figures). The review is a method guide and needed no change;
one summary point added on prudence and the 5/6-point penalty (manual).

### Topic 10, Norme sul sorpasso (chapter 15), applied 2026-09-04

One correction: the review said trams and trolleybuses are 'normally passed
on the right because they run on rails'. A trolleybus runs on tires; the
bank says a moving tram may be passed on the right (23569) or on either
side on a one-way road (23486), and a stopped tram or trolleybus on the
right only with a safety island (23487-23489, 23585). Rewritten. One
consistency fix across reviews: topic 16 said the law sets no lateral
distance for passing cyclists, topic 10 said 1.5 m; both now say the bank
marks '2 m' false (18835) and the 2024 Code asks 1.5 m where the road
allows. Addition: night passing on a two-lane extra-urban road (manual;
23580 marks a night ban false). Everything else matched (156 statements).

### Topic 12, Fermata, sosta, arresto e partenza (chapter 16), applied 2026-09-04

No disagreements (190 statements). Additions, each bank-backed: asking an
officer for directions is not a lawful halt if it obstructs (23655, 23657);
a halt near a sign that stays visible is fine (23684), but none on
preselection arrows, channelizing lanes (23679) or acceleration lanes
(23687); no halt on a crosswalk even to drop a passenger (23693) and none
on bike crossings (manual); the explicit list of places where a halt IS
allowed (driveway outlet, waste bins 23692, an open fuel station 23682,
market and loading areas, second row if no obstruction 23696).

### Topic 21, Ingombro, veicolo fermo, traino, autostrade (chapter 17), applied 2026-09-04

No disagreements (332 statements; triangle 50 m / 1 m / 100 m visibility,
3 h, 24 h, 500 m, panels, trailer ratios all matched). Additions: more of
the autostrada exclusion list (sidecars under 250 cm3, no pneumatic tires
23863, poor condition, out of inspection, oversize); pedestrians on the
emergency lane only to reach an SOS point (23866); lights during a night
emergency stop and the triangle when the vehicle cannot reach the
emergency lane (manual); the course-book advice of 100 m on the autostrada,
marked as advice beside the bank's 50 m (23831).

### Topic 17, Guida e condizioni psicofisiche, alcol, primo soccorso (manual 18, 19.2), applied 2026-09-04

No disagreements (141 statements; the bank tests effects and duties, not
figures beyond 0.5 / 0.0). Additions from the manual, consistent with the
bank: empty stomach and medicines amplify alcohol, impairment already
below 0.5; the sanction bands (fine/points/suspension up to 0.8, crime and
arrest above 0.8, vehicle stop and possible revocation above 1.5 or on
refusal, harsher at night or after a crash, vehicular homicide), keeping
24850's 'arrest'; the wider list of impairing medicines (24833, 24843
name sedatives); the former addict and the medical commission; drowsy
driving conduct (slow down, keep right, first bay 24827) and trip planning.
Chapter 18's conduct material (tolerance, junction prudence, vulnerable
users, two-wheelers, distraction, field of view) is tested under topics 16
and 18 and was checked there.

### Topic 18, Prevenire incidenti, in caso di incidente (manual 19.1, 19.3-19.5), applied 2026-09-04

No disagreements (126 statements; ice card 24738-24748, tunnel card
24792-24798, crash card 24764-24766 all matched). Additions from the
manual: ice distance three to four times, never in neutral (24748), off
the barrier (24745), no hard braking when meeting; vehicle fire (sand,
wet blanket, never drain the tank); the crash-without-injuries procedure
(clear the road, details to note, when to call the police, hit-and-run,
parked car), the signed claim form and passenger witnesses; with injuries,
no moving except imminent danger, onlookers, helmet visor, duty to animals,
arrest for leaving. The manual's detailed first aid (CPR 30:2, tourniquet,
recovery position) is not tested in this topic and stayed out; topic 17
carries the tested first-aid rules.

### Topic 23, Responsabilità, R.C.A. (manual 19.6), applied 2026-09-04

Two corrections. The force-majeure example "a sudden mechanical failure"
was replaced by the manual's earthquake or flood (the bank, 24986, gives
no example, and a mechanical failure is not what the law means). The
Italian review said an uninsured vehicle can be "sequestrato"; the bank
(25021) and the manual say confisca. Additions, all checked against the
bank: the civilly liable driver may agree the amount directly with the
injured party and repair his own vehicle, and may not offer to have his
license revoked instead (24969-24972); criminal-plus-civil responsibility
may lead to suspension, revision or revocation of the license, none
automatic, and not always preventive arrest (24977-24982); RCA covers the
owner as well as the driver whoever drives (25054, 25064) and passengers
when the vehicle is authorized to carry persons, not only taxi passengers
(25007, 25013); the limits are not the yearly sum paid, do not rise
every year and are never refunded (25043-25045); the guarantee fund also
covers insolvent insurers (manual) and does not cover underage drivers
(25032). Left out as untested: joint liability wording, parents of a
minor, attestato di rischio, franchigia and fixed-rate formulas, the
right of recourse (rivalsa), rischio statico for trailers, CONSAP, and the
December 2023 private-area rule.

### Topic 20, Elementi costitutivi, manutenzione (manual ch. 21), applied 2026-09-04

No disagreements between the review and the bank. Two sharpenings:
engine braking is greatest in first gear (25268, the review said "a low
gear"), and the space-saver spare's limit is about 80 km/h (manual; the
bank only rules out 120, 25265). Additions, all bank-checked: never
coast a descent in neutral or with the engine off (25275, 25311, 25390);
brakes turn kinetic energy into heat (25306); locked wheels do not steer
(manual, consistent with 25224); the three brakes and what does not
cause unbalanced braking (25328-25336, 25333-25334); tire pressure
effects, over-inflation, unequal pressures, rim material, long trips,
trailer, TPMS, no cooling by deflating (25230-25239, 25300-25304,
25321); studded tires on all wheels (25252); chains on a 4x4 on all four
and only on snow (25253, manual); tubeless nail handling (25244, 25247);
suspension traps: every wheel, straights too, no sports suspension, no
driver adjustment, pressure does not cure overload, no fixed mileage,
maintenance under warranty, one broken unit matters (25345-25385);
power steering does not improve braking and fails heavy (25395, 25398);
hands at 9 and 3 (25399); exhaust: no glass-wool patch, workshop only,
not at every oil change, no tampering, electric cars have none
(25411-25417); kill switch repaired promptly (25423). Aquaplaning is
tested under topic 18 and was handled there. Left out as untested: the
adhesion-coefficient table, tire markings (195/65 R15), emergency-braking
clutch technique with and without ABS, and catalytic-converter warm-up.

### Topic 24, Consumi, inquinamento (manual 22.1), applied 2026-09-04

No disagreements (103 statements). Additions, all bank-checked:
consumption rises above all with speed, with weight, a trailer, and
hilly or congested roads (25067, 25068, 25070, 25149); no prolonged low
gear, no maximum revs, no flooring when shifting, no throttle blip
before a shift (25101, 25128, 25135, 25136, 25142); diesel injection
pump and injectors (25132); the catalytic converter needs heat, so
pollution is greater right after a cold start (25107); clutch,
differential and shock absorbers are irrelevant to air pollution
(25103, 25104) and the oil filter is not seasonal (25138); hybrids
pollute less (25075); horn only for immediate danger or carrying the
injured or seriously ill, not banned everywhere, not "flashing lights
only at night" (25082, 25085, 25165); no revving during traffic stops
and gentle door closing (25083, 25084); scrapping not restricted to the
maker's dealer (25159); damaging road installations and abandoning
hazardous waste are punished (25158, 25160). Left out: the manual's
appendix pointer on combustion engines, electronic injection detail,
and the residential-parking and practice-driving distractors (25164,
25167), which the review already implies.

All 25 topics of the accuracy pass are now complete.

### 47. Topic 20 claimed: the split is the work, not the claiming (2026-09-16)

Topic 20 went from 13 claims to **284 of 284**, zero absent, blind check
**39 of 40**, the highest agreement of the five topics done so far. Three
things are worth carrying forward.

**The split was the whole job.** Before it, one paragraph on suspensions and
shock absorbers carried **47** statements: what a suspension is for, what
shock absorbers do, wear, overloading, sports springs, owner adjustment,
replacement and warranty, in five sentences. Cards 4707 to 4710 had almost
nothing else to land on, so every claim on it was nominally correct and
practically useless. Thirteen bundled blocks became **77 bullets**, and the
heaviest block now carries 10 statements instead of 47. The claims were
redistributed by the readers themselves, one statement to one bullet, so no
re-read was needed, unlike topic 13 where the split came after the claiming.

**Splitting exposes the gaps that claiming hides.** A statement can sit on a
paragraph that mentions its subject and looks settled. Split the paragraph and
the statement lands on a bullet that plainly does not decide it. That is how
these surfaced: sidewall checks were never mentioned although a VERO statement
turns on them, the ban on adhesive film on the windshield and front side
windows was missing while the notes said only that stickers reduce visibility,
nothing said a working muffler is required on every road, and nothing said what
a transmission chain connects. Four additions closed seven statements.

**Two gaps were left open on purpose.** 25173 (excessive grip overheating the
brakes) and 25191 (low grip saving fuel) are inventions whose only possible
fill is a paragraph denying them, which the standing-line doctrine forbids.
They stay unfilled and the standing line carries them.

**The one blind disagreement, 25335, kept its claim.** Running on methane is
one of eight invented causes of weak braking that the bank tests. The blind
reader moved it to the block listing the real causes, per rule 5b's preference
for the block that states the rule over the one that denies a confusion. It
stays on the denial block, for two reasons. 5b's own exception applies, since
the statement's point IS the invented connection and the notes discuss methane
nowhere else. And its seven siblings are all claimed there, so moving one
would make a single card land in two places for one idea.

### 48. The notes do not name the exam, with one exemption (2026-09-16)

Rule 41 has always banned the notes from naming the exam or the quiz: the
notes teach the rule, and the post-answer `explanation` is where a trap gets
named. The ban was enforced by a handful of verb patterns (*the exam loves*,
*il quiz adora*), which caught the showy cases and left the quiet ones.
A sweep on 2026-09-16 found **60 mentions in 20 topics**: 8 of them inside the
four kept sections (each block exists in both languages), and **52 elsewhere**.

**Four of them were kept, and they are a teaching device, not a slip.** Topics
02, 03, 04 and 05 each carry a block that opens

> **How the exam phrases it.** / **Come lo chiede l'esame.**

Its subject IS the Ministry's wording. It teaches that an obligation forbids
every alternative, that a warning sign permits and forbids nothing by itself,
that "the sign permits X" is true unless the sign's own rule reaches X, and
that a right-of-way statement describing two things at once is a scenario, not
a contradiction. That lesson cannot be taught without naming what is being
read. Topic 05's block said "How the exam words these", which was the same
device under a second name; it was normalized so the exemption can be one
literal string.

**The other 52 were cleared.** They fell into three kinds:

- **Narration**, which said nothing the learner could use: "The exam trap:
  these yellow ones are not used on a two-way road", "The exam draws the same
  junction both ways", "the exam trades on the difference". Deleting the
  frame leaves the fact standing, and the fact was always the point.
- **Attribution of a term** to the exam, which is simply wrong: "The exam
  calls these channelizing lanes" became "These are called channelizing
  lanes". The Code names them, not the exam.
- **Mentions carrying a fact**, which is the kind worth care. Topic 09's
  "the exam's numbers below are the one-second (reaction) values, not the
  much larger total-stopping figures" tells the learner WHICH convention our
  table follows, and that has to survive. It became "the numbers below are
  the one-second values", and the For-US-drivers note beside it, which
  contrasted "for the exam" with "on the actual road", now contrasts the
  legal minimum with the larger American habit. Same contrast, no exam.

Three headings named the exam and were renamed, so `review_anchors.json` was
updated with them: topic 09's "The quiz's numbers", topic 21's "The numbers
the quiz asks", topic 22's "B and trailers (a common exam point)".

**The checker now matches the noun, not a list of verbs**, because a verb list
is a losing game: each new offender was a new verb. English bans *the exam*,
*the exam's*, *the exams*, the attributive uses (*exam figures*, *exam bank*,
*exam claims*) and *quiz* outright; it also bans *the bank tests / marks /
uses*, which is the same defect with the source renamed. Italian keeps the
word *esame*, because topic 22 needs it in its real sense, the test you sit
for a license: *esame di guida*, *esame di teoria e di pratica*, *la CE
richiede il suo esame*. What Italian bans is the elided article, *l'esame*,
*d'esame*, *all'esame*, *dell'esame*, which is the form every narrator
sentence was written in. The two senses separate cleanly on the article.

The exemption is keyed to the fixed opening string, not to a topic number or a
heading level, so it cannot spread quietly: any other block naming the exam
still fails, and the other families still apply inside the exempt block.

### 49. No ladder: name the category, not the picture of one (2026-09-16)

The maintainer read "The license ladder (category, age, what it drives)" in
topic 22 and said the word was too informal for a reference text. It is, and it
is also the figure rule 41 already bans one step further on: `limit ladder`,
`scala dei limiti` and `rung of tens` were caught in topic 11 long ago, and the
licence topic simply kept a copy the patterns did not reach.

Six places carried it, and the formal word was available in every one:

| was | is |
|---|---|
| The license **ladder** (category, age, what it drives) | **License categories: minimum age and what each permits** |
| each category **on the ladder** includes the ones below | each **category** includes the ones below |
| which cap belongs to which **rung** | which **limit** belongs to which **category** |
| it transfers **down the ladder, never up** | it **extends to the lower categories, never to the higher ones** |
| Learn the **ladder** and the exceptions list | Learn the **table of limits** and the exceptions list |
| rain pushes the top two **rungs** down one step | rain **lowers the two highest limits** |

The tell is worth naming, because it is how the figure got in: a ladder was a
genuinely useful thing for the AUTHOR to picture while arranging the material,
and it then leaked into the page as if it were the subject. The reader does not
need the author's scaffolding. They need the rule.

Two collateral improvements fell out of the same sentences. "Which **cap**
belongs to which rung" became "which **limit**", since the notes say *limite*
throughout and *cap* was a second name for it (rule 6's terminology test).
And the Italian "Trainare a **scala di camion**" became "Trainare un rimorchio
di quelle dimensioni", which was the same figure hiding in the other language.

Five patterns now guard it. `rung` is matched on its own, since it has no
literal use anywhere in this corpus. `gradino` deliberately is NOT: topic 07
uses it for the physical step at the edge of the roadway, which is the real
word for a real thing, and banning it would fire on correct Italian.

Renaming the heading moved 12 entries in `review_anchors.json`, the usual
consequence of rule 13's map: a heading is an address, so changing it is a
data change and not only a wording one.
### 50. Define a category before you lean on it (2026-09-16)

The maintainer read the AM bullet in topic 22 and said: "you use A1 in a
sentence, and then you don't define it until later." He was right, and the
ordering was not incidental. The bullet answering 24486 (three years of AM
does not grant motorcycles up to 11 kW) sat between **AM** and **A1**,
so it named A1, quoted A1's power limit and asserted A1's exams one bullet
BEFORE the line that says what A1 is. A learner meeting these categories for
the first time had to hold an undefined token for the length of a sentence.

**The fix was to move it, not to reword it.** Its complement was already in
the right place: "A1 covers everything AM covers, because each category
includes the ones below it." The two are one idea in two directions, so
inclusion runs downward and seniority does not run upward, and they now sit
next to each other after A1 exists. Moving a bullet moves its claim marker
with it, which is the point of keeping the claim beside the paragraph.

**A mechanical check is cheap and worth re-running when a topic's structure
changes.** For each category token, find the bullet that DEFINES it (`- **A1
(16).**`) and its first use outside a heading, and report any use that comes
first. Headings are excluded on purpose: `### Two and three wheels: AM to A`
announces the scope of what follows and is not a forward reference. The run
that found A1 also found BE used in the C and D section, six lines before the
"B and trailers" section defines it.

**A signposted forward reference is allowed, a silent one is not.** BE stays
where it is, because the sentence needs it to contrast CE with BE, but it now
reads "CE also covers **BE**, the car-and-trailer category set out below",
which tells the reader the definition is coming rather than assuming they have
it. That distinction is the rule: name where it is defined, or define it here.
No checker can tell the two apart, so this one is judgment, like rule 13.
### 51. Organize by the category, not by the shape of the vehicle (2026-09-16)

The maintainer read the motorcycle section of topic 22 and made two points:
the material was badly organized, and "if A includes quadricycles why are you
organizing around 2 and 3 wheels?" Both were right, and the second explains
the first.

**The heading was falsified by its own first bullet.** `### Two and three
wheels: AM to A` promised a group defined by wheel count, and then the very
first entry said AM covers **light quadricycles**, which have four. Wheel count
is not what the law groups by. AM, A1, A2 and A are a progression by minimum
age and engine power, and what each covers is a consequence, not the
organizing idea. The heading is now `### Mopeds and motorcycles: the AM, A1,
A2 and A categories`, and the quadricycle is named as the exception it is:
"the one four-wheeled vehicle in this group". Naming an exception is teaching;
hiding it under a heading that denies it is not. (`### Four wheels: B1 and B`
stays, because there it is true: B1 is heavy quadricycles and B is cars.)

**The disorder had three separate causes**, worth separating because each has
its own fix:

1. *A general rule stated as a property of one category.* "A1 covers
   everything AM covers, because each category includes the ones below it"
   made the inclusion rule look like an A1 fact, and A2's bullet then had to
   repeat it ("A2 includes A1"). The rule now opens the section, once, where
   it governs all four, and both restatements are gone.
2. *One fact said three times.* The A1 bullet said displacement is one of
   three limits, a second bullet said A1 is the category defined by a
   displacement limit, and the closing paragraph said it again. Only the
   closing paragraph added anything, namely WHY: displacement is fixed by the
   engine's design, power can be altered. The two bullets went; the reason
   stayed. ("Cast into the metal" was itself corrected on 2026-09-16, see
   rule 52.)
3. *Bundled bullets.* AM carried four unrelated rules in one bullet, against
   rule 40. Split into three.

**Restructuring a section is the moment to check its claims**, because moving
blocks moves promises. Three of the claims here were wrong, all of them
transpositions that no build check can catch, since a claim only has to name a
statement that exists:

| claim | sat on | decides |
|---|---|---|
| 18559 tricycles need a license | the A1 **passenger** bullet | the tricycle bullet |
| 18592 A covers all agricultural machines | the **B** car bullet | A1's agricultural-machines bullet |
| 24498 passenger need not be an adult | nothing at all | the passenger bullet, which was written for it |

18559 and 24498 had been swapped outright. A wrong claim is worse than no
claim: an unclaimed statement falls back to the picker, which abstains when it
is unsure, while a wrong claim confidently opens the notes at a paragraph
about something else.

One weak claim is left deliberately: **18729** (a driver must respect and
cooperate with officers) sits on the vehicle-documents paragraph, whose last
sentence is "You must show your documents to officers … on request." That is
the cooperation duty in its concrete form, so it is defensible rather than
wrong, but the topic-22 claims pass should decide whether it belongs in topic
15 with the officers' signals instead.

A bold run straight after a colon counts as a sentence-opening label in
`check_review_bullets.py`, so "within **three limits at once**: **125 cm³** …"
tripped the rule-40 ratchet. Introducing each figure by name instead
("displacement up to **125 cm³**") reads better anyway.

### 52. A vivid image is not a fact (2026-09-16)

"Displacement is **cast into the metal** and cannot be altered" was the line
that explained why the law puts A1's limit on displacement rather than on
power. The maintainer replaced it with "Displacement is part of the vehicle's
design and is fixed and unalterable, and no owner can change it."

The image was not merely informal, it was wrong. Displacement is bore times
stroke times the number of cylinders, a consequence of how the engine was
designed. Nothing about it is cast into anything, and a reader who pictured a
number stamped on a casting would have learned something false about why the
limit holds. The correct reason is simpler and no longer: the figure follows
from the engine's design, so changing it means changing the engine.

This is the same defect rule 41 bans, arriving from a direction the checker
cannot see. The patterns there catch figures that stand in for a RULE, such as
a category that owns or a limit that bites. This one stood in for a
FACT, and it read as technical rather than as decoration, which is exactly why
it survived several passes over this paragraph. When a sentence explains why a
rule is shaped as it is, the explanation has to be true in its own right, not
merely evocative of the truth.

Fixing it exposed a second problem in the same sentences. The closing paragraph
on which limit belongs to which category restated the introduction's reasoning
almost word for word. It now APPLIES the two properties instead: A1's limit
needs nothing to defend it, while A2's needs the no-detuning rule beside it.
A paragraph that repeats its own section's opening is not a summary, it is
the same paragraph twice.

### 53. Every sentence stands on what the review has already said (2026-09-16)

The maintainer read the new opening of topic 22 and said: "you start that
paragraph with 'How the limits are written', but I immediately don't know what
is being limited until I read a few more sentences after that. That is bad
pedagogy. Each sentence should make sense, and only be based on prior content
in the topic review."

That is the rule, and it is stricter than it first sounds. A label is a
promise that the reader can already parse it. "How the limits are written"
could only be parsed by someone who knew that a licence category is DEFINED by
limits, which the review had not yet said. The reader had to hold the phrase
unresolved for three sentences and then retrofit a meaning onto it, which is
work that teaches nothing.

**The fix is upstream, not in the label.** Renaming it alone would have moved
the problem rather than solved it, so the section now opens by saying what a
category is: it names the vehicles it allows, it sets a minimum age, and for
mopeds and motorcycles it fixes how large or how powerful the engine may be.
Only after that does "How engine limits are written" refer to anything.

The same pass found three more, all of the same shape:

| was | why it failed | is |
|---|---|---|
| **Containment: a category carries the ones below it.** | "below" needs an order the reader has not met | **A license category also permits whatever a narrower category permits.** |
| …so A covers A2, A1 and AM, and B covers B1 and AM. | six category names, none of them yet defined | …the larger license always includes the smaller, and every license allows what the smallest of them, AM, allows |
| **Direct access and graduated access.** | both terms are defined in the sentence AFTER the label that uses them | **How a category is obtained.** |

The general form is worth naming, because it is easy to write and invisible to
every checker in this repo: a label or an example that would be clear to the
AUTHOR, who holds the whole topic in mind, and opaque to the reader, who is
one sentence in. Reading a section back in order, asking of each sentence
"could someone who has read only the sentences above this one parse it", is
the only test that finds it.

A forward reference is still allowed when it is SIGNPOSTED, as rule 50 records
for BE. The difference is whether the reader is told the definition is coming
or left to assume they have missed it.

**The first replacement was itself wrong, which is worth recording.** "A
category also allows what the smaller ones allow" fixed the ordering problem
and introduced two more. It said "category" where the subject is a **license
category**, and the reader one sentence in has no reason to supply the missing
word. And it called a license *smaller*, which is meaningless: a license has
no size. What varies between categories is the RANGE OF VEHICLES each one
permits, so the comparative belongs to that range and not to the document. The
line now reads "A license category also permits whatever a **narrower**
category permits", which says the same thing about the right noun.

The general lesson is that a comparative is a claim about a dimension, and the
dimension has to be real and named. *Larger*, *higher* and *smaller* all felt
natural here because the author was picturing a ladder of entitlements, which
is the author's mental model and not a property of any licence. Ask what
physical or defined quantity the comparative measures. If the answer is "the
shape I have in my head", rewrite it against the thing that actually differs.
### 54. They are all categories, not subcategories (2026-09-16)

The maintainer asked whether "A license category also permits whatever a
**subcategory** permits" would be correct in place of "a narrower category".
It would not, and the sources agree without exception.

**The Code defines them all as categories.** Art. 116 comma 3 opens "La
patente di guida, conforme al modello UE, si distingue nelle seguenti
**categorie**" and then lists them as lettered items: a) AM, b) A1, c) A2,
d) A, e) B1, f) B, and so on through BE, C1, C, D1, D and the E forms. Art.
115, which sets the minimum ages, says "categoria" every single time. The word
*sottocategoria* survives in exactly **two** places in the whole Code, both in
provisions about medical checks and exams, used as shorthand for the
numeral-suffixed variants in phrases such as "patenti di categoria A, B, BE e
sottocategorie". It is residual drafting, not the defining vocabulary.

**The Ministry's bank never uses it.** 118 statements say *categoria* and
**zero** say *sottocategoria*. The SIDA manual does not use it either. A word
the exam never prints is a word the notes should not teach.

**And it would be wrong about the relation even if the word were current.**
Containment is not "a category contains its subcategories". Every license
category permits what AM permits, and AM is nobody's subcategory. B permits
A1's vehicles within Italy, and A1 is not a subcategory of B. Reading the rule
as being about subcategories would make both of those look like exceptions
when they are ordinary instances.

The deeper trap is the one rule 53 named. *Subcategory* describes a
relationship between NAMES, and containment is a relationship between
PERMISSIONS. A1 and A share a letter, which makes the name relationship
tempting, but the letter is not what makes A permit what A1 permits. The
conversational use is harmless (the maintainer and I both said "subcategories
of A" while discussing the topic) and it must not reach the page.

Kept: "A license category also permits whatever a **narrower** category
permits."
### 55. When a figure earns its place, and what rule 13 is actually for (2026-09-16)

After the containment diagram the maintainer asked which other figures from
the SIDA manual would help. The answer took measuring rather than taste, so
the method is worth keeping.

**The manual's conceptual figures** (as opposed to its photographs of signs
and vehicles) cluster in six places: the containment principle, the
stopping-distance family, grip and its coefficients, the points system,
licence validity by age, and field of view. Counting the bank against each one
sorted them cleanly:

| candidate | statements | built? |
|---|---|---|
| the three stopping distances | 36 | yes: additive, and our own prose says mixing them up is the commonest mistake |
| the points scale | 38 in topic 22 | yes: 20 is both a start and a ceiling, which a bullet list cannot show |
| braking distance against speed | 3 tested | yes: 1:4:9 is visceral as bars and invisible as words |
| licence validity by age | 9 | no: four bullets already do it, a figure adds nothing |
| field of view | 3 | no; a first regex said 84 by sweeping in every alcohol and fatigue statement |
| grip factors | 31 | no: a list of causes, not a relation, so a figure would be decoration |

**The test that emerged: a figure earns its place when the content is a
RELATION, not a list.** Containment is a relation. Reaction plus braking
equals total is a relation. Which licence a combination mass needs is a
relation. The factors that reduce grip are a list, and a list in a picture is
just a list with a border. Statement count decides whether the relation is
worth the space; the shape of the content decides whether a figure can help at
all.

One figure was built that the manual does NOT have, and it is the one most
likely to save a learner marks: a number line of **combination mass**, banded
B to 3.5 t, B96 to 4,250 kg, BE beyond, because several statements hand you a
car mass and a trailer mass and ask which licence you need. Reading the Code
to draw it corrected the review as well, since art. 116 comma 3 makes the
code-96 test the consequence of the combination passing 3,500 kg rather than a
separate allowance.

**Two drafting rules, both learned by rendering and looking:**

1. *Draw it, then look at it.* Every one of the five figures shipped with a
   defect invisible in the markup: English captions in a file both languages
   share, spacing that collapsed because SVG ignores runs of spaces, an
   unfilled shape that vanished against a grey road with the lane dashes
   showing through it, a label colliding with an axis, and a three-wheel
   pictogram that came out as a stray "3" and three dots.
2. *One figure, one idea.* The points figure first carried the 20-point start,
   the doubling for new drivers, the 15-point cap and the recovery course, and
   collided with itself. The cap and the doubling went back to the prose,
   where a bullet states each perfectly, and the figure kept only what prose
   cannot show.

**Rule 13 had to be narrowed, and the reason is the rule's own point.** It
reports a rule bullet that sits away from the picture of its subject, and
topics 09 and 22 had been SKIPPED by it for having no images at all. Adding
concept figures made them eligible and produced five defects, every one a
false positive. A sign is an OBJECT: one meaning, one place, and a reader who
meets its picture should find everything about it there. A concept is not an
object, and the stopping distances and the points scale are discussed across a
whole topic precisely because that is what makes them concepts. So rule 13 now
counts only `domandeb_images/` pictures and ignores `review_media/` diagrams,
through one `is_sign_image` helper that all three of its image tests share.
### 56. The alt text IS the caption, so write it to teach (2026-09-16)

The maintainer sent a screenshot of the new containment figure with two
comments: the image could be larger, and the caption "it worthless". He was
right, and the reason is worth recording because it is not obvious from the
markdown.

**The app renders a figure's alt text as a visible `<figcaption>.**
`reviewMd` in app.js builds `<figure>` with both an `alt` attribute and a
`<figcaption>` from the same string. So alt is doing two jobs at once, and
writing it for the job it usually has, describing the picture for someone who
cannot see it, makes the visible caption a description of what the reader is
already looking at:

> Two groups of nested boxes: AM inside A1, inside A2, inside A; and AM inside
> B1, inside B, inside B96, inside BE, with dashed A1 and A boxes drawn inside B

Every word of that is true and none of it teaches. It is longer than the
paragraph it sits above and it names the geometry rather than the rule.

**The rule: a figure's alt text states what the figure MEANS, in one line.**
The five figures now read "Each license category permits whatever is drawn
inside it", "Reaction distance plus braking distance is the total stopping
distance", "Braking distance follows the square of the speed, so three times
the speed is nine times the distance", "The mass of the whole combination
decides the license: B, then B96, then BE", and "A license starts at 20 points,
and deductions run down toward 0". Each works as a caption, and each is better
alt text as well, since a relation is what a blind reader needs and a list of
rectangles is not.

The geometry has not been lost. It lives in the SVG's own `<title>`, and the
full relation is in the prose paragraph beside each figure, which a screen
reader reads anyway. That is the ordinary way to handle a figure whose content
the surrounding text already describes.

**Writing the caption exposed redundancy underneath it.** Each figure's
paragraph opened by restating what the caption now says, so "Each box permits
everything drawn inside it", "The two parts add up" and "The axis is the mass
of the whole combination" all went, leaving each paragraph to add only what the
picture cannot: why AM appears twice, what dashed means, which quantity the
question hands you.

**Size: use the `!xl` hint.** A concept diagram is not a sign, and the
standalone default is tuned for signs. `![!xl caption](path)` moves the
containment figure from 190x118 to 431x268 (`REVIEW_FIG_CFG.xl` in app.js).
All five concept figures carry it. The hint already existed for dense sign
boards, and a diagram whose whole value is being readable at a glance has the
same need.

**The audit the maintainer asked for, and the guard that came out of it.** The
two older figures had both faults:

| figure | was | is |
|---|---|---|
| `green-wave.svg` | 303x94, and the caption ended by describing the animation ("the light turns yellow then red behind it") | `!xl` at 480x149, caption "At the advised speed the car meets every light on green" |
| `disco-orario.svg` | 125x170, with the dial numerals about six pixels tall | `!big` at 174x238, caption "The dial shows your arrival time, and the disc goes on the dashboard" |

The green wave was the worse of the two, because its traffic-light COLORS are
the whole content of the animation and at 303 px they were dark specks.

Since a `review_media/` figure left at the sign-sized default is a defect by
construction rather than by taste, `check_review_placement.py` now enforces
the hint as **rule 6** and prints the two choices. Verified by removing a hint
and watching it fail. All seven of our diagrams now declare a size, and the
audit table above lives in the commit message rather than in code, since the
numbers move whenever `REVIEW_FIG_CFG` is retuned.
### 57. A caption explains the figure's DEVICES, not its shapes (2026-09-16)

The maintainer read the shortened captions and raised the bar again: "Any
figure with a caption should be fairly clear what the figure is showing and
explaining", so a reader should not have to work through the prose above and
below to decode the picture.

That sounds like a reversal of rule 56, which cut a caption for describing the
picture. It is not, and the distinction is the useful part.

**Rule 56 banned an inventory of SHAPES.** "Two groups of nested boxes: AM
inside A1, inside A2, inside A…" tells the reader what their own eyes already
report, and costs a line for nothing.

**Rule 57 requires the DEVICES.** A figure has a small grammar of its own: a
dashed border, a shape drawn twice, bars in true scale, an arrow that stops
against a bar, what the axis measures. Those are not visible facts, they are
CONVENTIONS, and a reader who does not know them cannot read the figure at all.
Every one belongs in the caption.

Measured against that bar, the five captions written under rule 56 were each
missing a device:

| figure | device left unexplained |
|---|---|
| containment | the dashed boxes, which mean "within Italy only" |
| stopping distance | the car drawn twice, at perception and at rest |
| braking squared | that the bars are in true scale, which is the whole argument |
| trailer mass | what the axis measures, and where the thresholds fall |
| points | the red block at 0, the arrow stopping at 20, the dashed stretch |

Green-wave is the instructive one. Rule 56 cut "and the light turns yellow
then red behind it" as animation description. That was wrong: it is the
behavior the animation exists to show, and without it a reader wonders why the
lights change at all. It is back, as "each light turns yellow then red only
once the car is past it". The test is not whether a clause describes something
visible, it is whether the reader can decode the figure without it.

**A complete caption makes its paragraph redundant, so the paragraph goes.**
Under the braking and the points figures the prose said only what the caption
now says, and both were deleted. The trailer paragraph lost two of three
sentences and kept the 750 kg case, which the axis cannot show. What must NOT
be deleted is a paragraph carrying a claim, since a caption is alt text and
cannot hold one: the containment paragraph stays for exactly that reason, and
it earns its place anyway by naming the two Italy-only reaches the caption
only gestures at.

One mechanical trap: deleting a paragraph that sat between a bullet and a
figure swallows the blank line that separated them, and an image line directly
after a bullet does not parse as a figure row. Check the blank lines after any
such deletion.
### 58. A rule needs the situation it exists for (2026-09-16)

The maintainer read the A2 paragraph and said of the last sentence, "i do not
understand". It was this:

> The **no-detuning rule** completes it, since the machine may not be a
> restricted version of a model producing more than **double** that power,
> over 70 kW, and manufacturers do sell detuned versions of large motorcycles.

Five faults in one sentence, and they are worth separating because each has its
own lesson:

1. **"completes it" is empty.** Completes what? The definition, but the reader
   has to reach for the referent.
2. **"that power" points two clauses back.** The 35 kW it means was in the
   previous sentence. A pronoun that far from its noun is a puzzle.
3. **"over 70 kW" arrived as a bare apposition**, with nothing saying it is
   double of 35. A number the reader cannot derive is a number to memorize,
   which is the opposite of what the sentence was for.
4. **The rationale was appended with "and".** "manufacturers do sell detuned
   versions of large motorcycles" is the REASON the rule exists, and grammar
   put it last and coordinated, so it read as an unrelated aside.
5. **The tested number was buried.** 24500 (VERO) and 24507 (FALSO) are the
   same sentence twice with two swaps: 35 kW against 25, and **double** against
   triple. The multiplier is the point, and it sat mid-clause.

The general lesson is fault 4 generalized. **A rule is not understandable
without the situation it exists for, and the situation belongs FIRST.** The
reader cannot evaluate "may not be a restricted version of a model producing
more than double" until they know that manufacturers restrict big motorcycles
on purpose to sell them into A2. Lead with what someone is trying to do, then
state the rule that governs it.

It now reads:

> One more condition, the **no-detuning rule**, stops a large motorcycle from
> being restricted down into A2: such a bike qualifies only if the model it
> derives from makes no more than **double** the limit, which is **70 kW**.
> The multiplier is two, and a statement that says three is false.

The situation comes first ("stops a large motorcycle from being restricted down
into A2"), the rule follows the colon, 70 kW is derived rather than asserted,
and the tested swap gets its own sentence. The paragraph already claimed 24500
and 24507; the difference is that it now decides them.
### 59. A fact's home is the thing, not the statement that tests it (2026-09-16)

Asked why the special license was defined in the validity section, the honest
answer is that the flag which prompted it (24686) is a validity statement, so
the definition landed where the statement lives. That is backwards, and it is
the same fault as rule 53's in a different dress.

**Split by what the sentence is about, not by which statement asked for it.**
What a licence IS belongs with the categories, next to the B it is a variant
of. How long it LASTS belongs in the validity section. So the categories
section now says the special license is not another category but one of the
ordinary ones issued to a driver with a physical disability, valid only for a
vehicle with the characteristics written on the licence itself (art. 116 comma
3 lett. g, and the fine in comma 4 for driving anything else). The validity
section keeps one line, five years up to 70, and keeps the claim, because
24686 is a validity statement and that bullet is what decides it.

Writing it there also improved the content. The first version said the licence
is issued "when the medical assessment requires an adapted vehicle", which is
the practical effect rather than the rule; the Code ties it to the holder and
restricts it to the vehicle described on the document, which is why driving a
different vehicle is itself an offence.

The batch instructions have said this all along, that a correction goes where
the reader FIRST meets the thing. The pull the other way is real, though,
because a flag arrives attached to a statement and the statement has a
section. Note which of the two the sentence is really about before placing it.

### 60. One bullet may not hold two rules with OPPOSITE answers (2026-09-20)

Topic 04 had a single bullet headed **"Tow-away is *not* automatic"**, which
covered both parking signs at once: the plain no-parking sign, where removal
needs a ZONA RIMOZIONE panel, and the no-stopping sign, where removal is always
ordered. Both statements were claimed onto it, 19907 (FALSO) and 19950 (VERO).

The reviewer opened 19950's 📖, landed on that bullet, read the heading and its
closing sentence ("'Always subject to tow-away' under the bare no-parking sign
is **false**") and concluded the statement was false. It is true. Nothing was
factually wrong in the bullet: the clause "or under the **no-stopping** sign"
was there and correct. The bullet simply argues one way and the statement went
the other, and a learner reads the emphasis, not the subordinate clause.

This is the sharpest form of rule 40. A bullet bundling related rules is
merely weak; a bullet bundling rules whose ANSWERS differ is actively
misleading to whichever statement sits on the minority side, and the claim
machinery cannot see it, because a claim only records which block a statement
belongs to and never what the block concludes.

The fix was to move the positive rule to the sign's own introduction, under its
own picture, where the reader first meets it: the no-stopping bullet now ends
"A vehicle left where this sign stands is **always** towed, which the plain
no-parking sign does not do on its own", and 19950 is claimed there. The
no-parking bullet keeps 19907 and its own emphasis.

**Check for this whenever one bullet carries claims with both answers.** The
VERO/FALSO split that `validate_data.py` prints is per topic, not per block, so
it will not show you this. Read the bullet's heading and last sentence as a
learner would, and ask whether a VERO statement claimed there could survive
them.

### 61. Parking spaces, not bays or stalls; pull-off, not lay-by (2026-09-26)

Flags 23724 and 23725: the maintainer wrote that American English does not use
*stall* for *le apposite strisce*, and that the phrase means a **marked parking
spot**. *Bay* is the same fault from the other side, British. A sweep of the
translations, the explanations, topics 01, 07, 12 and 16, the Glossario and
the Reference page replaced both: an *appositi spazi (stalli)* is a **marked
parking spot** or **parking space**, the color of a *stallo* is the color of
a **parking space**, and a *piazzola* is a **pull-off area** beside the
carriageway, never a *bay* and never a *lay-by* (topic 16's US-drivers note
had *lay-by* in the very sentence written to explain the word to an
American). A bus stop indentation is a **bus stop pull-out**. The vocabulary
entry `apposite strisce` was added with that gloss, and `strisce di
parcheggio` is now *parking space lines*. *Rubbish* went the same way in
23774 (*trash containers*). The `reader` family of `check_review_english.py`
does not list these words, because *bay* has other senses in the corpus;
they are on the writer.

### 62. A true rule with a clause that spoils it: say so in the explanation (2026-09-26)

Flags 23773 and 23774 ("a classic trick question with a true statement
invalidated by a clause... Be sure to alert the learner to this pattern in the
explanation of every question where it occurs"). The recurring shape in topic
12 is a real *sosta* ban with *ed anche la fermata* or *così come la fermata*
added, which turns it FALSO. 23773, 23774 and 20787 now end with one fixed
sentence pair: *Read the whole sentence: the ban on sosta is real, and the
clause adding the fermata is what makes the statement false.* / *Leggi tutta
la frase: il divieto di sosta è vero, ed è la clausola che aggiunge la
fermata a rendere falsa l'affermazione.* **The same day the maintainer asked for the whole bank to be read for
this shape**, and it was: eight readers over all 3,564 live FALSO statements,
rubric in `docs/clause-trap/RUBRIC.md`, four shapes (an extension, an
absolutizer, a false condition or exception, a false restriction or reason),
decisions in `docs/clause-trap/decisions.json`. **240 qualify** (102 false
restrictions, 67 false conditions, 47 absolutizers, 24 extensions), heaviest
in the prohibition signs (29), fermata and sosta (23), licences (17), and the
precedence and road-marking topics (16 each). Each carries
`clause: {text, kind}` in `questions.json` and its two explanations end with
one fixed pair: *Read the whole sentence: strike «clause» and what is left is
true; the added words are what make the statement false.* / *Leggi tutta la
frase: togli «clause» e ciò che resta è vero; sono le parole aggiunte a
rendere falsa l'affermazione.* `validate_data.py` checks the clause is
verbatim in the statement, the statement is FALSO, and both sentences are
present. The readers' own uncertain cases are recorded in the session of
2026-09-26; the rule they settled on is that a narrowing word (*solo*) on a
true claim counts, a swapped condition or subject does not, and a statement
false for two reasons does not. To add one, set the field and append the
pair. The clause is never marked visually in the app, at any level
(maintainer, 2026-09-26): the explanation sentence is the whole warning.
