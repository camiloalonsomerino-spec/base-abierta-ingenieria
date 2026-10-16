---
name: base-unidad
description: Use when one unit (unidad) of a university course in the open engineering base must be written or rewritten — the theory just deep enough to understand the method, one worked example, ten graded exercises with visible answer keys, typical errors, the integrating-case piece, sources and a tutor block — with every number recalculated by a verification script and the unit rendered to a branded PDF. Also when a subagent receives the brief "escribe la unidad N del ramo X". Escribe una unidad de la base abierta de ingeniería, con verificador y PDF, sin copiar nada del material del curso.
---

# Escribir una unidad de la base abierta

Una unidad es un archivo `ramos/<ramo>/unidades/NN-<tema>.md`, su verificador
`ramos/<ramo>/verificacion/uNN_<tema>.py` y su PDF `ramos/<ramo>/pdf/NN-<tema>.pdf`. Se escribe
**desde cero**: del material del curso se saca el alcance y la profundidad, nunca el texto ni los datos.

## Antes de escribir

1. Lee `ramos/<ramo>/ramo.yaml` (rutas del material privado, programa, caso y estilo del ramo) y el
   `README.md` del ramo (mapa de unidades y cadena del caso).
2. Lee una unidad ya terminada como modelo de formato. La de referencia es
   `ramos/gestion-de-operaciones/unidades/10-programacion-de-operaciones.md` con su verificador.
3. Busca tu tema en el texto del material (carpeta `texto` del `ramo.yaml`) para fijar alcance,
   profundidad y tipos de ejercicio. Anota lo que pide cada evaluación.
4. Lee el script del caso integrador y la pieza que le toca a tu unidad. **No lo edites**: si ves un
   problema, repórtalo a quien coordina.

## El formato (obligatorio)

Lo detalla [formato.md](formato.md). En resumen: frontmatter · qué vas a poder hacer · lo que
necesitas antes · tiempo · teoría justa en secciones numeradas · ejemplo resuelto · errores típicos ·
**exactamente 10 ejercicios** (4 básicos, 4 intermedios, 2 de desafío) · pautas visibles con su
lectura · pieza del caso integrador · para seguir. Si el `ramo.yaml` pide comentes, dos de los diez
son comentes con pauta argumentada.

## Datos originales (obligatorio)

Cada dato numérico de un ejercicio pasa por el detector antes de fijarse:

```
py -3 -P herramientas/colisiones.py "<carpeta texto del ramo>" <números del ejercicio>
```

Si avisa tres o más datos juntos en un mismo archivo, cambia los datos. De los libros se cita el
capítulo solo si el programa lo fija o si lo verificaste; nunca se inventan números de capítulo ni de
problema. Un libro abierto se cita solo después de verificar su URL con WebFetch.

## Verificación (obligatoria)

El verificador recalcula **todas** las cifras desde los datos y, con `--revisar`, busca cada resultado
formateado en el `.md` (normalizando `{,}` a `,` y `{.}` a `.`). Si la unidad usa el caso, lo importa y
compara (debe imprimir `CADENA: OK`). Termina en `REVISIÓN: OK`. Detalle y plantilla en
[verificador.md](verificador.md).

## Unidades generadas desde una plantilla

Si las tablas son largas (simplex, registros MRP) y el `.md` se arma desde una plantilla con un
script, **la plantilla y el armador viven en `ramos/<ramo>/verificacion/plantillas/`**, nunca en una
carpeta temporal, y el armador usa rutas relativas. Esa unidad no se corrige a mano: se corrige la
plantilla o el verificador y se vuelve a armar. (En Optimización, el armador de las unidades 9 y 10
quedó en un temporal y hubo que rescatarlo.)

## PDF

```
PYTHONIOENCODING=utf-8 py -3 -P herramientas/md_a_pdf.py ramos/<ramo>/unidades/NN-<tema>.md
py -3 -P herramientas/revisar_pdf.py ramos/<ramo>/pdf/NN-<tema>.pdf --png 2
```

Mira el PNG una vez. Un solo arreglo, sin bucle de capturas.

## Respuesta a quien coordina

Archivo, páginas del PDF, resultado de `--revisar` y de la cadena, un bloque para el tutor (notación,
4 a 6 errores típicos, una línea de métodos) y los problemas encontrados en el caso o en el material
(errores de pautas con archivo y cifra: le sirven al estudiante).

## Límites

- No toques el README del ramo, el `tutor/contexto.md`, el script del caso ni unidades ajenas.
- Nada del material del curso entra a la base: ni enunciados, ni tablas, ni datos, ni láminas.
- Windows: Bash es Git Bash; rutas con espacios entre comillas; `rm -rf` no borra.
