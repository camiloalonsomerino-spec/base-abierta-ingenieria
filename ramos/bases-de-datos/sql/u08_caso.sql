-- Unidad 8 · SQL para crear y modificar · caso integrador: Estampa Sur carga la primera semana de abril
-- y corrige precios. MODIFICA la base: córrelo sobre una COPIA, nunca sobre datos/estampa_sur.db.
--   Windows:      copy datos\estampa_sur.db datos\estampa_sur_copia.db
--   macOS/Linux:  cp datos/estampa_sur.db datos/estampa_sur_copia.db
--   sqlite3 datos/estampa_sur_copia.db < sql/u08_caso.sql
-- Algunas instrucciones FALLAN a propósito (las claves que empiezan con «falla_»).

-- @inicio
PRAGMA foreign_keys = ON;
SELECT COUNT(*) FROM pedido;

-- @semana_pedidos
INSERT INTO pedido (id_pedido, id_cliente, fecha, estado) VALUES
    (121, 27, '2026-04-01', 'pendiente'),
    (122,  3, '2026-04-01', 'en taller'),
    (123, 12, '2026-04-02', 'en taller'),
    (124, 29, '2026-04-03', 'pendiente'),
    (125,  8, '2026-04-06', 'pendiente'),
    (126, 21, '2026-04-07', 'pendiente');
SELECT changes();

-- @semana_detalle
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unit) VALUES
    (121, 1,  4, 3990),
    (121, 5,  2, 3190),
    (122, 2, 35, 9890),
    (123, 3, 60, 6290),
    (123, 4, 60, 2490),
    (124, 2,  3, 9980),
    (125, 4, 25, 2490),
    (126, 1,  2, 3990),
    (126, 5,  1, 3190);
SELECT COUNT(*) FROM detalle_pedido;

-- @falla_cliente
INSERT INTO pedido VALUES (127, 31, '2026-04-07', 'pendiente');

-- @falla_estado
INSERT INTO pedido VALUES (127, 5, '2026-04-07', 'despachado');

-- @falla_cantidad
INSERT INTO detalle_pedido VALUES (126, 3, 0, 6290);

-- @falla_repetido
INSERT INTO detalle_pedido VALUES (126, 1, 3, 3990);

-- @sin_pragma
PRAGMA foreign_keys = OFF;
INSERT INTO pedido VALUES (127, 31, '2026-04-07', 'pendiente');
SELECT changes();

-- @limpiar
DELETE FROM pedido WHERE id_pedido = 127;
PRAGMA foreign_keys = ON;
SELECT changes();

-- @lineas
SELECT d.id_pedido, pr.nombre, d.cantidad, d.precio_unit, pr.precio
FROM detalle_pedido d JOIN producto pr ON pr.id_producto = d.id_producto
WHERE d.id_pedido > 120
ORDER BY d.id_pedido, d.id_producto;

-- @correccion
UPDATE detalle_pedido
SET precio_unit = 9890
WHERE id_pedido = 124 AND id_producto = 2;
SELECT changes();

-- @total_semana
SELECT SUM(d.cantidad * d.precio_unit)
FROM detalle_pedido d JOIN pedido p ON p.id_pedido = d.id_pedido
WHERE p.fecha BETWEEN '2026-04-01' AND '2026-04-07';

-- @marzo_antes
SELECT SUM(d.cantidad * d.precio_unit)
FROM detalle_pedido d JOIN pedido p ON p.id_pedido = d.id_pedido
WHERE p.fecha < '2026-04-01';

-- @lista_precios
UPDATE producto
SET precio = 3390
WHERE id_producto = 5;
SELECT changes();

-- @marzo_despues
SELECT SUM(d.cantidad * d.precio_unit)
FROM detalle_pedido d JOIN pedido p ON p.id_pedido = d.id_pedido
WHERE p.fecha < '2026-04-01';

-- @sin_where
BEGIN;
UPDATE producto SET precio = 3390;
SELECT changes();

-- @deshacer
ROLLBACK;
SELECT id_producto, nombre, precio FROM producto;

-- @sin_pedidos
SELECT COUNT(*) FROM cliente
WHERE id_cliente NOT IN (SELECT id_cliente FROM pedido);
