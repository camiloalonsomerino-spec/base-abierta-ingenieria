---
ramo: Contabilidad y Costos
unidad: 11
titulo: Asignación de costos indirectos
version: 0.1 (16-10-2026)
requiere: [09-clasificacion-de-costos, 10-absorcion-y-variable]
alimenta: [12-costo-volumen-utilidad]
verificacion: verificacion/u11_asignacion_cif.py
---

# Unidad 11 · Asignación de costos indirectos

**Qué vas a poder hacer.** Calcular una tasa predeterminada de costos indirectos y aplicarla a
productos u órdenes; elegir la base de asignación que sigue a la causa del costo; medir y cerrar la
sobre o subaplicación con su asiento; repartir los departamentos de servicio con el método directo;
costear con actividades (ABC) en un caso chico, y detectar qué producto queda subcosteado por una
mala base y qué precio equivocado sale de ahí.

**Lo que necesitas antes.** Distinguir costo directo de indirecto y fijo de variable (unidad 9), y
saber que el costeo por absorción carga los costos fijos de fabricación al producto (unidad 10). Acá
se resuelve el cómo: cuánto le toca a cada producto.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

**Planilla.** `planillas/u11_asignacion_cif.xlsx` trae el ejemplo resuelto y el caso con fórmulas:
cambia una base o un dato y mira cómo se mueve el costo de cada producto.

---

## 1. La idea

El costo de fabricar un producto tiene tres partes (unidad 9): materia prima directa (MPD), mano de
obra directa (MOD) y costos indirectos de fabricación (CIF). Las dos primeras se miden producto por
producto: la madera de una silla se pesa, las horas del operario se anotan. Los CIF no: el arriendo
del galpón, la depreciación de la máquina, el sueldo del supervisor o la luz de la planta sirven a
todos los productos a la vez. Nadie puede decir cuánto arriendo «consumió» una silla.

Igual hay que repartirlos, por tres razones:

- **La norma lo pide.** El costeo por absorción (unidad 10) valoriza el inventario y el costo de
  ventas con todos los costos de fabricación, incluidos los indirectos.
- **El precio de largo plazo tiene que cubrirlos.** Si los precios cubren solo lo directo, el mes
  termina con el arriendo y la máquina sin pagar.
- **Comparar productos.** Saber cuál deja más después de pagar su parte de la planta.

Repartir es **asignar**: elegir una medida que todos los productos usan (la **base de asignación**)
y cargar el CIF en proporción a ella. La asignación es una estimación, no una medición. Si la base
está bien elegida, el producto que más usa la planta carga más; si está mal elegida, unos productos
pagan la planta de otros.

**Cuándo no se usa.** Para decisiones de corto plazo con capacidad ociosa (un pedido especial, seguir
o no con un producto un mes más), lo que manda es el margen de contribución (unidad 12). Asignar un
costo fijo no lo vuelve variable: el arriendo se paga igual si el pedido se acepta o no.

---

## 2. La tasa predeterminada

Los CIF reales se conocen al cierre del mes o del año, pero el costo de cada orden se necesita antes:
para cotizar, para valorizar lo que se entrega y para no esperar la última boleta de luz. Por eso
la tasa se fija **al inicio del período**, con el presupuesto:

$$\text{tasa predeterminada} = \frac{\text{CIF presupuestado del período}}{\text{base presupuestada del período}}$$

$$\text{CIF aplicado} = \text{tasa predeterminada} \times \text{base real usada}$$

La **base** es la medida en el denominador: horas máquina (HM), horas hombre (HH), unidades, kilos,
metros. El CIF aplicado a un producto es su uso de la base por la tasa.

**Por qué se fija para el período entero y no cada mes.** Si la tasa se recalculara con los CIF y la
producción de cada mes, la misma silla costaría más en un mes de poca producción (los fijos se
reparten entre menos unidades) y más en invierno (más calefacción). Ese vaivén no dice nada de la
silla. La tasa anual o del período presupuestado lo suaviza.

---

## 3. Elegir la base

La base correcta es la que **causa** el costo, el **inductor** (cost driver). Se pregunta: si este
producto usara el doble de la base, ¿la planta gastaría más en estos CIF?

| Base | Cuándo conviene | Ejemplo |
|---|---|---|
| Horas máquina | Los CIF son sobre todo de máquinas: depreciación, mantención, energía | Router CNC, inyectoras, pulpo de estampado |
| Horas hombre | El proceso es manual y los CIF siguen a la gente: supervisión, herramientas, espacio de trabajo | Costura, armado a mano, reparaciones |
| Unidades | Los productos son parecidos y usan la planta casi igual | Una sola línea con un producto en dos colores |
| Otra medida física (kilos, litros, metros) | El costo sigue al volumen de material | Lavandería (kilos), caldera (kilos de vapor) |

**La trampa de las unidades.** Repartir por unidades es lo más fácil y casi siempre lo más injusto
cuando los productos son distintos: carga lo mismo a un producto que ocupa la máquina 30 segundos y
a otro que la ocupa tres minutos. El producto lento queda **subcosteado** (se le carga menos de lo que
usa) y el rápido **sobrecosteado**. El CIF total asignado es el mismo; lo que cambia es quién lo paga.

---

## 4. Sobre y subaplicación

Al cierre se comparan los CIF reales con los aplicados:

$$\text{diferencia} = \text{CIF real} - \text{CIF aplicado} \qquad
\begin{cases} > 0 & \text{subaplicado: se cargó menos de lo gastado} \\ < 0 & \text{sobreaplicado: se cargó de más} \end{cases}$$

Hay diferencia por dos motivos: se gastó distinto de lo presupuestado (la luz subió) o se usó una
base distinta de la presupuestada (se produjo menos y la máquina trabajó menos horas, pero el
arriendo se pagó entero).

**En la contabilidad.** Los CIF reales se cargan al Debe de la cuenta **CIF** a medida que se
incurren (cada uno con su IVA crédito aparte, unidad 3). La aplicación los saca por el Haber hacia
**Productos en proceso**. Al cierre, el saldo de la cuenta CIF es la diferencia:

| Cuenta CIF | Debe | Haber |
|---|---|---|
| Lo que se gastó (CIF real) | ✓ | |
| Lo que se aplicó a la producción | | ✓ |
| Saldo deudor | subaplicado | |
| Saldo acreedor | | sobreaplicado |

Algunos cursos usan dos cuentas (CIF reales y CIF aplicados); al cierre se cancelan entre sí y el
resultado es el mismo.

**Cómo se cierra.**

- **Si es chica** (unos pocos puntos del aplicado), va entera a **Costo de ventas**: una
  subaplicación lo sube, una sobreaplicación lo baja.
- **Si es grande**, se **prorratea** entre Productos en proceso, Productos terminados y Costo de
  ventas, en proporción al CIF aplicado que tiene cada uno. Así el inventario queda al costo que de
  verdad tuvo.

Una diferencia grande y repetida dice que el presupuesto o la base están mal. Se corrige la tasa del
período siguiente, no se esconde en el costo de ventas.

---

## 5. Departamentos de servicio · el método directo

Una planta suele tener **departamentos productivos**, por donde pasa el producto (corte, armado), y
**departamentos de servicio**, que atienden a los productivos pero no tocan el producto (mantención,
bodega, casino). Los productos solo pasan por los productivos, así que primero hay que llevar el costo
de los servicios a los productivos; después cada productivo calcula su tasa con su propia base.

El **método directo** reparte cada servicio solo entre los productivos, en proporción a lo que cada
uno usó de ese servicio, e **ignora lo que los servicios se prestan entre sí**.

Una planta de muebles tiene Mantención ($1.170.000 al mes, se reparte por horas de mantención) y
Bodega ($640.000, se reparte por pedidos de materiales). Mantención atendió 312 horas a Corte, 138 a
Armado y 46 a Bodega; Bodega despachó 115 pedidos a Corte, 205 a Armado y 35 a Mantención. Corte
tiene $2.408.800 de CIF propio y Armado $1.761.200.

| | Corte | Armado |
|---|---|---|
| CIF propio | 2.408.800 | 1.761.200 |
| Mantención (312 y 138 de 450 horas) | 811.200 | 358.800 |
| Bodega (115 y 205 de 320 pedidos) | 230.000 | 410.000 |
| **Total del departamento** | **3.450.000** | **2.530.000** |
| Base | 1.150 HM | 1.840 HH |
| **Tasa** | **$3.000 por HM** | **$1.375 por HH** |

Las 46 horas que Mantención dio a Bodega y los 35 pedidos que Bodega dio a Mantención no se usan: el
método directo las salta. Los $5.980.000 de los cuatro departamentos quedan enteros en los dos
productivos. Si los servicios se prestan mucho entre sí, el **método escalonado** reparte primero el
servicio que más atiende a los otros (incluidos los demás servicios) y después el siguiente; el
**recíproco** resuelve las prestaciones cruzadas con un sistema de ecuaciones. El total que llega a
los productivos es el mismo en los tres; cambia cuánto le toca a cada uno.

**Por qué importa.** Corte es de máquinas y Armado de gente. Con una tasa única para toda la planta,
un producto que pasa mucho por Corte y poco por Armado recibiría la tasa promedio y quedaría mal
costeado (ejercicio 11.7).

---

## 6. Costeo basado en actividades (ABC)

El costeo tradicional usa una o dos bases que crecen con el volumen (horas, unidades). Pero muchos
CIF no dependen de cuántas unidades se hacen sino de **cuántas veces** se hace algo: preparar la
máquina para un trabajo nuevo, revisar un archivo, despachar un pedido. Un producto que se hace en
muchos lotes chicos consume mucho de eso aunque su volumen sea bajo.

El **ABC** reparte en dos pasos:

1. Se agrupan los CIF por **actividad** y cada actividad tiene su inductor: preparaciones, archivos
   revisados, horas de impresión, pedidos.
2. Se calcula una tasa por actividad y cada producto carga según cuánto usó de cada inductor.

$$\text{tasa de la actividad} = \frac{\text{costo de la actividad}}{\text{total del inductor}} \qquad \text{CIF del producto} = \sum_{\text{actividades}} \text{tasa} \times \text{uso del producto}$$

Una imprenta digital hace tarjetas de presentación (muchos trabajos chicos, personalizados) y volantes
(pocos trabajos, muy largos). Sus CIF del mes son $4.560.000. El método tradicional los reparte por
horas de impresión: 165 horas de tarjetas y 435 de volantes, $7.600 por hora.

| Actividad | Costo | Inductor | Tarjetas | Volantes | Tasa |
|---|---|---|---|---|---|
| Preparar trabajos | 1.776.000 | trabajos | 222 | 18 | 7.400 por trabajo |
| Revisar archivos | 912.000 | archivos | 170 | 22 | 4.750 por archivo |
| Imprimir | 1.872.000 | horas de impresión | 165 | 435 | 3.120 por hora |

| | Tarjetas | Volantes |
|---|---|---|
| Preparar | 1.642.800 | 133.200 |
| Revisar | 807.500 | 104.500 |
| Imprimir | 514.800 | 1.357.200 |
| **CIF con ABC** | **2.965.100** | **1.594.900** |
| CIF tradicional (por horas) | 1.254.000 | 3.306.000 |
| Volumen del mes | 2.400 cajas | 1.350 millares |
| CIF por unidad con ABC | 1.235,5 | 1.181,4 |
| CIF por unidad tradicional | 522,5 | 2.448,9 |

El método tradicional le cargaba a las tarjetas $1.711.100 menos de lo que consumen: cada caja parecía
costar \$522,5 de indirectos y cuesta $1.235,5. Con precios armados sobre el costo tradicional, la
imprenta regala las tarjetas y encarece los volantes, justo el producto donde compite por precio.

**Cuándo vale la pena el ABC.** Cuando los productos son muy distintos en tamaño de lote, en
complejidad o en atención que piden, y los CIF pesan mucho. Su costo es medir los inductores. Con
productos parecidos, una buena base de volumen da casi lo mismo.

---

## 7. Cómo una mala base distorsiona el precio

Muchas pymes fijan el precio con un **recargo** sobre el costo completo: precio = costo completo ×
(1 + recargo). Si el costo completo está mal, el precio también:

- El producto **subcosteado** sale con precio bajo: se vende mucho, parece estrella y en verdad deja
  poco o nada.
- El producto **sobrecosteado** sale caro: la competencia, que lo costea bien, lo vende más barato y
  se lleva a esos clientes.
- La empresa termina con más de lo que deja poco y menos de lo que deja mucho, y no entiende por qué
  baja la utilidad si «todos los productos tienen recargo».

La cifra total de CIF no cambia con la base. Lo que cambia es la **señal** que recibe cada decisión de
precio y de mezcla.

---

## 8. Ejemplo resuelto · la mueblería de Ignacia

Ignacia tiene una mueblería chica que hace **mesas de centro, sillas y repisas** con un router CNC y
dos maestros que arman y terminan. Para mayo presupuesta estos CIF:

| CIF presupuestado de mayo | Monto |
|---|---|
| Depreciación y mantención del router CNC | 3.094.000 |
| Energía | 947.300 |
| Arriendo del galpón | 1.480.000 |
| Supervisor | 708.000 |
| **Total** | **6.229.300** |

| Dato por unidad | Mesas de centro | Sillas | Repisas |
|---|---|---|---|
| Unidades presupuestadas | 125 | 460 | 310 |
| Horas máquina (router) | 2,4 | 0,5 | 0,9 |
| Horas hombre | 3,2 | 1,4 | 1,1 |
| Costo directo (MPD + MOD) | 58.400 | 21.700 | 17.900 |

Ignacia fija sus precios con un recargo de 40 % sobre el costo completo.

**Paso 1 · Elegir la base.** El router y su energía son $4.041.300, el 64,9 % de los CIF. El costo
lo causa la máquina: la base es **horas máquina**.

**Paso 2 · La tasa.** Horas máquina presupuestadas: 125 × 2,4 + 460 × 0,5 + 310 × 0,9 = 300 + 230 +
279 = **809 HM**.

$$\text{tasa} = \frac{6{.}229{.}300}{809} = 7{.}700 \text{ por HM}$$

**Paso 3 · CIF y costo completo por unidad, con tres bases.** Para comparar, las tasas por hora
hombre (1.385 HH presupuestadas) y por unidad (895 unidades) son $4.497,69 y $6.960,11.

| Por unidad | Mesas de centro | Sillas | Repisas |
|---|---|---|---|
| CIF por horas máquina | 18.480 | 3.850 | 6.930 |
| CIF por horas hombre | 14.393 | 6.297 | 4.947 |
| CIF por unidades | 6.960 | 6.960 | 6.960 |
| **Costo completo (HM)** | **76.880** | **25.550** | **24.830** |
| Costo completo (HH) | 72.793 | 27.997 | 22.847 |
| Costo completo (unidades) | 65.360 | 28.660 | 24.860 |
| **Precio con recargo (HM)** | **107.632** | **35.770** | **34.762** |
| Precio con recargo (unidades) | 91.504 | 40.124 | 34.804 |

Las tres bases reparten los mismos $6.229.300. Lo que cambia es quién los paga.

**Paso 4 · La distorsión.** Por unidades, cada mesa carga $6.960 de CIF cuando usa $18.480 de
máquina: en el mes, las mesas dejan de cargar $1.439.986, y las sillas cargan $1.430.651 de más (las
repisas casi no cambian). Con esa base Ignacia cobraría la mesa $16.128 menos de lo que debería y la
silla $4.354 más. Vendería mesas que no pagan el router y perdería clientes de sillas frente a un
competidor que las cobra a precio justo.

**Paso 5 · El cierre de mayo.** En mayo salieron 116 mesas, 505 sillas y 296 repisas. Horas máquina
reales: 278,4 + 252,5 + 266,4 = **797,3 HM**. CIF aplicado: 797,3 × 7.700 = **$6.139.210**. Los CIF
reales sumaron **$6.318.400**.

$$\text{subaplicado} = 6{.}318{.}400 - 6{.}139{.}210 = 179{.}190$$

Es el 2,9 % de lo aplicado: chico, va entero a costo de ventas.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 31-05-2026 | Productos en proceso | 6.139.210 | |
| | | CIF | | 6.139.210 |
| | | *Glosa: CIF aplicado a la producción de mayo (797,3 HM × $7.700).* | | |
| 2 | 31-05-2026 | Costo de ventas | 179.190 | |
| | | CIF | | 179.190 |
| | | *Glosa: cierre del CIF subaplicado contra el costo de ventas.* | | |

Con los dos asientos, la cuenta CIF queda en cero: tenía $6.318.400 al Debe (lo gastado durante el
mes) y $6.139.210 + $179.190 al Haber.

**Cómo se lee.** La base de horas máquina dice que la mesa de centro es el producto caro de la
planta: $76.880 de costo completo, no $65.360. Si Ignacia cotiza por unidades, la mesa queda a
$91.504 y la vende bajo lo que cuesta con su recargo; la silla, a $40.124, se le va a la competencia.
La subaplicación de mayo ($179.190) es chica y sale de que se produjo un poco menos que lo
presupuestado; no obliga a cambiar la tasa.

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Repartir por unidades productos que usan la planta de forma muy distinta | Busca qué causa el CIF; si es la máquina, horas máquina |
| Calcular la tasa con los CIF y la base reales de cada mes | La tasa se fija con el presupuesto del período; la diferencia se cierra al final |
| Aplicar el CIF con la base presupuestada en vez de la real | CIF aplicado = tasa × base **real** usada |
| Invertir sub y sobreaplicación | Real mayor que aplicado es subaplicado: falta costo, el costo de ventas sube |
| Invertir Debe y Haber en el cierre | Subaplicado: Debe Costo de ventas, Haber CIF. Sobreaplicado: al revés |
| Meter gastos de administración o de ventas en el CIF | El CIF es solo de fabricación; la oficina y la publicidad son gasto del período (unidad 9) |
| Poner el IVA de una factura de CIF dentro del costo | El IVA crédito va a su cuenta (unidad 3); al CIF entra el neto |
| Usar el costo completo con fijos asignados para decidir un pedido especial | Con capacidad ociosa decide el costo variable; el fijo se paga igual (ejercicio 11.8) |
| En el método directo, repartir un servicio también a otro servicio | El directo reparte solo a los productivos; si quieres incluir los cruces, usa el escalonado |
| Creer que el ABC cambia el CIF total | Solo cambia el reparto; el total es el mismo |

---

## 10. Práctica

Diez ejercicios: 11.1 a 11.4 básicos, 11.5 a 11.8 intermedios, 11.9 y 11.10 de desafío. Las pautas
están en la sección 11.

**11.1 · Taller mecánico (básico).** Un taller presupuesta $18.900.000 de CIF al año y 4.200 horas
hombre de mecánicos. Calcula la tasa predeterminada y el CIF que se aplica a tres órdenes: la A usó
6,5 HH, la B 2 HH y la C 11 HH.

**11.2 · Un matrimonio de 80 invitados (básico).** Una banquetería prepara un evento con $410.000 de
materias primas y 24 horas de cocineros a $5.200 la hora. Aplica CIF a $3.600 por hora hombre y cobra
con un recargo de 35 % sobre el costo completo. Calcula el costo del evento, el precio y el costo y
el precio por invitado.

**11.3 · Cierre en una fábrica de cecinas (básico).** La tasa predeterminada es $2.150 por hora
máquina. En el año se usaron 3.380 HM y los CIF reales fueron $6.980.000. (a) ¿Hubo sobre o
subaplicación, y de cuánto? (b) Registra el cierre contra el costo de ventas. (c) ¿El costo de ventas
sube o baja?

**11.4 · Botellas y bidones (básico).** Una fábrica de envases presupuesta $9.600.000 de CIF al mes,
casi todo de sus inyectoras. Hace 40.000 botellas (0,01 HM cada una) y 8.000 bidones (0,075 HM). (a)
Calcula el CIF por unidad con base horas máquina y con base unidades. (b) ¿Qué producto queda
subcosteado por unidades y en cuánto, en el mes? (c) ¿Qué base usarías y por qué?

**11.5 · Prorratear una subaplicación (intermedio).** Al cierre del año una empresa tiene $348.000 de
CIF subaplicado. El CIF aplicado del año quedó así: $640.000 en Productos en proceso, $1.160.000 en
Productos terminados y $4.000.000 en Costo de ventas. (a) Prorratea la diferencia y registra el
asiento. (b) ¿Cuánto del subaplicado queda en el inventario y cuánto pasa a resultados? (c) ¿Por qué
no mandar todo a costo de ventas?

**11.6 · Lavandería industrial (intermedio).** Dos departamentos de servicio: Mantención ($840.000,
por horas: 210 a Lavado, 70 a Planchado y 40 a Caldera) y Caldera ($1.260.000, por kilos de vapor:
5.400 a Lavado y 3.600 a Planchado). Los productivos tienen CIF propio de $2.100.000 (Lavado) y
$1.500.000 (Planchado). Lavado aplica por kilo de ropa (42.000 kg al mes) y Planchado por hora de
planchado (1.230 horas). (a) Reparte con el método directo y calcula las dos tasas. (b) ¿Cuánto CIF
carga el servicio a un hotel que mandó 1.500 kg y 60 horas de planchado? (c) Repite el reparto con el
método escalonado, empezando por Mantención, y compara.

**11.7 · Una tasa o dos (intermedio).** Una fábrica de mochilas hace 3.000 mochilas escolares y 1.500
mochilas técnicas al mes. Corte es de máquinas: $2.700.000 de CIF; la escolar usa 0,10 HM y la técnica
0,40 HM. Costura es manual: $2.340.000 de CIF; la escolar usa 0,8 HH y la técnica 1,0 HH. En Corte
también hay 0,05 HH por escolar y 0,10 HH por técnica. (a) Calcula el CIF por mochila con una tasa
única de planta por hora hombre. (b) Con una tasa por departamento (HM en Corte, HH en Costura). (c)
El costo directo es $9.800 (escolar) y $21.500 (técnica) y el precio lleva un recargo de 30 %. Un
competidor vende la escolar a $13.900: ¿qué precio sale en cada caso y qué concluye la fábrica?

**11.8 · Pedido especial de mochilas (intermedio).** Con los datos de 11.7 y tasas por departamento:
de los \$780 de CIF de la mochila escolar, \$180 son variables (hilo, energía de las máquinas); el resto
es fijo. Un colegio pide 600 mochilas escolares a $10.300 cada una. (a) ¿Cuánto «pierde» el pedido
según el costo completo? (b) ¿Cuánto aporta según el costo variable, si hay capacidad ociosa? (c) ¿Y
si no hay capacidad y cada mochila del colegio reemplaza una venta normal a $14.000?

**11.9 · La cerveza de edición especial (desafío).** Una cervecería artesanal vende 34.500 latas y
5.750 botellas de edición especial al mes. Sus CIF son $7.192.000 y hoy los reparte por horas hombre
de elaboración (870 para latas y 290 para la especial). Un análisis por actividades da:

| Actividad | Costo | Inductor | Latas | Especial |
|---|---|---|---|---|
| Cocción | 2.856.000 | cocciones | 31 | 17 |
| Control de calidad | 1.428.000 | análisis | 42 | 77 |
| Envasado | 2.184.000 | horas de línea | 210 | 154 |
| Despacho | 724.000 | pedidos | 88 | 93 |

El costo directo es \$835 por lata y $1.665 por botella; los precios netos son $1.420 y $2.640. (a)
Calcula el CIF por unidad con el método actual y con ABC. (b) Calcula la holgura (precio menos costo
completo) de cada producto con los dos métodos. ¿Cuál parecía la estrella y cuál lo es? (c) ¿Qué
precio necesita la especial para tener sobre su costo ABC el mismo recargo que aparentaba tener sobre
el costo tradicional?

**11.10 · La espiral (desafío).** Una planta de cajas tiene $5.880.000 de CIF fijo al mes y una
capacidad práctica de 2.100 HM. El año A presupuesta 1.680 HM; el año B, con menos demanda, 1.260 HM.
Cada caja usa 0,6 HM, su costo variable es $4.150 y el precio lleva un recargo de 25 % sobre el costo
completo. (a) Calcula la tasa, el CIF por caja y el precio en A y en B si la tasa usa la base
presupuestada. (b) Repite con la capacidad práctica como base y calcula el costo de la capacidad
ociosa de cada año. (c) ¿Qué pasa con la demanda si la planta sube el precio justo cuando vende
menos?

---

## 11. Pautas

**11.1.** Tasa: 18.900.000 / 4.200 = **$4.500 por HH**. CIF aplicado: A **$29.250**, B **$9.000** y C
**$49.500**; en total $87.750. La orden C carga cinco veces y media lo de la B porque usó cinco veces y
media sus horas: eso es lo que la base dice que la causa.

**11.2.** MOD: 24 × 5.200 = **$124.800**. CIF: 24 × 3.600 = **$86.400**. Costo completo: 410.000 +
124.800 + 86.400 = **$621.200**. Precio: × 1,35 = **$838.620**. Por invitado: costo **$7.765** y
precio **$10.483**. La banquetería sabe que bajo $7.765 por persona, en el largo plazo, no cubre su
cocina.

**11.3.** (a) Aplicado: 2.150 × 3.380 = **$7.267.000**. Real $6.980.000. **Sobreaplicado $287.000**
(3,9 % de lo aplicado): se cargó al producto más de lo que se gastó. (b)

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 30-06-2026 | CIF | 287.000 | |
| | | Costo de ventas | | 287.000 |
| | | *Glosa: cierre del CIF sobreaplicado contra el costo de ventas.* | | |

(c) **Baja**: el costo de ventas tenía $287.000 de más. El asiento lo corrige y la utilidad sube en lo
mismo.

**11.4.** (a) Horas máquina: 400 de botellas y 600 de bidones, 1.000 en total. Tasa **$9.600 por HM**:
botella **\$96**, bidón **\$720**. Por unidades (48.000): **\$200** a cada una. (b) El bidón queda
subcosteado: carga \$200 cuando usa \$720 de máquina. En el mes, los bidones dejan de cargar
**$4.160.000**, que pagan las botellas. (c) Horas máquina: los CIF son de las inyectoras y un bidón
ocupa la máquina siete veces y media lo que una botella.

**11.5.** (a) Total aplicado $5.800.000; la subaplicación es el 6,0 % de él.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 31-12-2026 | Productos en proceso | 38.400 | |
| | | Productos terminados | 69.600 | |
| | | Costo de ventas | 240.000 | |
| | | CIF | | 348.000 |
| | | *Glosa: prorrateo del CIF subaplicado del año.* | | |

(b) Quedan **$108.000** en inventario (proceso y terminados) y **$240.000** van a resultados este año.
(c) Porque una parte de lo producido todavía no se vende: mandar todo a costo de ventas castigaría la
utilidad de este año por costos que pertenecen a productos que se venden el próximo. Con un 6 % el
prorrateo se justifica; con un 1 % no valdría la pena.

**11.6.** (a) Método directo (Mantención reparte sobre 280 horas, sin las 40 de Caldera):

| | Lavado | Planchado |
|---|---|---|
| CIF propio | 2.100.000 | 1.500.000 |
| Mantención | 630.000 | 210.000 |
| Caldera | 756.000 | 504.000 |
| Total | **3.486.000** | **2.214.000** |
| Tasa | **\$83 por kg** | **$1.800 por hora** |

(b) Hotel: 1.500 × 83 = **$124.500** y 60 × 1.800 = **$108.000**; **$232.500** de CIF. (c) Escalonado:
Mantención reparte sobre sus 320 horas: **$551.250** a Lavado, **$183.750** a Planchado y **$105.000** a
Caldera. Caldera reparte ahora **$1.365.000**: **$819.000** a Lavado y **$546.000** a Planchado. Totales:
Lavado **$3.470.250** y Planchado **$2.229.750**. El total es el mismo; Planchado carga un poco más
porque la mantención de la caldera ahora le llega por kilos de vapor (donde pesa 40 %) y no por horas
de mantención (donde pesa 25 %). Con diferencias así de
chicas, el método directo basta.

**11.7.** (a) Horas hombre de la planta: 3.000 × 0,85 + 1.500 × 1,10 = **4.200 HH**. Tasa única
(2.700.000 + 2.340.000) / 4.200 = **$1.200 por HH**: escolar **$1.020**, técnica **$1.320**. (b)
Corte: 2.700.000 / 900 HM = **$3.000 por HM**. Costura: 2.340.000 / 3.900 HH = **\$600 por HH**.
Escolar: 0,10 × 3.000 + 0,8 × 600 = **\$780**. Técnica: 0,40 × 3.000 + 1,0 × 600 = **$1.800**. Las dos
formas asignan los mismos $5.040.000. (c)

| | Escolar | Técnica |
|---|---|---|
| Precio con tasa única | 14.066 | 29.666 |
| Precio con tasas por departamento | 13.754 | 30.290 |

Con la tasa única la fábrica cree que no puede competir con los $13.900 del rival en la escolar; con
las tasas por departamento ve que sí puede (13.754). La técnica, que pasa mucho por las máquinas de
Corte, estaba subcosteada en la tasa única.

**11.8.** (a) Costo completo de la escolar: 9.800 + 780 = **$10.580**; al precio del colegio
«perdería» (10.580 − 10.300) × 600 = **$168.000**. (b) Costo variable: 9.800 + 180 = **$9.980**. Cada
mochila aporta **\$320** y el pedido **$192.000** al resultado: con capacidad ociosa, **se acepta**. Los
fijos se pagan igual con o sin el pedido. (c) Sin capacidad, cada mochila del colegio desplaza una que
aportaba 14.000 − 9.980 = **$4.020**: el pedido le quitaría $2.412.000 de margen a cambio de $192.000. El
resultado empeora en **$2.220.000**: se rechaza. La decisión no la da el costo completo en ninguno de los
dos casos; la da el margen y la capacidad.

**11.9.** (a) Tasa actual: 7.192.000 / 1.160 HH = **$6.200 por HH**: latas **$5.394.000**, especial
**$1.798.000**; por unidad **156,35** y **312,70**. Tasas ABC: cocción **$59.500**, análisis **$12.000**,
hora de línea **$6.000** y pedido **$4.000**.

| Actividad | Latas | Especial |
|---|---|---|
| Cocción | 1.844.500 | 1.011.500 |
| Control de calidad | 504.000 | 924.000 |
| Envasado | 1.260.000 | 924.000 |
| Despacho | 352.000 | 372.000 |
| **CIF con ABC** | **3.960.500** | **3.231.500** |
| Por unidad | 114,80 | 562,00 |

(b)

| | Latas | Especial |
|---|---|---|
| Costo completo tradicional | 991,35 | 1.977,70 |
| Holgura tradicional | 428,65 | 662,30 |
| Costo completo ABC | 949,80 | 2.227,00 |
| Holgura ABC | 470,20 | 413,00 |

Con el método actual la especial parecía la estrella (\$662 por botella contra \$429 por lata). Con ABC
es al revés: la especial pide muchas cocciones chicas, muchos análisis y muchos pedidos, y deja
\$413; la lata deja \$470. (c) El recargo aparente era 2.640 / 1.977,70 − 1 = 33,5 %. Para tenerlo sobre
el costo ABC, la especial tendría que costar **$2.972,79**. Si el mercado no lo paga, la otra salida es
bajar su costo de actividades: lotes más grandes, menos análisis por cocción, pedidos mínimos.

**11.10.** (a) Base presupuestada: año A **$3.500 por HM**, **$2.100** por caja y precio **$7.812,50**;
año B **$4.667 por HM**, **$2.800** por caja y precio **$8.688**. (b) Capacidad práctica: **$2.800 por
HM** los dos años, **$1.680** por caja y precio **$7.288**. La capacidad ociosa cuesta **$1.176.000** en A
(420 HM sin usar) y **$2.352.000** en B (840 HM); se informa aparte como costo del período, no se carga a
la caja. (c) Con la base presupuestada, el precio sube 11,2 % justo cuando la demanda cae: vende
menos, la tasa del año siguiente sube otra vez y así. Es la **espiral de la muerte**. La capacidad
práctica corta la espiral: la caja carga solo la planta que usa y la gerencia ve el costo de lo que
sobra como un problema de capacidad, no de precio.

---

## 12. Caso integrador · Estampa Sur, el costo completo de cada prenda

> Este caso sigue el mes de marzo de Estampa Sur (taller de serigrafía ficticio) por todo el ramo.
> La unidad 9 separó los costos fijos de fabricación del mes y la unidad 10 los cargó a las prendas
> para el costeo por absorción. Acá se mira con lupa cómo se repartieron y qué pasa con otra base.

**Lo que recibe.** De la unidad 9, el CIF fijo de marzo: sueldos de las 4 personas $2.880.000,
depreciación de las dos máquinas $310.833,33 (unidad 4), seguro devengado $79.000 y arriendo
devengado $580.000 (unidad 5), en total **$3.849.833,33**. En este taller los sueldos son fijos: las
cuatro personas cobran el mes completo produzcan lo que produzcan, así que entran al CIF fijo y no al
costo variable. Y el costo variable estándar de cada prenda (unidad 9).

**Pregunta.** ¿Cuánto CIF fijo carga cada prenda? ¿Qué prenda queda mal costeada si el taller reparte
por unidades?

**Desarrollo.**

1. **La base.** El CIF fijo del taller es de la máquina de estampado y de la gente que la opera: lo
   causa el tiempo de estampado. Base: **segundos de estampado**.

| | Poleras básicas | Polerones | Poleras estampado doble | Bolsas | Gorros |
|---|---|---|---|---|---|
| Producidas en marzo | 2.236 | 839 | 838 | 1.006 | 671 |
| Segundos por prenda | 30 | 90 | 110 | 20 | 30 |
| Segundos del mes | 67.080 | 75.510 | 92.180 | 20.120 | 20.130 |

2. **La tasa.** Segundos del mes: **275.020**. Como marzo produjo exactamente lo planeado, la base
   presupuestada y la real coinciden y no queda sobre ni subaplicación por volumen.

$$\text{tasa} = \frac{3{.}849{.}833{,}33}{275{.}020} = 13{,}9984 \text{ por segundo}$$

3. **CIF fijo y costo completo por prenda.**

| Por prenda | Poleras básicas | Polerones | Poleras estampado doble | Bolsas | Gorros |
|---|---|---|---|---|---|
| Precio neto | 3.990 | 9.890 | 6.290 | 2.490 | 3.190 |
| Costo variable estándar | 2.610 | 5.950 | 4.020 | 1.530 | 2.020 |
| CIF fijo (segundos) | 419,95 | 1.259,85 | 1.539,82 | 279,97 | 419,95 |
| **Costo completo** | **3.029,95** | **7.209,85** | **5.559,82** | **1.809,97** | **2.439,95** |
| Precio − costo completo | 960,05 | 2.680,15 | 730,18 | 680,03 | 750,05 |
| Sobre el precio | 24,1 % | 27,1 % | 11,6 % | 27,3 % | 23,5 % |

4. **La misma cuenta por unidades.** Repartido entre las 5.590 prendas, cada una carga **\$688,70**,
   tarde lo que tarde en la máquina.

| Por prenda | Poleras básicas | Polerones | Poleras estampado doble | Bolsas | Gorros |
|---|---|---|---|---|---|
| Costo completo (unidades) | 3.298,70 | 6.638,70 | 4.708,70 | 2.218,70 | 2.708,70 |
| Precio − costo completo | 691,30 | 3.251,30 | 1.581,30 | 271,30 | 481,30 |
| CIF de más (+) o de menos (−) | +268,75 | −571,15 | −851,12 | +408,73 | +268,75 |
| En el mes | +600.922 | −479.198 | −713.240 | +411.185 | +180.330 |

Lo que una base le quita a unas prendas se lo pone a otras: la última fila suma cero.

**Lectura.** Por unidades, las **poleras de estampado doble** y los **polerones** quedan subcosteados:
la de estampado doble ocupa la máquina 110 segundos y cargaría lo mismo que una bolsa de 20. Con esa
base parecería que la de estampado doble deja \$1.581,30 por prenda y es de las mejores; con la base
correcta deja \$730,18, apenas el 11,6 % de su precio, la peor del taller. Al revés, las bolsas
parecerían casi no dejar nada (\$271,30) y en verdad dejan el 27,3 % de su precio. Un taller que
reparte por unidades empujaría la prenda que menos le deja y descuidaría la que más. La decisión de
precio que sale de aquí: en el largo plazo la polera de estampado doble no puede venderse bajo
$5.559,82; en un pedido puntual con capacidad ociosa, el piso es su costo variable de $4.020 (unidad
12).

**Lo que pasa a la unidad 12.** El CIF fijo de $3.849.833,33 (que con los $436.000 de administración
forma los costos fijos operacionales) y el margen de contribución de cada prenda. El punto de
equilibrio no usa la tasa por segundo: los fijos no cambian con lo que se vende, así que allá se
cubren con el margen, no se reparten.

---

## 13. Para seguir

**En los libros del ramo.**

- Obligatorios del programa: Gálvez y Clarke, *Contabilidad financiera para la dirección de empresas*,
  Ediciones UC, e Irarrázabal, *Contabilidad: fundamentos y usos*, Ediciones UC, 2014.
- Complementarios: Horngren, *Contabilidad de costos*, Pearson, 2012 (costeo por órdenes con tasas
  predeterminadas, asignación de departamentos de soporte y costeo basado en actividades), y Garrison,
  Noreen y Brewer, *Contabilidad administrativa*, McGraw-Hill, 2007 (tasas predeterminadas, sobre y
  subaplicación, y ABC).

**Abierto y gratis.**

- Franklin, Graybeal y Cooper, *Principles of Accounting, Volume 2: Managerial Accounting*, OpenStax
  (2019), en inglés, licencia CC BY-NC-SA. Capítulo 4, secciones 4.4 (tasa predeterminada) y 4.6
  (sobre y subaplicación): https://openstax.org/books/principles-managerial-accounting/pages/4-why-it-matters.
  Capítulo 6, secciones 6.1 a 6.4 (asignación tradicional, inductores y ABC):
  https://openstax.org/books/principles-managerial-accounting/pages/6-why-it-matters

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame tres productos con sus horas máquina y
horas hombre, déjame elegir la base y calcular el costo completo, y muéstrame qué precio saldría mal
con la base equivocada».
