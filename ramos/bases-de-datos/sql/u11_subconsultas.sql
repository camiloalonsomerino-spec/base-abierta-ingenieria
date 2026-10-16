-- Unidad 11 · Subconsultas y vistas · base del ejemplo
-- Préstamos de una biblioteca comunal de Tomé (socios y préstamos inventados).
-- Correr en SQLite:   sqlite3 biblioteca.db < u11_subconsultas.sql
-- Cada marca «-- @tipo nombre» separa un bloque: el verificador (verificacion/u11_subconsultas.py)
-- lo ejecuta en orden y exige que el SQL y su resultado estén en la unidad.

-- @crear tablas
CREATE TABLE socio (
    id_socio     INTEGER PRIMARY KEY,
    nombre       VARCHAR(40) NOT NULL,
    comuna       VARCHAR(30) NOT NULL,
    invitado_por INTEGER REFERENCES socio(id_socio)   -- NULL: nadie lo invitó
);
CREATE TABLE libro (
    id_libro INTEGER PRIMARY KEY,
    titulo   VARCHAR(60) NOT NULL,
    autor    VARCHAR(40) NOT NULL,
    genero   VARCHAR(20) NOT NULL,
    anio     INTEGER NOT NULL
);
CREATE TABLE prestamo (
    id_prestamo INTEGER PRIMARY KEY,
    id_socio    INTEGER NOT NULL REFERENCES socio(id_socio),
    id_libro    INTEGER NOT NULL REFERENCES libro(id_libro),
    fecha       DATE NOT NULL,
    dias        INTEGER                                -- NULL: todavía no lo devuelve
);

-- @datos carga
INSERT INTO socio VALUES
    (1, 'Ana Soto', 'Tomé', NULL), (2, 'Benjamín Rojas', 'Tomé', 1), (3, 'Carla Muñoz', 'Penco', 1),
    (4, 'Diego Fuentes', 'Tomé', NULL), (5, 'Elisa Vera', 'Penco', 3), (6, 'Felipe Araya', 'Coelemu', NULL),
    (7, 'Gabriela Paz', 'Tomé', 4), (8, 'Hugo Leiva', 'Coelemu', 6);
INSERT INTO libro VALUES
    (1, 'Hijo de ladrón', 'Manuel Rojas', 'novela', 1951),
    (2, 'Veinte poemas de amor y una canción desesperada', 'Pablo Neruda', 'poesía', 1924),
    (3, 'Altazor', 'Vicente Huidobro', 'poesía', 1931),
    (4, 'La casa de los espíritus', 'Isabel Allende', 'novela', 1982),
    (5, 'Martín Rivas', 'Alberto Blest Gana', 'novela', 1862),
    (6, 'Desolación', 'Gabriela Mistral', 'poesía', 1922),
    (7, 'Papelucho', 'Marcela Paz', 'infantil', 1947),
    (8, 'Mala onda', 'Alberto Fuguet', 'novela', 1991),
    (9, 'Poemas y antipoemas', 'Nicanor Parra', 'poesía', 1954);
INSERT INTO prestamo VALUES
    (1, 1, 1, '2026-09-01', 12), (2, 1, 2, '2026-09-03', 5), (3, 2, 4, '2026-09-04', 20),
    (4, 3, 2, '2026-09-05', 7), (5, 3, 5, '2026-09-08', 15), (6, 1, 6, '2026-09-10', 9),
    (7, 5, 7, '2026-09-11', 4), (8, 2, 1, '2026-09-12', NULL), (9, 7, 4, '2026-09-15', 18),
    (10, 3, 9, '2026-09-16', 6), (11, 1, 8, '2026-09-18', NULL), (12, 7, 6, '2026-09-20', 10),
    (13, 5, 2, '2026-09-22', 8), (14, 8, 7, '2026-09-24', 3), (15, 3, 4, '2026-09-25', NULL);

-- @consulta d_socio
SELECT * FROM socio;

-- @consulta d_libro
SELECT * FROM libro;

-- @consulta d_prestamo
SELECT * FROM prestamo;

-- ============================================================ 2. Subconsulta escalar
-- @consulta s2_promedio
SELECT AVG(dias) AS promedio FROM prestamo;

-- @consulta s2_sobre
SELECT id_prestamo, id_socio, dias
FROM prestamo
WHERE dias > (SELECT AVG(dias) FROM prestamo)
ORDER BY dias DESC;

-- @falla s2_error
SELECT id_prestamo, dias
FROM prestamo
WHERE dias > AVG(dias);

-- @consulta s2_varias
SELECT titulo
FROM libro
WHERE anio = (SELECT anio FROM libro WHERE genero = 'poesía');

-- ============================================================ 3. Subconsulta de lista
-- @consulta s3_in
SELECT nombre
FROM socio
WHERE id_socio IN (SELECT id_socio
                   FROM prestamo
                   WHERE id_libro IN (SELECT id_libro FROM libro WHERE genero = 'poesía'))
ORDER BY nombre;

-- @consulta s3_not_in
SELECT nombre
FROM socio
WHERE id_socio NOT IN (SELECT id_socio FROM prestamo)
ORDER BY nombre;

-- @consulta s3_invitadores
SELECT invitado_por FROM socio;

-- @consulta s3_trampa
SELECT nombre
FROM socio
WHERE id_socio NOT IN (SELECT invitado_por FROM socio);

-- @consulta s3_arreglo
SELECT nombre
FROM socio
WHERE id_socio NOT IN (SELECT invitado_por FROM socio WHERE invitado_por IS NOT NULL)
ORDER BY nombre;

-- ============================================================ 4. Subconsulta correlacionada
-- @consulta s4_reciente
SELECT genero, titulo, anio
FROM libro l
WHERE anio = (SELECT MAX(l2.anio) FROM libro l2 WHERE l2.genero = l.genero)
ORDER BY genero;

-- @consulta s4_conteo
SELECT s.nombre,
       (SELECT COUNT(*) FROM prestamo p WHERE p.id_socio = s.id_socio) AS prestamos
FROM socio s
ORDER BY s.id_socio;

-- ============================================================ 5. EXISTS y NOT EXISTS
-- @consulta s5_nunca
SELECT titulo
FROM libro l
WHERE NOT EXISTS (SELECT 1 FROM prestamo p WHERE p.id_libro = l.id_libro);

-- @consulta s5_no_invitan
SELECT nombre
FROM socio s
WHERE NOT EXISTS (SELECT 1 FROM socio i WHERE i.invitado_por = s.id_socio)
ORDER BY nombre;

-- ============================================================ 6. Subconsulta en el FROM
-- @consulta s6_promedio
SELECT AVG(y.n) AS promedio
FROM (SELECT COUNT(*) AS n FROM prestamo GROUP BY id_socio) AS y;

-- @consulta s6_derivada
SELECT x.id_socio, x.n
FROM (SELECT id_socio, COUNT(*) AS n FROM prestamo GROUP BY id_socio) AS x
WHERE x.n > (SELECT AVG(y.n)
             FROM (SELECT COUNT(*) AS n FROM prestamo GROUP BY id_socio) AS y)
ORDER BY x.id_socio;

-- ============================================================ 7. WITH (CTE)
-- @consulta s7_cte
WITH por_socio AS (
    SELECT id_socio, COUNT(*) AS n
    FROM prestamo
    GROUP BY id_socio
)
SELECT s.nombre, ps.n
FROM por_socio ps
JOIN socio s ON s.id_socio = ps.id_socio
WHERE ps.n > (SELECT AVG(n) FROM por_socio)
ORDER BY s.nombre;

-- ============================================================ 8. UNION, INTERSECT y EXCEPT
-- @consulta s8_intersect
SELECT id_socio FROM prestamo
WHERE id_libro IN (SELECT id_libro FROM libro WHERE genero = 'novela')
INTERSECT
SELECT id_socio FROM prestamo
WHERE id_libro IN (SELECT id_libro FROM libro WHERE genero = 'poesía')
ORDER BY id_socio;

-- @consulta s8_except
SELECT id_socio FROM prestamo
WHERE id_libro IN (SELECT id_libro FROM libro WHERE genero = 'novela')
EXCEPT
SELECT id_socio FROM prestamo
WHERE id_libro IN (SELECT id_libro FROM libro WHERE genero = 'poesía');

-- @consulta s8_union
SELECT id_socio FROM prestamo
WHERE id_libro IN (SELECT id_libro FROM libro WHERE genero = 'novela')
UNION
SELECT id_socio FROM prestamo
WHERE id_libro IN (SELECT id_libro FROM libro WHERE genero = 'poesía')
ORDER BY id_socio;

-- @consulta s8_union_all
SELECT COUNT(*) AS filas
FROM (SELECT id_socio FROM prestamo
      WHERE id_libro IN (SELECT id_libro FROM libro WHERE genero = 'novela')
      UNION ALL
      SELECT id_socio FROM prestamo
      WHERE id_libro IN (SELECT id_libro FROM libro WHERE genero = 'poesía'));

-- @falla s8_error
SELECT id_socio, nombre FROM socio
UNION
SELECT id_socio FROM prestamo;

-- ============================================================ 9. Vistas
-- @ejecuta s9_vista
CREATE VIEW v_prestamo AS
SELECT p.id_prestamo, s.nombre, s.comuna, l.titulo, l.genero, p.fecha, p.dias
FROM prestamo p
JOIN socio s ON s.id_socio = p.id_socio
JOIN libro l ON l.id_libro = p.id_libro;

-- @consulta s9_por_genero
SELECT genero, COUNT(*) AS prestamos, AVG(dias) AS dias_promedio
FROM v_prestamo
GROUP BY genero
ORDER BY prestamos DESC;

-- @ejecuta s9_begin
BEGIN;

-- @ejecuta s9_insert
INSERT INTO prestamo VALUES (16, 6, 3, '2026-09-29', NULL);

-- @consulta s9_viva
SELECT COUNT(*) AS filas FROM v_prestamo;

-- @ejecuta s9_rollback
ROLLBACK;

-- @consulta s9_despues
SELECT COUNT(*) AS filas FROM v_prestamo;

-- @ejecuta s9_poesia
CREATE VIEW v_poesia AS
SELECT id_libro, titulo, anio
FROM libro
WHERE genero = 'poesía';

-- @falla s9_update
UPDATE v_poesia SET titulo = 'Altazor o el viaje en paracaídas' WHERE id_libro = 3;

-- ============================================================ 10. Ejemplo resuelto
-- @ejecuta e_vista
CREATE VIEW v_prestamos_por_socio AS
SELECT s.id_socio, s.comuna, s.nombre, COUNT(p.id_prestamo) AS n
FROM socio s
LEFT JOIN prestamo p ON p.id_socio = s.id_socio
GROUP BY s.id_socio, s.comuna, s.nombre;

-- @consulta e_paso2
SELECT comuna, nombre, n
FROM v_prestamos_por_socio
ORDER BY comuna, n DESC;

-- @consulta e_lector
SELECT comuna, nombre, n
FROM v_prestamos_por_socio x
WHERE n = (SELECT MAX(y.n) FROM v_prestamos_por_socio y WHERE y.comuna = x.comuna)
ORDER BY comuna;

-- @consulta e_cte
WITH por_socio AS (
    SELECT s.id_socio, s.comuna, s.nombre, COUNT(p.id_prestamo) AS n
    FROM socio s
    LEFT JOIN prestamo p ON p.id_socio = s.id_socio
    GROUP BY s.id_socio, s.comuna, s.nombre
)
SELECT comuna, nombre, n
FROM por_socio x
WHERE n = (SELECT MAX(y.n) FROM por_socio y WHERE y.comuna = x.comuna)
ORDER BY comuna;

-- ============================================================ Pautas con la base del ejemplo
-- @consulta p3_prestados
SELECT titulo
FROM libro l
WHERE EXISTS (SELECT 1 FROM prestamo p WHERE p.id_libro = l.id_libro AND p.dias IS NULL)
ORDER BY titulo;

-- @consulta p3_igual_null
SELECT titulo
FROM libro l
WHERE EXISTS (SELECT 1 FROM prestamo p WHERE p.id_libro = l.id_libro AND p.dias = NULL);

-- @consulta p4_except
SELECT comuna FROM v_prestamo WHERE genero = 'infantil'
EXCEPT
SELECT comuna FROM v_prestamo WHERE genero = 'novela';

-- @consulta p4_intersect
SELECT comuna FROM v_prestamo WHERE genero = 'infantil'
INTERSECT
SELECT comuna FROM v_prestamo WHERE genero = 'novela';

-- @consulta p8_correlacionada
SELECT p.id_socio, p.id_prestamo, p.dias
FROM prestamo p
WHERE p.dias = (SELECT MAX(p2.dias) FROM prestamo p2 WHERE p2.id_socio = p.id_socio)
ORDER BY p.id_socio;

-- @consulta p8_sin_correlacion
SELECT p.id_socio, p.id_prestamo, p.dias
FROM prestamo p
WHERE p.dias = (SELECT MAX(p2.dias) FROM prestamo p2)
ORDER BY p.id_socio;

-- @ejecuta p9_resumen
CREATE VIEW v_resumen_genero AS
SELECT genero, COUNT(*) AS prestamos
FROM v_prestamo
GROUP BY genero;

-- @falla p9_insert
INSERT INTO v_poesia (id_libro, titulo, anio) VALUES (10, 'Versos del Itata', 2019);
