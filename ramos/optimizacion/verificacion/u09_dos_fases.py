"""Unidad 9 · Simplex: dos fases, gran M y casos especiales.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado y cada tabla del simplex aparezcan escritos tal cual en el .md.

    python u09_dos_fases.py            # imprime los resultados y las tablas
    python u09_dos_fases.py --revisar  # además las busca en el .md

Las tablas salen de una implementación propia del simplex con fracciones exactas (Fraction). En la
gran M cada costo reducido es un número de la forma a + b·M. Cada problema se resuelve además con
scipy (HiGHS) y, si hay CPLEX, con los modelos OPL de `modelos/`; los tres caminos tienen que
coincidir. Convención de la tabla (la del curso): la fila 0 lleva los costos reducidos
c̄_j = c_j − c_B·B⁻¹·A_j y, en el lado derecho, −z. En un máximo entra el c̄ más positivo; en un
mínimo, el más negativo. Empates: entra la columna de más a la izquierda y sale la fila de más arriba.
"""
from fractions import Fraction as F
from pathlib import Path
import importlib.util, sys

import numpy as np
from scipy.optimize import linprog

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402

# ---------------------------------------------------------------- formato a la chilena

def fmt(x, dec=0):
    s = f"{float(x):,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x, 0)


def menos(s):
    return s.replace("-", "−")


def num(q):
    """Fracción → texto de tabla: entero con punto de miles, decimal corto o a/b."""
    q = F(q)
    if q.denominator == 1:
        return menos(fmt(q.numerator, 0))
    d = q.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    if d == 1:
        for dec in range(1, 5):
            if (q * 10 ** dec).denominator == 1:
                return menos(fmt(q, dec))
    signo = "−" if q < 0 else ""
    return f"{signo}{fmt(abs(q.numerator), 0)}/{fmt(q.denominator, 0)}"


# ---------------------------------------------------------------- números de la gran M

class Mx:
    """a + b·M con M «más grande que cualquier número»: se compara primero b y después a."""

    def __init__(self, a=0, b=0):
        self.a, self.b = F(a), F(b)

    def __add__(self, o):
        o = o if isinstance(o, Mx) else Mx(o)
        return Mx(self.a + o.a, self.b + o.b)

    __radd__ = __add__

    def __sub__(self, o):
        o = o if isinstance(o, Mx) else Mx(o)
        return Mx(self.a - o.a, self.b - o.b)

    def __rsub__(self, o):
        return Mx(o) - self

    def __mul__(self, k):
        assert not isinstance(k, Mx)
        return Mx(self.a * k, self.b * k)

    __rmul__ = __mul__

    def __neg__(self):
        return Mx(-self.a, -self.b)

    def clave(self):
        return (self.b, self.a)

    def __lt__(self, o):
        o = o if isinstance(o, Mx) else Mx(o)
        return self.clave() < o.clave()

    def __gt__(self, o):
        o = o if isinstance(o, Mx) else Mx(o)
        return self.clave() > o.clave()

    def __eq__(self, o):
        o = o if isinstance(o, Mx) else Mx(o)
        return self.clave() == o.clave()

    def __hash__(self):
        return hash(self.clave())


def num_m(v):
    if not isinstance(v, Mx):
        return num(v)
    a, b = v.a, v.b
    if b == 0:
        return num(a)
    coef = "" if abs(b) == 1 else num(abs(b))
    tm = f"{coef}M"
    if a == 0:
        return ("−" if b < 0 else "") + tm
    return f"{num(a)} {'−' if b < 0 else '+'} {tm}"


def cero(v):
    return v == 0 if not isinstance(v, Mx) else (v.a == 0 and v.b == 0)


# ---------------------------------------------------------------- el simplex en tabla

class Problema:
    """sentido 'max' o 'min'; filas (coeficientes, tipo '<=' '>=' '=', lado derecho ≥ 0)."""

    def __init__(self, nombre, sentido, c, filas, nombres_x=None):
        self.nombre, self.sentido = nombre, sentido
        self.c = [F(v) for v in c]
        self.filas = [([F(v) for v in a], t, F(b)) for a, t, b in filas]
        n = len(c)
        self.nx = nombres_x or [f"x{j + 1}" for j in range(n)]
        # forma estándar: holgura s_i (≤), exceso e_i y artificial a_i (≥), artificial a_i (=)
        cols, A, base = list(self.nx), [], []
        extra = []
        for i, (a, t, b) in enumerate(self.filas, start=1):
            if t == "<=":
                extra.append((f"s{i}", i - 1, 1, "holgura"))
            elif t == ">=":
                extra.append((f"e{i}", i - 1, -1, "exceso"))
        for i, (a, t, b) in enumerate(self.filas, start=1):
            if t in (">=", "="):
                extra.append((f"a{i}", i - 1, 1, "artificial"))
        # orden de columnas: x, holguras y excesos por fila, artificiales al final
        self.tipo = {v: "decision" for v in self.nx}
        for nom, fila, coef, tipo in extra:
            cols.append(nom)
            self.tipo[nom] = tipo
        self.cols = cols
        m = len(self.filas)
        for i, (a, t, b) in enumerate(self.filas):
            fila = list(a) + [F(0)] * (len(cols) - len(a))
            for nom, fi, coef, tipo in extra:
                if fi == i:
                    fila[cols.index(nom)] = F(coef)
            A.append(fila)
            base.append(f"s{i + 1}" if t == "<=" else f"a{i + 1}")
        self.A, self.b, self.base0 = A, [r[2] for r in self.filas], base

    def artificiales(self):
        return [v for v in self.cols if self.tipo[v] == "artificial"]


def costos(problema, fase, M=None):
    """Vector de costos de la fase: 1 = fase 1 (min Σ a), 2 = fase 2 (c original),
    'M' = gran M simbólica, número = gran M con ese valor."""
    c = {}
    for v in problema.cols:
        if problema.tipo[v] == "decision":
            c[v] = problema.c[problema.nx.index(v)]
        else:
            c[v] = F(0)
    if fase == 1:
        c = {v: F(1 if problema.tipo[v] == "artificial" else 0) for v in problema.cols}
    elif fase == "M":
        signo = -1 if problema.sentido == "max" else 1
        c = {v: (Mx(0, signo) if problema.tipo[v] == "artificial" else Mx(c[v])) for v in problema.cols}
    elif fase == "Mnum":
        signo = -1 if problema.sentido == "max" else 1
        c = {v: (F(signo) * F(M) if problema.tipo[v] == "artificial" else c[v]) for v in problema.cols}
    return c


def fila0(T, base, cols, c):
    zero = Mx() if any(isinstance(v, Mx) for v in c.values()) else F(0)
    red = []
    for j, v in enumerate(cols):
        s = c[v] - sum((c[base[i]] * T[i][j] for i in range(len(T))), zero)
        red.append(s)
    mz = zero - sum((c[base[i]] * T[i][-1] for i in range(len(T))), zero)
    return red, mz


def iterar(T, base, cols, c, sentido, etiqueta, tope=30):
    """Corre el simplex desde la tabla T (filas [coeficientes..., LD]) y devuelve las tablas."""
    tablas = []
    for _ in range(tope):
        red, mz = fila0(T, base, cols, c)
        cand = [(j, r) for j, r in enumerate(red) if (r > 0 if sentido == "max" else r < 0)]
        tab = {"etiqueta": etiqueta, "cols": list(cols), "base": list(base), "T": [list(f) for f in T],
               "red": red, "mz": mz, "entra": None, "sale": None, "razones": None, "estado": None}
        tablas.append(tab)
        if not cand:
            tab["estado"] = "optima"
            break
        if sentido == "max":
            je = max(cand, key=lambda jr: (jr[1], -jr[0]))[0]
        else:
            je = min(cand, key=lambda jr: (jr[1], jr[0]))[0]
        razones = [(T[i][-1] / T[i][je]) if T[i][je] > 0 else None for i in range(len(T))]
        tab["entra"], tab["razones"] = cols[je], razones
        validas = [(r, i) for i, r in enumerate(razones) if r is not None]
        if not validas:
            tab["estado"] = "no acotado"
            break
        rmin = min(r for r, _ in validas)
        isale = min(i for r, i in validas if r == rmin)
        tab["sale"] = base[isale]
        tab["empate"] = sum(1 for r, _ in validas if r == rmin) > 1
        piv = T[isale][je]
        T[isale] = [v / piv for v in T[isale]]
        for i in range(len(T)):
            if i != isale and T[i][je] != 0:
                k = T[i][je]
                T[i] = [a - k * p for a, p in zip(T[i], T[isale])]
        base[isale] = cols[je]
    return tablas


def resolver(problema, metodo, M=None):
    """metodo: 'directo' (solo ≤), 'dos_fases', 'gran_m' o 'm_numerico'."""
    cols = list(problema.cols)
    T = [list(f) + [b] for f, b in zip(problema.A, problema.b)]
    base = list(problema.base0)
    out = {"problema": problema, "metodo": metodo, "tablas": []}
    if metodo == "directo":
        assert not problema.artificiales()
        out["tablas"] = iterar(T, base, cols, costos(problema, 2), problema.sentido, "")
    elif metodo == "gran_m":
        out["tablas"] = iterar(T, base, cols, costos(problema, "M"), problema.sentido, "Gran M")
    elif metodo == "m_numerico":
        out["tablas"] = iterar(T, base, cols, costos(problema, "Mnum", M), problema.sentido, f"M = {M}")
    elif metodo == "dos_fases":
        t1 = iterar(T, base, cols, costos(problema, 1), "min", "Fase 1")
        out["tablas"] += t1
        w = -t1[-1]["mz"]
        out["w"] = w
        if w > 0:
            out["estado"] = "infactible"
            return cierre(out)
        # una artificial que quedó básica en cero se saca pivoteando en cualquier columna no artificial
        arts = set(problema.artificiales())
        for i, v in enumerate(base):
            if v in arts:
                j = next((j for j, cv in enumerate(cols) if cv not in arts and T[i][j] != 0), None)
                assert j is not None, "fila redundante: no implementado"
                piv = T[i][j]
                T[i] = [x / piv for x in T[i]]
                for k in range(len(T)):
                    if k != i and T[k][j] != 0:
                        f = T[k][j]
                        T[k] = [a - f * p for a, p in zip(T[k], T[i])]
                base[i] = cols[j]
        keep = [j for j, v in enumerate(cols) if v not in arts]
        cols2 = [cols[j] for j in keep]
        T2 = [[f[j] for j in keep] + [f[-1]] for f in T]
        out["tablas"] += iterar(T2, base, cols2, costos(problema, 2), problema.sentido, "Fase 2")
    return cierre(out)


def cierre(out):
    p = out["problema"]
    ult = out["tablas"][-1]
    out.setdefault("estado", ult["estado"])
    if out["estado"] == "optima":
        valores = {v: F(0) for v in p.cols}
        for i, v in enumerate(ult["base"]):
            valores[v] = ult["T"][i][-1]
        out["valores"] = valores
        out["x"] = [valores[v] for v in p.nx]
        out["z"] = sum(ci * xi for ci, xi in zip(p.c, out["x"]))
        no_basicas = [v for v in ult["cols"] if v not in ult["base"]]
        out["multiples"] = [v for v in no_basicas if cero(ult["red"][ult["cols"].index(v)])]
        out["degenerada"] = any(ult["T"][i][-1] == 0 for i in range(len(ult["T"])))
        out["artificial_positiva"] = [v for v in p.artificiales() if valores.get(v, 0) > 0]
    return out


# ---------------------------------------------------------------- la tabla en Markdown

def latex_var(v):
    return f"${v[0]}_{{{v[1:]}}}$" if len(v) > 1 else f"${v}$"


def tabla_md(tab):
    cols = tab["cols"]
    enc = "| Base | " + " | ".join(latex_var(v) for v in cols) + " | LD |"
    sep = "|" + "---|" * (len(cols) + 2)
    filas = [enc, sep]
    filas.append("| $\\bar c$ | " + " | ".join(num_m(r) for r in tab["red"]) + f" | {num_m(tab['mz'])} |")
    for v, f in zip(tab["base"], tab["T"]):
        filas.append(f"| {latex_var(v)} | " + " | ".join(num(x) for x in f[:-1]) + f" | {num(f[-1])} |")
    return "\n".join(filas)


def paso_md(tab):
    if tab["estado"] == "optima":
        return "Óptima: ningún costo reducido mejora."
    if tab["estado"] == "no acotado":
        return f"Entra {latex_var(tab['entra'])}; ninguna fila tiene coeficiente positivo en su columna: **no acotado**."
    raz = " · ".join(f"{latex_var(v)} {num(r)}" if r is not None else f"{latex_var(v)} —"
                     for v, r in zip(tab["base"], tab["razones"]))
    emp = " (empate: sale la fila de más arriba)" if tab.get("empate") else ""
    return f"Entra {latex_var(tab['entra'])}. Razones: {raz}. Sale {latex_var(tab['sale'])}{emp}."


def todas_md(res):
    trozos = []
    for k, tab in enumerate(res["tablas"]):
        trozos.append(tabla_md(tab))
        trozos.append(paso_md(tab))
    return trozos


# ---------------------------------------------------------------- comprobación externa

def scipy_resolver(p):
    c = [float(v) for v in p.c]
    if p.sentido == "max":
        c = [-v for v in c]
    Aub, bub, Aeq, beq = [], [], [], []
    for a, t, b in p.filas:
        a = [float(v) for v in a]
        if t == "<=":
            Aub.append(a); bub.append(float(b))
        elif t == ">=":
            Aub.append([-v for v in a]); bub.append(-float(b))
        else:
            Aeq.append(a); beq.append(float(b))
    r = linprog(c, A_ub=Aub or None, b_ub=bub or None, A_eq=Aeq or None, b_eq=beq or None,
                bounds=[(0, None)] * len(c), method="highs")
    return r


def coincide_scipy(res):
    r = scipy_resolver(res["problema"])
    if res["estado"] == "optima":
        assert r.status == 0, (res["problema"].nombre, r.message)
        z = -r.fun if res["problema"].sentido == "max" else r.fun
        assert abs(z - float(res["z"])) < 1e-6, (res["problema"].nombre, z, res["z"])
    elif res["estado"] == "infactible":
        assert r.status == 2, (res["problema"].nombre, r.status)
    elif res["estado"] == "no acotado":
        assert r.status == 3, (res["problema"].nombre, r.status)
    return True


def opl(mod, claves):
    """Corre el modelo OPL; devuelve sus valores o None si no hay CPLEX."""
    r = correr(RAMO / "modelos" / mod)
    if r is None:
        return None
    return r


# ---------------------------------------------------------------- datos (originales; pasados por colisiones.py)

# Ejemplo · sustrato de un vivero: tierra de hoja (x1) y compost (x2), en litros por saco
EJEMPLO = Problema("ejemplo", "min", [180, 310],
                   [([1, 1], "=", 60),               # el saco lleva 60 litros
                    ([1, 4], ">=", 150),             # al menos 150 g de nitrógeno
                    ([0, 1], "<=", 40)])             # a lo más 40 litros de compost

# Ejercicios
E1 = Problema("9.1", "min", [4, 7, 3], [([2, 1, 1], ">=", 12), ([1, 3, 0], "=", 15), ([1, 1, 2], "<=", 20)])
E2 = Problema("9.2", "max", [5, 10], [([1, 2], "<=", 16), ([3, 2], "<=", 24)])
E3 = Problema("9.3", "max", [2, 3], [([1, -1], "<=", 4), ([-2, 1], "<=", 2)])
E4 = Problema("9.4", "max", [3, 2], [([1, 1], "<=", 5), ([2, 3], ">=", 18)])
E5 = Problema("9.5", "min", [6, 4], [([2, 1], ">=", 10), ([1, 2], ">=", 11), ([1, 1], "<=", 9)])
E6 = Problema("9.6", "max", [5, 4, 2], [([1, 1, 1], "=", 10), ([2, 1, 0], "<=", 14), ([0, 0, 1], ">=", 2)])
E7 = Problema("9.7", "max", [3, 2], [([1, 1], "<=", 6), ([1, 0], "<=", 4), ([2, 1], "<=", 8)])
# 9.8 · cuatro tablas para diagnosticar (cada una sale de un problema chico)
E8 = {
    "A": Problema("9.8A", "max", [4, 3], [([2, 1], "<=", 10), ([1, 1], "<=", 7)]),
    "B": Problema("9.8B", "max", [2, 4], [([1, 2], "<=", 8), ([1, 0], "<=", 5)]),
    "C": Problema("9.8C", "max", [1, 2], [([1, -1], "<=", 3), ([-1, 1], "<=", 1)]),
    "D": Problema("9.8D", "min", [2, 5], [([1, 1], "<=", 4), ([1, 2], ">=", 10)]),
}
E9_M = [2, 5]          # valores de M que se prueban en 9.9 (sobre el problema 9.5)

# Caso integrador · dos productos de la unidad 2 + un compromiso mínimo de polerones (≥)
COMPROMISO_POLERONES = 780
# 9.10 · el club pide además un mínimo de poleras básicas
COMPROMISO_POLERAS = 1_280


def cargar_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_lp.py")
    caso = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caso)
    return caso


def problema_caso(caso, con_poleras=False):
    d = caso.DOS
    filas = [(d["est"], "<=", d["cap_est"]), (d["pla"], "<=", d["cap_pla"]), ([0, 1], "<=", d["dem_polerones"]),
             ([0, 1], ">=", COMPROMISO_POLERONES)]
    if con_poleras:
        filas.append(([1, 0], ">=", COMPROMISO_POLERAS))
    return Problema("caso" + ("+" if con_poleras else ""), "max", d["margen"], filas)


# ---------------------------------------------------------------- resultados

def resultados():
    caso = cargar_caso()
    R = {"caso_mod": caso}
    R["ej_m"] = resolver(EJEMPLO, "gran_m")
    R["ej_2f"] = resolver(EJEMPLO, "dos_fases")
    assert R["ej_m"]["x"] == R["ej_2f"]["x"] == [30, 30]
    # bases visitadas: la gran M y las dos fases pasan por las mismas
    R["ej_bases_m"] = [t["base"] for t in R["ej_m"]["tablas"]]
    R["ej_bases_2f"] = [t["base"] for t in R["ej_2f"]["tablas"]]
    # costo de la mezcla y holgura del tope de maíz
    R["ej_holgura_compost"] = R["ej_m"]["valores"]["s3"]

    # 9.1 · solo la forma estándar y la fila 0 inicial de la fase 1 y de la gran M
    T0 = [list(f) + [b] for f, b in zip(E1.A, E1.b)]
    R["e1_fase1"] = fila0(T0, list(E1.base0), E1.cols, costos(E1, 1))
    R["e1_granm"] = fila0(T0, list(E1.base0), E1.cols, costos(E1, "M"))
    R["e1_res"] = resolver(E1, "dos_fases")

    R["e2"] = resolver(E2, "directo")
    assert R["e2"]["multiples"] == ["x1"]
    # la otra solución óptima: se hace entrar x1 en la tabla final
    ult = R["e2"]["tablas"][-1]
    T = [list(f) for f in ult["T"]]
    base = list(ult["base"])
    cols = ult["cols"]
    je = cols.index("x1")
    razones = [(T[i][-1] / T[i][je]) if T[i][je] > 0 else None for i in range(len(T))]
    isale = min((r, i) for i, r in enumerate(razones) if r is not None)[1]
    piv = T[isale][je]
    T[isale] = [v / piv for v in T[isale]]
    for i in range(len(T)):
        if i != isale:
            k = T[i][je]
            T[i] = [a - k * p for a, p in zip(T[i], T[isale])]
    base[isale] = "x1"
    red, mz = fila0(T, base, cols, costos(E2, 2))
    otra = {"etiqueta": "", "cols": cols, "base": base, "T": T, "red": red, "mz": mz, "estado": "optima"}
    R["e2_otra"] = otra
    v = {b: T[i][-1] for i, b in enumerate(base)}
    R["e2_vertices"] = [tuple(R["e2"]["x"]), (v.get("x1", 0), v.get("x2", 0))]

    R["e3"] = resolver(E3, "directo")
    assert R["e3"]["estado"] == "no acotado"
    ult = R["e3"]["tablas"][-1]
    R["e3_mz"] = -ult["mz"]
    R["e3_cbar"] = ult["red"][ult["cols"].index(ult["entra"])]
    R["e4"] = resolver(E4, "dos_fases")
    assert R["e4"]["estado"] == "infactible"
    R["e5"] = resolver(E5, "gran_m")
    R["e6"] = resolver(E6, "dos_fases")
    R["e7"] = resolver(E7, "directo")
    R["e7_z"] = [-t["mz"] for t in R["e7"]["tablas"]]
    R["e8"] = {k: resolver(p, "dos_fases" if p.artificiales() else "directo") for k, p in E8.items()}
    # tabla que se muestra de cada uno: A y B la final; C la tabla donde se detiene; D la final de la fase 1
    R["e8_tablas"] = {"A": R["e8"]["A"]["tablas"][1], "B": R["e8"]["B"]["tablas"][-1],
                      "C": R["e8"]["C"]["tablas"][-1], "D": R["e8"]["D"]["tablas"][-1]}
    R["e9"] = {M: resolver(E5, "m_numerico", M) for M in E9_M}
    # el umbral de M: el mayor precio dual de las restricciones ≥ del 9.5 (unidad 10)
    r = scipy_resolver(E5)
    R["e9_duales"] = [-float(m) for m in r.ineqlin.marginals]   # signo de linprog (A_ub con −)
    # caso
    p = problema_caso(caso)
    R["caso"] = resolver(p, "dos_fases")
    R["caso_m"] = resolver(p, "gran_m")
    R["caso_sin"] = caso.calcular()["u2"]
    R["caso_costo_compromiso"] = R["caso_sin"]["z"] - float(R["caso"]["z"])
    R["caso_doble"] = resolver(problema_caso(caso, True), "dos_fases")
    assert R["caso_doble"]["estado"] == "infactible"
    w = R["caso_doble"]["w"]
    R["caso_doble_w"] = w
    d = caso.DOS
    x = [COMPROMISO_POLERAS, COMPROMISO_POLERONES]
    # segundos de estampado que faltan para cumplir los dos compromisos
    R["caso_doble_seg"] = sum(a * xi for a, xi in zip(d["est"], x)) - d["cap_est"]
    # la fase 1 recorta donde le cuesta menos unidades: polerones, a 90 s cada uno
    assert w * d["est"][1] == R["caso_doble_seg"]
    # con esos segundos de más, el único plan factible
    R["caso_doble_z"] = sum(m * xi for m, xi in zip(d["margen"], x))
    R["caso_doble_pla"] = sum(a * xi for a, xi in zip(d["pla"], x))
    for k in ["ej_m", "e1_res", "e2", "e3", "e4", "e5", "e6", "e7", "caso", "caso_doble"]:
        coincide_scipy(R[k])
    for k in "ABCD":
        coincide_scipy(R["e8"][k])
    R["opl"] = comprobar_opl(R)
    return R


def comprobar_opl(R):
    """Corre los .mod de la unidad y exige que calcen con el simplex propio."""
    hechos = []
    r = correr(RAMO / "modelos" / "u09_sustrato.mod")
    if r is None:
        print("OPL: no hay CPLEX en este equipo; se sigue con scipy")
        return None
    v = r["valores"]
    assert abs(r["objetivo"] - float(R["ej_m"]["z"])) < 1e-6
    assert abs(v["x_tierra"] - 30) < 1e-6 and abs(v["x_compost"] - 30) < 1e-6
    R["ej_duales_opl"] = {k: v[k] for k in ["dual_volumen", "dual_nitrogeno", "dual_compost"]}
    hechos.append("u09_sustrato")
    r = correr(RAMO / "modelos" / "u09_compromiso.mod")
    v = r["valores"]
    assert abs(r["objetivo"] - float(R["caso"]["z"])) < 1e-6
    assert abs(v["x_poleras"] - float(R["caso"]["x"][0])) < 1e-6
    assert abs(v["x_polerones"] - float(R["caso"]["x"][1])) < 1e-6
    R["caso_duales_opl"] = {k: v[k] for k in ["dual_estampado", "dual_planchado", "dual_demanda", "dual_compromiso"]}
    hechos.append("u09_compromiso")
    r = correr(RAMO / "modelos" / "u09_fase1_compromisos.mod")
    assert abs(r["objetivo"] - float(R["caso_doble_w"])) < 1e-6
    R["fase1_opl"] = r["valores"]
    hechos.append("u09_fase1_compromisos")
    return hechos


# ---------------------------------------------------------------- impresión

def imprimir(R):
    def bloque(nombre, res):
        print(f"\n== {nombre} · {res['metodo']} · {res['estado']}")
        for t in todas_md(res):
            print(t)
            print()
        if res["estado"] == "optima":
            print("x =", [num(x) for x in res["x"]], "z =", num(res["z"]), "múltiples:", res["multiples"],
                  "degenerada:", res["degenerada"])
        if "w" in res:
            print("w* =", num(res["w"]))
    bloque("Ejemplo", R["ej_m"])
    bloque("Ejemplo", R["ej_2f"])
    print("bases gran M:", R["ej_bases_m"])
    print("bases 2 fases:", R["ej_bases_2f"])
    print("\n9.1 fila 0 fase 1:", [num(x) for x in R["e1_fase1"][0]], num(R["e1_fase1"][1]))
    print("9.1 fila 0 gran M:", [num_m(x) for x in R["e1_granm"][0]], num_m(R["e1_granm"][1]))
    print("9.1 óptimo:", [num(x) for x in R["e1_res"]["x"]], num(R["e1_res"]["z"]))
    bloque("9.2", R["e2"])
    print(tabla_md(R["e2_otra"]))
    print("vértices óptimos:", R["e2_vertices"])
    bloque("9.3", R["e3"])
    bloque("9.4", R["e4"])
    bloque("9.5", R["e5"])
    bloque("9.6", R["e6"])
    bloque("9.7", R["e7"])
    print("z por tabla:", [num(z) for z in R["e7_z"]])
    for k in "ABCD":
        bloque("9.8" + k, R["e8"][k])
    for M, res in R["e9"].items():
        bloque(f"9.9 M={M}", res)
        if res["estado"] == "optima":
            print("artificiales > 0:", res["artificial_positiva"], {v: num(res["valores"][v]) for v in res["problema"].artificiales()})
    print("duales 9.5:", R["e9_duales"])
    bloque("Caso", R["caso"])
    bloque("Caso gran M", R["caso_m"])
    print("costo del compromiso:", R["caso_costo_compromiso"])
    bloque("Caso doble compromiso", R["caso_doble"])
    print("segundos que faltan:", num(R["caso_doble_seg"]), "z con ellos:", R["caso_doble_z"], "planchado:", R["caso_doble_pla"])
    if R.get("opl"):
        print("\nOPL:", R["opl"], R.get("caso_duales_opl"), R.get("fase1_opl"))


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    e = []
    for k in ["ej_m", "ej_2f", "e2", "e3", "e4", "e5", "e6", "e7", "caso"]:
        e += [tabla_md(t) for t in R[k]["tablas"]]
        e += [paso_md(t) for t in R[k]["tablas"]]
    e.append(tabla_md(R["e2_otra"]))
    for k in "ABCD":
        e.append(tabla_md(R["e8_tablas"][k]))
    for M in E9_M:
        e.append(tabla_md(R["e9"][M]["tablas"][-1]))
    e.append(tabla_md(R["caso_doble"]["tablas"][-1]))
    e += [pesos(R["ej_m"]["z"]), pesos(R["caso"]["z"]), pesos(R["caso_sin"]["z"]),
          pesos(R["caso_costo_compromiso"]), pesos(R["caso_doble_z"])]
    e += [num(x) for x in R["e1_fase1"][0]] + [num(R["e1_fase1"][1])]
    e += [num(R["caso_doble_seg"]) + " segundos", num(R["caso_doble_w"])]
    e += [num(x) for x in R["e1_res"]["x"]] + [num(R["e1_res"]["z"])]
    e += [num(R["e6"]["z"]), num(R["e5"]["z"])]
    return e


def cadena(R):
    caso = R["caso_mod"]
    C = caso.calcular()
    sin = resolver(Problema("u2", "max", caso.DOS["margen"],
                            [(caso.DOS["est"], "<=", caso.DOS["cap_est"]), (caso.DOS["pla"], "<=", caso.DOS["cap_pla"]),
                             ([0, 1], "<=", caso.DOS["dem_polerones"])]), "directo")
    ok = all(abs(float(a) - b) < 1e-6 for a, b in zip(sin["x"], C["u2"]["x"])) and abs(float(sin["z"]) - C["u2"]["z"]) < 1e-6
    ok = ok and abs(float(R["caso"]["z"]) - float(R["caso_m"]["z"])) < 1e-9
    print("\nCADENA:", "OK, sin el compromiso el simplex propio da el óptimo de la unidad 2 del caso"
          if ok else "NO calza con el caso")
    return ok


def figura(R):
    """Región factible del caso con el compromiso y el camino del simplex (fase 1 y fase 2)."""
    d = R["caso_mod"].DOS
    W, H, m = 640, 380, 56
    X, Y = 3800, 1400                                   # rango de los ejes (unidades)
    sx = lambda x: m + (W - 2 * m) * x / X
    sy = lambda y: H - m + 10 - (H - 2 * m) * y / Y
    pt = lambda x, y: f"{sx(x):.1f},{sy(y):.1f}"
    est_x, est_y = d["cap_est"] / d["est"][0], d["cap_est"] / d["est"][1]
    pla_x, pla_y = d["cap_pla"] / d["pla"][0], d["cap_pla"] / d["pla"][1]
    dem, com = d["dem_polerones"], COMPROMISO_POLERONES
    # región de la unidad 2 (sin compromiso) y la franja que deja el compromiso
    region_u2 = [(0, 0), (3240, 0), (1440, 720), (1110, dem), (0, dem)]
    franja = [(0, com), (1260, com), (1110, dem), (0, dem)]
    camino = [(0, 0), (0, com), (0, dem), (1110, dem), (1260, com)]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         'font-family="Segoe UI, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>']
    for k in range(0, X + 1, 500):
        s.append(f'<line x1="{sx(k):.1f}" y1="{sy(0):.1f}" x2="{sx(k):.1f}" y2="{sy(0) + 4:.1f}" stroke="#2B2F33"/>')
        s.append(f'<text x="{sx(k):.1f}" y="{sy(0) + 17:.1f}" text-anchor="middle" fill="#5F656B">{fmt(k)}</text>')
    for k in range(0, Y + 1, 200):
        s.append(f'<line x1="{sx(0) - 4:.1f}" y1="{sy(k):.1f}" x2="{sx(0):.1f}" y2="{sy(k):.1f}" stroke="#2B2F33"/>')
        s.append(f'<text x="{sx(0) - 7:.1f}" y="{sy(k) + 4:.1f}" text-anchor="end" fill="#5F656B">{fmt(k)}</text>')
    s.append(f'<polygon points="{" ".join(pt(*p) for p in region_u2)}" fill="#F2F1EF" stroke="#D6D3CE"/>')
    s.append(f'<polygon points="{" ".join(pt(*p) for p in franja)}" fill="#E2622A" fill-opacity="0.35" stroke="#E2622A"/>')
    lineas = [((0, est_y), (est_x, 0), "estampado"), ((0, pla_y), (pla_x, 0), "planchado"),
              ((0, dem), (X, dem), f"x₂ ≤ {fmt(dem)}"), ((0, com), (X, com), f"x₂ ≥ {fmt(com)}")]
    for (a, b, nombre) in lineas:
        s.append(f'<line x1="{sx(a[0]):.1f}" y1="{sy(a[1]):.1f}" x2="{sx(b[0]):.1f}" y2="{sy(b[1]):.1f}" '
                 f'stroke="#5F656B" stroke-dasharray="4 3"/>')
    s.append(f'<text x="{sx(2700):.1f}" y="{sy(300) - 6:.1f}" fill="#5F656B">estampado</text>')
    s.append(f'<text x="{sx(2950):.1f}" y="{sy(80) - 6:.1f}" fill="#5F656B">planchado</text>')
    s.append(f'<text x="{sx(X) - 4:.1f}" y="{sy(dem) - 5:.1f}" text-anchor="end" fill="#5F656B">x₂ ≤ {fmt(dem)}</text>')
    s.append(f'<text x="{sx(X) - 4:.1f}" y="{sy(com) + 14:.1f}" text-anchor="end" fill="#5F656B">x₂ ≥ {fmt(com)} (pedido)</text>')
    s.append('<defs><marker id="f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" '
             'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#2B2F33"/></marker></defs>')
    for k, (a, b) in enumerate(zip(camino, camino[1:])):
        estilo = 'stroke-dasharray="2 3"' if k == 0 else ''
        s.append(f'<line x1="{sx(a[0]):.1f}" y1="{sy(a[1]):.1f}" x2="{sx(b[0]):.1f}" y2="{sy(b[1]):.1f}" '
                 f'stroke="#2B2F33" stroke-width="2" {estilo} marker-end="url(#f)"/>')
    for (x, y), rot in zip(camino, ["(0, 0)", "(0, 780)", "(0, 830)", "(1.110, 830)", "(1.260, 780)"]):
        s.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="3.5" fill="#2B2F33"/>')
    s.append(f'<text x="{sx(0) + 8:.1f}" y="{sy(390):.1f}" fill="#2B2F33">fase 1</text>')
    def rotulo(px, py, tx, ty, texto, color="#2B2F33", peso="400", ancla="start"):
        s.append(f'<line x1="{sx(px):.1f}" y1="{sy(py):.1f}" x2="{sx(tx):.1f}" y2="{sy(ty) - 4:.1f}" stroke="{color}" stroke-width="0.8"/>')
        s.append(f'<text x="{sx(tx):.1f}" y="{sy(ty):.1f}" text-anchor="{ancla}" fill="{color}" font-weight="{peso}">{texto}</text>')
    rotulo(1110, dem, 700, 1080, "(1.110, 830)", ancla="middle")
    rotulo(1260, com, 1150, 420, "óptimo con el pedido (1.260, 780)", "#E2622A", "600")
    s.append(f'<circle cx="{sx(1440):.1f}" cy="{sy(720):.1f}" r="3.5" fill="#FFFFFF" stroke="#2B2F33"/>')
    rotulo(1440, 720, 1750, 1000, "óptimo sin pedido (1.440, 720)", "#5F656B")
    s.append(f'<line x1="{sx(0)}" y1="{sy(0)}" x2="{sx(X)}" y2="{sy(0)}" stroke="#2B2F33"/>')
    s.append(f'<line x1="{sx(0)}" y1="{sy(0)}" x2="{sx(0)}" y2="{sy(Y)}" stroke="#2B2F33"/>')
    s.append(f'<text x="{sx(X):.1f}" y="{sy(0) + 34:.1f}" text-anchor="end" fill="#2B2F33">x₁ poleras básicas</text>')
    s.append(f'<text x="{sx(0):.1f}" y="{sy(Y) - 10:.1f}" fill="#2B2F33">x₂ polerones</text>')
    s.append("</svg>")
    ruta = RAMO / "unidades" / "figuras" / "u09_compromiso.svg"
    ruta.parent.mkdir(exist_ok=True)
    ruta.write_text("\n".join(s), encoding="utf-8")
    return ruta


if __name__ == "__main__":
    R = resultados()
    figura(R)
    imprimir(R)
    if not cadena(R):
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (RAMO / "unidades" / "09-simplex-casos-especiales.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}:")
        for x in faltan:
            print("  ·", x[:300].replace("\n", " ⏎ "))
        sys.exit(1 if faltan else 0)
