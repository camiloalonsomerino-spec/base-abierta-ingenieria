---
ramo: Gestión de Operaciones
unidad: 7
titulo: Programa maestro
version: 0.1 (15-10-2026)
requiere: [06-planeacion-agregada]
alimenta: [08-mrp, 09-capacidad-aproximada, 10-programacion-de-operaciones]
verificacion: verificacion/u07_programa_maestro.py
---

# Unidad 7 · Programa maestro

**Qué vas a poder hacer.** Pasar el plan agregado (familia y mes) a un programa por producto y
semana con el método de corte y ajuste; decidir en qué semanas se lanza un lote; calcular el
balance proyectado disponible con una semana de congelamiento, y responder a ventas cuánto se le
puede prometer a un cliente, semana a semana y en forma acumulada.

**Lo que necesitas antes.** El plan agregado (unidad 6): de ahí sale cuánto fabricar de la familia
cada mes. Basta con saber leer ese plan y repartirlo por porcentajes.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. La idea

El plan agregado dice «6.300 cajas de mermelada en julio». La planta no fabrica «mermelada»: fabrica
frutilla en lotes de 1.750 cajas o mora en lotes de 1.150, y lo hace en una semana precisa. El
**programa maestro de producción** (MPS, por *master production schedule*) es el puente:

- **Desagrega** la familia en productos y el mes en semanas.
- **Respeta** el plan agregado: en el horizonte, lo que programa debe calzar con lo que el plan
  decidió fabricar.
- **No es un pronóstico.** Es una decisión de qué fabricar, cuánto y cuándo. De ahí sale el MRP
  (unidad 8), que calcula los materiales.

| Entradas | Salidas |
|---|---|
| Plan agregado del mes | Lotes por producto y semana (el MPS) |
| Mezcla de productos (%) | Inventario proyectado por producto |
| Inventario inicial de cada producto | Disponible para promesa (DPP) |
| Lotes ya en fabricación (pedidos en curso) | |
| Pronóstico de corto plazo y pedidos firmes | |

### Dónde se programa

- **Fabricación para inventario** (MTS): se programa el producto final. El cliente compra lo que hay.
- **Ensamble a pedido** (ATO): se programan los módulos u opciones, no cada combinación. Una
  bicicleta con 3 marcos y 5 cambios son 15 combinaciones, pero solo 8 programas.
- **Fabricación a pedido** (MTO): se programan los pedidos de los clientes.

### Barreras de tiempo

Las primeras semanas del programa ya tienen material comprado y gente asignada. Por eso se
**congelan**: dentro de la barrera de congelamiento no se cambia el MPS sin autorización y se
planifica solo con pedidos firmes, no con pronósticos. Más allá, el programa todavía se puede
mover.

---

## 2. Corte y ajuste

Con el plan agregado mensual $PA_m$, la fracción $p$ del producto y 4 semanas por mes, las
**necesidades brutas** de cada semana son

$$NB_i = \frac{PA_m \cdot p}{4}$$

Para cada semana $i$ se calculan las **necesidades netas**, descontando el inventario en exceso
que viene de antes ($IE_i$) y el pedido en curso ($PC_i$, que llega en la semana 1):

$$NN_i = NB_i - IE_i - PC_i$$

La regla de decisión, con tamaño de lote $TL$:

| Si | MPS de la semana | Inventario en exceso que pasa a la siguiente |
|---|---|---|
| $NN_i < 0$ | $MPS_i = 0$ | $IE_{i+1} = \lvert NN_i \rvert$ |
| $NN_i \ge 0$ | $MPS_i = k \cdot TL$, con $k = \lceil NN_i / TL \rceil$ (al menos 1) | $IE_{i+1} = MPS_i - NN_i$ |

- $IE_1$ es el inventario inicial del producto. Si no hay, parte en 0.
- El pedido en curso entra solo en la semana 1; después $PC_i = 0$.
- Casi siempre $NN_i \le TL$ y basta un lote. Si las necesidades netas superan el lote, hace falta
  más de uno (ejercicio 7.7). Usar siempre un lote deja el inventario en negativo.
- Si $NN_i$ da exactamente 0, el inventario justo alcanza; la regla igual lanza un lote para no
  terminar la semana en cero.

> **Por qué se llama corte y ajuste.** Se «corta» el plan mensual en semanas y se «ajusta» a lotes
> enteros. El lote casi nunca coincide con la necesidad: lo que sobra pasa como inventario a la
> semana siguiente y evita un lote en ella.

---

## 3. Balance proyectado y disponible para promesa

Cuando el MPS se arma producto por producto con pronóstico y pedidos firmes, se lleva el
**balance proyectado disponible** ($BPD$): lo que quedaría en bodega al cierre de cada semana.

$$BPD_t = BPD_{t-1} + MPS_t - \text{demanda}_t \qquad BPD_0 = \text{inventario inicial}$$

- Dentro de la barrera de congelamiento, la demanda son **solo los pedidos firmes**.
- Después, la demanda es el **mayor** entre el pronóstico y los pedidos: si los pedidos ya superan
  el pronóstico, el pronóstico se quedó corto.
- Si el $BPD$ quedaría bajo cero (o bajo el stock de seguridad), se lanza un lote esa semana.

El **disponible para promesa** ($DPP$) dice cuánto de lo que se va a tener **no está comprometido**
con pedidos. Se calcula en la semana 1 y en cada semana con lote:

$$DPP_1 = I_0 + MPS_1 - \sum (\text{pedidos hasta el próximo lote}) \qquad DPP_t = MPS_t - \sum (\text{pedidos hasta el próximo lote})$$

- En las semanas sin lote el DPP es 0: no entra nada nuevo que prometer.
- Si un DPP sale negativo, los pedidos de ese tramo no caben en su lote y se cubren con lo
  disponible de semanas anteriores: se resta al DPP previo y ese tramo queda en 0.
- El **DPP acumulado** suma los DPP hasta cada semana. Es lo que ventas puede prometer para
  entregar a más tardar esa semana.

---

## 4. Ejemplo resuelto

### A · Mermeladas: del plan agregado al MPS

La fábrica de mermeladas de la unidad 6 eligió el plan mixto: **6.300 cajas en julio y 6.600 en
agosto**. La familia es 60 % frutilla y 40 % mora. Frutilla se fabrica en lotes de 1.750 cajas y
hay 210 en bodega; mora, en lotes de 1.150, con 90 en bodega y un lote de 1.150 en curso que llega
en la semana 1.

**Paso 1 · Necesidades brutas.** Frutilla: $6{.}300 \times 0{,}6 / 4 = 945$ por semana en julio y
$6{.}600 \times 0{,}6 / 4 = 990$ en agosto. Mora: 630 y 660.

**Paso 2 · Frutilla, semana a semana.** Semana 1: $NN_1 = 945 - 210 - 0 = 735 \ge 0$, se lanza un
lote y sobran $1{.}750 - 735 = 1{.}015$. Semana 2: $NN_2 = 945 - 1{.}015 = -70$, no se fabrica y
pasan 70.

| Frutilla | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|
| NB | 945 | 945 | 945 | 945 | 990 | 990 | 990 | 990 |
| IE | 210 | 1.015 | 70 | 875 | 1.680 | 690 | 1.450 | 460 |
| PC | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NN | 735 | −70 | 875 | 70 | −690 | 300 | −460 | 530 |
| MPS | 1.750 | 0 | 1.750 | 1.750 | 0 | 1.750 | 0 | 1.750 |

**Paso 3 · Mora.** El lote en curso cubre la semana 1 y casi toda la 2.

| Mora | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|
| NB | 630 | 630 | 630 | 630 | 660 | 660 | 660 | 660 |
| IE | 90 | 610 | 1.130 | 500 | 1.020 | 360 | 850 | 190 |
| PC | 1.150 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NN | −610 | 20 | −500 | 130 | −360 | 300 | −190 | 470 |
| MPS | 0 | 1.150 | 0 | 1.150 | 0 | 1.150 | 0 | 1.150 |

**Cómo se lee.** El MPS lanza 8.750 cajas de frutilla y 4.600 de mora: 13.350 en lotes, más que las
12.900 del plan. No es un error. El inventario inicial (300) y el lote de mora en curso (1.150)
suman, y los lotes enteros dejan 1.220 cajas de frutilla y 680 de mora para septiembre:
$13{.}350 + 300 + 1{.}150 - 12{.}900 = 1{.}220 + 680$. Fíjate en la semana 2 de mora: faltan solo 20
cajas y se lanza un lote completo de 1.150.

### B · Damasco: MPS con disponible para promesa

La mermelada de damasco se programa aparte, en lotes de 1.000 cajas. Hay 640 en bodega y la
primera semana está congelada.

| Damasco | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|
| Pronóstico | 520 | 540 | 560 | 590 | 570 | 610 | 630 | 600 |
| Pedidos firmes | 610 | 470 | 380 | 240 | 150 | 70 | 30 | 0 |

**Paso 1 · Balance.** Semana 1 (congelada, solo pedidos): $640 - 610 = 30$, alcanza. Semana 2: el
mayor es el pronóstico (540) y $30 - 540 < 0$: se lanza un lote y quedan $30 + 1{.}000 - 540 = 490$.
Semana 3: $490 - 560 < 0$, otro lote, quedan 930.

**Paso 2 · Disponible para promesa.** Semana 1: $640 - 610 = 30$ (el próximo lote llega en la
semana 2). Semana 2: $1{.}000 - 470 = 530$. Semana 3: el próximo lote es en la 5, así que se
descuentan los pedidos de las semanas 3 y 4: $1{.}000 - 380 - 240 = 380$.

| Damasco | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|
| BPD | 30 | 490 | 930 | 340 | 770 | 160 | 530 | 930 |
| MPS | 0 | 1.000 | 1.000 | 0 | 1.000 | 0 | 1.000 | 1.000 |
| DPP | 30 | 530 | 380 | 0 | 780 | 0 | 970 | 1.000 |
| DPP acumulado | 30 | 560 | 940 | 940 | 1.720 | 1.720 | 2.690 | 3.690 |

**Cómo se lee.** Si un supermercado pide 700 cajas para la semana 3, se le pueden prometer: el
acumulado a la semana 3 es 940. Si las pide para la semana 2, no: solo hay 560 sin comprometer. El
BPD usa el pronóstico para decidir los lotes; el DPP usa solo pedidos para no prometer dos veces
la misma caja.

---

## 5. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Repartir el plan del mes sin dividir por 4 | $NB$ es semanal: mes · fracción / 4 |
| Arrastrar el $IE$ con signo negativo | Si $NN < 0$, pasa $\lvert NN \rvert$; si $NN \ge 0$, pasa $MPS - NN$ |
| Restar el pedido en curso todas las semanas | Llega una vez, en la semana 1 |
| Lanzar un solo lote cuando $NN > TL$ | $k = \lceil NN / TL \rceil$ lotes; si no, el inventario queda negativo |
| Usar el pronóstico dentro de la semana congelada | Ahí manda solo lo que ya está pedido |
| Calcular el DPP con el pronóstico | El DPP descuenta solo pedidos firmes |
| Dejar un DPP negativo | Se cubre con el DPP de semanas anteriores y ese tramo queda en 0 |

---

## 6. Práctica

Diez ejercicios: 7.1 a 7.4 básicos, 7.5 a 7.8 intermedios, 7.9 y 7.10 de desafío. Las pautas
están en la sección 7. Intenta cada uno antes de mirarla.

**7.1 · Quesería, necesidades brutas (básico).** Una quesería planifica en hormas. El plan
agregado es de 4.360, 4.920 y 5.240 hormas para los próximos tres meses (4 semanas cada uno). La
mezcla es 50 % gauda, 30 % mantecoso y 20 % chanco. Calcula las necesidades brutas semanales de
cada queso. ¿Cuánto suma una semana del segundo mes?

**7.2 · Molino, corte y ajuste sin inventario (básico).** Un molino planifica sacos de harina:
1.640 en el mes 1 y 1.840 en el mes 2. No hay inventario ni pedidos en curso y el lote es de
1.000 sacos. Arma el MPS de 8 semanas.

**7.3 · Colchones, con inventario y pedido en curso (básico).** Una fábrica de colchones de una
plaza planifica 1.120 en el mes 1 y 1.260 en el mes 2. Tiene 140 en bodega y un lote de 600 en
curso que llega en la semana 1. El lote es de 600. Arma el MPS de 8 semanas.

**7.4 · Estufas compactas, DPP con el programa fijado (básico).** Hay 85 estufas en bodega y el MPS
ya tiene lotes de 200 en las semanas 2, 4 y 6. Calcula el DPP por semana y el acumulado.

| Semana | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Pedidos firmes | 70 | 95 | 60 | 110 | 45 | 30 |

**7.5 · Estufas a pellet, MPS completo con DPP (intermedio).** Lote de 150, 150 estufas en bodega
y una semana de congelamiento. Arma el BPD, el MPS, el DPP por semana y el acumulado. ¿Cuántas
estufas se le pueden prometer a una cadena que pide 70 para la semana 3?

| Semana | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Pronóstico | 60 | 65 | 70 | 80 | 85 | 95 | 100 | 90 | 75 | 70 |
| Pedidos firmes | 72 | 58 | 49 | 41 | 30 | 22 | 15 | 8 | 5 | 0 |

**7.6 · Detergente y suavizante, tres meses (intermedio).** Una planta envasa bidones. El plan
agregado es de 3.280, 3.560 y 3.920 bidones (4 semanas por mes). Detergente (P) es el 55 %, se
fabrica en lotes de 1.000, hay 120 en bodega y un lote de 1.000 en curso. Suavizante (Q) es el
45 %, en lotes de 900, con 440 en bodega. Arma los dos MPS de 12 semanas y compara lo fabricado
cada mes con el plan.

**7.7 · Empanadas congeladas, cuando no alcanza un lote (intermedio).** Una planta de empanadas
congeladas planifica 3.040 cajas en el mes 1 y 3.400 en el mes 2, en lotes de 500, con 300 en
bodega. (a) Aplica la regla de «un lote si $NN \ge 0$» y mira qué pasa con el inventario. (b)
Corrígela con $k = \lceil NN / TL \rceil$.

**7.8 · Kayaks, DPP negativo (intermedio).** Una fábrica de kayaks tiene 40 en bodega y lotes de
120 programados en las semanas 2, 4 y 5. (a) Calcula el DPP y corrige los negativos. (b) Un club
pide 8 kayaks para la semana 4: ¿se pueden prometer?

| Semana | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Pedidos firmes | 35 | 60 | 55 | 90 | 135 | 15 |

**7.9 · Estufas a pellet con stock de seguridad (desafío).** Repite 7.5 exigiendo que el BPD
nunca baje de 30 estufas (la semana 1 sigue congelada y no tiene lote). (a) ¿Qué lotes se mueven?
(b) Mide el inventario extra como la suma de los BPD (unidades-semana). (c) ¿Desde qué stock de
seguridad se mueve otro lote?

**7.10 · Detergente y suavizante, la carga de la envasadora (desafío).** En la envasadora, un lote
de detergente toma 14 horas y uno de suavizante 11. La capacidad es de 20 horas por semana. Con el
MPS de 7.6: (a) calcula la carga de cada semana; (b) nivélala adelantando lotes a la semana previa
más cercana con holgura; (c) mide el costo de nivelar en unidades-semana de inventario extra.

---

## 7. Pautas

**7.1.**

| Queso | Mes 1 | Mes 2 | Mes 3 |
|---|---|---|---|
| Gauda (50 %) | 545 | 615 | 655 |
| Mantecoso (30 %) | 327 | 369 | 393 |
| Chanco (20 %) | 218 | 246 | 262 |

Una semana del mes 2 suma $615 + 369 + 246 = 1{.}230$ hormas, que es $4{.}920 / 4$. Siempre conviene
revisar que las fracciones sumen 100 %.

**7.2.**

| Harina | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|
| NB | 410 | 410 | 410 | 410 | 460 | 460 | 460 | 460 |
| IE | 0 | 590 | 180 | 770 | 360 | 900 | 440 | 980 |
| NN | 410 | −180 | 230 | −360 | 100 | −440 | 20 | −520 |
| MPS | 1.000 | 0 | 1.000 | 0 | 1.000 | 0 | 1.000 | 0 |

Se lanza un lote cada dos semanas. En la semana 7 faltan solo 20 sacos y igual sale un lote
completo: la regla no fracciona.

**7.3.**

| Colchones | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|
| NB | 280 | 280 | 280 | 280 | 315 | 315 | 315 | 315 |
| IE | 140 | 460 | 180 | 500 | 220 | 505 | 190 | 475 |
| PC | 600 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NN | −460 | −180 | 100 | −220 | 95 | −190 | 125 | −160 |
| MPS | 0 | 0 | 600 | 0 | 600 | 0 | 600 | 0 |

El inventario y el lote en curso cubren las dos primeras semanas; desde ahí, un lote cada dos.

**7.4.** Semana 1: $85 - 70 = 15$. Semana 2: $200 - 95 - 60 = 45$. Semana 4: $200 - 110 - 45 = 45$.
Semana 6: $200 - 30 = 170$.

| Semana | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| DPP | 15 | 45 | 0 | 45 | 0 | 170 |
| DPP acumulado | 15 | 60 | 60 | 105 | 105 | 275 |

**7.5.**

| Pellet | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 |
|---|---|---|---|---|---|---|---|---|---|---|
| BPD | 78 | 13 | 93 | 13 | 78 | 133 | 33 | 93 | 18 | 98 |
| MPS | 0 | 0 | 150 | 0 | 150 | 150 | 0 | 150 | 0 | 150 |
| DPP | 20 | 0 | 60 | 0 | 120 | 113 | 0 | 137 | 0 | 150 |
| DPP acum. | 20 | 20 | 80 | 80 | 200 | 313 | 313 | 450 | 450 | 600 |

Semana 1 (congelada): $150 - 72 = 78$. Semana 2: el pronóstico (65) manda y quedan 13. El DPP de
la semana 1 descuenta los pedidos de las semanas 1 y 2, porque el primer lote llega en la 3:
$150 - 72 - 58 = 20$. A la cadena se le pueden prometer las 70 para la semana 3: el acumulado es
80. El BPD suma 650 unidades-semana.

**7.6.** Detergente (P):

| P | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 | S11 | S12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NB | 451 | 451 | 451 | 451 | 489,5 | 489,5 | 489,5 | 489,5 | 539 | 539 | 539 | 539 |
| IE | 120 | 669 | 218 | 767 | 316 | 826,5 | 337 | 847,5 | 358 | 819 | 280 | 741 |
| NN | −669 | −218 | 233 | −316 | 173,5 | −337 | 152,5 | −358 | 181 | −280 | 259 | −202 |
| MPS | 0 | 0 | 1.000 | 0 | 1.000 | 0 | 1.000 | 0 | 1.000 | 0 | 1.000 | 0 |

Suavizante (Q):

| Q | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 | S11 | S12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NB | 369 | 369 | 369 | 369 | 400,5 | 400,5 | 400,5 | 400,5 | 441 | 441 | 441 | 441 |
| IE | 440 | 71 | 602 | 233 | 764 | 363,5 | 863 | 462,5 | 62 | 521 | 80 | 539 |
| NN | −71 | 298 | −233 | 136 | −363,5 | 37 | −462,5 | −62 | 379 | −80 | 361 | −98 |
| MPS | 0 | 900 | 0 | 900 | 0 | 900 | 0 | 0 | 900 | 0 | 900 | 0 |

Fabricado por mes: P, 1.000 · 2.000 · 2.000; Q, 1.800 · 900 · 1.800. El plan pedía 1.804, 1.958 y
2.156 de P, y 1.476, 1.602 y 1.764 de Q. El mes 1 de P fabrica poco porque el lote en curso ya
cubre casi todo; el mes 2 de Q, porque lo que sobró del lote de la semana 6 cubre las semanas 7 y 8. Mes a mes el
MPS no calza con el plan; en el horizonte sí, salvo el inventario que queda al final.

**7.7.** (a) Con un solo lote por semana:

| Empanadas | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|
| IE | 300 | 40 | −220 | −480 | −740 | −1.090 | −1.440 | −1.790 |

Desde la semana 3 el «inventario en exceso» es negativo: faltan empanadas y la falta crece. Un lote
de 500 no alcanza para una semana de 760. (b) Con $k = \lceil NN / TL \rceil$:

| Empanadas | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|
| NB | 760 | 760 | 760 | 760 | 850 | 850 | 850 | 850 |
| IE | 300 | 40 | 280 | 20 | 260 | 410 | 60 | 210 |
| NN | 460 | 720 | 480 | 740 | 590 | 440 | 790 | 640 |
| MPS | 500 | 1.000 | 500 | 1.000 | 1.000 | 500 | 1.000 | 1.000 |

Con lotes más chicos que la necesidad semanal, se fabrica todas las semanas y a veces dos lotes.
La señal para la gerencia: el lote está mal elegido para esta demanda.

**7.8.** (a) Primer cálculo: semana 1, $40 - 35 = 5$; semana 2, $120 - 60 - 55 = 5$; semana 4,
$120 - 90 = 30$; semana 5, $120 - 135 - 15 = -30$.

| Kayaks | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| DPP antes de corregir | 5 | 5 | 0 | 30 | −30 | 0 |
| DPP corregido | 5 | 5 | 0 | 0 | 0 | 0 |
| DPP acumulado | 5 | 10 | 10 | 10 | 10 | 10 |

Los pedidos de la semana 5 se comen su lote y 30 kayaks del lote de la semana 4. (b) Sí: el
acumulado a la semana 4 es 10 y el club pide 8. Pero después de esa promesa solo quedan 2 kayaks
libres en todo el horizonte; cualquier pedido nuevo necesita otro lote.

**7.9.** (a) Con stock de seguridad de 30:

| Pellet | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 |
|---|---|---|---|---|---|---|---|---|---|---|
| BPD | 78 | 163 | 93 | 163 | 78 | 133 | 33 | 93 | 168 | 98 |
| MPS | 0 | 150 | 0 | 150 | 0 | 150 | 0 | 150 | 150 | 0 |
| DPP | 78 | 43 | 0 | 79 | 0 | 113 | 0 | 142 | 145 | 0 |
| DPP acum. | 78 | 121 | 121 | 200 | 200 | 313 | 313 | 455 | 600 | 600 |

Los lotes de las semanas 3, 5 y 10 se adelantan una semana (a la 2, 4 y 9); el de la 6 y el de
la 8 se quedan. El número de lotes no cambia: cambia cuándo llegan. (b) El BPD pasa de
650 unidades-semana a 1.100 unidades-semana: son 450 unidades-semana más de inventario para
tener 30 estufas de colchón. (c) Con un stock de seguridad de 34 o más, el BPD de la semana 7 (33)
queda corto y el lote de la semana 8 se adelanta a la 7; el MPS pasa a
0 | 150 | 0 | 150 | 0 | 150 | 150 | 0 | 150 | 0.

**7.10.** (a) Carga semanal en horas:

| Semana | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Original | 0 | 11 | 14 | 11 | 14 | 11 | 14 | 0 | 25 | 0 | 25 | 0 |
| Nivelada | 0 | 11 | 14 | 11 | 14 | 11 | 14 | 11 | 14 | 11 | 14 | 0 |

Las semanas 9 y 11 piden 25 horas y hay 20. (b) Se adelanta el lote de suavizante de la semana 9 a
la 8 y el de la 11 a la 10: el lote más corto es el que cabe en la holgura. (c) Cada lote de 900
bidones se guarda una semana más: 1.800 unidades-semana de inventario extra. Es el precio de no
pagar horas extra en la envasadora. La unidad 9 hace este mismo análisis para toda la planta.

---

## 8. Caso integrador · Estampa Sur, los lotes de las primeras 8 semanas

> Este caso sigue a Estampa Sur por todo el ramo. Cada unidad parte de lo que calculó la anterior;
> acá se usa el plan agregado de la unidad 6. Si no has hecho esa unidad, parte de esta tabla.

El plan agregado fija **5.590 prendas en el mes 1 y 6.080 en el mes 2**. La familia se reparte así:

| Producto | Mezcla | Lote | En bodega | En curso (S1) | NB S1 a S4 | NB S5 a S8 |
|---|---|---|---|---|---|---|
| Poleras básicas | 40 % | 720 | 80 | 720 | 559 | 608 |
| Polerones | 15 % | 360 | 120 | 0 | 209,625 | 228 |
| Poleras estampado doble | 15 % | 360 | 0 | 360 | 209,625 | 228 |
| Bolsas | 18 % | 540 | 260 | 0 | 251,55 | 273,6 |
| Gorros | 12 % | 480 | 50 | 480 | 167,7 | 182,4 |

> **Un solo inventario.** Lo que hay en bodega suma $80 + 120 + 0 + 260 + 50 = 510$ prendas: es el
> mismo inventario inicial con que partió el plan agregado de la unidad 6, ahora abierto por
> producto. Si el plan partiera con una cifra y el programa maestro con otra, uno de los dos estaría
> contando prendas que no existen. Antes de armar el MPS, se revisa que las dos cifras calcen.

**Pregunta 1.** Arma el MPS de las 8 semanas con corte y ajuste.

**Desarrollo.** Poleras básicas, completo:

| Poleras básicas | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|
| NB | 559 | 559 | 559 | 559 | 608 | 608 | 608 | 608 |
| IE | 80 | 241 | 402 | 563 | 4 | 116 | 228 | 340 |
| PC | 720 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NN | −241 | 318 | 157 | −4 | 604 | 492 | 380 | 268 |
| MPS | 0 | 720 | 720 | 0 | 720 | 720 | 720 | 720 |

Los otros cuatro productos (las necesidades fraccionarias se arrastran tal cual; se redondea solo
el lote):

| Polerones | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|
| IE | 120 | 270,375 | 60,75 | 211,125 | 1,5 | 133,5 | 265,5 | 37,5 |
| NN | 89,625 | −60,75 | 148,875 | −1,5 | 226,5 | 94,5 | −37,5 | 190,5 |
| MPS | 360 | 0 | 360 | 0 | 360 | 360 | 0 | 360 |

| Estampado doble | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|
| IE | 0 | 150,375 | 300,75 | 91,125 | 241,5 | 13,5 | 145,5 | 277,5 |
| NN | −150,375 | 59,25 | −91,125 | 118,5 | −13,5 | 214,5 | 82,5 | −49,5 |
| MPS | 0 | 360 | 0 | 360 | 0 | 360 | 360 | 0 |

| Bolsas | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|
| IE | 260 | 8,45 | 296,9 | 45,35 | 333,8 | 60,2 | 326,6 | 53 |
| NN | −8,45 | 243,1 | −45,35 | 206,2 | −60,2 | 213,4 | −53 | 220,6 |
| MPS | 0 | 540 | 0 | 540 | 0 | 540 | 0 | 540 |

| Gorros | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|
| IE | 50 | 362,3 | 194,6 | 26,9 | 339,2 | 156,8 | 454,4 | 272 |
| NN | −362,3 | −194,6 | −26,9 | 140,8 | −156,8 | 25,6 | −272 | −89,6 |
| MPS | 0 | 0 | 0 | 480 | 0 | 480 | 0 | 0 |

El MPS de la familia, en prendas:

| | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | Total |
|---|---|---|---|---|---|---|---|---|---|
| Poleras básicas | 0 | 720 | 720 | 0 | 720 | 720 | 720 | 720 | 4.320 |
| Polerones | 360 | 0 | 360 | 0 | 360 | 360 | 0 | 360 | 1.800 |
| Estampado doble | 0 | 360 | 0 | 360 | 0 | 360 | 360 | 0 | 1.440 |
| Bolsas | 0 | 540 | 0 | 540 | 0 | 540 | 0 | 540 | 2.160 |
| Gorros | 0 | 0 | 0 | 480 | 0 | 480 | 0 | 0 | 960 |
| **Semana** | 360 | 1.620 | 1.080 | 1.380 | 1.080 | 2.460 | 1.080 | 1.620 | |

**Lectura.** La semana 1 casi no fabrica: el inventario y los tres lotes en curso la cubren. La
**semana 6 tiene un lote de cada producto** (2.460 prendas, 33 horas de estampado) y es la más
cargada del horizonte. Ese es el programa que la unidad 10 secuencia. Antes, la unidad 9 revisará
si esas horas caben en la capacidad del estampado.

**Pregunta 2.** Ventas ya comprometió estas poleras básicas. Un club pide 400 para la semana 4:
¿se pueden prometer?

| Semana | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Pedidos firmes | 540 | 610 | 480 | 300 | 150 | 80 | 0 | 0 |

**Desarrollo.** En la semana 1 hay $80 + 720 = 800$ (bodega más lote en curso) y el próximo lote
llega en la 2: $800 - 540 = 260$. Semana 2: $720 - 610 = 110$. Semana 3 (el siguiente lote es en
la 5): $720 - 480 - 300 = -60$, que se cubre con el DPP de la semana 2.

| Poleras básicas | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| DPP antes de corregir | 260 | 110 | −60 | 0 | 570 | 640 | 720 | 720 |
| DPP corregido | 260 | 50 | 0 | 0 | 570 | 640 | 720 | 720 |
| DPP acumulado | 260 | 310 | 310 | 310 | 880 | 1.520 | 2.240 | 2.960 |

**Lectura.** No para la semana 4: hasta ahí solo hay 310 poleras sin comprometer. Sí para la
semana 5, cuando el acumulado sube a 880. La respuesta a ventas es «310 en la semana 4 y el resto en
la 5», o las 400 completas en la semana 5. Lo que no se hace es prometer las 400 y quitárselas a un
pedido que ya estaba firme.

**Lo que pasa a la unidad 8.** Los lotes de poleras básicas (720 en las semanas 2, 3, 5, 6, 7 y 8)
son las necesidades brutas de poleras lisas, tinta y etiquetas que explota el MRP.

---

## 9. Para seguir

**En los libros del ramo.**

- Schroeder, *Administración de operaciones* (2.ª ed., 2004), capítulos 12, 13 y 16 (los que fija el
  programa para la planificación y el control de la producción).
- Chase, Jacobs y Aquilano, *Administración de operaciones* (12.ª ed., 2009), capítulo de
  planeación de requerimientos de materiales: programa maestro, barreras de tiempo y disponible
  para promesa.
- Heizer y Render, *Principios de administración de operaciones* (5.ª ed., 2004), capítulo de
  planeación agregada (paso al programa maestro) y capítulo de MRP.

**Abiertos y gratis.**

- Abbas y Goosheh, *Operations Management*, Fanshawe College (2025), en inglés, capítulos de
  planeación agregada y de MRP (master production schedule). Descarga en la colección abierta de
  Ontario: https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/2473

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un MPS de dos productos con un DPP que
salga negativo y corrígeme semana a semana».
