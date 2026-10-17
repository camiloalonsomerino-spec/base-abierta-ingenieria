-- Ejercicio 5.8 · notas de un control (escala chilena de 1,0 a 7,0; datos inventados)
CREATE TABLE nota (
    rut        VARCHAR(12) NOT NULL,
    evaluacion VARCHAR(20) NOT NULL,
    nota       REAL CHECK (nota BETWEEN 1.0 AND 7.0),
    PRIMARY KEY (rut, evaluacion)
);
-- @a un 5,8
INSERT INTO nota VALUES ('43.639.852-2', 'control 2', 5.8);
-- @b una nota en blanco (NULL)
INSERT INTO nota VALUES ('41.011.070-9', 'control 2', NULL);
-- @c un 7,3
INSERT INTO nota VALUES ('42.426.568-3', 'control 2', 7.3);
-- @d el texto '6,2' copiado de una planilla
INSERT INTO nota VALUES ('40.101.107-2', 'control 2', '6,2');
-- @e un 1,0
INSERT INTO nota VALUES ('41.819.926-1', 'control 2', 1.0);
-- @f un 4,5
INSERT INTO nota VALUES ('44.044.280-3', 'control 2', 4.5);
-- @resumen
SELECT COUNT(*) AS filas, COUNT(nota) AS con_nota, ROUND(AVG(nota), 2) AS promedio FROM nota;

CREATE TABLE nota_floja (
    rut  VARCHAR(12) NOT NULL PRIMARY KEY,
    nota REAL CHECK (nota > 0)
);
-- @g el texto 'seis' con CHECK (nota > 0)
INSERT INTO nota_floja VALUES ('40.202.214-0', 'seis');
-- @h
SELECT rut, nota, typeof(nota) FROM nota_floja;

CREATE TABLE nota_estricta (
    rut        TEXT NOT NULL,
    evaluacion TEXT NOT NULL,
    nota       REAL NOT NULL CHECK (nota BETWEEN 1.0 AND 7.0),
    PRIMARY KEY (rut, evaluacion)
) STRICT;
-- @i 'seis' en la tabla STRICT
INSERT INTO nota_estricta VALUES ('40.202.214-0', 'control 2', 'seis');
-- @j NULL con NOT NULL
INSERT INTO nota_estricta VALUES ('41.011.070-9', 'control 2', NULL);
-- @k el entero 6 en la tabla STRICT
INSERT INTO nota_estricta VALUES ('41.314.391-8', 'control 2', 6);
-- @l
SELECT rut, nota, typeof(nota) FROM nota_estricta;
