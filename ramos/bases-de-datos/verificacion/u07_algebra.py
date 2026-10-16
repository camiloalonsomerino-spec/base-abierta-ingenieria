"""Unidad 7 · Álgebra relacional. Recalcula todas las cifras; con --revisar las busca en el .md.

El script trae un evaluador mínimo de álgebra relacional (relaciones como conjuntos de tuplas) y:

1. carga las bases de la unidad desde sql/u07_talleres.sql y sql/u07_feria.sql en memoria;
2. evalúa cada pregunta en álgebra con el evaluador y la misma pregunta en SQL con sqlite3, y exige
   que den el mismo conjunto de filas;
3. arma en memoria una copia de la base del caso (con los datos del script del caso, sin tocar
   datos/estampa_sur.db), corre sql/u07_caso.sql y compara con el álgebra y con el script del caso;
4. dibuja unidades/figuras/u07_arbol.svg (los dos árboles del ejemplo);
5. con --revisar, busca en el .md cada consulta, cada fila de cada resultado, el código del
   evaluador y las cifras del texto.

    python u07_algebra.py            # imprime los resultados
    python u07_algebra.py --tablas   # imprime las tablas de resultados en Markdown
    python u07_algebra.py --revisar  # además las busca en el .md
"""
from pathlib import Path
import importlib.util, json, re, sqlite3, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
SQL = RAMO / "sql"
MD = RAMO / "unidades" / "07-algebra-relacional.md"
SVG = RAMO / "unidades" / "figuras" / "u07_arbol.svg"


# --- evaluador (inicio)
class Rel:
    """Una relación: nombres de atributos y un CONJUNTO de tuplas (sin duplicados ni orden)."""
    def __init__(self, attrs, filas):
        self.attrs = tuple(attrs)
        self.filas = {tuple(f) for f in filas}

def sel(R, cond):                      # σ: las tuplas que cumplen la condición
    return Rel(R.attrs, {f for f in R.filas if cond(dict(zip(R.attrs, f)))})

def proy(R, *atr):                     # π: solo esas columnas; el conjunto borra repetidos
    i = [R.attrs.index(a) for a in atr]
    return Rel(atr, {tuple(f[k] for k in i) for f in R.filas})

def ren(R, nuevos):                    # ρ: cambia nombres de atributos {viejo: nuevo}
    return Rel([nuevos.get(a, a) for a in R.attrs], R.filas)

def compatibles(R, S):
    if len(R.attrs) != len(S.attrs):
        raise ValueError("no son compatibles: distinto número de atributos")

def union(R, S): compatibles(R, S); return Rel(R.attrs, R.filas | S.filas)
def dif(R, S):   compatibles(R, S); return Rel(R.attrs, R.filas - S.filas)
def inter(R, S): compatibles(R, S); return Rel(R.attrs, R.filas & S.filas)

def prod(R, S):                        # ×: cada tupla de R con cada tupla de S
    if set(R.attrs) & set(S.attrs):
        raise ValueError("atributos repetidos: renombra con ρ antes del producto")
    return Rel(R.attrs + S.attrs, {f + g for f in R.filas for g in S.filas})

def theta(R, S, cond):                 # ⋈θ = σθ(R × S)
    return sel(prod(R, S), cond)

def natural(R, S):                     # ⋈: iguala TODOS los atributos de igual nombre
    comun = [a for a in R.attrs if a in S.attrs]
    resto = [a for a in S.attrs if a not in comun]
    return Rel(R.attrs + tuple(resto),
               {f + tuple(g[S.attrs.index(a)] for a in resto)
                for f in R.filas for g in S.filas
                if all(f[R.attrs.index(a)] == g[S.attrs.index(a)] for a in comun)})

def div(R, S):                         # ÷ = πX(R) − πX((πX(R) × S) − R)
    X = [a for a in R.attrs if a not in S.attrs]
    rx = proy(R, *X)
    faltan = proy(dif(prod(rx, S), proy(R, *X, *S.attrs)), *X)
    return dif(rx, faltan)
# --- evaluador (fin)


# ---------------------------------------------------------------- formato
def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x)


def celda(v):
    return "NULL" if v is None else str(v)


def tabla(cols, filas):
    """Tabla Markdown tal como aparece en el .md (valores crudos, como los devuelve la base)."""
    lineas = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lineas += ["| " + " | ".join(celda(v) for v in f) + " |" for f in filas]
    return "\n".join(lineas)


def plano(s):
    return " ".join(s.split())


# ---------------------------------------------------------------- SQL desde los scripts
def leer_sql(ruta):
    """Separa un script en (preparación, {clave: consulta}) por las marcas «-- @clave»."""
    texto = ruta.read_text(encoding="utf-8")
    partes = re.split(r"^-- @(\w+)\s*$", texto, flags=re.M)
    prep, consultas = partes[0], {}
    for k, q in zip(partes[1::2], partes[2::2]):
        consultas[k] = q.strip()
    return prep, consultas


def base(ruta):
    prep, consultas = leer_sql(ruta)
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(prep)
    return con, consultas


def relacion(con, tabla_):
    cur = con.execute(f"SELECT * FROM {tabla_}")
    return Rel([d[0] for d in cur.description], cur.fetchall())


def correr(con, q):
    cur = con.execute(q)
    return [d[0] for d in cur.description], cur.fetchall()


def cargar_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_bd.py")
    caso = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caso)
    return caso


def base_del_caso(caso):
    """Copia en memoria de la base del caso, con los mismos datos y el mismo esquema."""
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(caso.ESQUEMA)
    clientes, pedidos, detalle, ordenes = caso.generar()
    con.executemany("INSERT INTO tienda VALUES (?,?,?)", caso.TIENDAS)
    con.executemany("INSERT INTO producto VALUES (?,?,?,?,?)", caso.PRODUCTOS)
    con.executemany("INSERT INTO proveedor VALUES (?,?,?)", caso.PROVEEDORES)
    con.executemany("INSERT INTO suministra VALUES (?,?,?)", caso.SUMINISTRA)
    con.executemany("INSERT INTO cliente VALUES (?,?,?,?)", clientes)
    con.executemany("INSERT INTO pedido VALUES (?,?,?,?)", pedidos)
    con.executemany("INSERT INTO detalle_pedido VALUES (?,?,?,?)", detalle)
    con.executemany("INSERT INTO orden_produccion VALUES (?,?,?,?)", ordenes)
    return con


# ---------------------------------------------------------------- comparación álgebra contra SQL
COMPARADAS = []   # (clave, columnas, filas SQL) para --tablas y --revisar
INTERMEDIAS = {}  # relaciones intermedias del ejemplo que el .md muestra completas


def igual(clave, alg, con, consultas, conjunto=True):
    cols, filas = correr(con, consultas[clave])
    if conjunto:
        assert len(filas) == len(set(filas)), f"{clave}: SQL devolvió duplicados"
    assert set(filas) == alg.filas, f"{clave}: álgebra {sorted(alg.filas)} ≠ SQL {sorted(filas)}"
    COMPARADAS.append((clave, cols, filas))
    return filas


def solo_sql(clave, con, consultas):
    cols, filas = correr(con, consultas[clave])
    COMPARADAS.append((clave, cols, filas))
    return filas


def resultados():
    R = {}
    # ======================= talleres (ejemplo y 7.1 a 7.4)
    con, Q = base(SQL / "u07_talleres.sql")
    V, T, I = (relacion(con, t) for t in ("vecino", "taller", "inscripcion"))
    R["tam"] = {"vecino": len(V.filas), "taller": len(T.filas), "inscripcion": len(I.filas)}

    # P1: vecinos del sector norte inscritos en cerámica
    ingenuo_prod = prod(prod(ren(V, {a: "v." + a for a in V.attrs}), ren(I, {a: "i." + a for a in I.attrs})),
                        ren(T, {a: "t." + a for a in T.attrs}))
    junta = natural(natural(V, I), T)
    ingenuo = proy(sel(junta, lambda r: r["sector"] == "norte" and r["actividad"] == "cerámica"), "nombre")
    vn = sel(V, lambda r: r["sector"] == "norte")
    vn_i = natural(vn, I)
    tc = sel(T, lambda r: r["actividad"] == "cerámica")
    final = natural(vn_i, tc)
    optimo = proy(final, "nombre")
    INTERMEDIAS["p1_vn_i"] = vn_i
    assert ingenuo.filas == optimo.filas
    R["p1"] = {"producto": len(ingenuo_prod.filas), "junta": len(junta.filas), "vn": len(vn.filas),
               "vn_i": len(vn_i.filas), "tc": len(tc.filas), "final": len(final.filas)}
    igual("p1", optimo, con, Q)

    # P2: vecinos sin inscripción
    sin = dif(proy(V, "id_vecino"), proy(I, "id_vecino"))
    igual("p2a", sin, con, Q)
    igual("p2b", proy(natural(sin, V), "id_vecino", "nombre"), con, Q)

    # P3: inscritos en todos los talleres del sábado (división)
    S = proy(sel(T, lambda r: r["dia"] == "sábado"), "id_taller")
    rx = proy(I, "id_vecino")
    todos_pares = prod(rx, S)
    faltan_pares = dif(todos_pares, I)
    faltan = proy(faltan_pares, "id_vecino")
    cociente = div(I, S)
    INTERMEDIAS["p3_faltan"] = faltan_pares
    assert cociente.filas == dif(rx, faltan).filas
    R["p3"] = {"S": sorted(S.filas), "rx": len(rx.filas), "pares": len(todos_pares.filas),
               "faltan_pares": sorted(faltan_pares.filas), "faltan": sorted(faltan.filas),
               "cociente": sorted(cociente.filas)}
    igual("p3", proy(natural(cociente, V), "id_vecino", "nombre"), con, Q)

    # 7.1
    igual("e1a", sel(V, lambda r: r["edad"] >= 60), con, Q)
    filas_b = solo_sql("e1b", con, Q)
    pi_sector = proy(V, "sector")
    igual("e1c", pi_sector, con, Q)
    R["e1"] = {"sin_distinct": len(filas_b), "pi": len(pi_sector.filas)}
    # 7.2
    paula = sel(V, lambda r: r["nombre"] == "Paula Rivas")
    igual("e2a", proy(natural(natural(paula, I), T), "actividad"), con, Q)
    sur_sab = natural(natural(sel(V, lambda r: r["sector"] == "sur"), I), sel(T, lambda r: r["dia"] == "sábado"))
    igual("e2b", proy(sur_sab, "nombre"), con, Q)
    # 7.3
    yoga = proy(natural(I, sel(T, lambda r: r["actividad"] == "yoga")), "id_vecino")
    guit = proy(natural(I, sel(T, lambda r: r["actividad"] == "guitarra")), "id_vecino")
    centro = proy(sel(V, lambda r: r["sector"] == "centro"), "id_vecino")
    igual("e3a", union(yoga, centro), con, Q)
    igual("e3b", inter(yoga, guit), con, Q)
    igual("e3c", dif(yoga, guit), con, Q)
    try:
        union(yoga, sel(V, lambda r: r["sector"] == "centro"))
        R["e3d"] = None
    except ValueError as e:
        R["e3d"] = str(e)
    try:
        con.execute("SELECT i.id_vecino FROM inscripcion i UNION SELECT * FROM vecino WHERE sector = 'centro'")
        R["e3d_sql"] = None
    except sqlite3.Error as e:
        R["e3d_sql"] = str(e)
    # 7.4
    jov = natural(natural(sel(V, lambda r: r["edad"] < 30), I), T)
    igual("e4", proy(jov, "actividad"), con, Q)
    R["e4"] = {"sin_distinct": len(solo_sql("e4sin", con, Q)), "con": len(proy(jov, "actividad").filas)}
    con.close()

    # ======================= feria (7.5 a 7.10)
    con, Q = base(SQL / "u07_feria.sql")
    P, PR, O = (relacion(con, t) for t in ("productor", "producto", "ofrece"))
    R["tam_feria"] = {"productor": len(P.filas), "producto": len(PR.filas), "ofrece": len(O.filas)}

    def quienes(desc):
        return proy(natural(O, sel(PR, lambda r: r["descripcion"] == desc)), "id_productor")
    tom, pap = quienes("tomate"), quienes("papa")
    igual("e5a", proy(natural(inter(tom, pap), P), "nombre"), con, Q)
    igual("e5b", proy(natural(dif(tom, pap), P), "nombre"), con, Q)

    # 7.6 · autojunta con ρ
    ot = proy(natural(O, sel(PR, lambda r: r["descripcion"] == "tomate")), "id_productor", "precio")
    A = ren(natural(ot, P), {"id_productor": "a.id", "precio": "precio_a", "nombre": "mas_barato", "comuna": "a.comuna"})
    B = ren(natural(ot, P), {"id_productor": "b.id", "precio": "precio_b", "nombre": "mas_caro", "comuna": "b.comuna"})
    pares = proy(theta(A, B, lambda r: r["precio_a"] < r["precio_b"]), "mas_barato", "mas_caro", "precio_a", "precio_b")
    igual("e6", pares, con, Q)
    R["e6"] = {"producto_AxB": len(prod(A, B).filas), "pares": len(pares.filas)}
    try:
        prod(natural(ot, P), natural(ot, P))
        R["e6_sin_rho"] = None
    except ValueError as e:
        R["e6_sin_rho"] = str(e)

    # 7.7 · división
    OP = proy(O, "id_productor", "id_producto")
    hort = proy(sel(PR, lambda r: r["tipo"] == "hortaliza"), "id_producto")
    frut = proy(sel(PR, lambda r: r["tipo"] == "fruta"), "id_producto")
    igual("e7a", proy(natural(div(OP, hort), P), "nombre"), con, Q)
    igual("e7b", proy(natural(div(OP, frut), P), "nombre"), con, Q)

    # 7.8 · tamaños
    Pq = ren(P, {"id_productor": "p.id_productor"})
    R["e8"] = {"x": solo_sql("e8a", con, Q)[0][0], "junta": solo_sql("e8b", con, Q)[0][0],
               "sin_cond": solo_sql("e8c", con, Q)[0][0], "con_cond": solo_sql("e8d", con, Q)[0][0]}
    assert R["e8"]["x"] == len(prod(Pq, O).filas)
    assert R["e8"]["junta"] == len(theta(Pq, O, lambda r: r["p.id_productor"] == r["id_productor"]).filas)
    caros = sel(O, lambda r: r["precio"] > 1000)
    assert R["e8"]["sin_cond"] == len(prod(Pq, caros).filas) == len(P.filas) * len(caros.filas)
    assert R["e8"]["con_cond"] == len(caros.filas)
    R["e8"]["caros"] = len(caros.filas)

    # 7.9 · divisor vacío
    leg = proy(sel(PR, lambda r: r["tipo"] == "legumbre"), "id_producto")
    div_vacio = div(OP, leg)
    filas_9a = igual("e9a", proy(natural(div_vacio, P), "nombre"), con, Q)
    igual("e9b", proy(natural(div(OP, hort), P), "nombre"), con, Q)
    filas_9c = solo_sql("e9c", con, Q)
    R["e9"] = {"vacio_alg": len(div_vacio.filas), "vacio_not_exists": len(filas_9a), "vacio_count": len(filas_9c)}

    # 7.10 · NULL
    filas_10a = solo_sql("e10a", con, Q)
    sc = proy(sel(P, lambda r: r["comuna"] == "San Carlos"), "nombre")
    igual("e10b", dif(proy(P, "nombre"), sc), con, Q)
    R["e10"] = {"distinto": sorted(f[0] for f in filas_10a), "except": sorted(dif(proy(P, "nombre"), sc).filas),
                "igual_null": solo_sql("e10c", con, Q)[0][0], "is_null": solo_sql("e10d", con, Q)[0][0]}
    con.close()

    # ======================= caso Estampa Sur
    caso = cargar_caso()
    con = base_del_caso(caso)
    Q = leer_sql(SQL / "u07_caso.sql")[1]
    t = {n: relacion(con, n) for n in ("tienda", "producto", "proveedor", "suministra", "cliente", "pedido",
                                       "detalle_pedido")}
    R["caso_tablas"] = {n: len(r.filas) for n, r in t.items()}
    c1 = proy(sel(t["producto"], lambda r: r["precio"] > 4000), "nombre", "precio")
    igual("c1", c1, con, Q)
    sinp = dif(proy(t["cliente"], "id_cliente"), proy(t["pedido"], "id_cliente"))
    c2 = proy(natural(sinp, t["cliente"]), "id_cliente", "nombre")
    igual("c2", c2, con, Q)
    def provee(nombre_prod):
        return proy(natural(t["suministra"], sel(proy(t["producto"], "id_producto", "nombre"),
                                                  lambda r: r["nombre"] == nombre_prod)), "id_proveedor")
    c3 = proy(natural(inter(provee("poleras básicas"), provee("gorros")), t["proveedor"]), "nombre")
    igual("c3", c3, con, Q)
    pend = sel(t["pedido"], lambda r: r["estado"] == "pendiente")
    mal = natural(natural(pend, t["cliente"]), t["tienda"])
    filas_mal = solo_sql("c4mal", con, Q)
    assert filas_mal[0][0] == len(mal.filas)
    tienda_r = ren(t["tienda"], {"nombre": "tienda", "comuna": "comuna_tienda"})
    cliente_r = ren(t["cliente"], {"nombre": "cliente"})
    c4 = proy(natural(natural(pend, cliente_r), tienda_r), "id_pedido", "cliente", "tienda")
    igual("c4", c4, con, Q)
    compras = proy(natural(t["pedido"], t["detalle_pedido"]), "id_cliente", "id_producto")
    catalogo = proy(t["producto"], "id_producto")
    c5 = proy(natural(div(compras, catalogo), t["cliente"]), "id_cliente", "nombre", "tipo")
    igual("c5", c5, con, Q)
    R["caso"] = {"c1": sorted(c1.filas, key=lambda f: -f[1]), "c2": sorted(c2.filas), "c3": sorted(c3.filas),
                 "c4mal": len(mal.filas), "comunes_c4": [a for a in natural(pend, t["cliente"]).attrs if a in t["tienda"].attrs],
                 "pendientes": len(pend.filas), "c4": sorted(c4.filas), "c5": sorted(c5.filas),
                 "compras": len(compras.filas),
                 "pares_catalogo": len(prod(proy(compras, "id_cliente"), catalogo).filas),
                 "con_compras": len(proy(compras, "id_cliente").filas),
                 "prod_cliente_pedido": len(t["cliente"].filas) * len(t["pedido"].filas)}
    con.close()
    return R


# ---------------------------------------------------------------- figura: los dos árboles de P1
def arbol_svg(R):
    def nodo(x, y, txt, w=None):
        w = w or 10 + 7.2 * len(txt)
        return (f'<rect x="{x - w / 2:.0f}" y="{y - 13}" width="{w:.0f}" height="26" rx="5" class="n"/>'
                f'<text x="{x}" y="{y + 5}">{txt}</text>')

    def linea(x1, y1, x2, y2):
        return f'<line x1="{x1}" y1="{y1 + 13}" x2="{x2}" y2="{y2 - 13}"/>'

    s = []
    # izquierda: selección arriba del producto
    L = [(170, 40, "π nombre"), (170, 100, "σ sector='norte' ∧ actividad='cerámica'"), (170, 160, f"× ({R['p1']['producto']} tuplas)"),
         (100, 220, "×"), (275, 220, "taller (5)"), (45, 280, "vecino (8)"), (172, 280, "inscripcion (15)")]
    for a, b in [(0, 1), (1, 2), (2, 3), (2, 4), (3, 5), (3, 6)]:
        s.append(linea(L[a][0], L[a][1], L[b][0], L[b][1]))
    s += [nodo(*n) for n in L]
    # derecha: selecciones empujadas hacia las hojas
    D = [(560, 40, "π nombre"), (560, 100, f"⋈ ({R['p1']['final']} tuplas)"), (470, 160, f"⋈ ({R['p1']['vn_i']} tuplas)"), (660, 160, "σ actividad='cerámica'"),
         (420, 220, "σ sector='norte'"), (560, 220, "inscripcion (15)"), (660, 220, "taller (5)"), (420, 280, "vecino (8)")]
    for a, b in [(0, 1), (1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (4, 7)]:
        s.append(linea(D[a][0], D[a][1], D[b][0], D[b][1]))
    s += [nodo(*n) for n in D]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 320" width="760" height="320" font-family="Segoe UI, sans-serif" font-size="12">
<style>.n{{fill:#F2F1EF;stroke:#2B2F33;stroke-width:1}} line{{stroke:#5F656B;stroke-width:1.2}} text{{text-anchor:middle;fill:#2B2F33}} .t{{font-weight:600;font-size:13px}}</style>
<text x="170" y="308" class="t">Árbol directo: filtra al final</text>
<text x="560" y="308" class="t">Árbol con las selecciones abajo</text>
{''.join(s)}
</svg>
"""
    SVG.parent.mkdir(parents=True, exist_ok=True)
    SVG.write_text(svg, encoding="utf-8")


# ---------------------------------------------------------------- cadena con el script del caso
def cadena(R):
    caso = cargar_caso()
    try:
        C = caso.calcular()
    except OSError:      # la base del caso está abierta por otro proceso: se usa el .json del caso
        C = json.loads((AQUI / "caso_estampa_sur_bd.json").read_text(encoding="utf-8"))
        C = {k: [tuple(f) for f in v] if isinstance(v, list) else v for k, v in C.items()}
    ok = all([
        all(R["caso_tablas"][n] == C["tablas"][n] for n in R["caso_tablas"]),
        [tuple(f) for f in C["u9_productos_caros"]] == R["caso"]["c1"],
        C["u10_clientes_sin_pedidos"][0][0] == len(R["caso"]["c2"]),
        C["u9_pedidos_pendientes"][0][0] == R["caso"]["pendientes"] == len(R["caso"]["c4"]),
    ])
    print("CADENA:", "OK, la pieza del caso calza (productos sobre $4.000, clientes sin pedidos y pedidos pendientes)"
          if ok else "NO calza")
    return ok


def esperados(R):
    s = []
    # cada consulta y cada fila de su resultado
    for clave, cols, filas in COMPARADAS:
        s.append(("consulta", clave, None))
        for f in filas:
            s.append(("fila", clave, "| " + " | ".join(celda(v) for v in f) + " |"))
    # cifras del texto
    p1, p3 = R["p1"], R["p3"]
    cifras = [f"{p1['producto']} tuplas", f"{p1['junta']} tuplas", f"{p1['vn_i']} tuplas", f"{p1['final']} tuplas",
              f"{p3['pares']} pares", f"{len(p3['faltan_pares'])} pares que faltan",
              f"{R['e1']['sin_distinct']} filas", f"{R['e1']['pi']} tuplas",
              f"{R['e4']['sin_distinct']} filas", f"{R['e6']['producto_AxB']} tuplas",
              f"{R['e8']['x']} filas", f"{R['e8']['junta']} filas", f"{R['e8']['sin_cond']} filas",
              f"{R['e8']['caros']} ofertas", f"{fmt(R['caso']['prod_cliente_pedido'])} tuplas", f"{R['caso']['compras']} pares",
              f"{R['caso']['pares_catalogo']} pares", f"{R['caso']['con_compras']} clientes con compras",
              R["e3d"], R["e3d_sql"], R["e6_sin_rho"]]
    s += [("cifra", None, c) for c in cifras]
    for nombre, rel in INTERMEDIAS.items():
        for f in sorted(rel.filas):
            s.append(("fila", nombre, "| " + " | ".join(celda(v) for v in f) + " |"))
    return s


def codigo_en_md(md):
    fuente = Path(__file__).read_text(encoding="utf-8")
    bloque = fuente.split("# --- evaluador (inicio)\n")[1].split("# --- evaluador (fin)")[0]
    return [l for l in bloque.splitlines() if l.strip() and l.rstrip() not in md]


if __name__ == "__main__":
    R = resultados()
    arbol_svg(R)
    for k, v in R.items():
        print(f"== {k}: {v}")
    if "--tablas" in sys.argv:
        prep_q = {}
        for f in ("u07_talleres.sql", "u07_feria.sql", "u07_caso.sql"):
            prep_q.update(leer_sql(SQL / f)[1])
        for clave, cols, filas in COMPARADAS:
            print(f"\n--- {clave}\n```sql\n{prep_q[clave]}\n```\n\n{tabla(cols, filas)}")
        for nombre, rel in INTERMEDIAS.items():
            print(f"\n--- {nombre}\n\n{tabla(rel.attrs, sorted(rel.filas))}")
    if not cadena(R):
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        md_plano = plano(md_n)
        lineas = set(l.strip() for l in md_n.splitlines())
        consultas = {}
        for f in ("u07_talleres.sql", "u07_feria.sql", "u07_caso.sql"):
            consultas.update(leer_sql(SQL / f)[1])
        faltan = []
        for tipo, clave, x in esperados(R):
            if tipo == "consulta" and plano(consultas[clave]) not in md_plano:
                faltan.append(f"consulta {clave}")
            elif tipo == "fila" and x not in lineas:
                faltan.append(f"fila {clave}: {x}")
            elif tipo == "cifra" and x not in md_n:
                faltan.append(f"cifra: {x}")
        faltan += [f"evaluador: {l.strip()}" for l in codigo_en_md(md)]
        # los datos de las dos bases, fila por fila
        for f in ("u07_talleres.sql", "u07_feria.sql"):
            con, _ = base(SQL / f)
            for t in [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]:
                for fila in con.execute(f"SELECT * FROM {t}"):
                    linea = "| " + " | ".join(celda(v) for v in fila) + " |"
                    if linea not in lineas:
                        faltan.append(f"dato {t}: {linea}")
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
