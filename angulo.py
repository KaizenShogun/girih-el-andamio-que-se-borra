"""¿Qué hace realmente el 54? Iba a escribir que sin él las líneas dejan de
continuarse en las aristas. Mi propia derivación dice que eso es falso: la
continuidad sólo necesita que las DOS caras usen el mismo ángulo. Compruebo."""
import girih
from girih import grow, continuity_report, polygon, strapwork, TILES

for phi in (54.0, 45.0, 36.0, 60.0, 72.0, 30.0):
    girih.PHI_DEG = phi
    p = grow(n_tiles=45, radius=6.0, seed=2718)
    rep = continuity_report(p)
    # ¿el decágono sigue siendo el único cerrado?
    cerradas = []
    for name, ang in TILES.items():
        segs = strapwork(polygon(ang))
        deg = {}
        for a, b in segs:
            for q in (a, b):
                k = (round(q[0], 6), round(q[1], 6))
                deg[k] = deg.get(k, 0) + 1
        if sum(1 for d in deg.values() if d == 1) == 0:
            cerradas.append(name)
    print(f"phi={phi:5.1f}  continuas {rep['continuas_sin_coser']:>3}/"
          f"{rep['aristas_compartidas']:<3}  figuras cerradas: "
          f"{cerradas if cerradas else '(ninguna)'}")
