---
ramo: Contabilidad y Costos
unidad: 9
titulo: Costos, conceptos y clasificación
version: 0.1 (16-10-2026)
requiere: [04-depreciacion, 05-ajustes-de-cierre, 07-inventarios, 08-razones-financieras]
alimenta: [10-absorcion-y-variable, 11-asignacion-de-costos-indirectos, 12-costo-volumen-utilidad]
verificacion: verificacion/u09_clasificacion_costos.py
---

# Unidad 9 · Costos, conceptos y clasificación

**Qué vas a poder hacer.** Separar lo que es costo de lo que es gasto o inversión; clasificar cada
partida como costo del producto o del período, directa o indirecta, fija, variable o semivariable;
separar un costo semivariable en su parte fija y su parte variable; armar el estado de costo de lo
producido y vendido, y decidir un pedido especial o un «hacer o comprar» con los costos relevantes, sin
dejarte engañar por el costo unitario que trae fijos ni por lo que ya se gastó.

**Lo que necesitas antes.** La depreciación (unidad 4), porque es un costo que no sale de caja; los
pagos anticipados (unidad 5), porque un pago no es un costo del mes; los inventarios (unidad 7), porque
el costo del producto vive ahí hasta que se vende, y el estado de resultados (unidad 8).

**Tiempo.** Unas 5 horas: 2 de lectura con el ejemplo y 3 de práctica.

**Planilla.** `planillas/u09_clasificacion_costos.xlsx` trae el ejemplo, la separación del gas del
horno y la pieza del caso, todo con fórmulas.

---

## 1. Costo, gasto e inversión

Hasta la unidad 8 todo lo que se consumía en el mes iba al estado de resultados. En una empresa que
fabrica eso ya no es cierto. Hay tres destinos posibles para un peso que la empresa sacrifica:

- **Costo (del producto).** Lo que se consume para **fabricar**: la tela, la tinta, el sueldo de quien
  estampa, el arriendo del taller. No va al estado de resultados cuando se incurre: se **acumula en el
  inventario** (un activo) y pasa a resultados como **costo de ventas** recién cuando el producto se
  vende.
- **Gasto (del período).** Lo que se consume para **administrar, vender o financiar**: el sueldo del
  contador, la publicidad, la comisión del vendedor, los intereses. Va a resultados en el mes en que
  se incurre, se venda o no se venda algo.
- **Inversión.** Lo que se compra para usar durante varios períodos: una máquina, un vehículo. Va al
  balance como activo fijo; su costo del mes es la **depreciación** (unidad 4), no el precio de compra.

**Desembolso no es costo.** Pagar no es consumir. Pagar el arriendo de los próximos tres meses deja un
activo (arriendo pagado por anticipado, unidad 5); el costo de cada mes es la parte que se devenga. Y al
revés: la depreciación es costo sin que salga un peso ese mes. El **IVA crédito fiscal** tampoco es
costo: es un derecho contra el fisco que se descuenta del IVA débito (unidad 3). Los costos se miden
siempre en neto.

El **ciclo del costo** en una fábrica:

$$\text{materias primas} \;\to\; \text{productos en proceso} \;\to\; \text{productos terminados} \;\to\; \text{costo de ventas}$$

Los tres primeros son cuentas de inventario en el balance. Solo el último es resultado.

**Por qué importa.** Si fabricas 1.000 unidades y vendes 600, el costo de las 400 que quedan en bodega
no es una pérdida del mes: es un activo que se venderá después. Tratarlo como gasto subestima la
utilidad del mes y el valor del inventario. Esa diferencia es el corazón de la unidad 10.

---

## 2. Los tres elementos del costo de fabricación

| Elemento | Qué es | Ejemplo en un taller de estampado |
|---|---|---|
| **Materia prima directa (MPD)** | Material que queda en el producto y se mide por unidad | la polera lisa, la tinta |
| **Mano de obra directa (MOD)** | Trabajo de quien transforma la materia prima | quien estampa y quien dobla |
| **Costos indirectos de fabricación (CIF)** | Todo lo demás que la fábrica necesita para producir | arriendo del taller, depreciación de la máquina, supervisor, limpieza |

Los CIF se dividen a su vez en materia prima indirecta (MPI: lija, pegamento, film, lo que se usa pero
no vale la pena medir por unidad), mano de obra indirecta (MOI: supervisión, mantención, aseo de planta)
y otros gastos generales de fabricación (energía de la planta, arriendo, seguros y depreciación de lo
productivo). Dos sumas tienen nombre propio:

$$\text{costo primo} = \text{MPD} + \text{MOD} \qquad \text{costo de conversión} = \text{MOD} + \text{CIF}$$

$$\text{costo de fabricación} = \text{MPD} + \text{MOD} + \text{CIF}$$

El costo primo es lo que se puede asignar a cada unidad sin repartir nada. El de conversión es lo que
cuesta **transformar** la materia prima.

**Directo o indirecto depende del objeto de costo.** Un costo es directo respecto de algo (un producto,
un pedido, un departamento) si se puede medir para ese algo de forma económica. El sueldo del jefe de
planta es indirecto respecto de cada polera, pero directo respecto de la planta. Por eso la pregunta
«¿es directo?» siempre lleva un «¿respecto de qué?».

**Lo que no es costo de fabricación.** El sueldo de la administrativa, la publicidad, el despacho a
clientes, la comisión del vendedor y los intereses son gastos del período, aunque la empresa sea una
fábrica. Un mismo concepto puede caer a los dos lados: la luz de la planta es CIF, la luz de la oficina
es gasto de administración. Y el terreno no se deprecia (unidad 4): nunca aparece como CIF.

---

## 3. Fijos, variables y semivariables

La segunda pregunta es cómo se mueve el costo cuando cambia la actividad (unidades, horas, kilos).

| Comportamiento | Total del mes | Por unidad | Ejemplos |
|---|---|---|---|
| **Variable** | sube en proporción a la actividad | constante | materia prima, comisión por venta, energía de la máquina |
| **Fijo** | constante dentro del rango relevante | baja cuando sube la actividad | arriendo, depreciación lineal, sueldos fijos, seguros |
| **Semivariable** | una parte fija más una variable | baja, pero no tanto | gas del horno con cargo fijo, teléfono con plan más minutos |

$$\text{costo total} = a + b \cdot q$$

donde $a$ es el costo fijo del período, $b$ el costo variable por unidad y $q$ la actividad.

**La trampa del costo fijo unitario.** Un arriendo de $1.200.000 cuesta $1.500 por almuerzo si se
venden 800 y $500 si se venden 2.400 (ejercicio 9.3). Nada se abarató: el arriendo es el mismo. El
costo fijo **unitario** depende del volumen; por eso no sirve como costo «de una unidad más».

**Rango relevante.** Un costo es fijo dentro de un rango de actividad. Si el taller dobla su producción
necesitará otra máquina u otro turno, y el «fijo» salta a un nuevo nivel (costo escalonado).

**La MOD no siempre es variable.** Si se paga a trato (por pieza), es variable. Si se paga un sueldo
mensual que no cambia con las unidades, es fija aunque sea directa. Directo/indirecto y fijo/variable
son dos preguntas distintas.

### Separar un semivariable · punto alto y punto bajo

Con los registros de varios meses (actividad y costo), se toman el mes de **mayor actividad** y el de
**menor actividad**. La diferencia de costo entre ellos solo puede venir de la parte variable:

$$b = \frac{\text{costo}_{\text{alto}} - \text{costo}_{\text{bajo}}}{q_{\text{alto}} - q_{\text{bajo}}} \qquad a = \text{costo}_{\text{alto}} - b \cdot q_{\text{alto}}$$

Alto y bajo se eligen por **actividad**, no por costo. Es rápido y usa solo dos puntos: si uno de ellos
es raro (un mes con una avería), la recta sale torcida. La **regresión lineal** (mínimos cuadrados)
usa todos los meses; en una planilla son las funciones `PENDIENTE` e `INTERSECCION.EJE`. Se menciona
aquí como el método de respaldo: el ejercicio 9.10 muestra cuándo hace falta.

---

## 4. Costos relevantes para decidir

Para decidir entre alternativas importa solo lo que **cambia** entre ellas y está **por venir**.

- **Costo relevante:** futuro y distinto entre las alternativas. En un pedido especial con capacidad
  ociosa, casi siempre es el costo variable más lo que el pedido agregue.
- **Costo hundido:** ya se incurrió y ninguna decisión lo cambia (la máquina comprada el año pasado, la
  investigación ya pagada). Es irrelevante, aunque duela.
- **Costo de oportunidad:** lo que se deja de ganar en la mejor alternativa que se descarta. No aparece
  en la contabilidad, pero cuenta para decidir: si aceptar un pedido obliga a dejar de vender a clientes
  normales, el margen perdido es parte del costo del pedido.
- **Costos fijos que no cambian:** el arriendo y la depreciación siguen igual se acepte o no el pedido.
  Por eso el costo unitario «completo» (con fijos repartidos) no es la vara para un pedido especial.

### El pedido especial

$$\text{acepta si} \quad (p_{\text{pedido}} - cv_{\text{pedido}}) \cdot q_{\text{pedido}} \;-\; \text{costo de oportunidad} \;>\; 0$$

Con capacidad ociosa el costo de oportunidad es cero, y el **precio mínimo** es el costo variable del
pedido. Sin capacidad, el precio mínimo sube en el margen que se deja de ganar por cada unidad
desplazada, repartido entre las unidades del pedido.

**Cuándo no basta.** Si vender barato a uno hace que los clientes normales pidan el mismo precio, el
cálculo de un mes no ve el daño. Y un pedido que se repite todos los meses deja de ser especial: tiene
que cubrir también los fijos.

### Hacer o comprar (introducción)

Se compara lo que se **ahorra** dejando de fabricar (el variable y los fijos **evitables**) contra lo
que se paga al proveedor. Los fijos que siguen igual (inevitables) no cuentan. Si el espacio liberado
se puede arrendar, ese arriendo es un costo de oportunidad de seguir fabricando. Hay razones que el
número no ve (calidad, plazos, depender de un proveedor); el número dice cuánto cuesta cada opción.

---

## 5. El estado de costo de lo producido y vendido

Es la tabla que lleva los costos del mes desde las materias primas hasta el costo de ventas:

| Paso | Cuenta |
|---|---|
| Inventario inicial de materias primas + compras netas − inventario final | = materia prima usada |
| + mano de obra directa + costos indirectos de fabricación | = **costo de fabricación** |
| + productos en proceso iniciales − productos en proceso finales | = **costo de lo producido** (de lo terminado) |
| + productos terminados iniciales − productos terminados finales | = **costo de ventas** |

La lógica es la de la tarjeta de existencias de la unidad 7 aplicada tres veces: lo que había más lo
que entró menos lo que quedó es lo que salió. El costo de ventas entra al estado de resultados; los
tres inventarios finales quedan en el balance.

El **costo unitario** de lo producido es el costo de lo producido dividido por las unidades
terminadas. Sirve para valorizar el inventario y el costo de ventas, no para decidir un pedido: trae
fijos repartidos.

---

## 6. Ejemplo resuelto · el taller de tazas en mayo

Un taller fabrica tazas de cerámica y las vende en su propia tienda. Datos de mayo (montos netos):

| Partida | Monto |
|---|---|
| Arcilla y esmalte: inventario inicial / compras / inventario final | 176.500 / 1.341.900 / 239.980 |
| Torneros y esmaltadores, pagados a trato (\$662 por taza) | 1.893.320 |
| Insumos de taller: lija, cera, guantes (\$17 por taza) | 48.620 |
| Sueldo de la supervisora de producción | 684.000 |
| Gas del horno | 297.300 |
| Depreciación del horno | 118.500 |
| Arriendo de la nave del taller | 532.000 |
| Mantención | 36.400 |
| Productos en proceso: inicial / final | 206.300 / 204.260 |
| Comisión de venta | 4 % de las ventas |
| Sueldo de la administrativa / publicidad / arriendo de la tienda | 615.000 / 174.000 / 163.000 |

Se terminaron 2.860 tazas. Había 230 tazas en bodega al inicio (a $1.710 cada una) y se vendieron
2.470 a $3.390.

**Paso 1 · Clasificar.** Arcilla y esmalte: MPD, variable. Torneros a trato: MOD, variable. Insumos de
taller: CIF (MPI), variable. Supervisora: CIF (MOI), fija. Gas del horno: CIF, semivariable.
Depreciación, arriendo de la nave y mantención: CIF, fijos. Comisión: gasto de venta, variable.
Administrativa, publicidad y arriendo de la tienda: gastos del período, fijos.

**Paso 2 · Estado de costo de lo producido y vendido.**

| Cuenta | Pesos |
|---|---|
| Materia prima usada: 176.500 + 1.341.900 − 239.980 | 1.278.420 |
| Mano de obra directa | 1.893.320 |
| CIF: 48.620 + 684.000 + 297.300 + 118.500 + 532.000 + 36.400 | 1.716.820 |
| **Costo de fabricación** | **4.888.560** |
| + productos en proceso iniciales − finales | + 206.300 − 204.260 |
| **Costo de lo producido** (2.860 tazas a $1.710) | **4.890.600** |
| + productos terminados iniciales (230 tazas) | + 393.300 |
| − productos terminados finales (230 + 2.860 − 2.470 = 620 tazas) | − 1.060.200 |
| **Costo de ventas** (2.470 tazas a $1.710) | **4.223.700** |

Costo primo: 1.278.420 + 1.893.320 = **$3.171.740**. Costo de conversión: 1.893.320 + 1.716.820 =
**$3.610.140**.

**Paso 3 · Estado de resultados del mes.**

| Cuenta | Pesos |
|---|---|
| Ventas (2.470 × 3.390) | 8.373.300 |
| − Costo de ventas | − 4.223.700 |
| **Margen bruto** | **4.149.600** |
| − Comisión (4 %) 334.932, administrativa 615.000, publicidad 174.000, arriendo tienda 163.000 | − 1.286.932 |
| **Resultado operacional** | **2.862.668** |

Los $1.060.200 de las 620 tazas en bodega no son pérdida: son inventario, y entrarán a resultados el
mes en que se vendan.

**Paso 4 · Separar el gas del horno.** Registros de enero a mayo:

| Mes | Tazas | Gas |
|---|---|---|
| Enero | 2.140 | 253.700 |
| Febrero | 1.730 | 227.340 |
| Marzo | 2.580 | 279.900 |
| Abril | 3.310 | 318.980 |
| Mayo | 2.860 | 297.300 |

Punto alto: abril (3.310 tazas). Punto bajo: febrero (1.730).

$$b = \frac{318{.}980 - 227{.}340}{3{.}310 - 1{.}730} = 58 \qquad a = 318{.}980 - 58 \times 3{.}310 = 127{.}000$$

El gas cuesta $127.000 fijos al mes (mantener el horno encendido) más \$58 por taza. Para mayo la recta
predice 127.000 + 58 × 2.860 = 127.000 + 165.880 = $292.880, y el gas real fue $297.300: $4.420 sobre lo esperado, una
diferencia chica que vale mirar si se repite. La regresión con los cinco meses da casi lo mismo
(\$58,45 por taza y $127.922 fijos): aquí ningún mes es raro.

**Paso 5 · El pedido especial.** Un café pide 380 tazas con su logo a $1.560 cada una. El logo es una
calcomanía de \$115. El horno da para 3.450 tazas al mes y en mayo se hicieron 2.860: quedan 590 libres.

- Costo variable de una taza: arcilla \$447 + mano de obra \$662 + insumos \$17 + gas \$58 = **$1.184**.
- Costo variable del pedido: 1.184 + 115 = **$1.299** por taza (sin comisión: el café compra directo).
- Contribución: (1.560 − 1.299) × 380 = 261 × 380 = **$99.180**.

Con el costo unitario completo, 1.710 + 115 = $1.825, el pedido parece perder $100.700. Es falso: el
arriendo, la supervisora, la depreciación y la parte fija del gas se pagan igual con o sin pedido.

**Cómo se lee.** El taller ganó $2.862.668 en mayo y tiene 620 tazas valorizadas a $1.710 en bodega. El
pedido del café conviene: suma $99.180 a la utilidad porque hay horno libre. El precio mínimo para
este pedido es $1.299 por taza. Si el horno estuviera lleno, habría que restar el margen de las tazas
normales que se dejarían de vender (ejercicio 9.9), y el $1.710 tampoco sería la vara: la vara sería
el costo variable más ese margen perdido.

---

## 7. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Mezclar costo y gasto: poner el sueldo de la administrativa o la publicidad en el costo de fabricación | Pregunta si se consume para **fabricar**. Si es para administrar, vender o financiar, es gasto del período |
| Usar el costo unitario total (con fijos) para decidir un pedido especial | Los fijos no cambian con el pedido. Compara el precio con el costo variable del pedido y suma el costo de oportunidad si falta capacidad |
| Contar la compra de una máquina como costo del mes | Es inversión. El costo del mes es la depreciación |
| Cargar como costo del mes un pago anticipado (el arriendo de tres meses) | Es un activo; el costo de cada mes es la parte devengada (unidad 5) |
| Sumar el IVA de las compras al costo | El IVA crédito es un derecho contra el fisco. Los costos van en neto |
| Depreciar el terreno de la planta como CIF | El terreno no se deprecia; solo la construcción y las máquinas |
| Creer que la MOD siempre es variable | Si se paga sueldo fijo, es directa y fija a la vez |
| Elegir el punto alto y el bajo por el costo | Se eligen por la **actividad**; y si uno es un mes raro, usa regresión o descártalo |
| Contar un costo hundido (lo que costó la máquina) al decidir | Lo pasado no cambia con la decisión. Solo cuenta lo futuro y distinto |
| Llamar «costo de producción» al costo de fabricación cuando hay productos en proceso | El costo de lo producido ajusta por el inventario en proceso inicial y final |

---

## 8. Práctica

Diez ejercicios: 9.1 a 9.4 básicos, 9.5 a 9.8 intermedios, 9.9 y 9.10 de desafío. Montos netos de
IVA. Las pautas están en la sección 9.

**9.1 · La fábrica de mermeladas (básico).** Clasifica cada partida del mes como MPD, MOD, CIF o gasto
del período, y como fija o variable. Calcula MPD, MOD, CIF, costo de fabricación, costo primo, costo de
conversión y gastos del período, y separa el costo de fabricación en su parte fija y su parte variable.

| Partida | Monto |
|---|---|
| Fruta (frambuesa y frutilla) | 1.860.000 |
| Azúcar | 420.000 |
| Frascos y tapas | 538.000 |
| Pectina (se usa en pequeñas cantidades, no se mide por frasco) | 74.000 |
| Sueldo fijo de las tres operarias de cocina | 1.950.000 |
| Sueldo de la jefa de producción | 980.000 |
| Gas de las ollas | 212.000 |
| Depreciación de ollas y envasadora | 145.000 |
| Arriendo de la planta | 700.000 |
| Detergente y sanitizante de la planta | 58.000 |
| Comisión de la vendedora | 336.000 |
| Contador externo | 250.000 |
| Despacho a clientes | 184.000 |

**9.2 · La cervecería (básico).** Compras netas de materias primas $2.140.000; inventario de materias
primas inicial $310.000 y final $265.000; MOD $1.480.000; CIF $1.395.000; productos en proceso
iniciales $420.000 y finales $515.000; productos terminados iniciales $690.000 y finales $540.000.
Ventas $9.300.000 y gastos de administración y ventas $2.240.000. Calcula materia prima usada, costo
primo, costo de conversión, costo de fabricación, costo de lo producido, costo de ventas, margen bruto
y resultado operacional.

**9.3 · La cocina de almuerzos (básico).** Una cocina arrienda su local en $1.200.000 al mes y cada
almuerzo le cuesta $1.850 en ingredientes y envase. Calcula el costo total, el costo fijo por almuerzo
y el costo total por almuerzo con 800, 1.600 y 2.400 almuerzos al mes. ¿Qué costo por unidad se queda
quieto y cuál se mueve?

**9.4 · El plotter (básico).** Una diseñadora compró hace un año un plotter en $2.600.000 que
deprecia en 48 meses. Hoy un cliente le encarga 40 pendones a $11.500 cada uno; cada pendón usa $4.800
de material y $1.300 de tinta. Si acepta, pierde la tarde, en la que podría hacer un diseño por el que
le pagan $95.000 (no alcanza a hacer los dos). ¿Qué costos son relevantes, cuál es hundido y cuál de
oportunidad? ¿Conviene el encargo y por cuánto?

**9.5 · La lavandería (intermedio).** Kilos lavados y costo de energía de una lavandería industrial:

| Mes | Kilos | Energía |
|---|---|---|
| Enero | 8.400 | 1.052.000 |
| Febrero | 7.100 | 948.000 |
| Marzo | 9.800 | 1.146.000 |
| Abril | 6.300 | 891.200 |
| Mayo | 10.600 | 1.209.400 |
| Junio | 8.900 | 1.088.000 |

Separa la parte fija y la variable con punto alto y punto bajo, y presupuesta la energía de un mes con
9.000 kilos. Compara con la regresión de la planilla.

**9.6 · La mueblería (intermedio).** Inventario de materiales inicial $640.000, compras netas
$3.920.000, inventario final $710.000. De los materiales usados, $330.000 son clavos, cola y lija
(indirectos) y el resto madera (directa). MOD $2.760.000; MOI $1.150.000; otros CIF (energía,
depreciación, arriendo de la planta) $1.290.000. Productos en proceso iniciales $380.000 y finales
$530.000. Se terminaron 200 mesas; había 20 en bodega valorizadas al mismo costo unitario y se
vendieron 190 a $72.000. Gastos de administración y ventas $2.380.000. Arma el estado de costo de lo
producido y vendido y el estado de resultados. Calcula también costo primo y costo de conversión.

**9.7 · La pastelería (intermedio).** Una pastelería vende 1.730 tortas al mes a $14.790. Por torta
gasta $4.270 en ingredientes, $640 en caja, $1.090 en mano de obra a trato y $335 de energía del
horno. Sus costos fijos son $5.882.000 al mes y su capacidad es de 2.260 tortas. Un hotel pide 260
tortas a $8.870, con una decoración que agrega $385 por torta. Calcula el costo completo por torta, el
costo relevante del pedido y su contribución. ¿Acepta? ¿Cuál es el precio mínimo?

**9.8 · Hacer o comprar (intermedio).** Una fábrica de bicicletas hace 1.180 portaequipajes al mes. Por
unidad: material $5.230, mano de obra a trato $2.270, CIF variable $910. Además se le asignan CIF fijos
por $3.658.000 al mes; de ellos, $1.416.000 (el arriendo de una soldadora que se devolvería) se evitan
si deja de fabricarlos. Un proveedor ofrece el portaequipajes a $10.380. (a) ¿Cuál es el costo completo
por unidad? (b) ¿Conviene comprar? (c) ¿Y si el espacio liberado se pudiera arrendar en $1.090.000 al
mes?

**9.9 · El bordado sin capacidad (desafío).** Un taller borda 2.140 poleras al mes, con capacidad para
2.330. Las vende a $12.180 y su costo variable es $7.390. Una empresa pide 470 poleras a $9.460 cada
una, con un hilo especial de $290 por polera, y no acepta entregas parciales. (a) ¿Cuántas ventas
normales desplaza el pedido? (b) ¿Conviene? (c) ¿Cuál es el precio mínimo? (d) ¿Qué ganaría si el
cliente aceptara solo lo que cabe?

**9.10 · El mes de la avería (desafío).** Horas máquina y costo de mantención de un frigorífico:

| Mes | Horas | Mantención |
|---|---|---|
| 1 | 1.090 | 1.268.000 |
| 2 | 1.240 | 1.321.500 |
| 3 | 1.410 | 1.402.800 |
| 4 | 1.170 | 1.293.900 |
| 5 | 1.630 | 1.947.000 |
| 6 | 1.330 | 1.369.200 |
| 7 | 1.470 | 1.417.600 |
| 8 | 1.060 | 1.249.300 |

En el mes 5 se rompió un compresor. (a) Separa fijo y variable con punto alto y punto bajo y
presupuesta 1.500 horas. (b) Haz lo mismo con la regresión de los ocho meses. (c) Repite (a) y (b) sin
el mes 5. (d) ¿Qué presupuesto usarías y por qué?

---

## 9. Pautas

**9.1.**

| Partida | Elemento | Comportamiento |
|---|---|---|
| Fruta, azúcar, frascos y tapas | MPD | variable |
| Pectina | CIF (MPI) | variable |
| Operarias de cocina | MOD | **fijo** (sueldo fijo) |
| Jefa de producción | CIF (MOI) | fijo |
| Gas de las ollas | CIF | variable (o semivariable) |
| Depreciación y arriendo de la planta | CIF | fijo |
| Detergente y sanitizante | CIF | variable |
| Comisión y despacho | gasto de venta | variable |
| Contador | gasto de administración | fijo |

MPD **$2.818.000**; MOD **$1.950.000**; CIF **$2.169.000**; costo de fabricación **$6.937.000**. Costo
primo **$4.768.000**; costo de conversión **$4.119.000**. Gastos del período **$770.000** (no entran al
costo). Del costo de fabricación, $3.775.000 es fijo y $3.162.000 variable. Lectura: más de la mitad del
costo de fabricación no baja si se producen menos frascos.

**9.2.** Materia prima usada: 310.000 + 2.140.000 − 265.000 = **$2.185.000**. Costo primo
**$3.665.000**; conversión **$2.875.000**; costo de fabricación **$5.060.000**. Costo de lo producido:
5.060.000 + 420.000 − 515.000 = **$4.965.000**. Costo de ventas: 4.965.000 + 690.000 − 540.000 =
**$5.115.000**. Margen bruto $4.185.000; resultado operacional **$1.945.000**. Lectura: el costo de ventas
supera al de fabricación porque la bodega de terminados bajó: se vendió algo de lo producido antes.

**9.3.**

| Almuerzos | Costo total | Fijo por almuerzo | Costo total por almuerzo |
|---|---|---|---|
| 800 | 2.680.000 | 1.500 | 3.350 |
| 1.600 | 4.160.000 | 750 | 2.600 |
| 2.400 | 5.640.000 | 500 | 2.350 |

El variable por almuerzo (\$1.850) se queda quieto; el fijo por almuerzo cae a la mitad cuando el volumen
se duplica. Lectura: un costo unitario siempre viene con un volumen; sin él no significa nada.

**9.4.** El plotter es **hundido**: lo que costó (y su depreciación de $54.167 al mes) no cambia se acepte o
no. Relevantes: el ingreso ($460.000), el material y la tinta ($6.100 por pendón) y el diseño que
deja de hacer, que es el **costo de oportunidad** ($95.000). Contribución: (11.500 − 6.100) × 40 =
5.400 × 40 = $216.000. Ventaja del encargo: 216.000 − 95.000 = **$121.000**. Acepta.

**9.5.** Punto alto: mayo (10.600 kg, $1.209.400); bajo: abril (6.300 kg, $891.200).
$b = 318{.}200 / 4{.}300 = 74$ pesos por kilo; $a = 891{.}200 - 74 \times 6{.}300 = 425{.}000$. Para 9.000
kilos: 425.000 + 74 × 9.000 = **$1.091.000**. La regresión da 73,93 por kilo y $426.142 fijos, y un
presupuesto de $1.091.499: casi igual, porque los seis meses caen cerca de una recta. Lectura: la
energía fija de tener la lavandería abierta es $425.000; cada kilo agrega \$74.

**9.6.**

| Cuenta | Pesos |
|---|---|
| Materiales usados: 640.000 + 3.920.000 − 710.000 | 3.850.000 |
| de ellos, madera (MPD) | 3.520.000 |
| MOD | 2.760.000 |
| CIF: 330.000 + 1.150.000 + 1.290.000 | 2.770.000 |
| **Costo de fabricación** | **9.050.000** |
| + 380.000 − 530.000 = **costo de lo producido** (200 mesas a $44.500) | **8.900.000** |
| + terminados iniciales (20 mesas) | + 890.000 |
| − terminados finales (20 + 200 − 190 = 30 mesas) | − 1.335.000 |
| **Costo de ventas** | **8.455.000** |

Ventas: 190 × 72.000 = $13.680.000. Margen bruto $5.225.000; resultado operacional **$2.845.000**. Costo
primo **$6.280.000**; conversión **$5.530.000**. Lectura: los materiales indirectos se compran con la
madera, pero van a CIF; si se dejan en la MPD el costo primo se infla.

**9.7.** Costo variable normal: 4.270 + 640 + 1.090 + 335 = $6.335. Fijo por torta: 5.882.000 / 1.730 =
$3.400. Costo completo: **$9.735**. Costo relevante del pedido: 6.335 + 385 = **$6.720**. Contribución:
(8.870 − 6.720) × 260 = 2.150 × 260 = **$559.000**. Hay 530 tortas de holgura, así que no desplaza
ventas. **Acepta**. Con el costo completo el pedido «perdería» $224.900, pero los $5.882.000 se pagan
igual. Precio mínimo: **$6.720**. Lectura: el pedido no debe vender barato a los clientes de siempre,
que dejan un margen de $8.455 por torta.

**9.8.** (a) Costo completo: 8.410 + 3.100 = **$11.510**: mirado así, comprar a $10.380 parece ahorrar.
(b) Lo que se ahorra dejando de fabricar: el variable (8.410 × 1.180 = $9.923.800) y los fijos
evitables ($1.416.000): **$11.339.800**, o $9.610 por unidad. Comprar cuesta 10.380 × 1.180 =
**$12.248.400**. **Conviene seguir fabricando**: ahorra $908.600 al mes. Los $2.242.000 de fijos
inevitables se pagan en los dos casos. (c) Con el arriendo del espacio, comprar cuesta en neto
12.248.400 − 1.090.000 = $11.158.400, menos que fabricar: ahora **conviene comprar**, por $181.400 al
mes. Lectura: el costo de oportunidad del espacio da vuelta la decisión.

**9.9.** (a) Holgura: 2.330 − 2.140 = 190 poleras. El pedido desplaza 470 − 190 = **280** ventas normales,
que dejan $4.790 de margen cada una. (b) Contribución del pedido: (9.460 − 7.680) × 470 = 1.780 × 470 =
$836.600. Costo de oportunidad: 280 × 4.790 = $1.341.200. Resultado: pierde **$504.600**. **Rechaza.**
(c) Precio mínimo: 7.680 + 1.341.200 / 470 = **$10.534** por polera. (d) Con solo 190 poleras ganaría
$338.200. Lectura: sin capacidad libre, el costo del pedido es el variable más el margen que se deja
de ganar.

**9.10.** (a) Punto alto: mes 5 (1.630 h); bajo: mes 8 (1.060 h). $b$ = 1.224,04 por hora y
$a = -48{.}177$: un costo fijo **negativo**, señal de que un punto está mal. Presupuesto para 1.500 h:
$1.787.875. (b) La regresión de los ocho meses: 971,71 por hora y $145.439 fijos; presupuesto
$1.603.005. Mejor, pero todavía arrastrada por la avería. (c) Sin el mes 5: punto alto y bajo da 410,49
por hora y $814.183 fijos (presupuesto $1.429.915); la regresión da 419,05 por hora y $806.748 fijos
(presupuesto **$1.435.322**). (d) La regresión sin el mes de la avería: usa siete meses normales y no
depende de dos. La avería se presupuesta aparte, como un riesgo. Lectura: un fijo negativo o una
pendiente que se triplica es un aviso de que los datos tienen un mes raro.

---

## 10. Caso integrador · Estampa Sur, qué costo es qué

> El caso sigue el mes de marzo de Estampa Sur por todo el ramo. Las unidades 1 a 8 registraron el
> mes: los 12 asientos, la depreciación de las dos máquinas (unidad 4), el arriendo y el seguro
> devengados (unidad 5), el interés del préstamo (unidad 6) y la tarjeta de las poleras lisas
> (unidad 7). El estado de resultados de la unidad 8 usó costeo por absorción. Aquí se ordenan esos
> costos.

**Pregunta.** ¿Qué es costo del producto y qué es gasto del período? ¿Qué es fijo y qué variable?
¿Cuánto cuesta, en variable, cada prenda, y cuál es el precio mínimo de un pedido especial?

**1 · El costo variable estándar por prenda.** Se mide a precio estándar: prenda lisa según su tipo,
tinta a $16.500 el kilo, y otros insumos variables menores.

| Producto | Prenda lisa | Tinta (g) | Tinta ($) | Otros variables | **Costo variable** | Precio | Margen de contribución |
|---|---|---|---|---|---|---|---|
| Poleras básicas | 2.400 | 12 | 198,0 | 12,0 | **2.610** | 3.990 | 1.380 |
| Polerones | 5.400 | 25 | 412,5 | 137,5 | **5.950** | 9.890 | 3.940 |
| Poleras estampado doble | 3.600 | 22 | 363,0 | 57,0 | **4.020** | 6.290 | 2.270 |
| Bolsas | 1.350 | 8 | 132,0 | 48,0 | **1.530** | 2.490 | 960 |
| Gorros | 1.880 | 6 | 99,0 | 41,0 | **2.020** | 3.190 | 1.170 |

**2 · La clasificación de marzo.**

| Partida | Monto del mes | Producto o período | Directo o indirecto (a la prenda) | Comportamiento |
|---|---|---|---|---|
| Prendas lisas consumidas | 15.533.380 | producto (MPD) | directo | variable |
| Tinta (78,317 kg) | 1.292.230,5 | producto (MPD) | directo | variable |
| Otros variables | 265.759,5 | producto | directo | variable |
| Sueldos de las 4 personas | 2.880.000 | producto | directa por lo que hacen; el caso la trata con los CIF | **fijo** |
| Depreciación: pulpo 102.500 y segunda máquina 208.333 | 310.833 | producto (CIF) | indirecto | fijo |
| Seguro (un mes de 948.000 al año) | 79.000 | producto (CIF) | indirecto | fijo |
| Arriendo de marzo | 580.000 | producto (CIF) | indirecto | fijo |
| Gastos de administración (luz, internet y mantención) | 436.000 | período | no aplica | fijo |
| Interés del préstamo | 73.600 | período (gasto financiero) | no aplica | fijo |

Tres partidas del mes **no son costo de marzo**: la segunda máquina ($14.300.000, inversión; su costo
del mes es la depreciación), el arriendo de abril a junio ($1.740.000, pagado por anticipado) y el IVA
crédito de todas las compras.

**3 · Los totales de fabricación de marzo.**

| Cuenta | Pesos |
|---|---|
| Costo variable de fabricación (5.590 prendas) | 17.091.370 |
| CIF fijos: 2.880.000 + 310.833 + 79.000 + 580.000 | 3.849.833,33 |
| **Costo de lo producido en marzo** | **20.941.203** |
| Gastos de administración (fuera del costo) | 436.000 |

No hay productos en proceso al cierre, así que el costo de fabricación es el costo de lo producido.

**Lectura.** Las cuatro personas que estampan son mano de obra directa por lo que hacen, pero fija por
cómo se pagan: por eso el caso las suma a los CIF fijos, que llegan a $3.849.833 al mes. Cada prenda
deja un margen de contribución (la última columna) que es lo único que mueve la utilidad cuando se
vende una más. Si un cliente pide un lote especial y el taller tiene capacidad libre, el **precio
mínimo** es el costo variable: $2.610 por polera básica, $5.950 por polerón, $4.020 por polera de
estampado doble, $1.530 por bolsa y $2.020 por gorro. Cobrar menos destruye valor; cobrar más suma, aunque
no alcance el costo «completo» que calculará la unidad 11.

**Lo que pasa a la unidad 10.** El costo variable por prenda, los CIF fijos de $3.849.833,33 y los gastos
de administración de $436.000. Allí se decide cuánto de esos CIF fijos queda en la bodega con las 290
prendas que no se vendieron.

---

## 11. Para seguir

**En los libros del ramo.**

- Obligatorios del programa: Gálvez y Clarke, *Contabilidad financiera para la dirección de empresas*,
  Ediciones UC, e Irarrázabal, *Contabilidad: fundamentos y usos*, Ediciones UC, 2014.
- Complementarios: Garrison, Noreen y Brewer, *Contabilidad administrativa*, McGraw-Hill, 2007 (sus
  capítulos sobre conceptos y comportamiento de costos, con punto alto y punto bajo y regresión, y
  sobre costos relevantes para decidir), y Horngren, *Contabilidad de costos*, Pearson, 2012 (la
  terminología de costos y el estado de costo de lo producido).

**Abierto y gratis.**

- OpenStax, *Principles of Accounting, Volume 2: Managerial Accounting* (en inglés, licencia
  CC BY-NC-SA). Capítulo 2: la sección 2.1 (materiales directos, mano de obra directa, CIF y costo de
  lo producido) y la sección 2.3 (punto alto y punto bajo, con la regresión mencionada):
  https://openstax.org/books/principles-managerial-accounting/pages/2-why-it-matters

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame 15 partidas de una fábrica y un pedido
especial; déjame clasificarlas, armar el estado de costo de lo producido y decidir el pedido, y
corrígeme partida por partida».
