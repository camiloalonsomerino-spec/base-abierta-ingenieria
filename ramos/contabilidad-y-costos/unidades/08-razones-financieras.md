---
ramo: Contabilidad y Costos
unidad: 8
titulo: Estados financieros y razones financieras
version: 0.1 (16-10-2026)
requiere: [01-contabilidad-y-estados-financieros, 05-ajustes-de-cierre, 06-prestamos-e-intereses, 07-inventarios]
alimenta: [10-absorcion-y-variable, 12-costo-volumen-utilidad]
verificacion: verificacion/u08_razones.py
---

# Unidad 8 · Estados financieros y razones financieras

**Qué vas a poder hacer.** Armar el estado de resultados por función y el balance clasificado desde
los saldos de las cuentas; calcular las razones de liquidez, endeudamiento, actividad y rentabilidad;
leer qué dice cada una de la empresa; predecir cómo mueve una operación esas razones, y usarlas para
decidir (pedir un crédito, pagar a un proveedor, comparar dos años o dos empresas).

**Lo que necesitas antes.** Qué es activo, pasivo y patrimonio, y la ecuación contable (unidad 1); los
ajustes de cierre que dejan los saldos al día (unidad 5); la separación de una deuda en porción
corriente y no corriente (unidad 6); y que el método de inventario cambia el costo de ventas y el
saldo de existencias (unidad 7).

**Tiempo.** Unas 4,5 horas: 2 de lectura con el ejemplo y 2,5 de práctica.

---

## 1. La idea

Los estados financieros resumen la contabilidad en dos fotos que se leen juntas:

- El **estado de resultados** cuenta lo que pasó **durante** un período: cuánto se vendió, cuánto
  costó y cuánto quedó.
- El **balance** (estado de situación financiera) muestra lo que hay **al cierre**: qué tiene la
  empresa, a quién le debe y cuánto es de los dueños.

Un número suelto dice poco. Que una empresa deba $27.000.000 no es bueno ni malo: depende de cuánto
tiene, cuánto vende y cuándo vence esa deuda. Una **razón financiera** divide dos partidas para que la
comparación tenga sentido: con el año anterior, con otra empresa del rubro o con lo que exige un
banco. Las razones no reemplazan a los estados: son preguntas que se le hacen a los estados.

---

## 2. El estado de resultados por función

Ordena los ingresos y gastos según **para qué** se gastó (producir, vender, administrar, financiar),
con un subtotal en cada escalón:

| Línea | Qué es |
|---|---|
| Ingresos por ventas | ventas netas, sin IVA |
| − Costo de ventas | lo que costó lo vendido (unidad 7; en una fábrica, unidad 10) |
| **= Margen bruto** | lo que deja el producto |
| − Gastos de administración y de ventas | lo que cuesta operar la empresa |
| **= Resultado operacional** | lo que deja el negocio (UAII: utilidad antes de intereses e impuestos) |
| ± Otros ingresos y gastos no operacionales | arriendos ganados, gastos financieros |
| **= Resultado antes de impuesto** | |
| − Impuesto a la renta | se calcula aparte, según la ley |
| **= Utilidad (o pérdida) del ejercicio** | va al patrimonio |

Cada escalón responde una pregunta distinta. Un margen bruto chico dice que el producto se vende
barato o se produce caro; un resultado operacional chico con buen margen bruto dice que la estructura
pesa; un resultado final chico con buen resultado operacional dice que la deuda pesa. Por eso el
**gasto financiero va debajo** del resultado operacional: el negocio puede ser bueno y la forma de
financiarlo, mala.

---

## 3. El balance clasificado

El balance separa activos y pasivos por **plazo**: corriente es lo que se convierte en dinero o se
paga dentro de los 12 meses siguientes al cierre; no corriente, lo que tarda más.

| Activo | Pasivo y patrimonio |
|---|---|
| **Corriente:** caja y banco, clientes, existencias, pagos anticipados, remanente de IVA | **Corriente:** proveedores, sueldos e impuestos por pagar, intereses por pagar, porción corriente de los préstamos |
| **No corriente:** maquinaria, vehículos y edificios (menos su depreciación acumulada), terrenos | **No corriente:** préstamos y documentos que vencen después de 12 meses |
| | **Patrimonio:** capital, utilidades retenidas, utilidad del ejercicio |

Tres reglas que se olvidan:

- La **depreciación acumulada** va restando dentro del activo no corriente, no en el pasivo. El
  **terreno no se deprecia**.
- Un préstamo en cuotas se **parte en dos**: lo que se amortiza en los próximos 12 meses es pasivo
  corriente (unidad 6). Dejarlo entero en el largo plazo hace ver a la empresa más líquida.
- La **utilidad del ejercicio** del estado de resultados es la que cierra el balance. Si el balance no
  cuadra, el error está en una cuenta, no en la ecuación.

---

## 4. Razones de liquidez · ¿puede pagar lo que vence pronto?

$$\text{liquidez corriente} = \frac{\text{activo corriente}}{\text{pasivo corriente}} \qquad \text{prueba ácida} = \frac{\text{activo corriente} - \text{inventarios}}{\text{pasivo corriente}}$$

$$\text{capital de trabajo} = \text{activo corriente} - \text{pasivo corriente}$$

- **Liquidez corriente** (o razón circulante): cuántos pesos de activo corriente hay por cada peso que
  vence en el año. Como referencia del curso, entre 1,5 y 2 es cómodo; bajo 1,5 empieza el riesgo de
  no pagar a tiempo, y muy sobre 2 puede haber plata ociosa.
- **Prueba ácida:** lo mismo, sin las existencias, porque el inventario hay que venderlo (y cobrarlo)
  antes de que sea dinero. Bajo 1, la empresa depende de vender para pagar. Una versión más exigente
  también saca los pagos anticipados, que nunca se convierten en dinero.
- **Capital de trabajo:** el colchón en pesos.

Cuándo no aplica: un supermercado vive con prueba ácida bajo 1 sin problema, porque vende al contado y
le paga a 60 días a sus proveedores. La razón se compara con el rubro, no con una regla universal.

---

## 5. Razones de endeudamiento · ¿quién financia la empresa?

$$\frac{\text{pasivo}}{\text{patrimonio}} \qquad \frac{\text{pasivo}}{\text{activo}} \qquad \frac{\text{pasivo no corriente}}{\text{pasivo}} \qquad \text{cobertura de gastos financieros} = \frac{\text{resultado operacional}}{\text{gastos financieros}}$$

- **Pasivo / patrimonio:** cuántos pesos ponen los acreedores por cada peso de los dueños. Sobre 1,
  los acreedores financian más que los dueños.
- **Pasivo / activo:** qué parte de los activos se financia con deuda.
- **Estructura del pasivo:** qué parte vence en el largo plazo. La misma deuda es más tranquila si vence
  en cinco años que si vence este.
- **Cobertura:** cuántas veces el resultado operacional paga los intereses.

---

## 6. Razones de actividad · ¿qué tan rápido gira?

$$\text{rotación de inventario} = \frac{\text{costo de ventas}}{\text{inventario}} \qquad \text{días de inventario} = \frac{\text{días del período}}{\text{rotación}}$$

$$\text{rotación de cuentas por cobrar} = \frac{\text{ventas}}{\text{clientes}} \qquad \text{días de cobro} = \frac{\text{días del período}}{\text{rotación}}$$

- La rotación de inventario va con **costo de ventas**, no con ventas: el inventario está a costo.
- Si hay datos, se usa el **inventario promedio** (inicial más final, dividido por 2); con el final
  solo, la razón se mueve con lo que pasó el último día.
- **Clientes incluye IVA** y las ventas no. Con las ventas netas, los días de cobro salen inflados en
  cerca de un 19 %; la versión correcta usa las ventas con IVA. Las dos aparecen en los ejercicios.
- Los días dependen del período: 365 para un año (algunos usan 360), 31 para marzo.

---

## 7. Razones de rentabilidad · ¿cuánto deja?

$$\text{margen bruto} = \frac{\text{margen bruto}}{\text{ventas}} \qquad \text{margen neto} = \frac{\text{utilidad}}{\text{ventas}}$$

$$\text{ROA} = \frac{\text{resultado operacional}}{\text{activo}} \qquad \text{ROE} = \frac{\text{utilidad}}{\text{patrimonio}}$$

- **ROA** (rentabilidad de los activos): lo que el negocio rinde sobre todo lo que usa, antes de
  intereses e impuestos. Mide al negocio, no a su financiamiento.
- **ROE** (rentabilidad del patrimonio): lo que les queda a los dueños por cada peso que pusieron.

Las tres piezas del ROE (la identidad de DuPont) muestran de dónde sale:

$$\text{ROE} = \frac{\text{utilidad}}{\text{ventas}} \times \frac{\text{ventas}}{\text{activo}} \times \frac{\text{activo}}{\text{patrimonio}}$$

Margen, rotación de activos y apalancamiento. Un ROE alto puede venir de vender con buen margen, de
usar bien los activos o de endeudarse mucho; las tres cosas no son igual de sanas.

Cuidado con los períodos: un ROE de un mes no se compara con uno anual, y multiplicarlo por 12 supone
que todos los meses son iguales.

---

## 8. Ejemplo resuelto · una ferretería que pide un crédito

Una ferretería cierra el año 2025 con estos saldos, ya ajustados. Ventas netas $96.400.000; costo de
ventas $63.700.000; gastos de administración y ventas $22.950.000; gastos financieros $1.480.000;
impuesto a la renta $2.105.000 (dato de su contador). Caja y banco $6.840.000; clientes $9.120.000;
existencias $14.350.000; seguro pagado por anticipado $1.260.000; vehículos $18.900.000 con
depreciación acumulada de $5.670.000; terreno $11.500.000; proveedores $10.480.000; IVA por pagar
$1.150.000; sueldos por pagar $2.310.000; préstamo bancario $13.400.000, de los que $3.600.000 vencen
en 2026; capital $20.000.000. Falta un dato: las utilidades retenidas de años anteriores.

Para comprar otra camioneta, quiere pedir un crédito de **$5.800.000 a cuatro años**. El banco exige
liquidez corriente de al menos 1,5 y un pasivo que no supere al patrimonio.

**Paso 1 · Estado de resultados de 2025.**

| Línea | Pesos |
|---|---|
| Ventas | 96.400.000 |
| − Costo de ventas | 63.700.000 |
| **Margen bruto** | **32.700.000** |
| − Gastos de administración y ventas | 22.950.000 |
| **Resultado operacional** | **9.750.000** |
| − Gastos financieros | 1.480.000 |
| **Resultado antes de impuesto** | **8.270.000** |
| − Impuesto a la renta | 2.105.000 |
| **Utilidad del ejercicio** | **6.165.000** |

**Paso 2 · Balance al 31-12-2025.** El préstamo se parte en $3.600.000 corrientes y $9.800.000 no
corrientes. Los vehículos van netos: 18.900.000 − 5.670.000 = $13.230.000.

| Activo | Pesos | Pasivo y patrimonio | Pesos |
|---|---|---|---|
| Caja y banco | 6.840.000 | Proveedores | 10.480.000 |
| Clientes | 9.120.000 | IVA por pagar | 1.150.000 |
| Existencias | 14.350.000 | Sueldos por pagar | 2.310.000 |
| Seguro pagado por anticipado | 1.260.000 | Préstamo bancario (corto plazo) | 3.600.000 |
| **Activo corriente** | **31.570.000** | **Pasivo corriente** | **17.540.000** |
| Vehículos (netos) | 13.230.000 | Préstamo bancario (largo plazo) | 9.800.000 |
| Terreno | 11.500.000 | **Pasivo no corriente** | **9.800.000** |
| **Activo no corriente** | **24.730.000** | Capital | 20.000.000 |
| | | Utilidades retenidas | 2.795.000 |
| | | Utilidad del ejercicio | 6.165.000 |
| | | **Patrimonio** | **28.960.000** |
| **Total activo** | **56.300.000** | **Total pasivo y patrimonio** | **56.300.000** |

El activo suma $56.300.000 y el pasivo $27.340.000, así que el patrimonio es $28.960.000. Restando el
capital y la utilidad del año, las utilidades retenidas son **$2.795.000**.

**Paso 3 · Las razones.**

| Razón | Cálculo | Valor |
|---|---|---|
| Liquidez corriente | 31.570.000 / 17.540.000 | 1,80 |
| Prueba ácida | (31.570.000 − 14.350.000) / 17.540.000 | 0,98 |
| Capital de trabajo | 31.570.000 − 17.540.000 | 14.030.000 |
| Pasivo / patrimonio | 27.340.000 / 28.960.000 | 0,94 |
| Pasivo / activo | 27.340.000 / 56.300.000 | 48,6 % |
| Pasivo no corriente / pasivo | 9.800.000 / 27.340.000 | 35,8 % |
| Rotación de inventario | 63.700.000 / 14.350.000 | 4,44 (82,2 días) |
| Rotación de clientes | 96.400.000 / 9.120.000 | 10,57 (34,5 días) |
| Rotación de clientes con IVA | 96.400.000 × 1,19 / 9.120.000 | 12,58 (29,0 días) |
| Margen bruto | 32.700.000 / 96.400.000 | 33,9 % |
| Margen neto | 6.165.000 / 96.400.000 | 6,4 % |
| ROA | 9.750.000 / 56.300.000 | 17,3 % |
| ROE | 6.165.000 / 28.960.000 | 21,3 % |
| Cobertura de gastos financieros | 9.750.000 / 1.480.000 | 6,6 |

**Paso 4 · El crédito.** El crédito nuevo es de largo plazo y la camioneta es activo no corriente: la
liquidez corriente no se mueve (salvo por la cuota del primer año, que pasaría a corriente). El pasivo
sí: (27.340.000 + 5.800.000) / 28.960.000 = **1,14**. Pasa la exigencia de liquidez y **no pasa la de
endeudamiento**: con el patrimonio actual, el pasivo solo puede crecer **$1.620.000**.

**Cómo se lee.** La ferretería es sana: buena liquidez, margen razonable, cobra en un mes y paga sus
intereses más de seis veces. Su punto débil es el inventario (y que el 64,2 % de su deuda vence en el año): tiene casi tres meses de mercadería y
por eso la prueba ácida queda bajo 1; si las ventas se frenan, pagar a los proveedores depende de
liquidar existencias. Para la camioneta tiene tres caminos: financiar con deuda solo lo que cabe y
poner el resto de caja (le sobra capital de trabajo), esperar a que la utilidad de 2026 engorde el
patrimonio, o bajar el inventario y usar esa plata. Pedir el crédito completo es justo lo que el banco
no aceptará.

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Rotación de inventario con ventas | El inventario está a costo: va con costo de ventas |
| Días de cobro con ventas netas contra clientes con IVA | Usa las ventas con IVA, o advierte que los días salen inflados cerca de un 19 % |
| Dejar todo el préstamo en el largo plazo | La amortización de los próximos 12 meses es pasivo corriente |
| Depreciación acumulada en el pasivo, o terreno depreciado | La depreciación resta dentro del activo; el terreno no se deprecia |
| Poner el gasto financiero sobre el resultado operacional | Va debajo: el resultado operacional mide el negocio, no su financiamiento |
| Mezclar costo y gasto en el estado de resultados | El costo de lo producido va al costo de ventas; administración y ventas son gastos del período |
| Comparar un ROE mensual con uno anual | Compara períodos iguales; multiplicar por 12 supone meses iguales |
| Leer una razón sola | Compárala con el año anterior, con el rubro y con las otras razones |
| Comparar el margen de dos empresas sin mirar su método de inventario | Con alza de precios FIFO muestra más margen que PPP (unidad 7) |
| Celebrar que la liquidez subió por pagar a los proveedores | Pagar deuda corriente con caja sube la razón si está sobre 1, pero la empresa tiene menos plata |

---

## 10. Práctica

Diez ejercicios: 8.1 a 8.4 básicos, 8.5 a 8.8 intermedios, 8.9 y 8.10 de desafío. Las pautas están en la
sección 11. La planilla `planillas/u08_razones.xlsx` trae el ejemplo y el caso con fórmulas.

**8.1 · El estado por función (básico).** Una distribuidora tuvo en el año ventas netas por
$41.850.000, costo de ventas $27.630.000, gastos de administración $6.920.000, gastos de ventas
$3.140.000, gastos financieros $865.000, un arriendo ganado por una bodega que no usa de $420.000 e
impuesto a la renta de $1.010.000. Arma el estado de resultados por función y calcula el margen bruto,
el operacional y el neto.

**8.2 · El balance clasificado (básico).** Al 31-12-2025 una distribuidora tiene: banco $3.415.000;
clientes $5.280.000; mercaderías $7.960.000; arriendo pagado por anticipado $900.000; maquinaria
$16.400.000; depreciación acumulada de la maquinaria $4.920.000; terreno $9.300.000; proveedores
$6.140.000; remuneraciones por pagar $1.870.000; IVA por pagar $640.000; préstamo bancario $8.200.000,
del que $2.050.000 se amortiza en 2026; capital $18.000.000. Arma el balance clasificado y calcula la
utilidad del ejercicio que lo cuadra.

**8.3 · Liquidez (básico).** Con el balance de 8.2: liquidez corriente, prueba ácida (la del curso y la
que además saca el arriendo anticipado) y capital de trabajo. ¿Qué dicen?

**8.4 · Endeudamiento (básico).** Con el balance de 8.2: pasivo / patrimonio, pasivo / activo, y qué
parte del pasivo es de corto y de largo plazo.

**8.5 · Rotaciones (intermedio).** La misma distribuidora vendió $58.300.000 netos en 2025 con un costo
de ventas de $39.900.000; sus mercaderías al 31-12-2024 eran $7.240.000. Calcula la rotación de
inventario y sus días con el inventario final y con el promedio, y la rotación de clientes y sus días
con ventas netas y con ventas con IVA. Si da 30 días de crédito a sus clientes, ¿cobra a tiempo?

**8.6 · Rentabilidad y DuPont (intermedio).** La misma distribuidora tuvo un resultado operacional de
$5.150.000, y su utilidad es la que cuadró el balance de 8.2. Calcula ROA, ROE, margen neto, rotación
de activos y el multiplicador activo / patrimonio, y comprueba que su producto da el ROE.

**8.7 · Dos años (intermedio).** Una empresa presenta:

| | 2024 | 2025 |
|---|---|---|
| Activo corriente | 12.600.000 | 15.900.000 |
| Inventario | 4.100.000 | 7.850.000 |
| Pasivo corriente | 6.300.000 | 9.940.000 |
| Pasivo total | 14.800.000 | 22.600.000 |
| Patrimonio | 18.500.000 | 19.700.000 |
| Ventas | 47.200.000 | 51.900.000 |
| Utilidad | 2.830.000 | 2.170.000 |

Calcula para cada año la liquidez, la prueba ácida, el capital de trabajo, pasivo / patrimonio, margen
neto y ROE, y el crecimiento de las ventas. ¿Mejoró o empeoró? ¿Qué pasó con el inventario?

**8.8 · Una operación a la vez (intermedio).** Una empresa tiene activo corriente $17.640.000 (con
$5.880.000 de inventario) y pasivo corriente $11.760.000. Calcula su liquidez y su prueba ácida, y cómo
quedan con cada operación, por separado: (a) paga $2.940.000 a proveedores; (b) compra mercadería a
crédito por $2.350.000 netos más IVA; (c) recibe un préstamo a cinco años por $4.700.000; (d) compra
al contado una máquina de $3.900.000 netos más IVA.

**8.9 · El método de inventario en las razones (desafío).** Una comercializadora tuvo ventas por
$30.500.000 y $22.600.000 de mercadería disponible (inventario inicial más compras). Su inventario
final vale $4.380.000 con FIFO o $4.150.000 con PPP. Sus gastos de operación fueron $7.400.000, su otro
activo corriente $6.900.000 y su pasivo corriente $7.200.000. Calcula con cada método el costo de
ventas, el margen bruto, el resultado operacional, la liquidez, la prueba ácida y la rotación de
inventario. ¿Qué método la hace ver mejor y qué cambia de verdad?

**8.10 · El balance desde sus razones (desafío).** De una empresa se sabe: activo total $40.000.000;
pasivo / activo 0,45; el 60 % del pasivo es corriente; liquidez corriente 1,6; prueba ácida 0,9;
rotación de inventario 5 veces al año (sobre el inventario final); margen bruto 30 %; ROE 12 %.
Reconstruye el balance resumido (activo corriente, inventario, activo no corriente, pasivo corriente,
no corriente y patrimonio), las ventas y la utilidad, y el margen neto.

---

## 11. Pautas

**8.1.**

| Línea | Pesos |
|---|---|
| Ventas | 41.850.000 |
| − Costo de ventas | 27.630.000 |
| **Margen bruto** | **14.220.000** |
| − Gastos de administración y de ventas (6.920.000 + 3.140.000) | 10.060.000 |
| **Resultado operacional** | **4.160.000** |
| + Arriendo ganado (no operacional) | 420.000 |
| − Gastos financieros | 865.000 |
| **Resultado antes de impuesto** | **3.715.000** |
| − Impuesto a la renta | 1.010.000 |
| **Utilidad del ejercicio** | **2.705.000** |

Margen bruto **34,0 %**, operacional **9,9 %** y neto **6,5 %**. El arriendo ganado va debajo del
resultado operacional porque no es el negocio: si se mezclara arriba, la operación se vería mejor de
lo que es.

**8.2.** La maquinaria va neta: 16.400.000 − 4.920.000 = **$11.480.000**. El préstamo se parte en
$2.050.000 corrientes y $6.150.000 no corrientes.

| Activo | Pesos | Pasivo y patrimonio | Pesos |
|---|---|---|---|
| Banco | 3.415.000 | Proveedores | 6.140.000 |
| Clientes | 5.280.000 | Remuneraciones por pagar | 1.870.000 |
| Mercaderías | 7.960.000 | IVA por pagar | 640.000 |
| Arriendo pagado por anticipado | 900.000 | Préstamo bancario (corto plazo) | 2.050.000 |
| **Activo corriente** | **17.555.000** | **Pasivo corriente** | **10.700.000** |
| Maquinaria (neta) | 11.480.000 | Préstamo bancario (largo plazo) | 6.150.000 |
| Terreno | 9.300.000 | **Pasivo no corriente** | **6.150.000** |
| **Activo no corriente** | **20.780.000** | Capital | 18.000.000 |
| | | Utilidad del ejercicio | 3.485.000 |
| | | **Patrimonio** | **21.485.000** |
| **Total activo** | **38.335.000** | **Total pasivo y patrimonio** | **38.335.000** |

El pasivo suma $16.850.000; el patrimonio que cuadra es $21.485.000 y la utilidad del ejercicio,
**$3.485.000**.

**8.3.** Liquidez: 17.555.000 / 10.700.000 = **1,64**. Prueba ácida: 9.595.000 / 10.700.000 = **0,90**;
sin el arriendo anticipado, **0,81**. Capital de trabajo: **$6.855.000**. Paga cómodo lo que vence en el
año si vende su mercadería; sin venderla, cubre nueve décimos. El arriendo anticipado no se
puede usar para pagar a nadie: por eso la versión estricta lo saca.

**8.4.** Pasivo / patrimonio: 16.850.000 / 21.485.000 = **0,78**. Pasivo / activo: **44,0 %** (los
dueños financian el 56,0 %). El **63,5 %** del pasivo vence en el año y el **36,5 %** después. Está
financiada sobre todo por sus dueños, pero la deuda que tiene es mayormente de corto plazo: por eso la
liquidez importa.

**8.5.** Con el inventario final: 39.900.000 / 7.960.000 = **5,01** veces, **72,8** días. Con el
promedio, (7.240.000 + 7.960.000) / 2 = **$7.600.000**: **5,25** veces, **69,5** días. Clientes con
ventas netas: 58.300.000 / 5.280.000 = **11,04**, **33,1** días. Con ventas con IVA ($69.377.000):
**13,14**, **27,8** días. La versión correcta dice que cobra a tiempo (menos de 30 días); la de ventas
netas haría creer que se atrasa tres días. El inventario subió en el año, por eso la razón con el final
se ve peor que con el promedio.

**8.6.** ROA: 5.150.000 / 38.335.000 = **13,4 %**. ROE: 3.485.000 / 21.485.000 = **16,2 %**. Margen
neto: **5,98 %**; rotación de activos: **1,52**; multiplicador: **1,784**. Producto:
0,0598 × 1,52 × 1,784 = 16,2 % ✓. La utilidad sobre el activo total es 9,1 % y el ROE es más alto
porque cada peso de los dueños mueve 1,78 pesos de activos: la deuda amplifica.

**8.7.**

| | 2024 | 2025 |
|---|---|---|
| Liquidez corriente | 2,00 | 1,60 |
| Prueba ácida | 1,35 | 0,81 |
| Capital de trabajo | 6.300.000 | 5.960.000 |
| Pasivo / patrimonio | 0,80 | 1,15 |
| Margen neto | 6,0 % | 4,2 % |
| ROE | 15,3 % | 11,0 % |

Las ventas crecieron **10,0 %**, pero empeoró casi todo. El inventario creció **91,5 %**, mucho más que
las ventas, y se financió con deuda de corto plazo (el pasivo corriente subió $3.640.000): por eso la
prueba ácida cayó bajo 1 y el endeudamiento pasó de 1. Vende más, gana menos por peso vendido y
acumula mercadería. La pregunta para la gerencia es si ese inventario se va a vender o está obsoleto.

**8.8.** Base: liquidez **1,50** y prueba ácida **1,00**.

| Operación | Activo corriente | Pasivo corriente | Liquidez | Prueba ácida |
|---|---|---|---|---|
| (a) paga 2.940.000 a proveedores | 14.700.000 | 8.820.000 | 1,667 | 1,000 |
| (b) compra a crédito: 2.350.000 + IVA 446.500 = 2.796.500 | 20.436.500 | 14.556.500 | 1,404 | 0,839 |
| (c) préstamo a cinco años por 4.700.000 | 22.340.000 | 11.760.000 | 1,900 | |
| (d) máquina al contado, 3.900.000 + IVA 741.000 | 13.740.000 | 11.760.000 | 1,168 | |

(a) Pagar sube la razón porque estaba sobre 1: resta lo mismo arriba y abajo. La empresa no está mejor,
tiene menos caja. (b) La compra entra al inventario y el IVA crédito es activo corriente; la deuda
entra entera al pasivo corriente: la liquidez baja y la ácida baja más. (c) Entra caja sin deuda
corriente: sube. (d) Sale caja hacia un activo no corriente; el IVA vuelve como crédito fiscal, así que
el activo corriente baja solo en el neto. Financiar una máquina con caja de corto plazo es lo que más
castiga la liquidez.

**8.9.**

| | FIFO | PPP |
|---|---|---|
| Costo de ventas (disponible − inventario final) | 18.220.000 | 18.450.000 |
| Margen bruto | 12.280.000 (40,3 %) | 12.050.000 (39,5 %) |
| Resultado operacional | 4.880.000 | 4.650.000 |
| Liquidez corriente | 1,567 | 1,535 |
| Prueba ácida | 0,958 | 0,958 |
| Rotación de inventario | 4,16 (87,7 días) | 4,45 (82,1 días) |

FIFO la hace ver mejor en margen, resultado y liquidez: $230.000 más de resultado, que son exactamente
los $230.000 más de inventario. La prueba ácida no cambia porque saca el inventario. Lo único real que
cambia es el impuesto, si se calcula sobre ese resultado; la caja de la operación es la misma. Y el PPP
muestra mejor rotación, porque su inventario vale menos. Por eso dos empresas solo se comparan con el
mismo método (o ajustando).

**8.10.** Pasivo: 0,45 × 40.000.000 = **$18.000.000**; patrimonio **$22.000.000**. Pasivo corriente:
60 % = **$10.800.000**; no corriente **$7.200.000**. Activo corriente: 1,6 × 10.800.000 =
**$17.280.000**. La prueba ácida da el activo corriente sin inventario: 0,9 × 10.800.000 =
**$9.720.000**, así que el inventario es **$7.560.000**. Activo no corriente: **$22.720.000**. Costo de
ventas: 5 × 7.560.000 = **$37.800.000**; con margen bruto de 30 %, ventas = 37.800.000 / 0,70 =
**$54.000.000**. Utilidad: 12 % × 22.000.000 = **$2.640.000**; margen neto **4,89 %**. Las razones son
ecuaciones: con suficientes, el balance se despeja.

---

## 12. Caso integrador · el cierre de marzo de Estampa Sur

> Las unidades 2 a 7 dejaron todo registrado: los 12 asientos del mes, el IVA, la depreciación, los
> ajustes del arriendo y el seguro, el interés del préstamo y la tarjeta de las poleras lisas. Falta
> juntarlo en los dos estados.

**Lo que recibe.**

- Del balance inicial (unidad 1) y los 12 asientos (unidad 2): ventas netas de $25.726.200, 60 % al
  contado; las compras de materiales; la máquina nueva con su pie y su documento a tres años; el
  préstamo de $6.400.000; los pagos de sueldos, arriendo, seguro y gastos de administración (luz,
  internet y mantención, $436.000).
- Del IVA (unidad 3): un remanente de crédito fiscal de **$1.224.837**, que queda como activo.
- De los ajustes: depreciación de **$310.833** (unidad 4); arriendo de marzo **$580.000** y seguro
  **$79.000** devengados (unidad 5); interés devengado **$73.600**, la cuota de **$306.678** y la porción
  del préstamo que se amortiza en los próximos 12 meses (unidad 6).
- De la unidad 7: las 764 poleras lisas a $1.860.340 (PPP) y una variación de precio de **$78.260**.
- Del costeo por absorción (unidades 10 y 11): los costos fijos de fabricación del mes (sueldos,
  depreciación, arriendo y seguro: **$3.849.833**) se reparten entre las prendas producidas. La
  producción completa cuesta **$20.941.203** a estándar y lo vendido, **$19.853.906**.

**Pregunta.** ¿Cuánto ganó Estampa Sur en marzo? ¿Cómo queda su balance al 31 de marzo? ¿Qué dicen las
razones, y qué decide Valentina?

**Desarrollo.**

1. **El estado de resultados.** El caso costea a estándar; el balance, en cambio, tiene las poleras a
   su costo real, así que la variación de la unidad 7 se reconoce en el mes:

| Línea | A costo estándar | Con la variación de precio |
|---|---|---|
| Ventas | 25.726.200 | 25.726.200 |
| − Costo de ventas a estándar | 19.853.906 | 19.853.906 |
| − Variación de precio de materias primas | | 78.260 |
| **Costo de ventas** | 19.853.906 | **19.932.166** |
| **Margen bruto** | **5.872.294** (22,8 %) | **5.794.034** (22,5 %) |
| − Gastos de administración | 436.000 | 436.000 |
| **Resultado operacional** | **5.436.294** | **5.358.034** |
| − Gastos financieros | 73.600 | 73.600 |
| **Resultado antes de impuesto** | **5.362.694** (20,8 %) | **5.284.434** (20,5 %) |

El impuesto a la renta no se calcula en este ramo; el resultado antes de impuesto queda en el
patrimonio.

2. **El balance.** Se pasan por las cuentas el saldo inicial, los 12 asientos, el cierre del IVA, los
   ajustes y la producción: los materiales salen de bodega a estándar (la diferencia a la cuenta de
   variación), los costos fijos de fabricación se cargan a la producción, la producción pasa a
   Productos terminados y lo vendido sale a Costo de ventas.

| Activo | Pesos | Pasivo y patrimonio | Pesos |
|---|---|---|---|
| Banco | 12.944.237 | Proveedores | 18.221.256 |
| Clientes | 12.245.671 | Insumos por facturar | 265.760 |
| Remanente de IVA crédito fiscal | 1.224.837 | Intereses por pagar | 73.600 |
| Poleras lisas básicas | 1.860.340 | Préstamo bancario (corto plazo) | 2.980.804 |
| Tinta | 82.500 | **Pasivo corriente** | **21.541.420** |
| Productos terminados | 1.087.298 | Préstamo bancario (largo plazo) | 3.419.196 |
| Arriendo pagado por anticipado | 1.740.000 | Documentos por pagar a largo plazo | 8.750.000 |
| Seguro pagado por anticipado | 869.000 | **Pasivo no corriente** | **12.169.196** |
| **Activo corriente** | **32.053.883** | Capital | 14.428.000 |
| Maquinaria | 24.140.000 | Resultado del ejercicio | 5.284.434 |
| Depreciación acumulada | −2.770.833 | **Patrimonio** | **19.712.434** |
| **Activo no corriente** | **21.369.167** | | |
| **Total activo** | **53.423.050** | **Total pasivo y patrimonio** | **53.423.050** |

Cuatro partidas piden explicación:

- **Productos terminados** son las 290 prendas producidas y no vendidas, a costo de absorción: llevan
  dentro **$199.617** de costos fijos que se irán al resultado cuando se vendan (unidad 10). Absorbe
  además el peso de redondeo de las demás partidas.
- **Tinta** son los 5 kg que quedan después de que la producción usó 78,317 kg.
- **Insumos por facturar** ($265.760) es una decisión de esta unidad: el costo variable de cada prenda
  incluye otros insumos (etiquetas, bolsas, energía de la estampadora) que ninguno de los 12 asientos
  pagó. Se consumieron en marzo, así que se reconocen como un pasivo devengado (unidad 5) hasta que
  llegue la factura; su IVA se registrará con ella.
- **Préstamo:** de los $6.400.000, las 12 cuotas siguientes amortizan $2.980.804 (corriente); el resto,
  $3.419.196, es lo que se deberá después de la cuota 12 (no corriente). El documento de la máquina
  vence a tres años: no corriente.

3. **Las razones de marzo.** Los flujos son de un mes y los días, 31.

| Razón | Valor | Lectura |
|---|---|---|
| Liquidez corriente | 1,49 | justo bajo el 1,5 de referencia |
| Prueba ácida | 1,35 | el inventario pesa poco (3.030.138) |
| Prueba ácida sin anticipados | 1,23 | |
| Capital de trabajo | 10.512.463 | |
| Pasivo / patrimonio | 1,71 | los acreedores financian más que los dueños |
| Pasivo / activo | 63,1 % | |
| Pasivo no corriente / pasivo | 36,1 % | dos tercios de la deuda vencen en el año |
| Rotación de inventario | 6,58 en el mes (4,7 días) | trabaja casi contra pedido |
| Rotación de clientes | 2,10 (14,8 días) | con IVA: 2,50 (12,4 días) |
| Margen bruto | 22,5 % | 22,8 % a estándar |
| Margen antes de impuesto | 20,5 % | 20,8 % a estándar |
| ROA (del mes) | 10,0 % | |
| ROE (del mes) | 26,8 % | por 12 daría 322 %: un mes no es un año |
| Cobertura de gastos financieros | 72,8 | el interés no pesa |

**Lectura.** El negocio de marzo es muy rentable: márgenes altos, inventario que gira en días y clientes
que pagan en dos semanas. Lo que se ve débil es el **financiamiento**: la máquina nueva se pagó con un
documento y un préstamo, y los materiales del mes se compraron a crédito. Proveedores es el **85 %** del
pasivo corriente. Por eso la liquidez queda bajo 1,5 y el pasivo ($33.710.616) es 1,71 veces el patrimonio, aunque el
banco tiene $12.944.237.

**Decisión.** Si Valentina usa **$10.000.000** del banco para pagar a proveedores, la liquidez sube a
**1,91** y el pasivo / patrimonio baja a **1,20**, y le quedan $2.944.237 en el banco, más los
$12.245.671 que cobrará en las próximas semanas. Antes de pedir más deuda (por ejemplo, para una tercera
máquina), conviene que el resultado de abril y mayo engorde el patrimonio: con 1,71 de pasivo por peso
propio, cualquier banco le pedirá garantías o más capital.

**Lo que pasa a las unidades siguientes.** A la unidad 10: el resultado operacional por absorción
($5.436.294 a estándar) y los $199.617 de costos fijos que quedaron en Productos terminados. A la unidad
12: los costos fijos operacionales del mes, con los que se calcula cuánto hay que vender para no perder.

---

## 13. Para seguir

**En los libros del ramo.**

- Gálvez y Clarke, *Contabilidad financiera para la dirección de empresas*, e Irarrázabal,
  *Contabilidad: fundamentos y usos* (2014), los dos de Ediciones UC y obligatorios en el programa: la
  preparación del balance y del estado de resultados, y su análisis.
- Weygandt, Kimmel y Kieso, *Accounting Principles* (Wiley, 12.ª ed., 2014), complementario: la parte de
  análisis de estados financieros, con las mismas razones y la identidad de DuPont.

**Abierto y gratis.**

- OpenStax, *Principles of Accounting, Volume 1: Financial Accounting*, en inglés, apéndice A
  (*Financial Statement Analysis*): capital de trabajo, liquidez corriente y ácida, endeudamiento,
  cobertura de intereses, rotaciones, márgenes, ROA y ROE. Licencia CC BY-NC-SA:
  https://openstax.org/books/principles-financial-accounting/pages/a-financial-statement-analysis

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame los saldos ajustados de una empresa
desordenados; déjame armar el balance clasificado y el estado de resultados, calcular diez razones y
explicar qué decidiría un banco, y corrígeme».
