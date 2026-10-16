-- Unidad 11 · Subconsultas y vistas · consultas sobre la base del caso (Estampa Sur)
-- Correr sobre una COPIA de datos/estampa_sur.db:   sqlite3 copia.db < u11_caso.sql
-- (el script crea vistas; la base original no se toca).
-- Cada marca «-- @tipo nombre» separa un bloque que el verificador ejecuta y busca en la unidad.

-- ============================================================ Caso integrador
-- @consulta c_sobre_promedio
SELECT COUNT(*) FROM (
    SELECT p.id_cliente, SUM(d.cantidad * d.precio_unit) AS total
    FROM pedido p JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
    GROUP BY p.id_cliente) x
WHERE x.total > (SELECT AVG(t) FROM (
    SELECT SUM(d.cantidad * d.precio_unit) AS t
    FROM pedido p JOIN detalle_pedido d ON d.id_pedido = p.id_pedido GROUP BY p.id_cliente) y);

-- @consulta c_promedio
SELECT ROUND(AVG(t), 2) AS promedio, COUNT(*) AS clientes
FROM (SELECT SUM(d.cantidad * d.precio_unit) AS t
      FROM pedido p JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
      GROUP BY p.id_cliente);

-- @consulta c_cte
WITH total_cliente AS (
    SELECT p.id_cliente, SUM(d.cantidad * d.precio_unit) AS total
    FROM pedido p
    JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
    GROUP BY p.id_cliente
)
SELECT COUNT(*) AS clientes
FROM total_cliente
WHERE total > (SELECT AVG(total) FROM total_cliente);

-- @consulta c_barato
SELECT pr.nombre AS producto, pv.nombre AS proveedor, s.costo_unidad
FROM suministra s
JOIN producto pr  ON pr.id_producto = s.id_producto
JOIN proveedor pv ON pv.id_proveedor = s.id_proveedor
WHERE s.costo_unidad = (SELECT MIN(s2.costo_unidad) FROM suministra s2 WHERE s2.id_producto = s.id_producto)
ORDER BY pr.id_producto;

-- @consulta c_barato_sin_correlacion
SELECT pr.nombre AS producto, pv.nombre AS proveedor, s.costo_unidad
FROM suministra s
JOIN producto pr  ON pr.id_producto = s.id_producto
JOIN proveedor pv ON pv.id_proveedor = s.id_proveedor
WHERE s.costo_unidad = (SELECT MIN(s2.costo_unidad) FROM suministra s2)
ORDER BY pr.id_producto;

-- @consulta c_semana6
SELECT pr.nombre, o.lote, o.lote * pr.seg_estampado / 3600.0 AS horas_estampado
FROM orden_produccion o JOIN producto pr ON pr.id_producto = o.id_producto
WHERE o.semana = 6 ORDER BY o.id_producto;

-- @consulta c_semana6_total
SELECT SUM(o.lote) AS prendas, SUM(o.lote * pr.seg_estampado) / 3600.0 AS horas_estampado
FROM orden_produccion o JOIN producto pr ON pr.id_producto = o.id_producto
WHERE o.semana = 6;

-- @ejecuta c_vista
CREATE VIEW v_ventas_tienda AS
SELECT t.nombre AS tienda, SUM(d.cantidad * d.precio_unit) AS ventas
FROM detalle_pedido d
JOIN pedido p  ON p.id_pedido = d.id_pedido
JOIN cliente c ON c.id_cliente = p.id_cliente
JOIN tienda t  ON t.id_tienda = c.id_tienda
GROUP BY t.nombre;

-- @consulta c_vista_usa
SELECT tienda, ventas FROM v_ventas_tienda ORDER BY ventas DESC;

-- @consulta c_vista_filtra
SELECT tienda, ventas
FROM v_ventas_tienda
WHERE ventas > (SELECT AVG(ventas) FROM v_ventas_tienda)
ORDER BY ventas DESC;

-- ============================================================ Pautas con la base del caso
-- @consulta p1_promedio
SELECT AVG(precio) AS precio_promedio FROM producto;

-- @consulta p1_sobre
SELECT nombre, precio
FROM producto
WHERE precio > (SELECT AVG(precio) FROM producto)
ORDER BY precio DESC;

-- @consulta p2_in
SELECT COUNT(*) AS clientes
FROM cliente
WHERE id_cliente IN (SELECT p.id_cliente
                     FROM pedido p
                     JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
                     WHERE d.id_producto = 5);

-- @consulta p2_not_in
SELECT COUNT(*) AS clientes
FROM cliente
WHERE id_cliente NOT IN (SELECT p.id_cliente
                         FROM pedido p
                         JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
                         WHERE d.id_producto = 5);

-- @consulta p5_mayor_por_tipo
WITH total_pedido AS (
    SELECT p.id_pedido, c.tipo, SUM(d.cantidad * d.precio_unit) AS total
    FROM pedido p
    JOIN cliente c        ON c.id_cliente = p.id_cliente
    JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
    GROUP BY p.id_pedido, c.tipo
)
SELECT tipo, id_pedido, total
FROM total_pedido t
WHERE total = (SELECT MAX(t2.total) FROM total_pedido t2 WHERE t2.tipo = t.tipo)
ORDER BY total DESC;

-- @falla p6_error
SELECT id_pedido
FROM detalle_pedido
WHERE SUM(cantidad * precio_unit) > AVG(SUM(cantidad * precio_unit))
GROUP BY id_pedido;

-- @consulta p6_cte
WITH total_pedido AS (
    SELECT id_pedido, SUM(cantidad * precio_unit) AS total
    FROM detalle_pedido
    GROUP BY id_pedido
)
SELECT COUNT(*) AS pedidos, ROUND((SELECT AVG(total) FROM total_pedido), 2) AS promedio
FROM total_pedido
WHERE total > (SELECT AVG(total) FROM total_pedido);

-- @consulta p6_having
SELECT COUNT(*) AS pedidos
FROM (SELECT id_pedido
      FROM detalle_pedido
      GROUP BY id_pedido
      HAVING SUM(cantidad * precio_unit) > (SELECT AVG(t.total)
                                             FROM (SELECT SUM(cantidad * precio_unit) AS total
                                                   FROM detalle_pedido
                                                   GROUP BY id_pedido) AS t));

-- @ejecuta p7_vista
CREATE VIEW v_ventas_cliente AS
SELECT c.id_cliente, c.nombre, c.tipo, SUM(d.cantidad * d.precio_unit) AS total
FROM cliente c
JOIN pedido p         ON p.id_cliente = c.id_cliente
JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
GROUP BY c.id_cliente, c.nombre, c.tipo;

-- @consulta p7_grandes
SELECT nombre, tipo, total
FROM v_ventas_cliente
WHERE total > 3000000
ORDER BY total DESC;

-- @consulta p7_filas
SELECT COUNT(*) AS filas FROM v_ventas_cliente;

-- @consulta p10_compra
SELECT pr.nombre, pv.nombre AS proveedor, o.lote, s.costo_unidad, o.lote * s.costo_unidad AS costo_lote
FROM orden_produccion o
JOIN producto pr  ON pr.id_producto = o.id_producto
JOIN suministra s ON s.id_producto = o.id_producto
JOIN proveedor pv ON pv.id_proveedor = s.id_proveedor
WHERE o.semana = 6
  AND s.costo_unidad = (SELECT MIN(s2.costo_unidad) FROM suministra s2 WHERE s2.id_producto = s.id_producto)
ORDER BY o.id_producto;

-- @consulta p10_por_proveedor
WITH compra AS (
    SELECT s.id_proveedor, o.lote * s.costo_unidad AS costo_lote
    FROM orden_produccion o
    JOIN suministra s ON s.id_producto = o.id_producto
    WHERE o.semana = 6
      AND s.costo_unidad = (SELECT MIN(s2.costo_unidad) FROM suministra s2 WHERE s2.id_producto = s.id_producto)
)
SELECT pv.nombre AS proveedor, SUM(c.costo_lote) AS total
FROM compra c
JOIN proveedor pv ON pv.id_proveedor = c.id_proveedor
GROUP BY pv.nombre
ORDER BY total DESC;

-- @consulta p10_ahorro
SELECT SUM(o.lote * (SELECT MIN(s.costo_unidad) FROM suministra s WHERE s.id_producto = o.id_producto)) AS al_mas_barato,
       SUM(o.lote * (SELECT MAX(s.costo_unidad) FROM suministra s WHERE s.id_producto = o.id_producto)) AS al_mas_caro
FROM orden_produccion o
WHERE o.semana = 6;
