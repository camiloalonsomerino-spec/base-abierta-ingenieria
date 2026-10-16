-- Ejercicio 5.9 · pauta · la liga rediseñada: la historia no se borra, el equipo se marca inactivo
PRAGMA foreign_keys = ON;
CREATE TABLE equipo (
    id_equipo  INTEGER PRIMARY KEY,
    nombre     VARCHAR(40) NOT NULL UNIQUE,
    activo     INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
);
CREATE TABLE jugador (
    id_jugador INTEGER PRIMARY KEY,
    nombre     VARCHAR(60) NOT NULL,
    id_equipo  INTEGER NOT NULL,
    FOREIGN KEY (id_equipo) REFERENCES equipo (id_equipo) ON DELETE RESTRICT
);
CREATE TABLE partido (
    id_partido INTEGER PRIMARY KEY,
    fecha      DATE NOT NULL,
    local      INTEGER NOT NULL,
    visita     INTEGER NOT NULL,
    CHECK (local <> visita),
    FOREIGN KEY (local) REFERENCES equipo (id_equipo) ON DELETE RESTRICT,
    FOREIGN KEY (visita) REFERENCES equipo (id_equipo) ON DELETE RESTRICT
);
CREATE TABLE gol (
    id_gol     INTEGER PRIMARY KEY,
    id_partido INTEGER NOT NULL,
    id_jugador INTEGER NOT NULL,
    minuto     INTEGER NOT NULL CHECK (minuto BETWEEN 1 AND 50),
    FOREIGN KEY (id_partido) REFERENCES partido (id_partido) ON DELETE CASCADE,
    FOREIGN KEY (id_jugador) REFERENCES jugador (id_jugador) ON DELETE RESTRICT
);
INSERT INTO equipo (id_equipo, nombre) VALUES (1, 'Deportivo Lircay');
INSERT INTO equipo (id_equipo, nombre) VALUES (2, 'Unión Piduco');
INSERT INTO jugador VALUES (1, 'Benjamín Pino', 1);
INSERT INTO jugador VALUES (3, 'Martín Acevedo', 2);
INSERT INTO partido VALUES (1, '2026-09-05', 1, 2);
INSERT INTO gol VALUES (1, 1, 1, 7);
INSERT INTO gol VALUES (2, 1, 3, 18);

-- @r1 borrar el equipo ya no se puede
DELETE FROM equipo WHERE id_equipo = 1;
-- @r2 se marca inactivo
UPDATE equipo SET activo = 0 WHERE id_equipo = 1;
-- @r3 y los goles de Martín siguen ahí
SELECT COUNT(*) FROM gol WHERE id_jugador = 3;
