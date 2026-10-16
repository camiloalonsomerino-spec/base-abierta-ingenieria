"""Unidad 1 · Programación entera: por qué no basta redondear.

Recalcula todas las cifras de la unidad desde los datos; con --revisar las busca en el .md.

1. Resuelve cada problema dos veces: la relajación lineal (scipy linprog, HiGHS) y el problema
   entero (scipy milp), y cuando el problema es chico lo comprueba enumerando los puntos enteros.
2. Si hay CPLEX (oplrun), corre los modelos de `modelos/u01_*.mod` con herramientas/opl.py y exige
   que coincidan con Python; corre también la versión `float+` (la relajación) y provoca el error de
   pedir `.dual` en un modelo entero.
3. Compara la pieza del caso integrador con `caso_estampa_sur_red.py` (debe imprimir CADENA: OK).
4. Dibuja las figuras SVG de `unidades/figuras/`.

    python u01_programacion_entera.py            # imprime resultados y redibuja las figuras
    python u01_programacion_entera.py --revisar  # además busca cada cifra en el .md
"""
from pathlib import Path
import importlib.util, itertools, math, re, shutil, sys, tempfile

import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds
from scipy.spatial import ConvexHull

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
FIGURAS = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "01-programacion-entera.md"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402

TOL = 1e-6


# ---------------------------------------------------------------- formato chileno
def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x, dec=0):
    return ("−" if x < 0 else "") + "$" + fmt(abs(x), dec)


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def num(x, maxdec=3):
    if abs(x - round(x)) < 1e-9:
        return fmt(round(x), 0)
    for d in range(1, maxdec + 1):
        if abs(x - round(x, d)) < 1e-9:
            return fmt(x, d)
    return fmt(x, maxdec)


def par(p, dec=2):
    return f"({num(p[0], dec)}; {num(p[1], dec)})"


# ---------------------------------------------------------------- datos (originales)
# Ejemplo · toldos y módulos de escenario para la temporada (empresa de eventos ficticia)
EJ = {"c": [1_300_000, 600_000],          # margen por temporada de cada toldo y de cada módulo
      "A": [[2, 7], [9, 4]],              # m² de bodega · millones de pesos de compra
      "b": [48, 41]}                      # 48 m² de bodega · $41 millones de presupuesto
# 1.2 · cotas
E2 = {"max_rel": 1_284_600, "max_inc": 1_212_000, "paso": 1_000,
      "min_rel": 418.5, "min_inc": 431}
# 1.3 · problema de dos variables para resolver a mano
E3 = {"c": [10, 11], "A": [[4, 5], [8, 1]], "b": [41, 31]}
# 1.4 · explosión combinatoria
E4 = {"n": [30, 50, 80], "por_segundo": 1e9, "enteras": (10, 100)}   # 10 variables de 0 a 99
# 1.5 · minimizar: buses y minibuses para una faena (pesos por día)
E5 = {"c": [70_000, 60_000], "A": [[7, 5], [1, 4]], "b": [47, 21]}
# 1.6 · envoltura convexa
E6 = {"c": [3, 4], "A": [[5, 3], [-1, 2]], "b": [16, 5]}
# 1.7 · fruta: camiones (12 t), furgones (3,5 t) y tren (continuo, a lo más 20 t)
E7 = {"camion": (12, 180_000), "furgon": (3.5, 65_000), "tren": (9_000, 20), "carga": 47.5}
# 1.8 · dos formulaciones del mismo conjunto entero
E8 = {"c": [5, 4, 3]}
# 1.9 · el tamaño del lote cambia todo
E9 = {"c": [4_200, 2_900, 6_100], "A": [[3, 2, 5], [2, 3, 2]], "b": [1_853, 1_393], "lote": 40}
# 1.10 · asignación con y sin una restricción de horas
E10 = {"costo": [[13, 8, 15], [9, 15, 15], [14, 12, 4]],      # miles de pesos
       "horas": [[9, 5, 2], [4, 3, 7], [9, 5, 8]], "tope": 14}


def caso_mod():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_red.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- herramientas
def lp(c, A, b, sentido="max", ge=False, cotas=None):
    sg = -1 if sentido == "max" else 1
    AA = [[-v for v in fila] for fila in A] if ge else A
    bb = [-v for v in b] if ge else b
    r = linprog([sg * v for v in c], A_ub=AA, b_ub=bb, bounds=cotas or [(0, None)] * len(c), method="highs")
    assert r.status == 0, r.message
    return list(r.x), sg * r.fun


def entero(c, A, b, sentido="max", ge=False, ub=None):
    sg = -1 if sentido == "max" else 1
    lo, hi = (b, [np.inf] * len(b)) if ge else ([-np.inf] * len(b), b)
    r = milp([sg * v for v in c], constraints=LinearConstraint(A, lo, hi), integrality=np.ones(len(c)),
             bounds=Bounds(np.zeros(len(c)), ub if ub is not None else np.full(len(c), np.inf)))
    assert r.status == 0, r.message
    return [int(round(v)) for v in r.x], sg * r.fun


def factible(p, A, b, ge=False):
    return all((np.dot(f, p) >= bi - TOL) if ge else (np.dot(f, p) <= bi + TOL) for f, bi in zip(A, b))


def puntos(A, b, hasta=15, ge=False):
    return [(i, j) for i in range(hasta + 1) for j in range(hasta + 1) if factible((i, j), A, b, ge)]


def dos_variables(d, sentido="max", ge=False):
    """Relajación, los cuatro redondeos, la enumeración y el óptimo entero de un problema 2D."""
    x, z = lp(d["c"], d["A"], d["b"], sentido, ge)
    val = lambda p: float(np.dot(d["c"], p))
    esquinas = []
    for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        p = (math.floor(x[0]) + dx, math.floor(x[1]) + dy)
        esquinas.append({"p": p, "factible": factible(p, d["A"], d["b"], ge), "z": val(p),
                         "viola": [k for k, (f, bi) in enumerate(zip(d["A"], d["b"]))
                                   if ((np.dot(f, p) < bi - TOL) if ge else (np.dot(f, p) > bi + TOL))]})
    pts = puntos(d["A"], d["b"], ge=ge)
    orden = sorted(pts, key=lambda p: val(p), reverse=(sentido == "max"))
    xi, zi = entero(d["c"], d["A"], d["b"], sentido, ge)
    assert tuple(xi) == orden[0] and abs(val(orden[0]) - zi) < TOL
    assert abs(val(orden[1]) - zi) > TOL, "el óptimo entero no es único"
    cercano = (round(x[0]), round(x[1]))
    return {"x": x, "z": z, "esquinas": esquinas, "puntos": pts, "xi": tuple(xi), "zi": zi,
            "segundo": (orden[1], val(orden[1])), "cercano": cercano,
            "cercano_factible": factible(cercano, d["A"], d["b"], ge),
            "gap": abs(z - zi) / abs(zi)}


def envoltura(pts):
    H = ConvexHull(np.array(pts, float))
    vert = [tuple(int(v) for v in H.points[k]) for k in H.vertices]
    caras = []
    for a1, a2, c0 in H.equations:          # a·x + c0 ≤ 0
        m = min(abs(v) for v in (a1, a2) if abs(v) > 1e-9)
        a1, a2, rhs = a1 / m, a2 / m, -c0 / m
        caras.append((round(a1), round(a2), round(rhs)))
        assert abs(a1 - round(a1)) < 1e-9 and abs(a2 - round(a2)) < 1e-9 and abs(rhs - round(rhs)) < 1e-9
    return vert, caras


# ---------------------------------------------------------------- ejemplo y ejercicios
def ejemplo():
    R = dos_variables(EJ)
    vert, caras = envoltura(R["puntos"])
    A = [[a1, a2] for a1, a2, _ in caras]; b = [r for *_, r in caras]
    xh, zh = lp(EJ["c"], A, b)
    assert abs(zh - R["zi"]) < 1e-3 and max(abs(xh[0] - R["xi"][0]), abs(xh[1] - R["xi"][1])) < 1e-6
    R.update({"envoltura": vert, "caras": caras, "n_puntos": len(R["puntos"]),
              "uso_int": [float(np.dot(f, R["xi"])) for f in EJ["A"]],
              "uso_piso": [float(np.dot(f, R["esquinas"][0]["p"])) for f in EJ["A"]],
              "uso_cercano": [float(np.dot(f, R["cercano"])) for f in EJ["A"]],
              "perdida_piso": R["z"] - R["esquinas"][0]["z"], "perdida_int": R["z"] - R["zi"],
              "pierde_redondeo": R["zi"] - R["esquinas"][0]["z"]})
    return R


def ej2():
    d = E2
    g_max = (d["max_rel"] - d["max_inc"]) / d["max_inc"]
    tope = math.floor(d["max_rel"] / d["paso"]) * d["paso"]
    g_max2 = (tope - d["max_inc"]) / d["max_inc"]
    piso = math.ceil(d["min_rel"])
    g_min = (d["min_inc"] - d["min_rel"]) / d["min_inc"]
    g_min2 = (d["min_inc"] - piso) / d["min_inc"]
    return {"g_max": g_max, "tope": tope, "g_max2": g_max2, "piso": piso, "g_min": g_min, "g_min2": g_min2,
            "dif_max": d["max_rel"] - d["max_inc"], "dif_min": d["min_inc"] - d["min_rel"]}


def ej4():
    d = E4
    seg = {n: 2 ** n / d["por_segundo"] for n in d["n"]}
    k, v = d["enteras"]
    seg_ent = v ** k / d["por_segundo"]
    anio = 365 * 24 * 3600
    return {"comb": {n: 2 ** n for n in d["n"]}, "seg": seg, "dias50": seg[50] / 86400,
            "anios80": seg[80] / anio, "ent": v ** k, "anios_ent": seg_ent / anio}


def ej6():
    R = dos_variables(E6)
    vert, caras = envoltura(R["puntos"])
    A = [[a1, a2] for a1, a2, _ in caras]; b = [r for *_, r in caras]
    xh, zh = lp(E6["c"], A, b)
    R.update({"envoltura": vert, "caras": caras, "xh": xh, "zh": zh, "n_puntos": len(R["puntos"])})
    return R


def ej7(enteros=True):
    d = E7
    (cap_c, k_c), (cap_f, k_f), (k_t, tope_t) = d["camion"], d["furgon"], d["tren"]
    c = [k_c, k_f, k_t]
    A = [[-cap_c, -cap_f, -1]]; b = [-d["carga"]]
    cotas = [(0, None), (0, None), (0, tope_t)]
    r = linprog(c, A_ub=A, b_ub=b, bounds=cotas, method="highs"); assert r.status == 0
    m = milp(c, constraints=LinearConstraint([[cap_c, cap_f, 1]], d["carga"], np.inf), integrality=[1, 1, 0],
             bounds=Bounds([0, 0, 0], [np.inf, np.inf, tope_t]))
    assert m.status == 0
    # enumeración: para cada número de camiones y furgones, el tren completa al menor costo
    mejor = None
    for nc in range(0, 6):
        for nf in range(0, 15):
            t = max(0.0, d["carga"] - cap_c * nc - cap_f * nf)
            if t > tope_t + TOL:
                continue
            costo = k_c * nc + k_f * nf + k_t * t
            if mejor is None or costo < mejor[0] - TOL:
                mejor = (costo, nc, nf, t)
    assert abs(mejor[0] - m.fun) < TOL
    sube = math.ceil(r.x[0])
    redondeo_fijo = k_c * sube + k_f * round(r.x[1]) + k_t * r.x[2]
    t_reopt = max(0.0, d["carga"] - cap_c * sube)
    redondeo_reopt = k_c * sube + k_t * t_reopt
    return {"lp_x": list(r.x), "lp_z": r.fun, "x": [int(round(m.x[0])), int(round(m.x[1])), float(m.x[2])],
            "z": m.fun, "sube": sube, "redondeo_fijo": redondeo_fijo, "t_reopt": t_reopt,
            "redondeo_reopt": redondeo_reopt, "baja_falta": d["carga"] - cap_c * math.floor(r.x[0]) - tope_t,
            "gap": (m.fun - r.fun) / m.fun}


def ej8():
    c = E8["c"]
    xa, za = lp(c, [[1, 1, 1]], [1], cotas=[(0, 1)] * 3)
    xb, zb = lp(c, [[1, 1, 0], [1, 0, 1], [0, 1, 1]], [1, 1, 1], cotas=[(0, 1)] * 3)
    ent = max(sum(ci * vi for ci, vi in zip(c, v)) for v in itertools.product((0, 1), repeat=3) if sum(v) <= 1)
    mismos = all((sum(v) <= 1) == (v[0] + v[1] <= 1 and v[0] + v[2] <= 1 and v[1] + v[2] <= 1)
                 for v in itertools.product((0, 1), repeat=3))
    assert mismos and abs(za - ent) < TOL
    return {"xa": xa, "za": za, "xb": xb, "zb": zb, "ent": ent, "n_ent": 4}


def ej9():
    d = E9
    x, z = lp(d["c"], d["A"], d["b"])
    piso_u = [math.floor(v + 1e-9) for v in x]
    xi_u, zi_u = entero(d["c"], d["A"], d["b"])
    L = d["lote"]
    cL = [v * L for v in d["c"]]; AL = [[v * L for v in f] for f in d["A"]]
    xl = [v / L for v in x]
    piso_l = [math.floor(v + 1e-9) for v in xl]
    z_piso_l = float(np.dot(cL, piso_l))
    xi_l, zi_l = entero(cL, AL, d["b"])
    cota_l = float(np.dot(cL, [a - b for a, b in zip(xl, piso_l)]))
    assert abs((z - z_piso_l) - cota_l) < 1e-6
    # comprobación por enumeración de los lotes
    best = max((float(np.dot(cL, p)), p) for p in itertools.product(range(0, 25), range(0, 25), range(0, 15))
               if factible(p, AL, d["b"]))
    assert abs(best[0] - zi_l) < TOL
    return {"x": x, "z": z, "piso_u": piso_u, "z_piso_u": float(np.dot(d["c"], piso_u)), "xi_u": xi_u, "zi_u": zi_u,
            "cota_u": sum(d["c"]), "xl": xl, "piso_l": piso_l, "z_piso_l": z_piso_l, "xi_l": xi_l, "zi_l": zi_l,
            "cota_l": cota_l, "cota_l_bruta": sum(cL),
            "perdida_u": z - zi_u, "perdida_l": z - zi_l, "perdida_piso_l": z - z_piso_l,
            "uso_int_l": [float(np.dot(f, xi_l)) for f in AL]}


def ej10():
    d = E10
    C, H, T = d["costo"], d["horas"], d["tope"]
    c = [C[i][j] for i in range(3) for j in range(3)]
    h = [H[i][j] for i in range(3) for j in range(3)]
    Aeq = [[1 if k // 3 == i else 0 for k in range(9)] for i in range(3)] + [[1 if k % 3 == j else 0 for k in range(9)] for j in range(3)]
    r = linprog(c, A_eq=Aeq, b_eq=[1] * 6, bounds=[(0, 1)] * 9, method="highs")
    assert r.status == 0 and np.all(np.abs(r.x - np.round(r.x)) < 1e-9)
    r2 = linprog(c, A_ub=[h], b_ub=[T], A_eq=Aeq, b_eq=[1] * 6, bounds=[(0, 1)] * 9, method="highs")
    assert r2.status == 0
    perms = sorted((sum(C[i][p[i]] for i in range(3)), sum(H[i][p[i]] for i in range(3)), p)
                   for p in itertools.permutations(range(3)))
    base = perms[0]
    assert abs(base[0] - r.fun) < TOL
    con = [q for q in perms if q[1] <= T]
    m = milp(c, constraints=[LinearConstraint(Aeq, [1] * 6, [1] * 6), LinearConstraint([h], -np.inf, T)],
             integrality=np.ones(9), bounds=Bounds(0, 1))
    assert m.status == 0 and abs(m.fun - con[0][0]) < TOL
    return {"base": base, "lp": r.fun, "lp_x": np.round(r.x).astype(int).reshape(3, 3).tolist(),
            "rel2": r2.fun, "rel2_x": np.round(r2.x, 6).reshape(3, 3).tolist(), "ent2": con[0], "perms": perms,
            "n_con": len(con)}


def caso_local():
    m = caso_mod()
    C = m.calcular()["u1"]
    caja = m.CAJA
    margen = [v * caja for v in m.MARGEN]
    A = [[v * caja for v in fila] for fila in (m.SEG_EST, m.SEG_PLA, m.TINTA_G)]
    tope = [math.floor(v / caja) for v in m.DEMANDA_MAX]
    # relajación del modelo tal como se escribe en OPL (24·cajas ≤ demanda) y la del modelo con el tope
    # ya redondeado (cajas ≤ 21): mismo conjunto entero, relajación más ajustada
    x, z = lp(margen, A, m.CAP, cotas=[(0, v / caja) for v in m.DEMANDA_MAX])
    x_aj, z_aj = lp(margen, A, m.CAP, cotas=[(0, t) for t in tope])
    piso = [math.floor(v + 1e-9) for v in x]
    cerca = [round(v) for v in x]
    viola_cerca = [k for k, (f, b) in enumerate(zip(A, m.CAP)) if np.dot(f, cerca) > b + TOL]
    viola_tope = [k for k in range(5) if cerca[k] * caja > m.DEMANDA_MAX[k]]
    xi, zi = entero(margen, A, m.CAP, ub=np.array(tope, float))
    # comprobación por enumeración: para cada (polerones, doble, bolsas, gorros) las poleras al máximo
    mejor = None
    for x2 in range(tope[1] + 1):
        for x3 in range(tope[2] + 1):
            for x4 in range(tope[3] + 1):
                for x5 in range(tope[4] + 1):
                    resto = [b - (f[1] * x2 + f[2] * x3 + f[3] * x4 + f[4] * x5) for f, b in zip(A, m.CAP)]
                    if min(resto) < 0:
                        continue
                    x1 = min(tope[0], *[math.floor(r / f[0] + 1e-9) for r, f in zip(resto, A)])
                    v = margen[0] * x1 + margen[1] * x2 + margen[2] * x3 + margen[3] * x4 + margen[4] * x5
                    if mejor is None or v > mejor[0]:
                        mejor = (v, [x1, x2, x3, x4, x5], 1)
                    elif v == mejor[0]:
                        mejor = (mejor[0], mejor[1], mejor[2] + 1)
    assert abs(mejor[0] - zi) < TOL and mejor[1] == xi and mejor[2] == 1, mejor
    uso = lambda p: [float(np.dot(f, p)) for f in A]
    return {"cajas_lp": x, "z_lp": z, "x_aj": x_aj, "z_aj": z_aj, "piso": piso, "z_piso": float(np.dot(margen, piso)), "cerca": cerca,
            "viola_cerca": viola_cerca, "viola_tope": viola_tope, "xi": xi, "zi": zi, "tope": tope,
            "uso_lp": uso(x), "uso_piso": uso(piso), "uso_int": uso(xi), "uso_cerca": uso(cerca), "cap": m.CAP,
            "unidades_int": [v * caja for v in xi], "margen_caja": margen, "C": C,
            "pierde_piso": z - float(np.dot(margen, piso)), "pierde_int": z - zi,
            "gana_int": zi - float(np.dot(margen, piso)), "unico": mejor[2] == 1,
            "cota_piso": float(np.dot(margen, [a - b for a, b in zip(x, piso)]))}


def resultados():
    return {"ej": ejemplo(), "e2": ej2(), "e3": dos_variables(E3), "e4": ej4(), "e5": dos_variables(E5, "min", ge=True),
            "e6": ej6(), "e7": ej7(), "e8": ej8(), "e9": ej9(), "e10": ej10(), "caso": caso_local()}


# ---------------------------------------------------------------- OPL
def comparar_con_opl(R):
    pruebas = [("u01_eventos.mod", None, R["ej"]["zi"], {"x[1]": R["ej"]["xi"][0], "x[2]": R["ej"]["xi"][1]}),
               ("u01_e07_fruta.mod", None, R["e7"]["z"], {"camiones": R["e7"]["x"][0], "furgones": R["e7"]["x"][1],
                                                         "toneladas_tren": R["e7"]["x"][2]}),
               ("u01_estampa_cajas.mod", "u01_estampa_cajas.dat", R["caso"]["zi"],
                {f"cajas[{p}]": v for p, v in zip(["poleras", "polerones", "doble", "bolsas", "gorros"], R["caso"]["xi"])})]
    for mod, dat, z, vals in pruebas:
        r = correr(MODELOS / mod, MODELOS / dat if dat else None)
        if r is None:
            print("OPL: oplrun no está instalado; se comparan solo las cifras de Python")
            return None
        assert r["codigo"] == 0 and r["objetivo"] is not None, (mod, r["salida"][-400:])
        assert abs(r["objetivo"] - z) < 1e-4, (mod, r["objetivo"], z)
        for k, v in vals.items():
            assert abs(r["valores"][k] - v) < 1e-6, (mod, k, r["valores"].get(k), v)
    # la relajación: el mismo .mod con float+
    tmp = Path(tempfile.mkdtemp(prefix="u01_"))
    try:
        mod = (MODELOS / "u01_estampa_cajas.mod").read_text(encoding="utf-8")
        assert "dvar int+ cajas[Prendas];" in mod
        f = tmp / "relajado.mod"; f.write_text(mod.replace("dvar int+", "dvar float+"), encoding="utf-8")
        r = correr(f, MODELOS / "u01_estampa_cajas.dat")
        assert abs(r["objetivo"] - R["caso"]["z_lp"]) < 1e-3, r["objetivo"]
        # pedir .dual en el modelo entero
        g = tmp / "dual.mod"
        g.write_text(mod.replace('writeln("margen = ", Margen);',
                                 'writeln("margen = ", Margen);\n  writeln("dual = ", Capacidad["planchado"].dual);'),
                     encoding="utf-8")
        r = correr(g, MODELOS / "u01_estampa_cajas.dat")
        assert "dual = undefined" in r["salida"], r["salida"][-500:]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("OPL: 3 modelos enteros y su relajación float+ coinciden con Python; .dual queda undefined")
    return True


# ---------------------------------------------------------------- figuras SVG
TINTA, SUAVE, ACENTO = "#2B2F33", "#5F656B", "#E2622A"
AZUL, VERDE, MORADO = "#1F5F8B", "#2E7D4F", "#8A4FA3"
FUENTE = "Segoe UI, Roboto, Arial, sans-serif"


class Lienzo:
    def __init__(self, x0, y0, w, h, xlim, ylim):
        self.x0, self.y0, self.w, self.h, self.xlim, self.ylim = x0, y0, w, h, xlim, ylim
        self.sx = w / (xlim[1] - xlim[0]); self.sy = h / (ylim[1] - ylim[0]); self.p = []

    def px(self, x, y):
        return self.x0 + (x - self.xlim[0]) * self.sx, self.y0 + self.h - (y - self.ylim[0]) * self.sy

    def texto(self, X, Y, t, color=TINTA, tam=12, ancla="start", peso="normal"):
        self.p.append(f'<text x="{X:.1f}" y="{Y:.1f}" font-family="{FUENTE}" font-size="{tam}" fill="{color}" '
                      f'text-anchor="{ancla}" font-weight="{peso}" stroke="#FFFFFF" stroke-width="3.5" '
                      f'paint-order="stroke" stroke-linejoin="round">{t}</text>')

    def ejes(self, ex, ey):
        x0, y0 = self.px(self.xlim[0], self.ylim[0]); x1, _ = self.px(self.xlim[1], 0); _, y1 = self.px(0, self.ylim[1])
        for t in range(self.xlim[0], self.xlim[1] + 1):
            X, _ = self.px(t, 0)
            self.p.append(f'<line x1="{X:.1f}" y1="{y1:.1f}" x2="{X:.1f}" y2="{y0:.1f}" stroke="#EEECE9"/>')
            self.p.append(f'<text x="{X:.1f}" y="{y0 + 16:.1f}" font-family="{FUENTE}" font-size="11" fill="{SUAVE}" text-anchor="middle">{t}</text>')
        for t in range(self.ylim[0], self.ylim[1] + 1):
            _, Y = self.px(0, t)
            self.p.append(f'<line x1="{x0:.1f}" y1="{Y:.1f}" x2="{x1:.1f}" y2="{Y:.1f}" stroke="#EEECE9"/>')
            self.p.append(f'<text x="{x0 - 7:.1f}" y="{Y + 4:.1f}" font-family="{FUENTE}" font-size="11" fill="{SUAVE}" text-anchor="end">{t}</text>')
        self.p.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1 + 6:.1f}" y2="{y0:.1f}" stroke="{TINTA}" stroke-width="1.3"/>')
        self.p.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x0:.1f}" y2="{y1 - 6:.1f}" stroke="{TINTA}" stroke-width="1.3"/>')
        self.texto(x1 + 4, y0 - 8, ex, TINTA, 12, "end", "600"); self.texto(x0 + 6, y1 - 4, ey, TINTA, 12, "start", "600")

    def poligono(self, pts, relleno, opac, borde="none", guion=None):
        d = " ".join(f"{self.px(*q)[0]:.1f},{self.px(*q)[1]:.1f}" for q in pts)
        g = f' stroke-dasharray="{guion}"' if guion else ""
        self.p.append(f'<polygon points="{d}" fill="{relleno}" fill-opacity="{opac}" stroke="{borde}" stroke-width="2"{g}/>')

    def recta(self, a1, a2, b, color, etiqueta, t=0.5, dx=6, dy=-6, ancla="start"):
        (xa, xb), (ya, yb) = self.xlim, self.ylim
        cand = []
        if abs(a2) > 1e-12:
            cand += [(x, (b - a1 * x) / a2) for x in (xa, xb)]
        if abs(a1) > 1e-12:
            cand += [((b - a2 * y) / a1, y) for y in (ya, yb)]
        cand = sorted({(round(p[0], 9), round(p[1], 9)) for p in cand if xa - 1e-9 <= p[0] <= xb + 1e-9 and ya - 1e-9 <= p[1] <= yb + 1e-9})
        P, Q = self.px(*cand[0]), self.px(*cand[-1])
        self.p.append(f'<line x1="{P[0]:.1f}" y1="{P[1]:.1f}" x2="{Q[0]:.1f}" y2="{Q[1]:.1f}" stroke="{color}" stroke-width="1.8"/>')
        self.texto(P[0] + t * (Q[0] - P[0]) + dx, P[1] + t * (Q[1] - P[1]) + dy, etiqueta, color, 12, ancla, "600")

    def punto(self, x, y, r=3.2, color=TINTA, borde="#FFFFFF", hueco=False):
        X, Y = self.px(x, y)
        if hueco:
            self.p.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="#FFFFFF" stroke="{color}" stroke-width="2"/>')
        else:
            self.p.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="{color}" stroke="{borde}" stroke-width="1.5"/>')

    def cruz(self, x, y, color=ACENTO):
        X, Y = self.px(x, y)
        self.p.append(f'<path d="M{X - 6:.1f},{Y - 6:.1f} L{X + 6:.1f},{Y + 6:.1f} M{X - 6:.1f},{Y + 6:.1f} L{X + 6:.1f},{Y - 6:.1f}" stroke="{color}" stroke-width="2.4"/>')

    def rotulo(self, x, y, t, color=TINTA, dx=8, dy=-8, ancla="start", peso="600"):
        X, Y = self.px(x, y); self.texto(X + dx, Y + dy, t, color, 12, ancla, peso)


def svg(ancho, alto, partes, titulo):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}" '
            f'role="img" aria-label="{titulo}"><title>{titulo}</title><rect width="{ancho}" height="{alto}" fill="#FFFFFF"/>'
            + "".join(partes) + "</svg>\n")


def region_lp(A, b, xmax, ymax):
    """Vértices de {A x ≤ b, x ≥ 0} dentro de la caja, ordenados."""
    filas = [(f[0], f[1], bi) for f, bi in zip(A, b)] + [(-1, 0, 0), (0, -1, 0), (1, 0, xmax), (0, 1, ymax)]
    V = []
    for (a1, a2, c1), (b1, b2, c2) in itertools.combinations(filas, 2):
        det = a1 * b2 - a2 * b1
        if abs(det) < 1e-12:
            continue
        x = (c1 * b2 - a2 * c2) / det; y = (a1 * c2 - c1 * b1) / det
        if all(f0 * x + f1 * y <= r + 1e-9 for f0, f1, r in filas):
            V.append((x, y))
    cx = sum(v[0] for v in V) / len(V); cy = sum(v[1] for v in V) / len(V)
    return sorted(set((round(v[0], 9), round(v[1], 9)) for v in V), key=lambda v: math.atan2(v[1] - cy, v[0] - cx))


def ordenar(pts):
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    return sorted(pts, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))


def fig_ejemplo(E):
    L = Lienzo(60, 24, 470, 400, (0, 6), (0, 7))
    L.ejes("toldos x₁", "módulos x₂")
    L.poligono(region_lp(EJ["A"], EJ["b"], 6, 7), ACENTO, 0.13)
    L.poligono(ordenar(E["envoltura"]), "none", 0, VERDE, "6 4")
    L.recta(2, 7, 48, AZUL, "bodega: 2x₁ + 7x₂ ≤ 48", t=0.62, dx=0, dy=-10)
    L.recta(9, 4, 41, MORADO, "presupuesto: 9x₁ + 4x₂ ≤ 41", t=0.78, dx=10, dy=-4)
    for p in E["puntos"]:
        L.punto(*p)
    L.punto(*E["x"], 6, ACENTO)
    L.rotulo(*E["x"], f"relajación {par(E['x'])}", ACENTO, 10, -6)
    L.cruz(*E["cercano"]); L.rotulo(*E["cercano"], f"al más cercano {par(E['cercano'])}: infactible", ACENTO, 12, 36)
    piso = E["esquinas"][0]["p"]
    L.punto(*piso, 6, AZUL, hueco=True); L.rotulo(*piso, f"hacia abajo {par(piso)}", AZUL, -10, 18, "end")
    L.punto(*E["xi"], 6, VERDE); L.rotulo(*E["xi"], f"óptimo entero {par(E['xi'])}", VERDE, 8, -10)
    X, Y = L.px(4.25, 3.3)
    L.texto(X, Y, "verde punteada:", VERDE, 11, "start", "600")
    L.texto(X, Y + 15, "envoltura convexa", VERDE, 11, "start", "600")
    return svg(600, 460, L.p, "Toldos y módulos: relajación, redondeos y óptimo entero")


def fig_e6(E):
    L = Lienzo(56, 20, 380, 300, (0, 4), (0, 4))
    L.ejes("x₁", "x₂")
    L.poligono(region_lp(E6["A"], E6["b"], 4, 4), ACENTO, 0.13)
    L.poligono(ordenar(E["envoltura"]), VERDE, 0.16, VERDE)
    L.recta(5, 3, 16, AZUL, "5x₁ + 3x₂ ≤ 16", t=0.86, dx=8, dy=0)
    L.recta(-1, 2, 5, MORADO, "−x₁ + 2x₂ ≤ 5", t=0.55, dx=-6, dy=-8, ancla="end")
    for p in E["puntos"]:
        L.punto(*p)
    L.punto(*E["x"], 6, ACENTO); L.rotulo(*E["x"], f"relajación {par(E['x'])}", ACENTO, 10, -8)
    L.punto(*E["xi"], 6, VERDE); L.rotulo(*E["xi"], f"óptimo entero {par(E['xi'])}", VERDE, -10, -10, "end")
    return svg(470, 360, L.p, "Región de la relajación y envoltura convexa de los puntos enteros")


# ---------------------------------------------------------------- revisión
def esperados(R):
    s = []
    E = R["ej"]
    s += [pesos(E["z"]), par(E["x"]), pesos(E["zi"]), par(E["xi"]), par(E["esquinas"][0]["p"]), pesos(E["esquinas"][0]["z"]),
          par(E["cercano"]), pct(E["gap"]), pesos(E["perdida_piso"]), pesos(E["pierde_redondeo"]), str(E["n_puntos"]),
          pesos(E["segundo"][1]), par(E["segundo"][0])]
    for q in E["esquinas"]:
        s.append(f"| {par(q['p'])} |")
    s += [num(v) for v in E["uso_int"]] + [num(v) for v in E["uso_cercano"]]
    s += [f"{a1}x_1 + {a2}x_2 \\le {r}".replace("1x_", "x_").replace("+ -", "- ") for a1, a2, r in E["caras"] if a1 > 0 and a2 > 0]
    e = R["e2"]; s += [pct(e["g_max"], 2), pesos(e["tope"]), pct(e["g_max2"], 2), str(e["piso"]), pct(e["g_min"], 2),
                       pct(e["g_min2"], 2), pesos(e["dif_max"])]
    e = R["e3"]; s += [par(e["x"]), num(e["z"], 2), par(e["xi"]), num(e["zi"]), pct(e["gap"]), par(e["esquinas"][0]["p"]),
                       num(e["esquinas"][0]["z"]), par(e["segundo"][0]), num(e["segundo"][1]), str(len(e["puntos"]))]
    e = R["e4"]; s += [fmt(e["comb"][30]), fmt(e["seg"][30], 2) + " s", fmt(e["dias50"], 1) + " días",
                       fmt(e["anios80"] / 1e6, 1) + " millones de años", fmt(e["anios_ent"] / 1e3, 0) + " mil años"]
    e = R["e5"]; s += [par(e["x"]), pesos(e["z"]), par(e["xi"]), pesos(e["zi"]), pct(e["gap"]), par(e["esquinas"][3]["p"]),
                       pesos(e["esquinas"][3]["z"]), par(e["cercano"]), pesos(e["segundo"][1]), par(e["segundo"][0])]
    e = R["e6"]; s += [par(e["x"]), num(e["z"], 2), par(e["xi"]), num(e["zi"]), str(e["n_puntos"]),
                       "x_1 + x_2 \\le 4", "2x_1 + x_2 \\le 6", "-x_1 + x_2 \\le 2"]
    s += [", ".join(par(v, 0) for v in sorted(e["envoltura"]))]
    e = R["e7"]; s += [pesos(e["lp_z"]), num(e["lp_x"][0], 4), pesos(e["z"]), pesos(e["redondeo_fijo"]),
                       pesos(e["redondeo_reopt"]), num(e["t_reopt"]) + " t", pct(e["gap"]), num(e["baja_falta"]) + " t"]
    e = R["e8"]; s += [num(e["za"]), num(e["zb"]), "(0,5; 0,5; 0,5)"]
    e = R["e9"]; s += [f"({num(e['x'][0])}; {num(e['x'][1])}; {num(e['x'][2])})", pesos(e["z"]), pesos(e["zi_u"]),
                       pesos(e["perdida_u"]), pesos(e["cota_u"]), f"({num(e['xl'][0], 3)}; {num(e['xl'][1], 3)}; 0)",
                       f"({e['piso_l'][0]}; {e['piso_l'][1]}; {e['piso_l'][2]})", pesos(e["z_piso_l"]),
                       f"({e['xi_l'][0]}; {e['xi_l'][1]}; {e['xi_l'][2]})", pesos(e["zi_l"]), pesos(e["cota_l"]),
                       pesos(e["perdida_l"]), pct(e["perdida_l"] / e["z"], 1), pct(e["perdida_u"] / e["z"], 3),
                       f"({e['xi_u'][0]}; {e['xi_u'][1]}; {e['xi_u'][2]})", pesos(e["perdida_piso_l"])]
    e = R["e10"]; s += [pesos(e["base"][0] * 1000), str(e["base"][1]) + " horas", pesos(e["rel2"] * 1000),
                        pesos(e["ent2"][0] * 1000), str(e["ent2"][1]) + " horas"]
    c = R["caso"]
    s += [num(v, 2) for v in c["cajas_lp"]] + [pesos(c["z_aj"]), pesos(c["z_lp"]), pesos(c["z_piso"]), pesos(c["zi"]),
          pesos(c["pierde_piso"]), pesos(c["pierde_int"]), pesos(c["gana_int"]), pct(c["pierde_piso"] / c["z_lp"], 2),
          pct(c["pierde_int"] / c["z_lp"], 2), pesos(c["cota_piso"])]
    s += [" | ".join(str(v) for v in c["xi"]), " | ".join(str(v) for v in c["piso"]), " | ".join(str(v) for v in c["cerca"])]
    s += [fmt(v) for v in c["uso_int"]] + [fmt(v) for v in c["uso_piso"]] + [fmt(v) for v in c["uso_cerca"]]
    s += [fmt(v) for v in c["unidades_int"]] + [fmt(v) for v in c["margen_caja"]]
    return s


def cadena(R):
    C, c = R["caso"]["C"], R["caso"]
    ok = all(abs(a - b) < TOL for a, b in zip(C["cajas_lp"], c["cajas_lp"]))
    ok &= C["redondeo_abajo"] == c["piso"] and C["cajas_entero"] == c["xi"]
    ok &= abs(C["margen_redondeo"] - c["z_piso"]) < TOL and abs(C["margen_entero"] - c["zi"]) < TOL
    ok &= abs(C["margen_lp"] - c["z_lp"]) < 1e-6
    print("CADENA:", "OK, la pieza del caso calza (cajas, redondeo y óptimo entero)" if ok else "NO calza")
    return ok


def codigo_en_md(md):
    faltan = []
    for f in ["u01_eventos.mod", "u01_estampa_cajas.mod", "u01_estampa_cajas.dat", "u01_e07_fruta.mod"]:
        for linea in (MODELOS / f).read_text(encoding="utf-8").splitlines():
            if linea.strip() and linea.rstrip() not in md:
                faltan.append(f"{f}: {linea.strip()}")
    return faltan


if __name__ == "__main__":
    R = resultados()
    for k, v in R.items():
        print(f"== {k}")
        for kk, vv in v.items():
            if kk in ("puntos", "perms", "C"):
                continue
            print(f"   {kk}: {vv}")
    if not cadena(R):
        sys.exit(1)
    comparar_con_opl(R)
    FIGURAS.mkdir(parents=True, exist_ok=True)
    (FIGURAS / "u01_eventos.svg").write_text(fig_ejemplo(R["ej"]), encoding="utf-8")
    (FIGURAS / "u01_e06_envoltura.svg").write_text(fig_e6(R["e6"]), encoding="utf-8")
    print("FIGURAS: u01_eventos.svg y u01_e06_envoltura.svg")
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md_n]
        faltan += codigo_en_md(md)
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
