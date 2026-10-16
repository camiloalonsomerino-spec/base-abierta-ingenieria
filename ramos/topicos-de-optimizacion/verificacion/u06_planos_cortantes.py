"""Unidad 6 · Simplex dual, planos cortantes y ramificación y corte.

Recalcula todas las cifras de la unidad desde los datos; con --revisar las busca en el .md.

1. Las tablas del simplex dual y de los cortes de Gomory salen de motor_ramificacion.Tabla, en
   fracciones exactas, con las reglas que fija el texto (sale la de lado derecho más negativo; entra la de
   menor |z_j − c_j| / |a_rj|; el corte sale de la fila con parte fraccional más cercana a 0,5, empate: la
   de más arriba). La tabla óptima de la relajación del caso viene del simplex de Optimización
   (`../../optimizacion/verificacion/u08_simplex.py`), sin reescribirlo.
2. Cada corte se reescribe en las variables originales sustituyendo las holguras, y se comprueba que es
   admisible (lo cumplen todos los puntos enteros factibles) y separador (lo viola el óptimo vigente).
3. Cada óptimo se compara con scipy (milp y linprog, HiGHS) y con fuerza bruta.
4. Si hay CPLEX (oplrun), corre los modelos de `modelos/u06_*.mod` y el caso con el corte agregado.
5. Compara la pieza del caso con la unidad 5 y con los scripts de caso (CADENA: OK).
6. Dibuja las figuras y, con --revisar, busca cada cifra y cada tabla en el .md.

    python u06_planos_cortantes.py            # imprime resultados y redibuja las figuras
    python u06_planos_cortantes.py --revisar  # además busca cada cifra en el .md
"""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import importlib.util, math, shutil, sys, tempfile

import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
FIGURAS = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "06-planos-cortantes.md"
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from motor_ramificacion import *  # noqa: E402,F401
from opl import correr  # noqa: E402
import u05_ramificacion as U5  # noqa: E402
from u05_ramificacion import con_cotas  # noqa: E402

TOL = 1e-6

# ---------------------------------------------------------------- datos (originales; pasados por colisiones.py)
# Ejemplo · comedor solidario: sacos de legumbres (x1) y cajas de verduras (x2), costo en miles de pesos
COMEDOR = {"c": [7, 8], "A": [[6, 1], [3, 4]], "b": [28, 27]}      # raciones de proteína y de fibra, mínimos
# 6.1, 6.2, 6.3, 6.6 y 6.7 · una instancia de dos variables (máximo)
H = {"c": [3, 4], "A": [[2, 3], [5, 2]], "b": [13, 18]}
H_DESIG = [(1, 1, 5), (2, 1, 7), (0, 1, 2), (1, 0, 3), (1, 2, 9), (3, 4, 18)]   # 6.1: a1 x1 + a2 x2 ≤ b
H_RAMA = (1, 0, 2)          # 6.3 (a): x1 ≤ 2
H_INF = (-1, -1, -6)        # 6.3 (b): x1 + x2 ≥ 6
H_B1 = 6                    # 6.6: la primera disponibilidad baja de 13 a 6
H_OBJ = [(3, 4), (1, 0), (0, 1), (1, 1)]                                          # 6.7
# 6.4 y 6.8 · mochila con cortes de cobertura (máximo)
K = {"v": [13, 10, 8, 16, 5], "a": [7, 6, 5, 9, 4], "b": 17}
# 6.5 y 6.9 · Gomory completo (máximo)
G = {"c": [5, 4], "A": [[1, 4], [7, 5]], "b": [25, 23]}
# 6.10 · cervecería: dos líneas con costo fijo; gran M floja y ajustada (miles de pesos, hectolitros)
CERV = {"c": [14, 11], "f": [172, 97], "U": [40, 30], "K": 55, "M_floja": 250}


# ---------------------------------------------------------------- utilidades
def u08():
    spec = importlib.util.spec_from_file_location("u08", RAMO.parent / "optimizacion" / "verificacion" / "u08_simplex.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def tabla_optima_u08(c, A, b):
    """Corre el simplex de Optimización (unidad 8) y devuelve sus tablas en la convención de esta unidad."""
    pasos = u08().simplex(c, A, b)
    out = []
    n, m = len(c), len(A)
    nombres = [f"x{j + 1}" for j in range(n)] + [f"s{i + 1}" for i in range(m)]
    for tab, e, s, raz in pasos:
        t = Tabla(nombres, tab.T, [-v for v in tab.z], tab.base, "max")
        out.append((t, e, s))
    return out


def afines(nombres_orig, A, b, tipo):
    """Cada variable como expresión afín en x: {'x1': coef, ..., 'k': constante}.
    tipo[i] = 'le' (s = b − a x) o 'ge' (s = a x − b)."""
    n = len(A[0])
    E = {}
    for j in range(n):
        E[f"x{j + 1}"] = {f"x{k + 1}": F(int(k == j)) for k in range(n)} | {"k": F(0)}
    for i, (fila, bi) in enumerate(zip(A, b)):
        sg = 1 if tipo[i] == "le" else -1
        E[f"s{i + 1}"] = {f"x{k + 1}": F(-sg * fila[k]) for k in range(n)} | {"k": F(sg * bi)}
    return E


def corte_en_x(f, f0, nombres, E, n):
    """Σ f_j v_j ≥ f0 con v_j afines en x → α·x ≤ β con enteros primitivos (lo devuelve como (α, β))."""
    expr = {f"x{k + 1}": F(0) for k in range(n)} | {"k": F(0)}
    for fj, nom in zip(f, nombres):
        if fj:
            for key, v in E[nom].items():
                expr[key] += fj * v
    # Σ coef x + k ≥ f0  →  −Σ coef x ≤ k − f0
    alfa = [-expr[f"x{k + 1}"] for k in range(n)]
    beta = expr["k"] - f0
    den = math.lcm(*[q.denominator for q in alfa + [beta]])
    alfa = [int(q * den) for q in alfa]; beta = beta * den
    g = math.gcd(*alfa)
    alfa = [a // g for a in alfa]; beta = beta / g
    return alfa, beta


def registrar_corte(T, f, f0, nombre_nuevo, E, n):
    """Agrega a E la expresión afín de la holgura del corte: s = Σ f_j v_j − f0."""
    expr = {f"x{k + 1}": F(0) for k in range(n)} | {"k": F(-f0)}
    for fj, nom in zip(f, T.nombres):
        if fj and nom != nombre_nuevo:
            for key, v in E[nom].items():
                expr[key] += fj * v
    E[nombre_nuevo] = expr


def gomory(T, E, n, tope=6):
    """Cortes de Gomory + simplex dual desde una tabla óptima. Devuelve los pasos con sus tablas en Markdown."""
    pasos = []
    k = len(T.nombres) - n
    while True:
        xs = [T.valor(f"x{j + 1}") for j in range(n)]
        if all(v.denominator == 1 for v in xs):
            return pasos
        assert len([p for p in pasos if p["tipo"] == "corte"]) < tope
        cand = [i for i in range(len(T.T)) if T.T[i][-1].denominator != 1]
        todos = []
        for i in cand:
            f = [frac(v) if j not in T.base else F(0) for j, v in enumerate(T.T[i][:-1])]
            todos.append({"fila": i, "basica": T.nombres[T.base[i]], "f": f, "f0": frac(T.T[i][-1]),
                          "en_x": corte_en_x(f, frac(T.T[i][-1]), T.nombres, E, n)})
        r = min(cand, key=lambda i: (abs(frac(T.T[i][-1]) - F(1, 2)), i))
        k += 1
        nombre = f"s{k}"
        antes = T.copia()
        f, f0 = T.corte_gomory(r, nombre)
        registrar_corte(T, f + [F(0)], f0, nombre, E, n)
        alfa, beta = corte_en_x(f, f0, antes.nombres, E, n)
        pasos.append({"tipo": "corte", "fila": r, "basica": antes.nombres[antes.base[r]], "f": f, "f0": f0,
                      "nombre": nombre, "en_x": (alfa, beta), "todos": todos, "md": T.md(), "z": T.z[-1],
                      "x": [T.valor(f"x{j + 1}") for j in range(n)]})
        while not T.factible():
            fila = T.base[[i for i in range(len(T.T)) if T.T[i][-1] < 0][0]]
            antes = T.copia()
            res = T.paso_dual()
            assert res[0] != "infactible"
            r2, e2, coc = res
            pasos.append({"tipo": "dual", "sale": antes.nombres[antes.base[r2]], "entra": T.nombres[e2],
                          "cocientes": coc, "md_antes": antes.md((r2, e2), coc), "md": T.md(), "z": T.z[-1],
                          "x": [T.valor(f"x{j + 1}") for j in range(n)]})


def ineq_txt(alfa, beta, sig="\\le"):
    t = []
    for k, a in enumerate(alfa):
        if a == 0:
            continue
        coef = "" if abs(a) == 1 else str(abs(a))
        term = f"{coef}x_{k + 1}"
        if not t:
            t.append(("-" if a < 0 else "") + term)
        else:
            t.append(("- " if a < 0 else "+ ") + term)
    return " ".join(t) + f" {sig} {fr(beta)}"


def ineq_ge(alfa, beta):
    """α·x ≤ β con todo negativo → −α·x ≥ −β (más natural en un mínimo)."""
    return ineq_txt([-a for a in alfa], -beta, "\\ge")


def puntos_y(A, b, sentido="le", hasta=30):
    filas = [(r[0], r[1], bi) if sentido == "le" else (-r[0], -r[1], -bi) for r, bi in zip(A, b)]
    return enteros(filas + [(-1, 0, 0), (0, -1, 0)], hasta), filas


def admisible(alfa, beta, P):
    return all(alfa[0] * p[0] + alfa[1] * p[1] <= beta for p in P)


# ---------------------------------------------------------------- ejemplo: comedor (mínimo, simplex dual desde el inicio)
def ejemplo():
    d = COMEDOR
    T = Tabla.desde_holguras(d["c"], [[-a for a in r] for r in d["A"]], [-v for v in d["b"]], "min")
    pasos = [{"tipo": "inicio", "md": T.md()}]
    assert T.optima() and not T.factible()
    while not T.factible():
        antes = T.copia()
        r, e, coc = T.paso_dual()
        pasos.append({"tipo": "dual", "sale": antes.nombres[antes.base[r]], "entra": T.nombres[e], "cocientes": coc,
                      "md_antes": antes.md((r, e), coc), "md": T.md(), "z": T.z[-1],
                      "x": [T.valor("x1"), T.valor("x2")]})
    z_lp, x_lp = T.z[-1], [T.valor("x1"), T.valor("x2")]
    r = linprog(d["c"], A_ub=[[-a for a in f] for f in d["A"]], b_ub=[-v for v in d["b"]], method="highs")
    assert abs(r.fun - float(z_lp)) < TOL
    E = afines(T.nombres, d["A"], d["b"], ["ge", "ge"])
    g = gomory(T, E, 2)
    z, x = T.z[-1], [T.valor("x1"), T.valor("x2")]
    P, filas = puntos_y(d["A"], d["b"], "ge")
    bf = mejor_entero(tuple(d["c"]), filas + [(-1, 0, 0), (0, -1, 0)], "min", 30)
    assert bf[0] == z and tuple(x) == bf[1]
    corte = g[0]["en_x"]
    assert admisible(*corte, P)
    return {"pasos": pasos, "z_lp": z_lp, "x_lp": x_lp, "g": g, "z": z, "x": x, "corte": corte,
            "sep": -(corte[0][0] * x_lp[0] + corte[0][1] * x_lp[1]), "gap_lp": (z - z_lp) / z}


# ---------------------------------------------------------------- 6.1 y 6.7 · la instancia H
def instancia_h():
    filas = con_cotas([(H["A"][0][0], H["A"][0][1], H["b"][0]), (H["A"][1][0], H["A"][1][1], H["b"][1])])
    z, x = lp2(tuple(H["c"]), filas)
    P = enteros(filas, 20)
    V = envoltura(P)
    caras = facetas(V)
    zi, xi = mejor_entero(tuple(H["c"]), filas)
    clas = []
    for a1, a2, b in H_DESIG:
        adm = all(a1 * p[0] + a2 * p[1] <= b for p in P)
        viola = [p for p in P if a1 * p[0] + a2 * p[1] > b]
        sep = a1 * x[0] + a2 * x[1] > b
        en = [p for p in P if a1 * p[0] + a2 * p[1] == b]
        faceta = adm and len(en) >= 2
        clas.append({"d": (a1, a2, b), "adm": adm, "viola": viola, "lhs": a1 * x[0] + a2 * x[1], "sep": sep,
                     "faceta": faceta, "toca": en})
    # 6.7: qué facetas hacen falta para cada objetivo
    obj = []
    for c in H_OBJ:
        zz, xx = lp2(c, filas)
        best = max(V, key=lambda p: (c[0] * p[0] + c[1] * p[1], p[0]))
        val = c[0] * best[0] + c[1] * best[1]
        opt_hull = [p for p in V if c[0] * p[0] + c[1] * p[1] == val]
        activas = [cf for cf in caras if all(cf[0] * p[0] + cf[1] * p[1] == cf[2] for p in opt_hull) or
                   (len(opt_hull) == 1 and cf[0] * opt_hull[0][0] + cf[1] * opt_hull[0][1] == cf[2])]
        obj.append({"c": c, "lp": (zz, xx), "hull": opt_hull, "val": val, "activas": activas,
                    "lp_entero": all(v.denominator == 1 for v in xx)})
    originales = []
    for (a1, a2), b in zip(H["A"], H["b"]):
        en = [p for p in P if a1 * p[0] + a2 * p[1] == b]
        originales.append({"d": (a1, a2, b), "toca": en, "faceta": len(en) >= 2})
    return {"filas": filas, "x": x, "z": z, "P": P, "V": V, "caras": caras, "xi": xi, "zi": zi, "clas": clas,
            "obj": obj, "originales": originales}


def ej2():
    """6.2 · todos los cortes de Gomory de la tabla óptima de H, en x."""
    pasos = tabla_optima_u08(H["c"], H["A"], H["b"])
    T = pasos[-1][0]
    E = afines(T.nombres, H["A"], H["b"], ["le", "le"])
    P = instancia_h()["P"]
    cortes = []
    for i in range(len(T.T)):
        if T.T[i][-1].denominator == 1:
            continue
        f = [frac(v) if j not in T.base else F(0) for j, v in enumerate(T.T[i][:-1])]
        f0 = frac(T.T[i][-1])
        alfa, beta = corte_en_x(f, f0, T.nombres, E, 2)
        x = [T.valor("x1"), T.valor("x2")]
        assert admisible(alfa, beta, P) and alfa[0] * x[0] + alfa[1] * x[1] > beta
        cortes.append({"fila": i, "basica": T.nombres[T.base[i]], "f": f, "f0": f0, "alfa": alfa, "beta": beta,
                       "lhs": alfa[0] * x[0] + alfa[1] * x[1]})
    return {"T": T, "md": T.md(), "cortes": cortes}


def agregar(T, coefs, b, nombre):
    """Agrega Σ coefs[nombre]·v ≤ b con holgura nueva y la escribe en las no básicas."""
    fila = [F(coefs.get(n, 0)) for n in T.nombres] + [F(1), F(b)]
    for row in T.T:
        row.insert(-1, F(0))
    T.z.insert(-1, F(0))
    T.nombres.append(nombre)
    for i, j in enumerate(T.base):
        if fila[j] != 0:
            k = fila[j]
            fila = [a - k * q for a, q in zip(fila, T.T[i])]
    T.T.append(fila); T.base.append(len(T.nombres) - 1)


def dual_hasta_el_final(T):
    pasos = []
    while not T.factible():
        antes = T.copia()
        res = T.paso_dual()
        if res[0] == "infactible":
            pasos.append({"tipo": "infactible", "fila": antes.nombres[antes.base[res[1]]], "md_antes": antes.md()})
            return pasos, False
        r, e, coc = res
        pasos.append({"tipo": "dual", "sale": antes.nombres[antes.base[r]], "entra": T.nombres[e], "cocientes": coc,
                      "md_antes": antes.md((r, e), coc), "md": T.md(), "z": T.z[-1],
                      "x": [T.valor("x1"), T.valor("x2")]})
    return pasos, True


def ej3():
    base = tabla_optima_u08(H["c"], H["A"], H["b"])[-1][0]
    a = base.copia(); agregar(a, {"x1": H_RAMA[0], "x2": H_RAMA[1]}, H_RAMA[2], "s3")
    md_a = a.md()
    pa, ok_a = dual_hasta_el_final(a)
    filas = instancia_h()["filas"]
    za, xa = lp2(tuple(H["c"]), filas + [H_RAMA])
    assert ok_a and a.z[-1] == za and (a.valor("x1"), a.valor("x2")) == xa
    b = base.copia(); agregar(b, {"x1": H_INF[0], "x2": H_INF[1]}, H_INF[2], "s3")
    md_b = b.md()
    pb, ok_b = dual_hasta_el_final(b)
    assert not ok_b and lp2(tuple(H["c"]), filas + [H_INF]) is None
    zmax = lp2((1, 1), filas)[0]
    return {"md_a": md_a, "pa": pa, "za": za, "xa": xa, "md_b": md_b, "pb": pb, "max_suma": zmax}


def ej6():
    base = tabla_optima_u08(H["c"], H["A"], H["b"])[-1][0]
    T = base.copia()
    Binv = [[T.T[i][2], T.T[i][3]] for i in range(len(T.T))]
    bn = [H_B1, H["b"][1]]
    for i in range(len(T.T)):
        T.T[i][-1] = Binv[i][0] * bn[0] + Binv[i][1] * bn[1]
    y = [T.z[2], T.z[3]]
    T.z[-1] = y[0] * bn[0] + y[1] * bn[1]
    md0 = T.md()
    rhs = {T.nombres[T.base[i]]: T.T[i][-1] for i in range(len(T.T))}
    pasos, ok = dual_hasta_el_final(T)
    assert ok
    filas = con_cotas([(H["A"][0][0], H["A"][0][1], H_B1), (H["A"][1][0], H["A"][1][1], H["b"][1])])
    z, x = lp2(tuple(H["c"]), filas)
    assert z == T.z[-1] and x == (T.valor("x1"), T.valor("x2"))
    r = linprog([-3, -4], A_ub=H["A"], b_ub=bn, method="highs")
    assert abs(-r.fun - float(z)) < TOL
    return {"Binv": Binv, "md0": md0, "rhs": rhs, "z0": y[0] * bn[0] + y[1] * bn[1], "pasos": pasos, "z": z, "x": x}


# ---------------------------------------------------------------- mochila: coberturas y ramificación y corte
def coberturas_minimas(a, b):
    n = len(a); out = []
    for k in range(1, n + 1):
        for C in combinations(range(n), k):
            if sum(a[j] for j in C) > b and all(sum(a[j] for j in C) - a[i] <= b for i in C):
                out.append(C)
    return out


def lp_n(v, filas, n, fijas):
    """Máximo exacto de v·x sobre filas (coefs, b) con 0 ≤ x ≤ 1 y fijas, por enumeración de vértices."""
    libres = [j for j in range(n) if j not in fijas]
    R = []
    for coefs, b in filas:
        bb = F(b) - sum(coefs[j] * fijas[j] for j in fijas)
        R.append(([coefs[j] for j in libres], bb))
    m = len(libres)
    for k in range(m):
        e = [0] * m; e[k] = 1
        R.append((e, F(1))); R.append(([-t for t in e], F(0)))
    best = None
    for comb in combinations(range(len(R)), m):
        M = [[F(c) for c in R[i][0]] + [R[i][1]] for i in comb]
        # Gauss exacto
        ok = True
        for col in range(m):
            piv = next((r for r in range(col, m) if M[r][col] != 0), None)
            if piv is None:
                ok = False; break
            M[col], M[piv] = M[piv], M[col]
            p = M[col][col]; M[col] = [q / p for q in M[col]]
            for r in range(m):
                if r != col and M[r][col] != 0:
                    f = M[r][col]; M[r] = [a_ - f * b_ for a_, b_ in zip(M[r], M[col])]
        if not ok:
            continue
        xl = [M[r][-1] for r in range(m)]
        if all(sum(F(c) * t for c, t in zip(coefs, xl)) <= bb for coefs, bb in R):
            x = [F(0)] * n
            for j, t in zip(libres, xl):
                x[j] = t
            for j, t in fijas.items():
                x[j] = F(t)
            z = sum(F(vj) * t for vj, t in zip(v, x))
            if best is None or z > best[0] or (z == best[0] and tuple(x) > best[1]):
                best = (z, tuple(x))
    if m == 0:
        x = tuple(F(fijas[j]) for j in range(n))
        if all(sum(c * t for c, t in zip(coefs, x)) <= b for coefs, b in filas):
            return sum(F(vj) * t for vj, t in zip(v, x)), x
        return None
    return best


def cobertura_violada(a, b, x, usados):
    """La cobertura mínima más violada por x (mayor exceso Σ_C x_j − (|C| − 1)), si la hay."""
    mejor = None
    for C in coberturas_minimas(a, b):
        if C in usados:
            continue
        exceso = sum(x[j] for j in C) - (len(C) - 1)
        if exceso > 0 and (mejor is None or exceso > mejor[0]):
            mejor = (exceso, C)
    return mejor


def ryc_mochila(d):
    """Ramificación y corte: en cada nodo, mientras haya una cobertura mínima violada se agrega como corte
    (válido para todo el árbol) y se re-resuelve; si no hay, se ramifica (profundidad, «= 1» primero)."""
    n = len(d["v"])
    cortes = []
    filas = lambda: [(d["a"], d["b"])] + [([1 if j in C else 0 for j in range(n)], len(C) - 1) for C in cortes]
    log, inc = [], None
    pila = [({}, None, None)]
    k = 0
    while pila:
        fijas, padre, rot = pila.pop()
        nodo = {"k": k, "fijas": fijas, "padre": padre, "rotulo": rot, "lps": []}
        k += 1
        while True:
            s = lp_n(d["v"], filas(), n, fijas)
            nodo["lps"].append(s)
            if s is None:
                nodo["estado"] = "infactible"; break
            if inc is not None and s[0] <= inc[0]:
                nodo["estado"] = "cota"; break
            if all(t.denominator == 1 for t in s[1]):
                nodo["estado"] = "entera"; inc = s; break
            viol = cobertura_violada(d["a"], d["b"], s[1], set(cortes))
            if viol:
                cortes.append(viol[1]); nodo.setdefault("cortes", []).append((viol[1], viol[0], s)); continue
            j = next(i for i, t in enumerate(s[1]) if t.denominator != 1)
            nodo["estado"] = "ramificado"; nodo["var"] = j
            pila.append(({**fijas, j: 0}, nodo["k"], (j, 0)))
            pila.append(({**fijas, j: 1}, nodo["k"], (j, 1)))
            break
        log.append(nodo)
    return {"log": log, "inc": inc, "cortes": cortes, "n_lp": sum(len(nd["lps"]) for nd in log)}


def ej4():
    d = K
    C = coberturas_minimas(d["a"], d["b"])
    x0 = mochila_lp(d["v"], d["a"], d["b"], {})
    viol = [(c, sum(x0[1][j] for j in c) - (len(c) - 1)) for c in C]
    return {"C": C, "x0": x0, "viol": viol, "separan": [c for c, e in viol if e > 0],
            "es_cob": sum(d["a"][j] for j in (0, 1, 2)) > d["b"], "suma_123": sum(d["a"][j] for j in (0, 1, 2)),
            "min_123": all(sum(d["a"][j] for j in (0, 1, 2)) - d["a"][i] <= d["b"] for i in (0, 1, 2))}


def ej8():
    d = K
    RyC = ryc_mochila(d)
    RyA = rya_mochila(d["v"], d["a"], d["b"], "profundidad", 1)
    bf = mochila_fuerza_bruta(d["v"], d["a"], d["b"])
    assert RyC["inc"][0] == bf[0] == RyA["inc"][0]
    r = milp([-x for x in d["v"]], constraints=LinearConstraint(np.array([d["a"]], float), ub=[d["b"]]),
             integrality=np.ones(5), bounds=Bounds(np.zeros(5), np.ones(5)))
    assert abs(-r.fun - float(bf[0])) < TOL
    return {"RyC": RyC, "RyA": RyA, "n_rya": len(RyA["nodos"]), "opt": bf}


# ---------------------------------------------------------------- 6.5 y 6.9 · Gomory completo
def ej5():
    pasos_p = tabla_optima_u08(G["c"], G["A"], G["b"])
    T = pasos_p[-1][0].copia()
    md_lp = T.md()
    z_lp, x_lp = T.z[-1], [T.valor("x1"), T.valor("x2")]
    E = afines(T.nombres, G["A"], G["b"], ["le", "le"])
    g = gomory(T, E, 2)
    P, filas = puntos_y(G["A"], G["b"])
    bf = mejor_entero(tuple(G["c"]), filas + [(-1, 0, 0), (0, -1, 0)])
    assert bf[0] == T.z[-1] and bf[1] == (T.valor("x1"), T.valor("x2"))
    for p in g:
        if p["tipo"] == "corte":
            assert admisible(*p["en_x"], P)
    return {"md_lp": md_lp, "z_lp": z_lp, "x_lp": x_lp, "g": g, "z": T.z[-1], "x": (T.valor("x1"), T.valor("x2")),
            "P": P, "n_primal": len(pasos_p) - 1}


def ej9():
    e5 = ej5()
    zi = e5["z"]; zlp = e5["z_lp"]
    rango = (zi, zlp)
    enteros_b = [b for b in range(int(zi), math.ceil(zlp)) if b < zlp]
    # Chvátal-Gomory: λ = (0, 1/5) sobre la segunda restricción, redondeando coeficientes y lado derecho
    lam = (F(0), F(1, 5))
    comb = [lam[0] * G["A"][0][k] + lam[1] * G["A"][1][k] for k in range(2)]
    rhs = lam[0] * G["b"][0] + lam[1] * G["b"][1]
    cg = ([math.floor(t) for t in comb], math.floor(rhs))
    primer = next(p for p in e5["g"] if p["tipo"] == "corte")["en_x"]
    assert tuple(cg[0]) == tuple(primer[0]) and cg[1] == primer[1]
    en = [p for p in e5["P"] if cg[0][0] * p[0] + cg[0][1] * p[1] == cg[1]]
    return {"rango": rango, "enteros_b": enteros_b, "comb": comb, "rhs": rhs, "cg": cg, "toca": en, "faceta": len(en) >= 2}


# ---------------------------------------------------------------- 6.10 · gran M floja y ajustada
def cerv(M, entero=False):
    d = CERV
    # variables: q1, q2, y1, y2
    c = [-d["c"][0], -d["c"][1], d["f"][0], d["f"][1]]
    A = [[1, 1, 0, 0], [1, 0, -M[0], 0], [0, 1, 0, -M[1]], [1, 0, 0, 0], [0, 1, 0, 0]]
    b = [d["K"], 0, 0, d["U"][0], d["U"][1]]
    if entero:
        r = milp(c, constraints=LinearConstraint(np.array(A, float), ub=np.array(b, float)),
                 integrality=np.array([0, 0, 1, 1]), bounds=Bounds([0] * 4, [np.inf, np.inf, 1, 1]))
    else:
        r = linprog(c, A_ub=A, b_ub=b, bounds=[(0, None), (0, None), (0, 1), (0, 1)], method="highs")
    assert r.status == 0
    x = [F(v).limit_denominator(1000) for v in r.x]
    z = -(F(c[0]) * x[0] + F(c[1]) * x[1]) - F(c[2]) * x[2] - F(c[3]) * x[3]
    assert abs(float(z) + r.fun) < 1e-6
    return z, x


def ej10():
    d = CERV
    zf, xf = cerv([d["M_floja"]] * 2)
    za, xa = cerv(d["U"])
    zi, xi = cerv(d["U"], True)
    zi2, xi2 = cerv([d["M_floja"]] * 2, True)
    assert abs(zi - zi2) < 1e-6
    viola = [j for j in range(2) if xf[j] > d["U"][j] * xf[2 + j]]
    return {"zf": zf, "xf": xf, "za": za, "xa": xa, "zi": zi, "xi": xi, "gap_f": (zf - zi) / zi, "gap_a": (za - zi) / zi,
            "viola": viola, "factor": (zf - zi) / (za - zi) if za != zi else None}


# ---------------------------------------------------------------- caso · el turno del sábado sin ramificar
def caso():
    D = U5.datos_caso()
    c = D["margen"]; A = [D["est"], D["pla"]]; b = [U5.SABADO["est_min"], U5.SABADO["pla_min"]]
    pasos_p = tabla_optima_u08(c, A, b)
    T = pasos_p[-1][0].copia()
    md_primal = [p[0].md((p[2], p[1]) if p[1] is not None else None) for p in pasos_p]
    z_lp, x_lp = T.z[-1], [T.valor("x1"), T.valor("x2")]
    E = afines(T.nombres, A, b, ["le", "le"])
    todos0 = []
    for i in range(len(T.T)):
        if T.T[i][-1].denominator != 1:
            f = [frac(v) if j not in T.base else F(0) for j, v in enumerate(T.T[i][:-1])]
            todos0.append({"basica": T.nombres[T.base[i]], "f": f, "f0": frac(T.T[i][-1]),
                           "en_x": corte_en_x(f, frac(T.T[i][-1]), T.nombres, E, 2)})
    g = gomory(T, E, 2)
    P, filas = puntos_y(A, b)
    for p in g:
        if p["tipo"] == "corte":
            assert admisible(*p["en_x"], P)
            p["toca"] = [q for q in P if p["en_x"][0][0] * q[0] + p["en_x"][0][1] * q[1] == p["en_x"][1]]
    cortes_g = [p for p in g if p["tipo"] == "corte"]
    assert cortes_g[0]["toca"] == [] and cortes_g[1]["toca"] == [(11, 3)]
    R5 = U5.caso()
    assert T.z[-1] == R5["inc"][0] and (T.valor("x1"), T.valor("x2")) == R5["inc"][1]
    # la forma reducida: dividir cada fila por el máximo común divisor de sus coeficientes y lado derecho
    Ar = [[r[0], r[1]] for r in R5["red"]]; br = [r[2] for r in R5["red"]]
    Tr = tabla_optima_u08(c, Ar, br)[-1][0].copia()
    md_red = Tr.md()
    Er = afines(Tr.nombres, Ar, br, ["le", "le"])
    gr = gomory(Tr, Er, 2)
    assert Tr.z[-1] == R5["inc"][0]
    corte_red = next(p for p in gr if p["tipo"] == "corte")["en_x"]
    toca_red = [q for q in P if corte_red[0][0] * q[0] + corte_red[0][1] * q[1] == corte_red[1]]
    # ramificación y corte en la raíz: con el corte reducido, la relajación ya es entera
    z_rc, x_rc = lp2(tuple(c), filas + [(-1, 0, 0), (0, -1, 0)] + [(corte_red[0][0], corte_red[0][1], corte_red[1])])
    assert all(v.denominator == 1 for v in x_rc) and z_rc == R5["inc"][0]
    n_cortes = len([p for p in g if p["tipo"] == "corte"])
    return {"c": c, "A": A, "b": b, "md_primal": md_primal, "z_lp": z_lp, "x_lp": x_lp, "todos0": todos0, "g": g,
            "z": T.z[-1], "x": (T.valor("x1"), T.valor("x2")), "md_red": md_red, "gr": gr, "corte_red": corte_red,
            "toca_red": toca_red, "z_rc": z_rc, "x_rc": x_rc, "n_cortes": n_cortes, "n_pl_rya": len(R5["R"]["nodos"]),
            "red": R5["red"], "P": P, "D": D}


def resultados():
    return {"ej": ejemplo(), "h": instancia_h(), "e2": ej2(), "e3": ej3(), "e4": ej4(), "e5": ej5(), "e6": ej6(),
            "e8": ej8(), "e9": ej9(), "e10": ej10(), "caso": caso()}


# ---------------------------------------------------------------- tablas en Markdown
def secuencia(T, p, g):
    """Las tablas de una corrida de cortes y simplex dual: cada pivote marcado y la tabla final."""
    n = 0
    for paso in g:
        if paso["tipo"] == "dual":
            n += 1
            T[f"{p}_d{n}"] = paso["md_antes"]
    T[f"{p}_fin"] = g[-1]["md"]


def conj(C):
    return "{" + ", ".join(str(j + 1) for j in C) + "}"


def tablas(R):
    T = {}
    E = R["ej"]
    T["ej_d1"] = E["pasos"][1]["md_antes"]; T["ej_d2"] = E["pasos"][2]["md_antes"]
    secuencia(T, "ej_g", E["g"])
    h = R["h"]
    L = ["| Desigualdad | ¿Admisible? | Valor en el óptimo relajado | ¿Separa? | ¿Faceta? | Caso |", "|---|---|---|---|---|---|"]
    for cl in h["clas"]:
        a1, a2, b = cl["d"]
        adm = "sí" if cl["adm"] else "no: la viola " + ", ".join(f"({p[0]}; {p[1]})" for p in cl["viola"][:2])
        caso = ("corte válido" if cl["adm"] and cl["sep"] else "admisible, no separa" if cl["adm"] else
                "inadmisible y separa" if cl["sep"] else "inadmisible y no separa")
        L.append(f"| ${ineq_txt([a1, a2], b)}$ | {adm} | {fr(cl['lhs'])} | {'sí' if cl['sep'] else 'no'} | "
                 f"{'sí' if cl['faceta'] else 'no'} | {caso} |")
    T["h_clas"] = "\n".join(L)
    L = ["| Objetivo | Óptimo sobre la envoltura | Facetas activas |", "|---|---|---|"]
    for o in h["obj"]:
        c = o["c"]
        obj = " + ".join(t for t in [("" if c[0] == 1 else str(c[0])) + "x_1" if c[0] else "",
                                       ("" if c[1] == 1 else str(c[1])) + "x_2" if c[1] else ""] if t)
        opt = " y ".join(f"({p[0]}; {p[1]})" for p in o["hull"])
        act = ", ".join("$" + (ineq_txt([cf[0], cf[1]], cf[2]) if cf[0] >= 0 and cf[1] >= 0 else "x_1 \\ge 0") + "$"
                        for cf in o["activas"])
        L.append(f"| $\\max {obj}$ | {opt} | {act} |")
    T["h_obj"] = "\n".join(L)
    T["e2"] = R["e2"]["md"]
    e3 = R["e3"]
    T["e3a"] = e3["pa"][0]["md_antes"]; T["e3a_fin"] = e3["pa"][-1]["md"]; T["e3b"] = e3["md_b"]
    e4 = R["e4"]
    L = ["| Cobertura mínima | Suma de pesos | Exceso en el óptimo relajado | ¿Separa? |", "|---|---|---|---|"]
    for C, ex in e4["viol"]:
        L.append(f"| {conj(C)} | {sum(K['a'][j] for j in C)} | {fr(ex)} | {'sí' if ex > 0 else 'no'} |")
    T["e4"] = "\n".join(L)
    T["e5_lp"] = R["e5"]["md_lp"]; secuencia(T, "e5_g", R["e5"]["g"])
    T["e6_d1"] = R["e6"]["pasos"][0]["md_antes"]; T["e6_fin"] = R["e6"]["pasos"][-1]["md"]
    L = ["| Nodo | Ramas | Relajaciones resueltas (solución; z) | Corte agregado | Qué pasa |", "|---|---|---|---|---|"]
    for nd in R["e8"]["RyC"]["log"]:
        ramas = ", ".join(f"{U5.nombre_sub(j)} = {v}" for j, v in nd["fijas"].items()) or "—"
        lps = " → ".join("infactible" if s_ is None else f"{vec(s_[1])}; {num(s_[0], 2)}" for s_ in nd["lps"])
        cortes = ", ".join("$" + " + ".join(f"x_{j + 1}" for j in C) + f" \\le {len(C) - 1}$" for C, _, _ in nd.get("cortes", [])) or "—"
        que = {"ramificado": f"ramifica en {U5.nombre_sub(nd.get('var', 0))}", "entera": "entera → incumbente",
               "cota": "poda por cota", "infactible": "infactible"}[nd["estado"]]
        L.append(f"| {nd['k']} | {ramas} | {lps} | {cortes} | {que} |")
    T["e8"] = "\n".join(L)
    C = R["caso"]
    for k, m in enumerate(C["md_primal"]):
        T[f"caso_p{k}"] = m
    secuencia(T, "caso_g", C["g"])
    T["caso_red"] = C["md_red"]; secuencia(T, "caso_red_g", C["gr"])
    return T


# ---------------------------------------------------------------- figuras
def fig_comedor(E):
    d = COMEDOR
    L = Lienzo(60, 24, 470, 360, (0, 10), (0, 9))
    L.ejes("sacos de legumbres x₁", "cajas de verduras x₂")
    filas = [(-r[0], -r[1], -bi) for r, bi in zip(d["A"], d["b"])] + [(-1, 0, 0), (0, -1, 0), (1, 0, 10), (0, 1, 9)]
    L.poligono(ordenar(list(vertices(filas))), ACENTO, 0.12)
    L.recta(6, 1, 28, TINTA, "proteína: 6x₁ + x₂ ≥ 28", t=0.10, dx=8, dy=0)
    L.recta(3, 4, 27, AZUL, "fibra: 3x₁ + 4x₂ ≥ 27", t=0.85, dx=-4, dy=16, ancla="end")
    a, b = E["corte"]
    L.recta(-a[0], -a[1], -b, VERDE, "corte: x₁ + x₂ ≥ 8", t=0.30, dx=8, dy=-6, guion="6 4")
    for p in enteros(filas, 12):
        L.punto(*p, 2.4, SUAVE)
    L.punto(*E["x_lp"], 6, ACENTO)
    L.rotulo(*E["x_lp"], f"relajación ({num(E['x_lp'][0], 2)}; {num(E['x_lp'][1], 2)})", ACENTO, -10, 22, "end")
    L.punto(*E["x"], 6, VERDE); L.rotulo(*E["x"], f"óptimo entero ({fr(E['x'][0])}; {fr(E['x'][1])})", VERDE, 10, 4)
    return svg(560, 420, L.p, "Comedor solidario: la relajación, el corte de Gomory y el óptimo entero")


def fig_sabado(C):
    L = Lienzo(60, 24, 520, 330, (0, 20), (0, 7))
    L.ejes("cajas de poleras x₁", "cajas de polerones x₂", 2, 1)
    filas = [(C["A"][0][0], C["A"][0][1], C["b"][0]), (C["A"][1][0], C["A"][1][1], C["b"][1]), (-1, 0, 0), (0, -1, 0)]
    L.poligono(ordenar(list(vertices(filas))), ACENTO, 0.10)
    L.recta(C["A"][0][0], C["A"][0][1], C["b"][0], TINTA, "estampado", t=0.15, dx=6, dy=-6)
    L.recta(C["A"][1][0], C["A"][1][1], C["b"][1], AZUL, "planchado", t=0.05, dx=10, dy=-2)
    cortes = [p["en_x"] for p in C["g"] if p["tipo"] == "corte"]
    for k, ((a1, a2), b) in enumerate(cortes):
        L.recta(a1, a2, b, MORADO, f"corte {k + 1}: {a1}x₁ + {a2}x₂ ≤ {fr(b)}", t=0.25 + 0.15 * k, dx=8, dy=-6 + 18 * k, guion="6 4")
    (a1, a2), b = C["corte_red"]
    L.recta(a1, a2, b, VERDE, f"{a1}x₁ + {a2}x₂ ≤ {fr(b)} (forma reducida)", t=0.62, dx=-14, dy=34, ancla="end")
    for p in C["P"]:
        L.punto(*p, 2.4, SUAVE)
    camino = [C["x_lp"]] + [p["x"] for p in C["g"] if p["tipo"] == "dual"]
    for (x0, y0), (x1, y1) in zip(camino, camino[1:]):
        A_, B_ = L.px(x0, y0), L.px(x1, y1)
        L.p.append(f'<line x1="{A_[0]:.1f}" y1="{A_[1]:.1f}" x2="{B_[0]:.1f}" y2="{B_[1]:.1f}" stroke="{ACENTO}" stroke-width="2"/>')
    for k, q in enumerate(camino):
        L.punto(*q, 5 if k < len(camino) - 1 else 6.5, ACENTO if k < len(camino) - 1 else VERDE)
    L.rotulo(*camino[0], f"relajación ({num(camino[0][0], 1)}; {num(camino[0][1], 1)})", ACENTO, 10, 4)
    L.rotulo(*camino[1], f"tras el corte 1 ({fr(camino[1][0])}; {fr(camino[1][1])})", ACENTO, 10, -10)
    L.rotulo(*camino[-1], f"tras el corte 2 ({fr(camino[-1][0])}; {fr(camino[-1][1])})", VERDE, -12, 20, "end")
    return svg(600, 400, L.p, "Turno del sábado: los cortes de Gomory y el camino del simplex dual")


def dibujar(R):
    FIGURAS.mkdir(parents=True, exist_ok=True)
    (FIGURAS / "u06_comedor.svg").write_text(fig_comedor(R["ej"]), encoding="utf-8")
    (FIGURAS / "u06_sabado_cortes.svg").write_text(fig_sabado(R["caso"]), encoding="utf-8")
    print("FIGURAS: u06_comedor.svg y u06_sabado_cortes.svg")


# ---------------------------------------------------------------- OPL
def comparar_con_opl(R):
    E, X = R["ej"], R["e10"]
    r = correr(MODELOS / "u06_comedor.mod")
    if r is None:
        print("OPL: oplrun no está instalado; se comparan solo las cifras de Python")
        return None
    assert abs(r["objetivo"] - float(E["z"])) < 1e-6 and r["valores"]["sacos"] == E["x"][0] and r["valores"]["cajas"] == E["x"][1]
    tmp = Path(tempfile.mkdtemp(prefix="u06_"))
    try:
        mod = (MODELOS / "u06_comedor.mod").read_text(encoding="utf-8")
        f = tmp / "comedor_rel.mod"; f.write_text(mod.replace("dvar int+", "dvar float+"), encoding="utf-8")
        r = correr(f)
        assert abs(r["objetivo"] - float(E["z_lp"])) < 1e-4, r["objetivo"]
        mod = (MODELOS / "u06_e10_cerveceria.mod").read_text(encoding="utf-8")
        rel = tmp / "cerv_rel.mod"
        rel.write_text(mod.replace("dvar boolean y[Lineas];", "dvar float+ y[Lineas] in 0..1;"), encoding="utf-8")
        for dat, zrel in [("u06_e10_floja.dat", X["zf"]), ("u06_e10_ajustada.dat", X["za"])]:
            r = correr(MODELOS / "u06_e10_cerveceria.mod", MODELOS / dat)
            assert abs(r["objetivo"] - float(X["zi"])) < 1e-4, (dat, r["objetivo"])
            r = correr(rel, MODELOS / dat)
            assert abs(r["objetivo"] - float(zrel)) < 1e-4, (dat, r["objetivo"], zrel)
        # el caso: la relajación con el corte reducido ya es entera
        mod = (MODELOS / "u05_sabado.mod").read_text(encoding="utf-8")
        (a1, a2), b = R["caso"]["corte_red"]
        g = tmp / "sabado_corte.mod"
        g.write_text(mod.replace("dvar int+", "dvar float+").replace(
            "subject to {", f'subject to {{\n  Corte: {a1} * cajas["poleras"] + {a2} * cajas["polerones"] <= {b};'), encoding="utf-8")
        r = correr(g, MODELOS / "u05_sabado.dat")
        assert abs(r["objetivo"] - float(R["caso"]["z"])) < 1e-4, r["objetivo"]
        assert r["valores"]["cajas[poleras]"] == R["caso"]["x"][0] and r["valores"]["cajas[polerones]"] == R["caso"]["x"][1]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("OPL: el comedor, su relajación, la cervecería (entera y relajada, M floja y ajustada) y el caso con el corte coinciden con Python")
    return True


# ---------------------------------------------------------------- revisión
def par(p):
    return f"({fr(p[0])}; {fr(p[1])})"


def esperados(R):
    s = []
    E = R["ej"]
    s += [par(E["x_lp"]), num(E["z_lp"], 2), fr(E["z_lp"]), ineq_ge(*E["corte"]), par(E["x"]), num(E["z"]), num(E["sep"], 2),
          pct(E["gap_lp"])]
    s += [ineq_ge(*t["en_x"]) for t in E["g"][0]["todos"]]
    h = R["h"]
    s += [par(h["x"]), num(h["z"], 2), par(h["xi"]), num(h["zi"]), str(len(h["P"])), ", ".join(f"({p[0]}; {p[1]})" for p in h["V"])]
    for cf in h["caras"]:
        if cf[0] > 0 and cf[1] > 0:
            s.append(ineq_txt([cf[0], cf[1]], cf[2]))
    s += [ineq_txt(c["alfa"], c["beta"]) for c in R["e2"]["cortes"]]
    e3 = R["e3"]; s += [par(e3["xa"]), num(e3["za"]), num(e3["max_suma"], 2)]
    e4 = R["e4"]; s += [vec(e4["x0"][1]), num(e4["x0"][0], 2), str(e4["suma_123"])] + [conj(c) for c in e4["C"]]
    e5 = R["e5"]; s += [par(e5["x_lp"]), num(e5["z_lp"], 2), par(e5["x"]), num(e5["z"])]
    s += [ineq_txt(*p["en_x"]) for p in e5["g"] if p["tipo"] == "corte"] + [par(p["x"]) for p in e5["g"] if p["tipo"] == "dual"]
    e6 = R["e6"]; s += [fr(e6["rhs"]["x2"]), fr(e6["rhs"]["x1"]), num(e6["z0"], 2), par(e6["x"]), num(e6["z"])]
    e8 = R["e8"]; s += [str(e8["RyC"]["n_lp"]), str(e8["n_rya"]), num(e8["opt"][0]), str(len(e8["RyC"]["log"]))]
    e9 = R["e9"]; s += [num(e9["rango"][1], 2), ineq_txt(*e9["cg"])]
    e10 = R["e10"]; s += [num(e10["zf"], 2), num(e10["za"], 2), num(e10["zi"]), pct(e10["gap_f"], 1), pct(e10["gap_a"], 1),
                          fr(e10["xf"][2]), fr(e10["xf"][3]), fr(e10["xa"][3]), num(e10["factor"], 1)]
    C = R["caso"]
    s += [par(C["x_lp"]), pesos(C["z_lp"]), par(C["x"]), pesos(C["z"]), ineq_txt(*C["corte_red"]), str(C["n_pl_rya"])]
    s += [ineq_txt(*t["en_x"]) for t in C["todos0"]]
    s += [ineq_txt(*p["en_x"]) for p in C["g"] if p["tipo"] == "corte"] + [par(p["x"]) for p in C["g"] if p["tipo"] == "dual"]
    s += [pesos(p["z"]) for p in C["g"] if p["tipo"] == "dual"]
    return s


def tablas_en_md(R, md):
    faltan = []
    for k, t in tablas(R).items():
        for linea in t.splitlines():
            if linea not in md:
                faltan.append(f"{k}: {linea}")
    return faltan


def codigo_en_md(md):
    faltan = []
    for f in ["u06_comedor.mod", "u06_e10_cerveceria.mod", "u06_e10_floja.dat"]:
        for linea in (MODELOS / f).read_text(encoding="utf-8").splitlines():
            if linea.strip() and linea.rstrip() not in md:
                faltan.append(f"{f}: {linea.strip()}")
    return faltan


def cadena(R):
    C = R["caso"]; D = C["D"]
    R5 = U5.caso()
    ok = tuple(C["c"]) == (D["red"].MARGEN[0] * D["q"], D["red"].MARGEN[1] * D["q"])
    ok &= C["z_lp"] == R5["z0"] and C["z"] == R5["inc"][0] and C["x"] == R5["inc"][1]
    print("CADENA:", "OK, la pieza del caso calza (el mismo turno del sábado de la unidad 5: relajación $650.400, "
          "óptimo $648.000 en (11; 3))" if ok else "NO calza")
    return ok


if __name__ == "__main__" and "--explorar" not in sys.argv:
    R = resultados()
    C = R["caso"]
    print("== ejemplo:", par(R["ej"]["x_lp"]), "→", par(R["ej"]["x"]), "z =", fr(R["ej"]["z"]), "corte", ineq_ge(*R["ej"]["corte"]))
    print("== caso:", par(C["x_lp"]), pesos(C["z_lp"]), "→", par(C["x"]), pesos(C["z"]), "con", C["n_cortes"], "cortes;",
          "forma reducida: 1 corte,", ineq_txt(*C["corte_red"]))
    dibujar(R)
    comparar_con_opl(R)
    if not cadena(R):
        sys.exit(1)
    if "--tablas" in sys.argv:
        for k, t in tablas(R).items():
            print(f"\n### {k}\n{t}")
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md2 = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md2]
        faltan += tablas_en_md(R, md) + codigo_en_md(md)
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)


if __name__ == "__main__" and "--explorar" in sys.argv:
    R = resultados()
    def show(g):
        for p in g:
            if p["tipo"] == "corte":
                print("CORTE desde", p["basica"], [fr(v) for v in p["f"]], fr(p["f0"]), "en x:", ineq_txt(*p["en_x"]))
                for t in p["todos"]:
                    print("    posible:", t["basica"], ineq_txt(*t["en_x"]))
            else:
                print("DUAL sale", p["sale"], "entra", p["entra"], "z", fr(p["z"]), "x", vec(p["x"]))
    E = R["ej"]; print("== ejemplo", vec(E["x_lp"]), fr(E["z_lp"]), "->", vec(E["x"]), fr(E["z"])); [print(p["md"]) for p in E["pasos"]]; show(E["g"])
    h = R["h"]; print("== H", vec(h["x"]), fr(h["z"]), h["xi"], h["zi"], "V", h["V"]); [print(c) for c in h["clas"]]
    [print(o["c"], o["hull"], [cf[:3] for cf in o["activas"]], o["lp_entero"]) for o in h["obj"]]; print(h["originales"])
    print("== e2"); print(R["e2"]["md"]); [print(c["basica"], [fr(v) for v in c["f"]], fr(c["f0"]), ineq_txt(c["alfa"], c["beta"])) for c in R["e2"]["cortes"]]
    e3 = R["e3"]; print("== e3", e3["za"], e3["xa"], e3["max_suma"]); print(e3["md_a"]); [print(p.get("md_antes"), "\n", p.get("md")) for p in e3["pa"]]; print(e3["md_b"]); [print(p) for p in e3["pb"]]
    print("== e4", R["e4"]); e8 = R["e8"]; print("== e8 RyC", [(n["k"], n["fijas"], n["estado"], [(vec(s[1]), fr(s[0])) if s else None for s in n["lps"]], n.get("cortes")) for n in e8["RyC"]["log"]], "n_lp", e8["RyC"]["n_lp"], "rya", e8["n_rya"], e8["opt"])
    e5 = R["e5"]; print("== e5", vec(e5["x_lp"]), fr(e5["z_lp"]), "->", vec(e5["x"]), fr(e5["z"])); print(e5["md_lp"]); show(e5["g"])
    e6 = R["e6"]; print("== e6", e6["rhs"], fr(e6["z0"]), vec(e6["x"]), fr(e6["z"])); print(e6["md0"]); [print(p["md_antes"], "\n", p["md"]) for p in e6["pasos"]]
    print("== e9", R["e9"]); print("== e10", {k: (str(v) if not isinstance(v, list) else [str(t) for t in v]) for k, v in R["e10"].items()})
    C = R["caso"]; print("== caso", vec(C["x_lp"]), fr(C["z_lp"]), "->", vec(C["x"]), fr(C["z"]), "cortes", C["n_cortes"])
    [print("  posible:", t["basica"], ineq_txt(*t["en_x"])) for t in C["todos0"]]; show(C["g"]); [print(p.get("md")) for p in C["g"]]
    print("reducida:"); print(C["md_red"]); show(C["gr"]); print("corte red", ineq_txt(*C["corte_red"]), C["toca_red"])
