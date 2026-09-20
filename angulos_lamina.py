"""Tres ángulos, la misma lámina. El 54 no compra la continuidad (esa es gratis
a cualquier ángulo): compra QUIÉN sobrevive al borrado del andamio."""
import girih, cairosvg
from girih import grow

OUT = "/root/agent-personality/projects/girih/"


def plate(phi, path, px=900):
    girih.PHI_DEG = phi
    placed = grow(n_tiles=45, radius=6.0, seed=2718)
    xs = [p[0] for t in placed for p in t.pts]
    ys = [p[1] for t in placed for p in t.pts]
    x0, x1 = min(xs) - .3, max(xs) + .3
    y0, y1 = min(ys) - .3, max(ys) + .3
    sc = px / (x1 - x0)
    H = int(px * (y1 - y0) / (x1 - x0))
    X = lambda p: (p[0] - x0) * sc
    Y = lambda p: (y1 - p[1]) * sc
    segs = [s for t in placed for s in girih.strapwork(t.pts)]
    d = "".join(f'M{X(a):.2f},{Y(a):.2f}L{X(b):.2f},{Y(b):.2f}' for a, b in segs)
    w = 0.046 * sc
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{H}" '
         f'viewBox="0 0 {px} {H}">'
         f'<rect width="{px}" height="{H}" fill="#14120e"/>'
         f'<path d="{d}" stroke="#231d14" fill="none" stroke-width="{w*2:.2f}" '
         f'stroke-linecap="round"/>'
         f'<path d="{d}" stroke="#e9d9a8" fill="none" stroke-width="{w:.2f}" '
         f'stroke-linecap="round"/></svg>')
    open(path, "w").write(s)
    cairosvg.svg2png(url=path, write_to=path[:-4] + ".png", output_width=900)


for phi, tag in ((54.0, "54"), (36.0, "36"), (60.0, "60")):
    plate(phi, OUT + f"d_phi{tag}.svg")
    print("hecho", phi)
