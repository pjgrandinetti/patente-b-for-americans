# Topic reviews — source of truth

These Markdown files are the **ground truth** for the per-topic concept reviews.
`public_html/topic_reviews.json` (what the app actually loads) is **generated**
from them — do not edit the JSON by hand; your changes would be overwritten on
the next build.

## House style (short version)

- **No em dashes (—).** Split the thought into separate sentences. See
  `docs/review-glossary.md` rules 10 and 13; both are checked by
  `python3 scripts/check_review_placement.py`.
- **One subject, one place: at its image.** A sign is explained completely where
  its picture appears, never split across sections.

## Editing workflow

1. Edit any `NN-topic.md` file here.
   - Keep the `<!-- TOPIC: ... -->`, `<!-- SOURCE: ... -->`, and
     `<!-- LANG: en -->` / `<!-- LANG: it -->` markers exactly as they are — they
     tell the build which topic, which authoring language, and which content block
     each section is.
   - Write English under `LANG: en`, Italian under `LANG: it` (Italian may be
     left empty for now; the app simply hides the review in Italian modes until
     it's filled in).
   - Body is the same Markdown subset the app renders: `##`/`###` headings,
     `**bold**`, `*italic*`, `- ` lists, `> ` blockquotes.
   - **Sign figures:** a line containing only `![caption](domandeb_images/NNNN.jpeg)`
     image tokens renders as a centered row of captioned thumbnails (tap to zoom).
     Put several on one line to show them side by side. Use clean isolated-sign
     card images, and keep figures sparing so reviews stay succinct.

2. From the repo root, build the JSON:

   ```
   python3 scripts/md_to_reviews.py
   ```

   This rewrites `public_html/topic_reviews.json` (preserving topic order via
   `_manifest.json`), writes a `.bak` of the previous JSON, validates the result,
   and bumps the service-worker cache version so the change ships.

## Ground-truth (source) language

Both languages live side by side in each file as peers; which one is *authored*
(the source) and which is *translated* (the derived copy) is a convention,
declared explicitly so it's clear and so translation tooling knows the direction:

- **Global default:** `"source": "en"` at the top of `_manifest.json`.
- **Per-file override:** a `<!-- SOURCE: xx -->` line in a file's header wins over
  the global default for that file (e.g. a fork could set `it`).

This is **metadata only** — the build always packs whatever is in both `LANG`
blocks into the JSON regardless of the source. Today English is the ground truth
(`source: en`) and Italian is translated from it; a fork that wants Italian as
the ground truth flips `source` to `it` (globally or per file) and authors the
`LANG: it` blocks instead. (A future translator script would read `source` to
decide which block to translate from.)

## Files

- `NN-topic.md` — one per topic, numbered to match the topic order in the app.
- `_manifest.json` — `{ "source": "en", "topics": [ … ] }`: the authoring
  language plus each file's exact topic key and order. Don't delete it; if you
  add a new topic, add a matching entry under `topics` (or re-seed).

## Re-seeding from JSON (rare)

`scripts/reviews_to_md.py` regenerates these Markdown files **from** the JSON. Because
that overwrites the ground truth, it refuses to run when this folder already has
`.md` files unless you pass `--force`. You normally never need it.
