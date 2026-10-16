# Formato de una unidad

## Frontmatter

```yaml
---
ramo: <nombre del ramo>
unidad: <N>
titulo: <título>
version: 0.1 (DD-MM-AAAA)
requiere: [<NN-slug real>, ...]     # nombres reales de archivo, no supuestos
alimenta: [<NN-slug real>, ...]
verificacion: verificacion/uNN_<tema>.py
---
```

## Secciones, en este orden

1. `# Unidad N · <Título>`
2. **Qué vas a poder hacer.** Una frase con los verbos del método, no con los temas.
3. **Lo que necesitas antes.** Las unidades previas y lo mínimo que hay que saber de ellas.
4. **Tiempo.** Horas de lectura y de práctica.
5. **Teoría justa**, en secciones numeradas: la idea y por qué importa, la notación, las fórmulas
   (LaTeX), la intuición detrás de cada una (por qué funciona) y cuándo NO aplica.
6. **Ejemplo resuelto** con un escenario cotidiano propio, paso a paso, con tablas, y un párrafo
   «Cómo se lee» que diga qué decisión se toma con el resultado.
7. **Errores típicos** en tabla: error · cómo evitarlo. Incluye los errores reales que el material o
   el estudiante han mostrado.
8. **Práctica:** exactamente 10 ejercicios, N.1 a N.4 básicos, N.5 a N.8 intermedios, N.9 y N.10 de
   desafío. Si el `ramo.yaml` pide comentes, dos de los diez son una afirmación «verdadero, falso o
   incierto» que se responde con un argumento.
9. **Pautas**, con la respuesta visible (nada plegable) y una frase de lectura en cada una. La pauta
   de un comente es una argumentación completa, no una palabra.
10. **Caso integrador**: la pieza de esta unidad, con las cifras exactas del script del caso, lo que
    recibe de la unidad anterior y lo que pasa a la siguiente.
11. **Para seguir**: libros del programa (capítulo solo si el programa lo fija o si lo verificaste),
    un libro abierto verificado con WebFetch, y una frase de ejemplo para pedirle práctica al tutor.

## Redacción

- Español de Chile, coma decimal y punto de miles; montos con punto de miles.
- Los incisos van entre paréntesis ( ). La raya (—) no se usa como paréntesis; solo separa.
- Fechas DD-MM-AAAA. Frases cortas y directas. Sin relleno.
- Explica la intuición, no repitas la fórmula en palabras.

## Escritura técnica que el PDF necesita

- Pesos con punto de miles se escriben tal cual (`$36.000`); bajo mil, `\$600`.
- Dentro de LaTeX: coma decimal `{,}`, separador de miles `{.}`. Una fórmula que empieza con un
  número de miles se envuelve: `${72{.}000}/…$`.
- Tablas de más de 9 columnas: abrevia rótulos o pásalas a filas para que quepan en A4.
- Tablas de datos largas (20 subgrupos, 24 meses): un registro por fila.
