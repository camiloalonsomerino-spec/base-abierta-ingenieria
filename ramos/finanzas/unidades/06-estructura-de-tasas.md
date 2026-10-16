---
ramo: Finanzas
unidad: 6
titulo: Estructura de tasas
version: 0.1 (15-10-2026)
requiere: [01-valor-del-dinero, 02-tasas-de-interes, 05-van-y-tir]
alimenta: [07-bonos, 08-duracion-e-inmunizacion, 11-portafolios]
verificacion: verificacion/u06_estructura_de_tasas.py
---

# Unidad 6 · Estructura de tasas

**Qué vas a poder hacer.** Sacar la tasa spot de cada plazo desde los precios de bonos cero cupón;
calcular las tasas forward implícitas y explicar por qué no son un pronóstico garantizado;
construir la curva desde bonos con cupón (bootstrapping); valorar un bono descontando cada flujo
a su propia tasa; reconocer una curva normal, plana o invertida, y explicar su forma con las tres
teorías (expectativas, preferencia por liquidez y segmentación).

**Lo que necesitas antes.** Traer un monto al presente con una tasa compuesta (unidad 1), la
equivalencia de tasas (unidad 2) y la TIR (unidad 5), porque la tasa de un bono es su TIR.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. La idea

Hasta ahora todo se descontó con **una** tasa. Pero el mercado no paga lo mismo por prestar un año
que por prestar cinco: cada plazo tiene su precio. La **estructura de tasas** (o estructura
temporal, o curva de rendimiento) es la lista de tasas de un mismo emisor ordenadas por plazo.

Para que la curva hable solo del plazo, todos los instrumentos tienen que tener **el mismo riesgo
de crédito**. Por eso se arma con bonos del Estado (en esta unidad, de una Tesorería ficticia): así
la diferencia entre la tasa a 1 año y la tasa a 5 años no se mezcla con la posibilidad de que el
emisor no pague.

---

## 2. Bonos cero cupón y tasa spot

Un **bono cero cupón** no paga nada en el camino: paga solo el nominal al vencimiento. Se compra
bajo la par y la diferencia es el interés. Como tiene un solo flujo, su tasa no tiene ambigüedad:

$$P_t = \frac{100}{(1+s_t)^t} \qquad\Longleftrightarrow\qquad s_t = \left(\frac{100}{P_t}\right)^{1/t} - 1$$

$s_t$ es la **tasa spot** a $t$ años: la tasa anual compuesta que se gana hoy, de una vez, entre
hoy y el año $t$. El cociente $P_t/100$ es el **factor de descuento** del año $t$: lo que vale hoy un
peso que llega en $t$ con certeza.

---

## 3. Tasas forward implícitas

Hay dos formas de colocar plata dos años:

- Comprar un cero a 2 años: un peso se convierte en $(1+s_2)^2$.
- Comprar un cero a 1 año y, al vencer, colocar todo otro año a la tasa que se pacte hoy para ese
  segundo año, $f_{1,2}$: un peso se convierte en $(1+s_1)(1+f_{1,2})$.

Si las dos dieran distinto, todos harían la mejor y nadie la otra. Por **no arbitraje** deben dar
lo mismo:

$$(1+s_2)^2 = (1+s_1)(1+f_{1,2}) \qquad\Longrightarrow\qquad f_{1,2} = \frac{(1+s_2)^2}{1+s_1} - 1$$

En general, la forward entre los años $a$ y $b$ (anual) es

$$(1+f_{a,b})^{\,b-a} = \frac{(1+s_b)^b}{(1+s_a)^a}$$

**Cómo se lee.** La forward es la tasa que el mercado ya deja **fijada hoy** para un préstamo que
empezará en el futuro. No es un pronóstico garantizado: es lo que hay que ganar en el tramo futuro
para que esperar y renovar dé lo mismo que colocar largo de una vez. Que coincida o no con la tasa
que de verdad habrá es lo que discuten las teorías de la sección 7.

**Spot y forward son promedio y marginal.** La spot a $t$ años es el promedio geométrico de las
forwards de cada año hasta $t$:

$$(1+s_3)^3 = (1+s_1)(1+f_{1,2})(1+f_{2,3})$$

Como con las notas de un ramo: si la nota nueva (la forward) es mayor que el promedio (la spot), el
promedio sube. Por eso, **cuando la curva spot sube, cada forward está sobre la spot de su plazo**;
cuando baja, bajo ella.

---

## 4. Valorar un bono con la curva

Un bono con cupones es un paquete de ceros: cada cupón es un cero a su plazo. Cada flujo se
descuenta **con la spot de su fecha**:

$$P = \sum_{t=1}^{n} \frac{F_t}{(1+s_t)^t}$$

La TIR del bono (su *yield to maturity*, YTM) es la tasa **única** que da ese mismo precio. Es una
especie de promedio de las spots, ponderado por el peso de cada flujo; como el nominal llega al
final, queda cerca de la spot más larga. Por eso descontar un bono con una sola tasa (aunque sea
la del plazo final) da un precio apenas distinto: no es lo mismo, y en un arbitraje esa diferencia
es plata (ejercicio 6.9).

---

## 5. Bootstrapping: la curva desde bonos con cupón

En la práctica hay pocos ceros y muchos bonos con cupón. La curva se saca **de a un plazo**:

1. Con el instrumento a 1 año se obtiene $s_1$ (si es un bono con cupón a un año, igual tiene un
   solo flujo).
2. Al bono a 2 años se le resta el valor presente de su primer cupón, descontado con $s_1$. Lo que
   queda del precio corresponde solo al flujo final, y de ahí sale $s_2$.
3. Al bono a 3 años se le restan sus cupones 1 y 2 (con $s_1$ y $s_2$), y de lo que queda sale $s_3$.
   Y así.

$$s_t = \left(\frac{100 + C_t}{P_t - \sum_{k=1}^{t-1} \dfrac{C_t}{(1+s_k)^k}}\right)^{1/t} - 1$$

El nombre viene de levantarse tirando de los cordones de las propias botas: cada tasa se apoya en
las que ya se calcularon.

---

## 6. Formas de la curva

| Forma | Cómo se ve | Qué suele acompañarla |
|---|---|---|
| **Normal** | sube con el plazo | la más frecuente; prestar más largo se paga más |
| **Plana** | casi igual en todos los plazos | transición entre una forma y otra |
| **Invertida** | baja con el plazo | el mercado espera que las tasas cortas bajen (por ejemplo, porque espera menos actividad y un banco central que recorte) |
| **Jorobada** | sube y después baja | expectativas que cambian de dirección en el tiempo |

Esta unidad usa curvas inventadas. Para mirar la curva real de un país hay que ir a los datos del
banco central o de la bolsa de esa fecha; ninguna cifra de esta unidad la describe.

---

## 7. Las tres teorías

¿Por qué la curva tiene la forma que tiene?

**Expectativas (puras).** Los inversionistas solo miran el retorno esperado y les da igual el
plazo. Entonces el arbitraje deja cada forward **igual a la tasa corta que se espera** para ese año.
Curva que sube = el mercado espera alzas; curva invertida = espera bajas. *Lo que no explica:* por
qué la curva normal es la más frecuente, si las tasas no suben siempre.

**Preferencia por liquidez.** Prestar largo es más riesgoso: si las tasas suben, el bono largo
pierde más precio (lo mide la duración, unidad 8). Para aceptar ese riesgo, el inversionista pide
un **premio** que crece con el plazo:

$$f_{t-1,t} = E[\text{tasa corta del año } t] + \text{premio}_t$$

Así, una curva puede subir **aunque nadie espere alzas**: la sube el premio. Explica bien por qué la
forma normal es la más común.

**Segmentación de mercados.** Cada plazo es un mercado aparte, con sus propios compradores: los
bancos y tesorerías de empresas viven en el corto plazo; las aseguradoras de vida y los fondos de
pensiones necesitan el largo para calzar pagos lejanos. La tasa de cada tramo la fija su propia
oferta y demanda. Si muchos fondos de pensiones compran bonos largos, la tasa larga baja aunque nada
haya cambiado en las expectativas. *Una versión intermedia* (hábitat preferido) dice que cada
inversionista tiene su plazo favorito, pero se cambia si le pagan lo suficiente.

> **Para un comente.** Las tres no se excluyen: la curva real tiene algo de expectativas, algo de
> premio y algo de presión de cada tramo. Lo que se pide es saber qué diría cada una de una misma
> curva.

---

## 8. Ejemplo resuelto · la matrícula del hermano de Tomás

Tomás tiene **$10.000.000** que necesitará en exactamente 2 años para pagar la matrícula de su
hermano. Su banco le ofrece un depósito a 2 años al **4,7 %** anual. En el mercado se transan, por
cada 100 de nominal:

| Instrumento | Plazo | Cupón anual | Precio |
|---|---|---|---|
| Cero cupón | 1 año | 0 | 95,85 |
| Bono con cupón | 2 años | 5 % (paga 5 al año) | 100,21 |

**Paso 1 · Spot a 1 año.** $s_1 = 100/95{,}85 - 1 =$ **4,33 %**.

**Paso 2 · Spot a 2 años por bootstrapping.** El primer cupón del bono es un cero a 1 año:

$$\frac{5}{1{,}0433} = 4{,}7925$$

Su valor presente es 4,7925. Lo que queda del precio, $100{,}21 - 4{,}7925 = 95{,}4175$, paga el flujo final de 105:

$$95{,}4175 = \frac{105}{(1+s_2)^2} \quad\Longrightarrow\quad s_2 = \left(\frac{105}{95{,}4175}\right)^{1/2} - 1 = 4{,}90\ \%$$

La spot a 2 años es **4,90 %**. Un cero a 2 años valdría hoy 90,87. Fíjate que la TIR del bono con
cupón (4,89 %) queda apenas bajo $s_2$: su cupón del año 1 se descuenta a la tasa más baja del
primer año.

**Paso 3 · Forward del segundo año.**

$$f_{1,2} = \frac{1{,}0490^2}{1{,}0433} - 1 = 5{,}48\ \%$$

La forward es **5,48 %**, mayor que las dos spots: la curva sube y la marginal arrastra el
promedio.

**Paso 4 · Decidir.**

| Estrategia | Lo que junta en 2 años |
|---|---|
| Depósito del banco a 2 años al 4,7 % | $10.962.090 |
| Colocar a la spot de 2 años (4,90 %) | $11.004.271 |
| Colocar 1 año a la spot (4,33 %) y renovar | $10.432.968 al año 1, y después depende de la tasa del año 2 |

**Cómo se lee.** El banco le paga menos que el mercado a 2 años: la diferencia es $42.181. Si
Tomás coloca solo un año y renueva, le conviene únicamente si la tasa a un año, dentro de un año,
supera **5,48 %** (la forward). Bajo esa tasa, colocar largo de una vez gana. Como Tomás necesita la
plata en una fecha fija, colocar a 2 años le elimina el riesgo de renovar a una tasa peor.

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Sacar la spot de un cero como $(100 - P)/P$ sin la raíz | Es una tasa anual compuesta: eleva a $1/t$ |
| Calcular la forward como resta de spots ($s_2 - s_1$) | Se divide capitalizaciones: $(1+s_2)^2/(1+s_1) - 1$ |
| Leer la forward como la tasa que habrá con seguridad | Es la tasa de equilibrio de hoy; bajo preferencia por liquidez trae un premio |
| En bootstrapping, descontar los cupones con la tasa del bono | Cada cupón con la spot de su fecha, ya calculada |
| Valorar un bono con una sola tasa cuando hay curva | Cada flujo con su spot; la YTM sale después |
| Mezclar emisores distintos en una misma curva | La curva es de un mismo riesgo de crédito; si no, la diferencia mezcla plazo y riesgo |
| Decir que curva normal «prueba» que vienen alzas | Solo bajo expectativas puras; el premio por liquidez también la sube |

---

## 10. Práctica

Diez ejercicios: 6.1 a 6.4 básicos, 6.5 a 6.8 intermedios, 6.9 y 6.10 de desafío. Dos son
**comentes** (6.3 y 6.8): responde Verdadero, Falso o Incierto y **argumenta**. Todos los precios
son por cada 100 de nominal y los cupones son anuales. Las pautas están en la sección 11.

**6.1 · Ceros de la Tesorería (básico).** Los ceros a 1, 2 y 3 años se transan a 96,30, 92,10 y 87,60.
(a) Calcula las spots y di qué forma tiene la curva. (b) ¿Cuánto vale hoy un pagaré sin riesgo que
paga $5.000.000 en 3 años?

**6.2 · Forwards desde spots (básico).** Las spots a 1, 2 y 3 años son 3,6 %, 4,1 % y 4,5 %. Calcula
$f_{1,2}$, $f_{2,3}$ y la tasa anual a dos años que empieza en un año, $f_{1,3}$. Comprueba que
$(1+s_3)^3 = (1+s_1)(1+f_{1,2})(1+f_{2,3})$.

**6.3 · Comente (básico).** «Si la curva spot tiene pendiente positiva, es porque el mercado espera
que las tasas de corto plazo suban.»

**6.4 · Un bono con la curva (básico).** Con las spots de 6.2, valora un bono a 3 años con cupón 7 %.
Calcula su TIR. ¿Qué precio darías si lo descontaras entero a la spot de 3 años? ¿Por qué no es lo
mismo?

**6.5 · Bootstrapping (intermedio).** Se transan tres bonos del Estado:

| Plazo | Cupón | Precio |
|---|---|---|
| 1 año | 5 % | 100,48 |
| 2 años | 5,5 % | 100,62 |
| 3 años | 6 % | 100,85 |

Construye la curva spot y calcula las forwards $f_{1,2}$ y $f_{2,3}$.

**6.6 · Fijar hoy la tasa del próximo año (intermedio).** La tesorera de una cooperativa recibirá
$40.000.000 en un año y los quiere colocar un año más. Su banco le ofrece fijar hoy esa colocación
al 5,3 %. Las spots son 4,2 % a un año y 4,9 % a dos años, y la cooperativa puede pedir y prestar a
esas tasas. (a) Calcula la forward. (b) Arma con ceros una estrategia que fije hoy la tasa
implícita y compara lo que junta al año 2 con la oferta del banco. (c) ¿Qué supuestos hacen falta?

**6.7 · Expectativas con premio (intermedio).** Las spots a 1, 2, 3 y 4 años son 4,4 %, 4,75 %, 4,95 %
y 5,05 %. (a) Calcula las forwards de un año. (b) Bajo expectativas puras, ¿qué tasas cortas espera
el mercado? (c) Si hay un premio por liquidez de 0,2 puntos porcentuales por cada año de plazo
sobre el primero (0,2 en el año 2; 0,4 en el 3; 0,6 en el 4), ¿qué tasas cortas espera ahora? ¿Qué
cambia en la lectura de una misma curva?

**6.8 · Comente (intermedio).** «Cuando la curva está invertida, lo racional es invertir solo a corto
plazo: el corto plazo paga más.»

**6.9 · Un bono mal valorado (desafío).** Con estos tres bonos se arma la curva:

| Bono | Plazo | Cupón | Precio |
|---|---|---|---|
| A | 1 año | 4 % | 99,61 |
| B | 2 años | 5 % | 100,10 |
| C | 3 años | 5,5 % | 100,05 |

Un cuarto bono del mismo emisor, D, a 3 años con cupón 8 %, se transa a 107,90. (a) Construye la
curva y calcula el precio de D según ella. (b) Arma una cartera de A, B y C que replique exactamente
los flujos de D (cuántas unidades de cada uno). (c) ¿Qué estrategia aprovecha la diferencia y
cuánto gana por cada bono D? (d) Compara la TIR de D a su precio de mercado con la que tendría a su
precio teórico.

**6.10 · Tres caminos para el pie (desafío).** Una pareja tiene $12.000.000 para el pie de un
departamento que comprará en 3 años. Las spots a 1, 2 y 3 años son 4,6 %, 5,0 % y 5,3 %.
Estrategias: (A) un cero a 3 años; (B) uno a 1 año, renovando cada año; (C) uno a 2 años y después
uno a 1 año. (a) Calcula $f_{1,2}$ y $f_{2,3}$ y muestra que, si las tasas futuras son iguales a las
forwards, A y B juntan lo mismo. (b) Si las tasas a un año que de verdad se dan son 5,0 % en el año 2
y 5,2 % en el año 3, ¿cuánto junta cada estrategia? (c) Dado que el año 2 salió a 5,0 %, ¿qué tasa
del año 3 habría hecho que B empatara con A? (d) Bajo preferencia por liquidez, ¿qué estrategia
conviene en promedio a esta pareja y por qué no corre riesgo de precio con ella?

---

## 11. Pautas

**6.1.** (a) $s_1 = 100/96{,}30 - 1 =$ 3,84 % · $s_2 = (100/92{,}10)^{1/2} - 1 =$ 4,20 % ·
$s_3 = (100/87{,}60)^{1/3} - 1 =$ 4,51 %. Curva **normal**: sube con el plazo. (b) El factor de descuento a
3 años es 0,876: el pagaré vale **$4.380.000**. No hace falta la tasa: el precio del cero ya es el
factor.

**6.2.** $f_{1,2} = 1{,}041^2/1{,}036 - 1 =$ **4,60 %** · $f_{2,3} = 1{,}045^3/1{,}041^2 - 1 =$ **5,30 %** ·
$f_{1,3} = (1{,}045^3/1{,}036)^{1/2} - 1 =$ **4,95 %**. Comprobación: $1{,}036 \times 1{,}0460 \times 1{,}0530 \approx 1{,}045^3$.
Cada forward queda sobre la spot de su plazo porque la curva sube.

**6.3.** **Incierto: depende de la teoría.** Bajo **expectativas puras** es verdadero: cada forward es
la tasa corta esperada, y si la curva sube, las forwards suben. Bajo **preferencia por liquidez** no
necesariamente: la forward es la tasa esperada **más un premio** que crece con el plazo, así que la
curva puede subir con tasas esperadas planas o incluso a la baja (el ejercicio 6.7 lo muestra con
números). Bajo **segmentación**, la pendiente refleja la oferta y la demanda de cada tramo (por
ejemplo, poca demanda por bonos largos) y no dice nada de expectativas. Como la curva normal es la
más frecuente y las tasas no suben siempre, la evidencia apoya que hay premio: la afirmación es
demasiado fuerte.

**6.4.** Valores presentes de los flujos: 6,76 + 6,46 + 93,76 = **106,98**. Su TIR es **4,46 %**: queda
cerca de la spot a 3 años (4,5 %) porque el flujo final pesa casi todo. Descontado entero al 4,5 %
daría 106,87: los cupones de los años 1 y 2 se castigarían con una tasa más alta que la suya. La
diferencia es chica en un bono, pero no es cero, y en una cartera grande es plata.

**6.5.** $s_1 = 105/100{,}48 - 1 =$ **4,50 %**. Para el año 2: $100{,}62 - 5{,}5/1{,}045$ paga 105,5 en el año 2,
de donde $s_2 =$ **5,18 %**. Para el año 3: se restan los cupones de 6 descontados con $s_1$ y $s_2$, y
$s_3 =$ **5,73 %**. Forwards: $f_{1,2} =$ **5,87 %** y $f_{2,3} =$ **6,83 %**. Curva normal y empinada.

**6.6.** (a) $f_{1,2} = 1{,}049^2/1{,}042 - 1 =$ **5,605 %**. (b) Hoy pide prestado a un año lo que valen hoy
los 40 millones (divididos por 1,042): $38.387.716. Lo devolverá exactamente con los $40.000.000
que recibe en un año. Con ese préstamo compra hoy un cero a 2 años, que al año 2 le entrega
$38.387.716 × 1,049² = **$42.241.881**. Con el banco juntaría $42.120.000. La estrategia con ceros
gana **$121.881**: la oferta del banco (5,3 %) está bajo la forward. (c) Poder pedir prestado a la
spot de un año (en la práctica una persona o una empresa paga más que el Estado), sin costos de
transacción y sin riesgo de que los 40 millones no lleguen.

**6.7.**

| Año | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Forward de un año | 4,40 % | 5,10 % | 5,35 % | 5,35 % |
| Tasa corta esperada, expectativas puras | 4,40 % | 5,10 % | 5,35 % | 5,35 % |
| Tasa corta esperada, con premio | 4,40 % | 4,90 % | 4,95 % | 4,75 % |

Bajo expectativas puras, el mercado espera que la tasa corta suba casi un punto y se quede ahí. Con
el premio, espera un alza moderada y después una **baja** en el año 4. La misma curva normal admite
las dos lecturas: la pendiente sola no separa expectativa de premio.

**6.8.** **Falso, o al menos incierto.** Es cierto que hoy el corto paga más, pero bajo expectativas una
curva invertida significa que el mercado **espera que las tasas cortas bajen**. Quien invierte corto
tendrá que renovar a tasas menores (riesgo de reinversión) y, en promedio, terminará igual que quien
fijó el largo: las forwards ya incorporan esa baja. Además, si las tasas efectivamente bajan, los
bonos largos **suben de precio**, y quien quedó solo en corto se pierde esa ganancia. La decisión
depende del horizonte: quien necesita la plata en cinco años y fija una tasa a cinco años elimina el
riesgo de reinversión. «Lo racional» es calzar el plazo con la necesidad, no perseguir la tasa más
alta del día. (Tampoco es seguro que una curva invertida anticipe una recesión: es una señal que
suele acompañarla, no una ley.)

**6.9.** (a) Bootstrapping: $s_1 =$ **4,41 %**, $s_2 =$ **4,96 %**, $s_3 =$ **5,52 %**. Precio teórico de D:
$8/1{,}0441 + 8/1{,}0496^2 + 108/1{,}0552^3 =$ **106,84**. (b) Se replica desde el último flujo: en el año 3,
$n_C \times 105{,}5 = 108$, así que $n_C =$ 1,0237; en el año 2, $n_B \times 105 + n_C \times 5{,}5 = 8$, así que
$n_B =$ 0,0226; en el año 1, $n_A \times 104 + n_B \times 5 + n_C \times 5{,}5 = 8$, así que $n_A =$ 0,0217. Esa cartera
cuesta lo mismo que el precio teórico, 106,84. (c) D está **caro**: se vende D (o se emite un
flujo igual) a 107,90 y se compra la cartera réplica en 106,84. Los flujos futuros se anulan y quedan
**1,06** por bono hoy, sin riesgo. Esa presión de venta baja el precio de D hasta 106,84. (d) A
107,90 la TIR de D es **5,09 %**; a 106,84 sería **5,47 %**. Un bono caro rinde menos que lo que su
plazo y su riesgo justifican.

**6.10.** (a) $f_{1,2} =$ **5,40 %** y $f_{2,3} =$ **5,90 %**. La estrategia A junta $12.000.000 × 1,053³ =
**$14.010.911**, y B con las forwards junta lo mismo, **$14.010.911**: por construcción, la forward es
la tasa que iguala los caminos. (b) Con 5,0 % y 5,2 %: A **$14.010.911** (fijo desde el inicio) ·
B **$13.864.939** · C **$13.917.960**. Las tasas reales quedaron bajo las forwards y ganó quien fijó
más largo. (c) Para empatar, el año 3 tendría que haber pagado **6,31 %**. (d) Si las forwards traen
premio por liquidez, las tasas que se esperan son menores que las forwards y A gana en promedio: el
premio se lo paga el mercado a quien compra largo. Esta pareja lo cobra sin correr riesgo de precio,
porque no vende el bono antes: lo mantiene hasta el vencimiento, que coincide con su fecha. Es el
argumento del hábitat preferido.

---

## 12. Caso integrador · la curva que usa Valentina

> Valentina es la dueña de Estampa Sur. Las cifras salen de `verificacion/caso_valentina.py`; todo es
> ficticio, incluida la Tesorería.

Antes de mirar bonos de empresas (unidad 7), Valentina quiere saber cuánto paga el Estado ficticio
por cada plazo. Encuentra estos ceros de la Tesorería, por cada 100 de nominal:

| Plazo (años) | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Precio del cero | 95,42 | 90,63 | 85,77 | 80,94 | 76,18 |
| Spot $s_t$ | 4,80 % | 5,04 % | 5,25 % | 5,43 % | 5,59 % |
| Forward $f_{t-1,t}$ | | 5,29 % | 5,67 % | 5,97 % | 6,25 % |

**Desarrollo.** Cada spot sale de $s_t = (100/P_t)^{1/t} - 1$; por ejemplo, $s_3 = (100/85{,}77)^{1/3} - 1 = 5{,}25\ \%$.
Cada forward sale de dividir capitalizaciones; por ejemplo,
$f_{2,3} = 1{,}0525^3/1{,}0504^2 - 1 = 5{,}67\ \%$. Comprobación de que la spot es el promedio de las
forwards: $1{,}0480 \times 1{,}0529 \times 1{,}0567$ elevado a $1/3$ da otra vez 5,25 %.

**Lectura.**

- **Curva normal**: la spot sube de 4,80 % a 5,59 % y cada forward queda sobre la spot de su plazo.
  Bajo expectativas puras, el mercado esperaría que la tasa a un año suba hasta cerca de 6,25 % en
  el año 5; con premio por liquidez, parte de esa subida es premio y no expectativa.
- **Lo que pasa a la unidad 7.** El bono de «Eléctrica Andina» (4 años, cupón 5,9 % anual) se valora
  descontando cada flujo con su spot: vale **101,75** y su TIR es **5,40 %**, cerca de la spot a 4
  años (5,43 %) porque el nominal llega al final.
- **Lo que pasa a la unidad 11.** La spot a 1 año, **4,80 %**, es la tasa libre de riesgo de los
  portafolios: lo que gana con certeza quien presta un año al Estado.
- **Un puente con la unidad 5.** El saldo de la máquina ($8.750.000 en el año 3) es una deuda cierta.
  Para tener hoy apartada la plata exacta, Valentina compraría ceros a 3 años: le costaría
  $8.750.000 × 0,8577 = **$7.504.875**. En la unidad 5 ese saldo valía $6.228.077 porque se descontó al
  12 %, el costo de oportunidad del proyecto. Las dos cifras responden preguntas distintas: cuánto
  pesa el saldo en el VAN del proyecto, y cuánto cuesta dejarlo asegurado sin riesgo. La unidad 8
  logra lo mismo con bonos con cupón (inmunización).

---

## 13. Para seguir

**En los libros del ramo.**

- Fabozzi, *The Handbook of Fixed Income Securities*: los capítulos sobre la estructura de tasas, las
  tasas spot y forward y las teorías de la curva. Es la referencia del ramo para renta fija.
- Ross, Westerfield y Jaffe, *Finanzas corporativas* (9.ª ed., 2012): el capítulo de valoración de
  bonos, en su parte sobre la estructura temporal de las tasas.
- Complementaria: Bodie, Kane y Marcus, *Investments*, el capítulo sobre la estructura temporal de
  las tasas (forwards, teorías y su interpretación).

**Abierto y gratis.**

- Dahlquist y Knight, *Principles of Finance*, OpenStax (2022), en inglés, sección 10.3 «Using the
  Yield Curve»: formas de la curva (normal, invertida y plana) y su lectura. No trae spots ni
  forwards; para eso, esta unidad. Licencia CC BY-NC-SA 4.0:
  https://openstax.org/books/principles-finance/pages/10-3-using-the-yield-curve

**Con el tutor.** Pega `tutor/contexto.md` al inicio de la conversación con cualquier IA y pídele,
por ejemplo: «Dame tres bonos con cupón, hazme construir la curva por bootstrapping y corrígeme
cada paso».
