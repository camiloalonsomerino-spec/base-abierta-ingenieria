-- Unidad 8 · SQL para crear y modificar · ejemplo resuelto
-- Liga vecinal de básquetbol de Los Ángeles (datos inventados; los RUT son ficticios).
-- Correr en una base nueva:  sqlite3 liga.db < u08_liga.sql
-- Algunas instrucciones FALLAN a propósito (pasos 4 y 7): el cliente sqlite3 muestra el error y sigue.
-- Cada bloque lleva encima su clave (-- @clave); el verificador u08_ddl_dml.py los corre uno por uno.

-- @crear
PRAGMA foreign_keys = ON;

CREATE TABLE equipo (
    id_equipo  INTEGER PRIMARY KEY,
    nombre     VARCHAR(30) NOT NULL UNIQUE,
    comuna     VARCHAR(30) NOT NULL DEFAULT 'Los Ángeles'
);

CREATE TABLE jugador (
    id_jugador INTEGER PRIMARY KEY,
    rut        VARCHAR(12) NOT NULL UNIQUE,
    nombre     VARCHAR(40) NOT NULL,
    fecha_nac  DATE NOT NULL,
    camiseta   INTEGER NOT NULL CHECK (camiseta BETWEEN 0 AND 99),
    id_equipo  INTEGER NOT NULL,
    UNIQUE (id_equipo, camiseta),
    FOREIGN KEY (id_equipo) REFERENCES equipo(id_equipo)
);

CREATE TABLE partido (
    id_partido INTEGER PRIMARY KEY,
    fecha      DATE NOT NULL,
    id_local   INTEGER NOT NULL,
    id_visita  INTEGER NOT NULL,
    pts_local  INTEGER CHECK (pts_local >= 0),
    pts_visita INTEGER CHECK (pts_visita >= 0),
    CHECK (id_local <> id_visita),
    FOREIGN KEY (id_local)  REFERENCES equipo(id_equipo),
    FOREIGN KEY (id_visita) REFERENCES equipo(id_equipo)
);

-- @equipos
INSERT INTO equipo (id_equipo, nombre, comuna) VALUES
    (1, 'Halcones', 'Los Ángeles'),
    (2, 'Toros de Mulchén', 'Mulchén'),
    (4, 'Nacimiento BC', 'Nacimiento');
INSERT INTO equipo (nombre) VALUES ('Escuela Industrial');
SELECT * FROM equipo;

-- @jugadores
INSERT INTO jugador (id_jugador, rut, nombre, fecha_nac, camiseta, id_equipo) VALUES
    (1, '43.538.745-4', 'Tomás Sepúlveda',     '2001-04-17',  7, 1),
    (2, '42.527.675-1', 'Ignacio Riquelme',    '1998-11-02', 23, 1),
    (3, '43.740.959-5', 'Benjamín Toro',       '2003-01-29',  7, 2),
    (4, '42.932.103-4', 'Vicente Jara',        '1999-08-12', 11, 2),
    (5, '43.437.638-6', 'Felipe Castro',       '2002-06-05',  4, 5),
    (6, '43.235.424-5', 'Cristóbal Navarrete', '2000-03-21', 15, 4);
SELECT COUNT(*) FROM jugador;

-- @falla_not_null
INSERT INTO jugador (rut, fecha_nac, camiseta, id_equipo) VALUES ('43.943.173-3', '2004-09-30', 9, 1);

-- @falla_unique
INSERT INTO jugador (rut, nombre, fecha_nac, camiseta, id_equipo)
VALUES ('42.527.675-1', 'Martín Riquelme', '2004-09-30', 9, 1);

-- @falla_check
INSERT INTO jugador (rut, nombre, fecha_nac, camiseta, id_equipo)
VALUES ('43.943.173-3', 'Martín Riquelme', '2004-09-30', 120, 1);

-- @falla_fk
INSERT INTO jugador (rut, nombre, fecha_nac, camiseta, id_equipo)
VALUES ('43.943.173-3', 'Martín Riquelme', '2004-09-30', 9, 3);

-- @falla_unique_doble
INSERT INTO jugador (rut, nombre, fecha_nac, camiseta, id_equipo)
VALUES ('43.943.173-3', 'Martín Riquelme', '2004-09-30', 7, 1);

-- @falla_check_partido
INSERT INTO partido (fecha, id_local, id_visita) VALUES ('2026-10-10', 2, 2);

-- @partidos
INSERT INTO partido (id_partido, fecha, id_local, id_visita, pts_local, pts_visita) VALUES
    (1, '2026-10-03', 1, 2, 68, 61);
INSERT INTO partido (id_partido, fecha, id_local, id_visita) VALUES
    (2, '2026-10-10', 5, 4),
    (3, '2026-10-10', 2, 1);
SELECT * FROM partido;

-- @resultado
UPDATE partido
SET pts_local = 54, pts_visita = 59
WHERE id_partido = 2;
SELECT changes();

-- @telefono
ALTER TABLE jugador ADD COLUMN telefono VARCHAR(15);
UPDATE jugador SET telefono = '+56 9 0000 0023' WHERE id_jugador = 2;
SELECT id_jugador, nombre, telefono FROM jugador WHERE id_equipo = 1;

-- @falla_borrar_equipo
DELETE FROM equipo WHERE id_equipo = 4;

-- @retiro
DELETE FROM jugador WHERE id_jugador = 6;
SELECT changes();

-- @borrar_equipo
DELETE FROM partido WHERE id_local = 4 OR id_visita = 4;
DELETE FROM equipo WHERE id_equipo = 4;
SELECT id_equipo, nombre FROM equipo;

-- @final
SELECT id_jugador, nombre, camiseta, id_equipo, telefono FROM jugador;
