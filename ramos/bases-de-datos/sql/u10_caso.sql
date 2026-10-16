-- Unidad 10 · consultas con varias tablas sobre la base del caso
-- Base abierta de ingeniería · Bases de Datos
--
-- Corre sobre la base de Estampa Sur que crea verificacion/caso_estampa_sur_bd.py:
--   sqlite3 ../datos/estampa_sur.db < u10_caso.sql
-- Cada consulta lleva una marca «-- @nombre» que usa el verificador (verificacion/u10_joins.py).

-- @u10_ventas_por_tienda
SELECT t.nombre, SUM(d.cantidad * d.precio_unit) AS ventas
FROM detalle_pedido d
JOIN pedido p   ON p.id_pedido = d.id_pedido
JOIN cliente c  ON c.id_cliente = p.id_cliente
JOIN tienda t   ON t.id_tienda = c.id_tienda
GROUP BY t.nombre ORDER BY ventas DESC;

-- @u10_unidades_por_producto
SELECT pr.nombre, SUM(d.cantidad) AS unidades
FROM detalle_pedido d JOIN producto pr ON pr.id_producto = d.id_producto
GROUP BY pr.nombre ORDER BY unidades DESC;

-- @u10_margen_por_tipo_cliente
SELECT c.tipo, SUM(d.cantidad * (d.precio_unit - pr.costo_var)) AS margen
FROM detalle_pedido d
JOIN pedido p    ON p.id_pedido = d.id_pedido
JOIN cliente c   ON c.id_cliente = p.id_cliente
JOIN producto pr ON pr.id_producto = d.id_producto
GROUP BY c.tipo HAVING SUM(d.cantidad) > 100 ORDER BY margen DESC;

-- @caso_unidades_por_tipo
SELECT c.tipo, SUM(d.cantidad) AS unidades
FROM detalle_pedido d
JOIN pedido p  ON p.id_pedido = d.id_pedido
JOIN cliente c ON c.id_cliente = p.id_cliente
GROUP BY c.tipo
ORDER BY unidades DESC;

-- @u10_clientes_sin_pedidos
SELECT COUNT(*) FROM cliente c LEFT JOIN pedido p ON p.id_cliente = c.id_cliente
WHERE p.id_pedido IS NULL;

-- @caso_clientes_sin_pedidos_lista
SELECT c.nombre, c.tipo, t.nombre AS tienda
FROM cliente c
JOIN tienda t ON t.id_tienda = c.id_tienda
LEFT JOIN pedido p ON p.id_cliente = c.id_cliente
WHERE p.id_pedido IS NULL
ORDER BY c.id_cliente;

-- @caso_cartesiano
SELECT COUNT(*) AS filas FROM cliente, pedido;

-- Ejercicios sobre el caso

-- @e1c
SELECT COUNT(*) AS filas FROM cliente, tienda;

-- @e1d
SELECT COUNT(*) AS filas FROM cliente c, tienda t WHERE t.id_tienda = c.id_tienda;

-- @e2
SELECT pr.nombre AS producto, pv.nombre AS proveedor, s.costo_unidad
FROM suministra s
JOIN producto pr  ON pr.id_producto = s.id_producto
JOIN proveedor pv ON pv.id_proveedor = s.id_proveedor
ORDER BY pr.id_producto, s.costo_unidad;

-- @e3
SELECT estado, COUNT(*) AS pedidos
FROM pedido
GROUP BY estado
ORDER BY pedidos DESC;

-- @e4
SELECT pv.nombre AS proveedor, COUNT(s.id_producto) AS productos
FROM proveedor pv
LEFT JOIN suministra s ON s.id_proveedor = pv.id_proveedor
GROUP BY pv.id_proveedor, pv.nombre
ORDER BY productos DESC, proveedor;

-- @e4_mal
SELECT pv.nombre AS proveedor, COUNT(*) AS productos
FROM proveedor pv
LEFT JOIN suministra s ON s.id_proveedor = pv.id_proveedor
GROUP BY pv.id_proveedor, pv.nombre
ORDER BY productos DESC, proveedor;

-- @e5
SELECT o.semana, SUM(o.lote * pr.seg_estampado) / 3600.0 AS horas_estampado
FROM orden_produccion o
JOIN producto pr ON pr.id_producto = o.id_producto
GROUP BY o.semana
ORDER BY o.semana;

-- @e6
SELECT t.nombre AS tienda, COUNT(*) AS pedidos
FROM pedido p
JOIN cliente c ON c.id_cliente = p.id_cliente
JOIN tienda t  ON t.id_tienda = c.id_tienda
GROUP BY t.nombre
HAVING COUNT(*) > 20
ORDER BY pedidos DESC;

-- @e7
SELECT pr.nombre AS producto, SUM(d.cantidad * d.precio_unit) AS ventas_entregadas
FROM detalle_pedido d
JOIN pedido p    ON p.id_pedido = d.id_pedido
JOIN producto pr ON pr.id_producto = d.id_producto
WHERE p.estado = 'entregado'
GROUP BY pr.nombre
HAVING SUM(d.cantidad * d.precio_unit) > 3000000
ORDER BY ventas_entregadas DESC;

-- @e9_mal
SELECT c.tipo, COUNT(*) AS pedidos, SUM(d.cantidad) AS unidades
FROM pedido p
JOIN cliente c        ON c.id_cliente = p.id_cliente
JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
GROUP BY c.tipo
ORDER BY c.tipo;

-- @e9_bien
SELECT c.tipo, COUNT(DISTINCT p.id_pedido) AS pedidos, SUM(d.cantidad) AS unidades,
       ROUND(1.0 * SUM(d.cantidad) / COUNT(DISTINCT p.id_pedido), 1) AS unidades_por_pedido
FROM pedido p
JOIN cliente c        ON c.id_cliente = p.id_cliente
JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
GROUP BY c.tipo
ORDER BY c.tipo;

-- @e10
SELECT t.nombre AS tienda,
       COUNT(DISTINCT c.id_cliente) AS clientes,
       COUNT(DISTINCT p.id_cliente) AS compradores,
       COUNT(DISTINCT p.id_pedido) AS pedidos,
       COALESCE(SUM(d.cantidad * d.precio_unit), 0) AS ventas
FROM tienda t
LEFT JOIN cliente c        ON c.id_tienda = t.id_tienda
LEFT JOIN pedido p         ON p.id_cliente = c.id_cliente
LEFT JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
GROUP BY t.id_tienda, t.nombre
ORDER BY ventas DESC;
