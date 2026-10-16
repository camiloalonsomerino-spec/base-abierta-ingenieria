"""Unidad 7 · Bonos.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md. La pieza del caso integrador se toma de
caso_valentina.py.

    py -3 -P u07_bonos.py            # imprime los resultados
    py -3 -P u07_bonos.py --revisar  # además los busca en el .md
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


def pct(x, dec=2):
    return fmt(100 * x, dec) + " %"


def clp(x):
    return "$" + fmt(x, 0)


def vp(flujos, y, t0=1):
    """Valor presente de flujos que llegan en t0, t0+1, … a una tasa única y."""
    return sum(f / (1 + y) ** t for t, f in enumerate(flujos, start=t0))


def vp_spot(flujos, spot):
    return sum(f / (1 + r) ** t for t, (f, r) in enumerate(zip(flujos, spot), start=1))


def bullet(vn, c, n):
    cup = vn * c
    return [cup] * (n - 1) + [cup + vn]


def tir(flujos, lo=-0.5, hi=1.0):
    """Tasa que anula el VAN de flujos que parten en t = 0 (bisección)."""
    van = lambda r: sum(f / (1 + r) ** t for t, f in enumerate(flujos))
    for _ in range(200):
        mid = (lo + hi) / 2
        if van(lo) * van(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def interpolar(flujos, r1, r2):
    """Interpolación lineal de la TIR entre r1 y r2 (VAN de signos opuestos)."""
    van = lambda r: sum(f / (1 + r) ** t for t, f in enumerate(flujos))
    v1, v2 = van(r1), van(r2)
    return {"r1": r1, "r2": r2, "van1": v1, "van2": v2, "r": r1 + (r2 - r1) * v1 / (v1 - v2)}


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. Emisores, personas y tasas son ficticios.

# Ejemplo resuelto · Paula compra un bono de «Aguas del Itata S.A.»
EJ = dict(vn=1_000_000, c=0.064, n=5, y0=0.056, k=2, yk=0.067, r1=0.04, r2=0.05)
# 7.1 · bono en UF a tres tasas
E1 = dict(vn=2_000, c=0.037, n=6, tasas=(0.032, 0.037, 0.044))
# 7.2 · cero cupón
E2 = dict(vn=10_000_000, n=4, y=0.063, y2=0.070, precio=7_650_000)
# 7.3 · bono que amortiza capital constante (alemán)
E3 = dict(vn=900, n=3, c=0.045, y=0.052)
# 7.5 · rentabilidad al vencimiento por interpolación
E5 = dict(vn=500_000, c=0.072, n=4, precio=479_800, r1=0.08, r2=0.09)
# 7.6 · cupón semestral con tasa anual efectiva
E6 = dict(vn=3_000, c_sem=0.019, semestres=14, y_anual=0.046)
# 7.7 · período de tenencia y reinversión
E7 = dict(vn=2_000_000, c=0.055, n=8, k=3, yk=0.043, reinv=0.038, r1=0.07, r2=0.08)
# 7.8 · precio sucio y limpio
E8 = dict(vn=100, c=0.066, quedan=3, y=0.059, fracciones=(0.25, 0.75))
# 7.9 y 7.10 · curva spot, réplica y arbitraje
SPOT = [0.044, 0.049, 0.055]
E9 = dict(c=0.082, precio_mercado=106.90)
E10 = dict(cupones=(0.02, 0.10))


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # ---- ejemplo resuelto
    e = EJ
    fl = bullet(e["vn"], e["c"], e["n"])
    p0 = vp(fl, e["y0"])
    a = (1 - (1 + e["y0"]) ** -e["n"]) / e["y0"]
    pk = vp(fl[e["k"]:], e["yk"])
    tenedor = [-p0] + fl[:e["k"] - 1] + [fl[e["k"] - 1] + pk]
    R["ej"] = {"cupon": fl[0], "a": a, "vp_cupones": fl[0] * a, "vp_nominal": e["vn"] / (1 + e["y0"]) ** e["n"],
               "p0": p0, "prima": p0 - e["vn"], "pk": pk, "perdida": p0 - pk, "tenedor": tenedor,
               "interp": interpolar(tenedor, e["r1"], e["r2"]), "hpr": tir(tenedor),
               "van_comprador": -pk + vp(fl[e["k"]:], e["yk"]),
               "p_a_la_par_en_k": vp(fl[e["k"]:], e["c"]),
               "pk_si_no_cambia": vp(fl[e["k"]:], e["y0"])}
    # ---- 7.1
    e = E1
    fl = bullet(e["vn"], e["c"], e["n"])
    R["e1"] = {"cupon": fl[0], "precios": [vp(fl, y) for y in e["tasas"]]}
    # ---- 7.2
    e = E2
    p = e["vn"] / (1 + e["y"]) ** e["n"]
    p2 = e["vn"] / (1 + e["y2"]) ** e["n"]
    R["e2"] = {"p": p, "p2": p2, "caida": p2 / p - 1, "dif": p - p2,
               "tasa_impl": (e["vn"] / e["precio"]) ** (1 / e["n"]) - 1}
    # ---- 7.3 alemán
    e = E3
    amort = e["vn"] / e["n"]
    saldo, filas = e["vn"], []
    for t in range(1, e["n"] + 1):
        i = saldo * e["c"]
        filas.append({"t": t, "saldo_ini": saldo, "interes": i, "amort": amort, "flujo": i + amort, "saldo_fin": saldo - amort})
        saldo -= amort
    flujos = [f["flujo"] for f in filas]
    R["e3"] = {"filas": filas, "p0": vp(flujos, e["y"]), "p1": vp(flujos[1:], e["y"]), "par1": filas[0]["saldo_fin"]}
    # ---- 7.5
    e = E5
    fl = bullet(e["vn"], e["c"], e["n"])
    flt = [-e["precio"]] + fl
    R["e5"] = {"cupon": fl[0], "interp": interpolar(flt, e["r1"], e["r2"]), "ytm": tir(flt),
               "p_r1": vp(fl, e["r1"]), "p_r2": vp(fl, e["r2"])}
    # ---- 7.6
    e = E6
    ys = (1 + e["y_anual"]) ** 0.5 - 1
    fl = bullet(e["vn"], e["c_sem"], e["semestres"])
    p = vp(fl, ys)
    p_mal = vp(fl, e["y_anual"] / 2)
    R["e6"] = {"ys": ys, "cupon": fl[0], "p": p, "p_mal": p_mal, "error": p_mal - p,
               "c_anual_equiv": (1 + e["c_sem"]) ** 2 - 1}
    # ---- 7.7
    e = E7
    fl = bullet(e["vn"], e["c"], e["n"])
    pk = vp(fl[e["k"]:], e["yk"])
    tenedor = [-e["vn"]] + fl[:e["k"] - 1] + [fl[e["k"] - 1] + pk]
    vf = sum(fl[0] * (1 + e["reinv"]) ** (e["k"] - t) for t in range(1, e["k"] + 1)) + pk
    R["e7"] = {"cupon": fl[0], "pk": pk, "tenedor": tenedor, "interp": interpolar(tenedor, e["r1"], e["r2"]),
               "hpr": tir(tenedor), "vf": vf, "efectiva": (vf / e["vn"]) ** (1 / e["k"]) - 1,
               "vf_cupones": vf - pk}
    # ---- 7.8 precio sucio y limpio
    e = E8
    fl = bullet(e["vn"], e["c"], e["quedan"])
    p_ex = vp(fl, e["y"])            # justo después de cobrar el último cupón
    fil = []
    for f in e["fracciones"]:
        sucio = p_ex * (1 + e["y"]) ** f
        dev = e["vn"] * e["c"] * f
        fil.append({"f": f, "sucio": sucio, "devengado": dev, "limpio": sucio - dev})
    antes = p_ex * (1 + e["y"])      # un instante antes del próximo cupón, con el cupón adentro
    despues = vp(fl[1:], e["y"])     # un instante después, sin ese cupón
    R["e8"] = {"p_ex": p_ex, "filas": fil, "antes": antes, "despues": despues,
               "limpio_antes": antes - e["vn"] * e["c"]}
    # ---- 7.9 réplica y arbitraje
    fl = bullet(100, E9["c"], 3)
    p_teo = vp_spot(fl, SPOT)
    ceros = [100 / (1 + r) ** t for t, r in enumerate(SPOT, start=1)]
    R["e9"] = {"flujos": fl, "vps": [f / (1 + r) ** t for t, (f, r) in enumerate(zip(fl, SPOT), start=1)],
               "p": p_teo, "ytm": tir([-p_teo] + fl), "ceros": ceros,
               "unidades_ceros": [f / 100 for f in fl], "ganancia": p_teo - E9["precio_mercado"],
               "ytm_mercado": tir([-E9["precio_mercado"]] + fl)}
    # ---- 7.10 efecto cupón
    fil = []
    for c in E10["cupones"]:
        fl = bullet(100, c, 3)
        p = vp_spot(fl, SPOT)
        fil.append({"c": c, "p": p, "ytm": tir([-p] + fl)})
    R["e10"] = fil
    # ---- caso integrador
    C = caso.calcular()
    u6, u7 = C["u6"], C["u7"]
    fl = u7["flujos"]
    spot = u6["spot"][:len(fl)]
    filas = [{"t": t, "flujo": f, "spot": r, "factor": 1 / (1 + r) ** t, "vp": f / (1 + r) ** t}
             for t, (f, r) in enumerate(zip(fl, spot), start=1)]
    R["caso"] = {"filas": filas, "precio": u7["precio"], "ytm": u7["ytm"], "sobre": u7["sobre_la_par"],
                 "precios_cero": caso.U6["precios_cero"][:len(fl)],
                 "interp": interpolar([-u7["precio"]] + fl, 0.05, 0.06),
                 "p_al_5": vp(fl, 0.05), "p_al_6": vp(fl, 0.06),
                 "chequeo_ytm": vp(fl, u7["ytm"]), "prima": u7["precio"] - caso.U7["nominal"],
                 "peso_final": filas[-1]["vp"] / u7["precio"]}
    return R


def imprimir(R):
    e = R["ej"]
    print("== Ejemplo")
    print(f"   cupón {clp(e['cupon'])} a {fmt(e['a'],4)} vp cupones {clp(e['vp_cupones'])} vp nominal {clp(e['vp_nominal'])} P0 {clp(e['p0'])} prima {clp(e['prima'])}")
    print(f"   P2 {clp(e['pk'])} pérdida {clp(e['perdida'])} P2 sin cambio {clp(e['pk_si_no_cambia'])} | tenedor {[clp(x) for x in e['tenedor']]}")
    i = e["interp"]; print(f"   VAN(r1) {clp(i['van1'])} VAN(r2) {clp(i['van2'])} interp {pct(i['r'])} exacta {pct(e['hpr'],3)} | VAN comprador {e['van_comprador']:.6f}")
    e = R["e1"]; print("== 7.1 cupón", e["cupon"], [fmt(p) for p in e["precios"]])
    e = R["e2"]; print(f"== 7.2 P {clp(e['p'])} P' {clp(e['p2'])} caída {pct(e['caida'])} dif {clp(e['dif'])} tasa impl {pct(e['tasa_impl'])}")
    e = R["e3"]; print("== 7.3", [(f['t'], fmt(f['interes']), fmt(f['flujo']), fmt(f['saldo_fin'])) for f in e["filas"]], "P0", fmt(e["p0"]), "P1", fmt(e["p1"]), "par1", e["par1"])
    e = R["e5"]; i = e["interp"]
    print(f"== 7.5 cupón {clp(e['cupon'])} P(8%) {clp(e['p_r1'])} P(9%) {clp(e['p_r2'])} VAN1 {clp(i['van1'])} VAN2 {clp(i['van2'])} interp {pct(i['r'])} exacta {pct(e['ytm'],3)}")
    e = R["e6"]; print(f"== 7.6 ys {pct(e['ys'],4)} cupón {fmt(e['cupon'])} P {fmt(e['p'])} P mal {fmt(e['p_mal'])} error {fmt(e['error'])} c anual eq {pct(e['c_anual_equiv'])}")
    e = R["e7"]; i = e["interp"]
    print(f"== 7.7 cupón {clp(e['cupon'])} P3 {clp(e['pk'])} VAN1 {clp(i['van1'])} VAN2 {clp(i['van2'])} interp {pct(i['r'])} exacta {pct(e['hpr'],3)} | vf cupones {clp(e['vf_cupones'])} vf {clp(e['vf'])} efectiva {pct(e['efectiva'])}")
    e = R["e8"]; print(f"== 7.8 P_ex {fmt(e['p_ex'])} antes {fmt(e['antes'])} después {fmt(e['despues'])} limpio antes {fmt(e['limpio_antes'])}", [(f['f'], fmt(f['sucio']), fmt(f['devengado']), fmt(f['limpio'])) for f in e["filas"]])
    e = R["e9"]; print(f"== 7.9 vps {[fmt(x) for x in e['vps']]} P {fmt(e['p'])} ytm {pct(e['ytm'])} ceros {[fmt(x) for x in e['ceros']]} unidades {[fmt(x,3) for x in e['unidades_ceros']]} ganancia {fmt(e['ganancia'])} ytm mercado {pct(e['ytm_mercado'])}")
    print("== 7.10", [(f['c'], fmt(f['p']), pct(f['ytm'])) for f in R["e10"]])
    c = R["caso"]
    print("== caso", [(f['t'], fmt(f['flujo'],1), pct(f['spot']), fmt(f['factor'],6), fmt(f['vp'],4)) for f in c["filas"]])
    i = c["interp"]
    print(f"   P {fmt(c['precio'],4)} ytm {pct(c['ytm'],3)} P(5%) {fmt(c['p_al_5'])} P(6%) {fmt(c['p_al_6'])} VAN1 {fmt(i['van1'])} VAN2 {fmt(i['van2'])} interp {pct(i['r'])} chequeo {fmt(c['chequeo_ytm'],4)} prima {fmt(c['prima'])} peso final {pct(c['peso_final'],1)}")


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    x = []
    e = R["ej"]; i = e["interp"]
    x += [clp(e["cupon"]), fmt(e["a"], 4), clp(e["vp_cupones"]), clp(e["vp_nominal"]), clp(e["p0"]), clp(e["prima"]),
          clp(e["pk"]), clp(e["perdida"]), clp(e["pk_si_no_cambia"]), clp(e["tenedor"][-1]),
          clp(i["van1"]), clp(-i["van2"]), pct(i["r"]), pct(e["hpr"])]
    e = R["e1"]; x += [fmt(p) for p in e["precios"]]
    e = R["e2"]; x += [clp(e["p"]), clp(e["p2"]), pct(-e["caida"]), clp(e["dif"]), pct(e["tasa_impl"])]
    e = R["e3"]; x += [fmt(f["interes"], 1) for f in e["filas"]] + [fmt(f["flujo"], 1) for f in e["filas"]] + [fmt(e["p0"]), fmt(e["p1"])]
    e = R["e5"]; i = e["interp"]; x += [clp(e["p_r1"]), clp(e["p_r2"]), clp(i["van1"]), clp(-i["van2"]), pct(i["r"]), pct(e["ytm"])]
    e = R["e6"]; x += [pct(e["ys"], 4), fmt(e["p"]), fmt(e["p_mal"]), fmt(-e["error"]), pct(e["c_anual_equiv"])]
    e = R["e7"]; i = e["interp"]; x += [clp(e["cupon"]), clp(e["pk"]), clp(e["tenedor"][-1]), clp(i["van1"]), clp(-i["van2"]),
                                       pct(i["r"]), pct(e["hpr"]), clp(e["vf_cupones"]), clp(e["vf"]), pct(e["efectiva"])]
    e = R["e8"]; x += [fmt(e["p_ex"]), fmt(e["antes"]), fmt(e["despues"]), fmt(e["limpio_antes"])]
    for f in e["filas"]:
        x += [fmt(f["sucio"]), fmt(f["devengado"]), fmt(f["limpio"])]
    e = R["e9"]; x += [fmt(v) for v in e["vps"]] + [fmt(e["p"]), pct(e["ytm"]), fmt(e["ganancia"]), pct(e["ytm_mercado"])] + [fmt(c) for c in e["ceros"]]
    for f in R["e10"]:
        x += [fmt(f["p"]), pct(f["ytm"])]
    c = R["caso"]; i = c["interp"]
    x += [fmt(f["factor"], 6) for f in c["filas"]] + [fmt(f["vp"], 4) for f in c["filas"]] + [pct(f["spot"]) for f in c["filas"]]
    x += [fmt(c["precio"]), fmt(c["precio"], 4), pct(c["ytm"]), fmt(c["p_al_5"]), fmt(c["p_al_6"]), fmt(i["van1"]), fmt(-i["van2"]),
          pct(i["r"]), fmt(c["prima"]), pct(c["peso_final"], 1)]
    return x


def comparar_con_caso(R):
    """El precio y la YTM del texto tienen que ser los del script del caso."""
    C = caso.calcular()["u7"]
    assert abs(R["caso"]["precio"] - C["precio"]) < 1e-9 and abs(R["caso"]["ytm"] - C["ytm"]) < 1e-9
    assert abs(R["caso"]["chequeo_ytm"] - C["precio"]) < 1e-6


if __name__ == "__main__":
    R = resultados()
    comparar_con_caso(R)
    imprimir(R)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "07-bonos.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".").replace("\\,\\%", " %")
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
