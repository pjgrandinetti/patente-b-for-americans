#!/usr/bin/env python3
"""The licensing How-to as plain text, for editing outside the markup.

  python3 scripts/howto_prose.py dump     # writes docs/howto-prose-en.txt and -it.txt
  python3 scripts/howto_prose.py merge    # carries an edited docs/howto-prose-en.txt back into index.html

The English block is `next.body` in public_html/index.html, the Italian the
same key in STATIC_IT in public_html/app.js. `dump` strips the markup and
writes one line per paragraph, "- " on a step or a list item, "## " on a
route tab. `merge` splits the HTML at the same tags, diffs each segment's
text against its edited line character by character, and keeps every tag
where it was, so the links and the bold labels survive an edit made in a
plain-text editor. Only the English is merged: the Italian is written by
hand in app.js. A bold label deleted in the text file leaves an empty
<strong></strong>, which merge reports; put the label back by hand.
"""
import re, html, difflib, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'public_html', 'index.html')
APP = os.path.join(ROOT, 'public_html', 'app.js')
EN = os.path.join(ROOT, 'docs', 'howto-prose-en.txt')
IT = os.path.join(ROOT, 'docs', 'howto-prose-it.txt')
BOUND = re.compile(r'(<ol[^>]*>|</ol>|<ul>|</ul>|<li[^>]*>|</li>|<br\s*/?>|</p>|<p>|<button[^>]*>|</button>|<div[^>]*>|</div>)')


def en_block():
    s = open(INDEX, encoding='utf-8').read()
    i = s.index('data-i18n-html="next.body"')
    i = s.index('>', i) + 1
    j = s.index('</details>', i)
    return s, i, j


def it_block():
    a = open(APP, encoding='utf-8').read()
    i = a.index("'next.body':")
    out = []
    for ln in a[i:i + 80000].split('\n'):
        out.append(ln)
        if len(out) > 2 and not ln.rstrip().endswith("' +"):
            break
    t = '\n'.join(out[1:]).strip()
    t = re.sub(r"'\s*\+\s*\n\s*'", '', t)
    assert t.startswith("'") and t.endswith("',"), 'the Italian block is not where this script expects it'
    return t[1:-2]


def to_text(t):
    t = re.sub(r'<ol[^>]*>|</ol>|<ul>|</ul>', '\n', t)
    t = re.sub(r'<li[^>]*>', '\n- ', t)
    t = re.sub(r'</li>', '\n', t)
    t = re.sub(r'<br\s*/?>', '\n\n', t)
    t = re.sub(r'</p>', '\n\n', t)
    t = re.sub(r'<button[^>]*>(.*?)</button>', r'\n\n## \1\n', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n ', '\n', t)
    t = re.sub(r'([.!?])(If you are considering|Se pensi)', r'\1\n\n\2', t)
    t = re.sub(r'\n{3,}', '\n\n', t).strip()
    return t + '\n'


def dump():
    s, i, j = en_block()
    open(EN, 'w', encoding='utf-8').write(to_text(s[i:j]))
    open(IT, 'w', encoding='utf-8').write(to_text(it_block()))
    print('wrote', os.path.relpath(EN, ROOT), os.path.relpath(IT, ROOT))


def norm(t):
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()


def strip_marker(l):
    l = l.strip()
    if l.startswith('- '):
        l = l[2:]
    if l.startswith('## '):
        l = l[3:]
    return l


def merge_segment(seg, new_text):
    items = [m.group(0) for m in re.finditer(r'<[^>]+>|.', seg, re.S)]
    cchars, cidx, prev_space = [], [], False
    for k, it in enumerate(items):
        if it.startswith('<') and len(it) > 1:
            continue
        if it.isspace():
            if prev_space or not cchars:
                continue
            cchars.append(' '); cidx.append(k); prev_space = True
        else:
            cchars.append(it); cidx.append(k); prev_space = False
    if cchars and cchars[-1] == ' ':
        cchars.pop(); cidx.pop()
    old = html.unescape(''.join(cchars))
    assert len(old) == len(cchars), 'an entity inside the text; merge by hand'
    sm = difflib.SequenceMatcher(None, old, new_text, autojunk=False)
    res, pos = [], 0

    def tags_until(end, keep_text):
        nonlocal pos
        while pos < end:
            it = items[pos]
            if keep_text or (it.startswith('<') and len(it) > 1):
                res.append(it)
            pos += 1

    for tag, a1, a2, b1, b2 in sm.get_opcodes():
        end = cidx[a2 - 1] + 1 if a2 > a1 else pos
        if tag == 'equal':
            tags_until(end, True)
        elif tag == 'delete':
            tags_until(end, False)
        elif tag == 'insert':
            res.append(new_text[b1:b2])
        else:
            start = len(res)
            tags_until(end, False)
            if len(res) > start:
                print('tags inside a replaced region, check by hand:', res[start:], repr(old[a1:a2]), '->', repr(new_text[b1:b2]), file=sys.stderr)
            res.append(new_text[b1:b2])
    tags_until(len(items), True)
    return ''.join(res)


def merge():
    s, i, j = en_block()
    parts = BOUND.split(s[i:j])
    new_lines = [l for l in open(EN, encoding='utf-8').read().split('\n') if l.strip()]
    out, li = [], 0
    for part in parts:
        if BOUND.fullmatch(part) or not norm(part):
            out.append(part); continue
        oldn = norm(part)
        cand, used = strip_marker(new_lines[li]), 1
        while True:
            ratio = difflib.SequenceMatcher(None, oldn, cand, autojunk=False).ratio()
            if ratio > 0.6 or li + used >= len(new_lines):
                break
            nxt = cand + ' ' + strip_marker(new_lines[li + used])
            if difflib.SequenceMatcher(None, oldn, nxt, autojunk=False).ratio() > ratio:
                cand, used = nxt, used + 1
            else:
                break
        if difflib.SequenceMatcher(None, oldn, cand, autojunk=False).ratio() < 0.6:
            sys.exit('no edited line matches: ' + oldn[:80])
        li += used
        out.append(merge_segment(part, cand) if oldn != cand else part)
    if li != len(new_lines):
        sys.exit('edited lines left over: %d' % (len(new_lines) - li))
    blk = ''.join(out)
    if '<strong></strong>' in blk:
        print('a bold label was deleted in the text; put it back by hand', file=sys.stderr)
    open(INDEX, 'w', encoding='utf-8').write(s[:i] + blk + s[j:])
    print('merged into', os.path.relpath(INDEX, ROOT))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    {'dump': dump, 'merge': merge}.get(cmd, lambda: sys.exit(__doc__))()
