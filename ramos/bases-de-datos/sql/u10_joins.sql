-- Unidad 10 · SQL con varias tablas: joins y agregación
-- Base abierta de ingeniería · Bases de Datos
--
-- Parte 1 crea y llena las tres tablas de una liga vecinal de baby fútbol de Chillán (teoría,
-- ejemplo resuelto y ejercicios 10.1 y 10.8). Datos inventados. Corre igual en SQLite y en MySQL.
-- Parte 2 son las consultas de la unidad; cada una lleva una marca «-- @nombre» que usa el
-- verificador (verificacion/u10_joins.py). Las marcadas «!error» fallan a propósito.
-- RIGHT JOIN y FULL OUTER JOIN necesitan SQLite 3.39 o más; MySQL no tiene FULL OUTER JOIN.
--
--   sqlite3 u10.db < u10_joins.sql

-- ------------------------------------------------------------------ parte 1 · tablas
CREATE TABLE equipo (
    id_equipo  INTEGER PRIMARY KEY,
    nombre     VARCHAR(30) NOT NULL UNIQUE,
    comuna     VARCHAR(30) NOT NULL
);

CREATE TABLE jugador (
    id_jugador INTEGER PRIMARY KEY,
    nombre     VARCHAR(40) NOT NULL,
    puesto     VARCHAR(12) NOT NULL,
    id_equipo  INTEGER REFERENCES equipo(id_equipo)   -- NULL: todavía sin equipo
);

CREATE TABLE gol (
    id_gol     INTEGER PRIMARY KEY,
    id_jugador INTEGER NOT NULL REFERENCES jugador(id_jugador),
    jornada    INTEGER NOT NULL,
    minuto     INTEGER NOT NULL                       -- dos tiempos de 30 minutos
);

INSERT INTO equipo VALUES
 (1, 'Los Robles',   'Chillán'),
 (2, 'Villa Alegre', 'Chillán Viejo'),
 (3, 'El Bajo',      'Chillán'),
 (4, 'Las Termas',   'Pinto');                       -- recién inscrito, sin jugadores

INSERT INTO jugador VALUES
 (1,  'Bastián Rojas',   'arquero',   1),
 (2,  'Felipe Sáez',     'delantero', 1),
 (3,  'Ignacio Lagos',   'defensa',   1),
 (4,  'Tomás Vidal',     'delantero', 2),
 (5,  'Cristóbal Mora',  'arquero',   2),
 (6,  'Diego Parra',     'defensa',   2),
 (7,  'Joaquín Reyes',   'delantero', 3),
 (8,  'Martín Cofré',    'defensa',   3),
 (9,  'Nicolás Bravo',   'arquero',   3),
 (10, 'Benjamín Lara',   'delantero', NULL);

INSERT INTO gol VALUES
 (1, 2, 1, 12), (2, 2, 1, 38), (3, 4, 1, 20), (4, 7, 1, 44),
 (5, 4, 2, 5),  (6, 6, 2, 31), (7, 2, 2, 47), (8, 7, 2, 50),
 (9, 3, 3, 18), (10, 4, 3, 26), (11, 7, 3, 39), (12, 4, 3, 41), (13, 8, 3, 49);

-- ------------------------------------------------------------------ parte 2 · consultas
-- Teoría

-- @cartesiano_cuenta
SELECT COUNT(*) AS filas FROM equipo, jugador;

-- @cartesiano_muestra
SELECT j.nombre AS jugador, e.nombre AS equipo
FROM jugador j, equipo e
WHERE j.id_jugador <= 2
ORDER BY j.id_jugador, e.id_equipo;

-- @join_sin_on
SELECT COUNT(*) AS filas FROM equipo JOIN jugador;

-- @inner
SELECT j.nombre AS jugador, e.nombre AS equipo
FROM jugador j
INNER JOIN equipo e ON e.id_equipo = j.id_equipo
ORDER BY e.nombre, j.nombre;

-- @implicito
SELECT j.nombre AS jugador, e.nombre AS equipo
FROM jugador j, equipo e
WHERE e.id_equipo = j.id_equipo
ORDER BY e.nombre, j.nombre;

-- @left
SELECT e.nombre AS equipo, j.nombre AS jugador
FROM equipo e
LEFT JOIN jugador j ON j.id_equipo = e.id_equipo
ORDER BY e.nombre, j.nombre;

-- @anti
SELECT e.nombre AS equipo
FROM equipo e
LEFT JOIN jugador j ON j.id_equipo = e.id_equipo
WHERE j.id_jugador IS NULL;

-- @right
SELECT e.nombre AS equipo, j.nombre AS jugador
FROM equipo e
RIGHT JOIN jugador j ON j.id_equipo = e.id_equipo
WHERE j.puesto = 'delantero'
ORDER BY j.nombre;

-- @full
SELECT e.nombre AS equipo, j.nombre AS jugador
FROM equipo e
FULL OUTER JOIN jugador j ON j.id_equipo = e.id_equipo
WHERE e.id_equipo IS NULL OR j.id_jugador IS NULL
ORDER BY equipo;

-- @full_mysql
SELECT e.nombre AS equipo, j.nombre AS jugador
FROM equipo e LEFT JOIN jugador j ON j.id_equipo = e.id_equipo
WHERE j.id_jugador IS NULL
UNION
SELECT e.nombre AS equipo, j.nombre AS jugador
FROM jugador j LEFT JOIN equipo e ON e.id_equipo = j.id_equipo
WHERE e.id_equipo IS NULL
ORDER BY equipo;

-- @left_where
SELECT e.nombre AS equipo, j.nombre AS arquero
FROM equipo e
LEFT JOIN jugador j ON j.id_equipo = e.id_equipo
WHERE j.puesto = 'arquero'
ORDER BY e.nombre;

-- @left_on
SELECT e.nombre AS equipo, j.nombre AS arquero
FROM equipo e
LEFT JOIN jugador j ON j.id_equipo = e.id_equipo AND j.puesto = 'arquero'
ORDER BY e.nombre;

-- @tres
SELECT g.minuto, j.nombre AS jugador, e.nombre AS equipo
FROM gol g
JOIN jugador j ON j.id_jugador = g.id_jugador
JOIN equipo e  ON e.id_equipo = j.id_equipo
WHERE g.jornada = 3
ORDER BY g.minuto;

-- @agregados
SELECT COUNT(*) AS goles, COUNT(DISTINCT id_jugador) AS goleadores,
       MIN(minuto) AS primero, MAX(minuto) AS ultimo, ROUND(AVG(minuto), 1) AS minuto_medio
FROM gol;

-- @count_columna
SELECT COUNT(*) AS jugadores, COUNT(id_equipo) AS con_equipo,
       COUNT(DISTINCT id_equipo) AS equipos_con_jugadores
FROM jugador;

-- @group
SELECT e.nombre AS equipo, COUNT(*) AS goles
FROM gol g
JOIN jugador j ON j.id_jugador = g.id_jugador
JOIN equipo e  ON e.id_equipo = j.id_equipo
GROUP BY e.nombre
ORDER BY goles DESC, equipo;

-- @group_left
SELECT j.nombre AS jugador, COUNT(g.id_gol) AS goles
FROM jugador j
LEFT JOIN gol g ON g.id_jugador = j.id_jugador
GROUP BY j.id_jugador, j.nombre
ORDER BY goles DESC, jugador;

-- @where_agregado !error
SELECT id_jugador, COUNT(*) AS goles
FROM gol
WHERE COUNT(*) >= 3
GROUP BY id_jugador;

-- @having
SELECT id_jugador, COUNT(*) AS goles
FROM gol
GROUP BY id_jugador
HAVING COUNT(*) >= 3
ORDER BY goles DESC, id_jugador;

-- @where_having
SELECT e.nombre AS equipo, COUNT(*) AS goles_2t
FROM gol g
JOIN jugador j ON j.id_jugador = g.id_jugador
JOIN equipo e  ON e.id_equipo = j.id_equipo
WHERE g.minuto > 30
GROUP BY e.nombre
HAVING COUNT(*) >= 3;

-- Ejemplo resuelto

-- @ej_boletin
SELECT e.nombre AS equipo, COUNT(g.id_gol) AS goles_j3
FROM equipo e
LEFT JOIN jugador j ON j.id_equipo = e.id_equipo
LEFT JOIN gol g     ON g.id_jugador = j.id_jugador AND g.jornada = 3
GROUP BY e.nombre
ORDER BY goles_j3 DESC, equipo;

-- @ej_boletin_where
SELECT e.nombre AS equipo, COUNT(g.id_gol) AS goles_j3
FROM equipo e
LEFT JOIN jugador j ON j.id_equipo = e.id_equipo
LEFT JOIN gol g     ON g.id_jugador = j.id_jugador
WHERE g.jornada = 3
GROUP BY e.nombre
ORDER BY goles_j3 DESC, equipo;

-- @ej_goleadores
SELECT j.nombre AS jugador, e.nombre AS equipo, COUNT(*) AS goles,
       SUM(CASE WHEN g.minuto > 30 THEN 1 ELSE 0 END) AS en_2t
FROM gol g
JOIN jugador j ON j.id_jugador = g.id_jugador
JOIN equipo e  ON e.id_equipo = j.id_equipo
GROUP BY j.id_jugador, j.nombre, e.nombre
HAVING COUNT(*) >= 2
ORDER BY goles DESC, jugador;

-- Ejercicios (liga)

-- @e1a
SELECT COUNT(*) AS filas FROM jugador, gol;

-- @e1b
SELECT COUNT(*) AS filas FROM jugador j, gol g WHERE g.id_jugador = j.id_jugador;

-- @e8a
SELECT e.nombre AS equipo, j.nombre AS jugador, COUNT(*) AS goles
FROM gol g
JOIN jugador j ON j.id_jugador = g.id_jugador
JOIN equipo e  ON e.id_equipo = j.id_equipo
GROUP BY e.nombre
ORDER BY equipo;

-- @e8a_bien
SELECT e.nombre AS equipo, j.nombre AS jugador, COUNT(*) AS goles
FROM gol g
JOIN jugador j ON j.id_jugador = g.id_jugador
JOIN equipo e  ON e.id_equipo = j.id_equipo
GROUP BY e.nombre, j.id_jugador, j.nombre
ORDER BY equipo, goles DESC, jugador;

-- @e8b
SELECT e.nombre AS equipo, COUNT(*) AS goles
FROM gol g
JOIN jugador j ON j.id_jugador = g.id_jugador
JOIN equipo e  ON e.id_equipo = j.id_jugador
GROUP BY e.nombre
ORDER BY goles DESC;

-- @e8c
SELECT e.nombre AS equipo, COUNT(*) AS jugadores
FROM equipo e
LEFT JOIN jugador j ON j.id_equipo = e.id_equipo
GROUP BY e.nombre
ORDER BY e.nombre;

-- @e8c_bien
SELECT e.nombre AS equipo, COUNT(j.id_jugador) AS jugadores
FROM equipo e
LEFT JOIN jugador j ON j.id_equipo = e.id_equipo
GROUP BY e.nombre
ORDER BY e.nombre;
