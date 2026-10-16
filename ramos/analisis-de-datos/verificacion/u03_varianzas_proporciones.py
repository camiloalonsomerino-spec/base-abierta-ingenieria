"""Unidad 3 · Comparar varianzas y proporciones.

Recalcula todas las cifras de la unidad desde los datos, a mano (con la fórmula) y con scipy o
statsmodels, y exige que los dos caminos coincidan. Deja los datos del ejemplo en
datos/u03_ejemplo.csv, dibuja las figuras en unidades/figuras/, ejecuta el cuaderno
notebooks/u03_varianzas_proporciones.ipynb y compara la pieza del caso con el script del caso.

    python u03_varianzas_proporciones.py            # imprime los resultados
    python u03_varianzas_proporciones.py --revisar  # además busca cada cifra en el .md
"""
from pathlib import Path
import importlib.util, itertools, json, os, subprocess, sys

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
DATOS, FIG, NB = RAMO / "datos", RAMO / "unidades" / "figuras", RAMO / "notebooks"
MD = RAMO / "unidades" / "03-varianzas-y-proporciones.md"
CUADERNO = NB / "u03_varianzas_proporciones.ipynb"


# ---------------------------------------------------------------- formato a la chilena

def fmt(x, dec=1):
    s = f"{x:,.{dec}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return "0" + s[2:] if s.startswith("-0") and set(s[1:]) <= set("0,") else s


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def pv(p, dec=3):
    """Valor p como se escribe en el texto: «p < 0,001» si es chico."""
    return "p < 0,001" if p < 0.001 else f"p = {fmt(p, dec)}"


def fila(*celdas):
    return "| " + " | ".join(celdas) + " |"


# ---------------------------------------------------------------- herramientas a mano

def una_varianza(n, s2, sigma2_0):
    """χ² = (n − 1) s² / σ0², con n − 1 gl. Devuelve el estadístico y las tres colas."""
    c = (n - 1) * s2 / sigma2_0
    izq, der = stats.chi2.cdf(c, n - 1), stats.chi2.sf(c, n - 1)
    return {"chi2": c, "gl": n - 1, "p_der": der, "p_izq": izq, "p_dos": 2 * min(izq, der)}


def ic_varianza(n, s2, conf=0.95):
    a = 1 - conf
    return ((n - 1) * s2 / stats.chi2.ppf(1 - a / 2, n - 1), (n - 1) * s2 / stats.chi2.ppf(a / 2, n - 1))


def dos_varianzas(s2_num, n_num, s2_den, n_den):
    F = s2_num / s2_den
    v1, v2 = n_num - 1, n_den - 1
    izq, der = stats.f.cdf(F, v1, v2), stats.f.sf(F, v1, v2)
    return {"F": F, "v1": v1, "v2": v2, "p_der": der, "p_dos": 2 * min(izq, der)}


def levene_a_mano(*grupos):
    """Levene con la mediana (Brown-Forsythe): ANOVA de un factor sobre |x − mediana del grupo|."""
    z = [np.abs(np.asarray(g, float) - np.median(g)) for g in grupos]
    N, k = sum(len(g) for g in z), len(z)
    zbar = np.concatenate(z).mean()
    medias = [g.mean() for g in z]
    entre = sum(len(g) * (m - zbar) ** 2 for g, m in zip(z, medias))
    dentro = sum(((g - m) ** 2).sum() for g, m in zip(z, medias))
    W = (N - k) / (k - 1) * entre / dentro
    return {"z": z, "medias_z": medias, "zbar": zbar, "entre": entre, "dentro": dentro,
            "W": W, "gl": (k - 1, N - k), "p": stats.f.sf(W, k - 1, N - k)}


def dos_proporciones(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2
    pb = (x1 + x2) / (n1 + n2)
    ee0 = np.sqrt(pb * (1 - pb) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / ee0
    ee = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    zc = stats.norm.ppf(0.975)
    return {"p1": p1, "p2": p2, "pb": pb, "ee0": ee0, "z": z, "p_dos": 2 * stats.norm.sf(abs(z)),
            "p_menor": stats.norm.cdf(z), "p_mayor": stats.norm.sf(z),
            "ee": ee, "ic": (p1 - p2 - zc * ee, p1 - p2 + zc * ee)}


def homogeneidad(x, n):
    """χ² de homogeneidad de k proporciones: tabla k × 2 con esperados n_i · p̄."""
    x, n = np.asarray(x, float), np.asarray(n, float)
    pb = x.sum() / n.sum()
    obs = np.c_[x, n - x]
    esp = np.c_[n * pb, n * (1 - pb)]
    contrib = (obs - esp) ** 2 / esp
    chi2 = contrib.sum()
    gl = len(x) - 1
    return {"pb": pb, "tasas": x / n, "esp": esp, "contrib": contrib, "chi2": chi2, "gl": gl,
            "p": stats.chi2.sf(chi2, gl)}


def potencia_F(v1, v2, razon, alfa=0.05):
    """Potencia de la prueba F bilateral si la razón verdadera de varianzas es `razon`."""
    fu, fl = stats.f.ppf(1 - alfa / 2, v1, v2), stats.f.ppf(alfa / 2, v1, v2)
    return stats.f.sf(fu / razon, v1, v2) + stats.f.cdf(fl / razon, v1, v2)


def n_dos_proporciones(p1, p2, alfa=0.05, potencia=0.80):
    za, zb = stats.norm.ppf(1 - alfa / 2), stats.norm.ppf(potencia)
    pb = (p1 + p2) / 2
    return (za * np.sqrt(2 * pb * (1 - pb)) + zb * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p1 - p2) ** 2


def potencia_dos_proporciones(p1, p2, n, alfa=0.05):
    za = stats.norm.ppf(1 - alfa / 2)
    pb = (p1 + p2) / 2
    return stats.norm.cdf((abs(p1 - p2) * np.sqrt(n) - za * np.sqrt(2 * pb * (1 - pb))) / np.sqrt(p1 * (1 - p1) + p2 * (1 - p2)))


# ---------------------------------------------------------------- datos (originales de esta base)
# Pasados por herramientas/colisiones.py contra el material del curso el 15-10-2026: sin alertas.

# Ejemplo · mermeladas: peso neto (g) de frascos de 250 g en dos dosificadoras y frascos con sello fallado
EJ_A = [251.2, 249.8, 250.6, 250.1, 249.5, 250.9, 250.3, 249.7]                  # dosificadora nueva
EJ_B = [252.4, 248.1, 250.9, 247.6, 251.8, 249.2, 253.0, 248.8, 250.5, 251.3]   # dosificadora antigua
EJ_SIGMA0 = 1.5                      # la norma interna pide σ ≤ 1,5 g
EJ_SELLO = {"A": (9, 600), "B": (21, 640)}

E1 = {"n": 20, "s": 5.1, "sigma0": 4.0}                     # marraquetas: σ ≤ 4 g
E2 = {"n1": 13, "s1": 0.84, "n2": 16, "s2": 0.52}           # pernos de dos proveedores (mm)
E3 = {"noche": (34, 980), "dia": (19, 1050)}                # latas mal selladas por turno
E4 = {"n1": 8, "n2": 11}                                    # valores críticos de S1²/S2²
E5_X = [10.02, 9.98, 10.01, 10.00, 9.99, 10.03, 9.97, 10.36]   # balanza X (kg)
E5_Y = [10.04, 9.95, 10.01, 9.97, 10.06, 9.94, 10.03, 9.99]    # balanza Y (kg)
E6 = {"A": (18, 240), "B": (34, 260), "C": (12, 230), "D": (25, 250)}   # despachos atrasados
E7 = [1200.3, 1199.6, 1200.9, 1199.2, 1200.5, 1201.4, 1199.8, 1200.4, 1199.1, 1200.7]  # largo (mm)
E7_SIGMA0 = 0.5
E8 = {"v1": (62, 1240), "v2": (88, 1310)}                   # formulario web, versión 1 y 2
E9 = {"v1": 17, "v2": 21, "razones": [1.5, 2, 3]}           # potencia con los tamaños del caso
E10 = {"p1": 0.045, "p2": 0.065, "n_caso": 830}

# Simulación del nivel real de las pruebas de varianzas cuando los datos no son normales
SIM = {"semilla": 3003, "reps": 20_000, "n": 15}


# ---------------------------------------------------------------- simulación

def simular():
    rng = np.random.default_rng(SIM["semilla"])
    n, reps = SIM["n"], SIM["reps"]
    gen = {"normal": lambda: rng.normal(0, 1, (reps, 2, n)),
           "uniforme": lambda: rng.uniform(0, 1, (reps, 2, n)),
           "t con 5 gl": lambda: rng.standard_t(5, (reps, 2, n)),
           "exponencial": lambda: rng.exponential(1, (reps, 2, n))}
    fu, fl = stats.f.ppf(0.975, n - 1, n - 1), stats.f.ppf(0.025, n - 1, n - 1)
    wc = stats.f.ppf(0.95, 1, 2 * n - 2)
    out = {}
    for nombre, g in gen.items():
        x = g()
        F = x[:, 0].var(axis=1, ddof=1) / x[:, 1].var(axis=1, ddof=1)
        z = np.abs(x - np.median(x, axis=2, keepdims=True))
        mz = z.mean(axis=2)
        zbar = z.reshape(reps, -1).mean(axis=1)
        entre = n * ((mz - zbar[:, None]) ** 2).sum(axis=1)
        dentro = ((z - mz[:, :, None]) ** 2).sum(axis=(1, 2))
        W = (2 * n - 2) * entre / dentro
        for i in range(3):   # el Levene vectorizado es el de scipy
            assert abs(W[i] - stats.levene(x[i, 0], x[i, 1]).statistic) < 1e-9
        out[nombre] = {"F": float(np.mean((F > fu) | (F < fl))), "Levene": float(np.mean(W > wc))}
    return out


# ---------------------------------------------------------------- caso

def cargar_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_datos.py")
    caso = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caso)
    nombres = ["registro", "defectos", "reclamos_canal", "llegadas", "ventas", "secado", "lotes", "reclamos_dia"]
    D = {k: pd.read_csv(DATOS / f"{k}.csv") for k in nombres}
    return caso, D


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    a, b = np.array(EJ_A), np.array(EJ_B)
    R["ej"] = {"media_a": a.mean(), "media_b": b.mean(), "s2_a": a.var(ddof=1), "s2_b": b.var(ddof=1),
               "s_a": a.std(ddof=1), "s_b": b.std(ddof=1),
               "ss_a": ((a - a.mean()) ** 2).sum(), "ss_b": ((b - b.mean()) ** 2).sum()}
    e = R["ej"]
    R["ej_chi"] = una_varianza(len(b), e["s2_b"], EJ_SIGMA0 ** 2)
    R["ej_chi_crit"] = stats.chi2.ppf(0.95, len(b) - 1)
    R["ej_F"] = dos_varianzas(e["s2_b"], len(b), e["s2_a"], len(a))
    R["ej_F_crit"] = stats.f.ppf(0.95, len(b) - 1, len(a) - 1)
    R["ej_lev"] = levene_a_mano(a, b)
    lev = stats.levene(a, b)
    assert abs(lev.statistic - R["ej_lev"]["W"]) < 1e-9 and abs(lev.pvalue - R["ej_lev"]["p"]) < 1e-9
    R["ej_sello"] = dos_proporciones(*EJ_SELLO["A"], *EJ_SELLO["B"])
    z_sm, p_sm = proportions_ztest([EJ_SELLO["A"][0], EJ_SELLO["B"][0]], [EJ_SELLO["A"][1], EJ_SELLO["B"][1]])
    assert abs(z_sm - R["ej_sello"]["z"]) < 1e-9 and abs(p_sm - R["ej_sello"]["p_dos"]) < 1e-9
    f_sc = stats.f.sf(R["ej_F"]["F"], len(b) - 1, len(a) - 1)
    assert abs(f_sc - R["ej_F"]["p_der"]) < 1e-12

    # 3.1
    R["e1"] = una_varianza(E1["n"], E1["s"] ** 2, E1["sigma0"] ** 2)
    R["e1_crit"] = stats.chi2.ppf(0.95, E1["n"] - 1)
    # 3.2
    R["e2"] = dos_varianzas(E2["s1"] ** 2, E2["n1"], E2["s2"] ** 2, E2["n2"])
    R["e2_crit"] = stats.f.ppf(0.975, E2["n1"] - 1, E2["n2"] - 1)
    # 3.3
    R["e3"] = dos_proporciones(*E3["noche"], *E3["dia"])
    # 3.4
    v1, v2 = E4["n1"] - 1, E4["n2"] - 1
    R["e4"] = {"sup": stats.f.ppf(0.95, v1, v2), "inv": stats.f.ppf(0.95, v2, v1), "inf": stats.f.ppf(0.05, v1, v2)}
    assert abs(R["e4"]["inf"] - 1 / R["e4"]["inv"]) < 1e-12
    # 3.5
    X, Y = np.array(E5_X), np.array(E5_Y)
    R["e5"] = {"s2x": X.var(ddof=1), "s2y": Y.var(ddof=1), "medx": np.median(X), "medy": np.median(Y)}
    R["e5_F"] = dos_varianzas(R["e5"]["s2x"], len(X), R["e5"]["s2y"], len(Y))
    R["e5_crit"] = stats.f.ppf(0.975, len(X) - 1, len(Y) - 1)
    R["e5_lev"] = levene_a_mano(X, Y)
    assert abs(stats.levene(X, Y).statistic - R["e5_lev"]["W"]) < 1e-9
    R["e5_sin"] = dos_varianzas(X[:-1].var(ddof=1), len(X) - 1, R["e5"]["s2y"], len(Y))
    R["e5_shapiro"] = stats.shapiro(X).pvalue
    # 3.6
    x6 = [v[0] for v in E6.values()]; n6 = [v[1] for v in E6.values()]
    R["e6"] = homogeneidad(x6, n6)
    sc = stats.chi2_contingency(np.c_[x6, np.array(n6) - np.array(x6)])
    assert abs(sc.statistic - R["e6"]["chi2"]) < 1e-9
    # 3.7
    L = np.array(E7)
    R["e7"] = {"media": L.mean(), "s2": L.var(ddof=1), "s": L.std(ddof=1)}
    R["e7_chi"] = una_varianza(len(L), R["e7"]["s2"], E7_SIGMA0 ** 2)
    R["e7_crit"] = stats.chi2.ppf(0.95, len(L) - 1)
    lo, hi = ic_varianza(len(L), R["e7"]["s2"])
    R["e7_ic"] = (np.sqrt(lo), np.sqrt(hi))
    R["e7_chi_q"] = (stats.chi2.ppf(0.025, len(L) - 1), stats.chi2.ppf(0.975, len(L) - 1))
    # 3.8
    R["e8"] = dos_proporciones(*E8["v1"], *E8["v2"])
    t8 = np.array([[E8["v1"][0], E8["v1"][1] - E8["v1"][0]], [E8["v2"][0], E8["v2"][1] - E8["v2"][0]]])
    R["e8_chi"] = stats.chi2_contingency(t8, correction=False).statistic
    assert abs(R["e8_chi"] - R["e8"]["z"] ** 2) < 1e-9
    zc = stats.norm.ppf(0.95)
    d = R["e8"]["p2"] - R["e8"]["p1"]
    R["e8_ic90"] = (d - zc * R["e8"]["ee"], d + zc * R["e8"]["ee"])
    # 3.9
    R["e9"] = {r: potencia_F(E9["v1"], E9["v2"], r) for r in E9["razones"]}
    R["e9_crit"] = (stats.f.ppf(0.025, E9["v1"], E9["v2"]), stats.f.ppf(0.975, E9["v1"], E9["v2"]))
    n = 2
    while potencia_F(n - 1, n - 1, 2) < 0.80:
        n += 1
    R["e9_n"] = n
    R["e9_n_pot"] = potencia_F(n - 1, n - 1, 2)
    # 3.10
    R["e10_n"] = n_dos_proporciones(E10["p1"], E10["p2"])
    R["e10_pot"] = potencia_dos_proporciones(E10["p1"], E10["p2"], E10["n_caso"])
    # comprobación por el otro camino: con n = ceil(e10_n) la potencia es al menos 0,80
    assert potencia_dos_proporciones(E10["p1"], E10["p2"], np.ceil(R["e10_n"])) >= 0.80
    # (c) con la mitad de la diferencia hacen falta algo menos de cuatro veces más prendas
    razon = n_dos_proporciones(E10["p1"], E10["p1"] + (E10["p2"] - E10["p1"]) / 2) / R["e10_n"]
    assert 3 < razon < 4, razon

    # simulación
    R["sim"] = simular()

    # caso · calculado a mano desde los CSV
    caso, D = cargar_caso()
    r = D["registro"]
    a6 = r[r.maquina == "pulpo 6"].desplazamiento_mm.values
    a4 = r[r.maquina == "pulpo 4"].desplazamiento_mm.values
    c = {"n6": len(a6), "n4": len(a4), "s2_6": a6.var(ddof=1), "s2_4": a4.var(ddof=1),
         "s_6": a6.std(ddof=1), "s_4": a4.std(ddof=1)}
    c["F"] = dos_varianzas(c["s2_6"], len(a6), c["s2_4"], len(a4))
    c["F_crit"] = (stats.f.ppf(0.025, len(a6) - 1, len(a4) - 1), stats.f.ppf(0.975, len(a6) - 1, len(a4) - 1))
    c["lev"] = levene_a_mano(a6, a4)
    c["lev_media"] = stats.levene(a6, a4, center="mean").pvalue
    c["shapiro"] = (stats.shapiro(a6).pvalue, stats.shapiro(a4).pvalue)
    c["potencia"] = potencia_F(len(a6) - 1, len(a4) - 1, c["F"]["F"])
    d = D["defectos"]
    c["prov"] = list(d.proveedor)
    c["x"], c["n"] = list(d.defectuosas), list(d.revisadas)
    c["homog"] = homogeneidad(c["x"], c["n"])
    c["pares"] = {}
    for i, j in itertools.combinations(range(3), 2):
        q = dos_proporciones(c["x"][i], c["n"][i], c["x"][j], c["n"][j])
        q["bonf"] = min(1.0, 3 * q["p_dos"])
        c["pares"][(i, j)] = q
    R["caso"] = c
    R["_caso_mod"], R["_D"] = caso, D
    return R


# ---------------------------------------------------------------- datos del ejemplo, figuras y cuaderno

def escribir_datos():
    filas = [{"dosificadora": "A", "peso_g": x} for x in EJ_A] + [{"dosificadora": "B", "peso_g": x} for x in EJ_B]
    pd.DataFrame(filas).to_csv(DATOS / "u03_ejemplo.csv", index=False, encoding="utf-8")
    pd.DataFrame([{"dosificadora": k, "sello_fallado": v[0], "frascos": v[1]} for k, v in EJ_SELLO.items()]) \
        .to_csv(DATOS / "u03_ejemplo_sellos.csv", index=False, encoding="utf-8")


AZUL, NARANJA, TINTA, SUAVE, LINEA = "#2a78d6", "#eb6834", "#2B2F33", "#52514e", "#D6D3CE"


def estilo(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(LINEA)
    ax.tick_params(colors=SUAVE, labelsize=8)
    ax.yaxis.label.set_color(SUAVE); ax.xaxis.label.set_color(SUAVE)
    ax.title.set_color(TINTA)


def figuras(R):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "Segoe UI", "font.size": 9, "axes.titlesize": 10})
    FIG.mkdir(parents=True, exist_ok=True)

    # 1 · regiones de rechazo del ejemplo
    fig, axs = plt.subplots(1, 2, figsize=(8, 2.8))
    gl = len(EJ_B) - 1
    x = np.linspace(0, 30, 600); y = stats.chi2.pdf(x, gl)
    ax = axs[0]; ax.plot(x, y, color=TINTA, lw=1.5)
    cr = R["ej_chi_crit"]; m = x >= cr
    ax.fill_between(x[m], y[m], color=NARANJA, alpha=.55, lw=0)
    ax.axvline(R["ej_chi"]["chi2"], color=AZUL, lw=2)
    ax.text(R["ej_chi"]["chi2"] - .4, y.max() * .92, f"observado {fmt(R['ej_chi']['chi2'], 2)}", color=TINTA, fontsize=8, ha="right")
    ax.text(cr + .4, y.max() * .35, f"rechazo\n(> {fmt(cr, 2)})", color=TINTA, fontsize=8)
    ax.set_title(f"Una varianza · χ² con {gl} gl"); ax.set_yticks([]); estilo(ax)
    v1, v2 = len(EJ_B) - 1, len(EJ_A) - 1
    x = np.linspace(0.01, 11, 600); y = stats.f.pdf(x, v1, v2)
    ax = axs[1]; ax.plot(x, y, color=TINTA, lw=1.5)
    cr = R["ej_F_crit"]; m = x >= cr
    ax.fill_between(x[m], y[m], color=NARANJA, alpha=.55, lw=0)
    ax.axvline(R["ej_F"]["F"], color=AZUL, lw=2)
    ax.text(R["ej_F"]["F"] - .2, y.max() * .5, f"observado {fmt(R['ej_F']['F'], 2)}", color=TINTA, fontsize=8, ha="right")
    ax.text(cr + .2, y.max() * .2, f"rechazo (> {fmt(cr, 2)})", color=TINTA, fontsize=8)
    ax.set_title(f"Dos varianzas · F con ({v1}, {v2}) gl"); ax.set_yticks([]); estilo(ax)
    fig.tight_layout(); fig.savefig(FIG / "u03_regiones.png", dpi=170); plt.close(fig)

    # 2 · nivel real de F y de Levene
    fig, ax = plt.subplots(figsize=(7, 2.9))
    nombres = list(R["sim"]); xs = np.arange(len(nombres)); w = .36
    fF = [R["sim"][k]["F"] for k in nombres]; fL = [R["sim"][k]["Levene"] for k in nombres]
    b1 = ax.bar(xs - w / 2 - .01, fF, w, color=NARANJA, label="prueba F")
    b2 = ax.bar(xs + w / 2 + .01, fL, w, color=AZUL, label="Levene (mediana)")
    for bars in (b1, b2):
        for r_ in bars:
            ax.text(r_.get_x() + r_.get_width() / 2, r_.get_height() + .004, pct(r_.get_height()), ha="center", fontsize=7.5, color=TINTA)
    ax.axhline(0.05, color=SUAVE, lw=1, ls="--"); ax.text(-.45, .053, "5 % prometido", fontsize=7.5, color=SUAVE, ha="left")
    ax.set_xticks(xs, nombres); ax.set_ylabel("rechazos con H0 verdadera")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: pct(v, 0)))
    ax.legend(frameon=False, fontsize=8, loc="upper center")
    ax.set_title(f"Nivel real con dos muestras de {SIM['n']} y varianzas iguales ({fmt(SIM['reps'], 0)} simulaciones)")
    estilo(ax); fig.tight_layout(); fig.savefig(FIG / "u03_nivel_real.png", dpi=170); plt.close(fig)

    # 3 · caso
    c, D = R["caso"], R["_D"]
    r = D["registro"]
    fig, axs = plt.subplots(1, 2, figsize=(8, 2.9), gridspec_kw={"width_ratios": [1, 1.2]})
    ax = axs[0]
    datos = [r[r.maquina == m].desplazamiento_mm for m in ("pulpo 6", "pulpo 4")]
    bp = ax.boxplot(datos, widths=.45, patch_artist=True, medianprops={"color": TINTA}, showfliers=False)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: fmt(v, 2)))
    for p_, col in zip(bp["boxes"], (AZUL, NARANJA)):
        p_.set_facecolor(col); p_.set_alpha(.35); p_.set_edgecolor(col)
    for i, d_ in enumerate(datos, 1):
        ax.scatter(np.full(len(d_), i) + np.linspace(-.12, .12, len(d_)), d_, s=9, color=TINTA, zorder=3)
    ax.set_xticks([1, 2], [f"pulpo 6 (s = {fmt(c['s_6'], 4)})", f"pulpo 4 (s = {fmt(c['s_4'], 4)})"])
    ax.set_ylabel("desplazamiento (mm)"); ax.set_title("Registro: ¿varían igual?"); estilo(ax)
    ax = axs[1]
    h = c["homog"]; t = h["tasas"]; nn = np.array(c["n"])
    ee = 1.96 * np.sqrt(t * (1 - t) / nn)
    ax.errorbar(range(3), t, yerr=ee, fmt="o", color=NARANJA, ecolor=NARANJA, capsize=4, ms=7)
    ax.axhline(h["pb"], color=SUAVE, ls="--", lw=1); ax.text(1.3, h["pb"] + .0006, f"p̄ = {pct(h['pb'], 2)}", fontsize=7.5, color=SUAVE, va="bottom", ha="left")
    for i, v in enumerate(t):
        ax.text(i + .1, v, pct(v, 2), fontsize=8, color=TINTA, va="center")
    ax.set_xticks(range(3), c["prov"]); ax.set_xlim(-.4, 2.5)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: pct(v, 0)))
    ax.set_title("Tasa de defecto con intervalo del 95 %"); estilo(ax)
    fig.tight_layout(); fig.savefig(FIG / "u03_caso.png", dpi=170); plt.close(fig)


def ejecutar_cuaderno():
    """Ejecuta el cuaderno (nbconvert si está; si no, exec de sus celdas) y devuelve su RES."""
    nb = json.loads(CUADERNO.read_text(encoding="utf-8"))
    import matplotlib
    matplotlib.use("Agg")
    import warnings
    warnings.filterwarnings("ignore", message=".*non-interactive.*")
    previo = Path.cwd()
    os.chdir(NB)
    try:
        ns = {"__name__": "__cuaderno__"}
        for celda in nb["cells"]:
            if celda["cell_type"] == "code":
                exec("".join(celda["source"]), ns)
    finally:
        os.chdir(previo)
    return ns["RES"]


def comparar_cuaderno(R, RES):
    c = R["caso"]
    pares = [("ej_F", R["ej_F"]["F"]), ("ej_p_F", R["ej_F"]["p_der"]), ("ej_levene_p", R["ej_lev"]["p"]),
             ("ej_chi2", R["ej_chi"]["chi2"]), ("ej_z", R["ej_sello"]["z"]), ("ej_p_z", R["ej_sello"]["p_dos"]),
             ("caso_F", c["F"]["F"]), ("caso_p_F", c["F"]["p_dos"]), ("caso_levene_p", c["lev"]["p"]),
             ("caso_chi2", c["homog"]["chi2"]), ("caso_p_homog", c["homog"]["p"])]
    malos = [k for k, v in pares if abs(RES[k] - v) > 1e-9]
    print("CUADERNO:", "OK, reproduce el ejemplo y el caso" if not malos else f"difiere en {malos}")
    return not malos


def cadena(R):
    caso, D = R["_caso_mod"], R["_D"]
    C = caso.calcular(D)["u3"]
    c = R["caso"]
    ok = (abs(C["F"] - c["F"]["F"]) < 1e-12 and abs(C["p_F"] - c["F"]["p_dos"]) < 1e-12
          and abs(C["chi2_homog"] - c["homog"]["chi2"]) < 1e-9 and abs(C["p_homog"] - c["homog"]["p"]) < 1e-9
          and all(abs(u - v) < 1e-12 for u, v in zip(C["tasas"], c["homog"]["tasas"])))
    print("CADENA:", "OK, la pieza u3 del caso calza (F, p, tasas, χ² y p de homogeneidad)" if ok else "NO calza")
    return ok


# ---------------------------------------------------------------- impresión

def imprimir(R):
    e = R["ej"]
    print("== Ejemplo")
    print(f"   medias {fmt(e['media_a'], 2)} {fmt(e['media_b'], 2)} | s² {fmt(e['s2_a'], 4)} {fmt(e['s2_b'], 4)} | s {fmt(e['s_a'], 3)} {fmt(e['s_b'], 3)} | SC {fmt(e['ss_a'], 4)} {fmt(e['ss_b'], 4)}")
    q = R["ej_chi"]; print(f"   χ² B {fmt(q['chi2'], 2)} crit {fmt(R['ej_chi_crit'], 2)} p der {fmt(q['p_der'], 3)}")
    q = R["ej_F"]; print(f"   F {fmt(q['F'], 2)} crit {fmt(R['ej_F_crit'], 2)} p {fmt(q['p_der'], 4)} | dos colas {fmt(q['p_dos'], 4)}")
    q = R["ej_lev"]; print(f"   Levene W {fmt(q['W'], 2)} p {fmt(q['p'], 3)} medias z {[fmt(m, 4) for m in q['medias_z']]}")
    q = R["ej_sello"]; print(f"   sello p1 {pct(q['p1'], 2)} p2 {pct(q['p2'], 2)} p̄ {pct(q['pb'], 2)} ee0 {fmt(q['ee0'], 5)} z {fmt(q['z'], 2)} p {fmt(q['p_dos'], 3)} IC {pct(q['ic'][0], 2)} a {pct(q['ic'][1], 2)}")
    q = R["e1"]; print(f"== 3.1 χ² {fmt(q['chi2'], 2)} crit {fmt(R['e1_crit'], 2)} p {fmt(q['p_der'], 3)}")
    q = R["e2"]; print(f"== 3.2 F {fmt(q['F'], 2)} crit {fmt(R['e2_crit'], 2)} p {fmt(q['p_dos'], 3)}")
    q = R["e3"]; print(f"== 3.3 {pct(q['p1'], 2)} {pct(q['p2'], 2)} p̄ {pct(q['pb'], 2)} z {fmt(q['z'], 2)} p {fmt(q['p_dos'], 3)}")
    q = R["e4"]; print(f"== 3.4 sup {fmt(q['sup'], 2)} F(10,7) {fmt(q['inv'], 2)} inf {fmt(q['inf'], 3)}")
    q = R["e5"]; print(f"== 3.5 s² {fmt(q['s2x'], 5)} {fmt(q['s2y'], 5)} med {fmt(q['medx'], 3)} {fmt(q['medy'], 3)} F {fmt(R['e5_F']['F'], 2)} crit {fmt(R['e5_crit'], 2)} p {fmt(R['e5_F']['p_dos'], 3)}")
    q = R["e5_lev"]; print(f"     z X {[fmt(v, 3) for v in q['z'][0]]} z Y {[fmt(v, 3) for v in q['z'][1]]}")
    print(f"     medias z {[fmt(m, 5) for m in q['medias_z']]} z̄ {fmt(q['zbar'], 5)} entre {fmt(q['entre'], 6)} dentro {fmt(q['dentro'], 6)} W {fmt(q['W'], 2)} p {fmt(q['p'], 3)}")
    print(f"     sin atípico F {fmt(R['e5_sin']['F'], 2)} p {fmt(R['e5_sin']['p_dos'], 3)} | Shapiro X p {fmt(R['e5_shapiro'], 4)}")
    q = R["e6"]; print(f"== 3.6 tasas {[pct(t, 2) for t in q['tasas']]} p̄ {pct(q['pb'], 2)} χ² {fmt(q['chi2'], 2)} p {fmt(q['p'], 3)}")
    print(f"     esperados {[[fmt(v, 2) for v in fila_] for fila_ in q['esp']]}")
    print(f"     aportes {[[fmt(v, 2) for v in fila_] for fila_ in q['contrib']]}")
    q = R["e7"]; print(f"== 3.7 media {fmt(q['media'], 2)} s² {fmt(q['s2'], 4)} s {fmt(q['s'], 3)} χ² {fmt(R['e7_chi']['chi2'], 2)} crit {fmt(R['e7_crit'], 2)} p {fmt(R['e7_chi']['p_der'], 3)} IC σ {fmt(R['e7_ic'][0], 3)} {fmt(R['e7_ic'][1], 3)} cuantiles {fmt(R['e7_chi_q'][0], 3)} {fmt(R['e7_chi_q'][1], 3)}")
    q = R["e8"]; print(f"== 3.8 {pct(q['p1'], 2)} {pct(q['p2'], 2)} p̄ {pct(q['pb'], 2)} z {fmt(q['z'], 2)} p menor {fmt(q['p_menor'], 4)} dos {fmt(q['p_dos'], 4)} χ² {fmt(R['e8_chi'], 2)}")
    print(f"     IC95 p1-p2 {pct(q['ic'][0], 2)} {pct(q['ic'][1], 2)} | IC90 p2-p1 {pct(R['e8_ic90'][0], 2)} {pct(R['e8_ic90'][1], 2)}")
    print(f"== 3.9 crit {fmt(R['e9_crit'][0], 3)} {fmt(R['e9_crit'][1], 3)} potencias { {k: fmt(v, 2) for k, v in R['e9'].items()} } n {R['e9_n']} ({fmt(R['e9_n_pot'], 3)})")
    print(f"== 3.10 n {fmt(R['e10_n'], 1)} potencia con {E10['n_caso']}: {fmt(R['e10_pot'], 2)}")
    print("== simulación", {k: {kk: pct(vv) for kk, vv in v.items()} for k, v in R["sim"].items()})
    c = R["caso"]
    print(f"== Caso s² {fmt(c['s2_6'], 6)} {fmt(c['s2_4'], 6)} s {fmt(c['s_6'], 4)} {fmt(c['s_4'], 4)} F {fmt(c['F']['F'], 2)} p {fmt(c['F']['p_dos'], 2)} crit {fmt(c['F_crit'][0], 2)} {fmt(c['F_crit'][1], 2)}")
    print(f"   Levene W {fmt(c['lev']['W'], 2)} p {fmt(c['lev']['p'], 2)} (media {fmt(c['lev_media'], 2)}) Shapiro {fmt(c['shapiro'][0], 2)} {fmt(c['shapiro'][1], 2)} potencia {fmt(c['potencia'], 2)}")
    h = c["homog"]; print(f"   tasas {[pct(t, 2) for t in h['tasas']]} p̄ {pct(h['pb'], 2)} χ² {fmt(h['chi2'], 2)} p {fmt(h['p'], 3)}")
    print(f"   esperados {[[fmt(v, 2) for v in f_] for f_ in h['esp']]} aportes {[[fmt(v, 2) for v in f_] for f_ in h['contrib']]}")
    for (i, j), q in c["pares"].items():
        print(f"   {c['prov'][i]} vs {c['prov'][j]}: z {fmt(q['z'], 2)} p {fmt(q['p_dos'], 3)} Bonferroni {fmt(q['bonf'], 3)}")


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    E = []
    e = R["ej"]
    E += [fila("A (nueva)", *(fmt(x, 1) for x in EJ_A), "", ""), fila("B (antigua)", *(fmt(x, 1) for x in EJ_B))]
    E += [fmt(e["media_a"], 2), fmt(e["media_b"], 2), fmt(e["s2_a"], 4), fmt(e["s2_b"], 4), fmt(e["s_a"], 3), fmt(e["s_b"], 3)]
    E += [fmt(R["ej_chi"]["chi2"], 2), fmt(R["ej_chi_crit"], 2), fmt(R["ej_chi"]["p_der"], 3)]
    E += [fmt(R["ej_F"]["F"], 2), fmt(R["ej_F_crit"], 2), fmt(R["ej_F"]["p_der"], 4)]
    E += [fmt(R["ej_lev"]["W"], 2), fmt(R["ej_lev"]["p"], 3)]
    q = R["ej_sello"]
    E += [pct(q["p1"], 2), pct(q["p2"], 2), pct(q["pb"], 2), fmt(q["ee0"], 5), fmt(q["z"], 2), fmt(q["p_dos"], 3),
          pct(q["ic"][0], 2), pct(q["ic"][1], 2)]
    # ejercicios
    E += [fmt(R["e1"]["chi2"], 2), fmt(R["e1_crit"], 2), fmt(R["e1"]["p_der"], 3)]
    E += [fmt(R["e2"]["F"], 2), fmt(R["e2_crit"], 2), fmt(R["e2"]["p_dos"], 3)]
    q = R["e3"]; E += [pct(q["p1"], 2), pct(q["p2"], 2), pct(q["pb"], 2), fmt(q["z"], 2), fmt(q["p_dos"], 3)]
    q = R["e4"]; E += [fmt(q["sup"], 2), fmt(q["inv"], 2), fmt(q["inf"], 3)]
    E += [fila("X", *(fmt(x, 2) for x in E5_X)), fila("Y", *(fmt(x, 2) for x in E5_Y))]
    q = R["e5"]; E += [fmt(q["s2x"], 5), fmt(q["s2y"], 5), fmt(q["medx"], 3), fmt(q["medy"], 3),
                       fmt(R["e5_F"]["F"], 2), fmt(R["e5_crit"], 2), fmt(R["e5_F"]["p_dos"], 3)]
    q = R["e5_lev"]
    E += [fila("$z$ en X", *(fmt(v, 3) for v in q["z"][0])), fila("$z$ en Y", *(fmt(v, 3) for v in q["z"][1]))]
    E += [fmt(q["medias_z"][0], 5), fmt(q["medias_z"][1], 5), fmt(q["zbar"], 5), fmt(q["entre"], 6), fmt(q["dentro"], 6),
          fmt(q["W"], 2), fmt(q["p"], 2), fmt(R["e5_sin"]["F"], 2), fmt(R["e5_shapiro"], 4)]
    q = R["e6"]
    for (k, (x, n)), t, es, co in zip(E6.items(), q["tasas"], q["esp"], q["contrib"]):
        E.append(fila(k, str(x), str(n), pct(t, 2), fmt(es[0], 2), fmt(co[0], 2), fmt(co[1], 2)))
    E += [pct(q["pb"], 2), fmt(q["chi2"], 2), fmt(q["p"], 3)]
    E += [fila("Largo", *(fmt(x, 1) for x in E7[:5])), fila("Largo", *(fmt(x, 1) for x in E7[5:]))]
    q = R["e7"]; E += [fmt(q["media"], 2), fmt(q["s2"], 4), fmt(q["s"], 3), fmt(R["e7_chi"]["chi2"], 2), fmt(R["e7_crit"], 2),
                       fmt(R["e7_chi"]["p_der"], 3), fmt(R["e7_ic"][0], 3), fmt(R["e7_ic"][1], 3),
                       fmt(R["e7_chi_q"][0], 2), fmt(R["e7_chi_q"][1], 2)]
    q = R["e8"]; E += [pct(q["p1"], 2), pct(q["p2"], 2), pct(q["pb"], 2), fmt(q["z"], 2), fmt(q["p_menor"], 3), fmt(q["p_dos"], 3),
                       fmt(R["e8_chi"], 2), pct(q["ic"][0], 2), pct(q["ic"][1], 2), pct(R["e8_ic90"][0], 2), pct(R["e8_ic90"][1], 2)]
    E += [fmt(R["e9_crit"][0], 3), fmt(R["e9_crit"][1], 3)] + [fmt(v, 2) for v in R["e9"].values()] + [str(R["e9_n"])]
    E += [fmt(np.ceil(R["e10_n"]), 0), fmt(R["e10_n"], 1), fmt(R["e10_pot"], 2)]
    for k, v in R["sim"].items():
        E.append(fila(k, pct(v["F"]), pct(v["Levene"])))
    # caso
    c = R["caso"]
    E += [fmt(c["s_6"], 4), fmt(c["s_4"], 4), fmt(c["s2_6"], 6), fmt(c["s2_4"], 6), fmt(c["F"]["F"], 2), fmt(c["F"]["p_dos"], 2),
          fmt(c["F_crit"][0], 2), fmt(c["F_crit"][1], 2), fmt(c["lev"]["W"], 2), fmt(c["lev"]["p"], 2), fmt(c["lev_media"], 2),
          fmt(c["shapiro"][0], 2), fmt(c["shapiro"][1], 2), fmt(c["potencia"], 2)]
    h = c["homog"]
    for p_, x, n, t, es, co in zip(c["prov"], c["x"], c["n"], h["tasas"], h["esp"], h["contrib"]):
        E.append(fila(p_, str(x), str(n), pct(t, 2), fmt(es[0], 2), fmt(co[0], 2), fmt(co[1], 2)))
    E += [pct(h["pb"], 2), fmt(h["chi2"], 2), fmt(h["p"], 3)]
    for (i, j), q in c["pares"].items():
        E.append(fila(f"{c['prov'][i]} y {c['prov'][j]}", fmt(q["z"], 2), fmt(q["p_dos"], 3), fmt(q["bonf"], 3)))
    # lo que recibe de la unidad 2, leído del script del caso
    u2 = R["_caso_mod"].calcular(R["_D"])["u2"]
    E += [fmt(u2["t_welch"], 2), fmt(u2["p_welch"], 4), fmt(u2["t_pool"], 2), fmt(u2["p_pool"], 4)]
    # totales que el texto escribe como fracción
    E += [f"{sum(c['x'])}/{fmt(sum(c['n']), 0)}", f"{sum(x for x, _ in E6.values())}/{sum(n for _, n in E6.values())}",
          f"{E3['noche'][0] + E3['dia'][0]}/{fmt(E3['noche'][1] + E3['dia'][1], 0)}",
          f"{E8['v1'][0] + E8['v2'][0]}/{fmt(E8['v1'][1] + E8['v2'][1], 0)}",
          f"{EJ_SELLO['A'][0] + EJ_SELLO['B'][0]}/{fmt(EJ_SELLO['A'][1] + EJ_SELLO['B'][1], 0)}"]
    E += [f"semilla {SIM['semilla']}"]
    return E


if __name__ == "__main__":
    R = resultados()
    escribir_datos()
    figuras(R)
    imprimir(R)
    ok = cadena(R)
    if CUADERNO.exists():
        ok = comparar_cuaderno(R, ejecutar_cuaderno()) and ok
    else:
        print("CUADERNO: falta", CUADERNO); ok = False
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8").replace("{,}", ",").replace("{.}", ".").replace("\\ \\%", " %")   # en LaTeX el % va como \ \%
        faltan = [x for x in esperados(R) if x not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        ok = ok and not faltan
    sys.exit(0 if ok else 1)
