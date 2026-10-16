"""Unidad 8 · Forma estándar y método simplex. Recalcula todas las cifras; con --revisar las busca en el .md.

Las tablas del simplex salen de una implementación propia, con fracciones exactas (fractions.Fraction),
y se comprueban contra scipy (HiGHS). Con --tablas imprime todas las tablas en Markdown, tal como van
en la unidad; con --figura regenera unidades/figuras/u08_camino_simplex.svg.

    python u08_simplex.py            # imprime los resultados
    python u08_simplex.py --tablas   # imprime las tablas en Markdown
    python u08_simplex.py --revisar  # busca cifras y tablas en el .md
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import importlib.util, sys

import numpy as np
from scipy.optimize import linprog

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent


# ---------------------------------------------------------------- formato
def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fr(x):
    """Fracción exacta a texto: 1.380 · −98/3 · 1/30."""
    x = F(x)
    signo = "−" if x < 0 else ""
    x = abs(x)
    if x.denominator == 1:
        return signo + fmt(x.numerator)
    return f"{signo}{fmt(x.numerator)}/{fmt(x.denominator)}"


def dec(x, d=2):
    return fmt(float(x), d)


# ---------------------------------------------------------------- simplex en tabla
class Tabla:
    def __init__(self, T, z, base, nombres):
        self.T, self.z, self.base, self.nombres = T, z, base, nombres


def simplex(c, A, b, nombres=None, pivotes=None):
    """Máximo de c·x con A x <= b, b >= 0, desde la base de holguras.

    Regla: entra la de costo reducido más positivo; sale la de razón mínima (con empate, la de más
    arriba). `pivotes` fuerza una lista de (entra, sale) para mostrar un paso equivocado.
    Devuelve la lista de tablas y, por tabla, la variable que entra, la fila que sale y las razones."""
    m, n = len(A), len(c)
    nombres = nombres or [f"x{j + 1}" for j in range(n)] + [f"s{i + 1}" for i in range(m)]
    T = [[F(v) for v in A[i]] + [F(int(i == k)) for k in range(m)] + [F(b[i])] for i in range(m)]
    z = [F(v) for v in c] + [F(0)] * m + [F(0)]
    base = [n + i for i in range(m)]
    pasos = []
    k = 0
    while True:
        tab = Tabla([r[:] for r in T], z[:], base[:], nombres)
        if pivotes is not None:
            if k >= len(pivotes):
                pasos.append((tab, None, None, None)); break
            e, s = pivotes[k]
        else:
            cand = [j for j in range(n + m) if z[j] > 0]
            if not cand:
                pasos.append((tab, None, None, None)); break
            e = max(cand, key=lambda j: (z[j], -j))
            s = None
        razones = [T[i][-1] / T[i][e] if T[i][e] > 0 else None for i in range(m)]
        if s is None:
            validas = [(r, i) for i, r in enumerate(razones) if r is not None]
            if not validas:
                raise ValueError("no acotado")
            s = min(validas)[1]
        pasos.append((tab, e, s, razones))
        p = T[s][e]
        T[s] = [v / p for v in T[s]]
        for i in range(m):
            if i != s and T[i][e] != 0:
                f = T[i][e]
                T[i] = [a - f * bb for a, bb in zip(T[i], T[s])]
        f = z[e]
        z = [a - f * bb for a, bb in zip(z, T[s])]
        base[s] = e
        k += 1
    return pasos


def tabla_md(paso, k):
    """Una tabla en Markdown; si no es la final, marca el pivote y agrega la razón mínima."""
    tab, e, s, razones = paso
    cab = ["Base"] + tab.nombres + ["LD"] + (["Razón"] if e is not None else [])
    filas = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    for i, r in enumerate(tab.T):
        celdas = [fr(v) for v in r]
        if e is not None and i == s:
            celdas[e] = f"**{celdas[e]}**"
        fila = [tab.nombres[tab.base[i]]] + celdas
        if e is not None:
            rz = razones[i]
            fila.append("—" if rz is None else f"{fr(r[-1])} ÷ {fr(r[e])} = {fr(rz)}")
        filas.append("| " + " | ".join(fila) + " |")
    ult = ["−z"] + [fr(v) for v in tab.z]
    if e is not None:
        ult.append("")
    filas.append("| " + " | ".join(ult) + " |")
    return "\n".join(filas)


def lectura(pasos, n):
    """Solución, objetivo, precios sombra (−fila objetivo bajo las holguras) y costos reducidos."""
    tab = pasos[-1][0]
    m = len(tab.T)
    x = [F(0)] * (n + m)
    for i, j in enumerate(tab.base):
        x[j] = tab.T[i][-1]
    return {"x": x, "z": -tab.z[-1], "duales": [-tab.z[n + i] for i in range(m)],
            "rc": tab.z[:n + m], "Binv": [[tab.T[i][n + k] for k in range(m)] for i in range(m)],
            "base": [tab.nombres[j] for j in tab.base], "iter": len(pasos) - 1}


def con_scipy(c, A, b, cotas=None):
    r = linprog([-v for v in c], A_ub=A, b_ub=b, bounds=cotas or [(0, None)] * len(c), method="highs")
    assert r.status == 0
    return -r.fun, list(r.x), list(-r.ineqlin.marginals)


def comprobar(c, A, b, L):
    z, x, y = con_scipy(c, A, b)
    n = len(c)
    assert abs(float(L["z"]) - z) < 1e-6
    assert all(abs(float(L["x"][j]) - x[j]) < 1e-6 for j in range(n))
    assert all(abs(float(L["duales"][i]) - y[i]) < 1e-6 for i in range(len(b)))
    # dualidad: el objetivo es igual a b·y
    assert sum(F(bi) * yi for bi, yi in zip(b, L["duales"])) == L["z"]


# ---------------------------------------------------------------- datos (originales)
EJEMPLO = {"c": [8, 6, 5], "A": [[2, 1, 2], [1, 2, 1]], "b": [18, 15]}      # miles de pesos, horas
E83 = {"c": [4, 2, 5], "A": [[1, 1, 2], [2, 1, 1], [1, 3, 1]], "b": [12, 14, 15]}
E84 = {"c": [6, 5, 4], "A": [[1, 1, 1], [2, 1, 3], [1, 2, 1]], "b": [10, 18, 14]}
E85 = {"c": [5, 4], "A": [[1, 1], [3, 1], [0, 1]], "b": [9, 21, 7]}
E86 = {"c": [7, 6, 5], "A": [[2, 1, 1], [1, 2, 1], [0, 1, 2]], "b": [16, 14, 10]}
E89 = {"c": [3, 1], "A": [[1, 1], [1, -1]], "b": [4, 8]}                     # x2 libre
E810 = {"c": [34, 36, 42], "A": [[2, 4, 3], [3, 2, 4]], "b": [200, 180]}    # miles de pesos, horas
E82 = {"A": [[1, 2, 1, 0], [3, 1, 0, 1]], "b": [8, 9]}
E81 = {"c": [4, -3, -2], "A_ge": [2, -1, 1], "b_ge": 5, "A_le": [1, 3, 0], "b_le": 12,
       "A_eq": [1, -1, 2], "b_eq": -4}   # mín; x1 >= 0, x2 <= 0, x3 libre


def caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_lp.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def datos_caso():
    d = caso().DOS
    return {"c": d["margen"], "A": [d["est"], d["pla"], [0, 1]], "b": [d["cap_est"], d["cap_pla"], d["dem_polerones"]]}


# ---------------------------------------------------------------- resultados
def resultados():
    R = {}
    for k, d, nom in [("ejemplo", EJEMPLO, None), ("e83", E83, None), ("e84", E84, None), ("e85", E85, None),
                      ("e86", E86, None), ("e810", E810, None), ("caso", datos_caso(), ["x1", "x2", "s1", "s2", "s3"])]:
        pasos = simplex(d["c"], d["A"], d["b"], nom)
        L = lectura(pasos, len(d["c"]))
        comprobar(d["c"], d["A"], d["b"], L)
        R[k] = {"pasos": pasos, "L": L, "d": d}
    # 8.3: solo una iteración se pide; la tabla siguiente no es óptima
    assert R["e83"]["pasos"][1][1] is not None
    # 8.5: vértices que visita el simplex
    R["e85"]["camino"] = [tuple(lectura([p], 2)["x"][:2]) for p in R["e85"]["pasos"]]
    R["caso"]["camino"] = [tuple(lectura([p], 2)["x"][:2]) for p in R["caso"]["pasos"]]
    R["caso"]["z_camino"] = [-p[0].z[-1] for p in R["caso"]["pasos"]]
    # 8.7: simplex matricial con dos bases del problema de 8.3
    R["e87"] = {nombre: matricial(E83, base) for nombre, base in [("a", [2, 4, 5]), ("b", [0, 2, 5])]}
    # 8.8: el paso equivocado (sale s1 en vez de s2) deja un lado derecho negativo
    malo = simplex(E85["c"], E85["A"], E85["b"], pivotes=[(0, 0)])
    R["e88"] = {"pasos": malo, "ld": [r[-1] for r in malo[-1][0].T]}
    assert min(R["e88"]["ld"]) < 0
    # 8.9: variable libre x2 = x2' − x2''
    d = E89
    pasos = simplex([d["c"][0], d["c"][1], -d["c"][1]], [[a[0], a[1], -a[1]] for a in d["A"]], d["b"],
                    ["x1", "x2'", "x2''", "s1", "s2"])
    L = lectura(pasos, 3)
    r = linprog([-v for v in d["c"]], A_ub=d["A"], b_ub=d["b"], bounds=[(0, None), (None, None)], method="highs")
    assert abs(-r.fun - float(L["z"])) < 1e-9 and abs(r.x[1] - float(L["x"][1] - L["x"][2])) < 1e-9
    for p in pasos:   # x2' y x2'' nunca son básicas a la vez
        assert not ({1, 2} <= set(p[0].base))
    R["e89"] = {"pasos": pasos, "L": L, "x2": L["x"][1] - L["x"][2]}
    # 8.10: el cojín entra primero y sale después; cuánto tiene que subir su margen
    L = R["e810"]["L"]
    R["e810"]["entra_primero"] = R["e810"]["pasos"][0][0].nombres[R["e810"]["pasos"][0][1]]
    sube = -L["rc"][2]
    R["e810"]["margen_cojin_min"] = E810["c"][2] + sube
    z2, x2, _ = con_scipy([34, 36, float(E810["c"][2] + sube) + 0.5], E810["A"], E810["b"])
    assert x2[2] > 1e-6     # con 0,5 más que el umbral, los cojines entran
    # 8.2: soluciones básicas
    R["e82"] = basicas(E82)
    # 8.1: el problema original y su forma estándar tienen el mismo óptimo
    R["e81"] = forma_estandar()
    # ejemplo y caso: precios sombra en pesos
    R["ejemplo"]["duales_pesos"] = [y * 1000 for y in R["ejemplo"]["L"]["duales"]]
    R["caso"]["duales_hora"] = [y * 3600 for y in R["caso"]["L"]["duales"]]
    return R


def matricial(d, base):
    """x_B = B⁻¹b y costos reducidos c_N − c_B B⁻¹ N, con fracciones."""
    A = [[F(v) for v in fila] + [F(int(i == k)) for k in range(len(d["A"]))] for i, fila in enumerate(d["A"])]
    c = [F(v) for v in d["c"]] + [F(0)] * len(d["A"])
    m = len(A)
    B = np.array([[A[i][j] for j in base] for i in range(m)], dtype=object)
    Binv = inversa(B)
    xB = [sum(Binv[i][k] * d["b"][k] for k in range(m)) for i in range(m)]
    cB = [c[j] for j in base]
    y = [sum(cB[i] * Binv[i][k] for i in range(m)) for k in range(m)]          # c_B B⁻¹
    rc = {j: c[j] - sum(y[k] * A[k][j] for k in range(m)) for j in range(len(c)) if j not in base}
    return {"base": base, "Binv": Binv, "xB": xB, "y": y, "rc": rc, "z": sum(cb * xb for cb, xb in zip(cB, xB))}


def inversa(M):
    m = len(M)
    A = [[F(M[i][j]) for j in range(m)] + [F(int(i == k)) for k in range(m)] for i in range(m)]
    for col in range(m):
        piv = next(i for i in range(col, m) if A[i][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        p = A[col][col]
        A[col] = [v / p for v in A[col]]
        for i in range(m):
            if i != col and A[i][col] != 0:
                f = A[i][col]
                A[i] = [a - f * b for a, b in zip(A[i], A[col])]
    return [fila[m:] for fila in A]


def basicas(d):
    sol = []
    n = len(d["A"][0])
    for par in combinations(range(n), 2):
        B = [[F(d["A"][i][j]) for j in par] for i in range(2)]
        det = B[0][0] * B[1][1] - B[0][1] * B[1][0]
        if det == 0:
            sol.append((par, None)); continue
        Bi = inversa(B)
        xb = [Bi[i][0] * d["b"][0] + Bi[i][1] * d["b"][1] for i in range(2)]
        x = [F(0)] * n
        for j, v in zip(par, xb):
            x[j] = v
        sol.append((par, x))
    return sol


def forma_estandar():
    d = E81
    # original: mín c·x, x1 >= 0, x2 <= 0, x3 libre
    r = linprog(d["c"], A_ub=[[-a for a in d["A_ge"]], d["A_le"]], b_ub=[-d["b_ge"], d["b_le"]],
                A_eq=[d["A_eq"]], b_eq=[d["b_eq"]], bounds=[(0, None), (None, 0), (None, None)], method="highs")
    assert r.status == 0
    # estándar: máx w = −4x1 − 3x2' + 2x3' − 2x3''  (x2 = −x2', x3 = x3' − x3'')
    #   2x1 + x2' + x3' − x3'' − e1 = 5 ;  x1 − 3x2' + h2 = 12 ;  −x1 − x2' − 2x3' + 2x3'' = 4 ; todo >= 0
    c = [-4, -3, 2, -2, 0, 0]
    Aeq = [[2, 1, 1, -1, -1, 0], [1, -3, 0, 0, 0, 1], [-1, -1, -2, 2, 0, 0]]
    s = linprog([-v for v in c], A_eq=Aeq, b_eq=[5, 12, 4], bounds=[(0, None)] * 6, method="highs")
    assert s.status == 0 and abs(-s.fun + r.fun) < 1e-9
    return {"z": F(r.fun).limit_denominator(1000), "x": [F(v).limit_denominator(1000) for v in r.x]}


# ---------------------------------------------------------------- figura del caso
def figura(R, ruta):
    d = caso().DOS
    W, H, m = 520, 360, 50
    X, Y = 3600, 1400
    px = lambda x: m + x / X * (W - 2 * m)
    py = lambda y: H - m - y / Y * (H - 2 * m)
    region = [(0, 0), (3240, 0), (1440, 720), (1110, 830), (0, 830)]
    poly = " ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in region)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Segoe UI, sans-serif" font-size="11">',
         '<rect width="100%" height="100%" fill="#ffffff"/>',
         f'<polygon points="{poly}" fill="#f6d9cb" stroke="none"/>']
    # rectas
    for (a, b_, cap), col, nombre in [((30, 90, 108000), "#2B2F33", "estampado"), ((20, 50, 64800), "#5F656B", "planchado")]:
        x0, y0, x1, y1 = 0, cap / b_, cap / a, 0
        s.append(f'<line x1="{px(x0):.1f}" y1="{py(y0):.1f}" x2="{px(min(x1, X)):.1f}" y2="{py(max(y1, (cap - a * X) / b_ if x1 > X else 0)):.1f}" stroke="{col}" stroke-width="1.2"/>')
        s.append(f'<text x="{px(0) + 6:.1f}" y="{py(y0) - 4:.1f}" fill="{col}">{nombre}</text>')
    s.append(f'<line x1="{px(0):.1f}" y1="{py(830):.1f}" x2="{px(X):.1f}" y2="{py(830):.1f}" stroke="#5F656B" stroke-dasharray="4 3"/>')
    s.append(f'<text x="{px(X) - 4:.1f}" y="{py(830) + 14:.1f}" text-anchor="end" fill="#5F656B">demanda de polerones (830)</text>')
    # ejes
    s.append(f'<line x1="{px(0)}" y1="{py(0)}" x2="{px(X)}" y2="{py(0)}" stroke="#2B2F33"/>')
    s.append(f'<line x1="{px(0)}" y1="{py(0)}" x2="{px(0)}" y2="{py(Y)}" stroke="#2B2F33"/>')
    for v in range(0, X + 1, 600):
        s.append(f'<text x="{px(v):.1f}" y="{py(0) + 16:.1f}" text-anchor="middle" fill="#5F656B">{fmt(v)}</text>')
    for v in range(0, Y + 1, 400):
        s.append(f'<text x="{px(0) - 6:.1f}" y="{py(v) + 4:.1f}" text-anchor="end" fill="#5F656B">{fmt(v)}</text>')
    s.append(f'<text x="{px(X / 2):.1f}" y="{H - 12}" text-anchor="middle">x1 · poleras básicas</text>')
    s.append(f'<text x="14" y="{py(Y / 2):.1f}" text-anchor="middle" transform="rotate(-90 14 {py(Y / 2):.1f})">x2 · polerones</text>')
    # camino del simplex
    cam = [(float(a), float(b_)) for a, b_ in R["caso"]["camino"]]
    s.append('<defs><marker id="f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#E2622A"/></marker></defs>')
    for (a, b_), (c_, d_) in zip(cam, cam[1:]):
        s.append(f'<line x1="{px(a):.1f}" y1="{py(b_):.1f}" x2="{px(c_):.1f}" y2="{py(d_):.1f}" stroke="#E2622A" stroke-width="2.4" marker-end="url(#f)"/>')
    for k, ((a, b_), z) in enumerate(zip(cam, R["caso"]["z_camino"])):
        s.append(f'<circle cx="{px(a):.1f}" cy="{py(b_):.1f}" r="4" fill="#E2622A"/>')
        dy = {0: -8, 1: 18, 2: -8, 3: 18}[k]
        s.append(f'<text x="{px(a) + 8:.1f}" y="{py(b_) + dy:.1f}" fill="#2B2F33">Tabla {k}: ({fmt(a)}; {fmt(b_)}) · ${fmt(float(z))}</text>')
    s.append("</svg>")
    ruta.write_text("\n".join(s), encoding="utf-8")


# ---------------------------------------------------------------- lo que el .md tiene que decir
def tablas(R):
    """Todas las tablas generadas, en el orden en que aparecen en la unidad."""
    out = {}
    for k in ["ejemplo", "e83", "e85", "e86", "e810", "caso"]:
        pasos = R[k]["pasos"]
        out[k] = [tabla_md(p, i) for i, p in enumerate(pasos)]
    out["e83"] = out["e83"][:2]                        # 8.3 pide una sola iteración
    out["e84"] = [tabla_md(R["e84"]["pasos"][-1], 0)]  # 8.4 da solo la tabla final
    out["e88"] = [tabla_md(p, i) for i, p in enumerate(R["e88"]["pasos"])]
    out["e89"] = [tabla_md(p, i) for i, p in enumerate(R["e89"]["pasos"])]
    return out


def esperados(R):
    s = []
    E = R["ejemplo"]["L"]
    s += ["$80.000", fr(E["duales"][0]), fr(E["duales"][1]), "$3.333", "$1.333", "$3.000", "x3 = 0"]
    C = R["caso"]["L"]
    s += ["(1.440; 720)", "$4.824.000", "32,67", "−98/3", "$117.600", "$72.000", "110"]
    for (x1, x2), z in zip(R["caso"]["camino"], R["caso"]["z_camino"]):
        s.append(f"({fmt(x1)}; {fmt(x2)})"); s.append("$" + fmt(z))
    # 8.1
    s += [fr(v) for v in R["e81"]["x"]] + [fr(R["e81"]["z"])]
    # 8.2
    for par, x in R["e82"]:
        s.append("(" + "; ".join(fr(v) for v in x) + ")")
    # 8.3, 8.4, 8.5, 8.6, 8.10
    L = R["e84"]["L"]; s += [f"z = {fr(L['z'])}", "(8; 2; 0)"]
    L = R["e85"]["L"]; s += [f"z = {fr(L['z'])}"] + [f"({fr(a)}; {fr(b)})" for a, b in R["e85"]["camino"]]
    L = R["e86"]["L"]; s += [f"z = {fr(L['z'])}", dec(L["z"], 1)] + [fr(v) for v in L["x"][:3]]
    L = R["e810"]["L"]; s += ["(40; 30; 0)", "$2.440.000", fr(R["e810"]["margen_cojin_min"]) + " mil"]
    # 8.7
    for k, M in R["e87"].items():
        s += [fr(v) for v in M["xB"]] + [fr(v) for v in M["rc"].values()] + [fr(M["z"])]
    # 8.8
    s += [fr(v) for v in R["e88"]["ld"]]
    # 8.9
    s += [f"x2 = {fr(R['e89']['x2'])}", f"z = {fr(R['e89']['L']['z'])}"]
    return s


def cadena(R):
    C = caso().calcular()["u2"]
    L = R["caso"]["L"]
    ok = abs(float(L["z"]) - C["z"]) < 1e-6
    ok &= all(abs(float(L["x"][j]) - C["x"][j]) < 1e-6 for j in range(2))
    ok &= all(abs(float(L["duales"][i]) - C["duales"][i]) < 1e-6 for i in range(2))
    verts = {(round(a, 4), round(b, 4)) for a, b, _ in C["vertices"]}
    ok &= all((float(a), float(b)) in verts for a, b in R["caso"]["camino"])
    print("CADENA:", "OK, el simplex a mano termina en el óptimo y los precios sombra de la unidad 2" if ok else "NO calza")
    return ok


if __name__ == "__main__":
    R = resultados()
    for k in ["ejemplo", "e83", "e84", "e85", "e86", "e810", "caso"]:
        L = R[k]["L"]
        print(f"== {k}: z = {fr(L['z'])} · x = {[fr(v) for v in L['x']]} · duales = {[fr(v) for v in L['duales']]} · iteraciones = {L['iter']}")
    print("== 8.1:", fr(R["e81"]["z"]), [fr(v) for v in R["e81"]["x"]])
    print("== 8.2:", [(p, x and [fr(v) for v in x]) for p, x in R["e82"]])
    for k, M in R["e87"].items():
        print(f"== 8.7{k}: xB = {[fr(v) for v in M['xB']]} · rc = { {j: fr(v) for j, v in M['rc'].items()} } · z = {fr(M['z'])} · Binv = {[[fr(v) for v in f] for f in M['Binv']]}")
    print("== 8.8: LD =", [fr(v) for v in R["e88"]["ld"]])
    print("== 8.9: x2 =", fr(R["e89"]["x2"]), "z =", fr(R["e89"]["L"]["z"]))
    print("== 8.10: entra primero", R["e810"]["entra_primero"], "· margen mínimo del cojín", fr(R["e810"]["margen_cojin_min"]))
    print("== caso: camino", [(fr(a), fr(b)) for a, b in R["caso"]["camino"]], "z", [fr(z) for z in R["caso"]["z_camino"]])
    if not cadena(R):
        sys.exit(1)
    T = tablas(R)
    if "--tablas" in sys.argv:
        for k, ts in T.items():
            for i, t in enumerate(ts):
                print(f"\n<!-- {k} · tabla {i} -->\n{t}")
    if "--figura" in sys.argv:
        figura(R, RAMO / "unidades" / "figuras" / "u08_camino_simplex.svg")
        print("figura: unidades/figuras/u08_camino_simplex.svg")
    if "--revisar" in sys.argv:
        md = (RAMO / "unidades" / "08-metodo-simplex.md").read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md_n]
        lineas = set(l.strip() for l in md.splitlines())
        for k, ts in T.items():
            for t in ts:
                faltan += [f"tabla {k}: {l}" for l in t.splitlines()[2:] if l.strip() not in lineas]
        print("REVISIÓN:", "OK, todas las cifras y tablas están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
