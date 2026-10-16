---
ramo: Finanzas
unidad: 7
titulo: Bonos
version: 0.1 (15-10-2026)
requiere: [03-anualidades, 05-van-y-tir, 06-estructura-de-tasas]
alimenta: [08-duracion-e-inmunizacion]
verificacion: verificacion/u07_bonos.py
---

# Unidad 7 · Bonos

**Qué vas a poder hacer.** Leer las condiciones de un bono (nominal, cupón, plazo, estructura) y
separarlas de lo que pone el mercado; valorar un bono como el valor presente de sus flujos, con una
tasa única o con la curva spot; explicar por qué un bono se transa sobre, bajo o a la par; despejar
la rentabilidad al vencimiento (YTM) a mano, por interpolación; calcular la rentabilidad de quien
vende antes del vencimiento; distinguir precio sucio de precio limpio; nombrar los cuatro riesgos
de la renta fija, y demostrar con el no arbitraje que un precio está bien puesto.

**Lo que necesitas antes.** Valor presente de un monto único y de una anualidad (unidades 1 y 3),
la TIR y su supuesto de reinversión (unidad 5) y las tasas spot (unidad 6).

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. Qué es un bono

Un bono es un **préstamo partido en pedacitos**. Una empresa o el Fisco necesita plata, y en vez de
pedírsela a un solo banco, se la pide a muchos inversionistas: cada uno compra un bono, le entrega
plata hoy al emisor y recibe a cambio una promesa de pagos futuros. Para el emisor es deuda; para
quien lo compra es una inversión de **renta fija**.

Piensa en un crédito al revés: cuando sacas un crédito de consumo para un viaje, tú eres el emisor
(recibes plata hoy y pagas cuotas). Cuando compras un bono, tú eres el banco.

### Las condiciones del contrato

| Elemento | Símbolo | Qué es |
|---|---|---|
| Valor nominal (valor cara, carátula o facial) | $VN$ | El capital que el emisor se compromete a devolver |
| Tasa cupón (tasa de emisión o carátula) | $c$ | La tasa que fija el interés; **solo** sirve para calcular el cupón |
| Cupón | $C = c \cdot VN$ | El interés que se paga en cada período |
| Plazo | $n$ | Cuántos períodos faltan hasta el último pago |
| Frecuencia | | Anual, semestral; define cuántos cupones hay por año |
| Estructura de amortización | | Cómo se devuelve el capital: todo al final o por partes |
| Moneda | | Pesos, dólares o UF; decide si hay riesgo de inflación |

> **Contrato contra mercado.** Todo lo de la tabla está escrito en el contrato y no cambia nunca. Lo
> que cambia todos los días es la **tasa de mercado** $y$: lo que hoy exigen los inversionistas a un
> bono comparable (mismo plazo y mismo riesgo). Es la única que descuenta. El error número uno del
> ramo es descontar con la tasa cupón.

### Tipos según cómo devuelven el capital

| Tipo | Flujos | Se parece a |
|---|---|---|
| **Bullet** | Cupones iguales en cada período y el nominal completo al final | Una anualidad (los cupones) más un monto único (el nominal) |
| **Cero cupón** | Nada hasta el vencimiento; ahí paga el nominal | Un monto único. Se compra con descuento: toda la ganancia es la diferencia entre lo que pagas y el nominal |
| **Amortizable** | Cada pago trae interés sobre el saldo y una parte del capital | Un crédito con tabla de amortización: francés (cuota constante) o alemán (amortización constante) |
| **Perpetuo** | Cupones para siempre, nunca devuelve el capital | Una perpetuidad: $P = C/y$ |

---

## 2. El precio es el valor presente de lo que falta

No hay fórmula nueva: un bono vale lo que valen hoy los flujos que **le quedan**.

### Con una sola tasa

Si todos los flujos se descuentan a la misma tasa $y$, un bullet vale

$$P = C \cdot \frac{1 - (1+y)^{-n}}{y} + \frac{VN}{(1+y)^{n}}$$

El primer término es la anualidad de los cupones y el segundo, el nominal traído a hoy. Un atajo de
pizarra: $n - 1$ cupones como anualidad más un pago único de $C + VN$ en $n$ da exactamente lo mismo.

### Con la curva spot

La tasa única es una simplificación. Lo correcto es descontar **cada flujo con la tasa spot de su
plazo** (unidad 6): el cupón del año 1 con la tasa a 1 año, el del año 2 con la tasa a 2 años, y así.

$$P = \sum_{t=1}^{n} \frac{F_t}{(1 + s_t)^{t}}$$

Si conoces el precio de los bonos cero cupón, ni siquiera necesitas la tasa: el factor de descuento
del año $t$ es el precio del cero a $t$ años dividido por su nominal.

### La rentabilidad al vencimiento (YTM)

La **rentabilidad al vencimiento** (YTM, *yield to maturity*; en Chile también TIR o RAV) es la tasa
única que, aplicada a todos los flujos, reproduce el precio de mercado:

$$P = \sum_{t=1}^{n} \frac{F_t}{(1 + YTM)^{t}}$$

Es la TIR del bono visto como proyecto: pagas $P$ hoy y recibes los flujos. Como en la unidad 5, se
despeja probando dos tasas que dejen el VAN con signos opuestos e interpolando:

$$YTM \approx r_1 + (r_2 - r_1)\,\frac{VAN(r_1)}{VAN(r_1) - VAN(r_2)}$$

La YTM promete esa rentabilidad **solo si** se cumplen tres cosas: (1) mantienes el bono hasta el
vencimiento, (2) reinviertes cada cupón a la misma YTM y (3) el emisor paga todo. Si falla una, ganas
otra cosa. Con una curva spot que sube, la YTM queda entre la tasa spot más corta y la más larga, más
cerca de la del vencimiento, porque ahí está casi todo el valor.

---

## 3. Sobre, bajo o a la par, y por qué

Compara la tasa cupón con la tasa de mercado **antes** de calcular. El resultado ya está decidido:

| Relación | Precio | Se transa |
|---|---|---|
| $y < c$ | $P > VN$ | **sobre la par** (con premio) |
| $y = c$ | $P = VN$ | **a la par** |
| $y > c$ | $P < VN$ | **bajo la par** (con descuento) |

**La intuición.** Si el mercado hoy exige 5 % y tu bono paga un cupón de 6 %, tu bono paga más de lo
que se exige: todos lo quieren, y el precio sube hasta que quien lo compra gane justo el 5 % del
mercado. El premio que pagas de más se «devuelve» con los cupones altos. Al revés, un bono con cupón
bajo solo se vende con descuento.

**Valor par no es lo mismo que nominal.** La definición matemática (tasa de mercado igual a la de
emisión) es correcta, pero la de fondo es otra: el valor par es **el saldo de la deuda** en ese
momento. En un bullet el saldo es el nominal hasta el final, así que coinciden. En un bono
amortizable el saldo baja con cada pago, y el valor par baja con él: comprar a 610 un bono al que le
quedan 600 de capital por devolver es comprarlo sobre la par.

**Convergencia a la par.** Si la tasa de mercado no cambia, el precio de un bono sobre la par baja un
poco cada año y el de uno bajo la par sube, hasta llegar al nominal el día del vencimiento. El
último día el bono es solo su último flujo.

---

## 4. Renta fija no es rentabilidad fija · el período de tenencia

Lo fijo es el cupón. La rentabilidad depende del precio al que compras y del precio al que vendes, y
los dos los pone la tasa de mercado de cada día.

Si compras en $t = 0$ y vendes en $t = k$, primero se valora el bono en $k$ con **los flujos que
quedan** y la tasa de mercado de ese día:

$$P_k = \sum_{t=k+1}^{n} \frac{F_t}{(1+y_k)^{t-k}}$$

La **rentabilidad del período de tenencia** es la TIR del flujo del tenedor:

$$-P_0,\quad C,\quad \dots,\quad C + P_k$$

En $t = k$ se cobra el cupón de ese año **y además** el precio de venta. Olvidar ese cupón es el error
clásico.

**Con reinversión explícita.** Si te dicen a qué tasa $r$ se depositan los cupones, capitaliza cada
uno hasta $k$, suma el precio de venta y anualiza:

$$VF_k = \sum_{t=1}^{k} C\,(1+r)^{k-t} + P_k \qquad \text{rentabilidad} = \left(\frac{VF_k}{P_0}\right)^{1/k} - 1$$

Si $r$ es menor que la TIR del flujo, la rentabilidad efectiva queda bajo esa TIR: es el problema de
reinversión de la unidad 5, ahora con cupones.

---

## 5. Precio sucio y precio limpio

Los cupones se pagan en fechas fijas, pero un bono se puede vender cualquier día. Si vendes tres
meses después del último cupón, durante esos tres meses el cupón que viene ya se fue «ganando», y es
tuyo. El comprador te lo paga dentro del precio.

- **Precio sucio** (*dirty*, *full price*): lo que de verdad se paga. Es el valor presente de los
  flujos que quedan, a la fecha exacta de la compra. Si $P_{ex}$ es el precio justo después del
  último cupón y ha pasado una fracción $f$ del período, $P_{sucio} = P_{ex}\,(1+y)^{f}$.
- **Interés devengado** (o corrido): la parte del próximo cupón que ya ganó el vendedor. Con la
  convención lineal, $C \cdot f$.
- **Precio limpio** (*clean*): $P_{limpio} = P_{sucio} - C \cdot f$. Es el que se cotiza en pantalla.

**Por qué se cotiza el limpio.** El sucio sube todo el período y cae de golpe el día del cupón (el
cupón sale del bono y entra al bolsillo). Ese diente de sierra no dice nada del mercado. El limpio
quita el cupón ganado y se mueve solo cuando cambia la tasa o por la convergencia a la par.

---

## 6. Los cuatro riesgos de la renta fija

| Riesgo | Qué pasa | Quién lo sufre más | Cómo se mide o se ve |
|---|---|---|---|
| **De tasa de interés** (de precio) | Si la tasa de mercado sube, el precio del bono cae | Quien vende antes del vencimiento; los bonos largos y de cupón bajo | Duración (unidad 8) |
| **De reinversión** | Los cupones se reinvierten a una tasa menor que la YTM | Los bonos con cupones altos y plazo largo; el cero cupón no lo tiene | Comparar la rentabilidad efectiva con la YTM |
| **De crédito** (de impago) | El emisor no paga o paga tarde; o le bajan la clasificación y el precio cae | Los emisores peor clasificados | Clasificación (AAA, AA, A, BBB…) y el premio sobre la tasa del Fisco |
| **De liquidez** | No encuentras comprador rápido sin rebajar el precio | Emisiones chicas o poco transadas | La diferencia entre el precio de compra y el de venta |

Los dos primeros van en direcciones opuestas: si la tasa sube, el bono vale menos (malo) pero los
cupones se reinvierten mejor (bueno). Esa tensión es la base de la inmunización de la unidad 8.

> **Y uno que en Chile se resuelve con la UF.** Un bono en pesos o en dólares tiene además **riesgo
> de inflación**: los pagos fijos compran menos si los precios suben. Un bono en UF se reajusta y ese
> riesgo desaparece.

---

## 7. No arbitraje · por qué el precio de mercado es el correcto

**Arbitraje** es ganar más sin asumir más riesgo, o ganar sin poner plata. En un mercado con muchos
compradores y vendedores, información para todos y un producto parejo, esas oportunidades duran
segundos.

**Primera forma · el VAN del comprador es cero.** Quien compra un bono al precio de mercado y lo
mantiene gana exactamente la tasa de un bono comparable. Su VAN, a esa tasa, es cero. Si el vendedor
pidiera más, el comprador se iría al comparable; si pidiera menos, regalaría plata. Para demostrar
que un precio está bien puesto, se calcula el VAN del comprador y se muestra que da cero.

**Segunda forma · un bono es una caja de ceros.** Un bono que paga $F_1, F_2, \dots, F_n$ es lo mismo
que un paquete de bonos cero cupón: uno que paga $F_1$ en el año 1, otro que paga $F_2$ en el año 2, y
así. Dos cosas que pagan lo mismo tienen que costar lo mismo (**ley de un solo precio**). Por eso el
precio con la curva spot es el precio de no arbitraje. Si el bono se vende más barato que el paquete,
se compra el bono y se venden los ceros (o, al revés, si se vende más caro): se cobra la diferencia
hoy y los flujos futuros se anulan.

---

## 8. Ejemplo resuelto · los ahorros de Paula

Paula es enfermera en Chillán y quiere sacar sus ahorros del depósito a plazo. Su ejecutivo le ofrece
un bono de **Aguas del Itata S.A.** (empresa ficticia):

| Dato | Valor |
|---|---|
| Nominal | $1.000.000 |
| Tasa cupón | 6,4 % anual, cupón anual |
| Plazo | 5 años, bullet |
| Tasa de mercado hoy (bonos comparables a 5 años) | 5,6 % anual |

**Paso 1 · Antes de calcular, el signo.** El mercado exige 5,6 % y el bono paga 6,4 %: tiene que salir
**sobre la par**.

**Paso 2 · Los flujos.** $C = 0{,}064 \times 1{.}000{.}000 = 64{.}000$ al año. En el año 5 llegan
$64.000 + $1.000.000 = $1.064.000.

**Paso 3 · El precio.** Factor de anualidad al 5,6 % por 5 años:
$\dfrac{1 - 1{,}056^{-5}}{0{,}056} = 4{,}2586$.

$$P_0 = 64{.}000 \times 4{,}2586 + \frac{1{.}000{.}000}{1{,}056^{5}} = 272{.}550 + 761{.}518 = 1{.}034{.}069$$

Los cupones valen hoy $272.550 y el nominal, $761.518. Paula paga **$1.034.069**: un premio de **$34.069** sobre el nominal. Ese premio no es una pérdida:
lo recupera porque cada año cobra $64.000, más que los $56.000 que pagaría un bono al 5,6 %. Por eso
su YTM es justo 5,6 %.

**Paso 4 · Dos años después, la tasa sube.** Paula cobra los cupones de los años 1 y 2 y en $t = 2$
necesita la plata para el pie de un auto. Ese día los bonos comparables a 3 años rinden **6,7 %**.
Quedan tres flujos: $64.000, $64.000 y $1.064.000.

$$P_2 = \frac{64{.}000}{1{,}067} + \frac{64{.}000}{1{,}067^{2}} + \frac{1{.}064{.}000}{1{,}067^{3}} = 992{.}084$$

Si la tasa se hubiera quedado en 5,6 %, el bono valdría $1.021.543 (más cerca del nominal, por la
convergencia a la par). Con el alza vale **$992.084**: bajo la par, porque ahora el mercado exige más
que el cupón.

**Paso 5 · El flujo de Paula.** Pagó $1.034.069 en $t = 0$; cobró $64.000 en $t = 1$; en $t = 2$ cobra el
cupón y vende: $64.000 + $992.084 = $1.056.084.

| $t$ | 0 | 1 | 2 |
|---|---|---|---|
| Flujo de Paula | −$1.034.069 | +$64.000 | +$1.056.084 |

**Paso 6 · La rentabilidad del período de tenencia, a mano.** Se prueban dos tasas:

$$\text{al } 4\,\%:\quad -1{.}034{.}069 + \frac{64{.}000}{1{,}04} + \frac{1{.}056{.}084}{1{,}04^{2}} = +3{.}878$$

$$\text{al } 5\,\%:\quad -1{.}034{.}069 + \frac{64{.}000}{1{,}05} + \frac{1{.}056{.}084}{1{,}05^{2}} = -15{.}217$$

El VAN cambia de signo: +$3.878 al 4 % y −$15.217 al 5 %.

$$r \approx 4\,\% + 1\,\% \times \frac{3{.}878}{3{.}878 + 15{.}217} = 4{,}20\,\%$$

El valor exacto también redondea a **4,20 %** anual.

**Paso 7 · La lectura.** Paula esperaba 5,6 % y ganó 4,20 %. No hubo impago ni sorpresa en los cupones:
la diferencia es **riesgo de tasa**. Al subir la tasa, el precio de venta cayó $41.985 respecto de lo
que pagó. Si hubiera mantenido el bono hasta el año 5 (y reinvertido al 5,6 %), habría ganado el
5,6 %: el riesgo de tasa duele a quien vende antes.

**Paso 8 · El que compra.** Quien le compra a Paula paga $992.084 y recibe 64.000, 64.000 y 1.064.000.
A la tasa de mercado de 6,7 % su VAN es exactamente cero: gana lo mismo que con cualquier bono
comparable. El precio está bien puesto; no hay arbitraje.

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Descontar con la tasa cupón | La tasa cupón solo arma el cupón; descuenta la de mercado |
| Valorar en $t = k$ con todos los cupones | En $t = k$ quedan $n - k$ flujos; lo cobrado ya está en el bolsillo |
| Olvidar el cupón del año de la venta | El último flujo del tenedor es $C + P_k$ |
| Con cupón semestral, dividir la tasa anual efectiva por dos | Equivalencia compuesta: $(1+y)^{1/2} - 1$ |
| Creer que comprar sobre la par es mala inversión | Se paga más, pero los cupones son más altos: se gana la tasa de mercado |
| Dar la YTM como rentabilidad segura | Solo si se mantiene al vencimiento, se reinvierte a la YTM y el emisor paga |
| Comparar tasas de bonos con distinto plazo o clasificación | La tasa de mercado sirve solo si viene de un bono comparable en plazo y riesgo |
| En un amortizable, tomar el nominal como valor par | El valor par es el saldo de la deuda en ese momento |

---

## 10. Práctica

Diez ejercicios: 7.1 a 7.4 básicos, 7.5 a 7.8 intermedios, 7.9 y 7.10 de desafío. Los ejercicios 7.4 y
7.10 son **comentes**: responde Verdadero, Falso o Incierto y argumenta en no más de cinco líneas.
Las pautas están en la sección 11.

**7.1 · Un bono en UF a tres tasas (básico).** Un bono bullet de 2.000 UF paga un cupón anual de 3,7 %
y vence en 6 años. Calcula su precio si el mercado exige 3,2 %, 3,7 % y 4,4 %, y di en cada caso cómo
se transa y por qué.

**7.2 · Un cero cupón y la tasa que sube (básico).** Un pagaré cero cupón paga $10.000.000 en 4 años.
(a) ¿Cuánto vale hoy si el mercado exige 6,3 %? (b) Justo después de comprarlo, la tasa sube a 7 %:
¿cuánto vale ahora y cuánto se perdió, en pesos y en porcentaje? (c) Si alguien te lo ofrece en
$7.650.000, ¿qué rentabilidad anual obtienes manteniéndolo hasta el final?

**7.3 · Un bono que amortiza (básico).** Una cooperativa emite un bono de 900 UF a 3 años que amortiza
300 UF de capital cada año y paga un interés de 4,5 % sobre el saldo (estructura alemana). (a) Arma la
tabla de flujos y el saldo de la deuda al final de cada año. (b) Valóralo hoy si el mercado exige
5,2 %. (c) Un año después, cobrado el primer pago y con la tasa de mercado igual, ¿cuánto vale y se
transa sobre o bajo la par?

**7.4 · Comente: la renta fija (básico).** «Un bono del Fisco es renta fija: quien lo compra sabe desde
el primer día cuánto va a ganar.» ¿Verdadero, falso o incierto?

**7.5 · La YTM a mano (intermedio).** Un bono bullet de $500.000 nominales con cupón anual de 7,2 % y 4
años al vencimiento se ofrece en $479.800. (a) Sin calcular, ¿la YTM es mayor o menor que 7,2 %? (b)
Calcula el precio al 8 % y al 9 % y despeja la YTM por interpolación. (c) Compárala con el valor
exacto.

**7.6 · Cupón semestral (intermedio).** Un bono bullet de 3.000 UF paga un cupón de 1,9 % cada semestre
y le quedan 7 años (14 semestres). La tasa de mercado es 4,6 % anual efectiva. (a) Pasa la tasa a
semestral por equivalencia. (b) Calcula el precio. (c) ¿Cuánto te equivocarías si dividieras 4,6 %
por dos? (d) Sin calcular el precio, ¿tenía que salir bajo la par?

**7.7 · Vender antes y reinvertir (intermedio).** Ignacio compró al emitirse, a la par, un bono bullet de
$2.000.000 con cupón anual de 5,5 % y 8 años de plazo. Cobró tres cupones y en $t = 3$ vendió, cuando
los bonos comparables a 5 años rendían 4,3 %. (a) ¿A qué precio vendió? (b) ¿Qué rentabilidad del
período de tenencia obtuvo? Interpola entre 7 % y 8 %. (c) Los cupones los dejó en una cuenta al
3,8 % anual: ¿cuál fue su rentabilidad efectiva? ¿Por qué difiere de (b)?

**7.8 · Precio sucio y limpio (intermedio).** A un bono bullet de 100 de nominal, con cupón anual de
6,6 %, le quedan 3 cupones y acaba de pagar uno. La YTM es 5,9 % y no cambia. (a) ¿Cuánto vale hoy?
(b) Calcula el precio sucio, el interés devengado y el precio limpio 3 meses ($f = 0{,}25$) y 9 meses
($f = 0{,}75$) después. (c) ¿Cuánto vale un instante antes y un instante después del próximo cupón,
en sucio y en limpio? ¿Qué muestra?

**7.9 · Una caja de ceros y un arbitraje (desafío).** Las tasas spot son 4,4 % a 1 año, 4,9 % a 2 años
y 5,5 % a 3 años. Un bono bullet de 100 de nominal y cupón anual de 8,2 % vence en 3 años. (a)
Valóralo con la curva spot. (b) Calcula su YTM. (c) Arma el paquete de ceros que lo replica. (d) En la
pantalla el bono se vende en 106,90. ¿Hay arbitraje? Describe la operación y cuánto se gana por bono.

**7.10 · Comente: el efecto cupón (desafío).** «Si dos bonos del mismo emisor vencen el mismo día pero
tienen distinta YTM, uno de los dos está mal valorado y hay una oportunidad de arbitraje.» Usa la
curva del ejercicio 7.9 y dos bonos a 3 años con cupones de 2 % y 10 %.

---

## 11. Pautas

**7.1.** Cupón: $0{,}037 \times 2{.}000 = 74$ UF al año.

| Tasa de mercado | Precio | Se transa |
|---|---|---|
| 3,2 % | 2.053,81 UF | sobre la par |
| 3,7 % | 2.000,00 UF | a la par |
| 4,4 % | 1.927,56 UF | bajo la par |

Lectura: cuando el mercado exige menos que el cupón (3,2 % contra 3,7 %), el bono paga más de lo que
se pide y se paga un premio. Si la tasa iguala al cupón, el precio es el nominal sin hacer cuentas.

**7.2.** (a) $P = {10{.}000{.}000}/{1{,}063^{4}} =$ **$7.831.897**. (b) Al 7 %:
$P = {10{.}000{.}000}/{1{,}07^{4}} =$ **$7.628.952**; se perdieron **$202.944**, un **2,59 %**. (c)
$({10{.}000{.}000}/{7{.}650{.}000})^{1/4} - 1 =$ **6,93 %** anual. Lectura: un cero cupón no tiene cupones que
reinvertir, así que su rentabilidad al vencimiento está asegurada si lo mantienes; pero su precio es
el más sensible a la tasa para su plazo (unidad 8).

**7.3.** (a)

| Año | Saldo inicial | Interés 4,5 % | Amortización | Flujo | Saldo final |
|---|---|---|---|---|---|
| 1 | 900 | 40,50 | 300 | 340,50 | 600 |
| 2 | 600 | 27,00 | 300 | 327,00 | 300 |
| 3 | 300 | 13,50 | 300 | 313,50 | 0 |

(b) Al 5,2 %: $340{,}50/1{,}052 + 327/1{,}052^{2} + 313{,}50/1{,}052^{3} =$ **888,41 UF**, bajo la par
(el saldo es 900). (c) En $t = 1$ quedan 327,00 y 313,50: valen **594,11 UF**. El saldo de la deuda es
600 UF, así que se transa **bajo la par**, aunque el precio sea mucho menor que el nominal original.
Lectura: en un amortizable el valor par es el saldo, no los 900 del inicio.

**7.4. Falso** (o incierto, si se argumenta igual). Un bono del Fisco casi no tiene riesgo de
crédito, pero la rentabilidad no queda fija: (1) si lo vendes antes del vencimiento, el precio depende
de la tasa de ese día (**riesgo de tasa**); (2) si es un bullet, la YTM supone reinvertir los cupones a
esa misma tasa (**riesgo de reinversión**); (3) si hay que venderlo rápido puede haber descuento
(**liquidez**), y (4) si es en pesos, la rentabilidad real depende de la inflación. Lo fijo es el
cupón, no la rentabilidad. Solo un cero cupón en UF mantenido hasta el vencimiento asegura su
rentabilidad real desde el primer día.

**7.5.** (a) El precio está bajo el nominal, así que la YTM es **mayor** que 7,2 %. (b) Cupón $36.000.
Al 8 %, el precio es $486.751: el VAN del comprador es +$6.951. Al 9 %, el precio es $470.843 y
el VAN, −$8.957.

$$YTM \approx 8\,\% + 1\,\% \times \frac{6{.}951}{6{.}951 + 8{.}957} = 8{,}44\,\%$$

(c) La exacta es **8,43 %**. Lectura: la interpolación sobreestima un poco porque el VAN es una curva
convexa y la recta entre dos puntos queda sobre ella; con un punto de separación, el error está en el
segundo decimal.

**7.6.** (a) $i_{sem} = 1{,}046^{1/2} - 1 =$ **2,2741 %**. (b) Cupón $0{,}019 \times 3{.}000 = 57$ UF;
$P = 57 \cdot \frac{1 - 1{,}022741^{-14}}{0{,}022741} + \frac{3{.}000}{1{,}022741^{14}} =$
**2.866,70 UF**. (c) Con $4{,}6/2 = 2{,}3\,\%$ saldría 2.857,75 UF: **8,96 UF** menos por bono, y el
ejercicio queda malo aunque el método esté bien. (d) Sí: el cupón semestral de 1,9 % equivale a
$1{,}019^{2} - 1 = 3{,}84\,\%$ anual, menos que el 4,6 % de mercado.

**7.7.** (a) Cupón $110.000. En $t = 3$ quedan 5 flujos, descontados al 4,3 %:
$P_3 =$ **$2.105.949**, sobre la par porque la tasa bajó. (b) Flujo de Ignacio: −$2.000.000 en $t = 0$;
+$110.000 en $t = 1$ y $t = 2$; +$2.215.949 en $t = 3$ (el cupón más la venta). Al 7 % el VAN es
+$7.757; al 8 %, −$44.749:

$$r \approx 7\,\% + 1\,\% \times \frac{7{.}757}{7{.}757 + 44{.}749} = 7{,}15\,\%$$

La exacta también da **7,15 %**: mucho más que el 5,5 % de emisión, gracias a la ganancia de capital.
(c) Los cupones en la cuenta suman $110{.}000 \times (1{,}038^{2} + 1{,}038 + 1)$ = $342.699 en $t = 3$;
con la venta, $VF_3$ = $2.448.648. Rentabilidad efectiva:
$({2{.}448{.}648}/{2{.}000{.}000})^{1/3} - 1 =$ **6,98 %**.
Difiere de (b) porque la TIR supone reinvertir los cupones al 7,15 %, y Ignacio solo consiguió 3,8 %.

**7.8.** (a) Con 3 cupones por delante al 5,9 %: $P_{ex} =$ **101,87**.

| Momento | Precio sucio | Interés devengado | Precio limpio |
|---|---|---|---|
| hoy, recién pagado el cupón | 101,87 | 0 | 101,87 |
| 3 meses después ($f = 0{,}25$) | 103,35 | 1,65 | 101,70 |
| 9 meses después ($f = 0{,}75$) | 106,35 | 4,95 | 101,40 |
| un instante antes del cupón | 107,89 | 6,60 | 101,29 |
| un instante después del cupón | 101,29 | 0 | 101,29 |

(c) El sucio cae 6,60 de golpe el día del pago, porque el cupón sale del bono. El limpio llega a
101,29 por los dos lados: no salta. Muestra por qué se cotiza el limpio: sin cambios de tasa, solo se
mueve por la convergencia a la par (baja de 101,87 a 101,29 en el año, porque está sobre la par).

**7.9.** (a)

| Año | Flujo | Tasa spot | Valor presente |
|---|---|---|---|
| 1 | 8,2 | 4,4 % | 7,85 |
| 2 | 8,2 | 4,9 % | 7,45 |
| 3 | 108,2 | 5,5 % | 92,14 |
| | | **Precio** | **107,45** |

(b) La YTM que reproduce 107,45 es **5,44 %**: queda entre las tres tasas spot, cerca de la de 3 años,
porque ahí está el 86 % del valor. (c) El bono es 0,082 ceros a 1 año, 0,082 a 2 años y 1,082 a 3 años
(cada cero paga 100). Los ceros valen 95,79, 90,88 y 85,16, y el paquete cuesta 107,45. (d) Sí: el bono
está barato. Se **compra** el bono en 106,90 y se **vende** el paquete de ceros en 107,45: se ganan
**0,55** por bono hoy, y en los años 1 a 3 los cupones que se cobran pagan justo lo que se debe por
los ceros vendidos. A 106,90 la YTM sería 5,64 %, más que la de un bono idéntico. Muchos harían la
misma operación, el precio del bono subiría y la oportunidad se cerraría.

**7.10. Falso.** Con una curva spot que no es plana, la YTM depende del cupón. Con la curva del 7.9:

| Bono a 3 años | Precio con la curva spot | YTM |
|---|---|---|
| cupón 2 % | 90,60 | 5,48 % |
| cupón 10 % | 112,34 | 5,43 % |

Los dos están valorados con las mismas tasas spot, así que **ninguno** está mal valorado y no hay
arbitraje. El de cupón alto recibe más plata en los años 1 y 2, que se descuentan a tasas más bajas;
su «promedio» de tasas queda más bajo. La YTM es un resumen, no el precio de cada flujo: para buscar
arbitraje se compara cada bono con su paquete de ceros, no las YTM entre sí.

---

## 12. Caso integrador · Valentina y el bono de Eléctrica Andina

> Este caso sigue a Valentina, dueña del taller de serigrafía Estampa Sur, por todo el ramo. Acá se usa
> la curva spot de la unidad 6. Si no has hecho esa unidad, parte de los precios de los ceros de esta
> sección. Todo es ficticio: el emisor, el bono y las tasas.

En la unidad 5, Valentina decidió comprar la segunda máquina del taller con un pie hoy y un saldo de
$8.750.000 que paga en 3 años. Quiere guardar desde ya la plata de ese saldo en algo seguro, y su
corredor le muestra un bono de **Eléctrica Andina** (ficticia): bullet, 100 de nominal, cupón anual de
5,9 %, 4 años al vencimiento.

**Los datos de la unidad 6.** Los ceros a 1, 2, 3 y 4 años se transan en 95,42, 90,63, 85,77 y 80,94 por
cada 100 de nominal. De ahí salieron las tasas spot: 4,80 %, 5,04 %, 5,25 % y 5,43 %.

**Pregunta.** ¿Cuánto vale el bono, cómo se transa y cuál es su YTM?

**Desarrollo.**

1. **Flujos.** Cupón $0{,}059 \times 100 = 5{,}9$ en los años 1 a 3, y $105{,}9$ en el año 4.
2. **Precio con la curva spot.** El factor de cada año es el precio del cero dividido por 100:

| Año | Flujo | Tasa spot | Factor | Valor presente |
|---|---|---|---|---|
| 1 | 5,9 | 4,80 % | 0,954200 | 5,6298 |
| 2 | 5,9 | 5,04 % | 0,906300 | 5,3472 |
| 3 | 5,9 | 5,25 % | 0,857700 | 5,0604 |
| 4 | 105,9 | 5,43 % | 0,809400 | 85,7155 |
| | | | **Precio** | **101,7528** |

3. **Cómo se transa.** **Sobre la par**: 101,75 por cada 100, un premio de 1,75. El cupón de 5,9 %
   supera todas las tasas spot de la curva.
4. **La YTM a mano.** Al 5 % el bono valdría 103,19 (VAN $+1{,}44$); al 6 %, 99,65 (VAN $-2{,}10$):

$$YTM \approx 5\,\% + 1\,\% \times \frac{1{,}44}{1{,}44 + 2{,}10} = 5{,}41\,\%$$

   La exacta es **5,40 %** (descontar los cuatro flujos a 5,401 % devuelve 101,7528).

**Lectura.** La YTM de 5,40 % queda entre la tasa a 1 año (4,80 %) y la de 4 años (5,43 %), pegada a la
de 4 años porque el último flujo es el 84,2 % del precio. Valentina paga un premio, pero no pierde
nada: el precio sale de la misma curva que valora cualquier otro flujo, así que su VAN es cero. Lo que
sí le preocupa es otra cosa: el bono vence en 4 años y ella necesita la plata en 3. En $t = 3$ tendrá
que venderlo, y su precio ese día depende de la tasa. Si sube, pierde.

**Lo que pasa a la unidad 8.** El bono (precio **101,75**, YTM **5,40 %**) y un cero a 1 año se combinan
para **inmunizar** el saldo de $8.750.000: armar hoy una cartera que llegue a esa cifra en 3 años
aunque la tasa se mueva.

---

## 13. Para seguir

**En los libros del ramo.**

- Ross, Westerfield y Jaffe, *Finanzas corporativas* (9.ª ed., 2012), capítulo 8, que el programa fija
  para las semanas de valoración de bonos: tasas de interés y valoración de bonos, con cero cupón,
  bonos con cupón, clasificación de riesgo y estructura de tasas.
- Fabozzi, *The Handbook of Fixed Income Securities*, capítulos 2 y 9, los que fija el programa para
  la semana de riesgo de tasa.
- Brealey, Myers y Allen, *Principios de finanzas corporativas* (9.ª ed., 2010), en la lectura
  complementaria de la unidad.

**Abiertos y gratis.**

- Dahlquist y Knight, *Principles of Finance*, OpenStax (2022), en inglés. Capítulo 10, «Bonds and
  Bond Valuation»: características, valoración, curva de rendimientos, riesgos de tasa y de impago, y
  bonos en planilla. https://openstax.org/books/principles-finance/pages/10-why-it-matters

**Con el tutor.** Pega `tutor/contexto.md` al inicio de la conversación y pídele, por ejemplo: «Dame
un bono con cupón semestral que se venda antes del vencimiento, y corrígeme el flujo del tenedor paso a
paso».
