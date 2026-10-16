-- Ejercicio 6.1 · reservas de canchas de pádel en Viña del Mar (datos inventados)
CREATE TABLE reserva (
    id_reserva  INTEGER PRIMARY KEY,
    fecha       DATE NOT NULL,
    hora        VARCHAR(5) NOT NULL,
    cancha      INTEGER NOT NULL,
    superficie  VARCHAR(20) NOT NULL,
    precio_hora INTEGER NOT NULL,
    rut_cliente VARCHAR(12) NOT NULL,
    cliente     VARCHAR(60) NOT NULL,
    fono        VARCHAR(16) NOT NULL
);
INSERT INTO reserva VALUES (1, '2026-11-06', '19:00', 1, 'césped', 14000, '19.876.301-2', 'Ignacia Fuentes', '+56 9 4410 2287');
INSERT INTO reserva VALUES (2, '2026-11-06', '19:00', 2, 'cemento', 11000, '20.345.998-K', 'Matías León', '+56 9 5503 8812');
INSERT INTO reserva VALUES (3, '2026-11-06', '20:00', 1, 'césped', 14000, '21.456.770-9', 'Catalina Reyes', '+56 9 6627 1043');
INSERT INTO reserva VALUES (4, '2026-11-07', '10:00', 2, 'cemento', 11000, '19.876.301-2', 'Ignacia Fuentes', '+56 9 4410 2287');
INSERT INTO reserva VALUES (5, '2026-11-07', '11:00', 3, 'césped', 16500, '20.345.998-K', 'Matías León', '+56 9 5503 8812');
INSERT INTO reserva VALUES (6, '2026-11-07', '12:00', 2, 'cemento', 11000, '19.876.301-2', 'Ignacia Fuentes', '+56 9 4410 2287');
INSERT INTO reserva VALUES (7, '2026-11-08', '18:00', 2, 'cemento', 11000, '18.234.509-1', 'Andrés Silva', '+56 9 7731 5590');
INSERT INTO reserva VALUES (8, '2026-11-08', '19:00', 1, 'césped', 14000, '21.456.770-9', 'Catalina Reyes', '+56 9 6627 1043');

-- @cancha2 filas que hay que corregir si sube el precio de la cancha 2
SELECT COUNT(*) AS filas FROM reserva WHERE cancha = 2;
-- @una_reserva clientes que desaparecen si se anula su única reserva
SELECT rut_cliente, cliente, COUNT(*) AS reservas
FROM reserva
GROUP BY rut_cliente, cliente
HAVING COUNT(*) = 1;
-- @cancha4 registrar una cancha nueva que todavía no tiene reservas
INSERT INTO reserva (cancha, superficie, precio_hora) VALUES (4, 'cemento', 12500);
