"""Unidad 9 · SQL para consultar una tabla. Corre cada consulta de la unidad; con --revisar las busca en el .md.

Este script:

1. crea en memoria las tablas del ejemplo (taller) y de los ejercicios (CESFAM) con la parte 1 de
   sql/u09_sql_una_tabla.sql y ejecuta cada consulta marcada «-- @nombre» de ese archivo;
2. corre el script del caso, copia datos/estampa_sur.db a memoria y ejecuta sql/u09_caso.sql;
3. recalcula en Python, desde las filas crudas, lo que cada WHERE, CASE o división debería dar
   (segundo camino) y exige que calce con lo que devolvió SQLite;
4. compara las consultas u9_* con las del script del caso (texto y resultado): CADENA;
5. con --revisar, exige que cada consulta, cada tabla de resultado (fila por fila, contigua), cada
   mensaje de error y cada cifra de la lectura estén en el .md.

    python u09_sql_una_tabla.py            # imprime los resultados
    python u09_sql_una_tabla.py --tablas   # además imprime cada resultado como tabla Markdown
    python u09_sql_una_tabla.py --revisar  # además los busca en el .md
"""
from pathlib import Path
import importlib.util, re, sqlite3, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
SQL_EJEMPLO = RAMO / "sql" / "u09_sql_una_tabla.sql"
SQL_CASO = RAMO / "sql" / "u09_caso.sql"
MD = RAMO / "unidades" / "09-sql-una-tabla.md"


# ---------------------------------------------------------------- formato chileno (para la lectura)
def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x, 0)


# ---------------------------------------------------------------- archivos SQL con marcas
def leer_sql(ruta):
    """Devuelve (preparación, [(nombre, consulta, espera_error)]). Una consulta va desde su marca
    «-- @nombre» hasta la primera línea que termina en «;»."""
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    prep, bloques, actual = [], [], None
    for l in lineas:
        m = re.match(r"^-- @(\w+)( !error)?\s*$", l)
        if m:
            actual = [m.group(1), [], bool(m.group(2))]
            continue
        if actual is None:
            prep.append(l)
        elif l.strip():
            actual[1].append(l.rstrip())
            if l.rstrip().endswith(";"):
                bloques.append((actual[0], "\n".join(actual[1]), actual[2]))
                actual = None
    return "\n".join(prep), bloques


def correr(con, bloques):
    R = {}
    for nombre, q, espera_error in bloques:
        try:
            cur = con.execute(q)
            filas = cur.fetchall()
            assert not espera_error, (nombre, "tenía que fallar")
            R[nombre] = {"sql": q, "cols": [d[0] for d in cur.description], "filas": filas}
        except sqlite3.Error as e:
            assert espera_error, (nombre, str(e))
            R[nombre] = {"sql": q, "error": str(e)}
    return R


def celda(v):
    if v is None:
        return "NULL"
    if isinstance(v, float):
        return repr(v)
    return str(v)


def tabla_md(r):
    """El resultado tal como se muestra en el .md: valores como los entrega SQLite."""
    if "error" in r:
        return f"Error: {r['error']}"
    if not r["filas"]:
        return "La consulta devuelve 0 filas (columnas " + ", ".join(f"`{c}`" for c in r["cols"]) + ")."
    ls = ["| " + " | ".join(r["cols"]) + " |", "|" + "---|" * len(r["cols"])]
    ls += ["| " + " | ".join(celda(v) for v in f) + " |" for f in r["filas"]]
    return "\n".join(ls)


# ---------------------------------------------------------------- inyección SQL (ejercicio 9.10)
INYECCION_MALA = '''sql = "SELECT paciente, edad, profesional FROM hora WHERE paciente = '" + texto + "'"
filas = con.execute(sql).fetchall()'''
INYECCION_BUENA = '''sql = "SELECT paciente, edad, profesional FROM hora WHERE paciente = ?"
filas = con.execute(sql, (texto,)).fetchall()'''
TEXTO_MALICIOSO = "x' OR '1'='1"


def inyeccion(con):
    out = {}
    for etiqueta, codigo in [("mala", INYECCION_MALA), ("buena", INYECCION_BUENA)]:
        for texto in ["Rosa Contreras", TEXTO_MALICIOSO]:
            ambiente = {"con": con, "texto": texto}
            exec(codigo, ambiente)
            out[(etiqueta, texto)] = len(ambiente["filas"])
    return out


# ---------------------------------------------------------------- el caso
def caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_bd.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def base_del_caso():
    """Corre el script del caso (regenera la base) y copia la base a memoria."""
    m = caso()
    C = m.calcular()
    src = sqlite3.connect(f"file:{m.DB.as_posix()}?mode=ro", uri=True)
    con = sqlite3.connect(":memory:")
    src.backup(con); src.close()
    return m, C, con


# ---------------------------------------------------------------- todo junto
def resultados():
    prep, bloques = leer_sql(SQL_EJEMPLO)
    ej = sqlite3.connect(":memory:")
    ej.executescript(prep)
    R = correr(ej, bloques)
    R["_inyeccion"] = inyeccion(ej)
    m, C, cas = base_del_caso()
    _, bloques_caso = leer_sql(SQL_CASO)
    RC = correr(cas, bloques_caso)
    segundo_camino(R, RC, ej, cas, m)
    ej.close(); cas.close()
    return R, RC, C, m


def filas(R, k):
    return R[k]["filas"]


def segundo_camino(R, RC, ej, cas, m):
    """Lo mismo calculado en Python desde las filas crudas."""
    ot = ej.execute("SELECT * FROM orden_trabajo").fetchall()
    # columnas: id_ot, patente, marca, servicio, ingreso, entrega, km, monto, detalle
    assert len(filas(R, "todo")) == 12
    assert filas(R, "proyeccion") == [(r[1], r[3], r[7]) for r in ot if r[3] == "frenos"]
    assert [f[2] for f in filas(R, "alias")] == [round(r[7] * 1.19) for r in ot if r[3] == "frenos"]
    assert [f[0] for f in filas(R, "alias_en_where")] == [r[1] for r in ot if r[7] is not None and r[7] * 1.19 > 140000]
    assert filas(R, "alias_en_where") == filas(R, "alias_en_where_estandar")
    assert [f[0] for f in filas(R, "sin_distinct")] == [r[2] for r in ot if r[6] > 150000]
    assert [f[0] for f in filas(R, "distinct")] == sorted({r[2] for r in ot if r[6] > 150000})
    assert [f[0] for f in filas(R, "between")] == [r[0] for r in ot if "2026-09-07" <= r[4] <= "2026-09-09"]
    assert [f[0] for f in filas(R, "in")] == [r[0] for r in ot if r[3] in ("embrague", "alineación")]
    assert [f[0] for f in filas(R, "like")] == [r[0] for r in ot if "pastillas" in r[8]]
    assert filas(R, "igual_null") == []
    assert [f[0] for f in filas(R, "is_null")] == [r[0] for r in ot if r[5] is None]
    assert all(f[2] is None and f[3] == 0 for f in filas(R, "null_aritmetica"))
    sin = [r[0] for r in ot if r[3] == "frenos" or (r[3] == "embrague" and r[5] is None)]
    con = [r[0] for r in ot if r[3] in ("frenos", "embrague") and r[5] is None]
    assert [f[0] for f in filas(R, "and_or_sin_parentesis")] == sin
    assert [f[0] for f in filas(R, "and_or_con_parentesis")] == con
    orden = sorted([r for r in ot if r[7] is not None], key=lambda r: (r[3], -r[7]))
    assert filas(R, "order_by") == [(r[3], r[1], r[7]) for r in orden]
    por_km = sorted(ot, key=lambda r: -r[6])
    assert filas(R, "limit") == [(r[1], r[6]) for r in por_km[:3]]
    assert filas(R, "limit_offset") == [(r[1], r[6]) for r in por_km[3:6]]
    assert [f[1] for f in filas(R, "division")] == [r[6] // 1000 for r in ot[:3]]
    tramo = lambda x: "sin presupuesto" if x is None else "menor" if x < 50000 else "medio" if x < 150000 else "mayor"
    assert [f[2] for f in filas(R, "case")] == [tramo(r[7]) for r in ot]
    assert filas(R, "cuenta") == [(sum(r[5] is None for r in ot),)]
    # ejemplo resuelto: días en el taller al 17-09-2026 y plazos de entrega
    from datetime import date
    d = lambda s: date.fromisoformat(s)
    assert sorted(f[3] for f in filas(R, "ej_en_taller")) == sorted(float((d("2026-09-17") - d(r[4])).days) for r in ot if r[5] is None)
    assert [f[1] for f in filas(R, "ej_cobro")] == [r[3] for r in sorted(
        [r for r in ot if r[5] and r[3] in ("frenos", "embrague")], key=lambda r: -r[7])]
    plazo = lambda n: "mismo día" if n == 0 else "al día siguiente" if n <= 1 else "más de un día"
    assert all(f[3] == plazo(f[2]) for f in filas(R, "ej_plazo"))
    assert len(filas(R, "ej_plazo")) == sum(r[5] is not None for r in ot)

    h = ej.execute("SELECT * FROM hora").fetchall()
    # columnas: id_hora, paciente, edad, sector, profesional, fecha, asistio, espera_min
    assert filas(R, "e1") == [(r[1], r[2]) for r in sorted(h, key=lambda r: -r[2]) if r[3] == "azul" and r[2] >= 65]
    assert sorted(filas(R, "e2")) == sorted((r[1], r[4], r[5]) for r in h
                                             if r[4] in ("matrona", "dental") and "2026-10-05" <= r[5] <= "2026-10-07")
    assert [f[0] for f in filas(R, "e3a")] == sorted({r[4] for r in h})
    assert filas(R, "e3b") == [(sum(r[6] is None for r in h),)] and filas(R, "e3c") == [(0,)]
    assert [f[0] for f in filas(R, "e5_mal")] == [r[1] for r in h if r[3] == "rojo" or (r[3] == "verde" and r[2] < 18)]
    assert [f[0] for f in filas(R, "e5_bien")] == [r[1] for r in h if r[3] in ("rojo", "verde") and r[2] < 18]
    t6 = lambda x: "sin dato" if x is None else "a tiempo" if x <= 15 else "demora" if x <= 40 else "larga"
    assert [f[2] for f in filas(R, "e6")] == [t6(r[7]) for r in h if r[5] <= "2026-10-07"]
    assert sorted(f[0] for f in filas(R, "e8")) == sorted(r[1].split(" ", 1)[1] for r in h if r[6] is None)
    assert "no such column" in R["e9a"]["error"]
    assert len(filas(R, "e9a_bien")) == sum(r[4] == "medicina" for r in h)
    assert filas(R, "e9b") == [] and len(filas(R, "e9b_bien")) == sum(r[7] is None for r in h)
    assert filas(R, "e9c") == [] and filas(R, "e9c_valor") == [(0,)]
    assert len(filas(R, "e9c_bien")) == sum(r[5] == "2026-10-07" for r in h)
    assert filas(R, "e9d") == [] and [f[0] for f in filas(R, "e9d_bien")] == [r[1] for r in h if r[1].endswith("Muñoz")]
    # afirmaciones del texto sobre el motor (secciones 4 y 6)
    v = lambda q: ej.execute(q).fetchone()[0]
    assert v("SELECT 'pastillas traseras' LIKE 'pastillas%'") == 1
    assert v("SELECT 'líquido y pastillas delanteras' LIKE 'pastillas%'") == 0
    assert v("SELECT 'líquido y pastillas delanteras' LIKE '%delanteras'") == 1
    assert v("SELECT 'pastillas y discos delanteros' LIKE '%delanteras'") == 0
    assert v("SELECT 'KFTR42' LIKE '____42'") == 1 and v("SELECT 'BV7302' LIKE '____42'") == 0
    assert v("SELECT 'A' LIKE 'a'") == 1 and v("SELECT 'Ñ' LIKE 'ñ'") == 0
    assert v("SELECT '08/10/2026' > '07/11/2026'") == 1
    assert v("SELECT 140.000") == 140 and v("SELECT 7 / 2") == 3
    assert v("SELECT 100 * 1170 / 3190") == 36 and v("SELECT 1170 / 3190 * 100") == 0
    assert v("SELECT UPPER('alineación')") == "ALINEACIóN"
    assert v("SELECT LENGTH('alineación y balanceo')") == 21 == len("alineación y balanceo")
    assert len("alineación y balanceo".encode("utf-8")) == 22
    try:
        ej.execute("SELECT patente FROM orden_trabajo FETCH FIRST 3 ROWS ONLY")
        raise AssertionError("SQLite aceptó FETCH FIRST")
    except sqlite3.OperationalError:
        pass
    iny = R["_inyeccion"]
    assert iny[("mala", "Rosa Contreras")] == 1 and iny[("buena", "Rosa Contreras")] == 1
    assert iny[("mala", TEXTO_MALICIOSO)] == len(h) and iny[("buena", TEXTO_MALICIOSO)] == 0

    # caso
    prod = m.PRODUCTOS   # (id, nombre, precio, costo_var, seg)
    assert filas(RC, "caso_margen_unitario") == [
        (p[1], p[2], p[3], p[2] - p[3], round(100 * (p[2] - p[3]) / p[2], 1))
        for p in sorted(prod, key=lambda p: -(p[2] - p[3]) / p[2])]
    assert filas(RC, "e4") == [(p[1], p[2], p[2] - p[3], round(100 * (p[2] - p[3]) / p[2], 1))
                               for p in sorted(prod, key=lambda p: -(p[2] - p[3])) if 3000 <= p[2] <= 7000]
    ped = cas.execute("SELECT id_pedido, fecha, estado FROM pedido").fetchall()
    abiertos = sorted([p for p in ped if "2026-03-16" <= p[1] <= "2026-03-31" and p[2] in ("pendiente", "en taller")],
                      key=lambda p: (p[1], p[0]))
    assert filas(RC, "e7a") == [(len(abiertos),)] and filas(RC, "e7b") == abiertos[:3]
    assert filas(RC, "e7c") == [(sum(p[1] == "2026-03-17" for p in abiertos),)]
    pend = sorted([p for p in ped if p[2] == "pendiente"], key=lambda p: (p[1], p[0]))
    assert [f[0] for f in filas(RC, "caso_pendientes_lista")] == [p[0] for p in pend]
    assert len(filas(RC, "e9e")) == len(prod)
    assert [f[0] for f in filas(RC, "e9e_bien")] == [p[1] for p in prod if p[2] > 5000]


def cadena(RC, C, m):
    plano = lambda s: " ".join(s.replace(";", "").split())
    ok = True
    for k in ["u9_productos_caros", "u9_pedidos_pendientes"]:
        ok &= plano(RC[k]["sql"]) == plano(m.CONSULTAS[k])
        ok &= [tuple(f) for f in RC[k]["filas"]] == [tuple(f) for f in C[k]]
    print("CADENA:", "OK, las consultas u9_* son las del caso y dan lo mismo"
          f" ({len(C['u9_productos_caros'])} productos sobre $4.000, {C['u9_pedidos_pendientes'][0][0]} pedidos pendientes)"
          if ok else "NO calza")
    return ok


def esperados(R, RC, C):
    """Cifras de la lectura (prosa) que el .md tiene que tener."""
    s = []
    f = filas(R, "ej_cobro")
    total = sum(x[3] for x in f)
    s += [pesos(total), f"{round(100 * f[0][3] / total)} %"]
    s += [fmt(x[3], 0) for x in f]
    f = filas(R, "ej_en_taller")
    s += [f"{int(max(x[3] for x in f))} días"]
    f = filas(RC, "caso_margen_unitario")
    s += [fmt(f[0][4], 1) + " %", fmt(f[-1][4], 1) + " %"]
    f = filas(RC, "e4")
    s += [pesos(f[0][2])]
    s += [f"{filas(RC, 'e7a')[0][0]} pedidos", f"{filas(RC, 'e7c')[0][0]} pedidos del 17-03"]
    iny = R["_inyeccion"]
    s += [f"{iny[('mala', TEXTO_MALICIOSO)]} filas"]
    T = C["tablas"]
    s += [f"{T['producto']} productos", f"{T['cliente']} clientes", f"{T['pedido']} pedidos de marzo",
          f"{T['detalle_pedido']} líneas de detalle", f"{len(T)} tablas"]
    urg = [x for x in filas(RC, "caso_pendientes_lista") if x[4] == "urgente"]
    s += [f"{len(urg)} son urgentes"]
    return s


def revisar(R, RC, C):
    md = MD.read_text(encoding="utf-8")
    md_n = md.replace("{,}", ",").replace("{.}", ".")
    faltan = []
    for nombre, r in list(R.items()) + list(RC.items()):
        if nombre.startswith("_"):
            continue
        if r["sql"] not in md:
            faltan.append(f"consulta {nombre}")
        if tabla_md(r) not in md:
            faltan.append(f"resultado {nombre}")
    for codigo in [INYECCION_MALA, INYECCION_BUENA, TEXTO_MALICIOSO]:
        if codigo not in md:
            faltan.append(f"código 9.10: {codigo[:40]}")
    faltan += [x for x in esperados(R, RC, C) if x not in md_n]
    return faltan


if __name__ == "__main__":
    R, RC, C, m = resultados()
    for nombre, r in list(R.items()) + list(RC.items()):
        if nombre.startswith("_"):
            print(f"== {nombre}: {r}")
        elif "error" in r:
            print(f"== {nombre}: ERROR {r['error']}")
        else:
            print(f"== {nombre}: {len(r['filas'])} filas {r['filas'][:6]}{' …' if len(r['filas']) > 6 else ''}")
    print("SEGUNDO CAMINO: OK, cada WHERE, CASE, ORDER BY y LIMIT calza con el cálculo en Python")
    if not cadena(RC, C, m):
        sys.exit(1)
    if "--tablas" in sys.argv:
        for nombre, r in list(R.items()) + list(RC.items()):
            if not nombre.startswith("_"):
                print(f"\n<!-- {nombre} -->\n```sql\n{r['sql']}\n```\n\n{tabla_md(r)}")
    if "--revisar" in sys.argv:
        faltan = revisar(R, RC, C)
        print("REVISIÓN:", "OK, todas las consultas, resultados y cifras están en el texto" if not faltan
              else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
