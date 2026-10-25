# Contributing

Thanks for helping improve the Patente B Study App for Americans. The most valuable
contributions right now are **content corrections** — the questions, answers,
translations, and explanations are AI-assisted and being human-verified.

## Reporting problems (no GitHub needed)

- **Content that looks wrong** (a translation, explanation, or answer): use
  **Reviewer mode** in the app — flag the statement with a category and note. If
  you're a certified driving-school teacher (*insegnante di teoria*), ask the
  maintainer for a **trusted reviewer code** so your flags are prioritized (see
  [docs/TRUSTED-REVIEWERS.md](docs/TRUSTED-REVIEWERS.md)).
- **App bugs**: use **"Report a problem"** in the app footer (open to everyone).
- Or open a **GitHub issue** for anything.

## Editing content (pull requests)

- **Concept reviews** live in `topic_reviews_md/*.md` — this is the **source of
  truth**. Edit the Markdown, then rebuild:
  ```bash
  python3 scripts/md_to_reviews.py
  ```
  **Never hand-edit `public_html/topic_reviews.json`** — it is generated, and CI
  checks it is in sync.
- **Question explanations / translations** are in `public_html/questions.json`.
  Edit **only** `english_translation`, `explanation`, and `explanation_it`.
- **Never change `italian_text` or `answer`.** Those are the Ministry's official
  question bank; an answer is only "wrong" if verified against the official key —
  flag it for the maintainer rather than editing.
- **English is American English** (yield, shoulder, tire, color, meter, …). Do not
  alter Italian text.

## Developing

It's a static PWA — no build step or framework. Serve `public_html/` with any
static server to run it. The optional PHP endpoints (`sync.php`, `submit-flags.php`,
`report-bug.php`, and the `*-admin.php` pages) need PHP and a private
`public_html/secrets.php` (copy it from `secrets.example.php` — **never commit
secrets**).

### What CI enforces (so PRs stay green)

- **Version lockstep:** bump `APP_VERSION` in `app.js` **and** `CACHE_VERSION` in
  `sw.js` to the same value for any change under `public_html/` (pattern
  `YYYYMMDD<letter>`).
- **`topic_reviews.json` in sync** with `topic_reviews_md/` (rebuild before commit).
- **JS:** `node --check` + ESLint `no-undef` on `app.js`/`sw.js`.
- **PHP:** `php -l` on every endpoint.
- **No secrets** in the tree (gitleaks).
- Data integrity: valid JSON, answers ∈ {VERO, FALSO}, no duplicate statement
  numbers, every image/abridged/review reference resolves
  (`python3 scripts/validate_data.py`).

Run the data check locally before pushing:
```bash
python3 scripts/validate_data.py
```

## Licensing of contributions

By contributing you agree your work is licensed as the project is: **code under
AGPL-3.0-or-later, content under CC-BY-SA-4.0** (see [LICENSING.md](LICENSING.md)).
The official question bank is not relicensed.
