# Anonymous "most-missed" analytics — the remaining build

Two features were planned together under one promise: **no email, name, password
or account is ever required, and no stored data can be tied to a person.**

**Sync shipped.** Encrypted cross-device sync is live and confirmed on two
devices. What it became is recorded at the bottom of this file, because some of
it went beyond the original plan and the reasoning is worth keeping.

**Analytics has not been started.** `stats.php` and `stats-admin.php` do not
exist, and `app.js` contains no `sendBeacon` and no analytics code of any kind.
Everything above the horizontal rule below is work still to do.

The two features must never share a store, or "we cannot read your synced data"
stops being true.

---

## Privacy invariants (must hold at every step)

- [x] No personal data collected (no email, name or login).
- [x] Sync blobs encrypted client-side; the server sees only a hash (the
      filename) and ciphertext.
- [ ] Analytics stores **aggregate counters only**. Hits are incremented and
      discarded: no per-event log, no per-hit timestamps.
- [x] No IP addresses stored in app data. `sync.php` hashes the IP for rate
      limiting and never writes it raw; `stats.php` must do the same.
- [x] Footer and privacy text describe exactly what leaves the device. It must
      be revised again the first time analytics sends anything.
- [ ] Analytics explained in Settings, default per D1.

## The one decision still open

- **D5 — the stats store.** SQLite via `pdo_sqlite` (cleaner concurrency) or a
  JSON file with `flock`. Pick at build time, based on what the host offers.
  Neither is installed or tested yet. `sync.php` is the working precedent for
  the file-based route: it already does `LOCK_EX` writes, an atomic
  temp-then-rename, an auto-created 0700 directory outside the web root with a
  deny-all `.htaccess` written on every request, and per-IP rate limiting on a
  hashed IP.

D1 (opt-in, default OFF), D2, D3, D4 and D6 are settled; see the record below.

## B1. Client buffer and beacon

- [ ] On answering a statement, if analytics is enabled, push `{ n, r:0|1 }` to
      an in-memory buffer. No identity, no session id.
- [ ] Flush with `navigator.sendBeacon('stats.php', batch)` every N events and
      on `pagehide` / `visibilitychange`.
- [ ] Settings toggle with a one-line explanation, default OFF per D1.

## B2. Server `stats.php`

- [ ] Accept `{ events: [{n, r}, …] }`. Validate that each `n` is a known
      statement number and `r` is 0 or 1, and cap the batch size.
- [ ] Increment aggregate counters per D5: `counts(number, seen, missed)`.
      Discard the events once counted.
- [ ] Guards: per-IP rate limit and a size cap, on the `sync.php` pattern. No
      IP in app data.
- [ ] A withdrawn statement must not be counted. `questions.json` marks 41 with
      `retired`, and the app filters them at load, so a number arriving for one
      is either a stale client or a forged post.

## B3. Admin `stats-admin.php`

- [ ] Key-protected through `secrets.php`, like the other admin pages. Rank by
      miss rate with a minimum sample size, and show the raw seen and missed
      counts beside it.

## B4. Verify

- [ ] Counts increment as expected, and turning the toggle off stops every
      network call.
- [ ] Nothing per-event or timestamped exists on disk anywhere.

## B5. Later: surface the insight

- [ ] Mark commonly missed statements in the UI, as a hint badge or a
      stumbling-points view. Design it once real data exists, not before.

## Ship checklist for each step

- [ ] Bump `APP_VERSION` (app.js) and `CACHE_VERSION` (sw.js) together.
- [ ] Add the new PHP file and its token.
- [ ] Revise the privacy and footer text, since analytics is the first thing to
      leave the device that is not the user's own encrypted blob.
- [ ] Record which files must be uploaded (`stats.php`, `stats-admin.php`).

---

## What sync became (shipped, 2026-06)

Kept because the reasoning outlived the checklist.

- **Full-state sync**, not only answers: mock-exam history, cards reopened by a
  mock miss, reviews read, flagged issues, and the scalar settings (Abridged,
  Reviewer, reviewer code). **Level and theme stay per-device** by decision.
- **Per-statement merge** on max seen, correct and streak. It replaced a
  whole-card `totalSeen` merge that lost correctness on ties. Commutative and
  idempotent, verified against two real device states.
- **Canonicalized code** for deriving the bucket and the key, so an en dash, a
  stray space or a capital letter cannot change it, plus a visible Sync ID and
  a status line that distinguishes pulled, merged and first-device.
- **PBKDF2 at 100k**, lowered from 200k for speed on phones and
  envelope-versioned so older blobs still decrypt. A 30 second fetch timeout,
  and per-phase `[sync]` timing logs.
- **Flags carry a tombstone** when cleared or sent, so a sync cannot resurrect
  one.
- Decisions resolved on the way: **D1** opt-in and default OFF; **D2** manual
  plus a quiet auto-sync on launch and on tab hide; **D3** all three levels and
  the full state; **D4** an app-generated high-entropy code
  (`patente-xxxx-xxxx-xxxx`, Crockford base32, about 60 bits); **D6** the build
  order, groundwork then sync then analytics.

The crypto is `syncGenerateCode`, `syncBucketId`, `syncDeriveKey`,
`syncEncrypt` and `syncDecrypt` in `app.js`, with `sync.php` on the server.
