-- Unidad 5 · Caso integrador · propuesta de restricciones para Estampa Sur
-- Se corre sobre OTRA copia de datos/estampa_sur.db. SQLite no cambia una restricción con ALTER TABLE:
-- la tabla se rehace (crear la nueva, copiar las filas, borrar la vieja y renombrar la nueva).
-- En MySQL basta ALTER TABLE ... DROP FOREIGN KEY y ADD CONSTRAINT.
PRAGMA foreign_keys = ON;

CREATE TABLE detalle_nuevo (
    id_pedido   INTEGER NOT NULL,
    id_producto INTEGER NOT NULL,
    cantidad    INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unit INTEGER NOT NULL CHECK (precio_unit > 0),
    PRIMARY KEY (id_pedido, id_producto),
    FOREIGN KEY (id_pedido) REFERENCES pedido (id_pedido) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES producto (id_producto) ON DELETE RESTRICT
);
INSERT INTO detalle_nuevo SELECT * FROM detalle_pedido;
DROP TABLE detalle_pedido;
ALTER TABLE detalle_nuevo RENAME TO detalle_pedido;

CREATE TABLE orden_nueva (
    id_orden    INTEGER PRIMARY KEY,
    id_producto INTEGER NOT NULL,
    semana      INTEGER NOT NULL CHECK (semana BETWEEN 1 AND 52),
    lote        INTEGER NOT NULL CHECK (lote > 0),
    UNIQUE (id_producto, semana),
    FOREIGN KEY (id_producto) REFERENCES producto (id_producto) ON DELETE RESTRICT
);
INSERT INTO orden_nueva SELECT * FROM orden_produccion;
DROP TABLE orden_produccion;
ALTER TABLE orden_nueva RENAME TO orden_produccion;

-- @q1 ahora borrar un pedido se lleva su detalle
DELETE FROM pedido WHERE id_pedido = 3;
-- @q2
SELECT COUNT(*) FROM detalle_pedido WHERE id_pedido = 3;
-- @q3
SELECT COUNT(*) FROM detalle_pedido;
-- @q4 el lote negativo ya no entra
INSERT INTO orden_produccion (id_producto, semana, lote) VALUES (2, 6, -360);
-- @q5 ni la orden repetida
INSERT INTO orden_produccion (id_producto, semana, lote) VALUES (1, 6, 720);
-- @q6 y el cliente con pedidos sigue protegido
DELETE FROM cliente WHERE id_cliente = 1;
