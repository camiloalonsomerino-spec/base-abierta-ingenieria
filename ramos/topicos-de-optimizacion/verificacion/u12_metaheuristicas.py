"""Unidad 12 · Metaheurísticas: búsqueda tabú, recocido simulado y algoritmos genéticos.

Recalcula todas las cifras de la unidad desde los datos: las corridas a mano (con sus números
aleatorios, que salen de una semilla fija y se escriben en el texto), las corridas sobre el caso
integrador (semilla 2026) y los experimentos de calibración con diez semillas. Compara cada resultado
con el óptimo exacto (enumeración, `scipy.optimize.milp` y, si hay CPLEX, el modelo OPL de
`modelos/`). Genera las tablas en Markdown, dibuja las figuras SVG e importa el caso integrador.

    python u12_metaheuristicas.py            # imprime los resultados y redibuja las figuras
    python u12_metaheuristicas.py --tablas   # además imprime las tablas en Markdown
    python u12_metaheuristicas.py --revisar  # además busca cada cifra y cada tabla en el .md
"""
from itertools import product, permutations
from pathlib import Path
import importlib.util, math, random, statistics, sys

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
FIGURAS = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "12-metaheuristicas.md"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402


def cargar(nombre):
    spec = importlib.util.spec_from_file_location(nombre, AQUI / f"{nombre}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


U11 = cargar("u11_heuristicas")       # formato, rutas, 2-opt y los datos de la panadería y del técnico
fmt, pct, signo, largo, flecha = U11.fmt, U11.pct, U11.signo, U11.largo, U11.flecha


def num(x, dec=2):
    return fmt(x, dec)


def aleatorios(semilla, n):
    """Números aleatorios para las corridas a mano: dos decimales (truncados), de una semilla fija."""
    rnd = random.Random(semilla)
    return [math.floor(rnd.random() * 100) / 100 for _ in range(n)]   # entre 0,00 y 0,99


# ---------------------------------------------------------------- datos (originales)

# Ejemplo resuelto · la camioneta de la feria: qué cajas llevar (ganancia en miles de pesos, volumen en jabas)
EJ = {"nombres": ["paltas", "tomates", "ajos", "zapallos", "frutillas"],
      "g": [25, 29, 13, 11, 26], "v": [7, 8, 4, 5, 3], "cap": 14, "inicio": (0, 1, 0, 0, 1),
      "tenencia": 2, "tmax_tabu": 6, "T0": 20.0, "alfa": 0.8, "tmax_rs": 4, "semilla_rs": 28,
      "pen": 10, "pm": 0.2, "semilla_ag": 8, "semilla_pob": 1}

# 12.1 · probabilidades de aceptar
E1 = {"deltas": [2, 5, 10], "temps": [20, 5, 1], "u": 0.35}

# 12.2 · ¿qué movimiento elige la tabú? (km de cada vecino; True = tabú)
E2 = {"actual": 96, "mejor": 91, "mejor_b": 89,
      "vecinos": [("(2, 6)", 99, False), ("(3, 5)", 90, True), ("(1, 4)", 93, True), ("(2, 4)", 97, False), ("(5, 6)", 101, False)]}

# 12.3 · cruce y mutación binarios (mochila con penalización)
E3 = {"g": [14, 9, 21, 7, 17, 11], "v": [4, 3, 6, 2, 5, 4], "cap": 13, "pen": 10,
      "A": (1, 1, 0, 0, 1, 0), "B": (0, 1, 1, 1, 0, 1), "corte": 3, "muta": 4}

# 12.4 · cruce OX en la ruta de la panadería (U11)
E4 = {"A": ["B", "F", "C", "D", "E", "A"], "B": ["D", "A", "E", "C", "B", "F"], "i": 1, "j": 3, "swap": (2, 5)}

# 12.5 · cartera de proyectos con dos recursos (búsqueda tabú)
E5 = {"g": [30, 18, 24, 15, 21], "c": [6, 3, 5, 2, 4], "h": [3, 4, 2, 3, 3], "C": 11, "H": 9,
      "inicio": (1, 0, 1, 0, 0), "tenencia": 2, "tmax": 5}

# 12.6 · recocido en una secuencia de cuatro trabajos
E6 = {"p": [3, 6, 4, 5], "d": [5, 14, 8, 10], "w": [2, 1, 3, 2], "inicio": [0, 1, 2, 3],
      "T0": 8.0, "alfa": 0.9, "tmax": 4, "semilla": 3}

# 12.7 · tabú con intercambio desde el óptimo local del ejercicio 11.7
E7 = {"inicio": [1, 2, 3, 4, 6, 5, 1], "tenencia": 2, "tmax": 5}

# 12.8 · calibrar la temperatura
E8 = {"delta": 6, "p0": 0.8, "alfa": 0.95, "k": 50, "p_fin": 0.01}

# 12.9 · una generación con ruleta
E9 = {"g": [20, 12, 18, 9, 15], "v": [6, 3, 5, 2, 4], "cap": 12, "pen": 8, "pm": 0.1, "semilla_pob": 3, "semilla": 26}

# 12.10 · calibrar la temperatura inicial del recocido en el caso (desde la ruta de 84 km)
E10 = {"T0": [0.5, 5.0, 100.0], "alfa": 0.97, "its": 100, "semillas": list(range(1, 11))}

# Caso · parámetros de la tabú y del genético (el recocido es el del script)
TABU = {"tenencia": 3, "tmax": 10}
AG = {"pob": 10, "gens": 30, "pc": 0.9, "pm": 0.2, "torneo": 2, "semilla": 2026}
SEMILLAS = list(range(1, 11))


# ---------------------------------------------------------------- mochilas

def mochila(g, v, cap, pen=None):
    val = lambda x: sum(a * b for a, b in zip(g, x))
    vol = lambda x: sum(a * b for a, b in zip(v, x))
    fit = (lambda x: val(x) - pen * max(0, vol(x) - cap)) if pen is not None else val
    return val, vol, fit


def exacto_mochila(g, v, cap, otra=None):
    val, vol, _ = mochila(g, v, cap)
    todas = sorted(((val(x), x) for x in product((0, 1), repeat=len(g)) if vol(x) <= cap and (otra is None or otra(x))), reverse=True)
    assert todas[0][0] > todas[1][0]
    return todas[0][1], todas[0][0], len(todas)


def mochila_milp(g, v, cap):
    res = milp(-np.array(g, float), constraints=LinearConstraint(np.array([v], float), -np.inf, cap),
               integrality=np.ones(len(g)), bounds=Bounds(0, 1))
    assert res.success
    return tuple(int(round(t)) for t in res.x), round(-res.fun)


def tabu_binaria(x0, factible, val, ten, tmax):
    """Tabú con vecindario de complemento. Tabú: la variable cambiada, durante `ten` iteraciones.
    Aspiración: un movimiento tabú se permite si mejora la mejor solución. Elige el mejor admisible."""
    x = tuple(x0); mejor = x; hasta = {}; filas = []
    for t in range(1, tmax + 1):
        vec = []
        for j in range(len(x)):
            y = list(x); y[j] = 1 - y[j]; y = tuple(y)
            tab = hasta.get(j, 0) >= t
            ok = factible(y)
            adm = ok and (not tab or val(y) > val(mejor))
            vec.append((j + 1, y, val(y), ok, tab, adm))
        adm = [q for q in vec if q[5]]
        if not adm:
            break
        top = max(q[2] for q in adm)
        el = [q for q in adm if q[2] == top]
        assert len(el) == 1, ("empate en tabú", el)
        j, y = el[0][0], el[0][1]
        prohibidas = sorted(k for k, h in hasta.items() if h >= t)
        filas.append({"t": t, "x": x, "val": val(x), "mejor": val(mejor), "vec": vec, "tabu": [k + 1 for k in prohibidas],
                      "elige": j, "y": y, "val_y": val(y), "aspira": el[0][4]})
        x = y; hasta[j - 1] = t + ten
        if val(x) > val(mejor):
            mejor = x
    return mejor, filas


def recocido_a_mano(x0, vecinos, f, peor, T0, alfa, tmax, U):
    """Recocido como en clases: un número elige el vecino (índice = ⌊u·m⌋); si empeora en e > 0, otro
    número decide: se acepta si u ≤ e^(−e/T). Rechazado, se vuelve a elegir sin avanzar t. La
    temperatura baja a alfa·T después de cada movimiento aceptado."""
    x = x0; mejor = x0; T = T0; t = 0; k = 0; filas = []
    while t < tmax:
        cand = vecinos(x); m = len(cand)
        u1 = U[k]; k += 1
        y = cand[int(u1 * m)]
        e = peor(x, y)
        if e <= 0:
            fila = {"t": t, "x": x, "T": T, "m": m, "u1": u1, "y": y, "e": e, "p": None, "u2": None, "acepta": True}
        else:
            u2 = U[k]; k += 1; p = math.exp(-e / T)
            fila = {"t": t, "x": x, "T": T, "m": m, "u1": u1, "y": y, "e": e, "p": p, "u2": u2, "acepta": u2 <= p}
        fila["fx"], fila["fy"], fila["mejor"] = f(x), f(y), f(mejor)
        filas.append(fila)
        if fila["acepta"]:
            x = y; t += 1; T = alfa * T
            if peor(mejor, x) < 0:
                mejor = x
    return mejor, filas, k


def ag_una_generacion(pob, fit, U, pm, seleccion="torneo"):
    """Una generación a mano: dos padres (torneo de dos o ruleta), cruce en un punto, mutación de un gen
    con probabilidad pm, y la nueva población = los dos mejores padres + los dos hijos."""
    k = 0; n = len(pob); L = len(pob[0]); pasos = []
    def u():
        nonlocal k
        k += 1
        return U[k - 1]
    padres = []
    for _ in range(2):
        if seleccion == "torneo":
            a, b = u(), u(); ia, ib = int(a * n), int(b * n)
            gana = ia if (fit(pob[ia]), -ia) >= (fit(pob[ib]), -ib) else ib
            pasos.append(("torneo", a, b, ia + 1, ib + 1, gana + 1)); padres.append(gana)
        else:
            tot = sum(fit(p) for p in pob); acum = 0; r = u()
            for i, p in enumerate(pob):
                acum += fit(p) / tot
                if r < acum:
                    break
            pasos.append(("ruleta", r, i + 1)); padres.append(i)
    c_u = u(); corte = 1 + int(c_u * (L - 1))
    P1, P2 = pob[padres[0]], pob[padres[1]]
    hijos = [P1[:corte] + P2[corte:], P2[:corte] + P1[corte:]]
    mut = []
    for h in range(2):
        r = u()
        if r < pm:
            g = int(u() * L); hh = list(hijos[h]); hh[g] = 1 - hh[g]; hijos[h] = tuple(hh); mut.append((r, g + 1))
        else:
            mut.append((r, None))
    orden = sorted(range(n), key=lambda i: (-fit(pob[i]), i))
    nueva = [pob[orden[0]], pob[orden[1]]] + hijos
    return {"padres": [p + 1 for p in padres], "pasos": pasos, "corte_u": c_u, "corte": corte, "hijos": hijos,
            "mut": mut, "nueva": nueva, "usados": k}


# ---------------------------------------------------------------- rutas (caso y panadería)

def matriz_caso():
    m = U11.caso(); D, N = U11.matriz_caso(m)
    return m, D, N


def recocido_ruta(D, ini, semilla, its, T0, alfa):
    """El mismo recocido del script del caso: 2-opt al azar (dos posiciones con rnd.sample), acepta si
    mejora o si u < e^(−Δ/T), con T = T0·alfa^k. Devuelve la mejor ruta y la traza."""
    rnd = random.Random(semilla)
    actual = ini[:]; mejor = actual[:]; curva = []; primera = None; peores = 0
    for k in range(its):
        temp = T0 * (alfa ** k)
        i, j = sorted(rnd.sample(range(1, len(actual) - 1), 2))
        cand = actual[:i] + actual[i:j + 1][::-1] + actual[j + 1:]
        dlt = largo(cand, D) - largo(actual, D)
        if dlt < 0 or rnd.random() < math.exp(-dlt / max(temp, 1e-9)):
            if dlt > 0:
                peores += 1
            actual = cand
            if largo(actual, D) < largo(mejor, D):
                mejor = actual[:]; primera = k + 1
        curva.append(largo(mejor, D))
    return mejor, curva, primera, peores


def tabu_ruta(D, ini, ten, tmax):
    """Tabú con vecindario 2-opt (sin la inversión completa). Tabú: el par de puntos de los extremos del
    tramo invertido, durante `ten` iteraciones. Aspiración. Elige el mejor admisible (empate: el primer par)."""
    act = ini[:]; mejor = act[:]; hasta = {}; filas = []; curva = []
    for t in range(1, tmax + 1):
        cand = []
        for (i, j) in U11.movs_2opt(act):
            n = U11.aplicar_2opt(act, i, j); attr = frozenset((act[i], act[j]))
            tab = hasta.get(attr, 0) >= t; L = largo(n, D)
            if tab and not L < largo(mejor, D):
                continue
            cand.append((L, i, j, n, attr, tab))
        L, i, j, n, attr, tab = min(cand, key=lambda c: (c[0], c[1], c[2]))
        prohib = [sorted(a) for a, h in hasta.items() if h >= t]
        filas.append({"t": t, "ruta": act, "km": largo(act, D), "mov": (i, j), "par": sorted(attr), "nueva": n, "km_n": L,
                      "tabu": prohib, "aspira": tab})
        antes = largo(mejor, D); revisados = len(U11.movs_2opt(act))
        act = n; hasta[attr] = t + ten
        if L < largo(mejor, D):
            mejor = n[:]
        curva += [antes] * (revisados - 1) + [largo(mejor, D)]   # la mejora se conoce al terminar de revisar
    return mejor, filas, curva


def genetico_ruta(D, tiendas, semilla, pob, gens, pc, pm, k):
    """Genético con codificación de permutación: torneo de k, cruce OX, mutación por intercambio y
    elitismo de uno. Devuelve la mejor ruta, la curva y las evaluaciones."""
    rnd = random.Random(semilla)
    fit = lambda p: largo(["Taller"] + p + ["Taller"], D)
    P = [rnd.sample(tiendas, len(tiendas)) for _ in range(pob)]
    curva = [min(fit(p) for p in P)] * pob; mejores = [min(fit(p) for p in P)]
    def torneo():
        c = rnd.sample(range(pob), k); return min((P[i] for i in c), key=fit)
    def ox(a, b):
        i, j = sorted(rnd.sample(range(len(a)), 2))
        return cruce_ox(a, b, i, j)
    for _ in range(gens):
        elite = min(P, key=fit); nueva = [elite[:]]
        while len(nueva) < pob:
            a, b = torneo(), torneo()
            h = ox(a, b) if rnd.random() < pc else a[:]
            if rnd.random() < pm:
                i, j = rnd.sample(range(len(h)), 2); h[i], h[j] = h[j], h[i]
            nueva.append(h)
            curva.append(min(curva[-1], fit(h)))
        P = nueva; mejores.append(min(fit(p) for p in P))
    b = min(P, key=fit)
    return ["Taller"] + b + ["Taller"], curva, mejores


def cruce_ox(a, b, i, j):
    """Cruce de orden (OX): el hijo copia a[i..j] en su lugar y completa, desde j+1 y dando la vuelta,
    con los genes de b en el orden en que aparecen en b a partir de j+1."""
    hijo = [None] * len(a); hijo[i:j + 1] = a[i:j + 1]
    resto = [x for x in b[j + 1:] + b[:j + 1] if x not in hijo]
    pos = [q for q in list(range(j + 1, len(a))) + list(range(0, j + 1)) if hijo[q] is None]
    for q, x in zip(pos, resto):
        hijo[q] = x
    return hijo


def tard(seq, E):
    t = 0; s = 0
    for j in seq:
        t += E["p"][j]; s += E["w"][j] * max(0, t - E["d"][j])
    return s


# ---------------------------------------------------------------- cálculo de todo

def resultados():
    R = {}
    # ---- ejemplo: mochila de la feria
    val, vol, _ = mochila(EJ["g"], EJ["v"], EJ["cap"])
    fact = lambda x: vol(x) <= EJ["cap"]
    opt, z, nf = exacto_mochila(EJ["g"], EJ["v"], EJ["cap"])
    assert mochila_milp(EJ["g"], EJ["v"], EJ["cap"]) == (opt, z)
    x0 = EJ["inicio"]
    # búsqueda local desde el inicio: ¿es óptimo local?
    vec0 = [(j + 1, y, val(y), vol(y)) for j in range(5) for y in [tuple(1 - x0[q] if q == j else x0[q] for q in range(5))]]
    es_local = all(not fact(y) or val(y) <= val(x0) for _, y, _, _ in vec0)
    m_t, filas_t = tabu_binaria(x0, fact, val, EJ["tenencia"], EJ["tmax_tabu"])
    U_rs = aleatorios(EJ["semilla_rs"], 20)
    def vec_fact(x):
        out = []
        for j in range(5):
            y = tuple(1 - x[q] if q == j else x[q] for q in range(5))
            if fact(y):
                out.append(y)
        return out
    m_rs, filas_rs, usados_rs = recocido_a_mano(x0, vec_fact, val, lambda a, b: val(a) - val(b), EJ["T0"], EJ["alfa"], EJ["tmax_rs"], U_rs)
    _, _, fit_ag = mochila(EJ["g"], EJ["v"], EJ["cap"], EJ["pen"])
    rp = random.Random(EJ["semilla_pob"])
    pob = [tuple(rp.randint(0, 1) for _ in range(5)) for _ in range(4)]
    U_ag = aleatorios(EJ["semilla_ag"], 20)
    ag = ag_una_generacion(pob, fit_ag, U_ag, EJ["pm"])
    R["ej"] = {"opt": opt, "z": z, "vol_opt": vol(opt), "factibles": nf, "x0": x0, "val0": val(x0), "vol0": vol(x0),
               "es_local": es_local, "vec0": vec0, "tabu": filas_t, "tabu_mejor": m_t, "tabu_z": val(m_t),
               "U_rs": U_rs[:usados_rs], "rs": filas_rs, "rs_mejor": m_rs, "rs_z": val(m_rs),
               "pob": pob, "fit_pob": [fit_ag(p) for p in pob], "U_ag": U_ag[:ag["usados"]], "ag": ag,
               "fit_nueva": [fit_ag(p) for p in ag["nueva"]], "val": val, "vol": vol, "fit": fit_ag}
    assert es_local and val(m_t) == z
    # ---- 12.1
    R["e1"] = {(d, T): math.exp(-d / T) for d in E1["deltas"] for T in E1["temps"]}
    # ---- 12.2
    def elige(mejor):
        adm = [(km, mov, tab) for mov, km, tab in E2["vecinos"] if not tab or km < mejor]
        return min(adm)
    R["e2"] = {"a": elige(E2["mejor"]), "b": elige(E2["mejor_b"])}
    # ---- 12.3
    v3, w3, f3 = mochila(E3["g"], E3["v"], E3["cap"], E3["pen"])
    c = E3["corte"]; h1 = E3["A"][:c] + E3["B"][c:]; h2 = E3["B"][:c] + E3["A"][c:]
    h1m = tuple(1 - h1[q] if q == E3["muta"] - 1 else h1[q] for q in range(len(h1)))
    o3, z3, _ = exacto_mochila(E3["g"], E3["v"], E3["cap"])
    R["e3"] = {"A": (v3(E3["A"]), w3(E3["A"]), f3(E3["A"])), "B": (v3(E3["B"]), w3(E3["B"]), f3(E3["B"])),
               "h1": h1, "h2": h2, "h1m": h1m, "f": {k: (v3(x), w3(x), f3(x)) for k, x in (("h1", h1), ("h2", h2), ("h1m", h1m))},
               "opt": o3, "z": z3}
    # ---- 12.4
    Dp = U11.matriz_de(U11.EJ_POS)
    hijo = cruce_ox(E4["A"], E4["B"], E4["i"], E4["j"])
    a, b = E4["swap"]; hm = hijo[:]; hm[a - 1], hm[b - 1] = hm[b - 1], hm[a - 1]
    ruta = lambda p: ["P"] + p + ["P"]
    R["e4"] = {"hijo": hijo, "mut": hm, "km_A": largo(ruta(E4["A"]), Dp), "km_B": largo(ruta(E4["B"]), Dp),
               "km_hijo": largo(ruta(hijo), Dp), "km_mut": largo(ruta(hm), Dp)}
    # ---- 12.5
    val5 = lambda x: sum(a * b for a, b in zip(E5["g"], x))
    fact5 = lambda x: sum(a * b for a, b in zip(E5["c"], x)) <= E5["C"] and sum(a * b for a, b in zip(E5["h"], x)) <= E5["H"]
    todas5 = sorted(((val5(x), x) for x in product((0, 1), repeat=5) if fact5(x)), reverse=True)
    assert todas5[0][0] > todas5[1][0]
    m5, f5 = tabu_binaria(E5["inicio"], fact5, val5, E5["tenencia"], E5["tmax"])
    R["e5"] = {"filas": f5, "mejor": m5, "z_tabu": val5(m5), "opt": todas5[0][1], "z": todas5[0][0], "val": val5,
               "cost": lambda x: sum(a * b for a, b in zip(E5["c"], x)), "hor": lambda x: sum(a * b for a, b in zip(E5["h"], x))}
    # ---- 12.6
    U6 = aleatorios(E6["semilla"], 20)
    def vec6(s):
        out = []
        for q in range(len(s) - 1):
            n = list(s); n[q], n[q + 1] = n[q + 1], n[q]; out.append(tuple(n))
        return out
    m6, f6, k6 = recocido_a_mano(tuple(E6["inicio"]), vec6, lambda s: tard(s, E6), lambda a, b: tard(b, E6) - tard(a, E6),
                                 E6["T0"], E6["alfa"], E6["tmax"], U6)
    todas6 = sorted((tard(s, E6), s) for s in permutations(range(4)))
    R["e6"] = {"U": U6[:k6], "filas": f6, "mejor": m6, "z_mejor": tard(m6, E6), "opt": todas6[0][1], "z": todas6[0][0],
               "z0": tard(E6["inicio"], E6)}
    # ---- 12.7
    D5 = U11.matriz_de(U11.E5_POS)
    m7, f7 = tabu_swap(D5, E7["inicio"], E7["tenencia"], E7["tmax"])
    R["e7"] = {"filas": f7, "mejor": m7, "km": largo(m7, D5), "z": U11.exacto(D5, 1)[0], "D": D5}
    # ---- 12.8
    T0 = E8["delta"] / math.log(1 / E8["p0"])
    Tk = T0 * E8["alfa"] ** E8["k"]
    Tmin = E8["delta"] / math.log(1 / E8["p_fin"])
    kmin = math.ceil(math.log(Tmin / T0) / math.log(E8["alfa"]))
    assert math.exp(-E8["delta"] / (T0 * E8["alfa"] ** kmin)) < E8["p_fin"] <= math.exp(-E8["delta"] / (T0 * E8["alfa"] ** (kmin - 1)))
    R["e8"] = {"T0": T0, "Tk": Tk, "pk": math.exp(-E8["delta"] / Tk), "Tmin": Tmin, "kmin": kmin}
    # ---- 12.9
    _, _, f9 = mochila(E9["g"], E9["v"], E9["cap"], E9["pen"])
    rp = random.Random(E9["semilla_pob"])
    pob9 = [tuple(rp.randint(0, 1) for _ in range(5)) for _ in range(4)]
    U9 = aleatorios(E9["semilla"], 20)
    ag9 = ag_una_generacion(pob9, f9, U9, E9["pm"], "ruleta")
    o9, z9, _ = exacto_mochila(E9["g"], E9["v"], E9["cap"])
    R["e9"] = {"pob": pob9, "fit": [f9(p) for p in pob9], "U": U9[:ag9["usados"]], "ag": ag9, "fit_nueva": [f9(p) for p in ag9["nueva"]],
               "opt": o9, "z": z9, "f": f9, "tot": sum(f9(p) for p in pob9)}
    # ---- 12.10
    mc, Dc, _ = matriz_caso()
    ini = mc.calcular()["u11"]["vecino_ruta"]
    tab10 = {}
    for T0_ in E10["T0"]:
        tab10[T0_] = [largo(recocido_ruta(Dc, ini, s, E10["its"], T0_, E10["alfa"])[0], Dc) for s in E10["semillas"]]
    R["e10"] = {"tab": tab10, "z": 78, "T_fin": {T0_: T0_ * E10["alfa"] ** (E10["its"] - 1) for T0_ in E10["T0"]}}
    # ---- caso
    R["caso"] = caso_u12()
    return R


def tabu_swap(D, ini, ten, tmax):
    r = ini[:]; mejor = r; hasta = {}; filas = []
    for t in range(1, tmax + 1):
        c = []; todos = []
        for i in range(1, len(r) - 1):
            for j in range(i + 1, len(r) - 1):
                n = r[:]; n[i], n[j] = n[j], n[i]; par = frozenset((r[i], r[j]))
                tab = hasta.get(par, 0) >= t; L = largo(n, D)
                todos.append((sorted(par), L, tab))
                if tab and not L < largo(mejor, D):
                    continue
                c.append((L, i, j, n, par, tab))
        c.sort(key=lambda x: (x[0], x[1], x[2]))
        assert not (len(c) > 1 and c[0][0] == c[1][0]), c[:2]
        L, i, j, n, par, tab = c[0]
        filas.append({"t": t, "ruta": r, "km": largo(r, D), "par": sorted(par), "nueva": n, "km_n": L,
                      "tabu": sorted(sorted(p) for p, h in hasta.items() if h >= t), "todos": todos, "aspira": tab,
                      "mejor": largo(mejor, D)})
        r = n; hasta[par] = t + ten
        if L < largo(mejor, D):
            mejor = n
    return mejor, filas


def caso_u12():
    m, D, N = matriz_caso()
    C = m.calcular()
    ini = C["u11"]["vecino_ruta"]; z = C["u4"]["tsp_km"]
    # recocido: el del script, reproducido paso a paso
    rs, curva_rs, primera, peores = recocido_ruta(D, ini, m.SEMILLA, 4000, 20.0, 0.999)
    assert rs == C["u12"]["recocido_ruta"] and largo(rs, D) == C["u12"]["recocido_km"]
    # tabú
    tb, filas_tb, curva_tb = tabu_ruta(D, ini, TABU["tenencia"], TABU["tmax"])
    it_tb = next(f["t"] for f in filas_tb if f["km_n"] == z)
    # genético
    ag, curva_ag, mejores_ag = genetico_ruta(D, m.TIENDAS, AG["semilla"], AG["pob"], AG["gens"], AG["pc"], AG["pm"], AG["torneo"])
    evals_ag = len(curva_ag)
    # diez semillas
    filas = {}
    def resumen(v, evals):
        return {"mejor": min(v), "media": statistics.mean(v), "peor": max(v), "llegan": sum(1 for x in v if x == z), "evals": evals}
    filas["rs4000"] = resumen([largo(recocido_ruta(D, ini, s, 4000, 20.0, 0.999)[0], D) for s in SEMILLAS], 4000)
    filas["rs300a"] = resumen([largo(recocido_ruta(D, ini, s, 300, 20.0, 0.999)[0], D) for s in SEMILLAS], 300)
    filas["rs300b"] = resumen([largo(recocido_ruta(D, ini, s, 300, 20.0, 0.99)[0], D) for s in SEMILLAS], 300)
    filas["tabu"] = resumen([largo(tabu_ruta(D, ["Taller"] + random.Random(s).sample(m.TIENDAS, 6) + ["Taller"], TABU["tenencia"], TABU["tmax"])[0], D)
                             for s in SEMILLAS], 14 * TABU["tmax"])
    filas["ag"] = resumen([largo(genetico_ruta(D, m.TIENDAS, s, AG["pob"], AG["gens"], AG["pc"], AG["pm"], AG["torneo"])[0], D) for s in SEMILLAS], evals_ag)
    return {"ini": ini, "km_ini": largo(ini, D), "z": z, "rs": rs, "km_rs": largo(rs, D), "primera_rs": primera, "peores_rs": peores,
            "T_fin": 20.0 * 0.999 ** 3999, "curva_rs": curva_rs, "tabu": tb, "km_tabu": largo(tb, D), "filas_tb": filas_tb,
            "it_tb": it_tb, "evals_tb": 14 * TABU["tmax"], "curva_tb": curva_tb, "ag": ag, "km_ag": largo(ag, D),
            "curva_ag": curva_ag, "evals_ag": evals_ag, "mejores_ag": mejores_ag, "semillas": filas,
            "gap_ag": (largo(ag, D) - z) / z, "D": D}


# ---------------------------------------------------------------- tablas en Markdown

def bits(x):
    return "".join(str(b) for b in x)


def tablas(R):
    T = {}
    e = R["ej"]; val, vol = e["val"], e["vol"]
    t = "| Caja | " + " | ".join(f"{k + 1} · {n}" for k, n in enumerate(EJ["nombres"])) + " |\n|---|" + "---|" * 5 + "\n"
    t += "| Ganancia (miles de \\$) | " + " | ".join(str(x) for x in EJ["g"]) + " |\n"
    t += "| Volumen (jabas) | " + " | ".join(str(x) for x in EJ["v"]) + " |\n"
    T["ej_datos"] = t
    t = "| Cambia | Vecino | Ganancia | Jabas | ¿Cabe? |\n|---|---|---|---|---|\n"
    for j, y, g, w in e["vec0"]:
        t += f"| $x_{j}$ | {bits(y)} | {g} | {w} | {'sí' if w <= EJ['cap'] else 'no'} |\n"
    T["ej_vec0"] = t
    t = "| t | Actual | Ganancia | Mejor hasta ahora | Prohibidas | Vecinos admisibles (cambia $x_j$: ganancia) | Elige |\n|---|---|---|---|---|---|---|\n"
    for f in e["tabu"]:
        adm = "; ".join(f"$x_{j}$: {g}" for j, y, g, ok, tab, a in f["vec"] if a)
        proh = ", ".join(f"$x_{j}$" for j in f["tabu"]) or "ninguna"
        t += f"| {f['t']} | {bits(f['x'])} | {f['val']} | {f['mejor']} | {proh} | {adm} | $x_{f['elige']}$ → {bits(f['y'])} ({f['val_y']}) |\n"
    T["ej_tabu"] = t
    T["ej_rs"] = tabla_rs(e["rs"], bits, "ganancia")
    t = "| Individuo | Cromosoma | Ganancia | Jabas | Aptitud |\n|---|---|---|---|---|\n"
    for i, p in enumerate(e["pob"], 1):
        t += f"| {i} | {bits(p)} | {val(p)} | {vol(p)} | {e['fit'](p)} |\n"
    T["ej_pob"] = t
    T["ej_ag"] = tabla_ag(e["ag"], e["fit"], val, vol)
    # 12.1
    t = "| Empeora en Δ | " + " | ".join(f"T = {T_}" for T_ in E1["temps"]) + " |\n|---|" + "---|" * len(E1["temps"]) + "\n"
    for d in E1["deltas"]:
        t += f"| {d} | " + " | ".join(fmt(R["e1"][(d, T_)], 3) for T_ in E1["temps"]) + " |\n"
    T["e1"] = t
    # 12.2
    t = "| Movimiento | Km del vecino | ¿Tabú? |\n|---|---|---|\n"
    for mov, km, tab in E2["vecinos"]:
        t += f"| {mov} | {km} | {'sí' if tab else 'no'} |\n"
    T["e2"] = t
    # 12.3
    t = "| Proyecto | 1 | 2 | 3 | 4 | 5 | 6 |\n|---|---|---|---|---|---|---|\n"
    t += "| Ganancia | " + " | ".join(str(x) for x in E3["g"]) + " |\n| Volumen | " + " | ".join(str(x) for x in E3["v"]) + " |\n"
    T["e3_datos"] = t
    t = "| Cromosoma | Bits | Ganancia | Volumen | Aptitud |\n|---|---|---|---|---|\n"
    e3 = R["e3"]
    for nom, x, f in (("Padre A", E3["A"], e3["A"]), ("Padre B", E3["B"], e3["B"]), ("Hijo 1", e3["h1"], e3["f"]["h1"]),
                      ("Hijo 2", e3["h2"], e3["f"]["h2"]), ("Hijo 1 mutado", e3["h1m"], e3["f"]["h1m"])):
        t += f"| {nom} | {bits(x)} | {f[0]} | {f[1]} | {f[2]} |\n"
    T["e3"] = t
    # 12.5
    t = "| Proyecto | 1 | 2 | 3 | 4 | 5 |\n|---|---|---|---|---|---|\n"
    t += "| Valor (millones de \\$) | " + " | ".join(str(x) for x in E5["g"]) + " |\n"
    t += "| Costo (millones de \\$) | " + " | ".join(str(x) for x in E5["c"]) + " |\n"
    t += "| Ingenieros | " + " | ".join(str(x) for x in E5["h"]) + " |\n"
    T["e5_datos"] = t
    e5 = R["e5"]
    t = "| t | Actual | Valor | Mejor | Prohibidas | Vecinos factibles (cambia $x_j$: valor) | Elige |\n|---|---|---|---|---|---|---|\n"
    for f in e5["filas"]:
        fac = "; ".join(f"$x_{j}$: {g}{' (tabú)' if tab and not a else ''}{' (tabú, aspira)' if tab and a else ''}" for j, y, g, ok, tab, a in f["vec"] if ok)
        proh = ", ".join(f"$x_{j}$" for j in f["tabu"]) or "ninguna"
        t += f"| {f['t']} | {bits(f['x'])} | {f['val']} | {f['mejor']} | {proh} | {fac} | $x_{f['elige']}$ → {bits(f['y'])} ({f['val_y']}) |\n"
    T["e5"] = t
    # 12.6
    t = "| Trabajo | 1 | 2 | 3 | 4 |\n|---|---|---|---|---|\n"
    t += "| Duración (h) | " + " | ".join(str(x) for x in E6["p"]) + " |\n| Entrega (h) | " + " | ".join(str(x) for x in E6["d"]) + " |\n"
    t += "| Multa por hora | " + " | ".join(str(x) for x in E6["w"]) + " |\n"
    T["e6_datos"] = t
    T["e6"] = tabla_rs(R["e6"]["filas"], lambda s: "-".join(str(j + 1) for j in s), "atraso")
    # 12.7
    t = "| t | Ruta actual | km | Prohibidos | Elige | km nuevo | Mejor |\n|---|---|---|---|---|---|---|\n"
    for f in R["e7"]["filas"]:
        proh = ", ".join("{" + f"{a}, {b}" + "}" for a, b in f["tabu"]) or "ninguno"
        t += f"| {f['t']} | {flecha(f['ruta'])} | {f['km']} | {proh} | {{{f['par'][0]}, {f['par'][1]}}} | {f['km_n']} | {min(f['mejor'], f['km_n'])} |\n"
    T["e7"] = t
    # 12.9
    e9 = R["e9"]
    t = "| Producto | 1 | 2 | 3 | 4 | 5 |\n|---|---|---|---|---|---|\n"
    t += "| Ganancia | " + " | ".join(str(x) for x in E9["g"]) + " |\n| Kilos | " + " | ".join(str(x) for x in E9["v"]) + " |\n"
    T["e9_datos"] = t
    val9, vol9, _ = mochila(E9["g"], E9["v"], E9["cap"])
    acum = 0
    t = "| Individuo | Cromosoma | Ganancia | Kilos | Aptitud | Probabilidad | Acumulada |\n|---|---|---|---|---|---|---|\n"
    for i, p in enumerate(e9["pob"], 1):
        f = e9["f"](p); acum += f / e9["tot"]
        t += f"| {i} | {bits(p)} | {val9(p)} | {vol9(p)} | {f} | {fmt(f / e9['tot'], 3)} | {fmt(acum, 3)} |\n"
    T["e9_pob"] = t
    T["e9_ag"] = tabla_ag(e9["ag"], e9["f"], val9, vol9)
    # 12.10
    e10 = R["e10"]
    t = "| Temperatura inicial | Mejor ruta de cada semilla (1 a 10), km | Llegan a 78 | Promedio |\n|---|---|---|---|\n"
    for T0_, v in e10["tab"].items():
        t += f"| {fmt(T0_, 1)} | {', '.join(str(x) for x in v)} | {sum(1 for x in v if x == e10['z'])} de 10 | {fmt(statistics.mean(v), 1)} |\n"
    T["e10"] = t
    # caso
    c = R["caso"]
    t = "| t | Ruta actual | km | Prohibidos | Movimiento | Par que entra a la lista | km nuevo |\n|---|---|---|---|---|---|---|\n"
    for f in c["filas_tb"]:
        proh = ", ".join("{" + f"{a}, {b}" + "}" for a, b in f["tabu"]) or "ninguno"
        t += f"| {f['t']} | {flecha(f['ruta'])} | {f['km']} | {proh} | ({f['mov'][0]}, {f['mov'][1]}) | {{{f['par'][0]}, {f['par'][1]}}} | {f['km_n']} |\n"
    T["caso_tabu"] = t
    S = c["semillas"]
    t = "| Método | Evaluaciones por corrida | Mejor | Promedio | Peor | Llegan a 78 |\n|---|---|---|---|---|---|\n"
    for k, nom in (("rs4000", "Recocido, 4.000 iteraciones, α = 0,999"), ("rs300a", "Recocido, 300 iteraciones, α = 0,999"),
                   ("rs300b", "Recocido, 300 iteraciones, α = 0,99"), ("tabu", "Tabú desde una ruta al azar, 10 iteraciones"),
                   ("ag", "Genético, 10 individuos, 30 generaciones")):
        s = S[k]
        t += f"| {nom} | {fmt(s['evals'])} | {s['mejor']} | {fmt(s['media'], 1)} | {s['peor']} | {s['llegan']} de 10 |\n"
    T["caso_semillas"] = t
    return T


def tabla_rs(filas, ver, nombre):
    t = f"| t | Actual ({nombre}) | T | u (vecino) | Vecino ({nombre}) | Empeora en | $e^{{-\\Delta/T}}$ | u (acepta) | Resultado |\n|---|---|---|---|---|---|---|---|---|\n"
    for f in filas:
        p = fmt(f["p"], 3) if f["p"] is not None else "–"
        u2 = fmt(f["u2"], 2) if f["u2"] is not None else "–"
        emp = str(f["e"]) if f["e"] > 0 else "no empeora"
        t += (f"| {f['t']} | {ver(f['x'])} ({f['fx']}) | {fmt(f['T'], 2)} | {fmt(f['u1'], 2)} de {f['m']} | {ver(f['y'])} ({f['fy']}) | "
              f"{emp} | {p} | {u2} | {'acepta' if f['acepta'] else 'rechaza'} |\n")
    return t


def tabla_ag(ag, fit, val, vol):
    t = "| Paso | Números | Resultado |\n|---|---|---|\n"
    for k, p in enumerate(ag["pasos"], 1):
        if p[0] == "torneo":
            t += f"| Padre {k}: torneo | {fmt(p[1], 2)} y {fmt(p[2], 2)} | compiten {p[3]} y {p[4]}; gana {p[5]} |\n"
        else:
            t += f"| Padre {k}: ruleta | {fmt(p[1], 2)} | sale el {p[2]} |\n"
    t += f"| Cruce | {fmt(ag['corte_u'], 2)} | corte después del gen {ag['corte']} |\n"
    for h, (r, g) in enumerate(ag["mut"], 1):
        t += f"| Mutación hijo {h} | {fmt(r, 2)} | {'muta el gen ' + str(g) if g else 'no muta'} |\n"
    for h, x in enumerate(ag["hijos"], 1):
        t += f"| Hijo {h} | – | {bits(x)}: ganancia {val(x)}, volumen {vol(x)}, aptitud {fit(x)} |\n"
    return t


# ---------------------------------------------------------------- cifras que el texto debe tener

def esperados(R):
    e, c = R["ej"], R["caso"]
    s = [bits(e["opt"]), f"{e['z']} mil", f"{e['factibles']} combinaciones", bits(e["x0"]), f"{e['val0']} mil"]
    s += [", ".join(fmt(u, 2) for u in e["U_rs"]), ", ".join(fmt(u, 2) for u in e["U_ag"])]
    s += [bits(e["rs_mejor"]), f"{e['rs_z']} mil"]
    s += [bits(p) for p in e["ag"]["nueva"]]
    s += [f"{max(e['fit_pob'])} a {max(e['fit_nueva'])}"]
    # 12.1
    s += [fmt(v, 3) for v in R["e1"].values()]
    # 12.2
    s += [f"{R['e2']['a'][1]}, de {R['e2']['a'][0]} km", f"{R['e2']['b'][1]}, de {R['e2']['b'][0]} km"]
    # 12.3
    s += [bits(R["e3"]["h1"]), bits(R["e3"]["h2"]), bits(R["e3"]["h1m"]), bits(R["e3"]["opt"]), f"{R['e3']['z']}"]
    # 12.4
    e4 = R["e4"]
    s += [" ".join(e4["hijo"]), " ".join(e4["mut"]), f"{e4['km_A']} km", f"{e4['km_B']} km", f"{e4['km_hijo']} km", f"{e4['km_mut']} km"]
    # 12.5
    e5 = R["e5"]
    s += [bits(e5["opt"]), f"{e5['z']} millones", bits(e5["mejor"])]
    # 12.6
    e6 = R["e6"]
    s += [", ".join(fmt(u, 2) for u in e6["U"]), "-".join(str(j + 1) for j in e6["opt"]), f"atraso ponderado de {e6['z']}",
          f"{e6['z0']}", f"{e6['z_mejor']}"]
    # 12.7
    s += [f"{R['e7']['km']} km", flecha(R["e7"]["mejor"])]
    # 12.8
    e8 = R["e8"]
    s += [fmt(e8["T0"], 2), fmt(e8["Tk"], 2), fmt(e8["pk"], 3), fmt(e8["Tmin"], 2), f"iteración {e8['kmin']}"]
    # 12.9
    e9 = R["e9"]
    s += [", ".join(fmt(u, 2) for u in e9["U"]), bits(e9["opt"]), f"{e9['z']} mil", f"{max(e9['fit'])} a {max(e9['fit_nueva'])}"]
    # caso
    s += [f"{c['km_ini']} km", flecha(c["rs"]), f"iteración {c['primera_rs']}", f"{c['peores_rs']} veces", fmt(c["T_fin"], 2),
          flecha(c["tabu"]), f"iteración {c['it_tb']}", flecha(c["ag"]), f"{c['km_ag']} km", pct(c["gap_ag"]),
          f"{c['evals_ag']} evaluaciones", f"{c['evals_tb']} evaluaciones"]
    return s


# ---------------------------------------------------------------- figuras

TINTA, SUAVE, ACENTO = U11.TINTA, U11.SUAVE, U11.ACENTO
COLORES = ["#1F5F8B", "#2E7D4F", "#8A4FA3", "#9C6B1F", "#5F656B"]
svg, texto = U11.svg, U11.texto


def fig_probabilidad(R):
    x0, y0, w, h = 70, 30, 520, 260
    px = lambda d: x0 + d / 20 * w
    py = lambda p: y0 + h - p * h
    partes = []
    for d in range(0, 21, 5):
        partes.append(f'<line x1="{px(d):.1f}" y1="{y0}" x2="{px(d):.1f}" y2="{y0 + h}" stroke="#EEECE9"/>')
        partes.append(texto(px(d), y0 + h + 18, str(d), SUAVE, 11))
    for p in (0, 0.25, 0.5, 0.75, 1):
        partes.append(f'<line x1="{x0}" y1="{py(p):.1f}" x2="{x0 + w}" y2="{py(p):.1f}" stroke="#EEECE9"/>')
        partes.append(texto(x0 - 8, py(p) + 4, fmt(p, 2), SUAVE, 11, "end"))
    partes.append(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{TINTA}" stroke-width="1.3"/>')
    partes.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{TINTA}" stroke-width="1.3"/>')
    for k, T_ in enumerate([1, 2, 5, 10, 20]):
        pts = " ".join(f"{px(d / 10):.1f},{py(math.exp(-(d / 10) / T_)):.1f}" for d in range(0, 201))
        partes.append(f'<polyline points="{pts}" fill="none" stroke="{COLORES[k % 5] if k < 4 else ACENTO}" stroke-width="2.2"/>')
        dl = {1: 1.2, 2: 2.6, 5: 6, 10: 11, 20: 16}[T_]
        partes.append(texto(px(dl) + 6, py(math.exp(-dl / T_)) - 6, f"T = {T_}", COLORES[k % 5] if k < 4 else ACENTO, 12, "start", "600"))
    partes.append(texto(x0 + w / 2, y0 + h + 38, "Δ: cuánto empeora el vecino", TINTA, 12, "middle", "600"))
    partes.append(texto(x0 - 52, y0 - 10, "probabilidad de aceptarlo", TINTA, 12, "start", "600"))
    return svg(620, 340, partes, "Probabilidad de aceptar un vecino peor en el recocido simulado")


def fig_convergencia(R):
    c = R["caso"]
    x0, y0, w, h = 70, 30, 560, 250
    lx = lambda n: x0 + math.log10(n) / math.log10(4000) * w
    ymin, ymax = 76, 92
    py = lambda v: y0 + h - (v - ymin) / (ymax - ymin) * h
    partes = []
    for n in (1, 10, 100, 1000, 4000):
        partes.append(f'<line x1="{lx(n):.1f}" y1="{y0}" x2="{lx(n):.1f}" y2="{y0 + h}" stroke="#EEECE9"/>')
        partes.append(texto(lx(n), y0 + h + 18, fmt(n), SUAVE, 11))
    for v in range(78, 93, 2):
        partes.append(f'<line x1="{x0}" y1="{py(v):.1f}" x2="{x0 + w}" y2="{py(v):.1f}" stroke="#EEECE9"/>')
        partes.append(texto(x0 - 8, py(v) + 4, str(v), SUAVE, 11, "end"))
    partes.append(f'<line x1="{x0}" y1="{py(78):.1f}" x2="{x0 + w}" y2="{py(78):.1f}" stroke="{TINTA}" stroke-dasharray="5 4"/>')
    partes.append(texto(x0 + w - 4, py(78) + 16, "óptimo: 78 km", TINTA, 11, "end"))
    def linea(curva, color, etiqueta, dx, dy):
        pts = []
        prev = None
        for n, v in enumerate(curva, 1):
            if prev is not None and v != prev:
                pts.append(f"{lx(n):.1f},{py(prev):.1f}")
            pts.append(f"{lx(n):.1f},{py(v):.1f}"); prev = v
        partes.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2.4"/>')
        partes.append(texto(lx(len(curva)) + dx, py(curva[-1]) + dy, etiqueta, color, 12, "end", "600"))
    linea(c["curva_rs"], COLORES[0], "recocido", 0, -8)
    linea(c["curva_tb"], COLORES[1], "tabú", 0, -22)
    linea(c["curva_ag"], ACENTO, "genético", 0, -8)
    partes.append(texto(x0 + w / 2, y0 + h + 38, "soluciones evaluadas (escala logarítmica)", TINTA, 12, "middle", "600"))
    partes.append(texto(x0 - 52, y0 - 10, "mejor ruta encontrada (km)", TINTA, 12, "start", "600"))
    return svg(660, 330, partes, "Estampa Sur: la mejor ruta de cada metaheurística según las soluciones evaluadas")


def dibujar(R):
    FIGURAS.mkdir(parents=True, exist_ok=True)
    figs = {"u12_probabilidad.svg": fig_probabilidad(R), "u12_convergencia.svg": fig_convergencia(R)}
    for n, s in figs.items():
        (FIGURAS / n).write_text(s, encoding="utf-8")
    print("   figuras:", ", ".join(figs))


# ---------------------------------------------------------------- OPL, cadena y revisión

def comparar_con_opl(R):
    r = correr(MODELOS / "u12_feria_exacto.mod", MODELOS / "u12_feria_exacto.dat")
    if r is None:
        print("OPL: oplrun no está instalado; el óptimo se comprueba con enumeración y milp")
        return None
    assert r["codigo"] == 0 and r["objetivo"] is not None, r["salida"][-500:]
    assert abs(r["objetivo"] - R["ej"]["z"]) < 1e-6
    x = tuple(int(r["valores"][f"x_{n}"]) for n in EJ["nombres"])
    assert x == R["ej"]["opt"], x
    print(f"OPL: el modelo exacto da {fmt(r['objetivo'])} mil pesos con {bits(x)}, igual que la enumeración y milp")
    return True


def cadena(R):
    C = U11.caso().calcular(); c = R["caso"]
    ok = C["u12"]["recocido_km"] == c["km_rs"] == 78 and C["u12"]["recocido_ruta"] == c["rs"]
    ok &= C["u12"]["optimo_km"] == c["z"] and C["u11"]["vecino_km"] == c["km_ini"]
    print("CADENA:", "OK, el recocido con semilla 2026 llega a 78 km desde la ruta de 84 km del caso" if ok else "NO calza")
    return ok


def imprimir(R):
    e, c = R["ej"], R["caso"]
    print("== ejemplo: óptimo", bits(e["opt"]), e["z"], "· inicio", bits(e["x0"]), e["val0"], "local:", e["es_local"])
    print("   tabú", [(f["t"], bits(f["y"]), f["val_y"]) for f in e["tabu"]])
    print("   recocido U", e["U_rs"], [(bits(f["y"]), f["e"], f["acepta"]) for f in e["rs"]], "mejor", e["rs_z"])
    print("   genético pob", [bits(p) for p in e["pob"]], e["fit_pob"], "nueva", [bits(p) for p in e["ag"]["nueva"]], e["fit_nueva"], "U", e["U_ag"])
    print("== 12.2", R["e2"], "· 12.3", R["e3"]["f"], R["e3"]["z"], "· 12.4", R["e4"])
    print("== 12.5", [(f["t"], bits(f["y"]), f["val_y"]) for f in R["e5"]["filas"]], "óptimo", bits(R["e5"]["opt"]), R["e5"]["z"])
    print("== 12.6", R["e6"]["U"], [(f["y"], f["e"], f["acepta"]) for f in R["e6"]["filas"]], R["e6"]["z_mejor"], "óptimo", R["e6"]["z"])
    print("== 12.7", [(f["t"], f["par"], f["km_n"]) for f in R["e7"]["filas"]], R["e7"]["km"])
    print("== 12.8", R["e8"])
    print("== 12.9", [bits(p) for p in R["e9"]["pob"]], R["e9"]["fit"], [bits(p) for p in R["e9"]["ag"]["nueva"]], R["e9"]["fit_nueva"], R["e9"]["z"])
    print("== 12.10", R["e10"]["tab"])
    print("== caso: recocido", c["km_rs"], "primera", c["primera_rs"], "peores", c["peores_rs"], "· tabú", c["km_tabu"], "it", c["it_tb"],
          "· genético", c["km_ag"], c["evals_ag"])
    print("   semillas", {k: (v["mejor"], round(v["media"], 1), v["peor"], v["llegan"]) for k, v in c["semillas"].items()})


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    dibujar(R)
    T = tablas(R)
    if "--tablas" in sys.argv:
        for k, v in T.items():
            print(f"\n<!-- {k} -->\n{v}")
    if not cadena(R):
        sys.exit(1)
    comparar_con_opl(R)
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        md_plano = " ".join(md_n.split())
        faltan = [x for x in esperados(R) if x not in md_n and x not in md_plano]
        faltan += [f"tabla {k}" for k, v in T.items() if v.strip() not in md]
        mod = (MODELOS / "u12_feria_exacto.mod").read_text(encoding="utf-8")
        faltan += [f"OPL: {l.strip()}" for l in mod.splitlines() if l.strip() and not l.strip().startswith(("/*", "*")) and l.rstrip() not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
