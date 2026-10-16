-- Unidad 2 · Modelo entidad-relación: comprobar el diagrama de Estampa Sur contra la base
-- Corre sobre una copia de datos/estampa_sur.db. Las funciones pragma_* son propias de SQLite;
-- en MySQL lo mismo se pregunta a information_schema (ver la unidad).

-- 1. Las columnas de una entidad: ¿están todos los atributos del diagrama?
SELECT name, type, pk FROM pragma_table_info('producto');

-- 2. Las claves foráneas de toda la base: cada una sale de un rombo del diagrama
SELECT m.name AS tabla, f."from" AS columna, f."table" AS apunta_a
FROM sqlite_master m
JOIN pragma_foreign_key_list(m.name) f
WHERE m.type = 'table'
ORDER BY m.name, f."from";
