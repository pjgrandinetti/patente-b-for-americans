#!/usr/bin/env python3
"""Diff the vFinal re-run shadow file against the frozen audit file.

Usage: python3 scripts/abridge_rerun_diff.py [card ids...]

For each card present in docs/abridged-rerun.json:
  IDENTICAL   - same partition (member-sets), same keeps, same answers
  PROTECTED   - differs, but current card carries a [ruling/final audit/4c/veto]
                annotation -> current wins unconditionally, diff shown FYI
  QUEUE       - differs on an unprotected card -> owner reconciliation needed
Never writes anything: docs/abridged-audit.json is only ever edited by hand
or by an owner-approved adoption script.
"""
import json, re, sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
audit = json.loads((REPO/'docs/abridged-audit.json').read_text())['cards']
rerun = json.loads((REPO/'docs/abridged-rerun.json').read_text())['cards']
PROT = re.compile(r'\[(ruling|final audit|4c:)')

def shape(entry):
    return sorted((g['answer'], tuple(sorted(g['members'], key=int)), g['keep'])
                  for g in entry['groups'])
def part(entry):  # partition only (ignore keeps)
    return sorted((g['answer'], tuple(sorted(g['members'], key=int)))
                  for g in entry['groups'])

ids = sys.argv[1:] or sorted(rerun, key=int)
counts = {'IDENTICAL':0,'KEEP-ONLY':0,'PROTECTED':0,'QUEUE':0}
for cid in ids:
    a, r = audit[cid], rerun[cid]
    if shape(a)==shape(r):
        counts['IDENTICAL']+=1; continue
    if part(a)==part(r):
        counts['KEEP-ONLY']+=1
        print(f"[{cid}] KEEP-ONLY: same partition, different representative(s)")
        continue
    protected = any(PROT.search(g['why_keep']) for g in a['groups'])
    tag = 'PROTECTED' if protected else 'QUEUE'
    counts[tag]+=1
    print(f"[{cid}] {tag}: partitions differ")
    sa = {m for g in a['groups'] for m in g['members']}
    for g in r['groups']:
        ms = tuple(sorted(g['members'], key=int))
        if not any(tuple(sorted(g2['members'],key=int))==ms and g2['answer']==g['answer'] for g2 in a['groups']):
            print(f"    rerun-only group [{g['concept']}] {g['answer']} {list(ms)}")
    for g in a['groups']:
        ms = tuple(sorted(g['members'], key=int))
        if not any(tuple(sorted(g2['members'],key=int))==ms and g2['answer']==g['answer'] for g2 in r['groups']):
            print(f"    audit-only group [{g['concept']}] {g['answer']} {list(ms)}")
print("\nsummary:", counts, f" cards compared: {len(ids)}")
