"""Unidad 2 · Tasas de interés.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto queda sin respaldo.

    py -3 -P u02_tasas.py            # imprime los resultados
    py -3 -P u02_tasas.py --revisar  # además los busca en el .md
"""
from math import exp, log
from pathlib import Path
import importlib.util
import sys

sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- herramientas

def fmt(x, dec=2):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return fmt(round(x), 0)


def pct(x, dec=2):
    """Tasa como porcentaje, solo el número (el .md escribe « %» aparte)."""
    return fmt(100 * x, dec)


def tea_nominal(j, m):
    """Tasa nominal anual j capitalizable m veces al año → efectiva anual."""
    return (1 + j / m) ** m - 1


def tea_continua(j):
    return exp(j) - 1


def equivalente(i, k):
    """Tasa de un período → tasa de un período k veces más largo (k puede ser fracción)."""
    return (1 + i) ** k - 1


def real(nominal, inflacion):
    return (1 + nominal) / (1 + inflacion) - 1


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso. Las tasas no
# describen el mercado chileno de ninguna fecha, y la UF de los ejemplos es una cifra ficticia.

TABLA_FREC = {"j": 0.09, "m": [1, 2, 4, 12, 365]}                 # sección 2
TABLA_EQ = {"tea": 0.09}                                          # sección 3
TABLA_FISHER = [(0.10, 0.02), (0.40, 0.30)]                       # sección 4
UF_EJ = {"uf_hoy": 30_000, "uf": 500, "real": 0.02, "inflacion": 0.04}   # sección 5, UF ficticia
EJEMPLO = {"monto": 2_400_000, "meses": 9, "x_mensual": 0.0145, "y_nominal": 0.182, "z_efectiva": 0.191,
           "inflacion": 0.038}
E1 = {"j": 0.108, "m": [4, 12, 365]}
E2 = {"tea": 0.074, "mensual": 0.012}
E3 = {"nominal": 0.059, "inflacion": 0.043}
E4 = {"nominal_mensual": 0.149, "efectiva": 0.158}               # comente
E5 = {"mensual": 0.0285, "techo": 0.38}
E6 = {"pesos": 0.0645, "uf_real": 0.0235, "inflacion": 0.0355, "inflacion_alta": 0.05}
E7 = {"continua": 0.057, "efectiva": 0.0585, "monto": 2_750_000, "anios": 2.5}
E8 = {"tasa": 0.044, "monto": 8_000_000}
E9 = {"uf_real": 0.039, "pesos": 0.073}                           # comente
E10 = {"monto": 4_100_000, "t1": (0.005, 8), "t2_tea": 0.069, "t2_meses": 10, "t3_nominal": 0.063, "t3_meses": 6,
       "inflacion": 0.035, "spot1": 0.056, "spot2": 0.060}


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    j = TABLA_FREC["j"]
    R["frec"] = [(m, j / m, tea_nominal(j, m)) for m in TABLA_FREC["m"]] + [("continua", None, tea_continua(j))]
    t = TABLA_EQ["tea"]
    R["eq"] = {"mensual": equivalente(t, 1 / 12), "dividir": t / 12, "trimestral": equivalente(t, 1 / 4),
               "semestral": equivalente(t, 1 / 2), "anual_desde_div": equivalente(t / 12, 12)}
    R["fisher"] = [(n, p, real(n, p), n - p) for n, p in TABLA_FISHER]
    u = UF_EJ
    uf_fin = u["uf_hoy"] * (1 + u["inflacion"])
    uf_recibe = u["uf"] * (1 + u["real"])
    R["uf"] = {"pesos_hoy": u["uf"] * u["uf_hoy"], "uf_fin": uf_fin, "uf_recibe": uf_recibe,
               "pesos_fin": uf_recibe * uf_fin, "nominal": (1 + u["real"]) * (1 + u["inflacion"]) - 1}

    e = EJEMPLO
    tea_x = equivalente(e["x_mensual"], 12)
    men_y = e["y_nominal"] / 12
    tea_y = tea_nominal(e["y_nominal"], 12)
    men_z = equivalente(e["z_efectiva"], 1 / 12)
    pagos = {k: e["monto"] * (1 + i) ** e["meses"] for k, i in (("X", e["x_mensual"]), ("Y", men_y), ("Z", men_z))}
    R["ej"] = {"tea_x": tea_x, "men_y": men_y, "tea_y": tea_y, "men_z": men_z, "tea_z": e["z_efectiva"],
               "pago": pagos, "interes": {k: v - e["monto"] for k, v in pagos.items()},
               "dif_y_x": pagos["Y"] - pagos["X"], "real_x": real(tea_x, e["inflacion"]),
               "aprox_x": tea_x - e["inflacion"], "suma_y": e["y_nominal"] / 12 * 12}

    R["e1"] = {m: tea_nominal(E1["j"], m) for m in E1["m"]}
    R["e1"]["continua"] = tea_continua(E1["j"])
    R["e1"]["trim"] = E1["j"] / 4
    R["e1"]["mens"] = E1["j"] / 12

    R["e2"] = {"mensual": equivalente(E2["tea"], 1 / 12), "trimestral": equivalente(E2["tea"], 1 / 4),
               "semestral": equivalente(E2["tea"], 1 / 2), "dividir": E2["tea"] / 12,
               "tea_desde_mensual": equivalente(E2["mensual"], 12), "por12": E2["mensual"] * 12}

    R["e3"] = {"exacta": real(E3["nominal"], E3["inflacion"]), "aprox": E3["nominal"] - E3["inflacion"]}
    R["e3"]["error"] = R["e3"]["aprox"] - R["e3"]["exacta"]

    R["e4"] = {"tea_a": tea_nominal(E4["nominal_mensual"], 12), "men_b": equivalente(E4["efectiva"], 1 / 12),
               "men_a": E4["nominal_mensual"] / 12}

    R["e5"] = {"tea": equivalente(E5["mensual"], 12), "max_mensual": equivalente(E5["techo"], 1 / 12),
               "max_si_nominal": E5["techo"] / 12, "por12": E5["mensual"] * 12, "tea_si_nominal": tea_nominal(E5["techo"], 12)}

    e6 = E6
    R["e6"] = {"uf_nominal": (1 + e6["uf_real"]) * (1 + e6["inflacion"]) - 1,
               "pesos_real": real(e6["pesos"], e6["inflacion"]),
               "quiebre": (1 + e6["pesos"]) / (1 + e6["uf_real"]) - 1,
               "pesos_real_alta": real(e6["pesos"], e6["inflacion_alta"]),
               "uf_nominal_alta": (1 + e6["uf_real"]) * (1 + e6["inflacion_alta"]) - 1}

    e7 = E7
    R["e7"] = {"tea_cont": tea_continua(e7["continua"]), "cont_equiv": log(1 + e7["efectiva"]),
               "vf_cont": e7["monto"] * exp(e7["continua"] * e7["anios"]),
               "vf_ef": e7["monto"] * (1 + e7["efectiva"]) ** e7["anios"]}
    R["e7"]["dif"] = R["e7"]["vf_cont"] - R["e7"]["vf_ef"]

    e8 = E8
    R["e8"] = {"sem_nom": e8["tasa"] / 2, "sem_ef": equivalente(e8["tasa"], 1 / 2),
               "vf_nom": e8["monto"] * (1 + e8["tasa"] / 2), "vf_ef": e8["monto"] * (1 + e8["tasa"]) ** 0.5}
    R["e8"]["dif"] = R["e8"]["vf_nom"] - R["e8"]["vf_ef"]
    R["e8"]["tea_nom"] = tea_nominal(e8["tasa"], 2)

    e9 = E9
    R["e9"] = {"quiebre": (1 + e9["pesos"]) / (1 + e9["uf_real"]) - 1, "uf_nominal_3": (1 + e9["uf_real"]) * 1.03 - 1,
               "uf_nominal_5": (1 + e9["uf_real"]) * 1.05 - 1, "pesos_real_3": real(e9["pesos"], 0.03),
               "pesos_real_5": real(e9["pesos"], 0.05)}

    e = E10
    i1, n1 = e["t1"]
    i2 = equivalente(e["t2_tea"], 1 / 12)
    i3 = e["t3_nominal"] / 12
    f1, f2, f3 = (1 + i1) ** n1, (1 + i2) ** e["t2_meses"], (1 + i3) ** e["t3_meses"]
    n_tot = n1 + e["t2_meses"] + e["t3_meses"]
    vf_ = e["monto"] * f1 * f2 * f3
    i_eq = (f1 * f2 * f3) ** (1 / n_tot) - 1
    prom_arit = (i1 * n1 + i2 * e["t2_meses"] + i3 * e["t3_meses"]) / n_tot
    tea_eq = equivalente(i_eq, 12)
    R["e10"] = {"i2": i2, "i3": i3, "f1": f1, "f2": f2, "f3": f3, "s1": e["monto"] * f1, "s2": e["monto"] * f1 * f2,
                "vf": vf_, "i_eq": i_eq, "prom_arit": prom_arit, "tea_eq": tea_eq,
                "real_anual": real(tea_eq, e["inflacion"]), "vf_real": vf_ / (1 + e["inflacion"]) ** 2,
                "forward": (1 + e["spot2"]) ** 2 / (1 + e["spot1"]) - 1}
    return R


def caso():
    spec = importlib.util.spec_from_file_location("caso", Path(__file__).with_name("caso_valentina.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    U1, U2, C = m.U1, m.U2, m.calcular()
    c2 = C["u2"]
    propio = {"tea_a": tea_nominal(U2["banco_a_nominal"], U2["banco_a_cap"]), "tea_b": U2["banco_b_efectiva"],
              "mensual_b": equivalente(U2["banco_b_efectiva"], 1 / 12),
              "real_a": real(tea_nominal(U2["banco_a_nominal"], U2["banco_a_cap"]), U2["inflacion"]),
              "real_b": real(U2["banco_b_efectiva"], U2["inflacion"])}
    calza = all(abs(propio[k] - c2[k]) < 1e-12 for k in propio)
    mensual_a = U2["banco_a_nominal"] / U2["banco_a_cap"]
    calza = calza and abs(mensual_a - U1["tasa_mensual"]) < 1e-12      # el 0,55 % de la unidad 1 sale del banco A
    a, n = U1["ahorro_hoy"], U1["meses"]
    vf_a = C["u1"]["vf_compuesto"]
    vf_b = a * (1 + U2["banco_b_efectiva"]) ** (n / 12)
    return {"U2": U2, **c2, "mensual_a": mensual_a, "aprox_a": c2["tea_a"] - U2["inflacion"],
            "aprox_b": c2["tea_b"] - U2["inflacion"], "vf_a": vf_a, "vf_b": vf_b, "dif_vf": vf_a - vf_b,
            "vf_real": vf_a / (1 + U2["inflacion"]) ** (n / 12), "gana_nominal": vf_a - a, "gana_real": vf_a / (1 + U2["inflacion"]) ** (n / 12) - a,
            "control_real": a * (1 + c2["real_a"]) ** (n / 12), "calza": calza}


def imprimir(R, K):
    print("== Sección 2 · 9 % nominal según frecuencia")
    for m, sub, t in R["frec"]:
        print(f"   m={m}: subperíodo {pct(sub, 4) if sub else '-'} | TEA {pct(t, 3)}")
    print("== Sección 3 · TEA 9 %", {k: pct(v, 4) for k, v in R["eq"].items()})
    print("== Sección 4 · Fisher", [(pct(n, 0), pct(p, 0), pct(r), pct(a, 0)) for n, p, r, a in R["fisher"]])
    print("== Sección 5 · UF ficticia", {k: (fmt(v, 2) if v > 1 else pct(v)) for k, v in R["uf"].items()})
    e = R["ej"]
    print("== Ejemplo · el viaje")
    print("   TEA X", pct(e["tea_x"]), "| mensual Y", pct(e["men_y"], 4), "| TEA Y", pct(e["tea_y"]),
          "| mensual Z", pct(e["men_z"], 4), "| TEA Z", pct(e["tea_z"], 1))
    print("   pagos", {k: pesos(v) for k, v in e["pago"].items()}, "| intereses", {k: pesos(v) for k, v in e["interes"].items()},
          "| Y−X", pesos(e["dif_y_x"]), "| real X", pct(e["real_x"]), "| aprox", pct(e["aprox_x"]))
    print("== 2.1", {k: pct(v, 3) for k, v in R["e1"].items()})
    print("== 2.2", {k: pct(v, 4) for k, v in R["e2"].items()})
    print("== 2.3", {k: pct(v, 3) for k, v in R["e3"].items()})
    print("== 2.4", {k: pct(v, 3) for k, v in R["e4"].items()})
    print("== 2.5", {k: pct(v, 3) for k, v in R["e5"].items()})
    print("== 2.6", {k: pct(v, 3) for k, v in R["e6"].items()})
    print("== 2.7", {k: (pesos(v) if v > 1 else pct(v, 3)) for k, v in R["e7"].items()})
    print("== 2.8", {k: (pesos(v) if v > 1 else pct(v, 4)) for k, v in R["e8"].items()})
    print("== 2.9", {k: pct(v, 3) for k, v in R["e9"].items()})
    print("== 2.10", {k: (pesos(v) if v > 100 else fmt(v, 6)) for k, v in R["e10"].items()})
    print("   i_eq", pct(R["e10"]["i_eq"], 4), "| prom", pct(R["e10"]["prom_arit"], 4), "| TEA eq", pct(R["e10"]["tea_eq"], 3),
          "| real", pct(R["e10"]["real_anual"], 3), "| forward", pct(R["e10"]["forward"], 3), "| i2", pct(R["e10"]["i2"], 4))
    print("== Caso u2 · Valentina")
    print("   TEA A", pct(K["tea_a"], 4), "| mensual A", pct(K["mensual_a"], 4), "| TEA B", pct(K["tea_b"]),
          "| mensual B", pct(K["mensual_b"], 4), "| real A", pct(K["real_a"], 4), "| real B", pct(K["real_b"], 4),
          "| aprox A", pct(K["aprox_a"]), "| aprox B", pct(K["aprox_b"]))
    print("   VF A", pesos(K["vf_a"]), "| VF B", pesos(K["vf_b"]), "| dif", pesos(K["dif_vf"]),
          "| VF real", pesos(K["vf_real"]), "| ganancia real", pesos(K["gana_real"]), "| control", pesos(K["control_real"]))


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R, K):
    """Cadenas que el .md tiene que contener tal cual."""
    e = []
    for m, sub, t in R["frec"]:
        e.append(pct(t, 3))
    q = R["eq"]
    e += [pct(q["mensual"], 4), pct(q["trimestral"], 4), pct(q["semestral"], 4), pct(q["anual_desde_div"], 3)]
    for n, p, r, a in R["fisher"]:
        e.append(pct(r))
    u = R["uf"]
    e += [pesos(u["pesos_hoy"]), pesos(u["uf_fin"]), fmt(u["uf_recibe"], 0), pesos(u["pesos_fin"]), pct(u["nominal"])]
    j = R["ej"]
    e += [pct(j["tea_x"]), pct(j["men_y"], 4), pct(j["tea_y"]), pct(j["men_z"], 4)]
    e += [pesos(v) for v in j["pago"].values()] + [pesos(v) for v in j["interes"].values()]
    e += [pesos(j["dif_y_x"]), pct(j["real_x"]), pct(j["aprox_x"])]
    e += [pct(v, 3) for k, v in R["e1"].items() if k not in ("trim", "mens")]
    e += [pct(R["e1"][12] - R["e1"][4]), pct(R["e1"]["continua"] - R["e1"][365], 3)]
    x = R["e2"]
    e += [pct(x["mensual"], 4), pct(x["trimestral"], 4), pct(x["semestral"], 4), pct(x["dividir"], 4),
          pct(x["tea_desde_mensual"], 3), pct(x["por12"], 1)]
    e += [pct(R["e3"]["exacta"], 3), pct(R["e3"]["error"], 3)]
    e += [pct(R["e4"]["tea_a"]), pct(R["e4"]["men_b"], 4), pct(R["e4"]["men_a"], 4)]
    x = R["e5"]
    e += [pct(x["tea"]), pct(x["por12"], 1), pct(x["max_mensual"], 3), pct(x["max_si_nominal"], 3), pct(x["tea_si_nominal"])]
    x = R["e6"]
    e += [pct(x["uf_nominal"], 3), pct(x["pesos_real"], 3), pct(x["quiebre"], 3), pct(x["pesos_real_alta"], 3),
          pct(x["uf_nominal_alta"], 3)]
    x = R["e7"]
    e += [pct(x["tea_cont"], 3), pct(x["cont_equiv"], 3), pesos(x["vf_cont"]), pesos(x["vf_ef"]), pesos(x["dif"])]
    x = R["e8"]
    e += [pct(x["sem_ef"], 4), pesos(x["vf_nom"]), pesos(x["vf_ef"]), pesos(x["dif"]), pct(x["tea_nom"], 4)]
    x = R["e9"]
    e += [pct(x["quiebre"], 3), pct(x["uf_nominal_3"], 3), pct(x["uf_nominal_5"], 3), pct(x["pesos_real_3"], 3),
          pct(x["pesos_real_5"], 3)]
    x = R["e10"]
    e += [pct(x["i2"], 4), pct(x["i3"], 3), fmt(x["f1"], 5), fmt(x["f2"], 5), fmt(x["f3"], 5), pesos(x["s1"]),
          pesos(x["s2"]), pesos(x["vf"]), pct(x["i_eq"], 4), pct(x["tea_eq"], 3),
          pct(x["real_anual"], 3), pesos(x["vf_real"]), pct(x["forward"], 3)]
    e += [pct(K["tea_a"], 4), pct(K["mensual_a"]), pct(K["mensual_b"], 4), pct(K["real_a"], 2), pct(K["real_b"], 2),
          pct(K["aprox_a"]), pct(K["aprox_b"]), pesos(K["vf_a"]), pesos(K["vf_b"]), pesos(K["dif_vf"]),
          pesos(K["vf_real"]), pesos(K["gana_real"]), pesos(K["gana_nominal"])]
    return e


if __name__ == "__main__":
    R, K = resultados(), caso()
    imprimir(R, K)
    print("\nCASO:", "OK, las cifras de la unidad 2 calzan con caso_valentina.py (y el 0,55 % mensual de la unidad 1 es el banco A)"
          if K["calza"] else "NO calza con caso_valentina.py")
    if not K["calza"]:
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "02-tasas-de-interes.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R, K) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
