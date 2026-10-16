"""Unidad 10 · Riesgo, utilidad y aversión al riesgo.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md. La pieza del caso integrador se toma de
caso_valentina.py, la fuente única del caso.

    py -3 -P u10_utilidad.py            # imprime los resultados
    py -3 -P u10_utilidad.py --revisar  # además los busca en el .md
"""
from math import exp, log, sqrt
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))  # con -P la carpeta del script no entra sola
import caso_valentina as caso  # noqa: E402

# ---------------------------------------------------------------- herramientas

def fmt(x, dec=2):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def clp(x):
    return "$" + fmt(x, 0)


# Utilidad CRRA: γ = 0 neutral, γ = 1/2 raíz, γ = 1 logaritmo, γ = 2 es −1/W.
def u(w, gamma):
    if gamma == 1:
        return log(w)
    return w ** (1 - gamma) / (1 - gamma)


def u_inv(x, gamma):
    if gamma == 1:
        return exp(x)
    return (x * (1 - gamma)) ** (1 / (1 - gamma))


def loteria(esc):
    """esc: [(probabilidad, riqueza final)] → valor esperado, varianza y desviación."""
    assert abs(sum(p for p, _ in esc) - 1) < 1e-12
    e = sum(p * w for p, w in esc)
    v = sum(p * (w - e) ** 2 for p, w in esc)
    return e, v, sqrt(v)


def eq_cierto(esc, gamma):
    return u_inv(sum(p * u(w, gamma) for p, w in esc), gamma)


def eu(esc, gamma):
    return sum(p * u(w, gamma) for p, w in esc)


def biseccion(f, lo, hi):
    """Raíz de f en [lo, hi] (f cambia de signo)."""
    for _ in range(200):
        m = (lo + hi) / 2
        if f(lo) * f(m) <= 0:
            hi = m
        else:
            lo = m
    return (lo + hi) / 2


def max_unimodal(f, lo, hi):
    """Máximo de una función cóncava en [lo, hi] por sección dorada."""
    r = (sqrt(5) - 1) / 2
    a, b = lo, hi
    for _ in range(300):
        c, d = b - r * (b - a), a + r * (b - a)
        if f(c) > f(d):
            b = d
        else:
            a = c
    return (a + b) / 2


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. Personas y cifras ficticias.

# Teoría · dos inversiones con el mismo valor esperado
TEO = dict(A=[(0.5, 1_100_000), (0.5, 1_100_000)], B=[(0.5, 1_500_000), (0.5, 700_000)])
# Ejemplo resuelto · Martina y el seguro del auto (riqueza total, auto, probabilidad de robo, prima)
EJ = dict(riqueza=12_000_000, auto=8_000_000, p_robo=0.04, prima=420_000)
# 10.1 · cabaña en Pucón, ingreso neto de la temporada; alternativa: arriendo fijo
E1 = dict(esc=[(0.25, 1_200_000), (0.50, 2_600_000), (0.25, 3_500_000)], fijo=2_300_000)
# 10.2 · cuatro funciones de utilidad, W en millones de pesos, evaluadas en W = 4
E2 = dict(W=4)
# 10.3 · el concurso de la tele: una caja con dos montos
E3 = dict(esc=[(0.5, 810_000), (0.5, 1_690_000)], oferta=1_230_000)
# 10.5 · sueldo fijo o honorarios (utilidad raíz sobre el ingreso del mes)
E5 = dict(fijo=1_150_000, p_bueno=0.6, bueno=1_600_000, malo_b=700_000)
# 10.6 · tres inversionistas, la misma inversión
E6 = dict(W=3_000_000, sube=0.40, baja=-0.20, p=0.5, deposito=0.06, gammas=(0.5, 1, 2))
# 10.7 · seguro de la casa con y sin deducible (utilidad logarítmica)
E7 = dict(W=42_000_000, perdidas=[(0.02, 31_000_000), (0.06, 4_600_000)], prima_total=1_150_000,
          deducible=2_500_000, prima_deducible=830_000)
# 10.8 · la riqueza importa: apuesta ±$1.000.000 al 50 % con utilidad logarítmica
E8 = dict(riquezas=(2_000_000, 20_000_000), monto=1_000_000)
# 10.9 · cuánto poner en lo riesgoso (utilidad logarítmica, dos escenarios)
E9 = dict(W=10_000_000, rf=0.05, p=0.5, sube=0.30, baja=-0.18)


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # ---- teoría
    a, b = loteria(TEO["A"]), loteria(TEO["B"])
    R["teo"] = {"EA": a[0], "EB": b[0], "sB": b[2], "EC_B_ln": eq_cierto(TEO["B"], 1),
                "EC_B_raiz": eq_cierto(TEO["B"], 0.5)}
    R["teo"]["prima_ln"] = b[0] - R["teo"]["EC_B_ln"]
    R["teo"]["prima_raiz"] = b[0] - R["teo"]["EC_B_raiz"]

    # ---- ejemplo resuelto
    e = EJ
    sin = [(1 - e["p_robo"], e["riqueza"]), (e["p_robo"], e["riqueza"] - e["auto"])]
    E, V, S = loteria(sin)
    perdida_esp = e["p_robo"] * e["auto"]
    ec_ln, ec_r = eq_cierto(sin, 1), eq_cierto(sin, 0.5)
    con = e["riqueza"] - e["prima"]
    R["ej"] = {"E": E, "S": S, "perdida_esp": perdida_esp, "recargo": e["prima"] / perdida_esp - 1,
               "eu_ln": eu(sin, 1), "ln_con": log(con), "ln_W": log(e["riqueza"]), "ln_r": log(e["riqueza"] - e["auto"]),
               "ec_ln": ec_ln, "prima_max_ln": e["riqueza"] - ec_ln, "premio_ln": E - ec_ln,
               "eu_r": eu(sin, 0.5) * 2, "raiz_W": sqrt(e["riqueza"]), "raiz_r": sqrt(e["riqueza"] - e["auto"]),
               "ec_r": ec_r, "prima_max_r": e["riqueza"] - ec_r, "premio_r": E - ec_r, "con": con}

    # ---- 10.1
    e = E1
    E, V, S = loteria(e["esc"])
    R["e1"] = {"E": E, "V": V, "S": S, "cv": S / E, "dif": E - e["fijo"],
               "ec_r": eq_cierto(e["esc"], 0.5), "ec_ln": eq_cierto(e["esc"], 1)}

    # ---- 10.2  (W en millones)
    W = E2["W"]
    R["e2"] = {"A_pot": 0.6 / W, "R_pot": 0.6, "A_exp": 0.5, "R_exp": 0.5 * W, "A_cuad": -1 / W}

    # ---- 10.3
    e = E3
    E, V, S = loteria(e["esc"])
    Eraiz = sum(p * sqrt(w) for p, w in e["esc"])
    ec = Eraiz ** 2
    R["e3"] = {"E": E, "Eraiz": Eraiz, "EC": ec, "premio": E - ec, "raices": [sqrt(w) for _, w in e["esc"]],
               "ec_ln": eq_cierto(e["esc"], 1)}

    # ---- 10.5
    e = E5
    q = 1 - e["p_bueno"]
    y = ((sqrt(e["fijo"]) - e["p_bueno"] * sqrt(e["bueno"])) / q) ** 2
    y_neutral = (e["fijo"] - e["p_bueno"] * e["bueno"]) / q
    p_ind = (sqrt(e["fijo"]) - sqrt(e["malo_b"])) / (sqrt(e["bueno"]) - sqrt(e["malo_b"]))
    E_y = e["p_bueno"] * e["bueno"] + q * y
    R["e5"] = {"raiz_fijo": sqrt(e["fijo"]), "raiz_bueno": sqrt(e["bueno"]), "raiz_malo": sqrt(e["malo_b"]),
               "Y": y, "Y_neutral": y_neutral, "E_Y": E_y, "premio_Y": E_y - e["fijo"], "p": p_ind,
               "raiz_Y": sqrt(y)}

    # ---- 10.6
    e = E6
    esc = [(e["p"], e["W"] * (1 + e["sube"])), (1 - e["p"], e["W"] * (1 + e["baja"]))]
    E, V, S = loteria(esc)
    dep = e["W"] * (1 + e["deposito"])
    filas = [{"gamma": g, "EC": eq_cierto(esc, g), "premio": E - eq_cierto(esc, g)} for g in e["gammas"]]
    g_ind = biseccion(lambda g: eq_cierto(esc, g) - dep, 0.01, 0.999)
    R["e6"] = {"E": E, "S": S, "Er": E / e["W"] - 1, "dep": dep, "filas": filas, "g_ind": g_ind,
               "riquezas": [w for _, w in esc]}

    # ---- 10.7
    e = E7
    W = e["W"]
    p0 = 1 - sum(p for p, _ in e["perdidas"])
    A = [(p0, W)] + [(p, W - L) for p, L in e["perdidas"]]
    B = [(1, W - e["prima_total"])]
    C = [(p0, W - e["prima_deducible"])] + [(p, W - e["prima_deducible"] - min(L, e["deducible"])) for p, L in e["perdidas"]]
    perdida_esp = sum(p * L for p, L in e["perdidas"])
    cubre_ded = sum(p * max(L - e["deducible"], 0) for p, L in e["perdidas"])
    R["e7"] = {"perdida_esp": perdida_esp, "cubre_ded": cubre_ded,
               "recargo_total": e["prima_total"] / perdida_esp - 1, "recargo_ded": e["prima_deducible"] / cubre_ded - 1,
               "EA": loteria(A)[0], "EB": loteria(B)[0], "EC_": loteria(C)[0],
               "ecA": eq_cierto(A, 1), "ecB": eq_cierto(B, 1), "ecC": eq_cierto(C, 1),
               "prima_max": W - eq_cierto(A, 1)}

    # ---- 10.8
    e = E8
    filas = []
    for W in e["riquezas"]:
        esc = [(0.5, W + e["monto"]), (0.5, W - e["monto"])]
        ec = eq_cierto(esc, 1)
        aprox = 0.5 * (1 / W) * e["monto"] ** 2
        filas.append({"W": W, "EC": ec, "premio": W - ec, "aprox": aprox, "premio_pct": (W - ec) / W})
    W0 = e["riquezas"][0]
    gana = W0 ** 2 / (W0 - e["monto"]) - W0     # 0,5 ln(W0+X) + 0,5 ln(W0−m) = ln W0
    R["e8"] = {"filas": filas, "gana": gana}

    # ---- 10.9
    e = E9
    a, b = e["sube"] - e["rf"], e["baja"] - e["rf"]
    p, q = e["p"], 1 - e["p"]
    alfa = -(1 + e["rf"]) * (p * a + q * b) / (a * b)
    def riq(al):
        return [(p, e["W"] * (1 + e["rf"] + al * a)), (q, e["W"] * (1 + e["rf"] + al * b))]
    alfa_num = max_unimodal(lambda al: eu(riq(al), 1), 0, 1)
    alfa_raiz = max_unimodal(lambda al: eu(riq(al), 0.5), 0, 1)
    E_r = p * e["sube"] + q * e["baja"]
    R["e9"] = {"a": a, "b": b, "E_r": E_r, "prima_exceso": E_r - e["rf"], "alfa": alfa, "alfa_num": alfa_num,
               "monto": alfa * e["W"], "ec_alfa": eq_cierto(riq(alfa), 1), "ec_0": e["W"] * (1 + e["rf"]),
               "ec_1": eq_cierto(riq(1), 1), "E_1": loteria(riq(1))[0], "alfa_raiz": alfa_raiz,
               "ec_mitad": eq_cierto(riq(alfa / 2), 1), "ec_doble": eq_cierto(riq(2 * alfa), 1),
               "riq_alfa": [w for _, w in riq(alfa)]}

    # ---- caso integrador (desde la fuente única)
    Cc = caso.calcular()
    u10, U10 = Cc["u10"], caso.U10
    Wc = U10["riqueza"]
    esc = [(p, Wc * (1 + x)) for p, x in U10["escenarios"]]
    E, V, S = loteria(esc)
    dep = Wc * (1 + U10["deposito"])
    g_ind = biseccion(lambda g: eq_cierto(esc, g) - dep, 1.0001, 10)
    assert abs(eq_cierto(esc, 1) - u10["equivalente_cierto"]) < 1e-6
    assert abs(E - Wc * (1 + u10["retorno_esperado"])) < 1e-6
    R["caso"] = {**u10, "riquezas": [w for _, w in esc], "lns": [log(w) for _, w in esc], "eu": eu(esc, 1),
                 "E": E, "S_pesos": S, "ec_raiz": eq_cierto(esc, 0.5), "ec_2": eq_cierto(esc, 2),
                 "g_ind": g_ind, "ventaja": u10["equivalente_cierto"] - u10["con_deposito"],
                 "r_ec": u10["equivalente_cierto"] / Wc - 1, "perdida": Wc - esc[2][1],
                 "ln_dep": log(dep)}
    return R


def imprimir(R):
    for k, v in R.items():
        print(f"== {k}")
        for a, b in v.items():
            if isinstance(b, float):
                b = round(b, 6)
            print(f"   {a}: {b}")


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    x = []
    t = R["teo"]
    x += [clp(t["sB"]), clp(t["EC_B_ln"]), clp(t["EC_B_raiz"]), clp(t["prima_ln"]), clp(t["prima_raiz"])]
    e = R["ej"]
    x += [clp(e["E"]), clp(e["S"]), clp(e["perdida_esp"]), pct(e["recargo"], 2), fmt(e["ln_W"], 5), fmt(e["ln_r"], 5),
          fmt(e["eu_ln"], 5), fmt(e["ln_con"], 5), clp(e["ec_ln"]), clp(e["prima_max_ln"]), clp(e["premio_ln"]),
          fmt(e["raiz_W"]), fmt(e["raiz_r"]), clp(e["ec_r"]), clp(e["prima_max_r"]), clp(e["premio_r"]), clp(e["con"])]
    e = R["e1"]; x += [clp(e["E"]), clp(e["S"]), pct(e["cv"], 1), clp(e["dif"]), clp(e["ec_r"]), clp(e["ec_ln"])]
    e = R["e2"]; x += [fmt(e["A_pot"], 2), fmt(e["R_exp"], 0), fmt(e["A_cuad"], 2)]
    e = R["e3"]; x += [clp(e["E"]), fmt(e["Eraiz"], 0), clp(e["EC"]), clp(e["premio"]), clp(e["ec_ln"])]
    e = R["e5"]; x += [fmt(e["raiz_fijo"]), fmt(e["raiz_bueno"]), fmt(e["raiz_malo"]), clp(e["Y"]), clp(e["Y_neutral"]),
                       clp(e["E_Y"]), clp(e["premio_Y"]), fmt(e["p"], 3), fmt(e["raiz_Y"]),
                       clp(e["Y"] - e["Y_neutral"])]
    e = R["e6"]; x += [clp(e["E"]), clp(e["dep"]), fmt(e["g_ind"], 2)] + [clp(w) for w in e["riquezas"]]
    for f in e["filas"]:
        x += [clp(f["EC"]), clp(f["premio"])]
    e = R["e7"]; x += [clp(e["perdida_esp"]), clp(e["cubre_ded"]), pct(e["recargo_total"], 1), pct(e["recargo_ded"], 1),
                       clp(e["EA"]), clp(e["EB"]), clp(e["EC_"]), clp(e["ecA"]), clp(e["ecB"]), clp(e["ecC"]),
                       clp(e["prima_max"])]
    e = R["e8"]
    for f in e["filas"]:
        x += [clp(f["EC"]), clp(f["premio"]), clp(f["aprox"]), pct(f["premio_pct"], 2)]
    x += [clp(e["gana"])]
    e = R["e9"]; x += [pct(e["E_r"], 1), pct(e["alfa"], 2), clp(e["monto"]), clp(e["ec_alfa"]), clp(e["ec_0"]),
                       clp(e["ec_1"]), clp(e["E_1"]), pct(e["alfa_raiz"], 1), clp(e["ec_mitad"]), clp(e["ec_doble"])]
    x += [clp(w) for w in e["riq_alfa"]]
    c = R["caso"]
    x += [pct(c["retorno_esperado"], 1), pct(c["desviacion"], 2), clp(c["equivalente_cierto"]), clp(c["premio_riesgo"]),
          clp(c["con_deposito"]), clp(c["E"]), clp(c["S_pesos"]), clp(c["ec_raiz"]), clp(c["ec_2"]), fmt(c["g_ind"], 2),
          clp(c["ventaja"]), pct(c["r_ec"], 2), fmt(c["eu"], 5), fmt(c["ln_dep"], 5), clp(c["perdida"])]
    x += [clp(w) for w in c["riquezas"]] + [fmt(v, 5) for v in c["lns"]]
    return x


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "10-riesgo-y-utilidad.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".")  # en LaTeX la coma decimal va {,} y el punto de miles {.}
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
