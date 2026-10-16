---
ramo: Contabilidad y Costos
unidad: 10
titulo: Costeo por absorción y costeo variable
version: 0.1 (16-10-2026)
requiere: [07-inventarios, 08-razones-financieras, 09-clasificacion-de-costos]
alimenta: [11-asignacion-de-costos-indirectos, 12-costo-volumen-utilidad]
verificacion: verificacion/u10_absorcion_variable.py
---

# Unidad 10 · Costeo por absorción y costeo variable

**Qué vas a poder hacer.** Calcular el costo unitario de un producto con los dos métodos; armar el
estado de resultados por absorción y por costeo variable; explicar y conciliar la diferencia entre los
dos resultados con el costo fijo que queda en el inventario; anticipar qué pasa cuando la producción es
mayor, igual o menor que las ventas, y elegir el método según para qué se usa: la norma o la decisión.

**Lo que necesitas antes.** La clasificación de costos de la unidad 9 (variable y fijo, costo del
producto y del período, CIF), el inventario valorizado con FIFO de la unidad 7 y el estado de resultados
de la unidad 8.

**Tiempo.** Unas 5 horas: 2 de lectura con el ejemplo y 3 de práctica.

**Planilla.** `planillas/u10_absorcion_variable.xlsx` trae los dos estados de resultados del caso y los
tres escenarios del ejemplo, todo con fórmulas.

---

## 1. La pregunta de fondo

La unidad 9 dejó claro que los costos de fabricación son costos del producto: se guardan en el
inventario hasta que se vende. Para los costos **variables** de fabricación nadie lo discute. La duda es
qué hacer con los **costos fijos de fabricación** (el arriendo de la planta, la depreciación de la
máquina, el supervisor):

- **Costeo por absorción** (también llamado tradicional o completo): son costo del producto. Cada unidad
  producida «absorbe» una parte del costo fijo del mes, y esa parte viaja con la unidad al inventario.
- **Costeo variable** (también llamado de contribución): son costo del período. La empresa los paga por
  tener la capacidad disponible, no por cada unidad que hace; van completos al resultado del mes.

Los dos métodos coinciden en todo lo demás. Los gastos de administración y ventas, fijos o variables,
son siempre del período: **ninguno de los dos métodos los guarda en inventario**.

---

## 2. Costeo por absorción

$$\text{costo unitario por absorción} = cv_{\text{fab}} + \frac{\text{CIF fijo del mes}}{\text{unidades producidas}}$$

donde $cv_{\text{fab}}$ es MPD + MOD variable + CIF variable por unidad.

| Estado de resultados por absorción |
|---|
| Ventas |
| − Costo de ventas (unidades vendidas × costo unitario por absorción) |
| **= Margen bruto** |
| − Gastos de administración y ventas (variables y fijos) |
| **= Resultado operacional** |
| − Gastos financieros |
| **= Resultado antes de impuesto** |

Es el formato del estado de resultados de la unidad 8: separa por **función** (fabricar, administrar,
vender, financiar).

**Lo que dice la norma.** La norma de inventarios (NIC 2, que en Chile se aplica con las NIIF) pide
incluir en el costo del inventario los costos indirectos fijos de producción, repartidos según la
capacidad **normal** de la planta. Si un mes se produce mucho menos que lo normal, la parte del costo
fijo que no se reparte va directo a resultados. En este ramo, como en el curso, el costo fijo del mes
se reparte entre las unidades producidas en el mes.

---

## 3. Costeo variable

$$\text{costo unitario variable} = cv_{\text{fab}}$$

| Estado de resultados por costeo variable |
|---|
| Ventas |
| − Costo variable de lo vendido (unidades vendidas × $cv_{\text{fab}}$) |
| − Gastos variables de administración y ventas |
| **= Margen de contribución** |
| − CIF fijo del mes (completo) |
| − Gastos fijos de administración y ventas |
| **= Resultado operacional** |
| − Gastos financieros |
| **= Resultado antes de impuesto** |

Separa por **comportamiento** (variable o fijo). El margen de contribución es lo que deja cada unidad
vendida para cubrir los fijos; es la base de la unidad 12 (costo-volumen-utilidad).

**Costeo directo, un nombre con dos usos.** Muchos textos llaman «costeo directo» al costeo variable.
Otros reservan ese nombre para el que guarda en inventario solo los costos **directos** (MPD y MOD).
Dan lo mismo cuando lo directo es lo variable. Si la MOD es un sueldo fijo (como en Estampa Sur), no:
pregunta siempre qué incluye cada uno.

---

## 4. Por qué difieren los resultados

Los dos métodos registran los mismos costos totales en el mes; lo que cambia es **cuándo** llega a
resultados el costo fijo de fabricación. Por absorción, el fijo de las unidades que quedan en bodega
espera en el inventario; por costeo variable, entra entero este mes. La conciliación exacta es:

$$RO_{\text{abs}} - RO_{\text{var}} = \text{CIF fijo en el inventario final} - \text{CIF fijo en el inventario inicial}$$

Si la tasa fija por unidad es la misma en los dos inventarios, queda la forma del curso:

$$RO_{\text{abs}} - RO_{\text{var}} = (\text{inventario final} - \text{inventario inicial}) \times \text{CIF fijo por unidad}$$

| Situación del mes | El inventario | Resultado por absorción |
|---|---|---|
| Producción **mayor** que ventas | sube | **mayor** que el variable: parte del fijo se guarda en bodega |
| Producción **igual** a ventas | no cambia | **igual** al variable |
| Producción **menor** que ventas | baja | **menor** que el variable: sale de bodega el fijo de meses anteriores |

**En el tiempo se compensan.** Si el inventario vuelve al nivel de partida, la suma de los resultados
de esos meses es la misma con los dos métodos (ejercicios 10.6 y el ejemplo): el costo fijo no
desaparece, solo cambia de mes.

**La consecuencia incómoda.** Por absorción se puede mostrar más utilidad **produciendo** más, sin
vender una unidad más: el fijo se reparte en más unidades y una parte se va a bodega. Por costeo
variable eso es imposible: el resultado solo sube si suben las ventas o bajan los costos.

---

## 5. Para qué sirve cada uno

| | Costeo por absorción | Costeo variable |
|---|---|---|
| Para quién | usuarios externos: bancos, accionistas, el SII | la gerencia |
| Lo exige | la norma contable (NIC 2) | nadie: es una herramienta interna |
| Valoriza el inventario | con todos los costos de fabricación | solo con los variables |
| El resultado sigue a | la producción y las ventas | solo las ventas |
| Sirve para | estados financieros, precio de largo plazo que cubra todo | pedido especial, mezcla, punto de equilibrio, evaluar a quien vende |
| Riesgo | inflar la utilidad acumulando inventario | olvidar que los fijos también hay que pagarlos |

**Cuándo no importa.** En una empresa sin inventarios (un servicio que se presta y se cobra en el mes)
o en un mes en que la producción iguala a las ventas, los dos resultados son iguales. La diferencia es
de cuándo, no de cuánto.

**La decisión.** Para un pedido especial o para elegir qué producto empujar se usa el costo variable
(unidad 9): el costo unitario por absorción trae fijos que no cambian con la decisión y, además,
cambia con el volumen producido (ejercicio 10.9).

---

## 6. Ejemplo resuelto · la fábrica de velas aromáticas

Una fábrica de velas vende a $6.500 cada vela. Por vela gasta \$1.450 de cera, mecha y esencia (MPD),
\$620 de mano de obra a trato y \$280 de CIF variable. El CIF fijo es $2.640.000 al mes. Los gastos de
ventas variables (despacho y cobro con tarjeta) son \$190 por vela vendida y los gastos fijos de
administración y ventas $1.150.000 al mes. En el mes 1 no hay inventario inicial: produce 4.400 velas
y vende 4.000. En el mes 2 produce 3.600 y vende 4.000. Inventario en FIFO.

**Paso 1 · Costo unitario del mes 1.** Variable: 1.450 + 620 + 280 = **$2.350**. Fijo por vela:
2.640.000 / 4.400 = **\$600**. Por absorción: **$2.950**.

**Paso 2 · Los dos estados del mes 1.**

| Costeo variable | Pesos | | Costeo por absorción | Pesos |
|---|---|---|---|---|
| Ventas (4.000 × 6.500) | 26.000.000 | | Ventas | 26.000.000 |
| − Costo variable de lo vendido (4.000 × 2.350) | − 9.400.000 | | − Costo de ventas (4.000 × 2.950) | − 11.800.000 |
| − Gastos variables de venta (4.000 × 190) | − 760.000 | | **Margen bruto** | **14.200.000** |
| **Margen de contribución** | **15.840.000** | | − Gastos de adm. y ventas (760.000 + 1.150.000) | − 1.910.000 |
| − Fijos: 2.640.000 + 1.150.000 | − 3.790.000 | | | |
| **Resultado operacional** | **12.050.000** | | **Resultado operacional** | **12.290.000** |

**Paso 3 · Conciliar.** La diferencia es 12.290.000 − 12.050.000 = **$240.000** = 400 velas en bodega
× \$600 de fijo cada una. El inventario final vale $940.000 a costo variable y $1.180.000 por absorción:
la misma diferencia.

**Paso 4 · El mes 2, con producción menor que ventas.** El fijo por vela sube a 2.640.000 / 3.600 =
\$733,33, y el costo por absorción del mes a $3.083,33. FIFO vende primero las 400 velas del mes 1 (a
$2.950) y luego 3.600 nuevas:

$$\text{costo de ventas} = 400 \times 2{.}950 + 3{.}600 \times 3{.}083{,}33 = 1{.}180{.}000 + 11{.}100{.}000 = 12{.}280{.}000$$

Por absorción: margen bruto 26.000.000 − 12.280.000 = $13.720.000 y resultado operacional
**$11.810.000**. Por costeo variable el estado es idéntico al del mes 1 (vendió lo mismo): **$12.050.000**.
Ahora absorción queda $240.000 **abajo**: salió de bodega el fijo que el mes 1 había guardado.

**Paso 5 · Tres escenarios con las mismas ventas.**

| | Mes 1 (produce 4.400) | Produce 4.000 | Mes 2 (produce 3.600) |
|---|---|---|---|
| Fijo por vela | 600 | 660 | 733 |
| Costo de ventas por absorción | 11.800.000 | 12.040.000 | 12.280.000 |
| Margen bruto | 14.200.000 | 13.960.000 | 13.720.000 |
| Resultado por absorción | 12.290.000 | 12.050.000 | 11.810.000 |
| Resultado variable | 12.050.000 | 12.050.000 | 12.050.000 |
| Diferencia | +240.000 | 0 | −240.000 |

En el escenario intermedio el costo por absorción es $3.010 y los dos resultados coinciden. Y en los
meses 1 y 2 juntos, absorción suma 12.290.000 + 11.810.000 = **$24.100.000**, lo mismo que el variable
(2 × 12.050.000): el inventario volvió a cero y el fijo terminó entero en resultados.

**Cómo se lee.** La fábrica vendió exactamente lo mismo los dos meses y su desempeño comercial fue el
mismo: eso es lo que muestra el costeo variable. El costeo por absorción muestra un mes «bueno» y uno
«malo» solo porque cambió la producción. Para el banco, el estado que vale es el de absorción; para
evaluar a quien vende o decidir un pedido, el variable. Si el gerente cobra un bono sobre el resultado
por absorción, conviene vigilar el inventario.

---

## 7. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Repartir el CIF fijo por las unidades **vendidas** | Se reparte por las unidades **producidas**; lo vendido sale de ahí |
| Poner los gastos de administración y ventas en el costo del producto | Son del período en los dos métodos, también los variables (comisiones, fletes) |
| En costeo variable, olvidar restar el CIF fijo completo del mes | El fijo no desaparece: va entero bajo el margen de contribución |
| Usar el costo unitario por absorción (con fijos) para decidir un pedido especial | Usa el costo variable más lo que agregue el pedido; el fijo no cambia y su valor por unidad depende del volumen |
| Conciliar con «ventas × tasa fija» | La diferencia viene del cambio de **inventario** × tasa fija (o fijo en inventario final menos inicial) |
| Creer que una diferencia positiva es «más ganancia» | Es costo fijo postergado: volverá a resultados cuando se venda ese inventario |
| Valorizar el inventario inicial con la tasa fija del mes actual | Con FIFO, el inventario inicial sale con el costo del mes en que se produjo |
| Mezclar costo y gasto: dejar en el inventario la comisión de venta | La comisión se causa al vender, no al fabricar |
| Llamar «costeo directo» a cualquier cosa | Pregunta si incluye la MOD fija; si es sueldo fijo, directo y variable no coinciden |

---

## 8. Práctica

Diez ejercicios: 10.1 a 10.4 básicos, 10.5 a 10.8 intermedios, 10.9 y 10.10 de desafío. Montos netos de
IVA, inventario en FIFO, sin impuesto a la renta. Las pautas están en la sección 9.

**10.1 · Los jabones (básico).** Una fábrica de jabones artesanales produce 6.000 jabones al mes. Por
jabón: MPD \$640, MOD a trato \$310, CIF variable \$150. El CIF fijo es $2.100.000 al mes. Calcula el
costo unitario con cada método y el valor de los 800 jabones que quedan en bodega. ¿Cuánto cambia el
resultado entre métodos?

**10.2 · Las cajas, mes 1 (básico).** Una fábrica de cajas de cartón para delivery vende a \$515 la
caja. Por caja: MPD \$162, MOD a trato \$47, CIF variable \$23. CIF fijo $1.396.800 al mes. Gastos
variables de venta \$19 por caja vendida; gastos fijos de administración y ventas $683.000. En el mes
1 produce y vende 11.640 cajas, sin inventario inicial. Arma los dos estados de resultados.

**10.3 · Las cajas, mes 2 (básico).** El mes siguiente vende otra vez 11.640 cajas, pero produce 14.550.
Arma los dos estados y concilia la diferencia.

**10.4 · Los cuchillos (básico).** Un taller produce 470 cuchillos y vende 385 a $24.900. Por cuchillo:
MPD $6.140, MOD a trato $3.460, CIF variable $1.170. CIF fijo $1.692.000; gasto variable de venta \$830
por cuchillo vendido; gastos fijos de administración y ventas \$915.000. Sin inventario inicial.
¿Cuánto de lo que se gastó en el mes va a resultados y cuánto queda en bodega con cada método? Calcula
los dos resultados operacionales.

**10.5 · Las cajas, mes 3 (intermedio).** En el mes 3 produce 9.700 cajas y vende 12.610 (las 2.910 que
quedaron del mes 2 y todas las del mes 3). Arma los dos estados y concilia.

**10.6 · Los tres meses de las cajas (intermedio).** Con 10.2, 10.3 y 10.5, suma los resultados de los
tres meses con cada método. ¿Por qué coinciden? ¿Qué método describe mejor lo que pasó con el negocio
mes a mes?

**10.7 · El bono del gerente (intermedio).** Una fábrica de sillas vende 2.000 sillas al mes a $38.000.
Su costo variable de fabricación es $17.000 por silla, el CIF fijo $16.000.000 al mes y los gastos fijos
de administración y ventas $6.000.000 (no hay gastos variables de venta). El gerente cobra un bono del
5 % del resultado operacional por absorción. Puede producir 2.000 o 2.800 sillas (capacidad máxima),
y las ventas no cambian. Calcula el resultado por absorción, el variable y el bono en cada caso. ¿Qué
pasa con la caja y la bodega si produce 2.800?

**10.8 · El bloqueador solar (intermedio).** Produce 9.240 envases y vende 7.630 a $7.940. Por envase:
MPD $1.870, MOD a trato \$715, CIF variable \$395. CIF fijo $8.316.000. Gastos variables de venta
(comisión y flete) \$585 por envase vendido; gastos fijos de administración y ventas $4.270.000. Gastos
financieros $517.000. Sin inventario inicial. Arma los dos estados hasta el resultado antes de
impuesto y concilia.

**10.9 · El pedido de la cadena de farmacias (desafío).** Con los datos de 10.8, una cadena ofrece
comprar 1.050 envases adicionales a $3.690, sin comisión: solo \$145 de flete por envase. Hay capacidad.
(a) Con el costo por absorción, ¿cuánto parece perder? (b) ¿Cuánto aporta de verdad? (c) Si se acepta y
se fabrican también esos 1.050, ¿cuánto sube el resultado con cada método? ¿Por qué no suben lo mismo?

**10.10 · El problema al revés (desafío).** Una empresa sin inventario inicial produjo 8.000 unidades y
vendió 6.200. Su resultado operacional fue $4.380.000 por absorción y $3.660.000 por costeo variable.
(a) ¿Cuál es el CIF fijo por unidad y el CIF fijo del mes? (b) ¿Con qué producción habrían coincidido?
(c) El mes siguiente produce 6.000 y vende 7.800. ¿Cuál será la diferencia entre los dos resultados?
(d) ¿Podía el primer mes dar absorción menor que variable?

---

## 9. Pautas

**10.1.** Variable: 640 + 310 + 150 = **$1.100**. Fijo por jabón: 2.100.000 / 6.000 = \$350. Absorción:
**$1.450**. Bodega: 800 × 1.100 = **$880.000** a costo variable y 800 × 1.450 = **$1.160.000** por
absorción. El resultado por absorción es $280.000 mayor: el fijo de los 800 jabones que no se vendieron.

**10.2.** Costo variable \$232; fijo por caja 1.396.800 / 11.640 = \$120; absorción \$352.

| Variable | Pesos | Absorción | Pesos |
|---|---|---|---|
| Ventas | 5.994.600 | Ventas | 5.994.600 |
| − Costo variable de lo vendido | − 2.700.480 | − Costo de ventas | − 4.097.280 |
| − Gastos variables de venta | − 221.160 | Margen bruto | 1.897.320 |
| Margen de contribución | 3.072.960 | − Gastos de adm. y ventas | − 904.160 |
| − Fijos (1.396.800 + 683.000) | − 2.079.800 | | |
| **Resultado operacional** | **993.160** | **Resultado operacional** | **993.160** |

Producción igual a ventas: no queda fijo en bodega y los resultados son iguales.

**10.3.** Fijo por caja: 1.396.800 / 14.550 = \$96; absorción \$328. Costeo variable: el mismo estado de
10.2, **$993.160**, porque vendió lo mismo. Absorción: costo de ventas 11.640 × 328 = $3.817.920, margen
bruto $2.176.680, resultado **$1.272.520**. Diferencia: **$279.360** = 2.910 cajas en bodega × \$96.
Lectura: vendió lo mismo y por absorción «ganó» un 28 % más.

**10.4.** Costo variable $10.770; fijo por cuchillo $3.600; absorción $14.370. Se gastaron en total
**$7.988.450** (470 × 10.770 + 1.692.000 + 319.550 + 915.000).

| | Costeo variable | Absorción |
|---|---|---|
| Costo de lo vendido | 4.146.450 | 5.532.450 |
| Gastos de venta variables | 319.550 | 319.550 |
| CIF fijo como gasto | 1.692.000 | 0 |
| Gastos fijos de adm. y ventas | 915.000 | 915.000 |
| **A resultados** | **7.073.000** | **6.767.000** |
| **Queda en bodega (85 cuchillos)** | **915.450** | **1.221.450** |

Con ventas de $9.586.500, el resultado operacional es $2.513.500 por costeo variable y $2.819.500 por
absorción. Diferencia: $306.000 = 85 × 3.600. Lectura: el total gastado es el mismo; cambia cuánto se
queda esperando en la bodega.

**10.5.** Fijo por caja del mes 3: 1.396.800 / 9.700 = \$144; absorción del mes \$376. Ventas: 12.610 ×
515 = $6.494.150. Costo de ventas por absorción (FIFO): 2.910 × 328 + 9.700 × 376 = 954.480 + 3.647.200 =
$4.601.680; margen bruto $1.892.470; gastos de adm. y ventas $922.590; resultado **$969.880**. Costeo
variable: costo variable de lo vendido $2.925.520, gastos variables $239.590, margen de contribución
$3.329.040, fijos $2.079.800, resultado **$1.249.240**. Absorción queda **$279.360** abajo: salió el fijo
de las 2.910 cajas guardadas en el mes 2.

**10.6.**

| Mes | Absorción | Variable |
|---|---|---|
| 1 (produce = vende) | 993.160 | 993.160 |
| 2 (produce más) | 1.272.520 | 993.160 |
| 3 (produce menos) | 969.880 | 1.249.240 |
| **Total** | **3.235.560** | **3.235.560** |

Coinciden porque la bodega empieza y termina vacía: los $279.360 que el mes 2 postergó volvieron en el
mes 3. El variable describe mejor el negocio: los meses 1 y 2 vendieron lo mismo y muestran lo mismo; el
mes 3 vendió más y muestra más.

**10.7.**

| Produce | Fijo por silla | Costo por absorción | Costo de ventas | Margen bruto | Resultado por absorción | Variable | Bono |
|---|---|---|---|---|---|---|---|
| 2.000 | 8.000 | 25.000 | 50.000.000 | 26.000.000 | 20.000.000 | 20.000.000 | 1.000.000 |
| 2.800 | 5.714 | 22.714 | 45.428.571 | 30.571.429 | 24.571.429 | 20.000.000 | 1.228.571 |

Produciendo 800 sillas que nadie compró, el resultado por absorción sube $4.571.429 y el bono $228.571.
La empresa no ganó nada más: el variable sigue en $20.000.000. Las 800 sillas quedan en bodega por
$18.171.429 y consumieron $13.600.000 de caja en costos variables. Lectura: un bono sobre el resultado por
absorción premia llenar la bodega; se corrige midiendo con costeo variable o castigando el inventario.

**10.8.** Costo variable $2.980; fijo por envase 8.316.000 / 9.240 = \$900; absorción $3.880.

| Costeo variable | Pesos | Absorción | Pesos |
|---|---|---|---|
| Ventas | 60.582.200 | Ventas | 60.582.200 |
| − Costo variable de lo vendido | − 22.737.400 | − Costo de ventas | − 29.604.400 |
| − Gastos variables de venta | − 4.463.550 | Margen bruto | 30.977.800 |
| Margen de contribución | 33.381.250 | − Gastos de adm. y ventas | − 8.733.550 |
| − Fijos (8.316.000 + 4.270.000) | − 12.586.000 | | |
| Resultado operacional | 20.795.250 | Resultado operacional | 22.244.250 |
| − Gastos financieros | − 517.000 | − Gastos financieros | − 517.000 |
| **Resultado antes de impuesto** | **20.278.250** | **Resultado antes de impuesto** | **21.727.250** |

Diferencia: $1.449.000 = 1.610 envases en bodega × \$900. El gasto financiero es igual en los dos: no
es costo de fabricación.

**10.9.** (a) Con el costo por absorción de $3.880, el pedido a $3.690 parece perder $199.500, y eso sin
contar el flete. (b) Costo relevante: 2.980 + 145 = **$3.125**; aporta (3.690 − 3.125) × 1.050 = 565 ×
1.050 = **$593.250**. Acepta. (c) Costeo variable: sube exactamente $593.250, a $21.388.500. Absorción:
con 10.290 envases producidos el fijo por envase baja a \$808,16 y el costo a $3.788,16. Ventas
$64.456.700, costo de ventas $32.881.257 y resultado $22.689.643: sube solo **$445.393**. La diferencia,
$147.857, es fijo que ya no queda en la bodega: los 1.610 envases guardados ahora cargan \$808,16 en vez
de \$900. La nueva diferencia entre métodos es $1.301.143. Lectura: el costo unitario por absorción
cambia con el volumen, así que no sirve para medir lo que aporta una decisión.

**10.10.** (a) Diferencia: 4.380.000 − 3.660.000 = **$720.000**, y el inventario subió 1.800 unidades.
CIF fijo por unidad: 720.000 / 1.800 = **\$400**; CIF fijo del mes: 400 × 8.000 = **$3.200.000**. (b)
Produciendo 6.200, lo mismo que vendió. (c) Con FIFO salen primero las 1.800 unidades guardadas, que
cargan $720.000 de fijo, y la bodega queda vacía: absorción quedará **$720.000 bajo** el variable. (d) No:
sin inventario inicial la producción no puede ser menor que las ventas, y el fijo en bodega solo puede
subir o quedar en cero.

---

## 10. Caso integrador · Estampa Sur, el costo fijo que queda en bodega

> La unidad 9 dejó el costo variable estándar de cada prenda, los CIF fijos de marzo ($3.849.833,33) y
> los gastos de administración ($436.000). El estado de resultados de la unidad 8 se hizo por absorción.
> En marzo Estampa Sur produjo 5.590 prendas y vendió 5.300.

**Pregunta.** ¿Cuál es el resultado de marzo con cada método? ¿Por qué el de absorción es mayor?
¿Cuál se le muestra al banco y cuál usa Valentina para decidir?

**1 · El CIF fijo por prenda.** El caso reparte los CIF fijos según los segundos de estampado de cada
prenda (la unidad 11 justifica este reparto). En marzo se estamparon 275.020 segundos, así que cada
segundo carga 3.849.833,33 / 275.020 = $13,9984.

| Producto | Producidas | Vendidas | En bodega | Costo variable | CIF fijo por prenda | Costo por absorción |
|---|---|---|---|---|---|---|
| Poleras básicas | 2.236 | 2.120 | 116 | 2.610 | 419,95 | 3.029,95 |
| Polerones | 839 | 795 | 44 | 5.950 | 1.259,85 | 7.209,85 |
| Poleras estampado doble | 838 | 795 | 43 | 4.020 | 1.539,82 | 5.559,82 |
| Bolsas | 1.006 | 954 | 52 | 1.530 | 279,97 | 1.809,97 |
| Gorros | 671 | 636 | 35 | 2.020 | 419,95 | 2.439,95 |
| **Total** | **5.590** | **5.300** | **290** | | | |

**2 · Los dos estados de resultados de marzo.**

| Costeo variable | Pesos | Costeo por absorción | Pesos |
|---|---|---|---|
| Ventas | 25.726.200 | Ventas | 25.726.200 |
| − Costo variable de lo vendido | − 16.203.690 | − Costo de ventas | − 19.853.906 |
| **Margen de contribución** | **9.522.510** | **Margen bruto** | **5.872.294** |
| − CIF fijos | − 3.849.833 | | |
| − Gastos de administración | − 436.000 | − Gastos de administración | − 436.000 |
| **Resultado operacional** | **5.236.677** | **Resultado operacional** | **5.436.294** |
| − Interés del préstamo | − 73.600 | − Interés del préstamo | − 73.600 |
| **Resultado antes de impuesto** | **5.163.077** | **Resultado antes de impuesto** | **5.362.694** |

El estado por absorción es el mismo de la unidad 8.

**3 · La conciliación.** 5.436.294 − 5.236.677 = **$199.617**. Es el CIF fijo de las 290 prendas en
bodega:

| Producto | En bodega | Fijo guardado | Bodega a costo variable |
|---|---|---|---|
| Poleras básicas | 116 | 48.714 | 302.760 |
| Polerones | 44 | 55.434 | 261.800 |
| Poleras estampado doble | 43 | 66.212 | 172.860 |
| Bolsas | 52 | 14.558 | 79.560 |
| Gorros | 35 | 14.698 | 70.700 |
| **Total** | **290** | **199.617** | **887.680** |

(El total exacto es $199.616,84; las filas redondeadas suman un peso menos.) La bodega vale $887.680 a
costo variable y $1.087.297 por absorción. De los $3.849.833 de CIF fijos, $3.650.216 salieron en el
costo de ventas y $199.617 esperan en la bodega. Segundo camino: el costo de lo producido (17.091.370 +
3.849.833 = 20.941.203, unidad 9) es igual al costo de ventas por absorción más la bodega por absorción.

**Lectura.** Estampa Sur produjo 290 prendas más de las que vendió, así que el costeo por absorción
posterga $199.617 de costo fijo a abril: por eso muestra $5.436.294 en vez de $5.236.677. Ninguno de
los dos «está mal». Al banco y al SII se les muestra el de absorción, que es el que pide la norma. Para
decidir, Valentina usa el variable: le dice que cada prenda vendida deja su margen de contribución y
que marzo cubrió los $4.285.833 de fijos operacionales (CIF más administración) con holgura. Si en abril
produce menos de lo que vende, la bodega se vacía y el resultado por absorción quedará bajo el
variable en ese mismo monto.

**Lo que pasa a la unidad 11.** El reparto de los CIF fijos por segundo de estampado ($13,9984), que
aquí se usó sin justificar, y el costo por absorción de cada prenda. La unidad 12 usa el margen de
contribución y los fijos operacionales del estado variable para el punto de equilibrio.

---

## 11. Para seguir

**En los libros del ramo.**

- Obligatorios del programa: Gálvez y Clarke, *Contabilidad financiera para la dirección de empresas*,
  Ediciones UC, e Irarrázabal, *Contabilidad: fundamentos y usos*, Ediciones UC, 2014.
- Complementarios: Garrison, Noreen y Brewer, *Contabilidad administrativa*, McGraw-Hill, 2007 (su
  capítulo de costeo variable, con la conciliación de utilidades y su uso en la gestión), y Horngren,
  *Contabilidad de costos*, Pearson, 2012 (su capítulo sobre costeo variable y por absorción de los
  inventarios y el efecto de la capacidad con que se fija la tasa).

**Abierto y gratis.**

- OpenStax, *Principles of Accounting, Volume 2: Managerial Accounting* (en inglés, licencia
  CC BY-NC-SA), capítulo 6, sección 6.5 «Compare and Contrast Variable and Absorption Costing»:
  https://openstax.org/books/principles-managerial-accounting/pages/6-why-it-matters

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame tres meses de una fábrica con producción y
ventas distintas; déjame armar los dos estados de cada mes y conciliar, y corrígeme línea por línea».
