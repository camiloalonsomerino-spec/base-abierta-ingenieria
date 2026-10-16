-- Unidad 7 · Álgebra relacional · base del ejemplo resuelto y de los ejercicios 7.1 a 7.4
-- Talleres de un centro comunitario de Chillán (datos inventados).
-- Correr en una base nueva:  sqlite3 talleres.db < u07_talleres.sql
-- Cada consulta lleva encima su clave (-- @clave); el verificador u07_algebra.py la ejecuta y la
-- compara con la misma pregunta escrita en álgebra relacional.

CREATE TABLE vecino (
    id_vecino INTEGER PRIMARY KEY,
    nombre    VARCHAR(40) NOT NULL,
    sector    VARCHAR(10) NOT NULL,
    edad      INTEGER NOT NULL
);
CREATE TABLE taller (
    id_taller INTEGER PRIMARY KEY,
    actividad VARCHAR(20) NOT NULL UNIQUE,
    dia       VARCHAR(10) NOT NULL,
    cupo      INTEGER NOT NULL
);
CREATE TABLE inscripcion (
    id_vecino INTEGER NOT NULL,
    id_taller INTEGER NOT NULL,
    PRIMARY KEY (id_vecino, id_taller),
    FOREIGN KEY (id_vecino) REFERENCES vecino(id_vecino),
    FOREIGN KEY (id_taller) REFERENCES taller(id_taller)
);

INSERT INTO vecino VALUES
    (1, 'Rosa Valdés', 'norte', 67), (2, 'Matías Fuentes', 'sur', 24),
    (3, 'Carmen Soto', 'norte', 58), (4, 'Diego Parra', 'centro', 35),
    (5, 'Javiera Lagos', 'sur', 41), (6, 'Luis Contreras', 'centro', 72),
    (7, 'Paula Rivas', 'norte', 29), (8, 'Héctor Muñoz', 'sur', 63);
INSERT INTO taller VALUES
    (1, 'yoga', 'sábado', 12), (2, 'guitarra', 'martes', 10), (3, 'cerámica', 'sábado', 8),
    (4, 'computación', 'jueves', 15), (5, 'huerto', 'sábado', 20);
INSERT INTO inscripcion VALUES
    (1, 1), (1, 3), (1, 5), (2, 2), (2, 4), (3, 3), (3, 5), (4, 4),
    (5, 1), (5, 2), (5, 3), (5, 5), (6, 5), (7, 1), (7, 2);

-- @p1
SELECT DISTINCT v.nombre
FROM vecino v
NATURAL JOIN inscripcion i
NATURAL JOIN taller t
WHERE v.sector = 'norte' AND t.actividad = 'cerámica';

-- @p2a
SELECT id_vecino FROM vecino
EXCEPT
SELECT id_vecino FROM inscripcion;

-- @p2b
SELECT v.id_vecino, v.nombre
FROM vecino v
WHERE v.id_vecino IN (SELECT id_vecino FROM vecino
                      EXCEPT
                      SELECT id_vecino FROM inscripcion);

-- @p3
SELECT v.id_vecino, v.nombre
FROM vecino v
WHERE NOT EXISTS (
    SELECT * FROM taller t
    WHERE t.dia = 'sábado'
      AND NOT EXISTS (
          SELECT * FROM inscripcion i
          WHERE i.id_vecino = v.id_vecino AND i.id_taller = t.id_taller));

-- @e1a
SELECT * FROM vecino WHERE edad >= 60;

-- @e1b
SELECT sector FROM vecino;

-- @e1c
SELECT DISTINCT sector FROM vecino;

-- @e2a
SELECT DISTINCT t.actividad
FROM taller t
JOIN inscripcion i ON i.id_taller = t.id_taller
JOIN vecino v ON v.id_vecino = i.id_vecino
WHERE v.nombre = 'Paula Rivas';

-- @e2b
SELECT DISTINCT v.nombre
FROM vecino v
JOIN inscripcion i ON i.id_vecino = v.id_vecino
JOIN taller t ON t.id_taller = i.id_taller
WHERE v.sector = 'sur' AND t.dia = 'sábado';

-- @e3a
SELECT i.id_vecino FROM inscripcion i JOIN taller t ON t.id_taller = i.id_taller WHERE t.actividad = 'yoga'
UNION
SELECT id_vecino FROM vecino WHERE sector = 'centro';

-- @e3b
SELECT i.id_vecino FROM inscripcion i JOIN taller t ON t.id_taller = i.id_taller WHERE t.actividad = 'yoga'
INTERSECT
SELECT i.id_vecino FROM inscripcion i JOIN taller t ON t.id_taller = i.id_taller WHERE t.actividad = 'guitarra';

-- @e3c
SELECT i.id_vecino FROM inscripcion i JOIN taller t ON t.id_taller = i.id_taller WHERE t.actividad = 'yoga'
EXCEPT
SELECT i.id_vecino FROM inscripcion i JOIN taller t ON t.id_taller = i.id_taller WHERE t.actividad = 'guitarra';

-- @e4
SELECT DISTINCT t.actividad
FROM taller t
JOIN inscripcion i ON i.id_taller = t.id_taller
JOIN vecino v ON v.id_vecino = i.id_vecino
WHERE v.edad < 30;

-- @e4sin
SELECT t.actividad
FROM taller t
JOIN inscripcion i ON i.id_taller = t.id_taller
JOIN vecino v ON v.id_vecino = i.id_vecino
WHERE v.edad < 30;
