---
ramo: Gestión de Operaciones
unidad: 8
titulo: MRP · planificación de requerimientos de materiales
version: 0.1 (15-10-2026)
requiere: [05-inventarios, 07-programa-maestro]
alimenta: [09-capacidad-aproximada, 10-programacion-de-operaciones]
verificacion: verificacion/u08_mrp.py
---

# Unidad 8 · MRP

**Qué vas a poder hacer.** Desarmar un producto en su lista de materiales y contar cuánto se
necesita de cada pieza; armar el registro MRP de un componente (requerimientos brutos, recepciones
programadas, disponible, requerimientos netos, recepción y liberación planeada); aplicar lote a
lote, cantidad fija y lotes múltiplos; bajar la explosión nivel por nivel con sus tiempos de
entrega, y decir qué órdenes hay que emitir cada semana y cuáles ya vienen atrasadas.

**Lo que necesitas antes.** El programa maestro (unidad 7): de ahí sale cuánto se fabrica de cada
producto final y en qué semana. Del EOQ (unidad 5) basta con saber que equilibra costo de pedir y
costo de mantener.

**Tiempo.** Unas 5 horas: 1,5 de lectura con el ejemplo y 3,5 de práctica. Los registros MRP se
hacen rápido a mano una vez que se agarra el ritmo; el primero cuesta.

---

## 1. La idea

Un producto final tiene **demanda independiente**: la decide el mercado y se pronostica. Sus
piezas tienen **demanda dependiente**: si el programa maestro dice «armar 200 sillas en la semana
4», las 800 patas que llevan no se pronostican, se calculan. El MRP hace ese cálculo para cada
pieza y cada semana, y responde tres preguntas: **qué** pedir, **cuánto** y **cuándo** liberar la
orden para que llegue a tiempo.

Es un sistema **de empuje** (*push*): parte del plan y empuja las órdenes hacia el taller y los
proveedores, aunque nadie las haya pedido todavía aguas abajo. Necesita cuatro entradas:

| Entrada | Qué aporta |
|---|---|
| Programa maestro (MPS) | cuántos productos finales y en qué semana |
| Lista de materiales (LDM) | qué piezas lleva cada producto y cuántas |
| Registro de inventario | lo disponible hoy, las órdenes ya emitidas (recepciones programadas) y el stock de seguridad |
| Tiempos de entrega | cuántas semanas pasan entre liberar una orden y tener la pieza |

Si una de las cuatro está mal, el MRP calcula perfecto un plan equivocado. Por eso exige registros
de inventario casi sin error: un conteo que dice 500 tapas cuando hay 300 genera un faltante que
nadie vio venir.

---

## 2. La lista de materiales y la explosión

La **lista de materiales** dice de qué está hecho un producto. Se dibuja como árbol:

- El producto final es el **nivel 0**. Sus piezas directas son el nivel 1, las piezas de esas
  piezas el nivel 2, y así.
- Un artículo con piezas debajo es **padre**; las piezas son sus **hijos**. Cada flecha lleva la
  cantidad por unidad del padre.
- **Explotar** es multiplicar hacia abajo: para 25 padres con 3 hijos cada uno hacen falta 75
  hijos; si cada hijo lleva 4 tornillos, 300 tornillos.

**Código de nivel más bajo.** Si una pieza aparece en dos niveles (un perno que va directo al
producto y también dentro de un subensamble), se planifica **una sola vez, en el nivel más bajo
donde aparece**. Así, cuando le toca su turno, ya se conocen todas las órdenes de sus padres y se
suman en un solo requerimiento bruto.

**Lo que se mueve en la explosión es la liberación del padre, no su recepción.** El hijo tiene que
estar disponible cuando el padre **empieza** a fabricarse:

$$RB^{\text{hijo}}_t = \sum_{\text{padres}} q_{\text{padre, hijo}} \cdot LIB^{\text{padre}}_t$$

Si el padre se arma dentro de la misma semana (plazo 0), su liberación coincide con su programa y
el requerimiento del hijo cae en la semana del MPS. Esa es la convención de esta unidad para el
producto final: **el MPS dice cuántas unidades se arman cada semana.**

---

## 3. El registro MRP

Cada pieza tiene su registro: una tabla con una columna por semana y seis filas. En esta base se
abrevian así:

| Fila | Nombre completo | Qué es |
|---|---|---|
| RB | requerimiento bruto | lo que piden los padres (o el MPS) esa semana |
| RP | recepción programada | una orden **ya emitida** que llega esa semana |
| Disp. | disponible (inventario proyectado) | lo que queda al cierre de la semana |
| RN | requerimiento neto | lo que falta después de usar el disponible y las recepciones |
| Rec. pl. | recepción planeada | la orden nueva que debe **llegar** esa semana (ya ajustada al lote) |
| Lib. pl. | liberación planeada | la misma orden, corrida hacia atrás en el tiempo de entrega |

Con disponible inicial $D_0$, stock de seguridad $SS$ y tiempo de entrega $L$, semana a semana:

$$RN_t = \max\left(0,\; RB_t + SS - D_{t-1} - RP_t\right)$$

$$REC_t = \text{lote}(RN_t) \qquad D_t = D_{t-1} + RP_t + REC_t - RB_t \qquad LIB_{t-L} = REC_t$$

Tres reglas que evitan la mitad de los errores:

1. **El stock de seguridad no se consume en el plan.** Entra en el neto: el disponible nunca baja
   de $SS$ en una semana con orden planeada.
2. **La recepción programada no se toca.** Es una orden que ya existe; el MRP la usa, no la vuelve
   a pedir.
3. **Si $t - L < 1$, la liberación está vencida.** Debió emitirse antes de hoy. El registro no
   tiene columna para eso: se anota aparte y se actúa (acelerar al proveedor, usar parte del stock
   de seguridad o mover el MPS).

---

## 4. Políticas de lote

| Política | Cuánto se pide cuando $RN_t > 0$ | Cuándo conviene |
|---|---|---|
| **Lote a lote** (L4L) | exactamente $RN_t$ | pedir es barato; deja el menor inventario |
| **Cantidad fija** (FOQ) | $Q$ o, si no alcanza, el menor múltiplo de $Q$ que cubra $RN_t$ | hay un lote económico ($Q$ cercano al EOQ) o un tamaño de máquina |
| **Lotes múltiplos** de $m$ | el menor múltiplo de $m$ que cubra $RN_t$ | el proveedor vende en cajas, sacos o tarros |

En la cuenta, cantidad fija y múltiplos hacen lo mismo ($\lceil RN_t / Q \rceil \cdot Q$). Cambia el
propósito y la escala: el lote fijo es grande y cubre varias semanas; el múltiplo es un empaque
chico que solo redondea el neto hacia arriba. Algunos libros, con cantidad fija, piden el neto
exacto cuando supera $Q$; si usas otro texto, revisa qué convención trae.

**Costo de una política.** Con $S$ el costo de pedir y $H$ el costo de mantener una unidad una
semana (sobre el disponible al cierre):

$$\text{Costo} = S \cdot (\text{n.º de pedidos}) + H \cdot \sum_t D_t$$

Lote a lote no paga mantener pero paga muchos pedidos. Un lote grande hace lo contrario.

**Balance de periodo parcial** (PPB). Una regla que busca el punto medio sin calcular todas las
combinaciones. Se define el **EPP** (*economic part period*), las unidades-semana de inventario que
cuestan lo mismo que un pedido:

$$EPP = \frac{S}{H}$$

Desde la primera semana con neto, se prueba cubrir 1, 2, 3… semanas. Cubrir la semana $j$ con un
pedido que llega en $t$ deja esas unidades guardadas $(j - t)$ semanas. Se acumulan las
unidades-semana y se elige la cobertura cuyo acumulado quede **más cerca** del EPP. Luego se
repite desde la siguiente semana con neto.

---

## 5. Lo que el MRP no ve

- **Capacidad.** Planifica con capacidad infinita: puede liberar más trabajo del que el taller
  hace en una semana. Eso se revisa en la unidad 9.
- **Nerviosismo.** Un cambio chico en el MPS mueve órdenes de varias semanas y de varios niveles
  (ejercicio 8.9). Por eso las empresas congelan las semanas más cercanas.
- **Variabilidad.** Los tiempos de entrega se toman como fijos. El stock de seguridad es la única
  defensa contra un proveedor que se atrasa.

---

## 6. Ejemplo resuelto · Mermeladas del Itata

Una fábrica de mermeladas de Ñuble arma **cajas de regalo** para fin de año. El programa maestro
dice cuántas cajas se arman cada semana (el armado cabe dentro de la semana):

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Cajas (MPS) | 0 | 140 | 0 | 210 | 95 | 0 | 170 | 130 |

**Paso 1 · Lista de materiales y niveles.**

| Artículo | Nivel | Por padre | Plazo | Política | Disponible | Otros |
|---|---|---|---|---|---|---|
| Caja de regalo | 0 | — | 0 | — | — | — |
| Frasco lleno | 1 | 3 por caja | 1 sem. | lote a lote | 380 | 300 llegan en la sem. 2 |
| Tapa | 2 | 1 por frasco | 2 sem. | múltiplos de 500 | 450 | stock de seguridad 50 |
| Estuche | 1 | 1 por caja | 2 sem. | cantidad fija 400 | 220 | — |

El frasco lleno lo fabrica la planta (llenado y tapado), así que sus tapas dependen de **cuándo
empieza** el llenado. El orden de cálculo es nivel por nivel: frasco y estuche, luego tapa.

**Paso 2 · Frasco lleno (lote a lote, plazo 1).** RB = 3 × MPS.

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 420 |  | 630 | 285 |  | 510 | 390 |
| RP |  | 300 |  |  |  |  |  |  |
| Disp. | 380 | 260 | 260 | 0 | 0 | 0 | 0 | 0 |
| RN |  |  |  | 370 | 285 |  | 510 | 390 |
| Rec. pl. |  |  |  | 370 | 285 |  | 510 | 390 |
| Lib. pl. |  |  | 370 | 285 |  | 510 | 390 |  |

En la semana 2 hay $380 + 300 = 680$ para 420: sobran 260. En la semana 4 se necesitan 630 y hay
260, así que el neto es 370. Lote a lote pide justo eso y lo libera una semana antes.

**Paso 3 · Tapa (múltiplos de 500, plazo 2, stock de seguridad 50).** Su RB es la **liberación**
del frasco (fila Lib. pl. de arriba), no su recepción.

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  |  | 370 | 285 |  | 510 | 390 |  |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 450 | 450 | 80 | 295 | 295 | 285 | 395 | 395 |
| RN |  |  |  | 255 |  | 265 | 155 |  |
| Rec. pl. |  |  |  | 500 |  | 500 | 500 |  |
| Lib. pl. |  | 500 |  | 500 | 500 |  |  |  |

Semana 3: $370 + 50 - 450 = -30$, no hay neto y quedan 80. Semana 4: $285 + 50 - 80 = 255$; se
redondea a 500 y quedan 295. El disponible nunca baja de 50.

**Paso 4 · Estuche (cantidad fija 400, plazo 2).** RB = 1 × MPS.

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 140 |  | 210 | 95 |  | 170 | 130 |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 220 | 80 | 80 | 270 | 175 | 175 | 5 | 275 |
| RN |  |  |  | 130 |  |  |  | 125 |
| Rec. pl. |  |  |  | 400 |  |  |  | 400 |
| Lib. pl. |  | 400 |  |  |  | 400 |  |  |

**Paso 5 · Las órdenes de cada semana.**

| Semana | Órdenes a liberar |
|---|---|
| 1 | ninguna |
| 2 | comprar 500 tapas y 400 estuches |
| 3 | llenar 370 frascos |
| 4 | llenar 285 frascos · comprar 500 tapas |
| 5 | comprar 500 tapas |
| 6 | llenar 510 frascos · comprar 400 estuches |
| 7 | llenar 390 frascos |

**Cómo se lee.**

- Esta semana no hay que hacer nada, pero la próxima salen dos compras. Si el proveedor de tapas
  necesitara tres semanas en vez de dos, la orden de la semana 2 ya estaría vencida.
- El frasco termina cada semana en 0: lote a lote no deja inventario, a cambio de una orden por
  semana con producción.
- Las tapas cargan unas 300 unidades por el empaque de 500. Es el precio de comprar en cajas.

---

## 7. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Usar la recepción del padre como RB del hijo | El hijo se necesita cuando el padre **empieza**: usa la fila Lib. pl. del padre |
| Olvidar multiplicar por la cantidad de la LDM | RB del hijo = cantidad por padre × liberación del padre |
| Volver a pedir una recepción programada | Ya existe: se suma al disponible, no entra al neto |
| Dejar que el disponible baje del stock de seguridad | El neto es $RB + SS - D_{t-1} - RP$, no $RB - D_{t-1} - RP$ |
| Correr la liberación hacia adelante | Se corre **hacia atrás**: $LIB_{t-L} = REC_t$ |
| Planificar una pieza común dos veces | Una pieza se calcula una vez, en su nivel más bajo, sumando todos sus padres |
| Callar una liberación que cae antes de la semana 1 | Es una orden vencida: se anota y se decide qué hacer |

---

## 8. Práctica

Diez ejercicios: 8.1 a 8.4 básicos, 8.5 a 8.8 intermedios, 8.9 y 8.10 de desafío. Las pautas están
en la sección 9. En todos, el disponible inicial es el de la semana 0 y no hay stock de seguridad
salvo que se diga.

**8.1 · Kit de riego por goteo (básico).** Un taller de Ñuble arma kits de riego para huertos. Cada
kit lleva 1 programador, 4 líneas de goteo y 2 conectores (para la matriz). Cada línea de goteo
lleva 1 tramo de manguera, 12 goteros, 1 conector y 1 tapón. (a) Dibuja el árbol con sus niveles.
(b) ¿Cuánto hace falta de cada pieza para un pedido de 250 kits, si en bodega hay 140 líneas ya
armadas y nada más? (c) ¿Cuál es el código de nivel más bajo del conector y por qué importa?

**8.2 · Cajas de cartón para arándanos (básico).** Un packing compra cajas con plazo de 1 semana.
Hay 450 en bodega y una orden de 200 que llega en la semana 2. Arma el registro con lote a lote.

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB | 0 | 340 | 260 | 0 | 410 | 380 | 0 | 290 |

**8.3 · Las mismas cajas en lotes de 800 (básico).** Repite 8.2 con cantidad fija de 800 cajas.
Compara con 8.2: número de pedidos y suma del disponible de las ocho semanas.

**8.4 · Pegamento en tarros (básico).** Una mueblería usa 0,06 kg de pegamento por silla. El
pegamento viene en tarros de 4 kg, con plazo de 1 semana, y hay 14 kg. Arma el registro en kg con
lotes múltiplos de 4 y di cuántos tarros se compran cada semana.

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Sillas (MPS) | 220 | 0 | 310 | 190 | 0 | 260 |

**8.5 · Mesa plegable, dos niveles (intermedio).** La mesa se fabrica con plazo de 1 semana (lote
a lote, 60 en bodega) y lleva 4 patas y 1 tablero. Las patas se compran con plazo de 2 semanas en
lotes fijos de 600 (hay 300); los tableros, con plazo de 1 semana y lote a lote (hay 40). Arma los
tres registros. Los requerimientos de mesas terminadas son:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB mesas | 0 | 0 | 130 | 110 | 0 | 140 | 125 | 75 |

**8.6 · Stock de seguridad y una orden que llega tarde (intermedio).** Un repuesto tiene plazo de
2 semanas, lote a lote, stock de seguridad de 40, 120 en bodega y una orden de 250 que llega en la
semana 3. (a) Arma el registro. (b) ¿Qué órdenes debieron liberarse antes de hoy? ¿Qué harías con
cada una? (c) Rehaz el registro sin stock de seguridad: ¿qué cambia en las órdenes vencidas?

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| RB | 95 | 130 | 60 | 140 | 0 | 110 |

**8.7 · Un perno en dos niveles (intermedio).** Un escritorio lleva 1 cajonera y 6 pernos; cada
cajonera lleva 4 pernos. Las cajoneras se fabrican con plazo de 1 semana, lote a lote, y hay 30.
Los pernos se compran con plazo de 1 semana en cajas de 250 y hay 400. Las liberaciones planeadas
de armado de escritorios son las de abajo. Arma el registro de la cajonera y después el del perno
(¿por qué en ese orden?).

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Lib. pl. escritorios | 0 | 45 | 0 | 60 | 35 | 50 |

**8.8 · ¿Cuál política sale más barata? (intermedio).** Un insumo comprado, plazo de 1 semana, sin
inventario inicial. Pedir cuesta $120.000 y mantener una unidad una semana, \$150. (a) Calcula el
EOQ con la demanda semanal promedio y redondéalo a la centena. (b) Arma los registros con lote a
lote y con esa cantidad fija. (c) Compara el costo de pedir más mantener.

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB | 0 | 260 | 340 | 0 | 310 | 280 | 0 | 360 |

**8.9 · Silla de terraza y un cambio de último minuto (desafío).** El MPS dice cuántas sillas se
arman cada semana (el armado cabe en la semana). Cada silla lleva 1 respaldo, 4 patas y 3 listones
(el asiento). Cada respaldo lleva 5 listones.

| Artículo | Plazo | Política | Disponible | Otros |
|---|---|---|---|---|
| Respaldo (fabricado) | 1 sem. | lote a lote | 80 | — |
| Pata (comprada) | 2 sem. | cantidad fija 1.200 | 600 | — |
| Listón (comprado) | 2 sem. | múltiplos de 50 | 900 | stock de seguridad 100 |

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Sillas (MPS) | 0 | 115 | 0 | 140 | 95 | 0 | 135 | 105 |

(a) Arma los tres registros (¿cuál va al final y por qué?). (b) Ventas consigue un pedido y la
semana 4 sube de 140 a 175 sillas. Rehaz los registros: ¿qué órdenes cambian y en qué semanas?
(c) ¿Qué le recomendarías a la planta para que esto no la desordene cada semana?

**8.10 · Balance de periodo parcial (desafío).** Un componente con plazo de 1 semana tiene 210 en
bodega (cubren justo la semana 1). Pedir cuesta $90.000 y mantener una unidad una semana, \$400.
(a) Calcula el EPP. (b) Arma los lotes con balance de periodo parcial y di en qué semana se libera
cada uno. (c) Compara el costo con lote a lote.

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB | 210 | 45 | 130 | 0 | 95 | 140 | 30 | 175 |

---

## 9. Pautas

**8.1.** Nivel 0: kit. Nivel 1: programador, línea de goteo y conector. Nivel 2: manguera, gotero,
conector y tapón (bajo la línea). Para 250 kits hacen falta 1.000 líneas; con 140 en bodega se arman
**860**. De ahí: 860 tramos de manguera, **10.320** goteros ($12 \times 860$), 860 tapones y 250
programadores. Conectores: $2 \times 250 + 860 =$ **1.360**. El conector aparece en los niveles 1 y
2, así que su código de nivel más bajo es 2: se calcula después de las líneas, sumando lo que piden
el kit y las líneas. Si se calculara en el nivel 1, se perdería la parte de las líneas o se
pediría dos veces. Sin las 140 líneas en bodega habrían sido 1.500.

**8.2.** Tres pedidos; la suma del disponible es 860.

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 340 | 260 |  | 410 | 380 |  | 290 |
| RP |  | 200 |  |  |  |  |  |  |
| Disp. | 450 | 310 | 50 | 50 | 0 | 0 | 0 | 0 |
| RN |  |  |  |  | 360 | 380 |  | 290 |
| Rec. pl. |  |  |  |  | 360 | 380 |  | 290 |
| Lib. pl. |  |  |  | 360 | 380 |  | 290 |  |

**8.3.** Dos pedidos; la suma del disponible sube a 1.990. Se ahorra un pedido a cambio de más del
doble de inventario.

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 340 | 260 |  | 410 | 380 |  | 290 |
| RP |  | 200 |  |  |  |  |  |  |
| Disp. | 450 | 310 | 50 | 50 | 440 | 60 | 60 | 570 |
| RN |  |  |  |  | 360 |  |  | 230 |
| Rec. pl. |  |  |  |  | 800 |  |  | 800 |
| Lib. pl. |  |  |  | 800 |  |  | 800 |  |

**8.4.** RB = 0,06 × MPS. Se compran 5 tarros en la semana 2, 3 en la semana 3 y 4 en la semana 5.

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| RB | 13,2 |  | 18,6 | 11,4 |  | 15,6 |
| RP |  |  |  |  |  |  |
| Disp. | 0,8 | 0,8 | 2,2 | 2,8 | 2,8 | 3,2 |
| RN |  |  | 17,8 | 9,2 |  | 12,8 |
| Rec. pl. |  |  | 20,0 | 12,0 |  | 16,0 |
| Lib. pl. |  | 20,0 | 12,0 |  | 16,0 |  |

**8.5.** Mesa:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  |  | 130 | 110 |  | 140 | 125 | 75 |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 60 | 60 | 0 | 0 | 0 | 0 | 0 | 0 |
| RN |  |  | 70 | 110 |  | 140 | 125 | 75 |
| Rec. pl. |  |  | 70 | 110 |  | 140 | 125 | 75 |
| Lib. pl. |  | 70 | 110 |  | 140 | 125 | 75 |  |

Pata (RB = 4 × Lib. pl. de la mesa):

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 280 | 440 |  | 560 | 500 | 300 |  |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 300 | 20 | 180 | 180 | 220 | 320 | 20 | 20 |
| RN |  |  | 420 |  | 380 | 280 |  |  |
| Rec. pl. |  |  | 600 |  | 600 | 600 |  |  |
| Lib. pl. | 600 |  | 600 | 600 |  |  |  |  |

Tablero (RB = 1 × Lib. pl. de la mesa):

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 70 | 110 |  | 140 | 125 | 75 |  |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 40 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RN |  | 30 | 110 |  | 140 | 125 | 75 |  |
| Rec. pl. |  | 30 | 110 |  | 140 | 125 | 75 |  |
| Lib. pl. | 30 | 110 |  | 140 | 125 | 75 |  |  |

La primera orden de patas y la de tableros caen en la semana 1: se emiten hoy, sin margen.

**8.6.** (a) Con stock de seguridad:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| RB | 95 | 130 | 60 | 140 |  | 110 |
| RP |  |  | 250 |  |  |  |
| Disp. | 40 | 40 | 230 | 90 | 90 | 40 |
| RN | 15 | 130 |  |  |  | 60 |
| Rec. pl. | 15 | 130 |  |  |  | 60 |
| Lib. pl. |  |  |  | 60 |  |  |

(b) Dos recepciones no tienen liberación posible: 15 unidades para la semana 1 (debieron pedirse en
la semana −1) y 130 para la semana 2 (en la semana 0). Las 15 solo reponen el stock de seguridad:
se acepta bajar de 40 a 25 esa semana, que para eso está. Las 130 son un faltante real: se
llama al proveedor para acelerar, o se pide a ventas mover parte del pedido de la semana 2 a la 3,
cuando llegan las 250.

(c) Sin stock de seguridad queda una sola orden vencida, de 105 para la semana 2:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| RB | 95 | 130 | 60 | 140 |  | 110 |
| RP |  |  | 250 |  |  |  |
| Disp. | 25 | 0 | 190 | 50 | 50 | 0 |
| RN |  | 105 |  |  |  | 60 |
| Rec. pl. |  | 105 |  |  |  | 60 |
| Lib. pl. |  |  |  | 60 |  |  |

**8.7.** Primero la cajonera, porque el perno es su hijo y además está en el nivel 2 (su código de
nivel más bajo): solo cuando se conocen las liberaciones de la cajonera se pueden sumar sus 4 pernos
a los 6 del escritorio.

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| RB |  | 45 |  | 60 | 35 | 50 |
| RP |  |  |  |  |  |  |
| Disp. | 30 | 0 | 0 | 0 | 0 | 0 |
| RN |  | 15 |  | 60 | 35 | 50 |
| Rec. pl. |  | 15 |  | 60 | 35 | 50 |
| Lib. pl. | 15 |  | 60 | 35 | 50 |  |

Perno, con RB = 6 × escritorios + 4 × Lib. pl. de la cajonera (por ejemplo, semana 4:
$6 \times 60 + 4 \times 35 = 500$):

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| RB | 60 | 270 | 240 | 500 | 410 | 300 |
| RP |  |  |  |  |  |  |
| Disp. | 340 | 70 | 80 | 80 | 170 | 120 |
| RN |  |  | 170 | 420 | 330 | 130 |
| Rec. pl. |  |  | 250 | 500 | 500 | 250 |
| Lib. pl. |  | 250 | 500 | 500 | 250 |  |

**8.8.** (a) Demanda semanal promedio: 1.550 / 8 = 193,8 unidades. EOQ =
$\sqrt{2 \cdot 193{,}75 \cdot 120.000 / 150}$ = 556,8, que redondeado da **600**. (b) Lote a lote:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 260 | 340 |  | 310 | 280 |  | 360 |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RN |  | 260 | 340 |  | 310 | 280 |  | 360 |
| Rec. pl. |  | 260 | 340 |  | 310 | 280 |  | 360 |
| Lib. pl. | 260 | 340 |  | 310 | 280 |  | 360 |  |

Cantidad fija de 600:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 260 | 340 |  | 310 | 280 |  | 360 |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 0 | 340 | 0 | 0 | 290 | 10 | 10 | 250 |
| RN |  | 260 |  |  | 310 |  |  | 350 |
| Rec. pl. |  | 600 |  |  | 600 |  |  | 600 |
| Lib. pl. | 600 |  |  | 600 |  |  | 600 |  |

(c) Lote a lote: 5 pedidos, $600.000 de pedir y mantener \$0, total **$600.000**. Cantidad fija:
3 pedidos ($360.000) más 900 unidades-semana de inventario ($135.000), total **$495.000**.
Con un pedido tan caro conviene el lote grande. Ojo: el EOQ supone demanda pareja; aquí la demanda
salta, y el último lote deja 250 unidades guardadas al final del horizonte.

**8.9.** (a) El listón va al final: está en el nivel 1 (asiento) y en el nivel 2 (dentro del
respaldo), así que necesita las liberaciones del respaldo. Su RB es
$3 \times \text{MPS} + 5 \times \text{Lib. pl. del respaldo}$.

Respaldo:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 115 |  | 140 | 95 |  | 135 | 105 |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 80 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RN |  | 35 |  | 140 | 95 |  | 135 | 105 |
| Rec. pl. |  | 35 |  | 140 | 95 |  | 135 | 105 |
| Lib. pl. | 35 |  | 140 | 95 |  | 135 | 105 |  |

Pata:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 460 |  | 560 | 380 |  | 540 | 420 |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 600 | 140 | 140 | 780 | 400 | 400 | 1.060 | 640 |
| RN |  |  |  | 420 |  |  | 140 |  |
| Rec. pl. |  |  |  | 1.200 |  |  | 1.200 |  |
| Lib. pl. |  | 1.200 |  |  | 1.200 |  |  |  |

Listón:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB | 175 | 345 | 700 | 895 | 285 | 675 | 930 | 315 |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 725 | 380 | 130 | 135 | 100 | 125 | 145 | 130 |
| RN |  |  | 420 | 865 | 250 | 675 | 905 | 270 |
| Rec. pl. |  |  | 450 | 900 | 250 | 700 | 950 | 300 |
| Lib. pl. | 450 | 900 | 250 | 700 | 950 | 300 |  |  |

(b) Con 175 sillas en la semana 4, el respaldo libera 175 en la semana 3:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 115 |  | 175 | 95 |  | 135 | 105 |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 80 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RN |  | 35 |  | 175 | 95 |  | 135 | 105 |
| Rec. pl. |  | 35 |  | 175 | 95 |  | 135 | 105 |
| Lib. pl. | 35 |  | 175 | 95 |  | 135 | 105 |  |

Las patas absorben el cambio con los mismos dos lotes; solo baja el disponible:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 460 |  | 700 | 380 |  | 540 | 420 |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 600 | 140 | 140 | 640 | 260 | 260 | 920 | 500 |
| RN |  |  |  | 560 |  |  | 280 |  |
| Rec. pl. |  |  |  | 1.200 |  |  | 1.200 |  |
| Lib. pl. |  | 1.200 |  |  | 1.200 |  |  |  |

El listón cambia en casi todo el horizonte:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB | 175 | 345 | 875 | 1.000 | 285 | 675 | 930 | 315 |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 725 | 380 | 105 | 105 | 120 | 145 | 115 | 100 |
| RN |  |  | 595 | 995 | 280 | 655 | 885 | 300 |
| Rec. pl. |  |  | 600 | 1.000 | 300 | 700 | 900 | 300 |
| Lib. pl. | 600 | 1.000 | 300 | 700 | 900 | 300 |  |  |

Treinta y cinco sillas más en **una** semana cambiaron cinco liberaciones de listón, entre ellas la
de la semana 1 (de 450 a 600) y una que **baja** (semana 5, de 950 a 900, porque el redondeo a
múltiplos de 50 se reacomoda). Eso es el nerviosismo del MRP.

(c) Congelar las semanas más cercanas (por ejemplo, las dos primeras): dentro de esa franja el MPS
no se toca y un pedido nuevo entra desde la semana 3. También ayuda un poco de stock de seguridad
en el listón o lotes que no se recalculen cada semana.

**8.10.** (a) $EPP = 90.000 / 400 = 225$ unidades-semana. (b) Las 210 de bodega cubren la semana
1, así que los netos parten en la semana 2: 45, 130, 0, 95, 140, 30 y 175.

| Pedido que llega en | Cubrir hasta | Unidades-semana acumuladas | Elegido |
|---|---|---|---|
| Semana 2 | sem. 2 · 3 · 4 · 5 | 0 · 130 · 130 · 415 | hasta la 3 (o la 4, da igual): **175** |
| Semana 5 | sem. 5 · 6 · 7 · 8 | 0 · 140 · 200 · 725 | hasta la 7: **265** |
| Semana 8 | sem. 8 | 0 | **175** |

Con plazo de 1 semana, se liberan 175 en la semana 1, 265 en la semana 4 y 175 en la semana 7.
(c) Balance de periodo parcial: 3 pedidos ($270.000) más 330 unidades-semana ($132.000), total
**$402.000**. Lote a lote: 6 pedidos, **$540.000**. La regla ahorró $138.000 sin probar todas
las combinaciones; no garantiza el óptimo, pero suele quedar cerca.

---

## 10. Caso integrador · Estampa Sur, los insumos de las poleras básicas

> Este caso sigue a Estampa Sur por todo el ramo. Acá se usa el programa maestro de poleras
> básicas que salió de la unidad 7 y el lote económico de poleras lisas de la unidad 5. Si no has
> hecho esas unidades, parte de estas tablas.

El programa maestro de **poleras básicas** (unidades que se estampan cada semana, en lotes de 720)
es:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Poleras básicas (MPS) | 0 | 720 | 720 | 0 | 720 | 720 | 720 | 720 |

La semana 1 está en 0 porque ya hay un lote de 720 en curso (unidad 7). Cada polera básica lleva:

| Insumo | Por polera | Plazo | Política | Disponible |
|---|---|---|---|---|
| Polera lisa | 1 | 1 sem. | cantidad fija 2.100 (el EOQ de 2.104,3 de la unidad 5, redondeado) | 900 |
| Tinta | 0,015 kg | 2 sem. | múltiplos de 5 kg (tarros) | 12 kg |
| Etiqueta | 1 | 1 sem. | lote a lote | 0 |

Un lote se estampa dentro de la semana, así que cada insumo debe estar al inicio de la semana del
MPS: el RB de cada insumo es su cantidad por polera × MPS de esa misma semana.

**Pregunta.** Arma los tres registros y di qué órdenes de compra debe emitir Estampa Sur cada
semana. ¿Cuál no admite ningún atraso?

**Desarrollo.** Polera lisa:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 720 | 720 |  | 720 | 720 | 720 | 720 |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 900 | 180 | 1.560 | 1.560 | 840 | 120 | 1.500 | 780 |
| RN |  |  | 540 |  |  |  | 600 |  |
| Rec. pl. |  |  | 2.100 |  |  |  | 2.100 |  |
| Lib. pl. |  | 2.100 |  |  |  | 2.100 |  |  |

Tinta, en kg (cada lote de 720 poleras usa $0{,}015 \times 720 = 10{,}8$ kg):

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 10,8 | 10,8 |  | 10,8 | 10,8 | 10,8 | 10,8 |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 12,0 | 1,2 | 0,4 | 0,4 | 4,6 | 3,8 | 3,0 | 2,2 |
| RN |  |  | 9,6 |  | 10,4 | 6,2 | 7,0 | 7,8 |
| Rec. pl. |  |  | 10,0 |  | 15,0 | 10,0 | 10,0 | 10,0 |
| Lib. pl. | 10,0 |  | 15,0 | 10,0 | 10,0 | 10,0 |  |  |

Etiqueta:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| RB |  | 720 | 720 |  | 720 | 720 | 720 | 720 |
| RP |  |  |  |  |  |  |  |  |
| Disp. | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RN |  | 720 | 720 |  | 720 | 720 | 720 | 720 |
| Rec. pl. |  | 720 | 720 |  | 720 | 720 | 720 | 720 |
| Lib. pl. | 720 | 720 |  | 720 | 720 | 720 | 720 |  |

**Lectura.**

- **La tinta de la semana 1 no admite atraso.** Faltan 9,6 kg en la semana 3 y el plazo es de 2
  semanas: la orden de 10 kg se emite hoy. La liberación en la semana 1 con plazo 2 significa
  eso, no que haya margen. Si el registro hubiera pedido liberar antes de la semana 1, la orden ya
  estaría vencida (como en el ejercicio 8.6) y habría que acelerar al proveedor.
- Las poleras lisas llegan en lotes de 2.100 en las semanas 3 y 7. Cada lote cubre casi tres
  semanas de estampado y deja en promedio unas 930 poleras en bodega. El EOQ se calculó con
  demanda pareja; acá la demanda viene a saltos de 720, pero el lote sigue siendo razonable.
- Las etiquetas, lote a lote, salen una vez por semana con producción y nunca quedan en bodega. Si
  el proveedor cobrara por despacho, convendría juntarlas (un balance de periodo parcial, como en
  el ejercicio 8.10).
- Resumen de compras: semana 1, 10 kg de tinta y 720 etiquetas; semana 2, 2.100 poleras y 720
  etiquetas; semana 3, 15 kg de tinta; semana 4, 10 kg y 720 etiquetas; semana 5, 10 kg y 720
  etiquetas; semana 6, 2.100 poleras, 10 kg y 720 etiquetas; semana 7, 720 etiquetas.

**Lo que pasa a las unidades 9 y 10.** El MRP supone que el taller puede estampar todo lo que el
MPS pide. La unidad 9 revisa si el estampado y el planchado alcanzan, semana a semana. La unidad 10
ordena las órdenes de producción de la semana 6.

---

## 11. Para seguir

**En los libros del ramo.**

- Schroeder, *Administración de operaciones* (2.ª ed., 2004), capítulos 12, 13 y 16 (los que fija el
  programa para planificación y control de la producción).
- Heizer y Render, *Principios de administración de operaciones* (5.ª ed., 2004), capítulo de
  planificación de requerimientos de materiales: estructura del producto, registro MRP y técnicas
  de tamaño de lote. Sus problemas del final del capítulo son buena práctica adicional.
- Chase, Jacobs y Aquilano, *Administración de operaciones* (12.ª ed., 2009), capítulo de
  planeación de requerimiento de materiales.

**Abiertos y gratis.**

- Abbas y Goosheh, *Operations Management*, Fanshawe College (2025), en inglés. Busca en su índice
  la planificación de materiales (MRP). Descarga en la colección abierta de Ontario:
  https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/2473

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un registro MRP de dos niveles con una
recepción programada y corrígeme fila por fila».
