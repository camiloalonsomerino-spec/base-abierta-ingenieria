---
ramo: Contabilidad y Costos
unidad: 6
titulo: Préstamos e intereses en la contabilidad
version: 0.1 (16-10-2026)
requiere: [02-partida-doble, 05-ajustes-de-cierre]
alimenta: [08-razones-financieras]
verificacion: verificacion/u06_prestamos.py
---

# Unidad 6 · Préstamos e intereses en la contabilidad

**Qué vas a poder hacer.** Registrar un préstamo desde que entra la plata hasta la última cuota;
separar en cada cuota el interés (gasto) del capital (deuda que baja); devengar al cierre el interés
que corre entre la última cuota y la fecha del balance; dividir la deuda en porción corriente y no
corriente; registrar y reclasificar documentos por pagar, y presentar todo en el balance y en el
estado de resultados.

**Lo que necesitas antes.** Los asientos (unidad 2) y los devengados de cierre (unidad 5): el
interés por pagar es uno más. La cuota y la tabla de amortización se calculan como en Finanzas,
unidad 4 (créditos y amortización); acá no se repite esa matemática, se usa.

**Tiempo.** Unas 4 horas: 1,5 de lectura con el ejemplo y 2,5 de práctica.

**Planilla.** `planillas/u06_prestamos.xlsx`: la tabla del préstamo del caso y la del ejemplo, con
fórmulas, y su clasificación al cierre.

---

## 1. La idea

Un préstamo tiene dos piezas que la contabilidad trata distinto:

- **El capital** es una **deuda**: entra al pasivo cuando llega la plata y baja con la parte de
  cada cuota que lo devuelve (la **amortización**). Devolverlo no es gasto: la empresa entrega plata
  y deja de deber lo mismo.
- **El interés** es el **precio de usar la plata** durante un tiempo. Es **gasto financiero** del
  período en que corre, se pague cuando se pague. Es un devengado más (unidad 5).

Por eso el error más caro de esta unidad es registrar la cuota entera como gasto: infla el gasto con
capital y deja en el pasivo una deuda que ya se pagó.

**Recordatorio de Finanzas.** En la cuota fija (sistema francés):

$$C = \frac{P \cdot i}{1-(1+i)^{-n}} \qquad \text{interés}_t = \text{saldo}_{t-1} \cdot i \qquad \text{amortización}_t = C - \text{interés}_t$$

El interés baja cuota a cuota porque el saldo baja; la amortización sube en la misma medida.

---

## 2. Recibir el préstamo

**Método neto (el que se usa en esta base).** Se registra solo lo que se debe hoy, el capital:

| Cuenta | Debe | Haber |
|---|---|---|
| Banco | $P$ | |
| Préstamo bancario | | $P$ |

El interés aparece después, mes a mes, a medida que corre.

**Método bruto (el que muestra la clase).** Se registra la deuda por el total de las cuotas
($n \cdot C$) y la diferencia con lo recibido en **Intereses diferidos** (también llamados intereses
anticipados o por devengar):

| Cuenta | Debe | Haber |
|---|---|---|
| Banco | $P$ | |
| Intereses diferidos | $n \cdot C - P$ | |
| Préstamo bancario | | $n \cdot C$ |

Cada mes, el interés que corre pasa de Intereses diferidos a gasto (Gasto financiero al Debe,
Intereses diferidos al Haber), y cada cuota rebaja el préstamo por la cuota completa (Préstamo
bancario al Debe, Banco al Haber). **Intereses diferidos no es un activo**: es una cuenta que resta
al pasivo. Préstamo bruto menos intereses diferidos da, en todo momento, el mismo saldo de capital
del método neto (ejercicio 6.6). En el balance se presenta neto.

**Cuándo no aplica tal cual.** Si el banco descuenta gastos al entregar la plata, llega menos que
$P$ y el costo real del crédito sube (la CAE de Finanzas). En este ramo esos gastos se registran como
gasto financiero del mes en que se pagan.

---

## 3. Cada cuota · separar interés y capital

| Cuenta | Debe | Haber |
|---|---|---|
| Préstamo bancario | amortización$_t$ | |
| Gasto financiero | interés$_t$ | |
| Banco | | $C$ |

La tabla de amortización es el **libro auxiliar** del préstamo: cada fila es un asiento. El saldo
final de cada fila es lo que el mayor de Préstamo bancario debe mostrar después de esa cuota; si no
coincide, falta o sobra un asiento. Chequeo de la tabla: el saldo final termina en cero y la
amortización crece en un factor $(1+i)$ cada cuota.

---

## 4. El interés devengado al cierre

Si la cuota vence el mismo día del cierre, no hay ajuste: el interés del período ya entró con la
cuota. Pero casi nunca coinciden. Si la última cuota se pagó antes del cierre, entre esa fecha y el
cierre **corre interés que todavía no se paga**:

$$\text{interés devengado} = \text{saldo después de la última cuota} \times i \times \frac{\text{tiempo transcurrido}}{\text{tiempo del período de la cuota}}$$

Asiento de ajuste: Gasto financiero (D) contra **Intereses por pagar** (H). Dentro de un período, el
interés se reparte en proporción al tiempo (medio mes, medio interés del mes); es la convención del
ramo.

**Al pagar la cuota siguiente**, el interés de esa cuota se divide en dos: la parte ya devengada
salda Intereses por pagar y solo el resto es gasto nuevo. Cargar todo el interés a gasto otra vez lo
cuenta dos veces.

---

## 5. Porción corriente y no corriente

El balance separa los pasivos por plazo: **corriente** lo que se paga dentro de los 12 meses
siguientes al cierre, **no corriente** lo que se paga después. Un préstamo en cuotas tiene las dos
partes:

$$\text{porción corriente} = \text{saldo al cierre} - \text{saldo después de las 12 cuotas siguientes} \qquad \text{no corriente} = \text{saldo después de las 12 cuotas siguientes}$$

La porción corriente es **la suma de las amortizaciones** de las 12 cuotas siguientes, no 12 cuotas
completas: el interés de esas cuotas todavía no corre, así que todavía no se debe. Lo único de
interés que va al pasivo es lo ya devengado (Intereses por pagar, siempre corriente).

**Por qué importa.** La razón corriente (unidad 8) compara activo corriente con pasivo corriente.
Esconder la porción corriente en el largo plazo hace ver a la empresa más líquida de lo que es, y
muchos préstamos traen un compromiso con el banco sobre esa razón (ejercicio 6.10).

---

## 6. Documentos por pagar

Un **documento por pagar** es una deuda firmada en un papel con fecha: una **letra de cambio** o un
**pagaré**. Aparece al comprar a plazo con documento (no a crédito simple, que es Proveedores o
Cuentas por pagar) o al pedir un préstamo con un pagaré.

- **Clasificación.** Vence dentro de 12 meses: Documentos por pagar a corto plazo. Después: a largo
  plazo.
- **Reclasificación.** El día en que a un documento de largo plazo le quedan 12 meses, pasa al
  corto: Documentos por pagar a largo plazo (D) contra Documentos por pagar a corto plazo (H). No
  cambia la deuda; cambia su plazo.
- **Con interés explícito.** Si el pagaré cobra interés al vencimiento, el interés se devenga en
  cada cierre como en la sección 4 (ejercicio 6.7).
- **Sin interés explícito.** Una deuda a varios años «sin interés» igual lo esconde: pagar
  $8.750.000 en tres años vale hoy bastante menos que $8.750.000. Este ramo, como el curso, la
  registra a su valor nominal. La norma internacional pide en rigor medirla a valor presente y
  devengar ese interés implícito cada año; el caso integrador muestra cuánto es.

---

## 7. La presentación en los estados

| Dónde | Qué va | Ejemplo |
|---|---|---|
| Pasivo corriente | porción corriente del préstamo, intereses por pagar, documentos por pagar a corto plazo | lo que vence en los próximos 12 meses |
| Pasivo no corriente | porción no corriente del préstamo, documentos por pagar a largo plazo | lo que vence después |
| Estado de resultados | gasto financiero del período, bajo el resultado operacional (fuera de la operación) | el interés devengado, pagado o no |
| No va a resultado | la amortización del capital | devolver plata no es gasto |

El gasto financiero queda fuera del resultado operacional porque depende de **cómo se financia** la
empresa, no de lo bien que opera: dos talleres idénticos, uno con préstamo y otro sin, tienen el
mismo resultado operacional y distinto resultado final.

---

## 8. Ejemplo resuelto · el horno de la panadería Masa Madre

La panadería Masa Madre pide **$7.350.000** para un horno. El banco los deposita el **01-10-2026**;
se pagan en **18 cuotas mensuales** al **1,35 % mensual**, el día 1 de cada mes desde el
**01-11-2026**. La panadería cierra su año el **31-12-2026**.

**Paso 1 · La cuota y la tabla.**

$$C = \frac{7{.}350{.}000 \times 0{,}0135}{1 - 1{,}0135^{-18}} = 462{.}690$$

Cifras redondeadas al peso (la planilla trabaja con todos los decimales):

| Cuota N.º | Saldo inicial | Interés | Amortización | Cuota | Saldo final |
|---|---|---|---|---|---|
| 1 | 7.350.000 | 99.225 | 363.465 | 462.690 | 6.986.535 |
| 2 | 6.986.535 | 94.318 | 368.372 | 462.690 | 6.618.164 |
| 3 | 6.618.164 | 89.345 | 373.345 | 462.690 | 6.244.819 |
| 4 | 6.244.819 | 84.305 | 378.385 | 462.690 | 5.866.434 |
| 5 | 5.866.434 | 79.197 | 383.493 | 462.690 | 5.482.941 |
| 6 | 5.482.941 | 74.020 | 388.670 | 462.690 | 5.094.271 |
| 7 | 5.094.271 | 68.773 | 393.917 | 462.690 | 4.700.354 |
| 8 | 4.700.354 | 63.455 | 399.235 | 462.690 | 4.301.119 |
| 9 | 4.301.119 | 58.065 | 404.625 | 462.690 | 3.896.494 |
| 10 | 3.896.494 | 52.603 | 410.087 | 462.690 | 3.486.407 |
| 11 | 3.486.407 | 47.066 | 415.623 | 462.690 | 3.070.783 |
| 12 | 3.070.783 | 41.456 | 421.234 | 462.690 | 2.649.549 |
| 13 | 2.649.549 | 35.769 | 426.921 | 462.690 | 2.222.628 |
| 14 | 2.222.628 | 30.005 | 432.684 | 462.690 | 1.789.944 |
| 15 | 1.789.944 | 24.164 | 438.526 | 462.690 | 1.351.418 |
| 16 | 1.351.418 | 18.244 | 444.446 | 462.690 | 906.972 |
| 17 | 906.972 | 12.244 | 450.446 | 462.690 | 456.527 |
| 18 | 456.527 | 6.163 | 456.527 | 462.690 | 0 |

Total pagado $8.328.417; interés total **$978.417**. La amortización crece en un factor 1,0135 por
cuota y el saldo termina en cero.

**Paso 2 · Los asientos de 2026.**

| Fecha | Cuenta | Debe | Haber | Glosa |
|---|---|---|---|---|
| 01-10-2026 | Banco | 7.350.000 | | se recibe el préstamo |
| | Préstamo bancario | | 7.350.000 | |
| 01-11-2026 | Préstamo bancario | 363.465 | | cuota 1 |
| | Gasto financiero | 99.225 | | |
| | Banco | | 462.690 | |
| 01-12-2026 | Préstamo bancario | 368.372 | | cuota 2 |
| | Gasto financiero | 94.318 | | |
| | Banco | | 462.690 | |
| 31-12-2026 | Gasto financiero | 89.345 | | ajuste: interés de diciembre |
| | Intereses por pagar | | 89.345 | |

El interés de diciembre corre sobre el saldo después de la cuota 2 y se paga con la cuota 3, el
01-01-2027. Por eso se devenga al cierre.

**Paso 3 · La cuota 3, ya en 2027.** Préstamo bancario $373.345 e Intereses por pagar $89.345 al
Debe; Banco $462.690 al Haber. No hay gasto financiero en este asiento: el interés de diciembre ya
está en 2026.

**Paso 4 · Lo que muestran los estados al 31-12-2026.**

| Estado | Partida | Monto |
|---|---|---|
| Resultados 2026 | Gasto financiero (octubre, noviembre y diciembre) | 282.888 |
| Pasivo corriente | Porción corriente del préstamo (amortización de las cuotas 3 a 14) | 4.828.220 |
| Pasivo corriente | Intereses por pagar | 89.345 |
| Pasivo no corriente | Préstamo bancario a largo plazo (saldo después de la cuota 14) | 1.789.944 |
| | **Total adeudado al banco al 31-12-2026** | **6.707.509** |

Comprobación: el capital al cierre es $6.618.164 (saldo después de la cuota 2) = 4.828.220 +
1.789.944; con el interés devengado suma $6.707.509, que es el saldo por $(1+i)$: lo que habría que
pagar el 01-01-2027 para cancelar todo.

**Paso 5 · El método bruto, para comparar.** Al recibir, Préstamo bancario $8.328.417 al Haber,
Intereses diferidos $978.417 y Banco $7.350.000 al Debe. Al 31-12 el neto que se presenta es el
mismo.

**Cómo se lee.** En 2026 la panadería paga $925.380 (dos cuotas), pero solo $193.543 de eso es
interés; el resto es deuda que se devolvió. Con el interés de diciembre, que corre aunque no se
pague, el gasto del año es $282.888. Y aunque la deuda dure 18 meses, casi tres cuartos de lo que
debe al cierre se pagan en 2027: si la panadería hubiera puesto 12
cuotas completas como pasivo corriente ($5.552.278), habría inflado el corto plazo en $724.058 de
intereses que todavía no corren. Si el banco le pide una razón corriente mínima, esa diferencia
puede decidir si cumple.

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Registrar la cuota entera como gasto | Solo el interés es gasto; la amortización rebaja el préstamo |
| Calcular el interés sobre el monto original | El interés va sobre el saldo después de la cuota anterior |
| Olvidar el interés devengado al cierre | Si la cuota vence después del cierre, el interés que ya corrió se ajusta: Gasto financiero contra Intereses por pagar |
| Cargar a gasto, al pagar, el interés que ya se devengó | La parte devengada salda Intereses por pagar; solo el resto es gasto |
| Poner como porción corriente 12 cuotas completas | La porción corriente es capital: la suma de las 12 amortizaciones siguientes |
| Dejar todo el préstamo en el largo plazo | Lo que se amortiza en los próximos 12 meses es pasivo corriente |
| Presentar Intereses diferidos como activo | Resta al pasivo; préstamo bruto menos intereses diferidos es la deuda real |
| No reclasificar un documento de largo plazo | Cuando le quedan 12 meses o menos, pasa a corto plazo |
| Invertir Debe y Haber al recibir el préstamo | Banco sube (Debe), la deuda sube (Haber) |

---

## 10. Práctica

Diez ejercicios: 6.1 a 6.4 básicos, 6.5 a 6.8 intermedios, 6.9 y 6.10 de desafío. Escribe cada
asiento con fecha, cuentas, Debe, Haber y glosa, y comprueba que cuadre. Redondea al peso. Las pautas
están en la sección 11.

**6.1 · La cámara de frío (básico).** Una pescadería recibe un préstamo de $4.650.000 a 15 cuotas
mensuales al 1,45 % mensual. Calcula la cuota y registra la recepción y la primera cuota. ¿Cuánto
debe después de pagarla y cuánto interés pagará en total?

**6.2 · La cuota como gasto (básico).** El contador de la pescadería de 6.1 registró las tres primeras
cuotas enteras como gasto financiero. ¿Cuánto gasto registró, cuánto debió registrar y cuánto
muestra de más el pasivo después de la tercera cuota?

**6.3 · Medio mes de interés (básico).** Un préstamo de $5.200.000 a 24 cuotas al 1,25 % mensual se
recibió el 15-01-2026; las cuotas vencen el día 15 de cada mes desde el 15-02-2026. La empresa cierra
estados semestrales al 30-06-2026. (a) Registra el interés devengado al cierre. (b) Registra la cuota
del 15-07-2026. (c) ¿Cuál es el gasto financiero del semestre?

**6.4 · La camioneta con letras (básico).** El 01-03-2026 un vivero compra una camioneta en
$18.900.000 neto más IVA. Paga con transferencia el IVA y $6.900.000; el resto lo documenta en dos
letras de $6.000.000, a 10 y 20 meses, sin intereses. (a) Registra la compra. (b) ¿Cómo se clasifican
las letras al 30-06-2026 y al 31-12-2026? ¿Qué asiento hace falta entre esas fechas y cuándo?

**6.5 · Corriente o no corriente (intermedio).** Un préstamo de $12.600.000 a 36 cuotas al 1,1 %
mensual se recibió el 01-01-2026; las cuotas vencen el último día de cada mes desde el 31-01-2026.
Al 31-12-2026, después de pagar la cuota 12: (a) ¿cuánto se debe? (b) ¿Cuál es la porción corriente
y la no corriente? (c) ¿Cuánto daría la porción corriente si se tomaran 12 cuotas completas, y qué
representa la diferencia? (d) ¿Cuál fue el gasto financiero de 2026?

**6.6 · Bruto contra neto (intermedio).** Registra el préstamo de 6.1 con el método bruto (intereses
diferidos), el devengo del interés del mes 1 y el pago de la cuota 1. Muestra que, después de la
cuota, préstamo bruto menos intereses diferidos es igual al saldo de la tabla.

**6.7 · El pagaré al vencimiento (intermedio).** El 01-08-2026 una distribuidora firma un pagaré por
$9.600.000 a 9 meses, con interés simple del 0,85 % mensual que se paga junto con el capital el
01-05-2027. Registra el ajuste al 31-12-2026 y el pago al vencimiento. ¿Cuánto gasto financiero va a
cada año?

**6.8 · Amortización constante (intermedio).** Un préstamo de $6.240.000 a 8 cuotas mensuales al 1,5 %
mensual en sistema alemán (la misma amortización cada mes). Calcula la amortización, el interés y la
cuota de los meses 1 y 2 y la última cuota. Registra la cuota 2. ¿Cuánto interés se paga en total y
cómo se clasifica el préstamo en el balance?

**6.9 · Cuotas anuales con cierre a mitad (desafío).** El 01-07-2026 una constructora recibe
$18.500.000 a 4 cuotas anuales al 9 % anual; la primera vence el 01-07-2027. Cierra cada 31-12. (a)
Calcula la cuota y el interés del primer año del préstamo. (b) Registra el ajuste al 31-12-2026 y la
cuota del 01-07-2027. (c) ¿Cómo se presenta la deuda al 31-12-2026? (d) ¿Cuál es el gasto financiero
de 2027?

**6.10 · El compromiso con el banco (desafío).** Una empresa tomó el 01-01-2026 un préstamo de
$15.000.000 a 48 cuotas al 1,05 % mensual, pagadas a fin de mes. El contrato le exige mantener una
razón corriente (activo corriente sobre pasivo corriente) de al menos 1,5. Al 31-12-2026 tiene
$18.400.000 de activo corriente y $9.300.000 de pasivo corriente sin contar el préstamo, que el
contador dejó entero en el largo plazo. El resultado operacional del año fue $4.100.000. (a) Calcula
la porción corriente y la no corriente. (b) Calcula la razón corriente informada y la correcta.
¿Cumple? (c) ¿Cuánto activo corriente le faltaría para cumplir y cuál es la porción corriente máxima
que admitiría? (d) Calcula el gasto financiero de 2026 y cuántas veces lo cubre el resultado
operacional.

---

## 11. Pautas

**6.1.** Cuota: **$347.167**. Recepción: Banco (D) contra Préstamo bancario (H), $4.650.000. Cuota 1:
interés 4.650.000 × 1,45 % = **$67.425**; amortización **$279.742**. Préstamo bancario $279.742 y
Gasto financiero $67.425 al Debe, Banco $347.167 al Haber. Queda debiendo **$4.370.258**. Interés
total: 15 × 347.167 − 4.650.000 = **$557.505**.

**6.2.** Registró **$1.041.501** de gasto (tres cuotas). El interés de las tres cuotas es
**$190.047**: ese era el gasto. Sobra **$851.453** de gasto, que es capital devuelto, y el pasivo
sigue mostrando $4.650.000 cuando la deuda real es **$3.798.547**. El resultado sale bajo y la deuda
alta en lo mismo; el asiento que corrige es Préstamo bancario (D) contra Gasto financiero (H) por $851.453.

**6.3.** Cuota: **$252.131**. Después de la cuota 5 (15-06) el saldo es **$4.240.662**; el interés de
la cuota 6 es **$53.008**. (a) Del 15-06 al 30-06 corre medio mes: Gasto financiero (D) contra
Intereses por pagar (H), **$26.504**. (b) Cuota 6 (15-07-2026): Préstamo bancario $199.122,
Intereses por pagar $26.504 y Gasto financiero $26.504 al Debe; Banco $252.131 al Haber. La mitad del
interés es de junio y la otra mitad de julio. (c) Gasto del semestre: los intereses de las cuotas 1 a
5 más el medio mes de junio, **$327.819**. Al 30-06 la porción corriente es $2.560.785 (cuotas 6 a
17) y la no corriente $1.679.877.

**6.4.** (a) IVA: **$3.591.000**. Vehículos $18.900.000 e IVA crédito fiscal $3.591.000 al Debe;
Banco **$10.491.000**, Documentos por pagar a corto plazo $6.000.000 y Documentos por pagar a largo
plazo $6.000.000 al Haber. Total $22.491.000; las letras suman $12.000.000. (b) La primera letra
vence el 01-01-2027 y es corriente en las dos fechas. La segunda vence el 01-11-2027: al 30-06-2026
le quedan 16 meses (no corriente); el **01-11-2026** le quedan 12 y se reclasifica: Documentos por
pagar a largo plazo (D) contra Documentos por pagar a corto plazo (H), $6.000.000. Al 31-12-2026 las
dos son corrientes. Las letras no llevan interés: el vivero paga lo mismo antes o después, pero el
plazo cambia la lectura de su liquidez.

**6.5.** Cuota: **$425.759**. (a) Saldo después de la cuota 12: **$8.937.783**. (b) Corriente: lo
que se amortiza en las cuotas 13 a 24, **$4.175.976**; no corriente: el saldo después de la cuota 24,
**$4.761.807**. (c) Doce cuotas completas suman **$5.109.103**; la diferencia, **$933.128**, es el
interés de 2027, que todavía no corre y no es deuda al 31-12-2026. (d) Gasto financiero de 2026 (los
intereses de las cuotas 1 a 12): **$1.446.886**.

**6.6.** Recepción: Banco $4.650.000 e Intereses diferidos **$557.505** al Debe; Préstamo bancario
**$5.207.505** (15 cuotas) al Haber. Devengo del mes 1: Gasto financiero (D) contra Intereses
diferidos (H), $67.425. Cuota 1: Préstamo bancario (D) contra Banco (H), $347.167. Quedan préstamo
bruto **$4.860.338** e intereses diferidos **$490.080**: neto **$4.370.258**, el saldo de la tabla. El
gasto del mes es el mismo en los dos métodos.

**6.7.** Interés por mes: 9.600.000 × 0,85 % = **$81.600**. Al 31-12-2026 corrieron 5 meses (agosto a
diciembre): Gasto financiero (D) contra Intereses por pagar (H), **$408.000**. Al vencimiento
(01-05-2027): Documentos por pagar $9.600.000, Intereses por pagar $408.000 y Gasto financiero
**$326.400** (enero a abril) al Debe; Banco **$10.334.400** al Haber. El interés total, **$734.400**,
se reparte entre los dos años según el tiempo, no según cuándo se paga.

**6.8.** Amortización: 6.240.000 / 8 = **$780.000**. Mes 1: interés **$93.600**, cuota **$873.600**.
Mes 2: interés sobre $5.460.000 = **$81.900**, cuota **$861.900**. Asiento de la cuota 2: Préstamo
bancario $780.000 y Gasto financiero $81.900 al Debe, Banco $861.900 al Haber. Última cuota:
**$791.700**. Interés total **$421.200**. Como todo se paga en 8 meses, el préstamo completo es pasivo
corriente desde el primer día (después de la cuota 2 quedan $4.680.000, todos corrientes).

**6.9.** (a) Cuota: **$5.710.370**. Interés del primer año del préstamo: 18.500.000 × 9 % =
**$1.665.000**. (b) Al 31-12-2026 corrió medio año: Gasto financiero (D) contra Intereses por pagar
(H), **$832.500**. Cuota del 01-07-2027: Préstamo bancario **$4.045.370**, Intereses por pagar
$832.500 y Gasto financiero $832.500 al Debe; Banco $5.710.370 al Haber. (c) Al 31-12-2026: pasivo
corriente $4.045.370 (la amortización de la cuota de julio) más $832.500 de intereses por pagar;
pasivo no corriente **$14.454.630**. (d) 2027 tiene la otra mitad del primer año ($832.500) y la
primera mitad del segundo: el interés del segundo año es **$1.300.917** y su mitad **$650.458**. Gasto
financiero de 2027: **$1.482.958**. El interés total del préstamo es $4.341.481.

**6.10.** Cuota: **$399.441**. (a) Saldo al 31-12-2026: **$11.923.035**. Corriente (cuotas 13 a 24):
**$3.487.854**; no corriente **$8.435.181**. (b) Informada: 18.400.000 / 9.300.000 = **1,98**.
Correcta: 18.400.000 / **12.787.854** = **1,44**. **No cumple**: la empresa está bajo el 1,5 y lo
escondía clasificando mal. (c) Necesitaría $19.181.782 de activo corriente: le faltan **$781.782**.
Con su activo actual, la porción corriente no podría pasar de **$2.966.667**. Antes del cierre puede
pedirle al banco alargar el plazo o una dispensa; maquillar la clasificación no es una opción. (d)
Gasto financiero de 2026: **$1.716.326**; el resultado operacional lo cubre **2,39** veces.

---

## 12. Caso integrador · Estampa Sur, el préstamo de marzo

> En marzo Estampa Sur compró su segunda máquina (Finanzas, unidad 5): pagó un pie y dejó un saldo
> de $8.750.000 a 3 años (asiento 4 de la unidad 2), y pidió un préstamo bancario de **$6.400.000**
> (asiento 5). La unidad 5 dejó ajustados el arriendo y el seguro. Las cifras salen de
> `verificacion/caso_estampa_sur_contable.py`.

**El préstamo.** 24 cuotas mensuales al **1,15 %** mensual. El caso supone que el préstamo entra a
comienzos de marzo y que la primera cuota se paga el 01-04: el interés de marzo se devenga al
cierre.

**Pregunta.** ¿Qué ajuste hace el taller al 31-03, cómo se registra la primera cuota y cómo se
presentan sus deudas financieras en el balance?

**Desarrollo.**

1. **La cuota.** $C = 6{.}400{.}000 \times 0{,}0115 / (1 - 1{,}0115^{-24})$ = **$306.678,11**. En 24
   cuotas paga $7.360.274,63: **$960.274,63** de interés. (El script trabaja con decimales; en la
   práctica el banco redondea la cuota al peso y ajusta la última.)
2. **La tabla.** La planilla la genera con fórmulas, en la hoja «Caso Estampa Sur».

| Cuota N.º | Saldo inicial | Interés | Amortización | Cuota | Saldo final |
|---|---|---|---|---|---|
| 1 | 6.400.000,00 | 73.600,00 | 233.078,11 | 306.678,11 | 6.166.921,89 |
| 2 | 6.166.921,89 | 70.919,60 | 235.758,51 | 306.678,11 | 5.931.163,38 |
| 3 | 5.931.163,38 | 68.208,38 | 238.469,73 | 306.678,11 | 5.692.693,65 |
| 4 | 5.692.693,65 | 65.465,98 | 241.212,13 | 306.678,11 | 5.451.481,52 |
| 5 | 5.451.481,52 | 62.692,04 | 243.986,07 | 306.678,11 | 5.207.495,45 |
| 6 | 5.207.495,45 | 59.886,20 | 246.791,91 | 306.678,11 | 4.960.703,54 |
| 7 | 4.960.703,54 | 57.048,09 | 249.630,02 | 306.678,11 | 4.711.073,52 |
| 8 | 4.711.073,52 | 54.177,35 | 252.500,76 | 306.678,11 | 4.458.572,75 |
| 9 | 4.458.572,75 | 51.273,59 | 255.404,52 | 306.678,11 | 4.203.168,23 |
| 10 | 4.203.168,23 | 48.336,43 | 258.341,67 | 306.678,11 | 3.944.826,56 |
| 11 | 3.944.826,56 | 45.365,51 | 261.312,60 | 306.678,11 | 3.683.513,95 |
| 12 | 3.683.513,95 | 42.360,41 | 264.317,70 | 306.678,11 | 3.419.196,25 |
| 13 | 3.419.196,25 | 39.320,76 | 267.357,35 | 306.678,11 | 3.151.838,90 |
| 14 | 3.151.838,90 | 36.246,15 | 270.431,96 | 306.678,11 | 2.881.406,94 |
| 15 | 2.881.406,94 | 33.136,18 | 273.541,93 | 306.678,11 | 2.607.865,01 |
| 16 | 2.607.865,01 | 29.990,45 | 276.687,66 | 306.678,11 | 2.331.177,35 |
| 17 | 2.331.177,35 | 26.808,54 | 279.869,57 | 306.678,11 | 2.051.307,78 |
| 18 | 2.051.307,78 | 23.590,04 | 283.088,07 | 306.678,11 | 1.768.219,71 |
| 19 | 1.768.219,71 | 20.334,53 | 286.343,58 | 306.678,11 | 1.481.876,12 |
| 20 | 1.481.876,12 | 17.041,58 | 289.636,53 | 306.678,11 | 1.192.239,59 |
| 21 | 1.192.239,59 | 13.710,76 | 292.967,35 | 306.678,11 | 899.272,24 |
| 22 | 899.272,24 | 10.341,63 | 296.336,48 | 306.678,11 | 602.935,76 |
| 23 | 602.935,76 | 6.933,76 | 299.744,35 | 306.678,11 | 303.191,41 |
| 24 | 303.191,41 | 3.486,70 | 303.191,41 | 306.678,11 | 0,00 |

3. **Los asientos.**

| N.º | Fecha | Cuenta | Debe | Haber | Glosa |
|---|---|---|---|---|---|
| 5 | marzo | Banco | 6.400.000,00 | | préstamo bancario (unidad 2) |
| | | Préstamo bancario | | 6.400.000,00 | |
| A6.1 | 31-03 | Gasto financiero | 73.600,00 | | interés de marzo devengado |
| | | Intereses por pagar | | 73.600,00 | |
| | 01-04 | Préstamo bancario | 233.078,11 | | cuota 1 |
| | | Intereses por pagar | 73.600,00 | | |
| | | Banco | | 306.678,11 | |

Después de la cuota 1 el taller debe **$6.166.921,89**.

4. **El balance al 31-03.**

| Pasivo | Monto | Por qué |
|---|---|---|
| Porción corriente del préstamo | 2.980.803,75 | amortización de las cuotas 1 a 12 (abril a marzo siguiente) |
| Intereses por pagar | 73.600,00 | interés de marzo, se paga el 01-04 |
| **Pasivo financiero corriente** | **3.054.403,75** | |
| Préstamo bancario a largo plazo | 3.419.196,25 | saldo después de la cuota 12 |
| Documentos por pagar a largo plazo | 8.750.000 | saldo de la máquina, vence en 3 años |
| **Pasivo financiero no corriente** | **12.169.196,25** | |
| **Total** | **15.223.600,00** | 6.400.000 + 73.600 + 8.750.000 |

El documento de la máquina pasa al corto plazo cuando le queden 12 meses, a los 24 meses de la
compra.

**Lectura.** De los $15.223.600 que el taller debe por financiamiento, solo $3.054.403,75 vencen
dentro de un año; la máquina se paga con plazo largo, como corresponde a un activo que dura cinco
años. El resultado de marzo carga **$73.600** de gasto financiero, nada de la amortización. El
documento de $8.750.000 no tiene interés explícito, pero lo esconde: al 12 % anual que usó Finanzas
(unidad 5), vale hoy $6.228.077, así que unos $2.521.923 de su valor nominal son interés implícito de
tres años. El caso lo registra a valor nominal, como el curso.

**Lo que pasa a la siguiente.** La unidad 8 lleva el gasto financiero de $73.600 al estado de
resultados de marzo, bajo el resultado operacional, y usa esta separación entre corriente y no
corriente para la razón corriente y el endeudamiento.

---

## 13. Para seguir

**En los libros del ramo.**

- Gálvez y Clarke, *Contabilidad financiera para la dirección de empresas*, Ediciones UC (texto
  obligatorio del programa): los capítulos de pasivos.
- Weygandt, Kimmel y Kieso, *Accounting Principles*, 12.ª ed., Wiley, 2014 (complementario del
  programa): los capítulos de pasivos corrientes y de pasivos de largo plazo.
- Para la cuota y la tabla: Finanzas, unidad 4 de esta base.

**Abierto y gratis.**

- OpenStax, *Principles of Accounting, Volume 1: Financial Accounting*, en inglés, capítulo 12
  (pasivos corrientes: porción corriente de una deuda de largo plazo, documentos por pagar de corto
  plazo y remuneraciones) y capítulo 13 (pasivos de largo plazo y amortización por el método del
  interés efectivo). Licencia CC BY-NC-SA 4.0:
  https://openstax.org/books/principles-financial-accounting/pages/12-why-it-matters

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un préstamo en cuotas cuya cuota venza a
mitad de mes y una fecha de cierre; déjame escribir el ajuste del interés, la cuota siguiente y la
porción corriente, y corrígeme».
