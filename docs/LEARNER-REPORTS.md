# Learner reports

What people who have actually taken the theory exam say about preparing for it,
and what each account changes here. One section per report.

The source documents are copyrighted by their authors, so they live in
`private/learner-reports/`, which is gitignored, for the reason the SIDA manual
lives there: this repo ships under CC-BY-SA and committing somebody else's
words would relicense them under our name. Everything in this file is our own
writing.

A report is one person's experience, so treat it as evidence rather than as a
finding. Where a claim can be measured against the bank, measure it before
acting on it. That is what turned the "trap words" section below from a list
somebody remembered into a table that tells us which of his words are real.

---

## 2026-09-21: passed 29/30, self-taught, B2 Italian

A long public post by an American expat, written for a Facebook group of
expats in Italy. He passed on the first attempt with 29 of
30, studied under two months with three weeks of that intensive, and used no
driving school course. His method was to learn a few high-value topics first,
then take whole practice sheets and let the misses direct his study.

He is our reader almost exactly: a non-native speaker studying alone in
English, which is who this app is built for. His account is the closest thing
we have to an outside test of the study loop's design.

### What it confirms, and none of this needs building

- **The two kinds of miss.** He sorts every uncertain question into "I did not
  understand the Italian" and "I understood it and did not know the rule", and
  he calls this the most important part of his method. That is exactly the
  Final Stretch page's two diagnosis groups, "Right in English, missed in
  Italian" against "Missed in English and Italian", and it is exactly the
  distinction the drill notes make. He arrived at it alone, by hand, with a
  notebook and a translator; the app computes it from the progress record and
  routes each kind to its own remedy. That is worth knowing because the split
  was a design decision nobody outside had ever confirmed.
- **Learn the whole bank rather than the Code.** His advice is to study the
  test itself rather than try to memorize the whole driving code, with volume
  at the end because recognition carries a large part of the exam. That is the reasoning
  in `docs/STUDY-EFFICIENCY-PLAN.md` for not shrinking the bank.
- **Per-topic practice before whole sheets.** He drills single topics until
  the signs stop being unfamiliar, then moves to full simulations. That is the
  topic grid followed by the mock exam.
- **A written explanation of every statement is the scarce thing.** He used a
  chatbot for the rules and warns that it gets these questions wrong
  surprisingly often, above all where an obscure exception is involved, so
  he had to push back on explanations constantly. Every statement here
  carries an explanation that a person wrote, a claimed paragraph in the notes
  behind it, and a cross-check against the manual. That is the answer to
  "why not just ask a chatbot", and it comes from someone who tried.
- **The readiness bar.** He would not take the exam until his sheets came
  back with no more than one wrong nearly every time, two now and then. The
  school's bar recorded in the How-to section of CLAUDE.md is an average
  under three mistakes. Our ring
  sits at 93%, about two wrong over the last five sheets, which is between the
  two and nearer his. Three independent sources now agree the bar is under
  three wrong on practice sheets, so leave the ring where it is.
- **Do not change an answer on second thoughts.** He changed one answer on
  review and it was the only one he got wrong. Worth a line somewhere, and the
  evidence is his own.

### The trap words, measured against our bank

He lists eighteen words that should make a reader slow down, on the theory
that a word making a rule more absolute is often what makes the statement
false. The list is from memory, so it was worth checking. Counting over the
7,106 live statements, against a bank that is **50.2% FALSO** overall:

| word | statements | FALSO | reading |
|---|---:|---:|---|
| unicamente | 7 | 100% | real, and absolute |
| obbligatoriamente | 6 | 100% | real, and absolute |
| mai | 12 | 92% | real, and absolute |
| qualunque | 19 | 79% | real, and absolute |
| solo | 242 | 76% | real, and common |
| purché | 61 | 74% | real |
| soltanto | 31 | 71% | real |
| qualsiasi | 27 | 70% | real |
| sempre | 82 | 65% | real |
| almeno | 67 | 60% | weak |
| alcun | 15 | 53% | no signal |
| nessun | 6 | 50% | no signal |
| anche | 241 | 43% | leans the other way |
| deve | 709 | 40% | leans the other way |
| può | 610 | 40% | leans the other way |
| salvo | 49 | 29% | leans the other way, strongly |
| tranne | 1 | — | too rare to say |
| necessariamente | 0 | — | our bank never uses it |

So nine of his words are real and five of them point the opposite way. *Salvo*
in particular marks an exception being stated correctly, which is what a true
statement looks like, and *può* and *deve* are simply the bank's two ordinary
modals. His own caution, that this is not a formula, is the right one, and the
measurement says which half of his list is worth a learner's attention.

**Topic 04 already teaches this**, in both language halves, as the "added
absolute" among three families of false statement, claimed by four statements.
What the measurement adds is that the skew is bank-wide rather than a property
of the prohibition signs. Whether to teach it outside topic 04 is an open
question and a careful one, because the useful lesson is a reading skill
("this word makes the claim absolute, so look for the exception") and not a
guessing rule ("*solo* usually means FALSO"). The second would train a learner
to pass sheets and fail the exam, and it is the sort of thing this app should
not print.

Every one of these words is already in `vocabulary.json`, so all of them
underline at the first two levels. None is in `glossary.json`, which is
correct: they are ordinary Italian, and the Glossario is for words whose
difficulty is the bank's register.

### Where he disagrees with our topic order

`TOPIC_ORDER` in app.js is already a curated teaching order rather than the
Ministry's. His order and ours agree on the opening, which is the danger signs
and then the other sign families. They differ in three places, and his
reasoning is that a topic worth learning early is one that is either
mechanical or heavily tested:

- **Worked junction examples** he puts fourth; we put them twelfth, after the
  rules of the road. His argument is that they are mechanical once you learn
  to trace each car's path, so they become the easiest points on the sheet.
  Ours is that they need the signs and the rules first. Both are defensible
  and his is worth considering, since a topic of 414 statements sitting
  twelfth is a long wait for the easiest points available.
- **Stopping and parking** he puts fifth; we put it sixteenth.
- **Licence categories** he says there is no way around learning early; we put
  that topic twenty-third.

Nothing to change on one person's account, but if the order is ever revisited,
this is the outside opinion to weigh against ours.

### What is genuinely missing here

- **A statement answered right by a guess is not learned.** He insists on
  reviewing every uncertain question, the ones answered right included,
  because a correct guess is worth nothing when the concept returns in a
  different form. Our record has no idea whether an answer was confident. A
  way to mark a statement as guessed, sending it into the drill despite being
  right, is the one idea in the post the app cannot do at all. The cost is a
  control, and the answer row is deliberately kept to three, so it would have
  to sit on the number line with the 📖 and the ↺.
- **Two exam-room details** the How-to does not mention: the screen may lock
  if you look away from it, since the station watches you; and glasses have to
  come off for the facial identification at the start, which cost him several
  minutes of confusion. Both are his account of one exam room rather than a
  published rule, so they want checking, or wording that says whose account
  they are.

### Follow-up in the same thread: English as an exam language (S.1543)

Someone replied that English will be an exam language "next year" and that it
is "going through Parliament now", with two links to senato.it. The bill is
real and the claim about next year is not supported by it.

**S.1543**, 19th legislature, *Modifiche all'articolo 116 del codice della
strada … per l'introduzione della lingua inglese come opzione per l'esame di
idoneità della patente di guida*. Communicated to the Senate presidency on
18 June 2025, first signatory Irto, sponsored by opposition senators. It would
let EU and non-EU citizens legally resident in Italy ask to take **both** the
theory and the practical exam in English. The explanatory report notes that
until 3 January 2011 the exam was available in the seven official UN
languages, and that the change to the examination procedure that year cut it
back to Italian plus French and German on request.

**Its status is committee, not passage.** Constitutional clearance came on
17 February 2026 and the Budget Commission asked for a *relazione tecnica* on
24 February 2026, which is the financial-coverage checkpoint and a common
place for a private member's bill to stop. Nothing found as of September 2026
says the Senate has voted it, and the Chamber would come after that. Treat
"next year" as the poster's optimism.

Two notes on the sourcing. Both links carry `utm_source=chatgpt.com`, so the
reply is a chatbot's summary passed on, which is worth knowing when the claim
being made is about parliamentary status. And `senato.it` does not answer a
plain fetch from here, so the status above came from search results rather
than from the committee page itself; read the page directly before acting on
this.

**What it would change here, if it ever passes.** One string, in step 4 of the
How-to and in both language faces: *"The exam is offered in Italian (with
French and German versions), never in English."* That is correct today and is
the only place the app asserts it. The app itself would not be undermined,
since the three levels already let someone study and stay in English; what
would change is which level they need to reach before booking. An official
English version of the bank would be a translation of the statements and
nothing else, with no explanation, no notes and no claims behind them.

### What to leave out

- **The failure-rate figures.** He gives about 60% as the 2025 national pass
  rate and reports a common belief that failure among foreigners runs to
  80% or more, while saying plainly that he found no Ministry data isolating
  that group. The second figure has no source and neither belongs on a screen
  a learner opens to study. If the first is ever wanted for
  `docs/american-guide.md`, source it first.
- **The exhortation.** Most of the post's length is encouragement, which is
  the right register for a Facebook post and the wrong one for this app's
  screens.
