#!/usr/bin/env python3
"""Draw review_media/roundabout-lanes-en.svg and -it.svg (20261103m, redrawn n).

A two-lane roundabout with four arms, seen from above, traffic counterclockwise
as in Italy. Two cars enter from the bottom arm. The one in the RIGHT lane
(green) takes the first exit, or goes straight on (dotted); the one in the LEFT
lane (blue) goes round in the inner lane for the left exit and moves to the
outer lane before leaving. The rule is circular 28819 para. d.4, which the
driving test page states under Roundabouts.

The markings are the ones an Italian roundabout carries (redrawn in n after
the maintainer found the first version technically wrong): a raised splitter
island between entry and exit on every arm, a double continuous line between
the two directions before it, solid edge lines, a row of white triangles with
their points toward the arriving driver as the yield line at every entry, a
broken edge line across every exit, a dashed line between the two lanes of the
ring, lane lines that turn continuous on the approach, and the yield sign at
each entry. Light colors only, like the other review_media figures. Edit the
labels HERE and rerun; both files are written from one drawing.
"""
import math
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "public_html" / "review_media"

L = {
 "en": dict(bl=["C. Left exit: left lane.", "Signal left as you enter", "and keep it on."],
            tl=["C. Past the exit before yours,", "signal right, move to the", "right lane and exit."],
            br=["A. First exit: right lane.", "Signal right on the approach", "and keep it on to exit."],
            tr=["B. Straight on: right lane.", "No signal as you enter.", "Past the first exit,", "signal right to exit."],
            mid=["Always signal", "right to exit"],
            title="A roundabout with two lanes, seen from above, traffic going counterclockwise, with three cars entering at the bottom. The green car (A), in the right lane, signals right on the approach and takes the first exit. The purple car (B), in the right lane, gives no signal on entering, goes straight on, and signals right once past the first exit. The blue car (C), in the left lane, signals left on entering, goes round in the inner lane, then signals right and moves to the right lane for the left exit. Every car signals right to exit. Each entry has a yield line of white triangles."),
 "it": dict(bl=["C. Uscita a sinistra: corsia", "di sinistra. Freccia a sinistra", "entrando, e tienila inserita."],
            tl=["C. Superata l'uscita prima", "della tua, freccia a destra,", "spostati nella corsia di", "destra ed esci."],
            br=["A. Prima uscita: corsia di", "destra. Freccia a destra", "avvicinandoti, e tienila", "fino all'uscita."],
            tr=["B. Dritto: corsia di destra.", "Nessuna freccia entrando.", "Superata la prima uscita,", "freccia a destra per uscire."],
            mid=["Per uscire,", "sempre freccia", "a destra"],
            title="Una rotatoria a due corsie vista dall'alto, con il traffico in senso antiorario e tre auto che entrano dal basso. L'auto verde (A), nella corsia di destra, mette la freccia a destra avvicinandosi e prende la prima uscita. L'auto viola (B), nella corsia di destra, entra senza freccia, prosegue dritto e mette la freccia a destra superata la prima uscita. L'auto blu (C), nella corsia di sinistra, mette la freccia a sinistra entrando, percorre la corsia interna, poi mette la freccia a destra e si sposta nella corsia di destra per l'uscita a sinistra. Ogni auto esce con la freccia a destra. Ogni ingresso ha la linea di dare precedenza a triangoli bianchi."),
}
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
W = H = 640
CX = CY = 320
RI, RD, RO = 66, 113, 160            # island kerb, lane divider, outer edge of the ring
R_IN, R_OUT = (RI + RD) / 2, (RD + RO) / 2
LANE, ISL, EDGE = 34, 14, 3          # lane width, splitter half-width at the ring, margin outside the edge line
U_FAR, U_NEAR = 250, 178             # the arm widens between these distances from the centre
GREEN, BLUE, PURPLE, RED, AMBER = "#0F6E56", "#1D4ED8", "#7E22CE", "#DC2626", "#F59E0B"
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

def svg(lang):
    t = L[lang]; o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(t["title"])}">')
    o.append(f'<title>{esc(t["title"])}</title>')
    o.append('<defs>'
             f'<clipPath id="card"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12"/></clipPath>'
             f'<marker id="ag" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4.2" markerHeight="4.2" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{GREEN}"/></marker>'
             f'<marker id="ab" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4.2" markerHeight="4.2" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>'
             f'<marker id="ap" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4.2" markerHeight="4.2" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{PURPLE}"/></marker>'
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
    # ---- the three paths. A node on an arm takes the heading of the lane there,
    # which leans with the taper, so the paths bend once and do not wobble.
    def unit(P, Q):
        dx, dy = Q[0] - P[0], Q[1] - P[1]; n = math.hypot(dx, dy); return (dx / n, dy / n)
    def entry(v_far, u0=304):                 # up the bottom arm in the lane whose far centre is v_far
        d = ARMS[0]
        S, F, Y = loc(d, u0, v_far), loc(d, U_FAR, v_far), loc(d, 186, ISL + v_far)
        h = unit(F, Y)
        return S, Y, h, f'M {f(S)} L {f(F)} {cubic(F, (0, -1), Y, h, 18)}'
    def leave(d, P, hP, k):                   # from a point on the ring out by arm d's right-hand exit lane
        X, Xf, E = loc(d, 186, -(ISL + LANE * 1.5)), loc(d, U_FAR, -LANE * 1.5), loc(d, 300, -LANE * 1.5)
        h = unit(X, Xf)
        return f'{cubic(P, hP, X, h, k)} {cubic(X, h, Xf, d, 18)} L {f(E)}'
    # Green and purple are one behind the other in the middle of the right lane.
    # Where they share the lane the green line is dashed over the purple one.
    VG = VP = LANE * 1.5; RP = R_OUT
    M1, P1, P2 = ring(R_OUT, 50), ring(RP, 52), ring(RP, -34)
    _, gY, gh, gpath = entry(VG, 262)
    g1 = f'M {f(gY)} {cubic(gY, gh, M1, tan(50), 40)} {leave(ARMS[1], M1, tan(50), 40)}'
    _, pY, ph, ppath = entry(VP, 306)
    g2 = f'{ppath} {cubic(pY, ph, P1, tan(52), 40)} A {RP} {RP} 0 0 0 {f(P2)} {leave(ARMS[2], P2, tan(-34), 36)}'
    _, bY, bh, bpath = entry(LANE * .5)
    N1, N2, N3 = ring(R_IN, 48), ring(R_IN, -80), ring(R_OUT, -124)
    K = 34                                    # the lane change, begun past the exit before yours
    c1 = (N2[0] + K * tan(-80)[0], N2[1] + K * tan(-80)[1]); c2 = (N3[0] - K * tan(-124)[0], N3[1] - K * tan(-124)[1])
    b1 = (f'{bpath} {cubic(bY, bh, N1, tan(48), 40)} {arc(R_IN, -80)} '
          f'C {f(c1)} {f(c2)} {f(N3)} {leave(ARMS[3], N3, tan(-124), 34)}')
    o.append('<g fill="none" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round">')
    o.append(f'<path d="{g2}" stroke="{PURPLE}" marker-end="url(#ap)"/>')
    o.append(f'<path d="{gpath}" stroke="{GREEN}" stroke-dasharray="9 9" stroke-linecap="butt"/>')
    o.append(f'<path d="{g1}" stroke="{GREEN}" marker-end="url(#ag)"/>')
    o.append(f'<path d="{b1}" stroke="{BLUE}" marker-end="url(#ab)"/>')
    o.append('</g>')
    # Turn signals (circular 28819 d). Entering: right for the first exit, none
    # for straight on, left for the left exit. Leaving: always right.
    o.append(car(loc(ARMS[0], 248, VG), 90, GREEN, "R"))
    o.append(car(loc(ARMS[0], 292, VP), 90, PURPLE))
    o.append(car(loc(ARMS[0], 286, LANE * .5), 90, BLUE, "L"))
    sa = -12                                  # straight on: past the first exit, signal right
    o.append(car(ring(RP, sa), math.degrees(math.atan2(math.cos(math.radians(sa)), math.sin(math.radians(sa)))), PURPLE, "R"))
    # the blue car again, half-way through its lane change, pointing along the path
    mid = tuple((N2[i] + 3 * c1[i] + 3 * c2[i] + N3[i]) / 8 for i in (0, 1))
    der = tuple((-N2[i] - c1[i] + c2[i] + N3[i]) for i in (0, 1))
    o.append(car(mid, math.degrees(math.atan2(-der[1], der[0])), BLUE, "R"))
    # Each car and each way out carries its letter, so the three are told apart
    # without color (blue and purple are a weak pair for red-green color blindness).
    def badge(pt, ch, color):
        o.append(f'<circle cx="{pt[0]:.1f}" cy="{pt[1]:.1f}" r="9.5" fill="#ffffff" stroke="{color}" stroke-width="2.5"/>'
                 f'<text x="{pt[0]:.1f}" y="{pt[1]+4.6:.1f}" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="700" fill="#0f172a">{ch}</text>')
    ga, pa, ba = loc(ARMS[0], 248, VG), loc(ARMS[0], 292, VP), loc(ARMS[0], 286, LANE * .5)
    badge((ga[0] + 31, ga[1]), "A", GREEN); badge((pa[0] + 25, pa[1]), "B", PURPLE); badge((ba[0] - 31, ba[1]), "C", BLUE)
    badge(loc(ARMS[1], 276, -LANE * 1.5 + 21), "A", GREEN)
    badge(loc(ARMS[2], 276, -LANE * 1.5 + 21), "B", PURPLE)
    badge(loc(ARMS[3], 276, -LANE * 1.5 + 21), "C", BLUE)
    badge(ring(RP - 25, sa), "B", PURPLE)
    badge((mid[0] + 4, mid[1] + 23), "C", BLUE)
    o.append('</g>')
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="none" stroke="#cbd5e1" stroke-width="1.5"/>')
    # ---- labels, one block in each free corner
    o.append(f'<g font-family="{FONT}" font-size="14.5" font-weight="600">')
    def block(x, y0, lines, color, anchor="start"):
        for i, s in enumerate(lines):
            o.append(f'<text x="{x}" y="{y0 + 19*i}" text-anchor="{anchor}" fill="{color}">{esc(s)}</text>')
    block(16, H - 16 - 19 * (len(t["bl"]) - 1), t["bl"], BLUE)
    block(W - 16, H - 16 - 19 * (len(t["br"]) - 1), t["br"], GREEN, "end")
    block(16, 30, t["tl"], BLUE)
    block(W - 16, 30, t["tr"], PURPLE, "end")
    for i, ln in enumerate(t["mid"]):         # the rule common to all three, on the island
        o.append(f'<text x="{CX}" y="{CY + 5 - 9.5 * (len(t["mid"]) - 1) + 19*i:.1f}" text-anchor="middle" font-size="13.5" fill="#334155">{esc(ln)}</text>')
    o.append('</g>')
    o.append('</svg>')
    return "\n".join(o) + "\n"

if __name__ == "__main__":
    for lang in ("en", "it"):
        (OUT / f"roundabout-lanes-{lang}.svg").write_text(svg(lang))
        print("wrote", OUT / f"roundabout-lanes-{lang}.svg")
