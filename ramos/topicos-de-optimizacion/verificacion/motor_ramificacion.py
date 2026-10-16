"""Motor de las unidades 5 y 6 de Tópicos de Optimización: ramificación y acotamiento, planos cortantes.

Todo en fracciones exactas (fractions.Fraction), para que las tablas y los árboles del texto salgan tal
cual los escribiría alguien a mano. Lo usan `u05_ramificacion.py` y `u06_planos_cortantes.py`.

- `lp2`: relajación lineal de un problema de dos variables por enumeración de vértices (máx. o mín.).
- `rya2`: ramificación y acotamiento sobre dos variables (puras o mixtas), en profundidad o mejor primero.
- `mochila_lp` y `rya_mochila`: la mochila binaria con su relajación por ranking.
- `traza`: incumbente, mejor cota abierta (con herencia de cota) y gap después de cada PL.
- `Tabla`: tabla simplex con fila z en la convención del curso (z_j − c_j), pivoteo, simplex dual
  y cortes de Gomory.
- `arbol_svg` y `Lienzo`: figuras SVG.
"""
from fractions import Fraction as F
from itertools import combinations, product
import math

INF = None


# ---------------------------------------------------------------- formato chileno
def fmt(x, dec=0):
    s = f"{float(x):,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x, dec=0):
    return ("−" if x < 0 else "") + "$" + fmt(abs(x), dec)


def pct(x, dec=2):
    return fmt(100 * x, dec) + " %"


def fr(x):
    """Fracción exacta a texto: 12 · 8/3 · −5/12 · 1.200."""
    x = F(x)
    s = "−" if x < 0 else ""
    x = abs(x)
    if x.denominator == 1:
        return s + fmt(x.numerator)
    return f"{s}{x.numerator}/{x.denominator}"


def num(x, maxdec=2):
    """Entero si lo es; si no, con los decimales justos (hasta maxdec), coma decimal."""
    x = float(x)
    if abs(x - round(x)) < 1e-9:
        return fmt(round(x), 0)
    for d in range(1, maxdec + 1):
        if abs(x - round(x, d)) < 1e-9:
            return fmt(x, d)
    return fmt(x, maxdec)


def vec(x):
    return "(" + "; ".join(fr(v) for v in x) + ")"


def frac(q):
    """Parte fraccionaria en [0, 1): frac(−5/12) = 7/12."""
    q = F(q)
    return q - math.floor(q)


# ---------------------------------------------------------------- relajación de dos variables
def lp2(c, filas, sentido="max"):
    """Óptimo de c·x sobre {a1 x1 + a2 x2 <= b} (las filas incluyen x >= 0). (z, (x1, x2)) o None.
    Con óptimos alternativos devuelve el vértice de mayor x1 (y luego mayor x2)."""
    sg = 1 if sentido == "max" else -1
    best = None
    for a, b in combinations(filas, 2):
        d = a[0] * b[1] - a[1] * b[0]
        if d == 0:
            continue
        x1 = F(a[2] * b[1] - a[1] * b[2], d)
        x2 = F(a[0] * b[2] - a[2] * b[0], d)
        if all(f[0] * x1 + f[1] * x2 <= f[2] for f in filas):
            z = c[0] * x1 + c[1] * x2
            clave = (sg * z, x1, x2)
            if best is None or clave > best[0]:
                best = (clave, (z, (x1, x2)))
    return None if best is None else best[1]


def vertices(filas):
    V = set()
    for a, b in combinations(filas, 2):
        d = a[0] * b[1] - a[1] * b[0]
        if d == 0:
            continue
        x1 = F(a[2] * b[1] - a[1] * b[2], d)
        x2 = F(a[0] * b[2] - a[2] * b[0], d)
        if all(f[0] * x1 + f[1] * x2 <= f[2] for f in filas):
            V.add((x1, x2))
    return V


def enteros(filas, hasta=60):
    return [(i, j) for i in range(hasta + 1) for j in range(hasta + 1)
            if all(f[0] * i + f[1] * j <= f[2] for f in filas)]


def mejor_entero(c, filas, sentido="max", hasta=60, enteras=(0, 1)):
    """Fuerza bruta: el óptimo entero (si una variable es continua, se resuelve su PL para cada valor)."""
    sg = 1 if sentido == "max" else -1
    best = None
    if set(enteras) == {0, 1}:
        for p in enteros(filas, hasta):
            z = c[0] * p[0] + c[1] * p[1]
            if best is None or sg * z > sg * best[0]:
                best = (z, p)
        return best
    j = enteras[0]
    for v in range(hasta + 1):
        e = [0, 0]; e[j] = 1
        s = lp2(c, filas + [(e[0], e[1], v), (-e[0], -e[1], -v)], sentido)
        if s and (best is None or sg * s[0] > sg * best[0]):
            best = s
    return best


def fila_txt(f, n=("x_1", "x_2")):
    """(1, 0, 12) → 'x_1 \\le 12'; (0, -1, -3) → 'x_2 \\ge 3' (para cotas de rama)."""
    a1, a2, b = f
    if a1 == 0 and a2 in (1, -1):
        return f"{n[1]} \\le {fr(b)}" if a2 == 1 else f"{n[1]} \\ge {fr(-b)}"
    if a2 == 0 and a1 in (1, -1):
        return f"{n[0]} \\le {fr(b)}" if a1 == 1 else f"{n[0]} \\ge {fr(-b)}"
    raise ValueError(f)


def rama_txt(f, n=("x₁", "x₂")):
    return fila_txt(f, n).replace("\\le", "≤").replace("\\ge", "≥")


# ---------------------------------------------------------------- ramificación y acotamiento (dos variables)
def elegir(x, enteras, regla):
    fracc = [j for j in enteras if F(x[j]).denominator != 1]
    if not fracc:
        return None
    if regla == "x1":
        return fracc[0]
    if regla == "frac":        # la más fraccional (parte fraccionaria más cerca de 1/2); empate: x1
        return min(fracc, key=lambda j: (abs(frac(x[j]) - F(1, 2)), j))
    if regla == "cerca":       # la más cercana a un entero
        return min(fracc, key=lambda j: (min(frac(x[j]), 1 - frac(x[j])), j))
    raise ValueError(regla)


def rya2(c, filas, sentido="max", estrategia="profundidad", primero="le", regla="frac", enteras=(0, 1)):
    """Ramificación y acotamiento sobre dos variables. Numera los PL en el orden en que se resuelven.

    profundidad: tras ramificar se resuelve el hijo `primero` ('le' = x ≤ ⌊v⌋, 'ge' = x ≥ ⌊v⌋+1) y se
    sigue bajando; al cerrar una rama se vuelve al último hijo pendiente (pila). Los pendientes
    heredan la cota de su padre.
    mejor: al ramificar se resuelven los dos hijos ('primero' antes) y se ramifica el nodo abierto
    de mejor cota (empate: el de menor número).
    Poda por cota: máx. si z ≤ incumbente; mín. si z ≥ incumbente."""
    def resolver(ramas):
        return lp2(c, filas + ramas, sentido)

    def ramas_de(nd):
        j = elegir(nd["x"], enteras, regla)
        v = math.floor(nd["x"][j])
        e = [0, 0]; e[j] = 1
        nd["var"], nd["corte_en"] = j, v
        le = (e[0], e[1], v); ge = (-e[0], -e[1], -(v + 1))
        return [le, ge] if primero == "le" else [ge, le]

    def es_entera(nd):
        return elegir(nd["x"], enteras, regla) is None

    return _rya(resolver, ramas_de, es_entera, sentido, estrategia)


def _rya(resolver, ramas_de, es_entera, sentido, estrategia):
    """Esqueleto común. Cada nodo guarda sus ramas acumuladas; `registro` guarda, después de cada PL,
    la incumbente y las cotas de los nodos abiertos o pendientes (los pendientes con la de su padre)."""
    sg = 1 if sentido == "max" else -1
    N, registro = [], []
    inc = None
    pendientes = []          # (ramas, padre, rótulo) creados y sin resolver
    abiertos = []            # resueltos, fraccionales, sin ramificar (solo en «mejor primero»)

    def nuevo(ramas, padre, rot):
        s = resolver(ramas)
        nd = {"k": len(N), "ramas": ramas, "padre": padre, "rotulo": rot, "sol": s, "estado": None,
              "z": None if s is None else s[0], "x": None if s is None else s[1]}
        N.append(nd)
        nonlocal inc
        if s is None:
            nd["estado"] = "infactible"
        elif inc is not None and sg * nd["z"] <= sg * inc[0]:
            nd["estado"] = "cota"
        elif es_entera(nd):
            nd["estado"] = "entera"; nd["nueva"] = inc is not None
            inc = (nd["z"], nd["x"], nd["k"])
        else:
            nd["estado"] = "abierto"
        return nd

    def ramificar(nd):
        nd["estado"] = "ramificado"
        return [(nd["ramas"] + [r], nd["k"], r) for r in ramas_de(nd)]

    def anotar(k):
        cotas = [N[p]["z"] for _, p, _ in pendientes] + [n["z"] for n in abiertos]
        if inc is not None:
            cotas.append(inc[0])
        cota = (max(cotas) if sg == 1 else min(cotas)) if cotas else None
        registro.append({"k": k, "inc": None if inc is None else inc[0], "cota": cota,
                         "pendientes": [p for _, p, _ in pendientes], "abiertos": [n["k"] for n in abiertos]})

    raiz = nuevo([], None, None)
    if estrategia == "profundidad":
        if raiz["estado"] == "abierto":
            pendientes += list(reversed(ramificar(raiz)))
        anotar(0)
        while pendientes:
            ramas, p, r = pendientes.pop()
            nd = nuevo(ramas, p, r)
            if nd["estado"] == "abierto":
                pendientes += list(reversed(ramificar(nd)))
            anotar(nd["k"])
    elif estrategia == "mejor":
        if raiz["estado"] == "abierto":
            abiertos.append(raiz)
        anotar(0)
        while abiertos:
            nd = max(abiertos, key=lambda n: (sg * n["z"], -n["k"]))
            abiertos.remove(nd)
            hs = ramificar(nd)
            pendientes += list(reversed(hs))
            while pendientes:
                ramas, p, r = pendientes.pop()
                h = nuevo(ramas, p, r)
                if h["estado"] == "abierto":
                    abiertos.append(h)
                for a in list(abiertos):          # una incumbente nueva poda a los abiertos que ya no la superan
                    if inc is not None and sg * a["z"] <= sg * inc[0]:
                        abiertos.remove(a); a["estado"] = "cota_tardia"; a["podado_tras"] = h["k"]
                anotar(h["k"])
    else:
        raise ValueError(estrategia)
    return {"nodos": N, "inc": inc, "sentido": sentido, "registro": registro, "estrategia": estrategia}


# ---------------------------------------------------------------- mochila binaria
def mochila_lp(v, a, cap, fijas):
    """Relajación de la mochila con algunas variables fijas en 0 o 1, por ranking v/a (mayor primero).
    Devuelve (z, x) o None si lo fijado en 1 ya no cabe."""
    n = len(v)
    x = [F(0)] * n
    libre = F(cap)
    for j, val in fijas.items():
        x[j] = F(val)
        libre -= a[j] * val
    if libre < 0:
        return None
    orden = sorted([j for j in range(n) if j not in fijas], key=lambda j: (-F(v[j], a[j]), j))
    for j in orden:
        if a[j] <= libre:
            x[j] = F(1); libre -= a[j]
        else:
            x[j] = libre / a[j]; libre = F(0)
            break
    return sum(F(v[j]) * x[j] for j in range(n)), tuple(x)


def rya_mochila(v, a, cap, estrategia="profundidad", primero=1):
    """Ramificación y acotamiento de la mochila binaria (máx.). Se ramifica en la única fraccional;
    `primero` dice qué hijo se resuelve antes (1: x_j = 1; 0: x_j = 0). Las ramas son pares (j, valor)."""
    def resolver(ramas):
        return mochila_lp(v, a, cap, dict(ramas))

    def ramas_de(nd):
        j = next(i for i, t in enumerate(nd["x"]) if F(t).denominator != 1)
        nd["var"] = j
        return [(j, primero), (j, 1 - primero)]

    def es_entera(nd):
        return all(F(t).denominator == 1 for t in nd["x"])

    return _rya(resolver, ramas_de, es_entera, "max", estrategia)


def mochila_fuerza_bruta(v, a, cap):
    best, n = None, 0
    for x in product((0, 1), repeat=len(v)):
        if sum(p * q for p, q in zip(a, x)) <= cap:
            z = sum(p * q for p, q in zip(v, x))
            if best is None or z > best[0]:
                best = (z, x)
    return best


# ---------------------------------------------------------------- cotas y gap después de cada PL
def traza(R):
    """Para cada PL resuelto: incumbente, mejor cota (con herencia) y gap absoluto y relativo.
    Gap relativo = |cota − incumbente| / |incumbente| (se divide por la incumbente, como en el curso)."""
    out = []
    for r in R["registro"]:
        inc, cota = r["inc"], r["cota"]
        ga = None if inc is None else abs(cota - inc)
        gr = None if inc is None or inc == 0 else ga / abs(F(inc))
        out.append(dict(r, gabs=ga, grel=gr))
    return out


# ---------------------------------------------------------------- tabla simplex (convención del curso)
class Tabla:
    """Tabla simplex con fila z en la convención del curso: z + Σ (z_j − c_j) x_j = z.

    En máximo la tabla es óptima cuando toda z_j − c_j ≥ 0; en mínimo, cuando toda z_j − c_j ≤ 0.
    Las filas son listas de fracciones (coeficientes de las columnas y, al final, el lado derecho)."""

    def __init__(self, nombres, filas, z, base, sentido="max"):
        self.nombres = list(nombres)
        self.T = [[F(v) for v in r] for r in filas]
        self.z = [F(v) for v in z]
        self.base = list(base)
        self.sentido = sentido

    def copia(self):
        t = Tabla(self.nombres, self.T, self.z, self.base, self.sentido)
        return t

    @classmethod
    def desde_holguras(cls, c, A, b, sentido="max", nx=("x1", "x2", "x3", "x4", "x5", "x6")):
        n, m = len(c), len(A)
        nombres = list(nx[:n]) + [f"s{i + 1}" for i in range(m)]
        T = [list(A[i]) + [int(i == k) for k in range(m)] + [b[i]] for i in range(m)]
        z = [-v for v in c] + [0] * m + [0]
        return cls(nombres, T, z, [n + i for i in range(m)], sentido)

    def pivotear(self, r, e):
        p = self.T[r][e]
        self.T[r] = [v / p for v in self.T[r]]
        for i in range(len(self.T)):
            if i != r and self.T[i][e] != 0:
                f = self.T[i][e]
                self.T[i] = [a - f * q for a, q in zip(self.T[i], self.T[r])]
        f = self.z[e]
        self.z = [a - f * q for a, q in zip(self.z, self.T[r])]
        self.base[r] = e

    def optima(self):
        if self.sentido == "max":
            return all(v >= 0 for v in self.z[:-1])
        return all(v <= 0 for v in self.z[:-1])

    def factible(self):
        return all(r[-1] >= 0 for r in self.T)

    def valor(self, nombre):
        j = self.nombres.index(nombre)
        return self.T[self.base.index(j)][-1] if j in self.base else F(0)

    def paso_dual(self):
        """Un pivote del simplex dual. Sale la básica de lado derecho más negativo (empate: la de más
        arriba); entra, entre las columnas con coeficiente negativo en esa fila, la de menor
        |z_j − c_j| / |a_rj| (empate: la de más a la izquierda). Devuelve (fila, columna, cocientes)
        o ('infactible', fila) si la fila no tiene coeficientes negativos."""
        neg = [i for i in range(len(self.T)) if self.T[i][-1] < 0]
        r = min(neg, key=lambda i: (self.T[i][-1], i))
        cand = {j: abs(self.z[j]) / abs(self.T[r][j]) for j in range(len(self.nombres)) if self.T[r][j] < 0}
        if not cand:
            return ("infactible", r)
        e = min(cand, key=lambda j: (cand[j], j))
        self.pivotear(r, e)
        return (r, e, cand)

    def paso_primal(self):
        """Un pivote del simplex primal (máximo): entra la de z_j − c_j más negativa, sale por razón mínima."""
        sg = 1 if self.sentido == "max" else -1
        cand = [j for j in range(len(self.nombres)) if sg * self.z[j] < 0]
        e = min(cand, key=lambda j: (sg * self.z[j], j))
        raz = {i: self.T[i][-1] / self.T[i][e] for i in range(len(self.T)) if self.T[i][e] > 0}
        r = min(raz, key=lambda i: (raz[i], i))
        self.pivotear(r, e)
        return (r, e, raz)

    def corte_gomory(self, r, nombre):
        """Corte de Gomory desde la fila r: Σ f_j x_j ≥ f_0, que entra como −Σ f_j x_j + s = −f_0."""
        fila = self.T[r]
        f = [frac(v) if j not in self.base else F(0) for j, v in enumerate(fila[:-1])]
        f0 = frac(fila[-1])
        for row in self.T:
            row.insert(-1, F(0))
        self.z.insert(-1, F(0))
        self.nombres.append(nombre)
        self.T.append([-v for v in f] + [F(1), -f0])
        self.base.append(len(self.nombres) - 1)
        return f, f0

    def md(self, marca=None, cocientes=None):
        """La tabla en Markdown. `marca` = (fila, columna) del pivote, que va en negrita."""
        cab = ["Base"] + [latex_nombre(n) for n in self.nombres] + ["LD"]
        L = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
        L.append("| z | " + " | ".join(fr(v) for v in self.z) + " |")
        for i, r in enumerate(self.T):
            celdas = [fr(v) for v in r]
            if marca and marca[0] == i:
                celdas[marca[1]] = f"**{celdas[marca[1]]}**"
            L.append("| " + latex_nombre(self.nombres[self.base[i]]) + " | " + " | ".join(celdas) + " |")
        if cocientes:
            fila = ["\\|z_j − c_j\\| / \\|a_rj\\|"] + [fr(cocientes[j]) if j in cocientes else "" for j in range(len(self.nombres))] + [""]
            L.append("| " + " | ".join(fila) + " |")
        return "\n".join(L)


def latex_nombre(n):
    """x1 → x₁, s3 → s₃ (para las tablas)."""
    sub = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    return n[0] + n[1:].translate(sub)


# ---------------------------------------------------------------- figuras
TINTA, SUAVE, ACENTO = "#2B2F33", "#5F656B", "#E2622A"
AZUL, VERDE, MORADO, ROJO = "#1F5F8B", "#2E7D4F", "#8A4FA3", "#B3261E"
FUENTE = "Segoe UI, Roboto, Arial, sans-serif"


def svg(ancho, alto, partes, titulo):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}" '
            f'role="img" aria-label="{titulo}"><title>{titulo}</title><rect width="{ancho}" height="{alto}" fill="#FFFFFF"/>'
            + "".join(partes) + "</svg>\n")


def texto(X, Y, t, color=TINTA, tam=12, ancla="middle", peso="normal"):
    return (f'<text x="{X:.1f}" y="{Y:.1f}" font-family="{FUENTE}" font-size="{tam}" fill="{color}" '
            f'text-anchor="{ancla}" font-weight="{peso}" stroke="#FFFFFF" stroke-width="3" '
            f'paint-order="stroke" stroke-linejoin="round">{t}</text>')


ESTADO = {"ramificado": ("ramifica", TINTA), "entera": ("entera", VERDE), "cota": ("poda por cota", AZUL),
          "cota_tardia": ("poda por cota", AZUL), "infactible": ("infactible", ROJO)}


def arbol_svg(R, lineas, titulo, ancho_nodo=150, alto_nodo=66, sep_x=14, sep_y=48, rama_txt_f=None, optimo=None):
    """Dibuja el árbol de ramificación. `lineas(nd)` devuelve las líneas de texto de cada nodo."""
    N = R["nodos"]
    hijos = {}
    for nd in N:
        if nd["padre"] is not None:
            hijos.setdefault(nd["padre"], []).append(nd["k"])
    # orden de hijos: el de la rama «≤» (o «= 0») a la izquierda
    def clave_hijo(k):
        r = N[k]["rotulo"]
        if isinstance(r, tuple) and len(r) == 2:        # mochila: (j, valor)
            return r[1]
        return 0 if (r[0] + r[1]) > 0 else 1             # x ≤ v a la izquierda
    for p in hijos:
        hijos[p].sort(key=clave_hijo)
    pos, prof = {}, {}
    cursor = [0]

    def ubicar(k, d):
        prof[k] = d
        hs = hijos.get(k, [])
        if not hs:
            pos[k] = cursor[0]; cursor[0] += 1
        else:
            for h in hs:
                ubicar(h, d + 1)
            pos[k] = sum(pos[h] for h in hs) / len(hs)
    ubicar(0, 0)
    hojas = cursor[0]; D = max(prof.values())
    W = int(hojas * (ancho_nodo + sep_x) + 40); H = int((D + 1) * (alto_nodo + sep_y) + 30)
    cx = lambda k: 20 + pos[k] * (ancho_nodo + sep_x) + ancho_nodo / 2
    cy = lambda k: 16 + prof[k] * (alto_nodo + sep_y)
    p = []
    for k, hs in hijos.items():
        for h in hs:
            x1, y1 = cx(k), cy(k) + alto_nodo; x2, y2 = cx(h), cy(h)
            p.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{SUAVE}" stroke-width="1.4"/>')
            t = rama_txt_f(N[h]["rotulo"]) if rama_txt_f else rama_txt(N[h]["rotulo"])
            p.append(texto((x1 + x2) / 2, (y1 + y2) / 2 + 4, t, TINTA, 11.5, "middle", "600"))
    for nd in N:
        k = nd["k"]
        if k not in pos:
            continue
        et, col = ESTADO.get(nd["estado"], ("", TINTA))
        x0, y0 = cx(k) - ancho_nodo / 2, cy(k)
        grosor = 3 if optimo is not None and k == optimo else 1.6
        p.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{ancho_nodo}" height="{alto_nodo}" rx="8" fill="#FFFFFF" '
                 f'stroke="{col}" stroke-width="{grosor}"/>')
        ls = lineas(nd)
        for i, l in enumerate(ls):
            p.append(texto(cx(k), y0 + 16 + i * 15, l, col if i == len(ls) - 1 else TINTA, 11.5 if i else 12,
                           "middle", "600" if i in (0, len(ls) - 1) else "normal"))
    return svg(W, H, p, titulo)


class Lienzo:
    def __init__(self, x0, y0, w, h, xlim, ylim):
        self.x0, self.y0, self.w, self.h, self.xlim, self.ylim = x0, y0, w, h, xlim, ylim
        self.sx = w / (xlim[1] - xlim[0]); self.sy = h / (ylim[1] - ylim[0]); self.p = []

    def px(self, x, y):
        return self.x0 + (float(x) - self.xlim[0]) * self.sx, self.y0 + self.h - (float(y) - self.ylim[0]) * self.sy

    def texto(self, X, Y, t, color=TINTA, tam=12, ancla="start", peso="normal"):
        self.p.append(texto(X, Y, t, color, tam, ancla, peso))

    def ejes(self, ex, ey, paso_x=1, paso_y=1):
        x0, y0 = self.px(self.xlim[0], self.ylim[0]); x1, _ = self.px(self.xlim[1], 0); _, y1 = self.px(0, self.ylim[1])
        for t in range(self.xlim[0], self.xlim[1] + 1, paso_x):
            X, _ = self.px(t, 0)
            self.p.append(f'<line x1="{X:.1f}" y1="{y1:.1f}" x2="{X:.1f}" y2="{y0:.1f}" stroke="#EEECE9"/>')
            self.p.append(f'<text x="{X:.1f}" y="{y0 + 16:.1f}" font-family="{FUENTE}" font-size="11" fill="{SUAVE}" text-anchor="middle">{t}</text>')
        for t in range(self.ylim[0], self.ylim[1] + 1, paso_y):
            _, Y = self.px(0, t)
            self.p.append(f'<line x1="{x0:.1f}" y1="{Y:.1f}" x2="{x1:.1f}" y2="{Y:.1f}" stroke="#EEECE9"/>')
            self.p.append(f'<text x="{x0 - 7:.1f}" y="{Y + 4:.1f}" font-family="{FUENTE}" font-size="11" fill="{SUAVE}" text-anchor="end">{t}</text>')
        self.p.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1 + 6:.1f}" y2="{y0:.1f}" stroke="{TINTA}" stroke-width="1.3"/>')
        self.p.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x0:.1f}" y2="{y1 - 6:.1f}" stroke="{TINTA}" stroke-width="1.3"/>')
        self.texto(x1 + 4, y0 - 8, ex, TINTA, 12, "end", "600"); self.texto(x0 + 6, y1 - 4, ey, TINTA, 12, "start", "600")

    def poligono(self, pts, relleno, opac, borde="none", guion=None):
        d = " ".join(f"{self.px(*q)[0]:.1f},{self.px(*q)[1]:.1f}" for q in pts)
        g = f' stroke-dasharray="{guion}"' if guion else ""
        self.p.append(f'<polygon points="{d}" fill="{relleno}" fill-opacity="{opac}" stroke="{borde}" stroke-width="2"{g}/>')

    def recta(self, a1, a2, b, color, etiqueta, t=0.5, dx=6, dy=-6, ancla="start", guion=None):
        (xa, xb), (ya, yb) = self.xlim, self.ylim
        a1, a2, b = float(a1), float(a2), float(b)
        cand = []
        if abs(a2) > 1e-12:
            cand += [(x, (b - a1 * x) / a2) for x in (xa, xb)]
        if abs(a1) > 1e-12:
            cand += [((b - a2 * y) / a1, y) for y in (ya, yb)]
        cand = sorted({(round(q[0], 9), round(q[1], 9)) for q in cand if xa - 1e-9 <= q[0] <= xb + 1e-9 and ya - 1e-9 <= q[1] <= yb + 1e-9})
        P, Q = self.px(*cand[0]), self.px(*cand[-1])
        g = f' stroke-dasharray="{guion}"' if guion else ""
        self.p.append(f'<line x1="{P[0]:.1f}" y1="{P[1]:.1f}" x2="{Q[0]:.1f}" y2="{Q[1]:.1f}" stroke="{color}" stroke-width="1.8"{g}/>')
        self.texto(P[0] + t * (Q[0] - P[0]) + dx, P[1] + t * (Q[1] - P[1]) + dy, etiqueta, color, 12, ancla, "600")

    def punto(self, x, y, r=3.2, color=TINTA, hueco=False):
        X, Y = self.px(x, y)
        if hueco:
            self.p.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="#FFFFFF" stroke="{color}" stroke-width="2"/>')
        else:
            self.p.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="{color}" stroke="#FFFFFF" stroke-width="1.2"/>')

    def rotulo(self, x, y, t, color=TINTA, dx=8, dy=-8, ancla="start", peso="600"):
        X, Y = self.px(x, y); self.texto(X + dx, Y + dy, t, color, 12, ancla, peso)


def ordenar(pts):
    cx = sum(float(q[0]) for q in pts) / len(pts); cy = sum(float(q[1]) for q in pts) / len(pts)
    return sorted(pts, key=lambda q: math.atan2(float(q[1]) - cy, float(q[0]) - cx))


def envoltura(pts):
    """Envoltura convexa (cadena monótona), vértices en orden antihorario, sin puntos colineales."""
    P = sorted(set(pts))
    if len(P) < 3:
        return P
    def cruz(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for q in P:
        while len(lo) >= 2 and cruz(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(P):
        while len(hi) >= 2 and cruz(hi[-2], hi[-1], q) <= 0:
            hi.pop()
        hi.append(q)
    return lo[:-1] + hi[:-1]


def facetas(V):
    """Desigualdades a1 x1 + a2 x2 ≤ b (enteros primitivos) de cada lado de la envoltura V (antihoraria)."""
    out = []
    for i in range(len(V)):
        p, q = V[i], V[(i + 1) % len(V)]
        a1, a2 = q[1] - p[1], p[0] - q[0]          # normal exterior para recorrido antihorario
        g = math.gcd(int(a1), int(a2)) or 1
        a1, a2 = int(a1) // g, int(a2) // g
        b = a1 * p[0] + a2 * p[1]
        out.append((a1, a2, b, p, q))
    return out
