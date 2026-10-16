"""Unidad 11 · Subconsultas y vistas. Ejecuta cada consulta de la unidad; con --revisar la busca en el .md.

Los scripts están en ramos/bases-de-datos/sql/:
  u11_subconsultas.sql   base del ejemplo (biblioteca de Tomé) y sus consultas
  u11_caso.sql           consultas sobre una COPIA de la base del caso (Estampa Sur)

Este script:
1. crea la base del ejemplo en una carpeta temporal y ejecuta cada bloque «-- @tipo nombre» en orden;
2. crea una copia de la base del caso en otra carpeta temporal (con el script del caso, sin tocar
   datos/estampa_sur.db) y ejecuta u11_caso.sql sobre ella;
3. recalcula en Python puro (sin SQL) los resultados clave y exige que coincidan con los del motor;
4. compara la pieza del caso con caso_estampa_sur_bd.py (CADENA);
5. con --revisar, exige que cada línea de SQL, cada tabla de resultado completa (encabezado y filas)
   y cada mensaje de error estén en el .md.

    python u11_subconsultas.py            # imprime los resultados
    python u11_subconsultas.py --revisar  # además los busca en el .md
"""
from pathlib import Path
import importlib.util, re, shutil, sqlite3, sys, tempfile

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
SQL = RAMO / "sql"
MD = RAMO / "unidades" / "11-subconsultas-y-vistas.md"


# ---------------------------------------------------------------- formato chileno
def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x, 0)


# ---------------------------------------------------------------- bloques de un script SQL
def bloques(ruta):
    """Devuelve [(tipo, nombre, sql)] según las marcas «-- @tipo nombre»."""
    out, actual = [], None
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^-- @(\w+) (\w+)\s*$", linea)
        if m:
            actual = [m.group(1), m.group(2), []]
            out.append(actual)
        elif actual is not None and not linea.startswith("-- ====="):
            actual[2].append(linea)
    return [(t, n, "\n".join(l).strip()) for t, n, l in out]


def ejecutar(con, ruta):
    """Ejecuta los bloques en orden sobre la conexión. Devuelve {nombre: resultado}."""
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
            R[nombre] = {"tipo": tipo, "sql": sql, "cols": [d[0] for d in cur.description],
                         "filas": cur.fetchall()}
        elif tipo == "falla":
            try:
                con.execute(sql)
            except sqlite3.Error as e:
                R[nombre] = {"tipo": tipo, "sql": sql, "error": str(e)}
            else:
                raise AssertionError(f"{nombre}: tenía que fallar y no falló")
        else:
            raise ValueError(f"tipo de bloque desconocido: {tipo}")
    return R


def celda(v):
    return "NULL" if v is None else str(v)


def tabla_md(r):
    """La tabla del resultado tal como la escribe la unidad (valores crudos del motor)."""
    lineas = ["| " + " | ".join(r["cols"]) + " |", "|" + "---|" * len(r["cols"])]
    lineas += ["| " + " | ".join(celda(v) for v in fila) + " |" for fila in r["filas"]]
    return "\n".join(lineas)


# ---------------------------------------------------------------- el caso, en una copia
def caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_bd.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def copia_del_caso(carpeta):
    """Crea la base del caso en `carpeta` con el mismo script (misma semilla): datos/ no se toca."""
    m = caso()
    m.DB = carpeta / "estampa_sur.db"
    m.SQL_ESQUEMA = carpeta / "esquema.sql"
    C = m.calcular()
    return m, C, m.DB


# ---------------------------------------------------------------- todo
def resultados():
    tmp = Path(tempfile.mkdtemp(prefix="u11_"))
    try:
        con = sqlite3.connect(tmp / "biblioteca.db", isolation_level=None)
        E = ejecutar(con, SQL / "u11_subconsultas.sql")
        con.close()
        m, C, ruta = copia_del_caso(tmp)
        con = sqlite3.connect(ruta, isolation_level=None)
        K = ejecutar(con, SQL / "u11_caso.sql")
        crudo = {t: con.execute(f"SELECT * FROM {t}").fetchall()
                 for t in ["producto", "suministra", "proveedor", "pedido", "detalle_pedido", "cliente",
                           "orden_produccion", "tienda"]}
        con.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    segundo_camino(E, K, crudo)
    return E, K, m, C


def filas(R, k):
    return R[k]["filas"]


def segundo_camino(E, K, crudo):
    """Recalcula en Python puro lo principal y lo compara con lo que devolvió el motor."""
    # base del ejemplo, desde las mismas tuplas que carga el script
    socio = filas(E, "d_socio"); libro = filas(E, "d_libro"); prest = filas(E, "d_prestamo")
    dias = [p[4] for p in prest if p[4] is not None]
    prom = sum(dias) / len(dias)
    assert filas(E, "s2_promedio") == [(prom,)]
    assert [p[0] for p in filas(E, "s2_sobre")] == [p[0] for p in sorted((p for p in prest if p[4] is not None and p[4] > prom), key=lambda p: -p[4])]
    genero = {l[0]: l[3] for l in libro}
    poesia = {p[1] for p in prest if genero[p[2]] == "poesía"}
    novela = {p[1] for p in prest if genero[p[2]] == "novela"}
    nombre = {s[0]: s[1] for s in socio}
    assert [f[0] for f in filas(E, "s3_in")] == sorted(nombre[i] for i in poesia)
    assert [f[0] for f in filas(E, "s3_not_in")] == sorted(nombre[i] for i in nombre if i not in {p[1] for p in prest})
    invitadores = {s[3] for s in socio if s[3] is not None}
    no_invitan = sorted(nombre[i] for i in nombre if i not in invitadores)
    assert filas(E, "s3_trampa") == []                                   # la trampa del NULL
    assert [f[0] for f in filas(E, "s3_arreglo")] == no_invitan
    assert [f[0] for f in filas(E, "s5_no_invitan")] == no_invitan       # NOT EXISTS da lo mismo
    conteo = {i: sum(1 for p in prest if p[1] == i) for i in nombre}
    assert [f[1] for f in filas(E, "s4_conteo")] == [conteo[i] for i in sorted(nombre)]
    activos = {i: n for i, n in conteo.items() if n > 0}
    prom_n = sum(activos.values()) / len(activos)
    assert filas(E, "s6_promedio") == [(prom_n,)]
    sobre = sorted(i for i, n in activos.items() if n > prom_n)
    assert [f[0] for f in filas(E, "s6_derivada")] == sobre
    assert [f[0] for f in filas(E, "s7_cte")] == sorted(nombre[i] for i in sobre)   # WITH = tabla derivada
    assert [f[0] for f in filas(E, "s8_intersect")] == sorted(novela & poesia)
    assert [f[0] for f in filas(E, "s8_except")] == sorted(novela - poesia)
    assert [f[0] for f in filas(E, "s8_union")] == sorted(novela | poesia)
    n_union_all = sum(1 for p in prest if genero[p[2]] in ("novela", "poesía"))
    assert filas(E, "s8_union_all") == [(n_union_all,)]
    assert filas(E, "s9_viva") == [(len(prest) + 1,)] and filas(E, "s9_despues") == [(len(prest),)]
    assert filas(E, "e_lector") == filas(E, "e_cte")                     # vista = CTE
    for comuna, nom, n in filas(E, "e_lector"):
        assert n == max(conteo[s[0]] for s in socio if s[2] == comuna)
    sin_prestar = [l[1] for l in libro if l[0] not in {p[2] for p in prest}]
    assert [f[0] for f in filas(E, "s5_nunca")] == sin_prestar
    assert filas(E, "p3_igual_null") == []                               # «= NULL» nunca es verdadero
    for id_s, id_p, d in filas(E, "p8_correlacionada"):
        assert d == max(p[4] for p in prest if p[1] == id_s and p[4] is not None)
    # base del caso, desde las tablas crudas de la copia
    precio = {p[0]: p[2] for p in crudo["producto"]}
    prom_precio = sum(precio.values()) / len(precio)
    assert filas(K, "p1_promedio") == [(prom_precio,)]
    total_cli = {}
    pedido_cli = {p[0]: p[1] for p in crudo["pedido"]}
    for idp, idprod, q, pu in crudo["detalle_pedido"]:
        total_cli[pedido_cli[idp]] = total_cli.get(pedido_cli[idp], 0) + q * pu
    prom_cli = sum(total_cli.values()) / len(total_cli)
    n_sobre = sum(1 for v in total_cli.values() if v > prom_cli)
    assert filas(K, "c_sobre_promedio") == [(n_sobre,)] == filas(K, "c_cte")
    assert filas(K, "c_promedio") == [(round(prom_cli, 2), len(total_cli))]
    compran_gorros = {pedido_cli[d[0]] for d in crudo["detalle_pedido"] if d[1] == 5}
    assert filas(K, "p2_in") == [(len(compran_gorros),)]
    assert filas(K, "p2_not_in") == [(len(crudo["cliente"]) - len(compran_gorros),)]
    tot_ped = {}
    for idp, idprod, q, pu in crudo["detalle_pedido"]:
        tot_ped[idp] = tot_ped.get(idp, 0) + q * pu
    prom_ped = sum(tot_ped.values()) / len(tot_ped)
    n_ped = sum(1 for v in tot_ped.values() if v > prom_ped)
    assert filas(K, "p6_cte") == [(n_ped, round(prom_ped, 2))] and filas(K, "p6_having") == [(n_ped,)]
    tipo = {c[0]: c[2] for c in crudo["cliente"]}
    for t, idp, tot in filas(K, "p5_mayor_por_tipo"):
        assert tot == max(v for k, v in tot_ped.items() if tipo[pedido_cli[k]] == t)
    assert [f[0] for f in filas(K, "p7_grandes")] == [f"Cliente {i:02d}" for i, v in sorted(total_cli.items(), key=lambda kv: -kv[1]) if v > 3_000_000]
    assert filas(K, "p7_filas") == [(len(total_cli),)]
    costos = {}
    for prov, prod, c in crudo["suministra"]:
        costos.setdefault(prod, []).append(c)
    lotes6 = {o[1]: o[3] for o in crudo["orden_produccion"] if o[2] == 6}
    barato = sum(q * min(costos[p]) for p, q in lotes6.items())
    caro = sum(q * max(costos[p]) for p, q in lotes6.items())
    assert filas(K, "p10_ahorro") == [(barato, caro)]
    assert sum(f[4] for f in filas(K, "p10_compra")) == barato == sum(f[1] for f in filas(K, "p10_por_proveedor"))
    tienda_cli = {c[0]: c[3] for c in crudo["cliente"]}
    nombre_t = {t[0]: t[1] for t in crudo["tienda"]}
    ventas_t = {}
    for k, v in total_cli.items():
        ventas_t[nombre_t[tienda_cli[k]]] = ventas_t.get(nombre_t[tienda_cli[k]], 0) + v
    prom_t = sum(ventas_t.values()) / len(ventas_t)
    assert [f[0] for f in filas(K, "c_vista_filtra")] == [t for t, v in sorted(ventas_t.items(), key=lambda kv: -kv[1]) if v > prom_t]
    assert filas(K, "c_barato_sin_correlacion") == [f for f in filas(K, "c_barato") if f[2] == min(min(v) for v in costos.values())]


def normal(sql):
    return " ".join(sql.split()).rstrip(";")


def cadena(K, m, C):
    ok = True
    # las tres consultas u11 del script del caso, escritas igual en u11_caso.sql
    for mia, suya in [("c_sobre_promedio", "u11_clientes_sobre_promedio"), ("c_barato", "u11_proveedor_mas_barato"),
                      ("c_semana6", "u11_produccion_semana_6")]:
        ok &= normal(K[mia]["sql"]) == normal(m.CONSULTAS[suya])
        ok &= [tuple(f) for f in filas(K, mia)] == [tuple(f) for f in C[suya]]
    ok &= filas(K, "c_cte") == [tuple(f) for f in C["u11_clientes_sobre_promedio"]]
    ok &= filas(K, "c_semana6_total")[0][1] == 33 == sum(f[2] for f in C["u11_produccion_semana_6"])
    ok &= [tuple(f) for f in filas(K, "c_vista_usa")] == [tuple(f) for f in C["u10_ventas_por_tienda"]]
    print("CADENA:", "OK, las consultas u11 y la vista de ventas por tienda calzan con el caso (12 clientes, "
          "proveedor más barato, 33 h en la semana 6)" if ok else "NO calza")
    return ok


def esperados(E, K):
    s = []
    for R in (E, K):
        for nombre, r in R.items():
            if r["tipo"] == "datos":
                continue
            s += [("sql", l.strip()) for l in r["sql"].splitlines() if l.strip() and not l.strip().startswith("-- ")]
            if r["tipo"] == "consulta":
                s.append(("tabla", tabla_md(r)))
            if r["tipo"] == "falla":
                s.append(("error", r["error"]))
    # cifras que el texto escribe con formato chileno
    prom = filas(K, "c_promedio")[0][0]
    p10 = filas(K, "p10_ahorro")[0]
    s += [("cifra", x) for x in [
        fmt(filas(E, "s2_promedio")[0][0], 2), fmt(filas(E, "s6_promedio")[0][0], 1),
        pesos(prom), pesos(filas(K, "p1_promedio")[0][0]), pesos(p10[0]), pesos(p10[1]), pesos(p10[1] - p10[0]),
        pesos(filas(K, "p6_cte")[0][1]),
        pesos(sum(f[1] for f in filas(K, "c_vista_usa")) / len(filas(K, "c_vista_usa"))),
    ]]
    s += [("cifra", pesos(v)) for _, v in filas(K, "c_vista_usa")]
    s += [("cifra", pesos(v)) for _, v in filas(K, "p10_por_proveedor")]
    return s


if __name__ == "__main__":
    E, K, m, C = resultados()
    for titulo, R in (("EJEMPLO", E), ("CASO", K)):
        print(f"===== {titulo}")
        for nombre, r in R.items():
            if r["tipo"] == "consulta":
                print(f"-- {nombre}: {r['filas']}")
            elif r["tipo"] == "falla":
                print(f"-- {nombre}: ERROR {r['error']}")
    print("SEGUNDO CAMINO: OK, Python puro da lo mismo que el motor en las consultas principales")
    if not cadena(K, m, C):
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        lineas = set(l.strip() for l in md.splitlines())
        faltan = []
        for clase, x in esperados(E, K):
            if clase == "sql" and x not in lineas:
                faltan.append(f"sql: {x}")
            elif clase in ("tabla", "error", "cifra") and x not in md_n:
                faltan.append(f"{clase}: {x}")
        print("REVISIÓN:", "OK, todas las consultas, tablas, errores y cifras están en el texto" if not faltan
              else f"faltan {len(faltan)}:\n  " + "\n  ".join(faltan))
        sys.exit(1 if faltan else 0)
