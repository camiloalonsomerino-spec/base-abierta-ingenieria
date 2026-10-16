# Tópicos de Optimización

La continuación de Optimización: cuando las decisiones son enteras o de sí y no (abrir o no una
bodega, lanzar o no un producto), cuando el problema es una red (rutas, flujos, árboles) y cuando el
problema es tan grande que hay que conformarse con una buena solución en vez de la óptima.

**Nivel:** tercer año de Ingeniería Civil Industrial. **Antes:** Optimización (programación lineal,
simplex y dualidad). **Software:** OPL (CPLEX), como en Optimización; los algoritmos de redes y las
heurísticas se muestran también en Python.

## Unidades

| N.º | Unidad | Estado (15-10-2026) |
|---|---|---|
| 1 | [Programación entera: por qué no basta redondear](unidades/01-programacion-entera.md) | 0.1 · [PDF](pdf/01-programacion-entera.pdf) |
| 2 | [Variables binarias I · decisiones, dependencias, mochila y asignación](unidades/02-binarias-decisiones-y-mochila.md) | 0.1 · [PDF](pdf/02-binarias-decisiones-y-mochila.pdf) |
| 3 | [Variables binarias II · costo fijo, gran M, K de N, lote mínimo y funciones por partes](unidades/03-binarias-costo-fijo-y-gran-m.md) | 0.1 · [PDF](pdf/03-binarias-costo-fijo-y-gran-m.pdf) |
| 4 | [Problemas clásicos · vendedor viajero, ruteo, corte, cobertura y localización](unidades/04-problemas-clasicos.md) | 0.1 · [PDF](pdf/04-problemas-clasicos.pdf) |
| 5 | [Solución gráfica y ramificación y acotamiento](unidades/05-ramificacion-y-acotamiento.md) | 0.1 · [PDF](pdf/05-ramificacion-y-acotamiento.pdf) |
| 6 | [Simplex dual, planos cortantes y ramificación y corte](unidades/06-planos-cortantes.md) | 0.1 · [PDF](pdf/06-planos-cortantes.pdf) |
| 7 | [Redes y árbol de expansión mínima](unidades/07-arbol-de-expansion-minima.md) | 0.1 · [PDF](pdf/07-arbol-de-expansion-minima.pdf) |
| 8 | [Ruta más corta y flujo máximo](unidades/08-ruta-mas-corta-y-flujo-maximo.md) | 0.1 · [PDF](pdf/08-ruta-mas-corta-y-flujo-maximo.pdf) |
| 9 | [Problema de transporte y sus métodos](unidades/09-transporte.md) | 0.1 · [PDF](pdf/09-transporte.pdf) |
| 10 | [Asignación y método húngaro](unidades/10-asignacion.md) | 0.1 · [PDF](pdf/10-asignacion.pdf) |
| 11 | [Heurísticas constructivas y búsqueda local](unidades/11-heuristicas.md) | 0.1 · [PDF](pdf/11-heuristicas.pdf) |
| 12 | [Metaheurísticas · tabú, recocido simulado y algoritmos genéticos](unidades/12-metaheuristicas.md) | 0.1 · [PDF](pdf/12-metaheuristicas.pdf) |

## El caso integrador · Estampa Sur crece

El mismo taller ficticio de Gestión de Operaciones, Finanzas y Optimización. Ahora tiene seis
tiendas (ficticias, con distancias ficticias) y decisiones que no admiten fracciones.

| Unidad | Lo que calcula |
|---|---|
| 1 | La mezcla de Optimización en cajas de 24: redondear contra el óptimo entero |
| 2 | Qué productos nuevos lanzar con un presupuesto, con dependencias y exclusiones |
| 3 | Si comprar una segunda máquina (costo fijo) y cuántas cajas hacer en ella (lote mínimo); flow shop |
| 4 | La ruta del camión que visita las seis tiendas (vendedor viajero) |
| 5 y 6 | El turno del sábado (dos prendas, en cajas) resuelto a mano: árbol, Gomory y una faceta |
| 7 | Los enlaces de radio que conectan tiendas y taller al menor largo (árbol mínimo) |
| 8 | La ruta más corta a cada tienda y cuántas cajas por día llegan a la tienda Cerro (flujo máximo) |
| 9 | Envíos desde el taller y un segundo taller a cuatro tiendas (transporte) |
| 10 | Qué operario va a cada máquina (asignación) |
| 11 | La ruta del camión con vecino más cercano y 2-opt: se queda en 84 km, el óptimo es 78 |
| 12 | Recocido simulado sobre la misma ruta: llega a 78 km |

La fuente única de las cifras es `verificacion/caso_estampa_sur_red.py`.

## Bibliografía

Obligatoria (la que fija el programa del ramo): Winston, *Investigación de operaciones: aplicaciones y
algoritmos*, Thomson, 4.ª ed., 2005; Hillier y Lieberman, *Investigación de operaciones*, McGraw-Hill,
7.ª ed., 2001.

## Cómo se usa

- **Estudiar:** lee la unidad en PDF (`pdf/`) o en Markdown (`unidades/`).
- **Practicar con IA:** pega `tutor/contexto.md` al inicio de la conversación.
- **Correr los modelos:** los `.mod` y `.dat` de `modelos/` en CPLEX Studio, o
  `python herramientas/opl.py <modelo.mod> <datos.dat>`.
- **Comprobar una cifra:** cada unidad tiene su script en `verificacion/`; con `--revisar` busca cada
  resultado en el texto.
