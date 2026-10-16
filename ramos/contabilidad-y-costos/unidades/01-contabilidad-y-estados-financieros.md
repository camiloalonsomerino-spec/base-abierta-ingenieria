---
ramo: Contabilidad y Costos
unidad: 1
titulo: La contabilidad y los estados financieros
version: 0.1 (16-10-2026)
requiere: []
alimenta: [02-partida-doble, 05-ajustes-de-cierre, 08-razones-financieras]
verificacion: verificacion/u01_estados_financieros.py
---

# Unidad 1 · La contabilidad y los estados financieros

**Qué vas a poder hacer.** Explicar para quién se lleva la contabilidad y qué decide cada uno con
ella; clasificar una cuenta como activo, pasivo, patrimonio, ingreso o gasto; analizar el efecto de una
transacción en la ecuación contable; reconocer ingresos y gastos con el criterio de devengado; armar
un balance clasificado y un estado de resultados clasificado, y conectar los dos con el flujo de
efectivo y con el cambio del patrimonio.

**Lo que necesitas antes.** Sumar, restar y porcentajes. Nada del ramo: esta es la puerta de entrada.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. La idea

La **contabilidad** registra, en pesos, los hechos económicos de una empresa (lo que compra, vende,
paga, cobra, debe y consume), los clasifica y los resume en unos pocos informes: los **estados
financieros**. Sirve para decidir y para rendir cuentas. Responde tres preguntas distintas:

| Pregunta | Se llama | Se mira en |
|---|---|---|
| ¿Qué tiene la empresa y a quién se lo debe? | situación patrimonial | balance |
| ¿Ganó o perdió en el período? | situación económica | estado de resultados |
| ¿Tiene plata para pagar lo que vence? | situación financiera | flujo de efectivo |

### Usuarios internos y externos

| Usuario | Quién | Qué decide con la contabilidad |
|---|---|---|
| Interno | dueños que administran, gerencia, jefaturas | precios, qué producto empujar, cuánto comprar, si contratar |
| Interno | trabajadores | si la empresa es estable; en algunas, la gratificación |
| Externo | bancos y proveedores | si le prestan o le venden a crédito, a qué plazo |
| Externo | inversionistas y socios que no administran | si ponen o retiran capital |
| Externo | el Estado (en Chile, el Servicio de Impuestos Internos) | cuánto impuesto corresponde |
| Externo | clientes | si el proveedor va a estar ahí el próximo año |

Los externos no pueden pedir los datos que quieran: reciben los estados financieros, preparados con
**reglas comunes** para que se puedan comparar entre empresas. En Chile esas reglas son las NIIF
(normas internacionales de información financiera, IFRS en inglés). La **contabilidad financiera** es
la que sigue esas reglas y mira hacia afuera. La **contabilidad de costos o de gestión** (la segunda
mitad del ramo, desde la unidad 9) es para adentro: no tiene formato obligatorio y se arma para
decidir.

---

## 2. La ecuación contable

Todo lo que la empresa tiene (**activo**) alguien lo financió: o un tercero al que se le debe
(**pasivo**) o los dueños (**patrimonio**).

$$\text{Activo} = \text{Pasivo} + \text{Patrimonio}$$

Son dos miradas a los mismos recursos: la izquierda dice **qué hay**, la derecha **de dónde salió**.
Por eso la igualdad se cumple siempre, antes y después de cualquier transacción. El patrimonio es lo
que queda para los dueños si se pagara todo lo que se debe:

$$\text{Patrimonio} = \text{Activo} - \text{Pasivo}$$

### Cómo entran las ganancias

El patrimonio crece por dos caminos: los dueños **aportan** capital o la empresa **gana**. Baja cuando
la empresa pierde o cuando los dueños **retiran** (retiros, dividendos). La ganancia es la diferencia
entre ingresos y gastos, así que la ecuación se puede abrir:

$$\text{Activo} = \text{Pasivo} + \text{Capital} + \underbrace{(\text{Ingresos} - \text{Gastos})}_{\text{resultado}} - \text{Retiros}$$

**La intuición.** Un ingreso es un aumento del patrimonio que viene de la operación (vender,
cobrar intereses); un gasto es una disminución por la operación (sueldos, arriendo, lo que costó lo
vendido). Un préstamo no es ingreso: entra plata, pero también una deuda del mismo tamaño, y el
patrimonio no cambia. Un retiro del dueño no es gasto: baja el patrimonio, pero no para generar
ventas.

### El análisis de transacciones

Antes de escribir un asiento (unidad 2) conviene preguntarse, para cada hecho, qué cuentas cambian y
en qué dirección. Cinco patrones cubren casi todo:

| Hecho | Activo | Pasivo | Patrimonio |
|---|---|---|---|
| Los dueños aportan dinero | sube | | sube |
| Se compra un activo al contado | uno sube, otro baja | | |
| Se compra a crédito | sube | sube | |
| Se vende o se presta un servicio | sube | | sube (ingreso) |
| Se paga un gasto | baja | | baja (gasto) |

---

## 3. Las cuentas

Una **cuenta** agrupa los hechos de una misma naturaleza bajo un nombre (Banco, Clientes,
Proveedores, Ventas). El **plan de cuentas** es la lista que usa una empresa. Hay cinco familias; las
tres primeras van al balance y las dos últimas al estado de resultados.

### Activo

Lo que la empresa controla y que le traerá beneficios: bienes y derechos.

- **Corriente** (o circulante): se convierte en dinero o se consume dentro de un año. Caja, Banco,
  Clientes (ventas a crédito por cobrar), Documentos por cobrar, Mercaderías o Existencias, IVA
  crédito fiscal (unidad 3), Arriendo pagado por anticipado, Seguro pagado por anticipado.
- **No corriente**: dura más de un año y se usa, no se vende. Terrenos, Edificios, Maquinaria,
  Vehículos, Equipos (todo esto es «propiedad, planta y equipo») y los intangibles, como una marca
  comprada. A los bienes que se desgastan se les resta la **Depreciación acumulada** (unidad 4): es una
  cuenta **complementaria de activo**, no un pasivo. El terreno no se deprecia.

**Un pago anticipado es un activo.** Pagar en marzo el arriendo de abril a junio da el derecho a usar
el local tres meses: es un activo que se irá convirtiendo en gasto mes a mes (unidad 5).

### Pasivo

Lo que la empresa debe a terceros que no son dueños.

- **Corriente**: vence dentro de un año. Proveedores, Cuentas por pagar, Sueldos por pagar, IVA débito
  fiscal o IVA por pagar, Préstamo bancario de corto plazo, **Ingreso percibido por adelantado** (un
  cliente pagó algo que todavía no se le entrega: se le debe el producto o el servicio).
- **No corriente**: vence en más de un año. Préstamo bancario de largo plazo, Documentos por pagar a
  largo plazo.

### Patrimonio

Lo de los dueños: **Capital** (lo aportado), **Utilidades retenidas** (ganancias de años anteriores
que no se repartieron) y **Resultado del ejercicio** (la utilidad o pérdida del período en curso).

### Ingresos y gastos

**Ingresos**: Ventas, Ingresos por servicios, Intereses ganados, Utilidad por venta de un activo fijo.
**Gastos**: Costo de ventas, Sueldos, Arriendo, Seguros, Electricidad, Depreciación del ejercicio,
Intereses pagados, Pérdida por venta de un activo fijo.

**Costo y gasto no son lo mismo.** Comprar mercadería no es un gasto: es cambiar un activo (dinero) por
otro (mercadería). Se vuelve gasto (el **costo de ventas**) recién cuando se vende, y solo por lo
vendido. Lo que queda en bodega sigue siendo activo.

---

## 4. Los principios que se usan en todo el ramo

| Principio | Qué dice | Qué evita |
|---|---|---|
| **Entidad** | la empresa es distinta de sus dueños | mezclar el auto o el retiro del dueño con los gastos de la empresa |
| **Devengado** | el ingreso se reconoce cuando se gana y el gasto cuando se consume, se cobre o se pague cuando sea | que una venta a crédito «no exista» o que pagar tres meses de arriendo parezca un mes carísimo |
| **Empresa en marcha** | se supone que la empresa seguirá operando | valorar la maquinaria a precio de remate |
| **Costo histórico** | los activos se registran a lo que costaron | subir el valor de un terreno porque «ahora vale más» y llamarlo utilidad |
| **Período** | los resultados se miden por períodos iguales (mes, año) | comparar un trimestre con un año |
| **Unidad monetaria** | todo se mide en una moneda (pesos) | sumar kilos con horas |

El **devengado** es el que más se usa y el que más se equivoca. Su contrario es la **base de caja**:
contar como ingreso lo cobrado y como gasto lo pagado. La base de caja dice cuánta plata entró; el
devengado dice cuánto se ganó. Las dos cifras casi nunca coinciden, y las dos sirven: por eso hay un
estado de resultados (devengado) y un flujo de efectivo (caja).

Las NIIF permiten, en casos puntuales, medir algunos activos a valor razonable en vez de costo
histórico. Este ramo trabaja siempre con costo histórico.

---

## 5. Los estados financieros

### Balance (estado de situación financiera)

Es una **foto en una fecha**: los saldos de activo, pasivo y patrimonio en un día. El **balance
clasificado** los ordena por plazo:

| Activo | | Pasivo y patrimonio | |
|---|---|---|---|
| Activo corriente | se agota en el año | Pasivo corriente | vence en el año |
| Activo no corriente (neto de depreciación) | dura más de un año | Pasivo no corriente | vence en más de un año |
| | | Patrimonio | no es exigible |
| **Total activo** | | **Total pasivo y patrimonio** | |

Dos lecturas inmediatas: el **capital de trabajo** (activo corriente − pasivo corriente) dice si lo
que vence en el año se puede pagar con lo que se convierte en dinero en el año, y la proporción
pasivo / activo dice cuánto de la empresa financian terceros. La unidad 8 agrega las demás razones.

### Estado de resultados

Es una **película de un período**: los ingresos y gastos acumulados, y su diferencia. El **estado de
resultados clasificado** separa lo que es del negocio de lo que no:

| Línea | Qué incluye |
|---|---|
| Ingresos por ventas | lo vendido en el período, neto de IVA y de devoluciones |
| − Costo de ventas | lo que costó lo vendido |
| **= Margen bruto** | lo que deja vender, antes de los gastos de estructura |
| − Gastos de administración y ventas | sueldos, arriendo, seguros, publicidad, distribución, depreciación |
| **= Resultado operacional** | lo que gana el negocio en sí |
| ± Resultado no operacional | intereses, utilidad o pérdida por vender un activo fijo |
| **= Resultado antes de impuesto** | |
| − Impuesto a la renta | (los ejercicios de esta unidad no lo consideran) |
| **= Resultado del ejercicio** | utilidad o pérdida |

### Estado de flujo de efectivo

Muestra **de dónde vino y en qué se fue el dinero** del período, en tres bloques:

- **Operación**: cobros a clientes, pagos a proveedores, sueldos, arriendos, impuestos.
- **Inversión**: compra y venta de activos de largo plazo (máquinas, vehículos, terrenos).
- **Financiamiento**: aportes y retiros de los dueños, préstamos recibidos y su devolución, dividendos.

La suma de los tres es la variación de Caja y Banco entre el balance inicial y el final. Los
intereses pagados se pueden presentar en operación o en financiamiento; en este ramo van en operación.

### Estado de cambios en el patrimonio

Explica cómo pasa el patrimonio del principio al fin del período:
$\text{Patrimonio final} = \text{inicial} + \text{aportes} + \text{resultado} - \text{retiros y dividendos}$.
Aquí basta con esa línea; la empresa lo presenta separado por cuenta (capital, utilidades retenidas,
resultado).

### Cómo se conectan

| Desde | Hacia | Por dónde |
|---|---|---|
| Estado de resultados | Balance | la utilidad entra al patrimonio (Resultado del ejercicio) |
| Estado de cambios en el patrimonio | Balance | el patrimonio final es el del balance |
| Flujo de efectivo | Balance | la variación de efectivo es la diferencia de Caja y Banco entre dos balances |
| Balance inicial | Balance final | las transacciones del período, ordenadas en los otros tres estados |

**Cuándo no basta.** Un balance solo no dice si la empresa pasó apuros durante el período: dos saldos
de caja no muestran los flujos de entre medio. Y una utilidad alta no garantiza caja: puede estar
en clientes que no han pagado o en inventario sin vender. Por eso se leen juntos.

---

## 6. Ejemplo resuelto · la bicicletería Rueda Libre

Matías abre una bicicletería en abril de 2026. Todo es sin IVA y sin depreciación (llegan en las
unidades 3 y 4). Lo que pasó en el mes:

| | Fecha | Hecho |
|---|---|---|
| a | 01-04-2026 | Matías aporta **$6.300.000** a la cuenta del banco |
| b | 02-04-2026 | Compra herramientas y un banco de trabajo por **$1.450.000** con transferencia |
| c | 03-04-2026 | Compra repuestos por **$2.150.000**: paga 40 % por transferencia y el resto a 30 días |
| d | 05-04-2026 | Paga **$670.000**: el arriendo de abril y el de mayo ($335.000 cada uno) |
| e | 15-04-2026 | Vende repuestos que le costaron **$1.240.000** con un recargo de 60 % sobre el costo; cobra la mitad al contado y la otra mitad a 30 días |
| f | 15-04-2026 | Cobra **$730.000** en reparaciones, al contado |
| g | 20-04-2026 | Un cliente paga por adelantado **$265.000** por una mantención que se hará en mayo |
| h | 30-04-2026 | Paga el sueldo del ayudante, **$560.000** |
| i | 30-04-2026 | Llega la cuenta de luz de abril, **$48.000**; se paga en mayo |
| j | 30-04-2026 | Matías retira **$185.000** para uso personal |

**Paso 1 · Cada hecho en la ecuación.**

| | Qué cambia | Activo | Pasivo | Patrimonio |
|---|---|---|---|---|
| a | Banco +6.300.000; Capital +6.300.000 | 6.300.000 | 0 | 6.300.000 |
| b | Equipos +1.450.000; Banco −1.450.000 | 6.300.000 | 0 | 6.300.000 |
| c | Mercaderías +2.150.000; Banco −860.000; Proveedores +1.290.000 | 7.590.000 | 1.290.000 | 6.300.000 |
| d | Banco −670.000; Arriendo pagado por anticipado +335.000 (mayo); gasto Arriendo 335.000 (abril) | 7.255.000 | 1.290.000 | 5.965.000 |
| e | Banco y Clientes +992.000 cada uno; Ventas 1.984.000; Mercaderías −1.240.000; Costo de ventas 1.240.000 | 7.999.000 | 1.290.000 | 6.709.000 |
| f | Banco +730.000; Ingresos por reparaciones 730.000 | 8.729.000 | 1.290.000 | 7.439.000 |
| g | Banco +265.000; Ingreso percibido por adelantado +265.000 | 8.994.000 | 1.555.000 | 7.439.000 |
| h | Banco −560.000; gasto Sueldos 560.000 | 8.434.000 | 1.555.000 | 6.879.000 |
| i | Cuentas por pagar +48.000; gasto Electricidad 48.000 | 8.434.000 | 1.603.000 | 6.831.000 |
| j | Banco −185.000; Retiros 185.000 | 8.249.000 | 1.603.000 | 6.646.000 |

En cada fila, activo = pasivo + patrimonio. Tres decisiones de clasificación: en (d) solo abril es
gasto; en (e) la venta es 1.240.000 × 1,6 = $1.984.000 y lo que sale de bodega es costo de ventas; en
(g) el anticipo es una deuda con el cliente, no una venta.

**Paso 2 · Estado de resultados de abril.**

| | Pesos |
|---|---|
| Ventas de repuestos | 1.984.000 |
| Ingresos por reparaciones | 730.000 |
| **Ingresos** | **2.714.000** |
| − Costo de ventas | 1.240.000 |
| **Margen bruto** | **1.474.000** |
| − Sueldos | 560.000 |
| − Arriendo | 335.000 |
| − Electricidad | 48.000 |
| Gastos de operación (560.000 + 335.000 + 48.000) | 943.000 |
| **Utilidad de abril** | **531.000** |

**Paso 3 · Balance clasificado al 30-04-2026.**

| Activo | Pesos | Pasivo y patrimonio | Pesos |
|---|---|---|---|
| Banco | 4.562.000 | Proveedores | 1.290.000 |
| Clientes | 992.000 | Cuentas por pagar | 48.000 |
| Mercaderías | 910.000 | Ingreso percibido por adelantado | 265.000 |
| Arriendo pagado por anticipado | 335.000 | **Total pasivo** | **1.603.000** |
| **Activo corriente** | **6.799.000** | Capital | 6.300.000 |
| Equipos y herramientas | 1.450.000 | Resultado del ejercicio | 531.000 |
| | | Retiros del dueño | −185.000 |
| | | **Total patrimonio** | **6.646.000** |
| **Total activo** | **8.249.000** | **Total pasivo y patrimonio** | **8.249.000** |

**Paso 4 · Flujo de efectivo de abril.**

| Bloque | Movimientos | Pesos |
|---|---|---|
| Operación | cobros 992.000 + 730.000 + 265.000 = 1.987.000; pagos 860.000 + 670.000 + 560.000 = 2.090.000 | −103.000 |
| Inversión | herramientas y banco de trabajo | −1.450.000 |
| Financiamiento | aporte 6.300.000 − retiro 185.000 | 6.115.000 |
| **Variación del banco** | (empezó en cero) | **4.562.000** |

**Paso 5 · Cambios en el patrimonio.** 0 + 6.300.000 + 531.000 − 185.000 = **$6.646.000**, el mismo
del balance.

**Cómo se lee.** Rueda Libre ganó $531.000 en su primer mes, pero la operación consumió $103.000 de
caja. No hay contradicción: de lo ganado, $992.000 están en clientes que aún no pagan y la empresa
compró más repuestos de los que vendió ($910.000 siguen en bodega). A su favor juegan la deuda con
proveedores ($1.290.000), la luz por pagar y el anticipo del cliente. El puente es exacto:
531.000 − 992.000 − 910.000 − 335.000 + 1.290.000 + 48.000 + 265.000 = −103.000. La decisión: en mayo
vencen los $1.290.000 a proveedores; con $4.562.000 en el banco los paga, pero si el negocio sigue
vendiendo la mitad a crédito y comprando de más, la utilidad no le va a alcanzar para la caja. Cobrar a
30 días y comprar según lo que vende pesa tanto como vender más.

La planilla `planillas/u01_estados_financieros.xlsx` trae este ejemplo con fórmulas: cambia un monto y
mira cómo se mueven los dos estados.

---

## 7. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Poner la depreciación acumulada en el pasivo | Es complementaria de activo: se resta de la máquina o del vehículo |
| Depreciar el terreno | El terreno no se desgasta; solo se deprecian edificios, máquinas, vehículos y equipos |
| Registrar como gasto un pago anticipado | Lo que aún no se usa es activo; es gasto solo la parte del período |
| Registrar como venta un anticipo de cliente | Es un pasivo (ingreso percibido por adelantado) hasta que se entrega |
| Llamar gasto a la compra de mercadería | Es activo; el gasto es el costo de lo **vendido** |
| Contar un préstamo como ingreso | Sube el activo y sube el pasivo; el patrimonio no cambia |
| Registrar el retiro del dueño como sueldo o gasto | Es un retiro: baja el patrimonio sin pasar por resultados (principio de entidad) |
| Subir un activo a su valor de tasación y llamarlo utilidad | Costo histórico: se queda a lo que costó |
| Creer que utilidad es caja | La utilidad puede estar en clientes y en bodega; mira el flujo de efectivo |
| Poner el capital en el pasivo | El capital es patrimonio: no es exigible por terceros |

---

## 8. Práctica

Diez ejercicios: 1.1 a 1.4 básicos, 1.5 a 1.8 intermedios, 1.9 y 1.10 de desafío. Ninguno considera
IVA ni impuesto a la renta. Las pautas están en la sección 9.

**1.1 · Clasificar (básico).** Di si cada cuenta es activo corriente (AC), activo no corriente (ANC),
pasivo corriente (PC), pasivo no corriente (PNC), patrimonio (PAT), ingreso (I) o gasto (G): Banco ·
Clientes · Mercaderías · Maquinaria · Depreciación acumulada · Proveedores · Sueldos por pagar ·
Préstamo bancario a 4 años · Ingreso percibido por adelantado · Capital · Utilidades retenidas · Ventas ·
Costo de ventas · Arriendo del mes · Seguro pagado por anticipado · Intereses pagados.

**1.2 · La ecuación (básico).** (a) La empresa A tiene activos por $37.400.000 y pasivos por
$15.900.000. ¿Cuál es su patrimonio? ¿Qué porcentaje del activo financian terceros? (b) La empresa B
debe $8.150.000 y su patrimonio es $22.600.000. ¿Cuánto es su activo? (c) La empresa C empezó el año
con un activo de $52.000.000 y un pasivo de $31.500.000. En el año el activo subió $6.300.000 y el
pasivo bajó $2.750.000. ¿Cuánto cambió su patrimonio?

**1.3 · La peluquería (básico).** Para cada hecho, di qué cuentas cambian y anota el total de activo,
pasivo y patrimonio después de él: (1) la dueña aporta $4.500.000 al banco; (2) compra sillones y
secadores por $1.680.000 a crédito; (3) cobra $395.000 en cortes, al contado; (4) paga $600.000 al
proveedor de los sillones; (5) paga el arriendo del mes, $280.000; (6) vende una tarjeta de regalo de
$90.000 que se usará el mes siguiente.

**1.4 · Devengado o caja (básico).** Un estudio de diseño, en mayo: factura $3.150.000 por trabajos
hechos en mayo y cobra $1.900.000 de eso (el resto en junio); cobra además $700.000 de un trabajo de
abril; paga los sueldos de mayo, $1.240.000; paga en mayo el arriendo de junio, $410.000 (el de mayo,
del mismo monto, lo había pagado en abril), y recibe la cuenta de internet de mayo, $36.000, que paga
en junio. Calcula la utilidad de mayo en base devengada y el resultado en base caja. Explica la
diferencia.

**1.5 · Balance clasificado (intermedio).** Una ferretería tiene estos saldos al 31-12-2026: Caja
$185.000 · Banco $3.920.000 · Clientes $2.640.000 · Mercaderías $7.350.000 · Seguro pagado por
anticipado $270.000 · Terreno $18.500.000 · Vehículo $11.800.000 · Depreciación acumulada del vehículo
$2.950.000 · Proveedores $4.110.000 · Sueldos por pagar $960.000 · IVA por pagar $515.000 · Préstamo
bancario de corto plazo $1.800.000 · Préstamo bancario de largo plazo $9.600.000 · Utilidades retenidas
$4.380.000 · Resultado del ejercicio $1.735.000 · Capital: no se sabe. Arma el balance clasificado,
calcula el capital y el capital de trabajo.

**1.6 · Estado de resultados clasificado (intermedio).** Una distribuidora entrega esta lista del año:
Ventas $84.600.000 · Costo de ventas $52.450.000 · Clientes $9.300.000 · Sueldos de administración
$9.720.000 · Publicidad $1.380.000 · Arriendo de oficina $3.600.000 · Préstamo bancario $18.000.000 ·
Depreciación del ejercicio $2.150.000 · Gasto de distribución $4.270.000 · Capital $25.000.000 ·
Intereses pagados $1.940.000 · Arriendo pagado por anticipado $600.000 · Utilidad por venta de un
vehículo $860.000. Arma el estado de resultados clasificado hasta el resultado antes de impuesto y
calcula el margen bruto, el operacional y el antes de impuesto como porcentaje de las ventas.

**1.7 · Del balance inicial al final (intermedio).** Una empresa tenía al 01-01-2026 activos por
$63.400.000 y pasivos por $27.500.000. Al 31-12-2026, activos por $71.900.000 y pasivos por
$26.300.000. En el año los socios aportaron $4.700.000 y se pagaron dividendos por $3.250.000. ¿Cuál
fue la utilidad del año? Arma el estado de cambios en el patrimonio en una línea.

**1.8 · Flujo de efectivo (intermedio).** El banco de una empresa empezó el mes con $2.380.000. En el
mes: cobros a clientes $12.640.000 · pagos a proveedores $7.910.000 · sueldos $2.450.000 · intereses
pagados $115.000 · compra de una camioneta $9.200.000 · venta de una máquina usada $1.260.000 ·
préstamo recibido $5.800.000 · amortización de un préstamo antiguo $750.000 · dividendos pagados
$870.000. Arma el flujo por bloques y calcula el saldo final.

**1.9 · Gana, pero se queda sin caja (desafío).** Una distribuidora que crece vende $18.500.000 en
junio: cobra el 25 % al contado y el resto a 60 días. Lo vendido le costó $11.100.000. Para preparar
julio compró al contado mercadería por $14.800.000, y pagó $4.250.000 de gastos del mes. (a) Calcula
la utilidad de junio y el flujo de caja de la operación. (b) Explica la diferencia con el cambio en
clientes y en inventario. (c) Si comprara solo lo que vende, ¿qué porcentaje mínimo de las ventas
tendría que cobrar al contado para que la operación no consuma caja?

**1.10 · Los errores del contador (desafío).** Una empresa presenta al 31-12-2026 una utilidad de
$31.500.000, activos por $148.000.000 y pasivos por $52.000.000. Al revisar se encuentra que: (a) el
terreno, comprado en $43.500.000, se subió a su tasación de $61.000.000 y la diferencia se llevó a
resultados; (b) el seguro anual de $1.440.000, pagado el 01-12-2026, se registró completo como gasto de
diciembre; (c) un anticipo de cliente de $2.300.000 por un pedido que se entrega en enero se registró
como venta; (d) un retiro del dueño de $760.000 se registró como sueldo; (e) la depreciación acumulada,
$5.600.000, se presentó en el pasivo. Corrige la utilidad, el activo, el pasivo y el patrimonio, y di
qué principio se rompió en cada caso.

---

## 9. Pautas

**1.1.** AC: Banco, Clientes, Mercaderías, Seguro pagado por anticipado. ANC: Maquinaria y
Depreciación acumulada (complementaria: resta). PC: Proveedores, Sueldos por pagar, Ingreso percibido
por adelantado. PNC: Préstamo bancario a 4 años (la parte que vence en los próximos 12 meses se pasa al
corriente). PAT: Capital, Utilidades retenidas. I: Ventas. G: Costo de ventas, Arriendo del mes,
Intereses pagados. Lectura: las dos que más se equivocan son la depreciación acumulada (no es deuda) y
el ingreso percibido por adelantado (no es ingreso todavía).

**1.2.** (a) Patrimonio: 37.400.000 − 15.900.000 = **$21.500.000**. Terceros financian 15,9 / 37,4 =
**42,5 %**. (b) Activo: 8.150.000 + 22.600.000 = **$30.750.000**. (c) Patrimonio inicial
**$20.500.000**; al final el activo es $58.300.000 y el pasivo $28.750.000, así que el patrimonio es
**$29.550.000**: subió **$9.050.000**. Lectura: el patrimonio sube lo que sube el activo más lo que baja
el pasivo; la ecuación no dice si fue por utilidad o por aportes.

**1.3.**

| | Cuentas | Activo | Pasivo | Patrimonio |
|---|---|---|---|---|
| 1 | Banco +, Capital + | 4.500.000 | 0 | 4.500.000 |
| 2 | Muebles y equipos +, Proveedores + | 6.180.000 | 1.680.000 | 4.500.000 |
| 3 | Banco +, Ingresos por servicios (sube patrimonio) | 6.575.000 | 1.680.000 | 4.895.000 |
| 4 | Banco −, Proveedores − | 5.975.000 | 1.080.000 | 4.895.000 |
| 5 | Banco −, gasto Arriendo (baja patrimonio) | 5.695.000 | 1.080.000 | 4.615.000 |
| 6 | Banco +, Ingreso percibido por adelantado + | 5.785.000 | 1.170.000 | 4.615.000 |

Lectura: pagar una deuda (4) achica el activo y el pasivo, pero no toca el patrimonio; la tarjeta de
regalo (6) trae plata y una deuda, no una venta.

**1.4.** Devengado: ingresos $3.150.000 (lo facturado de mayo, cobrado o no); gastos 1.240.000 +
410.000 (el arriendo de **mayo**) + 36.000 = **$1.686.000**; utilidad **$1.464.000**. Caja: entradas
1.900.000 + 700.000 = **$2.600.000**; salidas 1.240.000 + 410.000 = **$1.650.000**; neto **$950.000**. La
diferencia, **$514.000**, se explica partida por partida: quedan $1.250.000 de mayo por cobrar (suman a
la utilidad, no a la caja), entran $700.000 de abril (suman a la caja, no a la utilidad) y el internet
es gasto sin salida de plata (36.000). Los dos arriendos (el de mayo devengado y el de junio pagado)
son iguales y se cancelan. Lectura: el estudio ganó $1.464.000 en mayo; la caja dice cuánto tiene para
pagar, no cuánto ganó.

**1.5.**

| Activo | Pesos | Pasivo y patrimonio | Pesos |
|---|---|---|---|
| Caja | 185.000 | Proveedores | 4.110.000 |
| Banco | 3.920.000 | Sueldos por pagar | 960.000 |
| Clientes | 2.640.000 | IVA por pagar | 515.000 |
| Mercaderías | 7.350.000 | Préstamo bancario de corto plazo | 1.800.000 |
| Seguro pagado por anticipado | 270.000 | **Pasivo corriente** | **7.385.000** |
| **Activo corriente** | **14.365.000** | Préstamo bancario de largo plazo | 9.600.000 |
| Terreno | 18.500.000 | **Pasivo no corriente** | **9.600.000** |
| Vehículo | 11.800.000 | **Total pasivo** | **16.985.000** |
| − Depreciación acumulada | −2.950.000 | Capital | 18.615.000 |
| **Activo no corriente** | **27.350.000** | Utilidades retenidas | 4.380.000 |
| | | Resultado del ejercicio | 1.735.000 |
| | | **Total patrimonio** | **24.730.000** |
| **Total activo** | **41.715.000** | **Total pasivo y patrimonio** | **41.715.000** |

El patrimonio es 41.715.000 − 16.985.000 = $24.730.000; el capital, lo que falta para completarlo:
**$18.615.000**. Capital de trabajo: 14.365.000 − 7.385.000 = **$6.980.000**. El vehículo vale en libros
$8.850.000; el terreno, sin depreciación. Lectura: lo que vence en el año está cubierto casi dos veces
por lo que se convierte en dinero en el año, aunque la mitad de eso es mercadería que todavía hay que
vender.

**1.6.** Clientes, Préstamo bancario, Capital y Arriendo pagado por anticipado son cuentas de balance:
no entran.

| | Pesos | % de ventas |
|---|---|---|
| Ventas | 84.600.000 | 100 % |
| − Costo de ventas | 52.450.000 | |
| **Margen bruto** | **32.150.000** | 38,0 % |
| − Sueldos de administración, publicidad, arriendo de oficina, depreciación y distribución | 21.120.000 | |
| **Resultado operacional** | **11.030.000** | 13,0 % |
| + Utilidad por venta de un vehículo − intereses pagados | −1.080.000 | |
| **Resultado antes de impuesto** | **9.950.000** | 11,8 % |

Lectura: el negocio gana 13 pesos de cada 100 vendidos; la deuda se lleva casi 2 y la venta del
vehículo, que no se repite, devuelve casi 1. Para comparar con el año siguiente se mira el operacional.

**1.7.** Patrimonio inicial 63.400.000 − 27.500.000 = **$35.900.000**; final 71.900.000 − 26.300.000 =
**$45.600.000**; subió **$9.700.000**. De eso, 4.700.000 son aportes, y además se repartieron 3.250.000:
utilidad = 9.700.000 − 4.700.000 + 3.250.000 = **$8.250.000**. En una línea: 35.900.000 + 4.700.000 +
8.250.000 − 3.250.000 = 45.600.000. Lectura: el activo subió $8.500.000 y el patrimonio más que eso
porque además se pagó deuda; quien mirara solo el aumento del patrimonio creería que la utilidad fue
$9.700.000.

**1.8.**

| Bloque | Cálculo | Pesos |
|---|---|---|
| Operación | 12.640.000 − 7.910.000 − 2.450.000 − 115.000 | 2.165.000 |
| Inversión | −9.200.000 + 1.260.000 | −7.940.000 |
| Financiamiento | 5.800.000 − 750.000 − 870.000 | 4.180.000 |
| **Variación** | | **−1.595.000** |

Saldo final: 2.380.000 − 1.595.000 = **$785.000**. Lectura: la operación genera caja, pero no alcanza
para la camioneta; el préstamo cubre la mayor parte y aun así el banco baja. Pagar dividendos en un
mes así es una decisión que conviene mirar dos veces.

**1.9.** (a) Utilidad: 18.500.000 − 11.100.000 − 4.250.000 = **$3.150.000**. Caja de la operación: se
cobró 25 % de 18.500.000 = $4.625.000 y salieron 14.800.000 + 4.250.000: **−$14.425.000**. (b) Clientes
subió $13.875.000 (lo vendido a crédito) y el inventario $3.700.000 (lo comprado y no vendido):
3.150.000 − 13.875.000 − 3.700.000 = −14.425.000. (c) Con compras iguales al costo de ventas, la caja
de la operación es (% contado × 18.500.000) − 11.100.000 − 4.250.000, que es cero con un contado de
**83,0 %**. Lectura: la empresa es rentable y aun así necesita financiamiento para crecer; o consigue
un crédito de capital de trabajo o acorta los plazos que da. Vender más a 60 días empeora la caja.

**1.10.**

| Error | Principio | Efecto en la utilidad | Efecto en el balance |
|---|---|---|---|
| (a) Terreno a tasación | costo histórico | −17.500.000 | activo −17.500.000 |
| (b) Seguro anual a gasto | devengado | +1.320.000 (solo 120.000 es de diciembre) | activo +1.320.000 (seguro anticipado) |
| (c) Anticipo como venta | devengado | −2.300.000 | pasivo +2.300.000 |
| (d) Retiro como sueldo | entidad | +760.000 | patrimonio −760.000 por el retiro |
| (e) Depreciación en el pasivo | presentación | 0 | activo −5.600.000 y pasivo −5.600.000 |

Utilidad corregida: **$13.780.000**, una corrección de −17.720.000. Activo: 148.000.000 − 17.500.000 + 1.320.000 −
5.600.000 = **$126.220.000**. Pasivo: 52.000.000 + 2.300.000 − 5.600.000 = **$48.700.000**. Patrimonio:
de **$96.000.000** a **$77.520.000** (−18.480.000 = la caída de la utilidad más el retiro de 760.000).
Lectura: más de la mitad de la utilidad informada era una tasación; un banco que prestara mirando
$31.500.000 estaría mirando una cifra que el negocio no generó.

---

## 10. Caso integrador · Estampa Sur, el balance al 1 de marzo

> Estampa Sur es el taller de serigrafía que el ramo sigue durante un mes: marzo. Produce 5.590
> prendas y vende 5.300. Antes de registrar nada hay que saber con qué empieza.

El script del caso (`verificacion/caso_estampa_sur_contable.py`) entrega los saldos al 1 de marzo.
Las 900 poleras lisas valen al costo estándar de \$2.400 cada una y los 12 kg de tinta a $16.500 el kg.
El arriendo de marzo se pagó en febrero. La máquina de estampado (el pulpo de 6 estaciones) ya lleva
depreciación.

| Activo | Pesos | Pasivo y patrimonio | Pesos |
|---|---|---|---|
| Banco | 4.270.000 | Proveedores | 1.340.000 |
| Clientes | 1.180.000 | **Total pasivo** | **1.340.000** |
| Poleras lisas básicas (900 × 2.400) | 2.160.000 | | |
| Tinta (12 kg × 16.500) | 198.000 | | |
| Arriendo pagado por anticipado (marzo) | 580.000 | | |
| **Activo corriente** | **8.388.000** | | |
| Maquinaria | 9.840.000 | Capital | 14.428.000 |
| − Depreciación acumulada | −2.460.000 | | |
| **Activo no corriente** | **7.380.000** | **Total patrimonio** | **14.428.000** |
| **Total activo** | **15.768.000** | **Total pasivo y patrimonio** | **15.768.000** |

**La ecuación.** 15.768.000 = 1.340.000 + 14.428.000. El script calcula el patrimonio como activo
menos pasivo y lo deja todo como capital (no separa utilidades retenidas).

**Lectura.** Terceros financian solo el **8,5 %** del activo: el taller es casi todo de su dueña.
Capital de trabajo: 8.388.000 − 1.340.000 = **$7.048.000**: puede pagar a los proveedores más de seis
veces con lo que tiene en el año. Sin restar la depreciación, el activo bruto es **$18.228.000**; la
máquina costó $9.840.000 y en libros ya vale **$7.380.000**, tres cuartos de su costo.

**Tres operaciones de marzo, vistas en la ecuación** (los asientos 4, 5 y 7 de la unidad 2):

| Operación | Activo | Pasivo | Patrimonio |
|---|---|---|---|
| (5) Préstamo bancario de $6.400.000 | +6.400.000 | +6.400.000 | 0 |
| (4) Segunda máquina: $14.300.000 más IVA, con pie y saldo a 3 años | +8.750.000 | +8.750.000 | 0 |
| (7) Sueldos de marzo pagados | −2.880.000 | 0 | −2.880.000 |

El préstamo y la máquina agrandan el balance sin cambiar el patrimonio: la segunda máquina la
financian el banco y el vendedor. Los sueldos, tal como se registran al pagarlos, bajan el patrimonio. En
este taller son un costo indirecto de fabricación (unidad 9): la unidad 10 muestra que una parte queda
guardada en las prendas que siguen en bodega. En marzo el taller
pasa de financiarse casi solo con lo propio a deber más de lo que tenía en el banco; la unidad 8 mide
cuánto.

**Lo que pasa a la unidad 2.** Estos saldos son el **asiento de apertura** del libro diario de marzo.
La planilla `planillas/u01_estados_financieros.xlsx` trae este balance con fórmulas.

---

## 11. Para seguir

**En los libros del ramo.**

- Gálvez y Clarke, *Contabilidad financiera para la dirección de empresas* (Ediciones UC), el texto
  obligatorio del programa, capítulo 1: la lectura que el programa fija para las dos primeras semanas
  (conceptos, ecuación contable y estados financieros).
- Irarrázabal, *Contabilidad: fundamentos y usos* (Ediciones UC, 2014), el otro texto obligatorio.
- Weygandt, Kimmel y Kieso, *Accounting Principles* (Wiley, 12.ª ed., 2014), complementario: los
  capítulos iniciales sobre la ecuación contable y los estados financieros.

**Abiertos y gratis.**

- Franklin, Graybeal y Cooper, *Principles of Accounting, Volume 1: Financial Accounting*, OpenStax
  (2019), en inglés, capítulo 2 (los cuatro estados financieros, cómo se conectan y la clasificación en
  corriente y no corriente) y sección 3.1 (principios y supuestos). Licencia CC BY-NC-SA:
  https://openstax.org/books/principles-financial-accounting/pages/2-why-it-matters
- Jonick, *Principles of Financial Accounting*, University of North Georgia Press (2018), en inglés,
  el complementario abierto del programa. Licencia CC BY-SA 4.0, descarga en PDF:
  https://oer.galileo.usg.edu/business-textbooks/7/

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame diez transacciones de un mes de un negocio
chico, déjame anotar su efecto en la ecuación y armar el balance y el estado de resultados, y corrígeme
línea por línea».
