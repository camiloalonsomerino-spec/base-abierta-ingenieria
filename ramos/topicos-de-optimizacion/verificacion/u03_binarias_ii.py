"""Unidad 3 · Variables binarias II. Recalcula todas las cifras; con --revisar las busca en el .md.

Cada modelo OPL de la unidad está en ramos/topicos-de-optimizacion/modelos/u03_*.mod (y .dat). Este
script:

1. declara los datos del ejemplo, de los diez ejercicios y del caso en un solo lugar;
2. resuelve cada modelo en Python (scipy.optimize.milp, con HiGHS) y lo comprueba por un segundo
   camino (enumeración de las binarias o fuerza bruta);
3. si hay CPLEX (oplrun), corre los .mod con herramientas/opl.py y exige que objetivo y variables
   coincidan con Python, también en las relajaciones lineales;
4. compara la pieza del caso integrador con verificacion/caso_estampa_sur_red.py (CADENA);
5. con --revisar, busca cada cifra y el código OPL del ejemplo y del caso en el .md.

    python u03_binarias_ii.py            # imprime los resultados
    python u03_binarias_ii.py --revisar  # además los busca en el .md
    python u03_binarias_ii.py --figuras  # redibuja las figuras SVG
"""
from itertools import combinations, permutations, product
from pathlib import Path
import importlib.util, re, shutil, sys, tempfile

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds, linprog

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
MD = RAMO / "unidades" / "03-binarias-costo-fijo-y-gran-m.md"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402

TOL = 1e-6
TINTA, SUAVE, LINEA, ACENTO = "#2B2F33", "#5F656B", "#D6D3CE", "#E2622A"


# ---------------------------------------------------------------- formato chileno
def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x, dec=0):
    """$36.000 con punto de miles; bajo mil, \\$600 (así lo pide el PDF)."""
    s = fmt(x, dec)
    return ("$" if abs(x) >= 1000 else "\\$") + s


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def num(x):
    if abs(x - round(x)) < 1e-9:
        return fmt(round(x), 0)
    for d in (1, 2, 3):
        if abs(x - round(x, d)) < 1e-9:
            return fmt(x, d)
    return fmt(x, 2)


# ---------------------------------------------------------------- un MILP genérico
def resolver(sentido, c, filas, cotas, enteras, relajar=False):
    """filas: lista de (coeficientes, li, ld). enteras: 1 por variable entera o binaria."""
    sg = -1 if sentido == "max" else 1
    A = np.array([f[0] for f in filas], float)
    li = [f[1] for f in filas]
    ld = [f[2] for f in filas]
    integ = np.zeros(len(c)) if relajar else np.array(enteras, float)
    r = milp(sg * np.array(c, float), constraints=LinearConstraint(A, li, ld), integrality=integ,
             bounds=Bounds([b[0] for b in cotas], [b[1] for b in cotas]))
    assert r.status == 0, r.message
    return sg * r.fun, list(r.x)


INF = np.inf

# ---------------------------------------------------------------- datos (originales)
VELAS = {"velas": ["frasco", "pilar", "derretible"], "margen": [3190, 2530, 1045], "fijo": [70400, 24200, 30800],
         "cera": [0.32, 0.30, 0.08], "vertido": [6, 4, 2], "disp": [132, 2640], "demanda": [330, 198, 660],
         "minimo": [66, 132, 165], "M_grande": 10000}
SOPA = {"fijo": 26000, "margen": 310, "tope": 140, "feria": 80}                      # 3.1
BICI = {"kits": ["urbano", "montaña"], "margen": [7300, 10600], "fijo": [86000, 137000],
        "horas": [1.6, 2.4], "H": 412, "demanda": [236, 118], "M_mal": 150}            # 3.2
FLOW = {"trabajos": ["L1", "L2", "L3", "L4"], "maquinas": ["impresion", "encuadernacion"],
        "p": [[6, 2], [3, 7], [5, 4], [2, 5]]}                                           # sección 9
FLOW3 = {"trabajos": ["A", "B", "C"], "p": [[4, 2, 5], [3, 6, 2], [2, 4, 3]]}           # 3.3
POTENCIA = {"kw": [10, 20, 30, 50], "cargo": [18000, 31000, 43000, 66000], "pico": 26,
            "pico_corrido": 19, "costo_correr": 9000}                                   # 3.4
KDEN = {"c": [4, 3], "cota": 9, "filas": [([1, 1], "<=", 7), ([3, 1], "<=", 15), ([1, 4], "<=", 20),
                                          ([-1, 1], ">=", 1)], "K": 3}                   # 3.5
IMPR = {"margen": {"PLA": [2350, 4150], "PETG": [2350, 5650]}, "horas": {"PLA": [0.75, 1.45], "PETG": [1.05, 1.9]},
        "H": 126, "demanda": [160, 84], "topeCarcasaPLA": 48, "pedidoCarcasaPETG": 32, "topeSoportePETG": 66}  # 3.6
CERA = {"anchos": [200, 300], "precios": [1900, 1600, 1350], "compra": 640, "bodega": 1000}  # 3.7
POLAR = {"desde": [0, 300, 600], "hasta": [299, 599, 1500], "precio": [3200, 2900, 2650], "necesita": 280}  # 3.8
KOMBU = {"sabores": ["jengibre", "frambuesa", "maqui"], "margen": [1150, 1480, 1720], "fijo": [47000, 63000, 98000],
         "minimo": [320, 260, 210], "demanda": [880, 690, 470], "turnos": ["simple", "extendido", "doble"],
         "cap": [1250, 1750, 2300], "costo": [0, 165000, 385000], "max_sabores": 2, "frambuesa_baja": 230,
         "M_grande": 10000}                                                              # 3.9
TERRAZA = {"muebles": ["banca", "mesa"], "margen": [21400, 33800], "fijo": [147000, 212000],
           "uso": [[1.25, 2.05], [0.55, 1.4]], "disp": [316, 149], "demanda": [174, 88], "minimo": [42, 28],
           "M_mal": 95}                                                                 # 3.10


def caso_modulo():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_red.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- modelos de producción con costo fijo y lote
def produccion(margen, fijo, uso, disp, minimo, M, demanda, relajar=False, con_piso=True, enteras=True,
               objetivo_mal=False, piso_sin_y=False, cota_inf=None):
    """max Σ m x − Σ f y  s.a. Σ uso x ≤ disp, x ≤ M y, L y ≤ x, x ≤ demanda."""
    n = len(margen)
    c = list(margen) + [-f for f in fijo]
    if objetivo_mal:   # error 3.10: el costo fijo multiplicado por x
        c = [margen[i] - fijo[i] for i in range(n)] + [0] * n
    filas = [(list(u) + [0] * n, -INF, d) for u, d in zip(uso, disp)]
    for i in range(n):
        a = [0] * (2 * n); a[i] = 1; a[n + i] = -M[i]; filas.append((a, -INF, 0))
        if con_piso and not piso_sin_y:
            a = [0] * (2 * n); a[i] = 1; a[n + i] = -minimo[i]; filas.append((a, 0, INF))
    inf = cota_inf or [minimo[i] if piso_sin_y else 0 for i in range(n)]
    cotas = [(inf[i], demanda[i]) for i in range(n)] + [(0, 1)] * n
    z, x = resolver("max", c, filas, cotas, [1 if enteras else 0] * n + [1] * n, relajar)
    return {"z": z, "x": x[:n], "y": x[n:]}


def enumerar_produccion(margen, fijo, uso, disp, minimo, demanda):
    """Segundo camino: fija cada combinación de binarias y resuelve el entero que queda."""
    n = len(margen)
    mejor = None
    for ys in product([0, 1], repeat=n):
        cotas = [(minimo[i] * ys[i], demanda[i] * ys[i]) for i in range(n)]
        if any(lo > hi for lo, hi in cotas):
            continue
        r = milp(-np.array(margen, float), constraints=LinearConstraint(np.array(uso, float), -INF, disp),
                 integrality=np.ones(n), bounds=Bounds([c[0] for c in cotas], [c[1] for c in cotas]))
        if r.status != 0:
            continue
        z = -r.fun - sum(f * y for f, y in zip(fijo, ys))
        if mejor is None or z > mejor[0] + 1e-9:
            mejor = (z, ys)
    return mejor


# ---------------------------------------------------------------- ejemplo · taller de velas
def velas():
    d = VELAS
    uso = [d["cera"], d["vertido"]]
    M = [min(d["demanda"][i], d["disp"][0] / d["cera"][i], d["disp"][1] / d["vertido"][i]) for i in range(3)]
    R = {"M": M, "M_cera": [d["disp"][0] / v for v in d["cera"]], "M_vertido": [d["disp"][1] / v for v in d["vertido"]]}
    ent = produccion(d["margen"], d["fijo"], uso, d["disp"], d["minimo"], M, d["demanda"])
    R["entero"] = ent
    seg = enumerar_produccion(d["margen"], d["fijo"], uso, d["disp"], d["minimo"], d["demanda"])
    assert abs(seg[0] - ent["z"]) < TOL
    R["sin_piso"] = produccion(d["margen"], d["fijo"], uso, d["disp"], d["minimo"], M, d["demanda"], con_piso=False)
    # el pilar del plan sin lote mínimo es único: forzar uno más o uno menos empeora
    p = round(R["sin_piso"]["x"][1])
    for lo, hi in [(0, p - 1), (p + 1, d["demanda"][1])]:
        dem = list(d["demanda"]); dem[1] = hi
        alt = produccion(d["margen"], d["fijo"], uso, d["disp"], d["minimo"], M, dem, con_piso=False,
                         cota_inf=[0, lo, 0])
        assert alt["z"] < R["sin_piso"]["z"] - 1, ("el pilar del plan sin lote mínimo no es único", lo, hi)
    R["rel_ajustada"] = produccion(d["margen"], d["fijo"], uso, d["disp"], d["minimo"], M, d["demanda"], relajar=True)
    R["rel_grande"] = produccion(d["margen"], d["fijo"], uso, d["disp"], d["minimo"], [d["M_grande"]] * 3,
                                 d["demanda"], relajar=True)
    R["lp_sin_fijo"] = produccion(d["margen"], [0, 0, 0], uso, d["disp"], [0, 0, 0], M, d["demanda"], relajar=True)
    R["gap_ajustada"] = (R["rel_ajustada"]["z"] - ent["z"]) / ent["z"]
    R["gap_grande"] = (R["rel_grande"]["z"] - ent["z"]) / ent["z"]
    R["cera_usada"] = float(np.dot(d["cera"], ent["x"]))
    R["vertido_usado"] = float(np.dot(d["vertido"], ent["x"]))
    R["fijo_pagado_rel"] = [d["fijo"][i] * R["rel_ajustada"]["y"][i] for i in range(3)]
    R["fijo_pagado_grande"] = [d["fijo"][i] * R["rel_grande"]["y"][i] for i in range(3)]
    return R


# ---------------------------------------------------------------- caso · segunda máquina
def segunda_maquina():
    caso = caso_modulo(); u = caso.U3
    c = [u["margen_extra_por_caja"], -u["costo_fijo_maquina"]]
    def mod(M, relajar):
        filas = [([1, -M], -INF, 0), ([1, -u["lote_minimo_cajas"]], 0, INF)]
        return resolver("max", c, filas, [(0, u["cajas_max_maquina"]), (0, 1)], [1, 1], relajar)
    z, x = mod(u["cajas_max_maquina"], False)
    R = {"utilidad": z, "cajas": x[0], "compra": x[1], "equilibrio": u["costo_fijo_maquina"] / u["margen_extra_por_caja"],
         "ingreso": u["margen_extra_por_caja"] * u["cajas_max_maquina"]}
    R["rel_ajustada"], xr = mod(u["cajas_max_maquina"], True)
    R["rel_ajustada_y"] = xr[1]
    R["rel_1000"], xg = mod(1000, True)
    R["rel_1000_y"] = xg[1]
    R["fijo_pagado_1000"] = u["costo_fijo_maquina"] * xg[1]
    # ¿y si el mercado solo tomara 85 cajas? no se compra
    R["con_85"] = max(0, u["margen_extra_por_caja"] * 85 - u["costo_fijo_maquina"])
    R["perdida_85"] = u["margen_extra_por_caja"] * 85 - u["costo_fijo_maquina"]
    R["datos"] = u
    C2 = caso.calcular()["u2"]
    R["u2_valor"], R["u2_lanza"], R["u2_inversion"] = C2["valor_neto"], C2["lanza"], C2["inversion"]
    return R


# ---------------------------------------------------------------- ejercicios
def e01():
    d = SOPA
    R = {"equilibrio": d["fijo"] / d["margen"], "utilidad": d["margen"] * d["tope"] - d["fijo"],
         "ingreso_feria": d["margen"] * d["feria"], "perdida_feria": d["margen"] * d["feria"] - d["fijo"]}
    z, x = resolver("max", [d["margen"], -d["fijo"]], [([1, -d["tope"]], -INF, 0)], [(0, d["tope"]), (0, 1)], [1, 1])
    assert abs(z - R["utilidad"]) < TOL and round(x[1]) == 1
    z2, x2 = resolver("max", [d["margen"], -d["fijo"]], [([1, -d["tope"]], -INF, 0)], [(0, d["feria"]), (0, 1)], [1, 1])
    assert abs(z2) < TOL and round(x2[1]) == 0
    return R


def e02():
    d = BICI
    M = [min(d["demanda"][i], d["H"] / d["horas"][i]) for i in range(2)]
    ok = produccion(d["margen"], d["fijo"], [d["horas"]], [d["H"]], [0, 0], M, d["demanda"])
    seg = enumerar_produccion(d["margen"], d["fijo"], [d["horas"]], [d["H"]], [0, 0], d["demanda"])
    assert abs(seg[0] - ok["z"]) < TOL
    mal = produccion(d["margen"], d["fijo"], [d["horas"]], [d["H"]], [0, 0], [d["M_mal"], M[1]], d["demanda"])
    return {"M": M, "M_horas": [d["H"] / h for h in d["horas"]], "ok": ok, "mal": mal, "perdida": ok["z"] - mal["z"],
            "por_hora": [d["margen"][i] / d["horas"][i] for i in range(2)]}


def makespan(seq, p):
    """Flow shop de permutación: término del último trabajo en la última máquina."""
    m = len(p[0])
    fin = [0.0] * m
    for j in seq:
        for k in range(m):
            fin[k] = max(fin[k], fin[k - 1] if k else 0) + p[j][k]
    return fin[-1]


def johnson(p):
    """Regla de Johnson para dos máquinas (empates por orden de trabajo)."""
    n = len(p)
    adelante = sorted([j for j in range(n) if p[j][0] <= p[j][1]], key=lambda j: (p[j][0], j))
    atras = sorted([j for j in range(n) if p[j][0] > p[j][1]], key=lambda j: (-p[j][1], j))
    return adelante + atras


def disyuntivo(p, relajar=False):
    """s_jk inicio, z_ijk (i < j) 1 si i va antes que j en k, Cmax. Devuelve el makespan."""
    n, m = len(p), len(p[0])
    M = sum(map(sum, p))
    pares = [(i, j) for i in range(n) for j in range(n) if i < j]
    ns, nz = n * m, len(pares) * m
    nv = ns + nz + 1
    S = lambda j, k: j * m + k
    Z = lambda q, k: ns + q * m + k
    filas = []
    for j in range(n):
        for k in range(m - 1):
            a = [0] * nv; a[S(j, k + 1)] = 1; a[S(j, k)] = -1; filas.append((a, p[j][k], INF))
    for q, (i, j) in enumerate(pares):
        for k in range(m):
            a = [0] * nv; a[S(i, k)] = 1; a[S(j, k)] = -1; a[Z(q, k)] = M; filas.append((a, -INF, M - p[i][k]))
            a = [0] * nv; a[S(j, k)] = 1; a[S(i, k)] = -1; a[Z(q, k)] = -M; filas.append((a, -INF, -p[j][k]))
    for j in range(n):
        a = [0] * nv; a[-1] = 1; a[S(j, m - 1)] = -1; filas.append((a, p[j][m - 1], INF))
    c = [0] * (nv - 1) + [1]
    z, x = resolver("min", c, filas, [(0, INF)] * ns + [(0, 1)] * nz + [(0, INF)], [0] * ns + [1] * nz + [0], relajar)
    return z, M


def flowshop():
    d = FLOW
    p = d["p"]
    n = len(p)
    todas = {perm: makespan(perm, p) for perm in permutations(range(n))}
    opt = min(todas.values())
    optimas = [perm for perm, v in todas.items() if abs(v - opt) < TOL]
    jo = johnson(p)
    z, M = disyuntivo(p)
    zr, _ = disyuntivo(p, relajar=True)
    assert abs(z - opt) < TOL and abs(makespan(jo, p) - opt) < TOL
    cota = max(sum(r[0] for r in p) + min(r[1] for r in p), sum(r[1] for r in p) + min(r[0] for r in p))
    assert abs(cota - opt) < TOL and abs(zr - max(map(sum, p))) < TOL   # la cota prueba el óptimo; la relajación es el trabajo más largo
    nombre = lambda seq: ", ".join(d["trabajos"][j] for j in seq)
    peor = max(todas.values())
    return {"opt": opt, "n_opt": len(optimas), "optimas": [nombre(s) for s in optimas], "johnson": nombre(jo),
            "M": M, "rel": zr, "cota": cota, "peor": peor, "orden_dado": makespan(tuple(range(n)), p),
            "suma_M1": sum(r[0] for r in p), "suma_M2": sum(r[1] for r in p), "n_seq": len(todas),
            "n_binarias": len([1 for i in range(n) for j in range(n) if i < j]) * len(p[0])}


def e03():
    d = FLOW3
    p = d["p"]
    todas = {perm: makespan(perm, p) for perm in permutations(range(len(p)))}
    opt = min(todas.values())
    z, M = disyuntivo(p)
    zr, _ = disyuntivo(p, relajar=True)
    assert abs(zr - max(map(sum, p))) < TOL
    assert abs(z - opt) < TOL      # con tres máquinas el óptimo no necesita órdenes distintas por máquina
    nombre = lambda seq: "".join(d["trabajos"][j] for j in seq)
    return {"todas": {nombre(k): v for k, v in todas.items()}, "opt": opt,
            "optimas": [nombre(k) for k, v in todas.items() if abs(v - opt) < TOL], "M": M, "rel": zr,
            "max_trabajo": max(map(sum, p))}

def e04():
    d = POTENCIA
    n = len(d["kw"])
    def elegir(pico):
        z, x = resolver("min", d["cargo"], [([1] * n, 1, 1), (d["kw"], pico, INF)], [(0, 1)] * n, [1] * n)
        return z, d["kw"][int(np.argmax(x))]
    z, kw = elegir(d["pico"])
    z2, kw2 = elegir(d["pico_corrido"])
    # extensión con la binaria «correr el horno»: min Σ cargo y + c·w  s.a. Σ kw y ≥ pico − (pico − pico_corrido) w
    c = d["cargo"] + [d["costo_correr"]]
    z3, x3 = resolver("min", c, [([1] * n + [0], 1, 1), (d["kw"] + [d["pico"] - d["pico_corrido"]], d["pico"], INF)],
                      [(0, 1)] * (n + 1), [1] * (n + 1))
    assert abs(z3 - min(z, z2 + d["costo_correr"])) < TOL
    return {"costo": z, "kw": kw, "costo_corrido": z2, "kw_corrido": kw2, "total_corrido": z2 + d["costo_correr"],
            "ahorro": z - (z2 + d["costo_correr"]), "correr": round(x3[-1])}


def e05():
    d = KDEN
    c, U = d["c"], d["cota"]
    def maxlhs(a):
        return sum(max(v * U, 0) for v in a)
    def minlhs(a):
        return sum(min(v * U, 0) for v in a)
    M = [maxlhs(a) - b if s == "<=" else b - minlhs(a) for a, s, b in d["filas"]]
    def lp(cuales):
        A_ub, b_ub = [], []
        for i in cuales:
            a, s, b = d["filas"][i]
            if s == "<=":
                A_ub.append(a); b_ub.append(b)
            else:
                A_ub.append([-v for v in a]); b_ub.append(-b)
        r = linprog([-v for v in c], A_ub=A_ub, b_ub=b_ub, bounds=[(0, U)] * 2, method="highs")
        return (-r.fun, list(r.x)) if r.status == 0 else (None, None)
    todas = lp(range(4))
    sub = {}
    for fuera in range(4):
        sub[fuera] = lp([i for i in range(4) if i != fuera])
    mejor_fuera = max(sub, key=lambda k: sub[k][0])
    # el mismo resultado con el modelo de binarias (w_i = 1 si la restricción i se exige)
    n = 2
    cc = list(c) + [0] * 4
    filas = []
    for i, (a, s, b) in enumerate(d["filas"]):
        w = [0] * 4
        if s == "<=":   # a x ≤ b + M(1 − w)  →  a x + M w ≤ b + M
            w[i] = M[i]; filas.append((list(a) + w, -INF, b + M[i]))
        else:           # a x ≥ b − M(1 − w)  →  a x − M w ≥ b − M
            w[i] = -M[i]; filas.append((list(a) + w, b - M[i], INF))
    filas.append(([0, 0, 1, 1, 1, 1], d["K"], INF))
    z, x = resolver("max", cc, filas, [(0, U)] * 2 + [(0, 1)] * 4, [0, 0, 1, 1, 1, 1])
    assert abs(z - sub[mejor_fuera][0]) < TOL
    return {"M": M, "todas": todas, "sub": sub, "fuera": mejor_fuera, "z": z, "x": x[:2]}


def e06():
    d = IMPR
    def modo(m):
        filas = [(d["horas"][m], -INF, d["H"])]
        cot = [(0, d["demanda"][0]), (0, d["demanda"][1])]
        if m == "PLA":
            cot[1] = (0, min(d["demanda"][1], d["topeCarcasaPLA"]))
        else:
            cot[0] = (0, min(d["demanda"][0], d["topeSoportePETG"]))
            cot[1] = (d["pedidoCarcasaPETG"], d["demanda"][1])
        return resolver("max", d["margen"][m], filas, cot, [1, 1])
    pla, petg = modo("PLA"), modo("PETG")
    # el modelo con una sola binaria y variables desdobladas
    # x = [PLA_s, PLA_c, PETG_s, PETG_c, w]
    c = d["margen"]["PLA"] + d["margen"]["PETG"] + [0]
    filas = [(d["horas"]["PLA"] + [0, 0, d["H"]], -INF, d["H"]),
             ([0, 1, 0, 0, d["topeCarcasaPLA"]], -INF, d["topeCarcasaPLA"]),
             ([0, 0] + d["horas"]["PETG"] + [-d["H"]], -INF, 0),
             ([0, 0, 0, 1, -d["pedidoCarcasaPETG"]], 0, INF),
             ([0, 0, 1, 0, -d["topeSoportePETG"]], -INF, 0),
             ([1, 0, 1, 0, 0], -INF, d["demanda"][0]), ([0, 1, 0, 1, 0], -INF, d["demanda"][1])]
    z, x = resolver("max", c, filas, [(0, INF)] * 4 + [(0, 1)], [1] * 5)
    assert abs(z - max(pla[0], petg[0])) < TOL
    return {"PLA": pla, "PETG": petg, "z": z, "x": x, "w": round(x[4]),
            "horas_PETG": float(np.dot(d["horas"]["PETG"], petg[1])), "horas_PLA": float(np.dot(d["horas"]["PLA"], pla[1]))}


def e07():
    d = CERA
    a1, a2 = d["anchos"]
    p1, p2, p3 = d["precios"]
    def costo(q):
        t1 = min(q, a1); t2 = min(max(q - a1, 0), a2); t3 = max(q - a1 - a2, 0)
        return p1 * t1 + p2 * t2 + p3 * t3, (t1, t2, t3)
    C, tramos = costo(d["compra"])
    # sin binarias: el LP llena primero el tramo barato (función cóncava en un mínimo)
    r = linprog(d["precios"], A_eq=[[1, 1, 1]], b_eq=[d["compra"]],
                bounds=[(0, a1), (0, a2), (0, d["bodega"] - a1 - a2)], method="highs")
    # con binarias: q1 ≥ a1 z2, q2 ≤ a2 z2, q2 ≥ a2 z3, q3 ≤ (bodega − a1 − a2) z3
    M3 = d["bodega"] - a1 - a2
    filas = [([1, 1, 1, 0, 0], d["compra"], d["compra"]), ([1, 0, 0, -a1, 0], 0, INF), ([0, 1, 0, -a2, 0], -INF, 0),
             ([0, 1, 0, 0, -a2], 0, INF), ([0, 0, 1, 0, -M3], -INF, 0), ([0, 0, 0, -1, 1], -INF, 0)]
    z, x = resolver("min", d["precios"] + [0, 0], filas, [(0, a1), (0, a2), (0, M3), (0, 1), (0, 1)], [0, 0, 0, 1, 1])
    assert abs(z - C) < TOL
    return {"costo": C, "tramos": tramos, "lp_sin_binarias": r.fun, "lp_x": list(r.x), "M3": M3,
            "promedio": C / d["compra"]}


def e08():
    d = POLAR
    n = len(d["precio"])
    def costo(q):
        for s in range(n):
            if d["desde"][s] <= q <= d["hasta"][s]:
                return d["precio"][s] * q
    # modelo: q_s ∈ [desde_s y_s, hasta_s y_s], Σ y = 1, Σ q ≥ necesita
    c = d["precio"] + [0] * n
    filas = [([0] * n + [1] * n, 1, 1), ([1] * n + [0] * n, d["necesita"], INF)]
    for s in range(n):
        a = [0] * (2 * n); a[s] = 1; a[n + s] = -d["hasta"][s]; filas.append((a, -INF, 0))
        a = [0] * (2 * n); a[s] = 1; a[n + s] = -d["desde"][s]; filas.append((a, 0, INF))
    z, x = resolver("min", c, filas, [(0, INF)] * n + [(0, 1)] * n, [1] * (2 * n))
    q = sum(x[:n])
    # fuerza bruta sobre la cantidad comprada
    bruto = min((costo(qq), qq) for qq in range(d["necesita"], d["hasta"][-1] + 1))
    assert abs(bruto[0] - z) < TOL and abs(bruto[1] - q) < TOL
    return {"costo": z, "q": q, "costo_justo": costo(d["necesita"]), "ahorro": costo(d["necesita"]) - z,
            "sobra": q - d["necesita"], "costo_600": costo(600), "umbral": d["precio"][1] * d["desde"][1] / d["precio"][0]}


def e09():
    d = KOMBU
    nS, nT = len(d["sabores"]), len(d["turnos"])
    def modelo(demanda, max_sab, M=None, relajar=False):
        M = M or [min(demanda[i], max(d["cap"])) for i in range(nS)]
        # x (nS) · y (nS) · t (nT)
        c = list(d["margen"]) + [-f for f in d["fijo"]] + [-c for c in d["costo"]]
        filas = [([0] * (2 * nS) + [1] * nT, 1, 1),
                 ([1] * nS + [0] * nS + [-k for k in d["cap"]], -INF, 0),
                 ([0] * nS + [1] * nS + [0] * nT, -INF, max_sab)]
        for i in range(nS):
            a = [0] * (2 * nS + nT); a[i] = 1; a[nS + i] = -M[i]; filas.append((a, -INF, 0))
            a = [0] * (2 * nS + nT); a[i] = 1; a[nS + i] = -d["minimo"][i]; filas.append((a, 0, INF))
        cot = [(0, demanda[i]) for i in range(nS)] + [(0, 1)] * (nS + nT)
        z, x = resolver("max", c, filas, cot, [0] * nS + [1] * (nS + nT), relajar)
        return {"z": z, "x": x[:nS], "y": x[nS:2 * nS], "t": x[2 * nS:]}
    base = modelo(d["demanda"], d["max_sabores"])
    sin_tope = modelo(d["demanda"], nS)
    dem_baja = list(d["demanda"]); dem_baja[1] = d["frambuesa_baja"]
    baja = modelo(dem_baja, d["max_sabores"])
    rel = modelo(d["demanda"], d["max_sabores"], relajar=True)
    relg = modelo(d["demanda"], d["max_sabores"], M=[d["M_grande"]] * nS, relajar=True)
    # segundo camino: enumerar sabores (≤ 2) y turno; dentro, llenar por margen
    def bruto(demanda, max_sab):
        mejor = None
        for k in range(nS + 1):
            for S in combinations(range(nS), k):
                if k > max_sab or any(d["minimo"][i] > demanda[i] for i in S):
                    continue
                for tt in range(nT):
                    cap = d["cap"][tt]
                    if sum(d["minimo"][i] for i in S) > cap:
                        continue
                    x = {i: d["minimo"][i] for i in S}
                    resto = cap - sum(x.values())
                    for i in sorted(S, key=lambda i: -d["margen"][i]):
                        extra = min(resto, demanda[i] - x[i]); x[i] += extra; resto -= extra
                    z = sum(d["margen"][i] * x[i] - d["fijo"][i] for i in S) - d["costo"][tt]
                    if mejor is None or z > mejor[0]:
                        mejor = (z, S, tt)
        return mejor
    assert abs(bruto(d["demanda"], d["max_sabores"])[0] - base["z"]) < TOL
    assert abs(bruto(d["demanda"], nS)[0] - sin_tope["z"]) < TOL
    assert abs(bruto(dem_baja, d["max_sabores"])[0] - baja["z"]) < TOL
    return {"base": base, "sin_tope": sin_tope, "valor_tope": sin_tope["z"] - base["z"], "baja": baja, "rel": rel,
            "relg": relg, "gap": (rel["z"] - base["z"]) / base["z"], "gapg": (relg["z"] - base["z"]) / base["z"]}


def e10():
    d = TERRAZA
    M = [min(d["demanda"][i], min(d["disp"][r] / d["uso"][r][i] for r in range(2))) for i in range(2)]
    ok = produccion(d["margen"], d["fijo"], d["uso"], d["disp"], d["minimo"], M, d["demanda"])
    seg = enumerar_produccion(d["margen"], d["fijo"], d["uso"], d["disp"], d["minimo"], d["demanda"])
    assert abs(seg[0] - ok["z"]) < TOL
    mal_M = produccion(d["margen"], d["fijo"], d["uso"], d["disp"], d["minimo"], [d["M_mal"], M[1]], d["demanda"])
    mal_obj = produccion(d["margen"], d["fijo"], d["uso"], d["disp"], d["minimo"], M, d["demanda"], objetivo_mal=True)
    # lo que de verdad deja el plan del objetivo mal escrito
    real_obj = sum(d["margen"][i] * mal_obj["x"][i] - d["fijo"][i] * (mal_obj["x"][i] > 0.5) for i in range(2))
    piso = produccion(d["margen"], d["fijo"], d["uso"], d["disp"], d["minimo"], M, d["demanda"], piso_sin_y=True)
    return {"M": M, "ok": ok, "mal_M": mal_M, "perdida_M": ok["z"] - mal_M["z"], "mal_obj": mal_obj,
            "real_obj": real_obj, "piso": piso,
            "usado": [float(np.dot(d["uso"][r], ok["x"])) for r in range(2)]}


# ---------------------------------------------------------------- todo junto
def resultados():
    return {"velas": velas(), "caso": segunda_maquina(), "flow": flowshop(), "e01": e01(), "e02": e02(), "e03": e03(), "e04": e04(),
            "e05": e05(), "e06": e06(), "e07": e07(), "e08": e08(), "e09": e09(), "e10": e10()}


def cadena(R):
    C = caso_modulo().calcular()["u3"]
    v = R["caso"]
    ok = abs(v["utilidad"] - C["utilidad"]) < TOL and round(v["cajas"]) == C["cajas"] and round(v["compra"]) == C["compra"]
    ok &= abs(v["equilibrio"] - C["cajas_equilibrio"]) < TOL
    print("CADENA:", "OK, la segunda máquina calza con el caso (compra, 136 cajas, $852.400, equilibrio 89,67)"
          if ok else "NO calza")
    return ok


def relajar_texto(mod):
    """La relajación lineal en OPL: cada boolean pasa a float entre 0 y 1."""
    return re.sub(r"dvar boolean\s+(\w+(\[[^\]]+\])*);", r"dvar float \1 in 0..1;", mod)


def comparar_con_opl(R):
    if correr(MODELOS / "u03_segunda_maquina.mod", MODELOS / "u03_segunda_maquina.dat") is None:
        print("OPL: oplrun no está instalado; se comparan solo las cifras de Python")
        return None
    V, C = R["velas"], R["caso"]
    casos = {
        "velas": ("u03_velas.mod", "u03_velas.dat", V["entero"]["z"],
                  {**{f"x[{v}]": V["entero"]["x"][i] for i, v in enumerate(VELAS["velas"])},
                   **{f"M[{v}]": V["M"][i] for i, v in enumerate(VELAS["velas"])}}),
        "caso": ("u03_segunda_maquina.mod", "u03_segunda_maquina.dat", C["utilidad"], {"q": C["cajas"], "y": C["compra"]}),
        "e06": ("u03_e06_impresion.mod", "u03_e06_impresion.dat", R["e06"]["z"], {"w": R["e06"]["w"]}),
        "e07": ("u03_e07_cera.mod", "u03_e07_cera.dat", R["e07"]["costo"], {"q": CERA["compra"]}),
        "flow": ("u03_flowshop.mod", "u03_flowshop.dat", R["flow"]["opt"], {"makespan": R["flow"]["opt"]}),
        "e09": ("u03_e09_kombucha.mod", "u03_e09_kombucha.dat", R["e09"]["base"]["z"],
                {f"x[{s}]": R["e09"]["base"]["x"][i] for i, s in enumerate(KOMBU["sabores"])}),
    }
    for k, (mod, dat, z, vals) in casos.items():
        r = correr(MODELOS / mod, MODELOS / dat)
        assert r["codigo"] == 0 and r["objetivo"] is not None, (k, r["salida"][-400:])
        assert abs(r["objetivo"] - z) < 1e-4, (k, r["objetivo"], z)
        for clave, val in vals.items():
            assert abs(r["valores"][clave] - val) < 1e-4, (k, clave, r["valores"][clave], val)
        if k == "flow":   # el orden de OPL es el mismo en las dos máquinas y es una de las secuencias óptimas
            o1, o2 = (r["valores"][f"orden[{m}]"] for m in FLOW["maquinas"])
            assert o1 == o2, (o1, o2)
            assert o1.replace("-", ", ") in R["flow"]["optimas"], o1
            R["opl"] = {"flow": o1}
    # relajaciones lineales en OPL: velas con M ajustada y con M = 10.000; caso con M = 136 y M = 1.000
    tmp = Path(tempfile.mkdtemp(prefix="u03_rel_"))
    try:
        mod = relajar_texto((MODELOS / "u03_velas.mod").read_text(encoding="utf-8"))
        f = tmp / "velas_rel.mod"; f.write_text(mod.replace("dvar int+    x", "dvar float+  x"), encoding="utf-8")
        r = correr(f, MODELOS / "u03_velas.dat")
        assert abs(r["valores"]["utilidad"] - V["rel_ajustada"]["z"]) < 1e-3, (r["valores"]["utilidad"], V["rel_ajustada"]["z"])
        g = tmp / "velas_rel_M.mod"
        g.write_text(f.read_text(encoding="utf-8").replace(
            "float M[v in Velas] = minl(demanda[v], min(r in Recursos) disp[r] / uso[r][v]);",
            f"float M[v in Velas] = {VELAS['M_grande']};"), encoding="utf-8")
        r = correr(g, MODELOS / "u03_velas.dat")
        assert abs(r["valores"]["utilidad"] - V["rel_grande"]["z"]) < 1e-3, (r["valores"]["utilidad"], V["rel_grande"]["z"])
        mod = relajar_texto((MODELOS / "u03_segunda_maquina.mod").read_text(encoding="utf-8")).replace("dvar int+    q", "dvar float+  q")
        f = tmp / "caso_rel.mod"; f.write_text(mod, encoding="utf-8")
        r = correr(f, MODELOS / "u03_segunda_maquina.dat")
        assert abs(r["valores"]["utilidad"] - C["rel_ajustada"]) < 1e-3
        h = tmp / "caso_1000.dat"
        h.write_text((MODELOS / "u03_segunda_maquina.dat").read_text(encoding="utf-8").replace(
            "M      = 136;", "M      = 1000;"), encoding="utf-8")
        r = correr(f, h)
        assert abs(r["valores"]["utilidad"] - C["rel_1000"]) < 1e-3
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("OPL: 6 modelos y 4 relajaciones corridos con oplrun; objetivo y variables coinciden con Python")
    return True


# ---------------------------------------------------------------- cifras que el .md tiene que contener
def esperados(R):
    V, C = R["velas"], R["caso"]
    s = []
    # ejemplo
    E = V["entero"]
    s += [pesos(E["z"]), f"{num(E['x'][0])} velas de frasco", f"{num(E['x'][2])} derretibles", num(V["M_cera"][0]),
          num(V["M_vertido"][0]), num(V["M_cera"][1]), num(V["M_vertido"][2]), num(V["M_cera"][2]),
          pesos(V["sin_piso"]["z"]), num(V["sin_piso"]["x"][1]), num(V["sin_piso"]["x"][0]), num(V["sin_piso"]["x"][2]),
          pesos(V["rel_ajustada"]["z"], 0), pesos(V["rel_grande"]["z"], 0), pct(V["gap_ajustada"]), pct(V["gap_grande"]),
          fmt(V["rel_ajustada"]["y"][0], 3), fmt(V["rel_ajustada"]["y"][1], 3), fmt(V["rel_grande"]["y"][2], 3),
          fmt(V["rel_ajustada"]["x"][0], 2), fmt(V["rel_ajustada"]["x"][1], 2), pesos(V["lp_sin_fijo"]["z"], 0),
          pesos(V["fijo_pagado_rel"][0], 0), pesos(V["fijo_pagado_grande"][2], 0)]
    # caso
    s += [pesos(C["utilidad"]), "136 cajas", fmt(C["equilibrio"], 2), pesos(C["ingreso"]), pesos(C["rel_ajustada"]),
          pesos(C["rel_1000"]), fmt(C["rel_1000_y"], 3), pesos(C["fijo_pagado_1000"]), pesos(-C["perdida_85"]),
          pesos(C["u2_valor"]), pesos(C["u2_inversion"])]
    # 3.1
    e = R["e01"]; s += [fmt(e["equilibrio"], 2), pesos(e["utilidad"]), pesos(e["ingreso_feria"]), pesos(-e["perdida_feria"])]
    # 3.2
    e = R["e02"]; s += [fmt(e["M_horas"][0], 1), num(e["M_horas"][1]), pesos(e["ok"]["z"]), num(e["ok"]["x"][1]),
                        pesos(e["mal"]["z"]), num(e["mal"]["x"][1]), pesos(e["perdida"]), pesos(e["por_hora"][0], 1),
                        pesos(e["por_hora"][1], 1)]
    # sección 9 · flow shop
    F = R["flow"]
    s += [f"makespan de {num(F['opt'])} h", F["johnson"], f"{F['n_opt']} secuencias", f"de {F['n_seq']}", f"$M = {num(F['M'])}$",
          f"{num(F['rel'])} h", f"{num(F['peor'])} h", f"{num(F['orden_dado'])} h", f"{num(F['n_binarias'])} binarias"]
    s += [", ".join(o.split(", ")) for o in F["optimas"]]
    if "opl" in R:
        s.append(R["opl"]["flow"].replace("-", ", "))
    # 3.3
    e = R["e03"]
    s += [f"| {k} | {num(v)} |" for k, v in e["todas"].items()]
    s += [f"M = {num(e['M'])}", f"{num(e['rel'])} h", f"{num(e['opt'])} h"]
    # 3.4
    e = R["e04"]; s += [pesos(e["costo"]), f"{e['kw']} kW", pesos(e["costo_corrido"]), pesos(e["total_corrido"]),
                        pesos(e["ahorro"])]
    # 3.5
    e = R["e05"]; s += [f"M_{i + 1} = {num(m)}" for i, m in enumerate(e["M"])]
    s += [num(e["todas"][0]), num(e["z"]), f"({num(e['x'][0])}; {num(e['x'][1])})"]
    s += [num(e["sub"][k][0]) for k in range(4) if e["sub"][k][0] is not None]
    # 3.6
    e = R["e06"]; s += [pesos(e["PLA"][0]), pesos(e["PETG"][0]), f"{num(e['PLA'][1][0])} soportes",
                        f"{num(e['PLA'][1][1])} carcasas", f"{num(e['PETG'][1][1])} carcasas", fmt(e["horas_PLA"], 1),
                        fmt(e["horas_PETG"], 1)]
    # 3.7
    e = R["e07"]; s += [pesos(e["costo"]), pesos(e["lp_sin_binarias"]), fmt(e["promedio"], 1), num(e["M3"])]
    # 3.8
    e = R["e08"]; s += [pesos(e["costo"]), f"{num(e['q'])} m", pesos(e["costo_justo"]), pesos(e["ahorro"]),
                        pesos(e["costo_600"]), fmt(e["umbral"], 1)]
    # 3.9
    e = R["e09"]; b = e["base"]
    s += [pesos(b["z"]), pesos(e["sin_tope"]["z"]), pesos(e["valor_tope"]), pesos(e["baja"]["z"]),
          pesos(e["rel"]["z"]), pesos(e["relg"]["z"]), pct(e["gap"]), pct(e["gapg"])]
    # 3.10
    e = R["e10"]; s += [num(e["M"][0]), num(e["M"][1]), pesos(e["ok"]["z"]), num(e["ok"]["x"][0]), num(e["ok"]["x"][1]),
                        pesos(e["mal_M"]["z"]), pesos(e["perdida_M"]), num(e["mal_M"]["x"][1]), num(e["usado"][0])]
    return s


def codigo_en_md(md):
    faltan = []
    for f in ["u03_velas.mod", "u03_velas.dat", "u03_segunda_maquina.mod", "u03_segunda_maquina.dat",
              "u03_flowshop.mod", "u03_flowshop.dat"]:
        for linea in (MODELOS / f).read_text(encoding="utf-8").splitlines():
            if linea.strip() and linea.rstrip() not in md:
                faltan.append(f"{f}: {linea.strip()}")
    return faltan


# ---------------------------------------------------------------- figuras
def figuras(R):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "path",
                         "axes.edgecolor": SUAVE, "axes.labelcolor": TINTA, "xtick.color": SUAVE, "ytick.color": SUAVE})
    carpeta = RAMO / "unidades" / "figuras"
    carpeta.mkdir(parents=True, exist_ok=True)
    u = R["caso"]["datos"]
    m, k, U = u["margen_extra_por_caja"], u["costo_fijo_maquina"], u["cajas_max_maquina"]
    q = np.linspace(0, U, 300)
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot([0], [0], "o", color=ACENTO, ms=6, zorder=5)
    ax.plot(q[q > 0.5], (m * q[q > 0.5] - k) / 1e6, color=ACENTO, lw=2.4, label="utilidad real (paga el costo fijo completo)")
    ax.plot(q, (m * q - k * q / U) / 1e6, color=TINTA, lw=1.4, ls="--", label=f"relajación con M = {U} (paga k·q/{U})")
    ax.plot(q, (m * q - k * q / 1000) / 1e6, color=SUAVE, lw=1.2, ls=":", label="relajación con M = 1.000")
    ax.axhline(0, color=LINEA, lw=1)
    eq = k / m
    ax.axvline(eq, color=LINEA, lw=1, ls="--")
    ax.text(eq + 1.5, -1.45, f"equilibrio\n{fmt(eq, 2)} cajas", fontsize=8.5, color=TINTA, va="bottom")
    ax.annotate(f"{pesos(m * U - k)}", xy=(U, (m * U - k) / 1e6), xytext=(U - 50, 1.0), fontsize=9, color=TINTA,
                arrowprops=dict(arrowstyle="->", color=TINTA, lw=0.9))
    ax.annotate(f"{pesos(m * U - k * U / 1000)}", xy=(U, (m * U - k * U / 1000) / 1e6), xytext=(U - 52, 2.35),
                fontsize=9, color=SUAVE, arrowprops=dict(arrowstyle="->", color=SUAVE, lw=0.9))
    ax.annotate("salto de $1.650.000", xy=(1.5, -k / 1e6), xytext=(22, -1.72), fontsize=8.5, color=ACENTO, va="center",
                arrowprops=dict(arrowstyle="->", color=ACENTO, lw=0.9))
    ax.set_xlabel("cajas extra en la segunda máquina (q)")
    ax.set_ylabel("millones de pesos")
    ax.set_xlim(0, U + 4); ax.set_ylim(-1.8, 2.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(carpeta / "u03_costo_fijo.svg", metadata={"Date": None})
    plt.close(fig)
    print("figuras: u03_costo_fijo.svg")


if __name__ == "__main__":
    R = resultados()
    for k, v in R.items():
        print(f"== {k}")
        if isinstance(v, dict):
            for kk, vv in v.items():
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
