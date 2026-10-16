---
ramo: Optimización
unidad: 1
titulo: Investigación de operaciones y modelos
version: 0.1 (15-10-2026)
requiere: []
alimenta: [02-metodo-grafico, 04-modelamiento-produccion-y-mezcla]
verificacion: verificacion/u01_modelos.py
---

# Unidad 1 · Investigación de operaciones y modelos

**Qué vas a poder hacer.** Reconocer cuándo una decisión se puede optimizar; separar en un enunciado
lo que se decide de lo que está dado; escribir el modelo en palabras, en notación algebraica con
conjuntos e índices y en OPL; clasificarlo por tipo, y mostrar con números por qué una regla
intuitiva («primero lo más rentable») no reemplaza al modelo.

**Lo que necesitas antes.** Álgebra de enseñanza media y sumatorias ($\sum$). Nada del ramo: esta es
la primera unidad.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. Qué es la investigación de operaciones

La **investigación de operaciones** (IO) es la disciplina que usa modelos matemáticos para tomar
mejores decisiones. Su caja de herramientas tiene probabilidad y estadística, simulación, teoría de
colas y, sobre todo, **optimización**: elegir, entre todas las decisiones posibles, la que mejor
cumple un criterio.

**De dónde viene.** El nombre nace en la Segunda Guerra Mundial. En Gran Bretaña y luego en Estados
Unidos se formaron equipos de científicos (físicos, matemáticos, estadísticos) para estudiar
*operaciones* militares: dónde poner los radares, cómo organizar los convoyes, cómo buscar
submarinos. De ahí «operational research». Terminada la guerra, las mismas ideas pasaron a la
industria, y en 1947 George Dantzig formuló el método simplex para la programación lineal (lo verás
en la unidad 8). El computador hizo el resto: hoy se resuelven modelos con millones de variables.

**Casos de éxito.** Las aerolíneas arman sus turnos de tripulación y sus precios con modelos de
optimización; las cadenas de supermercados deciden con ellos qué bodega abastece a qué tienda. En
Chile hay dos casos documentados que conviene conocer:

- La **licitación de la alimentación escolar de la JUNAEB**, que adjudica los servicios de comida de
  los colegios con un modelo de programación entera (Epstein y coautores, revista *Interfaces*, 2002).
- Las **herramientas de análisis para enfrentar la pandemia de COVID-19** (búsqueda activa de casos,
  asignación de pacientes entre hospitales, seguimiento de la movilidad), que ganaron el premio
  Franz Edelman de INFORMS en 2022. Participaron los ministerios de Salud y de Ciencia, el Instituto
  Sistemas Complejos de Ingeniería (ISCI) y Entel.

Las cifras de ahorro que publican estos casos son estimaciones de sus autores. Para el ramo basta
con lo esencial: en ambos, alguien escribió **qué se decide, qué se busca y qué limita**, y un
computador encontró la mejor decisión.

---

## 2. Optimizar: decisiones, métrica y método

Para optimizar hacen falta dos cosas:

1. **Varios cursos de acción posibles** (si hay uno solo, no hay nada que decidir).
2. **Una métrica** para compararlos: margen, costo, tiempo, distancia, riesgo.

Optimizar es encontrar el curso de acción con el mejor valor de la métrica **entre los que se
pueden ejecutar**. La última frase es la que importa: el mejor plan imaginable casi nunca es
factible.

Una vez escrito el modelo, se resuelve con uno de dos tipos de método:

| Método | Qué garantiza | Cuándo se usa | Ejemplos |
|---|---|---|---|
| **Algoritmo exacto** | Encuentra el óptimo en un número finito de pasos | Cuando existe y termina en un tiempo razonable | Simplex (PL), ramificación y acotamiento (entera) |
| **Heurística** | Una buena solución en poco tiempo, sin garantía de que sea la mejor | Problemas enormes o sin algoritmo exacto práctico | Búsqueda tabú, recocido simulado, algoritmos genéticos |

---

## 3. Metodología: del problema a la decisión

| Etapa | Pregunta que responde | Qué sale | Error típico |
|---|---|---|---|
| 1. Definir el problema | ¿Qué se decide, para quién, en qué plazo? | Un enunciado acordado | Resolver el problema equivocado |
| 2. Construir el modelo | ¿Cómo se escribe en matemática? | Variables, objetivo, restricciones | Olvidar una restricción real |
| 3. Recolectar datos | ¿Cuánto vale cada parámetro? | Tablas con unidad y período | Datos de un mes que no representa la operación |
| 4. Resolver | ¿Cuál es la mejor decisión del modelo? | Solución y su lectura | Creer que el solver «sabe» algo que no se le dijo |
| 5. Validar | ¿La solución tiene sentido en la realidad? | Comparación con lo que se hace hoy | Saltarse esta etapa porque el solver dijo «óptimo» |
| 6. Implementar | ¿Cómo se usa, quién la usa, cada cuánto? | Procedimiento y capacitación | Un modelo que nadie entiende y nadie usa |

Las etapas no son una línea recta: la validación casi siempre devuelve a la etapa 2 o a la 3. Un
modelo que propone cosas absurdas no está equivocado en el solver, sino en lo que se le escribió o
en los datos que se le dieron.

---

## 4. Qué es un modelo y cuáles son sus partes

Un **modelo** es una simplificación de la realidad que conserva lo que importa para la pregunta.
Una maqueta de un auto a escala sirve para ver la forma, no para saber si tiene cenicero. Un modelo
es **matemático** cuando la relación entre sus partes se escribe con ecuaciones e inecuaciones.

Según para qué sirve, un modelo matemático es **descriptivo** (cómo es el sistema), **predictivo**
(qué va a pasar) o **prescriptivo** (qué conviene hacer). Los de optimización son prescriptivos.

### Los componentes

| Componente | Qué es | Pregunta para encontrarlo | Ejemplo |
|---|---|---|---|
| **Variables de decisión** (endógenas) | Lo que el modelo elige | ¿Qué valor tengo que decidir yo? | $x_i$ = litros de helado $i$ por semana |
| **Parámetros** (datos, exógenos) | Lo que ya está dado: coeficientes y lados derechos | ¿Qué valor me entregan? | margen por litro, minutos disponibles |
| **Función objetivo** | La métrica que se maximiza o minimiza | ¿Qué quiero mejorar? | $\max$ margen total |
| **Restricciones** | Lo que limita: recursos, demanda, contratos, balances | ¿Qué no puedo pasar? | minutos usados $\le$ minutos disponibles |
| **Naturaleza de las variables** | Signo y tipo | ¿Puede ser negativa? ¿Tiene que ser entera? | $x_i \ge 0$ |
| **Métricas o variables de estado** | Cantidades que se calculan a partir de las decisiones | ¿Qué quiero mirar del plan? | minutos usados, inventario final |

La forma general de un modelo de optimización es

$$\max \text{ (o } \min) \; f(x_1, \dots, x_n) \quad \text{s.a.} \quad g_k(x_1, \dots, x_n) \;\le, =, \ge\; b_k \quad k = 1, \dots, m$$

> **La prueba más útil del ramo.** Si el número está escrito en el enunciado, es un parámetro. Si
> el enunciado pregunta por él («cuánto producir», «a quién asignar»), es una variable. Un
> parámetro declarado como variable deja al modelo elegir, por ejemplo, cuánta materia prima
> «tiene»: elegirá infinita.

---

## 5. Tipos de modelos

| Criterio | Tipo | Cómo se reconoce |
|---|---|---|
| Certeza de los datos | **Determinístico** | Todos los parámetros se conocen con un valor |
| | **Estocástico** | Algún parámetro es aleatorio (una demanda con escenarios o distribución) |
| Forma de las funciones | **Lineal (PL)** | Objetivo y restricciones son sumas de «coeficiente × una variable» |
| | **No lineal (PNL)** | Aparece $x^2$, $\sqrt{x}$, $x_1 x_2$, $x_1/x_2$, $e^x$, $\lvert x \rvert$, un máximo… |
| Valores de las variables | **Continuo** | Las variables pueden tomar cualquier valor real (kilos, litros, horas) |
| | **Entero (PE)** | Las variables solo toman valores enteros (camiones, ramos) |
| | **Binario** | Variables 0 o 1 (abrir o no, asignar o no) |
| | **Entero mixto (PEM)** | Unas continuas y otras enteras o binarias |

Tres matices que se preguntan en las pruebas:

- **Lo lineal se juzga en las variables, no en los datos.** $c_i x_i$ es lineal aunque $c_i$ venga de
  multiplicar un precio por un rendimiento. $x_1 x_2$ no lo es.
- **Algunas no linealidades se arreglan.** La restricción $\dfrac{x_1}{x_1 + x_2} \ge 0{,}3$ parece no
  lineal, pero multiplicando por $x_1 + x_2 > 0$ queda $0{,}7x_1 - 0{,}3x_2 \ge 0$, que es lineal.
- **Cuándo NO sirve un modelo lineal.** Si duplicar la producción no duplica el costo (economías de
  escala), si el precio cae cuando se vende más o si hay costos fijos que se pagan solo al producir,
  el modelo lineal miente. Las unidades 3 y 4 tratan esos casos.

---

## 6. Del texto al modelo: la receta

**Paso 1 · En palabras.** Tres frases: *qué se decide* (con unidad y período), *qué se busca* y
*qué limita*. Si no puedes escribirlas, no entendiste el problema todavía.

**Paso 2 · Algebraico, con conjuntos e índices.** En vez de nombrar una variable por producto
($V$, $F$, $M$), se define un conjunto y se indexa:

- Conjuntos: $I$ (productos), con $i \in I$; $R$ (recursos), con $r \in R$.
- Parámetros: $c_i$ margen por unidad de $i$; $a_{ri}$ uso del recurso $r$ por unidad de $i$; $b_r$
  disponibilidad de $r$.
- Variables: $x_i \ge 0$, unidades de $i$ a producir.

$$\max \sum_{i \in I} c_i x_i \quad \text{s.a.} \quad \sum_{i \in I} a_{ri}\, x_i \le b_r \quad \forall r \in R, \qquad x_i \ge 0 \quad \forall i \in I$$

Por qué así: el mismo modelo sirve para 3 productos o para 300. Solo cambian los datos.

**Paso 3 · En OPL.** El modelo se copia casi tal cual: conjuntos, datos, variables, objetivo y
restricciones, y un bloque `execute` que imprime los resultados.

```opl
{string} I = ...;                    // conjuntos: se leen del .dat
{string} R = ...;
float c[I] = ...;                    // parámetros
float a[R][I] = ...;
float b[R] = ...;
dvar float+ x[I];                    // variables (float+ = no negativas)
maximize sum(i in I) c[i] * x[i];    // objetivo
subject to {
  forall(r in R)                     // una restricción por recurso
    ctRecurso: sum(i in I) a[r][i] * x[i] <= b[r];
}
```

**Control de unidades.** Cada término de una restricción tiene que estar en la misma unidad que su
lado derecho. Si $a_{ri}$ está en minutos por litro y $x_i$ en litros, $b_r$ va en minutos, no en
horas.

---

## 7. Ejemplo resuelto · Heladería Nieve del Sur

La heladería Nieve del Sur, de Pucón (ficticia), produce tres helados en litros: vainilla, frambuesa
y maqui. Cada litro pasa por la pasteurizadora y por el envasado. Esta semana la pasteurizadora
tiene 40 horas y el envasado 27. Un restaurante le compró 60 litros de vainilla por contrato y del
helado de maqui no se venden más de 60 litros.

| Helado | Precio por litro | Costo por litro | Pasteurización (min/L) | Envasado (min/L) |
|---|---|---|---|---|
| Vainilla | $17.800 | $8.600 | 5 | 4 |
| Frambuesa | $21.500 | $10.900 | 7 | 3 |
| Maqui | $25.700 | $14.300 | 6 | 5 |

**Paso 1 · En palabras.**

- *Qué se decide:* cuántos litros de cada helado producir esta semana.
- *Qué se busca:* el mayor margen total (precio menos costo, por litro producido).
- *Qué limita:* los minutos de pasteurización y de envasado, el contrato de vainilla y la demanda de
  maqui. Ninguna cantidad puede ser negativa.

**Paso 2 · Algebraico.** Conjuntos $I = \{V, F, M\}$ y $R = \{\text{past}, \text{env}\}$. El margen se
calcula antes de escribir el modelo: $c_V = 17{.}800 - 8{.}600$, y así.

| Parámetro | Vainilla | Frambuesa | Maqui |
|---|---|---|---|
| $c_i$ margen (CLP/L) | $9.200 | $10.600 | $11.400 |
| $a_{\text{past},i}$ (min/L) | 5 | 7 | 6 |
| $a_{\text{env},i}$ (min/L) | 4 | 3 | 5 |

Disponibilidad en minutos: $b_{\text{past}} = 40 \cdot 60 = 2{.}400$ y $b_{\text{env}} = 27 \cdot 60 = 1{.}620$.

$$\max \; 9{.}200\,x_V + 10{.}600\,x_F + 11{.}400\,x_M$$

$$\text{s.a.} \quad 5x_V + 7x_F + 6x_M \le 2{.}400 \;\; \text{[pasteurización]} \qquad 4x_V + 3x_F + 5x_M \le 1{.}620 \;\; \text{[envasado]}$$

$$x_V \ge 60 \;\; \text{[contrato]} \qquad x_M \le 60 \;\; \text{[demanda]} \qquad x_V, x_F, x_M \ge 0 \;\; \text{[naturaleza]}$$

**Paso 3 · En OPL.** El modelo está en `modelos/u01_heladeria.mod` y los datos en
`modelos/u01_heladeria.dat`. El contrato y la demanda se escriben como subconjuntos, para que el
mismo modelo sirva si mañana otro helado tiene contrato.

```opl
{string} Helados = ...;
{string} Recursos = ...;
float margen[Helados] = ...;
float uso[Recursos][Helados] = ...;
float cap[Recursos] = ...;
{string} ConMinimo = ...;   float minimo[ConMinimo] = ...;
{string} ConTope = ...;     float tope[ConTope] = ...;

dvar float+ x[Helados];

maximize sum(i in Helados) margen[i] * x[i];
subject to {
  forall(r in Recursos)  ctRecurso: sum(i in Helados) uso[r][i] * x[i] <= cap[r];
  forall(i in ConMinimo) ctMinimo:  x[i] >= minimo[i];
  forall(i in ConTope)   ctTope:    x[i] <= tope[i];
}
execute {
  writeln("z = ", cplex.getObjValue());
  for (var i in Helados) writeln("x_" + i + " = ", x[i]);
  for (var r in Recursos) writeln("holgura_" + r + " = ", ctRecurso[r].slack);
}
```

```opl
Helados = {"vainilla", "frambuesa", "maqui"};
Recursos = {"pasteurizacion", "envasado"};
margen = [9200, 10600, 11400];
uso = [[5, 7, 6],
       [4, 3, 5]];
cap = [2400, 1620];
ConMinimo = {"vainilla"};  minimo = [60];
ConTope = {"maqui"};       tope = [60];
```

**Paso 4 · La solución.** CPLEX (y el mismo modelo en Python, en el verificador) entrega:

| Helado | Litros | Pasteurización usada | Envasado usado |
|---|---|---|---|
| Vainilla | 240 L | 1.200 min | 960 min |
| Frambuesa | 120 L | 840 min | 360 min |
| Maqui | 60 L | 360 min | 300 min |
| **Total** | | **2.400 min** | **1.620 min** |

Margen total: **$4.164.000** a la semana.

**Paso 5 · Contra la regla intuitiva.** Un análisis de rentabilidad diría: cumplir el contrato y
después producir lo de mayor margen por litro hasta donde alcance. Maqui primero (hasta su tope de
60 L), después frambuesa, después vainilla. Con 60 L de vainilla y 60 de maqui quedan 1.740 minutos
de pasteurización, que alcanzan para 248,6 L de frambuesa y agotan la pasteurizadora. El envasado
queda con 334 minutos ociosos y el margen es de $3.870.857, es decir, $293.143 menos que el modelo.

**Cómo se lee.**

- Las dos máquinas quedan ocupadas al 100 %: son las restricciones **activas**. El contrato no
  aprieta (se hacen 240 L, no 60) y la demanda de maqui sí (se venden los 60 L).
- La regla de «lo más rentable primero» falla porque mira el margen **por litro**, y lo escaso son
  los **minutos**. La frambuesa deja más por litro que la vainilla, pero gasta 7 minutos de
  pasteurización contra 5. El modelo equilibra las dos máquinas a la vez; la regla no puede.
- **Decisión:** producir 240 L de vainilla, 120 de frambuesa y 60 de maqui. Si la heladería quiere
  ganar más, lo que hay que ampliar es la capacidad de las máquinas, no la demanda de vainilla. Cuánto
  vale un minuto más de cada máquina se calcula en la unidad 12.

---

## 8. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Declarar como variable un dato del enunciado (la capacidad, el precio) | Si el número está escrito, es parámetro; si se pregunta por él, es variable |
| Olvidar la no negatividad ($x \ge 0$, o `dvar float+` en OPL) | Escríbela siempre, al final, con nombre: [naturaleza] |
| Mezclar unidades (horas en el lado derecho, minutos en los coeficientes) | Escribe la unidad de cada parámetro en la tabla de datos antes de modelar |
| Poner el precio en el objetivo cuando el costo depende de la decisión | El objetivo de margen usa precio menos costo variable; el costo fijo no cambia la decisión |
| Sumar sobre el índice equivocado (`forall(r)` y adentro `x[r]` o `x["chica"]`) | Dentro de `sum(i in I)` solo puede variar $i$; lo fijo es el índice del `forall` |
| Usar «lo más rentable primero» como si fuera el óptimo | Sirve como plan de comparación; el óptimo lo da el modelo |
| Confundir variable de decisión con métrica (inventario, minutos usados) | Si se calcula a partir de otras decisiones, es una expresión (`dexpr`), no una decisión |
| Llamar «no lineal» a un modelo porque un dato es un producto | La linealidad se mira en las variables, no en cómo se calculó el coeficiente |

---

## 9. Práctica

Diez ejercicios: 1.1 a 1.4 básicos, 1.5 a 1.8 intermedios, 1.9 y 1.10 de desafío. En todos, escribe
primero el modelo en palabras y después en notación algebraica. Las pautas están en la sección 10.

**1.1 · Florería (básico).** Una florería de Puerto Varas arma dos ramos. El clásico lleva 6 rosas y
4 ramas de follaje y deja $5.400 de margen. El silvestre lleva 3 rosas, 8 flores silvestres y 2
ramas de follaje y deja $4.700. Cada día llegan 174 rosas, 184 flores silvestres y 156 ramas de
follaje, y hay un encargo de al menos 5 ramos clásicos. (a) Identifica variables, parámetros,
objetivo y restricciones. (b) Escribe el modelo. (c) ¿Las variables son continuas o enteras? ¿Qué
tipo de modelo es?

**1.2 · Clasificar modelos (básico).** Clasifica cada modelo (lineal o no lineal; continuo, entero,
binario o mixto; determinístico o estocástico) y justifica en una línea.

- (a) $\max\, 3x_1 + 5x_2$ s.a. $x_1 + 2x_2 \le 40$, $x_1, x_2 \ge 0$.
- (b) $\min \sum_{i}\sum_{j} c_{ij} x_{ij}$ s.a. $\sum_j x_{ij} = 1\ \forall i$, $x_{ij} \in \{0, 1\}$.
- (c) $\max\, x_1 x_2$ s.a. $2x_1 + 3x_2 \le 60$, $x_1, x_2 \ge 0$.
- (d) $\min\, 40y + \sum_i c_i x_i$ s.a. $x_i \le 500y\ \forall i$, $x_i \ge 0$, $y \in \{0, 1\}$.
- (e) $\max\, \mathbb{E}\left[\,p \min(q, D) - c\,q\,\right]$ con $D$ una demanda aleatoria de distribución conocida, $q \ge 0$.
- (f) $\min\, (x_1 - 4)^2 + (x_2 - 1)^2$ s.a. $x_1 + x_2 \le 3$.
- (g) $\max\, 2x_1 + 3x_2$ s.a. $\dfrac{x_1}{x_1 + x_2} \ge 0{,}3$, $x_1 + x_2 \le 50$, $x_1, x_2 \ge 0$.

**1.3 · Miel en dos frascos (básico).** Una apicultora de Linares vende miel en frascos de medio
kilo (margen $2.900) y de un kilo (margen $5.300). Este mes tiene 236 kg de miel y 13 horas de
envasado; un frasco chico toma 2 minutos y uno grande, 3. Una feria le compra al menos 90 frascos
chicos y no vende más de 140 grandes. (a) Escribe el modelo cuidando las unidades. (b) Un compañero
escribió la restricción de miel como $500x_1 + 1x_2 \le 236$: ¿qué está mal? (c) Comprueba que el
plan de 180 frascos chicos y 140 grandes es factible, calcula su margen y di qué restricciones
aprietan.

**1.4 · Etapas de un estudio (básico).** Una distribuidora de gas licuado de Temuco quiere decidir
cada mañana cuántos camiones manda a cada sector. Ordena estos hechos según las etapas de la
sección 3 y responde: ¿en qué etapa se detectó el problema y en qué etapas se originó?

- (i) Se resuelve el modelo con OPL.
- (ii) Se bajan del sistema los pedidos de enero a marzo para estimar la demanda por sector.
- (iii) El gerente dice: «queremos atender todos los pedidos del día al menor costo de flota».
- (iv) Se escribe que $x_{sk}$ es el número de camiones de tipo $k$ enviados al sector $s$.
- (v) Se compara el plan con lo que hicieron los despachadores en junio: el modelo manda camiones de
  10 toneladas a calles donde no entran y se queda corto de cilindros en todos los sectores.
- (vi) Se capacita a los despachadores y el plan se calcula cada día a las 7:00.

**1.5 · Alimento para gallinas (intermedio).** Una planta de Ñuble prepara alimento para gallinas
mezclando maíz, harina de soya y conchuela. Por kilo: el maíz cuesta \$310 y tiene 9 % de proteína;
la soya cuesta \$565 y tiene 47 % de proteína; la conchuela cuesta \$135, no tiene proteína y tiene
38 % de calcio. Cada tonelada de mezcla debe tener al menos 17,7 % de proteína y entre 3,42 % y
4,18 % de calcio. (a) Escribe el modelo para una tonelada, con un conjunto de ingredientes. (b) ¿Por
qué hace falta una restricción de igualdad? (c) Interpreta la solución: 635 kg de maíz, 255 kg de
soya y 110 kg de conchuela.

**1.6 · Cervecería: regla contra modelo (intermedio).** Una cervecería artesanal de Frutillar hace
lager y stout. Por hectolitro, la lager deja $48.000 de margen, usa 18 kg de malta y ocupa 6
días-tanque de fermentación; la stout deja $66.000, usa 30 kg de malta y ocupa 3 días-tanque. Este
mes hay 2.700 kg de malta y 480 días-tanque. (a) Aplica el análisis de rentabilidad: produce
primero la más rentable por hectolitro. (b) Comprueba que el plan de 50 hL de lager y 60 de stout
es factible y compara su margen. (c) Explica por qué falló la regla, con el margen por kilo de malta
y por día-tanque.

**1.7 · De frases a restricciones (intermedio).** Una fábrica hace tres productos, A, B y C, en
unidades por semana ($x_A$, $x_B$, $x_C$), que vende a $1.040, $1.560 y $1.330. Escribe cada frase
como una o dos restricciones **lineales**:

- (a) Por cada 3 unidades de A se hace al menos una de B.
- (b) C no puede pasar del 35 % de la producción total.
- (c) A es al menos el doble que C.
- (d) La producción total es exactamente 640 unidades.
- (e) A y B no pueden diferir en más de 50 unidades, en ninguna dirección.
- (f) El precio promedio por unidad vendida es de al menos $1.250.

**1.8 · Encuentra los cuatro errores (intermedio).** Una agrícola arma canastas de verduras chicas
(4 kg, 6 minutos de armado, $3.100 de margen) y grandes (9 kg, 10 minutos, $6.400). Cada semana tiene
1.800 kg de verduras y 38 horas de armado. Un compañero escribió este modelo, que no funciona.
Encuentra los cuatro errores, corrígelos y di qué hace cada uno con la solución.

```opl
{string} Canastas = {"chica", "grande"};
float margen[Canastas]  = [3100, 6400];
float kg[Canastas]      = [4, 9];
float minutos[Canastas] = [6, 10];
dvar float verduras;
float armado = 38;
dvar float x[Canastas];
maximize sum(i in Canastas) margen[i] * x[i];
subject to {
  ctVerduras: sum(i in Canastas) kg[i] * x[i] <= verduras;
  ctArmado:   sum(i in Canastas) minutos[i] * x["chica"] <= armado;
}
```

**1.9 · Un negocio, tres modelos (desafío).** Un carro de sándwiches vende a $4.600 cada uno, con un
costo de $2.350; la plancha alcanza para 170 sándwiches al día.

- (a) Si se sabe que la demanda es de 142 sándwiches, escribe el modelo y resuélvelo. ¿De qué tipo es?
- (b) Si el precio no está fijo, sino que para vender $q$ sándwiches hay que cobrar $p = 8{.}150 - 25q$
  (la recta pasa por 142 sándwiches a $4.600), escribe el modelo, di de qué tipo es y resuélvelo con
  cálculo.
- (c) Si el precio vuelve a ser $4.600 pero la demanda es incierta (85 sándwiches con probabilidad
  0,35, 125 con 0,40 y 165 con 0,25) y lo que no se vende se pierde, calcula la utilidad esperada de
  preparar 85, 121, 125 o 165 sándwiches. ¿Cuál conviene? ¿Por qué no basta con preparar la demanda
  promedio? Escribe el modelo como uno lineal por escenarios.

**1.10 · Cooperativa de pescadores (desafío).** Una cooperativa de Lebu recibe cada semana reineta y
merluza y decide cuántos kilos de cada especie destina a cada proceso: venta en fresco, ahumado o
congelado en filete. Cada proceso tiene una línea con capacidad en kilos de pescado entero y un costo
por kilo procesado; cada especie rinde distinto en cada proceso. (a) Escribe el modelo genérico con
conjuntos $E$ (especies) y $P$ (procesos). (b) Escríbelo en OPL con su `.dat`. (c) Resuélvelo con
estos datos e interpreta.

| | Fresco | Ahumado | Congelado |
|---|---|---|---|
| Capacidad de la línea (kg enteros/semana) | 3.400 | 2.600 | 3.100 |
| Costo de proceso (CLP por kg entero) | \$160 | $1.850 | \$870 |
| Reineta: rendimiento (kg producto / kg entero) | 1,00 | 0,52 | 0,46 |
| Reineta: precio (CLP por kg de producto) | $3.250 | $14.200 | $9.650 |
| Merluza: rendimiento | 1,00 | 0,41 | 0,43 |
| Merluza: precio (CLP por kg de producto) | $2.150 | $11.300 | $7.300 |

Captura disponible: 4.200 kg de reineta y 5.800 kg de merluza.

---

## 10. Pautas

**1.1.** Variables: $x_C$ y $x_S$, ramos clásicos y silvestres por día. Parámetros: márgenes, flores
por ramo, flores disponibles y el encargo. Objetivo: margen diario.

$$\max\; 5{.}400\,x_C + 4{.}700\,x_S \quad \text{s.a.} \quad 6x_C + 3x_S \le 174 \;\text{[rosas]} \quad 8x_S \le 184 \;\text{[silvestres]} \quad 4x_C + 2x_S \le 156 \;\text{[follaje]}$$

$$x_C \ge 5 \;\text{[encargo]} \qquad x_C, x_S \ge 0 \text{ y enteros}$$

Los ramos se cuentan de a uno: es un modelo **entero** (lineal y determinístico). Si se ignora la
integralidad, el óptimo es $x_C = 17{,}5$ y $x_S = 23$, con $202.600, que no se puede ejecutar.
Redondear hacia abajo da (17, 23) y $199.900, pero el mejor plan entero es **(18, 22)**, con
**$200.600**: el redondeo no es el óptimo entero. Fíjate además que el follaje nunca aprieta: dividida
por 2 queda $2x_C + x_S \le 78$, y las rosas, divididas por 3, ya exigen $2x_C + x_S \le 58$.

**1.2.**

- (a) Lineal, continuo, determinístico: una PL.
- (b) Lineal y **binario** (es una asignación).
- (c) **No lineal** (el producto $x_1 x_2$), continuo.
- (d) Lineal **entero mixto**: $y$ es binaria (pagar o no el costo fijo de 40) y las $x_i$ son continuas.
- (e) **Estocástico**: la demanda es aleatoria. Además el $\min$ lo hace no lineal tal como está
  escrito; con escenarios se vuelve lineal (ejercicio 1.9).
- (f) No lineal (cuadrático), continuo. Es convexo: la unidad 2 explica por qué eso ayuda.
- (g) **Lineal**, aunque no lo parezca: $x_1 \ge 0{,}3(x_1 + x_2)$, o sea $0{,}7x_1 - 0{,}3x_2 \ge 0$.

**1.3.** Variables $x_1$ (frascos chicos) y $x_2$ (grandes) en el mes. La envasadora tiene
$13 \cdot 60$, es decir, 780 min.

$$\max\; 2{.}900\,x_1 + 5{.}300\,x_2 \quad \text{s.a.} \quad 0{,}5x_1 + 1x_2 \le 236 \;\text{[kg de miel]} \qquad 2x_1 + 3x_2 \le 780 \;\text{[min]}$$

$$x_1 \ge 90 \;\text{[feria]} \qquad x_2 \le 140 \;\text{[demanda]} \qquad x_1, x_2 \ge 0$$

(b) Mezcla gramos con kilos: $500x_1$ está en gramos y 236 en kilos. Es $0{,}5x_1$ (o bien
$500x_1 + 1{.}000x_2 \le 236{.}000$ en gramos). (c) El plan (180, 140) usa $90 + 140 =$ 230 kg de miel
(sobran 6 kg) y $360 + 420 = 780$ minutos: la envasadora y la demanda de grandes aprietan. Margen:
**$1.264.000**. Ese plan es además el óptimo: por kilo de miel el frasco chico deja más ($5.800
contra $5.300), pero lo escaso son los minutos, y por minuto el grande deja más ($1.767 contra
$1.450).

**1.4.** Orden: (iii) definir el problema · (iv) construir el modelo · (ii) recolectar datos · (i)
resolver · (v) validar · (vi) implementar. El problema se **detectó en la validación** (v), pero
nació antes: en la **construcción del modelo** faltó la restricción de acceso de los camiones
grandes, y en la **recolección de datos** se usó el verano, cuando se vende menos gas, para planificar
el invierno. La validación devuelve a las etapas 2 y 3; después se vuelve a resolver y a validar.

**1.5.** Conjunto $I = \{\text{maíz}, \text{soya}, \text{conchuela}\}$; $x_i$ kg del ingrediente $i$ en
una tonelada; $c_i$ costo por kg, $p_i$ fracción de proteína, $k_i$ fracción de calcio.

$$\min \sum_{i \in I} c_i x_i \quad \text{s.a.} \quad \sum_{i \in I} x_i = 1{.}000 \qquad \sum_{i \in I} p_i x_i \ge 177 \qquad 34{,}2 \le \sum_{i \in I} k_i x_i \le 41{,}8 \qquad x_i \ge 0$$

(b) Sin la igualdad, el modelo de costo mínimo diría «no comprar nada», que cumple todo… salvo hacer
una tonelada. Los porcentajes se transforman en kilos justamente porque el total está fijo. Con 38 %
de calcio, la conchuela queda entre 90 y 110 kg. (c) La solución es 635 kg de maíz, 255 kg de soya y
110 kg de conchuela, con un costo de **$355.775** por tonelada. La proteína queda justo en 177 kg
(activa) y la conchuela en su máximo: es el ingrediente más barato y conviene usar todo el que el
calcio permite.

**1.6.** (a) La stout deja más por hectolitro, así que va primero: hasta que se acaba la malta, con
$2{.}700 / 30 = 90$ hL. No queda malta para lager. Margen: $5.940.000, con 210 días-tanque ociosos.
(b) El plan (50, 60) usa $900 + 1.800 =$ 2.700 kg de malta y $300 + 180 =$ 480 días-tanque: es
factible y deja **$6.360.000**, $420.000 más. (c) Lo escaso es la malta, no los hectolitros. Por kilo
de malta la lager deja $2.667 y la stout $2.200; por día-tanque, la stout deja $22.000 y la lager
$8.000. Cada cerveza es mejor en un recurso distinto, y el plan que usa los dos al máximo es el que
gana. El verificador comprueba que (50, 60) es el óptimo; la unidad 2 muestra por qué está en la
esquina donde se cruzan las dos restricciones.

**1.7.**

- (a) $x_B \ge x_A / 3$, es decir, $x_A - 3x_B \le 0$.
- (b) $x_C \le 0{,}35(x_A + x_B + x_C)$, es decir, $-0{,}35x_A - 0{,}35x_B + 0{,}65x_C \le 0$.
- (c) $x_A - 2x_C \ge 0$.
- (d) $x_A + x_B + x_C = 640$.
- (e) Dos restricciones: $x_A - x_B \le 50$ y $x_B - x_A \le 50$.
- (f) $\dfrac{1{.}040x_A + 1{.}560x_B + 1{.}330x_C}{x_A + x_B + x_C} \ge 1{.}250$. Multiplicando por el total
  (positivo) y pasando todo a la izquierda: $-210x_A + 310x_B + 80x_C \ge 0$. Se lee así: cada unidad
  de A queda 210 bajo la meta de precio, cada una de B la supera en 310 y cada una de C en 80.

El verificador prueba cada forma lineal contra la frase original en 20.000 puntos al azar.

**1.8.**

1. `dvar float verduras;` declara como variable un **dato**: el solver «elige» tener infinitas
   verduras y el modelo queda no acotado. Va `float verduras = 1800;`.
2. `float armado = 38;` está en **horas** y los coeficientes en minutos. Va `38 * 60` (2.280 min).
3. `dvar float x[...]` permite producir canastas **negativas**. Va `dvar float+`.
4. `minutos[i] * x["chica"]` suma sobre $i$ pero multiplica siempre la canasta chica: **índice
   equivocado**. Va `minutos[i] * x[i]`.

Corregido (`modelos/u01_e08_canastas.mod`), el óptimo es **(180, 120)**, con **$1.326.000** a la
semana, y aprietan las verduras y el armado. Si se corrigen 1, 3 y 4 pero se deja `armado = 38`, el
modelo propone 3,8 canastas grandes a la semana: un resultado absurdo que una validación atrapa de
inmediato.

**1.9.**

- (a) $\max\,(4{.}600 - 2{.}350)\,q$ s.a. $q \le 142$, $q \le 170$, $q \ge 0$: lineal, continuo (o entero)
  y determinístico. $q = 142$ y la utilidad es **$319.500**.
- (b) $\max\,(8{.}150 - 25q - 2{.}350)\,q = 5{.}800q - 25q^2$ s.a. $0 \le q \le 170$: **no lineal**
  (cuadrático y cóncavo). La derivada $5{.}800 - 50q = 0$ da $q^* = 116$, menor que 170. El precio
  es $8{.}150 - 25 \cdot 116$, o sea $5.250, y la utilidad **$336.400**. El óptimo no queda en un borde: queda en
  el interior, donde la derivada se anula (unidad 3).
- (c) Con $q$ preparados, las ventas son $\min(q, D)$. La demanda promedio es
  $0{,}35 \cdot 85 + 0{,}40 \cdot 125 + 0{,}25 \cdot 165 = 121$.

| Preparar | Ventas esperadas | Utilidad esperada |
|---|---|---|
| 85 | 85 | $191.250 |
| 121 (la media) | 108,4 | $214.290 |
| 125 | 111 | **$216.850** |
| 165 | 121 | $168.850 |

Conviene preparar **125**. Preparar la media no es lo mismo que maximizar la media: con 121 se pierde
la venta del escenario de 125 sin ganar nada en el de 85. Como modelo lineal por escenarios $s$, con
probabilidad $\pi_s$ y ventas $v_s$:

$$\max\; \sum_s \pi_s\, 4{.}600\, v_s - 2{.}350\, q \quad \text{s.a.} \quad v_s \le q,\;\; v_s \le D_s \;\; \forall s, \qquad 0 \le q \le 170$$

Resuelto, da $q = 125$ y **$216.850**. Comprobación rápida: la razón $(4{.}600 - 2{.}350)/4{.}600 = 45/92$
(cerca de 0,49) se compara con la probabilidad acumulada de la demanda: 0,35 en 85 (no alcanza) y
0,75 en 125 (alcanza). Es un modelo **estocástico** y lineal.

**1.10.** (a) Datos: $Q_e$ captura, $K_p$ capacidad de la línea, $r_{ep}$ rendimiento, $v_{ep}$
precio, $c_p$ costo de proceso. Variable $x_{ep}$: kg enteros de la especie $e$ al proceso $p$. El
margen por kilo entero es un dato calculado, $m_{ep} = v_{ep}\,r_{ep} - c_p$ (lineal en $x$).

$$\max \sum_{e \in E}\sum_{p \in P} (v_{ep}\, r_{ep} - c_p)\, x_{ep} \quad \text{s.a.} \quad \sum_{p \in P} x_{ep} \le Q_e \;\; \forall e \qquad \sum_{e \in E} x_{ep} \le K_p \;\; \forall p \qquad x_{ep} \ge 0$$

(b) Está en `modelos/u01_e10_cooperativa.mod` y `.dat`. Lo esencial:

```opl
dexpr float m[e in Especies][p in Procesos] = precio[e][p] * rend[e][p] - costo[p];
dvar float+ x[Especies][Procesos];
maximize sum(e in Especies, p in Procesos) m[e][p] * x[e][p];
subject to {
  forall(e in Especies) ctCaptura: sum(p in Procesos) x[e][p] <= captura[e];
  forall(p in Procesos) ctLinea:   sum(e in Especies) x[e][p] <= capacidad[p];
}
```

(c) Márgenes por kilo entero:

| $m_{ep}$ | Fresco | Ahumado | Congelado |
|---|---|---|---|
| Reineta | $3.090 | $5.534 | $3.569 |
| Merluza | $1.990 | $2.783 | $2.269 |

| Kilos enteros | Fresco | Ahumado | Congelado | Sin procesar |
|---|---|---|---|---|
| Reineta | 0 | 2.600 | 1.600 | 0 |
| Merluza | 3.400 | 0 | 1.500 | 900 |

Margen semanal: **$30.268.300**. Las tres líneas quedan llenas y sobran 900 kg de merluza. Lo
interesante es que la reineta no va a fresco aunque deja más ahí ($3.090) que la merluza ($1.990):
la reineta se aprovecha mejor en congelado ($3.569 contra $2.269), y la línea de fresco se le deja a
la merluza. El modelo asigna por **ventaja relativa**, no por el margen más alto de cada fila.
Decisión: si la cooperativa puede ampliar algo, que sea una línea (las tres aprietan), no la captura
de merluza, que ya sobra.

---

## 11. Caso integrador · Estampa Sur decide su mezcla

> Este caso sigue a Estampa Sur por todo el ramo: el mismo taller de serigrafía (ficticio) de
> Gestión de Operaciones. Acá se **plantea** el problema; la unidad 2 resuelve una versión de dos
> prendas con el método gráfico y la unidad 4 resuelve el modelo completo. Las cifras salen del
> script `verificacion/caso_estampa_sur_lp.py`.

Estampa Sur hace cinco prendas. Cada una pasa por la máquina de estampado y por el planchado, y gasta
tinta. En una semana el estampado tiene 40 horas, el planchado 18 y hay 29.500 g de tinta.

| Prenda | Margen por unidad | Estampado (s/u) | Planchado (s/u) | Tinta (g/u) | Demanda máxima (u/semana) |
|---|---|---|---|---|---|
| Poleras básicas | $1.380 | 30 | 20 | 12 | 1.450 |
| Polerones | $3.940 | 90 | 50 | 25 | 520 |
| Poleras estampado doble | $2.270 | 110 | 30 | 22 | 380 |
| Bolsas | \$960 | 20 | 40 | 8 | 860 |
| Gorros | $1.170 | 30 | 15 | 6 | 690 |

**En palabras.**

- *Qué se decide:* cuántas unidades de cada prenda producir en la semana.
- *Qué se busca:* el mayor margen total.
- *Qué limita:* los segundos de estampado y de planchado, los gramos de tinta y lo que se puede
  vender de cada prenda. Nada se produce en negativo.

**Algebraico.** Conjuntos $I$ (las cinco prendas) y $R = \{\text{est}, \text{pla}, \text{tinta}\}$.
Parámetros: $c_i$ margen, $a_{ri}$ uso del recurso $r$ por unidad de $i$, $b_r$ disponibilidad y
$d_i$ demanda máxima. Las horas se pasan a segundos para que calcen con los coeficientes:
$b_{\text{est}} = 40 \cdot 3{.}600 = 144{.}000$ s, $b_{\text{pla}} = 18 \cdot 3{.}600 = 64{.}800$ s y
$b_{\text{tinta}} = 29{.}500$ g.

$$\max \sum_{i \in I} c_i x_i \quad \text{s.a.} \quad \sum_{i \in I} a_{ri}\, x_i \le b_r \;\; \forall r \in R \qquad x_i \le d_i \;\; \forall i \in I \qquad x_i \ge 0 \;\; \forall i \in I$$

Es un modelo lineal, continuo (se aceptan fracciones de prenda como aproximación de una semana
grande) y determinístico.

**Por qué hace falta el modelo.** Si el taller quisiera producir toda la demanda, necesitaría:

| Recurso | Necesita | Tiene |
|---|---|---|
| Estampado | 170.000 s | 144.000 s |
| Planchado | 111.150 s | 64.800 s |
| Tinta | 49.780 g | 29.500 g |

Faltan los tres recursos, así que hay que elegir; vender todo daría $6.545.300, que no se puede
alcanzar. ¿Y una regla simple? Mira el margen por unidad del recurso escaso:

| Prenda | CLP por s de estampado | CLP por s de planchado | CLP por g de tinta |
|---|---|---|---|
| Poleras básicas | 46,0 | 69,0 | 115 |
| Polerones | 43,8 | 78,8 | 158 |
| Poleras estampado doble | 20,6 | 75,7 | 103 |
| Bolsas | 48,0 | 24,0 | 120 |
| Gorros | 39,0 | 78,0 | 195 |

Las bolsas son las mejores en estampado y las peores en planchado; los gorros ganan en tinta. Cada
recurso ordena las prendas de otra manera y no hay una regla que diga cuál mirar: eso lo resuelve el
modelo, en la unidad 4.

**Lo que pasa a la unidad 2.** Para dibujar el problema hacen falta dos variables. La unidad 2 toma
una versión reducida con sus propios datos: solo poleras básicas y polerones, 30 horas de estampado,
18 de planchado y un tope de 830 polerones, sin tinta ni las otras prendas. Ahí se ve en el plano
dónde está la mejor mezcla y por qué.

---

## 12. Para seguir

**En los libros del ramo.**

- Winston, *Investigación de operaciones: aplicaciones y algoritmos* (4.ª ed., 2005), el libro que fija
  el programa: sus capítulos introductorios sobre modelos y la introducción a la programación lineal
  traen muchos ejercicios de formulación como los de esta unidad.
- Hillier y Lieberman, *Introducción a la investigación de operaciones* (7.ª ed., 2001): los capítulos
  iniciales cuentan el origen de la disciplina y la metodología de un estudio.

**Abierto y gratis.**

- Bradley, Hax y Magnanti, *Applied Mathematical Programming* (Addison-Wesley, 1977), en inglés,
  publicado completo por el MIT. El capítulo 1 (*Mathematical Programming: An Overview*) cubre la
  clasificación de modelos (1.2), ejemplos de formulación (1.3) y una primera mirada geométrica (1.4):
  https://web.mit.edu/15.053/www/AMP.htm

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un enunciado de mezcla con tres
ingredientes, déjame escribir el modelo y corrígeme variable por variable».
