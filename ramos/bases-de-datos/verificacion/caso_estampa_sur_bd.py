"""Caso integrador de Bases de Datos · la base de datos de Estampa Sur.

El mismo taller ficticio de los otros ramos, ahora como sistema de información: productos, tiendas,
clientes, pedidos, detalle de pedidos, proveedores y órdenes de producción. El script crea la base en
SQLite con SQL estándar (corre igual en MySQL salvo lo que se indica), la llena con datos SIMULADOS con
semilla fija y ejecuta las consultas que usan las unidades.

    python caso_estampa_sur_bd.py          # crea datos/estampa_sur.db, imprime la cadena
    python caso_estampa_sur_bd.py --json   # además deja caso_estampa_sur_bd.json

MySQL 8.0 y 8.4 aceptan el REFERENCES escrito junto a la columna pero no crean la clave foránea:
para MySQL se usa sql/u08_esquema_mysql.sql, con las claves en líneas FOREIGN KEY aparte (unidad 8).

Los productos, precios y tiendas vienen de los otros ramos (Gestión de Operaciones, Optimización,
Tópicos y Contabilidad). Clientes y pedidos son inventados.
"""
from pathlib import Path
import json, random, sqlite3, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parents[1]
DB = BASE / "datos" / "estampa_sur.db"
SQL_ESQUEMA = BASE / "datos" / "esquema.sql"
SEMILLA = 2024

ESQUEMA = """
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
"""

TIENDAS = [(1, "Centro", "Concepción"), (2, "Puerto", "Talcahuano"), (3, "Lagos", "San Pedro de la Paz"),
           (4, "Valle", "Chiguayante"), (5, "Costa", "Penco"), (6, "Cerro", "Hualpén")]   # nombres ficticios del caso de Tópicos
PRODUCTOS = [(1, "poleras básicas", 3_990, 2_610, 30), (2, "polerones", 9_890, 5_950, 90),
             (3, "poleras estampado doble", 6_290, 4_020, 110), (4, "bolsas", 2_490, 1_530, 20),
             (5, "gorros", 3_190, 2_020, 30)]
PROVEEDORES = [(1, "Telas Norte", "prendas lisas"), (2, "Algodones Sur", "prendas lisas"),
               (3, "Textil Ñuble", "prendas lisas"), (4, "Tintas del Bío", "tintas")]
SUMINISTRA = [(1, 1, 2_400), (2, 1, 2_430), (2, 2, 5_400), (3, 3, 3_600), (1, 4, 1_350), (3, 5, 1_880), (2, 5, 1_910)]
LOTES = {1: 720, 2: 360, 3: 360, 4: 540, 5: 480}                 # Gestión de Operaciones U7
MPS = {1: [0, 720, 720, 0, 720, 720, 720, 720], 2: [360, 0, 360, 0, 360, 360, 0, 360],
       3: [0, 360, 0, 360, 0, 360, 360, 0], 4: [0, 540, 0, 540, 0, 540, 0, 540], 5: [0, 0, 0, 480, 0, 480, 0, 0]}


def generar():
    rnd = random.Random(SEMILLA)
    tipos = ["colegio"] * 6 + ["club"] * 5 + ["empresa"] * 7 + ["persona"] * 12
    nombres = [f"Cliente {i:02d}" for i in range(1, 31)]
    clientes = [(i + 1, nombres[i], tipos[i], i % 6 + 1) for i in range(30)]      # cinco clientes por tienda
    pedidos, detalle = [], []
    for k in range(1, 121):
        c = rnd.randint(1, 26)                    # los clientes 27 a 30 todavía no compran
        dia = rnd.randint(1, 31)
        estado = rnd.choices(["entregado", "en taller", "pendiente"], [0.7, 0.2, 0.1])[0]
        pedidos.append((k, c, f"2026-03-{dia:02d}", estado))
        for p in rnd.sample(range(1, 6), rnd.choice([1, 1, 2, 2, 3])):
            q = rnd.randint(5, 80) if clientes[c - 1][2] != "persona" else rnd.randint(1, 6)
            detalle.append((k, p, q, PRODUCTOS[p - 1][2]))
    ordenes = [(None, p, s + 1, q) for p, filas in MPS.items() for s, q in enumerate(filas) if q]
    return clientes, pedidos, detalle, ordenes


def crear():
    DB.parent.mkdir(exist_ok=True)
    if DB.exists():
        DB.unlink()
    SQL_ESQUEMA.write_text(ESQUEMA.strip() + "\n", encoding="utf-8")
    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(ESQUEMA)
    clientes, pedidos, detalle, ordenes = generar()
    con.executemany("INSERT INTO tienda VALUES (?,?,?)", TIENDAS)
    con.executemany("INSERT INTO producto VALUES (?,?,?,?,?)", PRODUCTOS)
    con.executemany("INSERT INTO proveedor VALUES (?,?,?)", PROVEEDORES)
    con.executemany("INSERT INTO suministra VALUES (?,?,?)", SUMINISTRA)
    con.executemany("INSERT INTO cliente VALUES (?,?,?,?)", clientes)
    con.executemany("INSERT INTO pedido VALUES (?,?,?,?)", pedidos)
    con.executemany("INSERT INTO detalle_pedido VALUES (?,?,?,?)", detalle)
    con.executemany("INSERT INTO orden_produccion VALUES (?,?,?,?)", ordenes)
    con.commit()
    return con


CONSULTAS = {
    "u9_productos_caros": "SELECT nombre, precio FROM producto WHERE precio > 4000 ORDER BY precio DESC",
    "u9_pedidos_pendientes": "SELECT COUNT(*) FROM pedido WHERE estado = 'pendiente'",
    "u10_ventas_por_tienda": """
        SELECT t.nombre, SUM(d.cantidad * d.precio_unit) AS ventas
        FROM detalle_pedido d
        JOIN pedido p   ON p.id_pedido = d.id_pedido
        JOIN cliente c  ON c.id_cliente = p.id_cliente
        JOIN tienda t   ON t.id_tienda = c.id_tienda
        GROUP BY t.nombre ORDER BY ventas DESC""",
    "u10_unidades_por_producto": """
        SELECT pr.nombre, SUM(d.cantidad) AS unidades
        FROM detalle_pedido d JOIN producto pr ON pr.id_producto = d.id_producto
        GROUP BY pr.nombre ORDER BY unidades DESC""",
    "u10_margen_por_tipo_cliente": """
        SELECT c.tipo, SUM(d.cantidad * (d.precio_unit - pr.costo_var)) AS margen
        FROM detalle_pedido d
        JOIN pedido p    ON p.id_pedido = d.id_pedido
        JOIN cliente c   ON c.id_cliente = p.id_cliente
        JOIN producto pr ON pr.id_producto = d.id_producto
        GROUP BY c.tipo HAVING SUM(d.cantidad) > 100 ORDER BY margen DESC""",
    "u10_clientes_sin_pedidos": """
        SELECT COUNT(*) FROM cliente c LEFT JOIN pedido p ON p.id_cliente = c.id_cliente
        WHERE p.id_pedido IS NULL""",
    "u11_clientes_sobre_promedio": """
        SELECT COUNT(*) FROM (
            SELECT p.id_cliente, SUM(d.cantidad * d.precio_unit) AS total
            FROM pedido p JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
            GROUP BY p.id_cliente) x
        WHERE x.total > (SELECT AVG(t) FROM (
            SELECT SUM(d.cantidad * d.precio_unit) AS t
            FROM pedido p JOIN detalle_pedido d ON d.id_pedido = p.id_pedido GROUP BY p.id_cliente) y)""",
    "u11_proveedor_mas_barato": """
        SELECT pr.nombre AS producto, pv.nombre AS proveedor, s.costo_unidad
        FROM suministra s
        JOIN producto pr  ON pr.id_producto = s.id_producto
        JOIN proveedor pv ON pv.id_proveedor = s.id_proveedor
        WHERE s.costo_unidad = (SELECT MIN(s2.costo_unidad) FROM suministra s2 WHERE s2.id_producto = s.id_producto)
        ORDER BY pr.id_producto""",
    "u11_produccion_semana_6": """
        SELECT pr.nombre, o.lote, o.lote * pr.seg_estampado / 3600.0 AS horas_estampado
        FROM orden_produccion o JOIN producto pr ON pr.id_producto = o.id_producto
        WHERE o.semana = 6 ORDER BY o.id_producto""",
}


def calcular():
    con = crear()
    R = {"tablas": {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                    for t in ["tienda", "producto", "proveedor", "suministra", "cliente", "pedido",
                              "detalle_pedido", "orden_produccion"]}}
    for k, q in CONSULTAS.items():
        R[k] = con.execute(q).fetchall()
    # coherencia con Gestión de Operaciones: la semana 6 suma 33 h de estampado
    assert abs(sum(r[2] for r in R["u11_produccion_semana_6"]) - 33) < 1e-9
    con.close()
    return R


if __name__ == "__main__":
    R = calcular()
    for k, v in R.items():
        print(f"== {k}: {v}")
    if "--json" in sys.argv:
        Path(__file__).with_suffix(".json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
