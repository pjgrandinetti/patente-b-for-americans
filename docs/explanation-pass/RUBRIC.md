# Explanation pass: is each explanation pedagogical? (2026-10-04)

The maintainer's flag on 19125 set this off. The statement was "the sign
announces possible trolleybus traffic" (FALSO), and the explanation read
"False. It warns of trams, not trolleybuses." That negates the statement and
teaches nothing: it never says what a tram is, what a trolleybus is, or why
the two are confused. Every explanation in the bank is read against the test
below, and the ones that fail are rewritten in English and Italian.

The learner reads ONE statement and its explanation, after answering. They
are an American with B1 Italian, or a native Italian. They may have answered
wrong, so the explanation is their one chance to learn the point.

## The test. An explanation FAILS if any of these holds.

1. **Bare negation or bare assertion.** It only restates the statement as
   true or false ("It warns of X, not Y", "It is not required"), without the
   rule, mechanism or definition that decides the answer.
2. **The swapped or invented element is not explained** (FALSO statements).
   If the statement names a thing that is not the right one (another sign,
   panel, marking, vehicle class, distance, authority, penalty), the
   explanation must say what the right thing is AND what the named thing
   really is or looks like, in words the learner can picture (shape, color,
   symbol), and, where the two are easily confused, why. If the named thing
   does not exist at all, say so.
3. **A term the answer turns on is left undefined.** A word a B1 learner or
   an American driver may not know (filobus, banchina, salvagente,
   semibarriere, carreggiata) gets one plain sentence. In the English half
   give the Italian word in *asterisks* once.
4. **A penalty statement does not say what really happens.** A FALSO
   statement of the shape "penalty X follows situation Y" must say what Y
   actually brings. Never write a euro amount.
5. **A membership statement** (who may pass, who is banned, which vehicles)
   does not give the list in both directions, allowed and banned.
7. **A link is missing** (maintainer, 2026-10-04). The explanation names or
   describes a sign, panel, marking or figure OTHER than the one on the
   card, `figures.json` lists that figure, and the explanation does not
   link it. The learner cannot see the other figure, so the link is how
   they get to it. If this is the ONLY failure, keep the explanation's
   wording and add the link around the words that name or describe the
   other figure, in both languages. Add a short description of the other
   figure only if the explanation has none.
6. **It is wrong or off the point**: the verdict contradicts the answer, it
   argues about another statement, or the English and Italian halves teach
   different things.

An explanation that passes all seven is LEFT ALONE. Do not rewrite for style alone, and
do not lengthen an explanation that already teaches its point. Expect to
rewrite a minority.

## How to write a rewrite

- Open with `True.` or `False.` (`Vero.` / `Falso.`), matching the answer.
  Never change which it is.
- Two to five complete sentences. One idea per sentence. No appositive that
  carries a definition: give the definition its own sentence.
- **Facts come only from** the topic review you were given, the other
  statements on the same card with their answers, the existing explanation,
  the Code text, or a figure you opened and looked at. If the fact you need
  is not there, do NOT invent it: put the statement in `problems` with what
  is missing. A wrong explanation is worse than a thin one.
- Describe a sign only from the review's own words, its caption in
  `figures.json`, or the figure itself. A .jpeg figure can be opened with
  the Read tool at `public_html/<image path>`. An .svg cannot be viewed, so
  for those rely on the review and the caption.
- **Link the other sign.** When the explanation names a sign, panel or
  marking other than the one pictured, and `figures.json` lists its figure,
  link the describing words: `[a white triangle with a black locomotive](notes:domandeb_images/4067.svg)`.
  The English and Italian halves must link the same figures. At most three
  links. Never link the card's own figure.
- Do not refer to "this card", "the other statements", "the false variant",
  "the trap answer", the exam, the quiz or the bank. The learner sees one
  statement.
- American English. "Take an exam", "license", "trailer", "truck". No
  colloquialisms, no em dashes, no exclamation marks, no rhetorical
  questions. No semicolon chains: split into sentences.
- The Italian half is natural Italian with no English in it, the same
  sentences in the same order as the English, the same facts.
- **Keep fixed sentences.** Some explanations end with a fixed sentence:
  the clause warning ("Read the whole sentence: strike «...» ..." /
  its Italian twin), the horn list ("... (a) ... (b) ... (c) when carrying
  ..."), a caution about the official answer. Keep any such closing sentence
  VERBATIM at the end of your rewrite, in both languages. The packet marks
  these statements with `keep_tail_en` / `keep_tail_it`: copy those strings
  exactly as the last sentence(s).
- Do not touch statements marked `"skip": true`.

## Output

Write one JSON file, exactly this shape:

```json
{
  "read": 251,
  "rewrites": {
    "19125": {"en": "False. ...", "it": "Falso. ...", "fails": "1,2,3"}
  },
  "problems": [
    {"number": "19999", "note": "what is wrong or missing"}
  ]
}
```

`read` is the number of statements you read (all of them). `fails` names the
test numbers the old explanation failed.
