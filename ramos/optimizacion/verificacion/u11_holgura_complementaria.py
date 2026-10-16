"""Unidad 11 · Holgura complementaria.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md. Cada comprobación de holgura complementaria se hace
con fracciones exactas y se contrasta con el óptimo que entrega un solver (HiGHS vía scipy) y, si
está instalado CPLEX, con el modelo OPL de `modelos/`.

    python u11_holgura_complementaria.py            # imprime los resultados
    python u11_holgura_complementaria.py --revisar  # además los busca en el .md
"""
from fractions import Fraction as Fr
from pathlib import Path
import importlib.util, sys

import numpy as np
from scipy.optimize import linprog

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402


# ---------------------------------------------------------------- formato chileno

def fmt(x, dec=0):
    s = f"{float(x):,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x, dec=0):
    return "$" + fmt(x, dec)


# ---------------------------------------------------------------- datos (originales; pasados por colisiones.py)

# Ejemplo · tostaduría: espresso, filtro, descafeinado (margen $/kg); tostadora (min), envasadora (min), bolsas
EJ = dict(nombres=["espresso", "filtro", "descafeinado"], c=[4200, 3450, 5100],
          A=[[6, 4, 9], [3, 2, 2], [1, 1, 1]], b=[2400, 1000, 350],
          propuesta_a=[250, 0, 100], propuesta_b=[200, 50, 100], y_dado=[300, 0, 2400])

E1 = dict(c=[5000, 4000], A=[[2, 1], [1, 3], [1, 0]], b=[40, 45, 18], x=[15, 10])          # amasandería
E2 = dict(c=[1800, 2100, 1500], A=[[3, 4, 2], [2, 2, 3]], b=[600, 480], x=[168, 0, 48])  # mermeladas
E3 = dict(c=[60000, 40000, 70000, 35000], A=[[3, 2, 4, 1], [1, 1, 2, 2]], b=[240, 140],   # bicicletas
          y=[17000, 9000])
E4 = dict(c=[40000, 100000, 80000], A=[[1, 5, 1], [2, 2, 3], [1, 1, 5]], b=[860, 1000, 320])  # imprenta
E5 = dict(c=[2600, 2900, 1900], A=[[4, 6, 3], [2, 1, 1], [1, 2, 1]], b=[960, 300, 260],   # quesería
          x=[0, 0, 260])
E6 = dict(c=[840, 320, 440], A=[[7, 1, 7], [7, 9, 3], [9, 4, 9]], b=[190, 390, 190],     # alimento (mín)
          tipos=[">=", ">=", ">="], sentido="min", x=[0, 36, 22])
E7 = dict(c=[8400, 2550, 2350], A=[[8, 3, 3], [1, 6, 2], [1, 1, 1]], b=[800, 2250, 230],  # canastas
          tipos=["<=", "<=", "="], x=[22, 208, 0])
E8 = dict(c=[4100, 1400, 4500], A=[[5, 4, 3], [4, 4, 3], [1, 0, 0], [0, 1, 0], [0, 0, 1]],  # chocolatería
          b=[660, 820, 180, 390, 80], x=[84, 0, 80])
E9 = dict(c=[3000, 2000], A=[[1, 1], [2, 1], [1, 0]], b=[40, 60, 20], x=[20, 20])          # cerámica
E10 = dict(c=[4200, 3600, 5100], A=EJ["A"], b=EJ["b"], x_a=[250, 0, 100], x_b=[0, 150, 200])


# ---------------------------------------------------------------- holgura complementaria exacta

def resolver_exacto(filas, lados):
    """Eliminación de Gauss con fracciones. Devuelve (solución única o None, rango, consistente)."""
    M = [[Fr(v) for v in f] + [Fr(l)] for f, l in zip(filas, lados)]
    n = len(filas[0]) if filas else 0
    piv, r = [], 0
    for col in range(n):
        p = next((i for i in range(r, len(M)) if M[i][col] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        M[r] = [v / M[r][col] for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][col] != 0:
                f = M[i][col]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv.append(col)
        r += 1
    consistente = all(any(v != 0 for v in fila[:-1]) or fila[-1] == 0 for fila in M)
    if not consistente or r < n:
        return None, r, consistente
    sol = [Fr(0)] * n
    for i, col in enumerate(piv):
        sol[col] = M[i][-1]
    return sol, r, True


def signo_dual_ok(yi, tipo, sentido):
    if tipo == "=":
        return True
    if sentido == "max":
        return yi >= 0 if tipo == "<=" else yi <= 0
    return yi >= 0 if tipo == ">=" else yi <= 0


def hc(c, A, b, x, tipos=None, sentido="max"):
    """Aplica holgura complementaria a una solución propuesta x."""
    m, n = len(A), len(c)
    tipos = tipos or ["<="] * m
    x = [Fr(v) for v in x]
    lhs = [sum(Fr(a) * xi for a, xi in zip(fila, x)) for fila in A]
    holg = [(Fr(bi) - l) if t == "<=" else (l - Fr(bi)) if t == ">=" else Fr(0) for bi, l, t in zip(b, lhs, tipos)]
    factible = all(h >= 0 for h in holg) and all(v >= 0 for v in x) and \
        all(l == bi for l, bi, t in zip(lhs, b, tipos) if t == "=")
    filas, lados = [], []
    for i in range(m):                       # restricción con holgura → su dual vale cero
        if holg[i] != 0:
            filas.append([int(k == i) for k in range(m)]); lados.append(0)
    for j in range(n):                       # variable positiva → su restricción dual se cumple con igualdad
        if x[j] > 0:
            filas.append([A[i][j] for i in range(m)]); lados.append(c[j])
    y, rango, consistente = resolver_exacto(filas, lados)
    R = dict(lhs=lhs, holg=holg, factible=factible, consistente=consistente, y=y, rango=rango,
             z=sum(Fr(cj) * xj for cj, xj in zip(c, x)))
    if y is not None:
        valor = [sum(Fr(A[i][j]) * y[i] for i in range(m)) for j in range(n)]
        cr = [Fr(c[j]) - valor[j] for j in range(n)]                   # costo reducido = holgura dual con signo
        dual_ok = all(signo_dual_ok(y[i], tipos[i], sentido) for i in range(m)) and \
            all((cr[j] <= 0 if sentido == "max" else cr[j] >= 0) for j in range(n))
        R.update(valor_recursos=valor, costo_reducido=cr, dual_factible=dual_ok,
                 w=sum(Fr(bi) * yi for bi, yi in zip(b, y)), optima=factible and dual_ok)
    else:
        R.update(optima=None)
    return R


def solver(c, A, b, tipos=None, sentido="max", bounds=None):
    """Óptimo con HiGHS: x, z, duales (con el signo de «cuánto mejora z por unidad de lado derecho»)."""
    m, n = len(A), len(c)
    tipos = tipos or ["<="] * m
    sg = -1 if sentido == "max" else 1
    Aub, bub, Aeq, beq, idx = [], [], [], [], []
    for i, t in enumerate(tipos):
        if t == "<=":
            Aub.append(A[i]); bub.append(b[i]); idx.append(("ub", len(Aub) - 1, 1))
        elif t == ">=":
            Aub.append([-a for a in A[i]]); bub.append(-b[i]); idx.append(("ub", len(Aub) - 1, -1))
        else:
            Aeq.append(A[i]); beq.append(b[i]); idx.append(("eq", len(Aeq) - 1, 1))
    r = linprog([sg * v for v in c], A_ub=Aub or None, b_ub=bub or None, A_eq=Aeq or None, b_eq=beq or None,
                bounds=bounds or [(0, None)] * n, method="highs")
    assert r.status == 0
    duales = []
    for tipo, k, s in idx:
        marg = r.ineqlin.marginals[k] if tipo == "ub" else r.eqlin.marginals[k]
        duales.append(sg * marg * s)          # dz/db en el sentido del problema original
    return dict(x=list(r.x), z=sg * r.fun, y=duales)


def iguales(a, b, tol=1e-6):
    return all(abs(float(u) - float(v)) < tol * max(1, abs(float(v))) for u, v in zip(a, b))


# ---------------------------------------------------------------- OPL

def opl(mod, dat=None):
    r = correr(MODELOS / mod, MODELOS / dat if dat else None)
    if r is None:
        return None
    assert r["codigo"] == 0, r["salida"][-800:]
    return r["valores"]


def comparar_opl(nombre, valores, esperado):
    """esperado: dict clave → número. Si OPL no está, no compara."""
    if valores is None:
        print(f"   OPL {nombre}: sin CPLEX, sigue con Python")
        return True
    malos = {k: (valores.get(k), v) for k, v in esperado.items()
             if k not in valores or abs(float(valores[k]) - float(v)) > 1e-6 * max(1, abs(float(v)))}
    print(f"   OPL {nombre}:", "coincide con Python" if not malos else f"NO coincide {malos}")
    return not malos


# ---------------------------------------------------------------- cálculo

def resultados():
    R = {}
    # Ejemplo
    a = hc(EJ["c"], EJ["A"], EJ["b"], EJ["propuesta_a"])
    bb = hc(EJ["c"], EJ["A"], EJ["b"], EJ["propuesta_b"])
    s = solver(EJ["c"], EJ["A"], EJ["b"])
    assert a["optima"] and iguales(s["x"], EJ["propuesta_a"]) and iguales(s["y"], a["y"])
    assert bb["optima"] is None and not bb["consistente"] and bb["factible"]
    # del dual al primal: con y dado, las restricciones con y>0 van activas y los productos con holgura dual valen 0
    yd = [Fr(v) for v in EJ["y_dado"]]
    holg_dual = [sum(Fr(EJ["A"][i][j]) * yd[i] for i in range(3)) - EJ["c"][j] for j in range(3)]
    filas = [EJ["A"][i] for i in range(3) if yd[i] > 0] + [[int(k == j) for k in range(3)] for j in range(3) if holg_dual[j] > 0]
    lados = [EJ["b"][i] for i in range(3) if yd[i] > 0] + [0 for j in range(3) if holg_dual[j] > 0]
    x_dual, _, _ = resolver_exacto(filas, lados)
    assert x_dual == [Fr(v) for v in EJ["propuesta_a"]]
    R["ej"] = dict(a=a, b=bb, holg_dual=holg_dual, x_desde_dual=x_dual)

    # 11.1 amasandería
    r1 = hc(**{k: E1[k] for k in ("c", "A", "b", "x")}); assert r1["optima"]
    assert iguales(solver(E1["c"], E1["A"], E1["b"])["y"], r1["y"])
    R["e1"] = r1
    # 11.2 mermeladas
    r2 = hc(**{k: E2[k] for k in ("c", "A", "b", "x")}); assert r2["optima"]
    R["e2"] = r2
    # 11.3 bicicletas: del dual al primal
    y3 = [Fr(v) for v in E3["y"]]
    hd3 = [sum(Fr(E3["A"][i][j]) * y3[i] for i in range(2)) - E3["c"][j] for j in range(4)]
    assert all(h >= 0 for h in hd3)
    cols = [j for j in range(4) if hd3[j] == 0]
    sub = [[E3["A"][i][j] for j in cols] for i in range(2)]
    xs, _, _ = resolver_exacto(sub, E3["b"])
    x3 = [Fr(0)] * 4
    for j, v in zip(cols, xs):
        x3[j] = v
    s3 = solver(E3["c"], E3["A"], E3["b"])
    assert iguales(s3["x"], x3) and iguales(s3["y"], y3)
    R["e3"] = dict(holg_dual=hd3, x=x3, z=sum(Fr(c) * v for c, v in zip(E3["c"], x3)),
                   w=sum(Fr(b) * v for b, v in zip(E3["b"], y3)), valor=[h + c for h, c in zip(hd3, E3["c"])])
    # 11.4 imprenta: el informe sale del solver y se comprueba con holgura complementaria
    s4 = solver(E4["c"], E4["A"], E4["b"])
    r4 = hc(E4["c"], E4["A"], E4["b"], [round(v) for v in s4["x"]]); assert r4["optima"]
    R["e4"] = dict(s=s4, hc=r4)
    # 11.5 quesería: propuesta no óptima; el óptimo sale de OPL y de HiGHS
    r5 = hc(**{k: E5[k] for k in ("c", "A", "b", "x")}); assert r5["factible"] and r5["optima"] is False
    s5 = solver(E5["c"], E5["A"], E5["b"])
    r5o = hc(E5["c"], E5["A"], E5["b"], [round(v) for v in s5["x"]]); assert r5o["optima"]
    R["e5"] = dict(prop=r5, opt=r5o, s=s5)
    # 11.6 alimento (mínimo)
    r6 = hc(E6["c"], E6["A"], E6["b"], E6["x"], E6["tipos"], E6["sentido"]); assert r6["optima"]
    s6 = solver(E6["c"], E6["A"], E6["b"], E6["tipos"], "min")
    assert iguales(s6["x"], E6["x"]) and iguales(s6["y"], r6["y"])
    R["e6"] = r6
    # 11.7 canastas (igualdad, dual libre)
    r7 = hc(E7["c"], E7["A"], E7["b"], E7["x"], E7["tipos"]); assert r7["optima"] and r7["y"][2] < 0
    s7 = solver(E7["c"], E7["A"], E7["b"], E7["tipos"])
    assert iguales(s7["x"], E7["x"]) and iguales(s7["y"], r7["y"])
    R["e7"] = r7
    # 11.8 chocolatería con topes de demanda como restricciones
    r8 = hc(**{k: E8[k] for k in ("c", "A", "b", "x")}); assert r8["optima"]
    s8 = solver(E8["c"], E8["A"], E8["b"])
    assert iguales(s8["x"], E8["x"]) and iguales(s8["y"], r8["y"])
    R["e8"] = r8
    # 11.9 cerámica degenerada: la familia de duales y las derivadas laterales
    r9 = hc(**{k: E9[k] for k in ("c", "A", "b", "x")})
    assert r9["y"] is None and r9["consistente"] and r9["rango"] == 2
    fam = []
    for t in (Fr(0), Fr(1, 2), Fr(1)):            # y2 = t ; y1 = 2000 - t·1000/1000 ... ver texto
        y2 = t * 1000
        y3 = 1000 - y2
        y1 = Fr(2000) - y2
        yy = [y1, y2, y3]
        assert all(v >= 0 for v in yy)
        assert all(sum(Fr(E9["A"][i][j]) * yy[i] for i in range(3)) >= E9["c"][j] for j in range(2))
        fam.append((yy, sum(Fr(b) * v for b, v in zip(E9["b"], yy))))
    z_mas = solver(E9["c"], E9["A"], [40, 61, 20])["z"]
    z_menos = solver(E9["c"], E9["A"], [40, 59, 20])["z"]
    z9 = solver(E9["c"], E9["A"], E9["b"])["z"]
    R["e9"] = dict(hc=r9, familia=fam, z=z9, z_mas=z_mas, z_menos=z_menos,
                   der_derecha=z_mas - z9, der_izquierda=z9 - z_menos)
    # 11.10 tostaduría con filtro a $3.600: dos óptimos alternativos
    ra = hc(E10["c"], E10["A"], E10["b"], E10["x_a"]); rb = hc(E10["c"], E10["A"], E10["b"], E10["x_b"])
    medio = [(Fr(u) + Fr(v)) / 2 for u, v in zip(E10["x_a"], E10["x_b"])]
    rm = hc(E10["c"], E10["A"], E10["b"], medio)
    assert ra["optima"] and rb["optima"] and rm["optima"] and ra["y"] == rb["y"] == rm["y"]
    assert ra["costo_reducido"][1] == 0
    R["e10"] = dict(a=ra, b=rb, medio=medio, m=rm)
    return R


def caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_lp.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    C = mod.calcular()["u4"]
    A = [mod.SEG_EST, mod.SEG_PLA, mod.TINTA_G] + [[int(i == j) for j in range(5)] for i in range(5)]
    b = [mod.CAP["estampado_s"], mod.CAP["planchado_s"], mod.CAP["tinta_g"]] + mod.DEMANDA_MAX
    x = [Fr(v).limit_denominator(1000) for v in C["x"]]
    r = hc(mod.MARGEN, A, b, x)
    return mod, C, r, A, b


def imprimir(R, K):
    f = lambda v: fmt(v, 2) if isinstance(v, (Fr, float)) and float(v) != int(v) else fmt(v)
    print("== Ejemplo · propuesta A", "óptima" if R["ej"]["a"]["optima"] else "no",
          "| y =", [f(v) for v in R["ej"]["a"]["y"]], "| z = w =", f(R["ej"]["a"]["z"]), f(R["ej"]["a"]["w"]))
    print("   holguras A", [f(v) for v in R["ej"]["a"]["holg"]], "| costos reducidos", [f(v) for v in R["ej"]["a"]["costo_reducido"]])
    print("   propuesta B holguras", [f(v) for v in R["ej"]["b"]["holg"]], "consistente:", R["ej"]["b"]["consistente"], "z =", f(R["ej"]["b"]["z"]))
    print("   del dual al primal: holguras duales", [f(v) for v in R["ej"]["holg_dual"]], "→ x =", [f(v) for v in R["ej"]["x_desde_dual"]])
    for k in ("e1", "e2", "e6", "e7", "e8"):
        r = R[k]
        print(f"== {k}: holguras {[f(v) for v in r['holg']]} y {[f(v) for v in r['y']]} cr {[f(v) for v in r['costo_reducido']]} z {f(r['z'])} w {f(r['w'])}")
    e3 = R["e3"]; print("== e3: holgura dual", [f(v) for v in e3["holg_dual"]], "x", [f(v) for v in e3["x"]], "z", f(e3["z"]), "w", f(e3["w"]))
    e4 = R["e4"]["hc"]; print("== e4: x", [f(v) for v in R["e4"]["s"]["x"]], "holg", [f(v) for v in e4["holg"]], "y", [f(v) for v in e4["y"]], "z", f(e4["z"]), "valor C", f(e4["valor_recursos"][2]))
    e5 = R["e5"]; print("== e5 propuesta: holg", [f(v) for v in e5["prop"]["holg"]], "y", [f(v) for v in e5["prop"]["y"]], "cr", [f(v) for v in e5["prop"]["costo_reducido"]], "z", f(e5["prop"]["z"]))
    print("   óptimo", [f(v) for v in e5["s"]["x"]], "z", f(e5["opt"]["z"]), "y", [f(v) for v in e5["opt"]["y"]], "cr", [f(v) for v in e5["opt"]["costo_reducido"]])
    e9 = R["e9"]; print("== e9 familia", [([f(v) for v in y], f(w)) for y, w in e9["familia"]], "z", f(e9["z"]), "b2+1", f(e9["z_mas"]), "b2-1", f(e9["z_menos"]))
    e10 = R["e10"]; print("== e10 y", [f(v) for v in e10["a"]["y"]], "cr", [f(v) for v in e10["a"]["costo_reducido"]], "z", f(e10["a"]["z"]), f(e10["b"]["z"]), "medio", [f(v) for v in e10["medio"]], "holg b", [f(v) for v in e10["b"]["holg"]])
    mod, C, r, A, b = K
    print("== CASO u4: x", [f(v) for v in C["x"]], "holguras", [f(v) for v in r["holg"]])
    print("   y", [f(v) for v in r["y"]], "valor recursos", [f(v) for v in r["valor_recursos"]], "cr", [f(v) for v in r["costo_reducido"]], "z", f(r["z"]), "w", f(r["w"]))


# ---------------------------------------------------------------- OPL contra Python

def verificar_opl(R, K):
    ok = True
    v = opl("u11_mezcla.mod", "u11_tostaduria.dat")
    a = R["ej"]["a"]
    esp = {"margen": a["z"]}
    for n, xv, h, y, cr in zip(EJ["nombres"], EJ["propuesta_a"], a["holg"], [None] * 3, a["costo_reducido"]):
        esp[f"x[{n}]"] = xv
        esp[f"costo_reducido[{n}]"] = cr
    for rec, h, y in zip(["tostadora", "envasadora", "bolsas"], a["holg"], a["y"]):
        esp[f"holgura[{rec}]"] = h; esp[f"dual[{rec}]"] = y
    ok &= comparar_opl("ejemplo", v, esp)
    v = opl("u11_mezcla.mod", "u11_quesos.dat")
    o = R["e5"]["opt"]
    esp = {"margen": o["z"], "x[gauda]": R["e5"]["s"]["x"][0], "x[mantecoso]": R["e5"]["s"]["x"][1],
           "x[fresco]": R["e5"]["s"]["x"][2], "dual[leche]": o["y"][0], "dual[camara]": o["y"][1],
           "dual[envasado]": o["y"][2], "costo_reducido[mantecoso]": o["costo_reducido"][1]}
    ok &= comparar_opl("11.5", v, esp)
    v = opl("u11_mezcla.mod", "u11_ceramica.dat")
    if v is not None:
        print("   OPL 11.9 (degenerado) informa duales:", {k: v[k] for k in v if k.startswith("dual")})
        y = [v["dual[horno]"], v["dual[esmalte]"], v["dual[tope_tazas]"]]
        fam_ok = abs(y[0] + y[1] - 2000) < 1e-6 and abs(y[1] + y[2] - 1000) < 1e-6
        print("   OPL 11.9: el dual que elige CPLEX", "está en la familia" if fam_ok else "NO está en la familia")
        ok &= fam_ok
        R["e9"]["opl"] = y
    mod, C, r, A, b = K
    v = opl("u11_dual_estampa.mod", "u11_dual_estampa.dat")
    esp = {"w": r["w"], "y[estampado]": r["y"][0], "y[planchado]": r["y"][1], "y[tinta]": r["y"][2]}
    for n, u in zip(["poleras", "polerones", "doble", "bolsas", "gorros"], r["y"][3:]):
        esp[f"u[{n}]"] = u
    for n, xv in zip(["poleras", "polerones", "doble", "bolsas", "gorros"], C["x"]):
        esp[f"x_desde_dual[{n}]"] = xv
    ok &= comparar_opl("caso (dual)", v, esp)
    return ok


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R, K):
    e = []
    a, bb = R["ej"]["a"], R["ej"]["b"]
    e += [pesos(a["z"]), pesos(a["w"]), "$300", "$2.400", pesos(bb["z"]), "−150", "4.200", "3.600"]
    e += [fmt(v) for v in bb["holg"]] + [pesos(a["z"] - bb["z"]), fmt(EJ["b"][0] * a["y"][0]), fmt(EJ["b"][2] * a["y"][2])]
    r1 = R["e1"]; e += [pesos(r1["y"][0]), pesos(r1["y"][1]), pesos(r1["z"])]
    r2 = R["e2"]; e += [pesos(r2["y"][0]), pesos(r2["y"][1]), pesos(r2["z"]), fmt(r2["valor_recursos"][1])]
    e3 = R["e3"]; e += [pesos(e3["z"]), pesos(e3["valor"][1]), pesos(e3["valor"][2])]
    e4 = R["e4"]["hc"]; e += [pesos(e4["z"]), pesos(e4["valor_recursos"][2]), pesos(e4["y"][0]), pesos(e4["y"][2]), fmt(e4["holg"][1])]
    e5 = R["e5"]; e += [pesos(e5["prop"]["z"]), pesos(e5["opt"]["z"]), pesos(e5["opt"]["y"][1]), pesos(e5["opt"]["y"][2]),
                        fmt(e5["opt"]["holg"][0]), pesos(-e5["opt"]["costo_reducido"][1])]
    r6 = R["e6"]; e += [pesos(r6["z"]), pesos(r6["y"][0]), pesos(r6["y"][1]), fmt(r6["holg"][2]), pesos(r6["valor_recursos"][0])]
    r7 = R["e7"]; e += [pesos(r7["y"][0]), "−$960", pesos(r7["z"]), fmt(r7["holg"][1]), pesos(-r7["costo_reducido"][2])]
    r8 = R["e8"]; e += [pesos(r8["y"][0]), pesos(r8["y"][4]), pesos(r8["z"]), fmt(r8["holg"][1]), pesos(-r8["costo_reducido"][1])]
    e9 = R["e9"]; e += [pesos(e9["z"]), pesos(e9["z_menos"])]
    e10 = R["e10"]; e += [pesos(e10["a"]["z"]), fmt(e10["b"]["holg"][1])]
    mod, C, r, A, b = K
    x = [Fr(v).limit_denominator(1000) for v in C["x"]]
    e += ["833,75", "294,375", "45.600", "1,5", "112,5", "1.052,5", "472,5", "2.520", "−250", pesos(r["z"]),
          "97.200", "3.318.750", "547.300", "326.025", "2.887,5", "697,5",
          fmt(r["holg"][0] / 3600, 2), fmt(r["holg"][3], 2), fmt(r["holg"][6], 3), fmt(sum(Fr(a) * xi for a, xi in zip(A[0], x)))]
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
    R = resultados()
    K = caso()
    imprimir(R, K)
    mod, C, r, A, b = K
    ok = r["optima"] and iguales(r["y"], C["precios_sombra"] + C["costo_reducido_cotas"]) and \
        iguales(r["holg"][:3], C["holguras"]) and abs(float(r["w"]) - C["z"]) < 1e-6 and \
        contra_u10(r["y"])
    print("\nCADENA:", "OK, la mezcla de la unidad 4 cumple holgura complementaria con los precios del caso" if ok else "NO calza")
    if not ok:
        sys.exit(1)
    if not verificar_opl(R, K):
        print("OPL: NO coincide"); sys.exit(1)
    if "--revisar" in sys.argv:
        md = (RAMO / "unidades" / "11-holgura-complementaria.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".").replace("\\$", "$")
        faltan = [x for x in esperados(R, K) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
