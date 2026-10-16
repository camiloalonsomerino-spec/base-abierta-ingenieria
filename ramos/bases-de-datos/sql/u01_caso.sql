-- Unidad 1 · Caso integrador: Estampa Sur deja la planilla
-- Corre sobre una copia de datos/estampa_sur.db (el verificador la arma en memoria, la base del caso
-- no se modifica). PRAGMA es propio de SQLite; las diferencias con MySQL están en la unidad.

-- 1. Así se vería la planilla de pedidos de hoy, armada desde la base (unidad 10)
SELECT p.id_pedido AS pedido, p.fecha, c.nombre AS cliente, t.nombre AS tienda, t.comuna,
       pr.nombre AS producto, d.cantidad AS cant, d.precio_unit AS precio, p.estado
FROM detalle_pedido d
JOIN pedido p    ON p.id_pedido = d.id_pedido
JOIN cliente c   ON c.id_cliente = p.id_cliente
JOIN tienda t    ON t.id_tienda = c.id_tienda
JOIN producto pr ON pr.id_producto = d.id_producto
ORDER BY p.id_pedido, d.id_producto
LIMIT 8;

-- 2. Nivel interno: el archivo se guarda en páginas (solo SQLite)
PRAGMA page_size;
PRAGMA page_count;

-- 3. Nivel externo: lo que ve la vendedora de la tienda Puerto
CREATE VIEW clientes_puerto AS
SELECT id_cliente, nombre, tipo FROM cliente WHERE id_tienda = 2;

SELECT * FROM clientes_puerto;

-- 4. Independencia física: un índice cambia el archivo, no la respuesta
CREATE INDEX idx_pedido_cliente ON pedido(id_cliente);

PRAGMA page_count;

-- 5. Independencia lógica: una columna nueva no rompe la vista
ALTER TABLE cliente ADD COLUMN telefono VARCHAR(15);

SELECT * FROM clientes_puerto;

-- 6. Integridad y concurrencia: lo que la planilla aceptaba y la base rechaza
-- debe fallar
INSERT INTO detalle_pedido VALUES (1, 2, -5, 9890);
-- debe fallar
INSERT INTO pedido VALUES (121, 31, '2026-03-15', 'pendiente');
-- debe fallar
INSERT INTO pedido VALUES (121, 3, '2026-03-15', 'despachado');
-- debe fallar
INSERT INTO pedido VALUES (120, 3, '2026-03-31', 'pendiente');
