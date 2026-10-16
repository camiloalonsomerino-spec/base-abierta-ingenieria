"""Unidad 2 · Variables binarias I: decisiones, dependencias, mochila y asignación.

Recalcula todas las cifras de la unidad desde los datos; con --revisar las busca en el .md.

1. Cada problema se resuelve por enumeración completa (son chicos) y con scipy milp; los dos tienen que
   coincidir, y el óptimo tiene que ser único cuando el texto lo da como único.
2. Si hay CPLEX (oplrun), corre los modelos `modelos/u02_*.mod` con herramientas/opl.py y exige que el
   objetivo y las decisiones coincidan con Python.
3. Compara la pieza del caso integrador con `caso_estampa_sur_red.py` (debe imprimir CADENA: OK).
4. Dibuja la figura de las reglas del ejemplo en `unidades/figuras/`.

    python u02_binarias_i.py            # imprime resultados y redibuja la figura
    python u02_binarias_i.py --revisar  # además busca cada cifra en el .md
"""
from pathlib import Path
import importlib.util, itertools, math, sys

import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
FIGURAS = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "02-binarias-decisiones-y-mochila.md"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402

TOL = 1e-6


def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x, dec=0):
    return ("−" if x < 0 else "") + "$" + fmt(abs(x), dec)


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def num(x, maxdec=2):
    if abs(x - round(x)) < 1e-9:
        return fmt(round(x), 0)
    for d in range(1, maxdec + 1):
        if abs(x - round(x, d)) < 1e-9:
            return fmt(x, d)
    return fmt(x, maxdec)


def lista(conj):
    """{1, 3, 4} -> «1, 3, 4»"""
    return ", ".join(str(v) for v in sorted(conj))


# ---------------------------------------------------------------- datos (originales)
# Ejemplo · cooperativa de agua potable rural, seis proyectos (millones de pesos)
COOP = {"nombres": ["estanque nuevo", "bomba solar", "medidores", "red al sector alto", "cloración", "telemetría"],
        "inv": [10, 39, 16, 26, 8, 15], "van": [18, 23, 9, 17, 13, 12], "B": 75, "k": 4}
REGLAS = {  # x indexado desde 0: proyecto j es x[j-1]
    "R1": ("telemetría exige medidores", lambda x: x[5] <= x[2]),
    "R2": ("la red al sector alto exige el estanque", lambda x: x[3] <= x[0]),
    "R3": ("bomba solar y cloración se excluyen", lambda x: x[1] + x[4] <= 1),
    "R4": ("al menos medidores o cloración", lambda x: x[2] + x[4] >= 1),
    "R5": ("a lo más cuatro proyectos", lambda x: sum(x) <= 4),
}
# 2.2 · seis actividades de un aniversario
E2 = {"reglas": [lambda x: x[0] <= x[1], lambda x: x[2] + x[3] <= 1, lambda x: x[4] + x[5] >= 1,
                 lambda x: sum(x) <= 4, lambda x: x[4] == x[0], lambda x: 1 - x[3] <= x[2]]}
# 2.4 · mochila: equipos de un carro de comida (kg y miles de pesos de venta extra)
E4 = {"nombres": ["freidora extra", "plancha", "máquina de jugos", "conservadora grande", "toldo con mesas"],
      "peso": [50, 90, 70, 110, 90], "valor": [41, 54, 49, 28, 11], "W": 190}
# 2.5 · seis proyectos con reglas y un tope de k
E5 = {"u": [24, 20, 21, 7, 21, 12]}
OK5 = lambda x: x[0] + x[1] <= 1 and x[1] == x[2] and x[5] <= x[3] + x[4]
# 2.6 · cuatro cuadrillas a cuatro obras (UF)
E6 = {"C": [[16, 31, 38, 24], [27, 34, 22, 32], [20, 16, 37, 39], [31, 14, 28, 31]]}
# 2.7 · cinco conductores, tres rutas (miles de pesos)
E7 = {"C": [[23, 25, 20], [44, 53, 59], [50, 50, 29], [24, 46, 24], [32, 48, 50]]}
# 2.8 · fondo concursable: ocho iniciativas (millones, horas, puntos)
E8 = {"inv": [3, 8, 3, 5, 4, 4, 3, 7], "horas": [67, 53, 58, 65, 35, 41, 76, 32],
      "valor": [27, 18, 30, 18, 16, 13, 16, 8], "B": 24, "H": 260}
# 2.9 · ocho piezas en tres impresoras 3D (horas)
E9 = {"p": [12, 10, 9, 8, 7, 6, 6, 3], "m": 3, "juntas": (2, 7), "separadas": (1, 3)}
# 2.10 · feria de dos días: diez números artísticos (1 a 4 son de folclor)
E10 = {"costo": [3, 4, 2, 4, 5, 2, 2, 2, 5, 6], "publico": [7, 3, 8, 8, 8, 6, 6, 7, 7, 6], "folclor": [1, 2, 3, 4],
       "dias": {"sábado": (3, 13, 1), "domingo": (4, 12, 2)}}   # (números exactos, presupuesto, folclor mínimo)


def caso_mod():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_red.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def binarios(n):
    return list(itertools.product((0, 1), repeat=n))


def mejor(cands, clave, sentido=max):
    vals = sorted(cands, key=clave, reverse=(sentido is max))
    unico = len(vals) < 2 or abs(clave(vals[0]) - clave(vals[1])) > TOL
    return vals[0], unico


def elegidos(x):
    return {j + 1 for j, v in enumerate(x) if v}


# ---------------------------------------------------------------- ejemplo
def coop(reglas=tuple(REGLAS), B=None):
    d = COOP; B = d["B"] if B is None else B
    cands = [x for x in binarios(6) if np.dot(d["inv"], x) <= B and all(REGLAS[r][1](x) for r in reglas)]
    x, unico = mejor(cands, lambda x: np.dot(d["van"], x))
    return {"x": x, "set": elegidos(x), "van": int(np.dot(d["van"], x)), "inv": int(np.dot(d["inv"], x)), "unico": unico}


def ejemplo():
    d = COOP
    R = coop()
    assert R["unico"]
    logicas = [x for x in binarios(6) if all(REGLAS[r][1](x) for r in REGLAS)]
    con_pres = [x for x in logicas if np.dot(d["inv"], x) <= d["B"]]
    sin = coop(reglas=())
    precio = {r: coop(reglas=[s for s in REGLAS if s != r])["van"] - R["van"] for r in REGLAS}
    # milp con las mismas reglas escritas como desigualdades lineales
    A = [d["inv"], [0, 0, -1, 0, 0, 1], [-1, 0, 0, 1, 0, 0], [0, 1, 0, 0, 1, 0], [0, 0, -1, 0, -1, 0], [1] * 6]
    ub = [d["B"], 0, 0, 1, -1, d["k"]]
    m = milp(-np.array(d["van"]), constraints=LinearConstraint(A, -np.inf, ub), integrality=np.ones(6), bounds=Bounds(0, 1))
    assert abs(-m.fun - R["van"]) < TOL and elegidos(np.round(m.x)) == R["set"]
    rel = linprog(-np.array(d["van"]), A_ub=A, b_ub=ub, bounds=[(0, 1)] * 6, method="highs")
    top = sorted(con_pres, key=lambda x: -np.dot(d["van"], x))[:4]
    return {**R, "n_logicas": len(logicas), "n_pres": len(con_pres), "sin": sin, "precio": precio,
            "rel_z": -rel.fun, "rel_x": list(rel.x),
            "top": [(elegidos(x), int(np.dot(d["van"], x)), int(np.dot(d["inv"], x))) for x in top],
            "sobra": d["B"] - R["inv"]}


# ---------------------------------------------------------------- ejercicios
def ej2():
    fact = [x for x in binarios(6) if all(r(x) for r in E2["reglas"])]
    return {"n": len(fact), "lista": [elegidos(x) for x in fact]}


def ej3():
    # (a) «si se abre A, se abren B o C»: correcta x_A ≤ x_B + x_C ; del alumno x_A ≤ x_B y x_A ≤ x_C
    filas = binarios(3)
    correcta = [x for x in filas if x[0] <= x[1] + x[2]]
    alumno = [x for x in filas if x[0] <= x[1] and x[0] <= x[2]]
    de_mas = [x for x in correcta if x not in alumno]
    # (b) «si se hacen A y B, se hace C»: x_A + x_B − 1 ≤ x_C
    b = [x for x in filas if x[0] + x[1] - 1 <= x[2]]
    b_prohibe = [x for x in filas if x not in b]
    # (c) «A solo si B» escrito al revés: x_B ≤ x_A
    return {"correcta": len(correcta), "alumno": len(alumno), "de_mas": de_mas, "b": len(b), "b_prohibe": b_prohibe}


def ej4():
    d = E4
    n = len(d["peso"])
    cands = [x for x in binarios(n) if np.dot(d["peso"], x) <= d["W"]]
    x, unico = mejor(cands, lambda x: np.dot(d["valor"], x))
    assert unico
    razon = [v / w for v, w in zip(d["valor"], d["peso"])]
    orden = sorted(range(n), key=lambda i: -razon[i])
    carga, vor = 0, []
    for i in orden:
        if carga + d["peso"][i] <= d["W"]:
            carga += d["peso"][i]; vor.append(i + 1)
    v_vor = sum(d["valor"][i - 1] for i in vor)
    # mochila fraccionaria (relajación): voraz por razón partiendo el último
    resto, cota, frac = d["W"], 0.0, None
    for i in orden:
        if d["peso"][i] <= resto:
            resto -= d["peso"][i]; cota += d["valor"][i]
        else:
            cota += d["valor"][i] * resto / d["peso"][i]; frac = (i + 1, resto / d["peso"][i]); break
    rel = linprog(-np.array(d["valor"]), A_ub=[d["peso"]], b_ub=[d["W"]], bounds=[(0, 1)] * n, method="highs")
    assert abs(-rel.fun - cota) < TOL
    return {"set": elegidos(x), "valor": int(np.dot(d["valor"], x)), "peso": int(np.dot(d["peso"], x)),
            "razon": razon, "orden": [i + 1 for i in orden], "voraz": vor, "v_voraz": v_vor,
            "p_voraz": sum(d["peso"][i - 1] for i in vor), "cota": cota, "frac": frac, "n_fact": len(cands)}


def ej5():
    u = E5["u"]
    res = []
    for k in range(1, 6):
        cands = [x for x in binarios(6) if OK5(x) and sum(x) <= k]
        x, unico = mejor(cands, lambda x: np.dot(u, x))
        assert unico
        res.append((k, elegidos(x), int(np.dot(u, x))))
    n_fact = sum(1 for x in binarios(6) if OK5(x))
    return {"res": res, "n_fact": n_fact}


def asignacion(C, prohibe=lambda p: False):
    n, m = len(C), len(C[0])
    perms = sorted((sum(C[i][p[i]] for i in range(n)), p) for p in itertools.permutations(range(m), n) if not prohibe(p))
    assert perms[0][0] < perms[1][0] - TOL
    return perms[0]


def ej6():
    C = E6["C"]
    a = asignacion(C)
    b = asignacion(C, lambda p: p[1] == 2)
    c = asignacion(C, lambda p: p[1] == 2 or (p[0] == 0 and p[2] == 1))
    peor = max(sum(C[i][p[i]] for i in range(4)) for p in itertools.permutations(range(4)))
    # la relajación de la asignación pura sale entera
    c_ = [C[i][j] for i in range(4) for j in range(4)]
    Aeq = [[1 if k // 4 == i else 0 for k in range(16)] for i in range(4)] + [[1 if k % 4 == j else 0 for k in range(16)] for j in range(4)]
    r = linprog(c_, A_eq=Aeq, b_eq=[1] * 8, bounds=[(0, 1)] * 16, method="highs")
    assert abs(r.fun - a[0]) < TOL and np.all(np.abs(r.x - np.round(r.x)) < 1e-9)
    return {"a": a, "b": b, "c": c, "peor": peor}


def ej7():
    C = E7["C"]
    a = min((sum(C[p[j]][j] for j in range(3)), p) for p in itertools.permutations(range(5), 3))
    b = []
    for p in itertools.permutations(range(5), 2):
        for q in itertools.combinations([k for k in range(5) if k not in p], 2):
            b.append((C[p[0]][0] + C[p[1]][1] + C[q[0]][2] + C[q[1]][2], p, q))
    b.sort()
    assert b[0][0] < b[1][0]
    # milp de la versión no balanceada
    c_ = [C[i][j] for i in range(5) for j in range(3)]
    filas = [[1 if k // 3 == i else 0 for k in range(15)] for i in range(5)]
    cols = [[1 if k % 3 == j else 0 for k in range(15)] for j in range(3)]
    m = milp(c_, constraints=[LinearConstraint(filas, -np.inf, 1), LinearConstraint(cols, 1, 1)], integrality=np.ones(15), bounds=Bounds(0, 1))
    assert abs(m.fun - a[0]) < TOL
    m2 = milp(c_, constraints=[LinearConstraint(filas, -np.inf, 1), LinearConstraint(cols, [1, 1, 2], [1, 1, 2])], integrality=np.ones(15), bounds=Bounds(0, 1))
    assert abs(m2.fun - b[0][0]) < TOL
    return {"a": a, "b": b[0]}


def ej8(reglas=True, B=None):
    d = E8; B = d["B"] if B is None else B
    def ok(x):
        return np.dot(d["inv"], x) <= B and np.dot(d["horas"], x) <= d["H"] and (not reglas or (x[0] + x[1] + x[2] >= 2 and x[3] == x[4]))
    cands = [x for x in binarios(8) if ok(x)]
    x, unico = mejor(cands, lambda x: np.dot(d["valor"], x))
    return {"set": elegidos(x), "valor": int(np.dot(d["valor"], x)), "inv": int(np.dot(d["inv"], x)),
            "horas": int(np.dot(d["horas"], x)), "unico": unico, "x": x}


def ej8_todo():
    d = E8
    R = ej8(); assert R["unico"]
    S = ej8(reglas=False)
    A = [d["inv"], d["horas"], [-1, -1, -1, 0, 0, 0, 0, 0]]
    ub = [d["B"], d["H"], -2]
    Aeq = [[0, 0, 0, 1, -1, 0, 0, 0]]
    rel = linprog(-np.array(d["valor"]), A_ub=A, b_ub=ub, A_eq=Aeq, b_eq=[0], bounds=[(0, 1)] * 8, method="highs")
    m = milp(-np.array(d["valor"]), constraints=[LinearConstraint(A, -np.inf, ub), LinearConstraint(Aeq, 0, 0)], integrality=np.ones(8), bounds=Bounds(0, 1))
    assert abs(-m.fun - R["valor"]) < TOL
    frac = [(j + 1, v) for j, v in enumerate(rel.x) if TOL < v < 1 - TOL]
    return {"R": R, "S": S, "rel_z": -rel.fun, "frac": frac}


def ej9(reglas=False):
    d = E9; p = d["p"]; m = d["m"]; n = len(p)
    a1, a2 = d["juntas"]; s1, s2 = d["separadas"]
    best = None
    for asig in itertools.product(range(m), repeat=n):
        if asig[0] != 0:          # simetría: la pieza 1 va a la impresora 1
            continue
        if reglas and (asig[a1 - 1] != asig[a2 - 1] or asig[s1 - 1] == asig[s2 - 1]):
            continue
        c = [0] * m
        for t, a in zip(p, asig):
            c[a] += t
        if best is None or max(c) < best[0]:
            best = (max(c), asig, c)
    return best


def lpt(p, m):
    carga = [0] * m; quien = [[] for _ in range(m)]
    for j in sorted(range(len(p)), key=lambda j: -p[j]):
        k = carga.index(min(carga)); carga[k] += p[j]; quien[k].append(j + 1)
    return max(carga), carga, quien


def ej9_todo():
    p, m = E9["p"], E9["m"]
    opt = ej9(); opt_r = ej9(True)
    cota = max(math.ceil(sum(p) / m), max(p))
    h = lpt(p, m)
    # milp: x[j][k] binarias, C continua
    n = len(p)
    c = [0] * (n * m) + [1]
    A1 = [[1 if v // m == j else 0 for v in range(n * m)] + [0] for j in range(n)]
    A2 = [[p[v // m] if v % m == k else 0 for v in range(n * m)] + [-1] for k in range(m)]
    r = milp(c, constraints=[LinearConstraint(A1, 1, 1), LinearConstraint(A2, -np.inf, 0)],
             integrality=[1] * (n * m) + [0], bounds=Bounds([0] * (n * m + 1), [1] * (n * m) + [np.inf]))
    assert abs(r.fun - opt[0]) < TOL
    return {"opt": opt, "opt_r": opt_r, "cota": cota, "lpt": h, "total": sum(p),
            "maquinas": [[j + 1 for j in range(n) if opt[1][j] == k] for k in range(m)],
            "maquinas_r": [[j + 1 for j in range(n) if opt_r[1][j] == k] for k in range(m)]}


def ej10():
    d = E10
    N = len(d["costo"])
    folk = [1 if i + 1 in d["folclor"] else 0 for i in range(N)]
    (n1, B1, f1), (n2, B2, f2) = d["dias"]["sábado"], d["dias"]["domingo"]

    def dia(disp, n, B, f, todos=False):
        sols = [(sum(d["publico"][i] for i in s), s) for s in itertools.combinations(disp, n)
                if sum(d["costo"][i] for i in s) <= B and sum(folk[i] for i in s) >= f]
        sols.sort(reverse=True)
        return sols if todos else (sols[0] if sols else None)

    s1 = dia(range(N), n1, B1, f1, True)
    assert s1[0][0] > s1[1][0]          # el sábado aislado tiene un solo óptimo: el miope está bien definido
    s2 = dia(range(N), n2, B2, f2)
    resto = [i for i in range(N) if i not in s1[0][1]]
    m2 = dia(resto, n2, B2, f2)
    mejor_ = []
    for a in itertools.combinations(range(N), n1):
        if sum(d["costo"][i] for i in a) > B1 or sum(folk[i] for i in a) < f1:
            continue
        b = dia([i for i in range(N) if i not in a], n2, B2, f2)
        if b:
            mejor_.append((sum(d["publico"][i] for i in a) + b[0], a, b[1]))
    mejor_.sort(reverse=True)
    opt = mejor_[0]
    # milp con x[i][t]
    c = [-d["publico"][i] for i in range(N)] * 2
    filas = [[1 if (k % N) == i else 0 for k in range(2 * N)] for i in range(N)]
    cupo = [[1 if k // N == t else 0 for k in range(2 * N)] for t in range(2)]
    pres = [[d["costo"][k % N] if k // N == t else 0 for k in range(2 * N)] for t in range(2)]
    fol = [[folk[k % N] if k // N == t else 0 for k in range(2 * N)] for t in range(2)]
    r = milp(c, constraints=[LinearConstraint(filas, -np.inf, 1), LinearConstraint(cupo, [n1, n2], [n1, n2]),
                             LinearConstraint(pres, -np.inf, [B1, B2]), LinearConstraint(fol, [f1, f2], np.inf)],
             integrality=np.ones(2 * N), bounds=Bounds(0, 1))
    assert abs(-r.fun - opt[0]) < TOL
    n_opt = sum(1 for v in mejor_ if v[0] == opt[0])
    return {"miope": s1[0][0] + m2[0], "miope_sab": s1[0], "miope_dom": m2, "opt": opt, "n_opt": n_opt,
            "cota": s1[0][0] + s2[0], "aislado_sab": s1[0], "aislado_dom": s2,
            "opt_sab": sum(d["publico"][i] for i in opt[1]), "opt_dom": sum(d["publico"][i] for i in opt[2]),
            "costo_opt": (sum(d["costo"][i] for i in opt[1]), sum(d["costo"][i] for i in opt[2]))}


# ---------------------------------------------------------------- caso
def caso_local():
    m = caso_mod()
    C = m.calcular()["u2"]
    nombres = list(m.NUEVOS); inv = [m.NUEVOS[n][0] for n in nombres]; mar = [m.NUEVOS[n][1] for n in nombres]
    neto = [a - b for a, b in zip(mar, inv)]
    B = m.PRESUPUESTO_LANZAMIENTO
    k = {n: i for i, n in enumerate(nombres)}

    def ok(x, reglas=True):
        return np.dot(inv, x) <= B and (not reglas or (x[k["parches"]] <= x[k["banderines"]] and x[k["chaquetas"]] + x[k["buzos"]] <= 1))

    def opt(reglas=True, presupuesto=None):
        Bb = B if presupuesto is None else presupuesto
        cands = [x for x in binarios(6) if np.dot(inv, x) <= Bb and (not reglas or (x[k["parches"]] <= x[k["banderines"]] and x[k["chaquetas"]] + x[k["buzos"]] <= 1))]
        x, unico = mejor(cands, lambda x: np.dot(neto, x))
        return {"lanza": sorted(nombres[i] for i in range(6) if x[i]), "neto": int(np.dot(neto, x)),
                "inv": int(np.dot(inv, x)), "unico": unico}

    R = opt(); assert R["unico"]
    sin = opt(reglas=False)
    n_logicas = sum(1 for x in binarios(6) if x[k["parches"]] <= x[k["banderines"]] and x[k["chaquetas"]] + x[k["buzos"]] <= 1)
    n_fact = sum(1 for x in binarios(6) if ok(x))
    # voraz por razón neto/inversión respetando las reglas
    orden = sorted(range(6), key=lambda i: -neto[i] / inv[i])
    x = [0] * 6
    for i in orden:
        y = x[:]; y[i] = 1
        if np.dot(inv, y) <= B and y[k["chaquetas"]] + y[k["buzos"]] <= 1:
            x = y
    if x[k["parches"]] and not x[k["banderines"]]:
        x[k["parches"]] = 0
    voraz = {"lanza": sorted(nombres[i] for i in range(6) if x[i]), "neto": int(np.dot(neto, x)), "inv": int(np.dot(inv, x))}
    # relajación lineal (cota)
    A = [inv, [0] * 6, [0] * 6]
    A[1][k["parches"]] = 1; A[1][k["banderines"]] = -1
    A[2][k["chaquetas"]] = 1; A[2][k["buzos"]] = 1
    rel = linprog(-np.array(neto), A_ub=A, b_ub=[B, 0, 1], bounds=[(0, 1)] * 6, method="highs")
    m_ = milp(-np.array(neto), constraints=LinearConstraint(A, -np.inf, [B, 0, 1]), integrality=np.ones(6), bounds=Bounds(0, 1))
    assert abs(-m_.fun - R["neto"]) < TOL
    frac = {nombres[i]: v for i, v in enumerate(rel.x) if TOL < v < 1 - TOL}
    # presupuestos alternativos
    tabla = {p: opt(presupuesto=p) for p in (3_500_000, 4_500_000, 5_200_000, 6_500_000)}
    return {"C": C, "R": R, "sin": sin, "n_logicas": n_logicas, "n_fact": n_fact, "voraz": voraz, "rel_z": -rel.fun,
            "frac": frac, "tabla": tabla, "neto": dict(zip(nombres, neto)), "sobra": B - R["inv"],
            "razon": {n: neto[i] / inv[i] for i, n in enumerate(nombres)}, "orden": [nombres[i] for i in orden]}


def resultados():
    return {"ej": ejemplo(), "e2": ej2(), "e3": ej3(), "e4": ej4(), "e5": ej5(), "e6": ej6(), "e7": ej7(),
            "e8": ej8_todo(), "e9": ej9_todo(), "e10": ej10(), "caso": caso_local()}


# ---------------------------------------------------------------- OPL
def comparar_con_opl(R):
    E = R["ej"]; c = R["caso"]["R"]
    pruebas = [
        ("u02_cooperativa.mod", "u02_cooperativa.dat", E["van"], {f"x[{j}]": int(j in E["set"]) for j in range(1, 7)}),
        ("u02_lanzamientos.mod", "u02_lanzamientos.dat", c["neto"],
         {f"lanza[{n}]": int(n in c["lanza"]) for n in R["caso"]["neto"]}),
        ("u02_e08_fondo.mod", "u02_e08_fondo.dat", R["e8"]["R"]["valor"], {f"x[{j}]": int(j in R["e8"]["R"]["set"]) for j in range(1, 9)}),
        ("u02_e09_impresoras.mod", "u02_e09_impresoras.dat", R["e9"]["opt_r"][0], {}),
        ("u02_e10_feria.mod", "u02_e10_feria.dat", R["e10"]["opt"][0], {}),
    ]
    for mod, dat, z, vals in pruebas:
        r = correr(MODELOS / mod, MODELOS / dat)
        if r is None:
            print("OPL: oplrun no está instalado; se comparan solo las cifras de Python")
            return None
        assert r["codigo"] == 0 and r["objetivo"] is not None, (mod, r["salida"][-500:])
        assert abs(r["objetivo"] - z) < 1e-4, (mod, r["objetivo"], z)
        for k, v in vals.items():
            assert abs(r["valores"][k] - v) < 1e-6, (mod, k, r["valores"].get(k), v)
    print(f"OPL: {len(pruebas)} modelos con dvar boolean corridos con oplrun; coinciden con Python")
    return True


# ---------------------------------------------------------------- figura
def fig_reglas():
    TINTA, SUAVE, ACENTO, AZUL, VERDE = "#2B2F33", "#5F656B", "#E2622A", "#1F5F8B", "#2E7D4F"
    F = "Segoe UI, Roboto, Arial, sans-serif"
    pos = {1: (120, 90), 4: (120, 250), 3: (330, 90), 6: (330, 250), 2: (540, 90), 5: (540, 250)}
    p = [f'<defs><marker id="fl" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{AZUL}"/></marker></defs>']
    def flecha(a, b):  # a depende de b: a → b
        (x1, y1), (x2, y2) = pos[a], pos[b]
        L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L
        p.append(f'<line x1="{x1 + 44 * ux:.1f}" y1="{y1 + 30 * uy:.1f}" x2="{x2 - 44 * ux:.1f}" y2="{y2 - 30 * uy:.1f}" stroke="{AZUL}" stroke-width="2.2" marker-end="url(#fl)"/>')
    flecha(4, 1); flecha(6, 3)
    (x1, y1), (x2, y2) = pos[2], pos[5]
    p.append(f'<line x1="{x1}" y1="{y1 + 30}" x2="{x2}" y2="{y2 - 30}" stroke="{ACENTO}" stroke-width="2.2" stroke-dasharray="6 4"/>')
    p.append(f'<text x="{x1 + 10}" y="{(y1 + y2) / 2 + 4}" font-family="{F}" font-size="12" fill="{ACENTO}" font-weight="600">no ambos (R3)</text>')
    p.append(f'<text x="{pos[1][0] + 10}" y="{(pos[1][1] + pos[4][1]) / 2 + 4}" font-family="{F}" font-size="12" fill="{AZUL}" font-weight="600">exige (R2)</text>')
    p.append(f'<text x="{pos[3][0] + 10}" y="{(pos[3][1] + pos[6][1]) / 2 + 4}" font-family="{F}" font-size="12" fill="{AZUL}" font-weight="600">exige (R1)</text>')
    # al menos uno entre 3 y 5
    p.append(f'<path d="M{pos[3][0] + 50},{pos[3][1] + 22} C 470,150 470,190 {pos[5][0] - 50},{pos[5][1] - 18}" fill="none" stroke="{VERDE}" stroke-width="2.2" stroke-dasharray="2 4"/>')
    p.append(f'<text x="436" y="134" font-family="{F}" font-size="12" fill="{VERDE}" font-weight="600" text-anchor="start">al menos uno (R4)</text>')
    for j, (x, y) in pos.items():
        elegido = j in ejemplo()["set"]
        p.append(f'<rect x="{x - 72}" y="{y - 28}" width="144" height="56" rx="10" fill="{"#FBE7DD" if elegido else "#FFFFFF"}" stroke="{TINTA if elegido else SUAVE}" stroke-width="{2 if elegido else 1.2}"/>')
        p.append(f'<text x="{x}" y="{y - 4}" font-family="{F}" font-size="13" fill="{TINTA}" text-anchor="middle" font-weight="700">{j} · {COOP["nombres"][j - 1]}</text>')
        p.append(f'<text x="{x}" y="{y + 15}" font-family="{F}" font-size="11.5" fill="{SUAVE}" text-anchor="middle">inv. {COOP["inv"][j - 1]} · VAN {COOP["van"][j - 1]}</text>')
    p.append(f'<text x="20" y="320" font-family="{F}" font-size="12" fill="{SUAVE}">Recuadros rellenos: el óptimo. Además: presupuesto de {COOP["B"]} millones y a lo más {COOP["k"]} proyectos (R5).</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 660 340" width="660" height="340" role="img" '
            f'aria-label="Reglas entre los seis proyectos de la cooperativa"><title>Reglas entre los seis proyectos</title>'
            f'<rect width="660" height="340" fill="#FFFFFF"/>' + "".join(p) + "</svg>\n")


# ---------------------------------------------------------------- revisión
def esperados(R):
    s = []
    E = R["ej"]
    s += [f"{{{lista(E['set'])}}}", str(E["van"]) + " millones", str(E["inv"]) + " millones", str(E["n_logicas"]) + " de las 64",
          str(E["n_pres"]), f"{{{lista(E['sin']['set'])}}}", str(E["sin"]["van"]) + " millones", num(E["rel_z"]) + " millones",
          str(E["sobra"]) + " millones"]
    s += [f"| {r} | {num(v)} |" for r, v in E["precio"].items()]
    for st, v, i in E["top"]:
        s.append(f"| {{{lista(st)}}} | {i} | {v} |")
    s += [str(R["e2"]["n"]) + " de las 64"]
    e = R["e3"]; s += [f"{e['correcta']} de las 8", f"{e['alumno']} de las 8", f"{e['b']} de las 8"]
    e = R["e4"]; s += [f"{{{lista(e['set'])}}}", pesos(e["valor"] * 1000), f"{e['peso']} kg", pesos(e["v_voraz"] * 1000),
                       f"{{{lista(e['voraz'])}}}", pesos(e["cota"] * 1000), str(e["p_voraz"]) + " kg",
                       num(e["frac"][1], 2), str(e["n_fact"])]
    s += [num(r, 2) for r in e["razon"]]
    e = R["e5"]
    for k, st, v in e["res"]:
        s.append(f"| {k} | {{{lista(st)}}} | {v} |")
    s.append(str(e["n_fact"]) + " de las 64")
    e = R["e6"]; s += [f"{e['a'][0]} UF", f"{e['b'][0]} UF", f"{e['c'][0]} UF", f"{e['peor']} UF"]
    e = R["e7"]; s += [pesos(e["a"][0] * 1000), pesos(e["b"][0] * 1000)]
    e = R["e8"]; s += [f"{{{lista(e['R']['set'])}}}", f"{e['R']['valor']} puntos", f"{e['R']['horas']} horas",
                       f"{e['R']['inv']} millones", f"{{{lista(e['S']['set'])}}}", f"{e['S']['valor']} puntos", num(e["rel_z"], 2)]
    e = R["e9"]; s += [f"{e['opt'][0]} horas", f"{e['lpt'][0]} horas", f"{e['cota']} horas", f"{e['opt_r'][0]} horas",
                       str(e["total"]) + " horas"]
    s += ["{" + lista(q) + "}" for q in e["maquinas"]] + ["{" + lista(q) + "}" for q in e["maquinas_r"]]
    s += ["{" + lista(q) + "}" for q in e["lpt"][2]]
    e = R["e10"]; s += [f"{e['miope']} ≤ {e['opt'][0]} ≤ {e['cota']}", f"= {e['miope']}", f"= {e['opt'][0]}", f"= {e['cota']}", "{" + lista(i + 1 for i in e["opt"][1]) + "}",
                        "{" + lista(i + 1 for i in e["opt"][2]) + "}", "{" + lista(i + 1 for i in e["miope_sab"][1]) + "}",
                        "{" + lista(i + 1 for i in e["miope_dom"][1]) + "}", f"{e['opt_sab']} + {e['opt_dom']}",
                        f"{e['miope_sab'][0]} + {e['miope_dom'][0]}", f"{e['aislado_sab'][0]} + {e['aislado_dom'][0]}"]
    c = R["caso"]
    s += [pesos(c["R"]["neto"]), pesos(c["R"]["inv"]), pesos(c["sobra"]), str(c["n_logicas"]) + " de las 64",
          str(c["n_fact"]), pesos(c["rel_z"])]
    s += [pesos(v) for v in c["neto"].values()]
    for p, t in c["tabla"].items():
        s.append(f"| {pesos(p)} | {', '.join(t['lanza'])} | {pesos(t['inv'])} | {pesos(t['neto'])} |")
    s += [pesos(c["voraz"]["neto"]), pesos(c["sin"]["neto"])]
    return s


def cadena(R):
    C, c = R["caso"]["C"], R["caso"]["R"]
    ok = C["lanza"] == c["lanza"] and C["valor_neto"] == c["neto"] and C["inversion"] == c["inv"]
    print("CADENA:", "OK, la pieza del caso calza (lanza, inversión y valor neto)" if ok else "NO calza")
    return ok


def codigo_en_md(md):
    faltan = []
    for f in ["u02_cooperativa.mod", "u02_cooperativa.dat", "u02_lanzamientos.mod", "u02_lanzamientos.dat",
              "u02_e09_impresoras.mod"]:
        for linea in (MODELOS / f).read_text(encoding="utf-8").splitlines():
            if linea.strip() and linea.rstrip() not in md:
                faltan.append(f"{f}: {linea.strip()}")
    return faltan


if __name__ == "__main__":
    R = resultados()
    for k, v in R.items():
        print(f"== {k}")
        for kk, vv in v.items():
            if kk in ("C", "lista"):
                continue
            print(f"   {kk}: {vv}")
    if not cadena(R):
        sys.exit(1)
    comparar_con_opl(R)
    FIGURAS.mkdir(parents=True, exist_ok=True)
    (FIGURAS / "u02_cooperativa.svg").write_text(fig_reglas(), encoding="utf-8")
    print("FIGURA: u02_cooperativa.svg")
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".").replace("\\{", "{").replace("\\}", "}")
        faltan = [x for x in esperados(R) if x not in md_n]
        faltan += codigo_en_md(md)
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
