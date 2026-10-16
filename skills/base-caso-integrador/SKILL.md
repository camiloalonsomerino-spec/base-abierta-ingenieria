---
name: base-caso-integrador
description: Use when a course in the open engineering base needs its integrating case — one fictitious person or company that walks through the units as a calculation chain, where what one unit computes is the input of the next — designed BEFORE the units are written, as a single Python script that is the only source of the shared numbers, checked for coincidences with the course material and for internal consistency. Also when a unit writer reports an inconsistency in the case. Diseña el caso integrador de un ramo como un solo script encadenado.
---

# El caso integrador de un ramo

Un caso que recorre el ramo como una **cadena de cálculo**. Se diseña **antes** de repartir las
unidades: si cada unidad inventa su pieza, las cifras no se encadenan.

## Diseño

1. Elige un protagonista ficticio que dé sentido a la cadena (un taller que planifica su producción;
   la dueña de ese taller que ahorra, se endeuda e invierte). Puede cruzar ramos: el mismo taller
   sirve a Operaciones y a Finanzas.
2. Escribe la cadena: para cada unidad, qué calcula y qué entrega a la siguiente. Las unidades que no
   encadenan (introducción, estrategia, calidad) usan la empresa con datos propios.
3. Fija datos **raros**: nada de cifras redondas ni de números que aparezcan en el material.

## El script

`ramos/<ramo>/verificacion/caso_<nombre>.py`, con:

- Un bloque de datos por unidad (`U3 = {...}`), comentado.
- Una función `calcular()` que devuelve un diccionario por unidad (`C["u7"]`), con todo lo que las
  unidades van a citar.
- `--json` para dejar `caso_<nombre>.json`.
- **Asserts de coherencia** para todo dato que dos unidades comparten (por ejemplo, el inventario
  inicial del plan agregado tiene que ser la suma de los inventarios por producto del programa
  maestro). Una incoherencia que no tiene assert vuelve a aparecer.
- Si una pieza tiene que cumplir una condición (por ejemplo, que la semana 6 tenga un lote de cada
  producto), una búsqueda (con programación dinámica, no fuerza bruta) que encuentra los datos que la
  cumplen sin mover lo que ya está escrito.

## Antes de entregarlo

- Corre `herramientas/colisiones.py` con todos los datos del caso contra el texto del material.
- Revisa los casos borde: una TIR con varios cambios de signo, un MRP que liberaría antes de la
  semana 1, una inicialización que sesga los primeros períodos. O se corrigen o se convierten en
  lección escrita en la unidad.

## Cuando una unidad reporta un problema del caso

Lo corrige **solo quien coordina**, en el script. Después corre todos los verificadores del ramo
(`herramientas/revisar_ramo.py`): los que fallen son exactamente las unidades que hay que tocar. Avisa a
los agentes que sigan trabajando con el cambio y sus cifras nuevas.
