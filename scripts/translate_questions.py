#!/usr/bin/env python3
"""
Batch-translate all english_translation fields in questions.json
using the Anthropic API (claude-haiku-3-5).

Usage:
    ANTHROPIC_API_KEY=sk-... python3 translate_questions.py

Resumes automatically — already-filled translations are skipped.
Progress is saved to questions.json after every batch.
"""

import json
import os
import sys
import time
from pathlib import Path

import anthropic

QUESTIONS_FILE = Path(__file__).parent / "public_html" / "questions.json"
BATCH_SIZE = 50          # statements per API call
RETRY_DELAY = 5          # seconds between retries on rate-limit
MAX_RETRIES = 3

SYSTEM_PROMPT = (
    "You are a precise Italian-to-English translator. "
    "You will receive a JSON array of Italian strings taken from Italy's "
    "official Category B driving licence test (Patente B). "
    "Return a JSON array of English translations — same length, same order. "
    "Keep translations concise and literal. Preserve technical driving/road terms "
    "(e.g. 'segnale di precedenza' → 'right-of-way sign', not 'sign that gives priority'). "
    "Output only the raw JSON array, no markdown, no commentary."
)


def build_batches(questions):
    """Yield (question_idx, statement_idx, italian_text) for empty translations."""
    for qi, q in enumerate(questions):
        for si, stmt in enumerate(q["statements"]):
            if not stmt["english_translation"]:
                yield (qi, si, stmt["italian_text"])


def translate_batch(client, texts):
    """Call the API and return a list of English strings, same length as texts."""
    payload = json.dumps(texts, ensure_ascii=False)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            msg = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=4096,
                messages=[{"role": "user", "content": payload}],
                system=SYSTEM_PROMPT,
            )
            raw = msg.content[0].text.strip()
            # Strip markdown code fences if the model wrapped the response
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]  # remove opening fence line
                raw = raw.rsplit("```", 1)[0].strip()  # remove closing fence
            translations = json.loads(raw)
            if not isinstance(translations, list) or len(translations) != len(texts):
                raise ValueError(
                    f"Expected {len(texts)} items, got {len(translations) if isinstance(translations, list) else type(translations)}"
                )
            return translations
        except anthropic.RateLimitError:
            if attempt == MAX_RETRIES:
                raise
            print(f"  Rate-limited, waiting {RETRY_DELAY}s…", flush=True)
            time.sleep(RETRY_DELAY)
        except json.JSONDecodeError as exc:
            raise ValueError(f"API returned non-JSON: {raw[:200]}") from exc


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: set ANTHROPIC_API_KEY in your environment before running.")

    client = anthropic.Anthropic(api_key=api_key)

    with open(QUESTIONS_FILE) as f:
        questions = json.load(f)

    pending = list(build_batches(questions))
    total = len(pending)
    if total == 0:
        print("All translations already filled — nothing to do.")
        return

    print(f"Translating {total} statements in batches of {BATCH_SIZE}…\n")
    done = 0

    for batch_start in range(0, total, BATCH_SIZE):
        batch = pending[batch_start : batch_start + BATCH_SIZE]
        texts = [italian for (_, _, italian) in batch]

        print(f"Batch {batch_start // BATCH_SIZE + 1} / {(total + BATCH_SIZE - 1) // BATCH_SIZE}  "
              f"({done}/{total} done)…", end=" ", flush=True)

        translations = translate_batch(client, texts)

        for (qi, si, _), en_text in zip(batch, translations):
            questions[qi]["statements"][si]["english_translation"] = en_text

        done += len(batch)

        # Save progress after every batch so a crash loses at most one batch
        with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

        print(f"saved. ({done}/{total})", flush=True)

    print(f"\nDone. {done} translations written to {QUESTIONS_FILE}")


if __name__ == "__main__":
    main()
