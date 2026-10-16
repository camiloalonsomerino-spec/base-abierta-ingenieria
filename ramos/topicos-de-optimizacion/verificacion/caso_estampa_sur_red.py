"""Caso integrador de Tópicos de Optimización · Estampa Sur crece.

El mismo taller ficticio de Gestión de Operaciones, Finanzas y Optimización. Ahora sus decisiones
son enteras y binarias (lotes, lanzamientos, una segunda máquina, una bodega) y su problema es una
red: seis tiendas, caminos entre ellas, una ruta de reparto. Las tiendas, sus nombres y todas las
distancias son ficticias.

    python caso_estampa_sur_red.py          # imprime la cadena
    python caso_estampa_sur_red.py --json   # la deja en caso_estampa_sur_red.json
"""
from itertools import combinations, permutations
from pathlib import Path
import json, math, random, sys

import networkx as nx
import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds

sys.stdout.reconfigure(encoding="utf-8")

# ------------------------------------------------------------------ la red (ficticia)
NODOS = ["Taller", "Centro", "Puerto", "Lagos", "Valle", "Costa", "Cerro", "Cruce"]
CAMINOS = {  # km, tiempo de camión en minutos aproximado = km × 1,5
    ("Taller", "Centro"): 7, ("Taller", "Cruce"): 11, ("Taller", "Costa"): 16,
    ("Centro", "Puerto"): 9, ("Centro", "Cruce"): 6, ("Centro", "Lagos"): 14,
    ("Puerto", "Costa"): 8, ("Puerto", "Lagos"): 12,
    ("Lagos", "Valle"): 10, ("Lagos", "Cruce"): 13,
    ("Valle", "Cruce"): 9, ("Valle", "Cerro"): 7,
    ("Cerro", "Cruce"): 12, ("Cerro", "Costa"): 23,
}
CAPACIDAD_DIARIA = {  # cajas por día que admite cada tramo (para flujo máximo, sentido Taller → tiendas)
    ("Taller", "Centro"): 60, ("Taller", "Cruce"): 45, ("Taller", "Costa"): 25,
    ("Centro", "Puerto"): 30, ("Centro", "Cruce"): 20, ("Centro", "Lagos"): 25,
    ("Puerto", "Costa"): 15, ("Puerto", "Lagos"): 20,
    ("Cruce", "Lagos"): 25, ("Cruce", "Valle"): 35, ("Cruce", "Cerro"): 20,
    ("Lagos", "Valle"): 15, ("Valle", "Cerro"): 25, ("Costa", "Cerro"): 10,
}
TIENDAS = ["Centro", "Puerto", "Lagos", "Valle", "Costa", "Cerro"]

# U1 · lotes enteros: la mezcla de Optimización U4 en cajas de 24 prendas
MEZCLA_LP = [833.75, 520.0, 0.0, 294.375, 690.0]     # resultado continuo de Optimización U4
MARGEN = [1_380, 3_940, 2_270, 960, 1_170]
SEG_EST = [30, 90, 110, 20, 30]; SEG_PLA = [20, 50, 30, 40, 15]; TINTA_G = [12, 25, 22, 8, 6]
DEMANDA_MAX = [1_450, 520, 380, 860, 690]
CAP = [40 * 3600, 18 * 3600, 29_500]
CAJA = 24

# U2 · seis productos nuevos para lanzar (mochila con dependencias)
NUEVOS = {  # inversión de lanzamiento (CLP), margen anual esperado (CLP)
    "chaquetas":   (2_850_000, 4_120_000), "buzos":     (1_960_000, 2_740_000),
    "parches":     (  430_000,   790_000), "banderines": (  610_000,   980_000),
    "toallas":     (1_380_000, 1_890_000), "delantales": (  920_000, 1_430_000),
}
PRESUPUESTO_LANZAMIENTO = 5_200_000

# U3 · segunda máquina (costo fijo) y lote mínimo
U3 = {"costo_fijo_maquina": 1_650_000, "margen_extra_por_caja": 18_400, "cajas_max_maquina": 136,
      "lote_minimo_cajas": 40}

# U9 · transporte: dos talleres (el actual y uno nuevo en Cruce) a cuatro tiendas grandes
OFERTA = {"Taller": 320, "Cruce": 216}                       # cajas por semana
DEMANDA_T = {"Centro": 156, "Lagos": 118, "Valle": 138, "Costa": 124}
# costo por caja (CLP) = 95 por km de ruta más corta (se calcula)

# U10 · asignación: cuatro operarios, cuatro máquinas (minutos por lote)
ASIGNACION = {
    "Ana":    {"pulpo 6 brazos": 38, "pulpo 4 brazos": 44, "térmica": 29, "bordadora": 51},
    "Bruno":  {"pulpo 6 brazos": 42, "pulpo 4 brazos": 37, "térmica": 33, "bordadora": 47},
    "Daniela":{"pulpo 6 brazos": 35, "pulpo 4 brazos": 41, "térmica": 36, "bordadora": 43},
    "Esteban":{"pulpo 6 brazos": 46, "pulpo 4 brazos": 39, "térmica": 31, "bordadora": 49},
}

SEMILLA = 2026


# ------------------------------------------------------------------ cálculo
def grafo():
    G = nx.Graph()
    for (a, b), d in CAMINOS.items():
        G.add_edge(a, b, km=d)
    return G


def calcular():
    C = {}
    G = grafo()
    # U1 · redondear contra entero (en cajas)
    cajas_lp = [x / CAJA for x in MEZCLA_LP]
    redondeo = [math.floor(c) for c in cajas_lp]
    A = np.array([SEG_EST, SEG_PLA, TINTA_G]) * CAJA
    c = -np.array(MARGEN) * CAJA
    res = milp(c, constraints=LinearConstraint(A, ub=CAP), integrality=np.ones(5),
               bounds=Bounds(np.zeros(5), np.floor(np.array(DEMANDA_MAX) / CAJA)))
    C["u1"] = {"cajas_lp": cajas_lp, "redondeo_abajo": redondeo,
               "margen_redondeo": float(np.dot(MARGEN, redondeo) * CAJA),
               "cajas_entero": [int(round(v)) for v in res.x], "margen_entero": float(-res.fun),
               "margen_lp": float(np.dot(MARGEN, MEZCLA_LP))}
    # U2 · mochila de lanzamientos: parches exige banderines; chaquetas y buzos se excluyen
    nombres = list(NUEVOS)
    mejor = None
    for k in range(len(nombres) + 1):
        for sub in combinations(nombres, k):
            s = set(sub)
            if "parches" in s and "banderines" not in s: continue
            if "chaquetas" in s and "buzos" in s: continue
            inv = sum(NUEVOS[n][0] for n in s)
            if inv > PRESUPUESTO_LANZAMIENTO: continue
            val = sum(NUEVOS[n][1] - NUEVOS[n][0] for n in s)
            if mejor is None or val > mejor[0]:
                mejor = (val, sorted(s), inv)
    C["u2"] = {"valor_neto": mejor[0], "lanza": mejor[1], "inversion": mejor[2]}
    # U3 · costo fijo: comprar la segunda máquina solo si las cajas extra pagan el costo fijo
    u = U3
    def utilidad(y, q):
        return u["margen_extra_por_caja"] * q - u["costo_fijo_maquina"] * y
    opciones = [(utilidad(0, 0), 0, 0)] + [(utilidad(1, q), 1, q) for q in range(u["lote_minimo_cajas"], u["cajas_max_maquina"] + 1)]
    best = max(opciones)
    C["u3"] = {"utilidad": best[0], "compra": best[1], "cajas": best[2],
               "cajas_equilibrio": u["costo_fijo_maquina"] / u["margen_extra_por_caja"]}
    # U4 · ruta del camión (vendedor viajero) con distancias de ruta más corta
    D = dict(nx.all_pairs_dijkstra_path_length(G, weight="km"))
    paradas = TIENDAS
    mejor_r = None
    for perm in permutations(paradas):
        ruta = ("Taller",) + perm + ("Taller",)
        km = sum(D[a][b] for a, b in zip(ruta, ruta[1:]))
        if mejor_r is None or km < mejor_r[0]:
            mejor_r = (km, list(ruta))
    C["u4"] = {"tsp_km": mejor_r[0], "tsp_ruta": mejor_r[1]}
    # U7 · árbol de expansión mínima (enlaces de radio entre tiendas y taller)
    T = nx.minimum_spanning_tree(G, weight="km", algorithm="kruskal")
    C["u7"] = {"mst_km": sum(d["km"] for *_, d in T.edges(data=True)),
               "mst_aristas": sorted([sorted([a, b]) for a, b in T.edges()])}
    # U8 · ruta más corta y flujo máximo
    dist, caminos = nx.single_source_dijkstra(G, "Taller", weight="km")
    H = nx.DiGraph()
    for (a, b), cap in CAPACIDAD_DIARIA.items():
        H.add_edge(a, b, capacity=cap)
    flujo, _ = nx.maximum_flow(H, "Taller", "Cerro")
    corte = nx.minimum_cut(H, "Taller", "Cerro")
    C["u8"] = {"dijkstra": {n: dist[n] for n in NODOS}, "camino_a_Cerro": caminos["Cerro"],
               "flujo_max_a_Cerro": flujo, "corte_min_valor": corte[0]}
    # U9 · transporte con costo 95 CLP por km
    o, d = list(OFERTA), list(DEMANDA_T)
    costo = [[95 * D[i][j] for j in d] for i in o]
    cvec = [costo[i][j] for i in range(len(o)) for j in range(len(d))]
    A_ub = [[1 if k // len(d) == i else 0 for k in range(len(cvec))] for i in range(len(o))]
    A_eq = [[1 if k % len(d) == j else 0 for k in range(len(cvec))] for j in range(len(d))]
    r = linprog(cvec, A_ub=A_ub, b_ub=[OFERTA[i] for i in o], A_eq=A_eq, b_eq=[DEMANDA_T[j] for j in d],
                method="highs")
    C["u9"] = {"costos": costo, "envios": [list(map(float, r.x[i * len(d):(i + 1) * len(d)])) for i in range(len(o))],
               "costo_total": float(r.fun), "oferta_total": sum(OFERTA.values()), "demanda_total": sum(DEMANDA_T.values())}
    # U10 · asignación óptima
    ops, maqs = list(ASIGNACION), list(next(iter(ASIGNACION.values())))
    best_a = min((sum(ASIGNACION[o_][m] for o_, m in zip(ops, p)), dict(zip(ops, p))) for p in permutations(maqs))
    C["u10"] = {"minutos": best_a[0], "asignacion": best_a[1]}
    # U11 · heurística: vecino más cercano y 2-opt sobre la ruta del U4
    def largo(ruta): return sum(D[a][b] for a, b in zip(ruta, ruta[1:]))
    ruta = ["Taller"]; pend = set(paradas)
    while pend:
        sig = min(sorted(pend), key=lambda n: D[ruta[-1]][n]); ruta.append(sig); pend.remove(sig)
    ruta.append("Taller")
    vecino = (largo(ruta), list(ruta))
    mejora = True
    while mejora:
        mejora = False
        for i in range(1, len(ruta) - 2):
            for j in range(i + 1, len(ruta) - 1):
                nueva = ruta[:i] + ruta[i:j + 1][::-1] + ruta[j + 1:]
                if largo(nueva) < largo(ruta):
                    ruta, mejora = nueva, True
    C["u11"] = {"vecino_km": vecino[0], "vecino_ruta": vecino[1], "dos_opt_km": largo(ruta), "dos_opt_ruta": ruta,
                "gap_vecino": (vecino[0] - mejor_r[0]) / mejor_r[0]}
    # U12 · recocido simulado (semilla fija) sobre la misma ruta
    rnd = random.Random(SEMILLA)
    actual = vecino[1][:]; mejor_sa = actual[:]; T0 = 20.0
    for k in range(4000):
        temp = T0 * (0.999 ** k)
        i, j = sorted(rnd.sample(range(1, len(actual) - 1), 2))
        cand = actual[:i] + actual[i:j + 1][::-1] + actual[j + 1:]
        dlt = largo(cand) - largo(actual)
        if dlt < 0 or rnd.random() < math.exp(-dlt / max(temp, 1e-9)):
            actual = cand
            if largo(actual) < largo(mejor_sa):
                mejor_sa = actual[:]
    C["u12"] = {"recocido_km": largo(mejor_sa), "recocido_ruta": mejor_sa, "optimo_km": mejor_r[0]}
    return C


if __name__ == "__main__":
    C = calcular()
    for k, v in C.items():
        print(f"== {k}")
        for kk, vv in v.items():
            print(f"   {kk}: {vv}")
    if "--json" in sys.argv:
        Path(__file__).with_suffix(".json").write_text(json.dumps(C, ensure_ascii=False, indent=1), encoding="utf-8")
