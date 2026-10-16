"""Unidad 5 · VAN, TIR y criterios de inversión.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md. El caso integrador se importa de
caso_valentina.py y se compara: si el caso cambia, este script lo nota.

    py -3 -P u05_van_tir.py            # imprime los resultados
    py -3 -P u05_van_tir.py --revisar  # además los busca en el .md
"""
from itertools import combinations
from pathlib import Path
import importlib.util, sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=2):
    return fmt(100 * x, dec) + " %"


def clp(x):
    return ("−" if x < 0 else "") + "$" + fmt(abs(x), 0)


def van(r, f):
    return sum(v / (1 + r) ** t for t, v in enumerate(f))


def tir(f, lo=-0.99, hi=5.0):
    """Bisección en un intervalo donde el VAN cambia de signo."""
    for _ in range(300):
        m = (lo + hi) / 2
        if van(lo, f) * van(m, f) <= 0:
            hi = m
        else:
            lo = m
    return (lo + hi) / 2


def raices(f):
    """Todas las raíces del polinomio en x = 1/(1+r); devuelve (reales con r > −1, complejas)."""
    xs = np.roots(f[::-1])
    reales = sorted(1 / x.real - 1 for x in xs if abs(x.imag) < 1e-9 and x.real > 0)
    return reales, [x for x in xs if abs(x.imag) >= 1e-9]


def cambios_de_signo(f):
    s = [v for v in f if v != 0]
    return sum(1 for a, b in zip(s, s[1:]) if a * b < 0)


def tirm(f, r_fin, r_rein=None):
    """TIR modificada: egresos a VP con r_fin, ingresos a VF con r_rein."""
    r_rein = r_fin if r_rein is None else r_rein
    n = len(f) - 1
    vp_neg = sum(-v / (1 + r_fin) ** t for t, v in enumerate(f) if v < 0)
    vf_pos = sum(v * (1 + r_rein) ** (n - t) for t, v in enumerate(f) if v > 0)
    return (vf_pos / vp_neg) ** (1 / n) - 1, vp_neg, vf_pos


def recuperacion(f, r=0.0):
    """Período de recuperación (simple si r = 0, descontado si r > 0).
    Toma la ÚLTIMA vez que el acumulado pasa de negativo a positivo y no vuelve a bajar.
    Devuelve (años o None, acumulados, flujos descontados)."""
    d = [v / (1 + r) ** t for t, v in enumerate(f)]
    cum, a = [], 0
    for v in d:
        a += v
        cum.append(a)
    if cum[-1] < 0:
        return None, cum, d
    for t in range(len(d) - 1, 0, -1):
        if cum[t - 1] < 0 <= cum[t]:
            return (t - 1) + (-cum[t - 1]) / d[t], cum, d
    return 0.0, cum, d


def interpolar(f, r1, r2):
    v1, v2 = van(r1, f), van(r2, f)
    return r1 + (r2 - r1) * v1 / (v1 - v2), v1, v2


def fa(r, n):
    """Factor de valor presente de una anualidad vencida."""
    return (1 - (1 + r) ** -n) / r


# ---------------------------------------------------------------- datos (originales de esta base)

# Ejemplo resuelto · Javiera y el furgón para fletes de fin de semana
EJ = {"flujos": [-9_800_000, 2_900_000, 3_100_000, 3_100_000, 2_700_000], "venta": 3_600_000, "r": 0.11}

# 5.1 · Martina y la máquina de bordado
E1 = {"flujos": [-3_150_000, 1_050_000, 1_200_000, 1_200_000, 900_000], "r": 0.10}
# 5.2 · paneles solares contra termo solar (ahorro anual en la cuenta)
E2 = {"paneles": (4_680_000, 720_000, 12), "termo": (1_900_000, 380_000, 6), "r": 0.07}
# 5.4 · racionamiento de capital (inversión, VAN)
E4 = {"presupuesto": 21_500_000,
      "proyectos": {"A": (12_600_000, 3_520_000), "B": (8_900_000, 2_580_000),
                    "C": (6_400_000, 2_250_000), "D": (5_700_000, 1_180_000)}}
# 5.5 · local del primer piso: remodelación chica o grande (5 años)
E5 = {"chica": (6_000_000, 1_900_000), "grande": (18_000_000, 5_300_000), "n": 5, "r": 0.09}
# 5.6 · panadería que agrega pizzas por la tarde (4 años, sin impuestos)
E6 = {"horno": 5_200_000, "estudio": 400_000, "arriendo_mes": 150_000, "ventas": 7_200_000,
      "costos": 3_600_000, "canibal": 600_000, "capital_trabajo": 500_000, "residual": 600_000,
      "n": 4, "r": 0.10, "tasa_credito": 0.08}
# 5.7 · máquina expendedora en la universidad (flujos en pesos de hoy)
E7 = {"inversion": 3_500_000, "flujo_real": 1_100_000, "n": 4, "inflacion": 0.038, "r_nominal": 0.11}
# 5.8 · comente: proyecto de TIR alta
E8 = {"flujos": [-10_000_000, 6_500_000, 5_500_000, 4_000_000], "r": 0.10}
# 5.9 · extracción de áridos con restauración del terreno
E9 = {"a": [-20_000_000, 47_000_000, -27_300_000], "b": [-20_000_000, 47_000_000, -28_000_000], "r": 0.12}
# 5.10 · lavandería: dos lavadoras industriales de distinta vida (inversión, costo anual, vida)
E10 = {"A": (7_000_000, 1_200_000, 3), "B": (11_500_000, 900_000, 5), "r": 0.10}


def caso():
    spec = importlib.util.spec_from_file_location("caso", Path(__file__).with_name("caso_valentina.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # ejemplo
    f = list(EJ["flujos"])
    f[-1] += EJ["venta"]
    r = EJ["r"]
    t_ej = tir(f)
    R["ej"] = {"f": f, "van": van(r, f), "vp_entradas": van(r, f) - f[0], "tir": t_ej,
               "interp": interpolar(f, 0.18, 0.19), "v15": van(0.15, f), "v20": van(0.20, f),
               "pay": recuperacion(f), "payd": recuperacion(f, r), "tirm": tirm(f, r),
               "ivan": van(r, f) / -f[0], "descontados": [v / (1 + r) ** t for t, v in enumerate(f)]}
    # 5.1
    f1 = E1["flujos"]
    R["e1"] = {"van": van(E1["r"], f1), "tir": tir(f1), "interp": interpolar(f1, 0.14, 0.15),
               "desc": [v / (1 + E1["r"]) ** t for t, v in enumerate(f1)]}
    # 5.2
    R["e2"] = {}
    for k in ("paneles", "termo"):
        I, a, n = E2[k]
        fl = [-I] + [a] * n
        R["e2"][k] = {"van": van(E2["r"], fl), "pay": recuperacion(fl)[0], "payd": recuperacion(fl, E2["r"])[0],
                      "tir": tir(fl), "vp_ahorro": a * fa(E2["r"], n),
                      "factor_vf": ((1 + E2["r"]) ** n - 1) / E2["r"],          # ojo con el −1
                      "vf_ahorro": a * ((1 + E2["r"]) ** n - 1) / E2["r"],
                      "vf_por_vp": a * fa(E2["r"], n) * (1 + E2["r"]) ** n,
                      "tirm": tirm(fl, E2["r"])[0]}
        assert abs(R["e2"][k]["vf_ahorro"] - R["e2"][k]["vf_por_vp"]) < 1e-6
    # 5.4
    P = E4["proyectos"]
    ivan = {k: v / i for k, (i, v) in P.items()}
    orden = sorted(P, key=lambda k: -ivan[k])
    usado, elegidos = 0, []
    for k in orden:
        if usado + P[k][0] <= E4["presupuesto"]:
            elegidos.append(k)
            usado += P[k][0]
    combos = []
    for n in range(1, 5):
        for c in combinations(sorted(P), n):
            inv = sum(P[k][0] for k in c)
            if inv <= E4["presupuesto"]:
                combos.append((sum(P[k][1] for k in c), c, inv))
    combos.sort(reverse=True)
    R["e4"] = {"ivan": ivan, "orden": orden, "codicioso": (elegidos, usado, sum(P[k][1] for k in elegidos)),
               "optimo": combos[0], "combos": combos}
    # 5.5
    n, r5 = E5["n"], E5["r"]
    fc = [-E5["chica"][0]] + [E5["chica"][1]] * n
    fg = [-E5["grande"][0]] + [E5["grande"][1]] * n
    fi = [g - c for c, g in zip(fc, fg)]
    R["e5"] = {"van_c": van(r5, fc), "tir_c": tir(fc), "van_g": van(r5, fg), "tir_g": tir(fg),
               "van_i": van(r5, fi), "tir_i": tir(fi), "fa": fa(r5, n), "van_c_15": van(0.15, fc), "van_g_15": van(0.15, fg)}
    # 5.6
    e = E6
    oport = 12 * e["arriendo_mes"]
    anual = e["ventas"] - e["costos"] - e["canibal"] - oport
    fl6 = [-(e["horno"] + e["capital_trabajo"])] + [anual] * e["n"]
    fl6[-1] += e["residual"] + e["capital_trabajo"]
    sin_op = [fl6[0]] + [v + oport for v in fl6[1:]]
    R["e6"] = {"oport": oport, "anual": anual, "f": fl6, "van": van(e["r"], fl6), "van_sin_oport": van(e["r"], sin_op),
               "fa": fa(e["r"], e["n"]), "vp_final": (e["residual"] + e["capital_trabajo"]) / (1 + e["r"]) ** e["n"],
               "con_estudio": van(e["r"], fl6) - e["estudio"], "tir": tir(fl6), "tir_sin": tir(sin_op)}
    # 5.7
    e = E7
    rr = (1 + e["r_nominal"]) / (1 + e["inflacion"]) - 1
    real = [-e["inversion"]] + [e["flujo_real"]] * e["n"]
    nom = [real[0]] + [e["flujo_real"] * (1 + e["inflacion"]) ** t for t in range(1, e["n"] + 1)]
    R["e7"] = {"rr": rr, "van_real": van(rr, real), "van_nom": van(e["r_nominal"], nom), "nom": nom,
               "mal": van(e["r_nominal"], real), "fisher_aprox": e["r_nominal"] - e["inflacion"]}
    # 5.8
    f8 = E8["flujos"]
    tm8 = tirm(f8, E8["r"])
    t8 = tir(f8)
    R["e8"] = {"tir": t8, "tirm": tm8, "van": van(E8["r"], f8),
               "vf_a_tir": -f8[0] * (1 + t8) ** 3, "vf_10": tm8[2]}
    # 5.9
    ra, _ = raices(E9["a"])
    rb, cb = raices(E9["b"])
    R["e9"] = {"tir_a": ra, "tir_b": rb, "van_a": van(E9["r"], E9["a"]), "van_b": van(E9["r"], E9["b"]),
               "tirm_a": tirm(E9["a"], E9["r"]), "tirm_b": tirm(E9["b"], E9["r"]),
               "van_a_max": max(van(x / 1000, E9["a"]) for x in range(0, 400)),
               "r_max": max(range(0, 400), key=lambda x: van(x / 1000, E9["a"])) / 1000,
               "van_b_0": van(0, E9["b"]), "cambios": cambios_de_signo(E9["a"])}
    # 5.10
    r10 = E10["r"]
    R["e10"] = {}
    for k in ("A", "B"):
        I, c, n = E10[k]
        vac = I + c * fa(r10, n)
        aeq = vac / fa(r10, n)
        R["e10"][k] = {"vac": vac, "aeq": aeq, "vac_inf": aeq / r10, "fa": fa(r10, n)}
    # vac a 15 años (período común): A se compra 5 veces, B 3 veces
    def vac_comun(I, c, n, H=15):
        return sum(I / (1 + r10) ** (n * j) for j in range(H // n)) + c * fa(r10, H)
    R["e10"]["comun"] = {k: vac_comun(*E10[k]) for k in ("A", "B")}

    # caso integrador
    m = caso()
    U5 = m.U5
    C5 = m.calcular()["u5"]
    fc5 = C5["flujos"]
    rc = U5["tasa"]
    reales, complejas = raices(fc5)
    vp_saldo = U5["saldo_maquina"] / (1 + rc) ** U5["anio_saldo"]
    vp_inv = U5["pie_maquina"] + vp_saldo
    R["caso"] = {"f": fc5, "van": C5["van"], "tir": C5["tir"], "vp_saldo": C5["vp_saldo"],
                 "cambios": cambios_de_signo(fc5), "reales": reales, "n_complejas": len(complejas),
                 "pay": recuperacion(fc5), "payd": recuperacion(fc5, rc), "tirm": tirm(fc5, rc),
                 "vp_inv": vp_inv, "ivan": C5["van"] / vp_inv, "ivan_pie": C5["van"] / U5["pie_maquina"],
                 "desc": [v / (1 + rc) ** t for t, v in enumerate(fc5)],
                 "curva": {x: van(x, fc5) for x in (0.0, 0.12, 0.20, 0.30, 0.40, 0.50, 1.00)},
                 "interp": interpolar(fc5, 0.41, 0.42),
                 "vp_operacion": C5["van"] + vp_inv}
    # saldo del proyecto a la TIR: lo que el proyecto le «debe» al dueño al cierre de cada año
    saldos, b = [], 0.0
    for t, v in enumerate(fc5):
        b = b * (1 + C5["tir"]) + v if t else v
        saldos.append(b)
    R["caso"]["saldos"] = saldos
    # la curva del VAN baja en todo el tramo de −95 % a 1.900 %: una sola cruce con el eje
    grilla = [-0.95 + k * 0.001 for k in range(20_000)]
    R["caso"]["monotona"] = all(van(a, fc5) > van(b2, fc5) for a, b2 in zip(grilla, grilla[1:]))
    assert R["caso"]["monotona"] and all(s < 0 for s in saldos[:-1])
    # el caso debe coincidir con lo que recalcula esta unidad
    assert abs(van(rc, fc5) - C5["van"]) < 1e-6
    assert len(reales) == 1 and abs(reales[0] - C5["tir"]) < 1e-6
    assert abs(vp_saldo - C5["vp_saldo"]) < 1e-6
    return R


def imprimir(R):
    e = R["ej"]
    print("== Ejemplo · furgón", e["f"])
    print("   descontados", [clp(x) for x in e["descontados"]])
    print("   VP entradas", clp(e["vp_entradas"]), "VAN", clp(e["van"]), "VAN15", clp(e["v15"]), "VAN20", clp(e["v20"]))
    print("   TIR", pct(e["tir"]), "interp 18-19", pct(e["interp"][0]), clp(e["interp"][1]), clp(e["interp"][2]))
    print("   recuperación simple", fmt(e["pay"][0], 2), [clp(x) for x in e["pay"][1]])
    print("   recuperación desc.", fmt(e["payd"][0], 2), [clp(x) for x in e["payd"][1]])
    print("   TIRM", pct(e["tirm"][0]), "VP egresos", clp(e["tirm"][1]), "VF ingresos", clp(e["tirm"][2]), "IVAN", fmt(e["ivan"], 3))
    e = R["e1"]; print("== 5.1 VAN", clp(e["van"]), "TIR", pct(e["tir"]), "interp", pct(e["interp"][0]), clp(e["interp"][1]), clp(e["interp"][2]),
                       [clp(x) for x in e["desc"]])
    for k, v in R["e2"].items():
        print(f"== 5.2 {k}: VAN {clp(v['van'])} VP ahorro {clp(v['vp_ahorro'])} recup {fmt(v['pay'], 2)} "
              f"desc {fmt(v['payd'], 2) if v['payd'] else 'no se recupera'} TIR {pct(v['tir'])} "
              f"factor VF {fmt(v['factor_vf'], 4)} VF {clp(v['vf_ahorro'])} TIRM {pct(v['tirm'])}")
    e = R["e4"]; print("== 5.4 IVAN", {k: fmt(v, 3) for k, v in e["ivan"].items()}, "orden", e["orden"])
    print("   codicioso", e["codicioso"][0], clp(e["codicioso"][1]), clp(e["codicioso"][2]), "| óptimo", e["optimo"][1], clp(e["optimo"][0]), clp(e["optimo"][2]))
    for c in e["combos"][:6]:
        print("     ", c[1], clp(c[0]), clp(c[2]))
    e = R["e5"]; print("== 5.5 chica VAN", clp(e["van_c"]), "TIR", pct(e["tir_c"]), "| grande VAN", clp(e["van_g"]), "TIR", pct(e["tir_g"]),
                       "| incremental VAN", clp(e["van_i"]), "TIR", pct(e["tir_i"]), "fa", fmt(e["fa"], 4),
                       "| al 15 %", clp(e["van_c_15"]), clp(e["van_g_15"]))
    e = R["e6"]; print("== 5.6 oport", clp(e["oport"]), "anual", clp(e["anual"]), "flujos", e["f"], "fa", fmt(e["fa"], 4),
                       "VP final", clp(e["vp_final"]), "VAN", clp(e["van"]), "sin oport", clp(e["van_sin_oport"]),
                       "restando estudio (mal)", clp(e["con_estudio"]), "TIR", pct(e["tir"]), "TIR sin oport", pct(e["tir_sin"]))
    e = R["e7"]; print("== 5.7 real", pct(e["rr"], 3), "aprox", pct(e["fisher_aprox"]), "VAN real", clp(e["van_real"]), "VAN nom", clp(e["van_nom"]),
                       "nominales", [clp(x) for x in e["nom"]], "mal", clp(e["mal"]))
    e = R["e8"]; print("== 5.8 TIR", pct(e["tir"]), "TIRM", pct(e["tirm"][0]), "VF a 10 %", clp(e["vf_10"]), "VF a la TIR", clp(e["vf_a_tir"]), "VAN", clp(e["van"]))
    e = R["e9"]; print("== 5.9 TIR a", [pct(x) for x in e["tir_a"]], "TIR b", e["tir_b"], "VAN a", clp(e["van_a"]), "VAN b", clp(e["van_b"]),
                       "TIRM a", pct(e["tirm_a"][0]), "TIRM b", pct(e["tirm_b"][0]), "máx", clp(e["van_a_max"]), "en", e["r_max"], "VAN b(0)", clp(e["van_b_0"]))
    for k in ("A", "B"):
        v = R["e10"][k]; print(f"== 5.10 {k}: VAC {clp(v['vac'])} Aeq {clp(v['aeq'])} VAC∞ {clp(v['vac_inf'])} fa {fmt(v['fa'], 4)}")
    print("   período común 15 años", {k: clp(v) for k, v in R["e10"]["comun"].items()})
    c = R["caso"]
    print("== Caso u5 flujos", c["f"], "cambios", c["cambios"], "TIR reales", c["reales"], "complejas", c["n_complejas"])
    print("   descontados", [clp(x) for x in c["desc"]])
    print("   VAN", clp(c["van"]), "TIR", pct(c["tir"]), "interp 41-42", pct(c["interp"][0]), clp(c["interp"][1]), clp(c["interp"][2]))
    print("   curva", {k: clp(v) for k, v in c["curva"].items()})
    print("   recup simple", fmt(c["pay"][0], 2), [clp(x) for x in c["pay"][1]])
    print("   recup desc", fmt(c["payd"][0], 2), [clp(x) for x in c["payd"][1]])
    print("   TIRM", pct(c["tirm"][0]), clp(c["tirm"][1]), clp(c["tirm"][2]), "VP saldo", clp(c["vp_saldo"]),
          "VP inversión", clp(c["vp_inv"]), "IVAN", fmt(c["ivan"], 2), "sobre el pie", fmt(c["ivan_pie"], 2), "VP operación", clp(c["vp_operacion"]))
    print("   saldos a la TIR", [clp(x) for x in c["saldos"]], "curva monótona", c["monotona"])


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    x = []
    e = R["ej"]
    x += [clp(e["van"]), clp(e["vp_entradas"]), pct(e["tir"]), pct(e["interp"][0]), clp(e["interp"][1]), clp(e["interp"][2]),
          clp(e["v15"]), clp(e["v20"]), fmt(e["pay"][0], 2), fmt(e["payd"][0], 2), pct(e["tirm"][0]), clp(e["tirm"][2]), fmt(e["ivan"], 3)]
    x += [clp(v) for v in e["descontados"][1:]]
    x += [clp(v) for v in e["payd"][1]]
    e = R["e1"]; x += [clp(e["van"]), pct(e["interp"][0]), clp(e["interp"][1]), clp(e["interp"][2])]
    for v in R["e2"].values():
        x += [clp(v["van"]), fmt(v["pay"], 1), pct(v["tir"])]
    v = R["e2"]["paneles"]; x += [clp(v["vf_ahorro"]), pct(v["tirm"]), fmt(v["factor_vf"], 4), clp(v["vp_ahorro"])]
    x += [fmt(R["e2"]["paneles"]["payd"], 2)]
    e = R["e4"]; x += [fmt(v, 3) for v in e["ivan"].values()] + [clp(e["codicioso"][2]), clp(e["optimo"][0])]
    e = R["e5"]; x += [clp(e["van_c"]), pct(e["tir_c"]), clp(e["van_g"]), pct(e["tir_g"]), clp(e["van_i"]), pct(e["tir_i"])]
    e = R["e6"]; x += [clp(e["oport"]), clp(e["anual"]), clp(e["van"]), clp(e["van_sin_oport"]), clp(e["vp_final"])] + [fmt(e["fa"], 4)]
    e = R["e7"]; x += [pct(e["rr"], 3), clp(e["van_real"]), clp(e["mal"])] + [clp(v) for v in e["nom"][1:]]
    e = R["e8"]; x += [pct(e["tir"]), pct(e["tirm"][0]), clp(e["vf_10"]), clp(e["vf_a_tir"]), clp(e["van"])]
    e = R["e9"]; x += [pct(v, 0) for v in e["tir_a"]] + [clp(e["van_a"]), clp(e["van_b"]), pct(e["tirm_a"][0]), pct(e["tirm_b"][0])]
    x += [clp(van(0, E9["a"]))]
    for k in ("A", "B"):
        v = R["e10"][k]; x += [clp(v["vac"]), clp(v["aeq"]), clp(v["vac_inf"])]
    x += [clp(v) for v in R["e10"]["comun"].values()]
    c = R["caso"]
    x += [clp(c["van"]), pct(c["tir"]), clp(c["vp_saldo"]), fmt(c["pay"][0], 2), fmt(c["payd"][0], 2), pct(c["tirm"][0]),
          clp(c["vp_inv"]), fmt(c["ivan"], 2), clp(c["vp_operacion"])]
    x += [clp(v) for v in c["desc"][1:]]
    x += [clp(c["curva"][k]) for k in (0.0, 0.20, 0.30, 0.40, 0.50, 1.00)]
    x += [clp(s) for s in c["saldos"][:-1]]
    return x


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    print("\nCADENA: OK, el caso de la unidad 5 calza con caso_valentina.py (VAN, TIR única y VP del saldo)")
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "05-van-y-tir.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [s for s in esperados(R) if s not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
