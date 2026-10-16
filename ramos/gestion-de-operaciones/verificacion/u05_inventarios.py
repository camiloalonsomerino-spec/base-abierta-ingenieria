"""Unidad 5 · Inventarios.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba
que cada resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto
queda sin respaldo. La pieza del caso integrador se toma de caso_estampa_sur.py.

    python u05_inventarios.py            # imprime los resultados
    python u05_inventarios.py --revisar  # además los busca en el .md
"""
from math import sqrt, ceil
from pathlib import Path
from statistics import NormalDist
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))  # con -P la carpeta del script no entra sola
import caso_estampa_sur as caso  # noqa: E402

N01 = NormalDist()

# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def clp(x):
    return "$" + fmt(x, 0)


def eoq(D, S, H):
    return sqrt(2 * D * S / H)


def costos(D, S, H, Q, C=0):
    pedir, mantener = D / Q * S, Q / 2 * H
    return {"pedir": pedir, "mantener": mantener, "inventario": pedir + mantener,
            "compra": D * C, "total": pedir + mantener + D * C}


def z_de(ns):
    return N01.inv_cdf(ns)


def perdida(z):
    """Función de pérdida normal estándar L(z) = φ(z) − z·(1 − Φ(z))."""
    return N01.pdf(z) - z * (1 - N01.cdf(z))


def sigma_plazo(sd, L, d=0.0, sL=0.0):
    """Desviación de la demanda durante el plazo, con plazo variable si sL > 0."""
    return sqrt(L * sd ** 2 + d ** 2 * sL ** 2)


def descuentos(D, S, i, tramos):
    """tramos: [(mínimo del tramo, precio)] → por tramo: Q*, Q factible, costo total.
    Descuento a todas las unidades: si Q* cae bajo el mínimo, se sube al mínimo; si cae
    sobre el tramo, ese precio no se alcanza con Q* y se descarta su EOQ."""
    filas = []
    for k, (minimo, precio) in enumerate(tramos):
        maximo = tramos[k + 1][0] - 1 if k + 1 < len(tramos) else float("inf")
        H = i * precio
        q = eoq(D, S, H)
        if q > maximo:
            filas.append({"min": minimo, "precio": precio, "H": H, "Qopt": q, "Q": None, "c": None})
            continue
        Q = max(q, minimo)
        filas.append({"min": minimo, "precio": precio, "H": H, "Qopt": q, "Q": Q, "c": costos(D, S, H, Q, precio)})
    return filas


def newsvendor_normal(mu, sigma, cu, co):
    rc = cu / (cu + co)
    z = z_de(rc)
    return {"cu": cu, "co": co, "rc": rc, "z": z, "Q": mu + z * sigma}


def newsvendor_discreto(dist, p, c, v):
    """dist: {demanda: probabilidad}. Devuelve razón crítica, acumulada y ganancia esperada por Q."""
    cu, co = p - c, c - v
    rc = cu / (cu + co)
    acum, F = {}, 0.0
    for x in sorted(dist):
        F += dist[x]
        acum[x] = F
    ganancia = {}
    for Q in sorted(dist):
        g = 0.0
        for x, pr in dist.items():
            vend = min(Q, x)
            g += pr * (p * vend + v * (Q - vend) - c * Q)
        ganancia[Q] = g
    q_rc = min(x for x in sorted(dist) if acum[x] >= rc - 1e-12)
    return {"cu": cu, "co": co, "rc": rc, "acum": acum, "ganancia": ganancia, "Q": q_rc}


def simular(demandas, inv0, s, politica, plazo_sem=1, costo_pedido=0, h_sem=0, c_falta=0):
    """Revisión al cierre de cada semana. Si la posición (físico + en tránsito) ≤ s, se pide:
    politica = ("S", S) pide hasta S; politica = ("Q", Q) pide Q fijo.
    El pedido hecho al cierre de la semana t llega al inicio de la semana t + 1 + plazo_sem.
    La demanda que no se atiende se pierde."""
    fisico, transito, filas = inv0, {}, []
    for t, dem in enumerate(demandas, start=1):
        llega = transito.pop(t, 0)
        fisico += llega
        vend = min(fisico, dem)
        falta = dem - vend
        fisico -= vend
        posicion = fisico + sum(transito.values())
        pide = 0
        if posicion <= s:
            pide = politica[1] - posicion if politica[0] == "S" else politica[1]
            transito[t + 1 + plazo_sem] = transito.get(t + 1 + plazo_sem, 0) + pide
        filas.append({"sem": t, "llega": llega, "dem": dem, "vende": vend, "falta": falta,
                      "fisico": fisico, "posicion": posicion, "pide": pide})
    n_ped = sum(f["pide"] > 0 for f in filas)
    faltas = sum(f["falta"] for f in filas)
    inv_prom = sum(f["fisico"] for f in filas) / len(filas)
    costo = n_ped * costo_pedido + sum(f["fisico"] for f in filas) * h_sem + faltas * c_falta
    return {"filas": filas, "pedidos": n_ped, "faltas": faltas, "inv_prom": inv_prom, "costo": costo}


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Ejemplo resuelto · ferretería de San Carlos, sacos de cemento de 25 kg
EJ = dict(D=10_080, dias=288, S=36_000, C=5_200, i=0.18, L=3, sd=9, ns=0.95,
          Q_red=880,                        # 22 pallets de 40 sacos
          desc_min=1_800, desc=0.03,        # 3 % desde 45 pallets
          sL=1)                             # variación del plazo (días) para la parte final

# Robustez del EOQ (sección 2)
ROB_FACTOR, SENS_DEM = 1.5, 0.8

# Newsvendor · vivero de Chillán, pinos de Navidad
NV = dict(c=9_000, p=22_000, v=1_500, mu=420, sigma=70)

# 5.1 · imprenta de Talca, resmas de papel
E1 = dict(D=3_600, dias=245, S=18_000, C=4_300, i=0.22, alza=1.44)
# 5.2 · distribuidora de Los Ángeles, bidones de aceite (plazo normal y máximo, días)
E2 = dict(d=48, L=7, Lmax=11, Q=450)
# 5.3 · farmacia de hospital, suero fisiológico
E3 = dict(d=64, sd=15, L=9, H=350, niveles=(0.90, 0.95, 0.99))
# 5.4 · club deportivo, bufandas para la final (normal)
E4 = dict(c=6_500, p=15_000, v=2_000, mu=600, sigma=150, v_devolucion=5_000)
# 5.5 · hotel de Pucón, bidones de aceite de oliva, descuento a todas las unidades
E5 = dict(D=1_440, S=24_000, i=0.30, tramos=[(1, 14_000), (500, 13_650), (1_000, 13_370)])
# 5.6 · planta de alimentos, envases, plazo variable
E6 = dict(d=140, sd=35, L=8, sL=2, ns=0.97, L_local=3, sL_local=0.5)
# 5.7 · farmacia de barrio, pañales, revisión periódica
E7 = dict(d=55, sd=12, R=7, L=3, ns=0.95, fisico=240, transito=0, R2=14)
# 5.8 · florería, ramos de rosas para el Día de los Enamorados (discreto)
E8 = dict(c=7_000, p=18_000, v=1_000, dist={100: 0.10, 150: 0.20, 200: 0.30, 250: 0.25, 300: 0.15})
# 5.9 · bodega de repuestos, (s,S) contra (s,Q), revisión semanal
E9 = dict(demandas=[46, 58, 39, 71, 52, 44, 63, 49], inv0=150, s=80, S=200, Q=120, s2=110,
          costo_pedido=30_000, h_sem=400, c_falta=5_000)
# 5.10 · distribuidora de fertilizante de Linares
E10 = dict(D=7_800, dias=312, S=52_000, C=11_500, i=0.16, camion=500, sd=8, L=10,
           niveles=(0.90, 0.95, 0.99))


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # ---- ejemplo resuelto
    e = EJ
    H = e["i"] * e["C"]
    q = eoq(e["D"], e["S"], H)
    N = e["D"] / q
    d = e["D"] / e["dias"]
    z = z_de(e["ns"])
    sdl = sigma_plazo(e["sd"], e["L"])
    ss = z * sdl
    C2 = e["C"] * (1 - e["desc"])
    H2 = e["i"] * C2
    sdl_v = sigma_plazo(e["sd"], e["L"], d, e["sL"])
    R["ej"] = {
        "H": H, "Q": q, "N": N, "T": e["dias"] / N, "d": d,
        "c_opt": costos(e["D"], e["S"], H, q, e["C"]),
        "c_red": costos(e["D"], e["S"], H, e["Q_red"], e["C"]),
        "C2": C2, "H2": H2, "Q2": eoq(e["D"], e["S"], H2),
        "c_desc": costos(e["D"], e["S"], H2, e["desc_min"], C2),
        "cob_desc": e["desc_min"] / d,
        "z": z, "sdl": sdl, "ss": ss, "dL": d * e["L"], "r": d * e["L"] + ss,
        "sdl_v": sdl_v, "ss_v": z * sdl_v, "r_v": d * e["L"] + z * sdl_v,
    }
    R["ej"]["ahorro"] = R["ej"]["c_red"]["total"] - R["ej"]["c_desc"]["total"]
    R["ej"]["ahorro_compra"] = R["ej"]["c_red"]["compra"] - R["ej"]["c_desc"]["compra"]
    R["ej"]["alza_inv"] = R["ej"]["c_desc"]["inventario"] - R["ej"]["c_red"]["inventario"]

    # ---- robustez y sensibilidad
    R["rob"] = 0.5 * (ROB_FACTOR + 1 / ROB_FACTOR)
    R["sens"] = sqrt(SENS_DEM)

    # ---- newsvendor de la teoría
    R["nv"] = newsvendor_normal(NV["mu"], NV["sigma"], NV["p"] - NV["c"], NV["c"] - NV["v"])

    # ---- 5.1
    e = E1
    H = e["i"] * e["C"]; q = eoq(e["D"], e["S"], H); N = e["D"] / q
    R["e1"] = {"H": H, "Q": q, "N": N, "T": e["dias"] / N, "c": costos(e["D"], e["S"], H, q, e["C"]),
               "Q_alza": q * sqrt(e["alza"])}
    # ---- 5.2
    e = E2
    R["e2"] = {"r0": e["d"] * e["L"], "ss": (e["Lmax"] - e["L"]) * e["d"],
               "r": e["d"] * e["Lmax"], "en_camino": e["d"] * e["L"] / e["Q"]}
    # ---- 5.3
    e = E3
    sdl = sigma_plazo(e["sd"], e["L"])
    filas = []
    for ns in e["niveles"]:
        z = z_de(ns); ss = z * sdl
        filas.append({"ns": ns, "z": z, "ss": ss, "r": e["d"] * e["L"] + ss, "costo": ss * e["H"]})
    R["e3"] = {"sdl": sdl, "dL": e["d"] * e["L"], "filas": filas,
               "alza_90_99": filas[2]["costo"] / filas[0]["costo"] - 1}
    # ---- 5.4
    e = E4
    R["e4"] = {"base": newsvendor_normal(e["mu"], e["sigma"], e["p"] - e["c"], e["c"] - e["v"]),
               "dev": newsvendor_normal(e["mu"], e["sigma"], e["p"] - e["c"], e["c"] - e["v_devolucion"])}
    # ---- 5.5
    e = E5
    tr = descuentos(e["D"], e["S"], e["i"], e["tramos"])
    mejor = min((f for f in tr if f["c"]), key=lambda f: f["c"]["total"])
    # precio máximo del tramo 2 para que pedir 500 empate con el mejor del tramo 1
    t1 = tr[0]["c"]["total"]
    m2 = e["tramos"][1][0]
    p_max = (t1 - e["D"] / m2 * e["S"]) / (e["D"] + m2 / 2 * e["i"])
    R["e5"] = {"tramos": tr, "mejor": mejor, "p_max": p_max, "desc_min": 1 - p_max / e["tramos"][0][1]}
    # ---- 5.6
    e = E6
    z = z_de(e["ns"])
    a = sigma_plazo(e["sd"], e["L"]); b = sigma_plazo(e["sd"], e["L"], e["d"], e["sL"])
    c = sigma_plazo(e["sd"], e["L_local"], e["d"], e["sL_local"])
    R["e6"] = {"z": z, "a": (a, z * a, e["d"] * e["L"] + z * a),
               "b": (b, z * b, e["d"] * e["L"] + z * b),
               "c": (c, z * c, e["d"] * e["L_local"] + z * c)}
    # ---- 5.7
    e = E7
    z = z_de(e["ns"])
    def nivel_max(R_):
        sd_ = e["sd"] * sqrt(R_ + e["L"])
        return e["d"] * (R_ + e["L"]), z * sd_, e["d"] * (R_ + e["L"]) + z * sd_
    base, ss, S = nivel_max(e["R"])
    S_ent = ceil(S)
    R["e7"] = {"z": z, "base": base, "ss": ss, "S": S, "S_ent": S_ent,
               "pedir": S_ent - e["fisico"] - e["transito"],
               "ss_cont": z * e["sd"] * sqrt(e["L"]), "R2": nivel_max(e["R2"])}
    # ---- 5.8
    e = E8
    R["e8"] = newsvendor_discreto(e["dist"], e["p"], e["c"], e["v"])
    # ---- 5.9
    e = E9
    kw = dict(costo_pedido=e["costo_pedido"], h_sem=e["h_sem"], c_falta=e["c_falta"])
    R["e9"] = {"sS": simular(e["demandas"], e["inv0"], e["s"], ("S", e["S"]), **kw),
               "sQ": simular(e["demandas"], e["inv0"], e["s"], ("Q", e["Q"]), **kw),
               "sS2": simular(e["demandas"], e["inv0"], e["s2"], ("S", e["S"]), **kw),
               "media": sum(e["demandas"]) / len(e["demandas"])}
    sS, sS2 = R["e9"]["sS"], R["e9"]["sS2"]
    # costo por unidad faltante desde el cual s = 110 sale más barato que s = 80
    R["e9"]["c_falta_eq"] = (sS2["costo"] - (sS["costo"] - sS["faltas"] * e["c_falta"])) / sS["faltas"]
    # ---- 5.10
    e = E10
    H = e["i"] * e["C"]; q = eoq(e["D"], e["S"], H); d = e["D"] / e["dias"]
    ratio = lambda Q: 0.5 * (Q / q + q / Q)
    sdl = sigma_plazo(e["sd"], e["L"])
    filas = []
    for ns in e["niveles"]:
        z = z_de(ns); ss = z * sdl
        esp = sdl * perdida(z)
        filas.append({"ns": ns, "z": z, "ss": ss, "r": d * e["L"] + ss, "costo_ss": ss * H,
                      "Lz": perdida(z), "falta_ciclo": esp, "fill": 1 - esp / e["camion"],
                      "falta_anual": esp * e["D"] / e["camion"]})
    R["e10"] = {"H": H, "Q": q, "d": d, "r500": ratio(e["camion"]), "r1000": ratio(2 * e["camion"]),
                "c_opt": costos(e["D"], e["S"], H, q), "c500": costos(e["D"], e["S"], H, e["camion"]),
                "c1000": costos(e["D"], e["S"], H, 2 * e["camion"]),
                "sdl": sdl, "dL": d * e["L"], "filas": filas, "N500": e["D"] / e["camion"]}

    # ---- caso integrador (desde la fuente única del caso)
    C = caso.calcular()
    u5, P, pron = C["u5"], caso.U5, C["u4"]["pronostico_redondeado"]
    mezcla = caso.PRODUCTOS["poleras básicas"]["mezcla"]
    Qc = u5["EOQ_redondeado"]
    R["caso"] = {
        "pron": pron[:2], "prom2": sum(pron[:2]) / 2, "mezcla": mezcla, "mensual": mezcla * sum(pron[:2]) / 2,
        "D": u5["demanda_anual"], "H": u5["H"], "EOQ": u5["EOQ"], "Q": Qc,
        "N": u5["demanda_anual"] / Qc, "T": P["dias_habiles"] * Qc / u5["demanda_anual"],
        "c_opt": costos(u5["demanda_anual"], P["costo_pedido"], u5["H"], u5["EOQ"]),
        "c_red": costos(u5["demanda_anual"], P["costo_pedido"], u5["H"], Qc),
        "d": u5["demanda_diaria"], "dL": u5["demanda_diaria"] * P["plazo_dias"],
        "sdl": P["desv_diaria"] * sqrt(P["plazo_dias"]), "ss": u5["stock_seguridad"],
        "r": u5["punto_reorden"], "ns": N01.cdf(P["z"]), "costo_ss": u5["stock_seguridad"] * u5["H"],
        "ss_ent": ceil(u5["stock_seguridad"]), "r_ent": ceil(u5["punto_reorden"]),
    }
    return R


def imprimir(R):
    e = R["ej"]
    print("== Ejemplo resuelto (cemento)")
    print(f"   H {fmt(e['H'],0)} | Q* {fmt(e['Q'])} | N {fmt(e['N'],2)} | T {fmt(e['T'])} d | d {fmt(e['d'],0)}/día")
    for k in ("c_opt", "c_red", "c_desc"):
        c = e[k]; print(f"   {k}: pedir {clp(c['pedir'])} mantener {clp(c['mantener'])} inv {clp(c['inventario'])} compra {clp(c['compra'])} total {clp(c['total'])}")
    print(f"   desc: C {clp(e['C2'])} H {fmt(e['H2'],2)} Q* {fmt(e['Q2'])} | ahorro {clp(e['ahorro'])} (compra {clp(e['ahorro_compra'])}, alza inv {clp(e['alza_inv'])}) | cobertura {fmt(e['cob_desc'])} d")
    print(f"   z {fmt(e['z'],3)} | σL {fmt(e['sdl'],2)} | SS {fmt(e['ss'])} | dL {fmt(e['dL'],0)} | r {fmt(e['r'])}")
    print(f"   plazo variable: σ {fmt(e['sdl_v'],2)} SS {fmt(e['ss_v'])} r {fmt(e['r_v'])}")
    print(f"== robustez ×{ROB_FACTOR}: {fmt(R['rob'],4)} | demanda ×{SENS_DEM}: Q × {fmt(R['sens'],4)}")
    nv = R["nv"]; print(f"== newsvendor pinos: Cu {nv['cu']} Co {nv['co']} RC {fmt(nv['rc'],3)} z {fmt(nv['z'],3)} Q {fmt(nv['Q'])}")
    e = R["e1"]; c = e["c"]
    print(f"== 5.1 H {fmt(e['H'],0)} Q* {fmt(e['Q'])} N {fmt(e['N'],2)} T {fmt(e['T'])} | pedir {clp(c['pedir'])} mant {clp(c['mantener'])} inv {clp(c['inventario'])} compra {clp(c['compra'])} total {clp(c['total'])} | Q con alza {fmt(e['Q_alza'])}")
    print("== 5.2", R["e2"])
    e = R["e3"]; print(f"== 5.3 σL {fmt(e['sdl'],1)} dL {e['dL']} alza 90→99 {pct(e['alza_90_99'])}")
    for f in e["filas"]:
        print(f"     {pct(f['ns'],0)} z {fmt(f['z'],3)} SS {fmt(f['ss'])} r {fmt(f['r'])} costo {clp(f['costo'])}")
    for k, v in R["e4"].items():
        print(f"== 5.4 {k}: Cu {v['cu']} Co {v['co']} RC {fmt(v['rc'],3)} z {fmt(v['z'],3)} Q {fmt(v['Q'])}")
    e = R["e5"]; print("== 5.5")
    for f in e["tramos"]:
        c = f["c"]
        print(f"     desde {f['min']} precio {f['precio']} H {fmt(f['H'],0)} Q* {fmt(f['Qopt'])} Q {f['Q'] and fmt(f['Q'])}", "" if not c else
              f"compra {clp(c['compra'])} pedir {clp(c['pedir'])} mant {clp(c['mantener'])} total {clp(c['total'])}")
    print(f"     mejor desde {e['mejor']['min']} | precio máx tramo 2 {fmt(e['p_max'])} | descuento mínimo {pct(e['desc_min'],2)}")
    e = R["e6"]; print(f"== 5.6 z {fmt(e['z'],3)}", {k: tuple(fmt(x) for x in e[k]) for k in 'abc'})
    e = R["e7"]; print(f"== 5.7 z {fmt(e['z'],3)} base {e['base']} SS {fmt(e['ss'])} S {fmt(e['S'])} → {e['S_ent']} pedir {e['pedir']} | SS continua {fmt(e['ss_cont'])} | R=14 {tuple(fmt(x) for x in e['R2'])}")
    e = R["e8"]; print(f"== 5.8 Cu {e['cu']} Co {e['co']} RC {fmt(e['rc'],3)} Q {e['Q']}")
    for q in e["ganancia"]:
        print(f"     Q {q}: F {fmt(e['acum'][q],2)} ganancia esperada {clp(e['ganancia'][q])}")
    print("== 5.9 media semanal", fmt(R["e9"]["media"], 2), "| faltante de equilibrio", clp(R["e9"]["c_falta_eq"]))
    for k, v in ((k, v) for k, v in R["e9"].items() if k in ("sS", "sQ", "sS2")):
        print(f"== 5.9 {k}: pedidos {v['pedidos']} faltas {v['faltas']} inv prom {fmt(v['inv_prom'])} costo {clp(v['costo'])}")
        for f in v["filas"]:
            print("     ", f)
    e = R["e10"]
    print(f"== 5.10 H {fmt(e['H'],0)} Q* {fmt(e['Q'])} d {fmt(e['d'],0)} | 500 {pct(e['r500']-1,1)} 1000 {pct(e['r1000']-1,1)} | inv opt {clp(e['c_opt']['inventario'])} 500 {clp(e['c500']['inventario'])} 1000 {clp(e['c1000']['inventario'])}")
    print(f"     σL {fmt(e['sdl'],2)} dL {fmt(e['dL'],0)}")
    for f in e["filas"]:
        print(f"     {pct(f['ns'],0)} z {fmt(f['z'],3)} SS {fmt(f['ss'])} r {fmt(f['r'])} costo SS {clp(f['costo_ss'])} L(z) {fmt(f['Lz'],4)} falta/ciclo {fmt(f['falta_ciclo'],2)} fill {pct(f['fill'],2)} falta/año {fmt(f['falta_anual'],1)}")
    c = R["caso"]
    print("== caso", {k: (v if isinstance(v, (list, dict)) else round(v, 3)) for k, v in c.items()})


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    """Cadenas que el .md tiene que contener tal cual."""
    x = []
    e = R["ej"]
    x += [fmt(e["Q"]), fmt(e["N"], 2), fmt(e["T"]), clp(e["c_opt"]["pedir"]), clp(e["c_opt"]["inventario"]),
          clp(e["c_opt"]["total"]), clp(e["c_red"]["inventario"]), clp(e["c_red"]["total"]),
          clp(e["C2"]), fmt(e["H2"], 2), fmt(e["Q2"]), clp(e["c_desc"]["pedir"]), clp(e["c_desc"]["mantener"]),
          clp(e["c_desc"]["compra"]), clp(e["c_desc"]["total"]), clp(e["ahorro"]), clp(e["ahorro_compra"]),
          clp(e["alza_inv"]), fmt(e["cob_desc"]), fmt(e["z"], 3), fmt(e["sdl"], 2), fmt(e["ss"]), fmt(e["r"]),
          fmt(e["sdl_v"], 2), fmt(e["ss_v"]), fmt(e["r_v"])]
    x += [fmt(R["rob"], 3), pct(1 - R["sens"])]
    nv = R["nv"]; x += [fmt(nv["rc"], 3), fmt(nv["z"], 3), fmt(nv["Q"])]
    e = R["e1"]; x += [fmt(e["Q"]), fmt(e["N"], 2), fmt(e["T"]), clp(e["c"]["pedir"]), clp(e["c"]["inventario"]),
                       clp(e["c"]["total"]), fmt(e["Q_alza"])]
    e = R["e2"]; x += [f"{e['r0']}", f"{e['ss']}", f"{e['r']}", fmt(e["en_camino"], 2)]
    e = R["e3"]; x += [fmt(e["sdl"], 0), pct(e["alza_90_99"])]
    for f in e["filas"]:
        x += [fmt(f["z"], 3), fmt(f["ss"]), fmt(f["r"]), clp(f["costo"])]
    for v in R["e4"].values():
        x += [fmt(v["rc"], 3), fmt(v["z"], 3), fmt(v["Q"])]
    e = R["e5"]
    for f in e["tramos"]:
        x += [fmt(f["Qopt"])]
        if f["c"]:
            x += [clp(f["c"]["total"])]
    x += [clp(e["p_max"]), pct(e["desc_min"], 2)]
    e = R["e6"]; x += [fmt(e["z"], 3)] + [fmt(v) for k in "abc" for v in e[k]]
    e = R["e7"]; x += [fmt(e["ss"]), fmt(e["S"]), str(e["S_ent"]), str(e["pedir"]), fmt(e["ss_cont"]), fmt(e["R2"][2])]
    e = R["e8"]; x += [fmt(e["rc"], 3)] + [clp(g) for g in e["ganancia"].values()] + [fmt(F, 2) for F in e["acum"].values()]
    for k in ("sS", "sQ", "sS2"):
        v = R["e9"][k]; x += [clp(v["costo"]), fmt(v["inv_prom"])]
    x += [fmt(R["e9"]["media"], 2), fmt(2 * R["e9"]["media"], 1)]
    x += [clp(R["e9"]["c_falta_eq"])]
    e = R["e10"]; x += [fmt(e["Q"]), pct(e["r500"] - 1), pct(e["r1000"] - 1), fmt(e["sdl"], 2), fmt(e["N500"]),
                        clp(e["c_opt"]["inventario"]), clp(e["c500"]["inventario"]), clp(e["c1000"]["inventario"])]
    x += [fmt(f["falta_anual"]) for f in e["filas"]]
    for f in e["filas"]:
        x += [fmt(f["ss"]), fmt(f["r"]), clp(f["costo_ss"]), fmt(f["falta_ciclo"], 2), pct(f["fill"], 2)]
    c = R["caso"]
    x += [fmt(c["prom2"], 0), fmt(c["mensual"], 0), fmt(c["D"], 0), fmt(c["EOQ"]), fmt(c["Q"], 0), fmt(c["N"], 2),
          fmt(c["T"]), clp(c["c_opt"]["inventario"]), clp(c["c_red"]["inventario"]), fmt(c["d"], 2),
          fmt(c["dL"], 1), fmt(c["sdl"], 2), fmt(c["ss"], 1), fmt(c["r"], 1), pct(c["ns"], 1), clp(c["costo_ss"]),
          str(c["r_ent"])]
    return x


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "05-inventarios.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",")  # en LaTeX la coma decimal se escribe {,} y se ve como coma
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
