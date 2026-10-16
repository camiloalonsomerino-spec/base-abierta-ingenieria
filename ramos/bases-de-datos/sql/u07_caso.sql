-- Unidad 7 · Álgebra relacional · caso integrador: cinco preguntas del dueño de Estampa Sur
-- Solo consulta, no modifica nada:  sqlite3 datos/estampa_sur.db < sql/u07_caso.sql
-- Cada consulta es la traducción de una expresión de álgebra relacional (unidad 7, sección 11).

-- @c1
SELECT nombre, precio FROM producto WHERE precio > 4000;

-- @c2
SELECT c.id_cliente, c.nombre
FROM cliente c
WHERE c.id_cliente IN (SELECT id_cliente FROM cliente
                       EXCEPT
                       SELECT id_cliente FROM pedido);

-- @c3
SELECT pv.nombre
FROM proveedor pv
WHERE pv.id_proveedor IN (
    SELECT s.id_proveedor FROM suministra s JOIN producto pr ON pr.id_producto = s.id_producto
    WHERE pr.nombre = 'poleras básicas'
    INTERSECT
    SELECT s.id_proveedor FROM suministra s JOIN producto pr ON pr.id_producto = s.id_producto
    WHERE pr.nombre = 'gorros');

-- @c4mal
SELECT COUNT(*) FROM pedido NATURAL JOIN cliente NATURAL JOIN tienda WHERE estado = 'pendiente';

-- @c4
SELECT p.id_pedido, c.nombre AS cliente, t.nombre AS tienda
FROM pedido p
JOIN cliente c ON c.id_cliente = p.id_cliente
JOIN tienda t  ON t.id_tienda = c.id_tienda
WHERE p.estado = 'pendiente'
ORDER BY p.id_pedido;

-- @c5
SELECT c.id_cliente, c.nombre, c.tipo
FROM cliente c
WHERE NOT EXISTS (
    SELECT * FROM producto pr
    WHERE NOT EXISTS (
        SELECT * FROM pedido p JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
        WHERE p.id_cliente = c.id_cliente AND d.id_producto = pr.id_producto))
ORDER BY c.id_cliente;