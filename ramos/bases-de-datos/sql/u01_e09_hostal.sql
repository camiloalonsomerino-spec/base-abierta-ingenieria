-- Unidad 1 · Ejercicio 1.9: las camas del hostal de Pucón, descontadas por el SGBD

CREATE TABLE cupo (
    fecha   DATE PRIMARY KEY,
    libres  INTEGER NOT NULL CHECK (libres >= 0)
);

INSERT INTO cupo VALUES ('2027-01-15', 6);

UPDATE cupo SET libres = libres - 2 WHERE fecha = '2027-01-15';
UPDATE cupo SET libres = libres - 3 WHERE fecha = '2027-01-15';

SELECT fecha, libres FROM cupo;

-- debe fallar
UPDATE cupo SET libres = libres - 3 WHERE fecha = '2027-01-15';

SELECT fecha, libres FROM cupo;
