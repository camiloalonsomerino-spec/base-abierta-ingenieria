---
ramo: Gestión de Operaciones
unidad: 3
titulo: Proceso y capacidad
version: 0.1 (15-10-2026)
requiere: [01-introduccion-y-productividad, 02-estrategia-de-operaciones]
alimenta: [09-capacidad-aproximada, 11-fisica-de-la-fabrica]
verificacion: verificacion/u03_proceso_capacidad.py
---

# Unidad 3 · Proceso y capacidad

**Qué vas a poder hacer.** Reconocer qué tipo de proceso conviene según el volumen y la variedad;
encontrar el cuello de botella de una línea y su tiempo de ciclo; calcular el ritmo que pide la
demanda; medir la utilización y la eficiencia de una instalación y estimar su producción esperada;
y evaluar una ampliación de capacidad con un árbol de decisión.

**Lo que necesitas antes.** Productividad (unidad 1) y prioridades competitivas (unidad 2). De
probabilidad basta el valor esperado: $E[X] = \sum p_i x_i$.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. La idea

Un **proceso** es cualquier parte de una organización que recibe insumos (materiales, personas,
máquinas, información) y los transforma en un producto o servicio que vale más que los insumos.

Diseñar el proceso es decidir **cómo** se produce. Esa decisión fija buena parte de la estrategia:
un proceso flexible y caro no compite en precio, y una línea rígida y barata no atiende pedidos a
la medida. Dos preguntas ordenan la unidad:

1. **¿Qué forma tiene el proceso?** Depende del volumen y de la variedad (sección 2).
2. **¿Cuánto puede producir?** Es la capacidad: cuánto se puede hacer, cuánto se espera hacer y
   cuánto se hizo de verdad (secciones 3 a 6).

---

## 2. Tipos de proceso

| Enfoque | Volumen y variedad | Cómo se organiza | Costos típicos | Ejemplo |
|---|---|---|---|---|
| **En el proceso** (taller de trabajo y por lotes) | bajo volumen, alta variedad | por departamentos que hacen una actividad (soldar, pintar) | variables altos, utilización baja | maestranza, imprenta a pedido |
| **Repetitivo** | volumen medio | línea con módulos preparados antes; a veces en células | intermedios | armado de bicicletas, comida rápida |
| **En el producto** (continuo) | alto volumen, poca variedad | alrededor del producto, corridas largas | fijos altos, variables bajos | celulosa, azúcar, cerveza industrial |
| **Personalización masiva** | alto volumen y alta variedad | módulos que se combinan a pedido, rápido y barato | depende de la modularidad | zapatillas armadas en una web |

Dentro del enfoque en el proceso hay dos variantes. El **taller de trabajo** (*job shop*) hace
cada pedido según lo que pidió el cliente, en lotes pequeños. El **proceso por lotes** (*batch*)
mueve paquetes de producto juntos de un centro al siguiente.

Una **célula de trabajo** junta en un grupo a personas y máquinas que antes estaban repartidas en
varios departamentos, para que se dediquen a una familia de productos. Se usa con volúmenes medios.

**Cuándo se activa el proceso.**

- **Fabricación a pedido (MTO):** se produce solo cuando llega una orden. El WIP y el inventario de
  producto terminado se mantienen al mínimo.
- **Fabricación contra stock (MTS):** se produce según un pronóstico y el cliente se atiende desde
  el inventario.

> **La regla de la diagonal.** Mientras más volumen y menos variedad, más conviene organizarse
> alrededor del producto. Una empresa que queda fuera de la diagonal (una línea continua para
> pedidos únicos, o un taller artesanal para un millón de unidades) paga el error cada minuto que
> opera.

---

## 3. Medir un proceso

### Tiempos de una operación

- **Tiempo de preparación:** lo que tarda dejar la máquina lista para un artículo (cambio de marco,
  de molde, limpieza).
- **Tiempo de corrida:** lo que tarda producir el lote.
- **Tiempo de operación** $=$ preparación $+$ corrida. La preparación se paga una vez por lote: con
  lotes más grandes, cada unidad carga menos preparación.

### Ritmo, cuello de botella y tiempo de rendimiento

Una etapa con tiempo $t$ por unidad y $m$ estaciones iguales en paralelo produce a una tasa

$$r = \frac{m}{t}$$

En una línea en serie, la etapa de menor tasa es el **cuello de botella**: fija la tasa de toda la
línea. El **tiempo de ciclo de la línea** es el tiempo entre dos unidades que salen, y es igual al
tiempo por unidad del cuello: $1/r_{\text{cuello}}$.

El **tiempo de ciclo requerido** (también se le dice *takt*) es el ritmo que pide la demanda:

$$C = \frac{\text{tiempo disponible}}{\text{unidades requeridas}}$$

La línea cumple si su tiempo de ciclo es menor o igual que $C$. Si una tarea suma un contenido de
trabajo $W$, se necesitan al menos $\lceil W / C \rceil$ estaciones.

El **tiempo de rendimiento** (*throughput time*) es lo que tarda una unidad en recorrer el proceso:
el tiempo de proceso más el tiempo que espera en las filas. La **tasa de rendimiento** es cuántas
unidades salen por período. Las dos se conectan con la ley de Little (unidad 11).

Para bajar el tiempo de rendimiento: hacer actividades **en paralelo**, cambiar la secuencia y
reducir las interrupciones.

### Palabras que se usan en el piso

| Término | Qué significa |
|---|---|
| **Buffer** | un área de almacenamiento entre dos etapas, donde espera lo que sale de una antes de entrar a la otra |
| **Bloqueo** | una etapa se detiene porque no tiene dónde dejar lo que terminó |
| **Privación** | una etapa se detiene porque no le llega trabajo |
| **Cuello de botella** | la etapa de capacidad limitada donde el trabajo se apila |
| **Ritmo** | el tiempo fijo con que los artículos avanzan por el proceso |

Herramientas para analizar un proceso: diagramas de flujo, gráficas de función-tiempo (el flujo con
el tiempo en el eje horizontal), mapas del flujo de valor y diagramas de proceso. Todas buscan lo
mismo: pasos que no agregan valor, duplicidades y esperas.

---

## 4. Capacidad

La **capacidad** es cuánto puede producir, recibir o atender una instalación en un período. Hay
tres cifras distintas:

| Capacidad | Qué es |
|---|---|
| **De diseño** | el máximo teórico en condiciones ideales: horas disponibles × tasa de diseño |
| **Efectiva** | lo que se espera lograr con las restricciones actuales (cambios de producto, mantención, mezcla) |
| **Real** (producción real) | lo que de verdad se produjo |

Con ellas se miden dos razones:

$$\text{Utilización} = \frac{\text{producción real}}{\text{capacidad de diseño}} \qquad \text{Eficiencia} = \frac{\text{producción real}}{\text{capacidad efectiva}}$$

Y si se conoce la eficiencia (de otra línea, de un período anterior), se estima lo que va a salir:

$$\text{Producción esperada} = \text{capacidad efectiva} \times \text{eficiencia}$$

Lo normal es real $\le$ efectiva $\le$ diseño, así que la utilización es menor que la eficiencia.
Que una planta no trabaje al 100 % de su diseño no es un defecto: opera mejor cuando no estira
sus recursos hasta el límite (la unidad 11 muestra por qué la fila explota cerca del 100 %).

---

## 5. Planificar la capacidad

La demanda suele crecer de a poco; la capacidad crece a saltos (una máquina, una línea, una nave).
Por eso siempre hay períodos con capacidad de sobra o de menos. La planificación sigue tres pasos:

1. Pronosticar la demanda de cada producto (unidad 4).
2. Traducirla a horas de equipo y de personas.
3. Comparar con lo que habrá disponible en el horizonte.

**Tácticas para ajustar la capacidad a la demanda:** cambiar el personal (contratar, despedir,
turnos), ajustar el equipo (comprar, arrendar, vender), mejorar el proceso, rediseñar el producto
para que se fabrique más rápido, ganar flexibilidad o cerrar instalaciones.

**En servicios** también se puede mover la demanda: citas, reservas, descuentos en horas valle.

**Economías y deseconomías de escala.** Una instalación más grande baja el costo por unidad hasta
un punto; pasado ese punto, la coordinación y la congestión lo vuelven a subir.

---

## 6. Árbol de decisión

Cuando la demanda futura es incierta, las alternativas de capacidad se comparan con un árbol:

- Un **nodo de decisión** (cuadrado) es una elección del dueño.
- Un **nodo de azar** (círculo) es algo que no controla, con sus probabilidades.
- Al final de cada rama va el resultado (ingresos menos costos del horizonte).

Se resuelve **de derecha a izquierda**. En cada nodo de azar se calcula el **valor monetario
esperado** (VME); en cada nodo de decisión se elige la rama de mayor VME y se «podan» las demás.

$$\text{VME} = \sum_i p_i \cdot \text{resultado}_i$$

Una decisión puede tener **dos etapas**: esperar, mirar qué pasó y recién decidir. Esperar vale
porque llega información; cuesta porque se pierde lo que se habría ganado mientras tanto. El árbol
pone las dos cosas en la misma balanza.

Acá no se descuentan los flujos (todos los años pesan igual). Con horizontes largos se descuentan
con la tasa de la empresa, como en Finanzas (valor actual neto).

---

## 7. Ejemplo resuelto · Mermeladas del Laja

Mermeladas del Laja envasa mermelada en Los Ángeles y vende a supermercados contra stock. Su línea
de envasado tiene cuatro etapas en serie:

| Etapa | Tiempo por frasco | Estaciones |
|---|---|---|
| Lavado de frascos | 3,0 s | 1 |
| Llenado | 7,2 s | 2 en paralelo |
| Tapado | 3,2 s | 1 |
| Etiquetado | 4,0 s | 1 |

La línea opera 6 días a la semana, 2 turnos de 8 horas. Un contrato nuevo exige 72.000 frascos
por semana. La capacidad efectiva (descontando cambios de sabor y limpieza) es de 78.000 frascos
por semana y la semana pasada salieron 64.740.

**Paso 1 · Tipo de proceso.** Volumen alto, cuatro sabores, mismo recorrido para todos: es un
proceso **repetitivo** que fabrica **contra stock**.

**Paso 2 · Cuello de botella.** Tasa de cada etapa, $r = 3.600 \cdot m / t$ por hora:

| Etapa | Tasa |
|---|---|
| Lavado | 1.200 frascos/h |
| Llenado | 1.000 frascos/h |
| Tapado | 1.125 frascos/h |
| Etiquetado | 900 frascos/h |

El cuello es el **etiquetado**: la línea saca 900 frascos por hora y su tiempo de ciclo es de 4,0
segundos. El llenado, que es la etapa más lenta por frasco (7,2 s), no es el cuello porque tiene dos
llenadoras. Un frasco que no espera en ninguna fila recorre la línea en $3{,}0 + 7{,}2 + 3{,}2 + 4{,}0 = 17{,}4$ s.

**Paso 3 · ¿El diseño alcanza para el contrato?** Horas por semana: $6 \times 2 \times 8 = 96$ h,
es decir, 345.600 segundos.

$$C = \frac{345.600 \text{ s}}{72.000 \text{ frascos}} = 4{,}8 \text{ s}$$

El tiempo de ciclo de la línea (4,0 s) es menor que el requerido (4,8 s): **por diseño, alcanza**.

**Paso 4 · Utilización y eficiencia.** Capacidad de diseño: $96 \times 900 = 86.400$ frascos por
semana.

$$\text{Utilización} = \frac{64.740}{86.400} = 74{,}9\ \% \qquad \text{Eficiencia} = \frac{64.740}{78.000} = 83{,}0\ \%$$

**Cómo se lee.** El diseño sobra, pero lo real no: faltaron 7.260 frascos para el contrato. Para
llegar a 72.000 con la capacidad efectiva actual, la eficiencia tendría que subir a
${72.000} / 78.000 = 92{,}3\ \%$. El problema no es de diseño sino de pérdidas: antes de comprar
otra máquina, hay que mirar por qué se pierden horas.

**Paso 5 · ¿Una segunda línea?** El dueño evalúa tres opciones para los próximos 4 años, sin
descontar. La probabilidad de que la cadena de supermercados amplíe el contrato (demanda alta) es
0,4. Montos en millones de pesos:

| Opción | Inversión | Flujo anual con demanda alta | Flujo anual con demanda baja |
|---|---|---|---|
| Comprar una segunda línea ahora | 60 | 55 | 14 |
| Arrendar una línea | 8 (instalación) | 22 | 6 |
| Esperar un año | 0 | 16 | 12 |

Si espera y la demanda resulta alta, al inicio del año 2 puede comprar la línea (ahora cuesta 68,
y le quedan 3 años con flujo de 55) o seguir igual (16 por año).

```
                        alta 0,4   4×55 − 60 = 160
         Comprar ──( )─┤
        /               baja 0,6   4×14 − 60 =  −4
       /                alta 0,4   4×22 − 8  =  80
[ ]── Arrendar ──( )──┤
       \                baja 0,6   4×6  − 8  =  16
        \               alta 0,4   16 + [ ] ┬ comprar: −68 + 3×55 = 97
         Esperar ─( )─┤                     └ seguir:  3×16       = 48
                        baja 0,6   4×12      =  48
```

Se resuelve de derecha a izquierda. En la rama «esperar, demanda alta» el dueño compra (97 contra
48), así que esa rama vale $16 + 97 = 113$.

$$\text{VME}_{\text{comprar}} = 0{,}4 \cdot 160 + 0{,}6 \cdot (-4) = 61{,}6$$
$$\text{VME}_{\text{arrendar}} = 0{,}4 \cdot 80 + 0{,}6 \cdot 16 = 41{,}6$$
$$\text{VME}_{\text{esperar}} = 0{,}4 \cdot 113 + 0{,}6 \cdot 48 = 74{,}0$$

**Cómo se lee.** Conviene **esperar un año**: VME de 74,0 millones contra 61,6 de comprar ahora.
Comprar de inmediato gana si la demanda sube (160 contra 113), pero pierde 4 millones si no sube.
Esperar evita ese riesgo y deja la compra abierta. Además, el paso 4 ya decía que la línea actual
tiene diseño de sobra: primero se recuperan las horas perdidas.

---

## 8. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Tomar como cuello la etapa con mayor tiempo por unidad | Divide por las estaciones en paralelo: manda la menor **tasa**, no el mayor tiempo |
| Confundir el tiempo de ciclo de la línea con el requerido | El de la línea sale del cuello; el requerido sale de la demanda. Se comparan |
| Calcular la utilización contra la capacidad efectiva | Utilización contra diseño; eficiencia contra efectiva |
| Multiplicar la eficiencia por la capacidad de diseño | La producción esperada es **efectiva** × eficiencia |
| Redondear hacia abajo el número de estaciones | $\lceil W/C \rceil$: 4,17 estaciones son 5 |
| Resolver el árbol de izquierda a derecha | Primero los nodos del final; en cada decisión se queda la mejor rama |
| Sumar la inversión una vez por año | La inversión se resta una sola vez; el flujo se multiplica por los años |

---

## 9. Práctica

Diez ejercicios: 3.1 a 3.4 básicos, 3.5 a 3.8 intermedios, 3.9 y 3.10 de desafío. Las pautas
están en la sección 10. Intenta cada uno antes de mirarla.

**3.1 · Empanadas congeladas (básico).** Una planta de Chillán debe producir 2.250 empanadas en un
turno de 7,5 horas. Armar una empanada suma 50 segundos de trabajo. (a) Calcula el tiempo de ciclo
requerido. (b) ¿Cuántas estaciones necesita, como mínimo? (c) Si el pedido sube a 2.700 empanadas
por turno, ¿cuánto queda el tiempo de ciclo y cuántas estaciones hacen falta?

**3.2 · Lavandería industrial (básico).** Una lavandería de Talcahuano opera 6 días a la semana,
2 turnos de 7 horas, y fue diseñada para lavar 250 kg por hora. Su capacidad efectiva es de 18.500
kg por semana y la semana pasada lavó 15.910 kg. Calcula la capacidad de diseño, la utilización y
la eficiencia, e interpreta la diferencia entre las dos.

**3.3 · ¿Qué proceso es? (básico).** Clasifica cada caso según el enfoque (proceso, repetitivo,
producto o personalización masiva) y di si fabrica a pedido o contra stock. (a) Una imprenta que
hace tarjetas de presentación con el diseño de cada cliente. (b) Una planta que produce azúcar de
remolacha todo el día durante la temporada. (c) Una línea que arma bicicletas de tres modelos con
piezas preparadas antes. (d) Una marca que vende zapatillas que el cliente combina en una web y
recibe en una semana. (e) Un taller de mantención de camiones.

**3.4 · Lavado de autos (básico).** Un lavado tiene cuatro etapas en serie. Calcula la tasa por
hora de cada etapa, el cuello de botella, cuántos autos atiende como máximo en 8 horas y el tiempo
de rendimiento de un auto que no espera. Luego: si se agrega un segundo secador, ¿cuánto sube la
capacidad?

| Etapa | Minutos por auto | Puestos |
|---|---|---|
| Prelavado | 4 | 1 |
| Lavado | 6 | 2 |
| Secado | 5 | 1 |
| Aspirado | 8 | 2 |

**3.5 · Planta de jugos (intermedio).** Una línea de jugos tiene una capacidad efectiva de 30.000
litros por semana y trabaja con una eficiencia de 82 %. Se instala una segunda línea igual, de la
que se espera una eficiencia de 76 % al principio. (a) Producción esperada de cada línea y total.
(b) Tras la capacitación, las dos llegan a 88 %: ¿cuánto producen? (c) Si la demanda sube a
70.000 litros por semana, ¿cuántas líneas como esas (al 88 %) se necesitan?

**3.6 · Plegadora CNC (intermedio).** Una maestranza de Coronel tiene una plegadora con 40 minutos
de preparación por lote y 1,5 minutos de corrida por pieza. Trabaja 40 horas a la semana. Compara
lotes de 60 y de 120 piezas: tiempo de operación del lote, minutos por pieza y piezas por semana
(en promedio). ¿Cuánto sube la producción con el lote grande? ¿Qué se paga a cambio?

**3.7 · Catering (intermedio).** Un pedido de catering pasa por picar (12 min), cocer (20 min),
armar (8 min) y empacar (5 min). (a) Tiempo de rendimiento si todo va en serie. (b) Picar y cocer
no dependen entre sí: si se hacen en paralelo, ¿cuánto queda y cuánto baja, en porcentaje? (c) Si
cada pedido espera en promedio 15 minutos antes de armar, ¿cuál es el tiempo de rendimiento con la
mejora?

**3.8 · Clínica dental (intermedio).** Una clínica de Temuco evalúa tres opciones para los
próximos 3 años. La demanda puede ser alta (0,3), media (0,5) o baja (0,2). Montos en millones de
pesos. Arma el árbol, calcula el VME de cada opción y recomienda.

| Opción | Inversión | Flujo anual alta | Flujo anual media | Flujo anual baja |
|---|---|---|---|---|
| Segundo sillón | 18 | 20 | 12 | 5 |
| Ampliar horario | 4 | 14 | 10 | 6 |
| No hacer nada | 0 | 9 | 8 | 6 |

**3.9 · Planta de pellets, el cuello que se mueve (desafío).** Una planta de pellets de madera
tiene cuatro etapas en serie y opera 120 horas a la semana. La demanda es de 230 toneladas por
semana.

| Etapa | Secado | Prensado | Enfriado | Ensacado |
|---|---|---|---|---|
| Tasa (t/h) | 2,0 | 1,6 | 2,4 | 1,8 |

(a) ¿Cuánto produce hoy y dónde está el cuello? (b) Se compra una segunda prensa usada que agrega
0,8 t/h al prensado: ¿cuánto produce ahora y dónde quedó el cuello? (c) Además se agrega una
ensacadora de 1,2 t/h: ¿alcanza la demanda? (d) Produciendo exactamente las 230 toneladas, ¿qué
utilización tiene cada etapa? ¿Cuál vigilarías?

**3.10 · Cervecería, esperar o invertir (desafío).** Una cervecería de Puerto Varas evalúa comprar
fermentadores para los próximos 3 años (millones de pesos, sin descontar).

- **A · Comprar ahora:** cuesta 30. Flujo anual de 30 si el mercado crece y de 9 si no crece.
- **B · Esperar un año:** el primer año gana 12 si crece y 10 si no. Si creció, al inicio del año 2
  decide entre comprar (cuesta 32 y da 30 por año los 2 años que quedan) o seguir sin comprar (12
  por año). Si no creció, sigue con 10 por año.

(a) Con probabilidad de crecer $p = 0{,}5$, calcula el VME de A y B. (b) Escribe los dos VME en
función de $p$ y encuentra la probabilidad con que da lo mismo. (c) ¿Qué decides con $p = 0{,}7$?

---

## 10. Pautas

**3.1.** (a) $C = 7{,}5 \cdot 3.600 / 2.250 = 27.000 / 2.250 = 12$ s. (b) $50 / 12 = 4{,}17$: se
necesitan **5 estaciones** (4 no alcanzan). (c) $C = 27.000 / 2.700 = 10$ s y $50/10 = 5$: siguen
bastando 5 estaciones, ahora sin holgura. Cualquier pérdida de ritmo deja el pedido corto.

**3.2.** Horas por semana: $6 \times 2 \times 7 = 84$ h. Capacidad de diseño: $84 \times 250 = 21.000$ kg.
Utilización: ${15.910} / 21.000 = 75{,}8\ \%$. Eficiencia: ${15.910} / 18.500 = 86{,}0\ \%$. La
lavandería rinde bien contra lo que se puede esperar hoy (86 %), pero usa solo tres cuartos de lo
que permite su diseño. La brecha entre las dos cifras son restricciones del día a día (cambios de
programa, mantención), no flojera del personal.

**3.3.** (a) Enfoque en el proceso (taller de trabajo), a pedido. (b) Enfoque en el producto
(continuo), contra stock. (c) Repetitivo, contra stock. (d) Personalización masiva, a pedido.
(e) Enfoque en el proceso (taller de trabajo), a pedido: cada camión trae una falla distinta.

**3.4.** Tasas: prelavado $60/4 =$ 15 autos/h · lavado $2 \cdot 60/6 =$ 20 autos/h · secado
$60/5 =$ 12 autos/h · aspirado $2 \cdot 60/8 =$ 15 autos/h. Cuello: **secado**, con 12 autos por
hora, es decir, 96 autos en 8 horas. Tiempo de rendimiento sin espera: $4+6+5+8 =$ 23 min. Con un
segundo secador, el secado sube a 24 autos/h y el nuevo cuello es compartido entre prelavado y
aspirado (15 por hora): la capacidad sube 25 %, no 100 %. Para seguir creciendo hay que mover las
dos etapas a la vez.

**3.5.** (a) Línea 1: ${30.000} \times 0{,}82 =$ 24.600 L. Línea 2: ${30.000} \times 0{,}76 =$ 22.800 L.
Total: 47.400 L. (b) $2 \times 30.000 \times 0{,}88 =$ 52.800 L, es decir, 26.400 L por línea.
(c) ${70.000} / 26.400 = 2{,}65$: se necesitan **3 líneas**. La tercera queda con holgura, que sirve
para absorber la variabilidad (unidad 11) o para crecer.

**3.6.**

| Lote | Tiempo de operación | Minutos por pieza | Piezas por semana |
|---|---|---|---|
| 60 | $40 + 1{,}5 \cdot 60 =$ 130 min | 2,17 min | 1.108 piezas |
| 120 | $40 + 1{,}5 \cdot 120 =$ 220 min | 1,83 min | 1.309 piezas |

Piezas por semana $= 2.400 / \text{minutos por pieza}$. El lote de 120 produce 18,2 % más, porque
la preparación se reparte entre más piezas. A cambio, cada lote tarda más en salir y hay más piezas
esperando entre etapas: más WIP y más tiempo de rendimiento (unidad 11).

**3.7.** (a) En serie: $12 + 20 + 8 + 5 =$ 45 min. (b) En paralelo: $\max(12, 20) + 8 + 5 =$ 33 min,
una baja de 26,7 %. Picar desaparece del camino crítico porque ocurre mientras se cuece. (c) Con la
espera: $33 + 15 =$ 48 min. La espera pesa casi la mitad de lo que se ganó en el diseño: muchas
veces se baja más el tiempo de rendimiento atacando las filas que los tiempos de proceso.

**3.8.** Flujo anual esperado: sillón $0{,}3 \cdot 20 + 0{,}5 \cdot 12 + 0{,}2 \cdot 5 = 13{,}0$ ·
horario $10{,}4$ · nada $7{,}9$. VME a 3 años, menos la inversión:

| Opción | VME (millones de pesos) |
|---|---|
| Segundo sillón | $3 \cdot 13{,}0 - 18 = 21{,}0$ |
| Ampliar horario | $3 \cdot 10{,}4 - 4 = 27{,}2$ |
| No hacer nada | $3 \cdot 7{,}9 = 23{,}7$ |

Recomendación: **ampliar el horario** (27,2). El sillón tiene el mejor flujo anual, pero en 3 años
no alcanza a pagar su inversión. Si el horizonte fuera más largo, la respuesta podría cambiar.

**3.9.** (a) Capacidades semanales: secado 240 t, prensado 192 t, enfriado 288 t, ensacado 216 t.
Hoy produce 192 t; el cuello es el **prensado**. (b) Prensado a 2,4 t/h: la planta sube a 216 t y
el cuello pasa al **ensacado**. No alcanza. (c) Ensacado a 3,0 t/h: la planta sube a 240 t, con el
**secado** como cuello. Ahora sí alcanza. (d) Para 230 t se necesita una tasa de
$230 / 120 = 1{,}92$ t/h. Utilizaciones: secado 95,8 %, prensado 79,9 %, enfriado 79,9 %,
ensacado 63,9 %. Se vigila el **secado**: a casi 96 % cualquier detención se traduce en
toneladas perdidas, y la fila frente a él va a crecer mucho (unidad 11). La lección: invertir en
una etapa que no es el cuello no agrega ni una tonelada.

**3.10.** (a) $\text{VME}_A = 0{,}5 \cdot 3 \cdot 30 + 0{,}5 \cdot 3 \cdot 9 - 30 = 28{,}5$. En B, si creció:
comprar en el año 2 da $-32 + 2 \cdot 30 = 28$ y seguir da $2 \cdot 12 = 24$; conviene comprar,
y la rama vale $12 + 28 = 40$. Si no creció: $3 \cdot 10 = 30$.
$\text{VME}_B = 0{,}5 \cdot 40 + 0{,}5 \cdot 30 = 35{,}0$. Con $p = 0{,}5$ **conviene esperar**.
(b) $\text{VME}_A(p) = -3 + 63p$ y $\text{VME}_B(p) = 30 + 10p$. Se igualan en
$p = 33/53 = 0{,}62$. (c) Con $p = 0{,}7$: $\text{VME}_A = 41{,}1$ y $\text{VME}_B = 37{,}0$:
conviene **comprar ahora**. Lectura: esperar es un seguro contra el mercado que no crece. Cuando el
crecimiento es casi seguro, ese seguro cuesta más de lo que protege.

---

## 11. Caso integrador · Estampa Sur, la capacidad del estampado

> Este caso sigue a Estampa Sur por todo el ramo. Cada unidad parte de lo que calculó la anterior;
> acá se mide la capacidad de la máquina que después programan las unidades 9 y 10. Los datos de
> partida están en `verificacion/caso_estampa_sur.py`.

Estampa Sur es un taller de serigrafía textil del Biobío. Estampa poleras, polerones, bolsas y
gorros a pedido de colegios, clubes y eventos: un **taller de trabajo** que fabrica **a pedido**
(con un stock pequeño de poleras básicas).

**Datos del estampado.** Trabaja 5 días a la semana, 1 turno de 9 horas. Descontando cambios de
marco y limpieza, la capacidad efectiva es de 40 horas por semana. La última semana estampó 34
horas.

**Pregunta 1 · Utilización y eficiencia.**

$$\text{Diseño} = 5 \times 1 \times 9 = 45 \text{ h} \qquad \text{Utilización} = \frac{34}{45} = 75{,}6\ \% \qquad \text{Eficiencia} = \frac{34}{40} = 85{,}0\ \%$$

Si la eficiencia se mantiene, la producción esperada es $40 \times 0{,}85 = 34$ h por semana. La
semana 6 del programa maestro carga 33 h de estampado (unidad 9): alcanza, con una hora de margen.

**Pregunta 2 · ¿Una segunda máquina?** El dueño postula a una licitación de uniformes de una liga
escolar regional para los próximos 3 años. Cree que tiene 0,35 de probabilidad de ganarla. Evalúa
comprar un segundo pulpo de estampado (nuevo o usado) o no comprar:

| Opción | Inversión | Flujo anual si gana | Flujo anual si pierde |
|---|---|---|---|
| Comprar nueva | $9.500.000 | $7.800.000 | $3.100.000 |
| Comprar usada | $5.200.000 | $6.200.000 | $2.600.000 |
| No comprar | 0 | $3.400.000 | $2.400.000 |

**Desarrollo.** VME a 3 años, menos la inversión:

| Opción | VME (pesos) |
|---|---|
| Comprar nueva | $3 \cdot (0{,}35 \cdot 7{,}8 + 0{,}65 \cdot 3{,}1) \text{ millones} - 9{,}5 \text{ millones} =$ 4.735.000 |
| Comprar usada | $3 \cdot (0{,}35 \cdot 6{,}2 + 0{,}65 \cdot 2{,}6) \text{ millones} - 5{,}2 \text{ millones} =$ 6.380.000 |
| No comprar | $3 \cdot (0{,}35 \cdot 3{,}4 + 0{,}65 \cdot 2{,}4) \text{ millones} =$ 8.250.000 |

¿Desde qué probabilidad de ganar cambia la decisión? Cada diferencia de VME es lineal en $p$. La
usada le gana a no comprar desde $p = 0{,}59$; la nueva le gana a no comprar desde $p = 0{,}67$ y a
la usada desde $p = 0{,}85$.

**Lectura.** Con 0,35 de probabilidad, **no conviene comprar**: el VME de no comprar es de $8.250.000,
$1.870.000 más que la usada. Es coherente con la pregunta 1: el taller usa 34 de sus 45 horas
de diseño, así que tiene 11 horas de holgura antes de necesitar otra máquina. Si Estampa Sur llega a
creer que ganará la licitación con más de 59 % de probabilidad, la usada pasa a ser la mejor
opción. Antes de invertir, conviene recuperar eficiencia: cada punto de eficiencia son 0,4 horas de
estampado por semana sin comprar nada.

**Lo que pasa a las unidades siguientes.** La capacidad efectiva de 40 horas es la que usa la
unidad 9 para comparar la carga del estampado; la utilización y la variabilidad del taller vuelven
en la unidad 11.

---

## 12. Para seguir

**En los libros del ramo.**

- Chase, Jacobs y Aquilano, *Administración de operaciones* (12.ª ed., 2009), capítulo 5 (el que fija
  el programa para la Unidad III): tipos de proceso, medición del desempeño y capacidad.
- Heizer y Render, *Principios de administración de operaciones* (5.ª ed., 2004), los capítulos de
  estrategia de proceso y de planeación de la capacidad, con su suplemento de árboles de decisión.
  Sus problemas del final son buena práctica adicional.
- Goldratt y Cox, *La meta*: una novela sobre una planta que aprende a buscar su cuello de botella.

**Abiertos y gratis.**

- Abbas y Goosheh, *Operations Management*, Fanshawe College (2025), en inglés, los capítulos de
  diseño del proceso y de planificación de la capacidad. Descarga en la colección abierta de
  Ontario: https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/2473

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame una línea de cinco etapas con estaciones
en paralelo y pregúntame dónde está el cuello de botella».
