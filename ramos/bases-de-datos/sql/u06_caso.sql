-- Unidad 6 · Caso integrador · la planilla única de pedidos de Estampa Sur y su normalización
-- Se corre sobre una COPIA de datos/estampa_sur.db (el verificador la copia en memoria).
-- Primero se arma la planilla que el taller llevaba antes de tener base: una fila por línea de pedido.
CREATE TABLE planilla AS
SELECT d.id_pedido, p.fecha, p.estado,
       c.id_cliente, c.nombre AS cliente, c.tipo,
       t.id_tienda, t.nombre AS tienda, t.comuna,
       pr.id_producto, pr.nombre AS producto, pr.precio, pr.costo_var, pr.seg_estampado,
       d.cantidad, d.precio_unit
FROM detalle_pedido d
JOIN pedido p    ON p.id_pedido = d.id_pedido
JOIN cliente c   ON c.id_cliente = p.id_cliente
JOIN tienda t    ON t.id_tienda = c.id_tienda
JOIN producto pr ON pr.id_producto = d.id_producto;

-- @tamano
SELECT COUNT(*) AS filas, (SELECT COUNT(*) FROM pragma_table_info('planilla')) AS columnas FROM planilla;
-- @muestra las tres líneas del pedido 3 (9 de las 16 columnas)
SELECT id_pedido, fecha, cliente, tienda, comuna, producto, precio, cantidad, precio_unit
FROM planilla WHERE id_pedido = 3;
-- @repetidos cuántas veces está escrito cada hecho
SELECT 'fecha y estado de cada pedido' AS hecho, COUNT(*) AS veces_escrito, COUNT(DISTINCT id_pedido) AS hechos FROM planilla
UNION ALL
SELECT 'tipo y tienda de cada cliente', COUNT(*), COUNT(DISTINCT id_cliente) FROM planilla
UNION ALL
SELECT 'comuna de cada tienda', COUNT(*), COUNT(DISTINCT id_tienda) FROM planilla
UNION ALL
SELECT 'precio y costo de cada producto', COUNT(*), COUNT(DISTINCT id_producto) FROM planilla;
-- @dfs las dependencias en los datos (1 = se cumple)
SELECT 'id_pedido → fecha, estado, id_cliente' AS dependencia,
       MAX(n) AS maximo FROM (SELECT COUNT(DISTINCT fecha || '|' || estado || '|' || id_cliente) AS n FROM planilla GROUP BY id_pedido)
UNION ALL
SELECT 'id_cliente → cliente, tipo, id_tienda',
       MAX(n) FROM (SELECT COUNT(DISTINCT cliente || '|' || tipo || '|' || id_tienda) AS n FROM planilla GROUP BY id_cliente)
UNION ALL
SELECT 'id_tienda → tienda, comuna',
       MAX(n) FROM (SELECT COUNT(DISTINCT tienda || '|' || comuna) AS n FROM planilla GROUP BY id_tienda)
UNION ALL
SELECT 'id_producto → producto, precio, costo_var, seg_estampado',
       MAX(n) FROM (SELECT COUNT(DISTINCT producto || '|' || precio || '|' || costo_var || '|' || seg_estampado) AS n FROM planilla GROUP BY id_producto)
UNION ALL
SELECT 'id_producto → precio_unit',
       MAX(n) FROM (SELECT COUNT(DISTINCT precio_unit) AS n FROM planilla GROUP BY id_producto);
-- @a_actualizacion si sube el precio de los gorros, filas que hay que corregir
SELECT COUNT(*) AS filas FROM planilla WHERE producto = 'gorros';
-- @a_insercion clientes de la base que no pueden estar en la planilla (no tienen pedidos)
SELECT COUNT(*) AS clientes FROM cliente WHERE id_cliente NOT IN (SELECT id_cliente FROM planilla);
-- @a_borrado clientes que desaparecen si se anula su único pedido
SELECT id_cliente, cliente, COUNT(DISTINCT id_pedido) AS pedidos
FROM planilla
GROUP BY id_cliente, cliente
HAVING COUNT(DISTINCT id_pedido) = 1;

-- La descomposición: cada tabla nueva sale de la planilla con SELECT DISTINCT
CREATE TABLE n_tienda AS SELECT DISTINCT id_tienda, tienda AS nombre, comuna FROM planilla;
CREATE TABLE n_producto AS SELECT DISTINCT id_producto, producto AS nombre, precio, costo_var, seg_estampado FROM planilla;
CREATE TABLE n_cliente AS SELECT DISTINCT id_cliente, cliente AS nombre, tipo, id_tienda FROM planilla;
CREATE TABLE n_pedido AS SELECT DISTINCT id_pedido, id_cliente, fecha, estado FROM planilla;
CREATE TABLE n_detalle AS SELECT id_pedido, id_producto, cantidad, precio_unit FROM planilla;

-- @contra_la_base cada tabla obtenida contra la tabla del esquema del caso
SELECT 'tienda' AS tabla, (SELECT COUNT(*) FROM n_tienda) AS desde_planilla, (SELECT COUNT(*) FROM tienda) AS en_la_base,
       (SELECT COUNT(*) FROM (SELECT * FROM n_tienda EXCEPT SELECT * FROM tienda)) AS distintas
UNION ALL
SELECT 'producto', (SELECT COUNT(*) FROM n_producto), (SELECT COUNT(*) FROM producto),
       (SELECT COUNT(*) FROM (SELECT * FROM n_producto EXCEPT SELECT * FROM producto))
UNION ALL
SELECT 'cliente', (SELECT COUNT(*) FROM n_cliente), (SELECT COUNT(*) FROM cliente),
       (SELECT COUNT(*) FROM (SELECT * FROM n_cliente EXCEPT SELECT * FROM cliente))
UNION ALL
SELECT 'pedido', (SELECT COUNT(*) FROM n_pedido), (SELECT COUNT(*) FROM pedido),
       (SELECT COUNT(*) FROM (SELECT * FROM n_pedido EXCEPT SELECT * FROM pedido))
UNION ALL
SELECT 'detalle_pedido', (SELECT COUNT(*) FROM n_detalle), (SELECT COUNT(*) FROM detalle_pedido),
       (SELECT COUNT(*) FROM (SELECT * FROM n_detalle EXCEPT SELECT * FROM detalle_pedido));
-- @reconstruir el join de las cinco tablas vuelve a dar la planilla
SELECT
  (SELECT COUNT(*) FROM (
     SELECT d.id_pedido, p.fecha, p.estado, c.id_cliente, c.nombre, c.tipo, t.id_tienda, t.nombre, t.comuna,
            pr.id_producto, pr.nombre, pr.precio, pr.costo_var, pr.seg_estampado, d.cantidad, d.precio_unit
     FROM n_detalle d
     JOIN n_pedido p    ON p.id_pedido = d.id_pedido
     JOIN n_cliente c   ON c.id_cliente = p.id_cliente
     JOIN n_tienda t    ON t.id_tienda = c.id_tienda
     JOIN n_producto pr ON pr.id_producto = d.id_producto)) AS filas_join,
  (SELECT COUNT(*) FROM (
     SELECT * FROM planilla
     EXCEPT
     SELECT d.id_pedido, p.fecha, p.estado, c.id_cliente, c.nombre, c.tipo, t.id_tienda, t.nombre, t.comuna,
            pr.id_producto, pr.nombre, pr.precio, pr.costo_var, pr.seg_estampado, d.cantidad, d.precio_unit
     FROM n_detalle d
     JOIN n_pedido p    ON p.id_pedido = d.id_pedido
     JOIN n_cliente c   ON c.id_cliente = p.id_cliente
     JOIN n_tienda t    ON t.id_tienda = c.id_tienda
     JOIN n_producto pr ON pr.id_producto = d.id_producto)) AS faltan,
  (SELECT COUNT(*) FROM (
     SELECT d.id_pedido, p.fecha, p.estado, c.id_cliente, c.nombre, c.tipo, t.id_tienda, t.nombre, t.comuna,
            pr.id_producto, pr.nombre, pr.precio, pr.costo_var, pr.seg_estampado, d.cantidad, d.precio_unit
     FROM n_detalle d
     JOIN n_pedido p    ON p.id_pedido = d.id_pedido
     JOIN n_cliente c   ON c.id_cliente = p.id_cliente
     JOIN n_tienda t    ON t.id_tienda = c.id_tienda
     JOIN n_producto pr ON pr.id_producto = d.id_producto
     EXCEPT
     SELECT * FROM planilla)) AS sobran;
