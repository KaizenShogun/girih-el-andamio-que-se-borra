"""¿Qué tesela sobrevive al borrado del andamio?

Mirando la lacería sin andamio veo que las estrellas de diez puntas siguen
gritando dónde estaba cada decágono, mientras que las otras cuatro teselas se
han disuelto en el tejido. Sospecha: lo que decide no es el tamaño, es si el
motivo de esa tesela es una FIGURA CERRADA o arcos abiertos.

Esto no mide el mundo: mira mi propio dibujo.
"""
import math
from girih import TILES, polygon, strapwork

K = 6  # decimales para identificar un punto


def nodes(segs):
    deg = {}
    for a, b in segs:
        for p in (a, b):
            k = (round(p[0], K), round(p[1], K))
            deg[k] = deg.get(k, 0) + 1
    return deg


print(f"{'tesela':9} {'aristas':>7} {'tramos':>7} {'extremos sueltos':>17}  motivo")
for name, angles in TILES.items():
    pts = polygon(angles)
    segs = strapwork(pts)
    deg = nodes(segs)
    sueltos = sum(1 for d in deg.values() if d == 1)
    # ¿hay un ciclo cerrado que no toque ningún borde?
    cerrado = (sueltos == 0)
    print(f"{name:9} {len(angles):>7} {len(segs):>7} {sueltos:>17}  "
          f"{'FIGURA CERRADA' if cerrado else 'arcos abiertos'}")

print()
print("Grados de los nodos (cuántos tramos concurren):")
for name, angles in TILES.items():
    deg = nodes(strapwork(polygon(angles)))
    hist = {}
    for d in deg.values():
        hist[d] = hist.get(d, 0) + 1
    print(f"  {name:9} {dict(sorted(hist.items()))}")
