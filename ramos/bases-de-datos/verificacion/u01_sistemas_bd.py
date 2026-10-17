"""Unidad 1 · Datos, información y sistemas de bases de datos. Recalcula todas las cifras; con
--revisar las busca en el .md.

1. Declara los datos de la unidad (la planilla del club, los diez ejercicios y la planilla del caso).
2. Cuenta en Python lo que la unidad cuenta a mano: copias de más, inconsistencias, celdas, filas.
3. Corre con sqlite3 cada script de sql/u01_*.sql y guarda el resultado de cada sentencia (filas o
   mensaje de error). Las marcadas «-- debe fallar» tienen que fallar; las demás, funcionar.
4. Arma en memoria la base del caso con el mismo esquema y los mismos datos del script del caso (sin
   tocar datos/estampa_sur.db), corre las consultas del caso y exige que den lo del .json: CADENA.
5. Dibuja unidades/figuras/u01_tres_niveles.svg.
6. Con --revisar, exige que cada cifra, cada sentencia SQL, cada fila de resultado y cada mensaje de
   error estén en el .md.

    python u01_sistemas_bd.py            # imprime los resultados
    python u01_sistemas_bd.py --revisar  # además los busca en el .md
"""
from pathlib import Path
from collections import Counter
from itertools import permutations
import importlib.util, json, sqlite3, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
SQL = RAMO / "sql"
FIG = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "01-sistemas-de-bases-de-datos.md"


# ---------------------------------------------------------------- formato chileno
def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return ("$" if x >= 1000 else "\\$") + fmt(x, 0)


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


# ---------------------------------------------------------------- correr un script SQL
def sentencias(texto):
    """Parte un script en sentencias (cada una termina con «;» al final de una línea). Devuelve
    (sql, debe_fallar)."""
    out, buf, falla = [], [], False
    for linea in texto.splitlines():
        s = linea.strip()
        if not buf and s.startswith("--"):
            falla = falla or s.lower().startswith("-- debe fallar")
            continue
        if not s and not buf:
            continue
        buf.append(linea.rstrip())
        if s.endswith(";"):
            out.append(("\n".join(buf).strip(), falla))
            buf, falla = [], False
    assert not buf, f"sentencia sin «;»: {buf}"
    return out


def correr(nombre, con):
    """Corre sql/<nombre> sentencia por sentencia. Devuelve una lista de dict con sql, columnas,
    filas, error y filas cambiadas."""
    res = []
    for q, falla in sentencias((SQL / nombre).read_text(encoding="utf-8")):
        r = {"sql": q, "falla": falla, "cols": None, "filas": None, "error": None, "cambios": None}
        try:
            cur = con.execute(q)
            if cur.description:
                r["cols"] = [d[0] for d in cur.description]
                r["filas"] = cur.fetchall()
            else:
                r["cambios"] = cur.rowcount
        except sqlite3.Error as e:
            r["error"] = str(e)
        assert (r["error"] is not None) == falla, (nombre, q, r["error"])
        res.append(r)
    return res


def nueva():
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    return con


def celda(v):
    return "NULL" if v is None else str(v)


def fila_md(fila):
    return "| " + " | ".join(celda(v) for v in fila) + " |"


def tabla_md(r):
    """La tabla Markdown que el .md tiene que mostrar para una consulta."""
    lineas = ["| " + " | ".join(r["cols"]) + " |", "|" + "---|" * len(r["cols"])]
    return "\n".join(lineas + [fila_md(f) for f in r["filas"]])


# ---------------------------------------------------------------- la base del caso, en memoria
def modulo_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_bd.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def base_del_caso(m):
    """Lo mismo que hace crear() en el script del caso, pero en memoria: el archivo no se toca."""
    con = nueva()
    con.executescript(m.ESQUEMA)
    clientes, pedidos, detalle, ordenes = m.generar()
    con.executemany("INSERT INTO tienda VALUES (?,?,?)", m.TIENDAS)
    con.executemany("INSERT INTO producto VALUES (?,?,?,?,?)", m.PRODUCTOS)
    con.executemany("INSERT INTO proveedor VALUES (?,?,?)", m.PROVEEDORES)
    con.executemany("INSERT INTO suministra VALUES (?,?,?)", m.SUMINISTRA)
    con.executemany("INSERT INTO cliente VALUES (?,?,?,?)", clientes)
    con.executemany("INSERT INTO pedido VALUES (?,?,?,?)", pedidos)
    con.executemany("INSERT INTO detalle_pedido VALUES (?,?,?,?)", detalle)
    con.executemany("INSERT INTO orden_produccion VALUES (?,?,?,?)", ordenes)
    con.commit()
    return con, (clientes, pedidos, detalle, ordenes)


# ---------------------------------------------------------------- datos (originales)
# Ejemplo · planilla de cuotas del club: (fecha, nombre escrito, teléfono escrito, categoría,
# cuota escrita, pagado, socio real). El socio real es lo que la planilla no guarda.
CLUB_SOCIOS = {1: ("Antonia Rivas", "9 0000 0033", "sub-13"), 2: ("Benjamín Soto", "9 0000 0028", "sub-15"),
               3: ("Catalina Mora", "9 0000 0038", "adulto"), 4: ("Diego Paredes", "9 0000 0015", "sub-15"),
               5: ("Emilia Cáceres", "9 0000 0008", "sub-13")}
CLUB_CUOTAS = {"sub-13": 14500, "sub-15": 16500, "adulto": 21000}
CLUB_PLANILLA = [
    ("2026-03-02", "Antonia Rivas", "9 0000 0033", "sub-13", 14500, 14500, 1),
    ("2026-03-03", "Benjamín Soto", "9 0000 0028", "sub-15", 16500, 16500, 2),
    ("2026-03-05", "Catalina Mora", "9 0000 0038", "adulto", 21000, 21000, 3),
    ("2026-03-09", "Diego Paredes", "9 0000 0015", "sub-15", 16500, 16500, 4),
    ("2026-03-10", "Emilia Cáceres", "9 0000 0008", "sub-13", 14500, 14500, 5),
    ("2026-04-01", "Antonia Rivas", "9 0000 0033", "sub-13", 14500, 14500, 1),
    ("2026-04-04", "Benjamín Soto", "9 0000 0027", "sub-15", 16500, 16500, 2),
    ("2026-04-06", "Catalina Mora", "9 0000 0038", "adulto", 21000, 21000, 3),
    ("2026-04-08", "Diego Paredes", "9 0000 0015", "sub-15", 16000, 16000, 4),
    ("2026-04-12", "Emilia Caceres", "9 0000 0008", "sub-13", 14500, 14500, 5),
]
CLUB_ESCALA = (120, 12)    # socios y meses de un año completo

# 1.2 · archivo de puestos de la feria
FERIA = [(14, "Juana Toledo", "verduras", 6, "miércoles"), (15, "Luis Arriagada", "frutas", 4, "miércoles"),
         (22, "Juana Toledo", "verduras", 6, "sábado"), (31, "Pedro Sanhueza", "huevos", 3, "sábado")]

# 1.5 · planilla de la veterinaria: (fecha, mascota, dueño, teléfono, servicio, precio)
VETE = [("2026-08-03", "Toby", "Marcela Ojeda", "9 0000 0005", "vacuna antirrábica", 18900),
        ("2026-08-03", "Luna", "Marcela Ojeda", "9 0000 0005", "desparasitación", 9400),
        ("2026-08-07", "Rocco", "Andrés Vidal", "9 0000 0031", "consulta", 22500),
        ("2026-08-12", "Toby", "Marcela Ojeda", "9 0000 0005", "consulta", 22500),
        ("2026-08-15", "Kira", "Sofía Henríquez", "9 0000 0024", "vacuna antirrábica", 18900),
        ("2026-08-19", "Rocco", "Andrés Vidal", "9 0000 0032", "desparasitación", 9400),
        ("2026-08-21", "Luna", "Marcela Ojeda", "9 0000 0005", "vacuna antirrábica", 19800),
        ("2026-08-26", "Kira", "Sofía Henríquez", "9 0000 0024", "consulta", 22500)]

# 1.7 · el pedido de la pastelería como documento
PASTELERIA = {"pedido": 5012, "fecha": "2026-09-18",
              "cliente": {"nombre": "Daniela Pizarro", "telefono": "9 0000 0013"},
              "items": [{"producto": "torta tres leches", "cantidad": 1, "precio": 18500},
                        {"producto": "kuchen de nuez", "cantidad": 2, "precio": 9800},
                        {"producto": "berlines", "cantidad": 12, "precio": 900}]}
PASTELERIA_PEDIDOS_DANIELA = 9

# 1.9 · hostal: camas libres y dos ventas simultáneas
HOSTAL = {"libres": 6, "A": 2, "B": 3, "despues": 3}

# 1.10 · planilla del taller de bicicletas: (orden, fecha, cliente, teléfono, bicicleta, servicio, valor)
BICI = [(101, "2026-07-02", "Felipe Cárcamo", "9 0000 0004", "ruta roja", "cambio de cadena", 12900),
        (101, "2026-07-02", "Felipe Cárcamo", "9 0000 0004", "ruta roja", "ajuste de frenos", 7500),
        (102, "2026-07-03", "Ignacia Muñoz", "9 0000 0035", "urbana azul", "mantención completa", 34900),
        (103, "2026-07-08", "Felipe Cárcamo", "9 0000 0004", "ruta roja", "parche de cámara", 4500),
        (103, "2026-07-08", "Felipe Cárcamo", "9 0000 0004", "ruta roja", "ajuste de frenos", 7500),
        (104, "2026-07-10", "Tomás Leiva", "9 0000 0009", "montaña negra", "cambio de cadena", 12900),
        (104, "2026-07-10", "Tomás Leiva", "9 0000 0009", "montaña negra", "ajuste de frenos", 7500),
        (104, "2026-07-10", "Tomás Leiva", "9 0000 0009", "montaña negra", "parche de cámara", 4500),
        (105, "2026-07-15", "Ignacia Muñoz", "9 0000 0035", "urbana azul", "ajuste de frenos", 7500)]


# ---------------------------------------------------------------- cálculos
def copias_de_mas(filas, dueno, valor):
    """Cuántas celdas repiten un dato que ya estaba escrito: filas menos dueños distintos."""
    return len(filas) - len({dueno(f) for f in filas}), {dueno(f) for f in filas}


def inconsistentes(filas, dueno, valor):
    """Dueños con más de un valor escrito para el mismo dato."""
    vals = {}
    for f in filas:
        vals.setdefault(dueno(f), set()).add(valor(f))
    return sorted(k for k, v in vals.items() if len(v) > 1)


def ejemplo():
    P = CLUB_PLANILLA
    R = {"filas": len(P), "columnas": 6, "celdas": len(P) * 6}
    socio = lambda f: f[6]
    R["copias"] = {
        "nombre": copias_de_mas(P, socio, lambda f: f[1])[0],
        "telefono": copias_de_mas(P, socio, lambda f: f[2])[0],
        "categoria": copias_de_mas(P, socio, lambda f: f[3])[0],
        "cuota": copias_de_mas(P, lambda f: f[3], lambda f: f[4])[0],
    }
    R["copias_total"] = sum(R["copias"].values())
    R["copias_pct"] = R["copias_total"] / R["celdas"]
    R["inc_nombre"] = inconsistentes(P, socio, lambda f: f[1])
    R["inc_telefono"] = inconsistentes(P, socio, lambda f: f[2])
    R["inc_cuota"] = inconsistentes(P, lambda f: f[3], lambda f: f[4])
    assert R["inc_nombre"] == [5] and R["inc_telefono"] == [2] and R["inc_cuota"] == ["sub-15"]
    R["celdas_tel_benjamin"] = sum(1 for f in P if f[6] == 2)
    # el diseño en tres tablas
    R["celdas_tablas"] = len(CLUB_CUOTAS) * 2 + len(CLUB_SOCIOS) * 4 + len(P) * 3
    s, m = CLUB_ESCALA
    R["escala_planilla"] = s * m * 6
    R["escala_tablas"] = len(CLUB_CUOTAS) * 2 + s * 4 + s * m * 3
    # lo cobrado de menos
    R["de_menos"] = [(CLUB_SOCIOS[f[6]][0], f[0], f[5], CLUB_CUOTAS[f[3]]) for f in P if f[5] < CLUB_CUOTAS[f[3]]]
    R["recaudado"] = sum(f[5] for f in P)
    # el script SQL
    con = nueva()
    R["sql"] = correr("u01_sistemas_bd.sql", con)
    # comprobación cruzada: lo que quedó en la base es la planilla
    assert con.execute("SELECT COUNT(*), SUM(monto) FROM pago").fetchone() == (len(P), R["recaudado"])
    sel = [r for r in R["sql"] if r["filas"] is not None]
    assert [tuple(x) for x in sel[0]["filas"]] == R["de_menos"]
    return R


def ejercicios():
    E = {}
    # 1.2
    E["e02"] = {"campos": len(FERIA[0]), "registros": len(FERIA), "celdas": len(FERIA) * len(FERIA[0]),
                "puestos_juana": sum(1 for f in FERIA if f[1] == "Juana Toledo")}
    # 1.5
    V = VETE
    dueno = lambda f: f[2]
    e = {"filas": len(V), "celdas": len(V) * 6,
         "veces_tel_marcela": sum(1 for f in V if f[2] == "Marcela Ojeda"),
         "copias_tel": copias_de_mas(V, dueno, lambda f: f[3])[0],
         "copias_precio": copias_de_mas(V, lambda f: f[4], lambda f: f[5])[0],
         "inc_tel": inconsistentes(V, dueno, lambda f: f[3]),
         "inc_precio": inconsistentes(V, lambda f: f[4], lambda f: f[5]),
         "duenos": len({f[2] for f in V}), "mascotas": len({f[1] for f in V}),
         "servicios": len({f[4] for f in V}), "atenciones": len(V)}
    assert e["inc_tel"] == ["Andrés Vidal"] and e["inc_precio"] == ["vacuna antirrábica"]
    e["copias_total"] = e["copias_tel"] + e["copias_precio"]
    E["e05"] = e
    # 1.6
    E["e06"] = {"sql": correr("u01_e06_almacen.sql", nueva())}
    # 1.7
    D = PASTELERIA
    total = sum(i["cantidad"] * i["precio"] for i in D["items"])
    filas = {"cliente": 1, "pedido": 1, "producto": len({i["producto"] for i in D["items"]}), "detalle": len(D["items"])}
    r = correr("u01_e07_pasteleria.sql", nueva())
    assert r[-1]["filas"][0][0] == total
    E["e07"] = {"total": total, "filas": filas, "filas_total": sum(filas.values()), "sql": r,
                "subtotales": [i["cantidad"] * i["precio"] for i in D["items"]]}
    # 1.9 · todas las intercalaciones de «A lee, A escribe» con «B lee, B escribe»
    h = HOSTAL
    finales = []
    for orden in permutations(["rA", "wA", "rB", "wB"]):
        if orden.index("rA") > orden.index("wA") or orden.index("rB") > orden.index("wB"):
            continue
        valor, leido = h["libres"], {}
        for paso in orden:
            quien = paso[1]
            if paso[0] == "r":
                leido[quien] = valor
            else:
                valor = leido[quien] - h[quien]
        finales.append(("".join(orden), valor))
    correcto = h["libres"] - h["A"] - h["B"]
    e = {"intercalaciones": len(finales), "correcto": correcto,
         "buenas": sum(1 for _, v in finales if v == correcto),
         "finales": sorted({v for _, v in finales}),
         "fig": dict(finales)["rArBwAwB"], "fig_inv": dict(finales)["rArBwBwA"]}
    e["vendidas_despues"] = h["despues"]
    e["sobreventa"] = (h["A"] + h["B"] + h["despues"]) - h["libres"]
    r = correr("u01_e09_hostal.sql", nueva())
    assert r[4]["filas"][0][1] == correcto and r[6]["filas"][0][1] == correcto
    e["sql"] = r
    E["e09"] = e
    # 1.10
    B = BICI
    e = {"filas": len(B), "clientes": len({f[2] for f in B}), "bicicletas": len({f[4] for f in B}),
         "servicios": len({f[5] for f in B}), "ordenes": len({f[0] for f in B}), "detalle": len(B),
         "total_104": sum(f[6] for f in B if f[0] == 104),
         "celdas_tel_felipe": sum(1 for f in B if f[2] == "Felipe Cárcamo"),
         "copias_cliente": len(B) - len({f[0] for f in B}),        # cliente de la orden, repetido por línea
         "copias_fecha": len(B) - len({f[0] for f in B}),
         "copias_valor": len(B) - len({f[5] for f in B})}
    e["tablas_filas"] = e["clientes"] + e["bicicletas"] + e["servicios"] + e["ordenes"] + e["detalle"]
    E["e10"] = e
    return E


def caso():
    m = modulo_caso()
    con, (clientes, pedidos, detalle, ordenes) = base_del_caso(m)
    C = {}
    C["tablas"] = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in
                   ["tienda", "producto", "proveedor", "suministra", "cliente", "pedido", "detalle_pedido", "orden_produccion"]}
    C["consultas_caso"] = {k: [list(r) for r in con.execute(q).fetchall()] for k, q in m.CONSULTAS.items()}
    # la planilla plana: una fila por línea de pedido, nueve columnas
    cli = {c[0]: c for c in clientes}
    tienda = {t[0]: t for t in m.TIENDAS}
    ped = {p[0]: p for p in pedidos}
    filas = [(d[0], ped[d[0]][2], cli[ped[d[0]][1]][1], tienda[cli[ped[d[0]][1]][3]][1],
              tienda[cli[ped[d[0]][1]][3]][2], m.PRODUCTOS[d[1] - 1][1], d[2], d[3], ped[d[0]][3]) for d in detalle]
    C["planilla_filas"] = len(filas)
    C["planilla_celdas"] = len(filas) * 9
    por_cliente = Counter(f[2] for f in filas)
    C["cliente_top"], C["cliente_top_filas"] = por_cliente.most_common(1)[0]
    C["clientes_en_planilla"] = len(por_cliente)
    C["clientes_fuera"] = len(clientes) - len(por_cliente)
    C["filas_concepcion"] = sum(1 for f in filas if f[4] == "Concepción")
    lineas = Counter(d[0] for d in detalle)
    C["pedidos_varias"] = sum(1 for v in lineas.values() if v > 1)
    C["pedidos_tres"] = sum(1 for v in lineas.values() if v == 3)
    C["copias_estado"] = len(filas) - len(pedidos)
    C["copias_cliente"] = len(filas) - len(pedidos)
    C["copias_comuna"] = len(filas) - len(m.TIENDAS)
    # aislamiento: la semana 6 cruza el plan del taller con la ficha de productos
    s6 = [(o[1], o[3]) for o in ordenes if o[2] == 6]
    C["s6_segundos"] = sum(q * m.PRODUCTOS[p - 1][4] for p, q in s6)
    C["s6_horas"] = C["s6_segundos"] / 3600
    C["s6_terminos"] = [(q, m.PRODUCTOS[p - 1][4]) for p, q in s6]
    # el script SQL del caso
    C["sql"] = correr("u01_caso.sql", con)
    sel = [r for r in C["sql"] if r["filas"] is not None]
    assert [tuple(x) for x in sel[0]["filas"]] == sorted(filas, key=lambda f: (f[0], [p[1] for p in m.PRODUCTOS].index(f[5])))[:8]
    C["page_size"], C["paginas"] = sel[1]["filas"][0][0], sel[2]["filas"][0][0]
    C["bytes"] = C["page_size"] * C["paginas"]
    C["vista"] = sel[3]["filas"]
    C["paginas_indice"] = sel[4]["filas"][0][0]
    assert sel[3]["filas"] == sel[5]["filas"], "la vista cambió"
    assert len(C["vista"]) == 5
    C["celdas_tablas"] = sum(n * len(con.execute(f"SELECT * FROM {t} LIMIT 0").description) for t, n in C["tablas"].items())
    con.close()
    return C


def cadena(C):
    J = json.loads((AQUI / "caso_estampa_sur_bd.json").read_text(encoding="utf-8"))
    ok = C["tablas"] == J["tablas"]
    ok &= all(C["consultas_caso"][k] == J[k] for k in J if k != "tablas")
    ok &= C["clientes_fuera"] == J["u10_clientes_sin_pedidos"][0][0]
    ok &= abs(C["s6_horas"] - sum(r[2] for r in J["u11_produccion_semana_6"])) < 1e-9
    print("CADENA:", "OK, la base en memoria es la del caso (8 tablas, sus filas y sus consultas); "
          "4 clientes fuera de la planilla y 33 h en la semana 6" if ok else "NO calza")
    return ok


# ---------------------------------------------------------------- figura
def figura(C):
    W, H = 760, 400
    tinta, suave, acento, papel, linea = "#2B2F33", "#5F656B", "#E2622A", "#F2F1EF", "#B9B5AE"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Segoe UI, Arial, sans-serif" font-size="13">',
         f'<rect width="{W}" height="{H}" fill="white"/>']

    def caja(x, y, w, h, texto, fill="white", borde=tinta, peso="normal", tam=12):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{borde}" stroke-width="1.3"/>')
        lineas = texto.split("\n")
        for k, t in enumerate(lineas):
            yy = y + h / 2 + (k - (len(lineas) - 1) / 2) * 15 + 4
            o.append(f'<text x="{x + w / 2}" y="{yy:.1f}" text-anchor="middle" font-size="{tam}" font-weight="{peso}" fill="{tinta}">{t}</text>')

    bandas = [(20, "NIVEL EXTERNO", "lo que ve cada usuario"), (150, "NIVEL CONCEPTUAL", "qué se guarda y sus reglas"),
              (280, "NIVEL INTERNO", "cómo se guarda en el disco")]
    for y, t, sub in bandas:
        o.append(f'<rect x="10" y="{y}" width="{W - 20}" height="100" rx="8" fill="{papel}"/>')
        o.append(f'<text x="24" y="{y + 22}" font-size="11.5" font-weight="bold" letter-spacing="1" fill="{acento}">{t}</text>')
        o.append(f'<text x="24" y="{y + 39}" font-size="11" fill="{suave}">{sub}</text>')
    # externo
    ext = [(200, "vendedora de Puerto\nclientes_puerto: 5 clientes"), (395, "taller\nórdenes de la semana"),
           (590, "dueño\nventas por tienda")]
    for x, t in ext:
        caja(x, 45, 160, 50, t)
    # conceptual
    caja(200, 172, 550, 56, "8 tablas: tienda · producto · proveedor · suministra · cliente · pedido\n"
                           "detalle_pedido · orden_produccion, con sus claves y restricciones", tam=11.5)
    # interno
    caja(200, 302, 260, 56, f"estampa_sur.db: {C['paginas']} páginas\nde {fmt(C['page_size'])} bytes = {fmt(C['bytes'])} bytes", tam=11.5)
    caja(490, 302, 260, 56, f"con un índice nuevo: {C['paginas_indice']} páginas\n(las consultas no cambian)", tam=11.5)
    # flechas de correspondencia
    for x in (280, 475, 670):
        o.append(f'<line x1="{x}" y1="95" x2="{x}" y2="172" stroke="{linea}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    o.append(f'<line x1="475" y1="228" x2="475" y2="302" stroke="{linea}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    o.append(f'<text x="186" y="138" text-anchor="end" font-size="10.5" fill="{suave}">independencia lógica</text>')
    o.append(f'<text x="186" y="268" text-anchor="end" font-size="10.5" fill="{suave}">independencia física</text>')
    o.append("</svg>")
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "u01_tres_niveles.svg").write_text("\n".join(o), encoding="utf-8")


# ---------------------------------------------------------------- lo que el .md tiene que decir
def esperados(R, E, C):
    s = []
    # ejemplo
    s += [f"{R['filas']} filas", f"{R['celdas']} celdas", f"{R['copias_total']} de esas {R['celdas']} celdas",
          pct(R["copias_pct"]), f"{R['copias']['cuota']} copias de más", f"{R['celdas_tablas']} celdas",
          fmt(R["escala_planilla"]), fmt(R["escala_tablas"]), f"{R['celdas_tel_benjamin']} celdas",
          pesos(R["recaudado"]), pesos(R["de_menos"][0][3] - R["de_menos"][0][2])]
    # 1.2
    e = E["e02"]; s += [f"{e['campos']} campos", f"{e['registros']} registros", f"{e['celdas']} datos"]
    # 1.5
    e = E["e05"]; s += [f"{e['veces_tel_marcela']} veces", f"{e['copias_tel']} copias de más del teléfono",
                        f"{e['copias_precio']} del precio", f"{e['copias_total']} de las {e['celdas']} celdas",
                        f"{e['duenos']} dueños", f"{e['mascotas']} mascotas", f"{e['servicios']} servicios",
                        f"{e['atenciones']} atenciones"]
    # 1.7
    e = E["e07"]; s += [pesos(e["total"]), f"{e['filas_total']} filas", f"{PASTELERIA_PEDIDOS_DANIELA} documentos"]
    s += [pesos(x) for x in e["subtotales"]]
    # 1.9
    e = E["e09"]; s += [f"{e['intercalaciones']} intercalaciones", f"solo {e['buenas']}", f"queda en {e['fig']}",
                        f"queda en {e['fig_inv']}", f"sobreventa de {e['sobreventa']} camas",
                        "{" + ", ".join(str(v) for v in e["finales"]) + "}"]
    # 1.10
    e = E["e10"]; s += [pesos(e["total_104"]), f"{e['clientes']} clientes", f"{e['bicicletas']} bicicletas",
                        f"{e['servicios']} servicios", f"{e['ordenes']} órdenes", f"{e['detalle']} líneas",
                        f"{e['tablas_filas']} filas", f"{e['celdas_tel_felipe']} celdas", f"{e['copias_fecha']} copias de más"]
    # caso
    s += [f"{C['planilla_filas']} filas", fmt(C["planilla_celdas"]) + " celdas", C["cliente_top"],
          f"{C['cliente_top_filas']} filas", f"{C['filas_concepcion']} veces", f"{C['pedidos_varias']} pedidos",
          f"{C['pedidos_tres']} tienen tres", f"{C['copias_estado']} copias de más", f"{C['clientes_en_planilla']} clientes",
          f"{C['clientes_fuera']} clientes", fmt(C["s6_segundos"]) + " segundos", f"{C['s6_horas']:.0f} horas",
          fmt(C["bytes"]) + " bytes", f"{C['paginas']} páginas", f"{C['paginas_indice']} páginas", fmt(C["celdas_tablas"])]
    s += [f"{q} × {sg}" for q, sg in C["s6_terminos"]]
    for t, n in C["tablas"].items():
        s.append(f"| `{t}` |")
        s.append(f"| {n} |")
    return s


def sql_en_md(md, *bloques):
    """Cada sentencia (sin importar los espacios), cada fila de resultado y cada error, en el .md."""
    plano = " ".join(md.split())
    lineas = set(l.strip() for l in md.splitlines())
    faltan = []
    for nombre, res in bloques:
        for r in res:
            if " ".join(r["sql"].split()) not in plano:
                faltan.append(f"{nombre} · sentencia: {r['sql'][:60]}")
            if r["error"] and r["error"] not in md:
                faltan.append(f"{nombre} · error: {r['error']}")
            if r["filas"] is not None:
                if "| " + " | ".join(r["cols"]) + " |" not in lineas:
                    faltan.append(f"{nombre} · encabezado: {r['cols']}")
                faltan += [f"{nombre} · fila: {fila_md(f)}" for f in r["filas"] if fila_md(f) not in lineas]
    return faltan


if __name__ == "__main__":
    R, E, C = ejemplo(), ejercicios(), caso()
    for nombre, d in (("ejemplo", R), ("caso", C)):
        print(f"== {nombre}")
        for k, v in d.items():
            if k != "sql":
                print(f"   {k} = {v}")
    for k, v in E.items():
        print(f"== {k}: " + str({kk: vv for kk, vv in v.items() if kk != "sql"}))
    for nombre, res in (("ejemplo", R["sql"]), ("1.6", E["e06"]["sql"]), ("1.7", E["e07"]["sql"]),
                        ("1.9", E["e09"]["sql"]), ("caso", C["sql"])):
        print(f"== SQL {nombre}")
        for r in res:
            primera = r["sql"].splitlines()[0]
            if r["error"]:
                print(f"   {primera} -> ERROR {r['error']}")
            elif r["filas"] is not None:
                print(f"   {primera}\n" + tabla_md(r))
            else:
                print(f"   {primera} -> {r['cambios']} filas")
    figura(C)
    print("figura: unidades/figuras/u01_tres_niveles.svg")
    if not cadena(C):
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = " ".join(md.replace("{,}", ",").replace("{.}", ".").split())   # sin saltos de línea
        faltan = [x for x in esperados(R, E, C) if " ".join(x.split()) not in md_n]
        faltan += sql_en_md(md, ("ejemplo", R["sql"]), ("1.6", E["e06"]["sql"]), ("1.7", E["e07"]["sql"]),
                            ("1.9", E["e09"]["sql"]), ("caso", C["sql"]))
        faltan += [f"figura {f}" for f in ["figuras/u01_tres_niveles.svg"] if f not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
