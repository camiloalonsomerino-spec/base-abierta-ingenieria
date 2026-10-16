---
ramo: Contabilidad y Costos
unidad: 12
titulo: Costo-volumen-utilidad y punto de equilibrio
version: 0.1 (16-10-2026)
requiere: [09-clasificacion-de-costos, 10-absorcion-y-variable, 11-asignacion-de-costos-indirectos]
alimenta: []
verificacion: verificacion/u12_cvu.py
---

# Unidad 12 · Costo-volumen-utilidad y punto de equilibrio

**Qué vas a poder hacer.** Calcular el margen de contribución y con él el punto de equilibrio en
unidades y en pesos, la venta necesaria para una utilidad objetivo, el margen de seguridad y el grado
de apalancamiento operativo; hacer lo mismo con varios productos usando la mezcla y el margen
ponderado; medir qué tan sensible es la utilidad al precio, al costo variable y al fijo, y elegir qué
producir cuando un recurso no alcanza, ordenando por margen por unidad del recurso escaso.

**Lo que necesitas antes.** Separar costos fijos y variables (unidad 9) y leer un estado de
resultados por costeo variable (unidad 10). De la unidad 11, una idea: los fijos asignados a cada
producto no cambian con lo que se vende, así que acá no se reparten, se cubren.

**Tiempo.** Unas 4,5 horas: 1,5 de lectura con el ejemplo y 3 de práctica.

**Planilla.** `planillas/u12_punto_de_equilibrio.xlsx` trae el punto de equilibrio multiproducto del
ejemplo y del caso, con fórmulas: cambia un precio, un costo o la mezcla y mira cómo se mueve el
equilibrio.

---

## 1. El margen de contribución

Cada unidad vendida trae su precio $p$ y se lleva su costo variable unitario $cv$ (materiales,
comisiones, lo que solo aparece si se vende). Lo que queda es el **margen de contribución unitario**:

$$mc = p - cv \qquad \text{razón de margen} = \frac{mc}{p}$$

Se llama de contribución porque **contribuye** primero a pagar los costos fijos ($CF$) y, cuando ya
los pagó, a la utilidad. Con $q$ unidades vendidas:

$$\text{utilidad operacional} = q \cdot mc - CF$$

Es el estado de resultados por costeo variable (unidad 10) escrito en una línea. La razón de margen
dice cuántos pesos de cada peso vendido quedan para los fijos: con una razón de 40 %, cada $1.000 de
venta aporta \$400.

---

## 2. El punto de equilibrio

Es la venta que deja utilidad cero: el margen total alcanza justo para los fijos.

$$q_0 = \frac{CF}{p - cv} = \frac{CF}{mc} \qquad\qquad Y_0 = p \cdot q_0 = \frac{CF}{\text{razón de margen}}$$

**La intuición.** Cada unidad paga $mc$ de los fijos. ¿Cuántas unidades hacen falta para pagarlos
todos? $CF / mc$. La fórmula en pesos sirve cuando no hay un precio único (una tienda con mil
productos): basta con la razón de margen promedio, que sale del estado de resultados.

El equilibrio en unidades casi nunca da entero. Como no se vende media unidad, para no perder hay que
vender el entero siguiente.

---

## 3. La utilidad objetivo

Si la meta es una utilidad $U$ antes de impuestos, el margen tiene que pagar los fijos **y** la meta:

$$q_U = \frac{CF + U}{mc}$$

Dos variantes:

- **Utilidad como porcentaje $i$ de las ventas.** La meta crece con lo que se vende: de cada unidad,
  $p \cdot i$ se reserva para la utilidad y queda menos margen para los fijos.

$$q_i = \frac{CF}{p\,(1 - i) - cv}$$

- **Utilidad después de impuestos.** Si la meta es una utilidad neta $U_n$ y la tasa de impuesto es
  $t$, antes de impuestos hay que ganar $U_n / (1-t)$:

$$q_t = \frac{CF + \dfrac{U_n}{1-t}}{mc}$$

En los ejercicios la tasa $t$ es un dato del enunciado. No uses una de memoria: la tasa vigente
depende del régimen tributario de la empresa y cambia con la ley.

---

## 4. Margen de seguridad y apalancamiento operativo

El **margen de seguridad** dice cuánto pueden caer las ventas antes de perder:

$$MS = q - q_0 \qquad MS\,\% = \frac{q - q_0}{q}$$

El **grado de apalancamiento operativo** (GAO) dice cuánto se amplifica en la utilidad un cambio en
las ventas:

$$GAO = \frac{\text{margen de contribución total}}{\text{utilidad operacional}} \qquad
\Delta\%\,\text{utilidad} = GAO \times \Delta\%\,\text{ventas}$$

**Por qué amplifica.** Si las ventas suben 10 %, el margen total sube 10 %, pero los fijos no se
mueven: toda la subida va a la utilidad, que es más chica que el margen. Lo mismo hacia abajo. Una
empresa con muchos fijos (una planta automatizada) tiene un GAO alto: gana mucho en un buen año y
sufre mucho en uno malo.

Los dos indicadores son la misma información vista de dos lados: con costos lineales,
$GAO = 1 / MS\,\%$. Un margen de seguridad de 25 % es un GAO de 4.

---

## 5. Varios productos · la mezcla

Con varios productos no hay un solo $mc$. La salida es pensar en una **unidad promedio** que respeta
la **mezcla** de ventas $w_j$ (la participación de cada producto en las unidades vendidas):

$$\overline{mc} = \sum_j w_j \, mc_j \qquad q_0 = \frac{CF}{\overline{mc}} \qquad q_{0,j} = w_j \, q_0$$

$\overline{mc}$ es el **margen ponderado**. En pesos, el equilibrio es $q_0$ por el precio ponderado
$\bar p = \sum_j w_j \, p_j$, o los fijos divididos por la razón de margen ponderada
$\overline{mc} / \bar p$.

**El supuesto que hay que vigilar.** El equilibrio vale **para esa mezcla**. Si las ventas se corren
hacia los productos de margen bajo, el margen ponderado baja y el equilibrio sube, aunque se vendan
las mismas unidades (ejercicio 12.6). Por eso el equilibrio multiproducto se recalcula cuando cambia la
mezcla y se comprueba siempre: con las cantidades de equilibrio de cada producto, la utilidad tiene que
dar cero.

---

## 6. Sensibilidad

Un análisis de sensibilidad mueve un dato a la vez y mira qué pasa con el equilibrio y la utilidad:

| Si sube | El margen unitario | El equilibrio | La utilidad |
|---|---|---|---|
| El precio | sube | baja | sube |
| El costo variable unitario | baja | sube | baja |
| El costo fijo | no cambia | sube | baja |
| El volumen | no cambia | no cambia | sube |

Para comparar palancas, sirve preguntar cuánto vale un 1 % de cada una. Un 1 % de precio mueve la
utilidad en $0{,}01 \cdot p \cdot q$ (toda la venta); un 1 % de volumen solo en $0{,}01 \cdot mc \cdot q$
(el margen). Por eso un descuento chico necesita un aumento grande de ventas para pagarse (ejercicios
12.7 y 12.10).

---

## 7. Cuando un recurso no alcanza

Si la demanda supera la capacidad de un recurso (horas de horno, segundos de una máquina, litros de
una heladera), la pregunta ya no es cuánto vender sino **qué** vender. El criterio cambia:

$$\text{margen por unidad de recurso} = \frac{mc_j}{\text{uso del recurso por unidad}_j}$$

Se llena el recurso en ese orden, cada producto hasta su demanda. El producto con mayor margen por
unidad puede ser el último de la fila si usa mucho del recurso escaso: lo que se maximiza es el
margen total que cabe en la capacidad, no el margen de cada unidad.

**Conexión con Optimización.** Con un solo recurso escaso y topes de demanda, ese orden da el óptimo.
Con dos o más recursos a la vez (horas de estampado y de planchado, tinta) el orden ya no basta y se
arma un modelo lineal (Optimización, unidad 4). Lo que vale una hora más del recurso escaso es su
**precio sombra** (Optimización, unidades 10 y 12): el margen por hora del producto que entraría con
esa hora.

---

## 8. Cuándo no aplica

El modelo costo-volumen-utilidad es una aproximación lineal. Vale dentro del **rango relevante**:

- Precio y costo variable constantes por unidad. Con descuentos por volumen o compras más baratas al
  por mayor, ya no.
- Fijos constantes. Si para vender más hay que arrendar otro local o contratar, los fijos saltan y el
  equilibrio se recalcula por tramos.
- Mezcla constante (con varios productos).
- Lo producido es lo vendido. Si no, el resultado por absorción difiere del variable (unidad 10); el
  equilibrio se calcula con el variable.

Fuera de esos supuestos, el equilibrio sigue siendo una buena primera cifra, pero no una promesa.

---

## 9. Ejemplo resuelto · la heladería de Martín

Martín tiene una heladería en una costanera. Vende tres formatos y en enero espera esta venta:

| Formato | Precio neto | Costo variable | Ventas de enero | Litros de helado por unidad |
|---|---|---|---|---|
| Cono simple | 2.250 | 880 | 3.150 | 0,12 |
| Vaso doble | 3.450 | 1.430 | 1.890 | 0,22 |
| Pote de 1 litro | 8.900 | 3.640 | 1.260 | 1 |

Sus costos fijos del mes (arriendo, dos vendedoras, luz de las vitrinas y depreciación de la máquina)
suman **$4.986.000**.

**Paso 1 · Margen y mezcla.** Se venden 6.300 unidades: la mezcla es 50 % conos, 30 % vasos y 20 %
potes.

| | Cono | Vaso | Pote |
|---|---|---|---|
| Margen unitario | 1.370 | 2.020 | 5.260 |
| Mezcla | 50 % | 30 % | 20 % |
| Margen × mezcla | 685 | 606 | 1.052 |

Margen ponderado: **$2.343** por unidad promedio. Precio ponderado: **$3.940**. Razón de margen:
2.343 / 3.940 = **59,47 %**.

**Paso 2 · Equilibrio.**

$$q_0 = \frac{4{.}986{.}000}{2{.}343} = 2{.}128{,}04 \text{ unidades} \qquad Y_0 = 2{.}128{,}04 \times 3{.}940 = 8{.}384{.}481$$

| En equilibrio | Cono | Vaso | Pote | Total |
|---|---|---|---|---|
| Unidades | 1.064,0 | 638,4 | 425,6 | 2.128,0 |
| Ingreso | 2.394.046 | 2.202.522 | 3.787.913 | 8.384.481 |

Comprobación: el margen de esas cantidades (1.064,0 × 1.370 + 638,4 × 2.020 + 425,6 × 5.260) da los
$4.986.000 de fijos: utilidad cero.

**Paso 3 · Enero completo.** Ventas $24.822.000, margen total $14.760.900, utilidad operacional
**$9.774.900**. Margen de seguridad: (6.300 − 2.128) / 6.300 = **66,2 %**. GAO: 14.760.900 / 9.774.900 =
**1,51**; si las ventas cayeran 10 %, la utilidad caería 15,1 %.

**Paso 4 · Utilidad objetivo.** Para ganar $6.150.000 en un mes flojo:
(4.986.000 + 6.150.000) / 2.343 = **4.752,9 unidades**, unos $18.726.351 de venta.

**Paso 5 · Sensibilidad.** Dos ideas de Martín, una a la vez:

| Escenario | Margen ponderado | Equilibrio | Utilidad de enero |
|---|---|---|---|
| Base | 2.343,0 | 2.128,0 | 9.774.900 |
| Cono a $2.475 (+10 %), mismas ventas | 2.455,5 | 2.030,5 | 10.483.650 |
| Una tercera vendedora ($640.000 al mes) | 2.343,0 | 2.401,2 | 9.134.900 |

Subir el cono solo sirve si no espanta a los clientes; la vendedora sube el equilibrio en 273 unidades
y tiene que traer venta (o ahorrar filas) por más de lo que cuesta.

**Paso 6 · Febrero: la máquina no da abasto.** En febrero la demanda sube 20 %: 3.780 conos, 2.268
vasos y 1.512 potes, que piden 2.464,56 litros. La máquina hace **2.050 litros** al mes. Algo hay que
dejar de vender. Margen por litro:

| | Cono | Vaso | Pote |
|---|---|---|---|
| Margen por unidad | 1.370 | 2.020 | 5.260 |
| Margen por litro | 11.417 | 9.182 | 5.260 |

| Plan | Conos | Vasos | Potes | Litros usados | Margen total |
|---|---|---|---|---|---|
| Por margen por litro | 3.780 | 2.268 | 1.097 | 453,60 + 498,96 + 1.097,00 | **15.530.180** |
| Por margen por unidad | 325 | 2.268 | 1.512 | 39,00 + 498,96 + 1.512,00 | 12.979.730 |

**Cómo se lee.** Martín necesita vender **2.129 unidades** en la mezcla de enero para no perder; espera
6.300, así que tiene dos tercios de holgura. En febrero el pote parece el mejor producto (deja $5.260 por
unidad), pero gasta un litro entero; el cono deja $11.417 por litro. Llenar la máquina con conos y vasos
primero y recortar potes deja **$2.550.450** más de margen que hacer lo contrario. Con los fijos de
siempre, febrero termina con $10.544.180 de utilidad. Si la demanda de potes es fiel, una segunda
máquina se pagaría con ese margen perdido: es una pregunta de capacidad, no de precio.

---

## 10. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Dividir los fijos por el precio en vez de por el margen | Cada unidad paga los fijos con su margen, no con su precio: $q_0 = CF / (p - cv)$ |
| Usar el costo unitario total (con fijos repartidos) como costo variable | El fijo por unidad cambia con el volumen; en CVU los fijos van enteros en $CF$ |
| Promediar los márgenes sin ponderar por la mezcla | El margen ponderado usa la participación de cada producto en las unidades |
| Creer que el equilibrio multiproducto vale para cualquier mezcla | Recalcula si cambia la mezcla; comprueba que la utilidad dé cero con las cantidades de equilibrio |
| Redondear el equilibrio hacia abajo | Media unidad no se vende: el entero siguiente |
| Olvidar los impuestos en una meta de utilidad neta | Antes de impuestos: $U_n / (1-t)$, con la tasa que da el enunciado |
| Elegir la mezcla por margen unitario cuando un recurso no alcanza | Ordena por margen por unidad del recurso escaso |
| Mezclar el interés con los fijos operacionales sin decirlo | El equilibrio operacional usa los fijos de operación; si se quiere cubrir también el interés, se suma aparte y se dice |
| Leer el GAO como bueno o malo | Es riesgo: amplifica las subidas y las caídas |

---

## 11. Práctica

Diez ejercicios: 12.1 a 12.4 básicos, 12.5 a 12.8 intermedios, 12.9 y 12.10 de desafío. Las pautas
están en la sección 12.

**12.1 · Lavado de autos (básico).** Un lavado cobra $12.400 por auto; agua, productos y la comisión
del lavador suman $3.350 por auto. Los fijos son $3.529.500 al mes. (a) Margen, razón de margen y
equilibrio en autos y en pesos. (b) Con 515 autos al mes, ¿cuál es la utilidad, el margen de seguridad
y el GAO?

**12.2 · Academia de reforzamiento (básico).** Cobra $64.500 por alumno al mes; material y plataforma
cuestan $13.800 por alumno. Los fijos (arriendo, profesores de planta) son $4.563.000. (a) Equilibrio.
(b) ¿Cuántos alumnos necesita para ganar $2.028.000 antes de impuestos? (c) ¿Y para que la utilidad
sea el 15 % de las ventas? (d) ¿Y para una utilidad neta de $1.512.000 si la tasa de impuesto fuera 25 %
(dato del ejercicio, no la tasa legal)?

**12.3 · Carro de comida (básico).** Precio promedio $6.450, costo variable $2.580, fijos $2.709.000
al mes y ventas de 1.120 platos. (a) Equilibrio y margen de seguridad en platos y en porcentaje. (b)
GAO. (c) Si las ventas caen 10 %, ¿cuánto cae la utilidad? Compruébalo recalculando.

**12.4 · Tienda de regalos (básico).** El estado de resultados por contribución del mes muestra ventas
por $18.450.000, costos variables por $11.070.000 y costos fijos por $5.535.000. La tienda tiene cientos
de productos. (a) Razón de margen y equilibrio en pesos. (b) Margen de seguridad y GAO. ¿Qué relación
hay entre los dos?

**12.5 · Panadería de barrio (intermedio).** Datos del mes:

| Producto | Precio | Costo variable | Ventas |
|---|---|---|---|
| Pan (kg) | 1.940 | 1.060 | 6.150 |
| Empanadas | 2.350 | 1.170 | 2.870 |
| Tortas | 18.700 | 8.950 | 205 |

Fijos: $7.348.000. Calcula la mezcla, el margen ponderado, el equilibrio total y por producto, el
equilibrio en pesos y el margen de seguridad. Comprueba que en equilibrio la utilidad es cero.

**12.6 · La mezcla se corre (intermedio).** Al mes siguiente la panadería vende las mismas 9.225
unidades, pero 100 tortas menos y 100 kilos de pan más (6.250 kg, 2.870 empanadas, 105 tortas). Recalcula
el margen ponderado, el equilibrio y la utilidad. ¿Por qué cambia si vendió lo mismo?

**12.7 · ¿Qué palanca duele más? (intermedio).** Una fábrica de mermeladas vende 4.560 frascos al mes a
$3.240, con costo variable de $1.710 y fijos de $4.192.000. Calcula el equilibrio y la utilidad en cuatro
escenarios por separado: precio −8 %, costo variable +10 %, costo fijo +15 % y volumen −10 %. Ordénalos
por daño. Después calcula cuánto mueve la utilidad un 1 % de cada palanca.

**12.8 · Automatizar la envasadora (intermedio).** Una tostaduría vende café a $5.450 la bolsa. Hoy
su costo variable es $2.930 y sus fijos $2.115.000. Una envasadora automática bajaría el variable a
$2.310 y subiría los fijos a $3.627.000. Espera vender 2.240 bolsas al mes. (a) Equilibrio y utilidad
con y sin la máquina. (b) ¿Desde qué volumen conviene la máquina? (c) Compara el GAO y el margen de
seguridad. ¿La compra ahora?

**12.9 · El horno de la pastelería (desafío).** Una pastelería tiene 164 horas de horno al mes y fijos
de $1.915.000.

| Producto | Margen unitario | Horas de horno | Demanda máxima |
|---|---|---|---|
| Kuchen | 7.250 | 0,5 | 148 |
| Pie de limón | 5.420 | 0,25 | 204 |
| Tarta de frambuesa | 9.830 | 1 | 62 |

(a) ¿Alcanza el horno para toda la demanda? (b) ¿Qué conviene producir? Compara con el plan que sigue el
margen unitario. (c) ¿Cuánto vale una hora más de horno?

**12.10 · El gimnasio (desafío).** Un gimnasio cobra $31.900 al mes, cada socio cuesta $4.150 al mes
(toallas, agua, sistema) y los fijos son $8.436.000. Tiene 418 socios y le caben 500. (a) Utilidad,
equilibrio y margen de seguridad. (b) Una opción es bajar el precio a $26.900: ¿cuántos socios necesita
para ganar lo mismo que hoy? ¿Es posible? (c) Otra es mantener el precio y gastar $1.480.000 más al mes
en publicidad: ¿cuántos socios necesita? (d) ¿Cuál es el precio mínimo que, con el gimnasio lleno,
mantiene la utilidad de hoy?

---

## 12. Pautas

**12.1.** (a) Margen **$9.050**, razón **73,0 %**. Equilibrio 3.529.500 / 9.050 = **390 autos**, o
**$4.836.000**. (b) Margen total $4.660.750, utilidad **$1.131.250**. Margen de seguridad: 125 autos,
**24,3 %**. GAO **4,12**: un 10 % menos de autos le quita el 41 % de la utilidad. Es un negocio de fijos
altos: cada auto extra sobre 390 es casi todo ganancia, y cada auto menos también duele.

**12.2.** (a) Margen **$50.700**: equilibrio **90 alumnos**. (b) (4.563.000 + 2.028.000) / 50.700 = **130
alumnos** ($8.385.000 de venta). (c)

$$q = \frac{4{.}563{.}000}{64{.}500 \times 0{,}85 - 13{.}800} = \frac{4{.}563{.}000}{41{.}025} = 111{,}2$$

Son **112 alumnos** (con 112 la utilidad es el 15,4 % de las ventas). (d)
Antes de impuestos tiene que ganar 1.512.000 / 0,75 = **$2.016.000**: (4.563.000 + 2.016.000) / 50.700 =
129,8, es decir **130 alumnos**. La meta neta casi coincide con la de (b) porque los $2.028.000 de (b)
dejan, con esa tasa, poco más de $1.512.000 netos.

**12.3.** (a) Margen **$3.870** (razón 60 %). Equilibrio 2.709.000 / 3.870 = **700 platos**. Margen de
seguridad: **420 platos**, **37,5 %**. (b) Margen total **$4.334.400**, utilidad **$1.625.400**: GAO
**2,67**. (c) Caída esperada 2,67 × 10 % = **26,7 %**. Recalculando con 1.008 platos: 1.008 × 3.870 −
2.709.000 = **$1.191.960**, que es justo 26,7 % menos ✓.

**12.4.** (a) Margen total **$7.380.000**; razón **40 %**. Equilibrio en pesos: 5.535.000 / 0,40 =
**$13.837.500**. (b) Utilidad **$1.845.000**. Margen de seguridad (18.450.000 − 13.837.500) /
18.450.000 = **25 %**; GAO 7.380.000 / 1.845.000 = **4,0**. Uno es el inverso del otro: 1 / 0,25 = 4.
Con cientos de productos no hace falta un precio único; basta la razón de margen, que se supone estable.

**12.5.** Total 9.225 unidades.

| | Pan | Empanadas | Tortas |
|---|---|---|---|
| Mezcla | 66,7 % | 31,1 % | 2,2 % |
| Margen unitario | 880 | 1.180 | 9.750 |
| Equilibrio | 4.185,3 kg | 1.953,1 | 139,5 |

Margen ponderado **$1.170,44**, precio ponderado $2.440,00, razón 47,97 %. Equilibrio **6.278,0
unidades** de la mezcla, **$15.318.215** de venta. Utilidad del mes $3.449.350; margen de seguridad
**31,9 %**. Comprobación: el margen de las cantidades de equilibrio paga exactamente los $7.348.000. Las
tortas son solo el 2,2 % de las unidades, pero aportan casi un quinto del margen.

**12.6.**

| | Mes 12.5 | Mes nuevo |
|---|---|---|
| Mezcla (pan, empanadas, tortas) | 66,7 % · 31,1 % · 2,2 % | 67,8 % · 31,1 % · 1,1 % |
| Margen ponderado | 1.170,44 | 1.074,29 |
| Precio ponderado | 2.440,00 | 2.258,32 |
| Razón de margen | 47,97 % | 47,57 % |
| Equilibrio | 6.278,0 | 6.839,8 |
| Equilibrio en pesos | 15.318.215 | 15.446.567 |
| Utilidad | 3.449.350 | 2.562.350 |
| Margen de seguridad | 31,9 % | 25,9 % |

Vendió las mismas unidades, pero cambió 100 tortas que dejaban \$9.750 cada una por 100 kilos de pan que
dejan \$880. El margen ponderado baja, el equilibrio sube en unas 560 unidades y la utilidad cae
$887.000. Equilibrio por producto del mes nuevo: 4.634,0 kg de pan, 2.128,0 empanadas y 77,9 tortas. La
panadería tiene que cuidar la venta de tortas, no solo el volumen.

**12.7.** Base: margen **$1.530**, equilibrio **2.740** frascos (2.739,9), utilidad **$2.784.800**.

| Escenario | Dato nuevo | Equilibrio | Utilidad | Caída |
|---|---|---|---|---|
| Precio −8 % | 2.981 | 3.298,7 | 1.602.848 | 42,4 % |
| Costo variable +10 % | 1.881 | 3.084,6 | 2.005.040 | 28,0 % |
| Volumen −10 % | 4.104 | 2.739,9 | 2.087.120 | 25,1 % |
| Costo fijo +15 % | 4.820.800 | 3.150,8 | 2.156.000 | 22,6 % |

Orden por daño: precio, costo variable, volumen y fijo. Un 1 % de cada palanca mueve la utilidad en:
precio **$147.744** (5,31 %), costo variable **$77.976** (2,80 %), volumen **$69.768** (2,51 %) y fijo
**$41.920** (1,51 %). Un punto de precio vale más del doble que un punto de volumen: antes de bajar el
precio para vender más, hay que estar seguro de que el volumen sube mucho.

**12.8.** (a)

| | Sin máquina | Con máquina |
|---|---|---|
| Margen unitario | 2.520 | 3.140 |
| Equilibrio | 839,3 | 1.155,1 |
| Utilidad con 2.240 bolsas | 3.529.800 | 3.406.600 |
| GAO | 1,60 | 2,06 |
| Margen de seguridad | 62,5 % | 48,4 % |

(b) Indiferencia: (3.627.000 − 2.115.000) / (2.930 − 2.310) = **2.439 bolsas** (2.438,7), con
$4.030.548 de utilidad en las dos opciones. Sobre ese volumen gana la máquina. (c) Con 2.240 bolsas la
máquina deja $123.200 menos al mes y más riesgo (GAO más alto, margen de seguridad más bajo). **No la
compra todavía**: la compra cuando la venta pase con holgura de 2.439 bolsas.

**12.9.** (a) La demanda pide 74 + 51 + 62 = **187 horas** y hay 164: no alcanza. (b) Margen por hora:
kuchen **$14.500**, pie **$21.680**, tarta **\$9.830**. Se llena el horno en ese orden: 204 pies (51 h),
148 kuchen (74 h) y con las 39 horas que quedan, 39 tartas. Margen **$2.562.050**, utilidad
**$647.050**. Siguiendo el margen unitario (tarta primero): 62 tartas (62 h), 148 kuchen (74 h) y 112
pies con las 28 horas que quedan: margen **$2.289.500**, utilidad **$374.500**. La regla correcta deja
**$272.550** más al mes. La comprobación por fuerza bruta (todas las combinaciones enteras) da el mismo
óptimo. (c) Una hora más de horno sirve para una tarta más: vale **$9.830**. Es el precio sombra del
horno; si arrendar un horno extra cuesta menos que eso por hora, conviene.

**12.10.** (a) Margen **$27.750**. Utilidad 418 × 27.750 − 8.436.000 = **$3.163.500**. Equilibrio **304
socios**; margen de seguridad **27,3 %**. (b) Con $26.900 el margen baja a $22.750 y el equilibrio sube a
370,8 socios. Para ganar lo mismo: (8.436.000 + 3.163.500) / 22.750 = 509,9, es decir **510 socios**
(+22,0 %). **No caben**: con 500 socios ganaría $2.939.000. (c) Con publicidad: (8.436.000 + 1.480.000 +
3.163.500) / 27.750 = 471,3, es decir **472 socios** (+12,8 %), dentro de la capacidad; el equilibrio sube
a 357,3. Es viable si la campaña trae al menos 54 socios. (d) Con 500 socios, para ganar $3.163.500:
$p = 4{.}150 + (8{.}436{.}000 + 3{.}163{.}500)/500 =$ **$27.349**. Bajar el precio a $26.900 no se puede
pagar con volumen; la publicidad, quizás.

---

## 13. Caso integrador · Estampa Sur, cuánto tiene que vender

> Este caso sigue el mes de marzo de Estampa Sur (taller de serigrafía ficticio) por todo el ramo.
> La unidad 11 repartió el CIF fijo entre las prendas para el costo completo. Acá los fijos no se
> reparten: se pregunta cuánto hay que vender para cubrirlos.

**Lo que recibe.** De la unidad 11, el CIF fijo de marzo, **$3.849.833,33**; con los **$436.000** de
gastos de administración forma los costos fijos operacionales, **$4.285.833,33**. De la unidad 9 (y de
Optimización), el margen de contribución de cada prenda. Y las ventas de marzo: 5.300 prendas.

**Pregunta.** ¿Cuántas prendas al mes necesita vender el taller para no perder? ¿Cuánto aguanta una
caída? ¿Qué prenda empujar si la máquina se llena?

**Desarrollo.**

1. **Mezcla y margen ponderado.**

| | Poleras básicas | Polerones | Poleras estampado doble | Bolsas | Gorros |
|---|---|---|---|---|---|
| Vendidas en marzo | 2.120 | 795 | 795 | 954 | 636 |
| Mezcla | 40 % | 15 % | 15 % | 18 % | 12 % |
| Margen unitario | 1.380 | 3.940 | 2.270 | 960 | 1.170 |

Margen ponderado: **$1.796,7** por prenda promedio. Precio ponderado: $4.854 (las ventas netas de
$25.726.200 divididas por 5.300). Razón de margen: 37,0 %.

2. **Equilibrio.**

$$q_0 = \frac{4{.}285{.}833{,}33}{1{.}796{,}7} = 2{.}385{,}39 \text{ prendas} \qquad Y_0 = 2{.}385{,}39 \times 4{.}854 = 11{.}578{.}691$$

| En equilibrio | Poleras básicas | Polerones | Poleras estampado doble | Bolsas | Gorros |
|---|---|---|---|---|---|
| Prendas | 954,2 | 357,8 | 357,8 | 429,4 | 286,2 |
| Ingreso | 3.807.085 | 3.538.729 | 2.250.617 | 1.069.133 | 913.128 |

La planilla `u12_punto_de_equilibrio.xlsx` (hoja «Estampa Sur») hace esta cuenta con fórmulas y
comprueba que en equilibrio la utilidad es cero.

3. **Marzo completo.** Margen total 5.300 × 1.796,7 = $9.522.510. Utilidad operacional
**$5.236.676,67**: es el resultado por costeo variable de la unidad 10, como tiene que ser. Margen de
seguridad: (5.300 − 2.385,39) / 5.300 = **55,0 %**. GAO: 9.522.510 / 5.236.676,67 = **1,82**.

4. **Si se cubre también el interés.** El préstamo cobra $73.600 de interés en marzo (unidad 6). Para
   cubrirlo, el taller necesita (4.285.833,33 + 73.600) / 1.796,7 = **2.426,36** prendas. La utilidad
   antes de impuesto, por costeo variable, es $5.163.076,67.

5. **Un mes malo.** Si las ventas caen 20 % (4.240 prendas con la misma mezcla), la utilidad baja a
   $3.332.174,67: un 36,4 % menos, 1,82 veces la caída de las ventas.

6. **Si la máquina se llena.** Margen por segundo de estampado:

| | Poleras básicas | Polerones | Poleras estampado doble | Bolsas | Gorros |
|---|---|---|---|---|---|
| Margen por segundo | 46,00 | 43,78 | 20,64 | 48,00 | 39,00 |

**Lectura.** Estampa Sur cubre sus fijos con **2.385 prendas** al mes (unos $11.578.691 de venta) y en
marzo vendió 5.300: aunque las ventas cayeran a menos de la mitad, no perdería (margen de seguridad de
55 %). Con un GAO de 1,82 la utilidad se mueve casi el doble que las ventas: un mes de 20 % menos se
nota, pero no asusta. Si algún mes la demanda supera la capacidad de estampado, el orden para llenar
la máquina es bolsas, poleras básicas, polerones, gorros y al final poleras de estampado doble, que
dejan por segundo menos de la mitad que las bolsas o las poleras básicas. Es la misma conclusión de la unidad 11 (la de
estampado doble es la que menos deja una vez que se mira cuánto usa la máquina) y la que el modelo
lineal de Optimización formaliza con todos los recursos a la vez.

**Lo que cierra el ramo.** Con esta unidad el mes de marzo queda completo: los asientos y el balance
(unidades 1 a 8) dicen qué pasó, y los costos (unidades 9 a 12) dicen cuánto cuesta cada prenda, cuál
conviene y cuánto hay que vender.

---

## 14. Para seguir

**En los libros del ramo.**

- Obligatorios del programa: Gálvez y Clarke, *Contabilidad financiera para la dirección de empresas*,
  Ediciones UC, e Irarrázabal, *Contabilidad: fundamentos y usos*, Ediciones UC, 2014.
- Complementarios: Garrison, Noreen y Brewer, *Contabilidad administrativa*, McGraw-Hill, 2007
  (relaciones de costo-volumen-utilidad, equilibrio con varios productos, margen de seguridad,
  apalancamiento operativo y decisiones con recursos restringidos), y Horngren, *Contabilidad de
  costos*, Pearson, 2012 (análisis costo-volumen-utilidad y sensibilidad).

**Abierto y gratis.**

- Franklin, Graybeal y Cooper, *Principles of Accounting, Volume 2: Managerial Accounting*, OpenStax
  (2019), en inglés, licencia CC BY-NC-SA. Capítulo 3, secciones 3.1 a 3.5 (margen de contribución,
  equilibrio en unidades y en dólares, sensibilidad con uno y con varios productos, margen de seguridad
  y apalancamiento operativo): https://openstax.org/books/principles-managerial-accounting/pages/3-why-it-matters

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame tres productos con precios, costos variables,
una mezcla y un recurso escaso; déjame calcular el equilibrio y la mejor mezcla, y corrígeme paso a
paso».
