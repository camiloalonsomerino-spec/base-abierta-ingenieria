-- Ejercicio 6.10 · boletas de un minimarket de Valparaíso (datos inventados)
-- El 01-10-2026 subieron el café y los huevos; producto guarda el precio de HOY.
PRAGMA foreign_keys = ON;
CREATE TABLE producto (
    id_producto   INTEGER PRIMARY KEY,
    nombre        VARCHAR(40) NOT NULL UNIQUE,
    precio_actual INTEGER NOT NULL CHECK (precio_actual > 0)
);
CREATE TABLE boleta (
    id_boleta     INTEGER PRIMARY KEY,
    fecha         DATE NOT NULL,
    total         INTEGER NOT NULL
);
CREATE TABLE linea (
    id_boleta     INTEGER NOT NULL,
    id_producto   INTEGER NOT NULL,
    cantidad      INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unit   INTEGER NOT NULL,
    PRIMARY KEY (id_boleta, id_producto),
    FOREIGN KEY (id_boleta) REFERENCES boleta (id_boleta),
    FOREIGN KEY (id_producto) REFERENCES producto (id_producto)
);
INSERT INTO producto VALUES (1, 'pan amasado (kg)', 2390);
INSERT INTO producto VALUES (2, 'leche entera 1 L', 1150);
INSERT INTO producto VALUES (3, 'café molido 250 g', 4990);
INSERT INTO producto VALUES (4, 'huevos (docena)', 3590);
INSERT INTO producto VALUES (5, 'aceite 1 L', 2790);
INSERT INTO boleta VALUES (1, '2026-09-04', 12920);
INSERT INTO boleta VALUES (2, '2026-09-12', 9370);
INSERT INTO boleta VALUES (3, '2026-09-25', 15060);
INSERT INTO boleta VALUES (4, '2026-10-03', 7290);
INSERT INTO boleta VALUES (5, '2026-10-09', 10760);
INSERT INTO boleta VALUES (6, '2026-10-15', 10570);
INSERT INTO linea VALUES (1, 1, 2, 2390);
INSERT INTO linea VALUES (1, 2, 3, 1150);
INSERT INTO linea VALUES (1, 3, 1, 4690);
INSERT INTO linea VALUES (2, 4, 2, 3290);
INSERT INTO linea VALUES (2, 5, 1, 2790);
INSERT INTO linea VALUES (3, 3, 2, 4690);
INSERT INTO linea VALUES (3, 1, 1, 2390);
INSERT INTO linea VALUES (3, 4, 1, 3290);
INSERT INTO linea VALUES (4, 3, 1, 4990);
INSERT INTO linea VALUES (4, 2, 2, 1150);
INSERT INTO linea VALUES (5, 4, 1, 3590);
INSERT INTO linea VALUES (5, 1, 3, 2390);
INSERT INTO linea VALUES (6, 5, 2, 2790);
INSERT INTO linea VALUES (6, 3, 1, 4990);

-- @sep_cobrado ventas de septiembre con el precio que se cobró
SELECT SUM(l.cantidad * l.precio_unit) AS ventas
FROM linea l JOIN boleta b ON b.id_boleta = l.id_boleta
WHERE b.fecha < '2026-10-01';
-- @sep_hoy las mismas ventas si precio_unit se borra y se usa el precio de hoy
SELECT SUM(l.cantidad * p.precio_actual) AS ventas
FROM linea l JOIN boleta b ON b.id_boleta = l.id_boleta
JOIN producto p ON p.id_producto = l.id_producto
WHERE b.fecha < '2026-10-01';
-- @total_ok boletas cuyo total no calza con la suma de sus líneas
SELECT b.id_boleta, b.total, SUM(l.cantidad * l.precio_unit) AS suma_lineas
FROM boleta b JOIN linea l ON l.id_boleta = b.id_boleta
GROUP BY b.id_boleta, b.total
HAVING b.total <> SUM(l.cantidad * l.precio_unit);
-- @corrige la boleta 5 llevaba 2 kg de pan, no 3: se corrige la línea
UPDATE linea SET cantidad = 2 WHERE id_boleta = 5 AND id_producto = 1;
-- @total_mal
SELECT b.id_boleta, b.total, SUM(l.cantidad * l.precio_unit) AS suma_lineas
FROM boleta b JOIN linea l ON l.id_boleta = b.id_boleta
GROUP BY b.id_boleta, b.total
HAVING b.total <> SUM(l.cantidad * l.precio_unit);
