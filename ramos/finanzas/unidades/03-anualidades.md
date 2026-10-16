---
ramo: Finanzas
unidad: 3
titulo: Anualidades, perpetuidades y gradientes
version: 0.1 (15-10-2026)
requiere: [01-valor-del-dinero, 02-tasas-de-interes]
alimenta: [04-creditos-y-amortizacion, 05-van-y-tir]
verificacion: verificacion/u03_anualidades.py
---

# Unidad 3 · Anualidades, perpetuidades y gradientes

**Qué vas a poder hacer.** Reconocer cuándo una serie de pagos es una anualidad y valorarla de una
vez, en el presente o en el futuro; distinguir la anualidad vencida de la anticipada y de la
diferida; valorar una perpetuidad, con y sin crecimiento; valorar series que crecen en porcentaje
(gradiente geométrica, o anualidad creciente) o en un monto fijo (gradiente aritmética); y armar un
plan de ahorro por tramos sin olvidar el −1 de la fórmula de valor futuro.

**Lo que necesitas antes.** Llevar un monto de una fecha a otra (unidad 1) y pasar una tasa de una
frecuencia a otra (unidad 2). Si la tasa es anual y los pagos mensuales, primero se resuelve eso.

**Tiempo.** Unas 4,5 horas: 2 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. La idea

Una serie de pagos son varios montos únicos repartidos en el tiempo. Se pueden valorar uno por uno
(unidad 1), pero cuando cumplen cuatro condiciones existe un atajo. Esa serie se llama **anualidad**:

| Condición | Qué exige |
|---|---|
| Monto constante | Todos los pagos son iguales: $A$ |
| Tasa constante | La misma tasa $i$ en todos los períodos |
| Periodicidad constante | Los pagos están separados por el mismo intervalo |
| Plazo definido | Hay un último pago: son $n$ pagos |

**El nombre engaña.** «Anualidad» no quiere decir anual. Una cuota mensual, un arriendo trimestral o
un depósito semanal son anualidades si cumplen las cuatro condiciones.

El resto de la unidad sale de soltar una condición a la vez:

- Si el plazo no termina, es una **perpetuidad**.
- Si el monto crece en un porcentaje fijo, es una **gradiente geométrica** (o anualidad creciente).
- Si el monto crece en una cantidad fija, es una **gradiente aritmética**.
- Si la serie cambia de monto o de tasa a mitad de camino, son **varias anualidades seguidas**
  (tramos), y cada una se valora por separado.

> **La regla de oro.** La tasa y los pagos tienen que estar en la misma unidad de tiempo. Si los
> pagos son mensuales, $i$ es mensual y $n$ se cuenta en meses. La mitad de los errores de esta
> unidad empiezan ahí.

---

## 2. Anualidad vencida · valor presente y valor futuro

En la **vencida** el primer pago cae al final del primer período (en $t = 1$) y el último en
$t = n$. Es el caso por defecto: cuotas de un crédito, depósitos a fin de mes, dividendos.

### Valor presente

Traer cada pago a $t = 0$ y sumar da una serie geométrica que se resume así:

$$VP = A \cdot \frac{1 - (1+i)^{-n}}{i}$$

El cociente se llama **factor de valor presente** de la anualidad. Una forma de verlo sin
memorizarlo: $n$ pagos son una perpetuidad que parte hoy (vale $A/i$) menos la perpetuidad que
empezaría después del pago $n$ (vale $A/i$ en $t = n$, o sea $\frac{A/i}{(1+i)^n}$ hoy):

$$VP = \frac{A}{i} - \frac{A/i}{(1+i)^{n}} = \frac{A}{i}\left[1 - (1+i)^{-n}\right]$$

### Valor futuro · y el −1

El valor futuro es lo que se junta en $t = n$, justo después del último pago. Cada pago capitaliza
los períodos que le quedan: el primero capitaliza $n-1$ veces y **el último no capitaliza nada**,
porque entra el mismo día en que se mide.

$$VF = A\left[(1+i)^{n-1} + \dots + (1+i) + 1\right] = A \cdot \frac{(1+i)^n \;\boxed{-\;1}}{i}$$

**Ese −1 no es un detalle.** Sin él queda $A(1+i)^n/i$, que es el valor en $t = n$ de una
perpetuidad comprada hoy. El −1 le resta la perpetuidad que sigue después de $n$ (que vale $A/i$ en
$t = n$) y que nadie va a depositar. Por eso olvidarlo infla el resultado exactamente en $A/i$: con
cuotas de $100.000 al 0,5 % mensual, el error son $20.000.000, sea cual sea el plazo (ejercicio 3.4).

> **Comprobación por el otro camino.** El valor futuro es el valor presente capitalizado:
> $$VF = VP \cdot (1+i)^n = A\,\frac{1-(1+i)^{-n}}{i}\,(1+i)^n = A\,\frac{(1+i)^n - 1}{i}$$
> Calcula los dos y deben coincidir. Si no coinciden, el −1 se perdió en algún lado.

**Despejar la cuota.** Si te dan la meta (un $VF$) o el monto prestado (un $VP$) y buscas $A$, se
divide por el factor correspondiente:

$$A = \frac{VF \cdot i}{(1+i)^n - 1} \qquad\qquad A = \frac{VP \cdot i}{1-(1+i)^{-n}}$$

**Despejar la tasa** (la tasa implícita de un plan de pago) no se puede hacer con álgebra: se tantea
o se usa la función TASA de una planilla o la calculadora. Es la TIR del plan, que se ve a fondo en
la unidad 5.

---

## 3. Anticipada y diferida

### Anticipada

El pago cae al **inicio** de cada período: el primero es hoy. Un arriendo, una matrícula, una
suscripción que se paga y recién ahí corre el mes. Es la misma serie corrida un período hacia atrás,
así que cada pago queda un período más cerca y se descuenta una vez menos:

$$VP_{\text{ant}} = A\,\frac{1-(1+i)^{-n}}{i}\,(1+i) \qquad\qquad VF_{\text{ant}} = A\,\frac{(1+i)^n - 1}{i}\,(1+i)$$

La anticipada siempre vale $(1+i)$ veces la vencida (si $i > 0$). Lo que se paga antes cuesta más en
plata de hoy; lo que se recibe antes vale más.

### Diferida

La serie parte más tarde: el primer pago cae en $t = k$ con $k > 1$ («compra hoy, primera cuota en
marzo»). El factor de anualidad deja el valor **un período antes del primer pago**, en $t = k-1$.
Desde ahí falta descontarlo $k-1$ períodos:

$$VP_0 = A\,\frac{1-(1+i)^{-n}}{i} \cdot \frac{1}{(1+i)^{k-1}}$$

El error típico es descontar $k$ períodos en vez de $k-1$. Para no equivocarse, dibuja la línea de
tiempo y marca dónde queda parado el valor antes de moverlo.

---

## 4. Perpetuidades

### Sin crecimiento

Un pago $A$ al final de cada período, para siempre. El factor de anualidad con $n \to \infty$
pierde el término $(1+i)^{-n}$:

$$VP = \frac{A}{i}$$

La intuición: si depositas $A/i$ a la tasa $i$, cada período retiras el interés ($A$) y el capital
queda intacto. Es lo que pasa cuando una deuda solo paga intereses: no se achica nunca.

### Con crecimiento constante

El primer pago es $A_1$ (en $t = 1$) y cada uno crece a la tasa $g$:

$$VP = \frac{A_1}{i - g} \qquad \text{solo si } i > g$$

Dos cuidados:

1. Si $g \ge i$, la suma no converge y la fórmula da un número sin sentido (o negativo). No existe
   un precio finito para eso.
2. El numerador es el pago del **próximo** período. Si te dan el pago que acaba de ocurrir ($A_0$),
   primero hazlo crecer: $A_1 = A_0(1+g)$. La unidad 9 usa esta fórmula para valorar acciones.

### Diferida

Si el primer pago llega en $t = k$, la fórmula deja el valor en $t = k-1$. Se descuenta desde ahí,
igual que la anualidad diferida.

---

## 5. Gradientes

### Gradiente geométrica · la anualidad creciente

Son $n$ pagos que empiezan en $A_1$ y crecen a la tasa $g$ cada período: $A_1$, $A_1(1+g)$, …,
$A_1(1+g)^{n-1}$. Es una anualidad que soltó la condición del monto constante, y también una
perpetuidad creciente a la que se le cortó la cola:

$$VP = \frac{A_1}{i-g}\left[1 - \left(\frac{1+g}{1+i}\right)^{n}\right] \quad (i \neq g) \qquad\qquad VP = \frac{n\,A_1}{1+i} \quad (i = g)$$

Acá $i$ puede ser mayor o menor que $g$: con plazo finito la suma siempre existe. Si $i = g$, cada
pago vale lo mismo en plata de hoy ($A_1/(1+i)$) y basta multiplicar por $n$.

> **Lo único difícil es dónde empieza.** Como toda anualidad, la fórmula deja el valor **un período
> antes del primer pago**. Si la serie parte en $t = 3$, el resultado queda en $t = 2$ y falta
> descontarlo dos períodos. Y $n$ es la cantidad de pagos, no el número del último período.

### Gradiente aritmética

Los pagos suben una cantidad fija $G$: $A_1$, $A_1 + G$, …, $A_1 + (n-1)G$. Se separa en una
anualidad de $A_1$ más una escalera de $G$:

$$VP = A_1\,\frac{1-(1+i)^{-n}}{i} + \frac{G}{i}\left[\frac{1-(1+i)^{-n}}{i} - \frac{n}{(1+i)^n}\right]$$

En este ramo se usa menos que la geométrica (crecer en porcentaje es lo natural en sueldos, arriendos
y dividendos), pero aparece en planes de ahorro que suben de a un monto fijo. Si dudas de la
fórmula, siempre puedes traer pago por pago: es el camino que nunca falla.

---

## 6. Planes de ahorro por tramos

Un plan real rara vez es una sola anualidad: el depósito sube cuando sube el sueldo, o la tasa cambia
porque se cambió de cuenta. El método tiene tres pasos:

1. **Corta la línea de tiempo en tramos.** Un tramo es un pedazo con el mismo depósito y la misma
   tasa.
2. **Cierra cada tramo en su propio final** con el valor futuro de la anualidad (el del −1).
3. **Lleva cada cierre a la fecha final** como un monto único, con la tasa que rige en los meses que
   faltan. Recién ahí se suma.

$$VF_{\text{total}} = \underbrace{A_1\,\frac{(1+i)^{n_1}-1}{i}}_{\text{tramo 1 en } n_1}\,(1+i)^{n_2} + \underbrace{A_2\,\frac{(1+i)^{n_2}-1}{i}}_{\text{tramo 2 en } n_1+n_2}$$

Lo que no se puede hacer: sumar el cierre del tramo 1 con el del tramo 2 sin moverlo, porque están en
fechas distintas. Y lo que no se puede olvidar: el −1 **en cada tramo**. Un control de este ramo se
perdió entero por resolver bien los tramos y comerse el −1 en todos.

---

## 7. Ejemplo resuelto · Ignacia y el pie del auto

Ignacia quiere juntar el pie de un auto. Depositará a fin de cada mes en una cuenta que paga
**0,65 % mensual**: los primeros 18 meses, **$150.000** al mes; desde el mes 19 hasta el 48, cuando
termine su práctica y le suban el sueldo, **$230.000** al mes. ¿Cuánto tendrá al final del mes 48?

**Paso 1 · La línea de tiempo.** Dos tramos, la misma tasa.

| Tramo | Meses | Depósito | Pagos | Se cierra en |
|---|---|---|---|---|
| 1 | 1 a 18 | $150.000 | 18 | mes 18 |
| 2 | 19 a 48 | $230.000 | 30 | mes 48 |

**Paso 2 · Cerrar el tramo 1 en el mes 18.**

$$VF_1 = {150{.}000} \cdot \frac{1{,}0065^{18} - 1}{0{,}0065} = {150{.}000} \times 19{,}0298 = 2{.}854{.}475$$

**Paso 3 · Llevar ese cierre al mes 48.** Desde el 18 al 48 hay 30 meses en los que ese monto queda
quieto ganando intereses:

$$2{.}854{.}475 \times 1{,}0065^{30} = 2{.}854{.}475 \times 1{,}2145 = 3{.}466{.}886$$

**Paso 4 · Cerrar el tramo 2 en el mes 48.** Su último depósito cae justo en el mes 48 y no
capitaliza:

$$VF_2 = {230{.}000} \cdot \frac{1{,}0065^{30} - 1}{0{,}0065} = {230{.}000} \times 33{,}0068 = 7{.}591{.}569$$

**Paso 5 · Sumar, ahora que todo está en el mes 48.**

$$VF_{48} = 3{.}466{.}886 + 7{.}591{.}569 = 11{.}058{.}455$$

Ignacia depositó $9.600.000 de su bolsillo (18 × $150.000 más 30 × $230.000). Los
**$1.458.455** restantes son intereses.

**Paso 6 · Comprobar por el otro camino.** Se trae todo a hoy y se capitaliza 48 meses.

- VP del tramo 1: $150.000 × factor de VP de 18 meses = **$2.540.260**.
- VP del tramo 2: su factor deja el valor en el mes 18; se descuenta 18 meses más y da
  **$5.562.502**.
- Suma: $8.102.762 en $t = 0$.

$$8{.}102{.}762 \times 1{,}0065^{48} = 8{.}102{.}762 \times 1{,}3648 = 11{.}058{.}455 \;\checkmark$$

**Paso 7 · El error que hay que evitar.** Si en los pasos 2 y 4 se usa $A(1+i)^n/i$ (sin el −1), el
plan «junta» **$74.471.017**: $63.412.562 de más, casi siete veces lo correcto. Un resultado así se
delata solo: nadie que deposita menos de 10 millones junta 74 en cuatro años al 0,65 % mensual.
Mira siempre si el orden de magnitud tiene sentido contra lo aportado.

**Cómo se lee.**

- El tramo 1 pesa más de lo que parece: depositó $2.700.000 y aporta $3.466.886 al final, porque
  sus pesos trabajaron más meses.
- El método (cortar, cerrar, mover, sumar) sirve igual con tres tramos o con una tasa que cambia; lo
  que cambia es la tasa con que se mueve cada cierre (ejercicio 3.8).

---

## 8. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Usar $A(1+i)^n/i$ para el valor futuro (sin el −1) | El último pago no capitaliza; el exceso es $A/i$. Comprueba con $VP \cdot (1+i)^n$ |
| Tasa anual con pagos mensuales | Pasa la tasa a la frecuencia de los pagos (unidad 2) antes de usar el factor |
| Sumar cierres de tramos que están en fechas distintas | Lleva cada cierre a la misma fecha como monto único y recién ahí suma |
| En una diferida, descontar $k$ períodos | El factor deja el valor en $k-1$; descuenta $k-1$ |
| Anticipada: aplicar $(1+i)$ solo al VP y no al VF | La anticipada es la vencida corrida un período: los dos se multiplican por $(1+i)$ |
| Perpetuidad creciente con el pago de hoy | El numerador es $A_1$, el próximo; si te dan $A_0$, multiplica por $(1+g)$ |
| Usar $A_1/(i-g)$ con $g \ge i$ | Con plazo infinito no hay valor finito; con plazo finito usa la fórmula de la gradiente |
| Mover un tramo con una tasa que no le corresponde | Cada mes se capitaliza con la tasa que rige ese mes |

---

## 9. Práctica

Diez ejercicios: 3.1 a 3.4 básicos, 3.5 a 3.8 intermedios, 3.9 y 3.10 de desafío. Dos son
**comentes** (3.4 y 3.9): se responde Verdadero, Falso o Incierto y se argumenta; la palabra final
sin argumento vale cero. Las pautas están en la sección 10.

**3.1 · El notebook (básico).** Un notebook cuesta $1.290.000 al contado o 12 cuotas mensuales
vencidas de $118.000, sin pie. Tu plata rinde 0,9 % mensual en un depósito. ¿Qué conviene? ¿Qué tasa
mensual implícita cobra el plan de cuotas?

**3.2 · Ahorro parejo y el −1 (básico).** Depositas $95.000 a fin de cada mes durante 30 meses al
0,45 % mensual. (a) ¿Cuánto tienes al final? (b) ¿Cuánto es interés? (c) Compruébalo capitalizando
el valor presente. (d) ¿Qué habrías obtenido sin el −1?

**3.3 · El jardín infantil (básico).** Un jardín cobra 11 mensualidades de $210.000 que se pagan al
inicio de cada mes (de marzo a enero), o un pago anual de $2.240.000 el primer día de marzo. Tu plata
rinde 0,6 % mensual. ¿Cuánto valen las mensualidades el 1 de marzo, como vencidas y como
anticipadas? ¿Qué conviene?

**3.4 · Comente (básico).** «Si el valor futuro de un plan de 24 depósitos mensuales se calcula con
$A(1+i)^{24}/i$ en vez de $A[(1+i)^{24}-1]/i$, el error es pequeño, porque solo se olvidó restar
uno.» Usa depósitos de $100.000 al 0,5 % mensual para ilustrar.

**3.5 · El sillón diferido (intermedio).** Una tienda ofrece un sillón en 10 cuotas mensuales de
$45.900 con «la primera cuota en cuatro meses» (la primera cae en el mes 4). Al contado cuesta
$380.000. La tienda cobra 1,9 % mensual. ¿Cuánto vale hoy el plan? ¿Qué conviene? ¿Qué pasa si se
descuenta un mes de más?

**3.6 · La beca a perpetuidad (intermedio).** Una exalumna quiere financiar una beca de $3.600.000
al año, para siempre. Un fondo paga 5,2 % anual. (a) ¿Cuánto debe donar hoy si la primera beca se
paga en un año? (b) ¿Y si quiere que la beca crezca 2 % al año? (c) ¿Y si la beca fija parte recién
en el año 3?

**3.7 · El arriendo del local (intermedio).** Un local se arrienda por 8 años. El arriendo del primer
año es $7.200.000, se paga al final del año y sube 3,5 % cada año. La tasa es 7 % anual. (a) ¿Cuánto
vale hoy el contrato? (b) ¿Cuánto valdría si el contrato partiera dos años más tarde (primer pago en
el año 3)? (c) ¿Y si el arriendo creciera 7 % al año?

**3.8 · Ahorro para los estudios, con cambio de tasa (intermedio).** Un papá deposita para los
estudios de su hija a fin de cada mes: los primeros 48 meses, $60.000 al 0,4 % mensual; después se
cambia a una cuenta que paga 0,5 % mensual y deposita $90.000 al mes durante 72 meses más. Desde el
cambio, todo el fondo gana 0,5 %. ¿Cuánto hay en el mes 120? ¿Cuánto da si se usa 0,5 % para los 120
meses?

**3.9 · Comente (desafío).** «Una perpetuidad que crece al 6 % anual descontada al 6 % anual vale
infinito. Por lo tanto, una gradiente geométrica de 10 pagos con $g = i = 6\ \%$ también vale
infinito, porque la fórmula divide por $i - g = 0$.» Ilustra con un primer pago de $1.000.000.

**3.10 · Depósitos que suben de a poco (desafío).** Florencia deposita $42.000 el mes 1 y sube
$3.500 cada mes, durante 24 meses, al 0,62 % mensual. (a) ¿Cuánto tiene al final del mes 24? (b) ¿Qué
depósito parejo, de 24 meses, la dejaría con lo mismo? (c) ¿Por qué ese depósito parejo es menor que
el promedio de sus depósitos?

---

## 10. Pautas

**3.1.** El factor de VP de 12 meses al 0,9 % es 11,3265. VP del plan:
$118.000 × 11,3265 = **$1.336.529**. Es mayor que el contado: **conviene pagar al contado**, que
sale $46.529 más barato en plata de hoy. La tasa implícita del plan es **1,46 %** mensual: el plan
te cobra más de lo que rinde tu plata (0,9 %). Fíjate que nominalmente el plan suma $1.416.000, pero
esa resta no sirve para decidir: mezcla pesos de distintas fechas.

**3.2.** (a) Factor de VF: $(1{,}0045^{30} - 1)/0{,}0045 = 32{,}0423$. VF = 95.000 × 32,0423 =
**$3.044.016**. (b) Aportaste $2.850.000; el interés es **$194.016**. (c) El VP es $2.660.411
(95.000 por el factor de VP de 30 meses); capitalizado 30 meses al 0,45 % da otra vez
$3.044.016 ✓. (d) Sin el −1 da **$24.155.127**: ocho veces lo que aportaste, imposible a una tasa
tan baja. El exceso es 95.000 / 0,0045, el valor de una perpetuidad.

**3.3.** Como vencidas, las 11 mensualidades valen **$2.228.958** el 1 de marzo; como anticipadas
(que es lo que son), $2.228.958 × 1,006 = **$2.242.331**. El pago anual ($2.240.000) es menor:
**conviene el pago anual**, pero solo por $2.331. El jardín ofrece un descuento implícito de
**0,62 %** mensual, apenas sobre lo que rinde tu plata (0,6 %): casi da lo mismo. Si tu plata rindiera
más de 0,62 %, convendría pagar mes a mes. Error típico: comparar los $2.310.000 nominales con los
$2.240.000 y concluir que el pago anual «ahorra $70.000».

**3.4.** **Falso.** El término que se olvida no es «un uno», es $A/i$, el valor de una perpetuidad.
Con $100.000 al 0,5 %, el VF correcto es **$2.543.196**; la fórmula sin el −1 da **$22.543.196**.
La diferencia es **$20.000.000**, igual a 100.000 / 0,005, y no depende del plazo. El resultado
erróneo es 8,9 veces el correcto. El error es más grave cuanto más chica es la tasa, porque $A/i$
crece cuando $i$ baja: justo en las tasas mensuales de los planes de ahorro. Se detecta comprobando
con $VP(1+i)^n$ o comparando con lo aportado ($2.400.000).

**3.5.** El factor de 10 cuotas al 1,9 % deja el valor en el mes 3 (un mes antes de la primera):
**$414.466**. Se descuenta 3 meses: 414.466 / 1,019³ = **$391.712**. Es más que el contado:
**conviene pagar al contado**, $11.712 menos en plata de hoy. Si se descuenta 4 meses (el error
típico) da $384.408: el error achica la diferencia y, con un contado un poco más caro, cambiaría la
decisión.

**3.6.** (a) 3.600.000 / 0,052 = **$69.230.769**. (b) Con crecimiento, 3.600.000 / (0,052 − 0,02)
= **$112.500.000**: hacer crecer la beca un 2 % cuesta $43.269.231 más hoy. El denominador
pasa de 5,2 % a 3,2 %, y por eso el valor salta. (c) La perpetuidad que parte en el año 3 vale
$69.230.769 en el año 2; descontada dos años, **$62.555.814**.

**3.7.** (a) Gradiente geométrica con un primer arriendo de $7.200.000, $g = 3{,}5\ \%$,
$i = 7\ \%$ y $n = 8$:

$$VP = \frac{7{.}200{.}000}{0{,}07 - 0{,}035}\left[1 - \left(\frac{1{,}035}{1{,}07}\right)^8\right] = 48{.}055{.}917$$

El contrato vale **$48.055.917**. El último arriendo es $9.160.411. Sin crecimiento valdría
$42.993.349. (b) Si parte en el año 3, la fórmula deja el valor en el año 2: 48.055.917 / 1,07² =
**$41.973.899**. (c) Con $g = i$, cada pago vale hoy 7.200.000 / 1,07; por 8 pagos,
**$53.831.776**.

**3.8.** Tramo 1 al 0,4 %: cierra en el mes 48 con **$3.168.098**. Ese monto pasa 72 meses al 0,5 %:
$3.168.098 × 1,4320 = **$4.536.857**. Tramo 2 al 0,5 %: cierra en el mes 120 con **$7.776.797**.
Total: **$12.313.654**. Aportó $9.360.000; el interés es $2.953.654. Si se usa 0,5 % para todo da
$12.425.026: sobreestima, porque los primeros cuatro años ganaron menos.

**3.9.** **Falso.** La perpetuidad sí vale infinito: con $g = i$ cada pago vale lo mismo en plata de
hoy y son infinitos. Pero con 10 pagos son solo diez términos iguales: cada uno vale
1.000.000 / 1,06 = $943.396 hoy y el total es **$9.433.962**. La fórmula general no da infinito, da
$0/0$ (se anulan el denominador y el corchete): es una indeterminación, no una explosión. Por eso
el caso $i = g$ se resuelve aparte con $VP = n A_1/(1+i)$. El argumento falla porque confunde el
plazo infinito con el finito.

**3.10.** (a) Con $i = 0{,}62\ \%$ y $n = 24$, el factor de VP es 22,2359. Parte pareja:
42.000 × 22,2359 = **$933.908**. Escalera:

$$\frac{3{.}500}{0{,}0062}\left[22{,}2359 - \frac{24}{1{,}0062^{24}}\right] = 871{.}954$$

VP: 933.908 + 871.954 = **$1.805.862**; capitalizado 24 meses, **$2.094.634**. Aportó $1.974.000
(su último depósito fue $122.500); interés $120.634. (b) $2.094.634 dividido por el factor de VF de
24 meses: **$81.214** al mes. (c) El promedio de sus
depósitos es $82.250, pero en el plan creciente los montos grandes llegan al final y ganan pocos
intereses. El depósito parejo pone más plata al principio, que trabaja más meses, y por eso alcanza
con menos.

---

## 11. Caso integrador · Valentina, el pie del departamento

> Este caso sigue a Valentina, dueña de Estampa Sur, por todo el ramo. Acá parte de lo que calculó
> la unidad 1: sus ahorros de hoy, capitalizados 36 meses, llegan a $4.215.322.

Valentina quiere comprar en 36 meses un departamento de **$98.400.000** y el banco le pide un pie del
**20 %**. Hoy tiene **$3.460.000** ahorrados en una cuenta que paga **0,55 % mensual**. ¿Cuánto debe
depositar a fin de cada mes, en esa misma cuenta, para juntar el pie?

**Desarrollo.**

| Paso | Cálculo | Resultado |
|---|---|---|
| Meta (pie) | 20 % de $98.400.000 | $19.680.000 |
| Lo que ya tiene, en el mes 36 | 3.460.000 × 1,0055³⁶ | $4.215.322 |
| Lo que falta juntar con depósitos | 19.680.000 − 4.215.322 | $15.464.678 |
| Factor de VF de 36 meses | $(1{,}0055^{36} - 1)/0{,}0055$ | 39,6911 |
| Depósito mensual | 15.464.678 / 39,6911 | **$389.625** |

**Comprobación por el valor presente.** Los 36 depósitos valen hoy $389.625 × 32,5791 = $12.693.640.
Con lo que ya tiene, hoy hay el equivalente a $16.153.640; capitalizado 36 meses
($\times 1{,}2183$) da exactamente los $19.680.000 ✓.

**Lectura.** De su bolsillo saldrán $17.486.515 (lo que tiene más los 36 depósitos); los
$2.193.485 que faltan los ponen los intereses. Si Valentina hubiera calculado el depósito sin el −1,
le habría dado **$69.815** al mes: con eso juntaría solo $6.986.360 y llegaría al mes 36 sin pie. El
−1 es la diferencia entre comprar el departamento y no comprarlo.

**Lo que pasa a la unidad 4.** El pie cubre el 20 %; el 80 % restante, **$78.720.000**, lo pide como
crédito hipotecario. La unidad 4 calcula su dividendo, su tabla de amortización y su CAE.

---

## 12. Para seguir

**En los libros del ramo.**

- Ross, Westerfield y Jaffe, *Finanzas corporativas* (9.ª ed., 2012), capítulo 4 (el que fija el
  programa para la matemática financiera): perpetuidades, anualidades y sus versiones crecientes,
  con flujos descontados.
- Brealey, Myers y Allen, *Principios de finanzas corporativas* (9.ª ed., 2010), la lectura de los
  capítulos 1 a 3 que fija el programa, donde se calculan valores presentes de series y
  perpetuidades.

**Abierto y gratis.**

- Dahlquist y Knight, *Principles of Finance*, OpenStax (2022), en inglés. Capítulo 8 (pagos
  iguales: perpetuidades, anualidades y amortización) y capítulo 9 (pagos desiguales, el camino
  flujo a flujo). Licencia CC BY-NC-SA:
  https://openstax.org/books/principles-finance/pages/8-why-it-matters

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un plan de ahorro de tres tramos con un
cambio de tasa y corrígeme el valor futuro, comprobándolo por el valor presente».
