---
ramo: Gestión de Operaciones
unidad: 9
titulo: Capacidad aproximada
version: 0.1 (15-10-2026)
requiere: [03-proceso-y-capacidad, 07-programa-maestro, 08-mrp]
alimenta: [10-programacion-de-operaciones]
verificacion: verificacion/u09_capacidad_aproximada.py
---

# Unidad 9 · Capacidad aproximada

**Qué vas a poder hacer.** Revisar si un programa maestro cabe en la planta antes de liberarlo:
calcular cuántas unidades debe procesar cada operación considerando su aprovechamiento, armar la
lista de capacidad de un producto (horas por unidad en cada centro de trabajo), cargar el MPS
semana a semana, compararlo con la capacidad disponible mediante la desviación y la desviación
acumulada, y decidir qué hacer cuando un centro no alcanza.

**Lo que necesitas antes.** Capacidad efectiva, utilización y eficiencia (unidad 3); el programa
maestro (unidad 7); la lista de materiales (unidad 8).

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. La idea

El MPS y el MRP planifican con **capacidad infinita**: suponen que el taller hace todo lo que se le
pide. La **planificación aproximada de la capacidad** (RCCP, por *rough-cut capacity planning*) es
el control que se hace **antes** de aprobar el MPS: ¿alcanzan las horas de cada centro de trabajo,
semana a semana?

Es aproximada porque mira solo los productos finales y unos pocos centros críticos, sin bajar a
cada orden del MRP. Más adelante, con las órdenes liberadas, se puede hacer un cálculo fino
(planificación detallada de capacidad), pero si el MPS no pasa este primer filtro no tiene sentido
seguir.

Necesita cuatro insumos:

| Insumo | Qué aporta |
|---|---|
| Ruta de cada producto y componente | qué operaciones lleva, en qué orden y en qué centro de trabajo |
| Tiempo de carga unitario $t_i$ | horas estándar por unidad que pasa por la operación $i$ |
| Aprovechamiento $a_i$ | fracción de unidades buenas que salen de la operación $i$ |
| Lista de materiales y MPS | cuántos componentes lleva cada producto y cuántos productos por semana |

Hay dos técnicas. La **lista de capacidad** carga todo en la semana del MPS. El **perfil de
recursos** reparte la carga de los componentes en las semanas anteriores, según su tiempo de
entrega (sección 5).

---

## 2. El aprovechamiento se recorre hacia atrás

Si una operación aprovecha el 96 %, para sacar 100 unidades buenas tienen que entrar
$100 / 0{,}96 = 104{,}2$. Con varias operaciones en serie, la cuenta parte de la **última** y sube:

$$N_i = \frac{B_i}{a_i} \qquad B_{i-1} = N_i$$

- $B_i$ (requerimiento bruto) es lo que debe **salir bueno** de la operación $i$.
- $N_i$ (requerimiento neto a procesar) es lo que debe **entrar**: lo que la operación trabaja de
  verdad y, por lo tanto, lo que carga al centro.
- Para la última operación, $B = 1$ unidad de producto final.

**Componentes.** Un componente lo consume una operación del padre, normalmente la primera. Si el
padre lleva $q$ componentes por unidad, la última operación del componente debe entregar
$q \cdot N$ de la primera operación del padre, y desde ahí se repite la cuenta hacia atrás por la
ruta del componente. Así una merma en el padre también encarece al componente: hay que fabricar
componentes para las unidades que se van a perder.

---

## 3. Lista de capacidad

La carga que una unidad de producto final deja en el centro $k$ es la suma, sobre todas las
operaciones de ese centro (del producto y de sus componentes), de lo procesado por su tiempo:

$$c_{p,k} = \sum_{i \,\in\, k} N_i \, t_i$$

En esta base se arrastran tres decimales y no se redondea entre operaciones: se calcula la cadena
completa y se redondea al final.

## 4. Plan aproximado de capacidad

Para cada centro $k$ y semana $s$:

$$\text{Carga}_{k,s} = \sum_p c_{p,k} \cdot MPS_{p,s} \qquad \text{Desviación}_{k,s} = \text{Cap}_{k,s} - \text{Carga}_{k,s}$$

y la **desviación acumulada** suma las desviaciones desde la semana 1.

**Capacidad disponible.** Si el centro es de personas: personas × 8 h × 5 días = 40 h por persona y
semana. Si es de máquinas, se usa la capacidad efectiva de la unidad 3:

$$\text{Cap. efectiva} = \text{máquinas} \times \frac{\text{h}}{\text{turno}} \times \text{turnos} \times \text{días} \times U \times E$$

**Cómo se lee.**

| Lo que ves | Qué significa | Qué se hace |
|---|---|---|
| Desviación ≥ 0 | la semana cabe | nada |
| Desviación < 0 y acumulada ≥ 0 | sobrecarga **de calendario**: sobró capacidad antes | adelantar parte del trabajo a semanas con holgura (si se puede guardar y hay material) |
| Desviación < 0 y acumulada < 0 | falta capacidad **de verdad** hasta esa semana | horas extra, otro turno, subcontratar, mover personas o cambiar el MPS |

La holgura solo sirve **hacia adelante**: la capacidad que sobra en la semana 5 no arregla la
semana 3. Por eso se acumula desde la semana 1.

Antes de declarar inviable un MPS, revisa tres cosas: si parte de la carga ya está en proceso
(pedidos en curso), si hay componentes en bodega que no hay que fabricar, y si la capacidad que
usaste es solo jornada regular.

---

## 5. Perfil de recursos

La lista de capacidad pone la carga de un componente en la misma semana del producto final. Pero
si el componente se fabrica una semana antes (su tiempo de entrega), su carga cae una semana
antes. El **perfil de recursos** corre cada carga a la semana en que realmente ocurre:

$$\text{Carga}_{k,s} = \sum_p \sum_{\text{ítem}} c_{\text{ítem},k} \cdot MPS_{p,\,s + L_{\text{ítem}}}$$

donde $L_{\text{ítem}}$ es cuántas semanas antes del producto final se trabaja ese ítem. Si el
tiempo de entrega es de varias semanas, la carga se reparte entre ellas (por ejemplo, en partes
iguales). La diferencia importa justo en el borde: una sobrecarga que la lista de capacidad ponía
en la semana 2, con el perfil cae en la semana 1, donde no hay holgura anterior (ejercicio 9.7).

---

## 6. Ejemplo resuelto · Fierros del Laja

Una metalúrgica de Los Ángeles fabrica **parrillas** y **braseros**. Cada parrilla lleva 2
**rejillas**, que también se fabrican en la planta. Hay tres centros de trabajo: corte, soldadura y
pintura.

| Ítem | Operación | Centro | $t_i$ (h/u) | $a_i$ |
|---|---|---|---|---|
| Parrilla | O1 | Soldadura | 0,40 | 0,96 |
| | O2 | Pintura | 0,24 | 0,98 |
| Rejilla (2 por parrilla) | O3 | Corte | 0,08 | 0,94 |
| | O4 | Soldadura | 0,14 | 0,97 |
| Brasero | O5 | Corte | 0,22 | 0,96 |
| | O6 | Soldadura | 0,30 | 0,92 |
| | O7 | Pintura | 0,20 | 0,98 |

Personas por centro: corte 2, soldadura 5 y pintura 2; en las semanas 5 y 6 una persona de pintura
sale de vacaciones. El MPS propuesto es:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Parrillas | 0 | 230 | 260 | 0 | 310 | 240 |
| Braseros | 210 | 0 | 190 | 250 | 0 | 270 |

**Paso 1 · Requerimientos de la parrilla, hacia atrás.**

| Ítem | Op. | Centro | Bruto $B$ | Neto $N = B/a$ | $t$ | Carga $N \cdot t$ |
|---|---|---|---|---|---|---|
| Parrilla | O2 | Pintura | 1,000 | 1,020 | 0,24 | 0,245 |
| | O1 | Soldadura | 1,020 | 1,063 | 0,40 | 0,425 |
| Rejilla | O4 | Soldadura | $2 \times 1{,}063 = 2{,}126$ | 2,192 | 0,14 | 0,307 |
| | O3 | Corte | 2,192 | 2,331 | 0,08 | 0,187 |

La rejilla parte de $2 \times 1{,}063$ porque O1 consume dos rejillas por cada parrilla que **entra**
a soldadura, incluidas las que se van a perder.

**Paso 2 · Requerimientos del brasero.**

| Op. | Centro | Bruto $B$ | Neto $N$ | $t$ | Carga |
|---|---|---|---|---|---|
| O7 | Pintura | 1,000 | 1,020 | 0,20 | 0,204 |
| O6 | Soldadura | 1,020 | 1,109 | 0,30 | 0,333 |
| O5 | Corte | 1,109 | 1,155 | 0,22 | 0,254 |

**Paso 3 · Lista de capacidad (horas por unidad de producto final).**

| | Corte | Soldadura | Pintura |
|---|---|---|---|
| Parrilla (con sus 2 rejillas) | 0,187 | $0{,}425 + 0{,}307 =$ 0,732 | 0,245 |
| Brasero | 0,254 | 0,333 | 0,204 |

**Paso 4 · Plan de capacidad por centro (horas).** Capacidad: corte $2 \times 40 = 80$, soldadura
$5 \times 40 = 200$, pintura 80 (40 en las semanas 5 y 6).

Corte:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Carga Parrilla | 0,0 | 43,0 | 48,6 | 0,0 | 58,0 | 44,9 |
| Carga Brasero | 53,3 | 0,0 | 48,3 | 63,5 | 0,0 | 68,6 |
| Plan de capacidad | 53,3 | 43,0 | 96,9 | 63,5 | 58,0 | 113,5 |
| Capacidad disponible | 80,0 | 80,0 | 80,0 | 80,0 | 80,0 | 80,0 |
| Desviación | 26,7 | 37,0 | −16,9 | 16,5 | 22,0 | −33,5 |
| Desv. acumulada | 26,7 | 63,6 | 46,8 | 63,3 | 85,3 | 51,8 |

Soldadura:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Carga Parrilla | 0,0 | 168,4 | 190,3 | 0,0 | 226,9 | 175,7 |
| Carga Brasero | 69,9 | 0,0 | 63,3 | 83,2 | 0,0 | 89,9 |
| Plan de capacidad | 69,9 | 168,4 | 253,6 | 83,2 | 226,9 | 265,6 |
| Capacidad disponible | 200,0 | 200,0 | 200,0 | 200,0 | 200,0 | 200,0 |
| Desviación | 130,1 | 31,6 | −53,6 | 116,8 | −26,9 | −65,6 |
| Desv. acumulada | 130,1 | 161,7 | 108,1 | 224,9 | 198,0 | 132,4 |

Pintura:

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Carga Parrilla | 0,0 | 56,4 | 63,7 | 0,0 | 76,0 | 58,8 |
| Carga Brasero | 42,8 | 0,0 | 38,8 | 51,0 | 0,0 | 55,1 |
| Plan de capacidad | 42,8 | 56,4 | 102,5 | 51,0 | 76,0 | 113,9 |
| Capacidad disponible | 80,0 | 80,0 | 80,0 | 80,0 | 40,0 | 40,0 |
| Desviación | 37,2 | 23,6 | −22,5 | 29,0 | −36,0 | −73,9 |
| Desv. acumulada | 37,2 | 60,8 | 38,4 | 67,4 | 31,4 | −42,5 |

**Cómo se lee.**

- **Corte y soldadura** tienen semanas sobrecargadas, pero la acumulada nunca baja de cero: sobra
  capacidad en las semanas anteriores. Se arregla adelantando trabajo; por ejemplo, cortar en las
  semanas 1 y 2 rejillas y piezas de brasero de la semana 3. Ojo: adelantar exige que el material
  llegue antes (el MRP de la unidad 8 debe reflejarlo).
- **Pintura** es el problema real. Hasta la semana 5 la holgura acumulada alcanza, pero en la
  semana 6 la acumulada llega a −42,5 h: aunque se adelante todo lo posible, faltan unas 43 horas.
  La causa son las vacaciones. Opciones: horas extra o un reemplazo en las semanas 5 y 6, pasar las
  vacaciones a la semana 4 (que tiene 29 h de holgura) o mover braseros de la semana 6 a la 7.
- El MPS **no** se aprueba tal cual: se aprueba con la decisión sobre pintura tomada.

---

## 7. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Recorrer el aprovechamiento desde la primera operación | Se parte de la **última** (bruto = 1) y se sube: $N = B / a$ |
| Multiplicar por el aprovechamiento en vez de dividir | Lo que entra es **más** que lo que sale: $N > B$ siempre |
| Cargar con el bruto en vez del neto | La operación trabaja también las unidades que se pierden: carga $= N \cdot t$ |
| Partir el componente desde 1 o desde $q$ | El componente parte de $q \cdot N$ de la operación del padre que lo consume |
| Leer solo la desviación de la semana | Mira la acumulada: dice si la sobrecarga es de calendario o real |
| Usar holgura de semanas **posteriores** | La capacidad no viaja hacia atrás; solo se adelanta trabajo |
| Desviación con el signo al revés | Desviación = capacidad − carga: negativa es sobrecarga |

---

## 8. Práctica

Diez ejercicios: 9.1 a 9.4 básicos, 9.5 a 9.8 intermedios, 9.9 y 9.10 de desafío. Las pautas están
en la sección 9. Trabaja con tres decimales en las listas de capacidad y uno en las horas.

**9.1 · Tazas de cerámica (básico).** Un taller de Pomaire hace tazas con cuatro operaciones en
serie: moldeado ($a = 0{,}93$), primera cocción ($a = 0{,}89$), esmaltado ($a = 0{,}96$) y segunda
cocción ($a = 0{,}97$). Le encargan 1.200 tazas buenas. (a) ¿Cuántas piezas deben entrar a cada
operación? (b) ¿Cuál es el aprovechamiento total del proceso? (c) ¿Qué operación conviene mejorar
primero?

**9.2 · Capacidad disponible (básico).** (a) Un centro de costura tiene 7 operarias que trabajan
8,5 h diarias, 5 días a la semana. ¿Cuál es su capacidad estándar semanal? (b) Un centro de
inyección de plástico tiene 3 máquinas, 2 turnos de 8 h y trabaja 6 días. La utilización es 0,91 y
la eficiencia 0,87. Calcula su capacidad de diseño y su capacidad efectiva semanales.

**9.3 · Tabla de picar (básico).** Una carpintería de Valdivia hace tablas de picar con tres
operaciones: corte ($t = 0{,}05$ h, $a = 0{,}97$), cepillado ($t = 0{,}07$ h, $a = 0{,}96$) y lijado
y aceite ($t = 0{,}09$ h, $a = 0{,}99$), cada una en su propio centro. Arma la lista de capacidad: horas
por tabla buena en cada centro y en total.

**9.4 · Un centro, seis semanas (básico).** Un centro de 4 personas carga 0,62 h por unidad del
único producto que procesa. Arma el plan de capacidad y explica qué pasa en las semanas 1 y 3.

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| MPS | 310 | 0 | 420 | 280 | 0 | 390 |

**9.5 · Velador con dos cajones (intermedio).** Una mueblería de Chillán hace veladores. Cada
velador lleva 2 cajones, que consume la operación O1.

| Ítem | Operación | Centro | $t_i$ (h/u) | $a_i$ |
|---|---|---|---|---|
| Velador | O1 | Armado | 0,35 | 0,97 |
| | O2 | Barnizado | 0,28 | 0,96 |
| Cajón (2 por velador) | O3 | Corte | 0,06 | 0,93 |
| | O4 | Armado | 0,09 | 0,98 |

Calcula los requerimientos bruto y neto de cada operación y la lista de capacidad del velador.

**9.6 · Dos productos, dos centros (intermedio).** Con la lista de capacidad de abajo (h por
unidad), arma el plan de los dos centros. CT-A tiene 3 personas y CT-B, 2. ¿Qué centro tiene un
problema de calendario y cuál uno real? ¿Desde qué semana?

| | CT-A | CT-B |
|---|---|---|
| Producto X | 0,45 | 0,20 |
| Producto Y | 0,30 | 0,55 |

| Sem. | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| MPS X | 200 | 0 | 260 | 0 | 240 |
| MPS Y | 0 | 170 | 140 | 210 | 0 |

**9.7 · Lista de capacidad frente a perfil de recursos (intermedio).** El producto Z lleva un
componente W que se fabrica en CT1 **una semana antes** que Z. W deja 0,35 h de CT1 por cada Z. CT1
tiene 2 personas. Arma el plan de CT1 con lista de capacidad (todo en la semana del MPS) y con perfil
de recursos (la carga de W una semana antes). ¿Cambia el diagnóstico?

| Sem. | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| MPS Z | 0 | 240 | 0 | 300 | 260 |

**9.8 · Horas extra o subcontrato (intermedio).** Un centro de 5 personas tiene la carga de abajo.
Las horas extra cuestan $9.000 la hora y no pueden pasar del 20 % de la capacidad regular en una
semana; el subcontrato cuesta $14.000 la hora, sin tope. Sin mover trabajo de una semana a otra,
¿cuántas horas extra y cuántas subcontratadas necesitas cada semana, y cuánto cuesta?

| Sem. | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Carga (h) | 210 | 260 | 190 | 280 |

**9.9 · Adelantar con horas extra (desafío).** Mismo centro de 9.8, pero ahora el producto se
puede fabricar antes y guardarse sin costo relevante. Las horas extra de una semana pueden usarse
para adelantar trabajo de semanas posteriores. ¿Cuál es el plan más barato? ¿Cuánto se ahorra
frente a 9.8? ¿Qué condición de la unidad 8 tiene que cumplirse para que esto funcione?

**9.10 · Embotelladora de aceite de oliva (desafío).** Una embotelladora del valle del Huasco tiene
tres operaciones en serie, cada una en su centro: llenado ($t = 0{,}010$ h por botella,
$a = 0{,}91$), taponado ($t = 0{,}004$, $a = 0{,}98$) y etiquetado ($t = 0{,}006$, $a = 0{,}99$). El
centro de llenado tiene 4 personas. En la semana peak el MPS pide 14.600 botellas. (a) ¿Cuántas
botellas entran al llenado y cuántas horas carga? ¿Cuánto falta? (b) ¿Qué aprovechamiento mínimo
necesitaría el llenado para que la semana quepa sin horas extra? (c) ¿Se podría lograr mejorando
solo el etiquetado? (d) ¿Qué recomiendas?

---

## 9. Pautas

**9.1.** Hacia atrás desde 1.200 buenas: entran 1.237,1 a la segunda cocción, 1.288,7 al
esmaltado, 1.447,9 a la primera cocción y 1.556,9 al moldeado (en la práctica, 1.557 piezas).
Aprovechamiento total: $0{,}93 \cdot 0{,}89 \cdot 0{,}96 \cdot 0{,}97 =$ 0,7708; casi una de cada
cuatro piezas moldeadas se pierde. Conviene mejorar primero la primera cocción, la de menor
aprovechamiento: ahí se pierden 159 piezas, más que en cualquier otra.

**9.2.** (a) $7 \times 8{,}5 \times 5 =$ 297,5 h. (b) Diseño: $3 \times 8 \times 2 \times 6 =$
288,0 h. Efectiva: $288 \times 0{,}91 \times 0{,}87 =$ 228,0 h.

**9.3.**

| Op. | Centro | Bruto | Neto | Carga (h) |
|---|---|---|---|---|
| O3 | Lijado y aceite | 1,000 | 1,010 | 0,091 |
| O2 | Cepillado | 1,010 | 1,052 | 0,074 |
| O1 | Corte | 1,052 | 1,085 | 0,054 |

Total: 0,219 h por tabla buena. El lijado es el que más carga, aunque tenga el mejor
aprovechamiento: manda el tiempo.

**9.4.** Capacidad: $4 \times 40 = 160$ h.

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Carga | 192,2 | 0,0 | 260,4 | 173,6 | 0,0 | 241,8 |
| Plan de capacidad | 192,2 | 0,0 | 260,4 | 173,6 | 0,0 | 241,8 |
| Capacidad disponible | 160,0 | 160,0 | 160,0 | 160,0 | 160,0 | 160,0 |
| Desviación | −32,2 | 160,0 | −100,4 | −13,6 | 160,0 | −81,8 |
| Desv. acumulada | −32,2 | 127,8 | 27,4 | 13,8 | 173,8 | 92,0 |

La semana 1 es un faltante real: no hay semanas anteriores con holgura, así que hacen falta 32,2 h
extra (o mover parte del lote a la semana 2). La semana 3 se sobrecarga en 100,4 h, pero la
acumulada sigue positiva: se arregla adelantando trabajo a la semana 2, que está vacía. Lo mismo
pasa con las semanas 4 y 6.

**9.5.**

| Ítem | Op. | Centro | Bruto | Neto | Carga (h) |
|---|---|---|---|---|---|
| Velador | O2 | Barnizado | 1,000 | 1,042 | 0,292 |
| | O1 | Armado | 1,042 | 1,074 | 0,376 |
| Cajón | O4 | Armado | 2,148 | 2,192 | 0,197 |
| | O3 | Corte | 2,192 | 2,357 | 0,141 |

Lista de capacidad del velador: corte 0,141 h, armado $0{,}376 + 0{,}197 =$ 0,573 h y barnizado
0,292 h; en total 1,006 h por velador.

**9.6.** CT-A tiene 120 h y CT-B, 80 h.

CT-A:

| Sem. | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Carga X | 90,0 | 0,0 | 117,0 | 0,0 | 108,0 |
| Carga Y | 0,0 | 51,0 | 42,0 | 63,0 | 0,0 |
| Plan de capacidad | 90,0 | 51,0 | 159,0 | 63,0 | 108,0 |
| Capacidad disponible | 120,0 | 120,0 | 120,0 | 120,0 | 120,0 |
| Desviación | 30,0 | 69,0 | −39,0 | 57,0 | 12,0 |
| Desv. acumulada | 30,0 | 99,0 | 60,0 | 117,0 | 129,0 |

CT-B:

| Sem. | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Carga X | 40,0 | 0,0 | 52,0 | 0,0 | 48,0 |
| Carga Y | 0,0 | 93,5 | 77,0 | 115,5 | 0,0 |
| Plan de capacidad | 40,0 | 93,5 | 129,0 | 115,5 | 48,0 |
| Capacidad disponible | 80,0 | 80,0 | 80,0 | 80,0 | 80,0 |
| Desviación | 40,0 | −13,5 | −49,0 | −35,5 | 32,0 |
| Desv. acumulada | 40,0 | 26,5 | −22,5 | −58,0 | −26,0 |

CT-A solo tiene un problema de calendario en la semana 3 (se adelanta trabajo a las semanas 1 y 2).
CT-B tiene un faltante real desde la semana 3, que llega a 58 h en la semana 4. La holgura de la
semana 5 no sirve para atrás. CT-B es el cuello de botella de este MPS: el producto Y, que carga
0,55 h ahí, es el que hay que mover o cubrir con horas extra.

**9.7.** Capacidad de CT1: 80 h. Con lista de capacidad:

| Sem. | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Plan de capacidad | 0,0 | 84,0 | 0,0 | 105,0 | 91,0 |
| Capacidad disponible | 80,0 | 80,0 | 80,0 | 80,0 | 80,0 |
| Desviación | 80,0 | −4,0 | 80,0 | −25,0 | −11,0 |
| Desv. acumulada | 80,0 | 76,0 | 156,0 | 131,0 | 120,0 |

Con perfil de recursos (la carga de W una semana antes):

| Sem. | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Plan de capacidad | 84,0 | 0,0 | 105,0 | 91,0 | 0,0 |
| Capacidad disponible | 80,0 | 80,0 | 80,0 | 80,0 | 80,0 |
| Desviación | −4,0 | 80,0 | −25,0 | −11,0 | 80,0 |
| Desv. acumulada | −4,0 | 76,0 | 51,0 | 40,0 | 120,0 |

Sí cambia. La lista de capacidad decía que todo se arreglaba adelantando trabajo. El perfil
muestra que la carga de W ocurre en la semana 1, sin holgura previa: faltan 4 h reales esa semana.
Son pocas, pero un plan aprobado con la lista habría prometido algo que el taller no puede cumplir.

**9.8.** Capacidad regular: 200 h; tope de horas extra: 40 h por semana.

| Sem. | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Plan de capacidad | 210,0 | 260,0 | 190,0 | 280,0 |
| Capacidad disponible | 200,0 | 200,0 | 200,0 | 200,0 |
| Desviación | −10,0 | −60,0 | 10,0 | −80,0 |
| Desv. acumulada | −10,0 | −70,0 | −60,0 | −140,0 |

Horas extra: 10, 40, 0 y 40 (90 h, $810.000). Subcontrato: 0, 20, 0 y 40 (60 h, $840.000). Total:
**$1.650.000**. Las 10 h libres de la semana 3 se pierden.

**9.9.** La acumulada final es −140: hacen falta al menos 140 horas adicionales en el horizonte.
Si todas pueden ser horas extra, el costo mínimo es $140 \times 9.000$, es decir, **$1.260.000**. Se
puede, porque el tope semanal deja hacerlo a tiempo. Un plan que lo logra:

| Sem. | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Horas extra | 30 | 40 | 30 | 40 |
| Uso | 10 propias + 20 de la sem. 2 | 40 propias | 10 de holgura + 30 extra = 40 de la sem. 4 | 40 propias |

No es el único plan con ese costo (por ejemplo, 30, 40, 40 y 30 también sirve). El ahorro frente a
9.8 es de **$390.000**: se dejan de subcontratar 60 h y se aprovechan las 10 h libres de la semana 3.
La condición: para fabricar antes, el material tiene que llegar antes. El MRP (unidad 8) debe
adelantar las liberaciones de los componentes, y si un proveedor no puede, el plan no sirve.

**9.10.** (a) Entran 14.600 / (0,91 · 0,98 · 0,99) = 16.537 botellas al llenado, que
cargan 165,4 h. La capacidad es $4 \times 40 = 160$ h: faltan 5,4 h. (b) Hay que despejar $a_1$ en
$0{,}010 \cdot 14.600 / (a_1 \cdot 0{,}98 \cdot 0{,}99) \le 160$: $a_1 \ge$ 0,941, es decir, subir el
llenado de 91 % a 94,1 % de aprovechamiento. (c) Con el etiquetado haría falta $a_3 \ge$ 1,023:
imposible. El etiquetado ya pierde muy poco, así que mejorarlo casi no libera llenado. (d) Una
merma cobra capacidad en su operación y en todas las anteriores. Aquí la merma grande está en el
mismo llenado (9 %). Subirlo a 94 % es plausible (revisar derrames y ajuste de boquillas), pero
para esta semana lo seguro son unas 5,4 h extra; la mejora del aprovechamiento resuelve las
semanas siguientes y además ahorra aceite.

---

## 10. Caso integrador · Estampa Sur, ¿alcanza el taller?

> Este caso sigue a Estampa Sur por todo el ramo. Acá se usa el programa maestro de los cinco
> productos (unidad 7) y la capacidad efectiva del estampado (unidad 3). Si no has hecho esas
> unidades, parte de estas tablas.

Estampa Sur tiene dos centros: **estampado** (capacidad efectiva de 40 h por semana, unidad 3) y
**planchado y doblado** (una persona media jornada: 18 h por semana). Las prendas falladas se
reestampan fuera del plan, así que el aprovechamiento se toma como 1, y las prendas lisas se
compran: la lista de capacidad sale directo de los segundos por unidad.

| Producto | Lote | Estampado (s/u) | Planchado (s/u) | Estampado por lote | Planchado por lote |
|---|---|---|---|---|---|
| Poleras básicas | 720 | 30 | 20 | 6 h | 4 h |
| Polerones | 360 | 90 | 50 | 9 h | 5 h |
| Poleras estampado doble | 360 | 110 | 30 | 11 h | 3 h |
| Bolsas | 540 | 20 | 40 | 3 h | 6 h |
| Gorros | 480 | 30 | 15 | 4 h | 2 h |

El MPS (unidades por semana, unidad 7):

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Poleras básicas | 0 | 720 | 720 | 0 | 720 | 720 | 720 | 720 |
| Polerones | 360 | 0 | 360 | 0 | 360 | 360 | 0 | 360 |
| Est. doble | 0 | 360 | 0 | 360 | 0 | 360 | 360 | 0 |
| Bolsas | 0 | 540 | 0 | 540 | 0 | 540 | 0 | 540 |
| Gorros | 0 | 0 | 0 | 480 | 0 | 480 | 0 | 0 |

**Pregunta.** Arma el plan aproximado de capacidad de los dos centros. ¿Qué semana no cabe, en qué
centro, y qué propones?

**Desarrollo.** Estampado (h):

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Plan de capacidad | 9 | 20 | 15 | 18 | 15 | 33 | 17 | 18 |
| Capacidad disponible | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 |
| Desviación | 31 | 20 | 25 | 22 | 25 | 7 | 23 | 22 |
| Desv. acumulada | 31 | 51 | 76 | 98 | 123 | 130 | 153 | 175 |

Planchado y doblado (h):

| Sem. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Plan de capacidad | 5 | 13 | 9 | 11 | 9 | 20 | 7 | 15 |
| Capacidad disponible | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 |
| Desviación | 13 | 5 | 9 | 7 | 9 | −2 | 11 | 3 |
| Desv. acumulada | 13 | 18 | 27 | 34 | 43 | 41 | 52 | 55 |

En la semana 6 coinciden los cinco productos: el estampado carga 33 h (cabe) y el planchado 20 h,
2 más de las que tiene. La acumulada del planchado sigue en 41 h: es un problema **de calendario**,
no de capacidad total.

**Propuestas para la semana 6.**

| Opción | Semana 5 (est. · planch.) | Semana 6 (est. · planch.) | Comentario |
|---|---|---|---|
| A · 2 h extra de planchado | 15 h · 9 h | 33 h · 20 h | no cambia el plan; cuesta 2 h extra |
| B · adelantar los gorros | 19 h · 11 h | 29 h · 18 h | cabe justo, sin margen para una falla |
| C · adelantar las bolsas | 18 h · 15 h | 30 h · 14 h | deja 4 h de holgura en el planchado |

**Lectura.**

- La opción A es la más simple: dos horas extra en una semana no le cambian nada a nadie, y es la
  que asume la unidad 10, que programa las cinco órdenes de la semana 6 con sus 20 h de planchado.
- La opción C es la más robusta si no hay horas extra: la semana 5 tiene 9 h libres en planchado y
  las bolsas son el producto que más carga ese centro. El costo: las 540 bolsas se guardan una
  semana más, y las bolsas lisas y su tinta deben llegar una semana antes (habría que revisar su
  MRP).
- La opción B resuelve la cuenta pero deja el planchado al 100 %: cualquier atraso se traslada a
  la semana 7.
- El estampado nunca es el cuello de botella en estas ocho semanas: su peor semana usa 33 de 40 h.
  El centro que limita es el planchado, aunque tenga menos horas de trabajo, porque tiene muchas
  menos horas disponibles.

**Lo que pasa a la unidad 10.** La semana 6 se programa tal como está (opción A): cinco órdenes que
pasan por estampado y después por planchado.

---

## 11. Para seguir

**En los libros del ramo.**

- Schroeder, *Administración de operaciones* (2.ª ed., 2004), capítulos 12, 13 y 16 (los que fija el
  programa para planificación y control de la producción).
- Chase, Jacobs y Aquilano, *Administración de operaciones* (12.ª ed., 2009), en el tema de
  planeación de requerimiento de materiales, la parte de planificación de la capacidad.
- Heizer y Render, *Principios de administración de operaciones* (5.ª ed., 2004), en el tema de
  MRP, la planificación de capacidad que acompaña al programa maestro.

**Abiertos y gratis.**

- Abbas y Goosheh, *Operations Management*, Fanshawe College (2025), en inglés. Busca en su índice
  la planificación de la capacidad. Descarga en la colección abierta de Ontario:
  https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/2473

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un producto con un componente y tres
operaciones con aprovechamiento, y corrígeme la lista de capacidad paso a paso».
