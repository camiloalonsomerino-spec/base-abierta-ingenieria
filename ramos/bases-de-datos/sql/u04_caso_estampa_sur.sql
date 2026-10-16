-- Unidad 4 · Caso integrador: lo que el esquema de Estampa Sur garantiza y lo que no
-- Base abierta de ingeniería · Bases de Datos
--
-- Las dos primeras consultas se pueden correr sobre datos/estampa_sur.db. El resto MODIFICA la base:
-- córrelo sobre una copia (el verificador lo hace en una copia en memoria).
--   copy datos\estampa_sur.db copia.db
--   sqlite3 copia.db < sql/u04_caso_estampa_sur.sql
PRAGMA foreign_keys = ON;

-- @consulta k1_pedidos_sin_detalle
SELECT COUNT(*) AS pedidos_sin_detalle
FROM pedido p
WHERE NOT EXISTS (SELECT 1 FROM detalle_pedido d WHERE d.id_pedido = p.id_pedido);

-- @consulta k2_productos_sin_proveedor
SELECT COUNT(*) AS productos_sin_proveedor
FROM producto pr
WHERE NOT EXISTS (SELECT 1 FROM suministra s WHERE s.id_producto = pr.id_producto);

-- @datos k3_pedido_vacio
INSERT INTO pedido VALUES (121, 5, '2026-03-31', 'pendiente');

-- @consulta k4_pedidos_sin_detalle_despues
SELECT COUNT(*) AS pedidos_sin_detalle
FROM pedido p
WHERE NOT EXISTS (SELECT 1 FROM detalle_pedido d WHERE d.id_pedido = p.id_pedido);

-- @error k5_producto_inexistente
INSERT INTO detalle_pedido VALUES (121, 9, 10, 3990);

-- @error k6_pedido_sin_cliente
INSERT INTO pedido VALUES (122, NULL, '2026-03-31', 'pendiente');
