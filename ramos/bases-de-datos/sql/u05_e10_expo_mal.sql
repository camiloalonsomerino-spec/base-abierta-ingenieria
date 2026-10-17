-- Ejercicio 5.10 · expo de emprendedores de La Serena (datos inventados): el esquema con seis errores
PRAGMA foreign_keys = ON;
CREATE TABLE emprendedor (
    rut         VARCHAR(12) PRIMARY KEY,
    nombre      VARCHAR(60) NOT NULL,
    numero_stand INTEGER REFERENCES stand (numero),
    categorias  VARCHAR(200)
);
CREATE TABLE stand (
    numero      INTEGER PRIMARY KEY,
    metros      INTEGER CHECK (metros > 0)
);
CREATE TABLE venta (
    id_venta    INTEGER PRIMARY KEY,
    rut         VARCHAR(12) NOT NULL,
    fecha       DATE NOT NULL,
    monto       INTEGER NOT NULL CHECK (monto > 0),
    FOREIGN KEY (rut) REFERENCES emprendedor (rut) ON DELETE SET NULL
);
INSERT INTO stand VALUES (1, 9);
INSERT INTO stand VALUES (2, 6);
INSERT INTO stand VALUES (3, 6);
INSERT INTO emprendedor VALUES ('41.415.498-0', 'Daniela Cortés', 1, 'joyas, cerámica');
INSERT INTO emprendedor VALUES ('42.123.247-4', 'Ignacio Pizarro', 2, 'papayas, mermeladas');
INSERT INTO venta VALUES (1, '41.415.498-0', '2026-12-18', 24000);
INSERT INTO venta VALUES (2, '42.123.247-4', '2026-12-18', 8500);

-- @m1 un emprendedor sin RUT
INSERT INTO emprendedor (nombre, numero_stand) VALUES ('Sin RUT', 3);
-- @m2 un stand sin metros
INSERT INTO stand VALUES (4, NULL);
-- @m3 Ignacio arrienda también el stand 3: solo cabe pisando el 2
UPDATE emprendedor SET numero_stand = 3 WHERE rut = '42.123.247-4';
-- @m4 quién vende mermeladas (la columna de texto obliga a buscar con LIKE)
SELECT nombre FROM emprendedor WHERE categorias LIKE '%mermelada%';
-- @m5 Daniela se retira de la expo
DELETE FROM emprendedor WHERE rut = '41.415.498-0';
