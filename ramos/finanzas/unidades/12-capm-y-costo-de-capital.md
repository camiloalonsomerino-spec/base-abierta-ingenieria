---
ramo: Finanzas
unidad: 12
titulo: CAPM, betas y costo de capital
version: 0.1 (15-10-2026)
requiere: [05-van-y-tir, 09-acciones, 11-portafolios]
alimenta: []
verificacion: verificacion/u12_capm.py
---

# Unidad 12 · CAPM, betas y costo de capital

**Qué vas a poder hacer.** Explicar por qué el mercado solo paga el riesgo sistemático y medirlo con
la beta; calcular el retorno exigido a un activo con la línea del mercado de valores (LMV); estimar una
beta por regresión con retornos mensuales y decir cuánto confiar en ella; leer el alfa; elegir la tasa
de descuento de un proyecto según **su** riesgo y no el de la empresa; desapalancar y reapalancar
betas, y cerrar con el costo promedio ponderado de capital (WACC).

**Lo que necesitas antes.** La cartera tangente, la LMC y la diferencia entre riesgo sistemático y no
sistemático (unidad 11). El modelo de Gordon (unidad 9) y el VAN (unidad 5), porque acá se revisan sus
tasas. De estadística, la regresión lineal simple.

**Tiempo.** Unas 5 horas: 2 de lectura con el ejemplo y 3 de práctica.

---

## 1. La idea

Hasta ahora la tasa de descuento venía dada: «descuente al 12 %». Esta unidad dice de dónde sale. La
respuesta tiene tres pasos:

1. En la unidad 11 todos los inversionistas terminan con la misma cartera riesgosa, la de mercado.
2. Entonces lo que importa de una acción no es cuánto se mueve sola, sino **cuánto riesgo agrega a la
   cartera de mercado**. Eso lo mide la beta.
3. El retorno que se le exige es la tasa libre de riesgo más un premio proporcional a esa beta. Ese
   retorno exigido es el costo de oportunidad del capital: la tasa con que se descuentan sus flujos.

**Notación.** $R_i$ retorno del activo $i$; $R_M$ retorno de la cartera de mercado (en la práctica, un
índice como el IPSA); $r_f$ tasa libre de riesgo; $E[R_M] - r_f$ premio por riesgo de mercado;
$\beta_i$ beta del activo; $k$ retorno exigido; $\alpha$ alfa.

---

## 2. La beta

### Definición

$$\beta_i = \frac{\operatorname{Cov}(R_i, R_M)}{\sigma_M^2} = \rho_{iM}\,\frac{\sigma_i}{\sigma_M}$$

La segunda forma muestra lo esencial: una acción muy volátil ($\sigma_i$ alto) puede tener beta baja si
se mueve poco con el mercado ($\rho_{iM}$ bajo). La volatilidad propia que no acompaña al mercado se
diversifica y no cuenta.

**Por qué esta medida.** La varianza de la cartera de mercado es la suma de las covarianzas de cada
acción con el mercado, ponderadas por su peso. La contribución de una acción al riesgo de la cartera es
su covarianza con ella; dividida por $\sigma_M^2$, queda la beta. Por eso el mercado tiene beta 1.

### Cómo se lee

| Beta | Qué dice | Ejemplo típico |
|---|---|---|
| $\beta > 1$ | amplifica: si el mercado sube 10 %, se espera que suba más | construcción, retail de bienes durables |
| $\beta = 1$ | se mueve como el mercado | un fondo que copia el índice |
| $0 < \beta < 1$ | amortigua | eléctricas, sanitarias, consumo básico |
| $\beta = 0$ | no se mueve con el mercado | el activo libre de riesgo |
| $\beta < 0$ | se mueve al revés | raro; algunos activos refugio en ciertas crisis |

**La beta de una cartera sí es el promedio ponderado:** $\beta_P = \sum_i w_i\beta_i$. A diferencia de
la desviación estándar, acá el promedio funciona directo, porque la covarianza es lineal en los pesos.

---

## 3. CAPM y la línea del mercado de valores

### La ecuación

$$k_i = E[R_i] = r_f + \beta_i\,\big(E[R_M] - r_f\big)$$

Dibujada en el plano beta (eje horizontal) contra retorno esperado, es una recta: la **línea del
mercado de valores (LMV)**, que parte en $r_f$ con beta 0 y pasa por el mercado con beta 1. Su
pendiente es el premio por riesgo de mercado: lo que se paga por cada unidad de beta.

### LMC contra LMV

| | LMC (unidad 11) | LMV (esta unidad) |
|---|---|---|
| Eje horizontal | desviación estándar $\sigma$ | beta $\beta$ |
| Qué activos están sobre ella | solo carteras eficientes ($r_f$ + mercado) | **todos** los activos, en equilibrio |
| Pendiente | razón de Sharpe del mercado | premio por riesgo de mercado |
| Para qué sirve | elegir cuánto riesgo tomar | fijar el retorno que se le exige a un activo |

Una acción suelta queda **bajo** la LMC (tiene riesgo propio que no paga), pero **sobre** la LMV.

### El alfa

Si un analista proyecta para una acción un retorno distinto del que pide el CAPM:

$$\alpha_i = E[R_i]_{\text{proyectado}} - \big[r_f + \beta_i\,(E[R_M] - r_f)\big]$$

- $\alpha > 0$: la acción queda sobre la LMV. Promete más de lo que su riesgo exige: está
  **subvalorada** y conviene comprarla. Al comprarla todos, su precio sube y su retorno esperado baja
  hasta la LMV.
- $\alpha < 0$: está **sobrevalorada**.

En equilibrio el alfa es cero. Un alfa distinto de cero dura lo que el mercado tarda en verlo.

---

## 4. Estimar la beta con datos

### La regresión del modelo de mercado

La beta verdadera no se observa. Se estima con la historia: retornos mensuales de la acción contra los
del índice,

$$R_{i,t} = a + b\,R_{M,t} + e_t$$

La pendiente $b$ es la beta estimada. Por mínimos cuadrados:

$$b = \frac{\sum_t (R_{M,t} - \bar R_M)(R_{i,t} - \bar R_i)}{\sum_t (R_{M,t} - \bar R_M)^2} \qquad a = \bar R_i - b\,\bar R_M$$

Es la misma fórmula de la sección 2: covarianza muestral sobre varianza muestral (los $n-1$ se
cancelan). En Excel, `=PENDIENTE(retornos de la acción; retornos del índice)`.

### El $R^2$ separa los dos riesgos

$$\sigma_i^2 = \underbrace{\beta_i^2\,\sigma_M^2}_{\text{sistemático}} + \underbrace{\sigma_e^2}_{\text{no sistemático}} \qquad R^2 = \frac{\beta_i^2\,\sigma_M^2}{\sigma_i^2}$$

Un $R^2$ de 0,25 significa que un cuarto de la varianza de la acción viene del mercado y tres cuartos
son riesgo propio, que se puede eliminar diversificando. Un $R^2$ bajo **no** significa que la beta
esté mal: significa que la acción tiene mucho riesgo propio.

### El intercepto y el alfa de Jensen

Si el CAPM se cumple, con retornos sin restar $r_f$:
$R_i = r_f + \beta(R_M - r_f) = r_f(1-\beta) + \beta R_M$. El intercepto que predice el CAPM es
$r_f(1-\beta)$, con $r_f$ en la misma frecuencia que los datos (mensual si los datos son mensuales).

$$\alpha_{\text{Jensen}} = a - r_f\,(1 - \beta)$$

Si es positivo, en ese período la acción rindió más de lo que su beta justificaba.

### Cuánto confiar · el error estándar

La beta estimada es una variable aleatoria. Su error estándar es

$$s_b = \frac{s_e}{\sqrt{\sum_t (R_{M,t} - \bar R_M)^2}} \qquad s_e = \sqrt{\frac{\sum_t e_t^2}{n-2}}$$

y el intervalo de 95 % es $b \pm t_{0{,}975;\,n-2}\, s_b$. Con pocos datos, $\sum (R_M - \bar R_M)^2$ es
chico y $t$ es grande: el intervalo es ancho. Por eso se usan, por ejemplo, 60 meses y no 12, y por
eso se prefiere la beta de una industria (una cartera de empresas parecidas) a la de una sola empresa:
en la cartera los errores de cada una se compensan.

**Dos ajustes habituales.**

- **Beta ajustada (Blume).** Las betas estimadas tienden a volver hacia 1 con el tiempo. Los servicios
  de información financiera publican $\beta_{\text{aj}} = \tfrac23\,b + \tfrac13$.
- **Elegir bien el índice y la frecuencia.** La beta de una acción chilena se mide contra un índice
  chileno amplio; medida contra un índice extranjero puede cambiar de valor y hasta de signo.

---

## 5. Del retorno exigido al costo de capital

### El precio de la acción

El retorno exigido es la tasa que va en el modelo de Gordon (unidad 9):
$P_0 = \dfrac{D_1}{k - g}$. Si la beta baja, baja $k$ y sube el precio.

### La tasa de un proyecto es la del proyecto

Cada proyecto se descuenta con el retorno que exige **su** riesgo, no el de la empresa que lo hace. La
beta de una empresa es el promedio de las betas de sus negocios. Si una empresa defensiva evalúa un
proyecto más riesgoso que ella con su propia tasa:

- lo descuenta a una tasa demasiado baja y le encuentra un VAN que no tiene;
- si repite eso, termina aceptando proyectos que destruyen valor y su beta sube.

Y al revés: un proyecto más seguro que la empresa, descontado con la tasa de la empresa, se rechaza
aunque sea bueno. La beta del proyecto se obtiene de **empresas comparables** que se dedican a ese
negocio.

### Desapalancar y reapalancar (Hamada)

La beta que se observa en bolsa es la del **patrimonio** y mezcla dos riesgos: el del negocio y el que
agrega la deuda. Con deuda sin riesgo e impuestos a la tasa $t$:

$$\beta_L = \beta_U\Big[1 + (1-t)\,\frac{D}{E}\Big] \qquad\Longleftrightarrow\qquad \beta_U = \frac{\beta_L}{1 + (1-t)\,D/E}$$

1. **Desapalancar** cada comparable con su propio $D/E$: queda la beta del negocio, $\beta_U$.
2. **Promediar** las $\beta_U$ de la industria.
3. **Reapalancar** con el $D/E$ de quien evalúa.
4. Aplicar el CAPM a esa $\beta_L$: es el retorno que exigen los accionistas.

### WACC

Cuando el proyecto se financia con deuda y patrimonio, la tasa que lo descuenta es el costo promedio
ponderado:

$$\text{WACC} = \frac{E}{V}\,k_e + \frac{D}{V}\,k_d\,(1 - t) \qquad V = E + D$$

- $E$ y $D$ van a **valor de mercado**: acciones por precio, bonos por su precio (no por su nominal).
- $k_e$ sale del CAPM; $k_d$ es la TIR de la deuda (unidad 7), no la tasa cupón.
- $(1-t)$ porque los intereses se descuentan de impuestos: cada peso de interés cuesta $1-t$.
- El WACC sirve para proyectos con **el mismo riesgo y el mismo financiamiento** que la empresa.
  Endeudarse más no lo baja para siempre: a más deuda, sube $\beta_L$, sube $k_e$ y, desde cierto
  punto, sube $k_d$.

---

## 6. ¿Funciona el CAPM? La evidencia

El CAPM es un modelo, no una ley. Lo que muestran los estudios empíricos, en términos generales:

- La relación entre beta y retorno promedio existe, pero es **más plana** de lo que predice el modelo:
  las acciones de beta baja rinden algo más de lo previsto y las de beta alta, algo menos.
- Aparecen **otros factores** que explican retornos y que la beta no capta, como el tamaño de la empresa
  y la razón entre valor libro y valor de mercado. De ahí salieron los modelos de varios factores.
- Aun así se sigue usando para el costo de capital: es simple, tiene una lógica clara (solo se paga lo
  que no se diversifica) y entrega un orden de magnitud razonable.

**La evidencia en Chile (lectura del programa).** Terceño, Barberà-Mariné y Laumann (2018) estiman
betas de acciones y de índices sectoriales del mercado chileno. Comparan la regresión de mínimos
cuadrados de la sección 4 con una **regresión borrosa**, que trata el retorno de cada período no como
un número exacto sino como un intervalo entre el mínimo y el máximo observados. Con eso ponen a prueba
dos predicciones de la teoría de carteras sobre la **estabilidad** de la beta: que sea más estable
cuanto más activos tenga la cartera (un índice sectorial frente a una acción sola) y cuanto más largo
sea el período de estimación. La idea que deja para esta unidad: la beta no es un dato que se lee, es
una estimación, y su calidad depende de cuántos activos y cuántos períodos la respaldan. En un mercado
chico y concentrado como el chileno, esa advertencia pesa más.

---

## 7. Ejemplo resuelto · Camila y Farmacias Lago Sur

Camila quiere comprar acciones de Farmacias Lago Sur (ficticia) y le pregunta a una amiga que trabaja
en una corredora cuánto debería exigirles. La amiga le pasa los retornos de los últimos seis meses de
la acción y del índice de la bolsa. La tasa libre de riesgo a un año es 4,35 % y el premio por riesgo de
mercado, 6,15 %. Un analista proyecta que la acción rendirá 13,7 % el próximo año.

**Paso 1 · Medias y desviaciones (en %).** La media del índice es 1,12 % y la de la acción, 1,39 %.

| Mes | Índice $R_M$ | Acción $R_i$ | $R_M - \bar R_M$ | $R_i - \bar R_i$ | Producto | Cuadrado |
|---|---|---|---|---|---|---|
| 1 | 2,96 | 4,07 | 1,84 | 2,68 | 0,000493 | 0,000339 |
| 2 | −1,87 | −2,93 | −2,99 | −4,32 | 0,001292 | 0,000894 |
| 3 | 2,43 | 1,26 | 1,31 | −0,13 | −0,000017 | 0,000172 |
| 4 | 4,61 | 5,74 | 3,49 | 4,35 | 0,001518 | 0,001218 |
| 5 | −2,58 | −1,98 | −3,70 | −3,37 | 0,001247 | 0,001369 |
| 6 | 1,17 | 2,18 | 0,05 | 0,79 | 0,000004 | 0,000000 |
| **Suma** | | | | | **0,004537** | **0,003991** |

Los productos y los cuadrados van en decimales ($0{,}0184 \times 0{,}0268 = 0{,}000493$).

**Paso 2 · Beta e intercepto.**

$$b = \frac{0{,}004537}{0{,}003991} = 1{,}1366 \qquad a = 1{,}39\,\% - 1{,}1366 \times 1{,}12\,\% = 0{,}12\,\% \text{ mensual}$$

El $R^2$ es 0,91: casi todo el movimiento de la acción en estos seis meses se explica por el índice.

**Paso 3 · Retorno exigido.**

$$k = 4{,}35\,\% + 1{,}1366 \times 6{,}15\,\% = 11{,}34\,\%$$

El mercado rinde en promedio $4{,}35\,\% + 6{,}15\,\% = 10{,}50\,\%$. La farmacia pide más porque
amplifica sus movimientos.

**Paso 4 · Alfa.** El analista proyecta 13,7 %; el CAPM exige 11,34 %. El alfa es de 2,36 puntos:
según esa proyección, la acción está sobre la LMV y estaría subvalorada.

**Paso 5 · Cuánto confiar.** El error estándar de la beta es 0,18. Con 4 grados de libertad
($t = 2{,}776$) el intervalo de 95 % va aproximadamente de 0,64 a 1,64: la acción puede ser defensiva o
muy agresiva. Seis meses no alcanzan.

**Cómo se lee.**

- La conclusión «está subvalorada» depende de dos números frágiles: la proyección del analista y una
  beta estimada con seis datos. Antes de comprar, Camila debería pedir la beta con 60 meses o la de la
  industria farmacéutica.
- El $R^2$ alto no arregla eso: dice que el ajuste es bueno en estos seis meses, no que la beta vaya a
  ser la misma el próximo año.

---

## 8. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Multiplicar la beta por $E[R_M]$ en vez de por el premio | $k = r_f + \beta\,(E[R_M] - r_f)$; si te dan el premio, no le restes $r_f$ otra vez |
| Exigir más retorno a la acción más volátil | Lo que se paga es la beta, no la $\sigma$ (ejercicio 12.3) |
| Usar la beta de la empresa para cualquier proyecto | Cada proyecto con la beta de su negocio (comparables) |
| Promediar betas apalancadas de comparables con deudas distintas | Desapalancar cada una con su $D/E$, promediar, reapalancar |
| Pesar el WACC con valores contables o nominales | Valor de mercado: precio de la acción y precio del bono |
| Usar la tasa cupón como costo de la deuda, u olvidar $(1-t)$ | $k_d$ es la TIR de la deuda; los intereses ahorran impuestos |
| Comparar el intercepto de la regresión con cero | El CAPM predice $r_f(1-\beta)$, en la frecuencia de los datos |
| Tratar una beta de 12 meses como exacta | Calcula su error estándar y su intervalo |

---

## 9. Práctica

Diez ejercicios: 12.1 a 12.4 básicos, 12.5 a 12.8 intermedios, 12.9 y 12.10 de desafío. Dos son
**comentes** (12.3 y 12.10): se responden Verdadero, Falso o Incierto con un argumento. Las pautas
están en la sección 10.

**12.1 · Tres betas (básico).** Con $r_f = 5{,}2\,\%$ y un premio por riesgo de mercado de 6,8 %,
calcula el retorno exigido a acciones con beta 0,55, 1,00 y 1,45. ¿Cuál es el retorno esperado del
mercado?

**12.2 · Beta desde los datos (básico).** (a) La covarianza de una acción con el mercado es 0,0156 y
la varianza del mercado, 0,0225. Calcula la beta. (b) Otra acción tiene $\sigma = 37\,\%$ y una
correlación de 0,62 con el mercado, cuya $\sigma$ es 19 %. Calcula su beta. (c) Calcula la beta de una
cartera con 35 % en la primera y 65 % en la segunda.

**12.3 · Comente (básico).** «La acción de una minera de litio es mucho más volátil que la de una
sanitaria. Por lo tanto, el CAPM le exige necesariamente un retorno mayor.»

**12.4 · ¿Comprar o vender? (básico).** La tasa libre de riesgo es 4 % y el mercado rinde en promedio
10,5 %. Un analista proyecta 12,9 % para la Acción X (beta 1,2) y 7,9 % para la Acción Y (beta 0,7).
Calcula el retorno exigido y el alfa de cada una y di cuál comprarías.

**12.5 · Beta por regresión (intermedio).** Ocho retornos mensuales, en %:

| Mes | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Índice | 2,17 | −3,46 | 4,08 | 0,83 | −1,24 | 2,97 | −2,41 | 1,06 |
| Acción | 1,84 | −1,63 | 2,71 | 1,47 | −1,12 | 0,58 | −0,39 | 1,34 |

Estima la beta y el intercepto, calcula el $R^2$ y di qué parte del riesgo de la acción es sistemática
y cuál se puede diversificar. Calcula el error estándar de la beta.

**12.6 · ¿Le ganó al mercado? (intermedio).** La regresión de los retornos mensuales de un fondo mutuo
contra el índice da un intercepto de 0,42 % mensual y una beta de 1,25. La tasa libre de riesgo
mensual del período fue 0,35 %. ¿Rindió el fondo más o menos que lo que predice el CAPM? ¿Cuánto al
mes y cuánto al año?

**12.7 · La tasa del proyecto (intermedio).** Una empresa eléctrica (beta 0,65) evalúa un centro de
datos: invertir $1.250 millones hoy y recibir $205 millones al año durante 10 años. Las empresas de
centros de datos tienen beta 1,35. Con $r_f = 4{,}7\,\%$ y un premio de 5,9 %, calcula el VAN con la
tasa de la empresa y con la del proyecto. ¿Qué decide cada una y cuál es la correcta?

**12.8 · Comparables (intermedio).** Una empresa que no transa en bolsa quiere su costo patrimonial.
Tasa de impuesto 27 %, $r_f = 5\,\%$, premio 6,5 %, y su estructura objetivo es $D/E = 0{,}65$.

| | Beta apalancada | $D/E$ |
|---|---|---|
| Comparable 1 | 1,08 | 0,32 |
| Comparable 2 | 1,47 | 0,85 |
| Comparable 3 | 1,21 | 0,58 |

Desapalanca, promedia, reapalanca y calcula $k_e$. ¿Cuánto exigirían los accionistas si la empresa no
tuviera deuda?

**12.9 · WACC y decisión (desafío).** Una empresa tiene 1.800.000 acciones a $3.650 cada una, con beta
1,24, y 35.000 bonos cero cupón de nominal $100.000 que vencen en 5 años y se transan a $72.400. Tasa de
impuesto 27 %, $r_f = 5\,\%$, premio 6,5 %. (a) Calcula los valores de mercado, el costo de la deuda,
el costo patrimonial y el WACC. (b) Un proyecto del mismo riesgo y el mismo financiamiento que la
empresa cuesta $1.400 millones y entrega $245 millones al año durante 12 años: ¿conviene? (c) ¿Qué VAN
obtendría alguien que lo descontara a $k_e$, y por qué eso es un error?

**12.10 · Comente (desafío).** «Si el CAPM se cumple, un activo con beta negativa tiene un retorno
esperado menor que la tasa libre de riesgo. Ningún inversionista racional lo compraría, porque el
depósito a plazo rinde más y no tiene riesgo.»

---

## 10. Pautas

**12.1.** $k = 5{,}2\,\% + \beta \times 6{,}8\,\%$: con beta 0,55, **8,94 %**; con beta 1,00,
**12,00 %**; con beta 1,45, **15,06 %**. El mercado rinde $5{,}2\,\% + 6{,}8\,\% = 12{,}00\,\%$, igual
que la acción de beta 1, como debe ser.

**12.2.** (a) $\beta = 0{,}0156/0{,}0225 = 0{,}6933$: amortigua. (b)
$\beta = 0{,}62 \times 0{,}37/0{,}19 = 1{,}2074$. (c) $\beta_P = 0{,}35 \times 0{,}6933 + 0{,}65 \times 1{,}2074 = 1{,}0275$.
La cartera se mueve casi como el mercado.

**12.3. Falso (o, siendo generoso, incierto).** El CAPM no paga la volatilidad total sino la beta,
$\beta = \rho\,\sigma_i/\sigma_M$. La minera puede tener una $\sigma$ enorme por razones propias (el
precio del litio, cambios regulatorios, un proyecto que falla), y ese riesgo se diversifica en una
cartera: el mercado no lo compensa porque cualquiera puede eliminarlo gratis. Si la correlación de la
minera con el mercado es baja, su beta puede ser parecida o incluso menor que la de la sanitaria, y
entonces se le exige un retorno parecido o menor. Solo si gran parte de su volatilidad acompaña al
mercado se le exigirá más. La afirmación confunde riesgo total con riesgo sistemático.

**12.4.** El premio es $10{,}5\,\% - 4\,\% = 6{,}5\,\%$. Acción X: exige $4\,\% + 1{,}2 \times 6{,}5\,\% = 11{,}80\,\%$;
alfa de 1,10 puntos: subvalorada, se compra. Acción Y: exige 8,55 %; alfa de −0,65 puntos:
sobrevalorada, se vende (o no se compra). Ojo: el alfa es tan confiable como la proyección del
analista.

**12.5.** Medias: 0,50 % el índice y 0,60 % la acción. $\sum(x-\bar x)(y-\bar y) = 0{,}002498$ y
$\sum(x-\bar x)^2 = 0{,}004931$, así que $b = 0{,}5067$ y $a = 0{,}347\,\%$ mensual. $R^2 = 0{,}78$:
el 78 % de la varianza es sistemática y el 22 % es riesgo propio que se elimina diversificando. Error
estándar de la beta: 0,11. Es una acción defensiva, y con ocho datos la estimación todavía es gruesa.

**12.6.** El intercepto que predice el CAPM es $r_f(1-\beta) = 0{,}35\,\% \times (1 - 1{,}25) = -0{,}0875\,\%$
mensual. El alfa de Jensen es $0{,}42\,\% - (-0{,}0875\,\%) = 0{,}5075\,\%$ mensual, que equivale a
$(1{,}005075)^{12} - 1 = 6{,}26\,\%$ al año. El fondo rindió más que lo que su beta justificaba. Error
frecuente: comparar 0,42 % con cero o con $r_f$; con beta mayor que 1 el CAPM predice un intercepto
negativo, así que el fondo lo hizo mejor de lo que parece a primera vista. Antes de pagarle comisión
al administrador, habría que ver si ese alfa es estadísticamente distinto de cero.

**12.7.** Tasa de la empresa: $4{,}7\,\% + 0{,}65 \times 5{,}9\,\% = 8{,}535\,\%$; factor de anualidad
6,5511; VAN $= -1{.}250 + 205 \times 6{,}5511 = 93{,}0$ millones. Tasa del proyecto:
$4{,}7\,\% + 1{,}35 \times 5{,}9\,\% = 12{,}665\,\%$; factor 5,4997; VAN $= -122{,}6$ millones. Con su
propia tasa la eléctrica lo aceptaría; con la del proyecto se rechaza, y esa es la correcta. El riesgo
del centro de datos no cambia porque lo haga una eléctrica: los inversionistas podrían comprar acciones
de empresas de centros de datos y les exigirían 12,665 %. Aceptarlo destruye 122,6 millones de valor y,
de paso, sube la beta de la eléctrica.

**12.8.** $\beta_U = \beta_L/[1 + 0{,}73\,D/E]$: 0,8755, 0,9071 y 0,8501. Promedio: 0,8776.
Reapalancada: $0{,}8776 \times (1 + 0{,}73 \times 0{,}65) = 1{,}2940$. Costo patrimonial:
$5\,\% + 1{,}2940 \times 6{,}5\,\% = 13{,}41\,\%$. Sin deuda: $5\,\% + 0{,}8776 \times 6{,}5\,\% = 10{,}70\,\%$.
La diferencia es el riesgo financiero: con deuda, los accionistas cobran después de los acreedores y sus
retornos se mueven más.

**12.9.** (a) Patrimonio: ${1{.}800{.}000} \times 3{.}650 = 6{.}570$ millones. Deuda:
${35{.}000} \times 72{.}400 = 2{.}534$ millones. Total: 9.104 millones; pesos 72,17 % y 27,83 %. Costo de la
deuda: $(100{.}000/72{.}400)^{1/5} - 1 = 6{,}67\,\%$, que después de impuestos es 4,87 %. Costo
patrimonial: $5\,\% + 1{,}24 \times 6{,}5\,\% = 13{,}06\,\%$.

$$\text{WACC} = 0{,}7217 \times 13{,}06\,\% + 0{,}2783 \times 6{,}67\,\% \times (1 - 0{,}27) = 10{,}78\,\%$$

(b) VAN al WACC: **207,4 millones**. Conviene. (c) A $k_e$ el VAN baja a 45,9 millones. Sigue siendo
positivo, pero el número está mal: los flujos del proyecto pagan a accionistas **y** acreedores, así
que se descuentan con el costo de toda la financiación, no solo con el de los accionistas. Descontar
a $k_e$ ignora que la deuda es más barata y que además ahorra impuestos, y, en un proyecto
con menos margen, haría rechazar uno bueno.

**12.10. Falso.** Con la tasa libre de riesgo del caso (4,80 %) y un premio de 6,1 %, un activo con
beta −0,3 exige $4{,}80\,\% - 0{,}3 \times 6{,}1\,\% = 2{,}97\,\%$, menos que el depósito. Y aun así se
compra con gusto. Lo que importa no es su riesgo ni su retorno solo, sino lo que hace en la cartera: sube
justo cuando el mercado cae, así que **reduce** el riesgo de la cartera más que un depósito (que solo no
agrega riesgo). Es como un seguro: se paga una prima (rendir menos que $r_f$) a cambio de que entregue
plata en los malos momentos. Que alguien acepte un retorno esperado menor que $r_f$ es exactamente lo
que predice el CAPM para un activo que cubre el riesgo sistemático. El error del comente es mirar el
activo solo y no su efecto en la cartera, que es lo que mide la beta.

---

## 11. Caso integrador · La beta de Textil Andes y la tasa del taller

> Este caso sigue a Valentina, dueña de Estampa Sur, por todo el ramo. En la unidad 9 valoró Textil
> Andes con la tasa de los analistas (11 %) y en la unidad 5 evaluó la segunda máquina del taller al
> 12 %. Ahora revisa las dos tasas con el CAPM. La tasa libre de riesgo es la spot a un año de la unidad
> 6 (4,80 %), la misma de la unidad 11. Todas las cifras salen de `verificacion/caso_valentina.py`.

### Parte 1 · La beta de Textil Andes con 12 meses

Los 12 retornos mensuales (en %), generados con una semilla fija:

| Mes | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Índice | 4,71 | 3,96 | 4,76 | 1,14 | −7,30 | 6,23 | 1,95 | 3,39 | −2,19 | −1,24 | 0,10 | −0,86 |
| Textil Andes | 4,86 | 3,10 | 6,14 | 6,58 | −3,94 | 5,89 | 0,71 | 5,48 | −3,02 | −4,22 | −0,97 | 0,72 |

Medias: 1,22 % el índice y 1,78 % la acción. La regresión da:

| Resultado | Valor |
|---|---|
| Beta $b$ | 0,8989 |
| Intercepto $a$ (en el script, `alfa`) | 0,68 % mensual |
| $R^2$ | 0,69 |
| Error estándar de la beta | 0,19 |
| Intervalo de 95 % ($t = 2{,}228$, 10 grados de libertad) | 0,47 a 1,32 |

**El intercepto no es todavía el alfa de Jensen.** La tasa libre de riesgo mensual es
$(1{,}048)^{1/12} - 1 = 0{,}391\,\%$, y el CAPM predice un intercepto de
$0{,}391\,\% \times (1 - 0{,}8989) = 0{,}040\,\%$. El alfa de Jensen es 0,64 % mensual. Pero el error
estándar del intercepto es 0,73 puntos: con 12 datos, ese alfa no se distingue de cero.

### Parte 2 · Retorno exigido y precio de la acción

$$k = 4{,}80\,\% + 0{,}8989 \times 6{,}1\,\% = 10{,}28\,\%$$

Más bajo que el 11 % de los analistas de la unidad 9. Con el mismo dividendo y el mismo crecimiento:

$$P_0 = \frac{86{,}40}{0{,}1028 - 0{,}032} = 1{.}219{,}80 \quad\text{contra}\quad 1{.}107{,}69 \text{ con el } 11\,\%$$

**¿Cuánto creerle a esa beta?** Los retornos del script se generaron con una beta verdadera de 1,30. La
regresión de 12 meses entregó 0,8989, y 1,30 cae dentro de su intervalo. Con la beta verdadera el
retorno exigido sería 12,73 % y el precio 906,63. Con la beta ajustada de Blume
($\tfrac23 \times 0{,}8989 + \tfrac13 = 0{,}9326$) sería 10,49 % y 1.185,40. **La misma acción vale entre
906,63 y 1.219,80 según qué beta se crea.** Con 12 datos la beta es ruidosa; la conclusión «la acción
vale más de lo que decían los analistas» no resiste ese ruido.

> **Nota sobre el premio.** El caso usa un premio por riesgo de mercado de 6,1 %, lo que pone el retorno
> esperado del mercado en 10,90 %. El Fondo IPSA de la unidad 11 tenía 9,8 %. No es una contradicción
> del modelo: son dos estimaciones distintas del mismo número (una del fondo, otra de largo plazo de
> los analistas). En la práctica el premio por riesgo es uno de los datos más discutidos del CAPM.

### Parte 3 · La tasa del proyecto del taller

La segunda máquina no es una acción de Textil Andes: es un proyecto de serigrafía. Su beta sale de
talleres comparables, 1,15:

$$k_{\text{proyecto}} = 4{,}80\,\% + 1{,}15 \times 6{,}1\,\% = 11{,}81\,\%$$

Con los flujos de la unidad 5 (−$5.550.000 hoy; $3.900.000, $4.200.000, −$4.300.000, $4.450.000 y
$6.250.000 en los años 1 a 5):

| Tasa | VAN |
|---|---|
| 12 % (la de la unidad 5) | $4.594.175 |
| 11,81 % (CAPM con la beta del proyecto) | $4.644.052 |

**Lectura.** La tasa casi no cambia y la decisión tampoco: la máquina conviene con holgura. Lo
importante es el método. Valentina no debe usar la beta de Textil Andes (0,8989) para su taller, aunque
sea «del rubro textil»: una fábrica grande que cotiza en bolsa y un taller de serigrafía no tienen el
mismo riesgo de negocio. Y si el taller tomara deuda para pagar el saldo de la máquina, la tasa
correcta sería el WACC, con la beta del proyecto reapalancada a la deuda del taller.

**Con esto se cierra el caso.** Valentina partió con $3.460.000 ahorrados (unidad 1) y termina sabiendo
de dónde sale cada tasa que usó: la libre de riesgo de la curva spot, el premio por riesgo del mercado
y la beta de cada inversión.

---

## 12. Para seguir

**En los libros del ramo.**

- Ross, Westerfield y Jaffe, *Finanzas corporativas* (9.ª ed., 2012): el programa fija los capítulos
  10 y 11 y, para CAPM y cálculo de betas, el capítulo 13.
- Brealey, Myers y Allen, *Principios de finanzas corporativas* (9.ª ed., 2010): el programa fija los
  capítulos 8, 9 y 10.
- Terceño, A., Barberà-Mariné, M. G. y Laumann, Y. (2018), «Análisis de los coeficientes beta:
  evidencia en el mercado de activos chileno», *Economía Chilena*, 21(3), 76-93, Banco Central de Chile.
  Lectura obligatoria del programa. Ficha y enlace al texto completo:
  https://ideas.repec.org/a/chb/bcchec/v21y2018i3p076-093.html

**Abierto y gratis.**

- Dahlquist y Knight, *Principles of Finance*, OpenStax (2022), en inglés. Sección 15.3 (CAPM, con una
  beta estimada por regresión de retornos mensuales) y capítulo 17, secciones 17.2 (costo de la deuda y
  del patrimonio) y 17.3 (WACC): https://openstax.org/details/books/principles-finance

**Con el tutor.** Pega `tutor/contexto.md` al inicio de la conversación y pídele, por ejemplo: «Dame
tres comparables con su beta y su deuda, hazme desapalancar y reapalancar, y corrígeme paso a paso».
