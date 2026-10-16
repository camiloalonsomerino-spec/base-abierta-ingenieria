"""Unidad 10 · Dualidad.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado y cada tabla aparezcan escritos tal cual en el .md.

    python u10_dualidad.py            # imprime los resultados
    python u10_dualidad.py --revisar  # además los busca en el .md

Cada par primal-dual se resuelve por tres caminos que tienen que coincidir: el simplex propio con
fracciones exactas (el de la unidad 9, `u09_dos_fases.py`), scipy (HiGHS) y, si hay CPLEX, los modelos
OPL de `modelos/` leyendo `.dual`. El dual se arma con las reglas de la unidad (función `dual`), no a
mano, y se exige que su óptimo sea igual al del primal (teorema fuerte).
"""
from fractions import Fraction as F
from pathlib import Path
import importlib.util, sys

from scipy.optimize import linprog

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent

spec = importlib.util.spec_from_file_location("u09", AQUI / "u09_dos_fases.py")
u09 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u09)
Problema, resolver, tabla_md, paso_md, num, fmt, pesos, correr = (
    u09.Problema, u09.resolver, u09.tabla_md, u09.paso_md, u09.num, u09.fmt, u09.pesos, u09.correr)


# ---------------------------------------------------------------- el dual con las reglas de la unidad

def dual(sentido, c, filas, signos):
    """Primal (sentido, c, filas [(a, tipo, b)], signos de las variables '+', '-' o 'libre').
    Devuelve el dual en el mismo formato, con los signos de sus variables.
    Máximo: ≤ → y ≥ 0 · ≥ → y ≤ 0 · = → y libre; x ≥ 0 → ≥ · x ≤ 0 → ≤ · x libre → =.
    Mínimo: al revés en las dos tablas."""
    m, n = len(filas), len(c)
    if sentido == "max":
        sig_y = {"<=": "+", ">=": "-", "=": "libre"}
        tipo_r = {"+": ">=", "-": "<=", "libre": "="}
        sd = "min"
    else:
        sig_y = {">=": "+", "<=": "-", "=": "libre"}
        tipo_r = {"+": "<=", "-": ">=", "libre": "="}
        sd = "max"
    cd = [b for a, t, b in filas]
    fd = [([filas[i][0][j] for i in range(m)], tipo_r[signos[j]], c[j]) for j in range(n)]
    sd_y = [sig_y[t] for a, t, b in filas]
    return sd, cd, fd, sd_y


def lp(sentido, c, filas, signos):
    """Resuelve con scipy; devuelve (estado, x, z, duales de las filas en el signo de la unidad)."""
    cc = [float(v) for v in c]
    if sentido == "max":
        cc = [-v for v in cc]
    Aub, bub, Aeq, beq, quien = [], [], [], [], []
    for i, (a, t, b) in enumerate(filas):
        a = [float(v) for v in a]
        if t == "<=":
            Aub.append(a); bub.append(float(b)); quien.append(("ub", len(Aub) - 1, 1))
        elif t == ">=":
            Aub.append([-v for v in a]); bub.append(-float(b)); quien.append(("ub", len(Aub) - 1, -1))
        else:
            Aeq.append(a); beq.append(float(b)); quien.append(("eq", len(Aeq) - 1, 1))
    cotas = {"+": (0, None), "-": (None, 0), "libre": (None, None)}
    r = linprog(cc, A_ub=Aub or None, b_ub=bub or None, A_eq=Aeq or None, b_eq=beq or None,
                bounds=[cotas[s] for s in signos], method="highs")
    if r.status != 0:
        return {2: "infactible", 3: "no acotado"}[r.status], None, None, None
    z = -r.fun if sentido == "max" else r.fun
    y = []
    for tipo, k, s in quien:
        marg = r.ineqlin.marginals[k] if tipo == "ub" else r.eqlin.marginals[k]
        # ∂z/∂b: linprog da ∂(fun)/∂(b_ub); el signo se corrige por el sentido y por la fila invertida
        v = marg * s
        y.append(-v if sentido == "max" else v)
    return "optima", list(r.x), z, y


def fuerte(nombre, sentido, c, filas, signos):
    """Teorema fuerte: el óptimo del primal y el del dual (armado con las reglas) coinciden, y los
    duales que reporta el solver del primal son la solución del dual."""
    e, x, z, y = lp(sentido, c, filas, signos)
    D = dual(sentido, c, filas, signos)
    ed, yd, w, xd = lp(*D)
    if e == "optima":
        assert ed == "optima" and abs(z - w) < 1e-6, (nombre, z, w)
        assert all(abs(a - b) < 1e-6 for a, b in zip(y, yd)), (nombre, y, yd)
        assert all(abs(a - b) < 1e-6 for a, b in zip(x, xd)), (nombre, x, xd)
    return {"estado": e, "x": x, "z": z, "y": y, "dual": D, "estado_dual": ed, "w": w, "y_dual": yd}


def leer_y(res, sentido="max"):
    """Precios del dual en la tabla final de un máximo con restricciones ≤: y_i = −c̄(s_i)."""
    ult = res["tablas"][-1]
    return [-ult["red"][ult["cols"].index(v)] for v in ult["cols"] if v.startswith("s")]


# ---------------------------------------------------------------- datos (originales; pasados por colisiones.py)

# Ejemplo · chocolatería: lotes de bombones (x1) y de tabletas (x2)
EJ = ("max", [8600, 4900], [([2, 1], "<=", 60), ([1, 1], "<=", 40), ([1, 0], "<=", 25)], ["+", "+"])
EJ_X_HAT, EJ_Y_HAT = [25, 10], [4900, 0, 0]          # un par factible para el teorema débil

E1 = ("max", [7, 5, 4], [([2, 1, 1], "<=", 40), ([1, 3, 2], "<=", 60)], ["+", "+", "+"])
E2 = ("min", [450, 380, 580], [([4, 2, 5], ">=", 40), ([1, 3, 1], ">=", 30)], ["+", "+", "+"])
E3 = ("min", [5, 3, -8], [([1, 1, -1], ">=", 6), ([2, -1, 1], "<=", 10), ([1, 2, 0], "=", 7)], ["libre", "+", "-"])
E4_X, E4_Y = [10, 10, 5], [4, 2]                      # par factible del 10.4 (sobre el 10.1)
E6 = {"a": ("max", [2, 1], [([1, -1], "<=", 4), ([1, -2], "<=", 2)], ["+", "+"]),
      "b": ("max", [1, 1], [([1, -1], "<=", -2), ([-1, 1], "<=", -1)], ["+", "+"])}
# 10.7 · taller de velas: velas (x1), jabones (x2), difusores (x3); horas de vertido, curado y empaque
E7 = ("max", [5200, 3600, 4300], [([3, 1, 2], "<=", 130), ([2, 1, 1], "<=", 70), ([1, 1, 2], "<=", 60)], ["+", "+", "+"])
E7_OFERTA_HORAS, E7_OFERTA_PRECIO = 10, 1150          # horas extra de curado y su precio por hora
E7_OFERTA_TOTAL = 220_000                             # oferta por toda la capacidad de la semana


def cargar_caso():
    s = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_lp.py")
    caso = importlib.util.module_from_spec(s)
    s.loader.exec_module(caso)
    return caso


# ---------------------------------------------------------------- resultados

def resultados():
    caso = cargar_caso()
    C = caso.calcular()
    R = {"C": C}

    # Ejemplo
    R["ej"] = fuerte("ejemplo", *EJ)
    R["ej_simplex"] = resolver(Problema("ej", EJ[0], EJ[1], EJ[2]), "directo")
    R["ej_y_tabla"] = leer_y(R["ej_simplex"])
    assert [float(v) for v in R["ej_y_tabla"]] == [3700, 1200, 0]
    assert R["ej_simplex"]["x"] == [20, 20]
    xh, yh = EJ_X_HAT, EJ_Y_HAT
    A = [f[0] for f in EJ[2]]; b = [f[2] for f in EJ[2]]
    assert all(sum(a * x for a, x in zip(fila, xh)) <= bi for fila, bi in zip(A, b))
    assert all(sum(A[i][j] * yh[i] for i in range(3)) >= EJ[1][j] for j in range(2))
    R["ej_zhat"] = sum(c * x for c, x in zip(EJ[1], xh))
    R["ej_what"] = sum(bi * y for bi, y in zip(b, yh))
    R["ej_opl"] = None

    # 10.1 · 10.4 · 10.5
    R["e1"] = fuerte("10.1", *E1)
    R["e1_simplex"] = resolver(Problema("10.1", E1[0], E1[1], E1[2]), "directo")
    R["e1_y_tabla"] = leer_y(R["e1_simplex"])
    ult = R["e1_simplex"]["tablas"][-1]
    R["e1_cbar_x3"] = ult["red"][ult["cols"].index("x3")]
    A1 = [f[0] for f in E1[2]]; b1 = [f[2] for f in E1[2]]
    assert all(sum(a * x for a, x in zip(fila, E4_X)) <= bi for fila, bi in zip(A1, b1))
    assert all(sum(A1[i][j] * E4_Y[i] for i in range(2)) >= E1[1][j] for j in range(3))
    R["e4_z"] = sum(c * x for c, x in zip(E1[1], E4_X))
    R["e4_w"] = sum(bi * y for bi, y in zip(b1, E4_Y))
    R["e4_brecha"] = R["e4_w"] - R["e4_z"]

    # 10.2 · 10.9 (el dual del 10.2 resuelto con simplex, sin artificiales)
    R["e2"] = fuerte("10.2", *E2)
    D2 = dual(*E2)
    R["e9_simplex"] = resolver(Problema("10.9", D2[0], D2[1], D2[2], nombres_x=["y1", "y2"]), "directo")
    ult = R["e9_simplex"]["tablas"][-1]
    R["e9_x_tabla"] = [-ult["red"][ult["cols"].index(v)] for v in ult["cols"] if v.startswith("s")]
    assert all(abs(float(a) - b) < 1e-9 for a, b in zip(R["e9_x_tabla"], R["e2"]["x"]))
    assert abs(float(R["e9_simplex"]["z"]) - R["e2"]["z"]) < 1e-9

    # 10.3
    R["e3"] = fuerte("10.3", *E3)

    # 10.6
    R["e6"] = {k: (lp(*p)[0], lp(*dual(*p))[0]) for k, p in E6.items()}
    assert R["e6"]["a"] == ("no acotado", "infactible") and R["e6"]["b"] == ("infactible", "infactible")

    # 10.7
    R["e7"] = fuerte("10.7", *E7)
    y7 = R["e7"]["y"]
    A7 = [f[0] for f in E7[2]]; b7 = [f[2] for f in E7[2]]
    R["e7_holguras"] = [bi - sum(a * x for a, x in zip(fila, R["e7"]["x"])) for fila, bi in zip(A7, b7)]
    R["e7_cbar"] = [E7[1][j] - sum(A7[i][j] * y7[i] for i in range(3)) for j in range(3)]
    R["e7_ganancia_oferta"] = E7_OFERTA_HORAS * (y7[1] - E7_OFERTA_PRECIO)
    # se comprueba re-resolviendo con 10 horas más de curado (el precio sombra vale en ese tramo)
    filas = [list(f) for f in E7[2]]
    filas[1] = (filas[1][0], "<=", filas[1][2] + E7_OFERTA_HORAS)
    z_mas = lp(E7[0], E7[1], filas, E7[3])[2]
    assert abs(z_mas - R["e7"]["z"] - E7_OFERTA_HORAS * y7[1]) < 1e-6
    R["e7_z_mas"] = z_mas

    # 10.8 · el dual del sustrato de la unidad 9, leído de su tabla final
    R9 = {"ej_m": u09.resolver(u09.EJEMPLO, "gran_m")}
    ult = R9["ej_m"]["tablas"][-1]
    red = dict(zip(ult["cols"], ult["red"]))
    # con la gran M, la columna de a_i trae M − y_i (mínimo): y_i = M − c̄(a_i); y la de e_2 trae y_2
    R["e8_y"] = [F(0) - red["a1"].a, F(0) - red["a2"].a, F(0) - red["s3"].a]
    assert red["a1"].b == 1 and red["a2"].b == 1
    assert red["e2"].a == R["e8_y"][1] and red["e2"].b == 0
    p9 = u09.EJEMPLO
    R["e8"] = fuerte("10.8", "min", p9.c, p9.filas, ["+", "+"])
    assert all(abs(float(a) - b) < 1e-9 for a, b in zip(R["e8_y"], R["e8"]["y"]))
    R["e8_w"] = sum(f[2] * y for f, y in zip(p9.filas, R["e8_y"]))

    # 10.10 · el dual del caso con el compromiso de la unidad 9
    pc = u09.problema_caso(caso)
    R["e10"] = fuerte("10.10", "max", pc.c, pc.filas, ["+", "+"])
    rc = u09.resolver(pc, "dos_fases")
    ult = rc["tablas"][-1]
    red = dict(zip(ult["cols"], ult["red"]))
    R["e10_y_tabla"] = [-red["s1"], -red["s2"], -red["s3"], red["e4"]]
    assert all(abs(float(a) - b) < 1e-9 for a, b in zip(R["e10_y_tabla"], R["e10"]["y"]))
    R["e10_w"] = sum(f[2] * y for f, y in zip(pc.filas, R["e10_y_tabla"]))

    # Caso · dual de la versión de dos productos (u2)
    d = caso.DOS
    P2 = ("max", d["margen"], [(d["est"], "<=", d["cap_est"]), (d["pla"], "<=", d["cap_pla"]),
                               ([0, 1], "<=", d["dem_polerones"])], ["+", "+"])
    R["u2"] = fuerte("u2", *P2)
    R["u2_simplex"] = resolver(Problema("u2", P2[0], P2[1], P2[2]), "directo")
    R["u2_y_tabla"] = leer_y(R["u2_simplex"])
    R["u2_hora"] = [float(y) * 3600 for y in R["u2_y_tabla"][:2]]
    # Caso · dual de la mezcla completa (u4): tres capacidades y cinco demandas máximas
    filas4 = [(caso.SEG_EST, "<=", caso.CAP["estampado_s"]), (caso.SEG_PLA, "<=", caso.CAP["planchado_s"]),
              (caso.TINTA_G, "<=", caso.CAP["tinta_g"])]
    for j in range(5):
        filas4.append(([1 if k == j else 0 for k in range(5)], "<=", caso.DEMANDA_MAX[j]))
    R["u4"] = fuerte("u4", "max", caso.MARGEN, filas4, ["+"] * 5)
    y4 = R["u4"]["y"]
    b4 = [f[2] for f in filas4]
    R["u4_aportes"] = [bi * yi for bi, yi in zip(b4, y4)]
    A4 = [caso.SEG_EST, caso.SEG_PLA, caso.TINTA_G]
    R["u4_valor_recursos"] = [sum(A4[r][j] * y4[r] for r in range(3)) for j in range(5)]
    R["u4_holgura_dual"] = [R["u4_valor_recursos"][j] + y4[3 + j] - caso.MARGEN[j] for j in range(5)]
    R["opl"] = comprobar_opl(R)
    return R


def comprobar_opl(R):
    M = RAMO / "modelos"
    r = correr(M / "u10_chocolateria.mod")
    if r is None:
        print("OPL: no hay CPLEX en este equipo; se sigue con scipy")
        return None
    hechos = []

    def igual(a, b):
        assert abs(a - b) < 1e-6, (a, b)

    v = r["valores"]
    igual(r["objetivo"], R["ej"]["z"])
    for k, y in zip(["y_templado", "y_empaque", "y_bombones"], R["ej"]["y"]):
        igual(v[k], y)
    rd = correr(M / "u10_chocolateria_dual.mod")
    igual(rd["objetivo"], R["ej"]["z"])
    igual(rd["valores"]["x_bombones"], 20); igual(rd["valores"]["x_tabletas"], 20)
    hechos.append("chocolatería primal y dual")
    r = correr(M / "u10_dos_productos.mod"); rd = correr(M / "u10_dual_dos_productos.mod")
    igual(r["objetivo"], R["u2"]["z"]); igual(rd["objetivo"], R["u2"]["z"])
    for k, y in zip(["y_estampado", "y_planchado", "y_demanda"], R["u2"]["y"]):
        igual(r["valores"][k], y); igual(rd["valores"][k], y)
    hechos.append("dos productos primal y dual")
    dat = M / "u10_mezcla.dat"
    r = correr(M / "u10_mezcla.mod", dat); rd = correr(M / "u10_dual_mezcla.mod", dat)
    igual(r["objetivo"], R["u4"]["z"]); igual(rd["objetivo"], R["u4"]["z"])
    claves = ["y_estampado", "y_planchado", "y_tinta"] + [f"u_{p}" for p in ["poleras", "polerones", "doble", "bolsas", "gorros"]]
    for k, y in zip(claves, R["u4"]["y"]):
        igual(r["valores"][k], y); igual(rd["valores"][k], y)
    hechos.append("mezcla primal y dual")
    r = correr(M / "u09_compromiso.mod")
    for k, y in zip(["dual_estampado", "dual_planchado", "dual_demanda", "dual_compromiso"], R["e10"]["y"]):
        igual(r["valores"][k], y)
    r = correr(M / "u09_sustrato.mod")
    for k, y in zip(["dual_volumen", "dual_nitrogeno", "dual_compost"], R["e8"]["y"]):
        igual(r["valores"][k], y)
    hechos.append("compromiso y sustrato (modelos de la unidad 9)")
    return hechos


def imprimir(R):
    def par(nombre, P):
        print(f"\n== {nombre}: {P['estado']} · x = {P['x']} · z = {P['z']} · y = {P['y']} · w = {P['w']}")
        print("   dual:", P["dual"])
    par("Ejemplo", R["ej"])
    for t in R["ej_simplex"]["tablas"]:
        print(tabla_md(t)); print(paso_md(t)); print()
    print("y de la tabla:", [num(v) for v in R["ej_y_tabla"]], "· par débil:", R["ej_zhat"], R["ej_what"])
    par("10.1", R["e1"])
    print(tabla_md(R["e1_simplex"]["tablas"][-1]))
    print("y de la tabla:", [num(v) for v in R["e1_y_tabla"]], "c̄ x3:", num(R["e1_cbar_x3"]))
    print("10.4: z =", R["e4_z"], "w =", R["e4_w"], "brecha", R["e4_brecha"])
    par("10.2", R["e2"])
    par("10.3", R["e3"])
    print("\n10.6:", R["e6"])
    par("10.7", R["e7"])
    print("   holguras", R["e7_holguras"], "c̄", R["e7_cbar"], "ganancia oferta", R["e7_ganancia_oferta"], "z con 10 h", R["e7_z_mas"])
    par("10.8", R["e8"])
    print("   y de la tabla de la unidad 9:", [num(v) for v in R["e8_y"]], "w =", num(R["e8_w"]))
    print("\n10.9 · el dual del 10.2 con simplex")
    for t in R["e9_simplex"]["tablas"]:
        print(tabla_md(t)); print(paso_md(t)); print()
    print("x leído de la tabla del dual:", [num(v) for v in R["e9_x_tabla"]])
    par("10.10", R["e10"])
    print("   y de la tabla de la unidad 9:", [num(v) for v in R["e10_y_tabla"]], "w =", num(R["e10_w"]))
    par("Caso u2", R["u2"])
    print(tabla_md(R["u2_simplex"]["tablas"][-1]))
    print("   y por hora:", R["u2_hora"])
    par("Caso u4", R["u4"])
    print("   aportes b·y:", R["u4_aportes"])
    print("   valor en recursos:", R["u4_valor_recursos"], "holgura dual:", R["u4_holgura_dual"])
    print("\nOPL:", R["opl"])


def esperados(R):
    e = []
    e += [tabla_md(t) for t in R["ej_simplex"]["tablas"]] + [paso_md(t) for t in R["ej_simplex"]["tablas"]]
    e += [tabla_md(R["e1_simplex"]["tablas"][-1]), tabla_md(R["u2_simplex"]["tablas"][-1])]
    e += [tabla_md(t) for t in R["e9_simplex"]["tablas"]] + [paso_md(t) for t in R["e9_simplex"]["tablas"]]
    e += [pesos(R["ej"]["z"]), pesos(R["ej_zhat"]), pesos(R["ej_what"]), pesos(3700), pesos(1200)]
    e += [num(v) for v in R["e1_y_tabla"]] + [num(R["e1_cbar_x3"]), num(R["e4_z"]), num(R["e4_w"]), num(R["e4_brecha"])]
    e += [pesos(R["e2"]["z"]), pesos(R["e2"]["y"][0]), pesos(R["e2"]["y"][1])]
    e += [fmt(R["e3"]["z"]), fmt(R["e3"]["y"][0]), u09.menos(fmt(R["e3"]["y"][2]))]
    e += [pesos(R["e7"]["z"]), pesos(R["e7"]["y"][1]), pesos(R["e7"]["y"][2]), pesos(abs(R["e7_cbar"][2])),
          pesos(R["e7_ganancia_oferta"]), pesos(R["e7_z_mas"]), pesos(E7_OFERTA_TOTAL)]
    e += [num(v) for v in R["e8_y"][:2]] + [pesos(R["e8_w"])]
    e += [num(v) for v in R["e9_x_tabla"][:2]]
    e += [pesos(R["e10_w"]), num(R["e10_y_tabla"][0]), num(R["e10_y_tabla"][3])]
    e += ["98/3", pesos(R["u2"]["z"]), pesos(R["u2_hora"][0]), pesos(R["u2_hora"][1])]
    e += [pesos(R["u4"]["z"])] + [pesos(a) for a in R["u4_aportes"] if a > 0]
    e += [fmt(R["u4"]["y"][4], 1), fmt(R["u4"]["y"][7], 1), fmt(R["u4"]["y"][1], 1), fmt(R["u4"]["y"][2], 1)]
    e += [pesos(R["u4"]["y"][1] * 3600), fmt(R["u4_holgura_dual"][2])]
    return e


def cadena(R):
    C = R["C"]
    ok = all(abs(a - b) < 1e-6 for a, b in zip(R["u2"]["y"][:2], C["u2"]["duales"]))
    ok &= abs(R["u2"]["w"] - C["u2"]["z"]) < 1e-6
    ok &= all(abs(a - b) < 1e-6 for a, b in zip(R["u4"]["y"][:3], C["u4"]["precios_sombra"]))
    ok &= all(abs(a - b) < 1e-6 for a, b in zip(R["u4"]["y"][3:], C["u4"]["costo_reducido_cotas"]))
    ok &= abs(R["u4"]["w"] - C["u4"]["z"]) < 1e-6
    print("\nCADENA:", "OK, los duales calzan con los precios sombra del caso (unidades 2 y 4)" if ok else "NO calza")
    return ok


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if not cadena(R):
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (RAMO / "unidades" / "10-dualidad.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}:")
        for x in faltan:
            print("  ·", x[:300].replace("\n", " ⏎ "))
        sys.exit(1 if faltan else 0)
