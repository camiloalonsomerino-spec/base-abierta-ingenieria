"""Unidad 2 · Comparar dos medias.

Recalcula todas las cifras de la unidad desde los datos, a mano (con la fórmula) y con scipy, y exige
que los dos caminos coincidan. Deja los datos del ejemplo en datos/u02_neumaticos.csv, dibuja las
figuras en unidades/figuras/, ejecuta el cuaderno notebooks/u02_dos_medias.ipynb y compara la pieza
del caso (u2) con el script del caso.

    python u02_dos_medias.py            # imprime los resultados
    python u02_dos_medias.py --revisar  # además busca cada cifra en el .md
"""
from pathlib import Path
from math import sqrt, ceil
import importlib.util, json, os, sys

import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
DATOS, FIG, NB = RAMO / "datos", RAMO / "unidades" / "figuras", RAMO / "notebooks"
MD = RAMO / "unidades" / "02-comparar-dos-medias.md"
CUADERNO = NB / "u02_dos_medias.ipynb"


# ---------------------------------------------------------------- formato a la chilena

def fmt(x, dec=1):
    s = f"{x:,.{dec}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return "0" + s[2:] if s.startswith("-0") and set(s[1:]) <= set("0,") else s


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def pv(p, dec=4):
    return "p < 0,001" if p < 0.001 else f"p = {fmt(p, dec)}"


def fila(*celdas):
    return "| " + " | ".join(celdas) + " |"


z = stats.norm.ppf
Phi = stats.norm.cdf


# ---------------------------------------------------------------- herramientas a mano

def resumen(x):
    x = np.asarray(x, float); n = len(x); m = x.sum() / n
    v = ((x - m) ** 2).sum() / (n - 1)
    return n, m, v


def t_combinada(n1, m1, v1, n2, m2, v2, d0=0.0):
    gl = n1 + n2 - 2
    sp2 = ((n1 - 1) * v1 + (n2 - 1) * v2) / gl
    ee = sqrt(sp2 * (1 / n1 + 1 / n2))
    t = (m1 - m2 - d0) / ee
    return {"sp2": sp2, "sp": sqrt(sp2), "ee": ee, "t": t, "gl": gl,
            "p_dos": 2 * stats.t.sf(abs(t), gl), "p_der": stats.t.sf(t, gl), "p_izq": stats.t.cdf(t, gl),
            "d": (m1 - m2) / sqrt(sp2), "dif": m1 - m2,
            "ic": (m1 - m2 - stats.t.ppf(0.975, gl) * ee, m1 - m2 + stats.t.ppf(0.975, gl) * ee)}


def t_welch(n1, m1, v1, n2, m2, v2, d0=0.0):
    a, b = v1 / n1, v2 / n2
    ee = sqrt(a + b)
    gl = (a + b) ** 2 / (a ** 2 / (n1 - 1) + b ** 2 / (n2 - 1))
    t = (m1 - m2 - d0) / ee
    return {"a": a, "b": b, "ee": ee, "t": t, "gl": gl,
            "p_dos": 2 * stats.t.sf(abs(t), gl), "p_der": stats.t.sf(t, gl), "p_izq": stats.t.cdf(t, gl),
            "dif": m1 - m2, "gl_tabla": int(gl),
            "ic": (m1 - m2 - stats.t.ppf(0.975, gl) * ee, m1 - m2 + stats.t.ppf(0.975, gl) * ee)}


def t_pareada(x, y):
    d = np.asarray(x, float) - np.asarray(y, float)
    n, m, v = resumen(d)
    ee = sqrt(v / n); t = m / ee
    return {"d": d, "n": n, "db": m, "sd": sqrt(v), "ee": ee, "t": t, "gl": n - 1,
            "p_dos": 2 * stats.t.sf(abs(t), n - 1), "p_der": stats.t.sf(t, n - 1), "dz": m / sqrt(v),
            "ic": (m - stats.t.ppf(0.975, n - 1) * ee, m + stats.t.ppf(0.975, n - 1) * ee)}


def comprobar_ind(x, y, C, W, alt="two-sided"):
    sp = stats.ttest_ind(x, y, equal_var=True, alternative=alt)
    sw = stats.ttest_ind(x, y, equal_var=False, alternative=alt)
    k = {"two-sided": "p_dos", "greater": "p_der", "less": "p_izq"}[alt]
    assert abs(sp.statistic - C["t"]) < 1e-10 and abs(sp.pvalue - C[k]) < 1e-10
    assert abs(sw.statistic - W["t"]) < 1e-10 and abs(sw.pvalue - W[k]) < 1e-10


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base (pasados por herramientas/colisiones.py).

# Ejemplo · flota de camiones de reparto de Puerto Montt, consumo (L/100 km) con dos marcas de neumático
EJ_A = [31.2, 28.4, 33.5, 29.8, 30.6, 27.9, 32.1, 30.3]    # diseño independiente: 8 camiones con marca A
EJ_B = [29.5, 27.1, 31.8, 28.9, 30.2, 26.4, 30.7, 28.6]    # y otros 8 camiones con marca B
EJ_PA = [30.8, 27.6, 33.9, 29.4, 31.5, 28.2, 32.7, 30.1]   # diseño pareado: 8 camiones con las dos marcas
EJ_PB = [29.6, 26.9, 32.4, 28.5, 30.1, 27.5, 31.2, 29.3]

# 2.2 · tiempo de ciclo (s) de dos moldes de inyección (resúmenes)
E2 = {"n1": 14, "m1": 38.6, "s1": 2.1, "n2": 12, "m2": 36.9, "s2": 1.8}
# 2.3 · horas de reparación de dos contratistas (resúmenes)
E3 = {"n1": 10, "m1": 6.8, "s1": 3.4, "n2": 16, "m2": 4.9, "s2": 1.2}
# 2.4 · piezas por hora de 8 operarios antes y después de reorganizar la estación
E4_ANTES = [42, 38, 45, 40, 36, 44, 39, 41]
E4_DESP = [45, 40, 47, 41, 40, 46, 39, 44]
# 2.5 · tiempo de fraguado (min) de un mortero con dos aditivos
E5_A = [42, 47, 39, 45, 50, 44, 41, 48, 46]
E5_B = [38, 41, 36, 44, 39, 35, 42, 40, 37, 43, 39]
# 2.6 · tiempo de despacho (min) con el software antiguo y el nuevo; el proveedor promete ahorrar más de 5
E6 = {"n1": 25, "m1": 48.2, "s1": 6.5, "n2": 22, "m2": 41.0, "s2": 5.9, "d0": 5.0}
# 2.7 · espesor de recubrimiento (µm) de 7 piezas medido con dos instrumentos
E7_I1 = [52.1, 48.7, 55.3, 50.2, 46.9, 53.8, 49.5]
E7_I2 = [53.0, 49.9, 56.1, 51.4, 47.5, 55.0, 50.3]
# 2.8 · tamaño de muestra para dos medias: δ = 1,5, σ = 3, α = 0,05 dos colas, potencia 0,80; potencia con 30
E8 = {"delta": 1.5, "sigma": 3.0, "alfa": 0.05, "pot": 0.80, "n_actual": 30}
# 2.9 · días de entrega de dos proveedores; A trae un pedido extraviado
E9_A = [4, 5, 3, 6, 4, 5, 4, 21]
E9_B = [7, 8, 6, 9, 7, 8, 7, 6]
# 2.10 · simulación del nivel real (H0 cierta) de la t combinada y de Welch
SIM = {"n1": 8, "s1": 4.0, "n2": 32, "s2": 1.0, "reps": 20_000, "semilla": 1101}
E10_K = 6     # tintas a comparar de a pares


# ---------------------------------------------------------------- resultados

def cargar_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_datos.py")
    caso = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caso)
    nombres = ["registro", "defectos", "reclamos_canal", "llegadas", "ventas", "secado", "lotes", "reclamos_dia"]
    D = {k: pd.read_csv(DATOS / f"{k}.csv") for k in nombres}
    return caso, D


def ind(x, y, alt="two-sided"):
    n1, m1, v1 = resumen(x); n2, m2, v2 = resumen(y)
    C = t_combinada(n1, m1, v1, n2, m2, v2); W = t_welch(n1, m1, v1, n2, m2, v2)
    comprobar_ind(x, y, C, W, alt)
    return {"n1": n1, "m1": m1, "v1": v1, "s1": sqrt(v1), "n2": n2, "m2": m2, "v2": v2, "s2": sqrt(v2),
            "C": C, "W": W, "sw1": stats.shapiro(x), "sw2": stats.shapiro(y), "mw": stats.mannwhitneyu(x, y, alternative=alt)}


def pareada(x, y, alt="two-sided"):
    P = t_pareada(x, y)
    sp = stats.ttest_rel(x, y, alternative=alt)
    k = {"two-sided": "p_dos", "greater": "p_der"}[alt]
    assert abs(sp.statistic - P["t"]) < 1e-10 and abs(sp.pvalue - P[k]) < 1e-10
    P["sw"] = stats.shapiro(P["d"])
    P["wil"] = stats.wilcoxon(x, y, alternative=alt)
    return P


def simular():
    rng = np.random.default_rng(SIM["semilla"])
    x = rng.normal(0, SIM["s1"], (SIM["reps"], SIM["n1"]))
    y = rng.normal(0, SIM["s2"], (SIM["reps"], SIM["n2"]))
    pc = stats.ttest_ind(x, y, axis=1, equal_var=True).pvalue
    pw = stats.ttest_ind(x, y, axis=1, equal_var=False).pvalue
    return {"comb": float((pc < 0.05).mean()), "welch": float((pw < 0.05).mean())}


def resultados():
    R = {}
    R["ej"] = ind(EJ_A, EJ_B)
    R["ej_par"] = pareada(EJ_PA, EJ_PB)
    R["ej_par_como_ind"] = ind(EJ_PA, EJ_PB)
    R["ej_par_r"] = stats.pearsonr(EJ_PA, EJ_PB).statistic
    # 2.2
    p = E2; R["e2"] = t_combinada(p["n1"], p["m1"], p["s1"] ** 2, p["n2"], p["m2"], p["s2"] ** 2)
    R["e2"]["crit"] = stats.t.ppf(0.975, R["e2"]["gl"])
    # 2.3
    p = E3; R["e3"] = {"W": t_welch(p["n1"], p["m1"], p["s1"] ** 2, p["n2"], p["m2"], p["s2"] ** 2),
                       "C": t_combinada(p["n1"], p["m1"], p["s1"] ** 2, p["n2"], p["m2"], p["s2"] ** 2)}
    R["e3"]["crit"] = stats.t.ppf(0.975, R["e3"]["W"]["gl_tabla"])
    R["e3"]["razon"] = p["s1"] / p["s2"]
    # 2.4
    R["e4"] = pareada(E4_DESP, E4_ANTES, "greater")
    R["e4"]["crit"] = stats.t.ppf(0.95, R["e4"]["gl"])
    # 2.5
    R["e5"] = ind(E5_A, E5_B)
    # 2.6
    p = E6
    R["e6"] = t_welch(p["n1"], p["m1"], p["s1"] ** 2, p["n2"], p["m2"], p["s2"] ** 2, d0=p["d0"])
    R["e6_0"] = t_welch(p["n1"], p["m1"], p["s1"] ** 2, p["n2"], p["m2"], p["s2"] ** 2)
    R["e6"]["ic_inf"] = (p["m1"] - p["m2"]) - stats.t.ppf(0.95, R["e6"]["gl"]) * R["e6"]["ee"]
    # 2.7
    R["e7_ind"] = ind(E7_I1, E7_I2)
    R["e7_par"] = pareada(E7_I1, E7_I2)
    R["e7_r"] = stats.pearsonr(E7_I1, E7_I2).statistic
    # 2.8
    p = E8
    nn = 2 * ((z(1 - p["alfa"] / 2) + z(p["pot"])) * p["sigma"] / p["delta"]) ** 2
    pot30 = Phi(p["delta"] / (p["sigma"] * sqrt(2 / p["n_actual"])) - z(1 - p["alfa"] / 2))
    from statsmodels.stats.power import NormalIndPower, TTestIndPower
    assert abs(NormalIndPower().solve_power(effect_size=p["delta"] / p["sigma"], alpha=p["alfa"], power=p["pot"]) - nn) < 0.05
    R["e8"] = {"n": nn, "n_ent": ceil(nn), "pot30": pot30,
               "n_t": TTestIndPower().solve_power(effect_size=p["delta"] / p["sigma"], alpha=p["alfa"], power=p["pot"]),
               "zarg": p["delta"] / (p["sigma"] * sqrt(2 / p["n_actual"]))}
    # 2.9
    R["e9"] = ind(E9_A, E9_B)
    R["e9_sin"] = ind(E9_A[:-1], E9_B)
    R["e9_med"] = (float(np.median(E9_A)), float(np.median(E9_B)))
    # 2.10
    R["sim"] = simular()
    k = E10_K * (E10_K - 1) // 2
    R["e10"] = {"k": k, "fwer": 1 - 0.95 ** k, "bonf": 0.05 / k}
    # caso
    caso, D = cargar_caso()
    reg = D["registro"]
    a = reg[reg.maquina == "pulpo 6"].desplazamiento_mm.to_numpy()
    b = reg[reg.maquina == "pulpo 4"].desplazamiento_mm.to_numpy()
    c = ind(a, b)
    c["mw_less"] = stats.mannwhitneyu(a, b, alternative="less")
    c["welch_less"] = stats.ttest_ind(a, b, equal_var=False, alternative="less")
    R["caso"] = c
    R["_caso_mod"], R["_D"], R["_a"], R["_b"] = caso, D, a, b
    return R


def escribir_datos():
    filas = ([{"diseno": "independiente", "camion": i, "marca": "A", "consumo_l100km": x} for i, x in enumerate(EJ_A, 1)]
             + [{"diseno": "independiente", "camion": i, "marca": "B", "consumo_l100km": x} for i, x in enumerate(EJ_B, 9)]
             + [{"diseno": "pareado", "camion": i, "marca": "A", "consumo_l100km": x} for i, x in enumerate(EJ_PA, 17)]
             + [{"diseno": "pareado", "camion": i, "marca": "B", "consumo_l100km": x} for i, x in enumerate(EJ_PB, 17)])
    pd.DataFrame(filas).to_csv(DATOS / "u02_neumaticos.csv", index=False, encoding="utf-8")


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

    # 1 · ejemplo: independiente contra pareado
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.0))
    ax = axs[0]
    for i, (d_, col) in enumerate(((EJ_A, AZUL), (EJ_B, NARANJA)), 1):
        ax.scatter(np.full(len(d_), i) + np.linspace(-.1, .1, len(d_)), d_, s=18, color=col, zorder=3)
        ax.hlines(np.mean(d_), i - .25, i + .25, color=TINTA, lw=1.5)
    ax.set_xticks([1, 2], ["marca A", "marca B"]); ax.set_xlim(.5, 2.5)
    ax.set_ylabel("consumo (L/100 km)"); ax.set_title(f"Independiente: 16 camiones · {pv(R['ej']['W']['p_dos'], 3)}"); estilo(ax)
    ax = axs[1]
    for a_, b_ in zip(EJ_PA, EJ_PB):
        ax.plot([1, 2], [a_, b_], color=SUAVE, lw=1, zorder=1)
    ax.scatter([1] * 8, EJ_PA, s=18, color=AZUL, zorder=3); ax.scatter([2] * 8, EJ_PB, s=18, color=NARANJA, zorder=3)
    ax.set_xticks([1, 2], ["marca A", "marca B"]); ax.set_xlim(.5, 2.5)
    ax.set_title(f"Pareado: 8 camiones con las dos · {pv(R['ej_par']['p_dos'], 3)}"); estilo(ax)
    fig.tight_layout(); fig.savefig(FIG / "u02_ejemplo.png", dpi=170); plt.close(fig)

    # 2 · caso: los dos pulpos
    c, a, b = R["caso"], R["_a"], R["_b"]
    fig, axs = plt.subplots(1, 2, figsize=(8, 2.9), gridspec_kw={"width_ratios": [1, 1.2]})
    ax = axs[0]
    bp = ax.boxplot([a, b], widths=.45, patch_artist=True, medianprops={"color": TINTA})
    for p_, col in zip(bp["boxes"], (AZUL, NARANJA)):
        p_.set_facecolor(col); p_.set_alpha(.35); p_.set_edgecolor(col)
    for i, d_ in enumerate((a, b), 1):
        ax.scatter(np.full(len(d_), i) + np.linspace(-.12, .12, len(d_)), d_, s=9, color=TINTA, zorder=3)
    ax.axhline(0.10, color=SUAVE, ls="--", lw=1); ax.text(2.45, 0.102, "meta", fontsize=7.5, color=SUAVE, ha="right")
    ax.set_xticks([1, 2], ["pulpo 6", "pulpo 4"]); ax.set_ylabel("desplazamiento (mm)"); ax.set_title("Registro por máquina"); estilo(ax)
    ax = axs[1]
    W = c["W"]
    ax.errorbar([W["dif"]], [0], xerr=[[W["dif"] - W["ic"][0]], [W["ic"][1] - W["dif"]]], fmt="o", color=NARANJA, capsize=5, ms=7)
    ax.axvline(0, color=SUAVE, lw=1, ls="--")
    ax.text(W["dif"], .25, f"{fmt(W['dif'], 4)} mm\n[{fmt(W['ic'][0], 3)}; {fmt(W['ic'][1], 3)}]", fontsize=8, ha="center", color=TINTA)
    ax.set_ylim(-.6, .8); ax.set_yticks([]); ax.set_xlim(-.08, .02)
    ax.set_xlabel("media pulpo 6 − media pulpo 4 (mm), IC 95 % de Welch"); ax.set_title("La diferencia y su intervalo"); estilo(ax)
    fig.tight_layout(); fig.savefig(FIG / "u02_caso.png", dpi=170); plt.close(fig)


# ---------------------------------------------------------------- cuaderno y cadena

def ejecutar_cuaderno():
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
    e, p, c = R["ej"], R["ej_par"], R["caso"]
    pares = [("ej_t_comb", e["C"]["t"]), ("ej_p_comb", e["C"]["p_dos"]), ("ej_t_welch", e["W"]["t"]), ("ej_p_welch", e["W"]["p_dos"]),
             ("ej_t_par", p["t"]), ("ej_p_par", p["p_dos"]),
             ("caso_t_welch", c["W"]["t"]), ("caso_p_welch", c["W"]["p_dos"]), ("caso_gl_welch", c["W"]["gl"]),
             ("caso_t_comb", c["C"]["t"]), ("caso_p_comb", c["C"]["p_dos"]), ("caso_d", c["C"]["d"]), ("caso_p_mw", c["mw"].pvalue)]
    malos = [k for k, v in pares if abs(RES[k] - v) > 1e-9]
    print("CUADERNO:", "OK, reproduce el ejemplo y el caso" if not malos else f"difiere en {malos}")
    return not malos


def cadena(R):
    caso, D = R["_caso_mod"], R["_D"]
    C = caso.calcular(D)["u2"]
    c = R["caso"]
    pares = [(C["media_6"], c["m1"]), (C["media_4"], c["m2"]), (C["de_6"], c["s1"]), (C["de_4"], c["s2"]),
             (C["t_welch"], c["W"]["t"]), (C["p_welch"], c["W"]["p_dos"]), (C["t_pool"], c["C"]["t"]), (C["p_pool"], c["C"]["p_dos"])]
    ok = all(abs(u - v) < 1e-10 for u, v in pares)
    J = json.loads((AQUI / "caso_estampa_sur_datos.json").read_text(encoding="utf-8"))["u2"]
    ok = ok and abs(J["t_welch"] - c["W"]["t"]) < 1e-10 and abs(J["p_pool"] - c["C"]["p_dos"]) < 1e-10
    print("CADENA:", "OK, la pieza u2 del caso calza (medias, desviaciones, t y p de Welch y combinada)" if ok else "NO calza")
    return ok


# ---------------------------------------------------------------- impresión

def imprimir_ind(nombre, r):
    C, W = r["C"], r["W"]
    print(f"== {nombre}: n {r['n1']},{r['n2']} medias {fmt(r['m1'], 4)} {fmt(r['m2'], 4)} var {fmt(r['v1'], 4)} {fmt(r['v2'], 4)} s {fmt(r['s1'], 4)} {fmt(r['s2'], 4)}")
    print(f"   comb: sp2 {fmt(C['sp2'], 4)} sp {fmt(C['sp'], 4)} ee {fmt(C['ee'], 4)} t {fmt(C['t'], 3)} gl {C['gl']} p {fmt(C['p_dos'], 4)} d {fmt(C['d'], 2)} IC {fmt(C['ic'][0], 3)}–{fmt(C['ic'][1], 3)}")
    print(f"   welch: a {fmt(W['a'], 5)} b {fmt(W['b'], 5)} ee {fmt(W['ee'], 4)} t {fmt(W['t'], 3)} gl {fmt(W['gl'], 2)} p {fmt(W['p_dos'], 4)} IC {fmt(W['ic'][0], 3)}–{fmt(W['ic'][1], 3)}")
    print(f"   SW p {fmt(r['sw1'].pvalue, 3)} {fmt(r['sw2'].pvalue, 3)} MW U {fmt(r['mw'].statistic, 1)} p {fmt(r['mw'].pvalue, 4)}")


def imprimir_par(nombre, P):
    print(f"== {nombre}: d {[fmt(x, 1) for x in P['d']]} d̄ {fmt(P['db'], 4)} sd {fmt(P['sd'], 4)} ee {fmt(P['ee'], 4)} t {fmt(P['t'], 2)} gl {P['gl']} p dos {P['p_dos']:.2e} der {P['p_der']:.2e} dz {fmt(P['dz'], 2)} IC {fmt(P['ic'][0], 3)}–{fmt(P['ic'][1], 3)} SW p {fmt(P['sw'].pvalue, 3)} Wilcoxon p {fmt(P['wil'].pvalue, 4)}")


def imprimir(R):
    imprimir_ind("Ejemplo independiente", R["ej"])
    imprimir_par("Ejemplo pareado", R["ej_par"])
    imprimir_ind("Ejemplo pareado analizado como independiente", R["ej_par_como_ind"])
    print(f"   r entre marcas {fmt(R['ej_par_r'], 3)}")
    e = R["e2"]; print(f"== 2.2 sp2 {fmt(e['sp2'], 4)} sp {fmt(e['sp'], 4)} ee {fmt(e['ee'], 4)} t {fmt(e['t'], 2)} gl {e['gl']} p {fmt(e['p_dos'], 4)} crit {fmt(e['crit'], 3)} IC {fmt(e['ic'][0], 2)}–{fmt(e['ic'][1], 2)} d {fmt(e['d'], 2)}")
    e = R["e3"]; W, C = e["W"], e["C"]
    print(f"== 2.3 razón s {fmt(e['razon'], 2)} welch a {fmt(W['a'], 3)} b {fmt(W['b'], 3)} ee {fmt(W['ee'], 4)} t {fmt(W['t'], 2)} gl {fmt(W['gl'], 2)} tabla {W['gl_tabla']} crit {fmt(e['crit'], 3)} p {fmt(W['p_dos'], 4)} | comb t {fmt(C['t'], 2)} gl {C['gl']} p {fmt(C['p_dos'], 4)}")
    imprimir_par("2.4", R["e4"]); print(f"   crit {fmt(R['e4']['crit'], 3)} p der {fmt(R['e4']['p_der'], 4)}")
    imprimir_ind("2.5", R["e5"])
    e = R["e6"]; e0 = R["e6_0"]; print(f"== 2.6 ee {fmt(e['ee'], 4)} t(5) {fmt(e['t'], 2)} gl {fmt(e['gl'], 1)} p {fmt(e['p_der'], 4)} cota inf {fmt(e['ic_inf'], 2)} | t(0) {fmt(e0['t'], 2)} p0 der {e0['p_der']:.2e}")
    imprimir_ind("2.7 como independiente", R["e7_ind"]); imprimir_par("2.7 pareada", R["e7_par"]); print(f"   r {fmt(R['e7_r'], 3)}")
    e = R["e8"]; print(f"== 2.8 n {fmt(e['n'], 2)} → {e['n_ent']} n t {fmt(e['n_t'], 2)} pot30 {fmt(e['pot30'], 3)} zarg {fmt(e['zarg'], 3)}")
    imprimir_ind("2.9 con el 21", R["e9"]); imprimir_ind("2.9 sin el 21", R["e9_sin"]); print(f"   medianas {R['e9_med']}")
    print(f"== 2.10 sim {R['sim']} k {R['e10']['k']} fwer {fmt(R['e10']['fwer'], 3)} bonf {fmt(R['e10']['bonf'], 4)}")
    imprimir_ind("Caso pulpo 6 contra pulpo 4", R["caso"])
    c = R["caso"]; print(f"   MW U {fmt(c['mw'].statistic, 0)} p {fmt(c['mw'].pvalue, 4)} | Welch una cola p {fmt(c['welch_less'].pvalue, 4)} | suma a {fmt(R['_a'].sum(), 3)} b {fmt(R['_b'].sum(), 3)}")


# ---------------------------------------------------------------- revisión contra el texto

def esp_ind(r, dm=4, dv=4, dt=2):
    C, W = r["C"], r["W"]
    return [fmt(r["m1"], dm), fmt(r["m2"], dm), fmt(r["v1"], dv), fmt(r["v2"], dv), fmt(C["sp2"], dv), fmt(C["ee"], 4),
            fmt(C["t"], dt), fmt(C["p_dos"], 4), fmt(W["ee"], 4), fmt(W["t"], dt), fmt(W["gl"], 1), fmt(W["p_dos"], 4)]


def esperados(R):
    E = []
    E += [fila(str(i), fmt(a, 1), fmt(b, 1)) for i, (a, b) in enumerate(zip(EJ_A, EJ_B), 1)]
    E += [fila(str(i), fmt(a, 1), fmt(b, 1), fmt(a - b, 1)) for i, (a, b) in enumerate(zip(EJ_PA, EJ_PB), 1)]
    e = R["ej"]; E += esp_ind(e, 3, 4) + [fmt(e["C"]["sp"], 4), fmt(e["C"]["d"], 2), fmt(e["C"]["ic"][0], 2), fmt(e["C"]["ic"][1], 2),
                                          fmt(e["sw1"].pvalue, 3), fmt(e["sw2"].pvalue, 3), fmt(e["W"]["a"], 4), fmt(e["W"]["b"], 4),
                                          fmt(stats.t.ppf(0.975, e["C"]["gl"]), 3), fmt(e["W"]["gl"], 1)]
    p = R["ej_par"]; E += [fmt(p["db"], 4), fmt(p["sd"], 4), fmt(p["ee"], 4), fmt(p["t"], 2), pv(p["p_dos"]), fmt(p["dz"], 2),
                           fmt(p["ic"][0], 2), fmt(p["ic"][1], 2), fmt(p["sw"].pvalue, 3)]
    q = R["ej_par_como_ind"]; E += [fmt(q["W"]["t"], 2), fmt(q["W"]["p_dos"], 4), fmt(R["ej_par_r"], 3)]
    e = R["e2"]; E += [fmt(e["sp2"], 4), fmt(e["sp"], 4), fmt(e["ee"], 4), fmt(e["t"], 2), fmt(e["p_dos"], 4), fmt(e["crit"], 3),
                       fmt(e["ic"][0], 2), fmt(e["ic"][1], 2), fmt(e["d"], 2)]
    e = R["e3"]; W, C = e["W"], e["C"]
    E += [fmt(e["razon"], 2), fmt(W["a"], 3), fmt(W["b"], 3), fmt(W["ee"], 4), fmt(W["t"], 2), fmt(W["gl"], 2), fmt(e["crit"], 3),
          fmt(W["p_dos"], 4), fmt(C["t"], 2), fmt(C["p_dos"], 4)]
    p = R["e4"]; E += [fila("Antes", *map(str, E4_ANTES)), fila("Después", *map(str, E4_DESP)),
                       fila("Diferencia", *(fmt(x, 0) for x in p["d"])),
                       fmt(p["db"], 3), fmt(p["sd"], 4), fmt(p["ee"], 4), fmt(p["t"], 2), fmt(p["crit"], 3), fmt(p["p_der"], 4), fmt(p["dz"], 2)]
    e = R["e5"]; E += [fila("A", *map(str, E5_A)), fila("B", *map(str, E5_B))] + esp_ind(e, 2, 2) + [
        fmt(e["sw1"].pvalue, 3), fmt(e["sw2"].pvalue, 3), fmt(e["C"]["d"], 2), fmt(e["W"]["ic"][0], 2), fmt(e["W"]["ic"][1], 2)]
    e = R["e6"]; e0 = R["e6_0"]; E += [fmt(e["ee"], 4), fmt(e["t"], 2), fmt(e["gl"], 1), fmt(e["p_der"], 4), fmt(e["ic_inf"], 2), fmt(e0["t"], 2)]
    i7 = R["e7_ind"]; p7 = R["e7_par"]
    E += [fila(str(i), fmt(a, 1), fmt(b, 1), fmt(a - b, 1)) for i, (a, b) in enumerate(zip(E7_I1, E7_I2), 1)]
    E += [fmt(i7["W"]["t"], 2), fmt(i7["W"]["p_dos"], 4), fmt(p7["db"], 3), fmt(p7["sd"], 4), fmt(p7["t"], 2), pv(p7["p_dos"]), fmt(R["e7_r"], 3)]
    e = R["e8"]; E += [fmt(e["n"], 1), f"{e['n_ent']} por grupo", fmt(e["n_t"], 1), fmt(e["pot30"], 3), fmt(e["zarg"], 3)]
    e = R["e9"]; s = R["e9_sin"]
    E += [fila("A", *map(str, E9_A)), fila("B", *map(str, E9_B)), fmt(e["m1"], 2), fmt(e["m2"], 2), fmt(e["W"]["t"], 2), fmt(e["W"]["p_dos"], 4),
          fmt(e["mw"].statistic, 1), fmt(e["mw"].pvalue, 4), fmt(s["m1"], 2), fmt(s["W"]["t"], 2), pv(s["W"]["p_dos"]),
          fmt(R["e9_med"][0], 1), fmt(R["e9_med"][1], 1), fmt(e["s1"], 2)]
    E += [pct(R["sim"]["comb"], 1), pct(R["sim"]["welch"], 1), f"semilla {SIM['semilla']}", fmt(SIM["reps"], 0),
          str(R["e10"]["k"]), fmt(R["e10"]["fwer"], 3), fmt(R["e10"]["bonf"], 4)]
    c = R["caso"]; C, W = c["C"], c["W"]
    E += [fmt(c["m1"], 4), fmt(c["m2"], 4), fmt(c["s1"], 4), fmt(c["s2"], 4), fmt(C["sp"], 4), fmt(C["ee"], 4), fmt(C["t"], 2), fmt(C["p_dos"], 4),
          fmt(W["ee"], 4), fmt(W["t"], 2), fmt(W["gl"], 1), fmt(W["p_dos"], 4), fmt(W["dif"], 4), fmt(W["ic"][0], 3), fmt(W["ic"][1], 3),
          fmt(C["d"], 2), fmt(c["sw1"].pvalue, 3), fmt(c["sw2"].pvalue, 3), fmt(c["mw"].statistic, 0), fmt(c["mw"].pvalue, 4),
          fmt(c["welch_less"].pvalue, 4)]
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
