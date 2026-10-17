# Bases de Datos

Cómo se diseña una base de datos (del problema en palabras al diagrama entidad-relación y a las
tablas), cómo se evita guardar lo mismo dos veces y cómo se le pregunta con SQL.

**Nivel:** segundo año de Ingeniería Civil Industrial. **Antes:** ninguno en particular.
**Software:** SQL estándar. Todo corre en SQLite, que viene con Python, y en MySQL; cada unidad
indica las diferencias con MySQL. Los scripts SQL de cada unidad están en `sql/` y la base del caso
en `datos/estampa_sur.db`.

## Unidades

| N.º | Unidad | Estado (16-10-2026) |
|---|---|---|
| 1 | [Datos, información y sistemas de bases de datos](unidades/01-sistemas-de-bases-de-datos.md) | 0.1 · [PDF](pdf/01-sistemas-de-bases-de-datos.pdf) |
| 2 | [Modelo entidad-relación](unidades/02-modelo-entidad-relacion.md) | 0.1 · [PDF](pdf/02-modelo-entidad-relacion.pdf) |
| 3 | [Cardinalidad, participación, entidades débiles y jerarquías](unidades/03-cardinalidad-y-jerarquias.md) | 0.1 · [PDF](pdf/03-cardinalidad-y-jerarquias.pdf) |
| 4 | [Del modelo entidad-relación al modelo relacional](unidades/04-mer-a-relacional.md) | 0.1 · [PDF](pdf/04-mer-a-relacional.pdf) |
| 5 | [Modelo relacional: claves e integridad](unidades/05-claves-e-integridad.md) | 0.1 · [PDF](pdf/05-claves-e-integridad.pdf) |
| 6 | [Normalización](unidades/06-normalizacion.md) | 0.1 · [PDF](pdf/06-normalizacion.pdf) |
| 7 | [Álgebra relacional](unidades/07-algebra-relacional.md) | 0.1 · [PDF](pdf/07-algebra-relacional.pdf) |
| 8 | [SQL para crear y modificar: DDL y DML](unidades/08-sql-ddl-y-dml.md) | 0.1 · [PDF](pdf/08-sql-ddl-y-dml.pdf) |
| 9 | [SQL para consultar una tabla](unidades/09-sql-una-tabla.md) | 0.1 · [PDF](pdf/09-sql-una-tabla.pdf) |
| 10 | [SQL con varias tablas: joins y agregación](unidades/10-sql-joins-y-agregacion.md) | 0.1 · [PDF](pdf/10-sql-joins-y-agregacion.pdf) |
| 11 | [Subconsultas y vistas](unidades/11-subconsultas-y-vistas.md) | 0.1 · [PDF](pdf/11-subconsultas-y-vistas.pdf) |
| 12 | [Transacciones, índices y la base dentro de un programa](unidades/12-transacciones-e-indices.md) | 0.1 · [PDF](pdf/12-transacciones-e-indices.pdf) |

## El caso integrador · la base de datos de Estampa Sur

El mismo taller ficticio de los otros ramos, ahora como sistema de información: tiendas, productos,
proveedores, clientes, pedidos y órdenes de producción. Los productos, precios y lotes vienen de los
otros ramos; clientes y pedidos son **simulados** con semilla fija por
`verificacion/caso_estampa_sur_bd.py`.

| Unidad | Lo que construye |
|---|---|
| 1 | Qué datos maneja el taller y por qué una planilla ya no alcanza |
| 2 y 3 | El diagrama entidad-relación del taller |
| 4 y 5 | Las tablas con sus claves primarias y foráneas |
| 6 | Por qué el detalle del pedido va en su propia tabla (normalización) |
| 7 | Las preguntas del dueño escritas en álgebra relacional |
| 8 | El `CREATE TABLE` de las 8 tablas y la carga de datos |
| 9 a 11 | Ventas por tienda, margen por tipo de cliente, clientes sin pedidos, proveedor más barato, la semana 6 de producción |
| 12 | Registrar un pedido como transacción e índices para las consultas frecuentes |

## Datos de los ejemplos

Todas las personas, RUT, teléfonos y patentes de los ejemplos son ficticios. Los RUT están en el rango
de los 40 millones, que hoy no usan ni las personas (bajo 30 millones) ni las empresas (sobre 50
millones); los teléfonos son `+56 9 0000 0xxx` y las patentes llevan vocales, que las patentes chilenas
no usan. Cambiados el 16-10-2026: la versión 0.1 traía RUT y celulares con forma real.

## Bibliografía

El programa del ramo no estaba disponible. Referencias habituales del área: Elmasri y Navathe,
*Fundamentos de sistemas de bases de datos*; Silberschatz, Korth y Sudarshan, *Fundamentos de bases de
datos*. Cada unidad cita además un libro abierto verificado.

## Cómo se usa

- **Estudiar:** lee la unidad en PDF (`pdf/`) o en Markdown (`unidades/`).
- **Practicar:** corre los scripts de `sql/` sobre `datos/estampa_sur.db` con `sqlite3` o en MySQL.
- **Practicar con IA:** pega `tutor/contexto.md` al inicio de la conversación.
- **Comprobar una cifra:** cada unidad tiene su script en `verificacion/`; con `--revisar` busca cada
  resultado en el texto.
