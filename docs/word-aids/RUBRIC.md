# Memory aids for Italian driving-test vocabulary

The reader is an American English speaker with B1 Italian, studying for the
Italian driving theory test. Each row in your batch is one Italian word as it
appears in the official question bank, with its English gloss (`en`), its
grammar line when it is an inflected form (`gram`: lemma · form), how many
statements use it (`f`), and one example statement.

## Classify every row into exactly one class

- `b1` — a word a B1 learner of Italian already knows (strada, casa, quando,
  sempre, fermare, destra, prima, uscire). No aid.
- `cognate` — recognizable from English by its look or sound, WITH the same
  meaning in this bank (veicolo, velocità, obbligatorio, automobile). No aid. Be strict: if an American would plausibly misread it, it is
  not a cognate.
- `false` — a false friend: it looks or sounds like an English word but means
  something different here (pretendere = to demand, not to pretend;
  eventuale = possible, not eventual; ricoverare = to admit to hospital, not "recover";
  attualmente = currently). Aid required.
- `new` — unfamiliar: a B1 American learner would not know it and cannot
  connect it to English (tergicristallo, sbocco, intralcio, sporgere,
  carreggiata, banchina, pedone). Aid required whenever an honest hook exists.

The same lemma's forms (sbocco / sbocchi) get the same class and the same aid.

## Writing the aid (classes `false` and `new` only)

Purpose: make the Italian word stick. One or two complete sentences, plain
American English, textbook register.

- For `false`: start with `Not ` and name the English look-alike, then say what
  the word means, then (optionally) a hook. Example:
  `Not "pretend": pretendere means to demand or to expect as a right, like the English "pretension" to a claim.`
- For `new`: give the word's parts or origin when it is well established,
  and link to an English word from the same root when one exists. Examples:
  `From tergere (to wipe, as in detergent) and cristallo (glass): the thing that wipes the glass.`
  `From s- (out of) and bocca (mouth): the place where one road comes out onto another.`
  `Related to the English "pedestrian": both come from the Latin pes, pedis (foot).`
- ACCURACY IS REQUIRED. State only etymology you are confident of. If you are
  not sure of a derivation, do not state one. You may instead give a plainly
  labelled sound or shape hook, beginning `Sounds like` or `Picture`, which
  makes no historical claim. If there is no honest hook, set aid to null.
- No driving rules, no figures, no digits, no em dashes, no colloquialisms,
  no exclamation marks, no "you'll", no "remember that". The aid is about the
  WORD, not the law.
- Keep to at most about 30 words.
- Italian words in the aid are written plainly (no asterisks); English words
  being compared go in straight double quotes.

## Output

Write a JSON array to the output path you are given, one object per input row,
in input order:

`{"term": "...", "lemma": "...", "class": "b1|cognate|false|new", "aid": "..." | null}`

`aid` must be null for `b1` and `cognate`. Check the file parses before you
finish, and report counts per class.
