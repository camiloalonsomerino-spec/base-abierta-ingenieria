-- Ejercicio 5.5 · arriendo de bicicletas en Puerto Varas (datos inventados) · la solución de la pauta
PRAGMA foreign_keys = ON;
CREATE TABLE cliente (
    id_cliente INTEGER PRIMARY KEY,
    rut        VARCHAR(12) NOT NULL UNIQUE,
    nombre     VARCHAR(60) NOT NULL,
    telefono   VARCHAR(16) NOT NULL
);
CREATE TABLE bicicleta (
    codigo      VARCHAR(8) NOT NULL PRIMARY KEY,
    tipo        VARCHAR(10) NOT NULL CHECK (tipo IN ('urbana', 'montaña', 'eléctrica')),
    tarifa_hora INTEGER NOT NULL CHECK (tarifa_hora > 0)
);
CREATE TABLE arriendo (
    id_arriendo INTEGER PRIMARY KEY,
    id_cliente  INTEGER NOT NULL,
    codigo      VARCHAR(8) NOT NULL,
    inicio      DATETIME NOT NULL,
    fin         DATETIME,
    CHECK (fin > inicio),
    FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente) ON DELETE RESTRICT,
    FOREIGN KEY (codigo) REFERENCES bicicleta (codigo) ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO cliente VALUES (1, '42.123.247-4', 'Francisca Oyarzún', '+56 9 0000 0026');
INSERT INTO cliente VALUES (2, '40.909.963-7', 'Ignacio Barrientos', '+56 9 0000 0030');
INSERT INTO bicicleta VALUES ('PV-014', 'urbana', 2500);
INSERT INTO bicicleta VALUES ('PV-022', 'montaña', 3800);
INSERT INTO bicicleta VALUES ('PV-031', 'eléctrica', 6200);
INSERT INTO arriendo VALUES (1, 1, 'PV-022', '2026-12-28 10:00', '2026-12-28 13:00');

-- @a una bicicleta tándem
INSERT INTO bicicleta VALUES ('PV-040', 'tándem', 4500);
-- @b una tarifa de cero pesos
INSERT INTO bicicleta VALUES ('PV-041', 'urbana', 0);
-- @c un RUT que ya existe
INSERT INTO cliente (rut, nombre, telefono) VALUES ('42.123.247-4', 'F. Oyarzún', '+56 9 0000 0026');
-- @d arrendar una bicicleta que no existe
INSERT INTO arriendo (id_cliente, codigo, inicio) VALUES (2, 'PV-099', '2026-12-29 09:30');
-- @e un arriendo que termina antes de empezar
INSERT INTO arriendo (id_cliente, codigo, inicio, fin) VALUES (2, 'PV-014', '2026-12-29 09:30', '2026-12-29 08:30');
-- @f un arriendo en curso (sin fin)
INSERT INTO arriendo (id_cliente, codigo, inicio) VALUES (2, 'PV-031', '2026-12-29 09:30');
-- @g borrar a una clienta con arriendos
DELETE FROM cliente WHERE id_cliente = 1;
