# Finanzas

Cuánto vale hoy una plata que llega mañana, cómo se valoran un bono y una acción, y cuánto retorno
hay que pedirle a una inversión según su riesgo.

**Nivel:** tercer año de Ingeniería Civil Industrial. **Antes:** cálculo, probabilidad y estadística
básica.

## Unidades

| N.º | Unidad | Estado (15-10-2026) |
|---|---|---|
| 1 | [Valor del dinero en el tiempo](unidades/01-valor-del-dinero.md) | 0.1 · [PDF](pdf/01-valor-del-dinero.pdf) |
| 2 | [Tasas de interés](unidades/02-tasas-de-interes.md) | 0.1 · [PDF](pdf/02-tasas-de-interes.pdf) |
| 3 | [Anualidades, perpetuidades y gradientes](unidades/03-anualidades.md) | 0.1 · [PDF](pdf/03-anualidades.pdf) |
| 4 | [Créditos y tablas de amortización](unidades/04-creditos-y-amortizacion.md) | 0.1 · [PDF](pdf/04-creditos-y-amortizacion.pdf) |
| 5 | [VAN, TIR y criterios de inversión](unidades/05-van-y-tir.md) | 0.1 · [PDF](pdf/05-van-y-tir.pdf) |
| 6 | [Estructura de tasas](unidades/06-estructura-de-tasas.md) | 0.1 · [PDF](pdf/06-estructura-de-tasas.pdf) |
| 7 | [Bonos](unidades/07-bonos.md) | 0.1 · [PDF](pdf/07-bonos.pdf) |
| 8 | [Duración, convexidad e inmunización](unidades/08-duracion-e-inmunizacion.md) | 0.1 · [PDF](pdf/08-duracion-e-inmunizacion.pdf) |
| 9 | [Acciones](unidades/09-acciones.md) | 0.1 · [PDF](pdf/09-acciones.pdf) |
| 10 | [Riesgo, utilidad y aversión al riesgo](unidades/10-riesgo-y-utilidad.md) | 0.1 · [PDF](pdf/10-riesgo-y-utilidad.pdf) |
| 11 | [Portafolios](unidades/11-portafolios.md) | 0.1 · [PDF](pdf/11-portafolios.pdf) |
| 12 | [CAPM, betas y costo de capital](unidades/12-capm-y-costo-de-capital.md) | 0.1 · [PDF](pdf/12-capm-y-costo-de-capital.pdf) |

Cada unidad trae la teoría justa, un ejemplo resuelto con un caso cotidiano, diez ejercicios con
pauta (dos de ellos «comentes»: afirmaciones que se responden con un argumento), errores típicos,
los libros donde seguir y una pieza del caso integrador.

## El caso integrador · Valentina

Valentina es la dueña de Estampa Sur, el taller de serigrafía del caso de Gestión de Operaciones.
Todo es ficticio: personas, empresas, bonos y tasas.

| Unidad | Lo que calcula | Pasa a la siguiente |
|---|---|---|
| 1 Valor del dinero | cuánto valen en 3 años sus $3.460.000 ahorrados | valor futuro del ahorro |
| 2 Tasas | qué banco paga más (nominal contra efectiva) y cuánto en términos reales | elige el banco A: 0,55 % mensual |
| 3 Anualidades | cuánto depositar al mes para juntar el pie del departamento | meta y depósito |
| 4 Créditos | cuota, tabla de amortización y CAE del hipotecario | — |
| 5 VAN y TIR | si conviene la segunda máquina del taller, con pie y saldo a 3 años | saldo de $8.750.000 a 3 años |
| 6 Estructura de tasas | tasas spot y forward desde bonos cero cupón | curva spot |
| 7 Bonos | precio y TIR de un bono de 4 años con esa curva | bono para inmunizar |
| 8 Duración | cómo asegurar hoy el pago del saldo de la máquina | — |
| 9 Acciones | precio de Textil Andes con crecimiento constante | precio con la tasa de los analistas |
| 10 Utilidad | si le conviene una inversión riesgosa o el depósito | — |
| 11 Portafolios | cartera de Textil Andes y un fondo, con activo libre de riesgo | tasa libre de riesgo |
| 12 CAPM | beta de Textil Andes, su retorno exigido y el del proyecto del taller | revisa las tasas de 5 y 9 |

La fuente única de las cifras es `verificacion/caso_valentina.py`.

## Bibliografía

Obligatoria (la que fija el programa del ramo):

- Ross, Westerfield y Jaffe, *Finanzas corporativas*, McGraw-Hill, 9.ª ed., 2012.
- Fabozzi, *The Handbook of Fixed Income Securities*, McGraw-Hill.
- Kelleher y MacCormack, «Internal rate of return: A cautionary tale», *The McKinsey Quarterly*,
  2004.
- Lazzatti, *Técnicas de inmunización basadas en la duración*, 2001.

Complementaria: Brealey, Myers y Allen, *Principios de finanzas corporativas*, 9.ª ed., 2010;
Bodie, Kane y Marcus, *Investments*.

## Cómo se usa

- **Estudiar:** lee la unidad en PDF (`pdf/`) o en Markdown (`unidades/`).
- **Practicar con IA:** pega `tutor/contexto.md` al inicio de la conversación.
- **Comprobar una cifra:** cada unidad tiene su script en `verificacion/`; con `--revisar` busca cada
  resultado en el texto.
