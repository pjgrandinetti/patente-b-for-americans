# Patente B Study App for Americans

A static, offline-first **Progressive Web App** for the Italian **Category B**
(*Patente B*) theory exam. It is **built for American English speakers**, whose
needs shape the levels, the translations and the notes, and it is **also usable
by native Italian speakers**: the interface switches to Italian on its own for
an Italian browser, every topic review has a full Italian half, and each
statement carries an Italian explanation, so Solo italiano is a complete study
path with no English in it. Built on the official *DomandeB* bank: **716 Ministry cards, split into 851 study cards / 7,147 true/false statements** across **25 topics** (41 statements the Ministry has since withdrawn are archived but never shown, so **849 study cards / 7,106 statements** reach the learner), every statement paired with an English translation and a plain-English explanation.

Live at **https://patente.physyapps.com**.

## Background

There is no US–Italy license-conversion agreement (the same is true for Canada, Australia, New Zealand, and South Africa; UK/Irish/Maltese drivers can simply convert). So a US resident must pass the full Italian exam like a first-time driver. The theory exam is **30 true/false questions in 20 minutes, no more than 3 wrong, entirely in Italian**. The app's own **How you get an Italian license** panel describes the full process and is kept current with it. [docs/american-guide.md](docs/american-guide.md) adds the background an American needs and the language preparation the app leaves out.

## The app

No framework, no build toolchain, no server-side runtime for the core. Deploy the `public_html/` directory to any static host; it works offline once installed. A few **optional** PHP endpoints (encrypted sync, reviewer content flags, bug reports) add server features where PHP is available.

### Three study levels

Switch freely at any time — there is **no unlock gating** — and each level keeps its **own progress**, though credit flows between them (see the study loop).

| Level | Language shown | Help |
|-------|----------------|------|
| **L1 — English** | Italian statement + English translation | Vocabulary tooltips |
| **L2 — Italian** | Italian only | Vocabulary tooltips |
| **L3 — Italiano** | Italian only | None — real exam conditions |

The UI itself is English at L1 and Italian at L2/L3. The mock exam runs **only at L3** (it mirrors the real, Italian-only exam).

### The study loop

You work a topic's cards; a **card retires once all its active statements are answered correctly**, so the active pool shrinks to what you still miss. The **mock exam is the rigor check** — a missed statement **reopens its card across all three levels** so you re-study it everywhere. **Readiness** is the **average of your last 5 Italiano mock exams** (exam-ready at **≥ 93%**, needs at least 3 mocks) — not 100% coverage.

Three mechanisms do the rest of the work:

- **Credit flows down the levels.** Answer a statement correctly at a higher level and it is credited to every level below, because nobody should have to prove in English what they have already proven under exam conditions. Credit only ever flows **down** and only ever **adds**: a miss at Italiano does not touch English. Without this, clearing the bank meant clearing it three times, about 21,000 answers.
- **A weak-spot drill collects what you actually miss**, on the **Final Stretch** page, with the mocks it is there to prepare for (and on the dashboard as a banner). Statements missed at the Italian or Italiano levels are ranked across all three and drilled at Italiano. One leaves the list after **two correct answers in a row**, or after a **single** correct answer at Italiano when Italiano is not where it was missed: the ladder already credits downward, so a statement proven under exam conditions does not need a second confirmation of a mistake made at an easier level. A statement missed **at** Italiano, in study or in a mock, still needs two, since no level above it can vouch for it. Any new miss puts it back. A statement missed **only** in English is left alone: an early mistake never repeated at the Italian levels counts as learned.
- **The dashboard projects a date rather than setting a quota.** It measures the pace you are actually keeping, in clears per calendar day, and says where that leads, with a companion figure for a five-day week. Rest days are part of how long the material takes, so a quiet day moves the date instead of failing a target. The estimate holds back days at the end for the drill and the mock exams.

### Abridged mode (optional, default on)

An AI-curated, ~20%-smaller set that hides near-duplicate statements within a card. The full set is always one tap away, and a mock miss restores a card's full set automatically. The set is frozen in `public_html/abridged.json`; the generation method is documented in [docs/ABRIDGE-PROMPT.md](docs/ABRIDGE-PROMPT.md).

### Cross-device sync (optional, end-to-end encrypted)

Sync your full study state between your own devices with a **private code** — no account, email, or login. Progress is AES-GCM encrypted **on the device** with a key derived from the code (PBKDF2); the server (`sync.php`) stores only a hash of the code (as the filename) plus ciphertext **it cannot read**. It syncs answers, mock history, reopened cards, reviews-read, flagged issues, and the Abridged/Reviewer settings, merged conservatively (per-statement max for progress; last-write-wins for settings; unions elsewhere, each union paired with a **tombstone** so that clearing something stays cleared rather than being restored by the next merge). **Every row of the Settings dialog syncs, and so does the active level**; the theme is the only per-device preference. Auto-syncs on app launch and when the app is backgrounded.

### Reviewer mode (optional)

While studying you can **flag a statement** that looks wrong (category + note). A **"Reviewer Flagged issues"** section at the bottom of the dashboard lets you **Send to developer** (stored server-side by `submit-flags.php` — no email is sent), **Export** a Markdown report, or **Discard**. A *trusted reviewer code* tags submissions; the developer reviews them at `admin.php`.

### Report a problem (all users)

A **"Report a problem"** link in the footer opens a short form for app/functionality bugs — separate from the per-statement content flags, and **available to everyone** (not just reviewers). It auto-attaches the app version, level, current screen, and browser, and posts to `report-bug.php` (same self-hosted, spam-guarded pattern; stored outside the web root). The developer reviews reports at `admin.php`.

### Settings (gear icon)

One dialog grouping **Sync**, **Backup** (export/import), **Abridged mode**, and **Reviewer mode** (+ trusted reviewer code).

### Progress persistence

Stored in `localStorage`, keyed **per level**. Each card record is per statement:

```json
{ "st": { "18315": { "seen": 3, "correct": 2, "streak": 1, "given": "VERO" } }, "lastSeen": "2026-06-19" }
```

A statement is **mastered** once answered correctly at least once (`correct ≥ 1`); a card clears when all its active statements are mastered.

Progress exports to a `.patente` file (plain JSON). The **v3 full-state** format:

```json
{
  "version": 3, "exportedAt": "2026-06-19", "level": 3,
  "progress": { "L1": {…}, "L2": {…}, "L3": {…} },
  "examHistory": [], "fullCards": [], "reviewsRead": [],
  "flags": [], "flagsClearedAt": 0,
  "settings": { "abridged": "1", "englishOnly": null, "reviewer": null, "reviewerCode": null,
                "vocabView": null, "autoScroll": null, "sound": null, "vibrate": null,
                "ignoreSilent": null, "explCorrect": null, "examMix": null, "ttsRate": null,
                "settingsLang": null, "t": 0 }
}
```

Import **merges per statement** (max `seen`/`correct`/`streak`), so importing an older backup never erases newer progress and two devices merge cleanly. A backup reminder appears once you've built up progress and weekly thereafter.

### Italian vocabulary tooltips

`vocabulary.json` (~360 terms, English meanings) drives dotted-underline highlights whose glosses open on click (the click is what records the look-up); inflected forms match automatically (e.g. `veicolo` also matches `veicoli`).

### American English

All user-facing English uses American spelling and terms (e.g. *yield, shoulder, tire, color, meter, divided highway, gasoline*). Italian text is never altered.

## Repository layout

```
patente/
├── README.md
├── CLAUDE.md                        ← working guide for AI agents (read first)
├── docs/
│   ├── american-guide.md           ← background + language prep for an American (the app has the process)
│   ├── STUDY-EFFICIENCY-PLAN.md    ← WHY the loop is shaped this way (the loop itself is above)
│   ├── SYNC-AND-STATS-TODO.md      ← the analytics build, still to do (sync shipped; what it became is recorded there)
│   └── ABRIDGE-PROMPT.md           ← frozen prompt that produced abridged.json
├── scripts/
│   ├── extract_domandeb_to_json.py ← build questions.json from DomandeB.pdf
│   ├── translate_questions.py / translate_explanations.py ← batch translate (Anthropic API)
│   ├── improve_explanations.py / fix_bare_negations.py    ← explanation-quality passes
│   ├── md_to_reviews.py            ← build public_html/topic_reviews.json from topic_reviews_md/
│   ├── reviews_to_md.py            ← reverse: re-seed Markdown from the JSON (guarded)
│   ├── abridge_validate.py / abridge_rerun_diff.py        ← abridged-set tooling
│   └── make_icons.py               ← generate PWA icons
├── topic_reviews_md/               ← per-topic concept reviews (Markdown — source of truth)
├── sources/                        ← official PDFs (gitignored, not committed)
└── public_html/                    ← deploy this directory
    ├── index.html · app.js · style.css · manifest.json · sw.js
    ├── questions.json              ← 851 study cards / 7,147 statements (41 retired)
    ├── vocabulary.json · topic_reviews.json (generated) · abridged.json (frozen)
    ├── submit-flags.php · report-bug.php · sync.php    ← reviewer flags · bug reports · encrypted sync
    ├── admin.php                                       ← the admin page (flags, bugs, sync buckets)
    │                                                     (all optional PHP endpoints)
    ├── .htaccess (cache + security headers) · favicon.ico · robots.txt
    └── icons/ · domandeb_images/   ← PWA icons · sign/scenario images
```

## What a clone does not carry

Everything needed to **run** the app is committed: `public_html/` holds the
statements, the translations, the reviews and every sign image, and it is a
static site, so a clone plus a web server is a working app. Four things are
deliberately absent.

| Not committed | Why, and what to do about it |
|---|---|
| `sources/*.pdf` | The Ministry bank and the *Codice della Strada*, tens of megabytes of binary, and everything in them is already extracted into `questions.json` and `domandeb_images/`. You need them only to **re-extract** the bank or to check a disputed character against the original. `.gitignore` excludes `*.pdf` everywhere. |
| `public_html/secrets.php` | Admin keys and reviewer codes. Copy `secrets.example.php` to `secrets.php` and fill it in. Every endpoint tolerates its absence and fails closed, so the app runs without it: you lose sync, flag submission and the admin pages, nothing else. |
| `private/` | Local-only reference material: a copyrighted driving-school textbook used as a teaching reference, and the learner reports. Never committed or redistributed. |
| Working scratch | `sign_svgs_staging/`, `replaced_images_backup/`, `sign_library/`, review CSVs, `.bak` and resume files. Local to whoever ran the pass. |

## Deploy & versioning

- **Deploy** = upload `public_html/`. The PHP endpoints need PHP and write to directories **outside** the web root; the rest is static.
- Every change under `public_html/` bumps **`APP_VERSION`** (`app.js`) and the matching **`CACHE_VERSION`** (`sw.js`). The service worker is network-first for code and prompts the user to "Restart now" to apply an update.
- Topic reviews are authored in `topic_reviews_md/` and built with `python3 scripts/md_to_reviews.py` — **never hand-edit `topic_reviews.json`** (the build regenerates it and bumps `CACHE_VERSION`).

## Rebuilding data

```bash
python3 scripts/extract_domandeb_to_json.py                 # questions.json from the PDF
ANTHROPIC_API_KEY=sk-ant-… python3 scripts/translate_questions.py   # fill translations (resumable)
python3 scripts/md_to_reviews.py                            # topic_reviews.json from Markdown
```

## Source documents

`DomandeB.pdf` (official Ministry of Transport question bank) and the *Codice della Strada* (D.Lgs. 285/1992 plus the 2024 reform) live under `sources/` (gitignored). All question content derives from `DomandeB.pdf`; legal references come from the Codice della Strada.

## Contributing & license

Contributions — especially content corrections — are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). The project is dual-licensed: **code under AGPL-3.0-or-later**, **original content under CC-BY-SA-4.0**, and the official Ministry question bank is included unmodified and not relicensed. Details in [LICENSING.md](LICENSING.md).
