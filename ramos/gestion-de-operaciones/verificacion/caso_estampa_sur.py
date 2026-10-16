"""Caso integrador · Estampa Sur.

Una sola fuente para la cadena de cálculo que recorre el ramo. Cada unidad toma de acá sus datos de
partida y sus resultados, así que una cifra del caso se cambia en un solo lugar.

    python caso_estampa_sur.py          # imprime toda la cadena
    python caso_estampa_sur.py --json   # la deja en caso_estampa_sur.json para los otros scripts

Todos los datos son originales de esta base (no vienen de ningún libro ni curso).
"""
from math import sqrt, ceil
from pathlib import Path
import json, sys

sys.stdout.reconfigure(encoding="utf-8")

# ------------------------------------------------------------------ la empresa
EMPRESA = {
    "nombre": "Estampa Sur",
    "rubro": "taller de serigrafía textil, Región del Biobío",
    "centros": ["estampado", "planchado y doblado"],
}

PRODUCTOS = {  # mezcla de la familia, lote fijo, segundos por unidad en cada centro
    "poleras básicas":         {"mezcla": 0.40, "lote": 720, "est_s": 30,  "pla_s": 20},
    "polerones":               {"mezcla": 0.15, "lote": 360, "est_s": 90,  "pla_s": 50},
    "poleras estampado doble": {"mezcla": 0.15, "lote": 360, "est_s": 110, "pla_s": 30},
    "bolsas":                  {"mezcla": 0.18, "lote": 540, "est_s": 20,  "pla_s": 40},
    "gorros":                  {"mezcla": 0.12, "lote": 480, "est_s": 30,  "pla_s": 15},
}

# ------------------------------------------------------------------ unidad 3 · capacidad del estampado
U3 = {
    "dias_semana": 5, "turnos": 1, "horas_turno": 9,      # capacidad de diseño: 45 h/semana
    "capacidad_efectiva_h": 40,                            # descontando cambios de marco y limpieza
    "horas_reales_ultima_semana": 34,                      # lo que de verdad estampó
}

# ------------------------------------------------------------------ unidad 4 · demanda histórica (unidades de la familia)
HISTORIA = [4120, 4310, 4260, 4480, 4550, 4490, 4700, 4820, 4760, 4950, 5080, 5010,
            5190, 5260, 5340, 5300, 5480, 5590, 5560, 5720, 5810, 5790, 5950, 6040]
ALFA, BETA = 0.3, 0.2

# ------------------------------------------------------------------ unidad 5 · polera lisa (insumo de las poleras básicas)
U5 = {"costo_pedido": 45_000, "precio": 2_400, "tasa_mantener": 0.25,   # CLP por pedido, CLP por polera, % anual
      "dias_habiles": 250, "plazo_dias": 5, "desv_diaria": 22, "z": 1.65}

# ------------------------------------------------------------------ unidad 6 · plan agregado
U6 = {
    "dias": [20, 19, 22, 21, 20, 22],
    "hh_por_unidad": 0.12, "horas_dia": 8, "trabajadores_iniciales": 4,
    "inventario_inicial": 510,          # igual a la suma de los inventarios por producto de U7
    "costo_contratar": 380_000, "costo_despedir": 500_000,
    "costo_mantener": 300, "costo_faltante": 1_200,        # CLP por unidad y mes
    "salario_hora": 4_500, "hora_extra": 6_750, "tope_extra": 0.20,
}

# ------------------------------------------------------------------ unidad 7 · programa maestro
U7 = {"inventario_inicial": {"poleras básicas": 80, "polerones": 120, "poleras estampado doble": 0,
                             "bolsas": 260, "gorros": 50},   # suman 510, el inventario inicial de U6
      "pedido_en_curso": {"poleras básicas": 720, "polerones": 0, "poleras estampado doble": 360,
                          "bolsas": 0, "gorros": 480}}

U9 = {"capacidad_planchado_h": 18}   # una persona media jornada; el estampado usa la efectiva de U3

# ------------------------------------------------------------------ unidad 8 · lista de materiales de las poleras básicas
LDM = {
    "polera lisa": {"por_unidad": 1,     "plazo": 1, "politica": "cantidad fija", "inventario": 900},
    "tinta (kg)":  {"por_unidad": 0.015, "plazo": 2, "politica": "múltiplos de 5", "inventario": 12},
    "etiqueta":    {"por_unidad": 1,     "plazo": 1, "politica": "lote a lote",   "inventario": 0},
}


# ================================================================== cálculo
def holt(serie, a, b):
    nivel, tend = serie[0], serie[1] - serie[0]
    filas = []
    for t, d in enumerate(serie[1:], start=2):
        prono = nivel + tend
        nuevo_nivel = a * d + (1 - a) * (nivel + tend)
        tend = b * (nuevo_nivel - nivel) + (1 - b) * tend
        nivel = nuevo_nivel
        filas.append((t, d, prono, abs(d - prono)))
    mad = sum(f[3] for f in filas) / len(filas)
    futuro = [nivel + k * tend for k in range(1, 7)]
    return filas, mad, nivel, tend, futuro


def eoq(demanda_anual, s, h):
    return sqrt(2 * demanda_anual * s / h)


def plan_mixto(demanda, p):
    """Estrategia mixta: dotación fija todo el horizonte y horas extra para cubrir lo que falte.
    Se prueba cada dotación posible y se queda la de menor costo total."""
    cap_trab_mes = [d * p["horas_dia"] / p["hh_por_unidad"] for d in p["dias"]]
    mejor = None
    for w in range(2, 10):
        inv, costo, filas = p["inventario_inicial"], 0, []
        cambio = w - p["trabajadores_iniciales"]
        costo_cambio = cambio * p["costo_contratar"] if cambio > 0 else -cambio * p["costo_despedir"]
        for dem, cap in zip(demanda, cap_trab_mes):
            regular = round(w * cap)
            extra = min(max(0, dem - inv - regular), round(p["tope_extra"] * regular))
            prod = regular + extra
            inv = inv + prod - dem
            fila = {"demanda": dem, "regular": regular, "extra": extra, "produccion": prod,
                    "inventario_final": inv,
                    "sueldos": w * cap * p["hh_por_unidad"] * p["salario_hora"],
                    "costo_extra": extra * p["hh_por_unidad"] * p["hora_extra"],
                    "mantener": max(inv, 0) * p["costo_mantener"],
                    "faltante": max(-inv, 0) * p["costo_faltante"]}
            costo += fila["sueldos"] + fila["costo_extra"] + fila["mantener"] + fila["faltante"]
            filas.append(fila)
        total = costo + costo_cambio
        if mejor is None or total < mejor[3]:
            mejor = (w, costo_cambio, filas, total)
    return mejor


def mps_corte_ajuste(mensual, mezcla, lote, ii, pc, semanas_mes=4):
    nb = [m * mezcla / semanas_mes for m in mensual for _ in range(semanas_mes)]
    ie, filas = ii, []
    for i, n in enumerate(nb):
        pci = pc if i == 0 else 0
        nn = n - ie - pci
        mps = lote if nn >= 0 else 0
        sig = -nn if nn < 0 else lote - nn
        filas.append({"sem": i + 1, "NB": n, "IE": ie, "PC": pci, "NN": nn, "MPS": mps})
        ie = sig
    return filas


def mrp(brutos, inventario, plazo, politica, recepciones=None):
    recepciones = recepciones or [0] * len(brutos)
    disp, filas = inventario, []
    lib = [0] * len(brutos)
    vencidas = []
    for t, rb in enumerate(brutos):
        disp += recepciones[t]
        neto = max(0, rb - disp)
        rp = 0
        if neto > 0:
            if isinstance(politica, (int, float)):
                rp = ceil(neto / politica) * politica
            elif politica == "lote a lote":
                rp = neto
            elif politica.startswith("múltiplos de"):
                m = int(politica.split()[-1])
                rp = ceil(neto / m) * m
        disp = disp + rp - rb
        if rp and t - plazo >= 0:
            lib[t - plazo] = rp
        elif rp:  # la liberación caería antes de la semana 1: es una orden vencida, no se pierde
            vencidas.append({"recepcion_sem": t + 1, "cantidad": rp})
        filas.append({"sem": t + 1, "bruto": rb, "neto": neto, "recepcion_planeada": rp, "disponible": disp})
    for f, l in zip(filas, lib):
        f["liberacion"] = l
    if vencidas:
        print(f"AVISO: {len(vencidas)} orden(es) vencida(s) en el MRP: {vencidas}")
        filas[0]["vencidas"] = vencidas
    return filas


def calcular():
    C = {"empresa": EMPRESA, "productos": PRODUCTOS}
    # U3
    diseno = U3["dias_semana"] * U3["turnos"] * U3["horas_turno"]
    C["u3"] = {"capacidad_diseno_h": diseno, "capacidad_efectiva_h": U3["capacidad_efectiva_h"],
               "utilizacion": U3["horas_reales_ultima_semana"] / diseno,
               "eficiencia": U3["horas_reales_ultima_semana"] / U3["capacidad_efectiva_h"]}
    # U4
    filas, mad, nivel, tend, futuro = holt(HISTORIA, ALFA, BETA)
    pron = [round(f, -2) for f in futuro]
    C["u4"] = {"mad": mad, "nivel": nivel, "tendencia": tend, "pronostico_6m": futuro, "pronostico_redondeado": pron}
    # U5
    dem_anual = 12 * PRODUCTOS["poleras básicas"]["mezcla"] * sum(pron[:2]) / 2
    h = U5["precio"] * U5["tasa_mantener"]
    q = eoq(dem_anual, U5["costo_pedido"], h)
    q_red = round(q, -2)
    d_dia = dem_anual / U5["dias_habiles"]
    ss = U5["z"] * U5["desv_diaria"] * sqrt(U5["plazo_dias"])
    C["u5"] = {"demanda_anual": dem_anual, "H": h, "EOQ": q, "EOQ_redondeado": q_red,
               "demanda_diaria": d_dia, "stock_seguridad": ss,
               "punto_reorden": d_dia * U5["plazo_dias"] + ss}
    # U6
    req, costo_cambio, plan, costo = plan_mixto(pron, U6)
    C["u6"] = {"trabajadores": req, "costo_cambio_personal": costo_cambio, "plan": plan, "costo_total": costo}
    # U7: los dos primeros meses del plan agregado
    assert sum(U7["inventario_inicial"].values()) == U6["inventario_inicial"], "U6 y U7 parten de inventarios distintos"
    meses = [plan[0]["produccion"], plan[1]["produccion"]]
    C["u7"] = {p: mps_corte_ajuste(meses, d["mezcla"], d["lote"], U7["inventario_inicial"][p],
                                   U7["pedido_en_curso"][p]) for p, d in PRODUCTOS.items()}
    # U9: carga por centro
    carga = []
    for s in range(8):
        est = sum(C["u7"][p][s]["MPS"] * d["est_s"] for p, d in PRODUCTOS.items()) / 3600
        pla = sum(C["u7"][p][s]["MPS"] * d["pla_s"] for p, d in PRODUCTOS.items()) / 3600
        carga.append({"sem": s + 1, "estampado_h": est, "planchado_h": pla})
    C["u9"] = carga
    # U8: componentes de las poleras básicas
    mps_pb = [f["MPS"] for f in C["u7"]["poleras básicas"]]
    C["u8"] = {}
    for comp, d in LDM.items():
        brutos = [x * d["por_unidad"] for x in mps_pb]
        pol = q_red if d["politica"] == "cantidad fija" else d["politica"]
        C["u8"][comp] = mrp(brutos, d["inventario"], d["plazo"], pol)
    # U10: lotes de la semana 6 con sus horas
    C["u10"] = {p: {"MPS": C["u7"][p][5]["MPS"], "est_h": C["u7"][p][5]["MPS"] * d["est_s"] / 3600,
                    "pla_h": C["u7"][p][5]["MPS"] * d["pla_s"] / 3600} for p, d in PRODUCTOS.items()}
    return C


def imprimir(C):
    print("U3", C["u3"])
    print("U4 MAD", round(C["u4"]["mad"], 1), "pronóstico", [round(x) for x in C["u4"]["pronostico_6m"]], "→", C["u4"]["pronostico_redondeado"])
    print("U5", {k: round(v, 1) for k, v in C["u5"].items()})
    print("U6 trabajadores", C["u6"]["trabajadores"], "cambio", C["u6"]["costo_cambio_personal"], "costo", round(C["u6"]["costo_total"]))
    for f in C["u6"]["plan"]:
        print("    ", f)
    for p, filas in C["u7"].items():
        print("U7", p, [f["MPS"] for f in filas], "NN", [round(f["NN"], 1) for f in filas])
    for c in C["u9"]:
        print("U9", c)
    for comp, filas in C["u8"].items():
        print("U8", comp, [(f["bruto"], f["recepcion_planeada"], f["liberacion"], round(f["disponible"], 2)) for f in filas])
    print("U10", C["u10"])


if __name__ == "__main__":
    C = calcular()
    imprimir(C)
    objetivo = {"poleras básicas": (6, 4), "polerones": (9, 5), "poleras estampado doble": (11, 3), "bolsas": (3, 6), "gorros": (4, 2)}
    ok = all((C["u10"][p]["est_h"], C["u10"][p]["pla_h"]) == objetivo[p] for p in objetivo)
    print("\nSemana 6 calza con la unidad 10:", "SÍ" if ok else "NO")
    if "--json" in sys.argv:
        Path(__file__).with_suffix(".json").write_text(json.dumps(C, ensure_ascii=False, indent=1), encoding="utf-8")
