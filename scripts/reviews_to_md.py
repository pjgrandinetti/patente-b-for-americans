#!/usr/bin/env python3
"""
Export topic_reviews.json -> one editable Markdown file per topic.

Run from the repo root:
    python3 scripts/reviews_to_md.py

Writes files into ./topic_reviews_md/ . Edit those .md files, then run
scripts/md_to_reviews.py to fold your changes back into public_html/topic_reviews.json.

Each file looks like:

    <!-- TOPIC: Segnali di indicazione -->
    <!-- Edit content below. Do NOT change the TOPIC line or the LANG markers. -->

    <!-- LANG: en -->
    ...English review markdown...

    <!-- LANG: it -->
    ...Italian review markdown (may be empty for now)...
"""
import json, re, pathlib, sys

# This script lives in scripts/; the project root is its parent.
ROOT   = pathlib.Path(__file__).resolve().parent.parent
SRC    = ROOT / "public_html" / "topic_reviews.json"
OUTDIR = ROOT / "topic_reviews_md"

# Default ground-truth (authoring) language. A fork can change this — and the
# build (md_to_reviews.py) honors a per-file <!-- SOURCE: xx --> override too.
SOURCE_LANG = "en"

def slug(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = s[:50].strip("-")          # cap length (some topic names are very long)
    return s or "topic"

def main():
    # The Markdown in topic_reviews_md/ is the GROUND TRUTH; topic_reviews.json is
    # generated from it by md_to_reviews.py. This reverse script (JSON -> Markdown)
    # would overwrite that ground truth, so it refuses to run once the folder
    # exists unless you pass --force. Normally you only need it once, to seed the
    # Markdown, or to deliberately re-seed from the JSON.
    force = "--force" in sys.argv
    if OUTDIR.exists() and any(OUTDIR.glob("*.md")) and not force:
        sys.exit(
            f"Refusing to overwrite the ground-truth Markdown in {OUTDIR.name}/.\n"
            f"Edit the .md files and run scripts/md_to_reviews.py instead.\n"
            f"To re-seed Markdown FROM the JSON anyway, run: python3 scripts/{pathlib.Path(__file__).name} --force"
        )

    data = json.loads(SRC.read_text(encoding="utf-8"))
    OUTDIR.mkdir(exist_ok=True)

    # Manifest preserves the exact key order so the import can rebuild it 1:1.
    manifest = []
    for i, (name, entry) in enumerate(data.items(), start=1):
        # Index prefix keeps the folder in the same order as the JSON and
        # guarantees unique filenames even when slugs collide/truncate equally.
        fn = f"{i:02d}-{slug(name)}"
        path = OUTDIR / f"{fn}.md"
        en = (entry.get("en") or "").strip("\n")
        it = (entry.get("it") or "").strip("\n")
        path.write_text(
            f"<!-- TOPIC: {name} -->\n"
            f"<!-- SOURCE: {SOURCE_LANG} -->\n"
            f"<!-- Edit content below. Do NOT change the TOPIC, SOURCE, or LANG markers. -->\n\n"
            f"<!-- LANG: en -->\n{en}\n\n"
            f"<!-- LANG: it -->\n{it}\n",
            encoding="utf-8",
        )
        manifest.append({"file": f"{fn}.md", "topic": name})

    (OUTDIR / "_manifest.json").write_text(
        json.dumps({"source": SOURCE_LANG, "topics": manifest}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Exported {len(manifest)} topics -> {OUTDIR}")

if __name__ == "__main__":
    main()
