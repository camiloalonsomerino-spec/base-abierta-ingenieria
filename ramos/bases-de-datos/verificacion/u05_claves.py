"""Unidad 5 · Modelo relacional: claves e integridad. Recalcula todo; con --revisar lo busca en el .md.

Cada base de la unidad está en ramos/bases-de-datos/sql/u05_*.sql. Este script:

1. corre cada script en una base nueva en memoria, sentencia por sentencia, con sqlite3, y guarda la
   respuesta real de SQLite a cada intento marcado con «-- @etiqueta» (acepta, rechaza con su mensaje,
   o las filas de una consulta);
2. corre los intentos del caso sobre COPIAS en memoria de datos/estampa_sur.db (la original se abre
   solo para leer) y arma la tabla de claves del esquema desde los PRAGMA de SQLite;
3. cuenta superclaves por fuerza bruta y las compara con la fórmula;
4. dibuja los diagramas de tablas en unidades/figuras/ (SVG) desde los PRAGMA de cada base;
5. compara la base del caso con el script del caso (esquema, filas y conteos): imprime CADENA;
6. con --revisar, exige que cada sentencia de los scripts (salvo los INSERT de carga), cada respuesta,
   cada fila de cada resultado y cada cifra estén en el .md.

    python u05_claves.py               # imprime los resultados
    python u05_claves.py --fragmentos  # además imprime las tablas en Markdown que van en la unidad
    python u05_claves.py --revisar     # además las busca en el .md
"""
from pathlib import Path
from itertools import combinations
import importlib.util, json, re, sqlite3, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
SQL = RAMO / "sql"
FIG = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "05-claves-e-integridad.md"
DB_CASO = RAMO / "datos" / "estampa_sur.db"


# ---------------------------------------------------------------- formato chileno
def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x, 0)


# ---------------------------------------------------------------- correr un script
def correr(ruta, con=None):
    """Corre el script sentencia por sentencia. Las sentencias marcadas con «-- @etiqueta descripción»
    pueden fallar: se guarda su respuesta. Las demás (preparación) tienen que funcionar."""
    con = con or sqlite3.connect(":memory:", isolation_level=None)
    R, buf, marca = {}, [], None
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^-- @(\S+)\s*(.*)$", linea)
        if m and not buf:
            marca = (m.group(1), m.group(2).strip())
            continue
        if not buf and (not linea.strip() or linea.startswith("--")):
            continue
        buf.append(linea)
        texto = "\n".join(buf)
        if sqlite3.complete_statement(texto):
            buf = []
            try:
                cur = con.execute(texto)
                filas = cur.fetchall()
                cols = [d[0] for d in cur.description] if cur.description else []
                r = {"sql": texto, "ok": True, "filas": filas, "cols": cols, "n": cur.rowcount}
            except sqlite3.Error as e:
                r = {"sql": texto, "ok": False, "error": str(e)}
            if marca:
                r["desc"] = marca[1]
                R[marca[0]] = r
                marca = None
            elif not r["ok"]:
                raise RuntimeError(f"{ruta.name}: falló una sentencia de preparación:\n{texto}\n{r['error']}")
    return con, R


def copia_del_caso():
    """Copia en memoria de la base del caso; la original se abre solo para leer."""
    src = sqlite3.connect(f"file:{DB_CASO.as_posix()}?mode=ro", uri=True)
    mem = sqlite3.connect(":memory:", isolation_level=None)
    src.backup(mem)
    src.close()
    return mem


# ---------------------------------------------------------------- Markdown generado
def celda(v):
    if v is None:
        return "NULL"
    return str(v)


def md_filas(cols, filas):
    """Una tabla Markdown con el resultado tal como lo entrega SQLite."""
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(celda(v) for v in f) + " |" for f in filas]
    return out


def md_consulta(con, sql):
    cur = con.execute(sql)
    return md_filas([d[0] for d in cur.description], cur.fetchall())


def filas_txt(n):
    return "1 fila" if n == 1 else f"{n} filas"


def respuesta(r):
    if not r["ok"]:
        return f"rechaza: `{r['error']}`"
    if r["cols"]:
        return f"responde {filas_txt(len(r['filas']))}"
    if r["sql"].lstrip().upper().startswith("PRAGMA"):
        return "acepta"
    return f"acepta ({filas_txt(r['n'])})"


def md_intentos(R, etiquetas):
    out = ["| Intento | Qué se intenta | Respuesta de SQLite |", "|---|---|---|"]
    out += [f"| {e} | {R[e]['desc']} | {respuesta(R[e])} |" for e in etiquetas]
    return out


# ---------------------------------------------------------------- diagramas de tablas (SVG)
TINTA, SUAVE, LINEA, PAPEL, ACENTO = "#2B2F33", "#5F656B", "#B9B4AC", "#F2F1EF", "#E2622A"
ANCHO, FILA, CABEZA = 210, 19, 24


def esquema_de(con, tablas):
    """Columnas, claves y foráneas de cada tabla, leídas de los PRAGMA de SQLite."""
    E = {}
    for t in tablas:
        cols = con.execute(f"PRAGMA table_info({t})").fetchall()       # cid, name, type, notnull, dflt, pk
        fks = con.execute(f"PRAGMA foreign_key_list({t})").fetchall()  # id, seq, table, from, to, on_update, on_delete, match
        unicas = []
        for idx in con.execute(f"PRAGMA index_list({t})").fetchall():  # seq, name, unique, origin, partial
            if idx[2] and idx[3] == "u":
                unicas.append([c[2] for c in con.execute(f"PRAGMA index_info('{idx[1]}')").fetchall()])
        E[t] = {"cols": [(c[1], c[2], bool(c[3]), c[5]) for c in cols],
                "pk": [c[1] for c in sorted(cols, key=lambda c: c[5]) if c[5]],
                "fk": [(f[3], f[2], f[4], f[5], f[6]) for f in fks],
                "uq": unicas}
    return E


def svg_tablas(E, pos, titulo, ruta, ancho=210):
    """Diagrama de tablas: cada caja es una tabla; la flecha va de la foránea a la clave que referencia.
    La acción de cada foránea (si no es NO ACTION) se escribe en la fila de la foránea."""
    ancho_total = max(x for x, _ in pos.values()) + ancho + 75
    alto_total = max(y + CABEZA + FILA * len(E[t]["cols"]) for t, (_, y) in pos.items()) + 40

    def caja(t):
        x, y = pos[t]
        return x, y, CABEZA + FILA * len(E[t]["cols"])

    def y_col(t, col):
        x, y = pos[t]
        k = [c[0] for c in E[t]["cols"]].index(col)
        return y + CABEZA + FILA * k + FILA / 2

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho_total} {alto_total}" '
         f'width="{ancho_total}" height="{alto_total}" font-family="Segoe UI, Roboto, sans-serif">',
         f'<title>{titulo}</title>',
         '<defs><marker id="flecha" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{ACENTO}"/></marker></defs>',
         f'<rect width="{ancho_total}" height="{alto_total}" fill="#FFFFFF"/>']
    hay_acciones = False
    for t in E:
        for col, destino, col_dest, on_upd, on_del in E[t]["fk"]:
            x1, y1, _ = caja(t)
            x2, y2, _ = caja(destino)
            ya, yb = y_col(t, col), y_col(destino, col_dest)
            if x2 > x1 + 5:
                xa, xb, ca, cb = x1 + ancho, x2, x1 + ancho + 45, x2 - 45
            elif x2 < x1 - 5:
                xa, xb, ca, cb = x1, x2 + ancho, x1 - 45, x2 + ancho + 45
            else:
                xa, xb, ca, cb = x1 + ancho, x2 + ancho, x1 + ancho + 55, x2 + ancho + 55
            s.append(f'<path d="M{xa},{ya} C{ca},{ya} {cb},{yb} {xb},{yb}" fill="none" stroke="{ACENTO}" '
                     f'stroke-width="1.6" marker-end="url(#flecha)"/>')
    for t in E:
        x, y, h = caja(t)
        fks = {f[0]: f for f in E[t]["fk"]}
        uqs = {c for u in E[t]["uq"] for c in u}
        s.append(f'<rect x="{x}" y="{y}" width="{ancho}" height="{h}" rx="5" fill="#FFFFFF" stroke="{TINTA}" stroke-width="1.3"/>')
        s.append(f'<path d="M{x},{y + CABEZA} v-{CABEZA - 5} a5,5 0 0 1 5,-5 h{ancho - 10} a5,5 0 0 1 5,5 v{CABEZA - 5} z" fill="{TINTA}"/>')
        s.append(f'<text x="{x + 9}" y="{y + 16.5}" font-size="12.5" font-weight="600" fill="#FFFFFF">{t}</text>')
        for k, (col, tipo, nn, pk) in enumerate(E[t]["cols"]):
            yy = y + CABEZA + FILA * k
            if k % 2:
                s.append(f'<rect x="{x + 1}" y="{yy}" width="{ancho - 2}" height="{FILA}" fill="{PAPEL}"/>')
            marcas = [m for m, c in [("PK", pk), ("FK", col in fks), ("UQ", col in uqs and not pk)] if c]
            if col in fks:
                _, _, _, on_upd, on_del = fks[col]
                if on_del != "NO ACTION":
                    marcas.append(on_del); hay_acciones = True
                if on_upd != "NO ACTION":
                    marcas.append("act. " + on_upd); hay_acciones = True
            peso = ' font-weight="700"' if pk else ""
            s.append(f'<text x="{x + 9}" y="{yy + 13.5}" font-size="11.5" fill="{TINTA}"{peso} '
                     f'font-family="Cascadia Mono, Consolas, monospace">{col}</text>')
            etiqueta = " · ".join(marcas) if marcas else ("" if nn else "nulo")
            s.append(f'<text x="{x + ancho - 8}" y="{yy + 13.5}" font-size="10" fill="{ACENTO if marcas else SUAVE}" '
                     f'text-anchor="end" font-weight="600">{etiqueta}</text>')
    nota = ("PK clave primaria (negrita) · FK clave foránea (la flecha apunta a la clave que referencia) · "
            "UQ clave alternativa · «nulo»: admite NULL")
    if hay_acciones:
        nota += " · junto a FK, la acción al borrar y al actualizar («act.»)"
    s.append(f'<text x="10" y="{alto_total - 10}" font-size="10" fill="{SUAVE}">{nota}</text>')
    s.append("</svg>")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(s), encoding="utf-8")


# ---------------------------------------------------------------- superclaves
def superclaves(atributos, claves):
    """Fuerza bruta: todo subconjunto que contiene alguna clave candidata."""
    return [set(c) for r in range(1, len(atributos) + 1) for c in combinations(atributos, r)
            if any(set(k) <= set(c) for k in claves)]


def formula_superclaves(n, claves):
    """Inclusión y exclusión sobre las claves candidatas: Σ (−1)^(m+1) 2^(n − |unión de m claves|)."""
    total = 0
    for m in range(1, len(claves) + 1):
        for grupo in combinations(claves, m):
            union = set().union(*map(set, grupo))
            total += (-1) ** (m + 1) * 2 ** (n - len(union))
    return total


def unicos_minimos(cols, filas):
    """Conjuntos de columnas que no se repiten en ESTOS datos y que son mínimos."""
    unicos = [set(c) for r in range(1, len(cols) + 1) for c in combinations(range(len(cols)), r)
              if len({tuple(f[i] for i in c) for f in filas}) == len(filas)]
    minimos = [u for u in unicos if not any(v < u for v in unicos)]
    return [tuple(cols[i] for i in sorted(u)) for u in minimos]


def dv_rut(n):
    s, m = 0, 2
    for d in reversed(str(n)):
        s += int(d) * m
        m = m + 1 if m < 7 else 2
    r = 11 - s % 11
    return {11: "0", 10: "K"}.get(r, str(r))


# ---------------------------------------------------------------- el caso
def caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_bd.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


TABLAS_CASO = ["tienda", "producto", "proveedor", "suministra", "cliente", "pedido", "detalle_pedido",
               "orden_produccion"]


def checks_de(sql_tabla):
    """Los CHECK de un CREATE TABLE, con sus paréntesis balanceados."""
    out, i = [], 0
    while True:
        j = sql_tabla.find("CHECK (", i)
        if j < 0:
            return out
        k, nivel = j + 6, 0
        while True:
            nivel += {"(": 1, ")": -1}.get(sql_tabla[k], 0)
            if nivel == 0:
                break
            k += 1
        out.append(sql_tabla[j + 7:k])
        i = k


def tabla_de_claves(con):
    E = esquema_de(con, TABLAS_CASO)
    out = ["| Tabla | Grado | Cardinalidad | Clave primaria | Claves alternativas | Claves foráneas | CHECK |",
           "|---|---|---|---|---|---|---|"]
    for t in TABLAS_CASO:
        sql_t = con.execute("SELECT sql FROM sqlite_master WHERE name = ?", (t,)).fetchone()[0]
        n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        pk = "(" + ", ".join(E[t]["pk"]) + ")"
        uq = ", ".join("(" + ", ".join(u) + ")" for u in E[t]["uq"]) or "—"
        fk = ", ".join(f"{c} → {d}" for c, d, *_ in E[t]["fk"]) or "—"
        ck = ", ".join(f"`{c}`" for c in checks_de(sql_t)) or "—"
        out.append(f"| {t} | {len(E[t]['cols'])} | {n} | {pk} | {uq} | {fk} | {ck} |")
    return out, E


def cadena(con_caso):
    m = caso()
    ok = True
    # 1 · el esquema de la base es el del script, tabla por tabla
    plano = lambda s: " ".join(s.split())
    bloques = {re.match(r"\s*(\w+)", b).group(1): plano("CREATE TABLE" + b.rstrip().rstrip(";"))
               for b in m.ESQUEMA.split("CREATE TABLE")[1:]}
    for t in TABLAS_CASO:
        ok &= plano(con_caso.execute("SELECT sql FROM sqlite_master WHERE name = ?", (t,)).fetchone()[0]) == bloques[t]
    # 2 · las filas son las que genera el script con su semilla
    clientes, pedidos, detalle, ordenes = m.generar()
    ok &= con_caso.execute("SELECT * FROM tienda ORDER BY 1").fetchall() == m.TIENDAS
    ok &= con_caso.execute("SELECT * FROM producto ORDER BY 1").fetchall() == m.PRODUCTOS
    ok &= con_caso.execute("SELECT * FROM cliente ORDER BY 1").fetchall() == clientes
    ok &= con_caso.execute("SELECT * FROM pedido ORDER BY 1").fetchall() == pedidos
    ok &= sorted(con_caso.execute("SELECT * FROM detalle_pedido").fetchall()) == sorted(detalle)
    ok &= con_caso.execute("SELECT id_producto, semana, lote FROM orden_produccion ORDER BY 1").fetchall() == [o[1:] for o in ordenes]
    # 3 · los conteos son los del .json del caso
    conteos = json.loads((AQUI / "caso_estampa_sur_bd.json").read_text(encoding="utf-8"))["tablas"]
    ok &= all(con_caso.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] == n for t, n in conteos.items())
    print("CADENA:", "OK, la base del caso es la que genera su script (mismo esquema, mismas filas, 8 tablas)"
          if ok else "NO calza")
    return ok


# ---------------------------------------------------------------- resultados
SCRIPTS = {
    "ej": "u05_biblioteca.sql", "e01": "u05_e01_carros.sql", "e03": "u05_e03_cesfam.sql",
    "e04": "u05_e04_jardin.sql", "e05": "u05_e05_bicicletas.sql", "e06": "u05_e06_conductores.sql",
    "e07": "u05_e07_veterinaria.sql", "e08": "u05_e08_notas.sql", "e09": "u05_e09_liga.sql",
    "e09b": "u05_e09_liga_bien.sql", "e10m": "u05_e10_expo_mal.sql", "e10b": "u05_e10_expo_bien.sql",
}
# tablas de datos que el texto muestra completas (se generan desde la base, antes de los intentos)
DATOS = {
    "ej": ["socio", "telefono_socio", "libro", "ejemplar", "prestamo"],
    "e01": ["carro"], "e03": ["box", "hora"], "e04": ["parvulo", "alergia_parvulo", "asistencia"],
    "e05": ["bicicleta", "cliente", "arriendo"], "e06": ["matricula"], "e07": ["mascota_1", "boleta_1"],
    "e09": ["equipo", "jugador", "partido", "gol"], "e10m": ["stand", "emprendedor", "venta"],
}
# intentos que el texto muestra como tabla de respuestas
INTENTOS = {
    "ej": ["i1", "i2", "i3", "i4", "i5", "i6", "i7", "i8", "i9", "i10a", "i10b", "i10d"],
    "e03": list("abcdefg"), "e04": list("acdeg"), "e05": list("abcdefg"), "e06": ["mal", "bien", "choque"],
    "e07": ["d1", "d2", "d3"], "e08": list("abcdefgijk"), "e09b": ["r1", "r2"],
    "e10m": ["m1", "m2", "m3", "m5"], "e10b": ["b1", "b2", "b3", "b6", "b7", "b8"],
    "caso": list("abcdefghijk") + ["m", "n", "p"], "prop": ["q1", "q4", "q5", "q6"],
}
# consultas cuyo resultado el texto muestra como tabla
CONSULTAS = {
    "ej": ["c8", "c9a", "c9b", "i10c"], "e01": ["grado", "filas", "distintas", "repetidas"],
    "e04": ["b", "f"], "e06": ["rut"], "e07": ["d2c"], "e08": ["resumen", "h", "l"],
    "e09": ["antes", "goleadores_antes", "despues", "goleadores_despues"], "e09b": ["r3"],
    "e10m": ["m4"], "e10b": ["b4", "b5"], "caso": ["l", "o"], "prop": ["q2", "q3"],
}


def datos_antes_de_intentos(ruta):
    """Corre solo la preparación (hasta la primera etiqueta) para mostrar los datos iniciales."""
    texto = Path(ruta).read_text(encoding="utf-8")
    prep = texto.split("\n-- @", 1)[0]
    con = sqlite3.connect(":memory:", isolation_level=None)
    con.executescript(prep)
    return con


def resultados():
    R = {"frag": {}}
    for k, f in SCRIPTS.items():
        con, r = correr(SQL / f)
        R[k] = r
        if k in DATOS:
            c0 = datos_antes_de_intentos(SQL / f)
            for t in DATOS[k]:
                R["frag"][f"{k}:{t}"] = md_consulta(c0, f"SELECT * FROM {t}")
        if k == "ej":
            R["E_ej"] = esquema_de(c0, DATOS["ej"])
    # caso: intentos sobre una copia; propuesta sobre otra copia
    con_caso = copia_del_caso()
    R["claves_md"], R["E_caso"] = tabla_de_claves(con_caso)
    R["caso_ok"] = cadena(con_caso)
    _, R["caso"] = correr(SQL / "u05_caso.sql", copia_del_caso())
    con_prop, R["prop"] = correr(SQL / "u05_caso_propuesta.sql", copia_del_caso())
    R["E_prop"] = esquema_de(con_prop, ["pedido", "producto", "detalle_pedido", "orden_produccion"])
    for k, etiquetas in INTENTOS.items():
        R["frag"][f"intentos:{k}"] = md_intentos(R[k], etiquetas)
    for k, etiquetas in CONSULTAS.items():
        for e in etiquetas:
            r = R[k][e]
            assert r["ok"], (k, e, r.get("error"))
            R["frag"][f"filas:{k}:{e}"] = md_filas(r["cols"], r["filas"]) if r["filas"] else []
    R["frag"]["claves"] = R["claves_md"]

    # --- teoría: superclaves de socio (dos claves candidatas de un atributo, grado 4)
    socio = ["id_socio", "rut", "nombre", "comuna"]
    R["sc_socio"] = len(superclaves(socio, [["id_socio"], ["rut"]]))
    assert R["sc_socio"] == formula_superclaves(4, [["id_socio"], ["rut"]])
    # --- 5.2: jugador(rut, nombre, equipo, camiseta) con claves {rut} y {equipo, camiseta}
    jug = ["rut", "nombre", "equipo", "camiseta"]
    K = [["rut"], ["equipo", "camiseta"]]
    R["e02_sc"] = superclaves(jug, K)
    assert len(R["e02_sc"]) == formula_superclaves(4, K)
    R["e02_n"] = len(R["e02_sc"])
    R["e02_lista"] = sorted(("{" + ", ".join(a for a in jug if a in s) + "}" for s in R["e02_sc"]),
                            key=lambda x: (x.count(","), x))
    # --- 5.2 (b): el mismo conteo si además el nombre fuera clave (no lo es): para mostrar la fórmula
    # --- 5.6: los conjuntos que no se repiten en los datos
    con6 = datos_antes_de_intentos(SQL / "u05_e06_conductores.sql")
    filas6 = con6.execute("SELECT * FROM matricula").fetchall()
    R["e06_unicos"] = unicos_minimos(["rut", "nombre", "curso", "horario"], filas6)
    R["e06_n_filas"] = len(filas6)
    # --- 5.9: lo que se llevó la cascada
    a, d = R["e09"]["antes"]["filas"][0], R["e09"]["despues"]["filas"][0]
    R["e09_borrados"] = tuple(x - y for x, y in zip(a, d))
    # --- 5.7: filas reescritas en el diseño 2 contra 1 en el diseño 3
    R["e07_filas_d2"] = sum(R["e07"]["d2c"]["filas"][0])
    # --- RUT: los dígitos verificadores de todos los RUT de la unidad son válidos
    for f in SCRIPTS.values():
        for num, dv in re.findall(r"'(\d{1,2}\.\d{3}\.\d{3})-([\dK])'", (SQL / f).read_text(encoding="utf-8")):
            assert dv_rut(int(num.replace(".", ""))) == dv, (f, num, dv)
    # --- caso: cuántas filas de detalle se llevó la cascada de la propuesta
    R["prop_detalle_borrado"] = 212 - R["prop"]["q3"]["filas"][0][0]
    assert R["prop_detalle_borrado"] == len([x for x in caso().generar()[2] if x[0] == 3])
    return R


def figuras(R):
    pos_ej = {"socio": (20, 20), "telefono_socio": (20, 175), "prestamo": (340, 95), "ejemplar": (660, 20),
              "libro": (660, 165)}
    svg_tablas(R["E_ej"], pos_ej, "Biblioteca vecinal: tablas, claves y acciones", FIG / "u05_biblioteca.svg", 250)
    pos_caso = {"tienda": (20, 20), "cliente": (20, 145), "pedido": (20, 300), "detalle_pedido": (310, 300),
                "producto": (310, 110), "suministra": (600, 20), "proveedor": (600, 150),
                "orden_produccion": (600, 300)}
    svg_tablas(R["E_caso"], pos_caso, "Estampa Sur: las 8 tablas con sus claves", FIG / "u05_estampa_sur.svg")


def lineas_de_codigo():
    """Toda línea de los scripts, salvo los INSERT de carga, tiene que estar en el .md."""
    faltan = {}
    for f in list(SCRIPTS.values()) + ["u05_caso.sql", "u05_caso_propuesta.sql"]:
        texto = (SQL / f).read_text(encoding="utf-8")
        partes = texto.split("\n-- @", 1)
        prep = [l for l in partes[0].splitlines() if l.strip() and not l.startswith("INSERT INTO")]
        resto = ("-- @" + partes[1]).splitlines() if len(partes) > 1 else []
        faltan[f] = prep + [l for l in resto if l.strip()]
    return faltan


def esperados(R):
    s = []
    for frag in R["frag"].values():
        s += frag
    s += [f"{R['sc_socio']} superclaves", f"{R['e02_n']} superclaves"] + R["e02_lista"]
    s += ["{" + ", ".join(u) + "}" for u in R["e06_unicos"]]
    j, p, g = R["e09_borrados"]
    s += [f"{j} jugadores", f"{p} partidos", f"{g} goles", f"{R['e07_filas_d2']} filas"]
    s += [f"{R['prop_detalle_borrado']} filas de detalle", "SQLite " + sqlite3.sqlite_version]
    return s


if __name__ == "__main__":
    R = resultados()
    print("SQLite", sqlite3.sqlite_version)
    for k in SCRIPTS:
        for e, r in R[k].items():
            print(f"{k}:{e:<18} {respuesta(r):<60} {r.get('filas', '') if r['ok'] else ''}")
    for e, r in list(R["caso"].items()) + list(R["prop"].items()):
        print(f"caso:{e:<16} {respuesta(r):<60} {r.get('filas', '') if r['ok'] else ''}")
    print("superclaves de socio:", R["sc_socio"], "· 5.2:", R["e02_n"], R["e02_lista"])
    print("5.6 únicos mínimos en los datos:", R["e06_unicos"])
    print("5.9 borrados (jugadores, partidos, goles):", R["e09_borrados"], "· 5.7 filas reescritas:", R["e07_filas_d2"])
    print("propuesta: filas de detalle borradas con el pedido 3:", R["prop_detalle_borrado"])
    figuras(R)
    print("FIGURAS: unidades/figuras/u05_biblioteca.svg y u05_estampa_sur.svg")
    if not R["caso_ok"]:
        sys.exit(1)
    if "--fragmentos" in sys.argv:
        for k, v in R["frag"].items():
            print(f"\n### {k}\n" + "\n".join(v))
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        lineas = set(l.rstrip() for l in md.splitlines())
        faltan = [x for x in esperados(R) if (x not in lineas if x.startswith("|") else x not in md_n)]
        for f, ls in lineas_de_codigo().items():
            faltan += [f"{f}: {l}" for l in ls if l.rstrip() not in lineas]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}:")
        for x in faltan[:80]:
            print("   ", x)
        sys.exit(1 if faltan else 0)
