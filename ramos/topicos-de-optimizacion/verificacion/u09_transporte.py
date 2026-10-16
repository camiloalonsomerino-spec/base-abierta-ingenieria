"""Unidad 9 · Problema de transporte y sus métodos. Recalcula todas las cifras; con --revisar las busca en el .md.

Este script:

1. implementa a mano los métodos de la unidad (esquina noroeste, costo mínimo, Vogel y MODI con su
   ciclo), con las reglas de desempate que fija el texto, y genera sus tablas en Markdown;
2. comprueba cada costo reducido de MODI por el camino del cruce de piedras (el costo del ciclo);
3. compara cada óptimo con el de scipy (HiGHS) y, en el caso, también con variables enteras (milp);
4. si hay CPLEX (oplrun), corre los modelos de `modelos/u09_*.mod` con herramientas/opl.py y exige
   que objetivo, envíos y costos reducidos coincidan; corre además el modelo con `dvar int+`;
5. compara la pieza del caso integrador con el script del caso (`CADENA: OK`);
6. con --revisar, busca cada cifra, cada línea de las tablas generadas y el código OPL en el .md.

    python u09_transporte.py            # imprime los resultados
    python u09_transporte.py --revisar  # además los busca en el .md
"""
from collections import deque
from pathlib import Path
import importlib.util, re, sys, tempfile

import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
MD = RAMO / "unidades" / "09-transporte.md"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402

TINTA, SUAVE, ACENTO, LINEA = "#2B2F33", "#5F656B", "#E2622A", "#D6D3CE"


# ---------------------------------------------------------------- formato chileno
def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x)


def signo(x):
    """Potencial u o v: con el signo menos tipográfico si es negativo."""
    return ("−" if x < 0 else "") + fmt(abs(x))


def firmado(x):
    """Costo reducido con signo: +285, −130 (signo menos tipográfico)."""
    return ("+" if x > 0 else ("−" if x < 0 else "")) + fmt(abs(x))


# ---------------------------------------------------------------- datos (originales; pasados por colisiones.py)
def caso_mod():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_red.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def datos_caso():
    m = caso_mod()
    import networkx as nx
    D = dict(nx.all_pairs_dijkstra_path_length(m.grafo(), weight="km"))
    o, d = list(m.OFERTA), list(m.DEMANDA_T)
    return {"orig": o, "dest": d, "a": [m.OFERTA[i] for i in o], "b": [m.DEMANDA_T[j] for j in d],
            "km": [[D[i][j] for j in d] for i in o], "C": [[95 * D[i][j] for j in d] for i in o]}


M_GRANDE = 100_000   # costo de una ruta prohibida en los métodos a mano (gran M)

EJ = {  # ejemplo resuelto: agua purificada, pesos por bidón
    "orig": ["Coihueco", "Bulnes", "Yungay"], "dest": ["Norte", "Poniente", "Oriente", "Sur"],
    "a": [312, 372, 228], "b": [216, 276, 180, 168],
    "C": [[428, 676, 552, 386], [524, 366, 458, 614], [662, 494, 336, 486]]}

E01 = {"orig": ["Hualqui", "Penco", "Tomé"], "dest": ["F1", "F2", "F3", "F4"], "a": [168, 114, 144],
       "b": [96, 132, 84, 150], "C": [[572, 671, 528, 770], [495, 429, 616, 682], [660, 517, 561, 473]]}
E02 = {"orig": ["H1", "H2", "H3"], "dest": ["Chillán", "San Carlos", "Coelemu"], "a": [70, 90, 60],
       "b": [80, 75, 65], "C": [[462, 671, 418], [605, 374, 517], [429, 572, 660]]}
E05 = {"orig": ["P1", "P2", "P3"], "dest": ["O1", "O2", "O3", "O4"], "a": [165, 220, 143],
       "b": [121, 154, 132, 121], "C": [[12, 9, 15, 11], [8, 13, 10, 14], [16, 11, 7, 9]]}
E06 = {"orig": ["Acopio A", "Acopio B"], "dest": ["S1", "S2", "S3"], "a": [132, 99], "b": [110, 99, 88],
       "C": [[341, 308, 385], [286, 363, 319]], "multa": [550, 495, 660]}
E07 = {"orig": ["B1", "B2", "B3"], "dest": ["T1", "T2", "T3"], "a": [110, 88, 132], "b": [110, 66, 154],
       "C": [[10, 8, 10], [7, 12, 4], [4, 11, 9]]}
E08 = {"orig": ["P1", "P2", "P3"], "dest": ["C1", "C2", "C3", "C4"], "a": [90, 75, 85], "b": [60, 70, 55, 65],
       "C": [[30, 25, 40, 46], [39, 37, 34, None], [29, 38, 36, 37]], "piso": ((0, 2), 15)}
E09 = {"orig": ["Huerto 1", "Huerto 2", "Huerto 3"], "dest": ["Planta A", "Planta B", "Planta C"],
       "a": [80, 70, 90], "b": [70, 85, 60], "G": [[70, 62, 46], [70, 70, 68], [None, 49, 40]]}
E10 = {"orig": ["Q1", "Q2", "Q3"], "dest": ["D1", "D2", "D3", "D4"], "a": [154, 110, 132],
       "b": [99, 121, 88, 88], "C": [[41, 59, 59, 54], [45, 73, 49, 64], [60, 71, 49, 58]]}


# ---------------------------------------------------------------- métodos de solución inicial
def noroeste(a, b):
    """Esquina noroeste. Si fila y columna se agotan juntas, se tacha la fila (salvo la última) y la
    columna queda con 0: la celda de abajo recibe un 0 básico."""
    a, b = list(a), list(b); m, n = len(a), len(b); i = j = 0; base = {}; pasos = []
    while i < m and j < n:
        q = min(a[i], b[j]); base[(i, j)] = q; a[i] -= q; b[j] -= q
        if a[i] == 0 and i < m - 1:
            pasos.append((i, j, q, ("f", i))); i += 1
        else:
            pasos.append((i, j, q, ("c", j))); j += 1
    return base, pasos


def _repartir(C, a, b, elegir):
    a, b = list(a), list(b); m, n = len(a), len(b)
    R, K = list(range(m)), list(range(n)); base = {}; pasos = []
    while R and K:
        i, j, info = elegir(C, a, b, R, K)
        q = min(a[i], b[j]); base[(i, j)] = q; a[i] -= q; b[j] -= q
        if a[i] == 0 and (b[j] != 0 or len(R) > 1):
            R.remove(i); tacha = ("f", i)
        else:
            K.remove(j); tacha = ("c", j)
        pasos.append((i, j, q, tacha, info))
    return base, pasos


def _elegir_min(C, a, b, R, K):
    """Menor costo; empate: la celda que admite más; luego la primera (fila, columna)."""
    _, _, i, j = min((C[i][j], -min(a[i], b[j]), i, j) for i in R for j in K)
    return i, j, None


def _elegir_vogel(C, a, b, R, K):
    """Mayor penalización (diferencia entre los dos menores costos de la línea); empate: la línea con el
    menor costo; luego filas antes que columnas, en orden. Con una sola fila o columna activa, el resto
    se asigna por menor costo."""
    if len(R) == 1 or len(K) == 1:
        i, j, _ = _elegir_min(C, a, b, R, K)
        return i, j, {"forzada": True}
    pen, cand = {}, []
    for i in R:
        cs = sorted(C[i][j] for j in K); pen[("f", i)] = cs[1] - cs[0]; cand.append((-(cs[1] - cs[0]), cs[0], 0, i))
    for j in K:
        cs = sorted(C[i][j] for i in R); pen[("c", j)] = cs[1] - cs[0]; cand.append((-(cs[1] - cs[0]), cs[0], 1, j))
    _, _, tipo, k = min(cand)
    if tipo == 0:
        i, j = k, min(K, key=lambda jj: (C[k][jj], jj))
    else:
        i, j = min(R, key=lambda ii: (C[ii][k], ii)), k
    return i, j, {"forzada": False, "pen": pen, "linea": ("f" if tipo == 0 else "c", k)}


def costo_minimo(C, a, b):
    return _repartir(C, a, b, _elegir_min)


def vogel(C, a, b):
    return _repartir(C, a, b, _elegir_vogel)


def costo(C, base):
    return sum(C[i][j] * q for (i, j), q in base.items())


# ---------------------------------------------------------------- MODI y cruce de piedras
def potenciales(C, base, m, n):
    u, v = [None] * m, [None] * n; u[0] = 0
    cambio = True
    while cambio:
        cambio = False
        for (i, j) in sorted(base):
            if u[i] is not None and v[j] is None:
                v[j] = C[i][j] - u[i]; cambio = True
            elif v[j] is not None and u[i] is None:
                u[i] = C[i][j] - v[j]; cambio = True
    assert None not in u and None not in v, "la base no es un árbol: faltan ceros básicos"
    return u, v


def ciclo(base, entra):
    """El único ciclo que forma la celda que entra con las básicas. Signos: + − + − ..."""
    i0, j0 = entra
    ady = {}
    for (i, j) in base:
        ady.setdefault(("f", i), []).append(("c", j)); ady.setdefault(("c", j), []).append(("f", i))
    ini, fin = ("c", j0), ("f", i0)
    prev = {ini: None}; cola = deque([ini])
    while cola:
        x = cola.popleft()
        for y in sorted(ady.get(x, [])):
            if y not in prev:
                prev[y] = x; cola.append(y)
    camino, x = [], fin
    while x is not None:
        camino.append(x); x = prev[x]
    camino = camino[::-1]
    celdas = [entra]
    for p, q in zip(camino, camino[1:]):
        celdas.append((q[1], p[1]) if p[0] == "c" else (p[1], q[1]))
    return celdas


def piedras(C, base, celda):
    cic = ciclo(base, celda)
    return sum((1 if k % 2 == 0 else -1) * C[i][j] for k, (i, j) in enumerate(cic))


def modi(C, base):
    m, n = len(C), len(C[0]); base = dict(base); its = []
    while True:
        u, v = potenciales(C, base, m, n)
        red = {(i, j): C[i][j] - u[i] - v[j] for i in range(m) for j in range(n) if (i, j) not in base}
        for celda, r in red.items():          # segundo camino: el costo del ciclo es el costo reducido
            assert piedras(C, base, celda) == r, (celda, r)
        it = {"base": dict(base), "u": u, "v": v, "red": red, "costo": costo(C, base)}
        its.append(it)
        neg = [(r, i, j) for (i, j), r in red.items() if r < 0]
        if not neg:
            return its
        r, i, j = min(neg)
        cic = ciclo(base, (i, j))
        th = min(base[c] for c in cic[1::2])
        sale = min(c for c in cic[1::2] if base[c] == th)
        for k, c in enumerate(cic):
            base[c] = th if k == 0 else base[c] + (th if k % 2 == 0 else -th)
        del base[sale]
        it.update(entra=(i, j), r_entra=r, ciclo=cic, theta=th, sale=sale, baja=-r * th)


# ---------------------------------------------------------------- programación lineal (segundo camino)
def lp(C, a, b, prohibidas=(), sentido="min", pisos=None, entero=False):
    """Transporte con oferta <= y demanda >= (al maximizar, demanda ==). Devuelve objetivo y envíos."""
    m, n = len(a), len(b)
    c = np.array([C[i][j] if C[i][j] is not None else 0 for i in range(m) for j in range(n)], float)
    if sentido == "max":
        c = -c
    A_of = [[1 if k // n == i else 0 for k in range(m * n)] for i in range(m)]
    A_de = [[1 if k % n == j else 0 for k in range(m * n)] for j in range(n)]
    lo = np.zeros(m * n); hi = np.full(m * n, np.inf)
    for (i, j) in prohibidas:
        hi[i * n + j] = 0
    for (i, j), q in (pisos or {}).items():
        lo[i * n + j] = q
    techo_de = list(b) if sentido == "max" else [np.inf] * n
    if entero:
        r = milp(c, constraints=[LinearConstraint(np.array(A_of, float), ub=a),
                                 LinearConstraint(np.array(A_de, float), lb=b, ub=techo_de)],
                 integrality=np.ones(m * n), bounds=Bounds(lo, hi))
    else:
        if sentido == "max":
            r = linprog(c, A_ub=A_of, b_ub=a, A_eq=A_de, b_eq=b, bounds=list(zip(lo, hi)), method="highs")
        else:
            r = linprog(c, A_ub=A_of + [[-v for v in f] for f in A_de], b_ub=list(a) + [-x for x in b],
                        bounds=list(zip(lo, hi)), method="highs")
    x = r.x
    z = float(r.fun) * (-1 if sentido == "max" else 1)
    return z, [[float(x[i * n + j]) for j in range(n)] for i in range(m)]


def balancear(d, costo_fict=None):
    """Agrega el destino o el origen ficticio. Devuelve orig, dest, a, b, C."""
    o, ds, a, b, C = list(d["orig"]), list(d["dest"]), list(d["a"]), list(d["b"]), [r[:] for r in d["C"]]
    C = [[M_GRANDE if x is None else x for x in r] for r in C]
    if sum(a) > sum(b):
        ds.append("Ficticio"); b.append(sum(a) - sum(b)); C = [r + [0] for r in C]
    elif sum(b) > sum(a):
        o.append("Ficticio"); a.append(sum(b) - sum(a)); C.append(costo_fict or [0] * len(b))
    return o, ds, a, b, C


# ---------------------------------------------------------------- tablas en Markdown
def nom_linea(t, o, d):
    return o[t[1]] if t[0] == "f" else d[t[1]]


def tabla_costos(o, d, C, a, b, cab="Oferta"):
    s = ["| | " + " | ".join(d) + f" | {cab} |", "|---" * (len(d) + 2) + "|"]
    for i, f in enumerate(C):
        s.append(f"| {o[i]} | " + " | ".join("—" if x is None or x >= M_GRANDE else fmt(x) for x in f) + f" | {fmt(a[i])} |")
    s.append("| Demanda | " + " | ".join(fmt(x) for x in b) + " | |")
    return "\n".join(s)


def tabla_asig(o, d, base, a, b):
    s = ["| | " + " | ".join(d) + " | Oferta |", "|---" * (len(d) + 2) + "|"]
    for i in range(len(o)):
        cel = []
        for j in range(len(d)):
            q = base.get((i, j))
            cel.append("·" if q is None else ("0 (básica)" if q == 0 else fmt(q)))
        s.append(f"| {o[i]} | " + " | ".join(cel) + f" | {fmt(a[i])} |")
    s.append("| Demanda | " + " | ".join(fmt(x) for x in b) + " | |")
    return "\n".join(s)


def tabla_pasos(o, d, C, pasos, metodo):
    if metodo == "vogel":
        s = ["| Paso | Penalizaciones de fila | Penalizaciones de columna | Línea elegida | Celda (costo) | Envío | Se tacha |",
             "|---|---|---|---|---|---|---|"]
    else:
        s = ["| Paso | Celda (costo) | Envío | Se tacha |", "|---|---|---|---|"]
    for k, p in enumerate(pasos, 1):
        i, j, q, tacha = p[:4]
        cel = f"{o[i]}–{d[j]} ({fmt(C[i][j])})"
        tch = ("fila " if tacha[0] == "f" else "columna ") + nom_linea(tacha, o, d)
        if metodo == "vogel":
            info = p[4]
            if info["forzada"]:
                s.append(f"| {k} | — | — | queda una sola línea | {cel} | {fmt(q)} | {tch} |")
            else:
                pf = ", ".join(f"{o[t[1]]} {fmt(v)}" for t, v in info["pen"].items() if t[0] == "f")
                pc = ", ".join(f"{d[t[1]]} {fmt(v)}" for t, v in info["pen"].items() if t[0] == "c")
                li = nom_linea(info["linea"], o, d) + f" ({fmt(info['pen'][info['linea']])})"
                s.append(f"| {k} | {pf} | {pc} | {li} | {cel} | {fmt(q)} | {tch} |")
        else:
            s.append(f"| {k} | {cel} | {fmt(q)} | {tch} |")
    return "\n".join(s)


def tabla_modi(o, d, it, g=False):
    """Con g=True la tabla se muestra en ganancias (el problema se resolvió con costo = −ganancia)."""
    sg = -1 if g else 1
    s = ["| | " + " | ".join(d) + " | $u_i$ |", "|---" * (len(d) + 2) + "|"]
    for i in range(len(o)):
        cel = []
        for j in range(len(d)):
            if (i, j) in it["base"]:
                cel.append(f"**{fmt(it['base'][(i, j)])}**")
            elif abs(it["red"][(i, j)]) >= M_GRANDE / 2:
                cel.append("—")
            else:
                cel.append(f"({firmado(sg * it['red'][(i, j)])})")
        s.append(f"| {o[i]} | " + " | ".join(cel) + f" | {signo(sg * it['u'][i])} |")
    s.append("| $v_j$ | " + " | ".join(signo(sg * x) for x in it["v"]) + " | |")
    return "\n".join(s)


def frase_modi(o, d, it, g=False):
    sg = -1 if g else 1
    if "entra" not in it:
        if g:
            return (f"Todas las ganancias reducidas son menores o iguales a cero: **óptimo**, con ganancia "
                    f"{fmt(-it['costo'])}.")
        return (f"Todos los costos reducidos son mayores o iguales a cero: **óptimo**, con costo "
                f"{fmt(it['costo'])}.")
    cel = lambda c: f"{o[c[0]]}–{d[c[1]]}"
    cic = " → ".join(f"{cel(c)} ({'+' if k % 2 == 0 else '−'})" for k, c in enumerate(it["ciclo"]))
    que = "ganancia reducida" if g else "costo reducido"
    verbo = "La ganancia sube" if g else "El costo baja"
    return (f"Entra {cel(it['entra'])} ({que} {firmado(sg * it['r_entra'])}). Ciclo: {cic}. "
            f"θ = {fmt(it['theta'])}; sale {cel(it['sale'])}. {verbo} "
            f"{fmt(it['theta'])} × {fmt(-it['r_entra'])} = {fmt(it['baja'])}: de {fmt(sg * it['costo'])} "
            f"a {fmt(sg * (it['costo'] - it['baja']))}.")


def bloque_modi(o, d, its, g=False):
    trozos = []
    for k, it in enumerate(its):
        cab = f"ganancia {fmt(-it['costo'])}" if g else f"costo {fmt(it['costo'])}"
        trozos += [f"*Iteración {k}* ({cab}).", tabla_modi(o, d, it, g), frase_modi(o, d, it, g)]
    return "\n\n".join(trozos)


# ---------------------------------------------------------------- cálculo de la unidad
def resolver_todo(o, d, a, b, C):
    no, pno = noroeste(a, b); cm, pcm = costo_minimo(C, a, b); vo, pvo = vogel(C, a, b)
    R = {"orig": o, "dest": d, "a": a, "b": b, "C": C,
         "no": no, "pno": pno, "cm": cm, "pcm": pcm, "vo": vo, "pvo": pvo,
         "c_no": costo(C, no), "c_cm": costo(C, cm), "c_vo": costo(C, vo),
         "modi_no": modi(C, no), "modi_cm": modi(C, cm), "modi_vo": modi(C, vo)}
    finales = {R["modi_no"][-1]["costo"], R["modi_cm"][-1]["costo"], R["modi_vo"][-1]["costo"]}
    assert len(finales) == 1
    R["opt"] = finales.pop()
    return R


def resultados():
    R = {}
    # caso
    dc = datos_caso()
    R["caso"] = resolver_todo(dc["orig"], dc["dest"], dc["a"], dc["b"], dc["C"])
    R["caso"]["km"] = dc["km"]
    z, x = lp(dc["C"], dc["a"], dc["b"]); zi, xi = lp(dc["C"], dc["a"], dc["b"], entero=True)
    assert abs(z - R["caso"]["opt"]) < 1e-6 and abs(zi - z) < 1e-6
    R["caso"]["lp_x"] = x
    # ejemplo (sobra oferta: destino ficticio)
    o, ds, a, b, C = balancear(EJ)
    R["ej"] = resolver_todo(o, ds, a, b, C)
    z, _ = lp(EJ["C"], EJ["a"], EJ["b"]); assert abs(z - R["ej"]["opt"]) < 1e-6
    R["ej"]["sobra"] = sum(EJ["a"]) - sum(EJ["b"])
    # 9.1 (falta oferta: origen ficticio de costo 0)
    o, ds, a, b, C = balancear(E01)
    r = resolver_todo(o, ds, a, b, C); z, _ = lp(C, a, b); assert abs(z - r["opt"]) < 1e-6
    r["falta"] = sum(E01["b"]) - sum(E01["a"]); r["basicas"] = len(a) + len(b) - 1
    R["e01"] = r
    # 9.2 a 9.4
    r = resolver_todo(E02["orig"], E02["dest"], E02["a"], E02["b"], E02["C"])
    z, _ = lp(E02["C"], E02["a"], E02["b"]); assert abs(z - r["opt"]) < 1e-6
    R["e02"] = r
    # 9.5
    r = resolver_todo(E05["orig"], E05["dest"], E05["a"], E05["b"], E05["C"])
    z, _ = lp(E05["C"], E05["a"], E05["b"]); assert abs(z - r["opt"]) < 1e-6
    R["e05"] = r
    # 9.6 (falta oferta: el ficticio cobra la multa de cada sector)
    o, ds, a, b, C = balancear(E06, costo_fict=E06["multa"])
    r = resolver_todo(o, ds, a, b, C); z, _ = lp(C, a, b); assert abs(z - r["opt"]) < 1e-6
    r["falta"] = sum(E06["b"]) - sum(E06["a"])
    fin = r["modi_vo"][-1]["base"]
    r["sin_atender"] = {ds[j]: q for (i, j), q in fin.items() if o[i] == "Ficticio" and q > 0}
    r["multas"] = sum(C[i][j] * q for (i, j), q in fin.items() if o[i] == "Ficticio")
    r["flete"] = r["opt"] - r["multas"]
    R["e06"] = r
    # 9.7 (degenerada)
    r = resolver_todo(E07["orig"], E07["dest"], E07["a"], E07["b"], E07["C"])
    z, _ = lp(E07["C"], E07["a"], E07["b"]); assert abs(z - r["opt"]) < 1e-6
    assert 0 in r["no"].values() and r["modi_no"][0]["theta"] == 0
    R["e07"] = r
    # 9.8 (ruta prohibida y envío mínimo)
    o, ds, a, b, C = balancear(E08)
    r = resolver_todo(o, ds, a, b, C)
    z, _ = lp(E08["C"], a, b, prohibidas=[(1, 3)]); assert abs(z - r["opt"]) < 1e-6
    (pi, pj), q = E08["piso"]
    zp, xp = lp(E08["C"], a, b, prohibidas=[(1, 3)], pisos={(pi, pj): q})
    r["red_piso"] = r["modi_vo"][-1]["red"][(pi, pj)]
    assert abs(zp - z - q * r["red_piso"]) < 1e-6, "el envío mínimo cambia la base: la lectura no vale"
    r["z_piso"] = zp; r["sube_piso"] = zp - z
    cic = ciclo(r["modi_vo"][-1]["base"], (pi, pj))
    r["theta_piso"] = min(r["modi_vo"][-1]["base"][c] for c in cic[1::2])
    zq, _ = lp(E08["C"], a, b, prohibidas=[(1, 3)], pisos={(pi, pj): r["theta_piso"] + 5})
    assert zq - z > (r["theta_piso"] + 5) * r["red_piso"] + 1e-6   # pasado θ, cada unidad cuesta más
    r["c_cm_real"] = r["c_cm"]; r["m_cm"] = r["cm"].get((1, 3), 0)
    R["e08"] = r
    # 9.9 (maximizar ganancia, ruta prohibida, sobra oferta)
    G = E09["G"]
    Cmin = [[M_GRANDE if g is None else -g for g in fila] for fila in G]
    o, ds, a, b, Cb = balancear({"orig": E09["orig"], "dest": E09["dest"], "a": E09["a"], "b": E09["b"], "C": Cmin})
    r = resolver_todo(o, ds, a, b, Cb)
    zg, xg = lp(G, a[:3], b[:3], prohibidas=[(2, 0)], sentido="max")
    assert abs(zg + r["opt"]) < 1e-6
    r["ganancia"] = -r["opt"]; r["x"] = xg
    fin = r["modi_vo"][-1]
    # en ganancias: g = u + v en las básicas; se corre la constante para que el ficticio valga 0
    k = fin["v"][-1]
    r["u_g"] = [-x - k for x in fin["u"]]; r["v_g"] = [-x + k for x in fin["v"]][:-1]
    for i in range(3):                      # segundo camino: una tonelada más en cada huerto
        a2 = list(E09["a"]); a2[i] += 1
        z2, _ = lp(G, a2, E09["b"], prohibidas=[(2, 0)], sentido="max")
        assert abs(z2 - zg - r["u_g"][i]) < 1e-6, (i, z2 - zg, r["u_g"][i])
    R["e09"] = r
    # 9.10 (óptimo alternativo)
    r = resolver_todo(E10["orig"], E10["dest"], E10["a"], E10["b"], E10["C"])
    z, _ = lp(E10["C"], E10["a"], E10["b"]); assert abs(z - r["opt"]) < 1e-6
    fin = r["modi_vo"][-1]
    ceros = [c for c, v in fin["red"].items() if v == 0]
    assert len(ceros) == 1
    alt = dict(fin["base"]); cic = ciclo(alt, ceros[0]); th = min(alt[c] for c in cic[1::2])
    sale = min(c for c in cic[1::2] if alt[c] == th)
    for k, c in enumerate(cic):
        alt[c] = th if k == 0 else alt[c] + (th if k % 2 == 0 else -th)
    del alt[sale]
    assert costo(E10["C"], alt) == r["opt"]
    r.update(cero=ceros[0], ciclo_alt=cic, theta_alt=th, alt=alt, sale_alt=sale)
    Cb = [f[:] for f in E10["C"]]; Cb[ceros[0][0]][ceros[0][1]] -= 1
    zb, _ = lp(Cb, E10["a"], E10["b"]); r["baja1"] = r["opt"] - zb
    assert abs(r["baja1"] - th) < 1e-6
    Cs = [f[:] for f in E10["C"]]; Cs[ceros[0][0]][ceros[0][1]] += 1
    zs, _ = lp(Cs, E10["a"], E10["b"]); assert abs(zs - r["opt"]) < 1e-6
    R["e10"] = r
    return R


# ---------------------------------------------------------------- OPL
def _dat(nombre):
    return MODELOS / nombre


MODELOS_U9 = {  # clave de R: (mod, dat, ¿comparar envíos y costos reducidos?)
    "caso": ("u09_transporte.mod", "u09_estampa.dat", True),
    "ej": ("u09_transporte.mod", "u09_bidones.dat", True),
    "e06": ("u09_transporte.mod", "u09_e06_lena.dat", True),
    "e08": ("u09_transporte.mod", "u09_e08_prohibida.dat", True),
    "e09": ("u09_e09_ganancia.mod", "u09_e09_ganancia.dat", True),
}
SALIDA_CASO = []


def comparar_con_opl(R):
    corridos = 0
    for k, (mod, dat, todo) in MODELOS_U9.items():
        r = correr(MODELOS / mod, _dat(dat))
        if r is None:
            print("OPL: oplrun no está instalado; se comparan solo las cifras de Python")
            return None
        assert r["codigo"] == 0 and r["objetivo"] is not None, (k, r["salida"][-400:])
        X = R[k]
        z = X["ganancia"] if k == "e09" else X["opt"]
        assert abs(r["objetivo"] - z) < 1e-6, (k, r["objetivo"], z)
        fin = X["modi_vo"][-1]
        o, d = X["orig"], X["dest"]
        vistos = 0
        for (i, j), q in fin["base"].items():
            if o[i] == "Ficticio" or d[j] == "Ficticio":
                continue
            clave = f"x[{o[i]}][{d[j]}]"
            assert abs(r["valores"].get(clave, 0) - q) < 1e-6, (k, clave, r["valores"].get(clave), q)
            vistos += 1
        for (i, j), red in fin["red"].items():
            if o[i] == "Ficticio" or d[j] == "Ficticio" or red >= M_GRANDE / 2:
                continue
            clave = f"cr[{o[i]}][{d[j]}]"
            if clave in r["valores"]:
                esperado = -red if k == "e09" else red
                assert abs(r["valores"][clave] - esperado) < 1e-6, (k, clave, r["valores"][clave], esperado)
                vistos += 1
        assert vistos >= 4, (k, vistos)
        if k == "caso":
            SALIDA_CASO[:] = [l.strip() for l in r["salida"].splitlines() if re.match(r"^[\w\[\]]+ = \S+$", l.strip())]
        corridos += 1
    # el mismo modelo con variables enteras da el mismo costo (y OPL ya no entrega duales)
    texto = (MODELOS / "u09_transporte.mod").read_text(encoding="utf-8").replace("dvar float+", "dvar int+")
    texto = "\n".join(l for l in texto.splitlines() if ".dual" not in l and "reducedCost" not in l)
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "u09_entero.mod"; f.write_text(texto, encoding="utf-8")
        r = correr(f, _dat("u09_estampa.dat"))
    assert abs(r["objetivo"] - R["caso"]["opt"]) < 1e-6
    print(f"OPL: {corridos} modelos corridos con oplrun; objetivo, envíos y costos reducidos coinciden con MODI;"
          f" con dvar int+ el caso da el mismo costo")
    return True


# ---------------------------------------------------------------- figura
def figura(R):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "path"})
    X = R["caso"]; fin = X["modi_vo"][-1]["base"]
    yo = {0: 2.6, 1: 0.9}; yd = {0: 3.4, 1: 2.3, 2: 1.2, 3: 0.1}
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    for i in range(2):
        for j in range(4):
            q = fin.get((i, j), 0)
            ax.annotate("", xy=(3.6, yd[j]), xytext=(1.0, yo[i]),
                        arrowprops=dict(arrowstyle="-|>", lw=2.4 if q else 0.8, color=ACENTO if q else LINEA,
                                        ls="-" if q else ":", shrinkA=6, shrinkB=6))
            fr = 0.62 if q else 0.34
            xm, ym = 1.0 + fr * 2.6, yo[i] + fr * (yd[j] - yo[i])
            etiqueta = f"{fmt(q)} cajas · ${fmt(X['C'][i][j])}" if q else f"${fmt(X['C'][i][j])}"
            ax.text(xm, ym, etiqueta, fontsize=8.2 if q else 7.6, ha="center", va="center",
                    color=TINTA if q else SUAVE, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    for i, nom in enumerate(X["orig"]):
        ax.text(0.95, yo[i], f"{nom}\noferta {X['a'][i]}", ha="right", va="center", fontsize=9.5, color=TINTA,
                bbox=dict(boxstyle="round,pad=0.35", fc="#F2F1EF", ec=SUAVE))
    for j, nom in enumerate(X["dest"]):
        ax.text(3.65, yd[j], f"{nom}\npide {X['b'][j]}", ha="left", va="center", fontsize=9.5, color=TINTA,
                bbox=dict(boxstyle="round,pad=0.35", fc="#F2F1EF", ec=SUAVE))
    ax.set_xlim(-0.2, 4.6); ax.set_ylim(-0.4, 3.9); ax.axis("off")
    fig.tight_layout()
    carpeta = RAMO / "unidades" / "figuras"; carpeta.mkdir(parents=True, exist_ok=True)
    fig.savefig(carpeta / "u09_red_transporte.svg", metadata={"Date": None})
    plt.close(fig)


# ---------------------------------------------------------------- tablas que el .md tiene que traer
def tablas(R):
    T = {}
    for k in ["caso", "ej", "e01", "e02", "e05", "e06", "e07", "e08", "e09", "e10"]:
        X = R[k]; o, d = X["orig"], X["dest"]
        T[f"{k}_costos"] = tabla_costos(o, d, X["C"], X["a"], X["b"])
        for met in ["no", "cm", "vo"]:
            T[f"{k}_{met}"] = tabla_asig(o, d, X[met], X["a"], X["b"])
            T[f"{k}_p{met}"] = tabla_pasos(o, d, X["C"], X["p" + met], {"no": "no", "cm": "cm", "vo": "vogel"}[met])
            T[f"{k}_modi_{met}"] = bloque_modi(o, d, X["modi_" + met], g=(k == "e09"))
        T[f"{k}_final"] = tabla_asig(o, d, X["modi_vo"][-1]["base"], X["a"], X["b"])
    for k, D in [("ej", EJ), ("e01", E01), ("e06", E06)]:   # enunciados: sin el ficticio
        T[f"{k}_dato"] = tabla_costos(D["orig"], D["dest"], D["C"], D["a"], D["b"])
    X = R["e10"]
    T["e10_alt"] = tabla_asig(X["orig"], X["dest"], X["alt"], X["a"], X["b"])
    X = R["e09"]
    T["e09_g"] = tabla_costos(E09["orig"], E09["dest"], E09["G"], E09["a"], E09["b"])
    return T


USADAS = {  # tablas que el .md muestra (las demás quedan para el tutor)
    "caso_costos", "caso_no", "caso_pno", "caso_cm", "caso_pcm", "caso_vo", "caso_pvo", "caso_modi_no",
    "caso_final", "ej_dato", "e01_dato", "e06_dato",
    "ej_costos", "ej_no", "ej_cm", "ej_pcm", "ej_vo", "ej_pvo", "ej_modi_cm",
    "e01_costos", "e01_no", "e02_costos", "e02_cm", "e02_pcm", "e02_vo", "e02_pvo", "e02_modi_cm",
    "e05_costos", "e05_no", "e05_modi_no", "e06_costos", "e06_vo", "e06_pvo", "e06_modi_vo",
    "e07_costos", "e07_no", "e07_pno", "e07_modi_no", "e08_costos", "e08_cm", "e08_vo",
    "e08_modi_vo", "e09_g", "e09_vo", "e09_modi_vo", "e10_costos", "e10_vo", "e10_modi_vo", "e10_alt",
}


def esperados(R):
    s = []
    X = R["caso"]
    s += [pesos(X["c_no"]), pesos(X["c_cm"]), pesos(X["c_vo"]), pesos(X["opt"]), "586.340", "$95",
          f"{len(X['modi_no']) - 1} iteraciones", "536"]
    s += [fmt(x) for f in X["C"] for x in f]
    X = R["ej"]
    s += [pesos(X["c_no"]), pesos(X["c_cm"]), pesos(X["c_vo"]), pesos(X["opt"]), fmt(X["sobra"]) + " bidones"]
    X = R["e01"]; s += [fmt(X["falta"]) + " sacos", pesos(X["c_no"]), pesos(X["opt"]), f"{X['basicas']} variables básicas"]
    X = R["e02"]; s += [pesos(X["c_cm"]), pesos(X["c_vo"]), pesos(X["opt"])]
    X = R["e05"]; s += [fmt(X["c_no"]), fmt(X["opt"]), f"{len(X['modi_no']) - 1} iteraciones"]
    X = R["e06"]; s += [pesos(X["opt"]), pesos(X["multas"]), pesos(X["flete"]), fmt(X["falta"]) + " sacos"]
    s += [f"{fmt(q)} sacos sin entregar" for q in X["sin_atender"].values()]
    X = R["e07"]; s += [fmt(X["c_no"]), fmt(X["opt"])]
    X = R["e08"]; s += [fmt(X["c_cm"]), fmt(X["opt"]), fmt(X["red_piso"]), fmt(X["sube_piso"]), fmt(X["z_piso"]), fmt(X["theta_piso"]) + " unidades"]
    X = R["e09"]; s += [fmt(X["ganancia"])] + [fmt(v) for v in X["u_g"] + X["v_g"] if v]
    s += [fmt(-X["c_vo"]), fmt(-X["c_no"])]
    X = R["e10"]; s += [fmt(X["opt"]), fmt(X["theta_alt"]), fmt(X["baja1"])]
    # cifras derivadas que el texto comenta
    X = R["ej"]
    s += [f"La oferta es {fmt(sum(EJ['a']))} y la demanda {fmt(sum(EJ['b']))}", pesos(X["c_vo"] - X["opt"]),
          f"penalización de {fmt(X['pvo'][3][4]['pen'][('f', 2)])}"]
    X = R["e01"]; s += [f"Oferta {fmt(sum(E01['a']))}, demanda {fmt(sum(E01['b']))}",
                        f"un {round(100 * (X['c_no'] / X['opt'] - 1))} % arriba"]
    X = R["e02"]; it = X["modi_cm"][0]
    s += [r"\$" + f"{fmt(X['c_cm'] - X['c_vo'])} menos", f"penalización {fmt(X['pvo'][0][4]['pen'][('c', 1)])}",
          f"H3 ({fmt(X['pvo'][1][4]['pen'][('f', 2)])})",
          f"costo reducido {firmado(it['r_entra'])}", f"Entran {fmt(it['theta'])}",
          "$+517 - 418 + 462 - 605 = -44$"]
    assert 517 - 418 + 462 - 605 == it["r_entra"] == piedras(X["C"], it["base"], it["entra"])
    X = R["e05"]; s += [f"ahorro de {fmt(X['c_no'] - X['opt'])} mil pesos"]
    s += [f"Oferta {fmt(sum(E06['a']))}, demanda {fmt(sum(E06['b']))}"]
    X = R["e09"]; s += [f"Oferta {fmt(sum(E09['a']))}, pedidos {fmt(sum(E09['b']))}", f"$k = {fmt(-R['e09']['modi_vo'][-1]['v'][-1])}$"]
    return s


def codigo_en_md(md):
    faltan = []
    for f in ["u09_transporte.mod", "u09_estampa.dat"]:
        for linea in (MODELOS / f).read_text(encoding="utf-8").splitlines():
            if linea.strip() and linea.rstrip() not in md:
                faltan.append(f"{f}: {linea.strip()}")
    return faltan


def cadena(R):
    C = caso_mod().calcular()["u9"]
    X = R["caso"]; fin = X["modi_vo"][-1]["base"]
    ok = abs(C["costo_total"] - X["opt"]) < 1e-6
    ok &= all(C["costos"][i][j] == X["C"][i][j] for i in range(2) for j in range(4))
    ok &= all(abs(C["envios"][i][j] - fin.get((i, j), 0)) < 1e-6 for i in range(2) for j in range(4))
    ok &= C["oferta_total"] == sum(X["a"]) == C["demanda_total"] == sum(X["b"])
    print("CADENA:", "OK, costos, envíos y costo total ($586.340) calzan con el script del caso" if ok else "NO calza")
    return ok


if __name__ == "__main__":
    R = resultados()
    for k, X in R.items():
        print(f"== {k}: NO {X['c_no']} · CM {X['c_cm']} · Vogel {X['c_vo']} · óptimo {X['opt']} · iteraciones MODI "
              f"{len(X['modi_no']) - 1}/{len(X['modi_cm']) - 1}/{len(X['modi_vo']) - 1}")
    print("e06:", R["e06"]["sin_atender"], R["e06"]["multas"], R["e06"]["flete"])
    print("e08:", R["e08"]["red_piso"], R["e08"]["sube_piso"], R["e08"]["z_piso"], "CM usa la ruta M:", R["e08"]["m_cm"])
    print("e09:", R["e09"]["ganancia"], R["e09"]["u_g"], R["e09"]["v_g"])
    print("e10:", R["e10"]["cero"], R["e10"]["theta_alt"], R["e10"]["baja1"])
    if not cadena(R):
        sys.exit(1)
    figura(R)
    hay = comparar_con_opl(R)
    if "--tablas" in sys.argv:
        for k, t in tablas(R).items():
            print(f"\n### {k}\n{t}")
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md_n]
        T = tablas(R)
        for k in sorted(USADAS):
            for linea in T[k].splitlines():
                if linea.strip() and linea not in md:
                    faltan.append(f"tabla {k}: {linea[:70]}")
        faltan += codigo_en_md(md)
        lineas_md = set(l.strip() for l in md.splitlines())
        faltan += [f"salida OPL: {l}" for l in SALIDA_CASO if l not in lineas_md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
