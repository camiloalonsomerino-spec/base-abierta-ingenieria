-- Ejercicio 5.10 · pauta · el esquema corregido de la expo de emprendedores
PRAGMA foreign_keys = ON;
CREATE TABLE emprendedor (
    id_emprendedor INTEGER PRIMARY KEY,
    rut            VARCHAR(12) NOT NULL UNIQUE,
    nombre         VARCHAR(60) NOT NULL,
    activo         INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
);
CREATE TABLE stand (
    numero         INTEGER PRIMARY KEY,
    metros         INTEGER NOT NULL CHECK (metros > 0),
    id_emprendedor INTEGER,
    FOREIGN KEY (id_emprendedor) REFERENCES emprendedor (id_emprendedor) ON DELETE SET NULL
);
CREATE TABLE categoria (
    id_categoria   INTEGER PRIMARY KEY,
    nombre         VARCHAR(30) NOT NULL UNIQUE
);
CREATE TABLE vende (
    id_emprendedor INTEGER NOT NULL,
    id_categoria   INTEGER NOT NULL,
    PRIMARY KEY (id_emprendedor, id_categoria),
    FOREIGN KEY (id_emprendedor) REFERENCES emprendedor (id_emprendedor) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria) ON DELETE RESTRICT
);
CREATE TABLE venta (
    id_venta       INTEGER PRIMARY KEY,
    id_emprendedor INTEGER NOT NULL,
    fecha          DATE NOT NULL,
    monto          INTEGER NOT NULL CHECK (monto > 0),
    FOREIGN KEY (id_emprendedor) REFERENCES emprendedor (id_emprendedor) ON DELETE RESTRICT
);
INSERT INTO emprendedor (id_emprendedor, rut, nombre) VALUES (1, '16.723.094-6', 'Daniela Cortés');
INSERT INTO emprendedor (id_emprendedor, rut, nombre) VALUES (2, '18.450.117-1', 'Ignacio Pizarro');
INSERT INTO stand VALUES (1, 9, 1);
INSERT INTO stand VALUES (2, 6, 2);
INSERT INTO stand VALUES (3, 6, NULL);
INSERT INTO categoria VALUES (1, 'joyas');
INSERT INTO categoria VALUES (2, 'cerámica');
INSERT INTO categoria VALUES (3, 'papayas');
INSERT INTO categoria VALUES (4, 'mermeladas');
INSERT INTO vende VALUES (1, 1);
INSERT INTO vende VALUES (1, 2);
INSERT INTO vende VALUES (2, 3);
INSERT INTO vende VALUES (2, 4);
INSERT INTO venta VALUES (1, 1, '2026-12-18', 24000);
INSERT INTO venta VALUES (2, 2, '2026-12-18', 8500);

-- @b1 un emprendedor sin RUT
INSERT INTO emprendedor (nombre) VALUES ('Sin RUT');
-- @b2 un stand sin metros
INSERT INTO stand (numero, metros) VALUES (4, NULL);
-- @b3 Ignacio arrienda también el stand 3, sin perder el 2
UPDATE stand SET id_emprendedor = 2 WHERE numero = 3;
-- @b4
SELECT numero, id_emprendedor FROM stand WHERE id_emprendedor = 2;
-- @b5 quién vende mermeladas
SELECT e.nombre FROM emprendedor e
JOIN vende v ON v.id_emprendedor = e.id_emprendedor
JOIN categoria c ON c.id_categoria = v.id_categoria
WHERE c.nombre = 'mermeladas';
-- @b6 la misma categoría dos veces
INSERT INTO vende VALUES (2, 4);
-- @b7 Daniela se retira: con ventas no se borra
DELETE FROM emprendedor WHERE id_emprendedor = 1;
-- @b8 se marca como retirada y sus ventas quedan
UPDATE emprendedor SET activo = 0 WHERE id_emprendedor = 1;
