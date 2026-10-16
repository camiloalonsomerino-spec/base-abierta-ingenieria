---
ramo: Contabilidad y Costos
unidad: 4
titulo: Activo fijo y depreciación
version: 0.1 (16-10-2026)
requiere: [02-partida-doble, 03-iva]
alimenta: [05-ajustes-de-cierre, 08-razones-financieras, 09-clasificacion-de-costos, 11-asignacion-de-costos-indirectos]
verificacion: verificacion/u04_depreciacion.py
---

# Unidad 4 · Activo fijo y depreciación

**Qué vas a poder hacer.** Determinar el costo con que un activo fijo entra a la contabilidad;
repartirlo en su vida útil con los métodos lineal, por unidades producidas, de saldo decreciente y
de suma de dígitos; registrar la depreciación de un ejercicio (también si el activo se compró a mitad
de año) y leer el valor libro; registrar la venta o la baja de un activo con su utilidad o pérdida;
corregir una estimación de vida útil, y separar lo que la contabilidad informa de lo que sirve para
decidir.

**Lo que necesitas antes.** La partida doble (unidad 2) y el IVA (unidad 3): un activo comprado con
factura entra por su neto y el IVA va al crédito fiscal.

**Tiempo.** Unas 4,5 horas: 2 de lectura con el ejemplo y 2,5 de práctica. La planilla
`planillas/u04_depreciacion.xlsx` trae los cuatro métodos del ejemplo y la tabla mensual de las dos
máquinas del caso, con fórmulas.

---

## 1. La idea · repartir un costo entre los años que lo usan

Un **activo fijo** (en las normas actuales, *propiedades, planta y equipo*) es un bien tangible que
la empresa compra para usarlo, no para venderlo, durante más de un período: máquinas, vehículos,
edificios, computadores, muebles, terrenos.

Si una panadería compra un horno de $9.040.000 que va a durar seis años, cargar los $9.040.000 como
gasto del mes de compra sería absurdo: ese mes parecería una catástrofe y los cinco años siguientes
parecerían más rentables de lo que son. La contabilidad busca que cada período cargue el costo de lo
que **usó** para generar sus ingresos (el principio de correspondencia entre ingresos y gastos).

La **depreciación** es ese reparto: el costo del activo, menos lo que se espera recuperar al final,
se distribuye como gasto a lo largo de su vida útil. Tres cosas que no es:

- **No es una salida de caja.** La plata salió el día de la compra. La depreciación es un gasto que
  no se paga; por eso el resultado del mes y la caja del mes no coinciden (unidad 8).
- **No es el valor de mercado.** El valor libro (costo menos depreciación acumulada) dice cuánto del
  costo falta por repartir, no cuánto pagaría alguien por el activo hoy.
- **No es un fondo de reposición.** Depreciar no junta plata para comprar el horno siguiente.

---

## 2. Qué entra al costo del activo

El costo de un activo fijo es **todo lo necesario para dejarlo en el lugar y en condiciones de
funcionar**:

| Entra al costo | No entra al costo (va a gasto o a otra cuenta) |
|---|---|
| Precio neto de compra, menos descuentos | El IVA recuperable (va a IVA crédito fiscal) |
| Flete y seguro del traslado | Reparar un daño ocurrido en el traslado |
| Instalación, montaje, bases y conexiones | Capacitar al personal que lo va a usar |
| Pruebas de puesta en marcha | La mantención ordinaria una vez en uso |
| Derechos e impuestos de importación no recuperables | Los intereses del crédito que lo financió (en este ramo, gasto financiero: unidad 6) |

**Por qué.** Lo que entra al costo se reparte en la vida útil, porque sirve a todos esos años. Lo que
no deja el activo en condiciones de uso (un golpe en el camión, una capacitación que la persona se
lleva si se va) no agrega capacidad: es un gasto del período.

Una **mejora** que alarga la vida útil o aumenta la capacidad (cambiar el motor, ampliar un galpón)
se suma al costo del activo. Una **reparación** que solo lo mantiene funcionando es gasto.

---

## 3. Vida útil, valor residual y base depreciable

- **Costo** ($C$): lo de la sección 2.
- **Vida útil** ($n$): el tiempo (años o meses) o la producción total (unidades, horas, kilómetros)
  durante la que se espera usar el activo. Es una estimación.
- **Valor residual** ($VR$): lo que se espera obtener al final de la vida útil (venderlo usado, como
  chatarra). Puede ser cero.
- **Base depreciable**: $C - VR$. Es lo único que se deprecia. El valor residual no se gasta nunca:
  queda como valor libro al final.

**El terreno no se deprecia.** No se consume con el uso ni tiene una vida útil que se acabe. Si se
compra un inmueble, hay que **separar** el valor del terreno del de la construcción (por ejemplo, en
proporción a una tasación) y depreciar solo la construcción (ejercicio 4.4).

---

## 4. Cuatro métodos para repartir la base

Todos reparten la misma base, $C - VR$, y terminan en el mismo valor libro, $VR$. Lo que cambia es
**cuándo** cae el gasto.

### Lineal

$$D = \frac{C - VR}{n}$$

El mismo gasto cada año. Sirve cuando el activo presta un servicio parejo en el tiempo (un edificio,
un mueble). Es el que más se usa y el que este ramo aplica cuando el enunciado no dice otra cosa.

### Por unidades producidas (o por uso)

$$\text{tasa por unidad} = \frac{C - VR}{U_{\text{total}}} \qquad D_t = \text{tasa por unidad} \times u_t$$

con $U_{\text{total}}$ la producción de toda la vida útil y $u_t$ la del año. El gasto sigue al uso:
un año flojo deprecia poco. Sirve cuando el desgaste depende de cuánto se usa (un camión por
kilómetros, una máquina por horas o por piezas).

### Saldo decreciente

Se aplica una tasa fija $g$ sobre el **valor libro** del inicio de cada año, no sobre el costo:

$$D_t = g \cdot VL_{t-1} \qquad g = 1 - \left(\frac{VR}{C}\right)^{1/n}$$

Esa tasa es la que, aplicada $n$ veces, deja exactamente el valor residual: $C (1-g)^n = VR$. Como el
valor libro baja, el gasto baja cada año. Si $VR = 0$, la fórmula no sirve (daría $g = 1$); en ese
caso se usa una tasa fija, como el **doble saldo decreciente** ($g = 2/n$), y el último año se ajusta
para llegar al residual.

### Suma de dígitos

Se suman los años de vida ($1 + 2 + \dots + n = n(n+1)/2$) y cada año se deprecia una fracción
decreciente de la base:

$$D_t = \frac{n - t + 1}{n(n+1)/2} \cdot (C - VR)$$

Con $n = 4$: 4/10, 3/10, 2/10 y 1/10 de la base.

### Cuándo conviene cada uno

Los dos últimos son **acelerados**: cargan más gasto al principio. Sirven cuando el activo rinde más
de nuevo y pierde eficiencia o se vuelve obsoleto rápido (computadores, equipos con tecnología que
cambia). Ninguno cambia el total depreciado ni la caja: solo cambia en qué años cae el gasto y, por
eso, la utilidad de cada año.

---

## 5. La depreciación del ejercicio, la acumulada y el valor libro

La depreciación anual se lleva a meses cuando el activo se compra (o se vende) a mitad de año:

$$D_{\text{ejercicio}} = \frac{D_{\text{anual}}}{12} \times \text{meses de uso en el ejercicio}$$

**Convención de esta base (la misma del curso):** el mes de compra se cuenta completo. Un activo
comprado el 10 de marzo se deprecia 10 meses en ese año (marzo a diciembre).

El registro usa dos cuentas:

| Cuenta | Qué es | Dónde va |
|---|---|---|
| Gasto por depreciación (o depreciación del ejercicio) | El gasto del período | Estado de resultados |
| Depreciación acumulada | Todo lo depreciado desde la compra | Balance, restando al activo (cuenta complementaria de saldo acreedor) |

| Cuenta | Debe | Haber |
|---|---|---|
| Gasto por depreciación | $D_{\text{ejercicio}}$ | |
| Depreciación acumulada | | $D_{\text{ejercicio}}$ |

**Por qué no se abona directo al activo.** Para que el balance muestre las dos cosas: cuánto costó
el activo y cuánto de ese costo ya se usó. La diferencia es el **valor libro** (o valor neto):

$$VL = C - \text{depreciación acumulada}$$

**En una fábrica,** la depreciación de las máquinas de producción no es un gasto del período: es un
**costo indirecto de fabricación** que se carga a los productos y queda en el inventario hasta que se
venden (unidades 9 a 11). La de la oficina o de los vehículos de reparto sí es gasto del período.

---

## 6. Venta o baja de un activo

Al vender, primero se **actualiza la depreciación hasta la fecha de venta**. Después se saca del
balance el activo completo (su costo y su depreciación acumulada) y la diferencia entre lo que se
recibe y el valor libro es el resultado:

$$\text{utilidad (o pérdida)} = \text{precio de venta} - VL$$

| Cuenta | Debe | Haber |
|---|---|---|
| Banco (o lo que se reciba) | precio | |
| Depreciación acumulada | su saldo | |
| Pérdida en venta de activo fijo (si el precio es menor que el VL) | diferencia | |
| Activo (por su costo) | | costo |
| Utilidad en venta de activo fijo (si el precio es mayor que el VL) | | diferencia |

Si el activo se **da de baja** sin venderlo (se rompió sin arreglo, se perdió), el precio es cero y
la pérdida es todo el valor libro.

**La utilidad o pérdida no dice si convenía vender.** Dice cuánto se equivocó la estimación: si se
vende sobre el valor libro, se depreció de más (o el mercado lo valora más de lo previsto). La
decisión de vender o seguir usando un activo se toma comparando lo que se recibe hoy con lo que el
activo todavía puede generar; el valor libro es un costo ya incurrido (hundido) y no entra en esa
cuenta (ejercicio 4.10).

En esta unidad, como en el curso, la venta del activo se registra sin IVA.

---

## 7. Cambios de estimación, y depreciación financiera y tributaria

**Si cambia la estimación** de vida útil o de valor residual, no se corrigen los años pasados: el
valor libro que queda, menos el nuevo residual, se reparte en la vida que queda. Los estados ya
emitidos estaban bien con la información de ese momento.

**Financiera y tributaria.** La depreciación de esta unidad es la **financiera**: la empresa estima
la vida útil según el uso real del activo. Para calcular el impuesto a la renta, en cambio, se usa
la **tributaria**: las vidas útiles las fija una tabla del SII, y la ley permite en algunos casos
depreciar más rápido (depreciación acelerada tributaria). Por eso una empresa puede llevar dos
cálculos para el mismo activo. La diferencia entre los dos (y sus impuestos diferidos) no entra en
este ramo; aquí se usa la vida útil que da el enunciado.

**Cuándo NO aplica.** No se deprecia el terreno, ni un activo que se compró para revender (es
inventario: unidad 7), ni uno que todavía no está disponible para usarse (una máquina en camino o
en instalación). Los activos intangibles (marcas, licencias) se reparten con la misma lógica, pero se
llama amortización y no entra en esta unidad.

---

## 8. Ejemplo resuelto · el horno de una panadería

La panadería Los Aromos compra un horno rotatorio el **10-03-2026**, por transferencia: precio
**$8.460.000 + IVA**, flete **$248.000 + IVA** e instalación de gas y ducto **$332.000 + IVA**.
Además paga **$164.000 + IVA** para capacitar a dos panaderos en el horno nuevo. Estima que lo usará
**6 años**, que al final lo venderá en **$940.000**, y que en su vida horneará 162.000 bandejas.

**Paso 1 · El costo y la compra.** Costo: 8.460.000 + 248.000 + 332.000 = **$9.040.000**. La
capacitación es gasto. IVA de las cuatro facturas: 19 % de 9.204.000 = **$1.748.760**.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 10-03-2026 | Maquinaria (horno) | 9.040.000 |  |
|  |  | Gasto en capacitación | 164.000 |  |
|  |  | IVA crédito fiscal | 1.748.760 |  |
|  |  | Banco |  | 10.952.760 |
| | | *Compra e instalación del horno rotatorio, por transferencia* | | |
| 2 | 31-12-2026 | Gasto por depreciación | 1.125.000 |  |
|  |  | Depreciación acumulada |  | 1.125.000 |
| | | *Depreciación de marzo a diciembre (10 meses)* | | |
| 3 | fin del año 4 | Banco | 3.980.000 |  |
|  |  | Depreciación acumulada | 5.400.000 |  |
|  |  | Maquinaria (horno) |  | 9.040.000 |
|  |  | Utilidad en venta de activo fijo |  | 340.000 |
| | | *Venta del horno tras 48 meses de uso* | | |

**Paso 2 · Los cuatro métodos, por año de uso.** Base: 9.040.000 − 940.000 = **$8.100.000**.

- Lineal: 8.100.000 / 6 = $1.350.000 al año.
- Por unidades: 8.100.000 / 162.000 = **$50** por bandeja.
- Saldo decreciente: $g = 1 - (940{.}000 / 9{.}040{.}000)^{1/6} = 31{,}43\ \%$ sobre el valor libro.
- Suma de dígitos: $1 + 2 + \dots + 6 = 21$; el primer año 6/21 de la base, el último 1/21.

| Año | Bandejas | Lineal | Unidades producidas | Saldo decreciente | Suma de dígitos |
|---|---|---|---|---|---|
| 1 | 29.400 | 1.350.000 | 1.470.000 | 2.840.904 | 2.314.286 |
| 2 | 31.800 | 1.350.000 | 1.590.000 | 1.948.124 | 1.928.571 |
| 3 | 28.600 | 1.350.000 | 1.430.000 | 1.335.908 | 1.542.857 |
| 4 | 26.200 | 1.350.000 | 1.310.000 | 916.086 | 1.157.143 |
| 5 | 24.300 | 1.350.000 | 1.215.000 | 628.198 | 771.429 |
| 6 | 21.700 | 1.350.000 | 1.085.000 | 430.781 | 385.714 |
| **Total** | 162.000 | 8.100.000 | 8.100.000 | 8.100.000 | 8.100.000 |

(Las columnas aceleradas están redondeadas a peso; sin redondear suman exactamente la base.)

| Al final del año | Lineal | Unidades producidas | Saldo decreciente | Suma de dígitos |
|---|---|---|---|---|
| 1 | 7.690.000 | 7.570.000 | 6.199.096 | 6.725.714 |
| 2 | 6.340.000 | 5.980.000 | 4.250.972 | 4.797.143 |
| 3 | 4.990.000 | 4.550.000 | 2.915.064 | 3.254.286 |
| 4 | 3.640.000 | 3.240.000 | 1.998.978 | 2.097.143 |
| 5 | 2.290.000 | 2.025.000 | 1.370.781 | 1.325.714 |
| 6 | 940.000 | 940.000 | 940.000 | 940.000 |

**Paso 3 · El primer ejercicio, con el método lineal.** Mensual: 1.350.000 / 12 = **$112.500**. De
marzo a diciembre son 10 meses: **$1.125.000** (asiento 2). Al 31-12-2026 el balance muestra
Maquinaria 9.040.000, menos depreciación acumulada 1.125.000: valor libro **$7.915.000**.

**Paso 4 · La venta.** Al cumplir 48 meses de uso, la depreciación acumulada es 48 × 112.500 =
**$5.400.000** y el valor libro **$3.640.000**. La panadería vende el horno en $3.980.000: utilidad de
**$340.000** (asiento 3).

**Cómo se lee.**

- Los cuatro métodos reparten los mismos $8.100.000. En los dos primeros años, el lineal carga
  **$2.700.000**, la suma de dígitos **$4.242.857** y el saldo decreciente **$4.789.028**: con un método
  acelerado la utilidad de esos años es menor y la de los últimos, mayor. La caja es idéntica.
- Para una panadería cuya producción sube y baja con la temporada, el método por unidades es el que
  mejor sigue el desgaste real. Para decidir el precio del pan no importa el método: importa cuánto
  cuesta de verdad cada bandeja, y la depreciación del horno es un costo fijo del mes (unidad 9).
- La utilidad de $340.000 no prueba que vender fuera buena idea: dice que el horno valía en el
  mercado más que su valor libro, o sea, que se depreció un poco de más.

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Incluir el IVA en el costo del activo | El activo va al neto; el IVA recuperable va al crédito fiscal |
| Dejar fuera el flete o la instalación (o cargar al activo la capacitación o un daño del traslado) | Al costo va todo lo necesario para dejarlo funcionando; nada más |
| Depreciar el terreno | Solo se deprecia la construcción; el terreno se separa |
| Depreciar el costo completo, sin restar el valor residual | La base es $C - VR$ |
| En saldo decreciente, aplicar la tasa sobre el costo todos los años | La tasa va sobre el valor libro del inicio de cada año |
| Depreciar el año completo un activo comprado en agosto | Proporcional a los meses de uso (en esta base, el mes de compra cuenta completo) |
| Abonar la depreciación directamente al activo | Va a Depreciación acumulada, que resta al activo en el balance |
| Vender sin actualizar la depreciación hasta la fecha de venta | Primero el asiento de depreciación, después el de la venta |
| En la venta, sacar el activo por su valor libro y olvidar la depreciación acumulada | Se saca el activo por su costo y se carga la depreciación acumulada completa |
| Corregir los años pasados cuando cambia la vida útil | El cambio se aplica hacia adelante, sobre el valor libro que queda |
| Decidir si vender un activo mirando la pérdida contable | El valor libro es hundido; se compara lo que se recibe con lo que el activo puede generar |

---

## 10. Práctica

Diez ejercicios: 4.1 a 4.4 básicos, 4.5 a 4.8 intermedios, 4.9 y 4.10 de desafío. Si no se dice otra
cosa, el método es lineal, el mes de compra cuenta completo y la venta del activo no lleva IVA. Las
pautas están en la sección 11.

**4.1 · El costo de una guillotina (básico).** El 06-04 una imprenta compra una guillotina de precio
lista $6.780.000 + IVA, con un 5 % de descuento. Paga además, todo + IVA y por transferencia: flete
$187.000, seguro del traslado $43.500, instalación $238.500 y la reparación de una tapa que se abolló
en el camión, $97.000. ¿Con qué costo entra la guillotina? Registra el asiento.

**4.2 · La camioneta (básico).** Una camioneta cuesta $18.960.000, tiene 6 años de vida útil y un
valor residual de $4.560.000. Calcula la depreciación anual y mensual, la depreciación acumulada y
el valor libro al final del tercer año, y el valor libro al final de su vida.

**4.3 · Un servidor comprado en agosto (básico).** El 18-08-2026 una empresa compra un servidor por
$3.312.000 neto, con 4 años de vida útil y un valor residual de $432.000. Calcula la depreciación
anual, la mensual y la del ejercicio 2026; registra el asiento al 31-12-2026 y da el valor libro a esa
fecha.

**4.4 · Terreno y galpón (básico).** Una empresa paga $94.300.000 por un terreno con un galpón. Una
tasación los valora en $41.000.000 el terreno y $61.500.000 el galpón. El galpón tiene 40 años de
vida útil y un valor residual de $6.580.000. ¿Con qué valor entra cada uno y cuánto se deprecia al
año? ¿Cuánto se equivocaría quien depreciara los $94.300.000 completos con el mismo residual y la
misma vida?

**4.5 · El furgón por kilómetros (intermedio).** Un furgón de reparto cuesta $21.780.000, tiene un
valor residual de $3.780.000 y se espera que recorra 300.000 km. Recorre 72.400 km el primer año,
80.600 el segundo, 65.900 el tercero y 81.100 el cuarto. Arma la tabla de depreciación y valor libro,
y compárala con la lineal en 4 años.

**4.6 · El torno con saldo decreciente (intermedio).** Un torno CNC cuesta $28.800.000, dura 5 años y
su valor residual es $900.000. Calcula la tasa de saldo decreciente que deja el residual, arma la
tabla y compara el primer año con el método lineal. ¿Qué tasa daría el doble saldo decreciente?

**4.7 · La grúa horquilla con suma de dígitos (intermedio).** Una grúa horquilla cuesta $15.460.000,
dura 4 años y su residual es $1.460.000. Arma la tabla de suma de dígitos y la lineal. ¿Cuánto más
gasto carga la suma de dígitos el primer año, y cuánto suma cada método en los dos primeros años?
¿Cómo quedan los valores libro al final del año 2?

**4.8 · Vender con pérdida (intermedio).** Una máquina comprada el 01-07-2023 costó $11.460.000; su
vida útil es de 9 años y su residual $660.000. Se vende el 30-09-2026 en $6.840.000 por transferencia.
¿Cuánta depreciación acumulada tenía al 31-12-2025? Registra la depreciación de 2026 y la venta.

**4.9 · ¿Cuándo se compró? (desafío).** Al 31-12-2025 el balance de una empresa muestra Maquinaria
$26.400.000 y Depreciación acumulada $9.900.000. La máquina tiene un valor residual de $2.640.000 y
una vida útil total de 8 años. ¿En qué mes se compró? Registra la depreciación del 01-01 al 31-05-2026
y da el valor libro a esa fecha. ¿Cuántos meses de vida le quedan?

**4.10 · Cambiar la estimación, y decidir si vender (desafío).** Una estampadora costó $12.640.000,
con 8 años de vida útil y $640.000 de residual. Al final del tercer año la empresa ve que durará solo
6 años en total y que al final valdrá $1.240.000. (a) ¿Cuánto se depreciaba al año, cuál es el valor
libro al revisar y cuánto se deprecia desde entonces? (b) Al final del quinto año le ofrecen
$2.900.000 por ella. ¿Qué resultado contable tendría venderla? (c) Si la mantiene el sexto año, le
deja $1.950.000 de margen de contribución y al final la vende en su nuevo residual. Sin descontar,
¿conviene vender ahora o al final? ¿Qué papel juega el valor libro en la decisión?

---

## 11. Pautas

**4.1.** Precio con descuento: 6.780.000 × 0,95 = **$6.441.000** (descuento $339.000). Costo:
6.441.000 + 187.000 + 43.500 + 238.500 = **$6.910.000**. La reparación del golpe es gasto. IVA de
todo: **$1.331.330**; total pagado **$8.338.330**.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 06-04 | Maquinaria (guillotina) | 6.910.000 |  |
|  |  | Gasto en reparaciones | 97.000 |  |
|  |  | IVA crédito fiscal | 1.331.330 |  |
|  |  | Banco |  | 8.338.330 |
| | | *Compra, traslado e instalación de la guillotina* | | |

Lectura: si la reparación entrara al costo, se repartiría en años de uso que no la necesitaban.

**4.2.** Anual: (18.960.000 − 4.560.000) / 6 = **$2.400.000**; mensual **$200.000**. Al final del año 3:
depreciación acumulada **$7.200.000**, valor libro **$11.760.000**. Al final de su vida, el valor libro
es el residual, **$4.560.000**. Lectura: la mitad de la vida no deja la mitad del costo, sino la mitad
de la base más el residual.

**4.3.** Anual: (3.312.000 − 432.000) / 4 = **$720.000**; mensual **$60.000**. De agosto a diciembre
son 5 meses: **$300.000**.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 31-12-2026 | Gasto por depreciación | 300.000 |  |
|  |  | Depreciación acumulada |  | 300.000 |
| | | *Depreciación del servidor, agosto a diciembre* | | |

Valor libro al 31-12-2026: **$3.012.000**. Lectura: cargar los $720.000 del año completo le pondría a
2026 siete meses de un servidor que no tenía.

**4.4.** La tasación suma $102.500.000; el terreno es el **40 %**. Se reparte lo pagado en esa
proporción: terreno **$37.720.000** (no se deprecia) y galpón **$56.580.000**. Depreciación del
galpón: (56.580.000 − 6.580.000) / 40 = **$1.250.000** al año. Depreciando todo se cargarían
**$2.193.000**: **$943.000** de más cada año, gasto inventado sobre un terreno que no se gasta.

**4.5.** Tasa: (21.780.000 − 3.780.000) / 300.000 km = **$60** por km.

| Año | Kilómetros | Depreciación | Valor libro |
|---|---|---|---|
| 1 | 72.400 | 4.344.000 | 17.436.000 |
| 2 | 80.600 | 4.836.000 | 12.600.000 |
| 3 | 65.900 | 3.954.000 | 8.646.000 |
| 4 | 81.100 | 4.866.000 | 3.780.000 |

En 4 años recorre los **300.000** km previstos y llega al residual. La lineal cargaría **$4.500.000**
cada año. Lectura: el año 3, con menos reparto, carga menos gasto; el costo del furgón sigue a los
kilómetros, que es lo que lo desgasta.

**4.6.** $g = 1 - (900{.}000/28{.}800{.}000)^{1/5} = 1 - (1/32)^{1/5} = 50\ \%$.

| Año | Valor libro al inicio | Depreciación (50 %) | Valor libro al final | Lineal |
|---|---|---|---|---|
| 1 | 28.800.000 | 14.400.000 | 14.400.000 | 5.580.000 |
| 2 | 14.400.000 | 7.200.000 | 7.200.000 | 5.580.000 |
| 3 | 7.200.000 | 3.600.000 | 3.600.000 | 5.580.000 |
| 4 | 3.600.000 | 1.800.000 | 1.800.000 | 5.580.000 |
| 5 | 1.800.000 | 900.000 | 900.000 | 5.580.000 |

El primer año el saldo decreciente carga **$8.820.000** más que el lineal. El doble saldo
decreciente usaría $2/5 = 40\ \%$, y como no llega solo al residual, el último año se ajusta.
Lectura: la mitad del costo se va el primer año; tiene sentido para una máquina que pierde valor
muy rápido, no para una que rinde parejo.

**4.7.** Suma de dígitos: 1 + 2 + 3 + 4 = 10; base $14.000.000.

| Año | Fracción | Suma de dígitos | Valor libro | Lineal | Valor libro lineal |
|---|---|---|---|---|---|
| 1 | 4/10 | 5.600.000 | 9.860.000 | 3.500.000 | 11.960.000 |
| 2 | 3/10 | 4.200.000 | 5.660.000 | 3.500.000 | 8.460.000 |
| 3 | 2/10 | 2.800.000 | 2.860.000 | 3.500.000 | 4.960.000 |
| 4 | 1/10 | 1.400.000 | 1.460.000 | 3.500.000 | 1.460.000 |

El primer año carga **$2.100.000** más. En dos años, **$9.800.000** contra **$7.000.000**; los valores
libro quedan en **$5.660.000** y **$8.460.000**. Lectura: los dos métodos terminan en el mismo
residual; lo que cambia es qué años muestran más utilidad.

**4.8.** Mensual: (11.460.000 − 660.000) / 108 = **$100.000**. De julio de 2023 a diciembre de 2025
son 30 meses: **$3.000.000** acumulados. En 2026, de enero a septiembre, **$900.000** más; acumulada
**$3.900.000**, valor libro **$7.560.000**. Se vende en 6.840.000: pérdida de **$720.000**.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 30-09-2026 | Gasto por depreciación | 900.000 |  |
|  |  | Depreciación acumulada |  | 900.000 |
| | | *Depreciación de enero a septiembre, antes de vender* | | |
| 2 | 30-09-2026 | Banco | 6.840.000 |  |
|  |  | Depreciación acumulada | 3.900.000 |  |
|  |  | Pérdida en venta de activo fijo | 720.000 |  |
|  |  | Maquinaria |  | 11.460.000 |
| | | *Venta de la máquina por transferencia* | | |

Lectura: sin el primer asiento la pérdida aparecería $900.000 mayor y el gasto por depreciación de
2026 quedaría en cero; el resultado total del año sería el mismo, pero mal clasificado.

**4.9.** Depreciación mensual: (26.400.000 − 2.640.000) / 96 = **$247.500** (**$2.970.000** al año). La
acumulada equivale a 9.900.000 / 247.500 = **40** meses: 4 de 2022 más 36 de 2023 a 2025, así que se
compró en **septiembre de 2022** (contando ese mes completo). Del 01-01 al 31-05-2026:

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| 1 | 31-05-2026 | Gasto por depreciación | 1.237.500 |  |
|  |  | Depreciación acumulada |  | 1.237.500 |
| | | *Depreciación de enero a mayo de 2026* | | |

Acumulada **$11.137.500**; valor libro **$15.262.500**. Le quedan 96 − 45 = **51** meses. Lectura: la
depreciación acumulada es un reloj; dividida por la cuota mensual dice cuánto tiempo lleva el activo.

**4.10.** (a) Antes: (12.640.000 − 640.000) / 8 = **$1.500.000** al año; al final del año 3, acumulada
**$4.500.000** y valor libro **$8.140.000**. Desde la revisión: (8.140.000 − 1.240.000) / 3 =
**$2.300.000** al año, sin tocar los tres años ya registrados. (b) Al final del año 5 la acumulada es
**$9.100.000** y el valor libro **$3.540.000**: venderla en 2.900.000 da una pérdida contable de
**$640.000**. (c) Mantenerla deja 1.950.000 + 1.240.000 = **$3.190.000**, contra $2.900.000 hoy:
conviene mantenerla, por **$290.000** (sin descontar; con una tasa, como en Finanzas, la diferencia
baja). El valor libro no juega ningún papel: los $3.540.000 ya se gastaron y no cambian con lo que se
decida. La pérdida de (b) asusta, pero la decisión se toma con lo que viene, no con lo que ya pasó.

---

## 12. Caso integrador · las dos máquinas de Estampa Sur

> Viene de la unidad 3: la segunda máquina se compró en marzo por $14.300.000 neto; su IVA quedó en
> el crédito fiscal y no forma parte del costo. El balance al 1 de marzo (unidad 1) trae el pulpo 6.

**Pregunta.** ¿Cuánto se deprecia en marzo, y cómo quedan las dos máquinas en el balance?

**Desarrollo.**

1. **Pulpo 6.** Costo $9.840.000, sin residual, 96 meses de vida: **$102.500** al mes. Al 1 de marzo
   ya acumulaba **$2.460.000**, es decir **24** meses usados; le quedan **72**. Su valor libro al 1 de
   marzo es **$7.380.000**.
2. **Segunda máquina.** Costo $14.300.000, residual $1.800.000 (el de Finanzas), 60 meses:

$$D = \frac{14{.}300{.}000 - 1{.}800{.}000}{60} = 208{.}333{,}33 \text{ al mes}$$

   Se compró en marzo y, con la convención del curso, deprecia marzo completo.
3. **El asiento de marzo:** **$310.833,33** entre las dos.

| N.º | Fecha | Cuenta | Debe | Haber |
|---|---|---|---|---|
| Ajuste | 31-03 | Depreciación de maquinaria (costo indirecto) | 310.833,33 |  |
|  |  | Depreciación acumulada |  | 310.833,33 |
| | | *Depreciación de marzo de las dos máquinas* | | |

4. **El balance al 31-03.** Maquinaria **$24.140.000**, menos depreciación acumulada
   **$2.770.833,33**: valor libro **$21.369.166,67**. Por separado, el pulpo 6 acumula $2.562.500 (valor
   libro $7.277.500) y la segunda máquina vale en libros $14.091.666,67.
5. **La tabla completa.** La planilla trae los 72 meses; año por año (de marzo a febrero), cada
   máquina deprecia $1.230.000 y $2.500.000:

| Año (de marzo a febrero) | Depreciación pulpo 6 | Valor libro pulpo 6 | Depreciación segunda máquina | Valor libro segunda máquina |
|---|---|---|---|---|
| 1 (03-2026 a 02-2027) | 1.230.000 | 6.150.000 | 2.500.000 | 11.800.000 |
| 2 (03-2027 a 02-2028) | 1.230.000 | 4.920.000 | 2.500.000 | 9.300.000 |
| 3 (03-2028 a 02-2029) | 1.230.000 | 3.690.000 | 2.500.000 | 6.800.000 |
| 4 (03-2029 a 02-2030) | 1.230.000 | 2.460.000 | 2.500.000 | 4.300.000 |
| 5 (03-2030 a 02-2031) | 1.230.000 | 1.230.000 | 2.500.000 | 1.800.000 |
| 6 (03-2031 a 02-2032) | 1.230.000 | 0 | 0 | 1.800.000 |

**Lectura.** Las dos máquinas estampan prendas, así que su depreciación no va directo a gasto: es un
costo indirecto de fabricación. Junto con los sueldos, el seguro y el arriendo del mes forma los
**$3.849.833,33** de costos fijos de fabricación de marzo, que las unidades 9 a 11 reparten entre las
prendas. La segunda máquina multiplicó por tres la depreciación mensual del taller (de $102.500 a
$310.833,33): cada prenda carga ahora más costo fijo, y eso solo se justifica si la máquina permite
producir y vender más (el punto de equilibrio de la unidad 12). Al quinto año, la segunda máquina
llega a sus $1.800.000 de residual y deja de depreciarse; si sigue funcionando, produce sin cargar
depreciación.

**Pasa a la unidad 5:** la depreciación es el primer ajuste de cierre del mes; la unidad 5 agrega el
arriendo y el seguro devengados.

---

## 13. Para seguir

**En los libros del ramo.** La bibliografía obligatoria del programa son dos libros de Ediciones UC:
Gálvez y Clarke, *Contabilidad financiera para la dirección de empresas*, cuyo capítulo VIII trata el
activo fijo y sus métodos de depreciación (lineal, por uso, acelerada y suma de dígitos), e
Irarrázabal, *Contabilidad: fundamentos y usos* (2014). Garrison, Noreen y Brewer, Horngren y
Weygandt, Kimmel y Kieso figuran como complementarios; el último, *Accounting Principles* (Wiley,
12.ª ed., 2014), trata el mismo tema en inglés.

**Abierto y gratis.**

- OpenStax, *Principles of Accounting, Volume 1: Financial Accounting*, en inglés, capítulo 11
  («Long-Term Assets»): qué se capitaliza y qué va a gasto (11.2) y los métodos de depreciación
  (11.3). Licencia CC BY-NC-SA 4.0:
  https://openstax.org/books/principles-financial-accounting/pages/11-why-it-matters

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame una máquina con su costo, flete,
instalación y valor residual, déjame armar la tabla de depreciación con los cuatro métodos y la venta
al tercer año, y corrígeme fila por fila».
