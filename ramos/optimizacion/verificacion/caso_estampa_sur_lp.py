"""Caso integrador de Optimización · Estampa Sur decide su mezcla de producción.

El mismo taller ficticio de Gestión de Operaciones (y de la Valentina de Finanzas). Acá decide
cuánto producir de cada prenda en una semana con sus horas de estampado y planchado y su tinta.
Una sola fuente para las cifras que cruzan unidades.

    python caso_estampa_sur_lp.py          # imprime la cadena
    python caso_estampa_sur_lp.py --json   # la deja en caso_estampa_sur_lp.json

Todos los datos son originales de esta base.
"""
from pathlib import Path
import json, sys
import numpy as np
from scipy.optimize import linprog, minimize_scalar

sys.stdout.reconfigure(encoding="utf-8")

# ------------------------------------------------------------------ datos de una semana
PRODUCTOS = ["poleras básicas", "polerones", "poleras estampado doble", "bolsas", "gorros"]
MARGEN = [1_380, 3_940, 2_270, 960, 1_170]           # CLP por unidad
SEG_EST = [30, 90, 110, 20, 30]                      # segundos de estampado por unidad (Operaciones)
SEG_PLA = [20, 50, 30, 40, 15]                       # segundos de planchado por unidad (Operaciones)
TINTA_G = [12, 25, 22, 8, 6]                         # gramos de tinta por unidad
DEMANDA_MAX = [1_450, 520, 380, 860, 690]            # unidades por semana
CAP = {"estampado_s": 40 * 3600, "planchado_s": 18 * 3600, "tinta_g": 29_500}
HORA_EXTRA = 6_750                                   # CLP por hora extra (Operaciones, unidad 6)

# U2 · versión de dos productos para el método gráfico y el simplex a mano
DOS = {"productos": ["poleras básicas", "polerones"], "margen": [1_380, 3_940],
       "est": [30, 90], "pla": [20, 50], "cap_est": 30 * 3600, "cap_pla": 18 * 3600, "dem_polerones": 830}

# U3 · polerones con precio libre: demanda lineal q = a − b·p, costo variable c por unidad
U3 = {"a": 1_960, "b": 0.112, "costo": 6_150}

# U5 · cuatro semanas con inventario y tres tiendas
U5 = {"semanas": 4, "demanda_polerones": [380, 460, 610, 540], "costo_inventario": 210, "inv_max": 380,
      "tiendas": ["Concepción", "Chillán", "Los Ángeles"], "pedido_tiendas": [690, 410, 340],
      "costo_envio": [140, 390, 520]}   # CLP por unidad enviada desde el taller

# U6 · dos objetivos: margen y tinta (meta ambiental)
U6 = {"peso_margen": 0.7, "meta_margen": 3_900_000, "meta_tinta": 24_000}


# ------------------------------------------------------------------ cálculo
def resolver_mezcla(cap=CAP, margen=MARGEN):
    c = [-m for m in margen]
    A = [SEG_EST, SEG_PLA, TINTA_G]
    b = [cap["estampado_s"], cap["planchado_s"], cap["tinta_g"]]
    r = linprog(c, A_ub=A, b_ub=b, bounds=list(zip([0] * 5, DEMANDA_MAX)), method="highs")
    assert r.status == 0
    return r


def calcular():
    C = {"productos": PRODUCTOS}
    # U2 · dos productos (gráfico)
    d = DOS
    r2 = linprog([-m for m in d["margen"]], A_ub=[d["est"], d["pla"]], b_ub=[d["cap_est"], d["cap_pla"]],
                 bounds=[(0, None), (0, d["dem_polerones"])], method="highs")
    vertices = []
    import itertools
    lineas = [(d["est"], d["cap_est"]), (d["pla"], d["cap_pla"]), ([0, 1], d["dem_polerones"]), ([1, 0], 0), ([0, 1], 0)]
    for (a1, b1), (a2, b2) in itertools.combinations(lineas, 2):
        M = np.array([a1, a2], float)
        if abs(np.linalg.det(M)) < 1e-9:
            continue
        x = np.linalg.solve(M, [b1, b2])
        if (x >= -1e-6).all() and np.dot(d["est"], x) <= d["cap_est"] + 1e-6 and np.dot(d["pla"], x) <= d["cap_pla"] + 1e-6 \
                and x[1] <= d["dem_polerones"] + 1e-6:
            vertices.append((round(x[0], 4), round(x[1], 4), round(float(np.dot(d["margen"], x)), 2)))
    C["u2"] = {"x": list(r2.x), "z": -r2.fun, "vertices": sorted(set(vertices)),
               "duales": list(-r2.ineqlin.marginals)}
    # U3 · precio óptimo (no lineal, cóncavo)
    a, b, cv = U3["a"], U3["b"], U3["costo"]
    util = lambda p: (p - cv) * (a - b * p)
    p_opt = (a + b * cv) / (2 * b)
    num = minimize_scalar(lambda p: -util(p), bounds=(cv, a / b), method="bounded")
    C["u3"] = {"precio_optimo": p_opt, "cantidad": a - b * p_opt, "utilidad": util(p_opt),
               "precio_numerico": num.x, "segunda_derivada": -2 * b}
    # U4 · mezcla completa
    r4 = resolver_mezcla()
    holg = [CAP["estampado_s"] - np.dot(SEG_EST, r4.x), CAP["planchado_s"] - np.dot(SEG_PLA, r4.x),
            CAP["tinta_g"] - np.dot(TINTA_G, r4.x)]
    C["u4"] = {"x": list(r4.x), "z": -r4.fun, "holguras": holg,
               "precios_sombra": list(-r4.ineqlin.marginals),            # CLP por segundo, segundo, gramo
               "costo_reducido_cotas": list(-r4.upper.marginals)}
    # U12 · cuánto vale una hora extra de estampado y planchado
    ps = C["u4"]["precios_sombra"]
    C["u12"] = {"valor_hora_estampado": ps[0] * 3600, "valor_hora_planchado": ps[1] * 3600,
                "conviene_extra_estampado": ps[0] * 3600 > HORA_EXTRA,
                "conviene_extra_planchado": ps[1] * 3600 > HORA_EXTRA}
    # U5 · polerones en cuatro semanas: producción e inventario. La capacidad de 560 por semana es un
    # dato propio de esta unidad (no sale de la mezcla de la U4, que deja 520 por la demanda)
    T = U5["semanas"]; dem = U5["demanda_polerones"]
    cap_sem = 560
    # variables: x1..x4 producción, I1..I4 inventario; min costo inventario sujeto a balance
    c = [0] * T + [U5["costo_inventario"]] * T
    A_eq, b_eq = [], []
    for t in range(T):
        fila = [0] * (2 * T)
        fila[t] = 1
        fila[T + t] = -1
        if t > 0:
            fila[T + t - 1] = 1
        A_eq.append(fila); b_eq.append(dem[t])
    bounds = [(0, cap_sem)] * T + [(0, U5["inv_max"])] * T
    r5 = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    assert r5.status == 0
    # transporte a tiendas: producción de una semana de poleras básicas repartida
    envio = sum(p * k for p, k in zip(U5["pedido_tiendas"], U5["costo_envio"]))
    C["u5"] = {"produccion": list(r5.x[:T]), "inventario": list(r5.x[T:]), "costo": r5.fun,
               "cap_semana": cap_sem, "costo_envio_total": envio}
    # U6 · suma ponderada margen/tinta (normalizados por su mejor valor)
    z_max = -r4.fun
    r_t = linprog(TINTA_G, A_ub=[SEG_EST, SEG_PLA, [-m for m in MARGEN]],
                  b_ub=[CAP["estampado_s"], CAP["planchado_s"], -U6["meta_margen"]],
                  bounds=list(zip([0] * 5, DEMANDA_MAX)), method="highs")
    C["u6"] = {"z_max": z_max, "tinta_en_z_max": float(np.dot(TINTA_G, r4.x)),
               "tinta_min_con_meta_margen": r_t.fun if r_t.status == 0 else None,
               "x_meta": list(r_t.x) if r_t.status == 0 else None}
    return C


def limpio(v):
    """numpy → números de Python, para imprimir y guardar sin «np.float64»."""
    if isinstance(v, dict):
        return {k: limpio(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [limpio(x) for x in v]
    if isinstance(v, (np.floating, np.integer)):
        return float(v)
    if isinstance(v, np.bool_):
        return bool(v)
    return v


def imprimir(C):
    C = limpio(C)
    for k, v in C.items():
        print(f"== {k}")
        if isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, float):
                    vv = round(vv, 4)
                elif isinstance(vv, list):
                    vv = [round(x, 4) if isinstance(x, float) else x for x in vv]
                print(f"   {kk}: {vv}")
        else:
            print("  ", v)


if __name__ == "__main__":
    C = calcular()
    imprimir(C)
    if "--json" in sys.argv:
        Path(__file__).with_suffix(".json").write_text(json.dumps(limpio(C), ensure_ascii=False, indent=1),
                                                       encoding="utf-8")
