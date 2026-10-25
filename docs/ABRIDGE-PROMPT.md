# Abridge tagging prompt (frozen)

This is the fixed prompt for the per-card concept-tagging pass described in
`docs/fable.md`. One LLM call per card. Do not vary the wording between cards or
batches within a build; if the rules change, bump the version and re-run affected
cards.

**Version:** vFinal (2026-06-09) — frozen after the consolidated whole-bank audit
(docs/final-audit.md) surfaced no new rule. Supersedes v1.6 + inline additions:
recall-protection override (4616/4621), its transpose (4658), context-vs-state
(4500). All rulings below are final; any future change requires a version bump
and a re-run of affected cards.

Previous: 1.6 (2026-06-09) — added rules 3b (VERO entailment merging), 4b, and
4c (cross-card consistency, with audit-chain tagging); plus 4b
(FALSO trap families) after the first right-of-way batch; 4b tightened to the
reviewed merge policy after the batch-1 ruling; rule 3c (yield ≠ position) and
the reason-trap safeguard made permanent after batch 2; v1.4: 3d bright line —
reason-traps never merge with each other (ruling on card 4486).
**Input:** the card block produced by `scripts/abridge_validate.py format-card <id>`
**Output:** one JSON object per card, appended to `docs/abridged-audit.json` under `cards.<id>`
**Validation:** `scripts/abridge_validate.py validate` after every batch

---

## PROMPT (verbatim from here to the few-shots, then append the card input)

You are abridging one card from the Italian Patente B theory-exam bank. The card
has one subject (usually a road sign) and a list of true/false statements about it.
Many statements repeat the same idea in different words. Your job is to partition
ALL statements into concept groups and pick one statement to keep per group. The
kept statements form the card's "Quick mode" subset; the rest stay in the database
but are hidden by default.

The Italian text is authoritative. The English translation and explanations are
secondary signals only.

### Rules

1. **Partition completely.** Every statement number appears in exactly one group.
   No statement may be omitted or invented.
2. **Never mix VERO and FALSO in one group.** A true fact and a misconception are
   never the same concept.
3. **VERO groups — merge aggressively.** Statements assert the same concept if a
   learner who knows one knows the others: same fact at different granularity,
   different sentence structure, or different vocabulary all merge ("address and
   phone numbers" / "location and phone numbers" / "some data of" → one group).
   When unsure on the VERO side, merge.
3b. **VERO entailment merging.** A VERO group may also include statements that the
   kept statement logically entails, even when they are not rewordings. Common on
   right-of-way cards: "the vehicles pass in the order H, A, F, L" entails "H passes
   first", "L passes last", "F waits for A", etc. — one group, keep the full-order
   statement. Coverage is preserved because the kept statement teaches everything
   its members teach. The kept statement MUST be the entailing one. VERO only;
   never merge FALSO by entailment of the false claims.
3c. **Yield ≠ position (PERMANENT SAFEGUARD — card 4463).** In this bank, "X deve
   dare la precedenza a Y" is a claim about conflicting trajectories, NOT about
   crossing order: a statement can be FALSO even though Y does pass before X
   (non-conflicting streams), and a vehicle can hold precedence over another yet
   conclude its crossing later (left-turn centre-wait, card 4472). Therefore:
   (a) a VERO yield-claim may merge into a positional order group only when it is
   consistent with the order (answering positionally gives the right answer);
   (b) a VERO yield-claim that is NOT derivable from order (e.g. "E yields to R
   and L" where E also follows A positionally but owes A nothing) stays its own
   group; (c) FALSO yield-form and position-form traps about the same pair ("R
   must yield to A" vs "R passes after A") are SEPARATE traps — never treat the
   phrasing as decoration; (d) engage/conclude distinctions ("impegna" vs
   "conclude l'attraversamento") are likewise distinct concepts.

3d. **Reason traps are always distinct (PERMANENT SAFEGUARD).** A FALSO statement
   whose error lies in the RULE it invokes — "the bus has precedence because it is
   a bus", "left-turners forfeit precedence", "the fastest passes first",
   "straight-goers outrank turners" — is always its own group, even when the
   relation it asserts happens to be positionally true on this card, and never
   merges with positional traps. **Bright line (ruling on card 4486): reason-traps
   never merge with each other either, even when they appear to invoke the same
   wrong rule.** Allowing same-rule merges would force a fresh judgment on every
   card and reintroduce the silent-merge risk this rule exists to kill.

3e. **Panel-reading merges (approved after batch 13, tightly scoped).** On composite
   information panels (urban-junction preavviso signs and similar), VERO statements
   that are homogeneous readings of the panel's explicitly listed contents
   (destination → direction/lane rows) merge into one `lettura-delle-direzioni`
   group: panel reading is one transferable perception skill, not N recall facts,
   and coverage holds because the stimulus is printed on the depicted panel.
   Guardrails: (1) only literally-present listed content — never interpretation,
   classification (shape/colour/meaning), or recall; (2) anything needing
   knowledge beyond reading (restrictions, prohibitions, category/vehicle limits,
   distance-as-rule, sign-type questions) stays its own group; (3) prefer a
   representative that exercises the panel's structure (junction-indexed read)
   over the most trivial one; (4) every such merge keeps the
   `lettura-delle-direzioni` label so the final audit can review the class.
   **Recall-protection override (ruling on cards 4616-4621): the uniform-attribute
   merge does NOT apply when the merged instances are themselves non-derivable
   recall facts the card exists to teach.** Violation→sanction and
   violation→points enumerations stay split like speed values and bands: the
   boundary (which violation triggers which sanction) is the non-derivable thing
   tested, as the cards' own FALSO sides show (cross-sanction traps).
   Distinction from 4527: there the violations were taught on other cards and the
   uniform consequence was not the unique curriculum; here the enumeration IS.
   Context vs state (ruling on card 4500): when one rule with a uniformly
   stated condition is instantiated across contexts, the CONTEXT
   (level crossing / traffic lights / congestion) is a belief-bearing variable
   and stays split — a learner can know the crossing case without generalizing;
   the STATE of the obstructing vehicle (stopped vs slow-moving) is inert
   decoration and merges (the 4114/4131 noise side).
   The transpose holds too (ruling on card 4658): "one violation → its several
   distinct sanctions" stays split, like "many triggers → one sanction". Cards
   organized by sanction do not enumerate a given subject's full sanction set,
   so the cross-card defense fails in both directions.
   Uniform-attribute principle (ruling on card 4527): an attribute attached
   UNIFORMLY across instances ("each of these violations costs licence points")
   is one rule applied → merge, keeping the clearest statement of the rule;
   DISTINCT attribute-values across instances (different limits, durations,
   sanctions) are N recall facts → split.
   Contrast: 4147 time windows and 4622 validity bands are recall facts → split;
   wrong interpretations of a printed number (4268, 4370) are distinct traps →
   split. **Refinement (ruling on card 4297): 3e merges readings whose only
   significance is locating a row (destinations, directions, lane assignments);
   it does NOT apply when the listed items are themselves recall facts tested
   elsewhere as knowledge (speed limits, legal thresholds, distances-as-rules).
   Reading-skill cards merge; curriculum-on-a-panel stays split.** **Stimulus-class
   extension (approved after batch 18): 3e also covers directional arrows painted
   in the depicted figure (lane-arrow assignments, cards 4222-4224) — perception
   of present content with no independent recall value. Same guardrails; the 4297
   recall-exclusion still binds. Extension class tagged for the final audit.**

4. **FALSO groups — merge conservatively.** FALSO statements are traps. Merge two
   only if they name the SAME wrong belief. Litmus test: *could a learner correctly
   reject trap A and still fall for trap B?* If yes, they are different traps —
   separate groups. When unsure on the FALSO side, keep them separate.
4b. **FALSO trap families — the reviewed merge policy (batch-1 ruling).** Merge
   FALSO statements only when BOTH hold: (a) one corrective fact defeats all of
   them, AND (b) a learner could not plausibly hold one of the beliefs while
   rejecting another. In practice:

   - **Same error + irrelevant decoration → merge (high).** "Slippery for 2 km" /
     "narrow for 2 km" / "dead-end at 2 km" all read the route number "SS 2" as a
     distance; the road-condition word is decoration. Likewise "lane reserved for
     buses" / "road reserved for buses" (width is decoration), and a wrong order
     that differs from the truth only by one swap merged with the pairwise form of
     that same swap (order T,A,O + "O waits for A" — the only false component in
     both is A-before-O).
   - **Different kind of error → separate.** Number misread as lanes vs exits vs
     vehicle count vs km: different quantities, distinct traps (card 4370).
   - **Opposite/complementary beliefs → separate.** "Valid only daytime" vs "valid
     only at night": a learner can reject one by holding the other, even though
     both resolve to "valid 24h".
   - **Category exemptions → separate.** "Buses exempt" vs "trucks exempt" vs
     "taxis exempt": plausibly independent beliefs.
   - **Different wrong class → separate.** "It's an indication sign" vs "a
     prohibition sign" vs "a lane sign" are different misconceptions; but pure
     rewordings of one misreading ("the arrow is one-way signage", said four ways)
     merge.
   - **Independent sub-claims → separate.** "R waits for H" vs "R waits for H and
     A": the second adds a claim the first lacks; a learner could hold one and
     reject the other. No blanket "wrong-order family": each wrong permutation
     that combines claims independently stays its own trap.
   - **Instance/entailment of one rule → merge ONLY with mutual entailment; a
     one-way broad⊇narrow relation stays split (rulings on cards 4071 and 4100).**
     "Two bars = two tracks" merges with "the bars count the tracks" because the
     narrow statement has no coherent standing except as the rule applied — you
     cannot hold it while rejecting the counting scheme. "Bans flammable liquids"
     does NOT merge with "bans flammable products": the narrow belief is
     coherently holdable on its own (the liquid-tanker association), so the
     superset relation is one-way → independent pattern → split. Contrast also
     4145: "particular categories may park" vs "off-duty ambulances may park" are
     separately holdable exemption beliefs → split. **The decoration line (ruling
     on card 4114): decoration that is pure noise to the error merges (road
     conditions on 4269, lane-line clauses on 4058); a varying quantity the
     learner holds independent beliefs about (a weight threshold, a cutoff) is
     NOT decoration → split** ("autocaravan >3.5 t banned" vs "autocaravan 6 t
     banned" stay separate: someone imagining a >5 t cutoff rejects one and
     accepts the other).
   - **When in doubt, stay split.** Use medium confidence only for merges you
     could not resolve under this policy; the shipped artifact is built with
     `--conservative-falso`, which splits sub-high FALSO merges until a human
     reviews them.
4c. **Cross-card consistency (approved after batch 5).** FALSO statements merge at
   high confidence when their phrasings are grouped as a single VERO concept
   elsewhere in the bank: if the bank itself treats "strada deformata" / "cattivo
   stato" / "pavimentazione irregolare" as one concept where they are true (card
   4051), they are one wrong belief where they are false. Two mandatory conditions:
   (1) every 4c merge cites the establishing VERO card/group in `why_keep`, in the
   form `[4c: <group-concept> @<cardId>]`, so the inference is auditable and
   reversible; (2) if a cited VERO group is ever revised, dependent FALSO merges
   must be revisited — the final whole-bank audit verifies this chain via the 4c
   tags.

5. **Wording similarity is irrelevant; only meaning counts.** Statements that differ
   by a single substitution — a vehicle letter (veicolo A / veicolo H), a count, a
   vehicle category (autobus / autocarri), a panel letter (figura A / figura B), a
   licence class (B / BE), a direction or order of precedence — are DIFFERENT
   concepts and must NOT merge, even at 99% identical wording. This applies
   especially to right-of-way cards ("Secondo le norme di precedenza…"), where each
   statement encodes a distinct crossing order.
6. **Compression falls out of the rules; it is not a target.** Typical cards land
   around half their statements via the VERO side and true FALSO rewordings —
   never by sacrificing a distinct trap. Dense cards (e.g. licence-validity bands,
   where every band is a distinct fact) legitimately stay near-full; that is
   correct behaviour, not a failure.
7. **Representative choice.** Within a group keep the clearest, most canonical,
   most general statement: prefer direct phrasing over circumlocution, and a
   statement covering the whole subject (e.g. both panels A and B) over one
   covering part of it.
8. **Confidence.** Per group: `"high"`, `"medium"`, or `"low"`. For multi-member
   FALSO groups this is your confidence that the members really are the same trap;
   a stricter build automatically splits FALSO merges below high confidence, so be
   honest, not optimistic.

### Output format

Strict JSON only, no commentary, statement numbers as strings:

```json
{
  "cardId": <id>,
  "groups": [
    {
      "concept": "<short-kebab-case-label, trap- prefix for FALSO>",
      "answer": "VERO" | "FALSO",
      "members": ["<number>", ...],
      "keep": "<number>",
      "why_keep": "<one short line>",
      "confidence": "high" | "medium" | "low"
    }
  ]
}
```

---

## Few-shot examples (include verbatim in every call)

### Example 1 — card 4272 (VERO rewordings collapse; every FALSO is a distinct trap)

INPUT:

```
CARD 4272 — topic: Segnali di indicazione — image: domandeb_images/4272.jpeg
21274 VERO  Il segnale raffigurato indica l'indirizzo ed i numeri telefonici del più vicino comando della polizia stradale
21275 VERO  Il segnale raffigurato indica la località ed i numeri di telefono del più vicino comando di polizia stradale
21276 VERO  Il segnale raffigurato indica la sede ed il numero telefonico del più vicino comando di polizia stradale
21277 VERO  Il segnale raffigurato riporta alcuni dati (località, via, telefoni) del più vicino comando di polizia stradale
21278 FALSO Il segnale raffigurato indica un posto di blocco della polizia
21279 FALSO Il segnale raffigurato indica una strada interrotta per incidente stradale
21280 FALSO Il segnale raffigurato indica una zona riservata al parcheggio dei veicoli della polizia
21281 FALSO Il segnale raffigurato indica la possibilità di incrociare una colonna di veicoli della polizia
21282 FALSO Il segnale raffigurato indica un tratto di strada riservato alla polizia
```

OUTPUT:

```json
{
  "cardId": 4272,
  "groups": [
    { "concept": "recapito-polizia-stradale", "answer": "VERO",
      "members": ["21274", "21275", "21276", "21277"], "keep": "21274",
      "why_keep": "most direct phrasing: address and phone numbers", "confidence": "high" },
    { "concept": "trap-posto-di-blocco", "answer": "FALSO",
      "members": ["21278"], "keep": "21278",
      "why_keep": "unique trap: checkpoint", "confidence": "high" },
    { "concept": "trap-strada-interrotta-incidente", "answer": "FALSO",
      "members": ["21279"], "keep": "21279",
      "why_keep": "unique trap: road closed by accident", "confidence": "high" },
    { "concept": "trap-parcheggio-veicoli-polizia", "answer": "FALSO",
      "members": ["21280"], "keep": "21280",
      "why_keep": "unique trap: police parking area", "confidence": "high" },
    { "concept": "trap-colonna-veicoli-polizia", "answer": "FALSO",
      "members": ["21281"], "keep": "21281",
      "why_keep": "unique trap: police convoy ahead", "confidence": "high" },
    { "concept": "trap-strada-riservata-polizia", "answer": "FALSO",
      "members": ["21282"], "keep": "21282",
      "why_keep": "unique trap: road reserved for police (travel, distinct from the parking trap)", "confidence": "high" }
  ]
}
```

Why: the four VERO statements are one fact reworded → one group. All five FALSO
statements pass the litmus test against each other (a learner could reject
"checkpoint" and still believe "reserved road") → five singleton groups. Kept 6/9.

### Example 2 — card 4370 (identical FALSO template, four DIFFERENT traps)

INPUT:

```
CARD 4370 — topic: Pannelli integrativi dei segnali — image: domandeb_images/4370.jpeg
22231 VERO  Il pannello integrativo in figura (A) indica la vicinanza di una o più curve strette
22232 VERO  La presenza di uno dei due pannelli integrativi in figura indica la vicinanza di una o più curve strette
22233 VERO  Il pannello integrativo in figura (B) indica la vicinanza di una o più curve particolarmente pericolose
22234 VERO  La presenza di uno dei due pannelli integrativi in figura indica la vicinanza di una o più curve particolarmente pericolose
22236 VERO  La presenza di uno dei due pannelli integrativi in figura può indicare uno o più tornanti
22238 FALSO Il pannello integrativo di figura B indica il numero di corsie di cui è composta la strada
22239 FALSO Il pannello integrativo di figura B indica quanti veicoli contemporaneamente possono percorrere la curva
22240 FALSO Il pannello integrativo di figura B indica quanti chilometri mancano per poter trovare un cavalcavia che consente di invertire il senso di marcia
22241 FALSO Il pannello integrativo di figura B indica il numero degli svincoli autostradali
22242 FALSO La presenza di uno dei due pannelli integrativi in figura indica l'incrocio con una strada dalla quale si immettono autocarri provenienti da una discarica
```

OUTPUT:

```json
{
  "cardId": 4370,
  "groups": [
    { "concept": "pannelli-indicano-curve-pericolose", "answer": "VERO",
      "members": ["22231", "22232", "22233", "22234", "22236"], "keep": "22232",
      "why_keep": "covers both panels with the core fact (sharp/dangerous curves ahead)", "confidence": "high" },
    { "concept": "trap-numero-corsie", "answer": "FALSO",
      "members": ["22238"], "keep": "22238",
      "why_keep": "unique trap: number means lane count", "confidence": "high" },
    { "concept": "trap-veicoli-contemporanei-in-curva", "answer": "FALSO",
      "members": ["22239"], "keep": "22239",
      "why_keep": "unique trap: number means simultaneous vehicles", "confidence": "high" },
    { "concept": "trap-km-a-cavalcavia", "answer": "FALSO",
      "members": ["22240"], "keep": "22240",
      "why_keep": "unique trap: number means km to a U-turn overpass", "confidence": "high" },
    { "concept": "trap-numero-svincoli", "answer": "FALSO",
      "members": ["22241"], "keep": "22241",
      "why_keep": "unique trap: number means motorway exits", "confidence": "high" },
    { "concept": "trap-autocarri-discarica", "answer": "FALSO",
      "members": ["22242"], "keep": "22242",
      "why_keep": "unique trap: junction with landfill trucks", "confidence": "high" }
  ]
}
```

Why: "sharp curves", "particularly dangerous curves", and "hairpins" all teach the
same panel meaning → one VERO group. The FALSO statements share a template
("figura B indica il numero…") but each names a different wrong reading of the
number — lanes, vehicles, kilometres, exits. Rule 5: template match never merges.
Kept 6/10.

### Example 3 — card 4322 (a legitimate FALSO merge)

INPUT:

```
CARD 4322 — topic: Segnali di indicazione — image: domandeb_images/4322.jpeg
21760 VERO  Il segnale raffigurato indica una fermata di autobus di pubblico trasporto extraurbano
21761 VERO  Il segnale raffigurato può essere abbinato ad un pannello che riporta gli orari di partenza degli autobus extraurbani
21762 VERO  Il segnale raffigurato indica il luogo dove aspettare un autobus di pubblico trasporto extraurbano
21763 FALSO Il segnale raffigurato indica un divieto di transito agli autobus
21764 FALSO Il segnale raffigurato indica una corsia riservata agli autobus
21765 FALSO Il segnale raffigurato indica un'area di sosta per autobus e filobus
21766 FALSO Il segnale raffigurato indica una strada riservata agli autobus
```

OUTPUT:

```json
{
  "cardId": 4322,
  "groups": [
    { "concept": "fermata-autobus-extraurbano", "answer": "VERO",
      "members": ["21760", "21762"], "keep": "21760",
      "why_keep": "names the sign's meaning directly (bus stop)", "confidence": "high" },
    { "concept": "abbinabile-pannello-orari", "answer": "VERO",
      "members": ["21761"], "keep": "21761",
      "why_keep": "distinct fact: may carry a timetable panel", "confidence": "high" },
    { "concept": "trap-divieto-transito-autobus", "answer": "FALSO",
      "members": ["21763"], "keep": "21763",
      "why_keep": "unique trap: no-entry for buses", "confidence": "high" },
    { "concept": "trap-via-riservata-autobus", "answer": "FALSO",
      "members": ["21764", "21766"], "keep": "21764",
      "why_keep": "same wrong belief: the sign reserves the way (lane/road) for buses", "confidence": "medium" },
    { "concept": "trap-area-sosta-autobus", "answer": "FALSO",
      "members": ["21765"], "keep": "21765",
      "why_keep": "unique trap: bus parking area (parking, not travel)", "confidence": "high" }
  ]
}
```

Why: "bus stop" and "place to wait for the bus" are one fact; the timetable-panel
fact is separate. On the FALSO side, "lane reserved for buses" and "road reserved
for buses" fail the litmus test in the merge direction — a learner who rejects one
rejects the other; it is the same wrong belief at different width — so they merge
(confidence medium, honestly). "No entry" and "parking area" are different beliefs
and stay. Kept 5/7.

---

## CARD INPUT

(append the `format-card` block for the card being processed)
