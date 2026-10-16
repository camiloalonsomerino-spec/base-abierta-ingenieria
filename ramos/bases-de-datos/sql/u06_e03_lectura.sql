-- Ejercicio 6.3 · un club de lectura de Punta Arenas (datos inventados): géneros en una celda
CREATE TABLE socio_planilla (
    id_socio INTEGER PRIMARY KEY,
    nombre   VARCHAR(60) NOT NULL,
    generos  VARCHAR(200)
);
INSERT INTO socio_planilla VALUES (1, 'Marcela Ojeda', 'novela negra, poesía');
INSERT INTO socio_planilla VALUES (2, 'Hernán Barría', 'Poesía');
INSERT INTO socio_planilla VALUES (3, 'Lorena Vidal', 'ciencia ficción, poesia, ensayo');
INSERT INTO socio_planilla VALUES (4, 'Cristián Andrade', 'ensayo');
INSERT INTO socio_planilla VALUES (5, 'Pilar Mansilla', 'novela negra');
INSERT INTO socio_planilla VALUES (6, 'Ramón Gallardo', 'poesía, novela negra');

-- La versión en primera forma normal: un género por fila, contra un catálogo
CREATE TABLE genero (
    id_genero INTEGER PRIMARY KEY,
    nombre    VARCHAR(30) NOT NULL UNIQUE
);
CREATE TABLE socio (
    id_socio  INTEGER PRIMARY KEY,
    nombre    VARCHAR(60) NOT NULL
);
CREATE TABLE prefiere (
    id_socio  INTEGER NOT NULL,
    id_genero INTEGER NOT NULL,
    PRIMARY KEY (id_socio, id_genero),
    FOREIGN KEY (id_socio) REFERENCES socio (id_socio),
    FOREIGN KEY (id_genero) REFERENCES genero (id_genero)
);
INSERT INTO genero VALUES (1, 'novela negra');
INSERT INTO genero VALUES (2, 'poesía');
INSERT INTO genero VALUES (3, 'ciencia ficción');
INSERT INTO genero VALUES (4, 'ensayo');
INSERT INTO socio SELECT id_socio, nombre FROM socio_planilla;
INSERT INTO prefiere VALUES (1, 1);
INSERT INTO prefiere VALUES (1, 2);
INSERT INTO prefiere VALUES (2, 2);
INSERT INTO prefiere VALUES (3, 3);
INSERT INTO prefiere VALUES (3, 2);
INSERT INTO prefiere VALUES (3, 4);
INSERT INTO prefiere VALUES (4, 4);
INSERT INTO prefiere VALUES (5, 1);
INSERT INTO prefiere VALUES (6, 2);
INSERT INTO prefiere VALUES (6, 1);

-- @like cuántos socios leen poesía, buscando en la celda
SELECT COUNT(*) AS socios FROM socio_planilla WHERE generos LIKE '%poesía%';
-- @normal lo mismo en las tablas normalizadas
SELECT COUNT(*) AS socios
FROM prefiere pf JOIN genero g ON g.id_genero = pf.id_genero
WHERE g.nombre = 'poesía';
-- @ranking socios por género
SELECT g.nombre, COUNT(*) AS socios
FROM prefiere pf JOIN genero g ON g.id_genero = pf.id_genero
GROUP BY g.nombre
ORDER BY socios DESC, g.nombre;
