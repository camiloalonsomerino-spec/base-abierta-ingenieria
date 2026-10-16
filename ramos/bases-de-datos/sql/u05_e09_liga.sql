-- Ejercicio 5.9 · liga de futbolito de Talca (datos inventados): CASCADE en todas partes
PRAGMA foreign_keys = ON;
CREATE TABLE equipo (
    id_equipo  INTEGER PRIMARY KEY,
    nombre     VARCHAR(40) NOT NULL UNIQUE
);
CREATE TABLE jugador (
    id_jugador INTEGER PRIMARY KEY,
    nombre     VARCHAR(60) NOT NULL,
    id_equipo  INTEGER NOT NULL,
    FOREIGN KEY (id_equipo) REFERENCES equipo (id_equipo) ON DELETE CASCADE
);
CREATE TABLE partido (
    id_partido INTEGER PRIMARY KEY,
    fecha      DATE NOT NULL,
    local      INTEGER NOT NULL,
    visita     INTEGER NOT NULL,
    CHECK (local <> visita),
    FOREIGN KEY (local) REFERENCES equipo (id_equipo) ON DELETE CASCADE,
    FOREIGN KEY (visita) REFERENCES equipo (id_equipo) ON DELETE CASCADE
);
CREATE TABLE gol (
    id_gol     INTEGER PRIMARY KEY,
    id_partido INTEGER NOT NULL,
    id_jugador INTEGER NOT NULL,
    minuto     INTEGER NOT NULL CHECK (minuto BETWEEN 1 AND 50),
    FOREIGN KEY (id_partido) REFERENCES partido (id_partido) ON DELETE CASCADE,
    FOREIGN KEY (id_jugador) REFERENCES jugador (id_jugador) ON DELETE CASCADE
);
INSERT INTO equipo VALUES (1, 'Deportivo Lircay');
INSERT INTO equipo VALUES (2, 'Unión Piduco');
INSERT INTO equipo VALUES (3, 'Estrella del Maule');
INSERT INTO equipo VALUES (4, 'Las Rastras');
INSERT INTO jugador VALUES (1, 'Benjamín Pino', 1);
INSERT INTO jugador VALUES (2, 'Cristóbal Leiva', 1);
INSERT INTO jugador VALUES (3, 'Martín Acevedo', 2);
INSERT INTO jugador VALUES (4, 'Joaquín Sanhueza', 2);
INSERT INTO jugador VALUES (5, 'Vicente Orellana', 3);
INSERT INTO jugador VALUES (6, 'Tomás Bravo', 3);
INSERT INTO jugador VALUES (7, 'Lucas Moya', 4);
INSERT INTO jugador VALUES (8, 'Felipe Cáceres', 4);
INSERT INTO partido VALUES (1, '2026-09-05', 1, 2);
INSERT INTO partido VALUES (2, '2026-09-05', 3, 4);
INSERT INTO partido VALUES (3, '2026-09-12', 1, 3);
INSERT INTO partido VALUES (4, '2026-09-12', 2, 4);
INSERT INTO partido VALUES (5, '2026-09-19', 4, 1);
INSERT INTO partido VALUES (6, '2026-09-19', 2, 3);
INSERT INTO gol VALUES (1, 1, 1, 7);
INSERT INTO gol VALUES (2, 1, 3, 18);
INSERT INTO gol VALUES (3, 1, 3, 41);
INSERT INTO gol VALUES (4, 2, 5, 12);
INSERT INTO gol VALUES (5, 2, 7, 33);
INSERT INTO gol VALUES (6, 3, 2, 9);
INSERT INTO gol VALUES (7, 3, 5, 22);
INSERT INTO gol VALUES (8, 3, 6, 47);
INSERT INTO gol VALUES (9, 4, 4, 15);
INSERT INTO gol VALUES (10, 4, 8, 29);
INSERT INTO gol VALUES (11, 4, 8, 44);
INSERT INTO gol VALUES (12, 5, 7, 6);
INSERT INTO gol VALUES (13, 5, 1, 26);
INSERT INTO gol VALUES (14, 5, 7, 38);
INSERT INTO gol VALUES (15, 6, 3, 11);
INSERT INTO gol VALUES (16, 6, 6, 35);

-- @antes
SELECT (SELECT COUNT(*) FROM jugador) AS jugadores, (SELECT COUNT(*) FROM partido) AS partidos,
       (SELECT COUNT(*) FROM gol) AS goles;
-- @goleadores_antes
SELECT j.nombre, COUNT(*) AS goles
FROM gol g JOIN jugador j ON j.id_jugador = g.id_jugador
GROUP BY j.id_jugador, j.nombre
ORDER BY goles DESC, j.nombre;
-- @borrar Deportivo Lircay se retira de la liga
DELETE FROM equipo WHERE id_equipo = 1;
-- @despues
SELECT (SELECT COUNT(*) FROM jugador) AS jugadores, (SELECT COUNT(*) FROM partido) AS partidos,
       (SELECT COUNT(*) FROM gol) AS goles;
-- @goleadores_despues
SELECT j.nombre, COUNT(*) AS goles
FROM gol g JOIN jugador j ON j.id_jugador = g.id_jugador
GROUP BY j.id_jugador, j.nombre
ORDER BY goles DESC, j.nombre;
