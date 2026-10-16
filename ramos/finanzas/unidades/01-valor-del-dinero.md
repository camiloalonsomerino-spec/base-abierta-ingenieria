---
ramo: Finanzas
unidad: 1
titulo: Valor del dinero en el tiempo
version: 0.1 (15-10-2026)
requiere: []
alimenta: [02-tasas-de-interes, 03-anualidades]
verificacion: verificacion/u01_valor_del_dinero.py
---

# Unidad 1 · Valor del dinero en el tiempo

**Qué vas a poder hacer.** Explicar para qué existen las finanzas corporativas y qué persigue el
administrador financiero; distinguir el interés simple del compuesto y explicar por qué el ramo
trabaja con el compuesto; llevar un monto de una fecha a otra (valor futuro y valor presente);
despejar el plazo y la tasa implícita de una operación; estimar un tiempo de duplicación con la regla
del 72, y comparar pagos que ocurren en fechas distintas sin sumar peras con manzanas.

**Lo que necesitas antes.** Potencias, raíces y logaritmos. Nada más: esta unidad es el piso de todo
el ramo.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. Para qué sirven las finanzas corporativas

Una empresa toma tres tipos de decisiones con plata:

| Decisión | Pregunta | Ejemplo |
|---|---|---|
| **Inversión** | ¿En qué activos ponemos el dinero? | Comprar una segunda máquina para el taller |
| **Financiamiento** | ¿Con qué plata pagamos esos activos? | Crédito bancario, aporte de los dueños, pagar con las ventas |
| **Capital de trabajo** | ¿Cómo manejamos la caja del día a día? | Cuánto plazo dar a los clientes, cuándo pagar a proveedores |

**El objetivo del administrador financiero** es maximizar el valor de la empresa para sus dueños (en
una sociedad abierta, el precio de la acción). No es maximizar la utilidad contable del año, por tres
razones:

1. La utilidad no mira **cuándo** llega la plata. Una ganancia en cinco años vale menos que la misma
   ganancia hoy, y la contabilidad las suma igual.
2. La utilidad no mira el **riesgo**. Dos proyectos con la misma utilidad esperada no valen lo mismo si
   uno es mucho más incierto.
3. La utilidad se puede mover con criterios contables; el valor depende de los flujos de caja.

Cuando quien decide (el gerente) no es el dueño, sus intereses pueden no calzar con los del dueño.
Ese es el **problema de agencia**, y por eso existen los directorios, los bonos por desempeño y las
auditorías.

**El mercado financiero** junta a quienes tienen plata que no usarán ahora (los que ofrecen capital:
personas que ahorran, fondos de pensiones, aseguradoras) con quienes la necesitan hoy (los que la
demandan: personas, empresas y el Estado). Los bancos son **intermediarios**: acercan a unos con otros
y ponen poco capital propio. El precio de ese arriendo de dinero es la **tasa de interés**, y no sale
de una fórmula: sale del **riesgo** de quien pide, del plazo y de la inflación que se espera. Por eso
dos personas piden el mismo crédito y reciben tasas distintas.

---

## 2. La idea de fondo: un peso hoy vale más que un peso mañana

Todo el ramo cuelga de esta frase. Hay tres razones, y conviene saberlas separadas:

1. **Costo de oportunidad.** El peso de hoy se puede invertir y mañana es más de un peso. Esperar
   significa renunciar a ese rendimiento.
2. **Inflación.** Con el tiempo el peso compra menos cosas.
3. **Riesgo.** El peso prometido para mañana puede no llegar.

La consecuencia práctica: **dos montos solo se pueden sumar o comparar si están en la misma fecha.**
Para moverlos en el tiempo se usa una tasa de interés. La paciencia tiene un precio, y ese precio se
puede calcular.

---

## 3. La línea de tiempo y la notación

Antes de cualquier fórmula se dibuja la línea de tiempo. El instante $t = 0$ es hoy; cada marca es un
período (mes, trimestre, año). Lo que recibes va con signo $+$ y lo que pagas con signo $-$.

| Símbolo | Significado |
|---|---|
| $VP$ | Valor presente: lo que vale el monto en $t = 0$ |
| $VF$ | Valor futuro: lo que vale el monto en $t = n$ |
| $i$ | Tasa de interés **por período** |
| $n$ | Número de períodos |

Dos operaciones, una de ida y otra de vuelta:

- **Capitalizar** es llevar un monto hacia adelante (sumarle los intereses).
- **Descontar** o **actualizar** es traerlo hacia el presente (quitarle los intereses que todavía no
  se ganan).

> **La regla que más puntos cuesta.** La tasa y los períodos tienen que estar en la misma unidad: tasa
> mensual con meses, tasa anual con años. Mezclarlas da un número, pero no significa nada. La
> unidad 2 enseña a convertir tasas; acá todos los datos ya vienen coherentes.

---

## 4. Interés simple contra interés compuesto

**Interés simple.** El interés de cada período se calcula siempre sobre el capital inicial. Los
intereses ganados quedan quietos y no generan más intereses. El crecimiento es **lineal**:

$$VF = VP\,(1 + i \cdot n)$$

**Interés compuesto.** El interés de cada período se suma al capital y desde el período siguiente
también genera intereses. El crecimiento es **exponencial**:

$$VF = VP\,(1 + i)^n$$

Esa acumulación de intereses sobre intereses se llama **anatocismo**. Con $800.000 al 1,5 % mensual:

| Mes | Interés simple | Interés compuesto | Diferencia (anatocismo) |
|---|---|---|---|
| 1 | $812.000 | $812.000 | 0 |
| 2 | $824.000 | $824.180 | \$180 |
| 3 | $836.000 | $836.543 | \$543 |
| 12 | $944.000 | $956.495 | $12.495 |
| 24 | $1.088.000 | $1.143.602 | $55.602 |

En el primer mes no hay diferencia: todavía no hay intereses que capitalizar. Después la brecha
crece cada vez más rápido, porque crece con $n$ en el exponente.

**Qué lugar ocupa cada uno.** Todo el ramo se trabaja con interés compuesto: es lo que hacen los
créditos, los depósitos y los bonos. El interés simple sirve para entender, por contraste, qué agrega
la capitalización.

**El interés simple equivalente.** Si alguien exige un rendimiento compuesto $i$ por $n$ períodos y lo
obligan a cobrar interés simple, para llegar al mismo valor final tiene que cobrar una tasa simple
mayor:

$$VP\,(1 + i_s\, n) = VP\,(1+i)^n \quad\Rightarrow\quad i_s = \frac{(1+i)^n - 1}{n}$$

Cambiar la fórmula no cambia lo que el prestamista exige; cambia el número que escribe en el contrato.
Esa es la base del ejercicio 1.9.

---

## 5. Valor futuro y valor presente de un monto único

Un **monto único** es un capital que se traslada en el tiempo sin pagos intermedios. Cuando hay
cuotas (un crédito, un plan de ahorro) son **series de pago**, que se ven en la unidad 3.

$$VF = VP\,(1+i)^n \qquad\qquad VP = \frac{VF}{(1+i)^n}$$

- $(1+i)^n$ es el **factor de capitalización**: cuántas veces se multiplica el capital.
- $\dfrac{1}{(1+i)^n}$ es el **factor de descuento**: qué fracción de hoy vale un peso futuro.

Mientras más lejos está el monto, o más alta es la tasa, menos vale hoy. El factor de descuento
siempre es menor que 1 si la tasa es positiva.

---

## 6. Despejar el plazo y la tasa

La ecuación $VF = VP\,(1+i)^n$ tiene cuatro variables. Con tres, sale la cuarta.

**El plazo**, con logaritmo (natural o en base 10, pero el mismo arriba y abajo):

$$n = \frac{\ln(VF/VP)}{\ln(1+i)}$$

El resultado sale en la unidad de la tasa: con tasa mensual, en meses. Si el enunciado pregunta en
qué mes se alcanza una meta, se redondea **hacia arriba**: en el mes anterior todavía no se llega.

**La tasa implícita**, con raíz enésima:

$$i = \left(\frac{VF}{VP}\right)^{1/n} - 1$$

Es el rendimiento (o el costo) que esconde una operación cuando solo se conocen los montos y las
fechas: un factoring, un precio al contado contra un precio a plazo, un descuento por pronto pago.

**La rentabilidad lleva apellido.** $VF/VP - 1$ es la rentabilidad **del período completo**. Si son
24 meses, es una rentabilidad **bienal** (cada dos años), no **bianual** (dos veces al año). Para
pasarla a un año se saca raíz, no se divide: la unidad 2 lo desarrolla.

---

## 7. La regla del 72

Para saber en cuánto tiempo se **duplica** un capital, se plantea $2 = (1+i)^n$, y el monto se cancela:
da lo mismo si son $100.000 o cien millones. El valor exacto es

$$n = \frac{\ln 2}{\ln(1+i)}$$

La **regla del 72** lo aproxima de cabeza:

$$n \approx \frac{72}{\text{tasa en \%}}$$

| Tasa anual | Años para duplicar (exacto) | Regla del 72 |
|---|---|---|
| 1 % | 69,7 | 72,0 |
| 6 % | 11,9 | 12,0 |
| 10 % | 7,3 | 7,2 |
| 20 % | 3,8 | 3,6 |

**Por qué funciona.** $\ln 2 = 0{,}693$, y para tasas chicas $\ln(1+i)$ es un poco menor que $i$. El 72
(en vez de 69,3) corrige justo eso cerca del 8 %, y además se divide fácil por 2, 3, 4, 6, 8, 9 y 12.
Lejos del 8 % la regla se equivoca más. Sirve para estimar y para detectar errores de cálculo; en un
certamen se usa la fórmula exacta.

---

## 8. Comparar flujos en distintas fechas

Para elegir entre alternativas que pagan en fechas distintas:

1. Dibuja la línea de tiempo de cada alternativa.
2. Elige una **fecha focal** (casi siempre hoy, $t = 0$).
3. Lleva cada monto a esa fecha con la tasa de oportunidad (capitalizando o descontando).
4. Recién ahí suma y compara.

**La fecha focal no cambia la decisión.** Pasar de una fecha a otra multiplica todos los valores por el
mismo factor $(1+i)^k$, así que el orden no cambia. Cambia el tamaño de la diferencia: medida en una
fecha más lejana, la ventaja se ve más grande, porque está expresada en pesos de esa fecha.

**La tasa de oportunidad** es lo que rendiría tu plata en la mejor alternativa de riesgo parecido. Si
cambia la tasa, puede cambiar la decisión: siempre conviene calcular la **tasa de indiferencia**, la
que deja las dos alternativas empatadas.

---

## 9. Ejemplo resuelto · vender el auto

Ignacio vende su auto. Tiene dos ofertas:

- **Oferta A:** $9.800.000 al contado hoy.
- **Oferta B:** $4.000.000 hoy y $6.300.000 dentro de 10 meses.

Su plata la tendría en un depósito que paga 0,9 % mensual. ¿Cuál le conviene?

**Paso 1 · La línea de tiempo.**

| Mes | 0 | 1 a 9 | 10 |
|---|---|---|---|
| Oferta A | +9.800.000 | 0 | 0 |
| Oferta B | +4.000.000 | 0 | +6.300.000 |

Sumar $4.000.000 y $6.300.000 y decir que B paga más ($10.300.000) es el error clásico: suma pesos de
fechas distintas.

**Paso 2 · Llevar todo a hoy.** Tasa mensual con meses: coherente. El factor de 10 meses es
$(1{,}009)^{10} = 1{,}09373$.

$$VP_B = 4{.}000{.}000 + \frac{6{.}300{.}000}{1{,}09373} = 4{.}000{.}000 + 5{.}760{.}085 = 9{.}760{.}085$$

$$VP_A = 9{.}800{.}000$$

La oferta A vale $39.915 más en pesos de hoy.

**Paso 3 · Comprobar en otra fecha.** En el mes 10:

$$VF_A = 9{.}800{.}000 \times 1{,}09373 = 10{.}718{.}592 \qquad VF_B = 4{.}000{.}000 \times 1{,}09373 + 6{.}300{.}000 = 4{.}374{.}935 + 6{.}300{.}000 = 10{.}674{.}935$$

A gana por $43.656 en pesos del mes 10, que es exactamente ${39{.}915} \times 1{,}09373$. Misma decisión;
la diferencia se ve más grande porque está en pesos futuros.

**Paso 4 · La tasa de indiferencia.** B equivale a recibir hoy $4.000.000 y dejarle al comprador los
$5.800.000 restantes, que devuelve como $6.300.000. Es un préstamo de Ignacio al comprador:

$$i^* = \left(\frac{6{.}300{.}000}{5{.}800{.}000}\right)^{1/10} - 1 = 0{,}830\ \%\ \text{mensual}$$

**Cómo se lee.**

- Con la oferta B, Ignacio le presta $5.800.000 al comprador por 10 meses y gana $500.000. Parece
  mucho, pero equivale a 0,830 % mensual, y su depósito le da 0,9 %.
- Si su tasa de oportunidad fuera menor que 0,830 % (por ejemplo, si la plata quedara en la cuenta
  corriente), convendría B.
- Falta un dato que la tabla no muestra: el **riesgo** de que el comprador no pague los $6.300.000.
  Ese riesgo empuja todavía más hacia A.

---

## 10. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Sumar montos de fechas distintas | Llévalos todos a una misma fecha focal antes de sumar |
| Tasa mensual con plazo en años (o al revés) | Antes de reemplazar, escribe la unidad de $i$ y de $n$ |
| Anualizar una rentabilidad de varios años dividiendo | Se saca raíz: $(1+r)^{1/n} - 1$ |
| Confundir bienal con bianual | Bienal = cada dos años; bianual = dos veces al año |
| Redondear hacia abajo el mes en que se llega a una meta | Si $n = 37{,}3$, recién en el mes 38 se alcanza |
| Usar la regla del 72 como si fuera exacta | Es una estimación; se aleja con tasas muy bajas o muy altas |
| Decidir por la tasa sin mirar el riesgo | Una tasa de oportunidad sirve solo si es de riesgo parecido |

---

## 11. Práctica

Diez ejercicios: 1.1 a 1.4 básicos, 1.5 a 1.8 intermedios, 1.9 y 1.10 de desafío. Dos son
**comentes** (1.3 y 1.9): se responde Verdadero, Falso o Incierto **con un argumento**; la palabra sola
no vale. Las pautas están en la sección 12.

**1.1 · Depósito a 30 meses (básico).** Martina deposita $2.350.000 al 0,65 % mensual durante 30
meses. Calcula el valor final con interés simple y con interés compuesto, la rentabilidad del período
en cada caso y cuánto se explica por anatocismo.

**1.2 · La matrícula (básico).** Necesitas $1.800.000 para pagar una matrícula dentro de 14 meses. Un
depósito paga 0,7 % mensual. ¿Cuánto tienes que depositar hoy? ¿Cuánto de la matrícula la pagan los
intereses?

**1.3 · Comente (básico).** «Si no existiera la inflación, un peso hoy valdría exactamente lo mismo que
un peso dentro de un año.»

**1.4 · El televisor a plazo (básico).** Una tienda vende un televisor a $489.990 al contado o a
$530.000 pagados en una sola vez dentro de 4 meses. (a) ¿Qué tasa mensual cobra la tienda por
esperar? (b) Tienes la plata en un depósito al 0,6 % mensual. ¿Te conviene pagar al contado o dejar la
plata depositada y pagar a los 4 meses?

**1.5 · Cuándo llego a la meta (intermedio).** Tienes $5.200.000 y quieres llegar a $7.000.000 con un
depósito al 0,8 % mensual. (a) ¿En qué mes llegas? Comprueba con el saldo del mes anterior y del mes
que encontraste. (b) ¿En cuántos meses se duplicaría el capital? Compara con la regla del 72.

**1.6 · Qué tan buena es la regla del 72 (intermedio).** (a) Calcula los años exactos para duplicar un
capital al 3 %, 8 %, 15 % y 36 % anual, y compáralos con la regla del 72. ¿Dónde se equivoca más y en
qué sentido? (b) Un fondo dice que «duplica tu inversión en 8 años». ¿Qué rentabilidad anual
compuesta es esa? ¿Por qué no es 12,5 %?

**1.7 · Tres ofertas por un terreno (intermedio).** Por un terreno te ofrecen $6.000.000 hoy,
$6.900.000 dentro de 18 meses o $7.500.000 dentro de 30 meses. Tu tasa de oportunidad es 0,75 %
mensual. (a) Ordena las ofertas por valor presente. (b) Compara las tres en el mes 30. (c) ¿Qué tasa
mensual deja empatadas la primera y la tercera?

**1.8 · Adelantar una factura (intermedio).** Una pyme tiene una factura de $3.900.000 que su cliente
pagará en 75 días. Una empresa de factoring le adelanta hoy $3.720.000 y se queda con la factura.
Usa meses de 30 días. (a) ¿Cuál es el costo mensual del adelanto? (b) Un crédito bancario le costaría
1,1 % mensual. ¿Cuánto tendría que adelantar el factoring para costar lo mismo?

**1.9 · Comente (desafío).** «Si la ley obligara a los bancos a cobrar interés simple en los créditos
de largo plazo, los deudores pagarían menos.» Apoya tu argumento con este caso: un crédito de
$12.000.000 que se paga en un solo pago a 8 años, por el que el banco exige 5,2 % anual compuesto.

**1.10 · El ahorro con un bono a mitad de camino (desafío).** Tienes $1.350.000 hoy y en el mes 12
recibirás un bono de $2.150.000, que también vas a depositar. Quieres juntar $4.300.000. El depósito
paga 0,6 % mensual. (a) ¿En qué mes llegas a la meta? (b) ¿Qué tasa mensual necesitarías para llegar
justo en el mes 24? (Pista: llama $x = (1+i)^{12}$.)

---

## 12. Pautas

**1.1.** Simple: ${2{.}350{.}000} \times (1 + 0{,}0065 \times 30) = 2{.}808{.}250$, rentabilidad 19,50 % en
30 meses. Compuesto: ${2{.}350{.}000} \times 1{,}0065^{30} = 2{.}854{.}179$, rentabilidad 21,45 % en 30 meses.
El anatocismo explica $45.929: intereses que ganaron los intereses. Ninguna de las dos rentabilidades
es anual; las dos son del período de 30 meses.

**1.2.** $VP = 1{.}800{.}000 / 1{,}007^{14} = 1{.}632{.}525$. Hoy depositas $1.632.525 y los intereses pagan
$167.475 de la matrícula. Lectura: el factor de descuento de 14 meses es cerca de 0,907; cada peso
de la matrícula te cuesta 91 centavos de hoy.

**1.3. Falso.** La inflación es solo una de las tres razones del valor del dinero en el tiempo. Aunque
los precios no cambiaran, el peso de hoy se puede invertir en algo productivo y dentro de un año ser
más de un peso: esperar tiene un **costo de oportunidad** (la tasa real es positiva porque el capital
produce y porque la gente prefiere consumir antes). Además, el peso futuro es una promesa y tiene
**riesgo** de no llegar. Por eso, sin inflación, quien presta igual exige una tasa: la tasa real. La
afirmación solo sería cierta en un mundo sin rendimiento real y sin riesgo, que no es el caso.

**1.4.** (a) $i = (530{.}000/489{.}990)^{1/4} - 1 = 1{,}982\ \%$ mensual. El recargo es $40.010 por cuatro
meses. (b) Conviene pagar al contado. Si dejas $489.990 depositados, en 4 meses tienes $501.856, que
no alcanzan para los $530.000. Dicho en tasas: la tienda te cobra 1,982 % mensual y tu plata solo gana
0,6 %; financiarse caro para invertir barato pierde.

**1.5.** (a) $n = \ln(7{.}000{.}000/5{.}200{.}000)/\ln 1{,}008 = 37{,}30$ meses. En el mes 37 tienes $6.983.016
(todavía no llegas); en el mes 38, $7.038.880. Llegas en el **mes 38**. (b) Duplicar toma
$\ln 2 / \ln 1{,}008 = 87{,}0$ meses; la regla del 72 da $72/0{,}8 = 90{,}0$ meses. Con una tasa mensual
chica la regla sobreestima unos tres meses (como en el 1 % anual de la sección 7).

**1.6.** (a)

| Tasa anual | Exacto (años) | Regla del 72 |
|---|---|---|
| 3 % | 23,45 | 24,00 |
| 8 % | 9,01 | 9,00 |
| 15 % | 4,96 | 4,80 |
| 36 % | 2,25 | 2,00 |

Cerca del 8 % es casi exacta. Con tasas bajas sobreestima el plazo; con tasas altas lo subestima, y a
36 % se equivoca en un cuarto de año (11 %). (b) $i = 2^{1/8} - 1 = 9{,}05\ \%$ anual. El 12,5 % sale
de dividir 100 % entre 8 años, que es pensar con interés simple: supone que las ganancias de cada año
no generan nada. Con capitalización basta una tasa menor para duplicar. La regla del 72 lo confirma:
$72/8 = 9$.

**1.7.** (a) VP: oferta 1 = $6.000.000; oferta 2 = ${6{.}900{.}000} / 1{,}0075^{18} = 6{.}031{.}677$; oferta 3 =
${7{.}500{.}000} / 1{,}0075^{30} = 5{.}993{.}902$. Orden: **2, 1, 3**. (b) En el mes 30: oferta 1 =
$7.507.631; oferta 2 = $7.547.268; oferta 3 = $7.500.000. Mismo orden, como garantiza la sección 8.
(c) $i = (7{.}500{.}000/6{.}000{.}000)^{1/30} - 1 = 0{,}747\ \%$ mensual, apenas bajo tu 0,75 %: por eso la
tercera pierde por poco. Entre la 1 y la 2 la tasa implícita es 0,779 %, mayor que 0,75 %: esperar 18
meses se paga bien. Pero esperar 12 meses más (de la 2 a la 3) rinde solo 0,697 % mensual.

**1.8.** (a) 75 días son 2,5 meses. $i = (3{.}900{.}000/3{.}720{.}000)^{1/2{,}5} - 1 = 1{,}908\ \%$ mensual. El
costo en pesos son $180.000, pero lo que se compara es la tasa: casi el doble del crédito bancario.
(b) Para costar 1,1 % mensual, el adelanto tendría que ser ${3{.}900{.}000} / 1{,}011^{2{,}5} = 3{.}794{.}781$.
Lectura: el factoring da liquidez inmediata y sin papeleo de crédito, y eso se paga. Que una empresa
no tenga caja hoy no significa que sea insolvente.

**1.9. Falso.** La tasa no la fija la fórmula: la fija lo que el banco exige por el riesgo del deudor y
por su costo de oportunidad. Con 5,2 % compuesto, a 8 años el deudor debe
${12{.}000{.}000} \times 1{,}052^8 = 18{.}001{.}437$. Si la ley obliga a interés simple, el banco cobra la tasa
simple que llega al mismo monto: $i_s = (1{,}052^8 - 1)/8 = 6{,}251\ \%$ anual, y la deuda vuelve a ser
$18.001.437. El deudor paga lo mismo; solo cambia el número del contrato, que ahora se ve más alto.
Y la brecha crece con el plazo: a 20 años la tasa simple equivalente es 8,781 %. Las familias pagarían
menos solo si el banco no pudiera subir la tasa (por ejemplo, con un techo legal): con la misma tasa
de 5,2 % simple la deuda sería $16.992.000. Pero entonces el crédito deja de compensar el riesgo, el
banco presta menos o deja de prestarles a los deudores más riesgosos, y quienes ofrecen capital buscan
otro destino. Menos oferta de capital sube el precio del dinero: la medida termina subiendo las tasas
o cerrando el acceso al crédito.

**1.10.** (a) Se lleva todo a hoy y se trata como un solo capital. El bono vale hoy
${2{.}150{.}000}/1{,}006^{12} = 2{.}001{.}072$; el total equivale a $3.351.072 en $t = 0$. Entonces
$n = \ln(4{.}300{.}000/3{.}351{.}072)/\ln 1{,}006 = 41{,}68$ meses. En el mes 41 tienes $4.282.535 y en el 42,
$4.308.231: llegas en el **mes 42**. La fórmula vale porque la meta se alcanza después del mes 12 (si
no, el bono todavía no habría entrado). (b) En el mes 24: ${1{.}350{.}000}\,x^2 + 2{.}150{.}000\,x = 4{.}300{.}000$,
con $x = (1+i)^{12}$. Es una cuadrática; la raíz positiva es $x = 1{,}15800$, y
$i = 1{,}15800^{1/12} - 1 = 1{,}230\ \%$ mensual. Más del doble de lo que paga el depósito: la meta a 24
meses no se logra solo con intereses; habría que ahorrar más.

---

## 13. Caso integrador · Valentina, el ahorro de hoy

> Este caso sigue a Valentina, dueña de Estampa Sur (el taller de serigrafía del caso de Gestión de
> Operaciones), por todo el ramo. Todo es ficticio. Cada unidad parte de lo que calculó la anterior.
> La fuente de las cifras es `verificacion/caso_valentina.py`.

Valentina quiere comprarse un departamento en tres años y empieza por lo que ya tiene: **$3.460.000
ahorrados**. Los deja en una cuenta que paga **0,55 % mensual** durante **36 meses**.

**Pregunta.** ¿Cuánto tendrá al cabo de los tres años? ¿Cuánto cambia si la cuenta pagara interés
simple?

**Desarrollo.**

| | Interés simple | Interés compuesto |
|---|---|---|
| Fórmula | ${3{.}460{.}000} \times (1 + 0{,}0055 \times 36)$ | ${3{.}460{.}000} \times 1{,}0055^{36}$ |
| Valor en el mes 36 | $4.145.080 | **$4.215.322** |

Con interés simple, cada mes gana los mismos $19.030 (el 0,55 % del capital inicial). Con compuesto
gana un poco más cada mes. La diferencia, **$70.242**, es el anatocismo de tres años.

- La rentabilidad del período es 21,83 % en 36 meses (trienal), no anual.
- Al 0,55 % mensual su plata se duplicaría en 126,4 meses (más de diez años y medio). La regla del 72
  estima 130,9 meses: sobreestima, como con toda tasa chica.
- Ese 0,55 % mensual equivale a 6,80 % al año, no a $0{,}55 \times 12 = 6{,}6\ \%$. De dónde sale y
  qué banco le conviene es la pregunta de la unidad 2.

**Lectura.** Los $4.215.322 son pesos del mes 36, no pesos de hoy. Para saber cuánto poder de compra
ganó, falta la inflación (unidad 2).

**Lo que pasa a las unidades siguientes.** La unidad 2 explica la tasa: compara dos bancos y calcula
cuánto gana Valentina en términos reales. La unidad 3 usa el valor futuro del ahorro, **$4.215.322**,
como punto de partida para calcular cuánto depositar al mes para juntar el pie del departamento.

---

## 14. Para seguir

**En los libros del ramo.**

- Ross, Westerfield y Jaffe, *Finanzas corporativas* (9.ª ed., 2012), capítulos 1 y 4 (los que fija el
  programa): qué es la empresa, el objetivo del administrador financiero, el problema de agencia y la
  valoración de montos únicos con flujos descontados.
- Brealey, Myers y Allen, *Principios de finanzas corporativas* (9.ª ed., 2010), capítulos 1 y 2 de la
  lectura que fija el programa: el rol del administrador financiero y cómo calcular valores
  presentes.

**Abierto y gratis.**

- Dahlquist y Knight, *Principles of Finance*, OpenStax (2022), en inglés, capítulo 7 (valor del dinero
  en el tiempo: conceptos de ahora contra después, valor presente y futuro, despejar plazo y tasa).
  Licencia CC BY-NC-SA: https://openstax.org/books/principles-finance/pages/7-why-it-matters

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame dos ofertas de pago en fechas distintas,
déjame elegir y corrígeme la línea de tiempo».
