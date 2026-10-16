"""Unidad 12 · Transacciones, índices y la base dentro de un programa. Ejecuta todo lo de la unidad;
con --revisar lo busca en el .md.

Los scripts están en ramos/bases-de-datos/sql/:
  u12_transacciones.sql  base del ejemplo (ferretería) y su sesión: transacciones, errores, índices
  u12_caso.sql           sesión sobre una COPIA de la base del caso (pedido 121, pedido 122 que falla,
                         índices); sus marcas «-- @python» llaman a las funciones de u12_programa.py
  u12_programa.py        las funciones de Python que muestra la unidad

Este script:
1. crea la ferretería en una carpeta temporal y corre su sesión bloque por bloque, en orden;
2. crea una copia de la base del caso con el script del caso (datos/estampa_sur.db no se toca) y corre
   su sesión; las marcas «-- @python» ejecutan registrar_pedido sobre esa copia;
3. corre cada función de u12_programa.py sobre copias nuevas (stock, dos cajas, dos vendedores,
   inyección SQL, transferencias) y la inyección del caso sobre una copia de juguete;
4. comprueba por un segundo camino (Python puro) los montos, los conteos y las invariantes;
5. compara con el script del caso (CADENA);
6. con --revisar, exige que cada línea de SQL y de Python, cada tabla, cada plan, cada mensaje de
   error y cada salida esté en el .md.

    python u12_transacciones.py            # imprime los resultados
    python u12_transacciones.py --revisar  # además los busca en el .md
"""
from pathlib import Path
import importlib.util, re, shutil, sqlite3, sys, tempfile

sys.stdout.reconfigure(encoding="utf-8")
sys.dont_write_bytecode = True          # no dejar __pycache__ en sql/
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
SQL = RAMO / "sql"
MD = RAMO / "unidades" / "12-transacciones-e-indices.md"


def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x, 0)


def modulo(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


P = modulo("u12_programa", SQL / "u12_programa.py")


# ---------------------------------------------------------------- bloques de un script SQL
def bloques(ruta):
    out, actual = [], None
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^-- @(\w+) (\w+)\s*$", linea)
        if m:
            actual = [m.group(1), m.group(2), []]
            out.append(actual)
        elif actual is not None and not linea.startswith("-- ====="):
            actual[2].append(linea)
    return [(t, n, "\n".join(l).strip()) for t, n, l in out]


def arbol(filas):
    """El plan de EXPLAIN QUERY PLAN dibujado como lo dibuja la consola sqlite3."""
    hijos = {}
    for id_, padre, _, detalle in filas:
        hijos.setdefault(padre, []).append((id_, detalle))
    lineas = ["QUERY PLAN"]

    def bajar(padre, sangria):
        nodos = hijos.get(padre, [])
        for k, (id_, detalle) in enumerate(nodos):
            ultimo = k == len(nodos) - 1
            lineas.append(sangria + ("`--" if ultimo else "|--") + detalle)
            bajar(id_, sangria + ("   " if ultimo else "|  "))
    bajar(0, "")
    return "\n".join(lineas)


def ejecutar(con, ruta, ganchos=None):
    R = {}
    for tipo, nombre, sql in bloques(ruta):
        if tipo in ("crear", "datos"):
            con.executescript(sql)
            R[nombre] = {"tipo": tipo, "sql": sql}
        elif tipo == "ejecuta":
            con.execute(sql)
            R[nombre] = {"tipo": tipo, "sql": sql}
        elif tipo == "consulta":
            cur = con.execute(sql)
            R[nombre] = {"tipo": tipo, "sql": sql, "cols": [d[0] for d in cur.description], "filas": cur.fetchall()}
        elif tipo == "plan":
            R[nombre] = {"tipo": tipo, "sql": sql, "plan": arbol(con.execute(sql).fetchall())}
        elif tipo == "falla":
            try:
                con.execute(sql)
            except sqlite3.Error as e:
                R[nombre] = {"tipo": tipo, "sql": sql, "error": str(e)}
            else:
                raise AssertionError(f"{nombre}: tenía que fallar y no falló")
        elif tipo == "python":
            R[nombre] = {"tipo": tipo, "sql": "", "salida": ganchos[nombre]()}
        else:
            raise ValueError(tipo)
    return R


def celda(v):
    return "NULL" if v is None else str(v)


def tabla_md(r):
    lineas = ["| " + " | ".join(r["cols"]) + " |", "|" + "---|" * len(r["cols"])]
    lineas += ["| " + " | ".join(celda(v) for v in f) + " |" for f in r["filas"]]
    return "\n".join(lineas)


def filas(R, k):
    return R[k]["filas"]


# ---------------------------------------------------------------- la ferretería
def ferreteria_nueva(ruta):
    """Solo las tablas y los datos (los bloques crear y datos), para probar las funciones."""
    con = sqlite3.connect(ruta)
    for tipo, _, sql in bloques(SQL / "u12_transacciones.sql"):
        if tipo in ("crear", "datos"):
            con.executescript(sql)
    con.commit(); con.close()


def demos_python(tmp):
    D = {}
    base = tmp / "ferreteria0.db"
    ferreteria_nueva(base)

    def copia(n):
        r = tmp / f"f_{n}.db"; shutil.copy(base, r); return r

    con = P.abrir(copia("stock"))
    D["stock_bajo"] = P.stock_bajo(con, 30)
    con.close()
    # vender: una que pasa, una que falla por stock, una con un producto que no existe
    r = copia("vender"); con = P.abrir(r)
    P.vender(con, 6, "2026-10-09", "Tomás", [(2, 2), (3, 5)])
    D["vender_ok"] = con.execute("SELECT id_producto, stock FROM producto WHERE id_producto IN (2, 3)").fetchall()
    try:
        P.vender(con, 7, "2026-10-09", "Rosa", [(6, 3), (5, 10)])
    except sqlite3.IntegrityError as e:
        D["vender_falla"] = f"{type(e).__name__}: {e}"
    D["vender_falla_queda"] = con.execute(
        "SELECT (SELECT COUNT(*) FROM venta WHERE id_venta = 7), (SELECT stock FROM producto WHERE id_producto = 6)").fetchall()
    try:
        P.vender(con, 7, "2026-10-09", "Rosa", [(6, 3), (9, 1)])
    except ValueError as e:
        D["vender_no_existe"] = f"{type(e).__name__}: {e}"
    D["vender_no_existe_queda"] = con.execute(
        "SELECT (SELECT COUNT(*) FROM venta WHERE id_venta = 7), (SELECT stock FROM producto WHERE id_producto = 6)").fetchall()
    con.close()
    # concurrencia
    D["dos_cajas"] = P.dos_cajas(copia("cajas"))
    D["leer_y_escribir"] = P.leer_y_escribir(copia("lee"), 5, 5)
    D["descontar"] = P.descontar_en_la_base(copia("desc"), 5, 5)
    D["leer_y_escribir_guantes"] = P.leer_y_escribir(copia("lee2"), 6, 20)
    D["descontar_guantes"] = P.descontar_en_la_base(copia("desc2"), 6, 20)
    # inyección, sobre una copia de juguete
    con = P.abrir(copia("juguete"))
    D["buscar_normal"] = P.buscar_inseguro(con, "Cinta aisladora")
    D["buscar_ataque"] = P.buscar_inseguro(con, "x' OR '1'='1")
    D["buscar_param"] = P.buscar(con, "x' OR '1'='1")
    try:
        P.buscar_inseguro(con, "x'; DROP TABLE producto; --")
    except sqlite3.Error as e:
        D["buscar_dos"] = f"{type(e).__name__}: {e}"
    D["anular_param"] = P.anular_venta(con, "3 OR 1=1")
    D["anular_ataque"] = P.anular_venta_inseguro(con, "3 OR 1=1")
    D["anular_queda"] = con.execute("SELECT COUNT(*) FROM detalle_venta").fetchall()
    con.close()
    # transferencias
    r = copia("cuentas"); con = P.abrir(r)
    P.crear_cuentas(con)
    tot = "SELECT SUM(saldo) FROM cuenta"
    D["cuentas_inicio"] = con.execute("SELECT * FROM cuenta").fetchall()
    D["total_inicio"] = con.execute(tot).fetchall()
    try:
        P.transferir(con, 2, 1, 50000)
    except sqlite3.IntegrityError as e:
        D["transferir_falla"] = f"{type(e).__name__}: {e}"
    D["cuentas_falla"] = con.execute("SELECT * FROM cuenta").fetchall()
    P.transferir(con, 3, 2, 30000)
    D["cuentas_ok"] = con.execute("SELECT * FROM cuenta").fetchall()
    D["total_ok"] = con.execute(tot).fetchall()
    con.close()
    try:
        P.transferir_sin_transaccion(r, 2, 1, 80000)
    except sqlite3.IntegrityError as e:
        D["sin_tx_falla"] = f"{type(e).__name__}: {e}"
    con = P.abrir(r)
    D["cuentas_sin_tx"] = con.execute("SELECT * FROM cuenta").fetchall()
    D["total_sin_tx"] = con.execute(tot).fetchall()
    con.close()
    return D


# ---------------------------------------------------------------- el caso
def copia_del_caso(carpeta):
    m = modulo("caso", AQUI / "caso_estampa_sur_bd.py")
    m.DB = carpeta / "estampa_sur.db"
    m.SQL_ESQUEMA = carpeta / "esquema.sql"
    C = m.calcular()
    return m, C, m.DB


def resultados():
    tmp = Path(tempfile.mkdtemp(prefix="u12_"))
    try:
        con = sqlite3.connect(tmp / "ferreteria.db", isolation_level=None)
        E = ejecutar(con, SQL / "u12_transacciones.sql")
        con.close()
        D = demos_python(tmp)
        m, C, ruta = copia_del_caso(tmp)
        juguete = tmp / "juguete_caso.db"
        shutil.copy(ruta, juguete)
        crudo0 = leer_crudo(ruta)
        S = {}

        def registrar_falla():
            c = P.abrir(ruta)
            try:
                P.registrar_pedido(c, 28, "2026-04-03", [(4, 3), (5, 0)])
            except sqlite3.IntegrityError as e:
                S["falla"] = f"{type(e).__name__}: {e}"
            S["falla_queda"] = c.execute("SELECT COUNT(*) FROM pedido").fetchall()
            c.close()
            return S["falla"]

        def registrar_ok():
            c = P.abrir(ruta)
            S["ok"] = P.registrar_pedido(c, 28, "2026-04-03", [(4, 3), (5, 1)])
            c.close()
            return S["ok"]

        con = sqlite3.connect(ruta, isolation_level=None)
        K = ejecutar(con, SQL / "u12_caso.sql", {"registrar_falla": registrar_falla, "registrar_ok": registrar_ok})
        con.close()
        crudo1 = leer_crudo(ruta)
        con = P.abrir(juguete)
        J = {"ataque": P.marcar_entregado_inseguro(con, "5 OR 1=1"),
             "estados": con.execute("SELECT estado, COUNT(*) FROM pedido GROUP BY estado").fetchall()}
        con.close()
        shutil.copy(ruta, juguete)
        con = P.abrir(juguete)
        J["param"] = P.marcar_entregado(con, "5 OR 1=1")
        J["normal"] = P.marcar_entregado(con, "5")
        con.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    segundo_camino(E, D, K, S, crudo0, crudo1)
    return E, D, K, S, J, m, C, crudo0, crudo1


def leer_crudo(ruta):
    con = sqlite3.connect(ruta)
    t = {n: con.execute(f"SELECT * FROM {n}").fetchall() for n in
         ["tienda", "producto", "cliente", "pedido", "detalle_pedido"]}
    con.close()
    return t


def ventas_por_tienda(cr):
    tienda_cli = {c[0]: c[3] for c in cr["cliente"]}
    nombre_t = {t[0]: t[1] for t in cr["tienda"]}
    pedido_cli = {p[0]: p[1] for p in cr["pedido"]}
    v = {}
    for idp, _, q, pu in cr["detalle_pedido"]:
        t = nombre_t[tienda_cli[pedido_cli[idp]]]
        v[t] = v.get(t, 0) + q * pu
    return v


def segundo_camino(E, D, K, S, crudo0, crudo1):
    stock = {p[0]: p[3] for p in filas(E, "d_producto")}
    precio = {p[0]: p[2] for p in filas(E, "d_producto")}
    # venta 6 confirmada, venta 7 deshecha
    assert filas(E, "v6_stock") == [(2, "Martillo carpintero 16 oz", stock[2] - 2), (3, "Cinta aisladora", stock[3] - 5)]
    assert stock[5] - 10 < 0                                                     # por eso falla la silicona
    assert filas(E, "v7_adentro") == [(7, 5, 10, stock[5]), (7, 6, 3, stock[6] - 3)]  # media venta adentro
    assert filas(E, "v7_despues") == [(0, stock[6], stock[5])]
    vendidas_5 = sum(d[2] for d in filas(E, "d_detalle") if d[1] == 5)
    assert filas(E, "i_resultado") == [(vendidas_5,)]
    lineas_tras_v6 = len(filas(E, "d_detalle")) + 2
    assert filas(E, "p2_adentro") == [(lineas_tras_v6 - 2, precio[1] + 100)]
    assert filas(E, "p2_despues") == [(lineas_tras_v6, precio[1])]
    assert filas(E, "p5_queda") == [(5, 10, stock[5]), (6, 3, stock[6] - 3)]       # COMMIT tras el error
    # Python sobre la ferretería
    assert D["stock_bajo"] == sorted([(n, s) for _, n, _, s in filas(E, "d_producto") if s < 30], key=lambda x: x[1])
    assert D["vender_ok"] == [(2, stock[2] - 2), (3, stock[3] - 5)]
    assert D["vender_falla_queda"] == [(0, stock[6])] == D["vender_no_existe_queda"]
    assert D["leer_y_escribir"] == (stock[5], 10, stock[5] - 5)                  # se vendieron 10 de 8
    assert D["descontar"] == ([1, 0], stock[5] - 5)
    assert D["leer_y_escribir_guantes"] == (stock[6], 40, stock[6] - 20)
    assert D["descontar_guantes"] == ([1, 0], stock[6] - 20)
    assert [v for _, v in D["dos_cajas"]][:2] == [stock[2] - 1, stock[2]] and D["dos_cajas"][-1][1] == stock[2] - 1
    assert len(D["buscar_ataque"]) == len(stock) and D["buscar_param"] == []
    n_lineas = len(filas(E, "d_detalle"))
    assert D["anular_param"] == 0 and D["anular_ataque"] == n_lineas and D["anular_queda"] == [(0,)]
    ini = sum(s for _, _, s in D["cuentas_inicio"])
    assert D["total_inicio"] == [(ini,)] == D["total_ok"] and D["cuentas_falla"] == D["cuentas_inicio"]
    assert D["total_sin_tx"] == [(ini + 80000,)]                                   # aparece plata de la nada
    # el caso
    v0, v1 = ventas_por_tienda(crudo0), ventas_por_tienda(crudo1)
    prec = {p[0]: p[2] for p in crudo0["producto"]}
    m121 = 4 * prec[1] + 2 * prec[2]
    m122 = 3 * prec[4] + 1 * prec[5]
    assert sum(f[4] for f in filas(K, "c121_detalle")) == m121
    assert dict(filas(K, "c121_ventas"))["Lagos"] == v0["Lagos"] + m121
    assert v1["Lagos"] == v0["Lagos"] + m121 and v1["Valle"] == v0["Valle"] + m122
    assert all(v1[t] == v0[t] for t in v0 if t not in ("Lagos", "Valle"))
    assert filas(K, "c122_adentro") == [(1, 1)] and filas(K, "c122_despues") == [(121, len(crudo0["detalle_pedido"]) + 2, 0)]
    assert S["falla_queda"] == [(121,)] and S["ok"] == 122
    assert len(crudo1["pedido"]) == 122 and len(crudo1["detalle_pedido"]) == len(crudo0["detalle_pedido"]) + 4
    assert filas(K, "c_final") == [(122, len(crudo1["detalle_pedido"]), 2)]
    assert dict(filas(K, "c_final_ventas")) == v1
    assert filas(K, "c_centro") == [("Centro", v0["Centro"])]
    assert K["c_plan_todas"]["plan"] == K["c_plan_todas_despues"]["plan"]           # el índice no cambia nada
    assert K["c_plan_centro_antes"]["plan"] == K["c_plan_centro_uno"]["plan"] != K["c_plan_centro_despues"]["plan"]
    assert E["i_antes"]["plan"] != E["i_despues"]["plan"]


def normal(sql):
    return " ".join(sql.split()).rstrip(";")


def cadena(K, S, m, C, crudo0, crudo1):
    ok = True
    ok &= len(crudo0["pedido"]) == C["tablas"]["pedido"] and len(crudo0["detalle_pedido"]) == C["tablas"]["detalle_pedido"]
    v0 = ventas_por_tienda(crudo0)
    ok &= sorted(v0.items(), key=lambda kv: -kv[1]) == [tuple(f) for f in C["u10_ventas_por_tienda"]]
    ok &= C["u10_clientes_sin_pedidos"][0][0] == 4 and filas(K, "c_final")[0][2] == 2
    caso_v = dict(tuple(f) for f in C["u10_ventas_por_tienda"])
    ok &= all(v == caso_v[t] for t, v in filas(K, "c121_ventas") if t != "Lagos")
    print("CADENA:", f"OK, la base parte de los {C['tablas']['pedido']} pedidos y las ventas por tienda del caso; "
          f"queda con {filas(K, 'c_final')[0][0]} pedidos y las ventas de Lagos y Valle suben justo lo registrado"
          if ok else "NO calza")
    return ok


# ---------------------------------------------------------------- lo que el .md tiene que mostrar
def esperados(E, D, K, S, J, crudo0, crudo1):
    s = []
    for R in (E, K):
        for nombre, r in R.items():
            if r["tipo"] == "datos":
                continue
            s += [("linea", l.strip()) for l in r["sql"].splitlines() if l.strip() and not l.strip().startswith("-- ")]
            if r["tipo"] == "consulta":
                s.append(("texto", tabla_md(r)))
            elif r["tipo"] == "plan":
                s.append(("texto", r["plan"]))
            elif r["tipo"] == "falla":
                s.append(("texto", r["error"]))
            elif r["tipo"] == "python":
                s.append(("texto", r["salida"] if isinstance(r["salida"], str) else repr(r["salida"])))
    # el código de Python, línea por línea (sin el docstring del módulo)
    codigo = (SQL / "u12_programa.py").read_text(encoding="utf-8").split('"""', 2)[2]
    s += [("linea", l.strip()) for l in codigo.splitlines() if l.strip()]
    # las salidas de las funciones
    for k, v in D.items():
        if k == "dos_cajas":
            continue
        s.append(("texto", v if isinstance(v, str) else repr(v)))
    for k, v in D["dos_cajas"]:
        s.append(("texto", f"{k}: {v}"))
    s += [("texto", repr(J["ataque"])), ("texto", repr(J["param"])), ("texto", repr(J["normal"])),
          ("texto", repr(sorted(J["estados"])))]
    # cifras con formato chileno
    prec = {p[0]: p[2] for p in crudo0["producto"]}
    v0, v1 = ventas_por_tienda(crudo0), ventas_por_tienda(crudo1)
    s += [("texto", x) for x in [pesos(4 * prec[1] + 2 * prec[2]), pesos(3 * prec[4] + prec[5]),
                                  pesos(v1["Lagos"]), pesos(v1["Valle"]), pesos(v0["Lagos"]), pesos(v0["Valle"]),
                                  pesos(filas(K, "p10_ventas")[0][0])]]
    return s


if __name__ == "__main__":
    E, D, K, S, J, m, C, crudo0, crudo1 = resultados()
    for titulo, R in (("FERRETERÍA", E), ("CASO", K)):
        print(f"===== {titulo}")
        for n, r in R.items():
            if r["tipo"] == "consulta":
                print(f"-- {n}: {r['filas']}")
            elif r["tipo"] == "plan":
                print(f"-- {n}:\n{r['plan']}")
            elif r["tipo"] == "falla":
                print(f"-- {n}: ERROR {r['error']}")
            elif r["tipo"] == "python":
                print(f"-- {n}: {r['salida']!r}")
    print("===== PYTHON")
    for k, v in D.items():
        print(f"-- {k}: {v!r}")
    print(f"-- juguete del caso: {J}")
    print("SEGUNDO CAMINO: OK, stock, montos, conteos e invariantes calzan con Python puro")
    if not cadena(K, S, m, C, crudo0, crudo1):
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        lineas = set(l.strip() for l in md.splitlines())
        faltan = []
        for clase, x in esperados(E, D, K, S, J, crudo0, crudo1):
            if clase == "linea" and x not in lineas:
                faltan.append(f"línea: {x}")
            elif clase == "texto" and x not in md_n:
                faltan.append(f"texto: {x}")
        print("REVISIÓN:", "OK, todo el SQL, el Python, las tablas, los planes, los errores y las salidas están en el texto"
              if not faltan else f"faltan {len(faltan)}:\n  " + "\n  ".join(faltan))
        sys.exit(1 if faltan else 0)
