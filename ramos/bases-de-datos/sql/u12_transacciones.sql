-- Unidad 12 · Transacciones, índices y la base dentro de un programa · base del ejemplo
-- Ventas y stock de una ferretería de Los Ángeles (datos inventados).
-- Correr en SQLite, en orden y en una sola sesión:   sqlite3 ferreteria.db < u12_transacciones.sql
-- Algunas sentencias fallan a propósito (se ve el mensaje y la sesión sigue).
-- Cada marca «-- @tipo nombre» separa un bloque: el verificador (verificacion/u12_transacciones.py)
-- lo ejecuta en orden y exige que el SQL y su resultado estén en la unidad.

-- @ejecuta fk
PRAGMA foreign_keys = ON;

-- @crear tablas
CREATE TABLE producto (
    id_producto INTEGER PRIMARY KEY,
    nombre      VARCHAR(40) NOT NULL,
    precio      INTEGER NOT NULL CHECK (precio > 0),
    stock       INTEGER NOT NULL CHECK (stock >= 0)
);
CREATE TABLE venta (
    id_venta INTEGER PRIMARY KEY,
    fecha    DATE NOT NULL,
    vendedor VARCHAR(30) NOT NULL
);
CREATE TABLE detalle_venta (
    id_venta    INTEGER NOT NULL REFERENCES venta(id_venta),
    id_producto INTEGER NOT NULL REFERENCES producto(id_producto),
    cantidad    INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unit INTEGER NOT NULL,
    PRIMARY KEY (id_venta, id_producto)
);

-- @datos carga
INSERT INTO producto VALUES
    (1, 'Tornillo volcanita 6x1 (caja 100)', 2990, 40), (2, 'Martillo carpintero 16 oz', 8490, 12),
    (3, 'Cinta aisladora', 1290, 60), (4, 'Brocha 2 pulgadas', 1890, 25),
    (5, 'Silicona transparente', 4590, 8), (6, 'Guantes de trabajo', 3290, 30);
INSERT INTO venta VALUES
    (1, '2026-10-05', 'Rosa'), (2, '2026-10-05', 'Tomás'), (3, '2026-10-06', 'Rosa'),
    (4, '2026-10-07', 'Tomás'), (5, '2026-10-08', 'Rosa');
INSERT INTO detalle_venta VALUES
    (1, 1, 2, 2990), (1, 3, 4, 1290), (2, 2, 1, 8490), (2, 6, 2, 3290), (3, 5, 1, 4590),
    (3, 4, 3, 1890), (4, 1, 5, 2990), (5, 3, 10, 1290), (5, 6, 1, 3290);

-- @consulta d_producto
SELECT * FROM producto;

-- @consulta d_detalle
SELECT * FROM detalle_venta;

-- ============================================================ 3. Una venta como transacción
-- @ejecuta v6_begin
BEGIN;

-- @ejecuta v6_venta
INSERT INTO venta VALUES (6, '2026-10-09', 'Tomás');

-- @ejecuta v6_linea1
INSERT INTO detalle_venta VALUES (6, 2, 2, 8490);

-- @ejecuta v6_stock1
UPDATE producto SET stock = stock - 2 WHERE id_producto = 2;

-- @ejecuta v6_linea2
INSERT INTO detalle_venta VALUES (6, 3, 5, 1290);

-- @ejecuta v6_stock2
UPDATE producto SET stock = stock - 5 WHERE id_producto = 3;

-- @ejecuta v6_commit
COMMIT;

-- @consulta v6_stock
SELECT id_producto, nombre, stock FROM producto WHERE id_producto IN (2, 3);

-- @ejecuta v7_begin
BEGIN;

-- @ejecuta v7_venta
INSERT INTO venta VALUES (7, '2026-10-09', 'Rosa');

-- @ejecuta v7_linea1
INSERT INTO detalle_venta VALUES (7, 6, 3, 3290);

-- @ejecuta v7_stock1
UPDATE producto SET stock = stock - 3 WHERE id_producto = 6;

-- @ejecuta v7_linea2
INSERT INTO detalle_venta VALUES (7, 5, 10, 4590);

-- @falla v7_stock2
UPDATE producto SET stock = stock - 10 WHERE id_producto = 5;

-- @consulta v7_adentro
SELECT d.id_venta, d.id_producto, d.cantidad, p.stock
FROM detalle_venta d JOIN producto p ON p.id_producto = d.id_producto
WHERE d.id_venta = 7;

-- @ejecuta v7_rollback
ROLLBACK;

-- @consulta v7_despues
SELECT (SELECT COUNT(*) FROM venta WHERE id_venta = 7) AS ventas_7,
       (SELECT stock FROM producto WHERE id_producto = 6) AS stock_guantes,
       (SELECT stock FROM producto WHERE id_producto = 5) AS stock_silicona;

-- @falla fk_falla
INSERT INTO detalle_venta VALUES (6, 9, 1, 1000);

-- ============================================================ 5. Índices
-- @plan i_antes
EXPLAIN QUERY PLAN
SELECT SUM(cantidad) FROM detalle_venta WHERE id_producto = 5;

-- @plan i_por_venta
EXPLAIN QUERY PLAN
SELECT SUM(cantidad) FROM detalle_venta WHERE id_venta = 5;

-- @ejecuta i_crear
CREATE INDEX idx_detalle_producto ON detalle_venta(id_producto);

-- @plan i_despues
EXPLAIN QUERY PLAN
SELECT SUM(cantidad) FROM detalle_venta WHERE id_producto = 5;

-- @consulta i_resultado
SELECT SUM(cantidad) FROM detalle_venta WHERE id_producto = 5;

-- @ejecuta i_fecha
CREATE INDEX idx_venta_fecha ON venta(fecha);

-- @plan i_fecha_rango
EXPLAIN QUERY PLAN
SELECT COUNT(*) FROM venta WHERE fecha BETWEEN '2026-10-05' AND '2026-10-07';

-- @plan i_fecha_funcion
EXPLAIN QUERY PLAN
SELECT COUNT(*) FROM venta WHERE substr(fecha, 9, 2) = '05';

-- ============================================================ Pautas
-- @ejecuta p2_begin
BEGIN;

-- @ejecuta p2_update
UPDATE producto SET precio = precio + 100;

-- @ejecuta p2_delete
DELETE FROM detalle_venta WHERE id_venta = 1;

-- @consulta p2_adentro
SELECT (SELECT COUNT(*) FROM detalle_venta) AS lineas,
       (SELECT precio FROM producto WHERE id_producto = 1) AS precio_tornillo;

-- @ejecuta p2_rollback
ROLLBACK;

-- @consulta p2_despues
SELECT (SELECT COUNT(*) FROM detalle_venta) AS lineas,
       (SELECT precio FROM producto WHERE id_producto = 1) AS precio_tornillo;

-- @ejecuta p5_begin
BEGIN;

-- @ejecuta p5_venta
INSERT INTO venta VALUES (7, '2026-10-09', 'Rosa');

-- @ejecuta p5_linea1
INSERT INTO detalle_venta VALUES (7, 6, 3, 3290);

-- @ejecuta p5_stock1
UPDATE producto SET stock = stock - 3 WHERE id_producto = 6;

-- @ejecuta p5_linea2
INSERT INTO detalle_venta VALUES (7, 5, 10, 4590);

-- @falla p5_stock2
UPDATE producto SET stock = stock - 10 WHERE id_producto = 5;

-- @ejecuta p5_commit
COMMIT;

-- @consulta p5_queda
SELECT d.id_producto, d.cantidad, p.stock
FROM detalle_venta d JOIN producto p ON p.id_producto = d.id_producto
WHERE d.id_venta = 7;
