# Optimización

Cómo convertir una decisión en un modelo matemático, resolverlo con un computador y, sobre todo,
leer lo que la solución dice: qué recurso aprieta, cuánto vale una hora más y hasta dónde puede
cambiar un dato sin que cambie la decisión.

**Nivel:** tercer año de Ingeniería Civil Industrial. **Antes:** álgebra lineal y cálculo.
**Software:** los modelos están escritos en OPL (IBM ILOG CPLEX Optimization Studio, con licencia
académica gratuita). Cada verificador también resuelve el modelo con un solver libre en Python, así
que las cifras se pueden comprobar sin CPLEX.

## Unidades

| N.º | Unidad | Estado (15-10-2026) |
|---|---|---|
| 1 | [Investigación de operaciones y modelos](unidades/01-investigacion-de-operaciones.md) | 0.1 · [PDF](pdf/01-investigacion-de-operaciones.pdf) |
| 2 | [Geometría de la optimización y método gráfico](unidades/02-metodo-grafico.md) | 0.1 · [PDF](pdf/02-metodo-grafico.pdf) |
| 3 | [Optimización no lineal básica](unidades/03-no-lineal.md) | 0.1 · [PDF](pdf/03-no-lineal.pdf) |
| 4 | [Modelamiento lineal I · producción y mezcla](unidades/04-modelamiento-produccion-y-mezcla.md) | 0.1 · [PDF](pdf/04-modelamiento-produccion-y-mezcla.pdf) |
| 5 | [Modelamiento lineal II · multiperíodo, transporte y asignación](unidades/05-modelamiento-multiperiodo-y-transporte.md) | 0.1 · [PDF](pdf/05-modelamiento-multiperiodo-y-transporte.pdf) |
| 6 | [Modelos con varios objetivos](unidades/06-varios-objetivos.md) | 0.1 · [PDF](pdf/06-varios-objetivos.pdf) |
| 7 | [Implementación en OPL](unidades/07-implementacion-en-opl.md) | 0.1 · [PDF](pdf/07-implementacion-en-opl.pdf) |
| 8 | [Forma estándar y método simplex](unidades/08-metodo-simplex.md) | 0.1 · [PDF](pdf/08-metodo-simplex.pdf) |
| 9 | [Simplex: dos fases, gran M y casos especiales](unidades/09-simplex-casos-especiales.md) | 0.1 · [PDF](pdf/09-simplex-casos-especiales.pdf) |
| 10 | [Dualidad](unidades/10-dualidad.md) | 0.1 · [PDF](pdf/10-dualidad.pdf) |
| 11 | [Holgura complementaria](unidades/11-holgura-complementaria.md) | 0.1 · [PDF](pdf/11-holgura-complementaria.pdf) |
| 12 | [Análisis de sensibilidad y precios sombra](unidades/12-sensibilidad.md) | 0.1 · [PDF](pdf/12-sensibilidad.pdf) |

## El caso integrador · Estampa Sur decide su mezcla

El mismo taller de serigrafía (ficticio) de Gestión de Operaciones y de Finanzas. Acá decide cuánto
producir de cada prenda en una semana con sus horas de estampado y planchado y su tinta.

| Unidad | Lo que calcula | Pasa a la siguiente |
|---|---|---|
| 1 Modelos | qué decide el taller, con qué restricciones y para qué | el problema planteado en palabras |
| 2 Método gráfico | la mezcla de poleras y polerones con dos recursos | vértices y óptimo |
| 3 No lineal | el precio de los polerones que maximiza la utilidad | precio y cantidad |
| 4 Modelamiento I | la mezcla de las cinco prendas | modelo y mezcla óptima |
| 5 Modelamiento II | producción de cuatro semanas con inventario y envío a tres tiendas | plan semanal |
| 6 Varios objetivos | margen contra tinta usada | mezcla de compromiso |
| 7 OPL | el modelo de la unidad 4 en `.mod` y `.dat` | el modelo que corre |
| 8 y 9 Simplex | la versión de dos productos, a mano | tabla final |
| 10 Dualidad | el dual: cuánto vale cada recurso | precios sombra |
| 11 Holgura complementaria | comprobar el óptimo con el dual | — |
| 12 Sensibilidad | si conviene pagar horas extra de planchado | decisión |

La fuente única de las cifras es `verificacion/caso_estampa_sur_lp.py`. Los modelos OPL de cada unidad
están en `modelos/`.

## Bibliografía

Obligatoria (la que fija el programa del ramo): Winston, *Investigación de operaciones: aplicaciones y
algoritmos*, Thomson, 4.ª ed., 2005. Complementaria: Hillier y Lieberman, *Introducción a la
investigación de operaciones*, McGraw-Hill, 7.ª ed., 2001.

## Cómo se usa

- **Estudiar:** lee la unidad en PDF (`pdf/`) o en Markdown (`unidades/`).
- **Practicar con IA:** pega `tutor/contexto.md` al inicio de la conversación.
- **Correr los modelos:** abre los `.mod` y `.dat` de `modelos/` en CPLEX Studio, o corre
  `python herramientas/opl.py <modelo.mod> <datos.dat>`.
- **Comprobar una cifra:** cada unidad tiene su script en `verificacion/`; con `--revisar` busca cada
  resultado en el texto.
