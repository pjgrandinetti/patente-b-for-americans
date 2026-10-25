# The bank we ship against the April 2025 publication

Our copy of the Ministry bank was extracted from `sources/DomandeB.pdf`, whose
PDF creation date is **18 January 2023**. The Ministry currently publishes the
category AB bank dated **23 April 2025**, on the Portale dell'Automobilista
notice "QUIZ PER LE PATENTI AM, B, SUPERIORI E CQC". Both files are in
`sources/` and both are gitignored.

This document records the full comparison, run on 2026-09-15, so the provenance
of our bank is dated and the next person does not have to redo it.

## Result

| Check | Outcome |
| --- | --- |
| Statements we hold | 7,147 |
| Statements in the April 2025 bank | 7,106 |
| In the 2025 bank but missing from ours | **0** |
| Answers that differ | **0** |
| Wordings that differ | **0** |
| In ours but gone from the 2025 bank | **41** |

So every statement we teach is still worded exactly as the Ministry words it,
and every answer still matches. The only change in two years and three months
is that 41 statements were withdrawn. The bank is stable, which is worth
knowing before anyone plans a re-extraction.

## Two details the comparison settled

**The digit-zero typo is still in the Ministry file.** Both publications print
statement 23949 as `riprodott0`, with a digit zero where the letter o belongs.
We store the corrected `riprodotto`, which is the sanctioned exception in
CLAUDE.md rule 1, and that correction stands: the defect is the Ministry's, not
an artifact of our 2023 extraction, so the fix must be re-applied if the bank
is ever re-extracted.

**Three of our statements carry a hyphen artifact.** 21574 stores
`turistico- alberghiere`, 24356 stores `air- bag`, and 24923 stores
`anti- shock`. In each case the word breaks across two lines in the source PDF
and the extraction kept the hyphen and added a space. Both source PDFs produce
the same artifact, so this is our text extraction rather than a Ministry
change. Statement 23329 looked like a fourth case and is not. The 2025 file
sets "E e S" so tightly that `pdftotext` reads it as "EeS", and our stored
reading is the correct one.

## A trap for whoever repeats this

In the layout extraction the answer sits at the **end of a statement's first
line**, and the rest of the statement wraps onto the lines that follow. A
parser that closes a record as soon as it sees VERO or FALSO therefore keeps
only the first line of every wrapped statement. On the first pass that reported
**5,030 wording differences**, all of them phantom. Accumulate lines until the
next statement number or the next `Quesito` heading, and strip the answer from
whichever line carries it.

## The 41 withdrawn statements, and why

The reasons below are grouped by cause. Where the cause is proved from the
Code or the amending law it is marked **proved**. Where it is the most
plausible reading of the evidence it is marked *inferred*, because the Ministry
publishes no changelog.

### The 2024 reform changed the law underneath them (proved)

Legge 177/2024 rewrote the articles these statements rest on, so the Ministry
withdrew the statements instead of rewording them.

- **24550**, new B drivers and engine power. Article 117 comma 2-bis now runs
  for the **first three years** instead of the first year, and the specific
  power cap is now **75 kW/t** where it was 55 kW/t. The statement quoted the
  old figures with the new period, which made it unanswerable. The April 2025
  bank contains **no** statement about neopatentato power limits at all.
- **24594**, **24622** and **24664**, driving after taking drugs. Article 187
  no longer requires proof of a state of impairment, so the phrase "sotto
  l'effetto di sostanze stupefacenti" no longer matches the statute, which now
  turns on having taken the substance.
- **24632**, suspension for exceeding a limit by 20 km/h. The reform reworked
  the speeding penalties, so the threshold the statement denied is no longer
  the threshold in force.

### Insurance was redefined (*inferred*)

- **24456**, **25008**, **25019** and **25020** all concern the compulsory
  liability insurance and where its obligation applies. 25008 is the clearest
  case, since it locates coverage in "aree pubbliche o aperte al pubblico",
  and the obligation no longer stops at that boundary.

### Child restraints are no longer classified by weight (*inferred*)

- **24367** says restraint systems are grouped by the child's weight, which
  describes the retired ECE R44 scheme. The i-Size standard classifies by
  height.
- **24363** went with it, from the same card.

### The bicycle-lane signs became ambiguous (*inferred*)

- **20357**, **20368**, **20376**, **20379** and **20388** each describe the
  cycle-track sign as marking a "corsia riservata alle biciclette". A *corsia
  ciclabile* has been a legally distinct thing from a *pista ciclabile* since
  2020, so calling the track sign a reserved lane no longer has one answer.

### One card looks as though it was misfiled (*inferred*)

- **Card 4143** lost all fifteen of its statements, 19960 through 19974. The
  card shows the parking-area sign, and it sat under *Segnali di divieto*,
  which is the wrong family for a sign that indicates rather than forbids.
  Nothing is lost by dropping it. The bank still holds 39 statements about
  parking signs on other cards.

### Redundant or ambiguous phrasing (*inferred*)

- **19762** and **19766**, both about motor quadricycles at a prohibition sign.
- **21915**, which said the sign tells trucks which lane they must take. Its
  neighbor 21916 survives and makes the same point by saying they may use only
  the right-hand lane.
- **22262**, on a variant card, about a panel admitting only buses.
- **22824**, on motorless vehicles keeping to the right edge.
- **23257**, one right-of-way figure statement out of a card that otherwise
  survives intact.
- **23852**, on the machines barred from the autostrada.
- **23883**, on using the emergency lane after a breakdown.
- **24481**, on the AM category and three-wheeled mopeds.
- **24545**, on a category B license towing a light trailer.

## What this means for the app

Nine or ten of the 41 are not merely unaskable, they are **out of date**, and
one of them contradicts our own teaching. Topic 22's review already states the
2024 rule correctly, three years and 75 kW/t with a 105 kW ceiling for M1 cars,
and `reference.json` carries those figures. A learner who meets 24550 is told
the answer is FALSO for a statement our own notes make look nearly true. That
is the strongest argument for excluding the withdrawn statements rather than
merely labeling them.

Nothing is lost by excluding them. The parking sign keeps 39 statements
elsewhere, 21915's point is made by 21916, and the rest are single statements
on cards that survive.

## Repeating the comparison

```sh
cd sources
pdftotext -layout "domande AB italiano 23 04 2025.pdf" /tmp/ab2025.txt
# then parse as described above and compare against public_html/questions.json
# on statement number, answer and italian_text
```

The Superiori and revisione AB files from the same notice are also in
`sources/`. The revisione AB file is a published subset, roughly six statements
per card, and every one of its 1,814 statements matches ours exactly.

## What was done about it, 2026-09-15

- The 41 statements carry `"retired": "2025-04-23"` in `questions.json` and
  are filtered at load by `dropRetiredStatements` in app.js. Cards 4143 and
  the variant 5034 disappear with them, so the app runs on 849 study cards
  and 7,106 statements. In Ministry terms that is 715 cards where we held 716,
  and the April 2025 file holds exactly those 715.
- `validate_data.py` enforces the marker, ignores retired statements in every
  later check, and fails if `abridged.json`, `review_anchors.json` or
  `reference.json` cites one. It caught six dangling citations immediately:
  20 entries in the abridged set, four per-statement anchors, and 23852 cited
  twice in the Reference access lists.
- The two Reference rows sourced only by 24550, the 75 kW/t cap and the
  105 kW ceiling, are removed. Six other rows simply lost one source and keep
  at least one.
- Four claim markers lost a withdrawn statement: 22824 in topic 13, 23852 and
  23883 in topic 21, and 24363 in topic 19, whose block had no other claimant.
- Topic 19's child-restraint bullet is rewritten. It had told the learner that
  "for the exam, the answer stays 'groups by weight'", which no statement now
  asks, and it bundled four rules into one bullet. It is now three bullets:
  approval and the capital E, the i-Size height sizing, and the taxi
  exception. The new approval bullet claims 24368.
- Topic 22 drops the superseded figures, the old one-year period and 55 kW/t.
- Topic 23 drops "in public areas or areas open to the public" from the
  insurance sentence in both languages.
- The Reference page goes from 100 numbers to 98.
- The Vocabulary loses **12 entries** that glossed a word surviving nowhere
  else: `sostanze stupefacenti`, `sotto l'effetto di`, `riferita alla tara`,
  `aperte al pubblico`, `gruppi`, `a tempo indeterminato`, `limitazione nel
  tempo`, `organizzata` and `tariffe` outright, and `la responsabilità
  civile`, `disponibili` and `statura` migrated by a `replaced_by` rule to the
  longer phrase that already covered them in surviving text. 304 further
  frequency counts were restamped. `consolidate_vocab.py` now counts over the
  live statements only, which is what made any of this visible. The hyphen
  fixes cost no gloss: the entry for `alberghiere` treats the hyphen as a word
  boundary and still matches `turistico-alberghiere`.
- Topic 17's drug content is deliberately **kept** although the bank now holds
  no statement mentioning drugs or psychotropic substances. It is safety
  material and the statements will likely return once redrafted around the
  new article 187.

## Appendix: the 41 statements in full

Each entry gives the statement number, its card, the official answer, the
Ministry's Italian, and our English translation.

### The 2024 reform changed the law underneath them

**24550** &nbsp; card 4613 &nbsp; **FALSO**

> La patente di categoria B, per i primi tre anni dal suo conseguimento, non consente la guida di autovetture aventi una potenza specifica, riferita alla tara, superiore a 55 kW/t o una potenza massima di 70 kW
>
> Category B license, for the first three years from its issue, does not permit driving motor vehicles having specific power, referred to curb weight, exceeding 55 kW/t or maximum power of 70 kW.

**24594** &nbsp; card 4617 &nbsp; **VERO**

> La revisione della patente di guida può essere disposta a seguito di guida in stato di ebbrezza o sotto l'effetto di sostanze stupefacenti
>
> Competency retest of the driving license may be ordered following driving under the influence of alcohol or under the effect of narcotic substances.

**24622** &nbsp; card 4619 &nbsp; **VERO**

> La sospensione della patente è disposta quando il conducente guida sotto l'effetto di sostanze stupefacenti
>
> Driving license suspension is ordered when the driver drives under the influence of narcotics.

**24632** &nbsp; card 4619 &nbsp; **FALSO**

> La sospensione della patente può essere disposta quando si superano di 20 km/h i limiti massimi di velocità
>
> Driving license suspension may be ordered when maximum speed limits are exceeded by 20 km/h.

**24664** &nbsp; card 4621 &nbsp; **VERO**

> Guidare sotto l'effetto di sostanze stupefacenti comporta una perdita di punti sulla patente
>
> Driving under the influence of narcotic substances results in loss of license points.

### Insurance was redefined

**24456** &nbsp; card 4605 &nbsp; **VERO**

> E' vietato utilizzare un autoveicolo sulle strade pubbliche quando il veicolo non è coperto dall'assicurazione per la responsabilità civile
>
> It is prohibited to use a motor vehicle on public roads when the vehicle is not covered by civil liability insurance.

**25008** &nbsp; card 4662 &nbsp; **VERO**

> L'assicurazione obbligatoria RCA copre i danni subiti da persone e/o cose che si trovano in aree pubbliche o aperte al pubblico
>
> Compulsory RCA insurance covers damages suffered by persons and/or things located in public areas or open to the public.

**25019** &nbsp; card 4664 &nbsp; **VERO**

> È vietato utilizzare il veicolo privo di copertura assicurativa sulle strade pubbliche
>
> It is prohibited to use a vehicle without insurance coverage on public roads.

**25020** &nbsp; card 4664 &nbsp; **VERO**

> Quando l'assicurazione per la responsabilità civile auto è scaduta di validità si incorre in una sanzione se si circola o si lascia in sosta il veicolo sulle strade pubbliche
>
> When auto liability insurance expires, a penalty is incurred if the vehicle is driven or parked on public roads.

### Child restraints are no longer classified by weight

**24363** &nbsp; card 4599 &nbsp; **VERO**

> I bambini di altezza inferiore a 1,50 metri, quando sono trasportati su una autovettura, devono essere trattenuti da sistemi di ritenuta omologati, adeguati alla loro statura e peso
>
> Children under 1.50 meters in height when transported in a motor car must be restrained by approved restraint systems appropriate to their height and weight.

**24367** &nbsp; card 4599 &nbsp; **VERO**

> I sistemi di ritenuta per bambini sono classificati in gruppi, in funzione del peso del bambino che possono accogliere
>
> Child restraint systems are classified into groups according to the weight of the child they can accommodate.

### The bicycle-lane signs became ambiguous

**20357** &nbsp; card 4178 &nbsp; **VERO**

> Il segnale raffigurato è posto in corrispondenza di una corsia riservata alle biciclette
>
> The sign shown is placed in correspondence with a lane reserved for bicycles.

**20368** &nbsp; card 4179 &nbsp; **VERO**

> Il segnale raffigurato è posto in corrispondenza della fine di una corsia riservata ai ciclisti
>
> The sign shown is placed at the end of a lane reserved for cyclists.

**20376** &nbsp; card 4180 &nbsp; **VERO**

> Il segnale raffigurato è posto in corrispondenza dell'inizio di una corsia riservata alle biciclette accanto ad un percorso pedonale
>
> The sign shown is placed at the beginning of a lane reserved for bicycles alongside a pedestrian path.

**20379** &nbsp; card 4180 &nbsp; **VERO**

> Il segnale raffigurato non consente la circolazione dei veicoli a motore
>
> The sign shown prohibits motor vehicles from entering.

**20388** &nbsp; card 4181 &nbsp; **VERO**

> Il segnale raffigurato non consente la circolazione dei veicoli a motore
>
> The sign shown prohibits motor vehicles from entering.

### Card 4143, the parking-area sign, withdrawn whole

**19960** &nbsp; card 4143 &nbsp; **VERO**

> Il segnale raffigurato indica un parcheggio autorizzato
>
> The sign shown indicates an authorized parking area.

**19961** &nbsp; card 4143 &nbsp; **VERO**

> Il segnale raffigurato indica un'area attrezzata ed organizzata per sostare a tempo indeterminato, salvo diversa indicazione
>
> The sign shown indicates an equipped, organized area where parking is allowed indefinitely, unless otherwise indicated.

**19962** &nbsp; card 4143 &nbsp; **VERO**

> Il segnale raffigurato indica un'area di parcheggio e può essere integrato con un pannello che ne indica la distanza
>
> The sign shown indicates a parking area and may be supplemented with a panel indicating its distance.

**19963** &nbsp; card 4143 &nbsp; **VERO**

> Il segnale raffigurato indica un'area di parcheggio e può essere integrato con un pannello che indica le categorie cui la stessa è riservata
>
> The sign shown indicates a parking area and may be supplemented with a panel indicating the categories to which it is reserved.

**19964** &nbsp; card 4143 &nbsp; **VERO**

> Il segnale raffigurato indica un'area di parcheggio e può essere integrato con pannello che indica le categorie di veicoli esclusi
>
> The sign shown indicates a parking area and may be supplemented with a panel indicating the categories of vehicles excluded.

**19965** &nbsp; card 4143 &nbsp; **VERO**

> Il segnale raffigurato indica un'area di parcheggio e può essere integrato con un pannello che ne indica la limitazione nel tempo
>
> The sign shown indicates a parking area and may be supplemented with a panel indicating the time limitation.

**19966** &nbsp; card 4143 &nbsp; **VERO**

> Il segnale raffigurato indica un'area di parcheggio e può essere integrato con un pannello che indica l'orario e le tariffe
>
> The sign shown indicates a parking area and may be supplemented with a panel indicating the hours and tariffs.

**19967** &nbsp; card 4143 &nbsp; **VERO**

> Il segnale raffigurato indica un'area di parcheggio e può essere integrato con un pannello indicante la disposizione dei veicoli
>
> The sign shown indicates a parking area and may be supplemented with a panel indicating the arrangement of vehicles.

**19968** &nbsp; card 4143 &nbsp; **FALSO**

> Il segnale raffigurato indica un'area di sosta con parchimetro
>
> The sign shown indicates a parking area with a parking meter.

**19969** &nbsp; card 4143 &nbsp; **FALSO**

> Il segnale raffigurato indica che il parcheggio è ammesso dalle 8.00 alle 20.00
>
> The sign shown indicates that parking is permitted from 8:00 to 20:00.

**19970** &nbsp; card 4143 &nbsp; **FALSO**

> Il segnale raffigurato indica un'area in cui è possibile la sosta al massimo per un'ora
>
> The sign shown indicates an area where parking is allowed for a maximum of one hour.

**19971** &nbsp; card 4143 &nbsp; **FALSO**

> Il segnale raffigurato indica la sosta libera, ma con divieto di fermata
>
> The sign shown indicates free parking, but with a stopping prohibition.

**19972** &nbsp; card 4143 &nbsp; **FALSO**

> Il segnale raffigurato indica un'area di parcheggio riservato ai veicoli della Polizia di Stato
>
> The sign shown indicates a parking area reserved for State Police vehicles.

**19973** &nbsp; card 4143 &nbsp; **FALSO**

> Il segnale raffigurato indica un'area di parcheggio e può essere integrato con un pannello che indica la superficie disponibile
>
> The sign shown indicates a parking area and may be supplemented with a panel indicating available surface.

**19974** &nbsp; card 4143 &nbsp; **FALSO**

> Il segnale raffigurato indica un'area di parcheggio e può essere integrato con la prescrizione di lasciare la chiave nel quadro
>
> The sign shown indicates a parking area and may be supplemented with the requirement to leave the key in the ignition.

### Redundant or ambiguous phrasing

**19762** &nbsp; card 4125 &nbsp; **VERO**

> In presenza del segnale raffigurato è consentito il transito ai quadricicli a motore
>
> Where this sign is posted, motor quadricycles are permitted to proceed.

**19766** &nbsp; card 4125 &nbsp; **FALSO**

> Il segnale raffigurato vieta il transito ai quadricicli a motore
>
> The sign shown bans motor quadricycles.

**21915** &nbsp; card 4339 &nbsp; **VERO**

> Il segnale raffigurato indica agli autocarri di massa complessiva superiore a 3,5 tonnellate quale corsia debbono percorrere
>
> The sign shown indicates to trucks with a total mass exceeding 3.5 metric tons which lane they must travel.

**22262** &nbsp; card 5034 &nbsp; **VERO**

> Il segnale in figura permette di transitare solo agli autobus
>
> With this sign, only buses may proceed.

**22824** &nbsp; card 5140 &nbsp; **VERO**

> I veicoli senza motore devono circolare il più possibile vicino al margine destro della carreggiata
>
> Motorless vehicles must travel as close as possible to the right edge of the carriageway.

**23257** &nbsp; card 4469 &nbsp; **FALSO**

> Nella situazione rappresentata in figura il veicolo G transita per primo
>
> In the situation shown in the figure, vehicle G passes first.

**23852** &nbsp; card 4537 &nbsp; **VERO**

> Sulle autostrade e strade extraurbane principali è vietata la circolazione di velocipedi, ciclomotori, motocicli di cilindrata inferiore a 150 cm3
>
> On autostrade and main extra-urban roads, bicycles, mopeds, and motorcycles with engine displacement less than 150 cc are barred.

**23883** &nbsp; card 4541 &nbsp; **VERO**

> E' consentito circolare sulle corsie per la sosta di emergenza delle autostrade e strade extraurbane principali per arrestarsi per avaria del veicolo
>
> It is permitted to drive on emergency stop lanes of autostrade and main extra-urban roads to stop due to vehicle breakdown.

**24481** &nbsp; card 4608 &nbsp; **FALSO**

> Con la patente di categoria AM si possono condurre i ciclomotori a due ruote mentre per condurre i ciclomotori a tre ruote occorre la patente A1
>
> With category AM license you can drive two-wheeled mopeds while to drive three-wheeled mopeds you need A1 license.

**24545** &nbsp; card 4613 &nbsp; **VERO**

> La patente di categoria B abilita a condurre gli autocarri di massa massima autorizzata non superiore a 3.500 chilogrammi anche se trainanti un rimorchio leggero (massa fino a 750 chilogrammi)
>
> Category B license enables driving trucks with maximum authorized mass not exceeding 3,500 kilograms even when towing a light trailer (mass up to 750 kilograms).
