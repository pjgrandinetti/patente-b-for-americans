#!/usr/bin/env python3
"""
Fix "bare-negation" explanations of FALSE statements across the whole bank.

Many FALSO statements have an explanation that merely negates the claim ("False.
It does not indicate a closed road.") without saying what the sign/situation
ACTUALLY is. This rewrites them to state the correct fact and why the claim is
wrong, using the card's own TRUE statements as the source of truth so no facts
are invented.

Usage (from the repo root):
    ANTHROPIC_API_KEY=sk-... python3 scripts/fix_bare_negations.py
    # dry run (no API, just list how many would change):
    python3 scripts/fix_bare_negations.py --dry-run

- Targets FALSO statements whose explanation is a main-clause negation with no
  positive contrast ("X, not Y"). Statements that already name the correct fact
  are left alone.
- Each item is given the card's VERO statements as `correct_facts`; the model
  must draw the correct answer ONLY from those (plus the statement itself).
- Resumable: progress tracked in scripts/.fixbare_progress.json (skip done).
- Saves questions.json after every batch. Bump CACHE_VERSION in sw.js when done.
"""

import json, os, re, sys, time
from pathlib import Path

ROOT           = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = ROOT / "public_html" / "questions.json"
PROGRESS_FILE  = Path(__file__).resolve().parent / ".fixbare_progress.json"
BATCH_SIZE     = 20
RETRY_DELAY    = 5
MAX_RETRIES    = 4
MODEL          = "claude-haiku-4-5"

# A main-clause negation: "it does not / is not / has no / cannot …".
MAIN_NEG = re.compile(
    r"\b(does not|do not|doesn'?t|did not|is not|isn'?t|are not|aren'?t|was not|"
    r"were not|has no\b|have no\b|cannot|can'?t|will not|won'?t|may not|must not|"
    r"need not|do nothing|does nothing)\b", re.I)
# A positive contrast that already names the correct thing: "X, not Y".
CONTRAST = re.compile(r",\s+not\b|,\s+rather than\b|\bnot\s+.+\bbut\b|\binstead of\b", re.I)


def is_bare(stmt):
    if stmt.get("answer") != "FALSO":
        return False
    e = stmt.get("explanation") or ""
    return bool(MAIN_NEG.search(e)) and not bool(CONTRAST.search(e))


def targets(questions, done):
    """Yield (qi, si, statement, correct_facts) for each bare-negation FALSO."""
    for qi, q in enumerate(questions):
        true_facts = [s.get("english_translation", "").strip()
                      for s in q["statements"] if s.get("answer") == "VERO"]
        true_facts = [t for t in true_facts if t]
        for si, s in enumerate(q["statements"]):
            if is_bare(s) and s["number"] not in done:
                yield qi, si, s, true_facts


SYSTEM_PROMPT = (
    "You improve answer explanations for Italy's Category B driving test (Patente B). "
    "Each item is a true/false statement whose answer is FALSE, and whose CURRENT "
    "explanation merely negates the claim without saying what is actually correct. "
    "You are given `correct_facts`: the TRUE statements from the same exam card, which "
    "describe what the sign or situation really is. "
    "Rewrite the explanation so it: (1) starts with 'False.'; (2) states the CORRECT fact "
    "(what it actually is or means), then (3) briefly says why the claim is wrong. "
    "Draw the correct fact ONLY from `correct_facts` and the statement itself. Do NOT invent "
    "signs, rules, numbers, colors, or categories that are not supported by `correct_facts`. "
    "If `correct_facts` is empty or does not determine the answer, write a concise, safe "
    "explanation that does not invent specifics. Keep it to one or two sentences, plain "
    "American English, no em-dashes. Also produce the Italian version, starting with 'Falso.'. "
    "Return ONLY a raw JSON array of objects {\"en\": \"...\", \"it\": \"...\"}, same length and "
    "order as the input, no markdown, no commentary."
)


def make_client(api_key):
    import anthropic
    proxy = os.environ.get("ANTHROPIC_PROXY")
    ca = os.environ.get("ANTHROPIC_CA_BUNDLE")
    if proxy or ca:
        import httpx
        hc = httpx.Client(proxy=proxy or None, verify=ca or True, trust_env=False, timeout=60)
        return anthropic.Anthropic(api_key=api_key, http_client=hc)
    return anthropic.Anthropic(api_key=api_key)


def _fix_prefix(text, word):
    m = re.match(rf"^\s*{word}\b\.?\s*", text, flags=re.IGNORECASE)
    body = text[m.end():].lstrip() if m else text.lstrip()
    return f"{word}. {body}"


def _api_call(client, items):
    import anthropic  # noqa: F401
    payload = json.dumps(items, ensure_ascii=False)
    msg = client.messages.create(model=MODEL, max_tokens=8192, system=SYSTEM_PROMPT,
                                 messages=[{"role": "user", "content": payload}])
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)


def fix_batch(client, items):
    import anthropic
    last = ""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            out = _api_call(client, items)
            if isinstance(out, list) and len(out) == len(items):
                return out
            last = f"got {len(out) if isinstance(out, list) else type(out).__name__}"
        except anthropic.RateLimitError:
            if attempt == MAX_RETRIES:
                raise
            print(f"  rate-limited, waiting {RETRY_DELAY}s…", flush=True)
            time.sleep(RETRY_DELAY); continue
        except Exception as exc:
            last = str(exc)[:100]
        time.sleep(1)
    if len(items) > 1:
        mid = len(items) // 2
        print(f"  splitting {len(items)} ({last})…", flush=True)
        return fix_batch(client, items[:mid]) + fix_batch(client, items[mid:])
    return [_api_call(client, items)[0]]


def main():
    dry = "--dry-run" in sys.argv
    questions = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    done = set(json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))) if PROGRESS_FILE.exists() else set()
    pending = list(targets(questions, done))
    total = len(pending)
    print(f"Bare-negation FALSO explanations pending: {total}")
    if dry:
        for _, _, s, facts in pending[:20]:
            print(f"  #{s['number']}: {s.get('explanation')}  | facts: {len(facts)}")
        print("(dry run — no changes written)")
        return
    if total == 0:
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: set ANTHROPIC_API_KEY before running (or use --dry-run).")
    client = make_client(api_key)
    print(f"Rewriting in batches of {BATCH_SIZE} ({MODEL})…\n", flush=True)

    n = 0
    nb = (total + BATCH_SIZE - 1) // BATCH_SIZE
    for start in range(0, total, BATCH_SIZE):
        batch = pending[start:start + BATCH_SIZE]
        items = [{"statement": s["italian_text"],
                  "english": s.get("english_translation", ""),
                  "current": s.get("explanation", ""),
                  "correct_facts": facts}
                 for (_, _, s, facts) in batch]
        print(f"Batch {start // BATCH_SIZE + 1}/{nb} ({n}/{total})…", end=" ", flush=True)
        out = fix_batch(client, items)
        for (qi, si, s, _), o in zip(batch, out):
            en = _fix_prefix(str(o.get("en", "")).strip(), "False")
            it = _fix_prefix(str(o.get("it", "")).strip(), "Falso")
            if len(en) > 6:
                questions[qi]["statements"][si]["explanation"] = en
            if len(it) > 6:
                questions[qi]["statements"][si]["explanation_it"] = it
            done.add(s["number"])
        n += len(batch)
        QUESTIONS_FILE.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")
        PROGRESS_FILE.write_text(json.dumps(sorted(done), ensure_ascii=False), encoding="utf-8")
        print(f"saved ({n}/{total})", flush=True)

    print(f"\nDone. Rewrote {n} explanations. Remember to bump CACHE_VERSION in public_html/sw.js.")


if __name__ == "__main__":
    main()
