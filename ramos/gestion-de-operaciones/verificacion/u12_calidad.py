"""Unidad 12 · Calidad y control estadístico de procesos.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba
que cada resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto
queda sin respaldo.

    python u12_calidad.py            # imprime los resultados
    python u12_calidad.py --revisar  # además los busca en el .md

Los datos del caso integrador se generan con una semilla fija (SEMILLA_CASO); el .md los
imprime y --revisar comprueba que estén escritos igual.
"""
from math import sqrt, erf
from pathlib import Path
import random
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def clp(x):
    return "$" + fmt(x, 0)


def phi(z):
    """Distribución normal estándar acumulada."""
    return 0.5 * (1 + erf(z / sqrt(2)))


# Constantes de las cartas X̄ y R (tablas estándar, n = tamaño del subgrupo)
CONST = {  # n: (A2, D3, D4, d2)
    2: (1.880, 0, 3.267, 1.128),
    3: (1.023, 0, 2.574, 1.693),
    4: (0.729, 0, 2.282, 2.059),
    5: (0.577, 0, 2.114, 2.326),
    6: (0.483, 0, 2.004, 2.534),
    7: (0.419, 0.076, 1.924, 2.704),
    8: (0.373, 0.136, 1.864, 2.847),
    9: (0.337, 0.184, 1.816, 2.970),
    10: (0.308, 0.223, 1.777, 3.078),
}
assert CONST[5][0] == 0.577 and CONST[5][2] == 2.114 and CONST[5][1] == 0


def limites_xr(xbarbar, rbar, n):
    a2, d3, d4, _ = CONST[n]
    return {"xbarbar": xbarbar, "rbar": rbar,
            "lsc_x": xbarbar + a2 * rbar, "lic_x": xbarbar - a2 * rbar,
            "lsc_r": d4 * rbar, "lic_r": d3 * rbar}


def carta_xr(subgrupos):
    """subgrupos: lista de listas de igual largo → medias, rangos, límites y puntos fuera."""
    n = len(subgrupos[0])
    medias = [sum(s) / n for s in subgrupos]
    rangos = [max(s) - min(s) for s in subgrupos]
    L = limites_xr(sum(medias) / len(medias), sum(rangos) / len(rangos), n)
    fuera_x = [i + 1 for i, m in enumerate(medias) if m > L["lsc_x"] or m < L["lic_x"]]
    fuera_r = [i + 1 for i, r in enumerate(rangos) if r > L["lsc_r"] or r < L["lic_r"]]
    return {"n": n, "medias": medias, "rangos": rangos, **L, "fuera_x": fuera_x, "fuera_r": fuera_r}


def capacidad(media, sigma, lie, lse):
    cp = (lse - lie) / (6 * sigma)
    cps, cpi = (lse - media) / (3 * sigma), (media - lie) / (3 * sigma)
    fuera_sup = 1 - phi((lse - media) / sigma)
    fuera_inf = phi((lie - media) / sigma)
    return {"cp": cp, "cps": cps, "cpi": cpi, "cpk": min(cps, cpi),
            "fuera_sup": fuera_sup, "fuera_inf": fuera_inf, "fuera": fuera_sup + fuera_inf}


def carta_p(defectuosas, tamanos):
    pbar = sum(defectuosas) / sum(tamanos)
    filas = []
    for i, (d, n) in enumerate(zip(defectuosas, tamanos), start=1):
        s = sqrt(pbar * (1 - pbar) / n)
        lsc, lic = pbar + 3 * s, max(0.0, pbar - 3 * s)
        p = d / n
        filas.append({"i": i, "d": d, "n": n, "p": p, "lsc": lsc, "lic": lic, "fuera": p > lsc or p < lic})
    return pbar, filas


def carta_c(conteos):
    cbar = sum(conteos) / len(conteos)
    lsc, lic = cbar + 3 * sqrt(cbar), max(0.0, cbar - 3 * sqrt(cbar))
    return {"cbar": cbar, "lsc": lsc, "lic": lic, "lic_bruto": cbar - 3 * sqrt(cbar),
            "fuera": [i + 1 for i, c in enumerate(conteos) if c > lsc or c < lic]}


def reglas(puntos, lc, sigma):
    """Las cuatro reglas de la unidad. Devuelve {regla: [punto en que se dispara]} (base 1).
    R1: un punto fuera de ±3σ. R2: 7 seguidos del mismo lado de la línea central.
    R3: 6 seguidos subiendo o bajando. R4: 2 de 3 seguidos más allá de 2σ del mismo lado."""
    out = {"R1": [], "R2": [], "R3": [], "R4": []}
    for i, x in enumerate(puntos):
        if abs(x - lc) > 3 * sigma:
            out["R1"].append(i + 1)
        if i >= 6:
            v = puntos[i - 6:i + 1]
            if all(y > lc for y in v) or all(y < lc for y in v):
                out["R2"].append(i + 1)
        if i >= 5:
            v = puntos[i - 5:i + 1]
            if all(b > a for a, b in zip(v, v[1:])) or all(b < a for a, b in zip(v, v[1:])):
                out["R3"].append(i + 1)
        if i >= 2:
            v = puntos[i - 2:i + 1]
            if sum(y > lc + 2 * sigma for y in v) >= 2 or sum(y < lc - 2 * sigma for y in v) >= 2:
                out["R4"].append(i + 1)
    return out


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Ejemplo resuelto · envasadora de miel del valle del Itata, peso neto (g), 8 subgrupos de 4 frascos
EJ = [
    [503, 501, 505, 502],
    [504, 502, 500, 503],
    [502, 506, 503, 504],
    [501, 503, 502, 499],
    [505, 503, 504, 506],
    [502, 500, 503, 502],
    [504, 505, 502, 503],
    [503, 501, 504, 505],
]
EJ_LIE, EJ_LSE = 497, 509   # el frasco dice 500 g: el cliente acepta de 497 a 509 g

# Ejercicio 12.1 · costos de calidad de una panadería industrial de Chillán (CLP al mes)
E1 = [
    ("Capacitación en buenas prácticas de manufactura", "prevención", 380_000),
    ("Mantención preventiva de hornos", "prevención", 520_000),
    ("Inspección de masa y temperatura en cada turno", "evaluación", 640_000),
    ("Calibración de balanzas", "evaluación", 110_000),
    ("Pan desechado por quemado o crudo", "falla interna", 1_350_000),
    ("Reproceso de masa fuera de punto", "falla interna", 290_000),
    ("Devoluciones de supermercados", "falla externa", 1_920_000),
    ("Descuento comercial por reclamos", "falla externa", 450_000),
]
E1_VENTAS = 72_000_000

# Ejercicio 12.2 · pernos de una maestranza de Talcahuano, largo (mm), n = 5
E2 = {"xbarbar": 40.12, "rbar": 0.42, "n": 5,
      "nuevos": [(40.31, 0.38), (40.45, 0.51), (40.05, 0.95)]}  # (media, rango) de tres subgrupos nuevos

# Ejercicio 12.3 · tres máquinas de corte de una planta de envases (mm); especificación 120,00 ± 0,30
E3_LIE, E3_LSE = 119.70, 120.30
E3 = {"Máquina A": (120.00, 0.12), "Máquina B": (120.00, 0.07), "Máquina C": (120.15, 0.07)}

# Ejercicio 12.4 · fallas por rollo de 100 m de manguera de riego (Ñuble), 12 rollos
E4 = [4, 6, 3, 5, 7, 2, 5, 13, 4, 6, 3, 5]

# Ejercicio 12.5 · espesor de tablas en un aserradero de Los Ángeles (mm), 10 subgrupos de 4
E5 = [
    [25.1, 24.9, 25.0, 25.2],
    [24.8, 25.0, 25.1, 24.9],
    [25.0, 25.2, 24.9, 25.1],
    [25.1, 25.0, 24.8, 25.0],
    [24.9, 25.1, 25.0, 25.2],
    [25.0, 24.9, 25.1, 25.0],
    [24.4, 25.6, 25.3, 24.7],
    [25.2, 25.0, 25.1, 24.9],
    [24.9, 25.0, 24.8, 25.1],
    [25.0, 25.1, 25.0, 24.9],
]

# Ejercicio 12.6 · botellas mal etiquetadas en una viña del Maule, 15 días de 200 botellas
E6 = [6, 4, 8, 5, 7, 3, 6, 18, 5, 4, 7, 6, 5, 8, 4]
E6_N = 200

# Ejercicio 12.7 · medias de 20 subgrupos, línea central 50,0 y σ de la media 1,0
E7 = [50.4, 49.2, 51.1, 50.6, 48.9, 50.2, 50.8, 51.3, 50.5, 51.0,
      50.9, 51.6, 50.3, 49.8, 49.5, 49.1, 48.6, 48.2, 47.7, 49.3]
E7_LC, E7_S = 50.0, 1.0

# Ejercicio 12.8 · diámetro interior de bujes (mm), n = 5
E8 = {"xbarbar": 74.80, "rbar": 1.86, "n": 5, "lie": 72.0, "lse": 78.0}

# Ejercicio 12.9 · centro de despacho: pedidos con error de registro, n variable por día
E9_D = [12, 9, 15, 8, 22, 10, 11, 13, 9, 52]
E9_N = [300, 220, 410, 180, 380, 250, 290, 160, 240, 640]

# Ejercicio 12.10 · cecinas: peso de un paquete (g), 30.000 paquetes al mes
E10 = {"media": 251.2, "sigma": 0.9, "lie": 248.0, "lse": 253.0, "paquetes": 30_000,
       "costo_externo": 4_500,        # CLP por paquete fuera de norma que llega al cliente
       "inspeccion_unit": 35, "deteccion": 0.95, "costo_interno": 900,  # opción A
       "recentrar_fijo": 1_200_000}   # opción B: ajuste de la dosificadora, CLP al mes

# ---------------------------------------------------------------- caso integrador · Estampa Sur
# Desplazamiento del registro (mm): distancia entre el color 1 y el color 2 en el pecho de la polera.
# Objetivo 0,00 mm. El cliente (un club deportivo) acepta ±0,25 mm.
SEMILLA_CASO = 1009
CASO_LIE, CASO_LSE = -0.25, 0.25
CASO_N, CASO_K = 5, 20
CASO_MEDIA, CASO_SIGMA = 0.06, 0.08
CASO_ESPECIAL = 14            # el subgrupo 14 se tomó con el marco mal apretado
CASO_CORRIMIENTO = 0.15

# Carta p: 20 días, 150 prendas inspeccionadas por día
CASO_P_N, CASO_P_BASE = 150, 0.04
CASO_P_ESPECIAL = 9           # el día 9 entró un lote nuevo de tinta
CASO_P_ALTA = 0.15


def generar_caso(semilla=SEMILLA_CASO):
    rng = random.Random(semilla)
    subgrupos = []
    for k in range(1, CASO_K + 1):
        mu = CASO_MEDIA + (CASO_CORRIMIENTO if k == CASO_ESPECIAL else 0)
        subgrupos.append([round(rng.gauss(mu, CASO_SIGMA), 2) + 0.0 for _ in range(CASO_N)])
    defectuosas = []
    for d in range(1, CASO_K + 1):
        p = CASO_P_ALTA if d == CASO_P_ESPECIAL else CASO_P_BASE
        defectuosas.append(sum(rng.random() < p for _ in range(CASO_P_N)))
    return subgrupos, defectuosas


def caso_bueno(subgrupos, defectuosas):
    """Criterio con que se eligió la semilla: solo la causa especial sembrada sale de los límites."""
    c = carta_xr(subgrupos)
    if c["fuera_x"] != [CASO_ESPECIAL] or c["fuera_r"]:
        return False
    sin = carta_xr([s for i, s in enumerate(subgrupos, 1) if i != CASO_ESPECIAL])
    if sin["fuera_x"] or sin["fuera_r"]:
        return False
    _, fp = carta_p(defectuosas, [CASO_P_N] * CASO_K)
    if [f["i"] for f in fp if f["fuera"]] != [CASO_P_ESPECIAL]:
        return False
    d2 = [d for i, d in enumerate(defectuosas, 1) if i != CASO_P_ESPECIAL]
    _, fp2 = carta_p(d2, [CASO_P_N] * len(d2))
    return not any(f["fuera"] for f in fp2)


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # Ejemplo
    c = carta_xr(EJ)
    sigma = c["rbar"] / CONST[4][3]
    R["ej"] = c
    R["ej_sigma"] = sigma
    R["ej_cap"] = capacidad(c["xbarbar"], sigma, EJ_LIE, EJ_LSE)
    R["ej_cap_centrado"] = capacidad((EJ_LIE + EJ_LSE) / 2, sigma, EJ_LIE, EJ_LSE)

    # 12.1
    tot = {}
    for _, cat, m in E1:
        tot[cat] = tot.get(cat, 0) + m
    total = sum(tot.values())
    R["e1"] = {"tot": tot, "total": total, "pct_ventas": total / E1_VENTAS,
               "pct_falla": (tot["falla interna"] + tot["falla externa"]) / total,
               "pct_cat": {k: v / total for k, v in tot.items()}}

    # 12.2
    L = limites_xr(E2["xbarbar"], E2["rbar"], E2["n"])
    R["e2"] = (L, [(m, r, L["lic_x"] <= m <= L["lsc_x"], L["lic_r"] <= r <= L["lsc_r"]) for m, r in E2["nuevos"]])

    # 12.3
    R["e3"] = {k: capacidad(m, s, E3_LIE, E3_LSE) for k, (m, s) in E3.items()}

    # 12.4
    R["e4"] = carta_c(E4)
    R["e4_sin"] = carta_c([x for i, x in enumerate(E4, 1) if i not in R["e4"]["fuera"]])

    # 12.5
    R["e5"] = carta_xr(E5)
    R["e5_sin"] = carta_xr([s for i, s in enumerate(E5, 1) if i not in R["e5"]["fuera_r"] + R["e5"]["fuera_x"]])

    # 12.6
    R["e6"] = carta_p(E6, [E6_N] * len(E6))
    fuera6 = [f["i"] for f in R["e6"][1] if f["fuera"]]
    d6 = [d for i, d in enumerate(E6, 1) if i not in fuera6]
    R["e6_sin"] = carta_p(d6, [E6_N] * len(d6))
    R["e6_fuera"] = fuera6

    # 12.7
    R["e7"] = reglas(E7, E7_LC, E7_S)

    # 12.8
    s8 = E8["rbar"] / CONST[E8["n"]][3]
    R["e8_sigma"] = s8
    R["e8"] = capacidad(E8["xbarbar"], s8, E8["lie"], E8["lse"])
    centro = (E8["lie"] + E8["lse"]) / 2
    R["e8_centrado"] = capacidad(centro, s8, E8["lie"], E8["lse"])
    # σ necesaria para Cpk = 1,33 con la media actual (lado más cercano: LSE − media o media − LIE)
    dist = min(E8["lse"] - E8["xbarbar"], E8["xbarbar"] - E8["lie"])
    R["e8_sigma_133"] = dist / (3 * 1.33)
    R["e8_rbar_133"] = R["e8_sigma_133"] * CONST[E8["n"]][3]

    # 12.9
    R["e9"] = carta_p(E9_D, E9_N)

    # 12.10
    p = E10
    cap = capacidad(p["media"], p["sigma"], p["lie"], p["lse"])
    malos = round(cap["fuera"] * p["paquetes"])          # paquetes enteros, para que las sumas cuadren a mano
    sin_accion = malos * p["costo_externo"]
    a_insp = p["inspeccion_unit"] * p["paquetes"]
    detectados = round(malos * p["deteccion"])
    a_int = detectados * p["costo_interno"]
    a_ext = (malos - detectados) * p["costo_externo"]
    centro = (p["lie"] + p["lse"]) / 2
    capb = capacidad(centro, p["sigma"], p["lie"], p["lse"])
    malos_b = round(capb["fuera"] * p["paquetes"])
    b_ext = malos_b * p["costo_externo"]
    # (c) σ con que el recentrado, sin inspección, iguala el costo de la opción A (bisección)
    lo, hi = 0.1, p["sigma"]
    for _ in range(100):
        mid = (lo + hi) / 2
        costo = p["recentrar_fijo"] + capacidad(centro, mid, p["lie"], p["lse"])["fuera"] * p["paquetes"] * p["costo_externo"]
        lo, hi = (mid, hi) if costo < a_insp + a_int + a_ext else (lo, mid)
    R["e10_sigma_empate"] = lo
    R["e10"] = {"cap": cap, "malos": malos, "detectados": detectados, "sin_accion": sin_accion,
                "a_insp": a_insp, "a_int": a_int, "a_ext": a_ext, "a_total": a_insp + a_int + a_ext,
                "capb": capb, "malos_b": malos_b, "b_ext": b_ext, "b_total": p["recentrar_fijo"] + b_ext}

    # Caso
    sub, defe = generar_caso()
    assert caso_bueno(sub, defe), "la semilla ya no cumple el criterio del caso"
    R["caso_sub"], R["caso_def"] = sub, defe
    cx = carta_xr(sub)
    cx_sin = carta_xr([s for i, s in enumerate(sub, 1) if i != CASO_ESPECIAL])
    R["caso_x"], R["caso_x_sin"] = cx, cx_sin
    sg = cx_sin["rbar"] / CONST[CASO_N][3]
    R["caso_sigma"] = sg
    R["caso_cap"] = capacidad(cx_sin["xbarbar"], sg, CASO_LIE, CASO_LSE)
    R["caso_cap_centrado"] = capacidad(0.0, sg, CASO_LIE, CASO_LSE)
    R["caso_sigma_133"] = CASO_LSE / (3 * 1.33)            # ya centrado en 0: σ que da Cp = Cpk = 1,33
    R["caso_rbar_133"] = R["caso_sigma_133"] * CONST[CASO_N][3]
    R["caso_baja_sigma"] = 1 - R["caso_sigma_133"] / sg
    R["caso_reglas"] = reglas(cx_sin["medias"], cx_sin["xbarbar"], (cx_sin["lsc_x"] - cx_sin["xbarbar"]) / 3)
    R["caso_p"] = carta_p(defe, [CASO_P_N] * CASO_K)
    d2 = [d for i, d in enumerate(defe, 1) if i != CASO_P_ESPECIAL]
    R["caso_p_sin"] = carta_p(d2, [CASO_P_N] * len(d2))
    return R


def imprimir(R):
    c = R["ej"]
    print("== Ejemplo miel")
    for i, (s, m, r) in enumerate(zip(EJ, c["medias"], c["rangos"]), 1):
        print(f"   {i}: {s} media {fmt(m, 2)} rango {r}")
    print(f"   X̄̄ {fmt(c['xbarbar'], 3)} R̄ {fmt(c['rbar'], 3)} | X̄: {fmt(c['lic_x'], 2)}–{fmt(c['lsc_x'], 2)} | R: {fmt(c['lic_r'], 2)}–{fmt(c['lsc_r'], 2)} | fuera {c['fuera_x']} {c['fuera_r']}")
    k = R["ej_cap"]
    print(f"   σ {fmt(R['ej_sigma'], 3)} Cp {fmt(k['cp'], 2)} Cps {fmt(k['cps'], 2)} Cpi {fmt(k['cpi'], 2)} Cpk {fmt(k['cpk'], 2)} fuera {pct(k['fuera'], 2)} (sup {pct(k['fuera_sup'], 3)} inf {pct(k['fuera_inf'], 4)})")
    print(f"   centrado: Cpk {fmt(R['ej_cap_centrado']['cpk'], 2)} fuera {pct(R['ej_cap_centrado']['fuera'], 3)}")
    e = R["e1"]
    print("== 12.1", {k: clp(v) for k, v in e["tot"].items()}, "total", clp(e["total"]), "% ventas", pct(e["pct_ventas"]), "% fallas", pct(e["pct_falla"]),
          {k: pct(v) for k, v in e["pct_cat"].items()})
    L, ev = R["e2"]
    print(f"== 12.2 X̄ {fmt(L['lic_x'], 2)}–{fmt(L['lsc_x'], 2)} R {fmt(L['lic_r'], 2)}–{fmt(L['lsc_r'], 2)}", ev)
    print("== 12.3"); [print(f"   {k}: Cp {fmt(v['cp'], 2)} Cpk {fmt(v['cpk'], 2)} fuera {pct(v['fuera'], 3)}") for k, v in R["e3"].items()]
    c4 = R["e4"]; print(f"== 12.4 c̄ {fmt(c4['cbar'], 2)} LSC {fmt(c4['lsc'], 2)} LIC bruto {fmt(c4['lic_bruto'], 2)} fuera {c4['fuera']} | sin: c̄ {fmt(R['e4_sin']['cbar'], 2)} LSC {fmt(R['e4_sin']['lsc'], 2)} LIC {fmt(R['e4_sin']['lic_bruto'], 2)}")
    for nombre in ("e5", "e5_sin"):
        c5 = R[nombre]
        print(f"== 12.5 {nombre}: medias {[fmt(m, 3) for m in c5['medias']]} rangos {[fmt(r, 1) for r in c5['rangos']]}")
        print(f"     X̄̄ {fmt(c5['xbarbar'], 3)} R̄ {fmt(c5['rbar'], 3)} X̄ {fmt(c5['lic_x'], 2)}–{fmt(c5['lsc_x'], 2)} R {fmt(c5['lic_r'], 2)}–{fmt(c5['lsc_r'], 2)} fuera {c5['fuera_x']} {c5['fuera_r']}")
    pb, f6 = R["e6"]; print(f"== 12.6 p̄ {fmt(pb, 4)} LSC {fmt(f6[0]['lsc'], 4)} LIC {fmt(f6[0]['lic'], 4)} fuera {R['e6_fuera']}")
    pb2, f62 = R["e6_sin"]; print(f"     sin: p̄ {fmt(pb2, 4)} LSC {fmt(f62[0]['lsc'], 4)} LIC {fmt(f62[0]['lic'], 4)}")
    print("== 12.7", R["e7"])
    k = R["e8"]; print(f"== 12.8 σ {fmt(R['e8_sigma'], 3)} Cp {fmt(k['cp'], 2)} Cps {fmt(k['cps'], 2)} Cpi {fmt(k['cpi'], 2)} Cpk {fmt(k['cpk'], 2)} fuera {pct(k['fuera'], 3)} sup {pct(k['fuera_sup'], 3)} inf {pct(k['fuera_inf'], 3)}")
    print(f"     centrado: Cpk {fmt(R['e8_centrado']['cpk'], 2)} fuera {pct(R['e8_centrado']['fuera'], 3)} | σ para 1,33: {fmt(R['e8_sigma_133'], 3)} R̄ {fmt(R['e8_rbar_133'], 2)}")
    pb9, f9 = R["e9"]; print(f"== 12.9 p̄ {fmt(pb9, 4)}")
    for f in f9:
        print(f"     día {f['i']}: p {fmt(f['p'], 4)} LSC {fmt(f['lsc'], 4)} LIC {fmt(f['lic'], 4)} {'FUERA' if f['fuera'] else ''}")
    e = R["e10"]
    print(f"== 12.10 fuera {pct(e['cap']['fuera'], 2)} Cpk {fmt(e['cap']['cpk'], 2)} malos {fmt(e['malos'], 0)} sin acción {clp(e['sin_accion'])}")
    print(f"     A: detectados {e['detectados']} insp {clp(e['a_insp'])} int {clp(e['a_int'])} ext {clp(e['a_ext'])} total {clp(e['a_total'])}")
    print(f"     B: Cpk {fmt(e['capb']['cpk'], 2)} fuera {pct(e['capb']['fuera'], 3)} malos {fmt(e['malos_b'], 0)} ext {clp(e['b_ext'])} total {clp(e['b_total'])}")
    print(f"     (c) σ de empate {fmt(R['e10_sigma_empate'], 3)} → Cp {fmt((E10['lse'] - E10['lie']) / (6 * R['e10_sigma_empate']), 2)}")
    print("== Caso · subgrupos")
    cx = R["caso_x"]
    for i, (s, m, r) in enumerate(zip(R["caso_sub"], cx["medias"], cx["rangos"]), 1):
        print(f"   {i:2}: {' · '.join(fmt(x, 2) for x in s)} | media {fmt(m, 3)} rango {fmt(r, 2)}")
    for nombre in ("caso_x", "caso_x_sin"):
        c = R[nombre]
        print(f"   {nombre}: X̄̄ {fmt(c['xbarbar'], 3)} R̄ {fmt(c['rbar'], 3)} X̄ {fmt(c['lic_x'], 3)}–{fmt(c['lsc_x'], 3)} R {fmt(c['lic_r'], 3)}–{fmt(c['lsc_r'], 3)} fuera {c['fuera_x']} {c['fuera_r']}")
    k = R["caso_cap"]
    print(f"   σ {fmt(R['caso_sigma'], 4)} Cp {fmt(k['cp'], 2)} Cps {fmt(k['cps'], 2)} Cpi {fmt(k['cpi'], 2)} Cpk {fmt(k['cpk'], 2)} fuera {pct(k['fuera'], 3)} | centrado Cpk {fmt(R['caso_cap_centrado']['cpk'], 2)} fuera {pct(R['caso_cap_centrado']['fuera'], 4)}")
    print("   reglas sin el 14:", R["caso_reglas"])
    print(f"   para Cpk 1,33 centrado: σ {fmt(R['caso_sigma_133'], 3)} R̄ {fmt(R['caso_rbar_133'], 3)} baja {pct(R['caso_baja_sigma'], 0)}")
    pb, fp = R["caso_p"]
    print(f"   carta p: defectuosas {R['caso_def']} p̄ {fmt(pb, 4)} LSC {fmt(fp[0]['lsc'], 4)} LIC {fmt(fp[0]['lic'], 4)} fuera {[f['i'] for f in fp if f['fuera']]}")
    print("     p por día", [fmt(f["p"], 3) for f in fp])
    pb2, fp2 = R["caso_p_sin"]
    print(f"   sin día 9: p̄ {fmt(pb2, 4)} LSC {fmt(fp2[0]['lsc'], 4)} LIC {fmt(fp2[0]['lic'], 4)}")


# ---------------------------------------------------------------- revisión contra el texto

def fila(*celdas):
    return "| " + " | ".join(celdas) + " |"


def esperados(R):
    """Cadenas que el .md tiene que contener tal cual (resultados y filas de datos)."""
    e = []
    c = R["ej"]
    for i, (s, m, r) in enumerate(zip(EJ, c["medias"], c["rangos"]), 1):
        e.append(fila(str(i), *map(str, s), fmt(m, 2), str(r)))
    e += [fmt(c["xbarbar"], 3), fmt(c["rbar"], 3), fmt(c["lsc_x"], 2), fmt(c["lic_x"], 2), fmt(c["lsc_r"], 2)]
    e += [fmt(R["ej_sigma"], 3)]
    k = R["ej_cap"]
    e += [fmt(k["cp"], 2), fmt(k["cps"], 2), fmt(k["cpi"], 2), pct(k["fuera"], 2), fmt(R["ej_cap_centrado"]["cpk"], 2)]
    # 12.1
    e1 = R["e1"]
    e += [clp(v) for v in e1["tot"].values()] + [clp(e1["total"]), pct(e1["pct_ventas"]), pct(e1["pct_falla"])]
    e += [pct(v) for v in e1["pct_cat"].values()]
    e += [fila(nombre, clp(m)) for nombre, _, m in E1]
    # 12.2
    L, _ = R["e2"]
    e += [fmt(L["lsc_x"], 2), fmt(L["lic_x"], 2), fmt(L["lsc_r"], 2)]
    # 12.3
    for v in R["e3"].values():
        e += [fmt(v["cp"], 2), fmt(v["cpk"], 2)]
    # 12.4
    c4 = R["e4"]
    e += [fila("Fallas", *map(str, E4))]
    e += [fmt(c4["cbar"], 2), fmt(c4["lsc"], 2), fmt(R["e4_sin"]["cbar"], 2), fmt(R["e4_sin"]["lsc"], 2)]
    # 12.5
    e += [fila(str(i), *(fmt(x, 1) for x in s)) for i, s in enumerate(E5, 1)]
    for nombre in ("e5", "e5_sin"):
        c5 = R[nombre]
        e += [fmt(c5["xbarbar"], 3), fmt(c5["rbar"], 3), fmt(c5["lsc_x"], 2), fmt(c5["lic_x"], 2), fmt(c5["lsc_r"], 2)]
    # 12.6
    pb, f6 = R["e6"]; pb2, f62 = R["e6_sin"]
    e += [fila("Mal etiquetadas", *map(str, E6))]
    e += [fmt(pb, 4), fmt(f6[0]["lsc"], 4), fmt(pb2, 4), fmt(f62[0]["lsc"], 4)]
    # 12.7
    e += [fila("Media", *(fmt(x, 1) for x in E7[:10])), fila("Media", *(fmt(x, 1) for x in E7[10:]))]
    # 12.8
    k = R["e8"]
    e += [fmt(R["e8_sigma"], 3), fmt(k["cp"], 2), fmt(k["cpk"], 2), pct(k["fuera"], 3), fmt(R["e8_sigma_133"], 3), fmt(R["e8_rbar_133"], 2)]
    # 12.9
    pb9, f9 = R["e9"]
    e += [fmt(pb9, 4)]
    e += [fila(str(f["i"]), fmt(f["n"], 0), str(f["d"])) for f in f9]
    e += [fila(str(f["i"]), fmt(f["p"], 4), fmt(f["lic"], 4), fmt(f["lsc"], 4)) for f in f9]
    # 12.10
    t = R["e10"]
    e += [pct(t["cap"]["fuera"], 2), fmt(t["cap"]["cpk"], 2), clp(t["sin_accion"]), clp(t["a_insp"]), clp(t["a_int"]), clp(t["a_ext"]),
          clp(t["a_total"]), pct(t["capb"]["fuera"], 3), clp(t["b_ext"]), clp(t["b_total"]), fmt(R["e10_sigma_empate"], 3)]
    # caso: datos generados, medias, rangos y resultados
    cx = R["caso_x"]
    for i, (s, m, r) in enumerate(zip(R["caso_sub"], cx["medias"], cx["rangos"]), 1):
        e.append(fila(str(i), *(fmt(x, 2) for x in s), fmt(m, 3), fmt(r, 2)))
    for nombre in ("caso_x", "caso_x_sin"):
        c = R[nombre]
        e += [fmt(c["xbarbar"], 3), fmt(c["rbar"], 3), fmt(c["lsc_x"], 3), fmt(c["lic_x"], 3), fmt(c["lsc_r"], 3)]
    e += [fmt(sum(cx["medias"]), 3), fmt(sum(cx["rangos"]), 2), fmt(R["caso_x_sin"]["rbar"], 4),
          fmt(sum(R["caso_x_sin"]["medias"]), 3), fmt(sum(R["caso_x_sin"]["rangos"]), 2)]
    k = R["caso_cap"]
    e += [fmt(R["caso_sigma"], 4), fmt(k["cp"], 2), fmt(k["cps"], 2), fmt(k["cpi"], 2), pct(k["fuera"], 3),
          fmt(R["caso_cap_centrado"]["cpk"], 2), pct(R["caso_cap_centrado"]["fuera"], 3),
          fmt(R["caso_sigma_133"], 3), fmt(R["caso_rbar_133"], 3), pct(R["caso_baja_sigma"], 0)]
    pb, fp = R["caso_p"]; pb2, fp2 = R["caso_p_sin"]
    e += [fila(str(f["i"]), str(f["d"]), fmt(f["p"], 3)) for f in fp]
    e += [fmt(pb, 4), fmt(fp[0]["lsc"], 4), fmt(pb2, 4), fmt(fp2[0]["lsc"], 4)]
    e += [f"semilla {SEMILLA_CASO}"]
    return e


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "12-calidad.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",")   # en LaTeX la coma decimal se escribe {,}; es la misma cifra
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
