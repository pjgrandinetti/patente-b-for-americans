#!/usr/bin/env python3
"""Stamp each data file's content hash into app.js and sw.js.

The three large data files are served cache-first under a URL that carries a
version, `questions.json?v=…`. Until 2026-09-24 that version was APP_VERSION,
so EVERY release, including one that changed a line of CSS, made every device
download all three files again (about 1.45 MB), and the server log for one
day of releases showed questions.json fetched 34 times by one person. The
version is now the file's own content hash, stamped here as DATA_HASH in
BOTH public_html/app.js and public_html/sw.js, so a data file is downloaded
only when that file has changed.

  python3 scripts/stamp_data_hashes.py          # rewrite the two stamps
  python3 scripts/stamp_data_hashes.py --check  # exit 1 if either is stale

validate_data.py runs --check, so a data file edited without re-running this
fails the build rather than shipping a URL that still names the old bytes.
"""
import hashlib, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public_html"
FILES = ["questions.json", "vocabulary.json", "topic_reviews.json"]
STAMP_RE = re.compile(r"^const DATA_HASH = \{[^}]*\};$", re.M)


def hashes():
    out = {}
    for f in FILES:
        out[f] = hashlib.sha1((PUB / f).read_bytes()).hexdigest()[:12]
    return out


def stamp_text(h):
    inner = ", ".join(f"'{f}': '{h[f]}'" for f in FILES)
    return "const DATA_HASH = { " + inner + " };"


def main():
    check = "--check" in sys.argv
    want = stamp_text(hashes())
    stale = []
    for name in ("app.js", "sw.js"):
        p = PUB / name
        s = p.read_text(encoding="utf-8")
        m = STAMP_RE.search(s)
        if not m:
            print(f"{name} carries no DATA_HASH stamp"); return 1
        if m.group(0) == want:
            continue
        stale.append(name)
        if not check:
            p.write_text(s[:m.start()] + want + s[m.end():], encoding="utf-8")
    if check:
        if stale:
            print(f"DATA_HASH is stale in {', '.join(stale)}: run scripts/stamp_data_hashes.py"); return 1
        print("✓ DATA_HASH fresh in app.js and sw.js"); return 0
    print(f"DATA_HASH {'rewritten in ' + ', '.join(stale) if stale else 'already fresh'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
