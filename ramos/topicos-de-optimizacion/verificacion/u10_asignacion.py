"""Unidad 10 · Asignación y método húngaro. Recalcula todas las cifras; con --revisar las busca en el .md.

Este script:

1. implementa el método húngaro paso a paso (reducción por filas y columnas, mínimo de líneas por el
   marcado de König, ajuste) y genera sus tablas en Markdown;
2. lleva la cota inferior que acumula el método y exige que termine igual al óptimo;
3. compara cada asignación con la fuerza bruta (todas las permutaciones) y con scipy (milp);
4. si hay CPLEX (oplrun), corre `modelos/u10_asignacion.mod` con cada `.dat` y exige el mismo
   objetivo y la misma asignación;
5. compara la pieza del caso integrador con el script del caso (`CADENA: OK`);
6. con --revisar, busca cada cifra, cada línea de las tablas generadas y el código OPL en el .md.

    python u10_asignacion.py            # imprime los resultados
    python u10_asignacion.py --revisar  # además los busca en el .md
"""
from itertools import permutations
from pathlib import Path
import importlib.util, re, sys, unicodedata

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
MD = RAMO / "unidades" / "10-asignacion.md"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402

TINTA, SUAVE, ACENTO, LINEA = "#2B2F33", "#5F656B", "#E2622A", "#D6D3CE"
M = 999   # costo de un par prohibido en el método a mano (gran M); en las tablas se muestra «M»


def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------- datos (originales; pasados por colisiones.py)
def caso_mod():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_red.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def datos_caso():
    A = caso_mod().ASIGNACION
    filas = list(A); cols = list(next(iter(A.values())))
    return {"filas": filas, "cols": cols, "C": [[A[f][c] for c in cols] for f in filas]}


EJ = {"filas": ["Rocío", "Matías", "Javiera", "Tomás", "Ignacia"], "cols": ["P1", "P2", "P3", "P4", "P5"],
      "C": [[24, 18, 21, 47, 49], [29, 61, 53, 30, 46], [50, 30, 64, 26, 44], [59, 42, 25, 43, 44],
            [31, 18, 35, 55, 37]]}
E01 = {"filas": ["Garzón 1", "Garzón 2", "Garzón 3"], "cols": ["Terraza", "Salón", "Barra"],
       "C": [[33, 48, 36], [20, 59, 41], [38, 44, 24]]}
E02 = {"filas": ["A", "B", "C", "D"], "cols": ["T1", "T2", "T3", "T4"],
       "C": [[14, 14, 18, 30], [32, 19, 12, 31], [23, 23, 31, 26], [16, 30, 27, 38]]}
E03 = {"filas": ["Grúa 1", "Grúa 2", "Grúa 3", "Grúa 4"], "cols": ["Obra 1", "Obra 2", "Obra 3", "Obra 4"],
       "C": [[77, 70, 90, 65], [42, 73, 90, 54], [86, 60, 68, 35], [56, 33, 36, 36]]}
E05 = {"filas": ["Amanda", "Beto", "Carla", "Dante", "Elisa"], "cols": ["J1", "J2", "J3", "J4", "J5"],
       "C": [[48, 97, 68, 61, 82], [86, 84, 73, 77, 48], [77, 42, 99, 41, 70], [98, 62, 84, 59, 42],
             [41, 78, 80, 44, 70]]}
E06 = {"filas": ["Pía", "Raúl", "Sara"], "cols": ["Inventario", "Caja", "Bodega", "Vitrinas"],
       "C": [[57, 65, 52, 47], [28, 38, 27, 62], [48, 67, 36, 64]]}
E07 = {"filas": ["V1", "V2", "V3", "V4"], "cols": ["Norte", "Centro", "Sur", "Costa"],
       "G": [[57, 127, 67, 197], [77, 167, 57, 177], [207, 117, 67, 77], [137, 197, 117, 197]]}
E08 = {"filas": ["Turno 1", "Turno 2", "Turno 3", "Turno 4"], "cols": ["Lavado", "Secado", "Planchado", "Doblado"],
       "C": [[45, None, 21, 17], [18, 32, 31, 35], [20, 37, 32, None], [41, 22, 23, 18]]}
E09 = {"filas": ["Hugo", "Inés", "Julio"], "cols": ["K1", "K2", "K3", "K4", "K5"], "tope": 2,
       "C": [[20, 50, 27, 45, 29], [22, 28, 27, 54, 34], [28, 29, 22, 23, 28]]}
E10 = {"nodos": ["A", "B", "C", "D", "E"],
       "D": [[0, 30, 13, 26, 7], [30, 0, 11, 9, 17], [13, 11, 0, 21, 13], [26, 9, 21, 0, 18], [7, 17, 13, 18, 0]]}


# ---------------------------------------------------------------- método húngaro
def emparejar(Z):
    """Máximo número de ceros independientes (caminos de aumento, en orden fijo)."""
    n = len(Z); col = [None] * n

    def aumentar(i, vis):
        for j in range(n):
            if Z[i][j] and j not in vis:
                vis.add(j)
                if col[j] is None or aumentar(col[j], vis):
                    col[j] = i
                    return True
        return False
    for i in range(n):
        aumentar(i, set())
    return {col[j]: j for j in range(n) if col[j] is not None}


def cubrir(Z, asig):
    """Marcado: (1) filas sin asignación; (2) columnas con un cero en una fila marcada; (3) filas con
    su asignación en una columna marcada; repetir. Líneas = filas NO marcadas + columnas marcadas."""
    n = len(Z); fil = {i for i in range(n) if i not in asig}; col = set()
    inv = {j: i for i, j in asig.items()}
    cambio = True
    while cambio:
        cambio = False
        for i in sorted(fil):
            for j in range(n):
                if Z[i][j] and j not in col:
                    col.add(j); cambio = True
                    if j in inv:
                        fil.add(inv[j])
    return sorted(set(range(n)) - fil), sorted(col)


def hungaro(C):
    n = len(C); A = [f[:] for f in C]; pasos = []
    mf = [min(f) for f in A]; A = [[x - mf[i] for x in f] for i, f in enumerate(A)]
    pasos.append({"tipo": "filas", "resta": mf, "A": [f[:] for f in A]})
    mc = [min(A[i][j] for i in range(n)) for j in range(n)]
    A = [[A[i][j] - mc[j] for j in range(n)] for i in range(n)]
    cota = sum(mf) + sum(mc)
    pasos.append({"tipo": "columnas", "resta": mc, "A": [f[:] for f in A], "cota": cota})
    while True:
        Z = [[A[i][j] == 0 for j in range(n)] for i in range(n)]
        asig = emparejar(Z)
        if len(asig) == n:
            pasos[-1]["lineas"] = None
            return asig, pasos, cota
        filas, cols = cubrir(Z, asig)
        assert len(filas) + len(cols) == len(asig)                     # König: líneas = ceros independientes
        assert all(not Z[i][j] or i in filas or j in cols for i in range(n) for j in range(n))
        d = min(A[i][j] for i in range(n) for j in range(n) if i not in filas and j not in cols)
        pasos[-1]["lineas"] = (filas, cols); pasos[-1]["delta"] = d
        for i in range(n):
            for j in range(n):
                if i not in filas and j not in cols:
                    A[i][j] -= d
                elif i in filas and j in cols:
                    A[i][j] += d
        cota += d * (n - len(filas) - len(cols))
        pasos.append({"tipo": "ajuste", "delta": d, "A": [f[:] for f in A], "cota": cota})


def fuerza(C):
    n = len(C)
    mejor = min(sum(C[i][p[i]] for i in range(n)) for p in permutations(range(n)))
    optimos = [p for p in permutations(range(n)) if sum(C[i][p[i]] for i in range(n)) == mejor]
    return mejor, optimos


def milp_asig(C, filas_max=None, filas_min=None, cols_igual=True):
    """Asignación con milp: cada fila entre filas_min y filas_max tareas; cada columna exactamente 1
    (o a lo más 1)."""
    m, n = len(C), len(C[0])
    c = np.array([C[i][j] for i in range(m) for j in range(n)], float)
    Af = np.array([[1 if k // n == i else 0 for k in range(m * n)] for i in range(m)], float)
    Ac = np.array([[1 if k % n == j else 0 for k in range(m * n)] for j in range(n)], float)
    fmax = filas_max or [1] * m; fmin = filas_min or [1] * m
    r = milp(c, constraints=[LinearConstraint(Af, lb=fmin, ub=fmax),
                             LinearConstraint(Ac, lb=[1 if cols_igual else 0] * n, ub=[1] * n)],
             integrality=np.ones(m * n), bounds=Bounds(0, 1))
    return float(r.fun), {(k // n, k % n) for k in range(m * n) if r.x[k] > 0.5}


def resolver(filas, cols, C):
    asig, pasos, cota = hungaro(C)
    total = sum(C[i][j] for i, j in asig.items())
    fb, optimos = fuerza(C)
    assert total == fb == cota, (total, fb, cota)
    return {"filas": filas, "cols": cols, "C": C, "asig": asig, "pasos": pasos, "total": total,
            "n_opt": len(optimos), "ajustes": sum(1 for p in pasos if p["tipo"] == "ajuste")}


def resultados():
    R = {}
    dc = datos_caso()
    R["caso"] = resolver(dc["filas"], dc["cols"], dc["C"])
    assert R["caso"]["n_opt"] == 1
    z, par = milp_asig(dc["C"]); assert abs(z - R["caso"]["total"]) < 1e-6
    for k, D in [("ej", EJ), ("e01", E01), ("e02", E02), ("e03", E03), ("e05", E05)]:
        R[k] = resolver(D["filas"], D["cols"], D["C"])
        assert R[k]["n_opt"] == 1
        z, _ = milp_asig(D["C"]); assert abs(z - R[k]["total"]) < 1e-6
    assert R["e02"]["ajustes"] == 0 and R["e03"]["ajustes"] == 1 and R["e05"]["ajustes"] == 2
    R["e01"]["todas"] = [(p, sum(E01["C"][i][p[i]] for i in range(3))) for p in permutations(range(3))]
    # 10.6: tres personas, cuatro tareas: fila ficticia de costo 0
    C6 = [f[:] for f in E06["C"]] + [[0] * 4]
    R["e06"] = resolver(E06["filas"] + ["Ficticio"], E06["cols"], C6)
    z, _ = milp_asig(E06["C"], cols_igual=False); assert abs(z - R["e06"]["total"]) < 1e-6
    R["e06"]["sin_hacer"] = E06["cols"][R["e06"]["asig"][3]]
    # 10.7: maximizar → costo de oportunidad = máximo − valor
    G = E07["G"]; mx = max(map(max, G))
    C7 = [[mx - g for g in f] for f in G]
    R["e07"] = resolver(E07["filas"], E07["cols"], C7)
    R["e07"]["max"] = mx
    R["e07"]["valor"] = sum(G[i][j] for i, j in R["e07"]["asig"].items())
    assert R["e07"]["valor"] == 4 * mx - R["e07"]["total"]
    z, _ = milp_asig([[-g for g in f] for f in G]); assert abs(-z - R["e07"]["valor"]) < 1e-6
    R["e07"]["codicioso"] = codicioso(G)
    # 10.8: prohibiciones con M
    C8 = [[M if x is None else x for x in f] for f in E08["C"]]
    R["e08"] = resolver(E08["filas"], E08["cols"], C8)
    assert R["e08"]["total"] < M
    libre = [[0 if x is None else x for x in f] for f in E08["C"]]
    R["e08"]["sin_prohibir"] = resolver(E08["filas"], E08["cols"], libre)
    R["e08"]["usa_prohibido"] = [(i, j) for i, j in R["e08"]["sin_prohibir"]["asig"].items() if E08["C"][i][j] is None]
    # 10.9: cada persona hasta 2 tareas → filas duplicadas y una columna ficticia
    C9 = [f[:] + [0] for f in E09["C"] for _ in range(2)]
    R["e09"] = resolver([f"{n} ({k})" for n in E09["filas"] for k in (1, 2)], E09["cols"] + ["Ficticio"], C9)
    z, _ = milp_asig(E09["C"], filas_max=[2] * 3, filas_min=[0] * 3); assert abs(z - R["e09"]["total"]) < 1e-6
    reales = {}
    for i, j in R["e09"]["asig"].items():
        if j < 5:
            reales.setdefault(E09["filas"][i // 2], []).append(E09["cols"][j])
    R["e09"]["reales"] = reales
    # 10.10: asignación como relajación del vendedor viajero
    D = E10["D"]; n = len(D)
    C10 = [[M if i == j else D[i][j] for j in range(n)] for i in range(n)]
    R["e10"] = resolver(E10["nodos"], E10["nodos"], C10)
    vis, ciclos = set(), []
    for s in range(n):
        if s in vis:
            continue
        c, x = [s], R["e10"]["asig"][s]; vis.add(s)
        while x != s:
            c.append(x); vis.add(x); x = R["e10"]["asig"][x]
        ciclos.append(c)
    R["e10"]["ciclos"] = ciclos
    tours = [(sum(D[r[k]][r[(k + 1) % n]] for k in range(n)), r) for r in [(0,) + p for p in permutations(range(1, n))]]
    R["e10"]["tsp"], R["e10"]["ruta"] = min(tours)
    R["e10"]["gap"] = (R["e10"]["tsp"] - R["e10"]["total"]) / R["e10"]["tsp"]
    import networkx as nx                                   # segundo camino del vendedor viajero
    Gx = nx.complete_graph(n)
    for i in range(n):
        for j in range(i + 1, n):
            Gx[i][j]["weight"] = D[i][j]
    assert len(ciclos) == 2 and R["e10"]["total"] < R["e10"]["tsp"]
    assert R["e10"]["tsp"] == min(sum(D[r[k]][r[(k + 1) % n]] for k in range(n)) for r in [(0,) + p for p in permutations(range(1, n))])
    return R


def codicioso(G):
    """Para 10.7: cada vendedor, en orden, toma la zona libre que más le rinde."""
    libres, total, plan = set(range(len(G))), 0, {}
    for i, f in enumerate(G):
        j = max(sorted(libres), key=lambda jj: f[jj]); plan[i] = j; total += f[j]; libres.remove(j)
    return total, plan


# ---------------------------------------------------------------- tablas en Markdown
def celda(x):
    return "M" if x >= M / 2 else fmt(x)


def tabla(filas, cols, A, extra=None, lineas=None, asig=None, extra_fila=None):
    """extra: (rótulo, valores por fila); lineas: (filas, cols) cubiertas; asig: ceros elegidos en negrita."""
    fl, cl = (lineas or ([], []))
    cab = [c + (" ▼" if j in cl else "") for j, c in enumerate(cols)]
    s = ["| | " + " | ".join(cab) + (f" | {extra[0]} |" if extra else (" | |" if lineas else " |")),
         "|---" * (len(cols) + (2 if (extra or lineas) else 1)) + "|"]
    for i, f in enumerate(A):
        cel = [f"**{celda(x)}**" if asig and asig.get(i) == j else celda(x) for j, x in enumerate(f)]
        fin = f" | {celda(extra[1][i])} |" if extra else (" | ◀ |" if lineas and i in fl else (" | |" if lineas else " |"))
        s.append(f"| {filas[i]} | " + " | ".join(cel) + fin)
    if extra_fila:
        s.append(f"| {extra_fila[0]} | " + " | ".join(celda(x) for x in extra_fila[1]) + (" | |" if (extra or lineas) else " |"))
    return "\n".join(s)


def frase_lineas(X, p):
    n = len(X["C"])
    if p.get("lineas") is None:
        return None
    fl, cl = p["lineas"]
    partes = ([("fila " if len(fl) == 1 else "filas ") + ", ".join(X["filas"][i] for i in fl)] if fl else []) + \
             ([("columna " if len(cl) == 1 else "columnas ") + ", ".join(X["cols"][j] for j in cl)] if cl else [])
    k = len(fl) + len(cl)
    return (f"Los ceros se cubren con {k} líneas ({' y '.join(partes)}): {k} < {n}, todavía no hay "
            f"{n} ceros independientes. El menor número sin cubrir es **{fmt(p['delta'])}**: se resta a "
            f"los no cubiertos y se suma en los cruces.")


def bloque(X):
    n = len(X["C"]); P = X["pasos"]; trozos = []
    trozos += ["*Matriz y mínimo de cada fila.*",
               tabla(X["filas"], X["cols"], X["C"], extra=("mín. fila", P[0]["resta"]))]
    trozos += ["*Reducción por filas y mínimo de cada columna.*",
               tabla(X["filas"], X["cols"], P[0]["A"], extra_fila=("mín. col.", P[1]["resta"]))]
    for k, p in enumerate(P[1:], 1):
        rot = "*Reducción por columnas" if p["tipo"] == "columnas" else f"*Ajuste {k - 1}"
        if p.get("lineas") is not None:
            trozos += [rot + f" (cota {fmt(p['cota'])}), con las líneas que cubren los ceros.*",
                       tabla(X["filas"], X["cols"], p["A"], lineas=p["lineas"]), frase_lineas(X, p)]
        else:
            trozos += [rot + f" (cota {fmt(p['cota'])}): hay {n} ceros independientes (en negrita).*",
                       tabla(X["filas"], X["cols"], p["A"], asig=X["asig"])]
    asig = "; ".join(f"{X['filas'][i]} → {X['cols'][j]} ({celda(X['C'][i][j])})" for i, j in sorted(X["asig"].items()))
    trozos.append(f"Asignación: {asig}. Total: **{fmt(X['total'])}**.")
    return "\n\n".join(trozos)


def tablas(R):
    T = {}
    for k in ["caso", "ej", "e01", "e02", "e03", "e05", "e06", "e07", "e08", "e09", "e10"]:
        X = R[k]
        T[f"{k}_datos"] = tabla(X["filas"], X["cols"], X["C"])
        T[f"{k}_hungaro"] = bloque(X)
    T["e07_g"] = tabla(E07["filas"], E07["cols"], E07["G"])
    T["e08_dato"] = tabla(E08["filas"], E08["cols"], [[M if x is None else x for x in f] for f in E08["C"]])
    T["e09_dato"] = tabla(E09["filas"], E09["cols"], E09["C"])
    T["e06_dato"] = tabla(E06["filas"], E06["cols"], E06["C"])
    T["e10_dato"] = tabla(E10["nodos"], E10["nodos"], [[M if i == j else x for j, x in enumerate(f)] for i, f in enumerate(E10["D"])])
    X = R["e01"]
    s = ["| Garzón 1 | Garzón 2 | Garzón 3 | Minutos |", "|---|---|---|---|"]
    for p, v in X["todas"]:
        s.append("| " + " | ".join(E01["cols"][p[i]] for i in range(3)) + f" | {fmt(v)} |")
    T["e01_todas"] = "\n".join(s)
    return T


USADAS = {"caso_datos", "caso_hungaro", "ej_datos", "ej_hungaro", "e01_datos", "e01_todas", "e02_datos",
          "e02_hungaro", "e03_datos", "e03_hungaro", "e05_datos", "e05_hungaro", "e06_dato", "e06_hungaro",
          "e07_g", "e07_hungaro", "e08_dato", "e08_hungaro", "e09_dato", "e09_hungaro", "e10_dato", "e10_hungaro"}


# ---------------------------------------------------------------- OPL
MODELOS_U10 = {"caso": "u10_estampa.dat", "ej": "u10_repartos.dat", "e05": "u10_e05_cinco.dat",
               "e06": "u10_e06_tres_personas.dat", "e08": "u10_e08_prohibidos.dat", "e09": "u10_e09_dos_tareas.dat"}
SALIDA_CASO = []


def sin_tilde(s):
    """Los .dat de OPL van sin tildes (Tomas, termica); se comparan sin ellas."""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def comparar_con_opl(R):
    corridos = 0
    for k, dat in MODELOS_U10.items():
        r = correr(MODELOS / "u10_asignacion.mod", MODELOS / dat)
        if r is None:
            print("OPL: oplrun no está instalado; se comparan solo las cifras de Python")
            return None
        assert r["codigo"] == 0 and r["objetivo"] is not None, (k, r["salida"][-400:])
        assert abs(r["objetivo"] - R[k]["total"]) < 1e-6, (k, r["objetivo"], R[k]["total"])
        X = R[k]
        if k == "e09":
            esperado = {f"x[{p}][{t}]" for p, ts in X["reales"].items() for t in ts}
        else:
            esperado = {f"x[{X['filas'][i]}][{X['cols'][j]}]" for i, j in X["asig"].items() if X["filas"][i] != "Ficticio"}
        obtenido = {c for c, v in r["valores"].items() if c.startswith("x[") and v == 1}
        esperado = {sin_tilde(c) for c in esperado}
        assert obtenido == esperado, (k, obtenido, esperado)
        if k == "caso":
            SALIDA_CASO[:] = [l.strip() for l in r["salida"].splitlines() if re.match(r"^[\w\[\] áéíóú]+ = \S+$", l.strip())]
        corridos += 1
    print(f"OPL: {corridos} modelos corridos con oplrun; objetivo y asignación coinciden con el húngaro")
    return True


# ---------------------------------------------------------------- figura
def figura(R):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "path"})
    X = R["caso"]; n = len(X["filas"])
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    y = [3 - k for k in range(n)]
    for i in range(n):
        for j in range(n):
            el = X["asig"][i] == j
            ax.plot([1.0, 3.6], [y[i], y[j]], color=ACENTO if el else LINEA, lw=2.4 if el else 0.7,
                    ls="-" if el else ":", zorder=2 if el else 1)
            if el:
                ax.text(2.3, (y[i] + y[j]) / 2 + 0.08, f"{X['C'][i][j]} min", ha="center", fontsize=8.5,
                        color=TINTA, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"), zorder=3)
    for i, nom in enumerate(X["filas"]):
        ax.text(0.95, y[i], nom, ha="right", va="center", fontsize=9.5, color=TINTA,
                bbox=dict(boxstyle="round,pad=0.3", fc="#F2F1EF", ec=SUAVE))
    for j, nom in enumerate(X["cols"]):
        ax.text(3.65, y[j], nom, ha="left", va="center", fontsize=9.5, color=TINTA,
                bbox=dict(boxstyle="round,pad=0.3", fc="#F2F1EF", ec=SUAVE))
    ax.set_xlim(-0.3, 5.0); ax.set_ylim(-0.5, 3.5); ax.axis("off")
    fig.tight_layout()
    carpeta = RAMO / "unidades" / "figuras"; carpeta.mkdir(parents=True, exist_ok=True)
    fig.savefig(carpeta / "u10_asignacion_caso.svg", metadata={"Date": None})
    plt.close(fig)


# ---------------------------------------------------------------- revisión
def esperados(R):
    s = []
    X = R["caso"]; s += [f"{fmt(X['total'])} minutos", f"{X['ajustes']} ajustes"]
    s += [fmt(p["cota"]) for p in X["pasos"][1:]]
    for k in ["ej", "e01", "e02", "e03", "e05", "e06", "e08", "e09", "e10"]:
        s.append(fmt(R[k]["total"]))
    s += [f"{fmt(R['ej']['total'])} minutos", R["e06"]["sin_hacer"], fmt(R["e07"]["valor"]), fmt(R["e07"]["max"]),
          fmt(R["e10"]["tsp"]), f"{round(100 * R['e10']['gap'])} %"]
    s += [f"{p}: {', '.join(ts)}" for p, ts in R["e09"]["reales"].items()]
    X = R["e08"]["sin_prohibir"]; s.append(fmt(X["total"]))
    # cifras derivadas que el texto comenta
    P = R["ej"]["pasos"]
    s += [f"Lo restado por filas ({fmt(sum(P[0]['resta']))}) y por columnas ({fmt(sum(P[1]['resta']))}) suma {fmt(P[1]['cota'])}"]
    G = E07["G"]; mx = R["e07"]["max"]
    s += [rf"$4 \cdot {mx} - {R['e07']['total']} = {R['e07']['valor']}$"]
    s += [f"cuestan {fmt(R['e08']['total'] - R['e08']['sin_prohibir']['total'])} minutos"]
    s += [f"La cota pasó de {fmt(R['caso']['pasos'][1]['cota'])}", f"sube la cota de {fmt(R['e03']['pasos'][1]['cota'])} a {fmt(R['e03']['total'])}"]
    C = R["caso"]["C"]; assert (C[3][2] - C[0][2], C[3][0] - C[0][0]) == (2, 8)
    return s


def codigo_en_md(md):
    faltan = []
    for f in ["u10_asignacion.mod", "u10_estampa.dat"]:
        for linea in (MODELOS / f).read_text(encoding="utf-8").splitlines():
            if linea.strip() and linea.rstrip() not in md:
                faltan.append(f"{f}: {linea.strip()}")
    return faltan


def cadena(R):
    C = caso_mod().calcular()["u10"]
    X = R["caso"]
    asig = {X["filas"][i]: X["cols"][j] for i, j in X["asig"].items()}
    ok = C["minutos"] == X["total"] and C["asignacion"] == asig
    print("CADENA:", f"OK, {X['total']} minutos y la misma asignación que el script del caso" if ok else "NO calza")
    return ok


if __name__ == "__main__":
    R = resultados()
    for k, X in R.items():
        print(f"== {k}: total {X['total']} · ajustes {X['ajustes']} · óptimos {X['n_opt']} · "
              + "; ".join(f"{X['filas'][i]}→{X['cols'][j]}" for i, j in sorted(X["asig"].items())))
    print("e06 sin hacer:", R["e06"]["sin_hacer"], "· e07 valor:", R["e07"]["valor"], "codicioso:", R["e07"]["codicioso"])
    print("e08 sin prohibir:", R["e08"]["sin_prohibir"]["total"], R["e08"]["usa_prohibido"])
    print("e09:", R["e09"]["reales"], "· e10:", R["e10"]["ciclos"], R["e10"]["tsp"], R["e10"]["ruta"], R["e10"]["gap"])
    if not cadena(R):
        sys.exit(1)
    figura(R)
    comparar_con_opl(R)
    if "--tablas" in sys.argv:
        for k, t in tablas(R).items():
            print(f"\n### {k}\n{t}")
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md_n]
        T = tablas(R)
        for k in sorted(USADAS):
            for linea in T[k].splitlines():
                if linea.strip() and linea not in md:
                    faltan.append(f"tabla {k}: {linea[:70]}")
        faltan += codigo_en_md(md)
        lineas_md = set(l.strip() for l in md.splitlines())
        faltan += [f"salida OPL: {l}" for l in SALIDA_CASO if l not in lineas_md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
