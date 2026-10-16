"""Unidad 6 · Correlación.

Recalcula todas las cifras de la unidad desde los datos (a mano, con la fórmula, y con scipy; las dos
tienen que coincidir), deja el CSV del ejemplo en datos/u06_mote.csv, dibuja las figuras en
unidades/figuras/, ejecuta el cuaderno notebooks/u06_correlacion.ipynb y compara sus resultados, y
comprueba la pieza del caso contra caso_estampa_sur_datos.py.

    python u06_correlacion.py            # imprime los resultados
    python u06_correlacion.py --revisar  # además busca cada cifra en el .md
"""
from math import atanh, sqrt, tanh
from pathlib import Path
import importlib.util, itertools, json, os, sys, warnings

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")

AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
DATOS, FIG, NB = RAMO / "datos", RAMO / "unidades" / "figuras", RAMO / "notebooks"
MD = RAMO / "unidades" / "06-correlacion.md"

TINTA, SUAVE, LINEA, ACENTO = "#2B2F33", "#5F656B", "#D6D3CE", "#E2622A"


# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def pval(p, dec=3):
    return "p < 0,001" if p < 0.001 else "p = " + fmt(p, dec)


def pearson_a_mano(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float); n = len(x)
    dx, dy = x - x.mean(), y - y.mean()
    sxy, sxx, syy = (dx * dy).sum(), (dx ** 2).sum(), (dy ** 2).sum()
    r = sxy / sqrt(sxx * syy)
    t = r * sqrt(n - 2) / sqrt(1 - r ** 2)
    p = 2 * stats.t.sf(abs(t), n - 2)
    return {"n": n, "mx": x.mean(), "my": y.mean(), "dx": dx, "dy": dy, "sxy": sxy, "sxx": sxx, "syy": syy,
            "cov": sxy / (n - 1), "sx": sqrt(sxx / (n - 1)), "sy": sqrt(syy / (n - 1)), "r": r, "t": t, "p": p}


def rangos(v):
    return stats.rankdata(v)


def spearman_a_mano(x, y):
    rx, ry = rangos(x), rangos(y); d = rx - ry; n = len(x)
    return {"rx": rx, "ry": ry, "d2": float((d ** 2).sum()), "rho": 1 - 6 * (d ** 2).sum() / (n * (n ** 2 - 1))}


def kendall_a_mano(x, y):
    c = dd = 0
    for i, j in itertools.combinations(range(len(x)), 2):
        s = np.sign(x[i] - x[j]) * np.sign(y[i] - y[j])
        c += s > 0; dd += s < 0
    n = len(x)
    return {"C": int(c), "D": int(dd), "pares": n * (n - 1) // 2, "tau": (c - dd) / (n * (n - 1) / 2)}


def todas(x, y):
    pr, sp, kt = stats.pearsonr(x, y), stats.spearmanr(x, y), stats.kendalltau(x, y)
    return {"r": float(pr.statistic), "p_r": float(pr.pvalue), "rho": float(sp.statistic), "p_rho": float(sp.pvalue),
            "tau": float(kt.statistic), "p_tau": float(kt.pvalue)}


def parcial(rxy, rxz, ryz):
    return (rxy - rxz * ryz) / sqrt((1 - rxz ** 2) * (1 - ryz ** 2))


def fisher_ic(r, n, z=1.959964):
    zr, se = atanh(r), 1 / sqrt(n - 3)
    return zr, se, tanh(zr - z * se), tanh(zr + z * se)


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base; pasados por herramientas/colisiones.py.

# Ejemplo · carrito de mote con huesillo en Chillán: temperatura máxima (°C) y vasos vendidos, 8 días
EJ_T = [21, 24, 26, 27, 29, 30, 32, 35]
EJ_V = [58, 66, 79, 72, 90, 84, 101, 98]

# 6.1 · horas de estudio semanales y puntaje de un ensayo, 6 estudiantes
E1_X = [2, 4, 5, 7, 8, 10]
E1_Y = [480, 530, 520, 600, 610, 650]

# 6.2 · prueba de la correlación con r dado
E2_R, E2_N, E2_N2 = -0.38, 25, 100

# 6.3 · dos jueces ordenan 7 empanadas (1 = la mejor)
E3_A = [1, 2, 3, 4, 5, 6, 7]
E3_B = [2, 1, 4, 3, 7, 5, 6]

# 6.4 · temperatura media (°C) y consumo de gas (kWh) de una casa, 5 semanas
E4_T = [4, 7, 9, 12, 15]
E4_G = [38, 31, 29, 22, 16]
E4_MJ = 3.6   # 1 kWh = 3,6 MJ

# 6.5 · superficie (m²) y ventas mensuales (millones de pesos) de 10 sucursales
E5_X = [84, 93, 101, 107, 116, 122, 129, 137, 146, 420]
E5_Y = [31, 27, 35, 29, 33, 26, 34, 30, 28, 96]

# 6.6 · semana y seguidores de una cuenta nueva
E6_X = [1, 2, 3, 4, 5, 6, 7, 8]
E6_Y = [120, 150, 200, 270, 380, 540, 790, 1150]

# 6.7 · temperatura media diaria (°C) y consumo eléctrico de una oficina (kWh)
E7_X = [2, 6, 10, 14, 18, 22, 26, 30]
E7_Y = [182, 151, 128, 116, 118, 131, 157, 190]

# 6.8 · 12 meses: temperatura media (°C), bufandas vendidas y consultas por resfrío en un CESFAM
E8_Z = [18, 17, 14, 11, 8, 6, 5, 7, 9, 12, 15, 17]
E8_X = [232, 238, 248, 270, 302, 333, 327, 312, 319, 284, 253, 232]
E8_Y = [118, 105, 149, 185, 181, 252, 210, 206, 177, 158, 154, 100]

# 6.9 · intervalo de Fisher y comparación de dos correlaciones
E9_R1, E9_N1, E9_RHO0 = 0.62, 40, 0.40
E9_R2, E9_N2 = 0.35, 55

# 6.10 · muchas correlaciones entre variables independientes
E10_SEMILLA, E10_VARS, E10_N = 606, 15, 40


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # ---- ejemplo
    a = pearson_a_mano(EJ_T, EJ_V); s = todas(EJ_T, EJ_V)
    assert abs(a["r"] - s["r"]) < 1e-12 and abs(a["p"] - s["p_r"]) < 1e-12
    sp = spearman_a_mano(EJ_T, EJ_V); kt = kendall_a_mano(EJ_T, EJ_V)
    assert abs(sp["rho"] - s["rho"]) < 1e-12 and abs(kt["tau"] - s["tau"]) < 1e-12
    R["ej"] = {**a, **{k: s[k] for k in ("p_rho", "p_tau")}, "rho": sp["rho"], "d2": sp["d2"], "rv": sp["ry"],
               "tau": kt["tau"], "C": kt["C"], "D": kt["D"], "r2": a["r"] ** 2,
               "crit_t": float(stats.t.ppf(0.975, a["n"] - 2))}
    zr, se, lo, hi = fisher_ic(a["r"], a["n"])
    R["ej"].update(ic=(lo, hi), zr=zr, se=se)

    # ---- 6.1
    a1 = pearson_a_mano(E1_X, E1_Y)
    assert abs(a1["r"] - stats.pearsonr(E1_X, E1_Y).statistic) < 1e-12
    R["e1"] = a1

    # ---- 6.2
    def prueba_r(r, n):
        t = r * sqrt(n - 2) / sqrt(1 - r ** 2)
        return t, 2 * stats.t.sf(abs(t), n - 2), float(stats.t.ppf(0.975, n - 2))
    t25, p25, c25 = prueba_r(E2_R, E2_N); t100, p100, c100 = prueba_r(E2_R, E2_N2)
    # r mínimo significativo con n = 25: t crítico despejado
    rmin = c25 / sqrt(E2_N - 2 + c25 ** 2)
    R["e2"] = {"t25": t25, "p25": p25, "c25": c25, "t100": t100, "p100": p100, "c100": c100, "r2": E2_R ** 2, "rmin": rmin}

    # ---- 6.3
    s3 = spearman_a_mano(E3_A, E3_B); k3 = kendall_a_mano(E3_A, E3_B)
    t3 = todas(E3_A, E3_B)
    assert abs(s3["rho"] - t3["rho"]) < 1e-12 and abs(k3["tau"] - t3["tau"]) < 1e-12
    R["e3"] = {**s3, **k3, "p_rho": t3["p_rho"], "p_tau": t3["p_tau"]}

    # ---- 6.4
    a4 = pearson_a_mano(E4_T, E4_G)
    tf = [32 + 1.8 * v for v in E4_T]; mj = [E4_MJ * v for v in E4_G]
    a4f = pearson_a_mano(tf, E4_G); a4m = pearson_a_mano(tf, mj)
    assert abs(a4["r"] - a4f["r"]) < 1e-12 and abs(a4["r"] - a4m["r"]) < 1e-12
    R["e4"] = {"cov": a4["cov"], "r": a4["r"], "cov_f": a4f["cov"], "cov_fmj": a4m["cov"], "tf": tf}

    # ---- 6.5
    con = todas(E5_X, E5_Y); sin = todas(E5_X[:-1], E5_Y[:-1])
    R["e5"] = {"con": con, "sin": sin}

    # ---- 6.6
    t6 = todas(E6_X, E6_Y); tl = todas(E6_X, np.log(E6_Y))
    R["e6"] = {**t6, "r_log": tl["r"]}

    # ---- 6.7
    t7 = todas(E7_X, E7_Y)
    izq = todas(E7_X[:4], E7_Y[:4]); der = todas(E7_X[4:], E7_Y[4:])
    R["e7"] = {**t7, "r_izq": izq["r"], "r_der": der["r"]}

    # ---- 6.8
    rxy = stats.pearsonr(E8_X, E8_Y).statistic; rxz = stats.pearsonr(E8_X, E8_Z).statistic
    ryz = stats.pearsonr(E8_Y, E8_Z).statistic
    rp = parcial(rxy, rxz, ryz)
    # segundo camino: correlación de los residuos de x y de y tras regresarlos en z
    rx = np.array(E8_X) - np.polyval(np.polyfit(E8_Z, E8_X, 1), E8_Z)
    ry = np.array(E8_Y) - np.polyval(np.polyfit(E8_Z, E8_Y, 1), E8_Z)
    assert abs(np.corrcoef(rx, ry)[0, 1] - rp) < 1e-12
    n8 = len(E8_X); tp = rp * sqrt(n8 - 3) / sqrt(1 - rp ** 2)
    R["e8"] = {"rxy": float(rxy), "rxz": float(rxz), "ryz": float(ryz), "rp": float(rp), "tp": tp,
               "pp": float(2 * stats.t.sf(abs(tp), n8 - 3)), "p_xy": float(stats.pearsonr(E8_X, E8_Y).pvalue)}

    # ---- 6.9
    z1, se1, lo1, hi1 = fisher_ic(E9_R1, E9_N1)
    zt = (z1 - atanh(E9_RHO0)) / se1
    z2 = atanh(E9_R2); zdif = (z1 - z2) / sqrt(1 / (E9_N1 - 3) + 1 / (E9_N2 - 3))
    R["e9"] = {"z1": z1, "se1": se1, "ic": (lo1, hi1), "zt": zt, "pt": float(2 * stats.norm.sf(abs(zt))),
               "z2": z2, "zdif": zdif, "pdif": float(2 * stats.norm.sf(abs(zdif)))}

    # ---- 6.10
    rng = np.random.default_rng(E10_SEMILLA)
    M = rng.normal(size=(E10_N, E10_VARS))
    ps = [stats.pearsonr(M[:, i], M[:, j]).pvalue for i, j in itertools.combinations(range(E10_VARS), 2)]
    rs = [abs(stats.pearsonr(M[:, i], M[:, j]).statistic) for i, j in itertools.combinations(range(E10_VARS), 2)]
    m = len(ps)
    R["e10"] = {"pares": m, "esperados": 0.05 * m, "sig": int(sum(p < 0.05 for p in ps)),
                "bonf": 0.05 / m, "sig_bonf": int(sum(p < 0.05 / m for p in ps)), "rmax": max(rs),
                "rcrit": float(stats.t.ppf(0.975, E10_N - 2) / sqrt(E10_N - 2 + stats.t.ppf(0.975, E10_N - 2) ** 2))}

    # ---- caso
    v = pd.read_csv(DATOS / "ventas.csv")
    a = pearson_a_mano(v.precio, v.unidades); s = todas(v.precio, v.unidades)
    assert abs(a["r"] - s["r"]) < 1e-12 and abs(a["p"] - s["p_r"]) < 1e-12
    zr, se, lo, hi = fisher_ic(a["r"], a["n"])
    r_pp = float(stats.pearsonr(v.precio, v.publicidad).statistic)
    r_up = float(stats.pearsonr(v.unidades, v.publicidad).statistic)
    rp = parcial(a["r"], r_pp, r_up)
    sw_x, sw_y = stats.shapiro(v.precio), stats.shapiro(v.unidades)
    R["caso"] = {**a, **s, "r2": a["r"] ** 2, "ic": (lo, hi), "crit_t": float(stats.t.ppf(0.975, 28)),
                 "r_pp": r_pp, "r_up": r_up, "r_parcial": rp, "sw_x": float(sw_x.pvalue), "sw_y": float(sw_y.pvalue),
                 "precio_min": float(v.precio.min()), "precio_max": float(v.precio.max()),
                 "u_min": int(v.unidades.min()), "u_max": int(v.unidades.max()),
                 "r_tend": float(stats.pearsonr(v.semana, v.precio).statistic),
                 "p_tend": float(stats.pearsonr(v.semana, v.precio).pvalue)}
    return R


# ---------------------------------------------------------------- CSV, figuras y cuaderno

def escribir_csv():
    pd.DataFrame({"temperatura": EJ_T, "vasos": EJ_V}).to_csv(DATOS / "u06_mote.csv", index=False)


def estilo(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(SUAVE)
    ax.tick_params(colors=SUAVE, labelsize=9)
    ax.grid(color=LINEA, lw=0.6); ax.set_axisbelow(True)


def puntos(ax, x, y):
    ax.plot(x, y, "o", ms=7, mfc=TINTA, mec="white", mew=1.2)


def figuras(R):
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "path", "axes.titlesize": 10})
    # 1 · ejemplo
    fig, ax = plt.subplots(figsize=(6.0, 3.3))
    ax.axvline(np.mean(EJ_T), color=LINEA, lw=1.2, ls="--"); ax.axhline(np.mean(EJ_V), color=LINEA, lw=1.2, ls="--")
    puntos(ax, EJ_T, EJ_V)
    ax.text(34.6, 60, "cuadrantes II y IV:\naportan negativo", color=SUAVE, fontsize=8, ha="right")
    ax.text(21.2, 99, "con las medias como ejes,\nlos 8 puntos caen en\nlos cuadrantes I y III", color=SUAVE, fontsize=8, va="top")
    ax.set_xlabel("temperatura máxima (°C)", color=SUAVE); ax.set_ylabel("vasos vendidos", color=SUAVE)
    estilo(ax); fig.tight_layout(); fig.savefig(FIG / "u06_ejemplo_dispersion.svg"); plt.close(fig)
    # 2 · cuatro patrones (los datos de 6.5, 6.6, 6.7 y el ejemplo), sin cifras: se calculan en la práctica
    fig, axs = plt.subplots(1, 4, figsize=(7.2, 2.2))
    for ax, (x, y, t) in zip(axs, [(EJ_T, EJ_V, "recta con ruido"), (E6_X, E6_Y, "curva que siempre sube"),
                                    (E5_X, E5_Y, "un punto lejano"), (E7_X, E7_Y, "forma de U")]):
        ax.plot(x, y, "o", ms=4.5, mfc=TINTA, mec="white", mew=0.8)
        ax.set_title(t, color=TINTA); ax.set_xticks([]); ax.set_yticks([]); estilo(ax)
    fig.tight_layout(); fig.savefig(FIG / "u06_cuatro_patrones.svg"); plt.close(fig)
    # 3 · caso
    v = pd.read_csv(DATOS / "ventas.csv")
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    puntos(ax, v.precio, v.unidades)
    ax.set_xlabel("precio de la polera ($)", color=SUAVE); ax.set_ylabel("unidades vendidas en la semana", color=SUAVE)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: fmt(x, 0)))
    estilo(ax); fig.tight_layout(); fig.savefig(FIG / "u06_caso_dispersion.svg"); plt.close(fig)


def ejecutar_cuaderno():
    nb = json.loads((NB / "u06_correlacion.ipynb").read_text(encoding="utf-8"))
    codigo = "\n\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    previo = os.getcwd(); os.chdir(NB)
    try:
        warnings.filterwarnings("ignore", message=".*non-interactive.*")
        ns = {"__name__": "__cuaderno__"}
        exec(compile(codigo, "u06_correlacion.ipynb", "exec"), ns)
    finally:
        os.chdir(previo); plt.close("all")
    return ns["RES"]


def comparar_cuaderno(R, C):
    e, c = R["ej"], R["caso"]
    pares = {"ej_r": e["r"], "ej_p": e["p"], "ej_rho": e["rho"], "ej_tau": e["tau"],
             "caso_r": c["r"], "caso_p": c["p_r"], "caso_rho": c["rho"], "caso_p_rho": c["p_rho"],
             "caso_tau": c["tau"], "caso_cov": c["cov"], "caso_r_parcial": c["r_parcial"]}
    malos = [k for k, v in pares.items() if k not in C or abs(C[k] - v) > 1e-9 * max(1, abs(v))]
    print("CUADERNO:", "OK, reproduce el ejemplo y el caso" if not malos else f"NO calza en {malos}")
    return not malos


def cadena(R):
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_datos.py")
    caso = importlib.util.module_from_spec(spec); spec.loader.exec_module(caso)
    D = {k: pd.read_csv(DATOS / f"{k}.csv") for k in ("registro", "defectos", "reclamos_canal", "llegadas",
                                                      "ventas", "secado", "lotes", "reclamos_dia")}
    C = caso.calcular(D)
    G = caso.generar()
    assert np.allclose(G["ventas"][["precio", "publicidad", "unidades"]].values,
                       D["ventas"][["precio", "publicidad", "unidades"]].values)
    u6, c = C["u6"], R["caso"]
    ok = all(abs(u6[k] - c[v]) < 1e-12 for k, v in
             (("pearson_r", "r"), ("pearson_p", "p_r"), ("spearman_rho", "rho"), ("spearman_p", "p_rho")))
    R["u5_media"] = C["u5"]["media"]
    print("CADENA:", "OK, la pieza del caso calza con caso_estampa_sur_datos.py" if ok else "NO calza")
    return ok


# ---------------------------------------------------------------- impresión y revisión

def imprimir(R):
    e = R["ej"]
    print("== Ejemplo")
    for x, y, dx, dy in zip(EJ_T, EJ_V, e["dx"], e["dy"]):
        print(f"   {x} {y} dx {fmt(dx, 0)} dy {fmt(dy, 0)} dxdy {fmt(dx * dy, 0)} dx² {fmt(dx ** 2, 0)} dy² {fmt(dy ** 2, 0)}")
    print(f"   medias {fmt(e['mx'], 0)} {fmt(e['my'], 0)} Sxy {fmt(e['sxy'], 0)} Sxx {fmt(e['sxx'], 0)} Syy {fmt(e['syy'], 0)} cov {fmt(e['cov'], 2)} sx {fmt(e['sx'], 3)} sy {fmt(e['sy'], 3)}")
    print(f"   r {fmt(e['r'], 4)} r² {pct(e['r2'], 1)} t {fmt(e['t'], 2)} crit {fmt(e['crit_t'], 3)} {pval(e['p'], 4)} | IC {fmt(e['ic'][0], 3)} a {fmt(e['ic'][1], 3)} z {fmt(e['zr'], 4)} se {fmt(e['se'], 4)}")
    print(f"   rangos vasos {list(e['rv'])} Σd² {e['d2']} ρ {fmt(e['rho'], 3)} {pval(e['p_rho'], 4)} | C {e['C']} D {e['D']} τ {fmt(e['tau'], 3)} {pval(e['p_tau'], 4)}")
    a = R["e1"]; print(f"== 6.1 medias {fmt(a['mx'], 0)} {fmt(a['my'], 0)} Sxy {fmt(a['sxy'], 0)} Sxx {fmt(a['sxx'], 0)} Syy {fmt(a['syy'], 0)} cov {fmt(a['cov'], 1)} r {fmt(a['r'], 3)} t {fmt(a['t'], 2)} {pval(a['p'])}")
    a = R["e2"]; print(f"== 6.2 n25 t {fmt(a['t25'], 2)} crit {fmt(a['c25'], 3)} p {fmt(a['p25'], 3)} | n100 t {fmt(a['t100'], 2)} crit {fmt(a['c100'], 3)} {pval(a['p100'], 4)} | r² {pct(a['r2'], 1)} rmin {fmt(a['rmin'], 3)}")
    a = R["e3"]; print(f"== 6.3 Σd² {a['d2']} ρ {fmt(a['rho'], 3)} p {fmt(a['p_rho'], 3)} | C {a['C']} D {a['D']} τ {fmt(a['tau'], 3)} p {fmt(a['p_tau'], 3)}")
    a = R["e4"]; print(f"== 6.4 cov {fmt(a['cov'], 2)} r {fmt(a['r'], 4)} °F {[fmt(v, 1) for v in a['tf']]} cov_f {fmt(a['cov_f'], 2)} cov_fMJ {fmt(a['cov_fmj'], 2)}")
    a = R["e5"]; print("== 6.5", {k: fmt(v, 3) for k, v in a["con"].items()}, {k: fmt(v, 3) for k, v in a["sin"].items()})
    a = R["e6"]; print("== 6.6", {k: fmt(v, 4) for k, v in a.items()})
    a = R["e7"]; print("== 6.7", {k: fmt(v, 3) for k, v in a.items()})
    a = R["e8"]; print("== 6.8", {k: fmt(v, 4) for k, v in a.items()})
    a = R["e9"]; print(f"== 6.9 z1 {fmt(a['z1'], 4)} se {fmt(a['se1'], 4)} IC {fmt(a['ic'][0], 3)} a {fmt(a['ic'][1], 3)} zt {fmt(a['zt'], 2)} p {fmt(a['pt'], 3)} | z2 {fmt(a['z2'], 4)} zdif {fmt(a['zdif'], 2)} p {fmt(a['pdif'], 3)}")
    a = R["e10"]; print(f"== 6.10 pares {a['pares']} esperados {fmt(a['esperados'], 2)} sig {a['sig']} bonf {fmt(a['bonf'], 5)} sig_bonf {a['sig_bonf']} rmax {fmt(a['rmax'], 3)} rcrit {fmt(a['rcrit'], 3)}")
    c = R["caso"]
    print(f"== Caso medias {fmt(c['mx'], 1)} {fmt(c['my'], 2)} sx {fmt(c['sx'], 1)} sy {fmt(c['sy'], 2)} cov {fmt(c['cov'], 0)} r {fmt(c['r'], 3)} r² {pct(c['r2'], 1)} t {fmt(c['t'], 2)} crit {fmt(c['crit_t'], 3)} {pval(c['p_r'])} ({c['p_r']:.6f})")
    print(f"   IC {fmt(c['ic'][0], 3)} a {fmt(c['ic'][1], 3)} | ρ {fmt(c['rho'], 3)} {pval(c['p_rho'])} | τ {fmt(c['tau'], 3)} {pval(c['p_tau'])}")
    print(f"   r(precio, publicidad) {fmt(c['r_pp'], 3)} r(unidades, publicidad) {fmt(c['r_up'], 3)} parcial {fmt(c['r_parcial'], 3)} | Shapiro p {fmt(c['sw_x'], 3)} {fmt(c['sw_y'], 3)}")
    print(f"   precio {fmt(c['precio_min'], 0)} a {fmt(c['precio_max'], 0)} unidades {c['u_min']} a {c['u_max']} | U5 media {fmt(R['u5_media'], 2)}")


def fila(*celdas):
    return "| " + " | ".join(celdas) + " |"


def esperados(R):
    e = []
    a = R["ej"]
    for x, y, dx, dy in zip(EJ_T, EJ_V, a["dx"], a["dy"]):
        e.append(fila(str(x), str(y), fmt(dx, 0), fmt(dy, 0), fmt(dx * dy, 0), fmt(dx ** 2, 0), fmt(dy ** 2, 0)))
    e += [fmt(a["sxy"], 0), fmt(a["sxx"], 0), fmt(a["syy"], 0), fmt(a["cov"], 2), fmt(a["r"], 4), pct(a["r2"], 1),
          fmt(a["t"], 2), fmt(a["crit_t"], 3), pval(a["p"]), fmt(a["ic"][0], 3), fmt(a["ic"][1], 3), fmt(a["rho"], 3),
          fmt(a["tau"], 3), f"Σd² = {int(a['d2'])}", f"{a['C']} pares concordantes", f"{a['D']} discordantes",
          fmt(a["zr"], 4), fmt(a["se"], 4)]
    a = R["e1"]
    e += [fmt(a["sxy"], 0), fmt(a["sxx"], 0), fmt(a["syy"], 0), fmt(a["cov"], 1), fmt(a["r"], 3), fmt(a["t"], 2), pval(a["p"])]
    a = R["e2"]
    e += [fmt(a["t25"], 2), fmt(a["c25"], 3), "p = " + fmt(a["p25"], 3), fmt(a["t100"], 2), fmt(a["c100"], 3), pval(a["p100"], 4),
          pct(a["r2"], 1), fmt(a["rmin"], 3)]
    a = R["e3"]
    e += [f"Σd² = {int(a['d2'])}", fmt(a["rho"], 3), "p = " + fmt(a["p_rho"], 3), fmt(a["tau"], 3), "p = " + fmt(a["p_tau"], 3),
          f"{a['C']} concordantes y {a['D']} discordantes"]
    a = R["e4"]
    e += [fmt(a["cov"], 2), fmt(a["r"], 4), fmt(a["cov_f"], 2), fmt(a["cov_fmj"], 2)]
    for k in ("con", "sin"):
        t = R["e5"][k]; e += [fmt(t["r"], 3), fmt(t["rho"], 3), fmt(t["tau"], 3)]
    a = R["e6"]; e += [fmt(a["r"], 3), fmt(a["rho"], 3), fmt(a["tau"], 3), fmt(a["r_log"], 4)]
    a = R["e7"]; e += [fmt(a["r"], 3), fmt(a["rho"], 3), fmt(a["r_izq"], 3), fmt(a["r_der"], 3), "p = " + fmt(a["p_r"], 2)]
    a = R["e8"]; e += [fmt(a["rxy"], 3), fmt(a["rxz"], 3), fmt(a["ryz"], 3), fmt(a["rp"], 3), fmt(a["tp"], 2), "p = " + fmt(a["pp"], 2), pval(a["p_xy"])]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
             "noviembre", "diciembre"]
    e += [fila(m, str(z), str(x), str(y)) for m, z, x, y in zip(meses, E8_Z, E8_X, E8_Y)]
    a = R["e9"]; e += [fmt(a["z1"], 4), fmt(a["se1"], 4), fmt(a["ic"][0], 3), fmt(a["ic"][1], 3), fmt(a["zt"], 2), "p = " + fmt(a["pt"], 3),
                       fmt(a["z2"], 4), fmt(a["zdif"], 2), "p = " + fmt(a["pdif"], 3)]
    a = R["e10"]; e += [f"{a['pares']} pares", fmt(a["esperados"], 2), f"{a['sig']} de los {a['pares']}", fmt(a["bonf"], 5),
                        fmt(a["rmax"], 3), fmt(a["rcrit"], 3), f"semilla {E10_SEMILLA}"]
    c = R["caso"]
    e += [fmt(c["mx"], 1), fmt(c["my"], 2), fmt(c["sx"], 1), fmt(c["sy"], 2), fmt(c["cov"], 0), fmt(c["r"], 3), pct(c["r2"], 1),
          fmt(c["t"], 2), fmt(c["crit_t"], 3), pval(c["p_r"]), fmt(c["ic"][0], 3), fmt(c["ic"][1], 3), fmt(c["rho"], 3), fmt(c["tau"], 3),
          fmt(c["r_pp"], 3), fmt(c["r_up"], 3), fmt(c["r_parcial"], 3), "p = " + fmt(c["sw_x"], 2), "p = " + fmt(c["sw_y"], 2),
          "$" + fmt(c["precio_min"], 0), fmt(c["r_tend"], 2), "p = " + fmt(c["p_tend"], 2), "$" + fmt(c["precio_max"], 0), f"{c['u_min']} y {c['u_max']}", fmt(R["u5_media"], 2)]
    # razones intermedias escritas en las pautas
    a3 = R["e3"]; n3 = len(E3_A)
    e += [fmt(E2_R ** 2, 4), f"{a3['C'] - a3['D']}/{a3['pares']}", f"{6 * int(a3['d2'])}/{n3 * (n3 ** 2 - 1)}",
          f"1/{E9_N1 - 3} + 1/{E9_N2 - 3}", fmt(R["e9"]["ic"][1] - R["e9"]["ic"][0], 1) + " de ancho",
          pct(1 - c["r2"], 0) + " restante", f"{sum(EJ_T)}/8 = {fmt(np.mean(EJ_T), 0)}", f"{sum(EJ_V)}/8 = {fmt(np.mean(EJ_V), 0)}"]
    return e


if __name__ == "__main__":
    R = resultados()
    escribir_csv()
    figuras(R)
    ok = cadena(R)
    imprimir(R)
    ok = comparar_cuaderno(R, ejecutar_cuaderno()) and ok
    if not ok:
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8").replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
