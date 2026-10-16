"""Unidad 8 · SQL para crear y modificar (DDL y DML). Recalcula todo; con --revisar lo busca en el .md.

El script:

1. corre bloque por bloque sql/u08_liga.sql (ejemplo) y sql/u08_ejercicios.sql (pautas) en bases en
   memoria; los bloques cuya clave contiene «falla» TIENEN que fallar, y se guarda el mensaje real;
2. recalcula en Python lo que esos bloques dejan (claves generadas, precios redondeados, filas
   borradas en cascada) y lo compara con lo que devuelve SQLite;
3. arma en memoria una copia de la base del caso (sin tocar datos/estampa_sur.db), corre
   sql/u08_caso.sql y compara con el script del caso (CADENA);
4. comprueba que datos/esquema.sql sea el esquema del script del caso y que sql/u08_esquema_mysql.sql
   tenga las mismas columnas, claves primarias y claves foráneas;
5. con --revisar, busca en el .md cada bloque SQL, cada fila de cada resultado, cada mensaje de error,
   cada línea de datos/esquema.sql y las cifras del texto.

    python u08_ddl_dml.py            # imprime los resultados
    python u08_ddl_dml.py --tablas   # imprime cada bloque con su resultado en Markdown
    python u08_ddl_dml.py --revisar  # además los busca en el .md
"""
from pathlib import Path
import importlib.util, json, math, re, sqlite3, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
SQL = RAMO / "sql"
MD = RAMO / "unidades" / "08-sql-ddl-y-dml.md"


def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x)


def celda(v):
    return "NULL" if v is None else str(v)


def fila_md(f):
    return "| " + " | ".join(celda(v) for v in f) + " |"


def tabla(cols, filas):
    return "\n".join(["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + [fila_md(f) for f in filas])


def plano(s):
    return " ".join(s.split())


# ---------------------------------------------------------------- correr scripts por bloques
def bloques(ruta):
    texto = ruta.read_text(encoding="utf-8")
    partes = re.split(r"^-- @(\w+)\s*$", texto, flags=re.M)
    return [(k, q.strip()) for k, q in zip(partes[1::2], partes[2::2])]


def sentencias(sql):
    """Parte un bloque en instrucciones completas (sqlite3.complete_statement)."""
    out, actual = [], ""
    for linea in sql.splitlines(keepends=True):
        if linea.lstrip().startswith("--") and not actual.strip():
            continue
        actual += linea
        if sqlite3.complete_statement(actual):
            out.append(actual.strip())
            actual = ""
    assert not actual.strip(), f"instrucción incompleta: {actual}"
    return out


def nueva():
    return sqlite3.connect(":memory:", isolation_level=None)   # autocommit: BEGIN y ROLLBACK a mano


BLOQUES = []   # (archivo, clave, resultado) en orden, para --tablas y --revisar


def correr_script(ruta, con=None):
    out = {}
    con = con or nueva()
    for clave, sql in bloques(ruta):
        if clave.startswith("base_"):
            con = nueva()
        r = {"sql": sql, "error": None, "cols": None, "filas": None}
        try:
            for st in sentencias(sql):
                cur = con.execute(st)
                if cur.description:
                    r["cols"] = [d[0] for d in cur.description]
                    r["filas"] = cur.fetchall()
        except sqlite3.Error as e:
            r["error"] = str(e)
        debe_fallar = "falla" in clave
        assert (r["error"] is not None) == debe_fallar, f"{ruta.name} · {clave}: error = {r['error']}"
        out[clave] = r
        BLOQUES.append((ruta.name, clave, r))
    return out, con


def cargar_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_bd.py")
    caso = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caso)
    return caso


def base_del_caso(caso):
    """Copia en memoria de la base del caso, con los mismos datos y el mismo esquema."""
    con = nueva()
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(caso.ESQUEMA)
    clientes, pedidos, detalle, ordenes = caso.generar()
    con.execute("BEGIN")
    con.executemany("INSERT INTO tienda VALUES (?,?,?)", caso.TIENDAS)
    con.executemany("INSERT INTO producto VALUES (?,?,?,?,?)", caso.PRODUCTOS)
    con.executemany("INSERT INTO proveedor VALUES (?,?,?)", caso.PROVEEDORES)
    con.executemany("INSERT INTO suministra VALUES (?,?,?)", caso.SUMINISTRA)
    con.executemany("INSERT INTO cliente VALUES (?,?,?,?)", clientes)
    con.executemany("INSERT INTO pedido VALUES (?,?,?,?)", pedidos)
    con.executemany("INSERT INTO detalle_pedido VALUES (?,?,?,?)", detalle)
    con.executemany("INSERT INTO orden_produccion VALUES (?,?,?,?)", ordenes)
    con.execute("COMMIT")
    return con


def estructura(con):
    """Columnas (nombre, tipo, not null, pk) y claves foráneas de cada tabla."""
    E = {}
    for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        cols = [(c[1], c[3], c[5]) for c in con.execute(f"PRAGMA table_info({t})")]
        fks = sorted((f[3], f[2], f[4]) for f in con.execute(f"PRAGMA foreign_key_list({t})"))
        E[t] = (cols, fks)
    return E


def redondeo_10(x):
    return int(math.floor(x / 10 + 0.5)) * 10


# ---------------------------------------------------------------- resultados
def resultados():
    R = {}
    L, _ = correr_script(SQL / "u08_liga.sql")
    eq = L["equipos"]["filas"]
    assert (5, "Escuela Industrial", "Los Ángeles") in eq            # clave generada = máximo + 1; DEFAULT
    R["liga"] = {"jugadores": L["jugadores"]["filas"][0][0], "id_escuela": 5,
                 "cambios_resultado": L["resultado"]["filas"][0][0], "cambios_retiro": L["retiro"]["filas"][0][0],
                 "final": len(L["final"]["filas"])}

    E, _ = correr_script(SQL / "u08_ejercicios.sql")
    # 8.2: SQLite no corta el VARCHAR
    assert E["base_e2"]["filas"] == [("Concepción", 10)]
    # 8.3: DEFAULT solo cuando la columna se omite
    soc = {f[1]: f for f in E["base_e3"]["filas"]}
    assert soc["Raúl Espinoza"][2:] == ("adulto", 14500, 1) and soc["Gloria Pinto"][3] is None
    # 8.6: redondeo a la decena
    base6 = {1: 1490, 2: 1190, 5: 2190}
    nuevos = {k: redondeo_10(v * 1.08) for k, v in base6.items()}
    res6 = {f[0]: f[3] for f in E["e6_resultado"]["filas"]}
    assert all(res6[k] == v for k, v in nuevos.items())
    assert E["e6_update"]["filas"][0][0] == 3 and E["e6_typeof"]["filas"] == [("integer",)]
    R["e6"] = {"cambios": 3, "nuevos": nuevos, "sin_where": len(res6)}
    # 8.7: tres acciones al borrar el club 2
    cas = E["base_e7_cascade"]["filas"]
    sn = E["base_e7_set_null"]["filas"]
    assert len(cas) == 2 and len(sn) == 5 and sum(1 for f in sn if f[2] is None) == 3
    R["e7"] = {"cascade_quedan": len(cas), "set_null_nulos": 3}
    # 8.8: reutiliza o no el número
    assert [f[0] for f in E["base_e8_rowid"]["filas"]] == [1, 2, 3]
    assert [f[0] for f in E["base_e8_autoinc"]["filas"]] == [1, 2, 4]
    # 8.9: la fecha con barras no es fecha para SQLite
    assert ("2", "05/11/2026") == (str(E["e9_fecha"]["filas"][1][0]), E["e9_fecha"]["filas"][1][1])
    assert E["e9_fecha"]["filas"][1][2] is None and E["e9_fecha"]["filas"][0][2] == "2026-11-05"
    # 8.10
    assert E["e10_error"]["filas"][0][0] == 6 and E["e10_guardia"]["filas"][0][0] == 6
    esperado10 = {1: 1610, 2: 1290, 3: 2490, 4: 450, 5: 2370, 6: 650}
    assert {f[0]: f[3] for f in E["e10_restaurar"]["filas"]} == esperado10
    assert E["e10_rollback"]["filas"] == [(1610,)]

    # ======================= sección 8: SQL armado pegando texto contra parámetros
    def socios():
        c = nueva()
        c.executescript(E["base_e3"]["sql"].rsplit("SELECT", 1)[0])
        return c
    nombre = "x' OR '1'='1"
    c = socios()
    c.execute(f"DELETE FROM socio WHERE nombre = '{nombre}'")
    pegado = c.execute("SELECT changes()").fetchone()[0]
    c = socios()
    c.execute("DELETE FROM socio WHERE nombre = ?", (nombre,))
    param = c.execute("SELECT changes()").fetchone()[0]
    assert (pegado, param) == (4, 0)
    R["inyeccion"] = {"pegado": pegado, "parametro": param}

    # ======================= caso
    caso = cargar_caso()
    con = base_del_caso(caso)
    antes = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
             for t in ["tienda", "producto", "proveedor", "suministra", "cliente", "pedido", "detalle_pedido",
                       "orden_produccion"]}
    C, con = correr_script(SQL / "u08_caso.sql", con)
    lineas = C["lineas"]["filas"]
    semana = sum(f[2] * f[3] for f in lineas)
    semana_corr = sum(f[2] * (9890 if (f[0], f[1]) == (124, "polerones") else f[3]) for f in lineas)
    R["caso"] = {
        "antes": antes, "pedidos_antes": C["inicio"]["filas"][0][0],
        "pedidos_nuevos": C["semana_pedidos"]["filas"][0][0], "detalle_despues": C["semana_detalle"]["filas"][0][0],
        "lineas_nuevas": len(lineas), "unidades_semana": sum(f[2] for f in lineas),
        "semana_con_error": semana, "semana": C["total_semana"]["filas"][0][0], "diferencia_error": semana - semana_corr,
        "marzo": C["marzo_antes"]["filas"][0][0], "marzo_despues": C["marzo_despues"]["filas"][0][0],
        "sin_where": C["sin_where"]["filas"][0][0], "sin_pedidos": C["sin_pedidos"]["filas"][0][0],
        "precios_finales": C["deshacer"]["filas"], "sin_pragma": C["sin_pragma"]["filas"][0][0],
    }
    assert semana_corr == R["caso"]["semana"]
    assert R["caso"]["marzo"] == R["caso"]["marzo_despues"]
    assert C["correccion"]["filas"][0][0] == 1 and C["lista_precios"]["filas"][0][0] == 1
    assert dict((f[0], f[2]) for f in C["deshacer"]["filas"])[5] == 3390
    assert sum(1 for f in C["deshacer"]["filas"] if f[2] == 3390) == 1          # el ROLLBACK deshizo los otros 4
    con.close()

    # ======================= esquemas
    esquema_sql = (RAMO / "datos" / "esquema.sql").read_text(encoding="utf-8")
    assert esquema_sql == caso.ESQUEMA.strip() + "\n", "datos/esquema.sql no es el esquema del script del caso"
    a = nueva(); a.executescript(caso.ESQUEMA)
    my = (SQL / "u08_esquema_mysql.sql").read_text(encoding="utf-8")
    my_sqlite = my.replace("INT AUTO_INCREMENT PRIMARY KEY", "INTEGER PRIMARY KEY").replace(" ENGINE=InnoDB", "")
    b = nueva(); b.executescript(my_sqlite)
    Ea, Eb = estructura(a), estructura(b)
    # tipos: INT de MySQL y INTEGER de SQLite son la misma afinidad; se comparan nombres, NOT NULL, PK y FK
    norm = lambda E: {t: ([(n, pk) for n, nn, pk in cols], fks) for t, (cols, fks) in E.items()}
    assert norm(Ea) == norm(Eb), "el esquema MySQL no calza con datos/esquema.sql"
    R["esquema"] = {"tablas": len(Ea), "fks": sum(len(f) for _, f in Ea.values()),
                    "lineas": [l for l in esquema_sql.splitlines() if l.strip()]}
    return R


def cadena(R):
    caso = cargar_caso()
    try:
        C = caso.calcular()
    except OSError:      # la base del caso está abierta por otro proceso: se usa el .json del caso
        C = json.loads((AQUI / "caso_estampa_sur_bd.json").read_text(encoding="utf-8"))
    c = R["caso"]
    ok = all([
        c["antes"] == C["tablas"],
        c["pedidos_antes"] == C["tablas"]["pedido"],
        c["detalle_despues"] == C["tablas"]["detalle_pedido"] + c["lineas_nuevas"],
        c["marzo"] == sum(v for _, v in C["u10_ventas_por_tienda"]),
        C["u10_clientes_sin_pedidos"][0][0] - 2 == c["sin_pedidos"],
    ])
    print("CADENA:", "OK, la pieza del caso calza (tablas, ventas de marzo y clientes sin pedidos)" if ok else "NO calza")
    return ok


def esperados(R):
    s = []
    for archivo, clave, r in BLOQUES:
        s.append(("sql", f"{archivo} · {clave}", r["sql"]))
        if r["error"]:
            s.append(("texto", f"{archivo} · {clave}", r["error"]))
        for f in r["filas"] or []:
            s.append(("fila", f"{archivo} · {clave}", fila_md(f)))
    c = R["caso"]
    for x in [pesos(c["semana"]), pesos(c["semana_con_error"]), pesos(c["diferencia_error"]), pesos(c["marzo"]),
              f"{c['unidades_semana']} unidades", f"{c['lineas_nuevas']} líneas", f"{R['esquema']['fks']} claves foráneas",
              f"borra las {R['inyeccion']['pegado']} filas", f"carga sus {sum(c['antes'].values())} filas", f"borra {R['inyeccion']['parametro']} filas"]:
        s.append(("texto", "cifra", x))
    for l in R["esquema"]["lineas"]:
        s.append(("linea", "esquema.sql", l.strip()))
    return s


if __name__ == "__main__":
    R = resultados()
    for k, v in R.items():
        print(f"== {k}: {v}")
    if "--tablas" in sys.argv:
        for archivo, clave, r in BLOQUES:
            print(f"\n--- {archivo} · {clave}\n```sql\n{r['sql']}\n```")
            if r["error"]:
                print(f"\nError: `{r['error']}`")
            if r["cols"]:
                print("\n" + tabla(r["cols"], r["filas"]))
    if not cadena(R):
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        md_plano = plano(md_n)
        lineas = set(l.strip() for l in md_n.splitlines())
        faltan = []
        for tipo, donde, x in esperados(R):
            if tipo == "sql" and plano(x) not in md_plano:
                faltan.append(f"bloque {donde}")
            elif tipo == "texto" and plano(x) not in md_plano:
                faltan.append(f"{donde}: {x}")
            elif tipo in ("fila", "linea") and x not in lineas:
                faltan.append(f"{tipo} {donde}: {x}")
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
