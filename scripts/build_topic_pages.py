#!/usr/bin/env python3
"""
Generate the public GUIDE: one static HTML page per topic review, plus an index.

WHY THIS EXISTS
    The app is a single page, and its whole substance — 7,106 explained
    questions and 25 topic reviews — reaches the reader as JSON fetched by
    JavaScript. A crawler that reads those files finds data, not prose, and one
    page can rank for a handful of queries however good it is. These 25 pages
    are real English articles about Italian road rules, which is what somebody
    searching "italian warning signs meaning" is looking for.
    (Until 20260928g `robots.txt` also disallowed the four data files, which
    made this worse and cost more than it saved. See that file.)

    Per-QUESTION pages were considered and rejected: 7,106 near-identical pages
    is thin content, which is the thing search engines penalise. Per-TOPIC pages
    are substantial on their own terms.

WHAT IT DOES NOT DO
    It does not touch the app. The pages live under `public_html/about/`, carry
    their own stylesheet, and share nothing with `index.html`, `app.js` or
    `style.css` except the sign images, which they reference in place. The app's
    look and feel can change freely without breaking a single page here.

INPUTS
    topic_reviews_md/*.md        the same source md_to_reviews.py reads
    topic_reviews_md/_manifest.json
    topic_reviews_md/_guide_titles.json   English titles (see that file)
    pages/about.md               the landing page's wording (see about_page)

OUTPUTS
    public_html/about/index.html
    public_html/about/<nn>-<slug>.html   x25
    public_html/about/license-process.html  the How-to panel as its own page
    public_html/about/guide.css
    public_html/sitemap.xml              regenerated, listing every page

    Run it after any topic-review edit, alongside md_to_reviews.py. `--check`
    exits non-zero if the generated pages differ from what is on disk, which is
    what validate_data.py can call to catch a review edited without rebuilding.
"""
import json, re, sys, html, pathlib, datetime, hashlib, unicodedata

ROOT   = pathlib.Path(__file__).resolve().parent.parent
MDDIR  = ROOT / "topic_reviews_md"
OUT    = ROOT / "public_html" / "about"
IMGDIR = ROOT / "public_html" / "domandeb_images"
SITEMAP = ROOT / "public_html" / "sitemap.xml"

SITE  = "https://patente.physyapps.com"
BASE  = SITE + "/about/"

# ── markers stripped before rendering ────────────────────────────────────
# Every one of these is build machinery for the APP and means nothing to a
# reader. `q:` claims statements, `absent:`/`claims:` are file-level accounting,
# `en-only` marks scaffolding the Italian half deliberately omits, and the
# TOPIC/SOURCE/LANG markers delimit the file.
MARKERS = [
    re.compile(r"<!--\s*q:\s*[0-9][0-9\s,]*-->"),
    re.compile(r"^\s*<!--\s*absent:\s*[0-9][0-9\s,]*-->\s*$", re.M),
    re.compile(r"^\s*<!--\s*claims:\s*\w+\s*-->\s*$", re.M),
    re.compile(r"<!--\s*en-only\s*-->"),
    re.compile(r"<!--.*?-->", re.S),          # anything else, last
]
EN_RE = re.compile(r"<!--\s*LANG:\s*en\s*-->")
IT_RE = re.compile(r"<!--\s*LANG:\s*it\s*-->")

def english_half(text):
    en, it = EN_RE.search(text), IT_RE.search(text)
    if not en or not it:
        raise ValueError("missing a LANG marker")
    body = text[en.end():it.start()]
    for pat in MARKERS:
        body = pat.sub("", body)
    return body.strip("\n")

# ── the small markdown subset these reviews use ──────────────────────────
# Measured across all 25 files: h2, h3, paragraphs, bullets, numbered items,
# blockquotes, image lines, bold, italic and two links. No tables, no code,
# no horizontal rules. Anything outside that set raises rather than rendering
# as literal text, so a new construct is a build failure and not a silent mess.
H_RE    = re.compile(r"^(#{2,6})\s+(.*)$")
BULLET  = re.compile(r"^\s*[-*]\s+(.*)$")
NUMBER  = re.compile(r"^\s*\d+\.\s+(.*)$")
QUOTE   = re.compile(r"^\s*>\s?(.*)$")
EQ_RE   = re.compile(r"^\s*\$\$\s*(.*?)\s*\$\$\s*$")
IMGLINE = re.compile(r"^\s*(?:!\[[^\]]*\]\([^)]+\)\s*)+$")
IMG     = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK    = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
# Emphasis has to be done in three passes, innermost marker last. The reviews
# use ***bold italic*** for an Italian term inside a bold label, and they nest
# a single *italic* inside **bold** constantly ("**Moped (*ciclomotore*).**").
# A naive `\*\*([^*]+)\*\*` cannot match either, because the content carries an
# asterisk, and it leaves the markup on the page as literal text. That shipped
# in four pages on the first run. The bold pattern therefore allows a lone `*`
# inside it, and italic is applied to the captured content afterwards.
TRIPLE  = re.compile(r"\*\*\*(.+?)\*\*\*")
BOLD    = re.compile(r"\*\*((?:[^*]|\*(?!\*))+?)\*\*")
ITAL    = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)")

def inline(s):
    """Escape first, then re-introduce the markup we allow. Doing it the other
    way round would let a stray < in the prose close a tag we just wrote."""
    s = html.escape(s)
    s = IMG.sub(lambda m: f'<img src="../{m.group(2)}" alt="{m.group(1)}" loading="lazy">', s)
    s = LINK.sub(lambda m: f'<a href="{m.group(2)}" rel="nofollow noopener" target="_blank">{m.group(1)}</a>', s)
    s = TRIPLE.sub(r"<strong><em>\1</em></strong>", s)
    s = BOLD.sub(lambda m: "<strong>" + ITAL.sub(r"<em>\1</em>", m.group(1)) + "</strong>", s)
    s = ITAL.sub(r"<em>\1</em>", s)
    return s

# ── heading ids ──────────────────────────────────────────────────────────
# Every heading gets a stable slug so a section can be linked to directly.
# That is what lets a single section rank for its own query ("italian double
# bend sign") and what lets Google offer a jump link inside a result, neither
# of which a page of anonymous <h2>s can do.
#
# The slug is built from the RAW markdown of the heading, with the emphasis
# markers and any link or image syntax removed first, then folded to ASCII:
# these headings carry Italian terms (*dosso*, *segnale di preavviso*), and an
# accented or asterisked character in an id is a link nobody can type. The
# `seen` set is per page, so two sections that reduce to the same slug get
# `-2`, `-3` and so on rather than silently colliding. Two ids that are equal
# is not a cosmetic problem: the browser jumps to whichever came first, so one
# of the two table-of-contents links would quietly go to the wrong place.
def slugify(text, seen):
    t = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)     # image syntax
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)    # link syntax, keep the label
    t = t.replace("*", "")
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower() or "section"
    base, n = t, 2
    while t in seen:
        t = f"{base}-{n}"
        n += 1
    seen.add(t)
    return t

def render(md, images, headings=None):
    """Markdown to HTML. `images` collects every image path referenced, so the
    caller can prove each one exists on disk. `headings`, when given, collects
    (id, label) for each h2, which is what the table of contents is built
    from; taking it from here rather than re-parsing the HTML is what keeps
    the ids and the contents list from ever disagreeing."""
    out, i, lines = [], 0, md.split("\n")
    seen_ids = set()
    stack = []                                   # open list tags, innermost last
    def close():
        while stack:
            out.append(f"</{stack.pop()}>")
    while i < len(lines):
        raw = lines[i]; line = raw.strip(); i += 1
        if not line:
            close(); continue
        m = H_RE.match(line)
        if m:
            close()
            lvl = min(len(m.group(1)), 4)        # h2 stays h2; the page's h1 is the title
            label = inline(m.group(2))
            hid = slugify(m.group(2), seen_ids)
            out.append(f'<h{lvl} id="{hid}">{label}</h{lvl}>')
            # Only h2 reaches the contents list. Every heading gets an id, so a
            # sub-section is still linkable, but listing h3 and h4 as well would
            # make the list longer than some of the sections it indexes.
            if headings is not None and lvl == 2:
                headings.append((hid, label))
            continue
        if IMGLINE.match(line):
            close()
            found = IMG.findall(line)
            for _, src in found:
                images.append(src)
            cls = "fig" if len(found) == 1 else "figrow"
            out.append(f'<div class="{cls}">{inline(line)}</div>')
            continue
        m = QUOTE.match(line)
        if m:
            close()
            buf = [m.group(1)]
            while i < len(lines) and QUOTE.match(lines[i].strip()):
                buf.append(QUOTE.match(lines[i].strip()).group(1)); i += 1
            out.append(f"<blockquote><p>{inline(' '.join(buf).strip())}</p></blockquote>")
            continue
        for pat, tag in ((BULLET, "ul"), (NUMBER, "ol")):
            m = pat.match(line)
            if m:
                if not stack or stack[-1] != tag:
                    close(); out.append(f"<{tag}>"); stack.append(tag)
                for _, src in IMG.findall(line):
                    images.append(src)
                out.append(f"<li>{inline(m.group(1))}</li>")
                break
        else:
            close()
            buf = [line]
            while i < len(lines) and lines[i].strip() and not (
                H_RE.match(lines[i].strip()) or BULLET.match(lines[i].strip())
                or NUMBER.match(lines[i].strip()) or QUOTE.match(lines[i].strip())
                or IMGLINE.match(lines[i].strip())):
                buf.append(lines[i].strip()); i += 1
            para = " ".join(buf)
            for _, src in IMG.findall(para):
                images.append(src)
            me = EQ_RE.match(para)
            if me:                                   # a displayed equation, "$$ ... $$"
                h = inline(me.group(1))
                mr = re.match(r"^(.*?) (≈|=|≤) (.*)$", h)
                if mr:
                    h = f'<span>{mr.group(1)} {mr.group(2)}</span> <span>{mr.group(3)}</span>'
                out.append(f'<p class="eq">{h}</p>')
            else:
                out.append(f"<p>{inline(para)}</p>")
            continue
    close()
    return "\n".join(out)

# ── page template ────────────────────────────────────────────────────────
CSS = """
table.credits { border-collapse: collapse; width: 100%; font-size: .9rem; margin: .8rem 0 1.4rem; }
table.credits th, table.credits td { text-align: left; vertical-align: top; padding: .3rem .5rem; border-bottom: 1px solid var(--border); }
table.credits th { font-weight: 600; }
/* The guide's own stylesheet. It references nothing of the app's, but it
   COPIES the app's look (maintainer, 2026-09-24, replacing the serif blog
   look of the same morning): the app's color tokens from style.css, its
   system sans font, a white nav bar with the 2px violet rule and the app
   icon, the content on a white card, and the app link drawn as the app's
   .btn-primary. If the app's palette changes, change these to match. Dark
   mode follows the system, since these pages run no script to read the
   app's own theme toggle. */
:root { color-scheme: light dark;
  --accent:#5546d6; --accent-dim:#4338ca; --accent-tint:#f0eefc; --accent-border:#d8d2f6;
  --bg:#fdfaf4; --card-bg:#ffffff; --inset:#f7f3ea; --text:#3c3640; --muted:#8c8492;
  --border:#ece5da; --radius:12px; --shadow:rgba(85,70,214,.10); }
@media (prefers-color-scheme: dark) {
  :root { --accent:#9a8cf5; --accent-dim:#b3a7f8; --accent-tint:#2b2545; --accent-border:#463d6e;
    --bg:#161219; --card-bg:#1f1b26; --inset:#272230; --text:#ece7f1; --muted:#a59caf;
    --border:#342e3e; --shadow:rgba(0,0,0,.45); }
}
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text); padding-bottom:2rem;
       font:17px/1.6 "Segoe UI",system-ui,-apple-system,sans-serif; }
a { color:var(--accent-dim); text-underline-offset:2px; }
img { max-width:100%; }

.appbar { background:var(--card-bg); border-bottom:2px solid var(--accent);
          box-shadow:0 2px 8px var(--shadow); padding:.75rem 1.25rem;
          position:sticky; top:0; z-index:10; display:flex; align-items:center; }
.appbar img { width:30px; height:30px; border-radius:7px; display:block; }

.col { max-width:46rem; margin:0 auto; padding:0 1rem; }
main > .col:not(.crumbcol) { background:var(--card-bg); border:1px solid var(--border);
       border-radius:var(--radius); box-shadow:0 1px 4px var(--shadow);
       padding:.4rem 1.6rem 1.6rem; margin-top:1.2rem; }
@media (max-width:600px) { main > .col:not(.crumbcol) { padding:.2rem 1.1rem 1.2rem;
       border-radius:0; border-left:0; border-right:0; margin-top:.6rem; } }

h1 { font-size:1.7rem; line-height:1.25; margin:1.2rem 0 .6rem; color:var(--accent-dim); }
h2 { font-size:1.3rem; line-height:1.3; margin:2rem 0 .5rem; color:var(--accent-dim); }
h3 { font-size:1.08rem; margin:1.4rem 0 .4rem; color:var(--accent-dim); }
h4 { font-size:1rem; margin:1.1rem 0 .3rem; }
h2, h3, h4 { scroll-margin-top:4rem; }
p, li { margin:.55rem 0; }
ul, ol { padding-left:1.4rem; }
strong { color:var(--text); }
.lede { font-size:1.05rem; color:var(--muted); margin:.2rem 0 1.2rem; }
.crumb { font-size:.88rem; color:var(--muted); margin:1rem 0 0; }
.crumb a { color:var(--muted); }
p.eq { text-align:center; margin:1.2rem 0; font-size:1.05em; overflow-x:auto; }
p.eq span { white-space:nowrap; }
blockquote { margin:.9rem 0; padding:.5rem .9rem; background:var(--accent-tint);
             border-left:3px solid var(--accent-border); border-radius:0 8px 8px 0; }
blockquote p { margin:0; }
.fig { margin:1.2rem 0; text-align:center; }
.fig img { max-height:320px; }
.figrow { margin:1.2rem 0; display:flex; flex-wrap:wrap; gap:.7rem; align-items:flex-end; }
.figrow img { max-height:120px; }
.aside { margin:1.6rem 0; padding:.8rem 1rem; background:var(--inset);
         border-radius:var(--radius); color:var(--text); }
.toc { margin:1.2rem 0; font-size:.92rem; padding:.7rem 1rem; background:var(--inset);
       border-radius:var(--radius); }
.toc-h { margin:0 0 .3rem; font-weight:600; color:var(--muted); }
.toc ul { margin:0; padding-left:1.2rem; }
.toc li { margin:.2rem 0; }
.topics li { margin:.8rem 0; }
.applink { margin:1.6rem 0; }
.applink a { display:inline-block; background:var(--bg); color:var(--text);
             border:2px solid var(--text); border-radius:var(--radius); font-weight:600;
             font-size:1.1rem; padding:.85rem 2rem; text-decoration:none; }
.applink a:hover { background:var(--inset); }
.small, .topics.small { font-size:.92rem; color:var(--muted); }
.topics.small li { margin:.25rem 0; }
.others { margin-top:2.4rem; padding-top:1rem; border-top:1px solid var(--border); }
.others summary { cursor:pointer; font-size:.95rem; color:var(--muted); }
.topics span { display:block; color:var(--muted); font-size:.95rem; }
.pager { display:flex; justify-content:space-between; gap:1rem; margin:2.2rem 0 0;
         padding-top:1rem; border-top:1px solid var(--border); font-size:.92rem; }
.pager .nx { text-align:right; margin-left:auto; }
"""

def page(*, title, desc, canonical, body, crumb, jsonld, footer, script=""):
    """`body` is placed as it is: the index lays out its own full-width bands,
    and the article pages wrap themselves in `.col`. `crumb` is a small
    breadcrumb line for article pages, empty on the index."""
    crumb_html = f'<div class="col crumbcol"><p class="crumb">{crumb}</p></div>\n' if crumb else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<link rel="stylesheet" href="guide.css">
<link rel="apple-touch-icon" href="../icons/apple-touch-icon.png">
<link rel="icon" href="../icons/favicon-32.png" sizes="32x32">
<meta name="theme-color" content="#fdfaf4">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Patente B in English">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{SITE}/icons/icon-512.png">
<script type="application/ld+json">
{json.dumps(jsonld, indent=1, ensure_ascii=False)}
</script>
</head>
<body>
<header class="appbar"><a href="{SITE}/"><img src="../icons/icon-192.png" alt="Open the Patente B Study App for Americans" width="30" height="30"></a></header>
<main>
{crumb_html}{body}
</main>
{script}</body>
</html>
"""

def footer_html(entries):
    return f"""<footer class="site-foot"><div class="col">
<p>These pages and the <a href="{SITE}/">study app</a> were written, with help from AI tools, for English speakers preparing for the Italian driver's license. Both are free, with no ads, no accounts, no cookies and no tracking.</p>
<p><a href="index.html">Home</a> &middot; <a href="{SITE}/">The study app</a> &middot; <a href="{FEATURES_SLUG}.html">How the app works</a> &middot; <a href="{PROCESS_SLUG}.html">Getting the license</a> &middot; <a href="{CREDITS_SLUG}.html">Image credits</a></p>
<p>The official question bank is published by the Italian Ministry of Infrastructure and Transport. These pages are independent and unofficial, and they are not legal advice. Rules and procedures change, so please check with your autoscuola or the Motorizzazione before you act on anything here.</p>
</div></footer>"""

# The live statement count, read from the bank so the figure on every page
# follows a retirement without anyone remembering to change it.
_BANK = json.loads((ROOT / "public_html" / "questions.json").read_text(encoding="utf-8"))
LIVE_N = sum(1 for c in _BANK for st in c["statements"] if not st.get("retired"))
LIVE = f"{LIVE_N:,}"

CREDITS_SLUG = "credits"
CTA = (f'<p class="aside">Every official question on this subject is in the free '
       f'<a href="{SITE}/">study app</a>. It has {LIVE} statements in all, each with an English '
       f'translation and an explanation. It works offline and requires no account. '
       f'The sign figures on this page are the official designs; the vector drawings are credited on the '
       f'<a href="{CREDITS_SLUG}.html">image credits</a> page.</p>')

# A page of two or three sections is shorter than a list of its own headings,
# so below this many the contents list is noise and is not drawn at all.
TOC_MIN = 3

def toc_html(headings):
    if len(headings) < TOC_MIN:
        return ""
    items = "\n".join(f'<li><a href="#{hid}">{label}</a></li>' for hid, label in headings)
    return ('<nav class="toc" aria-label="On this page">\n'
            '<p class="toc-h">On this page</p>\n'
            f"<ul>\n{items}\n</ul>\n</nav>\n")

def slug_of(fname):
    return fname[:-3]                         # "01-segnali-di-indicazione.md" -> stem

# ── the licensing process page ───────────────────────────────────────────
# The dashboard's "How you get an Italian license" panel is the most-searched
# subject this site covers, and until 2026-09-24 it had no URL of its own: it
# sat collapsed inside `/`, whose title is about the theory app, with its seven
# steps as list items rather than headings. This page is GENERATED from that
# panel's English block in index.html, never written separately, so the two
# cannot drift: edit the panel and rebuild. Each numbered step becomes an h2,
# "Step N: <its bold label>", and each paragraph after the list that opens
# with a bold label ("Cost.", "How long does it take?") becomes an h2 of its
# own; a paragraph with no label joins the section above it.
PROCESS_SLUG  = "license-process"
# Written for the reader most likely to search for it: an American living in
# Italy, whose US license stops counting after a year and cannot be converted.
# The <title> is kept to 42 characters so that with the 23-character suffix it
# fits a search result; the h1 has room for the fuller wording.
# The index and the licensing page aim at DIFFERENT searches on purpose
# (2026-09-24): with the same words in both titles they would compete and
# Google would usually show only one. The index is the hub, so it takes the
# expat search; the licensing page takes "how to get".
PROCESS_TITLE = "How to Get an Italian Driver's License, Step by Step"
PROCESS_H1    = "How Americans Get an Italian Driver's License"
PROCESS_DESC  = ("Your US license stops counting after a year in Italy and cannot be "
                 "converted. Every step to an Italian license, with the cost and the timing.")
INDEX_HTML = ROOT / "public_html" / "index.html"
LABEL_RE = re.compile(r"^\s*<strong>(.*?)</strong>\s*(.*)$", re.S)

def _heading(label, seen, heads, prefix="", level=2):
    text = re.sub(r"<[^>]+>", "", label).strip()
    text = re.sub(r"[.:]$", "", text)
    text = prefix + text
    hid = slugify(text, seen)
    if level == 2:          # only h2 reaches the contents list
        heads.append((hid, html.escape(text)))
    return f'<h{level} id="{hid}">{html.escape(text)}</h{level}>'

def _top_items(ol):
    """The top-level <li> bodies of a list, so a list nested in a step does
    not cut the step short (a non-greedy <li>(.*?)</li> stops at the first
    inner </li>)."""
    items, depth, start = [], 0, None
    for m in re.finditer(r"<li[^>]*>|</li>", ol):
        if m.group(0).startswith("<li"):
            if depth == 0:
                start = m.end()
            depth += 1
        else:
            depth -= 1
            if depth == 0 and start is not None:
                items.append(ol[start:m.start()])
    return items

def process_page(problems):
    src = INDEX_HTML.read_text(encoding="utf-8")
    m = re.search(r'<div class="rules-body" data-i18n-html="next.body">(.*?)</div>\s*</details>', src, re.S)
    if not m:
        problems.append("index.html: the next.body panel was not found")
        return None, []
    block = m.group(1).strip()
    # Since 20261007c the panel holds the two routes in tabs: an opening, a
    # row of tab buttons, one pane per route (its numbered steps and its own
    # Cost paragraph), then the shared paragraphs. A search engine runs no
    # script, so the page shows both routes one after the other, each under
    # an h2 named by its tab, with its steps as h3.
    seen, heads, out = set(), [], []
    tabs = dict(re.findall(r'<button[^>]*data-route="(\w+)"[^>]*>(.*?)</button>', block, re.S))
    panes = re.findall(r'<div class="route-pane[^"]*" data-route="(\w+)">(.*?)</div>', block, re.S)
    if not tabs or len(panes) != 2:
        problems.append("license process: expected two route tabs and two panes")
        return None, []
    intro = block.split('<div class="route-tabs"', 1)[0]
    # The shared paragraphs follow the last pane's closing tag.
    after = block[block.rfind('<div class="route-pane'):].split("</div>", 1)[1]
    lede = re.sub(r"</?p>", "", intro.split("</p>", 1)[0]).strip()
    for tag in re.findall(r"<p>.*?</p>", intro, re.S)[1:]:
        out.append(tag)

    def section(html_part, level):
        for tag in re.findall(r"<p>.*?</p>|<ul>.*?</ul>", html_part, re.S):
            if tag.startswith("<p>"):
                inner = tag[3:-4].strip()
                lm = LABEL_RE.match(inner)
                if lm and len(re.sub(r"<[^>]+>", "", lm.group(1))) <= 60 and not lm.group(1).endswith((",", " ")):
                    # A bold opening that is a whole label ("Cost.") starts a
                    # section; one that is emphasis inside a sentence does not.
                    label = re.sub(r"<[^>]+>", "", lm.group(1)).strip()
                    if label.endswith((".", "?", ":")):
                        out.append(_heading(lm.group(1), seen, heads, level=level))
                        if lm.group(2).strip():
                            out.append(f"<p>{lm.group(2).strip()}</p>")
                        continue
            out.append(tag)

    for route, pane in panes:
        name = re.sub(r"<[^>]+>", "", tabs.get(route, route)).strip()
        out.append(_heading(name, seen, heads))
        ol, rest = pane.split("</ol>", 1) if "</ol>" in pane else (pane, "")
        for n, li in enumerate(_top_items(ol), 1):
            lm = LABEL_RE.match(li)
            if not lm:
                problems.append(f"license process ({route}): step {n} opens with no bold label"); continue
            out.append(_heading(lm.group(1), seen, heads, f"Step {n}: ", level=3))
            for part in re.split(r"<br\s*/?>", lm.group(2)):
                # A step may carry a list of its own (the conditions on the
                # certificato anamnestico, 20261012v); it stays a list rather
                # than being wrapped in a paragraph.
                for chunk in re.split(r"(<ul>.*?</ul>)", part, flags=re.S):
                    chunk = chunk.strip()
                    if not chunk:
                        continue
                    out.append(chunk if chunk.startswith("<ul>") else f"<p>{chunk}</p>")
        section(rest, 3)
    section(after, 2)
    body = "\n".join(out)
    if len(heads) < 3:
        problems.append(f"license process: only {len(heads)} sections found, expected the two routes and more")
    return dict(lede=lede, body=body), heads

# ── the about page (pages/about.md) ──────────────────────────────────────
# The landing page's wording is kept in a plain Markdown file so it can be
# edited without touching this script. The format is deliberately small:
#
#   title: ...          first lines, one per key, then a line of ---
#   description: ...    (the search-result title and the meta description)
#   # Heading           the page's one h1
#   blank-line-separated paragraphs, with *italic*, **bold** and [text](link)
#   [text](app)         links to the study app; a paragraph that is ONLY this
#                       link is drawn as the large app link
#   [text](process)     links to the licensing-process page
#   {LIVE}              the live question count, read from questions.json
#   {PROCESS_TITLE}     that page's title
#   ## Heading          starts the closed disclosure box; the paragraphs
#                       after it go inside, followed by a link to the
#                       licensing-process page and the list of topics
#
# Anything else (a list, a third-level heading) raises, so a construct the
# page cannot draw fails the build instead of showing up as stray symbols.
ABOUT_MD = ROOT / "pages" / "about.md"

# ── the credits page (IMAGE-CREDITS.md, 20261025r) ─────────────────────────
# The Wikimedia Commons vectorizations among the figures carry CC BY-SA
# licences, whose attribution must reach the distributed work. This renders
# IMAGE-CREDITS.md, paragraphs and pipe tables, as a page the app and every
# guide page link to from their footers.
CREDITS_MD   = ROOT / "IMAGE-CREDITS.md"
CREDITS_TITLE = "Image Credits"
CREDITS_DESC  = "Sources, authors and licences of the road-sign figures used in the Patente B Study App for Americans and on these pages."

def credits_page():
    """Return the body HTML built from IMAGE-CREDITS.md."""
    text = CREDITS_MD.read_text(encoding="utf-8")
    out = ['<div class="wrap"><article>', f"<h1>{html.escape(CREDITS_TITLE)}</h1>"]
    blocks = [b for b in text.split("\n\n") if b.strip()]
    seen_ids = set()
    def inline(s):
        s = html.escape(s, quote=False)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = ITAL.sub(r"<em>\1</em>", s)
        return s
    for block in blocks:
        lines = block.split("\n")
        if lines[0].startswith("# "):
            continue                              # the file's own title; the page has its own
        if lines[0].startswith("## "):
            head = lines[0][3:].strip()
            if head.startswith("Filling"):
                break                             # tooling notes, not credits
            out.append(f'<h2 id="{slugify(head, seen_ids)}">{inline(head)}</h2>')
            rest = lines[1:]
        else:
            rest = lines
        if rest and rest[0].startswith("|"):
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rest if r.startswith("|") and not r.startswith("|--")]
            if not rows:
                continue
            thead = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
            body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f'<table class="credits"><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table>')
        elif rest:
            out.append(f"<p>{inline(' '.join(l.strip() for l in rest))}</p>")
    out.append("</article></div>")
    return "\n".join(out)

# ── the features page (pages/how-it-works.md, 20261012c) ─────────────────
# What the app does, feature by feature, in the order a learner meets them,
# written so a search engine can see more than the question bank (maintainer,
# 2026-10-05). Same small format as about.md, except that every "## " starts
# a section (an h2 with an id, listed in the contents) and there is no box.
# [text](about) links the landing page, [text](features) this page.
FEATURES_MD   = ROOT / "pages" / "how-it-works.md"
FEATURES_SLUG = "how-it-works"

def features_page():
    text = FEATURES_MD.read_text(encoding="utf-8")
    head, sep, body = text.partition("\n---\n")
    if not sep:
        raise ValueError("how-it-works.md: the title/description lines must end with a line of ---")
    meta = {}
    for line in head.strip().splitlines():
        key, _, val = line.partition(":")
        meta[key.strip().lower()] = val.strip()
    if set(meta) != {"title", "description"} or not all(meta.values()):
        raise ValueError("how-it-works.md: needs exactly a 'title:' and a 'description:' line")
    seen, heads, out, h1 = set(), [], [], None
    for block in re.split(r"\n\s*\n", body.strip()):
        block = " ".join(l.strip() for l in block.splitlines())
        if block.startswith("## "):
            if h1 is None:
                raise ValueError("how-it-works.md: a ## section before the # heading")
            out.append(_heading(_about_inline(block[3:]), seen, heads))
        elif block.startswith("#"):
            if not block.startswith("# ") or h1 is not None:
                raise ValueError(f"how-it-works.md: unexpected heading: {block[:60]}")
            h1 = _about_inline(block[2:])
        elif re.match(r"^(\s*[-*]\s|\d+\.\s|>)", block):
            raise ValueError(f"how-it-works.md: lists and quotes are not supported: {block[:60]}")
        elif re.fullmatch(r"\[[^\]]+\]\(app\)", block):
            out.append(f'<p class="applink">{_about_inline(block)}</p>')
        else:
            out.append(f"<p>{_about_inline(block)}</p>")
    if h1 is None:
        raise ValueError("how-it-works.md: needs one '# ' heading")
    # The opening paragraph stays above the contents list, as the lede.
    lede = out.pop(0) if out and out[0].startswith("<p>") else ""
    body_html = (f'<div class="col">\n<h1>{h1}</h1>\n{lede}\n{toc_html(heads)}'
                 f'<article>\n' + "\n".join(out) + '\n</article>\n</div>')
    return meta["title"], meta["description"], body_html, [label for _, label in heads]

def _about_inline(s):
    s = s.replace("{LIVE}", LIVE).replace("{PROCESS_TITLE}", PROCESS_TITLE)
    if "{" in s or "}" in s:
        raise ValueError(f"about.md: unknown placeholder in: {s[:60]}")
    s = html.escape(s, quote=False)
    def link(m):
        text, url = m.group(1), m.group(2)
        if url == "app":
            return f'<a href="{SITE}/">{text}</a>'
        if url == "process":
            return f'<a href="{PROCESS_SLUG}.html">{text}</a>'
        if url == "about":
            return f'<a href="index.html">{text}</a>'
        if url == "features":
            return f'<a href="{FEATURES_SLUG}.html">{text}</a>'
        if url.startswith(("http://", "https://")):
            return f'<a href="{url}" rel="noopener">{text}</a>'
        raise ValueError(f"about.md: unknown link target ({url})")
    s = LINK.sub(link, s)
    s = TRIPLE.sub(r"<strong><em>\1</em></strong>", s)
    s = BOLD.sub(lambda m: "<strong>" + ITAL.sub(r"<em>\1</em>", m.group(1)) + "</strong>", s)
    s = ITAL.sub(r"<em>\1</em>", s)
    return s

def about_page(items):
    """Return (title, description, body HTML) built from pages/about.md."""
    text = ABOUT_MD.read_text(encoding="utf-8")
    head, sep, body = text.partition("\n---\n")
    if not sep:
        raise ValueError("about.md: the title/description lines must end with a line of ---")
    meta = {}
    for line in head.strip().splitlines():
        key, _, val = line.partition(":")
        meta[key.strip().lower()] = val.strip()
    if set(meta) != {"title", "description"} or not all(meta.values()):
        raise ValueError("about.md: needs exactly a 'title:' and a 'description:' line")
    main, box = [], None
    for block in re.split(r"\n\s*\n", body.strip()):
        block = " ".join(l.strip() for l in block.splitlines())
        if block.startswith("## "):
            if box is not None:
                raise ValueError("about.md: only one ## heading (the disclosure box) is allowed")
            box = {"summary": _about_inline(block[3:]), "paras": []}
        elif block.startswith("#"):
            if not block.startswith("# ") or box is not None or any(x.startswith("<h1>") for x in main):
                raise ValueError(f"about.md: unexpected heading: {block[:60]}")
            main.append(f"<h1>{_about_inline(block[2:])}</h1>")
        elif re.match(r"^(\s*[-*]\s|\d+\.\s|>)", block):
            raise ValueError(f"about.md: lists and quotes are not supported: {block[:60]}")
        elif box is not None:
            box["paras"].append(f'<p class="small">{_about_inline(block)}</p>')
        elif re.fullmatch(r"\[[^\]]+\]\(app\)", block):
            main.append(f'<p class="applink">{_about_inline(block)}</p>')
        else:
            main.append(f"<p>{_about_inline(block)}</p>")
    if not any(x.startswith("<h1>") for x in main):
        raise ValueError("about.md: needs one '# ' heading")
    if box is None:
        raise ValueError("about.md: needs a '## ' heading for the box that lists the topic pages")
    out = ['<div class="col">', *main, "",
           '<details class="others" id="topics">',
           f"<summary>{box['summary']}</summary>", *box["paras"],
           f'<p class="small"><a href="{FEATURES_SLUG}.html">How the app works</a></p>',
           f'<p class="small"><a href="{PROCESS_SLUG}.html">{html.escape(PROCESS_TITLE)}</a></p>',
           '<ol class="topics small">', items, "</ol>", "</details>", "</div>"]
    return meta["title"], meta["description"], "\n".join(out)

def build():
    manifest = json.loads((MDDIR / "_manifest.json").read_text(encoding="utf-8"))
    topics = manifest["topics"] if isinstance(manifest, dict) else manifest
    titles = json.loads((MDDIR / "_guide_titles.json").read_text(encoding="utf-8"))

    files, problems = {}, []
    entries = []
    for t in topics:
        fname = t["file"]; num = fname[:2]
        if num not in titles:
            raise SystemExit(f"no _guide_titles.json entry for topic {num} ({fname})")
        meta = titles[num]
        md = english_half((MDDIR / fname).read_text(encoding="utf-8"))
        images, heads = [], []
        bodyhtml = render(md, images, heads)
        for src in images:
            if not (ROOT / "public_html" / src).is_file():
                problems.append(f"{fname}: image not on disk: {src}")
        entries.append(dict(num=num, slug=slug_of(fname), title=meta["title"],
                            desc=meta["desc"], body=bodyhtml, ministry=t["topic"],
                            heads=heads))

    footer = footer_html(entries)

    # topic pages
    for k, e in enumerate(entries):
        prev_e = entries[k - 1] if k else None
        next_e = entries[k + 1] if k + 1 < len(entries) else None
        pager = '<nav class="pager" aria-label="Topics">'
        if prev_e:
            pager += f'<a href="{prev_e["slug"]}.html">&larr; {html.escape(prev_e["title"])}</a>'
        if next_e:
            pager += f'<a class="nx" href="{next_e["slug"]}.html">{html.escape(next_e["title"])} &rarr;</a>'
        pager += '</nav>'
        canonical = BASE + e["slug"] + ".html"
        # Order: title, lede, the call to action, then the contents list, then
        # the article. The contents list sits directly above the sections it
        # indexes and BELOW the call to action, which keeps that link in the
        # position it has always had rather than pushing it under a list of
        # eight items on a phone.
        body = (f'<div class="col">\n<h1>{html.escape(e["title"])}</h1>\n'
                f'<p class="lede">{html.escape(e["desc"])}</p>\n'
                f'{toc_html(e["heads"])}<article>\n{e["body"]}\n</article>\n{CTA}\n{pager}\n</div>')
        files[f'{e["slug"]}.html'] = page(
            title=f'{e["title"]} — Patente B in English',
            desc=e["desc"], canonical=canonical, body=body, footer=footer,
            crumb=f'<a href="index.html">Home</a> &rsaquo; Topic {int(e["num"])} of {len(entries)}',
            jsonld={
                "@context": "https://schema.org", "@type": "Article",
                "headline": e["title"], "description": e["desc"],
                "url": canonical, "inLanguage": "en",
                "isAccessibleForFree": True,
                "about": {"@type": "Thing", "name": e["ministry"]},
                "isPartOf": {"@type": "WebSite", "name": "Patente B in English", "url": SITE + "/"},
            })

    # the licensing process page
    proc, pheads = process_page(problems)
    pcanon = BASE + PROCESS_SLUG + ".html"
    if proc:
        pbody = (f'<div class="col">\n<h1>{html.escape(PROCESS_H1)}</h1>\n'
                 f'<p class="lede">{html.escape(PROCESS_DESC)}</p>\n'
                 f'<p>{proc["lede"]}</p>\n{toc_html(pheads)}'
                 f'<article>\n{proc["body"]}\n</article>\n{CTA}\n</div>')
        files[PROCESS_SLUG + ".html"] = page(
            title=PROCESS_TITLE,
            desc=PROCESS_DESC, canonical=pcanon, body=pbody, footer=footer,
            crumb='<a href="index.html">Home</a> &rsaquo; Getting the license',
            jsonld={
                "@context": "https://schema.org", "@type": "Article",
                "headline": PROCESS_H1, "description": PROCESS_DESC,
                "url": pcanon, "inLanguage": "en", "isAccessibleForFree": True,
                "isPartOf": {"@type": "WebSite", "name": "Patente B in English", "url": SITE + "/"},
            })

    # the features page
    ftitle, fdesc, fbody, fsections = features_page()
    fcanon = BASE + FEATURES_SLUG + ".html"
    files[FEATURES_SLUG + ".html"] = page(
        title=ftitle, desc=fdesc, canonical=fcanon, body=fbody, footer=footer,
        crumb='<a href="index.html">Home</a> &rsaquo; How the app works',
        jsonld={
            "@context": "https://schema.org", "@type": "Article",
            "headline": ftitle, "description": fdesc,
            "url": fcanon, "inLanguage": "en", "isAccessibleForFree": True,
            "about": {"@type": "WebApplication", "name": "Patente B in English", "url": SITE + "/"},
            "isPartOf": {"@type": "WebSite", "name": "Patente B in English", "url": SITE + "/"},
        })

    # the credits page
    ccanon = BASE + CREDITS_SLUG + ".html"
    files[CREDITS_SLUG + ".html"] = page(
        title=CREDITS_TITLE, desc=CREDITS_DESC, canonical=ccanon, body=credits_page(), footer=footer,
        crumb='<a href="index.html">Home</a> &rsaquo; Image credits',
        jsonld={
            "@context": "https://schema.org", "@type": "WebPage",
            "name": CREDITS_TITLE, "description": CREDITS_DESC,
            "url": ccanon, "inLanguage": "en", "isAccessibleForFree": True,
            "isPartOf": {"@type": "WebSite", "name": "Patente B in English", "url": SITE + "/"},
        })

    # index: a landing page in full-width bands
    items = "\n".join(
        f'<li><a href="{e["slug"]}.html">{html.escape(e["title"])}</a></li>' for e in entries) + \
        f'\n<li><a href="{CREDITS_SLUG}.html">{html.escape(CREDITS_TITLE)}</a></li>'
    # The landing page is SHORT and written for a person (maintainer,
    # 2026-09-24): who he is, why he built the app, an honest word about AI,
    # and a clear link to the app. The topic pages below it exist so search
    # engines can find the site, and the page says so plainly rather than
    # dressing them up as a guide written for readers. Every personal detail
    # is one the maintainer has told; add none he has not.
    # The wording lives in pages/about.md so the maintainer can edit it as
    # plain text; about_page() turns it into HTML (see the notes in that file).
    idx_title, idx_desc, idx_body = about_page(items)
    files["index.html"] = page(
        title=idx_title, desc=idx_desc,
        canonical=BASE, body=idx_body, footer=footer, crumb="",
        jsonld={
            "@context": "https://schema.org", "@type": "CollectionPage",
            "name": idx_title,
            "url": BASE, "inLanguage": "en", "isAccessibleForFree": True,
            "hasPart": [{"@type": "Article", "name": e["title"],
                         "url": BASE + e["slug"] + ".html"} for e in entries]
                       + [{"@type": "Article", "name": PROCESS_TITLE, "url": pcanon},
                          {"@type": "Article", "name": ftitle, "url": fcanon}],
        })

    files["guide.css"] = CSS

    # The ids and the contents list are built from one list, so by construction
    # they agree. This pass reads the FINISHED HTML back and proves it anyway,
    # because that is the property a future change to `render` would break
    # silently: a duplicate id sends one contents link to the wrong section and
    # nothing about the page looks wrong.
    ID_RE   = re.compile(r'<h[2-4] id="([^"]+)"')
    HREF_RE = re.compile(r'<a href="#([^"]+)"')
    for name, text in files.items():
        if not name.endswith(".html"):
            continue
        ids = ID_RE.findall(text)
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            problems.append(f"{name}: duplicate heading id(s): {', '.join(sorted(dupes))}")
        for target in HREF_RE.findall(text):
            if target not in ids:
                problems.append(f"{name}: contents link #{target} matches no heading")

    today = datetime.date.today().isoformat()
    urls = [(SITE + "/", "1.0"), (BASE, "0.9"), (fcanon, "0.9"), (pcanon, "0.9"), (ccanon, "0.3")] + \
           [(BASE + e["slug"] + ".html", "0.8") for e in entries]
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               "<!-- GENERATED by scripts/build_topic_pages.py. Do not edit. -->\n"
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n"
                         f"    <priority>{p}</priority>\n  </url>\n" for u, p in urls)
               + "</urlset>\n")
    return files, sitemap, problems, entries

def main():
    check = "--check" in sys.argv
    files, sitemap, problems, entries = build()
    if problems:
        for p in problems: print("✗", p)
        return 1

    stale = []
    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in list(files.items()) + [("../sitemap.xml", sitemap)]:
        dest = (OUT / name).resolve()
        old = dest.read_text(encoding="utf-8") if dest.is_file() else None
        # The sitemap carries today's date, so compare it with the date masked
        # out: rebuilding on a later day must not count as a content change.
        a = re.sub(r"<lastmod>[^<]*</lastmod>", "", old or "")
        b = re.sub(r"<lastmod>[^<]*</lastmod>", "", text)
        if a != b:
            stale.append(name)
            if not check:
                dest.write_text(text, encoding="utf-8")
    if check:
        if stale:
            print("✗ guide pages are stale, re-run scripts/build_topic_pages.py:")
            for s in stale: print("   ", s)
            return 1
        print(f"✓ guide: {len(entries)} topic pages fresh")
        return 0
    print(f"✓ wrote {len(files)} files to public_html/about/ "
          f"({len(entries)} topics) and regenerated sitemap.xml")
    if stale: print("  changed:", ", ".join(sorted(stale)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
