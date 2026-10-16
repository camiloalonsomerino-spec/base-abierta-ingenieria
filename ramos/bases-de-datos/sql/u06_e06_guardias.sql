-- Ejercicio 6.6 · turnos de guardias de un condominio de Iquique (datos inventados)
-- Regla: cada guardia trabaja siempre en la misma portería.
CREATE TABLE turno (
    guardia  VARCHAR(30) NOT NULL,
    dia      VARCHAR(10) NOT NULL,
    porteria VARCHAR(10) NOT NULL,
    PRIMARY KEY (guardia, dia)
);
INSERT INTO turno VALUES ('Rubén', 'lunes', 'norte');
INSERT INTO turno VALUES ('Elsa', 'lunes', 'sur');
INSERT INTO turno VALUES ('Rubén', 'martes', 'norte');
INSERT INTO turno VALUES ('Mauricio', 'martes', 'sur');
INSERT INTO turno VALUES ('Ximena', 'miércoles', 'norte');
INSERT INTO turno VALUES ('Elsa', 'miércoles', 'sur');
INSERT INTO turno VALUES ('Ximena', 'jueves', 'norte');
INSERT INTO turno VALUES ('Mauricio', 'jueves', 'sur');

-- Descomposición A: (guardia, dia) y (dia, porteria)
CREATE TABLE a_gd AS SELECT DISTINCT guardia, dia FROM turno;
CREATE TABLE a_dp AS SELECT DISTINCT dia, porteria FROM turno;
-- Descomposición B: (guardia, dia) y (guardia, porteria)
CREATE TABLE b_gd AS SELECT DISTINCT guardia, dia FROM turno;
CREATE TABLE b_gp AS SELECT DISTINCT guardia, porteria FROM turno;

-- @a el join de la descomposición A
SELECT (SELECT COUNT(*) FROM turno) AS filas_originales,
       (SELECT COUNT(*) FROM (SELECT x.guardia, x.dia, y.porteria
                              FROM a_gd x JOIN a_dp y ON y.dia = x.dia)) AS filas_join,
       (SELECT COUNT(*) FROM (SELECT x.guardia, x.dia, y.porteria
                              FROM a_gd x JOIN a_dp y ON y.dia = x.dia
                              EXCEPT SELECT * FROM turno)) AS espurias;
-- @a_ejemplo las filas inventadas del lunes
SELECT x.guardia, x.dia, y.porteria
FROM a_gd x JOIN a_dp y ON y.dia = x.dia
WHERE x.dia = 'lunes'
EXCEPT SELECT * FROM turno;
-- @b el join de la descomposición B
SELECT (SELECT COUNT(*) FROM turno) AS filas_originales,
       (SELECT COUNT(*) FROM (SELECT x.guardia, x.dia, y.porteria
                              FROM b_gd x JOIN b_gp y ON y.guardia = x.guardia)) AS filas_join,
       (SELECT COUNT(*) FROM (SELECT x.guardia, x.dia, y.porteria
                              FROM b_gd x JOIN b_gp y ON y.guardia = x.guardia
                              EXCEPT SELECT * FROM turno)) AS espurias;
