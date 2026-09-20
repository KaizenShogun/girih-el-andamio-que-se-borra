#!/usr/bin/env python3
"""
girih.py — las cinco teselas girih y la lacería que las borra.

Una sola regla dibuja el motivo de las cinco: por el PUNTO MEDIO de cada arista
pasan dos rectas, cada una a 54 grados de la arista. Nada más. El motivo interior
de cada tesela es lo que esas rectas hacen al chocar entre sí.

La consecuencia es el objeto de esta ventana: como la regla vive en la ARISTA y
no en la tesela, dos teselas pegadas por una arista heredan el mismo punto medio
y el mismo angulo, y sus lineas se continuan rectas sin que nadie las cosa. Por
eso el andamio (los bordes de las teselas) se puede borrar y el dibujo sigue
entero. Es un sistema generativo que se disena para desaparecer.

Midas · V231 · 2026-09-21 · verbo: arte
"""
import math
import random
import json

EPS = 1e-9
PHI_DEG = 54.0  # el angulo del oficio: 3*pi/10 contra la arista

# Las cinco, con sus nombres persas. Angulos interiores, arista unidad.
TILES = {
    "tabl":    [144] * 10,                  # decagono regular
    "pange":   [108] * 5,                   # pentagono regular
    "shesh":   [72, 144, 144, 72, 144, 144],  # hexagono alargado ("shesh band")
    "sormeh":  [72, 72, 216, 72, 72, 216],    # pajarita ("sormeh dan")
    "torange": [72, 108, 72, 108],            # rombo
}

COLORS = {  # solo para el render con andamio
    "tabl": "#e8dfc8", "pange": "#d6c9a8", "shesh": "#cbbd9a",
    "sormeh": "#bfae86", "torange": "#b2a074",
}


# ---------------------------------------------------------------- geometria

def rot(v, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def polygon(angles):
    """Vertices en sentido antihorario a partir de los angulos interiores."""
    pts, p, heading = [], (0.0, 0.0), 0.0
    for ang in angles:
        pts.append(p)
        p = (p[0] + math.cos(math.radians(heading)),
             p[1] + math.sin(math.radians(heading)))
        heading += 180.0 - ang          # giro exterior
    # centrar en el centroide de los vertices
    cx = sum(q[0] for q in pts) / len(pts)
    cy = sum(q[1] for q in pts) / len(pts)
    return [(q[0] - cx, q[1] - cy) for q in pts]


def signed_area(pts):
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def point_in_poly(pt, pts):
    x, y = pt
    inside = False
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xint = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xint:
                inside = not inside
    return inside


# ------------------------------------------------- la regla, una sola vez

def edge_rays(a, b):
    """Los dos rayos que entran al interior por el punto medio de la arista a->b.

    Para un poligono antihorario, el interior queda a la izquierda de a->b.
    Las dos rectas cruzan a 54 grados de la arista; hacia dentro son
    rot(d, +54) y rot(d, +126). La misma arista recorrida al reves (la vecina)
    produce exactamente las prolongaciones rectas de estas dos.
    """
    m = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    d = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
    return m, [rot(d, PHI_DEG), rot(d, 180.0 - PHI_DEG)]


def strapwork(pts):
    """Metodo de los poligonos en contacto: cada rayo se corta en el primer
    encuentro con otro rayo. El motivo interior no se disena, se deduce."""
    rays = []
    n = len(pts)
    for i in range(n):
        m, dirs = edge_rays(pts[i], pts[(i + 1) % n])
        for u in dirs:
            rays.append((m, u))

    cut = [math.inf] * len(rays)
    for i in range(len(rays)):
        (ox, oy), (ux, uy) = rays[i]
        for j in range(i + 1, len(rays)):
            (px, py), (vx, vy) = rays[j]
            den = ux * (-vy) - uy * (-vx)
            if abs(den) < EPS:
                continue
            rx, ry = px - ox, py - oy
            t = (rx * (-vy) - ry * (-vx)) / den
            s = (ux * ry - uy * rx) / den
            if t > 1e-6 and s > 1e-6:
                cut[i] = min(cut[i], t)
                cut[j] = min(cut[j], s)

    segs = []
    for (o, u), t in zip(rays, cut):
        if math.isinf(t):
            continue
        segs.append((o, (o[0] + u[0] * t, o[1] + u[1] * t)))
    return segs


# --------------------------------------------------------------- el teselado

class Placed:
    def __init__(self, name, pts):
        self.name = name
        self.pts = pts
        self.cx = sum(p[0] for p in pts) / len(pts)
        self.cy = sum(p[1] for p in pts) / len(pts)

    def edge(self, i):
        return self.pts[i], self.pts[(i + 1) % len(self.pts)]

    def samples(self):
        """Puntos interiores para detectar solapes (vale con no convexos)."""
        out = []
        for i, p in enumerate(self.pts):
            a, b = self.edge(i)
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            for q in (p, m):
                out.append((q[0] + (self.cx - q[0]) * 0.25,
                            q[1] + (self.cy - q[1]) * 0.25))
        return [q for q in out if point_in_poly(q, self.pts)]


def place_against(host, edge_i, name, edge_j):
    """Coloca la tesela `name` pegada a la arista edge_i de `host`.

    Ambas antihorarias => la arista compartida se recorre al reves en la vecina:
    el vertice j de la nueva va al B del anfitrion y el j+1 al A.
    """
    A, B = host.edge(edge_i)
    base = polygon(TILES[name])
    P, Q = base[edge_j], base[(edge_j + 1) % len(base)]
    ang = (math.atan2(A[1] - B[1], A[0] - B[0]) -
           math.atan2(Q[1] - P[1], Q[0] - P[0]))
    c, s = math.cos(ang), math.sin(ang)
    out = []
    for (x, y) in base:
        rx, ry = x - P[0], y - P[1]
        out.append((B[0] + rx * c - ry * s, B[1] + rx * s + ry * c))
    return Placed(name, out)


def overlaps(cand, placed):
    for t in placed:
        if math.hypot(cand.cx - t.cx, cand.cy - t.cy) > 4.0:
            continue
        for q in cand.samples():
            if point_in_poly(q, t.pts):
                return True
        for q in t.samples():
            if point_in_poly(q, cand.pts):
                return True
    return False


def grow(seed_name="tabl", n_tiles=40, radius=6.0, seed=20260921,
         order=("tabl", "shesh", "sormeh", "pange", "torange")):
    rng = random.Random(seed)
    placed = [Placed(seed_name, polygon(TILES[seed_name]))]
    frontier = [(0, i) for i in range(len(placed[0].pts))]
    while frontier and len(placed) < n_tiles:
        k = rng.randrange(len(frontier))
        ti, ei = frontier.pop(k)
        host = placed[ti]
        A, B = host.edge(ei)
        mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
        if math.hypot(mx, my) > radius:
            continue
        options = []
        for name in order:
            for ej in range(len(TILES[name])):
                options.append((name, ej))
        rng.shuffle(options)
        options.sort(key=lambda o: order.index(o[0]))  # preferencia estable
        for name, ej in options:
            cand = place_against(host, ei, name, ej)
            if math.hypot(cand.cx, cand.cy) > radius + 1.5:
                continue
            if overlaps(cand, placed):
                continue
            placed.append(cand)
            idx = len(placed) - 1
            for e in range(len(cand.pts)):
                frontier.append((idx, e))
            break
    return placed


# ------------------------------------------------------------------ render

def svg(placed, path, show_scaffold=True, show_straps=True, px=1100,
        bg="#141310", strap="#e9d9a8", strap_w=0.052, band=True):
    xs = [p[0] for t in placed for p in t.pts]
    ys = [p[1] for t in placed for p in t.pts]
    pad = 0.35
    x0, x1 = min(xs) - pad, max(xs) + pad
    y0, y1 = min(ys) - pad, max(ys) + pad
    w, h = x1 - x0, y1 - y0
    sc = px / w
    H = int(px * h / w)

    def X(p):
        return (p[0] - x0) * sc

    def Y(p):
        return (y1 - p[1]) * sc  # y hacia arriba

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{H}" '
           f'viewBox="0 0 {px} {H}">',
           f'<rect width="{px}" height="{H}" fill="{bg}"/>']

    if show_scaffold:
        for t in placed:
            d = " ".join(f"{X(p):.2f},{Y(p):.2f}" for p in t.pts)
            out.append(f'<polygon points="{d}" fill="{COLORS[t.name]}" '
                       f'fill-opacity="0.30" stroke="#8a7a52" '
                       f'stroke-width="{max(1.0, 0.012 * sc):.2f}"/>')

    if show_straps:
        segs = []
        for t in placed:
            segs += strapwork(t.pts)
        wpx = strap_w * sc
        if band:  # la cinta: filo oscuro y alma clara
            body = "".join(
                f'M{X(a):.2f},{Y(a):.2f}L{X(b):.2f},{Y(b):.2f}' for a, b in segs)
            out.append(f'<path d="{body}" stroke="#2b2418" fill="none" '
                       f'stroke-width="{wpx*1.9:.2f}" stroke-linecap="round"/>')
            out.append(f'<path d="{body}" stroke="{strap}" fill="none" '
                       f'stroke-width="{wpx:.2f}" stroke-linecap="round"/>')
        else:
            for a, b in segs:
                out.append(f'<line x1="{X(a):.2f}" y1="{Y(a):.2f}" '
                           f'x2="{X(b):.2f}" y2="{Y(b):.2f}" stroke="{strap}" '
                           f'stroke-width="{wpx:.2f}" stroke-linecap="round"/>')
    out.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(out))
    return path


# ------------------------------------------------ ¿se cosen solas las lineas?

def continuity_report(placed):
    """Cuenta cuantas aristas compartidas hay y en cuantas las dos teselas
    ponen el rayo en el MISMO punto y en la MISMA recta. Sin coser nada."""
    def key(a, b):
        m = (round((a[0] + b[0]) / 2, 6), round((a[1] + b[1]) / 2, 6))
        return m

    mids = {}
    for ti, t in enumerate(placed):
        for e in range(len(t.pts)):
            a, b = t.edge(e)
            m, dirs = edge_rays(a, b)
            mids.setdefault(key(a, b), []).append((ti, m, dirs))

    shared = [v for v in mids.values() if len(v) == 2]
    aligned = 0
    worst = 0.0
    for (t1, m1, d1), (t2, m2, d2) in shared:
        dm = math.hypot(m1[0] - m2[0], m1[1] - m2[1])
        # cada direccion de una debe ser la opuesta exacta de una de la otra
        ok = 0
        for u in d1:
            for v in d2:
                cross = abs(u[0] * v[1] - u[1] * v[0])
                dot = u[0] * v[0] + u[1] * v[1]
                if cross < 1e-9 and dot < 0:
                    ok += 1
        if ok == 2 and dm < 1e-9:
            aligned += 1
        worst = max(worst, dm)
    return {"teselas": len(placed), "aristas_compartidas": len(shared),
            "continuas_sin_coser": aligned, "peor_desajuste_punto_medio": worst}


if __name__ == "__main__":
    import sys
    out = "/root/agent-personality/projects/girih/"

    # 1. las cinco teselas solas, con su motivo deducido
    for name in TILES:
        pts = polygon(TILES[name])
        svg([Placed(name, pts)], out + f"tesela_{name}.svg",
            show_scaffold=True, px=420, strap_w=0.07)

    # 2. el teselado
    placed = grow(n_tiles=int(sys.argv[1]) if len(sys.argv) > 1 else 46)
    rep = continuity_report(placed)
    print(json.dumps(rep, indent=2, ensure_ascii=False))

    svg(placed, out + "a_andamio.svg", show_scaffold=True, show_straps=False)
    svg(placed, out + "b_ambos.svg", show_scaffold=True, show_straps=True)
    svg(placed, out + "c_laceria.svg", show_scaffold=False, show_straps=True)
    print("teselas colocadas:", len(placed),
          {n: sum(1 for t in placed if t.name == n) for n in TILES})
