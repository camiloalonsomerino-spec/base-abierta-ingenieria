---
ramo: Gestión de Operaciones
unidad: 6
titulo: Planeación agregada
version: 0.1 (15-10-2026)
requiere: [03-proceso-y-capacidad, 04-pronosticos]
alimenta: [07-programa-maestro]
verificacion: verificacion/u06_planeacion_agregada.py
---

# Unidad 6 · Planeación agregada

**Qué vas a poder hacer.** Armar un plan de producción mes a mes para una familia de productos;
calcular cuánta gente hace falta con cada estrategia (persecución, nivelada sin faltantes, nivelada
con faltantes y mixta); sumar el costo total de cada plan con todas sus partidas (contratar,
despedir, sueldos, horas extra, subcontratación, inventario y faltantes), y elegir el plan con un
argumento que vaya más allá del número.

**Lo que necesitas antes.** El pronóstico mensual (unidad 4) y la idea de capacidad en horas
(unidad 3). Basta con saber pasar de horas-hombre por unidad a unidades por trabajador y día.

**Tiempo.** Unas 5 horas: 2 de lectura con el ejemplo y 3 de práctica.

---

## 1. La idea

El plan agregado responde una pregunta de mediano plazo (entre 3 y 18 meses): **con qué recursos
se va a cubrir la demanda de cada mes**. No mira productos sueltos sino la familia completa,
medida en una unidad común (cajas, toneladas, horas). El detalle por producto y semana lo hace
después el programa maestro (unidad 7).

Cuando la demanda sube y baja, la empresa tiene dos tipos de palancas:

| Palanca | Cómo absorbe la variación | Lo que cuesta |
|---|---|---|
| **Inventario** | Se produce de más en los meses flojos para vender en los altos | Mantener cada unidad un mes |
| **Fuerza de trabajo** | Se contrata cuando sube y se despide cuando baja | Contratar, capacitar, despedir |
| **Horas extra** | La misma gente trabaja más horas en el peak | Recargo sobre la hora normal |
| **Subcontratación** | Un tercero fabrica lo que no alcanza | Precio por unidad, casi siempre mayor |
| **Faltantes** | El cliente espera: se le entrega el mes siguiente | Multa, descuento o mala voluntad, por unidad y mes |
| **Demanda** | Precio, promociones o productos de temporada opuesta | Margen o inversión comercial |

Las cinco primeras son de capacidad y son las que se calculan en esta unidad. La última es
comercial y se nombra para no olvidar que la demanda también se gestiona.

> **El plan agregado no es un pronóstico.** El pronóstico dice cuánto se va a pedir; el plan dice
> cuánto se decide producir y con qué gente. Pueden diferir: un plan nivelado produce de más en
> meses flojos a propósito.

---

## 2. Notación y balance

Para cada mes $t$: $D_t$ demanda, $n_t$ días hábiles, $W_t$ trabajadores, $P_t$ producción e $I_t$
inventario al cierre ($I_0$ es el inicial). Si cada unidad toma $k$ horas-hombre y la jornada dura
$h$ horas, cada trabajador hace

$$r = \frac{h}{k} \quad \text{unidades por día} \qquad\qquad P_t^{\text{regular}} = W_t \cdot r \cdot n_t$$

El inventario se mueve con un balance simple:

$$I_t = I_{t-1} + P_t - D_t$$

Si $I_t$ sale negativo, son **faltantes**: unidades que se deben y se entregan después. Por eso se
separan las dos partes, $I_t^{+} = \max(0, I_t)$ e $I_t^{-} = \max(0, -I_t)$.

El costo total del plan suma todas las partidas de todos los meses:

$$CT = \sum_t \Big[ C_C\,C_t + C_D\,S_t + c_d\,W_t\,n_t + c_{HE}\,O_t + c_S\,U_t + c_I\,I_t^{+} + c_F\,I_t^{-} \Big]$$

con $C_t$ y $S_t$ trabajadores contratados y despedidos, $O_t$ horas extra, $U_t$ unidades
subcontratadas, $c_d$ sueldo por trabajador y día, $c_I$ costo de mantener una unidad un mes y
$c_F$ costo de una unidad faltante por mes.

> **El material no se suma.** Si todos los planes fabrican lo mismo en el horizonte, la tela, la
> fruta o el plástico cuestan igual en todos y no cambian la decisión. Se dejan fuera. La
> subcontratación sí se suma completa, porque reemplaza el trabajo propio.

---

## 3. Las estrategias

### Persecución

La producción sigue a la demanda: cada mes se contrata o se despide lo justo. Como no se puede
contratar media persona, se redondea **hacia arriba** y el redondeo deja un poco de inventario,
que se descuenta al mes siguiente:

$$W_t = \left\lceil \frac{\max(0,\; D_t - I_{t-1})}{r \cdot n_t} \right\rceil$$

Casi no carga inventario, pero paga muchos cambios de dotación y obliga a capacitar gente en cada
peak.

### Nivelada sin faltantes

Una sola dotación todo el horizonte, la menor que **nunca** deja faltantes. Se mira la demanda
acumulada contra los días acumulados y se toma el peor mes:

$$W = \left\lceil \max_t \frac{\sum_{s \le t} D_s \;-\; I_0}{r \cdot \sum_{s \le t} n_s} \right\rceil$$

No se toma el mes de mayor demanda por sí solo: el inventario de los meses anteriores ayuda a
cubrirlo. Tampoco basta el promedio: si el peak llega temprano, el promedio deja faltantes.

### Nivelada con faltantes

La dotación promedio del horizonte, redondeada hacia arriba:

$$W = \left\lceil \frac{\sum_t D_t - I_0}{r \cdot \sum_t n_t} \right\rceil$$

Alcanza para todo el horizonte, pero no necesariamente a tiempo: en los meses de peak quedan
faltantes que se recuperan después.

### Mixta

Combina palancas. La más usada: una **dotación fija** que cubre la base, más **horas extra** con un
tope (la ley y el cansancio lo ponen) y **subcontratación** para lo que todavía falte. La dotación
fija no sale de una fórmula: se prueban varias y se queda la de menor costo total.

### Días amortiguador

Para leer un inventario en días y no en unidades:

$$\text{días amortiguador}_t = \frac{I_t}{W_t \cdot r}$$

Dice cuántos días de producción tiene guardados la planta. Diez días de amortiguador antes del
peak es una decisión; diez días a fin de año es un costo que nadie pidió.

---

## 4. Ejemplo resuelto · fábrica de mermeladas

Una fábrica de mermeladas de Ñuble planifica el segundo semestre en cajas de 12 frascos. Hoy tiene
**15 trabajadores** y **300 cajas** en bodega. Cada caja toma **0,4 HH** y la jornada es de 8 horas.

| | Jul | Ago | Sep | Oct | Nov | Dic | Total |
|---|---|---|---|---|---|---|---|
| Demanda (cajas) | 5.340 | 5.870 | 7.690 | 8.120 | 5.960 | 4.870 | 37.850 |
| Días hábiles | 21 | 22 | 18 | 21 | 20 | 21 | 123 |

Costos: contratar $420.000 por persona, despedir $680.000, sueldo $29.200 por trabajador y día,
hora extra $5.400, subcontratar $2.380 por caja, mantener \$180 por caja y mes, faltante
$1.120 por caja y mes. Las horas extra no pueden pasar del 15 % de la producción regular.

**Paso 1 · Unidades por trabajador.** $r = 8 / 0{,}4 = 20$ cajas por día. En julio, un trabajador
hace $20 \times 21 = 420$ cajas.

**Paso 2 · Persecución.** En julio la demanda neta es $5{.}340 - 300 = 5{.}040$ y se necesitan
$5{.}040 / 420 = 12{,}00$ trabajadores: sobran 3 de los 15. En agosto, $5{.}870 / 440 = 13{,}34$, que
se redondea a 14.

| | Jul | Ago | Sep | Oct | Nov | Dic | Total |
|---|---|---|---|---|---|---|---|
| Demanda neta | 5.040 | 5.870 | 7.400 | 7.960 | 5.940 | 4.810 | |
| Trabajadores teóricos | 12,00 | 13,34 | 20,56 | 18,95 | 14,85 | 11,45 | |
| Trabajadores | 12 | 14 | 21 | 19 | 15 | 12 | |
| Contrata / despide | −3 | +2 | +7 | −2 | −4 | −3 | 9 / 12 |
| Producción | 5.040 | 6.160 | 7.560 | 7.980 | 6.000 | 5.040 | |
| Inventario final | 0 | 290 | 160 | 20 | 60 | 230 | |
| Cambio de dotación | 2.040.000 | 840.000 | 2.940.000 | 1.360.000 | 2.720.000 | 2.040.000 | 11.940.000 |
| Sueldos | 7.358.400 | 8.993.600 | 11.037.600 | 11.650.800 | 8.760.000 | 7.358.400 | 55.158.800 |
| Mantener | 0 | 52.200 | 28.800 | 3.600 | 10.800 | 41.400 | 136.800 |

Costo total de la persecución: **$67.235.600**. Casi no guarda cajas, pero contrata 9 personas y
despide 12 en seis meses.

**Paso 3 · Nivelada sin faltantes.** Se acumula demanda (menos las 300 cajas iniciales) y días:

| | Jul | Ago | Sep | Oct | Nov | Dic |
|---|---|---|---|---|---|---|
| Demanda acumulada − $I_0$ | 5.040 | 10.910 | 18.600 | 26.720 | 32.680 | 37.550 |
| Días acumulados | 21 | 43 | 61 | 82 | 102 | 123 |
| Trabajadores acumulados | 12,00 | 12,69 | 15,25 | 16,29 | 16,02 | 15,26 |

El peor mes es octubre con 16,29: hacen falta **17 trabajadores** todo el semestre (se contratan 2).

| | Jul | Ago | Sep | Oct | Nov | Dic |
|---|---|---|---|---|---|---|
| Producción | 7.140 | 7.480 | 6.120 | 7.140 | 6.800 | 7.140 |
| Inventario final | 2.100 | 3.710 | 2.140 | 1.160 | 2.000 | 4.270 |
| Días amortiguador | 6,2 | 10,9 | 6,3 | 3,4 | 5,9 | 12,6 |

Costo: contratar $840.000, sueldos $61.057.200 y mantener $2.768.400. Total **$64.665.600**.
Diciembre cierra con 4.270 cajas (12,6 días de producción) que nadie pidió.

**Paso 4 · Nivelada con faltantes.** El promedio es $37{.}550 / (20 \times 123) = 15{,}26$, que se
redondea a **16 trabajadores** (se contrata 1).

| | Jul | Ago | Sep | Oct | Nov | Dic |
|---|---|---|---|---|---|---|
| Producción | 6.720 | 7.040 | 5.760 | 6.720 | 6.400 | 6.720 |
| Inventario final | 1.680 | 2.850 | 920 | −480 | −40 | 1.810 |

En octubre se deben 480 cajas y en noviembre todavía 40. Costo: contratar $420.000, sueldos
$57.465.600, mantener $1.306.800 y faltantes $582.400. Total **$59.774.800**.

**Paso 5 · Mixta.** Se prueban dotaciones fijas; lo que falte se cubre con horas extra (hasta el
15 %) y luego con subcontratación.

| Dotación fija | 12 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|---|
| Costo total | $64.088.720 | $62.440.180 | $60.864.840 | **$59.502.500** | $60.394.800 | $64.665.600 |

Gana la dotación actual de 15. Con 17 ya no hay horas extra y el plan es la nivelada sin faltantes.
El detalle con 15:

| | Jul | Ago | Sep | Oct | Nov | Dic |
|---|---|---|---|---|---|---|
| Producción regular | 6.300 | 6.600 | 5.400 | 6.300 | 6.000 | 6.300 |
| Horas extra (cajas) | 0 | 0 | 300 | 945 | 0 | 0 |
| Subcontratadas | 0 | 0 | 0 | 875 | 0 | 0 |
| Inventario final | 1.260 | 1.990 | 0 | 0 | 40 | 1.470 |

Julio y agosto guardan 1.990 cajas para el peak; septiembre usa 300 cajas en horas extra
($300 \times 0{,}4 = 120$ horas) y octubre llega al tope (945 cajas) y subcontrata 875. Costo:
sueldos $53.874.000, horas extra $2.689.200, subcontratación $2.082.500 y mantener $856.800.
Total **$59.502.500**.

**Paso 6 · Comparar.**

| Plan | Cambios | Sueldos | Horas extra | Subcontr. | Mantener | Faltantes | Total |
|---|---|---|---|---|---|---|---|
| Persecución | 11.940.000 | 55.158.800 | 0 | 0 | 136.800 | 0 | $67.235.600 |
| Nivelada sin faltantes | 840.000 | 61.057.200 | 0 | 0 | 2.768.400 | 0 | $64.665.600 |
| Nivelada con faltantes | 420.000 | 57.465.600 | 0 | 0 | 1.306.800 | 582.400 | $59.774.800 |
| **Mixta (15 fijos)** | 0 | 53.874.000 | 2.689.200 | 2.082.500 | 856.800 | 0 | **$59.502.500** |

**Cómo se lee.**

- La persecución es la más cara: el ahorro en bodega no alcanza a pagar 21 cambios de dotación.
- La nivelada sin faltantes paga dos sueldos todo el semestre para cubrir un solo mes.
- La mixta gana por $272.300 a la nivelada con faltantes. La diferencia es chica, pero la
  mixta entrega todo a tiempo y no contrata a nadie.
- La pregunta para la gerencia: **¿cuánto vale realmente que un cliente espere un mes?** Si la
  multa real fuera más baja que $1.120 por caja, la nivelada con faltantes podría ganar.

> **Ajuste del último mes.** Algunos planes nivelados ajustan diciembre para cerrar con inventario
> cero: se produce menos y el sueldo se paga igual. Eso baja el costo de mantener, pero deja gente
> ociosa. Si un enunciado lo pide, se aplica; si no, la producción es $W \cdot r \cdot n_t$ todos
> los meses.

---

## 5. Programación lineal y método de transporte

Los métodos de las secciones 3 y 4 son de prueba y error: comparan pocos planes y no garantizan el
mejor. Con dotación fija, el problema se puede escribir como **programación lineal**:

- Variables: $x_{ts}$ unidades fabricadas en el mes $t$ con una fuente (regular, extra o
  subcontratada) para vender en el mes $s \ge t$.
- Objetivo: minimizar $\sum c_{ts}\,x_{ts}$, donde $c_{ts}$ es el costo de la fuente más
  $(s - t)\,c_I$ por guardarla.
- Restricciones: lo que sale de cada fuente no supera su capacidad; lo que llega a cada mes iguala
  su demanda.

Es un problema de transporte (Optimización). Cuando no se permiten faltantes y guardar siempre
cuesta, se resuelve a mano: se recorren los meses en orden y cada demanda se llena con la celda
disponible más barata. El ejercicio 6.10 lo hace paso a paso.

---

## 6. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Redondear los trabajadores hacia abajo | Con 13,34 se necesitan 14; con 13 falta producción |
| Olvidar el inventario inicial | Se resta de la demanda del primer mes (o de la acumulada) |
| Nivelar con el mes de mayor demanda | La regla es el máximo de los acumulados; el inventario previo ayuda |
| Nivelar con el promedio y decir «sin faltantes» | El promedio deja faltantes si el peak llega antes |
| Cobrar mantener sobre el inventario negativo | El negativo es faltante: se cobra con $c_F$, no con $c_I$ |
| Sumar el material en un plan y no en otro | O en todos o en ninguno; la subcontratación sí se suma |
| Poner horas extra sobre el tope | El tope se calcula sobre la producción regular de ese mes |

---

## 7. Práctica

Diez ejercicios: 6.1 a 6.4 básicos, 6.5 a 6.8 intermedios, 6.9 y 6.10 de desafío. Las pautas
están en la sección 8. Intenta cada uno antes de mirarla.

**6.1 · Ensamble de bicicletas, persecución (básico).** Un taller arma bicicletas eléctricas. Cada
trabajador arma 8 por día; hoy hay 15 trabajadores y nada en bodega. Contratar cuesta $380.000,
despedir $540.000, el sueldo es $31.000 por día y mantener una bicicleta un mes cuesta \$950.
Arma el plan de persecución y su costo total.

| Mes | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Demanda | 2.310 | 2.640 | 3.170 | 2.230 |
| Días hábiles | 21 | 20 | 22 | 19 |

**6.2 · Las mismas bicicletas, nivelada (básico).** Con los datos de 6.1, calcula la dotación de
la nivelada sin faltantes, el inventario y los días amortiguador de cada mes y el costo total.
¿Cuál de los dos planes conviene y por cuánto?

**6.3 · Planta de hielo, balance con faltantes (básico).** Una planta de hielo en bolsas produce
10.200 bolsas todos los meses y parte con 500. Mantener una bolsa un mes cuesta \$60 y cada bolsa
faltante \$210 por mes. Completa el inventario de cada mes y el costo de inventario y de faltantes.

| Mes | Oct | Nov | Dic | Ene | Feb | Mar |
|---|---|---|---|---|---|---|
| Demanda | 7.750 | 9.150 | 11.600 | 12.900 | 11.300 | 8.700 |

**6.4 · Qué palanca para qué caso (básico).** Sin calcular, indica la palanca principal y
justifica en una línea. (a) Un call center con peaks de dos horas cada mañana. (b) Una planta de
yogur (vida útil de tres semanas) con peak en verano. (c) Un taller de soldadura especializada
donde formar a un soldador toma seis meses. (d) Una juguetería que vende el 40 % del año en
diciembre. (e) Clasifica estas partidas en «cambio de dotación», «capacidad» o «inventario»:
capacitación, recargo de horas extra, arriendo de bodega, indemnización, pedido atrasado.

**6.5 · Ventanas de PVC, persecución contra nivelada (intermedio).** Una fábrica de ventanas trabaja
jornadas de 9 horas y cada ventana toma 1,5 HH. Tiene 14 trabajadores y nada en bodega. Contratar
cuesta $510.000, despedir $760.000, el sueldo es $34.000 por día y mantener una ventana un mes
$2.600. Compara la persecución con la nivelada sin faltantes.

| Mes | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Demanda | 1.620 | 1.930 | 2.170 | 1.720 | 1.240 | 1.390 |
| Días hábiles | 22 | 20 | 21 | 22 | 21 | 19 |

**6.6 · Ventanas, nivelada con faltantes (intermedio).** Con los datos de 6.5 y un costo de
$7.900 por ventana faltante y mes, arma la nivelada con faltantes. ¿En qué meses se deben
ventanas? Ordena los tres planes por costo.

**6.7 · Imprenta de cuadernos, dotación fija con horas extra y subcontratación (intermedio).** Una
imprenta tiene 9 operarios fijos, jornada de 9 horas y 0,05 HH por cuaderno. Parte con 1.200
cuadernos. Las horas extra pueden llegar al 25 % de la producción regular y cuestan $6.300 la
hora; lo que no alcance se subcontrata a \$260 por cuaderno. El sueldo es $30.600 por día y
mantener un cuaderno un mes cuesta \$35. (a) Completa el plan y su costo. (b) ¿Cuántas horas extra
se trabajan en febrero? (c) ¿Qué cambiarías mirando marzo?

| Mes | Dic | Ene | Feb | Mar |
|---|---|---|---|---|
| Demanda | 28.400 | 41.900 | 46.300 | 23.700 |
| Días hábiles | 21 | 22 | 20 | 22 |

**6.8 · ¿Desde qué costo de despido cambia la decisión? (intermedio).** En la fábrica de ventanas
(6.5 y 6.6) la persecución y la nivelada con faltantes quedan casi empatadas. (a) ¿Desde qué
costo de despido por trabajador conviene la nivelada con faltantes? (b) Nombra otro costo que, mal
estimado, podría dar vuelta la decisión.

**6.9 · Agua purificada, elegir la dotación fija (desafío).** Una planta llena bidones con 0,02 HH
cada uno y jornada de 8 horas. Tiene 15 trabajadores y 2.000 bidones en bodega. Contratar cuesta
$465.000, despedir $655.000, el sueldo es $27.500 por día, la hora extra $5.180 (tope: 25 % de
la producción regular), mantener un bidón un mes \$12 y un bidón faltante \$40 por mes. No se
subcontrata. (a) Prueba dotaciones fijas de 12 a 19 y elige la mejor. (b) ¿Cambia la respuesta si
la planta partiera con 17 trabajadores?

| Mes | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Demanda | 118.000 | 126.500 | 141.200 | 152.800 | 137.400 | 129.900 |
| Días hábiles | 22 | 21 | 21 | 22 | 20 | 22 |

**6.10 · Detergente, método de transporte (desafío).** Una planta de detergente tiene dotación fija.
Cada mes puede fabricar 4.150 cajas en horario regular a $2.000, 600 más en horas extra a $3.000
y subcontratar hasta 1.000 a $3.400. Guardar una caja cuesta \$250 por mes y no se aceptan
faltantes. Parte con 200 cajas. (a) Escribe el modelo de programación lineal. (b) Resuélvelo con
el método de transporte. (c) ¿Qué fuente del mes 1 termina vendiéndose en el mes 2 y por qué?

| Mes | 1 | 2 | 3 |
|---|---|---|---|
| Demanda | 3.750 | 4.900 | 5.600 |

---

## 8. Pautas

**6.1.**

| Mes | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Trabajadores teóricos | 13,75 | 16,24 | 17,32 | 13,88 |
| Trabajadores | 14 | 17 | 18 | 14 |
| Contrata / despide | −1 | +3 | +1 | −4 |
| Producción | 2.352 | 2.720 | 3.168 | 2.128 |
| Inventario final | 42 | 122 | 120 | 18 |
| Costo del mes | 9.693.900 | 11.795.900 | 12.770.000 | 10.423.100 |

Costo total **$44.682.900**. En el mes 2 se descuentan las 42 bicicletas que dejó el redondeo:
$(2{.}640 - 42)/160 = 16{,}24$.

**6.2.** Trabajadores acumulados: 13,75 · 15,09 · 16,11 · 15,78. El máximo da **17** (se
contratan 2, $760.000). Producción 2.856, 2.720, 2.992 y 2.584; inventario 546, 626, 448 y 802;
días amortiguador 4,0 · 4,6 · 3,3 · 5,9. Sueldos $43.214.000 y mantener $2.300.900. Total
**$46.274.900**. Acá conviene la persecución por $1.592.000: contratar y despedir es barato
frente a guardar bicicletas a \$950 al mes, y el plan nivelado termina con 802 de sobra.

**6.3.**

| Mes | Oct | Nov | Dic | Ene | Feb | Mar |
|---|---|---|---|---|---|---|
| Inventario final | 2.950 | 4.000 | 2.600 | −100 | −1.200 | 300 |

Mantener: $591.000. Faltantes: $273.000 (100 bolsas en enero y 1.200 en febrero). Total
**$864.000**. La producción constante alcanza para el verano completo, pero no a tiempo: en enero y
febrero se deben bolsas que se pagan en marzo.

**6.4.** (a) Turnos parciales o personal part-time: el peak dura horas y un servicio no se guarda.
(b) Horas extra o subcontratación: el inventario se vence. (c) Inventario y horas extra: contratar
no sirve si el nuevo tarda seis meses en rendir. (d) Inventario construido desde septiembre, más
temporales en noviembre. (e) Capacitación e indemnización: cambio de dotación. Recargo de horas
extra: capacidad. Arriendo de bodega: inventario. Pedido atrasado: faltante, que es inventario
negativo.

**6.5.** Persecución (cada ventanero hace $9 / 1{,}5 = 6$ por día):

| Mes | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Trabajadores teóricos | 12,27 | 15,28 | 16,54 | 12,59 | 9,41 | 11,54 |
| Trabajadores | 13 | 16 | 17 | 13 | 10 | 12 |
| Contrata / despide | −1 | +3 | +1 | −4 | −3 | +2 |
| Inventario final | 96 | 86 | 58 | 54 | 74 | 52 |

Cambios $9.140.000, sueldos $57.358.000, mantener $1.092.000: total **$67.590.000**.

Nivelada sin faltantes: trabajadores acumulados 12,27 · 14,09 · 15,13 · 14,59 · 13,65 · 13,43.
El máximo (mes 3) da **16 trabajadores** (se contratan 2). Inventario 492, 482, 328, 720, 1.496 y
1.930. Contratar $1.020.000, sueldos $68.000.000, mantener $14.164.800: total
**$83.184.800**. El peak llega temprano y obliga a cargar dos personas de más todo el semestre;
el segundo semestre se llena de ventanas a $2.600 por mes cada una.

**6.6.** Promedio: $10{.}070 / (6 \times 125) = 13{,}43$, se redondea a **14 trabajadores** (los que
ya hay).

| Mes | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Producción | 1.848 | 1.680 | 1.764 | 1.848 | 1.764 | 1.596 |
| Inventario final | 228 | −22 | −428 | −300 | 224 | 430 |

Se deben ventanas en los meses 2, 3 y 4. Sueldos $59.500.000, mantener $2.293.200 y faltantes
$5.925.000: total **$67.718.200**. Orden: persecución ($67.590.000), nivelada con faltantes
($67.718.200) y, muy lejos, nivelada sin faltantes ($83.184.800).

**6.7.** Cada operario hace $9 / 0{,}05 = 180$ cuadernos por día.

| Mes | Dic | Ene | Feb | Mar |
|---|---|---|---|---|
| Producción regular | 34.020 | 35.640 | 32.400 | 35.640 |
| Horas extra (cuadernos) | 0 | 0 | 8.100 | 0 |
| Subcontratados | 0 | 0 | 5.240 | 0 |
| Inventario final | 6.820 | 560 | 0 | 11.940 |

(a) Sueldos $23.409.000, horas extra $2.551.500, subcontratación $1.362.400 y mantener
$676.200: total **$27.999.100**. (b) $8{.}100 \times 0{,}05 = 405$ horas extra, justo el tope.
(c) Marzo termina con 11.940 cuadernos sin vender: la dotación de 9 sobra después de la temporada.
Conviene reducir la jornada en marzo, adelantar producción de febrero a enero (que sí tiene
holgura) o dejar que marzo fabrique para la temporada siguiente.

**6.8.** (a) La persecución despide 8 trabajadores en total y la nivelada con faltantes ninguno.
Sin los despidos, la persecución cuesta $61.510.000 y la nivelada $67.718.200. Se igualan cuando
$61{.}510{.}000 + 8\,C_D = 67{.}718{.}200$, es decir con $C_D =$ **$776.025**. Hoy el despido cuesta
$760.000 y la persecución gana por apenas $128.200. (b) El costo de faltante: la nivelada paga
$5.925.000 por 750 ventanas-mes atrasadas. Si un cliente grande se pierde por esperar, ese costo
está subestimado y la persecución gana con más holgura.

**6.9.** Cada trabajador llena $8 / 0{,}02 = 400$ bidones por día.

| Dotación fija | 12 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|---|
| Partiendo con 15 | $64.796.360 | $62.471.840 | $59.034.600 | **$57.133.240** | $58.191.400 | $64.331.600 |
| Partiendo con 17 | $66.106.360 | $63.781.840 | $60.344.600 | $58.443.240 | **$58.381.400** | $63.401.600 |

(a) Con 15 trabajadores gana el plan de **15 trabajadores**: $57.133.240, con horas extra en los
meses 4 y 5 y sin faltantes. Con 12 y 13 las horas extra no alcanzan y se acumulan faltantes.
(b) Sí. Partiendo con 17, despedir a dos cuesta $1.310.000 y la mejor opción pasa a ser
**16 trabajadores** ($58.381.400), que gana por $61.840. La dotación de partida es parte del
problema: el mismo pronóstico da planes distintos según con cuánta gente se empieza.

**6.10.** (a) Variables $x_{ts}$ para cada fuente (inicial, regular, extra, subcontratada) del mes
$t$ y cada mes de venta $s \ge t$. Minimizar $\sum c_{ts} x_{ts}$ con $c_{ts}$ = costo de la fuente
$+ 250\,(s - t)$; capacidad de cada fuente como cota y $\sum_t x_{ts} = D_s$. (b) Mes a mes, la
celda más barata:

| Mes de venta | Asignación (cajas · costo por caja) |
|---|---|
| 1 | inicial 200 · \$0 · regular mes 1: 3.550 · $2.000 |
| 2 | regular mes 2: 4.150 · $2.000 · regular mes 1: 600 · $2.250 · extra mes 2: 150 · $3.000 |
| 3 | regular mes 3: 4.150 · $2.000 · extra mes 3: 600 · $3.000 · extra mes 2: 450 · $3.250 · subcontrato mes 3: 400 · $3.400 |

Costo mínimo **$30.122.500** (la programación lineal da lo mismo). (c) Las 600 cajas regulares que
sobran en el mes 1: guardarlas un mes ($2.250) es más barato que cualquier hora extra ($3.000).
Por la misma razón, el mes 3 usa 450 cajas de horas extra del mes 2 ($3.250) antes que
subcontratar ($3.400).

---

## 9. Caso integrador · Estampa Sur, el plan del semestre

> Este caso sigue a Estampa Sur por todo el ramo. Cada unidad parte de lo que calculó la anterior;
> acá se usa el pronóstico de la unidad 4. Si no has hecho esa unidad, parte de esta tabla.

Estampa Sur estampa poleras, polerones, bolsas y gorros. El plan agregado mide la familia en
prendas. El pronóstico (redondeado a la centena) y los días hábiles son:

| Mes | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Demanda (prendas) | 6.100 | 6.200 | 6.200 | 6.300 | 6.400 | 6.500 |
| Días hábiles | 20 | 19 | 22 | 21 | 20 | 22 |

Cada prenda toma 0,12 HH; la jornada es de 8 horas, así que un trabajador hace
$8 / 0{,}12 \approx 66{,}7$ prendas por día. Hay 4 trabajadores y 510 prendas en bodega. Costos:
contratar $380.000, despedir $500.000, hora normal $4.500, hora extra $6.750, mantener \$300
por prenda y mes y faltante $1.200 por prenda y mes. Las horas extra no pueden pasar del 20 % de
la producción regular.

**Pregunta.** El dueño quiere una estrategia mixta: dotación fija más horas extra, aceptando
faltantes si las horas extra no alcanzan. ¿Cuántas personas fijas conviene tener y cuánto cuesta
el semestre?

**Desarrollo.** Se prueban dotaciones de 2 a 9. Con 3, las horas extra no alcanzan y los faltantes
llegan a 7.430 prendas ($47.693.600); con 5 sobra producción ($27.237.800). Gana **4
trabajadores**, la dotación actual:

| Mes | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Producción regular | 5.333 | 5.067 | 5.867 | 5.600 | 5.333 | 5.867 |
| Horas extra (prendas) | 257 | 1.013 | 453 | 700 | 1.067 | 633 |
| Producción total | 5.590 | 6.080 | 6.320 | 6.300 | 6.400 | 6.500 |
| Inventario final | 0 | −120 | 0 | 0 | 0 | 0 |
| Sueldos | 2.880.000 | 2.736.000 | 3.168.000 | 3.024.000 | 2.880.000 | 3.168.000 |
| Horas extra ($) | 208.170 | 820.530 | 366.930 | 567.000 | 864.270 | 512.730 |
| Faltantes ($) | 0 | 144.000 | 0 | 0 | 0 | 0 |

Sueldos $17.856.000, horas extra $3.339.630 y faltantes $144.000: costo total
**$21.339.630**.

**Lectura.** El mes 1 usa las 510 prendas de bodega y 257 en horas extra. En el mes 2 el tope
(20 % de 5.067 = 1.013) se queda corto y faltan **120 prendas**, que el mes 3 recupera con horas
extra. Contratar un quinto trabajador sale $5.898.170 más caro: su sueldo de todo el semestre
cuesta más que las horas extra que reemplaza. La señal para vigilar es otra: los cuatro trabajan
horas extra **todos** los meses. Si el pronóstico sigue subiendo, el quinto se vuelve necesario.

**Lo que pasa a la unidad 7.** La producción de los meses 1 y 2 (**5.590** y **6.080** prendas) es
la que el programa maestro reparte por producto y semana. Las 510 prendas en bodega también
pasan: el programa maestro las abre por producto y tienen que sumar lo mismo.

---

## 10. Para seguir

**En los libros del ramo.**

- Schroeder, *Administración de operaciones* (2.ª ed., 2004), capítulos 12, 13 y 16 (los que fija el
  programa para la planificación y el control de la producción).
- Heizer y Render, *Principios de administración de operaciones* (5.ª ed., 2004), capítulo de
  planeación agregada: estrategias, método gráfico y método de transporte. Sus problemas del final
  del capítulo son buena práctica adicional.
- Chase, Jacobs y Aquilano, *Administración de operaciones* (12.ª ed., 2009), capítulo de
  planeación agregada de ventas y operaciones.

**Abiertos y gratis.**

- Abbas y Goosheh, *Operations Management*, Fanshawe College (2025), en inglés, capítulo de
  planeación agregada (sales and operations planning). Descarga en la colección abierta de Ontario:
  https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/2473

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame un plan agregado de cuatro meses con
horas extra y subcontratación, y corrígeme el costo mes a mes».
