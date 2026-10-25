#!/usr/bin/env python3
"""Validate and freeze the Quick-mode (abridged) card selection.

Pipeline (see docs/fable.md and docs/ABRIDGE-PROMPT.md):

  1. `format-card <id>` prints a card as the prompt-ready input block.
  2. An LLM call per card produces a group structure, stored by hand or batch
     into docs/abridged-audit.json under cards.<id>.
  3. `validate` mechanically checks every audited card against
     public_html/questions.json, prints progress + compression metrics, and
     with --write freezes public_html/abridged.json (cardId -> kept numbers).

Audit file shape (docs/abridged-audit.json):

  {
    "version": "1.0",
    "cards": {
      "4272": {
        "groups": [
          { "concept": "...", "answer": "VERO"|"FALSO",
            "members": ["21274", ...], "keep": "21274",
            "why_keep": "...", "confidence": "high"|"medium"|"low" }
        ]
      }
    }
  }

Hard rules enforced (errors — block --write):
  E1  audited card id exists in questions.json
  E2  every statement of the card is in exactly one group (none missing,
      none invented, none duplicated)
  E3  keep is one of members; members non-empty
  E4  groups never mix VERO and FALSO, and the declared answer matches the
      actual answer of every member
  E5  confidence is high|medium|low; concept label non-empty
  E6  passthrough cards (<= PASSTHROUGH_MAX statements) keep ALL statements

Warnings (reported, never block):
  W1  abridged set equals the full set on a non-passthrough card (no-op)
  W2  multi-member FALSO group with confidence below high (the risky merges;
      use --conservative-falso to split them in the output)

The aggressiveness dial: --conservative-falso splits every multi-member FALSO
group whose confidence is not "high" (all its members are kept) WITHOUT
touching the audit file. Stdlib only; no third-party deps.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUESTIONS_PATH = REPO / "public_html" / "questions.json"
AUDIT_PATH = REPO / "docs" / "abridged-audit.json"
OUT_PATH = REPO / "public_html" / "abridged.json"

PASSTHROUGH_MAX = 3          # cards with <= this many statements keep all (brief req. #5)
CONFIDENCES = {"high", "medium", "low"}


# ── data loading ─────────────────────────────────────────────────────────────

def load_questions(path: Path) -> dict[int, dict]:
    cards = json.loads(path.read_text(encoding="utf-8"))
    return {c["id"]: c for c in cards}


def load_audit(path: Path) -> dict:
    if not path.exists():
        return {"version": "1.0", "cards": {}}
    return json.loads(path.read_text(encoding="utf-8"))


# ── format-card ──────────────────────────────────────────────────────────────

def format_card(card: dict) -> str:
    lines = [
        f"CARD {card['id']} — topic: {card['topic']}"
        + (f" — image: {card['image']}" if card.get("image") else "")
    ]
    for s in card["statements"]:
        lines.append(f"{s['number']} {s['answer']:<5} {s['italian_text']}")
    return "\n".join(lines)


# ── per-card validation ──────────────────────────────────────────────────────

def check_card(card: dict, entry: dict, conservative_falso: bool):
    """Return (kept_numbers, errors, warnings) for one audited card."""
    errors: list[str] = []
    warnings: list[str] = []
    real = {str(s["number"]): s["answer"] for s in card["statements"]}

    groups = entry.get("groups")
    if not isinstance(groups, list) or not groups:
        return [], ["no groups"], []

    seen: dict[str, int] = {}
    kept: list[str] = []

    for i, g in enumerate(groups):
        label = g.get("concept") or ""
        if not str(label).strip():
            errors.append(f"group {i}: empty concept label")            # E5
        conf = g.get("confidence")
        if conf not in CONFIDENCES:
            errors.append(f"group {i} ({label}): bad confidence {conf!r}")  # E5

        members = [str(m) for m in g.get("members", [])]
        if not members:
            errors.append(f"group {i} ({label}): no members")           # E3
            continue
        keep = str(g.get("keep", ""))
        if keep not in members:
            errors.append(f"group {i} ({label}): keep {keep!r} not in members")  # E3

        answers = set()
        for m in members:
            if m not in real:
                errors.append(f"group {i} ({label}): invented number {m}")  # E2
                continue
            seen[m] = seen.get(m, 0) + 1
            answers.add(real[m])
        if len(answers) > 1:
            errors.append(f"group {i} ({label}): mixes VERO and FALSO")     # E4
        elif answers and g.get("answer") not in answers:
            errors.append(
                f"group {i} ({label}): declared {g.get('answer')!r}, members are {answers.pop()}"
            )                                                               # E4

        is_falso = real.get(keep) == "FALSO" or g.get("answer") == "FALSO"
        risky = is_falso and len(members) > 1 and g.get("confidence") != "high"
        if risky:
            warnings.append(
                f"group {i} ({label}): {len(members)}-member FALSO merge at "
                f"confidence {g.get('confidence')!r}"
            )                                                               # W2
        if risky and conservative_falso:
            kept.extend(m for m in members if m in real)   # split: keep all
        elif keep in real:
            kept.append(keep)

    missing = sorted(set(real) - set(seen), key=int)
    if missing:
        errors.append(f"statements not in any group: {', '.join(missing)}")  # E2
    dupes = sorted((m for m, n in seen.items() if n > 1), key=int)
    if dupes:
        errors.append(f"statements in multiple groups: {', '.join(dupes)}")  # E2

    if len(real) <= PASSTHROUGH_MAX and len(kept) < len(real):
        errors.append(
            f"passthrough card ({len(real)} statements) must keep all"
        )                                                                    # E6
    if not errors and len(kept) == len(real) and len(real) > PASSTHROUGH_MAX:
        warnings.append("abridged set equals full set (no-op)")              # W1

    # preserve the card's original statement order in the output
    order = {n: i for i, n in enumerate(real)}
    kept = sorted(set(kept), key=lambda n: order[n])
    return kept, errors, warnings


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_format_card(args) -> int:
    questions = load_questions(args.questions)
    bad = [i for i in args.ids if i not in questions]
    if bad:
        print(f"unknown card id(s): {bad}", file=sys.stderr)
        return 1
    print("\n\n".join(format_card(questions[i]) for i in args.ids))
    return 0


def cmd_progress(args) -> int:
    questions = load_questions(args.questions)
    audit = load_audit(args.audit)
    audited = {int(k) for k in audit.get("cards", {})}
    todo = [
        i for i, c in sorted(questions.items())
        if len(c["statements"]) > PASSTHROUGH_MAX and i not in audited
    ]
    passthrough = sum(1 for c in questions.values() if len(c["statements"]) <= PASSTHROUGH_MAX)
    print(f"cards: {len(questions)}  passthrough(<= {PASSTHROUGH_MAX}): {passthrough}  "
          f"audited: {len(audited)}  remaining: {len(todo)}")
    if todo and args.list:
        print(" ".join(str(i) for i in todo[: args.list]))
    return 0


def cmd_validate(args) -> int:
    questions = load_questions(args.questions)
    audit = load_audit(args.audit)
    entries = audit.get("cards", {})

    out: dict[str, list[str]] = {}
    n_err = n_warn = 0
    tot_full = tot_kept = 0
    risky_cards: list[str] = []

    for cid_str, entry in sorted(entries.items(), key=lambda kv: int(kv[0])):
        cid = int(cid_str)
        card = questions.get(cid)
        if card is None:
            print(f"[{cid}] ERROR: not in questions.json")                  # E1
            n_err += 1
            continue
        kept, errors, warnings = check_card(card, entry, args.conservative_falso)
        for e in errors:
            print(f"[{cid}] ERROR: {e}")
        for w in warnings:
            print(f"[{cid}] warn: {w}")
            if "FALSO merge" in w:
                risky_cards.append(cid_str)
        n_err += len(errors)
        n_warn += len(warnings)
        if errors:
            continue
        tot_full += len(card["statements"])
        tot_kept += len(kept)
        if len(kept) < len(card["statements"]):
            out[cid_str] = kept

    audited = len(entries)
    remaining = sum(
        1 for i, c in questions.items()
        if len(c["statements"]) > PASSTHROUGH_MAX and str(i) not in entries
    )
    print(f"\naudited cards: {audited}   errors: {n_err}   warnings: {n_warn}   "
          f"non-passthrough cards still unaudited: {remaining}")
    if tot_full:
        pct = 100 * (1 - tot_kept / tot_full)
        print(f"compression over audited cards: kept {tot_kept}/{tot_full} "
              f"statements ({pct:.1f}% hidden)")
    if risky_cards:
        mode = "SPLIT in output (--conservative-falso)" if args.conservative_falso else "kept as merged"
        print(f"sub-high-confidence FALSO merges on {len(set(risky_cards))} card(s) — {mode}")

    if n_err:
        print("\nNOT writing artifact: fix errors first.", file=sys.stderr)
        return 1
    if args.write:
        args.out.write_text(
            json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {args.out} ({len(out)} cards with a real abridged set)")
    else:
        print("dry run: pass --write to freeze public_html/abridged.json")
    return 0


# ── cli ──────────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--questions", type=Path, default=QUESTIONS_PATH)
    p.add_argument("--audit", type=Path, default=AUDIT_PATH)
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("format-card", help="print prompt-ready input block(s)")
    f.add_argument("ids", nargs="+", type=int)
    f.set_defaults(func=cmd_format_card)

    g = sub.add_parser("progress", help="show audited / remaining counts")
    g.add_argument("--list", type=int, default=0, metavar="N",
                   help="also list up to N unaudited card ids")
    g.set_defaults(func=cmd_progress)

    v = sub.add_parser("validate", help="check audit file; --write freezes the artifact")
    v.add_argument("--write", action="store_true",
                   help="write the frozen artifact (refused if any error)")
    v.add_argument("--out", type=Path, default=OUT_PATH)
    v.add_argument("--conservative-falso", action="store_true",
                   help="split multi-member FALSO groups below high confidence")
    v.set_defaults(func=cmd_validate)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
