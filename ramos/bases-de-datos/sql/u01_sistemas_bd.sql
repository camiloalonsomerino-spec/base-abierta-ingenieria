-- Unidad 1 · Ejemplo resuelto: las cuotas del Club Deportivo Río Laja (Los Ángeles)
-- La planilla de cuotas pasada a tres tablas. Corre en SQLite y en MySQL 8.0.16 o más.
-- En SQLite, antes de correrlo: PRAGMA foreign_keys = ON;

CREATE TABLE categoria (
    nombre  VARCHAR(10) PRIMARY KEY,
    cuota   INTEGER NOT NULL CHECK (cuota > 0)
);

CREATE TABLE socio (
    id_socio   INTEGER PRIMARY KEY,
    nombre     VARCHAR(60) NOT NULL,
    telefono   VARCHAR(15),
    categoria  VARCHAR(10) NOT NULL REFERENCES categoria(nombre)
);

CREATE TABLE pago (
    id_socio  INTEGER NOT NULL REFERENCES socio(id_socio),
    fecha     DATE NOT NULL,
    monto     INTEGER NOT NULL CHECK (monto > 0),
    PRIMARY KEY (id_socio, fecha)
);

INSERT INTO categoria VALUES ('sub-13', 14500), ('sub-15', 16500), ('adulto', 21000);

INSERT INTO socio VALUES
    (1, 'Antonia Rivas',  '9 0000 0033', 'sub-13'),
    (2, 'Benjamín Soto',  '9 0000 0028', 'sub-15'),
    (3, 'Catalina Mora',  '9 0000 0038', 'adulto'),
    (4, 'Diego Paredes',  '9 0000 0015', 'sub-15'),
    (5, 'Emilia Cáceres', '9 0000 0008', 'sub-13');

INSERT INTO pago VALUES
    (1, '2026-03-02', 14500), (2, '2026-03-03', 16500), (3, '2026-03-05', 21000),
    (4, '2026-03-09', 16500), (5, '2026-03-10', 14500), (1, '2026-04-01', 14500),
    (2, '2026-04-04', 16500), (3, '2026-04-06', 21000), (4, '2026-04-08', 16000),
    (5, '2026-04-12', 14500);

-- ¿Alguien pagó menos que la cuota de su categoría?
SELECT s.nombre, p.fecha, p.monto, c.cuota
FROM pago p
JOIN socio s     ON s.id_socio = p.id_socio
JOIN categoria c ON c.nombre = s.categoria
WHERE p.monto < c.cuota;

-- Benjamín cambia de teléfono: se corrige en un solo lugar
UPDATE socio SET telefono = '9 0000 0029' WHERE id_socio = 2;

SELECT id_socio, nombre, telefono FROM socio WHERE id_socio = 2;

-- Lo que el SGBD rechaza
-- debe fallar
INSERT INTO pago VALUES (9, '2026-04-15', 14500);
-- debe fallar
INSERT INTO pago VALUES (3, '2026-04-20', -21000);
-- debe fallar
INSERT INTO socio VALUES (6, 'Martina Lagos', '9 0000 0003', 'sub-17');
-- debe fallar
INSERT INTO pago VALUES (1, '2026-04-01', 14500);

-- Nada de lo rechazado entró
SELECT COUNT(*) AS pagos, SUM(monto) AS recaudado FROM pago;
