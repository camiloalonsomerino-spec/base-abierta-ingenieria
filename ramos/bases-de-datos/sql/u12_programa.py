"""Unidad 12 · La base dentro de un programa: las funciones de Python que muestra la unidad.

Cada función recibe una conexión abierta (o la ruta de la base), así se puede probar sobre una copia.
El verificador (verificacion/u12_transacciones.py) las ejecuta sobre copias y busca su código en la unidad.
"""
import sqlite3


def abrir(ruta):
    con = sqlite3.connect(ruta)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def stock_bajo(con, minimo):
    cur = con.cursor()
    cur.execute("SELECT nombre, stock FROM producto WHERE stock < ? ORDER BY stock", (minimo,))
    return cur.fetchall()


def vender(con, id_venta, fecha, vendedor, lineas):
    """Registra una venta con sus líneas y descuenta el stock: todo o nada.
    lineas es una lista de (id_producto, cantidad)."""
    with con:
        con.execute("INSERT INTO venta VALUES (?, ?, ?)", (id_venta, fecha, vendedor))
        for id_producto, cantidad in lineas:
            cur = con.execute("INSERT INTO detalle_venta "
                              "SELECT ?, id_producto, ?, precio FROM producto "
                              "WHERE id_producto = ?",
                              (id_venta, cantidad, id_producto))
            if cur.rowcount != 1:
                raise ValueError(f"no existe el producto {id_producto}")
            con.execute("UPDATE producto SET stock = stock - ? WHERE id_producto = ?",
                        (cantidad, id_producto))


def leer_y_escribir(ruta, id_producto, cantidad):
    """Dos vendedores leen el stock, calculan en Python y escriben el resultado (MAL)."""
    a, b = abrir(ruta), abrir(ruta)
    sql = "SELECT stock FROM producto WHERE id_producto = ?"
    stock_a = a.execute(sql, (id_producto,)).fetchall()[0][0]
    stock_b = b.execute(sql, (id_producto,)).fetchall()[0][0]
    vendidas = 0
    for con, visto in ((a, stock_a), (b, stock_b)):
        if visto >= cantidad:
            con.execute("UPDATE producto SET stock = ? WHERE id_producto = ?",
                        (visto - cantidad, id_producto))
            con.commit()
            vendidas += cantidad
    final = a.execute(sql, (id_producto,)).fetchall()[0][0]
    a.close(); b.close()
    return stock_a, vendidas, final


def descontar_en_la_base(ruta, id_producto, cantidad):
    """Los mismos dos vendedores, pero el descuento y la condición van en una sola sentencia."""
    a, b = abrir(ruta), abrir(ruta)
    filas = []
    for con in (a, b):
        cur = con.execute("UPDATE producto SET stock = stock - ? "
                          "WHERE id_producto = ? AND stock >= ?",
                          (cantidad, id_producto, cantidad))
        con.commit()
        filas.append(cur.rowcount)
    sql = "SELECT stock FROM producto WHERE id_producto = ?"
    final = a.execute(sql, (id_producto,)).fetchall()[0][0]
    a.close(); b.close()
    return filas, final


def dos_cajas(ruta):
    """La caja A está a mitad de una transacción; la caja B mira y trata de escribir."""
    a = sqlite3.connect(ruta, isolation_level=None)
    b = sqlite3.connect(ruta, isolation_level=None, timeout=0)
    sql = "SELECT stock FROM producto WHERE id_producto = 2"
    visto = []
    a.execute("BEGIN")
    a.execute("UPDATE producto SET stock = stock - 1 WHERE id_producto = 2")
    visto.append(("A, dentro de su transacción", a.execute(sql).fetchall()[0][0]))
    visto.append(("B, mientras A no confirma", b.execute(sql).fetchall()[0][0]))
    try:
        b.execute("UPDATE producto SET stock = stock - 1 WHERE id_producto = 2")
    except sqlite3.OperationalError as e:
        visto.append(("B trata de escribir", str(e)))
    a.execute("COMMIT")
    visto.append(("B, después del COMMIT de A", b.execute(sql).fetchall()[0][0]))
    a.close(); b.close()
    return visto


def buscar_inseguro(con, texto):
    sql = "SELECT nombre, precio FROM producto WHERE nombre = '" + texto + "'"
    return con.execute(sql).fetchall()


def buscar(con, texto):
    sql = "SELECT nombre, precio FROM producto WHERE nombre = ?"
    return con.execute(sql, (texto,)).fetchall()


def anular_venta_inseguro(con, id_texto):
    with con:
        cur = con.execute("DELETE FROM detalle_venta WHERE id_venta = " + id_texto)
    return cur.rowcount


def anular_venta(con, id_texto):
    with con:
        cur = con.execute("DELETE FROM detalle_venta WHERE id_venta = ?", (id_texto,))
    return cur.rowcount


def crear_cuentas(con):
    with con:
        con.execute("CREATE TABLE cuenta (id INTEGER PRIMARY KEY, titular VARCHAR(30) NOT NULL, "
                    "saldo INTEGER NOT NULL CHECK (saldo >= 0))")
        con.executemany("INSERT INTO cuenta VALUES (?, ?, ?)",
                        [(1, "4.° A", 85000), (2, "4.° B", 42500),
                         (3, "Centro de padres", 120000)])


def transferir(con, origen, destino, monto):
    """Abona y después descuenta; si el descuento falla, el abono se deshace."""
    with con:
        con.execute("UPDATE cuenta SET saldo = saldo + ? WHERE id = ?", (monto, destino))
        con.execute("UPDATE cuenta SET saldo = saldo - ? WHERE id = ?", (monto, origen))


def transferir_sin_transaccion(ruta, origen, destino, monto):
    con = sqlite3.connect(ruta, isolation_level=None)      # cada sentencia se confirma sola
    try:
        con.execute("UPDATE cuenta SET saldo = saldo + ? WHERE id = ?", (monto, destino))
        con.execute("UPDATE cuenta SET saldo = saldo - ? WHERE id = ?", (monto, origen))
    finally:
        con.close()


def registrar_pedido(con, id_cliente, fecha, lineas):
    """Registra un pedido de Estampa Sur con su detalle, todo o nada.
    lineas es una lista de (id_producto, cantidad); el precio sale de la tabla producto."""
    with con:
        cur = con.execute("INSERT INTO pedido (id_cliente, fecha, estado) "
                          "VALUES (?, ?, 'pendiente')", (id_cliente, fecha))
        id_pedido = cur.lastrowid
        for id_producto, cantidad in lineas:
            cur = con.execute("INSERT INTO detalle_pedido "
                              "(id_pedido, id_producto, cantidad, precio_unit) "
                              "SELECT ?, id_producto, ?, precio FROM producto "
                              "WHERE id_producto = ?",
                              (id_pedido, cantidad, id_producto))
            if cur.rowcount != 1:
                raise ValueError(f"no existe el producto {id_producto}")
    return id_pedido


def marcar_entregado_inseguro(con, id_texto):
    with con:
        sql = "UPDATE pedido SET estado = 'entregado' WHERE id_pedido = " + id_texto
        cur = con.execute(sql)
    return cur.rowcount


def marcar_entregado(con, id_texto):
    with con:
        sql = "UPDATE pedido SET estado = 'entregado' WHERE id_pedido = ?"
        cur = con.execute(sql, (id_texto,))
    return cur.rowcount
