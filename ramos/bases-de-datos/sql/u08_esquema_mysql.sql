-- Unidad 8 · El esquema de Estampa Sur escrito para MySQL 8
-- Las mismas 8 tablas de datos/esquema.sql con tres cambios:
--   1. las claves foráneas van en una línea FOREIGN KEY aparte (MySQL 8.0 y 8.4 ignoran sin aviso un
--      REFERENCES escrito al lado de la columna; recién MySQL 9 lo acepta);
--   2. AUTO_INCREMENT en las claves que la base numera sola;
--   3. ENGINE=InnoDB, el motor de MySQL que hace cumplir las claves foráneas.
-- El verificador u08_ddl_dml.py lo carga en SQLite (quitando AUTO_INCREMENT y ENGINE) y comprueba que
-- las columnas, las claves primarias y las foráneas sean las mismas que las de datos/esquema.sql.

CREATE TABLE tienda (
    id_tienda   INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(40) NOT NULL UNIQUE,
    comuna      VARCHAR(40) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE producto (
    id_producto   INT AUTO_INCREMENT PRIMARY KEY,
    nombre        VARCHAR(40) NOT NULL UNIQUE,
    precio        INT NOT NULL CHECK (precio > 0),
    costo_var     INT NOT NULL CHECK (costo_var > 0),
    seg_estampado INT NOT NULL
) ENGINE=InnoDB;

CREATE TABLE proveedor (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(40) NOT NULL,
    rubro        VARCHAR(30) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE suministra (
    id_proveedor INT NOT NULL,
    id_producto  INT NOT NULL,
    costo_unidad INT NOT NULL,
    PRIMARY KEY (id_proveedor, id_producto),
    FOREIGN KEY (id_proveedor) REFERENCES proveedor(id_proveedor),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
) ENGINE=InnoDB;

CREATE TABLE cliente (
    id_cliente  INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(60) NOT NULL,
    tipo        VARCHAR(12) NOT NULL CHECK (tipo IN ('colegio', 'club', 'empresa', 'persona')),
    id_tienda   INT NOT NULL,
    FOREIGN KEY (id_tienda) REFERENCES tienda(id_tienda)
) ENGINE=InnoDB;

CREATE TABLE pedido (
    id_pedido   INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente  INT NOT NULL,
    fecha       DATE NOT NULL,
    estado      VARCHAR(12) NOT NULL CHECK (estado IN ('pendiente', 'en taller', 'entregado')),
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
) ENGINE=InnoDB;

CREATE TABLE detalle_pedido (
    id_pedido   INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad    INT NOT NULL CHECK (cantidad > 0),
    precio_unit INT NOT NULL,
    PRIMARY KEY (id_pedido, id_producto),
    FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
) ENGINE=InnoDB;

CREATE TABLE orden_produccion (
    id_orden    INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    semana      INT NOT NULL,
    lote        INT NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
) ENGINE=InnoDB;
