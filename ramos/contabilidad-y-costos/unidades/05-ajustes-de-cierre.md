---
ramo: Contabilidad y Costos
unidad: 5
titulo: Ajustes de cierre · anticipados, devengados y provisiones
version: 0.1 (16-10-2026)
requiere: [02-partida-doble, 03-iva, 04-depreciacion]
alimenta: [06-prestamos-e-intereses, 08-razones-financieras, 09-clasificacion-de-costos]
verificacion: verificacion/u05_ajustes.py
---

# Unidad 5 · Ajustes de cierre: anticipados, devengados y provisiones

**Qué vas a poder hacer.** Separar lo que pasó en un período de lo que se pagó o cobró en él;
repartir un pago o un cobro anticipado entre los meses que cubre; reconocer al cierre los gastos y
los ingresos ya ganados que todavía no se mueven por el banco; estimar los incobrables y las
vacaciones que se deben; escribir cada ajuste como asiento cuadrado, y medir cuánto cambia el
resultado y el balance si un ajuste se olvida.

**Lo que necesitas antes.** Escribir un asiento con Debe y Haber y llevarlo al mayor (unidad 2); el
IVA crédito y débito (unidad 3); la depreciación (unidad 4), que es el primer ajuste de cierre que
ya conoces.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

**Planilla.** `planillas/u05_ajustes.xlsx`: el cálculo de los anticipados, la estimación de
incobrables y el libro diario de los ajustes del ejemplo, con fórmulas.

---

## 1. La idea · base devengada contra base caja

Hay dos maneras de medir cuánto ganó una empresa en un mes:

- **Base caja.** Ingreso es la plata que entró; gasto, la que salió. Es fácil, pero mezcla meses:
  un arriendo de tres meses pagado hoy «pierde» este mes y «gana» los dos siguientes.
- **Base devengada.** Un ingreso se reconoce cuando se **gana** (se entregó el bien o se prestó el
  servicio) y un gasto cuando se **consume** el recurso para generar los ingresos del período,
  se haya pagado o no. Es la base de la contabilidad financiera.

| Hecho del mes | Base caja | Base devengada |
|---|---|---|
| Se vende a crédito, se cobra el mes siguiente | nada este mes | ingreso este mes |
| Un cliente paga hoy un servicio del mes siguiente | ingreso este mes | pasivo hoy, ingreso el mes siguiente |
| Se paga hoy un seguro de un año | gasto completo este mes | activo hoy, gasto mes a mes |
| Los sueldos del mes se pagan el día 5 del mes siguiente | nada este mes | gasto este mes |

**Por qué importa.** El resultado devengado responde la pregunta que interesa: ¿el negocio, con lo
que hizo este mes, cubre lo que consumió este mes? La caja responde otra (¿alcanza la plata?), que
se mira en el flujo de efectivo. Con base caja, un mes en que se paga el seguro anual parece malo y
los once siguientes parecen mejores de lo que son.

Durante el mes se registra lo que pasa por el banco o por un documento (unidades 2 y 3). Al cierre
quedan cuentas desalineadas con el período: un seguro pagado que ya se consumió en parte, un sueldo
ganado y no pagado. Los **asientos de ajuste** las alinean antes de armar los estados.

---

## 2. Las familias de ajustes

| Familia | Al momento del movimiento | Ajuste al cierre | Ejemplos |
|---|---|---|---|
| Gasto pagado por anticipado | Activo (D) contra Banco (H) | Gasto (D) contra el activo (H) | seguro (SPPA), arriendo (APPA) |
| Ingreso recibido por anticipado | Banco (D) contra Pasivo (H) | el pasivo (D) contra Ingreso (H) | arriendo recibido (ARA), anticipo de clientes |
| Gasto devengado no pagado | nada todavía | Gasto (D) contra un por pagar (H) | sueldos, luz, intereses por pagar |
| Ingreso devengado no cobrado | nada todavía | un por cobrar (D) contra Ingreso (H) | intereses por cobrar, arriendo por cobrar |
| Estimación | nada todavía | Gasto (D) contra una estimación o provisión (H) | depreciación, incobrables, vacaciones |

**La regla que ordena todo.** Cada ajuste toca **una cuenta de balance y una de resultado**, y **no
toca Banco**. La plata ya se movió (anticipados) o se moverá después (devengados); el ajuste solo
dice a qué período pertenece. Si un asiento de ajuste lleva Banco, es otra cosa: un pago o un cobro.

**Nombres.** En Chile se usan siglas: SPPA (seguro pagado por adelantado), APPA (arriendo pagado por
adelantado), ARA (arriendo recibido por adelantado), IPPA (ingreso percibido por adelantado).
«Adelantado» y «anticipado» son lo mismo.

---

## 3. Gastos pagados por anticipado · SPPA y APPA

Cuando se paga por adelantado, lo que se compra es un **derecho a recibir un servicio**: es un
activo. A medida que pasan los meses el derecho se consume y se vuelve gasto.

$$\text{devengado del período} = \text{monto} \times \frac{\text{meses consumidos en el período}}{\text{meses que cubre}} \qquad \text{saldo anticipado} = \text{monto} - \text{devengado acumulado}$$

**La intuición.** El servicio se presta parejo en el tiempo, así que el gasto se reparte parejo. El
saldo que queda en el activo es exactamente lo que valen los meses que faltan.

**Los meses.** Cuenta los meses de cobertura dentro del período: una póliza del 01-08 al 31-07,
cerrando el 31-12, lleva 5 meses consumidos (agosto a diciembre). Contar mal los meses es el error
más común de esta unidad.

**El IVA no se reparte.** Si la factura trae IVA (un seguro general, por ejemplo), el crédito fiscal
completo se registra **el día de la factura** (unidad 3). El ajuste reparte solo el neto.

**Dos formas de registrar el pago.** El curso lo registra como activo (**método del balance**) y
ajusta la parte consumida. Hay empresas que lo registran entero como gasto (**método del
resultado**) y al cierre devuelven al activo la parte no consumida. Los dos llegan a los mismos
saldos; lo que cambia es el ajuste (ejercicio 5.5).

**Cuándo no se usa.** Un pago chico que se consume en el mismo mes (una resma de papel) va directo a
gasto: repartirlo cuesta más de lo que informa. El ajuste importa cuando el monto es relevante y
cruza el cierre.

---

## 4. Ingresos recibidos por anticipado · ARA, IPPA y anticipos

Si un cliente paga antes de recibir el servicio, la empresa **le debe** ese servicio (o la
devolución de la plata): es un **pasivo**. El ingreso se reconoce a medida que se presta.

| Fecha | Cuenta | Debe | Haber |
|---|---|---|---|
| Al recibir | Banco | monto | |
| | Arriendo recibido por anticipado (pasivo) | | monto |
| Al cierre | Arriendo recibido por anticipado | parte ganada | |
| | Arriendo ganado (ingreso) | | parte ganada |

La parte ganada se calcula con la misma fórmula de la sección 3. Un **anticipo de clientes** por una
mercadería que se entregará después sigue el mismo camino, pero se salda cuando se entrega (no por
meses): mientras no se entregue, al cierre **no hay ajuste** y el anticipo sigue en el pasivo.

---

## 5. Devengados no pagados ni cobrados

Son lo contrario de los anticipados: el período ya consumió el servicio (o ya lo prestó), pero la
plata se mueve después.

- **Gasto devengado no pagado.** Sueldos del mes que se pagan el día 5 siguiente, la cuenta de luz
  que llega el 31 y vence el 15, intereses de un préstamo que se pagan con la próxima cuota (unidad
  6). Asiento: Gasto (D) contra Sueldos por pagar o Cuentas por pagar (H). Si la factura trae IVA,
  el crédito fiscal entra en el mismo asiento.
- **Ingreso devengado no cobrado.** Intereses de un depósito a plazo que vence el mes siguiente,
  un arriendo del mes que el arrendatario paga después. Asiento: Intereses por cobrar (D) contra
  Intereses ganados (H).

Cuando llega el pago, se salda el por pagar: Sueldos por pagar (D) contra Banco (H). **No se vuelve
a registrar el gasto**; ya está en el período en que se ganó.

### Remuneraciones con descuentos (mención)

Una liquidación de sueldo tiene tres capas: el **bruto** (lo que gana el trabajador, gasto de la
empresa), los **descuentos** que la empresa retiene y entera después a las instituciones (cotizaciones
previsionales y de salud, impuesto único) y el **líquido**, que es lo que se le paga al trabajador.
Además el empleador paga **aportes propios** que son gasto adicional.

| Cuenta | Debe | Haber |
|---|---|---|
| Gasto en remuneraciones | bruto | |
| Aportes del empleador | aportes | |
| Retenciones previsionales por pagar | | descuentos previsionales + aportes |
| Impuesto único por pagar | | impuesto retenido |
| Remuneraciones por pagar | | líquido |

El gasto es el bruto más los aportes, no el líquido. Las tasas de cada descuento las fija la ley y
cambian; en esta unidad vienen siempre como dato.

---

## 6. Estimaciones y provisiones

Algunos ajustes no salen de un contrato sino de una **estimación**. Ya viste una: la depreciación
(unidad 4). Hay dos más que el ramo usa.

### Deudores incobrables

Una parte de lo que los clientes deben no se va a cobrar. La base devengada pide reconocer esa
pérdida en el período de la venta, no cuando el cliente desaparece. Se estima con un porcentaje de
los saldos (o por **antigüedad**: más porcentaje a las deudas más viejas) y se registra en una
**cuenta complementaria de activo**, que resta a Clientes en el balance:

$$\text{ajuste} = \text{estimación requerida} - \text{saldo que ya tiene la estimación}$$

Asiento: Gasto por incobrables (D) contra Estimación de deudores incobrables (H). Cuando un cliente
se declara incobrable (el **castigo**), se rebajan las dos cuentas: Estimación (D) contra Clientes
(H). El castigo **no toca el resultado**: la pérdida ya se reconoció al estimar. El nombre clásico es
«provisión de deudores incobrables»; hoy se habla de estimación o deterioro.

### Vacaciones

Cada mes trabajado el trabajador gana días de vacaciones que tomará después. Al cierre, el costo de
los días ganados y no tomados es una deuda con él: Gasto en vacaciones (D) contra Provisión de
vacaciones (H), por la diferencia entre lo que debería tener la provisión y lo que tiene. Cuando
toma los días, se usa la provisión; no se vuelve a cargar gasto.

### Otros registros de cierre

- **Faltantes y mermas** del conteo físico: Gasto por merma (D) contra Existencias (H) (unidad 7).
- **Cierre de las cuentas de resultado.** Después de los ajustes, los ingresos y gastos (cuentas
  temporales) se cierran contra Resultado del ejercicio y empiezan el período siguiente en cero. Las
  cuentas de balance (permanentes) pasan con su saldo.

---

## 7. El efecto en los estados

Como cada ajuste toca una cuenta de balance y una de resultado, olvidarlo deja **dos** estados mal:

| Ajuste olvidado | Activo | Pasivo | Resultado y patrimonio |
|---|---|---|---|
| Gasto pagado por anticipado consumido | sobrevalorado | — | sobrevalorado |
| Ingreso recibido por anticipado ganado | — | sobrevalorado | subvalorado |
| Gasto devengado no pagado | — | subvalorado | sobrevalorado |
| Ingreso devengado no cobrado | subvalorado | — | subvalorado |
| Estimación de incobrables o depreciación | sobrevalorado | — | sobrevalorado |
| Provisión de vacaciones | — | subvalorado | sobrevalorado |

El chequeo es la ecuación contable: el error del patrimonio es igual al error del activo menos el
error del pasivo. Si no calza, falta un efecto.

---

## 8. Ejemplo resuelto · el cierre del Hostal Las Gaviotas

El Hostal Las Gaviotas cierra su año el **31-12-2026**. Antes de ajustar, su resultado es
**$3.900.000**. Los montos son netos salvo que se diga otra cosa. Pendientes del cierre:

1. El 01-08-2026 pagó un seguro de incendio de 12 meses: $1.236.000 neto más IVA.
2. El 01-11-2026 pagó por adelantado 6 meses del estacionamiento que arrienda: $930.000.
3. El 01-09-2026 recibió de una cafetería 6 meses de arriendo del local del primer piso: $2.580.000.
4. Los sueldos de diciembre, $3.150.000, se pagan el 05-01-2027.
5. La factura de luz de diciembre llegó el 31-12: $184.000 neto más IVA; vence el 15-01-2027.
6. El 01-11-2026 tomó un depósito a plazo de $5.000.000 al 0,4 % mensual simple, que vence el
   01-02-2027.
7. Clientes debe $6.420.000; se estima incobrable el 3 %. La estimación tiene hoy $45.000.

**Paso 1 · El pago del seguro, para ver de dónde parte.** El 01-08-2026 se registró:

| Cuenta | Debe | Haber |
|---|---|---|
| Seguro pagado por anticipado | 1.236.000 | |
| IVA crédito fiscal | 234.840 | |
| Banco | | 1.470.840 |

**Paso 2 · Los anticipados.** La planilla hace este cálculo en la hoja «Anticipados».

| Partida | Monto | Meses que cubre | Por mes | Meses al 31-12 | Devengado | Queda al 31-12 |
|---|---|---|---|---|---|---|
| Seguro (SPPA) | 1.236.000 | 12 | 103.000 | 5 | 515.000 | 721.000 |
| Estacionamiento (APPA) | 930.000 | 6 | 155.000 | 2 | 310.000 | 620.000 |
| Local arrendado (ARA, pasivo) | 2.580.000 | 6 | 430.000 | 4 | 1.720.000 | 860.000 |

**Paso 3 · Devengados y estimación.** Luz: IVA 184.000 × 19 % = $34.960; por pagar $218.960.
Interés del depósito: 5.000.000 × 0,4 % × 2 meses = **$40.000**. Incobrables: 6.420.000 × 3 % =
$192.600 requeridos; como ya hay $45.000, el ajuste es **$147.600** y Clientes queda en el balance a
su valor neto, $6.227.400.

**Paso 4 · El libro diario de los ajustes (31-12-2026).**

| N.º | Cuenta | Debe | Haber | Glosa |
|---|---|---|---|---|
| A1 | Gasto por seguro | 515.000 | | 5 meses de seguro |
| | Seguro pagado por anticipado | | 515.000 | |
| A2 | Gasto por arriendo | 310.000 | | 2 meses de estacionamiento |
| | Arriendo pagado por anticipado | | 310.000 | |
| A3 | Arriendo recibido por anticipado | 1.720.000 | | 4 meses del local |
| | Arriendo ganado | | 1.720.000 | |
| A4 | Gasto en sueldos | 3.150.000 | | sueldos de diciembre |
| | Sueldos por pagar | | 3.150.000 | |
| A5 | Gasto en electricidad | 184.000 | | luz de diciembre |
| | IVA crédito fiscal | 34.960 | | |
| | Cuentas por pagar | | 218.960 | |
| A6 | Intereses por cobrar | 40.000 | | 2 meses del depósito |
| | Intereses ganados | | 40.000 | |
| A7 | Gasto por incobrables | 147.600 | | estimación al 3 % |
| | Estimación de deudores incobrables | | 147.600 | |
| | **Totales** | **6.101.560** | **6.101.560** | cuadra |

Ningún ajuste toca Banco.

**Paso 5 · El efecto en el resultado.**

| | Monto |
|---|---|
| Resultado antes de ajustes | 3.900.000 |
| (−) Gastos de los ajustes (515.000 + 310.000 + 3.150.000 + 184.000 + 147.600) | −4.306.600 |
| (+) Ingresos de los ajustes (1.720.000 + 40.000) | +1.760.000 |
| **Resultado ajustado** | **1.353.400** |

Los ajustes bajan el resultado en $2.546.600.

**Cómo se lee.** El año del hostal fue bastante peor de lo que mostraba la cuenta corriente: casi dos
tercios de la utilidad aparente eran sueldos de diciembre sin pagar, seguro y estacionamiento ya
consumidos. Si la dueña pensaba repartirse $2.000.000 de utilidades, con el resultado ajustado eso
es más que toda la utilidad del año. En el balance, en cambio, aparecen $721.000 y $620.000 de
servicios ya pagados que el hostal todavía va a usar, y $860.000 de arriendo que le debe a la
cafetería en meses de local.

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Registrar como gasto todo el pago anticipado | Un pago por meses futuros es un activo; al cierre pasa a gasto solo lo consumido |
| Registrar como ingreso un cobro anticipado | Mientras no se preste el servicio, es un pasivo (le debes el servicio al cliente) |
| Contar mal los meses consumidos | Del 01-08 al 31-12 son 5 meses: cuenta agosto, septiembre, octubre, noviembre y diciembre |
| Repartir el IVA del seguro entre los meses | El crédito fiscal completo va el día de la factura; se reparte solo el neto |
| Poner Banco en un asiento de ajuste | El ajuste no mueve plata; si aparece Banco, es un pago o un cobro |
| Invertir Debe y Haber en el ARA | Al ganar el arriendo, el pasivo baja (Debe) y el ingreso sube (Haber) |
| Registrar otra vez el gasto al pagar un devengado | Al pagar se salda el por pagar; el gasto ya está en su período |
| Cargar la estimación completa sin mirar su saldo | El ajuste es lo requerido menos lo que ya tiene la estimación |
| Llevar a resultado el castigo de un cliente | El castigo rebaja Estimación y Clientes; la pérdida ya se reconoció al estimar |
| Registrar como gasto el sueldo líquido | El gasto es el bruto más los aportes del empleador; el líquido es solo lo que se paga |

---

## 10. Práctica

Diez ejercicios: 5.1 a 5.4 básicos, 5.5 a 5.8 intermedios, 5.9 y 5.10 de desafío. Escribe cada
asiento con fecha, cuentas, Debe, Haber y glosa, y comprueba que cuadre. Las pautas están en la
sección 11.

**5.1 · La peluquería canina (básico).** En abril de 2026 la peluquería «Patitas» prestó servicios
por $2.460.000, de los que cobró $1.980.000 en abril (el resto se cobra en mayo). Además cobró
$310.000 de servicios de marzo y recibió $240.000 de un cliente por un paquete de baños de mayo.
Pagó los sueldos de abril, $1.150.000, y $360.000 del arriendo de mayo; el arriendo de abril
($360.000) lo había pagado en marzo. Usó $185.000 de insumos comprados y pagados en marzo, y la
cuenta de agua de abril ($42.000) se paga en mayo. Sin IVA. Calcula el resultado de abril con base
caja y con base devengada, y explica la diferencia.

**5.2 · El seguro de la flota (básico).** El 01-05-2026 una empresa de reparto paga con transferencia
un seguro de 12 meses por $1.548.000 neto más IVA. Registra el pago y el ajuste al 30-09-2026.
¿Cuánto queda en Seguro pagado por anticipado?

**5.3 · El taller de música (básico).** El 01-03-2026 una academia cobra por adelantado $1.380.000 por
un taller de 6 meses (marzo a agosto). Sin IVA. Registra el cobro y el ajuste al 30-06-2026. ¿Qué
cuenta muestra el balance al 30-06 y por qué es un pasivo?

**5.4 · Cuatro pendientes (básico).** Al 31-05-2026 una mueblería tiene: (a) sueldos de mayo por
$2.240.000 que paga el 03-06; (b) $18.500 de intereses ganados en un depósito, que cobra al
vencimiento; (c) un anticipo de $650.000 cobrado el 20-05 por un mueble que entrega en junio; (d) la
factura del gas de mayo, $96.000 neto más IVA, que vence el 12-06. Di a qué familia pertenece cada
uno, registra los ajustes que correspondan y calcula el efecto en el resultado de mayo.

**5.5 · Pagado y anotado como gasto (intermedio).** El 01-10-2026 una empresa paga $2.720.000 por 8
meses de arriendo de una bodega (octubre a mayo) y lo registra entero como Gasto por arriendo. Al
31-12-2026, ¿qué ajuste hace? Compáralo con el ajuste que haría si lo hubiera registrado como activo
y comprueba que los saldos finales son iguales.

**5.6 · La planilla de sueldos (intermedio).** Las remuneraciones brutas de mayo de un taller son
$4.860.000. Los descuentos al trabajador son $1.003.590 de cotizaciones previsionales y de salud y
$41.200 de impuesto único; los aportes del empleador suman $145.800. Todo se paga en junio. Registra
el devengo al 31-05. ¿Cuánto cuestan las remuneraciones a la empresa, cuánto reciben los
trabajadores y qué porcentaje del costo es el líquido?

**5.7 · Incobrables por antigüedad (intermedio).** Al 31-12-2026 los clientes de una distribuidora
se reparten así: al día $8.400.000 (se estima incobrable el 1 %), de 1 a 30 días de atraso
$2.150.000 (4 %), de 31 a 90 días $960.000 (15 %) y más de 90 días $380.000 (50 %). La estimación
tiene un saldo de $210.000. (a) Calcula la estimación requerida, el ajuste y el valor neto de
clientes. (b) El 15-01-2027 se castiga un cliente de $130.000. Registra el castigo y muestra que el
valor neto de clientes no cambia.

**5.8 · Las vacaciones pendientes (intermedio).** Al 31-12-2026 un estudio tiene cuatro trabajadores
con días de vacaciones ganados y no tomados: Ana, 11 días a un costo diario de $26.000; Benjamín, 7,5
días a $31.000; Carla, 15 días a $22.500, y Diego, 4 días a $40.000. La provisión tiene $742.000.
Calcula la provisión requerida y el ajuste. En enero Diego toma sus 4 días: ¿qué asiento se hace y
cuánto queda en la provisión?

**5.9 · Lo que se olvidó (desafío).** Una empresa informó una utilidad de $5.240.000 y olvidó cinco
ajustes: $437.000 de seguro consumido, $915.000 de un arriendo recibido por anticipado ya ganado,
$1.285.000 de sueldos devengados, $74.000 de intereses por cobrar y $263.000 de incobrables. (a)
¿Cuál es la utilidad correcta? (b) ¿Cuánto está mal el activo, el pasivo y el patrimonio, y en qué
sentido? Comprueba con la ecuación contable. (c) El gerente cobra un bono del 8 % de la utilidad.
¿Cuánto se le pagó de más?

**5.10 · Leer los ajustes desde dos balances (desafío).** Estos son algunos saldos del balance de
comprobación de una empresa al 31-12-2026, antes y después de los ajustes:

| Cuenta | Antes | Después |
|---|---|---|
| Seguro pagado por anticipado | 2.040.000 | 1.530.000 |
| Arriendo recibido por anticipado | 3.780.000 | 2.520.000 |
| Sueldos por pagar | 0 | 1.910.000 |
| Estimación de deudores incobrables | 128.000 | 317.000 |
| Intereses por cobrar | 0 | 57.500 |
| Depreciación acumulada | 4.920.000 | 5.535.000 |

(a) Escribe los seis ajustes. (b) La póliza se pagó entera este año y cubre 12 meses; el arriendo se
cobró de una vez por un contrato de 12 meses. ¿Desde qué fecha corre cada uno? (c) ¿Cuánto cambian
los ajustes el resultado del año?

---

## 11. Pautas

**5.1.** Base caja: entran 1.980.000 + 310.000 + 240.000 = **$2.530.000** y salen 1.150.000 +
360.000 = **$1.510.000**: resultado **$1.020.000**. Base devengada: ingresos **$2.460.000** (todo lo
prestado en abril, cobrado o no); gastos 1.150.000 + 360.000 (arriendo de abril) + 185.000 + 42.000 =
**$1.737.000**: resultado **$723.000**. La caja muestra $297.000 más por dos razones.
Por el lado de los ingresos, cobró $550.000 de marzo y de mayo pero dejó $480.000 de abril por
cobrar: $70.000 a favor de la caja. Por el lado de los gastos, no ve los insumos pagados en marzo ni
el agua que se paga en mayo: $227.000 más. El arriendo se compensa (paga mayo, pero no abril).
Abril, con lo que hizo en abril, ganó $723.000.

**5.2.** Pago (01-05-2026): Seguro pagado por anticipado $1.548.000 y IVA crédito fiscal $294.120 al
Debe, Banco $1.842.120 al Haber. Por mes: $129.000. Ajuste (30-09-2026), 5 meses de mayo a
septiembre: Gasto por seguro (D) contra Seguro pagado por anticipado (H) por **$645.000**. Quedan
**$903.000**, los 7 meses que la flota todavía tiene cubiertos.

**5.3.** Cobro (01-03-2026): Banco (D) contra Ingreso recibido por anticipado (H) por $1.380.000.
Por mes: $230.000. Ajuste (30-06-2026), marzo a junio: Ingreso recibido por anticipado (D) contra
Ingresos por servicios (H) por **$920.000**. El balance muestra **$460.000** de Ingreso recibido por
anticipado: es pasivo porque la academia le debe a sus alumnos dos meses de taller (o la plata, si
no lo dicta).

**5.4.** (a) Gasto devengado no pagado: Gasto en sueldos (D) contra Sueldos por pagar (H), $2.240.000.
(b) Ingreso devengado no cobrado: Intereses por cobrar (D) contra Intereses ganados (H), $18.500. (c)
Ingreso recibido por anticipado: **no hay ajuste**; el mueble no se ha entregado y el anticipo de
$650.000 sigue en el pasivo. (d) Gasto devengado no pagado: Gasto en gas $96.000 e IVA crédito
fiscal $18.240 al Debe, Cuentas por pagar $114.240 al Haber. El resultado de mayo baja en
**$2.317.500** (−2.240.000 + 18.500 − 96.000). El IVA no es gasto.

**5.5.** Por mes $340.000; consumido al 31-12 (octubre a diciembre) $1.020.000; no consumido
**$1.700.000**. Como se registró todo como gasto, el ajuste devuelve al activo lo no consumido:
Arriendo pagado por anticipado (D) contra Gasto por arriendo (H), $1.700.000. Si se hubiera
registrado como activo, el ajuste sería Gasto por arriendo (D) contra Arriendo pagado por
anticipado (H), $1.020.000. En los dos casos el año termina con $1.020.000 de gasto y $1.700.000 de
activo: el método cambia el ajuste, no el resultado.

**5.6.** Líquido: 4.860.000 − 1.003.590 − 41.200 = **$3.815.210**.

| Cuenta | Debe | Haber |
|---|---|---|
| Gasto en remuneraciones | 4.860.000 | |
| Aportes del empleador | 145.800 | |
| Retenciones previsionales por pagar | | 1.149.390 |
| Impuesto único por pagar | | 41.200 |
| Remuneraciones por pagar | | 3.815.210 |
| **Totales** | **5.005.800** | **5.005.800** |

Las remuneraciones le cuestan a la empresa **$5.005.800**; los trabajadores reciben $3.815.210, el
**76,2 %** del costo. Para decidir si contratar a alguien se mira el costo total, no el líquido.

**5.7.** (a) Requerida por tramo: **$84.000**, **$86.000**, **$144.000** y **$190.000**; total
**$504.000**. Ajuste: 504.000 − 210.000 = **$294.000** (Gasto por incobrables contra Estimación).
Clientes $11.890.000 menos la estimación: valor neto **$11.386.000**. (b) Castigo (15-01-2027):
Estimación de deudores incobrables (D) contra Clientes (H), $130.000. Quedan Clientes $11.760.000 y
Estimación $374.000: el neto sigue en $11.386.000 y el resultado de enero no cambia. Fíjate en que la
deuda de más de 90 días (poco más del 3 % de los saldos) explica más de un tercio de la estimación:
cobrar a tiempo vale.

**5.8.** Ana $286.000, Benjamín $232.500, Carla $337.500, Diego $160.000: provisión requerida
**$1.016.000**. Ajuste: 1.016.000 − 742.000 = **$274.000** (Gasto en vacaciones contra Provisión de
vacaciones). Cuando Diego toma sus días: Provisión de vacaciones (D) contra Remuneraciones por pagar
(H), $160.000; sin gasto nuevo. Quedan **$856.000** en la provisión.

**5.9.** (a) Efecto: −437.000 + 915.000 − 1.285.000 + 74.000 − 263.000 = −996.000. La utilidad
correcta es **$4.244.000**. (b) Activo **sobrevalorado en $626.000** (seguro 437.000 más incobrables
263.000, menos los intereses por cobrar 74.000 que faltan). Pasivo **subvalorado en $370.000**
(faltan 1.285.000 de sueldos por pagar y sobran 915.000 de arriendo por anticipado). Patrimonio
sobrevalorado en **$996.000**: 626.000 + 370.000 = 996.000, la ecuación calza. (c) Bono pagado:
$419.200; correcto: $339.520; se pagaron **$79.680** de más. Un bono atado a la utilidad exige que
los ajustes estén hechos antes de calcularlo.

**5.10.** (a) Los ajustes son las diferencias:

| Ajuste | Debe | Haber | Monto |
|---|---|---|---|
| Seguro consumido | Gasto por seguro | Seguro pagado por anticipado | 510.000 |
| Arriendo ganado | Arriendo recibido por anticipado | Arriendo ganado | 1.260.000 |
| Sueldos devengados | Gasto en sueldos | Sueldos por pagar | 1.910.000 |
| Incobrables | Gasto por incobrables | Estimación de deudores incobrables | 189.000 |
| Intereses devengados | Intereses por cobrar | Intereses ganados | 57.500 |
| Depreciación | Gasto por depreciación | Depreciación acumulada | 615.000 |

(b) La póliza vale $170.000 al mes (2.040.000 / 12); se consumieron 510.000, o sea 3 meses: corre
desde el **01-10-2026**. El arriendo vale $315.000 al mes; se ganaron 1.260.000, 4 meses: corre
desde el **01-09-2026**. (c) −510.000 + 1.260.000 − 1.910.000 − 189.000 + 57.500 − 615.000: el
resultado baja en **$1.906.500**.

---

## 12. Caso integrador · Estampa Sur, el arriendo y el seguro de marzo

> El caso sigue el mes de marzo del taller de serigrafía Estampa Sur. La unidad 2 dejó los 12
> asientos del mes y la unidad 4 la depreciación de las dos máquinas. Las cifras salen de
> `verificacion/caso_estampa_sur_contable.py`.

**Lo que recibe.** El balance al 1 de marzo trae **$580.000** de Arriendo pagado por anticipado: el
arriendo de marzo, pagado en febrero. En marzo, el asiento 8 pagó **$1.740.000** por el arriendo de
abril a junio y el asiento 9 pagó el seguro anual: **$948.000** neto, con $180.120 de IVA crédito
fiscal que entró completo ese día.

**Pregunta.** ¿Qué ajustes hace el taller al 31-03 y qué queda pagado por anticipado?

**Desarrollo.**

| Partida | Antes del ajuste | Devengado en marzo | Queda al 31-03 |
|---|---|---|---|
| Arriendo pagado por anticipado | 2.320.000 (580.000 + 1.740.000) | 580.000 (marzo) | 1.740.000 (abril a junio) |
| Seguro pagado por anticipado | 948.000 | 79.000 (948.000 / 12) | 869.000 (11 meses) |

| N.º | Fecha | Cuenta | Debe | Haber | Glosa |
|---|---|---|---|---|---|
| A5.1 | 31-03 | Costo indirecto: arriendo del taller | 580.000 | | arriendo de marzo |
| | | Arriendo pagado por anticipado | | 580.000 | |
| A5.2 | 31-03 | Costo indirecto: seguro | 79.000 | | un mes de seguro |
| | | Seguro pagado por anticipado | | 79.000 | |

**Por qué «costo indirecto» y no «gasto».** Estampa Sur fabrica: el arriendo del taller y el seguro
de las máquinas son costos de producir, no gastos de administración. Entran al costo de las prendas
y llegan al estado de resultados por el costo de ventas, a medida que las prendas se venden
(unidades 9 a 11). En una empresa de servicios, como el hostal, serían gasto del período.

**Lectura.** Los dos ajustes cargan **$659.000** a marzo. Sin ellos, el balance mostraría $659.000 de
activos que ya se consumieron y el costo del mes saldría bajo en lo mismo. Al 31-03 quedan
$2.609.000 pagados por anticipado: tres meses de arriendo y once de seguro que el taller usará sin
volver a pagar.

**Lo que pasa a la siguiente.** Los $580.000 y $79.000 se suman a los sueldos y a la depreciación
para formar los costos indirectos fijos del mes, **$3.849.833** (unidad 9). La unidad 6 hace el otro
ajuste de cierre del caso: el interés del préstamo devengado en marzo.

---

## 13. Para seguir

**En los libros del ramo.**

- Gálvez y Clarke, *Contabilidad financiera para la dirección de empresas*, Ediciones UC (texto
  obligatorio del programa). Sus capítulos sobre la base devengada y el cierre, y sobre cuentas por
  cobrar e incobrables.
- Weygandt, Kimmel y Kieso, *Accounting Principles*, 12.ª ed., Wiley, 2014 (complementario del
  programa): los capítulos de ajustes de cuentas y de cuentas por cobrar.

**Abierto y gratis.**

- OpenStax, *Principles of Accounting, Volume 1: Financial Accounting*, en inglés, capítulo 4 (el
  proceso de ajuste: anticipados, devengados y balance de comprobación ajustado) y capítulo 9
  (incobrables por porcentaje y por antigüedad). Licencia CC BY-NC-SA 4.0:
  https://openstax.org/books/principles-financial-accounting/pages/4-why-it-matters

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame cinco pendientes de cierre de una empresa
de servicios, mezclando anticipados, devengados y una estimación; déjame escribir los ajustes y
corrígeme asiento por asiento».
