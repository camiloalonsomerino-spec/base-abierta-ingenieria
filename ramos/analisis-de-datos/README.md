# Análisis de Datos

Cómo decidir con datos cuando hay ruido: comparar grupos, probar si un dato sigue una distribución,
separar el efecto de varios factores, modelar una respuesta que es un sí o no o un conteo, y
actualizar una creencia con evidencia nueva.

**Nivel:** tercer año de Ingeniería Civil Industrial. **Antes:** Probabilidades y Estadística.
**Software:** Python con `scipy`, `pandas` y `statsmodels`. Cada unidad trae su cuaderno en
`notebooks/` y los datos en `datos/`.

## Unidades

| N.º | Unidad | Estado (15-10-2026) |
|---|---|---|
| 1 | [Prueba de hipótesis: valor p, región de rechazo y errores](unidades/01-prueba-de-hipotesis.md) | 0.1 · [PDF](pdf/01-prueba-de-hipotesis.pdf) |
| 2 | [Comparar dos medias](unidades/02-comparar-dos-medias.md) | 0.1 · [PDF](pdf/02-comparar-dos-medias.pdf) |
| 3 | [Comparar varianzas y proporciones](unidades/03-varianzas-y-proporciones.md) | 0.1 · [PDF](pdf/03-varianzas-y-proporciones.pdf) |
| 4 | [Tablas de contingencia y chi-cuadrado](unidades/04-chi-cuadrado.md) | 0.1 · [PDF](pdf/04-chi-cuadrado.pdf) |
| 5 | [Bondad de ajuste y normalidad](unidades/05-bondad-de-ajuste.md) | 0.1 · [PDF](pdf/05-bondad-de-ajuste.pdf) |
| 6 | [Correlación](unidades/06-correlacion.md) | 0.1 · [PDF](pdf/06-correlacion.pdf) |
| 7 | [Modelo lineal y ANOVA de un factor](unidades/07-anova-un-factor.md) | 0.1 · [PDF](pdf/07-anova-un-factor.pdf) |
| 8 | [Comparaciones múltiples](unidades/08-comparaciones-multiples.md) | 0.1 · [PDF](pdf/08-comparaciones-multiples.pdf) |
| 9 | [ANOVA de varios factores, interacciones y supuestos](unidades/09-anova-varios-factores.md) | 0.1 · [PDF](pdf/09-anova-varios-factores.pdf) |
| 10 | [Regresión lineal múltiple y diagnóstico](unidades/10-regresion-multiple.md) | 0.1 · [PDF](pdf/10-regresion-multiple.pdf) |
| 11 | [Modelos lineales generalizados: logística y Poisson](unidades/11-glm-logistica-y-poisson.md) | 0.1 · [PDF](pdf/11-glm-logistica-y-poisson.pdf) |
| 12 | [Inferencia bayesiana](unidades/12-inferencia-bayesiana.md) | 0.1 · [PDF](pdf/12-inferencia-bayesiana.pdf) |

## El caso integrador · Estampa Sur mira sus datos

El mismo taller ficticio de los otros ramos. Sus datos son **simulados** con semilla fija por
`verificacion/caso_estampa_sur_datos.py`, que los deja en `datos/`: no describen ningún taller real.

| Unidad | La pregunta |
|---|---|
| 1 y 2 | ¿Una máquina de estampado desplaza más el registro que la otra? |
| 3 | ¿Varían igual? ¿Un proveedor entrega más prendas defectuosas? |
| 4 | ¿El tipo de reclamo depende del canal de venta? |
| 5 | ¿Las llegadas de pedidos web siguen una exponencial? |
| 6 | ¿Cuánto se mueven juntas el precio y las unidades vendidas? |
| 7 a 9 | ¿Cuánto influyen la tinta y la temperatura en el tiempo de secado? |
| 10 | ¿Cuánto vende el taller según su precio y su publicidad? |
| 11 | ¿Qué sube la probabilidad de un defecto? ¿La campaña web trae más reclamos? |
| 12 | ¿Qué tan probable es que la tasa de defectos de un proveedor supere el 6 %? |

## Bibliografía

Obligatoria (la que fija el programa del ramo): Walpole, Myers, Myers y Ye, *Probability & Statistics
for Engineers & Scientists*, Pearson, 2017; Casella y Berger, *Statistical Inference*, Cengage, 2021;
Montgomery, *Design and Analysis of Experiments*, Wiley, 2005; Kutner, *Applied Linear Statistical
Models*, McGraw-Hill, 2004; Gelman y otros, *Bayesian Data Analysis*, 2013.

## Cómo se usa

- **Estudiar:** lee la unidad en PDF (`pdf/`) o en Markdown (`unidades/`).
- **Practicar:** abre el cuaderno de la unidad en `notebooks/` con los datos de `datos/`.
- **Practicar con IA:** pega `tutor/contexto.md` al inicio de la conversación.
- **Comprobar una cifra:** cada unidad tiene su script en `verificacion/`; con `--revisar` busca cada
  resultado en el texto.
