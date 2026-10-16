---
ramo: Finanzas
unidad: 8
titulo: Duración, convexidad e inmunización
version: 0.1 (15-10-2026)
requiere: [07-bonos]
alimenta: []
verificacion: verificacion/u08_duracion.py
---

# Unidad 8 · Duración, convexidad e inmunización

**Qué vas a poder hacer.** Calcular la duración de Macaulay de un bono con una tabla y leerla como
plazo promedio; pasar a la duración modificada y estimar cuánto cambia el precio cuando se mueve la
tasa; corregir esa estimación con la convexidad; comparar el riesgo de tasa de dos bonos; y armar con
dos instrumentos una cartera que asegure un pago futuro aunque la tasa se mueva (inmunización),
sabiendo qué protege y qué no.

**Lo que necesitas antes.** Precio de un bono y YTM (unidad 7), y la idea de reinversión de la TIR
(unidad 5). Un poco de cálculo: la derivada de $(1+y)^{-t}$.

**Tiempo.** Unas 4,5 horas: 2 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. El problema · cuánto se mueve el precio

En la unidad 7 viste que si la tasa sube, el precio del bono baja. La pregunta de esta unidad es
**cuánto**. Dos bonos con el mismo vencimiento pueden reaccionar muy distinto, y una cartera de bonos
necesita un número que resuma su sensibilidad sin volver a descontar todo cada vez.

La curva precio-tasa de un bono no es una recta: baja cada vez más lento a medida que la tasa sube.
Ese dibujo tiene dos piezas que esta unidad mide por separado:

- la **pendiente** en la tasa de hoy, que mide la **duración**;
- la **curvatura**, que mide la **convexidad**.

---

## 2. Duración de Macaulay · cuándo vuelve la plata, en promedio

$$D = \frac{1}{P}\sum_{t=1}^{n} t \cdot \frac{F_t}{(1+y)^{t}} \qquad \text{con} \quad P = \sum_{t=1}^{n} \frac{F_t}{(1+y)^{t}}$$

Es el **plazo promedio ponderado** de los flujos, donde cada fecha pesa lo que su flujo aporta, en
valor presente, al precio. Se mide en años (o en períodos, si los flujos son semestrales). $y$ es la
tasa de mercado, no la tasa cupón.

**La imagen.** Pon los flujos como pesos sobre una regla de 0 a $n$ años, cada uno del tamaño de su
valor presente. La duración es el punto donde la regla queda en equilibrio.

**Cómo se calcula a mano (seis pasos).**

1. Flujos: cupón $= VN \cdot c$; en el último período, cupón más nominal.
2. Factor de descuento $1/(1+y)^{t}$, con la tasa de mercado.
3. Columna de valor presente; la suma tiene que dar el precio.
4. Columna $t \times VP$; se suma y se divide por el precio: esa es $D$.
5. $D_{mod} = D/(1+y)$.
6. $\Delta P/P \approx -D_{mod}\,\Delta y$, con $\Delta y$ en decimal y con su signo.

### Lo que mueve la duración

| Si… | la duración… | por qué |
|---|---|---|
| el bono es **cero cupón** | es igual al plazo, $D = n$ | un solo flujo: todo el peso está al final |
| el plazo es más largo | sube | la plata llega más tarde |
| el cupón es más bajo | sube | pesa más el nominal del final |
| la tasa de mercado es más baja | sube, poco | los flujos lejanos se castigan menos |
| el bono amortiza capital | baja | la plata vuelve antes: cero cupón > bullet > francés > alemán |
| es una perpetuidad | $D = (1+y)/y$ | no depende de ningún plazo |

**La duración de una cartera** es el promedio de las duraciones ponderado por el **valor** de cada
instrumento: $D_{cartera} = \sum w_i D_i$. Esta propiedad es la que permite fabricar cualquier
duración combinando dos bonos, aunque ninguno la tenga solo.

---

## 3. Duración modificada · cuánto se mueve el precio

Derivando el precio respecto de la tasa:

$$\frac{dP}{dy} = -\sum_{t=1}^{n} t\,\frac{F_t}{(1+y)^{t+1}} = -\frac{D}{1+y}\,P$$

Se define la **duración modificada** $D_{mod} = \dfrac{D}{1+y}$ y queda la aproximación de primer orden:

$$\frac{\Delta P}{P} \approx -D_{mod}\,\Delta y \qquad \Delta P \approx -D_{mod}\,\Delta y\,P$$

**Cómo se lee.** Un bono con $D_{mod} = 4$ pierde cerca de 4 % si la tasa sube un punto, y gana cerca
de 4 % si baja un punto. Entre dos bonos, el de mayor $D_{mod}$ tiene **más riesgo de tasa**. La
comparación se hace en porcentaje: un bono caro puede perder más pesos sin ser más riesgoso.

**Cupón semestral.** Se trabaja todo en semestres: la tasa del semestre por equivalencia, la $D$ en
semestres (se divide por 2 para pasarla a años) y la $D_{mod}$ con la tasa del semestre, que se
multiplica por el cambio de la tasa **semestral**.

---

## 4. Convexidad · la corrección de segundo orden

La duración trata la curva precio-tasa como su recta tangente. Para cambios chicos sirve; para cambios
grandes se equivoca, y **siempre en el mismo sentido**: la curva queda sobre la recta. El precio real
cae menos de lo que dice la duración cuando la tasa sube, y sube más cuando la tasa baja.

La convexidad mide esa curvatura:

$$C = \frac{1}{P}\,\frac{d^{2}P}{dy^{2}} = \frac{1}{P}\sum_{t=1}^{n} \frac{t\,(t+1)\,F_t}{(1+y)^{t+2}}$$

y entra en la aproximación de segundo orden (un desarrollo de Taylor):

$$\frac{\Delta P}{P} \approx -D_{mod}\,\Delta y + \frac{1}{2}\,C\,(\Delta y)^{2}$$

**Tres ideas que se preguntan.**

1. El término de convexidad **siempre suma**, porque $(\Delta y)^2$ es positivo suba o baje la tasa.
2. Como va al cuadrado, con medio punto de cambio casi no se nota; con dos puntos ya pesa.
3. Entre dos bonos con la misma duración, **conviene el de mayor convexidad**: gana más si la tasa baja
   y pierde menos si sube. Por eso, en un mercado real, la convexidad se paga con algo menos de
   rentabilidad.

En un cero cupón la convexidad es $n(n+1)/(1+y)^2$: crece con el cuadrado del plazo.

---

## 5. Inmunización · asegurar un pago futuro

Tienes que pagar un monto $L$ en $H$ años (una cuota, el pie de una casa, una pensión) y tienes la
plata hoy. Si compras bonos, enfrentas dos riesgos que tiran para lados opuestos:

| Si la tasa sube… | Si la tasa baja… |
|---|---|
| **efecto precio:** lo que vendas antes del vencimiento vale menos | lo que vendas vale más |
| **efecto reinversión:** los cupones se reinvierten a más | los cupones se reinvierten a menos |

**Inmunizar** es armar la cartera para que los dos efectos se cancelen. Para un pasivo único:

1. **Mismo valor presente:** $VP_{activos} = L/(1+y)^{H}$.
2. **Misma duración:** $D_{activos} = H$.
3. (Para que el calce aguante también hacia los dos lados) **convexidad de los activos mayor o igual
   que la del pasivo**. El pasivo es un cero a $H$ años, con convexidad $H(H+1)/(1+y)^2$.

**Con dos instrumentos** de duraciones $D_A < H < D_B$, el peso en $B$ sale de calzar la duración:

$$w_B\,D_B + (1 - w_B)\,D_A = H \quad\Longrightarrow\quad w_B = \frac{H - D_A}{D_B - D_A}$$

y los montos son $w_B$ y $1 - w_B$ por el valor presente del pasivo.

### Por qué funciona (y para qué cambios)

El valor de la cartera en la fecha $H$ es $V_H(y) = P(y)\,(1+y)^{H}$: lo que vale hoy, capitalizado.
Derivando su logaritmo:

$$\frac{d \ln V_H}{dy} = \frac{P'(y)}{P(y)} + \frac{H}{1+y} = \frac{H - D}{1+y}$$

Si $D = H$, la pendiente es **cero**: un cambio chico de la tasa no mueve, en primer orden, lo que la
cartera tendrá en $H$. Si además la cartera es más convexa que el pasivo, esa tasa es un **mínimo**:
cualquier cambio paralelo, hacia arriba o hacia abajo, deja la cartera **un poco sobre** la meta.

Si $D > H$, domina el efecto precio: preocupa que la tasa **suba**. Si $D < H$, domina la
reinversión: preocupa que **baje**.

### Lo que la inmunización no cubre

- **Cambios no paralelos.** El argumento supone que todas las tasas se mueven lo mismo. Si las cortas
  bajan y las largas suben (la curva se tuerce), la cartera puede quedar corta (ejercicio 8.9).
- **El paso del tiempo y los cambios de tasa.** La duración de la cartera y el plazo del pasivo no
  bajan al mismo ritmo, y la duración cambia cada vez que se mueve la tasa. Hay que **rebalancear**.
- **Una curva que no es plana.** Con una sola tasa todo cuadra; con una curva real, cada flujo tiene
  su propia tasa y la duración por YTM es una aproximación.
- **Impago y rescate anticipado.** La inmunización cubre el riesgo de tasa, no el de crédito.

---

## 6. Ejemplo resuelto · el pie del departamento en verde

Camila y Tomás firmaron la promesa de compra de un departamento en verde. Al momento de la entrega,
**en 4 años**, tienen que pagar un pie de **$18.400.000**. Hoy tienen la plata de una herencia y quieren
dejarla invertida de modo que, pase lo que pase con las tasas, lleguen justo a esa cifra. La tasa de
mercado es **5,3 %** anual para todos los plazos (curva plana). Hay dos instrumentos:

| Instrumento | Condiciones |
|---|---|
| Un cero cupón a 2 años | paga 100 en el año 2 |
| Un bono bullet a 6 años | 100 de nominal, cupón anual de 6,2 % |

**Paso 1 · Cuánta plata hace falta hoy.**

$$VP_{pasivo} = \frac{18{.}400{.}000}{1{,}053^{4}} = 14{.}965{.}952$$

Necesitan invertir **$14.965.952**.

**Paso 2 · La duración del bono.**

| $t$ | Flujo | Factor al 5,3 % | Valor presente | $t \times VP$ |
|---|---|---|---|---|
| 1 | 6,2 | 0,949668 | 5,89 | 5,89 |
| 2 | 6,2 | 0,901869 | 5,59 | 11,18 |
| 3 | 6,2 | 0,856475 | 5,31 | 15,93 |
| 4 | 6,2 | 0,813367 | 5,04 | 20,17 |
| 5 | 6,2 | 0,772428 | 4,79 | 23,95 |
| 6 | 106,2 | 0,733550 | 77,90 | 467,42 |
| **Suma** | | | **104,52** | **544,54** |

$$D_B = \frac{544{,}54}{104{,}52} = 5{,}2096 \text{ años} \qquad D_{mod} = \frac{5{,}2096}{1{,}053} = 4{,}9474$$

La convexidad, con la misma tabla y la columna $t(t+1)F_t/(1+y)^{t+2}$, es **31,28**. El cero a 2 años
vale 90,19 y su duración es 2.

**Paso 3 · Qué pasaría con el bono si la tasa salta un punto.**

| Cambio de tasa | Solo duración | Duración y convexidad | Exacto (descontando de nuevo) |
|---|---|---|---|
| +1 punto | −4,95 % (99,35) | −4,79 % (99,52) | −4,79 % (99,51) |
| −1 punto | +4,95 % (109,70) | +5,10 % (109,86) | +5,11 % (109,86) |

La duración sola exagera la caída y se queda corta en la subida. Con la convexidad, el error baja al
segundo decimal.

**Paso 4 · Los pesos.** El cero tiene $D = 2$ y el bono $D = 5{,}2096$; el horizonte es 4:

$$w_B = \frac{4 - 2}{5{,}2096 - 2} = 62{,}31\,\% \qquad w_{cero} = 37{,}69\,\%$$

**Paso 5 · Los montos.** En el bono, $0{,}6231 \times 14{.}965{.}952$ = **$9.325.604**; en el cero,
**$5.640.347**. Al precio de cada uno, son $8.921.921 de nominal del bono y $6.254.068 de nominal del
cero, que es lo que el cero paga en el año 2.

**Paso 6 · La prueba.** Justo después de comprar, la tasa salta y se queda ahí. En el año 2 el cero paga
y esa plata se reinvierte hasta el año 4; los cupones del bono también se reinvierten; en el año 4 se
vende el bono, al que le quedan 2 años. Lo que tienen en el año 4:

| Estrategia | Tasa igual | Tasa +1 punto | Tasa −1 punto |
|---|---|---|---|
| **Inmunizada** (62,31 % bono, 37,69 % cero) | $18.400.000 | $18.403.186 | $18.403.244 |
| Todo en el bono a 6 años ($D > H$) | $18.400.000 | $18.192.737 | $18.615.575 |
| Todo en el cero a 2 años ($D < H$) | $18.400.000 | $18.751.137 | $18.052.182 |

**Paso 7 · La lectura.** La cartera inmunizada llega a la meta en los tres escenarios, e incluso la
supera un poco ($3.186 y $3.244): es la convexidad, 21,53 en la cartera contra 18,04 del pasivo. Si
ponen todo en el bono largo, una subida de un punto les deja **$207.263** cortos para el pie (pesa el
precio de venta), aunque una bajada les regalaría $215.575. Si ponen todo en el cero corto, el riesgo es
el contrario: una subida les deja $351.137 de sobra, pero una bajada los deja **$347.818** cortos (pesa la
reinversión). Calzar la duración es lo que hace que un riesgo tape al
otro. Ojo: esto vale para un salto **paralelo** y con rebalanceo; la sección 5 dice qué no cubre.

---

## 7. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Usar $D$ en vez de $D_{mod}$ en la fórmula del precio | La modificada divide por $1 + y$; siempre es algo menor que $D$ |
| Perder el signo | Si la tasa sube, el precio baja: $\Delta P/P \approx -D_{mod}\,\Delta y$ |
| Escribir $\Delta y$ en puntos | Medio punto es 0,005, no 0,5 |
| Descontar con la tasa cupón | Los pesos de la duración se calculan con la tasa de mercado |
| Dejar la duración en semestres | Se divide por 2 para reportarla en años |
| Decir que el bono que más pesos pierde es el más riesgoso | El riesgo de tasa se compara en %, con la $D_{mod}$ |
| Restar el término de convexidad | $\tfrac{1}{2}C(\Delta y)^2$ siempre suma, suba o baje la tasa |
| Inmunizar calzando solo la duración, sin el valor presente | Son dos condiciones: mismo VP y misma duración |
| Comprar y olvidarse | Hay que rebalancear con el tiempo y con cada movimiento de tasa |

---

## 8. Práctica

Diez ejercicios: 8.1 a 8.4 básicos, 8.5 a 8.8 intermedios, 8.9 y 8.10 de desafío. Los ejercicios 8.4 y
8.10 son **comentes**: responde Verdadero, Falso o Incierto y argumenta en no más de cinco líneas.
Salvo que se diga otra cosa, los cupones son anuales, los bonos son bullet de 100 de nominal y la curva
es plana. Las pautas están en la sección 9.

**8.1 · Duración con tabla (básico).** Un bono a 3 años paga un cupón de 7,4 % y la tasa de mercado es
6,1 %. (a) Arma la tabla y calcula el precio, la duración y la duración modificada. (b) Si la tasa sube
medio punto, estima el nuevo precio. (c) Compáralo con el precio exacto.

**8.2 · Los dos extremos (básico).** (a) Un cero cupón a 7 años con tasa de 4,8 %: precio, duración y
duración modificada sin tabla. (b) Una perpetuidad con tasa de 6,5 %: duración y duración modificada.
(c) Si la tasa de cada uno sube un punto, estima la caída por duración y compárala con la exacta.

**8.3 · La duración de una cartera (básico).** Un fondo de inversión tiene \$40 millones en el bono A
($D = 2{,}3$), \$25 millones en el B ($D = 5{,}8$) y \$35 millones en el C ($D = 8{,}6$), y debe pagar en 5
años un monto cuyo valor presente es justo \$100 millones. (a) ¿Cuál es la duración de la cartera? (b)
¿Está inmunizada? ¿Qué le preocupa más al gerente, que la tasa suba o que baje? (c) Sin tocar el B,
¿cuánto hay que pasar de C a A para inmunizar?

**8.4 · Comente: el cero cupón (básico).** «Un bono cero cupón no tiene riesgo de tasa, porque no paga
cupones que haya que reinvertir.»

**8.5 · Cupón semestral (intermedio).** Un bono de 2.500 UF paga un cupón de 2,25 % cada semestre y le
quedan 4 años (8 semestres). La tasa de mercado es 5,1 % anual efectiva. (a) Pasa la tasa a semestral
y calcula el precio. (b) Calcula la duración en semestres y en años, y la modificada por semestre. (c)
Si la tasa anual sube a 5,9 %, estima la variación del precio con la duración modificada y compárala con
la exacta.

**8.6 · Cuando la tasa salta dos puntos (intermedio).** Un bono a 8 años paga un cupón de 4,5 % y la
tasa es 6,8 %. (a) Calcula el precio, la duración, la modificada y la convexidad. (b) Estima el cambio
de precio si la tasa sube 2 puntos y si baja 2 puntos, con solo duración y con duración y convexidad.
(c) Compara con el exacto. ¿Qué muestra la asimetría?

**8.7 · Bala contra pesas (intermedio).** Con $10.000.000 y una tasa de 5,5 %, se puede comprar (A) un
cero cupón a 5 años o (B) mitad en un cero a 1 año y mitad en un cero a 9 años. (a) Muestra que las
dos carteras tienen la misma duración y la misma duración modificada. (b) Calcula la convexidad de
cada una. (c) Valora las dos si la tasa sube y si baja 2 puntos. ¿Cuál prefieres y por qué?

**8.8 · El estanque de la cooperativa (intermedio).** Una cooperativa de agua potable rural debe
pagar $45.000.000 en 6 años por un estanque nuevo. La tasa es 4,7 %. Puede comprar un cero a 3 años y
un bono a 10 años con cupón de 5 %. (a) Calcula el valor presente del pasivo, el precio y la duración
de cada instrumento. (b) Calcula los pesos y los montos que inmunizan. (c) Comprueba que se cumple la
condición de convexidad. (d) ¿Cuánto tiene la cooperativa en el año 6 si, justo después de comprar,
la tasa sube o baja un punto?

**8.9 · Lo que la inmunización no cubre (desafío).** Sigue la cartera del 8.8. (a) Pasa un año y la
tasa no cambia. La cooperativa cobró el primer cupón del bono. Calcula el valor de cada posición, la
duración de los dos bonos juntos (sin el cupón cobrado) y la duración contando el cupón como caja.
¿Cómo hay que rebalancear para volver a calzar? (b) Vuelve al día de la compra. Supón que la curva se
tuerce: todas las reinversiones hasta el año 6 se hacen a 3,7 % y el bono se vende en el año 6 con una
tasa de 5,7 %. ¿Cuánto tiene la cooperativa en el año 6?

**8.10 · Comente: comprar y olvidarse (desafío).** «Una cartera inmunizada asegura el pago: una vez
armada, el gerente puede olvidarse de ella hasta la fecha del pasivo.» Apóyate en el 8.9.

---

## 9. Pautas

**8.1.** (a)

| $t$ | Flujo | Factor al 6,1 % | Valor presente | $t \times VP$ |
|---|---|---|---|---|
| 1 | 7,4 | 0,942507 | 6,97 | 6,97 |
| 2 | 7,4 | 0,888320 | 6,57 | 13,15 |
| 3 | 107,4 | 0,837247 | 89,92 | 269,76 |
| **Suma** | | | **103,47** | **289,88** |

$D = 289{,}88/103{,}47 =$ **2,8017** años; $D_{mod} = 2{,}8017/1{,}061 =$ **2,6406**. (b)
$\Delta P/P \approx -2{,}6406 \times 0{,}005 = -1{,}320\,\%$: precio estimado **102,10**. (c) Al 6,6 % el
precio exacto es **102,11** (−1,308 %). Lectura: con medio punto la recta casi no se separa de la curva;
la estimación queda apenas bajo el exacto, como siempre.

**8.2.** (a) $P = 100/1{,}048^{7} =$ **72,02**; $D = 7$ (un solo flujo); $D_{mod} = 7/1{,}048 =$
**6,6794**. (b) $D = 1{,}065/0{,}065 =$ **16,38** años y $D_{mod} = 1/0{,}065 =$ **15,38**. (c)

| | Estimación por duración | Exacto |
|---|---|---|
| Cero a 7 años | −6,68 % | −6,43 % |
| Perpetuidad | −15,38 % | −13,33 % |

Lectura: la perpetuidad no vence nunca, pero su duración es finita (16,38 años) porque los flujos
lejanos casi no pesan en el precio. Es mucho más sensible que el cero, y la estimación lineal se
equivoca más porque su convexidad es enorme.

**8.3.** (a) $D = 0{,}40 \times 2{,}3 + 0{,}25 \times 5{,}8 + 0{,}35 \times 8{,}6 =$ **5,38** años. (b) Tiene
el valor presente, pero no la duración: $D > H$, así que domina el efecto precio y al gerente le
preocupa que la tasa **suba**. (c) Cada millón que pasa de C a A baja la duración en
$(8{,}6 - 2{,}3)/100$; para bajar 0,38 años hay que mover **6,03 millones**: A queda en 46,03 y C en
28,97 millones.

**8.4. Falso.** El cero cupón no tiene riesgo de **reinversión**, porque no hay cupones; eso es
verdad. Pero tiene el **máximo riesgo de precio** para su plazo: su duración es el plazo completo,
mayor que la de cualquier bono con cupón al mismo vencimiento. Si se vende antes de vencer, una subida
de tasa lo golpea más que a ninguno (8.2: un cero a 7 años cae cerca de 6,4 % con un punto). Solo deja
de tener riesgo de tasa para quien lo mantiene justo hasta su vencimiento: por eso un cero con
vencimiento en $H$ inmuniza por sí solo un pago en $H$.

**8.5.** (a) $i_{sem} = 1{,}051^{1/2} - 1 =$ **2,5183 %**; cupón $0{,}0225 \times 2{.}500 = 56{,}25$ UF;
precio **2.451,95 UF**. (b) $D =$ **7,4033** semestres $=$ **3,7016** años;
$D_{mod} = 7{,}4033/1{,}025183 =$ **7,2214** por semestre. (c) La tasa semestral pasa a
$1{,}059^{1/2} - 1 =$ **2,9077 %**: sube 0,3894 puntos por semestre.
$\Delta P/P \approx -7{,}2214 \times 0{,}003894 = -2{,}81\,\%$, precio estimado **2.382,99 UF**. El exacto es
**2.384,12 UF** (−2,77 %). Lectura: el cambio que se multiplica es el de la tasa **semestral**; si
multiplicaras la $D_{mod}$ semestral por los 0,8 puntos anuales, duplicarías la caída.

**8.6.** (a) Precio **86,16**; $D =$ **6,7919**; $D_{mod} =$ **6,3594**; convexidad **50,62**. (b) y (c)

| Cambio | Solo duración | Duración y convexidad | Exacto |
|---|---|---|---|
| +2 puntos | −12,72 % (75,20) | −11,71 % (76,07) | −11,76 % (76,02) |
| −2 puntos | +12,72 % (97,12) | +13,73 % (97,99) | +13,80 % (98,05) |

Lectura: la duración da el mismo 12,72 % para los dos lados; la realidad es asimétrica: se pierde
menos cuando sube (11,76 %) y se gana más cuando baja (13,80 %). Esa asimetría es la convexidad, y
juega a favor del tenedor. Con dos puntos, la duración sola se equivoca en más de un punto porcentual;
con la convexidad el error baja a menos de una décima.

**8.7.** (a) A: $D = 5$. B: $0{,}5 \times 1 + 0{,}5 \times 9 = 5$. Las dos tienen $D_{mod} = 5/1{,}055 =$
**4,7393**. (b) A: $5 \times 6/1{,}055^{2} =$ **26,95**. B: el promedio de $1 \times 2$ y $9 \times 10$,
dividido por $1{,}055^2$: **41,33**.

| Tasa | A · bala (cero a 5 años) | B · pesas (ceros a 1 y 9) | Ventaja de B |
|---|---|---|---|
| +2 puntos | $9.103.743 | $9.129.441 | $25.698 |
| −2 puntos | $11.004.253 | $11.036.516 | $32.264 |

(c) Con la misma duración, las pesas ganan en los dos escenarios: pierden menos si la tasa sube y ganan
más si baja. Es la convexidad. Ojo: con una curva plana parece plata gratis; en un mercado real la
convexidad se paga, y la cartera de pesas rinde algo menos si la tasa no se mueve.

**8.8.** (a) $VP_{pasivo} = {45{.}000{.}000}/{1{,}047^{6}} =$ **$34.161.145**. El cero a 3 años vale **87,13** y
su duración es 3. El bono vale **102,35** y su duración es **8,1330**. (b)
$w_B = (6 - 3)/(8{,}1330 - 3) =$ **58,45 %**; $w_{cero} =$ **41,55 %**. Montos: **$19.965.680** en el bono y
**$14.195.465** en el cero. (c) Convexidad de la cartera **48,81** contra **38,31** del pasivo: se cumple.
(d) En el año 6 tiene **$45.000.000** con la tasa igual, **$45.023.354** si sube un punto ($23.354 de
sobra) y **$45.023.907** si baja ($23.907 de sobra). Lectura: la cooperativa paga el estanque en los
tres escenarios.

**8.9.** (a) Con la tasa igual, el cero (ahora a 2 años) vale **$14.862.652** y el bono (a 9 años, con
$D =$ **7,4821**) vale **$19.928.710**; en caja está el cupón cobrado, **$975.357**. Total
**$35.766.719**, justo el valor presente del pasivo a 5 años: con la tasa quieta, nada se perdió. Pero
los dos bonos juntos tienen una duración de **5,1402** años, más que los 5 que faltan: el bono tiene
**57,28 %** de lo invertido en bonos y para calzar debería tener **54,72 %**. Contando el cupón como caja
($D = 0$) la duración da justo 5, pero solo mientras esa plata quede en caja, y la caja no puede quedarse
quieta 5 años. Rebalanceo: dejar **$19.572.876** en el bono (vender $355.834) y **$16.193.843** en el cero
(comprar $1.331.191, que son el cupón más lo vendido del bono). (b) Con la curva torcida, en el año 6
tiene **$43.620.417**: le faltan **$1.379.583**. El cero se reinvierte a menos y el bono se vende con una
tasa más alta: los dos efectos que debían taparse empujan para el mismo lado.

**8.10. Falso.** La inmunización calza duración y valor presente **hoy**, para un salto **paralelo y
chico** de una curva plana. Tres cosas la desarman: (1) el tiempo, porque la duración de los bonos no
baja al mismo ritmo que el plazo del pago (8.9 a: tras un año los bonos quedan en 5,14 contra 5); (2)
cada cambio de tasa mueve las duraciones, y (3) un cambio no paralelo puede dejarla corta aunque el
calce sea perfecto (8.9 b: faltan $1.379.583 de $45.000.000). Por eso hay que **rebalancear**
periódicamente. Además no cubre el impago del emisor.

---

## 10. Caso integrador · Valentina asegura el saldo de la máquina

> Este caso sigue a Valentina, dueña de Estampa Sur, por todo el ramo. Acá se usan el saldo de la
> unidad 5 y el bono de la unidad 7. Si no has hecho esas unidades, parte de los datos de esta sección.

Valentina tiene que pagar **$8.750.000 en 3 años** por la segunda máquina del taller (unidad 5). Quiere
dejar hoy apartada la plata justa, de modo que llegue a esa cifra aunque la tasa se mueva. Tiene dos
instrumentos:

- el bono de **Eléctrica Andina** de la unidad 7: 4 años, cupón 5,9 %, precio 101,75, YTM 5,40 %;
- un **cero cupón a 1 año**.

**Supuesto de trabajo.** Se toma la YTM del bono, **5,401 %**, como tasa plana para todos los plazos.
Es la simplificación de esta unidad; la curva real de la unidad 6 no es plana.

**Pregunta.** ¿Cuánto invierte, en qué proporción, y qué pasa si la tasa sube o baja un punto?

**Desarrollo.**

1. **Valor presente del pasivo.** ${8{.}750{.}000}/{1{,}05401^{3}} =$ **$7.472.623**.
2. **Duración del bono.**

| $t$ | Flujo | Factor al 5,401 % | Valor presente | $t \times VP$ |
|---|---|---|---|---|
| 1 | 5,9 | 0,948757 | 5,5977 | 5,5977 |
| 2 | 5,9 | 0,900140 | 5,3108 | 10,6217 |
| 3 | 5,9 | 0,854014 | 5,0387 | 15,1160 |
| 4 | 105,9 | 0,810252 | 85,8057 | 343,2227 |
| **Suma** | | | **101,75** | **374,5580** |

$$D = \frac{374{,}5580}{101{,}7528} = 3{,}6811 \qquad D_{mod} = \frac{3{,}6811}{1{,}05401} = 3{,}4924 \qquad C = 16{,}10$$

   Si la tasa sube un punto, el bono cae −3,49 % por duración y −3,41 % exacto; si baja, sube 3,49 % por
   duración y 3,57 % exacto.

3. **Pesos.** El cero a 1 año tiene $D = 1$; el bono, 3,6811; el horizonte es 3:

$$w_B = \frac{3 - 1}{3{,}6811 - 1} = 74{,}60\,\% \qquad w_{cero} = 25{,}40\,\%$$

4. **Montos.** **$5.574.385** en el bono (son $5.478.358 de nominal, al 101,75 %) y **$1.898.238** en el
   cero, que en un año paga $2.000.763. Esa plata se reinvierte a la tasa que haya entonces.
5. **Convexidad.** La cartera tiene 12,47 y el pasivo, 10,80: se cumple la tercera condición.
6. **La prueba en el año 3** (la tasa salta justo después de comprar):

| Estrategia | Tasa igual | Tasa +1 punto | Tasa −1 punto |
|---|---|---|---|
| **Inmunizada** | $8.750.000 | $8.750.723 | $8.750.733 |
| Todo en el bono (vender en el año 3) | $8.750.000 | $8.694.162 | $8.807.253 |
| Todo en ceros a 1 año, renovados | $8.750.000 | $8.916.820 | $8.584.755 |

**Lectura.** Con la cartera inmunizada, Valentina paga la máquina en los tres escenarios y le sobran
unos setecientos pesos: es la convexidad a su favor. Si hubiera puesto todo en el bono, que dura más de
3 años, una subida de la tasa le habría dejado corta (el bono se vende barato en el año 3); si hubiera
renovado ceros cortos, el peligro habría sido una bajada (reinvierte a menos). Le quedan dos tareas:
revisar los pesos una vez al año (rebalancear) y recordar que el cálculo usa una curva plana, cuando en
la unidad 6 la tasa a 1 año era 4,80 % y no 5,40 %. Con la curva real, el cero cuesta algo más y el calce
es aproximado.

---

## 11. Para seguir

**En los libros del ramo.**

- Lazzatti, *Técnicas de inmunización basadas en la duración* (2001), la lectura que fija el programa
  para la estrategia de inmunización.
- Fabozzi, *The Handbook of Fixed Income Securities*, capítulos 2 y 9, los que fija el programa para la
  semana de riesgo de tasa, duración y convexidad.
- Ross, Westerfield y Jaffe, *Finanzas corporativas* (9.ª ed., 2012), capítulo 8, para repasar el
  precio de los bonos sobre el que se construye todo esto.

**Abiertos y gratis.**

- Dahlquist y Knight, *Principles of Finance*, OpenStax (2022), en inglés. La sección 10.4, «Risks of
  Interest Rates and Default», explica el riesgo de tasa y define la duración como sensibilidad del
  precio; no trae el cálculo de la duración, la convexidad ni la inmunización.
  https://openstax.org/books/principles-finance/pages/10-4-risks-of-interest-rates-and-default

**Con el tutor.** Pega `tutor/contexto.md` al inicio de la conversación y pídele, por ejemplo:
«Dame un pasivo a 5 años y dos bonos para inmunizarlo; corrígeme la tabla de duración y después
pruébame la cartera con un salto de tasa no paralelo».
