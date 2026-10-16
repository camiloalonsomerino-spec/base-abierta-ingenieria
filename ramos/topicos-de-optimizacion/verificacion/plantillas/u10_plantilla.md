---
ramo: Tópicos de Optimización
unidad: 10
titulo: Asignación y método húngaro
version: 0.1 (16-10-2026)
requiere: [02-binarias-decisiones-y-mochila, 09-transporte]
alimenta: [11-heuristicas]
verificacion: verificacion/u10_asignacion.py
---

# Unidad 10 · Asignación y método húngaro

**Qué vas a poder hacer.** Plantear una asignación como modelo binario y como transporte, resolverla a
mano con el método húngaro (reducir filas y columnas, cubrir los ceros con el mínimo de líneas,
ajustar), adaptarla cuando no es cuadrada, cuando se maximiza o cuando hay pares prohibidos, y usarla
como cota inferior de un vendedor viajero.

**Lo que necesitas antes.** La unidad 2 (el modelo de asignación con variables binarias) y la unidad 9
(transporte, potenciales $u_i$ y $v_j$, degeneración). De Gestión de Operaciones basta la idea de
asignar trabajos a máquinas en la programación de corto plazo: acá se ve por qué el método funciona y
qué hacer cuando el problema no viene cuadrado.

**Tiempo.** Unas 5 horas: 1,5 de lectura con el ejemplo y 3,5 de práctica a mano.

---

## 1. La idea: el transporte más extremo

Hay $n$ personas y $n$ tareas, y un costo (o un tiempo) $c_{ij}$ por cada par. Cada persona hace una
tarea y cada tarea la hace una persona. Es un transporte en que todas las ofertas y demandas valen 1.

Ese caso extremo tiene un problema para MODI: una solución básica tiene $2n - 1$ celdas básicas, pero
solo $n$ envíos positivos (cada persona hace una sola tarea). Las otras $n - 1$ son **ceros básicos**:
la asignación es la solución más degenerada que existe, y MODI daría muchos pasos con $\theta = 0$. El
método húngaro (Kuhn, 1955, sobre ideas de König y Egerváry) evita ese problema: no recorre
soluciones básicas, sino que **transforma la matriz de costos** hasta que la asignación óptima se ve
a simple vista.

---

## 2. El modelo, pieza por pieza

**Conjuntos.** $P$ personas, $T$ tareas.

**Parámetro.** $c_{pt}$ costo (o minutos) de que la persona $p$ haga la tarea $t$.

**Variable de decisión**, con sus tres piezas y su naturaleza:

- índice con su rango: $x_{pt}$, con $p \in P$, $t \in T$;
- qué significa el 1: la persona $p$ hace la tarea $t$;
- el «en otro caso»: 0 si no la hace;
- naturaleza: $x_{pt} \in \{0, 1\}$.

**Objetivo y restricciones:**

$$\min \sum_{p \in P}\sum_{t \in T} c_{pt}\,x_{pt} \qquad \text{s.a.} \qquad \sum_{t \in T} x_{pt} = 1 \;\; \forall p \in P, \qquad \sum_{p \in P} x_{pt} = 1 \;\; \forall t \in T$$

Las dos familias hacen falta. Con solo la de personas, el modelo manda a todos a su tarea más barata
aunque sea la misma; con solo la de tareas, una persona hace varias. Como en el transporte, la
relajación lineal ya entrega ceros y unos: la asignación sale binaria aunque se declare continua.

En OPL (`modelos/u10_asignacion.mod`) el modelo se escribe un poco más general, para que el mismo
`.mod` sirva en todas las variantes de esta unidad: cada persona toma entre `minTareas` y `maxTareas`
tareas, cada tarea se hace a lo más una vez y, si es obligatoria, al menos una:

```opl
@@OPL:u10_asignacion.mod@@
```

Con `minTareas = maxTareas = 1` y todas las tareas obligatorias es exactamente el modelo de arriba.
Como las variables son `boolean`, OPL no entrega duales.

---

## 3. Por qué se puede restar

Toda asignación usa **exactamente un** número de cada fila y **exactamente uno** de cada columna. Si a
una fila entera se le resta una constante $k$, *todas* las asignaciones bajan $k$: su orden no cambia
y la mejor sigue siendo la mejor. Lo mismo con una columna. El método se apoya en eso:

1. Se resta lo más posible sin dejar números negativos: el mínimo de cada fila, después el de cada
   columna. Aparecen ceros.
2. Si se puede asignar a cada persona un cero, en filas y columnas distintas (**ceros
   independientes**), esa asignación cuesta 0 en la matriz transformada, y como nada es negativo, es
   la mejor. En la matriz original cuesta exactamente lo que se restó.

**Lo restado es una cota inferior.** Cada resta a una fila es un $u_i$ y cada resta a una columna es un
$v_j$, como los potenciales de MODI: la suma de lo restado es una solución dual y nunca supera el
costo de una asignación. El método va subiendo esa cota hasta que alcanza a una asignación: ahí
ambas coinciden y la asignación es óptima. Las tablas de esta unidad anotan la **cota** en cada paso
para que lo veas.

---

## 4. El método húngaro paso a paso

1. **Reducir filas.** A cada fila réstale su mínimo.
2. **Reducir columnas.** A cada columna réstale su mínimo (en la matriz ya reducida por filas).
3. **Cubrir los ceros con el menor número de líneas** (filas o columnas completas). El menor número de
   líneas es igual al mayor número de ceros independientes (teorema de König). Si se necesitan $n$
   líneas, hay una asignación óptima entre los ceros: termina.
4. **Ajustar.** Si hay menos de $n$ líneas, toma $\delta$ = el menor número **sin cubrir**. Réstalo a
   todos los no cubiertos y súmalo a los que están en el **cruce** de dos líneas; los cubiertos por
   una sola línea no cambian. Vuelve al paso 3.

**Cómo encontrar el mínimo de líneas sin adivinar.** A simple vista se suele trazar una línea de más.
El procedimiento seguro tiene dos partes:

- *Asigna* el mayor número de ceros independientes que puedas (empieza por las filas o columnas que
  tienen un solo cero).
- *Marca*: (a) las filas sin asignación; (b) las columnas que tienen un cero en una fila marcada;
  (c) las filas que tienen su cero asignado en una columna marcada. Repite (b) y (c) hasta que no
  cambie nada. Las líneas son las **filas no marcadas** y las **columnas marcadas**.

Las tablas de esta unidad usan exactamente ese procedimiento: las columnas cubiertas llevan ▼ en el
encabezado y las filas cubiertas, ◀ al final. Otra cobertura con el mismo número de líneas puede dar
tablas intermedias distintas, pero el mismo óptimo.

**Por qué el ajuste sube la cota.** Restar $\delta$ a las filas no cubiertas y sumarlo a las columnas
cubiertas es lo que hace el paso 4 (los cruces reciben $+\delta$ porque están en una columna cubierta
y en una fila cubierta, que no se restó). La cota sube $\delta \cdot (n - \text{líneas})$. Como hay
menos de $n$ líneas, siempre sube: el método no se queda dando vueltas.

**Cuándo NO aplica.** Si una persona puede tomar varias tareas *con un tope de horas* (no de cantidad),
si importa el **tiempo máximo** en vez de la suma (que el último termine pronto), o si hay condiciones
entre pares («Ana y Bruno no en el mismo turno»), ya no es una asignación: es un modelo binario para
OPL (unidad 2) o una programación de operaciones.

---

## 5. Variantes

| Situación | Qué se hace |
|---|---|
| Más tareas que personas | se agregan personas ficticias con costo 0: la tarea que les toca queda sin hacer |
| Más personas que tareas | se agregan tareas ficticias con costo 0: la persona que la recibe queda libre |
| Maximizar (ventas, puntaje) | se usa el costo de oportunidad: (mayor valor de la matriz) $-$ valor, y se minimiza; o se multiplica por $-1$ |
| Par prohibido | costo $M$ muy grande; en OPL, `x[p][t] == 0` |
| Una persona puede hacer hasta $k$ tareas | se repite su fila $k$ veces (y se completa con ficticios hasta que la matriz sea cuadrada); en OPL, `maxTareas` |
| Vendedor viajero | la asignación con $c_{ii} = M$ es su relajación: da una cota inferior, pero puede formar subciclos (ejercicio 10.10) |

---

## 6. Ejemplo resuelto · Cinco repartos a la misma hora

Una botillería de barrio tiene cinco repartidores y, a las 21:00, cinco pedidos. Minutos que tardaría
cada repartidor en entregar cada pedido (según dónde está y en qué se mueve):

@@T:ej_datos@@

Se busca la asignación que minimiza el total de minutos.

@@T:ej_hungaro@@

**Cómo se lee el paso de las líneas.** Después de reducir, Rocío e Ignacia tienen su único cero en la
misma columna (P2): no pueden quedarse las dos con P2. Por eso no alcanzan 5 ceros independientes y
el método ajusta. El menor sin cubrir (2) está en la fila de Ignacia: al restarlo aparece un cero en
Ignacia–P5, que destraba el problema.

**La cota.** Lo restado por filas (116) y por columnas (17) suma 133; el ajuste suma $2 \cdot (5 - 4) = 2$
y la cota llega a 135, que es el total de la asignación. Nadie puede hacerlo en menos.

**Decisión.** Rocío lleva P2, Matías P1, Javiera P4, Tomás P3 e Ignacia P5: 135 minutos de reparto en
total. Mandar a cada repartidor a su pedido más cercano no sirve: Rocío e Ignacia irían las dos a P2.

---

## 7. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Reducir solo filas | después de las filas, reduce las columnas; si no, se trabaja con una cota más baja y se ajusta de más |
| Trazar más líneas de las necesarias y concluir que no hay asignación | usa el marcado de la sección 4: da siempre el mínimo |
| Contar ceros en vez de ceros independientes | dos ceros en la misma fila o columna valen por uno |
| Restar $\delta$ también a los cubiertos, o no sumarlo en los cruces | no cubiertos: $-\delta$; cruces: $+\delta$; cubiertos por una línea: igual |
| Leer el total en la matriz reducida | el total se suma con los costos **originales** de los pares elegidos (o con la cota final) |
| Maximizar con el húngaro sin transformar | pasa a costo de oportunidad (mayor valor $-$ valor) antes de reducir |
| Matriz no cuadrada | agrega filas o columnas ficticias con costo 0 hasta que lo sea |
| Escribir solo una de las dos familias de restricciones | una por persona ($\forall p$) y una por tarea ($\forall t$) |
| Variable sin sus tres piezas | índice con rango, qué es el 1 y el «en otro caso»; $x_{pt} \in \{0,1\}$ en su propia línea |
| Dar por óptima una asignación sin comprobarla | compara con la cota (lo restado) o, si $n \le 5$, con todas las permutaciones: con $n = 4$ son 24 |

---

## 8. Práctica

Diez ejercicios: 10.1 a 10.4 básicos, 10.5 a 10.8 intermedios, 10.9 y 10.10 de desafío. Las pautas
están en la sección 9. Para que tus tablas coincidan con las de la pauta, cubre los ceros con el
marcado de la sección 4.

**10.1 · Tres garzones (básico).** Un restorán asigna tres garzones a tres sectores. Minutos promedio de
espera de las mesas según quién atiende cada sector:

@@T:e01_datos@@

(a) Escribe el modelo pieza por pieza. (b) Enumera las seis asignaciones posibles y elige la mejor.

**10.2 · Cuatro trabajos (básico).** Costos en miles de pesos:

@@T:e02_datos@@

Reduce filas y columnas. ¿Ya hay cuatro ceros independientes? ¿Cuál es la asignación y su costo?

**10.3 · Cuatro grúas (básico).** Una constructora asigna cuatro grúas a cuatro obras; costo de
traslado y montaje en miles de pesos:

@@T:e03_datos@@

Reduce filas y columnas y cubre los ceros con el menor número de líneas. ¿Cuántas líneas? ¿Es
óptima?

**10.4 · El ajuste (básico).** Sigue con 10.3: haz el ajuste, encuentra la asignación y comprueba que
su costo es igual a la cota (lo restado en total).

**10.5 · Cinco trabajos (intermedio).** Costo en miles de pesos:

@@T:e05_datos@@

Resuelve con el método húngaro. ¿Cuántos ajustes necesitaste? Anota la cota en cada paso.

**10.6 · Tres personas, cuatro tareas (intermedio).** En una tienda, tres personas cubren el cierre;
hay cuatro tareas y una puede quedar para mañana. Minutos:

@@T:e06_dato@@

(a) Completa la matriz y resuelve. (b) ¿Qué tarea queda sin hacer? (c) En OPL, ¿qué parámetro del
`.mod` reemplaza a la fila ficticia?

**10.7 · Vendedores y zonas (intermedio).** Ventas semanales esperadas, en miles de pesos, de cada
vendedor en cada zona. Se busca **maximizar** la venta total:

@@T:e07_g@@

(a) Transforma a costo de oportunidad y resuelve. (b) ¿Cuánto venden en total?

**10.8 · Turnos de lavandería (intermedio).** Cuatro turnos se reparten cuatro procesos; minutos por
carga. El turno 1 no puede secar (la secadora está en mantención a esa hora) y el turno 3 no puede
doblar (no hay mesa); en la tabla, «M»:

@@T:e08_dato@@

(a) Resuelve con $M$ en los pares prohibidos. (b) ¿Cuánto costaría la asignación si no hubiera
prohibiciones, y qué pares usaría? (c) Compruébalo con `u10_e08_prohibidos.dat`.

**10.9 · Hasta dos trabajos por técnico (desafío).** Tres técnicos y cinco trabajos de mantención.
Cada técnico puede tomar hasta dos; todos los trabajos se hacen. Horas:

@@T:e09_dato@@

(a) Arma la matriz cuadrada (filas repetidas y lo que falte) y resuelve. (b) ¿Qué hace cada técnico?
(c) Compruébalo con `u10_e09_dos_tareas.dat`, que usa `maxTareas` en vez de repetir filas.

**10.10 · La asignación como cota del vendedor viajero (desafío).** Un técnico visita cinco puntos
(A a E) y vuelve al inicio. Distancias en km (simétricas):

@@T:e10_dato@@

(a) Resuelve la asignación con $M$ en la diagonal (de un punto no se va a sí mismo). (b) Dibuja los
arcos elegidos: ¿forman una ruta? (c) La mejor ruta mide 58 km. ¿Qué tan lejos queda la cota de la
asignación? (d) ¿Qué restricción del vendedor viajero (unidad 4) le falta al modelo de asignación?

---

## 9. Pautas

**10.1.** (a) $x_{gs}$, con $g$ en los tres garzones y $s$ en los tres sectores: 1 si el garzón $g$
atiende el sector $s$, 0 en otro caso; $x_{gs} \in \{0,1\}$.
$\min \sum_g\sum_s c_{gs} x_{gs}$ s.a. $\sum_s x_{gs} = 1 \;\; \forall g$ y $\sum_g x_{gs} = 1 \;\; \forall s$.
(b) Las seis asignaciones:

@@T:e01_todas@@

La mejor: Garzón 1 en el salón, Garzón 2 en la terraza y Garzón 3 en la barra, **92** minutos. El Garzón 2 va
a la terraza, donde es el más rápido de los tres (20), y el Garzón 3 a la barra, su mejor sector
(24). Al Garzón 1 le queda el salón: su mejor sector, la terraza, ya está tomado.

**10.2.**

@@T:e02_hungaro@@

Basta con reducir: los cuatro ceros independientes aparecen sin ajustar. Costo **68** miles de pesos.

**10.3 y 10.4.**

@@T:e03_hungaro@@

Con 3 líneas no es óptima. El ajuste ($\delta = 5$) sube la cota de 178 a 183, que es el costo de la
asignación: **183** miles de pesos.

**10.5.**

@@T:e05_hungaro@@

Dos ajustes; la cota termina en **249**, igual al costo de la asignación.

**10.6.** (a) Se agrega una persona ficticia con 0 en todas las tareas:

@@T:e06_hungaro@@

(b) A la ficticia le toca la **Caja**: esa tarea queda para mañana. Total **111** minutos. (c) En OPL
no hace falta la fila ficticia: basta con `obligatoria = [0 0 0 0]`, que deja cada tarea con
«a lo más una persona».

**10.7.** (a) El mayor valor es 207. Costo de oportunidad $= 207 -$ venta:

@@T:e07_hungaro@@

(b) V1 a Costa (197), V2 a Centro (167), V3 a Norte (207) y V4 a Sur (117): **688** miles de pesos por
semana. Comprobación: $4 \cdot 207 - 140 = 688$.

**10.8.** (a)

@@T:e08_hungaro@@

Total **89** minutos. (b) Sin prohibiciones el óptimo sería 41 minutos, pero usaría justo los dos pares
prohibidos (Turno 1–Secado y Turno 3–Doblado): la mantención y la falta de mesa cuestan 48 minutos por
ronda. (c) OPL da el mismo total con `Prohibidos = {<"Turno 1", "Secado">, <"Turno 3", "Doblado">}`.

**10.9.** (a) Cada técnico aparece dos veces (seis filas) y se agrega un trabajo ficticio de 0 horas
(seis columnas): el técnico que lo recibe hace solo un trabajo.

@@T:e09_hungaro@@

(b) Hugo: K1, K5; Inés: K2; Julio: K3, K4. Total **122** horas. Inés toma un solo trabajo. (c) OPL,
con `maxTareas = [2 2 2]`, da lo mismo sin repetir filas.

**10.10.** (a)

@@T:e10_hungaro@@

(b) Los arcos son A→C→E→A y B→D→B: **dos subciclos**, no una ruta. (c) La asignación da 51 km y la
ruta óptima 58 km: la cota queda un 12 % abajo. Sirve como cota inferior en una ramificación y
acotamiento (unidad 5). (d) Falta la eliminación de subciclos: que todo subconjunto de puntos tenga
al menos un arco que salga de él. Con ella, el modelo ya no es una asignación y no sale binario solo.

---

## 10. Caso integrador · Qué operario va a cada máquina

> Este caso sigue a Estampa Sur por todo el ramo. En la unidad 9 se repartieron las cajas entre los dos
> talleres y las tiendas. Ahora, dentro del taller, hay que decidir qué operario trabaja en cada
> máquina durante el próximo pedido grande.

**Los datos.** Cuatro operarios y cuatro máquinas (dos pulpos de serigrafía, de 6 y de 4 brazos, la
prensa térmica y la bordadora). Minutos que tarda cada operario en un lote en cada máquina:

@@T:caso_datos@@

En OPL (`modelos/u10_estampa.dat`, sin tildes en los nombres):

```opl
@@OPL:u10_estampa.dat@@
```

**El método húngaro.**

@@T:caso_hungaro@@

Se necesitaron 2 ajustes. La cota pasó de 140 (lo restado por filas y columnas) a 144 y a 149, el
total de la asignación.

![Asignación óptima del caso: cada operario unido a su máquina, con los minutos por lote](figuras/u10_asignacion_caso.svg)

**La salida de OPL:**

```text
@@SALIDA@@
```

| Pregunta | Respuesta |
|---|---|
| ¿Quién va a cada máquina? | Ana al pulpo de 6 brazos, Bruno al de 4, Daniela a la bordadora y Esteban a la térmica |
| ¿Cuánto suman? | **149 minutos** por ronda de lotes (un lote en cada máquina) |
| ¿Hay otra asignación igual de buena? | no: es la única de 149 entre las 24 posibles |
| ¿Por qué Ana no va a la térmica, si es su máquina más rápida? | ahí le ganaría a Esteban por 2 minutos (29 contra 31); en el pulpo de 6 brazos le gana por 8 (38 contra 46), y Esteban no tiene otra máquina donde rinda tanto |
| ¿Qué pasa si se manda a cada uno a su máquina más rápida? | tres de los cuatro (Ana, Bruno y Esteban) querrían la térmica: no es una asignación |

**La cadena.** El verificador exige que el total (149 minutos) y la asignación coincidan con el script
del caso (`CADENA: OK`), con la fuerza bruta de las 24 asignaciones y con OPL.

**Lo que pasa a la unidad siguiente.** La asignación se resolvió exacta porque es un problema
«fácil»: la relajación lineal ya es binaria. La ruta del camión que visita las seis tiendas no lo es
(el ejercicio 10.10 muestra por qué); la unidad 11 la ataca con heurísticas.

---

## 11. Para seguir

**En los libros del ramo.**

- Winston, *Investigación de operaciones: aplicaciones y algoritmos* (4.ª ed., 2005): su capítulo de
  transporte, asignación y transbordo trae el método húngaro con la versión de maximización y los
  casos no cuadrados.
- Hillier y Lieberman, *Introducción a la investigación de operaciones* (7.ª ed., 2001): el capítulo
  de transporte y asignación presenta el húngaro como un caso del simplex de transporte.

**Abierto y gratis.**

- Bradley, Hax y Magnanti, *Applied Mathematical Programming* (MIT), capítulo 8 «Network Models», en
  inglés: la asignación como red y por qué su solución lineal es entera.
  https://web.mit.edu/15.053/www/AMP-Chapter-08.pdf

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame una matriz de 5 × 4 para maximizar, con un
par prohibido; yo la resuelvo con el húngaro y tú revisas mis líneas en cada paso».
