"""Unidad 5 · Solución gráfica y ramificación y acotamiento.

Recalcula todas las cifras de la unidad desde los datos; con --revisar las busca en el .md.

1. Resuelve cada problema con ramificación y acotamiento propio (motor_ramificacion.py, en
   fracciones exactas) con las reglas que fija el texto: qué variable, qué rama primero, qué estrategia.
2. Comprueba cada óptimo con scipy (milp, HiGHS) y por fuerza bruta (enumerando los puntos enteros
   o todas las combinaciones de la mochila).
3. Si hay CPLEX (oplrun), corre los modelos de `modelos/u05_*.mod` con herramientas/opl.py y exige que
   coincidan con Python; corre también la relajación (`float+`) del caso.
4. Compara la pieza del caso integrador con los dos scripts de caso (Optimización y Tópicos):
   imprime CADENA: OK.
5. Dibuja las figuras SVG de `unidades/figuras/` (región del caso y árboles).
6. Con --revisar, busca cada cifra y cada tabla generada en el .md.

    python u05_ramificacion.py            # imprime resultados y redibuja las figuras
    python u05_ramificacion.py --revisar  # además busca cada cifra en el .md
"""
from fractions import Fraction as F
from pathlib import Path
import importlib.util, math, shutil, sys, tempfile

import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
FIGURAS = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "05-ramificacion-y-acotamiento.md"
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from motor_ramificacion import *  # noqa: E402,F401
from motor_ramificacion import F as Fr  # noqa: E402
from opl import correr  # noqa: E402

TOL = 1e-6

# ---------------------------------------------------------------- datos (originales; pasados por colisiones.py)
# Ejemplo · feria navideña: qué cajas llevar en un maletero de 165 litros (ganancia en miles de pesos)
FERIA = {"nombres": ["tazones", "velas", "lámparas", "mantas", "jabones"],
         "v": [217, 259, 47, 248, 138], "a": [50, 65, 145, 60, 35], "cap": 165}
# 5.1 y 5.2 · carro de sopaipillas: tandas de sopaipillas (x1) y de empanadas (x2), margen en miles
E1 = {"c": (3, 8), "filas": [(1, 2, 8), (1, 8, 25)]}
# 5.3 · podar o ramificar (máximo, coeficientes enteros): (z, ¿entera?) en el orden en que se resuelven
E3 = [(F(477, 10), False), (F(452, 10), False), (F(44), True), (None, None), (F(448, 10), False),
      (F(468, 10), False), (F(44), True), (F(45), True), (F(451, 10), False)]
# 5.4 · gap: (a) máximo; (b) mínimo
E4 = {"max_inc": 1_240, "max_abiertos": [1_315, 1_288], "max_pendiente_padre": 1_331,
      "min_inc": 86, "min_abiertos": [F(794, 10), 81, F(835, 10)]}
# 5.5 · dos variables, profundidad, rama ≤ primero, la más fraccional
E5 = {"c": (9, 7), "filas": [(9, 8, 28), (4, 2, 9)]}
# 5.6 · fondo vecinal: proyectos (puntos de impacto) con $1.320.000 (costos en miles de pesos)
E6 = {"nombres": ["luminarias", "plaza", "huerto", "talleres", "cámaras"],
      "v": [132, 151, 207, 216, 77], "a": [980, 640, 360, 340, 560], "cap": 1320}
# 5.7 · mínimo con mejor primero: bolsas de compost (x1) y de humus (x2), costo en miles
E7 = {"c": (2, 7), "filas": [(-4, -4, -15), (-2, -9, -18)]}
# 5.8 · mixto: turnos completos (entero) y toneladas compradas (continua), margen en miles
E8 = {"c": (120, 70), "filas": [(6, 2, 29), (6, 8, 45)]}
# 5.9 · árbol parcial (mínimo, profundidad, rama ≥ primero)
E9 = {"c": (5, 6), "filas": [(-2, -5, -28), (-9, -5, -36)]}
# 5.10 · imprenta: seis pedidos para 162 horas-máquina (margen en miles)
E10 = {"v": [133, 232, 157, 124, 48, 144], "a": [34, 44, 84, 54, 59, 74], "cap": 162, "tol": F(8, 100)}
# Caso · el turno del sábado de Estampa Sur
SABADO = {"est_min": 240, "pla_min": 150}


def con_cotas(filas):
    return list(filas) + [(-1, 0, 0), (0, -1, 0)]


# ---------------------------------------------------------------- casos integradores
def cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def casos():
    lp = cargar("caso_lp", RAMO.parent / "optimizacion" / "verificacion" / "caso_estampa_sur_lp.py")
    red = cargar("caso_red", AQUI / "caso_estampa_sur_red.py")
    return lp, red


def datos_caso():
    lp, red = casos()
    d, q = lp.DOS, red.CAJA
    margen = [m * q for m in d["margen"]]                       # CLP por caja
    est = [s * q // 60 for s in d["est"]]                       # minutos por caja
    pla = [s * q // 60 for s in d["pla"]]
    assert all(s * q % 60 == 0 for s in d["est"] + d["pla"])
    # mismas cifras desde el caso de Tópicos (las dos primeras prendas)
    assert margen == [m * q for m in red.MARGEN[:2]]
    assert est == [s * q // 60 for s in red.SEG_EST[:2]] and pla == [s * q // 60 for s in red.SEG_PLA[:2]]
    semana = {"est": d["cap_est"] // 60, "pla": d["cap_pla"] // 60, "dem": d["dem_polerones"]}
    return {"margen": margen, "est": est, "pla": pla, "semana": semana, "q": q, "lp": lp, "red": red}


# ---------------------------------------------------------------- comprobaciones con scipy
def milp2(c, filas, sentido="max", enteras=(0, 1)):
    A = [[f[0], f[1]] for f in filas]; b = [f[2] for f in filas]
    sg = -1 if sentido == "max" else 1
    integ = np.array([1 if j in enteras else 0 for j in range(2)])
    r = milp([sg * v for v in c], constraints=LinearConstraint(np.array(A, float), ub=np.array(b, float)),
             integrality=integ, bounds=Bounds([0, 0], [np.inf, np.inf]))
    assert r.status == 0
    return sg * r.fun, list(r.x)


def milp_mochila(v, a, cap):
    r = milp([-x for x in v], constraints=LinearConstraint(np.array([a], float), ub=[cap]),
             integrality=np.ones(len(v)), bounds=Bounds(np.zeros(len(v)), np.ones(len(v))))
    assert r.status == 0
    return -r.fun, [int(round(x)) for x in r.x]


def comprobar2(R, c, filas, sentido="max", enteras=(0, 1)):
    z, x = milp2(c, filas, sentido, enteras)
    assert abs(float(R["inc"][0]) - z) < 1e-6, (R["inc"], z)
    bf = mejor_entero(c, filas, sentido, 60, enteras)
    assert bf[0] == R["inc"][0], (bf, R["inc"])
    return z


def comprobar_mochila(R, d):
    z, x = milp_mochila(d["v"], d["a"], d["cap"])
    bf = mochila_fuerza_bruta(d["v"], d["a"], d["cap"])
    assert abs(float(R["inc"][0]) - z) < 1e-6 and bf[0] == R["inc"][0]
    assert tuple(int(t) for t in R["inc"][1]) == tuple(bf[1])
    return z


# ---------------------------------------------------------------- resultados
def ejemplo():
    d = FERIA
    R = rya_mochila(d["v"], d["a"], d["cap"], "profundidad", 1)
    comprobar_mochila(R, d)
    ratio = [F(v, a) for v, a in zip(d["v"], d["a"])]
    x0 = R["nodos"][0]["x"]
    trunc = [math.floor(t) for t in x0]
    z_trunc = sum(v * t for v, t in zip(d["v"], trunc))
    Rm = rya_mochila(d["v"], d["a"], d["cap"], "mejor", 1)
    return {"R": R, "T": traza(R), "ratio": ratio, "trunc": trunc, "z_trunc": z_trunc,
            "litros_opt": sum(a * t for a, t in zip(d["a"], R["inc"][1])), "Rm": Rm, "n_mejor": len(Rm["nodos"]),
            "gap_inc": traza(R)[[n["estado"] for n in R["nodos"]].index("entera")]["grel"]}


def ej1():
    filas = con_cotas(E1["filas"])
    z, x = lp2(E1["c"], filas)
    P = enteros(filas, 30)
    cerca = (round(float(x[0])), round(float(x[1])))
    piso = (math.floor(x[0]), math.floor(x[1]))
    vecinos = [(piso[0] + i, piso[1] + j) for i in (0, 1) for j in (0, 1)]
    fact = {p: all(f[0] * p[0] + f[1] * p[1] <= f[2] for f in filas) for p in vecinos}
    zi, xi = mejor_entero(E1["c"], filas)
    assert abs(milp2(E1["c"], filas)[0] - zi) < TOL
    assert xi not in vecinos
    V = envoltura(P)
    return {"x": x, "z": z, "P": P, "n": len(P), "cerca": cerca, "piso": piso, "vecinos": vecinos, "fact": fact,
            "zv": {p: E1["c"][0] * p[0] + E1["c"][1] * p[1] for p in vecinos}, "xi": xi, "zi": zi, "V": V,
            "gap": (z - zi) / zi}


def ej2():
    filas = con_cotas(E1["filas"])
    z, x = lp2(E1["c"], filas)
    j = elegir(x, (0, 1), "frac")
    v = math.floor(x[j])
    izq = lp2(E1["c"], filas + [(1, 0, v)]); der = lp2(E1["c"], filas + [(-1, 0, -(v + 1))])
    nodo = lp2(E1["c"], filas + [(-1, 0, -3), (0, 1, 2)])
    return {"j": j, "v": v, "izq": izq, "der": der, "nodo": nodo}


def ej3():
    """Decide cada nodo: incumbente al momento, regla simple y regla con la cota redondeada."""
    inc = None; out = []
    for z, ent in E3:
        if z is None:
            out.append(("infactible", inc, "infactible")); continue
        if inc is not None and z <= inc:
            d = "cota"
        elif ent:
            d = "entera"
        else:
            d = "ramifica"
        # con la cota redondeada (coeficientes enteros: toda solución entera vale un entero)
        if inc is not None and math.floor(z) <= inc:
            d2 = "cota"
        else:
            d2 = d
        out.append((d, inc, d2))
        if d == "entera":
            inc = z
    return out


def ej4():
    e = E4
    cota_max = max(e["max_abiertos"] + [e["max_pendiente_padre"]])
    g_abs = cota_max - e["max_inc"]
    sin_herencia = max(e["max_abiertos"])
    cota_min = min(e["min_abiertos"])
    g_abs_min = e["min_inc"] - cota_min
    redondeada = math.ceil(cota_min)
    return {"cota_max": cota_max, "gabs": g_abs, "grel": F(g_abs, e["max_inc"]),
            "grel_sin": F(sin_herencia - e["max_inc"], e["max_inc"]),
            "cota_min": cota_min, "gabs_min": g_abs_min, "grel_min": g_abs_min / e["min_inc"],
            "grel_min_mal": g_abs_min / cota_min, "redondeada": redondeada,
            "grel_min_red": F(e["min_inc"] - redondeada, e["min_inc"])}


def ej5():
    filas = con_cotas(E5["filas"])
    R = rya2(E5["c"], filas, "max", "profundidad", "le", "frac")
    comprobar2(R, E5["c"], filas)
    Rx1 = rya2(E5["c"], filas, "max", "profundidad", "le", "x1")
    return {"R": R, "T": traza(R), "n_x1": len(Rx1["nodos"]), "Rx1": Rx1}


def ej6():
    d = E6
    R = rya_mochila(d["v"], d["a"], d["cap"], "profundidad", 0)
    comprobar_mochila(R, d)
    R1 = rya_mochila(d["v"], d["a"], d["cap"], "profundidad", 1)
    x0 = R["nodos"][0]["x"]
    return {"R": R, "T": traza(R), "ratio": [F(v, a) for v, a in zip(d["v"], d["a"])], "n_1": len(R1["nodos"]),
            "costo_opt": sum(a * t for a, t in zip(d["a"], R["inc"][1])),
            "z_trunc": sum(v * math.floor(t) for v, t in zip(d["v"], x0))}


def ej7():
    filas = con_cotas(E7["filas"])
    R = rya2(E7["c"], filas, "min", "mejor", "le", "frac")
    comprobar2(R, E7["c"], filas, "min")
    Rp = rya2(E7["c"], filas, "min", "profundidad", "le", "frac")
    comprobar2(Rp, E7["c"], filas, "min")
    return {"R": R, "T": traza(R), "Rp": Rp, "Tp": traza(Rp), "n_prof": len(Rp["nodos"])}


def ej8():
    filas = con_cotas(E8["filas"])
    z0, x0 = lp2(E8["c"], filas)
    Rm = rya2(E8["c"], filas, "max", "profundidad", "le", "x1", enteras=(0,))
    comprobar2(Rm, E8["c"], filas, "max", enteras=(0,))
    Rp = rya2(E8["c"], filas, "max", "profundidad", "le", "frac")
    comprobar2(Rp, E8["c"], filas)
    assert Rp["inc"][0] <= Rm["inc"][0] <= z0
    return {"z0": z0, "x0": x0, "Rm": Rm, "Tm": traza(Rm), "Rp": Rp, "n_m": len(Rm["nodos"]), "n_p": len(Rp["nodos"]),
            "costo_indiv": Rm["inc"][0] - Rp["inc"][0]}


def ej9():
    filas = con_cotas(E9["filas"])
    R = rya2(E9["c"], filas, "min", "profundidad", "ge", "frac")
    comprobar2(R, E9["c"], filas, "min")
    T = traza(R)
    tol = F(8, 100)
    para = next(t["k"] for t in T if t["grel"] is not None and t["grel"] <= tol)
    t = next(t for t in T if t["k"] == para)
    t2 = next(t for t in T if t["inc"] is not None)
    red = F(t2["inc"] - math.ceil(t2["cota"]), t2["inc"])
    assert red <= tol and t2["grel"] > tol
    return {"R": R, "T": T, "tol": tol, "para": para, "inc_para": t["inc"], "cota_para": t["cota"], "grel_red": red,
            "grel_para": t["grel"]}


def ej10():
    d = E10
    Rp = rya_mochila(d["v"], d["a"], d["cap"], "profundidad", 1)
    Rb = rya_mochila(d["v"], d["a"], d["cap"], "mejor", 1)
    comprobar_mochila(Rp, d); comprobar_mochila(Rb, d)
    Tp, Tb = traza(Rp), traza(Rb)
    def parada(T):
        for t in T:
            if t["grel"] is not None and t["grel"] <= d["tol"]:
                return t
    sp, sb = parada(Tp), parada(Tb)
    # primera incumbente de cada estrategia
    def primera(R, T):
        k = next(n["k"] for n in R["nodos"] if n["estado"] == "entera")
        return next(t for t in T if t["k"] == k)
    return {"Rp": Rp, "Rb": Rb, "Tp": Tp, "Tb": Tb, "sp": sp, "sb": sb, "np": len(Rp["nodos"]), "nb": len(Rb["nodos"]),
            "pp": primera(Rp, Tp), "pb": primera(Rb, Tb), "opt": Rp["inc"][0],
            "ratio": [F(v, a) for v, a in zip(d["v"], d["a"])],
            "perdida_sp": Rp["inc"][0] - sp["inc"], "perdida_sb": Rp["inc"][0] - sb["inc"]}


def caso():
    D = datos_caso()
    c = tuple(D["margen"])
    filas_min = [(D["est"][0], D["est"][1], SABADO["est_min"]), (D["pla"][0], D["pla"][1], SABADO["pla_min"])]
    filas = con_cotas(filas_min)
    z0, x0 = lp2(c, filas)
    R = rya2(c, filas, "max", "profundidad", "le", "frac")
    zmilp = comprobar2(R, c, filas)
    P = enteros(filas, 25)
    V = envoltura(P)
    caras = facetas(V)
    piso = (math.floor(x0[0]), math.floor(x0[1]))
    cerca = (math.floor(x0[0] + F(1, 2)), math.floor(x0[1] + F(1, 2)))     # 12,5 → 13; 2,5 → 3
    vecinos = [(piso[0] + i, piso[1] + j) for i in (0, 1) for j in (0, 1)]
    def ok(p):
        return all(f[0] * p[0] + f[1] * p[1] <= f[2] for f in filas)
    def zz(p):
        return c[0] * p[0] + c[1] * p[1]
    mejor_vecino = max((p for p in vecinos if ok(p)), key=zz)
    # la semana completa en cajas: la relajación ya sale entera
    s = D["semana"]
    sem = con_cotas([(D["est"][0], D["est"][1], s["est"]), (D["pla"][0], D["pla"][1], s["pla"]),
                     (0, D["q"], s["dem"])])
    zs, xs = lp2(c, sem)
    assert all(v.denominator == 1 for v in xs)
    caso_lp = D["lp"].calcular()["u2"]
    assert abs(zs - caso_lp["z"]) < 1e-6 and all(abs(float(a) * D["q"] - b) < 1e-6 for a, b in zip(xs, caso_lp["x"]))
    # forma reducida (dividida por el máximo común divisor de cada fila)
    red = []
    for f in filas_min:
        g = math.gcd(math.gcd(f[0], f[1]), f[2])
        red.append((f[0] // g, f[1] // g, f[2] // g, g))
    # rodeo: con el nodo 4, redondear la cota a múltiplos de g (todas las soluciones enteras valen múltiplos)
    g = math.gcd(*c)
    T = traza(R)
    return {"c": c, "filas_min": filas_min, "filas": filas, "x0": x0, "z0": z0, "R": R, "T": T, "zmilp": zmilp,
            "P": P, "V": V, "caras": caras, "piso": piso, "cerca": cerca, "vecinos": vecinos,
            "fact": {p: ok(p) for p in vecinos}, "zv": {p: zz(p) for p in vecinos if ok(p)}, "mejor_vecino": mejor_vecino,
            "inc": R["inc"], "semana_x": xs, "semana_z": zs, "red": red, "g": g, "D": D,
            "uso_opt": [f[0] * R["inc"][1][0] + f[1] * R["inc"][1][1] for f in filas_min],
            "gap_lp": (z0 - R["inc"][0]) / R["inc"][0], "z_piso": zz(piso), "pierde_piso": R["inc"][0] - zz(piso)}


def resultados():
    return {"ej": ejemplo(), "e1": ej1(), "e2": ej2(), "e3": ej3(), "e4": ej4(), "e5": ej5(), "e6": ej6(),
            "e7": ej7(), "e8": ej8(), "e9": ej9(), "e10": ej10(), "caso": caso()}


# ---------------------------------------------------------------- tablas en Markdown
def z_txt(z, modo):
    if z is None:
        return "—"
    if modo == "pesos":
        return pesos(z)
    return num(z, 2)


def que_pasa(nd, R, nombres=("x₁", "x₂")):
    e = nd["estado"]
    if e == "ramificado":
        j = nd["var"]
        nom = nombres[j] if len(nombres) > j else f"x{j + 1}"
        return f"fraccional en {nom} = {fr(nd['x'][j])} → ramifica"
    if e == "entera":
        return "entera → nueva incumbente" if nd.get("nueva") else "entera → primera incumbente"
    if e == "cota":
        return "poda por cota"
    if e == "cota_tardia":
        return f"poda por cota tras PL{nd['podado_tras']}"
    if e == "infactible":
        return "infactible → poda"
    return e


def rama_md(r, kind):
    if kind == "mochila":
        j, val = r
        return f"x{j + 1} = {val}".translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")).replace(" = ₀", " = 0").replace(" = ₁", " = 1")
    return rama_txt(r)


def nombre_sub(j):
    return "x" + str(j + 1).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉"))


def rama_mochila(r):
    j, val = r
    return f"{nombre_sub(j)} = {val}"


def tabla_nodos(R, modo="num", kind="dos"):
    nombres = ("x₁", "x₂") if kind == "dos" else tuple(nombre_sub(j) for j in range(len(R["nodos"][0]["x"])))
    L = ["| PL | Ramas acumuladas | Solución relajada | z | Qué pasa |", "|---|---|---|---|---|"]
    for nd in R["nodos"]:
        ramas = ", ".join(rama_mochila(r) if kind == "mochila" else rama_txt(r) for r in nd["ramas"]) or "—"
        sol = vec(nd["x"]) if nd["x"] is not None else "infactible"
        L.append(f"| PL{nd['k']} | {ramas} | {sol} | {z_txt(nd['z'], modo)} | {que_pasa(nd, R, nombres)} |")
    return "\n".join(L)


def tabla_traza(T, modo="num", sentido="max"):
    cab_inc = "Incumbente (cota inferior)" if sentido == "max" else "Incumbente (cota superior)"
    cab_cota = "Mejor cota (superior)" if sentido == "max" else "Mejor cota (inferior)"
    L = [f"| Tras | {cab_inc} | {cab_cota} | Gap absoluto | Gap relativo |", "|---|---|---|---|---|"]
    for t in T:
        inc = "—" if t["inc"] is None else z_txt(t["inc"], modo)
        ga = "—" if t["gabs"] is None else z_txt(t["gabs"], modo)
        gr = "indefinido" if t["grel"] is None else pct(t["grel"])
        L.append(f"| PL{t['k']} | {inc} | {z_txt(t['cota'], modo)} | {ga} | {gr} |")
    return "\n".join(L)


def tablas(R):
    T = {}
    T["ej_nodos"] = tabla_nodos(R["ej"]["R"], "num", "mochila")
    T["ej_traza"] = tabla_traza(R["ej"]["T"])
    T["e5_nodos"] = tabla_nodos(R["e5"]["R"]); T["e5_traza"] = tabla_traza(R["e5"]["T"])
    T["e6_nodos"] = tabla_nodos(R["e6"]["R"], "num", "mochila"); T["e6_traza"] = tabla_traza(R["e6"]["T"])
    T["e7_nodos"] = tabla_nodos(R["e7"]["R"]); T["e7_traza"] = tabla_traza(R["e7"]["T"], "num", "min")
    T["e8_nodos"] = tabla_nodos(R["e8"]["Rm"])
    T["e9_nodos"] = tabla_nodos(R["e9"]["R"]); T["e9_traza"] = tabla_traza(R["e9"]["T"], "num", "min")
    T["e9_enunciado"] = tabla_enunciado_e9(R["e9"]["R"])
    T["e10_p"] = tabla_nodos(R["e10"]["Rp"], "num", "mochila"); T["e10_b"] = tabla_nodos(R["e10"]["Rb"], "num", "mochila")
    T["e10_tp"] = tabla_traza(R["e10"]["Tp"]); T["e10_tb"] = tabla_traza(R["e10"]["Tb"])
    T["caso_nodos"] = tabla_nodos(R["caso"]["R"], "pesos"); T["caso_traza"] = tabla_traza(R["caso"]["T"], "pesos")
    T["e3"] = tabla_e3(R["e3"])
    return T


def tabla_enunciado_e9(R):
    L = ["| PL | Ramas acumuladas | Solución relajada | z |", "|---|---|---|---|"]
    for nd in R["nodos"]:
        ramas = ", ".join(rama_txt(r) for r in nd["ramas"]) or "—"
        sol = vec(nd["x"]) if nd["x"] is not None else "infactible"
        L.append(f"| PL{nd['k']} | {ramas} | {sol} | {z_txt(nd['z'], 'num')} |")
    return "\n".join(L)


def tabla_e3(out):
    nombre = {"ramifica": "ramifica", "entera": "entera: incumbente", "cota": "poda por cota", "infactible": "poda por infactibilidad"}
    L = ["| PL | z | ¿Entera? | Incumbente al resolverlo | Decisión | Con la cota redondeada |", "|---|---|---|---|---|---|"]
    for k, ((z, ent), (d, inc, d2)) in enumerate(zip(E3, out)):
        zt = "infactible" if z is None else num(z, 2)
        et = "—" if ent is None else ("sí" if ent else "no")
        it = "—" if inc is None else num(inc)
        L.append(f"| PL{k} | {zt} | {et} | {it} | {nombre[d]} | {nombre[d2] if d2 != d else 'igual'} |")
    return "\n".join(L)


# ---------------------------------------------------------------- OPL
def comparar_con_opl(R):
    pruebas = [("u05_feria.mod", "u05_feria.dat", R["ej"]["R"]["inc"][0],
                {f"x[{n}]": int(t) for n, t in zip(FERIA["nombres"], R["ej"]["R"]["inc"][1])}),
               ("u05_sabado.mod", "u05_sabado.dat", R["caso"]["inc"][0],
                {"cajas[poleras]": R["caso"]["inc"][1][0], "cajas[polerones]": R["caso"]["inc"][1][1]}),
               ("u05_e08_compost.mod", None, R["e8"]["Rm"]["inc"][0],
                {"turnos": R["e8"]["Rm"]["inc"][1][0], "toneladas": R["e8"]["Rm"]["inc"][1][1]}),
               ("u05_e10_imprenta.mod", "u05_e10_imprenta.dat", R["e10"]["opt"],
                {f"x[{j + 1}]": int(t) for j, t in enumerate(R["e10"]["Rp"]["inc"][1])})]
    for mod, dat, z, vals in pruebas:
        r = correr(MODELOS / mod, MODELOS / dat if dat else None)
        if r is None:
            print("OPL: oplrun no está instalado; se comparan solo las cifras de Python")
            return None
        assert r["codigo"] == 0 and r["objetivo"] is not None, (mod, r["salida"][-500:])
        assert abs(r["objetivo"] - float(z)) < 1e-4, (mod, r["objetivo"], z)
        for k, v in vals.items():
            assert abs(r["valores"][k] - float(v)) < 1e-6, (mod, k, r["valores"].get(k), v)
    # la relajación del caso: el mismo .mod con float+
    tmp = Path(tempfile.mkdtemp(prefix="u05_"))
    try:
        mod = (MODELOS / "u05_sabado.mod").read_text(encoding="utf-8")
        assert "dvar int+ cajas[Prendas];" in mod
        f = tmp / "relajado.mod"; f.write_text(mod.replace("dvar int+", "dvar float+"), encoding="utf-8")
        r = correr(f, MODELOS / "u05_sabado.dat")
        assert abs(r["objetivo"] - float(R["caso"]["z0"])) < 1e-4, r["objetivo"]
        # un nodo del árbol: el PL4 (x1 ≥ 13) con float+
        g = tmp / "nodo4.mod"
        g.write_text(mod.replace("dvar int+", "dvar float+").replace("subject to {", 'subject to {\n  Rama: cajas["poleras"] >= 13;'),
                     encoding="utf-8")
        r = correr(g, MODELOS / "u05_sabado.dat")
        z4 = next(n["z"] for n in R["caso"]["R"]["nodos"] if n["k"] == 4)
        assert abs(r["objetivo"] - float(z4)) < 1e-4, r["objetivo"]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("OPL: 4 modelos enteros, la relajación del caso y su PL4 coinciden con Python")
    return True


# ---------------------------------------------------------------- figuras
def etiqueta_nodo(modo, kind="dos"):
    def f(nd):
        L = [f"PL{nd['k']}"]
        if nd["x"] is None:
            L.append("sin solución")
        else:
            L.append(vec(nd["x"]) if kind == "dos" else "x = " + vec(nd["x"]))
            L.append("z = " + z_txt(nd["z"], modo))
        L.append({"ramificado": f"ramifica en {nombre_sub(nd.get('var', 0))}", "entera": "entera ★" if False else "entera",
                  "cota": "poda por cota", "cota_tardia": "poda por cota", "infactible": "infactible"}[nd["estado"]])
        return L
    return f


def fig_arbol(R, modo, kind, titulo, ancho=150, optimo=None):
    rf = rama_mochila if kind == "mochila" else rama_txt
    lineas = etiqueta_nodo(modo, kind)
    return arbol_svg(R, lineas, titulo, ancho_nodo=ancho, alto_nodo=70, rama_txt_f=rf, optimo=optimo)


def fig_region(C):
    L = Lienzo(60, 24, 520, 330, (0, 20), (0, 7))
    L.ejes("cajas de poleras x₁", "cajas de polerones x₂", 2, 1)
    reg = ordenar(list(vertices(C["filas"])))
    L.poligono(reg, ACENTO, 0.12)
    L.poligono(ordenar(C["V"]), VERDE, 0.16, VERDE, "5 3")
    (a1, a2, b1), (c1, c2, b2) = C["filas_min"]
    L.recta(a1, a2, b1, TINTA, f"estampado: {a1}x₁ + {a2}x₂ ≤ {b1}", t=0.30, dx=-4, dy=-10, ancla="end")
    L.recta(c1, c2, b2, AZUL, f"planchado: {c1}x₁ + {c2}x₂ ≤ {b2}", t=0.06, dx=10, dy=-2)
    for p in C["P"]:
        L.punto(*p, 2.6, SUAVE)
    L.punto(*C["x0"], 6, ACENTO); L.rotulo(*C["x0"], f"relajación ({num(C['x0'][0], 1)}; {num(C['x0'][1], 1)})", ACENTO, 10, -10)
    xi = C["inc"][1]
    L.punto(*xi, 6, VERDE); L.rotulo(*xi, f"óptimo entero ({fr(xi[0])}; {fr(xi[1])})", VERDE, -10, -12, "end")
    L.punto(*C["mejor_vecino"], 5, AZUL, hueco=True)
    L.rotulo(*C["mejor_vecino"], f"mejor vecino ({C['mejor_vecino'][0]}; {C['mejor_vecino'][1]})", AZUL, -6, 20, "end")
    L.texto(578, 40, "verde punteado: envoltura convexa", VERDE, 11, "end", "600")
    L.texto(578, 56, "de los puntos enteros factibles", VERDE, 11, "end", "600")
    return svg(600, 400, L.p, "Turno del sábado: relajación, puntos enteros y envoltura convexa")


def dibujar(R):
    FIGURAS.mkdir(parents=True, exist_ok=True)
    C = R["caso"]
    (FIGURAS / "u05_sabado_region.svg").write_text(fig_region(C), encoding="utf-8")
    (FIGURAS / "u05_sabado_arbol.svg").write_text(
        fig_arbol(C["R"], "pesos", "dos", "Árbol de ramificación del turno del sábado", 156, C["inc"][2]), encoding="utf-8")
    (FIGURAS / "u05_feria_arbol.svg").write_text(
        fig_arbol(R["ej"]["R"], "num", "mochila", "Árbol de ramificación de la feria", 168, R["ej"]["R"]["inc"][2]), encoding="utf-8")
    print("FIGURAS: u05_sabado_region.svg, u05_sabado_arbol.svg y u05_feria_arbol.svg")


# ---------------------------------------------------------------- revisión
def par(p):
    return f"({fr(p[0])}; {fr(p[1])})"


def ineq(a1, a2, b, sig="\\le"):
    t1 = "x_1" if a1 == 1 else f"{a1}x_1"
    t2 = "x_2" if a2 == 1 else f"{a2}x_2"
    return f"{t1} + {t2} {sig} {b}"


def esperados(R):
    s = []
    E = R["ej"]
    s += [num(r, 3) for r in E["ratio"]] + [num(E["R"]["nodos"][0]["z"], 2), num(E["z_trunc"]), num(E["R"]["inc"][0]),
          str(E["litros_opt"]), str(E["n_mejor"]), pct(E["gap_inc"])]
    e = R["e1"]; s += [par(e["x"]), num(e["z"], 2), str(e["n"]), par(e["cerca"]), par(e["piso"]), num(e["zv"][e["piso"]]),
                       par(e["xi"]), num(e["zi"]), pct(e["gap"])]
    s += [", ".join(par(v) for v in e["V"])]
    e = R["e2"]; s += [par(e["izq"][1]), num(e["izq"][0], 2), par(e["der"][1]), num(e["der"][0], 2), par(e["nodo"][1]), num(e["nodo"][0], 2)]
    e = R["e4"]; s += [fmt(e["cota_max"]), fmt(e["gabs"]), pct(e["grel"]), pct(e["grel_sin"]), num(e["cota_min"], 1),
                       num(e["gabs_min"], 1), pct(e["grel_min"]), pct(e["grel_min_mal"]), str(e["redondeada"]), pct(e["grel_min_red"])]
    e = R["e5"]; s += [str(len(e["R"]["nodos"])), str(e["n_x1"]), par(e["R"]["inc"][1]), num(e["R"]["inc"][0])]
    e = R["e6"]; s += [num(r, 3) for r in e["ratio"]] + [num(e["R"]["inc"][0]), fmt(e["costo_opt"]), str(e["n_1"]), num(e["z_trunc"])]
    e = R["e7"]; s += [str(len(e["R"]["nodos"])), str(e["n_prof"]), par(e["R"]["inc"][1]), num(e["R"]["inc"][0])]
    e = R["e8"]; s += [par(e["x0"]), num(e["z0"], 2), par(e["Rm"]["inc"][1]), num(e["Rm"]["inc"][0], 2),
                       par(e["Rp"]["inc"][1]), num(e["Rp"]["inc"][0]), str(e["n_m"]), str(e["n_p"]), num(e["costo_indiv"])]
    e = R["e9"]; s += [f"PL{e['para']}", num(e["inc_para"]), num(e["cota_para"], 2), pct(e["grel_para"]), pct(e["grel_red"]), par(e["R"]["inc"][1]),
                       num(e["R"]["inc"][0])]
    e = R["e10"]; s += [str(e["np"]), str(e["nb"]), num(e["opt"]), f"PL{e['sp']['k']}", f"PL{e['sb']['k']}",
                        num(e["sp"]["inc"]), num(e["sb"]["inc"]), pct(e["sp"]["grel"]), pct(e["sb"]["grel"]),
                        num(e["perdida_sp"]), num(e["perdida_sb"]), f"PL{e['pp']['k']}", f"PL{e['pb']['k']}",
                        pct(e["pp"]["grel"]), pct(e["pb"]["grel"])] + [num(r, 3) for r in e["ratio"]]
    C = R["caso"]
    s += [pesos(v) for v in C["c"]] + [pesos(C["z0"]), par(C["x0"]), pesos(C["inc"][0]), par(C["inc"][1]),
          pesos(C["zmilp"]), str(len(C["P"])), pesos(C["z_piso"]), pesos(C["pierde_piso"]), pct(C["gap_lp"]),
          par(C["mejor_vecino"]), pesos(C["zv"][C["mejor_vecino"]]), str(len(C["R"]["nodos"])),
          f"({fr(C['semana_x'][0])}; {fr(C['semana_x'][1])})", pesos(C["semana_z"])]
    s += [fmt(v) for v in C["uso_opt"]]
    s += [", ".join(par(v) for v in C["V"])]
    for a1, a2, b, *_ in C["caras"]:
        if a1 > 0 and a2 > 0:
            s.append(ineq(a1, a2, b))
    return s


def tablas_en_md(R, md):
    faltan = []
    for k, t in tablas(R).items():
        for linea in t.splitlines():
            if linea not in md:
                faltan.append(f"{k}: {linea}")
    return faltan


def codigo_en_md(md):
    faltan = []
    for f in ["u05_feria.mod", "u05_feria.dat", "u05_sabado.mod", "u05_sabado.dat", "u05_e08_compost.mod"]:
        for linea in (MODELOS / f).read_text(encoding="utf-8").splitlines():
            if linea.strip() and linea.rstrip() not in md:
                faltan.append(f"{f}: {linea.strip()}")
    return faltan


def cadena(R):
    C = R["caso"]; D = C["D"]
    red = D["red"].calcular()["u1"]
    ok = C["c"] == (D["red"].MARGEN[0] * D["q"], D["red"].MARGEN[1] * D["q"])
    ok &= C["semana_z"] == D["lp"].calcular()["u2"]["z"]
    ok &= C["inc"][0] == C["zmilp"]
    print("CADENA:", "OK, la pieza del caso calza (márgenes y tiempos por caja desde los dos casos; la semana "
          "completa en cajas es la mezcla de dos productos de Optimización)" if ok else "NO calza")
    return ok


def imprimir(R):
    E = R["ej"]
    print("== ejemplo feria:", "óptimo", vec(E["R"]["inc"][1]), num(E["R"]["inc"][0]), "PL:", len(E["R"]["nodos"]),
          "mejor primero:", E["n_mejor"])
    for k in ["e1", "e2", "e4"]:
        print("==", k, {kk: (str(v) if not isinstance(v, (list, dict, tuple)) else v) for kk, v in R[k].items() if kk not in ("P",)})
    print("== e3", R["e3"])
    for k, clave in [("e5", "R"), ("e6", "R"), ("e7", "R"), ("e8", "Rm"), ("e9", "R"), ("e10", "Rp"), ("caso", "R")]:
        RR = R[k][clave]
        print(f"== {k}: óptimo {vec(RR['inc'][1])} z = {num(RR['inc'][0], 2)} con {len(RR['nodos'])} PL")
    C = R["caso"]
    print("   caso: relajación", vec(C["x0"]), pesos(C["z0"]), "· semana completa", vec(C["semana_x"]), pesos(C["semana_z"]))


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    dibujar(R)
    comparar_con_opl(R)
    if not cadena(R):
        sys.exit(1)
    if "--tablas" in sys.argv:
        for k, t in tablas(R).items():
            print(f"\n### {k}\n{t}")
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md2 = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md2]
        faltan += tablas_en_md(R, md) + codigo_en_md(md)
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
