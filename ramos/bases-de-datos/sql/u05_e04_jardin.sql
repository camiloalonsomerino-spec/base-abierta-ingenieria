-- Ejercicio 5.4 · jardín infantil (datos inventados) · el diseño de la pauta
PRAGMA foreign_keys = ON;
CREATE TABLE sala (
    id_sala   INTEGER PRIMARY KEY,
    nombre    VARCHAR(30) NOT NULL UNIQUE
);
CREATE TABLE educadora (
    id_educadora INTEGER PRIMARY KEY,
    nombre       VARCHAR(60) NOT NULL
);
CREATE TABLE parvulo (
    id_parvulo   INTEGER PRIMARY KEY,
    nombre       VARCHAR(60) NOT NULL,
    id_sala      INTEGER NOT NULL,
    id_educadora INTEGER,
    retirado     INTEGER NOT NULL DEFAULT 0 CHECK (retirado IN (0, 1)),
    FOREIGN KEY (id_sala) REFERENCES sala (id_sala) ON DELETE RESTRICT,
    FOREIGN KEY (id_educadora) REFERENCES educadora (id_educadora) ON DELETE SET NULL
);
CREATE TABLE alergia_parvulo (
    id_parvulo INTEGER NOT NULL,
    alergeno   VARCHAR(30) NOT NULL,
    PRIMARY KEY (id_parvulo, alergeno),
    FOREIGN KEY (id_parvulo) REFERENCES parvulo (id_parvulo) ON DELETE CASCADE
);
CREATE TABLE asistencia (
    id_parvulo INTEGER NOT NULL,
    fecha      DATE NOT NULL,
    PRIMARY KEY (id_parvulo, fecha),
    FOREIGN KEY (id_parvulo) REFERENCES parvulo (id_parvulo) ON DELETE RESTRICT
);
INSERT INTO sala VALUES (1, 'Chincoles');
INSERT INTO sala VALUES (2, 'Queltehues');
INSERT INTO educadora VALUES (1, 'Paula Contreras');
INSERT INTO educadora VALUES (2, 'Gloria Navarrete');
INSERT INTO parvulo (id_parvulo, nombre, id_sala, id_educadora) VALUES (1, 'Agustín', 1, 1);
INSERT INTO parvulo (id_parvulo, nombre, id_sala, id_educadora) VALUES (2, 'Florencia', 1, 2);
INSERT INTO parvulo (id_parvulo, nombre, id_sala, id_educadora) VALUES (3, 'Matías', 2, 2);
INSERT INTO parvulo (id_parvulo, nombre, id_sala, id_educadora) VALUES (4, 'Isidora', 2, 1);
INSERT INTO alergia_parvulo VALUES (2, 'maní');
INSERT INTO alergia_parvulo VALUES (4, 'huevo');
INSERT INTO alergia_parvulo VALUES (4, 'kiwi');
INSERT INTO asistencia VALUES (1, '2026-10-05');
INSERT INTO asistencia VALUES (2, '2026-10-05');
INSERT INTO asistencia VALUES (3, '2026-10-05');
INSERT INTO asistencia VALUES (1, '2026-10-06');
INSERT INTO asistencia VALUES (3, '2026-10-06');

-- @a la educadora Gloria deja el jardín
DELETE FROM educadora WHERE id_educadora = 2;
-- @b
SELECT id_parvulo, nombre, id_educadora FROM parvulo WHERE id_parvulo IN (2, 3);
-- @c cerrar la sala Chincoles con niños dentro
DELETE FROM sala WHERE id_sala = 1;
-- @d borrar a un niño que ya asistió
DELETE FROM parvulo WHERE id_parvulo = 3;
-- @e borrar a Isidora, matriculada por error (nunca asistió)
DELETE FROM parvulo WHERE id_parvulo = 4;
-- @f
SELECT COUNT(*) FROM alergia_parvulo WHERE id_parvulo = 4;
-- @g el que se va se marca, no se borra
UPDATE parvulo SET retirado = 1 WHERE id_parvulo = 3;
