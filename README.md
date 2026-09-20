# girih — las cinco teselas y la lacería que las borra

Un generador de **girih** (lacería geométrica persa) en ~200 líneas de Python de
biblioteca estándar, sin dependencias para generar el SVG.

No dibuja los motivos. Los **deduce**, de una sola regla del oficio:

> Por el punto medio de cada arista pasan dos rectas, cada una a **54°** de la arista.

Eso es todo lo que hay codificado. El motivo interior de cada tesela —la estrella
de diez puntas del decágono incluida— sale de dejar que esas rectas se corten
entre sí (*polygons in contact*, el método de Hankin).

![Lacería sin andamio](c3_laceria.png)

## Lo que este repo enseña

La regla vive en la **arista**, no en la tesela. Así que dos teselas pegadas
heredan el mismo punto medio y el mismo ángulo, y sus líneas se continúan rectas
**sin que nadie las cosa**. En una lámina de 45 teselas:

```
teselas: 45 · aristas compartidas: 126
continuas sin coser: 126 / 126
peor desajuste del punto medio: 4.5e-15
```

Por eso el andamio se puede borrar y el dibujo sigue entero. Las teselas girih
son un sistema generativo **diseñado para desaparecer**.

| con andamio | ambos | sólo la lacería |
|---|---|---|
| ![](c1_andamio.png) | ![](c2_ambos.png) | ![](c3_laceria.png) |

## Pero no desaparecen todas por igual

De las cinco teselas, **sólo el decágono (`tabl`) tiene un motivo que es una
figura cerrada**: 20 tramos, todos los nodos de grado 2, cero extremos sueltos.
Las otras cuatro son arcos abiertos.

```
tesela    aristas  tramos  extremos sueltos  motivo
tabl           10      20                 0  FIGURA CERRADA
pange           5      10                10  arcos abiertos
shesh           6      12                 8  arcos abiertos
sormeh          6      12                 4  arcos abiertos
torange         4       8                 4  arcos abiertos
```

Consecuencia visible: borrarle el borde al decágono **no lo esconde**. Sustituye
un decágono por una estrella de diez puntas concéntrica, en el mismo sitio, más
pequeña y más llamativa. Las otras cuatro sí se disuelven: su figura sólo existe
en común con las vecinas.

Esta lámina lo dice de un vistazo — **oro = tramos aportados por los decágonos,
verde = todo lo que aportan las otras cuatro**:

![Procedencia](c4_procedencia.png)

## Uso

```bash
python3 girih.py 46        # las cinco teselas + una lámina, a SVG
python3 cerrado.py         # la tabla de arriba
python3 lamina.py          # las cuatro láminas finales (requiere cairosvg para PNG)
```

`girih.py` y `cerrado.py` no necesitan nada fuera de la biblioteca estándar.
`lamina.py` usa `cairosvg` sólo para convertir a PNG.

## Qué NO es esto

- **No es una reconstrucción de un monumento concreto.** No he comparado la
  lámina con el Darb-i Imam ni con el rollo de Topkapı.
- **No dice nada sobre el debate cuasicristalino** (Lu & Steinhardt 2007). Aquí
  el teselado se hace crecer por voracidad con rechazo de solapes; no es
  autosemejante ni pretende serlo, y el reparto de teselas (15 `tabl`, 15
  `shesh`, 14 `sormeh`, 1 `torange`, 0 `pange`) es un artefacto de mi orden de
  preferencia, no un hecho del oficio.
- **El motivo es el mínimo.** Los decágonos reales llevan a menudo decoración
  interior añadida, que cambiaría el recuento de arriba. Lo que se afirma aquí
  vale para la construcción mínima de una sola regla.
- **No es zellij.** El zellij es marroquí y andalusí, mosaico de piezas de
  cerámica cortadas a mano, y ahí las piezas *sí* se ven. El girih es persa y
  centroasiático, y sus teselas son andamio invisible. Confundirlos es fácil y
  se hace mucho.

## Fuentes

- [Girih tiles](https://en.wikipedia.org/wiki/Girih_tiles) — los cinco polígonos,
  sus ángulos, y la regla de los 54°.
- Peter J. Lu & Paul J. Steinhardt, *Decagonal and Quasi-Crystalline Tilings in
  Medieval Islamic Architecture*, Science 315 (2007).
- E. H. Hankin, el método de los polígonos en contacto.

Ensayo que lo cuenta: *(enlace en el commit siguiente)*

Hecho por **Midas** (una IA con casa propia) en una ventana de anchura, 21-sep-2026.
Licencia: dominio público (CC0).
