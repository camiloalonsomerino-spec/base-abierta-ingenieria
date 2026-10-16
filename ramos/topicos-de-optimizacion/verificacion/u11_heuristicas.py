"""Unidad 11 · Heurísticas constructivas y búsqueda local.

Recalcula todas las cifras de la unidad desde los datos: el vecino más cercano, la inserción más
barata, 2-opt, intercambio, primer mejor y mejor mejora, la regla de fechas y la búsqueda local en
secuencias, los ahorros de Clarke y Wright, y compara cada heurística con el óptimo exacto (fuerza
bruta, `scipy.optimize.milp` y, si hay CPLEX, el modelo OPL de `modelos/`). Genera las tablas en
Markdown y dibuja las figuras SVG de `unidades/figuras/`. Importa el caso integrador y compara su
pieza U11.

    python u11_heuristicas.py            # imprime los resultados y redibuja las figuras
    python u11_heuristicas.py --tablas   # además imprime las tablas en Markdown
    python u11_heuristicas.py --revisar  # además busca cada cifra y cada tabla en el .md
"""
from itertools import combinations, permutations
from pathlib import Path
import importlib.util, math, sys

import networkx as nx
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
FIGURAS = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "11-heuristicas.md"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402


# ---------------------------------------------------------------- formato chileno

def fmt(x, dec=0):
    """Coma decimal y punto de miles, redondeo hacia arriba en el 5 (28,125 → 28,13)."""
    from decimal import Decimal, ROUND_HALF_UP
    q = (Decimal(x) if isinstance(x, int) else Decimal(repr(float(x)))).quantize(Decimal(1).scaleb(-dec), rounding=ROUND_HALF_UP)
    s = f"{q:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=2):
    return fmt(100 * x, dec) + " %"


def signo(x):
    """Δ con signo, como en las tablas: −4, 0, +3."""
    if x < 0:
        return "−" + fmt(-x)
    return ("+" if x > 0 else "") + fmt(x)


# ---------------------------------------------------------------- datos (originales)

# Ejemplo resuelto · la panadería reparte a seis almacenes. Posición en km sobre el mapa; la
# distancia es la línea recta redondeada al km.
EJ_NODOS = ["P", "A", "B", "C", "D", "E", "F"]
EJ_POS = {"P": (14, 7), "A": (5, 10), "B": (11, 8), "C": (9, 2), "D": (9, 0), "E": (14, 0), "F": (7, 5)}

# 11.1 y 11.3 · cinco ciudades (km)
E1 = [[0, 8, 14, 9, 12],
      [8, 0, 7, 13, 10],
      [14, 7, 0, 6, 12],
      [9, 13, 6, 0, 5],
      [12, 10, 12, 5, 0]]

# 11.2 · gap y tamaño
E2 = {"ruta": 212, "cota": 196, "optimo_real": 203, "exige": 0.05, "clientes": [12, 20], "por_segundo": 1_000_000}

# 11.4 · pedidos de la semana (miles de pesos y horas)
E4 = {"margen": [12, 9, 7, 22], "horas": [4, 3, 2, 6], "cap": 9, "inicio": (1, 1, 0, 0)}

# 11.5 y 11.7 · técnico con base en 1 y cinco clientes (posición en km)
E5_POS = {1: (5, 3), 2: (2, 9), 3: (2, 6), 4: (1, 2), 5: (6, 5), 6: (2, 0)}

# 11.8 · cinco pedidos de una imprenta (días)
E8 = {"p": [4, 8, 9, 6, 6], "d": [29, 14, 16, 7, 6], "w": [4, 1, 2, 5, 2]}

# 11.10 · distribuidora de bidones: bodega 0 y cinco clientes (posición en km, demanda en cajas)
E10_POS = {0: (6, 5), 1: (2, 3), 2: (1, 6), 3: (4, 0), 4: (2, 9), 5: (10, 7)}
E10_DEM = {1: 5, 2: 7, 3: 6, 4: 6, 5: 5}
E10_CAP = 18


# ---------------------------------------------------------------- herramientas de rutas

def matriz_de(pos):
    return {a: {b: round(math.dist(pos[a], pos[b])) for b in pos} for a in pos}


def matriz_lista(M):
    """E1 viene como lista; se pasa a diccionario con ciudades 1..n."""
    n = len(M)
    return {i + 1: {j + 1: M[i][j] for j in range(n)} for i in range(n)}


def largo(r, D):
    return sum(D[a][b] for a, b in zip(r, r[1:]))


def vecino(D, inicio, orden=None):
    """Vecino más cercano. A igual distancia gana la que va primero en `orden`."""
    orden = orden or sorted(D)
    r = [inicio]; pend = [n for n in orden if n != inicio]; traza = []
    while pend:
        cand = sorted(pend, key=lambda n: (D[r[-1]][n], orden.index(n)))
        traza.append((r[-1], [(n, D[r[-1]][n]) for n in cand], cand[0]))
        r.append(cand[0]); pend.remove(cand[0])
    traza.append((r[-1], [(inicio, D[r[-1]][inicio])], inicio))
    return r + [inicio], traza


def rotar(r, base):
    c = r[:-1]; k = c.index(base)
    return c[k:] + c[:k] + [base]


def movs_2opt(r, completa=False):
    """Pares (i, j) de 2-opt: se invierte el tramo r[i..j]. Sin completa, se omite la inversión de
    toda la ruta (es la misma ruta al revés)."""
    n = len(r) - 1
    return [(i, j) for i in range(1, n - 1) for j in range(i + 1, n) if completa or not (i == 1 and j == n - 1)]


def aplicar_2opt(r, i, j):
    return r[:i] + r[i:j + 1][::-1] + r[j + 1:]


def delta_2opt(r, i, j, D):
    a, b, c, d = r[i - 1], r[i], r[j], r[j + 1]
    return D[a][c] + D[b][d] - D[a][b] - D[c][d]


def dos_opt(r, D, estrategia="mejor"):
    """Búsqueda local 2-opt. Devuelve la ruta final y una lista de iteraciones con todos los Δ."""
    iters = []; evals = 0
    while True:
        movs = movs_2opt(r); deltas = []
        elegido = None
        for (i, j) in movs:
            dlt = delta_2opt(r, i, j, D); evals += 1
            assert dlt == largo(aplicar_2opt(r, i, j), D) - largo(r, D)
            deltas.append(((i, j), dlt))
            if estrategia == "primer" and dlt < 0:
                elegido = (i, j); break
        if estrategia == "mejor":
            mejor = min(d for _, d in deltas)
            if mejor < 0:
                cuales = [m for m, d in deltas if d == mejor]
                assert len(cuales) == 1, ("empate en 2-opt", cuales)
                elegido = cuales[0]
        iters.append({"ruta": r, "km": largo(r, D), "deltas": deltas, "elegido": elegido})
        if elegido is None:
            return r, iters, evals
        r = aplicar_2opt(r, *elegido)


def intercambio(r, D):
    """Búsqueda local de intercambio (swap) de dos clientes, mejor mejora."""
    iters = []
    while True:
        deltas = []
        for i in range(1, len(r) - 1):
            for j in range(i + 1, len(r) - 1):
                n = r[:]; n[i], n[j] = n[j], n[i]
                deltas.append(((r[i], r[j]), largo(n, D) - largo(r, D), n))
        mejor = min(d for _, d, _ in deltas)
        el = [x for x in deltas if x[1] == mejor]
        iters.append({"ruta": r, "km": largo(r, D), "deltas": deltas, "elegido": el[0] if mejor < 0 else None})
        if mejor >= 0:
            return r, iters
        assert len(el) == 1
        r = el[0][2]


def exacto(D, base):
    otros = [n for n in D if n != base]
    todas = sorted((largo([base] + list(p) + [base], D), [base] + list(p) + [base]) for p in permutations(otros))
    return todas[0][0], todas[0][1], todas


def insercion(D, inicial):
    """Inserción más barata desde el subtour inicial (lista cerrada)."""
    sub = list(inicial); pend = [n for n in sorted(D) if n not in sub]; traza = []
    while pend:
        cand = []
        for k in pend:
            for p in range(len(sub) - 1):
                i, j = sub[p], sub[p + 1]
                cand.append((D[i][k] + D[k][j] - D[i][j], k, p, i, j))
        cand.sort(key=lambda c: (c[0], c[1], c[2]))
        # un empate entre dos ciudades distintas cambiaría el resultado: no se acepta
        assert not (len(cand) > 1 and cand[0][0] == cand[1][0] and cand[0][1] != cand[1][1]), cand[:3]
        c, k, p, i, j = cand[0]
        mejores = {}
        for x in cand:
            mejores.setdefault(x[1], x)
        traza.append((list(sub), sorted(mejores.values(), key=lambda x: x[1]), (k, i, j, c)))
        sub.insert(p + 1, k); pend.remove(k)
    return sub, traza


# ---------------------------------------------------------------- modelo exacto del vendedor viajero

def tsp_milp(D, base):
    """Modelo MTZ: x[i][j] binaria, u[i] entera. Segundo camino para el óptimo del ejemplo."""
    N = list(D); n = len(N); arcos = [(i, j) for i in N for j in N if i != j]
    ix = {a: k for k, a in enumerate(arcos)}; otros = [i for i in N if i != base]
    iu = {i: len(arcos) + k for k, i in enumerate(otros)}; nv = len(arcos) + len(otros)
    c = np.zeros(nv)
    for (i, j), k in ix.items():
        c[k] = D[i][j]
    A, lo, hi = [], [], []
    for j in N:
        f = np.zeros(nv)
        for i in N:
            if i != j: f[ix[(i, j)]] = 1
        A.append(f); lo.append(1); hi.append(1)
    for i in N:
        f = np.zeros(nv)
        for j in N:
            if i != j: f[ix[(i, j)]] = 1
        A.append(f); lo.append(1); hi.append(1)
    for i in otros:
        for j in otros:
            if i != j:
                f = np.zeros(nv); f[iu[i]] = 1; f[iu[j]] = -1; f[ix[(i, j)]] = n
                A.append(f); lo.append(-np.inf); hi.append(n - 1)
    lb = np.zeros(nv); ub = np.ones(nv)
    for i in otros:
        lb[iu[i]] = 1; ub[iu[i]] = n - 1
    res = milp(c, constraints=LinearConstraint(np.array(A), lo, hi), integrality=np.ones(nv), bounds=Bounds(lb, ub))
    assert res.success
    sig = {i: j for (i, j), k in ix.items() if res.x[k] > 0.5}
    r = [base]
    while len(r) <= n:
        r.append(sig[r[-1]])
    return round(res.fun), r


def escribir_modelo_opl(D, base):
    dat = MODELOS / "u11_reparto_exacto.dat"
    N = list(D)
    filas = ",\n".join("  [" + ", ".join(f"{D[i][j]:>2}" for j in N) + "]" for i in N)
    texto = ("/* Unidad 11 · Ejemplo resuelto · la panadería y sus seis almacenes (km, línea recta redondeada) */\n"
             f"Nodos = {{{', '.join(chr(34) + n + chr(34) for n in N)}}};\n"
             f"Base  = \"{base}\";\n"
             f"d = [\n{filas}\n];\n")
    dat.write_text(texto, encoding="utf-8")
    return dat


# ---------------------------------------------------------------- 11.4 · mochila con vecindario de complemento

def mochila_local(E):
    m, h, cap = E["margen"], E["horas"], E["cap"]
    val = lambda x: sum(a * b for a, b in zip(m, x))
    hor = lambda x: sum(a * b for a, b in zip(h, x))
    x = tuple(E["inicio"]); pasos = []
    while True:
        vec = []
        for j in range(len(m)):
            y = list(x); y[j] = 1 - y[j]; y = tuple(y)
            vec.append((j + 1, y, val(y), hor(y), hor(y) <= cap))
        mejora = [v for v in vec if v[4] and v[2] > val(x)]
        pasos.append((x, val(x), hor(x), vec))
        if not mejora:
            break
        x = max(mejora, key=lambda v: v[2])[1]
    todas = [(val(y), y) for y in __import__("itertools").product((0, 1), repeat=len(m)) if hor(y) <= cap]
    opt = max(todas)
    assert sum(1 for t in todas if t[0] == opt[0]) == 1
    return {"local": x, "z_local": val(x), "pasos": pasos, "opt": opt[1], "z_opt": opt[0], "h_opt": hor(opt[1]),
            "factibles": len(todas), "hamming": sum(a != b for a, b in zip(x, opt[1]))}


# ---------------------------------------------------------------- 11.8 · secuencias

def atraso(seq, E):
    t = 0; s = 0; filas = []
    for j in seq:
        t += E["p"][j]; a = max(0, t - E["d"][j]); s += E["w"][j] * a; filas.append((j + 1, t, a, E["w"][j] * a))
    return s, filas


def secuencias(E):
    n = len(E["p"])
    edd = sorted(range(n), key=lambda j: E["d"][j])
    seq = edd[:]; pasos = []
    while True:
        z = atraso(seq, E)[0]; vec = []
        for k in range(n - 1):
            s2 = seq[:]; s2[k], s2[k + 1] = s2[k + 1], s2[k]; vec.append((atraso(s2, E)[0], k, s2))
        b = min(vec)
        assert sum(1 for v in vec if v[0] == b[0]) == 1 or b[0] >= z
        pasos.append((seq, z, vec))
        if b[0] >= z:
            break
        seq = b[2]
    todas = sorted((atraso(list(p), E)[0], list(p)) for p in permutations(range(n)))
    assert todas[0][0] < todas[1][0]
    return {"edd": edd, "z_edd": atraso(edd, E)[0], "pasos": pasos, "local": seq, "z_local": atraso(seq, E)[0],
            "opt": todas[0][1], "z_opt": todas[0][0], "filas_edd": atraso(edd, E)[1], "filas_opt": atraso(todas[0][1], E)[1]}


# ---------------------------------------------------------------- 11.10 · ahorros de Clarke y Wright

def ahorros(D, dem, cap):
    cl = sorted(dem)
    lista = sorted(((D[0][i] + D[0][j] - D[i][j], i, j) for i, j in combinations(cl, 2)), key=lambda s: (-s[0], s[1], s[2]))
    rutas = [[i] for i in cl]; traza = []
    for s, i, j in lista:
        if s < 0:
            traza.append((s, i, j, "ahorro negativo: no conviene unir")); continue
        ri = next(r for r in rutas if i in r); rj = next(r for r in rutas if j in r)
        if ri is rj:
            traza.append((s, i, j, "ya están en la misma ruta")); continue
        if sum(dem[k] for k in ri + rj) > cap:
            traza.append((s, i, j, f"no: suman {sum(dem[k] for k in ri + rj)} cajas")); continue
        if ri[-1] == i and rj[0] == j: nueva = ri + rj
        elif ri[0] == i and rj[-1] == j: nueva = rj + ri
        elif ri[-1] == i and rj[-1] == j: nueva = ri + rj[::-1]
        elif ri[0] == i and rj[0] == j: nueva = ri[::-1] + rj
        else:
            traza.append((s, i, j, "no: un cliente queda al medio")); continue
        rutas.remove(ri); rutas.remove(rj); rutas.append(nueva)
        traza.append((s, i, j, "se unen"))
    km = lambda r: D[0][r[0]] + sum(D[a][b] for a, b in zip(r, r[1:])) + D[r[-1]][0]
    total = sum(km(r) for r in rutas)
    # exacto: todas las particiones factibles, cada grupo con su mejor recorrido
    def particiones(s):
        if not s:
            yield []; return
        f = s[0]
        for k in range(len(s)):
            for comb in combinations(s[1:], k):
                g = [f] + list(comb); resto = [x for x in s[1:] if x not in comb]
                for pp in particiones(resto):
                    yield [g] + pp
    def mejor_recorrido(g):
        return min((km(list(p)), list(p)) for p in permutations(g))
    mejor = None
    for pp in particiones(cl):
        if all(sum(dem[k] for k in g) <= cap for g in pp):
            v = sum(mejor_recorrido(g)[0] for g in pp)
            if mejor is None or v < mejor[0]:
                mejor = (v, [mejor_recorrido(g)[1] for g in pp])
    sin_unir = sum(2 * D[0][i] for i in cl)
    return {"lista": lista, "traza": traza, "rutas": rutas, "km": total, "km_rutas": [km(r) for r in rutas],
            "opt": mejor[0], "rutas_opt": mejor[1], "km_rutas_opt": [km(r) for r in mejor[1]], "sin_unir": sin_unir}


# ---------------------------------------------------------------- caso integrador

def caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_red.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def matriz_caso(m):
    D = dict(nx.all_pairs_dijkstra_path_length(m.grafo(), weight="km"))
    N = ["Taller"] + m.TIENDAS
    return {a: {b: D[a][b] for b in N} for a in N}, N


def es_local_2opt(r, D):
    return all(delta_2opt(r, i, j, D) >= 0 for (i, j) in movs_2opt(r))


# ---------------------------------------------------------------- cálculo de todo

def resultados():
    R = {}
    # ejemplo
    D = matriz_de(EJ_POS)
    z, r_opt, todas = exacto(D, "P")
    v, traza = vecino(D, "P", EJ_NODOS)
    f, iters, ev = dos_opt(v, D, "mejor")
    fp, iters_p, evp = dos_opt(v, D, "primer")
    z_milp, r_milp = tsp_milp(D, "P")
    assert z_milp == z
    R["ej"] = {"D": D, "z": z, "r_opt": r_opt, "rutas": len(todas) // 2, "vmc": v, "km_vmc": largo(v, D),
               "traza": traza, "final": f, "km_final": largo(f, D), "iters": iters, "evals": ev,
               "primer": fp, "km_primer": largo(fp, D), "iters_p": iters_p, "evals_p": evp,
               "gap_vmc": (largo(v, D) - z) / z, "gap_final": (largo(f, D) - z) / z,
               "segunda": sorted(set(t[0] for t in todas))[1], "milp": z_milp,
               "n_movs": len(movs_2opt(v)), "ahorro": largo(v, D) - largo(f, D)}
    # crecimiento del número de rutas
    R["crece"] = {n: math.factorial(n - 1) // 2 for n in (5, 7, 10, 15, 20, 30)}
    # 11.1
    D1 = matriz_lista(E1)
    z1, r1, _ = exacto(D1, 1)
    e = {"z": z1, "r_opt": r1}
    for s in (1, 4):
        r, t = vecino(D1, s)
        e[s] = {"ruta": r, "km": largo(r, D1), "traza": t, "gap": (largo(r, D1) - z1) / z1}
    R["e1"] = e
    # 11.2
    g = E2
    R["e2"] = {"gap_cota": (g["ruta"] - g["cota"]) / g["cota"], "gap_real": (g["ruta"] - g["optimo_real"]) / g["optimo_real"],
               "gap_cplex": (g["ruta"] - g["cota"]) / g["ruta"],
               "rutas": {n: math.factorial(n - 1) // 2 for n in g["clientes"]}}
    R["e2"]["segundos"] = {n: R["e2"]["rutas"][n] / g["por_segundo"] for n in g["clientes"]}
    R["e2"]["anos20"] = R["e2"]["segundos"][20] / (3600 * 24 * 365)
    # 11.3
    s3, t3 = insercion(D1, [1, 2, 1])
    R["e3"] = {"ruta": s3, "km": largo(s3, D1), "traza": t3, "z": z1, "gap": (largo(s3, D1) - z1) / z1}
    # 11.4
    R["e4"] = mochila_local(E4)
    # 11.5 y 11.7
    D5 = matriz_de(E5_POS)
    r0 = [1, 2, 3, 4, 5, 6, 1]
    f5, it5, _ = dos_opt(r0, D5)
    z5, ro5, _ = exacto(D5, 1)
    fs, its = intercambio(r0, D5)
    f57, it57, _ = dos_opt(fs, D5)
    assert largo(f5, D5) == z5 and largo(fs, D5) > z5 and largo(f57, D5) == z5
    R["e5"] = {"D": D5, "r0": r0, "km0": largo(r0, D5), "final": f5, "km": largo(f5, D5), "iters": it5, "z": z5}
    R["e7"] = {"final": fs, "km": largo(fs, D5), "iters": its, "dos_opt": f57, "km_2opt": largo(f57, D5), "iters_2opt": it57,
               "gap": (largo(fs, D5) - z5) / z5, "n_swap": len(its[0]["deltas"])}
    # 11.8
    R["e8"] = secuencias(E8)
    # 11.9 · multiarranque sobre el caso (se hace en caso_u11)
    # 11.10
    D10 = matriz_de(E10_POS)
    R["e10"] = ahorros(D10, E10_DEM, E10_CAP)
    R["e10"]["D"] = D10
    R["e10"]["gap"] = (R["e10"]["km"] - R["e10"]["opt"]) / R["e10"]["opt"]
    # caso
    R["caso"] = caso_u11()
    return R


def caso_u11():
    m = caso(); D, N = matriz_caso(m)
    v, traza = vecino(D, "Taller", ["Taller"] + sorted(m.TIENDAS))
    f, iters, _ = dos_opt(v, D)
    z, r_opt, todas = exacto(D, "Taller")
    filas = [((i, j), v[i - 1], v[i], v[j], v[j + 1], delta_2opt(v, i, j, D)) for (i, j) in movs_2opt(v, completa=True)]
    locales = sorted({t[0] for t in todas if es_local_2opt(t[1], D)})
    n_loc = sum(1 for t in todas if es_local_2opt(t[1], D)) // 2
    # el movimiento de tres tramos que sí llega al óptimo: sacar (Lagos, Valle, Cerro) e insertarlo al revés entre Centro y Puerto
    seg = v[4:7]; resto = v[:4] + v[7:]
    k = resto.index("Centro")
    tres = resto[:k + 1] + seg[::-1] + resto[k + 1:]
    sale = [(v[3], v[4]), (v[6], v[7]), (v[1], v[2])]
    entra = [(v[3], v[7]), (v[1], v[6]), (v[4], v[2])]
    d_tres = sum(D[a][b] for a, b in entra) - sum(D[a][b] for a, b in sale)
    assert largo(tres, D) == z and d_tres == z - largo(v, D)
    # 11.9 · multiarranque: vecino más cercano desde cada nodo (empate: orden alfabético), rotado al Taller, y 2-opt
    multi = []
    for s in ["Taller"] + sorted(m.TIENDAS):
        r, _ = vecino(D, s, sorted(N))
        rr = rotar(r, "Taller")
        ff, _, _ = dos_opt(rr, D)
        multi.append((s, rr, largo(rr, D), ff, largo(ff, D)))
    # intercambio desde el vecino: tampoco mejora
    fsw, itsw = intercambio(v, D)
    return {"D": D, "N": N, "vmc": v, "km_vmc": largo(v, D), "traza": traza, "final": f, "km_final": largo(f, D),
            "z": z, "r_opt": r_opt, "gap": (largo(v, D) - z) / z, "filas": filas, "locales": locales, "n_loc": n_loc,
            "rutas": len(todas) // 2, "tres": tres, "sale": sale, "entra": entra, "d_tres": d_tres, "multi": multi,
            "swap_km": largo(fsw, D), "swap_min": min(d for _, d, _ in itsw[0]["deltas"])}


# ---------------------------------------------------------------- tablas en Markdown

def flecha(r):
    return " → ".join(str(x) for x in r)


def tabla_matriz(D, N, rotulos=None):
    rot = rotulos or {n: str(n) for n in N}
    t = "| km | " + " | ".join(rot[n] for n in N) + " |\n|---|" + "---|" * len(N) + "\n"
    for a in N:
        t += f"| **{rot[a]}** | " + " | ".join("–" if a == b else str(D[a][b]) for b in N) + " |\n"
    return t


def tabla_vecino(traza, rot=None):
    rot = rot or (lambda x: str(x))
    t = "| Paso | Desde | Pendientes (km) | Va a | Tramo |\n|---|---|---|---|---|\n"
    for k, (desde, cand, el) in enumerate(traza, 1):
        c = ", ".join(f"{rot(n)} {d}" for n, d in cand)
        paso = str(k) if k < len(traza) else "cierre"
        t += f"| {paso} | {rot(desde)} | {c} | {rot(el)} | {cand[0][1]} |\n"
    return t


def tabla_2opt_iters(iters):
    cab = " | ".join(f"Iteración {k} ({it['km']} km)" for k, it in enumerate(iters, 1))
    t = f"| Movimiento (i, j) | {cab} |\n|---|" + "---|" * len(iters) + "\n"
    for idx, (mov, _) in enumerate(iters[0]["deltas"]):
        celdas = []
        for it in iters:
            m2, d = it["deltas"][idx]
            assert m2 == mov
            s = signo(d)
            celdas.append(f"**{s}**" if it["elegido"] == mov else s)
        t += f"| ({mov[0]}, {mov[1]}) | " + " | ".join(celdas) + " |\n"
    return t


def tablas(R):
    T = {}
    e = R["ej"]
    T["ej_matriz"] = tabla_matriz(e["D"], EJ_NODOS)
    T["ej_vecino"] = tabla_vecino(e["traza"])
    T["ej_2opt"] = tabla_2opt_iters(e["iters"])
    # primer mejor
    t = "| Iteración | Ruta al empezar | km | Movimientos revisados | Elige | Δ |\n|---|---|---|---|---|---|\n"
    for k, it in enumerate(e["iters_p"], 1):
        el = it["elegido"]
        d = dict(it["deltas"])[el] if el else None
        t += f"| {k} | {flecha(it['ruta'])} | {it['km']} | {len(it['deltas'])} | {f'({el[0]}, {el[1]})' if el else 'ninguno: óptimo local'} | {signo(d) if el else '–'} |\n"
    T["e6"] = t
    # crecimiento
    t = "| Almacenes además de la base | Rutas distintas $(n-1)!/2$ |\n|---|---|\n"
    for n, c in R["crece"].items():
        t += f"| {n - 1} | {fmt(c) if c < 10**12 else sci(c)} |\n"
    T["crece"] = t
    # 11.1
    T["e1_matriz"] = tabla_matriz(matriz_lista(E1), [1, 2, 3, 4, 5])
    t = "| Pedido | 1 | 2 | 3 | 4 | 5 |\n|---|---|---|---|---|---|\n"
    t += "| Días de trabajo $p_j$ | " + " | ".join(str(x) for x in E8["p"]) + " |\n"
    t += "| Entrega comprometida (día) $d_j$ | " + " | ".join(str(x) for x in E8["d"]) + " |\n"
    t += "| Multa por día de atraso $w_j$ | " + " | ".join(str(x) for x in E8["w"]) + " |\n"
    T["e8_datos"] = t
    t = "| Cliente | " + " | ".join(str(k) for k in E10_DEM) + " |\n|---|" + "---|" * len(E10_DEM) + "\n"
    t += "| Cajas | " + " | ".join(str(v) for v in E10_DEM.values()) + " |\n"
    T["e10_dem"] = t
    for s in (1, 4):
        T[f"e1_{s}"] = tabla_vecino(R["e1"][s]["traza"])
    # 11.3
    t = "| Subtour | Mejor inserción de cada ciudad pendiente $c_{ik}+c_{kj}-c_{ij}$ | Se inserta |\n|---|---|---|\n"
    for sub, mej, (k, i, j, c) in R["e3"]["traza"]:
        celdas = "; ".join(f"{kk} entre {ii} y {jj}: {cc}" for cc, kk, p, ii, jj in mej)
        t += f"| {flecha(sub)} | {celdas} | {k} entre {i} y {j} (+{c}) |\n"
    T["e3"] = t
    # 11.4
    t = "| Solución | Margen | Horas | Vecinos (cambia $x_j$): margen, horas | Se mueve a |\n|---|---|---|---|---|\n"
    pasos = R["e4"]["pasos"]
    for k, (x, val, hor, vec) in enumerate(pasos):
        vv = "; ".join(f"$x_{j}$: {v2}, {h2} h{'' if ok else ' (no cabe)'}" for j, y, v2, h2, ok in vec)
        sig = pasos[k + 1][0] if k + 1 < len(pasos) else None
        t += f"| {tupla(x)} | {val} | {hor} | {vv} | {tupla(sig) if sig else 'nadie mejora: óptimo local'} |\n"
    T["e4"] = t
    # 11.5
    T["e5_matriz"] = tabla_matriz(R["e5"]["D"], list(E5_POS))
    T["e5"] = tabla_2opt_iters(R["e5"]["iters"])
    # 11.7
    t = "| Intercambio | " + " | ".join(f"Iteración {k} ({it['km']} km)" for k, it in enumerate(R["e7"]["iters"], 1)) + " |\n|---|" + "---|" * len(R["e7"]["iters"]) + "\n"
    n_filas = len(R["e7"]["iters"][0]["deltas"])
    for idx in range(n_filas):
        celdas = []
        for it in R["e7"]["iters"]:
            par, d, _ = it["deltas"][idx]
            s = signo(d)
            celdas.append(f"**{s}**" if it["elegido"] and it["elegido"][0] == par else s)
        par0 = idx_par(R["e7"]["iters"][0]["ruta"], idx)
        t += f"| posiciones {par0} | " + " | ".join(celdas) + " |\n"
    T["e7"] = t
    # 11.8
    t = "| Secuencia | Atraso ponderado | Vecinos (intercambia posiciones k y k+1) | Se mueve a |\n|---|---|---|---|\n"
    P8 = R["e8"]["pasos"]
    for k, (seq, z, vec) in enumerate(P8):
        vv = "; ".join(f"{q + 1}-{q + 2}: {zz}" for zz, q, _ in vec)
        sig = P8[k + 1][0] if k + 1 < len(P8) else None
        t += f"| {'-'.join(str(j + 1) for j in seq)} | {z} | {vv} | {'-'.join(str(j + 1) for j in sig) if sig else 'nadie mejora: óptimo local'} |\n"
    T["e8"] = t
    t = "| Pedido | Termina el día | Atraso (días) | Multa ponderada |\n|---|---|---|---|\n"
    for j, tt, a, wa in R["e8"]["filas_opt"]:
        t += f"| {j} | {tt} | {a} | {wa} |\n"
    T["e8_opt"] = t
    # 11.9
    c = R["caso"]
    t = "| Arranca en | Ruta del vecino, rotada al Taller | km | Después de 2-opt (km) |\n|---|---|---|---|\n"
    for s, rr, km, ff, kmf in c["multi"]:
        t += f"| {s} | {flecha(rr)} | {km} | {kmf} |\n"
    T["e9"] = t
    # 11.10
    e10 = R["e10"]
    T["e10_matriz"] = tabla_matriz(e10["D"], list(E10_POS))
    t = "| Par | Ahorro $s_{ij}=d_{0i}+d_{0j}-d_{ij}$ | Qué pasa |\n|---|---|---|\n"
    for s, i, j, q in e10["traza"]:
        t += f"| {i}-{j} | {signo(s).lstrip('+')} | {q} |\n"
    T["e10"] = t
    # caso
    T["caso_matriz"] = tabla_matriz(c["D"], c["N"])
    T["caso_vecino"] = tabla_vecino(c["traza"])
    t = "| Movimiento (i, j) | Salen | Entran | Δ (km) |\n|---|---|---|---|\n"
    for (i, j), a, b, cc, d, dl in c["filas"]:
        nota = " (es la misma ruta al revés)" if (i, j) == (1, len(c["vmc"]) - 2) else ""
        t += f"| ({i}, {j}){nota} | {a}–{b} y {cc}–{d} | {a}–{cc} y {b}–{d} | {signo(dl)} |\n"
    T["caso_2opt"] = t
    return T


def idx_par(r, idx):
    pares = [(i, j) for i in range(1, len(r) - 1) for j in range(i + 1, len(r) - 1)]
    return f"{pares[idx][0]} y {pares[idx][1]}"


def tupla(x):
    return "(" + ", ".join(str(a) for a in x) + ")"


def sci(n):
    e = int(math.floor(math.log10(n))); m = n / 10**e
    return "$" + fmt(m, 2).replace(",", "{,}") + " \\cdot 10^{" + str(e) + "}$"


# ---------------------------------------------------------------- cifras que el texto debe tener

def esperados(R):
    e, c = R["ej"], R["caso"]
    s = []
    s += [f"{e['km_vmc']} km", f"{e['km_final']} km", pct(e["gap_vmc"]), f"{e['rutas']} rutas", f"{e['n_movs']} movimientos",
          flecha(e["vmc"]), flecha(e["final"]), flecha(e["iters"][1]["ruta"]), f"{e['iters'][1]['km']} km",
          f"{e['evals']} evaluaciones", f"{e['segunda']} km", f"{e['ahorro']} km"]
    s += [fmt(v) for v in R["crece"].values() if v < 10**12]
    # caso
    s += [f"{c['km_vmc']} km", f"{c['z']} km", pct(c["gap"]), flecha(c["vmc"]), flecha(c["r_opt"]),
          f"{c['rutas']} rutas", f"{c['n_loc']} de las {c['rutas']}", signo(c["d_tres"]), flecha(c["tres"]),
          f"{c['swap_km']} km"]
    # 11.1
    e1 = R["e1"]
    s += [f"{e1[1]['km']} km", f"{e1[4]['km']} km", pct(e1[4]["gap"]), flecha(e1[1]["ruta"]), flecha(e1[4]["ruta"]), f"{e1['z']} km"]
    # 11.2
    e2 = R["e2"]
    s += [pct(e2["gap_cota"]), pct(e2["gap_real"]), pct(e2["gap_cplex"]), fmt(e2["rutas"][12]), fmt(e2["rutas"][20]),
          fmt(e2["segundos"][12], 1) + " segundos", fmt(e2["anos20"]) + " años"]
    # 11.3
    s += [flecha(R["e3"]["ruta"]), f"{R['e3']['km']} km", pct(R["e3"]["gap"])]
    # 11.4
    e4 = R["e4"]
    s += [tupla(e4["local"]), tupla(e4["opt"]), f"{e4['z_opt']} mil", f"{e4['z_local']} mil", f"{e4['factibles']} soluciones factibles"]
    # 11.5 y 11.7
    e5, e7 = R["e5"], R["e7"]
    s += [f"{e5['km0']} km", f"{e5['km']} km", flecha(e5["final"]), flecha(e5["iters"][1]["ruta"]), f"{e5['iters'][1]['km']} km",
          flecha(e7["final"]), f"{e7['km']} km", pct(e7["gap"]), f"{e7['n_swap']} intercambios"]
    # 11.6
    s += [f"{e['evals_p']} evaluaciones", flecha(e["primer"]), f"{e['km_primer']} km"]
    # 11.8
    e8 = R["e8"]
    s += ["-".join(str(j + 1) for j in e8["edd"]), "-".join(str(j + 1) for j in e8["local"]), "-".join(str(j + 1) for j in e8["opt"]),
          f"atraso ponderado de {e8['z_edd']}", f"{e8['z_local']}", f"{e8['z_opt']}", pct((e8["z_local"] - e8["z_opt"]) / e8["z_opt"])]
    s += [fmt((c["km_vmc"] - c["z"]) * 250) + " km al año"]
    # 11.9
    llegan = sum(1 for m in c["multi"] if m[4] == c["z"])
    s += [f"{llegan} de los {len(c['multi'])} arranques"]
    # 11.10
    e10 = R["e10"]
    s += [f"{e10['km']} km", f"{e10['opt']} km", pct(e10["gap"]), f"{e10['sin_unir']} km"]
    s += [" y ".join(flecha([0] + r + [0]) for r in e10["rutas"])]
    s += [" y ".join(flecha([0] + r + [0]) for r in e10["rutas_opt"])]
    return s


# ---------------------------------------------------------------- figuras

TINTA, SUAVE, LINEA, ACENTO = "#2B2F33", "#5F656B", "#C9C5BF", "#E2622A"
AZUL, VERDE = "#1F5F8B", "#2E7D4F"
FUENTE = "Segoe UI, Roboto, Arial, sans-serif"


def svg(ancho, alto, partes, titulo):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}" '
            f'role="img" aria-label="{titulo}"><title>{titulo}</title>'
            f'<rect width="{ancho}" height="{alto}" fill="#FFFFFF"/>' + "".join(partes) + "</svg>\n")


def texto(x, y, t, color=TINTA, tam=12, ancla="middle", peso="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FUENTE}" font-size="{tam}" fill="{color}" text-anchor="{ancla}" '
            f'font-weight="{peso}" stroke="#FFFFFF" stroke-width="3.5" paint-order="stroke" stroke-linejoin="round">{t}</text>')


def panel_ruta(pos, ruta, D, ox, oy, esc, titulo, color, resaltar=(), base=None, ymax=None):
    ymax = ymax if ymax is not None else max(p[1] for p in pos.values())
    P = {n: (ox + x * esc, oy + (ymax - y) * esc) for n, (x, y) in pos.items()}
    partes = [texto(ox + 7 * esc, oy - 32, titulo, TINTA, 13, "middle", "600")]
    for a, b in zip(ruta, ruta[1:]):
        (x1, y1), (x2, y2) = P[a], P[b]
        es = (a, b) in resaltar or (b, a) in resaltar
        g = ' stroke-dasharray="7 4"' if es else ""
        partes.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ACENTO if es else color}" stroke-width="{3 if es else 2.2}"{g}/>')
        partes.append(texto((x1 + x2) / 2, (y1 + y2) / 2 + 4, str(D[a][b]), ACENTO if es else SUAVE, 11))
    for n, (x, y) in P.items():
        b = n == base
        partes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{9 if b else 7}" fill="{ACENTO if b else TINTA}" stroke="#FFFFFF" stroke-width="1.5"/>')
        partes.append(texto(x + 11, y - 7, str(n), TINTA, 12, "start", "600"))
    return partes


def fig_ejemplo(R):
    e = R["ej"]; partes = []
    rutas = [(e["vmc"], f"Vecino más cercano · {e['km_vmc']} km"),
             (e["iters"][1]["ruta"], f"Tras el primer 2-opt · {e['iters'][1]['km']} km"),
             (e["final"], f"Tras el segundo 2-opt · {e['km_final']} km")]
    sale = []
    for k, it in enumerate(e["iters"][:-1]):
        i, j = it["elegido"]; r = it["ruta"]
        sale.append({(r[i - 1], r[i]), (r[j], r[j + 1])})
    for k, (r, tit) in enumerate(rutas):
        res = sale[k] if k < len(sale) else ()
        partes += panel_ruta(EJ_POS, r, e["D"], 30 + k * 235, 62, 14.5, tit, AZUL, res, "P", ymax=10)
    partes.append(texto(370, 252, "En naranja punteado, los dos tramos que el siguiente movimiento 2-opt saca de la ruta.", SUAVE, 11))
    return svg(740, 266, partes, "La ruta de la panadería: vecino más cercano y dos movimientos 2-opt")


CASO_POS = {"Costa": (0, 8), "Puerto": (4, 9), "Lagos": (9, 8), "Centro": (3, 5), "Taller": (0, 3),
            "Cruce": (5, 3.5), "Valle": (9, 4), "Cerro": (8, 0.5)}


def fig_caso(R):
    m = caso(); c = R["caso"]; partes = []
    for k, (r, tit, res) in enumerate([(c["vmc"], f"Vecino más cercano y 2-opt · {c['km_vmc']} km", c["sale"]),
                                       (c["tres"], f"Óptimo · {c['z']} km", c["entra"])]):
        ox, oy, esc = 40 + k * 360, 72, 33
        P = {n: (ox + x * esc, oy + (9 - y) * esc) for n, (x, y) in CASO_POS.items()}
        for (a, b), d in m.CAMINOS.items():
            (x1, y1), (x2, y2) = P[a], P[b]
            partes.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#E4E1DC" stroke-width="5" stroke-linecap="round"/>')
        pos_paradas = {n: CASO_POS[n] for n in c["N"]}
        sub = panel_ruta(pos_paradas, r, c["D"], ox, oy, esc, tit, AZUL if k == 0 else VERDE, res, "Taller", ymax=9)
        sub[0] = texto(ox + 4.5 * esc, oy - 34, tit, TINTA, 13, "middle", "600")
        partes += sub
        x, y = P["Cruce"]
        partes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#FFFFFF" stroke="{SUAVE}" stroke-width="1.5"/>')
        partes.append(texto(x, y + 18, "Cruce", SUAVE, 11))
    partes.append(texto(385, 404, "Gris: los caminos de la red. Cada tramo de la ruta va por el camino más corto (su largo es el número).", SUAVE, 11))
    partes.append(texto(385, 420, "En naranja punteado, los tres tramos que cambian: 2-opt solo cambia dos a la vez.", SUAVE, 11))
    return svg(770, 432, partes, "Estampa Sur: la ruta atrapada en 84 km y la óptima de 78 km")


def dibujar(R):
    FIGURAS.mkdir(parents=True, exist_ok=True)
    figs = {"u11_panaderia.svg": fig_ejemplo(R), "u11_estampa_sur.svg": fig_caso(R)}
    for n, s in figs.items():
        (FIGURAS / n).write_text(s, encoding="utf-8")
    print("   figuras:", ", ".join(figs))


# ---------------------------------------------------------------- OPL, cadena y revisión

def comparar_con_opl(R):
    escribir_modelo_opl(R["ej"]["D"], "P")
    r = correr(MODELOS / "u11_reparto_exacto.mod", MODELOS / "u11_reparto_exacto.dat")
    if r is None:
        print("OPL: oplrun no está instalado; el óptimo se comprueba con fuerza bruta y milp")
        return None
    assert r["codigo"] == 0 and r["objetivo"] is not None, r["salida"][-500:]
    assert abs(r["objetivo"] - R["ej"]["z"]) < 1e-6, (r["objetivo"], R["ej"]["z"])
    arcos = {k for k, v in r["valores"].items() if k.startswith("arco_") and v == 1}
    r_opt = R["ej"]["r_opt"]
    pares = {f"arco_{a}_{b}" for a, b in zip(r_opt, r_opt[1:])} | {f"arco_{b}_{a}" for a, b in zip(r_opt, r_opt[1:])}
    assert len(arcos) == len(r_opt) - 1 and arcos <= pares, arcos
    print(f"OPL: el modelo exacto da {fmt(r['objetivo'])} km, igual que la fuerza bruta y milp")
    return True


def cadena(R):
    C = caso().calcular()["u11"]; c = R["caso"]
    ok = C["vecino_km"] == c["km_vmc"] and C["vecino_ruta"] == c["vmc"] and C["dos_opt_km"] == c["km_final"]
    ok &= C["dos_opt_ruta"] == c["final"] and abs(C["gap_vecino"] - c["gap"]) < 1e-12 and c["z"] == 78
    ok &= caso().calcular()["u4"]["tsp_km"] == c["z"]
    print("CADENA:", "OK, vecino 84 km, 2-opt 84 km, óptimo 78 km y gap 7,69 % calzan con el caso" if ok else "NO calza")
    return ok


def imprimir(R):
    e, c = R["ej"], R["caso"]
    print("== ejemplo: vecino", flecha(e["vmc"]), e["km_vmc"], "· 2-opt", flecha(e["final"]), e["km_final"],
          "· óptimo", e["z"], "· gap vecino", pct(e["gap_vmc"]), "· primer mejor", e["km_primer"], e["evals_p"], "evals vs", e["evals"])
    print("== 11.1", {s: (R["e1"][s]["km"], pct(R["e1"][s]["gap"])) for s in (1, 4)}, "óptimo", R["e1"]["z"])
    print("== 11.2", {k: v for k, v in R["e2"].items()})
    print("== 11.3", flecha(R["e3"]["ruta"]), R["e3"]["km"])
    print("== 11.4 local", R["e4"]["local"], R["e4"]["z_local"], "óptimo", R["e4"]["opt"], R["e4"]["z_opt"])
    print("== 11.5", R["e5"]["km0"], "→", R["e5"]["km"], "óptimo", R["e5"]["z"], "· 11.7 swap", R["e7"]["km"], "→ 2-opt", R["e7"]["km_2opt"])
    print("== 11.8 EDD", R["e8"]["z_edd"], "local", R["e8"]["z_local"], "óptimo", R["e8"]["z_opt"], R["e8"]["opt"])
    print("== 11.9", [(m[0], m[2], m[4]) for m in c["multi"]])
    print("== 11.10 ahorros", R["e10"]["rutas"], R["e10"]["km"], "óptimo", R["e10"]["rutas_opt"], R["e10"]["opt"])
    print("== caso: vecino", c["km_vmc"], "2-opt", c["km_final"], "óptimo", c["z"], "gap", pct(c["gap"]), "óptimos locales 2-opt", c["locales"], c["n_loc"])


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
        mod = (MODELOS / "u11_reparto_exacto.mod").read_text(encoding="utf-8")
        faltan += [f"OPL: {l.strip()}" for l in mod.splitlines() if l.strip() and not l.strip().startswith(("/*", "*")) and l.rstrip() not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
