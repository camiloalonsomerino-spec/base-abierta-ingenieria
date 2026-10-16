---
ramo: Optimización
unidad: 11
titulo: Holgura complementaria
version: 0.1 (15-10-2026)
requiere: [04-modelamiento-produccion-y-mezcla, 10-dualidad]
alimenta: [12-sensibilidad]
verificacion: verificacion/u11_holgura_complementaria.py
---

# Unidad 11 · Holgura complementaria

**Qué vas a poder hacer.** Comprobar si una solución que alguien propone es óptima sin volver a
resolver el modelo, obtener la solución del dual desde la del primal (y al revés) y leer, par por
par, qué recurso vale cero, qué producto paga exactamente sus recursos y cuál no alcanza a pagarlos.

**Lo que necesitas antes.** La unidad 10 (dualidad): escribir el dual de un primal, los teoremas
débil y fuerte, y el precio sombra como el valor de una unidad más de recurso. De la unidad 4, la
mezcla de Estampa Sur. Y resolver sistemas lineales de 2×2 y 3×3 a mano.

**Tiempo.** Unas 3,5 horas: 1 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. La idea

En el óptimo de un modelo lineal pasan dos cosas que el sentido común ya sospecha:

- **Un recurso que sobra no vale nada.** Si al taller le quedan horas de máquina sin usar, una hora
  más no cambia el margen: su precio sombra es cero.
- **Un producto que se fabrica paga exactamente sus recursos.** Si un producto está en el plan, su
  margen es igual a lo que valen, a precios sombra, los recursos que consume. Si dejara más, convendría
  fabricar más; si dejara menos, convendría fabricar menos.

La holgura complementaria convierte estas dos frases en ecuaciones. Con ellas se puede revisar una
solución en minutos, pasar del primal al dual sin resolver el dual y explicar en palabras de negocio
por qué el plan óptimo es el que es.

---

## 2. El teorema

### Notación

Primal de máximo con $m$ restricciones y $n$ variables, y su dual (unidad 10):

$$\text{(P)}\ \max\ c^{T}x \quad \text{s.a.}\ Ax \le b,\ x \ge 0 \qquad\qquad \text{(D)}\ \min\ b^{T}y \quad \text{s.a.}\ A^{T}y \ge c,\ y \ge 0$$

Cada restricción del primal tiene una **holgura** y cada restricción del dual también:

$$s_i = b_i - a_i x \ \ (i=1..m) \qquad\qquad t_j = a_j^{T}y - c_j \ \ (j=1..n)$$

donde $a_i$ es la fila $i$ de $A$ (lo que consume la restricción $i$) y $a_j$ la columna $j$ (lo que
consume el producto $j$). La holgura dual $t_j$ es «lo que valen los recursos del producto $j$ menos su
margen». Con signo contrario es el **costo reducido**: $d_j = c_j - a_j^{T}y = -t_j$.

### De dónde sale

La diferencia entre el valor del dual y el del primal se puede escribir así:

$$b^{T}y - c^{T}x = \underbrace{y^{T}(b - Ax)}_{\sum_i y_i\, s_i} + \underbrace{(A^{T}y - c)^{T}x}_{\sum_j t_j\, x_j}$$

Si $x$ e $y$ son factibles, todos los factores son no negativos, así que cada producto $y_i s_i$ y
$t_j x_j$ es no negativo (por eso el dual siempre acota al primal: teorema débil). En el óptimo la
diferencia es cero (teorema fuerte). Una suma de términos no negativos vale cero **solo si cada término
vale cero**. Eso es todo el teorema.

> **Teorema de la holgura complementaria.** Sean $x$ factible para (P) e $y$ factible para (D).
> Ambas son óptimas si y solo si
> $$y_i\, s_i = 0 \ \ \forall i \qquad\text{y}\qquad x_j\, t_j = 0 \ \ \forall j$$

### Las parejas

| En el primal | Su pareja en el dual | Lo que dice la condición |
|---|---|---|
| Restricción $i$, con holgura $s_i$ | Variable $y_i$ | Si $s_i > 0$, entonces $y_i = 0$. Si $y_i > 0$, entonces $s_i = 0$ |
| Variable $x_j$ | Restricción dual $j$, con holgura $t_j$ | Si $x_j > 0$, entonces $t_j = 0$. Si $t_j > 0$, entonces $x_j = 0$ |

Las implicancias van en un solo sentido. Una restricción **activa** ($s_i = 0$) puede tener precio
sombra cero (pasa en las soluciones degeneradas, ejercicio 11.9) y un producto con $t_j = 0$ puede no
fabricarse (pasa cuando hay óptimos alternativos, ejercicio 11.10). «Uno de los dos es cero» admite que
los dos lo sean.

### Otras formas del primal

La condición es siempre la misma (variable por holgura de su pareja igual a cero); lo que cambia es el
signo que se exige a cada cosa.

| Primal | Restricción | Signo del dual | Restricción dual de una $x_j \ge 0$ |
|---|---|---|---|
| Máximo | $\le$ | $y_i \ge 0$ | $a_j^{T}y \ge c_j$ |
| Máximo | $\ge$ | $y_i \le 0$ | $a_j^{T}y \ge c_j$ |
| Máximo o mínimo | $=$ | libre | (la condición $y_i s_i = 0$ se cumple sola: $s_i = 0$) |
| Mínimo | $\ge$ | $y_i \ge 0$ | $a_j^{T}y \le c_j$ |
| Mínimo | $\le$ | $y_i \le 0$ | $a_j^{T}y \le c_j$ |

En un problema de mínimo la «holgura» de una restricción $\ge$ es el **excedente** $a_i x - b_i$, y la
holgura dual de $x_j$ es $c_j - a_j^{T}y$ (lo que cuesta el insumo menos lo que valen sus aportes).

---

## 3. Comprobar si una solución propuesta es óptima

Alguien trae un plan. Sin resolver el modelo, se revisa en cinco pasos:

1. **Factibilidad primal.** Calcula el lado izquierdo de cada restricción y su holgura. Si alguna se
   viola, la propuesta no sirve y no hay nada más que revisar.
2. **Recursos que sobran.** Por cada restricción con holgura positiva escribe $y_i = 0$.
3. **Productos que se fabrican.** Por cada $x_j > 0$ escribe $a_j^{T}y = c_j$.
4. **Resuelve el sistema.** Hay tres salidas:
   - *No tiene solución.* Ningún vector de precios acompaña a esa propuesta: **no es óptima**.
   - *Solución única.* Pasa al paso 5.
   - *Infinitas soluciones* (más incógnitas que ecuaciones independientes, típico de una solución
     degenerada). Busca si alguna de ellas cumple el paso 5.
5. **Factibilidad dual.** Revisa el signo de cada $y_i$ y que los productos que **no** se fabrican
   cumplan su restricción dual ($a_j^{T}y \ge c_j$ en un máximo). Si todo se cumple, la propuesta es
   óptima y además $c^{T}x = b^{T}y$. Si un producto la viola, ese producto es el que mejoraría el plan.

**Por qué basta.** Los pasos 2 y 3 fuerzan la holgura complementaria; los pasos 1 y 5 dan la
factibilidad de los dos problemas. El teorema dice que esas tres cosas juntas son exactamente el
óptimo. Saltarse el paso 5 es el error más común: el sistema casi siempre tiene solución, pero esa
solución puede tener un precio negativo o dejar un producto que paga más que sus recursos.

---

## 4. Del dual al primal (y del primal al dual)

El mismo razonamiento funciona en la otra dirección. Si alguien entrega los precios sombra óptimos
$y^{*}$:

- Toda restricción con $y_i^{*} > 0$ está **activa**: se escribe como igualdad.
- Todo producto con $t_j > 0$ (sus recursos valen más que su margen) vale **cero** en el primal.
- Con lo que queda se resuelve un sistema, normalmente pequeño.

Esto es útil cuando el dual tiene dos variables y se resuelve con el método gráfico, aunque el primal
tenga cinco: se resuelve el dual en el plano y se recupera el primal con holgura complementaria. Del
primal al dual es el procedimiento de la sección 3: lo que entrega el paso 4 es el dual óptimo.

---

## 5. La lectura económica

| Lo que se ve en la solución | Lo que significa |
|---|---|
| Un recurso con holgura | Vale cero en el margen: pagar por más de ese recurso no sirve |
| Un recurso con precio sombra positivo | Se usa completo: es uno de los que limitan el plan |
| Un producto que se fabrica entre sus cotas | Su margen es igual a lo que valen sus recursos: no deja ni pierde a precios sombra |
| Un producto que no se fabrica | Sus recursos valen más que su margen; la diferencia (el costo reducido) es lo que le falta |
| Un tope de demanda activo con dual positivo | El producto deja más de lo que valen sus recursos; el dual es lo que vale vender una unidad más |
| $z^{*} = w^{*}$ | El margen total se reparte exacto entre los recursos y los topes que limitan el plan |

### Cuándo NO aplica tal cual

- **Hace falta factibilidad en los dos lados.** Holgura complementaria sola no prueba nada; el
  ejercicio 11.5 y el plan B del ejemplo lo muestran.
- **Soluciones degeneradas.** Si una variable básica vale cero, o si más restricciones de las
  necesarias pasan por el vértice, los precios sombra no son únicos: el precio de subir un recurso puede
  no ser el de bajarlo (11.9).
- **Modelos enteros.** Con variables enteras no hay dual que cierre la brecha, y estas condiciones no
  certifican el óptimo.
- **El precio vale en la frontera.** El precio sombra mide el efecto de una unidad más. Hasta dónde
  sigue valiendo es la pregunta de la unidad 12.

---

## 6. Ejemplo resuelto · Tostaduría de café

Una tostaduría de Valdivia vende tres mezclas en bolsas de 1 kg. Cada semana tiene 2.400 minutos de
tostadora, 1.000 minutos de envasadora y 350 bolsas con válvula (el proveedor no entrega más).

| Mezcla | Margen ($/kg) | Tostadora (min/kg) | Envasadora (min/kg) | Bolsas por kg |
|---|---|---|---|---|
| Espresso ($x_1$) | 4.200 | 6 | 3 | 1 |
| Filtro ($x_2$) | 3.450 | 4 | 2 | 1 |
| Descafeinado ($x_3$) | 5.100 | 9 | 2 | 1 |
| **Disponible** | | 2.400 | 1.000 | 350 |

**En palabras.** Se decide cuántos kilos de cada mezcla tostar en la semana; se busca el mayor margen;
limitan la tostadora, la envasadora y las bolsas.

**Algebraico.** Conjuntos $P$ (mezclas) y $R$ (recursos); parámetros $c_p$ (margen), $a_{rp}$ (consumo)
y $b_r$ (disponible); variable $x_p \ge 0$ (kg de la mezcla $p$).

$$\max \sum_{p\in P} c_p x_p \quad \text{s.a.} \quad \sum_{p\in P} a_{rp}\, x_p \le b_r \ \ \forall r\in R, \qquad x_p \ge 0 \ \ \forall p\in P$$

Su dual tiene un precio por recurso: $y_1$ por minuto de tostadora, $y_2$ por minuto de envasadora e
$y_3$ por bolsa.

$$\begin{aligned} \min\ & 2{.}400\,y_1 + 1{.}000\,y_2 + 350\,y_3 \\ \text{s.a.}\ & 6y_1 + 3y_2 + y_3 \ge 4{.}200 \quad 4y_1 + 2y_2 + y_3 \ge 3{.}450 \quad 9y_1 + 2y_2 + y_3 \ge 5{.}100 \quad y \ge 0 \end{aligned}$$

El encargado propone el **plan A**: 250 kg de espresso, nada de filtro y 100 kg de descafeinado. La
socia propone el **plan B**: 200 kg de espresso, 50 de filtro y 100 de descafeinado.

**Paso 1 · Factibilidad y holguras del plan A.**

| Recurso | Usado | Disponible | Holgura |
|---|---|---|---|
| Tostadora | $6(250) + 9(100) = 2{.}400$ | 2.400 | 0 |
| Envasadora | $3(250) + 2(100) = 950$ | 1.000 | 50 |
| Bolsas | $250 + 100 = 350$ | 350 | 0 |

**Paso 2 · Condiciones.** La envasadora sobra, así que $y_2 = 0$. Espresso y descafeinado se tuestan,
así que sus restricciones duales van con igualdad:

$$6y_1 + y_3 = 4{.}200 \qquad 9y_1 + y_3 = 5{.}100$$

Restando, $3y_1 = 900$: $y_1 = 300$ y $y_3 = 4{.}200 - 1{.}800 = 2{.}400$.

**Paso 3 · Factibilidad dual.** Los tres precios son no negativos. El filtro no se tuesta, así que
basta con que sus recursos valgan al menos su margen: $4(300) + 2(0) + 2{.}400 = 3{.}600 \ge 3{.}450$.
Se cumple, con holgura dual 150 (costo reducido −150).

**Paso 4 · Cierre.** $w = 2{.}400(300) + 1{.}000(0) + 350(2{.}400) = 720{.}000 + 840{.}000 = 1{.}560{.}000$,
igual al margen del plan A: $4{.}200(250) + 5{.}100(100) = 1{.}560{.}000$. El plan A es óptimo, con
margen **$1.560.000** y precios **\$300 por minuto de tostadora**, $0 por minuto de envasadora y
**$2.400 por bolsa**.

**El plan B.** Usa 2.300 minutos de tostadora, 900 de envasadora y 350 bolsas: holguras 100, 100 y 0.
Entonces $y_1 = y_2 = 0$ y, como las tres mezclas se tuestan, la bolsa tendría que valer a la vez
4.200, 3.450 y 5.100. El sistema no tiene solución: **no hay precios que acompañen al plan B** y no es
óptimo. Su margen es $1.522.500, $37.500 menos que el plan A.

**Del dual al primal.** Si alguien entrega solo $y^{*} = (300;\ 0;\ 2{.}400)$: tostadora y bolsas
tienen precio positivo, así que están activas; el filtro tiene holgura dual 150, así que $x_2 = 0$.
Queda $6x_1 + 9x_3 = 2{.}400$ y $x_1 + x_3 = 350$, que da $x_1 = 250$ y $x_3 = 100$: el plan A.

**En OPL.** El modelo es genérico (conjuntos y parámetros) y los datos van aparte
(`modelos/u11_mezcla.mod` con `modelos/u11_tostaduria.dat`). El bloque `execute` imprime lo que pide
la holgura complementaria: holgura y dual de cada restricción, y costo reducido de cada variable.

```opl
{string} Productos = ...;
{string} Recursos  = ...;
float margen[Productos]        = ...;
float uso[Recursos][Productos] = ...;
float cap[Recursos]            = ...;

dvar float+ x[Productos];
dexpr float Margen = sum(p in Productos) margen[p] * x[p];
maximize Margen;

subject to {
  forall(r in Recursos)
    Capacidad:
      sum(p in Productos) uso[r][p] * x[p] <= cap[r];
}

execute {
  writeln("margen = ", Margen);
  for (var p in Productos) {
    writeln("x[", p, "] = ", x[p]);
    writeln("costo_reducido[", p, "] = ", x[p].reducedCost);
  }
  for (var r in Recursos) {
    writeln("holgura[", r, "] = ", Capacidad[r].slack);
    writeln("dual[", r, "] = ", Capacidad[r].dual);
  }
}
```

```text
margen = 1560000
x[espresso] = 250          costo_reducido[espresso] = 0
x[filtro] = 0              costo_reducido[filtro] = -150
x[descafeinado] = 100      costo_reducido[descafeinado] = 0
holgura[tostadora] = 0     dual[tostadora] = 300
holgura[envasadora] = 50   dual[envasadora] = 0
holgura[bolsas] = 0        dual[bolsas] = 2400
```

**Cómo se lee.**

- La tostadora y las bolsas son las que limitan: un minuto más de tostadora vale \$300 y una bolsa más
  vale $2.400 de margen. La envasadora sobra 50 minutos y no vale nada: no tiene sentido pagar un
  turno extra de envasado.
- Espresso y descafeinado pagan justo sus recursos: $6(300) + 2{.}400 = 4{.}200$ y
  $9(300) + 2{.}400 = 5{.}100$.
- El filtro usa recursos que valen $3.600 por kilo y deja $3.450: a precios sombra, cada kilo de
  filtro pierde 150. Por eso no entra. La decisión: aprobar el plan A y, si se quiere crecer, negociar
  más bolsas con el proveedor (la unidad 12 dice cuántas siguen valiendo $2.400).

---

## 7. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Dar por óptima una propuesta porque el sistema de holgura complementaria tiene solución | Falta el paso 5: signos del dual y restricciones duales de los productos que no se fabrican (11.5) |
| Creer que toda restricción activa tiene precio sombra positivo | La implicancia es al revés: precio positivo obliga a activa. Activa con precio cero pasa en soluciones degeneradas (11.9) |
| Creer que un producto con costo reducido cero se fabrica | Puede haber óptimos alternativos: cero no obliga a nada (11.10) |
| Exigir $y \ge 0$ a una restricción de igualdad, o usar $\ge$ en el dual de un mínimo | Usa la tabla de signos de la sección 2: la igualdad tiene dual libre; en un mínimo la restricción dual es $\le$ (11.6, 11.7) |
| Olvidar los topes de demanda al plantear el sistema | Un tope es una restricción más con su propio dual; sin él, el sistema de un producto que llega a su tope no cuadra (11.8 y el caso) |
| Leer un precio por segundo como precio por hora | Revisa las unidades del lado derecho: 1,5 $/s son $5.400 por hora (caso) |

---

## 8. Práctica

Diez ejercicios: 11.1 a 11.4 básicos, 11.5 a 11.8 intermedios, 11.9 y 11.10 de desafío. Las pautas
están en la sección 9. En todos, escribe primero las condiciones y después resuelve.

**11.1 · Amasandería (básico).** Una amasandería hornea lotes de hallulla ($x_1$) y de marraqueta
($x_2$). Cada lote de hallulla usa 2 horas de horno y 1 de amasado; cada lote de marraqueta, 1 hora de
horno y 3 de amasado. En la semana hay 40 horas de horno y 45 de amasado, y el casino que compra la
hallulla no recibe más de 18 lotes. Los márgenes son $5.000 y $4.000 por lote. El dueño propone
15 lotes de hallulla y 10 de marraqueta. (a) Calcula las holguras. (b) Escribe las condiciones de
holgura complementaria. (c) Encuentra los precios sombra. (d) ¿Es óptima la propuesta?

**11.2 · Mermeladas (básico).** Una fábrica de Chillán produce cajas de mermelada de frambuesa,
de mora y de membrillo. Una caja usa 3, 4 y 2 kg de azúcar, respectivamente, y 2, 2 y 3 horas de
paila. Hay 600 kg de azúcar y 480 horas de paila al mes. Los márgenes son $1.800, $2.100 y $1.500 por
caja. Comprueba con holgura complementaria si el plan de 168 cajas de frambuesa, ninguna de mora y 48
de membrillo es óptimo.

**11.3 · Taller de bicicletas (básico).** Un taller ofrece cuatro servicios: mantención básica,
cambio de transmisión, restauración y ajuste express. Usan 3, 2, 4 y 1 horas de mecánico, y 1, 1, 2 y 2
horas de banco de lavado. En el mes hay 240 horas de mecánico y 140 de banco. Los márgenes son
$60.000, $40.000, $70.000 y $35.000 por servicio. La dueña resolvió el dual con el método gráfico y
obtuvo $y^{*} = (17{.}000;\ 9{.}000)$ (pesos por hora de mecánico y de banco). Sin resolver el primal,
encuentra cuántos servicios de cada tipo conviene vender y el margen del mes.

**11.4 · Imprenta de etiquetas (básico).** Una imprenta fabrica tres etiquetas (A, B y C), en
millares. Por millar usan 1, 5 y 1 horas de prensa; 2, 2 y 3 m² de adhesivo; y 1, 1 y 5 horas de
troquel. En el mes hay 860 horas de prensa, 1.000 m² de adhesivo y 320 horas de troquel. Los márgenes
son $40.000, $100.000 y $80.000 por millar. El solver entregó este informe:

| | Valor | Holgura | Precio sombra |
|---|---|---|---|
| Etiqueta A (millares) | 185 | | |
| Etiqueta B (millares) | 135 | | |
| Etiqueta C (millares) | 0 | | |
| Prensa (h) | | 0 | $15.000 |
| Adhesivo (m²) | | 360 | $0 |
| Troquel (h) | | 0 | $25.000 |

(a) Comprueba que el informe cumple holgura complementaria y que $z = w$. (b) ¿Por qué el adhesivo
vale cero? (c) ¿Cuánto valen los recursos de un millar de etiqueta C y por qué no se fabrica?

**11.5 · Quesería (intermedio).** Una quesería del sur produce hormas de gauda, mantecoso y queso
fresco. Por horma usan 4, 6 y 3 decenas de litros de leche; 2, 1 y 1 horas de cámara de maduración; y
1, 2 y 1 horas de envasado. En la semana hay 960 decenas de litros, 300 horas de cámara y 260 de
envasado. Los márgenes son $2.600, $2.900 y $1.900 por horma. El jefe de planta propone hacer solo
queso fresco: 260 hormas. (a) Comprueba con holgura complementaria si es óptimo. (b) Si no lo es, ¿qué
producto indica la prueba que mejoraría el plan? (c) Resuelve el modelo en OPL
(`u11_mezcla.mod` con `u11_quesos.dat`) y certifica el óptimo con holgura complementaria.

**11.6 · Alimento para una lechería (intermedio, mínimo).** Una lechería mezcla tres insumos para su
concentrado: afrecho, pellet de raps y maíz partido, que cuestan $840, $320 y $440 por kg. Un kg de
cada uno aporta 7, 1 y 7 unidades de proteína; 7, 9 y 3 de energía; y 9, 4 y 9 de fibra. La ración
diaria del lote necesita al menos 190 de proteína, 390 de energía y 190 de fibra. La nutricionista
propone 0 kg de afrecho, 36 de pellet y 22 de maíz. Comprueba si es la mezcla de menor costo e
interpreta cada precio sombra.

**11.7 · Canastas con pedido exacto (intermedio, igualdad).** Una distribuidora arma canastas
premium, familiares y básicas para el pedido de fin de año de una empresa, que exige **exactamente**
230 canastas. Cada una usa 8, 3 y 3 minutos de armado, y 1, 6 y 2 productos de bodega. Hay 800 minutos
de armado y 2.250 productos en bodega. Los márgenes son $8.400, $2.550 y $2.350 por canasta. El plan
propuesto es 22 premium, 208 familiares y ninguna básica. (a) ¿Es óptimo? (b) Interpreta el signo del
dual de la restricción del pedido.

**11.8 · Chocolatería con topes de demanda (intermedio).** Una chocolatería de Puerto Varas vende
cajas clásicas, surtidas y de trufas. Cada caja usa 5, 4 y 3 minutos de templado, y 4, 4 y 3 minutos de
envasado. En la semana hay 660 minutos de templado y 820 de envasado, y se pueden vender a lo más 180,
390 y 80 cajas. Los márgenes son $4.100, $1.400 y $4.500 por caja. Con los topes escritos como
restricciones (cada uno con su dual), comprueba si el plan de 84 clásicas, 0 surtidas y 80 de trufas es
óptimo, y explica qué significa el dual del tope de trufas.

**11.9 · Cerámica degenerada (desafío).** Un taller de cerámica hace tazas ($x_1$) y platos ($x_2$),
con márgenes de $3.000 y $2.000. Usan 1 y 1 horas de horno (hay 40), 2 y 1 litros de esmalte (hay 60), y
la tienda que compra no recibe más de 20 tazas. Se propone hacer 20 tazas y 20 platos. (a) Muestra que
las tres restricciones están activas. (b) Escribe el sistema de holgura complementaria y encuentra
**todas** sus soluciones. (c) ¿Es óptima la propuesta? (d) Calcula el margen óptimo con 61 y con 59
litros de esmalte y compáralo con los precios que encontraste. (e) Corre `u11_mezcla.mod` con
`u11_ceramica.dat`: ¿qué precio del esmalte informa CPLEX y qué significa?

**11.10 · La tostaduría con filtro más caro (desafío).** En el ejemplo, la tostaduría sube el precio
del filtro y su margen pasa a $3.600 por kg. El encargado mantiene el plan A (250, 0, 100). La socia
propone ahora (0, 150, 200). Usa holgura complementaria para decidir quién tiene razón, y di qué pasa
con el plan que está justo a medio camino entre los dos.

---

## 9. Pautas

**11.1.** Holguras: horno $2(15) + 10 = 40$, holgura 0; amasado $15 + 3(10) = 45$, holgura 0; tope
$18 - 15 = 3$. Condiciones: $y_3 = 0$ y, como se hacen los dos panes, $2y_1 + y_2 = 5{.}000$ y
$y_1 + 3y_2 = 4{.}000$. Resultado: $y_1 = 2{.}200$ e $y_2 = 600$. Ambos son no negativos y no hay
productos sin fabricar que revisar, así que es óptima: $w = 40(2{.}200) + 45(600) = 115{.}000$, igual al
margen $5{.}000(15) + 4{.}000(10)$. *Lectura:* una hora más de horno vale $2.200 y una de amasado
\$600; el tope del casino no aprieta (sobran 3 lotes) y vale cero. Margen óptimo **$115.000**.

**11.2.** Azúcar $3(168) + 2(48) = 600$ y paila $2(168) + 3(48) = 480$: las dos activas. Frambuesa y
membrillo se fabrican: $3y_1 + 2y_2 = 1{.}800$ y $2y_1 + 3y_2 = 1{.}500$, que da $y_1 = 480$ por kg de
azúcar e $y_2 = 180$ por hora de paila. La mora no se fabrica y sus recursos valen
$4(480) + 2(180) = 2{.}280$, más que sus $2.100: cumple. Es óptimo, con $z = w = 374{.}400$.
*Lectura:* margen **$374.400**; los precios son $480 por kg de azúcar y $180 por hora de paila, y cada
caja de mora perdería $180 a precios sombra.

**11.3.** Holguras duales: mantención $3(17{.}000) + 9{.}000 - 60{.}000 = 0$; transmisión
$43{.}000 - 40{.}000 = 3{.}000$; restauración $86{.}000 - 70{.}000 = 16{.}000$; express
$17{.}000 + 18{.}000 - 35{.}000 = 0$. Transmisión y restauración valen cero en el plan. Las dos horas
tienen precio positivo, así que las dos restricciones están activas: $3x_1 + x_4 = 240$ y
$x_1 + 2x_4 = 140$, con $x_1 = 68$ y $x_4 = 36$. Margen $60{.}000(68) + 35{.}000(36) = 5{.}340{.}000$,
igual a $w = 240(17{.}000) + 140(9{.}000)$. *Lectura:* 68 mantenciones y 36 ajustes express, margen
**$5.340.000**; la transmisión usa horas que valen $43.000 para ganar 40.000, y la restauración horas que
valen $86.000 para ganar 70.000.

**11.4.** (a) El adhesivo tiene holgura 360 y su precio es 0; prensa y troquel están activas con precio
positivo; A y B se fabrican y pagan justo sus recursos: A $1(15{.}000) + 1(25{.}000) = 40{.}000$ y B
$5(15{.}000) + 1(25{.}000) = 100{.}000$. $z = 185(40{.}000) + 135(100{.}000) = 20{.}900{.}000$ y
$w = 860(15{.}000) + 320(25{.}000) = 20{.}900{.}000$. (b) Sobran 360 m²: un m² más no cambia nada.
(c) Un millar de C usa recursos que valen $1(15{.}000) + 3(0) + 5(25{.}000) = 140{.}000$ y deja 80.000:
pierde $60.000 a precios sombra. *Lectura:* el margen del mes es **$20.900.000**; C solo entraría si su
margen superara $140.000 por millar (o si bajara su consumo de troquel, que es el recurso caro).

**11.5.** (a) Leche $3(260) = 780$, holgura 180; cámara 260, holgura 40; envasado 260, activa. Entonces
$y_1 = y_2 = 0$ y, como el fresco se fabrica, $y_3 = 1{.}900$. Factibilidad dual: el gauda usa recursos
que valen $1(1{.}900) = 1{.}900$, menos que su margen de 2.600: **se viola**. No es óptimo (margen
$494.000). (b) El gauda: deja 700 más de lo que valen sus recursos, así que meterlo al plan sube el
margen. (c) OPL entrega 40 hormas de gauda, 0 de mantecoso y 220 de fresco, margen **$522.000**. Para
certificarlo: leche $4(40) + 3(220) = 820$, holgura 140, así que $y_1 = 0$; con gauda y fresco,
$2y_2 + y_3 = 2{.}600$ e $y_2 + y_3 = 1{.}900$: $y_2 = 700$ e $y_3 = 1{.}200$. El mantecoso no se fabrica y
sus recursos valen $1(700) + 2(1{.}200) = 3{.}100 \ge 2{.}900$. Se cumple todo y
$w = 300(700) + 260(1{.}200) = 522{.}000$. *Lectura:* la hora de cámara vale $700, la de envasado
$1.200, la leche sobra; al mantecoso le faltan $200 por horma para entrar.

**11.6.** Proteína $36 + 7(22) = 190$, activa; energía $9(36) + 3(22) = 390$, activa; fibra
$4(36) + 9(22) = 342$, excedente 152, así que $y_3 = 0$. Pellet y maíz se usan:
$y_1 + 9y_2 = 320$ y $7y_1 + 3y_2 = 440$, con $y_1 = 50$ e $y_2 = 30$. En un mínimo con $\ge$ se exige
$y \ge 0$ (se cumple) y, para el afrecho que no se usa, que sus aportes valgan a lo más su costo:
$7(50) + 7(30) = 560 \le 840$. Es la mezcla de menor costo: $36(320) + 22(440) = 21{.}200$ y
$w = 190(50) + 390(30) = 21{.}200$. *Lectura:* costo mínimo **$21.200** por ración; exigir una unidad
más de proteína encarece la ración en \$50 y una de energía en \$30; la fibra sale sobrada y no cuesta
nada; el afrecho aporta lo que vale $560 y cuesta 840, por eso queda fuera.

**11.7.** Armado $8(22) + 3(208) = 800$, activa; bodega $22 + 6(208) = 1{.}270$, holgura 980, así que
$y_2 = 0$; el pedido suma 230, como exige. Premium y familiar se arman: $8y_1 + y_3 = 8{.}400$ y
$3y_1 + y_3 = 2{.}550$, con $y_1 = 1{.}170$ e $y_3 = -960$. El dual de una igualdad es libre, así que el
signo negativo está permitido. La básica no se arma y sus recursos valen
$3(1{.}170) + 2(0) - 960 = 2{.}550 \ge 2{.}350$: cumple. Es óptimo, margen
$8{.}400(22) + 2{.}550(208) = 715{.}200$ y $w = 800(1{.}170) + 230(-960) = 715{.}200$. *Lectura:* el
minuto de armado vale $1.170. El dual del pedido es **−$960**: cada canasta extra que exigiera el
cliente bajaría el margen en $960, porque obliga a cambiar premium (8 minutos) por familiares
(3 minutos). A la básica le faltan $200 por canasta. Margen **$715.200**.

**11.8.** Templado $5(84) + 3(80) = 660$, activo; envasado $4(84) + 3(80) = 576$, holgura 244, así que
$y_2 = 0$; los topes de clásicas y surtidas tienen holgura (96 y 390), así que sus duales valen cero; el
de trufas está activo. Clásicas se fabrican bajo su tope: $5y_1 = 4{.}100$, $y_1 = 820$. Trufas se
fabrican en su tope: $3y_1 + u_3 = 4{.}500$, $u_3 = 2{.}040$. La surtida no se fabrica y sus recursos
valen $4(820) = 3{.}280 \ge 1{.}400$. Es óptimo: $z = 4{.}100(84) + 4{.}500(80) = 704{.}400$ y
$w = 660(820) + 80(2{.}040) = 704{.}400$. *Lectura:* margen **$704.400**; el minuto de templado vale
$820; vender una caja más de trufas vale $2.040 (deja 4.500 y sus 3 minutos valen 2.460); a la
surtida le faltan $1.880 por caja.

**11.9.** (a) Horno $20 + 20 = 40$, esmalte $2(20) + 20 = 60$, tope $20$: las tres activas en un vértice
del plano, donde bastan dos. Es una solución degenerada. (b) Ninguna holgura es positiva, así que no
hay duales forzados a cero; las dos variables son positivas:
$y_1 + 2y_2 + y_3 = 3{.}000$ e $y_1 + y_2 = 2{.}000$. Con $y_2 = t$: $y_1 = 2{.}000 - t$ e
$y_3 = 1{.}000 - t$. Para que todos sean no negativos, $0 \le t \le 1{.}000$. (c) Cualquier $t$ de ese
intervalo es factible para el dual, así que la propuesta es óptima, con margen **$100.000** y
$w = 40(2{.}000 - t) + 60t + 20(1{.}000 - t) = 100{.}000$ para todo $t$. (d) Con 61 litros el margen
sigue en $100.000 (el vértice no se mueve: lo fijan el horno y el tope), una subida que vale 0. Con 59
litros baja a $99.000 (19 tazas y 21 platos), una bajada que cuesta 1.000. Son los dos extremos de la
familia: $t = 0$ y $t = 1{.}000$. (e) CPLEX informa horno 2.000, esmalte 0 y tope 1.000, el extremo
$t = 0$. *Lectura:* en un vértice degenerado el «precio sombra» depende de la dirección. El solver
entrega uno de los posibles; antes de usarlo para comprar o vender esmalte hay que preguntar si se
quiere subir o bajar.

**11.10.** Con margen 3.600, los precios $y = (300;\ 0;\ 2{.}400)$ siguen cumpliendo todo para el plan A,
pero ahora el filtro paga justo sus recursos: $4(300) + 2{.}400 = 3{.}600$, costo reducido 0. Plan de la
socia: tostadora $4(150) + 9(200) = 2{.}400$ y bolsas 350, activas; envasadora
$2(150) + 2(200) = 700$, holgura 300, así que $y_2 = 0$; filtro y descafeinado se tuestan:
$4y_1 + y_3 = 3{.}600$ y $9y_1 + y_3 = 5{.}100$, con los mismos $y_1 = 300$ e $y_3 = 2{.}400$; el espresso
no se tuesta y sus recursos valen $6(300) + 2{.}400 = 4{.}200 \ge 4{.}200$. **Los dos tienen razón**:
ambos planes dan $1.560.000. El plan intermedio (125, 75, 150) también cumple con los mismos precios y
es óptimo: todo el segmento entre los dos lo es. *Lectura:* un producto que no se fabrica con costo
reducido cero avisa óptimos alternativos. El modelo no elige entre ellos; se decide con un criterio de
afuera (menos mezclas que envasar, riesgo de la demanda de descafeinado).

---

## 10. Caso integrador · Estampa Sur comprueba su mezcla

> Este caso sigue a Estampa Sur por todo el ramo. La unidad 4 encontró la mezcla semanal de cinco
> prendas y la unidad 10 escribió su dual. Acá se certifica que esa mezcla es óptima con holgura
> complementaria, sin volver a resolver nada. Si no has hecho esas unidades, parte de esta tabla.

| Prenda | Margen ($) | Estampado (s) | Planchado (s) | Tinta (g) | Tope | Plan de la unidad 4 |
|---|---|---|---|---|---|---|
| Poleras básicas | 1.380 | 30 | 20 | 12 | 1.450 | 833,75 |
| Polerones | 3.940 | 90 | 50 | 25 | 520 | 520 |
| Poleras estampado doble | 2.270 | 110 | 30 | 22 | 380 | 0 |
| Bolsas | 960 | 20 | 40 | 8 | 860 | 294,375 |
| Gorros | 1.170 | 30 | 15 | 6 | 690 | 690 |
| **Disponible** | | 144.000 | 64.800 | 29.500 | | |

El margen del plan es $4.289.275. El dual tiene un precio por recurso ($y_E$, $y_P$, $y_T$) y uno por
cada tope de demanda ($u_i$).

**Paso 1 · Holguras.** Estampado usa 98.400 s: holgura **45.600 s** (12,67 h). Planchado y tinta se
usan completos. Los topes: poleras básicas 616,25 y bolsas 565,625 unidades de holgura, estampado doble
380; polerones y gorros llegan a su tope.

**Paso 2 · Lo que obliga cada holgura.** $y_E = 0$, y los topes con holgura tienen $u = 0$ (poleras
básicas, estampado doble y bolsas).

**Paso 3 · Las prendas que se fabrican bajo su tope.** Poleras básicas y bolsas pagan justo sus
recursos:

$$20\,y_P + 12\,y_T = 1{.}380 \qquad 40\,y_P + 8\,y_T = 960$$

Multiplicando la primera por 2 y restando: $16\,y_T = 1{.}800$, así que $y_T = 112{,}5$ \$/g y
$y_P = (1{.}380 - 1{.}350)/20 = 1{,}5$ \$/s.

**Paso 4 · Las prendas que llegan a su tope.** Lo que dejan por sobre el valor de sus recursos es el
dual del tope:

$$u_{\text{polerones}} = 3{.}940 - \big(50(1{,}5) + 25(112{,}5)\big) = 3{.}940 - 2{.}887{,}5 = 1{.}052{,}5$$

$$u_{\text{gorros}} = 1{.}170 - \big(15(1{,}5) + 6(112{,}5)\big) = 1{.}170 - 697{,}5 = 472{,}5$$

**Paso 5 · Factibilidad dual.** Todos los precios son no negativos. La polera de estampado doble no se
fabrica; sus recursos valen $30(1{,}5) + 22(112{,}5) = 2{.}520$, más que su margen de 2.270: cumple, con
costo reducido **−250**.

**Paso 6 · Cierre.**

$$\begin{aligned} w &= 64{.}800(1{,}5) + 29{.}500(112{,}5) + 520(1{.}052{,}5) + 690(472{,}5) \\ &= 97{.}200 + 3{.}318{.}750 + 547{.}300 + 326{.}025 = 4{.}289{.}275 \end{aligned}$$

Igual al margen del primal: la mezcla de la unidad 4 es óptima, certificada a mano.

**El dual en OPL.** `modelos/u11_dual_estampa.mod` resuelve el dual con los mismos datos. Las duales
de **sus** restricciones devuelven la mezcla del primal: el dual del dual es el primal.

```opl
dvar float+ y[Recursos];
dvar float+ u[Prendas];
dexpr float W = sum(r in Recursos) cap[r] * y[r] + sum(i in Prendas) demanda[i] * u[i];
minimize W;
subject to {
  forall(i in Prendas)
    Cubre:
      sum(r in Recursos) uso[r][i] * y[r] + u[i] >= margen[i];
}
execute {
  writeln("w = ", W);
  for (var r in Recursos) writeln("y[", r, "] = ", y[r]);
  for (var i in Prendas) {
    writeln("u[", i, "] = ", u[i]);
    writeln("x_desde_dual[", i, "] = ", Cubre[i].dual);
  }
}
```

```text
w = 4289275
y[estampado] = 0       y[planchado] = 1.5      y[tinta] = 112.5
u[poleras] = 0         x_desde_dual[poleras] = 833.75
u[polerones] = 1052.5  x_desde_dual[polerones] = 520
u[doble] = 0           x_desde_dual[doble] = 0
u[bolsas] = 0          x_desde_dual[bolsas] = 294.375
u[gorros] = 472.5      x_desde_dual[gorros] = 690
```

**Lectura.**

- **Un recurso que sobra vale cero.** Al estampado le sobran 45.600 segundos: una hora más de
  estampado no agrega ni un peso.
- **Los que limitan son el planchado y la tinta.** Un segundo de planchado vale $1,5 y un gramo de tinta
  $112,5. Las poleras básicas y las bolsas pagan exactamente esos recursos.
- **Lo que más vale es vender más polerones:** cada polerón de demanda adicional vale $1.052,5 de
  margen, y cada gorro $472,5.
- **Un producto que no se fabrica no paga sus recursos:** la polera de estampado doble consume
  planchado y tinta por $2.520 y deja 2.270.

**Lo que pasa a la unidad 12.** El precio del planchado es 1,5 \$/s, o $5.400 por hora. Estampa Sur
paga la hora extra a $6.750. ¿Conviene? ¿Y hasta cuántas horas sigue valiendo ese precio? Eso es
análisis de sensibilidad.

---

## 11. Para seguir

**En los libros del ramo.**

- Winston, *Investigación de operaciones: aplicaciones y algoritmos* (4.ª ed., 2005), capítulo de
  análisis de sensibilidad y dualidad: holgura complementaria y su uso para hallar el óptimo dual.
- Hillier y Lieberman, *Introducción a la investigación de operaciones* (7.ª ed., 2001), capítulo de
  teoría de dualidad: relaciones entre primal y dual y propiedad de holgura complementaria.

**Abierto y gratis.**

- Bradley, Hax y Magnanti, *Applied Mathematical Programming* (Addison-Wesley, 1977), en inglés,
  publicado por el MIT. El capítulo 4 («Duality in Linear Programming») trae la holgura complementaria
  (sección 4.5) con su interpretación económica:
  https://web.mit.edu/15.053/www/AMP-Chapter-04.pdf

**Con el tutor.** Pega `tutor/contexto.md` al inicio de la conversación con cualquier IA y pídele, por
ejemplo: «Dame un plan de producción de tres productos con un error escondido y déjame probar con
holgura complementaria que no es óptimo».
