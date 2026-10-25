# -*- coding: utf-8 -*-
"""Report blocks whose English and Italian halves split into a DIFFERENT number
of sentences, which silently kills the sentence highlight.

`reviewSentenceIndex` picks the sentence on the Italian block and reuses the
index for the English, and it only does so when both halves split the same
number of ways. When they do not, the learner lands on the right paragraph
with nothing marked inside it, and nothing anywhere says so: the build passes,
the pairing is intact, and only the highlight is gone.

The usual cause is the splitter's digit guard. It must not cut at "3.5 t" or
"0,1 kW/kg", so it never breaks after a digit, and a sentence ending in "at
24." or "outside A1." or "two years of A2." therefore welds itself to the next
one. One language ends such a sentence with a number and the other adds a word
("24 anni"), and the two counts drift apart. The fix is always in the prose:
end the sentence with a word.

Reports rather than fails, since 60 blocks across the corpus predate the check.

Usage: python3 scripts/check_review_sentences.py [NN ...]
"""
import sys
sys.path.insert(0,'scripts')
import md_to_reviews as M, review_landings as RL
import glob, re

def report(path, only_section=None):
    topic, en, it = M.parse_md(open(path,encoding='utf-8').read())
    en = M.extract_claims(en)[0]
    sync = M.review_sync(M.strip_markers(en), M.strip_markers(it))
    it_blocks=[]
    for _l,_h,lines in M._sections(M.strip_markers(it)):
        it_blocks += M._text_blocks(lines)
    bad=[]
    for _l,_h,lines in M._sections(M.strip_markers(en)):
        for b in M._text_blocks(lines):
            h=M._hash(b)
            if h not in sync['pairs']: continue
            tw=it_blocks[sync['pairs'][h]]
            na,nb=len(RL.sentences(b)),len(RL.sentences(tw))
            if na!=nb: bad.append((na,nb,b,tw))
    return bad

want = [a for a in sys.argv[1:] if a.isdigit()]
total = 0
for path in sorted(glob.glob('topic_reviews_md/[0-9]*.md')):
    nn = path.split('/')[-1][:2]
    if want and nn not in want:
        continue
    bad = report(path)
    total += len(bad)
    if not bad:
        if want:
            print(f'{nn}: both halves split alike in every block')
        continue
    print(f'{nn}: {len(bad)} block(s) whose halves split differently')
    for na, nb, b, tw in bad:
        print(f'  EN {na} vs IT {nb}: {b[:100]}')
        if want:
            for k, x in enumerate(RL.sentences(b)):
                print(f'     en{k}:', x[:88])
            for k, x in enumerate(RL.sentences(tw)):
                print(f'     it{k}:', x[:88])
    print()
print(f'total: {total} block(s); these land on the right paragraph with no sentence marked')
