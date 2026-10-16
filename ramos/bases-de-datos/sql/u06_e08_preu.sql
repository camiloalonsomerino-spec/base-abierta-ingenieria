-- Ejercicio 6.8 · tutorías de un preuniversitario de Temuco (datos inventados)
-- Reglas: cada tutor enseña un solo ramo; cada alumno tiene un solo tutor por ramo.
PRAGMA foreign_keys = ON;

-- Diseño en tercera forma normal (una tabla)
CREATE TABLE tutoria (
    alumno VARCHAR(40) NOT NULL,
    ramo   VARCHAR(20) NOT NULL,
    tutor  VARCHAR(40) NOT NULL,
    PRIMARY KEY (alumno, ramo),
    UNIQUE (alumno, tutor)
);
-- Diseño en forma normal de Boyce-Codd (dos tablas)
CREATE TABLE tutor (
    tutor  VARCHAR(40) NOT NULL PRIMARY KEY,
    ramo   VARCHAR(20) NOT NULL
);
CREATE TABLE asignacion (
    alumno VARCHAR(40) NOT NULL,
    tutor  VARCHAR(40) NOT NULL,
    PRIMARY KEY (alumno, tutor),
    FOREIGN KEY (tutor) REFERENCES tutor (tutor)
);
INSERT INTO tutoria VALUES ('Amanda', 'matemática', 'Valeria Sáez');
INSERT INTO tutoria VALUES ('Amanda', 'lenguaje', 'Fernanda Lagos');
INSERT INTO tutoria VALUES ('Bruno', 'matemática', 'Ignacio Pino');
INSERT INTO tutoria VALUES ('Bruno', 'ciencias', 'Claudio Mella');
INSERT INTO tutoria VALUES ('Carla', 'lenguaje', 'Hugo Neira');
INSERT INTO tutoria VALUES ('Carla', 'matemática', 'Valeria Sáez');
INSERT INTO tutor SELECT DISTINCT tutor, ramo FROM tutoria;
INSERT INTO asignacion SELECT alumno, tutor FROM tutoria;

-- @t1 3FN: un segundo tutor de matemática para Amanda
INSERT INTO tutoria VALUES ('Amanda', 'matemática', 'Ignacio Pino');
-- @t2 3FN: Valeria Sáez aparece enseñando lenguaje
INSERT INTO tutoria VALUES ('Diego', 'lenguaje', 'Valeria Sáez');
-- @t2_ver
SELECT tutor, COUNT(DISTINCT ramo) AS ramos FROM tutoria GROUP BY tutor HAVING COUNT(DISTINCT ramo) > 1;
-- @b1 FNBC: un segundo tutor de matemática para Amanda
INSERT INTO asignacion VALUES ('Amanda', 'Ignacio Pino');
-- @b1_ver
SELECT a.alumno, t.ramo, COUNT(*) AS tutores
FROM asignacion a JOIN tutor t ON t.tutor = a.tutor
GROUP BY a.alumno, t.ramo
HAVING COUNT(*) > 1;
-- @b2 FNBC: Valeria Sáez enseñando lenguaje
INSERT INTO tutor VALUES ('Valeria Sáez', 'lenguaje');
