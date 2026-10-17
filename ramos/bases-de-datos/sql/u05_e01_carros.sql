-- Ejercicio 5.1 · carros de comida de la costanera de Antofagasta (datos inventados)
CREATE TABLE carro (
    patente   VARCHAR(8),
    duenio    VARCHAR(60),
    comida    VARCHAR(30),
    metros    INTEGER
);
INSERT INTO carro VALUES ('EJAG-21', 'Juana Sepúlveda', 'empanadas', 6);
INSERT INTO carro VALUES ('EJAH-73', 'Luis Fuentealba', 'jugos', 4);
INSERT INTO carro VALUES ('EJAD-08', 'Juana Sepúlveda', 'sopaipillas', 3);
INSERT INTO carro VALUES ('EJAJ-45', 'Héctor Vergara', 'ceviche', 5);
INSERT INTO carro VALUES ('EJAL-19', 'Ana Cifuentes', 'completos', 6);
INSERT INTO carro VALUES ('EJAH-73', 'Luis Fuentealba', 'jugos', 4);
INSERT INTO carro VALUES ('EJAO-62', 'Ana Cifuentes', 'café', 3);

-- @grado
SELECT COUNT(*) FROM pragma_table_info('carro');
-- @filas
SELECT COUNT(*) FROM carro;
-- @distintas
SELECT COUNT(*) FROM (SELECT DISTINCT * FROM carro);
-- @repetidas
SELECT patente, duenio, comida, metros, COUNT(*) AS veces
FROM carro
GROUP BY patente, duenio, comida, metros
HAVING COUNT(*) > 1;
