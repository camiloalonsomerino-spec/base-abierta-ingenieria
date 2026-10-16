"""Unidad 6 · Modelos con varios objetivos.

Recalcula todas las cifras de la unidad desde los datos: matrices de pagos, ideal y nadir, fronteras
de soluciones no dominadas (por ε-restricción), suma ponderada normalizada, programación por metas y
por prioridades. Cada modelo lineal se resuelve en Python (scipy, HiGHS) y, si hay CPLEX, también con
su .mod de OPL; tienen que coincidir. Con --revisar busca cada resultado en el .md.

    python u06_varios_objetivos.py            # imprime los resultados y compara con OPL
    python u06_varios_objetivos.py --revisar  # además los busca en el .md
    python u06_varios_objetivos.py --figuras  # además redibuja las figuras SVG
    python u06_varios_objetivos.py --modelos  # además reescribe los .dat desde estos datos
"""
from pathlib import Path
from itertools import combinations
import importlib.util, sys, tempfile

import numpy as np
from scipy.optimize import linprog

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402

TOL = 1e-6


# ---------------------------------------------------------------- herramientas

def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x, 0)


def n(x, dec=0):
    return fmt(round(x, 9) + 0.0, dec)


def lp(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, bounds=None, maximizar=False):
    """Resuelve y devuelve x, z (en el sentido pedido) y los duales de A_ub como ∂z/∂b."""
    s = -1 if maximizar else 1
    r = linprog([s * v for v in c], A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    assert r.status == 0, r.message
    dual = [s * m for m in r.ineqlin.marginals] if A_ub is not None else []
    return {"x": np.array(r.x), "z": s * r.fun, "dual": dual}


def comparar_opl(nombre, mod, dat_txt, esperado, R_opl):
    """Corre el .mod con un .dat (texto) y compara cada «clave = valor» con lo calculado en Python."""
    with tempfile.TemporaryDirectory() as tmp:
        dat = Path(tmp) / "datos.dat"
        dat.write_text(dat_txt, encoding="utf-8")
        r = correr(MODELOS / mod, dat)
    if r is None:
        R_opl[nombre] = "sin CPLEX"
        return True
    malas = [(k, v, r["valores"].get(k)) for k, v in esperado.items()
             if not isinstance(r["valores"].get(k), float) or abs(r["valores"][k] - v) > 1e-5 * max(1, abs(v))]
    R_opl[nombre] = "OK" if not malas else malas
    return not malas


def no_dominados(puntos, sentidos):
    """puntos: lista de tuplas de objetivos; sentidos: +1 si se maximiza, −1 si se minimiza."""
    def domina(a, b):
        mejor_o_igual = all(s * x >= s * y for x, y, s in zip(a, b, sentidos))
        return mejor_o_igual and any(s * x > s * y for x, y, s in zip(a, b, sentidos))
    return [p for p in puntos if not any(domina(q, p) for q in puntos)]


# ---------------------------------------------------------------- datos (originales; pasados por colisiones.py)

# Ejemplo resuelto · huerto familiar en Quillón: x m² de tomate, y m² de lechuga
HUERTO = {"margen": [2600, 1400], "agua": [1100, 450],             # $ y litros por m² en la temporada
          "superficie": 120, "trabajo": [168, 84], "horas": 15120,       # minutos por m² y minutos disponibles
          "tomate_min": 20, "lechuga_max": 90,
          "meta_margen": 200000, "meta_agua": 68000, "pesos_metas": [(0.5, 0.5), (0.7, 0.3)],
          "pesos_suma": [0.5, 0.7]}

# 6.1 · siete departamentos: arriendo mensual y minutos a la universidad
E61 = {"A": (520000, 35), "B": (480000, 50), "C": (610000, 20), "D": (550000, 40), "E": (450000, 65),
       "F": (590000, 25), "G": (500000, 55)}

# 6.2 · matriz de pagos de un plan de buses: costo (MM$, mín), cobertura (%, máx), emisiones (t, mín)
E62 = {"pagos": [[12.4, 61, 830], [19.8, 88, 1140], [15.1, 70, 610]], "sentidos": [-1, 1, -1],
       "solucion": [16.0, 80, 760], "w": [0.5, 0.3, 0.2]}

# 6.3 · una solución contra tres metas
E63 = {"utilidad": 4.6, "meta_utilidad": 5.0, "extra": 52, "meta_extra": 40, "cuota": 27, "meta_cuota": 30,
       "w": (0.5, 0.3, 0.2)}

# 6.4 · cuatro proveedores: precio ($/unidad, mín), plazo (días, mín), fallas (%, mín)
E64 = {"P1": (8400, 12, 2.1), "P2": (7900, 20, 3.4), "P3": (9100, 7, 1.3), "P4": (8700, 15, 1.7), "w": (0.5, 0.3, 0.2)}

# 6.5 · cooperativa de reciclaje: x t de PET, y t de cartón; ingreso (miles de $, máx) y viajes (mín)
E65 = {"ingreso": [180, 90], "viajes": [3, 4], "pet_max": 30, "carton_max": 35, "contrato_min": 25,
       "planta_max": 50, "pesos": [0.5, 0.7]}

# 6.6 a 6.8 · mueblería: sillas, mesas, estantes
MUEBLES = {"utilidad": [17000, 45000, 32000], "horas": [2, 5, 3.4], "madera": [0.65, 2.25, 1.75],
           "horas_max": 480, "madera_max": 225, "dem_max": [135, 90, 50],
           "meta_utilidad": 4000000, "meta_horas": 410, "meta_mesas": 60,
           "pesos": [(0.5, 0.3, 0.2), (1 / 3, 1 / 3, 1 / 3)], "eps": [300, 360, 410, 450, 480]}

# 6.9 · cinco proyectos, presupuesto 10 MM$: (costo, VAN, empleos)
E69 = {"proyectos": {"P1": (6, 9, 2), "P2": (4, 5, 3), "P3": (5, 3, 8), "P4": (5, 2, 9), "P5": (3, 2, 4)},
       "presupuesto": 10, "meta_van": 8}

# 6.10 · transporte con dos objetivos: costo ($/t) y emisiones (kg CO2/t)
E610 = {"orig": ["Norte", "Sur"], "dest": ["D1", "D2", "D3"], "oferta": [620, 480], "demanda": [340, 410, 290],
        "costo": [[2100, 3400, 4800], [3900, 2600, 2900]], "co2": [[38, 22, 95], [72, 55, 44]], "tolerancia": 0.01}


def frontera_eps(f, lo, hi):
    """Quiebres de la frontera z(ε) = máx objetivo con el segundo objetivo ≤ ε, entre lo y hi.
    f(ε) devuelve el LP resuelto; su último dual es la pendiente del tramo. Cada quiebre se calcula
    exacto como la intersección de las rectas de los dos tramos vecinos."""
    pts = [(lo, f(lo)["z"])]
    a = lo
    while a < hi - 1e-9:
        ra = f(a + 1e-6)
        lam = ra["dual"][-1]
        rh = f(hi)
        if abs(rh["dual"][-1] - lam) < 1e-7 or abs(rh["z"] - (pts[-1][1] + lam * (hi - pts[-1][0]))) < 1e-6:
            pts.append((hi, rh["z"]))
            break
        izq, der = a + 1e-6, hi
        for _ in range(100):
            mid = (izq + der) / 2
            if abs(f(mid)["dual"][-1] - lam) < 1e-7:
                izq = mid
            else:
                der = mid
        # recta del tramo siguiente, medida un poco más allá del quiebre
        e2 = min(der + 1e-3, hi)
        r2 = f(e2)
        lam2 = r2["dual"][-1]
        e0, z0 = pts[-1]
        q = (r2["z"] - lam2 * e2 - z0 + lam * e0) / (lam - lam2)
        pts.append((q, z0 + lam * (q - e0)))
        a = q
    return pts


# ---------------------------------------------------------------- ejemplo · huerto

def huerto_restr(d):
    A = [[1, 1], d["trabajo"]]
    b = [d["superficie"], d["horas"]]
    bounds = [(d["tomate_min"], None), (0, d["lechuga_max"])]
    return A, b, bounds


def huerto(d):
    R = {}
    A, b, bounds = huerto_restr(d)
    M, W = d["margen"], d["agua"]
    # vértices de la región (enumerados) y sus objetivos
    lineas = [([1, 1], d["superficie"]), (d["trabajo"], d["horas"]), ([1, 0], d["tomate_min"]),
              ([0, 1], d["lechuga_max"]), ([0, 1], 0)]
    V = set()
    for (a1, b1), (a2, b2) in combinations(lineas, 2):
        Mx = np.array([a1, a2], float)
        if abs(np.linalg.det(Mx)) < 1e-9:
            continue
        p = np.linalg.solve(Mx, [b1, b2])
        if (p[0] >= d["tomate_min"] - 1e-9 and -1e-9 <= p[1] <= d["lechuga_max"] + 1e-9
                and np.dot([1, 1], p) <= d["superficie"] + 1e-9 and np.dot(d["trabajo"], p) <= d["horas"] + 1e-9):
            V.add((round(p[0], 6), round(p[1], 6)))
    V = sorted(V)
    R["vertices"] = [(x, y, np.dot(M, (x, y)), np.dot(W, (x, y))) for x, y in V]
    # matriz de pagos
    rm = lp(M, A, b, bounds=bounds, maximizar=True)
    ra = lp(W, A, b, bounds=bounds)
    R["pagos"] = [(rm["z"], np.dot(W, rm["x"]), rm["x"]), (np.dot(M, ra["x"]), ra["z"], ra["x"])]
    R["ideal"] = (rm["z"], ra["z"])
    R["nadir"] = (np.dot(M, ra["x"]), np.dot(W, rm["x"]))
    # frontera: vértices no dominados (máx margen, mín agua) y pendientes entre ellos
    pts = [(m, w) for _, _, m, w in R["vertices"]]
    nd = sorted(no_dominados(pts, [1, -1]), key=lambda p: p[1])
    R["frontera"] = nd
    R["pendientes"] = [(nd[k + 1][0] - nd[k][0]) / (nd[k + 1][1] - nd[k][1]) for k in range(len(nd) - 1)]
    # suma ponderada normalizada (utopía-nadir)
    u, na = R["ideal"], R["nadir"]
    R["umbrales"] = [(u[0] - na[0]) / ((u[0] - na[0]) + s * (na[1] - u[1])) for s in R["pendientes"]]
    R["suma"] = {}
    for w in d["pesos_suma"]:
        c = [w * M[i] / (u[0] - na[0]) - (1 - w) * W[i] / (na[1] - u[1]) for i in range(2)]
        r = lp(c, A, b, bounds=bounds, maximizar=True)
        R["suma"][w] = (r["x"], np.dot(M, r["x"]), np.dot(W, r["x"]), (1 - w) * (u[0] - na[0]) / (w * (na[1] - u[1])))
    # metas: margen ≥ meta (castiga d−), agua ≤ meta (castiga d+); variables x, y, dm−, dm+, da−, da+
    R["metas"] = {}
    for wm, wa in d["pesos_metas"]:
        c = [0, 0, wm / d["meta_margen"], 0, 0, wa / d["meta_agua"]]
        A_eq = [[M[0], M[1], 1, -1, 0, 0], [W[0], W[1], 0, 0, 1, -1]]
        r = lp(c, [list(f) + [0] * 4 for f in A], b, A_eq, [d["meta_margen"], d["meta_agua"]],
               bounds=bounds + [(0, None)] * 4)
        R["metas"][(wm, wa)] = r
    # prioridades: 1) margen ≥ meta, luego mín agua · 2) agua ≤ meta, luego máx margen
    r1 = lp(W, A + [[-M[0], -M[1]]], b + [-d["meta_margen"]], bounds=bounds)
    r2 = lp(M, A + [W], b + [d["meta_agua"]], bounds=bounds, maximizar=True)
    R["lex_margen"], R["lex_agua"] = r1, r2
    return R


# ---------------------------------------------------------------- ejercicios

def ej61(d):
    pts = {k: v for k, v in d.items()}
    nd = no_dominados(list(pts.values()), [-1, -1])
    nd_k = [k for k, v in pts.items() if v in nd]
    dom = {k: [j for j, w in pts.items() if j != k and w[0] <= v[0] and w[1] <= v[1] and w != v]
           for k, v in pts.items() if k not in nd_k}
    ideal = (min(v[0] for v in nd), min(v[1] for v in nd))
    nadir = (max(v[0] for v in nd), max(v[1] for v in nd))
    return {"nd": nd_k, "dom": dom, "ideal": ideal, "nadir": nadir}


def norm(f, u, na):
    return (f - na) / (u - na)


def ej62(d):
    P, s = d["pagos"], d["sentidos"]
    ideal = [P[k][k] for k in range(3)]
    nadir = [min(P[i][k] for i in range(3)) if s[k] > 0 else max(P[i][k] for i in range(3)) for k in range(3)]
    z = [norm(d["solucion"][k], ideal[k], nadir[k]) for k in range(3)]
    return {"ideal": ideal, "nadir": nadir, "norm": z, "puntaje": sum(w * v for w, v in zip(d["w"], z))}


def ej63(d):
    return {"d_util": d["meta_utilidad"] - d["utilidad"], "d_extra": d["extra"] - d["meta_extra"],
            "d_cuota": d["meta_cuota"] - d["cuota"],
            "rel": [(d["meta_utilidad"] - d["utilidad"]) / d["meta_utilidad"],
                    (d["extra"] - d["meta_extra"]) / d["meta_extra"], (d["meta_cuota"] - d["cuota"]) / d["meta_cuota"]],
            "penal": sum(w * r for w, r in zip(d["w"], [(d["meta_utilidad"] - d["utilidad"]) / d["meta_utilidad"],
                         (d["extra"] - d["meta_extra"]) / d["meta_extra"], (d["meta_cuota"] - d["cuota"]) / d["meta_cuota"]]))}


def ej64(d):
    prov = ["P1", "P2", "P3", "P4"]
    w = d["w"]
    crudo = {p: sum(wi * v for wi, v in zip(w, d[p])) for p in prov}
    u = [min(d[p][k] for p in prov) for k in range(3)]
    na = [max(d[p][k] for p in prov) for k in range(3)]
    nz = {p: [norm(d[p][k], u[k], na[k]) for k in range(3)] for p in prov}
    punt = {p: sum(wi * v for wi, v in zip(w, nz[p])) for p in prov}
    return {"crudo": crudo, "norm": nz, "puntaje": punt, "gana_crudo": min(crudo, key=crudo.get),
            "gana_norm": max(punt, key=punt.get)}


def ej65(d):
    A = [[1, 1], [-1, -1]]
    b = [d["planta_max"], -d["contrato_min"]]
    bounds = [(0, d["pet_max"]), (0, d["carton_max"])]
    I, V = d["ingreso"], d["viajes"]
    lineas = [([1, 1], d["planta_max"]), ([1, 1], d["contrato_min"]), ([1, 0], d["pet_max"]),
              ([0, 1], d["carton_max"]), ([1, 0], 0), ([0, 1], 0)]
    Vt = set()
    for (a1, b1), (a2, b2) in combinations(lineas, 2):
        Mx = np.array([a1, a2], float)
        if abs(np.linalg.det(Mx)) < 1e-9:
            continue
        p = np.linalg.solve(Mx, [b1, b2])
        if (-1e-9 <= p[0] <= d["pet_max"] + 1e-9 and -1e-9 <= p[1] <= d["carton_max"] + 1e-9
                and d["contrato_min"] - 1e-9 <= p.sum() <= d["planta_max"] + 1e-9):
            Vt.add((round(p[0], 6), round(p[1], 6)))
    vert = sorted((x, y, np.dot(I, (x, y)), np.dot(V, (x, y))) for x, y in Vt)
    ri = lp(I, A, b, bounds=bounds, maximizar=True)
    rv = lp(V, A, b, bounds=bounds)
    ideal = (ri["z"], rv["z"]); nadir = (np.dot(I, rv["x"]), np.dot(V, ri["x"]))
    nd = sorted(no_dominados([(f1, f2) for *_, f1, f2 in vert], [1, -1]), key=lambda p: p[1])
    pend = [(nd[k + 1][0] - nd[k][0]) / (nd[k + 1][1] - nd[k][1]) for k in range(len(nd) - 1)]
    suma = {}
    for w in d["pesos"]:
        c = [w * I[i] / (ideal[0] - nadir[0]) - (1 - w) * V[i] / (nadir[1] - ideal[1]) for i in range(2)]
        r = lp(c, A, b, bounds=bounds, maximizar=True)
        suma[w] = (r["x"], np.dot(I, r["x"]), np.dot(V, r["x"]),
                   (1 - w) * (ideal[0] - nadir[0]) / (w * (nadir[1] - ideal[1])))
    return {"vertices": vert, "ideal": ideal, "nadir": nadir, "frontera": nd, "pendientes": pend, "suma": suma}


def muebles_base(d):
    A = [d["horas"], d["madera"]]
    b = [d["horas_max"], d["madera_max"]]
    bounds = [(0, m) for m in d["dem_max"]]
    return A, b, bounds


def ej66(d):
    A, b, bounds = muebles_base(d)
    U, H = d["utilidad"], d["horas"]
    out = {"max_util": lp(U, A, b, bounds=bounds, maximizar=True),
           "max_util_400": lp(U, [H, d["madera"]], [d["meta_horas"], d["madera_max"]], bounds=bounds, maximizar=True)}
    for w in d["pesos"]:
        # variables: x1 x2 x3, du−, du+, dh−, dh+, dm−, dm+
        c = [0, 0, 0, w[0] / d["meta_utilidad"], 0, 0, w[1] / d["meta_horas"], w[2] / d["meta_mesas"], 0]
        A_eq = [U + [1, -1, 0, 0, 0, 0], H + [0, 0, 1, -1, 0, 0], [0, 1, 0, 0, 0, 0, 0, 1, -1]]
        r = lp(c, [f + [0] * 6 for f in A], b, A_eq, [d["meta_utilidad"], d["meta_horas"], d["meta_mesas"]],
               bounds=bounds + [(0, None)] * 6)
        r["util"] = np.dot(U, r["x"][:3]); r["horas_usadas"] = np.dot(H, r["x"][:3])
        out[w] = r
    return out


def ej67(d):
    A, b, bounds = muebles_base(d)
    U, H, Ma = d["utilidad"], d["horas"], d["madera"]
    mesas = [0, 1, 0]
    # orden A: 1) mesas ≥ 60 (alcanzable: desviación 0), 2) horas ≤ 400 (¿alcanzable con 1?), 3) máx utilidad
    rA2 = lp(H, A + [[-v for v in mesas]], b + [-d["meta_mesas"]], bounds=bounds)          # mín horas con mesas ≥ 60
    assert rA2["z"] <= d["meta_horas"] + TOL
    rA3 = lp(U, A + [[-v for v in mesas], H], b + [-d["meta_mesas"], d["meta_horas"]], bounds=bounds, maximizar=True)
    # orden B: 1) utilidad ≥ 4 MM, 2) mín horas, 3) máx mesas (sin bajar de lo anterior)
    rB2 = lp(H, A + [[-u for u in U]], b + [-d["meta_utilidad"]], bounds=bounds)
    rB3 = lp(mesas, A + [[-u for u in U], H], b + [-d["meta_utilidad"], rB2["z"] + 1e-9], bounds=bounds, maximizar=True)
    for r in (rA3, rB3):
        r["util"] = np.dot(U, r["x"]); r["horas_usadas"] = np.dot(H, r["x"])
    return {"A": rA3, "B": rB3, "B_horas": rB2["z"]}


def ej68(d):
    A, b, bounds = muebles_base(d)
    U = d["utilidad"]

    def f(e):
        r = lp(U, [d["madera"], d["horas"]], [d["madera_max"], e], bounds=bounds, maximizar=True)
        return r
    pts = [(e, f(e)["z"], f(e)["dual"][-1], f(e)["x"]) for e in d["eps"]]
    q = frontera_eps(f, d["eps"][0], d["horas_max"])
    return {"tabla": pts, "quiebres": q, "x_quiebre": f(q[1][0])["x"] if len(q) > 2 else None}


def ej69(d):
    P = d["proyectos"]
    pts = []
    for k in range(len(P) + 1):
        for S in combinations(P, k):
            if sum(P[p][0] for p in S) <= d["presupuesto"]:
                pts.append((sum(P[p][1] for p in S), sum(P[p][2] for p in S), S))
    nd_obj = no_dominados([(a, b) for a, b, _ in pts], [1, 1])
    nd = sorted({(a, b, S) for a, b, S in pts if (a, b) in nd_obj}, key=lambda t: -t[0])
    soportados = set()
    for w in np.linspace(0, 1, 2001):
        mejor = max(w * a + (1 - w) * b for a, b, _ in pts)
        soportados |= {(a, b) for a, b, _ in pts if abs(w * a + (1 - w) * b - mejor) < 1e-9}
    meta = max((p for p in pts if p[0] >= d["meta_van"]), key=lambda p: (p[1], p[0]))
    return {"n": len(pts), "nd": nd, "soportados": sorted(soportados & set(nd_obj)), "meta": meta}


def ej610(d):
    O, D = d["orig"], d["dest"]
    nv = len(O) * len(D)
    A = [[1 if k // len(D) == i else 0 for k in range(nv)] for i in range(len(O))]
    A += [[-1 if k % len(D) == j else 0 for k in range(nv)] for j in range(len(D))]
    b = list(d["oferta"]) + [-v for v in d["demanda"]]
    c = [v for f in d["costo"] for v in f]; e = [v for f in d["co2"] for v in f]
    rc = lp(c, A, b); re = lp(e, A, b)
    tope = (1 + d["tolerancia"]) * rc["z"]
    rl = lp(e, A + [c], b + [tope])
    return {"costo": rc, "co2_de_costo": float(np.dot(e, rc["x"])), "co2": re, "costo_de_co2": float(np.dot(c, re["x"])),
            "lex": rl, "tope": tope, "costo_lex": float(np.dot(c, rl["x"])), "dual_tope": rl["dual"][-1],
            "precio_medio": (float(np.dot(c, re["x"])) - rc["z"]) / (float(np.dot(e, rc["x"])) - re["z"])}


# ---------------------------------------------------------------- caso integrador

def cargar_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_lp.py")
    caso = importlib.util.module_from_spec(spec); spec.loader.exec_module(caso)
    return caso


def caso_u6():
    caso = cargar_caso()
    MG, TG = caso.MARGEN, caso.TINTA_G
    A = [caso.SEG_EST, caso.SEG_PLA]
    b = [caso.CAP["estampado_s"], caso.CAP["planchado_s"]]
    bounds = list(zip([0] * 5, caso.DEMANDA_MAX))
    cap_tinta = caso.CAP["tinta_g"]
    U6 = caso.U6

    def eps(e):
        return lp(MG, A + [TG], b + [e], bounds=bounds, maximizar=True)

    R = {"C": caso.calcular()["u6"], "U6": U6, "productos": caso.PRODUCTOS}
    # pagos: máx margen (con la tinta de la semana) y mín tinta (sin exigir margen: producir nada)
    rmax = eps(cap_tinta)
    R["z_max"], R["tinta_zmax"], R["x_zmax"] = rmax["z"], float(np.dot(TG, rmax["x"])), rmax["x"]
    R["ideal"] = (rmax["z"], 0.0)
    R["nadir"] = (0.0, R["tinta_zmax"])
    quiebres = frontera_eps(eps, 0.0, cap_tinta)
    R["quiebres"] = quiebres
    R["pendientes"] = [(quiebres[k + 1][1] - quiebres[k][1]) / (quiebres[k + 1][0] - quiebres[k][0])
                       for k in range(len(quiebres) - 1)]
    R["mezclas"] = [eps(q[0])["x"] for q in quiebres]
    # suma ponderada con el peso del caso
    u, na = R["ideal"], R["nadir"]
    w = U6["peso_margen"]
    c = [w * MG[i] / (u[0] - na[0]) - (1 - w) * TG[i] / (na[1] - u[1]) for i in range(5)]
    rs = lp(c, A + [TG], b + [cap_tinta], bounds=bounds, maximizar=True)
    R["suma_x"], R["suma_margen"], R["suma_tinta"] = rs["x"], float(np.dot(MG, rs["x"])), float(np.dot(TG, rs["x"]))
    R["precio_implicito"] = (1 - w) * (u[0] - na[0]) / (w * (na[1] - u[1]))
    R["umbrales"] = [(u[0] - na[0]) / ((u[0] - na[0]) + s * (na[1] - u[1])) for s in R["pendientes"]]
    # metas: margen ≥ meta_margen (castiga d−), tinta ≤ meta_tinta (castiga d+), con pesos (w, 1−w) y (½, ½)
    R["metas"] = {}
    for wm in (w, 0.5):
        cm = [0] * 5 + [wm / U6["meta_margen"], 0, 0, (1 - wm) / U6["meta_tinta"]]
        A_eq = [list(MG) + [1, -1, 0, 0], list(TG) + [0, 0, 1, -1]]
        r = lp(cm, [list(f) + [0] * 4 for f in A + [TG]], b + [cap_tinta], A_eq, [U6["meta_margen"], U6["meta_tinta"]],
               bounds=bounds + [(0, None)] * 4)
        r["margen"] = float(np.dot(MG, r["x"][:5])); r["tinta"] = float(np.dot(TG, r["x"][:5]))
        R["metas"][wm] = r
    # prioridades: (1) margen ≥ meta y luego mín tinta · (2) tinta ≤ meta y luego máx margen
    r1 = lp(TG, A + [TG, [-m for m in MG]], b + [cap_tinta, -U6["meta_margen"]], bounds=bounds)
    r2 = eps(U6["meta_tinta"])
    R["lex_margen"], R["lex_tinta"] = r1, r2
    R["lex_tinta_x"] = r2["x"]
    return R


# ---------------------------------------------------------------- todo

def resultados():
    return {"huerto": huerto(HUERTO), "e61": ej61(E61), "e62": ej62(E62), "e63": ej63(E63), "e64": ej64(E64),
            "e65": ej65(E65), "e66": ej66(MUEBLES), "e67": ej67(MUEBLES), "e68": ej68(MUEBLES), "e69": ej69(E69),
            "e610": ej610(E610), "caso": caso_u6()}


def imprimir(R):
    def limpio(v):
        if isinstance(v, dict):
            return {str(k): limpio(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)):
            return [limpio(x) for x in v]
        if isinstance(v, np.ndarray):
            return [round(float(x), 4) for x in v]
        if isinstance(v, (float, np.floating)):
            return round(float(v), 4)
        return v
    for k, v in R.items():
        print(f"== {k}")
        if isinstance(v, dict):
            for kk, vv in v.items():
                print(f"   {kk}: {limpio(vv)}")
        else:
            print("  ", limpio(v))


# ---------------------------------------------------------------- archivos .dat y OPL

def _v(v):
    return "[" + " ".join(f"{x:g}" for x in v) + "]"


def dat_huerto(d, wm, wa):
    return ("/* Unidad 6 · ejemplo del huerto (metas). Generado por verificacion/u06_varios_objetivos.py */\n"
            f"margen = {_v(d['margen'])};\nagua = {_v(d['agua'])};\ntrabajo = {_v(d['trabajo'])};\n"
            f"superficie = {d['superficie']};\nminutos = {d['horas']};\ntomateMin = {d['tomate_min']};\n"
            f"lechugaMax = {d['lechuga_max']};\nmetaMargen = {d['meta_margen']};\nmetaAgua = {d['meta_agua']};\n"
            f"wMargen = {wm:g};\nwAgua = {wa:g};\n")


def dat_muebles(d, w):
    return ("/* Unidad 6 · ejercicio 6.6 (metas). Generado por verificacion/u06_varios_objetivos.py */\n"
            'Muebles = {"sillas", "mesas", "estantes"};\n'
            f"utilidad = {_v(d['utilidad'])};\nhoras = {_v(d['horas'])};\nmadera = {_v(d['madera'])};\n"
            f"demMax = {_v(d['dem_max'])};\nhorasMax = {d['horas_max']};\nmaderaMax = {d['madera_max']};\n"
            f"metaUtil = {d['meta_utilidad']};\nmetaHoras = {d['meta_horas']};\nmetaMesas = {d['meta_mesas']};\n"
            f"w = [{' '.join(repr(float(x)) for x in w)}];\n")


def dat_estampa(extra):
    caso = cargar_caso()
    txt = ("/* Unidad 6 · caso integrador: las cifras de verificacion/caso_estampa_sur_lp.py.\n"
           "   Generado por verificacion/u06_varios_objetivos.py */\n"
           'Prendas = {"poleras", "polerones", "doble", "bolsas", "gorros"};\n'
           f"margen = {_v(caso.MARGEN)};\nest = {_v(caso.SEG_EST)};\npla = {_v(caso.SEG_PLA)};\n"
           f"tinta = {_v(caso.TINTA_G)};\ndemanda = {_v(caso.DEMANDA_MAX)};\n"
           f"capEst = {caso.CAP['estampado_s']};\ncapPla = {caso.CAP['planchado_s']};\n")
    return txt + "".join(f"{k} = {float(v)!r};\n" for k, v in extra.items())


def dats():
    caso = cargar_caso()
    return {"u06_huerto_metas.dat": dat_huerto(HUERTO, *HUERTO["pesos_metas"][0]),
            "u06_muebles_metas.dat": dat_muebles(MUEBLES, MUEBLES["pesos"][0]),
            "u06_estampa_epsilon.dat": dat_estampa({"eps": caso.U6["meta_tinta"]}),
            "u06_estampa_metas.dat": dat_estampa({"capTinta": caso.CAP["tinta_g"], "metaMargen": caso.U6["meta_margen"],
                                                  "metaTinta": caso.U6["meta_tinta"], "wMargen": caso.U6["peso_margen"]})}


def dats_al_dia(escribir=False):
    malos = []
    for nombre, txt in dats().items():
        f = MODELOS / nombre
        if escribir:
            f.write_text(txt, encoding="utf-8")
        elif not f.exists() or f.read_text(encoding="utf-8") != txt:
            malos.append(nombre)
    return malos


def opl(R):
    out, ok = {}, True
    h, d = R["huerto"], HUERTO
    for wm, wa in d["pesos_metas"]:
        x = h["metas"][(wm, wa)]["x"]
        esp = {"tomate": x[0], "lechuga": x[1], "margen": np.dot(d["margen"], x[:2]), "agua": np.dot(d["agua"], x[:2]),
               "falta_margen": x[2], "exceso_agua": x[5]}
        ok &= comparar_opl(f"huerto metas {wm}/{wa}", "u06_huerto_metas.mod", dat_huerto(d, wm, wa), esp, out)
    m = MUEBLES
    for w in m["pesos"]:
        r = R["e66"][w]; x = r["x"]
        esp = {"x[sillas]": x[0], "x[mesas]": x[1], "x[estantes]": x[2], "utilidad": r["util"], "horas": r["horas_usadas"],
               "falta_utilidad": x[3], "exceso_horas": x[6], "falta_mesas": x[7]}
        ok &= comparar_opl(f"muebles metas {[round(v, 2) for v in w]}", "u06_muebles_metas.mod", dat_muebles(m, w), esp, out)
    c = R["caso"]
    nombres = ["poleras", "polerones", "doble", "bolsas", "gorros"]
    # en un quiebre el precio sombra es ambiguo (vale la pendiente de la izquierda o la de la derecha):
    # el margen se compara en el quiebre y la pendiente en el punto medio de cada tramo
    q = c["quiebres"]
    for k in range(1, len(q)):
        e, z = round(q[k][0], 6), q[k][1]
        ok &= comparar_opl(f"estampa eps = {e:g}", "u06_estampa_epsilon.mod", dat_estampa({"eps": e}), {"margen": z}, out)
        medio = (q[k - 1][0] + q[k][0]) / 2
        ok &= comparar_opl(f"estampa pendiente del tramo {k}", "u06_estampa_epsilon.mod", dat_estampa({"eps": medio}),
                           {"dual_tinta": c["pendientes"][k - 1]}, out)
    r2 = c["lex_tinta"]
    esp = {"margen": r2["z"], **{f"x[{nm}]": v for nm, v in zip(nombres, r2["x"])}}
    ok &= comparar_opl("estampa eps = meta de tinta", "u06_estampa_epsilon.mod",
                       dat_estampa({"eps": c["U6"]["meta_tinta"]}), esp, out)
    caso = cargar_caso()
    for wm, r in c["metas"].items():
        esp = {"margen": r["margen"], "tinta": r["tinta"], "falta_margen": r["x"][5], "exceso_tinta": r["x"][8],
               **{f"x[{nm}]": v for nm, v in zip(nombres, r["x"][:5])}}
        ok &= comparar_opl(f"estampa metas {wm}", "u06_estampa_metas.mod",
                           dat_estampa({"capTinta": caso.CAP["tinta_g"], "metaMargen": c["U6"]["meta_margen"],
                                        "metaTinta": c["U6"]["meta_tinta"], "wMargen": wm}), esp, out)
    for k, v in out.items():
        print(f"OPL {k}: {v}")
    return ok


# ---------------------------------------------------------------- figuras

TINTA, SUAVE, ACENTO, LINEA, PAPEL = "#2B2F33", "#5F656B", "#E2622A", "#D6D3CE", "#F2F1EF"


def figuras(R):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "path",
                         "axes.edgecolor": SUAVE, "axes.labelcolor": TINTA, "xtick.color": SUAVE, "ytick.color": SUAVE})
    miles = FuncFormatter(lambda v, _: fmt(v, 0))
    carpeta = RAMO / "unidades" / "figuras"
    carpeta.mkdir(parents=True, exist_ok=True)
    h, d = R["huerto"], HUERTO
    letras = {(20.0, 0.0): "A", (20.0, 90.0): "B", (30.0, 90.0): "C", (60.0, 60.0): "D", (90.0, 0.0): "E"}

    # 1 · espacio de decisiones del huerto
    fig, ax = plt.subplots(figsize=(6.2, 3.9))
    orden = [(20.0, 0.0), (90.0, 0.0), (60.0, 60.0), (30.0, 90.0), (20.0, 90.0)]
    ax.fill([p[0] for p in orden], [p[1] for p in orden], color=PAPEL, edgecolor=SUAVE, lw=1)
    xs = np.linspace(0, 100, 2)
    ax.plot(xs, d["superficie"] - xs, color=SUAVE, lw=0.8, ls="--")
    ax.plot(xs, (d["horas"] - d["trabajo"][0] * xs) / d["trabajo"][1], color=SUAVE, lw=0.8, ls=":")
    ax.axvline(d["tomate_min"], color=SUAVE, lw=0.8, ls="-.")
    ax.axhline(d["lechuga_max"], color=SUAVE, lw=0.8, ls="-.")
    front = [(20.0, 0.0), (20.0, 90.0), (30.0, 90.0), (60.0, 60.0)]
    ax.plot([p[0] for p in front], [p[1] for p in front], color=ACENTO, lw=3, label="soluciones eficientes")
    for (x, y), L in letras.items():
        ax.plot(x, y, "o", color=TINTA, ms=4)
        ax.annotate(L, (x, y), xytext=(6, 4), textcoords="offset points", fontsize=10, color=TINTA, weight="bold")
    ax.text(70, 52, "superficie", fontsize=8.5, color=SUAVE, rotation=-38)
    ax.text(91, 8, "trabajo", fontsize=8.5, color=SUAVE)
    ax.text(21, 100, "tomate mín.", fontsize=8.5, color=SUAVE)
    ax.text(2, 92, "lechuga máx.", fontsize=8.5, color=SUAVE)
    ax.set_xlim(0, 100); ax.set_ylim(0, 110)
    ax.set_xlabel("tomate (m²)"); ax.set_ylabel("lechuga (m²)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper right", fontsize=9)
    fig.tight_layout(); fig.savefig(carpeta / "u06_huerto_decisiones.svg", metadata={"Date": None}); plt.close(fig)

    # 2 · espacio de objetivos del huerto
    fig, ax = plt.subplots(figsize=(6.2, 3.9))
    for x, y, mg, ag in h["vertices"]:
        L = letras[(x, y)]
        ax.plot(ag, mg, "o", color=ACENTO if L != "E" else SUAVE, ms=6)
        off = {"D": (-150, 6), "E": (8, -14)}.get(L, (8, -4))
        ax.annotate(f"{L}  ({fmt(ag)} L; ${fmt(mg)})", (ag, mg), xytext=off, textcoords="offset points",
                    fontsize=8.5, color=TINTA)
    f = h["frontera"]
    ax.plot([p[1] for p in f], [p[0] for p in f], color=ACENTO, lw=2, label="frontera no dominada")
    ax.plot(h["ideal"][1], h["ideal"][0], "*", color=TINTA, ms=11)
    ax.annotate("ideal", (h["ideal"][1], h["ideal"][0]), xytext=(8, -3), textcoords="offset points", fontsize=8.5)
    ax.plot(h["nadir"][1], h["nadir"][0], "x", color=TINTA, ms=8)
    ax.annotate("nadir", (h["nadir"][1], h["nadir"][0]), xytext=(-34, 6), textcoords="offset points", fontsize=8.5)
    ax.set_xlabel("agua de la temporada (litros) · menos es mejor")
    ax.set_ylabel("margen ($) · más es mejor")
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.set_xlim(15000, 135000); ax.set_ylim(30000, 265000)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    fig.tight_layout(); fig.savefig(carpeta / "u06_huerto_objetivos.svg", metadata={"Date": None}); plt.close(fig)

    # 3 · frontera margen-tinta de Estampa Sur
    c = R["caso"]
    q = c["quiebres"]
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.plot([p[0] for p in q], [p[1] for p in q], color=ACENTO, lw=2.4, marker="o", ms=5, label="frontera (ε-restricción)")
    for k, (e, z) in enumerate(q[1:], 1):
        ax.annotate(f"{fmt(e)} g\n${fmt(z)}", (e, z), xytext={1: (8, -22), 4: (-30, 10)}.get(k, (-64, 4)),
                    textcoords="offset points", fontsize=8, color=TINTA)
    for k in range(len(q) - 1):
        xm, ym = (q[k][0] + q[k + 1][0]) / 2, (q[k][1] + q[k + 1][1]) / 2
        ax.annotate(f"{fmt(c['pendientes'][k], 1)} $/g", (xm, ym), xytext=(8, -16), textcoords="offset points",
                    fontsize=8, color=SUAVE)
    mm = c["metas"][c["U6"]["peso_margen"]]
    ax.plot(mm["tinta"], mm["margen"], "s", color=TINTA, ms=7, label="compromiso por metas (peso 0,7)")
    lt = c["lex_tinta"]
    ax.plot(c["U6"]["meta_tinta"], lt["z"], "D", color=SUAVE, ms=6, label="tinta ≤ meta y máximo margen")
    ax.axhline(c["U6"]["meta_margen"], color=SUAVE, lw=0.8, ls="--")
    ax.axvline(c["U6"]["meta_tinta"], color=SUAVE, lw=0.8, ls=":")
    ax.text(300, c["U6"]["meta_margen"] + 60000, "meta de margen", fontsize=8, color=SUAVE)
    ax.text(c["U6"]["meta_tinta"] - 300, 1900000, "meta de tinta", fontsize=8, color=SUAVE, rotation=90, ha="right")
    ax.set_xlabel("tinta de la semana (g) · menos es mejor"); ax.set_ylabel("margen ($) · más es mejor")
    ax.xaxis.set_major_formatter(miles); ax.yaxis.set_major_formatter(miles)
    ax.set_xlim(0, 32000); ax.set_ylim(0, 5000000)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="lower right", fontsize=8.5)
    fig.tight_layout(); fig.savefig(carpeta / "u06_estampa_frontera.svg", metadata={"Date": None}); plt.close(fig)
    print("figuras: u06_huerto_decisiones.svg, u06_huerto_objetivos.svg, u06_estampa_frontera.svg")


# ---------------------------------------------------------------- revisión contra el texto y cadena

def g(x, dec=2):
    """Entero sin decimales; si no, con `dec` decimales."""
    return n(x) if abs(x - round(x)) < 1e-6 else n(x, dec)


def redondeo_caso():
    """La mezcla de compromiso redondeada a enteros que todavía respeta las restricciones duras."""
    caso = cargar_caso()
    x = [402, 520, 0, 510, 690]
    pla = float(np.dot(caso.SEG_PLA, x)); est = float(np.dot(caso.SEG_EST, x)); tin = float(np.dot(caso.TINTA_G, x))
    assert pla <= caso.CAP["planchado_s"] and est <= caso.CAP["estampado_s"] and tin <= caso.CAP["tinta_g"]
    ingenuo = [401, 520, 0, 511, 690]
    assert np.dot(caso.SEG_PLA, ingenuo) > caso.CAP["planchado_s"]     # el redondeo «a ojo» se pasa
    mg = float(np.dot(caso.MARGEN, x))
    assert mg >= caso.U6["meta_margen"]
    return {"planchado": pla, "cap_pla": caso.CAP["planchado_s"], "tinta": tin, "margen": mg}


def esperados(R):
    e = []
    h, d = R["huerto"], HUERTO
    letras = {(20.0, 0.0): "A", (20.0, 90.0): "B", (30.0, 90.0): "C", (60.0, 60.0): "D", (90.0, 0.0): "E"}
    for x, y, mg, ag in h["vertices"]:
        e.append(f"| {letras[(x, y)]} | {n(x)} | {n(y)} | {pesos(mg)} | {n(ag)} |")
    assert [letras[(round(a, 6), round(b, 6))] for a, b, *_ in h["vertices"]
            if (np.dot(d["margen"], (a, b)), np.dot(d["agua"], (a, b))) not in h["frontera"]] == ["E"]
    e += [f"| máx margen | **{pesos(h['pagos'][0][0])}** | {n(h['pagos'][0][1])} |",
          f"| mín agua | {pesos(h['pagos'][1][0])} | **{n(h['pagos'][1][1])}** |",
          f"Ideal: ({pesos(h['ideal'][0])}; {n(h['ideal'][1])} litros). Nadir: ({pesos(h['nadir'][0])}; {n(h['nadir'][1])} litros)",
          "A→B **{}**, B→C **{}**, C→D **{}**".format(*[n(s, 2) for s in h["pendientes"]]),
          f"{{{n(h['ideal'][0] - h['nadir'][0])}}}", f"{{{n(h['nadir'][1] - h['ideal'][1])}}}",
          f"= {n(h['suma'][0.5][3], 2)}$", f"precio baja a {n(h['suma'][0.7][3], 2)}",
          "$w = {}$ (de A a B), ${}$ (de B a C) y ${}$ (de C a D)".format(*[n(w, 2) for w in h["umbrales"]]),
          f"rinde \\${n(h['pendientes'][1], 2)} de margen"]
    assert list(h["suma"][0.5][0]) == [20, 90] and list(h["suma"][0.7][0]) == [60, 60]
    texto_metas = {(0.5, 0.5): "faltan {} de margen", (0.7, 0.3): "sobran {} litros"}
    for (wm, wa), r in h["metas"].items():
        x = r["x"]
        mg, ag = np.dot(d["margen"], x[:2]), np.dot(d["agua"], x[:2])
        dev = pesos(x[2]) if (wm, wa) == (0.5, 0.5) else g(x[5])
        e.append(f"| ({n(wm, 1)}; {n(wa, 1)}) | {g(x[0])} | {g(x[1])} | {pesos(mg)} | {g(ag)} | "
                 + texto_metas[(wm, wa)].format(dev) + " |")
    e += [f"el margen máximo es {pesos(h['lex_agua']['z'])}",
          f"queda en {g(h['lex_margen']['z'])} litros ({g(h['lex_margen']['x'][0])} m² de tomate",
          f"queda en {pesos(h['lex_agua']['z'])} ({g(h['lex_agua']['x'][0])} m² de tomate)"]
    # 6.1
    r = R["e61"]
    assert r["dom"] == {"D": ["A"], "G": ["B"]} and sorted(r["nd"]) == ["A", "B", "C", "E", "F"]
    e += [f"Ideal: ({pesos(r['ideal'][0])}; {r['ideal'][1]} minutos)", f"nadir: ({pesos(r['nadir'][0])}; {r['nadir'][1]} minutos)"]
    # 6.2
    r = R["e62"]
    e += [f"costo {g(r['ideal'][0], 1)}, cobertura {g(r['ideal'][1])}, emisiones {g(r['ideal'][2])}",
          f"costo {g(r['nadir'][0], 1)}, cobertura {g(r['nadir'][1])}, emisiones {g(r['nadir'][2])}"]
    e += [f"= {n(v, 4)}$" for v in r["norm"]] + [f"= {n(r['puntaje'], 4)}$"]
    # 6.3
    r = R["e63"]
    e += [f"Faltan {n(r['d_util'], 1)} millones de utilidad ({n(100 * r['rel'][0])} % de la meta), sobran {r['d_extra']} horas "
          f"extra ({n(100 * r['rel'][1])} %) y faltan {r['d_cuota']} puntos de premium ({n(100 * r['rel'][2])} %)",
          f"= {n(r['penal'], 2)}$"]
    # 6.4
    r = R["e64"]
    e.append("; ".join(f"{p} {n(v, 2)}" for p, v in r["crudo"].items()))
    e += [f"Gana **{r['gana_crudo']}**", f"Gana **{r['gana_norm']}**"]
    for p in ["P1", "P2", "P3", "P4"]:
        e.append(f"| {p} | " + " | ".join(g(v + 0.0, 4) for v in r["norm"][p]) + f" | {n(r['puntaje'][p], 4)} |")
    # 6.5
    r = R["e65"]
    vt = sorted((v[0], v[1]) for v in r["vertices"])
    e.append(", ".join(f"({g(a)}; {g(b)})" for a, b in vt[:-1]) + f" y ({g(vt[-1][0])}; {g(vt[-1][1])})")
    e += [f"máximo ingreso {n(r['ideal'][0])} en (30; 20), con {n(r['nadir'][1])} viajes",
          f"mínimo de viajes {n(r['ideal'][1])} en (25; 0), con ingreso {n(r['nadir'][0])}",
          f"Ideal ({n(r['ideal'][0])}; {n(r['ideal'][1])}), nadir ({n(r['nadir'][0])}; {n(r['nadir'][1])})",
          "pendientes de {} y {}".format(*[g(s, 1) for s in r["pendientes"]])]
    for w in (0.5, 0.7):
        x, f1, f2, pi = r["suma"][w]
        e += [f"vale {n(pi, 2)}", f"ingreso {n(f1)} y {n(f2)} viajes"]
    # 6.6 y 6.7
    m = R["e66"]
    w1, w2 = MUEBLES["pesos"]
    r = m[w1]; x = r["x"]
    e.append(f"| (0,5; 0,3; 0,2) | {g(x[0])} | {g(x[1])} | {g(x[2], 3)} | {pesos(r['util'])} | {g(r['horas_usadas'], 3)} | "
             f"{g(x[6], 3)} h de sobretiempo |")
    r = m[w2]; x = r["x"]
    e.append(f"| iguales | {g(x[0])} | {g(x[1])} | {g(x[2])} | {pesos(r['util'])} | {g(r['horas_usadas'])} | "
             f"faltan {pesos(x[3])} de utilidad |")
    e += [f"es {pesos(m['max_util_400']['z'])}",
          f"{n(MUEBLES['utilidad'][2] / MUEBLES['horas'][2])}/{n(MUEBLES['meta_utilidad'])}"]
    r = R["e67"]
    e += [f"**{pesos(r['A']['util'])}** (0 sillas, {g(r['A']['x'][1])} mesas, {g(r['A']['x'][2])} estantes)",
          f"**{g(r['B_horas'])} horas** ({g(r['B']['x'][1])} mesas y {g(r['B']['x'][2])}",
          f"**{g(r['B']['x'][1])} mesas**, {g(MUEBLES['meta_mesas'] - r['B']['x'][1])} menos"]
    assert abs(r["A"]["util"] - m[w2]["util"]) < 1e-6
    r = R["e68"]
    e.append("| Utilidad máxima | " + " | ".join(pesos(z) for _, z, _, _ in r["tabla"]) + " |")
    e.append("| Precio sombra de la hora | " + " | ".join(pesos(dl) for _, _, dl, _ in r["tabla"]) + " |")
    q = r["quiebres"][1]
    e += [f"**{g(q[0])} horas** (y {pesos(q[1])})", f"{g(r['x_quiebre'][1])} mesas"]
    # 6.9
    r = R["e69"]
    e += [f"Hay {r['n']} carteras",
          ", ".join(f"{'+'.join(S)} ({a}; {b})" for a, b, S in r["nd"][:-1]) + " y "
          + f"{'+'.join(r['nd'][-1][2])} ({r['nd'][-1][0]}; {r['nd'][-1][1]})",
          "Solo **({}; {})** y **({}; {})**".format(*r["soportados"][1], *r["soportados"][0]),
          f"**{'+'.join(r['meta'][2])}**, con VAN {r['meta'][0]} y {r['meta'][1]} empleos"]
    # 6.10
    r = R["e610"]
    xc, xe, xl = r["costo"]["x"], r["co2"]["x"], r["lex"]["x"]
    e += [f"**{pesos(r['costo']['z'])}** (Norte → D1 {g(xc[0])} y → D2 {g(xc[1])}; Sur → D2 {g(xc[4])} y → D3 {g(xc[5])}), "
          f"con {n(r['co2_de_costo'])} kg",
          f"**{n(r['co2']['z'])} kg**, con costo {pesos(r['costo_de_co2'])} (Norte manda {g(xe[1])} a D2 en vez de {g(xc[1])}, "
          f"Sur solo {g(xe[4])})",
          n(r["tope"]), f"**{g(r['lex']['z'])} kg**: Norte manda {g(xl[1])} t a D2 y Sur {g(xl[4])}",
          f"{pesos(r['costo_de_co2'] - r['costo']['z'])} más para evitar {n(r['co2_de_costo'] - r['co2']['z'])} kg: "
          f"**\\${n(r['precio_medio'], 2)} por kg**",
          f"${g(r['dual_tope'], 5)}$", f"evita {g(-r['dual_tope'], 5)} kg"]
    assert abs(r["costo_lex"] - r["tope"]) < 1e-6 and abs(-1 / r["dual_tope"] - r["precio_medio"]) < 1e-6
    # caso
    c = R["caso"]; caso = cargar_caso()
    nombres = ["Poleras básicas", "Polerones", "Poleras estampado doble", "Bolsas", "Gorros"]
    for nm, mg, tg in zip(nombres, caso.MARGEN, caso.TINTA_G):
        e.append(f"| {nm} | \\{pesos(mg)} | {tg} | \\${n(mg / tg, 1)} |")
    e.append(f"**{pesos(c['z_max'])}**, usando **{n(c['tinta_zmax'])} g**")
    agrega = ["gorros, hasta 690", "polerones, hasta 520", "bolsas, hasta 711,25 (el planchado se llena)",
              "cambiar bolsas por poleras básicas"]
    for k, (e_, z) in enumerate(c["quiebres"][1:]):
        e.append(f"| {n(e_)} | {pesos(z)} | {agrega[k]} | \\${n(c['pendientes'][k], 1)} por g |")
    assert abs(c["mezclas"][3][3] - 711.25) < 1e-6 and abs(c["mezclas"][1][4] - 690) < 1e-6
    e += [f"= {n(c['precio_implicito'], 2)}$"] + [n(u, 4) for u in c["umbrales"]]
    assert all(abs(c["suma_x"][i] - c["x_zmax"][i]) < 1e-6 for i in range(5))
    m7, m5 = c["metas"][c["U6"]["peso_margen"]], c["metas"][0.5]
    e += [f"| (0,7; 0,3) | {pesos(m7['margen'])} | {g(m7['tinta'])} | sobran {g(m7['x'][8])} g de tinta |",
          f"| (0,5; 0,5) | {pesos(m5['margen'])} | {g(m5['tinta'])} | faltan {pesos(m5['x'][5])} de margen |",
          f"**{g(c['lex_margen']['z'])} g**", f"**{pesos(c['lex_tinta']['z'])}**"]
    for nm, a, b in zip(nombres, c["x_zmax"], m7["x"][:5]):
        e.append(f"| {nm} | {g(a)} | {g(b)} |")
    e += [f"| Margen | {pesos(c['z_max'])} | {pesos(m7['margen'])} |",
          f"| Tinta | {n(c['tinta_zmax'])} g | {g(m7['tinta'])} g |",
          f"{g(c['x_zmax'][0] - m7['x'][0])} poleras menos y {g(m7['x'][3] - c['x_zmax'][3])} bolsas más",
          f"Cuesta {pesos(c['z_max'] - m7['margen'])} de margen y ahorra {g(c['tinta_zmax'] - m7['tinta'])} g",
          f"\\${n((c['z_max'] - m7['margen']) / (c['tinta_zmax'] - m7['tinta']), 1)} por gramo"]
    rd = redondeo_caso()
    e += [f"({n(rd['planchado'])} de {n(rd['cap_pla'])} segundos)", f"tinta ({n(rd['tinta'])} g)", pesos(rd["margen"])]
    return e


def cadena(R):
    c = R["caso"]; C = c["C"]
    m7 = c["metas"][c["U6"]["peso_margen"]]
    ok = (abs(c["z_max"] - C["z_max"]) < TOL and abs(c["tinta_zmax"] - C["tinta_en_z_max"]) < TOL
          and abs(c["lex_margen"]["z"] - C["tinta_min_con_meta_margen"]) < 1e-5
          and abs(m7["tinta"] - C["tinta_min_con_meta_margen"]) < 1e-5
          and all(abs(a - b) < 1e-5 for a, b in zip(m7["x"][:5], C["x_meta"])))
    print("CADENA:", "OK, margen máximo, tinta mínima con la meta y mezcla de compromiso calzan con el caso" if ok
          else f"NO calza: script {C}")
    return ok


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    malos = dats_al_dia(escribir="--modelos" in sys.argv)
    if malos:
        print("Los .dat no calzan con los datos del script:", malos, "(corre con --modelos)")
        sys.exit(1)
    if "--figuras" in sys.argv:
        figuras(R)
    if not opl(R):
        print("OPL: NO coincide con Python")
        sys.exit(1)
    if not cadena(R):
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (RAMO / "unidades" / "06-varios-objetivos.md").read_text(encoding="utf-8")
        md = " ".join(md.replace("{,}", ",").replace("{.}", ".").split())   # los saltos de línea no cuentan
        faltan = [x for x in esperados(R) if " ".join(x.split()) not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
