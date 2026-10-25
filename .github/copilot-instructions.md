# Copilot instructions — Patente B

## Bump the cache version on every shippable change

Whenever you change any app shell asset served to users (e.g.
`public_html/app.js`, `public_html/style.css`, `public_html/index.html`,
`public_html/manifest.json`, or the data JSON files), you MUST also bump
`CACHE_VERSION` in [public_html/sw.js](../public_html/sw.js).

- The value follows the pattern `patente-netfirst-YYYYMMDD<letter>`.
- Increment the trailing letter (`...l` → `...m`), or roll the date and reset
  the letter to `a` when the date changes.
- This installs a fresh service worker, clears stale caches, and triggers the
  in-app "A new version is available. Restart to update." prompt so installed
  (home-screen / dock) users actually receive the update.

If you forget this step, users on the installed PWA may keep running the old
cached code and never see the fix.

## Topic reviews: Markdown is the source of truth

The per-topic concept reviews are authored in `topic_reviews_md/*.md`. The file
the app loads, `public_html/topic_reviews.json`, is **generated** from them.

- **Never hand-edit `public_html/topic_reviews.json`** — edit the Markdown.
- After editing, run `python3 scripts/md_to_reviews.py` from the repo root. It rebuilds
  the JSON (preserving topic order via `_manifest.json`), writes a `.bak`,
  validates the output, and bumps `CACHE_VERSION` automatically.
- `scripts/reviews_to_md.py` is the reverse (JSON → Markdown) and refuses to overwrite
  the ground-truth Markdown unless `--force` is passed; you rarely need it.
- See `topic_reviews_md/README.md` for the file format and authoring conventions.

## Writing pedagogical question explanations

Each true/false question in `public_html/questions.json` has an `explanation`
field. These are study aids, so they should *teach the distinction*, not just
assert the answer. Lessons learned from real user feedback:

- **Start with `True.` or `False.`** matching the statement's `answer`
  (`VERO` → `True.`, `FALSO` → `False.`). A script checks this; keep it exact.
- **For a FALSE statement, name what the sign actually is *and* what the
  claimed thing would look like.** "It is a junction sign, not a level crossing"
  is weak. Better: explain that a junction is where two *roads* meet, while a
  level crossing is where the road crosses *railway tracks*, warned by a
  different sign. Give the learner the contrast they need to tell them apart.
- **Anchor on the single discriminating "tell."** Usually one feature decides
  the answer: background colour, symbol shape, arrow type, a number, a word.
  Say which feature and what it means.
- **Colour is the most common stumbling block.** When the answer depends on a
  sign's colour, name the colour, say what it means, and describe what the
  *other* case would look like (e.g. "this is a white urban direction sign; the
  same sign on an extra-urban road would be blue"). Reference key:
  - Direction/information signs: **white = urban**, **blue = extra-urban**,
    **green = motorway**, **brown = tourist/cultural**, **yellow = temporary
    roadworks**.
  - Sign families by shape: **red triangle = danger/warning**,
    **red circle = prohibition**, **blue circle = mandatory (obbligo)**,
    **blue square = information**. A red diagonal line through a sign = *end* of
    that restriction.
- **Spell out commonly confused pairs** rather than assuming: level crossing
  vs road junction; "pass to the left" means keeping the obstacle on your
  *right*; *fermata* (brief stop, allowed under no-parking) vs *sosta*
  (parking); *strada interrotta* (road cut at a point, with a detour) vs a road
  that is fully *closed*; minimum vs maximum speed limit.
- **Match the official exam answer even where real-world nuance differs.** The
  goal is to help the user pass the test; note the exam's expected reasoning,
  not edge cases the exam ignores.
- **Keep it to one or two plain-English sentences.** Exam-accurate, concrete,
  no jargon dumps.

(`questions.json` is a cached asset, so editing explanations still requires a
`CACHE_VERSION` bump per the section above. This `.github/` file does not.)

## Topic reviews: one subject, one place — at its image

A sign, marking, or device is explained **completely where its picture appears**:
what it means, what it requires of you, and the trap the quiz sets on it. Never
split a subject across sections — no "recognition" section holding the images
and a later "what it requires in practice" list holding the rules. The reader
studies the picture, forms an understanding, and moves on; a rules list further
down arrives too late and reads as a separate topic. The same applies to a
correction after a reviewer reports confusion: it belongs with the image, not
only in a later section or in the question's `explanation`.

There is **no acceptable split** — not even "one sentence up top, the detail
below".

Check it mechanically after editing any review:

```
python3 scripts/check_review_placement.py
```

It fails when a rule bullet names a subject that is pictured in a different
section. Reviews with no images at all (behavior topics such as safe distance or
licensing) are skipped.

## Writing style (reviews and explanations)

- **Write in complete, standalone sentences. Do not glue an explanatory
  fragment onto a sentence.** This applies to em-dashes (`text — aside — more`),
  trailing em-dashes (`text — aside`), colons that tack on a restating clause
  (`text: more text`), and semicolons joining two thoughts. The reader strongly
  dislikes all of these. Break the thought into separate full sentences ending in
  periods. (A colon is fine only to introduce a genuine list, and parentheses are
  fine for a short term gloss such as an Italian translation.)
  - Bad: "It has no same-level junctions — every road joins by a ramp — and a
    130 km/h limit."
  - Bad: "It has no same-level junctions: every road joins by a ramp."
  - Good: "It has no same-level junctions. Every road joins or leaves it by a
    ramp. The limit is 130 km/h."
- **Write complete sentences, not telegraphic fragments.** Compressing for
  brevity (`Green direction signs, limit 130 km/h`) creates ambiguity. Say it in
  full: "On an autostrada the direction signs have a green background, and the
  speed limit is 130 km/h."
- **American English, used directly.** The audience is American. Use the American
  term as *the* term; do not write it as "the American word for X" or gloss a
  British term with it. Examples: **yield** (not "give
  way"), **low/high beams** (not dipped/full beams), **crosswalk** (not
  "pedestrian crossing"), **median** (not "central reservation"), **shoulder**,
  **passing** (overtaking is acceptable but "passing" is the natural US term),
  **safety island** (salvagente, not "passenger refuge"), **pull-off** or
  "turnout" (piazzola, not "lay-by").
- **Road-type names: keep the Italian, do NOT translate to a single English word.**
  "Highway" is ambiguous to Americans (freeway? expressway? any big road?), and
  every English candidate misleads (freeway implies free; tollway/turnpike imply
  always-tolled, which is false; motorway is British). So use the exam's own term:
  **autostrada** (controlled-access road, 130 km/h, green signs, *usually* tolled —
  not always), **main extra-urban road** (*strada extraurbana principale*, 110,
  blue signs), **secondary extra-urban road** (90). Never write "highway" for
  autostrada. Note: *Codice della Strada* (the rulebook) is the **"road code"**,
  never the British "Highway Code".
- **Define a term at its first use**, and gloss Italian terms in parentheses.
