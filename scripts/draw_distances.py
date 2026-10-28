#!/usr/bin/env python3
"""Draw review_media/distances-en.svg and distances-it.svg (20261028q).

The distances the bank tests, in three panels: the multiples of 50 m, which
the railroad countdown panels count off one red bar per 50 m; the safe
following distance at each tested speed against the rough rule
(speed / 10) x 3; and the short distances of parking and stopping, with the
two outliers, 20 m from a snowplow and 500 m for the emergency lane. The
Reference page shows it inside "How to remember the distances". Edit the
labels HERE and rerun; both files are written from one table. Light colors
only, like the other review_media figures.
"""
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "public_html" / "review_media"
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
INK, MUTED = "#1e293b", "#475569"
CORAL = ("#FAECE7", "#D85A30", "#712B13")
TEAL = ("#E1F5EE", "#0F6E56", "#085041")
PURP = ("#EEEDFE", "#534AB7", "#3C3489")

L = {
 "en": dict(
   a="Multiples of 50 m: one red bar for every 50 m",
   cols=[
     (150, ["Danger sign ahead,|outside built-up areas", "Railroad crossing:|three-bar panel"]),
     (100, ["Railroad crossing:|two-bar panel", "Warning triangle:|visible from", "Trucks over 3.5 t|that may not pass:|gap between them", "Fog: visibility under|which a cap may be posted"]),
     (50, ["Railroad crossing:|one-bar panel", "Warning triangle:|behind the vehicle", "Fog: visibility under|which the rear fog|light goes on"])],
   b="Safe following distance, roughly (speed ÷ 10) × 3",
   kmh="km/h",
   c="Close by, and two outliers",
   near=[("1 m", "Pedestrians, with no raised sidewalk"), ("1 m", "Warning triangle, from the road edge"),
         ("3 m", "Left free to park on a one-way street's left"), ("5 m", "No stopping near an intersection, in town"),
         ("15 m", "No parking from a bus stop sign"), ("20 m", "Behind a working snowplow"),
         ("500 m", "Emergency lane usable to reach an exit")],
   title="Distances in meters: the multiples of 50 m that the railroad countdown panels count off, the safe following distance at each tested speed, and the short distances of parking and stopping."),
 "it": dict(
   a="Multipli di 50 m: una barra rossa ogni 50 m",
   cols=[
     (150, ["Segnale di pericolo,|fuori dai centri abitati", "Passaggio a livello:|pannello a tre barre"]),
     (100, ["Passaggio a livello:|pannello a due barre", "Triangolo:|visibile da", "Autocarri oltre 3,5 t|senza sorpasso:|distanza tra loro", "Nebbia: visibilità sotto|cui si può imporre|un limite"]),
     (50, ["Passaggio a livello:|pannello a una barra", "Triangolo:|dietro il veicolo", "Nebbia: visibilità|sotto cui si accende|il retronebbia"])],
   b="Distanza di sicurezza, circa (velocità ÷ 10) × 3",
   kmh="km/h",
   c="Da vicino, e due eccezioni",
   near=[("1 m", "Pedoni, senza marciapiede rialzato"), ("1 m", "Triangolo, dal bordo della strada"),
         ("3 m", "Liberi per la sosta a sinistra nel senso unico"), ("5 m", "Niente fermata vicino a un incrocio, in città"),
         ("15 m", "Niente sosta dal segnale di fermata bus"), ("20 m", "Dietro uno sgombraneve in azione"),
         ("500 m", "Corsia di emergenza per raggiungere un'uscita")],
   title="Distanze in metri: i multipli di 50 m che i pannelli del passaggio a livello contano a ritroso, la distanza di sicurezza a ogni velocità, e le distanze brevi di sosta e fermata."),
}
SAFE = [(30, 9), (50, 14), (100, 28), (130, 36), (150, 42)]

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")

def countdown(x, y, n):
    """The railroad countdown panel: white, red border, n red diagonal bars."""
    w, h = 22, 46
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="#ffffff" stroke="#b91c1c" stroke-width="1.5"/>']
    for k in range(n):
        yy = y + 8 + k * 12
        o.append(f'<path d="M{x+3} {yy+9} L{x+w-3} {yy} L{x+w-3} {yy+5} L{x+3} {yy+14} Z" fill="#dc2626"/>')
    return "".join(o)

def svg(lang):
    t = L[lang]; o = []; W = 640
    y = 18
    body = []
    body.append(f'<text x="16" y="{y+16}" font-size="14" font-weight="700" fill="{INK}">{esc(t["a"])}</text>')
    y += 30
    colw, gap = 196, 10
    tallest = 0
    for j, (m, items) in enumerate(t["cols"]):
        x = 16 + j * (colw + gap)
        f, s, ink = CORAL
        lines = sum(len(it.split("|")) for it in items) * 15 + len(items) * 8
        h = 62 + lines + 6
        tallest = max(tallest, h)
        body.append(("COL", x, y, colw, m, items, j))
    for b in body:
        if isinstance(b, str): o.append(b); continue
        _, x, y0, cw, m, items, j = b
        f, s, ink = CORAL
        o.append(f'<rect x="{x}" y="{y0}" width="{cw}" height="{tallest}" rx="8" fill="{f}" stroke="{s}" stroke-width="1.5"/>')
        o.append(countdown(x + 12, y0 + 10, 3 - j))
        o.append(f'<text x="{x+46}" y="{y0+42}" font-size="24" font-weight="700" fill="{ink}">{m} m</text>')
        yy = y0 + 76
        for it in items:
            for ln in it.split("|"):
                o.append(f'<text x="{x+12}" y="{yy}" font-size="12" fill="{ink}">{esc(ln)}</text>'); yy += 15
            yy += 8
    y = y + tallest + 26
    o.append(f'<text x="16" y="{y}" font-size="14" font-weight="700" fill="{INK}">{esc(t["b"])}</text>')
    y += 14
    f, s, ink = TEAL
    for v, m in SAFE:
        o.append(f'<text x="16" y="{y+15}" font-size="12" fill="{MUTED}">{v} {t["kmh"]}</text>')
        o.append(f'<rect x="84" y="{y+2}" width="{m*11}" height="18" rx="4" fill="{f}" stroke="{s}" stroke-width="1.2"/>')
        o.append(f'<text x="{84+m*11+8}" y="{y+16}" font-size="13" font-weight="700" fill="{ink}">{m} m</text>')
        y += 26
    y += 22
    o.append(f'<text x="16" y="{y}" font-size="14" font-weight="700" fill="{INK}">{esc(t["c"])}</text>')
    y += 12
    f, s, ink = PURP
    half = len(t["near"])   # one column: two left the Italian lines no room
    for k, (v, lab) in enumerate(t["near"]):
        x = 16; yy = y + k * 30
        o.append(f'<rect x="{x}" y="{yy}" width="54" height="22" rx="4" fill="{f}" stroke="{s}" stroke-width="1.2"/>')
        o.append(f'<text x="{x+27}" y="{yy+15}" text-anchor="middle" font-size="12" font-weight="700" fill="{ink}">{esc(v)}</text>')
        o.append(f'<text x="{x+62}" y="{yy+15}" font-size="12.5" fill="{INK}">{esc(lab)}</text>')
    H = y + half * 30 + 12
    head = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(t["title"])}">',
            f'<title>{esc(t["title"])}</title>',
            f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>',
            f'<g font-family="{FONT}">']
    return "\n".join(head + o + ['</g></svg>']) + "\n"

if __name__ == "__main__":
    for lang in L:
        (OUT / f"distances-{lang}.svg").write_text(svg(lang))
        print("wrote", OUT / f"distances-{lang}.svg")
