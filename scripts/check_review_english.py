#!/usr/bin/env python3
"""Plain-English guard for the topic reviews (glossary rule 41).

The notes are read by people whose English is good but not native-adjacent, and
by Italians reading the Italian half. So the register has to be plain: no
slang, no idiom that only some English speakers know, and no figure of speech
standing in for a rule. "A1 is the rung that owns the displacement cap" was the
line that started this; it told the learner nothing.

A single-word blocklist does NOT work here, and that was the first attempt:
scanning thirty suspect words returned 201 hits of which about a dozen were
real, because "its own lane", "with particular care", "lose grip", "twin
circuit" and "a pet in a suitable cage" are all ordinary English. What does
work is matching PHRASES, and requiring the figurative reading by context. Each
pattern below is tested against the whole corpus: this script must report zero
hits on a clean tree, so a pattern that fires on innocent prose is a bug in the
pattern, not a finding.

Four families, any of which fails the build:

  idiom       figures of speech and slang, including the ones that only part of
              the English-speaking world would recognize (baseball, cricket)
  persona     a rule, sign, category or exam given a personality: it owns,
              earns, wants, loves, lives, bites, wins
  exam        the notes naming the exam or the quiz; the notes teach the rule
              and the post-answer explanation names the trap. One exemption:
              a section teaching how the Ministry WORDS its statements may
              name the exam, and it must open with the fixed heading
              "**How the exam phrases it.**" / "**Come lo chiede l'esame.**"
  chat        conversational filler and asides that carry no rule
  reader      writing that treats the American reader as the foreign one,
              by naming an Italian or British part and then translating it
              into the reader's own everyday word, and, since 2026-09-23,
              the British word where the American one exists (centre, tyre,
              give way, dual carriageway, indicator, dipped beam)
  fragment    a legend in place of a sentence: "yellow = special", "130→110",
              "A = your lane". Added 2026-09-23 after a reading pass over all
              25 topics found 42 of them, every one in a summary or a caption
              where a sentence fit just as well. Alt text is not a block, so
              image captions are not scanned.

Italian patterns are checked too, since the same figures were written into the
Italian half (*vive sulla strada*, *il quiz adora*, *battere il passaggio*),
and the fragment family applies to both halves.

Usage: python3 scripts/check_review_english.py [--verbose]
"""
import glob
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import md_to_reviews as M          # noqa: E402
import review_landings as RL       # noqa: E402

# (family, pattern, what to write instead)
PATTERNS = [
    # ── persona: a rule or a sign behaving like a person ──────────────────
    ("persona", r"\b(?:rung|step|category|license|licence|sign|rule|topic|figure|number)\s+that\s+owns\b",
     "name the rule: 'A1 is the category defined by a displacement limit'"),
    ("persona", r"\bowns\s+the\s+\w+", "say what the rule is, not who owns it"),
    ("persona", r"\bearns?\s+(?:no|an?|the)\s+(?:exemption|pass|right|excuse)\b",
     "'is not exempt from', 'is not entitled to'"),
    ("persona", r"\b(?:rule|sign|limit|ban|duty|law|code)\s+(?:bites|wants|likes|loves|hates|cares|decides|knows|thinks)\b",
     "state the rule directly"),
    ("persona", r"\b(?:family|sign|rule|limit)\s+lives\s+on\b", "'stands on', 'applies on'"),
    ("persona", r"\bbites\s+hardest\b", "'is strictest'"),
    ("persona", r"\b(?:it|he|she|B|R|N)\s+(?:wins|loses)\b(?![^.]*\bpoints\b)",
     "'goes first' and 'must yield' at a junction"),
    ("persona", r"\b(?:is|are)\s+king\b", "say which rule prevails"),
    ("persona", r"\btrumps?\b", "'overrides', 'takes precedence over'"),
    ("persona", r"\b(?:sibling|cousin|brother|sister)\b",
     "name the other sign: 'the NO STOPPING sign, which carries two slashes'"),
    ("persona", r"\bil\s+fratello\b|\bla\s+sorella\b|\bil\s+cugino\b", "nomina l'altro segnale"),
    ("persona", r"\bvive\s+(?:sulla|sulle|su)\b", "'sta su', 'si applica su'"),
    ("persona", r"\b(?:regola|segnale|divieto|obbligo)\s+morde\b", "enuncia la regola"),
    ("persona", r"\bmorde\s+di\s+più\b", "'è più severa'"),
    ("persona", r"\bnon\s+guadagna\s+alcuna\b", "'non è esentato'"),

    # ── the exam named inside the notes ───────────────────────────────────
    ("exam", r"\bthe\s+(?:exam|quiz|test)\s+(?:loves|likes|adores|enjoys|favors|favours|probes|asks|tests|wants)\b",
     "drop the reference and state the fact"),
    ("exam", r"\b(?:favorite|favourite)\s+(?:absolutes|traps|trick|question)\b", "'the absolutes to watch'"),
    ("exam", r"\b(?:this\s+)?topic's\s+(?:favorite|favourite)\b", "'the ones to watch in this topic'"),
    ("exam", r"\bquirks?\s+(?:the|that)\s+(?:quiz|exam)\b", "'two particular points about'"),
    ("exam", r"\bl'esame\s+(?:gradisce|ama|adora|preferisce)\b", "elimina il riferimento all'esame"),
    ("exam", r"\bil\s+quiz\s+(?:adora|ama|gradisce|preferisce)\b", "elimina il riferimento al quiz"),
    ("exam", r"\bassoluti\s+preferiti\b", "'gli assoluti a cui fare attenzione'"),
    # The catch-all, added 2026-09-16 once the 52 narrative mentions were
    # cleared. Naming the exam inside the notes is always wrong outside the
    # reading-rule section, so these match the NOUN rather than a list of
    # verbs and every new phrasing is caught without extending the list.
    # What survives is the sense in which an exam is a THING A LICENSE NEEDS,
    # which topic 22 teaches: "CE takes its own exam", "both exams, theory and
    # practical", "a medical exam and/or a driving test". That sense never
    # takes the definite article on its own, so banning "the exam" and the
    # attributive uses separates the two cleanly.
    ("exam", r"\bthe\s+(?:Italian\s+)?exam(?:s|'s)?\b",
     "state the fact; the post-answer explanation is where a trap gets named"),
    ("exam", r"\bexam(?:'s)?\s+(?:bank|figures?|numbers?|claims?|statements?|traps?|point|questions?|wording|variant)\b",
     "state the fact; the post-answer explanation is where a trap gets named"),
    ("exam", r"\bquiz(?:zes|'s)?\b",
     "state the fact; the post-answer explanation is where a trap gets named"),
    ("exam", r"\bthe bank\s+(?:tests|marks|uses|asks|draws|swaps|trades)\b",
     "state the rule; naming the bank as an actor is the same defect"),
    # Italian: esame legitimately names the DRIVING test (esame di guida,
    # esame di teoria e di pratica, il suo esame), which topic 22 needs. What
    # is banned is the elided article, which is how the notes-as-narrator
    # forms are all written: l'esame chiede, d'esame, all'esame, nell'esame.
    # Bare *esame* survives, but only in the licensing sense, which is the one
    # that takes a modifier: esame di guida, esame di teoria e di pratica,
    # il suo esame. The narrator forms all elide the article, so the article
    # is what is banned, with the licensing phrases excepted so that
    # "non superare l'esame di guida" stays writable.
    ("exam", r"\b(?:l'|d'|all'|dell'|nell'|sull')esame\b(?!\s+(?:di\s+(?:guida|teoria|revisione)|pratico|teorico))",
     "enuncia il fatto; il tranello si nomina nella spiegazione dopo la risposta"),

    # ── idiom and slang, including region-specific figures ────────────────
    # Added 2026-09-17: "learn these by heart" shipped in a UI hint and the
    # maintainer caught it by eye. "Memorize" is the word this app already
    # uses everywhere else, and it is the one a learner reading English as a
    # second language will know.
    ("idiom", r"\b(?:know|knew|known|learn|learned|learnt|memoriz\w+)\s+(?:\w+\s+){0,3}by heart\b",
     "'memorize it' / 'memorize each one'"),
    ("idiom", r"\bgrab[- ]bag\b", "'several unrelated rules'"),
    ("idiom", r"\bunder the hood\b", "'inside the engine' or name the part"),
    ("idiom", r"\bsweet spot\b", "give the figure or the range"),
    ("idiom", r"\blow[- ]hanging fruit\b|\bdouble down\b|\bcircle back\b|\bdeep dive\b",
     "plain wording"),
    ("idiom", r"\bat the end of the day\b|\bin a nutshell\b|\bthe bottom line\b",
     "delete, then state the rule"),
    ("idiom", r"\bgame[- ]changer\b|\bno[- ]brainer\b|\bpro tip\b|\bcheat sheet\b|\bgotchas?\b",
     "plain wording"),
    ("idiom", r"\bball ?park\b|\bhome run\b|\bout of left field\b|\bthree strikes\b|\btouch base\b",
     "a baseball figure only some readers know; use plain wording"),
    ("idiom", r"\bsticky wicket\b|\binnings\b|\bknock(?:ed)? for six\b|\bon a good wicket\b",
     "a cricket figure only some readers know; use plain wording"),
    ("idiom", r"\bdon'?t let (?:the|it) \w+ fool you\b|\bfool you\b",
     "'the color alone does not identify it'"),
    ("idiom", r"\bspeed up to \"?beat\"? (?:the|it)\b", "'cross before the train'"),
    ("idiom", r"\bbattere il passaggio\b", "'passare prima del treno'"),
    ("idiom", r"\bto lean on\b", "'there is no state-by-state variation here'"),
    ("idiom", r"\b(?:ladder|rung)\s+of\s+(?:odd\s+)?(?:tens|numbers|limits)\b", "list the figures"),
    ("idiom", r"\bmissing rung\b", "'70 is not among them'"),
    ("idiom", r"\blimit ladder\b", "'the standard limits'"),
    ("idiom", r"\bscala dei limiti\b", "'i limiti ordinari'"),
    ("idiom", r"\bgradino mancante\b", "'il 70 non è tra questi'"),
    # A LADDER is the same figure as the limit ladder above, found in the
    # license topic on 2026-09-16 by the maintainer: "the license ladder",
    # "which cap belongs to which rung", "it transfers down the ladder". Each
    # one asked the reader to picture a thing instead of telling them a rule,
    # and the formal word was always available: category, limit, lower
    # categories. `rung` has no literal use anywhere in this corpus, so it is
    # matched on its own; `gradino` is NOT, because topic 07 uses it for the
    # physical step at the edge of the roadway, which is the real word.
    ("idiom", r"\b(?:licen[cs]e|category|categories|limit|speed)\s+ladders?\b",
     "name it plainly: 'the license categories', 'the standard limits'"),
    ("idiom", r"\b(?:up|down|on)\s+the\s+ladder\b",
     "'to the higher categories', 'to the lower categories'"),
    ("idiom", r"\brungs?\b", "'category', or 'limit'"),
    ("idiom", r"\bscala\s+(?:delle|dei|di)\s+(?:categorie|patenti|limiti)\b",
     "'le categorie di patente', 'i limiti ordinari'"),
    ("idiom", r"\bgradini\s+(?:alti|bassi)\b|\bgradino\s+(?:alto|basso)\b",
     "'i limiti più alti', 'i limiti più bassi'"),
    ("idiom", r"\bhinges? on\b", "'the distinction is', 'this is the central rule'"),
    ("idiom", r"\bsi giocano sul fatto\b", "'la distinzione è'"),

    # ── conversational filler and asides ─────────────────────────────────
    ("chat", r"\bthe good news is\b|\bhere'?s the (?:thing|catch|kicker)\b|\bthe catch is\b",
     "delete, then state the rule"),
    ("chat", r"\bstartles?\s+(?:american|us)\b|\bsurprises?\s+(?:american|us)\s+drivers\b",
     "state the rule without commenting on the reader"),
    ("chat", r"\bfermati un attimo su questo punto\b|\bperché la logica sorprende\b",
     "elimina l'aside e enuncia la regola"),
    ("chat", r"\byou'?re all set\b|\bheads up\b|\bkeep this in your back pocket\b", "delete"),
    # NOTE: "kind of" and "sort of" are deliberately NOT here. "the kind of
    # road", "this kind of tow" are ordinary English, and the filler sense
    # cannot be told apart by pattern. Caught in review, not by this script.
    ("chat", r"\ba (?:ton|bunch) of\b|\bpretty much\b|\bmore or less\b",
     "give the number, or 'most', or delete"),
    ("chat", r"\bsuper (?:easy|simple|important|common)\b", "'very' or delete"),

    # ── writing at the reader instead of to them ─────────────────────────
    # The English half is written FOR Americans, so the American word is the
    # word, not a translation of ours. "The brake booster (what Americans call
    # power brakes)" hands the reader a foreign term and then explains their
    # own back to them. Name the part the way they name it, and gloss the
    # ITALIAN word if anything needs glossing. Raised by the maintainer on
    # 2026-09-16.
    ("reader", r"\bwhat Americans (?:call|know|say|would call)\b",
     "use the American term as the term, and gloss the Italian one instead"),
    ("reader", r"\bwhat (?:we|you) (?:in America |in the US )?call\b",
     "name it directly"),
    ("reader", r"\bAmericans (?:call|know) (?:it|this|these|them)\b",
     "name it directly"),
    # A reference text has no author on the page. "We call the parking brake
    # the emergency brake" reads as a conversation, and it also smuggles in a
    # point of view (whose "we"?). Quoted statement wording is exempt, since
    # the Ministry writes many statements in the first person.
    ("reader", r"(?<![\"«*])\b(?:we|We|our|Our|ours)\b(?![^\"«]*[\"»])",
     "write in the third person: 'in American usage', 'the parking brake', 'a driver'"),
    # Loose physical verbs for operating a control. Note what was wrong with
    # "you never GRAB reverse gear": not that it was speech rather than
    # writing, but that no American says it at all. A driver USES or ENGAGES
    # a gear. "Grab" reaches for a control with the hand, so the one place it
    # even collocates is the parking brake, and there it is conversational and
    # still wrong for a reference text. Only verbs with no legitimate use in
    # this corpus are listed. "ditch" (the roadside ditch), "jam" (traffic
    # jam) and "dump" (dumping oil on the ground) all earn their place and are
    # deliberately absent.
    ("chat", r"\b(?:grab(?:s|bed|bing)?|yank(?:s|ed|ing)?|chuck(?:s|ed|ing)?|whack\w*)\b",
     "use the plain verb: use, engage, pull, press, select"),

    # ── British words where the American one exists ──────────────────────
    # The English half is written for Americans (glossary rule 42). "Centre",
    # "give way" and "dual carriageway" survived in topics 13, 14 and 25
    # until the 2026-09-23 reading pass, because nothing scanned for them.
    # Words this corpus uses in a legitimate sense are NOT listed: "carriageway"
    # is the app's term for *carreggiata*, "gearbox" is ordinary US automotive
    # English, and "queue" names the panel. "give way" is exempt in its
    # physical sense (a shoulder that gives way under a wheel, topic 03).
    ("reader", r"\b(?:centre|kerbs?|tyres?|colours?|metres?|kilometres?|licences?|favours?|behaviours?|signalling|manoeuvres?|windscreens?|bonnets?|motorways?|lorr(?:y|ies)|petrol|whilst|amongst|dipped\s+beams?|dual\s+carriageways?|number\s+plates?|car\s+parks?|footpaths?|turn\s+indicators?|towards)\b",
     "the American word: center, curb, tire, color, meter, license, low beam, road with two carriageways, license plate, parking lot, sidewalk, turn signal, toward"),
    ("reader", r"\b(?:give|gives|giving|gave)\s+way\b(?!\s+under)|\bsit(?:s|ting)?\s+(?:the|an?)\s+(?:exam|test)\b",
     "'yield' / 'take the exam'"),

    # ── a legend where a sentence belongs ────────────────────────────────
    # "Yellow = special; blue = paid parking", "130→110", "A = your lane".
    # A reader can decode these, and has to, which is the point: a sentence
    # is read once. The arrow is banned outright; the equals sign is banned
    # between two non-space characters, which is how every legend was
    # written and how no sentence is.
    ("fragment", r"\S\s=\s\S|→",
     "write the sentence: 'yellow marks something special', 'from 130 to 110'"),
]

SKIP_SECTION = ("the map for this topic", "la mappa dell'argomento")

# The one sanctioned exemption to the exam family, agreed 2026-09-16. A
# section whose subject IS how the Ministry words its statements has to name
# the exam to teach it, and four topics carry that device (02, 03, 04, 05).
# It is a fixed opening so the exemption cannot spread: any other block
# naming the exam still fails, and only the block that OPENS with the string
# is exempt, so a second paragraph of the same device would have to repeat it.
# The other families still apply inside the exempt block.
EXAM_SECTION = re.compile(
    r"^>?\s*\*\*(?:How the exam phrases it|Come lo chiede l'esame)\.\*\*")


def findings():
    out = []
    for f in sorted((ROOT / "topic_reviews_md").glob("[0-9]*.md")):
        topic, en, it = M.parse_md(f.read_text(encoding="utf-8"))
        en = M.extract_claims(en)[0]
        for lang, half in (("en", en), ("it", it)):
            for chain, b in RL.blocks(M.strip_markers(half)):
                if not b.strip():
                    continue
                # Typographic apostrophes would walk straight past every
                # pattern below (they are all written with the ASCII one) and
                # the corpus already contains U+2019. Normalize before
                # matching, exactly as review_landings.pick_tokens does.
                b = b.replace("\u2019", "'")
                reading_rule = bool(EXAM_SECTION.match(b.strip()))
                for family, pat, fix in PATTERNS:
                    if family == "exam" and reading_rule:
                        continue
                    # A displayed equation ("$$ ... $$") is where "=" belongs.
                    if family == "fragment" and re.match(r"^\s*\$\$.*\$\$\s*$", b.strip()):
                        continue
                    m = re.search(pat, b, re.I)
                    if m:
                        out.append((f.name[:2], lang, family, m.group(0), fix, b))
    return out


def main(argv):
    hits = findings()
    if not hits:
        print(f"✓ rule 41: plain English, {len(PATTERNS)} patterns, no hits")
        return 0
    print(f"Rule 41 defects: {len(hits)} line(s) use slang, idiom, or a figure of "
          f"speech in place of a rule:")
    for nn, lang, family, found, fix, b in hits:
        print(f"  - [{nn} {lang}] {family}: {found!r}\n      write instead: {fix}")
        if "--verbose" in argv:
            print(f"      in: {b[:160]}")
    print("\nFix the wording, or if the pattern fired on ordinary English, tighten "
          "the pattern in scripts/check_review_english.py (it must stay at zero "
          "hits on a clean tree).")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
