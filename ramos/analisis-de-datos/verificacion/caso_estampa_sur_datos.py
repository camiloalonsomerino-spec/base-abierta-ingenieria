"""Caso integrador de Análisis de Datos · Estampa Sur mira sus datos.

El mismo taller ficticio de los otros ramos. Acá tiene datos: mediciones de dos máquinas, prendas
defectuosas por proveedor, tiempos de secado según tinta y temperatura, ventas semanales y reclamos.
Todos los datos son SIMULADOS con semilla fija por este script: no describen ningún taller real.

    python caso_estampa_sur_datos.py          # genera los CSV en ramos/analisis-de-datos/datos/ e imprime la cadena
    python caso_estampa_sur_datos.py --json   # además deja caso_estampa_sur_datos.json
"""
from pathlib import Path
import json, sys

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multicomp import pairwise_tukeyhsd

sys.stdout.reconfigure(encoding="utf-8")
DATOS = Path(__file__).resolve().parents[1] / "datos"
SEMILLA = 2025


def generar():
    rng = np.random.default_rng(SEMILLA)
    D = {}
    # U1-U2 · desplazamiento del registro (mm) en dos máquinas de estampado, 18 y 22 prendas
    D["registro"] = pd.DataFrame({
        "maquina": ["pulpo 6"] * 18 + ["pulpo 4"] * 22,
        "desplazamiento_mm": np.round(np.r_[rng.normal(0.112, 0.041, 18), rng.normal(0.147, 0.049, 22)], 3)})
    # U3 · prendas defectuosas por proveedor de prendas lisas (conteos)
    D["defectos"] = pd.DataFrame({"proveedor": ["Telas Norte", "Algodones Sur", "Textil Ñuble"],
                                  "defectuosas": [37, 58, 29], "revisadas": [820, 910, 760]})
    # U4 · tipo de reclamo según canal de venta (tabla de contingencia)
    D["reclamos_canal"] = pd.DataFrame({"canal": ["tienda", "web", "colegios"],
                                        "talla": [41, 63, 22], "color": [28, 35, 31], "atraso": [17, 52, 46]})
    # U5 · tiempos entre llegadas de pedidos web (minutos) para bondad de ajuste
    D["llegadas"] = pd.DataFrame({"minutos": np.round(rng.exponential(23.4, 120), 1)})
    # U6 · precio de venta y unidades vendidas por semana (correlación y regresión)
    precio = np.round(rng.uniform(9_800, 13_200, 30), -1)
    publicidad = np.round(rng.uniform(40_000, 160_000, 30), -3)
    unidades = np.round(1_470 - 0.082 * precio + 0.0019 * publicidad + rng.normal(0, 38, 30))
    D["ventas"] = pd.DataFrame({"semana": range(1, 31), "precio": precio, "publicidad": publicidad,
                                "unidades": unidades.astype(int)})
    # U7-U9 · tiempo de secado (min) según tinta (3) y temperatura (2), 5 réplicas
    filas = []
    efecto_tinta = {"plastisol": 0.0, "agua": 3.1, "descarga": 5.4}
    efecto_temp = {"150 °C": 0.0, "170 °C": -2.6}
    for t, et in efecto_tinta.items():
        for c, ec in efecto_temp.items():
            inter = -1.5 if (t == "descarga" and c == "170 °C") else 0.0
            for _ in range(5):
                filas.append({"tinta": t, "temperatura": c,
                              "secado_min": round(18.6 + et + ec + inter + rng.normal(0, 1.2), 1)})
    D["secado"] = pd.DataFrame(filas)
    # U11 · probabilidad de defecto (logística) y reclamos diarios (Poisson)
    n = 160
    temp = rng.uniform(140, 180, n); tinta_agua = rng.integers(0, 2, n)
    logit = -9.2 + 0.052 * temp + 0.61 * tinta_agua
    D["lotes"] = pd.DataFrame({"temperatura": np.round(temp, 1), "tinta_agua": tinta_agua,
                               "defecto": rng.binomial(1, 1 / (1 + np.exp(-logit)))})
    dias = 60; web = rng.integers(0, 2, dias)
    D["reclamos_dia"] = pd.DataFrame({"campana_web": web, "reclamos": rng.poisson(np.exp(0.9 + 0.48 * web))})
    return D


def calcular(D):
    R = {}
    r = D["registro"]; a = r[r.maquina == "pulpo 6"].desplazamiento_mm; b = r[r.maquina == "pulpo 4"].desplazamiento_mm
    t_welch = stats.ttest_ind(a, b, equal_var=False)
    t_pool = stats.ttest_ind(a, b, equal_var=True)
    F = a.var(ddof=1) / b.var(ddof=1)
    pF = 2 * min(stats.f.cdf(F, len(a) - 1, len(b) - 1), 1 - stats.f.cdf(F, len(a) - 1, len(b) - 1))
    R["u2"] = {"media_6": a.mean(), "media_4": b.mean(), "de_6": a.std(ddof=1), "de_4": b.std(ddof=1),
               "t_welch": t_welch.statistic, "p_welch": t_welch.pvalue, "t_pool": t_pool.statistic, "p_pool": t_pool.pvalue}
    R["u3"] = {"F": F, "p_F": pF}
    d = D["defectos"]
    chi_h = stats.chi2_contingency(np.c_[d.defectuosas, d.revisadas - d.defectuosas])
    R["u3"].update({"tasas": list(d.defectuosas / d.revisadas), "chi2_homog": chi_h[0], "p_homog": chi_h[1]})
    rc = D["reclamos_canal"][["talla", "color", "atraso"]].values
    chi = stats.chi2_contingency(rc)
    R["u4"] = {"chi2": chi[0], "gl": int(chi[2]), "p": chi[1],
               "v_cramer": float(np.sqrt(chi[0] / (rc.sum() * (min(rc.shape) - 1))))}
    x = D["llegadas"].minutos
    ks = stats.kstest(x, "expon", args=(0, x.mean()))
    sh = stats.shapiro(x)
    R["u5"] = {"media": x.mean(), "ks_D": ks.statistic, "ks_p": ks.pvalue, "shapiro_W": sh.statistic, "shapiro_p": sh.pvalue}
    v = D["ventas"]
    pr = stats.pearsonr(v.precio, v.unidades); sp = stats.spearmanr(v.precio, v.unidades)
    R["u6"] = {"pearson_r": pr.statistic, "pearson_p": pr.pvalue, "spearman_rho": sp.statistic, "spearman_p": sp.pvalue}
    s = D["secado"]
    m1 = smf.ols("secado_min ~ C(tinta)", data=s).fit()
    a1 = sm.stats.anova_lm(m1, typ=1)
    tk = pairwise_tukeyhsd(s.secado_min, s.tinta)
    m2 = smf.ols("secado_min ~ C(tinta) * C(temperatura)", data=s).fit()
    a2 = sm.stats.anova_lm(m2, typ=2)
    lev = stats.levene(*[g.secado_min for _, g in s.groupby("tinta")])
    R["u7"] = {"F_tinta": float(a1["F"].iloc[0]), "p_tinta": float(a1["PR(>F)"].iloc[0]),
               "medias": s.groupby("tinta").secado_min.mean().round(3).to_dict()}
    R["u8"] = {"tukey": [[str(x) for x in fila] for fila in tk.summary().data[1:]]}
    R["u9"] = {"anova2": {k: {"F": float(a2.loc[k, "F"]), "p": float(a2.loc[k, "PR(>F)"])} for k in a2.index if k != "Residual"},
               "levene_p": lev.pvalue}
    m3 = smf.ols("unidades ~ precio + publicidad", data=v).fit()
    R["u10"] = {"coef": m3.params.round(6).to_dict(), "p": m3.pvalues.to_dict(), "r2": m3.rsquared, "r2_aj": m3.rsquared_adj}
    l = D["lotes"]; m4 = smf.logit("defecto ~ temperatura + tinta_agua", data=l).fit(disp=0)
    p5 = smf.glm("reclamos ~ campana_web", data=D["reclamos_dia"], family=sm.families.Poisson()).fit()
    R["u11"] = {"logit_coef": m4.params.to_dict(), "odds_tinta_agua": float(np.exp(m4.params["tinta_agua"])),
                "poisson_coef": p5.params.to_dict(), "razon_tasas_web": float(np.exp(p5.params["campana_web"]))}
    # U12 · bayesiano: tasa de defecto de Algodones Sur con a priori Beta(4, 76) (unos 5 %)
    a0, b0 = 4, 76; k_, n_ = int(d.defectuosas[1]), int(d.revisadas[1])
    post = stats.beta(a0 + k_, b0 + n_ - k_)
    R["u12"] = {"priori": [a0, b0], "posteriori": [a0 + k_, b0 + n_ - k_], "media_post": post.mean(),
                "ic95": [post.ppf(0.025), post.ppf(0.975)], "prob_sobre_6pct": 1 - post.cdf(0.06)}
    return R


def limpio(v):
    if isinstance(v, dict): return {str(k): limpio(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)): return [limpio(x) for x in v]
    if isinstance(v, (np.floating, np.integer)): return float(v)
    return v


if __name__ == "__main__":
    D = generar()
    DATOS.mkdir(exist_ok=True)
    for k, df in D.items():
        df.to_csv(DATOS / f"{k}.csv", index=False, encoding="utf-8")
    C = limpio(calcular(D))
    for k, v in C.items():
        print(f"== {k}")
        for kk, vv in v.items():
            print(f"   {kk}: {vv}")
    if "--json" in sys.argv:
        Path(__file__).with_suffix(".json").write_text(json.dumps(C, ensure_ascii=False, indent=1), encoding="utf-8")
