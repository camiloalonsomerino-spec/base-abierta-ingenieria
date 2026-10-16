"""Unidad 1 · Prueba de hipótesis: valor p, región de rechazo y errores.

Recalcula todas las cifras de la unidad desde los datos, a mano (con la fórmula) y con scipy o
statsmodels, y exige que los dos caminos coincidan. Deja los datos del ejemplo en
datos/u01_pellets.csv, dibuja las figuras en unidades/figuras/, ejecuta el cuaderno
notebooks/u01_hipotesis.ipynb y compara la pieza del caso con el script del caso.

    python u01_hipotesis.py            # imprime los resultados
    python u01_hipotesis.py --revisar  # además busca cada cifra en el .md
"""
from pathlib import Path
from math import sqrt, ceil
import importlib.util, json, os, sys

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.power import NormalIndPower, TTestPower
from statsmodels.stats.proportion import proportions_ztest

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
DATOS, FIG, NB = RAMO / "datos", RAMO / "unidades" / "figuras", RAMO / "notebooks"
MD = RAMO / "unidades" / "01-prueba-de-hipotesis.md"
CUADERNO = NB / "u01_hipotesis.ipynb"


# ---------------------------------------------------------------- formato a la chilena

def fmt(x, dec=1):
    s = f"{x:,.{dec}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return "0" + s[2:] if s.startswith("-0") and set(s[1:]) <= set("0,") else s


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def pv(p, dec=4):
    """Valor p como se escribe en el texto: «p < 0,001» si es chico."""
    return "p < 0,001" if p < 0.001 else f"p = {fmt(p, dec)}"


def fila(*celdas):
    return "| " + " | ".join(celdas) + " |"


z = stats.norm.ppf
Phi = stats.norm.cdf


# ---------------------------------------------------------------- herramientas a mano

def prueba_t(x, mu0):
    """t = (x̄ − μ0)/(s/√n) con n − 1 gl, a mano. Devuelve las tres colas."""
    x = np.asarray(x, float); n = len(x)
    xb = x.sum() / n
    s = sqrt(((x - xb) ** 2).sum() / (n - 1))
    ee = s / sqrt(n)
    t = (xb - mu0) / ee
    gl = n - 1
    return {"n": n, "suma": x.sum(), "media": xb, "sc": ((x - xb) ** 2).sum(), "s": s, "ee": ee, "t": t, "gl": gl,
            "p_izq": stats.t.cdf(t, gl), "p_der": stats.t.sf(t, gl), "p_dos": 2 * stats.t.sf(abs(t), gl)}


def prueba_z(xb, mu0, sigma, n):
    ee = sigma / sqrt(n); zz = (xb - mu0) / ee
    return {"ee": ee, "z": zz, "p_izq": Phi(zz), "p_der": stats.norm.sf(zz), "p_dos": 2 * stats.norm.sf(abs(zz))}


def prueba_prop(x, n, p0):
    ph = x / n; ee = sqrt(p0 * (1 - p0) / n); zz = (ph - p0) / ee
    return {"ph": ph, "ee": ee, "z": zz, "p_der": stats.norm.sf(zz), "p_izq": Phi(zz), "p_dos": 2 * stats.norm.sf(abs(zz)),
            "np0": n * p0, "nq0": n * (1 - p0)}


def potencia_una_cola(delta, sigma, n, alfa):
    """Potencia de la prueba z de una cola para detectar un corrimiento |δ|."""
    return Phi(abs(delta) / (sigma / sqrt(n)) - z(1 - alfa))


def n_una_cola(delta, sigma, alfa, pot):
    return ((z(1 - alfa) + z(pot)) * sigma / abs(delta)) ** 2


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base (pasados por herramientas/colisiones.py).

# Ejemplo · fábrica de pellets de Los Ángeles: peso de 12 sacos que dicen 15 kg (kg)
EJ = [14.82, 15.05, 14.91, 14.78, 15.02, 14.95, 14.87, 15.10, 14.84, 14.96, 14.89, 14.99]
EJ_MU0 = 15.0
EJ_DELTA = 0.10          # el cliente quiere detectar sacos 100 g livianos
EJ_POT = 0.90
EJ_DELTA2 = 0.05         # y si quisiera detectar 50 g

# 1.2 · tableros: largo medio 2.440 mm, σ = 1,8 mm conocida, n = 40, x̄ = 2.440,7
E2 = {"mu0": 2440.0, "sigma": 1.8, "n": 40, "xb": 2440.7}
# 1.3 · un programa entrega t = −1,94 con 15 gl
E3 = {"t": -1.94, "gl": 15}
# 1.4 · reparto: 34 pedidos atrasados de 420; la promesa es a lo más 6 %
E4 = {"x": 34, "n": 420, "p0": 0.06}
# 1.5 · humedad de madera aserrada (%), 10 piezas; el comprador exige media de a lo más 12 %
E5 = [12.4, 11.8, 12.9, 12.6, 12.1, 13.0, 11.9, 12.7, 12.3, 12.5]
E5_MU0 = 12.0
# 1.6 · agua mineral: σ = 4 ml, n = 25, H1: μ < 500, alternativa 498, α = 0,05
E6 = {"mu0": 500.0, "sigma": 4.0, "n": 25, "mu1": 498.0, "alfa": 0.05, "pot": 0.90}
# 1.7 · informe municipal: IC 95 % de [18,4; 22,6] min, n = 36 (con z)
E7 = {"lo": 18.4, "hi": 22.6, "n": 36, "mu0s": [18.0, 20.0, 23.0]}
# 1.8 · (a) app de reparto: n = 40.000, x̄ = 31,2, s = 12, μ0 = 31; (b) piloto: 6 rutas, ahorro medio 4,1 min, s = 5,3
E8a = {"n": 40000, "xb": 31.2, "s": 12.0, "mu0": 31.0}
E8b = {"n": 6, "db": 4.1, "s": 5.3}
# 1.9 · lotes de cemento: H0 μ = 250 (conforme) contra H1 μ < 250; σ = 12, n = 9; lote malo μ = 240
E9 = {"mu0": 250.0, "mu1": 240.0, "sigma": 12.0, "n": 9, "p_malo": 0.25,
      "c1": 800_000, "c2": 5_000_000, "alfas": [0.01, 0.05, 0.10, 0.20]}
# 1.10 · vidriería: 7 botellas con burbujas en 60; meta a lo más 5 %; detectar 12 % con potencia 0,80
E10 = {"x": 7, "n": 60, "p0": 0.05, "p1": 0.12, "alfa": 0.05, "pot": 0.80}

# Caso · la meta del desplazamiento medio del registro es de 0,10 mm
CASO_META = 0.10
CASO_DELTA = 0.03        # corrimiento que el taller quiere detectar (media de 0,13 mm)
CASO_DELTA2 = 0.02


# ---------------------------------------------------------------- resultados

def cargar_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_datos.py")
    caso = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caso)
    nombres = ["registro", "defectos", "reclamos_canal", "llegadas", "ventas", "secado", "lotes", "reclamos_dia"]
    D = {k: pd.read_csv(DATOS / f"{k}.csv") for k in nombres}
    return caso, D


def resultados():
    R = {}
    # ---- ejemplo
    e = prueba_t(EJ, EJ_MU0)
    sp = stats.ttest_1samp(EJ, EJ_MU0, alternative="less")
    assert abs(sp.statistic - e["t"]) < 1e-12 and abs(sp.pvalue - e["p_izq"]) < 1e-12
    e["crit05"] = stats.t.ppf(0.05, e["gl"]); e["crit01"] = stats.t.ppf(0.01, e["gl"])
    e["t975"] = stats.t.ppf(0.975, e["gl"])
    e["ic"] = (e["media"] - e["t975"] * e["ee"], e["media"] + e["t975"] * e["ee"])
    e["cota_sup"] = e["media"] - e["crit05"] * e["ee"]          # cota superior 95 % (una cola)
    ic_sp = stats.t.interval(0.95, e["gl"], e["media"], e["ee"])
    assert abs(ic_sp[0] - e["ic"][0]) < 1e-12
    e["sw"] = stats.shapiro(EJ)
    e["desv"] = [x - e["media"] for x in EJ]
    # potencia con z y σ ≈ s
    e["pot_n12"] = potencia_una_cola(EJ_DELTA, e["s"], e["n"], 0.05)
    e["n_nec"] = n_una_cola(EJ_DELTA, e["s"], 0.05, EJ_POT)
    e["n_nec_t"] = TTestPower().solve_power(effect_size=EJ_DELTA / e["s"], alpha=0.05, power=EJ_POT, alternative="larger")
    pot_sm = NormalIndPower().power(effect_size=EJ_DELTA / e["s"], nobs1=e["n"], alpha=0.05, ratio=0, alternative="larger")
    assert abs(pot_sm - e["pot_n12"]) < 1e-9
    e["pot2_n12"] = potencia_una_cola(EJ_DELTA2, e["s"], e["n"], 0.05)
    e["n_nec2"] = n_una_cola(EJ_DELTA2, e["s"], 0.05, EJ_POT)
    e["d"] = (e["media"] - EJ_MU0) / e["s"]
    R["ej"] = e

    # ---- 1.2
    r = prueba_z(E2["xb"], E2["mu0"], E2["sigma"], E2["n"])
    r["ic"] = (E2["xb"] - 1.959964 * r["ee"], E2["xb"] + 1.959964 * r["ee"])
    R["e2"] = r
    # ---- 1.3
    t, gl = E3["t"], E3["gl"]
    R["e3"] = {"p_izq": stats.t.cdf(t, gl), "p_dos": 2 * stats.t.cdf(-abs(t), gl), "p_der": stats.t.sf(t, gl),
               "c_una05": stats.t.ppf(0.95, gl), "c_una01": stats.t.ppf(0.99, gl),
               "c_dos05": stats.t.ppf(0.975, gl), "c_dos01": stats.t.ppf(0.995, gl)}
    # ---- 1.4
    r = prueba_prop(E4["x"], E4["n"], E4["p0"])
    zs, ps = proportions_ztest(E4["x"], E4["n"], E4["p0"], alternative="larger", prop_var=E4["p0"])
    assert abs(zs - r["z"]) < 1e-12 and abs(ps - r["p_der"]) < 1e-12
    r["crit"] = z(0.95)
    R["e4"] = r
    # ---- 1.5
    r = prueba_t(E5, E5_MU0)
    sp = stats.ttest_1samp(E5, E5_MU0, alternative="greater")
    assert abs(sp.statistic - r["t"]) < 1e-12 and abs(sp.pvalue - r["p_der"]) < 1e-12
    r["crit05"] = stats.t.ppf(0.95, r["gl"]); r["t975"] = stats.t.ppf(0.975, r["gl"])
    r["ic"] = (r["media"] - r["t975"] * r["ee"], r["media"] + r["t975"] * r["ee"])
    r["cota_inf"] = r["media"] - r["crit05"] * r["ee"]
    r["sw"] = stats.shapiro(E5)
    R["e5"] = r
    # ---- 1.6
    p = E6; ee = p["sigma"] / sqrt(p["n"])
    xcrit = p["mu0"] - z(1 - p["alfa"]) * ee        # se rechaza si x̄ < xcrit
    beta = 1 - Phi((xcrit - p["mu1"]) / ee)
    pot = 1 - beta
    assert abs(pot - potencia_una_cola(p["mu1"] - p["mu0"], p["sigma"], p["n"], p["alfa"])) < 1e-12
    xcrit01 = p["mu0"] - z(0.99) * ee
    beta01 = 1 - Phi((xcrit01 - p["mu1"]) / ee)
    n_nec = n_una_cola(p["mu1"] - p["mu0"], p["sigma"], p["alfa"], p["pot"])
    pot_n = potencia_una_cola(p["mu1"] - p["mu0"], p["sigma"], ceil(n_nec), p["alfa"])
    R["e6"] = {"ee": ee, "xcrit": xcrit, "beta": beta, "pot": pot, "xcrit01": xcrit01, "beta01": beta01,
               "n_nec": n_nec, "n": ceil(n_nec), "pot_n": pot_n, "zarg": (xcrit - p["mu1"]) / ee}
    # ---- 1.7
    p = E7; xb = (p["lo"] + p["hi"]) / 2; ee = (p["hi"] - p["lo"]) / 2 / z(0.975)
    zs = {m: (xb - m) / ee for m in p["mu0s"]}
    ps = {m: 2 * stats.norm.sf(abs(v)) for m, v in zs.items()}
    ic99 = (xb - z(0.995) * ee, xb + z(0.995) * ee)
    R["e7"] = {"xb": xb, "ee": ee, "s": ee * sqrt(p["n"]), "z": zs, "p": ps, "ic99": ic99}
    # ---- 1.8
    a = E8a; ee = a["s"] / sqrt(a["n"]); za = (a["xb"] - a["mu0"]) / ee
    b = E8b; eeb = b["s"] / sqrt(b["n"]); tb = b["db"] / eeb
    R["e8"] = {"ee_a": ee, "z_a": za, "p_a": 2 * stats.norm.sf(za), "d_a": (a["xb"] - a["mu0"]) / a["s"],
               "seg_a": 60 * (a["xb"] - a["mu0"]),
               "ee_b": eeb, "t_b": tb, "p_b": stats.t.sf(tb, b["n"] - 1), "d_b": b["db"] / b["s"]}
    # ---- 1.9
    p = E9; ee = p["sigma"] / sqrt(p["n"]); filas = []
    for al in p["alfas"]:
        be = 1 - potencia_una_cola(p["mu1"] - p["mu0"], p["sigma"], p["n"], al)
        costo = (1 - p["p_malo"]) * al * p["c1"] + p["p_malo"] * be * p["c2"]
        filas.append({"alfa": al, "zc": z(1 - al), "xcrit": p["mu0"] - z(1 - al) * ee, "beta": be,
                      "c_I": (1 - p["p_malo"]) * al * p["c1"], "c_II": p["p_malo"] * be * p["c2"], "costo": costo})
    grid = np.linspace(0.001, 0.5, 49_901)
    costos = (1 - p["p_malo"]) * grid * p["c1"] + p["p_malo"] * (1 - Phi(abs(p["mu1"] - p["mu0"]) / ee - z(1 - grid))) * p["c2"]
    i = int(np.argmin(costos))
    R["e9"] = {"ee": ee, "filas": filas, "alfa_opt": grid[i], "costo_opt": costos[i],
               "beta_opt": 1 - Phi(abs(p["mu1"] - p["mu0"]) / ee - z(1 - grid[i]))}
    # ---- 1.10
    p = E10; r = prueba_prop(p["x"], p["n"], p["p0"])
    r["p_exacto"] = stats.binom.sf(p["x"] - 1, p["n"], p["p0"])
    assert abs(r["p_exacto"] - stats.binomtest(p["x"], p["n"], p["p0"], alternative="greater").pvalue) < 1e-12
    q0, q1 = 1 - p["p0"], 1 - p["p1"]
    nn = ((z(1 - p["alfa"]) * sqrt(p["p0"] * q0) + z(p["pot"]) * sqrt(p["p1"] * q1)) / (p["p1"] - p["p0"])) ** 2
    r["n_nec"] = nn; r["n"] = ceil(nn)
    # x crítico exacto con n = 60: el menor k con P(X ≥ k) ≤ α
    k = next(k for k in range(p["n"] + 1) if stats.binom.sf(k - 1, p["n"], p["p0"]) <= p["alfa"])
    r["k_crit"] = k; r["alfa_real"] = stats.binom.sf(k - 1, p["n"], p["p0"])
    r["pot_60"] = stats.binom.sf(k - 1, p["n"], p["p1"])
    R["e10"] = r

    # ---- caso
    caso, D = cargar_caso()
    reg = D["registro"]
    a = reg[reg.maquina == "pulpo 6"].desplazamiento_mm.to_numpy()
    b = reg[reg.maquina == "pulpo 4"].desplazamiento_mm.to_numpy()
    c = prueba_t(a, CASO_META)
    sp = stats.ttest_1samp(a, CASO_META, alternative="greater")
    assert abs(sp.statistic - c["t"]) < 1e-12 and abs(sp.pvalue - c["p_der"]) < 1e-12
    c["crit05"] = stats.t.ppf(0.95, c["gl"]); c["t975"] = stats.t.ppf(0.975, c["gl"])
    c["ic"] = (c["media"] - c["t975"] * c["ee"], c["media"] + c["t975"] * c["ee"])
    c["xcrit"] = CASO_META + c["crit05"] * c["ee"]
    c["sw"] = stats.shapiro(a)
    c["pot"] = potencia_una_cola(CASO_DELTA, c["s"], c["n"], 0.05)
    c["n_nec"] = n_una_cola(CASO_DELTA, c["s"], 0.05, 0.80)
    c["n_nec2"] = n_una_cola(CASO_DELTA2, c["s"], 0.05, 0.80)
    c["n_nec_t"] = TTestPower().solve_power(effect_size=CASO_DELTA / c["s"], alpha=0.05, power=0.80, alternative="larger")
    c["datos"] = list(a)
    c4 = prueba_t(b, CASO_META)
    c4["ic"] = (c4["media"] - stats.t.ppf(0.975, c4["gl"]) * c4["ee"], c4["media"] + stats.t.ppf(0.975, c4["gl"]) * c4["ee"])
    c4["sw"] = stats.shapiro(b)
    R["caso"], R["caso4"] = c, c4
    R["_caso_mod"], R["_D"] = caso, D
    return R


def escribir_datos():
    pd.DataFrame({"saco": range(1, len(EJ) + 1), "peso_kg": EJ}).to_csv(DATOS / "u01_pellets.csv", index=False, encoding="utf-8")


# ---------------------------------------------------------------- figuras

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

    # 1 · región de rechazo y valor p del ejemplo (t con 11 gl, cola izquierda)
    e = R["ej"]
    fig, axs = plt.subplots(1, 2, figsize=(8, 2.8))
    x = np.linspace(-4, 4, 600); y = stats.t.pdf(x, e["gl"])
    ax = axs[0]; ax.plot(x, y, color=TINTA, lw=1.5)
    m = x <= e["crit05"]; ax.fill_between(x[m], y[m], color=NARANJA, alpha=.6, lw=0)
    ax.axvline(e["t"], color=AZUL, lw=2)
    ax.text(e["crit05"] - .1, .12, f"rechazo\nt < {fmt(e['crit05'], 3)}\n(área 0,05)", fontsize=7.5, color=TINTA, ha="right")
    ax.text(e["t"] + .12, .33, f"t observado\n{fmt(e['t'], 2)}", fontsize=7.5, color=AZUL)
    ax.set_title("Región de rechazo (α = 0,05)"); ax.set_yticks([]); estilo(ax)
    ax = axs[1]; ax.plot(x, y, color=TINTA, lw=1.5)
    m = x <= e["t"]; ax.fill_between(x[m], y[m], color=AZUL, alpha=.45, lw=0)
    ax.axvline(e["t"], color=AZUL, lw=2)
    ax.text(e["t"] - .15, .12, f"valor p\n{fmt(e['p_izq'], 4)}", fontsize=7.5, color=TINTA, ha="right")
    ax.set_title("Valor p: el área más extrema que lo observado"); ax.set_yticks([]); estilo(ax)
    fig.tight_layout(); fig.savefig(FIG / "u01_regiones.png", dpi=170); plt.close(fig)

    # 2 · errores tipo I y II y curva de potencia (ejercicio 1.6 y ejemplo)
    p = E6; ee = R["e6"]["ee"]; xc = R["e6"]["xcrit"]
    fig, axs = plt.subplots(1, 2, figsize=(8, 2.9), gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axs[0]
    xs = np.linspace(494, 504, 700)
    y0 = stats.norm.pdf(xs, p["mu0"], ee); y1 = stats.norm.pdf(xs, p["mu1"], ee)
    ax.plot(xs, y0, color=TINTA, lw=1.4); ax.plot(xs, y1, color=AZUL, lw=1.4)
    ax.fill_between(xs[xs <= xc], y0[xs <= xc], color=NARANJA, alpha=.65, lw=0)
    ax.fill_between(xs[xs >= xc], y1[xs >= xc], color=AZUL, alpha=.25, lw=0)
    ax.axvline(xc, color=SUAVE, ls="--", lw=1)
    ax.text(p["mu0"] + .2, y0.max() * 1.02, "si H0 es cierta (μ = 500)", fontsize=7.5, color=TINTA)
    ax.text(p["mu1"] - 3.4, y1.max() * 1.02, "si μ = 498", fontsize=7.5, color=AZUL)
    ax.text(xc - .15, y0.max() * .02, f"α = 0,05", ha="right", fontsize=7.5, color=NARANJA)
    ax.text(xc + .75, y1.max() * .30, f"β = {fmt(R['e6']['beta'], 3)}", fontsize=7.5, color=AZUL)
    ax.text(xc - .1, y0.max() * .62, f"x̄ crítico\n{fmt(xc, 2)}", fontsize=7.5, color=SUAVE, ha="right")
    ax.set_xlabel("media muestral x̄ (ml)"); ax.set_yticks([]); ax.set_title("Errores tipo I y II con n = 25"); estilo(ax)
    ax = axs[1]
    mus = np.linspace(495, 500, 200)
    for n, col in ((10, LINEA), (25, AZUL), (50, NARANJA)):
        pot = [Phi((p["mu0"] - m) / (p["sigma"] / sqrt(n)) - z(0.95)) for m in mus]
        ax.plot(mus, pot, color=col if col != LINEA else SUAVE, lw=1.6, label=f"n = {n}")
    ax.axhline(0.05, color=SUAVE, lw=.8, ls=":"); ax.set_ylim(0, 1.02)
    ax.set_xlabel("media verdadera μ (ml)"); ax.set_ylabel("potencia")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: fmt(v, 1)))
    ax.legend(frameon=False, fontsize=7.5); ax.set_title("Curva de potencia"); estilo(ax)
    fig.tight_layout(); fig.savefig(FIG / "u01_errores_potencia.png", dpi=170); plt.close(fig)

    # 3 · caso: pulpo 6 contra la meta
    c, c4 = R["caso"], R["caso4"]
    fig, axs = plt.subplots(1, 2, figsize=(8, 2.8), gridspec_kw={"width_ratios": [1.3, 1]})
    ax = axs[0]
    ax.hist(c["datos"], bins=np.arange(0, 0.26, 0.02), color=AZUL, alpha=.45, edgecolor="white")
    ax.axvline(CASO_META, color=NARANJA, lw=2); ax.text(CASO_META + .003, 4.6, "meta 0,10", fontsize=7.5, color=NARANJA)
    ax.axvline(c["media"], color=TINTA, lw=1.2, ls="--"); ax.text(c["media"] + .003, 3.9, f"x̄ = {fmt(c['media'], 4)}", fontsize=7.5, color=TINTA)
    ax.set_xlabel("desplazamiento del registro (mm)"); ax.set_ylabel("prendas"); ax.set_title("Pulpo 6 · 18 prendas"); estilo(ax)
    ax = axs[1]
    for i, (cc, nombre, col) in enumerate(((c, "pulpo 6", AZUL), (c4, "pulpo 4", NARANJA))):
        ax.errorbar([cc["media"]], [i], xerr=[[cc["media"] - cc["ic"][0]], [cc["ic"][1] - cc["media"]]], fmt="o", color=col, capsize=4, ms=6)
        ax.text(cc["ic"][1] + .003, i, f"[{fmt(cc['ic'][0], 3)}; {fmt(cc['ic'][1], 3)}]", fontsize=7.5, va="center", color=TINTA)
    ax.axvline(CASO_META, color=NARANJA, lw=1, ls="--")
    ax.set_yticks([0, 1], ["pulpo 6", "pulpo 4"]); ax.set_ylim(-.6, 1.6); ax.set_xlim(.06, .21)
    ax.set_xlabel("media (mm), IC 95 %"); ax.set_title("Intervalos contra la meta"); estilo(ax)
    fig.tight_layout(); fig.savefig(FIG / "u01_caso.png", dpi=170); plt.close(fig)


# ---------------------------------------------------------------- cuaderno y cadena

def ejecutar_cuaderno():
    """Ejecuta el cuaderno (nbconvert si está; si no, exec de sus celdas) y devuelve su RES."""
    nb = json.loads(CUADERNO.read_text(encoding="utf-8"))
    import matplotlib
    matplotlib.use("Agg")
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
    e, c, c4 = R["ej"], R["caso"], R["caso4"]
    pares = [("ej_t", e["t"]), ("ej_p", e["p_izq"]), ("ej_ic_lo", e["ic"][0]), ("ej_ic_hi", e["ic"][1]),
             ("ej_pot", e["pot_n12"]), ("ej_n", e["n_nec"]),
             ("caso_media", c["media"]), ("caso_t", c["t"]), ("caso_p", c["p_der"]), ("caso_ic_lo", c["ic"][0]),
             ("caso_ic_hi", c["ic"][1]), ("caso_pot", c["pot"]), ("caso_n", c["n_nec"]), ("caso4_t", c4["t"]),
             ("caso4_p", c4["p_der"])]
    malos = [k for k, v in pares if abs(RES[k] - v) > 1e-9]
    print("CUADERNO:", "OK, reproduce el ejemplo y el caso" if not malos else f"difiere en {malos}")
    return not malos


def cadena(R):
    caso, D = R["_caso_mod"], R["_D"]
    C = caso.calcular(D)["u2"]
    c, c4 = R["caso"], R["caso4"]
    ok = (abs(C["media_6"] - c["media"]) < 1e-12 and abs(C["de_6"] - c["s"]) < 1e-12
          and abs(C["media_4"] - c4["media"]) < 1e-12 and abs(C["de_4"] - c4["s"]) < 1e-12)
    # la pieza también calza con el JSON del caso
    J = json.loads((AQUI / "caso_estampa_sur_datos.json").read_text(encoding="utf-8"))["u2"]
    ok = ok and abs(J["media_6"] - c["media"]) < 1e-12 and abs(J["de_6"] - c["s"]) < 1e-12
    print("CADENA:", "OK, las medias y desviaciones de los dos pulpos calzan con el script del caso" if ok else "NO calza")
    return ok


# ---------------------------------------------------------------- impresión

def imprimir(R):
    e = R["ej"]
    print("== Ejemplo pellets")
    for x, d in zip(EJ, e["desv"]):
        print(f"   {fmt(x, 2)}  {fmt(d, 4)}  {fmt(d * d, 6)}")
    print(f"   suma {fmt(e['suma'], 2)} x̄ {fmt(e['media'], 4)} SC {fmt(e['sc'], 4)} s {fmt(e['s'], 4)} ee {fmt(e['ee'], 4)} t {fmt(e['t'], 3)} gl {e['gl']}")
    print(f"   p izq {fmt(e['p_izq'], 4)} crit05 {fmt(e['crit05'], 3)} crit01 {fmt(e['crit01'], 3)} t975 {fmt(e['t975'], 3)}")
    print(f"   IC95 {fmt(e['ic'][0], 3)}–{fmt(e['ic'][1], 3)} cota sup {fmt(e['cota_sup'], 3)} SW W {fmt(e['sw'].statistic, 3)} p {fmt(e['sw'].pvalue, 3)}")
    print(f"   potencia n=12 {fmt(e['pot_n12'], 3)} n necesario z {fmt(e['n_nec'], 2)} t {fmt(e['n_nec_t'], 2)} d {fmt(e['d'], 2)} | δ2: pot {fmt(e['pot2_n12'], 3)} n {fmt(e['n_nec2'], 2)}")
    r = R["e2"]; print(f"== 1.2 ee {fmt(r['ee'], 4)} z {fmt(r['z'], 2)} p dos {fmt(r['p_dos'], 4)} IC {fmt(r['ic'][0], 2)}–{fmt(r['ic'][1], 2)}")
    r = R["e3"]; print(f"== 1.3 p izq {fmt(r['p_izq'], 4)} p dos {fmt(r['p_dos'], 4)} p der {fmt(r['p_der'], 4)} crit una {fmt(r['c_una05'], 3)} {fmt(r['c_una01'], 3)} dos {fmt(r['c_dos05'], 3)} {fmt(r['c_dos01'], 3)}")
    r = R["e4"]; print(f"== 1.4 p̂ {fmt(r['ph'], 4)} ee {fmt(r['ee'], 5)} z {fmt(r['z'], 2)} p {fmt(r['p_der'], 4)} np0 {fmt(r['np0'], 1)} nq0 {fmt(r['nq0'], 1)}")
    r = R["e5"]; print(f"== 1.5 x̄ {fmt(r['media'], 2)} s {fmt(r['s'], 4)} ee {fmt(r['ee'], 4)} t {fmt(r['t'], 2)} p {fmt(r['p_der'], 4)} crit {fmt(r['crit05'], 3)} IC {fmt(r['ic'][0], 2)}–{fmt(r['ic'][1], 2)} cota inf {fmt(r['cota_inf'], 2)} SW p {fmt(r['sw'].pvalue, 3)}")
    r = R["e6"]; print(f"== 1.6 ee {fmt(r['ee'], 2)} x̄crit {fmt(r['xcrit'], 2)} zarg {fmt(r['zarg'], 3)} β {fmt(r['beta'], 3)} pot {fmt(r['pot'], 3)} | α=0,01 x̄crit {fmt(r['xcrit01'], 2)} β {fmt(r['beta01'], 3)} | n {fmt(r['n_nec'], 2)} → {r['n']} pot {fmt(r['pot_n'], 3)}")
    r = R["e7"]; print(f"== 1.7 x̄ {fmt(r['xb'], 2)} ee {fmt(r['ee'], 4)} s {fmt(r['s'], 2)}", {k: (fmt(v, 2), fmt(r['p'][k], 4)) for k, v in r["z"].items()}, f"IC99 {fmt(r['ic99'][0], 2)}–{fmt(r['ic99'][1], 2)}")
    r = R["e8"]; print(f"== 1.8 a: ee {fmt(r['ee_a'], 3)} z {fmt(r['z_a'], 2)} p {pv(r['p_a'])} ({r['p_a']:.6f}) d {fmt(r['d_a'], 3)} seg {fmt(r['seg_a'], 0)} | b: ee {fmt(r['ee_b'], 3)} t {fmt(r['t_b'], 2)} p {fmt(r['p_b'], 4)} d {fmt(r['d_b'], 2)}")
    r = R["e9"]; print(f"== 1.9 ee {fmt(r['ee'], 1)}")
    for f in r["filas"]:
        print(f"   α {fmt(f['alfa'], 2)} z {fmt(f['zc'], 3)} x̄crit {fmt(f['xcrit'], 2)} β {fmt(f['beta'], 4)} cI {fmt(f['c_I'], 0)} cII {fmt(f['c_II'], 0)} total {fmt(f['costo'], 0)}")
    print(f"   óptimo α {fmt(r['alfa_opt'], 3)} β {fmt(r['beta_opt'], 3)} costo {fmt(r['costo_opt'], 0)}")
    r = R["e10"]; print(f"== 1.10 p̂ {fmt(r['ph'], 4)} np0 {fmt(r['np0'], 1)} z {fmt(r['z'], 2)} p z {fmt(r['p_der'], 4)} p exacto {fmt(r['p_exacto'], 4)} n {fmt(r['n_nec'], 1)} → {r['n']} k crit {r['k_crit']} α real {fmt(r['alfa_real'], 4)} pot60 {fmt(r['pot_60'], 3)}")
    c = R["caso"]; c4 = R["caso4"]
    print("== Caso pulpo 6:", " ".join(fmt(x, 3) for x in c["datos"]))
    print(f"   n {c['n']} suma {fmt(c['suma'], 3)} x̄ {fmt(c['media'], 4)} s {fmt(c['s'], 4)} ee {fmt(c['ee'], 4)} t {fmt(c['t'], 2)} p {fmt(c['p_der'], 3)} crit {fmt(c['crit05'], 3)} x̄crit {fmt(c['xcrit'], 4)}")
    print(f"   IC {fmt(c['ic'][0], 3)}–{fmt(c['ic'][1], 3)} SW W {fmt(c['sw'].statistic, 3)} p {fmt(c['sw'].pvalue, 3)} pot(0,03) {fmt(c['pot'], 3)} n80 {fmt(c['n_nec'], 1)} n80 t {fmt(c['n_nec_t'], 1)} n80(0,02) {fmt(c['n_nec2'], 1)}")
    print(f"   pulpo 4: x̄ {fmt(c4['media'], 4)} s {fmt(c4['s'], 4)} t {fmt(c4['t'], 2)} p {pv(c4['p_der'])} IC {fmt(c4['ic'][0], 3)}–{fmt(c4['ic'][1], 3)} SW p {fmt(c4['sw'].pvalue, 3)}")


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    E = []
    e = R["ej"]
    for i, (x, d) in enumerate(zip(EJ, e["desv"]), 1):
        E.append(fila(str(i), fmt(x, 2), fmt(d, 4), fmt(d * d, 6)))
    E += [fmt(e["suma"], 2), fmt(e["media"], 4), fmt(e["sc"], 4), fmt(e["s"], 4), fmt(e["ee"], 4), fmt(e["t"], 2),
          fmt(e["p_izq"], 4), fmt(e["crit05"], 3), fmt(e["crit01"], 3), fmt(e["t975"], 3),
          fmt(e["ic"][0], 3), fmt(e["ic"][1], 3), fmt(e["cota_sup"], 3), fmt(e["sw"].statistic, 3), fmt(e["sw"].pvalue, 3),
          fmt(e["pot_n12"], 3), fmt(e["n_nec"], 1), fmt(e["n_nec_t"], 1), fmt(e["d"], 2), fmt(e["pot2_n12"], 3), fmt(e["n_nec2"], 1),
          f"{fmt(1000 * (EJ_MU0 - e['media']), 0)} g por saco", f"unos {fmt(2000 * (EJ_MU0 - e['media']), 0)} kg",
          fmt(stats.t.ppf(0.975, 9), 3)]      # t de 9 gl del IC de 1.5
    r = R["e2"]; E += [fmt(r["ee"], 4), fmt(r["z"], 2), fmt(r["p_dos"], 4), fmt(r["ic"][0], 2), fmt(r["ic"][1], 2)]
    r = R["e3"]; E += [fmt(r["p_izq"], 4), fmt(r["p_dos"], 4), fmt(r["c_una05"], 3), fmt(r["c_una01"], 3), fmt(r["c_dos05"], 3), fmt(r["c_dos01"], 3)]
    r = R["e4"]; E += [fmt(r["ph"], 4), fmt(r["ee"], 5), fmt(r["z"], 2), fmt(r["p_der"], 4), fmt(r["np0"], 1)]
    r = R["e5"]; E += [fila(*(fmt(x, 1) for x in E5)), fmt(r["media"], 2), fmt(r["s"], 4), fmt(r["ee"], 4), fmt(r["t"], 2), fmt(r["p_der"], 4),
                       fmt(r["crit05"], 3), fmt(r["ic"][0], 2), fmt(r["ic"][1], 2), fmt(r["cota_inf"], 2), fmt(r["sw"].pvalue, 3)]
    r = R["e6"]; E += [fmt(r["xcrit"], 2), fmt(r["zarg"], 3), fmt(r["beta"], 3), fmt(r["pot"], 3), fmt(r["xcrit01"], 2), fmt(r["beta01"], 3),
                       fmt(r["n_nec"], 2), f"n = {r['n']}", fmt(r["pot_n"], 3)]
    r = R["e7"]; E += [fmt(r["xb"], 2), fmt(r["ee"], 4), fmt(r["ic99"][0], 2), fmt(r["ic99"][1], 2)]
    E += [fmt(v, 2) for v in r["z"].values()] + [fmt(v, 4) for v in r["p"].values()]
    r = R["e8"]; E += [fmt(r["ee_a"], 3), fmt(r["z_a"], 2), pv(r["p_a"]), fmt(r["d_a"], 3), fmt(r["ee_b"], 3), fmt(r["t_b"], 2), fmt(r["p_b"], 4), fmt(r["d_b"], 2)]
    r = R["e9"]
    for f in r["filas"]:
        E.append(fila(fmt(f["alfa"], 2), fmt(f["xcrit"], 2), fmt(f["beta"], 4), "$" + fmt(f["c_I"], 0), "$" + fmt(f["c_II"], 0), "$" + fmt(f["costo"], 0)))
    E += [fmt(r["alfa_opt"], 3), fmt(r["beta_opt"], 3), "$" + fmt(r["costo_opt"], 0)]
    r = R["e10"]; E += [fmt(r["ph"], 4), fmt(r["z"], 2), fmt(r["p_der"], 4), fmt(r["p_exacto"], 4), fmt(r["n_nec"], 1), f"{r['n']} botellas",
                        f"{r['k_crit']} o más", fmt(r["alfa_real"], 4), fmt(r["pot_60"], 3)]
    c, c4 = R["caso"], R["caso4"]
    E += [fila(*(fmt(x, 3) for x in c["datos"][:9])), fila(*(fmt(x, 3) for x in c["datos"][9:]))]
    E += [fmt(c["suma"], 3), fmt(c["media"], 4), fmt(c["s"], 4), fmt(c["ee"], 4), fmt(c["t"], 2), fmt(c["p_der"], 3), fmt(c["crit05"], 3),
          fmt(c["xcrit"], 4), fmt(c["ic"][0], 3), fmt(c["ic"][1], 3), fmt(c["sw"].statistic, 3), fmt(c["sw"].pvalue, 3),
          fmt(c["pot"], 2), fmt(c["n_nec"], 1), fmt(c["n_nec2"], 1),
          fmt(c4["media"], 4), fmt(c4["s"], 4), fmt(c4["t"], 2), pv(c4["p_der"]), fmt(c4["ic"][0], 3), fmt(c4["ic"][1], 3)]
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
        md = MD.read_text(encoding="utf-8").replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        ok = ok and not faltan
    sys.exit(0 if ok else 1)
