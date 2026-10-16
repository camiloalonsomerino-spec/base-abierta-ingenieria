-- Ejercicio 6.7 · planilla de una liga de futsal de Antofagasta (datos inventados)
CREATE TABLE planilla (
    fecha        DATE NOT NULL,
    cancha       VARCHAR(20) NOT NULL,
    direccion    VARCHAR(40) NOT NULL,
    local        VARCHAR(30) NOT NULL,
    visita       VARCHAR(30) NOT NULL,
    goles_local  INTEGER NOT NULL,
    goles_visita INTEGER NOT NULL,
    arbitro      VARCHAR(40) NOT NULL,
    fono_arbitro VARCHAR(16) NOT NULL,
    PRIMARY KEY (fecha, cancha)
);
INSERT INTO planilla VALUES ('2026-08-01', 'Coloso', 'calle Coloso 1170', 'Cobre FC', 'Los Changos', 4, 2, 'Juan Contreras', '+56 9 3301 4478');
INSERT INTO planilla VALUES ('2026-08-01', 'Las Algas', 'pasaje Las Algas 225', 'Atlético Caliche', 'Puerto Norte', 3, 3, 'Marisol Páez', '+56 9 4420 7716');
INSERT INTO planilla VALUES ('2026-08-08', 'Coloso', 'calle Coloso 1170', 'Unión Salitre', 'La Portada FS', 1, 5, 'Diego Saavedra', '+56 9 5519 0362');
INSERT INTO planilla VALUES ('2026-08-08', 'Las Algas', 'pasaje Las Algas 225', 'Los Changos', 'Atlético Caliche', 2, 0, 'Juan Contreras', '+56 9 3301 4478');
INSERT INTO planilla VALUES ('2026-08-15', 'Coloso', 'calle Coloso 1170', 'Puerto Norte', 'Cobre FC', 2, 6, 'Marisol Páez', '+56 9 4420 7716');
INSERT INTO planilla VALUES ('2026-08-15', 'Las Algas', 'pasaje Las Algas 225', 'La Portada FS', 'Los Changos', 3, 1, 'Diego Saavedra', '+56 9 5519 0362');
INSERT INTO planilla VALUES ('2026-08-22', 'Coloso', 'calle Coloso 1170', 'Atlético Caliche', 'Unión Salitre', 4, 4, 'Juan Contreras', '+56 9 3301 4478');
INSERT INTO planilla VALUES ('2026-08-22', 'Las Algas', 'pasaje Las Algas 225', 'Cobre FC', 'La Portada FS', 2, 3, 'Marisol Páez', '+56 9 4420 7716');

-- La pauta: tres tablas en tercera forma normal
CREATE TABLE cancha (
    nombre       VARCHAR(20) NOT NULL PRIMARY KEY,
    direccion    VARCHAR(40) NOT NULL
);
CREATE TABLE arbitro (
    nombre       VARCHAR(40) NOT NULL PRIMARY KEY,
    fono         VARCHAR(16) NOT NULL
);
CREATE TABLE partido (
    fecha        DATE NOT NULL,
    cancha       VARCHAR(20) NOT NULL,
    local        VARCHAR(30) NOT NULL,
    visita       VARCHAR(30) NOT NULL,
    goles_local  INTEGER NOT NULL,
    goles_visita INTEGER NOT NULL,
    arbitro      VARCHAR(40) NOT NULL,
    PRIMARY KEY (fecha, cancha),
    UNIQUE (fecha, local),
    UNIQUE (fecha, visita),
    FOREIGN KEY (cancha) REFERENCES cancha (nombre),
    FOREIGN KEY (arbitro) REFERENCES arbitro (nombre)
);
INSERT INTO cancha SELECT DISTINCT cancha, direccion FROM planilla;
INSERT INTO arbitro SELECT DISTINCT arbitro, fono_arbitro FROM planilla;
INSERT INTO partido SELECT fecha, cancha, local, visita, goles_local, goles_visita, arbitro FROM planilla;

-- @filas
SELECT 'cancha' AS tabla, COUNT(*) AS filas FROM cancha
UNION ALL SELECT 'arbitro', COUNT(*) FROM arbitro
UNION ALL SELECT 'partido', COUNT(*) FROM partido;
-- @reconstruir
SELECT
  (SELECT COUNT(*) FROM (
     SELECT * FROM planilla
     EXCEPT
     SELECT p.fecha, p.cancha, c.direccion, p.local, p.visita, p.goles_local, p.goles_visita, p.arbitro, a.fono
     FROM partido p JOIN cancha c ON c.nombre = p.cancha JOIN arbitro a ON a.nombre = p.arbitro)) AS faltan,
  (SELECT COUNT(*) FROM (
     SELECT p.fecha, p.cancha, c.direccion, p.local, p.visita, p.goles_local, p.goles_visita, p.arbitro, a.fono
     FROM partido p JOIN cancha c ON c.nombre = p.cancha JOIN arbitro a ON a.nombre = p.arbitro
     EXCEPT
     SELECT * FROM planilla)) AS sobran;
-- @doble un equipo que juega dos partidos la misma fecha
INSERT INTO partido VALUES ('2026-08-22', 'Norte', 'Cobre FC', 'Puerto Norte', 0, 0, 'Diego Saavedra');
