---
ramo: Finanzas
unidad: 9
titulo: Acciones
version: 0.1 (15-10-2026)
requiere: [03-anualidades, 05-van-y-tir]
alimenta: [11-portafolios, 12-capm-y-costo-de-capital]
verificacion: verificacion/u09_acciones.py
---

# Unidad 9 · Acciones

**Qué vas a poder hacer.** Explicar por qué el precio de una acción es el valor presente de los
dividendos que se esperan; valorar una acción sin crecimiento, con crecimiento constante (modelo de
Gordon) y con dos etapas de crecimiento; estimar la tasa de crecimiento desde la retención de
utilidades y el ROE; separar el precio en lo que valen los activos de hoy y lo que valen las
oportunidades de crecimiento (VPOC); leer la razón precio/utilidad, y sacar del precio de mercado la
rentabilidad que exigen los accionistas.

**Lo que necesitas antes.** Valor presente de un monto, de una perpetuidad y de una perpetuidad con
crecimiento (unidad 3), y la idea de VAN (unidad 5): comprar una acción es un proyecto en el que
pagas hoy y recibes flujos después.

**Tiempo.** Unas 4,5 horas: 2 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. Qué compras cuando compras una acción

Una acción es una parte de la propiedad de una empresa. El accionista no tiene un contrato que le
prometa pagos fijos, como el dueño de un bono: tiene derecho a lo que quede después de pagar a todos
los demás. Ese derecho le llega por dos vías:

- **Dividendos**, que la empresa reparte de sus utilidades. Los propone el directorio y los aprueba la
  junta de accionistas. En Chile, una sociedad anónima abierta reparte por ley al menos el 30 % de la
  utilidad del ejercicio, salvo acuerdo unánime en contrario.
- **El precio de venta**, cuando el accionista decide salir.

| | Bono | Acción |
|---|---|---|
| Flujo periódico | cupón fijo por contrato | dividendo, que se estima |
| Flujo final | valor nominal, en fecha conocida | precio de venta, lo fija el mercado |
| Vencimiento | sí | no tiene |
| Si la empresa quiebra | cobra antes | cobra lo que sobre, si sobra |

Hay acciones **ordinarias** (dividendo variable, derecho a voto) y **preferentes** (dividendo fijo y
prioridad para cobrarlo, casi siempre sin voto). El **valor bursátil** de la empresa es el número de
acciones por el precio de cada una.

---

## 2. Un período: rentabilidad y precio de hoy

Si compras hoy a $P_0$, cobras el dividendo $D_1$ al final del año y vendes a $P_1$, ganaste

$$r = \frac{D_1 + P_1 - P_0}{P_0} = \underbrace{\frac{D_1}{P_0}}_{\text{rendimiento por dividendo}} + \underbrace{\frac{P_1 - P_0}{P_0}}_{\text{ganancia de capital}}$$

La base es siempre $P_0$, lo que pusiste al inicio. Si el mercado exige una rentabilidad $k$ a las
acciones de ese riesgo, el precio que hoy deja esa rentabilidad exacta es

$$P_0 = \frac{D_1 + P_1}{1 + k}$$

Esa es la idea entera de la unidad: el precio es lo máximo que puedes pagar para ganar justo $k$. Si
pagas menos, ganas más que $k$ (el VAN de comprar es positivo); si pagas más, ganas menos.

> **Notación.** En esta unidad $k$ es la rentabilidad que exigen los accionistas (el apunte del ramo
> la llama $r$; es lo mismo). $D_0$ es el dividendo que la empresa **acaba de pagar** y $D_1$ el
> **próximo**. $UPA$ es la utilidad por acción (en inglés, EPS).

---

## 3. El precio es el valor presente de todos los dividendos

Pero $P_1$ es, a su vez, lo que pagará el próximo comprador: $P_1 = (D_2 + P_2)/(1 + k)$. Reemplazando
una y otra vez,

$$P_0 = \frac{D_1}{1+k} + \frac{D_2}{(1+k)^2} + \dots + \frac{D_T + P_T}{(1+k)^T} = \sum_{t=1}^{\infty} \frac{D_t}{(1+k)^t}$$

**El horizonte no cambia el precio.** El que piensa vender en dos años y el que piensa quedarse para
siempre pagan lo mismo, porque el precio de venta resume los dividendos que vienen después. Ejemplo
con $D_1 = 40$, crecimiento de 4 % al año y $k = 9\ \%$ (la fórmula de la sección 5 da 800):

| Horizonte | Cálculo | $P_0$ |
|---|---|---|
| Para siempre | $40 / (0{,}09 - 0{,}04)$ | 800 |
| Vender en 1 año ($P_1 = 832$) | $(40 + 832) / 1{,}09$ | 800 |
| Vender en 2 años ($D_2 = 41{,}6$, $P_2 = 865{,}28$) | $36{,}70 + 35{,}01 + 728{,}29$ | 800 |

El precio mira **hacia adelante**. Los dividendos pasados sirven solo como información para estimar
los que vienen: si una empresa con diez años de buenos dividendos anuncia que deja de pagarlos, su
precio cae hoy, aunque su historia sea la misma.

---

## 4. Crecimiento cero · la perpetuidad

Si el dividendo es siempre el mismo ($D_1 = D_2 = \dots = D$), el precio es una perpetuidad:

$$P_0 = \frac{D}{k}$$

Así se valoran las **acciones preferentes**, cuyo dividendo es fijo. Y así se valora una empresa que
reparte toda su utilidad y no crece: $P_0 = UPA/k$.

---

## 5. Crecimiento constante · el modelo de Gordon

Si el dividendo crece a una tasa $g$ para siempre ($D_2 = D_1(1+g)$, $D_3 = D_1(1+g)^2$, …), la suma
es una perpetuidad con crecimiento:

$$P_0 = \frac{D_1}{k - g} \qquad \text{solo si } k > g$$

Tres cosas que se preguntan:

1. **$D_1$, no $D_0$.** Si el enunciado dice «acaba de pagar», ese dividendo ya lo cobró el dueño
   anterior. Hay que hacerlo crecer: $D_1 = D_0(1+g)$. Las palabras de $D_0$: «acaba de pagar»,
   «pagó», «el último». Las de $D_1$: «pagará», «el próximo», «se espera».
2. **El precio crece a la tasa $g$.** $P_1 = D_2/(k-g) = P_0(1+g)$. En el ejemplo de la sección 3,
   de 800 a 832. Por eso la rentabilidad se parte en dividendo y ganancia de capital: $40/800 =$
   5,0 % de dividendo más 4,0 % de ganancia, que suman el 9 % exigido.
3. **Por qué $k > g$.** Si $g$ alcanza a $k$, el denominador se hace cero y el precio infinito.
   Ninguna empresa puede crecer para siempre más rápido que la economía; un crecimiento alto cabe
   solo como etapa (sección 6).

> **La sensibilidad de Gordon.** Con $D_1 = 40$ y $k = 9\ \%$: si $g$ es 4 %, el precio es 800; si es
> 5 %, 1.000; si es 6 %, 1.333. Cuando $g$ se acerca a $k$, un error chico en $g$ cambia todo. Usa
> Gordon con un $g$ de largo plazo prudente, del orden del crecimiento de la economía.

---

## 6. Dos etapas · crecimiento alto y después estable

Una empresa con una patente, una planta nueva o un mercado que recién se abre puede crecer rápido unos
años y después volver a un ritmo normal. Se valora en tres pasos:

1. Los dividendos de la etapa alta, uno por uno, y su valor presente.
2. El **valor terminal** en el último año de la etapa alta ($T$), con Gordon desde el primer dividendo
   de la etapa estable:

   $$P_T = \frac{D_{T+1}}{k - g_2} \qquad D_{T+1} = D_T (1 + g_2)$$

3. Traer $P_T$ a hoy dividiendo por $(1+k)^T$ y sumar.

$$P_0 = \sum_{t=1}^{T} \frac{D_t}{(1+k)^t} + \frac{P_T}{(1+k)^T}$$

**La trampa del valor terminal.** $P_T$ se calcula con $D_{T+1}$, pero queda parado en $T$: un
período antes del primer flujo que resume. Se descuenta $T$ veces, no $T+1$. Dibuja la línea de
tiempo y marca dónde cae.

Solo la etapa estable necesita $k > g_2$. La etapa alta puede tener $g_1$ mayor que $k$, porque dura
un número finito de años.

---

## 7. De dónde sale el crecimiento

Una empresa crece si reinvierte. Si retiene una fracción $b$ de sus utilidades (la **tasa de
retención**; $1 - b$ es la tasa de reparto) y lo retenido rinde el $ROE$ (utilidad sobre patrimonio
contable), las utilidades del año siguiente son las de este año más lo que rinde lo retenido:

$$UPA_{t+1} = UPA_t + b \cdot UPA_t \cdot ROE \quad\Longrightarrow\quad g = b \times ROE$$

Si la tasa de reparto se mantiene, el dividendo crece al mismo ritmo que la utilidad. Juntando con
Gordon:

$$P_0 = \frac{(1 - b)\, UPA_1}{k - b \cdot ROE}$$

Fíjate que retener tiene dos efectos opuestos: **baja el dividendo de hoy** (el numerador) y **sube el
crecimiento** (achica el denominador). Cuál gana depende de la sección siguiente.

---

## 8. El valor de las oportunidades de crecimiento (VPOC)

Una empresa que reparte toda su utilidad y no crece vale $UPA_1/k$: es lo que valen sus activos de
hoy. Todo lo que el precio tenga por encima es lo que el mercado paga por los proyectos que vendrán:

$$P_0 = \frac{UPA_1}{k} + VPOC$$

El **VPOC** (valor presente de las oportunidades de crecimiento; en inglés, PVGO; la ayudantía del
ramo lo llama VPNOC) es el VAN, por acción, de los proyectos que la empresa financia reteniendo
utilidades.

**Crecer no es lo mismo que crear valor.** El signo del VPOC lo decide una comparación simple:

| Si el ROE de lo reinvertido es… | El VPOC es… | Retener… |
|---|---|---|
| mayor que $k$ | positivo | sube el precio |
| igual a $k$ | cero | no cambia el precio, aunque la empresa crezca |
| menor que $k$ | negativo | baja el precio, aunque la empresa crezca |

La intuición: cada peso retenido es un peso que el accionista podría haber invertido él mismo al $k$.
Si la empresa lo pone a rendir menos que eso, el accionista pierde, por mucho que las utilidades
crezcan.

Cuando el VPOC viene de un proyecto puntual (una inversión en $t = 1$ que genera utilidades desde
$t = 2$), se calcula como cualquier VAN: la perpetuidad de las utilidades nuevas queda parada en
$t = 1$, junto a la inversión; se suman ahí y se descuentan **una** vez a hoy.

---

## 9. La razón precio/utilidad y la rentabilidad implícita

**Precio/utilidad (P/U).** Dividiendo la ecuación del VPOC por $UPA_1$:

$$\frac{P_0}{UPA_1} = \frac{1}{k} + \frac{VPOC}{UPA_1}$$

Una empresa que no crece se transa a $1/k$ veces su utilidad. Un P/U sobre $1/k$ dice que el mercado
espera oportunidades de crecimiento rentables. Pero un P/U alto **no** dice por sí solo que la acción
esté cara: puede reflejar un VPOC grande o un $k$ bajo (una empresa de poco riesgo). Para comparar
P/U de dos empresas, hay que mirar también su riesgo.

**Rentabilidad exigida implícita.** Despejando Gordon:

$$k = \frac{D_1}{P_0} + g$$

El mercado exige el rendimiento por dividendo más el crecimiento. Es la TIR de comprar la acción al
precio de hoy. Con dos etapas no hay despeje: se busca la tasa que iguala el VP de los dividendos con
el precio, por tanteo o con la función TIR de una planilla.

> **Ojo con la utilidad de qué año.** Si el enunciado da la utilidad **reportada** (la del año que
> terminó), el dividendo del próximo año sale de la utilidad del próximo año: $UPA_1 = UPA_0(1 + g)$.
> Escribe en una línea qué utilidad usas.

---

## 10. Ejemplo resuelto · las acciones de la abuela

La abuela tiene **2.500 acciones** de Lácteos del Ñuble S.A. (ficticia) y un corredor le ofrece
comprárselas a **\$905** cada una, el precio de hoy en bolsa. Ella pregunta si le conviene vender.

| Dato | Valor |
|---|---|
| Dividendo que la empresa acaba de pagar $D_0$ | \$52 |
| Crecimiento los próximos 3 años (planta nueva de quesos) | 8 % anual |
| Crecimiento desde el año 4, para siempre | 3 % anual |
| Rentabilidad que exige a una acción de este riesgo $k$ | 10 % |
| Utilidad por acción esperada para el próximo año $UPA_1$ | \$78 |

**Paso 1 · El primer dividendo.** «Acaba de pagar» es $D_0$. El que entra al precio es
$D_1 = 52 \times 1{,}08 = 56{,}16$.

**Paso 2 · Una referencia rápida.** Si la empresa creciera solo 3 % desde hoy, valdría
$52 \times 1{,}03 / (0{,}10 - 0{,}03) = 765{,}14$. Con tres años al 8 % tiene que valer más.

**Paso 3 · La etapa alta.**

| Año | Dividendo | Factor $1{,}10^t$ | VP |
|---|---|---|---|
| 1 | 56,16 | 1,1000 | 51,05 |
| 2 | 60,65 | 1,2100 | 50,13 |
| 3 | 65,51 | 1,3310 | 49,21 |
| Suma | | | 150,40 |

**Paso 4 · El valor terminal.** El primer dividendo de la etapa estable es
$D_4 = 65{,}51 \times 1{,}03 = 67{,}47$. El valor terminal queda parado en $t = 3$:

$$P_3 = \frac{67{,}47}{0{,}10 - 0{,}03} = 963{,}86 \qquad \frac{963{,}86}{1{,}10^3} = 724{,}16$$

**Paso 5 · El precio.** $P_0 = 150{,}40 + 724{,}16 = 874{,}56$. El valor terminal pesa el 82,8 % del
precio: casi todo el valor está en lo que pasa después del año 3, que es lo más incierto.

**Paso 6 · Comparar con la bolsa.** El mercado paga \$905, más que los \$874,56 que vale a un 10 %. Al
revés: quien compre hoy a \$905 con estas mismas expectativas gana una rentabilidad implícita de
**9,77 %** (la tasa que iguala el VP de los dividendos con 905, buscada por tanteo), menos que el 10 %
que exige la abuela.

**Paso 7 · El VPOC y el P/U.** Sin crecimiento, la acción valdría $78 / 0{,}10 = 780$. El VPOC es
$874{,}56 - 780 = 94{,}56$ por acción. El P/U es $874{,}56 / 78 = 11{,}21$, sobre el 10 de una empresa
que no crece; el del mercado es $905 / 78 = 11{,}60$. La empresa reparte el 72 % de su utilidad.

**La decisión.** Vendiendo recibe **$2.262.500**; las acciones le valen $2.186.394 a su tasa. Vender
le deja **$76.106** más. Le conviene vender, salvo que crea que el crecimiento alto va a durar más de
tres años, que es justo lo que el mercado parece estar creyendo. Si lo cree, la diferencia no es
plata gratis: es una apuesta sobre el futuro de la planta.

---

## 11. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Usar el dividendo que «acaba de pagar» como $D_1$ | $D_1 = D_0(1+g)$. El error es justo el factor $(1+g)$ |
| Descontar el valor terminal $T+1$ veces porque se calculó con $D_{T+1}$ | $P_T$ queda parado en $T$: se descuenta $T$ veces |
| Aplicar Gordon con $g \ge k$, o con el $g$ de la etapa alta | Gordon solo para la etapa estable y con $k > g$ |
| Creer que retener utilidades siempre sube el precio | Sube solo si el ROE de lo reinvertido supera $k$ |
| Sacar $D_1$ de la utilidad reportada sin hacerla crecer | $UPA_1 = UPA_0(1+g)$, y dilo en una línea |
| Leer un P/U alto como «cara» | Puede ser VPOC alto o $k$ bajo: compara contra $1/k$ |
| Dividir la rentabilidad de un período por $P_1$ | La base es lo que pagaste, $P_0$ |

---

## 12. Práctica

Diez ejercicios: 9.1 a 9.4 básicos, 9.5 a 9.8 intermedios, 9.9 y 9.10 de desafío. Dos son comentes
(9.4 y 9.8): se responden Verdadero, Falso o Incierto con un argumento. Las pautas están en la sección
13. Intenta cada uno antes de mirarla. Todas las empresas son ficticias.

**9.1 · «Acaba de pagar» (básico).** Pesquera Golfo de Arauco acaba de pagar un dividendo de \$38 por
acción. Se espera que crezca 2,5 % al año para siempre, y los accionistas exigen 9,5 %. (a) ¿Cuánto
vale la acción hoy? (b) ¿En cuánto te equivocas si usas \$38 como el próximo dividendo? (c) ¿Cuánto
debería valer en un año y en cinco años, si nada cambia? (d) ¿Qué parte de la rentabilidad es
dividendo?

**9.2 · Acción preferente (básico).** Embotelladora Sur tiene acciones preferentes que pagan un
dividendo fijo de $1.450 al año, para siempre. (a) Si a ese riesgo se le exige 8,2 %, ¿cuánto vale? (b)
En bolsa se transa a $16.900: ¿qué rentabilidad obtiene quien compra a ese precio? (c) Si la tasa
exigida sube a 9 %, ¿cuánto vale y cuánto cae?

**9.3 · Del ROE a la rentabilidad exigida (básico).** Molinos del Itata acaba de reportar utilidades
por $2.640 millones y tiene 400 millones de acciones, que se transan a \$78. Retiene el 35 % de sus
utilidades y su ROE es 13 %, que se espera se mantenga. (a) ¿En cuánto crecerán las utilidades el
próximo año, en millones y en porcentaje? (b) ¿Cuál será el dividendo por acción del próximo año? (c)
¿Qué rentabilidad exige el mercado? (d) ¿Cuánto da si sacas el dividendo de la utilidad reportada?

**9.4 · Comente (básico).** «Una empresa que no pagará dividendos durante los próximos cinco años no le
sirve a un inversionista que piensa vender la acción en tres: no va a cobrar nada mientras la tenga.»

**9.5 · Clínicas dentales en expansión (intermedio).** Sonrisa Sur abrirá clínicas en tres regiones.
Pagará un dividendo de \$120 el próximo año, que crecerá 14 % al año hasta el año 4; desde el año 5
crecerá 4 % para siempre. Se exige 12 %. (a) Calcula el precio. (b) ¿Qué parte del precio es el valor
terminal? (c) ¿Cuánto darías si descontaras el valor terminal un año de más? (d) ¿Cuánto valdría con
4 % desde el primer año?

**9.6 · Repartir o retener (intermedio).** Ferretería Austral espera una utilidad por acción de \$340
el próximo año y hoy reparte el 100 %. Sus accionistas exigen 11 %. La gerencia propone retener el
45 % para abrir sucursales. Calcula el precio, el VPOC y el P/U con la nueva política si el ROE de las
sucursales es (a) 15 %, (b) 8 %, (c) 11 %. ¿Qué le recomiendas al directorio?

**9.7 · Qué dice el P/U (intermedio).** Una sanitaria se transa a $1.250, con utilidad esperada de
\$96 por acción y una rentabilidad exigida de 8 %. Una tecnológica se transa a \$820, con utilidad
esperada de \$40 y rentabilidad exigida de 13 %. (a) Calcula el P/U de cada una. (b) Calcula el valor
sin crecimiento y el VPOC de cada una, y qué parte del precio es VPOC. (c) Un amigo dice que la
tecnológica es más cara porque su P/U es más alto. ¿Qué le respondes?

**9.8 · Comente (intermedio).** «Si el Banco Central sube su tasa, el precio de las acciones de una
empresa cuyas utilidades y dividendos esperados no cambian no tiene por qué moverse: el precio es el
VP de los dividendos, y los dividendos son los mismos.»

**9.9 · Camiones eléctricos (desafío).** Transportes Cordillera reparte toda su utilidad, que sin
proyectos nuevos será de \$95 por acción al año para siempre. Tiene 600 millones de acciones y sus
accionistas exigen 11 %. En $t = 1$ puede invertir $18.000 millones en camiones eléctricos que bajan
sus costos y suben la utilidad en $2.700 millones al año desde $t = 2$, para siempre. (a) Calcula el
precio sin el proyecto, el VPOC por acción y el precio con el proyecto. ¿Cuánto da el P/U? (b) Si el
proyecto tiene más riesgo que el negocio actual y se le exige 14 %, ¿cuánto vale? (c) ¿Hasta qué tasa
exigida conviene hacerlo?

**9.10 · La tasa que esconde un precio (desafío).** Energía Solar Atacama se transa a $3.200. Pagará
un dividendo de \$96 el próximo año, que crecerá 18 % al año hasta el año 5; después, 3,5 % para
siempre. (a) Calcula la rentabilidad que exige el mercado. (b) Compárala con lo que darían dos atajos
equivocados: Gordon con el crecimiento de largo plazo y Gordon con el de la etapa alta. (c) ¿Qué parte
del precio es el valor terminal y qué te dice eso del riesgo de esta acción?

---

## 13. Pautas

**9.1.** (a) $D_1 = 38 \times 1{,}025 = 38{,}95$; $P_0 = 38{,}95 / (0{,}095 - 0{,}025) =$ **556,43**.
(b) Con 38 como $D_1$ da 542,86: te equivocas en 13,57, justo el factor 1,025. (c) El precio crece
a la tasa $g$: $P_1 = 570{,}34$ y $P_5 = 556{,}43 \times 1{,}025^5 = 629{,}55$. (d)
$38{,}95/556{,}43 =$ 7,0 % de dividendo; los otros 2,5 puntos son ganancia de capital. Lectura: en
Gordon el precio sube al mismo ritmo que el dividendo, así que la ganancia de capital es $g$.

**9.2.** (a) $P_0 = 1.450 / 0{,}082 =$ **$17.683**. (b) ${1{.}450} / 16.900 =$ 8,58 %, más que el 8,2 %:
a ese precio la preferente está barata para quien exige 8,2 %. (c) ${1{.}450} / 0{,}09 =$ $16.111, una
caída de 8,9 %. Lectura: con el dividendo fijo, todo el movimiento del precio viene de la tasa, igual
que en un bono perpetuo.

**9.3.** (a) Las utilidades suben ${2{.}640} \times 0{,}35 \times 0{,}13 = 120{,}12$ millones, un
$g = 0{,}35 \times 0{,}13 =$ **4,55 %**. (b) $UPA_0 = 2.640/400 = 6{,}60$;
$UPA_1 = 6{,}60 \times 1{,}0455 = 6{,}9003$; se reparte el 65 %: $D_1 = 4{,}4852$. (c)
$k = 4{,}4852/78 + 0{,}0455$: 5,75 % de dividendo más 4,55 % de crecimiento, **10,30 %**. (d) Con la utilidad reportada,
$D = 4{,}29$ y $k =$ 10,05 %: un cuarto de punto menos. Lectura: las dos convenciones aparecen en el
ramo; la consistente es hacer crecer la utilidad, porque el dividendo del próximo año sale de la
utilidad del próximo año.

**9.4. Falso.** El inversionista que vende en tres años cobra el precio $P_3$, y ese precio es el VP,
en $t = 3$, de los dividendos que vienen después, incluidos los que empiezan en el año 6. Por eso el
horizonte no cambia el valor (sección 3): que no cobre dividendos mientras tenga la acción no
significa que no reciba nada; recibe su retorno como ganancia de capital. Si la empresa retiene esas
utilidades y las reinvierte a un ROE mayor que $k$, los dividendos futuros serán mayores y su acción
vale más, no menos. Solo valdría cero una empresa que nunca va a repartir nada. **Lo que anula la
respuesta:** decir «gana por la ganancia de capital» sin explicar de dónde sale el precio de venta.
Si $P_3$ no se ancla a dividendos futuros, el argumento contradice el modelo.

**9.5.**

| Año | Dividendo | VP al 12 % |
|---|---|---|
| 1 | 120,00 | 107,14 |
| 2 | 136,80 | 109,06 |
| 3 | 155,95 | 111,00 |
| 4 | 177,79 | 112,99 |
| Suma | | 440,19 |

$D_5 = 177{,}79 \times 1{,}04 = 184{,}90$; $P_4 = 184{,}90 / 0{,}08 = 2.311{,}21$, que a hoy vale
${2{.}311}{,}21 / 1{,}12^4 = 1.468{,}81$. (a) $P_0 = 440{,}19 + 1.468{,}81 =$ **1.909,00**. (b) El valor
terminal es el 76,9 % del precio. (c) Descontándolo cinco veces da 1.751,63: un error de 157 pesos por
acción. (d) Con 4 % desde el año 1, $120/0{,}08 = 1.500$. Lectura: los cuatro años de expansión valen
unos 409 pesos por acción; si la expansión se atrasa, eso es lo que está en juego.

**9.6.** Sin crecimiento: $340/0{,}11 = 3.090{,}91$ y P/U de 9,09. Con la nueva política,
$D_1 = 0{,}55 \times 340 = 187$.

| ROE | $g = 0{,}45 \times ROE$ | Precio | VPOC | P/U |
|---|---|---|---|---|
| (a) 15 % | 6,75 % | 4.400,00 | 1.309,09 | 12,94 |
| (b) 8 % | 3,60 % | 2.527,03 | $-563{,}88$ | 7,43 |
| (c) 11 % | 4,95 % | 3.090,91 | 0,00 | 9,09 |

Recomendación: retener solo si las sucursales rinden más que el 11 % que exigen los accionistas. En
(b) la empresa crece 3,60 % al año y aun así su acción cae de 3.090,91 a 2.527,03: invierte al 8 % la
plata que sus dueños podrían poner al 11 %. En (c) crece sin crear valor. Si el directorio no sabe
qué ROE tendrán las sucursales, esa es la pregunta que debe responder antes de decidir.

**9.7.** (a) Sanitaria: ${1{.}250}/96 =$ **13,02**. Tecnológica: $820/40 =$ **20,50**. (b)

| | Sin crecimiento ($UPA_1/k$) | VPOC | Parte del precio | P/U sin crecimiento ($1/k$) |
|---|---|---|---|---|
| Sanitaria | 1.200,00 | 50,00 | 4,0 % | 12,50 |
| Tecnológica | 307,69 | 512,31 | 62,5 % | 7,69 |

(c) El P/U alto de la sanitaria casi no tiene que ver con crecimiento: viene de su $k$ bajo (una
empresa regulada y estable se transa a 12,50 veces aunque no crezca). El de la tecnológica es casi
todo VPOC: el 62,5 % del precio es una apuesta a proyectos futuros. «Más cara» no se sigue del P/U; lo
que sí se sigue es que la tecnológica depende mucho más de que sus oportunidades se cumplan.

**9.8. Falso.** La tasa que exigen los accionistas se construye desde la tasa sin riesgo más un premio
por el riesgo de la acción. Si el Banco Central sube la tasa y eso sube la rentabilidad sin riesgo,
sube $k$ aunque los dividendos esperados sean los mismos, y el precio cae porque los mismos flujos se
descuentan a una tasa mayor. Con $D_1 = 50$ y $g = 3\ \%$, si $k$ pasa de 9 % a 10 %, el precio baja de
833,33 a 714,29, un 14,3 %. Además, cuanto más cerca esté $g$ de $k$, más fuerte es la caída (la
sensibilidad de Gordon). **Matiz:** en la práctica una subida de tasas también puede cambiar los
dividendos esperados (menos ventas, deuda más cara), pero eso refuerza la caída; la afirmación es falsa
incluso con los flujos quietos. **Lo que anula la respuesta:** mirar solo el numerador.

**9.9.** (a) Sin el proyecto: $95/0{,}11 = 863{,}64$. La perpetuidad de la utilidad nueva vale
${2{.}700}/0{,}11 = 24.545{,}45$ millones, parada en $t = 1$ junto a la inversión: VAN en $t = 1$ de
$-18.000 + 24.545{,}45 = 6.545{,}45$ millones; a hoy, ${6{.}545}{,}45/1{,}11 = 5.896{,}81$ millones. Por
acción, VPOC $= 5.896{,}81/600 =$ **9,83**, y el precio queda en **873,46**. El P/U sube de 9,09 a
9,19. Si olvidas traer el VAN desde $t = 1$, el VPOC da 10,91. (b) Al 14 %: la perpetuidad vale
19.285,71 millones, el VAN en $t = 1$ es 1.285,71 y a hoy 1.127,82 millones; el VPOC baja a 1,88 y el
precio a 865,52. (c) El proyecto rinde ${2{.}700}/18.000 =$ 15 % al año sobre lo invertido: conviene
mientras la tasa exigida sea menor que 15 %. Es la regla de la sección 8 con otro nombre: el VPOC es
positivo si lo invertido rinde más de lo que se le exige.

**9.10.** (a) Los dividendos de la etapa alta son 96,00, 113,28, 133,67, 157,73 y 186,12. Se prueba
con algunas tasas:

| $k$ | Precio con dos etapas |
|---|---|
| 9 % | 2.795,72 |
| 10 % | 2.344,81 |
| 11 % | 2.014,80 |

A 9 % el precio todavía queda bajo 3.200, así que la tasa es menor. Afinando, **$k =$ 8,33 %**: a esa
tasa la etapa alta suma 529,51 y el valor terminal, 3.984,90 en el año 5, vale 2.670,49 hoy; juntos,
3.200. (b) Gordon con 3,5 %: $96/3.200 + 3{,}5\ \% =$ 6,5 %, demasiado bajo porque ignora cinco años de
crecimiento alto. Gordon con 18 %: 21,0 %, absurdo porque supone 18 % para siempre. La respuesta
correcta queda entre los dos. (c) El valor terminal es el 83,5 % del precio: casi todo lo que se paga
depende de lo que pase después del año 5. Si el crecimiento alto dura menos, el precio no se sostiene.

---

## 14. Caso integrador · Valentina y las acciones de Textil Andes

> Este caso sigue a Valentina, dueña de Estampa Sur, por todo el ramo. Todo es ficticio. La fuente de
> las cifras es `verificacion/caso_valentina.py`.

Valentina piensa poner parte de sus ahorros en acciones de **Textil Andes**, una textil que cotiza en
bolsa. Los analistas esperan un dividendo de **\$86,40** por acción el próximo año, que crecerá
**3,2 %** al año para siempre, y le exigen a la acción un **11 %**. La utilidad por acción esperada es
**\$118**.

**Pregunta.** ¿Cuánto vale una acción? ¿Cuánto de ese precio paga por crecimiento?

**Desarrollo.**

1. **Precio con Gordon.** $P_0 = 86{,}40/(0{,}11 - 0{,}032) =$ **1.107,69**.
2. **Valor sin crecimiento.** Si repartiera toda la utilidad y no creciera: $118/0{,}11 = 1.072{,}73$.
3. **VPOC.** ${1{.}107}{,}69 - 1.072{,}73 =$ **34,97** por acción, apenas el 3,2 % del precio.
4. **De dónde sale el crecimiento.** Reparte $86{,}40/118 =$ 73,2 % y retiene 26,8 %. Para crecer 3,2 %
   con esa retención, el ROE de lo que reinvierte tiene que ser $0{,}032/0{,}268 =$ 11,95 %. Como supera
   el 11 % exigido, el VPOC es positivo, aunque chico.
5. **P/U.** ${1{.}107}{,}69/118 = 9{,}39$, apenas sobre el $1/0{,}11 = 9{,}09$ de una empresa que no crece.
6. **Comprobación.** $86{,}40/1.107{,}69 + 3{,}2\ \% =$ 7,8 % de dividendo más 3,2 % de crecimiento: el 11 %
   exigido. Si nada cambia, en un año la acción valdrá ${1{.}107}{,}69 \times 1{,}032 = 1.143{,}14$.

**Lectura.** Textil Andes es una empresa madura: casi todo su precio son los activos de hoy, y su
crecimiento crea poco valor porque reinvierte a un ROE apenas sobre lo que se le exige. El precio es
muy sensible a la tasa: el 11 % es una cifra de analistas, no un cálculo. **La unidad 12** la recalcula
con el CAPM desde el beta de la acción; da 10,28 %, y con esa tasa el precio sube a 1.219,80. Bajar
la tasa en 0,72 puntos sube el precio en 112 pesos: 3,2 veces todo el VPOC.

**Lo que pasa a la unidad 11.** Textil Andes entra a la cartera de Valentina junto con un fondo, y lo
que importa ahí ya no es solo cuánto rinde, sino cuánto varía y cómo se mueve con el resto.

---

## 15. Para seguir

**En los libros del ramo.**

- Ross, Westerfield y Jaffe, *Finanzas corporativas* (9.ª ed., 2012), capítulo 9 (el que fija el
  programa para valoración de acciones): dividendos con crecimiento cero, constante y diferencial,
  de dónde salen $g$ y $k$, y el valor de las oportunidades de crecimiento.
- Brealey, Myers y Allen, *Principios de finanzas corporativas* (9.ª ed., 2010): el programa asigna su
  capítulo 5 en las semanas de acciones. La numeración cambia entre ediciones; busca el capítulo sobre
  el valor de las acciones ordinarias.

**Abierto y gratis.**

- Dahlquist y Knight, *Principles of Finance*, OpenStax (2022), en inglés, capítulo 11 (valoración de
  acciones: modelos de descuento de dividendos, acciones preferentes y mercados eficientes).
  Licencia CC BY-NC-SA: https://openstax.org/books/principles-finance/pages/11-why-it-matters

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame una acción con dos etapas de crecimiento
que parta de un dividendo que ya se pagó, y corrígeme la línea de tiempo del valor terminal».
