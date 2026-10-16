---
ramo: Finanzas
unidad: 2
titulo: Tasas de interés
version: 0.1 (15-10-2026)
requiere: [01-valor-del-dinero]
alimenta: [03-anualidades, 04-creditos-y-amortizacion, 06-estructura-de-tasas]
verificacion: verificacion/u02_tasas.py
---

# Unidad 2 · Tasas de interés

**Qué vas a poder hacer.** Leer una tasa con su apellido completo (período, nominal o efectiva, en
pesos o en UF); pasar de una tasa nominal a la efectiva con cualquier frecuencia de capitalización,
incluida la continua; convertir una tasa de un período a otro sin dividir ni multiplicar; separar
la inflación con la ecuación de Fisher; explicar qué es la UF y por qué una tasa «UF + x %» es real, y
explicar qué es la tasa máxima convencional y qué efecto tiene un techo a la tasa.

**Lo que necesitas antes.** La unidad 1: valor futuro y presente de un monto único, y despejar la tasa
con raíz enésima.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. Una tasa siempre tiene apellido

«Un 9 %» no dice nada. Para usar una tasa hay que saber tres cosas:

1. **De qué período es.** Mensual, trimestral, anual.
2. **Si es nominal o efectiva.** Si ya incluye la capitalización o no.
3. **En qué unidad está.** En pesos (incluye la inflación) o en UF (no la incluye).

**Tasa nominal anual** ($j$) con capitalización $m$ veces al año: es una forma de **escribir** la tasa,
no de pagarla. La tasa que de verdad se aplica en cada subperíodo es $j/m$. «12 % anual capitalizable
mensualmente» significa 1 % cada mes.

**Tasa efectiva** de un período: lo que de verdad crece un peso en ese período, con toda la
capitalización adentro. La **tasa efectiva anual** (TEA) es

$$TEA = \left(1 + \frac{j}{m}\right)^m - 1$$

> **Regla corta.** La nominal se **divide** (para sacar la tasa del subperíodo). La efectiva se
> convierte con **potencia o raíz**. Confundirlas es el error de arrastre que arruina un ejercicio
> completo.

**Los dos «nominal».** La palabra se usa para dos cosas distintas y conviene no mezclarlas:

| Se opone a | Qué significa «nominal» | Qué la corrige |
|---|---|---|
| Efectiva | Tasa escrita sin capitalizar | La frecuencia de capitalización |
| Real | Tasa (o flujo) en pesos, con la inflación adentro | La inflación (Fisher) |

---

## 2. Frecuencia de capitalización

Mientras más seguido se capitaliza, más intereses ganan los intereses. Con una tasa nominal de 9 %:

| Capitalización | $m$ | Tasa del subperíodo | TEA |
|---|---|---|---|
| Anual | 1 | 9 % | 9,000 % |
| Semestral | 2 | 4,5 % | 9,202 % |
| Trimestral | 4 | 2,25 % | 9,308 % |
| Mensual | 12 | 0,75 % | 9,381 % |
| Diaria | 365 | 0,0247 % | 9,416 % |
| Continua | $\infty$ | no aplica | 9,417 % |

La TEA sube con $m$, pero cada vez menos: tiene un techo. Ese techo es la **capitalización continua**:

$$\lim_{m\to\infty}\left(1 + \frac{j}{m}\right)^m = e^{j} \qquad\Rightarrow\qquad TEA = e^{j} - 1$$

Con capitalización continua, el valor futuro de un monto a $t$ años (con $t$ que puede ser fracción) es

$$VF = VP\,e^{j\,t}$$

y la tasa continua que equivale a una efectiva anual dada es $j = \ln(1 + TEA)$.

**Dónde se usa.** En modelos de valoración (opciones, bonos en tiempo continuo) y en evaluación
económica. En un crédito de consumo no la vas a ver, pero sirve de cota: ninguna frecuencia de
capitalización hace que una tasa nominal de 9 % rinda más de 9,417 % al año.

---

## 3. Tasas equivalentes entre períodos

Dos tasas son **equivalentes** si hacen crecer un peso exactamente lo mismo en el mismo tiempo. Si un
período largo contiene $k$ períodos cortos:

$$(1 + i_{\text{largo}}) = (1 + i_{\text{corto}})^{k} \qquad\Rightarrow\qquad i_{\text{corto}} = (1 + i_{\text{largo}})^{1/k} - 1$$

- **De corto a largo** (de mes a año): se **eleva** a $k$.
- **De largo a corto** (de año a mes): se saca **raíz** $k$.
- **Nunca se divide ni se multiplica** una tasa efectiva por el número de períodos.

La pregunta para encontrar $k$ es siempre «¿cuántos períodos cortos caben en el largo?». De año a
trimestre, $k = 4$ (no 3, que son los meses del trimestre).

Con una TEA de 9 %:

| Período | Tasa equivalente |
|---|---|
| Mensual | $(1{,}09)^{1/12} - 1 = 0{,}7207\ \%$ |
| Trimestral | $(1{,}09)^{1/4} - 1 = 2{,}1778\ \%$ |
| Semestral | $(1{,}09)^{1/2} - 1 = 4{,}4031\ \%$ |

**Por qué dividir sobreestima.** $9\ \%/12 = 0{,}75\ \%$ mensual. Capitalizado 12 meses da 9,381 %, más
que el 9 % de partida: la división olvida que los intereses de cada mes también ganan intereses.
(Fíjate que 0,75 % mensual es justo la tasa del subperíodo de un 9 % **nominal** capitalizable
mensualmente: dividir convierte, sin querer, una efectiva en una nominal.)

**Cuando el enunciado dice «7 % anual» a secas.** Hay dos lecturas posibles: efectiva (se saca raíz) o
nominal (se divide). Escribe en una línea qué supones. Un supuesto declarado no se castiga; uno
escondido se lee como error.

**Adelanto: el CAE.** En los créditos de consumo e hipotecarios, la ley obliga a informar el **costo
anual equivalente**, que suma a la tasa los gastos y seguros del crédito. Se calcula en la unidad 4.

---

## 4. Tasa real e inflación

La tasa en pesos (nominal) mezcla dos cosas: lo que crece tu poder de compra y lo que suben los
precios. La **ecuación de Fisher** las separa. Con $n$ la tasa nominal, $r$ la real y $\pi$ la inflación,
todas del mismo período:

$$(1 + n) = (1 + r)(1 + \pi) \qquad\Rightarrow\qquad r = \frac{1 + n}{1 + \pi} - 1$$

La inflación **no se resta, se descuenta**: también es compuesta. La **aproximación** $r \approx n - \pi$
sirve para cuentas rápidas, pero se aleja cuando la inflación es alta:

| Nominal | Inflación | Real exacta | Aproximación $n - \pi$ |
|---|---|---|---|
| 10 % | 2 % | 7,84 % | 8 % |
| 40 % | 30 % | 7,69 % | 10 % |

La diferencia es $r \cdot \pi$, que con inflaciones de un dígito es chica y con inflaciones altas no.

**Dos reglas que se preguntan siempre.**

- **Flujo nominal con tasa nominal; flujo real con tasa real.** Cruzarlas es un error clásico.
- **La inflación que importa al decidir es la esperada.** Al firmar un depósito a tasa fija en pesos,
  la tasa real que vas a obtener depende de la inflación que efectivamente ocurra. Si la inflación
  resulta mayor que la esperada, el ahorrante pierde poder de compra y el deudor gana.

---

## 5. La UF, una unidad que se reajusta sola

La **Unidad de Fomento** (UF) es una unidad de cuenta chilena que existe desde 1967. No es una
moneda: nadie paga con billetes de UF. Es una regla para convertir: su valor en pesos lo publica el
Banco Central y cambia todos los días. Entre el día 10 de un mes y el día 9 del siguiente, la UF
avanza de a poco hasta acumular la variación del IPC (el índice de precios) del mes anterior.

**Qué consigue.** Un monto en UF mantiene su poder de compra: si los precios suben 4 %, la UF sube
aproximadamente 4 %. Por eso:

- Una tasa «UF + 2 %» es una **tasa real**: 2 % por sobre la inflación.
- Un dividendo hipotecario de 20 UF es constante en UF y sube en pesos con la inflación. El esfuerzo
  real del deudor no cambia, pero el monto en pesos sí.
- Un crédito largo (20 o 30 años) se pacta en UF porque a ese plazo nadie quiere asumir el riesgo de
  la inflación en pesos fijos.

**Ejemplo con una UF ficticia.** Supón que hoy 1 UF = $30.000 y que la inflación del año será 4 %.
Depositas 500 UF ($15.000.000) a un año a UF + 2 %.

- Al final del año recibes $500 \times 1{,}02 = 510$ UF.
- La UF sube a ${30{.}000} \times 1{,}04 = 31{.}200$ pesos.
- Recibes $510 \times 31{.}200 = 15{.}912{.}000$ pesos.

La tasa en pesos fue $1{,}02 \times 1{,}04 - 1 = 6{,}08\ \%$: Fisher en acción. El 2 % real estaba
asegurado; el 6,08 % nominal dependía de la inflación.

**Quién carga el riesgo de inflación.** En un crédito en pesos a tasa fija, lo carga el banco: si la
inflación sube, le devuelven pesos que valen menos. En un crédito en UF lo carga el deudor: su deuda
en pesos sube con la inflación, aunque su sueldo quizás no.

---

## 6. Tasa máxima convencional y usura

**La regla.** En Chile, la Ley 18.010 regula las operaciones de crédito de dinero. Define el **interés
corriente**: el promedio que se cobra en un tipo de operación, que calcula y publica la Comisión para
el Mercado Financiero (CMF). Sobre él fija un techo, la **tasa máxima convencional** (TMC): no se puede
pactar un interés mayor. La regla general pone el techo un 50 % por sobre el interés corriente; para
los créditos de montos pequeños la ley usa otra fórmula. Si un contrato pacta más que el máximo, ese
pacto se tiene por no escrito y el interés baja al corriente. Cobrar intereses abusivos (la
**usura**) es, además, un delito que sanciona el Código Penal.

**El efecto económico.** El techo protege a quien igual consigue el crédito: paga menos. Pero la tasa
es el precio del **riesgo** del deudor. Si para un deudor riesgoso la tasa que compensa su riesgo
queda por encima del techo, el prestamista no baja la tasa: **no le presta**. Ese racionamiento deja
fuera del crédito formal a los más riesgosos, que terminan en el mercado informal, sin protección y
a tasas más altas. Un techo intercambia precio por acceso.

**Al comparar contra el techo**, mira el apellido: la tasa de la oferta y la del techo tienen que estar
en el mismo período y de la misma forma (ejercicio 2.5). Las cifras vigentes se consultan en la CMF el
día que se necesitan; este ramo no las memoriza.

---

## 7. Adelanto: la estructura de tasas

La tasa no es una sola: depende del **plazo**. Un depósito a un año y uno a tres años, del mismo
banco, pagan tasas anuales distintas. La relación entre plazo y tasa es la **estructura de tasas** (o
curva de rendimiento). De ella salen:

- Las **tasas spot**: la tasa anual de hoy para un plazo dado.
- Las **tasas forward** (implícitas): la tasa que la curva de hoy «promete» para un período futuro.
  Si a un año pagan $s_1$ y a dos años $s_2$ (anual), la tasa implícita del segundo año es
  $\frac{(1+s_2)^2}{1+s_1} - 1$.

La curva sube, baja o se dobla según lo que el mercado espera de las tasas y de la inflación, y según
el premio que exige por prestar a más plazo. Se desarrolla en la unidad 6; el ejercicio 2.10 la
asoma.

---

## 8. Ejemplo resuelto · elegir el crédito para el viaje

Fernanda quiere pagar un viaje de $2.400.000 con un crédito de consumo que paga **de una sola vez a
los 9 meses** (las cuotas son la unidad 3). Tiene tres ofertas:

- **Banco X:** 1,45 % mensual.
- **Banco Y:** 18,2 % anual, nominal, capitalizable mensualmente.
- **Caja Z:** 19,1 % efectiva anual.

A primera vista Y es la más barata (18,2 es el número más chico). ¿Lo es?

**Paso 1 · Poner las tres en la misma moneda: TEA.**

- X es efectiva mensual: se eleva. $TEA_X = (1{,}0145)^{12} - 1 = 18{,}86\ \%$.
- Y es nominal: primero se divide, después se eleva. $0{,}182/12 = 1{,}5167\ \%$ mensual y
  $TEA_Y = (1{,}015167)^{12} - 1 = 19{,}80\ \%$.
- Z ya es efectiva anual: 19,1 %.

**Paso 2 · Comprobar en mensual.** Para Z se saca raíz: $(1{,}191)^{1/12} - 1 = 1{,}4673\ \%$ mensual.

| Oferta | Mensual | TEA | Orden |
|---|---|---|---|
| X | 1,4500 % | 18,86 % | 1.º |
| Z | 1,4673 % | 19,10 % | 2.º |
| Y | 1,5167 % | 19,80 % | 3.º |

El orden es el mismo en mensual y en anual, como tiene que ser.

**Paso 3 · Pasarlo a pesos.** Se paga ${2{.}400{.}000} \times (1 + i_{mensual})^9$:

| Oferta | Pago a los 9 meses | Intereses |
|---|---|---|
| X | $2.731.994 | $331.994 |
| Z | $2.736.183 | $336.183 |
| Y | $2.748.194 | $348.194 |

Elegir Y por «tener la tasa más baja» le habría costado $16.200 más que X.

**Paso 4 · El costo real.** Si la inflación esperada es 3,8 % anual, el costo real de X es

$$r = \frac{1{,}1886}{1{,}038} - 1 = 14{,}51\ \%$$

Restando se obtendría $18{,}86 - 3{,}8 = 15{,}06\ \%$: la resta exagera el costo real en más de medio
punto.

**Cómo se lee.**

- Y escribe su tasa como nominal: el 18,2 % no incluye la capitalización mensual. Por eso el número
  publicado es el más bajo y la oferta es la más cara.
- Las ofertas solo se comparan en la misma forma (todas efectivas) y el mismo período.
- En términos reales el viaje le cuesta a Fernanda 14,51 % al año: ese es el sacrificio de poder de
  compra por adelantar el viaje.

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Dividir una tasa efectiva anual por 12 | Se saca raíz 12; dividir sobreestima la tasa mensual |
| Elevar una tasa nominal sin dividirla primero | Nominal: $j/m$ y recién ahí se eleva a $m$ |
| Comparar créditos por el número publicado | Pasa todas las ofertas a TEA antes de comparar |
| Restar la inflación | Fisher: $(1+n)/(1+\pi) - 1$; la resta es solo aproximación |
| Descontar flujos en pesos con una tasa real | Flujo nominal con tasa nominal; flujo real con tasa real |
| De año a trimestre usar $k = 3$ | $k$ es cuántos trimestres caben en el año: 4 |
| Creer que una tasa en UF es «más baja» que una en pesos | Una es real y la otra nominal; compáralas con Fisher |

---

## 10. Práctica

Diez ejercicios: 2.1 a 2.4 básicos, 2.5 a 2.8 intermedios, 2.9 y 2.10 de desafío. Dos son **comentes**
(2.4 y 2.9): se responde Verdadero, Falso o Incierto **con un argumento**; la palabra sola no vale. Las
pautas están en la sección 11.

**2.1 · Una tasa, cuatro frecuencias (básico).** Una tasa nominal anual de 10,8 %. Calcula la TEA si se
capitaliza trimestral, mensual y diariamente (365 días), y con capitalización continua. ¿Qué pasa con
las diferencias a medida que $m$ crece?

**2.2 · Convertir sin dividir (básico).** (a) Un depósito tiene una TEA de 7,4 %. Calcula su tasa
mensual, trimestral y semestral equivalente. ¿Cuánto da si divides por 12, y en qué sentido se
equivoca? (b) Una tarjeta cobra 1,2 % mensual. ¿Cuál es su TEA? Compárala con multiplicar por 12.

**2.3 · Lo que ganaste de verdad (básico).** Un depósito a un año rindió 5,9 % y la inflación de ese
año fue 4,3 %. Calcula la rentabilidad real exacta y la aproximada. ¿Cuánto se equivoca la
aproximación?

**2.4 · Comente (básico).** «Entre dos créditos, el que publica la tasa anual más baja es siempre el más
barato.» Para tu argumento, usa este par: un crédito A a 14,9 % nominal anual capitalizable
mensualmente y un crédito B a 15,8 % efectivo anual.

**2.5 · La tienda y el techo (intermedio).** Una tienda cobra 2,85 % mensual en su crédito. Supón (cifra
ficticia) que el techo legal para ese tipo de crédito es 38 % anual expresado como **tasa efectiva**.
(a) ¿La tienda supera el techo? (b) ¿Cuál es la tasa mensual máxima que podría cobrar? (c) Si el
mismo 38 % fuera una tasa **nominal** anual capitalizable mensualmente, ¿cambia la respuesta?

**2.6 · Depósito en pesos o en UF (intermedio).** Un banco ofrece un depósito a un año en pesos a 6,45 %
o en UF a UF + 2,35 %. La inflación esperada es 3,55 %. (a) ¿Cuál rinde más en lo esperado? (b) ¿Con
qué inflación quedan empatados? (c) Si la inflación resulta 5 %, ¿cuánto rindió cada uno en términos
reales? (d) ¿Qué estás comprando al elegir la UF?

**2.7 · Capitalización continua (intermedio).** Un fondo paga 5,7 % anual con capitalización continua y
otro paga 5,85 % efectivo anual. (a) ¿Cuál paga más? (b) ¿Qué tasa continua equivale al 5,85 %
efectivo? (c) ¿Cuánto tendrías en cada uno al cabo de 2,5 años si inviertes $2.750.000?

**2.8 · «Paga 4,4 % anual» (intermedio).** Un depósito a 6 meses de $8.000.000 «paga 4,4 % anual». (a)
Calcula lo que recibes si el 4,4 % es nominal (se divide) y si es efectivo (se saca raíz). (b) ¿Cuánto
es la diferencia en pesos? (c) Si la lectura nominal fuera la correcta y renovaras el depósito por
otros 6 meses a la misma tasa, ¿cuál sería la TEA?

**2.9 · Comente (desafío).** «Un crédito hipotecario a UF + 3,9 % es más barato que uno en pesos a
7,3 % anual fijo, porque 3,9 es menor que 7,3.»

**2.10 · Ahorro en tres tramos y una tasa implícita (desafío).** (a) Depositas $4.100.000 durante 24
meses: los primeros 8 meses al 0,5 % mensual, los 10 siguientes a 6,9 % efectivo anual y los últimos 6
a 6,3 % nominal anual capitalizable mensualmente. Calcula el saldo al final de cada tramo, la tasa
mensual equivalente de los 24 meses y su TEA. Con una inflación de 3,5 % anual, ¿cuál fue la
rentabilidad real anual y cuánto vale el saldo final en pesos de hoy? (b) Otro banco paga 5,6 % anual
por un depósito a un año y 6,0 % anual por uno a dos años. ¿Qué tasa implícita está pagando por el
segundo año?

---

## 11. Pautas

**2.1.**

| Capitalización | TEA |
|---|---|
| Trimestral (2,7 % por trimestre) | 11,245 % |
| Mensual (0,9 % por mes) | 11,351 % |
| Diaria | 11,403 % |
| Continua ($e^{0{,}108} - 1$) | 11,405 % |

Las diferencias se achican: de trimestral a mensual se ganan 0,11 puntos; de diaria a continua, 0,002.
La continua es el techo.

**2.2.** (a) Mensual: $1{,}074^{1/12} - 1 = 0{,}5967\ \%$. Trimestral: 1,8008 %. Semestral: 3,6340 %.
Dividiendo, $7{,}4/12 = 0{,}6167\ \%$: sobreestima la tasa mensual, porque ignora que los intereses de
cada mes también ganan intereses. (b) $TEA = 1{,}012^{12} - 1 = 15{,}389\ \%$. Multiplicar da 14,4 %:
subestima casi un punto. Es el mismo error al revés.

**2.3.** Exacta: $1{,}059/1{,}043 - 1 = 1{,}534\ \%$. Aproximada: $5{,}9 - 4{,}3 = 1{,}6\ \%$. La resta
exagera en 0,066 puntos. Lectura: de un 5,9 % que «se veía», el poder de compra creció 1,5 %. La
mayor parte del rendimiento solo compensó la inflación.

**2.4. Falso.** La tasa publicada puede ser nominal o efectiva, y solo las efectivas del mismo período
se pueden comparar. A publica 14,9 %, pero es nominal: cobra $14{,}9/12 = 1{,}2417\ \%$ mensual y su TEA
es 15,96 %. B publica 15,8 %, que ya es efectiva: equivale a 1,2300 % mensual. **B es más barato**
aunque su número sea más alto. Además, aun con las dos tasas en TEA, el costo total de un crédito
incluye gastos y seguros que la tasa no muestra; por eso la ley exige informar el CAE. La regla
correcta es comparar la tasa efectiva del mismo período o, mejor, el costo total equivalente.

**2.5.** (a) $TEA = 1{,}0285^{12} - 1 = 40{,}10\ \%$, mayor que 38 %: **supera el techo**, aunque multiplicar
2,85 × 12 = 34,2 % parezca dejarla bajo él. (b) $1{,}38^{1/12} - 1 = 2{,}720\ \%$ mensual. (c) Sí cambia. Si el techo
fuera nominal, la tasa mensual máxima sería $38/12 = 3{,}167\ \%$ (que equivale a una TEA de 45,37 %),
y 2,85 % mensual quedaría dentro. La misma cifra de techo permite tasas muy distintas según cómo se
exprese: por eso siempre se lee el apellido de la tasa antes de comparar.

**2.6.** (a) El de UF rinde en pesos $1{,}0235 \times 1{,}0355 - 1 = 5{,}983\ \%$ esperado, menos que el
6,45 % del de pesos. En reales, el de pesos da $1{,}0645/1{,}0355 - 1 = 2{,}801\ \%$ contra el 2,35 % del
de UF. En lo esperado gana el de pesos. (b) Empatan con una inflación de
$1{,}0645/1{,}0235 - 1 = 4{,}006\ \%$. (c) Con 5 %: el de pesos rinde solo 1,381 % real; el de UF sigue en 2,35 % real (7,468 % en
pesos). (d) Con la UF compras un **seguro contra la inflación**: renuncias a algo de rendimiento
esperado a cambio de asegurar el rendimiento real. Elegir el de pesos es apostar a que la inflación
quedará bajo 4,006 %.

**2.7.** (a) $e^{0{,}057} - 1 = 5{,}866\ \%$ efectivo, más que 5,85 %: **paga más el de capitalización
continua**, aunque su número sea menor. (b) $\ln 1{,}0585 = 5{,}685\ \%$ continuo. (c) Continuo:
${2{.}750{.}000} \times e^{0{,}057 \times 2{,}5} = 3{.}171{.}171$. Efectivo:
${2{.}750{.}000} \times 1{,}0585^{2{,}5} = 3{.}170{.}004$. Diferencia: $1.167 a favor del continuo. Es poco, pero confirma que el número publicado
solo se compara una vez convertido.

**2.8.** (a) Nominal: 2,2 % en el semestre, recibes $8.176.000. Efectivo: $1{,}044^{1/2} - 1 = 2{,}1763\ \%$,
recibes $8.174.105. (b) $1.895 de diferencia en un semestre. (c) Con la lectura nominal, dos semestres al
2,2 % dan una TEA de $1{,}022^2 - 1 = 4{,}4484\ \%$. Lectura: el enunciado ambiguo cuesta plata real. En
un certamen se escribe el supuesto; en un contrato se pregunta.

**2.9. Incierto (depende de la inflación).** La comparación es inválida: 3,9 % es una tasa **real** (por
sobre la UF) y 7,3 % es **nominal** (en pesos). Para compararlas hay que pasar por Fisher. El punto de
empate es la inflación que las iguala: $1{,}073/1{,}039 - 1 = 3{,}272\ \%$ anual. Si la inflación promedio
del crédito queda bajo 3,272 %, el de UF es más barato (con 3 %, el de UF cuesta 7,017 % en pesos, y el
de pesos cuesta 4,175 % real); si queda sobre, el de pesos es más barato (con 5 %, el de UF cuesta
9,095 % en pesos, y el de pesos solo 2,190 % real). Además cambia **quién carga el riesgo**: en UF lo
carga el deudor, cuya deuda en pesos sube con la inflación; en pesos fijo lo carga el banco. Un
deudor cuyo sueldo se reajusta con la inflación está más cubierto en UF. La afirmación es falsa como
razonamiento y la respuesta correcta depende de la inflación esperada y del riesgo que el deudor
quiera asumir.

**2.10.** (a) Tramo 1: factor $1{,}005^8 = 1{,}04071$, saldo $4.266.899. Tramo 2: la TEA de 6,9 % equivale
a $1{,}069^{1/12} - 1 = 0{,}5576\ \%$ mensual; factor de 10 meses 1,05718, saldo $4.510.871. Tramo 3: la
nominal se divide, $6{,}3/12 = 0{,}525\ \%$ mensual; factor de 6 meses 1,03192, saldo final **$4.654.842**.
La tasa mensual equivalente es la que da el mismo factor total en 24 meses:
$(4{.}654{.}842/4{.}100{.}000)^{1/24} - 1 = 0{,}5302\ \%$ mensual, que equivale a una TEA de 6,552 %. Real:
$1{,}06552/1{,}035 - 1 = 2{,}949\ \%$ anual. En pesos de hoy, el saldo vale
${4{.}654{.}842}/1{,}035^2 = 4{.}345{.}345$. (b) $(1{,}06)^2/1{,}056 - 1 = 6{,}402\ \%$. El banco está pagando por el
segundo año más que el 6,0 % que publica: el 6,0 % es un promedio de dos años, y el primero paga solo
5,6 %. Es una tasa forward, la puerta de entrada a la unidad 6.

---

## 12. Caso integrador · Valentina, ¿qué banco?

> Este caso sigue a Valentina, dueña de Estampa Sur, por todo el ramo. Todo es ficticio, incluidas
> las tasas. La fuente de las cifras es `verificacion/caso_valentina.py`.

En la unidad 1, Valentina dejó sus $3.460.000 al 0,55 % mensual por 36 meses. Ese 0,55 % salió de
elegir entre dos bancos:

- **Banco A:** 6,6 % anual nominal, capitalizable mensualmente.
- **Banco B:** 6,75 % efectivo anual.

La inflación esperada es 3,4 % anual.

**Pregunta.** ¿Qué banco paga más? ¿Cuánto gana Valentina en términos reales?

**Desarrollo.**

| | Banco A | Banco B |
|---|---|---|
| Tasa publicada | 6,6 % nominal | 6,75 % efectiva |
| Mensual | $6{,}6/12 = 0{,}55\ \%$ | $1{,}0675^{1/12} - 1 = 0{,}5458\ \%$ |
| TEA | $1{,}0055^{12} - 1 = 6{,}8034\ \%$ | 6,75 % |
| Real exacta (Fisher) | 3,29 % | 3,24 % |
| Real aproximada ($TEA - \pi$) | 3,40 % | 3,35 % |
| Saldo a los 36 meses | $4.215.322 | $4.209.008 |

**Lectura.**

- **Paga más el banco A**, aunque publique el número más bajo: el 6,6 % es nominal y, capitalizado
  cada mes, rinde 6,80 % al año. Por eso la unidad 1 usó 0,55 % mensual.
- La diferencia en tres años es de $6.314. Chica, pero la decisión correcta no depende del tamaño.
- En términos reales Valentina gana 3,29 % al año. Sus $4.215.322 del mes 36 valen $3.813.021 en
  pesos de hoy: su poder de compra creció $353.021, no los $755.322 que muestra el saldo. El resto
  solo compensa la inflación.
- Restar la inflación (3,40 %) exagera la ganancia real en una décima.

**Lo que pasa a la unidad siguiente.** La unidad 3 sigue con el banco A y su tasa mensual de **0,55 %**,
y calcula cuánto tiene que depositar Valentina cada mes, además de estos $3.460.000, para juntar el pie
de su departamento.

---

## 13. Para seguir

**En los libros del ramo.**

- Ross, Westerfield y Jaffe, *Finanzas corporativas* (9.ª ed., 2012), capítulo 4 (lo fija el
  programa): la parte de períodos de capitalización, tasa efectiva anual y capitalización continua.
  La tasa real y la inflación aparecen en el capítulo de tasas de interés y bonos del mismo libro.
- Brealey, Myers y Allen, *Principios de finanzas corporativas* (9.ª ed., 2010), capítulos 2 y 3 de la
  lectura que fija el programa: capitalización a distintas frecuencias, tasas nominales y reales.

**Abierto y gratis.**

- Dahlquist y Knight, *Principles of Finance*, OpenStax (2022), en inglés, sección 8.4 «Stated versus
  Effective Rates» (tasa publicada contra tasa efectiva). Licencia CC BY-NC-SA:
  https://openstax.org/books/principles-finance/pages/8-why-it-matters

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame tres créditos con tasas escritas de formas
distintas y corrígeme cuál es el más barato».
