"""Unidad 2 · Geometría de la optimización y método gráfico.

Recalcula todas las cifras de la unidad desde los datos: vértices de cada región, valor del objetivo
en cada uno, holguras, rangos y los casos especiales. Corre los modelos OPL de `modelos/` (si hay
CPLEX) y exige que coincidan con Python (scipy, HiGHS). Dibuja las figuras SVG de `unidades/figuras/`.
Con --revisar busca cada resultado, escrito como en el texto, dentro del .md.

    python u02_metodo_grafico.py            # imprime los resultados y redibuja las figuras
    python u02_metodo_grafico.py --revisar  # además los busca en el .md
"""
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import importlib.util, math, random, sys

import numpy as np
from scipy.optimize import linprog, minimize

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402

MODELOS = RAMO / "modelos"
FIGURAS = RAMO / "unidades" / "figuras"
EPS = 1e-7


# ---------------------------------------------------------------- formato chileno

def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def num(x):
    """Entero si lo es; si no, con los decimales justos (hasta 2)."""
    if abs(x - round(x)) < 1e-9:
        return fmt(round(x) + 0, 0).replace("-0", "0") if abs(x) < 1e-9 else fmt(round(x), 0)
    return fmt(x, 2).rstrip("0").rstrip(",")


def pesos(x):
    return "$" + fmt(x, 0)


def igual(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1, abs(a), abs(b))


# ---------------------------------------------------------------- geometría en el plano

def factible(p, restr):
    for a1, a2, b, s, *_ in restr:
        v = a1 * p[0] + a2 * p[1]
        if s == "<=" and v > b + EPS * max(1, abs(b)):
            return False
        if s == ">=" and v < b - EPS * max(1, abs(b)):
            return False
        if s == "=" and abs(v - b) > EPS * max(1, abs(b)):
            return False
    return True


def vertices(restr):
    """Cruza las rectas de a dos y se queda con los puntos factibles. Cada vértice trae sus rectas."""
    V = {}
    for i, j in combinations(range(len(restr)), 2):
        (a1, a2, b1, *_), (c1, c2, b2, *_) = restr[i], restr[j]
        det = a1 * c2 - a2 * c1
        if abs(det) < 1e-12:
            continue
        x = (b1 * c2 - a2 * b2) / det
        y = (a1 * b2 - b1 * c1) / det
        if factible((x, y), restr):
            k = (round(x, 6) + 0.0, round(y, 6) + 0.0)
            V.setdefault(k, set()).update({restr[i][4], restr[j][4]})
    return V


def ordenar(poly):
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    return sorted(poly, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))


def R(a1, a2, b, s, nombre):
    return (a1, a2, b, s, nombre)


NO_NEG = [R(1, 0, 0, ">=", "x₁ ≥ 0"), R(0, 1, 0, ">=", "x₂ ≥ 0")]


def lp(c, restr, sentido="max"):
    """Resuelve el PL de dos (o más) variables; devuelve estado, x y z."""
    A, b = [], []
    for a1, a2, bb, s, _ in restr:
        if s in ("<=", "="):
            A.append([a1, a2]); b.append(bb)
        if s in (">=", "="):
            A.append([-a1, -a2]); b.append(-bb)
    cc = [-v for v in c] if sentido == "max" else list(c)
    r = linprog(cc, A_ub=A, b_ub=b, bounds=[(None, None)] * 2, method="highs")
    if r.status != 0:
        return {2: "infactible", 3: "no acotado"}[r.status], None, None
    z = -r.fun if sentido == "max" else r.fun
    return "óptimo", list(r.x), z


def contra_opl(nombre, mod, esperado):
    r = correr(MODELOS / mod)
    if r is None:
        print(f"   OPL {nombre}: sin CPLEX, se usa solo Python")
        return True
    distintos = {k: (v, r["valores"].get(k)) for k, v in esperado.items()
                 if not isinstance(r["valores"].get(k), float) or not igual(r["valores"][k], v, 1e-6)}
    print(f"   OPL {nombre}:", "coincide con Python" if not distintos else f"NO coincide {distintos}")
    return not distintos


# ---------------------------------------------------------------- datos (originales)

# Ejemplo resuelto · jugos prensados en frío, Talca. V = jugo verde, N = naranja-zanahoria (L/día)
EJ = {"c": (1_740, 1_450), "prensa": (3, 2, 385), "fruta": (1.2, 1.8, 207), "tope_v": 103, "botellas": 178}

E1 = {"c": (7, 5), "r": [(1, 1, 11), (3, 1, 27), (0, 1, 8)]}                     # 2.1 máx
E2 = {"c": (5, 4), "r": [(2, 1, 12), (1, 3, 21)]}                                 # 2.2 mín con ≥
E3 = {"c": (4, 3), "r": [(2, 1, 16), (1, 1, 10), (1, 0, 7), (0, 1, 9), (1, 2, 22)]}  # 2.3
E5 = {"c2": 6}                                                                     # 2.5 sobre la región de 2.1
E6 = {"rango_b": (9, 12.5), "prueba": [9, 10, 11, 12.5, 13]}                      # 2.6 mueve R2 de 2.3
E9 = {"centro": (2, 1), "r": [(1, 1, 6), (1, 0, 5), (0, 1, 4)]}                    # 2.9 máx de una convexa
E10 = {"c": [5, 4, 6], "A": [[1, 1, 2], [2, 1, 1], [1, 2, 1]], "b": [24, 24, 24]}  # 2.10 tres variables

# Teoría: los cuatro casos y el óptimo local
CASOS = {"única": {"c": (3, 2), "r": [R(1, 1, 4, "<=", "x₁ + x₂ ≤ 4"), R(1, 0, 3, "<=", "x₁ ≤ 3")] + NO_NEG},
         "múltiples": {"c": (1, 1), "r": [R(1, 1, 4, "<=", "x₁ + x₂ ≤ 4"), R(1, 0, 3, "<=", "x₁ ≤ 3")] + NO_NEG},
         "no acotada": {"c": (1, 1), "r": [R(1, -1, 2, "<=", "x₁ − x₂ ≤ 2"), R(1, 0, 1, ">=", "x₁ ≥ 1")] + NO_NEG},
         "infactible": {"c": (1, 1), "r": [R(1, 1, 2, "<=", "x₁ + x₂ ≤ 2"), R(1, 1, 4, ">=", "x₁ + x₂ ≥ 4")] + NO_NEG}}
ELE = {"c": (2, 1), "poligono": [(0, 0), (6, 0), (6, 2), (2, 2), (2, 6), (0, 6)]}


# ---------------------------------------------------------------- cálculo

def tabla_vertices(V, c, nombres=("x₁", "x₂"), unidad="", moneda=False, sentido="max"):
    filas = sorted(V.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    z = {p: c[0] * p[0] + c[1] * p[1] for p, _ in filas}
    mejor = (max if sentido == "max" else min)(z.values())
    letras = "ABCDEFGH"
    out = [f"| Vértice | Se cruzan | {nombres[0]} | {nombres[1]} | {'Margen' if moneda else 'z'} |",
           "|---|---|---|---|---|"]
    for k, (p, rs) in enumerate(filas):
        val = pesos(z[p]) if moneda else num(z[p])
        if igual(z[p], mejor):
            val = f"**{val}**"
        out.append(f"| {letras[k]} | {' y '.join(sorted(rs))} | {num(p[0])}{unidad} | {num(p[1])}{unidad} | {val} |")
    return "\n".join(out), z


def ejemplo():
    cV, cN = EJ["c"]
    pa, pb, P = EJ["prensa"]; fa, fb, F_ = EJ["fruta"]
    restr = [R(pa, pb, P, "<=", "prensa"), R(fa, fb, F_, "<=", "fruta"), R(1, 0, EJ["tope_v"], "<=", "demanda V"),
             R(1, 1, EJ["botellas"], "<=", "botellas"), R(1, 0, 0, ">=", "V ≥ 0"), R(0, 1, 0, ">=", "N ≥ 0")]
    V = vertices(restr)
    tabla, z = tabla_vertices(V, (cV, cN), ("V", "N"), " L", moneda=True)
    est, x, zz = lp((cV, cN), restr)
    opt = max(z, key=z.get)
    assert igual(zz, z[opt]) and igual(x[0], opt[0]) and igual(x[1], opt[1])
    holg = {"prensa": P - pa * x[0] - pb * x[1], "fruta": F_ - fa * x[0] - fb * x[1],
            "demanda V": EJ["tope_v"] - x[0], "botellas": EJ["botellas"] - x[0] - x[1]}
    # la recta de botellas no toca la región: su máximo de V + N sobre la región sin ella es menor que el tope
    sin_bot = [r for r in restr if r[4] != "botellas"]
    _, _, max_vn = lp((1, 1), sin_bot)
    # rango de la razón cV/cN en que el vértice óptimo no cambia: entre las pendientes de fruta y prensa
    rango = (fa / fb, pa / pb)
    rango_cV = (cN * rango[0], cN * rango[1])
    ok = contra_opl("jugos", "u02_jugos.mod",
                    {"z": zz, "x_verde": x[0], "x_naranja": x[1], "holgura_prensa": holg["prensa"],
                     "holgura_fruta": holg["fruta"], "holgura_verde": holg["demanda V"],
                     "holgura_botellas": holg["botellas"]})
    nivel = [200_000, zz]
    return {"restr": restr, "V": V, "tabla": tabla, "z": z, "x": x, "zopt": zz, "holg": holg, "max_vn": max_vn,
            "rango": rango, "rango_cV": rango_cV, "nivel": nivel, "opl": ok,
            "intercepto_prensa_N": P / pb, "intercepto_fruta_N": F_ / fb, "intercepto_prensa_V": P / pa,
            "intercepto_fruta_V": F_ / fa}


def ej1():
    restr = [R(*E1["r"][0], "<=", "R1"), R(*E1["r"][1], "<=", "R2"), R(*E1["r"][2], "<=", "R3")] + NO_NEG
    V = vertices(restr)
    tabla, z = tabla_vertices(V, E1["c"])
    est, x, zz = lp(E1["c"], restr)
    return {"V": V, "tabla": tabla, "z": z, "x": x, "zopt": zz}


def ej2():
    restr = [R(*E2["r"][0], ">=", "R1"), R(*E2["r"][1], ">=", "R2")] + NO_NEG
    V = vertices(restr)
    tabla, z = tabla_vertices(V, E2["c"], sentido="min")
    est, x, zz = lp(E2["c"], restr, "min")
    est_max, _, _ = lp(E2["c"], restr, "max")
    return {"V": V, "tabla": tabla, "z": z, "x": x, "zopt": zz, "max": est_max}


def ej3():
    restr = [R(*r, "<=", f"R{k + 1}") for k, r in enumerate(E3["r"])] + NO_NEG
    est, x, zz = lp(E3["c"], restr)
    holg = {r[4]: r[2] - r[0] * x[0] - r[1] * x[1] for r in restr[:5]}
    redundante = {}
    for k, r in enumerate(restr[:5]):
        resto = [q for q in restr if q is not r]
        e, xx, m = lp((r[0], r[1]), resto)
        redundante[r[4]] = e == "óptimo" and m <= r[2] + 1e-9
    V = vertices(restr)
    tabla, z = tabla_vertices(V, E3["c"])
    sin_r3 = vertices([q for q in restr if q[4] != "R3"])
    return {"x": x, "zopt": zz, "holg": holg, "redundante": redundante, "tabla": tabla,
            "nuevo_sin_r3": sorted(set(sin_r3) - set(V))}


def ej4():
    """Hessianas y muestreo de segmentos."""
    hes = {"f2": [[2, -1], [-1, 4]], "f3": [[-2, 0], [0, -2]], "f4": [[2, 0], [0, -2]], "f6": [[0, 1], [1, 0]]}
    autov = {k: sorted(np.linalg.eigvalsh(np.array(v, float))) for k, v in hes.items()}
    tipo = {}
    for k, (l1, l2) in autov.items():
        tipo[k] = "convexa" if l1 >= 0 else ("cóncava" if l2 <= 0 else "ni convexa ni cóncava")
    conjuntos = {"a": lambda x, y: x + y <= 4 and x >= 0 and y >= 0,
                 "b": lambda x, y: x * x + y * y >= 1,
                 "c": lambda x, y: x > 0 and x * y >= 1,
                 "d": lambda x, y: x <= 2 or x >= 5,
                 "e": lambda x, y: x * x + y * y <= 4 and y >= x * x - 1}
    rnd = random.Random(4)
    convexo = {}
    for k, f in conjuntos.items():
        pts = []
        while len(pts) < 400:
            p = (rnd.uniform(-6, 8), rnd.uniform(-6, 8))
            if f(*p):
                pts.append(p)
        roto = False
        for _ in range(20_000):
            p, q = rnd.sample(pts, 2); t = rnd.random()
            m = (t * p[0] + (1 - t) * q[0], t * p[1] + (1 - t) * q[1])
            if not f(*m):
                roto = True; break
        convexo[k] = not roto
    assert not conjuntos["b"](0, 0) and conjuntos["b"](1, 0) and conjuntos["b"](-1, 0)
    assert not conjuntos["d"](3.5, 0) and conjuntos["d"](2, 0) and conjuntos["d"](5, 0)
    return {"autov": autov, "tipo": tipo, "convexo": convexo}


def ej5():
    restr = [R(*E1["r"][0], "<=", "R1"), R(*E1["r"][1], "<=", "R2"), R(*E1["r"][2], "<=", "R3")] + NO_NEG
    c2 = E5["c2"]
    # paralelo a R1 (1, 1) y a R2 (3, 1): c1/c2 = a1/a2
    c1_r1 = c2 * E1["r"][0][0] / E1["r"][0][1]
    c1_r2 = c2 * E1["r"][1][0] / E1["r"][1][1]
    V = vertices(restr)
    z_r1 = {p: c1_r1 * p[0] + c2 * p[1] for p in V}
    z_r2 = {p: c1_r2 * p[0] + c2 * p[1] for p in V}
    opt_r1 = sorted(p for p, v in z_r1.items() if igual(v, max(z_r1.values())))
    opt_r2 = sorted(p for p, v in z_r2.items() if igual(v, max(z_r2.values())))
    # punto medio del segmento: también es óptimo
    m = ((opt_r1[0][0] + opt_r1[1][0]) / 2, (opt_r1[0][1] + opt_r1[1][1]) / 2)
    assert igual(c1_r1 * m[0] + c2 * m[1], max(z_r1.values()))
    return {"c1_r1": c1_r1, "c1_r2": c1_r2, "opt_r1": opt_r1, "z_r1": max(z_r1.values()),
            "opt_r2": opt_r2, "z_r2": max(z_r2.values()), "medio": m}


def ej6():
    base = [R(*r, "<=", f"R{k + 1}") for k, r in enumerate(E3["r"])] + NO_NEG
    res = {}
    for b in E6["prueba"]:
        restr = [R(r[0], r[1], b, "<=", "R2") if r[4] == "R2" else r for r in base]
        _, x, z = lp(E3["c"], restr)
        res[b] = (x, z)
    lo, hi = E6["rango_b"]
    pend = (res[11][1] - res[10][1]) / 1
    assert igual(res[lo][1], 16 + 2 * lo) and igual(res[hi][1], 16 + 2 * hi) and igual(pend, 2)
    pend_fuera = (res[13][1] - res[hi][1]) / (13 - hi)
    return {"res": res, "pendiente": pend, "pendiente_fuera": pend_fuera}


def ej7():
    a = [R(1, 1, 4, ">=", "R1"), R(1, -1, 2, "<=", "R2")] + NO_NEG
    b = [R(1, 2, 6, "<=", "R1"), R(1, 1, 8, ">=", "R2")] + NO_NEG
    ea, _, _ = lp((2, 3), a)
    eb, _, _ = lp((1, 1), b)
    ec, xc, zc = lp((1, 1), a, "min")
    Vc = vertices(a)
    optc = sorted(p for p in Vc if igual(p[0] + p[1], zc))
    _, _, max_b = lp((1, 1), [R(1, 2, 6, "<=", "R1")] + NO_NEG)
    return {"a": ea, "b": eb, "c": ec, "zc": zc, "optc": optc, "max_suma_b": max_b}


def ej8():
    r = minimize(lambda v: -(v[0] + v[1]), [1, 0], constraints=[{"type": "ineq", "fun": lambda v: 9 - v[0] ** 2 - v[1] ** 2}])
    za = -r.fun
    assert igual(za, 3 * math.sqrt(2), 1e-5)
    rc = minimize(lambda v: v[0] + v[1], [3, 3], bounds=[(0, None), (0, None)],
                  constraints=[{"type": "ineq", "fun": lambda v: v[0] * v[1] - 4}])
    assert igual(rc.fun, 4, 1e-5) and igual(rc.x[0], 2, 1e-4)
    return {"za": za, "xa": 3 / math.sqrt(2), "zc": rc.fun}


def ej9():
    cx, cy = E9["centro"]
    f = lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2
    restr = [R(*E9["r"][0], "<=", "R1"), R(*E9["r"][1], "<=", "R2"), R(*E9["r"][2], "<=", "R3")] + NO_NEG
    V = sorted(vertices(restr))
    valores = {p: f(p) for p in V}
    rnd = random.Random(9)
    locales = []
    for p in V:
        es = True
        for _ in range(4000):
            q = (p[0] + rnd.uniform(-0.05, 0.05), p[1] + rnd.uniform(-0.05, 0.05))
            if factible(q, restr) and f(q) > f(p) + 1e-12:
                es = False; break
        if es:
            locales.append(p)
    glob = max(valores, key=valores.get)
    assert factible((cx, cy), restr)
    return {"V": V, "valores": valores, "locales": locales, "global": glob}


def ej10():
    c, A, b = E10["c"], E10["A"], E10["b"]
    H = [(np.array(a, float), bb, f"L{i + 1}") for i, (a, bb) in enumerate(zip(A, b))] + \
        [(np.eye(3)[j], 0.0, f"x{j + 1} = 0") for j in range(3)]
    candidatos = list(combinations(range(len(H)), 3))
    singulares, filas = 0, []
    for comb in candidatos:
        M = np.array([H[i][0] for i in comb]); rr = np.array([H[i][1] for i in comb])
        if abs(np.linalg.det(M)) < 1e-9:
            singulares += 1; continue
        x = np.linalg.solve(M, rr)
        ok = (x >= -1e-9).all() and all(np.dot(a, x) <= bb + 1e-9 for a, bb in zip(A, b))
        filas.append((x, ok, [H[i][2] for i in comb]))
    fact = sorted({tuple(np.round(x, 6) + 0.0) for x, ok, _ in filas if ok})
    zs = {p: float(np.dot(c, p)) for p in fact}
    opt = max(zs, key=zs.get)
    r = linprog([-v for v in c], A_ub=A, b_ub=b, method="highs")
    assert igual(-r.fun, zs[opt])
    du = list(-r.ineqlin.marginals)
    ok = contra_opl("tres variables", "u02_e10_tres_variables.mod",
                    {"z": zs[opt], "x_1": opt[0], "x_2": opt[1], "x_3": opt[2],
                     "dual_1": du[0], "dual_2": du[1], "dual_3": du[2]})
    lineas = ["| Punto | $x_1$ | $x_2$ | $x_3$ | $z$ |", "|---|---|---|---|---|"]
    for k, p in enumerate(fact):
        val = num(zs[p]) if p != opt else f"**{num(zs[p])}**"
        lineas.append(f"| P{k + 1} | {num(p[0])} | {num(p[1])} | {num(p[2])} | {val} |")
    return {"candidatos": len(candidatos), "singulares": singulares, "no_factibles": sum(1 for f in filas if not f[1]),
            "factibles": len(fact), "zs": zs, "opt": opt, "tabla": "\n".join(lineas), "opl": ok}


def teoria():
    out = {}
    for k, d in CASOS.items():
        out[k] = lp(d["c"], d["r"])
    Vm = vertices(CASOS["múltiples"]["r"])
    out["seg_multiples"] = sorted(p for p in Vm if igual(p[0] + p[1], out["múltiples"][2]))
    Vu = vertices(CASOS["única"]["r"])
    out["V_unica"] = {p: 3 * p[0] + 2 * p[1] for p in Vu}
    c = ELE["c"]
    out["ele"] = {p: c[0] * p[0] + c[1] * p[1] for p in ELE["poligono"]}
    return out


def caso_local():
    """La versión de dos productos, resuelta acá sin mirar el script del caso."""
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_lp.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    d = m.DOS
    c = tuple(d["margen"])
    restr = [R(d["est"][0], d["est"][1], d["cap_est"], "<=", "estampado"),
             R(d["pla"][0], d["pla"][1], d["cap_pla"], "<=", "planchado"),
             R(0, 1, d["dem_polerones"], "<=", "demanda"),
             R(1, 0, 0, ">=", "x₁ ≥ 0"), R(0, 1, 0, ">=", "x₂ ≥ 0")]
    V = vertices(restr)
    tabla, z = tabla_vertices(V, c, ("Poleras", "Polerones"), moneda=True)
    _, x, zz = lp(c, restr)
    holg = {"estampado": d["cap_est"] - np.dot(d["est"], x), "planchado": d["cap_pla"] - np.dot(d["pla"], x),
            "demanda": d["dem_polerones"] - x[1]}
    # el atajo: tope de polerones y lo que sobre de estampado a poleras
    x2g = d["dem_polerones"]
    x1g = min((d["cap_est"] - d["est"][1] * x2g) / d["est"][0], (d["cap_pla"] - d["pla"][1] * x2g) / d["pla"][0])
    zg = c[0] * x1g + c[1] * x2g
    pend_est = d["est"][0] / d["est"][1]; pend_pla = d["pla"][0] / d["pla"][1]
    rango_c2 = (c[0] / pend_pla, c[0] / pend_est)
    rango_c1 = (c[1] * pend_est, c[1] * pend_pla)
    ok = contra_opl("Estampa Sur", "u02_estampa_sur.mod",
                    {"z": zz, "x_poleras": x[0], "x_polerones": x[1], "holgura_estampado": holg["estampado"],
                     "holgura_planchado": holg["planchado"], "holgura_demanda": holg["demanda"]})
    por_est = [c[i] / d["est"][i] for i in range(2)]
    por_pla = [c[i] / d["pla"][i] for i in range(2)]
    return {"d": d, "restr": restr, "V": V, "tabla": tabla, "z": z, "x": x, "zopt": zz, "holg": holg,
            "atajo": (x1g, x2g), "z_atajo": zg, "brecha": zz - zg, "rango_c2": rango_c2, "rango_c1": rango_c1,
            "por_est": por_est, "por_pla": por_pla, "opl": ok,
            "horas": (d["cap_est"] / 3600, d["cap_pla"] / 3600), "modulo": m}


def resultados():
    return {"ej": ejemplo(), "e1": ej1(), "e2": ej2(), "e3": ej3(), "e4": ej4(), "e5": ej5(), "e6": ej6(),
            "e7": ej7(), "e8": ej8(), "e9": ej9(), "e10": ej10(), "teo": teoria(), "caso": caso_local()}


# ---------------------------------------------------------------- figuras SVG

TINTA, SUAVE, LINEA, ACENTO = "#2B2F33", "#5F656B", "#C9C5BF", "#E2622A"
COLORES = ["#1F5F8B", "#2E7D4F", "#8A4FA3", "#9C6B1F", "#5F656B"]
FUENTE = "Segoe UI, Roboto, Arial, sans-serif"


class Lienzo:
    def __init__(self, x0, y0, w, h, xlim, ylim):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.xlim, self.ylim = xlim, ylim
        self.sx = w / (xlim[1] - xlim[0]); self.sy = h / (ylim[1] - ylim[0])
        self.partes = []

    def px(self, x, y):
        return self.x0 + (x - self.xlim[0]) * self.sx, self.y0 + self.h - (y - self.ylim[0]) * self.sy

    def caja(self):
        return [R(1, 0, self.xlim[0], ">=", "_"), R(1, 0, self.xlim[1], "<=", "_"),
                R(0, 1, self.ylim[0], ">=", "_"), R(0, 1, self.ylim[1], "<=", "_")]

    def texto(self, x, y, t, color=TINTA, tam=12, ancla="start", peso="normal", halo=True):
        h = f' stroke="#FFFFFF" stroke-width="3.5" paint-order="stroke" stroke-linejoin="round"' if halo else ""
        self.partes.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FUENTE}" font-size="{tam}" fill="{color}" '
                           f'text-anchor="{ancla}" font-weight="{peso}"{h}>{t}</text>')

    def ejes(self, tx, ty, ex, ey, fmt_tick=num):
        x0, y0 = self.px(self.xlim[0], self.ylim[0]); x1, _ = self.px(self.xlim[1], self.ylim[0])
        _, y1 = self.px(self.xlim[0], self.ylim[1])
        for t in tx:
            X, _ = self.px(t, 0)
            self.partes.append(f'<line x1="{X:.1f}" y1="{y1:.1f}" x2="{X:.1f}" y2="{y0:.1f}" stroke="#EEECE9" stroke-width="1"/>')
            self.texto(X, y0 + 16, fmt_tick(t), SUAVE, 11, "middle", halo=False)
        for t in ty:
            _, Y = self.px(0, t)
            self.partes.append(f'<line x1="{x0:.1f}" y1="{Y:.1f}" x2="{x1:.1f}" y2="{Y:.1f}" stroke="#EEECE9" stroke-width="1"/>')
            self.texto(x0 - 6, Y + 4, fmt_tick(t), SUAVE, 11, "end", halo=False)
        self.partes.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1 + 6:.1f}" y2="{y0:.1f}" stroke="{TINTA}" stroke-width="1.3"/>')
        self.partes.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x0:.1f}" y2="{y1 - 6:.1f}" stroke="{TINTA}" stroke-width="1.3"/>')
        self.texto(x1 + 4, y0 - 8, ex, TINTA, 12, "end", "600")
        self.texto(x0 + 6, y1 - 4, ey, TINTA, 12, "start", "600")

    def poligono(self, pts, color=ACENTO, opac=0.16):
        d = " ".join(f"{self.px(*p)[0]:.1f},{self.px(*p)[1]:.1f}" for p in pts)
        self.partes.append(f'<polygon points="{d}" fill="{color}" fill-opacity="{opac}" stroke="none"/>')

    def region(self, restr, color=ACENTO, opac=0.16):
        V = vertices(list(restr) + self.caja())
        if len(V) >= 3:
            self.poligono(ordenar(list(V)), color, opac)

    def segmento_recta(self, a1, a2, b):
        pts = []
        (xa, xb), (ya, yb) = self.xlim, self.ylim
        if abs(a2) > 1e-12:
            for x in (xa, xb):
                pts.append((x, (b - a1 * x) / a2))
        if abs(a1) > 1e-12:
            for y in (ya, yb):
                pts.append(((b - a2 * y) / a1, y))
        pts = [p for p in pts if xa - 1e-9 <= p[0] <= xb + 1e-9 and ya - 1e-9 <= p[1] <= yb + 1e-9]
        pts = sorted(set((round(p[0], 9), round(p[1], 9)) for p in pts))
        return (pts[0], pts[-1]) if len(pts) >= 2 else None

    def recta(self, a1, a2, b, color, etiqueta=None, t=0.5, dx=6, dy=-6, guion=None, ancho=1.8, ancla="start"):
        s = self.segmento_recta(a1, a2, b)
        if not s:
            return
        (p, q) = s
        P, Q = self.px(*p), self.px(*q)
        g = f' stroke-dasharray="{guion}"' if guion else ""
        self.partes.append(f'<line x1="{P[0]:.1f}" y1="{P[1]:.1f}" x2="{Q[0]:.1f}" y2="{Q[1]:.1f}" stroke="{color}" stroke-width="{ancho}"{g}/>')
        if etiqueta:
            X = P[0] + t * (Q[0] - P[0]); Y = P[1] + t * (Q[1] - P[1])
            self.texto(X + dx, Y + dy, etiqueta, color, 12, ancla, "600")

    def punto(self, x, y, etiqueta=None, destacado=False, dx=8, dy=-8, ancla="start"):
        X, Y = self.px(x, y)
        r, col = (6, ACENTO) if destacado else (4, TINTA)
        self.partes.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="{col}" stroke="#FFFFFF" stroke-width="1.5"/>')
        if etiqueta:
            self.texto(X + dx, Y + dy, etiqueta, ACENTO if destacado else TINTA, 12, ancla, "600" if destacado else "normal")

    def flecha(self, x, y, c, largo=46, etiqueta="mejora", sentido=1):
        X, Y = self.px(x, y)
        # normal de la recta de nivel ya dibujada en pixeles: (c1/sx, −c2/sy), escalada por sx·sy
        gx, gy = c[0] * self.sy, -c[1] * self.sx
        m = math.hypot(gx, gy)
        gx, gy = sentido * gx / m * largo, sentido * gy / m * largo
        X2, Y2 = X + gx, Y + gy
        ang = math.atan2(Y2 - Y, X2 - X)
        a1 = (X2 - 9 * math.cos(ang - 0.4), Y2 - 9 * math.sin(ang - 0.4))
        a2 = (X2 - 9 * math.cos(ang + 0.4), Y2 - 9 * math.sin(ang + 0.4))
        self.partes.append(f'<line x1="{X:.1f}" y1="{Y:.1f}" x2="{X2:.1f}" y2="{Y2:.1f}" stroke="{ACENTO}" stroke-width="2"/>')
        self.partes.append(f'<polygon points="{X2:.1f},{Y2:.1f} {a1[0]:.1f},{a1[1]:.1f} {a2[0]:.1f},{a2[1]:.1f}" fill="{ACENTO}"/>')
        if etiqueta:
            self.texto(X2 + 6, Y2 + 4, etiqueta, ACENTO, 11, "start", "600")


def svg(ancho, alto, partes, titulo):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}" '
            f'role="img" aria-label="{titulo}"><title>{titulo}</title>'
            f'<rect width="{ancho}" height="{alto}" fill="#FFFFFF"/>' + "".join(partes) + "</svg>\n")


def fig_jugos(E):
    L = Lienzo(64, 22, 560, 360, (0, 140), (0, 200))
    L.ejes(range(0, 141, 20), range(0, 201, 25), "V (L/día)", "N (L/día)")
    L.region(E["restr"])
    cols = dict(zip(["prensa", "fruta", "demanda V", "botellas"], COLORES))
    pa, pb, P = EJ["prensa"]; fa, fb, F_ = EJ["fruta"]
    L.recta(pa, pb, P, cols["prensa"], "prensa", t=0.93, dx=8, dy=0)
    L.recta(fa, fb, F_, cols["fruta"], "fruta", t=0.12, dx=4, dy=-8)
    L.recta(1, 0, EJ["tope_v"], cols["demanda V"], "demanda V", t=0.9, dx=6, dy=0)
    L.recta(1, 1, EJ["botellas"], cols["botellas"], "botellas (no toca la región)", t=0.42, dx=8, dy=-4, guion="2 4")
    for k in E["nivel"]:
        L.recta(EJ["c"][0], EJ["c"][1], k, ACENTO, f"margen {pesos(k)}", t=0.1 if k == E["nivel"][0] else 0.42, dx=6, dy=-6, guion="6 4", ancho=1.4)
    letras = "ABCDE"
    for k, p in enumerate(sorted(E["V"], key=lambda p: (p[0], p[1]))):
        opt = igual(p[0], E["x"][0]) and igual(p[1], E["x"][1])
        L.punto(*p, f"{letras[k]} ({num(p[0])}; {num(p[1])})", opt, dx=-8 if p[0] > 0 else 8, dy=(16 if p[0] == 0 else -8) if p[1] > 0 else -10,
                ancla="end" if p[0] > 0 else "start")
    L.flecha(E["x"][0], E["x"][1], EJ["c"], 40, "mejora")
    return svg(660, 420, L.partes, "Método gráfico de los jugos prensados")


def fig_casos(T):
    partes = []
    titulos = {"única": "a) Óptimo único", "múltiples": "b) Óptimos múltiples",
               "no acotada": "c) No acotado", "infactible": "d) Infactible"}
    for k, (nombre, d) in enumerate(CASOS.items()):
        col, fila = k % 2, k // 2
        L = Lienzo(48 + col * 330, 40 + fila * 250, 250, 170, (0, 6), (0, 6))
        L.ejes(range(0, 7), range(0, 7), "x₁", "x₂")
        L.texto(48 + col * 330, 26 + fila * 250, titulos[nombre], TINTA, 13, "start", "700", halo=False)
        if nombre == "infactible":
            L.region([d["r"][0]] + NO_NEG, COLORES[0], 0.14)
            L.region([d["r"][1]] + NO_NEG, COLORES[1], 0.14)
        else:
            L.region(d["r"])
        for j, r in enumerate(d["r"][:2]):
            L.recta(r[0], r[1], r[2], COLORES[j], r[4], t=0.5 if j == 0 else 0.9, dx=4 if j == 0 else 6, dy=18 if j == 0 else -4)
        est, x, z = T[nombre]
        c = d["c"]
        if nombre == "única":
            L.recta(c[0], c[1], z, ACENTO, f"z = {num(z)}", t=0.2, dx=6, dy=0, guion="6 4", ancho=1.4)
            L.punto(*x, f"({num(x[0])}; {num(x[1])})", True, dx=8, dy=-6)
            L.flecha(x[0], x[1], c, 30, "")
        elif nombre == "múltiples":
            (p, q) = T["seg_multiples"]
            P, Q = L.px(*p), L.px(*q)
            L.partes.append(f'<line x1="{P[0]:.1f}" y1="{P[1]:.1f}" x2="{Q[0]:.1f}" y2="{Q[1]:.1f}" stroke="{ACENTO}" stroke-width="5" stroke-opacity="0.85"/>')
            L.punto(*p, f"({num(p[0])}; {num(p[1])})", True, dx=8, dy=-2)
            L.punto(*q, f"({num(q[0])}; {num(q[1])})", True, dx=8, dy=-6)
            L.texto(L.px(2.2, 2.4)[0], L.px(2.2, 2.4)[1], "z = 4 en todo el tramo", ACENTO, 11, "start", "600")
        elif nombre == "no acotada":
            for k2 in (4, 8):
                L.recta(c[0], c[1], k2, ACENTO, f"z = {k2}", t=0.12, dx=4, dy=-4, guion="6 4", ancho=1.4)
            L.flecha(2.5, 2.5, c, 36, "z crece sin tope")
        else:
            L.texto(L.px(3.3, 4.9)[0], L.px(3.3, 4.9)[1], "no hay punto común", TINTA, 11, "start", "600")
        partes += L.partes
    return svg(660, 520, partes, "Los cuatro casos del método gráfico")


def fig_ele(T):
    L = Lienzo(56, 20, 380, 300, (0, 8), (0, 8))
    L.ejes(range(0, 9), range(0, 9), "x₁", "x₂")
    L.poligono(ELE["poligono"])
    c = ELE["c"]
    for k in (10, 14):
        L.recta(c[0], c[1], k, ACENTO, f"z = {k}", t=0.62 if k == 10 else 0.72, dx=6, dy=-4, guion="6 4", ancho=1.4)
    L.punto(2, 6, "local: (2; 6), z = 10", False, dx=8, dy=-8)
    L.punto(6, 2, "global: (6; 2), z = 14", True, dx=-6, dy=-12, ancla="end")
    L.punto(2, 2, "", False)
    return svg(470, 360, L.partes, "Óptimo local y global en una región no convexa")


def fig_caso(C):
    d = C["d"]
    L = Lienzo(76, 22, 560, 360, (0, 3800), (0, 1400))
    L.ejes(range(0, 3801, 500), range(0, 1401, 200), "poleras x₁", "polerones x₂", fmt_tick=lambda t: fmt(t, 0))
    L.region(C["restr"])
    L.recta(d["est"][0], d["est"][1], d["cap_est"], COLORES[0], f"estampado ({num(C['horas'][0])} h)", t=0.62, dx=10, dy=-10)
    L.recta(d["pla"][0], d["pla"][1], d["cap_pla"], COLORES[1], f"planchado ({num(C['horas'][1])} h)", t=0.80, dx=-8, dy=24, ancla="end")
    L.recta(0, 1, d["dem_polerones"], COLORES[2], f"demanda de polerones ({fmt(d['dem_polerones'])})", t=0.68, dx=0, dy=-8)
    c = d["margen"]
    for k in (3_000_000, C["zopt"]):
        L.recta(c[0], c[1], k, ACENTO, f"margen {pesos(k)}", t=0.06 if k != C["zopt"] else 0.04, dx=6 if k != C["zopt"] else 10, dy=14 if k != C["zopt"] else -6, guion="6 4", ancho=1.4)
    letras = "ABCDE"
    pos = {0: (8, -8, "start"), 1: (8, -10, "start"), 2: (-10, -12, "end"), 3: (10, -6, "start"), 4: (-6, -10, "end")}
    for k, p in enumerate(sorted(C["V"], key=lambda p: (p[0], p[1]))):
        opt = igual(p[0], C["x"][0]) and igual(p[1], C["x"][1])
        dx, dy, an = pos[k]
        L.punto(*p, f"{letras[k]} ({fmt(p[0])}; {fmt(p[1])})", opt, dx=dx, dy=dy, ancla=an)
    L.flecha(C["x"][0], C["x"][1], c, 44, "mejora")
    return svg(680, 420, L.partes, "Estampa Sur: poleras y polerones")


def dibujar(Rs):
    FIGURAS.mkdir(parents=True, exist_ok=True)
    figs = {"u02_jugos.svg": fig_jugos(Rs["ej"]), "u02_cuatro_casos.svg": fig_casos(Rs["teo"]),
            "u02_local_global.svg": fig_ele(Rs["teo"]), "u02_estampa_sur.svg": fig_caso(Rs["caso"])}
    for n, s in figs.items():
        (FIGURAS / n).write_text(s, encoding="utf-8")
    print("   figuras:", ", ".join(figs))


# ---------------------------------------------------------------- impresión, cadena y revisión

def imprimir(Rs):
    for k, v in Rs.items():
        print(f"== {k}")
        for kk, vv in v.items():
            if kk in ("restr", "modulo", "d"):
                continue
            if isinstance(vv, str):
                print(f"   {kk}:\n{vv}")
            else:
                print(f"   {kk}: {vv}")


def cadena(Rs):
    C = Rs["caso"]
    u2 = C["modulo"].calcular()["u2"]
    mis_v = sorted((p[0], p[1], round(C["z"][p], 2)) for p in C["V"])
    ok = (igual(u2["z"], C["zopt"]) and all(igual(a, b) for a, b in zip(u2["x"], C["x"]))
          and len(u2["vertices"]) == len(mis_v)
          and all(all(igual(a, b) for a, b in zip(v1, v2)) for v1, v2 in zip(sorted(u2["vertices"]), mis_v)))
    print("CADENA:", "OK, vértices y óptimo calzan con el script del caso" if ok else "NO calza")
    return ok


def esperados(Rs):
    e = []
    E = Rs["ej"]
    e += [E["tabla"], pesos(E["zopt"])] + [f"{k}: {num(v)}" for k, v in E["holg"].items()]
    e += [num(E["max_vn"]), pesos(E["rango_cV"][0]), pesos(E["rango_cV"][1]), num(E["intercepto_prensa_N"], ),
          num(E["intercepto_fruta_N"]), num(E["intercepto_prensa_V"]), num(E["intercepto_fruta_V"])]
    e += [Rs["e1"]["tabla"], Rs["e2"]["tabla"], Rs["e3"]["tabla"]]
    e += [f"({num(Rs['e1']['x'][0])}, {num(Rs['e1']['x'][1])})", f"z^* = {num(Rs['e1']['zopt'])}"]
    e += [f"({num(Rs['e2']['x'][0])}, {num(Rs['e2']['x'][1])})", f"z^* = {num(Rs['e2']['zopt'])}"]
    e3 = Rs["e3"]
    e += [f"({num(e3['x'][0])}, {num(e3['x'][1])})", f"z^* = {num(e3['zopt'])}"]
    e += [f"holgura {num(v)}" for k, v in e3["holg"].items() if v > 1e-9]
    e += [f"({num(p[0])}, {num(p[1])})" for p in e3["nuevo_sin_r3"]]
    e4 = Rs["e4"]
    e += [f"{num(a)} y {num(b)}" for a, b in (e4["autov"]["f3"], e4["autov"]["f4"], e4["autov"]["f6"])]
    e += ["{} y {}".format(*(fmt(v, 2) for v in e4["autov"]["f2"]))]
    e5 = Rs["e5"]
    e += [f"c_1 = {num(e5['c1_r1'])}", f"c_1 = {num(e5['c1_r2'])}", f"z^* = {num(e5['z_r1'])}", f"z^* = {num(e5['z_r2'])}",
          f"{num(e5['c1_r1'])} < c_1 < {num(e5['c1_r2'])}"]
    e6 = Rs["e6"]
    e += [f"z = {num(z)}" for b, (x, z) in e6["res"].items()] + [num(e6["pendiente_fuera"])]
    e7 = Rs["e7"]
    e += [f"({num(p[0])}, {num(p[1])})" for p in e7["optc"]] + [f"z^* = {num(e7['zc'])}"]
    e8 = Rs["e8"]
    e += [fmt(e8["za"], 2), fmt(e8["xa"], 2)]
    e9 = Rs["e9"]
    e += [f"({num(p[0])}, {num(p[1])}) | {num(v)}" for p, v in e9["valores"].items()]
    e += [f"({num(p[0])}, {num(p[1])})" for p in e9["locales"]]
    e10 = Rs["e10"]
    e += [e10["tabla"], f"{e10['candidatos']} candidatos", f"{e10['factibles']} son vértices"]
    T = Rs["teo"]
    e += [f"z^* = {num(T['única'][2])}", f"z = {num(T['ele'][(6, 2)])}", f"z = {num(T['ele'][(2, 6)])}"]
    C = Rs["caso"]
    e += [C["tabla"], pesos(C["zopt"]), pesos(C["z_atajo"]), pesos(C["brecha"]), fmt(C["holg"]["demanda"]),
          pesos(C["rango_c2"][0]), pesos(C["rango_c2"][1]), pesos(C["rango_c1"][0]), pesos(C["rango_c1"][1]),
          fmt(C["d"]["cap_est"]), fmt(C["d"]["cap_pla"]), fmt(C["por_est"][0], 1), fmt(C["por_est"][1], 1),
          fmt(C["por_pla"][0], 1), fmt(C["por_pla"][1], 1)]
    return e


if __name__ == "__main__":
    Rs = resultados()
    imprimir(Rs)
    dibujar(Rs)
    if not all(Rs[k]["opl"] for k in ("ej", "e10", "caso")):
        print("OPL y Python no coinciden")
        sys.exit(1)
    if not cadena(Rs):
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (RAMO / "unidades" / "02-metodo-grafico.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".").replace("\\$", "$")
        faltan = [x for x in esperados(Rs) if x not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
