-- Unidad 5 · Ejemplo resuelto · biblioteca vecinal de Valdivia (datos inventados)
-- Corre en SQLite (sqlite3 de Python) y en MySQL 8 (ver las notas de la unidad).
-- Las líneas «-- @nombre» marcan los intentos que el verificador muestra con su respuesta.
PRAGMA foreign_keys = ON;

CREATE TABLE socio (
    id_socio   INTEGER PRIMARY KEY,
    rut        VARCHAR(12) NOT NULL UNIQUE,
    nombre     VARCHAR(60) NOT NULL,
    comuna     VARCHAR(40) NOT NULL DEFAULT 'Valdivia'
);
CREATE TABLE telefono_socio (
    id_socio   INTEGER NOT NULL,
    telefono   VARCHAR(16) NOT NULL,
    PRIMARY KEY (id_socio, telefono),
    FOREIGN KEY (id_socio) REFERENCES socio (id_socio) ON DELETE CASCADE
);
CREATE TABLE libro (
    isbn       VARCHAR(17) NOT NULL PRIMARY KEY,
    titulo     VARCHAR(80) NOT NULL,
    anio       INTEGER NOT NULL CONSTRAINT ck_anio CHECK (anio BETWEEN 1450 AND 2026)
);
CREATE TABLE ejemplar (
    id_ejemplar INTEGER PRIMARY KEY,
    isbn        VARCHAR(17) NOT NULL,
    estado      VARCHAR(12) NOT NULL DEFAULT 'disponible'
                CONSTRAINT ck_estado CHECK (estado IN ('disponible', 'prestado', 'baja')),
    FOREIGN KEY (isbn) REFERENCES libro (isbn) ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE TABLE prestamo (
    id_prestamo INTEGER PRIMARY KEY,
    id_ejemplar INTEGER NOT NULL,
    id_socio    INTEGER,
    salida      DATE NOT NULL,
    devolucion  DATE,
    CONSTRAINT ck_fechas CHECK (devolucion >= salida),
    FOREIGN KEY (id_ejemplar) REFERENCES ejemplar (id_ejemplar) ON DELETE RESTRICT,
    FOREIGN KEY (id_socio) REFERENCES socio (id_socio) ON DELETE SET NULL
);

INSERT INTO socio VALUES (1, '15.432.876-9', 'Rosa Paillalef', 'Valdivia');
INSERT INTO socio VALUES (2, '17.209.334-5', 'Tomás Riquelme', 'Valdivia');
INSERT INTO socio VALUES (3, '12.884.051-6', 'Marta Huenchullán', 'Corral');
INSERT INTO socio VALUES (4, '20.115.672-6', 'Diego Altamirano', 'Valdivia');

INSERT INTO telefono_socio VALUES (1, '+56 9 6123 4471');
INSERT INTO telefono_socio VALUES (1, '+56 63 221 3390');
INSERT INTO telefono_socio VALUES (2, '+56 9 7745 0812');
INSERT INTO telefono_socio VALUES (3, '+56 9 5390 2268');
INSERT INTO telefono_socio VALUES (3, '+56 9 8812 0047');
INSERT INTO telefono_socio VALUES (4, '+56 9 9031 5524');

INSERT INTO libro VALUES ('978-956-7401-12-3', 'Crónicas del Calle-Calle', 2019);
INSERT INTO libro VALUES ('978-956-8820-05-7', 'Huertos de invierno', 2022);
INSERT INTO libro VALUES ('978-956-3315-04-9', 'Mareas de niebla', 2011);

INSERT INTO ejemplar VALUES (1, '978-956-7401-12-3', 'prestado');
INSERT INTO ejemplar VALUES (2, '978-956-7401-12-3', 'disponible');
INSERT INTO ejemplar VALUES (3, '978-956-8820-05-7', 'prestado');
INSERT INTO ejemplar VALUES (4, '978-956-3315-04-9', 'disponible');
INSERT INTO ejemplar VALUES (5, '978-956-3315-04-9', 'baja');

INSERT INTO prestamo VALUES (1, 1, 2, '2026-08-03', '2026-08-17');
INSERT INTO prestamo VALUES (2, 3, 3, '2026-08-20', '2026-09-02');
INSERT INTO prestamo VALUES (3, 2, 3, '2026-09-05', '2026-09-19');
INSERT INTO prestamo VALUES (4, 4, 1, '2026-09-11', '2026-09-24');
INSERT INTO prestamo VALUES (5, 1, 1, '2026-10-01', NULL);
INSERT INTO prestamo VALUES (6, 3, 4, '2026-10-06', NULL);

-- @i1 un ejemplar de un libro que no está en el catálogo
INSERT INTO ejemplar (isbn) VALUES ('978-956-9999-99-9');
-- @i2 un socio con un RUT que ya existe
INSERT INTO socio (rut, nombre) VALUES ('15.432.876-9', 'Rosa P. Paillalef');
-- @i3 un socio sin nombre
INSERT INTO socio (rut, comuna) VALUES ('19.640.208-K', 'Paillaco');
-- @i4 un año mal digitado (2062 por 2026)
INSERT INTO libro VALUES ('978-956-6102-77-1', 'Atlas del sur lluvioso', 2062);
-- @i5 una devolución anterior a la salida
INSERT INTO prestamo (id_ejemplar, id_socio, salida, devolucion) VALUES (2, 4, '2026-10-09', '2026-09-23');
-- @i6 un estado que no está en la lista
INSERT INTO ejemplar (isbn, estado) VALUES ('978-956-8820-05-7', 'perdido');
-- @i7 borrar un libro que tiene ejemplares
DELETE FROM libro WHERE isbn = '978-956-7401-12-3';
-- @i8 corregir un ISBN mal digitado
UPDATE libro SET isbn = '978-956-3315-40-9' WHERE isbn = '978-956-3315-04-9';
-- @c8 los ejemplares siguen a su libro
SELECT id_ejemplar, isbn, estado FROM ejemplar WHERE isbn LIKE '978-956-3315%';
-- @i9 Marta pide que borren sus datos
DELETE FROM socio WHERE id_socio = 3;
-- @c9a sus teléfonos se fueron con ella
SELECT COUNT(*) FROM telefono_socio WHERE id_socio = 3;
-- @c9b sus préstamos quedan, sin socio
SELECT id_prestamo, id_ejemplar, id_socio, salida FROM prestamo WHERE id_prestamo IN (2, 3);
-- @i10a se apagan las claves foráneas
PRAGMA foreign_keys = OFF;
-- @i10b un préstamo de un ejemplar que no existe
INSERT INTO prestamo (id_ejemplar, id_socio, salida) VALUES (8, 2, '2026-10-12');
-- @i10c la revisión encuentra al huérfano
PRAGMA foreign_key_check;
-- @i10d se borra el huérfano y se vuelven a encender
DELETE FROM prestamo WHERE id_ejemplar = 8;
PRAGMA foreign_keys = ON;
