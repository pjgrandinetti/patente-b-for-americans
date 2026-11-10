#!/usr/bin/env python3
"""Draw review_media/roundabout-lanes-en.svg and -it.svg (20261103m).

A two-lane roundabout with four arms, seen from above, traffic counterclockwise
as in Italy. Two cars enter from the bottom arm. The one in the RIGHT lane
(green) takes the first exit or goes straight; the one in the LEFT lane
(blue) goes round in the inner lane for the left exit and moves to the outer
lane, with a right signal, before leaving. Every exit is taken from the outer
lane. The rule is circular 28819 para. d.4, the one the driving test page
states under Roundabouts; the maintainer's instructor drew the same at his
second lesson (2026-11-10). Light colors only, like the other review_media
figures, which sit on a light card in both themes. Edit the labels HERE and
rerun; both files are written from one drawing.
"""
import math
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "public_html" / "review_media"

L = {
 "en": dict(right="Right lane: first exit, or straight on",
            left="Left lane: left exit",
            move="Move to the right lane before your exit",
            yld="Yield on entering",
            signal_l="Left signal on while you go round",
            title="A roundabout with two lanes, seen from above, traffic going counterclockwise. From the entry at the bottom the car in the right lane takes the first exit or goes straight on; the car in the left lane goes round in the inner lane for the left exit and moves to the right lane, with a right signal, before leaving. Every exit is taken from the outer lane."),
 "it": dict(right="Corsia di destra: prima uscita, o dritto",
            left="Corsia di sinistra: uscita a sinistra",
            move="Spostati nella corsia di destra prima dell'uscita",
            yld="Dai la precedenza entrando",
            signal_l="Freccia a sinistra durante il giro",
            title="Una rotatoria a due corsie vista dall'alto, con il traffico in senso antiorario. Dall'ingresso in basso l'auto nella corsia di destra prende la prima uscita o prosegue dritto; l'auto nella corsia di sinistra percorre la corsia interna per l'uscita a sinistra e si sposta nella corsia di destra, con la freccia a destra, prima di uscire. Ogni uscita si prende dalla corsia esterna."),
}
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
W, H = 560, 560
CX, CY = 280, 268
R_ISLAND, R_IN, R_OUT = 62, 108, 154   # island edge, lane divider, outer kerb
ARM = 72                               # half-width of an arm (two lanes each way)
GREEN, BLUE = "#0F6E56", "#1D4ED8"
ROAD, ISLAND, LINE = "#E2E8F0", "#CBD5E1", "#ffffff"

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def P(x, y): return f"{x:.1f},{y:.1f}"
def pol(r, deg):
    a = math.radians(deg)
    return CX + r * math.cos(a), CY - r * math.sin(a)

def arc(r, a0, a1):
    """Arc on the circle of radius r from angle a0 to a1 (degrees, ccw positive)."""
    x0, y0 = pol(r, a0); x1, y1 = pol(r, a1)
    large = 1 if abs(a1 - a0) > 180 else 0
    # y points down in SVG, so a visually counterclockwise arc is sweep 0.
    return f"A {r} {r} 0 {large} 0 {x1:.1f} {y1:.1f}"

def car(x, y, deg, color):
    """A small car seen from above, nose pointing at `deg` (0 = right, ccw)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({-deg})">'
            f'<rect x="-11" y="-6.5" width="22" height="13" rx="3.5" fill="{color}"/>'
            f'<rect x="-2" y="-5" width="8" height="10" rx="2" fill="#ffffff" opacity=".55"/></g>')

def svg(lang):
    t = L[lang]; o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(t["title"])}">')
    o.append(f'<title>{esc(t["title"])}</title>')
    o.append('<defs>'
             f'<marker id="ag" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{GREEN}"/></marker>'
             f'<marker id="ab" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>'
             '</defs>')
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>')
    # Roads: four arms and the ring.
    o.append(f'<g fill="{ROAD}">')
    o.append(f'<rect x="{CX-ARM}" y="0" width="{2*ARM}" height="{CY}"/>')
    o.append(f'<rect x="{CX-ARM}" y="{CY}" width="{2*ARM}" height="{H-CY}"/>')
    o.append(f'<rect x="0" y="{CY-ARM}" width="{CX}" height="{2*ARM}"/>')
    o.append(f'<rect x="{CX}" y="{CY-ARM}" width="{W-CX}" height="{2*ARM}"/>')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{R_OUT}"/>')
    o.append('</g>')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{R_ISLAND}" fill="{ISLAND}"/>')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{R_ISLAND+4}" fill="none" stroke="#94a3b8" stroke-width="1.5"/>')
    # Lane markings: the ring divider (dashed) and each arm's centre and lane lines.
    o.append(f'<g stroke="{LINE}" stroke-width="2.5" fill="none">')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{R_IN}" stroke-dasharray="10 9"/>')
    for (x0, y0, x1, y1) in [(CX, 0, CX, CY-R_OUT), (CX, CY+R_OUT, CX, H), (0, CY, CX-R_OUT, CY), (CX+R_OUT, CY, W, CY)]:
        o.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke-width="3"/>')  # between the two directions
    for d in (-ARM/2, ARM/2):
        o.append(f'<line x1="{CX+d}" y1="0" x2="{CX+d}" y2="{CY-R_OUT}" stroke-dasharray="10 9"/>')
        o.append(f'<line x1="{CX+d}" y1="{CY+R_OUT}" x2="{CX+d}" y2="{H}" stroke-dasharray="10 9"/>')
        o.append(f'<line x1="0" y1="{CY+d}" x2="{CX-R_OUT}" y2="{CY+d}" stroke-dasharray="10 9"/>')
        o.append(f'<line x1="{CX+R_OUT}" y1="{CY+d}" x2="{W}" y2="{CY+d}" stroke-dasharray="10 9"/>')
    o.append('</g>')
    # Yield line at the bottom entry (the right-hand half of the arm) and its triangle.
    o.append(f'<line x1="{CX+2}" y1="{CY+R_OUT+2}" x2="{CX+ARM-2}" y2="{CY+R_OUT+2}" stroke="#ffffff" stroke-width="4" stroke-dasharray="6 5"/>')
    ty = CY + R_OUT + 22
    o.append(f'<polygon points="{CX+ARM+10},{ty} {CX+ARM+34},{ty} {CX+ARM+22},{ty+21}" fill="#ffffff" stroke="#DC2626" stroke-width="4" stroke-linejoin="round"/>')
    # Lanes of the entry arm: right lane centre x = CX + 3*ARM/4, left lane centre x = CX + ARM/4.
    xr, xl = CX + 3*ARM/4, CX + ARM/4
    r_outer, r_inner = (R_IN + R_OUT) / 2, (R_ISLAND + R_IN) / 2 + 4
    # GREEN, right lane: enters the outer lane, first exit (to the right, exiting along y = CY + 3*ARM/4).
    ye = CY + 3*ARM/4
    g1 = (f'M {P(xr, H-28)} L {P(xr, CY+R_OUT+30)} '
          f'Q {P(xr, CY+R_OUT-20)} {P(*pol(r_outer, -60))} '
          f'{arc(r_outer, -60, -28)} '
          f'Q {P(CX+R_OUT-12, ye)} {P(CX+R_OUT+30, ye)} L {P(W-30, ye)}')
    # GREEN dotted: straight on, staying in the outer lane, exiting the top arm
    # in the right lane heading north, x = CX + 3*ARM/4.
    xt = CX + 3*ARM/4
    g2 = (f'M {P(*pol(r_outer, -28))} {arc(r_outer, -28, 68)} '
          f'Q {P(xt-4, CY-R_OUT+6)} {P(xt, CY-R_OUT-30)} L {P(xt, 30)}')
    # BLUE, left lane: enters the inner lane, goes round past the top, moves out to the outer lane and leaves by the left arm along y = CY - 3*ARM/4.
    yl = CY - 3*ARM/4
    b1 = (f'M {P(xl, H-28)} L {P(xl, CY+R_OUT+30)} '
          f'Q {P(xl, CY+R_OUT-30)} {P(*pol(r_inner, -70))} '
          f'{arc(r_inner, -70, 100)} '
          f'Q {P(*pol(r_inner+10, 122))} {P(*pol(r_outer, 138))} '
          f'{arc(r_outer, 138, 150)} '
          f'C {P(*pol(r_outer+2, 160))} {P(CX-R_OUT-26, yl+2)} {P(CX-R_OUT-54, yl)} L {P(30, yl)}')
    o.append(f'<g fill="none" stroke-width="5" stroke-linecap="round">')
    o.append(f'<path d="{g2}" stroke="{GREEN}" stroke-dasharray="2 11" marker-end="url(#ag)"/>')
    o.append(f'<path d="{g1}" stroke="{GREEN}" marker-end="url(#ag)"/>')
    o.append(f'<path d="{b1}" stroke="{BLUE}" marker-end="url(#ab)"/>')
    o.append('</g>')
    # The two cars at the entry, and the blue car again where it moves out.
    o.append(car(xr, H-52, 90, GREEN))
    o.append(car(xl, H-52, 90, BLUE))
    mx, my = pol((r_inner + r_outer) / 2 + 2, 130)
    o.append(car(mx, my, 232, BLUE))
    # Labels. A white halo keeps them readable over the road.
    o.append(f'<g font-family="{FONT}" font-size="14" font-weight="600">')
    def label(x, y, text, color, anchor="start"):
        o.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="#ffffff" stroke="#ffffff" stroke-width="5" stroke-linejoin="round" paint-order="stroke">{esc(text)}</text>')
        o.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}">{esc(text)}</text>')
    label(W-16, H-56, t["right"], GREEN, "end")
    label(W-16, H-36, t["yld"], "#DC2626", "end")
    label(16, H-56, t["left"], BLUE)
    label(16, H-36, t["signal_l"], BLUE)
    label(16, CY-ARM-40, t["move"], BLUE)
    o.append('</g>')
    o.append('</svg>')
    return "\n".join(o) + "\n"

if __name__ == "__main__":
    for lang in ("en", "it"):
        (OUT / f"roundabout-lanes-{lang}.svg").write_text(svg(lang))
        print("wrote", OUT / f"roundabout-lanes-{lang}.svg")
