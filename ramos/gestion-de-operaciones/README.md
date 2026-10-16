# Gestión de Operaciones

Cómo se planifica, se produce y se controla lo que fabrica o entrega una organización: desde
pronosticar la demanda hasta decidir en qué orden pasa cada pedido por cada máquina.

**Nivel:** tercer año de Ingeniería Civil Industrial. **Antes:** Optimización (programación lineal) y
probabilidad básica.

## Unidades

| N.º | Unidad | Estado (15-10-2026) |
|---|---|---|
| 1 | [Introducción y productividad](unidades/01-introduccion-y-productividad.md) | 0.1 · [PDF](pdf/01-introduccion-y-productividad.pdf) |
| 2 | [Estrategia de operaciones](unidades/02-estrategia-de-operaciones.md) | 0.1 · [PDF](pdf/02-estrategia-de-operaciones.pdf) |
| 3 | [Proceso y capacidad](unidades/03-proceso-y-capacidad.md) | 0.1 · [PDF](pdf/03-proceso-y-capacidad.pdf) |
| 4 | [Pronósticos](unidades/04-pronosticos.md) | 0.1 · [PDF](pdf/04-pronosticos.pdf) |
| 5 | [Inventarios](unidades/05-inventarios.md) | 0.1 · [PDF](pdf/05-inventarios.pdf) |
| 6 | [Planeación agregada](unidades/06-planeacion-agregada.md) | 0.1 · [PDF](pdf/06-planeacion-agregada.pdf) |
| 7 | [Programa maestro](unidades/07-programa-maestro.md) | 0.1 · [PDF](pdf/07-programa-maestro.pdf) |
| 8 | [MRP](unidades/08-mrp.md) | 0.1 · [PDF](pdf/08-mrp.pdf) |
| 9 | [Capacidad aproximada](unidades/09-capacidad-aproximada.md) | 0.1 · [PDF](pdf/09-capacidad-aproximada.pdf) |
| 10 | [Programación de operaciones](unidades/10-programacion-de-operaciones.md) | 0.1 · [PDF](pdf/10-programacion-de-operaciones.pdf) |
| 11 | [Física de la fábrica](unidades/11-fisica-de-la-fabrica.md) | 0.1 · [PDF](pdf/11-fisica-de-la-fabrica.pdf) |
| 12 | [Calidad](unidades/12-calidad.md) | 0.1 · [PDF](pdf/12-calidad.pdf) |

Cada unidad trae la teoría justa para entender el método, un ejemplo resuelto, diez ejercicios
graduados con pauta, errores típicos, los libros donde seguir y una pieza del caso integrador.

## El caso integrador · Estampa Sur

Estampa Sur es un taller de serigrafía (ficticio) de la Región del Biobío. Recorre el ramo como una
cadena de cálculo: lo que sale de una unidad entra a la siguiente.

| Unidad | Lo que calcula | Pasa a la siguiente |
|---|---|---|
| 4 Pronósticos | demanda mensual de poleras, polerones, bolsas y gorros | demanda por mes |
| 5 Inventarios | cuánto y cuándo comprar poleras lisas (EOQ y punto de reorden) | lote de compra para el MRP |
| 6 Planeación agregada | producción y personal por mes | plan por familia |
| 7 Programa maestro | lotes por producto y semana | MPS |
| 8 MRP | órdenes de prendas lisas y tintas | órdenes liberadas |
| 9 Capacidad aproximada | horas de estampado y planchado por semana | carga por centro |
| 10 Programación | orden de las órdenes de la semana 6 | tiempo en taller y WIP |
| 11 Física de la fábrica | WIP, throughput y tiempo en taller de la semana 6 | — |
| 12 Calidad | carta de control del registro del estampado y Cp, Cpk | — |

Cada pieza trae también sus datos de partida, para que un error en una unidad no arrastre a las
siguientes.

## Bibliografía

Obligatoria (la que fija el programa del ramo):

- Chase, Jacobs y Aquilano, *Administración de operaciones: producción y cadena de suministros*,
  McGraw-Hill, 12.ª ed., 2009.
- Schroeder, *Administración de operaciones: conceptos y casos contemporáneos*, McGraw-Hill,
  2.ª ed., 2004.
- Heizer y Render, *Principios de administración de operaciones*, Pearson, 5.ª ed., 2004.

Complementaria: Chopra y Meindl, *Administración de la cadena de suministro*; Goldratt y Cox,
*La meta*; Hopp y Spearman, *Factory Physics*.

Abierta y gratis: Abbas y Goosheh, *Operations Management*, Fanshawe College, 2025 (en inglés):
https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/2473

## Cómo se usa

- **Estudiar:** lee la unidad en PDF (`pdf/`) o en Markdown (`unidades/`).
- **Practicar con IA:** pega `tutor/contexto.md` al inicio de la conversación.
- **Comprobar una cifra:** cada unidad tiene su script en `verificacion/`; con `--revisar` busca cada
  resultado en el texto.
