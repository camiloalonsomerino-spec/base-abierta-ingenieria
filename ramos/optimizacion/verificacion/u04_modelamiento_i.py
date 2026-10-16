"""Unidad 4 · Modelamiento lineal I · producción y mezcla. Recalcula todas las cifras; con --revisar
las busca en el .md.

    python u04_modelamiento_i.py            # imprime los resultados y compara con OPL y con el caso
    python u04_modelamiento_i.py --revisar  # además busca cada cifra en unidades/04-modelamiento-produccion-y-mezcla.md

Cada modelo se resuelve en Python con scipy.optimize.linprog (HiGHS). Los que tienen versión OPL
(modelos/u04_*.mod) se corren también con oplrun si CPLEX está instalado, y se exige que objetivo,
variables y precios sombra coincidan. Las versiones enteras se resuelven con scipy.optimize.milp y se
comprueban por enumeración. Todos los datos son originales.
"""
from pathlib import Path
import importlib.util, itertools, sys

import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MOD = RAMO / "modelos"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402


def fmt(x, dec=1):
    s = f"{float(x):,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x, 0)


def cerca(a, b, tol=1e-6):
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))


# ------------------------------------------------------------------ datos (originales; pasados por colisiones.py)
GRANOLA = {"ing": ["avena", "mani", "pasas"], "prod": ["clasica", "premium"],
           "prot": [12, 24, 4], "azu": [1, 5, 65], "costo": [1380, 4150, 2950], "disp": [980, 190, 280],
           "precio": [4650, 6980], "dem": [760, 230], "pmin": [12, 16], "amin": [14, 9], "amax": [18, 12]}
E41 = {"margen": [730, 1060], "arcilla": [0.22, 0.38], "arcilla_disp": 760, "horno": 2900, "dem_fuentes": 1150}
E42 = {"margen": [9000, 7500], "tunel_min": [12, 8], "tunel_h": 40, "term_min": [10, 20], "term_h": 50}
E43 = {"alim": ["legumbres", "arroz", "huevo"], "kcal": [235, 190, 85], "prot": [16, 3, 7], "sodio": [12, 4, 75],
       "costo": [340, 115, 165], "kcal_min": 880, "prot_min": 42, "sodio_max": 290}
E44 = {"prot": [10, 22, 6], "max2": 0.30, "prot_min": 12, "mezcla": [50, 30, 20]}
E45 = {"vinos": ["cabernet", "merlot", "carmenere"], "alc": [14.0, 13.0, 14.5], "costo": [1900, 1480, 1100],
       "disp": [7000, 4000, 5800], "total": 9600, "alc_min": 13.2, "alc_max": 13.8, "part": 0.5}
E46 = {"inst": ["depósito a plazo", "fondo de renta fija", "fondo accionario", "bono corporativo"],
       "ret": [5.2, 6.8, 11.5, 8.3], "riesgo": [1, 2, 6, 3], "total": 50, "riesgo_max": 3.0,
       "acc_max": 0.35, "dep_min": 10, "bono_max": 12}
E47 = {"largo": 6.0, "piezas": [2.4, 1.7, 1.1], "dem": [130, 205, 170]}
E48 = {"leche_max": 7600, "leche_precio": 440, "l_queso": 9.5, "l_yogur": 1.15, "p_queso": 7200, "max_queso": 480,
       "p_yogur": 1750, "max_yogur": 2900, "h_queso": 0.125, "h_yogur": 0.025, "horas": 85}
E49 = {"ing": ["harina_pescado", "soya", "aceite_pescado", "aceite_raps"], "prot": [64, 45, 0, 0],
       "lip": [10, 2, 100, 100], "costo": [1650, 520, 2400, 1150], "disp_hp": 60, "dem": [40, 120],
       "pmin": [48, 38], "lmin": [18, 28], "lmax": [22, 32], "omega": 0.4, "hp_min": 0.25}
E410 = {"margen": [900_000, 700_000], "costo": [4, 3], "presupuesto": 25, "espacio": [1, 3], "m2": 12}


def caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_lp.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ solver genérico
def lp(c, filas, bounds=None, maxi=True):
    """filas: lista de (nombre, coeficientes, sentido '<=', '>=' o '==', lado derecho).
    Devuelve x, objetivo, y duales con el signo de «cuánto mejora el objetivo por unidad más de lado derecho»."""
    A_ub, b_ub, A_eq, b_eq, nub, neq, sgn = [], [], [], [], [], [], []
    for nom, a, s, b in filas:
        if s == "==":
            A_eq.append(a); b_eq.append(b); neq.append(nom)
        else:
            k = 1 if s == "<=" else -1
            A_ub.append([k * v for v in a]); b_ub.append(k * b); nub.append(nom); sgn.append(k)
    cc = [-v for v in c] if maxi else list(c)
    r = linprog(cc, A_ub=A_ub or None, b_ub=b_ub or None, A_eq=A_eq or None, b_eq=b_eq or None,
                bounds=bounds, method="highs")
    assert r.status == 0, r.message
    obj = -r.fun if maxi else r.fun
    m = -1 if maxi else 1
    duales, holg = {}, {}
    for i, nom in enumerate(nub):
        duales[nom] = m * r.ineqlin.marginals[i] * sgn[i] * (1 if maxi else 1)
        holg[nom] = r.ineqlin.residual[i]
    for i, nom in enumerate(neq):
        duales[nom] = m * r.eqlin.marginals[i]
    return {"x": list(r.x), "z": obj, "dual": duales, "holg": holg, "res": r}


# ------------------------------------------------------------------ modelos
def granola(d=GRANOLA):
    I, J = d["ing"], d["prod"]
    n = len(I) * len(J)
    k = lambda i, j: i * len(J) + j
    c = [d["precio"][j] - d["costo"][i] for i in range(len(I)) for j in range(len(J))]
    filas = []
    for i in range(len(I)):
        a = [0] * n
        for j in range(len(J)): a[k(i, j)] = 1
        filas.append((f"disp_{I[i]}", a, "<=", d["disp"][i]))
    for j in range(len(J)):
        a = [0] * n
        for i in range(len(I)): a[k(i, j)] = 1
        filas.append((f"dem_{J[j]}", a, "<=", d["dem"][j]))
    for j in range(len(J)):
        for nom, vec, lim, s in (("prot", d["prot"], d["pmin"][j], ">="), ("azumin", d["azu"], d["amin"][j], ">="),
                                 ("azumax", d["azu"], d["amax"][j], "<=")):
            a = [0] * n
            for i in range(len(I)): a[k(i, j)] = vec[i] - lim
            filas.append((f"{nom}_{J[j]}", a, s, 0))
    R = lp(c, filas)
    X = np.array(R["x"]).reshape(len(I), len(J))
    R["X"] = X
    R["kilos"] = X.sum(axis=0)
    R["uso"] = X.sum(axis=1)
    R["ingreso"] = sum(d["precio"][j] * R["kilos"][j] for j in range(len(J)))
    R["costo"] = sum(d["costo"][i] * R["uso"][i] for i in range(len(I)))
    R["prot_pct"] = [sum(d["prot"][i] * X[i, j] for i in range(len(I))) / R["kilos"][j] for j in range(len(J))]
    R["azu_pct"] = [sum(d["azu"][i] * X[i, j] for i in range(len(I))) / R["kilos"][j] for j in range(len(J))]
    return R


def mezcla_caso(m):
    filas = [("estampado", m.SEG_EST, "<=", m.CAP["estampado_s"]), ("planchado", m.SEG_PLA, "<=", m.CAP["planchado_s"]),
             ("tinta", m.TINTA_G, "<=", m.CAP["tinta_g"])]
    for i, p in enumerate(m.PRODUCTOS):
        a = [0] * 5; a[i] = 1
        filas.append((f"dem_{i}", a, "<=", m.DEMANDA_MAX[i]))
    R = lp(m.MARGEN, filas)
    ps = [R["dual"][k] for k in ("estampado", "planchado", "tinta")]
    uso = [m.SEG_EST, m.SEG_PLA, m.TINTA_G]
    R["costo_recursos"] = [sum(ps[r] * uso[r][i] for r in range(3)) for i in range(5)]
    R["reducido"] = [m.MARGEN[i] - R["costo_recursos"][i] for i in range(5)]
    # entero: el mejor plan con unidades enteras, y el que sale de truncar el lineal
    A = np.array(uso, float)
    b = [m.CAP["estampado_s"], m.CAP["planchado_s"], m.CAP["tinta_g"]]
    e = milp([-v for v in m.MARGEN], constraints=LinearConstraint(A, -np.inf, b), integrality=[1] * 5,
             bounds=Bounds([0] * 5, m.DEMANDA_MAX))
    assert e.status == 0
    piso = [int(np.floor(v + 1e-9)) for v in R["x"]]
    assert all(np.dot(A[r], piso) <= b[r] for r in range(3))
    R["entero_x"] = [round(v) for v in e.x]
    R["entero_z"] = -e.fun
    R["piso_x"] = piso
    R["piso_z"] = float(np.dot(m.MARGEN, piso))
    R["usado"] = [float(np.dot(A[r], R["x"])) for r in range(3)]
    return R


def e41():
    d = E41
    return lp(d["margen"], [("arcilla", d["arcilla"], "<=", d["arcilla_disp"]), ("horno", [1, 1], "<=", d["horno"]),
                            ("fuentes", [0, 1], "<=", d["dem_fuentes"])])


def e42():
    d = E42
    bien = lp(d["margen"], [("tunel", d["tunel_min"], "<=", 60 * d["tunel_h"]), ("term", d["term_min"], "<=", 60 * d["term_h"])])
    mal = lp(d["margen"], [("tunel", d["tunel_min"], "<=", d["tunel_h"]), ("term", d["term_min"], "<=", d["term_h"])])
    return bien, mal


def e43():
    d = E43
    return lp(d["costo"], [("kcal", d["kcal"], ">=", d["kcal_min"]), ("prot", d["prot"], ">=", d["prot_min"]),
                           ("sodio", d["sodio"], "<=", d["sodio_max"])], maxi=False)


def e44():
    d = E44
    x1, x2, x3 = d["mezcla"]
    tot = x1 + x2 + x3
    prot = (d["prot"][0] * x1 + d["prot"][1] * x2 + d["prot"][2] * x3) / tot
    return {"tot": tot, "a": (x2, d["max2"] * tot, x2 <= d["max2"] * tot), "b": (x1, 2 * x3, x1 >= 2 * x3),
            "c": (prot, prot >= d["prot_min"]), "d": (2 * x1, 3 * x2, 2 * x1 <= 3 * x2)}


def e45(d=E45):
    n = len(d["vinos"])
    filas = [("total", [1] * n, "==", d["total"]),
             ("alcmax", [a - d["alc_max"] for a in d["alc"]], "<=", 0),
             ("alcmin", [a - d["alc_min"] for a in d["alc"]], ">=", 0),
             ("cepa", [1 - d["part"]] + [-d["part"]] * (n - 1), ">=", 0)]
    R = lp(d["costo"], filas, bounds=[(0, v) for v in d["disp"]], maxi=False)
    R["alc"] = sum(a * x for a, x in zip(d["alc"], R["x"])) / d["total"]
    return R


def e46(d=E46):
    filas = [("total", [1] * 4, "==", d["total"]),
             ("riesgo", [r - d["riesgo_max"] for r in d["riesgo"]], "<=", 0),
             ("acciones", [-d["acc_max"], -d["acc_max"], 1 - d["acc_max"], -d["acc_max"]], "<=", 0)]
    R = lp([r / 100 for r in d["ret"]], filas, bounds=[(d["dep_min"], None), (0, None), (0, None), (0, d["bono_max"])])
    R["tasa"] = R["z"] / d["total"]
    R["riesgo_prom"] = sum(r * x for r, x in zip(d["riesgo"], R["x"])) / d["total"]
    R["tope_acc"] = d["acc_max"] * d["total"]
    return R


def e47(d=E47):
    L, P = d["largo"], d["piezas"]
    pats = []
    for cant in itertools.product(*(range(int(L // p) + 1) for p in P)):
        s = sum(c * p for c, p in zip(cant, P))
        if any(cant) and s <= L + 1e-9 and all(s + p > L + 1e-9 for p in P):
            pats.append((cant, round(L - s, 2)))
    A = np.array([[p[0][k] for p in pats] for k in range(len(P))], float)
    filas = [(f"pieza_{k}", list(A[k]), ">=", d["dem"][k]) for k in range(len(P))]
    R = lp([1] * len(pats), filas, maxi=False)
    e = milp([1] * len(pats), constraints=LinearConstraint(A, d["dem"], np.inf), integrality=[1] * len(pats))
    R["pats"] = pats
    R["entero_z"] = e.fun
    R["redondeo"] = [int(np.ceil(v - 1e-9)) for v in R["x"]]
    assert all(np.dot(A[k], R["redondeo"]) >= d["dem"][k] for k in range(len(P)))
    R["cota_largo"] = sum(p * q for p, q in zip(P, d["dem"])) / L
    R["metros"] = sum(p * q for p, q in zip(P, d["dem"]))
    return R


def e48(d=E48):
    # variables: L (litros comprados), Q (kg de queso), Y (kg de yogur)
    filas = [("leche", [-1, d["l_queso"], d["l_yogur"]], "<=", 0), ("horas", [0, d["h_queso"], d["h_yogur"]], "<=", d["horas"])]
    R = lp([-d["leche_precio"], d["p_queso"], d["p_yogur"]], filas,
           bounds=[(0, d["leche_max"]), (0, d["max_queso"]), (0, d["max_yogur"])])
    R["margen_queso_kg"] = d["p_queso"] - d["l_queso"] * d["leche_precio"]
    R["margen_yogur_kg"] = d["p_yogur"] - d["l_yogur"] * d["leche_precio"]
    return R


def e49(d=E49, pmin=None, disp_hp=None, solo_harina=False):
    pmin = pmin or d["pmin"]
    disp_hp = d["disp_hp"] if disp_hp is None else disp_hp
    nI, nJ = 4, 2
    k = lambda i, j: i * nJ + j
    n = nI * nJ
    c = [1000 * d["costo"][i] for i in range(nI) for j in range(nJ)]
    if solo_harina:                       # cuánta harina de pescado es imprescindible
        c = [1 if i == 0 else 0 for i in range(nI) for j in range(nJ)]
    filas = []
    a = [0] * n
    for j in range(nJ): a[k(0, j)] = 1
    filas.append(("disp_hp", a, "<=", disp_hp))
    for j in range(nJ):
        a = [0] * n
        for i in range(nI): a[k(i, j)] = 1
        filas.append((f"dem_{j}", a, "==", d["dem"][j]))
        for nom, vec, lim, s in (("prot", d["prot"], pmin[j], ">="), ("lipmin", d["lip"], d["lmin"][j], ">="),
                                 ("lipmax", d["lip"], d["lmax"][j], "<=")):
            a = [0] * n
            for i in range(nI): a[k(i, j)] = vec[i] - lim
            filas.append((f"{nom}_{j}", a, s, 0))
        a = [0] * n
        a[k(2, j)] = 1 - d["omega"]; a[k(3, j)] = -d["omega"]
        filas.append((f"omega_{j}", a, ">=", 0))
    a = [0] * n
    for i in range(nI): a[k(i, 0)] = -d["hp_min"]
    a[k(0, 0)] += 1
    filas.append(("hp_inicio", a, ">=", 0))
    R = lp(c, filas, maxi=False)
    R["X"] = np.array(R["x"]).reshape(nI, nJ)
    return R


def e410(d=E410):
    R = lp(d["margen"], [("presupuesto", d["costo"], "<=", d["presupuesto"]), ("espacio", d["espacio"], "<=", d["m2"])])
    fact = [(i, j) for i in range(20) for j in range(20)
            if d["costo"][0] * i + d["costo"][1] * j <= d["presupuesto"] and d["espacio"][0] * i + d["espacio"][1] * j <= d["m2"]]
    mejor = max(fact, key=lambda p: d["margen"][0] * p[0] + d["margen"][1] * p[1])
    e = milp([-v for v in d["margen"]], constraints=LinearConstraint([d["costo"], d["espacio"]], -np.inf, [d["presupuesto"], d["m2"]]),
             integrality=[1, 1])
    assert cerca(-e.fun, d["margen"][0] * mejor[0] + d["margen"][1] * mejor[1])
    piso = tuple(int(np.floor(v)) for v in R["x"])
    red = tuple(int(round(v)) for v in R["x"])
    R["mejor"], R["mejor_z"] = mejor, -e.fun
    R["piso"], R["piso_z"] = piso, d["margen"][0] * piso[0] + d["margen"][1] * piso[1]
    R["red"] = red
    R["red_presup"] = d["costo"][0] * red[0] + d["costo"][1] * red[1]
    R["red_esp"] = d["espacio"][0] * red[0] + d["espacio"][1] * red[1]
    return R


def resultados():
    m = caso()
    R = {"gran": granola(), "caso": mezcla_caso(m), "e41": e41(), "e42": e42(), "e43": e43(), "e44": e44(),
         "e45": e45(), "e46": e46(), "e47": e47(), "e48": e48(), "e49": e49(), "e410": e410()}
    R["e49_p39"] = e49(pmin=[E49["pmin"][0], E49["pmin"][1] + 1])
    R["e49_hp_min"] = e49(solo_harina=True)
    try:
        e49(disp_hp=30)
        raise AssertionError("con 30 t debía ser infactible")
    except AssertionError as err:
        assert "infeasible" in str(err).lower()
    R["m"] = m
    return R


# ------------------------------------------------------------------ OPL
def opl(R):
    pares = [("u04_granola", R["gran"]), ("u04_mezcla", R["caso"]), ("u04_e05_ensamblaje", R["e45"]),
             ("u04_e09_alimento_salmones", R["e49"])]
    ok = True
    for nombre, P in pares:
        r = correr(MOD / f"{nombre}.mod", MOD / f"{nombre}.dat")
        if r is None:
            print("OPL: no instalado; se sigue con Python")
            return True
        v = r["valores"]
        bien = r["codigo"] == 0 and r["objetivo"] is not None
        if nombre == "u04_granola":
            G = GRANOLA
            bien &= cerca(v["margen"], P["z"])
            for i, ing in enumerate(G["ing"]):
                bien &= cerca(v[f"dual_disp_{ing}"], P["dual"][f"disp_{ing}"])
                for j, pr in enumerate(G["prod"]):
                    bien &= cerca(v[f"x_{ing}_{pr}"], P["X"][i, j])
            for pr in G["prod"]:
                bien &= cerca(v[f"dual_demanda_{pr}"], P["dual"][f"dem_{pr}"])
        elif nombre == "u04_mezcla":
            bien &= cerca(v["margen"], P["z"])
            for i, pr in enumerate(["poleras", "polerones", "doble", "bolsas", "gorros"]):
                bien &= cerca(v[f"x_{pr}"], P["x"][i]) and cerca(v[f"dual_demanda_{pr}"], P["dual"][f"dem_{i}"])
            for rr in ("estampado", "planchado", "tinta"):
                bien &= cerca(v[f"dual_{rr}"], P["dual"][rr]) and cerca(v[f"holgura_{rr}"], P["holg"][rr], 1e-5)
        elif nombre == "u04_e05_ensamblaje":
            bien &= cerca(v["costo"], P["z"]) and cerca(v["dual_total"], P["dual"]["total"])
            for i, vino in enumerate(E45["vinos"]):
                bien &= cerca(v[f"x_{vino}"], P["x"][i])
        else:
            bien &= cerca(v["costo"], P["z"], 1e-7)
            for i, ing in enumerate(E49["ing"]):
                for j, al in enumerate(["inicio", "engorda"]):
                    bien &= cerca(v[f"x_{ing}_{al}"], P["X"][i, j], 1e-6)
        print(f"OPL {nombre}:", "OK, coincide con Python" if bien else f"NO coincide: {v}")
        ok &= bien
    return ok


# ------------------------------------------------------------------ cadena
def cadena(R):
    C = R["m"].calcular()["u4"]
    P = R["caso"]
    ok = cerca(P["z"], C["z"]) and all(cerca(a, b) for a, b in zip(P["x"], C["x"]))
    ok &= all(cerca(P["dual"][k], C["precios_sombra"][i]) for i, k in enumerate(("estampado", "planchado", "tinta")))
    ok &= all(abs(P["holg"][k] - C["holguras"][i]) < 1e-5 for i, k in enumerate(("estampado", "planchado", "tinta")))
    ok &= all(cerca(P["dual"][f"dem_{i}"], C["costo_reducido_cotas"][i]) for i in range(5))
    print("CADENA:", "OK, la pieza del caso calza (mezcla, margen, holguras, precios sombra y costos reducidos)" if ok else "NO calza")
    return ok


# ------------------------------------------------------------------ esperados
def esperados(R):
    E = []
    g = R["gran"]
    E += [pesos(g["z"]), fmt(g["X"][0, 0], 0), fmt(g["X"][1, 0], 1), fmt(g["X"][2, 0], 1), fmt(g["X"][0, 1], 0),
          fmt(g["X"][1, 1], 1), fmt(g["X"][2, 1], 1), fmt(g["kilos"][1], 0), fmt(g["uso"][0], 0),
          fmt(980 - g["uso"][0], 0), fmt(280 - g["uso"][2], 0), pesos(g["dual"]["disp_mani"]),
          pesos(g["dual"]["dem_clasica"]), pesos(g["ingreso"]), pesos(g["costo"]),
          fmt(GRANOLA["dem"][1] - g["kilos"][1], 0) + " kg"]
    assert all(cerca(v, GRANOLA["pmin"][j]) for j, v in enumerate(g["prot_pct"]))
    assert all(cerca(v, GRANOLA["amin"][j]) for j, v in enumerate(g["azu_pct"]))
    c = R["caso"]
    m = R["m"]
    E += [fmt(c["x"][0], 2), fmt(c["x"][1], 0), fmt(c["x"][3], 3), fmt(c["x"][4], 0), pesos(c["z"]),
          fmt(c["holg"]["estampado"], 0) + " s", fmt(c["usado"][0], 0), fmt(c["usado"][0] / 3600, 2),
          fmt(c["dual"]["planchado"], 1), pesos(c["dual"]["planchado"] * 3600), fmt(c["dual"]["tinta"], 1),
          fmt(c["dual"]["dem_1"], 1), fmt(c["dual"]["dem_4"], 1), fmt(-c["reducido"][2], 0),
          fmt(c["costo_recursos"][2], 0), pesos(c["entero_z"]), pesos(c["piso_z"]), pesos(c["z"] - c["piso_z"]),
          pesos(c["z"] - c["entero_z"]), "144.000", "64.800", "29.500"]
    E += [fmt(v, 0) for v in c["entero_x"] if v > 0]
    a = R["e41"]
    E += [fmt(a["x"][0], 1), fmt(a["x"][1], 1), pesos(a["z"]), fmt(a["dual"]["arcilla"], 1), fmt(a["dual"]["horno"], 2),
          fmt(a["holg"]["fuentes"], 1)]
    bien, mal = R["e42"]
    E += [f"({fmt(bien['x'][0], 0)}, {fmt(bien['x'][1], 0)})", pesos(bien["z"]),
          f"({fmt(mal['x'][0], 1)}; {fmt(mal['x'][1], 2)})", pesos(mal["z"]), "2.400", "3.000"]
    d = R["e43"]
    E += [fmt(d["x"][0], 2), fmt(d["x"][1], 2), pesos(d["z"]), fmt(d["holg"]["sodio"], 1)]
    e = R["e44"]
    E += [fmt(e["a"][1], 0), fmt(e["c"][0], 1) + " %", f"{fmt(e['d'][0], 0)} \\le {fmt(e['d'][1], 0)}"]
    assert e["a"][2] and e["b"][2] and e["c"][1] and not e["d"][2]
    f = R["e45"]
    E += [fmt(v, 0) for v in f["x"]] + [pesos(f["z"]), pesos(f["dual"]["total"]), fmt(f["alc"], 1),
                                         pesos(f["z"] / E45["total"])]
    h = R["e46"]
    E += [fmt(v, 0) for v in h["x"]] + [pesos(h["z"] * 1e6), fmt(100 * h["tasa"], 3) + " %",
                                         fmt(h["riesgo_prom"], 1), fmt(h["tope_acc"], 1)]
    i = R["e47"]
    E += [fmt(i["z"], 1), fmt(i["entero_z"], 0), fmt(i["metros"], 1), fmt(i["cota_largo"], 2)]
    E += [fmt(v, 1) for v in i["x"] if v > 1e-9]
    E += [f"{p[0][0]} · {p[0][1]} · {p[0][2]} | {fmt(p[1], 1)}" for p in i["pats"]]
    j = R["e48"]
    E += [fmt(j["x"][0], 0), fmt(j["x"][1], 0), fmt(j["x"][2], 0), pesos(j["z"]), pesos(j["dual"]["leche"]),
          pesos(j["dual"]["horas"]), pesos(j["margen_queso_kg"]), pesos(j["margen_yogur_kg"])]
    k = R["e49"]
    E += [pesos(k["z"]), pesos(R["e49_p39"]["z"]), pesos(R["e49_p39"]["z"] - k["z"]), fmt(k["X"][0].sum(), 2), fmt(R["e49_hp_min"]["z"], 2)]
    E += [fmt(v, 2) for v in k["X"].flatten()]
    # cifras derivadas que el texto menciona de paso
    E += [fmt(100 * k["X"][0, 0] / E49["dem"][0], 0) + " %", fmt(c["holg"]["estampado"] / 3600, 2) + " h",
          fmt(c["costo_recursos"][1], 1), f"{fmt(1 / E48['h_queso'], 0)} kg más de queso"]
    T, Fu = int(a["x"][0]), int(a["x"][1])
    assert E41["arcilla"][0] * T + E41["arcilla"][1] * Fu <= E41["arcilla_disp"] and T + Fu <= E41["horno"]
    E += [f"{fmt(T, 0)} tazas y {fmt(Fu, 0)} fuentes caben"]
    rc_huevo = E43["costo"][2] - sum(d["dual"][n] * E43[n][2] for n in ("kcal", "prot"))
    assert rc_huevo > 0
    l_ = R["e410"]
    E += [f"({fmt(l_['x'][0], 2)}; {fmt(l_['x'][1], 2)})", pesos(l_["z"]), pesos(l_["piso_z"]), pesos(l_["mejor_z"]),
          f"({l_['mejor'][0]}, {l_['mejor'][1]})", f"({l_['piso'][0]}, {l_['piso'][1]})", f"({l_['red'][0]}, {l_['red'][1]})"]
    return E


def imprimir(R):
    for k, v in R.items():
        if k == "m":
            continue
        print(f"== {k}")
        vv = v if isinstance(v, tuple) else (v,)
        for P in vv:
            if isinstance(P, dict) and "z" in P:
                print("   z =", round(P["z"], 4), "| x =", [round(float(t), 4) for t in P["x"]])
                print("   duales =", {a: round(float(b), 4) for a, b in P["dual"].items()})
                print("   holguras =", {a: round(float(b), 4) for a, b in P["holg"].items()})
                for extra in ("entero_x", "entero_z", "piso_x", "piso_z", "reducido", "costo_recursos", "usado", "pats",
                              "redondeo", "cota_largo", "mejor", "mejor_z", "piso", "red", "red_presup", "red_esp",
                              "tasa", "riesgo_prom", "alc", "kilos", "uso"):
                    if extra in P:
                        print(f"   {extra} =", P[extra])
            else:
                print("  ", P)


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    ok = opl(R)
    if not cadena(R) or not ok:
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (RAMO / "unidades" / "04-modelamiento-produccion-y-mezcla.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
