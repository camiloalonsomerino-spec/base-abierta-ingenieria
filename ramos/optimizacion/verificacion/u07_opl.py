"""Unidad 7 · Implementación en OPL. Recalcula todas las cifras; con --revisar las busca en el .md.

Cada modelo de la unidad está en ramos/optimizacion/modelos/u07_*.mod (y .dat). Este script:

1. declara los mismos datos en Python y resuelve cada modelo con scipy (HiGHS);
2. si hay CPLEX (oplrun), corre el .mod con herramientas/opl.py y exige que objetivo, variables,
   precios sombra, holguras y costos reducidos coincidan con los de Python;
3. vuelve a provocar los errores de OPL que cita la unidad y comprueba que el mensaje sea el citado;
4. compara la pieza del caso integrador (unidad 4) con el script del caso;
5. con --revisar, busca cada cifra (y el código del ejemplo y del caso) en el .md.

    python u07_opl.py            # imprime los resultados
    python u07_opl.py --revisar  # además los busca en el .md
"""
from pathlib import Path
import importlib.util, re, shutil, sys, tempfile

import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402

TOL = 1e-6


# ---------------------------------------------------------------- formato chileno
def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x, dec=0):
    return "$" + fmt(x, dec)


def num(x):
    """Entero si lo es; si no, con los decimales justos (hasta 4)."""
    if abs(x - round(x)) < 1e-9:
        return fmt(round(x), 0)
    for d in (1, 2, 3, 4):
        if abs(x - round(x, d)) < 1e-9:
            return fmt(x, d)
    return fmt(x, 2)


# ---------------------------------------------------------------- un LP genérico
def resolver(sentido, c, filas, cotas=None):
    """filas: lista de (clave, coeficientes, tipo, lado_derecho). Devuelve valores con la convención
    de OPL: dual = ∂objetivo/∂lado derecho; costo reducido = ∂objetivo/∂x_j; holgura = |ld − li|."""
    sg = -1 if sentido == "max" else 1
    A_ub, b_ub, A_eq, b_eq, idx = [], [], [], [], []
    for clave, a, tipo, b in filas:
        if tipo == "<=":
            idx.append(("ub", len(A_ub), 1)); A_ub.append(a); b_ub.append(b)
        elif tipo == ">=":
            idx.append(("ub", len(A_ub), -1)); A_ub.append([-v for v in a]); b_ub.append(-b)
        else:
            idx.append(("eq", len(A_eq), 1)); A_eq.append(a); b_eq.append(b)
    r = linprog([sg * v for v in c], A_ub=A_ub or None, b_ub=b_ub or None, A_eq=A_eq or None,
                b_eq=b_eq or None, bounds=cotas or [(0, None)] * len(c), method="highs")
    assert r.status == 0, r.message
    dual, holg = {}, {}
    for (clave, a, tipo, b), (cual, k, signo) in zip(filas, idx):
        m = (r.ineqlin.marginals if cual == "ub" else r.eqlin.marginals)[k]
        dual[clave] = sg * signo * m
        holg[clave] = abs(b - float(np.dot(a, r.x)))
    return {"z": sg * r.fun, "x": list(r.x), "dual": dual, "holgura": holg,
            "rc": [sg * v for v in r.lower.marginals]}


# ---------------------------------------------------------------- datos (originales)
PAN = {"panes": ["marraqueta", "hallulla", "amasado"], "recursos": ["horno", "amasadora", "harina"],
       "margen": [6000, 4200, 6500], "uso": [[16, 12, 20], [8, 10, 18], [5, 4.5, 6]],
       "disp": [2480, 1730, 885], "tope": [80, 125, 60]}
CERV = {"margen": [23000, 29000], "mac": [3, 5], "fer": [2, 2], "cap": [150, 80]}
ALIM = {"ing": ["pollo", "arroz", "maiz", "aceite"], "nut": ["proteina", "grasa"],
        "costo": [2380, 870, 640, 1950], "aporte": [[58, 8, 10, 0], [9, 1, 5, 100]],
        "minimo": [24, 10], "maximo": [0, 16], "K": 250}
VIV = {"plantas": ["lavanda", "romero", "suculenta"], "recursos": ["trasplante", "sustrato"],
       "margen": [1070, 845, 1360], "uso": [[4, 3, 6], [3, 2, 1]], "cap": [2510, 1570],
       "demanda": [310, 410, 240]}
CARP = {"muebles": ["mesa", "silla", "estante", "velador"], "procesos": ["corte", "armado", "barniz"],
        "margen": [32800, 21700, 56100, 27600], "uso": [[3, 2, 4, 2], [2, 1, 5, 3], [2, 1, 3, 2]],
        "cap": [452, 306, 281], "tope_sillas": 126, "oferta_armado": (10, 4000)}
MERM = {"sabores": ["frutilla", "damasco", "mora", "naranja"], "recursos": ["coccion", "envasado", "azucar"],
        "margen": [38000, 30000, 45500, 33500], "uso": [[50, 40, 60, 45], [20, 20, 25, 15], [12, 10, 14, 11]],
        "disp": [2350, 925, 560]}
EMP = {"T": 4, "demanda": [370, 460, 515, 290], "inv0": 45, "cap_regular": 410, "cap_extra": 160,
       "c_regular": 1750, "c_extra": 2480, "c_inv": 135}
LAV = {"lav": ["A", "B", "C"], "cap": [920, 680, 470], "fijo": [61000, 43500, 24800], "cvar": [38, 45, 61],
       "D": 1340}
MOCH = {"modelos": ["urbana", "trekking", "escolar"], "procesos": ["costura", "corte"],
        "margen": [58300, 68000, 31700], "horas": [[3, 4, 2], [2, 2, 1]], "disp": [342, 196], "tope": 52}
TRANS = {"bodegas": ["Talca", "Linares", "Parral"], "locales": ["L1", "L2", "L3", "L4"],
         "oferta": [535, 615, 385], "pedido": [305, 265, 345, 218],
         "costo": [[146, 212, 264, 188], [231, 127, 183, 249], [297, 238, 114, 176]],
         "ampliacion": (40, 10)}   # 7.10: 40 cajas más en Parral a $10 por caja


def caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_lp.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- modelos
def mezcla(margen=None, cap=None):
    m = caso()
    prendas = ["poleras", "polerones", "doble", "bolsas", "gorros"]
    rec = ["estampado", "planchado", "tinta"]
    margen = margen or m.MARGEN
    cap = cap or [m.CAP["estampado_s"], m.CAP["planchado_s"], m.CAP["tinta_g"]]
    uso = [m.SEG_EST, m.SEG_PLA, m.TINTA_G]
    filas = [(f"r:{r}", uso[k], "<=", cap[k]) for k, r in enumerate(rec)]
    filas += [(f"d:{p}", [int(j == i) for j in range(5)], "<=", m.DEMANDA_MAX[i]) for i, p in enumerate(prendas)]
    R = resolver("max", margen, filas)
    v = {"margen": R["z"]}
    for i, p in enumerate(prendas):
        v[f"x[{p}]"] = R["x"][i]
        v[f"costo_reducido[{p}]"] = R["rc"][i]
        v[f"dual_demanda[{p}]"] = R["dual"][f"d:{p}"]
    for k, r in enumerate(rec):
        v[f"usado[{r}]"] = float(np.dot(uso[k], R["x"]))
        v[f"holgura[{r}]"] = R["holgura"][f"r:{r}"]
        v[f"dual[{r}]"] = R["dual"][f"r:{r}"]
    return v


def panaderia():
    d = PAN
    n = len(d["panes"])
    filas = [(f"r:{r}", d["uso"][k], "<=", d["disp"][k]) for k, r in enumerate(d["recursos"])]
    filas += [(f"v:{p}", [int(j == i) for j in range(n)], "<=", d["tope"][i]) for i, p in enumerate(d["panes"])]
    R = resolver("max", d["margen"], filas)
    v = {"margen": R["z"]}
    for i, p in enumerate(d["panes"]):
        v[f"x[{p}]"] = R["x"][i]; v[f"costo_reducido[{p}]"] = R["rc"][i]; v[f"dual_venta[{p}]"] = R["dual"][f"v:{p}"]
    for k, r in enumerate(d["recursos"]):
        v[f"holgura[{r}]"] = R["holgura"][f"r:{r}"]; v[f"dual[{r}]"] = R["dual"][f"r:{r}"]
    return v


def cerveceria():
    d = CERV
    R = resolver("max", d["margen"], [("mac", d["mac"], "<=", d["cap"][0]), ("fer", d["fer"], "<=", d["cap"][1])])
    return {"margen": R["z"], "L": R["x"][0], "S": R["x"][1], "maceracion_usada": float(np.dot(d["mac"], R["x"])),
            "dual_maceracion": R["dual"]["mac"], "dual_fermentacion": R["dual"]["fer"]}


def alimento():
    d = ALIM
    n = len(d["ing"])
    filas = [("total", [1] * n, "==", d["K"])]
    filas += [(f"piso:{nu}", d["aporte"][k], ">=", d["minimo"][k] * d["K"]) for k, nu in enumerate(d["nut"])]
    filas += [(f"techo:{nu}", d["aporte"][k], "<=", d["maximo"][k] * d["K"]) for k, nu in enumerate(d["nut"]) if d["maximo"][k] > 0]
    R = resolver("min", d["costo"], filas)
    v = {"costo": R["z"], "dual_total": R["dual"]["total"], "holgura_techo[grasa]": R["holgura"]["techo:grasa"]}
    for i, ing in enumerate(d["ing"]):
        v[f"kg[{ing}]"] = R["x"][i]; v[f"costo_reducido[{ing}]"] = R["rc"][i]
    for nu in d["nut"]:
        v[f"dual_piso[{nu}]"] = R["dual"][f"piso:{nu}"]
    return v


def vivero():
    d = VIV
    n = len(d["plantas"])
    filas = [(f"r:{r}", d["uso"][k], "<=", d["cap"][k]) for k, r in enumerate(d["recursos"])]
    filas += [(f"d:{p}", [int(j == i) for j in range(n)], "<=", d["demanda"][i]) for i, p in enumerate(d["plantas"])]
    R = resolver("max", d["margen"], filas)
    v = {"margen": R["z"]}
    for i, p in enumerate(d["plantas"]):
        v[f"x[{p}]"] = R["x"][i]; v[f"dual_demanda[{p}]"] = R["dual"][f"d:{p}"]
    for r in d["recursos"]:
        v[f"dual[{r}]"] = R["dual"][f"r:{r}"]
    return v


def carpinteria(cap=None):
    d = CARP
    cap = cap or d["cap"]
    filas = [(f"r:{p}", d["uso"][k], "<=", cap[k]) for k, p in enumerate(d["procesos"])]
    filas += [("sillas", [0, 1, 0, 0], "<=", d["tope_sillas"])]
    R = resolver("max", d["margen"], filas)
    v = {"margen": R["z"], "dual_sillas": R["dual"]["sillas"]}
    for i, m in enumerate(d["muebles"]):
        v[f"x[{m}]"] = R["x"][i]; v[f"costo_reducido[{m}]"] = R["rc"][i]
    for p in d["procesos"]:
        v[f"holgura[{p}]"] = R["holgura"][f"r:{p}"]; v[f"dual[{p}]"] = R["dual"][f"r:{p}"]
    return v


def mermeladas():
    d = MERM
    filas = [(f"r:{r}", d["uso"][k], "<=", d["disp"][k]) for k, r in enumerate(d["recursos"])]
    R = resolver("max", d["margen"], filas)
    v = {"margen": R["z"]}
    for i, s in enumerate(d["sabores"]):
        v[f"lotes[{s}]"] = R["x"][i]; v[f"costo_reducido[{s}]"] = R["rc"][i]
    for k, r in enumerate(d["recursos"]):
        v[f"usado[{r}]"] = float(np.dot(d["uso"][k], R["x"])); v[f"dual[{r}]"] = R["dual"][f"r:{r}"]
    return v


def empanadas():
    d = EMP
    T = d["T"]
    c = [d["c_regular"]] * T + [d["c_extra"]] * T + [d["c_inv"]] * T
    filas = []
    for t in range(T):
        a = [0] * (3 * T); a[t] = 1; a[T + t] = 1; a[2 * T + t] = -1
        if t > 0:
            a[2 * T + t - 1] = 1
        filas.append((f"b{t + 1}", a, "==", d["demanda"][t] - (d["inv0"] if t == 0 else 0)))
    cotas = [(0, d["cap_regular"])] * T + [(0, d["cap_extra"])] * T + [(0, None)] * T
    R = resolver("min", c, filas, cotas)
    v = {"costo": R["z"]}
    for t in range(T):
        v[f"r[{t + 1}]"] = R["x"][t]; v[f"e[{t + 1}]"] = R["x"][T + t]; v[f"I[{t + 1}]"] = R["x"][2 * T + t]
        v[f"dual_balance[{t + 1}]"] = R["dual"][f"b{t + 1}"]
    return v


def lavanderia():
    d = LAV
    n = len(d["lav"])
    c = d["cvar"] + d["fijo"]
    A = [[1] * n + [0] * n] + [[int(j == i) for j in range(n)] + [-d["cap"][i] * int(j == i) for j in range(n)] for i in range(n)]
    m = milp(c, constraints=LinearConstraint(A, [d["D"]] + [-np.inf] * n, [np.inf] + [0] * n),
             integrality=[0] * n + [1] * n, bounds=Bounds([0] * (2 * n), [np.inf] * n + [1] * n))
    assert m.status == 0
    v = {"costo": m.fun}
    for i, l in enumerate(d["lav"]):
        v[f"y[{l}]"] = round(m.x[n + i]); v[f"kg[{l}]"] = m.x[i]
    # relajación lineal: y entre 0 y 1
    rel = linprog(c, A_ub=[[-1] * n + [0] * n] + A[1:], b_ub=[-d["D"]] + [0] * n,
                  bounds=[(0, None)] * n + [(0, 1)] * n, method="highs")
    assert rel.status == 0
    v["rel_costo"] = rel.fun
    for i, l in enumerate(d["lav"]):
        v[f"rel_y[{l}]"] = rel.x[n + i]; v[f"rel_kg[{l}]"] = rel.x[i]
    v["costo_por_kg"] = [d["cvar"][i] + d["fijo"][i] / d["cap"][i] for i in range(n)]
    # comprobación por fuerza bruta: las 7 combinaciones de máquinas encendidas
    mejor = None
    for k in range(1, 2 ** n):
        on = [i for i in range(n) if k >> i & 1]
        if sum(d["cap"][i] for i in on) < d["D"]:
            continue
        resto, costo = d["D"], sum(d["fijo"][i] for i in on)
        for i in sorted(on, key=lambda i: d["cvar"][i]):
            q = min(resto, d["cap"][i]); costo += q * d["cvar"][i]; resto -= q
        mejor = costo if mejor is None else min(mejor, costo)
    assert abs(mejor - m.fun) < TOL
    return v


def mochilas():
    d = MOCH
    filas = [(f"h:{p}", d["horas"][k], "<=", d["disp"][k]) for k, p in enumerate(d["procesos"])]
    filas += [("trek", [0, 1, 0], "<=", d["tope"])]
    R = resolver("max", d["margen"], filas)
    v = {"margen": R["z"], "holgura_trekking": R["holgura"]["trek"]}
    for i, m in enumerate(d["modelos"]):
        v[f"x[{m}]"] = R["x"][i]; v[f"costo_reducido[{m}]"] = R["rc"][i]
    for k, p in enumerate(d["procesos"]):
        v[f"usado[{p}]"] = float(np.dot(d["horas"][k], R["x"])); v[f"dual[{p}]"] = R["dual"][f"h:{p}"]
    return v


def transporte(oferta=None):
    d = TRANS
    oferta = oferta or d["oferta"]
    nb, nl = len(d["bodegas"]), len(d["locales"])
    c = [d["costo"][i][j] for i in range(nb) for j in range(nl)]
    filas = [(f"o:{b}", [int(k // nl == i) for k in range(nb * nl)], "<=", oferta[i]) for i, b in enumerate(d["bodegas"])]
    filas += [(f"p:{l}", [int(k % nl == j) for k in range(nb * nl)], ">=", d["pedido"][j]) for j, l in enumerate(d["locales"])]
    R = resolver("min", c, filas)
    v = {"costo": R["z"]}
    for i, b in enumerate(d["bodegas"]):
        v[f"holgura[{b}]"] = R["holgura"][f"o:{b}"]; v[f"dual_oferta[{b}]"] = R["dual"][f"o:{b}"]
        for j, l in enumerate(d["locales"]):
            if R["x"][i * nl + j] > TOL:
                v[f"x[{b}][{l}]"] = R["x"][i * nl + j]
            v[f"cr[{b}][{l}]"] = R["rc"][i * nl + j]
    for l in d["locales"]:
        v[f"dual_pedido[{l}]"] = R["dual"][f"p:{l}"]
    return v


MODELOS_U7 = {
    "panaderia": (panaderia, "u07_panaderia.mod", "u07_panaderia.dat"),
    "mezcla": (mezcla, "u07_mezcla.mod", "u07_mezcla.dat"),
    "e01": (cerveceria, "u07_e01_cerveceria.mod", None),
    "e02": (alimento, "u07_e02_alimento.mod", "u07_e02_alimento.dat"),
    "e03": (vivero, "u07_e03_vivero.mod", "u07_e03_vivero.dat"),
    "e04": (carpinteria, "u07_e04_carpinteria.mod", "u07_e04_carpinteria.dat"),
    "e05": (mermeladas, "u07_e05_mermeladas.mod", "u07_e05_mermeladas.dat"),
    "e06": (empanadas, "u07_e06_empanadas.mod", "u07_e06_empanadas.dat"),
    "e07": (lavanderia, "u07_e07_lavanderia.mod", "u07_e07_lavanderia.dat"),
    "e08": (mochilas, "u07_e08_mochilas.mod", "u07_e08_mochilas.dat"),
    "e09a": (lambda: mezcla(margen=caso().MARGEN[:4] + [0]), "u07_mezcla.mod", "u07_e09_error_a.dat"),
    "e09b": (lambda: mezcla(cap=[40, 18, caso().CAP["tinta_g"]]), "u07_mezcla.mod", "u07_e09_error_b.dat"),
    "e10": (transporte, "u07_e10_transporte.mod", "u07_e10_transporte.dat"),
}


# ---------------------------------------------------------------- errores que cita la unidad
VIVERO_ERR = [
    ("float cap[Recursos]            = ...;", "dvar float cap[Recursos]       = ...;", "syntax error, unexpected ..."),
    ("dvar float+ x[Plantas];", "dvar float+ x[Plantas]", "syntax error, unexpected maximize, expecting ';'"),
    ("margen[p] * x[p];", "margen[p] * x[i];", 'Name "i" does not exist.'),
    ("uso[r][p] * x[p] <= cap[r]", "uso[p][r] * x[p] <= cap[r]", 'Index out of bound for array "uso": lavanda.'),
    ("x[p] <= demanda[p];", "x[p] = demanda[p];", "syntax error, unexpected ="),
]
MEZCLA_ERR = [
    ("mod", "dvar float+ x[Prendas];", "dvar float+ x[Prendas]", "syntax error, unexpected dexpr, expecting ';'"),
    ("dat", "demanda = [1450 520 380 860 690];", "", 'External data element "demanda" was not defined.'),
    ("mod", "x[i] <= demanda[i];", 'x[i] <= demanda[i];\n    Minimo: x["poleron"] >= 100;', 'Index out of bound for array "x": poleron.'),
    ("mod", "dvar float+ x[Prendas];", "dvar int+ x[Prendas];", "CPLEX Error 1017: Not available for mixed-integer problems."),
    ("mod", "x[i] <= demanda[i];", "x[i] <= demanda[i];\n    Piso: sum(i in Prendas) x[i] >= 4000;", "Row 'Piso' infeasible, all entries at implied bounds."),
]
TRANS_ERR = [("dvar float+ x", "dvar float x", "make problem unbounded")]


def provocar_errores():
    """Corre cada variante con error; devuelve la lista de mensajes esperados (vacía si no hay CPLEX)."""
    if correr(MODELOS / "u07_e01_cerveceria.mod") is None:
        return None
    vistos = []
    tmp = Path(tempfile.mkdtemp(prefix="u07_err_"))
    try:
        base = (MODELOS / "u07_e03_vivero.mod").read_text(encoding="utf-8")
        for k, (a, b, msg) in enumerate(VIVERO_ERR):
            assert a in base
            f = tmp / f"vivero_{k}.mod"; f.write_text(base.replace(a, b), encoding="utf-8")
            r = correr(f, MODELOS / "u07_e03_vivero.dat")
            assert msg in " ".join(r["salida"].split()), (msg, r["salida"][-400:])
            vistos.append(msg)
        # sin el «+» el vivero da lo mismo: el error no se ve en este modelo
        f = tmp / "vivero_sin_mas.mod"; f.write_text(base.replace("dvar float+ x[Plantas];", "dvar float x[Plantas];"), encoding="utf-8")
        r = correr(f, MODELOS / "u07_e03_vivero.dat")
        assert abs(r["objetivo"] - vivero()["margen"]) < TOL
        mod = (MODELOS / "u07_mezcla.mod").read_text(encoding="utf-8")
        dat = (MODELOS / "u07_mezcla.dat").read_text(encoding="utf-8")
        for k, (donde, a, b, msg) in enumerate(MEZCLA_ERR):
            fm, fd = tmp / f"mezcla_{k}.mod", tmp / f"mezcla_{k}.dat"
            assert a in (mod if donde == "mod" else dat)
            fm.write_text(mod.replace(a, b) if donde == "mod" else mod, encoding="utf-8")
            fd.write_text(dat.replace(a, b) if donde == "dat" else dat, encoding="utf-8")
            r = correr(fm, fd)
            assert msg in " ".join(r["salida"].split()), (msg, r["salida"][-400:])
            vistos.append(msg)
        mod = (MODELOS / "u07_e10_transporte.mod").read_text(encoding="utf-8")
        for a, b, msg in TRANS_ERR:
            f = tmp / "trans.mod"; f.write_text(mod.replace(a, b), encoding="utf-8")
            r = correr(f, MODELOS / "u07_e10_transporte.dat")
            assert msg in r["salida"] and "no solution" in r["salida"]
            vistos.append(msg)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return vistos


# ---------------------------------------------------------------- todo junto
def resultados():
    R = {k: f() for k, (f, _, _) in MODELOS_U7.items()}
    # 7.4 · ¿conviene comprar 10 h de armado a $4.000? Se re-resuelve con 10 h más
    h, precio = CARP["oferta_armado"]
    nuevo = carpinteria(cap=[CARP["cap"][0], CARP["cap"][1] + h, CARP["cap"][2]])
    R["e04"]["ganancia_10h"] = nuevo["margen"] - R["e04"]["margen"]
    R["e04"]["neto_10h"] = R["e04"]["ganancia_10h"] - h * precio
    assert abs(R["e04"]["ganancia_10h"] - h * R["e04"]["dual[armado]"]) < TOL   # dentro del rango
    # 7.2 · un punto más de proteína mínima sube el lado derecho en K
    R["e02"]["punto_proteina"] = R["e02"]["dual_piso[proteina]"] * ALIM["K"]
    # 7.6 · el dual de la semana 1 es el turno extra de la semana 3 menos dos semanas de inventario
    assert abs(R["e06"]["dual_balance[1]"] - (EMP["c_extra"] - 2 * EMP["c_inv"])) < TOL
    # 7.10 · ampliar Parral en 40 cajas a $10 cada una
    q, precio = TRANS["ampliacion"]
    amp = transporte(oferta=[TRANS["oferta"][0], TRANS["oferta"][1], TRANS["oferta"][2] + q])
    R["e10"]["ahorro_amp"] = R["e10"]["costo"] - amp["costo"]
    R["e10"]["neto_amp"] = R["e10"]["ahorro_amp"] - q * precio
    assert abs(R["e10"]["ahorro_amp"] + q * R["e10"]["dual_oferta[Parral]"]) < TOL
    # 7.9 · el costo reducido de los gorros con margen 0 es justo lo que «cobran» sus recursos
    m = caso()
    R["e09a"]["cobro_gorros"] = 1.5 * m.SEG_PLA[4] + 112.5 * m.TINTA_G[4]
    assert abs(R["e09a"]["costo_reducido[gorros]"] + R["e09a"]["cobro_gorros"]) < TOL
    return R


SALIDAS_EN_MD = ["panaderia", "mezcla", "e04"]   # su salida se muestra completa en el .md
SALIDAS = {}


def comparar_con_opl(R):
    """Exige que cada valor que imprime OPL coincida con el de Python."""
    corridos = 0
    for k, (_, mod, dat) in MODELOS_U7.items():
        r = correr(MODELOS / mod, MODELOS / dat if dat else None)
        if r is None:
            print("OPL: oplrun no está instalado; se comparan solo las cifras de Python")
            return None
        assert r["codigo"] == 0 and r["objetivo"] is not None, (k, r["salida"][-300:])
        z_py = R[k].get("margen", R[k].get("costo"))
        assert abs(r["objetivo"] - z_py) < 1e-4, (k, r["objetivo"], z_py)
        comunes = 0
        for clave, val in r["valores"].items():
            if clave in R[k] and isinstance(val, float):
                assert abs(val - R[k][clave]) < 1e-4 * max(1, abs(val)), (k, clave, val, R[k][clave])
                comunes += 1
        assert comunes >= 3, (k, "muy pocas cifras comparadas")
        if k in SALIDAS_EN_MD:
            SALIDAS[k] = [l.strip() for l in r["salida"].splitlines() if re.match(r"^[\w\[\]]+ = \S+$", l.strip())]
        corridos += 1
    print(f"OPL: {corridos} modelos corridos con oplrun; objetivo, variables, duales y holguras coinciden con Python")
    return True


def cadena(R):
    C = caso().calcular()["u4"]
    v = R["mezcla"]
    prendas = ["poleras", "polerones", "doble", "bolsas", "gorros"]
    ok = abs(v["margen"] - C["z"]) < TOL
    ok &= all(abs(v[f"x[{p}]"] - C["x"][i]) < TOL for i, p in enumerate(prendas))
    ok &= all(abs(v[f"holgura[{r}]"] - C["holguras"][k]) < TOL for k, r in enumerate(["estampado", "planchado", "tinta"]))
    ok &= all(abs(v[f"dual[{r}]"] - C["precios_sombra"][k]) < TOL for k, r in enumerate(["estampado", "planchado", "tinta"]))
    ok &= all(abs(v[f"dual_demanda[{p}]"] - C["costo_reducido_cotas"][i]) < TOL for i, p in enumerate(prendas))
    print("CADENA:", "OK, la mezcla de OPL es la de la unidad 4 (x, margen, holguras y precios sombra)" if ok else "NO calza")
    return ok


def esperados(R):
    P, M, E = R["panaderia"], R["mezcla"], R
    s = []
    # ejemplo
    s += [pesos(P["margen"]), "80 bandejas de marraqueta", "100 de hallulla", "350", "400", "500",
          "90 minutos", "35 kg"]
    # caso
    s += [pesos(M["margen"]), num(M["x[poleras]"]), num(M["x[bolsas]"]), num(M["holgura[estampado]"]),
          num(M["dual[planchado]"]), num(M["dual[tinta]"]), num(M["dual_demanda[polerones]"]),
          num(M["dual_demanda[gorros]"]), num(M["costo_reducido[doble]"]).replace("-", "−"),
          pesos(M["dual[planchado]"] * 3600), num(M["usado[estampado]"])]
    # 7.1
    e = E["e01"]; s += [pesos(e["margen"]), f"L = {num(e['L'])}", f"S = {num(e['S'])}", pesos(e["dual_maceracion"]), pesos(e["dual_fermentacion"])]
    # 7.2
    e = E["e02"]; s += [pesos(e["costo"]), num(e["kg[pollo]"]) + " kg", num(e["kg[maiz]"]) + " kg", num(e["kg[aceite]"]) + " kg",
                        num(e["costo_reducido[arroz]"]), fmt(e["dual_piso[proteina]"], 2), fmt(e["dual_piso[grasa]"], 2),
                        fmt(e["dual_total"], 2), pesos(e["punto_proteina"]), num(e["holgura_techo[grasa]"])]
    # 7.3
    e = E["e03"]; s += [pesos(e["margen"]), num(e["x[lavanda]"]), num(e["x[romero]"]), num(e["x[suculenta]"]),
                        num(e["dual[trasplante]"]), num(e["dual[sustrato]"]), num(e["dual_demanda[romero]"])]
    # 7.4
    e = E["e04"]; s += [pesos(e["margen"]), pesos(e["dual[corte]"]), pesos(e["dual[armado]"]), pesos(-e["costo_reducido[velador]"]),
                        pesos(e["dual_sillas"]), num(e["holgura[barniz]"]) + " L", pesos(e["ganancia_10h"]), pesos(e["neto_10h"])]
    # 7.5
    e = E["e05"]; s += [pesos(e["margen"]), num(e["lotes[frutilla]"]) + " de frutilla", num(e["lotes[mora]"]) + " de mora",
                        num(e["lotes[naranja]"]) + " de naranja", pesos(e["dual[coccion]"]), pesos(e["dual[envasado]"]),
                        pesos(e["dual[azucar]"]), pesos(-e["costo_reducido[damasco]"])]
    # 7.6
    e = E["e06"]; s += [pesos(e["costo"]), num(e["e[3]"]), num(e["I[1]"]), num(e["I[2]"]), pesos(e["dual_balance[1]"]),
                        pesos(e["dual_balance[2]"]), pesos(e["dual_balance[3]"]), pesos(e["dual_balance[4]"])]
    # 7.7
    e = E["e07"]; s += [pesos(e["costo"]), num(e["kg[A]"]), num(e["kg[C]"]), pesos(e["rel_costo"]), fmt(e["rel_y[B]"], 2),
                        pesos(e["costo_por_kg"][0], 1), pesos(e["costo_por_kg"][1], 1), pesos(e["costo_por_kg"][2], 1),
                        num(e["rel_kg[B]"])]
    # 7.8
    e = E["e08"]; s += [pesos(e["margen"]), num(e["x[urbana]"]), num(e["x[trekking]"]), pesos(e["dual[costura]"]),
                        pesos(e["dual[corte]"]), pesos(-e["costo_reducido[escolar]"]), num(e["holgura_trekking"])]
    # 7.9
    a, b = E["e09a"], E["e09b"]
    s += [num(a["margen"]), num(a["x[poleras]"]), num(a["x[bolsas]"]), num(-a["costo_reducido[gorros]"]),
          num(b["margen"]), num(b["x[polerones]"]), num(b["dual[planchado]"])]
    # 7.10
    e = E["e10"]; s += [pesos(e["costo"]), pesos(-e["dual_oferta[Parral]"]), pesos(e["dual_pedido[L4]"]), pesos(e["cr[Linares][L3]"]),
                        num(e["holgura[Talca]"]), num(e["holgura[Linares]"]), pesos(e["ahorro_amp"]), pesos(e["neto_amp"])]
    return s


def codigo_en_md(md):
    """El código del ejemplo y del caso tiene que estar en el .md tal cual, línea por línea."""
    faltan = []
    for f in ["u07_panaderia.mod", "u07_panaderia.dat", "u07_mezcla.mod", "u07_mezcla.dat"]:
        for linea in (MODELOS / f).read_text(encoding="utf-8").splitlines():
            if linea.strip() and linea.rstrip() not in md:
                faltan.append(f"{f}: {linea.strip()}")
    return faltan


if __name__ == "__main__":
    R = resultados()
    for k, v in R.items():
        print(f"== {k}")
        for kk, vv in v.items():
            print(f"   {kk} = {vv if not isinstance(vv, float) else round(vv, 6)}")
    if not cadena(R):
        sys.exit(1)
    hay_opl = comparar_con_opl(R)
    mensajes = provocar_errores() if hay_opl else None
    if mensajes is not None:
        print(f"ERRORES: {len(mensajes)} mensajes de OPL provocados; todos dicen lo que cita la unidad")
    if "--revisar" in sys.argv:
        md = (RAMO / "unidades" / "07-implementacion-en-opl.md").read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        md_plano = " ".join(md_n.split())
        faltan = [x for x in esperados(R) if x not in md_n]
        faltan += [f"mensaje: {m}" for m in (mensajes or []) if " ".join(m.split()) not in md_plano]
        faltan += codigo_en_md(md)
        lineas_md = set(l.strip() for l in md.splitlines())
        faltan += [f"salida OPL {k}: {l}" for k, ls in SALIDAS.items() for l in ls if l not in lineas_md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
