-- Unidad 9 · SQL para consultar una tabla
-- Base abierta de ingeniería · Bases de Datos
--
-- Parte 1 crea y llena dos tablas propias de la unidad: las órdenes de trabajo de un taller
-- mecánico de Los Ángeles (teoría y ejemplo resuelto) y las horas de un CESFAM de Coronel
-- (ejercicios). Datos inventados. Corre igual en SQLite y en MySQL.
-- Parte 2 son las consultas de la unidad; cada una lleva una marca «-- @nombre» que usa el
-- verificador (verificacion/u09_sql_una_tabla.py). Las marcadas «!error» fallan a propósito.
--
--   sqlite3 u09.db < u09_sql_una_tabla.sql

-- ------------------------------------------------------------------ parte 1 · tablas
CREATE TABLE orden_trabajo (
    id_ot     INTEGER PRIMARY KEY,
    patente   VARCHAR(6)  NOT NULL,
    marca     VARCHAR(20) NOT NULL,
    servicio  VARCHAR(20) NOT NULL,
    ingreso   DATE        NOT NULL,
    entrega   DATE,                      -- NULL: el auto sigue en el taller
    km        INTEGER     NOT NULL,
    monto     INTEGER,                   -- neto, sin IVA; NULL: falta el presupuesto
    detalle   VARCHAR(60) NOT NULL
);

INSERT INTO orden_trabajo VALUES
 (1,  'EJAE42', 'Toyota',    'mantención',  '2026-09-01', '2026-09-01',  85200,  64900, 'aceite y filtros'),
 (2,  'EJAB17', 'Chevrolet', 'frenos',      '2026-09-02', '2026-09-03', 132400, 118500, 'pastillas y discos delanteros'),
 (3,  'AE5821', 'Nissan',    'embrague',    '2026-09-02', '2026-09-05', 210700, 389000, 'kit de embrague'),
 (4,  'EJAI63', 'Hyundai',   'mantención',  '2026-09-04', '2026-09-04',  40100,  72400, 'aceite, filtros y revisión'),
 (5,  'EJAK28', 'Kia',       'diagnóstico', '2026-09-07', NULL,          98300,   NULL, 'ruido en la suspensión'),
 (6,  'EJAC90', 'Toyota',    'frenos',      '2026-09-08', '2026-09-09', 156900,  86300, 'pastillas traseras'),
 (7,  'AE4417', 'Suzuki',    'alineación',  '2026-09-09', '2026-09-09', 187500,  28000, 'alineación y balanceo'),
 (8,  'EJAM55', 'Mazda',     'mantención',  '2026-09-10', '2026-09-11',  61800,  79900, 'aceite, filtros y bujías'),
 (9,  'EJAA31', 'Chevrolet', 'embrague',    '2026-09-14', NULL,         176200, 412000, 'embrague patina'),
 (10, 'EJAF74', 'Hyundai',   'frenos',      '2026-09-15', NULL,         119600,  97800, 'líquido y pastillas delanteras'),
 (11, 'AE7302', 'Nissan',    'diagnóstico', '2026-09-16', NULL,         243100,   NULL, 'luz de motor encendida'),
 (12, 'EJAN16', 'Kia',       'alineación',  '2026-09-16', '2026-09-16',  72900,  26000, 'alineación');

CREATE TABLE hora (
    id_hora     INTEGER PRIMARY KEY,
    paciente    VARCHAR(40) NOT NULL,
    edad        INTEGER     NOT NULL,
    sector      VARCHAR(10) NOT NULL,    -- rojo, azul o verde
    profesional VARCHAR(15) NOT NULL,
    fecha       DATE        NOT NULL,
    asistio     INTEGER,                 -- 1 sí, 0 no; NULL: la hora todavía no llega
    espera_min  INTEGER                  -- minutos en sala de espera; NULL si no asistió
);

INSERT INTO hora VALUES
 (1,  'Rosa Contreras',  71, 'azul',  'medicina',   '2026-10-05', 1,    35),
 (2,  'Matías Fuentes',   8, 'rojo',  'dental',     '2026-10-05', 1,    12),
 (3,  'Javiera Muñoz',   29, 'verde', 'matrona',    '2026-10-05', 0,    NULL),
 (4,  'Luis Sepúlveda',  66, 'azul',  'enfermería', '2026-10-06', 1,    48),
 (5,  'Ana Riquelme',    15, 'verde', 'dental',     '2026-10-06', 1,    20),
 (6,  'Pedro Muñoz',     80, 'rojo',  'medicina',   '2026-10-06', 1,    55),
 (7,  'Camila Vergara',  33, 'azul',  'matrona',    '2026-10-07', 1,    9),
 (8,  'Jorge Toledo',    58, 'verde', 'nutrición',  '2026-10-07', 0,    NULL),
 (9,  'Sofía Mella',     12, 'rojo',  'enfermería', '2026-10-07', 1,    15),
 (10, 'Héctor Muñoz',    69, 'azul',  'medicina',   '2026-10-07', 1,    41),
 (11, 'Valentina Soto',  24, 'rojo',  'matrona',    '2026-10-08', NULL, NULL),
 (12, 'Raúl Castillo',   74, 'verde', 'medicina',   '2026-10-08', NULL, NULL),
 (13, 'Daniela Pino',    17, 'rojo',  'dental',     '2026-10-09', NULL, NULL),
 (14, 'Manuel Ortiz',    45, 'azul',  'nutrición',  '2026-10-09', NULL, NULL);

-- ------------------------------------------------------------------ parte 2 · consultas
-- Teoría (taller)

-- @todo
SELECT * FROM orden_trabajo;

-- @proyeccion
SELECT patente, servicio, monto
FROM orden_trabajo
WHERE servicio = 'frenos';

-- @alias
SELECT patente, monto, ROUND(monto * 1.19) AS con_iva
FROM orden_trabajo
WHERE servicio = 'frenos';

-- @alias_en_where
SELECT patente, ROUND(monto * 1.19) AS con_iva
FROM orden_trabajo
WHERE con_iva > 140000;

-- @alias_en_where_estandar
SELECT patente, ROUND(monto * 1.19) AS con_iva
FROM orden_trabajo
WHERE monto * 1.19 > 140000;

-- @sin_distinct
SELECT marca FROM orden_trabajo WHERE km > 150000;

-- @distinct
SELECT DISTINCT marca FROM orden_trabajo WHERE km > 150000 ORDER BY marca;

-- @between
SELECT id_ot, patente, ingreso
FROM orden_trabajo
WHERE ingreso BETWEEN '2026-09-07' AND '2026-09-09';

-- @in
SELECT id_ot, patente, servicio
FROM orden_trabajo
WHERE servicio IN ('embrague', 'alineación');

-- @like
SELECT id_ot, patente, detalle
FROM orden_trabajo
WHERE detalle LIKE '%pastillas%';

-- @igual_null
SELECT id_ot, patente FROM orden_trabajo WHERE entrega = NULL;

-- @is_null
SELECT id_ot, patente, servicio FROM orden_trabajo WHERE entrega IS NULL;

-- @null_aritmetica
SELECT id_ot, monto, monto * 1.19 AS con_iva, COALESCE(monto, 0) AS monto_o_cero
FROM orden_trabajo
WHERE servicio = 'diagnóstico';

-- @and_or_sin_parentesis
SELECT id_ot, servicio, entrega
FROM orden_trabajo
WHERE servicio = 'frenos' OR servicio = 'embrague' AND entrega IS NULL;

-- @and_or_con_parentesis
SELECT id_ot, servicio, entrega
FROM orden_trabajo
WHERE (servicio = 'frenos' OR servicio = 'embrague') AND entrega IS NULL;

-- @order_by
SELECT servicio, patente, monto
FROM orden_trabajo
WHERE monto IS NOT NULL
ORDER BY servicio, monto DESC;

-- @limit
SELECT patente, km FROM orden_trabajo ORDER BY km DESC LIMIT 3;

-- @limit_offset
SELECT patente, km FROM orden_trabajo ORDER BY km DESC LIMIT 3 OFFSET 3;

-- @division
SELECT patente, km / 1000 AS miles_entera, km / 1000.0 AS miles, ROUND(km / 1000.0, 1) AS miles_1
FROM orden_trabajo
WHERE id_ot <= 3;

-- @texto
SELECT marca || ' ' || patente AS auto, UPPER(servicio) AS servicio_may,
       LENGTH(detalle) AS largo, SUBSTR(patente, 1, 2) AS inicio
FROM orden_trabajo
WHERE id_ot IN (2, 7, 11);

-- @fechas
SELECT patente, strftime('%d-%m-%Y', ingreso) AS ingreso_cl,
       julianday(entrega) - julianday(ingreso) AS dias,
       date(ingreso, '+30 days') AS garantia_hasta
FROM orden_trabajo
WHERE servicio = 'embrague';

-- @case
SELECT id_ot, monto,
       CASE
           WHEN monto IS NULL THEN 'sin presupuesto'
           WHEN monto < 50000 THEN 'menor'
           WHEN monto < 150000 THEN 'medio'
           ELSE 'mayor'
       END AS tramo
FROM orden_trabajo
ORDER BY id_ot;

-- @cuenta
SELECT COUNT(*) AS en_taller FROM orden_trabajo WHERE entrega IS NULL;

-- Ejemplo resuelto (taller, jueves 17-09-2026)

-- @ej_en_taller
SELECT patente, servicio, ingreso,
       julianday('2026-09-17') - julianday(ingreso) AS dias_en_taller
FROM orden_trabajo
WHERE entrega IS NULL
ORDER BY dias_en_taller DESC, patente;

-- @ej_cobro
SELECT patente, servicio, monto, ROUND(monto * 1.19) AS total_con_iva
FROM orden_trabajo
WHERE entrega IS NOT NULL
  AND servicio IN ('frenos', 'embrague')
ORDER BY total_con_iva DESC;

-- @ej_plazo
SELECT patente, servicio,
       julianday(entrega) - julianday(ingreso) AS dias,
       CASE
           WHEN entrega = ingreso THEN 'mismo día'
           WHEN julianday(entrega) - julianday(ingreso) <= 1 THEN 'al día siguiente'
           ELSE 'más de un día'
       END AS plazo
FROM orden_trabajo
WHERE entrega IS NOT NULL
ORDER BY dias DESC, patente;

-- Ejercicios (CESFAM)

-- @e1
SELECT paciente, edad
FROM hora
WHERE sector = 'azul' AND edad >= 65
ORDER BY edad DESC;

-- @e2
SELECT paciente, profesional, fecha
FROM hora
WHERE profesional IN ('matrona', 'dental')
  AND fecha BETWEEN '2026-10-05' AND '2026-10-07'
ORDER BY fecha, paciente;

-- @e3a
SELECT DISTINCT profesional FROM hora ORDER BY profesional;

-- @e3b
SELECT COUNT(*) AS sin_registro FROM hora WHERE asistio IS NULL;

-- @e3c
SELECT COUNT(*) AS sin_registro FROM hora WHERE asistio = NULL;

-- @e5_mal
SELECT paciente, sector, edad
FROM hora
WHERE sector = 'rojo' OR sector = 'verde' AND edad < 18
ORDER BY id_hora;

-- @e5_bien
SELECT paciente, sector, edad
FROM hora
WHERE (sector = 'rojo' OR sector = 'verde') AND edad < 18
ORDER BY id_hora;

-- @e6
SELECT paciente, espera_min,
       CASE
           WHEN espera_min IS NULL THEN 'sin dato'
           WHEN espera_min <= 15 THEN 'a tiempo'
           WHEN espera_min <= 40 THEN 'demora'
           ELSE 'larga'
       END AS tramo
FROM hora
WHERE fecha <= '2026-10-07'
ORDER BY id_hora;

-- @e8
SELECT SUBSTR(paciente, INSTR(paciente, ' ') + 1) AS apellido,
       strftime('%d-%m-%Y', fecha) AS dia,
       julianday(fecha) - julianday('2026-10-07') AS faltan,
       profesional
FROM hora
WHERE asistio IS NULL
ORDER BY fecha, apellido;

-- @e9a !error
SELECT paciente FROM hora WHERE profesional = medicina;

-- @e9a_bien
SELECT paciente FROM hora WHERE profesional = 'medicina';

-- @e9b
SELECT paciente FROM hora WHERE espera_min = NULL;

-- @e9b_bien
SELECT paciente FROM hora WHERE espera_min IS NULL;

-- @e9c
SELECT paciente FROM hora WHERE fecha = 07/10/2026;

-- @e9c_valor
SELECT 07/10/2026 AS lo_que_compara;

-- @e9c_bien
SELECT paciente FROM hora WHERE fecha = '2026-10-07';

-- @e9d
SELECT paciente FROM hora WHERE paciente LIKE 'Muñoz';

-- @e9d_bien
SELECT paciente FROM hora WHERE paciente LIKE '%Muñoz';
