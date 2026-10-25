# Verifying memory aids

Each item is a memory aid drafted for an Italian word in a driving-test
vocabulary, for American learners at B1. `cls` is `false` (false friend, the
aid starts "Not ...") or `new` (unfamiliar word). `en` is the gloss.

You are the accuracy check. For every item decide one verdict:

- `ok` — every factual claim is correct: the etymology, the English words said
  to share a root, the meaning given, and for a false friend, the English
  look-alike really does look or sound like the Italian word.
- `fix` — a claim is wrong or doubtful, or the aid misstates what the word
  means in the gloss. Supply a corrected aid that follows the same rules
  (below), or `null` if no honest aid is possible.
- `drop` — the aid is correct but does no work: it only restates the gloss, or
  the hook is so weak or strained it will not help anyone remember.

Be strict about etymology. A derivation you cannot vouch for is `fix`, with
the claim removed or replaced by a hook plainly labelled "Sounds like" or
"Picture", which makes no historical claim. Folk etymology is wrong even when
it is memorable.

Rules for a corrected aid: one or two complete sentences, at most about 30
words, plain American English, no digits, no em dashes, no exclamation marks,
no driving rules. A false-friend aid starts with `Not ` and names the English
look-alike in straight double quotes. Italian words appear plainly.

Write a JSON array to the output path you are given, one object per input
item, in input order:

`{"aid": "<the original aid text>", "verdict": "ok|fix|drop", "new": "<corrected aid>" | null, "why": "<short reason, for fix or drop>"}`

Check that the file parses. Reply with the counts per verdict and the three
most serious errors you found.
