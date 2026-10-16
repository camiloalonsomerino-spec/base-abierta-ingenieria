-- Ejercicio 5.3 · horas médicas de un Cesfam (datos inventados)
PRAGMA foreign_keys = ON;
CREATE TABLE box (
    id_box  INTEGER PRIMARY KEY,
    piso    INTEGER NOT NULL CHECK (piso IN (1, 2))
);
CREATE TABLE hora (
    id_hora      INTEGER PRIMARY KEY,
    id_box       INTEGER NOT NULL,
    fecha        DATE NOT NULL,
    bloque       INTEGER NOT NULL CHECK (bloque BETWEEN 1 AND 16),
    rut_paciente VARCHAR(12),
    UNIQUE (id_box, fecha, bloque),
    FOREIGN KEY (id_box) REFERENCES box (id_box)
);
INSERT INTO box VALUES (1, 1);
INSERT INTO box VALUES (2, 1);
INSERT INTO box VALUES (3, 2);
INSERT INTO hora VALUES (1, 1, '2026-11-04', 3, '16.723.094-6');

-- @a otro box, mismo día y bloque
INSERT INTO hora VALUES (2, 2, '2026-11-04', 3, '18.450.117-1');
-- @b el mismo box, día y bloque de la hora 1
INSERT INTO hora VALUES (3, 1, '2026-11-04', 3, '13.902.556-3');
-- @c el bloque 17
INSERT INTO hora VALUES (4, 3, '2026-11-04', 17, '21.088.430-0');
-- @d un box que no existe
INSERT INTO hora VALUES (5, 4, '2026-11-05', 2, '14.567.302-K');
-- @e una hora sin paciente asignado
INSERT INTO hora VALUES (6, 3, '2026-11-05', 2, NULL);
-- @f repetir el id_hora 1
INSERT INTO hora VALUES (1, 2, '2026-11-05', 5, '19.234.871-4');
-- @g un box en el piso 3
INSERT INTO box VALUES (4, 3);
