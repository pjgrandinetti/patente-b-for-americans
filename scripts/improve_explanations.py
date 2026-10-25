#!/usr/bin/env python3
"""
Improve the explanations of FALSE statements that hinge on a single absolute /
operative word (sempre, mai, solo, tutti, qualsiasi, anche, ...), so the
explanation names the trick word and states the real rule instead of merely
negating the sentence.

It does NOT invent facts: each explanation is rewritten *from the current,
correct explanation*, so the factual content is preserved — only the pedagogy
(naming the operative word + the rule) is improved. Both the English
`explanation` and the Italian `explanation_it` are regenerated together.

Usage (from the repo root):
    ANTHROPIC_API_KEY=sk-... python3 scripts/improve_explanations.py

- Targets FALSO statements whose Italian text contains an absolute word.
- Resumable: progress is tracked in scripts/.improve_progress.json (skip done).
- Saves questions.json after every batch. Bump CACHE_VERSION in sw.js when done.
"""

import json, os, re, sys, time
from pathlib import Path

import anthropic

ROOT           = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = ROOT / "public_html" / "questions.json"
PROGRESS_FILE  = Path(__file__).resolve().parent / ".improve_progress.json"
BATCH_SIZE     = 25
RETRY_DELAY    = 5
MAX_RETRIES    = 4
MODEL          = "claude-haiku-4-5"

QUANT = re.compile(r"\b(sempre|mai|solo|soltanto|esclusivamente|tutti|tutte|ogni|"
                   r"qualsiasi|qualunque|nessun\w*|anche)\b", re.I)

SYSTEM_PROMPT = (
    "You improve answer explanations for Italy's Category B driving test (Patente B). "
    "Each item has: the Italian true/false statement (the answer is always FALSE), its "
    "English translation, and the CURRENT English explanation, which is factually correct. "
    "These statements are tricky because they are false due to one operative word — usually "
    "an absolute such as sempre (always), mai (never), solo/soltanto (only), tutti (all), "
    "qualsiasi/qualunque (any), nessuno (none/any), or anche (even/also). "
    "Rewrite the explanation so it: (1) starts with 'False.'; (2) explicitly names that "
    "operative word in quotes, giving the Italian word and its English meaning, e.g. "
    "\"the trick is 'sempre' (always)\"; (3) states the real rule concisely — WHY the absolute "
    "makes it false (the condition under which it would be true). Stay faithful to the facts in "
    "the current explanation; do NOT introduce new rules or numbers. If no single operative word "
    "is the crux, just make the explanation clearer. Keep it to one or two sentences. "
    "Also produce the Italian version, starting with 'Falso.', naming the same word. "
    "Return ONLY a raw JSON array of objects {\"en\": \"...\", \"it\": \"...\"}, same length and "
    "order as the input, no markdown, no commentary."
)


def targets(questions, done):
    for qi, q in enumerate(questions):
        for si, s in enumerate(q["statements"]):
            if (s.get("answer") == "FALSO"
                    and QUANT.search(s.get("italian_text", ""))
                    and s["number"] not in done):
                yield qi, si, s


def make_client(api_key):
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
    payload = json.dumps(items, ensure_ascii=False)
    msg = client.messages.create(model=MODEL, max_tokens=8192, system=SYSTEM_PROMPT,
                                 messages=[{"role": "user", "content": payload}])
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)


def improve_batch(client, items):
    """Return list of {'en','it'} same length as items (split on mismatch)."""
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
        return improve_batch(client, items[:mid]) + improve_batch(client, items[mid:])
    return [_api_call(client, items)[0]]


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: set ANTHROPIC_API_KEY before running.")
    client = make_client(api_key)

    questions = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    done = set(json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))) if PROGRESS_FILE.exists() else set()

    pending = list(targets(questions, done))
    total = len(pending)
    if total == 0:
        print("No pending trick-word explanations — nothing to do.")
        return
    print(f"Improving {total} FALSE trick-word explanations in batches of {BATCH_SIZE} ({MODEL})…\n", flush=True)

    n = 0
    for start in range(0, total, BATCH_SIZE):
        batch = pending[start:start + BATCH_SIZE]
        items = [{"statement": s["italian_text"], "english": s.get("english_translation", ""),
                  "current": s.get("explanation", "")} for (_, _, s) in batch]
        nb = (total + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"Batch {start // BATCH_SIZE + 1}/{nb} ({n}/{total})…", end=" ", flush=True)

        out = improve_batch(client, items)
        for (qi, si, s), o in zip(batch, out):
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

    print(f"\nDone. Improved {n} explanations. Remember to bump CACHE_VERSION in public_html/sw.js.")


if __name__ == "__main__":
    main()
