"""Unidad 10 · SQL con varias tablas: joins y agregación. Corre cada consulta; con --revisar las busca en el .md.

Este script:

1. crea en memoria la liga del ejemplo con la parte 1 de sql/u10_joins.sql y ejecuta cada consulta
   marcada «-- @nombre» de ese archivo;
2. corre el script del caso, copia datos/estampa_sur.db a memoria y ejecuta sql/u10_caso.sql;
3. recalcula en Python, desde las filas crudas de cada tabla, cada join, cada grupo y cada HAVING
   (segundo camino), y cruza totales entre consultas (las ventas por tienda suman lo mismo que el
   reporte del 10.10; los pedidos por tipo suman 120);
4. compara las consultas u10_* con las del script del caso (texto y resultado): CADENA;
5. con --revisar, exige que cada consulta, cada tabla de resultado (contigua), cada mensaje de error y
   cada cifra de la lectura estén en el .md.

Usa las funciones de lectura y formato de u09_sql_una_tabla.py (mismo formato de resultados).

    python u10_joins.py            # imprime los resultados
    python u10_joins.py --tablas   # además imprime cada resultado como tabla Markdown
    python u10_joins.py --revisar  # además los busca en el .md
"""
from collections import Counter, defaultdict
from pathlib import Path
import importlib.util, sqlite3, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
SQL_EJEMPLO = RAMO / "sql" / "u10_joins.sql"
SQL_CASO = RAMO / "sql" / "u10_caso.sql"
MD = RAMO / "unidades" / "10-sql-joins-y-agregacion.md"

_spec = importlib.util.spec_from_file_location("u09", AQUI / "u09_sql_una_tabla.py")
u09 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(u09)
leer_sql, correr, tabla_md, base_del_caso, fmt, pesos = (u09.leer_sql, u09.correr, u09.tabla_md,
                                                         u09.base_del_caso, u09.fmt, u09.pesos)


def filas(R, k):
    return R[k]["filas"]


def resultados():
    prep, bloques = leer_sql(SQL_EJEMPLO)
    ej = sqlite3.connect(":memory:")
    ej.executescript(prep)
    R = correr(ej, bloques)
    m, C, cas = base_del_caso()
    _, bloques_caso = leer_sql(SQL_CASO)
    RC = correr(cas, bloques_caso)
    X = segundo_camino(R, RC, ej, cas)
    ej.close(); cas.close()
    return R, RC, C, m, X


def segundo_camino(R, RC, ej, cas):
    """Los mismos joins y grupos hechos a mano en Python, desde las filas crudas."""
    X = {}
    eq = ej.execute("SELECT id_equipo, nombre FROM equipo").fetchall()
    ju = ej.execute("SELECT id_jugador, nombre, puesto, id_equipo FROM jugador").fetchall()
    go = ej.execute("SELECT id_gol, id_jugador, jornada, minuto FROM gol").fetchall()
    nom_eq = dict(eq)
    jug = {j[0]: j for j in ju}
    # producto cartesiano y join
    assert filas(R, "cartesiano_cuenta") == [(len(eq) * len(ju),)] == filas(R, "join_sin_on")
    assert len(filas(R, "cartesiano_muestra")) == 2 * len(eq)
    inner = sorted([(j[1], nom_eq[j[3]]) for j in ju if j[3] in nom_eq], key=lambda r: (r[1], r[0]))
    assert filas(R, "inner") == inner == filas(R, "implicito")
    left = sorted([(e[1], j[1]) for e in eq for j in ju if j[3] == e[0]] +
                  [(e[1], None) for e in eq if not any(j[3] == e[0] for j in ju)],
                  key=lambda r: (r[0], r[1] or ""))
    assert filas(R, "left") == left
    sin_jug = [e[1] for e in eq if not any(j[3] == e[0] for j in ju)]
    sin_eq = [j[1] for j in ju if j[3] is None]
    assert [f[0] for f in filas(R, "anti")] == sin_jug
    assert sorted(f[1] for f in filas(R, "right")) == sorted(j[1] for j in ju if j[2] == "delantero")
    assert sorted(filas(R, "full"), key=str) == sorted(filas(R, "full_mysql"), key=str) == \
        sorted([(e, None) for e in sin_jug] + [(None, j) for j in sin_eq], key=str)
    arq = {j[3]: j[1] for j in ju if j[2] == "arquero"}
    assert filas(R, "left_where") == sorted([(nom_eq[k], v) for k, v in arq.items()])
    assert filas(R, "left_on") == sorted([(e[1], arq.get(e[0])) for e in eq])
    assert len(filas(R, "left_on")) == len(eq) and len(filas(R, "left_where")) == len(eq) - 1
    j3 = sorted([g for g in go if g[2] == 3], key=lambda g: g[3])
    assert filas(R, "tres") == [(g[3], jug[g[1]][1], nom_eq[jug[g[1]][3]]) for g in j3]
    mins = [g[3] for g in go]
    assert filas(R, "agregados") == [(len(go), len({g[1] for g in go}), min(mins), max(mins),
                                      round(sum(mins) / len(mins), 1))]
    assert filas(R, "count_columna") == [(len(ju), sum(j[3] is not None for j in ju),
                                          len({j[3] for j in ju if j[3] is not None}))]
    por_eq = Counter(nom_eq[jug[g[1]][3]] for g in go)
    assert filas(R, "group") == sorted(por_eq.items(), key=lambda kv: (-kv[1], kv[0]))
    por_j = Counter(g[1] for g in go)
    assert filas(R, "group_left") == sorted([(j[1], por_j.get(j[0], 0)) for j in ju], key=lambda r: (-r[1], r[0]))
    assert "misuse of aggregate" in R["where_agregado"]["error"]
    assert filas(R, "having") == sorted([(k, v) for k, v in por_j.items() if v >= 3], key=lambda r: (-r[1], r[0]))
    t2 = Counter(nom_eq[jug[g[1]][3]] for g in go if g[3] > 30)
    assert filas(R, "where_having") == [(k, v) for k, v in t2.items() if v >= 3]
    # ejemplo resuelto
    b3 = Counter(nom_eq[jug[g[1]][3]] for g in go if g[2] == 3)
    assert filas(R, "ej_boletin") == sorted([(e[1], b3.get(e[1], 0)) for e in eq], key=lambda r: (-r[1], r[0]))
    assert filas(R, "ej_boletin_where") == sorted(b3.items(), key=lambda kv: (-kv[1], kv[0]))
    gol2t = Counter(g[1] for g in go if g[3] > 30)
    gl = sorted([(jug[k][1], nom_eq[jug[k][3]], v, gol2t.get(k, 0)) for k, v in por_j.items() if v >= 2],
                key=lambda r: (-r[2], r[0]))
    assert filas(R, "ej_goleadores") == gl
    X["ej_filas_join"] = len(go)                        # FROM + JOIN: una fila por gol
    X["ej_grupos"] = len(por_j)                         # GROUP BY: un grupo por goleador
    X["ej_quedan"] = len(gl)                            # HAVING
    X["sin_gol"] = [j[1] for j in ju if j[0] not in por_j]
    # ejercicios de la liga
    assert filas(R, "e1a") == [(len(ju) * len(go),)] and filas(R, "e1b") == [(len(go),)]
    assert len(filas(R, "e8a")) == len(por_eq)          # un nombre de jugador cualquiera por equipo
    assert all(f[2] == por_eq[f[0]] for f in filas(R, "e8a"))
    assert sorted(filas(R, "e8a_bien")) == sorted((nom_eq[jug[k][3]], jug[k][1], v) for k, v in por_j.items())
    mal = Counter(nom_eq[g[1]] for g in go if g[1] in nom_eq)      # e.id_equipo = j.id_jugador
    assert sorted(filas(R, "e8b")) == sorted(mal.items())
    n_j = Counter(j[3] for j in ju if j[3] is not None)
    assert filas(R, "e8c") == sorted((e[1], max(n_j.get(e[0], 0), 1)) for e in eq)
    assert filas(R, "e8c_bien") == sorted((e[1], n_j.get(e[0], 0)) for e in eq)

    # ---------------- caso
    T = dict(cas.execute("SELECT id_tienda, nombre FROM tienda").fetchall())
    PR = {p[0]: p for p in cas.execute("SELECT id_producto, nombre, precio, costo_var, seg_estampado FROM producto")}
    PV = dict(cas.execute("SELECT id_proveedor, nombre FROM proveedor").fetchall())
    S = cas.execute("SELECT id_proveedor, id_producto, costo_unidad FROM suministra").fetchall()
    CL = {c[0]: c for c in cas.execute("SELECT id_cliente, nombre, tipo, id_tienda FROM cliente")}
    PE = {p[0]: p for p in cas.execute("SELECT id_pedido, id_cliente, fecha, estado FROM pedido")}
    D = cas.execute("SELECT id_pedido, id_producto, cantidad, precio_unit FROM detalle_pedido").fetchall()
    O = cas.execute("SELECT id_producto, semana, lote FROM orden_produccion").fetchall()
    ventas_t = defaultdict(int)
    for d in D:
        ventas_t[T[CL[PE[d[0]][1]][3]]] += d[2] * d[3]
    assert filas(RC, "u10_ventas_por_tienda") == sorted(ventas_t.items(), key=lambda kv: -kv[1])
    uds = Counter()
    for d in D:
        uds[PR[d[1]][1]] += d[2]
    assert filas(RC, "u10_unidades_por_producto") == sorted(uds.items(), key=lambda kv: -kv[1])
    mg, ut = defaultdict(int), Counter()
    for d in D:
        tipo = CL[PE[d[0]][1]][2]
        mg[tipo] += d[2] * (d[3] - PR[d[1]][3]); ut[tipo] += d[2]
    assert filas(RC, "u10_margen_por_tipo_cliente") == sorted([(k, v) for k, v in mg.items() if ut[k] > 100], key=lambda kv: -kv[1])
    assert filas(RC, "caso_unidades_por_tipo") == sorted(ut.items(), key=lambda kv: -kv[1])
    compran = {p[1] for p in PE.values()}
    sin = [c for c in sorted(CL) if c not in compran]
    assert filas(RC, "u10_clientes_sin_pedidos") == [(len(sin),)]
    assert filas(RC, "caso_clientes_sin_pedidos_lista") == [(CL[c][1], CL[c][2], T[CL[c][3]]) for c in sin]
    assert filas(RC, "caso_cartesiano") == [(len(CL) * len(PE),)]
    assert filas(RC, "e1c") == [(len(CL) * len(T),)] and filas(RC, "e1d") == [(len(CL),)]
    assert filas(RC, "e2") == sorted([(PR[s[1]][1], PV[s[0]], s[2]) for s in S], key=lambda r: (
        [k for k in PR if PR[k][1] == r[0]][0], r[2]))
    assert sorted(filas(RC, "e3")) == sorted(Counter(p[3] for p in PE.values()).items())
    n_s = Counter(s[0] for s in S)
    assert filas(RC, "e4") == sorted([(PV[k], n_s.get(k, 0)) for k in PV], key=lambda r: (-r[1], r[0]))
    assert filas(RC, "e4_mal") == sorted([(PV[k], max(n_s.get(k, 0), 1)) for k in PV], key=lambda r: (-r[1], r[0]))
    hs = defaultdict(int)
    for o in O:
        hs[o[1]] += o[2] * PR[o[0]][4]
    assert filas(RC, "e5") == [(s, hs[s] / 3600) for s in sorted(hs)]
    assert dict(filas(RC, "e5"))[6] == 33
    pt = Counter(T[CL[p[1]][3]] for p in PE.values())
    assert filas(RC, "e6") == sorted([(k, v) for k, v in pt.items() if v > 20], key=lambda kv: -kv[1])
    ve = defaultdict(int)
    for d in D:
        if PE[d[0]][3] == "entregado":
            ve[PR[d[1]][1]] += d[2] * d[3]
    assert filas(RC, "e7") == sorted([(k, v) for k, v in ve.items() if v > 3_000_000], key=lambda kv: -kv[1])
    lineas, pedidos = Counter(), defaultdict(set)
    for d in D:
        tipo = CL[PE[d[0]][1]][2]
        lineas[tipo] += 1; pedidos[tipo].add(d[0])
    assert filas(RC, "e9_mal") == [(k, lineas[k], ut[k]) for k in sorted(ut)]
    assert filas(RC, "e9_bien") == [(k, len(pedidos[k]), ut[k], round(ut[k] / len(pedidos[k]), 1)) for k in sorted(ut)]
    assert sum(f[1] for f in filas(RC, "e9_bien")) == len(PE) and sum(f[1] for f in filas(RC, "e9_mal")) == len(D)
    rep = {f[0]: f for f in filas(RC, "e10")}
    for tid, tn in T.items():
        cl = [c for c in CL.values() if c[3] == tid]
        ped = [p for p in PE.values() if CL[p[1]][3] == tid]
        assert rep[tn][1:] == (len(cl), len({p[1] for p in ped}), len(ped), ventas_t[tn])
    assert sum(f[4] for f in filas(RC, "e10")) == sum(ventas_t.values())
    X["ventas_total"] = sum(ventas_t.values())
    X["ticket"] = {tn: ventas_t[tn] / pt[tn] for tn in T.values()}
    try:
        ej.execute("SELECT nombre FROM jugador j JOIN equipo e ON e.id_equipo = j.id_equipo")
        raise AssertionError("tenía que ser ambigua")
    except sqlite3.OperationalError as e:
        assert str(e) == "ambiguous column name: nombre"
        X["ambigua"] = str(e)
    assert ej.execute("SELECT 19 * 3600 / 2 / 3600").fetchone()[0] == 9   # 9,5 h con división entera
    X["lineas"] = len(D)
    return X


def cadena(RC, C, m):
    plano = lambda s: " ".join(s.replace(";", "").split())
    ok = True
    for k in ["u10_ventas_por_tienda", "u10_unidades_por_producto", "u10_margen_por_tipo_cliente",
              "u10_clientes_sin_pedidos"]:
        ok &= plano(RC[k]["sql"]) == plano(m.CONSULTAS[k])
        ok &= [tuple(f) for f in RC[k]["filas"]] == [tuple(f) for f in C[k]]
    print("CADENA:", "OK, las cuatro consultas u10_* son las del caso y dan lo mismo"
          f" ({C['u10_clientes_sin_pedidos'][0][0]} clientes sin pedidos, ventas de Valle"
          f" {pesos(dict(C['u10_ventas_por_tienda'])['Valle'])})" if ok else "NO calza")
    return ok


def esperados(R, RC, X):
    s = []
    s += [f"{X['ej_filas_join']} filas", f"{X['ej_grupos']} grupos", f"quedan {X['ej_quedan']}"]
    s += [", ".join(X["sin_gol"][:-1]) + " y " + X["sin_gol"][-1]]
    v = filas(RC, "u10_ventas_por_tienda")
    s += [pesos(v[0][1]), pesos(v[-1][1]), pesos(X["ventas_total"])]
    s += [fmt(100 * v[0][1] / X["ventas_total"], 1) + " %"]
    mg = filas(RC, "u10_margen_por_tipo_cliente")
    s += [pesos(x[1]) for x in mg]
    s += [f"{filas(RC, 'caso_cartesiano')[0][0]:,}".replace(",", ".") + " filas"]
    e9 = filas(RC, "e9_bien")
    s += [fmt(x[3], 1) for x in e9]
    s += [f"{X['lineas']} líneas"]
    e7 = filas(RC, "e7")
    s += [pesos(x[1]) for x in e7]
    s += [pesos(round(X["ticket"]["Valle"])), pesos(round(X["ticket"]["Centro"])), X["ambigua"]]
    return s


def revisar(R, RC, X):
    md = MD.read_text(encoding="utf-8")
    md_n = md.replace("{,}", ",").replace("{.}", ".")
    faltan = []
    for nombre, r in list(R.items()) + list(RC.items()):
        if r["sql"] not in md:
            faltan.append(f"consulta {nombre}")
        if tabla_md(r) not in md:
            faltan.append(f"resultado {nombre}")
    faltan += [x for x in esperados(R, RC, X) if x not in md_n]
    return faltan


if __name__ == "__main__":
    R, RC, C, m, X = resultados()
    for nombre, r in list(R.items()) + list(RC.items()):
        if "error" in r:
            print(f"== {nombre}: ERROR {r['error']}")
        else:
            print(f"== {nombre}: {len(r['filas'])} filas {r['filas'][:6]}{' …' if len(r['filas']) > 6 else ''}")
    print("== cifras:", X)
    print("SEGUNDO CAMINO: OK, cada join, grupo y HAVING calza con el cálculo en Python y los totales cruzan")
    if not cadena(RC, C, m):
        sys.exit(1)
    if "--tablas" in sys.argv:
        for nombre, r in list(R.items()) + list(RC.items()):
            print(f"\n<!-- {nombre} -->\n```sql\n{r['sql']}\n```\n\n{tabla_md(r)}")
    if "--revisar" in sys.argv:
        faltan = revisar(R, RC, X)
        print("REVISIÓN:", "OK, todas las consultas, resultados y cifras están en el texto" if not faltan
              else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
