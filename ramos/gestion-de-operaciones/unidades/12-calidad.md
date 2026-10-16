---
ramo: Gestión de Operaciones
unidad: 12
titulo: Calidad y control estadístico de procesos
version: 0.1 (15-10-2026)
requiere: [03-proceso-y-capacidad, 11-fisica-de-la-fabrica]
alimenta: []
verificacion: verificacion/u12_calidad.py
---

# Unidad 12 · Calidad y control estadístico de procesos

**Qué vas a poder hacer.** Clasificar lo que gasta una empresa en calidad y decir dónde conviene
gastar; distinguir la variación normal de un proceso de una causa que hay que buscar; construir y
leer cartas de control $\bar X$ y $R$, $p$ y $c$; aplicar las reglas que detectan un proceso fuera
de control; medir con $C_p$ y $C_{pk}$ si un proceso puede cumplir la tolerancia del cliente, y
ordenar una mejora con DMAIC.

**Lo que necesitas antes.** Probabilidad básica: media, desviación estándar y la distribución
normal (leer una tabla de $Z$). De la unidad 11 sirve la idea de que la variabilidad cuesta.

**Tiempo.** Unas 5 horas: 2 de lectura con el ejemplo y 3 de práctica.

---

## 1. La idea · qué es calidad y cuánto cuesta

Calidad es **cumplir lo que el cliente espera, todas las veces**. Tiene dos caras:

- **Calidad de diseño:** qué promete el producto (una polera con estampado de cuatro colores).
- **Calidad de conformidad:** si cada unidad cumple lo prometido (los cuatro colores calzan en todas).

Esta unidad trata de la segunda: medir, controlar y mejorar la conformidad.

### Los cuatro costos de la calidad

| Categoría | Cuándo se gasta | Ejemplos |
|---|---|---|
| **Prevención** | antes de producir, para que no haya fallas | capacitación, mantención preventiva, diseño del proceso, proveedores certificados |
| **Evaluación** | mientras se produce, para detectar fallas | inspección, ensayos, calibración de instrumentos, auditorías |
| **Falla interna** | la falla se detecta antes de que salga | desecho, reproceso, tiempo de máquina perdido, segunda selección |
| **Falla externa** | la falla la descubre el cliente | devoluciones, garantías, descuentos por reclamo, clientes que no vuelven |

Las dos primeras son el **costo de controlar**; las dos últimas, el **costo de no controlar**. La
regla práctica: un peso en prevención ahorra varios en falla, y la falla externa es la más cara
porque además de reponer el producto se pierde confianza (y ese costo no aparece en la
contabilidad).

> **La inspección no mejora el proceso.** Evaluar separa lo bueno de lo malo, pero la próxima
> unidad sale igual de mala. Solo la prevención cambia lo que se produce.

---

## 2. Variabilidad común y especial

Ningún proceso produce dos unidades iguales. La pregunta no es si varía, sino **por qué varía**.

| | Causa común (aleatoria) | Causa especial (asignable) |
|---|---|---|
| Qué es | la suma de muchas causas chicas, siempre presentes | un hecho puntual que se puede identificar |
| Ejemplos | humedad del día, pequeñas diferencias de la tela, pulso del operador | un marco suelto, un lote de tinta distinto, un operador nuevo |
| Qué hace con los datos | patrón estable y predecible | un punto raro, un salto o una tendencia |
| Quién la corrige | la gerencia: hay que **cambiar el sistema** | el operador o el supervisor: hay que **encontrarla y eliminarla** |

Un proceso que solo tiene variación común está **bajo control estadístico**: es predecible. Eso no
significa que sea bueno; significa que su resultado futuro se puede anticipar.

Hay dos errores simétricos:

- **Sobreajustar:** tratar la variación común como especial (mover la máquina cada vez que una
  medida sale un poco alta). Aumenta la variación.
- **No reaccionar:** tratar una causa especial como común. El problema sigue ahí y se repite.

Las cartas de control existen para distinguir una de otra con una regla, no con la intuición.

---

## 3. Cartas de control por variables · $\bar X$ y $R$

Se usan cuando se **mide** algo continuo (peso, largo, desplazamiento). Se toman $k$ subgrupos de
$n$ unidades seguidas (típicamente $n = 4$ o $5$, con $k \ge 20$). Para cada subgrupo $i$:

$$\bar x_i = \frac{1}{n}\sum_{j=1}^{n} x_{ij} \qquad R_i = \max_j x_{ij} - \min_j x_{ij}$$

Las líneas centrales son los promedios de las medias y de los rangos:

$$\bar{\bar X} = \frac{1}{k}\sum_{i=1}^{k} \bar x_i \qquad \bar R = \frac{1}{k}\sum_{i=1}^{k} R_i$$

Los límites de control están a tres desviaciones estándar de la línea central. Con las constantes de
la tabla:

$$LSC_{\bar X} = \bar{\bar X} + A_2 \bar R \qquad LIC_{\bar X} = \bar{\bar X} - A_2 \bar R$$

$$LSC_R = D_4 \bar R \qquad LIC_R = D_3 \bar R$$

| $n$ | $A_2$ | $D_3$ | $D_4$ | $d_2$ |
|---|---|---|---|---|
| 2 | 1,880 | 0 | 3,267 | 1,128 |
| 3 | 1,023 | 0 | 2,574 | 1,693 |
| 4 | 0,729 | 0 | 2,282 | 2,059 |
| 5 | 0,577 | 0 | 2,114 | 2,326 |
| 6 | 0,483 | 0 | 2,004 | 2,534 |
| 7 | 0,419 | 0,076 | 1,924 | 2,704 |
| 8 | 0,373 | 0,136 | 1,864 | 2,847 |
| 9 | 0,337 | 0,184 | 1,816 | 2,970 |
| 10 | 0,308 | 0,223 | 1,777 | 3,078 |

$d_2$ convierte el rango promedio en una estimación de la desviación estándar del proceso:
$\hat\sigma = \bar R / d_2$. De ahí sale $A_2 = 3 / (d_2\sqrt n)$.

**Las dos cartas se leen juntas.** La de $R$ dice si la **dispersión** es estable; la de $\bar X$,
si el **centro** es estable. Se mira primero $R$: si la dispersión está fuera de control, los
límites de $\bar X$ (que dependen de $\bar R$) no son confiables.

**Dos fases.**

1. **Fase I (establecer).** Con los datos históricos se calculan los límites. Si un punto sale y se
   encuentra su causa especial, se elimina ese subgrupo y se recalculan. Si no se encuentra causa,
   el punto se deja.
2. **Fase II (vigilar).** Los límites quedan fijos y cada subgrupo nuevo se compara contra ellos.

> **Límites de control no son especificaciones.** Los límites de control salen del proceso (lo que
> hace). Las especificaciones salen del cliente (lo que pide). Un proceso puede estar en control y
> producir unidades fuera de especificación. Eso lo mide la capacidad (sección 6).

---

## 4. Cartas de control por atributos · $p$ y $c$

Se usan cuando se **cuenta** en vez de medir.

**Carta $p$: proporción de unidades defectuosas.** Cada unidad es buena o defectuosa. Con $k$
muestras de tamaño $n_i$ y $d_i$ defectuosas:

$$\bar p = \frac{\sum d_i}{\sum n_i} \qquad \sigma_{p,i} = \sqrt{\frac{\bar p(1-\bar p)}{n_i}} \qquad LSC_i = \bar p + 3\sigma_{p,i} \qquad LIC_i = \max(0,\ \bar p - 3\sigma_{p,i})$$

Si $n$ cambia de una muestra a otra, **cada muestra tiene sus propios límites**. Una muestra grande
tiene límites más estrechos: con muchos datos, una misma proporción es una señal más fuerte.

**Carta $c$: número de defectos por unidad de inspección.** Una unidad puede tener varios defectos
(manchas en un rollo de tela, burbujas en una plancha). El conteo sigue una distribución de Poisson,
cuya varianza es igual a su media:

$$\bar c = \frac{\sum c_i}{k} \qquad LSC = \bar c + 3\sqrt{\bar c} \qquad LIC = \max(0,\ \bar c - 3\sqrt{\bar c})$$

| Pregunta | Carta |
|---|---|
| ¿Se mide una variable continua? | $\bar X$ y $R$ |
| ¿Cada unidad es buena o mala? | $p$ |
| ¿Se cuentan defectos en una unidad de tamaño fijo? | $c$ |

---

## 5. Reglas para detectar un proceso fuera de control

Un punto fuera de los límites es la señal más clara, pero no la única. Un proceso con causa especial
también deja **patrones** dentro de los límites. Esta unidad usa cuatro reglas (otros textos usan
rachas de 8 o 9; lo importante es fijar una y aplicarla siempre):

| Regla | Se dispara cuando | Qué suele indicar |
|---|---|---|
| **R1** | un punto queda fuera de $\pm 3\sigma$ | un hecho puntual (un lote, un ajuste mal hecho) |
| **R2** | 7 puntos seguidos quedan del mismo lado de la línea central | la media se corrió |
| **R3** | 6 puntos seguidos van subiendo (o bajando) | desgaste, temperatura que sube, fatiga |
| **R4** | 2 de 3 puntos seguidos quedan más allá de $\pm 2\sigma$ del mismo lado | un corrimiento que empieza |

Para $\bar X$, $\sigma$ es la desviación de las medias: $(LSC_{\bar X} - \bar{\bar X})/3$. Un punto
**sobre** la línea central no cuenta para la racha de ningún lado.

Cada regla agrega falsas alarmas. Con R1 sola, un proceso en control da una falsa alarma cada 370
puntos en promedio; con las cuatro, bastante más seguido. Por eso las reglas se eligen antes de
mirar los datos.

---

## 6. Capacidad de proceso · $C_p$ y $C_{pk}$

La carta dice si el proceso es **estable**. La capacidad dice si, estable, **cumple lo que pide el
cliente**: el límite inferior y el superior de especificación ($LIE$, $LSE$).

$$C_p = \frac{LSE - LIE}{6\sigma}$$

$C_p$ compara el ancho de la tolerancia con el ancho natural del proceso ($6\sigma$). No mira dónde
está la media: es la capacidad **potencial**, la que tendría si estuviera centrado.

$$C_{pk} = \min\left(\frac{LSE - \mu}{3\sigma},\ \frac{\mu - LIE}{3\sigma}\right)$$

$C_{pk}$ mide la distancia de la media a la especificación **más cercana**. Siempre
$C_{pk} \le C_p$, y son iguales solo si el proceso está centrado.

| Valor | Lectura |
|---|---|
| $< 1$ | el proceso no cabe en la tolerancia: produce fuera de especificación de forma sistemática |
| $1$ a $1{,}33$ | cabe justo; cualquier corrimiento produce defectos |
| $\ge 1{,}33$ | capaz; es el mínimo habitual que exige un cliente industrial |
| $\ge 2$ | nivel Seis Sigma: $\pm 6\sigma$ caben en la tolerancia |

**Cómo se estima $\sigma$.** Si el proceso está en control, con $\hat\sigma = \bar R / d_2$. Se usa
la desviación de las **unidades**, no la de las medias: el cliente recibe unidades.

**Fracción fuera de especificación.** Si las unidades se distribuyen normal:

$$P(\text{fuera}) = P\!\left(Z > \frac{LSE-\mu}{\sigma}\right) + P\!\left(Z < \frac{LIE-\mu}{\sigma}\right)$$

Fíjate que $\frac{LSE-\mu}{\sigma} = 3\,C_{ps}$: con $C_{pk} = 1$ el lado cercano deja 0,135 % afuera.

> **El orden importa.** La capacidad se calcula solo con un proceso en control. Si hay causas
> especiales, $\sigma$ no describe nada estable y el $C_{pk}$ no predice el futuro.

---

## 7. Ejemplo resuelto · envasadora de miel

Una envasadora de miel del valle del Itata llena frascos que dicen 500 g. Su cliente (una cadena de
supermercados) acepta de **497 a 509 g**. Cada hora se pesan 4 frascos seguidos. Estos son 8
subgrupos (en una planta real se esperan 20 o más antes de fijar límites):

| Subgrupo | $x_1$ | $x_2$ | $x_3$ | $x_4$ | $\bar x$ | $R$ |
|---|---|---|---|---|---|---|
| 1 | 503 | 501 | 505 | 502 | 502,75 | 4 |
| 2 | 504 | 502 | 500 | 503 | 502,25 | 4 |
| 3 | 502 | 506 | 503 | 504 | 503,75 | 4 |
| 4 | 501 | 503 | 502 | 499 | 501,25 | 4 |
| 5 | 505 | 503 | 504 | 506 | 504,50 | 3 |
| 6 | 502 | 500 | 503 | 502 | 501,75 | 3 |
| 7 | 504 | 505 | 502 | 503 | 503,50 | 3 |
| 8 | 503 | 501 | 504 | 505 | 503,25 | 4 |

**Paso 1 · Líneas centrales.**

$$\bar{\bar X} = \frac{4.023}{8} = 502{,}875 \text{ g} \qquad \bar R = \frac{29}{8} = 3{,}625 \text{ g}$$

**Paso 2 · Límites** (con $n = 4$: $A_2 = 0{,}729$, $D_3 = 0$, $D_4 = 2{,}282$).

$$LSC_{\bar X} = 502{,}875 + 0{,}729 \cdot 3{,}625 = 505{,}52 \qquad LIC_{\bar X} = 502{,}875 - 2{,}64 = 500{,}23$$

$$LSC_R = 2{,}282 \cdot 3{,}625 = 8{,}27 \qquad LIC_R = 0$$

**Paso 3 · Leer.** Primero $R$: todos los rangos (3 y 4) están entre 0 y 8,27. Después $\bar X$:
todas las medias están entre 500,23 y 505,52, sin rachas de 7 ni tendencias de 6. El proceso está
**en control**. Ahora tiene sentido preguntar por la capacidad.

**Paso 4 · Capacidad.**

$$\hat\sigma = \frac{\bar R}{d_2} = \frac{3{,}625}{2{,}059} = 1{,}761 \text{ g}$$

$$C_p = \frac{509 - 497}{6 \cdot 1{,}761} = 1{,}14 \qquad C_{ps} = \frac{509 - 502{,}875}{3 \cdot 1{,}761} = 1{,}16 \qquad C_{pi} = \frac{502{,}875 - 497}{3 \cdot 1{,}761} = 1{,}11$$

$C_{pk} = 1{,}11$. Fuera de especificación: $P(Z > 3{,}48) + P(Z < -3{,}34)$, es decir
0,025 % sobre 509 g más 0,042 % bajo 497 g: **0,07 %** en total.

**Cómo se lee.**

- El proceso es estable y cabe en la tolerancia, pero justo: $C_{pk}$ está bajo 1,33.
- El problema **no es el centrado**. Si se llenara exactamente en 503 g (el centro de la tolerancia),
  el $C_{pk}$ subiría solo a 1,14, el mismo $C_p$. Lo que limita es la dispersión: la máquina
  reparte 1,76 g de desviación en una tolerancia de 12 g.
- Para llegar a 1,33 hay que bajar $\sigma$ (mantención de la dosificadora, miel a temperatura
  pareja), no mover el ajuste. Si el operador mueve el ajuste cada vez que un frasco sale alto,
  sobreajusta y empeora.

---

## 8. DMAIC · el marco de la mejora

Las cartas y la capacidad dicen **dónde** está el problema. DMAIC (el ciclo de Seis Sigma) ordena
**cómo** se resuelve:

| Fase | Pregunta | Herramientas de esta unidad |
|---|---|---|
| **D**efinir | ¿Qué le importa al cliente y cuál es la meta? | especificación, costo de la falla externa |
| **M**edir | ¿Cómo está hoy el proceso, en números? | carta $\bar X$ y $R$, carta $p$, $C_p$, $C_{pk}$ |
| **A**nalizar | ¿Cuál es la causa? ¿Común o especial? | puntos fuera, reglas de racha, centrado frente a dispersión |
| **I**ntegrar mejoras (*Improve*) | ¿Qué se cambia y cuánto mejora? | $C_{pk}$ esperado tras el cambio, costo de prevención |
| **C**ontrolar | ¿Cómo se sostiene? | nuevos límites en fase II, plan de reacción |

DMAIC es un ciclo: lo que se controla en la última fase se vuelve la línea base de la próxima mejora.

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Usar las especificaciones como límites de control | Los límites salen de $\bar{\bar X}$ y $\bar R$; las especificaciones, del cliente |
| Calcular la capacidad con un proceso fuera de control | Primero carta y limpieza de causas especiales; después $C_p$ y $C_{pk}$ |
| Usar la desviación de las medias en $C_p$ | $\hat\sigma = \bar R/d_2$ es la de las unidades; la de las medias es $\hat\sigma/\sqrt n$ |
| Dejar el $LIC$ negativo en una carta $R$, $p$ o $c$ | Un rango, una proporción o un conteo no bajan de cero: $LIC = \max(0, \dots)$ |
| Creer que «en control» significa «bueno» | En control es predecible; si el $C_{pk}$ es bajo, produce defectos de forma predecible |
| Informar solo $C_p$ | $C_p$ ignora el centrado; un proceso descentrado tiene $C_p$ alto y $C_{pk}$ bajo |
| En la carta $p$ con $n$ variable, usar un solo límite | Cada muestra tiene su $\sigma_{p,i}$ con su propio $n_i$ |
| Mirar $\bar X$ sin mirar antes $R$ | Si $R$ está fuera de control, los límites de $\bar X$ no valen |

---

## 10. Práctica

Diez ejercicios: 12.1 a 12.4 básicos, 12.5 a 12.8 intermedios, 12.9 y 12.10 de desafío. Las pautas
están en la sección 11. Usa la tabla de constantes de la sección 3.

**12.1 · Costos de calidad de una panadería industrial (básico).** Una panadería de Chillán vende
$72.000.000 al mes. Clasifica cada partida en prevención, evaluación, falla interna o falla externa;
suma cada categoría, calcula el costo total de calidad como porcentaje de las ventas y qué fracción
del total se va en fallas. ¿Dónde pondrías el próximo peso?

| Partida (mensual) | Monto |
|---|---|
| Capacitación en buenas prácticas de manufactura | $380.000 |
| Mantención preventiva de hornos | $520.000 |
| Inspección de masa y temperatura en cada turno | $640.000 |
| Calibración de balanzas | $110.000 |
| Pan desechado por quemado o crudo | $1.350.000 |
| Reproceso de masa fuera de punto | $290.000 |
| Devoluciones de supermercados | $1.920.000 |
| Descuento comercial por reclamos | $450.000 |

**12.2 · Pernos de una maestranza (básico).** Una maestranza de Talcahuano controla el largo de un
perno con subgrupos de 5. En la fase I obtuvo $\bar{\bar X} = 40{,}12$ mm y $\bar R = 0{,}42$ mm.
Calcula los límites de las dos cartas y di si cada uno de estos tres subgrupos nuevos está en
control: (a) $\bar x = 40{,}31$, $R = 0{,}38$; (b) $\bar x = 40{,}45$, $R = 0{,}51$;
(c) $\bar x = 40{,}05$, $R = 0{,}95$.

**12.3 · Tres máquinas de corte (básico).** Una planta de envases corta piezas de
120,00 ± 0,30 mm. Las tres máquinas están en control. Calcula $C_p$ y $C_{pk}$ de cada una e indica
cuál deja más piezas fuera y por qué.

| Máquina | Media (mm) | $\sigma$ (mm) |
|---|---|---|
| A | 120,00 | 0,12 |
| B | 120,00 | 0,07 |
| C | 120,15 | 0,07 |

**12.4 · Manguera de riego (básico).** Una fábrica de Ñuble cuenta las fallas (poros y
aplastamientos) en rollos de 100 m. Arma la carta $c$, identifica los rollos fuera de control y
recalcula los límites sin ellos.

| Rollo | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fallas | 4 | 6 | 3 | 5 | 7 | 2 | 5 | 13 | 4 | 6 | 3 | 5 |

**12.5 · Espesor de tablas (intermedio).** Un aserradero de Los Ángeles mide el espesor de 4 tablas
seguidas cada media hora (mm). Construye las cartas $\bar X$ y $R$, encuentra el subgrupo fuera de
control y di qué tipo de causa sugiere. Si se confirma la causa (un diente roto de la sierra),
recalcula los límites sin ese subgrupo.

| Subgrupo | $x_1$ | $x_2$ | $x_3$ | $x_4$ |
|---|---|---|---|---|
| 1 | 25,1 | 24,9 | 25,0 | 25,2 |
| 2 | 24,8 | 25,0 | 25,1 | 24,9 |
| 3 | 25,0 | 25,2 | 24,9 | 25,1 |
| 4 | 25,1 | 25,0 | 24,8 | 25,0 |
| 5 | 24,9 | 25,1 | 25,0 | 25,2 |
| 6 | 25,0 | 24,9 | 25,1 | 25,0 |
| 7 | 24,4 | 25,6 | 25,3 | 24,7 |
| 8 | 25,2 | 25,0 | 25,1 | 24,9 |
| 9 | 24,9 | 25,0 | 24,8 | 25,1 |
| 10 | 25,0 | 25,1 | 25,0 | 24,9 |

**12.6 · Etiquetado en una viña (intermedio).** Una viña del Maule revisa 200 botellas al día y
cuenta las mal etiquetadas. Arma la carta $p$ de los 15 días, identifica los días fuera de control
y recalcula sin ellos. ¿Qué proporción de botellas mal etiquetadas debería esperar la viña en un día
normal?

| Día | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Mal etiquetadas | 6 | 4 | 8 | 5 | 7 | 3 | 6 | 18 | 5 | 4 | 7 | 6 | 5 | 8 | 4 |

**12.7 · Rachas y tendencias (intermedio).** Una carta $\bar X$ tiene línea central 50,0 y
$\sigma_{\bar x} = 1{,}0$ (límites 47,0 y 53,0). Aplica las cuatro reglas de la sección 5 a estas 20
medias: ¿cuál se dispara primero, en qué subgrupo y qué historia cuentan los datos?

| Subgrupo | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Media | 50,4 | 49,2 | 51,1 | 50,6 | 48,9 | 50,2 | 50,8 | 51,3 | 50,5 | 51,0 |

| Subgrupo | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|
| Media | 50,9 | 51,6 | 50,3 | 49,8 | 49,5 | 49,1 | 48,6 | 48,2 | 47,7 | 49,3 |

**12.8 · Bujes (intermedio).** El diámetro interior de un buje se controla con subgrupos de 5 y está
en control con $\bar{\bar X} = 74{,}80$ mm y $\bar R = 1{,}86$ mm. La especificación es de 72,0 a
78,0 mm. (a) Estima $\sigma$ y calcula $C_p$, $C_{pk}$ y la fracción fuera de especificación.
(b) ¿Cuánto vale $C_{pk}$ si se centra en 75,0? (c) Sin moverla de 74,80, ¿qué $\sigma$ (y qué
$\bar R$) haría falta para un $C_{pk}$ de 1,33?

**12.9 · Carta $p$ con muestras de distinto tamaño (desafío).** Un centro de despacho revisa cada
día una cantidad distinta de pedidos y cuenta los que tienen error de registro. Arma la carta $p$
con límites para cada día. Después compara los días 8 y 10: tienen la misma proporción de error,
¿por qué uno está en control y el otro no?

| Día | Pedidos revisados | Con error |
|---|---|---|
| 1 | 300 | 12 |
| 2 | 220 | 9 |
| 3 | 410 | 15 |
| 4 | 180 | 8 |
| 5 | 380 | 22 |
| 6 | 250 | 10 |
| 7 | 290 | 11 |
| 8 | 160 | 13 |
| 9 | 240 | 9 |
| 10 | 640 | 52 |

**12.10 · Inspeccionar o prevenir (desafío).** Una planta de cecinas envasa 30.000 paquetes al mes.
El peso de un paquete se distribuye normal con media 251,2 g y $\sigma = 0{,}9$ g; la norma acepta de
248,0 a 253,0 g. Cada paquete fuera de norma que llega al cliente cuesta $4.500 (devolución y
multa). Trabaja con paquetes enteros.

- (a) Calcula $C_{pk}$, la fracción fuera de norma, los paquetes malos al mes y el costo de no hacer
  nada.
- (b) Compara dos opciones. **A:** inspeccionar el 100 % a $35 por paquete; la inspección detecta el
  95 % de los malos, y cada malo detectado se reprocesa a $900. **B:** ajustar la dosificadora para
  centrar el peso en 250,5 g, a $1.200.000 al mes, sin inspección. ¿Cuál es más barata? Clasifica
  cada costo en las cuatro categorías.
- (c) ¿Hasta qué $\sigma$ habría que bajar la dispersión para que B (centrada y sin inspección) iguale
  el costo de A?

---

## 11. Pautas

**12.1.**

| Categoría | Partidas | Monto | % del costo de calidad |
|---|---|---|---|
| Prevención | capacitación, mantención de hornos | $900.000 | 15,9 % |
| Evaluación | inspección de masa, calibración | $750.000 | 13,3 % |
| Falla interna | pan desechado, reproceso | $1.640.000 | 29,0 % |
| Falla externa | devoluciones, descuentos | $2.370.000 | 41,9 % |
| **Total** | | **$5.660.000** | |

(Los porcentajes suman 100,1 % por redondeo.) El costo de calidad es el **7,9 %** de las ventas y el
**70,8 %** de ese costo ($4.010.000) son fallas. La panadería gasta casi la mitad de su costo de
calidad en que el supermercado le devuelva pan. El próximo peso va a **prevención**: control de
temperatura y tiempos del horno (la causa del pan quemado o crudo) antes que más inspección.

**12.2.** $A_2 \bar R = 0{,}577 \cdot 0{,}42 = 0{,}24$: carta $\bar X$ de **39,88 a 40,36** mm. Carta
$R$: $LSC = 2{,}114 \cdot 0{,}42 = 0{,}89$ y $LIC = 0$. (a) En control en las dos. (b) La media
(40,45) supera 40,36: **fuera** en $\bar X$; el centro se corrió. (c) La media está bien, pero el
rango (0,95) supera 0,89: **fuera** en $R$; la dispersión aumentó. Una media dentro de límites no
salva un rango fuera.

**12.3.**

| Máquina | $C_p$ | $C_{pk}$ | Fuera de especificación |
|---|---|---|---|
| A | 0,83 | 0,83 | 1,24 % |
| B | 1,43 | 1,43 | 0,002 % |
| C | 1,43 | 0,71 | 1,61 % |

C es tan precisa como B, pero está corrida 0,15 mm hacia arriba: deja más piezas fuera que A, que es
la más dispersa. A tiene un problema de **dispersión** (no cabe aunque esté centrada); C, de
**centrado** (cabe, pero mal ubicada). Arreglar C es un ajuste; arreglar A exige cambiar la máquina o
el método.

**12.4.** $\bar c = 63/12 = 5{,}25$; $\sqrt{5{,}25} = 2{,}29$. $LSC = 5{,}25 + 3 \cdot 2{,}29 = 12{,}12$
y $LIC = \max(0;\ -1{,}62) = 0$. El **rollo 8** (13 fallas) está fuera. Sin él: $\bar c = 50/11 = 4{,}55$
y $LSC = 10{,}94$, $LIC = 0$. Los once rollos restantes quedan dentro. Hay que averiguar qué pasó con
el rollo 8 (cambio de resina, temperatura de la extrusora) antes de usar los nuevos límites.

**12.5.** Con los 10 subgrupos: $\bar{\bar X} = 25{,}008$ mm y $\bar R = 0{,}370$ mm. Carta $\bar X$:
$25{,}008 \pm 0{,}729 \cdot 0{,}370$, de **24,74 a 25,28**. Carta $R$: $LSC = 2{,}282 \cdot 0{,}370 = 0{,}84$,
$LIC = 0$. Todas las medias están en control (la del subgrupo 7 es 25,00), pero el **rango del
subgrupo 7** (1,2 mm) supera 0,84. Es una causa especial de **dispersión**: tablas muy gruesas y muy
delgadas en la misma media hora, lo que calza con un diente roto. Sin el subgrupo 7:
$\bar{\bar X} = 25{,}008$, $\bar R = 0{,}278$; carta $\bar X$ de **24,81 a 25,21** y carta $R$ con
$LSC = 0{,}63$. Todo queda en control. Mirar solo $\bar X$ habría escondido el problema.

**12.6.** $\bar p = 96/3.000 = 0{,}0320$. $\sigma_p = \sqrt{0{,}032 \cdot 0{,}968/200} = 0{,}0124$, así que
$LSC = 0{,}0693$ y $LIC = 0$. El **día 8** ($18/200 = 0{,}09$) está fuera. Sin él:
$\bar p = 78/2.800 = 0{,}0279$, $LSC = 0{,}0628$, $LIC = 0$. En un día normal la viña debe esperar
cerca de **2,8 %** de botellas mal etiquetadas: eso es variación común, y bajarla exige cambiar la
etiquetadora o el proceso, no castigar al turno.

**12.7.** R1 no se dispara (el mínimo, 47,7, está sobre 47,0). R4 tampoco (solo el 47,7 pasa de
48,0). **R2 se dispara primero, en el subgrupo 12**: los subgrupos 6 a 12 están todos sobre 50,0 (y
sigue en el 13). Después **R3 en el subgrupo 17**: del 12 al 17 las medias bajan seis veces seguidas
(sigue en el 18 y el 19). Y R2 vuelve en el 20, ahora bajo la línea (subgrupos 14 a 20). La historia:
la media subió cerca de un punto hacia el subgrupo 6 y, desde el 12, empezó a caer en forma
sostenida (desgaste de una herramienta o un ajuste que se afloja). Ningún punto salió de los límites:
con R1 sola, nadie habría reaccionado.

**12.8.** (a) $\hat\sigma = 1{,}86/2{,}326 = 0{,}800$ mm. $C_p = 6/(6 \cdot 0{,}800) = 1{,}25$.
$C_{ps} = (78 - 74{,}8)/2{,}4 = 1{,}33$ y $C_{pi} = (74{,}8 - 72)/2{,}4 = 1{,}17$, así que
$C_{pk} = 1{,}17$. Fuera: 0,003 % sobre 78 y 0,023 % bajo 72, **0,026 %** en total. (b) Centrado en
75,0, $C_{pk} = C_p = 1{,}25$. (c) El lado cercano es el inferior (2,8 mm). Hace falta
$\sigma = 2{,}8/(3 \cdot 1{,}33) = 0{,}702$ mm, es decir $\bar R = 0{,}702 \cdot 2{,}326 = 1{,}63$ mm. Bajar el
rango promedio de 1,86 a 1,63 mm.

**12.9.** $\bar p = 161/3.070 = 0{,}0524$. Cada día tiene su $\sigma_{p,i} = \sqrt{\bar p(1-\bar p)/n_i}$:

| Día | $p_i$ | $LIC_i$ | $LSC_i$ | ¿En control? |
|---|---|---|---|---|
| 1 | 0,0400 | 0,0138 | 0,0911 | sí |
| 2 | 0,0409 | 0,0074 | 0,0975 | sí |
| 3 | 0,0366 | 0,0194 | 0,0855 | sí |
| 4 | 0,0444 | 0,0026 | 0,1023 | sí |
| 5 | 0,0579 | 0,0181 | 0,0867 | sí |
| 6 | 0,0400 | 0,0101 | 0,0947 | sí |
| 7 | 0,0379 | 0,0132 | 0,0917 | sí |
| 8 | 0,0813 | 0,0000 | 0,1053 | sí |
| 9 | 0,0375 | 0,0093 | 0,0956 | sí |
| 10 | 0,0813 | 0,0260 | 0,0789 | **no** |

Los días 8 y 10 tienen la misma proporción (13/160 y 52/640 son 0,0813). Con 160 pedidos, 8 % de
error cabe en la variación común; con 640, la misma proporción es una señal fuerte, porque el límite
se estrecha con $\sqrt{n}$. El día 10 merece una investigación (¿un digitador nuevo para el día de
mayor carga?). El día 8 no.

**12.10.** (a) $z_{sup} = (253 - 251{,}2)/0{,}9 = 2{,}00$ y $z_{inf} = (248 - 251{,}2)/0{,}9 = -3{,}56$.
Fuera: **2,29 %** (casi todo por arriba). $C_{pk} = 1{,}8/2{,}7 = 0{,}67$. Son 688 paquetes malos al
mes; no hacer nada cuesta 688 × 4.500, es decir $3.096.000 al mes en falla externa.

(b)

| | A · inspeccionar todo | B · centrar en 250,5 g |
|---|---|---|
| Evaluación (inspección) | $1.050.000 | 0 |
| Prevención (ajuste) | 0 | $1.200.000 |
| Falla interna | 654 detectados · $900 = $588.600 | 0 |
| Falla externa | 34 que escapan · $4.500 = $153.000 | 164 malos · $4.500 = $738.000 |
| **Total al mes** | $1.791.600 | $1.938.000 |

Centrada, la fracción fuera baja a 0,547 % ($C_{pk} = C_p = 0{,}93$). A es más barata este mes por
$146.400. Pero A es puro costo de evaluación: el proceso sigue produciendo 688 malos y la planta
paga por separarlos todos los meses. B cambia el proceso.

(c) B iguala a A cuando $\sigma$ baja a **0,877 g** (desde 0,9). Con un ajuste de la dosificadora y
una mejora chica de la dispersión, prevenir sale más barato que inspeccionar, y además deja de
producir los malos. La recomendación: hacer B y usar parte de lo que se ahorra en bajar $\sigma$; la
inspección al 100 % se deja solo mientras tanto.

---

## 12. Caso integrador · Estampa Sur, control del registro

> Este caso sigue a Estampa Sur por todo el ramo. Hasta la unidad 11 se decidió cuánto, cuándo y en
> qué orden producir; esta pieza pregunta si lo que se produce sale bien. Los datos son propios de
> esta unidad: no dependen de las anteriores.

Un club deportivo encargó 3.000 poleras con un escudo de dos colores. El **registro** es el calce
entre el color 1 y el color 2: se mide el desplazamiento del color 2 respecto de su posición
correcta, en mm (positivo hacia la derecha). El objetivo es 0,00 mm y el club acepta
**±0,25 mm**; más allá, el escudo se ve «corrido».

Durante 20 turnos se midieron 5 poleras seguidas por turno. Los datos son simulados con la semilla
1009 del verificador (`verificacion/u12_calidad.py`, semilla 1009 en `SEMILLA_CASO`), para que
cualquiera pueda regenerarlos.

| Subgrupo | $x_1$ | $x_2$ | $x_3$ | $x_4$ | $x_5$ | $\bar x$ | $R$ |
|---|---|---|---|---|---|---|---|
| 1 | 0,10 | 0,14 | 0,15 | 0,11 | 0,20 | 0,140 | 0,10 |
| 2 | -0,02 | -0,09 | 0,06 | 0,08 | 0,01 | 0,008 | 0,17 |
| 3 | 0,11 | 0,09 | -0,04 | 0,00 | 0,13 | 0,058 | 0,17 |
| 4 | 0,17 | -0,02 | 0,02 | 0,02 | 0,06 | 0,050 | 0,19 |
| 5 | -0,12 | -0,06 | 0,14 | 0,15 | -0,07 | 0,008 | 0,27 |
| 6 | 0,10 | -0,07 | 0,12 | 0,00 | 0,08 | 0,046 | 0,19 |
| 7 | 0,05 | 0,14 | 0,12 | 0,02 | 0,00 | 0,066 | 0,14 |
| 8 | 0,08 | 0,12 | 0,20 | 0,13 | 0,13 | 0,132 | 0,12 |
| 9 | 0,03 | 0,00 | 0,09 | -0,07 | 0,06 | 0,022 | 0,16 |
| 10 | 0,05 | 0,07 | -0,09 | 0,13 | 0,01 | 0,034 | 0,22 |
| 11 | 0,04 | 0,11 | 0,03 | -0,09 | 0,14 | 0,046 | 0,23 |
| 12 | 0,12 | 0,03 | 0,09 | 0,15 | 0,01 | 0,080 | 0,14 |
| 13 | -0,07 | 0,13 | 0,15 | -0,04 | 0,09 | 0,052 | 0,22 |
| 14 | 0,18 | 0,19 | 0,13 | 0,16 | 0,31 | 0,194 | 0,18 |
| 15 | 0,11 | 0,04 | 0,07 | 0,13 | 0,09 | 0,088 | 0,09 |
| 16 | 0,05 | 0,03 | 0,05 | 0,09 | 0,07 | 0,058 | 0,06 |
| 17 | 0,14 | 0,10 | -0,14 | 0,01 | -0,03 | 0,016 | 0,28 |
| 18 | 0,09 | 0,05 | 0,08 | 0,00 | 0,17 | 0,078 | 0,17 |
| 19 | 0,07 | 0,04 | 0,16 | 0,01 | 0,09 | 0,074 | 0,15 |
| 20 | 0,17 | 0,04 | 0,06 | 0,09 | 0,00 | 0,072 | 0,17 |

Además, cada día se revisaron 150 poleras terminadas y se contaron las defectuosas por cualquier
causa (registro, manchas, tinta corrida):

| Día | Defectuosas | $p$ |
|---|---|---|
| 1 | 8 | 0,053 |
| 2 | 7 | 0,047 |
| 3 | 9 | 0,060 |
| 4 | 6 | 0,040 |
| 5 | 4 | 0,027 |
| 6 | 6 | 0,040 |
| 7 | 8 | 0,053 |
| 8 | 5 | 0,033 |
| 9 | 18 | 0,120 |
| 10 | 3 | 0,020 |
| 11 | 7 | 0,047 |
| 12 | 5 | 0,033 |
| 13 | 7 | 0,047 |
| 14 | 5 | 0,033 |
| 15 | 7 | 0,047 |
| 16 | 7 | 0,047 |
| 17 | 6 | 0,040 |
| 18 | 8 | 0,053 |
| 19 | 1 | 0,007 |
| 20 | 8 | 0,053 |

**Pregunta.** ¿Está en control el registro? ¿Puede cumplir los ±0,25 mm del club? ¿Qué dice la
carta $p$? Cierra con un plan DMAIC.

**Desarrollo.**

*Carta $\bar X$ y $R$ con los 20 subgrupos* ($n = 5$: $A_2 = 0{,}577$, $D_4 = 2{,}114$, $D_3 = 0$).
$\bar{\bar X} = 1{,}322/20 = 0{,}066$ mm y $\bar R = 3{,}42/20 = 0{,}171$ mm. Carta $\bar X$ de **-0,033 a 0,165**; carta $R$
de 0 a 0,361. Los rangos están todos en control. En $\bar X$, el **subgrupo 14** (0,194) supera el
límite superior. El registro del turno revela la causa: ese turno se cambió el marco y quedó mal
apretado. Es causa especial y se elimina.

*Sin el subgrupo 14.* $\bar{\bar X} = 1{,}128/19 = 0{,}059$ mm y $\bar R = 3{,}24/19 = 0{,}1705$ mm. Carta $\bar X$ de
**-0,039 a 0,158**; carta $R$ de 0 a 0,360. Los 19 subgrupos quedan dentro y ninguna de las
reglas R2 a R4 se dispara. El proceso está **en control**.

*Capacidad.* $\hat\sigma = \bar R/d_2 = 0{,}1705/2{,}326 = 0{,}0733$ mm.

$$C_p = \frac{0{,}50}{6 \cdot 0{,}0733} = 1{,}14 \qquad C_{ps} = \frac{0{,}25 - 0{,}059}{3 \cdot 0{,}0733} = 0{,}87 \qquad C_{pi} = \frac{0{,}059 + 0{,}25}{3 \cdot 0{,}0733} = 1{,}41$$

$C_{pk} = 0{,}87$: se espera un **0,467 %** de poleras con el escudo corrido más allá de 0,25 mm, casi
todas hacia la derecha. Si la media estuviera en 0,00, el $C_{pk}$ subiría a 1,14 y la fracción
fuera bajaría a 0,065 %.

*Carta $p$.* $\bar p = 135/3.000 = 0{,}0450$; $\sigma_p = \sqrt{0{,}045 \cdot 0{,}955/150}$, así que
$LSC = 0{,}0958$ y $LIC = 0$. El **día 9** (0,120) está fuera: ese día entró un lote nuevo de tinta
que se corrió en el secado. Sin el día 9: $\bar p = 117/2.850 = 0{,}0411$, $LSC = 0{,}0897$, $LIC = 0$.

**Lectura.** Hay dos causas especiales (el marco del subgrupo 14 y la tinta del día 9) que se
corrigen en el piso. Pero lo más importante es lo que queda **en control**: un registro corrido
0,06 mm hacia la derecha en todos los turnos y un 4,1 % de prendas defectuosas todos los días. Eso es
variación común: no lo arregla el operador; lo arregla un cambio del sistema.

**Mini DMAIC.**

| Fase | Estampa Sur |
|---|---|
| Definir | El club acepta ±0,25 mm de registro. Meta: $C_{pk} \ge 1{,}33$ y bajar el 4,1 % de defectuosas. Una polera devuelta por el club es falla externa: la más cara. |
| Medir | Registro: $C_p = 1{,}14$, $C_{pk} = 0{,}87$. Defectuosas: $\bar p = 4{,}1\ \%$ en un día normal. |
| Analizar | Dos causas especiales (marco suelto, lote de tinta). Causa común: la media está corrida hacia la derecha (el tope de registro de la paleta) y la dispersión es de 0,073 mm. |
| Mejorar | (1) Recentrar el tope de registro: $C_{pk}$ sube a 1,14. (2) Para 1,33 ya centrado hace falta $\sigma = 0{,}25/(3 \cdot 1{,}33) = 0{,}063$ mm, o sea $\bar R = 0{,}146$ mm: bajar la dispersión un 15 % (pallets fijos y tensión de malla pareja). (3) Lista de chequeo de apriete al cambiar marco y prueba de cada lote de tinta antes de usarlo: prevención. |
| Controlar | Fase II con los límites limpios ($\bar X$ de -0,039 a 0,158; $R$ hasta 0,360) hasta recalcularlos tras el cambio; carta $p$ diaria con $LSC = 0{,}0897$. Plan de reacción: punto fuera o racha de 7, se detiene y se revisa marco y tinta. |

**Cierre de la cadena.** Con esta unidad termina el recorrido de Estampa Sur: la demanda decidió
cuánto producir, la planificación cuándo, la programación en qué orden, la física de la fábrica
cuánto espera cada orden, y la calidad, si lo producido sirve.

---

## 13. Para seguir

**En los libros del ramo.**

- Chase, Jacobs y Aquilano, *Administración de operaciones* (12.ª ed., 2009), capítulo de calidad
  Seis Sigma (costos de calidad, DMAIC) y capítulo de capacidad del proceso y control estadístico de
  procesos (cartas $\bar X$, $R$, $p$ y $C_{pk}$). Es la bibliografía que fija el programa para esta
  unidad.
- Heizer y Render, *Principios de administración de operaciones* (5.ª ed., 2004), capítulo de
  administración de la calidad y su suplemento de control estadístico de procesos: más ejercicios de
  cartas por atributos.

**Abiertos y gratis.**

- Abbas y Goosheh, *Operations Management*, Fanshawe College (2025), en inglés, en lo que trata de
  control de calidad. Descarga en la colección abierta de Ontario:
  https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/2473
- NIST/SEMATECH, *e-Handbook of Statistical Methods*, sección 6.3 «Univariate and Multivariate
  Control Charts» (en inglés): https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc3.htm

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame 20 subgrupos simulados con una causa
especial escondida y corrígeme la carta paso a paso».
