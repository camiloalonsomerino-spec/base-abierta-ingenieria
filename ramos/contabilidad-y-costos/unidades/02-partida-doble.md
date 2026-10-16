---
ramo: Contabilidad y Costos
unidad: 2
titulo: "Partida doble: asientos, libro diario, mayor y balance de comprobación"
version: 0.1 (16-10-2026)
requiere: [01-contabilidad-y-estados-financieros]
alimenta: [03-iva, 04-depreciacion, 05-ajustes-de-cierre, 07-inventarios, 08-razones-financieras]
verificacion: verificacion/u02_partida_doble.py
---

# Unidad 2 · Partida doble: asientos, libro diario, mayor y balance de comprobación

**Qué vas a poder hacer.** Decidir si un movimiento va al Debe o al Haber según el tipo de cuenta;
escribir asientos simples y compuestos con fecha, cuentas, montos y glosa, incluidos los que llevan
IVA; pasar el libro diario al libro mayor en cuentas T; armar el balance de comprobación de sumas y
saldos, y saber qué errores delata y cuáles no.

**Lo que necesitas antes.** La unidad 1: la ecuación contable, las cinco familias de cuentas (activo,
pasivo, patrimonio, ingreso y gasto) y el criterio de devengado.

**Tiempo.** Unas 5 horas: 1,5 de lectura con el ejemplo y 3,5 de práctica (los asientos se aprenden
escribiéndolos).

---

## 1. La idea

En la unidad 1 cada transacción se anotó como su efecto en la ecuación. Con diez transacciones eso
funciona; con mil, no. La **partida doble** es la forma ordenada de hacer lo mismo: cada hecho se
registra en al menos dos cuentas, con montos iguales a cada lado, de modo que la ecuación se mantiene
sola.

Una **cuenta** tiene dos lados. El izquierdo se llama **Debe** y el derecho **Haber**. Son nombres
históricos: no significan «deber» ni «tener». Cuatro palabras que se usan todo el tiempo:

| Palabra | Significa |
|---|---|
| **Cargar** o debitar | anotar en el Debe de una cuenta |
| **Abonar** o acreditar | anotar en el Haber |
| **Saldo deudor** | el Debe suma más que el Haber |
| **Saldo acreedor** | el Haber suma más que el Debe |

La regla de oro: **en cada asiento, la suma de los cargos es igual a la suma de los abonos.** No hay
excepciones.

---

## 2. Las reglas del Debe y el Haber

Se deducen de la ecuación. Si se pasan los gastos al lado izquierdo:

$$\underbrace{\text{Activo} + \text{Gastos}}_{\text{aumentan al Debe}} = \underbrace{\text{Pasivo} + \text{Patrimonio} + \text{Ingresos}}_{\text{aumentan al Haber}}$$

Lo que está a la izquierda de la igualdad crece por la izquierda de la cuenta (el Debe), y lo que
está a la derecha crece por la derecha (el Haber). Para que la igualdad se mantenga, cada peso
cargado en una cuenta tiene que abonarse en otra.

| Tipo de cuenta | Aumenta en | Disminuye en | Saldo normal | Ejemplos |
|---|---|---|---|---|
| Activo | Debe | Haber | deudor | Banco, Clientes, Mercaderías, IVA crédito fiscal, Maquinaria |
| Gasto (pérdida) | Debe | Haber | deudor | Costo de ventas, Sueldos, Arriendo, Electricidad |
| Pasivo | Haber | Debe | acreedor | Proveedores, Préstamo bancario, IVA débito fiscal |
| Patrimonio | Haber | Debe | acreedor | Capital, Utilidades retenidas |
| Ingreso (ganancia) | Haber | Debe | acreedor | Ventas, Ingresos por servicios, Intereses ganados |

**Dos cuentas con la naturaleza al revés.** La **Depreciación acumulada** es de activo pero tiene saldo
acreedor: resta de la máquina (unidad 4). Los **Retiros** o dividendos son de patrimonio pero tienen
saldo deudor: lo restan. Y las **Devoluciones sobre ventas** restan de las ventas con saldo deudor.

**Un chequeo que sirve siempre.** Si al final del mes una cuenta tiene saldo del lado contrario a su
naturaleza (Clientes acreedor, Proveedores deudor, Ventas deudora), casi seguro hay un asiento mal
hecho.

---

## 3. El asiento contable

Un **asiento** traduce un hecho económico (que llega en un documento: factura, boleta, comprobante de
transferencia, contrato) al lenguaje de las cuentas. Tiene cinco elementos:

1. **Número** correlativo.
2. **Fecha** del hecho.
3. **Cuentas**: primero las que se cargan; debajo, corridas a la derecha, las que se abonan.
4. **Montos** en la columna Debe o Haber.
5. **Glosa**: una línea que dice qué pasó.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | dd-mm-aaaa | Cuenta que se carga | xx | |
| | | &emsp;Cuenta que se abona | | xx |
| | | *Glosa: qué pasó* | | |

Un asiento es **simple** si mueve una cuenta en el Debe y una en el Haber; **compuesto** si mueve más
de dos (una compra pagada en parte al contado y en parte a crédito, una compra con IVA).

**Cómo se arma, en tres preguntas.** ¿Qué cuentas cambian? ¿Sube o baja cada una? Según su tipo, ¿eso
es Debe o Haber? Después se comprueba que cuadra.

### La venta con inventario: dos asientos

Cuando se vende mercadería se registran dos cosas a la vez: la **venta** (al precio, contra Clientes o
Banco) y la **salida de bodega** (al costo: se carga Costo de ventas y se abona Mercaderías). El primer
asiento mide lo que se cobra; el segundo, lo que se entregó. La diferencia es el margen.

**Margen sobre el costo no es margen sobre el precio.** «Vender con 25 % de margen sobre el costo» es
precio = costo × 1,25. «25 % sobre el precio» es precio = costo / 0,75, más alto. Lee cuál de los dos
pide el enunciado.

---

## 4. El IVA en el asiento

La unidad 3 trata el IVA completo; aquí basta con saber dónde va en el asiento. En Chile la tasa es
19 % sobre el precio neto.

- **Al comprar**, el IVA que paga la empresa se carga en **IVA crédito fiscal**, una cuenta de
  **activo**: es un derecho a descontarlo del IVA que cobre.
- **Al vender**, el IVA que cobra se abona en **IVA débito fiscal**, una cuenta de **pasivo**: es plata
  del Fisco que la empresa recauda.
- La mercadería, la máquina o la venta se registran por el **neto**; el proveedor o el cliente, por el
  **total** (neto + IVA).

Las facturas van en pesos enteros: el IVA se redondea al peso y el total es neto + IVA. No todo lleva
IVA en los ejercicios: los sueldos nunca; el arriendo, el seguro y otros servicios lo llevan o no según
lo diga el enunciado.

---

## 5. Libro diario y libro mayor

El **libro diario** reúne los asientos en orden de fecha: es la historia completa, un hecho detrás de
otro. Sirve para saber qué pasó el 14 de marzo, pero no para saber cuánto hay en el banco.

El **libro mayor** reordena lo mismo **por cuenta**: cada cuenta junta todos sus cargos y todos sus
abonos. Pasar del diario al mayor (el **pase**) es copiar cada línea del asiento a su cuenta, con el
número del asiento como referencia. El formato más usado para estudiar es la **cuenta T**:

| Debe · Banco | | Haber · Banco | |
|---|---|---|---|
| (1) | cargos | (2) | abonos |
| Sumas | Σ Debe | | Σ Haber |
| **Saldo** | Σ Debe − Σ Haber | | |

El mayor es lo que responde «cuánto hay»: el saldo de Banco es la plata en el banco; el de
Proveedores, lo que se les debe. La planilla de esta unidad hace el pase con fórmulas.

---

## 6. El balance de comprobación de sumas y saldos

Es una lista de todas las cuentas del mayor con cuatro columnas: lo que suma su Debe, lo que suma su
Haber, y su saldo, deudor o acreedor.

| Cuenta | Sumas Debe | Sumas Haber | Saldo deudor | Saldo acreedor |
|---|---|---|---|---|
| cada cuenta del mayor | Σ cargos | Σ abonos | si Debe > Haber | si Haber > Debe |
| **Totales** | **A** | **A** | **B** | **B** |

**Por qué cuadra.** Si cada asiento tiene el mismo monto al Debe y al Haber, el total de cargos de
todas las cuentas es igual al total de abonos (las sumas, A = A), y restar en cada cuenta no rompe la
igualdad (los saldos, B = B). Las sumas además coinciden con la suma de todos los asientos del diario.

**Para qué sirve.**

- Comprobar que el diario y el pase al mayor no tienen errores aritméticos.
- Tener en una sola hoja los saldos con los que se arman los estados financieros: los saldos de
  activo, pasivo y patrimonio van al balance; los de ingreso y gasto, al estado de resultados. La
  versión extendida que hace esa repartición en columnas se llama **balance de ocho columnas**.

**Lo que detecta.** Un asiento que no cuadra, un monto que se pasó al mayor solo de un lado o dos
veces del mismo lado, un error de suma en una cuenta. Una pista útil: si la diferencia entre los
totales es divisible por 9, probablemente se trasponen dos dígitos (escribir 470.000 como 407.000).

**Lo que NO detecta.** Todo error que mueva lo mismo al Debe y al Haber:

| Error | Por qué no aparece |
|---|---|
| Omitir un asiento completo | faltan los dos lados por igual |
| Registrar un asiento dos veces | sobran los dos lados por igual |
| Invertir el Debe y el Haber de un asiento | el asiento sigue cuadrando, al revés |
| Usar una cuenta equivocada del mismo lado (sueldos en arriendo, IVA débito en vez de crédito) | el monto está, en la cuenta equivocada |
| El mismo monto equivocado en los dos lados | cuadra con el monto malo |
| Dos errores que se compensan | se anulan en los totales |

Que la comprobación cuadre dice que la aritmética está bien, **no que la contabilidad esté bien**. Por
eso, además de mirar los totales, se mira cada saldo: una cuenta con saldo del lado contrario a su
naturaleza, o un saldo que no calza con la realidad (el banco que no coincide con la cartola), delata
lo que los totales esconden.

---

## 7. Ejemplo resuelto · Capa a Capa, mayo de 2026

Fernanda abre Capa a Capa, un servicio de impresión 3D por encargo. Lo que pasó en mayo de 2026:

| Fecha | Hecho |
|---|---|
| 02-05-2026 | Fernanda aporta **$7.400.000** a la cuenta corriente |
| 03-05-2026 | Compra dos impresoras por **$3.260.000** neto + IVA; paga la mitad por transferencia y la otra mitad a 60 días |
| 05-05-2026 | Compra filamento por **$870.000** neto + IVA, a crédito del proveedor |
| 06-05-2026 | Paga por transferencia el arriendo de mayo y el de junio, **$365.000** cada uno (sin IVA) |
| 20-05-2026 | Vende piezas por **$2.540.000** neto + IVA: 30 % por transferencia y el resto a crédito. El filamento usado en esas piezas costó **$510.000** |
| 31-05-2026 | Paga los sueldos de mayo, **$1.150.000** |
| 31-05-2026 | Abona **$640.000** al proveedor de filamento |
| 31-05-2026 | Cobra **$1.050.000** a los clientes |
| 31-05-2026 | Llega la cuenta de luz de mayo: **$64.000** neto + IVA, se paga en junio |

**Paso 1 · Los cálculos de IVA.** Impresoras: IVA 3.260.000 × 0,19 = $619.400, total $3.879.400,
mitad al contado ($1.939.700) y mitad a crédito. Filamento: IVA $165.300, total $1.035.300. Venta: IVA
$482.600, total $3.022.600; al contado 30 % = $906.780 y a crédito $2.115.820. Luz: IVA $12.160.

**Paso 2 · El libro diario.**

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 02-05-2026 | Banco | 7.400.000 |  |
|  |  | &emsp;Capital |  | 7.400.000 |
| | | *Aporte inicial de Fernanda* | | |
| 2 | 03-05-2026 | Maquinaria | 3.260.000 |  |
|  |  | IVA crédito fiscal | 619.400 |  |
|  |  | &emsp;Banco |  | 1.939.700 |
|  |  | &emsp;Cuentas por pagar |  | 1.939.700 |
| | | *Compra de dos impresoras, mitad al contado y mitad a 60 días* | | |
| 3 | 05-05-2026 | Materiales | 870.000 |  |
|  |  | IVA crédito fiscal | 165.300 |  |
|  |  | &emsp;Proveedores |  | 1.035.300 |
| | | *Compra de filamento a crédito del proveedor* | | |
| 4 | 06-05-2026 | Arriendo | 365.000 |  |
|  |  | Arriendo pagado por anticipado | 365.000 |  |
|  |  | &emsp;Banco |  | 730.000 |
| | | *Arriendo de mayo y junio pagado por transferencia* | | |
| 5 | 20-05-2026 | Banco | 906.780 |  |
|  |  | Clientes | 2.115.820 |  |
|  |  | &emsp;Ventas |  | 2.540.000 |
|  |  | &emsp;IVA débito fiscal |  | 482.600 |
| | | *Venta de piezas, 30 % por transferencia y el resto a crédito* | | |
| 6 | 20-05-2026 | Costo de ventas | 510.000 |  |
|  |  | &emsp;Materiales |  | 510.000 |
| | | *Costo del filamento de las piezas vendidas* | | |
| 7 | 31-05-2026 | Sueldos | 1.150.000 |  |
|  |  | &emsp;Banco |  | 1.150.000 |
| | | *Sueldos de mayo pagados* | | |
| 8 | 31-05-2026 | Proveedores | 640.000 |  |
|  |  | &emsp;Banco |  | 640.000 |
| | | *Abono a proveedores* | | |
| 9 | 31-05-2026 | Banco | 1.050.000 |  |
|  |  | &emsp;Clientes |  | 1.050.000 |
| | | *Cobro a clientes* | | |
| 10 | 31-05-2026 | Electricidad | 64.000 |  |
|  |  | IVA crédito fiscal | 12.160 |  |
|  |  | &emsp;Cuentas por pagar |  | 76.160 |
| | | *Cuenta de luz de mayo, se paga en junio* | | |

Tres decisiones: el asiento 4 separa el arriendo de mayo (gasto) del de junio (activo, porque aún no se
usa); la venta lleva dos asientos (5 al precio y 6 al costo); y la luz es gasto de mayo aunque se pague
en junio (devengado).

**Paso 3 · El mayor de cuatro cuentas.**

| Debe · Banco | | Haber · Banco | |
|---|---|---|---|
| (1) | 7.400.000 | (2) | 1.939.700 |
| (5) | 906.780 | (4) | 730.000 |
| (9) | 1.050.000 | (7) | 1.150.000 |
|  |  | (8) | 640.000 |
| Sumas | 9.356.780 | | 4.459.700 |
| **Saldo deudor** | **4.897.080** | | |

| Debe · Clientes | | Haber · Clientes | |
|---|---|---|---|
| (5) | 2.115.820 | (9) | 1.050.000 |
| Sumas | 2.115.820 | | 1.050.000 |
| **Saldo deudor** | **1.065.820** | | |

| Debe · IVA crédito fiscal | | Haber · IVA crédito fiscal | |
|---|---|---|---|
| (2) | 619.400 |  |  |
| (3) | 165.300 |  |  |
| (10) | 12.160 |  |  |
| Sumas | 796.860 | | 0 |
| **Saldo deudor** | **796.860** | | |

| Debe · Proveedores | | Haber · Proveedores | |
|---|---|---|---|
| (8) | 640.000 | (3) | 1.035.300 |
| Sumas | 640.000 | | 1.035.300 |
| | | **Saldo acreedor** | **395.300** |

**Paso 4 · El balance de comprobación.**

| Cuenta | Sumas Debe | Sumas Haber | Saldo deudor | Saldo acreedor |
|---|---|---|---|---|
| Banco | 9.356.780 | 4.459.700 | 4.897.080 |  |
| Clientes | 2.115.820 | 1.050.000 | 1.065.820 |  |
| Materiales | 870.000 | 510.000 | 360.000 |  |
| IVA crédito fiscal | 796.860 | 0 | 796.860 |  |
| Arriendo pagado por anticipado | 365.000 | 0 | 365.000 |  |
| Maquinaria | 3.260.000 | 0 | 3.260.000 |  |
| Proveedores | 640.000 | 1.035.300 |  | 395.300 |
| Cuentas por pagar | 0 | 2.015.860 |  | 2.015.860 |
| IVA débito fiscal | 0 | 482.600 |  | 482.600 |
| Capital | 0 | 7.400.000 |  | 7.400.000 |
| Ventas | 0 | 2.540.000 |  | 2.540.000 |
| Costo de ventas | 510.000 | 0 | 510.000 |  |
| Arriendo | 365.000 | 0 | 365.000 |  |
| Sueldos | 1.150.000 | 0 | 1.150.000 |  |
| Electricidad | 64.000 | 0 | 64.000 |  |
| **Totales** | **19.493.460** | **19.493.460** | **12.833.760** | **12.833.760** |

Las sumas ($19.493.460) son la suma de los diez asientos. Los saldos también cuadran.

**Cómo se lee.** De la comprobación salen, sin más trabajo, las dos cifras que Fernanda necesita. La
**utilidad de mayo**: ventas 2.540.000 − costo 510.000 − arriendo 365.000 − sueldos 1.150.000 − luz
64.000 = **$451.000**. Y la **caja**: $4.897.080 en el banco. En julio vence la segunda mitad de las
impresoras ($1.939.700) y hay $2.015.860 en cuentas por pagar en total; el banco los cubre, pero solo
si los clientes siguen pagando: todavía deben $1.065.820. El IVA crédito ($796.860) supera al débito
($482.600): en mayo no paga IVA y le queda un remanente de $314.260 para el mes siguiente (unidad 3).
La decisión de junio es cuánto vender a crédito: con 70 % a crédito, cada venta nueva tarda en volverse
caja justo cuando vence la máquina.

La planilla `planillas/u02_partida_doble.xlsx` trae este ejemplo y el caso: diario, mayor y
comprobación, con fórmulas.

---

## 8. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Invertir el Debe y el Haber | Activo y gasto suben al Debe; pasivo, patrimonio e ingreso, al Haber. Revisa la naturaleza del saldo final de cada cuenta |
| Olvidar el IVA | Si la factura dice neto + IVA, el asiento lleva una línea de IVA y el proveedor o cliente va por el total |
| Poner el IVA en la cuenta equivocada | Compra → IVA crédito fiscal (activo, Debe). Venta → IVA débito fiscal (pasivo, Haber) |
| Registrar la mercadería o la venta por el total con IVA | Mercadería, máquina y ventas van por el neto |
| Registrar como gasto un pago anticipado | Va a una cuenta de activo (Arriendo o Seguro pagado por anticipado); es gasto solo la parte del período |
| Olvidar el asiento del costo de ventas | Toda venta de mercadería lleva dos asientos: el de la venta y el de la salida de bodega al costo |
| Confundir margen sobre costo con margen sobre precio | Sobre costo: costo × (1 + m). Sobre precio: costo / (1 − m) |
| Registrar un anticipo de cliente como venta | Es un pasivo hasta que se entrega |
| Creer que si la comprobación cuadra, todo está bien | No detecta omisiones, duplicados, inversiones ni cuentas equivocadas; mira los saldos |
| Calcular el saldo restando al revés | Saldo = mayor suma − menor suma, y se anota del lado que suma más |

---

## 9. Práctica

Diez ejercicios: 2.1 a 2.4 básicos, 2.5 a 2.8 intermedios, 2.9 y 2.10 de desafío. IVA de 19 %
redondeado al peso. Las pautas están en la sección 10.

**2.1 · Debe o Haber (básico).** Para cada movimiento di la cuenta y si va al Debe o al Haber: (a)
entra dinero al banco; (b) sale dinero del banco; (c) se compra a crédito y aumenta la deuda con
proveedores; (d) se paga a un proveedor; (e) los socios aportan capital; (f) se registra una venta;
(g) se registra el sueldo del mes; (h) aumenta el IVA débito fiscal; (i) aumenta el IVA crédito fiscal;
(j) aumenta la depreciación acumulada; (k) un cliente paga su deuda; (l) el dueño hace un retiro.

**2.2 · El carro de comida (básico).** Escribe los asientos (sin IVA) y calcula el saldo de Caja y de
Banco: 02-03-2026, el dueño aporta $3.500.000 en efectivo; 03-03-2026, deposita $2.800.000 de la caja en
una cuenta corriente; 04-03-2026, compra insumos por $420.000 con transferencia; 07-03-2026, vende
$690.000 en efectivo (el costo de los insumos usados se registra a fin de mes, no aquí); 09-03-2026,
paga el permiso municipal, $85.000, con transferencia.

**2.3 · Compra con IVA (básico).** El 10-03-2026 una tienda compra mercadería por $1.260.000 neto +
IVA; paga 40 % por transferencia y el resto queda a 30 días. Escribe el asiento.

**2.4 · Venta con margen (básico).** El 12-03-2026 se vende a crédito mercadería que costó $740.000,
con un margen de 35 % sobre el costo, más IVA. Escribe los dos asientos. ¿Qué porcentaje del precio es
el margen? ¿Cuál habría sido el precio neto si el 35 % fuera sobre el precio?

**2.5 · La lavandería (intermedio).** Lavandería Burbuja, junio de 2026, sin IVA. Escribe el diario,
pasa al mayor y arma el balance de comprobación de sumas y saldos. ¿Ganó o perdió en el mes?
01-06, la dueña aporta $7.250.000 en efectivo; 02-06, deposita $5.900.000 en la cuenta corriente; 04-06,
compra dos lavadoras industriales por $3.840.000, paga 30 % con cheque y firma documentos a 12 meses
por el resto; 08-06, compra detergente por $515.000 con transferencia; 15-06, factura servicios de
lavado por $1.410.000, cobra 60 % en efectivo y el resto queda a crédito; 30-06, el consumo de
detergente del mes fue $298.000; 30-06, paga sueldos por $1.180.000 con transferencia.

**2.6 · La tienda de bicicletas (intermedio).** El 05-06-2026 compra 12 bicicletas a $178.000 neto cada
una + IVA, a crédito. El 07-06-2026 devuelve 2 que venían falladas y el proveedor rebaja la deuda. El
20-06-2026 vende 7 a $279.000 neto cada una + IVA: la mitad por transferencia y la mitad a crédito.
Escribe los asientos (con el costo de ventas). Calcula el saldo de Mercaderías y de Proveedores, el IVA
crédito y débito del mes, y el margen bruto.

**2.7 · Cinco errores (intermedio).** El ayudante de una tienda cometió estos errores en el mes: (a)
una venta al contado de $470.000 la cargó bien a Caja pero la abonó a Ventas por $407.000; (b) omitió
la compra de insumos por $135.000 pagada por transferencia; (c) un pago de $310.000 a un proveedor lo
registró al revés: Banco al Debe y Proveedores al Haber; (d) los sueldos de $820.000 los cargó a
Arriendo; (e) al pasar al mayor un cobro de $265.000 a clientes, lo anotó dos veces en el Haber de
Clientes. ¿Cuáles hacen que el balance de comprobación no cuadre? ¿Por cuánto y de qué lado? ¿En
cuánto queda mal el saldo de Banco?

**2.8 · Del mayor al asiento (intermedio).** Estas cuentas T son de una empresa recién creada; las
letras son los asientos. Reconstruye los asientos con su glosa y calcula las sumas del balance de
comprobación y los saldos de Banco, Préstamo bancario y Mercaderías.

| Cuenta | Debe | Haber |
|---|---|---|
| Banco | (a) 4.600.000 · (c) 904.400 | (b) 1.642.200 · (d) 531.000 |
| Préstamo bancario | (d) 470.000 | (a) 4.600.000 |
| Mercaderías | (b) 1.380.000 | (e) 475.000 |
| IVA crédito fiscal | (b) 262.200 | |
| Ventas | | (c) 760.000 |
| IVA débito fiscal | | (c) 144.400 |
| Intereses pagados | (d) 61.000 | |
| Costo de ventas | (e) 475.000 | |

**2.9 · El taller de muebles Raulí (desafío).** Julio de 2026. Escribe el diario y arma el balance de
comprobación de sumas y saldos. Calcula la utilidad del mes y el IVA a pagar. Después responde: si el
ayudante hubiera olvidado los asientos de la devolución, ¿lo habría detectado la comprobación? ¿Cuánto
cambiarían la utilidad y el IVA?
01-07, un socio aporta $9.000.000 por transferencia y el otro una camioneta tasada en $7.200.000; 03-07,
compra madera por $2.450.000 neto + IVA, mitad por transferencia y mitad a 30 días; 08-07, vende
muebles por $3.900.000 neto + IVA, 40 % por transferencia y el resto a crédito; la madera usada costó
$1.170.000; 10-07, el cliente devuelve una mesa de $300.000 neto + IVA y se le rebaja la deuda; la mesa
vuelve a bodega (su madera costó $90.000); 15-07, un cliente anticipa $950.000 por un mueble que se
entrega en agosto (supón que el anticipo no lleva IVA hasta que se facture); 20-07, compra herramientas
por $680.000 neto + IVA, por transferencia; 31-07, paga sueldos por $1.600.000 y el arriendo de julio,
$520.000 (sin IVA).

**2.10 · La comprobación cuadra, pero... (desafío).** Una agencia de viajes registró así su primer mes
(agosto de 2026):

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 01-08-2026 | Banco | 5.200.000 | |
| | | &emsp;Capital | | 5.200.000 |
| 2 | 01-08-2026 | Computadores | 1.800.000 | |
| | | IVA débito fiscal | 342.000 | |
| | | &emsp;Banco | | 2.142.000 |
| 3 | 01-08-2026 | Gasto en seguros | 1.260.000 | |
| | | &emsp;Banco | | 1.260.000 |
| 4 | 20-08-2026 | Ventas | 3.450.000 | |
| | | IVA débito fiscal | 655.500 | |
| | | &emsp;Clientes | | 4.105.500 |
| 5 | 31-08-2026 | Sueldos | 1.450.000 | |
| | | &emsp;Banco | | 1.450.000 |

El asiento 3 es un seguro **anual** que empieza el 01-08-2026; el 4, una venta a crédito. La
comprobación cuadró y el ayudante informó una pérdida. (a) Encuentra los tres errores y por qué la
comprobación no los vio. (b) ¿Qué saldos delataban el problema? (c) Calcula la utilidad que informó
el ayudante, la correcta y el IVA del mes.

---

## 10. Pautas

**2.1.** (a) Banco, Debe. (b) Banco, Haber. (c) Proveedores, Haber. (d) Proveedores, Debe. (e)
Capital, Haber. (f) Ventas, Haber. (g) Sueldos, Debe. (h) IVA débito fiscal, Haber. (i) IVA crédito
fiscal, Debe. (j) Depreciación acumulada, Haber (es complementaria de activo). (k) Clientes, Haber. (l)
Retiros, Debe. Lectura: si dudas, pregúntate si la cuenta está a la izquierda (activo, gasto) o a la
derecha (pasivo, patrimonio, ingreso) de la ecuación.

**2.2.**

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 02-03-2026 | Caja | 3.500.000 | |
| | | &emsp;Capital | | 3.500.000 |
| 2 | 03-03-2026 | Banco | 2.800.000 | |
| | | &emsp;Caja | | 2.800.000 |
| 3 | 04-03-2026 | Insumos | 420.000 | |
| | | &emsp;Banco | | 420.000 |
| 4 | 07-03-2026 | Caja | 690.000 | |
| | | &emsp;Ventas | | 690.000 |
| 5 | 09-03-2026 | Gasto en permisos | 85.000 | |
| | | &emsp;Banco | | 85.000 |

(Glosas: aporte, depósito, compra de insumos, venta al contado, permiso municipal.) Caja: 3.500.000 −
2.800.000 + 690.000 = **$1.390.000**. Banco: 2.800.000 − 420.000 − 85.000 = **$2.295.000**. Sumas del
diario: **$7.495.000**. Lectura: el depósito (2) no cambia nada en la ecuación; solo mueve plata de una
cuenta de activo a otra.

**2.3.** IVA: 1.260.000 × 0,19 = **$239.400**; total **$1.499.400**; al contado **$599.760**; a crédito
**$899.640**.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 10-03-2026 | Mercaderías | 1.260.000 | |
| | | IVA crédito fiscal | 239.400 | |
| | | &emsp;Banco | | 599.760 |
| | | &emsp;Proveedores | | 899.640 |
| | | *Compra de mercadería, 40 % al contado* | | |

Lectura: el 40 % se aplica sobre el total con IVA, porque eso es lo que se paga.

**2.4.** Precio neto: 740.000 × 1,35 = **$999.000**; IVA **$189.810**; total **$1.188.810**.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 12-03-2026 | Clientes | 1.188.810 | |
| | | &emsp;Ventas | | 999.000 |
| | | &emsp;IVA débito fiscal | | 189.810 |
| | | *Venta a crédito* | | |
| 2 | 12-03-2026 | Costo de ventas | 740.000 | |
| | | &emsp;Mercaderías | | 740.000 |
| | | *Salida de bodega al costo* | | |

El margen es **$259.000**: el **25,9 %** del precio. Si el 35 % fuera sobre el precio, el precio neto
sería 740.000 / 0,65 = **$1.138.462**. Lectura: el mismo «35 %» da precios que difieren en casi
$140.000.

**2.5.** Asientos: (1) Caja / Capital 7.250.000. (2) Banco / Caja 5.900.000. (3) Maquinaria 3.840.000 /
Banco **1.152.000** y Documentos por pagar **2.688.000**. (4) Insumos / Banco 515.000. (5) Caja
**846.000** y Clientes **564.000** / Ingresos por servicios 1.410.000. (6) Gasto en insumos / Insumos
298.000. (7) Sueldos / Banco 1.180.000.

| Cuenta | Sumas Debe | Sumas Haber | Saldo deudor | Saldo acreedor |
|---|---|---|---|---|
| Caja | 8.096.000 | 5.900.000 | 2.196.000 |  |
| Banco | 5.900.000 | 2.847.000 | 3.053.000 |  |
| Clientes | 564.000 | 0 | 564.000 |  |
| Insumos | 515.000 | 298.000 | 217.000 |  |
| Maquinaria | 3.840.000 | 0 | 3.840.000 |  |
| Documentos por pagar | 0 | 2.688.000 |  | 2.688.000 |
| Capital | 0 | 7.250.000 |  | 7.250.000 |
| Ingresos por servicios | 0 | 1.410.000 |  | 1.410.000 |
| Gasto en insumos | 298.000 | 0 | 298.000 |  |
| Sueldos | 1.180.000 | 0 | 1.180.000 |  |
| **Totales** | **20.393.000** | **20.393.000** | **11.348.000** | **11.348.000** |

Resultado: 1.410.000 − 298.000 − 1.180.000 = **−68.000**: perdió $68.000. Lectura: el detergente que
sobra ($217.000) es activo, no gasto; la pérdida viene de que un mes de sueldos pesa más que medio mes
de clientes. Sin depreciar las lavadoras (unidad 4) la pérdida real es aún mayor.

**2.6.** Compra: Mercaderías **2.136.000**, IVA crédito fiscal **405.840** / Proveedores **2.541.840**.
Devolución (el asiento de la compra al revés, por las dos): Proveedores **423.640** / Mercaderías
**356.000**, IVA crédito fiscal **67.640**. Venta: Banco **1.162.035** y Clientes 1.162.035 / Ventas
**1.953.000**, IVA débito fiscal **371.070** (total **2.324.070**). Costo: Costo de ventas **1.246.000** /
Mercaderías 1.246.000. Saldo de Mercaderías **$534.000** (las 3 que quedan a $178.000). Proveedores
**$2.118.200**. IVA crédito **$338.200**, débito **$371.070**: se pagan **$32.870** de IVA (unidad 3).
Margen bruto **$707.000**. Lectura: la devolución también devuelve el IVA crédito; si se olvida,
el IVA a pagar sale más bajo de lo que corresponde.

**2.7.**

| Error | ¿Descuadra? | Efecto |
|---|---|---|
| (a) Venta 470.000 abonada por 407.000 | sí | el Debe supera al Haber en 63.000 |
| (b) Compra omitida | no | faltan 135.000 a cada lado |
| (c) Pago al revés | no | Banco y Proveedores quedan mal por 620.000 cada uno |
| (d) Sueldos en Arriendo | no | el gasto total está bien; su clasificación, no |
| (e) Cobro pasado dos veces al Haber | sí | el Haber supera al Debe en 265.000 |

En los totales, (a) y (e) se compensan en parte: el Haber supera al Debe en **$202.000**. La diferencia
de (a), **$63.000**, es divisible por 9 (63.000 / 9 = 7.000): la huella de una trasposición. Banco
queda sobrestimado en **$620.000** (debía bajar 310.000 y subió 310.000), más los 135.000 de la compra
omitida. Lectura: de cinco errores, la comprobación solo ve dos; el pago al revés, el más caro para
la caja, solo aparece al conciliar el banco con la cartola.

**2.8.** (a) Banco / Préstamo bancario 4.600.000: *se recibe un préstamo*. (b) Mercaderías 1.380.000,
IVA crédito fiscal **262.200** / Banco **1.642.200**: *compra de mercadería al contado*. (c) Banco
**904.400** / Ventas 760.000, IVA débito fiscal **144.400**: *venta al contado*. (d) Préstamo bancario
470.000, Intereses pagados 61.000 / Banco **531.000**: *se paga una cuota del préstamo* (amortización
más interés). (e) Costo de ventas / Mercaderías 475.000: *salida de bodega de lo vendido*. Sumas del
balance de comprobación: **$8.152.600**. Saldos: Banco **$3.331.200**, Préstamo bancario **$4.130.000**,
Mercaderías **$905.000**. Lectura: la cuota del préstamo no es toda gasto; solo el interés.

**2.9.**

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 01-07-2026 | Banco | 9.000.000 |  |
|  |  | Vehículos | 7.200.000 |  |
|  |  | &emsp;Capital |  | 16.200.000 |
| | | *Aportes de los socios* | | |
| 2 | 03-07-2026 | Madera | 2.450.000 |  |
|  |  | IVA crédito fiscal | 465.500 |  |
|  |  | &emsp;Banco |  | 1.457.750 |
|  |  | &emsp;Proveedores |  | 1.457.750 |
| | | *Compra de madera* | | |
| 3 | 08-07-2026 | Banco | 1.856.400 |  |
|  |  | Clientes | 2.784.600 |  |
|  |  | &emsp;Ventas |  | 3.900.000 |
|  |  | &emsp;IVA débito fiscal |  | 741.000 |
| | | *Venta de muebles* | | |
| 4 | 08-07-2026 | Costo de ventas | 1.170.000 |  |
|  |  | &emsp;Madera |  | 1.170.000 |
| | | *Costo de la venta* | | |
| 5 | 10-07-2026 | Devoluciones sobre ventas | 300.000 |  |
|  |  | IVA débito fiscal | 57.000 |  |
|  |  | &emsp;Clientes |  | 357.000 |
| | | *Devolución de una mesa* | | |
| 6 | 10-07-2026 | Madera | 90.000 |  |
|  |  | &emsp;Costo de ventas |  | 90.000 |
| | | *La mesa vuelve a bodega* | | |
| 7 | 15-07-2026 | Banco | 950.000 |  |
|  |  | &emsp;Ingreso percibido por adelantado |  | 950.000 |
| | | *Anticipo de un cliente* | | |
| 8 | 20-07-2026 | Herramientas | 680.000 |  |
|  |  | IVA crédito fiscal | 129.200 |  |
|  |  | &emsp;Banco |  | 809.200 |
| | | *Compra de herramientas* | | |
| 9 | 31-07-2026 | Sueldos | 1.600.000 |  |
|  |  | &emsp;Banco |  | 1.600.000 |
| | | *Sueldos de julio* | | |
| 10 | 31-07-2026 | Arriendo | 520.000 |  |
|  |  | &emsp;Banco |  | 520.000 |
| | | *Arriendo de julio* | | |

Cálculos: madera total $2.915.500 (IVA 465.500), mitad $1.457.750; venta total $4.641.000 (IVA
741.000), al contado $1.856.400 y a crédito $2.784.600; devolución $357.000 (IVA 57.000); herramientas
$809.200 (IVA 129.200).

| Cuenta | Sumas Debe | Sumas Haber | Saldo deudor | Saldo acreedor |
|---|---|---|---|---|
| Banco | 11.806.400 | 4.386.950 | 7.419.450 |  |
| Clientes | 2.784.600 | 357.000 | 2.427.600 |  |
| Madera | 2.540.000 | 1.170.000 | 1.370.000 |  |
| IVA crédito fiscal | 594.700 | 0 | 594.700 |  |
| Vehículos | 7.200.000 | 0 | 7.200.000 |  |
| Herramientas | 680.000 | 0 | 680.000 |  |
| Proveedores | 0 | 1.457.750 |  | 1.457.750 |
| IVA débito fiscal | 57.000 | 741.000 |  | 684.000 |
| Ingreso percibido por adelantado | 0 | 950.000 |  | 950.000 |
| Capital | 0 | 16.200.000 |  | 16.200.000 |
| Ventas | 0 | 3.900.000 |  | 3.900.000 |
| Devoluciones sobre ventas | 300.000 | 0 | 300.000 |  |
| Costo de ventas | 1.170.000 | 90.000 | 1.080.000 |  |
| Sueldos | 1.600.000 | 0 | 1.600.000 |  |
| Arriendo | 520.000 | 0 | 520.000 |  |
| **Totales** | **29.252.700** | **29.252.700** | **23.191.750** | **23.191.750** |

Ventas netas: 3.900.000 − 300.000 = **$3.600.000**; costo neto **$1.080.000**; utilidad: 3.600.000 −
1.080.000 − 1.600.000 − 520.000 = **$400.000**. IVA débito 741.000 − 57.000 = **$684.000**; crédito
**$594.700**; a pagar **$89.300**. El anticipo de $950.000 no es ingreso de julio. Sin los asientos de
la devolución, la comprobación **habría cuadrado igual** (una omisión saca lo mismo de los dos lados),
la utilidad habría sido **$610.000** (sobrestimada en **$210.000**: el precio de la mesa menos su costo)
y el IVA a pagar, **$57.000** más alto. Lectura: el aporte de la camioneta va al capital por su
tasación, sin pasar por el banco ni por resultados.

**2.10.** (a) Los errores: en el asiento 2 el IVA de la compra va a **IVA crédito fiscal**, no al
débito (cuenta equivocada del mismo lado); en el 3, el seguro anual es un activo, **Seguro pagado por
anticipado**, y solo $105.000 (un doceavo) es gasto de agosto, quedando **$1.155.000** como anticipado;
en el 4 el asiento está **invertido**: debía ser Clientes **4.105.500** al Debe, Ventas 3.450.000 e IVA
débito fiscal **655.500** al Haber. La comprobación cuadró (sumas de **$14.157.500** en los dos casos)
porque cada asiento, aunque mal, carga y abona lo mismo. (b) Los saldos delataban el problema: Ventas
con saldo **deudor**, Clientes con saldo **acreedor** y el IVA débito fiscal (un pasivo) con saldo
**deudor** de **$997.500**. (c) El ayudante informó −3.450.000 − 1.260.000 − 1.450.000 =
**−6.160.000**. Lo correcto es 3.450.000 − 105.000 − 1.450.000 = **$1.895.000**: una diferencia de
**$8.055.000**. IVA: débito 655.500 − crédito 342.000 = **$313.500** a pagar. El Banco (**$348.000**)
estaba bien, porque ningún error tocaba el banco. Lectura: con la comprobación cuadrada la agencia
creía que perdía más de seis millones; en realidad ganó casi dos.

---

## 11. Caso integrador · Estampa Sur, los asientos de marzo

> La unidad 1 dejó el balance al 1 de marzo: activo $15.768.000, pasivo $1.340.000 y capital
> $14.428.000. Ahora se registra el mes.

El script del caso (`verificacion/caso_estampa_sur_contable.py`) define doce operaciones. Este libro
diario las escribe con sus fechas, después de un **asiento de apertura** con el balance inicial (la
depreciación acumulada va al Haber, como complementaria). El caso no fija el año: las fechas son del
mes de marzo. Tres decisiones del caso:

- Las compras, las ventas, el seguro y los otros gastos fijos de administración (luz, internet y
  mantención) llevan IVA de 19 %; los sueldos y el arriendo, no. El pago del saldo inicial a proveedores
  y el cobro a clientes tampoco: el IVA de esas facturas se registró en febrero.
- Las ventas del mes van en un solo asiento resumen (el 6), con el 60 % cobrado al contado.
- La tinta comprada es la que exige la producción menos los 12 kg que había, más 5 kg que quedan de
  reserva: **71,317 kg** a $16.500, un neto de **$1.176.730,5**. Cada documento se redondea al peso como
  una factura (el medio peso sube): neto **$1.176.731**, IVA $223.579 y total $1.400.310.

El consumo de las prendas y de la tinta, la depreciación y el costo de lo vendido **no** están aquí: se
registran al cierre (unidades 4, 5 y 7) y llegan al estado de resultados en la unidad 8.

**El libro diario de marzo.**

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 0 | 01-03 | Banco | 4.270.000 |  |
|  |  | Clientes | 1.180.000 |  |
|  |  | Poleras lisas básicas | 2.160.000 |  |
|  |  | Tinta | 198.000 |  |
|  |  | Arriendo pagado por anticipado | 580.000 |  |
|  |  | Maquinaria | 9.840.000 |  |
|  |  | &emsp;Depreciación acumulada |  | 2.460.000 |
|  |  | &emsp;Proveedores |  | 1.340.000 |
|  |  | &emsp;Capital |  | 14.428.000 |
| | | *Apertura con el balance al 1 de marzo* | | |
| 1 | 01-03 | Poleras lisas básicas | 5.145.000 |  |
|  |  | IVA crédito fiscal | 977.550 |  |
|  |  | &emsp;Proveedores |  | 6.122.550 |
| | | *Compra de poleras lisas básicas a crédito* | | |
| 2 | 01-03 | Otras prendas lisas | 10.166.980 |  |
|  |  | IVA crédito fiscal | 1.931.726 |  |
|  |  | &emsp;Proveedores |  | 12.098.706 |
| | | *Compra de las otras prendas lisas a crédito* | | |
| 3 | 02-03 | Tinta | 1.176.731 |  |
|  |  | IVA crédito fiscal | 223.579 |  |
|  |  | &emsp;Banco |  | 1.400.310 |
| | | *Compra de tinta al contado* | | |
| 4 | 04-03 | Maquinaria | 14.300.000 |  |
|  |  | IVA crédito fiscal | 2.717.000 |  |
|  |  | &emsp;Banco |  | 8.267.000 |
|  |  | &emsp;Documentos por pagar a largo plazo |  | 8.750.000 |
| | | *Compra de la segunda máquina* | | |
| 5 | 04-03 | Banco | 6.400.000 |  |
|  |  | &emsp;Préstamo bancario |  | 6.400.000 |
| | | *Préstamo bancario* | | |
| 6 | 31-03 | Banco | 18.368.507 |  |
|  |  | Clientes | 12.245.671 |  |
|  |  | &emsp;Ventas |  | 25.726.200 |
|  |  | &emsp;IVA débito fiscal |  | 4.887.978 |
| | | *Ventas del mes* | | |
| 7 | 31-03 | Sueldos | 2.880.000 |  |
|  |  | &emsp;Banco |  | 2.880.000 |
| | | *Pago de sueldos* | | |
| 8 | 31-03 | Arriendo pagado por anticipado | 1.740.000 |  |
|  |  | &emsp;Banco |  | 1.740.000 |
| | | *Arriendo de abril a junio pagado por anticipado* | | |
| 9 | 31-03 | Seguro pagado por anticipado | 948.000 |  |
|  |  | IVA crédito fiscal | 180.120 |  |
|  |  | &emsp;Banco |  | 1.128.120 |
| | | *Seguro anual pagado al contado* | | |
| 10 | 31-03 | Proveedores | 1.340.000 |  |
|  |  | &emsp;Banco |  | 1.340.000 |
| | | *Pago a proveedores del saldo inicial* | | |
| 11 | 31-03 | Banco | 1.180.000 |  |
|  |  | &emsp;Clientes |  | 1.180.000 |
| | | *Cobro a clientes del saldo inicial* | | |
| 12 | 31-03 | Gastos de administración | 436.000 |  |
|  |  | IVA crédito fiscal | 82.840 |  |
|  |  | &emsp;Banco |  | 518.840 |
| | | *Otros gastos fijos de administración* | | |

**El mayor de las cuentas principales** (Ap. = apertura).

| Debe · Banco | | Haber · Banco | |
|---|---|---|---|
| Ap. | 4.270.000 | (3) | 1.400.310 |
| (5) | 6.400.000 | (4) | 8.267.000 |
| (6) | 18.368.507 | (7) | 2.880.000 |
| (11) | 1.180.000 | (8) | 1.740.000 |
|  |  | (9) | 1.128.120 |
|  |  | (10) | 1.340.000 |
|  |  | (12) | 518.840 |
| Sumas | 30.218.507 | | 17.274.270 |
| **Saldo deudor** | **12.944.237** | | |

| Debe · Proveedores | | Haber · Proveedores | |
|---|---|---|---|
| (10) | 1.340.000 | Ap. | 1.340.000 |
|  |  | (1) | 6.122.550 |
|  |  | (2) | 12.098.706 |
| Sumas | 1.340.000 | | 19.561.256 |
| | | **Saldo acreedor** | **18.221.256** |

| Debe · Clientes | | Haber · Clientes | |
|---|---|---|---|
| Ap. | 1.180.000 | (11) | 1.180.000 |
| (6) | 12.245.671 |  |  |
| Sumas | 13.425.671 | | 1.180.000 |
| **Saldo deudor** | **12.245.671** | | |

| Debe · IVA crédito fiscal | | Haber · IVA crédito fiscal | |
|---|---|---|---|
| (1) | 977.550 |  |  |
| (2) | 1.931.726 |  |  |
| (3) | 223.579 |  |  |
| (4) | 2.717.000 |  |  |
| (9) | 180.120 |  |  |
| (12) | 82.840 |  |  |
| Sumas | 6.112.815 | | 0 |
| **Saldo deudor** | **6.112.815** | | |

| Debe · IVA débito fiscal | | Haber · IVA débito fiscal | |
|---|---|---|---|
|  |  | (6) | 4.887.978 |
| Sumas | 0 | | 4.887.978 |
| | | **Saldo acreedor** | **4.887.978** |

**El balance de comprobación al 31 de marzo** (antes de los ajustes de cierre).

| Cuenta | Sumas Debe | Sumas Haber | Saldo deudor | Saldo acreedor |
|---|---|---|---|---|
| Banco | 30.218.507 | 17.274.270 | 12.944.237 |  |
| Clientes | 13.425.671 | 1.180.000 | 12.245.671 |  |
| Poleras lisas básicas | 7.305.000 | 0 | 7.305.000 |  |
| Otras prendas lisas | 10.166.980 | 0 | 10.166.980 |  |
| Tinta | 1.374.731 | 0 | 1.374.731 |  |
| IVA crédito fiscal | 6.112.815 | 0 | 6.112.815 |  |
| Arriendo pagado por anticipado | 2.320.000 | 0 | 2.320.000 |  |
| Seguro pagado por anticipado | 948.000 | 0 | 948.000 |  |
| Maquinaria | 24.140.000 | 0 | 24.140.000 |  |
| Depreciación acumulada | 0 | 2.460.000 |  | 2.460.000 |
| Proveedores | 1.340.000 | 19.561.256 |  | 18.221.256 |
| IVA débito fiscal | 0 | 4.887.978 |  | 4.887.978 |
| Documentos por pagar a largo plazo | 0 | 8.750.000 |  | 8.750.000 |
| Préstamo bancario | 0 | 6.400.000 |  | 6.400.000 |
| Capital | 0 | 14.428.000 |  | 14.428.000 |
| Ventas | 0 | 25.726.200 |  | 25.726.200 |
| Sueldos | 2.880.000 | 0 | 2.880.000 |  |
| Gastos de administración | 436.000 | 0 | 436.000 |  |
| **Totales** | **100.667.704** | **100.667.704** | **80.873.434** | **80.873.434** |

Las sumas son la apertura ($18.228.000) más los doce asientos ($82.439.704). Los saldos también
cuadran.

**Lectura.**

1. **El día de la máquina.** Después de comprar la tinta el banco tiene $2.869.690. Si el pie y el IVA
   de la máquina ($8.267.000) se pagaran antes de que llegue el préstamo, la cuenta quedaría en
   **−5.397.310**. Por eso el préstamo y la máquina se firman el mismo día: el préstamo existe para
   pagar el pie.
2. **La comprobación no es el balance.** Las poleras lisas muestran $7.305.000, las 3.000 unidades del
   mes, aunque 2.236 ya se estamparon: el consumo todavía no se registra. Sumar hoy los saldos de
   activo (dan $75.097.434) sería sumar prendas que ya no están en bodega. Tampoco hay utilidad todavía:
   solo están las ventas y $3.316.000 de sueldos y gastos de administración. Faltan el costo de lo
   vendido, la depreciación y el arriendo y el seguro devengados. En este taller los sueldos, el
   arriendo, el seguro y la depreciación son **costos indirectos de fabricación** (unidad 9): no se
   restan directo de las ventas, sino que pasan por el costo de cada prenda.
3. **Lo que vence.** El taller debe $18.221.256 a proveedores (lo que compró en el mes) y tiene
   $12.944.237 en el banco y $12.245.671 por cobrar: alcanza si los clientes pagan a tiempo.

**Lo que pasa a las unidades siguientes.** A la unidad 3, los saldos de IVA: crédito **$6.112.815** y
débito **$4.887.978**. A las unidades 4 y 5, la maquinaria ($24.140.000) y los pagos anticipados de
arriendo y seguro, que al devengarse se registran como costo indirecto. A la unidad 7, las 3.000 poleras lisas de la tarjeta de existencias. La planilla
`planillas/u02_partida_doble.xlsx` trae este diario, el mayor de las 18 cuentas y la comprobación, con
fórmulas.

---

## 12. Para seguir

**En los libros del ramo.**

- Gálvez y Clarke, *Contabilidad financiera para la dirección de empresas* (Ediciones UC), capítulos 2
  y 3: la lectura que el programa fija para las semanas de asientos y cuentas T.
- Irarrázabal, *Contabilidad: fundamentos y usos* (Ediciones UC, 2014), el otro texto obligatorio.
- Weygandt, Kimmel y Kieso, *Accounting Principles* (Wiley, 12.ª ed., 2014), complementario: el
  capítulo del proceso de registro (diario, mayor y balance de comprobación).

**Abiertos y gratis.**

- Franklin, Graybeal y Cooper, *Principles of Accounting, Volume 1: Financial Accounting*, OpenStax
  (2019), en inglés, capítulo 3: la ecuación ampliada, los asientos y el pase a cuentas T (sección 3.5)
  y el balance de comprobación (sección 3.6). Licencia CC BY-NC-SA:
  https://openstax.org/books/principles-financial-accounting/pages/3-why-it-matters
- Jonick, *Principles of Financial Accounting*, University of North Georgia Press (2018), en inglés,
  el complementario abierto del programa. Licencia CC BY-SA 4.0: https://oer.galileo.usg.edu/business-textbooks/7/

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame ocho transacciones de un mes con IVA,
déjame escribir el diario y el balance de comprobación, y después dime qué errores míos la
comprobación no habría detectado».
