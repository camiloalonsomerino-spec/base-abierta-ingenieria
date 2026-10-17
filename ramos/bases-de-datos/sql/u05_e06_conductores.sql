-- Ejercicio 5.6 · escuela de conductores de Curicó (datos inventados)
CREATE TABLE matricula (
    rut     VARCHAR(12) NOT NULL,
    nombre  VARCHAR(60) NOT NULL,
    curso   VARCHAR(20) NOT NULL,
    horario VARCHAR(20) NOT NULL
);
INSERT INTO matricula VALUES ('41.314.391-8', 'Carolina Muñoz', 'clase B', 'martes 18:00');
INSERT INTO matricula VALUES ('41.314.391-8', 'Carolina Muñoz', 'mecánica básica', 'jueves 19:30');
INSERT INTO matricula VALUES ('40.101.107-2', 'Pedro Araya', 'clase A2', 'lunes 17:00');
INSERT INTO matricula VALUES ('41.819.926-1', 'Valentina Rojas', 'clase B', 'martes 18:00');
INSERT INTO matricula VALUES ('40.202.214-0', 'Jorge Lillo', 'mecánica básica', 'jueves 19:30');
INSERT INTO matricula VALUES ('44.044.280-3', 'Camila Soto', 'clase A2', 'lunes 17:00');
INSERT INTO matricula VALUES ('41.819.926-1', 'Valentina Rojas', 'clase C', 'sábado 11:00');
INSERT INTO matricula VALUES ('40.202.214-0', 'Jorge Lillo', 'clase C', 'sábado 11:00');

-- @rut
SELECT rut, COUNT(*) FROM matricula GROUP BY rut HAVING COUNT(*) > 1;
-- @nombre_curso
SELECT nombre, curso, COUNT(*) FROM matricula GROUP BY nombre, curso HAVING COUNT(*) > 1;

CREATE TABLE matricula_mal (
    rut     VARCHAR(12) NOT NULL,
    nombre  VARCHAR(60) NOT NULL,
    curso   VARCHAR(20) NOT NULL,
    horario VARCHAR(20) NOT NULL,
    PRIMARY KEY (nombre, curso)
);
CREATE TABLE matricula_bien (
    rut     VARCHAR(12) NOT NULL,
    nombre  VARCHAR(60) NOT NULL,
    curso   VARCHAR(20) NOT NULL,
    horario VARCHAR(20) NOT NULL,
    PRIMARY KEY (rut, curso),
    UNIQUE (rut, horario)
);
INSERT INTO matricula_mal SELECT * FROM matricula;
INSERT INTO matricula_bien SELECT * FROM matricula;
-- @mal llega otro Pedro Araya al curso clase A2
INSERT INTO matricula_mal VALUES ('42.426.568-3', 'Pedro Araya', 'clase A2', 'lunes 17:00');
-- @bien el mismo Pedro, con las claves que dicen las reglas
INSERT INTO matricula_bien VALUES ('42.426.568-3', 'Pedro Araya', 'clase A2', 'lunes 17:00');
-- @choque Carolina pide un segundo curso el martes a las 18:00
INSERT INTO matricula_bien VALUES ('41.314.391-8', 'Carolina Muñoz', 'clase D', 'martes 18:00');
