"""Unidad 6 · Estructura de tasas.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md. El caso integrador se importa de
caso_valentina.py y se compara.

    py -3 -P u06_estructura_de_tasas.py            # imprime los resultados
    py -3 -P u06_estructura_de_tasas.py --revisar  # además los busca en el .md
"""
from pathlib import Path
import importlib.util, sys

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=2):
    return fmt(100 * x, dec) + " %"


def clp(x):
    return ("−" if x < 0 else "") + "$" + fmt(abs(x), 0)


def spot_de_cero(precio, t, nominal=100):
    return (nominal / precio) ** (1 / t) - 1


def forward(s, a, b):
    """Tasa forward anual entre los años a y b (a < b), desde spots s[0] = s_1, s[1] = s_2, ..."""
    num = (1 + s[b - 1]) ** b
    den = (1 + s[a - 1]) ** a if a > 0 else 1
    return (num / den) ** (1 / (b - a)) - 1


def bootstrapping(bonos, nominal=100):
    """bonos: lista ordenada por plazo 1, 2, ... de (cupón en $ por 100, precio). Devuelve spots."""
    s = []
    for t, (c, p) in enumerate(bonos, start=1):
        vp_cupones = sum(c / (1 + s[k]) ** (k + 1) for k in range(t - 1))
        s.append(((nominal + c) / (p - vp_cupones)) ** (1 / t) - 1)
    return s


def precio_con_curva(flujos, s):
    return sum(f / (1 + s[t - 1]) ** t for t, f in enumerate(flujos, start=1))


def ytm(precio, flujos):
    lo, hi = -0.5, 1.0
    g = lambda y: sum(f / (1 + y) ** t for t, f in enumerate(flujos, start=1)) - precio
    for _ in range(300):
        m = (lo + hi) / 2
        if g(lo) * g(m) <= 0:
            hi = m
        else:
            lo = m
    return (lo + hi) / 2


# ---------------------------------------------------------------- datos (originales de esta base)

# Ejemplo resuelto · Tomás y la matrícula de su hermano (por cada 100 de nominal)
EJ = {"cero_1": 95.85, "bono_2": (5.0, 100.21), "monto": 10_000_000, "deposito_banco": 0.047}
# 6.1 · ceros de la Tesorería ficticia, plazos 1 a 3
E1 = {"precios": [96.30, 92.10, 87.60], "pagare": 5_000_000}
# 6.2 · spots dadas
E2 = [0.036, 0.041, 0.045]
# 6.4 · bono a 3 años, cupón 7 % anual, con la curva de 6.2
E4 = {"cupon": 7.0, "plazo": 3}
# 6.5 · bonos con cupón anual (cupón por 100, precio)
E5 = [(5.0, 100.48), (5.5, 100.62), (6.0, 100.85)]
# 6.6 · tesorera de una cooperativa: recibe un monto en un año y lo quiere colocar un año
E6 = {"s": [0.042, 0.049], "oferta_banco": 0.053, "monto": 40_000_000}
# 6.7 · spots y premio por liquidez de 0,2 puntos por cada año de plazo sobre el primero
E7 = {"s": [0.044, 0.0475, 0.0495, 0.0505], "premio_por_anio": 0.002}
# 6.9 · tres bonos para la curva y un cuarto bono para revisar
E9 = {"bonos": [(4.0, 99.61), (5.0, 100.10), (5.5, 100.05)], "D": (8.0, 107.90)}
# 6.10 · pie del departamento: tres años, tres estrategias
E10 = {"s": [0.046, 0.050, 0.053], "monto": 12_000_000, "realizadas": [0.050, 0.052]}


def caso():
    spec = importlib.util.spec_from_file_location("caso", Path(__file__).with_name("caso_valentina.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # ejemplo
    s1 = spot_de_cero(EJ["cero_1"], 1)
    s = bootstrapping([(0.0, EJ["cero_1"]), EJ["bono_2"]])
    assert abs(s[0] - s1) < 1e-12
    c, p = EJ["bono_2"]
    vp_cup1 = c / (1 + s1)
    f12 = forward(s, 1, 2)
    R["ej"] = {"s1": s1, "s2": s[1], "vp_cup1": vp_cup1, "resto": p - vp_cup1, "f12": f12,
               "vf_curva": EJ["monto"] * (1 + s[1]) ** 2, "vf_banco": EJ["monto"] * (1 + EJ["deposito_banco"]) ** 2,
               "vf_1": EJ["monto"] * (1 + s1), "ytm_bono": ytm(p, [c, 100 + c]),
               "precio_cero_2": 100 / (1 + s[1]) ** 2}
    R["ej"]["dif"] = R["ej"]["vf_curva"] - R["ej"]["vf_banco"]
    # 6.1
    sp1 = [spot_de_cero(pp, t) for t, pp in enumerate(E1["precios"], start=1)]
    R["e1"] = {"s": sp1, "pagare": E1["pagare"] * E1["precios"][2] / 100}
    # 6.2
    R["e2"] = {"f12": forward(E2, 1, 2), "f23": forward(E2, 2, 3), "f13": forward(E2, 1, 3)}
    # 6.4
    fl = [E4["cupon"]] * (E4["plazo"] - 1) + [100 + E4["cupon"]]
    P4 = precio_con_curva(fl, E2)
    R["e4"] = {"precio": P4, "ytm": ytm(P4, fl), "precio_s3": precio_con_curva(fl, [E2[2]] * 3),
               "vp": [f / (1 + E2[t - 1]) ** t for t, f in enumerate(fl, start=1)]}
    # 6.5
    s5 = bootstrapping(E5)
    R["e5"] = {"s": s5, "f12": forward(s5, 1, 2), "f23": forward(s5, 2, 3)}
    # 6.6
    f6 = forward(E6["s"], 1, 2)
    m = E6["monto"]
    pedir_hoy = m / (1 + E6["s"][0])
    R["e6"] = {"f": f6, "pedir_hoy": pedir_hoy, "al_final": pedir_hoy * (1 + E6["s"][1]) ** 2,
               "con_banco": m * (1 + E6["oferta_banco"]), "ganancia": pedir_hoy * (1 + E6["s"][1]) ** 2 - m * (1 + E6["oferta_banco"])}
    # 6.7
    s7 = E7["s"]
    f7 = [s7[0]] + [forward(s7, t, t + 1) for t in range(1, len(s7))]
    R["e7"] = {"f": f7, "esperadas": [f - E7["premio_por_anio"] * t for t, f in enumerate(f7)]}
    # 6.9
    s9 = bootstrapping(E9["bonos"])
    cD, pD = E9["D"]
    flD = [cD, cD, 100 + cD]
    teorico = precio_con_curva(flD, s9)
    (cA, pA), (cB, pB), (cC, pC) = E9["bonos"]
    nC = flD[2] / (100 + cC)
    nB = (flD[1] - nC * cC) / (100 + cB)
    nA = (flD[0] - nC * cC - nB * cB) / (100 + cA)
    costo = nA * pA + nB * pB + nC * pC
    R["e9"] = {"s": s9, "teorico": teorico, "nA": nA, "nB": nB, "nC": nC, "costo": costo,
               "ganancia": pD - costo, "ytm_D": ytm(pD, flD), "ytm_D_teorico": ytm(teorico, flD)}
    assert abs(costo - teorico) < 1e-9
    # 6.10
    s10, M = E10["s"], E10["monto"]
    f12, f23 = forward(s10, 1, 2), forward(s10, 2, 3)
    a, b = E10["realizadas"]
    R["e10"] = {"f12": f12, "f23": f23, "A": M * (1 + s10[2]) ** 3,
                "B_esperada_forward": M * (1 + s10[0]) * (1 + f12) * (1 + f23),
                "B_real": M * (1 + s10[0]) * (1 + a) * (1 + b),
                "C_real": M * (1 + s10[1]) ** 2 * (1 + b),
                "f13": forward(s10, 1, 3)}
    # breakeven del año 3 para la estrategia B, dado que el año 2 salió a
    R["e10"]["equilibrio_3"] = (1 + s10[2]) ** 3 / ((1 + s10[0]) * (1 + a)) - 1

    # caso
    mc = caso()
    C = mc.calcular()
    sp = [spot_de_cero(pp, t) for t, pp in enumerate(mc.U6["precios_cero"], start=1)]
    fw = [forward(sp, t, t + 1) for t in range(1, len(sp))]
    assert all(abs(x - y) < 1e-12 for x, y in zip(sp, C["u6"]["spot"]))
    assert all(abs(x - y) < 1e-12 for x, y in zip(fw, C["u6"]["forward_1_anio"]))
    assert abs(C["u11"]["rf"] - sp[0]) < 1e-12
    R["caso"] = {"precios": mc.U6["precios_cero"], "s": sp, "f": fw, "rf": C["u11"]["rf"],
                 "precio_bono": C["u7"]["precio"], "ytm_bono": C["u7"]["ytm"], "cupon": mc.U7["cupon"],
                 "f_media": ((1 + sp[0]) * (1 + fw[0]) * (1 + fw[1])) ** (1 / 3) - 1,
                 "cuanto_hoy_1M_en_5": 1_000_000 * mc.U6["precios_cero"][4] / 100,
                 "saldo_con_cero": mc.U5["saldo_maquina"] * mc.U6["precios_cero"][mc.U5["anio_saldo"] - 1] / 100,
                 "saldo_al_12": C["u5"]["vp_saldo"]}
    return R


def imprimir(R):
    e = R["ej"]
    print("== Ejemplo · s1", pct(e["s1"]), "VP cupón 1", fmt(e["vp_cup1"], 4), "resto", fmt(e["resto"], 4), "s2", pct(e["s2"]),
          "f12", pct(e["f12"]), "YTM bono", pct(e["ytm_bono"]), "precio cero 2", fmt(e["precio_cero_2"], 2))
    print("   VF curva", clp(e["vf_curva"]), "VF banco", clp(e["vf_banco"]), "diferencia", clp(e["dif"]), "VF 1 año", clp(e["vf_1"]))
    print("== 6.1", [pct(x) for x in R["e1"]["s"]], "pagaré", clp(R["e1"]["pagare"]))
    print("== 6.2", {k: pct(v) for k, v in R["e2"].items()})
    e = R["e4"]; print("== 6.4 precio", fmt(e["precio"], 2), "YTM", pct(e["ytm"]), "precio a s3 plana", fmt(e["precio_s3"], 2), [fmt(x, 2) for x in e["vp"]])
    e = R["e5"]; print("== 6.5", [pct(x) for x in e["s"]], "f12", pct(e["f12"]), "f23", pct(e["f23"]))
    e = R["e6"]; print("== 6.6 f", pct(e["f"], 3), "pedir hoy", clp(e["pedir_hoy"]), "al final", clp(e["al_final"]), "banco", clp(e["con_banco"]), "ganancia", clp(e["ganancia"]))
    e = R["e7"]; print("== 6.7 f", [pct(x) for x in e["f"]], "esperadas", [pct(x) for x in e["esperadas"]])
    e = R["e9"]; print("== 6.9 s", [pct(x) for x in e["s"]], "teórico", fmt(e["teorico"], 2), "n", fmt(e["nA"], 4), fmt(e["nB"], 4), fmt(e["nC"], 4),
                       "costo", fmt(e["costo"], 2), "ganancia", fmt(e["ganancia"], 2), "YTM D", pct(e["ytm_D"]), "YTM teórica", pct(e["ytm_D_teorico"]))
    e = R["e10"]; print("== 6.10 f12", pct(e["f12"]), "f23", pct(e["f23"]), "f13", pct(e["f13"]), "A", clp(e["A"]), "B forward", clp(e["B_esperada_forward"]),
                        "B real", clp(e["B_real"]), "C real", clp(e["C_real"]), "equilibrio año 3", pct(e["equilibrio_3"]))
    c = R["caso"]; print("== Caso u6 precios", c["precios"], "spot", [pct(x) for x in c["s"]], "forward", [pct(x) for x in c["f"]],
                         "rf", pct(c["rf"]), "bono U7", fmt(c["precio_bono"], 2), "YTM", pct(c["ytm_bono"]), "media 3", pct(c["f_media"]),
                         "1M en 5 años hoy", clp(c["cuanto_hoy_1M_en_5"]), "saldo con cero", clp(c["saldo_con_cero"]), "al 12", clp(c["saldo_al_12"]))


def esperados(R):
    x = []
    e = R["ej"]
    x += [pct(e["s1"]), pct(e["s2"]), pct(e["f12"]), fmt(e["vp_cup1"], 4), fmt(e["resto"], 4), clp(e["vf_curva"]),
          clp(e["vf_banco"]), clp(e["dif"]), clp(e["vf_1"]), pct(e["ytm_bono"]), fmt(e["precio_cero_2"], 2)]
    x += [pct(v) for v in R["e1"]["s"]] + [clp(R["e1"]["pagare"])]
    x += [pct(v) for v in R["e2"].values()]
    e = R["e4"]; x += [fmt(e["precio"], 2), pct(e["ytm"]), fmt(e["precio_s3"], 2)] + [fmt(v, 2) for v in e["vp"]]
    e = R["e5"]; x += [pct(v) for v in e["s"]] + [pct(e["f12"]), pct(e["f23"])]
    e = R["e6"]; x += [pct(e["f"], 3), clp(e["pedir_hoy"]), clp(e["al_final"]), clp(e["con_banco"]), clp(e["ganancia"])]
    e = R["e7"]; x += [pct(v) for v in e["f"]] + [pct(v) for v in e["esperadas"]]
    e = R["e9"]; x += [pct(v) for v in e["s"]] + [fmt(e["teorico"], 2), fmt(e["nA"], 4), fmt(e["nB"], 4), fmt(e["nC"], 4),
                                                    fmt(e["ganancia"], 2), pct(e["ytm_D"]), pct(e["ytm_D_teorico"])]
    e = R["e10"]; x += [pct(e["f12"]), pct(e["f23"]), clp(e["A"]), clp(e["B_esperada_forward"]), clp(e["B_real"]),
                        clp(e["C_real"]), pct(e["equilibrio_3"])]
    c = R["caso"]; x += [pct(v) for v in c["s"]] + [pct(v) for v in c["f"]] + [fmt(c["precio_bono"], 2), pct(c["ytm_bono"]),
                                                                              clp(c["saldo_con_cero"]), clp(c["saldo_al_12"]), pct(c["rf"])]
    return x


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    print("\nCADENA: OK, spot y forward calzan con caso_valentina.py; la spot a 1 año es la rf de la unidad 11")
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "06-estructura-de-tasas.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [s for s in esperados(R) if s not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
