---
ramo: Finanzas
unidad: 4
titulo: Créditos y tablas de amortización
version: 0.1 (15-10-2026)
requiere: [02-tasas-de-interes, 03-anualidades]
alimenta: [05-van-y-tir, 07-bonos]
verificacion: verificacion/u04_creditos.py
---

# Unidad 4 · Créditos y tablas de amortización

**Qué vas a poder hacer.** Calcular la cuota de un crédito de cuota fija (sistema francés); armar su
tabla de amortización y leer qué parte de cada cuota es interés y qué parte paga deuda; contrastarlo
con el sistema alemán (amortización constante); sacar el saldo que se debe en cualquier mes sin
armar la tabla; analizar un crédito de consumo, un hipotecario y una tarjeta de crédito; decidir un
prepago o un refinanciamiento, y calcular la CAE de un crédito con gastos y seguros.

**Lo que necesitas antes.** El valor presente de una anualidad vencida (unidad 3) y pasar una tasa
anual a mensual (unidad 2). Un crédito es una anualidad vista desde el banco.

**Tiempo.** Unas 4,5 horas: 2 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. La idea

Quien pide un crédito recibe un monto hoy ($P$) y devuelve cuotas después. Para el banco es una
inversión: entrega $P$ y recibe una anualidad. El crédito es justo (a la tasa pactada) cuando el
valor presente de las cuotas es igual a lo prestado:

$$P = C \cdot \frac{1-(1+i)^{-n}}{i} \qquad\Longrightarrow\qquad C = \frac{P \cdot i}{1-(1+i)^{-n}}$$

Es la misma fórmula de la unidad 3 con la incógnita en la cuota $C$. Tres consecuencias:

- **El total pagado** es $n \cdot C$, y **el interés total** es $n \cdot C - P$. Sumar cuotas
  sirve para saber cuánto interés se paga, no para comparar créditos: mezcla pesos de distintas
  fechas.
- **La tasa no sale de la fórmula.** La fija el banco según el riesgo de quien pide, el plazo y la
  inflación esperada (unidad 1). Por eso dos personas piden lo mismo y reciben tasas distintas.
- **La periodicidad manda.** Si la cuota es mensual, $i$ es mensual y $n$ son meses. Una tasa anual
  efectiva $r$ se pasa a mensual con $(1+r)^{1/12} - 1$; una nominal anual capitalizable cada mes se
  divide por 12 (unidad 2). Lee cómo está expresada antes de convertir.

---

## 2. La tabla de amortización · sistema francés

En el **sistema francés** la cuota es fija. Por dentro, cada cuota se reparte en dos:

$$\text{interés}_t = \text{saldo}_{t-1} \cdot i \qquad \text{amortización}_t = C - \text{interés}_t \qquad \text{saldo}_t = \text{saldo}_{t-1} - \text{amortización}_t$$

| Mes | Saldo inicial | Interés | Amortización | Cuota | Saldo final |
|---|---|---|---|---|---|
| 1 | $P$ | $P \cdot i$ | $C - P\,i$ | $C$ | $P - (C - P\,i)$ |
| … | … | … | … | $C$ | … |
| $n$ | igual a la última amortización | pequeño | casi toda la cuota | $C$ | 0 |

**Cómo se lee.**

- Al principio la deuda es grande, así que casi toda la cuota se va en interés. Al final la deuda es
  chica y casi toda la cuota paga capital. Por eso al francés se le llama **amortización gradual**.
- La amortización crece mes a mes exactamente al ritmo $(1+i)$:
  $\text{amortización}_{t+1} = \text{amortización}_t \cdot (1+i)$. Es un buen chequeo de la tabla.
- **El saldo final tiene que dar cero.** Si no da cero, hay un error de resta o de tasa.

### El saldo sin armar la tabla

El saldo que se debe después de pagar $k$ cuotas (el **saldo insoluto**) es el valor presente de
las cuotas que faltan, a la tasa del crédito:

$$\text{saldo}_k = C \cdot \frac{1-(1+i)^{-(n-k)}}{i}$$

Lo que se debe hoy es lo que valen hoy los pagos que quedan. Es lo que el banco pide si quieres
pagar todo de una vez, más la comisión de prepago que corresponda.

---

## 3. Sistema alemán · amortización constante

En el **sistema alemán** se paga la misma porción de capital cada mes, $P/n$, más el interés sobre
el saldo. La cuota **baja** cada mes en $i \cdot P/n$:

$$\text{amortización} = \frac{P}{n} \qquad C_t = \frac{P}{n} + \text{saldo}_{t-1} \cdot i \qquad \text{interés total} = i \cdot P \cdot \frac{n+1}{2}$$

| | Francés | Alemán |
|---|---|---|
| Cuota | fija | decreciente |
| Amortización | crece | constante |
| Primera cuota | más baja | más alta |
| Interés total | mayor | menor, porque devuelve el capital antes |
| Para quién | quien necesita una cuota pareja y predecible | quien puede pagar más al principio |

**Que el alemán pague menos interés no lo hace más barato.** A la tasa del crédito, los dos tienen
el mismo valor presente: el monto prestado. Paga menos interés porque se queda menos tiempo con la
plata del banco. Comparar intereses totales entre los dos es comparar créditos de distinto tamaño
promedio. En bonos, la unidad 7 usa los mismos nombres: bullet, francés y alemán.

---

## 4. Tres créditos de todos los días

### Crédito de consumo

Se pide para un viaje, un auto o arreglar la casa. La tasa es **mensual**, el plazo va de meses a
pocos años y casi siempre hay **gastos de otorgamiento** (que se descuentan del monto que llega) y
**seguros** (que se suman a la cuota). Por eso lo que llega a la cuenta es menos que el monto
pedido y lo que sale cada mes es más que la cuota.

### Crédito hipotecario

Se pide para la casa. El plazo es largo (15 a 30 años), así que se pacta en **UF**: el dividendo es
constante en UF y sube en pesos con la inflación, pero es el mismo esfuerzo real. La tasa se da
**anual** y hay que pasarla a mensual. El banco pide un **pie** (en este ramo, un 20 %) y suele exigir
que el dividendo no pase de un cuarto de la renta. Alargar el plazo baja el dividendo y sube mucho
el interés total.

### Tarjeta de crédito

Es la deuda más cara de las tres. Dos trampas:

- **Pagar el mínimo.** Si cada mes se paga solo el interés ($P \cdot i$), la deuda no baja nunca: es
  una perpetuidad (unidad 3). Se paga y se paga, y se sigue debiendo lo mismo.
- **Pagar un monto fijo** $A$ mayor que el interés: la deuda se apaga en

$$n = \frac{-\ln\!\left(1 - \dfrac{P \cdot i}{A}\right)}{\ln(1+i)}$$

meses. Si $A$ está apenas sobre $P \cdot i$, $n$ se dispara.

---

## 5. Prepago y refinanciamiento

**Prepagar** es devolver capital antes de tiempo. Se calcula el saldo insoluto, se le resta lo que
se prepaga y el banco cobra una comisión de prepago. Con el saldo nuevo hay dos caminos:

1. **Mantener el plazo y bajar la cuota:** $C' = \text{saldo nuevo} / \text{factor}(i,\, n - k)$.
2. **Mantener la cuota y acortar el plazo:** se despeja $n'$ con la fórmula de la tarjeta.

El segundo ahorra más interés en pesos porque devuelve el capital antes. En valor presente, a la tasa
del crédito, los dos caminos valen lo mismo: la elección depende de la holgura de caja de quien
paga.

**Refinanciar** es pedir un crédito nuevo, más barato, para pagar el saldo del viejo. Conviene si,
para el mismo plazo, la cuota nueva (con los gastos incluidos) es menor que la vieja. Dicho de otro
modo: la tasa implícita del refinanciamiento (la TIR entre el saldo que se paga hoy y las cuotas
nuevas) tiene que ser menor que la tasa del crédito viejo.

---

## 6. La CAE · la TIR del crédito

La tasa del contrato no cuenta los gastos ni los seguros. La **carga anual equivalente (CAE)** sí:
es la tasa $r_m$ que iguala lo que **realmente llega** con todo lo que **realmente sale**:

$$P - \text{gastos} = \sum_{t=1}^{n} \frac{C + \text{seguros}_t}{(1+r_m)^t}$$

Es una TIR (unidad 5) y se busca por tanteo o con la función TIR de una planilla. Luego se anualiza:

- **Como la publica la norma chilena:** $CAE = 12 \cdot r_m$, la tasa del período por el número de
  períodos del año (así aparece la fórmula $CAE = i_f \cdot f$ en la propuesta de reglamento de crédito
  de consumo del Ministerio de Economía de 2025).
- **Como tasa efectiva anual:** $(1+r_m)^{12} - 1$. Es la que se compara con otras efectivas en este
  ramo.

Las dos sirven para comparar créditos, siempre que se compare la misma versión. La CAE resuelve el
problema de la sección 1: los créditos se comparan por su costo total con todo incluido, no por la
tasa del aviso ni por la suma de cuotas.

---

## 7. Ejemplo resuelto · el viaje de titulación con crédito de consumo

Tomás pide **$3.800.000** para su viaje de titulación, en **18 cuotas mensuales** vencidas, al
**1,42 % mensual**. El banco descuenta **$96.000** de gastos al entregar la plata y cobra un seguro
de desgravamen de **$3.200** al mes junto con la cuota.

**Paso 1 · La cuota.** El factor de VP de 18 meses al 1,42 % es 15,7855.

$$C = \frac{3{.}800{.}000 \times 0{,}0142}{1 - 1{,}0142^{-18}} = \frac{3{.}800{.}000}{15{,}7855} = 240{.}727$$

**Paso 2 · La tabla.** Interés sobre el saldo anterior; lo que sobra de la cuota amortiza.

| Mes | Saldo inicial | Interés (1,42 %) | Amortización | Saldo final |
|---|---|---|---|---|
| 1 | 3.800.000 | 53.960 | 186.767 | 3.613.233 |
| 2 | 3.613.233 | 51.308 | 189.419 | 3.423.815 |
| 3 | 3.423.815 | 48.618 | 192.108 | 3.231.707 |
| … | … | … | … | … |
| 18 | 237.356 | 3.370 | 237.356 | 0 |

Chequeo: la amortización crece en un factor 1,0142 cada mes ($186.767 × 1,0142 = $189.419). Y el
saldo termina en cero.

**Paso 3 · El saldo en el mes 6, sin la tabla.** Faltan 12 cuotas:

$$\text{saldo}_6 = 240{.}727 \cdot \frac{1 - 1{,}0142^{-12}}{0{,}0142} = 2{.}638{.}858$$

Si Tomás quisiera pagar todo después de la sexta cuota, eso es lo que debe.

**Paso 4 · Cuánto paga en intereses.** Total pagado: 18 × 240.727 = $4.333.077. Interés:
**$533.077**.

**Paso 5 · El mismo crédito en sistema alemán.** Amortiza $211.111 cada mes. La primera cuota es
211.111 + 53.960 = **$265.071** y la última **$214.109**. El interés total baja a **$512.620**: paga
menos porque devuelve el capital antes, no porque la tasa sea menor. Tomás elegiría el francés si su
problema es la caja de los primeros meses.

**Paso 6 · La CAE.** A Tomás le llegan 3.800.000 − 96.000 = **$3.704.000** y paga cada mes
240.727 + 3.200 = **$243.927**. La tasa mensual que iguala los dos es:

$$3{.}704{.}000 = 243{.}927 \cdot \frac{1-(1+r_m)^{-18}}{r_m} \quad\Longrightarrow\quad r_m = 1{,}855\ \%$$

| | Mensual | Anual (× 12) | Anual efectiva |
|---|---|---|---|
| Tasa del contrato | 1,42 % | 17,04 % | 18,44 % |
| Costo con gastos y seguro (CAE) | 1,855 % | **22,26 %** | 24,68 % |

**Cómo se lee.** Los gastos y el seguro suben el costo en más de cinco puntos al año. Sin el seguro
la CAE sería 20,47 %: los gastos de entrada pesan más de lo que parece porque se pagan sobre un
crédito corto. Un crédito al 1,42 % «del aviso» puede ser más caro que otro al 1,5 % sin gastos; por
eso se compara la CAE (ejercicio 4.9).

---

## 8. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Calcular el interés de cada mes sobre el monto original | El interés va sobre el saldo del mes anterior |
| Pasar una tasa anual efectiva a mensual dividiendo por 12 | Efectiva: $(1+r)^{1/12}-1$. Solo una nominal capitalizable mensual se divide por 12 |
| Comparar créditos por la suma de cuotas | Suma pesos de distintas fechas; compara la CAE o el VP a una misma tasa |
| Comparar créditos por la tasa del aviso | La tasa no cuenta gastos ni seguros; la CAE sí |
| Creer que el alemán es «más barato» porque paga menos interés | A la tasa del crédito los dos valen lo mismo; paga menos interés porque debe menos tiempo |
| En la tarjeta, pagar el mínimo y creer que se avanza | Si el pago es solo el interés, la deuda no baja: es una perpetuidad |
| Saldo insoluto con todas las cuotas (o con las ya pagadas) | Es el VP de las $n-k$ cuotas que faltan |
| Tabla cuyo saldo final no da cero | Revisa la cuota, la tasa del período y las restas |

---

## 9. Práctica

Diez ejercicios: 4.1 a 4.4 básicos, 4.5 a 4.8 intermedios, 4.9 y 4.10 de desafío. Dos son
**comentes** (4.4 y 4.9): se responde Verdadero, Falso o Incierto y se argumenta. Las pautas están
en la sección 10.

**4.1 · El auto (básico).** Un crédito automotriz de $9.500.000 a 36 cuotas mensuales al 1,1 %
mensual. Calcula la cuota, el total pagado, el interés total y el interés de la primera cuota.

**4.2 · El refrigerador en cuotas (básico).** Una tienda financia $1.750.000 en 10 cuotas mensuales al
2,1 % mensual, con cuota fija. Calcula la cuota y las dos primeras filas de la tabla. Comprueba el
saldo del mes 2 sin la tabla.

**4.3 · El mismo refrigerador, en alemán (básico).** Con los datos de 4.2 pero amortización
constante: amortización mensual, primera, segunda y última cuota, e interés total. ¿Cuánto baja la
cuota cada mes? Compara con el francés.

**4.4 · Comente (básico).** «En un crédito de cuota fija, como la cuota no cambia, el interés que se
paga cada mes tampoco cambia.» Usa las dos primeras filas de 4.2.

**4.5 · La tarjeta (intermedio).** Debes $850.000 en una tarjeta que cobra 3,2 % mensual y no vuelves
a comprar con ella. (a) ¿Cuánto es el pago que solo cubre el interés y cuánto habrás pagado así en
12 meses? ¿Cuánto debes al final? (b) Si pagas $60.000 al mes, ¿en cuántos meses la apagas y cuánto
pagas en total? (c) ¿Y con $40.000 al mes? (d) ¿Qué tasa efectiva anual es 3,2 % mensual?

**4.6 · Prepagar el hipotecario (intermedio).** Un crédito de $42.000.000 a 180 cuotas mensuales al
0,42 % mensual. Después de pagar la cuota 60, la deudora recibe una herencia y prepaga $6.500.000. El
banco cobra una comisión de un mes de intereses sobre lo prepagado. (a) Saldo antes del prepago y
comisión. (b) Cuota nueva si mantiene el plazo. (c) Plazo nuevo si mantiene la cuota. (d) ¿Cuánto
interés ahorra en cada caso (descontando la comisión)? ¿Cuál conviene?

**4.7 · Refinanciar (intermedio).** Hace seis meses tomaste un crédito de consumo de $4.200.000 a 36
cuotas al 1,9 % mensual y ya pagaste 6 cuotas. Otro banco te ofrece pagar el saldo con un crédito
nuevo al 1,3 % mensual por las 30 cuotas que faltan, sumando $120.000 de gastos al monto. ¿Conviene?
Calcula la cuota vieja, el saldo, la cuota nueva, el ahorro mensual y su valor hoy, y la tasa
implícita del refinanciamiento.

**4.8 · La CAE (intermedio).** Un crédito de consumo de $2.900.000 a 24 cuotas al 1,6 % mensual, con
$85.000 de gastos descontados al inicio y un seguro de $4.100 al mes. Calcula la cuota, la tasa
mensual del costo total, la CAE (× 12) y su efectiva anual, y compáralas con la tasa del contrato.

**4.9 · Comente (desafío).** «Entre dos créditos por el mismo monto y plazo, conviene siempre el de
menor tasa de interés.» Ilustra con $2.400.000 a 12 cuotas: el crédito A cobra 1,55 % mensual sin
gastos; el B, 1,45 % mensual con $165.000 de gastos descontados al inicio.

**4.10 · El departamento más caro que se puede comprar (desafío).** Una pareja gana $2.300.000 al mes
y el banco exige que el dividendo no pase del 25 % de la renta. La tasa es 4,3 % anual efectiva en
UF, a 25 años, con pie de 20 %. Supón una UF de $39.800. (a) ¿Cuál es el crédito máximo y el precio
máximo del departamento, en UF y en pesos? (b) ¿Cuánto más pueden comprar a 30 años y cuánto más
interés pagan? (c) ¿Qué pasa si se convierte la tasa dividiendo por 12?

---

## 10. Pautas

**4.1.** $C = 9{.}500{.}000 \cdot 0{,}011 / (1 - 1{,}011^{-36})$ = **$321.008**. Total pagado
**$11.556.305**; interés total **$2.056.305**. La primera cuota lleva 9.500.000 × 1,1 % = **$104.500**
de interés: casi un tercio de la cuota.

**4.2.** Cuota: **$195.842**.

| Mes | Saldo inicial | Interés | Amortización | Saldo final |
|---|---|---|---|---|
| 1 | 1.750.000 | 36.750 | 159.092 | 1.590.908 |
| 2 | 1.590.908 | 33.409 | 162.433 | 1.428.475 |

Sin la tabla: el VP de las 8 cuotas que faltan, $195.842 por el factor de 8 meses al 2,1 %, da
**$1.428.475** ✓. El interés total del crédito es $208.421.

**4.3.** Amortización: 1.750.000 / 10 = **$175.000**. Primera cuota 175.000 + 36.750 = **$211.750**;
segunda **$208.075**; última **$178.675**. La cuota baja $3.675 cada mes (175.000 × 2,1 %). Interés
total **$202.125**, contra $208.421 del francés. La primera cuota alemana es $15.908 más alta que
la francesa; esa es la contracara de pagar menos interés.

**4.4.** **Falso.** El interés se calcula sobre el saldo, y el saldo baja con cada cuota. En 4.2 el
primer mes paga $36.750 de interés y el segundo $33.409. Como la cuota es fija y el interés baja, la
amortización sube (de $159.092 a $162.433, un 2,1 % más). Lo fijo es la suma, no sus partes. Solo en
un crédito que paga solo intereses (bullet) el interés no cambia, pero ahí la cuota no amortiza nada.

**4.5.** (a) Interés del mes: 850.000 × 3,2 % = **$27.200**. En 12 meses pagas $326.400 y sigues
debiendo los mismos $850.000: es una perpetuidad. (b) Con $60.000:
$n = -\ln(1 - 27{.}200/60{.}000)/\ln 1{,}032 = 19{,}2$, o sea **20 pagos**: 19 de $60.000 y un último
de $10.500. Total pagado **$1.150.500**; interés $300.500. (c) Con $40.000, $n = 36{,}2$: tres años.
Bajar el pago un tercio casi duplica el plazo, porque el pago se acerca al interés. (d)
$1{,}032^{12} - 1 = 45{,}9\ \%$ anual.

**4.6.** (a) Cuota original **$333.009**. Saldo después de la cuota 60, VP de las 120 restantes:
**$31.338.750**. Comisión: 6.500.000 × 0,42 % = **$27.300**. Saldo nuevo: **$24.838.750**. (b)
Manteniendo 120 meses: cuota **$263.939**, $69.070 menos. (c) Manteniendo la cuota:
$n' = 89{,}7$ meses (90 pagos, el último parcial), unos 30,3 meses antes. (d) Interés ahorrado, ya
restada la comisión: **$1.761.069** con (b) y **$3.573.420** con (c). En pesos ahorra más acortando
el plazo, porque devuelve el capital antes; en valor presente al 0,42 % los dos caminos valen lo
mismo. Si la deudora tiene holgura, acorta; si su problema es la caja del mes, baja la cuota.

**4.7.** Cuota vieja: **$162.143**. Saldo después de 6 cuotas (VP de 30 al 1,9 %): **$3.681.869**.
Crédito nuevo: 3.681.869 + 120.000 = **$3.801.869**, a 30 cuotas al 1,3 %: cuota **$153.855**. Ahorra
**$8.288** al mes, $248.649 en las 30 cuotas, que hoy valen **$204.810** (descontadas al 1,3 %). La
tasa implícita del refinanciamiento (recibe el saldo, paga las cuotas nuevas) es **1,525 %** mensual,
menor que el 1,9 % del crédito viejo: **conviene**. Sin los gastos la cuota sería $148.999; los
$120.000 se comen parte del ahorro, pero no todo.

**4.8.** Cuota: **$146.467**. Llegan $2.815.000 y salen $150.567 al mes. Tasa mensual del costo
total: **2,103 %**. CAE: **25,23 %**; efectiva anual **28,36 %**. La tasa del contrato era 1,6 %
mensual: 19,20 % anual (× 12) y 20,98 % efectiva. Gastos y seguro suman unos seis puntos al año.

**4.9.** **Falso** (o Incierto, si se argumenta igual). La tasa del contrato no incluye los gastos ni
los seguros; lo que hay que comparar es el costo total, la CAE. Con los datos:

| | Tasa | Gastos | Cuota | CAE | Total que sale |
|---|---|---|---|---|---|
| A | 1,55 % | 0 | $220.718 | 18,60 % | $2.648.615 |
| B | 1,45 % | $165.000 | $219.347 | 31,33 % | $2.797.167 |

B tiene menor tasa y menor cuota, pero los $165.000 que se quedan al inicio lo hacen mucho más caro.
La afirmación solo sería cierta si los dos créditos tuvieran los mismos gastos, seguros y forma de
pago; como en general no es así, la regla correcta es comparar la CAE.

**4.10.** (a) Dividendo máximo: 25 % de 2.300.000 = **$575.000** = **14,45 UF**. Tasa mensual:
$1{,}043^{1/12} - 1 = 0{,}3515\ \%$. Crédito máximo: 14,45 UF por el factor de 300 meses =
**2.675,8 UF**. Como es el 80 %, el precio máximo es **3.344,8 UF** (pie de 669,0 UF), unos
**$133.121.422**. (b) A 30 años el crédito sube a 2.948,2 UF y el precio a **3.685,2 UF**: 340,5 UF
más de departamento. El interés total pasa de 1.658,4 UF a 2.252,8 UF. (c) Dividir por 12 da
0,3583 % mensual: una tasa más alta que la pactada, que subestima lo que el banco presta. El error es
chico por mes pero se acumula en 300 meses.

---

## 11. Caso integrador · Valentina, el hipotecario

> Este caso sigue a Valentina, dueña de Estampa Sur, por todo el ramo. La unidad 3 dejó el pie
> juntado: $19.680.000, el 20 % de un departamento de $98.400.000.

Valentina pide el 80 % restante, **$78.720.000**, al **4,6 % anual efectivo**. Duda entre 20 y 25
años. El banco cobra **$1.150.000** de gastos operacionales al cursar el crédito.

**Pregunta.** ¿Cuál es el dividendo en cada plazo? ¿Cómo se ven los primeros meses? ¿Cuál es el
costo real con los gastos?

**Desarrollo.**

1. **Tasa mensual.** $1{,}046^{1/12} - 1 = 0{,}3755\ \%$. Si alguien dividiera 4,6 % por 12
   (0,3833 %), el dividendo a 20 años le daría $502.281: unos $4.000 de más cada mes.
2. **Dividendo.**

| Plazo | Dividendo | Total pagado | Interés total | Renta mínima (dividendo × 4) |
|---|---|---|---|---|
| 20 años (240 meses) | **$498.267** | $119.584.080 | $40.864.080 | $1.993.068 |
| 25 años (300 meses) | **$437.809** | $131.342.816 | $52.622.816 | $1.751.238 |

3. **Los primeros meses a 20 años.**

| Mes | Interés | Amortización | Saldo |
|---|---|---|---|
| 1 | 295.579 | 202.688 | 78.517.312 |
| 2 | 294.818 | 203.449 | 78.313.863 |
| 3 | 294.054 | 204.213 | 78.109.649 |

Casi el 60 % del primer dividendo es interés. Después de cinco años (60 cuotas) todavía debe
$65.108.392 de los $78.720.000.

4. **CAE.** Le llegan 78.720.000 − 1.150.000 = **$77.570.000** y paga 240 dividendos de $498.267.
La tasa mensual que los iguala es 0,390 %. Como la publica la norma chilena (× 12), la CAE es
**4,68 %**; anualizada como efectiva, 4,78 %. Los gastos suben el costo en casi dos décimas sobre el 4,6 % del
contrato.

**Lectura.** Pasar de 20 a 25 años baja el dividendo en $60.458 al mes, pero suma $11.758.736 de
interés. Si su renta pasa holgada la exigencia de los 20 años, el plazo corto le ahorra intereses;
si la caja del taller es irregular, el plazo largo le da aire y siempre puede prepagar después
(sección 5). La decisión no es solo de tasa: es de cuánta holgura quiere tener cada mes.

---

## 12. Para seguir

**En los libros del ramo.**

- Ross, Westerfield y Jaffe, *Finanzas corporativas* (9.ª ed., 2012), capítulo 4 (el que fija el
  programa para la matemática financiera): anualidades aplicadas a préstamos y su amortización.
- Brealey, Myers y Allen, *Principios de finanzas corporativas* (9.ª ed., 2010), la lectura de los
  capítulos 1 a 3 que fija el programa.

**Abierto y gratis.**

- Dahlquist y Knight, *Principles of Finance*, OpenStax (2022), en inglés, capítulo 8, sección 8.3
  (amortización de préstamos) y sección 8.4 (tasas declaradas contra efectivas). Licencia
  CC BY-NC-SA: https://openstax.org/books/principles-finance/pages/8-why-it-matters
- La fórmula de la CAE, en la propuesta de reglamento de crédito de consumo del Ministerio de
  Economía (2025): https://pac.economia.gob.cl/wp-content/uploads/2025/10/Propuesta-Nuevo-Reglamento-Credito-de-Consumo.pdf

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un crédito de consumo con gastos y
seguro, déjame armar la tabla y la CAE, y corrígeme fila por fila».
