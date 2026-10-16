-- Unidad 3 · Cardinalidad, participación, entidades débiles y jerarquías
-- Base abierta de ingeniería · Bases de Datos
--
-- Se corre sobre la base del caso: datos/estampa_sur.db (la crea verificacion/caso_estampa_sur_bd.py).
--   sqlite3 datos/estampa_sur.db < sql/u03_cardinalidad.sql
-- Mide en los datos el par (mínimo, máximo) de cada lado de las relaciones del diagrama. Los datos
-- pueden desmentir un par declarado, nunca probarlo.
-- Corre igual en MySQL: el alias de la subconsulta (AS x) es obligatorio allá.

-- @consulta c1_productos_por_pedido
SELECT MIN(n) AS minimo, MAX(n) AS maximo
FROM (SELECT p.id_pedido, COUNT(d.id_producto) AS n
      FROM pedido p
      LEFT JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
      GROUP BY p.id_pedido) AS x;

-- @consulta c2_pedidos_por_producto
SELECT MIN(n) AS minimo, MAX(n) AS maximo
FROM (SELECT pr.id_producto, COUNT(d.id_pedido) AS n
      FROM producto pr
      LEFT JOIN detalle_pedido d ON d.id_producto = pr.id_producto
      GROUP BY pr.id_producto) AS x;

-- @consulta c3_proveedores_por_producto
SELECT MIN(n) AS minimo, MAX(n) AS maximo
FROM (SELECT pr.id_producto, COUNT(s.id_proveedor) AS n
      FROM producto pr
      LEFT JOIN suministra s ON s.id_producto = pr.id_producto
      GROUP BY pr.id_producto) AS x;

-- @consulta c4_productos_por_proveedor
SELECT MIN(n) AS minimo, MAX(n) AS maximo
FROM (SELECT pv.id_proveedor, COUNT(s.id_producto) AS n
      FROM proveedor pv
      LEFT JOIN suministra s ON s.id_proveedor = pv.id_proveedor
      GROUP BY pv.id_proveedor) AS x;

-- @consulta c5_pedidos_por_cliente
SELECT MIN(n) AS minimo, MAX(n) AS maximo
FROM (SELECT c.id_cliente, COUNT(p.id_pedido) AS n
      FROM cliente c
      LEFT JOIN pedido p ON p.id_cliente = c.id_cliente
      GROUP BY c.id_cliente) AS x;

-- @consulta c6_pedidos_segun_productos
SELECT n AS productos, COUNT(*) AS pedidos
FROM (SELECT d.id_pedido, COUNT(*) AS n
      FROM detalle_pedido d
      GROUP BY d.id_pedido) AS x
GROUP BY n
ORDER BY n;

-- @consulta c7_precio_distinto_al_de_lista
SELECT COUNT(*) AS lineas_con_otro_precio
FROM detalle_pedido d
JOIN producto pr ON pr.id_producto = d.id_producto
WHERE d.precio_unit <> pr.precio;

-- @consulta c8_orden_repetida
SELECT COUNT(*) AS pares_repetidos
FROM (SELECT id_producto, semana
      FROM orden_produccion
      GROUP BY id_producto, semana
      HAVING COUNT(*) > 1) AS x;

-- @consulta c9_clientes_por_tipo
SELECT tipo, COUNT(*) AS clientes
FROM cliente
GROUP BY tipo
ORDER BY tipo;

-- Ejercicio 3.8

-- @consulta e38_clientes_por_tienda
SELECT MIN(n) AS minimo, MAX(n) AS maximo
FROM (SELECT t.id_tienda, COUNT(c.id_cliente) AS n
      FROM tienda t
      LEFT JOIN cliente c ON c.id_tienda = t.id_tienda
      GROUP BY t.id_tienda) AS x;

-- @consulta e38_ordenes_por_producto
SELECT MIN(n) AS minimo, MAX(n) AS maximo
FROM (SELECT pr.id_producto, COUNT(o.id_orden) AS n
      FROM producto pr
      LEFT JOIN orden_produccion o ON o.id_producto = pr.id_producto
      GROUP BY pr.id_producto) AS x;
