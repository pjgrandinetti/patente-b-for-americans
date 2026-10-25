#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glossary rule 39: give an idiom its word-for-word rendering.

Appends "(literally: ...)" to the English gloss of every vocabulary entry whose
term contains one of the idioms in LIT below, i.e. a phrase whose word-for-word
reading differs from its natural translation. Transparent phrases are absent
from the map on purpose: there a literal line just repeats the gloss.

Idempotent: an entry whose gloss already says "literally" is skipped, so adding
an idiom to LIT and re-running only touches the new matches.

Usage:  python3 scripts/add_literal_glosses.py [--apply]
"""
import json, re, sys

# Idiom -> word-for-word rendering. Only phrases whose literal reading is
# genuinely different from the natural translation. Transparent phrases
# (veicoli a motore, corsia di destra, limite massimo di velocita) are absent
# on purpose: there a literal line just repeats the gloss.
LIT = {
 # road furniture and places
 'passaggio a livello'        : 'passage at level',
 'passaggi a livello'         : 'passages at level',
 'passo carrabile'            : 'drivable step',
 'piazzola di sosta'          : 'little square for stopping',
 'piazzola di fermata'        : 'little square for stopping',
 'casello autostradale'       : 'little house on the highway',
 'sede ferroviaria'           : 'railway seat',
 'isola di traffico'          : 'island of traffic',
 'fondo stradale'             : 'road bottom',
 'bordo del marciapiede'      : 'edge of the foot-walk',
 'marciapiede'                : 'foot-walk',
 'strada senza uscita'        : 'road without exit',
 'ponte mobile'               : 'mobile bridge',
 'a raso'                     : 'level with the ground',
 'pista ciclabile'            : 'cyclable track',
 'piste ciclabili'            : 'cyclable tracks',
 'corsia di preselezione'     : 'preselection lane',
 'centro abitato'             : 'inhabited center',
 'centri abitati'             : 'inhabited centers',
 # movement and maneuvers
 'senso di marcia'            : 'sense of travel',
 'inversione di marcia'       : 'reversal of travel',
 'invertire il senso di marcia': 'to invert the sense of travel',
 'riprendere la marcia'       : 'to take the travel up again',
 'durante la marcia'          : 'during the travel',
 'a senso unico'              : 'at a single direction',
 'senso unico'                : 'single direction',
 'doppio senso di marcia'     : 'double direction of travel',
 'doppio senso di circolazione': 'double direction of movement',
 'doppio senso'               : 'double direction',
 'impegnare'                  : 'to engage',
 'dare la precedenza'         : 'to give precedence',
 'diritto di precedenza'      : 'right of precedence',
 'moderare la velocita'       : 'to moderate the speed',
 'alla guida'                 : 'at the driving',
 'in discesa'                 : 'in descent',
 'in salita'                  : 'in ascent',
 'in sosta'                   : 'in a stop',
 'file parallele'             : 'parallel files, that is, queues',
 'strisce di guida'           : 'driving stripes',
 'strisce pedonali'           : 'pedestrian stripes',
 'tenuta di strada'           : 'holding of the road',
 # distances and physics
 'distanza di sicurezza'      : 'safety distance',
 'spazio di frenatura'        : 'braking space',
 'spazio totale di arresto'   : 'total space of halting',
 'spazio di arresto'          : 'space of halting',
 'forza aderente'             : 'adhering force',
 'coefficiente di aderenza'   : 'coefficient of adhesion',
 # lights, signals, dashboard
 'luci abbaglianti'           : 'dazzling lights',
 'proiettori a luce abbagliante' : 'dazzling-light headlights',
 'segnalazione luminosa di pericolo' : 'luminous danger signaling',
 'segnale mobile di pericolo' : 'portable danger signal',
 'segnale mobile triangolare di pericolo' : 'portable triangular danger signal',
 'segnale triangolare mobile di pericolo' : 'triangular portable danger signal',
 'luci di posizione'          : 'position lights',
 'luce gialla fissa'          : 'fixed yellow light',
 'indicatori di direzione'    : 'direction indicators',
 'indicatore di direzione'    : 'direction indicator',
 'via libera'                 : 'free way',
 'pannello integrativo'       : 'integrative panel',
 'pannelli integrativi'       : 'integrative panels',
 'pannello distanziometrico'  : 'distance-measuring panel',
 # vehicle parts and paperwork
 'carta di circolazione'      : 'circulation card',
 'cambio di velocita'         : 'change of speed',
 'freno di stazionamento'     : 'stationing brake',
 'impianto di scarico'        : 'discharge installation',
 'gas di scarico'             : 'discharge gas',
 'organi di traino'           : 'towing organs',
 'sistemi di ritenuta'        : 'retention systems',
 'cinture di sicurezza'       : 'safety belts',
 'cintura di sicurezza'       : 'safety belt',
 'carrello appendice'         : 'appendix cart',
 'occhiali da vista'          : 'glasses for sight',
 'macchine agricole'          : 'agricultural machines',
 'macchine operatrici'        : 'operating machines',
 'macchine sgombraneve'       : 'snow-clearing machines',
 'soggetti a revisione'       : 'subject to revision',
 'revisione della patente'    : 'revision of the license',
 # people, law, first aid
 'sinistro stradale'          : 'road mishap; sinistro also means left',
 'responsabilita civile auto' : 'auto civil liability',
 'organi di polizia'          : 'organs of police',
 'posto di blocco'            : 'block post',
 'pronto soccorso'            : 'ready help',
 'corpi estranei'             : 'foreign bodies',
 'bastone bianco'             : 'white stick',
 'giorni festivi'             : 'festive days',
 'giorni lavorativi'          : 'working days',
 # fixed adverbials
 'salvo diversa segnalazione' : 'except different signaling',
 'tenere presente'            : 'to hold present',
 'tenere conto'               : 'to hold count',
 'fare attenzione'            : 'to make attention',
 'in quanto'                  : 'in how much',
 'in genere'                  : 'in kind',
 'di norma'                   : 'by norm',
 'in corrispondenza'          : 'in correspondence with',
 'lavori in corso'            : 'works in course',
}

def norm(s):
    s = s.lower()
    for a,b in [('à','a'),('è','e'),('é','e'),('ì','i'),('ò','o'),('ù','u')]:
        s = s.replace(a,b)
    return s

ART = re.compile(r"^(?:il |lo |la |i |gli |le |un |uno |una |l'|dei |degli |delle |del |dello |della |di |a |ad |da |in |su |per |con |nel |nella |nei |nelle |sul |sulla |al |alla |ai |agli |alle |dal |dalla |dall'|all'|nell'|sull'|dell')+")

def core(term):
    t = norm(term)
    prev = None
    while prev != t:
        prev = t
        t = ART.sub('', t)
    return t.strip()

path = str(__import__('pathlib').Path(__file__).resolve().parent.parent / 'public_html' / 'vocabulary.json')
v = json.load(open(path))
changed = []
# longest idiom first, so 'segnale mobile triangolare di pericolo' wins over
# 'segnale mobile di pericolo'
keys = sorted(LIT, key=len, reverse=True)

for e in v['common']:
    en = e.get('en') or ''
    if 'literal' in en.lower() or 'literal' in (e.get('note') or '').lower():
        continue
    nt = norm(e['term'])
    hit = next((k for k in keys if re.search(r'\b' + re.escape(k) + r'\b', nt)), None)
    if not hit:
        continue
    # already self-explaining: the gloss spells the idiom out itself
    if re.search(r'\b' + re.escape(hit) + r'\b', norm(en)):
        continue
    if nt.strip() == hit or core(e['term']) == hit or core(e['term']) == hit + 'e':
        add = ' (literally: %s)' % LIT[hit]
    else:
        add = ' (literally: %s = %s)' % (hit, LIT[hit])
    e['en'] = en.rstrip() + add
    changed.append((e.get('f') or 0, e['term'], e['en']))

# Hand-written, because the generated "(literally: ...)" form reads badly here.
MANUAL = {
 'in folle': 'in neutral, out of gear (folle on its own means mad)',
 'in folle e a motore spento': 'in neutral and with the engine off (folle on its own means mad)',
 'con il cambio in folle': 'with the transmission in neutral (folle on its own means mad)',
}
for e in v['common']:
    if e['term'].lower() in MANUAL and 'folle on its own' not in (e.get('en') or ''):
        e['en'] = MANUAL[e['term'].lower()]
        changed.append((e.get('f') or 0, e['term'], e['en']))

if '--apply' in sys.argv:
    json.dump(v, open(path,'w'), ensure_ascii=False, indent=1)
    open(path,'a').write('\n')

changed.sort(key=lambda x:-x[0])
print('entries touched:', len(changed))
for f,t,en in changed:
    print(f"  f={f:<4} {t}\n         {en}")
