#!/usr/bin/env python3
"""Draw the three turning-around figures of the driving test page (20261103u).

review_media/turnaround-{1,2,3}-{en,it}.svg: the inversione di marcia of
circular 28819 para. b, one figure per move, seen from above on a two-way
street 7 m wide with a sidewalk on each side and a broken center line.
  1. Forward from the right edge, steering left, to a stop before the left
     edge. Left signal. Look ahead, behind and to both sides first.
  2. Reverse, far enough to leave room for the last move. Right signal.
     Look back, with glances ahead, right and left.
  3. Forward into the right lane of the opposite direction. Left signal.
     Look right and left.
Every label names where to look as well as the signal (maintainer, 20261103v).
Each figure shows the car where the move starts (solid, with its signal in
amber), the path of its leading end, the front going forward and the rear in reverse (dashed when reversing), and the car where
the move ends (a dashed outline, drawn over the starting car, with a bar at its front). One figure per move, because the car is longer
than half the road is wide and the four positions overlap when drawn
together. The car (4.0 m by 1.7 m) and its turning radius (4.5 m at the
center) are to the road's scale, so the three moves are what the geometry
allows: 77 degrees forward, 32 in reverse, 71 forward. Light colors only.
Edit the labels HERE and rerun; all six files come from one drawing.
"""
import math
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "public_html" / "review_media"

L = {
 1: {"en": dict(l=["Look ahead,", "behind and to", "both sides.", "Left signal on.", "Forward at", "walking pace,", "steering left."], r=["Stop before", "the edge."],
                title="Turning around, first move, seen from above on a two-way street. The car starts at the right edge with its left signal on, goes forward steering left, and stops across the road with its front just short of the left edge."),
     "it": dict(l=["Guarda avanti,", "dietro e ai lati.", "Freccia a", "sinistra.", "Avanti a passo", "d'uomo,", "sterzando a", "sinistra."], r=["Fermati prima", "del margine."],
                title="Inversione di marcia, prima manovra, vista dall'alto su una strada a doppio senso. L'auto parte dal margine destro con la freccia a sinistra, avanza sterzando a sinistra e si ferma di traverso con il muso poco prima del margine sinistro.")},
 2: {"en": dict(r=["Right signal on.", "Look back, and", "glance ahead,", "right and left.", "Reverse."], l=["Leave room for", "the last move."],
                title="Turning around, second move, seen from above. The car, across the road with its right signal on, reverses toward the right edge, far enough to leave room for the last move."),
     "it": dict(r=["Freccia a destra.", "Guarda indietro,", "poi avanti, a", "destra e a", "sinistra.", "Retromarcia."], l=["Lascia spazio", "per l'ultima", "manovra."],
                title="Inversione di marcia, seconda manovra, vista dall'alto. L'auto, di traverso con la freccia a destra, fa retromarcia verso il margine destro, per un tratto sufficiente all'ultima manovra.")},
 3: {"en": dict(l=["Left signal on.", "Look right", "and left.", "Yield to anyone", "coming."], r=["Then move into", "the right lane."],
                title="Turning around, third move, seen from above. The car, with its left signal on, goes forward steering left into the right lane of the opposite direction and drives away."),
     "it": dict(l=["Freccia a", "sinistra.", "Guarda a destra", "e a sinistra.", "Dai la precedenza", "a chi arriva."], r=["Poi immettiti", "nella corsia", "di destra."],
                title="Inversione di marcia, terza manovra, vista dall'alto. L'auto, con la freccia a sinistra, avanza sterzando a sinistra, entra nella corsia di destra del senso opposto e si allontana.")},
}
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
W, H = 640, 500
KL, KR = 170, 470                      # kerbs: the road is 300 px for 7 m
WALK = 30
PX = (KR - KL) / 7.0                   # pixels per meter
CL, CW, R = 4.0 * PX, 1.7 * PX, 4.5 * PX
BLUE, AMBER, RED = "#1D4ED8", "#F59E0B", "#DC2626"
ROAD, SIDE, KERB, WHITE = "#B4BCC8", "#E2E8F0", "#7C8798", "#ffffff"

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def fwd(h):   a = math.radians(h); return (math.cos(a), -math.sin(a))   # screen y points down
def right(h): a = math.radians(h); return (math.sin(a), math.cos(a))

def move(pos, h, steer, direction, deg):
    """Drive an arc. steer 'L' or 'R', direction +1 forward or -1 reverse, deg > 0.
    Returns (new position, new heading, SVG arc command)."""
    side = 1 if steer == "R" else -1
    r = right(h); c = (pos[0] + side * R * r[0], pos[1] + side * R * r[1])
    turn = deg * (1 if steer == "L" else -1) * direction        # counterclockwise on the map is positive
    a = math.radians(turn)
    x, y = pos[0] - c[0], pos[1] - c[1]
    new = (c[0] + x * math.cos(a) + y * math.sin(a), c[1] - x * math.sin(a) + y * math.cos(a))
    return new, h + turn, f"A {R:.1f} {R:.1f} 0 0 {0 if turn > 0 else 1} {new[0]:.1f} {new[1]:.1f}"

def trace(pos, h, steer, direction, deg, n=28):
    """The path of the car's LEADING end through a move (front going forward, rear
    reversing), as SVG line commands. The center's path hides under the car on a
    short move; the leading end shows where the car is going."""
    pts = []
    for k in range(n + 1):
        q, hq, _ = move(pos, h, steer, direction, deg * k / n) if k else (pos, h, "")
        f = fwd(hq); e = direction * CL / 2
        pts.append((q[0] + e * f[0], q[1] + e * f[1]))
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts), pts[-1]

def car(pos, h, sig=None, ghost=False):
    hl, hw = CL / 2, CW / 2
    g = f'<g transform="translate({pos[0]:.1f} {pos[1]:.1f}) rotate({-h:.1f})">'
    if ghost:
        # Drawn OVER the starting car, which it overlaps: a dark line under a white
        # dashed one shows on the road and on the car alike. The bar marks the front.
        box = f'x="{-hl:.1f}" y="{-hw:.1f}" width="{CL:.1f}" height="{CW:.1f}" rx="16" fill="none"'
        bar = f'd="M {hl-30:.1f} {-hw+10:.1f} L {hl-30:.1f} {hw-10:.1f}" fill="none"'
        return g + (f'<rect {box} stroke="#0f172a" stroke-width="5"/><path {bar} stroke="#0f172a" stroke-width="5"/>'
                    f'<rect {box} stroke="#ffffff" stroke-width="2.5" stroke-dasharray="9 7"/><path {bar} stroke="#ffffff" stroke-width="2.5"/></g>')
    g += f'<rect x="{-hl:.1f}" y="{-hw:.1f}" width="{CL:.1f}" height="{CW:.1f}" rx="16" fill="{BLUE}" stroke="#ffffff" stroke-width="1.5"/>'
    g += f'<path d="M {hl-58:.1f} {-hw+8:.1f} L {hl-34:.1f} {-hw+11:.1f} L {hl-34:.1f} {hw-11:.1f} L {hl-58:.1f} {hw-8:.1f} Z" fill="#ffffff" opacity=".65"/>'   # windshield
    g += f'<rect x="{-hl+18:.1f}" y="{-hw+10:.1f}" width="14" height="{CW-20:.1f}" rx="4" fill="#ffffff" opacity=".45"/>'                                      # rear window
    if sig:
        o = 1 if sig == "R" else -1
        y = o * (hw + 1)
        for x in (hl - 14, -hl + 14):
            g += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{AMBER}" stroke="#7C2D12" stroke-width="1.2"/>'
                  f'<path d="M {x-7:.1f} {y+o*11:.1f} L {x-11:.1f} {y+o*18:.1f} M {x:.1f} {y+o*12.5:.1f} L {x:.1f} {y+o*20:.1f} M {x+7:.1f} {y+o*11:.1f} L {x+11:.1f} {y+o*18:.1f}" stroke="{AMBER}" stroke-width="3" stroke-linecap="round" fill="none"/>')
    return g + '</g>'

# The three moves, from the start at the right edge heading up the picture.
P0, H0 = (KR - 15 - CW / 2, 300.0), 90.0
P1, H1, A1 = move(P0, H0, "L", +1, 77)
P2, H2, A2 = move(P1, H1, "R", -1, 32)
P3, H3, A3 = move(P2, H2, "L", +1, 270 - H2)
END = (P3[0], H - 26)

def svg(n, lang):
    t = L[n][lang]; o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(t["title"])}">')
    o.append(f'<title>{esc(t["title"])}</title>')
    o.append('<defs>'
             f'<clipPath id="card"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12"/></clipPath>'
             f'<marker id="ab" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>'
             '</defs>')
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="#f8fafc"/>')
    o.append('<g clip-path="url(#card)">')
    # the street: sidewalks, kerbs, carriageway, broken center line
    o.append(f'<rect x="{KL-WALK}" y="0" width="{KR-KL+2*WALK}" height="{H}" fill="{SIDE}"/>')
    o.append(f'<rect x="{KL}" y="0" width="{KR-KL}" height="{H}" fill="{ROAD}"/>')
    for x in (KL, KR):
        o.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{KERB}" stroke-width="3"/>')
    for x in (KL - WALK, KR + WALK):
        o.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#cbd5e1" stroke-width="1.5"/>')
    o.append(f'<line x1="{(KL+KR)/2}" y1="0" x2="{(KL+KR)/2}" y2="{H}" stroke="{WHITE}" stroke-width="3.5" stroke-dasharray="26 20"/>')
    style = f'fill="none" stroke="{BLUE}" stroke-width="5" stroke-linecap="round" marker-end="url(#ab)"'
    if n == 1:
        o.append(car(P0, H0, "L"))
        o.append(car(P1, H1, ghost=True))
        o.append(f'<path d="{trace(P0, H0, "L", +1, 77)[0]}" {style}/>')
    elif n == 2:
        o.append(car(P1, H1, "R"))
        o.append(car(P2, H2, ghost=True))
        o.append(f'<path d="{trace(P1, H1, "R", -1, 32)[0]}" {style} stroke-dasharray="11 10"/>')
    else:
        o.append(car(P2, H2, "L"))
        o.append(car((P3[0], P3[1] + 30), 270, ghost=True))
        o.append(f'<path d="{trace(P2, H2, "L", +1, 270 - H2)[0]} L {END[0]:.1f} {END[1]:.1f}" {style}/>')
    o.append('</g>')
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="none" stroke="#cbd5e1" stroke-width="1.5"/>')
    # the move's number, and the labels in the two margins
    o.append(f'<circle cx="34" cy="36" r="19" fill="{BLUE}"/>'
             f'<text x="34" y="43.5" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="#ffffff">{n}</text>')
    o.append(f'<g font-family="{FONT}" font-size="14" font-weight="600" fill="#1e293b">')
    for i, ln in enumerate(t["l"]):
        o.append(f'<text x="14" y="{86 + 19*i}">{esc(ln)}</text>')
    for i, ln in enumerate(t["r"]):
        o.append(f'<text x="{W-14}" y="{40 + 19*i}" text-anchor="end">{esc(ln)}</text>')
    o.append('</g>')
    o.append('</svg>')
    return "\n".join(o) + "\n"

if __name__ == "__main__":
    for n in (1, 2, 3):
        for lang in ("en", "it"):
            out = OUT / f"turnaround-{n}-{lang}.svg"
            out.write_text(svg(n, lang)); print("wrote", out.name)
    print("positions:", [(round(p[0]), round(p[1]), round(h)) for p, h in ((P0, H0), (P1, H1), (P2, H2), (P3, H3))])
