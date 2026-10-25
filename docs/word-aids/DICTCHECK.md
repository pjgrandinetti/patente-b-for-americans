# Checking memory aids against dictionaries

Each item is a memory aid for an Italian word, shown to American learners of
the Italian driving test. `kind` is `ff` (false friend: the aid starts "Not"
and names an English look-alike) or `new` (unfamiliar word). `words` are the
bank's forms that carry this aid, `lemma` the dictionary form, `gloss` the
app's English meaning.

The aids were drafted by a model. Your job is to make every factual claim in
each aid rest on a DICTIONARY you actually consulted in this task, not on
memory. A claim you cannot find in a dictionary comes out.

## Sources (fetch them with the web fetch tool; do not use curl or Python)

1. English Wiktionary via kaikki.org, one HTML page per word (the .jsonl
   files arrive as unreadable binary, and en.wiktionary.org returns empty
   pages through this tool, so use this form):
   `https://kaikki.org/dictionary/Italian/meaning/<c1>/<c1c2>/<word>.html`
   where c1 is the first letter and c1c2 the first two letters, e.g.
   `https://kaikki.org/dictionary/Italian/meaning/t/te/tergicristallo.html`.
   Read the Etymology line and the senses. English words the same way under
   `/dictionary/English/meaning/...`.
2. If that has no etymology: the Treccani dictionary, `https://www.treccani.it/vocabolario/<word>/`
   (authoritative for Italian etymology; read it, never copy its wording).
3. For an English word's origin, English Wiktionary as above, or
   `https://www.etymonline.com/word/<word>`.

Look up the lemma, not an inflected form. For an aid that names parts
("From X and Y"), check the word's own etymology first; look up a part only if
the word's entry does not settle it.

## What to check in each aid

- The MEANING it gives the Italian word agrees with the dictionary senses.
- Every historical claim: the parts, the Latin or other source, and any
  statement that an English word "shares the root" or "comes from the same"
  source. Each must be stated in a dictionary entry you fetched.
- For `ff`: the English look-alike really resembles the Italian word, and the
  aid does not deny a sense the Italian word really has (say "here" or "not
  only" where the Italian also carries the English sense).
- A "Sounds like" hook must actually sound like it: check the IPA.
  A "Picture" hook makes no claim, so only check it is not misleading.

## Verdict for each item

- `verified`: every claim is supported. Give the source URLs.
- `revised`: some claim was unsupported or wrong. Rewrite the aid keeping
  only supported claims (a supported etymology, or an honestly labelled
  "Sounds like" / "Picture" hook with no historical claim). Give the URLs.
- `drop`: nothing supportable and useful is left.

Rules for a rewritten aid: one or two complete sentences, at most about 30
words, plain American English, no digits, no em dashes, no exclamation marks,
no driving rules. A false-friend aid starts with `Not ` and names the English
look-alike in straight double quotes. Write your own words; never copy a
dictionary's sentence.

## Pace

The sites rate-limit. Fetch one page at a time, never in parallel, and if
a fetch returns HTTP 429, wait a minute or two and try again rather than
stopping; keep going until every item is checked. Only if a site refuses for
more than twenty minutes, mark the remaining items `unchecked` and stop.

## Output

Write a JSON array to the path you are given, one object per input item, in
input order:

`{"id": <id>, "verdict": "verified|revised|drop", "aid": "<final aid text, or null for drop>", "sources": ["<url>", ...], "note": "<what was unsupported or changed, if anything>"}`

Every `verified` and `revised` item must list at least one URL you actually
fetched. Check the file parses. Reply with the counts per verdict and the
most serious corrections.
