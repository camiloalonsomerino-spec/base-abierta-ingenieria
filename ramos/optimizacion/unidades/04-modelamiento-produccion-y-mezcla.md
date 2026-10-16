---
ramo: Optimización
unidad: 4
titulo: Modelamiento lineal I · producción y mezcla
version: 0.1 (15-10-2026)
requiere: [01-investigacion-de-operaciones, 03-no-lineal]
alimenta: [05-modelamiento-multiperiodo-y-transporte, 07-implementacion-en-opl, 10-dualidad]
verificacion: verificacion/u04_modelamiento_i.py
---

# Unidad 4 · Modelamiento lineal I · producción y mezcla

**Qué vas a poder hacer.** Traducir un problema de decisión a un modelo lineal en tres pasos (en
palabras, en notación algebraica con conjuntos e índices y en OPL), elegir variables que alcancen para
calcular todo, escribir restricciones de capacidad, demanda, balance y proporción con unidades
coherentes, reconocer las familias de producción, mezcla, dieta, cartera y corte, y leer la solución:
qué restricción aprieta, cuánto sobra y cuánto vale una unidad más de cada recurso.

**Lo que necesitas antes.** Las partes de un modelo de la unidad 1 (decisión, objetivo, restricciones)
y la idea de la unidad 3: un modelo lineal es convexo, así que el óptimo que entrega el solver es el
global. Para correr los modelos, OPL instalado (o Python con `scipy`, como el verificador).

**Tiempo.** Unas 6 horas: 2 de lectura con el ejemplo y 4 de práctica.

---

## 1. La idea · un modelo en tres pasos

Modelar es la parte difícil de la optimización: el solver resuelve en segundos lo que uno le escribe,
también si está mal escrito. Por eso cada modelo de esta unidad se arma en tres pasos y no se salta
ninguno.

1. **En palabras.** Qué se decide, qué se busca y qué lo limita. Si no cabe en tres frases, todavía
   no se entiende el problema.
2. **Algebraico.** Conjuntos, índices, parámetros (datos) y variables (decisiones); después el
   objetivo y las restricciones, cada una con una frase que diga qué hace.
3. **En OPL.** Casi una copia del paso 2: los conjuntos y parámetros se leen de un `.dat`, las
   variables se declaran con `dvar` y cada familia de restricciones con un `forall`.

Un modelo **lineal** tiene objetivo y restricciones que son sumas de «número por variable». No hay
productos de variables, ni divisiones por una variable, ni potencias. Esa es la condición que permite
resolver modelos con miles de variables y confiar en el óptimo.

---

## 2. Elegir las variables

### La prueba de las variables

Una variable de decisión es algo que **el que decide controla** y cuyo valor no se conoce antes de
resolver. La prueba para saber si alcanzan:

> Si alguien te diera el valor de todas las variables, ¿podrías calcular el objetivo y comprobar cada
> restricción sin preguntar nada más?

Si la respuesta es no, falta una variable. En una mezcla con dos productos, «kilos de cada
ingrediente» no basta: no se sabe cuánto de cada ingrediente va a cada producto, y sin eso no se puede
revisar la proteína de cada uno. Hace falta $x_{ij}$, los kilos del ingrediente $i$ que van al
producto $j$.

### Variable o parámetro

| | Parámetro (dato) | Variable (decisión) |
|---|---|---|
| Quién lo fija | el problema (precio, capacidad, demanda) | el modelo |
| Cuándo se conoce | antes de resolver | después de resolver |
| Notación de esta base | letras con índice: $c_i$, $a_{ij}$, $b_j$ | $x_i$, $x_{ij}$, $y_j$ |
| En OPL | `float c[I] = ...;` | `dvar float+ x[I];` |

El costo por kilo de un ingrediente es un parámetro; los kilos que se compran son la variable. Llamar
«variable de decisión» al costo (se ve en apuntes y tareas) es el error más común del ramo.

### Conjuntos e índices

Un modelo **compacto** no escribe una restricción por producto: escribe una para todos, con un índice.

| Elemento | Ejemplo | Lectura |
|---|---|---|
| Conjunto | $I$ = ingredientes, $J$ = productos | sobre qué se repite |
| Parámetro con índice | $a_{ik}$ = % del atributo $k$ en el ingrediente $i$ | una tabla de datos |
| Variable con índice | $x_{ij}$ | una tabla de decisiones |
| Suma | $\sum_{i \in I} x_{ij}$ | total del producto $j$ (se suma sobre $i$, queda $j$ libre) |
| Para todo | $\forall j \in J$ | una copia de la restricción por cada $j$ |

La regla para no equivocarse: **todo índice que aparece en una restricción está o sumado o en el
«para todo»**. Si queda un índice suelto, la restricción está mal escrita.

---

## 3. Las restricciones que se repiten

| Tipo | Forma | Se lee |
|---|---|---|
| Capacidad | $\sum_{i} a_{ri}\, x_i \le b_r \quad \forall r$ | lo que se usa del recurso $r$ no supera lo disponible |
| Demanda máxima | $x_i \le d_i \quad \forall i$ | no se produce más de lo que se vende |
| Demanda mínima o compromiso | $x_i \ge m_i$ | hay que entregar al menos eso |
| Demanda exacta | $\sum_i x_{ij} = D_j$ | se produce justo lo pedido |
| Balance | lo que entra $=$ lo que sale (o $\ge$) | conecta dos etapas: la leche que se compra alimenta el queso |
| Proporción | $\sum_i a_{ik} x_{ij} \ge l_{jk} \sum_i x_{ij}$ | el producto $j$ tiene al menos $l_{jk}$ % del atributo $k$ |
| Naturaleza | $x \ge 0$ | no se produce una cantidad negativa |

### La proporción, sin dividir

«El producto debe tener al menos 12 % de proteína» se escribe primero como un promedio:

$$\frac{\sum_i a_i\, x_i}{\sum_i x_i} \ge 12$$

Eso divide por una variable: no es lineal. Como la cantidad total es positiva, se multiplica a los dos
lados y queda lineal:

$$\sum_i a_i\, x_i \ge 12 \sum_i x_i \quad\Longleftrightarrow\quad \sum_i (a_i - 12)\, x_i \ge 0$$

La segunda forma lo explica: cada ingrediente aporta su diferencia con la meta. Los que están sobre
12 % «pagan» por los que están bajo.

Si el total es un dato (una mezcla de exactamente 9.600 L), la proporción tiene lado derecho fijo:
$\sum_i a_i x_i \ge 12 \cdot 9.600$. Si el total es variable, hay que usar la suma de las variables.

---

## 4. Unidades coherentes

Cada restricción se escribe en **una sola unidad** a los dos lados. Antes de resolver, revisa cada
fila con la pregunta «¿en qué se mide esto?»:

- **Tiempo.** Si los coeficientes están en segundos por unidad, la capacidad va en segundos: 40 horas
  son 144.000 s, 18 horas son 64.800 s.
- **Porcentajes.** O todo en % (12) o todo en fracción (0,12). Mezclarlos multiplica una restricción
  por cien.
- **Toneladas y kilos.** Si el costo está en pesos por kilo y la variable en toneladas, el costo de
  una tonelada es $1000 \times c_i$.
- **El objetivo también.** Sumar pesos con unidades (o margen por kilo con margen por litro) da un
  número que no significa nada.

Un error de unidades no hace fallar al solver: entrega una solución que se ve razonable y no lo es
(ejercicio 4.2).

---

## 5. Las familias de modelos

Las cinco familias de esta unidad, en forma compacta. En todas, $x \ge 0$.

**Producción (mezcla de productos).** $I$ productos, $R$ recursos. Margen $c_i$, uso $a_{ri}$,
capacidad $b_r$, demanda máxima $d_i$.

$$\max \sum_{i \in I} c_i x_i \quad\text{s.a.}\quad \sum_{i \in I} a_{ri} x_i \le b_r \;\; \forall r \in R, \qquad x_i \le d_i \;\; \forall i \in I$$

**Mezcla (blending).** Ingredientes $I$, productos $J$, atributos $K$. La variable tiene dos índices:
$x_{ij}$, cuánto de $i$ va a $j$. Lo producido de $j$ es $\sum_i x_{ij}$.

$$\max \sum_{j} p_j \sum_{i} x_{ij} - \sum_{i} c_i \sum_{j} x_{ij} \quad\text{s.a.}\quad \sum_j x_{ij} \le S_i \;\; \forall i, \qquad \sum_i a_{ik} x_{ij} \ge l_{jk} \sum_i x_{ij} \;\; \forall j, k$$

(más los máximos de cada atributo y las demandas). Si hay un solo producto, el índice $j$ sobra.

**Dieta.** Alimentos $I$, nutrientes $K$. Mínimo costo cumpliendo cada nutriente:
$\min \sum_i c_i x_i$ s.a. $\sum_i a_{ik} x_i \ge r_k$ para los mínimos y $\le$ para los máximos (sodio,
grasa). Es una mezcla de un solo producto sin proporciones: las exigencias son cantidades absolutas.

**Cartera.** Instrumentos $I$, presupuesto $B$. Máximo retorno esperado con límites:
$\max \sum_i r_i x_i$ s.a. $\sum_i x_i = B$, topes por instrumento, y proporciones («a lo más 35 % en
acciones», «riesgo promedio a lo más 3») escritas sin dividir, como en el punto 3.

**Corte simple.** Rollos o barras de largo $L$ que se cortan en piezas de largo $\ell_k$ con demanda
$d_k$. Se listan los **patrones** de corte $P$ (cuántas piezas de cada largo salen de una barra) y la
variable es $y_p$, cuántas barras se cortan con el patrón $p$:

$$\min \sum_{p \in P} y_p \quad\text{s.a.}\quad \sum_{p \in P} n_{kp}\, y_p \ge d_k \;\; \forall k$$

La variable no es «cuántas piezas», sino «cuántas barras con cada patrón»: elegir bien la variable
hace lineal un problema que a primera vista no lo es.

---

## 6. Por qué salen fracciones

Un modelo lineal busca el óptimo en un vértice de la región, y un vértice es la intersección de
restricciones: la solución de un sistema de ecuaciones. Con datos cualesquiera, ese sistema da
fracciones: 833,75 poleras, 62,5 barras.

- Si la cantidad es grande (kilos, litros, 800 poleras), la fracción no importa: se redondea y la
  pérdida es mínima.
- Si es chica (seis hidrolavadoras, cinco camiones), redondear puede dejar un plan **infactible**
  (redondear hacia arriba se pasa de un recurso) o **malo** (el mejor plan entero puede estar lejos
  del lineal; ejercicio 4.10).

Cuando la variable tiene que ser entera, el modelo es de **programación entera** y se resuelve de
otra forma (ramificación y acotamiento). Lo trata Tópicos de Optimización (programación entera). En
OPL basta con cambiar `dvar float+` por `dvar int+`; lo que cambia es el algoritmo y el tiempo que
tarda.

---

## 7. Leer la solución

El solver entrega más que el plan. Para cada restricción:

| Qué | Significa | Cómo se usa |
|---|---|---|
| **Activa** | se cumple con igualdad (holgura 0) | es la que limita; aflojarla mejora el objetivo |
| **Holgura** | cuánto sobra (o cuánto se pasa del mínimo) | recurso ocioso: no vale la pena comprar más |
| **Precio sombra** (dual) | cuánto mejora el objetivo por cada unidad más de lado derecho | lo máximo que conviene pagar por esa unidad extra |
| **Costo reducido** | cuánto le falta a una variable en 0 para que convenga | o, para una variable en su tope, cuánto aportaría una unidad más de tope |

Tres reglas de lectura:

- Una restricción con holgura tiene precio sombra 0: si sobra, una unidad más no sirve.
- El precio sombra vale **en el margen**: es la pendiente para cambios chicos. Para cambios grandes
  hay que volver a resolver (la unidad 12 calcula el rango en que vale).
- En un problema de **mínimo**, el signo se lee al revés: un precio sombra positivo en una exigencia
  $\ge$ dice cuánto **sube el costo** si la exigencia sube. Leerlo como si fuera de máximo es un error
  frecuente.

En OPL se piden en el bloque `execute`: `Restriccion.dual` y `Restriccion.slack`. La unidad 10 explica
de dónde salen.

---

## 8. Ejemplo resuelto · la granola de la feria

Una emprendedora de Concepción hace dos granolas: **clásica** y **premium**. Las arma con avena, maní y
pasas, y vende todo lo que produce hasta un tope semanal.

| Ingrediente | Proteína (%) | Azúcar (%) | Costo (\$/kg) | Disponible (kg/semana) |
|---|---|---|---|---|
| Avena | 12 | 1 | 1.380 | 980 |
| Maní | 24 | 5 | 4.150 | 190 |
| Pasas | 4 | 65 | 2.950 | 280 |

| Granola | Precio (\$/kg) | Venta máxima (kg/semana) | Proteína mínima | Azúcar |
|---|---|---|---|---|
| Clásica | 4.650 | 760 | 12 % | entre 14 % y 18 % |
| Premium | 6.980 | 230 | 16 % | entre 9 % y 12 % |

**Paso 1 · En palabras.** Se decide cuántos kilos de cada ingrediente van a cada granola. Se busca el
mayor margen semanal (ventas menos ingredientes). Limitan los ingredientes disponibles, lo que se
puede vender y la receta: proteína mínima y azúcar entre un mínimo (sabor) y un máximo.

**Paso 2 · Algebraico.**

- Conjuntos: $I$ = {avena, maní, pasas}, $J$ = {clásica, premium}, $K$ = {proteína, azúcar}.
- Parámetros: $c_i$ costo, $S_i$ disponible, $p_j$ precio, $D_j$ venta máxima, $a_{ik}$ % del atributo
  $k$ en $i$, $l_{jk}$ y $u_{jk}$ % mínimo y máximo de $k$ en $j$.
- Variable: $x_{ij}$ = kg del ingrediente $i$ en la granola $j$, por semana.

$$\max\; \sum_{j \in J} p_j \sum_{i \in I} x_{ij} - \sum_{i \in I} c_i \sum_{j \in J} x_{ij}$$

$$\sum_{j \in J} x_{ij} \le S_i \;\; \forall i \qquad \text{(no se usa más ingrediente del que hay)}$$

$$\sum_{i \in I} x_{ij} \le D_j \;\; \forall j \qquad \text{(no se produce más de lo que se vende)}$$

$$\sum_{i \in I} a_{ik}\, x_{ij} \ge l_{jk} \sum_{i \in I} x_{ij} \;\; \forall j, k \qquad \text{(mínimo de proteína y de azúcar)}$$

$$\sum_{i \in I} a_{ik}\, x_{ij} \le u_{jk} \sum_{i \in I} x_{ij} \;\; \forall j, k \text{ con tope} \qquad \text{(máximo de azúcar)}$$

$$x_{ij} \ge 0$$

**Paso 3 · En OPL** (`modelos/u04_granola.mod`, con los datos en `u04_granola.dat`).

```opl
{string} Ingredientes = ...;
{string} Productos    = ...;
{string} Atributos    = ...;

float contenido[Ingredientes][Atributos] = ...;
float costo[Ingredientes] = ...;   float disp[Ingredientes] = ...;
float precio[Productos]   = ...;   float demanda[Productos] = ...;
float minimo[Productos][Atributos] = ...;
float maximo[Productos][Atributos] = ...;   // 100 = sin tope

dvar float+ x[Ingredientes][Productos];

dexpr float kilos[j in Productos] = sum(i in Ingredientes) x[i][j];
dexpr float Margen = sum(j in Productos) precio[j] * kilos[j]
                   - sum(i in Ingredientes, j in Productos) costo[i] * x[i][j];
maximize Margen;

subject to {
  forall(i in Ingredientes)
    Disponibilidad: sum(j in Productos) x[i][j] <= disp[i];
  forall(j in Productos)
    Demanda: kilos[j] <= demanda[j];
  forall(j in Productos, a in Atributos)
    Minimo: sum(i in Ingredientes) contenido[i][a] * x[i][j] >= minimo[j][a] * kilos[j];
  forall(j in Productos, a in Atributos: maximo[j][a] < 100)
    Maximo: sum(i in Ingredientes) contenido[i][a] * x[i][j] <= maximo[j][a] * kilos[j];
}
```

Fíjate en tres detalles: la proporción multiplica por `kilos[j]` en vez de dividir; la condición
`maximo[j][a] < 100` crea la restricción de máximo solo donde hay tope (la proteína no tiene); y cada
`forall` lleva un nombre para pedir después su `.dual`.

**La solución** (OPL y Python coinciden).

| kg por semana | Avena | Maní | Pasas | Total |
|---|---|---|---|---|
| Clásica | 513 | 98,8 | 148,2 | 760 |
| Premium | 114 | 91,2 | 22,8 | 228 |
| Usado / disponible | 627 / 980 | 190 / 190 | 171 / 280 | |

Ventas por $5.125.440, ingredientes por $2.158.210: **margen de $2.967.230 por semana**. Las dos
granolas quedan justo en su proteína mínima y en su azúcar mínima (12 % y 14 % la clásica; 16 % y 9 %
la premium); los máximos de azúcar sobran.

| Restricción | Estado | Precio sombra |
|---|---|---|
| Avena | sobran 353 kg | 0 |
| Maní | activa | $10.838 por kg |
| Pasas | sobran 109 kg | 0 |
| Venta clásica | activa (760) | $1.195 por kg |
| Venta premium | sobran 2 kg | 0 |

**Cómo se lee.**

- **El maní es el cuello de botella.** La proteína mínima obliga a usar maní, y se acaba. Por eso la
  premium (que necesita más maní por kilo) se queda en 228 kg aunque podría vender 230.
- Cada kilo más de maní subiría el margen en unos $10.838, ya descontado lo que cuesta. Conviene
  buscar otro proveedor aunque cobre bastante más que los $4.150 actuales.
- Comprar más avena o pasas no sirve: sobran.
- La receta la fijan las exigencias de calidad, no el gusto de la dueña: cada granola usa justo el
  mínimo de proteína y de azúcar, porque el maní y las pasas son caros. Si quisiera una premium más
  dulce, tendría que agregar la exigencia y volver a resolver.
- Las cantidades tienen decimales (98,8 kg): en kilos no importa.

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Declarar como variable un dato (el costo, la capacidad) | Haz la prueba: ¿lo controla quien decide y se conoce solo después de resolver? |
| Olvidar la no negatividad | Escríbela siempre; en OPL, `dvar float+` |
| Escribir la proporción dividiendo por la suma de variables | Multiplica: $\sum a_i x_i \ge l \sum x_i$ |
| En una mezcla con varios productos, usar $x_i$ en vez de $x_{ij}$ | Si cada producto tiene su receta, la variable necesita los dos índices |
| Sumar sobre el índice equivocado en OPL (`sum(j in Productos) x[i][j]` cuando se quería el total del producto) | El índice que queda libre es el del `forall`; el que se suma desaparece |
| Dejar un índice suelto en una restricción | Todo índice está en la suma o en el «para todo» |
| Mezclar horas con minutos, % con fracción, kg con t | Revisa la unidad de cada fila antes de resolver |
| Leer el precio sombra de un problema de mínimo como si fuera de máximo | En un mínimo, el dual de una exigencia $\ge$ dice cuánto sube el costo |
| Redondear una solución fraccionaria sin revisar | Comprueba que el redondeo sea factible y compáralo con el óptimo entero si las cantidades son chicas |

---

## 10. Práctica

Diez ejercicios: 4.1 a 4.4 básicos, 4.5 a 4.8 intermedios, 4.9 y 4.10 de desafío. Las pautas están en
la sección 11. En todos, escribe primero el modelo en palabras.

**4.1 · Taller de cerámica (básico).** Un taller hace tazas y fuentes. Cada taza deja $730 de margen y
usa 0,22 kg de arcilla; cada fuente deja $1.060 y usa 0,38 kg. Hay 760 kg de arcilla a la semana y el
horno cuece 2.900 piezas por semana (de cualquier tipo). Se venden a lo más 1.150 fuentes. Formula en
palabras y en forma algebraica, resuelve e indica qué restricciones quedan activas.

**4.2 · El modelo con unidades cruzadas (básico).** Un lavado de autos ofrece lavado con encerado ($x$,
margen $9.000) y lavado con aspirado interior ($y$, margen $7.500). En el túnel, el primero tarda
12 min y el segundo 8 min; en la zona de terminación, 10 y 20 min. El túnel funciona 40 h a la semana
y la terminación 50 h. Un practicante entregó este modelo:

$$\max\; 9000x + 7500y \quad\text{s.a.}\quad 12x + 8y \le 40, \quad 10x + 20y \le 50, \quad x, y \ge 0$$

Resuélvelo, explica por qué el resultado es absurdo, corrígelo y resuelve el modelo bueno.

**4.3 · El almuerzo del casino (básico).** El casino de una empresa arma el plato base con legumbres,
arroz y huevo, y quiere el menor costo por persona que cumpla al menos 880 kcal y 42 g de proteína, con
a lo más 290 mg de sodio.

| Por porción | kcal | Proteína (g) | Sodio (mg) | Costo (\$) |
|---|---|---|---|---|
| Legumbres | 235 | 16 | 12 | 340 |
| Arroz | 190 | 3 | 4 | 115 |
| Huevo | 85 | 7 | 75 | 165 |

Formula y resuelve. ¿Qué exigencias quedan activas? ¿Por qué no entra el huevo?

**4.4 · Cuatro frases a ecuaciones (básico).** Una mezcla usa $x_1$, $x_2$ y $x_3$ kilos de tres
ingredientes, con 10 %, 22 % y 6 % de proteína. Escribe cada frase como una restricción lineal: (a) el
ingrediente 2 es a lo más el 30 % de la mezcla; (b) del ingrediente 1 se usa al menos el doble que del
3; (c) la mezcla tiene al menos 12 % de proteína; (d) la razón entre los ingredientes 1 y 2 es a lo más
de 3 a 2. Después revisa si la mezcla de 50, 30 y 20 kg cumple cada una.

**4.5 · Un ensamblaje de 9.600 litros (intermedio).** Una viña del Maule arma un ensamblaje de
9.600 L con tres vinos base. La etiqueta exige que al menos la mitad sea cabernet y que el alcohol
quede entre 13,2 % y 13,8 %.

| Vino base | Alcohol (%) | Costo (\$/L) | Disponible (L) |
|---|---|---|---|
| Cabernet | 14,0 | 1.900 | 7.000 |
| Merlot | 13,0 | 1.480 | 4.000 |
| Carmenere | 14,5 | 1.100 | 5.800 |

Formula el modelo en los tres pasos (con OPL), resuélvelo al menor costo y explica qué restricciones
deciden la receta. ¿Cuánto cuesta un litro más de ensamblaje?

**4.6 · Una cartera de 50 millones (intermedio).** Una persona invierte $50 millones a un año en cuatro
instrumentos.

| Instrumento | Retorno esperado | Nivel de riesgo |
|---|---|---|
| Depósito a plazo | 5,2 % | 1 |
| Fondo de renta fija | 6,8 % | 2 |
| Fondo accionario | 11,5 % | 6 |
| Bono corporativo | 8,3 % | 3 |

Quiere el mayor retorno esperado con estas condiciones: el riesgo promedio (ponderado por monto) es a
lo más 3,0; a lo más el 35 % va al fondo accionario; al menos $10 millones quedan en depósito
(liquidez), y el bono se vende hasta $12 millones. Formula sin dividir por variables y resuelve.

**4.7 · Cortar tubos de 6 metros (intermedio).** Una ferretería corta tubos de 6 m para un pedido de
130 piezas de 2,4 m, 205 de 1,7 m y 170 de 1,1 m. (a) Lista todos los patrones de corte maximales (a
los que no les cabe otra pieza) con su pérdida. (b) Formula el modelo que minimiza los tubos usados y
resuélvelo. (c) ¿Sale entero? ¿Cuántos tubos hacen falta como mínimo y qué tan lejos está de la cota
que da el largo total?

**4.8 · Leche, queso y yogur (intermedio).** Una quesería compra hasta 7.600 L de leche a la semana a
$440 el litro. Un kilo de queso usa 9,5 L de leche y uno de yogur 1,15 L. El queso se vende a
$7.200/kg (a lo más 480 kg) y el yogur a $1.750/kg (a lo más 2.900 kg). La planta tiene 85 h a la
semana y el queso pide 0,125 h/kg y el yogur 0,025 h/kg. Formula con una variable para la leche y una
restricción de balance, resuelve e interpreta el precio sombra de la leche y el de las horas.

**4.9 · Alimento para salmones (desafío).** Una planta de Puerto Montt produce a la semana 40 t de
alimento de inicio y 120 t de engorda con harina de pescado, harina de soya, aceite de pescado y aceite
de raps.

| Ingrediente | Proteína (%) | Lípidos (%) | Costo (\$/kg) |
|---|---|---|---|
| Harina de pescado | 64 | 10 | 1.650 |
| Harina de soya | 45 | 2 | 520 |
| Aceite de pescado | 0 | 100 | 2.400 |
| Aceite de raps | 0 | 100 | 1.150 |

El inicio necesita al menos 48 % de proteína y entre 18 % y 22 % de lípidos; la engorda, al menos 38 %
de proteína y entre 28 % y 32 % de lípidos. En cada alimento, al menos el 40 % del aceite tiene que ser
de pescado (omega 3), y el de inicio lleva al menos 25 % de harina de pescado. Hay 60 t de harina de
pescado a la semana. (a) Formula en forma compacta con conjuntos e índices y escríbelo en OPL, con las
variables en toneladas. (b) Resuelve al menor costo. (c) ¿Cuánto cuesta subir la proteína de la
engorda a 39 %? (d) ¿Qué pasa si esta semana solo llegan 30 t de harina de pescado?

**4.10 · Equipos para arrendar (desafío).** Una pyme de arriendo compra hidrolavadoras industriales
($x$) y generadores ($y$). Cada hidrolavadora deja $900.000 de margen al mes y cuesta 4 millones; cada
generador deja $700.000 y cuesta 3 millones. El presupuesto es de 25 millones y en la bodega hay
12 m²: la hidrolavadora ocupa 1 m² y el generador 3 m². (a) Resuelve el modelo lineal. (b) Redondea la
solución hacia abajo y al entero más cercano: ¿son factibles?, ¿cuánto dejan? (c) Encuentra el mejor
plan entero (enumerando o con `dvar int+`) y compáralo.

---

## 11. Pautas

**4.1.** En palabras: se decide cuántas tazas ($T$) y fuentes ($F$) hacer por semana; se busca el
mayor margen; limitan la arcilla, el horno y la venta de fuentes.

$$\max\; 730T + 1060F \quad\text{s.a.}\quad 0{,}22T + 0{,}38F \le 760, \quad T + F \le 2900, \quad F \le 1150, \quad T, F \ge 0$$

Óptimo: 2.137,5 tazas y 762,5 fuentes, con margen de $2.368.625 por semana. Activas: arcilla y horno.
La venta de fuentes sobra en 387,5. Precios sombra: 2.062,5 pesos por kg de arcilla y 276,25 pesos por
pieza de horno. Lectura: la arcilla es lo que más vale ampliar; las medias piezas se resuelven
redondeando (2.137 tazas y 762 fuentes caben).

**4.2.** El modelo del practicante da (2,5; 1,25) con un margen de $31.875 a la semana: dos lavados y
medio por semana con 90 horas de trabajo disponibles. El error: los coeficientes están en minutos y las
capacidades en horas. Corregido, el túnel tiene 2.400 min y la terminación 3.000 min:

$$\max\; 9000x + 7500y \quad\text{s.a.}\quad 12x + 8y \le 2400, \quad 10x + 20y \le 3000, \quad x, y \ge 0$$

Óptimo: (150, 75), con margen de $1.912.500 a la semana; las dos estaciones quedan activas. Lectura:
el solver no avisa los errores de unidades; el resultado absurdo sí, si uno lo mira.

**4.3.** Variables: porciones de legumbres ($L$), arroz ($A$) y huevo ($H$).

$$\min\; 340L + 115A + 165H \quad\text{s.a.}\quad 235L + 190A + 85H \ge 880, \quad 16L + 3A + 7H \ge 42, \quad 12L + 4A + 75H \le 290$$

Óptimo: 2,29 porciones de legumbres y 1,80 de arroz, sin huevo, con un costo de $985 por persona
(redondeado). Activas: calorías y proteína; el sodio sobra en 255,3 mg. El huevo no entra porque, por
peso, entrega menos calorías y proteína que la combinación de legumbres y arroz al mismo costo. Lectura:
una porción de 2,29 se sirve como «dos porciones y un cuarto»; en una dieta, las fracciones son
naturales.

**4.4.** Con el total $x_1 + x_2 + x_3$:

| Frase | Restricción lineal |
|---|---|
| (a) | $x_2 \le 0{,}30\,(x_1 + x_2 + x_3)$, o sea $-0{,}3x_1 + 0{,}7x_2 - 0{,}3x_3 \le 0$ |
| (b) | $x_1 \ge 2x_3$ |
| (c) | $10x_1 + 22x_2 + 6x_3 \ge 12\,(x_1 + x_2 + x_3)$, o sea $-2x_1 + 10x_2 - 6x_3 \ge 0$ |
| (d) | $x_1 / x_2 \le 3/2$ se escribe $2x_1 \le 3x_2$ |

Con 50, 30 y 20 kg (total 100): (a) 30 ≤ 30, se cumple justo (activa); (b) 50 ≥ 40, se cumple; (c) la
proteína es 12,8 % ≥ 12 %, se cumple; (d) $100 \le 90$ no se cumple: sobra ingrediente 1 respecto del 2.
Lectura: toda razón o porcentaje se vuelve lineal multiplicando, nunca dividiendo.

**4.5.** En palabras: se decide cuántos litros de cada vino base usar; se busca el menor costo; limitan
el volumen exacto, el rango de alcohol, la mitad de cabernet y lo disponible.

$$\min \sum_{v} c_v x_v \;\;\text{s.a.}\;\; \sum_v x_v = 9600, \;\; \sum_v a_v x_v \le 13{,}8 \sum_v x_v, \;\; \sum_v a_v x_v \ge 13{,}2 \sum_v x_v, \;\; x_{\text{cab}} \ge 0{,}5 \sum_v x_v, \;\; x_v \le S_v$$

El modelo OPL está en `modelos/u04_e05_ensamblaje.mod`. Óptimo: 4.800 L de cabernet, 2.880 de merlot y
1.920 de carmenere, con un costo de $15.494.400. Deciden la receta dos restricciones activas: el
cabernet justo en la mitad (es el más caro) y el alcohol justo en el máximo de 13,8 % (el carmenere es
el más barato, pero sube el alcohol; el merlot lo baja y por eso entra). Ningún vino base se agota. El
precio sombra del volumen es $1.614 por litro, igual al costo promedio ($15.494.400 / 9.600): como
todas las demás restricciones son proporciones, un litro más se hace con la misma receta. Lectura: en
una mezcla con solo proporciones, el costo crece en línea recta con el volumen.

**4.6.** Variables: millones en cada instrumento ($x_1$ a $x_4$).

$$\max\; 0{,}052x_1 + 0{,}068x_2 + 0{,}115x_3 + 0{,}083x_4$$

$$\text{s.a.}\;\; x_1 + x_2 + x_3 + x_4 = 50, \;\; x_1 + 2x_2 + 6x_3 + 3x_4 \le 3{,}0\,(x_1 + x_2 + x_3 + x_4), \;\; x_3 \le 0{,}35 \cdot 50, \;\; x_1 \ge 10, \;\; x_4 \le 12$$

Óptimo: 10 en depósito, 16 en renta fija, 12 en el fondo accionario y 12 en el bono. Retorno esperado:
$3.984.000, un 7,968 % sobre la cartera. Activas: el riesgo promedio (justo en 3,0), el mínimo de
depósito y el tope del bono. El fondo accionario queda en 12, bajo su tope de 17,5: no lo frena el
35 %, lo frena el riesgo. Lectura: subir el tope de acciones no cambia nada; lo que cambiaría la cartera
es aceptar más riesgo promedio.

**4.7.** (a) Patrones maximales de un tubo de 6 m (piezas de 2,4 · 1,7 · 1,1 m):

| Patrón | Piezas 2,4 · 1,7 · 1,1 | Pérdida (m) |
|---|---|---|
| P1 | 0 · 0 · 5 | 0,5 |
| P2 | 0 · 1 · 3 | 1,0 |
| P3 | 0 · 2 · 2 | 0,4 |
| P4 | 0 · 3 · 0 | 0,9 |
| P5 | 1 · 0 · 3 | 0,3 |
| P6 | 1 · 1 · 1 | 0,8 |
| P7 | 1 · 2 · 0 | 0,2 |
| P8 | 2 · 0 · 1 | 0,1 |

(b) Con $y_p$ = tubos cortados con el patrón $p$: $\min \sum_p y_p$ s.a.
$y_5 + y_6 + y_7 + 2y_8 \ge 130$ (piezas de 2,4), $y_2 + 2y_3 + 3y_4 + y_6 + 2y_7 \ge 205$ (de 1,7) y
$5y_1 + 3y_2 + 2y_3 + 3y_5 + y_6 + y_8 \ge 170$ (de 1,1). Una solución óptima del modelo lineal: 62,5
tubos con P3, 40,0 con P7 y 45,0 con P8, en total 147,5 tubos. (c) No sale entero. Subiendo P3 a 63 se
cumplen las tres demandas con 148 tubos, que es el óptimo entero. El pedido suma 847,5 m de piezas, o
sea al menos 141,25 tubos aunque no se perdiera nada: la diferencia es la pérdida que imponen los
largos. Lectura: los patrones elegidos son los que pierden poco (0,4, 0,2 y 0,1 m).

**4.8.** Variables: litros de leche $L$, kg de queso $Q$ y de yogur $Y$.

$$\max\; 7200Q + 1750Y - 440L \;\;\text{s.a.}\;\; 9{,}5Q + 1{,}15Y \le L, \;\; 0{,}125Q + 0{,}025Y \le 85, \;\; L \le 7600, \;\; Q \le 480, \;\; Y \le 2900$$

La primera es el balance: la leche que se usa no supera la que se compra. Óptimo: 4.285 L de leche,
100 kg de queso y 2.900 kg de yogur (en su tope), con margen de $3.909.600 por semana. Las horas están
activas; la leche no (se compran 4.285 de 7.600 L posibles). Precios sombra: el balance vale $440 por
litro, justo su precio, porque la leche sobra en el mercado y un litro más solo cuesta lo que se paga.
Una hora más de planta vale $24.160: permite 8 kg más de queso, que dejan $3.020 por kg ya descontada la
leche (el yogur deja $1.244 por kg, pero ya está en su tope). Lectura: el cuello es la planta, no la
leche.

**4.9.** (a) Conjuntos $I$ (ingredientes), $A \subset I$ (aceites), $K$ (proteína, lípidos), $J$
(inicio, engorda). Parámetros $a_{ik}$, $c_i$ en pesos por kg, $D_j$ en t, $l_{jk}$, $u_{jk}$, $\omega = 0{,}4$,
$h = 0{,}25$ y $S$ = 60 t. Variable $x_{ij}$ en toneladas.

$$\min \sum_{i, j} 1000\, c_i\, x_{ij} \;\;\text{s.a.}\;\; \sum_i x_{ij} = D_j \;\forall j, \;\; \sum_i a_{ik} x_{ij} \ge l_{jk} \sum_i x_{ij} \;\forall j, k, \;\; \sum_i a_{ik} x_{ij} \le u_{jk} \sum_i x_{ij} \;\forall j, k$$

$$x_{\text{ap},j} \ge \omega \sum_{i \in A} x_{ij} \;\forall j, \qquad x_{\text{hp},\text{inicio}} \ge h \sum_i x_{i,\text{inicio}}, \qquad \sum_j x_{\text{hp},j} \le S$$

El 1000 convierte pesos por kg en pesos por tonelada. El modelo está en
`modelos/u04_e09_alimento_salmones.mod`. (b) Óptimo, en toneladas:

| | Harina de pescado | Soya | Aceite de pescado | Aceite de raps |
|---|---|---|---|---|
| Inicio | 18,25 | 16,71 | 2,02 | 3,02 |
| Engorda | 26,14 | 64,16 | 11,88 | 17,82 |

Costo: $172.623.582 por semana. Quedan activas la proteína mínima, los lípidos mínimos y la regla del
40 % de aceite de pescado en los dos alimentos; el 25 % de harina en el inicio sobra (se usa 46 %), y
se usan 44,39 t de las 60 t de harina. Lo interesante: con dos fuentes de proteína y dos exigencias
activas, la harina y la soya quedan **fijadas** por la receta; el costo solo decide cómo se reparte el
aceite (el mínimo de pescado, porque es el caro). (c) Con 39 % de proteína en la engorda el costo sube a
$178.115.932: $5.492.349 más por semana. (d) Con 30 t el modelo es **infactible**: la proteína del
inicio y de la engorda exige al menos 44,39 t de harina de pescado (es lo mínimo que resulta si se
minimiza solo la harina). Lectura: un modelo infactible no es un error de OPL, es una respuesta: con
esos datos no hay receta posible, y hay que bajar una exigencia o conseguir harina.

**4.10.** (a) $\max\; 900.000x + 700.000y$ s.a. $4x + 3y \le 25$, $x + 3y \le 12$. Óptimo lineal:
(4,33; 2,56), con $5.688.889 al mes. (b) Hacia abajo, (4, 2): factible, $5.000.000. Al más cercano,
(4, 3): infactible, ocupa 13 m² de 12. (c) Enumerando los planes enteros factibles, el mejor es (6, 0):
seis hidrolavadoras, sin generadores, con $5.400.000 al mes. Usa 24 millones y 6 m². Lectura: el mejor
plan entero no está «cerca» del lineal: cambia de estructura. Cuando las cantidades son chicas, se
resuelve como problema entero, no se redondea.

---

## 12. Caso integrador · Estampa Sur decide su mezcla

> Este caso sigue a Estampa Sur, un taller de serigrafía ficticio, por todo el ramo. Las cifras salen
> de `verificacion/caso_estampa_sur_lp.py`. La unidad 2 resolvió la mezcla con dos prendas; la unidad 3
> puso precio a los polerones mirándolos solos.

**Lo que recibe.** El planteamiento en palabras de la unidad 1 y los tiempos por prenda que midió el
taller. Ahora entran las cinco prendas a competir por los mismos recursos. Los márgenes son los de
lista (el polerón, $3.940); la decisión de precio de la unidad 3 no entra acá, porque un margen que
depende de la cantidad vendida haría el modelo no lineal.

| Prenda | Margen (\$/u) | Estampado (s/u) | Planchado (s/u) | Tinta (g/u) | Venta máxima |
|---|---|---|---|---|---|
| Poleras básicas | 1.380 | 30 | 20 | 12 | 1.450 |
| Polerones | 3.940 | 90 | 50 | 25 | 520 |
| Poleras estampado doble | 2.270 | 110 | 30 | 22 | 380 |
| Bolsas | 960 | 20 | 40 | 8 | 860 |
| Gorros | 1.170 | 30 | 15 | 6 | 690 |

A la semana hay 40 h de estampado (144.000 s), 18 h de planchado (64.800 s) y 29.500 g de tinta.

**Paso 1 · En palabras.** Se decide cuántas unidades de cada prenda producir en la semana. Se busca el
mayor margen. Limitan las horas de estampado y de planchado, la tinta y lo que se puede vender.

**Paso 2 · Algebraico.** $I$ = prendas, $R$ = {estampado, planchado, tinta}; $c_i$ margen, $a_{ri}$
uso del recurso $r$ por unidad de $i$ (segundos o gramos), $b_r$ disponible, $d_i$ venta máxima;
$x_i$ = unidades de la prenda $i$ en la semana.

$$\max \sum_{i \in I} c_i x_i \quad\text{s.a.}\quad \sum_{i \in I} a_{ri}\, x_i \le b_r \;\; \forall r \in R, \qquad x_i \le d_i \;\; \forall i \in I, \qquad x_i \ge 0$$

**Paso 3 · En OPL** (`modelos/u04_mezcla.mod` y `u04_mezcla.dat`).

```opl
{string} Prendas  = ...;
{string} Recursos = ...;

float margen[Prendas]        = ...;   // CLP por unidad
float uso[Recursos][Prendas] = ...;   // segundos o gramos por unidad
float cap[Recursos]          = ...;   // segundos o gramos por semana
float demanda[Prendas]       = ...;   // unidades por semana, máximo

dvar float+ x[Prendas];

maximize sum(i in Prendas) margen[i] * x[i];

subject to {
  forall(r in Recursos)
    Capacidad: sum(i in Prendas) uso[r][i] * x[i] <= cap[r];
  forall(i in Prendas)
    Demanda: x[i] <= demanda[i];
}

execute {
  for (var r in Recursos)
    writeln("holgura_", r, " = ", Capacidad[r].slack, "  dual_", r, " = ", Capacidad[r].dual);
}
```

Las capacidades del `.dat` van en segundos (144000 y 64800) porque los usos están en segundos por
unidad: es la regla de unidades del punto 4.

**Desarrollo.**

| Prenda | Unidades | Estado |
|---|---|---|
| Poleras básicas | 833,75 | bajo su tope |
| Polerones | 520 | en su tope (costo reducido 1.052,5 por unidad) |
| Poleras estampado doble | 0 | no conviene (le faltan 250 de margen) |
| Bolsas | 294,375 | bajo su tope |
| Gorros | 690 | en su tope (costo reducido 472,5 por unidad) |

**Margen semanal: $4.289.275.**

| Recurso | Usado | Holgura | Precio sombra |
|---|---|---|---|
| Estampado | 98.400 s (27,33 h) | 45.600 s | 0 |
| Planchado | 64.800 s | 0 (activo) | 1,5 pesos por segundo ($5.400 por hora) |
| Tinta | 29.500 g | 0 (activo) | 112,5 pesos por gramo |

**Lectura.**

- **Planchado y tinta mandan; el estampado sobra.** Le quedan 45.600 s (12,67 h) ociosos: más horas de
  estampado no sirven para nada esta semana.
- **Polerones y gorros se venden hasta el tope.** Con los precios sombra, producir un polerón «gasta»
  50 × 1,5 + 25 × 112,5 = 2.887,5 pesos de planchado y tinta y deja 3.940: sobra 1.052,5, el costo
  reducido de su tope. Si se pudiera vender un polerón más, el margen subiría en esa cifra. Los gorros,
  igual, con 472,5.
- **La polera de estampado doble no entra.** Gasta 30 × 1,5 + 22 × 112,5 = 2.520 pesos de recursos
  escasos y deja 2.270: pierde 250 por unidad frente a usar esos recursos en otra prenda. Tendría que
  subir su margen en más de 250 pesos para entrar.
- **Poleras básicas y bolsas reparten lo que queda.** Por eso quedan en fracciones: son las dos
  variables que ajustan el planchado y la tinta exactos.
- **Las fracciones.** 833,75 poleras no se pueden hacer. Truncar a (833, 520, 0, 294, 690) es
  factible y deja $4.287.880, $1.395 menos. El mejor plan entero (lo calcula el verificador con un
  modelo entero) es 834 poleras, 520 polerones, 294 bolsas y 690 gorros, con $4.289.260: apenas \$15
  bajo el lineal. Con cantidades de cientos, redondear basta; el ramo Tópicos de Optimización
  (programación entera) trata los casos en que no.

**Lo que pasa a las unidades siguientes.** La unidad 5 extiende este modelo a cuatro semanas con
inventario y envío a tres tiendas. La unidad 7 lo implementa en OPL con todo detalle (`.mod`, `.dat` y
lectura de resultados). La unidad 10 explica de dónde salen los precios sombra de 1,5 y 112,5, y la
unidad 12 usa el de planchado ($5.400 por hora) para decidir si conviene pagar horas extra.

---

## 13. Para seguir

**En los libros del ramo.**

- Winston, *Investigación de operaciones: aplicaciones y algoritmos* (4.ª ed., 2005), capítulo 3, el
  que fija el programa: los problemas de dieta, de mezcla y de procesos de producción, con muchos
  ejemplos resueltos y propuestos (en la versión en inglés que entrega el curso son las secciones 3.4,
  3.8 y 3.9).
- Hillier y Lieberman, *Introducción a la investigación de operaciones* (7.ª ed., 2001), los capítulos
  de introducción a la programación lineal y de formulación, con casos de mezcla y de cartera.

**Abiertos y gratis.**

- Bradley, Hax y Magnanti, *Applied Mathematical Programming* (Addison-Wesley, 1977), en inglés, que el
  MIT deja descargar completo. El capítulo 1, «Mathematical Programming: An Overview», formula
  problemas de producción, mezcla y cartera; el capítulo 9, «Integer Programming», explica por qué
  redondear no basta: https://web.mit.edu/15.053/www/AMP.htm

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un problema de mezcla con dos productos y
tres ingredientes, déjame formularlo en forma compacta y corrígeme los índices».
