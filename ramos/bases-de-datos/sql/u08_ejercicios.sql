-- Unidad 8 · SQL para crear y modificar · ejercicios 8.1 a 8.10 (pautas)
-- Cada ejercicio parte de una base vacía: el verificador abre una base nueva en cada bloque
-- cuya clave empieza con «base_». Para practicar, corre cada ejercicio en su propia base:
--   sqlite3 e1.db   y pega los bloques del ejercicio.
-- Algunas instrucciones FALLAN a propósito; el verificador exige el mensaje que cita la unidad.

-- @base_e1
PRAGMA foreign_keys = ON;
CREATE TABLE mascota (
    id_mascota INTEGER PRIMARY KEY,
    nombre     VARCHAR(30) NOT NULL,
    especie    VARCHAR(10) NOT NULL CHECK (especie IN ('perro', 'gato', 'otro')),
    fecha_nac  DATE,
    peso_kg    DECIMAL(5,1) CHECK (peso_kg > 0),
    rut_dueno  VARCHAR(12) NOT NULL
);
INSERT INTO mascota (nombre, especie, fecha_nac, peso_kg, rut_dueno)
VALUES ('Canela', 'perro', '2019-05-14', 12.5, '18.904.265-5');
SELECT * FROM mascota;

-- @e1_falla_especie
INSERT INTO mascota (nombre, especie, rut_dueno) VALUES ('Pirata', 'loro', '18.904.265-5');

-- @e1_falla_peso
INSERT INTO mascota (nombre, especie, peso_kg, rut_dueno) VALUES ('Mota', 'gato', 0, '18.904.265-5');

-- @base_e2
CREATE TABLE prueba (comuna VARCHAR(5));
INSERT INTO prueba VALUES ('Concepción');
SELECT comuna, length(comuna) FROM prueba;

-- @e2_fechas_texto
CREATE TABLE control (fecha_txt VARCHAR(10), fecha_iso DATE);
INSERT INTO control VALUES ('07/03/2026', '2026-03-07'), ('15/01/2026', '2026-01-15'), ('28/02/2025', '2025-02-28');
SELECT fecha_txt FROM control ORDER BY fecha_txt;

-- @e2_fechas_iso
SELECT fecha_iso FROM control ORDER BY fecha_iso;

-- @base_e3
CREATE TABLE socio (
    id_socio  INTEGER PRIMARY KEY,
    nombre    VARCHAR(40) NOT NULL,
    categoria VARCHAR(10) NOT NULL DEFAULT 'adulto',
    cuota     INTEGER DEFAULT 14500,
    activo    INTEGER NOT NULL DEFAULT 1
);
INSERT INTO socio VALUES (1, 'Antonia Bravo', 'juvenil', 9800, 1);
INSERT INTO socio (nombre) VALUES ('Raúl Espinoza');
INSERT INTO socio (nombre, cuota) VALUES ('Gloria Pinto', NULL);
INSERT INTO socio (nombre, categoria, activo) VALUES ('Sergio Vidal', 'senior', 0);
SELECT * FROM socio;

-- @base_e4
PRAGMA foreign_keys = ON;
CREATE TABLE box (
    id_box  INTEGER PRIMARY KEY,
    piso    INTEGER NOT NULL
);
CREATE TABLE atencion (
    id_atencion INTEGER PRIMARY KEY,
    fecha       DATE NOT NULL,
    id_box      INTEGER NOT NULL,
    FOREIGN KEY (id_box) REFERENCES box(id_box)
);

-- @e4_falla_orden
INSERT INTO atencion VALUES (1, '2026-11-05', 3);

-- @e4_orden
INSERT INTO box VALUES (3, 1), (7, 2);
INSERT INTO atencion VALUES (1, '2026-11-05', 3), (2, '2026-11-05', 7), (3, '2026-11-06', 3);
SELECT COUNT(*) FROM atencion;

-- @e4_falla_drop
DROP TABLE box;

-- @e4_drop
DROP TABLE atencion;
DROP TABLE box;
SELECT COUNT(*) FROM sqlite_master WHERE type = 'table';

-- @base_e5
CREATE TABLE puesto (
    id_puesto INTEGER PRIMARY KEY,
    titular   VARCHAR(40) NOT NULL,
    metros    INTEGER NOT NULL
);
INSERT INTO puesto VALUES (1, 'Olga Retamal', 6), (2, 'Juan Saavedra', 9), (3, 'Elsa Fuentealba', 4);
ALTER TABLE puesto ADD COLUMN rubro VARCHAR(20) NOT NULL DEFAULT 'verduras';
ALTER TABLE puesto RENAME COLUMN metros TO metros2;
SELECT * FROM puesto;

-- @e5_falla_modify
ALTER TABLE puesto MODIFY COLUMN metros2 DECIMAL(4,1);

-- @e5_reconstruir
CREATE TABLE puesto_nueva (
    id_puesto INTEGER PRIMARY KEY,
    titular   VARCHAR(40) NOT NULL,
    metros2   DECIMAL(4,1) NOT NULL CHECK (metros2 > 0),
    rubro     VARCHAR(20) NOT NULL DEFAULT 'verduras'
);
INSERT INTO puesto_nueva (id_puesto, titular, metros2, rubro)
SELECT id_puesto, titular, metros2, rubro FROM puesto;
DROP TABLE puesto;
ALTER TABLE puesto_nueva RENAME TO puesto;
UPDATE puesto SET metros2 = 4.5 WHERE id_puesto = 3;
SELECT * FROM puesto;

-- @e5_drop_column
ALTER TABLE puesto DROP COLUMN rubro;
SELECT * FROM puesto;

-- @base_e6
CREATE TABLE articulo (
    id_articulo INTEGER PRIMARY KEY,
    nombre      VARCHAR(40) NOT NULL,
    categoria   VARCHAR(20) NOT NULL,
    precio      INTEGER NOT NULL CHECK (precio > 0)
);
INSERT INTO articulo VALUES
    (1, 'cuaderno universitario 100 hojas', 'cuaderno', 1490),
    (2, 'cuaderno college 80 hojas', 'cuaderno', 1190),
    (3, 'lápiz grafito caja 12', 'escritura', 2350),
    (4, 'goma de borrar', 'escritura', 390),
    (5, 'cuaderno croquis', 'cuaderno', 2190),
    (6, 'regla 30 cm', 'geometría', 650);

-- @e6_update
UPDATE articulo
SET precio = ROUND(precio * 1.08 / 10) * 10
WHERE categoria = 'cuaderno';
SELECT changes();

-- @e6_resultado
SELECT * FROM articulo;

-- @e6_typeof
SELECT typeof(precio) FROM articulo WHERE id_articulo = 1;

-- @base_e7_restrict
PRAGMA foreign_keys = ON;
CREATE TABLE club (id_club INTEGER PRIMARY KEY, nombre VARCHAR(30) NOT NULL);
CREATE TABLE inscrito (
    id_inscrito INTEGER PRIMARY KEY,
    nombre      VARCHAR(40) NOT NULL,
    id_club     INTEGER,
    FOREIGN KEY (id_club) REFERENCES club(id_club)
);
INSERT INTO club VALUES (1, 'ajedrez'), (2, 'robótica');
INSERT INTO inscrito VALUES (1, 'Amanda', 1), (2, 'Bruno', 2), (3, 'Catalina', 2), (4, 'Damián', 1), (5, 'Elena', 2);

-- @e7_falla_restrict
DELETE FROM club WHERE id_club = 2;

-- @base_e7_cascade
PRAGMA foreign_keys = ON;
CREATE TABLE club (id_club INTEGER PRIMARY KEY, nombre VARCHAR(30) NOT NULL);
CREATE TABLE inscrito (
    id_inscrito INTEGER PRIMARY KEY,
    nombre      VARCHAR(40) NOT NULL,
    id_club     INTEGER,
    FOREIGN KEY (id_club) REFERENCES club(id_club) ON DELETE CASCADE
);
INSERT INTO club VALUES (1, 'ajedrez'), (2, 'robótica');
INSERT INTO inscrito VALUES (1, 'Amanda', 1), (2, 'Bruno', 2), (3, 'Catalina', 2), (4, 'Damián', 1), (5, 'Elena', 2);
DELETE FROM club WHERE id_club = 2;
SELECT * FROM inscrito;

-- @base_e7_set_null
PRAGMA foreign_keys = ON;
CREATE TABLE club (id_club INTEGER PRIMARY KEY, nombre VARCHAR(30) NOT NULL);
CREATE TABLE inscrito (
    id_inscrito INTEGER PRIMARY KEY,
    nombre      VARCHAR(40) NOT NULL,
    id_club     INTEGER,
    FOREIGN KEY (id_club) REFERENCES club(id_club) ON DELETE SET NULL
);
INSERT INTO club VALUES (1, 'ajedrez'), (2, 'robótica');
INSERT INTO inscrito VALUES (1, 'Amanda', 1), (2, 'Bruno', 2), (3, 'Catalina', 2), (4, 'Damián', 1), (5, 'Elena', 2);
DELETE FROM club WHERE id_club = 2;
SELECT * FROM inscrito;

-- @base_e8_rowid
CREATE TABLE ticket (id_ticket INTEGER PRIMARY KEY, detalle VARCHAR(40) NOT NULL);
INSERT INTO ticket (detalle) VALUES ('impresora sin tóner'), ('wifi del segundo piso'), ('clave bloqueada');
DELETE FROM ticket WHERE id_ticket = 3;
INSERT INTO ticket (detalle) VALUES ('monitor parpadea');
SELECT * FROM ticket;

-- @base_e8_autoinc
CREATE TABLE ticket (id_ticket INTEGER PRIMARY KEY AUTOINCREMENT, detalle VARCHAR(40) NOT NULL);
INSERT INTO ticket (detalle) VALUES ('impresora sin tóner'), ('wifi del segundo piso'), ('clave bloqueada');
DELETE FROM ticket WHERE id_ticket = 3;
INSERT INTO ticket (detalle) VALUES ('monitor parpadea');
SELECT * FROM ticket;

-- @base_e9
PRAGMA foreign_keys = ON;
CREATE TABLE medico (
    id_medico  INTEGER PRIMARY KEY,
    nombre     VARCHAR(40) NOT NULL,
    fono       INTEGER
);

-- @e9_falla_fk_sintaxis
CREATE TABLE hora (
    id_hora   INTEGER PRIMARY KEY,
    fecha     DATE NOT NULL,
    id_medico INTEGER NOT NULL,
    FOREIGN KEY id_medico REFERENCES medico(id_medico)
);

-- @e9_falla_modify
ALTER TABLE medico MODIFY COLUMN fono telefono VARCHAR(15);

-- @e9_falla_comillas
INSERT INTO medico VALUES (1, Pedro Alarcón, 412345678);

-- @e9_falla_columna
UPDATE medico SET nombre = 'Pedro Alarcón Rojas' WHERE id_doctor = 1;

-- @e9_corregido
DROP TABLE medico;
CREATE TABLE medico (
    id_medico  INTEGER PRIMARY KEY,
    nombre     VARCHAR(40) NOT NULL,
    telefono   VARCHAR(15)
);
CREATE TABLE hora (
    id_hora   INTEGER PRIMARY KEY,
    fecha     DATE NOT NULL,
    id_medico INTEGER NOT NULL,
    FOREIGN KEY (id_medico) REFERENCES medico(id_medico)
);
INSERT INTO medico VALUES (1, 'Pedro Alarcón', '+56 41 234 5678');
INSERT INTO hora VALUES (1, '2026-11-05', 1);
UPDATE medico SET nombre = 'Pedro Alarcón Rojas' WHERE id_medico = 1;
SELECT h.id_hora, h.fecha, m.nombre, m.telefono FROM hora h JOIN medico m ON m.id_medico = h.id_medico;

-- @e9_fecha
INSERT INTO hora VALUES (2, '05/11/2026', 1);
SELECT id_hora, fecha, date(fecha) FROM hora;

-- @base_e10
CREATE TABLE articulo (
    id_articulo INTEGER PRIMARY KEY,
    nombre      VARCHAR(40) NOT NULL,
    categoria   VARCHAR(20) NOT NULL,
    precio      INTEGER NOT NULL CHECK (precio > 0)
);
INSERT INTO articulo VALUES
    (1, 'cuaderno universitario 100 hojas', 'cuaderno', 1610),
    (2, 'cuaderno college 80 hojas', 'cuaderno', 1290),
    (3, 'lápiz grafito caja 12', 'escritura', 2350),
    (4, 'goma de borrar', 'escritura', 390),
    (5, 'cuaderno croquis', 'cuaderno', 2370),
    (6, 'regla 30 cm', 'geometría', 650);
CREATE TABLE articulo_respaldo AS SELECT * FROM articulo;
UPDATE articulo SET precio = 2490 WHERE id_articulo = 3;

-- @e10_error
UPDATE articulo SET precio = 450;
SELECT changes();

-- @e10_restaurar
UPDATE articulo
SET precio = (SELECT r.precio FROM articulo_respaldo r WHERE r.id_articulo = articulo.id_articulo)
WHERE id_articulo <> 3;
UPDATE articulo SET precio = 2490 WHERE id_articulo = 3;
UPDATE articulo SET precio = 450 WHERE id_articulo = 4;
SELECT * FROM articulo;

-- @e10_guardia
BEGIN;
UPDATE articulo SET precio = 450;
SELECT changes();

-- @e10_rollback
ROLLBACK;
SELECT precio FROM articulo WHERE id_articulo = 1;
