# Reader rubric: the added-clause trap

You are reading statements from the Italian Ministry's Patente B question bank.
Each card holds several statements, marked VERO (true) or FALSO (false). Read
ONLY the FALSO statements, but use the VERO siblings on the same card: they
often state the true rule that the FALSO one distorts.

Find every FALSO statement of this exact shape:

  The statement contains a claim the Ministry marks TRUE, and it is FALSO only
  because one clause or word was ADDED to that true claim. Strike the clause
  and what is left would be a VERO statement in this bank.

The three shapes that count:

  (a) EXTENSION: a true rule is extended to a second thing.
      "La sosta, ed anche la fermata, sono vietate davanti ai cassonetti"
      (the sosta ban is real; adding the fermata makes it false).
  (b) ABSOLUTIZER: a true rule is made absolute or widened by a word such as
      sempre, in ogni caso, anche di giorno, in qualsiasi caso, a qualsiasi
      velocità, su tutte le strade, when the real rule has exceptions.
      "Il conducente deve sempre dare la precedenza ai pedoni" is NOT this
      shape unless the bank marks the same claim without "sempre" as VERO.
  (c) FALSE CONDITION OR EXCEPTION: a true duty or ban is followed by a
      condition or exception that does not exist.
      "...purché la sosta sia di brevissima durata", "...se il veicolo non
      arreca intralcio", "...salvo che di notte".

  (d) FALSE RESTRICTION OR REASON: a true claim narrowed by solo, soltanto,
      esclusivamente, unicamente, or followed by a false reason (perché, in
      quanto, poiché) or a false purpose (per ...).
      "Il segnale consente la sosta solo ai residenti" (the sign does allow
      parking; "solo ai residenti" is the invention).
      "impone di arrestarsi perché il transito è vietato" (the stop duty is
      real; the reason is false).
      Use kind "d" for these.

What does NOT count (leave these out):
  - a statement whose core claim is itself false (wrong sign meaning, wrong
    rule, invented duty);
  - a wrong NUMBER (distance, speed, age, time) swapped for the right one;
  - a negation flipped ("non è consentito" for "è consentito");
  - a wrong subject or object swapped in ("ai ciclomotori" for "agli
    autobus") unless it is added ON TOP of the true subject;
  - a statement that is false for two reasons at once.

Be strict. The test is: would a learner who knows the rule and reads only the
first two-thirds of the sentence answer VERO, and be wrong only because of
the tail? If the base claim is not one the Ministry marks VERO somewhere
(usually on the same card), it does not qualify.

Output: write a JSON file at the path you were given, an array of objects:
  {"n": "23774", "kind": "a|b|c|d", "clause": "così come la fermata",
   "base": "La sosta è vietata davanti ai cassonetti dei rifiuti urbani"}
where "clause" is the ADDED words copied VERBATIM from the statement (a
contiguous substring; if the addition is one word, that word), and "base" is
the true claim left when it is removed, in Italian. Include nothing else in
the file. Report in your final message only: how many FALSO statements you
read, how many qualify, and any statement you were unsure about (number and
one line).
