"""Extract DomandeB.pdf into questions.json for the Patente B study website.

Output schema (one element per quesito):

    {
        "id": 4328,
        "topic": "Segnali di indicazione",
        "image": "domandeb_images/quesito_0001.jpeg",   // null if no image
        "statements": [
            {
                "number": "21810",
                "italian_text": "Il segnale raffigurato ...",
                "answer": "VERO",
                "english_translation": "",
                "explanation": "",
                "image": "domandeb_images/stmt_21810.jpeg"  // optional; only present
                                                             // when this statement has
                                                             // its own image (A/B sign
                                                             // pairs etc.) that differs
                                                             // from the card-level image
            },
            ...
        ]
    }

The fields "english_translation" and "explanation" are intentionally left empty
here — they form the human-authored content layer that is added separately.

Usage:
    python extract_domandeb_to_json.py DomandeB.pdf questions.json
    python extract_domandeb_to_json.py DomandeB.pdf questions.json \\
        --image-dir-name domandeb_images --pretty
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

# Re-use all parsing logic from the original extractor unchanged.
from extract_domandeb_to_latex import Statement, Quesito, parse_document


def quesito_to_dict(q: Quesito, image_dir_name: str) -> dict:
    """Convert a Quesito dataclass to the website JSON schema."""
    return {
        "id": int(q.quesito_number),
        "topic": q.topic,
        "image": f"{image_dir_name}/{q.image_path}" if q.image_path else None,
        "statements": [
            {
                "number": s.number,
                "italian_text": s.text,
                "answer": s.answer,
                "english_translation": "",
                "explanation": "",
            }
            for s in q.statements
        ],
    }


def build_json(quesiti: list[Quesito], image_dir_name: str, pretty: bool) -> str:
    data = [quesito_to_dict(q, image_dir_name) for q in quesiti]
    indent = 2 if pretty else None
    return json.dumps(data, ensure_ascii=False, indent=indent)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract DomandeB.pdf to questions.json"
    )
    parser.add_argument("pdf_path", type=Path, help="Path to DomandeB.pdf")
    parser.add_argument("output_json", type=Path, help="Output path for questions.json")
    parser.add_argument(
        "--image-dir-name",
        default="domandeb_images",
        help="Subdirectory name for images, relative to the output JSON file",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=False,
        help="Pretty-print the JSON (2-space indent)",
    )
    args = parser.parse_args()

    pdf_path = args.pdf_path.resolve()
    output_json = args.output_json.resolve()
    output_dir = output_json.parent
    image_dir = output_dir / args.image_dir_name
    image_dir.mkdir(parents=True, exist_ok=True)

    print(f"Parsing {pdf_path} ...")
    quesiti = parse_document(pdf_path, image_dir)
    print(f"Parsed {len(quesiti)} quesiti")

    json_text = build_json(quesiti, args.image_dir_name, args.pretty)
    output_json.write_text(json_text, encoding="utf-8")
    print(f"Wrote {output_json}  ({output_json.stat().st_size // 1024} KB)")
    print(f"Images in {image_dir}")


if __name__ == "__main__":
    main()
