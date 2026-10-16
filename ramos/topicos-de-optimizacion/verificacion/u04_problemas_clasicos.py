"""Unidad 4 · Problemas clásicos. Recalcula todas las cifras; con --revisar las busca en el .md.

Cada modelo OPL de la unidad está en ramos/topicos-de-optimizacion/modelos/u04_*.mod (y .dat). Este
script:

1. declara los datos del ejemplo, de los ejercicios y del caso en un solo lugar (las distancias del
   caso salen de verificacion/caso_estampa_sur_red.py, con ruta más corta por los caminos);
2. resuelve cada modelo en Python (scipy.optimize.milp) y lo compara con un segundo camino: fuerza
   bruta sobre las rutas, los patrones o las combinaciones de bodegas;
3. si hay CPLEX (oplrun), corre los .mod con herramientas/opl.py y exige el mismo objetivo;
4. compara la ruta del camión con el script del caso (CADENA);
5. con --revisar, busca cada cifra y el código OPL del ejemplo y del caso en el .md.

    python u04_problemas_clasicos.py            # imprime los resultados
    python u04_problemas_clasicos.py --revisar  # además los busca en el .md
    python u04_problemas_clasicos.py --figuras  # redibuja las figuras SVG
"""
from itertools import combinations, permutations, product
from pathlib import Path
import importlib.util, re, sys

import numpy as np
import networkx as nx
from scipy.optimize import milp, LinearConstraint, Bounds

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
MD = RAMO / "unidades" / "04-problemas-clasicos.md"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402

TOL = 1e-6
INF = np.inf
TINTA, SUAVE, LINEA, ACENTO = "#2B2F33", "#5F656B", "#D6D3CE", "#E2622A"


# ---------------------------------------------------------------- formato chileno
def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x, dec=0):
    return ("$" if abs(x) >= 1000 else "\\$") + fmt(x, dec)


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def num(x):
    if abs(x - round(x)) < 1e-9:
        return fmt(round(x), 0)
    for d in (1, 2, 3):
        if abs(x - round(x, d)) < 1e-9:
            return fmt(x, d)
    return fmt(x, 2)


def caso_modulo():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_red.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- datos (originales)
ASC = {"lugares": ["Base", "Torre", "Plaza", "Liceo", "Hotel", "Mall"],
       "d": [[0, 3, 7, 8, 6, 5], [3, 0, 5, 7, 8, 6], [7, 5, 0, 2, 6, 8],
             [8, 7, 2, 0, 5, 7], [6, 8, 6, 5, 0, 2], [5, 6, 8, 7, 2, 0]]}
DEA = {"sitios": ["S1", "S2", "S3", "S4", "S5", "S6", "S7"],
       "cubre": [[1, 2, 4], [2, 3, 5], [1, 4, 7], [3, 5, 6, 9], [4, 7, 8], [6, 8, 9], [2, 5, 6]],
       "costo": [410, 390, 350, 820, 340, 560, 310],             # miles de pesos
       "pobl": [640, 410, 980, 520, 730, 870, 470, 590, 690],    # vecinos por junta J1..J9
       "presupuesto": 910}                                       # 4.2
MTZ5 = {"n": 5, "subtours": [[1, 3], [2, 4, 5]], "ruta": [1, 3, 2, 5, 4]}  # 4.3
CORTE = {"largo": 320, "piezas": ["A", "B", "C"], "medida": [110, 80, 50], "pide": [40, 65, 90]}  # 4.4 y 4.6
TURNOS = {"franjas": 6, "turnos": ["T1", "T2", "T3", "T4", "T5", "T6", "T7"],
          "cubre": [[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 1], [3, 4, 5]],
          "costo": [95000, 82000, 71000, 76000, 91000, 108000, 66000],
          "pref": [4, 6, 3, 5, 2, 3, 8]}   # 4.5
BOD = {"bodegas": ["Norte", "Rio", "Sur"], "clientes": ["C1", "C2", "C3", "C4", "C5"],
       "fijo": [430000, 380000, 410000], "demanda": [120, 85, 145, 65, 105],
       "costo": [[1800, 2600, 4150, 3350, 5200], [3400, 1900, 2300, 4550, 3100], [4950, 3800, 2700, 2100, 1650]],
       "cap": [290, 260, 270]}                                    # 4.7 y 4.10
CAMIONETAS = {"q": {"Centro": 31, "Puerto": 24, "Lagos": 19, "Valle": 36, "Costa": 14, "Cerro": 22}, "Q": 80, "K": 2}  # 4.9


# ---------------------------------------------------------------- vendedor viajero
def largo(ruta, D):
    return sum(D[a][b] for a, b in zip(ruta, ruta[1:]))


def tsp_bruto(n, D):
    """Todas las rutas que salen y vuelven al nodo 0. Devuelve el mínimo y las rutas óptimas."""
    rutas = [(0,) + p + (0,) for p in permutations(range(1, n))]
    m = min(largo(r, D) for r in rutas)
    return m, [r for r in rutas if abs(largo(r, D) - m) < TOL]


def tsp_milp(n, D, mtz=True, relajar=False):
    """x_ij binaria (i ≠ j), u_i para i ≥ 1. Asignación + MTZ."""
    arcos = [(i, j) for i in range(n) for j in range(n) if i != j]
    na = len(arcos)
    nv = na + (n - 1 if mtz else 0)
    c = [D[i][j] for i, j in arcos] + [0] * (nv - na)
    filas = []
    for i in range(n):
        a = [0] * nv
        for k, (p, q) in enumerate(arcos):
            if p == i: a[k] = 1
        filas.append((a, 1, 1))
        a = [0] * nv
        for k, (p, q) in enumerate(arcos):
            if q == i: a[k] = 1
        filas.append((a, 1, 1))
    if mtz:
        for k, (i, j) in enumerate(arcos):
            if i == 0 or j == 0:
                continue
            a = [0] * nv
            a[na + i - 1] += 1; a[na + j - 1] -= 1; a[k] += n - 1
            filas.append((a, -INF, n - 2))     # u_i − u_j + 1 ≤ (n−1)(1 − x_ij)
    cotas = [(0, 1)] * na + [(2, n)] * (nv - na)
    integ = np.zeros(nv) if relajar else np.array([1] * na + [0] * (nv - na))
    r = milp(c, constraints=LinearConstraint(np.array([f[0] for f in filas], float), [f[1] for f in filas],
                                              [f[2] for f in filas]),
             integrality=integ, bounds=Bounds([b[0] for b in cotas], [b[1] for b in cotas]))
    assert r.status == 0, r.message
    x = {arcos[k]: r.x[k] for k in range(na)}
    u = list(r.x[na:])
    return r.fun, x, u


def ciclos(x, n):
    sig = {i: j for (i, j), v in x.items() if v > 0.5}
    vistos, out = set(), []
    for s in range(n):
        if s in vistos:
            continue
        c, k = [], s
        while k not in vistos:
            vistos.add(k); c.append(k); k = sig[k]
        out.append(c)
    return out


def ascensores():
    d = ASC
    n = len(d["lugares"])
    m, opt = tsp_bruto(n, d["d"])
    z, x, u = tsp_milp(n, d["d"])
    assert abs(z - m) < TOL
    za, xa, _ = tsp_milp(n, d["d"], mtz=False)
    zr, _, _ = tsp_milp(n, d["d"], relajar=True)
    zar, _, _ = tsp_milp(n, d["d"], mtz=False, relajar=True)
    cic = ciclos(xa, n)
    # la solución de la asignación es única: forzar cualquier otra cuesta más
    nombres = d["lugares"]
    return {"km": m, "optimas": opt, "n_opt": len(opt) // 2, "asig": za, "asig_ciclos": [[nombres[i] for i in c] for c in cic],
            "rel_mtz": zr, "rel_asig": zar, "gap_asig": (m - za) / m, "gap_rel": (m - zr) / m,
            "pares": sum(n - 1 - 1 for _ in range(1)), "n_mtz": (n - 1) * (n - 2)}


def caso_ruta():
    caso = caso_modulo()
    G = caso.grafo()
    Dd = dict(nx.all_pairs_dijkstra_path_length(G, weight="km"))
    P = dict(nx.all_pairs_dijkstra_path(G, weight="km"))
    L = ["Taller"] + caso.TIENDAS
    n = len(L)
    D = [[Dd[a][b] for b in L] for a in L]
    m, opt = tsp_bruto(n, D)
    z, x, u = tsp_milp(n, D)
    assert abs(z - m) < TOL
    za, xa, _ = tsp_milp(n, D, mtz=False)
    zr, _, _ = tsp_milp(n, D, relajar=True)
    cic = ciclos(xa, n)
    ruta = caso.calcular()["u4"]["tsp_ruta"]
    tramos = [(a, b, Dd[a][b], P[a][b]) for a, b in zip(ruta, ruta[1:])]
    km_directo_ruta = sum(G[a][b]["km"] for a, b in zip(ruta, ruta[1:]) if G.has_edge(a, b))
    return {"L": L, "D": D, "km": m, "n_opt": len(opt) // 2, "optimas": [[L[i] for i in r] for r in opt],
            "asig": za, "asig_ciclos": [[L[i] for i in c] for c in cic], "rel_mtz": zr,
            "gap_asig": (m - za) / m, "gap_rel": (m - zr) / m, "ruta": ruta, "tramos": tramos,
            "caminos": caso.CAMINOS, "G": G}


# ---------------------------------------------------------------- ejercicios
def e02():
    d = DEA
    nS, nJ = len(d["sitios"]), 9
    A = [[1 if (j + 1) in d["cubre"][s] else 0 for s in range(nS)] for j in range(nJ)]
    def cubrir(c):
        r = milp(c, constraints=LinearConstraint(np.array(A, float), 1, INF), integrality=np.ones(nS),
                 bounds=Bounds(0, 1))
        return r.fun, [d["sitios"][s] for s in range(nS) if r.x[s] > 0.5]
    n_min, sel_n = cubrir([1] * nS)
    c_min, sel_c = cubrir(d["costo"])
    # fuerza bruta: todas las combinaciones de sitios
    todas = []
    for k in range(1, nS + 1):
        for S in combinations(range(nS), k):
            if all(any(A[j][s] for s in S) for j in range(nJ)):
                todas.append((k, sum(d["costo"][s] for s in S), S))
    assert min(t[0] for t in todas) == round(n_min) and min(t[1] for t in todas) == round(c_min)
    assert sum(1 for t in todas if t[1] == round(c_min)) == 1, "la cobertura de costo mínimo no es única"
    de_n = [t for t in todas if t[0] == round(n_min)]
    costo_de_n = min(t[1] for t in de_n)
    # cobertura máxima con presupuesto: max Σ pobl_j z_j, z_j ≤ Σ_{s cubre j} x_s, Σ costo x ≤ presupuesto
    mejor = None
    for k in range(0, nS + 1):
        for S in combinations(range(nS), k):
            if sum(d["costo"][s] for s in S) > d["presupuesto"]:
                continue
            p = sum(d["pobl"][j] for j in range(nJ) if any(A[j][s] for s in S))
            if mejor is None or p > mejor[0]:
                mejor = (p, S)
    c = [0] * nS + [-p for p in d["pobl"]]
    filas = [(list(d["costo"]) + [0] * nJ, -INF, d["presupuesto"])]
    for j in range(nJ):
        a = [-A[j][s] for s in range(nS)] + [0] * nJ; a[nS + j] = 1; filas.append((a, -INF, 0))
    r = milp(c, constraints=LinearConstraint(np.array([f[0] for f in filas], float), [f[1] for f in filas],
                                              [f[2] for f in filas]), integrality=np.ones(nS + nJ), bounds=Bounds(0, 1))
    assert abs(-r.fun - mejor[0]) < TOL
    empates = [S for k in range(nS + 1) for S in combinations(range(nS), k)
               if sum(d["costo"][s] for s in S) <= d["presupuesto"]
               and sum(d["pobl"][j] for j in range(nJ) if any(A[j][s] for s in S)) == mejor[0]]
    assert len(empates) == 1, "la cobertura máxima no es única"
    mclp_sel = [d["sitios"][s] for s in range(nS) if r.x[s] > 0.5]
    return {"A": A, "n_min": n_min, "sel_n": sel_n, "costo_de_n": costo_de_n, "n_soluciones_n": len(de_n),
            "c_min": c_min, "sel_c": sel_c, "mclp": mejor[0], "mclp_sel": [d["sitios"][s] for s in mejor[1]],
            "mclp_sel_milp": mclp_sel, "pobl_total": sum(d["pobl"]),
            "mclp_costo": sum(d["costo"][s] for s in mejor[1]),
            "J": {j + 1: [d["sitios"][s] for s in range(nS) if A[j][s]] for j in range(nJ)}}


def e03():
    d = MTZ5
    n = d["n"]
    # subtour 2→4→5→2: sumar sus tres MTZ da 3 ≤ 0
    sub = d["subtours"][1]
    suma_izq = len(sub)            # (u2 − u4 + 1) + (u4 − u5 + 1) + (u5 − u2 + 1) = 3
    # ruta 1→3→2→5→4→1: posiciones
    u = {nodo: k + 1 for k, nodo in enumerate(d["ruta"])}
    usados = set(zip(d["ruta"], d["ruta"][1:] + [d["ruta"][0]]))
    holguras = {}
    for i in range(2, n + 1):
        for j in range(2, n + 1):
            if i == j:
                continue
            x = 1 if (i, j) in usados else 0
            izq, der = u[i] - u[j] + 1, (n - 1) * (1 - x)
            assert izq <= der
            holguras[(i, j)] = (izq, der)
    max_izq = max(v[0] for k, v in holguras.items() if k not in usados)
    return {"u": u, "suma": suma_izq, "h42": holguras[(4, 2)], "h53": holguras[(5, 3)], "max_izq": max_izq, "n": n}


def patrones(largo, medida):
    """Patrones maximales: no cabe ninguna pieza más en lo que sobra."""
    out = []
    rangos = [range(largo // m + 1) for m in medida]
    for a in product(*rangos):
        usado = sum(k * m for k, m in zip(a, medida))
        if usado <= largo and largo - usado < min(medida):
            out.append((a, largo - usado))
    out.sort(key=lambda t: (-t[0][0], -t[0][1], -t[0][2]))
    return out


def e04():
    d = CORTE
    P = patrones(d["largo"], d["medida"])
    # todos los patrones factibles (maximales o no), para contarlos
    tot = sum(1 for a in product(*[range(d["largo"] // m + 1) for m in d["medida"]])
              if 0 < sum(k * m for k, m in zip(a, d["medida"])) <= d["largo"])
    return {"P": P, "n_max": len(P), "n_todos": tot}


def e06():
    d = CORTE
    P = patrones(d["largo"], d["medida"])
    nP, nI = len(P), len(d["medida"])
    A = np.array([[P[p][0][i] for p in range(nP)] for i in range(nI)], float)
    r = milp(np.ones(nP), constraints=LinearConstraint(A, d["pide"], INF), integrality=np.ones(nP), bounds=Bounds(0, INF))
    assert r.status == 0
    barras = r.fun
    x = [round(v) for v in r.x]
    hechas = [int(sum(A[i][p] * x[p] for p in range(nP))) for i in range(nI)]
    sobra = [hechas[i] - d["pide"][i] for i in range(nI)]
    material = sum(m * q for m, q in zip(d["medida"], d["pide"]))
    merma_patron = sum(P[p][1] * x[p] for p in range(nP))
    desperdicio_total = barras * d["largo"] - material
    cota = material / d["largo"]
    rl = milp(np.ones(nP), constraints=LinearConstraint(A, d["pide"], INF), integrality=np.zeros(nP), bounds=Bounds(0, INF))
    # segundo camino: igual óptimo minimizando la merma de patrón + sobreproducción (desperdicio total)
    return {"barras": barras, "x": x, "hechas": hechas, "sobra": sobra, "material": material,
            "merma_patron": merma_patron, "desperdicio": desperdicio_total, "cota": cota, "lp": rl.fun,
            "usados": [(P[p][0], x[p]) for p in range(nP) if x[p] > 0]}


def e05():
    d = TURNOS
    nT, nF = len(d["turnos"]), d["franjas"]
    A = np.array([[1 if f + 1 in d["cubre"][t] else 0 for t in range(nT)] for f in range(nF)], float)
    def resolver(sentido, c, li, ld):
        r = milp(c if sentido == "min" else -np.array(c, float), constraints=LinearConstraint(A, li, ld),
                 integrality=np.ones(nT), bounds=Bounds(0, 1))
        if r.status != 0:
            return None, None
        return (r.fun if sentido == "min" else -r.fun), [d["turnos"][t] for t in range(nT) if r.x[t] > 0.5]
    cov = resolver("min", d["costo"], 1, INF)
    par = resolver("min", d["costo"], 1, 1)
    pack = resolver("max", d["pref"], -INF, 1)
    # fuerza bruta
    def bruto(cond, val, mejor_es):
        best = None
        for S in product([0, 1], repeat=nT):
            cub = A @ np.array(S)
            if cond(cub):
                v = val(S)
                if best is None or mejor_es(v, best[0]):
                    best = (v, S)
        return best
    bc = bruto(lambda c: all(c >= 1), lambda S: sum(s * k for s, k in zip(S, d["costo"])), lambda a, b: a < b)
    bp = bruto(lambda c: all(c == 1), lambda S: sum(s * k for s, k in zip(S, d["costo"])), lambda a, b: a < b)
    bk = bruto(lambda c: all(c <= 1), lambda S: sum(s * k for s, k in zip(S, d["pref"])), lambda a, b: a > b)
    assert abs(bc[0] - cov[0]) < TOL and abs(bp[0] - par[0]) < TOL and abs(bk[0] - pack[0]) < TOL
    for cond, val, opt in [(lambda c: all(c >= 1), lambda S: sum(s * k for s, k in zip(S, d["costo"])), bc[0]),
                           (lambda c: all(c == 1), lambda S: sum(s * k for s, k in zip(S, d["costo"])), bp[0]),
                           (lambda c: all(c <= 1), lambda S: sum(s * k for s, k in zip(S, d["pref"])), bk[0])]:
        assert sum(1 for S in product([0, 1], repeat=nT) if cond(A @ np.array(S)) and abs(val(S) - opt) < TOL) == 1
    cub_cov = A @ np.array([1 if d["turnos"][t] in cov[1] else 0 for t in range(nT)])
    return {"cov": cov, "par": par, "pack": pack, "dobles": int(sum(cub_cov > 1)), "sobreprecio": par[0] - cov[0]}


def ufl(fijo, cap=None, relajar=False, agregada=False, unico=False):
    d = BOD
    nB, nC = len(d["bodegas"]), len(d["clientes"])
    c = list(fijo) + [d["costo"][i][j] * d["demanda"][j] for i in range(nB) for j in range(nC)]
    nv = nB + nB * nC
    filas = []
    for j in range(nC):
        a = [0] * nv
        for i in range(nB): a[nB + i * nC + j] = 1
        filas.append((a, 1, 1))
    if agregada:
        for i in range(nB):
            a = [0] * nv; a[i] = -nC
            for j in range(nC): a[nB + i * nC + j] = 1
            filas.append((a, -INF, 0))
    else:
        for i in range(nB):
            for j in range(nC):
                a = [0] * nv; a[i] = -1; a[nB + i * nC + j] = 1; filas.append((a, -INF, 0))
    if cap:
        for i in range(nB):
            a = [0] * nv; a[i] = -cap[i]
            for j in range(nC): a[nB + i * nC + j] = d["demanda"][j]
            filas.append((a, -INF, 0))
    integ = np.zeros(nv) if relajar else np.array([1] * nB + [1 if unico else 0] * (nB * nC))
    r = milp(c, constraints=LinearConstraint(np.array([f[0] for f in filas], float), [f[1] for f in filas],
                                              [f[2] for f in filas]), integrality=integ, bounds=Bounds(0, 1))
    assert r.status == 0
    y = list(r.x[:nB])
    x = [[r.x[nB + i * nC + j] for j in range(nC)] for i in range(nB)]
    return r.fun, y, x


def e07():
    d = BOD
    nB, nC = len(d["bodegas"]), len(d["clientes"])
    z, y, x = ufl(d["fijo"])
    # segundo camino: para cada conjunto de bodegas abiertas, cada cliente va a la más barata
    mejor = None
    for k in range(1, nB + 1):
        for S in combinations(range(nB), k):
            v = sum(d["fijo"][i] for i in S) + sum(min(d["costo"][i][j] for i in S) * d["demanda"][j] for j in range(nC))
            if mejor is None or v < mejor[0]:
                mejor = (v, S)
    assert abs(mejor[0] - z) < TOL
    asign = {d["clientes"][j]: d["bodegas"][max(range(nB), key=lambda i: x[i][j])] for j in range(nC)}
    zd, yd, _ = ufl(d["fijo"], relajar=True)
    za, ya, _ = ufl(d["fijo"], relajar=True, agregada=True)
    fijo_total = sum(d["fijo"][i] for i in range(nB) if y[i] > 0.5)
    return {"z": z, "abre": [d["bodegas"][i] for i in range(nB) if y[i] > 0.5], "asign": asign, "fijo_total": fijo_total,
            "transporte": z - fijo_total, "rel_des": zd, "rel_agr": za, "y_agr": ya, "y_des": yd,
            "gap_des": (z - zd) / z, "gap_agr": (z - za) / z,
            "solo": {d["bodegas"][i]: d["fijo"][i] + sum(d["costo"][i][j] * d["demanda"][j] for j in range(nC)) for i in range(nB)}}


def e10():
    d = BOD
    nB, nC = len(d["bodegas"]), len(d["clientes"])
    z, y, x = ufl(d["fijo"], cap=d["cap"], unico=True)
    # fuerza bruta: cada cliente a una bodega (3^5 asignaciones)
    mejor = None
    for asg in product(range(nB), repeat=nC):
        carga = [sum(d["demanda"][j] for j in range(nC) if asg[j] == i) for i in range(nB)]
        if any(carga[i] > d["cap"][i] for i in range(nB)):
            continue
        v = sum(d["fijo"][i] for i in set(asg)) + sum(d["costo"][asg[j]][j] * d["demanda"][j] for j in range(nC))
        if mejor is None or v < mejor[0]:
            mejor = (v, asg)
    assert abs(mejor[0] - z) < TOL
    n_emp = 0
    for asg in product(range(nB), repeat=nC):
        carga = [sum(d["demanda"][j] for j in range(nC) if asg[j] == i) for i in range(nB)]
        if all(carga[i] <= d["cap"][i] for i in range(nB)):
            v = sum(d["fijo"][i] for i in set(asg)) + sum(d["costo"][asg[j]][j] * d["demanda"][j] for j in range(nC))
            n_emp += abs(v - z) < TOL
    assert n_emp == 1, "la asignación con capacidad no es única"
    zf, _, _ = ufl(d["fijo"], cap=d["cap"], unico=False)   # con capacidad pero dividiendo clientes
    asign = {d["clientes"][j]: d["bodegas"][mejor[1][j]] for j in range(nC)}
    carga = {d["bodegas"][i]: sum(d["demanda"][j] for j in range(nC) if mejor[1][j] == i) for i in range(nB)}
    return {"z": z, "abre": [d["bodegas"][i] for i in range(nB) if y[i] > 0.5], "asign": asign, "carga": carga,
            "dividido": zf, "demanda_total": sum(d["demanda"])}


def e09(C):
    d = CAMIONETAS
    L, D = C["L"], C["D"]
    tiendas = L[1:]
    idx = {t: k for k, t in enumerate(L)}
    def tsp_sub(S):
        if not S:
            return 0, ()
        best = None
        for p in permutations(S):
            r = (0,) + tuple(idx[t] for t in p) + (0,)
            v = largo(r, D)
            if best is None or v < best[0]:
                best = (v, p)
        return best
    mejor = None
    for k in range(0, len(tiendas) + 1):
        for S in combinations(tiendas, k):
            T = tuple(t for t in tiendas if t not in S)
            if sum(d["q"][t] for t in S) > d["Q"] or sum(d["q"][t] for t in T) > d["Q"]:
                continue
            a, b = tsp_sub(S), tsp_sub(T)
            v = a[0] + b[0]
            if mejor is None or v < mejor[0] - TOL:
                mejor = (v, a, b); n_emp = 1
            elif abs(v - mejor[0]) < TOL:
                n_emp += 1
    assert n_emp == 2, ("reparto de camionetas no único", n_emp)   # cada reparto aparece dos veces (S y su complemento)
    km = mejor[0]
    r1, r2 = sorted([mejor[1], mejor[2]], key=lambda t: -len(t[1]))
    return {"km": km, "r1": r1, "r2": r2, "carga1": sum(d["q"][t] for t in r1[1]), "carga2": sum(d["q"][t] for t in r2[1]),
            "total": sum(d["q"].values()), "extra": km - C["km"]}


# ---------------------------------------------------------------- todo junto
def resultados():
    C = caso_ruta()
    return {"asc": ascensores(), "caso": C, "e02": e02(), "e03": e03(), "e04": e04(), "e05": e05(), "e06": e06(),
            "e07": e07(), "e09": e09(C), "e10": e10()}


def cadena(R):
    C4 = caso_modulo().calcular()["u4"]
    v = R["caso"]
    ok = abs(v["km"] - C4["tsp_km"]) < TOL and v["ruta"] == C4["tsp_ruta"]
    ok &= abs(largo([v["L"].index(t) for t in C4["tsp_ruta"]], v["D"]) - C4["tsp_km"]) < TOL
    ok &= v["n_opt"] == 1
    print("CADENA:", f"OK, la ruta del camión es la del caso ({C4['tsp_km']} km, única salvo el sentido)" if ok else "NO calza")
    return ok


def comparar_con_opl(R):
    if correr(MODELOS / "u04_tsp.mod", MODELOS / "u04_ascensores.dat") is None:
        print("OPL: oplrun no está instalado; se comparan solo las cifras de Python")
        return None
    A, C = R["asc"], R["caso"]
    salidas = {}
    pruebas = [("asc", "u04_tsp.mod", "u04_ascensores.dat", A["km"]), ("caso", "u04_tsp.mod", "u04_ruta_camion.dat", C["km"]),
               ("e06", "u04_e06_corte.mod", "u04_e06_corte.dat", R["e06"]["barras"]),
               ("e07", "u04_e07_bodegas.mod", "u04_e07_bodegas.dat", R["e07"]["z"]),
               ("e09", "u04_e09_camionetas.mod", "u04_e09_camionetas.dat", R["e09"]["km"]),
               ("e10", "u04_e10_capacidad.mod", "u04_e10_capacidad.dat", R["e10"]["z"])]
    for k, mod, dat, z in pruebas:
        r = correr(MODELOS / mod, MODELOS / dat)
        assert r["codigo"] == 0 and r["objetivo"] is not None, (k, r["salida"][-400:])
        assert abs(r["objetivo"] - z) < 1e-4, (k, r["objetivo"], z)
        salidas[k] = r
    # la ruta que imprime OPL es una de las óptimas
    for k, lugares_ok in [("asc", [[ASC["lugares"][i] for i in rr] for rr in A["optimas"]]), ("caso", C["optimas"])]:
        ruta = salidas[k]["valores"]["ruta"].split("-")
        assert ruta in lugares_ok, (k, ruta)
    # el .dat del caso trae exactamente las distancias de ruta más corta
    dat = (MODELOS / "u04_ruta_camion.dat").read_text(encoding="utf-8")
    filas = re.findall(r"\[\s*([\d\s]+)\]\s*//\s*(\w+)", dat)
    assert [[int(v) for v in f.split()] for f, _ in filas] == [[int(v) for v in fila] for fila in C["D"]]
    # el .dat del corte trae exactamente los patrones maximales
    dat = (MODELOS / "u04_e06_corte.dat").read_text(encoding="utf-8")
    pat = [tuple(int(v) for v in f.split()) for f in re.findall(r"\[\s*(\d+\s+\d+\s+\d+)\s*\]\s*//\s*P\d", dat)]
    assert pat == [p for p, _ in patrones(CORTE["largo"], CORTE["medida"])], pat
    R["opl"] = {k: v["valores"] for k, v in salidas.items()}
    print(f"OPL: {len(pruebas)} modelos corridos con oplrun; objetivos iguales a Python y rutas entre las óptimas")
    return True


def esperados(R):
    A, C = R["asc"], R["caso"]
    s = [f"{num(A['km'])} km", f"{num(A['asig'])} km", num(A["rel_mtz"]), pct(A["gap_rel"]), pct(A["gap_asig"]),
         num(A["n_mtz"])]
    s += [" → ".join(c + [c[0]]) for c in A["asig_ciclos"]]
    if "opl" in R:
        s.append(R["opl"]["asc"]["ruta"].replace("-", ", "))
        s.append(R["opl"]["caso"]["ruta"].replace("-", ", "))
    # caso
    s += ["78 km", ", ".join(C["ruta"]), fmt(C["rel_mtz"], 2), f"{num(C['asig'])} km", pct(C["gap_rel"]), pct(C["gap_asig"])]
    s += [" → ".join(c + [c[0]]) for c in C["asig_ciclos"]]
    for a, b, km, camino in C["tramos"]:
        s.append(f"| {a} → {b} | {km} |")
    for i, a in enumerate(C["L"]):
        s.append(f"| {a} | " + " | ".join("—" if i == j else str(C["D"][i][j]) for j in range(len(C["L"]))) + " |")
    # 4.2
    e = R["e02"]; s += [f"{num(e['n_min'])} sitios", ", ".join(e["sel_n"]), pesos(e["costo_de_n"] * 1000),
                        pesos(e["c_min"] * 1000), ", ".join(e["sel_c"]), fmt(e["mclp"]), fmt(e["pobl_total"]),
                        ", ".join(e["mclp_sel"]), pesos(e["mclp_costo"] * 1000)]
    # 4.3
    e = R["e03"]; s += [f"{e['h42'][0]} \\le {e['h42'][1]}", f"{e['h53'][0]} \\le {e['h53'][1]}", f"3 \\le 0"]
    # 4.4
    e = R["e04"]
    for (a, m) in e["P"]:
        s.append(f"| {a[0]} | {a[1]} | {a[2]} | {320 - m} | {m} |")
    s += [f"{e['n_max']} patrones maximales", f"{e['n_todos']} patrones"]
    # 4.5
    e = R["e05"]; s += [pesos(e["cov"][0]), ", ".join(e["cov"][1]), pesos(e["par"][0]), ", ".join(e["par"][1]),
                        f"{num(e['pack'][0])} puntos", ", ".join(e["pack"][1]), pesos(e["sobreprecio"])]
    # 4.6
    e = R["e06"]; s += [f"{num(e['barras'])} tablas", fmt(e["cota"], 2), fmt(e["lp"], 2), f"{fmt(e['material'])} cm",
                        f"{fmt(e['desperdicio'])} cm", f"{fmt(e['merma_patron'])} cm"]
    # 4.7
    e = R["e07"]; s += [pesos(e["z"]), pesos(e["fijo_total"]), pesos(e["transporte"]), pesos(e["rel_des"]),
                        pesos(e["rel_agr"]), pct(e["gap_des"]), pct(e["gap_agr"])]
    s += [pesos(v) for v in e["solo"].values()]
    # 4.9
    e = R["e09"]; s += [f"{num(e['km'])} km", f"{num(e['extra'])} km", f"{e['carga1']} cajas", f"{e['carga2']} cajas",
                        f"{e['total']} cajas"]
    # 4.10
    e = R["e10"]; s += [pesos(e["z"]), pesos(e["dividido"])]
    s += [f"{k}: {v} cajas" for k, v in e["carga"].items() if v > 0]
    return s


def codigo_en_md(md):
    faltan = []
    for f in ["u04_tsp.mod", "u04_ascensores.dat", "u04_ruta_camion.dat"]:
        for linea in (MODELOS / f).read_text(encoding="utf-8").splitlines():
            if linea.strip() and linea.rstrip() not in md:
                faltan.append(f"{f}: {linea.strip()}")
    return faltan


# ---------------------------------------------------------------- figuras
POS = {"Taller": (0.0, 2.2), "Centro": (1.6, 3.2), "Cruce": (2.6, 1.9), "Puerto": (2.6, 4.5), "Costa": (0.9, 4.9),
       "Lagos": (4.4, 3.4), "Valle": (5.0, 1.7), "Cerro": (4.0, 0.3)}


def figuras(R):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "path"})
    carpeta = RAMO / "unidades" / "figuras"
    carpeta.mkdir(parents=True, exist_ok=True)
    C = R["caso"]
    # 1 · la red del caso y la ruta óptima del camión
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    usados = set()
    for a, b, km, camino in C["tramos"]:
        for p, q in zip(camino, camino[1:]):
            usados.add(frozenset((p, q)))
    for (a, b), km in C["caminos"].items():
        (x1, y1), (x2, y2) = POS[a], POS[b]
        en = frozenset((a, b)) in usados
        ax.plot([x1, x2], [y1, y2], color=ACENTO if en else LINEA, lw=3.2 if en else 1.4, zorder=1,
                solid_capstyle="round")
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, str(km), fontsize=8.5, ha="center", va="center",
                color=TINTA if en else SUAVE, bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"), zorder=3)
    for nodo, (x, y) in POS.items():
        tienda = nodo in caso_modulo().TIENDAS
        ax.scatter([x], [y], s=520 if nodo != "Cruce" else 260, color="#F2F1EF" if nodo != "Taller" else TINTA,
                   edgecolor=TINTA if nodo != "Cruce" else SUAVE, linewidth=1.2, zorder=4,
                   linestyle="-" if nodo != "Cruce" else "--")
        ax.text(x, y - 0.42 if y > 0.6 else y + 0.42, nodo, ha="center", va="center", fontsize=9,
                color=TINTA if tienda or nodo == "Taller" else SUAVE, zorder=5)
    orden = C["ruta"]
    for k, nodo in enumerate(orden[1:-1], start=1):
        x, y = POS[nodo]
        ax.text(x, y, str(k), ha="center", va="center", fontsize=9, fontweight="bold", color=ACENTO, zorder=6)
    x, y = POS["Taller"]
    ax.text(x, y, "T", ha="center", va="center", fontsize=9, fontweight="bold", color="white", zorder=6)
    ax.set_xlim(-0.7, 5.7); ax.set_ylim(-0.4, 5.5); ax.axis("off"); ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(carpeta / "u04_red_camion.svg", metadata={"Date": None})
    plt.close(fig)
    # 2 · el ejemplo: la asignación arma subtours; con MTZ queda una sola ruta
    A = R["asc"]
    pos = {"Base": (0.0, 1.0), "Torre": (0.9, 2.0), "Plaza": (2.3, 2.1), "Liceo": (3.0, 1.3), "Hotel": (2.2, 0.0), "Mall": (1.0, 0.1)}
    rutas = [[c + [c[0]] for c in A["asig_ciclos"]], [R["opl"]["asc"]["ruta"].split("-")] if "opl" in R else []]
    titulos = [f"Solo asignación: {num(A['asig'])} km en subtours", f"Con MTZ: una ruta de {num(A['km'])} km"]
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.9))
    for ax, rr, tt in zip(axs, rutas, titulos):
        for r in rr:
            for a, b in zip(r, r[1:]):
                (x1, y1), (x2, y2) = pos[a], pos[b]
                ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                            arrowprops=dict(arrowstyle="-|>", color=ACENTO, lw=1.8, shrinkA=11, shrinkB=11,
                                            connectionstyle="arc3,rad=0.18"))
        for nodo, (x, y) in pos.items():
            ax.scatter([x], [y], s=380, color=TINTA if nodo == "Base" else "#F2F1EF", edgecolor=TINTA, zorder=3)
            ax.text(x, y - 0.36 if y < 1.5 else y + 0.36, nodo, ha="center", va="center", fontsize=8.5, color=TINTA)
        ax.set_title(tt, fontsize=9.5, color=TINTA)
        ax.set_xlim(-0.5, 3.5); ax.set_ylim(-0.6, 2.7); ax.axis("off"); ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(carpeta / "u04_subtours.svg", metadata={"Date": None})
    plt.close(fig)
    print("figuras: u04_red_camion.svg, u04_subtours.svg")


if __name__ == "__main__":
    R = resultados()
    for k, v in R.items():
        print(f"== {k}")
        if isinstance(v, dict):
            for kk, vv in v.items():
                if kk in ("G", "caminos", "D", "A"):
                    continue
                print(f"   {kk} = {vv}")
    if not cadena(R):
        sys.exit(1)
    comparar_con_opl(R)
    if "--figuras" in sys.argv:
        figuras(R)
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md_n]
        faltan += codigo_en_md(md)
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
