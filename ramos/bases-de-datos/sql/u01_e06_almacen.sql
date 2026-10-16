-- Unidad 1 · Ejercicio 1.6: el almacén de Quilpué. ¿Qué acepta y qué rechaza el SGBD?

CREATE TABLE producto (
    codigo  VARCHAR(13) PRIMARY KEY,
    nombre  VARCHAR(40) NOT NULL,
    precio  INTEGER NOT NULL CHECK (precio > 0),
    stock   INTEGER NOT NULL CHECK (stock >= 0)
);

INSERT INTO producto VALUES ('7809900000017', 'Pan de molde', 2290, 14);
-- debe fallar
INSERT INTO producto VALUES ('7809900000024', 'Leche entera 1 L', 1150, -3);
-- debe fallar
INSERT INTO producto VALUES ('7809900000017', 'Pan integral', 2490, 8);
-- debe fallar
INSERT INTO producto VALUES ('7809900000031', NULL, 890, 20);
INSERT INTO producto VALUES ('7809900000048', 'Té 100 bolsitas', 3790, 6);

SELECT codigo, nombre, stock FROM producto;
