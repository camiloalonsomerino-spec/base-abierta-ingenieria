---
ramo: Contabilidad y Costos
unidad: 7
titulo: Inventarios · FIFO y precio promedio ponderado
version: 0.1 (16-10-2026)
requiere: [02-partida-doble, 03-iva]
alimenta: [08-razones-financieras, 10-absorcion-y-variable]
verificacion: verificacion/u07_inventarios.py
---

# Unidad 7 · Inventarios: FIFO y precio promedio ponderado

**Qué vas a poder hacer.** Elegir entre el sistema periódico y el permanente; llevar una tarjeta de
existencias con entradas, salidas y saldo en unidades y en pesos; valorizar cada salida con FIFO y con
precio promedio ponderado (con devoluciones y mermas); registrar los asientos de compra, venta, costo
y merma con su IVA; explicar por qué el método mueve la utilidad cuando cambian los precios, y medir
cuánto se aparta el costo real del costo estándar.

**Lo que necesitas antes.** Asientos con Debe y Haber (unidad 2) y el IVA de compras y ventas
(unidad 3). Basta con saber que una compra suma a Existencias y al IVA crédito fiscal, y que una venta
suma a Ventas y al IVA débito fiscal.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica (las tarjetas se aprenden
haciéndolas).

---

## 1. La idea

Lo que una empresa compra para vender (o para producir) es un **activo**: está en la bodega y vale lo
que costó. Cuando se vende o se consume, ese costo deja de ser activo y pasa al estado de resultados
como **costo de ventas**. Hasta ahí no hay problema.

El problema aparece cuando las mismas unidades se compraron a precios distintos. Si hay 40 cascos a
$18.500 y 60 a $19.700 y se venden 70, ¿cuánto costaron esos 70? Las unidades son idénticas; nadie
anota de qué caja salió cada una. La respuesta la da una **fórmula de costo**, una regla que dice qué
precio se le asigna a lo que sale. Con la misma bodega y las mismas ventas, dos fórmulas dan dos
costos de ventas distintos y dos saldos distintos. Lo que no cambia es la suma:

$$\text{costo de lo disponible} = \text{costo de ventas} + \text{mermas} + \text{saldo final}$$

La fórmula solo decide **cuánto de lo disponible va al resultado ahora y cuánto queda en la bodega**
para después. Es el primer chequeo de toda tarjeta.

---

## 2. Sistema periódico y sistema permanente

Hay dos formas de saber cuánto costó lo vendido.

**Periódico.** No se registra el costo en cada venta. Al cierre se cuenta la bodega y el costo de
ventas sale por diferencia:

$$\text{costo de ventas} = \text{inventario inicial} + \text{compras} - \text{inventario final}$$

Es barato de llevar, pero tiene dos debilidades: durante el mes no se sabe el margen, y todo lo que
falta en la bodega (robo, daño, error) queda **escondido dentro del costo de ventas**, porque la fórmula
no distingue lo vendido de lo perdido.

**Permanente (o perpetuo).** Cada entrada y cada salida se anota en una **tarjeta de existencias** al
momento, con su costo. La tarjeta dice en todo momento cuántas unidades debería haber y cuánto valen.
Al contar la bodega, la diferencia entre la tarjeta y el conteo es una **merma** que se ve y se
registra aparte. Con un sistema de ventas y bodega computarizado, el permanente es lo normal; el
periódico queda para negocios pequeños o productos de bajo valor.

| | Periódico | Permanente |
|---|---|---|
| Costo de cada venta | no se registra | se registra con cada venta |
| Costo de ventas del mes | al cierre, por diferencia | suma de las salidas de la tarjeta |
| Faltantes | escondidos en el costo de ventas | se ven como merma |
| Margen durante el mes | no se conoce | se conoce |

---

## 3. La tarjeta de existencias

Una tarjeta por producto. Cada fila es un movimiento, con tres bloques:

| Fecha | Movimiento | Entra | Sale | Saldo (u) | Saldo (pesos) |
|---|---|---|---|---|---|
| fecha del hecho | compra, venta, devolución o merma | unidades × costo unitario | unidades × costo unitario | unidades que quedan | pesos que quedan |

- **Entradas:** compras al costo neto (sin IVA, porque el IVA crédito se recupera) y devoluciones de
  venta.
- **Salidas:** ventas o consumos, devoluciones de compra y mermas.
- **Saldo:** se arrastra fila a fila: saldo anterior más entradas menos salidas, en unidades y en
  pesos.

Las dos devoluciones se tratan distinto, y es donde más se equivoca la gente:

- **Devolución de compra:** sale al **precio al que se compró** lo que se devuelve. Se le devuelve al
  proveedor lo que él facturó.
- **Devolución de venta:** entra al **costo con que salió**, no al precio de venta. Lo que vuelve a la
  bodega vale lo que costó; el precio de venta se reversa en Ventas.

---

## 4. FIFO · primero en entrar, primero en salir

FIFO (*first in, first out*) supone que lo primero que entró es lo primero que sale. Cada salida toma
unidades del **lote más antiguo** hasta agotarlo y sigue con el siguiente. La tarjeta lleva el detalle
de los **lotes que quedan en bodega**, cada uno con su precio.

Intuición: es como una góndola de leche bien repuesta, donde lo nuevo va atrás. El saldo final queda
valorizado con las **compras más recientes**, así que se parece al precio de reposición. El costo de
ventas, en cambio, arrastra precios viejos.

Una merma con FIFO también sale del lote más antiguo. Una devolución de venta vuelve con el precio de
las últimas unidades que tomó esa venta.

---

## 5. Precio promedio ponderado (PPP)

El **precio promedio ponderado** (en el curso, PMP: precio medio ponderado) mezcla todas las unidades en
un solo precio:

$$\bar p = \frac{\text{saldo en pesos}}{\text{saldo en unidades}}$$

- En el **sistema permanente** el promedio se recalcula **cada vez que entra algo** (por eso se llama
  promedio móvil) y cada salida se valoriza al promedio vigente. Una salida no cambia el promedio:
  saca unidades y pesos en la misma proporción.
- En el **sistema periódico** se calcula un solo promedio del período, con todo lo disponible:
  $\bar p = (\text{inventario inicial} + \text{compras}) / \text{unidades disponibles}$.

Los dos promedios dan distinto cuando hay compras entre ventas: el periódico le carga a una venta de
la primera semana parte de una compra que llegó después. El ejemplo resuelto los compara.

Intuición: el PPP suaviza. Una compra cara sube el promedio un poco, no del todo, porque se mezcla con
lo que ya había. Por eso su costo de ventas y su saldo quedan entre los dos extremos.

---

## 6. Qué método se puede usar

Existe un tercer método de libro, **LIFO** (*last in, first out*: lo último que entró sale primero). En
Chile no se usa:

- La **ley de la renta** (artículo 30) manda usar los costos más antiguos (FIFO) y permite optar por el
  costo promedio ponderado; el método elegido se mantiene **al menos cinco ejercicios comerciales
  consecutivos** y no se pueden aplicar los dos en un mismo ejercicio (así lo reitera el SII en su
  Oficio N.º 3190, de 17-12-2015).
- La **NIC 2** (la norma internacional de inventarios) admite la identificación específica para
  artículos no intercambiables y, para los intercambiables, FIFO o costo promedio ponderado. LIFO no
  está entre sus fórmulas.

Esta unidad trabaja con FIFO y PPP. Si un libro en inglés muestra LIFO, sirve para entender el efecto
de los precios, no como método aplicable aquí.

---

## 7. Los asientos

En el sistema permanente, cada venta genera **dos asientos**: el de la venta a precio de venta y el del
costo a precio de costo.

| Hecho | Debe | Haber |
|---|---|---|
| Compra | Existencias (neto) · IVA crédito fiscal | Proveedores o Banco (bruto) |
| Venta | Clientes o Banco (bruto) | Ventas (neto) · IVA débito fiscal |
| Costo de la venta | Costo de ventas | Existencias (al costo de la tarjeta) |
| Devolución de venta | Ventas · IVA débito fiscal | Clientes o Banco |
| Su costo vuelve a bodega | Existencias | Costo de ventas |
| Devolución de compra | Proveedores o Banco | Existencias · IVA crédito fiscal |
| Merma | Pérdida por merma | Existencias |
| Consumo en producción | Productos en proceso | Materias primas |

La merma va a una cuenta propia (un gasto o pérdida), no al costo de ventas: así se ve cuánto se
perdió. En una empresa que produce, como el taller del caso, lo que sale de la bodega de materias
primas no es costo de ventas todavía: pasa a **productos en proceso** y se convierte en costo de
ventas cuando se vende la prenda terminada (unidad 10).

---

## 8. El método y la utilidad cuando suben los precios

Con precios que **suben**, los lotes viejos son los baratos:

| | FIFO | PPP |
|---|---|---|
| Costo de ventas | más bajo (usa lo viejo y barato) | intermedio |
| Margen bruto y utilidad | más alta | intermedia |
| Saldo final | más alto, cerca del precio de reposición | intermedio |

Con precios que **bajan** todo se invierte: FIFO da el costo de ventas más alto (ejercicio 7.9).

Tres consecuencias:

- **La caja es la misma.** Se pagaron las mismas compras con cualquiera de los dos métodos. Lo que
  cambia es en qué período aparece el costo. (El único efecto en caja vendría del impuesto a la renta,
  que se calcula sobre la utilidad.)
- **La diferencia es chica si la bodega rota rápido.** Si casi todo lo comprado se vende en el mes, los
  dos métodos casi coinciden (ejercicio 7.6). Pesa en bodegas lentas y con precios que se mueven
  mucho.
- **Para comparar dos empresas hay que mirar su método.** Una con FIFO muestra más margen que otra
  idéntica con PPP en tiempos de alza. Las razones de la unidad 8 heredan esa diferencia.

---

## 9. Costo estándar y variación de precio

Muchas empresas calculan el costo de sus productos con **precios estándar**: un precio por unidad de
material fijado de antemano, que no cambia con cada factura. Sirve para cotizar y para fijar precios
sin rehacer las cuentas cada semana. Cuando el precio real se aparta del estándar, la diferencia es
una **variación de precio**:

$$\text{variación de precio} = \text{costo real de lo consumido} - q_{\text{consumida}} \times p_{\text{estándar}}$$

Si es positiva, el material costó más de lo previsto (**desfavorable**). El costo real de lo consumido
depende del método: FIFO o PPP reparten la compra cara de distinta forma entre lo consumido y lo que
queda. Por eso hay dos variaciones distintas para la misma compra, pero la suma de lo que pasa al mes
y lo que queda en bodega es siempre la misma:

$$q_{\text{comprada}} \times (p_{\text{real}} - p_{\text{estándar}}) = \text{variación del consumo} + \text{exceso que queda en bodega}$$

La variación no es un error contable: es una señal. Si se repite, el estándar quedó viejo y hay que
actualizarlo, o hay que renegociar con el proveedor.

---

## 10. Ejemplo resuelto · los cascos de una bicicletería

Una bicicletería lleva sus cascos con sistema permanente. En mayo de 2026:

| Fecha | Hecho |
|---|---|
| 01-05-2026 | Saldo inicial: 40 cascos a $18.500 |
| 06-05-2026 | Compra a crédito de 60 cascos a $19.700 neto |
| 12-05-2026 | Venta a crédito de 70 cascos a $32.900 neto |
| 20-05-2026 | Compra de 50 cascos a $20.300 neto |
| 27-05-2026 | Venta de 55 cascos a $33.500 neto |
| 31-05-2026 | Conteo físico: hay 24 cascos |

Entraron 150 cascos con un costo de **$2.937.000** y se vendieron 125. La tarjeta dice que deberían
quedar 25; hay 24: **una merma de 1 casco**.

**Paso 1 · Tarjeta FIFO.** Cada venta empieza por el lote más antiguo.

| Fecha | Movimiento | Entra | Sale | Saldo (u) | Saldo (pesos) | Lotes en bodega |
|---|---|---|---|---|---|---|
| 01-05-2026 | Saldo inicial | 40 × 18.500 = 740.000 |  | 40 | 740.000 | 40 × 18.500 |
| 06-05-2026 | Compra | 60 × 19.700 = 1.182.000 |  | 100 | 1.922.000 | 40 × 18.500 + 60 × 19.700 |
| 12-05-2026 | Venta |  | 40 × 18.500 + 30 × 19.700 = 1.331.000 | 30 | 591.000 | 30 × 19.700 |
| 20-05-2026 | Compra | 50 × 20.300 = 1.015.000 |  | 80 | 1.606.000 | 30 × 19.700 + 50 × 20.300 |
| 27-05-2026 | Venta |  | 30 × 19.700 + 25 × 20.300 = 1.098.500 | 25 | 507.500 | 25 × 20.300 |
| 31-05-2026 | Merma |  | 1 × 20.300 | 24 | 487.200 | 24 × 20.300 |

**Paso 2 · Tarjeta PPP (promedio móvil).** El promedio cambia solo cuando entra algo:
$1{.}922{.}000 / 100 = 19{.}220$ y después $1{.}591{.}600 / 80 = 19{.}895$.

| Fecha | Movimiento | Entra | Sale | Saldo (u) | Saldo (pesos) | Promedio |
|---|---|---|---|---|---|---|
| 01-05-2026 | Saldo inicial | 40 × 18.500 = 740.000 |  | 40 | 740.000 | 18.500 |
| 06-05-2026 | Compra | 60 × 19.700 = 1.182.000 |  | 100 | 1.922.000 | 19.220 |
| 12-05-2026 | Venta |  | 70 × 19.220 = 1.345.400 | 30 | 576.600 | 19.220 |
| 20-05-2026 | Compra | 50 × 20.300 = 1.015.000 |  | 80 | 1.591.600 | 19.895 |
| 27-05-2026 | Venta |  | 55 × 19.895 = 1.094.225 | 25 | 497.375 | 19.895 |
| 31-05-2026 | Merma |  | 1 × 19.895 | 24 | 477.480 | 19.895 |

**Paso 3 · Los asientos (con FIFO).** Los de la primera compra, la primera venta y la merma:

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 06-05-2026 | Existencias | 1.182.000 |  |
|  |  | IVA crédito fiscal | 224.580 |  |
|  |  | Proveedores |  | 1.406.580 |
|  |  | *Compra de 60 cascos a crédito* |  |  |
| 2 | 12-05-2026 | Clientes | 2.740.570 |  |
|  |  | Ventas |  | 2.303.000 |
|  |  | IVA débito fiscal |  | 437.570 |
|  |  | *Venta de 70 cascos a crédito* |  |  |
| 3 | 12-05-2026 | Costo de ventas | 1.331.000 |  |
|  |  | Existencias |  | 1.331.000 |
|  |  | *Costo de la venta del 12-05 (FIFO)* |  |  |
| 4 | 31-05-2026 | Pérdida por merma | 20.300 |  |
|  |  | Existencias |  | 20.300 |
|  |  | *Merma detectada en el conteo (FIFO)* |  |  |

Con PPP, el asiento 3 iría por $1.345.400 y el 4 por $19.895.

**Paso 4 · Los dos métodos lado a lado.** Ventas del mes: 2.303.000 + 1.842.500 = **$4.145.500**.

| | FIFO | PPP |
|---|---|---|
| Costo de ventas | 2.429.500 | 2.439.625 |
| Margen bruto | 1.716.000 | 1.705.875 |
| Merma | 20.300 | 19.895 |
| Saldo final (24 cascos) | 487.200 | 477.480 |
| Costo de ventas + merma + saldo | 2.937.000 | 2.937.000 |

FIFO muestra **$10.125** más de margen bruto. Esa plata no desaparece: el PPP la deja de más entre la
bodega y la merma. La suma de cada columna es los $2.937.000 que costó todo lo disponible.

**Paso 5 · Y si fuera periódico.** Sin tarjeta, al 31-05 se cuentan 24 cascos. Promedio del período:
$2{.}937{.}000 / 150 = 19{.}580$. Inventario final: 24 × 19.580 = **$469.920**. Costo de ventas por
diferencia: 2.937.000 − 469.920 = **$2.467.080**. Ahí adentro están los 125 cascos vendidos (125 ×
19.580 = $2.447.500) y el casco perdido, sin que nadie lo vea.

**Cómo se lee.** Con precios subiendo, FIFO muestra más margen porque carga a las ventas los cascos
viejos y baratos; el PPP queda $10.125 por debajo. Para decidir el precio del próximo pedido, la
bicicletería no debe mirar ninguno de los dos costos históricos sino el de reposición: el último casco
costó $20.300, y ese es el piso de su margen. El sistema permanente, además, le mostró que perdió un
casco; con el periódico se habría enterado solo de que el margen bajó.

---

## 11. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Registrar la venta y olvidar el asiento del costo | En el permanente, cada venta lleva dos asientos: el de la venta y el de Costo de ventas contra Existencias |
| Poner el IVA en Existencias | Existencias va al costo neto; el IVA de la compra va a IVA crédito fiscal porque se recupera |
| Valorizar la salida al precio de venta | La tarjeta va a costo; el precio de venta solo aparece en el asiento de la venta |
| Devolución de venta que entra al precio de venta | Entra al costo con que salió; el precio se reversa en Ventas e IVA débito |
| Devolución de compra al promedio | Sale al precio de la compra que se devuelve |
| Recalcular el promedio después de una venta | Una salida no cambia el promedio; solo las entradas lo mueven |
| Mezclar el promedio móvil con el del período | En el permanente el promedio se recalcula con cada entrada; el del período es otro número |
| Meter la merma en el costo de ventas | Va a Pérdida por merma; si se esconde en el costo, el margen miente |
| Comparar el margen de dos empresas sin ver su método | Con alza de precios FIFO muestra más margen que PPP con la misma operación |
| Creer que la tarjeta cuadra porque cada fila suma | El chequeo es costo de ventas + mermas + saldo = costo de lo disponible, y el saldo en unidades = el conteo |

---

## 12. Práctica

Diez ejercicios: 7.1 a 7.4 básicos, 7.5 a 7.8 intermedios, 7.9 y 7.10 de desafío. Las pautas están en la
sección 13. El IVA es 19 %. La planilla `planillas/u07_inventarios.xlsx` trae las tarjetas del ejemplo,
de 7.5, de 7.10 y del caso, con fórmulas.

**7.1 · La librería que cuenta a fin de mes (básico).** Una librería usa sistema periódico. Inventario
inicial $3.250.000, compras netas del mes $8.940.000, inventario final contado $2.715.000 y ventas
netas $14.600.000. Calcula el costo de ventas y el margen bruto (en pesos y en porcentaje). ¿Qué parte
de ese costo de ventas podría no haberse vendido?

**7.2 · Una compra y una venta, FIFO (básico).** Saldo inicial al 02-06-2026: 120 unidades a $4.300.
El 09-06-2026 se compran 200 a $4.580 y el 16-06-2026 se venden 250. Con FIFO, calcula el costo de la
venta y el saldo final.

**7.3 · Lo mismo con PPP (básico).** Con los datos de 7.2 y promedio ponderado: promedio después de la
compra, costo de la venta y saldo final. ¿Cuánto más costo de ventas da el PPP que el FIFO, y por qué?

**7.4 · Los asientos (básico).** La compra de 7.2 fue a crédito y la venta, al contado a $7.200 neto
cada unidad. Registra la compra, la venta y el costo (con PPP). ¿Cuál es el margen bruto?

**7.5 · Pintura con devoluciones (intermedio).** Una distribuidora de pintura lleva el galón con PPP
móvil. En julio de 2026: saldo inicial de 314 galones a $8.230 (01-07); compra de 506 a $8.640 (04-07);
devuelve 35 de esa compra (07-07); vende 437 (15-07); un cliente devuelve 23 de esa venta (18-07);
compra 406 a $8.920 (22-07); vende 479 (28-07); el conteo del 31-07 encuentra 295 galones. Arma la
tarjeta y calcula el costo de ventas neto, la merma y el saldo final.

**7.6 · Rollos de film: FIFO, PPP y promedio del período (intermedio).** Saldo inicial 470 rollos a
$1.240 (01-08-2026); compra de 705 a $1.295 (05-08); venta de 1.013 a $2.090 neto (12-08); compra de
801 a $1.380 (19-08); venta de 836 a $2.140 neto (26-08). (a) Arma las tarjetas FIFO y PPP y compara el
margen bruto. (b) Calcula el costo de ventas con un solo promedio del período (sistema periódico). (c)
¿Por qué los tres dan tan parecido?

**7.7 · Harina a costo estándar (intermedio).** Una panadería costea su pan con harina a $14.200 el saco
(estándar). Tiene 60 sacos a ese precio, compra 140 a $14.650 y consume 150 en el mes. (a) Costo real
del consumo con FIFO y con PPP, y su variación de precio contra el estándar. (b) La variación de
precio de toda la compra y cuánto de ella queda en la bodega con cada método. (c) Si el proveedor
mantiene $14.650 el mes siguiente y se consumen otros 150 sacos, ¿qué variación habrá? ¿Qué decide la
panadería?

**7.8 · El conteo (intermedio).** (a) Una ferretería con sistema permanente tiene en la tarjeta 1.240
cajas de tornillos a un promedio de $3.150; el conteo encuentra 1.212. Registra el ajuste y di qué
porcentaje se perdió. (b) Otra ferretería, con sistema periódico, tuvo un inventario inicial de
$4.100.000 y compras por $11.350.000, y contó las mismas 1.212 cajas a $3.150. Calcula su costo de
ventas. Si el conteo hubiera incluido por error 40 cajas que no estaban, ¿cuánto se inflaría la
utilidad del mes? ¿Qué pasa el mes siguiente?

**7.9 · Cuando los precios bajan (desafío).** Saldo inicial 380 unidades a $6.900 (01-09-2026); compra
de 608 a $6.510 (08-09); venta de 713 (14-09); compra de 475 a $6.120 (21-09); venta de 597 (28-09).
(a) Tarjetas FIFO y PPP. (b) ¿Cuál da más costo de ventas y por qué? (c) ¿Cuál deja el saldo más cerca
del precio de reposición? (d) El gerente propone pasarse a PPP este año «porque da más utilidad». ¿Qué
le respondes?

**7.10 · Mochilas: la tarjeta completa (desafío).** Una tienda vende mochilas a $35.581 cada una, IVA
incluido, y lleva FIFO. Todo se paga y se cobra por transferencia. En octubre de 2026: saldo inicial
83 mochilas a $16.100 (01-10); compra de 127 a $16.900 neto (05-10); venta de 154 (09-10); devolución de
9 de esa venta (13-10); compra de 96 a $17.450 neto (20-10); devuelve 6 de esa compra (24-10); venta de
117 (27-10); el conteo del 31-10 encuentra 37. (a) Tarjeta FIFO. (b) Todos los asientos. (c) Margen
bruto y resultado después de la merma. (d) IVA del mes y el asiento de su pago el 12-11-2026.

---

## 13. Pautas

**7.1.** Costo de ventas: 3.250.000 + 8.940.000 − 2.715.000 = **$9.475.000**. Margen bruto:
14.600.000 − 9.475.000 = **$5.125.000**, el **35,1 %** de las ventas. De los $12.190.000 disponibles,
lo que no está en la bodega se da por vendido: si hubo robo o daño, está dentro de los $9.475.000 y el
margen real de lo vendido es mayor que el que se ve.

**7.2.** FIFO: salen las 120 del saldo inicial y 130 de la compra: 120 × 4.300 + 130 × 4.580 =
**$1.111.400**. Quedan 70 a $4.580: **$320.600**. Suma: $1.432.000, lo disponible.

**7.3.** Promedio: (516.000 + 916.000) / 320 = **$4.475**. Costo de la venta: 250 × 4.475 =
**$1.118.750**. Saldo: 70 × 4.475 = **$313.250**. El PPP da **$7.350** más de costo porque mezcla en
el precio de salida la compra cara; FIFO, en cambio, vendió primero las 120 baratas.

**7.4.**

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 09-06-2026 | Existencias | 916.000 |  |
|  |  | IVA crédito fiscal | 174.040 |  |
|  |  | Proveedores |  | 1.090.040 |
|  |  | *Compra a crédito* |  |  |
| 2 | 16-06-2026 | Banco | 2.142.000 |  |
|  |  | Ventas |  | 1.800.000 |
|  |  | IVA débito fiscal |  | 342.000 |
|  |  | *Venta al contado* |  |  |
| 3 | 16-06-2026 | Costo de ventas | 1.118.750 |  |
|  |  | Existencias |  | 1.118.750 |
|  |  | *Costo de la venta (PPP)* |  |  |

Margen bruto: 1.800.000 − 1.118.750 = **$681.250** (37,8 %). El IVA no toca el margen: el débito se
paga al fisco y el crédito se descuenta de él.

**7.5.**

| Fecha | Movimiento | Entra | Sale | Saldo (u) | Saldo (pesos) | Promedio |
|---|---|---|---|---|---|---|
| 01-07-2026 | Saldo inicial | 314 × 8.230 = 2.584.220 |  | 314 | 2.584.220 | 8.230 |
| 04-07-2026 | Compra | 506 × 8.640 = 4.371.840 |  | 820 | 6.956.060 | 8.483 |
| 07-07-2026 | Devolución de compra |  | 35 × 8.640 = 302.400 | 785 | 6.653.660 | 8.476 |
| 15-07-2026 | Venta |  | 437 × 8.476 = 3.704.012 | 348 | 2.949.648 | 8.476 |
| 18-07-2026 | Devolución de venta | 23 × 8.476 = 194.948 |  | 371 | 3.144.596 | 8.476 |
| 22-07-2026 | Compra | 406 × 8.920 = 3.621.520 |  | 777 | 6.766.116 | 8.708 |
| 28-07-2026 | Venta |  | 479 × 8.708 = 4.171.132 | 298 | 2.594.984 | 8.708 |
| 31-07-2026 | Merma |  | 3 × 8.708 = 26.124 | 295 | 2.568.860 | 8.708 |

Costo de ventas neto: 3.704.012 − 194.948 + 4.171.132 = **$7.680.196**. Merma: **$26.124**. Saldo:
**$2.568.860**. Chequeo: lo disponible neto de la devolución es $10.275.180, y 7.680.196 + 26.124 +
2.568.860 lo iguala. Fíjate en dos cosas: la devolución de compra salió a $8.640 (su precio) y por eso
movió el promedio; la devolución de venta entró a $8.476 (el costo con que salió) y no lo movió.

**7.6.** (a)

| Fecha | Movimiento | Entra | Sale | Saldo (u) | Saldo (pesos) | Lotes en bodega |
|---|---|---|---|---|---|---|
| 01-08-2026 | Saldo inicial | 470 × 1.240 = 582.800 |  | 470 | 582.800 | 470 × 1.240 |
| 05-08-2026 | Compra | 705 × 1.295 = 912.975 |  | 1.175 | 1.495.775 | 470 × 1.240 + 705 × 1.295 |
| 12-08-2026 | Venta |  | 470 × 1.240 + 543 × 1.295 = 1.285.985 | 162 | 209.790 | 162 × 1.295 |
| 19-08-2026 | Compra | 801 × 1.380 = 1.105.380 |  | 963 | 1.315.170 | 162 × 1.295 + 801 × 1.380 |
| 26-08-2026 | Venta |  | 162 × 1.295 + 674 × 1.380 = 1.139.910 | 127 | 175.260 | 127 × 1.380 |

| Fecha | Movimiento | Entra | Sale | Saldo (u) | Saldo (pesos) | Promedio |
|---|---|---|---|---|---|---|
| 01-08-2026 | Saldo inicial | 470 × 1.240 = 582.800 |  | 470 | 582.800 | 1.240 |
| 05-08-2026 | Compra | 705 × 1.295 = 912.975 |  | 1.175 | 1.495.775 | 1.273 |
| 12-08-2026 | Venta |  | 1.013 × 1.273 = 1.289.549 | 162 | 206.226 | 1.273 |
| 19-08-2026 | Compra | 801 × 1.380 = 1.105.380 |  | 963 | 1.311.606 | 1.362 |
| 26-08-2026 | Venta |  | 836 × 1.362 = 1.138.632 | 127 | 172.974 | 1.362 |

Ventas: **$3.906.210**. Costo de ventas FIFO **$2.425.895** y PPP **$2.428.181**; margen bruto
**$1.480.315** y **$1.478.029**: FIFO gana por **$2.286**. Saldos: $175.260 y $172.974 (los dos suman
con su costo de ventas $2.601.155). (b) Promedio del período: 2.601.155 / 1.976 = **$1.316,37**. Costo
de ventas: 1.849 × 1.316,37 = **$2.433.976**; inventario final **$167.179**; margen bruto
**$1.472.234**. Es el más alto de los tres porque le carga a la venta del 12-08 parte de la compra cara
del 19-08, que todavía no llegaba. (c) La bodega rota casi entera cada mes: de 1.976 rollos disponibles
quedan 127. Cuando casi todo se vende, casi todo el costo va al resultado con cualquier método, y la
diferencia se reduce a lo poco que queda en la bodega.

**7.7.** (a) Con FIFO salen los 60 sacos a estándar y 90 de la compra: 60 × 14.200 + 90 × 14.650 =
**$2.170.500**. Con PPP, promedio (852.000 + 2.051.000) / 200 = **$14.515** y consumo 150 × 14.515 =
**$2.177.250**. El estándar es 150 × 14.200 = **$2.130.000**. Variación de precio desfavorable:
**$40.500** con FIFO y **$47.250** con PPP. (b) Toda la compra salió 140 × 450 = **$63.000** sobre el
estándar. En bodega queda el resto: **$22.500** con FIFO (50 sacos a $14.650) y **$15.750** con PPP. Con
cada método, lo consumido más lo que queda suma los $63.000: el método solo decide cuándo aparece. (c)
Si todo el consumo es a $14.650, la variación será 150 × 450 = **$67.500**, y así cada mes. Una
variación que se repite ya no es ruido: la panadería debe actualizar el estándar (con PPP, cada saco
consumido ya le cuesta **$315** más) y revisar si el precio del pan aguanta ese costo o si busca otro
proveedor.

**7.8.** (a) Faltan 28 cajas: 28 × 3.150 = **$88.200**, el **2,26 %** de lo que decía la tarjeta.
Asiento: Pérdida por merma $88.200 al Debe, Existencias $88.200 al Haber. (b) Inventario final:
1.212 × 3.150 = **$3.817.800**; costo de ventas 4.100.000 + 11.350.000 − 3.817.800 = **$11.632.200**.
Con el error, el inventario final sería **$3.943.800** y el costo de ventas **$11.506.200**: la
utilidad sube **$126.000** sin que se haya vendido nada más. El mes siguiente ese inventario inflado
es el inicial, el costo de ventas sube en los mismos $126.000 y la utilidad baja: el error se devuelve
solo, pero deja dos meses mal informados.

**7.9.** (a)

| Fecha | Movimiento | Entra | Sale | Saldo (u) | Saldo (pesos) | Lotes en bodega |
|---|---|---|---|---|---|---|
| 01-09-2026 | Saldo inicial | 380 × 6.900 = 2.622.000 |  | 380 | 2.622.000 | 380 × 6.900 |
| 08-09-2026 | Compra | 608 × 6.510 = 3.958.080 |  | 988 | 6.580.080 | 380 × 6.900 + 608 × 6.510 |
| 14-09-2026 | Venta |  | 380 × 6.900 + 333 × 6.510 = 4.789.830 | 275 | 1.790.250 | 275 × 6.510 |
| 21-09-2026 | Compra | 475 × 6.120 = 2.907.000 |  | 750 | 4.697.250 | 275 × 6.510 + 475 × 6.120 |
| 28-09-2026 | Venta |  | 275 × 6.510 + 322 × 6.120 = 3.760.890 | 153 | 936.360 | 153 × 6.120 |

| Fecha | Movimiento | Entra | Sale | Saldo (u) | Saldo (pesos) | Promedio |
|---|---|---|---|---|---|---|
| 01-09-2026 | Saldo inicial | 380 × 6.900 = 2.622.000 |  | 380 | 2.622.000 | 6.900 |
| 08-09-2026 | Compra | 608 × 6.510 = 3.958.080 |  | 988 | 6.580.080 | 6.660 |
| 14-09-2026 | Venta |  | 713 × 6.660 = 4.748.580 | 275 | 1.831.500 | 6.660 |
| 21-09-2026 | Compra | 475 × 6.120 = 2.907.000 |  | 750 | 4.738.500 | 6.318 |
| 28-09-2026 | Venta |  | 597 × 6.318 = 3.771.846 | 153 | 966.654 | 6.318 |

(b) Costo de ventas FIFO **$8.550.720** y PPP **$8.520.426**: con precios a la baja, FIFO da
**$30.294** más de costo porque vende primero lo viejo, que es lo caro. (c) FIFO: su saldo, **$936.360**,
es 153 unidades al último precio ($6.120), el de reposición. El PPP ($966.654) arrastra precios viejos.
Los dos suman con su costo de ventas los $9.487.080 disponibles. (d) Tres cosas: el método no cambia la
caja (salvo por el impuesto), solo el momento en que se reconoce el costo; la ley obliga a mantener el
método elegido al menos cinco ejercicios, así que no se cambia por un año bueno; y cuando los precios
vuelvan a subir, el efecto se invierte. Elegir el método por la utilidad de un año es maquillar.

**7.10.** (a)

| Fecha | Movimiento | Entra | Sale | Saldo (u) | Saldo (pesos) | Lotes en bodega |
|---|---|---|---|---|---|---|
| 01-10-2026 | Saldo inicial | 83 × 16.100 = 1.336.300 |  | 83 | 1.336.300 | 83 × 16.100 |
| 05-10-2026 | Compra | 127 × 16.900 = 2.146.300 |  | 210 | 3.482.600 | 83 × 16.100 + 127 × 16.900 |
| 09-10-2026 | Venta |  | 83 × 16.100 + 71 × 16.900 = 2.536.200 | 56 | 946.400 | 56 × 16.900 |
| 13-10-2026 | Devolución de venta | 9 × 16.900 = 152.100 |  | 65 | 1.098.500 | 65 × 16.900 |
| 20-10-2026 | Compra | 96 × 17.450 = 1.675.200 |  | 161 | 2.773.700 | 65 × 16.900 + 96 × 17.450 |
| 24-10-2026 | Devolución de compra |  | 6 × 17.450 = 104.700 | 155 | 2.669.000 | 65 × 16.900 + 90 × 17.450 |
| 27-10-2026 | Venta |  | 65 × 16.900 + 52 × 17.450 = 2.005.900 | 38 | 663.100 | 38 × 17.450 |
| 31-10-2026 | Merma |  | 1 × 17.450 | 37 | 645.650 | 37 × 17.450 |

(b) El precio neto es 35.581 / 1,19 = **$29.900**.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 05-10-2026 | Existencias | 2.146.300 |  |
|  |  | IVA crédito fiscal | 407.797 |  |
|  |  | Banco |  | 2.554.097 |
|  |  | *Compra de 127 mochilas por transferencia* |  |  |
| 2 | 09-10-2026 | Banco | 5.479.474 |  |
|  |  | Ventas |  | 4.604.600 |
|  |  | IVA débito fiscal |  | 874.874 |
|  |  | *Venta de 154 mochilas* |  |  |
| 3 | 09-10-2026 | Costo de ventas | 2.536.200 |  |
|  |  | Existencias |  | 2.536.200 |
|  |  | *Costo de la venta del 09-10* |  |  |
| 4 | 13-10-2026 | Ventas | 269.100 |  |
|  |  | IVA débito fiscal | 51.129 |  |
|  |  | Banco |  | 320.229 |
|  |  | *Devolución de 9 mochilas de la venta del 09-10* |  |  |
| 5 | 13-10-2026 | Existencias | 152.100 |  |
|  |  | Costo de ventas |  | 152.100 |
|  |  | *Las 9 mochilas vuelven a bodega a su costo* |  |  |
| 6 | 20-10-2026 | Existencias | 1.675.200 |  |
|  |  | IVA crédito fiscal | 318.288 |  |
|  |  | Banco |  | 1.993.488 |
|  |  | *Compra de 96 mochilas por transferencia* |  |  |
| 7 | 24-10-2026 | Banco | 124.593 |  |
|  |  | Existencias |  | 104.700 |
|  |  | IVA crédito fiscal |  | 19.893 |
|  |  | *Devolución de 6 mochilas al proveedor* |  |  |
| 8 | 27-10-2026 | Banco | 4.162.977 |  |
|  |  | Ventas |  | 3.498.300 |
|  |  | IVA débito fiscal |  | 664.677 |
|  |  | *Venta de 117 mochilas* |  |  |
| 9 | 27-10-2026 | Costo de ventas | 2.005.900 |  |
|  |  | Existencias |  | 2.005.900 |
|  |  | *Costo de la venta del 27-10* |  |  |
| 10 | 31-10-2026 | Pérdida por merma | 17.450 |  |
|  |  | Existencias |  | 17.450 |
|  |  | *Merma del conteo* |  |  |
| 11 | 12-11-2026 | IVA débito fiscal | 1.488.422 |  |
|  |  | IVA crédito fiscal |  | 706.192 |
|  |  | Banco |  | 782.230 |
|  |  | *Pago del IVA de octubre* |  |  |

(c) Se vendieron 154 − 9 + 117 = 262 mochilas: ventas **$7.833.800**. Costo de ventas: 2.536.200 −
152.100 + 2.005.900 = **$4.390.000**. Margen bruto **$3.443.800** (44,0 %). Después de la merma,
**$3.426.350**. Chequeo: lo disponible neto de la devolución de compra es $5.053.100 = 4.390.000 +
17.450 + 645.650. (d) Débito: 19 % de las ventas netas, **$1.488.422**. Crédito: 19 % de las compras
netas, descontada la devolución, **$706.192**. Se pagan **$782.230** en noviembre (asiento 11). La devolución de
venta rebaja el débito y la de compra rebaja el crédito: por eso las dos llevan su IVA.

---

## 14. Caso integrador · las poleras lisas de Estampa Sur

> En marzo, Estampa Sur produce 5.590 prendas. Las poleras básicas se estampan sobre poleras lisas que
> el taller compra. La unidad 2 dejó el asiento 1 del mes: la compra de 2.100 poleras lisas a crédito.

**Lo que recibe.** De la unidad 1, el saldo inicial: 900 poleras lisas a $2.400, **$2.160.000**. De la
unidad 2, la compra de la semana 1: 2.100 poleras a $2.450, **$5.145.000** netos, con $977.550 de IVA
crédito y $6.122.550 a pagar al proveedor. Del plan de producción, el consumo: 1.100 poleras en la
semana 2 y 1.136 en la semana 4, en total **2.236**, las poleras básicas que se producen. El costo de
todo el taller se calcula con un **costo estándar** de $2.400 por polera lisa.

**Pregunta.** ¿Cuánto costaron de verdad las poleras consumidas, con FIFO y con PPP? ¿Cuánto se apartan
del estándar? ¿Qué decide el taller?

**Desarrollo.**

1. **Tarjeta FIFO.**

| Fecha | Movimiento | Entra | Sale | Saldo (u) | Saldo (pesos) | Lotes en bodega |
|---|---|---|---|---|---|---|
| 1 de marzo | Saldo inicial | 900 × 2.400 = 2.160.000 |  | 900 | 2.160.000 | 900 × 2.400 |
| semana 1 | Compra | 2.100 × 2.450 = 5.145.000 |  | 3.000 | 7.305.000 | 900 × 2.400 + 2.100 × 2.450 |
| semana 2 | Consumo |  | 900 × 2.400 + 200 × 2.450 = 2.650.000 | 1.900 | 4.655.000 | 1.900 × 2.450 |
| semana 4 | Consumo |  | 1.136 × 2.450 = 2.783.200 | 764 | 1.871.800 | 764 × 2.450 |

2. **Tarjeta PPP.** Como la compra llega antes de los dos consumos, hay un solo promedio:
$7{.}305{.}000 / 3{.}000 = 2{.}435$.

| Fecha | Movimiento | Entra | Sale | Saldo (u) | Saldo (pesos) | Promedio |
|---|---|---|---|---|---|---|
| 1 de marzo | Saldo inicial | 900 × 2.400 = 2.160.000 |  | 900 | 2.160.000 | 2.400 |
| semana 1 | Compra | 2.100 × 2.450 = 5.145.000 |  | 3.000 | 7.305.000 | 2.435 |
| semana 2 | Consumo |  | 1.100 × 2.435 = 2.678.500 | 1.900 | 4.626.500 | 2.435 |
| semana 4 | Consumo |  | 1.136 × 2.435 = 2.766.160 | 764 | 1.860.340 | 2.435 |

3. **Contra el estándar.** El estándar del consumo es 2.236 × 2.400 = **$5.366.400**.

| | FIFO | PPP |
|---|---|---|
| Costo real del consumo | 5.433.200 | 5.444.660 |
| Variación de precio (desfavorable) | 66.800 | 78.260 |
| Saldo de 764 poleras al 31 de marzo | 1.871.800 | 1.860.340 |
| Exceso sobre el estándar que queda en bodega | 38.200 | 26.740 |
| Variación de toda la compra (2.100 × \$50) | 105.000 | 105.000 |

Con FIFO el consumo cuesta en promedio $2.429,87 por polera; con PPP, $2.435: **\$35** sobre el
estándar.

4. **Los asientos del consumo (PPP).** El taller usa PPP, el método del curso, y lo mantendrá cinco
   ejercicios. Productos en proceso recibe el estándar; la diferencia va a una cuenta de variación:

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| U7-1 | marzo, semana 2 | Productos en proceso | 2.640.000 |  |
|  |  | Variación de precio de materias primas | 38.500 |  |
|  |  | Poleras lisas básicas |  | 2.678.500 |
|  |  | *Consumo de 1.100 poleras lisas a estándar* |  |  |
| U7-2 | marzo, semana 4 | Productos en proceso | 2.726.400 |  |
|  |  | Variación de precio de materias primas | 39.760 |  |
|  |  | Poleras lisas básicas |  | 2.766.160 |
|  |  | *Consumo de 1.136 poleras lisas a estándar* |  |  |

Con FIFO serían 2.650.000 y 2.783.200 al Haber, con variaciones de 10.000 y 56.800.

**Lectura.** El proveedor subió \$50 por polera y eso le cuesta al taller **$78.260** en marzo (con PPP)
que el costo estándar no muestra. Cada polera básica tiene un margen de contribución estándar de
$1.380; con el costo real de marzo queda en **$1.345** (2,5 % menos). Si el precio de $2.450 se queda,
el promedio terminará en $2.450 y el margen en **$1.330** (3,6 % menos): unos **$111.800** al mes con la
producción de marzo. No justifica subir el precio de venta de $3.990, pero sí dos decisiones: actualizar
el estándar a $2.450 desde abril, para que las cotizaciones no se hagan con un costo que ya no existe, y
cotizar con otro proveedor antes de la próxima compra.

**Lo que pasa a las unidades siguientes.** A la unidad 8: el saldo de poleras lisas al 31 de marzo,
**$1.860.340** (764 poleras, PPP), para el balance, y la variación de **$78.260**, que el estado de
resultados a costo estándar no trae y que el balance obliga a reconocer. A la unidad 10: el costo
estándar de $2.400 por polera lisa, con el que se costea cada prenda.

---

## 15. Para seguir

**En los libros del ramo.**

- Gálvez y Clarke, *Contabilidad financiera para la dirección de empresas* (Ediciones UC), capítulo 7:
  sistemas periódico y perpetuo, FIFO, LIFO y promedio. Es la bibliografía obligatoria del programa.
- Weygandt, Kimmel y Kieso, *Accounting Principles* (Wiley, 12.ª ed., 2014): la parte de inventarios
  de una empresa comercial, con tarjetas FIFO y promedio. Ojo: es un libro de Estados Unidos y trabaja
  también con LIFO, que en Chile no se usa.
- Horngren, *Contabilidad de costos* (Pearson, 2012): costos estándar y variaciones de precio, para la
  sección 9.

**Abierto y gratis.**

- OpenStax, *Principles of Accounting, Volume 1: Financial Accounting*, en inglés, capítulo 10
  (*Inventory*): métodos de valorización, sistema periódico y perpetuo, y errores de inventario.
  Licencia CC BY-NC-SA: https://openstax.org/books/principles-financial-accounting/pages/10-why-it-matters
- El Oficio N.º 3190 del SII (17-12-2015), sobre los métodos de valorización de existencias del
  artículo 30 de la ley de la renta:
  https://www.sii.cl/normativa_legislacion/jurisprudencia_administrativa/ley_impuesto_renta/2015/ja3190.htm

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un producto con dos compras, dos ventas, una
devolución de venta y una merma; déjame armar la tarjeta FIFO y la PPP, y corrígeme fila por fila».
