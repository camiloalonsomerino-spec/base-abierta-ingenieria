# Contabilidad y Costos

Cómo se registra lo que pasa en una empresa (cada compra, venta, pago y desgaste), cómo se arman los
estados financieros que lo resumen y cómo se calcula cuánto cuesta de verdad cada producto para decidir
precios, mezcla y cuánto hay que vender para no perder.

**Nivel:** segundo o tercer año de Ingeniería Civil Industrial. **Antes:** Gestión de Empresas.
**Herramienta:** planilla de cálculo; las tablas largas (libro diario, mayor, tarjeta de existencias,
punto de equilibrio) también vienen como planilla en `planillas/`.

## Unidades

| N.º | Unidad | Estado (16-10-2026) |
|---|---|---|
| 1 | [La contabilidad y los estados financieros](unidades/01-contabilidad-y-estados-financieros.md) | 0.1 · [PDF](pdf/01-contabilidad-y-estados-financieros.pdf) |
| 2 | [Partida doble: asientos, libro diario, mayor y balance de comprobación](unidades/02-partida-doble.md) | 0.1 · [PDF](pdf/02-partida-doble.pdf) |
| 3 | [IVA](unidades/03-iva.md) | 0.1 · [PDF](pdf/03-iva.pdf) |
| 4 | [Activo fijo y depreciación](unidades/04-depreciacion.md) | 0.1 · [PDF](pdf/04-depreciacion.pdf) |
| 5 | [Ajustes de cierre: anticipados, devengados y provisiones](unidades/05-ajustes-de-cierre.md) | 0.1 · [PDF](pdf/05-ajustes-de-cierre.pdf) |
| 6 | [Préstamos e intereses en la contabilidad](unidades/06-prestamos-e-intereses.md) | 0.1 · [PDF](pdf/06-prestamos-e-intereses.pdf) |
| 7 | [Inventarios: FIFO y precio promedio ponderado](unidades/07-inventarios.md) | 0.1 · [PDF](pdf/07-inventarios.pdf) |
| 8 | [Estados financieros y razones financieras](unidades/08-razones-financieras.md) | 0.1 · [PDF](pdf/08-razones-financieras.pdf) |
| 9 | [Costos: conceptos y clasificación](unidades/09-clasificacion-de-costos.md) | 0.1 · [PDF](pdf/09-clasificacion-de-costos.pdf) |
| 10 | [Costeo por absorción y costeo variable](unidades/10-absorcion-y-variable.md) | 0.1 · [PDF](pdf/10-absorcion-y-variable.pdf) |
| 11 | [Asignación de costos indirectos](unidades/11-asignacion-de-costos-indirectos.md) | 0.1 · [PDF](pdf/11-asignacion-de-costos-indirectos.pdf) |
| 12 | [Costo-volumen-utilidad y punto de equilibrio](unidades/12-costo-volumen-utilidad.md) | 0.1 · [PDF](pdf/12-costo-volumen-utilidad.pdf) |

## El caso integrador · el mes de marzo de Estampa Sur

El mismo taller ficticio de los otros ramos, en un solo mes coherente: produce 5.590 prendas y vende
5.300 (plan y mezcla de Gestión de Operaciones), con los márgenes de contribución de Optimización y la
segunda máquina de Finanzas.

| Unidad | Lo que calcula |
|---|---|
| 1 | El balance al 1 de marzo y la ecuación contable |
| 2 | Los 12 asientos del mes, el mayor y el balance de comprobación |
| 3 | El IVA del mes: débito, crédito y el remanente que deja la máquina nueva |
| 4 | La depreciación de las dos máquinas |
| 5 | El arriendo y el seguro devengados al cierre |
| 6 | La cuota, el interés y la tabla del préstamo bancario |
| 7 | La tarjeta de las poleras lisas con FIFO y precio promedio, y su diferencia con el costo estándar |
| 8 | El estado de resultados de marzo y las razones financieras |
| 9 | Qué costo es fijo, variable, directo o indirecto en el taller |
| 10 | Por qué el resultado por absorción supera al variable en $199.617 (el costo fijo que queda en bodega) |
| 11 | El costo fijo por segundo de estampado y el costo completo de cada prenda |
| 12 | El punto de equilibrio con la mezcla de ventas: 2.385 prendas al mes |

La fuente única de las cifras es `verificacion/caso_estampa_sur_contable.py`. Todo es ficticio salvo la
tasa de IVA (19 %).

## Bibliografía

Obligatoria (la que fija el programa del ramo): Gálvez y Clarke, *Contabilidad financiera para la
dirección de empresas*, Ediciones UC; Irarrázabal, *Contabilidad: fundamentos y usos*, Ediciones UC, 2014.

Complementaria: Garrison, Noreen y Brewer, *Contabilidad administrativa*, McGraw-Hill, 2007; Horngren,
*Contabilidad de costos*, Pearson, 2012; Weygandt, Kimmel y Kieso, *Accounting Principles*, Wiley, 12.ª
ed., 2014. Abierta: Jonick, *Principles of Financial Accounting*, University of North Georgia, 2017.

## Cómo se usa

- **Estudiar:** lee la unidad en PDF (`pdf/`) o en Markdown (`unidades/`).
- **Practicar:** abre la planilla de la unidad en `planillas/`.
- **Practicar con IA:** pega `tutor/contexto.md` al inicio de la conversación.
- **Comprobar una cifra:** cada unidad tiene su script en `verificacion/`; con `--revisar` busca cada
  resultado en el texto.
