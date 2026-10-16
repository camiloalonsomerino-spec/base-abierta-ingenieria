"""Unidad 9 · ANOVA de varios factores, interacciones y supuestos.

Recalcula todas las cifras de la unidad desde los datos (a mano, con las fórmulas de la tabla ANOVA
de dos factores, y con statsmodels, y exige que coincidan), genera los gráficos de `unidades/figuras/`
y el CSV del ejemplo en `datos/`, ejecuta el cuaderno `notebooks/u09_anova_factorial.ipynb`, compara
la pieza del caso con `caso_estampa_sur_datos.py` y, con --revisar, busca cada cifra en el .md.

    python u09_anova_factorial.py            # imprime los resultados
    python u09_anova_factorial.py --revisar  # además los busca en el .md
"""
from pathlib import Path
import importlib.util, io, json, os, sys, contextlib, warnings

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.oneway import anova_oneway
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
DATOS = RAMO / "datos"
FIG = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "09-anova-varios-factores.md"
CUADERNO = RAMO / "notebooks" / "u09_anova_factorial.ipynb"


# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    s = f"{x:,.{dec}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return "0" + s[2:] if s.startswith("-0") and float(x) == 0 else s


def fp(p, dec=3):
    """Valor p como se escribe en el texto: «p < 0,001» o «p = 0,467»."""
    return "p < 0,001" if p < 0.001 else f"p = {fmt(p, dec)}"


def anova2_mano(celdas, A, B):
    """ANOVA de dos factores balanceado con las fórmulas de la tabla (sin statsmodels).
    celdas[(a, b)] = lista de n observaciones."""
    a, b = len(A), len(B)
    n = len(celdas[(A[0], B[0])])
    assert all(len(v) == n for v in celdas.values()), "el cálculo a mano es para el caso balanceado"
    m = {k: float(np.mean(v)) for k, v in celdas.items()}
    mA = {i: np.mean([m[(i, j)] for j in B]) for i in A}
    mB = {j: np.mean([m[(i, j)] for i in A]) for j in B}
    g = float(np.mean(list(m.values())))
    sca = b * n * sum((mA[i] - g) ** 2 for i in A)
    scb = a * n * sum((mB[j] - g) ** 2 for j in B)
    inter = {(i, j): m[(i, j)] - mA[i] - mB[j] + g for i in A for j in B}
    scab = n * sum(v ** 2 for v in inter.values())
    sce = sum((y - m[k]) ** 2 for k, v in celdas.items() for y in v)
    sct = sum((y - g) ** 2 for v in celdas.values() for y in v)
    assert abs(sct - (sca + scb + scab + sce)) < 1e-8
    gl = {"A": a - 1, "B": b - 1, "AB": (a - 1) * (b - 1), "E": a * b * (n - 1), "T": a * b * n - 1}
    mce = sce / gl["E"]
    T = {"n": n, "medias": m, "mA": mA, "mB": mB, "g": g, "inter": inter, "gl": gl,
         "SC": {"A": sca, "B": scb, "AB": scab, "E": sce, "T": sct}, "MCE": mce}
    T["CM"] = {k: T["SC"][k] / gl[k] for k in ("A", "B", "AB", "E")}
    T["F"] = {k: T["CM"][k] / mce for k in ("A", "B", "AB")}
    T["p"] = {k: float(stats.f.sf(T["F"][k], gl[k], gl["E"])) for k in ("A", "B", "AB")}
    T["Fcrit"] = {k: float(stats.f.ppf(0.95, gl[k], gl["E"])) for k in ("A", "B", "AB")}
    T["eta2p"] = {k: T["SC"][k] / (T["SC"][k] + sce) for k in ("A", "B", "AB")}
    return T


def a_df(celdas, nA="A", nB="B", ny="y"):
    filas = [{nA: i, nB: j, ny: y} for (i, j), v in celdas.items() for y in v]
    return pd.DataFrame(filas)


def anova_sm(df, ny, nA, nB, typ=2):
    mod = smf.ols(f"{ny} ~ C({nA}) * C({nB})", data=df).fit()
    return mod, sm.stats.anova_lm(mod, typ=typ)


def coincide(T, tab, nA, nB):
    """El cálculo a mano y statsmodels dan lo mismo."""
    filas = {"A": f"C({nA})", "B": f"C({nB})", "AB": f"C({nA}):C({nB})", "E": "Residual"}
    for k, f in filas.items():
        assert abs(tab.loc[f, "sum_sq"] - T["SC"][k]) < 1e-6, (k, tab.loc[f, "sum_sq"], T["SC"][k])
        if k != "E":
            assert abs(tab.loc[f, "F"] - T["F"][k]) < 1e-6


# ---------------------------------------------------------------- datos (originales; pasados por herramientas/colisiones.py)

# Ejemplo resuelto · taller de impresión 3D de Temuco: resistencia a la tracción (MPa) de una probeta
# según material (PLA, PETG) y orientación de impresión (horizontal, vertical), 3 probetas por celda
EJ_A, EJ_B = ["PLA", "PETG"], ["horizontal", "vertical"]
EJ = {("PLA", "horizontal"): [44, 48, 46], ("PLA", "vertical"): [31, 28, 31],
      ("PETG", "horizontal"): [51, 54, 51], ("PETG", "vertical"): [45, 44, 43]}

# 9.1 · lavandería industrial de Chillán: consumo de agua por carga; 3 programas × 2 tipos de carga, n = 4
E1 = {"a": 3, "b": 2, "n": 4, "SC_A": 58.6, "SC_B": 21.3, "SC_AB": 4.2, "SC_T": 131.5}

# 9.2 · call center: tiempo medio de atención (min) por canal y turno (medias de celda)
E2_A, E2_B = ["teléfono", "chat"], ["mañana", "tarde", "noche"]
E2 = {("teléfono", "mañana"): 6.2, ("teléfono", "tarde"): 6.8, ("teléfono", "noche"): 7.9,
      ("chat", "mañana"): 8.1, ("chat", "tarde"): 8.7, ("chat", "noche"): 11.0}

# 9.3 · taller de bicicletas: minutos para cambiar una cadena, técnico × tipo de bicicleta, n = 2
E3_A, E3_B = ["Ana", "Benjamín"], ["ruta", "montaña"]
E3 = {("Ana", "ruta"): [12, 14], ("Ana", "montaña"): [17, 19],
      ("Benjamín", "ruta"): [15, 15], ("Benjamín", "montaña"): [24, 22]}

# 9.4 · viña: 4 clones × 3 tipos de poda, n = 3 (y la variante sin réplicas, n = 1)
E4 = {"a": 4, "b": 3, "n": 3}

# 9.5 · panadería: minutos de fermentación según levadura y temperatura de la sala, n = 3
E5_A, E5_B = ["fresca", "seca"], ["22 °C", "26 °C", "30 °C"]
E5 = {("fresca", "22 °C"): [92, 88, 95], ("fresca", "26 °C"): [74, 78, 73], ("fresca", "30 °C"): [61, 66, 62],
      ("seca", "22 °C"): [101, 97, 99], ("seca", "26 °C"): [84, 80, 85], ("seca", "30 °C"): [70, 72, 67]}

# 9.6 · empacadora de arándanos: peso (g) de cajas de 125 g, máquina × turno, n = 5.
# El último dato de M1-noche se digitó 152,4 en vez de 125,4.
E6_A, E6_B = ["M1", "M2"], ["día", "noche"]
E6 = {("M1", "día"): [125.8, 126.1, 125.5, 126.4, 125.9], ("M1", "noche"): [126.2, 125.7, 126.6, 126.0, 152.4],
      ("M2", "día"): [127.1, 126.8, 127.5, 126.9, 127.3], ("M2", "noche"): [127.0, 127.6, 126.7, 127.4, 127.2]}
E6_BIEN = 125.4

# 9.7 · tiempo de respuesta (ms) de una API según servidor y tamaño de la consulta, n = 4
E7_A, E7_B = ["estándar", "optimizado"], ["chica", "grande"]
E7 = {("estándar", "chica"): [38, 44, 41, 36], ("estándar", "grande"): [131, 108, 124, 115],
      ("optimizado", "chica"): [21, 18, 22, 19], ("optimizado", "grande"): [57, 66, 54, 63]}

# 9.8 · rendimiento de trigo (qq/ha): medias de celda, n = 4 por celda, MCE = 6,8 con 12 gl
E8 = {"medias": {("secano", "sin"): 38.2, ("secano", "con"): 41.0, ("riego", "sin"): 52.4, ("riego", "con"): 63.8},
      "n": 4, "MCE": 6.8, "glE": 12}

# 9.9 · tienda en línea (estudio observacional, desbalanceado): monto del pedido (miles de $)
E9 = {("normal", "Santiago"): [12, 14, 13, 15, 11, 13], ("normal", "regiones"): [9, 10],
      ("express", "Santiago"): [16, 18], ("express", "regiones"): [13, 12, 14, 15, 13, 12]}

# 9.10 · días de entrega de tres transportistas (un factor, varianzas distintas, n distinto)
E10 = {"A": [2.14, 2.38, 2.21, 2.02, 2.33, 2.19],
       "B": [3.46, 1.83, 4.87, 2.25, 5.61, 1.42, 3.94, 2.68],
       "C": [2.81, 2.93, 3.07, 2.74, 3.02]}


# ---------------------------------------------------------------- caso

def cargar_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_datos.py")
    caso = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caso)
    return caso


CASO_A = ["plastisol", "agua", "descarga"]
CASO_B = ["150 °C", "170 °C"]


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # Ejemplo
    T = anova2_mano(EJ, EJ_A, EJ_B)
    df = a_df(EJ, "material", "orientacion", "resistencia")
    mod, tab = anova_sm(df, "resistencia", "material", "orientacion")
    coincide(T, tab, "material", "orientacion")
    tab1 = sm.stats.anova_lm(mod, typ=1)
    assert np.allclose(tab1["sum_sq"].values, tab["sum_sq"].values), "balanceado: tipo I = tipo II"
    # forma matricial con codificación de referencia (PLA y horizontal son la referencia)
    filas = [(i, j, y) for (i, j), v in EJ.items() for y in v]
    X = np.array([[1, i == "PETG", j == "vertical", (i == "PETG") and (j == "vertical")] for i, j, _ in filas], float)
    y = np.array([f[2] for f in filas], float)
    XtX, Xty = X.T @ X, X.T @ y
    beta = np.linalg.solve(XtX, Xty)
    m = T["medias"]
    b_celdas = [m[("PLA", "horizontal")], m[("PETG", "horizontal")] - m[("PLA", "horizontal")],
                m[("PLA", "vertical")] - m[("PLA", "horizontal")],
                (m[("PETG", "vertical")] - m[("PETG", "horizontal")]) - (m[("PLA", "vertical")] - m[("PLA", "horizontal")])]
    assert np.allclose(beta, b_celdas)
    assert np.allclose(X @ beta, mod.fittedvalues.values)   # statsmodels usa otra referencia (alfabética), mismo ajuste
    res = y - X @ beta
    lev = stats.levene(*[EJ[k] for k in EJ])
    sh = stats.shapiro(mod.resid)
    # efectos simples de la orientación dentro de cada material (con el MCE del modelo completo)
    ee_simple = np.sqrt(T["MCE"] * 2 / T["n"])
    simples = {mat: (m[(mat, "horizontal")] - m[(mat, "vertical")]) / ee_simple for mat in EJ_A}
    R["ej"] = {"T": T, "XtX": XtX, "Xty": Xty, "beta": beta, "levene": lev, "shapiro": sh,
               "resid_sc": float(res @ res), "ee_simple": ee_simple, "simples": simples,
               "t_crit": float(stats.t.ppf(0.975, T["gl"]["E"])), "df": df}

    # 9.1
    e = dict(E1)
    e["SC_E"] = e["SC_T"] - e["SC_A"] - e["SC_B"] - e["SC_AB"]
    gl = {"A": e["a"] - 1, "B": e["b"] - 1, "AB": (e["a"] - 1) * (e["b"] - 1), "E": e["a"] * e["b"] * (e["n"] - 1)}
    e["gl"] = gl
    e["MCE"] = e["SC_E"] / gl["E"]
    e["CM"] = {k: e[f"SC_{k}"] / gl[k] for k in ("A", "B", "AB")}
    e["F"] = {k: e["CM"][k] / e["MCE"] for k in e["CM"]}
    e["p"] = {k: float(stats.f.sf(e["F"][k], gl[k], gl["E"])) for k in e["F"]}
    e["Fcrit"] = {k: float(stats.f.ppf(0.95, gl[k], gl["E"])) for k in e["F"]}
    R["e1"] = e

    # 9.2
    mA = {i: np.mean([E2[(i, j)] for j in E2_B]) for i in E2_A}
    mB = {j: np.mean([E2[(i, j)] for i in E2_A]) for j in E2_B}
    g = np.mean(list(E2.values()))
    inter = {(i, j): E2[(i, j)] - mA[i] - mB[j] + g for i in E2_A for j in E2_B}
    dif = {j: E2[("chat", j)] - E2[("teléfono", j)] for j in E2_B}
    R["e2"] = {"mA": mA, "mB": mB, "g": g, "inter": inter, "dif": dif}

    # 9.3
    T3 = anova2_mano(E3, E3_A, E3_B)
    filas3 = [(i, j, yy) for (i, j), v in E3.items() for yy in v]
    X3 = np.array([[1, i == "Benjamín", j == "montaña", (i == "Benjamín") and (j == "montaña")] for i, j, _ in filas3], float)
    y3 = np.array([f[2] for f in filas3], float)
    b3 = np.linalg.solve(X3.T @ X3, X3.T @ y3)
    R["e3"] = {"T": T3, "X": X3, "beta": b3, "XtX": X3.T @ X3}

    # 9.4
    a, b, n = E4["a"], E4["b"], E4["n"]
    gl4 = {"A": a - 1, "B": b - 1, "AB": (a - 1) * (b - 1), "E": a * b * (n - 1), "T": a * b * n - 1}
    R["e4"] = {"gl": gl4, "Fcrit": {k: float(stats.f.ppf(0.95, gl4[k], gl4["E"])) for k in ("A", "B", "AB")},
               "glE_n1_inter": a * b * (1 - 1), "glE_n1_aditivo": (a - 1) * (b - 1),
               "Fcrit_n1": {k: float(stats.f.ppf(0.95, gl4[k], (a - 1) * (b - 1))) for k in ("A", "B")}}

    # 9.5
    T5 = anova2_mano(E5, E5_A, E5_B)
    _, tab5 = anova_sm(a_df(E5), "y", "A", "B")
    coincide(T5, tab5, "A", "B")
    # Tukey sobre las temperaturas (marginales, sin interacción) con el MCE del modelo de dos factores
    q5 = float(stats.studentized_range.ppf(0.95, 3, T5["gl"]["E"]))
    hsd5 = q5 * np.sqrt(T5["MCE"] / (len(E5_A) * T5["n"]))
    R["e5"] = {"T": T5, "q": q5, "hsd": hsd5}

    # 9.6
    T6 = anova2_mano(E6, E6_A, E6_B)
    m6, _ = anova_sm(a_df(E6), "y", "A", "B")
    r6 = m6.resid.values
    rstd6 = r6 / np.sqrt(T6["MCE"])
    sh6 = stats.shapiro(r6)
    lev6 = stats.levene(*[E6[k] for k in E6])
    E6c = {k: list(v) for k, v in E6.items()}
    E6c[("M1", "noche")][-1] = E6_BIEN
    T6c = anova2_mano(E6c, E6_A, E6_B)
    m6c, _ = anova_sm(a_df(E6c), "y", "A", "B")
    sh6c = stats.shapiro(m6c.resid.values)
    lev6c = stats.levene(*[E6c[k] for k in E6c])
    R["e6"] = {"T": T6, "rmax": float(r6.max()), "rstd_max": float(rstd6.max()), "sh": sh6, "lev": lev6,
               "Tc": T6c, "shc": sh6c, "levc": lev6c, "rstd_max_c": float(np.max(np.abs(m6c.resid.values)) / np.sqrt(T6c["MCE"]))}

    # 9.7
    T7 = anova2_mano(E7, E7_A, E7_B)
    E7l = {k: [float(np.log(y)) for y in v] for k, v in E7.items()}
    T7l = anova2_mano(E7l, E7_A, E7_B)
    var7 = {k: float(np.var(v, ddof=1)) for k, v in E7.items()}
    lev7 = stats.levene(*[E7[k] for k in E7])
    lev7l = stats.levene(*[E7l[k] for k in E7l])
    razon7 = max(var7.values()) / min(var7.values())
    var7l = {k: float(np.var(v, ddof=1)) for k, v in E7l.items()}
    razon7l = max(var7l.values()) / min(var7l.values())
    # efecto del servidor en la escala original del log: razón de medias geométricas
    efecto_serv = float(np.exp(T7l["mA"]["optimizado"] - T7l["mA"]["estándar"]))
    R["e7"] = {"T": T7, "Tl": T7l, "var": var7, "razon": razon7, "razon_l": razon7l, "lev": lev7, "levl": lev7l,
               "efecto_serv": efecto_serv}

    # 9.8
    m8 = E8["medias"]
    ee8 = np.sqrt(E8["MCE"] * 2 / E8["n"])
    t8 = {r: (m8[(r, "con")] - m8[(r, "sin")]) / ee8 for r in ("secano", "riego")}
    p8 = {r: float(2 * stats.t.sf(abs(t), E8["glE"])) for r, t in t8.items()}
    tc8 = float(stats.t.ppf(0.975, E8["glE"]))
    tc8b = float(stats.t.ppf(1 - 0.05 / 4, E8["glE"]))   # Bonferroni con dos comparaciones
    inter8 = (m8[("riego", "con")] - m8[("riego", "sin")]) - (m8[("secano", "con")] - m8[("secano", "sin")])
    F8 = inter8 ** 2 / (E8["MCE"] * 4 / E8["n"])          # contraste de interacción 2×2: F = c²/(MCE Σc²/n)
    R["e8"] = {"ee": ee8, "t": t8, "p": p8, "tc": tc8, "tcb": tc8b, "inter": inter8, "F": F8,
               "pF": float(stats.f.sf(F8, 1, E8["glE"])),
               "ic": {r: (m8[(r, "con")] - m8[(r, "sin")] - tc8 * ee8, m8[(r, "con")] - m8[(r, "sin")] + tc8 * ee8) for r in t8}}

    # 9.9
    df9 = a_df(E9, "envio", "region", "monto")
    mod9 = smf.ols("monto ~ C(envio) * C(region)", data=df9).fit()
    mod9b = smf.ols("monto ~ C(region) * C(envio)", data=df9).fit()
    t1a = sm.stats.anova_lm(mod9, typ=1)
    t1b = sm.stats.anova_lm(mod9b, typ=1)
    t2 = sm.stats.anova_lm(mod9, typ=2)
    medias9 = {k: float(np.mean(v)) for k, v in E9.items()}
    marg_envio_bruto = {e: float(df9[df9.envio == e].monto.mean()) for e in ("normal", "express")}
    marg_envio_celdas = {e: np.mean([medias9[(e, r)] for r in ("Santiago", "regiones")]) for e in ("normal", "express")}
    # segundo camino para el tipo I: diferencia de SCE entre modelos anidados
    sce0 = smf.ols("monto ~ 1", data=df9).fit().ssr
    sce_e = smf.ols("monto ~ C(envio)", data=df9).fit().ssr
    sce_r = smf.ols("monto ~ C(region)", data=df9).fit().ssr
    sce_er = smf.ols("monto ~ C(envio) + C(region)", data=df9).fit().ssr
    assert abs((sce0 - sce_e) - t1a.loc["C(envio)", "sum_sq"]) < 1e-9
    assert abs((sce_r - sce_er) - t2.loc["C(envio)", "sum_sq"]) < 1e-9
    assert abs((sce_e - sce_er) - t2.loc["C(region)", "sum_sq"]) < 1e-9
    R["e9"] = {"t1a": t1a, "t1b": t1b, "t2": t2, "medias": medias9, "bruto": marg_envio_bruto, "celdas": marg_envio_celdas,
               "n": {k: len(v) for k, v in E9.items()}}

    # 9.10
    grupos = [E10[k] for k in ("A", "B", "C")]
    clas = stats.f_oneway(*grupos)
    welch = anova_oneway(grupos, use_var="unequal")
    # Welch a mano
    n_ = np.array([len(g) for g in grupos], float)
    m_ = np.array([np.mean(g) for g in grupos])
    v_ = np.array([np.var(g, ddof=1) for g in grupos])
    w = n_ / v_
    mw = (w * m_).sum() / w.sum()
    k = len(grupos)
    lam = ((1 - w / w.sum()) ** 2 / (n_ - 1)).sum()
    Fw = ((w * (m_ - mw) ** 2).sum() / (k - 1)) / (1 + 2 * (k - 2) / (k ** 2 - 1) * lam)
    gl2w = (k ** 2 - 1) / (3 * lam)
    assert abs(Fw - welch.statistic) < 1e-9 and abs(gl2w - welch.df[1]) < 1e-9
    kw = stats.kruskal(*grupos)
    lev10 = stats.levene(*grupos)
    R["e10"] = {"clas": clas, "Fw": Fw, "gl2w": gl2w, "pw": float(welch.pvalue), "kw": kw, "lev": lev10,
                "m": m_, "v": v_, "s": np.sqrt(v_), "n": n_}

    # Caso · secado según tinta y temperatura (datos del caso en datos/secado.csv)
    s = pd.read_csv(DATOS / "secado.csv")
    celdas = {(t, c): list(s[(s.tinta == t) & (s.temperatura == c)].secado_min) for t in CASO_A for c in CASO_B}
    Tc = anova2_mano(celdas, CASO_A, CASO_B)
    modc = smf.ols("secado_min ~ C(tinta) * C(temperatura)", data=s).fit()
    tabc = sm.stats.anova_lm(modc, typ=2)
    coincide(Tc, tabc, "tinta", "temperatura")
    lev_tinta = stats.levene(*[g.secado_min for _, g in s.groupby("tinta")])
    lev_celdas = stats.levene(*[celdas[k] for k in celdas])
    sh_c = stats.shapiro(modc.resid)
    # un factor (U7) frente a dos factores
    m1 = smf.ols("secado_min ~ C(tinta)", data=s).fit()
    a1 = sm.stats.anova_lm(m1, typ=1)
    mce1 = float(a1.loc["Residual", "mean_sq"])
    # efecto de la temperatura (sin interacción): diferencia de medias marginales con IC 95 %
    d_temp = Tc["mB"]["150 °C"] - Tc["mB"]["170 °C"]
    ee_temp = np.sqrt(Tc["MCE"] * (2 / (len(CASO_A) * Tc["n"])))
    tcrit = float(stats.t.ppf(0.975, Tc["gl"]["E"]))
    # Tukey de las tintas con el MCE del modelo de dos factores
    qc = float(stats.studentized_range.ppf(0.95, 3, Tc["gl"]["E"]))
    hsd_c = qc * np.sqrt(Tc["MCE"] / (len(CASO_B) * Tc["n"]))
    pares = {(x, y): Tc["mA"][y] - Tc["mA"][x] for x, y in [("plastisol", "agua"), ("agua", "descarga"), ("plastisol", "descarga")]}
    # modelo aditivo (sin interacción) para predecir la celda
    mod_ad = smf.ols("secado_min ~ C(tinta) + C(temperatura)", data=s).fit()
    R["caso"] = {"s": s, "celdas": celdas, "T": Tc, "lev_tinta": lev_tinta, "lev_celdas": lev_celdas, "sh": sh_c,
                 "F1": float(a1["F"].iloc[0]), "MCE1": mce1, "d_temp": d_temp, "ee_temp": ee_temp, "tcrit": tcrit,
                 "ic_temp": (d_temp - tcrit * ee_temp, d_temp + tcrit * ee_temp), "q": qc, "hsd": hsd_c, "pares": pares,
                 "mod": modc, "mod_ad": mod_ad,
                 "var_celdas": {k: float(np.var(v, ddof=1)) for k, v in celdas.items()}}
    return R


# ---------------------------------------------------------------- CSV, figuras y cuaderno

def escribir_csv(R):
    R["ej"]["df"].to_csv(DATOS / "u09_ejemplo.csv", index=False, encoding="utf-8")


COL = ["#2B2F33", "#E2622A", "#5F8FB4"]


def grafico_interaccion(medias, A, B, titulo, ylabel, archivo, xlab):
    fig, ax = plt.subplots(figsize=(5.6, 3.4), dpi=150)
    for k, i in enumerate(A):
        ys = [medias[(i, j)] for j in B]
        ax.plot(B, ys, marker="o", color=COL[k % 3], lw=2, label=i)
        ax.annotate(i, (len(B) - 1, ys[-1]), xytext=(6, 0), textcoords="offset points", va="center", color=COL[k % 3], fontsize=9)
    ax.set_xlabel(xlab); ax.set_ylabel(ylabel); ax.set_title(titulo, fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#D6D3CE", lw=0.6)
    ax.set_xlim(-0.2, len(B) - 1 + 0.5)
    fig.tight_layout()
    fig.savefig(FIG / archivo); plt.close(fig)


def graficos(R):
    FIG.mkdir(parents=True, exist_ok=True)
    T = R["ej"]["T"]
    grafico_interaccion(T["medias"], EJ_A, EJ_B, "Ejemplo: las líneas no son paralelas (hay interacción)",
                        "resistencia media (MPa)", "u09_interaccion_ejemplo.png", "orientación de impresión")
    Tc = R["caso"]["T"]
    grafico_interaccion(Tc["medias"], CASO_A, CASO_B, "Caso: líneas casi paralelas (interacción no significativa)",
                        "secado medio (min)", "u09_interaccion_caso.png", "temperatura del túnel")
    mod = R["caso"]["mod"]
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0), dpi=150)
    ax[0].scatter(mod.fittedvalues, mod.resid, color=COL[0], s=16)
    ax[0].axhline(0, color=COL[1], lw=1)
    ax[0].set_xlabel("valor ajustado (media de la celda, min)"); ax[0].set_ylabel("residuo (min)")
    ax[0].set_title("Residuos frente a ajustados", fontsize=10)
    (osm, osr), (pend, inter, _) = stats.probplot(mod.resid, dist="norm")
    ax[1].scatter(osm, osr, color=COL[0], s=16)
    ax[1].plot(osm, pend * np.array(osm) + inter, color=COL[1], lw=1)
    ax[1].set_xlabel("cuantil normal teórico"); ax[1].set_ylabel("residuo ordenado (min)")
    ax[1].set_title("Gráfico cuantil-cuantil", fontsize=10)
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / "u09_residuos_caso.png"); plt.close(fig)


def ejecutar_cuaderno():
    """Ejecuta las celdas de código del cuaderno con exec (no hace falta Jupyter) y devuelve su espacio de nombres."""
    nb = json.loads(CUADERNO.read_text(encoding="utf-8"))
    ns = {"__name__": "__cuaderno__"}
    previo = os.getcwd()
    os.chdir(CUADERNO.parent)
    try:
        with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for celda in nb["cells"]:
                if celda["cell_type"] == "code":
                    exec("".join(celda["source"]), ns)
    finally:
        os.chdir(previo)
        plt.close("all")
    return ns


def comparar_cuaderno(R, ns):
    tej, tca = ns["tabla_ejemplo"], ns["tabla_caso"]
    T, Tc = R["ej"]["T"], R["caso"]["T"]
    ok = abs(tej.loc["C(material):C(orientacion)", "F"] - T["F"]["AB"]) < 1e-9
    ok &= abs(tca.loc["C(tinta)", "F"] - Tc["F"]["A"]) < 1e-9
    ok &= abs(tca.loc["C(tinta):C(temperatura)", "F"] - Tc["F"]["AB"]) < 1e-9
    ok &= np.allclose(ns["beta_ejemplo"], R["ej"]["beta"])
    ok &= abs(ns["levene_caso"].pvalue - R["caso"]["lev_celdas"].pvalue) < 1e-12
    print("CUADERNO:", "OK, reproduce el ejemplo y el caso" if ok else "NO coincide")
    return bool(ok)


def cadena(R):
    caso = cargar_caso()
    D = caso.generar()                    # en memoria: no reescribe los CSV
    C = caso.calcular(D)["u9"]
    s = R["caso"]["s"]
    mismo_csv = np.allclose(D["secado"].secado_min.values, s.secado_min.values) and (D["secado"].tinta.values == s.tinta.values).all()
    Tc = R["caso"]["T"]
    ok = mismo_csv
    ok &= abs(C["anova2"]["C(tinta)"]["F"] - Tc["F"]["A"]) < 1e-9
    ok &= abs(C["anova2"]["C(temperatura)"]["F"] - Tc["F"]["B"]) < 1e-9
    ok &= abs(C["anova2"]["C(tinta):C(temperatura)"]["F"] - Tc["F"]["AB"]) < 1e-9
    ok &= abs(C["anova2"]["C(tinta):C(temperatura)"]["p"] - Tc["p"]["AB"]) < 1e-9
    ok &= abs(C["levene_p"] - R["caso"]["lev_tinta"].pvalue) < 1e-12
    print("CADENA:", "OK, la pieza del caso calza con caso_estampa_sur_datos.py" if ok else "NO calza")
    return bool(ok)


# ---------------------------------------------------------------- impresión y revisión

def fila(*c):
    return "| " + " | ".join(c) + " |"


def imprimir(R):
    T = R["ej"]["T"]
    print("== Ejemplo")
    print("  medias", {k: fmt(v, 2) for k, v in T["medias"].items()}, "mA", {k: fmt(v, 1) for k, v in T["mA"].items()},
          "mB", {k: fmt(v, 1) for k, v in T["mB"].items()}, "g", fmt(T["g"], 1))
    print("  inter", {k: fmt(v, 1) for k, v in T["inter"].items()})
    print("  SC", {k: fmt(v, 2) for k, v in T["SC"].items()}, "CM", {k: fmt(v, 3) for k, v in T["CM"].items()})
    print("  F", {k: fmt(v, 2) for k, v in T["F"].items()}, "p", {k: fp(v) for k, v in T["p"].items()},
          "Fcrit", {k: fmt(v, 2) for k, v in T["Fcrit"].items()}, "eta2p", {k: fmt(v, 2) for k, v in T["eta2p"].items()})
    e = R["ej"]
    print("  XtX", e["XtX"].tolist(), "Xty", e["Xty"].tolist(), "beta", [fmt(b, 2) for b in e["beta"]])
    print("  Levene", fmt(e["levene"].statistic, 3), fp(e["levene"].pvalue), "Shapiro", fmt(e["shapiro"].statistic, 3), fp(e["shapiro"].pvalue))
    print("  efectos simples ee", fmt(e["ee_simple"], 3), {k: fmt(v, 2) for k, v in e["simples"].items()}, "tcrit", fmt(e["t_crit"], 3))
    e = R["e1"]
    print("== 9.1 SCE", fmt(e["SC_E"], 1), "gl", e["gl"], "MCE", fmt(e["MCE"], 3), "CM", {k: fmt(v, 2) for k, v in e["CM"].items()},
          "F", {k: fmt(v, 2) for k, v in e["F"].items()}, "p", {k: fp(v) for k, v in e["p"].items()}, "Fcrit", {k: fmt(v, 2) for k, v in e["Fcrit"].items()})
    e = R["e2"]
    print("== 9.2 mA", {k: fmt(v, 2) for k, v in e["mA"].items()}, "mB", {k: fmt(v, 2) for k, v in e["mB"].items()}, "g", fmt(e["g"], 2))
    print("  inter", {k: fmt(v, 2) for k, v in e["inter"].items()}, "dif", {k: fmt(v, 1) for k, v in e["dif"].items()})
    e = R["e3"]
    print("== 9.3 beta", [fmt(b, 1) for b in e["beta"]], "XtX", e["XtX"].tolist(), "F", {k: fmt(v, 2) for k, v in e["T"]["F"].items()},
          "p", {k: fp(v) for k, v in e["T"]["p"].items()}, "MCE", fmt(e["T"]["MCE"], 2))
    e = R["e4"]
    print("== 9.4", e["gl"], {k: fmt(v, 2) for k, v in e["Fcrit"].items()}, "n=1:", e["glE_n1_inter"], e["glE_n1_aditivo"], {k: fmt(v, 2) for k, v in e["Fcrit_n1"].items()})
    T5 = R["e5"]["T"]
    print("== 9.5 medias", {k: fmt(v, 2) for k, v in T5["medias"].items()}, "mA", {k: fmt(v, 2) for k, v in T5["mA"].items()},
          "mB", {k: fmt(v, 2) for k, v in T5["mB"].items()}, "g", fmt(T5["g"], 2))
    print("  SC", {k: fmt(v, 2) for k, v in T5["SC"].items()}, "CM", {k: fmt(v, 2) for k, v in T5["CM"].items()}, "F", {k: fmt(v, 2) for k, v in T5["F"].items()},
          "p", {k: fp(v) for k, v in T5["p"].items()}, "eta2p", {k: fmt(v, 2) for k, v in T5["eta2p"].items()}, "q", fmt(R["e5"]["q"], 3), "HSD", fmt(R["e5"]["hsd"], 2))
    e = R["e6"]
    for nom, T6, sh, lev in (("con error", e["T"], e["sh"], e["lev"]), ("corregido", e["Tc"], e["shc"], e["levc"])):
        print(f"== 9.6 {nom}: F", {k: fmt(v, 2) for k, v in T6["F"].items()}, "p", {k: fp(v) for k, v in T6["p"].items()},
              "MCE", fmt(T6["MCE"], 3), "Shapiro", fmt(sh.statistic, 3), fp(sh.pvalue), "Levene", fmt(lev.statistic, 2), fp(lev.pvalue),
              "medias", {k: fmt(v, 2) for k, v in T6["medias"].items()})
    print("  rmax", fmt(e["rmax"], 2), "rstd max", fmt(e["rstd_max"], 2), "corregido rstd max", fmt(e["rstd_max_c"], 2))
    e = R["e7"]
    print("== 9.7 bruto F", {k: fmt(v, 2) for k, v in e["T"]["F"].items()}, "p", {k: fp(v) for k, v in e["T"]["p"].items()},
          "medias", {k: fmt(v, 2) for k, v in e["T"]["medias"].items()}, "var", {k: fmt(v, 1) for k, v in e["var"].items()}, "razón", fmt(e["razon"], 1))
    print("  log F", {k: fmt(v, 2) for k, v in e["Tl"]["F"].items()}, "p", {k: fp(v) for k, v in e["Tl"]["p"].items()}, "razón log", fmt(e["razon_l"], 1),
          "Levene", fp(e["lev"].pvalue), "Levene log", fp(e["levl"].pvalue), "efecto servidor", fmt(e["efecto_serv"], 3),
          "medias log", {k: fmt(v, 3) for k, v in e["Tl"]["medias"].items()})
    e = R["e8"]
    print("== 9.8 ee", fmt(e["ee"], 3), "t", {k: fmt(v, 2) for k, v in e["t"].items()}, "p", {k: fp(v) for k, v in e["p"].items()},
          "tc", fmt(e["tc"], 3), "tcB", fmt(e["tcb"], 3), "inter", fmt(e["inter"], 1), "F", fmt(e["F"], 2), fp(e["pF"]),
          "IC", {k: (fmt(a, 2), fmt(b, 2)) for k, (a, b) in e["ic"].items()})
    e = R["e9"]
    print("== 9.9 medias", {k: fmt(v, 2) for k, v in e["medias"].items()}, "bruto", {k: fmt(v, 2) for k, v in e["bruto"].items()},
          "celdas", {k: fmt(v, 2) for k, v in e["celdas"].items()})
    for nom in ("t1a", "t1b", "t2"):
        t = e[nom]
        print("  ", nom, {i: (fmt(t.loc[i, "sum_sq"], 2), fmt(t.loc[i, "F"], 2) if i != "Residual" else "", fp(t.loc[i, "PR(>F)"]) if i != "Residual" else "") for i in t.index})
    e = R["e10"]
    print("== 9.10 medias", [fmt(x, 3) for x in e["m"]], "de", [fmt(x, 3) for x in e["s"]], "var", [fmt(x, 3) for x in e["v"]])
    print("  clásico F", fmt(e["clas"].statistic, 2), fp(e["clas"].pvalue), "Welch F", fmt(e["Fw"], 2), "gl2", fmt(e["gl2w"], 2), fp(e["pw"]),
          "KW H", fmt(e["kw"].statistic, 2), fp(e["kw"].pvalue), "Levene", fmt(e["lev"].statistic, 2), fp(e["lev"].pvalue))
    c = R["caso"]; Tc = c["T"]
    print("== Caso")
    for k, v in c["celdas"].items():
        print("  ", k, v, "media", fmt(Tc["medias"][k], 2), "var", fmt(c["var_celdas"][k], 3))
    print("  mA", {k: fmt(v, 2) for k, v in Tc["mA"].items()}, "mB", {k: fmt(v, 2) for k, v in Tc["mB"].items()}, "g", fmt(Tc["g"], 2))
    print("  SC", {k: fmt(v, 2) for k, v in Tc["SC"].items()}, "CM", {k: fmt(v, 2) for k, v in Tc["CM"].items()}, "MCE", fmt(Tc["MCE"], 3))
    print("  F", {k: fmt(v, 2) for k, v in Tc["F"].items()}, "p", {k: fp(v) for k, v in Tc["p"].items()}, "Fcrit", {k: fmt(v, 2) for k, v in Tc["Fcrit"].items()},
          "eta2p", {k: fmt(v, 2) for k, v in Tc["eta2p"].items()})
    print("  inter", {k: fmt(v, 2) for k, v in Tc["inter"].items()})
    print("  Levene tinta", fmt(c["lev_tinta"].statistic, 3), fp(c["lev_tinta"].pvalue), "Levene celdas", fmt(c["lev_celdas"].statistic, 3), fp(c["lev_celdas"].pvalue),
          "Shapiro", fmt(c["sh"].statistic, 3), fp(c["sh"].pvalue))
    print("  U7: F", fmt(c["F1"], 2), "MCE1", fmt(c["MCE1"], 3), "| temp dif", fmt(c["d_temp"], 2), "ee", fmt(c["ee_temp"], 3), "t", fmt(c["tcrit"], 3),
          "IC", fmt(c["ic_temp"][0], 2), fmt(c["ic_temp"][1], 2), "| q", fmt(c["q"], 3), "HSD", fmt(c["hsd"], 2), "pares", {k: fmt(v, 2) for k, v in c["pares"].items()})
    print("  aditivo params", {k: fmt(v, 2) for k, v in c["mod_ad"].params.items()})


def esperados(R):
    e = []
    T = R["ej"]["T"]
    # ejemplo: datos, medias, tabla
    for (i, j), v in EJ.items():
        e.append(fila(i, j, *map(str, v), fmt(T["medias"][(i, j)], 0)))
    e += [fmt(T["SC"][k], 0) for k in ("A", "B", "AB", "E", "T")]
    e += [fmt(T["MCE"], 2), fmt(T["F"]["A"], 2), fmt(T["F"]["B"], 2), fmt(T["F"]["AB"], 2), fmt(T["Fcrit"]["AB"], 2)]
    e += [fmt(T["eta2p"][k], 2) for k in ("A", "B", "AB")]
    e += [fmt(R["ej"]["levene"].pvalue, 2), fmt(R["ej"]["shapiro"].pvalue, 2)]
    e += [fmt(R["ej"]["ee_simple"], 3), fmt(R["ej"]["simples"]["PLA"], 2), fmt(R["ej"]["simples"]["PETG"], 2), fmt(R["ej"]["t_crit"], 3)]
    e += [f"\\begin{{pmatrix}} {fmt(b, 0)}" for b in R["ej"]["beta"][:1]]
    e += [fmt(b, 0) for b in R["ej"]["beta"]]
    # 9.1
    x = R["e1"]
    e += [fmt(x["SC_E"], 1), fmt(x["MCE"], 3)] + [fmt(v, 2) for v in x["F"].values()] + [fmt(v, 2) for v in x["Fcrit"].values()]
    e += [fp(x["p"]["A"]), fp(x["p"]["B"]), fp(x["p"]["AB"])]
    # 9.2
    x = R["e2"]
    e += [fmt(v, 2) for v in x["inter"].values()] + [fmt(v, 2) for v in x["mA"].values()] + [fmt(v, 2) for v in x["mB"].values()]
    # 9.3
    x = R["e3"]
    e += [fila(i, j, *map(str, v)) for (i, j), v in E3.items()]
    e += [fmt(b, 0) for b in x["beta"]] + [fmt(x["T"]["F"]["AB"], 2), fp(x["T"]["p"]["AB"])]
    # 9.4
    x = R["e4"]
    e += [fmt(v, 2) for v in x["Fcrit"].values()] + [fmt(v, 2) for v in x["Fcrit_n1"].values()]
    # 9.5
    T5 = R["e5"]["T"]
    e += [fila(i, j, *map(str, v)) for (i, j), v in E5.items()]
    e += [fmt(T5["SC"][k], 2) for k in ("A", "B", "AB", "E")] + [fmt(T5["F"][k], 2) for k in ("A", "B", "AB")]
    e += [fp(T5["p"]["AB"]), fmt(T5["MCE"], 2), fmt(R["e5"]["hsd"], 2)] + [fmt(T5["eta2p"][k], 2) for k in ("A", "B")]
    # 9.6
    x = R["e6"]
    e += [fila(i, j, *(fmt(y, 1) for y in v)) for (i, j), v in E6.items()]
    e += [fmt(x["sh"].pvalue, 3) if x["sh"].pvalue >= 0.001 else fp(x["sh"].pvalue), fmt(x["rstd_max"], 1), fmt(x["T"]["F"]["B"], 2), fmt(x["Tc"]["F"]["B"], 2),
          fmt(x["Tc"]["F"]["A"], 1), fmt(x["shc"].pvalue, 2), fmt(x["levc"].pvalue, 2), fmt(x["T"]["MCE"], 2), fmt(x["Tc"]["MCE"], 3)]
    # 9.7
    x = R["e7"]
    e += [fila(i, j, *map(str, v)) for (i, j), v in E7.items()]
    e += [fmt(x["T"]["F"]["AB"], 2), fp(x["T"]["p"]["AB"]), fmt(x["Tl"]["F"]["AB"], 2), fp(x["Tl"]["p"]["AB"]), fmt(x["razon"], 1), fmt(x["razon_l"], 1),
          fmt(x["efecto_serv"], 2)]
    # 9.8
    x = R["e8"]
    e += [fmt(x["ee"], 3), fmt(x["t"]["secano"], 2), fmt(x["t"]["riego"], 2), fmt(x["tc"], 3), fmt(x["tcb"], 3), fmt(x["F"], 2)]
    e += [fmt(v, 2) for ab in x["ic"].values() for v in ab]
    # 9.9
    x = R["e9"]
    e += [fmt(x["t1a"].loc["C(envio)", "sum_sq"], 2), fmt(x["t1b"].loc["C(envio)", "sum_sq"], 2), fmt(x["t2"].loc["C(envio)", "sum_sq"], 2),
          fmt(x["t1a"].loc["C(region)", "sum_sq"], 2), fmt(x["t1b"].loc["C(region)", "sum_sq"], 2), fmt(x["t2"].loc["C(region)", "sum_sq"], 2)]
    e += [fmt(v, 2) for v in x["bruto"].values()] + [fmt(v, 2) for v in x["celdas"].values()]
    # 9.10
    x = R["e10"]
    e += [fmt(x["clas"].statistic, 2), fmt(x["Fw"], 2), fmt(x["gl2w"], 2), fmt(x["kw"].statistic, 2), fp(x["pw"]), fp(x["clas"].pvalue), fp(x["kw"].pvalue)]
    e += [fmt(v, 2) for v in x["s"]]
    # caso
    c = R["caso"]; Tc = c["T"]
    for (t, temp), v in c["celdas"].items():
        e.append(fila(t, temp, *(fmt(y, 1) for y in v), fmt(Tc["medias"][(t, temp)], 2)))
    e += [fmt(Tc["SC"][k], 2) for k in ("A", "B", "AB", "E", "T")] + [fmt(Tc["F"][k], 2) for k in ("A", "B", "AB")]
    e += [fmt(Tc["MCE"], 3), fp(Tc["p"]["AB"]), fmt(c["lev_tinta"].pvalue, 2), fmt(c["lev_celdas"].pvalue, 2), fmt(c["sh"].pvalue, 2)]
    e += [fmt(c["F1"], 2), fmt(c["MCE1"], 3), fmt(c["d_temp"], 2), fmt(c["ic_temp"][0], 2), fmt(c["ic_temp"][1], 2), fmt(c["hsd"], 2)]
    e += [fmt(v, 2) for v in Tc["mA"].values()] + [fmt(v, 2) for v in Tc["mB"].values()] + [fmt(Tc["eta2p"][k], 2) for k in ("A", "B", "AB")]
    e += [fmt(c["tcrit"], 3), fmt(c["ee_temp"], 3), fmt(c["q"], 3)] + [fmt(v, 2) for v in c["pares"].values()]
    # agregados de las pautas
    T5 = R["e5"]["T"]
    e += [fmt(v, 2) for v in T5["medias"].values()] + [fmt(v, 2) for v in T5["mA"].values()] + [fmt(v, 2) for v in T5["mB"].values()]
    e += [fmt(R["e5"]["q"], 3), fmt(T5["mB"]["22 °C"] - T5["mB"]["26 °C"], 2), fmt(T5["mB"]["26 °C"] - T5["mB"]["30 °C"], 2), fmt(T5["SC"]["T"], 2),
          fmt(T5["CM"]["B"], 2)]
    x = R["e6"]
    e += [fmt(x["T"]["medias"][("M1", "noche")], 2)] + [fmt(v, 2) for v in x["Tc"]["mA"].values()]
    x = R["e7"]
    e += [fmt(v, 2) for v in x["T"]["medias"].values()] + [fmt(v, 1) for v in x["var"].values()] + [fp(x["lev"].pvalue), fp(x["levl"].pvalue)]
    x = R["e8"]
    e += [fmt(x["inter"], 1), fp(x["pF"]), fp(x["p"]["secano"])]
    x = R["e9"]
    e += [fmt(x["t2"].loc["C(envio):C(region)", "sum_sq"], 2), fp(x["t2"].loc["C(envio):C(region)", "PR(>F)"]), fmt(x["t2"].loc["Residual", "sum_sq"], 2)]
    x = R["e10"]
    e += [fmt(v, 2) for v in x["m"]] + [fp(x["lev"].pvalue)]
    # afirmaciones en palabras de las pautas y del caso
    assert R["e6"]["T"]["MCE"] / R["e6"]["Tc"]["MCE"] > 260          # «infló el error más de 260 veces»
    assert R["e10"]["v"][1] / R["e10"]["v"][0] > 100                  # «más de cien veces la de A»
    e += [fmt(np.sqrt(c["T"]["MCE"] / 10), 3)]
    e += [fmt(Tc["CM"]["A"], 2), fmt(Tc["CM"]["AB"], 2), fmt(Tc["Fcrit"]["AB"], 2)]
    return e


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    escribir_csv(R)
    graficos(R)
    ok = cadena(R)
    if CUADERNO.exists():
        ok &= comparar_cuaderno(R, ejecutar_cuaderno())
    else:
        print("CUADERNO: no existe todavía"); ok = False
    if not ok:
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8").replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
