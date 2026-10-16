-- Unidad 9 · consultas sobre la base del caso (una tabla a la vez)
-- Base abierta de ingeniería · Bases de Datos
--
-- Corre sobre la base de Estampa Sur que crea verificacion/caso_estampa_sur_bd.py:
--   sqlite3 ../datos/estampa_sur.db < u09_caso.sql
-- Cada consulta lleva una marca «-- @nombre» que usa el verificador (verificacion/u09_sql_una_tabla.py).

-- @u9_productos_caros
SELECT nombre, precio FROM producto WHERE precio > 4000 ORDER BY precio DESC;

-- @u9_pedidos_pendientes
SELECT COUNT(*) FROM pedido WHERE estado = 'pendiente';

-- @caso_pendientes_lista
SELECT id_pedido, id_cliente, fecha,
       julianday('2026-04-01') - julianday(fecha) AS dias_esperando,
       CASE
           WHEN julianday('2026-04-01') - julianday(fecha) > 14 THEN 'urgente'
           ELSE 'normal'
       END AS prioridad
FROM pedido
WHERE estado = 'pendiente'
ORDER BY fecha, id_pedido;

-- @caso_margen_unitario
SELECT nombre, precio, costo_var,
       precio - costo_var AS margen,
       ROUND(100.0 * (precio - costo_var) / precio, 1) AS margen_pct
FROM producto
ORDER BY margen_pct DESC;

-- Ejercicios sobre el caso

-- @e4
SELECT nombre, precio, precio - costo_var AS margen,
       ROUND(100.0 * (precio - costo_var) / precio, 1) AS margen_pct
FROM producto
WHERE precio BETWEEN 3000 AND 7000
ORDER BY margen DESC;

-- @e7a
SELECT COUNT(*) AS abiertos
FROM pedido
WHERE fecha BETWEEN '2026-03-16' AND '2026-03-31'
  AND estado IN ('pendiente', 'en taller');

-- @e7b
SELECT id_pedido, fecha, estado
FROM pedido
WHERE fecha BETWEEN '2026-03-16' AND '2026-03-31'
  AND estado IN ('pendiente', 'en taller')
ORDER BY fecha, id_pedido
LIMIT 3;

-- @e7c
SELECT COUNT(*) AS empatados
FROM pedido
WHERE fecha = '2026-03-17'
  AND estado IN ('pendiente', 'en taller');

-- @e9e
SELECT nombre, precio FROM producto WHERE precio > 5.000;

-- @e9e_bien
SELECT nombre, precio FROM producto WHERE precio > 5000;
