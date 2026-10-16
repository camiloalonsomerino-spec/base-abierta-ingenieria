---
ramo: Contabilidad y Costos
unidad: 3
titulo: IVA
version: 0.1 (16-10-2026)
requiere: [02-partida-doble]
alimenta: [04-depreciacion, 07-inventarios, 08-razones-financieras]
verificacion: verificacion/u03_iva.py
---

# Unidad 3 · IVA

**Qué vas a poder hacer.** Separar el neto y el IVA de cualquier precio; registrar compras, ventas y
devoluciones con su IVA en la cuenta que corresponde; liquidar el IVA de un mes (cuánto se paga o
cuánto remanente queda) y arrastrar el remanente a los meses siguientes; reconocer cuándo el IVA
deja de ser recuperable y pasa a ser costo, y usar todo eso para fijar un precio o elegir un
proveedor.

**Lo que necesitas antes.** La partida doble de la unidad 2: cada asiento tiene un Debe y un Haber
que suman lo mismo, el activo aumenta por el Debe y el pasivo por el Haber.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica. La planilla
`planillas/u03_iva.xlsx` trae el ejemplo, el ejercicio 3.9 y el caso con fórmulas.

---

## 1. La idea · un impuesto al valor que agrega cada etapa

El IVA (impuesto al valor agregado) lo paga el **consumidor final**: en Chile es el 19 % de lo que
paga por el producto, sin IVA. Pero el fisco no lo cobra de una sola vez en la caja de la tienda.
Lo cobra **en cada etapa de la cadena**, y cada empresa entrega solo el 19 % del valor que ella
agregó.

El mecanismo tiene dos piezas:

- Cuando una empresa **vende**, le cobra al cliente el 19 % sobre el precio neto. Ese IVA no es suyo:
  lo recauda para el fisco. Se llama **débito fiscal**.
- Cuando una empresa **compra** a otra empresa (con factura), paga el 19 % sobre el neto. Ese IVA lo
  puede descontar de lo que debe entregar. Se llama **crédito fiscal**.

Cada mes la empresa entrega la diferencia: débito menos crédito.

$$\text{IVA del mes} = \text{débito fiscal} - \text{crédito fiscal} = 0{,}19 \cdot (\text{ventas netas} - \text{compras netas})$$

**Por qué funciona.** Ventas menos compras es justamente el valor que la empresa agregó. Si se suman
todas las etapas, las compras de una son las ventas de la anterior y se cancelan: queda el 19 % del
precio final, el que paga el consumidor. El ejercicio 3.4 lo comprueba con una cadena de tres
etapas.

**Por qué se cobra así y no solo al final.** Porque cada empresa tiene interés en exigir factura a
su proveedor (sin factura no hay crédito), y eso deja registrada toda la cadena. Si alguien evade en
una etapa, la siguiente igual paga sobre su venta completa, así que el fisco pierde menos.

**Lo que esto significa para la contabilidad.** Para una empresa que recupera el IVA, el impuesto
**no es costo ni ingreso**. El IVA de una compra no forma parte del costo de la mercadería (ni, por
lo tanto, del costo de ventas), y el IVA de una venta no forma parte de los ingresos. Es plata que
pasa por la empresa: un derecho contra el fisco cuando compra y una deuda con el fisco cuando vende.

---

## 2. Neto, IVA y bruto

- **Neto:** el precio sin IVA. Es el que va a los ingresos, al costo y a los inventarios.
- **Bruto** (o precio con IVA incluido): lo que efectivamente se paga o se cobra.

$$\text{bruto} = \text{neto} \times 1{,}19 \qquad \text{neto} = \frac{\text{bruto}}{1{,}19} \qquad \text{IVA} = \text{bruto} \times \frac{19}{119}$$

En un enunciado, «$500.000 + IVA» es un neto (hay que sumarle el 19 %) y «$595.000 IVA incluido» es
un bruto (hay que sacarle el IVA dividiendo por 1,19).

**El error clásico** es sacar el IVA de un bruto multiplicando por 0,19. El 19 % se calcula sobre el
neto, no sobre el bruto: el IVA es 19/119 del bruto, es decir un 15,97 % del total. El ejercicio 3.1
mide cuánto se equivoca quien lo hace mal.

En una factura real los montos van en pesos enteros; en esta unidad el IVA se redondea a peso en
cada documento.

---

## 3. Las cuentas del IVA

| Cuenta | Qué es | Naturaleza | Aumenta por |
|---|---|---|---|
| IVA crédito fiscal | El IVA pagado en compras, que el fisco descuenta | Activo | Debe |
| IVA débito fiscal | El IVA cobrado en ventas, que se debe al fisco | Pasivo | Haber |
| IVA por pagar | La diferencia que se entrega al fisco tras la liquidación | Pasivo | Haber |
| IVA remanente | Crédito que sobró y se usa el mes siguiente | Activo | Debe |

Algunas empresas llevan las dos primeras cuentas por separado todo el mes y las cierran al final;
otras llevan una sola cuenta de IVA que termina deudora (remanente) o acreedora (por pagar). El
resultado es el mismo. En esta base se llevan separadas, porque así se ve qué viene de compras y
qué de ventas.

**Compra con IVA** (la mercadería entra al neto; el IVA va aparte):

| Cuenta | Debe | Haber |
|---|---|---|
| Mercaderías (o el gasto o el activo que se compra) | neto | |
| IVA crédito fiscal | 0,19 × neto | |
| Banco, Caja o Proveedores | | bruto |

**Venta con IVA** (el ingreso es el neto; el IVA es una deuda):

| Cuenta | Debe | Haber |
|---|---|---|
| Banco, Caja o Clientes | bruto | |
| Ventas | | neto |
| IVA débito fiscal | | 0,19 × neto |

Si la empresa lleva inventario permanente, junto con la venta se registra su costo (Debe Costo de
ventas, Haber Mercaderías), **sin IVA**: el IVA de esa mercadería ya quedó en el crédito fiscal el
día que se compró.

### Qué lleva IVA y qué no, dentro de un mismo mes

Lleva IVA lo que se compra o se vende con factura afecta: mercaderías, insumos, servicios de otras
empresas (luz, internet, mantención), activos fijos. **No lleva IVA** el pago de sueldos (no es una
compra a una empresa), el pago de una deuda o el cobro a un cliente (el IVA ya se registró en la
compra o la venta original), ni un préstamo bancario recibido (no es una venta).

### Devoluciones

Una devolución anula una parte de la operación original, IVA incluido. El proveedor emite una nota
de crédito y la empresa reversa el crédito fiscal en proporción; si devuelve un cliente, se reversa
el débito fiscal. Si la mercadería vendida vuelve a bodega en buen estado, también se reversa su
costo de ventas.

---

## 4. La liquidación del mes

Al cierre del mes se comparan los saldos de las dos cuentas:

$$\text{saldo} = \text{débito fiscal} - \text{crédito fiscal} - \text{remanente del mes anterior}$$

- Si el saldo es **positivo**, la empresa tiene **IVA por pagar** y lo entrega al mes siguiente. En
  Chile se declara y se paga en la declaración mensual del SII (el formulario 29), dentro del mes
  siguiente.
- Si es **negativo**, queda un **remanente** de crédito fiscal: no se paga nada ese mes y el
  remanente se descuenta del débito del mes siguiente. Si tampoco alcanza, sigue al otro.

El asiento de liquidación deja en cero las dos cuentas del mes y abre la que corresponda:

| Si hay IVA por pagar | Debe | Haber | | Si queda remanente | Debe | Haber |
|---|---|---|---|---|---|---|
| IVA débito fiscal | su saldo | | | IVA débito fiscal | su saldo | |
| IVA crédito fiscal | | su saldo | | IVA remanente | la diferencia | |
| IVA por pagar | | la diferencia | | IVA crédito fiscal | | su saldo |

**Por qué aparece un remanente.** Porque el crédito sigue a las compras y el débito a las ventas, y
no tienen por qué coincidir en el mes. El caso típico es la compra de un activo fijo caro: una
máquina de $14.300.000 trae $2.717.000 de IVA de una vez, aunque la máquina se use durante años. El
remanente no es una pérdida: es IVA que la empresa ya pagó y que recupera pagando menos en los meses
que vienen. Lo que sí cuesta es la **caja**: esa plata sale el día de la compra y vuelve de a poco.

---

## 5. Cuándo el IVA deja de ser recuperable

Todo lo anterior supone que la empresa vende con IVA y compra con factura. Si una de las dos cosas
falla, el IVA de la compra **no se recupera y pasa a ser parte del costo**:

- **Compra sin factura.** El crédito fiscal se respalda con la factura de la compra. Si el
  proveedor entrega una boleta, la empresa paga el IVA igual (va dentro del precio) pero no lo puede
  descontar: el costo es el bruto completo.
- **Operaciones exentas o no afectas.** La ley define algunas ventas que no llevan IVA. Quien las
  hace no genera débito fiscal y, como regla general, tampoco puede usar como crédito el IVA de las
  compras que destina a ellas: ese IVA se queda en el costo. Cuáles operaciones son exentas lo fija
  la ley y no entra en este ramo; aquí basta con reconocer el efecto.
- **El consumidor final** está siempre en este caso: paga el IVA y no tiene a quién descontarlo. Por
  eso es él quien soporta el impuesto.

**Cuándo NO aplica lo de esta unidad.** Una persona que no es empresa no lleva débito ni crédito.
Una empresa que solo hace ventas exentas registra sus compras al bruto, como costo. Y los montos de
los ejercicios de otras unidades que dicen «no considere IVA» se registran al neto, sin cuentas de
IVA.

---

## 6. Ejemplo resuelto · el IVA de mayo de un taller de bicicletas

Ciclo Austral repara bicicletas y vende repuestos. En mayo de 2026:

1. **04-05.** Compra repuestos por **$1.840.000 + IVA**; paga la mitad por transferencia y la otra mitad
   a 30 días.
2. **08-05.** Devuelve repuestos fallados por **$107.100 IVA incluido**; el proveedor rebaja la deuda.
3. **12-05.** Compra un soporte de taller (herramienta que durará años) por **$620.000 + IVA**, por
   transferencia.
4. **20-05.** Sus ventas del mes (reparaciones y repuestos) suman **$3.260.000 + IVA**: 70 % al
   contado y 30 % a crédito a empresas en convenio. Los repuestos vendidos le habían costado
   **$1.130.000**.
5. **28-05.** Paga la luz y el internet: **$142.800 IVA incluido**.
6. Se liquida el IVA al 31-05 y se paga en junio.

**Paso 1 · Separar neto e IVA de cada documento.**

| Documento | Neto | IVA | Bruto |
|---|---|---|---|
| Compra de repuestos | 1.840.000 | 349.600 | 2.189.600 |
| Devolución (107.100 / 1,19) | 90.000 | 17.100 | 107.100 |
| Soporte de taller | 620.000 | 117.800 | 737.800 |
| Ventas del mes | 3.260.000 | 619.400 | 3.879.400 |
| Luz e internet (142.800 / 1,19) | 120.000 | 22.800 | 142.800 |

**Paso 2 · El libro diario.**

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 04-05 | Mercaderías (repuestos) | 1.840.000 |  |
|  |  | IVA crédito fiscal | 349.600 |  |
|  |  | Banco |  | 1.094.800 |
|  |  | Proveedores |  | 1.094.800 |
| | | *Compra de repuestos, mitad por transferencia y mitad a 30 días* | | |
| 2 | 08-05 | Proveedores | 107.100 |  |
|  |  | Mercaderías (repuestos) |  | 90.000 |
|  |  | IVA crédito fiscal |  | 17.100 |
| | | *Devolución de repuestos fallados (nota de crédito del proveedor)* | | |
| 3 | 12-05 | Herramientas y equipos | 620.000 |  |
|  |  | IVA crédito fiscal | 117.800 |  |
|  |  | Banco |  | 737.800 |
| | | *Compra de un soporte de taller por transferencia* | | |
| 4 | 20-05 | Banco | 2.715.580 |  |
|  |  | Clientes | 1.163.820 |  |
|  |  | Ventas |  | 3.260.000 |
|  |  | IVA débito fiscal |  | 619.400 |
| | | *Ventas del mes: 70 % al contado, 30 % a crédito a empresas en convenio* | | |
| 5 | 20-05 | Costo de ventas | 1.130.000 |  |
|  |  | Mercaderías (repuestos) |  | 1.130.000 |
| | | *Costo de los repuestos vendidos (sin IVA)* | | |
| 6 | 28-05 | Gasto en luz e internet | 120.000 |  |
|  |  | IVA crédito fiscal | 22.800 |  |
|  |  | Banco |  | 142.800 |
| | | *Pago de luz e internet, IVA incluido* | | |
| 7 | 31-05 | IVA débito fiscal | 619.400 |  |
|  |  | IVA crédito fiscal |  | 473.100 |
|  |  | IVA por pagar |  | 146.300 |
| | | *Liquidación del IVA de mayo* | | |
| 8 | 12-06 | IVA por pagar | 146.300 |  |
|  |  | Banco |  | 146.300 |
| | | *Pago del IVA de mayo en la declaración mensual* | | |

Cada asiento cuadra: en el 1, 1.840.000 + 349.600 = 1.094.800 + 1.094.800.

**Paso 3 · Las cuentas T del IVA, antes de liquidar.**

| IVA crédito fiscal · Debe | IVA crédito fiscal · Haber | IVA débito fiscal · Debe | IVA débito fiscal · Haber |
|---|---|---|---|
| (1) 349.600 | (2) 17.100 |  | (4) 619.400 |
| (3) 117.800 |  |  |  |
| (6) 22.800 |  |  |  |
| Suma 490.200 | Suma 17.100 |  | Suma 619.400 |
| **Saldo deudor 473.100** |  |  | **Saldo acreedor 619.400** |

**Paso 4 · La liquidación.** Débito 619.400 menos crédito 473.100 = **$146.300 de IVA por pagar**
(asiento 7), que se paga en junio (asiento 8).

**Comprobación por el valor agregado.** Ventas netas 3.260.000 menos compras netas
(1.840.000 − 90.000 + 620.000 + 120.000) = 770.000; y 19 % de 770.000 = 146.300. ✓

**Cómo se lee.**

- El IVA no tocó el resultado: el margen bruto del mes es 3.260.000 − 1.130.000 = **$2.130.000**,
  calculado con netos. Quien lo calcule con brutos infla las ventas en un 19 %.
- Los $146.300 no son un gasto del taller: es lo que cobró por cuenta del fisco y aún no entrega.
  Por eso, al 31-05, el banco tiene plata que no es del taller. Si el dueño mira solo el saldo del
  banco para decidir cuánto retirar, se gasta el IVA de junio.
- El soporte de taller trajo $117.800 de crédito, que se descontó entero en mayo aunque el soporte
  dure años. Si el soporte hubiera sido mucho más caro, mayo habría cerrado con remanente (el caso
  de la sección 10).

---

## 7. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Sacar el IVA de un precio con IVA incluido multiplicando por 0,19 | Neto = bruto / 1,19; el IVA es 19/119 del bruto |
| Cargar el IVA de la compra a Mercaderías (o al activo) | El IVA recuperable va a IVA crédito fiscal; el inventario y el activo van al neto |
| Registrar las ventas por el bruto | Ventas va al neto; el IVA va a IVA débito fiscal |
| Poner el IVA de la compra en IVA débito fiscal (o al revés) | Compra → crédito (activo, Debe); venta → débito (pasivo, Haber) |
| Calcular el costo de ventas con IVA | El costo de ventas es el costo neto de lo vendido |
| Ponerle IVA a los sueldos, a un préstamo o al cobro de un cliente | Solo lleva IVA una compra o venta con factura afecta |
| Olvidar el IVA en una devolución | La nota de crédito reversa el neto y su IVA; si vuelve la mercadería, también el costo |
| Pagar el remanente o perderlo | El remanente es un activo que se descuenta del débito del mes siguiente |
| Usar como crédito el IVA de una compra con boleta | Sin factura no hay crédito: ese IVA es costo |
| Invertir Debe y Haber en la liquidación | El débito (pasivo) se cierra por el Debe; el crédito (activo) por el Haber |

---

## 8. Práctica

Diez ejercicios: 3.1 a 3.4 básicos, 3.5 a 3.8 intermedios, 3.9 y 3.10 de desafío. Tasa del IVA:
19 %. Cada IVA se redondea a peso. Las pautas están en la sección 9.

**3.1 · Neto, IVA y bruto (básico).** (a) Un taladro cuesta $46.000 + IVA: ¿cuánto es el IVA y cuánto
se paga? (b) Una cotización dice $83.300 IVA incluido: ¿cuál es el neto y cuál el IVA? (c) Lo mismo
para $1.249.500 IVA incluido. (d) Si alguien saca el IVA de (b) multiplicando 83.300 por 0,19,
¿cuánto le da y por cuánto se equivoca?

**3.2 · La compra de una librería (básico).** El 02-04 una librería compra cuadernos por $2.350.000
+ IVA; paga el 30 % por transferencia y el resto a 60 días. Calcula el IVA, el total de la factura y
registra el asiento.

**3.3 · La venta (básico).** El 15-04 la librería de 3.2 vende el 60 % de los cuadernos con un
margen del 40 % sobre el costo, + IVA. El cliente paga la mitad al contado y la otra mitad a
crédito. Registra la venta y su costo, y calcula el margen bruto.

**3.4 · La cadena de un chaleco (básico).** Una hilandería (sin compras con IVA) vende hilado a una
tejedora en $410.000 neto. La tejedora vende los chalecos a una tienda en $1.160.000 neto, y la
tienda los vende a sus clientes en $1.870.000 neto. ¿Cuánto IVA le entrega al fisco cada empresa?
Comprueba que el total es el 19 % del precio final y que cada una paga el 19 % de su valor agregado.
¿Cuánto pagan los consumidores en total?

**3.5 · Devoluciones (intermedio).** Con la librería de 3.2 y 3.3: (a) el 05-04 devuelve al
proveedor cuadernos por $71.400 IVA incluido, que se rebajan de la deuda; (b) el 18-04 el cliente de
3.3 devuelve el 5 % de lo que compró, en perfecto estado, y se le rebaja lo que debe. Registra los
asientos. Con las cuatro operaciones de abril (3.2, 3.3 y estas dos), ¿cuánto queda en IVA crédito y
en IVA débito, y cómo cierra el mes?

**3.6 · La liquidación de un almacén (intermedio).** En agosto, un almacén tuvo ventas netas por
$6.420.000; compró mercaderías por $4.150.000 neto, pagó gas y luz por $236.000 neto y la mantención
de la cámara de frío por $310.000 neto (todo con factura), y pagó sueldos por $1.240.000. Calcula el
débito, el crédito y el IVA del mes; registra la liquidación al 31-08 y el pago del 12-09. ¿Cuánto
pagaría si se equivocara y le pusiera IVA a los sueldos como si fueran crédito?

**3.7 · El remanente del elevador (intermedio).** Un taller mecánico vende en julio $2.940.000 neto,
compra repuestos por $1.310.000 neto y compra un elevador hidráulico por $5.640.000 neto. En agosto
vende $5.720.000 neto y compra repuestos por $1.490.000 neto. Liquida los dos meses con sus asientos.
¿Cuánto habría pagado en julio sin el elevador?

**3.8 · Factura o boleta (intermedio).** Una carpintería necesita 40 planchas de terciado. El
proveedor A vende a $18.500 + IVA cada una, con factura; el proveedor B vende a $21.200 cada una con
boleta (IVA incluido, sin derecho a crédito). (a) ¿Cuánto le cuestan las 40 planchas con cada
proveedor y a cuál le compra? (b) ¿Y si quien compra es una persona para su casa? (c) ¿Por qué
cambia la respuesta?

**3.9 · Tres meses de remanente (desafío).** Una florería abre en marzo y compra una cámara
refrigerada por $4.260.000 neto. Sus ventas netas son $1.820.000 en marzo, $2.630.000 en abril y
$4.960.000 en mayo; sus compras netas de flores e insumos, $1.160.000, $1.480.000 y $2.140.000.
Arma la tabla mes a mes (débito, crédito, remanente que llega, IVA a pagar, remanente que sigue) y
registra la liquidación de mayo. ¿Cuánto IVA pagó en los tres meses, y cuánto habría pagado sin la
cámara? Explica la diferencia.

**3.10 · El precio del pan amasado (desafío).** Una panadería vende el kilo de pan amasado a $2.400
con IVA incluido. Su costo es $1.500 neto por kilo, todo comprado con factura. El dueño cree que
gana $900 por kilo. (a) ¿Cuánto gana de verdad y qué margen sobre el costo es? (b) ¿A qué precio con
IVA tiene que vender para ganar un 40 % sobre el costo? (c) Con ese precio y 3.150 kilos al mes,
¿cuánto es el débito, el crédito y el IVA a pagar del pan? Compruébalo con el valor agregado.

---

## 9. Pautas

**3.1.** (a) IVA: 46.000 × 0,19 = **$8.740**; se pagan **$54.740**. (b) Neto: 83.300 / 1,19 =
**$70.000**; IVA **$13.300**. (c) Neto **$1.050.000**; IVA **$199.500**. (d) 83.300 × 0,19 =
$15.827: **$2.527** de más. Lectura: el 19 % se aplica sobre el neto; sobre un bruto, el IVA es
menos del 16 %.

**3.2.** IVA **$446.500**; total **$2.796.500**; por transferencia **$838.950** y a 60 días
**$1.957.550**.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 02-04 | Mercaderías | 2.350.000 |  |
|  |  | IVA crédito fiscal | 446.500 |  |
|  |  | Banco |  | 838.950 |
|  |  | Proveedores |  | 1.957.550 |
| | | *Compra de cuadernos, 30 % por transferencia y el resto a 60 días* | | |

Lectura: los cuadernos entran a bodega a $2.350.000; el IVA es un derecho contra el fisco, no
parte del inventario.

**3.3.** Costo de lo vendido: 60 % de 2.350.000 = **$1.410.000**. Venta neta: 1.410.000 × 1,4 =
**$1.974.000**; IVA **$375.060**; total **$2.349.060**, mitad al contado (**$1.174.530**) y mitad a
crédito.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 15-04 | Banco | 1.174.530 |  |
|  |  | Clientes | 1.174.530 |  |
|  |  | Ventas |  | 1.974.000 |
|  |  | IVA débito fiscal |  | 375.060 |
| | | *Venta del 60 % de los cuadernos, mitad al contado* | | |
| 2 | 15-04 | Costo de ventas | 1.410.000 |  |
|  |  | Mercaderías |  | 1.410.000 |
| | | *Costo de los cuadernos vendidos* | | |

Margen bruto: **$564.000**. Lectura: el margen del 40 % se aplica sobre el costo neto, y el IVA se
suma después; aplicarlo sobre un costo con IVA sube el precio sin razón.

**3.4.**

| Etapa | Compra neta | Venta neta | Valor agregado | Débito | Crédito | Paga al fisco |
|---|---|---|---|---|---|---|
| Hilandería | 0 | 410.000 | 410.000 | 77.900 | 0 | 77.900 |
| Tejedora | 410.000 | 1.160.000 | 750.000 | 220.400 | 77.900 | 142.500 |
| Tienda | 1.160.000 | 1.870.000 | 710.000 | 355.300 | 220.400 | 134.900 |
| **Total** |  |  | 1.870.000 |  |  | **355.300** |

El total, **$355.300**, es el 19 % de 1.870.000, y cada fila paga el 19 % de su valor agregado
(por ejemplo 0,19 × 750.000 = 142.500). Los consumidores pagan **$2.225.300**. Lectura: ninguna
empresa soporta el impuesto; cada una adelanta su parte y la recupera del siguiente, y el único que
no recupera es el consumidor.

**3.5.** (a) Neto 71.400 / 1,19 = **$60.000**, IVA **$11.400**. (b) Se reversa el 5 % de la venta:
neto **$98.700**, IVA **$18.753**, total **$117.453**; y vuelven a bodega cuadernos que costaron
**$70.500**.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 05-04 | Proveedores | 71.400 |  |
|  |  | Mercaderías |  | 60.000 |
|  |  | IVA crédito fiscal |  | 11.400 |
| | | *Devolución de cuadernos al proveedor* | | |
| 2 | 18-04 | Ventas | 98.700 |  |
|  |  | IVA débito fiscal | 18.753 |  |
|  |  | Clientes |  | 117.453 |
| | | *El cliente devuelve el 5 % de la venta del 15-04* | | |
| 3 | 18-04 | Mercaderías | 70.500 |  |
|  |  | Costo de ventas |  | 70.500 |
| | | *Los cuadernos devueltos vuelven a bodega a su costo* | | |

En abril quedan **$435.100** de crédito (446.500 − 11.400) y **$356.307** de débito
(375.060 − 18.753). El crédito es mayor: no se paga IVA y queda un remanente de **$78.793** para
mayo. Lectura: la librería compró más de lo que vendió en el mes; el IVA de los cuadernos que
siguen en bodega se recupera cuando se vendan.

**3.6.** Débito: 6.420.000 × 0,19 = **$1.219.800**. Crédito: $788.500 (mercaderías) + $44.840 (gas
y luz) + $58.900 (mantención) = **$892.240**. Los sueldos no llevan IVA. IVA del mes: **$327.560**.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 31-08 | IVA débito fiscal | 1.219.800 |  |
|  |  | IVA crédito fiscal |  | 892.240 |
|  |  | IVA por pagar |  | 327.560 |
| | | *Liquidación del IVA de agosto* | | |
| 2 | 12-09 | IVA por pagar | 327.560 |  |
|  |  | Banco |  | 327.560 |
| | | *Pago del IVA de agosto* | | |

Con el error, el crédito subiría en 235.600 y declararía solo **$91.960**: pagaría de menos y el
error aparecería en una fiscalización. Lectura: solo da crédito lo que tiene factura afecta.

**3.7.** Julio: débito **$558.600**; crédito 248.900 + **$1.071.600** del elevador = **$1.320.500**;
remanente **$761.900**. Agosto: débito **$1.086.800**, crédito **$283.100**; antes del remanente
serían **$803.700**, y descontado el remanente se pagan **$41.800**.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 31-07 | IVA débito fiscal | 558.600 |  |
|  |  | IVA remanente | 761.900 |  |
|  |  | IVA crédito fiscal |  | 1.320.500 |
| | | *Liquidación de julio: queda remanente* | | |
| 2 | 31-08 | IVA débito fiscal | 1.086.800 |  |
|  |  | IVA crédito fiscal |  | 283.100 |
|  |  | IVA remanente |  | 761.900 |
|  |  | IVA por pagar |  | 41.800 |
| | | *Liquidación de agosto: se usa el remanente de julio* | | |

Sin el elevador, julio habría pagado **$309.700**. Lectura: el IVA del elevador se recuperó en dos
meses (309.700 que no pagó en julio y 761.900 que descontó en agosto suman 1.071.600).

**3.8.** (a) Para la carpintería, el IVA de la factura se recupera: A le cuesta 40 × 18.500 =
**$740.000** (paga $22.015 por plancha, pero $3.515 vuelven como crédito, $140.600 en total); B le
cuesta 40 × 21.200 = **$848.000**, porque sin factura todo el precio es costo. Compra a A y ahorra
**$108.000**. (b) Una persona no recupera nada: A le cuesta **$880.600** y B **$848.000**; le
conviene B por **$32.600**. (c) La diferencia es el crédito fiscal: para quien lo usa, el precio
relevante es el neto; para quien no, el bruto. Lectura: compara proveedores por lo que te cuesta a
ti, no por el número de la cotización.

**3.9.**

| Mes | Débito | Crédito del mes | Remanente que llega | IVA a pagar | Remanente que sigue |
|---|---|---|---|---|---|
| Marzo | 345.800 | 1.029.800 | 0 | 0 | 684.000 |
| Abril | 499.700 | 281.200 | 684.000 | 0 | 465.500 |
| Mayo | 942.400 | 406.600 | 465.500 | 70.300 | 0 |

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 31-05 | IVA débito fiscal | 942.400 |  |
|  |  | IVA crédito fiscal |  | 406.600 |
|  |  | IVA remanente |  | 465.500 |
|  |  | IVA por pagar |  | 70.300 |
| | | *Liquidación de mayo: se agota el remanente* | | |

En los tres meses pagó $70.300, que es el débito total ($1.787.900) menos el crédito total
($1.717.600). Sin la cámara habría pagado **$879.700**; la diferencia, $809.400, es exactamente el IVA
de la cámara. Lectura: el remanente no se pierde, solo se demora; la florería recuperó todo el IVA
de la cámara en tres meses, pero tuvo que financiarlo con su caja mientras tanto.

**3.10.** (a) El neto del kilo es 2.400 / 1,19 = **$2.016,81**; $383,19 son IVA. Gana
**$516,81** por kilo, no $900: un margen de **34,5 %** sobre el costo. (b) 1.500 × 1,40 × 1,19 =
**$2.499** con IVA (neto **$2.100**). (c) Débito: 3.150 × 2.499 × 19/119 = **$1.256.850**; crédito:
3.150 × 1.500 × 0,19 = **$897.750**; IVA a pagar **$359.100**, que es el 19 % del valor agregado
(3.150 × 600 = **$1.890.000**). Lectura: un precio con IVA incluido esconde un 16 % que no es del
negocio; el margen se calcula siempre con el neto.

---

## 10. Caso integrador · el IVA de marzo de Estampa Sur

> Viene de la unidad 2: los 12 asientos de marzo, registrados con sus netos y el IVA aparte. Aquí se
> junta todo ese IVA y se liquida el mes.

**Pregunta.** ¿Cuánto IVA debe pagar Estampa Sur por marzo, y qué pasa con lo que sobra?

**Desarrollo.**

1. **El débito.** Las ventas netas del mes son $25.726.200 (asiento 6), y su IVA es
   **$4.887.978**.
2. **El crédito.** Seis asientos traen IVA de compras (los sueldos, el préstamo, el arriendo y los
   pagos y cobros de saldos no llevan):

| Asiento | Compra | Neto | IVA crédito fiscal |
|---|---|---|---|
| 1 | Poleras lisas básicas | 5.145.000 | 977.550 |
| 2 | Otras prendas lisas | 10.166.980 | 1.931.726 |
| 3 | Tinta | 1.176.731 | 223.579 |
| 4 | Segunda máquina | 14.300.000 | 2.717.000 |
| 9 | Seguro anual | 948.000 | 180.120 |
| 12 | Otros gastos de administración | 436.000 | 82.840 |
|  | **Crédito fiscal de marzo** |  | **6.112.815** |
| 6 | Ventas del mes (débito fiscal) | 25.726.200 | **4.887.978** |

   Cada factura va a peso entero: el IVA se redondea documento por documento y el crédito del mes es
   la suma de esos IVA.

3. **La liquidación.** El crédito supera al débito: no hay IVA por pagar y queda un **remanente de
   $1.224.837**.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| Liq. | 31-03 | IVA débito fiscal | 4.887.978 |  |
|  |  | IVA remanente | 1.224.837 |  |
|  |  | IVA crédito fiscal |  | 6.112.815 |
| | | *Liquidación del IVA de marzo: queda remanente* | | |

4. **Por qué.** Sin la máquina, el crédito habría sido 6.112.815 − 2.717.000 y Estampa Sur habría
   pagado **$1.492.163**. La máquina trajo $2.717.000 de IVA de una vez.

5. **Qué pasa en abril.** El remanente queda en el balance al 31-03 como un activo corriente (IVA
   remanente) y en abril se descuenta del débito, antes de pagar nada. Si abril repitiera las
   operaciones de marzo sin la máquina (un supuesto, para ver el orden de magnitud), Estampa Sur
   pagaría 1.492.163 − 1.224.837 = **$267.326**. Con eso habría recuperado los $2.717.000 en dos meses:
   1.492.163 que no pagó en marzo y 1.224.837 que descuenta en abril.

**Lectura.** El IVA no cambió el resultado de marzo (las ventas, los costos y la máquina van al neto),
pero sí la caja: en marzo la máquina se llevó $2.717.000 de IVA en efectivo (asiento 4) que el taller
recupera recién en abril. Para decidir cuánta caja necesita el taller en marzo, ese IVA cuenta; para
decidir si la máquina conviene, no.

**Pasa a la unidad 4:** la segunda máquina entra al activo por su neto, $14.300.000, sin el IVA. Esa
es la base de su depreciación.

---

## 11. Para seguir

**En los libros del ramo.** El programa fija como bibliografía obligatoria a Gálvez y Clarke,
*Contabilidad financiera para la dirección de empresas* (Ediciones UC), y a Irarrázabal,
*Contabilidad: fundamentos y usos* (Ediciones UC, 2014). Garrison, Noreen y Brewer, Horngren y
Weygandt, Kimmel y Kieso figuran como complementarios. El programa no fija capítulos para el IVA.

**Abierto y gratis.**

- El SII explica la declaración mensual del IVA (formulario 29, que se declara y paga el mes
  siguiente) en su página para quienes venden: https://www.sii.cl/destacados/iva/iva_vende.html
- Jonick, *Principles of Financial Accounting*, University of North Georgia Press (2018), en inglés,
  licencia CC BY-SA 4.0: https://oer.galileo.usg.edu/business-textbooks/7/ (está en la bibliografía
  complementaria del programa; trata la partida doble con planillas).

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un mes de operaciones de una pyme con
compras, ventas, una devolución y un activo fijo, déjame hacer el libro diario y la liquidación del
IVA, y corrígeme asiento por asiento».
