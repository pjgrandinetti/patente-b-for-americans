#!/usr/bin/env python3
"""
Pre-commit checks on the topic reviews.

1. Rule 13: one subject, one place, at its image.
2. Rule 10: no em dash in review prose (split the thought into sentences).
3. Rule 31: no mention of "the manual" (internal source) in review prose.
4. Audience asymmetry: the Italian half never compares with the US.
5. American spelling in the English halves (meters, not metres).
6. Every `review_media/` figure carries an explicit size hint.

A sign/marking/device must be explained completely where its picture appears.
The defect this catches: a rule bullet sitting in a section WITHOUT images while
the subject it names is pictured in a different section, so the reader studies
the image, forms an understanding, and moves on before ever reaching the rule.

Reviews with no images at all (behavior topics: safe distance, overtaking,
licenses, liability…) are skipped: there is nothing to sit beside.

**Rule 13 counts only the SIGN pictures**, which live in `domandeb_images/`.
The concept diagrams in `review_media/` are deliberately excluded, and the
distinction is the whole point of the rule rather than a convenience. A sign is
an OBJECT: it has one meaning, it belongs in one place, and a reader who meets
its picture should find everything about it there. A concept is not an object.
The containment principle, the stopping distances and the points scale are each
discussed across a whole topic, because that is what makes them concepts, so
every bullet naming one would be reported as orphaned from its figure.
Measured on 2026-09-16, when the first four concept figures went in: they
turned topics 09 and 22 from skipped into eligible and produced five defects,
all of them this false positive.

Usage:  python3 scripts/check_review_placement.py        # exit 1 if defects
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "topic_reviews_md"
SKIP_SECTION = ("summary", "riepilogo", "key points", "what this", "what these",
                "cosa copre", "cosa fanno", "how to", "come ", "the map", "la mappa")


# Rule 6: our own diagrams must declare their size.
#
# app.js sizes a standalone figure from REVIEW_FIG_CFG['single'], which is tuned
# for SIGN pictures: a sign is compact and its meaning survives at 150 px. A
# concept diagram is wide and carries small labels, so the same default renders
# it too small to read at a glance, which is the only reason it exists. Measured
# on 2026-09-16, when the maintainer asked for a check of the older figures: the
# containment diagram came out 190x118 and the green wave 303x94, with the
# traffic-light colors that are the whole point of that animation reduced to
# dark specks. The !xl hint gives 452x281 and 480x149 instead.
#
# So a review_media figure without a hint is a defect by construction, which is
# why the hint is required and not merely advised. Use !xl for a wide diagram
# and !big for an object whose detail must stay legible, such as the parking
# disc, whose dial is the reason the figure is there.


def media_figs_without_hint(text):
    out = []
    for line in text.splitlines():
        if not line.strip().startswith("!["):
            continue
        for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip()):
            alt, src = m.group(1), m.group(2)
            if "review_media/" in src and not re.match(r"^!(?:xl|big|small)\s", alt):
                out.append(src.rsplit("/", 1)[-1])
    return out


def is_sign_image(line):
    """A rule-13 image: a sign picture, not one of our own concept diagrams."""
    t = line.strip()
    return t.startswith("![") and "domandeb_images/" in t


def sections(text):
    """[(name, [lines])] for one language part."""
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("## "):
            cur = (line[3:].strip(), [])
            out.append(cur)
        elif cur is not None:
            cur[1].append(line)
    return out


# Generic words that appear all over a review and mean nothing as a subject.
STOPWORDS = {"white", "yellow", "blue", "red", "green", "black", "right", "left",
             "bianco", "giallo", "blu", "rosso", "verde", "nero", "destra",
             "sinistra", "true", "false", "vero", "falso", "not", "never",
             "always", "sempre", "mai", "tutti", "tutte", "everyone", "all"}


def key_terms(line):
    """What a bullet is *about*: its italic Italian term(s), or a multi-word
    bold lead-in. Single generic words are ignored — matching on 'yellow' or
    'right' produced false alarms that buried the real defect."""
    terms = set()
    for t in re.findall(r"\*([a-zà-ù][a-zà-ù' ]{4,30})\*", line):   # italic Italian
        terms.add(t.strip().lower())
    for t in re.findall(r"\*\*([^*]{4,40})\*\*", line):            # bold lead-in
        t = t.strip().rstrip(".:").lower()
        if " " in t:                                                # multi-word only
            terms.add(t)
    return {t for t in terms if t not in STOPWORDS and len(t) > 4}


def inline_image_defects():
    """Rule 16: an image line carries images only. Prose on the same line as an
    image renders as literal Markdown, and it also puts the explanation beside
    the picture instead of after it. Split it into its own paragraph."""
    out = []
    for f in sorted(MD.glob("[0-9]*.md")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            s = line.strip()
            if not s.startswith("!["):
                continue
            rest = re.sub(r"!\[[^\]]*\]\([^)]*\)\s*", "", s)
            if rest:
                out.append(f"{f.name}:{n}: prose on an image line: {rest[:70]}")
    return out


def image_row_defects():
    """Rule 26: at most TWO images before an explanation. That is two on one
    line, or two stacked one under the other; three or more, on one line or
    stacked (the renderer groups consecutive figure rows into one block),
    make the reader hold several pictures in mind before any is explained."""
    out = []
    for f in sorted(MD.glob("[0-9]*.md")):
        lines = f.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(lines):
            if lines[i].lstrip().startswith("!["):
                start, total, rows, j = i, 0, 0, i
                while j < len(lines) and (lines[j].lstrip().startswith("![") or not lines[j].strip()):
                    if lines[j].lstrip().startswith("!["):
                        total += len(re.findall(r"!\[", lines[j])); rows += 1
                    j += 1
                if total >= 3:
                    out.append(f"{f.name}:{start + 1}: {total} images before one explanation "
                               f"({rows} row{'s' if rows != 1 else ''})")
                i = j
            else:
                i += 1
    return out


def em_dash_defects():
    """Rule 10: an em dash gluing two thoughts together. Split into sentences."""
    out = []
    for f in sorted(MD.glob("[0-9]*.md")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if "\u2014" in line:
                out.append(f"{f.name}:{n}: {line.strip()[:90]}")
    return out


# American English is house style (glossary 2026-07-13). These are the spellings
# that actually slipped in: metre/litre and the -re, -our, -ise families the
# reviews have used by accident.
BRITISH_RE = re.compile(r"\b(metres?|litres?|kilometres?|centimetres?|millimetres?|"
                        r"colour|behaviour|neighbour|licence|tyres?|kerb|manoeuvres?)\b", re.I)


def british_defects():
    """The English half of a review, in American spelling."""
    out = []
    for f in sorted(MD.glob("[0-9]*.md")):
        text = f.read_text(encoding="utf-8")
        en = text.split("<!-- LANG: it -->")[0]
        for n, line in enumerate(en.splitlines(), 1):
            m = BRITISH_RE.search(line)
            if m:
                out.append(f"{f.name}:{n}: {m.group(0)}  in  {line.strip()[:70]}")
    return out


MANUAL_RE = re.compile(r"\b(the|our|sida) manual\b|\b(il|del|nel|dal|al) manuale\b", re.I)


def manual_defects():
    """Rule 31: the manual is an internal source; user-facing text never cites it."""
    out = []
    for f in sorted(MD.glob("[0-9]*.md")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if MANUAL_RE.search(line):
                out.append(f"{f.name}:{n}: {line.strip()[:90]}")
    return out


US_IT_RE = re.compile(r"Stati Uniti|\bUSA\b|[Aa]meric|statunitens|California|\bU\.S\.")


def us_in_italian_defects():
    """Audience asymmetry (glossary 2026-07-13): the IT half assumes a novice
    and never compares with the US. Only the EN half carries such notes."""
    out = []
    for f in sorted(MD.glob("[0-9]*.md")):
        text = f.read_text(encoding="utf-8")
        if "<!-- LANG: it -->" not in text:
            continue
        head, it = text.split("<!-- LANG: it -->", 1)
        base = head.count("\n") + 1
        for n, line in enumerate(it.splitlines(), base):
            if US_IT_RE.search(line):
                out.append(f"{f.name}:{n}: {line.strip()[:90]}")
    return out


def main():
    defects = []
    for f in sorted(MD.glob("[0-9]*.md")):
        for part in f.read_text(encoding="utf-8").split("<!-- LANG: ")[1:]:
            lang, body = part[:2], part
            secs = sections(body)
            if not any(is_sign_image(l) for _, ls in secs for l in ls):
                continue                      # no sign pictures: nothing to split
            pictured = set()
            for name, lines in secs:
                if any(is_sign_image(l) for l in lines):
                    for l in lines:
                        if l.strip().startswith("- ") or is_sign_image(l):
                            pictured |= key_terms(l)
            for name, lines in secs:
                if any(is_sign_image(l) for l in lines):
                    continue
                if any(k in name.lower() for k in SKIP_SECTION):
                    continue
                bullets = [l for l in lines if l.strip().startswith("- ")]
                if len(bullets) < 3:
                    continue
                orphans = [b for b in bullets if key_terms(b) & pictured]
                if orphans:
                    defects.append(
                        f"{f.name} [{lang}] section '{name}': "
                        f"{len(orphans)} of {len(bullets)} rule bullets name a subject "
                        f"pictured in another section")
    hintless = []
    for f in sorted(MD.glob("[0-9]*.md")):
        for part in f.read_text(encoding="utf-8").split("<!-- LANG: ")[1:]:
            for fn in media_figs_without_hint(part):
                hintless.append(f"{f.name} [{part[:2]}] {fn}")
    if hintless:
        print("Rule 6 defects (our own diagram left at the sign-sized default):")
        for h in sorted(set(hintless)):
            print("  -", h)
        print("  Add !xl for a wide diagram, or !big where detail must stay "
              "legible: ![!xl caption](review_media/....svg)")
        return 1

    if defects:
        print("Rule 13 defects (subject split from its image):")
        for d in defects:
            print("  -", d)
        print(f"\n{len(defects)} section(s) to fix: move each rule beside its image.")
        return 1
    us = us_in_italian_defects()
    if us:
        print(f"Audience defects: {len(us)} Italian line(s) compare with the US "
              f"(IT assumes a novice; US notes belong in the EN half only):")
        for d in us[:15]:
            print("  -", d)
        return 1
    brit = british_defects()
    if brit:
        print(f"British spelling: {len(brit)} line(s) in the English halves "
              f"(house style is American):")
        for d in brit[:15]:
            print("  -", d)
        return 1
    manual = manual_defects()
    if manual:
        print(f"Rule 31 defects: {len(manual)} line(s) cite the manual in review prose "
              f"(state the fact as our own):")
        for d in manual[:15]:
            print("  -", d)
        return 1
    dashes = em_dash_defects()
    if dashes:
        print(f"Rule 10 defects: {len(dashes)} em dash(es) in review prose "
              f"(split the thought into separate sentences):")
        for d in dashes[:15]:
            print("  -", d)
        if len(dashes) > 15:
            print(f"  … and {len(dashes) - 15} more")
        return 1
    rows = image_row_defects()
    if rows:
        print(f"Rule 26 defects: {len(rows)} image line(s) with three or more "
              f"images (split into rows of at most two, each followed by its "
              f"explanation):")
        for d in rows[:15]:
            print("  -", d)
        return 1
    print("\u2713 rule 26: never more than two images before an explanation")
    inline = inline_image_defects()
    if inline:
        print(f"Rule 16 defects: {len(inline)} image line(s) carrying prose "
              f"(put the text in its own paragraph AFTER the image):")
        for d in inline[:15]:
            print("  -", d)
        if len(inline) > 15:
            print(f"  … and {len(inline) - 15} more")
        return 1
    print("✓ rule 6: every review_media figure declares its size")
    print("✓ rule 13: every rule bullet sits with the image of its subject")
    print("✓ rule 10: no em dashes in review prose")
    print("✓ rule 16: image lines carry images only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
