"""Unidad 12 · Análisis de sensibilidad y precios sombra.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md.

Los rangos se calculan como en clase, con la base óptima y fracciones exactas: B⁻¹, xB = B⁻¹b,
y = cB·B⁻¹, costos reducidos y la tabla final. Se comprueban de tres maneras:
  1. resolviendo de nuevo con HiGHS (scipy) justo dentro y justo fuera de cada rango;
  2. si hay CPLEX, contra el informe «display sensitivity» del optimizador interactivo, leyendo el
     modelo que exporta OPL con «oplrun -e»;
  3. si hay CPLEX, corriendo los .mod de la unidad y comparando objetivo, variables y duales.
También genera la figura SVG de la sección 2 y las tablas largas del texto.

    python u12_sensibilidad.py            # imprime los resultados
    python u12_sensibilidad.py --revisar  # además los busca en el .md
"""
from fractions import Fraction as Fr
from pathlib import Path
import importlib.util, re, subprocess, sys, tempfile

import numpy as np
from scipy.optimize import linprog

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
FIGURAS = RAMO / "unidades" / "figuras"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
import opl as opl_mod  # noqa: E402

INF = None   # rango abierto


# ---------------------------------------------------------------- formato chileno

def fmt(x, dec=0):
    s = f"{float(x):,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x, dec=0):
    return "$" + fmt(x, dec)


def num(x):
    """Con los decimales justos (hasta tres) y signo menos tipográfico: 1,5 · 294,375 · 191,33 · −150."""
    x = Fr(x)
    dec = next((d for d in (0, 1, 2, 3) if (x * 10 ** d).denominator == 1), 2)
    s = fmt(abs(x), dec)
    return s if x >= 0 else "−" + s


def frac(x):
    """Fracción exacta para las tablas: 3/2 → «3/2», 300 → «300»."""
    x = Fr(x)
    if x.denominator == 1:
        return fmt(x) if x >= 0 else "−" + fmt(-x)
    s = f"{abs(x.numerator)}/{x.denominator}"
    return s if x >= 0 else "−" + s


# ---------------------------------------------------------------- datos (originales; pasados por colisiones.py)

# Ejemplo · la tostaduría de la unidad 11 (espresso, filtro, descafeinado)
EJ = dict(prod=["espresso", "filtro", "descafeinado"], rec=["tostadora", "envasadora", "bolsas"],
          c=[4200, 3450, 5100], A=[[6, 4, 9], [3, 2, 2], [1, 1, 1]], b=[2400, 1000, 350],
          nueva=dict(nombre="organico", uso=[4, 2, 1], margen=3700), tostadora_nueva=2700)

E1 = dict(c=[40000, 100000, 80000], A=[[1, 5, 1], [2, 2, 3], [1, 1, 5]], b=[860, 1000, 320],  # imprenta
          prensa_mas=100, troquel_menos=200, baja_b=50000)
E2 = dict(c=[1400000, 1000000], A=[[1, 1], [4, 2], [2, 4]], b=[28, 96, 90], tierra_nueva=30)   # huerto
E4 = dict(c=[1800, 2100, 1500], A=[[3, 4, 2], [2, 2, 3]], b=[600, 480], mora_nueva=2400)    # mermeladas
E5 = dict(c=[2600, 2900, 1900], A=[[4, 6, 3], [2, 1, 1], [1, 2, 1]], b=[960, 300, 260],     # quesería
          envasado_nuevo=290)
E7 = dict(c=[4100, 1400, 4500], A=[[5, 4, 3], [4, 4, 3]], b=[660, 820], U=[180, 390, 80],   # chocolatería
          nueva=dict(uso=[2, 3], margen=2000, tope=150))
E8 = dict(c=[840, 320, 440], A=[[7, 1, 7], [7, 9, 3], [9, 4, 9]], b=[190, 390, 190])        # alimento (mín)
E9 = dict(cambios_a=(2, -6), cambios_b=(3, 12))                                              # huerto, regla 100 %
E10 = dict(c=[5000, 4000], A=[[2, 1], [1, 3], [1, 0]], b=[40, 45, 18],                      # amasandería
           horno=[40, 42, 45, 50], arriendo_horno=1500, max_horno=10, arriendo_amasado=650, max_amasado=30)


# ---------------------------------------------------------------- álgebra exacta

def inversa(M):
    n = len(M)
    A = [[Fr(v) for v in fila] + [Fr(int(i == j)) for j in range(n)] for i, fila in enumerate(M)]
    for col in range(n):
        p = next(r for r in range(col, n) if A[r][col] != 0)
        A[col], A[p] = A[p], A[col]
        pv = A[col][col]
        A[col] = [v / pv for v in A[col]]
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [a - f * b for a, b in zip(A[r], A[col])]
    return [fila[n:] for fila in A]


def simplex(c, A, b):
    """Simplex de tabla con fracciones (máximo, restricciones ≤, b ≥ 0). Devuelve la tabla final."""
    m, n = len(A), len(c)
    T = [[Fr(v) for v in A[i]] + [Fr(int(k == i)) for k in range(m)] + [Fr(b[i])] for i in range(m)]
    cc = [Fr(v) for v in c] + [Fr(0)] * m
    base = [n + i for i in range(m)]
    while True:
        cb = [cc[j] for j in base]
        d = [cc[j] - sum(cb[i] * T[i][j] for i in range(m)) for j in range(n + m)]
        e = max(range(n + m), key=lambda j: (d[j], -j))
        if d[e] <= 0:
            z = sum(cb[i] * T[i][-1] for i in range(m))
            return dict(T=T, base=base, d=d, z=z)
        razones = [(T[i][-1] / T[i][e], base[i], i) for i in range(m) if T[i][e] > 0]
        _, _, s = min(razones)
        pv = T[s][e]
        T[s] = [v / pv for v in T[s]]
        for i in range(m):
            if i != s and T[i][e] != 0:
                f = T[i][e]
                T[i] = [a - f * bb for a, bb in zip(T[i], T[s])]
        base[s] = e


def sens(c, A, b, tipos=None, sentido="max"):
    """Base óptima, precios sombra, costos reducidos y rangos (lados derechos y coeficientes)."""
    m, n = len(A), len(c)
    tipos = tipos or ["<="] * m
    cols = [[Fr(A[i][j]) for i in range(m)] for j in range(n)]
    for i, t in enumerate(tipos):
        cols.append([Fr((1 if t == "<=" else -1) if k == i else 0) for k in range(m)])
    cc = [Fr(v) for v in c] + [Fr(0)] * m
    sg = 1 if sentido == "max" else -1
    Aub = [[(1 if t == "<=" else -1) * a for a in fila] for fila, t in zip(A, tipos)]
    bub = [(1 if t == "<=" else -1) * v for v, t in zip(b, tipos)]
    r = linprog([-sg * v for v in c], A_ub=Aub, b_ub=bub, method="highs")
    assert r.status == 0
    s = [(bb - np.dot(fila, r.x)) * (1 if t == "<=" else -1) for fila, bb, t in zip(A, b, tipos)]
    base = [j for j, v in enumerate(list(r.x) + s) if v > 1e-7]
    assert len(base) == m, "solución degenerada: este verificador no la usa"
    Bi = inversa([[cols[j][i] for j in base] for i in range(m)])
    xB = [sum(Bi[k][i] * Fr(b[i]) for i in range(m)) for k in range(m)]
    cB = [cc[j] for j in base]
    y = [sum(cB[k] * Bi[k][i] for k in range(m)) for i in range(m)]
    d = [cc[j] - sum(y[i] * cols[j][i] for i in range(m)) for j in range(n + m)]
    alfa = [[sum(Bi[k][i] * cols[j][i] for i in range(m)) for j in range(n + m)] for k in range(m)]
    rhs = []
    for i in range(m):
        col = [Bi[k][i] for k in range(m)]
        bajo = max([-xB[k] / col[k] for k in range(m) if col[k] > 0], default=INF)
        alto = min([-xB[k] / col[k] for k in range(m) if col[k] < 0], default=INF)
        rhs.append((INF if bajo is INF else b[i] + bajo, Fr(b[i]), INF if alto is INF else b[i] + alto))
    obj, nb = [], [j for j in range(n + m) if j not in base]
    for j in range(n):
        if j not in base:
            obj.append((INF, Fr(c[j]), c[j] - d[j]) if sentido == "max" else (c[j] - d[j], Fr(c[j]), INF))
            continue
        k, lo, hi = base.index(j), INF, INF
        for q in nb:
            a = alfa[k][q]
            if a == 0:
                continue
            cota = d[q] / a
            if (sentido == "max") == (a > 0):
                lo = cota if lo is INF else max(lo, cota)
            else:
                hi = cota if hi is INF else min(hi, cota)
        obj.append((INF if lo is INF else c[j] + lo, Fr(c[j]), INF if hi is INF else c[j] + hi))
    x = [Fr(0)] * (n + m)
    for k, j in enumerate(base):
        x[j] = xB[k]
    return dict(x=x[:n], holg=x[n:], z=sum(Fr(cj) * xj for cj, xj in zip(c, x[:n])), y=y, d=d[:n],
                base=base, Bi=Bi, xB=xB, alfa=alfa, rhs=rhs, obj=obj, n=n, m=m, tipos=tipos, sentido=sentido)


def resolver(c, A, b, tipos=None, sentido="max", bounds=None):
    m, n = len(A), len(c)
    tipos = tipos or ["<="] * m
    sg = 1 if sentido == "max" else -1
    Aub = [[(1 if t == "<=" else -1) * a for a in fila] for fila, t in zip(A, tipos)]
    bub = [(1 if t == "<=" else -1) * v for v, t in zip(b, tipos)]
    r = linprog([-sg * v for v in c], A_ub=Aub, b_ub=bub, bounds=bounds or [(0, None)] * n, method="highs")
    assert r.status == 0
    return dict(x=list(r.x), z=sg * -r.fun if sentido == "max" else r.fun,
                y=[sg * -v * (1 if t == "<=" else -1) for v, t in zip(r.ineqlin.marginals, tipos)],
                ub=list(-r.upper.marginals) if bounds else None)


def comprobar_rangos(c, A, b, S, tipos=None, sentido="max", eps=Fr(1, 1000)):
    """Segundo camino: dentro del rango el precio sombra (o la solución) no cambia; fuera, sí."""
    m, n = len(A), len(c)
    for i, (lo, _, hi) in enumerate(S["rhs"]):
        for lado, borde, dentro in ((lo, lo, +1), (hi, hi, -1)):
            if borde is INF:
                continue
            bb = list(b); bb[i] = float(borde + dentro * eps)
            assert abs(resolver(c, A, bb, tipos, sentido)["y"][i] - float(S["y"][i])) < 1e-6
            bb[i] = float(borde - dentro * Fr(1, 2))
            try:
                fuera = resolver(c, A, bb, tipos, sentido)
            except AssertionError:          # se volvió infactible: también es salir del rango
                continue
            assert abs(fuera["y"][i] - float(S["y"][i])) > 1e-9 or S["y"][i] == 0 and \
                abs(fuera["z"] - float(S["z"] + S["y"][i] * (borde - dentro * Fr(1, 2) - b[i]))) > 1e-9
    xs = [float(v) for v in S["x"]]
    for j, (lo, _, hi) in enumerate(S["obj"]):
        for borde, dentro in ((lo, +1), (hi, -1)):
            if borde is INF:
                continue
            cc = list(c); cc[j] = float(borde + dentro * eps)
            assert np.allclose(resolver(cc, A, b, tipos, sentido)["x"], xs, atol=1e-6)
            cc[j] = float(borde - dentro * Fr(1, 2))
            assert not np.allclose(resolver(cc, A, b, tipos, sentido)["x"], xs, atol=1e-6)


# ---------------------------------------------------------------- CPLEX: informe de sensibilidad

def cplex_exe():
    exe = opl_mod.oplrun()
    if exe is None:
        return None
    c = Path(exe).parents[3] / "cplex" / "bin" / "x64_win64" / "cplex.exe"
    return c if c.exists() else None


def correr_opl(mod, dat=None):
    exe = opl_mod.oplrun()
    if exe is None:
        return None
    p = subprocess.run([exe, mod] + ([dat] if dat else []), capture_output=True, text=True, timeout=120,
                       encoding="utf-8", errors="replace", cwd=MODELOS)
    assert p.returncode == 0, p.stdout[-800:] + p.stderr[-800:]
    vals = {}
    for linea in (p.stdout + p.stderr).splitlines():
        mm = re.match(r"^\s*([A-Za-z_][\w\[\]., ]*?)\s*=\s*(-?[\d.eE+-]+)\s*$", linea)
        if mm:
            vals[mm.group(1).strip()] = float(mm.group(2))
    return vals


def informe_cplex(mod, dat):
    """Exporta con oplrun -e y pide los rangos al optimizador interactivo. None si no hay CPLEX."""
    exe, cx = opl_mod.oplrun(), cplex_exe()
    if exe is None or cx is None:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        lp = Path(tmp) / "modelo.lp"
        subprocess.run([exe, "-e", str(lp), mod, dat], capture_output=True, text=True, timeout=120, cwd=MODELOS)
        p = subprocess.run([str(cx), "-c", f"read {lp}", "optimize", "display sensitivity rhs -",
                            "display sensitivity obj -"], capture_output=True, text=True, timeout=120, cwd=tmp)
    out = {}
    val = lambda s: None if "infinity" in s else (0.0 if s == "zero" else float(s))
    for linea in p.stdout.splitlines():
        mm = re.match(r"^(\S+\(\"[^\"]+\"\))\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$", linea)
        if mm:
            out[mm.group(1)] = tuple(val(g) for g in mm.groups()[1:])
    return out


def igual_rango(a, b):
    return (a is INF and b is None) or (a is not INF and b is not None and abs(float(a) - b) < 1e-4 * max(1, abs(b)))


def comparar_cplex(nombre, rep, S, filas, columnas):
    """filas: nombres CPLEX de las restricciones (en orden); columnas: de las variables."""
    if rep is None:
        print(f"   CPLEX {nombre}: no instalado, sigue con Python")
        return True
    malos = []
    for k, nom in enumerate(filas):
        dual, bajo, actual, alto = rep[nom]
        lo, cur, hi = S["rhs"][k]
        if not (abs(dual - float(S["y"][k])) < 1e-6 and igual_rango(lo, bajo) and igual_rango(hi, alto)):
            malos.append((nom, rep[nom], (lo, cur, hi), S["y"][k]))
    for j, nom in enumerate(columnas):
        dred, bajo, actual, alto = rep[nom]
        lo, cur, hi = S["obj"][j]
        if not (abs(dred - float(S["d"][j])) < 1e-6 and igual_rango(lo, bajo) and igual_rango(hi, alto)):
            malos.append((nom, rep[nom], (lo, cur, hi)))
    print(f"   CPLEX {nombre}:", "los rangos coinciden con los calculados a mano" if not malos else f"NO coinciden {malos}")
    return not malos


# ---------------------------------------------------------------- tablas en Markdown

def tabla_final(S, nombres_x, nombres_h):
    n, m = S["n"], S["m"]
    nombres = nombres_x + nombres_h
    filas = ["| Básica | " + " | ".join(nombres) + " | Valor |", "|---" * (n + m + 2) + "|"]
    for k, j in enumerate(S["base"]):
        filas.append(f"| {nombres[j]} | " + " | ".join(frac(v) for v in S["alfa"][k]) + f" | {frac(S['xB'][k])} |")
    dfull = list(S["d"]) + [-v for v in S["y"]]
    filas.append("| $c_j - z_j$ | " + " | ".join(frac(v) for v in dfull) + f" | $z = {fmt(S['z'])}$ |")
    return "\n".join(filas)


def lim(v, dec=0):
    return "sin límite" if v is INF else num(v) if dec == 0 else fmt(v, dec)


def tabla_rangos(S, nombres_r, nombres_p, unidad_y=""):
    t = ["| Restricción | Precio sombra | Desde | Actual | Hasta |", "|---|---|---|---|---|"]
    for k, nom in enumerate(nombres_r):
        lo, cur, hi = S["rhs"][k]
        t.append(f"| {nom} | {num(S['y'][k])}{unidad_y} | {lim(lo)} | {num(cur)} | {lim(hi)} |")
    t += ["", "| Variable | Costo reducido | Desde | Actual | Hasta |", "|---|---|---|---|---|"]
    for j, nom in enumerate(nombres_p):
        lo, cur, hi = S["obj"][j]
        t.append(f"| {nom} | {num(S['d'][j])} | {lim(lo)} | {num(cur)} | {lim(hi)} |")
    return "\n".join(t)


def informe_solver(S, nombres_p, nombres_r):
    """El informe de sensibilidad de Solver de Excel, con «1E+30» para lo ilimitado."""
    e30 = lambda v: "1E+30" if v is INF else num(v)
    t = ["| Celda | Valor final | Costo reducido | Coeficiente objetivo | Aumento permisible | Reducción permisible |",
         "|---|---|---|---|---|---|"]
    for j, nom in enumerate(nombres_p):
        lo, cur, hi = S["obj"][j]
        t.append(f"| {nom} | {num(S['x'][j])} | {num(S['d'][j])} | {num(cur)} | "
                 f"{e30(INF if hi is INF else hi - cur)} | {e30(INF if lo is INF else cur - lo)} |")
    t += ["", "| Restricción | Valor final | Precio sombra | Lado derecho | Aumento permisible | Reducción permisible |",
          "|---|---|---|---|---|---|"]
    for k, nom in enumerate(nombres_r):
        lo, cur, hi = S["rhs"][k]
        usado = cur - S["holg"][k] if S["tipos"][k] == "<=" else cur + S["holg"][k]
        t.append(f"| {nom} | {num(usado)} | {num(S['y'][k])} | {num(cur)} | "
                 f"{e30(INF if hi is INF else hi - cur)} | {e30(INF if lo is INF else cur - lo)} |")
    return "\n".join(t)


# ---------------------------------------------------------------- figura

def figura_dos(caso):
    """Rango del lado derecho del planchado en la versión de dos prendas (unidad 2 del caso)."""
    d = caso.DOS
    W, H, m = 560, 400, 50
    X, Y = 4000, 1400
    px = lambda x: m + x / X * (W - 2 * m)
    py = lambda y: H - m - y / Y * (H - 2 * m)
    def recta(a, rhs, color, ancho=2, guion=None, etiqueta=None, pos=None):
        # a·x = rhs, recortada a la caja
        pts = []
        if a[1] != 0:
            pts += [(0, rhs / a[1]), (X, (rhs - a[0] * X) / a[1])]
        if a[0] != 0:
            pts += [(rhs / a[0], 0), ((rhs - a[1] * Y) / a[0], Y)]
        pts = sorted({(round(x, 6), round(y, 6)) for x, y in pts if -1e-6 <= x <= X + 1e-6 and -1e-6 <= y <= Y + 1e-6})
        (x1, y1), (x2, y2) = pts[0], pts[-1]
        g = f' stroke-dasharray="{guion}"' if guion else ""
        s = f'<line x1="{px(x1):.1f}" y1="{py(y1):.1f}" x2="{px(x2):.1f}" y2="{py(y2):.1f}" stroke="{color}" stroke-width="{ancho}"{g}/>'
        if etiqueta:
            s += f'<text x="{px(pos[0]):.1f}" y="{py(pos[1]):.1f}" font-size="12" fill="{color}">{etiqueta}</text>'
        return s
    S = sens(d["margen"], [d["est"], d["pla"], [0, 1]], [d["cap_est"], d["cap_pla"], d["dem_polerones"]])
    lo, _, hi = S["rhs"][1]
    v_lo = (Fr(d["cap_est"] - d["est"][1] * d["dem_polerones"], d["est"][0]), Fr(d["dem_polerones"]))
    v_hi = (Fr(d["cap_est"], d["est"][0]), Fr(0))
    region = [(0, 0), (0, d["dem_polerones"]), (float(v_lo[0]), d["dem_polerones"]),
              tuple(float(v) for v in S["x"]), (d["cap_pla"] / d["pla"][0], 0)]
    poly = " ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in region)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Segoe UI, sans-serif">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           f'<polygon points="{poly}" fill="#E2622A" fill-opacity="0.12" stroke="none"/>',
           f'<line x1="{px(0)}" y1="{py(0)}" x2="{px(X)}" y2="{py(0)}" stroke="#2B2F33"/>',
           f'<line x1="{px(0)}" y1="{py(0)}" x2="{px(0)}" y2="{py(Y)}" stroke="#2B2F33"/>']
    for t in range(0, X + 1, 1000):
        svg.append(f'<text x="{px(t):.1f}" y="{py(0) + 16:.1f}" font-size="11" text-anchor="middle" fill="#5F656B">{fmt(t)}</text>')
    for t in range(0, Y + 1, 400):
        svg.append(f'<text x="{px(0) - 6:.1f}" y="{py(t) + 4:.1f}" font-size="11" text-anchor="end" fill="#5F656B">{fmt(t)}</text>')
    svg.append(f'<text x="{px(X):.1f}" y="{py(0) + 32:.1f}" font-size="12" text-anchor="end" fill="#2B2F33">poleras básicas (x1)</text>')
    svg.append(f'<text x="{px(0) + 6:.1f}" y="{py(Y) + 4:.1f}" font-size="12" fill="#2B2F33">polerones (x2)</text>')
    svg.append(recta(d["est"], d["cap_est"], "#2B2F33", 2))
    svg.append(recta([0, 1], d["dem_polerones"], "#5F656B", 1.5, "6 4"))
    svg.append(recta(d["pla"], d["cap_pla"], "#E2622A", 2.5))
    svg.append(recta(d["pla"], float(lo), "#E2622A", 1.5, "5 4"))
    svg.append(recta(d["pla"], float(hi), "#E2622A", 1.5, "5 4"))
    # leyenda en la esquina vacía (arriba a la derecha)
    lx, ly = px(2250), py(1370)
    for k, (color, guion, ancho, texto) in enumerate((
            ("#E2622A", None, 2.5, f"planchado actual: {fmt(d['cap_pla'])} s"),
            ("#E2622A", "5 4", 1.5, f"bordes del rango: {fmt(lo)} s y {fmt(hi)} s"),
            ("#2B2F33", None, 2, "estampado"),
            ("#5F656B", "6 4", 1.5, "tope de 830 polerones"))):
        g = f' stroke-dasharray="{guion}"' if guion else ""
        yy = ly + 18 * k
        svg.append(f'<line x1="{lx:.1f}" y1="{yy:.1f}" x2="{lx + 28:.1f}" y2="{yy:.1f}" stroke="{color}" stroke-width="{ancho}"{g}/>')
        svg.append(f'<text x="{lx + 34:.1f}" y="{yy + 4:.1f}" font-size="11.5" fill="#2B2F33">{texto}</text>')
    for (x, y), et, dx in ((S["x"], f"óptimo ({fmt(S['x'][0])}; {fmt(S['x'][1])})", 10),
                           (v_lo, f"({fmt(v_lo[0])}; {fmt(v_lo[1])})", 10), (v_hi, f"({fmt(v_hi[0])}; 0)", -100)):
        svg.append(f'<circle cx="{px(float(x)):.1f}" cy="{py(float(y)):.1f}" r="5" fill="#E2622A" stroke="#2B2F33"/>')
        svg.append(f'<text x="{px(float(x)) + dx:.1f}" y="{py(float(y)) - 9:.1f}" font-size="12" fill="#2B2F33">{et}</text>')
    svg.append("</svg>")
    FIGURAS.mkdir(parents=True, exist_ok=True)
    (FIGURAS / "u12_rango_planchado.svg").write_text("\n".join(svg), encoding="utf-8")
    return dict(S=S, lo=lo, hi=hi, v_lo=v_lo, v_hi=v_hi)


# ---------------------------------------------------------------- cálculo

def cargar_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_lp.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def resultados(caso):
    R = {}
    # Sección 2 · la figura con la versión de dos prendas
    R["fig"] = figura_dos(caso)
    C2 = caso.calcular()["u2"]
    assert np.allclose([float(v) for v in R["fig"]["S"]["y"][:2]], C2["duales"])

    # Ejemplo · tostaduría
    S = sens(EJ["c"], EJ["A"], EJ["b"])
    sx = simplex(EJ["c"], EJ["A"], EJ["b"])
    assert sorted(sx["base"]) == sorted(S["base"]) and sx["z"] == S["z"]
    comprobar_rangos(EJ["c"], EJ["A"], EJ["b"], S)
    b2 = list(EJ["b"]); b2[0] = EJ["tostadora_nueva"]
    xb_nuevo = [sum(S["Bi"][k][i] * Fr(b2[i]) for i in range(3)) for k in range(3)]
    z_nuevo = S["z"] + S["y"][0] * (EJ["tostadora_nueva"] - EJ["b"][0])
    assert abs(resolver(EJ["c"], EJ["A"], b2)["z"] - float(z_nuevo)) < 1e-6
    nv = EJ["nueva"]
    valor_nueva = sum(Fr(a) * yi for a, yi in zip(nv["uso"], S["y"]))
    A4 = [fila + [u] for fila, u in zip(EJ["A"], nv["uso"])]
    S4 = sens(EJ["c"] + [nv["margen"]], A4, EJ["b"])
    R["ej"] = dict(S=S, xb_nuevo=xb_nuevo, z_nuevo=z_nuevo, valor_nueva=valor_nueva,
                   cr_nueva=nv["margen"] - valor_nueva, S4=S4)

    # 12.1 · imprenta: informe tipo Solver
    S1 = sens(E1["c"], E1["A"], E1["b"])
    comprobar_rangos(E1["c"], E1["A"], E1["b"], S1)
    z_prensa = S1["z"] + S1["y"][0] * E1["prensa_mas"]
    assert E1["prensa_mas"] <= S1["rhs"][0][2] - S1["rhs"][0][1]
    b_tr = list(E1["b"]); b_tr[2] -= E1["troquel_menos"]
    z_tr = resolver(E1["c"], E1["A"], b_tr)["z"]
    cota_tr = S1["z"] - S1["y"][2] * E1["troquel_menos"]
    assert z_tr < float(cota_tr)
    z_bajab = S1["z"] - E1["baja_b"] * S1["x"][1]
    cc = list(E1["c"]); cc[1] -= E1["baja_b"]
    assert abs(resolver(cc, E1["A"], E1["b"])["z"] - float(z_bajab)) < 1e-6
    R["e1"] = dict(S=S1, z_prensa=z_prensa, z_tr=z_tr, cota_tr=cota_tr, z_bajab=z_bajab)

    # 12.2 y 12.3 · huerto (dos variables, vértices)
    S2 = sens(E2["c"], E2["A"], E2["b"])
    comprobar_rangos(E2["c"], E2["A"], E2["b"], S2)
    lo, _, hi = S2["rhs"][0]
    vert_lo = resolver(E2["c"], E2["A"], [float(lo), E2["b"][1], E2["b"][2]])["x"]
    vert_hi = resolver(E2["c"], E2["A"], [float(hi), E2["b"][1], E2["b"][2]])["x"]
    z_t30 = S2["z"] + S2["y"][0] * (E2["tierra_nueva"] - E2["b"][0])
    assert abs(resolver(E2["c"], E2["A"], [E2["tierra_nueva"], E2["b"][1], E2["b"][2]])["z"] - float(z_t30)) < 1e-6
    # 12.3 por pendientes: c1/c2 entre la pendiente de tierra (1/1) y la del agua (4/2)
    p_lo = Fr(E2["A"][0][0], E2["A"][0][1]) * E2["c"][1]
    p_hi = Fr(E2["A"][1][0], E2["A"][1][1]) * E2["c"][1]
    assert (p_lo, p_hi) == (S2["obj"][0][0], S2["obj"][0][2])
    R["e2"] = dict(S=S2, vert_lo=vert_lo, vert_hi=vert_hi, z_t30=z_t30, p_lo=p_lo, p_hi=p_hi)

    # 12.4 · mermeladas: cuánto le falta a la mora
    S4m = sens(E4["c"], E4["A"], E4["b"])
    cc = list(E4["c"]); cc[1] = E4["mora_nueva"]
    nuevo4 = sens(cc, E4["A"], E4["b"])
    R["e4"] = dict(S=S4m, umbral=S4m["obj"][1][2], nuevo=nuevo4)

    # 12.5 y 12.6 · quesería: tabla final, rangos y nueva solución
    S5 = sens(E5["c"], E5["A"], E5["b"])
    sx5 = simplex(E5["c"], E5["A"], E5["b"])
    assert sorted(sx5["base"]) == sorted(S5["base"])
    comprobar_rangos(E5["c"], E5["A"], E5["b"], S5)
    b5 = list(E5["b"]); b5[2] = E5["envasado_nuevo"]
    xb5 = [sum(S5["Bi"][k][i] * Fr(b5[i]) for i in range(3)) for k in range(3)]
    z5 = S5["z"] + S5["y"][2] * (E5["envasado_nuevo"] - E5["b"][2])
    assert abs(resolver(E5["c"], E5["A"], b5)["z"] - float(z5)) < 1e-6
    R["e5"] = dict(S=S5, xb_nuevo=xb5, z_nuevo=z5)

    # 12.7 · chocolatería: una caja nueva
    A7 = E7["A"] + [[int(i == j) for j in range(3)] for i in range(3)]
    b7 = E7["b"] + E7["U"]
    S7 = sens(E7["c"], A7, b7)
    nv = E7["nueva"]
    valor7 = sum(Fr(a) * yi for a, yi in zip(nv["uso"], S7["y"][:2]))
    A7n = [fila + [u] for fila, u in zip(E7["A"], nv["uso"])] + [[int(i == j) for j in range(4)] for i in range(4)]
    b7n = E7["b"] + E7["U"] + [nv["tope"]]
    S7n = sens(E7["c"] + [nv["margen"]], A7n, b7n)
    R["e7"] = dict(S=S7, valor=valor7, cr=nv["margen"] - valor7, Sn=S7n)

    # 12.8 · alimento (mínimo)
    S8 = sens(E8["c"], E8["A"], E8["b"], [">="] * 3, "min")
    comprobar_rangos(E8["c"], E8["A"], E8["b"], S8, [">="] * 3, "min")
    z_prot = S8["z"] + 10 * S8["y"][0]
    assert 10 <= S8["rhs"][0][2] - S8["rhs"][0][1]
    assert abs(resolver(E8["c"], E8["A"], [200, 390, 190], [">="] * 3, "min")["z"] - float(z_prot)) < 1e-6
    assert abs(resolver(E8["c"], E8["A"], [190, 390, 300], [">="] * 3, "min")["z"] - float(S8["z"])) < 1e-6
    R["e8"] = dict(S=S8, z_prot=z_prot)

    # 12.9 · regla del 100 % en el huerto
    out = {}
    for clave in ("cambios_a", "cambios_b"):
        dt, da = E9[clave]
        lo_t, cur_t, hi_t = S2["rhs"][0]; lo_a, cur_a, hi_a = S2["rhs"][1]
        f_t = Fr(dt) / (hi_t - cur_t) if dt > 0 else Fr(-dt) / (cur_t - lo_t)
        f_a = Fr(da) / (hi_a - cur_a) if da > 0 else Fr(-da) / (cur_a - lo_a)
        bb = [E2["b"][0] + dt, E2["b"][1] + da, E2["b"][2]]
        Sn = sens(E2["c"], E2["A"], bb) if f_t + f_a < 1 else None
        rr = resolver(E2["c"], E2["A"], bb)
        z_pred = S2["z"] + S2["y"][0] * dt + S2["y"][1] * da
        assert abs(rr["z"] - float(z_pred)) < 1e-6           # la base aguanta en los dos casos
        out[clave] = dict(pct=f_t + f_a, f_t=f_t, f_a=f_a, x=rr["x"], z=z_pred, mo=sum(a * v for a, v in zip(E2["A"][2], rr["x"])))
    R["e9"] = out

    # 12.10 · amasandería: más allá del rango y el arriendo
    S10 = sens(E10["c"], E10["A"], E10["b"])
    curva = []
    for h in E10["horno"]:
        r = resolver(E10["c"], E10["A"], [h, E10["b"][1], E10["b"][2]])
        curva.append((h, r["x"], r["z"]))
    def arriendo(ca):
        bounds = [(0, None), (0, None), (0, E10["max_horno"]), (0, E10["max_amasado"] if ca is not None else 0)]
        r = linprog([-E10["c"][0], -E10["c"][1], E10["arriendo_horno"], ca or 0],
                    A_ub=[[2, 1, -1, 0], [1, 3, 0, -1], [1, 0, 0, 0]], b_ub=E10["b"], bounds=bounds, method="highs")
        assert r.status == 0
        return list(r.x), -r.fun
    solo_horno = arriendo(None)
    ambos = arriendo(E10["arriendo_amasado"])
    R["e10"] = dict(S=S10, curva=curva, solo_horno=solo_horno, ambos=ambos)
    return R


def caso_u12(caso):
    C = caso.calcular()
    A = [caso.SEG_EST, caso.SEG_PLA, caso.TINTA_G] + [[int(i == j) for j in range(5)] for i in range(5)]
    b = [caso.CAP["estampado_s"], caso.CAP["planchado_s"], caso.CAP["tinta_g"]] + caso.DEMANDA_MAX
    S = sens(caso.MARGEN, A, b)
    comprobar_rangos(caso.MARGEN, A, b, S)
    hora = 3600
    curva = []
    for h in range(18, 25):
        bb = list(b); bb[1] = h * hora
        r = resolver(caso.MARGEN, A, bb)
        curva.append((h, r["z"], r["y"][1]))
    lo, cur, hi = S["rhs"][1]
    extra_sem6 = 2
    K = dict(S=S, C=C, curva=curva, valor_hora=S["y"][1] * hora, hora_extra=caso.HORA_EXTRA,
             perdida_hora=caso.HORA_EXTRA - S["y"][1] * hora, rango_h=(lo / hora, hi / hora),
             aumento_h=(hi - cur) / hora, sem6_margen=extra_sem6 * S["y"][1] * hora,
             sem6_costo=extra_sem6 * caso.HORA_EXTRA, falta_doble=-S["d"][2],
             estampado_h=S["holg"][0] / hora, z_max_planchado=curva[-1][1])
    K["sem6_neto"] = K["sem6_margen"] - K["sem6_costo"]
    return K


# ---------------------------------------------------------------- OPL y CPLEX contra Python

def verificar_software(R, K):
    ok = True
    S = R["ej"]["S"]
    rep = informe_cplex("u11_mezcla.mod", "u11_tostaduria.dat")
    ok &= comparar_cplex("ejemplo", rep, S, [f'Capacidad("{r}")' for r in EJ["rec"]], [f'x("{p}")' for p in EJ["prod"]])
    v = correr_opl("u11_mezcla.mod", "u12_tostaduria_organico.dat")
    if v is not None:
        S4 = R["ej"]["S4"]
        esp = {"margen": S4["z"], **{f"x[{p}]": S4["x"][j] for j, p in enumerate(EJ["prod"] + ["organico"])}}
        malos = {k: (v.get(k), float(e)) for k, e in esp.items() if abs(v.get(k, 1e99) - float(e)) > 1e-6}
        print("   OPL ejemplo con la mezcla nueva:", "coincide" if not malos else f"NO {malos}"); ok &= not malos
    rep = informe_cplex("u11_mezcla.mod", "u11_quesos.dat")
    ok &= comparar_cplex("12.5 y 12.6", rep, R["e5"]["S"], [f'Capacidad("{r}")' for r in ("leche", "camara", "envasado")],
                         [f'x("{p}")' for p in ("gauda", "mantecoso", "fresco")])
    v = correr_opl("u12_mezcla_topes.mod", "u12_chocolateria.dat")
    if v is not None:
        Sn = R["e7"]["Sn"]
        esp = {"margen": Sn["z"], "dual[templado]": Sn["y"][0], "dual[envasado]": Sn["y"][1],
               **{f"x[{p}]": Sn["x"][j] for j, p in enumerate(("clasica", "surtida", "trufas", "degustacion"))}}
        malos = {k: (v.get(k), float(e)) for k, e in esp.items() if abs(v.get(k, 1e99) - float(e)) > 1e-6}
        print("   OPL 12.7:", "coincide" if not malos else f"NO {malos}"); ok &= not malos
    v = correr_opl("u12_arriendo.mod")
    if v is not None:
        (x, z) = R["e10"]["ambos"]
        esp = {"margen_neto": z, "x[hallulla]": x[0], "x[marraqueta]": x[1], "horas_horno": x[2], "horas_amasado": x[3]}
        malos = {k: (v.get(k), e) for k, e in esp.items() if abs(v.get(k, 1e99) - e) > 1e-6}
        print("   OPL 12.10:", "coincide" if not malos else f"NO {malos}"); ok &= not malos
    # caso
    S = K["S"]
    rep = informe_cplex("u12_mezcla_topes.mod", "u12_estampa.dat")
    ok &= comparar_cplex("caso", rep, S, [f'Capacidad("{r}")' for r in ("estampado", "planchado", "tinta")] +
                         [f'Demanda("{p}")' for p in ("poleras", "polerones", "doble", "bolsas", "gorros")],
                         [f'x("{p}")' for p in ("poleras", "polerones", "doble", "bolsas", "gorros")])
    v = correr_opl("u12_planchado_parametrico.mod", "u12_estampa.dat")
    if v is not None:
        malos = [(h, v.get(f"margen_{h}h"), z, v.get(f"dual_planchado_{h}h"), y) for h, z, y in K["curva"]
                 if abs(v.get(f"margen_{h}h", 1e99) - z) > 1e-6 or abs(v.get(f"dual_planchado_{h}h", 1e99) - y) > 1e-9]
        print("   OPL caso paramétrico:", "coincide hora por hora" if not malos else f"NO {malos}"); ok &= not malos
    return ok


# ---------------------------------------------------------------- impresión

def imprimir(R, K):
    F = R["fig"]; print("== figura: planchado de", num(F["lo"]), "a", num(F["hi"]), "s; vértices", F["v_lo"], F["v_hi"],
                        "duales", [num(v) for v in F["S"]["y"]])
    S = R["ej"]["S"]
    print("== Ejemplo · z", num(S["z"]), "y", [num(v) for v in S["y"]], "d", [num(v) for v in S["d"]])
    print(tabla_final(S, ["$x_1$", "$x_2$", "$x_3$"], ["$s_1$", "$s_2$", "$s_3$"]))
    print(tabla_rangos(S, ["Tostadora (min)", "Envasadora (min)", "Bolsas"], ["Espresso", "Filtro", "Descafeinado"]))
    print("   tostadora 2.700 → xB", [num(v) for v in R["ej"]["xb_nuevo"]], "z", num(R["ej"]["z_nuevo"]))
    print("   orgánico: recursos valen", num(R["ej"]["valor_nueva"]), "cr", num(R["ej"]["cr_nueva"]), "→ nuevo óptimo",
          [num(v) for v in R["ej"]["S4"]["x"]], "z", num(R["ej"]["S4"]["z"]), "y", [num(v) for v in R["ej"]["S4"]["y"]])
    e1 = R["e1"]; print("== 12.1"); print(informe_solver(e1["S"], ["Etiqueta A", "Etiqueta B", "Etiqueta C"], ["Prensa (h)", "Adhesivo (m²)", "Troquel (h)"]))
    print("   prensa +100 →", num(e1["z_prensa"]), "| troquel −200 → real", num(e1["z_tr"]), "cota", num(e1["cota_tr"]), "| B −50.000 →", num(e1["z_bajab"]))
    e2 = R["e2"]; print("== 12.2/12.3", tabla_rangos(e2["S"], ["Tierra", "Agua", "Mano de obra"], ["Arándano", "Frambuesa"]),
                        "\n   vértices", e2["vert_lo"], e2["vert_hi"], "z tierra 30", num(e2["z_t30"]))
    e4 = R["e4"]; print("== 12.4 umbral mora", num(e4["umbral"]), "nuevo", [num(v) for v in e4["nuevo"]["x"]], num(e4["nuevo"]["z"]), [num(v) for v in e4["nuevo"]["y"]])
    e5 = R["e5"]; print("== 12.5"); print(tabla_final(e5["S"], ["$x_1$", "$x_2$", "$x_3$"], ["$s_1$", "$s_2$", "$s_3$"]))
    print(tabla_rangos(e5["S"], ["Leche", "Cámara", "Envasado"], ["Gauda", "Mantecoso", "Fresco"]))
    print("   B⁻¹", [[frac(v) for v in f] for f in e5["S"]["Bi"]], "base", e5["S"]["base"], "| envasado 290 →", [num(v) for v in e5["xb_nuevo"]], num(e5["z_nuevo"]))
    e7 = R["e7"]; print("== 12.7 valor", num(e7["valor"]), "cr", num(e7["cr"]), "nuevo", [num(v) for v in e7["Sn"]["x"]], num(e7["Sn"]["z"]), [num(v) for v in e7["Sn"]["y"]])
    print(tabla_rangos(e7["S"], ["Templado", "Envasado", "Tope clásica", "Tope surtida", "Tope trufas"], ["Clásica", "Surtida", "Trufas"]))
    e8 = R["e8"]; print("== 12.8"); print(informe_solver(e8["S"], ["Afrecho", "Pellet", "Maíz"], ["Proteína", "Energía", "Fibra"]))
    for k, v in R["e9"].items():
        print("== 12.9", k, "pct", num(v["pct"] * 100), "x", v["x"], "z", num(v["z"]), "mo", v["mo"])
    e10 = R["e10"]; print("== 12.10 rangos"); print(tabla_rangos(e10["S"], ["Horno", "Amasado", "Tope"], ["Hallulla", "Marraqueta"]))
    print("   curva", e10["curva"], "solo horno", e10["solo_horno"], "ambos", e10["ambos"])
    S = K["S"]; print("== CASO"); print(tabla_rangos(S, ["Estampado (s)", "Planchado (s)", "Tinta (g)", "Tope poleras", "Tope polerones",
                                                      "Tope doble", "Tope bolsas", "Tope gorros"], ["Poleras", "Polerones", "Doble", "Bolsas", "Gorros"]))
    print("   curva", [(h, num(z), num(y)) for h, z, y in K["curva"]])
    print("   hora planchado", num(K["valor_hora"]), "pérdida", num(K["perdida_hora"]), "rango h", [fmt(v, 2) for v in K["rango_h"]],
          "aumento", fmt(K["aumento_h"], 2), "sem6", num(K["sem6_margen"]), num(K["sem6_costo"]), num(K["sem6_neto"]), "estampado sobra h", fmt(K["estampado_h"], 2))


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R, K):
    e = []
    F = R["fig"]; e += [fmt(F["lo"]), fmt(F["hi"]), fmt(F["v_lo"][0]), "72.000", "u12_rango_planchado.svg"]
    S = R["ej"]["S"]
    e += [tabla_final(S, ["$x_1$", "$x_2$", "$x_3$"], ["$s_1$", "$s_2$", "$s_3$"])]
    e += [tabla_rangos(S, ["Tostadora (min)", "Envasadora (min)", "Bolsas"], ["Espresso", "Filtro", "Descafeinado"])]
    e += [num(v) for v in R["ej"]["xb_nuevo"]] + [pesos(R["ej"]["z_nuevo"]), pesos(R["ej"]["valor_nueva"]),
                                                 pesos(R["ej"]["S4"]["z"]), num(R["ej"]["S4"]["x"][2]), num(R["ej"]["S4"]["x"][3])]
    e1 = R["e1"]
    e += [informe_solver(e1["S"], ["Etiqueta A", "Etiqueta B", "Etiqueta C"], ["Prensa (h)", "Adhesivo (m²)", "Troquel (h)"])]
    e += [pesos(e1["z_prensa"]), pesos(e1["z_tr"]), pesos(e1["cota_tr"]), pesos(e1["z_bajab"])]
    e2 = R["e2"]; e += [num(e2["S"]["rhs"][0][0]), num(e2["S"]["rhs"][0][2]), pesos(e2["z_t30"]), pesos(e2["p_lo"]), pesos(e2["p_hi"]),
                        pesos(e2["S"]["y"][0]), pesos(e2["S"]["y"][1])]
    e4 = R["e4"]; e += [pesos(e4["umbral"]), pesos(e4["nuevo"]["z"]), num(e4["nuevo"]["x"][1]), num(e4["nuevo"]["x"][2])]
    e5 = R["e5"]
    e += [tabla_final(e5["S"], ["$x_1$", "$x_2$", "$x_3$"], ["$s_1$", "$s_2$", "$s_3$"])]
    e += [num(v) for v in e5["xb_nuevo"]] + [pesos(e5["z_nuevo"])]
    for k in (1, 2):
        e += [num(e5["S"]["rhs"][k][0]), num(e5["S"]["rhs"][k][2])]
    e += [pesos(e5["S"]["obj"][0][0]), pesos(e5["S"]["obj"][0][2]), pesos(e5["S"]["obj"][2][0], 2), pesos(e5["S"]["obj"][2][2])]
    e7 = R["e7"]; e += [pesos(e7["valor"]), pesos(e7["cr"]), pesos(e7["Sn"]["z"]), num(e7["Sn"]["x"][0])]
    e8 = R["e8"]; e += [informe_solver(e8["S"], ["Afrecho", "Pellet", "Maíz"], ["Proteína", "Energía", "Fibra"]),
                        pesos(e8["z_prot"]), pesos(e8["S"]["z"]), pesos(e8["S"]["obj"][1][2]), pesos(e8["S"]["obj"][0][0])]
    for v in R["e9"].values():
        e += [fmt(v["pct"] * 100, 1) + " %", pesos(v["z"])]
    e10 = R["e10"]
    e += [pesos(z) for _, _, z in e10["curva"]] + [pesos(e10["solo_horno"][1]), pesos(e10["ambos"][1])]
    S = K["S"]
    e += [tabla_rangos(S, ["Estampado (s)", "Planchado (s)", "Tinta (g)", "Tope poleras", "Tope polerones", "Tope doble",
                           "Tope bolsas", "Tope gorros"], ["Poleras básicas", "Polerones", "Estampado doble", "Bolsas", "Gorros"])]
    e += [pesos(K["valor_hora"]), pesos(K["hora_extra"]), pesos(K["perdida_hora"]), fmt(K["rango_h"][0], 2) + " h",
          fmt(K["rango_h"][1], 2) + " h", fmt(K["aumento_h"], 2) + " h", pesos(K["sem6_margen"]), pesos(K["sem6_costo"]),
          pesos(-K["sem6_neto"]), pesos(K["falta_doble"]), pesos(K["z_max_planchado"]), fmt(K["estampado_h"], 2) + " h"]
    e += ["| " + str(h) + " | " + pesos(z) + " | " + num(y) + " |" for h, z, y in K["curva"]]
    return e


def contra_u10(y):
    """Compara los duales de la mezcla (3 recursos y 5 cotas) con los que calcula la unidad 10."""
    ruta = AQUI / "u10_dualidad.py"
    if not ruta.exists():
        print("   unidad 10: todavía no hay verificador, no se compara")
        return True
    import contextlib, io
    spec = importlib.util.spec_from_file_location("u10", ruta)
    u10 = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.TextIOWrapper(io.BytesIO(), encoding="utf-8")):
        spec.loader.exec_module(u10)
        y10 = u10.resultados()["u4"]["y"]
    ok = len(y10) == len(y) and all(abs(float(a) - float(b)) < 1e-6 for a, b in zip(y10, y))
    print("   unidad 10:", "los duales de la mezcla coinciden" if ok else f"NO coinciden {list(map(float, y10))} vs {list(map(float, y))}")
    return ok


if __name__ == "__main__":
    caso = cargar_caso()
    R = resultados(caso)
    K = caso_u12(caso)
    imprimir(R, K)
    C = K["C"]
    ok = abs(float(K["valor_hora"]) - C["u12"]["valor_hora_planchado"]) < 1e-6 and \
        abs(float(K["S"]["y"][0]) * 3600 - C["u12"]["valor_hora_estampado"]) < 1e-6 and \
        (K["valor_hora"] > K["hora_extra"]) == C["u12"]["conviene_extra_planchado"] and \
        np.allclose([float(v) for v in K["S"]["x"]], C["u4"]["x"]) and abs(float(K["S"]["z"]) - C["u4"]["z"]) < 1e-6 and \
        contra_u10(K["S"]["y"])
    print("\nCADENA:", "OK, la hora de planchado vale lo que dice el caso y la decisión calza" if ok else "NO calza")
    if not ok:
        sys.exit(1)
    if not verificar_software(R, K):
        print("OPL/CPLEX: NO coincide"); sys.exit(1)
    if "--revisar" in sys.argv:
        md = (RAMO / "unidades" / "12-sensibilidad.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".").replace("\\$", "$")
        faltan = [x for x in esperados(R, K) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
