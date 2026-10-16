"""Unidad 5 · Bondad de ajuste y normalidad.

Recalcula todas las cifras de la unidad desde los datos (a mano, con la fórmula, y con scipy o
statsmodels; las dos tienen que coincidir), deja los CSV del ejemplo en datos/u05_*.csv, dibuja las
figuras en unidades/figuras/, ejecuta el cuaderno notebooks/u05_bondad_de_ajuste.ipynb y compara sus
resultados, y comprueba la pieza del caso contra caso_estampa_sur_datos.py.

    python u05_bondad_de_ajuste.py            # imprime los resultados
    python u05_bondad_de_ajuste.py --revisar  # además busca cada cifra en el .md
"""
from math import exp, log, sqrt
from pathlib import Path
import importlib.util, json, os, sys, warnings

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import lilliefors
from statsmodels.stats._lilliefors import pval_lf

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore", category=FutureWarning)

AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
DATOS, FIG, NB = RAMO / "datos", RAMO / "unidades" / "figuras", RAMO / "notebooks"
MD = RAMO / "unidades" / "05-bondad-de-ajuste.md"

TINTA, SUAVE, LINEA, ACENTO = "#2B2F33", "#5F656B", "#D6D3CE", "#E2622A"


# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def pval(p, dec=3):
    return "p < 0,001" if p < 0.001 else "p = " + fmt(p, dec)


def chi2_gof(obs, esp):
    obs, esp = np.asarray(obs, float), np.asarray(esp, float)
    return float(((obs - esp) ** 2 / esp).sum())


def ks_a_mano(x, F):
    """D+ y D- para cada dato ordenado, con F la distribución acumulada de H0."""
    x = np.sort(np.asarray(x, float)); n = len(x)
    Fi = np.array([F(v) for v in x])
    i = np.arange(1, n + 1)
    dmas, dmenos = i / n - Fi, Fi - (i - 1) / n
    return {"x": x, "F": Fi, "dmas": dmas, "dmenos": dmenos, "D": float(max(dmas.max(), dmenos.max()))}


def ad_a_mano(x, F):
    """Estadístico de Anderson-Darling: A² = -n - (1/n) Σ (2i-1)[ln F(x_i) + ln(1 - F(x_{n+1-i}))]."""
    x = np.sort(np.asarray(x, float)); n = len(x)
    Fi = np.array([F(v) for v in x])
    i = np.arange(1, n + 1)
    terminos = (2 * i - 1) * (np.log(Fi) + np.log(1 - Fi[::-1]))
    return {"F": Fi, "terminos": terminos, "A2": float(-n - terminos.sum() / n)}


def poisson_clases(valores, frec, ultima):
    """Frecuencias esperadas de Poisson con lambda estimado; la última clase es «ultima o más»."""
    valores, frec = np.asarray(valores), np.asarray(frec)
    n = frec.sum(); lam = (valores * frec).sum() / n
    p = [stats.poisson.pmf(k, lam) for k in range(ultima)] + [stats.poisson.sf(ultima - 1, lam)]
    obs = [frec[valores == k].sum() for k in range(ultima)] + [frec[valores >= ultima].sum()]
    return lam, np.array(obs), n * np.array(p)


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base; pasados por herramientas/colisiones.py.

# Ejemplo · pizzería: llamadas por intervalo de 15 minutos (120 intervalos de un mes de viernes)
EJ_LLAM_K = [0, 1, 2, 3, 4, 5, 6]
EJ_LLAM_F = [27, 36, 30, 17, 6, 3, 1]
# Ejemplo · 10 tiempos entre llamadas (min); la central dice que el promedio histórico es 9 min
EJ_TIEMPOS = [2.1, 3.4, 4.8, 6.0, 7.7, 9.5, 12.3, 15.0, 19.6, 26.2]
EJ_MEDIA_H0 = 9.0

# 5.1 · grados de libertad (clases finales, parámetros estimados)
E1 = {"a": (6, 0), "b": (6, 1), "c": (8, 2), "d": (5, 0)}

# 5.2 · boletas por día en una ferretería de Los Ángeles (lunes a sábado)
E2 = [58, 44, 41, 47, 52, 68]

# 5.3 · peso de 6 bolsas de harina (g); el envasador declara N(1.000; 8²)
E3 = [991, 1004, 996, 1013, 1000, 1009]
E3_MU, E3_SIGMA = 1000, 8

# 5.4 · largo de 6 pernos (mm) para un Q-Q normal
E4 = [49.2, 49.8, 50.0, 50.1, 50.4, 51.9]

# 5.5 · fallas por rollo de tela en 100 rollos
E5_K = [0, 1, 2, 3, 4, 5]
E5_F = [40, 26, 15, 10, 5, 4]

# 5.6 · frascos defectuosos por caja de 4, en 150 cajas
E6_K = [0, 1, 2, 3, 4]
E6_F = [96, 42, 10, 2, 0]

# 5.7 · peso de 200 paquetes de café (g) en clases; media 250,1 g y desviación 2,9 g de los datos
E7_BORDES = [-np.inf, 246, 248, 250, 252, 254, np.inf]
E7_F = [18, 27, 52, 49, 37, 17]
E7_MEDIA, E7_S = 250.1, 2.9

# 5.8 · KS contra una normal con media y desviación estimadas
E8_N, E8_D = 50, 0.152

# 5.9 · 5 tiempos de reparación (h); H0: exponencial de media 4 h (especificada)
E9 = [0.6, 1.9, 3.1, 5.2, 11.8]
E9_MEDIA = 4.0
E9_COLA = 24.0     # (b) el último tiempo pasa de 11,8 a 24 h
AD_CRIT_5 = 2.492   # A² al 5 % con la distribución completamente especificada (Stephens)

# 5.10 · simulación: KS con parámetros estimados en muestras normales
E10_SEMILLA, E10_REP, E10_N = 505, 5000, 30


# ---------------------------------------------------------------- resultados

def caso_datos():
    return pd.read_csv(DATOS / "llegadas.csv").minutos


CASO_BORDES = [0, 10, 20, 30, 45, 60, np.inf]


def resultados():
    R = {}
    # ---- ejemplo A · chi-cuadrado Poisson
    lam, obs, esp = poisson_clases(np.array(EJ_LLAM_K), np.array(EJ_LLAM_F), 5)
    R["ej_lambda"], R["ej_obs7"], R["ej_esp7"] = lam, obs, esp       # clases 0,1,2,3,4,≥5
    obs4 = np.r_[obs[:4], obs[4:].sum()]; esp4 = np.r_[esp[:4], esp[4:].sum()]
    chi = chi2_gof(obs4, esp4); gl = len(obs4) - 1 - 1
    R["ej_obs"], R["ej_esp"], R["ej_contrib"] = obs4, esp4, (obs4 - esp4) ** 2 / esp4
    R["ej_chi2"], R["ej_gl"], R["ej_p"] = chi, gl, float(stats.chi2.sf(chi, gl))
    R["ej_crit"] = float(stats.chi2.ppf(0.95, gl))
    sp = stats.chisquare(obs4, esp4, ddof=1)
    assert abs(sp.statistic - chi) < 1e-9 and abs(sp.pvalue - R["ej_p"]) < 1e-12
    R["ej_media_tiempo_poisson"] = 15 / lam
    # ---- ejemplo B · KS a mano contra exponencial de media 9
    F0 = lambda v: 1 - exp(-v / EJ_MEDIA_H0)
    ks = ks_a_mano(EJ_TIEMPOS, F0)
    sks = stats.kstest(EJ_TIEMPOS, "expon", args=(0, EJ_MEDIA_H0))
    assert abs(sks.statistic - ks["D"]) < 1e-12
    R["ej_ks"], R["ej_ks_p"] = ks, float(sks.pvalue)
    R["ej_ks_crit"] = float(stats.kstwo.ppf(0.95, len(EJ_TIEMPOS)))
    R["ej_media_t"] = float(np.mean(EJ_TIEMPOS))
    sh = stats.shapiro(EJ_TIEMPOS)
    R["ej_sh_W"], R["ej_sh_p"] = float(sh.statistic), float(sh.pvalue)
    ad = ad_a_mano(EJ_TIEMPOS, F0)
    R["ej_ad"] = ad["A2"]

    # ---- 5.1
    R["e1"] = {k: (c - 1 - p, float(stats.chi2.ppf(0.95, c - 1 - p))) for k, (c, p) in E1.items()}

    # ---- 5.2
    e = np.full(6, sum(E2) / 6)
    chi = chi2_gof(E2, e)
    R["e2"] = {"n": sum(E2), "e": e[0], "contrib": (np.array(E2) - e) ** 2 / e, "chi2": chi,
               "p": float(stats.chi2.sf(chi, 5)), "crit": float(stats.chi2.ppf(0.95, 5))}
    assert abs(stats.chisquare(E2).statistic - chi) < 1e-9

    # ---- 5.3
    ks3 = ks_a_mano(E3, lambda v: stats.norm.cdf(v, E3_MU, E3_SIGMA))
    s3 = stats.kstest(E3, stats.norm(E3_MU, E3_SIGMA).cdf)
    assert abs(s3.statistic - ks3["D"]) < 1e-12
    R["e3"] = {**ks3, "p": float(s3.pvalue), "crit": float(stats.kstwo.ppf(0.95, len(E3)))}

    # ---- 5.4 · Q-Q con posiciones de Blom
    n4 = len(E4); i = np.arange(1, n4 + 1)
    pos = (i - 0.375) / (n4 + 0.25); z = stats.norm.ppf(pos)
    r_qq = float(np.corrcoef(np.sort(E4), z)[0, 1])
    r_qq5 = float(np.corrcoef(np.sort(E4)[:-1], stats.norm.ppf((np.arange(1, n4) - 0.375) / (n4 - 1 + 0.25)))[0, 1])
    sh4 = stats.shapiro(E4)
    R["e4"] = {"pos": pos, "z": z, "r_qq": r_qq, "r_qq_sin": r_qq5, "W": float(sh4.statistic), "p": float(sh4.pvalue)}

    # ---- 5.5 · Poisson con sobredispersión
    lam5, obs5, esp5 = poisson_clases(np.array(E5_K), np.array(E5_F), 3)
    chi5 = chi2_gof(obs5, esp5)
    k5 = np.repeat(E5_K, E5_F)
    R["e5"] = {"lam": lam5, "obs": obs5, "esp": esp5, "contrib": (obs5 - esp5) ** 2 / esp5,
               "chi2": chi5, "gl": len(obs5) - 2, "p": float(stats.chi2.sf(chi5, len(obs5) - 2)),
               "crit": float(stats.chi2.ppf(0.95, len(obs5) - 2)), "var": float(np.var(k5, ddof=1)),
               "esp_todas": 100 * np.array([stats.poisson.pmf(k, lam5) for k in range(5)] + [stats.poisson.sf(4, lam5)])}

    # ---- 5.6 · binomial con p estimado
    k6, f6 = np.array(E6_K), np.array(E6_F)
    n6 = f6.sum(); p6 = (k6 * f6).sum() / (4 * n6)
    pr = stats.binom.pmf(np.arange(5), 4, p6)
    esp6_todas = n6 * pr
    obs6 = np.r_[f6[:2], f6[2:].sum()]; esp6 = np.r_[esp6_todas[:2], esp6_todas[2:].sum()]
    chi6 = chi2_gof(obs6, esp6)
    R["e6"] = {"p_hat": p6, "esp_todas": esp6_todas, "obs": obs6, "esp": esp6, "chi2": chi6, "gl": 1,
               "p": float(stats.chi2.sf(chi6, 1)), "crit": float(stats.chi2.ppf(0.95, 1)),
               "contrib": (obs6 - esp6) ** 2 / esp6}

    # ---- 5.7 · normal con media y desviación estimadas
    pr7 = np.diff(stats.norm.cdf(E7_BORDES, E7_MEDIA, E7_S))
    esp7 = sum(E7_F) * pr7
    chi7 = chi2_gof(E7_F, esp7)
    R["e7"] = {"pr": pr7, "esp": esp7, "contrib": (np.array(E7_F) - esp7) ** 2 / esp7, "chi2": chi7, "gl": 3,
               "p": float(stats.chi2.sf(chi7, 3)), "crit": float(stats.chi2.ppf(0.95, 3))}

    # ---- 5.8 · KS clásico frente a Lilliefors
    R["e8"] = {"crit_ks": 1.36 / sqrt(E8_N), "crit_lf": 0.886 / sqrt(E8_N),
               "p_ks": float(stats.kstwo.sf(E8_D, E8_N)), "p_lf": float(pval_lf(E8_D, E8_N))}

    # ---- 5.9 · Anderson-Darling a mano
    F9 = lambda v: 1 - exp(-v / E9_MEDIA)
    ad9 = ad_a_mano(E9, F9); ks9 = ks_a_mano(E9, F9)
    s9 = stats.kstest(E9, "expon", args=(0, E9_MEDIA))
    assert abs(s9.statistic - ks9["D"]) < 1e-12
    # segundo camino: la integral de Anderson-Darling por la fórmula de cómputo de scipy (goodness_of_fit)
    gof = stats.goodness_of_fit(stats.expon, E9, known_params={"loc": 0, "scale": E9_MEDIA},
                                statistic="ad", n_mc_samples=2000, rng=np.random.default_rng(9))
    assert abs(gof.statistic - ad9["A2"]) < 1e-9
    # valor crítico de A² al 5 % con F0 especificada (tabla de Stephens, asintótico 2,492): se comprueba
    # simulando 20.000 muestras de 5 uniformes, porque F0(X) es uniforme bajo H0
    u = np.sort(np.random.default_rng(59).uniform(size=(20000, 5)), axis=1)
    j = np.arange(1, 6)
    a2 = -5 - ((2 * j - 1) * (np.log(u) + np.log(1 - u[:, ::-1]))).sum(axis=1) / 5
    assert abs(np.quantile(a2, 0.95) - AD_CRIT_5) < 0.08, np.quantile(a2, 0.95)
    R["e9"] = {"ad": ad9, "ks": ks9, "p_ks": float(s9.pvalue), "p_ad": float(gof.pvalue),
               "crit_ks": float(stats.kstwo.ppf(0.95, 5))}
    E9b = E9[:-1] + [E9_COLA]
    R["e9b"] = {"A2": ad_a_mano(E9b, F9)["A2"], "D": ks_a_mano(E9b, F9)["D"], "F": 1 - exp(-E9_COLA / E9_MEDIA)}

    # ---- 5.10 · simulación
    rng = np.random.default_rng(E10_SEMILLA)
    D = np.empty(E10_REP)
    for j in range(E10_REP):
        m = rng.normal(0, 1, E10_N)
        D[j] = stats.kstest(m, stats.norm(m.mean(), m.std(ddof=1)).cdf).statistic
    crit_ks30 = float(stats.kstwo.ppf(0.95, E10_N))
    R["e10"] = {"p95": float(np.quantile(D, 0.95)), "media": float(D.mean()),
                "frac_ks": float((D > crit_ks30).mean()), "n_ks": int((D > crit_ks30).sum()), "crit_ks": crit_ks30,
                "frac_lf": float((D > 0.886 / sqrt(E10_N)).mean()),
                "crit_lf": 0.886 / sqrt(E10_N)}

    # ---- caso · tiempos entre llegadas de pedidos web
    x = caso_datos(); n = len(x); media = float(x.mean())
    ks = stats.kstest(x, "expon", args=(0, media))
    lf = lilliefors(x, dist="exp")
    pr = np.diff(stats.expon.cdf(CASO_BORDES, scale=media))
    obs = np.histogram(x, bins=CASO_BORDES)[0]
    esp = n * pr
    chi = chi2_gof(obs, esp)
    ad = ad_a_mano(x, lambda v: 1 - exp(-v / media))
    sad = stats.anderson(x, dist="expon", method="interpolate")
    assert abs(sad.statistic - ad["A2"]) < 1e-9
    crit_ad = stats.anderson(x, dist="expon").critical_values  # 15, 10, 5, 2,5 y 1 %
    sh = stats.shapiro(x)
    R["caso"] = {"n": n, "media": media, "s": float(x.std(ddof=1)), "mediana": float(x.median()),
                 "min": float(x.min()), "max": float(x.max()),
                 "ks_D": float(ks.statistic), "ks_p": float(ks.pvalue),
                 "lf_D": float(lf[0]), "lf_p": float(lf[1]),
                 "obs": obs, "esp": esp, "contrib": (obs - esp) ** 2 / esp, "chi2": chi, "gl": len(obs) - 2,
                 "chi_p": float(stats.chi2.sf(chi, len(obs) - 2)), "chi_crit": float(stats.chi2.ppf(0.95, len(obs) - 2)),
                 "ad": ad["A2"], "ad_p": float(sad.pvalue), "ad_crit5": float(crit_ad[2]),
                 "sh_W": float(sh.statistic), "sh_p": float(sh.pvalue),
                 "lambda_hora": 60 / media, "p_mas_60": exp(-60 / media), "cv": float(x.std(ddof=1)) / media}
    return R


# ---------------------------------------------------------------- CSV del ejemplo, figuras y cuaderno

def escribir_csv():
    pd.DataFrame({"llamadas": EJ_LLAM_K, "intervalos": EJ_LLAM_F}).to_csv(DATOS / "u05_pizzeria_llamadas.csv", index=False)
    pd.DataFrame({"minutos": EJ_TIEMPOS}).to_csv(DATOS / "u05_pizzeria_tiempos.csv", index=False)


def estilo(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(SUAVE)
    ax.tick_params(colors=SUAVE, labelsize=9)
    ax.grid(color=LINEA, lw=0.6); ax.set_axisbelow(True)


def figuras(R):
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "path", "axes.titlesize": 10.5})
    # 1 · ejemplo: distribución empírica frente a la exponencial de media 9
    ks = R["ej_ks"]; x = ks["x"]; n = len(x)
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    grid = np.linspace(0, 30, 300)
    ax.plot(grid, 1 - np.exp(-grid / EJ_MEDIA_H0), color=ACENTO, lw=2, label="exponencial de media 9 min ($H_0$)")
    ax.step(np.r_[0, x, 30], np.r_[0, np.arange(1, n + 1) / n, 1], where="post", color=TINTA, lw=2, label="distribución empírica")
    j = int(np.argmax(np.maximum(ks["dmas"], ks["dmenos"])))
    alto = (j + 1) / n if ks["dmas"][j] >= ks["dmenos"][j] else j / n
    ax.annotate("", xy=(x[j], ks["F"][j]), xytext=(x[j], alto), arrowprops=dict(arrowstyle="<->", color=TINTA, lw=1.2))
    ax.text(x[j] + 0.6, (ks["F"][j] + alto) / 2, f"D = {fmt(ks['D'], 3)}", color=TINTA, fontsize=9, va="center")
    ax.set_xlabel("minutos entre llamadas", color=SUAVE); ax.set_ylabel("proporción acumulada", color=SUAVE)
    ax.set_xlim(0, 30); ax.set_ylim(0, 1.02); estilo(ax); ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    fig.tight_layout(); fig.savefig(FIG / "u05_ejemplo_ks.svg"); plt.close(fig)

    # 2 · caso: histograma con la densidad exponencial ajustada
    c = R["caso"]; xc = np.sort(caso_datos().values); m = c["media"]
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    ax.hist(xc, bins=np.arange(0, 130, 10), density=True, color=SUAVE, alpha=0.55, edgecolor="white", lw=2, label="120 tiempos")
    g = np.linspace(0, 125, 300)
    ax.plot(g, np.exp(-g / m) / m, color=ACENTO, lw=2, label=f"exponencial de media {fmt(m, 2)} min")
    ax.set_xlabel("minutos entre pedidos web", color=SUAVE); ax.set_ylabel("densidad", color=SUAVE)
    estilo(ax); ax.legend(frameon=False, fontsize=8.5)
    fig.tight_layout(); fig.savefig(FIG / "u05_caso_histograma.svg"); plt.close(fig)

    # 3 · caso: Q-Q contra la exponencial y contra la normal
    nn = len(xc); pos = (np.arange(1, nn + 1) - 0.5) / nn
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 3.3))
    qe = stats.expon.ppf(pos, scale=m)
    axs[0].plot([0, 125], [0, 125], color=ACENTO, lw=1.6)
    axs[0].plot(qe, xc, "o", ms=4, mfc=TINTA, mec="white", mew=0.6)
    axs[0].set_title("contra la exponencial", color=TINTA); axs[0].set_xlabel("cuantil teórico (min)", color=SUAVE)
    axs[0].set_ylabel("dato ordenado (min)", color=SUAVE)
    qn = stats.norm.ppf(pos, loc=m, scale=c["s"])
    axs[1].plot([-50, 125], [-50, 125], color=ACENTO, lw=1.6)
    axs[1].plot(qn, xc, "o", ms=4, mfc=TINTA, mec="white", mew=0.6)
    axs[1].set_title("contra la normal", color=TINTA); axs[1].set_xlabel("cuantil teórico (min)", color=SUAVE)
    for a in axs:
        estilo(a)
    fig.tight_layout(); fig.savefig(FIG / "u05_caso_qq.svg"); plt.close(fig)


def ejecutar_cuaderno():
    """Ejecuta las celdas de código del cuaderno con exec (sin Jupyter) y devuelve su diccionario RES."""
    nb = json.loads((NB / "u05_bondad_de_ajuste.ipynb").read_text(encoding="utf-8"))
    codigo = "\n\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    previo = os.getcwd(); os.chdir(NB)
    try:
        warnings.filterwarnings("ignore", message=".*non-interactive.*")
        ns = {"__name__": "__cuaderno__"}
        exec(compile(codigo, "u05_bondad_de_ajuste.ipynb", "exec"), ns)
    finally:
        os.chdir(previo); plt.close("all")
    return ns["RES"]


def comparar_cuaderno(R, C):
    pares = {"ej_lambda": R["ej_lambda"], "ej_chi2": R["ej_chi2"], "ej_p": R["ej_p"],
             "ej_ks_D": R["ej_ks"]["D"], "ej_ks_p": R["ej_ks_p"], "ej_sh_W": R["ej_sh_W"], "ej_sh_p": R["ej_sh_p"],
             "caso_ks_D": R["caso"]["ks_D"], "caso_ks_p": R["caso"]["ks_p"], "caso_lf_p": R["caso"]["lf_p"],
             "caso_chi2": R["caso"]["chi2"], "caso_chi_p": R["caso"]["chi_p"], "caso_ad": R["caso"]["ad"],
             "caso_sh_W": R["caso"]["sh_W"], "caso_sh_p": R["caso"]["sh_p"]}
    malos = [k for k, v in pares.items() if k not in C or abs(C[k] - v) > 1e-9 * max(1, abs(v))]
    print("CUADERNO:", "OK, reproduce el ejemplo y el caso" if not malos else f"NO calza en {malos}")
    return not malos


def cadena(R):
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_datos.py")
    caso = importlib.util.module_from_spec(spec); spec.loader.exec_module(caso)
    D = {k: pd.read_csv(DATOS / f"{k}.csv") for k in ("registro", "defectos", "reclamos_canal", "llegadas",
                                                      "ventas", "secado", "lotes", "reclamos_dia")}
    C = caso.calcular(D)
    G = caso.generar()   # los CSV tienen que ser los de la semilla del caso
    assert np.allclose(G["llegadas"].minutos.values, D["llegadas"].minutos.values)
    u5, c = C["u5"], R["caso"]
    ok = all(abs(u5[k] - c[v]) < 1e-12 for k, v in
             (("media", "media"), ("ks_D", "ks_D"), ("ks_p", "ks_p"), ("shapiro_W", "sh_W"), ("shapiro_p", "sh_p")))
    R["u4_chi2"], R["u4_p"] = C["u4"]["chi2"], C["u4"]["p"]
    rc = D["reclamos_canal"].set_index("canal")
    R["u4_web"], R["u4_total"] = int(rc.loc["web"].sum()), int(rc.values.sum())
    print("CADENA:", "OK, la pieza del caso calza con caso_estampa_sur_datos.py" if ok else "NO calza")
    return ok


# ---------------------------------------------------------------- impresión y revisión

def imprimir(R):
    print("== Ejemplo A · Poisson")
    print(f"   λ {fmt(R['ej_lambda'], 2)} | obs {list(R['ej_obs'])} | esp {[fmt(v, 2) for v in R['ej_esp']]} | esp7 {[fmt(v, 2) for v in R['ej_esp7']]}")
    print(f"   aportes {[fmt(v, 3) for v in R['ej_contrib']]} | χ² {fmt(R['ej_chi2'], 3)} gl {R['ej_gl']} crit {fmt(R['ej_crit'], 3)} p {fmt(R['ej_p'], 3)} | media entre llamadas {fmt(R['ej_media_tiempo_poisson'], 2)}")
    k = R["ej_ks"]
    print("== Ejemplo B · KS")
    for i, (x, F, a, b) in enumerate(zip(k["x"], k["F"], k["dmas"], k["dmenos"]), 1):
        print(f"   {i}: {fmt(x, 1)} F {fmt(F, 4)} D+ {fmt(a, 4)} D- {fmt(b, 4)}")
    print(f"   D {fmt(k['D'], 4)} crit {fmt(R['ej_ks_crit'], 3)} p {fmt(R['ej_ks_p'], 3)} media {fmt(R['ej_media_t'], 2)} | Shapiro W {fmt(R['ej_sh_W'], 3)} p {fmt(R['ej_sh_p'], 3)} | AD {fmt(R['ej_ad'], 3)}")
    print("== 5.1", {k: (g, fmt(c, 2)) for k, (g, c) in R["e1"].items()})
    e = R["e2"]; print(f"== 5.2 e {fmt(e['e'], 2)} aportes {[fmt(v, 3) for v in e['contrib']]} χ² {fmt(e['chi2'], 2)} crit {fmt(e['crit'], 2)} p {fmt(e['p'], 3)}")
    e = R["e3"]; print(f"== 5.3 F {[fmt(v, 4) for v in e['F']]} D+ {[fmt(v, 4) for v in e['dmas']]} D- {[fmt(v, 4) for v in e['dmenos']]} D {fmt(e['D'], 4)} crit {fmt(e['crit'], 3)} p {fmt(e['p'], 3)}")
    e = R["e4"]; print(f"== 5.4 pos {[fmt(v, 3) for v in e['pos']]} z {[fmt(v, 2) for v in e['z']]} r {fmt(e['r_qq'], 3)} sin {fmt(e['r_qq_sin'], 3)} W {fmt(e['W'], 3)} p {fmt(e['p'], 3)}")
    e = R["e5"]; print(f"== 5.5 λ {fmt(e['lam'], 2)} var {fmt(e['var'], 2)} esp_todas {[fmt(v, 2) for v in e['esp_todas']]} obs {list(e['obs'])} esp {[fmt(v, 2) for v in e['esp']]} aportes {[fmt(v, 2) for v in e['contrib']]} χ² {fmt(e['chi2'], 2)} gl {e['gl']} crit {fmt(e['crit'], 2)} p {fmt(e['p'], 4)}")
    e = R["e6"]; print(f"== 5.6 p̂ {fmt(e['p_hat'], 4)} esp_todas {[fmt(v, 2) for v in e['esp_todas']]} obs {list(e['obs'])} esp {[fmt(v, 2) for v in e['esp']]} aportes {[fmt(v, 3) for v in e['contrib']]} χ² {fmt(e['chi2'], 3)} crit {fmt(e['crit'], 2)} p {fmt(e['p'], 3)}")
    e = R["e7"]; print(f"== 5.7 pr {[fmt(v, 4) for v in e['pr']]} esp {[fmt(v, 2) for v in e['esp']]} aportes {[fmt(v, 3) for v in e['contrib']]} χ² {fmt(e['chi2'], 2)} crit {fmt(e['crit'], 2)} p {fmt(e['p'], 3)}")
    e = R["e8"]; print(f"== 5.8 crit KS {fmt(e['crit_ks'], 3)} crit LF {fmt(e['crit_lf'], 3)} p KS {fmt(e['p_ks'], 3)} p LF {fmt(e['p_lf'], 3)}")
    e = R["e9"]; print(f"== 5.9 F {[fmt(v, 4) for v in e['ad']['F']]} términos {[fmt(v, 3) for v in e['ad']['terminos']]} A² {fmt(e['ad']['A2'], 3)} p AD {fmt(e['p_ad'], 2)} | (b) A² {fmt(R['e9b']['A2'], 3)} D {fmt(R['e9b']['D'], 4)} F {fmt(R['e9b']['F'], 4)} | crit KS {fmt(e['crit_ks'], 3)} D {fmt(e['ks']['D'], 4)} p KS {fmt(e['p_ks'], 3)}")
    e = R["e10"]; print(f"== 5.10 p95 {fmt(e['p95'], 3)} media {fmt(e['media'], 3)} frac>{fmt(e['crit_ks'], 3)} {pct(e['frac_ks'], 2)} ({e['n_ks']}) crit LF {fmt(e['crit_lf'], 3)} frac>LF {pct(e['frac_lf'], 1)}")
    c = R["caso"]
    print(f"== Caso n {c['n']} media {fmt(c['media'], 2)} s {fmt(c['s'], 2)} mediana {fmt(c['mediana'], 1)} min {c['min']} max {c['max']} cv {fmt(c['cv'], 2)}")
    print(f"   KS D {fmt(c['ks_D'], 4)} p {fmt(c['ks_p'], 2)} | Lilliefors p {fmt(c['lf_p'], 2)}")
    print(f"   obs {list(c['obs'])} esp {[fmt(v, 2) for v in c['esp']]} aportes {[fmt(v, 3) for v in c['contrib']]} χ² {fmt(c['chi2'], 2)} gl {c['gl']} crit {fmt(c['chi_crit'], 2)} p {fmt(c['chi_p'], 2)}")
    print(f"   AD {fmt(c['ad'], 3)} crit 5 % {fmt(c['ad_crit5'], 3)} p≥ {fmt(c['ad_p'], 2)} | Shapiro W {fmt(c['sh_W'], 3)} {pval(c['sh_p'])}")
    print(f"   λ por hora {fmt(c['lambda_hora'], 2)} P(>60) {pct(c['p_mas_60'], 1)} | U4 χ² {fmt(R['u4_chi2'], 2)} {pval(R['u4_p'])}")


def fila(*celdas):
    return "| " + " | ".join(celdas) + " |"


def esperados(R):
    e = []
    # ejemplo A
    e += [fila("Intervalos", *map(str, EJ_LLAM_F))]
    e += [fmt(R["ej_lambda"], 2), fmt(R["ej_chi2"], 3), fmt(R["ej_crit"], 3), "p = " + fmt(R["ej_p"], 3),
          fmt(R["ej_media_tiempo_poisson"], 2)]
    e += [fmt(v, 2) for v in R["ej_esp"]] + [fmt(v, 3) for v in R["ej_contrib"]] + [fmt(v, 2) for v in R["ej_esp7"][4:]]
    # ejemplo B
    k = R["ej_ks"]
    for i, (x, F, a, b) in enumerate(zip(k["x"], k["F"], k["dmas"], k["dmenos"]), 1):
        e.append(fila(str(i), fmt(x, 1), fmt(i / 10, 1), fmt(F, 4), fmt(a, 4), fmt(b, 4)))
    e += [fmt(k["D"], 4), fmt(R["ej_ks_crit"], 3), "p = " + fmt(R["ej_ks_p"], 3), fmt(R["ej_media_t"], 2),
          fmt(R["ej_sh_W"], 3), "p = " + fmt(R["ej_sh_p"], 3)]
    # 5.1
    for g, c in R["e1"].values():
        e.append(f"{g} gl")
        e.append(fmt(c, 2))
    # 5.2
    t = R["e2"]; e += [fila("Boletas", *map(str, E2)), fmt(t["e"], 2), fmt(t["chi2"], 2), fmt(t["crit"], 2), "p = " + fmt(t["p"], 3)]
    e += [fmt(v, 3) for v in t["contrib"]]
    # 5.3
    t = R["e3"]; e += [fmt(t["D"], 4), fmt(t["crit"], 3), "p = " + fmt(t["p"], 3)] + [fmt(v, 4) for v in t["F"]]
    # 5.4
    t = R["e4"]; e += [fmt(v, 2) for v in t["z"]] + [fmt(t["r_qq"], 3), fmt(t["r_qq_sin"], 3), fmt(t["W"], 3), "p = " + fmt(t["p"], 3)]
    # 5.5
    t = R["e5"]; e += [fila("Rollos", *map(str, E5_F)), fmt(t["lam"], 2), fmt(t["var"], 2), fmt(t["chi2"], 2), fmt(t["crit"], 2), pval(t["p"], 4)]
    e += [fmt(v, 2) for v in t["esp"]] + [fmt(v, 2) for v in t["contrib"]]
    # 5.6
    t = R["e6"]; e += [fila("Cajas", *map(str, E6_F)), fmt(t["p_hat"], 4), fmt(t["chi2"], 3), fmt(t["crit"], 2), "p = " + fmt(t["p"], 3)]
    e += [fmt(v, 2) for v in t["esp_todas"]] + [fmt(v, 2) for v in t["esp"]]
    # 5.7
    t = R["e7"]; e += [fmt(t["chi2"], 2), fmt(t["crit"], 2), "p = " + fmt(t["p"], 3)] + [fmt(v, 2) for v in t["esp"]] + [fmt(v, 4) for v in t["pr"]]
    # 5.8
    t = R["e8"]; e += [fmt(t["crit_ks"], 3), fmt(t["crit_lf"], 3), "p = " + fmt(t["p_ks"], 3), "p = " + fmt(t["p_lf"], 3)]
    # 5.9
    t = R["e9"]; e += [fmt(v, 4) for v in t["ad"]["F"]] + [fmt(v, 3) for v in t["ad"]["terminos"]]
    e += [fmt(t["ad"]["A2"], 3), fmt(t["ks"]["D"], 4), "p = " + fmt(t["p_ks"], 3), fmt(AD_CRIT_5, 3), fmt(t["crit_ks"], 3),
          fmt(R["e9b"]["A2"], 3), fmt(R["e9b"]["D"], 4), fmt(R["e9b"]["F"], 4)]
    # 5.10
    t = R["e10"]; e += [fmt(t["p95"], 3), pct(t["frac_ks"], 2), pct(t["frac_lf"], 1), f"{t['n_ks']} de 5.000", fmt(t["crit_ks"], 3), fmt(t["crit_lf"], 3), f"semilla {E10_SEMILLA}"]
    # caso
    c = R["caso"]
    e += [fmt(c["media"], 2), fmt(c["s"], 2), fmt(c["ks_D"], 4), "p = " + fmt(c["ks_p"], 2), "p = " + fmt(c["lf_p"], 2),
          fila("Observados", *map(str, c["obs"])), fila("Esperados", *(fmt(v, 2) for v in c["esp"])),
          fila("Aporte", *(fmt(v, 3) for v in c["contrib"])),
          fmt(c["chi2"], 2), fmt(c["chi_crit"], 2), "p = " + fmt(c["chi_p"], 2), fmt(c["ad"], 3), fmt(c["ad_crit5"], 3),
          fmt(c["sh_W"], 3), pval(c["sh_p"]), fmt(c["lambda_hora"], 2), pct(c["p_mas_60"], 1), fmt(c["cv"], 2),
          fmt(R["u4_chi2"], 2), f"{R['u4_web']} de los {R['u4_total']} reclamos"]
    # sumas y razones escritas en el texto
    e += ["{%d}{120}" % int(np.dot(EJ_LLAM_K, EJ_LLAM_F)), f"{int(np.dot(E5_K, E5_F))}/100", f"{int(np.dot(E6_K, E6_F))}/600",
          f"Hay {sum(E2)} boletas", fmt(R["e9"]["ad"]["terminos"].sum(), 3), pct(max(E2) / (sum(E2) / 6) - 1, 0),
          pct(1 - exp(-3.4 / EJ_MEDIA_H0), 0), pct(log(2), 0), fmt(E4[-1] - E4[-2], 1) + " mm"]
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
