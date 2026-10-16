# Base abierta de ingeniería

Los ramos de Ingeniería Civil Industrial reescritos de cero para entender, practicar y estudiar con
un tutor de IA. Gratis. Por Camilo Merino.

**Léelo en la web:** https://camiloalonsomerino-spec.github.io/base-abierta-ingenieria/

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23423082.svg)](https://doi.org/10.5281/zenodo.23423082)

**Cómo citarla:** Merino, C. (2026). *Base abierta de ingeniería: ramos de Ingeniería Civil Industrial
reescritos de cero* (v0.1). Zenodo. https://doi.org/10.5281/zenodo.23423082

## Qué trae cada ramo

```
ramos/<ramo>/
  README.md          mapa del ramo: unidades, caso integrador y bibliografía
  unidades/NN-*.md   una unidad por archivo (teoría, ejemplo, 10 ejercicios con pauta, caso)
  pdf/NN-*.pdf       la misma unidad en PDF
  verificacion/      un script por unidad que recalcula cada cifra del texto
  tutor/contexto.md  lo que se le pega a una IA para que enseñe el ramo
```

## Ramos

| Ramo | Estado (16-10-2026) |
|---|---|
| [Gestión de Operaciones](ramos/gestion-de-operaciones/README.md) | 12 unidades en versión 0.1, verificadas |
| [Finanzas](ramos/finanzas/README.md) | 12 unidades en versión 0.1, verificadas |
| [Optimización](ramos/optimizacion/README.md) | 12 unidades en versión 0.1, verificadas; modelos en OPL |
| [Tópicos de Optimización](ramos/topicos-de-optimizacion/README.md) | 12 unidades en versión 0.1, verificadas; modelos en OPL |
| [Análisis de Datos](ramos/analisis-de-datos/README.md) | 12 unidades en versión 0.1, verificadas; Python con cuadernos |
| [Contabilidad y Costos](ramos/contabilidad-y-costos/README.md) | 12 unidades en versión 0.1, verificadas; planillas con fórmulas |
| [Bases de Datos](ramos/bases-de-datos/README.md) | 12 unidades en versión 0.1, verificadas; SQL que corre en SQLite, con las diferencias de MySQL |

## Cómo se construye un ramo

1. **Ingeniería inversa del material del curso.** Se saca la estructura: temas, orden, tipos de
   ejercicio, profundidad y de qué libro sale cada cosa. El material original no se publica.
2. **Reescritura desde cero.** Teoría propia, ejemplos y datos originales. Del libro se cita el
   capítulo y el número del problema; el enunciado no se copia.
3. **Cada cifra verificada.** Ningún número entra al texto sin que un script lo recalcule y lo
   encuentre escrito.
4. **Un caso integrador por ramo** que encadena las unidades, con datos de partida en cada una.

## Skills

Las cuatro skills de `skills/` dejan el método estándar para cualquier ramo:

| Skill | Qué hace |
|---|---|
| `base-ramo` | Orquesta un ramo completo: ingeniería inversa, caso, unidades en paralelo y revisión final |
| `base-ingenieria-inversa` | Del material del curso al mapa de unidades y al `ramo.yaml`, sin publicar el material |
| `base-caso-integrador` | Diseña el caso como un solo script encadenado, con colisiones y asserts |
| `base-unidad` | Escribe una unidad con su verificador y su PDF |

## Generar un PDF

```
pip install markdown
python herramientas/md_a_pdf.py ramos/gestion-de-operaciones/unidades/10-programacion-de-operaciones.md
```

Necesita Chrome, Edge o Chromium.

Para regenerar el sitio web (queda en `docs/`, que GitHub Pages publica):

```
python herramientas/sitio.py
```

Para revisar todas las cifras de un ramo:

```
python herramientas/revisar_ramo.py ramos/gestion-de-operaciones
```

Al escribir: los montos en pesos van con punto de miles (`$36.000`) o como `\$600`; dentro de una
fórmula, la coma decimal va como `{,}` y los miles como `{.}`.

## Licencia

- **Textos, unidades, PDF y figuras:** [CC BY 4.0](LICENSE-CONTENIDO.txt). Puedes copiarlos, adaptarlos y
  compartirlos, también con fines comerciales, citando a Camilo Merino y esta base.
- **Código** (`herramientas/`, `verificacion/`, `sql/`, `modelos/`, cuadernos y skills): [MIT](LICENSE).
- Los libros citados conservan sus derechos: se citan por capítulo y problema, no se reproducen.
