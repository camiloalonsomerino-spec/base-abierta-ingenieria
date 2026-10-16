"""Unidad 6 · Normalización. Recalcula todo; con --revisar lo busca en el .md.

1. Un motor de dependencias funcionales: clausura, claves candidatas, atributos primos, forma normal más
   alta (1FN, 2FN, 3FN, FNBC), cubrimiento mínimo, síntesis en 3FN, prueba de descomposición sin
   pérdida (el «chase») y de conservación de dependencias. Todo por fuerza bruta sobre subconjuntos.
2. Corre los scripts sql/u06_*.sql en bases nuevas en memoria (el del caso, sobre una copia en memoria de
   datos/estampa_sur.db) y guarda la respuesta real de SQLite a cada consulta marcada con «-- @».
3. Comprueba que la síntesis del motor da las mismas tablas que el SQL y que el esquema del caso.
4. Dibuja las figuras de la descomposición en unidades/figuras/.
5. CADENA: la planilla sale de la base del caso y su descomposición devuelve las tablas del caso.
6. Con --revisar, exige cada línea de código (salvo los INSERT ... VALUES de carga), cada tabla de
   resultado y cada cifra en el .md.

    python u06_normalizacion.py               # imprime los resultados
    python u06_normalizacion.py --fragmentos  # además imprime las tablas en Markdown de la unidad
    python u06_normalizacion.py --revisar     # además las busca en el .md
"""
from pathlib import Path
from itertools import combinations
import importlib.util, json, re, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
SQL = RAMO / "sql"
FIG = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "06-normalizacion.md"

_spec = importlib.util.spec_from_file_location("u05", AQUI / "u05_claves.py")
u05 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(u05)
correr, md_filas, md_consulta, md_intentos = u05.correr, u05.md_filas, u05.md_consulta, u05.md_intentos
datos_antes_de_intentos, copia_del_caso, fmt, pesos = u05.datos_antes_de_intentos, u05.copia_del_caso, u05.fmt, u05.pesos


# ================================================================ motor de dependencias funcionales
def DF(texto):
    """'a, b -> c, d; c -> e' → [(frozenset{a,b}, frozenset{c,d}), (frozenset{c}, frozenset{e})]"""
    out = []
    for parte in texto.split(";"):
        izq, der = parte.split("->")
        out.append((frozenset(x.strip() for x in izq.split(",")), frozenset(x.strip() for x in der.split(","))))
    return out


def clausura(X, F):
    C = set(X)
    cambio = True
    while cambio:
        cambio = False
        for izq, der in F:
            if izq <= C and not der <= C:
                C |= der
                cambio = True
    return C


def es_superclave(X, R, F):
    return set(R) <= clausura(X, F)


def claves(R, F):
    """Claves candidatas: superclaves mínimas. Los atributos que no aparecen a la derecha de ninguna
    dependencia están en toda clave; se parte de ellos."""
    derecha = set().union(*(d for _, d in F)) if F else set()
    nucleo = [a for a in R if a not in derecha]
    resto = [a for a in R if a in derecha]
    encontradas = []
    for r in range(0, len(resto) + 1):
        for extra in combinations(resto, r):
            X = set(nucleo) | set(extra)
            if any(k <= X for k in encontradas):
                continue
            if es_superclave(X, R, F):
                encontradas.append(frozenset(X))
    return encontradas


def proyectar(F, Ri):
    """Las dependencias que valen dentro de Ri: X → (X⁺ ∩ Ri) − X para todo X ⊆ Ri."""
    out = []
    Ri = list(Ri)
    for r in range(1, len(Ri) + 1):
        for X in combinations(Ri, r):
            der = (clausura(X, F) & set(Ri)) - set(X)
            if der:
                out.append((frozenset(X), frozenset(der)))
    return out


def forma_normal(R, F, proyectada=True):
    """La forma normal más alta (desde 1FN, que se supone: valores atómicos)."""
    Fp = proyectar(F, R) if proyectada else F
    K = claves(R, Fp)
    primos = set().union(*K)
    no_primos = set(R) - primos
    # 2FN: ningún no primo depende de una parte propia de una clave
    for k in K:
        for r in range(1, len(k)):
            for S in combinations(k, r):
                if (clausura(S, Fp) - set(S)) & no_primos:
                    return "1FN"
    # 3FN: toda X → A no trivial tiene X superclave o A primo; FNBC: X superclave siempre
    fnbc = True
    for izq, der in Fp:
        if es_superclave(izq, R, Fp):
            continue
        fnbc = False
        if (der - izq) - primos:
            return "2FN"
    return "FNBC" if fnbc else "3FN"


def violaciones(R, F):
    """Las dependencias (de la lista dada) que impiden FNBC dentro de R, con su tipo."""
    K = claves(R, F)
    primos = set().union(*K)
    out = []
    for izq, der in F:
        if not (izq <= set(R)) or es_superclave(izq, R, F):
            continue
        parcial = any(izq < k for k in K)
        no_p = (der - izq) - primos
        tipo = "parcial" if parcial and no_p else ("transitiva" if no_p else "FNBC")
        out.append((izq, der, tipo))
    return out


def cubrimiento_minimo(F):
    # 1 · un atributo a la derecha
    G = [(izq, frozenset({a})) for izq, der in F for a in sorted(der)]
    # 2 · sacar atributos sobrantes a la izquierda
    H = []
    for izq, der in G:
        izq = set(izq)
        for a in sorted(izq):
            if len(izq) > 1 and der <= clausura(izq - {a}, G):
                izq = izq - {a}
        H.append((frozenset(izq), der))
    # 3 · sacar dependencias redundantes (y duplicadas)
    H = list(dict.fromkeys(H))
    i = 0
    while i < len(H):
        resto = H[:i] + H[i + 1:]
        if H[i][1] <= clausura(H[i][0], resto):
            H = resto
        else:
            i += 1
    return H


def sintesis_3fn(R, F):
    Fm = cubrimiento_minimo(F)
    grupos = {}
    for izq, der in Fm:
        grupos.setdefault(izq, set(izq)).update(der)
    tablas = [frozenset(t) for t in grupos.values()]
    if not any(any(k <= t for k in claves(R, F)) for t in tablas):
        tablas.append(claves(R, F)[0])
    tablas = [t for t in tablas if not any(t < u for u in tablas)]
    return list(dict.fromkeys(tablas)), Fm


def sin_perdida(R, tablas, F):
    """Chase: una fila por tabla con «a» en sus columnas; se igualan por dependencias; sin pérdida si
    alguna fila queda toda en «a»."""
    R = list(R)
    T = [{a: ("a", a) if a in t else ("b", i, a) for a in R} for i, t in enumerate(tablas)]
    cambio = True
    while cambio:
        cambio = False
        for izq, der in F:
            for i in range(len(T)):
                for j in range(i + 1, len(T)):
                    if all(T[i][x] == T[j][x] for x in izq):
                        for y in der:
                            if T[i][y] != T[j][y]:
                                nuevo = min(T[i][y], T[j][y], key=lambda v: v[0] != "a")
                                viejo = T[j][y] if nuevo == T[i][y] else T[i][y]
                                for fila in T:
                                    if fila[y] == viejo:
                                        fila[y] = nuevo
                                cambio = True
    return any(all(f[a][0] == "a" for a in R) for f in T)


def no_conservadas(F, tablas):
    """Las dependencias de F que no se deducen de las proyecciones sobre las tablas."""
    out = []
    for izq, der in F:
        Z = set(izq)
        cambio = True
        while cambio:
            cambio = False
            for t in tablas:
                nuevo = (clausura(Z & t, F) & t) - Z
                if nuevo:
                    Z |= nuevo
                    cambio = True
        if not der <= Z:
            out.append((izq, der))
    return out


def txt(X, orden=None):
    xs = sorted(X, key=(orden.index if orden else None))
    return "{" + ", ".join(xs) + "}"


def txt_df(izq, der, orden=None):
    return ", ".join(sorted(izq, key=(orden.index if orden else None))) + " → " + \
        ", ".join(sorted(der, key=(orden.index if orden else None)))


# ================================================================ los datos de la unidad
NAT_R = ["rut", "nadador", "curso", "nivel", "horario", "piscina", "profesor", "fono_profesor", "mensualidad"]
NAT_F = DF("rut -> nadador; curso -> nivel, horario, piscina, profesor; profesor -> fono_profesor; "
           "nivel -> mensualidad")
NAT_2FN = [{"rut", "nadador"}, {"curso", "nivel", "horario", "piscina", "profesor", "fono_profesor", "mensualidad"},
           {"rut", "curso"}]
NAT_3FN = [{"nivel", "mensualidad"}, {"profesor", "fono_profesor"}, {"curso", "nivel", "horario", "piscina", "profesor"},
           {"rut", "nadador"}, {"rut", "curso"}]

GIM_R = ["socio", "actividad", "instructor"]               # teoría: 3FN que no es FNBC
GIM_F = DF("instructor -> actividad; socio, actividad -> instructor")

E02_R = ["A", "B", "C", "D", "E"]
E02_F = DF("A -> B; B -> C; C, D -> E; E -> A")

E04 = {
    "arriendo": (["depto", "mes", "arrendatario", "valor"], DF("depto, mes -> arrendatario; depto -> valor")),
    "vuelo": (["numero", "fecha", "avion", "capacidad"], DF("numero, fecha -> avion; avion -> capacidad")),
    "atencion": (["paciente", "especialidad", "medico"], DF("medico -> especialidad; paciente, especialidad -> medico")),
    "producto": (["sku", "nombre", "precio"], DF("sku -> nombre, precio; nombre -> sku")),
}
E05_R = ["cajero", "fecha", "caja", "piso", "supervisor"]
E05_F = DF("cajero, fecha -> caja; caja, fecha -> cajero; caja -> piso; piso, fecha -> supervisor")

E06_R = ["guardia", "dia", "porteria"]
E06_F = DF("guardia -> porteria")

E07_R = ["fecha", "cancha", "direccion", "local", "visita", "goles_local", "goles_visita", "arbitro", "fono_arbitro"]
E07_F = DF("fecha, cancha -> local, visita, goles_local, goles_visita, arbitro; fecha, local -> cancha; "
           "fecha, visita -> cancha; cancha -> direccion; arbitro -> fono_arbitro")

E08_R = ["alumno", "ramo", "tutor"]
E08_F = DF("tutor -> ramo; alumno, ramo -> tutor")

E09_R = ["n_pedido", "fecha", "rut", "cliente", "direccion", "sector", "camion", "chofer", "cilindros"]
E09_F = DF("n_pedido -> fecha, rut, cilindros, camion; rut -> cliente, direccion; direccion -> sector; "
           "rut -> sector; sector, fecha -> camion; camion, fecha -> chofer; n_pedido, rut -> cilindros")

CASO_R = ["id_pedido", "fecha", "estado", "id_cliente", "cliente", "tipo", "id_tienda", "tienda", "comuna",
          "id_producto", "producto", "precio", "costo_var", "seg_estampado", "cantidad", "precio_unit"]
CASO_F = DF("id_pedido -> fecha, estado, id_cliente; id_cliente -> cliente, tipo, id_tienda; "
            "id_tienda -> tienda, comuna; tienda -> id_tienda; "
            "id_producto -> producto, precio, costo_var, seg_estampado; producto -> id_producto; "
            "id_pedido, id_producto -> cantidad, precio_unit")
# columnas de las tablas del caso con los nombres de la planilla
CASO_TABLAS = {"tienda": ["id_tienda", "tienda", "comuna"],
               "producto": ["id_producto", "producto", "precio", "costo_var", "seg_estampado"],
               "cliente": ["id_cliente", "cliente", "tipo", "id_tienda"],
               "pedido": ["id_pedido", "id_cliente", "fecha", "estado"],
               "detalle_pedido": ["id_pedido", "id_producto", "cantidad", "precio_unit"]}


def caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_bd.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ================================================================ figuras
COLORES = ["#E2622A", "#2F7F8C", "#7A5BA6", "#B8862B", "#4E7D3A"]
TINTA, SUAVE, PAPEL = "#2B2F33", "#5F656B", "#F2F1EF"


def svg_descomposicion(planilla, tablas, casa, titulo, ruta, cols_der=2):
    """A la izquierda la planilla, cada columna con el color de la tabla donde vive su dato; a la derecha
    las tablas de la descomposición, con su clave en negrita."""
    FILA, CAB, AN, ANT = 19, 24, 200, 210
    color = {t: COLORES[i] for i, t in enumerate(tablas)}
    alto_izq = CAB + FILA * len(planilla)
    # tablas a la derecha, repartidas en columnas
    pos, cols = {}, [[] for _ in range(cols_der)]
    for i, t in enumerate(tablas):
        cols[i % cols_der].append(t)
    for c, lista in enumerate(cols):
        y = 0
        for t in lista:
            pos[t] = (AN + 90 + c * (ANT + 25), y)
            y += CAB + FILA * len(tablas[t][0]) + 16
    alto = max(alto_izq, max(y + CAB + FILA * len(tablas[t][0]) for t, (_, y) in pos.items())) + 50
    ancho = AN + 90 + cols_der * (ANT + 25) + 10
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}" '
         f'font-family="Segoe UI, Roboto, sans-serif"><title>{titulo}</title>',
         f'<rect width="{ancho}" height="{alto}" fill="#FFFFFF"/>']
    # planilla
    s.append(f'<rect x="10" y="0" width="{AN}" height="{alto_izq}" rx="5" fill="#FFFFFF" stroke="{TINTA}" stroke-width="1.3"/>')
    s.append(f'<path d="M10,{CAB} v-{CAB - 5} a5,5 0 0 1 5,-5 h{AN - 10} a5,5 0 0 1 5,5 v{CAB - 5} z" fill="{TINTA}"/>')
    s.append(f'<text x="19" y="16.5" font-size="12.5" font-weight="600" fill="#FFFFFF">planilla</text>')
    for k, col in enumerate(planilla):
        yy = CAB + FILA * k
        s.append(f'<rect x="11" y="{yy}" width="9" height="{FILA}" fill="{color[casa[col]]}"/>')
        s.append(f'<text x="27" y="{yy + 13.5}" font-size="11.5" fill="{TINTA}" '
                 f'font-family="Cascadia Mono, Consolas, monospace">{col}</text>')
    s.append(f'<text x="{AN + 50}" y="{alto_izq / 2}" font-size="26" fill="{SUAVE}" text-anchor="middle">→</text>')
    for t, (x, y) in pos.items():
        columnas, clave = tablas[t]
        h = CAB + FILA * len(columnas)
        s.append(f'<rect x="{x}" y="{y}" width="{ANT}" height="{h}" rx="5" fill="#FFFFFF" stroke="{color[t]}" stroke-width="1.6"/>')
        s.append(f'<path d="M{x},{y + CAB} v-{CAB - 5} a5,5 0 0 1 5,-5 h{ANT - 10} a5,5 0 0 1 5,5 v{CAB - 5} z" fill="{color[t]}"/>')
        s.append(f'<text x="{x + 9}" y="{y + 16.5}" font-size="12.5" font-weight="600" fill="#FFFFFF">{t}</text>')
        for k, col in enumerate(columnas):
            yy = y + CAB + FILA * k
            peso = ' font-weight="700"' if col in clave else ""
            s.append(f'<rect x="{x + 1}" y="{yy}" width="8" height="{FILA}" fill="{color[casa[col]]}"/>')
            s.append(f'<text x="{x + 15}" y="{yy + 13.5}" font-size="11.5" fill="{TINTA}"{peso} '
                     f'font-family="Cascadia Mono, Consolas, monospace">{col}</text>')
            if casa[col] != t:
                s.append(f'<text x="{x + ANT - 8}" y="{yy + 13.5}" font-size="10" fill="{color[casa[col]]}" '
                         f'text-anchor="end" font-weight="600">FK</text>')
    s.append(f'<text x="10" y="{alto - 12}" font-size="10" fill="{SUAVE}">Cada color es una tabla: la franja dice en '
             f'qué tabla vive el dato de esa columna. En negrita, la clave primaria; FK, la columna que vuelve a '
             f'conectar las tablas.</text>')
    s.append("</svg>")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(s), encoding="utf-8")


# ================================================================ resultados
SCRIPTS = {"ej": "u06_natacion.sql", "e01": "u06_e01_padel.sql", "e03": "u06_e03_lectura.sql",
           "e06": "u06_e06_guardias.sql", "e07": "u06_e07_futsal.sql", "e08": "u06_e08_preu.sql",
           "e10": "u06_e10_minimarket.sql"}
DATOS = {"ej": ["planilla"], "e01": ["reserva"], "e03": ["socio_planilla", "prefiere"], "e06": ["turno"],
         "e07": ["planilla"], "e08": ["tutoria"], "e10": ["producto", "boleta", "linea"]}
INTENTOS = {"ej": ["a_insercion", "a_insercion_bien", "a_actualizacion", "a_borrado"], "e01": ["cancha4"],
            "e07": ["doble"], "e08": ["t1", "t2", "b1", "b2"], "e10": ["corrige"]}
CONSULTAS = {"ej": ["origen", "dfs", "repetido", "filas", "reconstruir", "a_actualizacion_ver", "a_borrado_ver"],
             "e01": ["cancha2", "una_reserva"], "e03": ["like", "normal", "ranking"], "e06": ["a", "a_ejemplo", "b"],
             "e07": ["filas", "reconstruir"], "e08": ["t2_ver", "b1_ver"],
             "e10": ["sep_cobrado", "sep_hoy", "total_mal"],
             "caso": ["tamano", "muestra", "repetidos", "dfs", "a_actualizacion", "a_insercion", "a_borrado",
                      "contra_la_base", "reconstruir"]}


def resultados():
    R = {"frag": {}}
    for k, f in SCRIPTS.items():
        _, R[k] = correr(SQL / f)
        c0 = datos_antes_de_intentos(SQL / f)
        for t in DATOS.get(k, []):
            R["frag"][f"{k}:{t}"] = md_consulta(c0, f"SELECT * FROM {t}")
    con_caso = copia_del_caso()
    _, R["caso"] = correr(SQL / "u06_caso.sql", con_caso)
    for k, e in INTENTOS.items():
        R["frag"][f"intentos:{k}"] = md_intentos(R[k], e)
    for k, es in CONSULTAS.items():
        for e in es:
            r = R[k][e]
            assert r["ok"], (k, e, r.get("error"))
            R["frag"][f"filas:{k}:{e}"] = md_filas(r["cols"], r["filas"]) if r["filas"] else []

    # ---- ejemplo: el motor confirma cada paso
    E = {}
    E["claves"] = claves(NAT_R, NAT_F)
    E["fn"] = forma_normal(NAT_R, NAT_F, proyectada=False)
    E["viol"] = violaciones(NAT_R, NAT_F)
    E["fn_2fn"] = [forma_normal(sorted(t, key=NAT_R.index), NAT_F) for t in NAT_2FN]
    E["fn_3fn"] = [forma_normal(sorted(t, key=NAT_R.index), NAT_F) for t in NAT_3FN]
    sint, _ = sintesis_3fn(NAT_R, NAT_F)
    assert set(map(frozenset, NAT_3FN)) == set(sint), sint
    E["sin_perdida"] = sin_perdida(NAT_R, NAT_3FN, NAT_F)
    E["no_cons"] = no_conservadas(NAT_F, [set(t) for t in NAT_3FN])
    assert E["sin_perdida"] and not E["no_cons"] and E["claves"] == [frozenset({"rut", "curso"})]
    assert E["fn"] == "1FN" and E["fn_2fn"] == ["FNBC", "2FN", "FNBC"] and set(E["fn_3fn"]) == {"FNBC"}
    filas = dict(R["ej"]["filas"]["filas"])
    E["celdas_planilla"] = 10 * len(NAT_R)
    E["celdas_3fn"] = sum(filas[t] * n for t, n in [("tarifa", 2), ("profesor", 2), ("curso", 5), ("nadador", 2),
                                                     ("inscripcion", 2)])
    R["ej_motor"] = E
    # una mala descomposición en el ejemplo (para la sección de teoría): (rut, nadador, curso) y (curso... ) está bien;
    # la del gimnasio (teoría de FNBC)
    R["gim"] = {"claves": claves(GIM_R, GIM_F), "fn": forma_normal(GIM_R, GIM_F, False),
                "no_cons": no_conservadas(GIM_F, [{"instructor", "actividad"}, {"socio", "instructor"}]),
                "sin_perdida": sin_perdida(GIM_R, [{"instructor", "actividad"}, {"socio", "instructor"}], GIM_F)}
    assert R["gim"]["fn"] == "3FN" and R["gim"]["sin_perdida"] and len(R["gim"]["no_cons"]) == 1

    # ---- 6.2
    R["e02"] = {"A+": clausura({"A"}, E02_F), "CD+": clausura({"C", "D"}, E02_F),
                "BD+": clausura({"B", "D"}, E02_F), "claves": claves(E02_R, E02_F),
                "fn": forma_normal(E02_R, E02_F, False)}
    # ---- 6.4
    R["e04"] = {n: (forma_normal(r, f, False), claves(r, f)) for n, (r, f) in E04.items()}
    assert [v[0] for v in R["e04"].values()] == ["1FN", "2FN", "3FN", "FNBC"]
    # ---- 6.5
    s5, _ = sintesis_3fn(E05_R, E05_F)
    R["e05"] = {"claves": claves(E05_R, E05_F), "fn": forma_normal(E05_R, E05_F, False), "sintesis": s5,
                "fn_tablas": [forma_normal(sorted(t, key=E05_R.index), E05_F) for t in s5],
                "sin_perdida": sin_perdida(E05_R, s5, E05_F), "no_cons": no_conservadas(E05_F, s5)}
    # ---- 6.6
    R["e06m"] = {"A": sin_perdida(E06_R, [{"guardia", "dia"}, {"dia", "porteria"}], E06_F),
                 "B": sin_perdida(E06_R, [{"guardia", "dia"}, {"guardia", "porteria"}], E06_F)}
    assert R["e06m"] == {"A": False, "B": True}
    # ---- 6.7
    t7 = [{"cancha", "direccion"}, {"arbitro", "fono_arbitro"},
          {"fecha", "cancha", "local", "visita", "goles_local", "goles_visita", "arbitro"}]
    R["e07m"] = {"claves": claves(E07_R, E07_F), "fn": forma_normal(E07_R, E07_F, False),
                 "fn_tablas": [forma_normal(sorted(t, key=E07_R.index), E07_F) for t in t7],
                 "sin_perdida": sin_perdida(E07_R, t7, E07_F), "no_cons": no_conservadas(E07_F, t7)}
    assert R["e07m"]["sin_perdida"] and not R["e07m"]["no_cons"]
    # ---- 6.8
    tb = [{"tutor", "ramo"}, {"alumno", "tutor"}]
    R["e08m"] = {"claves": claves(E08_R, E08_F), "fn": forma_normal(E08_R, E08_F, False),
                 "sin_perdida": sin_perdida(E08_R, tb, E08_F), "no_cons": no_conservadas(E08_F, tb)}
    # ---- 6.9
    s9, Fm9 = sintesis_3fn(E09_R, E09_F)
    R["e09"] = {"claves": claves(E09_R, E09_F), "fn": forma_normal(E09_R, E09_F, False), "Fm": Fm9, "sintesis": s9,
                "fn_tablas": [forma_normal(sorted(t, key=E09_R.index), E09_F) for t in s9],
                "sin_perdida": sin_perdida(E09_R, s9, E09_F), "no_cons": no_conservadas(E09_F, s9),
                "quitadas": [(i, frozenset({a})) for i, d in E09_F for a in sorted(d)
                             if (i, frozenset({a})) not in Fm9]}
    # cada dependencia que sale del cubrimiento se deduce de las que quedan
    assert all(d <= clausura(i, Fm9) for i, d in R["e09"]["quitadas"])
    # ---- 6.10
    sep_c, sep_h = R["e10"]["sep_cobrado"]["filas"][0][0], R["e10"]["sep_hoy"]["filas"][0][0]
    R["e10_dif"] = sep_h - sep_c
    # ---- caso
    sC, FmC = sintesis_3fn(CASO_R, CASO_F)
    R["casoM"] = {"claves": claves(CASO_R, CASO_F), "fn": forma_normal(CASO_R, CASO_F, False), "sintesis": sC,
                  "viol": violaciones(CASO_R, CASO_F),
                  "sin_perdida": sin_perdida(CASO_R, sC, CASO_F), "no_cons": no_conservadas(CASO_F, sC)}
    assert set(sC) == {frozenset(v) for v in CASO_TABLAS.values()}, sC
    assert all(forma_normal(sorted(t, key=CASO_R.index), CASO_F) == "FNBC" for t in sC)
    # si alguien declara id_producto → precio_unit, la síntesis se lleva el precio al producto
    sX, _ = sintesis_3fn(CASO_R, CASO_F + DF("id_producto -> precio_unit"))
    R["casoM"]["con_trampa"] = sX
    fc = {r[0]: r for r in R["caso"]["contra_la_base"]["filas"]}
    R["caso_celdas_planilla"] = 212 * 16
    R["caso_celdas_tablas"] = sum(fc[t][1] * len(c) for t, c in CASO_TABLAS.items())
    return R


def figuras():
    casa_nat = {"rut": "nadador", "nadador": "nadador", "curso": "curso", "nivel": "tarifa", "horario": "curso",
                "piscina": "curso", "profesor": "profesor", "fono_profesor": "profesor", "mensualidad": "tarifa"}
    tablas_nat = {"inscripcion": (["rut", "curso"], {"rut", "curso"}),
                  "nadador": (["rut", "nadador"], {"rut"}),
                  "curso": (["curso", "nivel", "horario", "piscina", "profesor"], {"curso"}),
                  "profesor": (["profesor", "fono_profesor"], {"profesor"}),
                  "tarifa": (["nivel", "mensualidad"], {"nivel"})}
    casa_nat_i = dict(casa_nat)
    svg_descomposicion(NAT_R, tablas_nat, casa_nat_i, "Club de natación: de la planilla a cinco tablas",
                       FIG / "u06_natacion.svg")
    casa = {"id_pedido": "pedido", "fecha": "pedido", "estado": "pedido", "id_cliente": "cliente", "cliente": "cliente",
            "tipo": "cliente", "id_tienda": "tienda", "tienda": "tienda", "comuna": "tienda",
            "id_producto": "producto", "producto": "producto", "precio": "producto", "costo_var": "producto",
            "seg_estampado": "producto", "cantidad": "detalle_pedido", "precio_unit": "detalle_pedido"}
    tablas = {"detalle_pedido": (CASO_TABLAS["detalle_pedido"], {"id_pedido", "id_producto"}),
              "pedido": (CASO_TABLAS["pedido"], {"id_pedido"}),
              "producto": (CASO_TABLAS["producto"], {"id_producto"}),
              "cliente": (CASO_TABLAS["cliente"], {"id_cliente"}),
              "tienda": (CASO_TABLAS["tienda"], {"id_tienda"})}
    svg_descomposicion(CASO_R, tablas, casa, "Estampa Sur: la planilla de pedidos y sus cinco tablas",
                       FIG / "u06_estampa_sur.svg")


def cadena(R):
    m = caso()
    js = json.loads((AQUI / "caso_estampa_sur_bd.json").read_text(encoding="utf-8"))
    ok = R["caso"]["tamano"]["filas"][0][0] == js["tablas"]["detalle_pedido"] == len(m.generar()[2])
    fc = {r[0]: r for r in R["caso"]["contra_la_base"]["filas"]}
    ok &= all(fc[t][3] == 0 for t in fc)                                      # nada distinto de la base
    ok &= all(fc[t][1] == js["tablas"][t] for t in ["tienda", "producto", "pedido", "detalle_pedido"])
    ok &= fc["cliente"][2] - fc["cliente"][1] == js["u10_clientes_sin_pedidos"][0][0]
    ok &= R["caso"]["a_insercion"]["filas"][0][0] == js["u10_clientes_sin_pedidos"][0][0]
    ok &= R["caso"]["reconstruir"]["filas"][0] == (212, 0, 0)
    print("CADENA:", "OK, la planilla sale de la base del caso, su descomposición devuelve sus 5 tablas y los "
          "4 clientes sin pedidos son los de la unidad 10" if ok else "NO calza")
    return ok


def lineas_de_codigo():
    faltan = {}
    for f in list(SCRIPTS.values()) + ["u06_caso.sql"]:
        ls = (SQL / f).read_text(encoding="utf-8").splitlines()
        faltan[f] = [l for l in ls if l.strip() and not re.match(r"^INSERT INTO \w+ VALUES", l)]
    return faltan


def esperados(R):
    s = []
    for frag in R["frag"].values():
        s += frag
    E = R["ej_motor"]
    s += [f"{E['celdas_planilla']} celdas", f"{E['celdas_3fn']} celdas"]
    s += [fmt(R["caso_celdas_planilla"]) + " celdas", fmt(R["caso_celdas_tablas"]) + " celdas"]
    e2 = R["e02"]
    s += ["{" + ", ".join(sorted(e2["A+"])) + "}", "{" + ", ".join(sorted(e2["CD+"])) + "}"]
    s += [", ".join("{" + ", ".join(sorted(k)) + "}" for k in sorted(e2["claves"], key=sorted))]
    s += [txt(k, E05_R) for k in R["e05"]["claves"]] + [txt(t, E05_R) for t in R["e05"]["sintesis"]]
    s += [txt(t, E09_R) for t in R["e09"]["sintesis"]]
    s += [txt_df(i, d, E09_R) for i, d in R["e09"]["Fm"]]
    s += [txt(k, E07_R) for k in R["e07m"]["claves"]]
    s += [txt(k, CASO_R) for k in R["casoM"]["claves"]]
    s += [pesos(R["e10_dif"])]
    return s


def mostrar(R):
    E = R["ej_motor"]
    print("ejemplo · claves", [sorted(k) for k in E["claves"]], "· forma normal", E["fn"],
          "· 2FN", E["fn_2fn"], "· 3FN", E["fn_3fn"], "· celdas", E["celdas_planilla"], "→", E["celdas_3fn"])
    for i, d, t in E["viol"]:
        print("   violación", txt_df(i, d, NAT_R), t)
    g = R["gim"]
    print("gimnasio · claves", [sorted(k) for k in g["claves"]], g["fn"], "· no conservadas",
          [txt_df(i, d) for i, d in g["no_cons"]], "· sin pérdida", g["sin_perdida"])
    e2 = R["e02"]
    print("6.2 · A+", sorted(e2["A+"]), "CD+", sorted(e2["CD+"]), "BD+", sorted(e2["BD+"]), "claves",
          [sorted(k) for k in e2["claves"]], e2["fn"])
    print("6.4 ·", {n: (v[0], [sorted(k) for k in v[1]]) for n, v in R["e04"].items()})
    e5 = R["e05"]
    print("6.5 · claves", [txt(k, E05_R) for k in e5["claves"]], e5["fn"], "· síntesis",
          [txt(t, E05_R) for t in e5["sintesis"]], e5["fn_tablas"], e5["sin_perdida"], e5["no_cons"])
    print("6.6 ·", R["e06m"])
    e7 = R["e07m"]
    print("6.7 · claves", [txt(k, E07_R) for k in e7["claves"]], e7["fn"], e7["fn_tablas"])
    e8 = R["e08m"]
    print("6.8 · claves", [sorted(k) for k in e8["claves"]], e8["fn"], "sin pérdida", e8["sin_perdida"],
          "no conservadas", [txt_df(i, d) for i, d in e8["no_cons"]])
    e9 = R["e09"]
    print("6.9 · claves", [txt(k, E09_R) for k in e9["claves"]], e9["fn"])
    print("   cubrimiento mínimo:", [txt_df(i, d, E09_R) for i, d in e9["Fm"]])
    print("   quitadas:", [txt_df(i, d, E09_R) for i, d in e9["quitadas"]])
    print("   síntesis:", [txt(t, E09_R) for t in e9["sintesis"]], e9["fn_tablas"], e9["sin_perdida"], e9["no_cons"])
    print("6.10 · diferencia septiembre:", R["e10_dif"])
    c = R["casoM"]
    print("caso · claves", [txt(k, CASO_R) for k in c["claves"]], c["fn"], "· sin pérdida", c["sin_perdida"],
          "· no conservadas", c["no_cons"], "· celdas", R["caso_celdas_planilla"], "→", R["caso_celdas_tablas"])
    for i, d, t in c["viol"]:
        print("   violación", txt_df(i, d, CASO_R), t)
    print("   con la trampa id_producto → precio_unit:", [txt(t, CASO_R) for t in c["con_trampa"]])
    for k in list(SCRIPTS) + ["caso"]:
        for e, r in R[k].items():
            print(f"{k}:{e:<20} {u05.respuesta(r):<50} {r.get('filas', '') if r['ok'] else ''}")


if __name__ == "__main__":
    R = resultados()
    mostrar(R)
    figuras()
    print("FIGURAS: unidades/figuras/u06_natacion.svg y u06_estampa_sur.svg")
    if not cadena(R):
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
