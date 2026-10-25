#!/usr/bin/env python3
"""
Batch-translate the English `explanation` of every true/false statement in
public_html/questions.json into Italian, written to `explanation_it`.

Usage (from the repo root):
    ANTHROPIC_API_KEY=sk-... python3 scripts/translate_explanations.py

- Resumes automatically: statements that already have a non-empty
  `explanation_it` are skipped, so you can stop and re-run any time.
- Saves progress to questions.json after every batch (a crash loses at most one).
- Preserves the polarity convention: a VERO statement's Italian explanation
  starts with "Vero." and a FALSO one with "Falso." (mirroring the English
  "True." / "False."), enforced as a safety net after translation.

After it finishes, bump CACHE_VERSION in public_html/sw.js (questions.json is a
cached asset) so installed users receive the new content.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import anthropic

ROOT           = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = ROOT / "public_html" / "questions.json"
BATCH_SIZE     = 50
RETRY_DELAY    = 5
MAX_RETRIES    = 4
MODEL          = "claude-haiku-4-5"

SYSTEM_PROMPT = (
    "You are a precise English-to-Italian translator. You will receive a JSON "
    "array of short explanations from Italy's official Category B driving-licence "
    "test (Patente B); each explains why a true/false statement is true or false. "
    "Return a JSON array of Italian translations — same length, same order. "
    "Rules: (1) If the English begins with 'True.' translate that to 'Vero.'; if it "
    "begins with 'False.' translate that to 'Falso.' — keep it as the first word. "
    "(2) Use correct, current Italian road-code terminology (e.g. 'right-of-way' → "
    "'precedenza', 'yield' → 'dare la precedenza', 'highway' → 'autostrada', "
    "'railroad crossing' → 'passaggio a livello', 'roadway/carriageway' → "
    "'carreggiata', 'lane' → 'corsia'). (3) Keep each explanation concise and "
    "faithful — do not add or drop information. Output only the raw JSON array, no "
    "markdown, no commentary."
)


def pending_statements(questions):
    """Yield (qi, si, english_explanation) for statements still needing Italian."""
    for qi, q in enumerate(questions):
        for si, stmt in enumerate(q["statements"]):
            en = (stmt.get("explanation") or "").strip()
            it = (stmt.get("explanation_it") or "").strip()
            if en and not it:
                yield (qi, si, en)


def enforce_polarity(answer, text):
    """Ensure the Italian explanation opens with Vero./Falso. matching the answer."""
    want = "Vero." if answer == "VERO" else "Falso." if answer == "FALSO" else None
    if not want:
        return text
    # Replace a leading Vero./Falso./Vero/Falso (any case) with the correct word.
    m = re.match(r"^\s*(vero|falso)\b\.?\s*", text, flags=re.IGNORECASE)
    if m:
        return want + " " + text[m.end():].lstrip()
    return want + " " + text.lstrip()


def _api_call(client, texts):
    """One attempt. Returns the parsed JSON value (list of any length)."""
    payload = json.dumps(texts, ensure_ascii=False)
    msg = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": payload}],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)


def translate_batch(client, texts):
    """Return Italian translations, guaranteed same length as `texts`.

    The model occasionally returns the wrong number of items (it merges or splits
    a line). When that happens we retry a few times, then split the batch in half
    and recurse — so a single problematic line can never stall the whole run.
    """
    last = ""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            out = _api_call(client, texts)
            if isinstance(out, list) and len(out) == len(texts):
                return [str(x) for x in out]
            last = f"got {len(out) if isinstance(out, list) else type(out).__name__}, want {len(texts)}"
        except anthropic.RateLimitError:
            if attempt == MAX_RETRIES:
                raise
            print(f"  rate-limited, waiting {RETRY_DELAY}s…", flush=True)
            time.sleep(RETRY_DELAY)
            continue
        except Exception as exc:  # JSON / transient transport errors
            last = str(exc)[:100]
        time.sleep(1)

    if len(texts) > 1:
        mid = len(texts) // 2
        print(f"  splitting {len(texts)} ({last})…", flush=True)
        return translate_batch(client, texts[:mid]) + translate_batch(client, texts[mid:])

    # Single item still failing: accept whatever the model returns for it.
    out = _api_call(client, texts)
    if isinstance(out, list) and out:
        return [str(out[0])]
    return [str(out).strip().strip('[]"')]


def make_client(api_key):
    """Build the client. Honors optional ANTHROPIC_PROXY / ANTHROPIC_CA_BUNDLE
    env vars for environments behind an HTTP/TLS-intercepting proxy; with neither
    set, behaves exactly like the default client."""
    proxy = os.environ.get("ANTHROPIC_PROXY")
    ca = os.environ.get("ANTHROPIC_CA_BUNDLE")
    if proxy or ca:
        import httpx
        http_client = httpx.Client(proxy=proxy or None, verify=ca or True,
                                   trust_env=False, timeout=60)
        return anthropic.Anthropic(api_key=api_key, http_client=http_client)
    return anthropic.Anthropic(api_key=api_key)


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: set ANTHROPIC_API_KEY before running.")
    client = make_client(api_key)

    questions = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    pending = list(pending_statements(questions))
    total = len(pending)
    if total == 0:
        print("All Italian explanations already filled — nothing to do.")
        return

    print(f"Translating {total} explanations in batches of {BATCH_SIZE} ({MODEL})…\n", flush=True)
    done = 0
    for start in range(0, total, BATCH_SIZE):
        batch = pending[start:start + BATCH_SIZE]
        texts = [en for (_, _, en) in batch]
        n_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"Batch {start // BATCH_SIZE + 1}/{n_batches} ({done}/{total})…", end=" ", flush=True)

        out = translate_batch(client, texts)
        for (qi, si, _), it_text in zip(batch, out):
            ans = questions[qi]["statements"][si].get("answer", "")
            questions[qi]["statements"][si]["explanation_it"] = enforce_polarity(ans, str(it_text).strip())

        done += len(batch)
        QUESTIONS_FILE.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"saved ({done}/{total})", flush=True)

    print(f"\nDone. {done} Italian explanations written to {QUESTIONS_FILE}")
    print("Remember to bump CACHE_VERSION in public_html/sw.js.")


if __name__ == "__main__":
    main()
