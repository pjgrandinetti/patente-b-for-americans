#!/usr/bin/env python3
"""Draw review_media/speed-limits-en.svg and speed-limits-it.svg (20261028m).

The speed limits as a grid of road types against conditions, colored by how
each figure is found: green follows from the standard row by one step of
20 km/h (a sign up, rain or towing down), purple is the fog cap an operator
may post on the two fastest roads, "slow to visibility" is fog elsewhere, gray is unchanged, orange falls
outside the series of odd tens and has to be memorized. Topic 11 shows it at
the head of "How to remember the numbers" and the Reference page inside "How
to remember the speeds". Edit the figures or labels HERE and rerun; the two
files are written from one table so they cannot disagree. Light colors only,
like the other review_media figures, which sit on a light card in both themes.
"""
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "public_html" / "review_media"

L = {
 "en": dict(cols=["Autostrada", "Principale", "Secondaria", "Town"],
            rows=["Where signed", "Standard", "Rain", "Dense fog", "New driver", "Towing"],
            veh="Vehicle limits", vsub=["Quadricycle", "Moped", "Farm, tires", "Farm, tracks"],
            leg=["Follows the rule", "Unchanged", "Outside the series", "Cap that may be posted", "Does not apply"],
            vis=["Slow to", "visibility"],
            title="Italian speed limits in km/h by road type and condition. The standard row and one step of 20 km/h up or down give most figures; in dense fog a cap of 50 may be posted on the two fastest roads, and elsewhere you slow to what you can see; 100 and 80 on the autostrada and the vehicle limits 80, 45, 40 and 15 must be memorized."),
 "it": dict(cols=["Autostrada", "Principale", "Secondaria", "Centro abitato"],
            rows=["Dove segnalato", "Ordinario", "Pioggia", "Nebbia fitta", "Neopatentato", "Traino"],
            veh="Limiti per veicolo", vsub=["Quadriciclo", "Ciclomotore", "Agricola, gomme", "Agricola, cingoli"],
            leg=["Segue la regola", "Invariato", "Fuori dalla serie", "Tetto che può essere imposto", "Non si applica"],
            vis=["Adegua alla", "visibilità"],
            title="Limiti di velocità italiani in km/h per tipo di strada e condizione. La riga ordinaria e un passo di 20 km/h in su o in giù danno quasi tutte le cifre; con nebbia fitta sulle due strade più veloci può essere imposto un tetto di 50, e altrove si rallenta secondo la visibilità; 100 e 80 in autostrada e i limiti per veicolo 80, 45, 40 e 15 vanno memorizzati."),
}
# (value, kind): r = follows the rule, u = unchanged, x = outside the series, None = does not apply
GRID = [
 [(150, "r"), None, None, (70, "r")],
 [(130, "s"), (110, "s"), (90, "s"), (50, "s")],
 [(110, "r"), (90, "r"), (90, "u"), (50, "u")],
 [(50, "f"), (50, "f"), "vis", "vis"],
 [(100, "x"), (90, "r"), (90, "u"), (50, "u")],
 [(80, "x"), (70, "r"), (70, "r"), (50, "u")],
]
VEH = [80, 45, 40, 15]
C = {"r": ("#E1F5EE", "#0F6E56", "#085041"), "s": ("#E1F5EE", "#0F6E56", "#085041"),
     "u": ("#F1EFE8", "#B4B2A9", "#5F5E5A"), "x": ("#FAECE7", "#D85A30", "#712B13"),
     "f": ("#EEEDFE", "#534AB7", "#3C3489")}
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
X0, CW, GAP, RH, RG, TOP = 160, 104, 10, 40, 8, 44

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")

def svg(lang):
    t = L[lang]; out = []
    W = X0 + 4 * CW + 3 * GAP + 16
    vy = TOP + 6 * (RH + RG) + 10
    ly = vy + 56 + 26
    H = ly + 22 + 24
    cx = lambda j: X0 + j * (CW + GAP)
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(t["title"])}">')
    out.append(f'<title>{esc(t["title"])}</title>')
    out.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>')
    out.append(f'<g font-family="{FONT}">')
    out.append(f'<text x="16" y="{TOP-14}" font-size="12" fill="#64748b">km/h</text>')
    for j, c in enumerate(t["cols"]):
        out.append(f'<text x="{cx(j)+CW/2}" y="{TOP-14}" text-anchor="middle" font-size="13" font-weight="600" fill="#1e293b">{esc(c)}</text>')
    for i, row in enumerate(GRID):
        y = TOP + i * (RH + RG)
        bold = ' font-weight="600"' if i == 1 else ''
        out.append(f'<text x="16" y="{y+RH/2+5}" font-size="13"{bold} fill="#1e293b">{esc(t["rows"][i])}</text>')
        for j, cell in enumerate(row):
            x = cx(j)
            if cell == "vis":
                f_, s_, ink = C["u"]
                out.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{RH}" rx="5" fill="{f_}" stroke="{s_}"/>')
                out.append(f'<text x="{x+CW/2}" y="{y+16}" text-anchor="middle" font-size="11.5" fill="{ink}">{esc(t["vis"][0])}</text>')
                out.append(f'<text x="{x+CW/2}" y="{y+30}" text-anchor="middle" font-size="11.5" fill="{ink}">{esc(t["vis"][1])}</text>')
                continue
            if cell is None:
                out.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{RH}" rx="5" fill="none" stroke="#B4B2A9" stroke-dasharray="4 3"/>')
                continue
            v, k = cell; fill, stroke, ink = C[k]
            sw = "2" if k in ("s", "x", "f") else "1"
            w = "700" if k != "u" else "500"
            out.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{RH}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
            out.append(f'<text x="{x+CW/2}" y="{y+RH/2+6}" text-anchor="middle" font-size="17" font-weight="{w}" fill="{ink}">{v}</text>')
    out.append(f'<text x="16" y="{vy+30}" font-size="13" font-weight="600" fill="#1e293b">{esc(t["veh"])}</text>')
    fill, stroke, ink = C["x"]
    for j, v in enumerate(VEH):
        x = cx(j)
        out.append(f'<rect x="{x}" y="{vy}" width="{CW}" height="52" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        out.append(f'<text x="{x+CW/2}" y="{vy+24}" text-anchor="middle" font-size="17" font-weight="700" fill="{ink}">{v}</text>')
        out.append(f'<text x="{x+CW/2}" y="{vy+42}" text-anchor="middle" font-size="11.5" fill="{ink}">{esc(t["vsub"][j])}</text>')
    # Two rows: the three kinds of figure, then the fog cap and the empty cell.
    lpos = [(16, 0), (16 + 170, 0), (16 + 300, 0), (16, 24), (16 + 300, 24)]
    keys = ["r", "u", "x", "f", None]
    for n, ((x, dy), k) in enumerate(zip(lpos, keys)):
        ly0 = ly + dy
        if k is None:
            out.append(f'<rect x="{x}" y="{ly0-11}" width="14" height="14" rx="3" fill="none" stroke="#B4B2A9" stroke-dasharray="3 2"/>')
        else:
            f_, s_, _ = C[k]
            out.append(f'<rect x="{x}" y="{ly0-11}" width="14" height="14" rx="3" fill="{f_}" stroke="{s_}" stroke-width="{2 if k in ("x", "f") else 1}"/>')
        out.append(f'<text x="{x+20}" y="{ly0}" font-size="12" fill="#334155">{esc(t["leg"][n])}</text>')
    out.append('</g></svg>')
    return "\n".join(out) + "\n"

if __name__ == "__main__":
    for lang in L:
        (OUT / f"speed-limits-{lang}.svg").write_text(svg(lang))
        print("wrote", OUT / f"speed-limits-{lang}.svg")
