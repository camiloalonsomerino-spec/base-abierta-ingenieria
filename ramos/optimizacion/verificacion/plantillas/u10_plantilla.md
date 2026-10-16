---
ramo: Optimización
unidad: 10
titulo: Dualidad
version: 0.1 (15-10-2026)
requiere: [@@REQ@@]
alimenta: [11-holgura-complementaria, 12-sensibilidad]
verificacion: verificacion/u10_dualidad.py
---

# Unidad 10 · Dualidad

**Qué vas a poder hacer.** Escribir el dual de cualquier problema lineal (máximo o mínimo, con
restricciones $\le$, $\ge$ o $=$ y variables de cualquier signo); acotar el óptimo con el teorema
débil y certificarlo con el fuerte; leer la solución dual en la tabla final del simplex, e
interpretar cada variable dual como el precio de un recurso para decidir si conviene comprar más.

**Lo que necesitas antes.** Las unidades 8 y 9: la tabla del simplex, sus costos reducidos
$\bar c_j = c_j - c_B^\top B^{-1}A_j$ y las variables de holgura, exceso y artificiales. De la unidad 4,
qué es un recurso y qué es una demanda máxima en un modelo de producción.

**Tiempo.** Unas 5 horas: 2 de lectura con el ejemplo y 3 de práctica.

---

## 1. La idea: dos preguntas con los mismos datos

Un problema de producción responde **cómo usar** los recursos para ganar lo más posible. Con los
mismos datos se puede hacer otra pregunta: **cuánto vale** cada recurso.

Imagina que alguien quiere comprarle al taller todas sus horas y materiales de la semana, y ofrece
un precio $y_i$ por cada unidad del recurso $i$. El taller solo acepta si, para **cada** producto,
los recursos que ese producto usa le pagan al menos su margen; si no, le conviene más fabricarlo. El
comprador quiere pagar lo menos posible. Ese problema del comprador es el **dual**:

$$\text{Primal:}\quad \max\; z = c^\top x \quad \text{s.a.}\quad Ax \le b,\; x \ge 0$$
$$\text{Dual:}\quad \min\; w = b^\top y \quad \text{s.a.}\quad A^\top y \ge c,\; y \ge 0$$

- Cada **restricción** del primal tiene una **variable** dual; cada **variable** del primal, una
  **restricción** dual.
- La matriz se **transpone**: la restricción dual $j$ usa la columna $j$ de $A$ (lo que el producto
  $j$ consume de cada recurso).
- Los lados derechos del primal pasan a ser los costos del dual, y al revés.
- Un máximo pasa a mínimo y un mínimo, a máximo. El dual del dual es el primal.

---

## 2. Reglas de construcción

Cuando el primal no tiene la forma de arriba, el signo de cada variable dual y el tipo de cada
restricción dual salen de esta tabla. Para un primal de **máximo** se lee de izquierda a derecha;
para uno de **mínimo**, de derecha a izquierda (el primal es la columna derecha).

| Primal de máximo | Dual de mínimo |
|---|---|
| restricción $i$ del tipo $\le$ | $y_i \ge 0$ |
| restricción $i$ del tipo $\ge$ | $y_i \le 0$ |
| restricción $i$ del tipo $=$ | $y_i$ libre |
| $x_j \ge 0$ | restricción $j$ del tipo $\ge$ |
| $x_j \le 0$ | restricción $j$ del tipo $\le$ |
| $x_j$ libre | restricción $j$ del tipo $=$ |

**La intuición, para no memorizar.** En un máximo, la restricción «natural» es un recurso ($\le$):
tener más nunca hace daño, así que su precio es $\ge 0$. Una $\ge$ en un máximo es un compromiso
(un pedido firmado, un mínimo de calidad): exigir más solo puede costar, así que su precio es
$\le 0$. Una $=$ puede jugar a favor o en contra: su precio es libre. Con las variables pasa lo mismo:
una variable natural ($x_j \ge 0$) da una restricción dual natural; una rara, una rara; una libre,
una igualdad. En un mínimo, lo natural es la $\ge$ (un requisito que se cubre) y su precio es
$\ge 0$.

---

## 3. Teorema débil de dualidad

Para un primal de máximo, si $x$ es factible en el primal e $y$ es factible en el dual:

$$c^\top x \;\le\; b^\top y$$

**Por qué.** Con $x \ge 0$ y $A^\top y \ge c$, se tiene $c^\top x \le (A^\top y)^\top x = y^\top Ax$;
y con $y \ge 0$ y $Ax \le b$, $y^\top Ax \le y^\top b$. Todo valor del máximo queda bajo todo valor del
mínimo.

**Para qué sirve.**

- **Cotas sin resolver.** Cualquier plan factible da un piso para el óptimo y cualquier sistema de
  precios factible da un techo.
- **Certificado de óptimo.** Si encuentras $x$ e $y$ factibles con $c^\top x = b^\top y$, los dos son
  óptimos: no puede haber nada mejor que un valor que ya toca el techo.
- **No acotado.** Si el primal es no acotado, el dual es infactible (no hay techo posible). Y si el
  primal es factible y el dual infactible, el primal es no acotado.

| Primal \ Dual | Óptimo finito | No acotado | Infactible |
|---|---|---|---|
| **Óptimo finito** | posible, con $z^* = w^*$ | imposible | imposible |
| **No acotado** | imposible | imposible | posible |
| **Infactible** | imposible | posible | posible |

---

## 4. Teorema fuerte de dualidad

Si uno de los dos problemas tiene óptimo finito, el otro también, y los valores son iguales:
$z^* = w^*$.

**De dónde sale (la tabla lo demuestra).** En la tabla óptima de un máximo, defina
$y^\top = c_B^\top B^{-1}$. Entonces:

- La columna de cada $x_j$ trae $\bar c_j = c_j - y^\top A_j$. Que la tabla sea óptima
  ($\bar c_j \le 0$) es **exactamente** que $A_j^\top y \ge c_j$: la restricción dual $j$ se cumple.
- La columna de cada holgura $s_i$ trae $\bar c_{s_i} = 0 - y^\top e_i = -y_i$. Que sea $\le 0$ es que
  $y_i \ge 0$.
- El valor: $b^\top y = c_B^\top B^{-1} b = c_B^\top x_B = z$.

O sea, **el criterio de optimalidad del simplex es la factibilidad del dual**. El simplex busca un
vértice del primal cuyos precios $c_B^\top B^{-1}$ sean factibles en el dual; cuando los encuentra,
el teorema débil certifica que terminó.

---

## 5. Leer el dual en la tabla final

| Primal | Restricción | Dónde está $y_i$ en la tabla final |
|---|---|---|
| máximo | $\le$ (holgura $s_i$) | $y_i = -\bar c_{s_i}$ |
| mínimo | $\ge$ (exceso $e_i$) | $y_i = \bar c_{e_i}$ |
| mínimo, gran M | $=$ o $\ge$ (artificial $a_i$) | $y_i = M - \bar c_{a_i}$ |
| máximo, gran M | $\ge$ o $=$ (artificial $a_i$) | $y_i = -M - \bar c_{a_i}$ |

Las cuatro filas salen de la misma cuenta, $\bar c_j = c_j - y^\top A_j$, aplicada a una columna que
es $\pm$ un vector unitario. Y el costo reducido de una variable de decisión es, con signo cambiado,
la **holgura de su restricción dual**: $\bar c_j = c_j - A_j^\top y$ dice cuánto le falta (o le sobra)
al margen del producto $j$ para pagar los recursos que usa a esos precios.

---

## 6. Interpretación económica

$y_i$ es el **precio sombra** del recurso $i$: cuánto cambia el valor óptimo si el recurso aumenta en
una unidad, mientras la base óptima no cambie (el rango es materia de la unidad 12).

- **Unidades.** $y_i$ se mide en «unidades del objetivo por unidad del recurso»: pesos por hora, por
  segundo, por gramo. Un precio por segundo se pasa a hora multiplicando por 3.600.
- **Recurso que sobra, precio cero.** Si al óptimo le sobra un recurso, una unidad más no sirve:
  $y_i = 0$. (La unidad 11 lo vuelve una regla.)
- **El valor de los recursos es el valor de lo producido.** $z^* = \sum_i b_i y_i^*$: lo que el taller
  gana produciendo es exactamente lo que valen sus recursos a precios sombra.
- **Costo de oportunidad.** $\sum_i a_{ij}y_i$ es lo que valen los recursos que usa una unidad del
  producto $j$. Si es mayor que su margen, el producto no se fabrica: usarlos en otra cosa rinde más.

**Cuándo no aplica.** El precio sirve para cambios chicos: fuera del rango de la unidad 12 cambia la
base y cambia el precio. Si la solución óptima es degenerada, puede haber varios sistemas de precios
óptimos y «el» precio sombra no es único. En modelos con variables enteras no hay dual con estas
propiedades. Y en un **mínimo**, un $y_i > 0$ de una $\ge$ es lo que **sube el costo** por cada unidad
más de requisito, no una ganancia.

---

## 7. Ejemplo resuelto · una chocolatería

Una chocolatería de Puerto Varas produce por semana lotes de bombones (margen \$8.600 por lote) y de
tabletas (\$4.900 por lote). Un lote de bombones usa 2 horas de la templadora y uno de tabletas, 1
hora; hay 60 horas de templadora a la semana. El empaque toma 1 hora por lote de cualquiera de los
dos y hay 40 horas. Se venden a lo más 25 lotes de bombones.

**El primal en palabras.** Se decide cuántos lotes de cada producto hacer. Se busca el mayor margen.
Lo limitan la templadora, el empaque y la demanda de bombones.

$$\max\; z = 8{.}600x_1 + 4{.}900x_2 \quad \text{s.a.}\quad 2x_1 + x_2 \le 60 \qquad x_1 + x_2 \le 40 \qquad x_1 \le 25 \qquad x \ge 0$$

```opl
@@OPL:u10_chocolateria.mod@@
```

**Paso 1 · Resolver el primal con simplex.**

@@ALL:ej_simplex@@

El óptimo es 20 lotes de cada uno, con **$270.000** de margen.

**Paso 2 · Escribir el dual.** Tres restricciones $\le$ en un máximo: tres variables duales
$y_1, y_2, y_3 \ge 0$. Dos variables $x \ge 0$: dos restricciones $\ge$. La restricción dual de
$x_1$ usa la columna de $x_1$, que es $(2, 1, 1)$:

$$\min\; w = 60y_1 + 40y_2 + 25y_3 \quad \text{s.a.}\quad 2y_1 + y_2 + y_3 \ge 8{.}600 \qquad y_1 + y_2 \ge 4{.}900 \qquad y \ge 0$$

En palabras: un comprador que quiere quedarse con las horas de templadora, las de empaque y el
derecho a vender bombones busca el pago mínimo que la chocolatería aceptaría.

```opl
@@OPL:u10_chocolateria_dual.mod@@
```

**Paso 3 · Leer el dual en la tabla final.** Las holguras tienen $\bar c_{s_1} = -3{.}700$,
$\bar c_{s_2} = -1{.}200$ y $\bar c_{s_3} = 0$, así que $y^* = (3{.}700;\ 1{.}200;\ 0)$. Comprobación:
$w^* = 60 \cdot 3{.}700 + 40 \cdot 1{.}200 + 25 \cdot 0 = 270{.}000 = z^*$. Las dos restricciones duales
se cumplen justas ($2 \cdot 3{.}700 + 1{.}200 = 8{.}600$ y $3{.}700 + 1{.}200 = 4{.}900$), porque los dos
productos se fabrican. OPL da los mismos precios con `.dual` en el primal y el mismo óptimo al
resolver el dual.

**Paso 4 · El teorema débil antes de terminar.** La segunda tabla del simplex ya tenía un plan
factible, $\hat x = (25, 10)$, con un margen de $264.000. El precio $\hat y = (4{.}900;\ 0;\ 0)$ es
factible en el dual ($2 \cdot 4{.}900 \ge 8{.}600$ y $4{.}900 \ge 4{.}900$) y le pone a los recursos un
valor de $294.000. Sin resolver nada más ya se sabe que **el óptimo está entre $264.000 y $294.000**.
El óptimo, $270.000, cae adentro.

**Cómo se lee.**

- Una hora más de templadora vale **$3.700** y una de empaque, **$1.200**. El tope de bombones no
  vale nada: se hacen 20 y se podrían vender 25.
- Si alguien arrienda una hora de templadora por menos de $3.700, conviene (dentro del rango de la
  unidad 12). Una hora extra de empaque a \$1.500 no conviene: rinde \$1.200.
- Si un comprador ofrece menos de $270.000 por toda la capacidad de la semana, la chocolatería gana
  más produciendo.

---

## 8. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Armar la restricción dual $j$ con la **fila** $j$ de $A$ | La restricción dual $j$ usa la **columna** de $x_j$: lo que ese producto consume de cada recurso |
| Dar $y_i \ge 0$ a una $\ge$ de un máximo | En un máximo, $\ge$ da $y_i \le 0$ (un compromiso solo cuesta); revisa la tabla de la sección 2 |
| Creer que el dual de un máximo es otro máximo | Máximo ↔ mínimo, siempre |
| Olvidar la variable dual de una cota ($x_2 \le 830$) | Una cota escrita como restricción es una restricción más, con su propio precio |
| Leer $y_i$ como $\bar c_{s_i}$ sin cambiar el signo | En un máximo, $y_i = -\bar c_{s_i}$; la tabla óptima tiene esos $\bar c$ negativos |
| Leer el precio sombra de un mínimo como si fuera de un máximo | En un mínimo, $y_i > 0$ en una $\ge$ es cuánto **sube el costo**, no cuánto se gana |
| Dar vuelta las cotas del teorema débil | Lo que sale del máximo es piso; lo que sale del mínimo es techo |
| Mezclar pesos por segundo con pesos por hora | Escribe la unidad del precio: (pesos del objetivo) / (unidad del recurso) |
| Usar el precio sombra para cualquier cambio | Vale mientras la base no cambie (unidad 12) |

---

## 9. Práctica

Diez ejercicios: 10.1 a 10.4 básicos, 10.5 a 10.8 intermedios, 10.9 y 10.10 de desafío.

**10.1 · El dual de un máximo (básico).** Escribe el dual de
$\max\; z = 7x_1 + 5x_2 + 4x_3$ s.a. $2x_1 + x_2 + x_3 \le 40$, $x_1 + 3x_2 + 2x_3 \le 60$, $x \ge 0$.
El óptimo del primal es $x^* = (12, 16, 0)$ con $z^* = 164$. ¿Cuánto vale el óptimo del dual, sin
resolverlo?

**10.2 · El dual de una dieta (básico).** Un criadero mezcla tres forrajes. Por kilo, cuestan \$450,
\$380 y \$580; aportan 4, 2 y 5 unidades de proteína y 1, 3 y 1 de fibra. Cada animal necesita al día
al menos 40 de proteína y 30 de fibra. Escribe el modelo de mínimo costo y su dual. ¿Qué representa
cada variable dual y en qué unidades se mide?

**10.3 · El dual de un problema mixto (básico).** Escribe el dual de
$\min\; z = 5x_1 + 3x_2 - 8x_3$ s.a. $x_1 + x_2 - x_3 \ge 6$, $2x_1 - x_2 + x_3 \le 10$,
$x_1 + 2x_2 = 7$, con $x_1$ libre, $x_2 \ge 0$ y $x_3 \le 0$. El óptimo del primal es $x^* = (5, 1, 0)$
con $z^* = 28$. Comprueba que $y = (7;\ 0;\ -2)$ es factible en tu dual y que es óptimo.

**10.4 · Cotas con el teorema débil (básico).** Para el primal del 10.1: (a) comprueba que
$\hat x = (10, 10, 5)$ es factible en el primal y que $\hat y = (4, 2)$ lo es en el dual; (b) ¿qué dice
el teorema débil sobre $z^*$? (c) Repite con $x = (12, 16, 0)$ e $y = (3{,}2;\ 0{,}6)$: ¿qué concluyes?

**10.5 · El dual en la tabla final (intermedio).** Esta es la tabla final del simplex del 10.1:

@@FIN:e1_simplex@@

(a) Lee la solución dual y comprueba que $w^* = z^*$. (b) ¿Qué dice, en el dual, el $\bar c = -0{,}4$ de
$x_3$? (c) ¿Por qué $x_3$ no se produce, en términos de lo que valen sus recursos?

**10.6 · Pares sin óptimo (intermedio).** Para cada primal, escribe su dual y clasifica el par
(óptimo, no acotado o infactible) usando el teorema débil y sus consecuencias.
(a) $\max\; z = 2x_1 + x_2$ s.a. $x_1 - x_2 \le 4$, $x_1 - 2x_2 \le 2$, $x \ge 0$.
(b) $\max\; z = x_1 + x_2$ s.a. $x_1 - x_2 \le -2$, $-x_1 + x_2 \le -1$, $x \ge 0$.

**10.7 · El taller de velas (intermedio).** Un taller hace velas, jabones y difusores (margen por lote
\$5.200, \$3.600 y \$4.300). Por lote usan 3, 1 y 2 horas de vertido (hay 130), 2, 1 y 1 horas de
curado (hay 70) y 1, 1 y 2 horas de empaque (hay 60). El programa entrega el plan $x = (10, 50, 0)$ con
un margen de $232.000 y los precios duales $y = (0;\ 1{.}600;\ 2{.}000)$. (a) Escribe el dual y comprueba que
$y$ es factible y óptimo. (b) ¿Por qué el vertido vale cero? (c) Un proveedor ofrece 10 horas extra
de curado a \$1.150 la hora: ¿conviene y cuánto se gana? (d) Una empresa ofrece $220.000 por toda la
capacidad de la semana: ¿se acepta? (e) ¿Por qué no se hacen difusores?

**10.8 · El dual del sustrato (intermedio).** Escribe el dual del ejemplo de la unidad 9 (el saco de
sustrato: $\min\; 180x_1 + 310x_2$ s.a. $x_1 + x_2 = 60$, $x_1 + 4x_2 \ge 150$, $x_2 \le 40$, $x \ge 0$)
y lee su solución en la tabla final de la gran M de esa unidad. Interpreta cada precio.

**10.9 · Resolver el dual en vez del primal (desafío).** El primal del 10.2 necesita dos artificiales
para arrancar el simplex. Su dual no necesita ninguna. Resuelve el dual con simplex, lee en su tabla
final la mezcla óptima de forrajes y comprueba que el costo coincide.

**10.10 · El precio del pedido firmado (desafío).** Escribe el dual del caso de la unidad 9 (Estampa
Sur con el pedido de al menos 780 polerones). Lee su solución en la tabla final de la unidad 9,
comprueba que $w^* = z^*$ y explica por qué, con el pedido, un segundo de estampado vale \$46 y no los
32,67 pesos de la versión sin pedido.

---

## 10. Pautas

**10.1.** $\min\; w = 40y_1 + 60y_2$ s.a. $2y_1 + y_2 \ge 7$, $y_1 + 3y_2 \ge 5$, $y_1 + 2y_2 \ge 4$,
$y \ge 0$. Por el teorema fuerte, $w^* = z^* = 164$. Cada restricción dual es la columna de una $x_j$:
tres variables en el primal, tres restricciones en el dual.

**10.2.** Primal: $\min\; z = 450x_1 + 380x_2 + 580x_3$ s.a. $4x_1 + 2x_2 + 5x_3 \ge 40$,
$x_1 + 3x_2 + x_3 \ge 30$, $x \ge 0$. Dual: $\max\; w = 40y_1 + 30y_2$ s.a. $4y_1 + y_2 \le 450$,
$2y_1 + 3y_2 \le 380$, $5y_1 + y_2 \le 580$, $y \ge 0$. $y_1$ es el precio de una unidad de proteína y
$y_2$ el de una de fibra, en pesos por unidad: lo máximo que un vendedor de suplementos podría cobrar
para que su producto compita con los forrajes. Las restricciones dicen que ningún forraje puede salir
más caro que comprar sus nutrientes por separado. (El óptimo, en el 10.9: precios de \$97 por unidad de proteína y \$62 por unidad de fibra, y
un costo de **$5.740** por animal al día.)

**10.3.** Es un mínimo: se lee la tabla de la sección 2 de derecha a izquierda. La $\ge$ da
$y_1 \ge 0$, la $\le$ da $y_2 \le 0$ y la $=$ da $y_3$ libre. $x_1$ libre da una $=$, $x_2 \ge 0$ da
una $\le$ y $x_3 \le 0$ da una $\ge$:

$$\max\; w = 6y_1 + 10y_2 + 7y_3 \quad \text{s.a.}\quad y_1 + 2y_2 + y_3 = 5 \qquad y_1 - y_2 + 2y_3 \le 3 \qquad -y_1 + y_2 \ge -8$$

Con $y = (7;\ 0;\ -2)$: $7 + 0 - 2 = 5$ ✓, $7 - 0 - 4 = 3 \le 3$ ✓, $-7 + 0 = -7 \ge -8$ ✓, y los signos
($7 \ge 0$, $0 \le 0$, $-2$ libre) ✓. El valor es $w = 42 + 0 - 14 = 28 = z^*$: por el teorema débil
(corolario del certificado) los dos son óptimos. El precio de la igualdad es −2: si el lado derecho
de $x_1 + 2x_2 = 7$ sube en 1, el costo **baja** en 2.

**10.4.** (a) $\hat x$: $20 + 10 + 5 = 35 \le 40$ y $10 + 30 + 10 = 50 \le 60$ ✓. $\hat y$:
$8 + 2 = 10 \ge 7$, $4 + 6 = 10 \ge 5$, $4 + 4 = 8 \ge 4$ ✓. (b) $z(\hat x) = 140$ y
$w(\hat y) = 280$, así que $140 \le z^* \le 280$: una brecha de 140 sin haber resuelto nada.
(c) $z = 164$ y $w = 40 \cdot 3{,}2 + 60 \cdot 0{,}6 = 164$: el piso toca el techo, los dos son
óptimos.

**10.5.** (a) $y_1 = -\bar c_{s_1} = 3{,}2$ e $y_2 = -\bar c_{s_2} = 0{,}6$.
$w = 40 \cdot 3{,}2 + 60 \cdot 0{,}6 = 128 + 36 = 164 = z^*$. (b) $\bar c_{x_3} = 4 - (3{,}2 + 2 \cdot 0{,}6) = -0{,}4$:
la tercera restricción dual tiene holgura 0,4 ($y_1 + 2y_2 = 4{,}4 \ge 4$). (c) Los recursos que usa
una unidad de $x_3$ valen 4,4 a precios sombra y deja solo 4: fabricarla quitaría recursos a $x_1$ y
$x_2$, que rinden más.

**10.6.** (a) Dual: $\min\; 4y_1 + 2y_2$ s.a. $y_1 + y_2 \ge 2$, $-y_1 - 2y_2 \ge 1$, $y \ge 0$. La
segunda pide un número negativo $\ge 1$: **dual infactible**. El primal es factible (el origen) y
entonces es **no acotado** (por ejemplo, $x = (t, t)$ cumple todo y $z = 3t$). (b) Sumando las dos
restricciones del primal: $0 \le -3$, **infactible**. Dual: $\min\; -2y_1 - y_2$ s.a.
$y_1 - y_2 \ge 1$, $-y_1 + y_2 \ge 1$, $y \ge 0$; sumando, $0 \ge 2$: **también infactible**. Es la
casilla «infactible–infactible» de la tabla de la sección 3.

**10.7.** (a) $\min\; w = 130y_1 + 70y_2 + 60y_3$ s.a. $3y_1 + 2y_2 + y_3 \ge 5{.}200$,
$y_1 + y_2 + y_3 \ge 3{.}600$, $2y_1 + y_2 + 2y_3 \ge 4{.}300$, $y \ge 0$. Con $y = (0;\ 1{.}600;\ 2{.}000)$:
$5{.}200 \ge 5{.}200$, $3{.}600 \ge 3{.}600$ y $5{.}600 \ge 4{.}300$ ✓. $w = 70 \cdot 1{.}600 + 60 \cdot 2{.}000 = 232{.}000 = z$:
óptimo. (b) El plan usa $30 + 50 = 80$ de las 130 horas de vertido; sobran 50, y una hora más no
sirve. (c) Cada hora de curado vale **$1.600** y cuesta \$1.150: se ganan
10 · (1.600 − 1.150) = **$4.500**. Re-resolviendo con 80 horas de curado el margen sube a
$248.000, justo 10 · 1.600 = 16.000 más: en ese tramo el precio sigue valiendo. (d) No: para el
taller los recursos valen $w^*$, es decir, $232.000; $220.000 es menos de lo que gana usándolos. (e) Los recursos de
un lote de difusores valen $2 \cdot 0 + 1{.}600 + 2 \cdot 2{.}000 = 5{.}600$ y su margen es \$4.300: le
faltan **$1.300**, que es su costo reducido. El empaque (\$2.000 la hora) es caro y el difusor usa 2
horas.

**10.8.** El primal es un mínimo: la $=$ da $y_1$ libre, la $\ge$ da $y_2 \ge 0$ y la $\le$ da
$y_3 \le 0$.

$$\max\; w = 60y_1 + 150y_2 + 40y_3 \quad \text{s.a.}\quad y_1 + y_2 \le 180 \qquad y_1 + 4y_2 + y_3 \le 310$$

En la tabla final de la gran M, las artificiales tienen $\bar c_{a_1} = M - 410/3$ y
$\bar c_{a_2} = M - 130/3$, y la holgura $\bar c_{s_3} = 0$. Con $y_i = M - \bar c_{a_i}$:
$y = (410/3;\ 130/3;\ 0)$, que es $(136{,}67;\ 43{,}33;\ 0)$. También $\bar c_{e_2} = 130/3 = y_2$. Valor:
$60 \cdot 410/3 + 150 \cdot 130/3 = 8{.}200 + 6{.}500$, o sea **$14.700**, el costo del saco. Lectura:
un gramo más de nitrógeno exigido sube el costo en unos \$43; un litro más de saco (con el mismo
nitrógeno) lo sube en unos \$137, y el tope de compost no cuesta nada porque sobran 10 litros. OPL da
los mismos `.dual`.

**10.9.** El dual (del 10.2) tiene solo restricciones $\le$ con lado derecho positivo: arranca en el
origen con las holguras.

@@ALL:e9_simplex@@

El óptimo del dual es $y = (97, 62)$ con $w = 5{.}740$. La mezcla de forrajes está en las holguras
del dual: $x_j = -\bar c_{s_j}$, o sea $x = (6, 8, 0)$: 6 kilos del primero, 8 del segundo y nada del
tercero, con costo $450 \cdot 6 + 380 \cdot 8 = 5{.}740$. Se evitaron las dos artificiales: cuando el
primal es un mínimo con muchas $\ge$, a veces conviene resolver el dual.

**10.10.** El primal es un máximo con tres $\le$ y una $\ge$, así que $y_1, y_2, y_3 \ge 0$ e
$y_4 \le 0$:

$$\min\; w = 108{.}000y_1 + 64{.}800y_2 + 830y_3 + 780y_4$$
$$\text{s.a.}\quad 30y_1 + 20y_2 \ge 1{.}380 \qquad 90y_1 + 50y_2 + y_3 + y_4 \ge 3{.}940$$

De la tabla final de la unidad 9: $y_1 = -\bar c_{s_1} = 46$, $y_2 = y_3 = 0$ y, para el exceso de una
$\ge$ en un máximo, $y_4 = \bar c_{e_4} = -200$. Valor: $108{.}000 \cdot 46 - 780 \cdot 200 = 4{.}968{.}000 - 156{.}000$,
o sea **$4.812.000**, igual a $z^*$. Sin pedido, el segundo de estampado se reparte entre poleras y
polerones y vale 32,67 pesos. Con el pedido, los polerones quedan fijos en su mínimo y el segundo
extra solo puede ir a poleras: $1.380/30 = 46$. El pedido tiene precio −200: cada polerón más que
se comprometa le quita \$200 al margen.

---

## 11. Caso integrador · cuánto vale cada recurso de Estampa Sur

> Este caso sigue a Estampa Sur por todo el ramo. La unidad 8 resolvió con simplex la versión de dos
> productos (1.440 poleras y 720 polerones, **$4.824.000**) y la unidad 4 la mezcla completa de cinco
> prendas (**$4.289.275**). Acá se escribe el dual de cada una y se lee cuánto vale cada recurso.

### a) La versión de dos productos

$$\min\; w = 108{.}000y_1 + 64{.}800y_2 + 830y_3 \quad \text{s.a.}\quad 30y_1 + 20y_2 \ge 1{.}380 \qquad 90y_1 + 50y_2 + y_3 \ge 3{.}940 \qquad y \ge 0$$

$y_1$ y $y_2$ son pesos por segundo de estampado y de planchado; $y_3$, pesos por polerón de
demanda. La tabla final del primal:

@@FIN:u2_simplex@@

Se lee $y^* = (98/3;\ 20;\ 0)$: **32,67 pesos por segundo de estampado** y **20 por segundo de
planchado**, o sea $117.600 y $72.000 por hora. La demanda de polerones no vale nada: sobran 110. El
dual da $w^* = 108{.}000 \cdot 98/3 + 64{.}800 \cdot 20 = 3{.}528{.}000 + 1{.}296{.}000$, que es
**$4.824.000**, igual a $z^*$. OPL lo confirma por dos caminos: el `.dual` del primal y el óptimo del dual.

```opl
@@OPL:u10_dual_dos_productos.mod@@
```

### b) La mezcla de cinco prendas

Con los conjuntos de la unidad 4 (prendas $i$, recursos $r$), el primal es
$\max \sum_i m_i x_i$ s.a. $\sum_i a_{ri}x_i \le b_r$ para cada recurso y $x_i \le d_i$ para cada
prenda. El dual tiene una variable $y_r \ge 0$ por recurso y una $u_i \ge 0$ por demanda máxima:

$$\min\; w = \sum_r b_r\, y_r + \sum_i d_i\, u_i \quad \text{s.a.}\quad \sum_r a_{ri}\, y_r + u_i \ge m_i \quad \forall i \qquad y, u \ge 0$$

```opl
@@OPL:u10_dual_mezcla.mod@@
```

| Restricción del primal | Disponible | Precio dual | Aporte a $w^*$ |
|---|---|---|---|
| Estampado | 144.000 s | 0 | 0 |
| Planchado | 64.800 s | 1,5 por segundo | $97.200 |
| Tinta | 29.500 g | 112,5 por gramo | $3.318.750 |
| Demanda de polerones | 520 | 1.052,5 por unidad | $547.300 |
| Demanda de gorros | 690 | 472,5 por unidad | $326.025 |
| Demanda de las otras tres | 1.450, 380 y 860 | 0 | 0 |
| **Total** | | | **$4.289.275** |

El total es el margen óptimo de la unidad 4: los recursos valen exactamente lo que permiten ganar.
OPL entrega los mismos precios con `.dual` en `u10_mezcla.mod` y al resolver `u10_dual_mezcla.mod`.

**Lectura.**

- **El estampado no vale nada** en la mezcla completa (le sobran 45.600 segundos), aunque en la
  versión de dos productos valía 32,67 pesos por segundo. El precio sombra no es una propiedad del
  recurso: depende de todo el modelo. Con 40 horas, cinco prendas y la tinta, el estampado deja de
  ser el cuello.
- **Una hora de planchado vale $5.400** ($1{,}5 \cdot 3{.}600$). La unidad 12 la compara con lo que
  cuesta una hora extra.
- **Un gramo de tinta vale 112,5 pesos.** Es el recurso más apretado.
- **Un polerón más de demanda vale 1.052,5 pesos:** su margen (3.940) menos lo que valen sus 50
  segundos de planchado (75) y sus 25 gramos de tinta (2.812,5). Lo mismo con los gorros: 472,5.
- **Las poleras de estampado doble no se hacen** porque sus recursos valen 2.520 a precios sombra y
  dejan 2.270: la restricción dual tiene holgura 250. Cada unidad le quitaría \$250 al margen.

**Lo que pasa a la unidad 11.** El par $(x^*, y^*)$ de la mezcla completa, con las holguras de las
dos columnas: la unidad 11 comprueba que cada recurso con holgura tiene precio cero y que cada prenda
que se fabrica cumple su restricción dual justa. **Y a la unidad 12:** el planchado a $5.400 la hora.

---

## 12. Para seguir

**En los libros del ramo.**

- Winston, *Investigación de operaciones: aplicaciones y algoritmos* (4.ª ed., 2005), el capítulo de
  análisis de sensibilidad y dualidad: cómo se arma el dual de un problema no normal, los teoremas y
  la interpretación económica de los precios sombra.
- Hillier y Lieberman, *Introducción a la investigación de operaciones* (7.ª ed., 2001), el capítulo
  de teoría de dualidad y análisis de sensibilidad.

**Abierto y gratis.**

- Bradley, Hax y Magnanti, *Applied Mathematical Programming* (Addison-Wesley, 1977), en inglés, que
  el MIT publica completo. El capítulo 4 (*Duality in Linear Programming*) trae el dual como problema
  de precios y la lectura en la tabla: https://web.mit.edu/15.053/www/AMP.htm

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un primal de mínimo con una restricción de
igualdad y una variable libre, y corrígeme el dual».
