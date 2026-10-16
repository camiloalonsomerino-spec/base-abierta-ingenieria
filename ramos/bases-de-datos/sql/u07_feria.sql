-- Unidad 7 · Álgebra relacional · base de los ejercicios 7.5 a 7.10
-- Feria de productores de Ñuble (datos inventados). Un productor tiene la comuna sin registrar (NULL).
-- Correr en una base nueva:  sqlite3 feria.db < u07_feria.sql

CREATE TABLE productor (
    id_productor INTEGER PRIMARY KEY,
    nombre       VARCHAR(40) NOT NULL,
    comuna       VARCHAR(30)
);
CREATE TABLE producto (
    id_producto  INTEGER PRIMARY KEY,
    descripcion  VARCHAR(30) NOT NULL UNIQUE,
    tipo         VARCHAR(12) NOT NULL
);
CREATE TABLE ofrece (
    id_productor INTEGER NOT NULL,
    id_producto  INTEGER NOT NULL,
    precio       INTEGER NOT NULL,
    PRIMARY KEY (id_productor, id_producto),
    FOREIGN KEY (id_productor) REFERENCES productor(id_productor),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

INSERT INTO productor VALUES
    (1, 'Huerta Los Robles', 'San Carlos'), (2, 'Agrícola Ñiquén', 'Ñiquén'),
    (3, 'Don Tito', 'Coihueco'), (4, 'Las Camelias', 'San Carlos'), (5, 'Campo Lindo', NULL);
INSERT INTO producto VALUES
    (1, 'tomate', 'hortaliza'), (2, 'papa', 'hortaliza'), (3, 'lechuga', 'hortaliza'),
    (4, 'frutilla', 'fruta'), (5, 'manzana', 'fruta'), (6, 'zapallo', 'hortaliza');
INSERT INTO ofrece VALUES
    (1, 1, 1290), (1, 2, 790), (1, 3, 650), (1, 6, 890),
    (2, 2, 750), (2, 4, 2990), (2, 5, 1150),
    (3, 1, 1190), (3, 3, 700), (3, 4, 3190),
    (4, 1, 1350), (4, 2, 820), (4, 3, 600), (4, 6, 950), (4, 5, 1090),
    (5, 4, 2790), (5, 5, 990);

-- @e5a
SELECT p.nombre FROM productor p
WHERE p.id_productor IN (
    SELECT o.id_productor FROM ofrece o JOIN producto pr ON pr.id_producto = o.id_producto
    WHERE pr.descripcion = 'tomate'
    INTERSECT
    SELECT o.id_productor FROM ofrece o JOIN producto pr ON pr.id_producto = o.id_producto
    WHERE pr.descripcion = 'papa');

-- @e5b
SELECT p.nombre FROM productor p
WHERE p.id_productor IN (
    SELECT o.id_productor FROM ofrece o JOIN producto pr ON pr.id_producto = o.id_producto
    WHERE pr.descripcion = 'tomate'
    EXCEPT
    SELECT o.id_productor FROM ofrece o JOIN producto pr ON pr.id_producto = o.id_producto
    WHERE pr.descripcion = 'papa');

-- @e6
SELECT a.nombre AS mas_barato, b.nombre AS mas_caro, oa.precio AS precio_a, ob.precio AS precio_b
FROM ofrece oa
JOIN ofrece ob    ON ob.id_producto = oa.id_producto AND oa.precio < ob.precio
JOIN producto pr  ON pr.id_producto = oa.id_producto
JOIN productor a  ON a.id_productor = oa.id_productor
JOIN productor b  ON b.id_productor = ob.id_productor
WHERE pr.descripcion = 'tomate';

-- @e7a
SELECT p.nombre FROM productor p
WHERE NOT EXISTS (
    SELECT * FROM producto pr WHERE pr.tipo = 'hortaliza'
      AND NOT EXISTS (SELECT * FROM ofrece o
                      WHERE o.id_productor = p.id_productor AND o.id_producto = pr.id_producto));

-- @e7b
SELECT p.nombre FROM productor p
WHERE NOT EXISTS (
    SELECT * FROM producto pr WHERE pr.tipo = 'fruta'
      AND NOT EXISTS (SELECT * FROM ofrece o
                      WHERE o.id_productor = p.id_productor AND o.id_producto = pr.id_producto));

-- @e8a
SELECT COUNT(*) FROM productor, ofrece;

-- @e8b
SELECT COUNT(*) FROM productor p, ofrece o WHERE p.id_productor = o.id_productor;

-- @e8c
SELECT COUNT(*) FROM productor, ofrece WHERE precio > 1000;

-- @e8d
SELECT COUNT(*) FROM productor p JOIN ofrece o ON o.id_productor = p.id_productor WHERE o.precio > 1000;

-- @e9a
SELECT p.nombre FROM productor p
WHERE NOT EXISTS (
    SELECT * FROM producto pr WHERE pr.tipo = 'legumbre'
      AND NOT EXISTS (SELECT * FROM ofrece o
                      WHERE o.id_productor = p.id_productor AND o.id_producto = pr.id_producto));

-- @e9b
SELECT p.nombre
FROM productor p
JOIN ofrece o    ON o.id_productor = p.id_productor
JOIN producto pr ON pr.id_producto = o.id_producto
WHERE pr.tipo = 'hortaliza'
GROUP BY p.id_productor, p.nombre
HAVING COUNT(*) = (SELECT COUNT(*) FROM producto WHERE tipo = 'hortaliza');

-- @e9c
SELECT p.nombre
FROM productor p
JOIN ofrece o    ON o.id_productor = p.id_productor
JOIN producto pr ON pr.id_producto = o.id_producto
WHERE pr.tipo = 'legumbre'
GROUP BY p.id_productor, p.nombre
HAVING COUNT(*) = (SELECT COUNT(*) FROM producto WHERE tipo = 'legumbre');

-- @e10a
SELECT nombre FROM productor WHERE comuna <> 'San Carlos';

-- @e10b
SELECT nombre FROM productor
EXCEPT
SELECT nombre FROM productor WHERE comuna = 'San Carlos';

-- @e10c
SELECT COUNT(*) FROM productor WHERE comuna = NULL;

-- @e10d
SELECT COUNT(*) FROM productor WHERE comuna IS NULL;
