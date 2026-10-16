-- Ejercicio 5.7 · clínica veterinaria de Osorno (datos inventados): el RUT quedó mal digitado
PRAGMA foreign_keys = ON;

-- Diseño 1: el RUT es la clave primaria, sin acción al actualizar
CREATE TABLE cliente_1 (
    rut       VARCHAR(12) NOT NULL PRIMARY KEY,
    nombre    VARCHAR(60) NOT NULL
);
CREATE TABLE mascota_1 (
    id_mascota INTEGER PRIMARY KEY,
    nombre     VARCHAR(30) NOT NULL,
    rut_dueno  VARCHAR(12) NOT NULL,
    FOREIGN KEY (rut_dueno) REFERENCES cliente_1 (rut)
);
CREATE TABLE boleta_1 (
    id_boleta   INTEGER PRIMARY KEY,
    rut_cliente VARCHAR(12) NOT NULL,
    monto       INTEGER NOT NULL,
    FOREIGN KEY (rut_cliente) REFERENCES cliente_1 (rut)
);

-- Diseño 2: el RUT es la clave primaria, con ON UPDATE CASCADE
CREATE TABLE cliente_2 (
    rut       VARCHAR(12) NOT NULL PRIMARY KEY,
    nombre    VARCHAR(60) NOT NULL
);
CREATE TABLE mascota_2 (
    id_mascota INTEGER PRIMARY KEY,
    nombre     VARCHAR(30) NOT NULL,
    rut_dueno  VARCHAR(12) NOT NULL,
    FOREIGN KEY (rut_dueno) REFERENCES cliente_2 (rut) ON UPDATE CASCADE
);
CREATE TABLE boleta_2 (
    id_boleta   INTEGER PRIMARY KEY,
    rut_cliente VARCHAR(12) NOT NULL,
    monto       INTEGER NOT NULL,
    FOREIGN KEY (rut_cliente) REFERENCES cliente_2 (rut) ON UPDATE CASCADE
);

-- Diseño 3: clave subrogada y el RUT como clave alternativa
CREATE TABLE cliente_3 (
    id_cliente INTEGER PRIMARY KEY,
    rut        VARCHAR(12) NOT NULL UNIQUE,
    nombre     VARCHAR(60) NOT NULL
);
CREATE TABLE mascota_3 (
    id_mascota INTEGER PRIMARY KEY,
    nombre     VARCHAR(30) NOT NULL,
    id_dueno   INTEGER NOT NULL,
    FOREIGN KEY (id_dueno) REFERENCES cliente_3 (id_cliente)
);
CREATE TABLE boleta_3 (
    id_boleta  INTEGER PRIMARY KEY,
    id_cliente INTEGER NOT NULL,
    monto      INTEGER NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES cliente_3 (id_cliente)
);

INSERT INTO cliente_1 VALUES ('12.354.678-4', 'Soledad Ulloa');
INSERT INTO cliente_2 VALUES ('12.354.678-4', 'Soledad Ulloa');
INSERT INTO cliente_3 VALUES (1, '12.354.678-4', 'Soledad Ulloa');
INSERT INTO mascota_1 VALUES (1, 'Canela', '12.354.678-4');
INSERT INTO mascota_1 VALUES (2, 'Pelusa', '12.354.678-4');
INSERT INTO mascota_1 VALUES (3, 'Toby', '12.354.678-4');
INSERT INTO mascota_2 SELECT * FROM mascota_1;
INSERT INTO mascota_3 SELECT id_mascota, nombre, 1 FROM mascota_1;
INSERT INTO boleta_1 VALUES (1, '12.354.678-4', 18500);
INSERT INTO boleta_1 VALUES (2, '12.354.678-4', 32900);
INSERT INTO boleta_1 VALUES (3, '12.354.678-4', 7400);
INSERT INTO boleta_1 VALUES (4, '12.354.678-4', 45200);
INSERT INTO boleta_1 VALUES (5, '12.354.678-4', 12800);
INSERT INTO boleta_2 SELECT * FROM boleta_1;
INSERT INTO boleta_3 SELECT id_boleta, 1, monto FROM boleta_1;

-- @d1 corregir el RUT en el diseño 1
UPDATE cliente_1 SET rut = '12.345.678-5' WHERE rut = '12.354.678-4';
-- @d2 corregirlo en el diseño 2
UPDATE cliente_2 SET rut = '12.345.678-5' WHERE rut = '12.354.678-4';
-- @d2c cuántas filas cambiaron en el diseño 2
SELECT (SELECT COUNT(*) FROM cliente_2 WHERE rut = '12.345.678-5') AS clientes,
       (SELECT COUNT(*) FROM mascota_2 WHERE rut_dueno = '12.345.678-5') AS mascotas,
       (SELECT COUNT(*) FROM boleta_2 WHERE rut_cliente = '12.345.678-5') AS boletas;
-- @d3 corregirlo en el diseño 3
UPDATE cliente_3 SET rut = '12.345.678-5' WHERE rut = '12.354.678-4';
