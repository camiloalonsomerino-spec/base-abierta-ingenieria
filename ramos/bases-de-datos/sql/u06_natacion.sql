-- Unidad 6 · Ejemplo resuelto · la planilla de un club de natación de Coquimbo (datos inventados)
-- Las líneas «-- @nombre» marcan las consultas que el verificador muestra con su resultado.
PRAGMA foreign_keys = ON;

CREATE TABLE planilla (
    rut           VARCHAR(12) NOT NULL,
    nadador       VARCHAR(60) NOT NULL,
    curso         VARCHAR(4)  NOT NULL,
    nivel         VARCHAR(12) NOT NULL,
    horario       VARCHAR(20) NOT NULL,
    piscina       VARCHAR(12) NOT NULL,
    profesor      VARCHAR(60) NOT NULL,
    fono_profesor VARCHAR(16) NOT NULL,
    mensualidad   INTEGER NOT NULL,
    PRIMARY KEY (rut, curso)
);
INSERT INTO planilla VALUES ('23.456.781-0', 'Sofía Tapia', 'C1', 'inicial', 'lun y mié 17:00', 'temperada', 'Paz Rivera', '+56 9 5521 7740', 26500);
INSERT INTO planilla VALUES ('23.987.654-4', 'Benjamín Rojas', 'C1', 'inicial', 'lun y mié 17:00', 'temperada', 'Paz Rivera', '+56 9 5521 7740', 26500);
INSERT INTO planilla VALUES ('23.987.654-4', 'Benjamín Rojas', 'C2', 'inicial', 'mar y jue 18:00', 'olímpica', 'Iván Toro', '+56 9 6034 1187', 26500);
INSERT INTO planilla VALUES ('24.110.392-7', 'Antonia Vega', 'C3', 'intermedio', 'lun y mié 18:30', 'temperada', 'Paz Rivera', '+56 9 5521 7740', 30500);
INSERT INTO planilla VALUES ('22.876.013-7', 'Tomás Carvajal', 'C3', 'intermedio', 'lun y mié 18:30', 'temperada', 'Paz Rivera', '+56 9 5521 7740', 30500);
INSERT INTO planilla VALUES ('22.876.013-7', 'Tomás Carvajal', 'C4', 'avanzado', 'sáb 10:00', 'olímpica', 'Rocío Godoy', '+56 9 7712 9065', 34500);
INSERT INTO planilla VALUES ('23.345.109-6', 'Emilia Araya', 'C1', 'inicial', 'lun y mié 17:00', 'temperada', 'Paz Rivera', '+56 9 5521 7740', 26500);
INSERT INTO planilla VALUES ('24.567.820-7', 'Gaspar Olivares', 'C4', 'avanzado', 'sáb 10:00', 'olímpica', 'Rocío Godoy', '+56 9 7712 9065', 34500);
INSERT INTO planilla VALUES ('23.001.457-4', 'Josefa Muñoz', 'C1', 'inicial', 'lun y mié 17:00', 'temperada', 'Paz Rivera', '+56 9 5521 7740', 26500);
INSERT INTO planilla VALUES ('23.001.457-4', 'Josefa Muñoz', 'C3', 'intermedio', 'lun y mié 18:30', 'temperada', 'Paz Rivera', '+56 9 5521 7740', 30500);

-- @origen así la llevaba la secretaria: una fila por nadador y los cursos en una celda
SELECT rut, nadador, GROUP_CONCAT(curso, ', ' ORDER BY curso) AS cursos
FROM planilla
GROUP BY rut, nadador
ORDER BY nadador;
-- @dfs cuántos valores distintos toma el lado derecho por cada valor del izquierdo (1 = se cumple)
SELECT 'rut → nadador' AS dependencia, MAX(n) AS maximo
FROM (SELECT COUNT(DISTINCT nadador) AS n FROM planilla GROUP BY rut)
UNION ALL
SELECT 'curso → profesor', MAX(n)
FROM (SELECT COUNT(DISTINCT profesor) AS n FROM planilla GROUP BY curso)
UNION ALL
SELECT 'profesor → fono_profesor', MAX(n)
FROM (SELECT COUNT(DISTINCT fono_profesor) AS n FROM planilla GROUP BY profesor)
UNION ALL
SELECT 'nivel → mensualidad', MAX(n)
FROM (SELECT COUNT(DISTINCT mensualidad) AS n FROM planilla GROUP BY nivel);
-- @repetido cuántas veces está escrito el teléfono de cada profesor
SELECT profesor, fono_profesor, COUNT(*) AS veces
FROM planilla
GROUP BY profesor, fono_profesor
ORDER BY veces DESC;

-- La descomposición en tercera forma normal
CREATE TABLE tarifa (
    nivel       VARCHAR(12) NOT NULL PRIMARY KEY,
    mensualidad INTEGER NOT NULL
);
CREATE TABLE profesor (
    nombre      VARCHAR(60) NOT NULL PRIMARY KEY,
    fono        VARCHAR(16) NOT NULL
);
CREATE TABLE curso (
    curso       VARCHAR(4)  NOT NULL PRIMARY KEY,
    nivel       VARCHAR(12) NOT NULL,
    horario     VARCHAR(20) NOT NULL,
    piscina     VARCHAR(12) NOT NULL,
    profesor    VARCHAR(60) NOT NULL,
    FOREIGN KEY (nivel) REFERENCES tarifa (nivel),
    FOREIGN KEY (profesor) REFERENCES profesor (nombre)
);
CREATE TABLE nadador (
    rut         VARCHAR(12) NOT NULL PRIMARY KEY,
    nombre      VARCHAR(60) NOT NULL
);
CREATE TABLE inscripcion (
    rut         VARCHAR(12) NOT NULL,
    curso       VARCHAR(4)  NOT NULL,
    PRIMARY KEY (rut, curso),
    FOREIGN KEY (rut) REFERENCES nadador (rut),
    FOREIGN KEY (curso) REFERENCES curso (curso)
);
INSERT INTO tarifa SELECT DISTINCT nivel, mensualidad FROM planilla;
INSERT INTO profesor SELECT DISTINCT profesor, fono_profesor FROM planilla;
INSERT INTO curso SELECT DISTINCT curso, nivel, horario, piscina, profesor FROM planilla;
INSERT INTO nadador SELECT DISTINCT rut, nadador FROM planilla;
INSERT INTO inscripcion SELECT rut, curso FROM planilla;

-- @filas cuántas filas quedó en cada tabla
SELECT 'tarifa' AS tabla, COUNT(*) AS filas FROM tarifa
UNION ALL SELECT 'profesor', COUNT(*) FROM profesor
UNION ALL SELECT 'curso', COUNT(*) FROM curso
UNION ALL SELECT 'nadador', COUNT(*) FROM nadador
UNION ALL SELECT 'inscripcion', COUNT(*) FROM inscripcion;
-- @reconstruir el join de las cinco tablas contra la planilla, en los dos sentidos
SELECT
  (SELECT COUNT(*) FROM planilla) AS filas_planilla,
  (SELECT COUNT(*) FROM (
     SELECT i.rut, n.nombre, i.curso, c.nivel, c.horario, c.piscina, c.profesor, p.fono, t.mensualidad
     FROM inscripcion i
     JOIN nadador n  ON n.rut = i.rut
     JOIN curso c    ON c.curso = i.curso
     JOIN profesor p ON p.nombre = c.profesor
     JOIN tarifa t   ON t.nivel = c.nivel)) AS filas_join,
  (SELECT COUNT(*) FROM (
     SELECT * FROM planilla
     EXCEPT
     SELECT i.rut, n.nombre, i.curso, c.nivel, c.horario, c.piscina, c.profesor, p.fono, t.mensualidad
     FROM inscripcion i
     JOIN nadador n  ON n.rut = i.rut
     JOIN curso c    ON c.curso = i.curso
     JOIN profesor p ON p.nombre = c.profesor
     JOIN tarifa t   ON t.nivel = c.nivel)) AS faltan,
  (SELECT COUNT(*) FROM (
     SELECT i.rut, n.nombre, i.curso, c.nivel, c.horario, c.piscina, c.profesor, p.fono, t.mensualidad
     FROM inscripcion i
     JOIN nadador n  ON n.rut = i.rut
     JOIN curso c    ON c.curso = i.curso
     JOIN profesor p ON p.nombre = c.profesor
     JOIN tarifa t   ON t.nivel = c.nivel
     EXCEPT
     SELECT * FROM planilla)) AS sobran;

-- Las tres anomalías, ahora sobre la planilla
-- @a_insercion un curso nuevo que todavía no tiene nadadores
INSERT INTO planilla (curso, nivel, horario, piscina, profesor, fono_profesor, mensualidad)
VALUES ('C5', 'avanzado', 'dom 09:00', 'olímpica', 'Rocío Godoy', '+56 9 7712 9065', 34500);
-- @a_insercion_bien en las tablas normalizadas entra sin problema
INSERT INTO curso VALUES ('C5', 'avanzado', 'dom 09:00', 'olímpica', 'Rocío Godoy');
-- @a_actualizacion Paz Rivera cambia de teléfono y alguien lo corrige solo en las filas del curso C1
UPDATE planilla SET fono_profesor = '+56 9 8840 2215' WHERE curso = 'C1';
-- @a_actualizacion_ver
SELECT profesor, COUNT(DISTINCT fono_profesor) AS telefonos
FROM planilla
GROUP BY profesor
HAVING COUNT(DISTINCT fono_profesor) > 1;
-- @a_borrado Benjamín deja el curso C2, el único de Iván Toro
DELETE FROM planilla WHERE rut = '23.987.654-4' AND curso = 'C2';
-- @a_borrado_ver
SELECT COUNT(*) AS filas_con_ivan FROM planilla WHERE profesor = 'Iván Toro';
