"""La lámina final: el andamio, la lacería, y la lacería coloreada por
procedencia — que enseña de un vistazo lo que el conteo dice:
el decágono es el único que sobrevive a que le borren el borde."""
import math
import cairosvg
from girih import (TILES, COLORS, grow, polygon, strapwork, Placed,
                   continuity_report)

OUT = "/root/agent-personality/projects/girih/"
BG = "#14120e"
ORO = "#e9d9a8"

# El decágono aparte; los otros cuatro en un tono que se lee como tejido.
PROC = {"tabl": "#f2dd9a", "pange": "#6f8f8a", "shesh": "#6f8f8a",
        "sormeh": "#6f8f8a", "torange": "#6f8f8a"}


def render(placed, path, scaffold=False, straps=True, by_origin=False,
           px=1400, w_strap=0.050):
    xs = [p[0] for t in placed for p in t.pts]
    ys = [p[1] for t in placed for p in t.pts]
    pad = 0.30
    x0, x1 = min(xs) - pad, max(xs) + pad
    y0, y1 = min(ys) - pad, max(ys) + pad
    sc = px / (x1 - x0)
    H = int(px * (y1 - y0) / (x1 - x0))
    X = lambda p: (p[0] - x0) * sc
    Y = lambda p: (y1 - p[1]) * sc

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{H}" '
         f'viewBox="0 0 {px} {H}">',
         f'<rect width="{px}" height="{H}" fill="{BG}"/>']

    if scaffold:
        for t in placed:
            d = " ".join(f"{X(p):.2f},{Y(p):.2f}" for p in t.pts)
            s.append(f'<polygon points="{d}" fill="{COLORS[t.name]}" '
                     f'fill-opacity="0.26" stroke="#7d6e49" stroke-width="1.4"/>')

    if straps:
        wpx = w_strap * sc
        groups = {}
        for t in placed:
            groups.setdefault(t.name if by_origin else "_", []).extend(
                strapwork(t.pts))
        # filo oscuro común primero: la cinta parece una sola pieza
        allsegs = [seg for v in groups.values() for seg in v]
        d = "".join(f'M{X(a):.2f},{Y(a):.2f}L{X(b):.2f},{Y(b):.2f}'
                    for a, b in allsegs)
        s.append(f'<path d="{d}" stroke="#231d14" fill="none" '
                 f'stroke-width="{wpx*2.0:.2f}" stroke-linecap="round"/>')
        for name, segs in groups.items():
            col = PROC[name] if by_origin else ORO
            d = "".join(f'M{X(a):.2f},{Y(a):.2f}L{X(b):.2f},{Y(b):.2f}'
                        for a, b in segs)
            s.append(f'<path d="{d}" stroke="{col}" fill="none" '
                     f'stroke-width="{wpx:.2f}" stroke-linecap="round"/>')

    s.append("</svg>")
    open(path, "w").write("\n".join(s))
    cairosvg.svg2png(url=path, write_to=path[:-4] + ".png", output_width=1100)
    return path


if __name__ == "__main__":
    placed = grow(n_tiles=70, radius=6.0, seed=2718,
                  order=("tabl", "shesh", "sormeh", "pange", "torange"))
    print(continuity_report(placed))
    print({n: sum(1 for t in placed if t.name == n) for n in TILES})
    render(placed, OUT + "l1_andamio.svg", scaffold=True, straps=False)
    render(placed, OUT + "l2_ambos.svg", scaffold=True, straps=True)
    render(placed, OUT + "l3_laceria.svg", scaffold=False, straps=True)
    render(placed, OUT + "l4_procedencia.svg", scaffold=False, straps=True,
           by_origin=True)
