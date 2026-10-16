"""Unidad 1 · Valor del dinero en el tiempo.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto queda sin respaldo.

    py -3 -P u01_valor_del_dinero.py            # imprime los resultados
    py -3 -P u01_valor_del_dinero.py --revisar  # además los busca en el .md
"""
from math import log, sqrt
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


def vf(vp, i, n):
    return vp * (1 + i) ** n


def vp(vf_, i, n):
    return vf_ / (1 + i) ** n


def tasa(vp_, vf_, n):
    return (vf_ / vp_) ** (1 / n) - 1


def periodos(vp_, vf_, i):
    return log(vf_ / vp_) / log(1 + i)


def duplicar(i):
    return log(2) / log(1 + i)


def regla72(i):
    return 72 / (100 * i)


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

TABLA_SC = {"capital": 800_000, "i": 0.015, "meses": [1, 2, 3, 12, 24]}      # sección 4
TABLA_72 = [0.01, 0.06, 0.10, 0.20]                                          # sección 7, tasas anuales
EJEMPLO = {"contado": 9_800_000, "pie": 4_000_000, "saldo": 6_300_000, "mes_saldo": 10, "i": 0.009}
E1 = {"capital": 2_350_000, "i": 0.0065, "n": 30}
E2 = {"meta": 1_800_000, "i": 0.007, "n": 14}
E4 = {"contado": 489_990, "plazo": 530_000, "n": 4, "deposito": 0.006}
E5 = {"hoy": 5_200_000, "meta": 7_000_000, "i": 0.008}
E6 = {"tasas": [0.03, 0.08, 0.15, 0.36], "anios_duplica": 8}
E7 = {"ofertas": [(6_000_000, 0), (6_900_000, 18), (7_500_000, 30)], "i": 0.0075}
E8 = {"factura": 3_900_000, "adelanto": 3_720_000, "dias": 75, "credito": 0.011}
E9 = {"credito": 12_000_000, "i": 0.052, "n": 8, "n_largo": 20}
E10 = {"hoy": 1_350_000, "bono": 2_150_000, "mes_bono": 12, "meta": 4_300_000, "i": 0.006, "plazo_b": 24}


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    c, i = TABLA_SC["capital"], TABLA_SC["i"]
    R["tabla_sc"] = [(m, c * (1 + i * m), vf(c, i, m), vf(c, i, m) - c * (1 + i * m)) for m in TABLA_SC["meses"]]
    R["tabla_72"] = [(t, duplicar(t), regla72(t)) for t in TABLA_72]

    e = EJEMPLO
    f = (1 + e["i"]) ** e["mes_saldo"]
    vp_b = e["pie"] + e["saldo"] / f
    R["ej"] = {"factor": f, "vp_saldo": e["saldo"] / f, "vp_b": vp_b, "dif_vp": e["contado"] - vp_b,
               "vf_a": e["contado"] * f, "vf_pie": e["pie"] * f, "vf_b": e["pie"] * f + e["saldo"],
               "dif_vf": e["contado"] * f - (e["pie"] * f + e["saldo"]),
               "i_indif": tasa(e["contado"] - e["pie"], e["saldo"], e["mes_saldo"]),
               "gana_saldo": e["saldo"] - (e["contado"] - e["pie"])}

    R["e1"] = {"simple": E1["capital"] * (1 + E1["i"] * E1["n"]), "comp": vf(E1["capital"], E1["i"], E1["n"])}
    R["e1"]["anat"] = R["e1"]["comp"] - R["e1"]["simple"]
    R["e1"]["rent_s"] = R["e1"]["simple"] / E1["capital"] - 1
    R["e1"]["rent_c"] = R["e1"]["comp"] / E1["capital"] - 1

    R["e2"] = {"vp": vp(E2["meta"], E2["i"], E2["n"])}
    R["e2"]["interes"] = E2["meta"] - R["e2"]["vp"]

    R["e4"] = {"i": tasa(E4["contado"], E4["plazo"], E4["n"]), "recargo": E4["plazo"] - E4["contado"],
               "vf_dep": vf(E4["contado"], E4["deposito"], E4["n"])}

    n5 = periodos(E5["hoy"], E5["meta"], E5["i"])
    R["e5"] = {"n": n5, "mes37": vf(E5["hoy"], E5["i"], 37), "mes38": vf(E5["hoy"], E5["i"], 38),
               "dup": duplicar(E5["i"]), "r72": regla72(E5["i"])}

    R["e6"] = {"filas": [(t, duplicar(t), regla72(t), regla72(t) - duplicar(t)) for t in E6["tasas"]],
               "i_exacta": 2 ** (1 / E6["anios_duplica"]) - 1, "i_simple": 1 / E6["anios_duplica"],
               "i_r72": 72 / E6["anios_duplica"] / 100}

    i7 = E7["i"]
    R["e7"] = {"vp": [vp(m, i7, t) for m, t in E7["ofertas"]], "vf30": [vf(m, i7, 30 - t) for m, t in E7["ofertas"]],
               "i_1_3": tasa(6_000_000, 7_500_000, 30), "i_1_2": tasa(6_000_000, 6_900_000, 18),
               "i_2_3": tasa(6_900_000, 7_500_000, 12)}

    n8 = E8["dias"] / 30
    R["e8"] = {"n": n8, "i": tasa(E8["adelanto"], E8["factura"], n8), "costo": E8["factura"] - E8["adelanto"],
               "adelanto_justo": vp(E8["factura"], E8["credito"], n8)}

    fac8 = (1 + E9["i"]) ** E9["n"]
    fac20 = (1 + E9["i"]) ** E9["n_largo"]
    R["e9"] = {"deuda": E9["credito"] * fac8, "i_s": (fac8 - 1) / E9["n"], "i_s20": (fac20 - 1) / E9["n_largo"],
               "deuda_simple_misma": E9["credito"] * (1 + E9["i"] * E9["n"])}

    e = E10
    vp_bono = e["bono"] / (1 + e["i"]) ** e["mes_bono"]
    n10 = log(e["meta"] / (e["hoy"] + vp_bono)) / log(1 + e["i"])
    a, b, cc = e["hoy"], e["bono"], -e["meta"]
    x = (-b + sqrt(b * b - 4 * a * cc)) / (2 * a)          # x = (1+i)^12
    i_b = x ** (1 / 12) - 1
    R["e10"] = {"vp_bono": vp_bono, "vp_total": e["hoy"] + vp_bono, "n": n10,
                "saldo41": vf(e["hoy"], e["i"], 41) + vf(e["bono"], e["i"], 41 - 12),
                "saldo42": vf(e["hoy"], e["i"], 42) + vf(e["bono"], e["i"], 42 - 12),
                "x": x, "i_b": i_b,
                "control_b": vf(e["hoy"], i_b, 24) + vf(e["bono"], i_b, 12)}
    return R


def caso():
    spec = importlib.util.spec_from_file_location("caso", Path(__file__).with_name("caso_valentina.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    U1, C = m.U1, m.calcular()["u1"]
    a, i, n = U1["ahorro_hoy"], U1["tasa_mensual"], U1["meses"]
    propio = {"vf_compuesto": vf(a, i, n), "vf_simple": a * (1 + i * n)}
    calza = all(abs(propio[k] - C[k]) < 1e-6 for k in propio)
    return {"datos": U1, "vf_c": C["vf_compuesto"], "vf_s": C["vf_simple"], "dif": C["vf_compuesto"] - C["vf_simple"],
            "rent": C["vf_compuesto"] / a - 1, "anual": (1 + i) ** 12 - 1, "dup": duplicar(i), "r72": regla72(i),
            "int_simple_mes": a * i, "calza": calza}


def imprimir(R, K):
    print("== Sección 4 · simple contra compuesto ($800.000 al 1,5 %)")
    for m, s, c, d in R["tabla_sc"]:
        print(f"   mes {m:2}: simple {pesos(s)} | compuesto {pesos(c)} | diferencia {pesos(d)}")
    print("== Sección 7 · regla del 72")
    for t, ex, r in R["tabla_72"]:
        print(f"   {pct(t, 0)} %: exacto {fmt(ex, 1)} | regla {fmt(r, 1)}")
    e = R["ej"]
    print("== Ejemplo · el auto")
    for k, v in e.items():
        print(f"   {k}: {pesos(v) if abs(v) > 100 else fmt(v, 6)}")
    print("   i indiferencia:", pct(e["i_indif"], 3), "%")
    print("== 1.1", {k: (pesos(v) if v > 10 else pct(v)) for k, v in R["e1"].items()})
    print("== 1.2", {k: pesos(v) for k, v in R["e2"].items()})
    print("== 1.4 i", pct(R["e4"]["i"], 3), "| recargo", pesos(R["e4"]["recargo"]), "| depósito llega a", pesos(R["e4"]["vf_dep"]))
    print("== 1.5 n", fmt(R["e5"]["n"], 2), "| mes 37", pesos(R["e5"]["mes37"]), "| mes 38", pesos(R["e5"]["mes38"]),
          "| duplica", fmt(R["e5"]["dup"], 1), "| regla", fmt(R["e5"]["r72"], 1))
    print("== 1.6")
    for t, ex, r, d in R["e6"]["filas"]:
        print(f"   {pct(t, 0)} %: exacto {fmt(ex, 2)} | regla {fmt(r, 2)} | error {fmt(d, 2)}")
    print("   duplica en 8 años: exacta", pct(R["e6"]["i_exacta"]), "| simple", pct(R["e6"]["i_simple"], 1), "| regla", pct(R["e6"]["i_r72"]))
    print("== 1.7 VP", [pesos(v) for v in R["e7"]["vp"]], "| VF mes 30", [pesos(v) for v in R["e7"]["vf30"]],
          "| i 1→3", pct(R["e7"]["i_1_3"], 3), "| i 1→2", pct(R["e7"]["i_1_2"], 3), "| i 2→3", pct(R["e7"]["i_2_3"], 3))
    print("== 1.8 n", fmt(R["e8"]["n"], 1), "| i", pct(R["e8"]["i"], 3), "| costo", pesos(R["e8"]["costo"]),
          "| adelanto justo", pesos(R["e8"]["adelanto_justo"]))
    print("== 1.9 deuda", pesos(R["e9"]["deuda"]), "| i simple 8", pct(R["e9"]["i_s"], 3), "| i simple 20", pct(R["e9"]["i_s20"], 3),
          "| simple misma tasa", pesos(R["e9"]["deuda_simple_misma"]))
    e = R["e10"]
    print("== 1.10 vp bono", pesos(e["vp_bono"]), "| vp total", pesos(e["vp_total"]), "| n", fmt(e["n"], 2),
          "| mes 41", pesos(e["saldo41"]), "| mes 42", pesos(e["saldo42"]), "| x", fmt(e["x"], 5),
          "| i", pct(e["i_b"], 3), "| control", pesos(e["control_b"]))
    print("== Caso u1 · Valentina")
    print("   VF compuesto", pesos(K["vf_c"]), "| simple", pesos(K["vf_s"]), "| diferencia", pesos(K["dif"]),
          "| rentabilidad 36 meses", pct(K["rent"]), "| anual", pct(K["anual"]),
          "| duplica", fmt(K["dup"], 1), "| regla", fmt(K["r72"], 1), "| interés simple al mes", pesos(K["int_simple_mes"]))


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R, K):
    """Cadenas que el .md tiene que contener tal cual."""
    e = []
    for m, s, c, d in R["tabla_sc"]:
        e += [pesos(s), pesos(c), pesos(d)] if d > 0.5 else [pesos(s)]
    for t, ex, r in R["tabla_72"]:
        e += [fmt(ex, 1), fmt(r, 1)]
    j = R["ej"]
    e += [fmt(j["factor"], 5), pesos(j["vp_saldo"]), pesos(j["vp_b"]), pesos(j["dif_vp"]), pesos(j["vf_a"]),
          pesos(j["vf_pie"]), pesos(j["vf_b"]), pesos(j["dif_vf"]), pct(j["i_indif"], 3)]
    e += [pesos(R["e1"]["simple"]), pesos(R["e1"]["comp"]), pesos(R["e1"]["anat"]), pct(R["e1"]["rent_s"]), pct(R["e1"]["rent_c"])]
    e += [pesos(R["e2"]["vp"]), pesos(R["e2"]["interes"])]
    e += [pct(R["e4"]["i"], 3), pesos(R["e4"]["recargo"]), pesos(R["e4"]["vf_dep"])]
    e += [fmt(R["e5"]["n"], 2), pesos(R["e5"]["mes37"]), pesos(R["e5"]["mes38"]), fmt(R["e5"]["dup"], 1), fmt(R["e5"]["r72"], 1)]
    for t, ex, r, d in R["e6"]["filas"]:
        e += [fmt(ex, 2), fmt(r, 2)]
    e += [pct(R["e6"]["i_exacta"])]
    e += [pesos(v) for v in R["e7"]["vp"][1:]] + [pesos(v) for v in R["e7"]["vf30"][:2]]
    e += [pct(R["e7"]["i_1_3"], 3), pct(R["e7"]["i_1_2"], 3), pct(R["e7"]["i_2_3"], 3)]
    e += [pct(R["e8"]["i"], 3), pesos(R["e8"]["adelanto_justo"])]
    e += [pesos(R["e9"]["deuda"]), pct(R["e9"]["i_s"], 3), pct(R["e9"]["i_s20"], 3), pesos(R["e9"]["deuda_simple_misma"])]
    j = R["e10"]
    e += [pesos(j["vp_bono"]), pesos(j["vp_total"]), fmt(j["n"], 2), pesos(j["saldo41"]), pesos(j["saldo42"]),
          fmt(j["x"], 5), pct(j["i_b"], 3)]
    e += [pesos(K["vf_c"]), pesos(K["vf_s"]), pesos(K["dif"]), pct(K["rent"]), pct(K["anual"]), fmt(K["dup"], 1),
          fmt(K["r72"], 1), pesos(K["int_simple_mes"])]
    return e


if __name__ == "__main__":
    R, K = resultados(), caso()
    imprimir(R, K)
    print("\nCASO:", "OK, las cifras de la unidad 1 calzan con caso_valentina.py" if K["calza"] else "NO calza con caso_valentina.py")
    if not K["calza"]:
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "01-valor-del-dinero.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R, K) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
