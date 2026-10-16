---
ramo: Tópicos de Optimización
unidad: 9
titulo: Problema de transporte y sus métodos
version: 0.1 (16-10-2026)
requiere: [08-ruta-mas-corta-y-flujo-maximo, ../../optimizacion/unidades/05-modelamiento-multiperiodo-y-transporte, ../../optimizacion/unidades/10-dualidad]
alimenta: [10-asignacion]
verificacion: verificacion/u09_transporte.py
---

# Unidad 9 · Problema de transporte y sus métodos

**Qué vas a poder hacer.** Balancear un problema de transporte con un origen o un destino ficticio,
armar una solución inicial por esquina noroeste, costo mínimo y Vogel, mejorarla con el método MODI
(potenciales $u_i$ y $v_j$, costos reducidos y ciclo) hasta el óptimo, reconocer y destrabar una
solución degenerada, y leer en la tabla final cuánto cuesta usar una ruta que el plan no usa.

**Lo que necesitas antes.** De Optimización, la unidad 5 (el transporte como programa lineal, con
oferta, demanda y destino ficticio) y la unidad 10 (qué es un precio dual). De la unidad 8 de este
ramo, la ruta más corta: los costos del caso salen de ella. Basta con saber que un modelo de
transporte tiene una restricción por origen y una por destino.

**Tiempo.** Unas 6 horas: 2 de lectura con el ejemplo y 4 de práctica a mano (los métodos se
aprenden haciéndolos).

---

## 1. La idea: una red de dos columnas

Un problema de transporte es una red con dos columnas de nodos. A la izquierda, los **orígenes**
(talleres, plantas, bodegas), cada uno con una oferta $a_i$. A la derecha, los **destinos**
(tiendas, clientes), cada uno con una demanda $b_j$. Cada arco $i \to j$ es una ruta con un costo
$c_{ij}$ por unidad. Se decide cuánto mandar por cada arco.

En Optimización ya lo escribiste como programa lineal y lo resolviste con el solver. Esta unidad hace
otra cosa: lo resuelve **a mano**, aprovechando su estructura, con un simplex que no necesita tabla
simplex. Sirve por tres razones:

1. **Se ve qué hace el solver.** Cada paso de MODI es un paso del simplex: una ruta entra, otra sale.
2. **La tabla final se lee sola.** El costo reducido de cada ruta vacía dice cuánto subiría el costo
   por cada unidad que se mande por ella.
3. **Escala.** Una tabla de $m \times n$ se recorre en minutos; el simplex con $m \cdot n$ variables y
   $m + n$ restricciones, no.

El problema de transporte es un caso del flujo de costo mínimo de la unidad 8: una red sin nodos de
paso. Si hay bodegas intermedias (transbordo), se vuelve al flujo general (sección 8).

---

## 2. El modelo, pieza por pieza

Así se escribe y así se corrige: cada pieza vale por sí sola.

**Conjuntos.** $O$ orígenes, $D$ destinos.

**Parámetros.** $a_i$ oferta del origen $i \in O$; $b_j$ demanda del destino $j \in D$; $c_{ij}$ costo
por unidad enviada de $i$ a $j$.

**Variable de decisión.** Tiene tres piezas y una naturaleza:

- índice con su rango: $x_{ij}$, con $i \in O$, $j \in D$;
- qué significa el valor: unidades enviadas del origen $i$ al destino $j$ en el período;
- el «en otro caso»: vale 0 si la ruta no se usa;
- naturaleza: $x_{ij} \in \mathbb{Z}_0^+$ (entera y no negativa).

**Objetivo y restricciones**, cada familia con su «para todo»:

$$\min \sum_{i \in O}\sum_{j \in D} c_{ij}\,x_{ij} \qquad \text{s.a.} \qquad \sum_{j \in D} x_{ij} \le a_i \;\; \forall i \in O, \qquad \sum_{i \in O} x_{ij} \ge b_j \;\; \forall j \in D$$

**¿Por qué entera si en OPL va `float+`?** Porque el transporte tiene una propiedad que casi ningún
modelo tiene: si las ofertas y demandas son enteras, **todos los vértices son enteros**. Cada variable
aparece con coeficiente 1 en exactamente una fila de oferta y una de demanda, y con esa matriz el
simplex nunca divide. Por eso se declara continua, se resuelve como programa lineal (con duales, que
es lo que interesa) y sale entera igual. El verificador de esta unidad corre el modelo también con
`dvar int+` y obtiene el mismo costo.

En OPL (`modelos/u09_transporte.mod`), con las rutas prohibidas como un conjunto de pares:

```opl
@@OPL:u09_transporte.mod@@
```

---

## 3. Balancear: el origen o el destino ficticio

Los métodos a mano exigen que la oferta total sea igual a la demanda total. Si no lo es:

| Caso | Se agrega | Su costo | Qué significa lo que recibe o envía |
|---|---|---|---|
| $\sum a_i > \sum b_j$ | un **destino ficticio** con demanda $\sum a_i - \sum b_j$ | 0 (o el costo de guardar) | lo que el origen no despacha |
| $\sum a_i < \sum b_j$ | un **origen ficticio** con oferta $\sum b_j - \sum a_i$ | 0, o la multa por unidad no entregada en cada destino | la demanda que queda sin atender |

Con costo 0 en el origen ficticio, el modelo deja sin atender a quien sale más caro abastecer. Si
cada destino tiene una multa distinta, ponla como costo del ficticio: el método decide entonces a
quién le falta, comparando flete contra multa.

Después de balancear, las restricciones se cumplen con igualdad y la tabla tiene $m + n$ filas y
columnas en total (contando el ficticio).

---

## 4. La tabla de transporte y la solución básica

La tabla tiene una fila por origen y una columna por destino; cada celda es una ruta. Una **solución
básica** usa exactamente $m + n - 1$ celdas (las **básicas**). ¿Por qué $m + n - 1$ y no $m + n$?
Porque en un problema balanceado una de las $m + n$ igualdades sobra: si se cumplen todas las de
oferta y todas las de demanda menos una, la última se cumple sola.

Las celdas básicas forman un **árbol** que conecta todas las filas y columnas: no tienen ciclos y no
dejan ninguna fila o columna aislada. Esa propiedad es la que usan los métodos de mejora. Si una
solución tiene menos de $m + n - 1$ celdas con envío positivo, se completa con **ceros básicos**
(sección 7).

---

## 5. Tres maneras de partir

Los tres métodos llenan la tabla de a una celda: mandan por ella lo más que se pueda (el menor entre
lo que le queda al origen y lo que le falta al destino) y tachan la fila o la columna que se agotó.

**Esquina noroeste.** Parte en la celda de arriba a la izquierda y avanza: a la derecha si se agotó
el destino, hacia abajo si se agotó el origen. **No mira los costos.** Es rápido y sirve para tener
una solución básica, nada más.

**Costo mínimo.** Elige la celda más barata entre las que siguen disponibles. Empate: la que admite
el envío más grande; si sigue el empate, la primera de arriba a la izquierda. Mira los costos, pero
uno a la vez: puede gastar una ruta barata y dejar a otro destino con una ruta carísima.

**Aproximación de Vogel.** Para cada fila y columna disponible calcula su **penalización**: la
diferencia entre sus dos costos más bajos. Elige la línea con la mayor penalización y asigna en su
celda más barata. Empate de penalizaciones: la línea con el costo más bajo; si sigue, filas antes que
columnas y en orden. Cuando queda una sola fila o una sola columna, el resto está forzado y se asigna
de la celda más barata a la más cara.

La intuición de Vogel: la penalización es **lo que se pierde por no usar la mejor ruta de esa línea**.
Si un destino tiene una ruta a \$400 y la siguiente a \$900, perder la primera cuesta \$500 por unidad;
si otro tiene dos rutas a \$500 y \$510, da casi lo mismo. Vogel atiende primero al que más arriesga.
Por eso suele quedar muy cerca del óptimo, y muchas veces en él.

**Si una fila y una columna se agotan a la vez**, se tacha solo una (en esta base, la fila, salvo que
sea la última) y la columna queda con demanda 0: más adelante recibe un envío de 0, que cuenta como
celda básica. Así la solución siempre tiene sus $m + n - 1$ básicas.

**Cuándo NO aplican.** Los tres suponen un costo lineal por unidad y ninguna capacidad por ruta. Si la
ruta tiene un tope o un costo fijo por usarla (camión que se paga entero), el problema deja de ser
transporte: va a OPL con las variables de la unidad 3.

---

## 6. Mejorar: el método MODI

Una solución básica es óptima si ninguna ruta vacía conviene. Para saberlo sin probar ruta por ruta,
MODI (*modified distribution*) le pone un **potencial** a cada fila y columna.

**Paso 1 · Potenciales.** En cada celda básica, el costo se reparte entre su fila y su columna:

$$u_i + v_j = c_{ij} \qquad \text{para cada celda básica } (i, j)$$

Son $m + n$ incógnitas y $m + n - 1$ ecuaciones: se fija $u_1 = 0$ y el resto sale en cadena,
siguiendo el árbol de básicas.

**Paso 2 · Costos reducidos.** Para cada celda vacía:

$$\bar c_{ij} = c_{ij} - u_i - v_j$$

Si todos son $\bar c_{ij} \ge 0$, la solución es **óptima**. Si alguno es negativo, esa ruta mejora el
plan: cada unidad que se mande por ella baja el costo en $|\bar c_{ij}|$.

**Paso 3 · El ciclo.** Entra la celda con el costo reducido más negativo (empate: la primera de arriba
a la izquierda). Con las básicas forma un **único ciclo** que dobla solo en celdas básicas,
alternando fila y columna. Se marcan sus celdas $+, -, +, -, \dots$ partiendo por la que entra. Se
manda $\theta$ = el menor envío entre las celdas marcadas con $-$: se suma en las $+$, se resta en las
$-$, y sale la celda $-$ que llegó a cero (si llegan dos, sale solo una, la primera; la otra queda
como cero básico). El costo baja exactamente $\theta \cdot |\bar c_{ij}|$.

**Por qué funciona.** Los potenciales son los **duales** del programa lineal: $u_i$ el de la oferta
del origen $i$ y $v_j$ el de la demanda del destino $j$ (unidad 10 de Optimización). La condición
$\bar c_{ij} \ge 0$ en todas las celdas es la factibilidad dual, y $u_i + v_j = c_{ij}$ en las
básicas es la holgura complementaria: cuando las dos se cumplen, el plan es óptimo. Por eso la salida
de OPL trae los mismos $u$, $v$ y costos reducidos que la última tabla de MODI (sección 13).

**El cruce de piedras (*stepping stone*) es el mismo cálculo por otro camino.** Para una celda
vacía, se arma su ciclo y se suma el costo de las celdas con signo: $+c$ en las $+$ y $-c$ en las $-$.
Ese total es su costo reducido. MODI es más rápido porque saca todos los costos reducidos con una
resta por celda; el cruce de piedras arma un ciclo por celda. El verificador comprueba que ambos
caminos den lo mismo en todas las celdas de todas las tablas de esta unidad.

---

## 7. Degeneración

Una solución es **degenerada** si tiene menos de $m + n - 1$ envíos positivos. Pasa cuando una fila y
una columna se agotan en el mismo paso. Sin la celda que falta, los potenciales no se pueden calcular
(el árbol queda partido en dos). El remedio: poner un **cero básico** en una celda que reconecte el
árbol, sin formar ciclo. Los métodos de la sección 5 ya lo hacen solos.

El cero básico es una celda como cualquier otra: tiene potencial, puede quedar marcada con $-$ en un
ciclo y entonces $\theta = 0$. En esa iteración **el costo no baja**, pero la base cambia y la
siguiente sí avanza. No es un error: es el simplex dando un paso en el mismo vértice. El ejercicio 9.7
lo muestra.

---

## 8. Variantes que aparecen siempre

| Situación | Qué se hace |
|---|---|
| Ruta prohibida | costo $M$ muy grande en los métodos a mano (gran M); en OPL, `x[o][d] == 0` |
| Maximizar ganancia | se resuelve con costo $= -$ganancia; o se invierte la regla: entra la ganancia reducida más positiva y es óptimo cuando todas son $\le 0$ |
| Envío mínimo por una ruta | se manda ese mínimo primero y se resuelve el resto; mientras la base no cambie, el costo sube (mínimo) $\times\ \bar c_{ij}$ |
| Varios óptimos | un $\bar c_{ij} = 0$ en la tabla final: esa ruta puede entrar sin cambiar el costo |
| Transbordo (bodegas de paso) | flujo de costo mínimo con balance en los nodos intermedios, como en la unidad 5 de Optimización; también se puede convertir en transporte dándole a cada nodo de paso una oferta y una demanda iguales a lo que puede mover |

**Una advertencia con la gran M.** Costo mínimo y Vogel pueden poner envío en una ruta $M$ cuando no
les queda otra. Lo arregla MODI: esa ruta tiene un costo enorme y sale en la primera iteración que la
toque. El ejercicio 9.8 lo muestra.

---

## 9. Ejemplo resuelto · Agua del Itata

Una envasadora de agua purificada tiene tres plantas en Ñuble que despachan bidones de 20 litros a
cuatro sectores de reparto. Costo en pesos por bidón:

@@T:ej_dato@@

**Paso 1 · Balancear.** La oferta es 912 y la demanda 840: sobran 72 bidones. Se agrega un destino
ficticio con demanda 72 y costo 0 (los bidones que no salen de la planta).

@@T:ej_costos@@

**Paso 2 · Esquina noroeste.** Sin mirar costos, de arriba a la izquierda hacia abajo a la derecha:

@@T:ej_no@@

Usa $3 + 5 - 1 = 7$ celdas y cuesta **$388.848**.

**Paso 3 · Costo mínimo.** El ficticio cuesta 0 y se lleva la primera asignación:

@@T:ej_pcm@@

@@T:ej_cm@@

Cuesta **$339.240**. Fíjate en el paso 7: a Yungay le quedan 48 bidones y la única columna abierta es
Norte, su ruta más cara (\$662).

**Paso 4 · Vogel.** Penalizaciones en cada paso:

@@T:ej_pvo@@

@@T:ej_vo@@

Cuesta **$332.808**: mejor que los otros dos. En el paso 4, Yungay tiene una penalización de 176:
sin Oriente ni Poniente, le quedan Sur (\$486) y Norte (\$662), y si pierde Sur cada bidón le cuesta
\$176 más. Vogel le asigna Sur antes de que se pierda.

**Paso 5 · MODI desde la solución de costo mínimo.** En cada tabla, las celdas básicas van en negrita
con su envío; las vacías, con su costo reducido entre paréntesis.

@@T:ej_modi_cm@@

El óptimo cuesta **$325.704**. Desde Vogel también se llega en 2 iteraciones; desde la esquina
noroeste, en 4.

**Cómo se lee.**

- **El plan.** Coihueco abastece Norte (144) y Sur (168); Bulnes, Poniente (276) y el resto de Norte
  (72); Yungay, Oriente (180). Sobran 24 bidones en Bulnes y 48 en Yungay. Coihueco despacha todo.
- **Coihueco es la planta escasa.** Su potencial es 0 y el de las otras dos es 96: un bidón más en
  Coihueco ahorra \$96 (reemplaza un bidón que Bulnes manda a Norte a \$524 por uno de Coihueco a
  \$428).
- **Yungay–Sur tiene costo reducido +4.** Casi entra: si su flete bajara más de \$4 por bidón,
  convendría mandar desde Yungay a Sur.
- **Decisión.** Si hay que ampliar una planta, es Coihueco; ampliar Bulnes o Yungay no ahorra nada,
  porque ya les sobra.

---

## 10. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Aplicar los métodos sin balancear | suma ofertas y demandas antes de dibujar la tabla; si no calzan, agrega el ficticio |
| Origen ficticio con costo 0 cuando el enunciado da multas | la multa por unidad no entregada es el costo del ficticio en cada destino |
| Contar mal las básicas (o dejar la solución con menos de $m + n - 1$) | cuenta filas y columnas *con* el ficticio; si faltan, pon un cero básico que conecte sin formar ciclo |
| Calcular $u_i + v_j$ en celdas vacías al buscar potenciales | las ecuaciones $u_i + v_j = c_{ij}$ son solo de las básicas; en las vacías se *usa* el resultado |
| Ciclo que dobla en una celda vacía | el ciclo dobla solo en básicas; la única vacía es la que entra |
| Tomar $\theta$ como el menor envío del ciclo entero | $\theta$ es el menor de las celdas marcadas con $-$ |
| Leer $\bar c_{ij} = 0$ como «la ruta se usa» | significa que podría usarse sin cambiar el costo: hay otro óptimo |
| Variable sin sus tres piezas («$x$ = envío») | índice con rango, qué es el valor y el «en otro caso», y la naturaleza en una línea aparte |
| Familia de restricciones sin su «$\forall$» | cada restricción de oferta va con $\forall i \in O$; cada una de demanda, con $\forall j \in D$ |
| Suponer que Vogel ya es óptimo | compruébalo con MODI: en el ejemplo, Vogel quedó a \$7.104 del óptimo |

---

## 11. Práctica

Diez ejercicios: 9.1 a 9.4 básicos, 9.5 a 9.8 intermedios, 9.9 y 9.10 de desafío. Las pautas están
en la sección 12. Resuelve a mano con las reglas de desempate de la sección 5 (así tus tablas
coinciden con las de la pauta) y comprueba el óptimo con `modelos/u09_transporte.mod`.

**9.1 · Cemento a cuatro ferreterías (básico).** Tres bodegas reparten sacos de cemento a cuatro
ferreterías. Costo en pesos por saco:

@@T:e01_dato@@

(a) ¿Está balanceado? Si no, agrega lo que falte y di qué significa. (b) Escribe el modelo pieza por
pieza: variable con sus tres piezas, naturaleza, objetivo y cada familia con su «para todo».
(c) ¿Cuántas celdas básicas tiene una solución básica de la tabla balanceada? (d) Arma la solución
de esquina noroeste y calcula su costo.

**9.2 · Tomates de tres huertos (básico).** Tres huertos mandan cajones a tres ferias. Costo en pesos
por cajón:

@@T:e02_costos@@

Arma la solución inicial por costo mínimo y calcula su costo.

**9.3 · Los mismos tomates con Vogel (básico).** Con los datos de 9.2, arma la solución de Vogel
mostrando las penalizaciones de cada paso. ¿Cuánto mejora respecto de costo mínimo?

**9.4 · ¿Es óptima? (básico).** Toma la solución de costo mínimo de 9.2. (a) Calcula $u_i$, $v_j$ y los
costos reducidos. (b) ¿Es óptima? Si no, haz una iteración de MODI. (c) Comprueba el costo reducido
de la celda que entra con el cruce de piedras.

**9.5 · Áridos para cuatro obras (intermedio).** Tres plantas de áridos mandan camiones a cuatro obras.
Costo en miles de pesos por camión:

@@T:e05_costos@@

Parte de la esquina noroeste y aplica MODI hasta el óptimo. ¿Cuántas iteraciones necesitaste y
cuánto ahorra el óptimo respecto de la solución inicial?

**9.6 · Leña que no alcanza (intermedio).** Dos acopios reparten sacos de leña a tres sectores. Flete
en pesos por saco:

@@T:e06_dato@@

Cada saco que no se entrega tiene una multa (compra de emergencia): \$550 en S1, \$495 en S2 y \$660
en S3. (a) Balancea poniendo las multas como costo del ficticio. (b) Resuelve con Vogel y comprueba
con MODI. (c) ¿A qué sector le falta leña y por qué a ese y no al de la multa más baja en flete?
(d) Separa el costo total en flete y multas.

**9.7 · Una solución degenerada (intermedio).** Tres bodegas y tres tiendas; costo en miles de pesos
por pallet:

@@T:e07_costos@@

(a) Arma la esquina noroeste. ¿Qué pasa en el primer paso y dónde queda el cero básico? (b) Aplica
MODI hasta el óptimo. ¿En qué iteración el costo no baja y por qué? (c) ¿Llegan al mismo óptimo
costo mínimo y Vogel?

**9.8 · Una ruta prohibida (intermedio).** Tres plantas y cuatro clientes; costo en miles de pesos por
tonelada. La planta P2 no puede abastecer a C4 (el puente no resiste su camión):

@@T:e08_costos@@

(a) Arma costo mínimo y Vogel con $M = 100.000$ en la ruta prohibida. ¿Qué le pasa a costo mínimo?
(b) Comprueba con MODI que Vogel es óptimo. (c) El cliente C3 pide que al menos 15 toneladas le
lleguen desde P1 (quiere un segundo proveedor). ¿Cuánto sube el costo? ¿Hasta cuántas toneladas por
esa ruta vale esa cuenta?

**9.9 · Fruta para tres plantas (desafío).** Tres huertos venden fruta a tres plantas procesadoras.
Cada planta compra exactamente lo que pide; lo que un huerto no vende se queda en el huerto.
Ganancia en miles de pesos por tonelada (Huerto 3 no tiene contrato con Planta A):

@@T:e09_g@@

(a) Balancea y resuelve con Vogel y MODI, maximizando la ganancia. (b) ¿Qué huerto se queda con
fruta y cuánta? (c) ¿Cuánto vale una tonelada más en cada huerto? Ajusta los potenciales para que el
ficticio valga 0 y explica por qué ese ajuste es legítimo. (d) Compruébalo con
`modelos/u09_e09_ganancia.mod`.

**9.10 · Dos planes que cuestan lo mismo (desafío).** Tres molinos mandan harina a cuatro
distribuidoras; costo en miles de pesos por tonelada:

@@T:e10_costos@@

(a) Resuelve con Vogel y MODI. (b) La tabla final tiene un costo reducido 0: encuentra el otro plan
óptimo con su ciclo. (c) ¿Qué pasa con cada plan si el costo de esa ruta sube \$1.000 por tonelada?
¿Y si baja \$1.000? Cuantifica el cambio de costo.

---

## 12. Pautas

**9.1.** (a) Oferta 426, demanda 462: faltan 36 sacos. Se agrega un origen ficticio con 36 sacos y
costo 0; lo que «manda» a una ferretería es demanda que queda sin atender.

@@T:e01_costos@@

(b) Conjuntos $O$ = {Hualqui, Penco, Tomé, Ficticio}, $D$ = {F1, …, F4}. Variable: $x_{ij}$, $i \in O$,
$j \in D$, sacos enviados de la bodega $i$ a la ferretería $j$ en la semana, 0 si no se usa la ruta;
$x_{ij} \in \mathbb{Z}_0^+$. $\min \sum_{i}\sum_{j} c_{ij} x_{ij}$ s.a.
$\sum_{j \in D} x_{ij} = a_i \;\; \forall i \in O$ y $\sum_{i \in O} x_{ij} = b_j \;\; \forall j \in D$
(con el ficticio, todas son igualdades). (c) $4 + 4 - 1$: 7 variables básicas. (d) Esquina noroeste:

@@T:e01_no@@

Cuesta **$232.980** (el ficticio aporta 0). El óptimo es **$209.418**: la esquina noroeste no mira
costos y queda un 11 % arriba.

**9.2.** Costo mínimo, paso a paso:

@@T:e02_pcm@@

@@T:e02_cm@@

Costo **$92.345**. La ruta más barata de H1 (Coelemu, \$418) se usó bien, pero a Chillán le tocó
recibir de H2 a \$605.

**9.3.** Vogel:

@@T:e02_pvo@@

@@T:e02_vo@@

Costo **$91.685**: \$660 menos que costo mínimo. Vogel atendió primero a San Carlos (penalización 198:
perder H2 costaba eso por cajón) y a H3 (231).

**9.4.** (a) y (b), con la solución de costo mínimo:

@@T:e02_modi_cm@@

H2–Coelemu tenía costo reducido −44: cada cajón por ahí ahorra \$44. Entran 15 y el costo baja \$660,
justo lo que separaba a costo mínimo de Vogel: el óptimo es la solución de Vogel. (c) Cruce de piedras
para H2–Coelemu: $+517 - 418 + 462 - 605 = -44$. Es el mismo número.

**9.5.**

@@T:e05_no@@

@@T:e05_modi_no@@

Dos iteraciones. El óptimo cuesta **4.686** miles de pesos contra 5.621 de la esquina noroeste: un
ahorro de 935 mil pesos por semana. La segunda iteración usa un ciclo de seis celdas: los ciclos no
siempre son rectángulos.

**9.6.** (a) Oferta 231, demanda 297: faltan 66 sacos. El ficticio ofrece 66 con las multas como costo:

@@T:e06_costos@@

(b) Vogel:

@@T:e06_pvo@@

@@T:e06_vo@@

@@T:e06_modi_vo@@

Vogel ya es óptimo: **$107.811**. (c) A S2 le faltan **66 sacos sin entregar**. No es por su flete
(S2 tiene el flete más barato desde A), sino porque su multa es la más baja (\$495): dejar sin leña a
S2 cuesta menos que dejar sin leña a S1 o S3. (d) Multas $66 \cdot 495 =$ **$32.670**; flete
**$75.141**.

**9.7.** (a) En el primer paso B1–T1 recibe 110 y se agotan a la vez B1 y T1. Se tacha la fila B1 y T1
queda con demanda 0: el paso 2 manda 0 por B2–T1, el cero básico.

@@T:e07_pno@@

@@T:e07_no@@

Costo 3.168. (b) MODI:

@@T:e07_modi_no@@

En la iteración 0 el ciclo pasa por el cero básico, que está marcado con $-$: $\theta = 0$ y el costo
no baja, pero la base cambia (B3–T1 entra con 0) y desde ahí MODI avanza. El óptimo es **1.958**
miles de pesos. (c) Sí: costo mínimo y Vogel llegan directo a 1.958, sin degeneración.

**9.8.** (a) Costo mínimo:

@@T:e08_cm@@

Cuesta 2.007.205: al final solo le quedaba la columna C4, y P2 tuvo que mandar 20 por la ruta
prohibida. Vogel no cae ahí:

@@T:e08_vo@@

(b) MODI sobre Vogel:

@@T:e08_modi_vo@@

Óptimo **7.985** miles de pesos (la ruta prohibida se muestra con «—»). Desde costo mínimo, MODI saca
la ruta $M$ en la primera iteración y llega al mismo óptimo en dos. (c) P1–C3 tiene costo reducido
15: cada tonelada forzada por ahí sube el costo 15 mil pesos. Con 15 toneladas, sube 225 y el costo
queda en 8.210. La cuenta vale mientras el ciclo de P1–C3 (P1–C3, P2–C3, P2–C1, P1–C1) pueda
absorberlo: hasta $\theta =$ 20 unidades, el menor envío de sus celdas $-$. Más allá cambia la base
y cada tonelada adicional cuesta más.

**9.9.** (a) Oferta 240, pedidos 215: sobran 25 toneladas, destino ficticio con ganancia 0. Con
costo $= -$ganancia, Vogel da:

@@T:e09_vo@@

Ganancia 13.145 (la esquina noroeste daba 13.065). MODI, mostrado en ganancias (entra la ganancia
reducida más positiva):

@@T:e09_modi_vo@@

Ganancia máxima **13.485** miles de pesos. (b) Huerto 3 se queda con 25 toneladas: es el de menor
ganancia por tonelada. (c) Los potenciales están definidos salvo una constante: sumar $k$ a todos
los $u_i$ y restarlo a todos los $v_j$ no cambia ninguna suma $u_i + v_j$. Se elige $k$ para que el
ficticio valga 0 (una tonelada más de pedido «ficticio» no gana nada): $k = 13$ da
$u = (13, 21, 0)$ y $v = (57, 49, 47)$. Una tonelada más en Huerto 1 vale 13 mil pesos; en Huerto 2,
21 mil; en Huerto 3, nada (ya le sobra). Una tonelada más pedida por Planta A vale 57 mil, por B 49 y
por C 47. (d) OPL entrega exactamente esos duales: `dual_oferta` 13, 21 y 0; `dual_pedido` 57, 49 y
47.

**9.10.** (a) Vogel y MODI:

@@T:e10_vo@@

@@T:e10_modi_vo@@

Óptimo **20.878** miles de pesos. (b) Q1–D4 tiene costo reducido 0. Su ciclo es Q1–D4 (+), Q3–D4 (−),
Q3–D3 (+), Q2–D3 (−), Q2–D1 (+), Q1–D1 (−); $\theta =$ 33 (lo que lleva Q1–D1). El otro plan óptimo:

@@T:e10_alt@@

Cuesta lo mismo. Cualquier mezcla de los dos también es óptima. (c) Si Q1–D4 sube \$1.000, el plan
de MODI sigue óptimo con el mismo costo (no la usa) y el alternativo deja de serlo. Si baja \$1.000, el
alternativo pasa a ser el único óptimo y el costo baja $33 \times 1 = 33$ miles de pesos: lo que pasa
por esa ruta por lo que bajó.

---

## 13. Caso integrador · Estampa Sur abre un segundo taller

> Este caso sigue a Estampa Sur por todo el ramo. En la unidad 8 se calculó la ruta más corta del
> taller a cada tienda. Ahora Estampa Sur abrió un segundo taller en Cruce y debe repartir la
> producción semanal de los dos entre sus cuatro tiendas grandes.

**Los datos.** El taller ofrece 320 cajas por semana y el de Cruce 216; Centro pide 156, Lagos 118,
Valle 138 y Costa 124. Oferta y demanda suman 536: está balanceado. El flete cuesta \$95 por km de la
ruta más corta (unidad 8): del taller, 7, 21, 20 y 16 km; de Cruce, 6, 13, 9 y 23 km. Costo por caja:

@@T:caso_costos@@

En OPL, el mismo `.mod` de la sección 2 con estos datos (`modelos/u09_estampa.dat`):

```opl
@@OPL:u09_estampa.dat@@
```

**Esquina noroeste.**

@@T:caso_pno@@

@@T:caso_no@@

Costo **$776.150**.

**Costo mínimo.**

@@T:caso_pcm@@

@@T:caso_cm@@

Costo **$712.310**.

**Vogel.**

@@T:caso_pvo@@

@@T:caso_vo@@

Costo **$586.340**. Vogel atendió primero a Valle (penalización 1.045: si no se abastece desde Cruce,
cada caja cuesta \$1.045 más) y después al taller y a Cruce.

**MODI desde la esquina noroeste.**

@@T:caso_modi_no@@

En 2 iteraciones MODI llega al mismo plan que Vogel. Desde costo mínimo también son 2 iteraciones, y
desde Vogel, ninguna: Vogel ya era óptimo.

![Red de transporte del caso: los dos talleres y las cuatro tiendas, con los envíos óptimos](figuras/u09_red_transporte.svg)

**La salida de OPL** confirma el plan y trae los potenciales de MODI como duales:

```text
@@SALIDA@@
```

| Pregunta | Respuesta |
|---|---|
| ¿Qué manda cada taller? | el taller: 156 cajas a Centro, 40 a Lagos y 124 a Costa; Cruce: 78 a Lagos y 138 a Valle |
| ¿Cuánto cuesta? | **$586.340** por semana |
| ¿Hay otro plan igual de barato? | no: todos los costos reducidos son positivos |
| ¿Qué ruta vacía está más cerca de entrar? | taller–Valle, con +285: tendría que bajar \$285 por caja |
| ¿Cuánto vale una caja más de capacidad en Cruce? | \$760: el dual de su oferta es −760 (en un mínimo, más capacidad baja el costo) |
| ¿Por qué Lagos recibe de los dos? | Cruce no alcanza para Lagos y Valle completos; Lagos es la tienda que reparte la diferencia |

**La cadena.** El verificador exige que los costos, los envíos y el total ($586.340) coincidan con el
script del caso (`CADENA: OK`), y que OPL, scipy y MODI den lo mismo.

**Lo que pasa a la unidad siguiente.** Si cada taller mandara una sola caja y cada tienda pidiera una,
el transporte sería una asignación: la unidad 10 decide qué operario va a cada máquina con un método
hecho para ese caso extremo.

---

## 14. Para seguir

**En los libros del ramo.**

- Winston, *Investigación de operaciones: aplicaciones y algoritmos* (4.ª ed., 2005): su capítulo de
  transporte, asignación y transbordo desarrolla los tres métodos de partida, MODI y el cruce de
  piedras con muchos ejercicios.
- Hillier y Lieberman, *Introducción a la investigación de operaciones* (7.ª ed., 2001): su capítulo
  sobre el problema de transporte y asignación presenta el simplex de transporte con la misma
  notación $u_i$, $v_j$.

**Abierto y gratis.**

- Bradley, Hax y Magnanti, *Applied Mathematical Programming* (MIT), capítulo 8 «Network Models», en
  inglés: el transporte y la asignación como redes, con la propiedad de soluciones enteras.
  https://web.mit.edu/15.053/www/AMP-Chapter-08.pdf

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un transporte de 3 × 4 desbalanceado con
multas por demanda no atendida; yo lo resuelvo con Vogel y MODI y tú me corriges cada tabla».
