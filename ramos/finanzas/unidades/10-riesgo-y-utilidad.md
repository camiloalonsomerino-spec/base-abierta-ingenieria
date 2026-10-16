---
ramo: Finanzas
unidad: 10
titulo: Riesgo, utilidad y aversión al riesgo
version: 0.1 (15-10-2026)
requiere: [01-valor-del-dinero, 09-acciones]
alimenta: [11-portafolios]
verificacion: verificacion/u10_utilidad.py
---

# Unidad 10 · Riesgo, utilidad y aversión al riesgo

**Qué vas a poder hacer.** Calcular el valor esperado y la varianza de una inversión con escenarios;
explicar por qué el valor esperado no basta para decidir; describir una persona con una función de
utilidad y leer en su forma si es aversa, neutral o amante del riesgo; calcular el equivalente cierto
y el premio por riesgo de una apuesta y usarlos para decidir entre algo riesgoso y algo seguro; medir
cuánta aversión tiene una función, y reconocer en qué se aparta la gente real de este modelo.

**Lo que necesitas antes.** Probabilidad básica (valor esperado y varianza de una variable discreta),
logaritmo natural y su inversa, y derivadas de primer y segundo orden.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. Valor esperado y varianza de una inversión

Una inversión riesgosa se describe con sus **escenarios**: qué puede pasar, con qué probabilidad y
cuánto rinde en cada caso. Con probabilidades $p_s$ y retornos $r_s$:

$$E[r] = \sum_s p_s\, r_s \qquad \sigma^2 = \sum_s p_s\,(r_s - E[r])^2 \qquad \sigma = \sqrt{\sigma^2}$$

El valor esperado es el promedio que se obtendría repitiendo la apuesta muchas veces. La desviación
estándar $\sigma$ mide cuánto se aleja, típicamente, el resultado de ese promedio: es la medida de
riesgo de esta unidad. Lo mismo vale para la riqueza final $W$ en vez del retorno: si la riqueza
inicial es $W_0$, $E[W] = W_0(1 + E[r])$ y $\sigma_W = W_0\,\sigma$.

---

## 2. Por qué el valor esperado no basta

Dos alternativas para $1.000.000 durante un año:

| | Resultado | Valor esperado | Desviación |
|---|---|---|---|
| A · depósito | $1.100.000 seguro | $1.100.000 | 0 |
| B · negocio | $1.500.000 o $700.000, al 50 % | $1.100.000 | $400.000 |

Tienen el mismo valor esperado, pero casi nadie queda indiferente: la mayoría elige A. Y la vida
real está llena de decisiones que el valor esperado no explica:

- **Los seguros.** La prima de un seguro siempre es mayor que la pérdida esperada (de esa diferencia
  vive la aseguradora). Si la gente decidiera por valor esperado, nadie se aseguraría.
- **La paradoja de San Petersburgo.** Una moneda se lanza hasta que sale cara; si sale en el
  lanzamiento $n$, se cobran $2^n$ pesos. El valor esperado es infinito
  ($\tfrac12 \cdot 2 + \tfrac14 \cdot 4 + \dots = 1 + 1 + \dots$), pero nadie pagaría más que unos pocos
  pesos por jugar.

La salida, propuesta por Daniel Bernoulli en el siglo XVIII, es que la gente no maximiza la plata
esperada, sino la **satisfacción** esperada que esa plata le da. Y un peso extra satisface menos al
que ya tiene mucho.

---

## 3. La función de utilidad

Una **función de utilidad** $u(W)$ asigna a cada nivel de riqueza un número que ordena las
preferencias de una persona. Más riqueza es siempre mejor: $u'(W) > 0$. Lo que distingue a una
persona de otra es la **curvatura**:

| Forma | $u''(W)$ | Utilidad marginal | Actitud | Compara |
|---|---|---|---|---|
| Cóncava | negativa | decreciente | **aversa** al riesgo | $u(E[W]) > E[u(W)]$ |
| Lineal | cero | constante | **neutral** al riesgo | $u(E[W]) = E[u(W)]$ |
| Convexa | positiva | creciente | **amante** del riesgo | $u(E[W]) < E[u(W)]$ |

La persona elige la alternativa con mayor **utilidad esperada**:

$$E[u(W)] = \sum_s p_s\, u(W_s)$$

**Por qué la concavidad es aversión.** En una función cóncava, perder $400.000 baja la utilidad más
de lo que la sube ganar $400.000. Por eso la apuesta B, con el mismo valor esperado que A, da menos
utilidad esperada: la cuerda entre los dos resultados queda bajo la curva. Aversión al riesgo **no**
es rechazar todo riesgo: es exigir una compensación por tomarlo.

Los números de utilidad no tienen unidad ni significado propio («15,6 útiles» no dice nada). Sirven
solo para comparar. Por eso, antes de concluir, se vuelve a pesos con el equivalente cierto.

---

## 4. Equivalente cierto y premio por riesgo

El **equivalente cierto** ($EC$) de una apuesta es el monto **seguro** que le da a la persona la misma
utilidad que la apuesta:

$$u(EC) = E[u(W)] \qquad\Longrightarrow\qquad EC = u^{-1}\big(E[u(W)]\big)$$

El **premio por riesgo** es lo que la persona está dispuesta a sacrificar, en valor esperado, para no
cargar con el riesgo:

$$\pi = E[W] - EC$$

Para un averso, $EC < E[W]$ y $\pi > 0$; para un neutral, $\pi = 0$; para un amante, $\pi < 0$.

**La regla de decisión.** Entre una apuesta y una alternativa segura $W_{\text{seguro}}$, se elige la
apuesta si $EC > W_{\text{seguro}}$. Es lo mismo que comparar utilidades esperadas, pero se lee en
pesos.

---

## 5. Dos funciones de ejemplo

| | $u(W) = \ln W$ | $u(W) = \sqrt{W}$ |
|---|---|---|
| Inversa | $W = e^{u}$ | $W = u^2$ |
| Equivalente cierto | $EC = e^{E[\ln W]}$ (la media geométrica) | $EC = \big(E[\sqrt{W}]\big)^2$ |
| En la apuesta B | $\sqrt{1{.}500{.}000 \times 700{.}000}$ = $1.024.695 | $\big(\tfrac12\sqrt{1{.}500{.}000} + \tfrac12\sqrt{700{.}000}\big)^2$ = $1.062.348 |
| Premio por riesgo en B | $75.305 | $37.652 |

Las dos personas prefieren el depósito A ($1.100.000 seguro supera ambos equivalentes ciertos). La del
logaritmo exige el doble de premio: su función se curva más. Con utilidad logarítmica, un **50 % de
pérdida** se compensa recién con un **100 % de ganancia**: $\tfrac12 \ln 0{,}5 + \tfrac12 \ln 2 = 0$.

---

## 6. Cuánta aversión

La curvatura se mide con dos coeficientes (de Arrow y Pratt):

$$A(W) = -\frac{u''(W)}{u'(W)} \quad\text{(absoluto)} \qquad R(W) = W \cdot A(W) \quad\text{(relativo)}$$

$A$ dice cuánto le molesta a la persona un riesgo de un monto fijo en pesos; $R$, un riesgo que es un
porcentaje fijo de su riqueza. Una familia muy usada tiene $R$ constante e igual a $\gamma$:

$$u(W) = \frac{W^{1-\gamma}}{1-\gamma} \qquad (\gamma = 1:\ u = \ln W)$$

| Función | $\gamma = R$ | $A(W)$ |
|---|---|---|
| $W$ (lineal) | 0 | 0 |
| $\sqrt{W}$ | 1/2 | $1/(2W)$ |
| $\ln W$ | 1 | $1/W$ |
| $-1/W$ | 2 | $2/W$ |

Mayor $\gamma$, más aversión: menor equivalente cierto para la misma apuesta. En todas estas
funciones $A$ **baja** cuando la riqueza sube: la misma apuesta de $1.000.000 asusta mucho al que
tiene $2.000.000 y poco al que tiene $20.000.000 (ejercicio 10.8).

**Una aproximación útil.** Para riesgos chicos respecto de la riqueza,

$$\pi \approx \tfrac12\, A(W)\,\sigma_W^2$$

El premio crece con la **varianza** y con la aversión. De aquí sale el puente a la unidad 11: un
inversionista que se mueve con media y varianza resume su aversión en un solo número y castiga la
varianza en vez de calcular utilidades escenario por escenario.

---

## 7. Lo que se observa: no somos Spock

El programa del ramo incluye la lectura *We are not Spock* (Satya Gabriel, Mount Holyoke College, 2015). El título apunta a Spock, el
personaje de *Star Trek* que decide con lógica pura. La teoría de la utilidad esperada describe a un
decisor así: estable, que calcula probabilidades sin error y que solo mira su riqueza final. La
economía conductual muestra que las personas reales se apartan de ese modelo de formas sistemáticas,
no al azar:

| Lo que se observa | En qué se aparta del modelo |
|---|---|
| **Aversión a las pérdidas** | Perder duele más de lo que alegra ganar lo mismo. Mucha gente rechaza una moneda al aire que paga 150 si sale cara y quita 100 si sale sello, aunque con apuestas tan chicas cualquier utilidad cóncava razonable la aceptaría |
| **Punto de referencia** | Se evalúan ganancias y pérdidas respecto de algo (lo que se pagó, lo del vecino), no la riqueza total |
| **Probabilidades chicas sobrevaloradas** | Se paga de más por loterías y por seguros contra eventos rarísimos |
| **Encuadre** | La misma decisión, contada como ganancia o como pérdida, recibe respuestas distintas |
| **Contabilidad mental** | La plata se separa en «cuentas» (el aguinaldo, el ahorro), aunque un peso es un peso |
| **Exceso de confianza** | Se sobreestima la propia capacidad de elegir acciones o de predecir |

La teoría prospectiva de Kahneman y Tversky (1979) ordena varias de estas observaciones. Para este
ramo, la lectura práctica es doble. La utilidad esperada sigue siendo la **vara** para decidir bien,
sobre todo en decisiones grandes y pensadas. Y conocer los sesgos sirve para no caer en ellos: vender
una acción solo porque «ya bajó» o aferrarse a ella para no «realizar la pérdida» es punto de
referencia, no finanzas.

---

## 8. Ejemplo resuelto · el seguro del auto de Martina

Martina tiene una riqueza total de **$12.000.000**, de la que **$8.000.000** es su auto. La
probabilidad de que se lo roben este año (sin recuperarlo) es **4 %**. Un seguro contra robo cuesta
**$420.000** al año. ¿Le conviene contratarlo?

**Paso 1 · Valor esperado y riesgo sin seguro.** Con 96 % termina el año con $12.000.000 y con 4 %
con $4.000.000.

$$E[W] = 0{,}96 \times 12{.}000{.}000 + 0{,}04 \times 4{.}000{.}000 = 11{.}680{.}000$$

La pérdida esperada es $0{,}04 \times 8{.}000{.}000$ = $320.000, y la desviación de su riqueza,
$1.567.673. La prima cobra un recargo de 31,25 % sobre la pérdida esperada. Por valor esperado, el
seguro no conviene: con él termina con $11.580.000 seguros, menos que $11.680.000 esperados.

**Paso 2 · Con utilidad logarítmica.** $\ln 12{.}000{.}000 = 16{,}30042$ y $\ln 4{.}000{.}000 = 15{,}20180$.

$$E[\ln W] = 0{,}96 \times 16{,}30042 + 0{,}04 \times 15{,}20180 = 16{,}25647$$

Con seguro: $\ln 11{.}580{.}000 = 16{,}26479$, **mayor** que 16,25647. Le conviene el seguro.

**Paso 3 · En pesos.** $EC = e^{16{,}25647}$ = $11.484.085. Quedarse sin seguro le vale lo mismo que
tener $11.484.085 seguros, menos que los $11.580.000 que le deja el seguro. Su premio por riesgo es
$11.680.000 − $11.484.085 = **$195.915**, y lo máximo que pagaría por el seguro es
$12.000.000 − $11.484.085 = **$515.915**. La aseguradora cobra $420.000: hay espacio para los dos.

**Paso 4 · Y si fuera menos aversa.** Con $u = \sqrt{W}$: $\sqrt{12{.}000{.}000} = 3.464{,}10$ y
$\sqrt{4{.}000{.}000} = 2.000{,}00$.

$$EC = \big(0{,}96 \times 3.464{,}10 + 0{,}04 \times 2.000{,}00\big)^2$$

El resultado es $11.597.686: su premio por riesgo baja a $82.314 y lo máximo que pagaría, a
$402.314. Con esta función **no** contrata el seguro a $420.000.

**Lectura.** El mismo seguro conviene o no según cuánto le moleste el riesgo a la persona. Por eso
existen los seguros: la aseguradora reparte el riesgo entre miles de autos y casi no le pesa, mientras
que para Martina perder dos tercios de su riqueza es grave. Fíjate también que el riesgo pesa porque el
auto es una parte grande de lo que tiene: con una riqueza diez veces mayor, el premio por riesgo
caería mucho (sección 6).

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Decidir comparando utilidades esperadas con montos en pesos | Compara utilidad con utilidad, o vuelve a pesos con el equivalente cierto |
| Aplicar la utilidad al retorno o a la ganancia en vez de a la riqueza final | $u$ se evalúa en lo que la persona tiene al final: riqueza inicial más resultado |
| Calcular $u(E[W])$ en vez de $E[u(W)]$ | Primero la utilidad de cada escenario, después el promedio |
| Creer que un averso nunca toma riesgos | Los toma si el premio lo compensa: compara $EC$ con lo seguro |
| Confundir el premio por riesgo con la pérdida esperada | $\pi = E[W] - EC$, no $W_0 - E[W]$ |
| Leer «utilidad 16,26» como un resultado | La utilidad solo ordena; la respuesta se da en pesos |
| Olvidar que la aversión depende de la riqueza | Con $\ln W$ o $\sqrt{W}$, la misma apuesta pesa menos al que tiene más |

---

## 10. Práctica

Diez ejercicios: 10.1 a 10.4 básicos, 10.5 a 10.8 intermedios, 10.9 y 10.10 de desafío. Dos son
comentes (10.4 y 10.10): se responden Verdadero, Falso o Incierto con un argumento. Las pautas están en
la sección 11. Salvo que se diga otra cosa, la utilidad se aplica a la riqueza final y no hay
descuento en el tiempo.

**10.1 · La cabaña en Pucón (básico).** Ignacio puede arrendar su cabaña por día durante el verano.
El ingreso neto de la temporada depende del clima: $1.200.000 con 25 % (verano lluvioso), $2.600.000
con 50 % (normal) y $3.500.000 con 25 % (muy bueno). Una agencia le ofrece arrendársela toda la
temporada por $2.300.000 fijos. (a) Calcula el valor esperado, la desviación estándar y el coeficiente
de variación del arriendo por día. (b) ¿Cuánto más rinde en valor esperado? (c) Si evalúa solo el
ingreso de la temporada, ¿qué elige con $u = \sqrt{W}$ y con $u = \ln W$?

**10.2 · Leer una función (básico).** Con $W$ en millones de pesos, clasifica cada función como
aversa, neutral o amante del riesgo, y calcula el coeficiente absoluto en $W = 4$: (a) $u = 5W + 200$;
(b) $u = W^{0{,}4}$; (c) $u = W^2$; (d) $u = 1 - e^{-0{,}5W}$. Ordénalas de más a menos aversa en ese
punto. ¿Cuál tiene aversión relativa constante y cuál la tiene absoluta constante?

**10.3 · La caja del concurso (básico).** En un programa de televisión, Benjamín tiene una caja cerrada
con $810.000 o $1.690.000, con igual probabilidad. Su utilidad es $u = \sqrt{W}$ sobre lo que gane.
(a) ¿Cuál es el valor esperado de la caja? (b) ¿Por cuánto la vendería, como mínimo? (c) ¿Cuál es su
premio por riesgo? (d) El animador le ofrece $1.230.000 por la caja: ¿acepta? (e) ¿Y si su utilidad
fuera $\ln W$?

**10.4 · Comente (básico).** «Una persona aversa al riesgo nunca debería invertir en algo riesgoso si
tiene a mano un depósito sin riesgo.»

**10.5 · Sueldo fijo u honorarios (intermedio).** Una diseñadora puede firmar un contrato con sueldo
fijo de $1.150.000 al mes o trabajar a honorarios: un mes bueno (60 %) gana $1.600.000 y un mes malo
(40 %) gana $Y$. Su utilidad del ingreso mensual es $u = \sqrt{W}$. (a) ¿Qué $Y$ la deja indiferente?
(b) ¿Qué $Y$ dejaría indiferente a una persona neutral al riesgo? Explica la diferencia. (c) Si el mes
malo paga $700.000, ¿con qué probabilidad de mes bueno queda indiferente?

**10.6 · Tres inversionistas, una inversión (intermedio).** Tres personas tienen $3.000.000 cada una.
Pueden ponerlos en un depósito al 6 % o en una inversión que sube 40 % o baja 20 %, con igual
probabilidad. Sus utilidades son $\sqrt{W}$, $\ln W$ y $-1/W$. (a) Calcula el retorno esperado y la
riqueza esperada de la inversión. (b) Calcula el equivalente cierto y el premio por riesgo de cada
una. (c) ¿Quién invierte? (d) ¿Con qué aversión relativa $\gamma$ queda alguien indiferente?

**10.7 · El seguro de la casa (intermedio).** Una familia tiene una riqueza de $42.000.000, de la que
$31.000.000 es su casa. En un año, la casa se quema entera con 2 % de probabilidad y tiene un daño
parcial de $4.600.000 con 6 %. Su utilidad es $\ln W$. Puede elegir: (A) sin seguro; (B) seguro
completo por $1.150.000; (C) seguro con deducible de $2.500.000 (la familia paga los primeros
$2.500.000 de cada siniestro) por $830.000. (a) Calcula la pérdida esperada y el recargo de cada
seguro. (b) Calcula el equivalente cierto de cada opción y elige. (c) ¿Cuánto pagaría como máximo por
el seguro completo?

**10.8 · La riqueza importa (intermedio).** Una apuesta gana o pierde $1.000.000 con igual
probabilidad. Dos personas con $u = \ln W$ la evalúan: una tiene $2.000.000 y otra $20.000.000. (a)
Calcula el equivalente cierto y el premio por riesgo de cada una, y el premio como porcentaje de su
riqueza. (b) Compara con la aproximación $\pi \approx \tfrac12 A(W)\sigma^2$. (c) Si la apuesta pierde
$1.000.000, ¿cuánto tendría que ganar para que la primera persona quede indiferente entre apostar y no
apostar?

**10.9 · Cuánto poner en lo riesgoso (desafío).** Tomás tiene $10.000.000 y utilidad $\ln W$. Puede
dividirlos entre un depósito al 5 % y un fondo que en un año sube 30 % o baja 18 %, con igual
probabilidad. Llama $\alpha$ a la fracción que pone en el fondo. (a) Escribe su utilidad esperada en
función de $\alpha$ y encuentra el $\alpha$ óptimo. (b) Compara el equivalente cierto con el óptimo,
con todo en el depósito, con todo en el fondo, con la mitad del óptimo y con el doble. (c) ¿Cómo cambia
el óptimo con $u = \sqrt{W}$? (d) ¿Cambia el óptimo si Tomás tuviera el doble de plata?

**10.10 · Comente (desafío).** «Mucha gente compra un seguro para su auto y, la misma semana, boletos de
lotería. Como eso no se puede explicar con una función de utilidad cóncava, la teoría de la utilidad
esperada no sirve para tomar decisiones financieras.»

---

## 11. Pautas

**10.1.** (a) $E = 0{,}25 \times 1{.}200{.}000 + 0{,}50 \times 2{.}600{.}000 + 0{,}25 \times 3{.}500{.}000$
= **$2.475.000**; la desviación es **$822.724** y el coeficiente de variación, 33,2 %. (b) Rinde
$175.000 más en valor esperado. (c) Equivalente cierto con raíz: $2.395.667; con logaritmo:
$2.308.336. Los dos superan los $2.300.000 fijos, así que arrienda por día, aunque con logaritmo por
muy poco. Lectura: el supuesto de que el ingreso de la temporada es toda su riqueza exagera la
aversión; si Ignacio tiene otros ingresos, el riesgo de la cabaña le pesa todavía menos.

**10.2.** Con $u' > 0$ en todas, manda el signo de $u''$.

| Función | $u''$ | Actitud | $A(W)$ | En $W = 4$ |
|---|---|---|---|---|
| (a) $5W + 200$ | 0 | neutral | 0 | 0 |
| (b) $W^{0{,}4}$ | negativa | aversa | $0{,}6/W$ | 0,15 |
| (c) $W^2$ | positiva | amante | $-1/W$ | $-0{,}25$ |
| (d) $1 - e^{-0{,}5W}$ | negativa | aversa | $0{,}5$ | 0,5 |

De más a menos aversa en $W = 4$: (d), (b), (a), (c). La (b) tiene aversión relativa constante
($R = 0{,}6$); la (d), absoluta constante ($A = 0{,}5$), así que su aversión relativa crece con la
riqueza: en $W = 4$ vale $R = 0{,}5 \times 4 = 2$. Lectura: sumar una constante o multiplicar por un
número positivo, como en (a), no cambia las decisiones: la utilidad solo ordena.

**10.3.** (a) **$1.250.000**. (b) $E[\sqrt{W}] = \tfrac12 \times 900 + \tfrac12 \times 1.300 = 1.100$,
así que $EC = 1.100^2$ = **$1.210.000**: es lo mínimo por lo que la vende. (c) Premio por riesgo:
**$40.000**. (d) Acepta: $1.230.000 seguros le dan más que la caja. (e) Con logaritmo,
$EC = \sqrt{810{.}000 \times 1{.}690{.}000}$ = $1.170.000: aceptaría hasta $1.170.000. Lectura: un
neutral pediría $1.250.000; cuanto más aversa la persona, más barato vende la incertidumbre.

**10.4. Falso.** Aversión al riesgo no es rechazar el riesgo: es exigir una compensación por tomarlo.
Una persona aversa compara el equivalente cierto de la inversión riesgosa con lo que le deja el
depósito. Si el retorno esperado extra es lo bastante alto para su nivel de aversión, el equivalente
cierto supera al depósito y le conviene invertir. Valentina, con utilidad logarítmica, es aversa y aun
así prefiere la inversión riesgosa a un depósito al 5,3 % (sección 12). El ejercicio 10.6 muestra que
la respuesta depende de **cuánta** aversión tiene cada uno: con la misma inversión, una persona
invierte y otra no. **Lo que anula la respuesta:** decir «depende de la persona» sin el mecanismo (el
premio por riesgo frente al retorno extra).

**10.5.** $\sqrt{1{.}150{.}000} = 1.072{,}38$, $\sqrt{1{.}600{.}000} = 1.264{,}91$. (a) Indiferencia:
$0{,}6 \times 1.264{,}91 + 0{,}4\sqrt{Y} = 1.072{,}38$, de donde $\sqrt{Y} = 783{,}58$ e
**$Y$ = $614.005**. (b) Neutral: $0{,}6 \times 1{.}600{.}000 + 0{,}4\,Y = 1{.}150{.}000$, **$Y$ =
$475.000**. La diseñadora aversa exige un mes malo $139.005 mejor: con $Y$ = $614.005, los honorarios
le rinden en promedio $1.205.602, y los $55.602 sobre el sueldo fijo son su premio por riesgo. (c) Con
$\sqrt{700{.}000} = 836{,}66$: $p = (1.072{,}38 - 836{,}66)/(1.264{,}91 - 836{,}66) =$ **0,550**. Si
la probabilidad de mes bueno supera 55 %, conviene trabajar a honorarios.

**10.6.** (a) $E[r] = 0{,}5 \times 40\ \% - 0{,}5 \times 20\ \%$, es decir 10 %; la riqueza termina en
$4.200.000 o $2.400.000, con valor esperado **$3.300.000**. El depósito deja $3.180.000. (b)

| Utilidad | $\gamma$ | Equivalente cierto | Premio por riesgo | Elige |
|---|---|---|---|---|
| $\sqrt{W}$ | 1/2 | $3.237.451 | $62.549 | inversión |
| $\ln W$ | 1 | $3.174.902 | $125.098 | depósito, por poco |
| $-1/W$ | 2 | $3.054.545 | $245.455 | depósito |

(c) Solo invierte la de raíz. (d) Con $\gamma$ = 0,96 el equivalente cierto iguala al depósito: más
averso que eso, deposita. Lectura: el premio por riesgo casi se duplica cada vez que la aversión se
duplica, y una diferencia chica de carácter cambia la decisión.

**10.7.** (a) Pérdida esperada: $0{,}02 \times 31{.}000{.}000 + 0{,}06 \times 4{.}600{.}000$ =
**$896.000**; el seguro completo cobra un recargo de 28,3 %. Con deducible, la aseguradora paga en
promedio $0{,}02 \times 28{.}500{.}000 + 0{,}06 \times 2{.}100{.}000$ = $696.000 y cobra un recargo de
19,3 %. (b)

| Opción | Riqueza esperada | Equivalente cierto |
|---|---|---|
| A · sin seguro | $41.104.000 | $40.605.933 |
| B · seguro completo | $40.850.000 | $40.850.000 |
| C · con deducible | $40.970.000 | **$40.964.186** |

Elige **C**. (c) Lo máximo que pagaría por el seguro completo es $42.000.000 − $40.605.933 =
$1.394.067; le cobran menos, así que el seguro completo también le conviene más que no asegurarse.
Lectura: el deducible deja en la familia los daños chicos, que puede absorber, y asegura el desastre,
que no puede. El recargo se paga solo por la parte que de verdad necesita cubrir.

**10.8.** (a) Con $2.000.000: $EC = \sqrt{3{.}000{.}000 \times 1{.}000{.}000}$ = $1.732.051, premio
**$267.949** (13,40 % de su riqueza). Con $20.000.000: $EC$ = $19.974.984, premio **$25.016** (0,13 %).
(b) Con $A = 1/W$ y $\sigma^2 = 1{.}000{.}000^2$, la aproximación da $250.000 y $25.000. Es casi exacta
para el rico, para quien el riesgo es chico; para el que apuesta la mitad de lo que tiene, se queda
corta. (c) Indiferencia: $\tfrac12\ln(2{.}000{.}000 + X) + \tfrac12\ln 1{.}000{.}000 = \ln 2{.}000{.}000$,
de donde $2{.}000{.}000 + X = 4{.}000{.}000$: tendría que ganar **$2.000.000** para arriesgar
$1.000.000. Lectura: es el «50 % de pérdida se compensa con 100 % de ganancia» de la sección 5.

**10.9.** (a) Con $a = 0{,}30 - 0{,}05 = 0{,}25$ y $b = -0{,}18 - 0{,}05 = -0{,}23$ (los retornos del fondo
sobre el depósito):

$$E[u] = \tfrac12 \ln\big(W(1{,}05 + 0{,}25\,\alpha)\big) + \tfrac12 \ln\big(W(1{,}05 - 0{,}23\,\alpha)\big)$$

Derivando e igualando a cero, $\alpha^* = -\dfrac{1{,}05\,(\tfrac12 a + \tfrac12 b)}{a\,b}$, que da
**18,26 %**: $1.826.087 en el fondo. El fondo rinde en promedio 6,0 %, apenas un punto sobre el
depósito, y por eso la fracción es chica. Con $\alpha^*$ la riqueza termina en $10.956.522 o
$10.080.000. (b)

| Fracción en el fondo | Equivalente cierto |
|---|---|
| 0 (todo al depósito) | $10.500.000 |
| la mitad del óptimo | $10.506.846 |
| $\alpha^*$ | **$10.509.126** |
| el doble del óptimo | $10.500.000 |
| 100 % | $10.324.728 (con riqueza esperada de $10.600.000) |

Todo en el fondo tiene el mayor valor esperado y el peor equivalente cierto. Con el doble del óptimo
ya no gana nada frente al depósito. (c) Con raíz, $\alpha^*$ = 36,5 %: la mitad de aversión relativa,
aproximadamente el doble en lo riesgoso. (d) No cambia: con $\ln W$ la riqueza sale como factor común
($\ln W + \ln(\dots)$), así que la fracción óptima es la misma para cualquier $W$. Es la aversión
relativa constante. Lectura: la unidad 11 resuelve la misma pregunta con media y varianza, y con un
portafolio de varios activos.

**10.10. Incierto.** La primera parte es correcta: con una sola función cóncava, la persona compra
seguros (paga para sacarse riesgo) pero nunca una lotería, que tiene valor esperado negativo **y**
agrega riesgo. Que mucha gente haga las dos cosas muestra que las personas no son el decisor
perfectamente lógico del modelo: sobrevaloran las probabilidades muy chicas (el premio mayor), le
asignan a la lotería un valor de entretención y separan la plata en cuentas mentales (sección 7). Pero
la conclusión no se sigue. La utilidad esperada no pretende describir cada compra de $1.000; es la
**vara** para decisiones financieras con montos grandes, donde equivocarse cuesta, y explica bien por
qué existen los seguros, por qué se exige más retorno a lo más riesgoso y por qué conviene
diversificar. Que la gente se aparte del modelo es un argumento para conocer los sesgos, no para
tirar la herramienta. **Lo que anula la respuesta:** responder «Verdadero, la gente es irracional» o
«Falso, la teoría es correcta» sin separar la parte descriptiva de la normativa.

---

## 12. Caso integrador · Valentina, ¿invertir o depositar?

> Este caso sigue a Valentina, dueña de Estampa Sur, por todo el ramo. Todo es ficticio. La fuente de
> las cifras es `verificacion/caso_valentina.py`.

Valentina tiene **$5.000.000** para invertir un año. Puede dejarlos en un **depósito al 5,3 %** o
ponerlos en una inversión riesgosa con tres escenarios:

| Escenario | Probabilidad | Retorno | Riqueza final | $\ln W$ |
|---|---|---|---|---|
| Bueno | 45 % | +28 % | $6.400.000 | 15,67181 |
| Normal | 35 % | +6 % | $5.300.000 | 15,48322 |
| Malo | 20 % | −22 % | $3.900.000 | 15,17649 |

Su utilidad es logarítmica.

**Pregunta.** ¿Le conviene la inversión riesgosa o el depósito?

**Desarrollo.**

1. **Valor esperado y riesgo.** $E[r] = 0{,}45 \times 28\ \% + 0{,}35 \times 6\ \% - 0{,}20 \times 22\ \%$,
   o sea **10,3 %**, con una desviación de **18,87 %**. En pesos: riqueza esperada de $5.515.000 y
   desviación de $943.544. Con 20 % de probabilidad pierde $1.100.000.
2. **Utilidad esperada.** $E[\ln W] = 0{,}45 \times 15{,}67181 + 0{,}35 \times 15{,}48322 + 0{,}20 \times 15{,}17649 = 15{,}50674$.
3. **Equivalente cierto.** $EC = e^{15{,}50674}$ = **$5.426.133**. La inversión le vale lo mismo que
   tener esa cifra segura: un retorno seguro equivalente de 8,52 %.
4. **Premio por riesgo.** $5.515.000 − $5.426.133 = **$88.867**: lo que el riesgo le «cuesta» en su
   escala.
5. **Comparar con el depósito.** El depósito deja $5.000.000 × 1,053 = **$5.265.000**
   ($\ln$ = 15,47659, menor que 15,50674). El equivalente cierto de la inversión lo supera en $161.133.

**Decisión.** Valentina elige la **inversión riesgosa**. Es aversa al riesgo (paga $88.867 de premio),
pero el retorno extra (10,3 % contra 5,3 %) le compensa con creces.

**Qué tan firme es la decisión.** Con $u = \sqrt{W}$ (menos aversa) el equivalente cierto sube a
$5.471.617; con $-1/W$ (más aversa) baja a $5.329.573, que todavía supera al depósito. La decisión solo
se da vuelta con una aversión relativa sobre 2,64. Un 20 % de probabilidad de perder $1.100.000 es
real: si esa plata fuera la del pie del departamento (unidad 3), lo sensato sería mirar la decisión con
una aversión mayor.

**Lo que pasa a la unidad 11.** Ahí Valentina deja de elegir entre «todo o nada»: arma una cartera con
acciones de Textil Andes (unidad 9) y un fondo, decide qué fracción poner en lo riesgoso y resume su
aversión en un solo número que castiga la varianza (sección 6).

---

## 13. Para seguir

**En las lecturas del ramo.**

- Vial y Zurita, *Microeconomía intermedia* (Ediciones Universidad Católica, 2007), capítulo 7, el que
  fija el programa para valor esperado, función de utilidad y aversión al riesgo.
- Satya Gabriel, *We are not Spock* (Mount Holyoke College, 2015), la lectura del programa sobre el comportamiento observado de las
  personas frente al riesgo (sección 7).
- Ross, Westerfield y Jaffe, *Finanzas corporativas* (9.ª ed., 2012), capítulos 10 y 11, y Brealey,
  Myers y Allen, *Principios de finanzas corporativas* (9.ª ed., 2010), capítulos 8 y 9: los que el
  programa asigna a estas semanas. Tratan riesgo y retorno de los activos y llevan a la unidad 11.

**Abierto y gratis.**

- Dahlquist y Knight, *Principles of Finance*, OpenStax (2022), en inglés, capítulo 15, sección 15.2
  (riesgo y retorno de un activo: retorno esperado, varianza y desviación estándar). Licencia CC
  BY-NC-SA: https://openstax.org/books/principles-finance/pages/15-why-it-matters

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un seguro con deducible y una función de
utilidad, déjame calcular los equivalentes ciertos y corrígeme».
