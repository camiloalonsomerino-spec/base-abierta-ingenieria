---
ramo: Gestión de Operaciones
unidad: 11
titulo: Física de la fábrica
version: 0.1 (15-10-2026)
requiere: [03-proceso-y-capacidad, 10-programacion-de-operaciones]
alimenta: [12-calidad]
verificacion: verificacion/u11_fisica_fabrica.py
---

# Unidad 11 · Física de la fábrica

**Qué vas a poder hacer.** Usar la ley de Little para pasar entre trabajo en proceso, tasa de
salida y tiempo de ciclo (y saber por qué se cumple); acotar lo que puede lograr una línea con el
mejor caso, el peor caso y el peor caso práctico; explicar por qué la fila explota cuando la
utilización se acerca a 100 %; estimar la espera con la aproximación de Kingman; y simular a mano
una fila de un servidor con un reloj de eventos.

**Lo que necesitas antes.** Cuello de botella y utilización (unidad 3); el programa de la semana
6 de Estampa Sur (unidad 10). De probabilidad: media, desviación estándar y números aleatorios.

**Tiempo.** Unas 4,5 horas: 2 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. La idea

Las unidades anteriores decidieron **cuánto** producir y **en qué orden**. Esta mira **cómo fluye**
el trabajo: cuánto se acumula, cuánto sale y cuánto tarda. Tres medidas lo describen:

| Medida | Símbolo | Qué es | Unidad típica |
|---|---|---|---|
| Trabajo en proceso | WIP o $L$ | unidades que ya entraron y todavía no salen | unidades |
| Throughput (tasa de salida) | TH o $\lambda$ | unidades que salen por unidad de tiempo | unidades/h |
| Tiempo de ciclo | CT o $W$ | lo que tarda una unidad desde que entra hasta que sale | h |

Para una línea se agregan tres parámetros:

- $r_b$, la **tasa del cuello de botella**: la máxima tasa de salida sostenible.
- $T_0$, el **tiempo de proceso bruto**: la suma de los tiempos de proceso, sin esperas.
- $W_0 = r_b \cdot T_0$, el **WIP crítico**: el WIP justo para que la línea, sin variabilidad, saque
  $r_b$ con un tiempo de ciclo $T_0$.

«Física» porque son relaciones que se cumplen siempre, como una ley de conservación. Una planta que
promete un tiempo de ciclo corto con mucho WIP y poca salida está prometiendo algo imposible.

---

## 2. Ley de Little

En un sistema estable, en el largo plazo:

$$\text{WIP} = \text{TH} \times \text{CT} \qquad (L = \lambda W)$$

Sirve para despejar la que falta: con dos medidas se conoce la tercera.

### Por qué se cumple

Mira un intervalo $[0, T]$ que empieza y termina con el sistema vacío, en el que entran y salen
$n$ unidades. Sea $N(t)$ el número de unidades dentro en el instante $t$ y $W_i$ el tiempo que pasó
dentro la unidad $i$.

1. Dibuja $N(t)$ contra el tiempo. Cada unidad aporta una franja de altura 1 y largo $W_i$
   (desde que entra hasta que sale). Apiladas, las franjas forman el área bajo la curva:
   $$\int_0^T N(t)\,dt = \sum_{i=1}^{n} W_i$$
2. Divide los dos lados por $T$ y multiplica y divide el lado derecho por $n$:
   $$\underbrace{\frac{1}{T}\int_0^T N(t)\,dt}_{L} = \underbrace{\frac{n}{T}}_{\lambda} \cdot \underbrace{\frac{1}{n}\sum_{i=1}^{n} W_i}_{W}$$
3. El lado izquierdo es el número promedio dentro (promediado en el tiempo); $n/T$ es la tasa a la
   que pasan las unidades; el último factor es su tiempo promedio dentro. Queda $L = \lambda W$.

Si el sistema no parte o no termina vacío, sobran o faltan los pedazos de franja cortados en los
bordes. Divididos por $T$, se hacen despreciables cuando el intervalo crece, siempre que el sistema
sea **estable** (que el WIP no crezca sin límite).

### Qué no exige

No importa la distribución de los tiempos, ni el orden de atención (FCFS, SPT, EDD), ni cuántas
máquinas hay. Por eso sirve para cualquier «caja»: la línea entera, una sola máquina o solo la
fila frente a ella. Aplicada a la fila:

$$L_q = \lambda W_q$$

donde $L_q$ son las unidades esperando y $W_q$ la espera promedio.

> **Little no dice qué causa qué.** Dice que las tres medidas se mueven juntas. Si se quiere bajar
> el tiempo de ciclo sin perder salida, hay que bajar el WIP. Si se suelta más trabajo al piso sin
> agregar capacidad, el TH no sube: sube el tiempo de ciclo.

---

## 3. WIP, throughput y tiempo de ciclo en una línea

¿Qué TH y qué CT puede dar una línea con $w$ trabajos adentro? Hopp y Spearman acotan la respuesta
con tres casos.

| Caso | Throughput | Tiempo de ciclo | Cuándo ocurre |
|---|---|---|---|
| **Mejor caso** | $\min\left(\dfrac{w}{T_0},\; r_b\right)$ | $\max\left(T_0,\; \dfrac{w}{r_b}\right)$ | tiempos fijos, sin variabilidad |
| **Peor caso** | $\dfrac{1}{T_0}$ | $w \cdot T_0$ | los trabajos viajan en un solo paquete |
| **Peor caso práctico** | $\dfrac{w}{W_0 + w - 1}\, r_b$ | $T_0 + \dfrac{w-1}{r_b}$ | línea balanceada con variabilidad alta (tiempos exponenciales) |

Las tres cumplen Little: TH × CT $= w$. Una línea real que rinde **peor que el peor caso
práctico** tiene un problema que se puede corregir (variabilidad evitable, lotes grandes, cuello mal
alimentado). Una que rinde mejor va bien encaminada.

### Ejemplo · línea de sillas

Un taller de muebles de Chillán arma sillas en cuatro estaciones de una máquina cada una: corte
(20 min), armado (30 min), lijado (25 min) y barnizado (15 min). Tiene 6 sillas en la línea.

- Cuello: armado, $r_b = 60/30 = 2$ sillas/h.
- $T_0 = 20 + 30 + 25 + 15 = 90$ min $= 1{,}5$ h.
- $W_0 = 2 \times 1{,}5 = 3$ sillas.

| Caso con $w = 6$ | Throughput | Tiempo de ciclo |
|---|---|---|
| Mejor | 2,00 sillas/h | 3,0 h |
| Peor | 0,67 sillas/h | 9,0 h |
| Peor práctico | $\frac{6}{3+6-1} \times 2 =$ 1,50 sillas/h | $1{,}5 + \frac{5}{2} =$ 4,0 h |

Con 6 sillas ya está pasado del WIP crítico (3): en el mejor caso, agregar sillas no sube la
salida, solo alarga el tiempo de ciclo.

---

## 4. Utilización y congestión

La **utilización** de una estación es la fracción del tiempo que trabaja:

$$u = \frac{r_a \cdot t_e}{m}$$

con $r_a$ la tasa de llegada, $t_e$ el tiempo de proceso efectivo y $m$ las máquinas en paralelo.
Si $u \ge 1$, la estación recibe más de lo que puede hacer: la fila crece sin límite y el sistema
es **inestable**. Ninguna regla de prioridad lo arregla.

Con $u < 1$ la fila igual existe, porque las llegadas y los tiempos varían. Y su tamaño depende
del factor $u/(1-u)$, que crece cada vez más rápido:

| Utilización $u$ | 50 % | 80 % | 90 % | 95 % |
|---|---|---|---|---|
| $u/(1-u)$ | 1 | 4 | 9 | 19 |

Pasar de 80 % a 90 % de utilización no sube la espera en un 12 %: la **duplica con creces**. Por eso
una planta sana no trabaja al 100 % de su capacidad (unidad 3): la holgura es lo que mantiene corta
la fila.

---

## 5. Variabilidad

La variabilidad se mide sin unidades con el **coeficiente de variación**:

$$c = \frac{\sigma}{t}$$

donde $\sigma$ es la desviación estándar y $t$ la media. Se usa $c_a$ para los tiempos entre
llegadas y $c_e$ para los tiempos de proceso. Hopp y Spearman la clasifican así:

| Variabilidad | Baja | Moderada | Alta |
|---|---|---|---|
| $c$ | menor que 0,75 | entre 0,75 y 1,33 | mayor que 1,33 |

Fuentes típicas de variabilidad en el proceso: fallas, preparaciones, retrabajos, operadores
distintos, material que falta. Las llegadas varían por lo que hace la estación anterior y por los
pedidos de los clientes.

### Aproximación de Kingman (VUT)

Para una estación de una máquina, la espera promedio en la fila es aproximadamente:

$$W_q \approx \underbrace{\left(\frac{c_a^2 + c_e^2}{2}\right)}_{V} \cdot \underbrace{\left(\frac{u}{1-u}\right)}_{U} \cdot \underbrace{t_e}_{T}$$

Tres palancas, multiplicadas: **V**ariabilidad, **U**tilización y **T**iempo de proceso. Con
llegadas y servicios exponenciales ($c_a = c_e = 1$) la fórmula es exacta (fila M/M/1). El tiempo
de ciclo de la estación es $W_q + t_e$ y el WIP sale con Little.

### La variabilidad viaja aguas abajo

Lo que sale de una estación llega a la siguiente. La variabilidad de las salidas es, en una
estación de una máquina:

$$c_d^2 = u^2 c_e^2 + (1 - u^2)\, c_a^2$$

Si la estación está muy cargada ($u$ cerca de 1), sus salidas copian la variabilidad de **su
proceso**; si está poco cargada, copian la de **sus llegadas**. Una máquina con fallas y muy
cargada contamina a toda la línea que viene detrás.

---

## 6. Buffers y estabilidad

La variabilidad no desaparece por decreto: se paga con alguna de estas tres cosas (la «ley de los
buffers» de Hopp y Spearman):

| Buffer | Ejemplo |
|---|---|
| **Inventario** | stock entre etapas, WIP frente a la máquina |
| **Capacidad** | máquinas o personas que a veces están ociosas |
| **Tiempo** | plazos de entrega más largos, clientes que esperan |

Reducir la variabilidad libera esos buffers. Si no se reduce, hay que elegir cuál se paga.

**Dónde va el buffer.** Frente al cuello de botella: una hora perdida ahí es una hora perdida en
toda la planta (Goldratt, *La meta*). Un buffer frente a una estación con holgura casi no sirve.

**Estabilidad.** Un sistema es estable si en todas las estaciones $u < 1$. Con $u$ muy cerca de 1
es estable en teoría, pero cualquier racha (una falla, un pedido grande) deja una fila que tarda
mucho en vaciarse.

**Controlar el WIP.** Como el TH no sube por encima de $r_b$, soltar trabajo al piso antes de
tiempo solo agrega WIP y tiempo de ciclo (Little). Los sistemas que fijan un tope de WIP (CONWIP,
kanban) liberan una orden nueva solo cuando sale otra.

---

## 7. Simular una fila a mano

Las fórmulas dan promedios de largo plazo. Para ver qué pasa cliente a cliente se **simula** con
eventos discretos y avance al próximo evento.

**Componentes.**

- **Variables de entrada:** tiempos entre llegadas y de servicio.
- **Variables de estado:** servidor libre (0) u ocupado (1), y cuántos hay en la fila.
- **Reloj:** el instante en que va la simulación. Parte en 0.
- **Lista de eventos:** la próxima llegada y la próxima salida. El reloj salta al **menor** de los
  dos.
- **Contadores:** atendidos, esperas, tiempo con el servidor ocupado, tiempo con $k$ en la fila.

**Paso a paso.**

1. Programa la primera llegada.
2. Avanza el reloj al evento más próximo. Si coinciden una salida y una llegada, procesa primero la
   salida.
3. **Llegada:** si el servidor está libre, el cliente pasa directo (espera 0); si no, entra a la
   fila. Programa la llegada siguiente.
4. **Salida:** suma un atendido. Si hay fila, el primero pasa a atención; su espera es el reloj
   menos su hora de llegada.
5. Repite hasta atender a todos.

**Al final:** utilización $=$ tiempo ocupado / tiempo total; espera promedio y máxima; fracción
del tiempo con 0, 1, 2… en la fila; y el largo promedio de la fila, que es el área bajo la curva
de la fila dividida por el tiempo total.

**Montecarlo.** Si los tiempos son aleatorios, se asigna a cada valor un tramo de números de 00 a
99 según su probabilidad acumulada, y cada número aleatorio se traduce al valor de su tramo.

---

## 8. Ejemplo resuelto · Ferretería en Los Ángeles

Una ferretería tiene un solo mesón de despacho. El dueño midió estas distribuciones (en minutos):

| Entre llegadas | Probabilidad | Números |
|---|---|---|
| 1 | 0,10 | 00 a 09 |
| 2 | 0,20 | 10 a 29 |
| 3 | 0,30 | 30 a 59 |
| 4 | 0,25 | 60 a 84 |
| 5 | 0,15 | 85 a 99 |

| Servicio | Probabilidad | Números |
|---|---|---|
| 1 | 0,15 | 00 a 14 |
| 2 | 0,30 | 15 a 44 |
| 3 | 0,35 | 45 a 79 |
| 4 | 0,20 | 80 a 99 |

Números aleatorios para 8 clientes (el reloj parte en 0 y el primero llega después del primer
tiempo entre llegadas):

| Cliente | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|---|
| Aleatorio llegada | 47 | 08 | 21 | 83 | 05 | 66 | 92 | 31 |
| Aleatorio servicio | 71 | 88 | 54 | 19 | 93 | 37 | 60 | 08 |

**Paso 1 · Traducir los números.** 47 cae en 30 a 59: 3 minutos. Así con todos:

| Cliente | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|---|
| Entre llegadas | 3 | 1 | 2 | 4 | 1 | 4 | 5 | 3 |
| Llega en | 3 | 4 | 6 | 10 | 11 | 15 | 20 | 23 |
| Servicio | 3 | 4 | 3 | 2 | 4 | 2 | 3 | 1 |

**Paso 2 · Tabla de eventos.** El reloj salta de evento en evento. En el minuto 6 coinciden la
salida de C1 y la llegada de C3: primero sale C1 (entra C2) y después C3 se pone en la fila.

| Reloj | Evento | Servidor | En cola | Entra a atención (esperó) | Atendidos |
|---|---|---|---|---|---|
| 3 | Llega C1 | 1 | 0 | C1 (0) | 0 |
| 4 | Llega C2 | 1 | 1 | — | 0 |
| 6 | Sale C1 | 1 | 0 | C2 (2) | 1 |
| 6 | Llega C3 | 1 | 1 | — | 1 |
| 10 | Sale C2 | 1 | 0 | C3 (4) | 2 |
| 10 | Llega C4 | 1 | 1 | — | 2 |
| 11 | Llega C5 | 1 | 2 | — | 2 |
| 13 | Sale C3 | 1 | 1 | C4 (3) | 3 |
| 15 | Sale C4 | 1 | 0 | C5 (4) | 4 |
| 15 | Llega C6 | 1 | 1 | — | 4 |
| 19 | Sale C5 | 1 | 0 | C6 (4) | 5 |
| 20 | Llega C7 | 1 | 1 | — | 5 |
| 21 | Sale C6 | 1 | 0 | C7 (1) | 6 |
| 23 | Llega C8 | 1 | 1 | — | 6 |
| 24 | Sale C7 | 1 | 0 | C8 (1) | 7 |
| 25 | Sale C8 | 0 | 0 | — | 8 |

**Paso 3 · Estadísticas.** La simulación dura 25 min (del 0 a la última salida).

- **Utilización:** el mesón atiende $3+4+3+2+4+2+3+1 = 22$ min de 25: $u = 88{,}0\ \%$.
- **Espera:** $0+2+4+3+4+4+1+1 = 19$ min entre 8 clientes: $W_q = 2{,}375 \approx 2{,}4$ min. La
  espera máxima es de 4 min (C3, C5 y C6). Esperaron 7 de los 8 clientes.
- **Largo de la fila:** con 0 en la fila durante 8 min, con 1 durante 15 min y con 2 durante 2 min.
  En fracciones: 32,0 % · 60,0 % · 8,0 %. Promedio: $L_q = (0 \cdot 8 + 1 \cdot 15 + 2 \cdot 2)/25 = 19/25 = 0{,}76$.

**Paso 4 · Little dentro de la simulación.** Tasa de llegada observada: $\lambda = 8/25 = 0{,}320$
clientes por minuto. Entonces $\lambda W_q = 0{,}320 \times 2{,}375 = 0{,}76$, igual a $L_q$. No es
casualidad: el área bajo la curva de la fila (19) es la suma de las esperas (19), que es justo la
derivación de la sección 2. Se cumple exacto porque la simulación parte y termina vacía.

**Paso 5 · Comparar con Kingman.** Con las distribuciones: tiempo medio entre llegadas
$t_a = 3{,}15$ min y desviación 1,19; servicio medio $t_e = 2{,}6$ min y desviación 0,97. Entonces
$c_a = 0{,}38$, $c_e = 0{,}37$ y $u = 2{,}6/3{,}15 = 82{,}5\ \%$.

$$W_q \approx \left(\frac{0{,}38^2 + 0{,}37^2}{2}\right) \cdot \frac{0{,}825}{0{,}175} \cdot 2{,}6 = 0{,}14 \cdot 4{,}73 \cdot 2{,}6 = 1{,}7 \text{ min}$$

y $L_q \approx 1{,}74 / 3{,}15 = 0{,}55$ clientes.

**Cómo se lee.** La simulación dio más espera (2,4 contra 1,7 min) y más utilización (88 % contra
82,5 %) que el largo plazo, porque en estos 8 clientes los números aleatorios trajeron llegadas
seguidas al principio (C2 y C3 a 1 y 2 minutos). Ocho clientes son una muestra, no el promedio: para
decidir se corren muchas réplicas largas. Lo que sí vale siempre, también en una corrida corta, es
Little. Para el dueño: con 82,5 % de utilización la espera es corta, pero un mesón al 90 % o más
duplicaría la fila (sección 4).

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Mezclar unidades en Little (TH por hora con CT en minutos) | Pasa todo a la misma unidad de tiempo antes de multiplicar |
| Usar Little con la tasa de llegada cuando el sistema es inestable ($u \ge 1$) | Primero revisa $u < 1$; si no, el WIP crece y no hay promedio |
| Creer que más WIP da más salida siempre | Pasado $W_0$ el TH queda en $r_b$; solo crece el tiempo de ciclo |
| Pensar que la espera crece en proporción a la utilización | Crece con $u/(1-u)$: de 80 % a 90 % se duplica con creces |
| En la simulación, procesar la llegada antes que la salida cuando coinciden | Convención: primero la salida |
| Calcular el largo de la fila como el promedio de la columna «en cola» | Es un promedio **en el tiempo**: pondera cada valor por cuánto duró |
| Usar la desviación estándar en vez del coeficiente de variación en Kingman | Kingman pide $c = \sigma / t$, sin unidades, al cuadrado |

---

## 10. Práctica

Diez ejercicios: 11.1 a 11.4 básicos, 11.5 a 11.8 intermedios, 11.9 y 11.10 de desafío. Las pautas
están en la sección 11. Intenta cada uno antes de mirarla.

**11.1 · Packing de arándanos (básico).** Un packing de Linares despacha 450 cajas por hora y tiene
en promedio 1.350 cajas en proceso. (a) ¿Cuánto tarda una caja en pasar por el packing? (b) La
exportadora quiere que una caja no pase más de 2 horas adentro, sin bajar el despacho. ¿Qué WIP
promedio necesita?

**11.2 · Oficina de licencias (básico).** En una oficina municipal hay en promedio 18 personas
adentro, y cada una pasa 45 minutos en total. De esas 18, en promedio 12 están esperando. (a) ¿A
cuántas personas por hora atiende la oficina? (b) ¿Cuántas en una jornada de 8 horas? (c) ¿Cuánto
espera una persona en promedio y cuánto dura su atención?

**11.3 · Congestión en una máquina (básico).** Una máquina tarda 12 minutos por pieza. Suponiendo
llegadas y servicios exponenciales ($c_a = c_e = 1$), calcula la utilización, el factor $u/(1-u)$ y
la espera en la fila para 3; 4; 4,5 y 4,8 piezas por hora. ¿Qué ves?

**11.4 · ¿Cuánta variabilidad? (básico).** Calcula $c$ y $c^2$ de cada estación y clasifica su
variabilidad. ¿Cuál atacarías primero?

| Estación | Media (min) | Desviación estándar (min) |
|---|---|---|
| Torno | 10 | 4 |
| Soldadura | 20 | 18 |
| Pintura | 15 | 24 |

**11.5 · Simulación de un cajero (intermedio).** Simula una fila de un servidor con estos tiempos
(minutos). Arma la tabla de eventos y calcula utilización, espera promedio y máxima, fracción del
tiempo con 0, 1 y 2 en la fila, y el largo promedio de la fila. Comprueba Little.

| Cliente | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| Entre llegadas | 3 | 5 | 1 | 2 | 6 | 2 |
| Servicio | 4 | 6 | 3 | 5 | 2 | 4 |

**11.6 · Centro de mecanizado (intermedio).** Llega una pieza cada 12 minutos en promedio
($c_a = 1$) y el centro tarda 10 minutos por pieza ($c_e = 0{,}5$). (a) Con Kingman calcula la
espera en la fila, el tiempo de ciclo y el WIP. (b) Si aparecen fallas y $c_e$ sube a 1,5, ¿qué
pasa? (c) Volviendo a $c_e = 0{,}5$: si se baja el tiempo de proceso a 9 minutos, ¿cuánto baja la
espera?

**11.7 · Tres estaciones, tres casos (intermedio).** Una línea tiene tres estaciones de una máquina
con 12, 20 y 16 minutos por unidad. (a) Calcula $r_b$, $T_0$ y $W_0$. (b) Para $w = 2$, 5 y 10,
calcula TH y CT en el mejor caso, el peor caso y el peor caso práctico. (c) La línea real, con 10
unidades adentro, saca 2,1 unidades por hora. ¿Cuál es su tiempo de ciclo y cómo la evalúas?

**11.8 · Planta de cecinas (intermedio).** Una línea saca 40 unidades por hora. El WIP promedio es
de 60 unidades en picado, 120 en embutido y 20 en empaque (incluidas las que esperan). (a) Tiempo de
ciclo en cada etapa y total. (b) La gerencia quiere un tiempo de ciclo total de 3 horas sin bajar
la salida. ¿Qué tope de WIP total fijarías? ¿En qué etapa buscarías el WIP que sobra?

**11.9 · Romana de camiones (desafío).** Los camiones llegan a la romana de un packing y se pesan
de a uno (minutos):

| Entre llegadas | Probabilidad | | Pesaje | Probabilidad |
|---|---|---|---|---|
| 4 | 0,15 | | 5 | 0,30 |
| 6 | 0,25 | | 7 | 0,45 |
| 8 | 0,35 | | 9 | 0,25 |
| 10 | 0,25 | | | |

Números aleatorios para 10 camiones:

| Camión | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Aleatorio llegada | 58 | 03 | 91 | 27 | 44 | 76 | 15 | 62 | 89 | 35 |
| Aleatorio pesaje | 22 | 67 | 81 | 49 | 05 | 93 | 38 | 71 | 56 | 14 |

(a) Arma los tramos de números, traduce y simula. (b) Calcula utilización, espera promedio y
máxima, largo promedio de la fila, y comprueba Little. (c) Calcula la utilización y la espera de
largo plazo con Kingman. (d) ¿Por qué difieren tanto? ¿Le dirías al packing que la romana sobra?

**11.10 · Dos estaciones en serie (desafío).** Llega un trabajo cada 10 minutos ($c_a = 1$). La
estación 1 (lavado) tarda 8 minutos con $c_e = 1{,}2$; la estación 2 (inspección) tarda 9 minutos
con $c_e = 0{,}6$. (a) Calcula la espera en cada fila, el tiempo de ciclo total y el WIP (usa la
ecuación de enlace para las llegadas a la estación 2). (b) Hay presupuesto para una sola mejora:
**A**, mantención que baja el $c_e$ del lavado a 0,6, o **B**, una mejora que baja la inspección a
8 minutos. ¿Cuál baja más el tiempo de ciclo?

---

## 11. Pautas

**11.1.** (a) $\text{CT} = \text{WIP}/\text{TH} = 1.350/450 = 3$ h. (b) $\text{WIP} = 450 \times 2 = 900$ cajas. Hay que sacar 450 cajas del piso: soltar menos fruta a la vez, no trabajar más rápido.

**11.2.** (a) $\text{TH} = 18 / 0{,}75 = 24$ personas/h. (b) $24 \times 8 = 192$ personas por día.
(c) Little sobre la fila: $W_q = 12/24 = 0{,}5$ h $=$ 30 min. La atención dura $45 - 30 =$ 15 min (y
se comprueba: $24 \times 0{,}25 = 6$ personas siendo atendidas, las 18 menos las 12 que esperan).
Dos tercios del tiempo de la gente es espera.

**11.3.**

| Llegadas por hora | 3 | 4 | 4,5 | 4,8 |
|---|---|---|---|---|
| Utilización | 60 % | 80 % | 90 % | 96 % |
| $u/(1-u)$ | 1,5 | 4,0 | 9,0 | 24,0 |
| Espera en la fila | 18 min | 48 min | 108 min | 288 min |

Subir las llegadas en 60 % (de 3 a 4,8) multiplica la espera por 16. Cerca del 100 % un pequeño
aumento de carga produce una fila enorme.

**11.4.** Torno: $c = 4/10 = 0{,}40$, $c^2 = 0{,}16$, baja. Soldadura: $c = 0{,}90$, $c^2 = 0{,}81$,
moderada. Pintura: $c = 1{,}60$, $c^2 = 2{,}56$, alta. Se ataca primero la **pintura**: en Kingman
pesa $c^2$, y su aporte es más de tres veces el de la soldadura. Hay que buscar qué la hace tan
irregular (retoques, secado que depende del clima, cambios de color).

**11.5.** Llegadas en 3, 8, 9, 11, 17 y 19.

| Reloj | Evento | Servidor | En cola | Entra a atención (esperó) | Atendidos |
|---|---|---|---|---|---|
| 3 | Llega C1 | 1 | 0 | C1 (0) | 0 |
| 7 | Sale C1 | 0 | 0 | — | 1 |
| 8 | Llega C2 | 1 | 0 | C2 (0) | 1 |
| 9 | Llega C3 | 1 | 1 | — | 1 |
| 11 | Llega C4 | 1 | 2 | — | 1 |
| 14 | Sale C2 | 1 | 1 | C3 (5) | 2 |
| 17 | Sale C3 | 1 | 0 | C4 (6) | 3 |
| 17 | Llega C5 | 1 | 1 | — | 3 |
| 19 | Llega C6 | 1 | 2 | — | 3 |
| 22 | Sale C4 | 1 | 1 | C5 (5) | 4 |
| 24 | Sale C5 | 1 | 0 | C6 (5) | 5 |
| 28 | Sale C6 | 0 | 0 | — | 6 |

Dura 28 min. Utilización: $24/28 = 85{,}7\ \%$. Espera: $(0+0+5+6+5+5)/6 = 3{,}5$ min; máxima 6
min (C4). Fila: 0 durante 13 min, 1 durante 9 min y 2 durante 6 min, es decir 46,4 % · 32,1 % ·
21,4 % del tiempo. $L_q = (9 + 2 \cdot 6)/28 = 21/28 = 0{,}75$. Little: $\lambda = 6/28 = 0{,}214$ y
$\lambda W_q = 0{,}214 \times 3{,}5 = 0{,}75$. Se cumple.

**11.6.** (a) $u = 10/12 = 0{,}833$; $V = (1 + 0{,}25)/2 = 0{,}625$; $U = 0{,}833/0{,}167 = 5$.
$W_q \approx 0{,}625 \cdot 5 \cdot 10 = 31{,}25$ min. CT $= 31{,}25 + 10 = 41{,}25$ min.
WIP $= 41{,}25/12 = 3{,}44$ piezas. (b) Con fallas: $V = (1 + 2{,}25)/2 = 1{,}625$;
$W_q = 81{,}25$ min, CT $= 91{,}25$ min y WIP $= 7{,}60$ piezas: el WIP se duplica sin que cambie la
utilización. (c) Con 9 minutos: $u = 0{,}75$ y $U = 3$; $W_q = 0{,}625 \cdot 3 \cdot 9 = 16{,}88$ min; CT $= 25{,}88$ min; WIP $= 2{,}16$ piezas. Bajar el proceso un 10 % baja la espera un 46 %:
cerca del 100 %, cada minuto de capacidad vale mucho.

**11.7.** (a) $r_b = 60/20 = 3$ por hora; $T_0 = 48$ min $= 0{,}8$ h; $W_0 = 3 \times 0{,}8 = 2{,}4$.
(b) TH en unidades por hora y CT en horas:

| $w$ | Mejor (TH · CT) | Peor (TH · CT) | Peor práctico (TH · CT) |
|---|---|---|---|
| 2 | 2,50 · 0,80 | 1,25 · 1,60 | 1,76 · 1,13 |
| 5 | 3,00 · 1,67 | 1,25 · 4,00 | 2,34 · 2,13 |
| 10 | 3,00 · 3,33 | 1,25 · 8,00 | 2,63 · 3,80 |

(c) $\text{CT} = 10/2{,}1 = 4{,}76$ h. Saca menos que el peor caso práctico (2,63) con el mismo WIP:
la línea está en la zona «mala». Tiene variabilidad o pérdidas evitables (lotes, fallas, cuello
desabastecido). Además, con 10 unidades lleva mucho más WIP que el crítico (2,4): bajar el WIP
acortaría el tiempo de ciclo casi sin perder salida.

**11.8.** (a) Picado $60/40 =$ 1,5 h · embutido $120/40 =$ 3,0 h · empaque $20/40 =$ 0,5 h. Total
$200/40 =$ 5 h. (b) $\text{WIP} = 40 \times 3 = 120$ unidades: hay que sacar 80. Se buscan en el
embutido, que concentra 60 % del WIP; si no es el cuello, ese inventario solo está esperando. Un
tope CONWIP de 120 unidades lo logra sin bajar la salida, siempre que 120 siga sobre el WIP crítico.

**11.9.** (a) Tramos de llegada: 00 a 14 → 4 · 15 a 39 → 6 · 40 a 74 → 8 · 75 a 99 → 10. Tramos de
pesaje: 00 a 29 → 5 · 30 a 74 → 7 · 75 a 99 → 9. Entre llegadas: 8, 4, 10, 6, 8, 10, 6, 8, 10, 6.
Pesajes: 5, 7, 9, 7, 5, 9, 7, 7, 7, 5.

| Reloj | Evento | Servidor | En cola | Entra a atención (esperó) | Atendidos |
|---|---|---|---|---|---|
| 8 | Llega C1 | 1 | 0 | C1 (0) | 0 |
| 12 | Llega C2 | 1 | 1 | — | 0 |
| 13 | Sale C1 | 1 | 0 | C2 (1) | 1 |
| 20 | Sale C2 | 0 | 0 | — | 2 |
| 22 | Llega C3 | 1 | 0 | C3 (0) | 2 |
| 28 | Llega C4 | 1 | 1 | — | 2 |
| 31 | Sale C3 | 1 | 0 | C4 (3) | 3 |
| 36 | Llega C5 | 1 | 1 | — | 3 |
| 38 | Sale C4 | 1 | 0 | C5 (2) | 4 |
| 43 | Sale C5 | 0 | 0 | — | 5 |
| 46 | Llega C6 | 1 | 0 | C6 (0) | 5 |
| 52 | Llega C7 | 1 | 1 | — | 5 |
| 55 | Sale C6 | 1 | 0 | C7 (3) | 6 |
| 60 | Llega C8 | 1 | 1 | — | 6 |
| 62 | Sale C7 | 1 | 0 | C8 (2) | 7 |
| 69 | Sale C8 | 0 | 0 | — | 8 |
| 70 | Llega C9 | 1 | 0 | C9 (0) | 8 |
| 76 | Llega C10 | 1 | 1 | — | 8 |
| 77 | Sale C9 | 1 | 0 | C10 (1) | 9 |
| 82 | Sale C10 | 0 | 0 | — | 10 |

(b) Dura 82 min. Utilización: $68/82 = 82{,}9\ \%$. Espera: $12/10 = 1{,}2$ min; máxima 3 min.
$L_q = 12/82 = 0{,}15$; $\lambda = 10/82$ y $\lambda W_q = 0{,}122 \times 1{,}2 = 0{,}15$. Little se
cumple. (c) Llegadas: media 7,4 min, $c_a = 0{,}27$. Pesaje: media 6,9 min, $c_e = 0{,}21$.
$u = 6{,}9/7{,}4 = 93{,}2\ \%$. Kingman: $W_q \approx \frac{0{,}27^2 + 0{,}21^2}{2} \cdot \frac{0{,}932}{0{,}068} \cdot 6{,}9 = 5{,}7$ min.
(d) En la corrida salieron llegadas algo más espaciadas que el promedio y la romana partió vacía
(los primeros 8 minutos no tuvo nada que pesar), así que trabajó al 82,9 % y no al 93,2 %, y la espera fue de 1,2 min contra 5,7 de largo plazo. Diez
camiones no bastan para concluir nada. Con 93,2 % la romana **no sobra**: está cerca del límite, y
una temporada con más camiones (o un pesaje que se alarga) haría crecer la fila muy rápido.

**11.10.** (a) Estación 1: $u_1 = 0{,}8$, $W_{q1} = \frac{1 + 1{,}44}{2} \cdot 4 \cdot 8 = 39{,}04$
min. Salidas: $c_d^2 = 0{,}64 \cdot 1{,}44 + 0{,}36 \cdot 1 = 1{,}2816$. Estación 2: $u_2 = 0{,}9$,
$W_{q2} = \frac{1{,}2816 + 0{,}36}{2} \cdot 9 \cdot 9 = 66{,}48$ min. CT
$= 39{,}04 + 8 + 66{,}48 + 9 = 122{,}52$ min y WIP $= 122{,}52/10 = 12{,}25$ trabajos.
(b)

| Opción | Espera 1 | Espera 2 | Tiempo de ciclo | WIP |
|---|---|---|---|---|
| Hoy | 39,04 | 66,48 | 122,52 min | 12,25 |
| A · menos variabilidad en el lavado | 21,76 | 38,49 | 77,25 min | 7,73 |
| B · inspección más rápida | 39,04 | 26,27 | 81,31 min | 8,13 |

Gana **A**, aunque no toca la inspección (la estación más cargada). Con $c_e = 0{,}6$ las salidas
del lavado bajan a $c_d^2 = 0{,}5904$, y eso baja también la espera de la inspección. La
variabilidad que se corta arriba se ahorra dos veces.

---

## 12. Caso integrador · Estampa Sur, la semana 6 en el piso

> Este caso sigue a Estampa Sur por todo el ramo. Acá se miden las dos secuencias que comparó la
> unidad 10 para la semana 6. Si no has hecho esa unidad, parte de estos datos.

Las cinco órdenes de la semana 6 pasan por estampado y después por planchado y doblado (horas):

| Orden | OP-61 | OP-62 | OP-63 | OP-64 | OP-65 |
|---|---|---|---|---|---|
| Estampado | 6 | 9 | 11 | 3 | 4 |
| Planchado | 4 | 5 | 3 | 6 | 2 |

Johnson ordena OP-64, OP-62, OP-61, OP-63, OP-65 y EDD ordena OP-64, OP-61, OP-63, OP-62, OP-65.
Todas las órdenes se liberan el lunes a las 8:00 (hora 0).

**Pregunta.** Para cada secuencia: ¿cuánto WIP hay en el taller, cuánto sale por hora y cuánto
tarda una orden? ¿Dónde se acumula el trabajo? ¿Qué cambiaría si las órdenes se liberaran recién
cuando el estampado las toma?

**Desarrollo.** El tiempo en taller de cada orden es la hora en que sale del planchado.

| Orden (Johnson) | OP-64 | OP-62 | OP-61 | OP-63 | OP-65 |
|---|---|---|---|---|---|
| Estampado | 0–3 | 3–12 | 12–18 | 18–29 | 29–33 |
| Planchado | 3–9 | 12–17 | 18–22 | 29–32 | 33–35 |

| Orden (EDD) | OP-64 | OP-61 | OP-63 | OP-62 | OP-65 |
|---|---|---|---|---|---|
| Estampado | 0–3 | 3–9 | 9–20 | 20–29 | 29–33 |
| Planchado | 3–9 | 9–13 | 20–23 | 29–34 | 34–36 |

Con Little sobre el intervalo de la semana (empieza y termina vacío, así que se cumple exacto):

| | Johnson | EDD |
|---|---|---|
| Makespan | 35 h | 36 h |
| Tiempo en taller promedio (CT) | $115/5 =$ 23,0 h | $115/5 =$ 23,0 h |
| Throughput (TH) | $5/35 =$ 0,143 órdenes/h | $5/36 =$ 0,139 órdenes/h |
| WIP promedio | $115/35 =$ 3,29 órdenes | $115/36 =$ 3,19 órdenes |
| Espera promedio antes del estampado | 12,4 h | 12,2 h |
| Órdenes esperando el estampado (promedio) | 1,77 | 1,69 |
| Espera promedio antes del planchado | 0,0 h | 0,2 h |
| Órdenes esperando el planchado (promedio) | 0,00 | 0,03 |
| Utilización del estampado | 94,3 % | 91,7 % |
| Utilización del planchado | 57,1 % | 55,6 % |

Comprobación de Little con Johnson: $\text{TH} \times \text{CT} = 0{,}143 \times 23{,}0 = 3{,}29$.

**Liberar justo a tiempo.** Si cada orden entra al taller recién cuando el estampado la toma, el
tiempo en taller se mide desde ese inicio. Con Johnson queda en 10,6 h promedio y el WIP en 1,51
órdenes; con EDD, 10,8 h y 1,50 órdenes. El makespan y el TH no cambian: es la misma secuencia.

**Lectura.**

- El trabajo se acumula **frente al estampado**, no frente al planchado. El estampado es el cuello
  (94,3 % de utilización con Johnson); el planchado espera trabajo más de lo que el trabajo lo
  espera a él (privación).
- Soltar las cinco órdenes el lunes no adelanta nada: el TH lo pone el estampado. Solo infla el WIP
  (3,29 contra 1,51) y el tiempo en taller (23,0 contra 10,6 h). Es Little: con el mismo TH, menos
  WIP es menos tiempo de ciclo. En la práctica, liberar tarde significa que las prendas lisas y las
  tintas no ocupan mesas ni se ensucian esperando.
- Johnson y EDD dan el mismo tiempo promedio en taller (23,0 h). La diferencia entre ellas está en
  las fechas (unidad 10), no en el flujo.
- **Una alerta para la unidad 9.** La unidad 10 supuso el planchado disponible toda la semana. Con
  la media jornada que considera la unidad 9 (18 h), la carga de 20 h da $u = 20/18 = 1{,}11$: el
  planchado sería inestable esa semana y la cola crecería hacia la semana 7. Con un estampado al
  94 % y un planchado sobre 100 %, la semana 6 necesita horas extra en el planchado o mover una
  orden.

---

## 13. Para seguir

**En los libros del ramo.**

- Hopp y Spearman, *Factory Physics* (2.ª ed., 2001), la bibliografía complementaria que fija el
  programa para la Unidad VII: ley de Little, mejor y peor caso, variabilidad, Kingman y la ley de
  los buffers. Es la fuente de esta unidad.
- Chase, Jacobs y Aquilano, *Administración de operaciones* (12.ª ed., 2009), capítulo 5 (medición
  del desempeño del proceso y ley de Little) y los capítulos de filas de espera y de simulación.
- Goldratt y Cox, *La meta*: el cuello de botella, los buffers y por qué soltar trabajo de más no
  sube la producción.

**Abiertos y gratis.**

- Abbas y Goosheh, *Operations Management*, Fanshawe College (2025), en inglés, los capítulos de
  análisis de procesos y de filas de espera. Descarga en la colección abierta de Ontario:
  https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/2473

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame tiempos entre llegadas y de servicio
para seis clientes, déjame armar la tabla de eventos y corrígeme fila por fila».
