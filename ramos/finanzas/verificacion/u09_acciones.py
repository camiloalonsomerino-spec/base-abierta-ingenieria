"""Unidad 9 · Acciones.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md. La pieza del caso integrador se toma de
caso_valentina.py, la fuente única del caso.

    py -3 -P u09_acciones.py            # imprime los resultados
    py -3 -P u09_acciones.py --revisar  # además los busca en el .md
"""
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


def clp(x, dec=0):
    return "$" + fmt(x, dec)


def gordon(d1, k, g):
    assert k > g, "Gordon exige k > g"
    return d1 / (k - g)


def dos_etapas(d1, g1, n_alto, g2, k):
    """d1 es el dividendo del año 1. Crece g1 hasta el año n_alto (inclusive) y g2 después.
    Devuelve dividendos de la etapa alta, VP de cada uno, valor terminal en n_alto y precio."""
    divs = [d1 * (1 + g1) ** (t - 1) for t in range(1, n_alto + 1)]
    vps = [d / (1 + k) ** t for t, d in enumerate(divs, start=1)]
    d_sig = divs[-1] * (1 + g2)
    vt = gordon(d_sig, k, g2)
    vp_vt = vt / (1 + k) ** n_alto
    return {"divs": divs, "vps": vps, "suma_vp": sum(vps), "d_sig": d_sig, "vt": vt,
            "vp_vt": vp_vt, "P0": sum(vps) + vp_vt, "peso_vt": vp_vt / (sum(vps) + vp_vt)}


def k_implicita(precio, f, lo, hi):
    """Tasa que iguala f(k) con el precio (f decrece en k)."""
    for _ in range(200):
        m = (lo + hi) / 2
        if f(m) > precio:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. Empresas y cifras ficticias.

# Teoría · el mismo ejemplo para el horizonte y P1
TEO = dict(d1=40, g=0.04, k=0.09)
# Ejemplo resuelto · Lácteos del Ñuble, las acciones de la abuela
EJ = dict(d0=52, g1=0.08, n=3, g2=0.03, k=0.10, precio=905, acciones=2_500, upa1=78)
# 9.1 · Pesquera Golfo de Arauco, «acaba de pagar»
E1 = dict(d0=38, g=0.025, k=0.095)
# 9.2 · acción preferente de una cooperativa
E2 = dict(div=1_450, k=0.082, precio=16_900, k2=0.09)
# 9.3 · Molinos del Itata, g y k implícita
E3 = dict(utilidad=2_640, acciones=400, b=0.35, roe=0.13, precio=78)   # millones de pesos y de acciones
# 9.5 · Sonrisa Sur, clínicas dentales, dos etapas desde un D1
E5 = dict(d1=120, g1=0.14, n=4, g2=0.04, k=0.12)
# 9.6 · Ferretería Austral, cambiar la política de reparto
E6 = dict(upa1=340, k=0.11, b=0.45, roes=(0.15, 0.08, 0.11))
# 9.7 · una sanitaria y una tecnológica, qué dice el P/U
E7 = dict(san=dict(k=0.08, upa1=96, precio=1_250), tec=dict(k=0.13, upa1=40, precio=820))
# 9.8 · comente de la tasa del Banco Central
E8 = dict(d1=50, g=0.03, k=0.09, k2=0.10)
# 9.9 · Transportes Cordillera, camiones eléctricos (millones de pesos y de acciones)
E9 = dict(upa1=95, acciones=600, k=0.11, inversion=18_000, utilidad_extra=2_700, k_proy=0.14)
# 9.10 · Energía Solar Atacama, k implícita con dos etapas
E10 = dict(precio=3_200, d1=96, g1=0.18, n=5, g2=0.035)


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # ---- teoría: horizonte y P1
    t = TEO
    p0 = gordon(t["d1"], t["k"], t["g"])
    d2 = t["d1"] * (1 + t["g"])
    p1 = p0 * (1 + t["g"])
    p2 = p1 * (1 + t["g"])
    R["teo"] = {"P0": p0, "d2": d2, "P1": p1, "P2": p2,
                "vp_d1": t["d1"] / (1 + t["k"]), "vp_d2": d2 / (1 + t["k"]) ** 2, "vp_p2": p2 / (1 + t["k"]) ** 2,
                "uno": (t["d1"] + p1) / (1 + t["k"]),
                "rd": t["d1"] / p0, "g_cap": (p1 - p0) / p0,
                "sens_g": gordon(t["d1"], t["k"], 0.05), "sens_g2": gordon(t["d1"], t["k"], 0.06)}

    # ---- ejemplo resuelto
    e = EJ
    d1 = e["d0"] * (1 + e["g1"])
    de = dos_etapas(d1, e["g1"], e["n"], e["g2"], e["k"])
    solo_g2 = gordon(e["d0"] * (1 + e["g2"]), e["k"], e["g2"])
    f = lambda k: dos_etapas(d1, e["g1"], e["n"], e["g2"], k)["P0"]
    kimp = k_implicita(e["precio"], f, e["g2"] + 1e-6, 0.5)
    sin_crec = e["upa1"] / e["k"]
    R["ej"] = {**de, "d1": d1, "solo_g2": solo_g2, "kimp": kimp, "sin_crec": sin_crec,
               "vpoc": de["P0"] - sin_crec, "pu": de["P0"] / e["upa1"], "pu_mercado": e["precio"] / e["upa1"],
               "pu_sin": 1 / e["k"], "payout": d1 / e["upa1"],
               "vende": e["acciones"] * e["precio"], "vale": e["acciones"] * de["P0"],
               "dif": e["acciones"] * (e["precio"] - de["P0"])}

    # ---- 9.1
    e = E1
    d1 = e["d0"] * (1 + e["g"])
    p0 = gordon(d1, e["k"], e["g"])
    mal = gordon(e["d0"], e["k"], e["g"])
    R["e1"] = {"d1": d1, "P0": p0, "mal": mal, "error": p0 - mal, "P1": p0 * (1 + e["g"]),
               "P5": p0 * (1 + e["g"]) ** 5, "rd": d1 / p0}

    # ---- 9.2
    e = E2
    R["e2"] = {"P0": e["div"] / e["k"], "r_mercado": e["div"] / e["precio"], "P0_k2": e["div"] / e["k2"],
               "caida": e["div"] / e["k2"] / (e["div"] / e["k"]) - 1}

    # ---- 9.3
    e = E3
    g = e["b"] * e["roe"]
    upa0 = e["utilidad"] / e["acciones"]
    upa1 = upa0 * (1 + g)
    div1 = (1 - e["b"]) * upa1
    k = div1 / e["precio"] + g
    div_mal = (1 - e["b"]) * upa0
    R["e3"] = {"g": g, "upa0": upa0, "upa1": upa1, "div1": div1, "rd": div1 / e["precio"], "k": k,
               "div_mal": div_mal, "k_mal": div_mal / e["precio"] + g,
               "aumento": e["utilidad"] * e["b"] * e["roe"]}

    # ---- 9.5
    e = E5
    R["e5"] = dos_etapas(e["d1"], e["g1"], e["n"], e["g2"], e["k"])
    R["e5"]["mal"] = R["e5"]["vt"] / (1 + e["k"]) ** (e["n"] + 1) + R["e5"]["suma_vp"]
    R["e5"]["solo_g2"] = gordon(e["d1"], e["k"], e["g2"])
    R["e5"]["dif_mal"] = R["e5"]["P0"] - R["e5"]["mal"]
    R["e5"]["dif_exp"] = R["e5"]["P0"] - R["e5"]["solo_g2"]

    # ---- 9.6
    e = E6
    sin = e["upa1"] / e["k"]
    d1 = (1 - e["b"]) * e["upa1"]
    filas = []
    for roe in e["roes"]:
        g = e["b"] * roe
        p = gordon(d1, e["k"], g)
        filas.append({"roe": roe, "g": g, "P0": p, "vpoc": p - sin, "pu": p / e["upa1"]})
    R["e6"] = {"sin": sin, "d1": d1, "filas": filas, "pu_sin": 1 / e["k"]}

    # ---- 9.7
    R["e7"] = {}
    for n, e in E7.items():
        sin = e["upa1"] / e["k"]
        R["e7"][n] = {"pu": e["precio"] / e["upa1"], "sin": sin, "vpoc": e["precio"] - sin,
                      "peso": (e["precio"] - sin) / e["precio"], "pu_sin": 1 / e["k"]}

    # ---- 9.8
    e = E8
    a, b = gordon(e["d1"], e["k"], e["g"]), gordon(e["d1"], e["k2"], e["g"])
    R["e8"] = {"antes": a, "despues": b, "caida": b / a - 1}

    # ---- 9.9
    e = E9
    sin = e["upa1"] / e["k"]
    van1 = -e["inversion"] + e["utilidad_extra"] / e["k"]
    van0 = van1 / (1 + e["k"])
    vpoc = van0 / e["acciones"]
    van1_b = -e["inversion"] + e["utilidad_extra"] / e["k_proy"]
    van0_b = van1_b / (1 + e["k_proy"])
    R["e9"] = {"sin": sin, "perp": e["utilidad_extra"] / e["k"], "van1": van1, "van0": van0, "vpoc": vpoc,
               "P0": sin + vpoc, "pu": (sin + vpoc) / e["upa1"], "pu_sin": 1 / e["k"],
               "perp_b": e["utilidad_extra"] / e["k_proy"], "van1_b": van1_b, "van0_b": van0_b,
               "vpoc_b": van0_b / e["acciones"], "P0_b": sin + van0_b / e["acciones"],
               "rend": e["utilidad_extra"] / e["inversion"],
               "mal": (-e["inversion"] + e["utilidad_extra"] / e["k"]) / e["acciones"]}

    # ---- 9.10
    e = E10
    f = lambda k: dos_etapas(e["d1"], e["g1"], e["n"], e["g2"], k)["P0"]
    kimp = k_implicita(e["precio"], f, e["g2"] + 1e-6, 0.17)
    chk = dos_etapas(e["d1"], e["g1"], e["n"], e["g2"], kimp)
    R["e10"] = {"kimp": kimp, "chk": chk, "k_bajo": e["d1"] / e["precio"] + e["g2"],
                "k_alto": e["d1"] / e["precio"] + e["g1"], "rd": e["d1"] / e["precio"],
                "a10": f(0.10), "a9": f(0.09), "a11": f(0.11)}

    # ---- caso integrador (desde la fuente única)
    C = caso.calcular()
    u9, U9 = C["u9"], caso.U9
    b = 1 - u9["payout"]
    R["caso"] = {**u9, "retencion": b, "roe": U9["g"] / b, "pu": u9["precio_gordon"] / U9["utilidad_por_accion"],
                 "pu_sin": 1 / U9["k_analistas"], "rd": U9["dividendo_1"] / u9["precio_gordon"],
                 "k_chk": U9["dividendo_1"] / u9["precio_gordon"] + U9["g"],
                 "peso_vpoc": u9["pvgo"] / u9["precio_gordon"],
                 "P1": u9["precio_gordon"] * (1 + U9["g"]),
                 "k_capm": C["u12"]["k_capm"], "precio_capm": C["u12"]["precio_con_capm"],
                 "baja_k": U9["k_analistas"] - C["u12"]["k_capm"],
                 "sube_p": C["u12"]["precio_con_capm"] - u9["precio_gordon"]}
    R["caso"]["veces_vpoc"] = R["caso"]["sube_p"] / u9["pvgo"]
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
    x += [fmt(t["P0"], 0), fmt(t["d2"], 1), fmt(t["P1"], 0), fmt(t["P2"], 2), fmt(t["vp_d1"]), fmt(t["vp_d2"]),
          fmt(t["vp_p2"]), pct(t["rd"], 1), pct(t["g_cap"], 1), fmt(t["sens_g"], 0), fmt(t["sens_g2"], 0)]
    e = R["ej"]
    x += [fmt(e["d1"]), fmt(e["solo_g2"])] + [fmt(d) for d in e["divs"]] + [fmt(v) for v in e["vps"]]
    x += [fmt(e["suma_vp"]), fmt(e["d_sig"]), fmt(e["vt"]), fmt(e["vp_vt"]), fmt(e["P0"]), pct(e["peso_vt"]),
          pct(e["kimp"], 2), fmt(e["sin_crec"], 0), fmt(e["vpoc"]), fmt(e["pu"]), fmt(e["pu_mercado"]),
          pct(e["payout"], 0), clp(e["vende"]), clp(e["vale"]), clp(e["dif"])]
    e = R["e1"]; x += [fmt(e["d1"]), fmt(e["P0"]), fmt(e["mal"]), fmt(e["error"]), fmt(e["P1"]), fmt(e["P5"]), pct(e["rd"], 1)]
    e = R["e2"]; x += [clp(e["P0"]), pct(e["r_mercado"], 2), clp(e["P0_k2"]), pct(-e["caida"], 1)]
    e = R["e3"]; x += [pct(e["g"], 2), fmt(e["upa0"]), fmt(e["upa1"], 4), fmt(e["div1"], 4), pct(e["rd"], 2),
                       pct(e["k"], 2), fmt(e["div_mal"]), pct(e["k_mal"], 2), fmt(e["aumento"], 2)]
    e = R["e5"]; x += [fmt(d) for d in e["divs"]] + [fmt(v) for v in e["vps"]]
    x += [fmt(e["suma_vp"]), fmt(e["d_sig"]), fmt(e["vt"]), fmt(e["vp_vt"]), fmt(e["P0"]), pct(e["peso_vt"]),
          fmt(e["mal"]), fmt(e["solo_g2"], 0), fmt(e["dif_mal"], 0), fmt(e["dif_exp"], 0)]
    e = R["e6"]; x += [fmt(e["sin"]), fmt(e["d1"], 0)]
    for f in e["filas"]:
        x += [pct(f["g"], 2), fmt(f["P0"]), fmt(f["vpoc"]), fmt(f["pu"])]
    for v in R["e7"].values():
        x += [fmt(v["pu"]), fmt(v["sin"]), fmt(v["vpoc"]), pct(v["peso"], 1), fmt(v["pu_sin"])]
    e = R["e8"]; x += [fmt(e["antes"]), fmt(e["despues"]), pct(-e["caida"], 1)]
    e = R["e9"]; x += [fmt(e["sin"]), fmt(e["perp"]), fmt(e["van1"]), fmt(e["van0"]), fmt(e["vpoc"]), fmt(e["P0"]),
                       fmt(e["pu"]), fmt(e["perp_b"]), fmt(e["van1_b"]), fmt(e["van0_b"]), fmt(e["vpoc_b"]),
                       fmt(e["P0_b"]), pct(e["rend"], 0), fmt(e["mal"])]
    e = R["e10"]; x += [pct(e["kimp"], 2), pct(e["k_bajo"], 1), pct(e["k_alto"], 1), fmt(e["chk"]["vt"]),
                        fmt(e["chk"]["vp_vt"]), fmt(e["chk"]["suma_vp"]), pct(e["chk"]["peso_vt"]),
                        fmt(e["a10"]), fmt(e["a9"]), fmt(e["a11"])] + [fmt(d) for d in e["chk"]["divs"]]
    c = R["caso"]
    x += [fmt(c["precio_gordon"]), fmt(c["valor_sin_crecimiento"]), fmt(c["pvgo"]), pct(c["payout"]),
          pct(c["retencion"]), pct(c["roe"], 2), fmt(c["pu"]), fmt(c["pu_sin"]), pct(c["rd"]), pct(c["peso_vpoc"]),
          fmt(c["P1"]), pct(c["k_capm"], 2), fmt(c["precio_capm"]), fmt(100 * c["baja_k"], 2), fmt(c["sube_p"], 0),
          fmt(c["veces_vpoc"], 1)]
    return x


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "09-acciones.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".")  # en LaTeX la coma decimal va {,} y el punto de miles {.}
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
