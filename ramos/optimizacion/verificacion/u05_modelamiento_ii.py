"""Unidad 5 · Modelamiento lineal II: multiperíodo, transporte y asignación.

Recalcula todas las cifras de la unidad desde los datos. Cada modelo se resuelve en Python
(scipy, HiGHS) y, si hay CPLEX instalado, también con su .mod de OPL; objetivo, variables y precios
sombra tienen que coincidir. Con --revisar busca cada resultado, tal como se escribe, en el .md.

    python u05_modelamiento_ii.py            # imprime los resultados y compara con OPL
    python u05_modelamiento_ii.py --revisar  # además los busca en el .md
    python u05_modelamiento_ii.py --figuras  # además redibuja las figuras SVG
"""
from pathlib import Path
from itertools import product
import importlib.util, sys, tempfile

import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds, linear_sum_assignment

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402

TOL = 1e-6


# ---------------------------------------------------------------- herramientas

def fmt(x, dec=0):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x, 0)


class LP:
    """Modelo lineal con nombres. Los duales salen como en OPL: cuánto cambia el objetivo
    (en su propio sentido, máx o mín) por una unidad más de lado derecho."""

    def __init__(self, sentido="min"):
        self.sentido, self.v, self.lb, self.ub, self.c, self.r, self.entera = sentido, [], [], [], {}, [], set()

    def var(self, nombre, lb=0.0, ub=None, costo=0.0, entera=False):
        self.v.append(nombre); self.lb.append(lb); self.ub.append(ub)
        self.c[nombre] = costo
        if entera:
            self.entera.add(nombre)
        return nombre

    def add(self, nombre, coef, signo, rhs):
        self.r.append((nombre, dict(coef), signo, rhs))

    def resolver(self):
        idx = {n: k for k, n in enumerate(self.v)}
        s = 1 if self.sentido == "min" else -1
        c = np.array([s * self.c[n] for n in self.v])
        filas = {"<=": [], ">=": [], "==": []}
        for nombre, coef, signo, rhs in self.r:
            fila = np.zeros(len(self.v))
            for n, a in coef.items():
                fila[idx[n]] += a
            filas[signo].append((nombre, fila, rhs))
        A_ub = [f for _, f, _ in filas["<="]] + [-f for _, f, _ in filas[">="]]
        b_ub = [b for *_, b in filas["<="]] + [-b for *_, b in filas[">="]]
        A_eq = [f for _, f, _ in filas["=="]]
        b_eq = [b for *_, b in filas["=="]]
        if self.entera:
            cons = []
            if A_ub:
                cons.append(LinearConstraint(np.array(A_ub), -np.inf, np.array(b_ub)))
            if A_eq:
                cons.append(LinearConstraint(np.array(A_eq), np.array(b_eq), np.array(b_eq)))
            integ = np.array([1 if n in self.entera else 0 for n in self.v])
            lb = np.array(self.lb, float); ub = np.array([np.inf if u is None else u for u in self.ub], float)
            r = milp(c, constraints=cons, integrality=integ, bounds=Bounds(lb, ub))
            assert r.status == 0, r.message
            x = {n: r.x[idx[n]] for n in self.v}
            return {"z": s * r.fun, "x": x, "dual": {}}
        r = linprog(c, A_ub=np.array(A_ub) if A_ub else None, b_ub=b_ub or None,
                    A_eq=np.array(A_eq) if A_eq else None, b_eq=b_eq or None,
                    bounds=list(zip(self.lb, self.ub)), method="highs")
        assert r.status == 0, r.message
        dual = {}
        mu = list(r.ineqlin.marginals) if A_ub else []
        for k, (nombre, _, _) in enumerate(filas["<="]):
            dual[nombre] = s * mu[k]
        for k, (nombre, _, _) in enumerate(filas[">="]):
            dual[nombre] = -s * mu[len(filas["<="]) + k]
        for k, (nombre, _, _) in enumerate(filas["=="]):
            dual[nombre] = s * r.eqlin.marginals[k]
        x = {n: r.x[idx[n]] for n in self.v}
        holgura = {}
        for signo, lst in filas.items():
            for nombre, fila, rhs in lst:
                act = float(fila @ r.x)
                holgura[nombre] = rhs - act if signo == "<=" else (act - rhs if signo == ">=" else 0.0)
        return {"z": s * r.fun, "x": x, "dual": {k: v + 0.0 for k, v in dual.items()}, "holgura": holgura}


def comparar_opl(nombre, mod, dat, esperado, R_opl):
    """Corre el .mod en OPL y compara cada clave «clave = valor» con lo calculado en Python."""
    r = correr(MODELOS / mod, MODELOS / dat if dat else None)
    if r is None:
        R_opl[nombre] = "sin CPLEX"
        return True
    malas = []
    for k, v in esperado.items():
        o = r["valores"].get(k)
        if not isinstance(o, float) or abs(o - v) > 1e-4 * max(1, abs(v)):
            malas.append((k, v, o))
    R_opl[nombre] = "OK" if not malas else malas
    return not malas


# ---------------------------------------------------------------- datos (originales; pasados por colisiones.py)

# Ejemplo resuelto · Pellet del Laja planifica abril a julio
PELLETS = {"meses": ["abril", "mayo", "junio", "julio"], "demanda": [1850, 2700, 3450, 3150],
           "cap_reg": 2480, "c_reg": 2140, "cap_ext": 690, "c_ext": 2590, "c_inv": 95,
           "bodega": 1250, "inv0": 240, "inv_fin": 180}

# Sección 3 · transporte no balanceado: huevos de dos granjas a tres supermercados
HUEVOS = {"orig": ["Limache", "Casablanca"], "dest": ["Vina", "Valparaiso", "Quilpue"],
          "oferta": [900, 700], "demanda": [620, 480, 350],
          "costo": [[58, 72, 41], [66, 49, 83]]}

# 5.1 · mermelada: plan dado, completar inventario
E51 = {"prod": [500, 500, 500, 500], "dem": [380, 520, 610, 450], "inv0": 60, "h": 40, "dem3_b": 720}

# 5.2 · leche de tres predios a tres plantas (balanceado)
E52 = {"orig": ["PredioA", "PredioB", "PredioC"], "dest": ["Planta1", "Planta2", "Planta3"],
       "oferta": [4200, 3100, 4700], "demanda": [3600, 4300, 4100],
       "costo": [[18, 25, 31], [22, 15, 27], [29, 20, 14]]}

# 5.3 · asignación de cuatro buses a cuatro recorridos (minutos en vacío)
E53 = {"orig": ["B1", "B2", "B3", "B4"], "dest": ["R1", "R2", "R3", "R4"],
       "costo": [[14, 9, 12, 17], [11, 13, 16, 10], [15, 12, 8, 14], [10, 16, 13, 11]]}

# 5.5 · bicicletas eléctricas con atraso permitido
E55 = {"dem": [120, 160, 210, 150], "cap": 170, "h": 9000, "b": 15000}

# 5.6 · transbordo de alimento para mascotas
E56 = {"plantas": ["Rancagua", "Talca"], "oferta": [1180, 870],
       "centros": ["SanBernardo", "Chillan"], "cap_centro": [2000, 960],
       "clientes": ["Santiago", "Concepcion", "Temuco"], "demanda": [780, 640, 470],
       "c_pc": [[4100, 12800], [8700, 6300]],
       "c_ck": [[2400, 14600, 20700], [13900, 3300, 9200]]}

E510_B = 20000   # 5.10 (b) · penalización por atraso más alta

# 5.7 · turnos de 8 horas en bloques de 4 horas (call center de una clínica)
E57 = {"bloques": ["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"], "req": [4, 6, 15, 13, 11, 7]}

# 5.8 · contratación y despido en una empresa de aseo industrial
E58 = {"horas": [3200, 4100, 4800, 3600], "h_por_persona": 160, "w0": 22,
       "c_contratar": 380000, "c_despedir": 520000, "sueldo": 720000}

# 5.9 · transporte multiperíodo con inventario en las plantas
E59 = {"plantas": ["Talca", "Chillan"], "clientes": ["Curico", "Linares", "LosAngeles"], "T": 3,
       "cap": [880, 690], "c_prod": [1170, 1020], "c_inv": [60, 75],
       "c_env": [[95, 117, 370], [285, 155, 138]],
       "dem": [[430, 370, 590], [380, 390, 470], [360, 415, 570]]}   # [cliente][mes]

# Caso · ampliación propia del envío: el taller y la bodega de temporada en Chillán
CASO_BODEGA = {"stock_bodega": 500, "costo_bodega": [380, 90, 310]}


# ---------------------------------------------------------------- modelos

def multiperiodo_pellets(d):
    m = LP("min")
    T = range(len(d["demanda"]))
    for t in T:
        m.var(f"R{t}", ub=d["cap_reg"], costo=d["c_reg"])
        m.var(f"E{t}", ub=d["cap_ext"], costo=d["c_ext"])
        m.var(f"I{t}", ub=d["bodega"], costo=d["c_inv"])
    for t in T:
        coef = {f"R{t}": 1, f"E{t}": 1, f"I{t}": -1}
        rhs = d["demanda"][t]
        if t == 0:
            rhs -= d["inv0"]
        else:
            coef[f"I{t-1}"] = 1
        m.add(f"balance{t}", coef, "==", rhs)
    m.add("final", {f"I{len(T)-1}": 1}, ">=", d["inv_fin"])
    return m.resolver()


def transporte(d, igualdad=False):
    m = LP("min")
    O, D = d["orig"], d["dest"]
    for i, o in enumerate(O):
        for j, k in enumerate(D):
            m.var(f"x[{o}][{k}]", costo=d["costo"][i][j])
    for i, o in enumerate(O):
        m.add(f"oferta[{o}]", {f"x[{o}][{k}]": 1 for k in D}, "==" if igualdad else "<=", d["oferta"][i])
    for j, k in enumerate(D):
        m.add(f"demanda[{k}]", {f"x[{o}][{k}]": 1 for o in O}, "==" if igualdad else ">=", d["demanda"][j])
    return m.resolver()


def inventario_dado(prod, dem, inv0):
    inv, I = [], inv0
    for p, q in zip(prod, dem):
        I = I + p - q
        inv.append(I)
    return inv


def bicicletas(d):
    m = LP("min")
    T = range(len(d["dem"]))
    for t in T:
        m.var(f"x{t}", ub=d["cap"])
        m.var(f"Ip{t}", costo=d["h"])
        m.var(f"Im{t}", costo=d["b"], ub=0 if t == len(T) - 1 else None)
    for t in T:
        coef = {f"x{t}": 1, f"Ip{t}": -1, f"Im{t}": 1}
        if t > 0:
            coef[f"Ip{t-1}"] = 1; coef[f"Im{t-1}"] = -1
        m.add(f"balance{t}", coef, "==", d["dem"][t])
    return m.resolver()


def transbordo(d):
    m = LP("min")
    P, C, K = d["plantas"], d["centros"], d["clientes"]
    for i, p in enumerate(P):
        for j, c in enumerate(C):
            m.var(f"x[{p}][{c}]", costo=d["c_pc"][i][j])
    for j, c in enumerate(C):
        for k, q in enumerate(K):
            m.var(f"y[{c}][{q}]", costo=d["c_ck"][j][k])
    for i, p in enumerate(P):
        m.add(f"oferta[{p}]", {f"x[{p}][{c}]": 1 for c in C}, "<=", d["oferta"][i])
    for j, c in enumerate(C):
        coef = {f"x[{p}][{c}]": 1 for p in P}
        coef.update({f"y[{c}][{q}]": -1 for q in K})
        m.add(f"balance[{c}]", coef, "==", 0)
        m.add(f"capCentro[{c}]", {f"x[{p}][{c}]": 1 for p in P}, "<=", d["cap_centro"][j])
    for k, q in enumerate(K):
        m.add(f"demanda[{q}]", {f"y[{c}][{q}]": 1 for c in C}, ">=", d["demanda"][k])
    return m.resolver()


def turnos(d, entera=True):
    m = LP("min")
    n = len(d["req"])
    for s in range(n):
        m.var(f"x{s}", costo=1, entera=entera)
    for b in range(n):
        m.add(f"cubre{b}", {f"x{b}": 1, f"x{(b-1) % n}": 1}, ">=", d["req"][b])
    return m.resolver()


def contratacion(d, entera=False):
    m = LP("min")
    T = range(len(d["horas"]))
    for t in T:
        m.var(f"W{t}", costo=d["sueldo"], entera=entera)
        m.var(f"H{t}", costo=d["c_contratar"], entera=entera)
        m.var(f"F{t}", costo=d["c_despedir"], entera=entera)
    for t in T:
        coef = {f"W{t}": 1, f"H{t}": -1, f"F{t}": 1}
        rhs = 0
        if t == 0:
            rhs = d["w0"]
        else:
            coef[f"W{t-1}"] = -1
        m.add(f"dotacion{t}", coef, "==", rhs)
        m.add(f"horas{t}", {f"W{t}": d["h_por_persona"]}, ">=", d["horas"][t])
    return m.resolver()


def transporte_multiperiodo(d):
    m = LP("min")
    P, K, T = d["plantas"], d["clientes"], range(1, d["T"] + 1)
    for i, p in enumerate(P):
        for t in T:
            m.var(f"Y[{p}][{t}]", ub=d["cap"][i], costo=d["c_prod"][i])
            m.var(f"Z[{p}][{t}]", costo=d["c_inv"][i])
            for j, k in enumerate(K):
                m.var(f"X[{p}][{k}][{t}]", costo=d["c_env"][i][j])
    for i, p in enumerate(P):
        for t in T:
            coef = {f"Y[{p}][{t}]": 1, f"Z[{p}][{t}]": -1}
            coef.update({f"X[{p}][{k}][{t}]": -1 for k in K})
            if t > 1:
                coef[f"Z[{p}][{t-1}]"] = 1
            m.add(f"balance[{p}][{t}]", coef, "==", 0)
    for j, k in enumerate(K):
        for t in T:
            m.add(f"demanda[{k}][{t}]", {f"X[{p}][{k}][{t}]": 1 for p in P}, ">=", d["dem"][j][t - 1])
    return m.resolver()


def produccion_como_transporte(d):
    """El plan de 5.5 como transporte: origen = mes en que se produce, destino = mes que se atiende."""
    T = len(d["dem"])
    costo = [[d["h"] * (j - i) if j >= i else d["b"] * (i - j) for j in range(T)] for i in range(T)]
    datos = {"orig": [f"prod{i+1}" for i in range(T)], "dest": [f"dem{j+1}" for j in range(T)],
             "oferta": [d["cap"]] * T, "demanda": list(d["dem"]), "costo": costo}
    return datos, transporte(datos)


def polerones(U5, cap):
    """La pieza del caso, con la capacidad como restricción para leer su precio sombra."""
    m = LP("min")
    T = range(U5["semanas"])
    for t in T:
        m.var(f"x{t}")
        m.var(f"I{t}", costo=U5["costo_inventario"])
    for t in T:
        coef = {f"x{t}": 1, f"I{t}": -1}
        if t > 0:
            coef[f"I{t-1}"] = 1
        m.add(f"balance{t}", coef, "==", U5["demanda_polerones"][t])
        m.add(f"cap{t}", {f"x{t}": 1}, "<=", cap)
        m.add(f"invmax{t}", {f"I{t}": 1}, "<=", U5["inv_max"])
    return m.resolver()


# ---------------------------------------------------------------- cálculo

def cargar_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_lp.py")
    caso = importlib.util.module_from_spec(spec); spec.loader.exec_module(caso)
    return caso


def resultados():
    R = {}
    R["pellets"] = multiperiodo_pellets(PELLETS)
    R["huevos"] = transporte(HUEVOS)
    R["e51"] = {"inv": inventario_dado(E51["prod"], E51["dem"], E51["inv0"])}
    R["e51"]["costo"] = E51["h"] * sum(R["e51"]["inv"])
    dem_b = list(E51["dem"]); dem_b[2] = E51["dem3_b"]
    R["e51"]["inv_b"] = inventario_dado(E51["prod"], dem_b, E51["inv0"])
    R["e52"] = transporte(E52, igualdad=True)
    C = np.array(E53["costo"])
    fil, col = linear_sum_assignment(C)
    asig = {"orig": E53["orig"], "dest": E53["dest"], "oferta": [1] * 4, "demanda": [1] * 4, "costo": E53["costo"]}
    R["e53"] = transporte(asig, igualdad=True)
    R["e53"]["hungaro"] = (list(zip(fil, col)), int(C[fil, col].sum()))
    R["e55"] = bicicletas(E55)
    R["e56"] = transbordo(E56)
    R["e57"] = turnos(E57)
    R["e57_lp"] = turnos(E57, entera=False)
    R["e58"] = contratacion(E58)
    R["e58_ent"] = contratacion(E58, entera=True)
    R["e59"] = transporte_multiperiodo(E59)
    R["e510_datos"], R["e510"] = produccion_como_transporte(E55)
    _, R["e510_b"] = produccion_como_transporte(dict(E55, b=E510_B))
    R["e55_b"] = bicicletas(dict(E55, b=E510_B))
    # 5.9 · cuánto vale una unidad más de capacidad en Chillán: precio en Linares menos el costo de llevarla desde Chillán
    R["e59_cap_chillan"] = [R["e59"]["dual"][f"demanda[Linares][{t}]"] - E59["c_prod"][1] - E59["c_env"][1][1]
                            for t in (1, 2, 3)]
    # 5.3 · el segundo mejor total, para ver que el óptimo es único
    C3 = E53["costo"]
    R["e53_totales"] = sorted(sum(C3[i][p[i]] for i in range(4)) for p in __import__("itertools").permutations(range(4)))

    caso = cargar_caso()
    U5 = caso.U5
    cap = caso.calcular()["u5"]["cap_semana"]
    R["caso_pol"] = polerones(U5, cap)
    R["caso_envio_simple"] = sum(p * k for p, k in zip(U5["pedido_tiendas"], U5["costo_envio"]))
    tiendas = ["Concepcion", "Chillan", "LosAngeles"]
    datos = {"orig": ["Taller", "BodegaChillan"], "dest": tiendas + ["Ficticio"],
             "oferta": [sum(U5["pedido_tiendas"]), CASO_BODEGA["stock_bodega"]],
             "demanda": list(U5["pedido_tiendas"]) + [CASO_BODEGA["stock_bodega"]],
             "costo": [list(U5["costo_envio"]) + [0], list(CASO_BODEGA["costo_bodega"]) + [0]]}
    R["caso_tr_datos"] = datos
    R["caso_tr"] = transporte(datos)
    R["caso_C"] = caso.calcular()["u5"]
    return R


def imprimir(R):
    def mostrar(nombre, s, solo_pos=True):
        print(f"== {nombre}: z = {s['z']:.4f}")
        print("   x:", {k: round(v, 4) for k, v in s["x"].items() if not solo_pos or abs(v) > 1e-7})
        if s.get("dual"):
            print("   dual:", {k: round(v, 4) for k, v in s["dual"].items()})
    mostrar("pellets", R["pellets"])
    mostrar("huevos", R["huevos"])
    print("== e51", R["e51"])
    mostrar("e52", R["e52"])
    mostrar("e53", R["e53"]); print("   húngaro:", R["e53"]["hungaro"])
    mostrar("e55", R["e55"])
    mostrar("e56", R["e56"])
    mostrar("e57", R["e57"]); mostrar("e57 lp", R["e57_lp"])
    mostrar("e58", R["e58"]); mostrar("e58 entera", R["e58_ent"])
    mostrar("e59", R["e59"])
    mostrar("e510", R["e510"])
    mostrar("caso polerones", R["caso_pol"])
    print("== caso envío simple:", R["caso_envio_simple"])
    mostrar("caso transporte", R["caso_tr"])


# ---------------------------------------------------------------- archivos .dat (se generan desde estos datos)

def _vec(v):
    return "[" + " ".join(f"{x:g}" for x in v) + "]"


def _mat(M):
    return "[\n  " + "\n  ".join(_vec(f) for f in M) + "\n]"


def _set(S):
    return "{" + ", ".join(f'"{x}"' for x in S) + "}"


def dat_transporte(d, titulo):
    return (f"/* Unidad 5 · {titulo}. Generado por verificacion/u05_modelamiento_ii.py */\n"
            f"Origenes = {_set(d['orig'])};\nDestinos = {_set(d['dest'])};\n"
            f"oferta  = {_vec(d['oferta'])};\ndemanda = {_vec(d['demanda'])};\n"
            f"costo = {_mat(d['costo'])};\n")


def dats(R):
    caso = cargar_caso(); U5 = caso.U5
    asig = {"orig": E53["orig"], "dest": E53["dest"], "oferta": [1] * 4, "demanda": [1] * 4, "costo": E53["costo"]}
    D = {
        "u05_huevos.dat": dat_transporte(HUEVOS, "sección 3, huevos de dos granjas a tres supermercados"),
        "u05_leche.dat": dat_transporte(E52, "ejercicio 5.2, leche de tres predios a tres plantas"),
        "u05_buses.dat": dat_transporte(asig, "ejercicio 5.3, asignación de buses (oferta y demanda 1)"),
        "u05_bicis_transporte.dat": dat_transporte(R["e510_datos"], "ejercicio 5.10, el plan de 5.5 como transporte"),
        "u05_tiendas.dat": dat_transporte(R["caso_tr_datos"], "caso integrador, envío a las tres tiendas"),
        "u05_transbordo.dat": (
            "/* Unidad 5 · ejercicio 5.6. Generado por verificacion/u05_modelamiento_ii.py */\n"
            f"Plantas = {_set(E56['plantas'])};\nCentros = {_set(E56['centros'])};\n"
            f"Clientes = {_set(E56['clientes'])};\noferta = {_vec(E56['oferta'])};\n"
            f"capCentro = {_vec(E56['cap_centro'])};\ndemanda = {_vec(E56['demanda'])};\n"
            f"cPC = {_mat(E56['c_pc'])};\ncCK = {_mat(E56['c_ck'])};\n"),
        "u05_transporte_multiperiodo.dat": (
            "/* Unidad 5 · ejercicio 5.9. Generado por verificacion/u05_modelamiento_ii.py */\n"
            f"NMeses = {E59['T']};\nPlantas = {_set(E59['plantas'])};\nClientes = {_set(E59['clientes'])};\n"
            f"cap = {_vec(E59['cap'])};\ncProd = {_vec(E59['c_prod'])};\ncInv = {_vec(E59['c_inv'])};\n"
            f"cEnv = {_mat(E59['c_env'])};\ndem = {_mat(E59['dem'])};\n"),
        "u05_polerones.dat": (
            "/* Unidad 5 · caso integrador: las cifras de verificacion/caso_estampa_sur_lp.py (U5).\n"
            "   Generado por verificacion/u05_modelamiento_ii.py */\n"
            f"NSemanas = {U5['semanas']};\ndemanda = {_vec(U5['demanda_polerones'])};\n"
            f"cap = {caso.calcular()['u5']['cap_semana']};\ninvMax = {U5['inv_max']};\ncInv = {U5['costo_inventario']};\n"),
    }
    return D


def dats_al_dia(R, escribir=False):
    malos = []
    for nombre, txt in dats(R).items():
        f = MODELOS / nombre
        if escribir:
            f.write_text(txt, encoding="utf-8")
        elif not f.exists() or f.read_text(encoding="utf-8") != txt:
            malos.append(nombre)
    return malos


# ---------------------------------------------------------------- comparación con OPL

def opl(R):
    """Mismo modelo en OPL: objetivo, variables y precios sombra (solo donde son únicos)."""
    out, ok = {}, True
    p = R["pellets"]
    esp = {"costo": p["z"]}
    for t in range(4):
        for v in "REI":
            esp[f"{v}[{t+1}]"] = p["x"][f"{v}{t}"]
        esp[f"dual_balance[{t+1}]"] = p["dual"][f"balance{t}"]
    esp["dual_final"] = p["dual"]["final"]
    ok &= comparar_opl("pellets", "u05_pellets.mod", "u05_pellets.dat", esp, out)

    def esp_tr(d, s, con_duales):
        e = {"costo": s["z"]}
        for o in d["orig"]:
            for k in d["dest"]:
                e[f"x[{o}][{k}]"] = s["x"][f"x[{o}][{k}]"]
        if con_duales:
            for o in d["orig"]:
                e[f"dual_oferta[{o}]"] = s["dual"][f"oferta[{o}]"]
            for k in d["dest"]:
                e[f"dual_demanda[{k}]"] = s["dual"][f"demanda[{k}]"]
        return e
    asig = {"orig": E53["orig"], "dest": E53["dest"]}
    # un transporte balanceado tiene duales no únicos (u_i + v_j = c_ij admite sumar una constante)
    ok &= comparar_opl("huevos", "u05_transporte.mod", "u05_huevos.dat", esp_tr(HUEVOS, R["huevos"], True), out)
    ok &= comparar_opl("leche", "u05_transporte.mod", "u05_leche.dat", esp_tr(E52, R["e52"], False), out)
    ok &= comparar_opl("buses", "u05_transporte.mod", "u05_buses.dat", esp_tr(asig, R["e53"], False), out)
    ok &= comparar_opl("bicis", "u05_transporte.mod", "u05_bicis_transporte.dat",
                       esp_tr(R["e510_datos"], R["e510"], False), out)
    ok &= comparar_opl("tiendas", "u05_transporte.mod", "u05_tiendas.dat",
                       esp_tr(R["caso_tr_datos"], R["caso_tr"], True), out)
    s = R["e56"]; e = {"costo": s["z"]}
    e.update({k: v for k, v in s["x"].items()})
    for k, v in s["dual"].items():
        nombre, idx = k.split("[")
        e[f"dual_{nombre}[{idx}"] = v
    ok &= comparar_opl("transbordo", "u05_transbordo.mod", "u05_transbordo.dat", e, out)
    ok &= comparar_opl("turnos", "u05_turnos.mod", "u05_turnos.dat", {"personas": R["e57"]["z"]}, out)
    s = R["e59"]; e = {"costo": s["z"]}
    e.update({k: v for k, v in s["x"].items()})
    e.update({f"dual_{k}": v for k, v in s["dual"].items() if k.startswith("demanda")})
    ok &= comparar_opl("transporte multiperíodo", "u05_transporte_multiperiodo.mod",
                       "u05_transporte_multiperiodo.dat", e, out)
    s = R["caso_pol"]; e = {"costo": s["z"]}
    for t in range(4):
        e[f"x[{t+1}]"] = s["x"][f"x{t}"]; e[f"I[{t+1}]"] = s["x"][f"I{t}"]
        e[f"dual_capacidad[{t+1}]"] = s["dual"][f"cap{t}"]; e[f"dual_balance[{t+1}]"] = s["dual"][f"balance{t}"]
    ok &= comparar_opl("polerones", "u05_polerones.mod", "u05_polerones.dat", e, out)
    for k, v in out.items():
        print(f"OPL {k}: {v}")
    return ok


# ---------------------------------------------------------------- figuras

TINTA, SUAVE, ACENTO, LINEA = "#2B2F33", "#5F656B", "#E2622A", "#D6D3CE"


def figuras(R):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "path",
                         "axes.edgecolor": SUAVE, "axes.labelcolor": TINTA, "xtick.color": SUAVE, "ytick.color": SUAVE})
    carpeta = RAMO / "unidades" / "figuras"
    carpeta.mkdir(parents=True, exist_ok=True)

    # 1 · polerones: demanda, producción, inventario y tope semanal
    caso = cargar_caso(); U5 = caso.U5
    s = R["caso_pol"]
    sem = np.arange(1, 5)
    dem = U5["demanda_polerones"]
    x = [s["x"][f"x{t}"] for t in range(4)]
    inv = [s["x"][f"I{t}"] for t in range(4)]
    cap = R["caso_C"]["cap_semana"]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.bar(sem - 0.19, dem, 0.36, color=LINEA, edgecolor=SUAVE, label="demanda")
    ax.bar(sem + 0.19, x, 0.36, color=ACENTO, label="producción")
    ax.axhline(cap, color=TINTA, ls="--", lw=1)
    ax.text(0.55, cap + 8, f"tope semanal {cap}", ha="left", va="bottom", color=TINTA, fontsize=9)
    for t in range(4):
        ax.text(sem[t] - 0.19, dem[t] - 34, f"{dem[t]:.0f}", ha="center", fontsize=8.5, color=TINTA)
        ax.text(sem[t] + 0.19, x[t] - 34, f"{x[t]:.0f}", ha="center", fontsize=8.5, color="white")
        if inv[t] > 0:
            ax.annotate(f"guarda {inv[t]:.0f}", xy=(sem[t] + 0.5, 300), xytext=(sem[t] + 0.5, 140),
                        ha="center", fontsize=8.5, color=TINTA,
                        arrowprops=dict(arrowstyle="->", color=TINTA, lw=0.9))
    ax.set_xticks(sem, [f"semana {t}" for t in sem])
    ax.set_ylabel("polerones")
    ax.set_ylim(0, 690)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.13), ncol=2, fontsize=9)
    fig.tight_layout()
    fig.savefig(carpeta / "u05_polerones.svg", metadata={"Date": None})
    plt.close(fig)

    # 2 · red de transporte del caso: dos orígenes, tres tiendas y el destino ficticio
    d, sol = R["caso_tr_datos"], R["caso_tr"]
    nom = {"Taller": "Taller\n(oferta 1.440)", "BodegaChillan": "Bodega Chillán\n(stock 500)",
           "Concepcion": "Concepción\n(pide 690)", "Chillan": "Chillán\n(pide 410)",
           "LosAngeles": "Los Ángeles\n(pide 340)", "Ficticio": "Ficticio\n(sobra 500)"}
    yo = {"Taller": 2.6, "BodegaChillan": 0.6}
    yd = {"Concepcion": 3.3, "Chillan": 2.1, "LosAngeles": 0.9, "Ficticio": -0.3}
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    for i, o in enumerate(d["orig"]):
        for j, k in enumerate(d["dest"]):
            f = sol["x"][f"x[{o}][{k}]"]
            usada = f > 1e-7
            ax.annotate("", xy=(3.55, yd[k]), xytext=(0.95, yo[o]),
                        arrowprops=dict(arrowstyle="-|>", lw=2.2 if usada else 0.7,
                                        color=ACENTO if usada and k != "Ficticio" else (SUAVE if usada else LINEA),
                                        ls="-" if usada else ":", shrinkA=4, shrinkB=4))
            c = d["costo"][i][j]
            fr = {("Taller", "Concepcion"): 0.55, ("Taller", "LosAngeles"): 0.78, ("Taller", "Ficticio"): 0.82,
                  ("BodegaChillan", "Chillan"): 0.3, ("BodegaChillan", "LosAngeles"): 0.66}.get((o, k), 0.6)
            xm, ym = 0.95 + fr * (3.55 - 0.95), yo[o] + fr * (yd[k] - yo[o])
            if usada:
                ax.text(xm, ym, f"{f:.0f} u · ${c}" if c else f"{f:.0f} u", fontsize=8.5, ha="center",
                        color=TINTA, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    for o, y in yo.items():
        ax.text(0.9, y, nom[o], ha="right", va="center", fontsize=9, color=TINTA,
                bbox=dict(boxstyle="round,pad=0.35", fc="#F2F1EF", ec=SUAVE))
    for k, y in yd.items():
        ax.text(3.6, y, nom[k], ha="left", va="center", fontsize=9, color=TINTA if k != "Ficticio" else SUAVE,
                bbox=dict(boxstyle="round,pad=0.35", fc="#F2F1EF" if k != "Ficticio" else "white", ec=SUAVE,
                          ls="-" if k != "Ficticio" else "--"))
    ax.set_xlim(-0.6, 4.9); ax.set_ylim(-0.8, 3.8); ax.axis("off")
    fig.tight_layout()
    fig.savefig(carpeta / "u05_red_tiendas.svg", metadata={"Date": None})
    plt.close(fig)
    print("figuras: u05_polerones.svg, u05_red_tiendas.svg")


# ---------------------------------------------------------------- revisión contra el texto y cadena

def n(x):
    return fmt(round(x, 6), 0)


def esperados(R):
    """Cadenas que el .md tiene que contener tal cual."""
    e = []
    p, d = R["pellets"], PELLETS
    reg = sum(p["x"][f"R{t}"] for t in range(4)); ext = sum(p["x"][f"E{t}"] for t in range(4))
    inv = sum(p["x"][f"I{t}"] for t in range(4))
    e += [pesos(p["z"]), pesos(d["c_reg"] * reg), pesos(d["c_ext"] * ext), pesos(d["c_inv"] * inv),
          f"({n(reg)} bolsas)", f"({n(ext)} bolsas)", f"({n(inv)} bolsas-mes)"]
    for t, mes in enumerate(d["meses"]):
        e.append(f"| {mes} | {n(p['x'][f'R{t}'])} | {n(p['x'][f'E{t}'])} | {n(p['x'][f'I{t}'])} | "
                 f"\\{pesos(p['dual'][f'balance{t}'])} |")
    e += [f"\\{pesos(p['dual']['final'])} por bolsa", f"le sobran {n(d['bodega'] - p['x']['I0'])} bolsas",
          f"sobran {n(d['cap_ext'] - p['x']['E2'])}", f"abril produce {n(d['cap_reg'] - d['demanda'][0])} bolsas"]
    h = R["huevos"]
    e += [pesos(h["z"]),
          f"Limache manda {n(h['x']['x[Limache][Vina]'])} a Viña y {n(h['x']['x[Limache][Quilpue]'])} a Quilpué; "
          f"Casablanca manda {n(h['x']['x[Casablanca][Vina]'])} a Viña y {n(h['x']['x[Casablanca][Valparaiso]'])} a Valparaíso",
          f"Limache ${n(h['dual']['oferta[Limache]'])}$, Casablanca {n(h['dual']['oferta[Casablanca]'])}, "
          f"Viña {n(h['dual']['demanda[Vina]'])}, Valparaíso {n(h['dual']['demanda[Valparaiso]'])}, "
          f"Quilpué {n(h['dual']['demanda[Quilpue]'])}",
          f"sobran {n(sum(HUEVOS['oferta']) - sum(HUEVOS['demanda']))} docenas"]
    r = R["e51"]
    e += [", ".join(n(x) for x in r["inv"][:-1]) + f" y {n(r['inv'][-1])} frascos", pesos(r["costo"]),
          f"= {r['inv_b'][2]}$", f"${r['inv_b'][3]}$"]
    x = R["e52"]["x"]
    e += [pesos(R["e52"]["z"]),
          f"A → Planta 1 {n(x['x[PredioA][Planta1]'])}, A → Planta 2 {n(x['x[PredioA][Planta2]'])}, "
          f"B → Planta 2 {n(x['x[PredioB][Planta2]'])}, C → Planta 2 {n(x['x[PredioC][Planta2]'])}, "
          f"C → Planta 3 {n(x['x[PredioC][Planta3]'])}"]
    asig = ", ".join(f"{o} → {k}" for o in E53["orig"] for k in E53["dest"] if R["e53"]["x"][f"x[{o}][{k}]"] > 0.5)
    e += [asig, f"**{n(R['e53']['z'])} minutos**", f"{R['e53_totales'][1]} minutos"]
    assert R["e53"]["z"] == R["e53"]["hungaro"][1] and R["e53_totales"][1] > R["e53_totales"][0]
    b = R["e55"]["x"]
    e += [", ".join(n(b[f"x{t}"]) for t in range(3)) + f" y {n(b['x3'])}", pesos(R["e55"]["z"]),
          f"guardar {n(b['Ip0'])} al cierre del mes 1 y {n(b['Ip1'])} al cierre del mes 2",
          f"{n(b['Im2'])} bicicletas pendientes", f"**\\{pesos(R['e55']['dual']['balance3'])}**"]
    t5 = R["e56"]; x = t5["x"]
    e += [pesos(t5["z"]),
          f"Rancagua → San Bernardo {n(x['x[Rancagua][SanBernardo]'])}, Rancagua → Chillán {n(x['x[Rancagua][Chillan]'])}, "
          f"Talca → Chillán {n(x['x[Talca][Chillan]'])}",
          f"Bernardo → Santiago {n(x['y[SanBernardo][Santiago]'])} y → Concepción {n(x['y[SanBernardo][Concepcion]'])}",
          f"Chillán → Concepción {n(x['y[Chillan][Concepcion]'])} y → Temuco {n(x['y[Chillan][Temuco]'])}",
          f"**\\{pesos(-t5['dual']['capCentro[Chillan]'])}**", f"**\\{pesos(t5['dual']['demanda[Temuco]'])}**",
          f"ahorra \\{pesos(-t5['dual']['oferta[Talca]'])}", f"Rancagua deja {n(t5['holgura']['oferta[Rancagua]'])} t"]
    x = R["e57"]["x"]
    e += [f"**{n(R['e57']['z'])} personas**",
          f"{n(x['x0'])} entran a las 0:00, {n(x['x1'])} a las 4:00, {n(x['x2'])} a las 8:00 y {n(x['x4'])} a las 16:00",
          f"$4 + 15 + 11 = {sum(E57['req'][b] for b in (0, 2, 4))}$"]
    assert R["e57_lp"]["z"] == R["e57"]["z"] == sum(E57["req"][b] for b in (0, 2, 4))
    l, z = R["e58"]["x"], R["e58_ent"]["x"]
    e += [pesos(R["e58"]["z"]), pesos(R["e58_ent"]["z"]),
          "contratar " + fmt(l["H1"], 3) + " en el mes 2 y " + fmt(l["H2"], 3),
          "despedir " + fmt(l["F3"], 1) + " en el mes 4",
          ", ".join(n(z[f"W{t}"]) for t in range(3)) + f" y {n(z['W3'])} personas",
          f"\\{pesos(R['e58_ent']['z'] - R['e58']['z'])} más"]
    x = R["e59"]["x"]
    e += [pesos(R["e59"]["z"]),
          "| Talca produce | " + " | ".join(n(x[f"Y[Talca][{t}]"]) for t in (1, 2, 3)) + " |",
          "| Talca guarda al cierre | " + " | ".join(n(x[f"Z[Talca][{t}]"]) for t in (1, 2, 3)) + " |",
          "| Chillán produce | " + " | ".join(n(x[f"Y[Chillan][{t}]"]) for t in (1, 2, 3)) + " |",
          "| Talca → Curicó / Linares | " + " | ".join(
              f"{n(x[f'X[Talca][Curico][{t}]'])} / {n(x[f'X[Talca][Linares][{t}]'])}" for t in (1, 2, 3)) + " |",
          "| Chillán → Linares / Los Ángeles | " + " | ".join(
              f"{n(x[f'X[Chillan][Linares][{t}]'])} / {n(x[f'X[Chillan][LosAngeles][{t}]'])}" for t in (1, 2, 3)) + " |",
          f"**\\{pesos(R['e59_cap_chillan'][0])}**", f"**\\{pesos(R['e59_cap_chillan'][2])}**",
          f"\\{pesos(R['e59']['dual']['demanda[Linares][1]'])} y \\{pesos(R['e59']['dual']['demanda[Linares][3]'])}",
          f"pide {n(sum(r[2] for r in E59['dem']))} unidades", f"caben {n(sum(E59['cap']))}"]
    assert R["e59_cap_chillan"][0] == R["e59_cap_chillan"][1]
    C = R["e510_datos"]["costo"]
    for i in range(4):
        e.append(f"| Mes {i+1} | " + " | ".join(n(c) for c in C[i]) + " |")
    e += [pesos(R["e510"]["z"]), pesos(R["e510_b"]["z"])]
    assert abs(R["e510"]["z"] - R["e55"]["z"]) < TOL and abs(R["e510_b"]["z"] - R["e55_b"]["z"]) < TOL
    xb = R["e55_b"]["x"]
    e.append(f"el mes 1 produce {n(xb['x0'])} y guarda {n(xb['Ip0'])}, el mes 2 guarda {n(xb['Ip1'])}")
    assert all(xb[f"Im{t}"] < TOL for t in range(4))
    # caso
    s = R["caso_pol"]
    e += ["**" + ", ".join(n(s["x"][f"x{t}"]) for t in range(3)) + f" y {n(s['x']['x3'])}**",
          "**" + ", ".join(n(s["x"][f"I{t}"]) for t in range(3)) + f" y {n(s['x']['I3'])}**",
          pesos(s["z"]), f"${n(s['dual']['cap2'])}$", f"es \\{pesos(s['dual']['balance2'])}"]
    caso = cargar_caso(); U5 = caso.U5
    for tienda, ped, c in zip(["Concepción", "Chillán", "Los Ángeles"], U5["pedido_tiendas"], U5["costo_envio"]):
        e.append(f"| {tienda} | {n(ped)} | \\${c} | {pesos(ped * c)} |")
    e.append(f"| **Total** | **{n(sum(U5['pedido_tiendas']))}** | | **{pesos(R['caso_envio_simple'])}** |")
    t = R["caso_tr"]; x = t["x"]
    e += [pesos(t["z"]), pesos(R["caso_envio_simple"] - t["z"]),
          f"la bodega manda {n(x['x[BodegaChillan][Chillan]'])} a Chillán y {n(x['x[BodegaChillan][LosAngeles]'])} a Los\n"
          f"Ángeles; el taller manda {n(x['x[Taller][Concepcion]'])} a Concepción y {n(x['x[Taller][LosAngeles]'])} a Los "
          f"Ángeles, y {n(x['x[Taller][Ficticio]'])} quedan en el taller",
          f"su precio sombra es ${n(t['dual']['oferta[BodegaChillan]'])}$",
          f"cuesta \\{pesos(t['dual']['demanda[Chillan]'])} y no", f"vale \\{pesos(-t['dual']['oferta[BodegaChillan]'])} de flete"]
    return e


def cadena(R):
    C = R["caso_C"]
    s = R["caso_pol"]
    ok = (all(abs(s["x"][f"x{t}"] - C["produccion"][t]) < TOL for t in range(4))
          and all(abs(s["x"][f"I{t}"] - C["inventario"][t]) < TOL for t in range(4))
          and abs(s["z"] - C["costo"]) < TOL
          and abs(R["caso_envio_simple"] - C["costo_envio_total"]) < TOL)
    print("CADENA:", "OK, el plan de polerones y el envío calzan con el caso integrador" if ok else
          f"NO calza: script {C} · unidad {s['x']} {s['z']} {R['caso_envio_simple']}")
    return ok


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    malos = dats_al_dia(R, escribir="--modelos" in sys.argv)
    if malos:
        print("Los .dat no calzan con los datos del script:", malos, "(corre con --modelos)")
        sys.exit(1)
    if "--figuras" in sys.argv:
        figuras(R)
    if not opl(R):
        print("OPL: NO coincide con Python")
        sys.exit(1)
    if not cadena(R):
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (RAMO / "unidades" / "05-modelamiento-multiperiodo-y-transporte.md").read_text(encoding="utf-8")
        md = " ".join(md.replace("{,}", ",").replace("{.}", ".").split())   # los saltos de línea no cuentan
        faltan = [x for x in esperados(R) if " ".join(x.split()) not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
