---
ramo: Gestión de Operaciones
unidad: 4
titulo: Pronósticos
version: 0.1 (15-10-2026)
requiere: []
alimenta: [05-inventarios, 06-planeacion-agregada]
verificacion: verificacion/u04_pronosticos.py
---

# Unidad 4 · Pronósticos

**Qué vas a poder hacer.** Elegir un método de pronóstico según la forma de la demanda; calcular
promedios móviles simples y ponderados, suavizamiento exponencial simple, Holt (con tendencia) y
Winter (con tendencia y estacionalidad); ajustar una recta por mínimos cuadrados, tanto en el tiempo
como con datos de corte transversal; medir el error con MAD, MSE y MAPE, y usar la señal de rastreo
para saber si un pronóstico está sesgado.

**Lo que necesitas antes.** Ninguna unidad previa del ramo. Basta con estadística básica: promedio,
desviación y la idea de una recta de mínimos cuadrados.

**Tiempo.** Unas 5 horas: 2 de lectura con los ejemplos y 3 de práctica.

---

## 1. La idea

Casi todas las decisiones de operaciones se toman antes de conocer la demanda: cuánto comprar,
cuánta gente contratar, cuánta capacidad instalar. El pronóstico es la única estimación de esa
demanda hasta que llega la real. Cuatro cosas conviene tener claras desde el principio:

1. **Un pronóstico casi siempre se equivoca.** Por eso un buen pronóstico viene con su medida de
   error.
2. **Agregar ayuda.** La demanda de una familia de productos se pronostica mejor que la de cada
   producto por separado: los errores individuales se compensan.
3. **Mientras más lejos, menos exacto.** El error crece con el horizonte.
4. **El método no reemplaza lo que ya sabes.** Si sabes que viene una promoción o una huelga, eso
   entra al pronóstico aunque los datos no lo muestren.

### Horizonte y uso

| Horizonte | Plazo típico | Para qué se usa |
|---|---|---|
| Corto | hasta un año, casi siempre menos de 3 meses | compras, programación, dotación semanal |
| Mediano | de 3 meses a 3 años | plan de ventas y de producción, presupuesto |
| Largo | 3 años o más | productos nuevos, inversión, ubicación de plantas |

Esta unidad trabaja sobre todo el corto y el mediano plazo: es lo que necesitan el inventario
(unidad 5) y la planeación agregada (unidad 6).

### Cualitativos y cuantitativos

- **Cualitativos:** juicio experto, método Delphi (rondas anónimas de expertos hasta converger),
  investigación de mercado, analogía con un producto parecido. Se usan cuando no hay datos: un
  producto nuevo, una tecnología nueva.
- **Cuantitativos:** modelos matemáticos sobre datos. Se dividen en **series de tiempo** (el futuro
  se proyecta solo desde el pasado de la misma variable) y **causales** (la demanda se explica con
  otra variable, como el precio o el tráfico frente al local).

### Los componentes de una serie de tiempo

| Componente | Qué es | Método que lo captura |
|---|---|---|
| Nivel | el valor «de base» alrededor del cual se mueve la demanda | promedio móvil, suavizamiento simple |
| Tendencia | crecimiento o caída sostenida | Holt, recta de tendencia |
| Estacionalidad | patrón que se repite cada año, mes o semana | índices estacionales, Winter |
| Ciclo | subidas y bajadas de varios años, ligadas a la economía | difícil; casi siempre con juicio |
| Aleatorio | el ruido que queda | ninguno: es lo que el método no debe perseguir |

**La regla para elegir:** grafica primero. Si la serie es plana, basta un promedio o un
suavizamiento simple. Si sube o baja, necesitas tendencia. Si se repite un patrón, necesitas
estacionalidad.

---

## 2. Medir el error

El error se mide antes de aprender los métodos porque es lo que los compara. Para cada período:

$$e_t = D_t - F_t$$

donde $D_t$ es la demanda real y $F_t$ el pronóstico que se hizo para ese período. Con esta
convención, **un error positivo significa que te quedaste corto** (la demanda fue mayor que lo
pronosticado).

Con $n$ períodos medidos:

$$\text{MAD} = \frac{\sum |e_t|}{n} \qquad \text{MSE} = \frac{\sum e_t^2}{n} \qquad \text{MAPE} = \frac{100}{n}\sum \frac{|e_t|}{D_t}\ \%$$

| Medida | Unidad | Sirve para |
|---|---|---|
| MAD (desviación absoluta media) | la de la demanda | leer el error típico en unidades; es la más usada |
| MSE (error cuadrático medio) | unidades al cuadrado | castigar los errores grandes; útil si un error grande es muy caro |
| MAPE (error porcentual absoluto medio) | % | comparar series de escala distinta (un producto de 50 y otro de 5.000) |

### Sesgo y señal de rastreo

MAD, MSE y MAPE miden **cuánto** te equivocas, pero no **hacia dónde**. Un pronóstico que siempre se
queda corto puede tener un MAD chico y estar mal. Para eso se suma el error con su signo:

$$\text{RSFE} = \sum e_t \qquad \text{TS} = \frac{\text{RSFE}}{\text{MAD}}$$

La **señal de rastreo** (TS, *tracking signal*) cuenta cuántos MAD de error se han acumulado hacia un
lado. Si el pronóstico no tiene sesgo, los errores se compensan y la TS oscila cerca de cero. La
regla habitual es revisar el método cuando la TS sale de **±4** (hay empresas que usan ±3 o ±6).
TS positiva: el pronóstico se queda corto; TS negativa: se pasa.

> **Compara en la misma ventana.** Un promedio móvil de 3 períodos no tiene pronóstico para los
> tres primeros; el suavizamiento sí. Si mides cada método en períodos distintos, la comparación no
> vale. Elige una ventana en que todos tengan pronóstico y mide ahí.

---

## 3. Promedios móviles

**Ingenuo.** El pronóstico del próximo período es la última demanda: $F_{t+1} = D_t$. Parece tonto,
pero es la vara mínima: un método que no le gana al ingenuo no sirve.

**Promedio móvil simple de $k$ períodos.** Promedia las últimas $k$ demandas:

$$F_{t+1} = \frac{D_t + D_{t-1} + \dots + D_{t-k+1}}{k}$$

Un $k$ grande suaviza más el ruido, pero reacciona más lento a un cambio real.

**Promedio móvil ponderado.** Da más peso a lo reciente. Los pesos suman 1:

$$F_{t+1} = w_1 D_t + w_2 D_{t-1} + \dots + w_k D_{t-k+1} \qquad \sum w_i = 1$$

Los pesos se eligen por experiencia o probando cuál da menor error.

**Su límite.** Un promedio siempre mira atrás. Si la demanda sube de forma sostenida, el promedio
queda **siempre por debajo**: los errores salen casi todos positivos y la señal de rastreo crece. El
ponderado reduce ese atraso, pero no lo elimina.

---

## 4. Suavizamiento exponencial simple

El nuevo pronóstico corrige el anterior en una fracción $\alpha$ del error que acaba de observar:

$$F_{t+1} = F_t + \alpha\,(D_t - F_t) = \alpha D_t + (1-\alpha) F_t \qquad 0 < \alpha < 1$$

Si se despliega la fórmula, el pronóstico es un promedio ponderado de **toda** la historia, con pesos
$\alpha$, $\alpha(1-\alpha)$, $\alpha(1-\alpha)^2$… que decrecen de forma exponencial. Por eso
necesita guardar un solo número (el último pronóstico) y no una tabla de datos.

- **$\alpha$ chico (0,1 a 0,3):** suaviza mucho; sirve si la demanda es estable.
- **$\alpha$ grande (0,5 o más):** sigue de cerca los cambios; sirve si la demanda cambia de nivel,
  pero también persigue el ruido.
- **Equivalencia útil:** un suavizamiento con $\alpha = 2/(k+1)$ responde parecido a un promedio
  móvil de $k$ períodos.
- **Hacia adelante es plano:** el pronóstico para dos, tres o más períodos es el mismo
  $F_{t+1}$. El método no sabe de tendencias.
- **Hay que inicializarlo.** El primer pronóstico $F_1$ se da (el valor de un experto, la primera
  demanda o el promedio de los primeros períodos). La elección cambia los primeros errores; por eso
  conviene medir después de unos períodos de «calentamiento».

---

## 5. Ejemplo resuelto · bidones de agua en Chillán

Una distribuidora de agua purificada de Chillán despacha bidones de 20 litros. Estas son las últimas
12 semanas:

| Semana | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bidones | 412 | 398 | 431 | 405 | 446 | 420 | 389 | 437 | 452 | 418 | 441 | 463 |

**Pregunta.** ¿Qué método conviene para la semana 13? Se comparan cinco: ingenuo, promedio móvil de
3 semanas (PM3), promedio móvil ponderado de 3 semanas con pesos 0,6 · 0,3 · 0,1 (PMP3, el 0,6 para
la semana más reciente) y suavizamiento exponencial (SE) con $\alpha = 0{,}2$ y $\alpha = 0{,}5$, ambos
con $F_1 = D_1 = 412$.

**Paso 1 · Un cálculo de cada método, a mano.**

- PM3, semana 4: $(412 + 398 + 431)/3 = 413{,}7$.
- PMP3, semana 4: $0{,}6 \cdot 431 + 0{,}3 \cdot 398 + 0{,}1 \cdot 412 = 258{,}6 + 119{,}4 + 41{,}2 = 419{,}2$.
- SE con $\alpha = 0{,}2$: $F_2 = 412 + 0{,}2\,(412 - 412) = 412$; $F_3 = 412 + 0{,}2\,(398 - 412) = 409{,}2$;
  $F_4 = 409{,}2 + 0{,}2\,(431 - 409{,}2) = 413{,}6$.

**Paso 2 · La tabla completa.** El PM3 y el PMP3 recién tienen pronóstico desde la semana 4, así que
**todos se miden en las semanas 4 a 12**.

| Semana | Demanda | Ingenuo | PM3 | PMP3 | SE α = 0,2 | SE α = 0,5 |
|---|---|---|---|---|---|---|
| 4 | 405 | 431,0 | 413,7 | 419,2 | 413,6 | 418,0 |
| 5 | 446 | 405,0 | 411,3 | 412,1 | 411,8 | 411,5 |
| 6 | 420 | 446,0 | 427,3 | 432,2 | 418,7 | 428,8 |
| 7 | 389 | 420,0 | 423,7 | 426,3 | 418,9 | 424,4 |
| 8 | 437 | 389,0 | 418,3 | 404,0 | 413,0 | 406,7 |
| 9 | 452 | 437,0 | 415,3 | 420,9 | 417,8 | 421,8 |
| 10 | 418 | 452,0 | 426,0 | 441,2 | 424,6 | 436,9 |
| 11 | 441 | 418,0 | 435,7 | 430,1 | 423,3 | 427,5 |
| 12 | 463 | 441,0 | 437,0 | 435,2 | 426,8 | 434,2 |
| **13** | ? | **463,0** | **440,7** | **451,9** | **434,1** | **448,6** |

**Paso 3 · Errores del PM3, como muestra.** $e_t = D_t - F_t$ en las semanas 4 a 12:
−8,7 · 34,7 · −7,3 · −34,7 · 18,7 · 36,7 · −8,0 · 5,3 · 26,0. La suma de los valores absolutos es 180,
así que $\text{MAD} = 180/9 = 20{,}0$. La suma con signo es $\text{RSFE} = 62{,}7$ y
$\text{TS} = 62{,}7/20{,}0 = 3{,}13$.

**Paso 4 · Comparar.**

| Método | MAD | MSE | MAPE | TS | Pronóstico semana 13 |
|---|---|---|---|---|---|
| Ingenuo | 29,6 | 965,8 | 6,9 % | 1,08 | 463,0 |
| PM3 | **20,0** | **554,9** | **4,6 %** | 3,13 | 440,7 |
| PMP3 | 24,8 | 708,6 | 5,8 % | 2,00 | 451,9 |
| SE α = 0,2 | 21,4 | 617,1 | 4,9 % | 4,79 | 434,1 |
| SE α = 0,5 | 23,7 | 653,8 | 5,5 % | 2,58 | 448,6 |

**Cómo se lee.**

- La demanda es casi plana con mucho ruido: gana el que más suaviza. El **PM3** tiene el menor
  error en las tres medidas; el ingenuo, que persigue cada salto, es el peor.
- El SE con $\alpha = 0{,}2$ queda segundo en MAD, pero su señal de rastreo es **4,79**: pasó el
  límite de ±4. Se está quedando corto de forma sistemática, porque las últimas semanas suben un
  poco y un $\alpha$ tan chico tarda en seguirlas. El MAD solo no lo habría mostrado.
- Recomendación para el jefe de despacho: pronosticar **unos 441 bidones** para la semana 13 con
  el PM3 y vigilar la señal de rastreo. Si sigue subiendo, la demanda tiene tendencia y hay que pasar
  a Holt (sección 6).

---

## 6. Con tendencia · Holt

Cuando la demanda sube o baja de forma sostenida, el suavizamiento simple siempre llega tarde. Holt
suaviza dos cosas por separado: el **nivel** $N_t$ y la **tendencia** $T_t$ (cuánto cambia el nivel
por período).

$$N_t = \alpha D_t + (1-\alpha)(N_{t-1} + T_{t-1})$$

$$T_t = \beta\,(N_t - N_{t-1}) + (1-\beta)\,T_{t-1}$$

$$F_{t+1} = N_t + T_t \qquad F_{t+k} = N_t + k\,T_t$$

- $\alpha$ suaviza el nivel y $\beta$ suaviza la tendencia; ambos entre 0 y 1.
- Para $k$ períodos hacia adelante, la tendencia se multiplica por $k$. Es la diferencia con el
  suavizamiento simple, que queda plano.
- **Inicialización de esta base:** $N_1 = D_1$ y $T_1 = D_2 - D_1$. Otras opciones válidas: la
  pendiente de los primeros meses, o un nivel y una tendencia que entregue el enunciado. Cambian los
  primeros errores (el caso integrador muestra cuánto).
- En las láminas del curso y en Heizer el nivel se llama $F_t$ y el pronóstico con tendencia
  $FIT_t = F_t + T_t$. Es la misma cuenta: su $F_t$ es el nivel calculado con datos hasta $t-1$.

### Ejemplo · socios de un gimnasio en Los Ángeles

Socios activos a fin de mes, con $\alpha = 0{,}4$ y $\beta = 0{,}3$. Inicio: $N_1 = 520$ y
$T_1 = 548 - 520 = 28$.

Mes 3, paso a paso: el pronóstico era $F_3 = N_2 + T_2 = 548 + 28 = 576$. Llegó $D_3 = 571$.

$$N_3 = 0{,}4 \cdot 571 + 0{,}6\,(548 + 28) = 228{,}4 + 345{,}6 = 574{,}0$$

$$T_3 = 0{,}3\,(574{,}0 - 548) + 0{,}7 \cdot 28 = 7{,}8 + 19{,}6 = 27{,}4$$

| Mes | Demanda | Pronóstico $F_t$ | Nivel $N_t$ | Tendencia $T_t$ |
|---|---|---|---|---|
| 1 | 520 | — | 520,0 | 28,0 |
| 2 | 548 | 548,0 | 548,0 | 28,0 |
| 3 | 571 | 576,0 | 574,0 | 27,4 |
| 4 | 590 | 601,4 | 596,8 | 26,0 |
| 5 | 622 | 622,9 | 622,5 | 25,9 |
| 6 | 641 | 648,5 | 645,5 | 25,0 |

Pronóstico: mes 7, $645{,}5 + 25{,}0 = 670{,}5$ socios; mes 8, $645{,}5 + 2 \cdot 25{,}0 = 695{,}5$. El
mes 2 tiene error cero por construcción (la tendencia inicial salió de ese mismo dato), así que el
error se mide desde el mes 3.

---

## 7. Recta de tendencia y regresión

### Mínimos cuadrados

Se ajusta $\hat y = a + b\,x$ minimizando la suma de los errores al cuadrado:

$$b = \frac{\sum xy - n\,\bar x\,\bar y}{\sum x^2 - n\,\bar x^2} \qquad a = \bar y - b\,\bar x$$

La calidad del ajuste se lee con el **coeficiente de determinación**:

$$R^2 = 1 - \frac{\text{SSE}}{\text{SST}} = 1 - \frac{\sum (y - \hat y)^2}{\sum (y - \bar y)^2}$$

$R^2$ es la fracción de la variación de $y$ que explica la recta (0 a 1). El coeficiente de
correlación $r$ es su raíz, con el signo de $b$.

### Dos usos

- **Proyección de tendencia:** $x$ es el período (1, 2, 3…). Sirve para el mediano plazo cuando la
  serie es casi recta. No captura estacionalidad y pierde validez si se proyecta muy lejos.
- **Regresión con datos de corte transversal:** $x$ es otra variable medida **en el mismo momento**
  en varias unidades (locales, comunas, clientes). Por ejemplo, las ventas de ocho sucursales contra
  el tráfico frente a cada una. Sirve para pronosticar una unidad nueva, como un local por abrir.

### Cuidados

- **Grafica antes.** La recta supone una relación lineal.
- **No extrapoles lejos.** Fuera del rango de $x$ observado, la recta es una suposición, no un dato.
- **Correlación no es causa.** Que dos variables se muevan juntas no dice cuál mueve a cuál.
- **En el modelo causal hay que pronosticar $x$.** Si $x$ es el precio del próximo mes, también hay
  que estimarlo.

---

## 8. Estacionalidad · índices y Winter

### Índices estacionales

Con $L$ estaciones por ciclo (4 trimestres, 12 meses) y varios ciclos de historia:

1. Promedia cada estación entre los años.
2. Calcula el promedio general (el promedio de esos promedios).
3. **Índice** de la estación $s$: $I_s = \dfrac{\text{promedio de la estación } s}{\text{promedio general}}$.
   Los $L$ índices suman $L$ (su promedio es 1).
4. Pronóstico de cada estación: $\dfrac{\text{demanda anual esperada}}{L} \times I_s$.

Un índice de 1,30 dice que esa estación vende un 30 % más que una estación promedio.
**Desestacionalizar** es dividir cada dato por su índice: lo que queda muestra la tendencia sin el
patrón. Si hay tendencia, se desestacionaliza, se ajusta una recta a los datos limpios, se proyecta y
al final se multiplica por el índice.

Variante que también aparece: dividir cada dato por el promedio de **su** año y luego promediar
esos cocientes por estación. Da índices parecidos pero no iguales; usa una sola en todo el ejercicio.

### Winter (tendencia y estacionalidad)

Agrega a Holt un índice $S_t$ que se actualiza cada vez que vuelve la misma estación:

$$N_t = \alpha \frac{D_t}{S_{t-L}} + (1-\alpha)(N_{t-1} + T_{t-1})$$

$$T_t = \beta\,(N_t - N_{t-1}) + (1-\beta)\,T_{t-1}$$

$$S_t = \gamma \frac{D_t}{N_t} + (1-\gamma)\,S_{t-L}$$

$$F_{t+p} = (N_t + p\,T_t)\; S_{t-L+p} \qquad (p \le L)$$

- El nivel se actualiza con la demanda **desestacionalizada** ($D_t / S_{t-L}$).
- $\gamma$ suaviza los índices; $L$ es el largo de la temporada.
- **Inicialización de las láminas del curso:** $N_1 = D_1$, $T_1 = 0$ y $S = 1$ en la temporada
  anterior al primer dato. Es simple, pero el primer año el método no sabe nada de la estacionalidad
  y se equivoca mucho. Una alternativa mejor, si hay al menos dos temporadas: tomar los índices
  iniciales del primer año y partir desde el segundo (ejercicio 4.10).

---

## 9. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Comparar el MAD de métodos medidos en períodos distintos | Fija una ventana común en que todos tengan pronóstico |
| Invertir el signo del error | $e_t = D_t - F_t$: positivo es quedarse corto; la señal de rastreo depende de ese signo |
| Elegir solo por MAD | Mira también la señal de rastreo: un MAD bajo puede esconder un sesgo |
| Usar promedio móvil o suavizamiento simple con tendencia clara | Se quedan atrás siempre; usa Holt o una recta de tendencia |
| En Holt, pronosticar $k$ períodos con $N_t + T_t$ | Es $N_t + k\,T_t$; la tendencia se multiplica |
| Medir el error en los períodos que se usaron para inicializar | Esos errores son cero o casi cero por construcción; mide después |
| Proyectar una regresión muy fuera del rango de $x$ | Avisa que es extrapolación; el $R^2$ no garantiza nada fuera del rango |
| Índices estacionales que no suman $L$ | Revisa el promedio general; si no suman $L$, el pronóstico anual no cuadra |

---

## 10. Práctica

Diez ejercicios: 4.1 a 4.4 básicos, 4.5 a 4.8 intermedios, 4.9 y 4.10 de desafío. Las pautas están
en la sección 11. Intenta cada uno antes de mirarla.

**4.1 · Ferretería de Talca (básico).** Cajas de tornillos vendidas por semana. Calcula el pronóstico
ingenuo, el PM3 y el PM4 para las semanas 5 a 9. Compara el MAD en las semanas 5 a 8 y elige.

| Semana | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Cajas | 64 | 71 | 58 | 67 | 75 | 62 | 69 | 73 |

**4.2 · Lavandería industrial de Puerto Montt (básico).** Cientos de kilos lavados por semana.
Calcula el PM3 y un promedio ponderado de 3 semanas con pesos 0,7 · 0,2 · 0,1 (el 0,7 para la más
reciente) para las semanas 4 a 9. Compara el MAD y la señal de rastreo en las semanas 4 a 8. ¿Qué
te dice la señal de rastreo de los dos?

| Semana | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Cientos de kg | 236 | 251 | 244 | 262 | 270 | 259 | 281 | 288 |

**4.3 · Farmacia de Coyhaique (básico).** Cajas de un analgésico vendidas por mes. El pronóstico del
mes 1 fue 150. Aplica suavizamiento exponencial con $\alpha = 0{,}1$ y con $\alpha = 0{,}4$, calcula el
pronóstico del mes 9 y el MAD de los meses 1 a 8. ¿Cuál eliges y por qué ninguno de los dos queda
del todo bien?

| Mes | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Cajas | 152 | 147 | 160 | 171 | 158 | 166 | 179 | 172 |

**4.4 · Panadería de Linares (básico).** Kilos de pan por día y el pronóstico que se usó.
(a) Calcula MAD, MSE, MAPE, RSFE y la señal de rastreo. (b) ¿El pronóstico tiene sesgo? ¿Hacia
dónde? (c) Si a la panadería le cuesta muchísimo quedarse sin pan un día puntual, ¿qué medida mira?
(d) Si quiere comparar este error con el de sus empanadas, que vende en docenas, ¿cuál usa?

| Día | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Demanda (kg) | 318 | 296 | 335 | 342 | 327 | 351 |
| Pronóstico (kg) | 305 | 310 | 312 | 320 | 330 | 333 |

**4.5 · Paneles solares en Rancagua (intermedio).** Kits instalados por mes. Aplica Holt con
$\alpha = 0{,}4$ y $\beta = 0{,}2$ ($N_1 = D_1$, $T_1 = D_2 - D_1$) y pronostica los meses 11, 12 y 13.
Compara su MAD con el de un suavizamiento simple con $\alpha = 0{,}4$ y $F_1 = D_1$, ambos en los
meses 3 a 10. ¿Qué muestra la señal de rastreo del suavizamiento simple?

| Mes | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Kits | 34 | 38 | 41 | 47 | 50 | 55 | 58 | 63 | 68 | 71 |

**4.6 · Internet rural en la Araucanía (intermedio).** Clientes con contrato a fin de año, en
cientos. Ajusta una recta de tendencia con $x = 1$ para 2018, calcula $R^2$ y pronostica 2026 y
2027. ¿Hasta qué año confiarías en esta recta?

| Año | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| Clientes (cientos) | 23 | 27 | 32 | 34 | 40 | 43 | 49 | 52 |

**4.7 · Lavado de autos, datos de corte transversal (intermedio).** Una cadena tiene ocho locales.
Para el mismo mes se midió el flujo vehicular diario frente a cada local (miles de vehículos) y los
autos lavados. Ajusta la recta, calcula $r$ y $R^2$ y pronostica dos locales nuevos: uno con flujo
5,0 y otro con flujo 11,0. ¿Confías igual en los dos pronósticos?

| Local | A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|
| Flujo (miles/día) | 4,2 | 6,8 | 3,5 | 8,1 | 5,6 | 7,3 | 2,9 | 6,1 |
| Autos lavados | 1.240 | 1.580 | 1.010 | 1.890 | 1.330 | 1.790 | 820 | 1.600 |

**4.8 · Parque nacional en Los Lagos (intermedio).** Visitas por trimestre, en cientos (T1 es el
verano). Calcula los índices estacionales con el método de la sección 8. Si para el año 4 se esperan
410 cientos de visitas en total, pronostica cada trimestre. Desestacionaliza el año 3: ¿qué ves?

| Trimestre | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| Año 1 | 142 | 61 | 38 | 97 |
| Año 2 | 155 | 66 | 41 | 104 |
| Año 3 | 168 | 70 | 45 | 111 |

**4.9 · Pastelería en línea de Concepción (desafío).** Pedidos por día. El día 8 partió una campaña
en redes sociales. (a) Aplica suavizamiento simple con $\alpha = 0{,}2$ y $F_1 = D_1$, y calcula la
señal de rastreo día a día desde el día 2 (con el MAD acumulado hasta ese día). ¿Qué día cruza el
límite de ±4? (b) Prueba $\alpha$ de 0,1 a 0,9 y busca el que minimiza el MAD de los días 2 a 14.
(c) ¿Usarías ese $\alpha$ para siempre?

| Día | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Pedidos | 52 | 49 | 55 | 50 | 53 | 51 | 48 | 66 | 69 | 64 | 70 | 67 | 72 | 68 |

**4.10 · Leña certificada en Aysén (desafío).** Metros cúbicos vendidos por trimestre (T2 y T3 son
otoño e invierno). (a) Aplica Winter con $L = 4$, $\alpha = 0{,}2$, $\beta = 0{,}2$, $\gamma = 0{,}7$ y la
inicialización de las láminas ($N_1 = D_1$, $T_1 = 0$, $S = 1$ en la temporada anterior). Pronostica
el año 4 y calcula el MAD de los trimestres 5 a 12. (b) Repite con otra inicialización: índices
iniciales = cada trimestre del año 1 dividido por el promedio del año 1, nivel inicial = ese
promedio, tendencia inicial 0, y corre desde el trimestre 5. (c) Compara y explica la diferencia.

| Trimestre | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| Año 1 | 410 | 820 | 960 | 380 |
| Año 2 | 450 | 890 | 1.030 | 420 |
| Año 3 | 480 | 950 | 1.110 | 450 |

---

## 11. Pautas

**4.1.**

| Semana | 5 | 6 | 7 | 8 | 9 | MAD (5 a 8) |
|---|---|---|---|---|---|---|
| Ingenuo | 67,0 | 75,0 | 62,0 | 69,0 | 73,0 | 8,0 |
| PM3 | 65,3 | 66,7 | 68,0 | 68,7 | 68,0 | **4,9** |
| PM4 | 65,0 | 67,8 | 65,5 | 68,2 | 69,8 | 6,0 |

Gana el **PM3**: pronostica 68,0 cajas para la semana 9. La serie sube y baja sin dirección; el
ingenuo persigue cada salto y el PM4 promedia datos que ya pesan poco.

**4.2.**

| Semana | 4 | 5 | 6 | 7 | 8 | 9 | MAD (4 a 8) | TS |
|---|---|---|---|---|---|---|---|---|
| PM3 | 243,7 | 252,3 | 258,7 | 263,7 | 270,0 | 276,0 | 14,3 | 5,00 |
| PMP3 | 244,6 | 257,3 | 265,8 | 261,5 | 275,5 | 283,7 | **13,8** | 4,01 |

El ponderado gana por poco y pronostica 283,7 cientos de kilos para la semana 9. Pero los dos tienen
señal de rastreo de 4 o más: se quedan cortos siempre, porque la serie tiene tendencia. El
ponderado reduce el atraso, no lo elimina. Con tendencia, el método es Holt.

**4.3.** Con $\alpha = 0{,}1$: $F_2 = 150 + 0{,}1\,(152 - 150) = 150{,}2$, y así sucesivamente.

| Mes | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | MAD | TS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| α = 0,1 | 150,0 | 150,2 | 149,9 | 150,9 | 152,9 | 153,4 | 154,7 | 157,1 | 158,6 | 11,5 | 7,45 |
| α = 0,4 | 150,0 | 150,8 | 149,3 | 153,6 | 160,5 | 159,5 | 162,1 | 168,9 | 170,1 | **7,9** | 6,39 |

Se elige $\alpha = 0{,}4$ (pronóstico del mes 9: 170,1 cajas), porque sigue mejor la subida. Ninguno
queda bien: los dos tienen la señal de rastreo muy sobre 4. La demanda crece y el suavizamiento
simple no tiene tendencia.

**4.4.** Errores: 13 · −14 · 23 · 22 · −3 · 18.

(a) $\text{MAD} = 93/6 = 15{,}5$ kg · $\text{MSE} = 285{,}2$ · MAPE = 4,7 % ·
$\text{RSFE} = 59$ · $\text{TS} = 59/15{,}5 = 3{,}81$.
(b) Sí: cuatro de seis errores son positivos y la señal de rastreo se acerca a +4. El pronóstico se
queda corto; conviene subirlo antes de que cruce el límite. (c) El **MSE**, que castiga más los
errores grandes. (d) El **MAPE**, porque está en porcentaje y no depende de la unidad.

**4.5.** Inicio: $N_1 = 34$, $T_1 = 4$.

| Mes | Demanda | $F_t$ Holt | $N_t$ | $T_t$ | $F_t$ SE |
|---|---|---|---|---|---|
| 1 | 34 | — | 34,00 | 4,00 | 34,00 |
| 2 | 38 | 38,00 | 38,00 | 4,00 | 34,00 |
| 3 | 41 | 42,00 | 41,60 | 3,92 | 35,60 |
| 4 | 47 | 45,52 | 46,11 | 4,04 | 37,76 |
| 5 | 50 | 50,15 | 50,09 | 4,03 | 41,46 |
| 6 | 55 | 54,12 | 54,47 | 4,10 | 44,87 |
| 7 | 58 | 58,57 | 58,34 | 4,05 | 48,92 |
| 8 | 63 | 62,39 | 62,64 | 4,10 | 52,55 |
| 9 | 68 | 66,74 | 67,24 | 4,20 | 56,73 |
| 10 | 71 | 71,44 | 71,27 | 4,17 | 61,24 |

Pronóstico Holt: mes 11 = 75,4 · mes 12 = 79,6 · mes 13 = 83,8 kits. MAD en los meses 3 a 10:
Holt **0,80** contra 9,23 del suavizamiento simple. La señal de rastreo del simple es 8,00: todos sus
errores son positivos, va siempre detrás de la demanda. Su pronóstico para el mes 11 (65,1) sería el
mismo para el 12 y el 13.

**4.6.** $n = 8$ · $\sum x = 36$ · $\sum y = 300$ · $\sum xy = 1.526$ · $\sum x^2 = 204$ · $\bar x = 4{,}5$ ·
$\bar y = 37{,}5$.

$$b = \frac{1.526 - 8 \cdot 4{,}5 \cdot 37{,}5}{204 - 8 \cdot 4{,}5^2} = \frac{176}{42} = 4{,}19 \qquad a = 37{,}5 - 4{,}19 \cdot 4{,}5 = 18{,}64$$

Recta: $\hat y = 18{,}64 + 4{,}19\,x$, con $R^2 = 0{,}994$. Pronóstico 2026 ($x = 9$): 56,4 cientos; 2027
($x = 10$): 60,5 cientos. El ajuste es muy bueno, pero un servicio rural tiene techo (las viviendas
de la zona). Uno o dos años hacia adelante es razonable; más allá, la recta supone que nunca se
satura.

**4.7.** $\bar x = 5{,}5625$ · $\bar y = 1.407{,}5$ · $\sum xy = 67.449$ · $\sum x^2 = 272{,}01$.
Recta: $\hat y = 313{,}3 + 196{,}7\,x$. Cada mil vehículos diarios más frente al local suman unos 197
lavados al mes. $r = 0{,}982$ y $R^2 = 0{,}963$: el flujo explica el 96 % de la diferencia entre
locales.

Local con flujo 5,0: **1.297** lavados. Local con flujo 11,0: **2.477** lavados. El primero está dentro
del rango observado (2,9 a 8,1) y es confiable. El segundo es extrapolación: ningún local actual
tiene ese flujo y nada asegura que la relación siga siendo lineal (con tanto tráfico, la capacidad del
local o la dificultad para entrar pueden frenar las ventas).

**4.8.** Promedios por trimestre: 155,00 · 65,67 · 41,33 · 104,00. Promedio general: 91,50.

| Trimestre | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| Índice | 1,694 | 0,718 | 0,452 | 1,137 |
| Pronóstico año 4 (cientos) | 173,6 | 73,6 | 46,3 | 116,5 |

Los índices suman 4. Base: $410/4 = 102{,}5$ por trimestre, multiplicada por cada índice. El año 3
desestacionalizado da 99,2 · 97,5 · 99,6 · 97,7: dentro del año es casi plano. Todo el sube y baja
era estacionalidad (un verano muy marcado). El crecimiento está entre un año y otro: el promedio
trimestral pasa de 84,5 en el año 1 a 91,5 en el año 2 y 98,5 en el año 3. Por eso los 410 cientos
del año 4 (102,5 por trimestre) son coherentes con la historia.

**4.9.** (a) Señal de rastreo con $\alpha = 0{,}2$:

| Día | Demanda | $F_t$ | $e_t$ | RSFE | MAD acumulado | TS |
|---|---|---|---|---|---|---|
| 2 | 49 | 52,00 | −3,00 | −3,00 | 3,00 | −1,00 |
| 3 | 55 | 51,40 | 3,60 | 0,60 | 3,30 | 0,18 |
| 4 | 50 | 52,12 | −2,12 | −1,52 | 2,91 | −0,52 |
| 5 | 53 | 51,70 | 1,30 | −0,22 | 2,51 | −0,09 |
| 6 | 51 | 51,96 | −0,96 | −1,17 | 2,20 | −0,53 |
| 7 | 48 | 51,77 | −3,77 | −4,94 | 2,46 | −2,01 |
| 8 | 66 | 51,01 | 14,99 | 10,05 | 4,25 | 2,37 |
| 9 | 69 | 54,01 | 14,99 | 25,04 | 5,59 | 4,48 |
| 10 | 64 | 57,01 | 6,99 | 32,03 | 5,75 | 5,57 |
| 11 | 70 | 58,41 | 11,59 | 43,63 | 6,33 | 6,89 |
| 12 | 67 | 60,73 | 6,27 | 49,90 | 6,33 | 7,89 |
| 13 | 72 | 61,98 | 10,02 | 59,92 | 6,63 | 9,03 |
| 14 | 68 | 63,98 | 4,02 | 63,94 | 6,43 | 9,94 |

La señal cruza +4 el **día 9** (TS = 4,48), al día siguiente del cambio, y no vuelve: el pronóstico se
queda corto todos los días siguientes.

(b) MAD de los días 2 a 14 según $\alpha$:

| α | 0,1 | 0,2 | 0,3 | 0,4 | 0,5 | 0,6 | 0,7 | 0,8 | 0,9 |
|---|---|---|---|---|---|---|---|---|---|
| MAD | 7,82 | 6,43 | 5,42 | 4,77 | **4,42** | 4,46 | 4,60 | 4,75 | 4,91 |

El mejor es $\alpha = 0{,}5$, con MAD 4,42; su pronóstico para el día 15 es 68,7 pedidos (con 0,2
habría sido 64,8).

(c) No. Ese $\alpha$ ganó porque en la ventana hubo un salto de nivel. Si la campaña termina y la
demanda vuelve a ser estable, un $\alpha$ de 0,5 perseguirá el ruido. Lo sensato: usar la señal de
rastreo como alarma, subir $\alpha$ (o reiniciar el pronóstico en el nuevo nivel) cuando cruza ±4, y
volver a un $\alpha$ bajo cuando la demanda se asienta.

**4.10.** (a) Winter con la inicialización de las láminas:

| Trimestre | Demanda | Nivel $N_t$ | Tendencia $T_t$ | Índice $S_t$ | Pronóstico $F_t$ |
|---|---|---|---|---|---|
| 1 | 410 | 410,0 | 0,00 | 1,000 | — |
| 2 | 820 | 492,0 | 16,40 | 1,467 | 410,0 |
| 3 | 960 | 598,7 | 34,46 | 1,422 | 508,4 |
| 4 | 380 | 582,5 | 24,34 | 0,757 | 633,2 |
| 5 | 450 | 575,5 | 18,06 | 0,847 | 606,9 |
| 6 | 890 | 596,2 | 18,59 | 1,485 | 870,6 |
| 7 | 1.030 | 636,7 | 22,96 | 1,559 | 874,5 |
| 8 | 420 | 638,7 | 18,78 | 0,687 | 499,1 |
| 9 | 480 | 639,3 | 15,14 | 0,780 | 557,1 |
| 10 | 950 | 651,5 | 14,55 | 1,466 | 971,8 |
| 11 | 1.110 | 675,2 | 16,39 | 1,618 | 1.038,5 |
| 12 | 450 | 684,3 | 14,91 | 0,667 | 475,3 |

Año 4: 545,2 · 1.047,0 · 1.179,8 · 495,8 m³. MAD de los trimestres 5 a 12: **75,8** m³ (en el año 1,
trimestres 2 a 4, el MAD llega a 371,6: el método todavía no sabe del invierno).

(b) Con índices iniciales del año 1 (promedio 642,5), el MAD de los trimestres 5 a 12 baja a
**26,6** m³ y el año 4 queda en 505,4 · 999,3 · 1.163,7 · 470,0 m³.

(c) Con $S = 1$ al inicio, el método confunde la subida de invierno del año 1 con tendencia: la
tendencia se infla hasta 34,46 en el trimestre 3 y el pronóstico del año 2 parte desordenado. Los
índices tardan una temporada entera en aprender. Si hay historia de al menos dos temporadas, conviene
inicializar los índices con el primer año. La inicialización no es un detalle: acá casi triplica el
error.

---

## 12. Caso integrador · Estampa Sur, pronóstico de la familia

> Este caso sigue a Estampa Sur por todo el ramo. Cada unidad parte de lo que calculó la anterior;
> acá empieza la cadena: el pronóstico de esta unidad alimenta el plan agregado (unidad 6) y la
> compra de prendas lisas (unidad 5).

Estampa Sur es un taller de serigrafía textil de la Región del Biobío. Fabrica una familia de
productos (poleras básicas, polerones, poleras con estampado doble, bolsas y gorros) y la planifica
en unidades totales. Esta es la demanda de los últimos 24 meses:

| Mes | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Unidades | 4.120 | 4.310 | 4.260 | 4.480 | 4.550 | 4.490 | 4.700 | 4.820 | 4.760 | 4.950 | 5.080 | 5.010 |

| Mes | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Unidades | 5.190 | 5.260 | 5.340 | 5.300 | 5.480 | 5.590 | 5.560 | 5.720 | 5.810 | 5.790 | 5.950 | 6.040 |

**Pregunta.** La jefa de planificación necesita la demanda de los meses 25 a 30 para armar el plan
agregado. ¿Qué método usa, cuánto se equivoca y qué cifras pasa?

**Desarrollo.**

1. **Mirar la serie.** Sube de forma sostenida, unas 83,5 unidades por mes en promedio
   ($(6.040 - 4.120)/23$), con ruido y sin un patrón estacional claro en dos años. Necesita
   tendencia: **Holt**, con $\alpha = 0{,}3$ y $\beta = 0{,}2$.
2. **Inicializar.** $N_1 = 4.120$ y $T_1 = 4.310 - 4.120 = 190$.
3. **Correr Holt** (primeros y últimos meses; $e_t = D_t - F_t$):

| Mes | Demanda | Pronóstico $F_t$ | Error $e_t$ | Nivel $N_t$ | Tendencia $T_t$ |
|---|---|---|---|---|---|
| 1 | 4.120 | — | — | 4.120,0 | 190,0 |
| 2 | 4.310 | 4.310,0 | 0,0 | 4.310,0 | 190,0 |
| 3 | 4.260 | 4.500,0 | −240,0 | 4.428,0 | 175,6 |
| 4 | 4.480 | 4.603,6 | −123,6 | 4.566,5 | 168,2 |
| 5 | 4.550 | 4.734,7 | −184,7 | 4.679,3 | 157,1 |
| 6 | 4.490 | 4.836,4 | −346,4 | 4.732,5 | 136,3 |
| … | … | … | … | … | … |
| 22 | 5.790 | 5.851,1 | −61,1 | 5.832,7 | 71,2 |
| 23 | 5.950 | 5.904,0 | 46,0 | 5.917,8 | 74,0 |
| 24 | 6.040 | 5.991,7 | 48,3 | 6.006,2 | 76,9 |

4. **Medir el error.**

| Ventana | MAD | Señal de rastreo |
|---|---|---|
| Meses 2 a 24 (toda la historia) | 104,0 | −18,13 |
| Meses 2 a 12 (primer año) | 161,7 | −11,00 |
| Meses 13 a 24 (segundo año) | 51,2 | −2,09 |

   El MAD de toda la historia es **104,0 unidades** (un MAPE de 2,2 %). Si se descuenta el mes 2,
   cuyo error es cero por construcción, sube a 108,7. Como contraste, un suavizamiento simple con
   $\alpha = 0{,}3$ tiene un MAD de 251,2 en los meses 3 a 24 y una señal de rastreo de 22,00: va
   siempre detrás.

5. **Pronosticar.** Con $N_{24} = 6.006{,}2$ y $T_{24} = 76{,}9$:
   $F_{24+k} = 6.006{,}2 + 76{,}9\,k$.

| Mes | 25 | 26 | 27 | 28 | 29 | 30 |
|---|---|---|---|---|---|---|
| Holt | 6.083 | 6.160 | 6.237 | 6.314 | 6.391 | 6.467 |
| Redondeado a la centena | **6.100** | **6.200** | **6.200** | **6.300** | **6.400** | **6.500** |

**Lectura.**

- La señal de rastreo de toda la historia (−18,13) parece una alarma, pero hay que mirar de dónde
  viene. En el primer año **todos** los errores son negativos (TS = −11,00 en 11 meses): el
  pronóstico se pasó siempre. La causa es la inicialización: la tendencia inicial de 190 más que
  duplica la pendiente real (83,5), y con $\beta = 0{,}2$ tarda casi un año en bajar.
- En el segundo año el método ya está asentado: MAD de 51,2 y señal de rastreo de −2,09, dentro de
  ±4. La tendencia final (76,9) es coherente con la pendiente real. **El pronóstico hacia adelante es
  confiable**; el error de toda la historia exagera lo que se puede esperar.
- Se redondea a la centena porque un error típico de unas 50 a 100 unidades hace que las decenas no
  signifiquen nada. Planificar con 6.237 en vez de 6.200 es fingir una precisión que no existe.
- Recomendación: usar Holt con estas cifras, volver a correrlo cada mes con la demanda real y
  vigilar la señal de rastreo. Si en una próxima versión se inicializa la tendencia con la pendiente
  de los primeros meses en vez de $D_2 - D_1$, el primer año deja de verse tan mal.

**Lo que pasa a las unidades 5 y 6.** El pronóstico redondeado (6.100, 6.200, 6.200, 6.300, 6.400 y
6.500 unidades) es la demanda del plan agregado de la unidad 6. La unidad 5 toma el promedio de los
dos primeros meses para estimar la demanda anual de poleras lisas:
12 × 0,40 × 6.150 = 29.520 poleras al año (las poleras básicas son el 40 % de la familia).

---

## 13. Para seguir

**En los libros del ramo.**

- Schroeder, *Administración de operaciones* (2.ª ed., 2004), capítulo 11 (el que fija el programa
  para pronósticos).
- Heizer y Render, *Principios de administración de operaciones* (5.ª ed., 2004), capítulo de
  pronósticos: promedios móviles, suavizamiento con tendencia, índices estacionales, regresión y
  señal de rastreo. Sus problemas del final del capítulo son la mejor práctica adicional.
- Chase, Jacobs y Aquilano, *Administración de operaciones* (12.ª ed., 2009), capítulo de
  pronósticos de la demanda.

**Abiertos y gratis.**

- Abbas y Goosheh, *Operations Management*, Fanshawe College (2025), en inglés; busca el capítulo de
  pronósticos (*forecasting*). Descarga en la colección abierta de Ontario:
  https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/2473

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame una serie con tendencia, hazme correr Holt
y corrígeme la señal de rastreo paso a paso».
