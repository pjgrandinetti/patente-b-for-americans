# Pre-public checklist (URGENT)

Do these **in order** before flipping the GitHub repo from private to public.
Going public exposes all git history permanently, so item 1 is a hard gate.

**Verify the ignore rules actually match before the flip.** `.gitignore` listed
the private folder with a capital letter while the folder on disk was lower-case (it is `private/` since 2026-10-25). It appeared to work because
git's `core.ignorecase` is true on macOS, but the pattern does not match
case-sensitively, so on a Linux checkout an 819 MB copyrighted textbook would
have become committable. Both cases are now listed (2026-09-16). Re-run
`git check-ignore -v` on the private paths after any `.gitignore` edit, and
confirm `git ls-files | grep -i private/` is empty.

- [x] **1. Deploy the secrets refactor + `secrets.php` to the server.** Done (maintainer, confirmed 2026-10-25: the refactored endpoints and `secrets.php` have been on the server since the rotation, and the old keys no longer work).
  Upload the refactored PHP endpoints **and** `public_html/secrets.php` (with the
  rotated admin keys + reviewer code). Verify the **new** `admin.php` key
  works and the **old** keys no longer do. (`flags-admin.php` and
  `bugs-admin.php`, the pages the old keys belonged to, were removed from
  the repository on 2026-10-25; delete them on the server too.) This makes the old
  keys still sitting in git history harmless.
  *(Optional, cleanest: also purge the old key strings from history with
  `git filter-repo` / BFG before publishing.)*

- [x] **2. Add the `LICENSE` file (AGPL-3.0).** Done 2026-10-17: the verbatim
  text from gnu.org/licenses/agpl-3.0.txt is committed at the repo root, which
  GitHub detects for the license badge. Content stays **CC-BY-SA-4.0**.

- [x] **3. Enable secret scanning + push protection.** Done 2026-10-25 on the new repository.
  GitHub repo **Settings → Code security**: turn on secret scanning and push
  protection (free on public repos) so no new secret can ever be pushed.
  *(Optional once public: enable Dependabot and CodeQL.)*

- [x] **4. Publish.** Done 2026-10-25: the development history, which held personal details trimmed only on 2026-10-17 and two dead admin keys, was not published. The local repository was recreated with the current tree as a single commit, the old private GitHub repository is to be deleted, and this commit is pushed to a new public repository. The old history survives only in a bundle file on the maintainer's own disk.

## Already done (context)

- Admin keys + reviewer codes moved out of committed code into gitignored
  `public_html/secrets.php`; all rotated; admin pages fail closed if absent.
- CI green: data integrity + version lockstep + reviews-in-sync, JS `no-undef`,
  `php -l`, gitleaks.
- `LICENSING.md` (AGPL-3.0 code / CC-BY-SA-4.0 content) and `CONTRIBUTING.md` added.
- README and docs reflect the current app.
- Disclaimer in-app: independent/unofficial; question bank is the Ministry's
  publicly published material (also covers redistribution of `domandeb_images/`).
