---
name: base-ingenieria-inversa
description: Use when a university course (ramo) is about to enter the open engineering base and its structure must be reverse-engineered from the course material — gathering every file (local folders, the semester archive, Canvas), extracting the text privately, reading the official program and its bibliography, mapping which class, test and book chapter feeds each topic, and proposing the list of units. Also "hagamos el ramo X", "ingeniería inversa de Finanzas", "¿qué unidades tendría este ramo?". Saca la estructura de un ramo desde su material, sin publicar nada del material.
---

# Ingeniería inversa de un ramo

El material del curso es la **fuente privada** para entender qué se enseña, en qué orden y con qué
profundidad. Nunca se publica. Lo que sale de esta skill es un mapa y un `ramo.yaml`.

## 1. Juntar el material

- Busca el ramo en la carpeta del semestre vivo y en `_Archivo` (por nombre del ramo).
- Compara contra el curso en Canvas: lista sus archivos por módulos con la API
  (`/api/v1/courses/<id>/modules?include[]=items`, solo los ID) y descarga **de a uno** navegando a
  `/courses/<cid>/files/<fid>/download?download_frd=1`, en tandas de diez. Pide permiso antes de
  descargar, diciendo cuántos archivos, de dónde y cuánto pesan.
- Verifica cada descarga por tamaño en bytes contra Canvas y archiva con el prefijo del ramo, dejando
  una fila por archivo en el registro de movimientos.

## 2. Extraer el texto, en privado

```
py -3 -P herramientas/extraer_texto.py "<carpeta del material>" "<datos-privados>/<ramo>/texto-del-material"
```

Copia también los `.md` propios del estudiante (punteos, transcripciones): dicen lo que el profesor
enfatizó. Los libros completos no se extraen; se consultan por partes.

## 3. Leer el programa

El programa (calendarización) fija las unidades oficiales, los resultados de aprendizaje, la
bibliografía con su edición y, a veces, el capítulo por semana. Es la única fuente válida para citar un
capítulo. **Separa la bibliografía obligatoria de la complementaria tal como la rotula el programa**
(en Contabilidad se confundieron al primer intento). Anota también cómo se evalúa (por ejemplo, «40 % conceptual con comentes»): define el estilo
de los ejercicios.

## 4. Mapear

Por cada tema: en qué clase se explica, en qué ayudantía o práctica se ejercita, en qué evaluación
salió, y de qué libro viene el material (se reconoce por los ejemplos: si las láminas usan el ejemplo
clásico de un libro, ese es el libro). Incluye los temas del programa que no tuvieron material en
clase: se escriben desde los libros.

## 5. Proponer las unidades

Entre 8 y 14 unidades, ordenadas por dependencia (lo que una calcula, la siguiente lo usa). Cada una
con su título, sus métodos y la pieza del caso integrador que podría tocarle.

## Salidas

- `<datos-privados>/<ramo>/ingenieria-inversa.md`: el mapa (unidad → clases, evaluaciones, libro) y lo
  que pidió cada evaluación. **Privado.**
- `ramos/<ramo>/README.md`: unidades, cadena del caso (por diseñar) y bibliografía del programa.
  **Público:** sin nombres de profesores ni datos del material.
- `ramos/<ramo>/ramo.yaml`: ver [ramo.yaml](ramo-plantilla.yaml). **Público:** sin nombres de archivos
  del material, códigos de curso ni números de Canvas (el nombre del programa va en el encargo privado).

## Límites

- Nada del material entra a la carpeta pública: ni enunciados, ni tablas, ni láminas, ni datos.
- Un error encontrado en una pauta se anota en `<datos-privados>/<ramo>/errores-del-material.md`: le
  sirve al estudiante para estudiar.
