# Cross-checking the app against the SIDA manual

Working plan for using the autoscuola's textbook, *Manuale della patente A e B*
(SIDA / AutoSoft Multimedia, 276 pages, "aggiornato con il Listato Ministeriale
ufficiale"), to improve the app's content. Work through the items one at a
time; update the status columns as we go. Delete this file when the pass is
complete.

## Status and what remains (updated 2026-09-04)

The topic-by-topic accuracy pass (workstream 2) is complete for all 25
topics, v20260904m through v20260905k. Eight corrections and a large body
of bank-backed additions went into the reviews; the per-topic notes at the
end of this file list each with its bank statement numbers. The Ministry
bank was the ground truth throughout and was never edited.

### Remaining suggestions, in suggested order

1. **Verify two parked figures against the current Code** (cheap, and the
   only open accuracy questions):
   - "-8 points" for failing to yield to pedestrians (manual, topic 03;
     bank 19160 does not quantify). Add the figure only if confirmed.
   - The 2021 autostrada rule for motorcycles of 120 cm3 / 6 kW with an
     adult rider (manual, topic 16). The bank still tests 150 cm3 (18449),
     so the review keeps 150; decide whether to mention the newer rule as
     a note.
2. **Ask the instructor how the exam sheet is composed by topic**
   (workstream 1). Record the answer here and adjust `SAFETY_TOPICS` in
   app.js if it differs from the current 25 x 1 + 5 safety draw.
3. ~~Ambiguous statements (`warn` / `warn_it`)~~ Done 2026-09-04
   (v20260905l): only 20697 carried a badge; the manual's "senso unico
   alternato" versus "doppio senso" vocabulary, together with sibling
   20696, settled it. Explanation strengthened, badge dropped, glossary
   note appended under rule 18. The list is now empty.
4. **Thin explanations** (workstream 3): use the manual's rule as the
   source for a real WHY, in our words. Start with the topics whose notes
   below mention many trap statements (04, 13, 20, 23).
5. **Trap vocabulary** (workstream 3): the manual's bold keywords against
   `vocabulary.json`; add missing glosses (translation only, rule 14).
6. **Images** (workstream 4): the only wish recorded during the pass is an
   SVG of the whole level-crossing approach (triangle, three countdown
   panels, cross) for topic 03; 4071.jpeg already shows the panels, so
   this is optional. Search Wikimedia Commons before drawing.
7. **Process facts** (workstream 5): check manual 20.7 "Candidati alla
   patente" (p. 214) against the How-to section on getting a license.
8. **Regenerative braking note** (topic 20, optional): the review now says
   brakes turn kinetic energy into heat (25306, VERO). Electric and hybrid
   cars recover part of that energy through the motor before the friction
   brakes act; a one-clause note would be consistent with 25075 and the
   manual's remark on hybrids.

When items 1 to 7 are done, delete this file or move the per-topic notes
into `docs/review-glossary.md`.

## The resource

- `private/Manuale-reduced.pdf`: the OCR'd scan (Italian text layer, ~53 MB).
- `private/Manuale-text.txt`: the extracted text, one `===== PAGE N =====`
  marker per PDF page (PDF page = printed page + 10). Body text is clean;
  small-print margin notes and the picture-heavy sign pages are noisier.
  Render a page as an image when the text is doubtful
  (`pdftoppm -r 110 -f N -l N -png Manuale-reduced.pdf out`).
- `private/Manuale.pdf`: the original 820 MB scan, kept only for pulling a
  page image at full resolution when an illustration is worth studying.
- The whole `private/` folder is gitignored and never leaves this machine.

Why it is authoritative for us: it is written to the same Ministry listing our
bank comes from, organizes the official statements by rule, and prints in bold
the keywords that recur in the TRUE statements. Where a topic review and the
manual disagree, the manual is the tiebreaker (after checking the current law
where a figure may have changed since printing).

## Rules

1. **No copied wording.** The manual is copyrighted. Use it to verify facts and
   to see which reading the examiners intend; write our own sentences, in the
   style of `docs/review-glossary.md`.
2. **No copied images.** Its illustrations are AutoSoft's artwork. When one of
   them would make a review clearer, find an equivalent on Wikimedia Commons
   (sign designs are public domain as acts of the Italian State; vectorizations
   may be CC BY-SA), and record it in `IMAGE-CREDITS.md` as usual. If nothing
   suitable exists, draw our own (as with the Green Wave SVG) or do without.
3. **Reviews and explanations change through the normal workflows** in
   `CLAUDE.md`: edit `topic_reviews_md/*.md`, rebuild, validate, bump both
   version markers; explanations only in `english_translation` /
   `explanation` / `explanation_it`; never `italian_text` or `answer`.
4. **Report before editing.** For each topic, produce the discrepancy list
   first (section 3 below) and get it approved; then apply.

## Workstreams

### 1. Mock-exam weighting

The preface states that the Ministry marks some topics as more relevant to
safety and draws **two** questions from each of those per 30-question sheet,
**one** from the others. The sommario shades the relevant sections:

| Manual section (shaded) | Our topic |
|---|---|
| 3.1 Segnali di prescrizione: precedenza | 05 Segnali di precedenza |
| 11.5 Specchi retrovisori; 11.6 Dispositivi obbligatori; 11.7 Sicurezza passiva (cinture, airbag, seggiolini) | 19 Dispositivi di equipaggiamento |
| 12.2 Arresto del veicolo; 16.1 Arresto, fermata e sosta | 12 Fermata, sosta, arresto e partenza |
| 13.1–13.3 Posizione sulla carreggiata, cambio di direzione, altre norme | 13 Norme sulla circolazione |
| 17.1 Carico, trasporto di persone e traino; 17.2 Autostrade | 21 Ingombro della carreggiata … |
| 18.1 Cautele di guida | 17 / 18 (conduct topics) |
| 19.1–19.5 Cause di incidenti, stato psicofisico, cosa fare, primo soccorso | 18 Comportamenti per prevenire incidenti … (19.2 → 17) |

What the official sources say (checked 2026-09-03):

- DM 27 ottobre 2021 (GU n. 292, 9-12-2021), arts. 1–2: the sheet is drawn
  from the Ministry database "secondo un metodo di casualità", 30 statements,
  20 minutes, at most 3 errors. No per-topic distribution is stated.
- Circolare prot. 38460 of 14-12-2021 (applicability from 20-12-2021 per
  decreto dirigenziale n. 439 of 13-12-2021): confirms the random draw and
  that the database is unchanged; again no distribution.
- The pre-2021 scheme (40 questions) was documented as 15 safety topics × 2
  + 10 topics × 1. The manual's shading (seven or so of our topics) looks
  inherited from that era rather than from a published 30-question scheme.
- Third-party quiz sites describe the 30-question sheet as "one per topic
  plus five more", but none cites an official act; the distribution lives in
  the Motorizzazione's exam software, not in a published rule.

Conclusion: there is no official published per-topic scheme for the
30-question sheet. Two ways to pin it down empirically: ask the autoscuola
instructor (their SIDA software mirrors the Ministry's), or read the topic
mix off real sheets (every candidate can download their own scheda from the
Portale dell'Automobilista after the exam; the school's Wednesday
simulations use the same generator).

Independently of that, `startExam()` currently draws 30 statements uniformly
from all 7,147, which over-represents big topics (Segnali di pericolo, 662
statements) against small ones (Limitazione dei consumi, 103). Drawing one
statement per topic plus five extra (from the safety-relevant topics if the
scheme is confirmed, otherwise at random) is closer to the real sheet under
any reading of the sources.

- [ ] Ask the instructor how the sheet is composed by topic; note the answer
      here, and adjust `SAFETY_TOPICS` in app.js if it differs.
- [x] `startExam()` now draws per topic by default (25 topics x 1 + 5 more
      from the safety-relevant topics, `SAFETY_TOPICS` in app.js), with a
      Settings option for a flat random draw over the whole bank
      (`patente_exam_mix`). v20260903t.

### 2. Topic-by-topic accuracy pass on the reviews (complete)

For each of our 25 topics, read the matching chapter against
`topic_reviews_md/NN-*.md` and list: (a) disagreements (numbers, categories,
exceptions, sign meanings), (b) rules the manual covers and the bank tests but
the review omits, (c) passages where the manual's framing would make ours
clearer. Then apply the approved items in both languages.

Order: sign topics and numeric topics first (an error there costs the most),
then conduct, then the rest.

| # | Our topic | Manual chapter(s) | Printed pages | Report | Applied |
|---|---|---|---|---|---|
| 03 | Segnali di pericolo | 2 | 18–32 | 2026-09-04 | v20260904m |
| 05 | Segnali di precedenza | 3 | 33–37 | 2026-09-04 | v20260904n |
| 04 | Segnali di divieto | 4 | 38–51 | 2026-09-04 | v20260904o |
| 02 | Segnali di obbligo | 5 | 52–58 | 2026-09-04 | v20260904p |
| 01 | Segnali di indicazione | 6 | 59–75 | 2026-09-04 | v20260904q |
| 06 | Segnali complementari; temporanei e di cantiere | 7 | 76–83 | 2026-09-04 | v20260904r |
| 08 | Pannelli integrativi | 8 | 84–90 | 2026-09-04 | v20260904s |
| 15 | Segnalazioni semaforiche; agenti | 9 | 91–97 | 2026-09-04 | v20260904t |
| 07 | Segnaletica orizzontale | 10 | 98–107 | 2026-09-04 | v20260904u |
| 11 | Limiti di velocità; pericolo e intralcio | 12.1 | 126–128 | 2026-09-04 | v20260904v |
| 09 | Distanza di sicurezza | 12.2 | 129–132 | 2026-09-04 | v20260904w |
| 22 | Patenti; documenti | 20 | 202–216 | 2026-09-04 | v20260904x |
| 16 | Definizioni stradali; classificazione dei veicoli | 1 | 1–17 | 2026-09-04 | v20260904y |
| 14 | Uso delle luci; dispositivi acustici; spie | 11.1–11.4, 22.2 | 108–115, 234–236 | 2026-09-04 | v20260904z |
| 19 | Dispositivi di equipaggiamento; cinture | 11.5–11.8 | 115–125 | 2026-09-04 | v20260905a |
| 13 | Norme sulla circolazione; posizione | 13 | 133–140 | 2026-09-04 | v20260905b |
| 25 | Esempi di precedenza | 14 | 141–144 | 2026-09-04 | v20260905c |
| 10 | Norme sul sorpasso | 15 | 145–150 | 2026-09-04 | v20260905d |
| 12 | Fermata, sosta, arresto | 16 | 151–157 | 2026-09-04 | v20260905e |
| 21 | Ingombro della carreggiata; veicolo fermo; traino; autostrade | 17 | 158–166 | 2026-09-04 | v20260905f |
| 17 | Guida e condizioni fisiche; alcol | 18, 19.2 | 167–180, 181–183 | 2026-09-04 | v20260905g |
| 18 | Comportamenti per prevenire incidenti; in caso di incidente | 19.1, 19.3–19.5 | 181, 184–197 | 2026-09-04 | v20260905h |
| 23 | Responsabilità; R.C.A. | 19.6 | 198–201 | 2026-09-04 | v20260905i |
| 20 | Elementi costitutivi; manutenzione | 21 | 217–229 | 2026-09-04 | v20260905j |
| 24 | Limitazione dei consumi; inquinamento | 22.1 | 230–233 | 2026-09-04 | v20260905k |

Chapters 23 (Veicoli a due ruote, pp. 237–246) and 24 (Veicoli con rimorchi,
pp. 247–263) cut across several of our topics (16, 19, 20, 21, 22); consult
them when those topics are checked.

Per-topic workflow:

1. `sed -n '/===== PAGE A =====/,/===== PAGE B =====/p' private/Manuale-text.txt`
   with A = printed first page + 10, B = printed last page + 11. Render pages
   where the OCR is poor.
2. Read the review (EN and IT) and the topic's section of `docs/review-glossary.md`.
3. Write the report (a), (b), (c) into this file's topic section below, or in
   chat, and get approval.
4. Apply through the concept-review workflow; run
   `check_review_placement.py`, `validate_data.py`; commit.

### 3. Ambiguous questions and thin explanations

- [ ] For every statement carrying `warn` / `warn_it`, look up the manual's
      treatment of the rule. If it shows a decisive reading, strengthen the
      explanation with that argument and drop the badge (glossary rule on
      defeating ambiguity flags first).
- [ ] For explanations that still merely assert the answer (no WHY), use the
      manual's rule as the source for a proper explanation, in our words.
- [ ] The manual's bold keywords are the exam's own trap vocabulary. Check
      each against `vocabulary.json`; add glosses for any that are
      missing (translation only, ≤ 80 chars, rule 14).

### 4. Images

When a manual illustration would help a review:

- [ ] Note it in the topic's section below (manual page, what it shows).
- [ ] Search Wikimedia Commons for an equivalent (Italian traffic signs are
      well covered under `Category:Road signs in Italy` and
      `Category:Diagrams of road signs of Italy`; road situations less so).
- [ ] Add it under `public_html/domandeb_images/` or the review image folder,
      credit it in `IMAGE-CREDITS.md`, reference it from the review Markdown
      (`![alt](…)`; one image per line renders large).
- [ ] If nothing equivalent exists, draw an SVG of our own or skip.

### 5. Process facts

- [x] Exam format confirmed by the preface: 30 statements, 20 minutes, at most
      3 errors; Italian, with German and French versions.
- [ ] Chapter 20.7 "Candidati alla patente" (p. 214) against the How-to
      section "How you get an Italian license" (attempts, foglio rosa,
      neopatentato limits, validity by age).

## Per-topic notes

The applied notes for all 25 topics, written as the pass ran on 2026-09-04,
were moved into `docs/review-glossary.md` (rule 46) on 2026-09-16, as the
instruction at the top of this file directed. This file now carries only what
is still open.

