---
name: base-ramo
description: Use when a whole university course (ramo) must be added to the open engineering base, end to end — "hagamos el ramo X", "sigue con el siguiente ramo", "libera el ramo X", "pasa X a la base abierta". Orchestrates in the main conversation the reverse engineering of the course material, a visual preview, the integrating case, one subagent per pair of units writing in parallel, and the final review that fixes the case in one place and closes README, tutor and PDFs. Orquesta un ramo completo de la base abierta, de la ingeniería inversa a los PDF verificados.
---

# Un ramo completo para la base abierta

Corre en la **conversación principal**: un agente no puede lanzar agentes. Las etapas van en orden;
cada una deja algo verificable antes de pasar a la siguiente.

## 0. Antes de empezar

- Lee `README.md` de la base y un ramo terminado (`ramos/gestion-de-operaciones/`) como modelo.
- Confirma con el estudiante qué ramo es y, si lo está cursando ahora, cuándo es su próxima
  evaluación: la base le sirve para estudiar y conviene saber qué unidades le urgen.

## 1. Ingeniería inversa → skill `base-ingenieria-inversa`

Sale el mapa privado, el `README.md` del ramo con las unidades y el `ramo.yaml`.

## 2. Vista previa (solo si el formato no está decidido)

Si el ramo es de un tipo nuevo (por ejemplo, el primero con código o con laboratorio), muestra antes
una hoja con dos o tres formas numeradas de escribir una unidad, con una muestra real. El estudiante
elige un número. Si es un ramo como los anteriores, el formato ya está decidido: capítulo de libro y
caso integrador donde la unidad recibe datos de la anterior.

## 3. Caso integrador → skill `base-caso-integrador`

El script del caso queda cerrado, sin colisiones y con sus asserts, **antes** del paso 4.

## 4. Unidades en paralelo → skill `base-unidad`

- Escribe en la carpeta privada del ramo un `ENCARGO-UNIDADES.md` con lo específico del ramo (estilo,
  comentes, ejemplos cotidianos que le sirven al estudiante, errores que ya cometió) y que remita a la
  skill `base-unidad` para el formato y la verificación.
- Lanza **un agente por par de unidades** (seis agentes para doce unidades), todos en un mismo
  mensaje. A cada uno: el encargo, sus dos unidades con el alcance y la pieza del caso, y qué buscar
  en el material.
- Mientras trabajan: arma la base de `tutor/contexto.md` (quién eres, cómo enseñas, tabla de
  unidades).

## 5. Revisión a medida que llegan

Cada informe trae problemas. Clasifícalos:

| Problema | Quién lo corrige |
|---|---|
| Inconsistencia del caso | Quien coordina, en el script; luego `revisar_ramo.py` dice qué unidades tocar y se avisa a los agentes activos |
| Dato que coincide con el material | Quien coordina, en el caso; el agente, en sus ejercicios |
| Error de la herramienta (PDF, signos) | Quien coordina, en `herramientas/`; se avisa a los agentes activos |
| Error en una pauta del curso | Se anota en `errores-del-material.md` privado y se le cuenta al estudiante |
| Referencias cruzadas (`requiere`, `alimenta`) | Quien coordina, al final, con los nombres reales |

## 6. Cierre

1. `py -3 -P herramientas/revisar_ramo.py ramos/<ramo>` → todos en OK.
2. Regenera todos los PDF con la versión final de la herramienta y revísalos con `revisar_pdf.py`.
3. Completa `tutor/contexto.md` con el bloque de cada agente (notación, errores, métodos).
4. Actualiza el `README.md` del ramo (estado y enlaces) y el de la base (tabla de ramos).
5. Registra el avance en el tablero de proyectos y en la memoria del proyecto.

## 7. Publicar (la base es pública desde el 16-10-2026)

1. Pasa el escáner antes de subir (secretos, datos privados, nombres de la lista privada):
   `py -3 -P ../ingeniero-agentico/security/scan.py --root . --all-files --denylist ../ingeniero-agentico-datos/security/denylist.txt`.
   Los HIGH de `private-denylist` se corrigen; PDF, `exec()` de verificadores y RUT inventados son esperables.
2. Regenera el sitio: `py -3 -P herramientas/sitio.py` (deja `docs/`, que GitHub Pages publica).
3. Commit con el correo noreply del estudiante y `git push`.
4. Deja relleno un release nuevo (`v0.N`) en GitHub con sus notas; lo publica el estudiante y Zenodo
   le asigna el DOI solo. El README cita el DOI general, que siempre apunta a la última versión.

## Lo que se aprendió (y por qué existe cada regla)

- **El caso antes que las unidades.** En Operaciones, el plan agregado partía con 400 unidades y el
  programa maestro con 770; se arregló con un assert en el script.
- **Detector de colisiones.** La primera muestra reutilizó sin querer los datos del ejemplo de clase.
- **Pesos y LaTeX.** `$36.000` se leía como fórmula; ahora la herramienta lo distingue y el formato
  fija `{,}` y `{.}` dentro de LaTeX.
- **Un perfil de navegador por proceso.** Varios agentes imprimiendo a la vez se bloqueaban.
- **Los agentes encuentran errores del material.** Son valiosos para el estudiante: se guardan.
