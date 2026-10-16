-- Unidad 4 · Del modelo entidad-relación al modelo relacional
-- Base abierta de ingeniería · Bases de Datos
--
-- Crea en una base vacía las tablas del ejemplo (clínica veterinaria Patitas del Sur) y las de los
-- ejercicios 4.5, 4.6, 4.8 y 4.10, las llena y corre las consultas de la unidad.
--   sqlite3 u04.db < sql/u04_mer_a_relacional.sql
--
-- SQLite: las claves foráneas se revisan solo con PRAGMA foreign_keys = ON (MySQL las revisa siempre).
-- MySQL no tiene DEFERRABLE: crea sede sin su clave foránea, carga los datos y agrégala al final con
--   ALTER TABLE sede ADD FOREIGN KEY (rut_director) REFERENCES veterinario(rut);
PRAGMA foreign_keys = ON;

-- @crear vet_tablas
CREATE TABLE sede (
    cod_sede     VARCHAR(3)  NOT NULL,
    nombre       VARCHAR(30) NOT NULL,
    direccion    VARCHAR(60) NOT NULL,
    rut_director VARCHAR(12) NOT NULL UNIQUE,
    PRIMARY KEY (cod_sede),
    FOREIGN KEY (rut_director) REFERENCES veterinario(rut) DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE personal (
    rut           VARCHAR(12) NOT NULL,
    nombre        VARCHAR(60) NOT NULL,
    fecha_ingreso DATE        NOT NULL,
    cod_sede      VARCHAR(3)  NOT NULL,
    PRIMARY KEY (rut),
    FOREIGN KEY (cod_sede) REFERENCES sede(cod_sede)
);
CREATE TABLE veterinario (
    rut         VARCHAR(12) NOT NULL,
    colegiatura VARCHAR(10) NOT NULL,
    PRIMARY KEY (rut),
    FOREIGN KEY (rut) REFERENCES personal(rut)
);
CREATE TABLE tecnico (
    rut   VARCHAR(12) NOT NULL,
    turno VARCHAR(6)  NOT NULL,
    PRIMARY KEY (rut),
    FOREIGN KEY (rut) REFERENCES personal(rut)
);
CREATE TABLE tutor (
    rut_tutor VARCHAR(12) NOT NULL,
    nombre    VARCHAR(60) NOT NULL,
    calle     VARCHAR(40) NOT NULL,
    numero    INTEGER     NOT NULL,
    comuna    VARCHAR(30) NOT NULL,
    PRIMARY KEY (rut_tutor)
);
CREATE TABLE telefono_tutor (
    rut_tutor VARCHAR(12) NOT NULL,
    telefono  VARCHAR(16) NOT NULL,
    PRIMARY KEY (rut_tutor, telefono),
    FOREIGN KEY (rut_tutor) REFERENCES tutor(rut_tutor)
);
CREATE TABLE mascota (
    rut_tutor VARCHAR(12) NOT NULL,
    nombre    VARCHAR(30) NOT NULL,
    especie   VARCHAR(20) NOT NULL,
    fecha_nac DATE,
    PRIMARY KEY (rut_tutor, nombre),
    FOREIGN KEY (rut_tutor) REFERENCES tutor(rut_tutor)
);
CREATE TABLE atencion (
    num_atencion    INTEGER     NOT NULL,
    fecha           DATE        NOT NULL,
    motivo          VARCHAR(80) NOT NULL,
    rut_tutor       VARCHAR(12) NOT NULL,
    nombre_mascota  VARCHAR(30) NOT NULL,
    rut_veterinario VARCHAR(12) NOT NULL,
    PRIMARY KEY (num_atencion),
    FOREIGN KEY (rut_tutor, nombre_mascota) REFERENCES mascota(rut_tutor, nombre),
    FOREIGN KEY (rut_veterinario) REFERENCES veterinario(rut)
);
CREATE TABLE vacuna (
    cod_vacuna VARCHAR(3)  NOT NULL,
    nombre     VARCHAR(40) NOT NULL,
    PRIMARY KEY (cod_vacuna)
);
CREATE TABLE aplica (
    num_atencion INTEGER     NOT NULL,
    cod_vacuna   VARCHAR(3)  NOT NULL,
    lote         VARCHAR(12) NOT NULL,
    PRIMARY KEY (num_atencion, cod_vacuna),
    FOREIGN KEY (num_atencion) REFERENCES atencion(num_atencion),
    FOREIGN KEY (cod_vacuna) REFERENCES vacuna(cod_vacuna)
);
CREATE TABLE laboratorio (
    rut_lab VARCHAR(12) NOT NULL,
    nombre  VARCHAR(40) NOT NULL,
    PRIMARY KEY (rut_lab)
);
CREATE TABLE provee (
    rut_lab    VARCHAR(12) NOT NULL,
    cod_vacuna VARCHAR(3)  NOT NULL,
    cod_sede   VARCHAR(3)  NOT NULL,
    precio     INTEGER     NOT NULL,
    PRIMARY KEY (cod_vacuna, cod_sede),
    FOREIGN KEY (rut_lab) REFERENCES laboratorio(rut_lab),
    FOREIGN KEY (cod_vacuna) REFERENCES vacuna(cod_vacuna),
    FOREIGN KEY (cod_sede) REFERENCES sede(cod_sede)
);

-- @datos vet_datos
BEGIN;
INSERT INTO sede VALUES ('CEN', 'Centro', 'Urmeneta 512', '13.482.906-0');
INSERT INTO sede VALUES ('ALE', 'Alerce', 'Av. Los Notros 1840', '16.937.214-4');
INSERT INTO personal VALUES ('13.482.906-0', 'Daniela Ojeda', '2018-03-05', 'CEN');
INSERT INTO personal VALUES ('16.937.214-4', 'Matías Barría', '2021-08-16', 'ALE');
INSERT INTO personal VALUES ('19.205.873-2', 'Fernanda Mansilla', '2023-01-09', 'CEN');
INSERT INTO personal VALUES ('12.774.351-7', 'Jorge Cárcamo', '2017-05-11', 'CEN');
INSERT INTO personal VALUES ('18.360.429-5', 'Valentina Soto', '2022-10-03', 'ALE');
INSERT INTO personal VALUES ('20.118.645-5', 'Paula Alvarado', '2025-02-19', 'ALE');
INSERT INTO veterinario VALUES ('13.482.906-0', 'MV-2231');
INSERT INTO veterinario VALUES ('16.937.214-4', 'MV-3017');
INSERT INTO veterinario VALUES ('19.205.873-2', 'MV-3842');
INSERT INTO tecnico VALUES ('12.774.351-7', 'mañana');
INSERT INTO tecnico VALUES ('18.360.429-5', 'tarde');
INSERT INTO tutor VALUES ('15.630.218-K', 'Ignacio Paredes', 'Los Aromos', 245, 'Puerto Montt');
INSERT INTO tutor VALUES ('17.049.582-9', 'Rocío Gallardo', 'Pedro Montt', 1302, 'Puerto Montt');
INSERT INTO tutor VALUES ('11.893.760-0', 'Héctor Uribe', 'Chinquihue', 88, 'Puerto Montt');
INSERT INTO tutor VALUES ('19.876.031-5', 'Marcela Toledo', 'Bernardo Philippi', 77, 'Puerto Varas');
INSERT INTO telefono_tutor VALUES ('15.630.218-K', '+56 9 5550 0101');
INSERT INTO telefono_tutor VALUES ('15.630.218-K', '+56 9 5550 0102');
INSERT INTO telefono_tutor VALUES ('17.049.582-9', '+56 9 5550 0201');
INSERT INTO telefono_tutor VALUES ('11.893.760-0', '+56 9 5550 0301');
INSERT INTO telefono_tutor VALUES ('11.893.760-0', '+56 65 555 0302');
INSERT INTO telefono_tutor VALUES ('19.876.031-5', '+56 9 5550 0401');
INSERT INTO mascota VALUES ('15.630.218-K', 'Luna', 'perro', '2020-06-14');
INSERT INTO mascota VALUES ('15.630.218-K', 'Michi', 'gato', '2022-11-02');
INSERT INTO mascota VALUES ('17.049.582-9', 'Luna', 'gato', '2019-09-30');
INSERT INTO mascota VALUES ('11.893.760-0', 'Toby', 'perro', '2016-04-21');
INSERT INTO mascota VALUES ('11.893.760-0', 'Pelusa', 'conejo', '2024-01-08');
INSERT INTO mascota VALUES ('19.876.031-5', 'Rocky', 'perro', NULL);
INSERT INTO atencion VALUES (1, '2026-03-02', 'vacunación anual', '15.630.218-K', 'Luna', '13.482.906-0');
INSERT INTO atencion VALUES (2, '2026-03-02', 'control', '15.630.218-K', 'Michi', '13.482.906-0');
INSERT INTO atencion VALUES (3, '2026-03-09', 'vacunación', '17.049.582-9', 'Luna', '16.937.214-4');
INSERT INTO atencion VALUES (4, '2026-03-15', 'cojera', '11.893.760-0', 'Toby', '19.205.873-2');
INSERT INTO atencion VALUES (5, '2026-04-06', 'control de cojera', '11.893.760-0', 'Toby', '19.205.873-2');
INSERT INTO atencion VALUES (6, '2026-04-20', 'vacunación', '19.876.031-5', 'Rocky', '16.937.214-4');
INSERT INTO atencion VALUES (7, '2026-05-04', 'control', '15.630.218-K', 'Luna', '13.482.906-0');
INSERT INTO vacuna VALUES ('ANR', 'antirrábica');
INSERT INTO vacuna VALUES ('OCT', 'óctuple canina');
INSERT INTO vacuna VALUES ('TRF', 'triple felina');
INSERT INTO aplica VALUES (1, 'ANR', 'L-2611');
INSERT INTO aplica VALUES (1, 'OCT', 'L-2648');
INSERT INTO aplica VALUES (3, 'TRF', 'L-3105');
INSERT INTO aplica VALUES (6, 'ANR', 'L-2611');
INSERT INTO aplica VALUES (6, 'OCT', 'L-2702');
INSERT INTO laboratorio VALUES ('76.402.118-5', 'Andes Vet');
INSERT INTO laboratorio VALUES ('77.915.640-0', 'BioSur');
INSERT INTO provee VALUES ('76.402.118-5', 'ANR', 'CEN', 8900);
INSERT INTO provee VALUES ('77.915.640-0', 'ANR', 'ALE', 9300);
INSERT INTO provee VALUES ('76.402.118-5', 'OCT', 'CEN', 14500);
INSERT INTO provee VALUES ('76.402.118-5', 'OCT', 'ALE', 14900);
INSERT INTO provee VALUES ('77.915.640-0', 'TRF', 'CEN', 12700);
COMMIT;

-- @consulta v1_mascotas
SELECT t.nombre AS tutor, m.nombre AS mascota, m.especie
FROM mascota m
JOIN tutor t ON t.rut_tutor = m.rut_tutor
ORDER BY t.nombre, m.nombre;

-- @consulta v2_telefonos
SELECT t.nombre AS tutor, f.telefono
FROM telefono_tutor f
JOIN tutor t ON t.rut_tutor = f.rut_tutor
ORDER BY t.nombre, f.telefono;

-- @consulta v3_directores
SELECT s.nombre AS sede, p.nombre AS director, v.colegiatura
FROM sede s
JOIN veterinario v ON v.rut = s.rut_director
JOIN personal p ON p.rut = v.rut
ORDER BY s.nombre;

-- @consulta v4_vacunas_aplicadas
SELECT a.num_atencion, a.fecha, a.nombre_mascota, v.nombre AS vacuna, ap.lote
FROM aplica ap
JOIN atencion a ON a.num_atencion = ap.num_atencion
JOIN vacuna v ON v.cod_vacuna = ap.cod_vacuna
ORDER BY a.num_atencion, v.nombre;

-- @consulta v5_precio_antirrabica
SELECT s.nombre AS sede, l.nombre AS laboratorio, p.precio
FROM provee p
JOIN sede s ON s.cod_sede = p.cod_sede
JOIN laboratorio l ON l.rut_lab = p.rut_lab
WHERE p.cod_vacuna = 'ANR'
ORDER BY s.nombre;

-- @error v_err_tutor_inexistente
INSERT INTO mascota VALUES ('99.999.999-9', 'Kira', 'perro', NULL);

-- @error v_err_luna_repetida
INSERT INTO mascota VALUES ('15.630.218-K', 'Luna', 'gato', NULL);

-- @error v_err_director_repetido
UPDATE sede SET rut_director = '13.482.906-0' WHERE cod_sede = 'ALE';

-- @error v_err_tecnico_dirige
UPDATE sede SET rut_director = '12.774.351-7' WHERE cod_sede = 'ALE';

-- La misma jerarquía con la estrategia C: una sola tabla con discriminador.

-- @crear v_una_tabla
CREATE TABLE personal_una_tabla (
    rut           VARCHAR(12) NOT NULL,
    nombre        VARCHAR(60) NOT NULL,
    fecha_ingreso DATE        NOT NULL,
    tipo          VARCHAR(12),
    colegiatura   VARCHAR(10),
    turno         VARCHAR(6),
    cod_sede      VARCHAR(3)  NOT NULL,
    PRIMARY KEY (rut),
    FOREIGN KEY (cod_sede) REFERENCES sede(cod_sede)
);

-- @datos v_una_tabla_datos
INSERT INTO personal_una_tabla VALUES ('13.482.906-0', 'Daniela Ojeda', '2018-03-05', 'veterinario', 'MV-2231', NULL, 'CEN');
INSERT INTO personal_una_tabla VALUES ('16.937.214-4', 'Matías Barría', '2021-08-16', 'veterinario', 'MV-3017', NULL, 'ALE');
INSERT INTO personal_una_tabla VALUES ('19.205.873-2', 'Fernanda Mansilla', '2023-01-09', 'veterinario', 'MV-3842', NULL, 'CEN');
INSERT INTO personal_una_tabla VALUES ('12.774.351-7', 'Jorge Cárcamo', '2017-05-11', 'tecnico', NULL, 'mañana', 'CEN');
INSERT INTO personal_una_tabla VALUES ('18.360.429-5', 'Valentina Soto', '2022-10-03', 'tecnico', NULL, 'tarde', 'ALE');
INSERT INTO personal_una_tabla VALUES ('20.118.645-5', 'Paula Alvarado', '2025-02-19', NULL, NULL, NULL, 'ALE');

-- @consulta v6_nulos_una_tabla
SELECT COUNT(*) - COUNT(tipo) AS sin_tipo,
       COUNT(*) - COUNT(colegiatura) AS sin_colegiatura,
       COUNT(*) - COUNT(turno) AS sin_turno
FROM personal_una_tabla;

-- Ejercicio 4.5 · cuotas de una cooperativa de ahorro

-- @crear e45_tablas
CREATE TABLE credito (
    num_credito INTEGER NOT NULL,
    monto       INTEGER NOT NULL,
    plazo       INTEGER NOT NULL,
    PRIMARY KEY (num_credito)
);
CREATE TABLE cuota (
    num_credito INTEGER NOT NULL,
    numero      INTEGER NOT NULL,
    vence       DATE    NOT NULL,
    monto       INTEGER NOT NULL,
    PRIMARY KEY (num_credito, numero),
    FOREIGN KEY (num_credito) REFERENCES credito(num_credito)
);

-- @datos e45_datos
INSERT INTO credito VALUES (501, 1470000, 24);
INSERT INTO credito VALUES (502, 1173600, 24);
INSERT INTO cuota VALUES (501, 1, '2026-11-05', 61250);
INSERT INTO cuota VALUES (501, 2, '2026-12-05', 61250);
INSERT INTO cuota VALUES (501, 3, '2027-01-05', 61250);
INSERT INTO cuota VALUES (502, 1, '2026-11-20', 48900);
INSERT INTO cuota VALUES (502, 2, '2026-12-20', 48900);

-- @error e45_cuota_repetida
INSERT INTO cuota VALUES (501, 2, '2026-12-05', 61250);

-- @error e45_credito_inexistente
INSERT INTO cuota VALUES (503, 1, '2026-11-30', 52000);

-- @consulta e45_cuotas_por_credito
SELECT num_credito, COUNT(*) AS cuotas, SUM(monto) AS total
FROM cuota
GROUP BY num_credito
ORDER BY num_credito;

-- Ejercicio 4.6 · dónde va la clave foránea de una 1:1 (Cesfam)

-- @crear e46_tablas
CREATE TABLE sector_a (
    id_sector INTEGER     NOT NULL,
    nombre    VARCHAR(30) NOT NULL,
    rut_jefe  VARCHAR(12) NOT NULL UNIQUE,
    PRIMARY KEY (id_sector)
);
CREATE TABLE medico_b (
    rut_medico VARCHAR(12) NOT NULL,
    nombre     VARCHAR(60) NOT NULL,
    jefe_de    INTEGER UNIQUE,
    PRIMARY KEY (rut_medico)
);

-- @datos e46_datos
INSERT INTO sector_a VALUES (1, 'Verde', 'M03');
INSERT INTO sector_a VALUES (2, 'Azul', 'M07');
INSERT INTO sector_a VALUES (3, 'Rojo', 'M01');
INSERT INTO sector_a VALUES (4, 'Amarillo', 'M10');
INSERT INTO medico_b VALUES ('M01', 'Andrea Fuentes', 3);
INSERT INTO medico_b VALUES ('M02', 'Ignacio Henríquez', NULL);
INSERT INTO medico_b VALUES ('M03', 'Carolina Bustos', 1);
INSERT INTO medico_b VALUES ('M04', 'Felipe Cid', NULL);
INSERT INTO medico_b VALUES ('M05', 'Javiera Muñoz', NULL);
INSERT INTO medico_b VALUES ('M06', 'Tomás Riquelme', NULL);
INSERT INTO medico_b VALUES ('M07', 'Isidora Sepúlveda', 2);
INSERT INTO medico_b VALUES ('M08', 'Cristián Lagos', NULL);
INSERT INTO medico_b VALUES ('M09', 'Antonia Vera', NULL);
INSERT INTO medico_b VALUES ('M10', 'Diego Navarrete', 4);
INSERT INTO medico_b VALUES ('M11', 'Macarena Pino', NULL);

-- @consulta e46_nulos_en_sector
SELECT COUNT(*) AS filas, COUNT(*) - COUNT(rut_jefe) AS nulos
FROM sector_a;

-- @consulta e46_nulos_en_medico
SELECT COUNT(*) AS filas, COUNT(*) - COUNT(jefe_de) AS nulos
FROM medico_b;

-- Ejercicio 4.8 · la clave de una ternaria (agricultores en ferias de Ñuble)

-- @crear e48_tablas
CREATE TABLE lleva_a (
    agricultor VARCHAR(20) NOT NULL,
    feria      VARCHAR(20) NOT NULL,
    producto   VARCHAR(20) NOT NULL,
    precio_kg  INTEGER     NOT NULL,
    PRIMARY KEY (agricultor, feria, producto)
);
CREATE TABLE lleva_b (
    agricultor VARCHAR(20) NOT NULL,
    feria      VARCHAR(20) NOT NULL,
    producto   VARCHAR(20) NOT NULL,
    precio_kg  INTEGER     NOT NULL,
    PRIMARY KEY (agricultor, producto)
);

-- @datos e48_datos
INSERT INTO lleva_a VALUES ('Rosa', 'Chillán', 'papas', 700);
INSERT INTO lleva_a VALUES ('Rosa', 'San Carlos', 'frutillas', 2800);
INSERT INTO lleva_a VALUES ('Luis', 'Chillán', 'frutillas', 2600);
INSERT INTO lleva_a VALUES ('Luis', 'San Carlos', 'papas', 750);
INSERT INTO lleva_a VALUES ('Rosa', 'Chillán', 'porotos verdes', 1900);
INSERT INTO lleva_b SELECT * FROM lleva_a;
INSERT INTO lleva_a VALUES ('Rosa', 'San Carlos', 'papas', 720);

-- @error e48_rosa_papas_dos_ferias
INSERT INTO lleva_b VALUES ('Rosa', 'San Carlos', 'papas', 720);

-- @consulta e48_papas_de_rosa
SELECT feria, precio_kg
FROM lleva_a
WHERE agricultor = 'Rosa' AND producto = 'papas'
ORDER BY feria;

-- Ejercicio 4.10 · biblioteca comunal de Ancud (de las tablas al diagrama)

-- @crear e410_biblioteca
CREATE TABLE socio (
    rut_socio VARCHAR(12) NOT NULL,
    nombre    VARCHAR(60) NOT NULL,
    PRIMARY KEY (rut_socio)
);
CREATE TABLE carnet (
    num_carnet INTEGER     NOT NULL,
    vence      DATE        NOT NULL,
    rut_socio  VARCHAR(12) NOT NULL UNIQUE,
    PRIMARY KEY (num_carnet),
    FOREIGN KEY (rut_socio) REFERENCES socio(rut_socio)
);
CREATE TABLE autor (
    id_autor INTEGER     NOT NULL,
    nombre   VARCHAR(60) NOT NULL,
    PRIMARY KEY (id_autor)
);
CREATE TABLE libro (
    isbn   VARCHAR(17) NOT NULL,
    titulo VARCHAR(80) NOT NULL,
    PRIMARY KEY (isbn)
);
CREATE TABLE escribe (
    isbn     VARCHAR(17) NOT NULL,
    id_autor INTEGER     NOT NULL,
    PRIMARY KEY (isbn, id_autor),
    FOREIGN KEY (isbn) REFERENCES libro(isbn),
    FOREIGN KEY (id_autor) REFERENCES autor(id_autor)
);
CREATE TABLE ejemplar (
    isbn      VARCHAR(17) NOT NULL,
    num_copia INTEGER     NOT NULL,
    estado    VARCHAR(10) NOT NULL,
    PRIMARY KEY (isbn, num_copia),
    FOREIGN KEY (isbn) REFERENCES libro(isbn)
);
CREATE TABLE prestamo (
    id_prestamo INTEGER     NOT NULL,
    fecha       DATE        NOT NULL,
    devuelto    DATE,
    isbn        VARCHAR(17) NOT NULL,
    num_copia   INTEGER     NOT NULL,
    rut_socio   VARCHAR(12) NOT NULL,
    PRIMARY KEY (id_prestamo),
    FOREIGN KEY (isbn, num_copia) REFERENCES ejemplar(isbn, num_copia),
    FOREIGN KEY (rut_socio) REFERENCES socio(rut_socio)
);
