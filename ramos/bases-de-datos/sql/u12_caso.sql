-- Unidad 12 · Transacciones e índices · la base del caso (Estampa Sur)
-- Correr sobre una COPIA de datos/estampa_sur.db, en orden y en una sola sesión:
--     sqlite3 copia.db < u12_caso.sql
-- Registra un pedido, intenta otro que falla y crea índices: la base original no se toca.
-- Cada marca «-- @tipo nombre» separa un bloque que el verificador ejecuta y busca en la unidad.

-- @ejecuta c_fk
PRAGMA foreign_keys = ON;

-- @ejecuta c_vista
CREATE VIEW v_ventas_tienda AS
SELECT t.nombre AS tienda, SUM(d.cantidad * d.precio_unit) AS ventas
FROM detalle_pedido d
JOIN pedido p  ON p.id_pedido = d.id_pedido
JOIN cliente c ON c.id_cliente = p.id_cliente
JOIN tienda t  ON t.id_tienda = c.id_tienda
GROUP BY t.nombre;

-- @consulta c_antes
SELECT (SELECT COUNT(*) FROM pedido) AS pedidos,
       (SELECT COUNT(*) FROM detalle_pedido) AS lineas,
       (SELECT COUNT(*) FROM pedido WHERE id_cliente = 27) AS pedidos_cliente_27;

-- ============================================================ El pedido 121, todo o nada
-- @ejecuta c121_begin
BEGIN;

-- @ejecuta c121_pedido
INSERT INTO pedido (id_pedido, id_cliente, fecha, estado) VALUES (121, 27, '2026-04-02', 'pendiente');

-- @ejecuta c121_linea1
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unit)
SELECT 121, id_producto, 4, precio FROM producto WHERE id_producto = 1;

-- @ejecuta c121_linea2
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unit)
SELECT 121, id_producto, 2, precio FROM producto WHERE id_producto = 2;

-- @ejecuta c121_commit
COMMIT;

-- @consulta c121_detalle
SELECT id_pedido, id_producto, cantidad, precio_unit, cantidad * precio_unit AS monto
FROM detalle_pedido
WHERE id_pedido = 121;

-- @consulta c121_ventas
SELECT tienda, ventas FROM v_ventas_tienda ORDER BY ventas DESC;

-- ============================================================ El pedido 122 falla a la mitad
-- @ejecuta c122_begin
BEGIN;

-- @ejecuta c122_pedido
INSERT INTO pedido (id_pedido, id_cliente, fecha, estado) VALUES (122, 28, '2026-04-03', 'pendiente');

-- @ejecuta c122_linea1
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unit)
SELECT 122, id_producto, 3, precio FROM producto WHERE id_producto = 4;

-- @falla c122_linea2
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unit)
SELECT 122, id_producto, 0, precio FROM producto WHERE id_producto = 5;

-- @consulta c122_adentro
SELECT (SELECT COUNT(*) FROM pedido WHERE id_pedido = 122) AS pedido_122,
       (SELECT COUNT(*) FROM detalle_pedido WHERE id_pedido = 122) AS lineas_122;

-- @ejecuta c122_rollback
ROLLBACK;

-- @consulta c122_despues
SELECT (SELECT COUNT(*) FROM pedido) AS pedidos,
       (SELECT COUNT(*) FROM detalle_pedido) AS lineas,
       (SELECT COUNT(*) FROM pedido WHERE id_pedido = 122) AS pedido_122;

-- ============================================================ Índices para las ventas de una tienda
-- @plan c_plan_todas
EXPLAIN QUERY PLAN
SELECT tienda, ventas FROM v_ventas_tienda ORDER BY ventas DESC;

-- @plan c_plan_centro_antes
EXPLAIN QUERY PLAN
SELECT tienda, ventas FROM v_ventas_tienda WHERE tienda = 'Centro';

-- @ejecuta c_idx_cliente
CREATE INDEX idx_cliente_tienda ON cliente(id_tienda);

-- @plan c_plan_centro_uno
EXPLAIN QUERY PLAN
SELECT tienda, ventas FROM v_ventas_tienda WHERE tienda = 'Centro';

-- @ejecuta c_idx_pedido
CREATE INDEX idx_pedido_cliente ON pedido(id_cliente);

-- @plan c_plan_centro_despues
EXPLAIN QUERY PLAN
SELECT tienda, ventas FROM v_ventas_tienda WHERE tienda = 'Centro';

-- @plan c_plan_todas_despues
EXPLAIN QUERY PLAN
SELECT tienda, ventas FROM v_ventas_tienda ORDER BY ventas DESC;

-- @consulta c_centro
SELECT tienda, ventas FROM v_ventas_tienda WHERE tienda = 'Centro';

-- ============================================================ El mismo registro desde Python
-- @python registrar_falla
-- (estas dos marcas llaman a registrar_pedido de u12_programa.py sobre la misma copia)

-- @python registrar_ok

-- @consulta c_final
SELECT (SELECT COUNT(*) FROM pedido) AS pedidos,
       (SELECT COUNT(*) FROM detalle_pedido) AS lineas,
       (SELECT COUNT(*) FROM cliente c
        WHERE NOT EXISTS (SELECT 1 FROM pedido p WHERE p.id_cliente = c.id_cliente)) AS clientes_sin_pedidos;

-- @consulta c_final_ventas
SELECT tienda, ventas FROM v_ventas_tienda ORDER BY ventas DESC;

-- ============================================================ Pautas
-- @plan p3_por_pedido
EXPLAIN QUERY PLAN
SELECT * FROM detalle_pedido WHERE id_pedido = 40;

-- @plan p3_por_producto
EXPLAIN QUERY PLAN
SELECT * FROM detalle_pedido WHERE id_producto = 3;

-- @plan p6_estado
EXPLAIN QUERY PLAN
SELECT COUNT(*) FROM pedido WHERE estado = 'pendiente';

-- @plan p6_cliente
EXPLAIN QUERY PLAN
SELECT * FROM pedido WHERE id_cliente = 12;

-- @consulta p6_cuantos
SELECT estado, COUNT(*) AS pedidos FROM pedido GROUP BY estado ORDER BY pedidos DESC;

-- @plan p10_antes
EXPLAIN QUERY PLAN
SELECT SUM(d.cantidad * d.precio_unit) AS ventas
FROM detalle_pedido d
JOIN pedido p ON p.id_pedido = d.id_pedido
WHERE p.fecha BETWEEN '2026-03-16' AND '2026-03-31';

-- @ejecuta p10_idx
CREATE INDEX idx_pedido_fecha ON pedido(fecha);

-- @plan p10_despues
EXPLAIN QUERY PLAN
SELECT SUM(d.cantidad * d.precio_unit) AS ventas
FROM detalle_pedido d
JOIN pedido p ON p.id_pedido = d.id_pedido
WHERE p.fecha BETWEEN '2026-03-16' AND '2026-03-31';

-- @plan p10_funcion
EXPLAIN QUERY PLAN
SELECT SUM(d.cantidad * d.precio_unit) AS ventas
FROM detalle_pedido d
JOIN pedido p ON p.id_pedido = d.id_pedido
WHERE substr(p.fecha, 9, 2) >= '16';

-- @consulta p10_ventas
SELECT SUM(d.cantidad * d.precio_unit) AS ventas
FROM detalle_pedido d
JOIN pedido p ON p.id_pedido = d.id_pedido
WHERE p.fecha BETWEEN '2026-03-16' AND '2026-03-31';

-- @consulta p10_indices
SELECT name AS indice, tbl_name AS tabla
FROM sqlite_master
WHERE type = 'index'
ORDER BY tbl_name, name;
