-- Unidad 1 · Ejercicio 1.7: el pedido 5012 de la pastelería de La Serena, en tablas

CREATE TABLE cliente (
    id_cliente INTEGER PRIMARY KEY,
    nombre     VARCHAR(60) NOT NULL,
    telefono   VARCHAR(15)
);

CREATE TABLE producto (
    id_producto INTEGER PRIMARY KEY,
    nombre      VARCHAR(40) NOT NULL UNIQUE
);

CREATE TABLE pedido (
    id_pedido  INTEGER PRIMARY KEY,
    id_cliente INTEGER NOT NULL REFERENCES cliente(id_cliente),
    fecha      DATE NOT NULL
);

CREATE TABLE detalle (
    id_pedido   INTEGER NOT NULL REFERENCES pedido(id_pedido),
    id_producto INTEGER NOT NULL REFERENCES producto(id_producto),
    cantidad    INTEGER NOT NULL CHECK (cantidad > 0),
    precio      INTEGER NOT NULL,
    PRIMARY KEY (id_pedido, id_producto)
);

INSERT INTO cliente VALUES (1, 'Daniela Pizarro', '9 5520 7714');
INSERT INTO producto VALUES (1, 'torta tres leches'), (2, 'kuchen de nuez'), (3, 'berlines');
INSERT INTO pedido VALUES (5012, 1, '2026-09-18');
INSERT INTO detalle VALUES (5012, 1, 1, 18500), (5012, 2, 2, 9800), (5012, 3, 12, 900);

SELECT SUM(cantidad * precio) AS total FROM detalle WHERE id_pedido = 5012;
