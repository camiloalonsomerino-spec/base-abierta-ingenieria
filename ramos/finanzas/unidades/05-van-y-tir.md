---
ramo: Finanzas
unidad: 5
titulo: VAN, TIR y criterios de inversión
version: 0.1 (15-10-2026)
requiere: [01-valor-del-dinero, 02-tasas-de-interes, 03-anualidades]
alimenta: [08-duracion-e-inmunizacion, 12-capm-y-costo-de-capital]
verificacion: verificacion/u05_van_tir.py
---

# Unidad 5 · VAN, TIR y criterios de inversión

**Qué vas a poder hacer.** Decidir si un proyecto crea valor con el VAN y explicar qué significa
la cifra; sacar la TIR a mano por interpolación y decir cuándo engaña; calcular el período de
recuperación (simple y descontado) y el índice de rentabilidad, y saber para qué sirve cada uno;
reconocer un flujo con más de una TIR (o con ninguna) usando la regla de signos de Descartes;
elegir entre proyectos excluyentes de distinta escala o de distinta vida; armar un flujo
incremental con su costo de oportunidad, y tratar la inflación sin mezclar pesos nominales con
tasas reales.

**Lo que necesitas antes.** Traer un monto al presente y llevarlo al futuro (unidad 1), pasar de
una tasa nominal a una real (unidad 2) y el valor presente de una anualidad (unidad 3).

**Tiempo.** Unas 5 horas: 2 de lectura con el ejemplo y 3 de práctica.

---

## 1. La idea

Invertir es entregar plata hoy a cambio de plata después. La pregunta de esta unidad es una sola:
**¿lo que recibo después vale, hoy, más que lo que entrego?** Para responderla hay que comparar
pesos de fechas distintas, y eso exige una tasa.

Esa tasa es el **costo de oportunidad del capital**: lo que rendiría la misma plata en la mejor
alternativa **comparable**. Comparable quiere decir de riesgo, plazo y escala parecidos. Un
depósito a plazo a un año no es comparable con un negocio de cinco años: casi no tiene riesgo y
dura mucho menos. Si el proyecto es más riesgoso (un país más inestable, un mercado nuevo), la
alternativa comparable rinde más y la tasa sube.

Los indicadores de esta unidad responden preguntas distintas:

| Indicador | Pregunta que responde |
|---|---|
| VAN | ¿Cuánta riqueza crea hoy el proyecto, en pesos? |
| TIR | ¿Qué rentabilidad promedio compuesta anual obtiene el capital que queda invertido? |
| Período de recuperación | ¿Cuánto tarda en volver la plata invertida? |
| Índice de rentabilidad (IVAN) | ¿Cuánto VAN genera cada peso invertido? |
| TIRM | ¿Qué rentabilidad se obtiene si los flujos se reinvierten a una tasa realista? |

---

## 2. Valor actual neto (VAN)

Con $FC_t$ el flujo de caja neto del año $t$ (ingresos menos costos, gastos e impuestos, en caja),
$I_0$ la inversión de hoy y $r$ el costo de oportunidad:

$$VAN = -I_0 + \sum_{t=1}^{n} \frac{FC_t}{(1+r)^t}$$

La fórmula trae cada flujo al presente y lo compara con lo que se invierte. Por eso está mal sumar
los flujos sin descontar: un peso del año 5 no es un peso de hoy.

**Regla de decisión.**

- $VAN > 0$: el proyecto rinde más que la alternativa comparable. Crea riqueza y conviene.
- $VAN < 0$: rinde menos que la alternativa. Destruye riqueza.
- $VAN = 0$: rinde **exactamente** lo que exige el inversionista. No es «no gana nada»: gana lo
  mismo que la alternativa, y hacerlo o no da igual.

**Cómo se lee la cifra.** Un VAN de $1.000.000 significa que el dueño queda, hoy, un millón más
rico que si hubiera puesto su plata en la alternativa. Es lo máximo que podría pagar por encima de
la inversión por el derecho a hacer el proyecto.

> **Por qué la inversión es el dato más firme.** La máquina se cotiza hoy; los flujos son
> proyecciones. Un VAN positivo pero chico no es «más riesgoso» por ser chico: el riesgo ya está en
> la tasa. Lo que sí dice un VAN chico es que un error pequeño en los flujos lo puede dar vuelta.

---

## 3. Tasa interna de retorno (TIR)

La TIR es la tasa que hace cero el VAN:

$$\sum_{t=0}^{n} \frac{FC_t}{(1+TIR)^t} = 0$$

Esa es la definición matemática. La financiera es otra: **la TIR es la rentabilidad promedio,
compuesta y anual, que obtiene el capital que sigue invertido en el proyecto**. Si inviertes 100
y al año recibes 110, la TIR es 10 %: a esa tasa, $110/1{,}10 = 100$ y el VAN es cero.

**Regla.** Con flujos convencionales (primero salidas, después entradas):

$$r < TIR \Rightarrow VAN > 0 \qquad r = TIR \Rightarrow VAN = 0 \qquad r > TIR \Rightarrow VAN < 0$$

**La curva del VAN.** Si dibujas el VAN contra la tasa, en un proyecto convencional la curva baja:
mientras más se castiga el futuro, menos valen los flujos. La TIR es donde la curva corta el eje.

### TIR a mano: prueba, error e interpolación

En el certamen no hay calculadora programable. La TIR se encuentra así:

1. Prueba una tasa. Si el VAN da positivo, la TIR es mayor; si da negativo, es menor.
2. Encierra la TIR entre dos tasas cercanas $r_1$ y $r_2$, con VAN de signos opuestos.
3. Interpola en línea recta:

$$TIR \approx r_1 + (r_2 - r_1)\,\frac{VAN(r_1)}{VAN(r_1) - VAN(r_2)}$$

Mientras más cerca estén $r_1$ y $r_2$, mejor la aproximación (la curva no es una recta).

---

## 4. Período de recuperación

**Simple.** Cuántos años tarda el flujo acumulado en volver a cero. Si en el año $k$ el
acumulado todavía es negativo y en el $k+1$ ya es positivo:

$$PR = k + \frac{\text{lo que falta al cierre de } k}{FC_{k+1}}$$

(supone que el flujo del año $k+1$ llega parejo durante el año).

**Descontado.** Lo mismo, pero acumulando los flujos **ya descontados**. Siempre es más largo que
el simple, porque cada flujo vale menos.

**Para qué sirve y para qué no.** Mide liquidez y exposición: un negocio en un país inestable o
una tecnología que envejece rápido quiere recuperar pronto. Pero tiene dos defectos serios:
**ignora todo lo que pasa después del corte** y (el simple) **ignora el valor del dinero en el
tiempo**. Un proyecto puede recuperarse rápido y destruir valor (ejercicio 5.2).

---

## 5. Índice de rentabilidad (IVAN)

$$IVAN = \frac{VAN}{I_0} \qquad\qquad IR = \frac{VP(\text{flujos futuros})}{I_0} = 1 + IVAN$$

Dice cuánto VAN genera cada peso invertido. Si la inversión se paga en partes, $I_0$ se reemplaza
por el **valor presente de todas las inversiones** (el caso de Valentina lo usa).

**Cuándo importa.** Cuando hay **racionamiento de capital**: un presupuesto fijo y más proyectos
buenos de los que alcanza a pagar. Se ordenan por IVAN y se eligen de arriba hacia abajo. Si los
proyectos no se pueden partir, hay que revisar las combinaciones que caben: la mejor puede no ser
la que da el orden (ejercicio 5.4). Sin racionamiento, manda el VAN.

---

## 6. Ejemplo resuelto · el furgón de Javiera

Javiera quiere comprar un furgón usado para hacer fletes los fines de semana. Cuesta **$9.800.000**.
Después de combustible, mantención, seguro, permiso de circulación y de pagarse su propio tiempo,
estima estos flujos netos, y al final del año 4 vende el furgón en **$3.600.000**. Su alternativa
comparable (un negocio de riesgo parecido) rinde **11 %** anual.

| Año | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| Flujo neto | −$9.800.000 | $2.900.000 | $3.100.000 | $3.100.000 | $2.700.000 |
| Venta del furgón | | | | | $3.600.000 |
| $FC_t$ | −$9.800.000 | $2.900.000 | $3.100.000 | $3.100.000 | $6.300.000 |

**Paso 1 · VAN.** Se descuenta cada flujo al 11 %.

| Año | $FC_t$ | $FC_t / 1{,}11^t$ | Acumulado descontado |
|---|---|---|---|
| 0 | −$9.800.000 | −$9.800.000 | −$9.800.000 |
| 1 | $2.900.000 | $2.612.613 | −$7.187.387 |
| 2 | $3.100.000 | $2.516.030 | −$4.671.358 |
| 3 | $3.100.000 | $2.266.693 | −$2.404.665 |
| 4 | $6.300.000 | $4.150.005 | $1.745.341 |

El valor presente de lo que entra es $11.545.341; menos la inversión, **VAN = $1.745.341**.
Javiera queda 1,7 millones más rica que con su alternativa: conviene.

**Paso 2 · TIR por prueba y error.** Al 15 % el VAN es $706.130 (positivo: la TIR es mayor); al
20 % es −$398.380 (negativo: es menor). Se acerca el intervalo: al 18 % el VAN es $20.224 y al 19 %
es −$192.712.

$$TIR \approx 18\ \% + 1\ \% \times \frac{20{.}224}{20{.}224 + 192{.}712} = 18{,}09\ \%$$

La TIR es **18,09 %**, mayor que el 11 % exigido: coherente con el VAN positivo.

**Paso 3 · Recuperación.** Simple: el acumulado sin descontar es −$9.800.000, −$6.900.000,
−$3.800.000, −$700.000 y $5.600.000. Al cierre del año 3 faltan $700.000 y el año 4 trae
$6.300.000:

$$PR = 3 + \frac{700{.}000}{6{.}300{.}000} = 3{,}11 \text{ años}$$

Descontado: al cierre del año 3 faltan $2.404.665 (tabla del paso 1) y el año 4 trae $4.150.005
descontados: $PR_d = 3 + 2{.}404{.}665 / 4{.}150{.}005 =$ **3,58 años**.

**Paso 4 · IVAN.** $IVAN = {1{.}745{.}341}/{9{.}800{.}000} =$ **0,178**: cada peso invertido crea 18 centavos de
riqueza por sobre la alternativa.

**Paso 5 · TIR modificada.** ¿Y si lo que gana el furgón solo se puede reinvertir al 11 %? Cada
flujo se lleva al año 4 a esa tasa:

$$VF_4 = 2{.}900{.}000(1{,}11)^3 + 3{.}100{.}000(1{,}11)^2 + 3{.}100{.}000(1{,}11) + 6{.}300{.}000 = 17{.}526{.}640$$

El valor futuro de los ingresos es $17.526.640, y:

$$TIRM = \left(\frac{17{.}526{.}640}{9{.}800{.}000}\right)^{1/4} - 1 = 15{,}64\ \%$$

**Cómo se lee.** Los cinco indicadores dicen lo mismo con palabras distintas: el furgón crea valor
(VAN), su capital rinde bastante más que el 11 % (TIR), la plata vuelve antes del cuarto año
(recuperación) y, si la reinversión es realista, el rendimiento efectivo es 15,64 % y no 18,09 %.
La TIR exageraba porque supone algo que Javiera no puede hacer: reinvertir cada flete al 18 %.

---

## 7. Los problemas de la TIR

### 7.1 Cambios de signo: varias TIR o ninguna

La ecuación de la TIR es un polinomio. Con $x = 1/(1+r)$:

$$FC_0 + FC_1\,x + FC_2\,x^2 + \dots + FC_n\,x^n = 0$$

Un polinomio de grado $n$ tiene $n$ raíces, pero solo sirven las reales con $x > 0$ (es decir,
$r > -100\ \%$). La **regla de signos de Descartes** da una cota: **el número de raíces positivas es,
como máximo, el número de cambios de signo de la secuencia de flujos, y difiere de él en un número
par.**

| Cambios de signo | TIR posibles | Ejemplo |
|---|---|---|
| 1 (convencional) | exactamente 1 | − + + + |
| 2 | 2 o 0 | − + − (inversión, ganancias, costo de cierre) |
| 3 | 3 o 1 | − + + − + + |

Descartes **acota**; no dice cuántas hay. Para saberlo, se mira la curva del VAN: cuántas veces
corta el eje. Si corta dos veces, hay dos TIR y ninguna de las dos es «la» rentabilidad; si no
corta, no hay TIR y el VAN igual sirve.

**Una prueba que sí asegura una sola TIR.** Calcula el **saldo del proyecto** a la TIR: lo que el
proyecto le debe al dueño al cierre de cada año, $S_t = S_{t-1}(1+TIR) + FC_t$ con $S_0 = FC_0$. Si
el saldo se mantiene negativo hasta el último año, el proyecto nunca le presta plata al dueño
(es una **inversión pura**) y la TIR es única. El caso de Valentina lo usa.

### 7.2 Proyectos excluyentes de distinta escala

Cuando hay que elegir **uno** entre dos, la TIR puede elegir mal. Un proyecto chico puede tener una
TIR altísima y crear poca plata; la TIR es un porcentaje y los porcentajes no dicen cuánto se gana.

La salida es el **flujo incremental** (grande menos chico): la plata extra que se invierte en el
grande, ¿rinde más que $r$?

- Si la TIR incremental es mayor que $r$ (o el VAN incremental es positivo), conviene el grande.
- La TIR incremental es la **tasa de Fisher**: la tasa donde las dos curvas del VAN se cruzan.
  Bajo ella gana el grande; sobre ella, el chico.

Con proyectos excluyentes, **se elige el de mayor VAN**. La TIR incremental llega a la misma
respuesta por otro camino.

### 7.3 Distinta vida útil

Dos máquinas que hacen lo mismo pero duran distinto no se comparan por VAN (o por valor actual de
costos, VAC) directo: la de vida corta habría que recomprarla. Hay dos caminos equivalentes:

- **Período común:** repetir cada una hasta un horizonte común (el mínimo común múltiplo de las
  vidas) y comparar.
- **Anualidad equivalente:** convertir el VAN (o el VAC) de un ciclo en una cuota anual
  $A_{eq} = VAN / a_{n,r}$, con $a_{n,r} = \dfrac{1-(1+r)^{-n}}{r}$. Si se repite para siempre,
  $VAN_\infty = A_{eq}/r$. Se elige la de mayor $A_{eq}$ (o menor costo anual equivalente).

### 7.4 El supuesto de reinversión y la TIRM

Que la TIR sea 30 % no significa que el dueño termine ganando 30 % anual. **Eso solo pasa si cada
flujo intermedio se reinvierte, hasta el final, a ese mismo 30 %.** Si se reinvierte a menos, la
rentabilidad realizada baja. Mientras más alta la TIR, más irreal el supuesto.

La **TIR modificada** lo corrige: lleva los ingresos al año $n$ a una tasa de reinversión realista
(normalmente $r$) y los egresos al año 0 a la tasa de financiamiento:

$$TIRM = \left(\frac{VF_n(\text{ingresos})}{VP_0(\text{egresos})}\right)^{1/n} - 1$$

Siempre hay una sola TIRM, y está entre $r$ y la TIR. Si $TIRM > r$, el VAN es positivo.

**Cuando los ingresos son una anualidad**, su valor futuro es

$$VF_n = A\,\frac{(1+r)^n \boxed{-\,1}}{r}$$

**Ojo con el −1.** Sin él calculas otra cosa. Compruébalo siempre por el otro camino: el valor
presente de la anualidad llevado al año $n$, $A\,a_{n,r}\,(1+r)^n$, tiene que dar lo mismo.

### 7.5 La advertencia de Kelleher y MacCormack (2004)

Es un artículo corto de la revista de McKinsey, y su tesis cabe en una frase: **la TIR es el
indicador favorito de los ejecutivos y, a la vez, uno de los que más los engaña.** Su argumento,
dicho con palabras de esta unidad:

1. **El defecto central es la reinversión.** La TIR solo describe lo que el dueño gana si los flujos
   intermedios rinden la misma TIR. En los proyectos más atractivos en apariencia (TIR muy por
   sobre el costo de capital) ese supuesto es el más falso, y por eso la TIR **infla justo a los
   proyectos que más brillan**.
2. **Eso distorsiona las decisiones.** Una empresa que ordena su cartera por TIR puede preferir
   proyectos cortos y de TIR alta sobre otros que crean más valor.
3. **Los otros defectos conocidos** (varias TIR con cambios de signo, ceguera a la escala) se suman.
4. **Qué recomiendan.** Decidir con el VAN, que descuenta al costo de capital: la tasa a la que de
   verdad se puede reinvertir. Si la organización insiste en una tasa, reportar la **TIRM**, con la
   reinversión al costo de capital.

> **Un matiz que suma en un comente.** La TIR no «supone» nada por sí sola: es una propiedad del
> flujo. El supuesto aparece cuando se la **interpreta** como la rentabilidad que obtendrá el
> dueño. El VAN no tiene ese problema porque no promete una rentabilidad: mide riqueza al costo de
> oportunidad.

---

## 8. Flujos incrementales y costo de oportunidad

Se evalúa **la diferencia** entre hacer el proyecto y no hacerlo. Todo lo que cambia entra; lo que
no cambia, no.

| Partida | ¿Entra? | Por qué |
|---|---|---|
| Costo hundido (un estudio ya pagado) | **No** | Se pagó igual, se haga o no el proyecto |
| Costo de oportunidad de un recurso propio (un local que se podría arrendar) | **Sí** | Usarlo en el proyecto hace perder ese ingreso |
| Efectos sobre otras líneas (canibalización) | **Sí** | Es plata que deja de entrar por hacer el proyecto |
| Capital de trabajo | **Sí** | Sale al inicio y se recupera al final |
| Valor residual | **Sí** | Es un ingreso del último año |
| Intereses del crédito | **No** | El costo del tiempo ya lo cobra la tasa; restarlos lo cobra dos veces |

El costo de oportunidad es la idea que más se olvida: **que algo sea propio no lo hace gratis.**
Un galpón propio que se podría arrendar le cuesta al proyecto ese arriendo.

---

## 9. Inflación: nominal contra real

Un flujo **nominal** está en pesos de cada año; uno **real**, en pesos de hoy (poder de compra
constante). La tasa se convierte con Fisher (unidad 2):

$$(1 + r_{\text{nominal}}) = (1 + r_{\text{real}})(1 + \pi)$$

**La regla es una sola: consistencia.** Flujos nominales con tasa nominal; flujos reales con tasa
real. Bien hecho, los dos caminos dan **el mismo VAN** (ejercicio 5.7). Las dos mezclas fallan:

- Flujos reales con tasa nominal: se castiga la inflación sin haberla puesto en los flujos. El VAN
  sale **subestimado**.
- Flujos nominales con tasa real: se infla el valor de los flujos futuros. El VAN sale
  **sobrestimado** y un proyecto malo puede parecer bueno.

Ojo con lo que no se reajusta: un saldo de precio fijo, una cuota pactada en pesos o un arriendo
sin reajuste son nominales aunque el resto del flujo se haya estimado en pesos de hoy.

---

## 10. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Sumar los flujos sin descontar | Cada flujo se divide por $(1+r)^t$ antes de sumar |
| Decir que VAN = 0 «no gana nada» | Gana exactamente la rentabilidad de la alternativa comparable |
| Elegir entre excluyentes por la mayor TIR | Se elige el mayor VAN; la TIR ignora la escala |
| Dar por única la TIR de un flujo con varios cambios de signo | Cuenta los cambios (Descartes) y mira la curva del VAN o el saldo del proyecto |
| Restar un estudio ya pagado o los intereses del crédito | Hundido no entra; el financiamiento ya está en la tasa |
| Olvidar el arriendo que se pierde por usar un local propio | Todo recurso con uso alternativo tiene costo de oportunidad |
| Descontar flujos en pesos de hoy con la tasa nominal | Real con real, nominal con nominal |
| Olvidar el −1 en el valor futuro de una anualidad | $A[(1+r)^n - 1]/r$; compruébalo con $A\,a_{n,r}(1+r)^n$ |
| Leer la TIR como lo que efectivamente ganará el dueño | Solo si reinvierte a la TIR; si no, calcula la TIRM |

---

## 11. Práctica

Diez ejercicios: 5.1 a 5.4 básicos, 5.5 a 5.8 intermedios, 5.9 y 5.10 de desafío. Dos son
**comentes** (5.3 y 5.8): responde Verdadero, Falso o Incierto y **argumenta**; la nota está en la
explicación, no en la palabra. Las pautas están en la sección 12.

**5.1 · La máquina de bordado de Martina (básico).** Martina compra una máquina de bordado por
$3.150.000 para su emprendimiento de poleras personalizadas. Sus flujos netos serán $1.050.000,
$1.200.000, $1.200.000 y $900.000 en los años 1 a 4; después la máquina no vale nada. Su costo de
oportunidad es 10 %. Calcula el VAN, encuentra la TIR por interpolación entre 14 % y 15 % e
interpreta las dos cifras.

**5.2 · Paneles o termo solar (básico).** Una familia evalúa dos formas de bajar su cuenta de luz
y gas, con tasa 7 %:

| Opción | Inversión | Ahorro anual | Vida útil |
|---|---|---|---|
| Paneles fotovoltaicos | $4.680.000 | $720.000 | 12 años |
| Termo solar | $1.900.000 | $380.000 | 6 años |

(a) Calcula el período de recuperación simple y el descontado de cada una. (b) Calcula el VAN.
(c) ¿Qué elegiría alguien que mira solo la recuperación? ¿Y con el VAN? (d) Calcula el valor futuro
de los ahorros de los paneles al año 12 y la TIRM con reinversión al 7 %.

**5.3 · Comente (básico).** «Si un proyecto tiene VAN igual a cero, no gana nada, así que no vale
la pena el esfuerzo de hacerlo.»

**5.4 · Presupuesto limitado (básico).** Una cooperativa tiene $21.500.000 para invertir este año y
cuatro proyectos, independientes y que no se pueden partir:

| Proyecto | Inversión | VAN |
|---|---|---|
| A | $12.600.000 | $3.520.000 |
| B | $8.900.000 | $2.580.000 |
| C | $6.400.000 | $2.250.000 |
| D | $5.700.000 | $1.180.000 |

(a) Calcula el IVAN de cada uno y elige siguiendo ese orden. (b) Revisa las combinaciones que caben
en el presupuesto: ¿la regla dio la mejor?

**5.5 · El local del primer piso (intermedio).** Una dueña de casa con un local en el primer piso
puede remodelarlo de dos formas excluyentes, para arrendarlo 5 años; tasa 9 %:

| Opción | Inversión | Arriendo neto anual |
|---|---|---|
| Chica (bodega) | $6.000.000 | $1.900.000 |
| Grande (local comercial) | $18.000.000 | $5.300.000 |

(a) Calcula VAN y TIR de cada una. (b) ¿Cuál elige la TIR y cuál el VAN? (c) Calcula la TIR del
flujo incremental e interprétala como tasa de Fisher. (d) ¿Cambia la decisión si la tasa fuera
15 %?

**5.6 · Pizzas en la panadería (intermedio).** Don Raúl tiene una panadería de barrio y evalúa un
horno para vender pizzas en la tarde, por 4 años y sin impuestos. Tasa 10 %. Arma el flujo
incremental y calcula el VAN.

- El horno cuesta $5.200.000 y al final se vende en $600.000.
- Ya pagó un estudio de mercado de $400.000.
- El rincón donde iría el horno hoy se lo arrienda a una florista en $150.000 al mes; con el horno,
  pierde ese arriendo.
- Venderá $7.200.000 de pizza al año, con costos de $3.600.000.
- Algunos clientes de la tarde comprarán pizza en vez de pan: el margen del pan baja $600.000 al año.
- Necesita $500.000 de capital de trabajo al inicio, que recupera al final.
- Financiará el horno con un crédito al 8 %.

**5.7 · Máquina expendedora (intermedio).** Un estudiante evalúa instalar una máquina expendedora
en su universidad por $3.500.000. Estima flujos de $1.100.000 al año **en pesos de hoy** durante
4 años. La inflación esperada es 3,8 % anual y su costo de oportunidad nominal es 11 %.
(a) Calcula la tasa real y el VAN en términos reales. (b) Convierte los flujos a nominales y
calcula el VAN nominal. (c) ¿Qué VAN obtiene quien descuenta los flujos en pesos de hoy al 11 %?
¿Qué decisión equivocada tomaría?

**5.8 · Comente (intermedio).** Un proyecto requiere $10.000.000 y entrega $6.500.000, $5.500.000 y
$4.000.000 en los años 1 a 3; el costo de capital es 10 %. «La TIR de este proyecto es 30,58 %,
así que la empresa ganará un 30,58 % anual sobre los diez millones durante tres años.»

**5.9 · Áridos con restauración (desafío).** Una empresa explotaría un pozo de áridos un año: invierte
$20.000.000 hoy, gana $47.000.000 al año 1 y al año 2 debe restaurar el terreno por $27.300.000.
Tasa 12 %. (a) Cuenta los cambios de signo y di qué permite Descartes. (b) Encuentra las TIR
(resuelve la cuadrática en $u = 1+r$). (c) Calcula el VAN al 12 % y di para qué tasas conviene.
(d) Si la restauración costara $28.000.000, ¿cuántas TIR hay? ¿Conviene? (e) Calcula la TIRM al
12 % en los dos casos.

**5.10 · Dos lavadoras industriales (desafío).** Una lavandería necesita una lavadora y la
mantendrá para siempre, recomprándola al final de su vida. Tasa 10 %.

| Lavadora | Inversión | Costo de operación anual | Vida útil |
|---|---|---|---|
| A | $7.000.000 | $1.200.000 | 3 años |
| B | $11.500.000 | $900.000 | 5 años |

(a) Calcula el valor actual de costos (VAC) de un ciclo de cada una. ¿Cuál parece mejor?
(b) Calcula el costo anual equivalente y el VAC a perpetuidad. (c) Compruébalo con el período común
de 15 años.

---

## 12. Pautas

**5.1.** Descontados al 10 %: $954.545, $991.736, $901.578 y $614.712. **VAN = $312.571**: Martina
queda 312 mil pesos más rica que con su alternativa. Al 14 % el VAN es $37.252 y al 15 % es
−$25.987:

$$TIR \approx 14\ \% + 1\ \% \times \frac{37{.}252}{37{.}252 + 25{.}987} = 14{,}59\ \%$$

La TIR es **14,59 %**: el capital que queda en la máquina rinde, en promedio, 14,59 % anual
compuesto, más que el 10 % exigido.

**5.2.**

| | Paneles | Termo |
|---|---|---|
| Recuperación simple | 6,5 años | 5,0 años |
| Recuperación descontada | 8,97 años | no se recupera en sus 6 años |
| VAN al 7 % | $1.038.734 | −$88.715 |
| TIR | 10,98 % | 5,47 % |

Quien mira la recuperación elige el termo: vuelve la plata antes. El VAN dice lo contrario: el
termo **destruye valor** (su TIR, 5,47 %, no alcanza el 7 %), y los paneles crean un millón. La
recuperación no ve los seis años extra de ahorro de los paneles ni el valor del tiempo.

(d) Con la anualidad de ahorros, $VF_{12} = 720{.}000 \times \dfrac{1{,}07^{12} - 1}{0{,}07} = 720{.}000 \times 17{,}8885$:
el valor futuro es **$12.879.685**. Comprobación por el otro camino: el VP de los ahorros ($5.718.734)
por $1{,}07^{12}$ da lo mismo. TIRM $= (12{.}879{.}685/4{.}680{.}000)^{1/12} - 1 =$ **8,80 %**: mayor que
7 % (VAN positivo) y menor que la TIR de 10,98 %.

**5.3.** **Falso.** El VAN se calcula descontando al costo de oportunidad, así que un VAN igual a
cero significa que el proyecto rinde **exactamente** lo mismo que la mejor alternativa comparable:
devuelve la inversión y además paga el retorno exigido por el tiempo y el riesgo. Sí gana; lo que
no hace es ganar **más** que la alternativa. Por eso la decisión es indiferente, no negativa:
hacerlo o no deja al dueño igual de rico. Lo que podría inclinar la balanza son elementos que el
flujo no recoge (el esfuerzo personal, si no se valoró en los flujos, o una opción de crecer que
el proyecto abre).

**5.4.** IVAN: A 0,279 · B 0,290 · C 0,352 · D 0,207. Siguiendo el orden: C ($6.400.000), luego B
(van $15.300.000); A no cabe; entra D. Total invertido $21.000.000 y **VAN $6.010.000**. Revisando
las combinaciones, **A + B** usa exactamente el presupuesto y da **VAN $6.100.000**, más. El IVAN
ordena bien cuando los proyectos se pueden partir; si no, deja plata ociosa ($500.000 en este caso)
y hay que comparar las combinaciones que caben.

**5.5.**

| | Chica | Grande | Incremental (grande − chica) |
|---|---|---|---|
| Inversión | $6.000.000 | $18.000.000 | $12.000.000 |
| Flujo anual | $1.900.000 | $5.300.000 | $3.400.000 |
| VAN al 9 % | $1.390.337 | $2.615.152 | $1.224.814 |
| TIR | 17,57 % | 14,45 % | 12,86 % |

La TIR elige la chica; el VAN, la grande. Manda el VAN: la dueña quiere riqueza, no un porcentaje.
Los doce millones extra de la grande rinden 12,86 %, más que el 9 % exigido: vale la pena ponerlos.
Esa es la **tasa de Fisher**: bajo 12,86 % gana la grande; sobre ella, la chica. Al 15 % la chica
tiene VAN $369.095 y la grande −$233.578: ahí se elige la chica.

**5.6.** Lo que entra y lo que no:

- El estudio ($400.000) es **hundido**: no entra.
- El arriendo perdido es **costo de oportunidad**: $1.800.000 al año.
- Los intereses del crédito **no entran**: la tasa de descuento ya cobra el tiempo.

Flujo anual: $7.200.000 - 3.600.000 - 600.000 - 1.800.000 = $1.200.000. En $t=0$ salen
$5.700.000 (horno y capital de trabajo); en $t=4$ entran además $1.100.000 (venta del horno y
capital de trabajo), cuyo VP es $751.315.

$$VAN = -5{.}700{.}000 + 1{.}200{.}000 \times 3{,}1699 + 751{.}315 = -1{.}144{.}847$$

**VAN = −$1.144.847**: no conviene. Sin el costo de oportunidad el VAN habría sido $4.560.911 y
don Raúl habría comprado el horno. Las pizzas sí ganan plata, pero menos que lo que ya le paga la
florista por ese rincón. (Quien además resta el estudio llega a un VAN todavía más negativo por un
motivo equivocado.)

**5.7.** (a) $r_{\text{real}} = 1{,}11/1{,}038 - 1 =$ **6,936 %** (la resta $11 - 3{,}8 = 7{,}2\ \%$ es solo una
aproximación). VAN real: $-3{.}500{.}000 + 1{.}100{.}000 \times a_{4;\,6{,}936\%} =$ **$231.287**.
(b) Flujos nominales: $1.141.800, $1.185.188, $1.230.226 y $1.276.974. Descontados al 11 %, el VAN
es el mismo $231.287. (c) Descontar pesos de hoy al 11 % da −$87.310: un proyecto bueno parece malo
porque se castigó una inflación que nunca se puso en los flujos.

**5.8.** **Incierto, y falso tal como está planteado.** La TIR de 30,58 % es correcta como propiedad
del flujo, pero que la empresa **termine ganando** 30,58 % anual exige reinvertir cada flujo
intermedio a 30,58 % hasta el año 3. En ese caso tendría $22.264.954 al final. Si lo que recibe
solo rinde el costo de capital (10 %), al año 3 junta $17.915.000 y su rentabilidad efectiva es la
**TIRM = 21,45 %**. Es la advertencia de Kelleher y MacCormack: mientras más alta la TIR, más irreal
el supuesto de reinversión y más se infla el proyecto. La decisión no cambia (VAN $3.459.805 al
10 %, conviene), pero la promesa del 30,58 % no es creíble. Sería verdadera solo si la empresa
tuviera, año tras año, otras oportunidades que rindan 30,58 %.

**5.9.** (a) Los flujos van − + −: **dos cambios de signo**. Descartes permite dos TIR o ninguna.
(b) En millones y con $u = 1 + r$: $-20u^2 + 47u - 27{,}3 = 0$, de donde
$u = \dfrac{47 \pm \sqrt{2209 - 2184}}{40} = \dfrac{47 \pm 5}{40}$. Las TIR son **5 %** y **30 %**.
(c) Al 12 %, VAN = **$200.893**: conviene. El VAN es positivo solo para tasas entre 5 % y 30 %: bajo
5 % pesa demasiado la restauración (a tasa 0 el VAN es −$300.000); sobre 30 % pesa demasiado la
inversión inicial. Decir «la TIR es 30 %, mayor que 12 %» o «la TIR es 5 %, menor que 12 %» lleva a
conclusiones opuestas; ninguna de las dos es la rentabilidad del proyecto. (d) Con $28.000.000 el
discriminante queda $2209 - 2240 < 0$: **no hay TIR**. El VAN es negativo a toda tasa (al 12 % da
−$357.143): no conviene, y el VAN lo dice aunque la TIR no exista. (e) TIRM al 12 %: **12,27 %** en
el primer caso (mayor que 12 %, coherente con VAN positivo) y **11,53 %** en el segundo (menor que
12 %). La TIRM siempre existe y es única.

**5.10.** (a) VAC de un ciclo: A $9.984.222 · B $14.911.708. Así comparada, A parece mucho más
barata, pero dura 3 años y B dura 5.
(b) Costo anual equivalente: A **$4.014.804** al año · B **$3.933.671** al año. VAC a perpetuidad
(costo anual entre 0,10): A $40.148.036 · B $39.336.710. **Conviene B**, por unos 81 mil pesos al
año.
(c) En 15 años A se compra 5 veces y B 3 veces: VAC A $30.536.916 · VAC B $29.919.815. Misma
conclusión. Mirar el VAC de un ciclo habría elegido mal.

---

## 13. Caso integrador · la segunda máquina de Estampa Sur

> Valentina es la dueña de Estampa Sur, el taller de serigrafía. Todas las cifras salen de
> `verificacion/caso_valentina.py`.

El taller está copado y Valentina evalúa una **segunda máquina de estampado**. El vendedor le
ofrece pagarla en dos partes: un **pie de $5.550.000** hoy y un **saldo de $8.750.000 al final del
año 3**. La máquina dejaría estos flujos netos y, al final del año 5, se vendería en **$1.800.000**.
Los flujos y el saldo están en pesos nominales (el saldo es una cifra fija), y su costo de
oportunidad nominal es **12 %**.

| Año | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| Pie y saldo | −$5.550.000 | | | −$8.750.000 | | |
| Flujo de operación | | $3.900.000 | $4.200.000 | $4.450.000 | $4.450.000 | $4.450.000 |
| Venta de la máquina | | | | | | $1.800.000 |
| $FC_t$ | −$5.550.000 | $3.900.000 | $4.200.000 | −$4.300.000 | $4.450.000 | $6.250.000 |

**Pregunta.** ¿Conviene la máquina? ¿Qué rentabilidad tiene, y se puede confiar en esa cifra si el
flujo cambia de signo tres veces?

**Desarrollo.**

*VAN.* Descontados al 12 %: $3.482.143, $3.348.214, −$3.060.655, $2.828.055 y $3.546.418. Con el
pie, **VAN = $4.594.175**. Conviene.

*TIR.* Al 41 % el VAN es positivo y al 42 % es negativo; interpolando, **TIR = 41,48 %**.

*¿Es única?* El flujo va − + + − + +: **tres cambios de signo**. Descartes dice que puede haber tres
TIR o una; no dice cuál de los dos casos es. Tres formas de cerrarlo:

1. **La curva del VAN.** Baja en todo el tramo, desde valores enormes cerca de −100 % hasta
   acercarse a −$5.550.000 (el pie) cuando la tasa crece sin límite, y corta el eje una sola vez:

| Tasa | 0 % | 12 % | 20 % | 30 % | 40 % | 50 % | 100 % |
|---|---|---|---|---|---|---|---|
| VAN | $8.950.000 | $4.594.175 | $2.786.002 | $1.219.368 | $131.978 | −$655.350 | −$2.614.062 |

2. **Las raíces del polinomio.** De sus cinco raíces, una es real y positiva (la TIR) y las otras
   cuatro son complejas: no son tasas.
3. **El saldo del proyecto a la TIR.** Al cierre de cada año la máquina le «debe» a Valentina
   −$5.550.000, −$3.951.928, −$1.391.036, −$6.267.985 y −$4.417.705, y en el año 5 el saldo llega a
   cero. Nunca pasa a positivo: la máquina nunca le presta plata a su dueña, es una inversión pura
   y su TIR es única. El pago del saldo en el año 3 hace crecer la deuda del proyecto, pero no
   alcanza a dar vuelta el signo.

*Recuperación.* Simple: el acumulado se vuelve positivo en el año 2, pero el saldo del año 3 lo
devuelve a negativo. La recuperación que cuenta es la definitiva: **3,39 años**. Descontada:
**3,63 años**. Con un flujo así, el período de recuperación necesita la aclaración de cuál cruce se
mira.

*IVAN.* La inversión se paga en dos partes, así que se usa su valor presente: el pie más el saldo
descontado, $5.550.000 + $6.228.077 = $11.778.077. IVAN $= 4{.}594{.}175 / 11{.}778{.}077 =$ **0,39**.
(El VP de los flujos de operación y la venta, $16.372.253, cubre esa inversión con holgura.)

*TIRM al 12 %.* Los egresos (pie y el flujo negativo del año 3) traídos a hoy suman $8.610.655 y los
ingresos llevados al año 5 suman $23.271.423: **TIRM = 22,00 %**.

**Lectura.** La máquina crea $4.594.175 de riqueza y conviene. Su TIR de 41,48 % es única (la
curva, las raíces y el saldo lo confirman), pero no es la rentabilidad que Valentina va a obtener:
para eso tendría que reinvertir lo que genera la máquina al 41 %. Con reinversión al 12 %, la
rentabilidad efectiva es 22,00 %: muy buena, pero la mitad de lo que promete la TIR.

**Lo que pasa a otras unidades.** El saldo de $8.750.000 a 3 años vale hoy **$6.228.077** al 12 %.
La unidad 8 se pregunta cómo asegurar hoy ese pago contra los cambios de tasa, y lo vuelve a
calcular con la tasa del bono que usa para inmunizarlo. La unidad 12 revisa si el 12 % era la tasa
correcta para el riesgo de este proyecto.

---

## 14. Para seguir

**En los libros del ramo.**

- Ross, Westerfield y Jaffe, *Finanzas corporativas* (9.ª ed., 2012): el capítulo sobre el valor
  presente neto y otros criterios de inversión (recuperación, TIR, índice de rentabilidad, TIR
  múltiples y proyectos excluyentes) y el de decisiones de inversión de capital (flujos
  incrementales, costo de oportunidad, inflación, vidas distintas).
- Kelleher y MacCormack, «Internal rate of return: A cautionary tale», *The McKinsey Quarterly*
  (2004). Es corto y conceptual; léelo entero.
- Complementaria: Brealey, Myers y Allen, *Principios de finanzas corporativas* (9.ª ed., 2010),
  los capítulos sobre el VAN frente a otros criterios y sobre decisiones de inversión con el VAN.

**Abierto y gratis.**

- Dahlquist y Knight, *Principles of Finance*, OpenStax (2022), en inglés, capítulo 16, secciones
  16.1 a 16.5 (recuperación, VAN, TIR, métodos alternativos y elección entre proyectos). Licencia
  CC BY-NC-SA 4.0: https://openstax.org/books/principles-finance/pages/16-why-it-matters

**Con el tutor.** Pega `tutor/contexto.md` al inicio de la conversación con cualquier IA y pídele,
por ejemplo: «Dame un flujo con dos cambios de signo, pídeme las TIR y corrígeme la lectura del
VAN paso a paso».
