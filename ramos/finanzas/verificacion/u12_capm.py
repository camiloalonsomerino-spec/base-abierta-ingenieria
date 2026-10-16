"""Unidad 12 · CAPM, betas y costo de capital.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto queda sin respaldo.

    py -3 -P u12_capm.py            # imprime los resultados
    py -3 -P u12_capm.py --revisar  # además los busca en el .md
"""
from math import sqrt
from pathlib import Path
from statistics import fmean
import importlib.util, sys

sys.stdout.reconfigure(encoding="utf-8")

T_975 = {4: 2.776, 6: 2.447, 10: 2.228}   # t de Student, 95 % a dos colas, por grados de libertad


# ---------------------------------------------------------------- herramientas

def fmt(x, dec=2):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=2):
    return fmt(100 * x, dec) + " %"


def clp(x):
    return "$" + fmt(x, 0)


def regresion(x, y):
    """Mínimos cuadrados de y = a + b·x, con lo que hace falta para leerla."""
    n = len(x)
    mx, my = fmean(x), fmean(y)
    sxx = sum((xi - mx) ** 2 for xi in x)
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    syy = sum((yi - my) ** 2 for yi in y)
    b = sxy / sxx
    a = my - b * mx
    ssr = sum((yi - a - b * xi) ** 2 for xi, yi in zip(x, y))
    se = sqrt(ssr / (n - 2))
    return {"n": n, "mx": mx, "my": my, "sxx": sxx, "sxy": sxy, "syy": syy, "b": b, "a": a,
            "r2": 1 - ssr / syy, "se_resid": se, "se_b": se / sqrt(sxx),
            "se_a": se * sqrt(1 / n + mx ** 2 / sxx),
            "dx": [xi - mx for xi in x], "dy": [yi - my for yi in y]}


def capm(rf, beta, premio):
    return rf + beta * premio


def van_anualidad(k, inversion, flujo, n):
    return -inversion + flujo * (1 - (1 + k) ** -n) / k


def desapalancar(bl, de, t):
    return bl / (1 + (1 - t) * de)


def apalancar(bu, de, t):
    return bu * (1 + (1 - t) * de)


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Ejemplo resuelto · Camila mira la acción de Farmacias Lago Sur (ficticia), seis meses
EJ_RM = [0.0296, -0.0187, 0.0243, 0.0461, -0.0258, 0.0117]     # índice
EJ_RI = [0.0407, -0.0293, 0.0126, 0.0574, -0.0198, 0.0218]     # Farmacias Lago Sur
EJ_RF, EJ_PREMIO, EJ_ANALISTA = 0.0435, 0.0615, 0.137

# 12.1
E1_RF, E1_PREMIO, E1_BETAS = 0.052, 0.068, [0.55, 1.00, 1.45]
# 12.2
E2 = dict(cov=0.0156, var_m=0.0225, rho=0.62, s_i=0.37, s_m=0.19, w=0.35)
# 12.4 · (beta, retorno que proyecta un analista)
E4_RF, E4_RM = 0.04, 0.105
E4 = {"Acción X": (1.2, 0.129), "Acción Y": (0.7, 0.079)}
# 12.5 · ocho meses
E5_RM = [0.0217, -0.0346, 0.0408, 0.0083, -0.0124, 0.0297, -0.0241, 0.0106]
E5_RI = [0.0184, -0.0163, 0.0271, 0.0147, -0.0112, 0.0058, -0.0039, 0.0134]
# 12.6 · regresión mensual de un fondo mutuo
E6 = dict(a=0.0042, b=1.25, rf_m=0.0035)
# 12.7 · empresa eléctrica que evalúa un centro de datos (millones de pesos)
E7 = dict(rf=0.047, premio=0.059, beta_empresa=0.65, beta_proyecto=1.35, inversion=1250, flujo=205, n=10)
# 12.8 · comparables (beta apalancada, D/E) y empresa objetivo
E8 = dict(comp={"Comparable 1": (1.08, 0.32), "Comparable 2": (1.47, 0.85), "Comparable 3": (1.21, 0.58)},
          de_obj=0.65, t=0.27, rf=0.05, premio=0.065)
# 12.9 · WACC (pesos; proyecto en millones)
E9 = dict(acciones=1_800_000, precio=3_650, beta=1.24, bonos=35_000, nominal=100_000, precio_bono=72_400,
          plazo=5, t=0.27, rf=0.05, premio=0.065, inversion=1400, flujo=245, n=12)
# 12.10 · beta negativa (con la tasa y el premio del caso)
E10_BETA = -0.3


# ---------------------------------------------------------------- resultados

def caso():
    spec = importlib.util.spec_from_file_location("caso", Path(__file__).with_name("caso_valentina.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def resultados(m):
    C = m.calcular()
    R = {}
    # ejemplo
    r = regresion(EJ_RM, EJ_RI)
    r["k"] = capm(EJ_RF, r["b"], EJ_PREMIO)
    r["alfa_analista"] = EJ_ANALISTA - r["k"]
    r["rm_anual"] = EJ_RF + EJ_PREMIO
    r["dxdy"] = [a * b for a, b in zip(r["dx"], r["dy"])]
    r["dx2"] = [a * a for a in r["dx"]]
    R["ej"] = r

    R["e1"] = [capm(E1_RF, b, E1_PREMIO) for b in E1_BETAS]
    R["e1_rm"] = E1_RF + E1_PREMIO

    d = E2
    b1 = d["cov"] / d["var_m"]
    b2 = d["rho"] * d["s_i"] / d["s_m"]
    R["e2"] = {"b1": b1, "b2": b2, "bp": d["w"] * b1 + (1 - d["w"]) * b2}

    R["e4"] = {}
    for k, (b, proy) in E4.items():
        req = capm(E4_RF, b, E4_RM - E4_RF)
        R["e4"][k] = {"req": req, "alfa": proy - req}

    r5 = regresion(E5_RM, E5_RI)
    r5["sist"] = r5["r2"]
    r5["div"] = 1 - r5["r2"]
    R["e5"] = r5

    d = E6
    a_capm = d["rf_m"] * (1 - d["b"])
    jensen = d["a"] - a_capm
    R["e6"] = {"a_capm": a_capm, "jensen": jensen, "jensen_anual": (1 + jensen) ** 12 - 1}

    d = E7
    ke = capm(d["rf"], d["beta_empresa"], d["premio"])
    kp = capm(d["rf"], d["beta_proyecto"], d["premio"])
    R["e7"] = {"k_empresa": ke, "k_proyecto": kp,
               "van_empresa": van_anualidad(ke, d["inversion"], d["flujo"], d["n"]),
               "van_proyecto": van_anualidad(kp, d["inversion"], d["flujo"], d["n"]),
               "factor_empresa": (1 - (1 + ke) ** -d["n"]) / ke, "factor_proyecto": (1 - (1 + kp) ** -d["n"]) / kp}

    d = E8
    bus = {k: desapalancar(bl, de, d["t"]) for k, (bl, de) in d["comp"].items()}
    bu = fmean(bus.values())
    bl = apalancar(bu, d["de_obj"], d["t"])
    R["e8"] = {"bu": bus, "bu_prom": bu, "bl": bl, "ke": capm(d["rf"], bl, d["premio"]),
               "ke_sin_deuda": capm(d["rf"], bu, d["premio"])}

    d = E9
    E = d["acciones"] * d["precio"]
    D = d["bonos"] * d["precio_bono"]
    V = E + D
    kd = (d["nominal"] / d["precio_bono"]) ** (1 / d["plazo"]) - 1
    ke9 = capm(d["rf"], d["beta"], d["premio"])
    wacc = E / V * ke9 + D / V * kd * (1 - d["t"])
    R["e9"] = {"E": E, "D": D, "V": V, "wE": E / V, "wD": D / V, "kd": kd, "kd_neto": kd * (1 - d["t"]), "ke": ke9,
               "wacc": wacc, "van": van_anualidad(wacc, d["inversion"], d["flujo"], d["n"]),
               "van_ke": van_anualidad(ke9, d["inversion"], d["flujo"], d["n"])}

    rf = C["u6"]["spot"][0]
    prem = m.U12["premio_mercado"]
    R["e10"] = {"k": capm(rf, E10_BETA, prem), "rf": rf}

    # caso
    u = C["u12"]
    rc = regresion(u["rm"], u["ri"])
    rf_m = (1 + rf) ** (1 / 12) - 1
    t = T_975[rc["n"] - 2]
    beta_real = m.U12["beta_real"]
    k_real = capm(rf, beta_real, prem)
    blume = 2 / 3 * rc["b"] + 1 / 3
    k_blume = capm(rf, blume, prem)
    g, d1 = m.U9["g"], m.U9["dividendo_1"]
    R["caso"] = {"u": u, "reg": rc, "rf": rf, "rf_m": rf_m, "premio": prem, "rm_anual": rf + prem,
                 "ic": (rc["b"] - t * rc["se_b"], rc["b"] + t * rc["se_b"]), "t": t,
                 "a_capm": rf_m * (1 - rc["b"]), "jensen": rc["a"] - rf_m * (1 - rc["b"]),
                 "beta_real": beta_real, "k_real": k_real, "p_real": d1 / (k_real - g),
                 "blume": blume, "k_blume": k_blume, "p_blume": d1 / (k_blume - g),
                 "k_u9": m.U9["k_analistas"], "p_u9": C["u9"]["precio_gordon"],
                 "k_u5": m.U5["tasa"], "van_u5": C["u5"]["van"], "flujos_u5": C["u5"]["flujos"],
                 "fondo_ipsa": m.U11["E"]["Fondo IPSA"], "beta_proyecto": m.U12["beta_proyecto"]}
    return R


# ---------------------------------------------------------------- impresión

def imprimir(R):
    r = R["ej"]
    print("== Ejemplo · Farmacias Lago Sur")
    for k in ("mx", "my", "sxx", "sxy", "syy", "b", "a", "r2", "se_resid", "se_b", "k", "alfa_analista", "rm_anual"):
        print(f"   {k:14} {r[k]:.6f}")
    print("   dx", [round(v, 4) for v in r["dx"]]); print("   dy", [round(v, 4) for v in r["dy"]])
    print("   dx·dy", [round(v, 6) for v in r["dxdy"]]); print("   dx²", [round(v, 6) for v in r["dx2"]])
    print("== 12.1", [round(v, 6) for v in R["e1"]], "E[Rm]", R["e1_rm"])
    print("== 12.2", {k: round(v, 6) for k, v in R["e2"].items()})
    print("== 12.4", {k: {kk: round(vv, 6) for kk, vv in v.items()} for k, v in R["e4"].items()})
    r5 = R["e5"]
    print("== 12.5", {k: round(r5[k], 6) for k in ("mx", "my", "sxx", "sxy", "b", "a", "r2", "sist", "div", "se_resid", "se_b")})
    print("== 12.6", {k: round(v, 6) for k, v in R["e6"].items()})
    print("== 12.7", {k: round(v, 6) for k, v in R["e7"].items()})
    print("== 12.8", {k: (round(v, 6) if isinstance(v, float) else {kk: round(vv, 6) for kk, vv in v.items()}) for k, v in R["e8"].items()})
    print("== 12.9", {k: round(v, 6) for k, v in R["e9"].items()})
    print("== 12.10", {k: round(v, 6) for k, v in R["e10"].items()})
    c = R["caso"]
    print("== Caso u12 (script)", {k: (round(v, 6) if isinstance(v, float) else v) for k, v in c["u"].items()})
    rc = c["reg"]
    print("   regresión", {k: round(rc[k], 6) for k in ("mx", "my", "sxx", "sxy", "b", "a", "r2", "se_resid", "se_b", "se_a")})
    print("   extra", {k: (round(v, 6) if isinstance(v, float) else v) for k, v in c.items() if k not in ("u", "reg")})


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    e = []
    r = R["ej"]
    e += [pct(r["mx"]), pct(r["my"]), fmt(r["sxx"], 6), fmt(r["sxy"], 6), fmt(r["b"], 4), pct(r["a"]),
          fmt(r["r2"], 2), pct(r["k"]), fmt(100 * r["alfa_analista"]) + " puntos", pct(r["rm_anual"]),
          fmt(r["se_b"], 2), fmt(T_975[r["n"] - 2], 3),
          fmt(r["b"] - T_975[r["n"] - 2] * r["se_b"], 2), fmt(r["b"] + T_975[r["n"] - 2] * r["se_b"], 2)]
    e += [fmt(100 * v, 2) for v in r["dx"]] + [fmt(100 * v, 2) for v in r["dy"]]
    e += [fmt(v, 6) for v in r["dxdy"]] + [fmt(v, 6) for v in r["dx2"]]
    e += [pct(v) for v in R["e1"]]
    e += [fmt(R["e2"]["b1"], 4), fmt(R["e2"]["b2"], 4), fmt(R["e2"]["bp"], 4)]
    for v in R["e4"].values():
        e += [pct(v["req"]), fmt(100 * v["alfa"]) + " puntos"]
    r5 = R["e5"]
    e += [pct(r5["mx"]), pct(r5["my"]), fmt(r5["sxx"], 6), fmt(r5["sxy"], 6), fmt(r5["b"], 4), pct(r5["a"], 3),
          fmt(r5["r2"], 2), pct(r5["sist"], 0), pct(r5["div"], 0), fmt(r5["se_b"], 2)]
    e += [pct(R["e6"]["a_capm"], 4), pct(R["e6"]["jensen"], 4), pct(R["e6"]["jensen_anual"])]
    d = R["e7"]
    e += [pct(d["k_empresa"], 3), pct(d["k_proyecto"], 3), fmt(d["van_empresa"], 1), fmt(d["van_proyecto"], 1),
          fmt(d["factor_empresa"], 4), fmt(d["factor_proyecto"], 4)]
    d = R["e8"]
    e += [fmt(v, 4) for v in d["bu"].values()] + [fmt(d["bu_prom"], 4), fmt(d["bl"], 4), pct(d["ke"]), pct(d["ke_sin_deuda"])]
    d = R["e9"]
    e += [fmt(d["E"] / 1e6, 0), fmt(d["D"] / 1e6, 0), fmt(d["V"] / 1e6, 0), pct(d["wE"]), pct(d["wD"]), pct(d["kd"]),
          pct(d["kd_neto"]), pct(d["ke"]), pct(d["wacc"]), fmt(d["van"], 1), fmt(d["van_ke"], 1)]
    e += [pct(R["e10"]["k"]), pct(R["e10"]["rf"])]
    c = R["caso"]
    u, rc = c["u"], c["reg"]
    e += [fmt(100 * v, 2) for v in u["rm"]] + [fmt(100 * v, 2) for v in u["ri"]]
    e += [fmt(u["beta"], 4), pct(u["alfa"]), pct(u["k_capm"]), fmt(u["precio_con_capm"], 2), pct(u["k_proyecto"]),
          clp(u["van_proyecto_capm"]), pct(c["k_u9"], 0), fmt(c["p_u9"], 2), pct(c["k_u5"], 0), clp(c["van_u5"]),
          pct(rc["mx"]), pct(rc["my"]), fmt(rc["r2"], 2), fmt(rc["se_b"], 2), fmt(c["ic"][0], 2), fmt(c["ic"][1], 2),
          pct(c["rf_m"], 3), pct(c["a_capm"], 3), pct(c["jensen"]), fmt(c["beta_real"], 2), pct(c["k_real"]),
          fmt(c["p_real"], 2), fmt(c["blume"], 4), pct(c["k_blume"]), fmt(c["p_blume"], 2), pct(c["rm_anual"]),
          pct(c["fondo_ipsa"], 1), fmt(c["beta_proyecto"], 2), pct(c["rf"]), fmt(rc["se_a"] * 100, 2)]
    e += [clp(f) for f in c["flujos_u5"] if f > 0] + [clp(-f) for f in c["flujos_u5"] if f < 0]
    return e


if __name__ == "__main__":
    m = caso()
    R = resultados(m)
    imprimir(R)
    # el caso tiene que salir igual recalculado acá y en el script del caso
    c = R["caso"]; u, rc = c["u"], c["reg"]
    C = m.calcular()
    k_proy = capm(c["rf"], c["beta_proyecto"], c["premio"])
    van_proy = sum(f / (1 + k_proy) ** t for t, f in enumerate(C["u5"]["flujos"]))
    chequeos = {
        "beta": abs(rc["b"] - u["beta"]) < 1e-12,
        "alfa": abs(rc["a"] - u["alfa"]) < 1e-12,
        "k_capm": abs(capm(c["rf"], rc["b"], c["premio"]) - u["k_capm"]) < 1e-12,
        "precio": abs(m.U9["dividendo_1"] / (u["k_capm"] - m.U9["g"]) - u["precio_con_capm"]) < 1e-9,
        "k_proyecto": abs(k_proy - u["k_proyecto"]) < 1e-12,
        "van_proyecto": abs(van_proy - u["van_proyecto_capm"]) < 1e-6,
        "rf = spot 1 año = rf u11": abs(c["rf"] - C["u11"]["rf"]) < 1e-15,
    }
    malos = [k for k, ok in chequeos.items() if not ok]
    print("\nCADENA:", "OK, la unidad 12 calza con el caso integrador" if not malos else f"NO calza: {malos}")
    if malos:
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "12-capm-y-costo-de-capital.md").read_text(encoding="utf-8")
        md = (md.replace("{,}", ",").replace("{.}", ".").replace("\\%", "%").replace("\\,", " ")
                .replace("\\$", "$").replace("−", "-"))
        faltan = [x for x in dict.fromkeys(esperados(R)) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
