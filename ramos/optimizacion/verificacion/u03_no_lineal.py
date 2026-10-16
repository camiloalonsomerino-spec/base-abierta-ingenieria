"""Unidad 3 · Optimización no lineal básica. Recalcula todas las cifras; con --revisar las busca en el .md.

    python u03_no_lineal.py            # imprime los resultados, dibuja las figuras y compara con el caso
    python u03_no_lineal.py --revisar  # además busca cada cifra en unidades/03-no-lineal.md

Las cuentas usan fracciones exactas (fractions.Fraction) cuando los datos lo permiten; cada óptimo se
comprueba por un segundo camino (scipy.optimize). El precio de los polerones se resuelve también en OPL
(modelos/u03_precio_polerones.mod) si CPLEX está instalado. Todos los datos son originales.
"""
from fractions import Fraction as F
from pathlib import Path
import importlib.util, math, sys

import numpy as np
from scipy.optimize import minimize, minimize_scalar

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402


def fmt(x, dec=1):
    s = f"{float(x):,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x, 0)


# ------------------------------------------------------------------ datos (originales; pasados por colisiones.py)
# Ejemplo · invernadero: x = horas de abonado, y = horas de riego por semana; U en miles de pesos
INV = {"ax": 52, "ay": 82, "cxx": 2, "cyy": 3, "cxy": 1, "horas": 18}
E31 = {"a": (3, -12, 7), "b": (40, 6, F(-1, 2))}            # 3x²−12x+7 ; 40+6x−0,5x² ; x⁴
E32 = {"coef": (2, -15, 24, 10), "intervalo": (0, 6)}       # 2x³−15x²+24x+10
E33 = {"a": ((2, -2), (-2, 4)), "b": ((-6, 4), (4, -2)), "c": ((-2, 2), (2, -8)), "d": ((2, 4), (4, 8))}
E34 = {}                                                    # x²+3y²−2xy−4x+8y+5
E35 = {"a": 960, "b": F(32, 100), "c": 1150, "c2": 1390}
E36 = {"centro": (6, 5), "recta": (1, 2, 10), "centro_b": (2, 1)}
E37 = {"centro": (4, 0), "radio": 3, "tope": 10, "obj": (2, -3)}
E38 = {"a1": F(2, 100), "b1": 35, "a2": F(5, 100), "b2": 20, "total": 1200}
E39 = {"a1": 870, "a2": 690, "b11": F(24, 100), "b22": F(15, 100), "g": F(6, 100), "c1": 500, "c2": 1400}
E310 = {"a": 960, "b": F(32, 100), "c": 1150, "K": 240}


def caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_lp.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ cálculo
def precio_optimo(a, b, c):
    p = F(a) + b * c
    p = p / (2 * b)
    q = a - b * p
    return p, q, (p - c) * q


def resultados():
    R = {}
    # --- ejemplo
    d = INV
    H = np.array([[-2 * d["cxx"], -d["cxy"]], [-d["cxy"], -2 * d["cyy"]]])
    U = lambda x, y: d["ax"] * x + d["ay"] * y - d["cxx"] * x * x - d["cyy"] * y * y - d["cxy"] * x * y
    # ∇U = 0:  ax − 4x − y = 0 ; ay − x − 6y = 0
    A = [[F(2 * d["cxx"]), F(d["cxy"])], [F(d["cxy"]), F(2 * d["cyy"])]]
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    x0 = (d["ax"] * A[1][1] - A[0][1] * d["ay"]) / det
    y0 = (A[0][0] * d["ay"] - A[1][0] * d["ax"]) / det
    # con x + y = h : ∂U/∂x = ∂U/∂y = λ
    def con_h(h):
        # ax − 4x − y = ay − x − 6y  →  (ax − ay) − 3x + 5y = 0 ; y = h − x
        x = F(d["ax"] - d["ay"] + 5 * h, 8)
        y = h - x
        lam = d["ax"] - 2 * d["cxx"] * x - d["cxy"] * y
        return x, y, lam, U(x, y)
    xc, yc, lam, Uc = con_h(d["horas"])
    x19, y19, _, U19 = con_h(d["horas"] + 1)
    num = minimize(lambda v: -U(*v), [1, 1], constraints=[{"type": "ineq", "fun": lambda v: d["horas"] - v[0] - v[1]}],
                   bounds=[(0, None), (0, None)], method="SLSQP")
    assert abs(num.x[0] - float(xc)) < 1e-4 and abs(num.x[1] - float(yc)) < 1e-4
    R["ej"] = {"H11": H[0, 0], "H22": H[1, 1], "detH": float(det), "x0": x0, "y0": y0, "U0": U(x0, y0),
               "vert": {"(0, 0)": U(0, 0), "(18, 0)": U(18, 0), "(0, 18)": U(0, 18)},
               "xc": xc, "yc": yc, "lam": lam, "Uc": Uc, "costo_restr": U(x0, y0) - Uc,
               "x19": x19, "y19": y19, "U19": U19, "gana19": U19 - Uc}
    assert x0 + y0 > d["horas"]           # el óptimo libre no cabe en 18 h
    # --- 3.1
    a2, a1, a0 = E31["a"]
    xa = F(-a1, 2 * a2)
    b0, b1, b2 = E31["b"]
    xb = F(-b1) / (2 * b2)
    R["e31"] = {"xa": xa, "fa": a2 * xa ** 2 + a1 * xa + a0, "f2a": 2 * a2,
                "xb": xb, "gb": b0 + b1 * xb + b2 * xb ** 2, "g2b": 2 * b2}
    # --- 3.2
    c3, c2, c1, c0 = E32["coef"]
    h = lambda x: c3 * x ** 3 + c2 * x ** 2 + c1 * x + c0
    disc = (2 * c2) ** 2 - 4 * (3 * c3) * c1
    r1 = F(-2 * c2 - int(math.isqrt(disc)), 6 * c3)
    r2 = F(-2 * c2 + int(math.isqrt(disc)), 6 * c3)
    lo, hi = E32["intervalo"]
    cand = {x: h(x) for x in (lo, r1, r2, hi)}
    R["e32"] = {"r1": r1, "r2": r2, "h1": h(r1), "h2": h(r2), "infl": F(-c2, 3 * c3), "h_lo": h(lo), "h_hi": h(hi),
                "max": max(cand.items(), key=lambda kv: kv[1]), "min": min(cand.items(), key=lambda kv: kv[1]),
                "h2pp1": 6 * c3 * r1 + 2 * c2, "h2pp2": 6 * c3 * r2 + 2 * c2}
    # --- 3.3
    R["e33"] = {k: (m[0][0] * m[1][1] - m[0][1] * m[1][0]) for k, m in E33.items()}
    # --- 3.4 : 2x − 2y − 4 = 0 ; −2x + 6y + 8 = 0
    M = np.array([[2, -2], [-2, 6]], float)
    x34, y34 = np.linalg.solve(M, [4, -8])
    f34 = lambda x, y: x * x + 3 * y * y - 2 * x * y - 4 * x + 8 * y + 5
    R["e34"] = {"x": round(x34, 9), "y": round(y34, 9), "f": f34(x34, y34), "det": 2 * 6 - 4}
    # --- 3.5
    p, q, u = precio_optimo(E35["a"], E35["b"], E35["c"])
    p2, q2, u2 = precio_optimo(E35["a"], E35["b"], E35["c2"])
    num = minimize_scalar(lambda x: -(x - E35["c"]) * (E35["a"] - float(E35["b"]) * x), bounds=(E35["c"], 3000), method="bounded")
    assert abs(num.x - float(p)) < 1e-3
    R["e35"] = {"p": p, "q": q, "u": u, "upp": -2 * E35["b"], "p2": p2, "q2": q2, "u2": u2, "dp": p2 - p}
    # --- 3.6
    cx, cy = E36["centro"]; a, b, rhs = E36["recta"]
    t = F(a * cx + b * cy - rhs, a * a + b * b)
    px, py = cx - t * a, cy - t * b
    f36 = lambda x, y: (x - cx) ** 2 + (y - cy) ** 2
    R["e36"] = {"x": px, "y": py, "f": f36(px, py), "mult": 2 * (cx - px),
                "vert": {"(0, 0)": f36(0, 0), "(10, 0)": f36(10, 0), "(0, 5)": f36(0, 5)},
                "fb": (E36["centro_b"][0] - E36["centro_b"][0]) ** 2}
    assert a * cx + b * cy > rhs and px >= 0 and py >= 0
    # --- 3.7
    (ox, oy), r, top = E37["centro"], E37["radio"], E37["tope"]
    zf = lambda x, y: E37["obj"][0] * x + E37["obj"][1] * y
    izq = ox - r
    # fuerza bruta en una grilla fina: el máximo global y que el punto (1, 0) es máximo local
    g = np.linspace(0, top, 2001)
    X, Y = np.meshgrid(g, g)
    fact = ((X - ox) ** 2 + (Y - oy) ** 2 >= r * r - 1e-9) & (X + Y <= top + 1e-9)
    Z = np.where(fact, 2 * X - 3 * Y, -np.inf)
    k = np.unravel_index(np.argmax(Z), Z.shape)
    assert abs(X[k] - top) < 1e-9 and abs(Y[k]) < 1e-9
    vec = fact & ((X - izq) ** 2 + Y ** 2 <= 0.25)
    assert Z[vec].max() <= zf(izq, 0) + 1e-9
    R["e37"] = {"local": (izq, 0, zf(izq, 0)), "global": (top, 0, zf(top, 0)), "der": ox + r, "medio": (ox, oy)}
    # --- 3.8 : a1 q1² + b1 q1 + a2 q2² + b2 q2 con q1 + q2 = total
    d8 = E38
    q1 = (2 * d8["a2"] * d8["total"] + d8["b2"] - d8["b1"]) / (2 * d8["a1"] + 2 * d8["a2"])
    q2_ = d8["total"] - q1
    lam8 = 2 * d8["a1"] * q1 + d8["b1"]
    C1 = d8["a1"] * q1 ** 2 + d8["b1"] * q1
    C2 = d8["a2"] * q2_ ** 2 + d8["b2"] * q2_
    assert lam8 == 2 * d8["a2"] * q2_ + d8["b2"]
    R["e38"] = {"q1": q1, "q2": q2_, "lam": lam8, "C1": C1, "C2": C2, "C": C1 + C2}
    # --- 3.9
    d9 = E39
    b11, b22, g9 = d9["b11"], d9["b22"], d9["g"]
    # conjunto: [2b11 2g; 2g 2b22] p = [a1 + b11 c1 + g c2 ; a2 + b22 c2 + g c1]
    def resolver(m11, m12, m21, m22, r1_, r2_):
        dd = m11 * m22 - m12 * m21
        return (r1_ * m22 - m12 * r2_) / dd, (m11 * r2_ - m21 * r1_) / dd
    p1, p2_ = resolver(2 * b11, 2 * g9, 2 * g9, 2 * b22, d9["a1"] + b11 * d9["c1"] + g9 * d9["c2"],
                       d9["a2"] + b22 * d9["c2"] + g9 * d9["c1"])
    dem = lambda x1, x2: (d9["a1"] - b11 * x1 - g9 * x2, d9["a2"] - b22 * x2 - g9 * x1)
    util = lambda x1, x2: (x1 - d9["c1"]) * dem(x1, x2)[0] + (x2 - d9["c2"]) * dem(x1, x2)[1]
    s1, s2 = resolver(2 * b11, g9, g9, 2 * b22, d9["a1"] + b11 * d9["c1"], d9["a2"] + b22 * d9["c2"])
    num = minimize(lambda v: -float(util(F(v[0]), F(v[1]))), [1000, 2000], method="Nelder-Mead",
                   options={"xatol": 1e-6, "fatol": 1e-6, "maxiter": 4000})
    assert abs(num.x[0] - float(p1)) < 1e-2 and abs(num.x[1] - float(p2_)) < 1e-2
    R["e39"] = {"p1": p1, "p2": p2_, "q1": dem(p1, p2_)[0], "q2": dem(p1, p2_)[1], "u": util(p1, p2_),
                "H11": -2 * b11, "H22": -2 * b22, "H12": -2 * g9, "det": 4 * b11 * b22 - 4 * g9 * g9,
                "s1": s1, "s2": s2, "sq1": dem(s1, s2)[0], "sq2": dem(s1, s2)[1], "su": util(s1, s2),
                "pierde": util(p1, p2_) - util(s1, s2)}
    # --- 3.10 : en la variable q, p = (a − q)/b
    d10 = E310
    pq = lambda qq: (d10["a"] - qq) / d10["b"]
    pi = lambda qq: (pq(qq) - d10["c"]) * qq
    dpi = lambda qq: (d10["a"] - 2 * qq) / d10["b"] - d10["c"]
    qlib = (d10["a"] - d10["b"] * d10["c"]) / 2
    R["e310"] = {"qlib": qlib, "K": d10["K"], "p": pq(d10["K"]), "pi": pi(d10["K"]), "mu": dpi(d10["K"]),
                 "pi_lib": pi(qlib), "gana": pi(qlib) - pi(d10["K"]), "pend_q": 1 / d10["b"]}
    assert qlib > d10["K"] and dpi(d10["K"]) > 0
    # --- caso
    m = caso()
    a, b, cv = m.U3["a"], F(m.U3["b"]).limit_denominator(10000), m.U3["costo"]
    p, q, u = precio_optimo(a, b, cv)
    p_hoy = cv + m.MARGEN[1]
    q_hoy = a - b * p_hoy
    R["caso"] = {"a": a, "b": b, "costo": cv, "p": p, "q": q, "u": u, "upp": -2 * b, "margen": p - cv,
                 "p_hoy": p_hoy, "q_hoy": q_hoy, "u_hoy": (p_hoy - cv) * q_hoy, "gana": u - (p_hoy - cv) * q_hoy,
                 "q_costo": a - b * cv, "p_max": F(a) / b, "dem_u2": m.DOS["dem_polerones"],
                 "margen_u2": m.MARGEN[1], "dem_u4": m.DEMANDA_MAX[1]}
    return R


# ------------------------------------------------------------------ figuras (SVG)
TINTA, SUAVE, LINEA, PAPEL, ACENTO, AZUL = "#2B2F33", "#5F656B", "#D6D3CE", "#F2F1EF", "#E2622A", "#2F6F8F"


class Lienzo:
    def __init__(self, ancho, alto, xr, yr, margen=(52, 18, 34, 40)):
        self.w, self.h, self.xr, self.yr = ancho, alto, xr, yr
        self.ml, self.mr, self.mt, self.mb = margen
        self.el = []

    def X(self, x):
        return self.ml + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * (self.w - self.ml - self.mr)

    def Y(self, y):
        return self.h - self.mb - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * (self.h - self.mt - self.mb)

    def poli(self, pts, cerrado=False, recorte=True, **kw):
        s = " ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in pts)
        tag = "polygon" if cerrado else "polyline"
        attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
        clip = ' clip-path="url(#area)"' if recorte else ""
        self.el.append(f'<{tag} points="{s}" {attrs}{clip}/>')

    def punto(self, x, y, r=4.5, color=ACENTO):
        self.el.append(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" fill="{color}" stroke="white" stroke-width="1.2"/>')

    def texto(self, x, y, t, dx=0, dy=0, size=12, color=TINTA, anchor="start", peso="normal"):
        self.el.append(f'<text x="{self.X(x) + dx:.1f}" y="{self.Y(y) + dy:.1f}" font-size="{size}" fill="{color}" '
                       f'text-anchor="{anchor}" font-weight="{peso}" paint-order="stroke" stroke="white" stroke-width="3">{t}</text>')

    def ejes(self, xt, yt, xl, yl, fx=lambda v: fmt(v, 0), fy=lambda v: fmt(v, 0)):
        x0, y0 = self.xr[0], self.yr[0]
        for v in xt:
            self.el.append(f'<line x1="{self.X(v):.1f}" y1="{self.Y(y0):.1f}" x2="{self.X(v):.1f}" y2="{self.Y(self.yr[1]):.1f}" stroke="{LINEA}" stroke-width="0.6"/>')
            self.texto(v, y0, fx(v), dy=16, size=11, color=SUAVE, anchor="middle")
        for v in yt:
            self.el.append(f'<line x1="{self.X(x0):.1f}" y1="{self.Y(v):.1f}" x2="{self.X(self.xr[1]):.1f}" y2="{self.Y(v):.1f}" stroke="{LINEA}" stroke-width="0.6"/>')
            self.texto(x0, v, fy(v), dx=-6, dy=4, size=11, color=SUAVE, anchor="end")
        self.poli([(x0, self.yr[1]), (x0, y0), (self.xr[1], y0)], recorte=False, fill="none", stroke=TINTA, stroke_width=1.2)
        self.texto(self.xr[1], y0, xl, dy=32, size=12, anchor="end")
        self.el.append(f'<text x="{self.ml - 40}" y="{self.mt - 12}" font-size="12" fill="{TINTA}">{yl}</text>')

    def guardar(self, ruta):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
               f'font-family="Segoe UI, Arial, sans-serif"><rect width="100%" height="100%" fill="white"/>'
               f'<defs><clipPath id="area"><rect x="{self.ml}" y="{self.mt}" width="{self.w - self.ml - self.mr}" '
               f'height="{self.h - self.mt - self.mb}"/></clipPath></defs>'
               + "".join(self.el) + "</svg>\n")
        Path(ruta).write_text(svg, encoding="utf-8")


def elipse(c, Q, k, n=240):
    """Puntos de dᵀQd = k alrededor de c."""
    lam, V = np.linalg.eigh(np.array(Q, float))
    t = np.linspace(0, 2 * math.pi, n)
    D = V @ np.vstack([np.sqrt(k / lam[0]) * np.cos(t), np.sqrt(k / lam[1]) * np.sin(t)])
    return [(c[0] + D[0, i], c[1] + D[1, i]) for i in range(n)]


def figuras(R):
    carpeta = RAMO / "unidades" / "figuras"
    carpeta.mkdir(parents=True, exist_ok=True)
    # 1 · convexa y cóncava
    L = Lienzo(640, 250, (0, 13), (0, 10), margen=(20, 20, 20, 30))
    f = lambda x: 0.22 * (x - 3.2) ** 2 + 1.2
    xs = np.linspace(0.3, 6.1, 80)
    L.poli([(x, f(x)) for x in xs], fill="none", stroke=AZUL, stroke_width=2.4)
    L.poli([(1, f(1)), (5.6, f(5.6))], fill="none", stroke=ACENTO, stroke_width=1.6, stroke_dasharray="5,4")
    L.punto(1, f(1)); L.punto(5.6, f(5.6))
    L.texto(3.2, 0.2, "convexa: la cuerda queda arriba", size=12, anchor="middle")
    g = lambda x: -0.22 * (x - 9.8) ** 2 + 8.4
    xs = np.linspace(6.9, 12.7, 80)
    L.poli([(x, g(x)) for x in xs], fill="none", stroke=AZUL, stroke_width=2.4)
    L.poli([(7.4, g(7.4)), (12, g(12))], fill="none", stroke=ACENTO, stroke_width=1.6, stroke_dasharray="5,4")
    L.punto(7.4, g(7.4)); L.punto(12, g(12))
    L.texto(9.8, 0.2, "cóncava: la cuerda queda abajo", size=12, anchor="middle")
    L.guardar(carpeta / "u03_convexa_concava.svg")

    # 2 · invernadero
    e = R["ej"]
    L = Lienzo(560, 470, (0, 20), (0, 20))
    L.ejes(range(0, 21, 2), range(0, 21, 2), "x · horas de abonado", "y · horas de riego")
    L.poli([(0, 0), (18, 0), (0, 18)], cerrado=True, fill="#FBE3D6", stroke="none")
    L.poli([(0, 18), (18, 0)], fill="none", stroke=ACENTO, stroke_width=2)
    L.texto(16.6, 1.0, "x + y = 18", size=12, color=ACENTO)
    Q = [[2, 0.5], [0.5, 3]]
    c = (float(e["x0"]), float(e["y0"]))
    for nivel in (729, 690, 620, 520):
        k = float(e["U0"]) - nivel
        L.poli(elipse(c, Q, k), fill="none", stroke=AZUL, stroke_width=1.3 if nivel != 729 else 2.2)
        px, py = elipse(c, Q, k, 8)[1]
        L.texto(c[0] + math.sqrt(k / 2) * 0.73, c[1] + math.sqrt(k / 3) * 0.72, f"U = {nivel}", dx=6, size=11, color=AZUL)
    L.punto(*c, color=AZUL)
    L.texto(*c, "(10, 12) · U = 752, no cabe", dx=8, dy=-10, size=12)
    L.punto(float(e["xc"]), float(e["yc"]))
    L.texto(float(e["xc"]), float(e["yc"]), "(7,5; 10,5) · U = 729", dx=-8, dy=20, size=12, anchor="end", peso="bold")
    L.texto(4, 4, "región factible", size=12, color=SUAVE)
    L.guardar(carpeta / "u03_invernadero.svg")

    # 3 · precio de los polerones
    k = R["caso"]
    a, b, cv = k["a"], float(k["b"]), k["costo"]
    L = Lienzo(600, 330, (6000, 18000), (0, 4.2))
    L.ejes(range(6000, 18001, 2000), [0, 1, 2, 3, 4], "precio del polerón (CLP)", "utilidad semanal (millones de CLP)",
           fx=lambda v: fmt(v, 0), fy=lambda v: fmt(v, 0))
    ps = np.linspace(cv, a / b, 120)
    L.poli([(p, (p - cv) * (a - b * p) / 1e6) for p in ps], fill="none", stroke=AZUL, stroke_width=2.4)
    L.punto(float(k["p"]), float(k["u"]) / 1e6)
    L.texto(float(k["p"]), float(k["u"]) / 1e6, "óptimo: $11.825 · $3.607.030", dy=-12, size=12, anchor="middle", peso="bold")
    L.punto(float(k["p_hoy"]), float(k["u_hoy"]) / 1e6, color=AZUL)
    L.texto(float(k["p_hoy"]), float(k["u_hoy"]) / 1e6, "hoy: $10.090 · $3.269.885", dx=-8, dy=22, size=12, anchor="end")
    L.guardar(carpeta / "u03_precio_polerones.svg")

    # 4 · ejercicio 3.7: región no convexa
    d = R["e37"]
    L = Lienzo(520, 420, (0, 10.5), (0, 10.5))
    L.ejes(range(0, 11, 1), range(0, 11, 1), "x", "y")
    L.poli([(0, 0), (10, 0), (0, 10)], cerrado=True, fill="#FBE3D6", stroke=TINTA, stroke_width=1.2)
    t = np.linspace(0, math.pi, 120)
    L.poli([(4 + 3 * math.cos(s), 3 * math.sin(s)) for s in t], cerrado=True, fill="white", stroke=AZUL, stroke_width=2)
    L.texto(4, 1.1, "círculo excluido", size=12, color=AZUL, anchor="middle")
    for z0, xa in ((2, -0.2), (20, 9.4)):
        L.poli([(xa, (2 * xa - z0) / 3), (xa + 1.5, (2 * (xa + 1.5) - z0) / 3)], fill="none", stroke=ACENTO,
               stroke_width=1.4, stroke_dasharray="5,4")
    L.punto(1, 0); L.texto(1, 0, "(1, 0) · z = 2, local", dx=-4, dy=-12, size=12, anchor="end")
    L.punto(10, 0); L.texto(10, 0, "(10, 0) · z = 20, global", dx=-6, dy=-12, size=12, anchor="end", peso="bold")
    L.punto(4, 0, color=AZUL); L.texto(4, 0, "(4, 0) no factible", dy=-8, size=11, color=AZUL, anchor="middle")
    L.guardar(carpeta / "u03_e37_region.svg")


# ------------------------------------------------------------------ OPL
def opl(R):
    r = correr(RAMO / "modelos" / "u03_precio_polerones.mod")
    if r is None:
        print("OPL: no instalado; se sigue con Python")
        return True
    v = r["valores"]
    k = R["caso"]
    ok = abs(v["precio"] - float(k["p"])) < 1e-3 and abs(v["cantidad"] - float(k["q"])) < 1e-3 \
        and abs(v["utilidad"] - float(k["u"])) < 1e-2
    print("OPL:", "OK, CPLEX da el mismo precio, cantidad y utilidad" if ok else f"NO coincide: {v}")
    return ok


# ------------------------------------------------------------------ cadena
def cadena(R):
    C = caso().calcular()["u3"]
    k = R["caso"]
    ok = all(abs(float(k[a]) - C[b]) < 1e-6 for a, b in
             (("p", "precio_optimo"), ("q", "cantidad"), ("u", "utilidad"), ("upp", "segunda_derivada")))
    ok = ok and abs(C["precio_numerico"] - float(k["p"])) < 1e-3
    print("CADENA:", "OK, la pieza del caso calza (precio, cantidad, utilidad y segunda derivada)" if ok else "NO calza")
    return ok


# ------------------------------------------------------------------ esperados
def esperados(R):
    e, k = R["ej"], R["caso"]
    E = ["-4", "-6", "= 23", "(10, 12)", "752", "288", "504", "7,5", "10,5", "11,5", "729", "23 mil",
         fmt(e["x19"], 3), fmt(e["y19"], 3), fmt(e["U19"], 2), fmt(e["gana19"], 2),
         "figuras/u03_convexa_concava.svg", "figuras/u03_invernadero.svg", "figuras/u03_precio_polerones.svg",
         "figuras/u03_e37_region.svg"]
    a = R["e31"]
    E += [f"x = {fmt(a['xa'], 0)}", f"f(2) = {fmt(a['fa'], 0)}", f"x = {fmt(a['xb'], 0)}", f"g(6) = {fmt(a['gb'], 0)}"]
    b = R["e32"]
    E += [f"h(1) = {fmt(b['h1'], 0)}", f"h(4) = {fmt(b['h2'], 0)}", fmt(b["infl"], 1), f"h(0) = {fmt(b['h_lo'], 0)}",
          f"h(6) = {fmt(b['h_hi'], 0)}", f"h''(1) = {fmt(b['h2pp1'], 0)}", f"h''(4) = {fmt(b['h2pp2'], 0)}"]
    E += [f"\\det H = {fmt(v, 0)}" for v in R["e33"].values()]
    c = R["e34"]
    E += [f"({fmt(c['x'], 0)}, {fmt(c['y'], 0)})", f"f(1, -1) = {fmt(c['f'], 0)}", f"\\det H = {fmt(c['det'], 0)}"]
    d = R["e35"]
    E += [pesos(d["p"]), fmt(d["q"], 0) + " unidades", pesos(d["u"]), fmt(d["upp"], 2), pesos(d["p2"]), pesos(d["dp"]),
          fmt(d["q2"], 1), pesos(d["u2"])]
    f = R["e36"]
    E += [f"({fmt(f['x'], 1)}; {fmt(f['y'], 1)})", fmt(f["f"], 1), fmt(f["mult"], 1)] + [fmt(v, 0) for v in f["vert"].values()]
    g = R["e37"]
    E += ["(1, 0)", "z = 2", "(10, 0)", "z = 20", "(7, 0)", "(4, 0)"]
    h = R["e38"]
    E += [fmt(h["q1"], 0), fmt(h["q2"], 0), pesos(h["lam"]), pesos(h["C1"]), pesos(h["C2"]), pesos(h["C"])]
    i = R["e39"]
    E += [pesos(i["p1"]), pesos(i["p2"]), fmt(i["q1"], 0), fmt(i["q2"], 0), pesos(i["u"]), fmt(i["det"], 4),
          pesos(i["s1"]), pesos(i["s2"]), fmt(i["sq1"], 1), fmt(i["sq2"], 1), pesos(i["su"]), pesos(i["pierde"])]
    j = R["e310"]
    E += [fmt(j["qlib"], 0), pesos(j["p"]), pesos(j["pi"]), pesos(j["mu"]), pesos(j["pi_lib"]), pesos(j["gana"]),
          fmt(j["pend_q"], 3)]
    # cifras derivadas que el texto menciona de paso
    peor_vertice = 1 - max(e["vert"].values()) / e["Uc"]
    E += [fmt(100 * peor_vertice, 0) + " %", f"unos {fmt(k['q_hoy'] - k['q'], 0)} polerones",
          f"{fmt(j['qlib'] - j['K'], 0)} \\times {fmt(j['mu'], 0)}"]
    assert (j["qlib"] - j["K"]) * j["mu"] > j["gana"]
    assert R["e36"]["vert"]["(0, 5)"] == 5 * R["e36"]["f"] and R["e37"]["global"][2] == 10 * R["e37"]["local"][2]
    E += [pesos(k["p"]), fmt(k["q"], 1), pesos(k["u"]), fmt(k["upp"], 3), pesos(k["margen"]), pesos(k["p_hoy"]),
          fmt(k["q_hoy"], 2), pesos(k["u_hoy"]), pesos(k["gana"]), fmt(k["q_costo"], 1), pesos(k["p_max"]),
          fmt(k["dem_u4"], 0), pesos(k["costo"]), "1.960 − 0,112"]
    return E


def imprimir(R):
    for bloque, v in R.items():
        print(f"== {bloque}")
        for kk, vv in v.items():
            if isinstance(vv, F):
                vv = f"{vv} ≈ {float(vv):.4f}"
            print(f"   {kk}: {vv}")


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    figuras(R)
    ok = opl(R)
    if not cadena(R) or not ok:
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (RAMO / "unidades" / "03-no-lineal.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
