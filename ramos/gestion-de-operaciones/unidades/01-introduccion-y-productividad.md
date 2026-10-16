---
ramo: Gestión de Operaciones
unidad: 1
titulo: Introducción y productividad
version: 0.1 (15-10-2026)
requiere: []
alimenta: [02-estrategia-de-operaciones, 03-proceso-y-capacidad, 06-planeacion-agregada]
verificacion: verificacion/u01_productividad.py
---

# Unidad 1 · Introducción y productividad

**Qué vas a poder hacer.** Describir una operación como un sistema que transforma entradas en
salidas; distinguir eficiencia de eficacia y un bien de un servicio; medir la productividad de una
empresa con indicadores parciales, multifactoriales, físicos y económicos (con el valor agregado);
calcular cuánta gente hace falta cuando cambia la jornada; leer las curvas de producto y de costo de
corto plazo para elegir una planta, y comparar sitios por costo total.

**Lo que necesitas antes.** Álgebra y porcentajes. Nada del ramo: esta es la puerta de entrada.

**Tiempo.** Unas 3,5 horas: 1,5 de lectura con el ejemplo y 2 de práctica.

---

## 1. La idea

Una **operación** toma entradas (materiales, información, clientes con una necesidad), usa
recursos (personas, máquinas, edificios, energía) y las transforma en salidas que alguien valora. La
**gestión de operaciones** planifica, organiza, dirige y controla esa transformación para que cree
valor. No es lo mismo que la investigación de operaciones: esa es una caja de herramientas
cuantitativas (programación lineal, colas, simulación) que la gestión usa cuando le sirve.

| Sistema | Entradas | Recursos | Transformación | Salida |
|---|---|---|---|---|
| Taller de serigrafía | prendas lisas, tintas, diseños del cliente | pulpos de estampado, planchas, personas | estampar, secar, planchar, doblar | prendas estampadas a tiempo |
| Centro de salud familiar | pacientes con un síntoma | médicos, box, fichas, insumos | evaluar, diagnosticar, tratar | paciente atendido y derivado |
| Empresa de buses | pasajeros en el terminal | buses, conductores, rutas | trasladar | pasajero en destino, seguro y a la hora |

### Eficiencia y eficacia

- **Eficacia:** lograr el efecto buscado (el pedido llegó, el paciente sanó).
- **Eficiencia:** lograrlo con la menor cantidad de recursos.

Suelen tirar para lados distintos. Un banco con dos cajeros es eficiente (cada cajero trabaja todo
el día) pero poco eficaz si la fila da vuelta a la cuadra; con ocho cajeros la fila desaparece, pero
la mitad del tiempo están ociosos. La pregunta de operaciones es dónde ponerse en esa línea.

### Bienes y servicios

| | Bien | Servicio |
|---|---|---|
| Qué se entrega | algo físico | una acción o una experiencia |
| Inventario | se puede fabricar antes y guardar | no se guarda: se produce y se consume a la vez |
| Cliente | no necesita estar presente | suele estar dentro del proceso |
| Estandarizar | más fácil | más difícil, cada cliente es distinto |
| Ubicación | puede estar lejos del cliente | cerca del cliente pesa mucho |

La frontera es borrosa: un fabricante de calefactores vende también la instalación y la garantía, y
una cadena de comida rápida es en parte una fábrica. Por eso se habla de un continuo entre bienes
puros y servicios puros.

### Las decisiones de operaciones

Las decisiones que toma esta función (y que el ramo recorre unidad por unidad) son: diseño de bienes
y servicios, calidad, proceso y capacidad, localización, distribución de las instalaciones, personas y
diseño del trabajo, cadena de suministro, inventario, programación y mantenimiento. Todas se juzgan
contra cuatro objetivos (**costo, calidad, entrega y flexibilidad**), que son el tema de la unidad 2.

Las tendencias que cambian estas decisiones: operación global, justo a tiempo, coordinación de la
cadena de suministro, desarrollo rápido de productos, personalización masiva, más autonomía para el
trabajador, producción cuidadosa con el ambiente y automatización con robótica e inteligencia
artificial.

---

## 2. Productividad

La productividad es la razón entre lo que sale y lo que entra:

$$P = \frac{\text{salidas}}{\text{entradas}}$$

Sube si se produce más con lo mismo o lo mismo con menos. Es la medida más directa del trabajo de
operaciones: a nivel de empresa explica la rentabilidad y a nivel de país explica el nivel de vida.

### Parcial y multifactorial

- **Parcial:** una sola entrada. La más usada es la de mano de obra, con las **horas-hombre**
  ($HH$ = personas × horas trabajadas por persona):

$$P_{MO} = \frac{Q}{HH}$$

- **Multifactorial:** todas las entradas, llevadas a pesos para poder sumarlas. La salida puede ir en
  unidades o en pesos de venta:

$$P_{MF} = \frac{Q \text{ (o ventas en pesos)}}{C_{MO} + C_{\text{materiales}} + C_{\text{energía}} + C_{\text{capital}} + C_{\text{otros}}}$$

Si la salida va en unidades, el resultado sale en unidades por peso, un número muy chico: conviene
expresarlo por cada 1.000 CLP. Si va en pesos de venta, queda en «pesos vendidos por peso gastado».

> **Por qué hacen falta las dos.** Una máquina nueva reemplaza personas: la productividad de la mano
> de obra sube casi siempre, pero la multifactorial puede bajar si la máquina cuesta más de lo que
> ahorra. Mirar solo la parcial premia cualquier sustitución de trabajo por capital.

### Física, económica y valor agregado

El **valor agregado** es lo que la empresa le suma a lo que compra afuera. Se calcula de dos formas
que tienen que dar lo mismo:

$$VA = \underbrace{V - I}_{\text{por sustracción}} = \underbrace{W + U}_{\text{por adición}} \qquad U = V - W - I$$

con $V$ ventas, $I$ insumos comprados a terceros (materiales, energía, arriendos, servicios), $W$
remuneraciones y $U$ utilidad. En esta base, todo costo que se le paga a un tercero (incluidos el
arriendo y la luz) entra en $I$; así las dos formas siempre cuadran.

| Indicador | Fórmula | Unidad típica |
|---|---|---|
| Productividad física | $Q / HH$ | unidades por HH |
| Productividad económica | $VA / HH$ | pesos por HH |
| Parcial del trabajo | $VA / \text{personas}$ | pesos por persona al mes |
| Parcial del capital | $VA / \text{activo fijo}$ | pesos por peso invertido |

### Variación porcentual

$$\Delta\% = \frac{P_{\text{final}} - P_{\text{inicial}}}{P_{\text{inicial}}}$$

Siempre se divide por el valor **inicial**. Un alza de 15 a 18 es de 20 %; una baja de 18 a 15 es de
16,7 %, no de 20 %.

### Dotación para sostener una productividad

Si la jornada cambia (en Chile, la Ley 21.561 baja la jornada a 40 horas semanales en forma gradual) y
se quiere producir $Q_1$ con la misma productividad $P_0$:

$$N_1 = \left\lceil \frac{Q_1}{P_0 \cdot h_1} \right\rceil$$

con $h_1$ las horas por persona en el período. Se redondea **hacia arriba**: con 41,3 personas no se
cumple, con 42 sí.

### Calidad y medición

- Una unidad defectuosa que se vende como segunda no vale lo mismo: si la salida se mide en pesos de
  venta, la mala calidad baja la productividad aunque salgan las mismas unidades.
- La productividad mide cantidad. Si la calidad cambia y la cantidad no, el indicador no lo ve.
- Factores externos (un corte de luz, una alza del dólar) la mueven sin que la operación haya
  cambiado.
- En servicios cuesta definir la unidad de salida (¿una consulta corta vale lo mismo que una larga?).

La productividad mejora por tres palancas: la mano de obra (formación, salud, motivación), el capital
(máquinas y tecnología) y la administración (cómo se combinan los dos). Las unidades 3 a 11 son, en el
fondo, herramientas de la tercera.

---

## 3. Ejemplo resuelto · Frutos del Itata

Frutos del Itata es una planta de mermeladas de Coelemu. En 2026 cambió su paila a vapor por una
cocedora con control automático de temperatura. El jefe de planta compara un mes típico de cada año
(montos en CLP):

| Dato del mes | 2025 | 2026 |
|---|---|---|
| Personas | 14 | 13 |
| Horas por persona | 176 | 176 |
| Frascos producidos | 36.960 | 41.184 |
| Precio por frasco | 2.900 | 2.900 |
| Remuneración por persona | 690.000 | 720.000 |
| Insumos comprados (fruta, azúcar, frascos, energía, arriendo) | 71.500.000 | 80.900.000 |
| Activo fijo | 150.000.000 | 185.000.000 |

**Paso 1 · Horas-hombre.** En 2025, 14 × 176 = 2.464 HH; en 2026, 13 × 176 = 2.288 HH.

**Paso 2 · Ventas, valor agregado y utilidad (CLP).**

| | 2025 | 2026 |
|---|---|---|
| Ventas $V$ | 107.184.000 | 119.433.600 |
| Remuneraciones $W$ | 9.660.000 | 9.360.000 |
| Valor agregado $V - I$ | 35.684.000 | 38.533.600 |
| Utilidad $V - W - I$ | 26.024.000 | 29.173.600 |

Comprobación por adición en 2025: 26.024.000 + 9.660.000 = 35.684.000. Cuadra.

**Paso 3 · Indicadores y variación.**

| Indicador | 2025 | 2026 | Variación |
|---|---|---|---|
| Física (frascos por HH) | 15,0 | 18,0 | +20,0 % |
| Económica (CLP de VA por HH) | 14.482 | 16.842 | +16,3 % |
| Parcial del trabajo (CLP de VA por persona) | 2.548.857 | 2.964.123 | +16,3 % |
| Parcial del capital (VA por peso de activo) | 0,238 | 0,208 | −12,4 % |
| Multifactorial (ventas por peso de $W + I$) | 1,321 | 1,323 | +0,2 % |

**Cómo se lee.**

- Cada hora-hombre produce un 20 % más: la cocedora hace parte del trabajo. La física sube más que la
  económica porque el insumo por frasco subió de 1.935 a 1.964 CLP (la cocedora gasta más energía).
- Cada peso invertido en activo rinde un 12,4 % menos de valor agregado: el activo creció más rápido
  que el valor agregado.
- La multifactorial casi no se movió (+0,2 %). La inversión sustituyó trabajo por capital y energía
  sin ganar mucho en conjunto. La utilidad sí subió, porque se vendieron más frascos.
- La pregunta para el dueño no es «¿subió la productividad?» (la de mano de obra, sí), sino **¿la
  planta vende todo lo que ahora puede producir?** Si no, la cocedora es capacidad ociosa cara.

---

## 4. Producción y costos de corto plazo

En el corto plazo hay un factor fijo (la máquina, el local) y uno variable (las personas). Al sumar
personas a un mismo equipo, la producción total sube, pero no siempre al mismo ritmo.

$$PMg_n = Q_n - Q_{n-1} \qquad PMe_n = \frac{Q_n}{n}$$

- **Producto marginal** ($PMg$): cuánto agrega la persona número $n$.
- **Producto medio** ($PMe$): cuánto produce cada persona en promedio.
- **Rendimientos decrecientes:** desde cierto punto, cada persona extra agrega menos que la
  anterior, porque comparte el mismo equipo fijo.

Los costos siguen a la producción:

$$CT = CF + CV \qquad CMg = \frac{\Delta CT}{\Delta Q} \qquad CFMe = \frac{CF}{Q} \qquad CVMe = \frac{CV}{Q} \qquad CTMe = \frac{CT}{Q}$$

Mientras el costo marginal es menor que el costo total medio, cada unidad extra baja el promedio;
cuando lo supera, lo sube. El mínimo de $CTMe$ está donde se cruzan.

### Ejemplo · cocina de empanadas congeladas

Un horno arrendado a 30.000 CLP por día; cada cocinero cuesta 28.000 CLP por día. Costos en CLP:

| Cocineros | Empanadas $Q$ | $PMg$ | $PMe$ | $CT$ | $CMg$ | $CTMe$ |
|---|---|---|---|---|---|---|
| 0 | 0 | | | 30.000 | | |
| 1 | 120 | 120 | 120 | 58.000 | 233,3 | 483,3 |
| 2 | 300 | 180 | 150 | 86.000 | 155,6 | 286,7 |
| 3 | 420 | 120 | 140 | 114.000 | 233,3 | 271,4 |
| 4 | 480 | 60 | 120 | 142.000 | 466,7 | 295,8 |

El segundo cocinero rinde más que el primero (se reparten la masa y el horno), y desde el tercero los
rendimientos bajan. El costo medio mínimo está con tres cocineros (271,4 CLP por empanada): con el
cuarto, el costo marginal (466,7) ya supera al medio y lo empuja hacia arriba.

**Elegir una planta.** Si hay varias configuraciones posibles (un horno, dos hornos), se arma una
tabla así para cada una y, para el volumen que hay que producir, se elige la de menor $CTMe$. Una
planta grande suele ganar con volúmenes altos y perder con volúmenes bajos, porque su costo fijo se
reparte en pocas unidades (ejercicio 1.5).

---

## 5. Costos para decidir dónde producir

**Costo de mano de obra por unidad.** Un sueldo bajo no implica un costo bajo: importa el sueldo
dividido por la productividad.

$$\text{costo MO por unidad} = \frac{\text{costo por persona y día}}{\text{unidades por persona y día}}$$

Un taller en Temuco paga 52.000 CLP por persona y día y cada persona hace 130 unidades: 400 CLP por
unidad. Uno en Tacna paga 21.000 CLP y cada persona hace 42: 500 CLP por unidad. El sueldo más alto
produce más barato.

**Localización por costo total.** Cuando los ingresos no dependen del lugar, se compara el costo
total de cada sitio para el volumen esperado:

$$CT_i(Q) = CF_i + cv_i \, Q \qquad Q^* = \frac{CF_B - CF_A}{cv_A - cv_B}$$

$Q^*$ es el **volumen de indiferencia**: bajo él gana el sitio de menor costo fijo, sobre él el de
menor costo variable. Una bodega en Penco (30.000.000 CLP fijos al año, 2.500 CLP por unidad) contra
una en Lota (22.000.000 CLP y 3.300 CLP): $Q^* = 8.000.000 / 800$, es decir 10.000 unidades al año.
Con menos de 10.000, Lota; con más, Penco.

---

## 6. Errores típicos

| Error | Cómo evitarlo |
|---|---|
| Dividir la producción por el número de personas y llamarlo «por hora» | Primero calcula $HH$ = personas × horas por persona |
| Restar las remuneraciones para obtener el valor agregado | Los sueldos son parte del VA; solo se restan los insumos comprados afuera |
| Dividir la variación por el valor final | $\Delta\% = (P_1 - P_0)/P_0$, siempre sobre el inicial |
| Redondear la dotación hacia abajo | 41,3 personas son 42; con 41 no se cumple la meta |
| Contar las unidades defectuosas al precio normal | Si la salida va en pesos, cada segunda se valora a su precio |
| Concluir con una sola productividad parcial | Revisa también la multifactorial: la parcial premia reemplazar personas por máquinas |
| Elegir un sitio solo por su costo fijo o solo por el variable | Compara el costo total con el volumen esperado y calcula $Q^*$ |
| Buscar el mínimo de costo en la columna de costo total | El mínimo que importa es el del costo **medio** ($CTMe$) |

---

## 7. Práctica

Diez ejercicios: 1.1 a 1.4 básicos, 1.5 a 1.8 intermedios, 1.9 y 1.10 de desafío. Las pautas están
en la sección 8. Intenta cada uno antes de mirarla.

**1.1 · Lavandería industrial (básico).** Una lavandería de Talcahuano lavó 3.150 kg de ropa en una
semana con 5 personas de 45 horas. La semana siguiente lavó 3.360 kg con 6 personas de 42 horas.
Calcula la productividad de la mano de obra de cada semana (kg por HH) y su variación. ¿Mejoró?

**1.2 · Fábrica de cajas de cartón (básico).** En un mes produjo 12.600 cajas. Sus costos fueron:
mano de obra 1.890.000 CLP, materiales 4.410.000 CLP, energía 630.000 CLP y arriendo de máquinas
1.050.000 CLP. (a) Calcula la productividad multifactorial en cajas por cada 1.000 CLP. (b) Si el
cartón sube 10 % y todo lo demás se mantiene, ¿cuánto varía?

**1.3 · Sistemas y servicios (básico).** Sin calcular. (a) Para una viña, una aplicación de reparto
y una notaría, identifica entradas, recursos, transformación y salida. (b) Ubica cada una en el
continuo bien–servicio con un argumento. (c) Una notaría atiende con un solo funcionario para no
tener a nadie ocioso. ¿Es eficiente, eficaz, ambas o ninguna?

**1.4 · Taller de costura (básico).** Prendas por día según el número de costureras, con las mismas
cuatro máquinas. Calcula el producto marginal y el medio. ¿Desde qué costurera hay rendimientos
decrecientes? ¿Con cuántas es máximo el producto medio?

| Costureras | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| Prendas por día | 0 | 35 | 80 | 110 | 128 | 136 |

**1.5 · Elegir configuración (intermedio).** Un taller de bolsas reutilizables evalúa trabajar con
una o con dos máquinas de coser industriales. Cada máquina cuesta 18.000 CLP por día (arriendo) y
cada operaria 32.000 CLP por día. Producción diaria según operarias:

| Operarias | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Una máquina | 50 | 120 | 160 | 180 |
| Dos máquinas | 60 | 150 | 220 | 260 |

(a) Calcula el costo total medio de cada combinación. (b) Si un cliente pide al menos 150 bolsas
diarias, ¿qué configuración y cuántas operarias conviene, y a qué costo por bolsa? (c) ¿Dónde está
el costo medio mínimo de cada configuración?

**1.6 · Dos fábricas de muebles (intermedio).** Datos de un mes (montos en CLP). Calcula, para cada
una, el valor agregado (por sustracción y por adición), la productividad física, la económica, la
parcial del trabajo y la parcial del capital. ¿Cuál es más productiva? Responde por indicador.

| Dato | Fábrica A | Fábrica B |
|---|---|---|
| Personas | 18 | 11 |
| Horas por persona al mes | 176 | 168 |
| Muebles producidos | 1.320 | 1.050 |
| Precio por mueble | 64.000 | 61.000 |
| Remuneración por persona | 720.000 | 850.000 |
| Insumos comprados | 41.500.000 | 33.800.000 |
| Activo fijo | 240.000.000 | 410.000.000 |

**1.7 · Jornada de 40 horas (intermedio).** Una conservera tiene 38 personas con 42 horas semanales y
48 semanas al año, y su productividad es de 12,5 unidades por HH. Para el año en que la jornada baja a
40 horas espera vender un 5 % más. (a) ¿Cuántas personas necesita para sostener la productividad?
(b) Si no quiere contratar, ¿cuánto tendría que subir la productividad?

**1.8 · Envasado de miel (intermedio).** Una línea llena 1.800 frascos por turno de 8 horas con 5
personas. El 6 % sale con la etiqueta chueca y se vende como segunda al 60 % del precio normal de
3.500 CLP. (a) Calcula la productividad en pesos de venta por HH sin defectos y con defectos. (b) Una
etiquetadora nueva baja los defectos a 2 %: ¿cuánto sube la productividad?

**1.9 · Tres comunas (desafío).** Una empresa elige dónde instalar su planta. Los ingresos no
dependen del lugar. Montos en CLP:

| Comuna | Costo fijo anual | Costo variable por unidad |
|---|---|---|
| Chillán | 42.000.000 | 6.800 |
| Los Ángeles | 58.000.000 | 5.600 |
| Coronel | 85.000.000 | 4.300 |

(a) ¿Cuál conviene para 18.000 unidades al año? (b) Calcula los volúmenes de indiferencia y di qué
comuna gana en cada rango. (c) Si el volumen sube 20 %, ¿cambia la decisión?

**1.10 · Llenadora automática (desafío).** Una planta envasa vino para viñas chicas y cobra 1.300 CLP
por botella; los materiales (botella, corcho, etiqueta) cuestan 620 CLP por botella. Datos de un mes
(montos en CLP):

| Dato | Actual (A) | Con llenadora (B) |
|---|---|---|
| Personas | 12 | 8 |
| Horas por persona | 180 | 180 |
| Botellas | 54.000 | 60.000 |
| Remuneración por persona | 780.000 | 780.000 |
| Energía | 1.900.000 | 3.100.000 |
| Capital (cuota del leasing) | 2.400.000 | 9.800.000 |

(a) Calcula la productividad de la mano de obra (botellas por HH) y la multifactorial (pesos de venta
por peso de costo) en A y en B, con su variación. (b) ¿Conviene la llenadora con 60.000 botellas?
(c) La llenadora puede llegar a 70.000 botellas con las mismas 8 personas. ¿Desde qué volumen
mensual deja más utilidad que la situación actual?

---

## 8. Pautas

**1.1.** Semana 1: 3.150 / (5 × 45) = 14,00 kg por HH. Semana 2: 3.360 / (6 × 42) = 13,33 kg por HH.
Variación: −4,8 %. Lavó más kilos, pero con más horas en proporción: la productividad bajó.

**1.2.** (a) Costo total: 7.980.000 CLP. Son 12.600 cajas / 7.980 miles de pesos = 1,579 cajas por
cada 1.000 CLP. (b) Los materiales pasan a 4.851.000 CLP y el total a 8.421.000 CLP: 1,496 cajas por
cada 1.000 CLP, una variación de −5,2 %. La planta no cambió nada y su multifactorial bajó: un factor
externo mueve el indicador.

**1.3.** (a) Viña: entradas uva; recursos tierra, prensas, cubas, enólogo; transformación
fermentar y guardar; salida vino embotellado. Aplicación de reparto: entradas pedidos; recursos
repartidores, plataforma, motos; transformación recoger y trasladar; salida pedido entregado.
Notaría: entradas documentos y clientes; recursos notario, funcionarios, sistema; transformación
revisar, autorizar, registrar; salida documento con fe pública. (b) La viña está cerca del bien puro
(se guarda en inventario); la notaría, cerca del servicio puro (el cliente está presente y no se
almacena); el reparto es un servicio que mueve un bien. (c) Eficiente (nadie ocioso), pero no eficaz
si la espera hace que la gente se vaya sin su trámite: el cliente es parte del proceso y su tiempo
también es un recurso.

**1.4.**

| Costureras | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Producto marginal | 35 | 45 | 30 | 18 | 8 |
| Producto medio | 35,0 | 40,0 | 36,7 | 32,0 | 27,2 |

Rendimientos decrecientes desde la tercera costurera (agrega 30, menos que las 45 de la segunda). El
producto medio es máximo con dos (40,0 prendas por persona). Desde la tercera, las costureras
empiezan a esperar máquina.

**1.5.** (a) Costo total medio en CLP por bolsa:

| Operarias | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Una máquina | 1.000,0 | 683,3 | 712,5 | 811,1 |
| Dos máquinas | 1.133,3 | 666,7 | 600,0 | 630,8 |

(b) Con una máquina hacen falta 3 operarias (160 bolsas): 18.000 + 96.000 = 114.000 CLP al día, es
decir 712,5 CLP por bolsa. Con dos máquinas bastan 2 operarias (150 bolsas): 36.000 + 64.000 =
100.000 CLP, o 666,7 CLP por bolsa. Conviene **dos máquinas con dos operarias**. (c) Una máquina:
mínimo de 683,3 CLP con dos operarias. Dos máquinas: mínimo de 600,0 CLP con tres operarias. Si el
cliente crece a 220 bolsas, la segunda máquina se vuelve aún más conveniente.

**1.6.**

| Indicador | Fábrica A | Fábrica B |
|---|---|---|
| Valor agregado (CLP) | 42.980.000 | 30.250.000 |
| Física (muebles por HH) | 0,42 | 0,57 |
| Económica (CLP de VA por HH) | 13.567 | 16.369 |
| Parcial del trabajo (CLP de VA por persona) | 2.387.778 | 2.750.000 |
| Parcial del capital | 0,179 | 0,074 |

Por adición: A tiene utilidad de 30.020.000 CLP más remuneraciones de 12.960.000 CLP; B, 20.900.000
más 9.350.000. Las dos formas cuadran. B es más productiva por persona y por hora (está más
automatizada); A rinde más del doble por peso de activo. No hay una «más productiva» en abstracto: B
gana si lo escaso es la gente, A si lo escaso es el capital.

**1.7.** Hoy: 38 × 42 × 48 = 76.608 HH, y 12,5 × 76.608 = 957.600 unidades. Meta: 957.600 × 1,05 =
1.005.480 unidades. (a) Personas: 1.005.480 / (12,5 × 40 × 48) = 41,90, es decir **42 personas**
(cuatro más). Solo por la jornada harían falta 39,9; el resto es el alza de ventas. (b) Con 38
personas, la productividad tendría que ser 1.005.480 / (38 × 40 × 48) = 13,78 unidades por HH: un alza
de 10,2 %. Es mucho para lograrlo sin invertir.

**1.8.** Son 5 × 8 = 40 HH. (a) Sin defectos: 1.800 × 3.500 / 40 = 157.500 CLP por HH. Con 108
frascos de segunda (a 2.100 CLP): (1.692 × 3.500 + 108 × 2.100) / 40 = 153.720 CLP por HH, una
variación de −2,4 %. (b) Con 2 % de defectos (36 frascos): 156.240 CLP por HH, un alza de 1,6 %. La
mala calidad le cuesta productividad a una línea que produce las mismas unidades.

**1.9.** (a) Costo total con 18.000 unidades: Chillán 164.400.000 CLP, Los Ángeles 158.800.000 CLP,
Coronel 162.400.000 CLP. Conviene **Los Ángeles**. (b) Chillán–Los Ángeles: 16.000.000 / 1.200 =
13.333 unidades. Los Ángeles–Coronel: 27.000.000 / 1.300 = 20.769. Chillán–Coronel: 17.200 (no decide
nada, porque en ese tramo gana Los Ángeles). Bajo 13.333 unidades gana Chillán; entre 13.333 y 20.769,
Los Ángeles; sobre 20.769, Coronel. (c) Con 21.600 unidades: Chillán 188.880.000 CLP, Los Ángeles
178.960.000 CLP, Coronel 177.880.000 CLP. **Cambia a Coronel**, aunque por poco: si el alza de ventas
es dudosa, Los Ángeles es la opción menos arriesgada.

**1.10.** (a)

| | A | B | Variación |
|---|---|---|---|
| Botellas por HH | 25,00 | 41,67 | +66,7 % |
| Costo total (CLP) | 47.140.000 | 56.340.000 | |
| Multifactorial | 1,489 | 1,384 | −7,0 % |
| Utilidad (CLP) | 23.060.000 | 21.660.000 | |

(b) No: la productividad de la mano de obra sube dos tercios, pero la multifactorial baja y la
utilidad cae en 1.400.000 CLP al mes. La llenadora ahorra 3.120.000 CLP en sueldos y agrega 8.600.000
CLP en energía y capital. (c) Cada botella deja 1.300 − 620 = 680 CLP. Con la llenadora, los costos
que no dependen del volumen suman 19.140.000 CLP. La utilidad iguala a la actual cuando
$680 \, Q - 19.140.000 = 23.060.000$, es decir con 62.059 botellas al mes. La llenadora solo se
justifica si hay clientes para más de 62.059 botellas (la situación actual no puede pasar de 54.000
con 12 personas).

---

## 9. Caso integrador · Estampa Sur, marzo

> Este caso sigue a Estampa Sur por todo el ramo (taller de serigrafía ficticio de la Región del
> Biobío, con dos centros: estampado y planchado y doblado). Acá se mide su productividad y se fija
> el estándar de horas-hombre por unidad que usa la planeación agregada (unidad 6).

En marzo (21 días hábiles) trabajaron las 4 personas del taller, 8 horas al día, y salieron 5.600
prendas estampadas. En marzo del año anterior, con la misma dotación y los mismos días, salieron
4.872 (todavía estampaban con el pulpo manual). Datos del mes:

| Dato | Valor |
|---|---|
| Costo por hora-hombre | 4.500 CLP |
| Prenda lisa (costo promedio) | 2.400 CLP |
| Tinta por prenda | 0,015 kg, a 16.500 CLP el kg |
| Energía y arriendo | 1.250.000 CLP |
| Precio promedio de venta | 4.900 CLP |

**Pregunta.** ¿Cuánto mejoró la productividad del taller? ¿Cuántas horas-hombre por prenda debe usar
el plan de producción? Y si el pronóstico para el próximo mes (20 días hábiles) es de 6.100 prendas,
¿alcanza la gente?

**Desarrollo.**

| Indicador | Valor |
|---|---|
| Horas-hombre del mes | 4 × 8 × 21 = 672 |
| Productividad física | 8,33 prendas por HH (el año anterior, 7,25): +14,9 % |
| Estándar | 0,12 HH por prenda |
| Remuneraciones | 3.024.000 CLP |
| Insumos comprados (prendas, 84 kg de tinta, energía y arriendo) | 16.076.000 CLP |
| Ventas | 27.440.000 CLP |
| Valor agregado | 11.364.000 CLP |
| Utilidad | 8.340.000 CLP |
| Productividad económica | 16.911 CLP por HH |
| Multifactorial | 1,437 pesos vendidos por peso gastado |

Para el próximo mes: 6.100 × 0,12 = 732 HH necesarias, contra 4 × 8 × 20 = 640 disponibles. Faltan
92 HH, un 14,4 % de lo disponible.

**Lectura.** El pulpo automático subió la productividad de la mano de obra en 14,9 %. Cada prenda
toma 0,12 HH de trabajo total (no solo de máquina: incluye preparar marcos, revisar, doblar y
embalar). Con ese estándar, las cuatro personas no alcanzan para el pronóstico del próximo mes. Hay
tres salidas: horas extra, usar el inventario que haya o contratar. Elegir entre ellas al menor costo
es la planeación agregada.

**Lo que pasa a la unidad 6.** El estándar de 0,12 HH por prenda, el costo de 4.500 CLP por HH y la
dotación de 4 personas.

---

## 10. Para seguir

**En los libros del ramo.**

- Chase, Jacobs y Aquilano, *Administración de operaciones* (12.ª ed., 2009), capítulo 1 (el que fija
  el programa para esta unidad): qué es la administración de operaciones, bienes y servicios, y su
  evolución.
- Heizer y Render, *Principios de administración de operaciones* (5.ª ed., 2004), capítulo
  introductorio: productividad parcial y multifactorial, y las decisiones de operaciones. Sus
  problemas del final del capítulo son buena práctica adicional.

**Abiertos y gratis.**

- Abbas y Goosheh, *Operations Management*, Fanshawe College (2025), en inglés. Busca en el índice la
  parte introductoria y la de productividad. Descarga en la colección abierta de Ontario:
  https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/2473

**Con el tutor.** La carpeta `tutor/` trae el contexto de este ramo. Pégalo al inicio de la
conversación con cualquier IA y pídele, por ejemplo: «Dame dos empresas con datos de un mes y
corrígeme el valor agregado y las cuatro productividades paso a paso».
