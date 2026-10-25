#!/usr/bin/env python3
"""
Write the SIDA manual's chapter(s) for one topic to a text file, so a reader
can check the topic's review against the textbook.

    python3 scripts/sida_extract.py 12 OUTDIR        # -> OUTDIR/12.txt
    python3 scripts/sida_extract.py all OUTDIR

The manual is copyrighted and lives in the gitignored `private/` folder
(`private/Manuale-text.txt`, a pdftotext extraction). Nothing from it is ever
pasted into the app; the extract is a reading aid for the cross-check step in
docs/CLAIMS-ROLLOUT.md, and it stays outside the repo.

The line ranges below were read off the extraction on 2026-09-18 (chapter
headings found with grep). If the extraction is redone, re-run the grep in
the docstring of `RANGES` and update them.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUAL = ROOT / "private" / "Manuale-text.txt"

# topic -> list of (first line, line after last), 1-based, in Manuale-text.txt.
# Found with:  grep -n "^12\.1 Limiti\|^13\.1 Posizione\|..." private/Manuale-text.txt
RANGES = {
    "16": [(345, 828)],                      # ch. 1  veicoli, strade
    "14": [(4673, 5054), (10776, 10929)],    # 11.1-11.5 luci, clacson; 22.2 spie
    "11": [(5407, 5755), (7226, 7915)],      # 12.1-12.2 velocità; 18.1 cautele
    "13": [(5755, 6111)],                    # ch. 13 posizione, svolte
    "12": [(6530, 6785)],                    # ch. 16 arresto, fermata, sosta
    "21": [(6785, 7226)],                    # ch. 17 carico, autostrade
    "17": [(7943, 8092), (8232, 8756)],      # 19.2 stato psicofisico; 19.4-19.5 soccorso
    "23": [(8756, 8994)],                    # 19.6 responsabilità, RCA
    "22": [(8994, 9926)],                    # ch. 20 patenti, documenti
    "20": [(9926, 10551), (11599, 11942)],   # ch. 21 tenuta di strada; appendice meccanica
    "24": [(10551, 10776)],                  # 22.1 inquinamento
    # not yet claimed:
    "09": [(5557, 5755)],                    # 12.2 arresto del veicolo (distanza di sicurezza)
    "10": [(6313, 6530)],                    # ch. 15 sorpasso
    "18": [(7226, 7915), (7915, 7943), (8092, 8232)],  # 18.1 cautele; 19.1, 19.3
    "19": [(5054, 5407), (10992, 11128)],    # 11.6-11.8 dispositivi, cinture; 23.4-23.7 casco, indumenti
    "25": [(6111, 6313)],                    # ch. 14 precedenze
    "15": [(3950, 4264)],                    # 9.1-9.2 semafori, agenti
    "03": [(828, 1414)],                     # ch. 2 segnali di pericolo
    "01": [(2511, 3302)],                    # ch. 6 segnali di indicazione
    "04": [(1616, 2227)],                    # ch. 4 segnali di divieto, sosta
    "06": [(3302, 3950)],                    # ch. 7-8 segnali temporanei, complementari
    "07": [(4264, 4671)],                    # ch. 10 segnaletica orizzontale
    "05": [(1414, 1616)],                    # ch. 3 segnali di precedenza
    "02": [(2227, 2511)],                    # ch. 5 segnali di obbligo
    "08": [(3622, 3950)],                    # ch. 8 pannelli integrativi (inside 06's ch. 7-8 range)
}


def extract(topic: str) -> str:
    lines = MANUAL.read_text(encoding="utf-8", errors="ignore").split("\n")
    parts = []
    for a, b in RANGES[topic]:
        body = [x.rstrip() for x in lines[a - 1:b - 1]
                if x.strip() and not x.strip().isdigit()]
        parts.append("\n".join(body))
    return "\n\n[...]\n\n".join(parts)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    topic, out = sys.argv[1], Path(sys.argv[2])
    if not MANUAL.exists():
        sys.exit(f"manual not found at {MANUAL} (gitignored; ask the maintainer)")
    out.mkdir(parents=True, exist_ok=True)
    topics = sorted(RANGES) if topic == "all" else [topic.zfill(2)]
    for t in topics:
        txt = extract(t)
        (out / f"{t}.txt").write_text(txt, encoding="utf-8")
        print(f"{t}: {len(txt):,} chars -> {out / (t + '.txt')}")


if __name__ == "__main__":
    main()
