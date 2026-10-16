---
ramo: Finanzas
unidad: 11
titulo: Portafolios
version: 0.1 (15-10-2026)
requiere: [06-estructura-de-tasas, 10-riesgo-y-utilidad]
alimenta: [12-capm-y-costo-de-capital]
verificacion: verificacion/u11_portafolios.py
---

# Unidad 11 · Portafolios

**Qué vas a poder hacer.** Calcular el retorno esperado y el riesgo de una cartera de dos activos;
medir con la covarianza y la correlación cuánto se acompañan; explicar por qué diversificar baja el
riesgo y por qué no lo baja a cero; encontrar la cartera de mínima varianza y dibujar la frontera
eficiente; agregar un activo libre de riesgo para obtener la línea de mercado de capitales (LMC) y la
cartera tangente, con su razón de Sharpe, y decidir qué parte de la plata va a lo riesgoso según la
aversión al riesgo de cada persona.

**Lo que necesitas antes.** Valor esperado, varianza y desviación estándar de un activo, y la idea de
aversión al riesgo (unidad 10). La tasa libre de riesgo sale de la curva spot (unidad 6). Del cálculo,
derivar una función cuadrática e igualar a cero.

**Tiempo.** Unas 5 horas: 2 de lectura con el ejemplo y 3 de práctica.

---

## 1. La idea

Nadie invierte toda su plata en una sola cosa, y hay una razón matemática para eso. El retorno de una
cartera es un **promedio** de los retornos de sus activos. El riesgo **no** lo es: casi siempre es
menor que el promedio de los riesgos. Esa diferencia es la diversificación, y es lo único que en
finanzas se consigue «gratis».

La unidad avanza en tres pasos:

1. **Dos activos riesgosos.** Cuánto rinde y cuánto se mueve una mezcla, y cuál es la mezcla que menos
   se mueve.
2. **Muchos activos.** Por qué el riesgo baja al agregar activos, pero se estanca en un piso: el riesgo
   sistemático.
3. **Un activo libre de riesgo.** Con un depósito a plazo o un bono del Estado en el menú, la mejor
   cartera riesgosa es la misma para todos, y cada persona solo decide cuánto pone en ella.

**Notación.** $w$ es la fracción de la plata en el activo 1 (y $1-w$ en el activo 2); $E[R_i]$ el
retorno esperado del activo $i$; $\sigma_i$ su desviación estándar; $\sigma_{12}$ la covarianza;
$\rho$ la correlación; $r_f$ la tasa libre de riesgo; $A$ el coeficiente de aversión al riesgo; $y$ la
fracción de la riqueza que va a la cartera riesgosa.

---

## 2. Covarianza y correlación

La **covarianza** mide si dos retornos se desvían de su media hacia el mismo lado. Con escenarios:

$$\sigma_{12} = \sum_s p_s\,\big(R_{1s} - E[R_1]\big)\big(R_{2s} - E[R_2]\big)$$

Si en los escenarios en que A sube B también sube, los productos son positivos y la covarianza es
positiva. Su problema es la unidad («porcentaje al cuadrado»): no dice si 0{,}009 es mucho o poco. Por
eso se normaliza y se obtiene la **correlación**:

$$\rho_{12} = \frac{\sigma_{12}}{\sigma_1\,\sigma_2} \qquad -1 \le \rho_{12} \le 1 \qquad\Longleftrightarrow\qquad \sigma_{12} = \rho_{12}\,\sigma_1\,\sigma_2$$

| $\rho$ | Qué significa | Ejemplo cotidiano |
|---|---|---|
| $+1$ | se mueven siempre juntos, en la misma proporción | dos fondos que copian el mismo índice |
| entre 0 y 1 | tienden a ir juntos, pero no siempre | dos acciones chilenas de sectores distintos |
| $0$ | no hay relación lineal | el precio del pan y la lluvia en otra región |
| negativo | cuando uno sube, el otro tiende a bajar | una aerolínea y una petrolera ante un alza del crudo |
| $-1$ | espejo perfecto | solo existe en el papel |

> **Correlación no es causa.** Que dos activos se muevan al revés en una crisis puede deberse a que
> ambos responden a lo mismo (el precio del petróleo). Esa cobertura puede desaparecer cuando cambia la
> causa común. Diversificar de verdad es combinar activos que dependen de cosas distintas.

---

## 3. Cartera de dos activos

### Retorno esperado: promedio ponderado

$$E[R_P] = w\,E[R_1] + (1-w)\,E[R_2]$$

### Varianza: aquí está la diversificación

$$\sigma_P^2 = w^2\sigma_1^2 + (1-w)^2\sigma_2^2 + 2\,w\,(1-w)\,\sigma_{12}$$

Los dos primeros términos son siempre positivos. El tercero lleva la covarianza y es el único que
puede restar. Escrito con la correlación, $2w(1-w)\rho\,\sigma_1\sigma_2$, se ve que todo depende de
$\rho$.

**Los dos extremos.**

- Con $\rho = +1$ la varianza es un cuadrado perfecto: $\sigma_P = w\sigma_1 + (1-w)\sigma_2$. El riesgo
  es el promedio ponderado; mezclar no sirve para nada.
- Con $\rho = -1$ queda $\sigma_P = |w\sigma_1 - (1-w)\sigma_2|$, que se anula en
  $w = \dfrac{\sigma_2}{\sigma_1+\sigma_2}$. Una cartera sin riesgo hecha con dos activos riesgosos.

Para cualquier $\rho < 1$ el riesgo de la cartera queda **por debajo** del promedio ponderado de los
riesgos. Nunca por encima: combinar no agrega riesgo, solo lo redistribuye y, si $\rho<1$, lo achica.

### Cartera de mínima varianza (PMV)

Se reemplaza $1-w$ y se deriva $\sigma_P^2$ respecto de $w$:

$$\frac{d\sigma_P^2}{dw} = 2w\sigma_1^2 - 2(1-w)\sigma_2^2 + 2(1-2w)\sigma_{12} = 0 \quad\Longrightarrow\quad w_{\min} = \frac{\sigma_2^2 - \sigma_{12}}{\sigma_1^2 + \sigma_2^2 - 2\sigma_{12}}$$

**Lectura.** Si la covarianza es chica, la PMV pone algo del activo más riesgoso aunque solo se busque
bajar el riesgo: un poco de un activo que se mueve distinto aquieta la mezcla. Si $w_{\min}$ resulta
negativo o mayor que 1, la PMV pide **venta corta** (vender un activo que no se tiene para comprar más
del otro). Si la venta corta no está permitida, la PMV queda en el extremo 0 o 1.

### La frontera eficiente

Al mover $w$ de 0 a 1 la cartera dibuja una curva en el plano riesgo ($\sigma$, eje horizontal)
contra retorno ($E[R]$, eje vertical). Con $\rho<1$ la curva se dobla hacia la izquierda y su punto
más a la izquierda es la PMV.

- **Tramo eficiente:** desde la PMV hacia arriba. Para cada riesgo es el mayor retorno posible.
- **Tramo ineficiente:** bajo la PMV. Cada cartera ahí está **dominada**: hay otra con el mismo riesgo
  y más retorno.

Nadie racional elige el tramo ineficiente, sea cual sea su aversión al riesgo. Cuál punto del tramo
eficiente elige cada persona depende de sus preferencias (sección 6).

### Con más de dos activos

La PMV se plantea como un problema de optimización:

$$\min_{w_1,\dots,w_n}\; \sigma_P^2 = \sum_i\sum_j w_i w_j \sigma_{ij} \qquad \text{s. a.} \quad \sum_i w_i = 1$$

Con Lagrange se llega a $2\sum_j \sigma_{ij}w_j = \lambda$ para todo $i$: en la PMV, cada activo aporta
lo mismo al riesgo en el margen. En matrices, $w \propto \Sigma^{-1}\mathbf 1$. Agregar un activo
nuevo nunca empeora la frontera: en el peor caso se le da peso cero.

---

## 4. Diversificación con muchos activos

Con $n$ activos de igual peso ($1/n$), todos con la misma varianza $\sigma^2$ y la misma correlación
$\rho$ entre cada par:

$$\sigma_P^2 = \frac{\sigma^2}{n} + \Big(1 - \frac{1}{n}\Big)\rho\,\sigma^2 = \underbrace{\rho\,\sigma^2}_{\text{no baja con } n} + \underbrace{\frac{(1-\rho)\,\sigma^2}{n}}_{\text{desaparece al crecer } n}$$

Al crecer $n$ el riesgo cae rápido al principio y después se estanca en $\sigma\sqrt{\rho}$. Dos
riesgos distintos:

| Riesgo | Otros nombres | Origen | ¿Se diversifica? |
|---|---|---|---|
| **No sistemático** | propio, específico, diversificable | lo que le pasa a una empresa: una huelga, un incendio, un fraude, un mal lanzamiento | sí: en una cartera grande los golpes de unas empresas se compensan con los de otras |
| **Sistemático** | de mercado, no diversificable | lo que le pasa a todas a la vez: tasas, ciclo económico, tipo de cambio, crisis | no: no hay dónde esconderse |

**La consecuencia que abre la unidad 12.** Si el riesgo propio se elimina gratis diversificando, el
mercado no paga por soportarlo. Solo se compensa el riesgo sistemático. Por eso la volatilidad total de
una acción no dice cuánto retorno exigirle; lo dice cuánto se mueve con el mercado.

---

## 5. Activo libre de riesgo y línea de mercado de capitales

El activo libre de riesgo rinde $r_f$ con certeza: $\sigma_f = 0$ y covarianza cero con todo. En la
práctica, un depósito a plazo o un bono del Estado al plazo de la inversión (la tasa spot de la unidad
6).

### Combinar $r_f$ con una cartera riesgosa P

Si $y$ va a P y $1-y$ a $r_f$:

$$E[R_C] = r_f + y\,\big(E[R_P] - r_f\big) \qquad \sigma_C = y\,\sigma_P$$

El riesgo crece en línea recta con $y$ porque $r_f$ no varía ni covaría. Despejando $y = \sigma_C/\sigma_P$:

$$E[R_C] = r_f + \underbrace{\frac{E[R_P] - r_f}{\sigma_P}}_{\text{razón de Sharpe de P}}\,\sigma_C$$

Toda combinación es una **recta** que parte en $r_f$ y pasa por P. Con $y>1$ se pide prestado a $r_f$
para poner más del 100 % en P (cartera apalancada).

### La razón de Sharpe y la cartera tangente

$$S_P = \frac{E[R_P] - r_f}{\sigma_P}$$

es el **premio por unidad de riesgo**: cuánto retorno sobre $r_f$ entrega cada punto de desviación. La
mejor recta es la más empinada, la que toca la frontera eficiente justo en un punto: la **cartera
tangente** T. Esa recta es la **línea de mercado de capitales (LMC)**:

$$E[R_C] = r_f + S_T\,\sigma_C$$

Ninguna otra cartera riesgosa, combinada con $r_f$, ofrece más retorno para el mismo riesgo. Si todos
los inversionistas ven los mismos datos, todos eligen la misma T y, en equilibrio, T es la **cartera de
mercado**.

**Con dos activos**, maximizar $S$ respecto de $w$ da (con $a_i = E[R_i] - r_f$):

$$w_T = \frac{a_1\,\sigma_2^2 - a_2\,\sigma_{12}}{a_1\,\sigma_2^2 + a_2\,\sigma_1^2 - (a_1 + a_2)\,\sigma_{12}}$$

**Con cualquier número de activos**, la condición de óptimo es un sistema lineal: se buscan $Z_i$
tales que

$$E[R_i] - r_f = \sum_j Z_j\,\sigma_{ij} \quad \text{para cada } i, \qquad w_{T,i} = \frac{Z_i}{\sum_j Z_j}$$

Se lee así: en la cartera tangente, el premio de cada activo es proporcional a su covarianza con la
cartera. Un activo que paga poco por lo que agrega de riesgo pierde peso; uno que paga mucho, gana.

---

## 6. Cuánto poner en lo riesgoso · aversión al riesgo

La unidad 10 midió la aversión al riesgo con funciones de utilidad. Para elegir carteras se usa una
aproximación de media y varianza:

$$U = E[R_C] - \tfrac{1}{2}\,A\,\sigma_C^2$$

$A$ mide cuánto castiga la persona la varianza: con $A=0$ solo mira el retorno; con $A$ alto pide mucho
premio por cada punto de riesgo. Reemplazando $E[R_C]$ y $\sigma_C$ de la sección 5 y derivando
respecto de $y$:

$$\frac{dU}{dy} = \big(E[R_T] - r_f\big) - A\,\sigma_T^2\,y = 0 \quad\Longrightarrow\quad y^* = \frac{E[R_T] - r_f}{A\,\sigma_T^2}$$

| Si | Entonces |
|---|---|
| $y^* < 1$ | parte en T y el resto en $r_f$ (presta al Estado o al banco) |
| $y^* = 1$ | todo en T |
| $y^* > 1$ | pide prestado a $r_f$ e invierte más del 100 % en T |

**Teorema de separación.** La decisión se parte en dos. Primero, **qué** cartera riesgosa: T, igual
para todos, porque solo depende de los datos del mercado. Después, **cuánto** poner en ella: $y^*$,
distinto para cada persona, porque depende de $A$. Un inversionista conservador y uno agresivo tienen
la misma mezcla dentro de lo riesgoso; se distinguen en cuánto de su plata va ahí.

En el gráfico riesgo contra retorno, las curvas de indiferencia de una persona muy aversa son
empinadas: tocan la LMC cerca de $r_f$. Las de una persona poco aversa son más planas y la tocan lejos,
incluso más allá de T.

---

## 7. Ejemplo resuelto · Martina y la plata de su auto

Martina vendió su auto en $6.000.000 y no va a necesitar esa plata durante un año. Su banco le ofrece
dos fondos mutuos (ficticios) y un depósito a plazo a un año al 4,15 %.

| | Retorno esperado | Desviación estándar |
|---|---|---|
| (1) Fondo Andino Acciones | 11,5 % | 21 % |
| (2) Fondo Austral Balanceado | 7,2 % | 10 % |

La correlación entre los fondos es 0,28 y Martina tiene una aversión al riesgo $A = 4$.

**Paso 1 · Covarianza.** $\sigma_{12} = \rho\,\sigma_1\sigma_2 = 0{,}28 \times 0{,}21 \times 0{,}10 = 0{,}00588$.

**Paso 2 · Una mezcla mitad y mitad.**

$$E[R_P] = 0{,}5 \times 11{,}5\,\% + 0{,}5 \times 7{,}2\,\% = 9{,}35\,\%$$

$$\sigma_P^2 = 0{,}25 \times 0{,}0441 + 0{,}25 \times 0{,}01 + 2 \times 0{,}25 \times 0{,}00588 = 0{,}016465 \qquad \sigma_P = 12{,}83\,\%$$

El promedio de los riesgos sería 15,50 %. La mezcla se mueve 2,67 puntos menos sin resignar retorno:
eso es la diversificación.

**Paso 3 · Mínima varianza.**

$$w_{\min} = \frac{0{,}01 - 0{,}00588}{0{,}0441 + 0{,}01 - 2 \times 0{,}00588} = 9{,}73\,\% \text{ en Andino}$$

La PMV rinde 7,62 % con un riesgo de 9,80 %. Fíjate: **menos riesgo que el fondo balanceado solo**
(10 %), y eso agregando un poco del fondo más volátil. Como no se mueven juntos, ese pedazo de acciones
compensa parte de los vaivenes del balanceado.

**Paso 4 · Cartera tangente con el depósito.** Los premios sobre $r_f$ son $a_1 = 0{,}0735$ y
$a_2 = 0{,}0305$.

$$w_T = \frac{0{,}0735 \times 0{,}01 - 0{,}0305 \times 0{,}00588}{0{,}0735 \times 0{,}01 + 0{,}0305 \times 0{,}0441 - 0{,}104 \times 0{,}00588} = \frac{0{,}000556}{0{,}001469} = 37{,}84\,\%$$

Por el sistema se llega a lo mismo: resolviendo $0{,}0735 = 0{,}0441\,Z_1 + 0{,}00588\,Z_2$ y
$0{,}0305 = 0{,}00588\,Z_1 + 0{,}01\,Z_2$ salen $Z_1 = 1{,}3672$ y $Z_2 = 2{,}2461$, y
$w_T = 1{,}3672 / 3{,}6133 = 37{,}84\,\%$.

La cartera tangente tiene 37,84 % en Andino y 62,16 % en Austral, rinde 8,83 % y su riesgo es 11,38 %.

**Paso 5 · Sharpe y LMC.**

$$S_T = \frac{8{,}83\,\% - 4{,}15\,\%}{11{,}38\,\%} = 0{,}4111 \qquad S_1 = 0{,}3500 \qquad S_2 = 0{,}3050$$

La mezcla paga más por unidad de riesgo que cualquiera de los fondos solos. La LMC de Martina es
$E[R_C] = 4{,}15\,\% + 0{,}4111\,\sigma_C$.

**Paso 6 · Cuánto pone en lo riesgoso.**

$$y^* = \frac{0{,}0883 - 0{,}0415}{4 \times 0{,}1138^2} = 90{,}33\,\%$$

| Destino | Monto |
|---|---|
| Cartera tangente | $5.419.922 |
| · de eso, en Fondo Andino Acciones | $2.050.781 |
| · de eso, en Fondo Austral Balanceado | $3.369.141 |
| Depósito a plazo | $580.078 |

Su cartera completa rinde 8,37 % esperado con un riesgo de 10,28 %. Su utilidad es
$U = 0{,}0837 - \tfrac12 \times 4 \times 0{,}1028^2 = 0{,}0626$, mayor que con todo en la tangente
($0{,}0624$) y que con todo en el depósito ($0{,}0415$).

**Cómo se lee.**

- Martina no elige entre «el fondo de acciones» y «el balanceado». Elige **la mezcla de mayor Sharpe**
  y después decide cuánto riesgo tomar moviendo $y$.
- Si su hermano, más arriesgado, tuviera el mismo menú, armaría **la misma** mezcla de 37,84 % y
  62,16 % dentro de lo riesgoso. Solo cambiaría cuánto deja en el depósito.
- El ahorro de riesgo existe porque la correlación es 0,28, no porque sea negativa. Basta con que sea
  menor que 1.

---

## 8. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Promediar las desviaciones para obtener el riesgo de la cartera | El promedio solo vale con $\rho = 1$. Pasa por la varianza y la covarianza |
| Olvidar el 2 del término cruzado, o usar $\rho$ donde va $\sigma_{12}$ | $2w(1-w)\sigma_{12}$ con $\sigma_{12} = \rho\sigma_1\sigma_2$ |
| Mezclar porcentajes y decimales en la varianza ($21^2 = 441$ junto a $0{,}01$) | Todo en decimales antes de elevar al cuadrado |
| Creer que la PMV es la mejor cartera | Es la de menor riesgo; la de mejor premio por riesgo es la tangente |
| Elegir el activo de mayor Sharpe en vez de la tangente | La mezcla supera a cada activo solo (paso 5) |
| Pensar que la persona más aversa tiene otra mezcla riesgosa | Con $r_f$ disponible, todos tienen T; cambia $y^*$ |
| Leer $y^* > 1$ como un error | Significa pedir prestado a $r_f$ |

---

## 9. Práctica

Diez ejercicios: 11.1 a 11.4 básicos, 11.5 a 11.8 intermedios, 11.9 y 11.10 de desafío. Dos son
**comentes** (11.4 y 11.10): se responden Verdadero, Falso o Incierto con un argumento, no con una
palabra. Las pautas están en la sección 10.

**11.1 · Dos acciones, pesos dados (básico).** Inviertes 30 % en Minera Norte ($E[R] = 14\,\%$,
$\sigma = 30\,\%$) y 70 % en Eléctrica Costa ($E[R] = 8\,\%$, $\sigma = 15\,\%$), con correlación 0,20.
Calcula la covarianza, el retorno y el riesgo de la cartera, y cuántos puntos de riesgo te ahorra
diversificar frente al promedio ponderado de las desviaciones.

**11.2 · Covarianza desde escenarios (básico).** Para el próximo año se prevén tres escenarios:

| Escenario | Probabilidad | Retorno A | Retorno B |
|---|---|---|---|
| Recesión | 0,25 | −12 % | 6 % |
| Normal | 0,50 | 10 % | 4 % |
| Auge | 0,25 | 28 % | 1 % |

Calcula el retorno esperado y la desviación de cada activo, su covarianza y su correlación. Luego
calcula la desviación de una cartera mitad y mitad de dos formas: con la fórmula y armando el retorno
de la cartera en cada escenario. Tienen que coincidir.

**11.3 · Correlación perfecta (básico).** El activo 1 tiene $E[R] = 13\,\%$ y $\sigma = 24\,\%$; el 2,
$E[R] = 6\,\%$ y $\sigma = 9\,\%$. (a) Si $\rho = -1$, ¿qué pesos dan una cartera sin riesgo y cuánto
rinde? (b) Con esos mismos pesos y $\rho = +1$, ¿cuál es el riesgo? (c) Si el depósito a plazo pagara
menos que lo que rinde la cartera de (a), ¿qué harías?

**11.4 · Comente (básico).** «Si dos acciones tienen correlación positiva, por ejemplo 0,6, combinarlas
no reduce el riesgo. Para diversificar se necesitan activos con correlación negativa.»

**11.5 · Frontera de dos acciones (intermedio).** Viña del Valle: $E[R] = 10\,\%$, $\sigma = 18\,\%$.
Salmonera Fiordo: $E[R] = 15\,\%$, $\sigma = 32\,\%$. Correlación 0,10. Calcula el retorno y el riesgo
con 0 %, 25 %, 50 %, 75 % y 100 % en la viña; encuentra la PMV; di qué tramo es eficiente y si
conviene tener solo acciones de la viña.

**11.6 · Cartera tangente y LMC (intermedio).** Con las acciones de 11.5 y una tasa libre de riesgo de
4,5 %, calcula la cartera tangente (con la fórmula y con el sistema de $Z$), su retorno, su riesgo y su
Sharpe. Compara con el Sharpe de cada acción sola. Escribe la LMC y di qué retorno y qué fracción en
la tangente tiene una cartera sobre la LMC con riesgo de 15 %.

**11.7 · Dos inversionistas, una tangente (intermedio).** Rocío ($A = 2$) y Hernán ($A = 7$) tienen
$10.000.000 cada uno y el menú de 11.6. Calcula $y^*$ de cada uno, cuánto ponen en cada acción y en el
activo libre de riesgo, y el retorno esperado y el riesgo de su cartera completa. ¿Quién pide prestado?

**11.8 · Cuántas acciones bastan (intermedio).** Todas las acciones de un mercado tienen
$\sigma = 35\,\%$ y una correlación de 0,25 entre cada par. Calcula el riesgo de una cartera de igual
peso con 1, 2, 5, 10 y 50 acciones, el piso al que tiende y qué fracción de la varianza es sistemática
en cada caso.

**11.9 · Tres activos y mínima varianza (desafío).** Tres activos con $E[R]$ de 11 %, 13 % y 5 %;
desviaciones de 20 %, 25 % y 15 %; correlaciones $\rho_{12} = 0{,}5$, $\rho_{13} = -0{,}2$ y
$\rho_{23} = 0{,}1$. Se permite la venta corta. (a) Plantea el problema de mínima varianza con su
función objetivo y su restricción. (b) Resuélvelo. (c) Compara con la PMV que se arma solo con los
activos 1 y 2, y explica la diferencia con un gráfico de fronteras.

**11.10 · Comente (desafío).** «Un inversionista muy averso al riesgo debería armar la parte riesgosa
de su cartera con más del activo menos volátil que un inversionista agresivo.»

---

## 10. Pautas

**11.1.** $\sigma_{12} = 0{,}20 \times 0{,}30 \times 0{,}15 = 0{,}0090$. $E[R_P] = 9{,}80\,\%$.
$\sigma_P^2 = 0{,}09 \times 0{,}09 + 0{,}49 \times 0{,}0225 + 2 \times 0{,}21 \times 0{,}0090$, y
$\sigma_P = 15{,}13\,\%$. El promedio ponderado de las desviaciones es 19,50 %: diversificar ahorra
4,37 puntos. Fíjate que la cartera tiene casi el riesgo de la eléctrica sola (15 %) pero rinde más.

**11.2.** $E[R_A] = 9{,}00\,\%$ y $E[R_B] = 3{,}75\,\%$; $\sigma_A = 14{,}18\,\%$ y
$\sigma_B = 1{,}79\,\%$. Covarianza: $0{,}25(-0{,}21)(0{,}0225) + 0{,}50(0{,}01)(0{,}0025) + 0{,}25(0{,}19)(-0{,}0275) = -0{,}002475$.
Correlación: $\rho = -0{,}9778$, casi un espejo. La cartera mitad y mitad rinde −3 %, 7 % y 14,5 % en
los tres escenarios: retorno esperado 6,38 % y desviación 6,22 %, por los dos caminos. Lectura: B paga
poco, pero sube justo cuando A cae; por eso la mezcla tiene menos de la mitad del riesgo de A.

**11.3.** (a) $w_1 = 9/(24+9) = 27{,}27\,\%$ y $w_2 = 72{,}73\,\%$; rinde 7,91 % sin riesgo. (b) Con
$\rho = +1$ el riesgo es el promedio: 13,09 %. (c) Si el depósito paga menos que 7,91 %, hay arbitraje:
pedir prestado al depósito e invertir en la cartera sin riesgo deja una ganancia segura sin poner plata
propia. En un mercado en equilibrio eso no dura: los precios se ajustan hasta que la cartera sin riesgo
rinda lo mismo que $r_f$. Por eso en la realidad no existen activos con $\rho = -1$ que paguen más que
$r_f$.

**11.4. Falso.** El riesgo de la cartera queda bajo el promedio ponderado de los riesgos siempre que
$\rho < 1$, no solo cuando es negativo. El término $2w(1-w)\rho\sigma_1\sigma_2$ con $\rho = 0{,}6$ es
positivo, pero más chico que con $\rho = 1$, que es el caso en que el riesgo sería el promedio. Lo que
cambia con el signo es **cuánto** se diversifica: con correlación negativa el ahorro es mayor y con
$\rho = -1$ el riesgo puede llegar a cero. El ejercicio 11.1 lo muestra con $\rho = 0{,}20$: un ahorro
de 4,37 puntos. Y en una cartera grande lo que manda es la covarianza promedio: con correlaciones
positivas el riesgo no baja a cero, se estanca en el riesgo sistemático (ejercicio 11.8). Diversificar
sirve; lo que no hace es eliminar todo el riesgo.

**11.5.** $\sigma_{12} = 0{,}00576$.

| En la viña | Retorno | Riesgo |
|---|---|---|
| 0 % | 15,00 % | 32,00 % |
| 25 % | 13,75 % | 24,86 % |
| 50 % | 12,50 % | 19,13 % |
| 75 % | 11,25 % | 16,37 % |
| 100 % | 10,00 % | 18,00 % |

PMV: 78,39 % en la viña, con retorno 11,08 % y riesgo 16,32 %. El tramo eficiente va desde la PMV
hacia la salmonera. **Tener solo la viña no conviene:** la PMV tiene menos riesgo (16,32 % contra 18 %)
y más retorno (11,08 % contra 10 %). Esa cartera está dominada; nadie racional la elige.

**11.6.** Con $a_1 = 0{,}055$ y $a_2 = 0{,}105$, la tangente pone 61,97 % en la viña y el resto en la
salmonera; rinde 11,90 % con riesgo 17,31 %. Por el sistema, $Z_1 = 1{,}5305$ y $Z_2 = 0{,}9393$, y
$1{,}5305/2{,}4698$ da el mismo peso. Sharpe de la tangente: 0,4276; de la viña sola, 0,3056; de la
salmonera sola, 0,3281. LMC: $E[R_C] = 4{,}5\,\% + 0{,}4276\,\sigma_C$. Con $\sigma_C = 15\,\%$ la
cartera rinde 10,91 % y tiene 86,65 % en la tangente y el resto en $r_f$.

**Lectura.** La salmonera tiene mejor Sharpe que la viña, y aun así la tangente pone más en la viña.
El Sharpe de cada acción sola no decide los pesos: decide cuánto premio aporta cada una por el riesgo
que **agrega a la mezcla**, y la viña, por ser menos volátil y poco correlacionada, agrega poco.

**11.7.**

| | Rocío ($A = 2$) | Hernán ($A = 7$) |
|---|---|---|
| $y^*$ | 123,49 % | 35,28 % |
| En la tangente | $12.349.211 | $3.528.346 |
| · Viña del Valle | $7.652.723 | $2.186.492 |
| · Salmonera Fiordo | $4.696.487 | $1.341.854 |
| Activo libre de riesgo | pide prestado $2.349.211 | presta $6.471.654 |
| Retorno esperado | 13,64 % | 7,11 % |
| Riesgo | 21,38 % | 6,11 % |

Rocío pide prestado: su $y^*$ pasa de 100 %. Los dos tienen 61,97 % de su parte riesgosa en la viña.

**11.8.**

| Acciones | Riesgo de la cartera | Varianza sistemática |
|---|---|---|
| 1 | 35,00 % | 25,0 % |
| 2 | 27,67 % | 40,0 % |
| 5 | 22,14 % | 62,5 % |
| 10 | 19,95 % | 76,9 % |
| 50 | 18,02 % | 94,3 % |

El piso es $\sqrt{0{,}25} \times 35\,\% = 17{,}50\,\%$. Con 10 acciones ya se eliminó la mayor parte
de lo que se puede eliminar; pasar de 10 a 50 ahorra menos de 2 puntos. Lo que queda es riesgo
sistemático, y eso no se diversifica con más acciones del mismo mercado (sí, en parte, con otros
mercados u otras clases de activos).

**11.9.** (a) $\min\ \sigma_P^2 = \sum_i\sum_j w_iw_j\sigma_{ij}$ s. a. $w_1+w_2+w_3 = 1$. La matriz de
covarianzas es

$$\Sigma = \begin{pmatrix} 0{,}04 & 0{,}025 & -0{,}006 \\ 0{,}025 & 0{,}0625 & 0{,}0037 \\ -0{,}006 & 0{,}0037 & 0{,}0225 \end{pmatrix}$$

(b) Con Lagrange, $2\Sigma w = \lambda\mathbf 1$: se resuelve $\Sigma z = \mathbf 1$ y se normaliza.
Pesos: 38,68 %, -0,64 % y 61,96 %. Retorno 7,27 %, riesgo 10,77 %. Comprobación: $2\Sigma w$ da
0,0232 en las tres filas, y $\lambda/2 = 0{,}0116$ es justo la varianza mínima.
(c) Solo con 1 y 2, la PMV pone 71,43 % en el 1, rinde 11,57 % y tiene riesgo 18,90 %. El tercer
activo, con correlación negativa con el 1, corre toda la frontera hacia la izquierda: la nueva PMV
tiene casi la mitad del riesgo. El activo 2 queda levemente vendido corto porque, con el 3 disponible,
solo agrega riesgo. En el gráfico, la frontera de tres activos envuelve a la de dos: para cada retorno
ofrece igual o menos riesgo, nunca más.

**11.10. Falso, si existe un activo libre de riesgo.** Por el teorema de separación, la mejor cartera
riesgosa es la tangente, y es la misma para todos porque depende solo de los retornos esperados, los
riesgos, las correlaciones y $r_f$, no de las preferencias. La aversión al riesgo decide **cuánto** de
la riqueza va a esa cartera ($y^*$), no **qué** hay dentro. En 11.7, Hernán ($A = 7$) pone 35,28 % en lo
riesgoso y Rocío ($A = 2$) 123,49 %, pero ambos tienen 61,97 % de esa parte en la viña. **Sin activo libre
de riesgo** la afirmación se vuelve razonable: cada persona elige un punto de la frontera eficiente y el
más averso elige uno más cerca de la PMV, que tiene más del activo menos volátil. Así que la respuesta
completa es: falso con $r_f$, verdadero sin él.

---

## 11. Caso integrador · Valentina invierte con riesgo

> Este caso sigue a Valentina, dueña de Estampa Sur, por todo el ramo. En la unidad 10 decidió que una
> inversión riesgosa le convenía más que el depósito. Ahora arma la cartera. La tasa libre de riesgo es
> la spot a un año de la unidad 6. Todas las cifras salen de `verificacion/caso_valentina.py`.

| | Retorno esperado | Desviación estándar |
|---|---|---|
| Textil Andes (acción ficticia) | 13,4 % | 26 % |
| Fondo IPSA (ficticio) | 9,8 % | 17,5 % |

Correlación 0,42; tasa libre de riesgo 4,80 %; aversión al riesgo de Valentina, $A = 4$.

> **Por qué A = 4 y no la utilidad logarítmica de la unidad 10.** La utilidad logarítmica equivale,
> en media y varianza, a una aversión cercana a 1. Allá Valentina decidía con plata que podía
> arriesgar; acá invierte parte del ahorro del pie del departamento, que tiene fecha y monto fijos.
> Con esa plata es más aversa, y por eso el caso usa $A = 4$. Una misma persona puede tener
> aversiones distintas para plata con destinos distintos (la unidad 10 lo trata en la sección
> «No somos Spock»).

**Desarrollo.**

| Cartera | En Textil Andes | En el fondo | Retorno | Riesgo | Sharpe |
|---|---|---|---|---|---|
| Solo Textil Andes | 100 % | 0 % | 13,4 % | 26 % | 0,3308 |
| Solo Fondo IPSA | 0 % | 100 % | 9,8 % | 17,5 % | 0,2857 |
| Mínima varianza | 19,19 % | 80,81 % | 10,49 % | 16,86 % | |
| Tangente | 49,15 % | 50,85 % | 11,57 % | 18,38 % | 0,3682 |

La covarianza es $0{,}42 \times 0{,}26 \times 0{,}175 = 0{,}01911$. La PMV tiene un riesgo de 16,86 %,
bajo el 19,13 % que daría promediar las desviaciones con esos pesos y bajo el 17,5 % del fondo solo.

**Cuánto pone en lo riesgoso.**

$$y^* = \frac{0{,}1157 - 0{,}0480}{4 \times 0{,}1838^2} = 50{,}07\,\%$$

Si invierte los $5.000.000 de la unidad 10:

| Destino | Monto |
|---|---|
| Cartera tangente | $2.503.500 |
| · Textil Andes | $1.230.361 |
| · Fondo IPSA | $1.273.140 |
| Activo libre de riesgo (bono cero a un año) | $2.496.500 |

Su cartera completa rinde 8,19 % esperado con un riesgo de 9,21 %.

**Lectura.** Valentina no se queda con Textil Andes aunque tenga el mejor Sharpe individual: mezclada
con el fondo paga 0,3682 por unidad de riesgo, más que cualquiera de las dos sola. Con su aversión,
pone la mitad en esa mezcla y la otra mitad en el bono cero cupón. Si quisiera más retorno no cambiaría
la mezcla: subiría $y$.

**Lo que pasa a la unidad 12.** La tasa libre de riesgo (4,80 %) y la idea de que solo se paga el riesgo
que no se diversifica. La unidad 12 estima la beta de Textil Andes y pregunta qué retorno le exige el
mercado.

---

## 12. Para seguir

**En los libros del ramo.**

- Ross, Westerfield y Jaffe, *Finanzas corporativas* (9.ª ed., 2012): el programa fija los capítulos
  10 y 11 para riesgo, rendimiento y carteras, y el 13 para la segunda parte de la Unidad III.
- Brealey, Myers y Allen, *Principios de finanzas corporativas* (9.ª ed., 2010): el programa fija los
  capítulos 8 y 9, y el 10 para carteras con activo libre de riesgo.
- Bodie, Kane y Marcus, *Investments* (bibliografía complementaria): el desarrollo más completo de la
  asignación entre activo libre de riesgo y cartera riesgosa con aversión al riesgo.

**Abierto y gratis.**

- Dahlquist y Knight, *Principles of Finance*, OpenStax (2022), en inglés. Capítulo 15, secciones
  15.1 (riesgo y retorno de un activo) y 15.2 (riesgo y retorno de varios activos):
  https://openstax.org/details/books/principles-finance

**Con el tutor.** Pega `tutor/contexto.md` al inicio de la conversación y pídele, por ejemplo: «Dame
dos activos con su correlación, hazme calcular la PMV y la tangente, y corrígeme paso a paso».
