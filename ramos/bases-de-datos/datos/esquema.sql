CREATE TABLE tienda (
    id_tienda   INTEGER PRIMARY KEY,
    nombre      VARCHAR(40) NOT NULL UNIQUE,
    comuna      VARCHAR(40) NOT NULL
);
CREATE TABLE producto (
    id_producto INTEGER PRIMARY KEY,
    nombre      VARCHAR(40) NOT NULL UNIQUE,
    precio      INTEGER NOT NULL CHECK (precio > 0),
    costo_var   INTEGER NOT NULL CHECK (costo_var > 0),
    seg_estampado INTEGER NOT NULL
);
CREATE TABLE proveedor (
    id_proveedor INTEGER PRIMARY KEY,
    nombre       VARCHAR(40) NOT NULL,
    rubro        VARCHAR(30) NOT NULL
);
CREATE TABLE suministra (
    id_proveedor INTEGER NOT NULL REFERENCES proveedor(id_proveedor),
    id_producto  INTEGER NOT NULL REFERENCES producto(id_producto),
    costo_unidad INTEGER NOT NULL,
    PRIMARY KEY (id_proveedor, id_producto)
);
CREATE TABLE cliente (
    id_cliente  INTEGER PRIMARY KEY,
    nombre      VARCHAR(60) NOT NULL,
    tipo        VARCHAR(12) NOT NULL CHECK (tipo IN ('colegio', 'club', 'empresa', 'persona')),
    id_tienda   INTEGER NOT NULL REFERENCES tienda(id_tienda)
);
CREATE TABLE pedido (
    id_pedido   INTEGER PRIMARY KEY,
    id_cliente  INTEGER NOT NULL REFERENCES cliente(id_cliente),
    fecha       DATE NOT NULL,
    estado      VARCHAR(12) NOT NULL CHECK (estado IN ('pendiente', 'en taller', 'entregado'))
);
CREATE TABLE detalle_pedido (
    id_pedido   INTEGER NOT NULL REFERENCES pedido(id_pedido),
    id_producto INTEGER NOT NULL REFERENCES producto(id_producto),
    cantidad    INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unit INTEGER NOT NULL,
    PRIMARY KEY (id_pedido, id_producto)
);
CREATE TABLE orden_produccion (
    id_orden    INTEGER PRIMARY KEY,
    id_producto INTEGER NOT NULL REFERENCES producto(id_producto),
    semana      INTEGER NOT NULL,
    lote        INTEGER NOT NULL
);
