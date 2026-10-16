---
ramo: Gestión de Operaciones
unidad: 10
titulo: Programación de operaciones
version: 0.1 (piloto, 15-10-2026)
requiere: [07-programa-maestro, 09-capacidad-aproximada]
alimenta: [11-fisica-de-la-fabrica]
verificacion: verificacion/u10_programacion.py
---

# Unidad 10 · Programación de operaciones

**Qué vas a poder hacer.** Ordenar los trabajos que compiten por una máquina y medir qué costó ese
orden; secuenciar un taller de dos máquinas con la regla de Johnson; extender la idea a tres o más
máquinas y a rutas distintas; asignar personas a tareas al menor costo, y leer un control de
entradas y salidas para saber si un centro de trabajo se está atorando.

**Lo que necesitas antes.** El programa maestro y el MRP (unidades 7 y 8): de ahí salen las órdenes
que esta unidad ordena. Basta con saber que esos planes liberan órdenes con una cantidad y una fecha.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. La idea

El MRP dice **qué** fabricar y **para cuándo**. No dice en qué orden pasa cada orden por cada
máquina. Ese es el trabajo de la programación de corto plazo, que tiene tres fases:

1. **Revisar y liberar el pedido.** Se comprueba que haya material y capacidad; recién entonces la
   orden queda «en curso».
2. **Programar.** Primero se *carga* (qué centro de trabajo hace cada orden), luego se *secuencia*
   (en qué orden las atiende) y al final se fija la hora de inicio y fin de cada operación.
3. **Controlar.** Se compara lo real con lo programado y se corrige.

Ordenar es elegir qué se sacrifica. No existe una secuencia que gane en todo; los cuatro criterios
habituales tiran para lados distintos:

| Criterio | Pregunta que responde |
|---|---|
| Tiempo de flujo | ¿Cuánto espera, en promedio, un trabajo desde que llega hasta que sale? |
| Utilización | ¿Qué fracción del tiempo la máquina está trabajando y no esperando? |
| Trabajos en el sistema | ¿Cuánto trabajo en proceso (WIP) se acumula en el taller? |
| Atraso | ¿Cuánto llegan tarde los pedidos respecto de lo prometido? |

### Hacia adelante y hacia atrás

- **Hacia adelante:** cada trabajo empieza apenas se puede. El programa siempre es factible, pero
  puede terminar después de la fecha prometida y acumula WIP.
- **Hacia atrás:** se parte de la fecha de entrega y se programa primero la última operación. Cumple
  la fecha si alcanza la capacidad, pero puede pedir recursos que no hay. El MRP es un ejemplo de
  programación hacia atrás con capacidad infinita: por eso después hace falta revisar la capacidad
  (unidad 9).

---

## 2. Una máquina, varios trabajos

### Notación

Para cada trabajo $j$: $p_j$ tiempo de proceso, $d_j$ fecha de entrega. Si los trabajos se
procesan uno tras otro desde el tiempo 0, el **tiempo de flujo** (o de terminación) del trabajo en la
posición $k$ es la suma de los tiempos de proceso hasta él:

$$F_{[k]} = \sum_{i=1}^{k} p_{[i]}$$

El **atraso** nunca es negativo: un trabajo que termina antes no «devuelve» días.

$$T_j = \max(0,\; F_j - d_j)$$

Los cuatro indicadores, con $n$ trabajos:

$$\bar F = \frac{\sum F_j}{n} \qquad U = \frac{\sum p_j}{\sum F_j} \qquad \bar N = \frac{\sum F_j}{\sum p_j} \qquad \bar T = \frac{\sum T_j}{n}$$

$U$ y $\bar N$ son inversos: si la máquina pasa más tiempo trabajando por cada día que los
trabajos esperan, hay menos trabajos acumulados.

### Las reglas de prioridad

| Regla | Qué atiende primero | Qué optimiza |
|---|---|---|
| **FCFS** | el que llegó primero | nada en particular; el cliente lo percibe justo |
| **SPT** | el de menor $p_j$ | minimiza siempre $\bar F$ y $\bar N$ (y maximiza $U$) |
| **EDD** | el de entrega más próxima | minimiza siempre el **atraso máximo** |
| **LPT** | el de mayor $p_j$ | casi siempre el peor; sirve de contraste |
| **Holgura** | el de menor $d_j - \text{hoy} - p_j$ | cuida las fechas mirando el trabajo que falta |
| **Razón crítica** | el de menor $RC_j = \dfrac{d_j - \text{hoy}}{p_j}$ | se recalcula al terminar cada trabajo |

Cómo leer la razón crítica: $RC > 1$ va holgado, $RC = 1$ va justo, $RC < 1$ ya no alcanza aunque
empiece ahora, y $RC \le 0$ significa que la fecha ya pasó.

> **Por qué SPT gana en flujo.** El tiempo de proceso del primer trabajo se suma al flujo de todos
> los que vienen detrás: con $n$ trabajos, el primero pesa $n$ veces y el último pesa una. Poner los
> cortos adelante hace que lo que más se repite sea lo más chico.

---

## 3. Ejemplo resuelto · Estampa Sur

Estampa Sur es un taller de serigrafía de la Región del Biobío con **una sola máquina de
estampado**. El lunes (día 0) tiene seis pedidos, en este orden de llegada:

| Pedido | Proceso $p_j$ (días) | Entrega $d_j$ (día) |
|---|---|---|
| Poleras club | 4 | 10 |
| Bolsas feria | 7 | 9 |
| Uniformes colegio | 3 | 6 |
| Gorros evento | 8 | 27 |
| Delantales cocina | 5 | 14 |
| Banderas | 2 | 20 |

**Paso 1 · FCFS a mano.** Se acumula el proceso y se compara con la entrega.

| Orden | $p_j$ | Flujo $F_j$ | $d_j$ | Atraso $T_j$ |
|---|---|---|---|---|
| Poleras club | 4 | 4 | 10 | 0 |
| Bolsas feria | 7 | 11 | 9 | 2 |
| Uniformes colegio | 3 | 14 | 6 | 8 |
| Gorros evento | 8 | 22 | 27 | 0 |
| Delantales cocina | 5 | 27 | 14 | 13 |
| Banderas | 2 | 29 | 20 | 9 |
| **Suma** | **29** | **107** | | **32** |

$$\bar F = \frac{107}{6} = 17{,}8 \text{ d} \qquad U = \frac{29}{107} = 27{,}1\ \% \qquad \bar N = \frac{107}{29} = 3{,}69 \qquad \bar T = \frac{32}{6} = 5{,}3 \text{ d}$$

**Paso 2 · Las otras reglas.** Mismo procedimiento con otro orden. SPT ordena por $p_j$
(Banderas, Uniformes, Poleras, Delantales, Bolsas, Gorros); EDD por $d_j$ (Uniformes, Bolsas,
Poleras, Delantales, Banderas, Gorros).

**Paso 3 · Razón crítica, recalculada.** Se calcula $RC$ para todos los pendientes, se atiende el
menor y se avanza el reloj.

| Día | Razones críticas de los pendientes | Se atiende |
|---|---|---|
| 0 | Bolsas 1,29 · Uniformes 2,00 · Poleras 2,50 · Delantales 2,80 · Gorros 3,38 · Banderas 10,00 | Bolsas feria |
| 7 | Uniformes −0,33 · Poleras 0,75 · Delantales 1,40 · Gorros 2,50 · Banderas 6,50 | Uniformes colegio |
| 10 | Poleras 0,00 · Delantales 0,80 · Gorros 2,12 · Banderas 5,00 | Poleras club |
| 14 | Delantales 0,00 · Gorros 1,62 · Banderas 3,00 | Delantales cocina |
| 19 | Banderas 0,50 · Gorros 1,00 | Banderas |
| 21 | Gorros 0,75 | Gorros evento |

En el día 7 los uniformes ya tienen $RC$ negativa: su fecha (día 6) pasó mientras se estampaban
las bolsas. La regla los pone primero porque son los más urgentes, no porque todavía alcancen.

**Paso 4 · Comparar.**

| Regla | Flujo prom. | Utilización | Trabajos en sistema | Atraso prom. | Atraso máx. | Atrasados |
|---|---|---|---|---|---|---|
| FCFS | 17,8 d | 27,1 % | 3,69 | 5,3 d | 13 d | 4 |
| SPT | **13,3 d** | **36,2 %** | **2,76** | 2,3 d | 12 d | **2** |
| EDD | 16,0 d | 30,2 % | 3,31 | **2,2 d** | **5 d** | 5 |
| LPT | 20,5 d | 23,6 % | 4,24 | 9,3 d | 21 d | 5 |
| Holgura | 16,7 d | 29,0 % | 3,45 | 2,7 d | 5 d | 5 |
| Razón crítica | 16,7 d | 29,0 % | 3,45 | 2,7 d | 5 d | 5 |

**Cómo se lee.**

- SPT gana en flujo, utilización y WIP, como garantiza la teoría, y además deja solo dos pedidos
  atrasados. El costo: las bolsas llegan 12 días tarde.
- EDD baja el peor atraso a 5 días, pero reparte un poco de atraso entre cinco clientes.
- La pregunta para el dueño del taller no es «qué regla es mejor», sino **¿prefiere un cliente muy
  molesto o cinco un poco molestos?** Esa respuesta elige la regla.
- Acá la holgura y la razón crítica dieron la misma secuencia. No siempre pasa (el ejercicio 10.5 lo
  muestra).

---

## 4. Dos máquinas en serie · regla de Johnson

Cuando **todos** los trabajos pasan por la máquina 1 y después por la máquina 2, el objetivo
habitual es el **makespan**: el tiempo hasta que termina el último. Johnson lo minimiza:

1. Busca el menor tiempo de toda la tabla (en cualquiera de las dos máquinas).
2. Si está en la máquina 1, ese trabajo va **lo más adelante posible**; si está en la máquina 2, va
   **lo más atrás posible**.
3. Tacha el trabajo y repite con los que quedan.

La intuición: la máquina 2 queda ociosa mientras espera el primer trabajo y el último trabajo la
deja sola al final. Johnson pone adelante lo que sale rápido de la máquina 1 y atrás lo que pasa
rápido por la máquina 2.

### Ejemplo · estampado → planchado y doblado (horas)

| Trabajo | Estampado (M1) | Planchado (M2) |
|---|---|---|
| J1 | 4 | 6 |
| J2 | 8 | 3 |
| J3 | 2 | 5 |
| J4 | 6 | 7 |
| J5 | 9 | 4 |
| J6 | 5 | 8 |

Los pasos: J3 (2 en M1, adelante) · J2 (3 en M2, atrás) · J1 (4 en M1, adelante) · J5 (4 en M2,
atrás) · J6 (5 en M1, adelante) · J4 (queda al medio). Secuencia: **J3 → J1 → J6 → J4 → J5 → J2**.

| Trabajo | M1 inicio–fin | M2 inicio–fin |
|---|---|---|
| J3 | 0–2 | 2–7 |
| J1 | 2–6 | 7–13 |
| J6 | 6–11 | 13–21 |
| J4 | 11–17 | 21–28 |
| J5 | 17–26 | 28–32 |
| J2 | 26–34 | 34–37 |

Cada operación en M2 empieza en el mayor entre «terminó en M1» y «M2 quedó libre». Makespan:
**37 h**. El planchado solo espera 4 horas (2 al inicio y 2 antes de J2). Si se hubieran tomado en
orden J1 a J6, el makespan habría sido de 42 horas.

---

## 5. Más de dos máquinas y rutas distintas

**Tres máquinas en serie (Johnson extendido).** Si se cumple que el menor tiempo en M1 es mayor o
igual que el mayor tiempo en M2, o que el menor tiempo en M3 es mayor o igual que el mayor en M2,
la máquina del medio nunca manda. Entonces se arman dos máquinas ficticias, $M1+M2$ y $M2+M3$, y se
aplica Johnson. Si la condición no se cumple, el método puede no dar el óptimo.

**$m$ máquinas · CDS (Campbell, Dudek y Smith).** Se arman $m-1$ problemas ficticios de dos
máquinas. En el problema $k$, la máquina ficticia A suma las primeras $k$ máquinas y la B las últimas
$k$. Se resuelve cada uno con Johnson, se simula cada secuencia en el taller real y se queda la de
menor makespan. Es una **heurística**: suele quedar cerca del óptimo, pero no lo garantiza
(ejercicio 10.9).

**Dos máquinas, rutas distintas · Jackson.** Los trabajos se separan en cuatro grupos: solo A,
solo B, A→B y B→A.

- Orden en A: primero los A→B (con Johnson), luego los solo A y al final los B→A.
- Orden en B: primero los B→A (con Johnson, tomando B como primera máquina), luego los solo B y al
  final los A→B.

Así ninguna máquina espera un trabajo que la otra todavía no suelta, salvo que no haya otra opción.

---

## 6. Asignación · método húngaro

Con $n$ personas (o máquinas) y $n$ tareas, cada par con un costo o un tiempo, se busca asignar una
tarea a cada persona con el menor total. Es un caso especial del problema de transporte
(Optimización).

1. A cada fila réstale su mínimo.
2. A cada columna réstale su mínimo.
3. Cubre todos los ceros con el menor número de líneas. Si necesitas $n$ líneas, hay una asignación
   óptima entre los ceros.
4. Si no, toma el menor número sin cubrir, réstaselo a los no cubiertos y súmaselo a los que están
   en un cruce de líneas. Vuelve al paso 3.

---

## 7. Control · entradas y salidas

Un programa se desarma en días. El **control de entradas y salidas** compara, semana a semana, el
trabajo que entra a un centro (input) y el que sale (output) contra lo planeado:

$$\text{cola}_t = \text{cola}_{t-1} + \text{entrada real}_t - \text{salida real}_t$$

- Si la entrada real supera a la salida real, la cola crece y los tiempos de espera también.
- **La entrada planeada nunca debería superar la salida planeada**: sería programar una cola.
- Se mira primero el cuello de botella: lo que se pierde ahí se pierde en todo el sistema.

El **diagrama de Gantt** cumple la misma función a la vista: barras planeadas contra barras reales.
Sirve solo si se actualiza.

### Límites de las reglas

- La programación es dinámica: llegan trabajos nuevos y la regla se vuelve a aplicar.
- Una regla mira un solo centro. No ve si el siguiente está parado o es el cuello de botella.
- Las reglas no ven más allá de la fecha: no distinguen un cliente grande de uno chico.

---

## 8. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Contar como atraso negativo un pedido que llega antes | $T_j = \max(0, F_j - d_j)$; nunca se resta |
| Calcular la utilización al revés ($\sum F / \sum p$) | La utilización es menor que 1; si te dio mayor, invertiste |
| Usar la razón crítica del día 0 para toda la secuencia | Se recalcula cada vez que termina un trabajo |
| En Johnson, mandar adelante un mínimo que está en M2 | Mínimo en M1 → adelante; mínimo en M2 → atrás |
| En el Gantt, empezar en M2 apenas M2 se libera | Empieza en el mayor entre «M2 libre» y «terminó en M1» |
| Creer que CDS da el óptimo | Es heurística; compárala con la cota o con todas las secuencias si son pocas |

---

## 9. Práctica

Diez ejercicios: 10.1 a 10.4 básicos, 10.5 a 10.8 intermedios, 10.9 y 10.10 de desafío. Las pautas
están en la sección 10. Intenta cada uno antes de mirarla.

**10.1 · Horno de un laboratorio dental (básico).** Un laboratorio tiene un horno de cerámica y
cuatro trabajos en orden de llegada. Aplica FCFS, SPT, EDD y LPT y calcula los cuatro indicadores.

| Trabajo | Proceso (días) | Entrega (día) |
|---|---|---|
| Corona | 3 | 5 |
| Puente | 6 | 8 |
| Carilla | 1 | 4 |
| Prótesis | 4 | 13 |

**10.2 · Qué regla para qué objetivo (básico).** Sin calcular, indica la regla y justifica en una
línea. (a) Un hospital quiere que los pacientes en espera sean los menos posibles. (b) Una imprenta
cobra multa solo al pedido más atrasado de la semana. (c) Un servicio público quiere que nadie pueda
reclamar que lo pasaron. (d) ¿Por qué LPT casi nunca se usa, si es una regla legítima?

**10.3 · Mueblería: corte → lijado (básico).** Secuencia con Johnson, dibuja el Gantt, calcula el
makespan y el tiempo ocioso del lijado.

| Mueble | Corte (h) | Lijado (h) |
|---|---|---|
| Mesa | 6 | 2 |
| Silla | 2 | 4 |
| Repisa | 3 | 5 |
| Velador | 7 | 6 |
| Banco | 4 | 1 |

**10.4 · Razón crítica en el día 12 (básico).** Hoy es el día 12. Calcula la razón crítica de cada
pedido, ordénalos e interpreta cada valor. Si hay empate, decide con EDD.

| Pedido | Trabajo restante (días) | Entrega (día) |
|---|---|---|
| P1 | 4 | 20 |
| P2 | 6 | 15 |
| P3 | 2 | 13 |
| P4 | 5 | 27 |

**10.5 · Imprenta digital, seis reglas (intermedio).** Una impresora y seis trabajos en orden de
llegada. Aplica FCFS, SPT, EDD, LPT, holgura y razón crítica (recalculada) y arma la tabla
comparativa. ¿Cuál recomiendas si la imprenta cobra multa por cada día de atraso de cualquier pedido?

| Trabajo | Proceso (días) | Entrega (día) |
|---|---|---|
| Afiches | 5 | 7 |
| Folletos | 2 | 11 |
| Libros | 9 | 16 |
| Tarjetas | 1 | 3 |
| Calendarios | 6 | 18 |
| Revistas | 4 | 22 |

**10.6 · Johnson con empates (intermedio).** Cocina industrial: preparación → horneado, en minutos.
Secuencia con Johnson, calcula el makespan y el ocio del horno. Luego prueba otra forma de romper
los empates: ¿cambia el makespan?

| Pedido | Preparación | Horneado |
|---|---|---|
| K1 | 30 | 30 |
| K2 | 20 | 45 |
| K3 | 40 | 20 |
| K4 | 25 | 25 |
| K5 | 35 | 50 |

**10.7 · Laboratorio clínico, rutas distintas (intermedio).** A es la centrífuga y B el analizador
(minutos). Aplica Jackson, simula las dos máquinas y calcula el makespan. ¿Se podía terminar antes?

| Muestra | A | B | Ruta |
|---|---|---|---|
| M1 | 15 | 25 | A→B |
| M2 | 30 | 10 | A→B |
| M3 | 20 | — | solo A |
| M4 | 10 | 20 | B→A |
| M5 | 25 | 15 | B→A |
| M6 | — | 30 | solo B |
| M7 | 10 | 35 | A→B |

**10.8 · Control de entradas y salidas (intermedio).** Centro de soldadura, en horas estándar, con
una cola inicial de 60 h. Completa las desviaciones acumuladas y la cola de cada semana, y
diagnostica qué pasa y qué harías.

| Semana | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Entrada planeada | 200 | 200 | 220 | 220 |
| Entrada real | 190 | 230 | 240 | 210 |
| Salida planeada | 200 | 210 | 220 | 220 |
| Salida real | 195 | 200 | 205 | 200 |

**10.9 · CDS, cuatro órdenes y cuatro estaciones (desafío).** Todas pasan por E1→E2→E3→E4
(horas). Aplica CDS con sus tres problemas ficticios y elige la mejor secuencia. Después revisa las
24 secuencias posibles (a mano o con código): ¿CDS encontró el óptimo?

| Orden | E1 | E2 | E3 | E4 |
|---|---|---|---|---|
| O1 | 6 | 4 | 7 | 3 |
| O2 | 3 | 8 | 2 | 6 |
| O3 | 7 | 3 | 5 | 8 |
| O4 | 2 | 6 | 4 | 5 |

**10.10 · Cuatro técnicos y cuatro reparaciones (desafío).** Horas que tarda cada técnico en cada
reparación. Asigna con el método húngaro para minimizar las horas totales. Luego: si Carla se
enferma y entra un quinto técnico que tarda 8 h en cualquier reparación, ¿cuánto cambia el total?

| | Bomba | Motor | Tablero | Válvula |
|---|---|---|---|---|
| Ana | 9 | 7 | 11 | 6 |
| Beto | 8 | 10 | 7 | 9 |
| Carla | 6 | 8 | 9 | 10 |
| Diego | 10 | 6 | 8 | 7 |

---

## 10. Pautas

**10.1.**

| Regla | Secuencia | Flujo prom. | Utilización | En sistema | Atraso prom. | Atraso máx. |
|---|---|---|---|---|---|---|
| FCFS | Corona, Puente, Carilla, Prótesis | 9,0 d | 38,9 % | 2,57 | 2,0 d | 6 d |
| SPT | Carilla, Corona, Prótesis, Puente | 6,8 d | 51,9 % | 1,93 | 1,5 d | 6 d |
| EDD | Carilla, Corona, Puente, Prótesis | 7,2 d | 48,3 % | 2,07 | 0,8 d | 2 d |
| LPT | Puente, Prótesis, Corona, Carilla | 10,8 d | 32,6 % | 3,07 | 4,5 d | 10 d |

SPT gana en flujo; EDD en atraso. Fíjate que $U \times \bar N = 1$ en cada fila.

**10.2.** (a) SPT: minimiza el número promedio de trabajos en el sistema. (b) EDD: minimiza el atraso
máximo, que es lo único que se multa. (c) FCFS: es la que se percibe como justa. (d) Porque maximiza
el flujo y el WIP; solo tiene sentido si los trabajos largos traen un beneficio que la tabla no
muestra (por ejemplo, un cliente que paga por adelantado).

**10.3.** Secuencia: **Silla → Repisa → Velador → Mesa → Banco**.

| Mueble | Corte | Lijado |
|---|---|---|
| Silla | 0–2 | 2–6 |
| Repisa | 2–5 | 6–11 |
| Velador | 5–12 | 12–18 |
| Mesa | 12–18 | 18–20 |
| Banco | 18–22 | 22–23 |

Makespan: **23 h**. El lijado está ocioso 5 h: 2 al inicio, 1 antes del velador y 2 antes del banco.

**10.4.** $RC_{P1} = (20-12)/4 = 2{,}00$ · $RC_{P2} = (15-12)/6 = 0{,}50$ ·
$RC_{P3} = (13-12)/2 = 0{,}50$ · $RC_{P4} = (27-12)/5 = 3{,}00$. Empatan P2 y P3; EDD pone primero a
P3 (entrega 13). Orden: **P3, P2, P1, P4**. P2 y P3 ya no alcanzan aunque partan hoy (RC < 1); P1 va
holgado; P4 tiene margen de sobra.

**10.5.**

| Regla | Secuencia | Flujo prom. | Utilización | En sistema | Atraso prom. | Atraso máx. | Atrasados |
|---|---|---|---|---|---|---|---|
| FCFS | Afi, Fol, Lib, Tar, Cal, Rev | 15,8 d | 28,4 % | 3,52 | 4,0 d | 14 d | 3 |
| SPT | Tar, Fol, Rev, Afi, Cal, Lib | 11,3 d | 39,7 % | 2,52 | 2,7 d | 11 d | 2 |
| EDD | Tar, Afi, Fol, Lib, Cal, Rev | 13,7 d | 32,9 % | 3,04 | 1,8 d | 5 d | 3 |
| LPT | Lib, Cal, Afi, Rev, Fol, Tar | 20,2 d | 22,3 % | 4,48 | 9,0 d | 24 d | 4 |
| Holgura | Afi, Tar, Lib, Fol, Cal, Rev | 15,5 d | 29,0 % | 3,44 | 3,2 d | 6 d | 4 |
| Razón crítica | Afi, Tar, Lib, Fol, Cal, Rev | 15,5 d | 29,0 % | 3,44 | 3,2 d | 6 d | 4 |

Si la multa es por cada día de atraso de cualquier pedido, lo que importa es el atraso total (o
promedio): **EDD**, con 1,8 días promedio. Holgura y razón crítica empiezan por los afiches porque
miran el trabajo restante, y eso empuja a las tarjetas (entrega día 3) a un atraso evitable.

**10.6.** Una secuencia de Johnson: **K2 → K4 → K1 → K5 → K3**. Makespan **190 min**; el horno espera
20 min (solo al inicio). Las otras formas de romper los empates entre K1 y K4 (adelante o atrás)
dan el mismo makespan de 190 min, que además es el óptimo. Con empates, Johnson tiene varias
secuencias óptimas.

**10.7.** Orden en A: **M7, M1, M2, M3, M5, M4**. Orden en B: **M5, M4, M6, M7, M1, M2**.
Simulación: en A terminan M7 a los 10, M1 a los 25, M2 a los 55, M3 a los 75, M5 a los 100 (esperó
a que B la soltara a los 15; A estaba ocupada igual) y M4 a los 110. En B terminan M5 a los 15, M4 a
los 35, M6 a los 65, M7 a los 100, M1 a los 125 y M2 a los 135. Makespan: **135 min**. No se podía
terminar antes: la carga total de B es $25+10+20+15+30+35 = 135$ min y B nunca estuvo ociosa.

**10.8.**

| Semana | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Desviación acumulada de entrada | −10 | +20 | +40 | +30 |
| Desviación acumulada de salida | −5 | −15 | −30 | −50 |
| Cola al cierre | 55 | 85 | 120 | 130 |

Entra más de lo planeado y sale menos: la cola se duplica en cuatro semanas. El problema no es solo
la entrada (se pasa en 30 h), es la salida (pierde 50 h): el centro no está rindiendo su capacidad
planeada. Primero se revisa por qué (ausencias, fallas, falta de material) y, mientras tanto, se
frena la liberación de órdenes hacia este centro para que la cola no siga creciendo.

**10.9.**

| $k$ | Máquinas ficticias | Secuencia de Johnson | Makespan real |
|---|---|---|---|
| 1 | E1 · E4 | O4, O2, O3, O1 | 35 h |
| 2 | E1+E2 · E3+E4 | O4, O1, O3, O2 | 38 h |
| 3 | E1+E2+E3 · E2+E3+E4 | O4, O2, O3, O1 | 35 h |

CDS elige **O4 → O2 → O3 → O1** con 35 h. Revisando las 24 secuencias, el óptimo es
**O4 → O3 → O2 → O1** con **34 h**. CDS quedó a una hora: es una buena heurística, no un método exacto.

**10.10.** Restando el mínimo de cada fila (6, 7, 6 y 6) aparecen ceros en Ana-Válvula,
Beto-Tablero, Carla-Bomba y Diego-Motor. Restar por columnas no cambia nada (cada columna ya tiene un
cero) y cuatro ceros independientes bastan. Asignación: Ana → Válvula, Beto → Tablero, Carla → Bomba,
Diego → Motor, con **25 h** totales. Sin Carla y con el quinto técnico (8 h en todo), conviene que él
tome la bomba (Carla tardaba 6, nadie más baja de 8): Ana → Válvula, Beto → Tablero, Diego → Motor,
nuevo → Bomba, con $6+7+6+8 = 27$ h. El total sube 2 h.

---

## 11. Caso integrador · Estampa Sur, semana 6

> Este caso sigue a Estampa Sur por todo el ramo. Cada unidad parte de lo que calculó la anterior;
> acá se usan los lotes que el programa maestro (unidad 7) dejó en la semana 6, con los tiempos por
> unidad de cada centro (unidad 9). Si no has hecho esas unidades, parte de esta tabla.

El programa maestro tiene un lote de cada producto en la semana 6. Todos pasan por estampado y luego
por planchado y doblado. Las horas salen de multiplicar el lote por los segundos por unidad de cada
centro. Las entregas se cuentan en horas de trabajo desde el lunes a las 8:00.

| Orden | Lote (unidades) | Estampado (h) | Planchado (h) | Entrega (h) |
|---|---|---|---|---|
| OP-61 poleras básicas | 720 | 6 | 4 | 16 |
| OP-62 polerones | 360 | 9 | 5 | 30 |
| OP-63 poleras estampado doble | 360 | 11 | 3 | 24 |
| OP-64 bolsas | 540 | 3 | 6 | 12 |
| OP-65 gorros | 480 | 4 | 2 | 34 |

El planchado tiene 18 h disponibles y esta semana carga 20 h. La unidad 9 compara tres salidas y la
semana 6 toma la primera: 2 horas extra de planchado. Por eso acá el planchado trabaja las 20 h, y
se supone que la persona ajusta su media jornada a los momentos en que llega trabajo del estampado.

**Pregunta.** El jefe de producción duda entre Johnson (minimiza el makespan) y ordenar por fecha
de entrega (EDD) en el estampado. Compara las dos y recomienda.

**Desarrollo.**

| | Johnson | EDD |
|---|---|---|
| Secuencia | OP-64, OP-62, OP-61, OP-63, OP-65 | OP-64, OP-61, OP-63, OP-62, OP-65 |
| Makespan | 35 h | 36 h |
| Órdenes atrasadas | OP-61 (6 h), OP-63 (8 h), OP-65 (1 h) | OP-62 (4 h), OP-65 (2 h) |
| Atraso total | 15 h | 6 h |

**Lectura.** Johnson termina la semana una hora antes, pero atrasa tres órdenes y suma 15 horas de
atraso. EDD tarda una hora más y deja 6 horas de atraso en dos órdenes con entregas holgadas. Si los
clientes de Estampa Sur pagan por cumplir la fecha (colegios y clubes con evento), la recomendación
es **EDD**. El makespan importa cuando la planta tiene que liberarse para otra cosa; acá lo que
importa es la fecha.

**Lo que pasa a la unidad 11.** El tiempo que cada orden pasa en el taller y el trabajo en proceso
que se acumula frente al estampado (el centro más cargado) son el punto de partida de la física de
la fábrica (ley de Little).

---

## 12. Para seguir

**En los libros del ramo.**

- Heizer y Render, *Principios de administración de operaciones* (5.ª ed., 2004), capítulo de
  programación a corto plazo: reglas de prioridad, Johnson, asignación y control de entradas y
  salidas. Sus problemas del final del capítulo son la mejor práctica adicional.
- Schroeder, *Administración de operaciones* (2.ª ed., 2004), capítulos 12, 13 y 16 (los que fija el
  programa para planificación y control).
- Chase, Jacobs y Aquilano, *Administración de operaciones* (12.ª ed., 2009), capítulo de
  programación.

**Abiertos y gratis.**

- Abbas y Goosheh, *Operations Management*, Fanshawe College (2025), en inglés, capítulo de
  programación a corto plazo. Descarga en la colección abierta de Ontario:
  https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/2473

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un ejercicio de Johnson con empates y
corrígeme paso a paso».
