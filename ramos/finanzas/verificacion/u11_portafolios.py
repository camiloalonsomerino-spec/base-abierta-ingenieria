"""Unidad 11 · Portafolios.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto queda sin respaldo.

    py -3 -P u11_portafolios.py            # imprime los resultados
    py -3 -P u11_portafolios.py --revisar  # además los busca en el .md
"""
from math import sqrt
from pathlib import Path
import importlib.util, sys

sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- herramientas

def fmt(x, dec=2):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=2):
    return fmt(100 * x, dec) + " %"


def clp(x):
    return "$" + fmt(x, 0)


def cartera(w, e1, e2, s1, s2, cov):
    """Retorno esperado y desviación de una cartera con w en el activo 1 y 1 − w en el 2."""
    e = w * e1 + (1 - w) * e2
    v = w ** 2 * s1 ** 2 + (1 - w) ** 2 * s2 ** 2 + 2 * w * (1 - w) * cov
    return e, sqrt(v)


def minima_varianza(s1, s2, cov):
    return (s2 ** 2 - cov) / (s1 ** 2 + s2 ** 2 - 2 * cov)


def tangente(e1, e2, s1, s2, cov, rf):
    a1, a2 = e1 - rf, e2 - rf
    return (a1 * s2 ** 2 - a2 * cov) / (a1 * s2 ** 2 + a2 * s1 ** 2 - (a1 + a2) * cov)


def tangente_por_sistema(e1, e2, s1, s2, cov, rf):
    """Resuelve E_i − rf = Z1·cov(i,1) + Z2·cov(i,2) y normaliza: el método que sirve para n activos."""
    a1, a2 = e1 - rf, e2 - rf
    det = s1 ** 2 * s2 ** 2 - cov ** 2
    z1 = (a1 * s2 ** 2 - a2 * cov) / det
    z2 = (s1 ** 2 * a2 - cov * a1) / det
    return z1, z2, z1 / (z1 + z2)


def resolver(M, b):
    """Gauss con pivoteo parcial (sistemas chicos)."""
    n = len(b)
    A = [list(map(float, fila)) + [float(bi)] for fila, bi in zip(M, b)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(A[r][c]))
        A[c], A[p] = A[p], A[c]
        for r in range(n):
            if r != c:
                f = A[r][c] / A[c][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [A[i][n] / A[i][i] for i in range(n)]


def analisis_dos(e1, e2, s1, s2, rho, rf, A=None):
    cov = rho * s1 * s2
    wm = minima_varianza(s1, s2, cov)
    em, sm = cartera(wm, e1, e2, s1, s2, cov)
    wt = tangente(e1, e2, s1, s2, cov, rf)
    et, st = cartera(wt, e1, e2, s1, s2, cov)
    r = {"cov": cov, "wm": wm, "em": em, "sm": sm, "wt": wt, "et": et, "st": st,
         "sharpe": (et - rf) / st, "sharpe1": (e1 - rf) / s1, "sharpe2": (e2 - rf) / s2,
         "sistema": tangente_por_sistema(e1, e2, s1, s2, cov, rf)}
    if A is not None:
        r["y"] = (et - rf) / (A * st ** 2)
    return r


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Ejemplo resuelto · Martina vendió su auto y tiene $6.000.000 para invertir un año
EJ = dict(e1=0.115, s1=0.21, e2=0.072, s2=0.10, rho=0.28, rf=0.0415, A=4, W=6_000_000)
# (1) Fondo Andino Acciones · (2) Fondo Austral Balanceado · rf = depósito a plazo a un año

# 11.1 · Minera Norte (1) y Eléctrica Costa (2), 30 % y 70 %
E1 = dict(e1=0.14, s1=0.30, e2=0.08, s2=0.15, rho=0.20, w=0.30)
# 11.2 · tres escenarios: (probabilidad, retorno A, retorno B)
E2 = [(0.25, -0.12, 0.06), (0.50, 0.10, 0.04), (0.25, 0.28, 0.01)]
# 11.3 · correlación perfecta
E3 = dict(e1=0.13, s1=0.24, e2=0.06, s2=0.09)
# 11.5 y 11.6 · Viña del Valle (1) y Salmonera Fiordo (2)
E5 = dict(e1=0.10, s1=0.18, e2=0.15, s2=0.32, rho=0.10)
E5_PESOS = [0, 0.25, 0.50, 0.75, 1.0]     # peso en la viña
E6_RF, E6_SIGMA = 0.045, 0.15
# 11.7 · dos inversionistas con $10.000.000 cada uno
E7_W, E7_A = 10_000_000, (2, 7)
# 11.8 · n acciones iguales, mismo peso
E8 = dict(s=0.35, rho=0.25, n=[1, 2, 5, 10, 50])
# 11.9 · tres activos
E9_E = [0.11, 0.13, 0.05]
E9_S = [0.20, 0.25, 0.15]
E9_R = [[1, 0.5, -0.2], [0.5, 1, 0.1], [-0.2, 0.1, 1]]


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # ejemplo
    d = EJ
    ej = analisis_dos(d["e1"], d["e2"], d["s1"], d["s2"], d["rho"], d["rf"], d["A"])
    ej["e50"], ej["s50"] = cartera(0.5, d["e1"], d["e2"], d["s1"], d["s2"], ej["cov"])
    ej["prom50"] = 0.5 * d["s1"] + 0.5 * d["s2"]
    ej["var50"] = ej["s50"] ** 2
    ej["ahorro50"] = ej["prom50"] - ej["s50"]
    a1, a2 = d["e1"] - d["rf"], d["e2"] - d["rf"]
    ej["num"] = a1 * d["s2"] ** 2 - a2 * ej["cov"]
    ej["den"] = a1 * d["s2"] ** 2 + a2 * d["s1"] ** 2 - (a1 + a2) * ej["cov"]
    ej["riesgosa"] = ej["y"] * d["W"]
    ej["en1"] = ej["riesgosa"] * ej["wt"]
    ej["en2"] = ej["riesgosa"] * (1 - ej["wt"])
    ej["deposito"] = d["W"] - ej["riesgosa"]
    ej["e_comp"] = d["rf"] + ej["y"] * (ej["et"] - d["rf"])
    ej["s_comp"] = ej["y"] * ej["st"]
    ej["u_comp"] = ej["e_comp"] - 0.5 * d["A"] * ej["s_comp"] ** 2
    ej["u_tan"] = ej["et"] - 0.5 * d["A"] * ej["st"] ** 2
    ej["u_rf"] = d["rf"]
    R["ej"] = ej

    # 11.1
    d = E1
    cov = d["rho"] * d["s1"] * d["s2"]
    e, s = cartera(d["w"], d["e1"], d["e2"], d["s1"], d["s2"], cov)
    prom = d["w"] * d["s1"] + (1 - d["w"]) * d["s2"]
    R["e1"] = {"cov": cov, "e": e, "s": s, "prom": prom, "ahorro": prom - s}

    # 11.2
    ea = sum(p * a for p, a, _ in E2)
    eb = sum(p * b for p, _, b in E2)
    va = sum(p * (a - ea) ** 2 for p, a, _ in E2)
    vb = sum(p * (b - eb) ** 2 for p, _, b in E2)
    cv = sum(p * (a - ea) * (b - eb) for p, a, b in E2)
    rho = cv / sqrt(va * vb)
    sp_formula = cartera(0.5, ea, eb, sqrt(va), sqrt(vb), cv)[1]
    rp = [0.5 * a + 0.5 * b for _, a, b in E2]
    ep = sum(p * x for (p, _, _), x in zip(E2, rp))
    sp_directo = sqrt(sum(p * (x - ep) ** 2 for (p, _, _), x in zip(E2, rp)))
    R["e2"] = {"ea": ea, "eb": eb, "va": va, "vb": vb, "sa": sqrt(va), "sb": sqrt(vb), "cov": cv, "rho": rho,
               "rp": rp, "ep": ep, "sp_formula": sp_formula, "sp_directo": sp_directo}

    # 11.3
    d = E3
    w0 = d["s2"] / (d["s1"] + d["s2"])
    R["e3"] = {"w": w0, "e": w0 * d["e1"] + (1 - w0) * d["e2"],
               "s_menos1": abs(w0 * d["s1"] - (1 - w0) * d["s2"]),
               "s_mas1": w0 * d["s1"] + (1 - w0) * d["s2"]}

    # 11.5
    d = E5
    cov = d["rho"] * d["s1"] * d["s2"]
    puntos = [(w, *cartera(w, d["e1"], d["e2"], d["s1"], d["s2"], cov)) for w in E5_PESOS]
    wm = minima_varianza(d["s1"], d["s2"], cov)
    R["e5"] = {"cov": cov, "puntos": puntos, "wm": wm, "pmv": cartera(wm, d["e1"], d["e2"], d["s1"], d["s2"], cov)}

    # 11.6
    a6 = analisis_dos(d["e1"], d["e2"], d["s1"], d["s2"], d["rho"], E6_RF)
    a6["y15"] = E6_SIGMA / a6["st"]
    a6["e15"] = E6_RF + a6["sharpe"] * E6_SIGMA
    R["e6"] = a6

    # 11.7
    R["e7"] = {}
    for A in E7_A:
        y = (a6["et"] - E6_RF) / (A * a6["st"] ** 2)
        R["e7"][A] = {"y": y, "riesgosa": y * E7_W, "vina": y * E7_W * a6["wt"],
                      "salmonera": y * E7_W * (1 - a6["wt"]), "rf": E7_W * (1 - y),
                      "e": E6_RF + y * (a6["et"] - E6_RF), "s": y * a6["st"]}

    # 11.8
    d = E8
    R["e8"] = {n: sqrt(d["s"] ** 2 / n + (1 - 1 / n) * d["rho"] * d["s"] ** 2) for n in d["n"]}
    R["e8_limite"] = sqrt(d["rho"]) * d["s"]
    # σp² = ρσ² (sistemático, no baja con n) + (1 − ρ)σ²/n (diversificable)
    R["e8_sistematico"] = {n: d["rho"] * d["s"] ** 2 / R["e8"][n] ** 2 for n in d["n"]}

    # 11.9 · mínima varianza con tres activos: w ∝ Σ⁻¹·1
    S = [[E9_R[i][j] * E9_S[i] * E9_S[j] for j in range(3)] for i in range(3)]
    z = resolver(S, [1, 1, 1])
    w = [x / sum(z) for x in z]
    e9 = sum(wi * ei for wi, ei in zip(w, E9_E))
    s9 = sqrt(sum(w[i] * w[j] * S[i][j] for i in range(3) for j in range(3)))
    cov12 = S[0][1]
    w2 = minima_varianza(E9_S[0], E9_S[1], cov12)
    e2_, s2_ = cartera(w2, E9_E[0], E9_E[1], E9_S[0], E9_S[1], cov12)
    # gradiente en el óptimo: 2Σw tiene que dar el mismo valor en las tres filas (el multiplicador)
    lam = [2 * sum(S[i][j] * w[j] for j in range(3)) for i in range(3)]
    R["e9"] = {"S": S, "w": w, "e": e9, "s": s9, "w2": w2, "e2": e2_, "s2": s2_, "lambda": lam}
    return R


def caso():
    spec = importlib.util.spec_from_file_location("caso", Path(__file__).with_name("caso_valentina.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def resultados_caso(m):
    C = m.calcular()
    u = C["u11"]
    U = m.U11
    e1, e2 = U["E"]["Textil Andes"], U["E"]["Fondo IPSA"]
    s1, s2 = U["sigma"]["Textil Andes"], U["sigma"]["Fondo IPSA"]
    rf = C["u6"]["spot"][0]
    propio = analisis_dos(e1, e2, s1, s2, U["rho"], rf, U["aversion"])
    W = m.U10["riqueza"]
    extra = {"W": W, "riesgosa": u["fraccion_riesgosa"] * W,
             "textil": u["fraccion_riesgosa"] * W * u["w_tangente"],
             "fondo": u["fraccion_riesgosa"] * W * (1 - u["w_tangente"]),
             "deposito": W * (1 - u["fraccion_riesgosa"]),
             "e_comp": rf + u["fraccion_riesgosa"] * (u["e_tangente"] - rf),
             "s_comp": u["fraccion_riesgosa"] * u["s_tangente"],
             "sharpe_ta": (e1 - rf) / s1, "sharpe_fondo": (e2 - rf) / s2,
             "prom_s_min": u["w_min_var"] * s1 + (1 - u["w_min_var"]) * s2}
    return u, propio, extra


# ---------------------------------------------------------------- impresión

def imprimir(R, caso_r):
    ej = R["ej"]
    print("== Ejemplo · Martina")
    for k in ("cov", "e50", "s50", "prom50", "wm", "em", "sm", "wt", "et", "st", "sharpe", "sharpe1", "sharpe2",
              "y", "riesgosa", "en1", "en2", "deposito", "e_comp", "s_comp", "u_comp", "u_tan", "u_rf"):
        print(f"   {k:9} {ej[k]:.6f}")
    print("   sistema Z", [round(x, 6) for x in ej["sistema"]])
    print("== 11.1", {k: round(v, 6) for k, v in R["e1"].items()})
    print("== 11.2", {k: (round(v, 6) if isinstance(v, float) else [round(x, 4) for x in v]) for k, v in R["e2"].items()})
    print("== 11.3", {k: round(v, 6) for k, v in R["e3"].items()})
    print("== 11.5 cov", round(R["e5"]["cov"], 6), "PMV", round(R["e5"]["wm"], 6), [round(x, 6) for x in R["e5"]["pmv"]])
    for w, e, s in R["e5"]["puntos"]:
        print(f"     w={w:.2f}  E={e:.6f}  s={s:.6f}")
    a6 = R["e6"]
    print("== 11.6", {k: (round(v, 6) if isinstance(v, float) else [round(x, 6) for x in v]) for k, v in a6.items()})
    print("== 11.7", {A: {k: round(v, 4) for k, v in d.items()} for A, d in R["e7"].items()})
    print("== 11.8", {n: round(v, 6) for n, v in R["e8"].items()}, "límite", R["e8_limite"],
          "sistemático", {n: round(v, 4) for n, v in R["e8_sistematico"].items()})
    e9 = R["e9"]
    print("== 11.9 S", [[round(x, 4) for x in f] for f in e9["S"]])
    print("   w", [round(x, 6) for x in e9["w"]], "E", round(e9["e"], 6), "s", round(e9["s"], 6), "λ", [round(x, 6) for x in e9["lambda"]])
    print("   solo A y B: w", round(e9["w2"], 6), "E", round(e9["e2"], 6), "s", round(e9["s2"], 6))
    u, propio, extra = caso_r
    print("== Caso u11 (script)", {k: round(v, 6) for k, v in u.items()})
    print("   extra", {k: round(v, 4) for k, v in extra.items()})


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R, caso_r):
    e = []
    ej = R["ej"]
    e += [fmt(ej["cov"], 5), pct(ej["e50"]), pct(ej["s50"]), pct(ej["prom50"]),
          pct(ej["wm"]), pct(ej["em"]), pct(ej["sm"]), pct(ej["wt"]), pct(1 - ej["wt"]), pct(ej["et"]), pct(ej["st"]),
          fmt(ej["sharpe"], 4), fmt(ej["sharpe1"], 4), fmt(ej["sharpe2"], 4), pct(ej["y"]),
          clp(ej["riesgosa"]), clp(ej["en1"]), clp(ej["en2"]), clp(ej["deposito"]),
          pct(ej["e_comp"]), pct(ej["s_comp"]), fmt(ej["sistema"][0], 4), fmt(ej["sistema"][1], 4),
          fmt(ej["u_comp"], 4), fmt(ej["u_tan"], 4), fmt(ej["var50"], 6), fmt(100 * ej["ahorro50"]) + " puntos",
          fmt(ej["num"], 6), fmt(ej["den"], 6), fmt(ej["sistema"][0] + ej["sistema"][1], 4)]
    d = R["e1"]
    e += [fmt(d["cov"], 4), pct(d["e"]), pct(d["s"]), pct(d["prom"]), fmt(100 * d["ahorro"]) + " puntos"]
    d = R["e2"]
    e += [pct(d["ea"]), pct(d["eb"]), pct(d["sa"]), pct(d["sb"]), fmt(d["cov"], 6), fmt(d["rho"], 4),
          pct(d["ep"]), pct(d["sp_directo"])]
    d = R["e3"]
    e += [pct(d["w"]), pct(d["e"]), pct(d["s_mas1"])]
    d = R["e5"]
    e += [pct(d["wm"]), pct(d["pmv"][0]), pct(d["pmv"][1])]
    for _, ee, ss in d["puntos"]:
        e += [pct(ee), pct(ss)]
    a6 = R["e6"]
    e += [pct(a6["wt"]), pct(a6["et"]), pct(a6["st"]), fmt(a6["sharpe"], 4), fmt(a6["sharpe1"], 4),
          fmt(a6["sharpe2"], 4), pct(a6["y15"]), pct(a6["e15"]),
          fmt(a6["sistema"][0], 4), fmt(a6["sistema"][1], 4), fmt(a6["sistema"][0] + a6["sistema"][1], 4)]
    for A, d in R["e7"].items():
        e += [pct(d["y"]), clp(d["riesgosa"]), clp(d["vina"]), clp(d["salmonera"]), pct(d["e"]), pct(d["s"])]
        e += [clp(abs(d["rf"]))]
    e += [pct(v) for v in R["e8"].values()] + [pct(R["e8_limite"])]
    e += [pct(v, 1) for v in R["e8_sistematico"].values() if v > 0]
    e9 = R["e9"]
    e += [pct(x) for x in e9["w"]] + [pct(e9["e"]), pct(e9["s"]), pct(e9["w2"]), pct(e9["s2"]), pct(e9["e2"]),
          fmt(e9["lambda"][0], 4), fmt(e9["lambda"][0] / 2, 4), fmt(e9["s"] ** 2, 4)]
    u, propio, extra = caso_r
    e += [pct(u["rf"]), fmt(u["cov"], 5), pct(u["w_min_var"]), pct(1 - u["w_min_var"]), pct(u["e_min_var"]),
          pct(u["s_min_var"]), pct(u["w_tangente"]), pct(1 - u["w_tangente"]), pct(u["e_tangente"]),
          pct(u["s_tangente"]), fmt(u["sharpe"], 4), pct(u["fraccion_riesgosa"]),
          clp(extra["riesgosa"]), clp(extra["textil"]), clp(extra["fondo"]), clp(extra["deposito"]),
          pct(extra["e_comp"]), pct(extra["s_comp"]), fmt(extra["sharpe_ta"], 4), fmt(extra["sharpe_fondo"], 4),
          pct(extra["prom_s_min"])]
    return e


if __name__ == "__main__":
    R = resultados()
    m = caso()
    caso_r = resultados_caso(m)
    imprimir(R, caso_r)
    # el caso tiene que salir igual recalculado acá y en el script del caso
    u, propio, _ = caso_r
    pares = {"w_min_var": "wm", "e_min_var": "em", "s_min_var": "sm", "w_tangente": "wt", "e_tangente": "et",
             "s_tangente": "st", "sharpe": "sharpe", "fraccion_riesgosa": "y", "cov": "cov"}
    distintos = [k for k, p in pares.items() if abs(u[k] - propio[p]) > 1e-12]
    z1, z2, wz = propio["sistema"]
    if abs(wz - u["w_tangente"]) > 1e-12:
        distintos.append("tangente por sistema")
    print("\nCADENA:", "OK, la unidad 11 calza con el caso integrador" if not distintos else f"NO calza: {distintos}")
    if distintos:
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "11-portafolios.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".").replace("\\%", "%").replace("\\,", " ").replace("\\$", "$").replace("−", "-")
        faltan = [x for x in dict.fromkeys(esperados(R, caso_r)) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
