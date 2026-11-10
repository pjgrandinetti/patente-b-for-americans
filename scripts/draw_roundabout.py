#!/usr/bin/env python3
"""Draw the four roundabout figures of the driving test page (20261103s).

review_media/roundabout-first-{en,it}.svg, roundabout-straight-{en,it}.svg and
roundabout-left-{en,it}.svg and roundabout-uturn-{en,it}.svg: a two-lane roundabout with four arms, seen from
above, traffic counterclockwise as in Italy, and ONE car entering from the
bottom in each figure. First exit: right lane, right signal on the approach.
Straight on: right lane, no signal on entering, right signal once past the
first exit. Left exit: left lane, left signal on entering and kept on round
the inner lane, then right signal and a move to the outer lane past the exit
before yours. Back the way you came (uturn, added 20261103t at the
maintainer's word: it is a legal maneuver): as for the left exit, one exit
further; the circular does not describe it, and it follows from d.4. The car is drawn again at each point where its signal matters,
with the signal in amber on that side. The rule is circular 28819 para. d.

One figure held all three cars until 20261103r. The maintainer found it too
complicated (three colors, letters, six label blocks), so each exit has its
own figure, one car and one color, and nothing has to be told apart.

The markings are the ones an Italian roundabout carries: a raised splitter
island on every arm with a double continuous line before it, solid edge
lines, a row of white triangles pointing at the arriving driver as the yield
line at every entry, a broken edge line across every exit, a dashed line
between the ring's two lanes, entry lane lines that turn continuous on the
approach, and the yield sign at each entry. Light colors only. Edit the
labels HERE and rerun; all six files are written from one drawing.
"""
import math
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "public_html" / "review_media"

# For each figure and language: label blocks by corner, and the title.
L = {
 "first": {
  "en": dict(br=["Right lane.", "Signal right on the approach", "and keep it on to exit."],
             title="A two-lane roundabout seen from above, traffic counterclockwise. A car approaches at the bottom in the right lane with its right signal on, enters the outer lane, and leaves by the first exit with the signal still on."),
  "it": dict(br=["Corsia di destra.", "Freccia a destra avvicinandoti,", "e tienila fino all'uscita."],
             title="Una rotatoria a due corsie vista dall'alto, traffico in senso antiorario. Un'auto si avvicina dal basso nella corsia di destra con la freccia a destra, entra nella corsia esterna ed esce alla prima uscita con la freccia ancora inserita.")},
 "straight": {
  "en": dict(br=["Right lane.", "No signal as you enter."], tr=["Past the first exit,", "signal right to exit."],
             title="A two-lane roundabout seen from above, traffic counterclockwise. A car enters at the bottom in the right lane with no signal, follows the outer lane past the first exit, then signals right and leaves by the exit straight ahead."),
  "it": dict(br=["Corsia di destra.", "Nessuna freccia entrando."], tr=["Superata la prima uscita,", "freccia a destra per uscire."],
             title="Una rotatoria a due corsie vista dall'alto, traffico in senso antiorario. Un'auto entra dal basso nella corsia di destra senza freccia, percorre la corsia esterna oltre la prima uscita, poi mette la freccia a destra ed esce all'uscita di fronte.")},
 "left": {
  "en": dict(bl=["Left lane.", "Signal left as you enter", "and keep it on."], tl=["Past the exit before yours,", "signal right, move to the", "right lane and exit."],
             title="A two-lane roundabout seen from above, traffic counterclockwise. A car enters at the bottom in the left lane with its left signal on, goes round in the inner lane with the signal on, and once past the exit straight ahead signals right, moves to the outer lane and leaves by the left exit."),
  "it": dict(bl=["Corsia di sinistra.", "Freccia a sinistra entrando,", "e tienila inserita."], tl=["Superata l'uscita prima", "della tua, freccia a destra,", "spostati nella corsia di", "destra ed esci."],
             title="Una rotatoria a due corsie vista dall'alto, traffico in senso antiorario. Un'auto entra dal basso nella corsia di sinistra con la freccia a sinistra, percorre la corsia interna con la freccia inserita e, superata l'uscita di fronte, mette la freccia a destra, si sposta nella corsia esterna ed esce a sinistra.")},
 "uturn": {
  "en": dict(br=["Left lane.", "Signal left as you enter", "and keep it on."], bl=["Past the left exit,", "signal right, move to the", "right lane and exit."],
             title="A two-lane roundabout seen from above, traffic counterclockwise. A car enters at the bottom in the left lane with its left signal on, goes round in the inner lane with the signal on past the first, second and left exits, then signals right, moves to the outer lane and leaves by the road it came from."),
  "it": dict(br=["Corsia di sinistra.", "Freccia a sinistra entrando,", "e tienila inserita."], bl=["Superata l'uscita a sinistra,", "freccia a destra, spostati", "nella corsia di destra", "ed esci."],
             title="Una rotatoria a due corsie vista dall'alto, traffico in senso antiorario. Un'auto entra dal basso nella corsia di sinistra con la freccia a sinistra, percorre la corsia interna con la freccia inserita oltre la prima uscita, quella di fronte e quella a sinistra, poi mette la freccia a destra, si sposta nella corsia esterna ed esce dalla strada da cui è arrivata.")},
}
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
W = H = 640
CX = CY = 320
RI, RD, RO = 66, 113, 160            # island kerb, lane divider, outer edge of the ring
R_IN, R_OUT = (RI + RD) / 2, (RD + RO) / 2
LANE, ISL, EDGE = 34, 14, 3          # lane width, splitter half-width at the ring, margin outside the edge line
U_FAR, U_NEAR = 250, 178             # the arm widens between these distances from the centre
BLUE, RED, AMBER = "#1D4ED8", "#DC2626", "#F59E0B"
ROAD, GRASS, KERB, WHITE = "#B4BCC8", "#DCE8DA", "#7C8798", "#ffffff"
ARMS = [(0, 1), (1, 0), (0, -1), (-1, 0)]   # outward directions: bottom, right, top, left

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def f(p): return f"{p[0]:.1f},{p[1]:.1f}"
def right_of(d): return (d[1], -d[0])       # the entry side: right of a driver heading for the centre
def loc(d, u, v):
    r = right_of(d)
    return (CX + u * d[0] + v * r[0], CY + u * d[1] + v * r[1])
def isl(u):
    if u >= U_FAR: return 0.0
    if u <= U_NEAR: return float(ISL)
    return ISL * (U_FAR - u) / (U_FAR - U_NEAR)
def ring(r, deg):
    a = math.radians(deg); return (CX + r * math.cos(a), CY + r * math.sin(a))
def tan(deg):                               # heading of counterclockwise traffic (screen y points down)
    a = math.radians(deg); return (math.sin(a), -math.cos(a))
def cubic(A, a, B, b, k):
    return f"C {f((A[0]+k*a[0], A[1]+k*a[1]))} {f((B[0]-k*b[0], B[1]-k*b[1]))} {f(B)}"
def arc(r, a1):                             # counterclockwise on the map is sweep 0 in SVG
    return f"A {r} {r} 0 0 0 {f(ring(r, a1))}"
def car(p, deg, color, sig=None):
    """A car seen from above, nose at `deg`. sig 'L' or 'R' lights that side's turn signals (amber)."""
    out = (f'<g transform="translate({p[0]:.1f} {p[1]:.1f}) rotate({-deg})">'
           f'<rect x="-12" y="-7" width="24" height="14" rx="4" fill="{color}" stroke="#ffffff" stroke-width="1"/>'
           f'<rect x="-1" y="-5" width="7" height="10" rx="2" fill="#ffffff" opacity=".6"/>')
    if sig:
        y = 8 if sig == "R" else -8          # the car's right is +y once the nose points along +x
        o = 1 if sig == "R" else -1
        for x in (10, -10):
            out += (f'<circle cx="{x}" cy="{y}" r="4.2" fill="{AMBER}" stroke="#7C2D12" stroke-width="1"/>'
                    f'<path d="M {x-4} {y+o*7} L {x-6} {y+o*11} M {x} {y+o*8} L {x} {y+o*12.5} M {x+4} {y+o*7} L {x+6} {y+o*11}" stroke="{AMBER}" stroke-width="2" stroke-linecap="round" fill="none"/>')
    return out + '</g>'

def svg(which, lang):
    t = L[which][lang]; o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(t["title"])}">')
    o.append(f'<title>{esc(t["title"])}</title>')
    o.append('<defs>'
             f'<clipPath id="card"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12"/></clipPath>'
             f'<marker id="ab" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4.2" markerHeight="4.2" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>'
             '</defs>')
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="#f8fafc"/>')
    o.append('<g clip-path="url(#card)">')
    hw_far, hw_near = LANE * 2 + EDGE, ISL + LANE * 2 + EDGE
    UA = 172                                 # where the corner kerb leaves the arm's edge
    QK = 105.5                               # control of the corner kerb, so it clears the ring by a few px
    # ---- road surface: the ring, the four arms, the four rounded corners
    o.append(f'<g fill="{ROAD}">')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{RO}"/>')
    for d in ARMS:
        pts = [loc(d, 340, hw_far), loc(d, U_FAR, hw_far), loc(d, U_NEAR, hw_near), loc(d, 90, hw_near),
               loc(d, 90, -hw_near), loc(d, U_NEAR, -hw_near), loc(d, U_FAR, -hw_far), loc(d, 340, -hw_far)]
        o.append(f'<polygon points="{" ".join(f(p) for p in pts)}"/>')
        n = right_of(d)                      # the arm on this arm's entry side
        A, A2 = loc(d, UA, hw_near), loc(n, UA, -hw_near)
        Q = (CX + QK * (d[0] + n[0]), CY + QK * (d[1] + n[1]))
        o.append(f'<path d="M {f(A)} Q {f(Q)} {f(A2)} L {CX},{CY} Z"/>')
    o.append('</g>')
    # ---- the central island and the splitter islands (raised, kerbed)
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{RI}" fill="{GRASS}" stroke="{KERB}" stroke-width="2"/>')
    for d in ARMS:
        tip, b1, b2 = loc(d, U_FAR - 6, 0), loc(d, 166, -(ISL - 2)), loc(d, 166, ISL - 2)
        o.append(f'<path d="M {f(tip)} Q {f(loc(d, 205, -4))} {f(b1)} L {f(b2)} Q {f(loc(d, 205, 4))} {f(tip)} Z" fill="{GRASS}" stroke="{KERB}" stroke-width="1.5" stroke-linejoin="round"/>')
    # ---- markings
    o.append(f'<g fill="none" stroke="{WHITE}" stroke-width="2.5" stroke-linecap="butt">')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{RI+5}"/>')                               # edge line round the island
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{RD}" stroke-dasharray="12 10"/>')        # between the ring's two lanes
    for d in ARMS:
        n = right_of(d)
        e, e2 = hw_far - EDGE, hw_near - EDGE
        # edge line: down this arm's entry side, round the corner, up the next arm's exit side
        A, A2 = loc(d, UA, e2), loc(n, UA, -e2)
        Q = (CX + (QK - 2) * (d[0] + n[0]), CY + (QK - 2) * (d[1] + n[1]))
        o.append(f'<path d="M {f(loc(d, 340, e))} L {f(loc(d, U_FAR, e))} L {f(loc(d, U_NEAR, e2))} L {f(A)} Q {f(Q)} {f(A2)} '
                 f'L {f(loc(n, U_NEAR, -e2))} L {f(loc(n, U_FAR, -e))} L {f(loc(n, 340, -e))}"/>')
        # the two directions: double continuous line up to the splitter island
        for v in (-2.5, 2.5):
            o.append(f'<line x1="{loc(d,340,v)[0]:.1f}" y1="{loc(d,340,v)[1]:.1f}" x2="{loc(d,U_FAR-2,v)[0]:.1f}" y2="{loc(d,U_FAR-2,v)[1]:.1f}" stroke-width="2"/>')
        # entry lanes: broken far out, continuous on the approach
        um = 222
        o.append(f'<path d="M {f(loc(d, 340, LANE))} L {f(loc(d, U_FAR, LANE))} L {f(loc(d, um, isl(um)+LANE))}" stroke-dasharray="12 10"/>')
        o.append(f'<path d="M {f(loc(d, um, isl(um)+LANE))} L {f(loc(d, U_NEAR+6, ISL+LANE))}"/>')
        # exit lanes: broken all the way
        o.append(f'<path d="M {f(loc(d, U_NEAR-4, -(ISL+LANE)))} L {f(loc(d, U_FAR, -LANE))} L {f(loc(d, 340, -LANE))}" stroke-dasharray="12 10"/>')
        # across the exit: the ring's edge line, broken
        pts = []
        for k in range(0, 13):
            a = math.radians(5.5 + (30 - 5.5) * k / 12)
            pts.append(loc(d, 166 * math.cos(a), -166 * math.sin(a)))
        o.append(f'<path d="M {" L ".join(f(p) for p in pts)}" stroke-dasharray="6 6"/>')
    o.append('</g>')
    # across each entry: the yield line, white triangles with the point toward the arriving driver
    o.append(f'<g fill="{WHITE}">')
    for d in ARMS:
        for k in range(6):
            a = math.radians(7.2 + 4.0 * k)
            rad = (math.cos(a), math.sin(a))                 # in (u, v)
            per = (-math.sin(a), math.cos(a))
            base = (174 * rad[0], 174 * rad[1]); tip = (186 * rad[0], 186 * rad[1])
            p1 = loc(d, base[0] - 4.6 * per[0], base[1] - 4.6 * per[1])
            p2 = loc(d, base[0] + 4.6 * per[0], base[1] + 4.6 * per[1])
            o.append(f'<polygon points="{f(p1)} {f(p2)} {f(loc(d, tip[0], tip[1]))}"/>')
    o.append('</g>')
    # the yield sign at each entry, on the driver's right
    for d in ARMS:
        x, y = loc(d, 214, hw_near + 20)
        o.append(f'<polygon points="{x-11:.1f},{y-9:.1f} {x+11:.1f},{y-9:.1f} {x:.1f},{y+10:.1f}" fill="{WHITE}" stroke="{RED}" stroke-width="3.5" stroke-linejoin="round"/>')
    # ---- the car's path. A node on an arm takes the heading of the lane there,
    # which leans with the taper, so the path bends once and does not wobble.
    def unit(P, Q):
        dx, dy = Q[0] - P[0], Q[1] - P[1]; n = math.hypot(dx, dy); return (dx / n, dy / n)
    def entry(v_far):                         # up the bottom arm in the lane whose far centre is v_far
        d = ARMS[0]
        S, F, Y = loc(d, 304, v_far), loc(d, U_FAR, v_far), loc(d, 186, ISL + v_far)
        h = unit(F, Y)
        return Y, h, f'M {f(S)} L {f(F)} {cubic(F, (0, -1), Y, h, 18)}'
    def leave(d, P, hP, k):                   # from a point on the ring out by arm d's right-hand exit lane
        X, Xf, E = loc(d, 186, -(ISL + LANE * 1.5)), loc(d, U_FAR, -LANE * 1.5), loc(d, 300, -LANE * 1.5)
        h = unit(X, Xf)
        return f'{cubic(P, hP, X, h, k)} {cubic(X, h, Xf, d, 18)} L {f(E)}'
    def heading(deg):                         # of counterclockwise traffic at that point of the ring, for car()
        a = math.radians(deg); return math.degrees(math.atan2(math.cos(a), math.sin(a)))
    VR, VL = LANE * 1.5, LANE * .5
    cars = []
    if which == "first":
        Y, h, path = entry(VR); M1 = ring(R_OUT, 50)
        path += f' {cubic(Y, h, M1, tan(50), 40)} {leave(ARMS[1], M1, tan(50), 40)}'
        cars = [(loc(ARMS[0], 284, VR), 90, "R"), (loc(ARMS[1], 252, -VR), 0, "R")]
    elif which == "straight":
        Y, h, path = entry(VR); P1, P2 = ring(R_OUT, 52), ring(R_OUT, -34)
        path += f' {cubic(Y, h, P1, tan(52), 40)} {arc(R_OUT, -34)} {leave(ARMS[2], P2, tan(-34), 36)}'
        cars = [(loc(ARMS[0], 284, VR), 90, None), (ring(R_OUT, -12), heading(-12), "R"), (loc(ARMS[2], 252, -VR), 90, "R")]
    elif which == "uturn":
        # The left-exit maneuver carried one exit further. Circular 28819 does not
        # describe this case; it follows from d.4.
        Y, h, path = entry(VL)
        N1, N2, N3 = ring(R_IN, 48), ring(R_IN, -170), ring(R_OUT, -214)
        K = 34
        c1 = (N2[0] + K * tan(-170)[0], N2[1] + K * tan(-170)[1]); c2 = (N3[0] - K * tan(-214)[0], N3[1] - K * tan(-214)[1])
        path += (f' {cubic(Y, h, N1, tan(48), 40)} {arc(R_IN, -60)} {arc(R_IN, -170)} '
                 f'C {f(c1)} {f(c2)} {f(N3)} {leave(ARMS[0], N3, tan(-214), 34)}')
        mid = tuple((N2[i] + 3 * c1[i] + 3 * c2[i] + N3[i]) / 8 for i in (0, 1))
        der = tuple((-N2[i] - c1[i] + c2[i] + N3[i]) for i in (0, 1))
        cars = [(loc(ARMS[0], 284, VL), 90, "L"), (ring(R_IN, 0), heading(0), "L"), (ring(R_IN, -90), heading(-90), "L"),
                (mid, math.degrees(math.atan2(-der[1], der[0])), "R"), (loc(ARMS[0], 252, -VR), 270, "R")]
    else:
        Y, h, path = entry(VL)
        N1, N2, N3 = ring(R_IN, 48), ring(R_IN, -80), ring(R_OUT, -124)
        K = 34                                # the lane change, begun past the exit before yours
        c1 = (N2[0] + K * tan(-80)[0], N2[1] + K * tan(-80)[1]); c2 = (N3[0] - K * tan(-124)[0], N3[1] - K * tan(-124)[1])
        path += (f' {cubic(Y, h, N1, tan(48), 40)} {arc(R_IN, -80)} '
                 f'C {f(c1)} {f(c2)} {f(N3)} {leave(ARMS[3], N3, tan(-124), 34)}')
        mid = tuple((N2[i] + 3 * c1[i] + 3 * c2[i] + N3[i]) / 8 for i in (0, 1))
        der = tuple((-N2[i] - c1[i] + c2[i] + N3[i]) for i in (0, 1))
        cars = [(loc(ARMS[0], 284, VL), 90, "L"), (ring(R_IN, 0), heading(0), "L"),
                (mid, math.degrees(math.atan2(-der[1], der[0])), "R"), (loc(ARMS[3], 252, -VR), 180, "R")]
    o.append(f'<path d="{path}" fill="none" stroke="{BLUE}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ab)"/>')
    for pt, deg, sig in cars:
        o.append(car(pt, deg, BLUE, sig))
    o.append('</g>')
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="none" stroke="#cbd5e1" stroke-width="1.5"/>')
    # ---- labels, in the free corners
    o.append(f'<g font-family="{FONT}" font-size="15" font-weight="600" fill="#1e293b">')
    def block(x, y0, lines, anchor="start"):
        for i, ln in enumerate(lines):
            o.append(f'<text x="{x}" y="{y0 + 20*i}" text-anchor="{anchor}">{esc(ln)}</text>')
    if "bl" in t: block(16, H - 16 - 20 * (len(t["bl"]) - 1), t["bl"])
    if "br" in t: block(W - 16, H - 16 - 20 * (len(t["br"]) - 1), t["br"], "end")
    if "tl" in t: block(16, 30, t["tl"])
    if "tr" in t: block(W - 16, 30, t["tr"], "end")
    o.append('</g>')
    o.append('</svg>')
    return "\n".join(o) + "\n"

if __name__ == "__main__":
    for which in ("first", "straight", "left", "uturn"):
        for lang in ("en", "it"):
            out = OUT / f"roundabout-{which}-{lang}.svg"
            out.write_text(svg(which, lang)); print("wrote", out)
