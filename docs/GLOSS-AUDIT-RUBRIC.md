# Gloss-chain audit: rubric

You are checking whether the vocabulary glosses shown to a B1 Italian learner
lead to the meaning of the full English translation. The learner at this level
sees ONLY the Italian sentence with tappable glosses; the English sentence is
what they should arrive at.

For EVERY statement in the batch file:
1. Read IT (the Italian).
2. Read GLOSSES in order. Each is `surface text = gloss`, exactly what the app
   shows when the learner taps that span. Assume the learner knows B1 Italian
   grammar and function words but relies on the glosses for vocabulary.
3. Read EN. Ask: assembling the glosses in order, would the learner reach THIS
   meaning, including the polarity (must/may/forbidden), the subject, and any
   condition? Minor awkwardness is fine. Report a FAILURE only when the
   glosses would lead to a different meaning, leave a key idea unrecoverable,
   or give a sense of a word that is wrong for this sentence (e.g. "indicata =
   indicated/shown" where the sentence means "well-suited").

Report ONLY failures, as strict JSON: a list of objects with keys
  "number"  (string),
  "problem" (one sentence: which span misleads or is missing, and why),
  "fix"     (one of: "phrase" | "gloss"),
  "term"    (the Italian term to add or correct; for "phrase" it MUST be an
             exact substring of IT, 2 to 6 words, lowercase, no leading article
             unless the article is needed for the sense),
  "en"      (the English gloss to use: a TRANSLATION, natural American English,
             under 80 characters, no em dashes, no driving advice, no "the exam
             ..." commentary; it may end with "(literally: ...)" when the
             word-for-word reading differs).

Rules for fixes:
- Prefer "phrase": add a multi-word entry so the span glosses as a unit. Use
  "gloss" (correct an existing single-word gloss) ONLY when the current gloss
  is wrong in general, not merely in this sentence, and say so in "problem".
- One object per failure; a statement may have more than one.
- Do not propose changes to the English translation or to the Italian.
- No output other than the JSON list. If there are no failures, output [].
