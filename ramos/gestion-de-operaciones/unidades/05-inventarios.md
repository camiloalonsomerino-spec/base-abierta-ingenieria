---
ramo: Gestión de Operaciones
unidad: 5
titulo: Inventarios
version: 0.1 (15-10-2026)
requiere: [04-pronosticos]
alimenta: [08-mrp]
verificacion: verificacion/u05_inventarios.py
---

# Unidad 5 · Inventarios

**Qué vas a poder hacer.** Explicar para qué sirve un inventario y cuánto cuesta tenerlo; calcular
cuánto pedir con el lote económico (EOQ) y decidir si conviene un descuento por cantidad; fijar
cuándo pedir con el punto de reorden y un stock de seguridad ligado a un nivel de servicio; medir
cuánto pesan la variabilidad de la demanda y la del plazo; elegir entre las políticas (Q, r),
(R, S) y (s, S), y resolver la compra de una sola vez con el modelo del vendedor de diarios
(newsvendor).

**Lo que necesitas antes.** Un pronóstico de demanda (unidad 4) y la distribución normal: qué es $z$, cómo se lee $\Phi(z)$ y que la varianza de una suma de variables
independientes es la suma de las varianzas.

**Tiempo.** Unas 4,5 horas: 2 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. La función económica del inventario

Un inventario es plata detenida en forma de cosas. Se acepta tenerla quieta porque cumple funciones
que de otro modo costarían más:

| Función | Qué resuelve |
|---|---|
| Desacoplar | Que una etapa no tenga que esperar a la anterior (la máquina 2 trabaja aunque la 1 pare) |
| Economía de escala | Pedir pocas veces en lotes grandes, porque cada pedido tiene un costo fijo |
| Protección | Cubrir la demanda o el plazo que salen distintos de lo esperado (stock de seguridad) |
| Anticipación | Fabricar antes de un peak de temporada que la capacidad no alcanza a cubrir |
| Tránsito | Lo que ya se compró y viene en camino |

**Demanda independiente o dependiente.** La demanda de un producto terminado depende del mercado y
se pronostica: es **independiente**, y es la que trata esta unidad. La demanda de sus componentes se
calcula desde el plan de producción (cada polera estampada usa una polera lisa): es **dependiente** y
la resuelve el MRP (unidad 8).

**Los cuatro costos.**

| Costo | Símbolo | Qué incluye | Cómo se mueve con el lote $Q$ |
|---|---|---|---|
| Compra | $C$ por unidad | el precio | fijo por unidad, salvo descuentos |
| Pedir (o preparar) | $S$ por pedido | emitir la orden, transporte, recepción; en fábrica, el cambio de máquina | baja: con lotes grandes se pide menos veces |
| Mantener | $H = i \cdot C$ por unidad y año | costo del capital, bodega, seguros, mermas, obsolescencia | sube: con lotes grandes hay más stock promedio |
| Faltante | por unidad o por quiebre | venta perdida, cliente molesto, faena detenida | baja con más stock de seguridad |

La tasa $i$ es un porcentaje anual del valor. El componente más grande suele ser el costo del capital:
una polera en bodega es plata que no está pagando deudas ni ganando intereses.

---

## 2. Cuánto pedir · el lote económico (EOQ)

### Supuestos

Demanda conocida y constante ($D$ unidades al año, $d$ por día); $S$ y $H$ constantes; el pedido
llega completo y de una vez; plazo conocido; sin faltantes y sin descuentos. El inventario dibuja un
**diente de sierra**: sube de golpe a $Q$ cuando llega el pedido y baja en línea recta hasta cero.
El inventario promedio es $Q/2$.

### El costo total y su mínimo

$$CT(Q) = \underbrace{D \cdot C}_{\text{compra}} + \underbrace{\frac{D}{Q}\, S}_{\text{pedir}} + \underbrace{\frac{Q}{2}\, H}_{\text{mantener}}$$

Derivando e igualando a cero (la compra no depende de $Q$):

$$Q^* = \sqrt{\frac{2\,D\,S}{H}} \qquad N = \frac{D}{Q^*} \qquad T = \frac{\text{días hábiles}}{N} \qquad CT_{\text{inv}}(Q^*) = \sqrt{2\,D\,S\,H}$$

En el óptimo, **el costo de pedir es igual al de mantener**. Si en tus cuentas no te da igual, hay un
error.

### Dos propiedades que se preguntan

**La curva es plana cerca del óptimo.** Si pides $Q$ en vez de $Q^*$, el costo de pedir más mantener
crece en la razón

$$\frac{CT_{\text{inv}}(Q)}{CT_{\text{inv}}(Q^*)} = \frac{1}{2}\left(\frac{Q}{Q^*} + \frac{Q^*}{Q}\right)$$

Pedir un 50 % más que el óptimo multiplica ese costo por 1,083: sube apenas un 8,3 %. Por eso se
puede redondear $Q^*$ a un pallet, una caja o un camión sin culpa.

**$Q^*$ crece con la raíz de la demanda.** Si la demanda baja un 20 %, el lote baja en un factor
$\sqrt{0{,}8}$: el lote nuevo es un 10,6 % menor, no un 20 %.

> **Unidades.** $D$, $S$ y $H$ tienen que hablar de la misma unidad (unidades o cajas) y del mismo
> período (año o mes). Si el proveedor vende por caja de 12 y la demanda viene en unidades, convierte
> antes de la raíz.

---

## 3. Descuentos por cantidad

El proveedor baja el precio si el pedido supera un mínimo. En el esquema más común el precio rebajado
vale para **todas las unidades** del pedido. Como $H = i \cdot C$, cada tramo tiene su propio EOQ.

1. Para cada tramo, calcula $Q^*$ con su precio.
2. Si $Q^*$ cae dentro del tramo, es candidato. Si cae **bajo** el mínimo, el candidato es el mínimo
   del tramo. Si cae **sobre** el tramo, ese precio no se usa con ese $Q^*$.
3. Calcula el **costo total con la compra incluida** para cada candidato.
4. Elige el menor.

La compra pesa aquí porque cambia de un tramo a otro. Sin ella, el descuento nunca se vería.

---

## 4. Cuándo pedir · el punto de reorden

Con plazo de entrega $L$ (en días) y demanda diaria constante $d$, se pide cuando lo que queda alcanza
justo para cubrir el plazo:

$$r = d \cdot L$$

**Posición de inventario.** Se compara $r$ con la posición, no con lo que hay en la bodega:

$$\text{posición} = \text{físico} + \text{en camino} - \text{comprometido}$$

Si $Q$ es menor que $d \cdot L$, siempre hay al menos un pedido en camino; mirar solo el físico
dispararía pedidos repetidos.

**Stock de seguridad por plazo máximo.** La forma más simple: si el proveedor a veces se atrasa
hasta $L_{\max}$ días, se guarda lo que se vende en esos días extra.

$$SS = (L_{\max} - L) \cdot d \qquad r = d \cdot L + SS$$

---

## 5. Nivel de servicio y stock de seguridad

Cuando la demanda diaria varía (media $d$, desviación $\sigma_d$), la demanda durante el plazo es
aleatoria. Si los días son independientes, su desviación crece con la **raíz** del plazo:

$$\sigma_L = \sigma_d \sqrt{L} \qquad SS = z \cdot \sigma_L \qquad r = d \cdot L + z\,\sigma_L$$

El **nivel de servicio por ciclo** es la probabilidad de no quedarse sin stock mientras se espera un
pedido: $NS = \Phi(z)$. Los valores que más se usan:

| Nivel de servicio | 90 % | 95 % | 97 % | 99 % |
|---|---|---|---|---|
| $z$ | 1,282 | 1,645 | 1,881 | 2,326 |

**Si el plazo también varía** (media $L$, desviación $\sigma_{LT}$ en días):

$$\sigma = \sqrt{L\,\sigma_d^2 + d^2\,\sigma_{LT}^2}$$

El segundo término suele dominar: un día de atraso del proveedor equivale a un día entero de demanda
($d$), mientras que la variabilidad diaria se diluye con la raíz.

**Tasa de servicio (unidades atendidas).** El nivel por ciclo no dice cuántas unidades faltan. Las
unidades faltantes esperadas en cada ciclo son $\sigma_L \cdot \mathcal{L}(z)$, con la función de
pérdida normal $\mathcal{L}(z) = \varphi(z) - z\,[1 - \Phi(z)]$. Como hay $D/Q$ ciclos al año:

$$\text{tasa de servicio} = 1 - \frac{\sigma_L\,\mathcal{L}(z)}{Q}$$

Con lotes grandes se pide pocas veces y cada quiebre es chico, así que un 90 % por ciclo puede ser un
99 % en unidades (ejercicio 5.10).

> **Lo que mueve el stock de seguridad.** Crece **lineal** con $\sigma_d$, con la **raíz** de $L$ y
> cada vez más rápido con $z$ cerca del 100 %. Reducir la variabilidad o el plazo suele salir más
> barato que comprar seguridad con más stock.

---

## 6. Ejemplo resuelto · cemento en una ferretería

Una ferretería de San Carlos vende sacos de cemento de 25 kg. Los datos:

| Dato | Valor |
|---|---|
| Demanda anual $D$ | 10.080 sacos |
| Días hábiles al año | 288 (seis días por semana, 48 semanas) |
| Costo por pedido $S$ | \$36.000 (flete del camión y recepción) |
| Precio $C$ | \$5.200 por saco |
| Tasa de mantener $i$ | 18 % anual |
| Plazo $L$ | 3 días hábiles |
| Desviación de la demanda diaria $\sigma_d$ | 9 sacos |
| Nivel de servicio pedido | 95 % |

**Paso 1 · Demanda diaria y costo de mantener.**
$d = 10.080 / 288 = 35$ sacos por día · $H = 0{,}18 \times 5.200 = 936$ pesos por saco y año.

**Paso 2 · Lote económico.**

$$Q^* = \sqrt{\frac{2 \times 10.080 \times 36.000}{936}} = 880{,}6 \text{ sacos}$$

Pedidos al año: $N = 10.080 / 880{,}6 = 11{,}45$. Tiempo entre pedidos: $T = 288 / 11{,}45 = 25{,}2$
días hábiles.

**Paso 3 · Costos.** Se redondea a **880 sacos** (22 pallets de 40).

| Lote | Pedir | Mantener | Pedir + mantener | Compra | Total |
|---|---|---|---|---|---|
| $Q^*$ = 880,6 | \$412.102 | \$412.102 | \$824.203 | \$52.416.000 | \$53.240.203 |
| 880 | \$412.364 | \$411.840 | \$824.204 | \$52.416.000 | \$53.240.204 |

Redondear costó un peso. La curva plana de la sección 2, en vivo.

**Paso 4 · El proveedor ofrece 3 % desde 1.800 sacos.** El precio baja a \$5.044 y $H$ a 907,92. El
EOQ con ese precio da 894,1 sacos, bajo el mínimo: el candidato es **1.800**.

| Lote | Pedir | Mantener | Compra | Total |
|---|---|---|---|---|
| 880 a \$5.200 | \$412.364 | \$411.840 | \$52.416.000 | \$53.240.204 |
| 1.800 a \$5.044 | \$201.600 | \$817.128 | \$50.843.520 | **\$51.862.248** |

El descuento ahorra **\$1.377.956** al año: la compra baja \$1.572.480 y pedir más mantener sube
\$194.524. El costo escondido es otro: 1.800 sacos cubren 51,4 días de venta. Conviene solo si la
bodega es seca y techada (el cemento se endurece con la humedad) y si la ferretería tiene caja para
pagar el doble de mercadería por pedido.

**Paso 5 · Punto de reorden con nivel de servicio.** $z = 1{,}645$ para el 95 %.

$$\sigma_L = 9\sqrt{3} = 15{,}59 \qquad SS = 1{,}645 \times 15{,}59 = 25{,}6 \qquad r = 35 \times 3 + 25{,}6 = 130{,}6$$

La demanda esperada en el plazo es de 105 sacos; con la seguridad, el punto de reorden es 130,6, y
se redondea hacia arriba: **131 sacos**. Se redondea hacia arriba porque hacia abajo el servicio
quedaría bajo el 95 %.

**Paso 6 · Y si el camión se atrasa.** Si el plazo varía con una desviación de 1 día:

$$\sigma = \sqrt{3 \times 9^2 + 35^2 \times 1^2} = 38{,}31 \qquad SS = 63{,}0 \qquad r = 168{,}0$$

Un día de incertidumbre en el flete casi multiplica por 2,5 el stock de seguridad. Antes de comprar
esa seguridad, conviene negociar un día fijo de despacho.

**La política.** Con el descuento: **(Q, r) = (1.800, 131)**. Cada vez que la posición de
inventario baja de 131 sacos se piden 1.800.

---

## 7. Políticas de inventario

| Política | Cuándo se pide | Cuánto se pide | Conviene cuando |
|---|---|---|---|
| **(Q, r)** revisión continua | cuando la posición llega a $r$ | siempre $Q$ (el EOQ) | hay registro en línea (código de barras, ERP) y el lote importa |
| **(R, S)** revisión periódica | cada $R$ días, en fecha fija | lo que falta para llegar a $S$ | el proveedor pasa en días fijos o se piden muchos artículos juntos |
| **(s, S)** mixta | en la revisión, solo si la posición es $\le s$ | lo que falta para llegar a $S$ | pedir tiene un costo fijo alto y no vale la pena pedir poco |

**Revisión periódica.** Entre una revisión y la llegada del pedido siguiente pasan $R + L$ días, así
que el nivel máximo $S$ (también llamado nivel objetivo) tiene que cubrir ese tramo completo:

$$S = d\,(R + L) + z\,\sigma_d\sqrt{R + L} \qquad \text{pedido} = S - \text{posición}$$

La revisión periódica necesita **más** stock de seguridad que la continua, porque protege $R + L$ días
y no solo $L$. A cambio, no exige mirar el inventario todo el tiempo.

**(s, S).** Cuando $s$ está cerca de $S$, se pide en casi todas las revisiones y se parece a la periódica; cuando $S - s$ es grande, se parece a pedir
un lote fijo. El punto $s$ cumple el papel de $r$: tiene que cubrir la demanda del plazo **más** la del
período de revisión.

---

## 8. Compra de una sola vez · el vendedor de diarios

Hay productos que se compran una vez y lo que sobra vale poco: diarios, flores para una fecha,
productos de temporada, poleras de un evento. Ya no hay ciclos que repetir; la pregunta es cuánto
comprar para **una** venta incierta.

- **Costo de quedarse corto** $C_u = p - c$: lo que se deja de ganar por cada unidad que faltó.
- **Costo de pasarse** $C_o = c - v$: lo que se pierde por cada unidad que sobró ($v$ es lo que se
  recupera al liquidarla).

Se compra hasta que la probabilidad de vender la última unidad iguala la **razón crítica**:

$$RC = \frac{C_u}{C_u + C_o} \qquad F(Q^*) = RC \qquad \text{con demanda normal: } Q^* = \mu + z\,\sigma,\ z = \Phi^{-1}(RC)$$

Con demanda discreta (una tabla de probabilidades), $Q^*$ es la **menor** cantidad cuya probabilidad
acumulada llega a la razón crítica.

**Ejemplo breve · pinos de Navidad.** Un vivero de Chillán compra pinos a \$9.000 y los vende a
\$22.000; lo que sobra se vende para leña a \$1.500. La demanda es normal con media 420 y desviación 70.
$C_u = 13.000$, $C_o = 7.500$, $RC = 0{,}634$, $z = 0{,}343$, $Q^* = 420 + 0{,}343 \times 70 = 444{,}0$:
se compran **444 pinos**. Como quedarse corto duele más que pasarse ($RC$ mayor que 0,5), se compra
sobre la media.

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Mezclar unidades: demanda en unidades y costo por caja, o $D$ anual con $H$ mensual | Escribe la unidad al lado de cada dato antes de la raíz |
| Usar la tasa $i$ como si fuera $H$ | $H = i \cdot C$, en pesos por unidad y año |
| Calcular $\sigma_L = \sigma_d \cdot L$ | Las varianzas se suman: $\sigma_L = \sigma_d \sqrt{L}$ |
| Comparar el punto de reorden con el stock físico | Se compara con la posición: físico más lo que viene en camino |
| En descuentos, comparar sin el costo de compra o sin subir al mínimo del tramo | Costo total completo y, si $Q^*$ cae bajo el tramo, el mínimo del tramo |
| En revisión periódica, cubrir solo el plazo | El nivel máximo cubre $R + L$ |
| En el newsvendor, comprar la media o invertir $C_u$ y $C_o$ | Primero la razón crítica; si es mayor que 0,5, se compra sobre la media |

---

## 10. Práctica

Diez ejercicios: 5.1 a 5.4 básicos, 5.5 a 5.8 intermedios, 5.9 y 5.10 de desafío. Las pautas están
en la sección 11. Intenta cada uno antes de mirarla.

**5.1 · Papel para una imprenta (básico).** Una imprenta de Talca usa 3.600 resmas al año y trabaja
245 días. Cada pedido cuesta \$18.000, la resma vale \$4.300 y mantener cuesta el 22 % anual del valor.
(a) Calcula el EOQ, los pedidos al año y los días entre pedidos. (b) Calcula el costo de pedir, el de
mantener y el total con la compra. (c) Si la demanda sube un 44 %, ¿cuál es el lote nuevo?

**5.2 · Punto de reorden con proveedor que se atrasa (básico).** Una distribuidora de Los Ángeles
vende 48 bidones de aceite por día. El proveedor tarda normalmente 7 días hábiles, pero a veces llega
a 11. (a) Calcula el punto de reorden sin stock de seguridad. (b) Calcula el stock de seguridad por
plazo máximo y el nuevo punto de reorden. (c) Si el lote es de 450 bidones, ¿qué problema aparece si
la bodega compara el punto de reorden con el stock físico?

**5.3 · Suero en un hospital (básico).** La farmacia de un hospital usa en promedio 64 bolsas de suero
por día, con desviación de 15 bolsas. El plazo es de 9 días y mantener una bolsa cuesta \$350 al año.
Calcula el stock de seguridad, el punto de reorden y el costo anual de la seguridad para niveles de
servicio de 90 %, 95 % y 99 %. ¿Cuánto más cuesta pasar de 90 % a 99 %?

**5.4 · Bufandas para la final (básico).** Un club de fútbol encarga bufandas para la final a \$6.500
cada una y las vende a \$15.000. Las que sobran se liquidan a \$2.000. La demanda es normal con media
600 y desviación 150. (a) ¿Cuántas encarga? (b) Si el proveedor acepta devoluciones pagando \$5.000
por bufanda, ¿cuántas encarga?

**5.5 · Aceite de oliva con descuento (intermedio).** Un hotel de Pucón usa 1.440 bidones de aceite
de oliva al año. Cada pedido cuesta \$24.000 y mantener cuesta el 30 % anual del precio. El proveedor
ofrece descuento a todas las unidades:

| Unidades por pedido | Precio por bidón |
|---|---|
| 1 a 499 | \$14.000 |
| 500 a 999 | \$13.650 |
| 1.000 o más | \$13.370 |

(a) ¿Cuánto pedir? (b) ¿Desde qué descuento en el segundo tramo convendría pedir 500?

**5.6 · Envases con plazo variable (intermedio).** Una planta de alimentos usa en promedio 140
envases por día (desviación 35). El proveedor tarda en promedio 8 días, con desviación de 2 días. La
planta quiere un 97 % de servicio. (a) Calcula el stock de seguridad y el punto de reorden si se
ignora la variación del plazo. (b) Repite incluyéndola. (c) Un proveedor local ofrece 3 días con
desviación de medio día: ¿cuánto queda el stock de seguridad?

**5.7 · Pañales con revisión semanal (intermedio).** Una farmacia de barrio de Talcahuano revisa los
pañales cada 7 días y el distribuidor entrega 3 días después. La demanda diaria es de 55 paquetes en
promedio, con desviación de 12. Quiere un 95 % de servicio. (a) Calcula el nivel máximo $S$. (b) Hoy
hay 240 paquetes en el estante y nada en camino: ¿cuánto pide? (c) ¿Cuánto stock de seguridad
necesitaría con revisión continua? (d) ¿Cuál sería $S$ si revisara cada 14 días?

**5.8 · Rosas para el Día de los Enamorados (intermedio).** Una florería arma ramos que le cuestan
\$7.000 y vende a \$18.000. Los que sobran se venden al día siguiente a \$1.000. La demanda estimada:

| Ramos | 100 | 150 | 200 | 250 | 300 |
|---|---|---|---|---|---|
| Probabilidad | 0,10 | 0,20 | 0,30 | 0,25 | 0,15 |

(a) ¿Cuántos ramos arma según la razón crítica? (b) Calcula la ganancia esperada de cada cantidad y
comprueba que la razón crítica eligió bien.

**5.9 · (s, S) contra (s, Q) en una bodega de repuestos (desafío).** Una bodega revisa un repuesto
cada viernes. Si la posición (físico más lo que viene en camino) es menor o igual que $s$, pide. Lo
pedido el viernes de la semana $t$ llega el lunes de la semana $t + 2$. La venta que no se puede
atender se pierde. Al inicio de la semana 1 hay 150 unidades y nada en camino. Costos: \$30.000 por
pedido, \$400 por unidad que queda al cierre de cada semana y \$5.000 por unidad faltante.

| Semana | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Demanda | 46 | 58 | 39 | 71 | 52 | 44 | 63 | 49 |

(a) Simula la política (s, S) con $s = 80$ y $S = 200$. (b) Simula (s, Q) con $s = 80$ y $Q = 120$.
(c) ¿Cuánto debería cubrir $s$? Simula (s, S) con $s = 110$ y $S = 200$ y compara las tres.

**5.10 · Fertilizante, camiones y servicio (desafío).** Una distribuidora de Linares vende 7.800 sacos
de fertilizante al año en 312 días hábiles. Pedir cuesta \$52.000, el saco vale \$11.500 y mantener
cuesta el 16 % anual. (a) Calcula el EOQ. (b) La fábrica solo despacha camiones completos de 500
sacos: ¿pide uno o dos camiones por vez, y cuánto más cuesta que el EOQ? (c) La demanda diaria tiene
desviación de 8 sacos y el plazo es de 10 días. Para niveles de servicio por ciclo de 90 %, 95 % y
99 %, calcula el stock de seguridad, el punto de reorden, su costo anual y la tasa de servicio en
unidades. ¿Qué nivel recomiendas?

---

## 11. Pautas

**5.1.** $H = 0{,}22 \times 4.300 = 946$ pesos. $Q^* = \sqrt{2 \times 3.600 \times 18.000 / 946} =$
**370,1 resmas**; $N = 9{,}73$ pedidos al año; $T = 245 / 9{,}73 = 25{,}2$ días. Pedir y mantener
cuestan lo mismo, \$175.073 cada uno (\$350.145 entre ambos); con la compra de \$15.480.000, el total es
**\$15.830.145**. Con 44 % más de demanda el lote se multiplica por $\sqrt{1{,}44} = 1{,}2$: **444,2
resmas**. Lectura: el inventario cuesta poco al lado de la compra; lo que se gana con el EOQ es orden,
no una fortuna.

**5.2.** (a) $r = 48 \times 7 =$ **336 bidones**. (b) $SS = (11 - 7) \times 48 =$ **192**;
$r = 336 + 192 =$ **528** (lo mismo que $48 \times 11$). (c) Con lotes de 450, menores que 528, cuando
se pide todavía queda un pedido anterior en camino: en promedio hay $336 / 450 = 0{,}75$ pedidos
viajando. Si se mira solo el físico, que casi siempre está bajo 528, se pediría cada día. La regla se
aplica a la posición: físico más lo que viene en camino.

**5.3.** $\sigma_L = 15\sqrt{9} = 45$ bolsas; demanda en el plazo $64 \times 9 = 576$.

| Nivel | $z$ | Stock de seguridad | Punto de reorden | Costo anual de la seguridad |
|---|---|---|---|---|
| 90 % | 1,282 | 57,7 | 633,7 | \$20.184 |
| 95 % | 1,645 | 74,0 | 650,0 | \$25.906 |
| 99 % | 2,326 | 104,7 | 680,7 | \$36.640 |

Pasar de 90 % a 99 % cuesta un 81,5 % más. En un hospital, quedarse sin suero no se mide en pesos: se
justifica el 99 %. En un artículo de bajo impacto, no.

**5.4.** (a) $C_u = 15.000 - 6.500 = 8.500$; $C_o = 6.500 - 2.000 = 4.500$; $RC = 0{,}654$;
$z = 0{,}396$; $Q^* = 600 + 0{,}396 \times 150 = 659{,}4$: **660 bufandas**. (b) Con devolución,
$C_o = 6.500 - 5.000 = 1.500$; $RC = 0{,}850$; $z = 1{,}036$; $Q^* = 755{,}5$: **756 bufandas**. Lectura:
abaratar el sobrante hace que convenga arriesgar más. Negociar la devolución vale casi 100 bufandas
más de venta posible.

**5.5.**

| Tramo | $H$ | EOQ del tramo | Lote candidato | Costo total |
|---|---|---|---|---|
| \$14.000 | \$4.200 | 128,3 | 128,3 | **\$20.698.799** |
| \$13.650 | \$4.095 | 129,9 | 500 (mínimo) | \$20.748.870 |
| \$13.370 | \$4.011 | 131,3 | 1.000 (mínimo) | \$21.292.860 |

(a) Conviene **no** tomar el descuento: pedir unos 128 bidones por vez. Con 30 % anual, guardar 500
bidones cuesta más de lo que ahorra el precio. (b) Pedir 500 empata con el primer tramo si el precio
baja a \$13.617 por bidón: un descuento de al menos **2,74 %** (el ofrecido es 2,5 %).

**5.6.** $z = 1{,}881$.

| Caso | Desviación en el plazo | Stock de seguridad | Punto de reorden |
|---|---|---|---|
| (a) plazo fijo de 8 días | 99,0 | 186,2 | 1.306,2 |
| (b) plazo de 8 ± 2 días | 297,0 | 558,6 | 1.678,6 |
| (c) proveedor local, 3 ± 0,5 días | 92,6 | 174,2 | 594,2 |

Ignorar la variación del plazo deja un tercio de la seguridad necesaria. El proveedor local baja el
stock de seguridad a menos de un tercio y el punto de reorden a poco más de un tercio: aunque cobre algo más,
puede salir a cuenta.

**5.7.** $z = 1{,}645$; $R + L = 10$ días. (a) $S = 55 \times 10 + 1{,}645 \times 12\sqrt{10} = 550 + 62{,}4 = 612{,}4$; se redondea a **613**. (b) Pide $613 - 240 =$ **373 paquetes**. (c) Con
revisión continua bastaría $1{,}645 \times 12\sqrt{3} = 34{,}2$ paquetes de seguridad: revisar una vez
por semana casi duplica la seguridad necesaria. (d) Con $R = 14$: $S = 935 + 81{,}4 = 1.016{,}4$.
Revisar menos seguido ahorra trabajo, pero obliga a guardar mucho más.

**5.8.** (a) $C_u = 11.000$, $C_o = 6.000$, $RC = 0{,}647$. Las acumuladas son 0,10, 0,30, 0,60, 0,85
y 1,00: la primera que llega a 0,647 es la de **250 ramos**. (b)

| Ramos armados | 100 | 150 | 200 | 250 | 300 |
|---|---|---|---|---|---|
| Probabilidad acumulada | 0,10 | 0,30 | 0,60 | 0,85 | 1,00 |
| Ganancia esperada | \$1.100.000 | \$1.565.000 | \$1.860.000 | **\$1.900.000** | \$1.727.500 |

La ganancia esperada es máxima en 250, como dijo la razón crítica. Fíjate que la demanda más probable
es 200: armar la moda deja plata en la mesa.

**5.9.** Físico al cierre de cada viernes y pedido (P) en las dos primeras políticas:

| Semana | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Demanda | 46 | 58 | 39 | 71 | 52 | 44 | 63 | 49 |
| (s, S) = (80, 200) | 104 | 46 · P 154 | 7 | 90 | 38 · P 162 | 0 (faltan 6) | 99 | 50 · P 150 |
| (s, Q) = (80, 120) | 104 | 46 · P 120 | 7 | 56 · P 120 | 4 | 80 · P 120 | 17 | 88 |

| Política | Pedidos | Faltantes | Inventario promedio | Costo de las 8 semanas |
|---|---|---|---|---|
| (s, S) = (80, 200) | 3 | 6 | 54,2 | \$293.600 |
| (s, Q) = (80, 120) | 3 | 0 | 50,2 | \$250.800 |
| (s, S) = (110, 200) | 4 | 0 | 66,5 | \$332.800 |

(c) La demanda media es de 52,75 unidades por semana, y $s$ tiene que cubrir la revisión más el plazo
(dos semanas): unas 105,5 unidades más la seguridad. Con $s = 80$ las dos primeras políticas van
expuestas: (s, Q) no tuvo faltantes por suerte (en la semana 5 quedaron 4 unidades). Con $s = 110$ no
falta nada, pero cuesta más en estas 8 semanas. Conviene solo si cada unidad faltante cuesta más de
\$11.533 (el punto en que $s = 110$ empata con $s = 80$). Si el repuesto detiene una máquina de un
cliente minero, cuesta mucho más que eso. Lectura: ocho semanas son una muestra corta; el número que
decide es el costo real de un faltante.

**5.10.** (a) $H = 0{,}16 \times 11.500 = 1.840$ pesos; $Q^* = \sqrt{2 \times 7.800 \times 52.000 / 1.840} =$
**664,0 sacos**. (b) Con 500 sacos, la razón de la curva plana da un costo 4,0 % mayor; con 1.000,
un 8,5 % mayor. Se pide **un camión**: pedir más mantener cuesta \$1.271.200 al año contra \$1.221.723
del EOQ (con dos camiones, \$1.325.600). Son 15,6 pedidos al año. (c) $d = 25$ sacos por día,
$\sigma_L = 8\sqrt{10} = 25{,}30$, demanda en el plazo 250.

| Nivel por ciclo | Stock de seguridad | Punto de reorden | Costo anual | Faltan por ciclo | Faltan al año | Tasa de servicio |
|---|---|---|---|---|---|---|
| 90 % | 32,4 | 282,4 | \$59.655 | 1,20 | 18,7 | 99,76 % |
| 95 % | 41,6 | 291,6 | \$76.566 | 0,53 | 8,2 | 99,89 % |
| 99 % | 58,9 | 308,9 | \$108.289 | 0,09 | 1,3 | 99,98 % |

Con camiones de 500 sacos, un 90 % por ciclo ya atiende el 99,76 % de las unidades: faltan unos 19
sacos al año. Pasar al 99 % cuesta \$48.634 más al año para salvar unos 17 sacos. Si un agricultor que
no encuentra su saco se va a la competencia para siempre, vale; si solo espera un día, el 90 % basta.
La política queda en (Q, r) = (500, 283) con el 90 %.

---

## 12. Caso integrador · Estampa Sur, la polera lisa

> Este caso sigue a Estampa Sur por todo el ramo. Cada unidad parte de lo que calculó la anterior;
> acá se usa el pronóstico de la unidad 4. Si no has hecho esa unidad, parte de los datos de esta
> sección.

Las poleras básicas se estampan sobre una **polera lisa** que Estampa Sur compra a un proveedor de
Santiago. Cada polera básica usa una polera lisa.

**De dónde sale la demanda anual.** El pronóstico de Holt de la unidad 4 da, para la familia
completa, 6.100 unidades el mes 1 y 6.200 el mes 2 (redondeadas a la centena). Las poleras básicas son
el 40 % de la familia. Se toma el promedio de los dos primeros meses y se lleva a un año:

$$D = 12 \times 0{,}40 \times \frac{6.100 + 6.200}{2} = 12 \times 0{,}40 \times 6.150 = 12 \times 2.460 = 29.520 \text{ poleras lisas al año}$$

Se usan solo los dos primeros meses porque son los más confiables del pronóstico. Como la tendencia
sube, la cifra queda algo corta: se recalcula cada trimestre.

| Dato | Valor |
|---|---|
| Demanda anual $D$ | 29.520 poleras |
| Costo por pedido $S$ | \$45.000 |
| Precio $C$ | \$2.400 por polera |
| Tasa de mantener $i$ | 25 % anual, así que $H = 600$ pesos |
| Días hábiles | 250 |
| Plazo $L$ | 5 días hábiles (una semana) |
| Desviación de la demanda diaria $\sigma_d$ | 22 poleras |
| Factor de seguridad $z$ | 1,65 |

**Pregunta.** ¿Cuánto y cuándo pedir poleras lisas?

**Desarrollo.**

1. **Lote.** $Q^* = \sqrt{2 \times 29.520 \times 45.000 / 600} = 2.104{,}3$; se redondea a la centena:
   **2.100 poleras**. Pedir más mantener cuesta \$1.262.569 al año con el EOQ exacto y \$1.262.571 con
   2.100: dos pesos de diferencia.
2. **Frecuencia.** $N = 29.520 / 2.100 = 14{,}06$ pedidos al año, uno cada 17,8 días hábiles (algo
   más de tres semanas y media).
3. **Demanda en el plazo.** $d = 29.520 / 250 = 118{,}08$ poleras por día; en 5 días,
   $118{,}08 \times 5 = 590{,}4$.
4. **Seguridad.** $\sigma_L = 22\sqrt{5} = 49{,}19$; $SS = 1{,}65 \times 49{,}19 = 81{,}2$ poleras.
   Con $z = 1{,}65$ el nivel de servicio por ciclo es del 95,1 %. Guardar esa seguridad cuesta
   \$48.702 al año.
5. **Punto de reorden.** $r = 590{,}4 + 81{,}2 = 671{,}6$, que se redondea hacia arriba a **672**.

**Lectura.** La política es **(Q, r) = (2.100, 672)**: cuando la posición de poleras lisas baja de
672, se piden 2.100. El stock de seguridad cuesta menos del 4 % del costo de pedir más mantener; es
una protección barata. Lo que más movería esta política es el plazo del proveedor: si el despacho
desde Santiago empieza a variar, el stock de seguridad crece mucho más que con la variación de la
demanda (sección 5).

**Lo que pasa a la unidad 8.** El lote de **2.100 poleras** entra al MRP como política de cantidad
fija de la polera lisa. Ahí la demanda deja de ser pareja (llega en lotes de 720 poleras básicas por
semana), así que el EOQ pasa a ser una aproximación: el MRP decide cuándo pedir mirando las
necesidades de cada semana, no el punto de reorden.

---

## 13. Para seguir

**En los libros del ramo.**

- Chase, Jacobs y Aquilano, *Administración de operaciones* (12.ª ed., 2009), capítulo 15 (el que fija
  el programa para esta unidad): EOQ, punto de reorden, stock de seguridad, revisión periódica y el
  modelo de un período.
- Heizer y Render, *Principios de administración de operaciones* (5.ª ed., 2004), capítulo de
  administración de inventarios: modelos de pedido, descuentos por cantidad y modelos
  probabilísticos. Sus problemas del final del capítulo son buena práctica adicional.
- Schroeder, *Administración de operaciones* (2.ª ed., 2004), capítulo de inventarios de demanda
  independiente.

**Abiertos y gratis.**

- Abbas y Goosheh, *Operations Management*, Fanshawe College (2025), en inglés. Busca en su índice la
  parte de inventarios. Descarga en la colección abierta de Ontario:
  https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/2473

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un ejercicio de descuentos por cantidad
donde el descuento no convenga y corrígeme paso a paso».
