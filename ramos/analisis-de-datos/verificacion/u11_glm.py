"""Unidad 11 · Modelos lineales generalizados: logística y Poisson.

Recalcula todas las cifras de la unidad desde los datos, a mano (con la fórmula cerrada de la tabla
2 × 2 o de dos grupos) y con statsmodels, y exige que los dos caminos coincidan. Deja los datos del
ejemplo en datos/u11_*.csv, dibuja las figuras en unidades/figuras/, ejecuta el cuaderno
notebooks/u11_glm.ipynb y compara la pieza del caso con el script del caso.

    python u11_glm.py            # imprime los resultados
    python u11_glm.py --revisar  # además busca cada cifra en el .md
"""
from pathlib import Path
from math import exp, log, sqrt, lgamma
import contextlib, importlib.util, io, json, os, shutil, subprocess, sys, warnings

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore")  # las tablas 2 × 2 en GLM son modelos saturados: avisan separación sin que importe
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
DATOS, FIG, NB = RAMO / "datos", RAMO / "unidades" / "figuras", RAMO / "notebooks"
MD = RAMO / "unidades" / "11-glm-logistica-y-poisson.md"
CUADERNO = NB / "u11_glm.ipynb"


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


def cerca(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


# ---------------------------------------------------------------- fórmulas a mano

def expit(z):
    return 1 / (1 + exp(-z))


def logit_2x2(a1, n1, a0, n0):
    """Logística con un solo predictor binario, desde la tabla 2 × 2 (fórmula cerrada).
    a1 de n1 con el predictor en 1; a0 de n0 con el predictor en 0."""
    b1_, b0_ = n1 - a1, n0 - a0
    beta0 = log(a0 / b0_)
    OR = (a1 / b1_) / (a0 / b0_)
    beta1 = log(OR)
    se0 = sqrt(1 / a0 + 1 / b0_)
    se1 = sqrt(1 / a1 + 1 / b1_ + 1 / a0 + 1 / b0_)
    z = beta1 / se1
    p = 2 * stats.norm.sf(abs(z))
    ic = (exp(beta1 - 1.96 * se1), exp(beta1 + 1.96 * se1))

    def ll(k, n, q):  # log-verosimilitud binomial sin la constante combinatoria
        return k * log(q) + (n - k) * log(1 - q)
    p1, p0, pc = a1 / n1, a0 / n0, (a1 + a0) / (n1 + n0)
    ll_mod = ll(a1, n1, p1) + ll(a0, n0, p0)
    ll_nul = ll(a1, n1, pc) + ll(a0, n0, pc)
    G = 2 * (ll_mod - ll_nul)
    return {"beta0": beta0, "beta1": beta1, "se0": se0, "se1": se1, "OR": OR, "z": z, "p": p,
            "ic": ic, "p1": p1, "p0": p0, "odds1": a1 / b1_, "odds0": a0 / b0_,
            "G": G, "pG": stats.chi2.sf(G, 1)}


def poisson_2g(s0, t0, s1, t1):
    """Poisson con un predictor binario: s = total de conteos, t = exposición (días, horas)."""
    l0, l1 = s0 / t0, s1 / t1
    RR = l1 / l0
    se = sqrt(1 / s0 + 1 / s1)
    z = log(RR) / se
    lc = (s0 + s1) / (t0 + t1)

    def ll(s, t, lam):  # parte de la log-verosimilitud que depende de λ
        return s * log(lam) - lam * t
    G = 2 * (ll(s0, t0, l0) + ll(s1, t1, l1) - ll(s0, t0, lc) - ll(s1, t1, lc))
    return {"l0": l0, "l1": l1, "RR": RR, "beta0": log(l0), "beta1": log(RR), "se": se, "z": z,
            "p": 2 * stats.norm.sf(abs(z)), "ic": (exp(log(RR) - 1.96 * se), exp(log(RR) + 1.96 * se)),
            "G": G, "pG": stats.chi2.sf(G, 1)}


def pearson_phi(grupos):
    """Dispersión de Pearson de una Poisson con un nivel por grupo: Σ (y − ȳ_g)² / ȳ_g / (n − k)."""
    x2 = sum(sum((y - np.mean(g)) ** 2 / np.mean(g) for y in g) for g in grupos)
    n = sum(len(g) for g in grupos)
    return x2, x2 / (n - len(grupos))


def confusion(prob, real, umbral):
    pred = [1 if q >= umbral else 0 for q in prob]
    VP = sum(1 for a, b in zip(pred, real) if a == 1 and b == 1)
    FP = sum(1 for a, b in zip(pred, real) if a == 1 and b == 0)
    FN = sum(1 for a, b in zip(pred, real) if a == 0 and b == 1)
    VN = sum(1 for a, b in zip(pred, real) if a == 0 and b == 0)
    n = len(real)
    return {"VP": VP, "FP": FP, "FN": FN, "VN": VN, "exactitud": (VP + VN) / n,
            "sensibilidad": VP / (VP + FN), "especificidad": VN / (VN + FP)}


# ---------------------------------------------------------------- datos (originales de esta base)

# Ejemplo resuelto A · Reparto Biobío: pedidos atrasados según distancia (km) y lluvia
EJ_KM = [2, 4, 6, 8, 10]
EJ_N = {0: [60, 55, 50, 45, 40], 1: [30, 30, 25, 25, 20]}      # pedidos por tramo
EJ_A = {0: [3, 7, 7, 12, 12], 1: [6, 7, 10, 10, 13]}           # atrasados por tramo
# Ejemplo resuelto B · imprenta de etiquetas: atascos por turno según papel (0 virgen, 1 reciclado)
EJ_AT = {0: [1, 0, 2, 1, 3, 1, 0, 2, 1, 2], 1: [3, 2, 4, 1, 3, 5, 2, 3, 4, 2]}

# 11.1 · recompra con despacho gratis
E1 = {"beta": 0.42, "p_base": 0.30}
# 11.2 · falla de una bomba: logit = b0 + b1 · meses + b2 · noche
E2 = {"b0": -4.1, "b1": 0.035, "b2": 0.9, "casos": [(24, 0), (60, 1)]}
# 11.3 · Poisson: log μ = c0 + c1 · lluvia
E3 = {"c0": 0.85, "c1": 0.31}
# 11.5 · cobranza: recordatorio por WhatsApp
E5 = {"a1": 132, "n1": 180, "a0": 98, "n0": 170}
# 11.6 · log-verosimilitudes de tres modelos anidados (n = 480)
E6 = {"nulo": (-312.4, 1), "A": (-298.7, 3), "B": (-295.9, 5)}
# 11.7 · accidentes con tiempo perdido y horas-hombre de dos plantas
E7 = {"sA": 14, "hA": 52_000, "sB": 9, "hB": 61_000}
# 11.8 · doce clientes con su probabilidad predicha de abandono y lo que pasó
E8_P = [0.83, 0.74, 0.62, 0.53, 0.46, 0.41, 0.36, 0.29, 0.23, 0.18, 0.12, 0.07]
E8_Y = [1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0]
# 11.9 · abandono de una llamada según minutos de espera: logit = d0 + d1 · min
E9 = {"d0": -3.4, "d1": 0.45, "minutos": [2, 6, 10]}
# 11.10 · fallas diarias de dos líneas de envasado (12 días cada una)
E10 = {"L1": [0, 1, 7, 0, 2, 9, 1, 0, 6, 1, 3, 0], "L2": [2, 8, 0, 11, 1, 4, 0, 9, 3, 12, 1, 5]}


def ejemplo_df():
    filas = []
    for ll_ in (0, 1):
        for km, n, a in zip(EJ_KM, EJ_N[ll_], EJ_A[ll_]):
            filas.append({"km": km, "lluvia": ll_, "pedidos": n, "atrasados": a})
    return pd.DataFrame(filas)


def atascos_df():
    return pd.DataFrame([{"turno": i + 1 + 10 * g, "reciclado": g, "atascos": y}
                         for g in (0, 1) for i, y in enumerate(EJ_AT[g])])


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
    # --- ejemplo A: a mano la tabla 2 × 2 (solo lluvia), con statsmodels el modelo con distancia
    d = ejemplo_df(); d["a_tiempo"] = d.pedidos - d.atrasados
    a1, n1 = int(d[d.lluvia == 1].atrasados.sum()), int(d[d.lluvia == 1].pedidos.sum())
    a0, n0 = int(d[d.lluvia == 0].atrasados.sum()), int(d[d.lluvia == 0].pedidos.sum())
    m = logit_2x2(a1, n1, a0, n0)
    g1 = smf.glm("atrasados + a_tiempo ~ lluvia", data=d, family=sm.families.Binomial()).fit()
    assert cerca(g1.params["lluvia"], m["beta1"]) and cerca(g1.params["Intercept"], m["beta0"])
    assert cerca(g1.bse["lluvia"], m["se1"], 1e-5) and cerca(g1.null_deviance - g1.deviance, m["G"], 1e-6)
    g2 = smf.glm("atrasados + a_tiempo ~ km + lluvia", data=d, family=sm.families.Binomial()).fit()
    gk = smf.glm("atrasados + a_tiempo ~ km", data=d, family=sm.families.Binomial()).fit()
    pred = {(km, ll_): float(g2.predict(pd.DataFrame({"km": [km], "lluvia": [ll_]}))[0])
            for km in (2, 6, 10) for ll_ in (0, 1)}
    for (km, ll_), q in pred.items():  # la probabilidad predicha a mano desde los coeficientes
        assert cerca(q, expit(g2.params["Intercept"] + g2.params["km"] * km + g2.params["lluvia"] * ll_))
    G_ll = gk.deviance - g2.deviance
    G_km = g1.deviance - g2.deviance
    R["ejA"] = {**m, "a1": a1, "n1": n1, "a0": a0, "n0": n0,
                "b": g2.params.to_dict(), "se": g2.bse.to_dict(), "zb": g2.tvalues.to_dict(),
                "pb": g2.pvalues.to_dict(), "OR_ll": exp(g2.params["lluvia"]), "OR_km": exp(g2.params["km"]),
                "OR_ll_ic": tuple(np.exp(g2.conf_int().loc["lluvia"])), "pred": pred,
                "dev": g2.deviance, "dev_nula": g2.null_deviance, "gl": int(g2.df_resid),
                "p_dev": stats.chi2.sf(g2.deviance, g2.df_resid),
                "G_ll": G_ll, "pG_ll": stats.chi2.sf(G_ll, 1), "G_km": G_km, "pG_km": stats.chi2.sf(G_km, 1),
                "props": [(km, ll_, a / n) for ll_ in (0, 1) for km, n, a in zip(EJ_KM, EJ_N[ll_], EJ_A[ll_])]}

    # --- ejemplo B: Poisson de atascos
    s0, s1 = sum(EJ_AT[0]), sum(EJ_AT[1])
    pB = poisson_2g(s0, len(EJ_AT[0]), s1, len(EJ_AT[1]))
    t = atascos_df()
    gp = smf.glm("atascos ~ reciclado", data=t, family=sm.families.Poisson()).fit()
    assert cerca(gp.params["reciclado"], pB["beta1"]) and cerca(gp.bse["reciclado"], pB["se"], 1e-5)
    assert cerca(gp.null_deviance - gp.deviance, pB["G"], 1e-6)
    x2, phi = pearson_phi([EJ_AT[0], EJ_AT[1]])
    assert cerca(x2, gp.pearson_chi2, 1e-9)
    R["ejB"] = {**pB, "s0": s0, "s1": s1, "var0": float(np.var(EJ_AT[0], ddof=1)),
                "var1": float(np.var(EJ_AT[1], ddof=1)), "dev": gp.deviance, "gl": int(gp.df_resid),
                "x2": x2, "phi": phi}

    # --- ejercicios
    odds_base = E1["p_base"] / (1 - E1["p_base"])
    OR1 = exp(E1["beta"]); odds_t = odds_base * OR1
    R["e1"] = {"OR": OR1, "odds_base": odds_base, "logodds_base": log(odds_base), "odds_t": odds_t,
               "p_t": odds_t / (1 + odds_t), "cambio_pct_odds": OR1 - 1}
    R["e2"] = [{"eta": E2["b0"] + E2["b1"] * mes + E2["b2"] * no,
                "p": expit(E2["b0"] + E2["b1"] * mes + E2["b2"] * no)} for mes, no in E2["casos"]]
    R["e2_OR_noche"] = exp(E2["b2"]); R["e2_OR_12m"] = exp(12 * E2["b1"])
    R["e3"] = {"mu0": exp(E3["c0"]), "mu1": exp(E3["c0"] + E3["c1"]), "RR": exp(E3["c1"])}
    m5 = logit_2x2(**E5)
    d5 = pd.DataFrame({"x": [1, 0], "si": [E5["a1"], E5["a0"]], "no": [E5["n1"] - E5["a1"], E5["n0"] - E5["a0"]]})
    g5 = smf.glm("si + no ~ x", data=d5, family=sm.families.Binomial()).fit()
    assert cerca(g5.params["x"], m5["beta1"]) and cerca(g5.bse["x"], m5["se1"], 1e-5)
    R["e5"] = m5
    ll = {k: v[0] for k, v in E6.items()}; k_ = {k: v[1] for k, v in E6.items()}
    GA = 2 * (ll["A"] - ll["nulo"]); GB = 2 * (ll["B"] - ll["A"])
    R["e6"] = {"GA": GA, "pA": stats.chi2.sf(GA, k_["A"] - k_["nulo"]), "GB": GB,
               "pB": stats.chi2.sf(GB, k_["B"] - k_["A"]), "crit": stats.chi2.ppf(0.95, 2),
               "aic": {k: -2 * ll[k] + 2 * k_[k] for k in ll},
               "dev": {k: -2 * ll[k] for k in ll}}
    p7 = poisson_2g(E7["sB"], E7["hB"], E7["sA"], E7["hA"])   # grupo 1 = planta A, base = planta B
    d7 = pd.DataFrame({"y": [E7["sA"], E7["sB"]], "A": [1, 0], "h": [E7["hA"], E7["hB"]]})
    g7 = smf.glm("y ~ A", data=d7, family=sm.families.Poisson(), offset=np.log(d7.h)).fit()
    assert cerca(g7.params["A"], p7["beta1"]) and cerca(g7.bse["A"], p7["se"], 1e-5)
    R["e7"] = {**p7, "tasaA": 100_000 * E7["sA"] / E7["hA"], "tasaB": 100_000 * E7["sB"] / E7["hB"]}
    R["e8"] = {u: confusion(E8_P, E8_Y, u) for u in (0.5, 0.3)}
    e9 = {}
    for mi in E9["minutos"]:
        q = expit(E9["d0"] + E9["d1"] * mi)
        e9[mi] = {"p": q, "pendiente": E9["d1"] * q * (1 - q),
                  "salto": expit(E9["d0"] + E9["d1"] * (mi + 1)) - q}
    R["e9"] = {"OR1": exp(E9["d1"]), "OR5": exp(5 * E9["d1"]), "m50": -E9["d0"] / E9["d1"],
               "pend_max": E9["d1"] / 4, "por_min": e9}
    L1, L2 = E10["L1"], E10["L2"]
    p10 = poisson_2g(sum(L1), len(L1), sum(L2), len(L2))
    x2_10, phi10 = pearson_phi([L1, L2])
    t10 = pd.DataFrame({"x": [0] * len(L1) + [1] * len(L2), "y": L1 + L2})
    g10 = smf.glm("y ~ x", data=t10, family=sm.families.Poisson()).fit()
    q10 = smf.glm("y ~ x", data=t10, family=sm.families.Poisson()).fit(scale="X2")
    assert cerca(g10.pvalues["x"], p10["p"], 1e-5) and cerca(q10.scale, phi10, 1e-9)
    se_q = p10["se"] * sqrt(phi10); z_q = p10["beta1"] / se_q
    p_q = 2 * stats.norm.sf(abs(z_q))
    # statsmodels usa la normal también en la cuasi-Poisson: deben coincidir
    assert cerca(q10.bse["x"], se_q, 1e-6) and cerca(q10.pvalues["x"], p_q, 1e-5)
    R["e10"] = {**p10, "m1": np.mean(L1), "m2": np.mean(L2), "v1": float(np.var(L1, ddof=1)),
                "v2": float(np.var(L2, ddof=1)), "x2": x2_10, "phi": phi10, "se_q": se_q, "z_q": z_q,
                "p_q": p_q, "s1": sum(L1), "s2": sum(L2)}

    # --- caso
    caso, D = cargar_caso()
    l = D["lotes"]; r = D["reclamos_dia"]
    a1c = int(l[l.tinta_agua == 1].defecto.sum()); n1c = int((l.tinta_agua == 1).sum())
    a0c = int(l[l.tinta_agua == 0].defecto.sum()); n0c = int((l.tinta_agua == 0).sum())
    mc = logit_2x2(a1c, n1c, a0c, n0c)
    mt = smf.logit("defecto ~ tinta_agua", data=l).fit(disp=0)
    assert cerca(mt.params["tinta_agua"], mc["beta1"]) and cerca(mt.bse["tinta_agua"], mc["se1"], 1e-5)
    m4 = smf.logit("defecto ~ temperatura + tinta_agua", data=l).fit(disp=0)
    m4t = smf.logit("defecto ~ temperatura", data=l).fit(disp=0)
    prc = {(T, w): float(m4.predict(pd.DataFrame({"temperatura": [T], "tinta_agua": [w]}))[0])
           for T in (150, 160, 170) for w in (0, 1)}
    cm = confusion(list(m4.predict()), list(l.defecto), 0.5)
    G_tinta = 2 * (m4.llf - m4t.llf)
    s0c, s1c = int(r[r.campana_web == 0].reclamos.sum()), int(r[r.campana_web == 1].reclamos.sum())
    d0c, d1c = int((r.campana_web == 0).sum()), int((r.campana_web == 1).sum())
    pc = poisson_2g(s0c, d0c, s1c, d1c)
    p5 = smf.glm("reclamos ~ campana_web", data=r, family=sm.families.Poisson()).fit()
    assert cerca(p5.params["campana_web"], pc["beta1"]) and cerca(p5.bse["campana_web"], pc["se"], 1e-5)
    x2c, phic = pearson_phi([list(r[r.campana_web == 0].reclamos), list(r[r.campana_web == 1].reclamos)])
    assert cerca(x2c, p5.pearson_chi2, 1e-9)
    R["caso"] = {"tabla": mc, "a1": a1c, "n1": n1c, "a0": a0c, "n0": n0c,
                 "b": m4.params.to_dict(), "se": m4.bse.to_dict(), "z": m4.tvalues.to_dict(),
                 "p": m4.pvalues.to_dict(), "OR_tinta": exp(m4.params["tinta_agua"]),
                 "OR_tinta_ic": tuple(np.exp(m4.conf_int().loc["tinta_agua"])),
                 "OR_temp": exp(m4.params["temperatura"]), "OR_temp10": exp(10 * m4.params["temperatura"]),
                 "pred": prc, "cm": cm, "dev": -2 * m4.llf, "dev_nula": -2 * m4.llnull,
                 "G": m4.llr, "pG": m4.llr_pvalue, "G_tinta": G_tinta, "pG_tinta": stats.chi2.sf(G_tinta, 1),
                 "aic": m4.aic, "temp_media": l.groupby("tinta_agua").temperatura.mean().to_dict(),
                 "pois": pc, "s0": s0c, "s1": s1c, "d0": d0c, "d1": d1c,
                 "var0": float(r[r.campana_web == 0].reclamos.var()), "var1": float(r[r.campana_web == 1].reclamos.var()),
                 "pdev": p5.deviance, "pgl": int(p5.df_resid), "x2": x2c, "phi": phic,
                 "raiz_phi": sqrt(phic), "se_q": pc["se"] * sqrt(phic), "z_q": pc["beta1"] / (pc["se"] * sqrt(phic)),
                 "pois_coef": p5.params.to_dict()}
    R["_caso_mod"], R["_D"] = caso, D
    return R


# ---------------------------------------------------------------- datos del ejemplo, figuras y cuaderno

def escribir_datos():
    ejemplo_df().to_csv(DATOS / "u11_ejemplo_reparto.csv", index=False, encoding="utf-8")
    atascos_df().to_csv(DATOS / "u11_ejemplo_atascos.csv", index=False, encoding="utf-8")


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
    FIG.mkdir(parents=True, exist_ok=True)
    pc = lambda v, _: pct(v, 0)

    # ejemplo: proporción observada y curva ajustada por lluvia
    e = R["ejA"]; b = e["b"]
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    xs = np.linspace(1, 11, 200)
    for ll_, col, nom in ((0, AZUL, "sin lluvia"), (1, NARANJA, "con lluvia")):
        ax.plot(xs, [expit(b["Intercept"] + b["km"] * x + b["lluvia"] * ll_) for x in xs], color=col, lw=2, label=f"modelo, {nom}")
        pts = [(km, q) for km, l_, q in e["props"] if l_ == ll_]
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], color=col, s=28, zorder=3, edgecolor="white", label=f"observado, {nom}")
    ax.set_xlabel("distancia del pedido (km)"); ax.set_ylabel("pedidos atrasados")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(pc))
    ax.set_title("Reparto Biobío · probabilidad de atraso", fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=7.5); estilo(ax)
    fig.tight_layout(); fig.savefig(FIG / "u11_ejemplo.png", dpi=170); plt.close(fig)

    # caso: curvas de la logística y reclamos por día
    c = R["caso"]; b = c["b"]; l = R["_D"]["lotes"]; r = R["_D"]["reclamos_dia"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.2), gridspec_kw={"width_ratios": [1.4, 1]})
    xs = np.linspace(140, 180, 200)
    rng = np.random.default_rng(11)
    for w, col, nom in ((0, AZUL, "plastisol"), (1, NARANJA, "tinta al agua")):
        a1.plot(xs, [expit(b["Intercept"] + b["temperatura"] * x + b["tinta_agua"] * w) for x in xs], color=col, lw=2, label=nom)
        s = l[l.tinta_agua == w]
        a1.scatter(s.temperatura, s.defecto + rng.uniform(-0.03, 0.03, len(s)) + (0.04 if w else -0.04) * (2 * s.defecto - 1),
                   color=col, s=8, alpha=.45)
    a1.set_xlabel("temperatura de curado (°C)"); a1.set_ylabel("probabilidad de defecto")
    a1.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(pc))
    a1.set_title("Lotes con defecto (puntos: 0 o 1)", fontsize=9.5, loc="left"); a1.legend(frameon=False, fontsize=7.5)
    estilo(a1)
    maxi = int(r.reclamos.max())
    k = np.arange(0, maxi + 1)
    for w, col, nom, dx in ((0, AZUL, "sin campaña", -0.2), (1, NARANJA, "con campaña", 0.2)):
        s = r[r.campana_web == w].reclamos
        a2.bar(k + dx, [(s == i).sum() for i in k], width=0.4, color=col, label=f"{nom} (media {fmt(s.mean(), 2)})")
    a2.set_xlabel("reclamos en el día"); a2.set_ylabel("días")
    a2.set_title("Reclamos diarios", fontsize=9.5, loc="left"); a2.legend(frameon=False, fontsize=7.5)
    estilo(a2)
    fig.tight_layout(); fig.savefig(FIG / "u11_caso.png", dpi=170); plt.close(fig)


def ejecutar_cuaderno():
    """Ejecuta el cuaderno (nbconvert si está; si no, exec de sus celdas) y devuelve su RES."""
    nb = json.loads(CUADERNO.read_text(encoding="utf-8"))
    import matplotlib
    matplotlib.use("Agg")
    jup = shutil.which("jupyter")
    if jup:  # se ejecuta de verdad con nbconvert; RES se vuelve a leer con exec para comparar
        subprocess.run([jup, "nbconvert", "--to", "notebook", "--execute", "--stdout", str(CUADERNO)],
                       check=True, cwd=NB, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    previo = Path.cwd()
    os.chdir(NB)
    try:
        ns = {"__name__": "__cuaderno__"}
        with contextlib.redirect_stdout(io.StringIO()):  # lo que imprime el cuaderno no ensucia el informe
            for celda in nb["cells"]:
                if celda["cell_type"] == "code":
                    exec("".join(celda["source"]), ns)
    finally:
        os.chdir(previo)
    return ns["RES"]


def comparar_cuaderno(R, RES):
    a, b, c = R["ejA"], R["ejB"], R["caso"]
    pares = [("ej_beta_lluvia_2x2", a["beta1"]), ("ej_se_lluvia_2x2", a["se1"]),
             ("ej_beta_km", a["b"]["km"]), ("ej_beta_lluvia", a["b"]["lluvia"]), ("ej_dev", a["dev"]),
             ("ej_rr_atascos", b["RR"]), ("ej_phi_atascos", b["phi"]),
             ("caso_or_tinta", c["OR_tinta"]), ("caso_beta_temp", c["b"]["temperatura"]),
             ("caso_G", c["G"]), ("caso_rr_web", c["pois"]["RR"]), ("caso_phi", c["phi"])]
    malos = [k for k, v in pares if not cerca(RES[k], v, 1e-6)]
    print("CUADERNO:", "OK, reproduce el ejemplo y el caso" if not malos else f"difiere en {malos}")
    return not malos


def cadena(R):
    caso, D = R["_caso_mod"], R["_D"]
    C = caso.calcular(D)["u11"]
    c = R["caso"]
    ok = (all(cerca(C["logit_coef"][k], c["b"][k], 1e-9) for k in c["b"])
          and cerca(C["odds_tinta_agua"], c["OR_tinta"], 1e-9)
          and all(cerca(C["poisson_coef"][k], c["pois_coef"][k], 1e-9) for k in c["pois_coef"])
          and cerca(C["razon_tasas_web"], c["pois"]["RR"], 1e-9))
    J = json.loads((AQUI / "caso_estampa_sur_datos.json").read_text(encoding="utf-8"))["u11"]
    ok = ok and cerca(J["odds_tinta_agua"], c["OR_tinta"], 1e-9) and cerca(J["razon_tasas_web"], c["pois"]["RR"], 1e-9)
    print("CADENA:", f"OK, la pieza u11 del caso calza (odds ratio {fmt(c['OR_tinta'], 2)}, razón de tasas {fmt(c['pois']['RR'], 2)})"
          if ok else "NO calza")
    return ok


# ---------------------------------------------------------------- impresión

def imprimir(R):
    for k, v in R.items():
        if not k.startswith("_"):
            print(f"== {k}")
            if isinstance(v, dict):
                for kk, vv in v.items():
                    print(f"   {kk}: {vv}")
            else:
                print("  ", v)


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    E = []
    a = R["ejA"]
    E += [f"{a['a1']}/{a['n1']}", f"{a['a0']}/{a['n0']}", fmt(a["odds1"], 4), fmt(a["odds0"], 4),
          fmt(a["OR"], 3), fmt(a["beta0"], 4), fmt(a["beta1"], 4), fmt(a["se1"], 4), fmt(a["z"], 2),
          fmt(a["G"], 2), fmt(a["ic"][0], 2), fmt(a["ic"][1], 2), pct(a["p1"], 1), pct(a["p0"], 1)]
    E += [fmt(a["b"]["Intercept"], 4), fmt(a["b"]["km"], 4), fmt(a["b"]["lluvia"], 4),
          fmt(a["se"]["km"], 4), fmt(a["se"]["lluvia"], 4), fmt(a["zb"]["km"], 2), fmt(a["zb"]["lluvia"], 2),
          fmt(a["OR_ll"], 2), fmt(a["OR_km"], 3), fmt(a["OR_ll_ic"][0], 2), fmt(a["OR_ll_ic"][1], 2),
          fmt(a["dev"], 2), fmt(a["dev_nula"], 2), fmt(a["p_dev"], 2), fmt(a["G_ll"], 2), fmt(a["G_km"], 2)]
    E += [pct(q, 1) for q in a["pred"].values()]
    eta10 = a["b"]["Intercept"] + 10 * a["b"]["km"] + a["b"]["lluvia"]
    assert cerca(expit(eta10), a["pred"][(10, 1)])
    E += [f"{a['a1'] + a['a0']} atrasos", fmt(eta10, 3),
          f"{fmt(100 * (a['pred'][(2, 1)] - a['pred'][(2, 0)]), 0)} puntos a 2 km",
          f"{fmt(100 * (a['pred'][(10, 1)] - a['pred'][(10, 0)]), 0)} puntos a 10 km"]
    E += [fila(str(km), str(n), str(at), pct(at / n, 1)) for ll_ in (0, 1)
          for km, n, at in zip(EJ_KM, EJ_N[ll_], EJ_A[ll_])]
    b = R["ejB"]
    E += [", ".join(str(y) for y in EJ_AT[0]), ", ".join(str(y) for y in EJ_AT[1]),
          fmt(b["l0"], 1), fmt(b["l1"], 1), fmt(b["RR"], 3), fmt(b["beta0"], 4), fmt(b["beta1"], 4),
          fmt(b["se"], 4), fmt(b["z"], 2), pv(b["p"]), fmt(b["ic"][0], 2), fmt(b["ic"][1], 2), fmt(b["G"], 2),
          pv(b["pG"]), f"{fmt(b['l1'] - b['l0'], 1)} atascos más", f"{b['gl']} grados de libertad", fmt(b["var0"], 2), fmt(b["var1"], 2), fmt(b["x2"], 2), fmt(b["phi"], 2), fmt(b["dev"], 2)]
    e1 = R["e1"]
    E += [fmt(e1["OR"], 3), fmt(e1["odds_base"], 4), fmt(e1["logodds_base"], 4), fmt(e1["odds_t"], 4),
          pct(e1["p_t"], 1), pct(e1["cambio_pct_odds"], 1),
          f"{fmt(100 * (e1['p_t'] - E1['p_base']), 1)} puntos"]
    E += [fmt(x["eta"], 2) for x in R["e2"]] + [pct(x["p"], 1) for x in R["e2"]]
    E += [fmt(R["e2_OR_noche"], 2), fmt(R["e2_OR_12m"], 2)]
    e3 = R["e3"]; E += [fmt(e3["mu0"], 2), fmt(e3["mu1"], 2), fmt(e3["RR"], 3),
                        f"unas {fmt(8 * (e3['mu1'] - e3['mu0']), 0)} llamadas más"]
    e5 = R["e5"]
    E += [fmt(e5["odds1"], 3), fmt(e5["odds0"], 3), fmt(e5["OR"], 3), fmt(e5["beta0"], 4), fmt(e5["beta1"], 4),
          fmt(e5["se1"], 4), fmt(e5["z"], 2), pv(e5["p"]), fmt(e5["ic"][0], 2), fmt(e5["ic"][1], 2),
          pct(e5["p0"], 1), pct(e5["p1"], 1)]
    e6 = R["e6"]
    E += [fmt(e6["GA"], 1), fmt(e6["GB"], 1), pv(e6["pB"]), fmt(e6["crit"], 2)] + [fmt(v, 1) for v in e6["aic"].values()]
    e7 = R["e7"]
    E += [fmt(e7["tasaA"], 1), fmt(e7["tasaB"], 1), fmt(e7["RR"], 2), fmt(e7["beta1"], 4), fmt(e7["se"], 4),
          fmt(e7["z"], 2), pv(e7["p"]), fmt(e7["ic"][0], 2), fmt(e7["ic"][1], 2),
          f"{E7['sA'] + E7['sB']} accidentes"]
    for u, c in R["e8"].items():
        E += [fila(f"**{fmt(u, 1)}**", str(c["VP"]), str(c["FP"]), str(c["FN"]), str(c["VN"]),
                   pct(c["exactitud"], 1), pct(c["sensibilidad"], 1), pct(c["especificidad"], 1))]
    e9 = R["e9"]
    E += [fmt(e9["OR1"], 3), fmt(e9["OR5"], 2), fmt(e9["m50"], 2), fmt(e9["pend_max"], 4)]
    for mi, v in e9["por_min"].items():
        E += [fila(str(mi), pct(v["p"], 1), fmt(v["pendiente"], 4), fmt(100 * v["salto"], 1))]
    e10 = R["e10"]
    E += [fmt(e10["m1"], 2), fmt(e10["m2"], 2), fmt(e10["v1"], 2), fmt(e10["v2"], 2), fmt(e10["RR"], 3),
          fmt(e10["se"], 4), fmt(e10["z"], 2), pv(e10["p"]), fmt(e10["x2"], 2), fmt(e10["phi"], 2),
          fmt(e10["se_q"], 4), fmt(e10["z_q"], 2), pv(e10["p_q"]),
          f"{len(E10['L1']) + len(E10['L2']) - 2} grados de libertad"]
    c = R["caso"]; t = c["tabla"]
    E += [f"{c['a1']}/{c['n1']}", f"{c['a0']}/{c['n0']}", fmt(t["odds1"], 3), fmt(t["odds0"], 3), fmt(t["OR"], 2),
          fmt(t["beta1"], 4), fmt(t["se1"], 4), fmt(t["z"], 2), pv(t["p"])]
    E += [fmt(c["b"]["Intercept"], 4), fmt(c["b"]["temperatura"], 4), fmt(c["b"]["tinta_agua"], 4),
          fmt(c["se"]["temperatura"], 4), fmt(c["se"]["tinta_agua"], 4), fmt(c["z"]["temperatura"], 2),
          fmt(c["z"]["tinta_agua"], 2), pv(c["p"]["tinta_agua"]), fmt(c["OR_tinta"], 2),
          fmt(c["OR_tinta_ic"][0], 2), fmt(c["OR_tinta_ic"][1], 2), fmt(c["OR_temp"], 3), fmt(c["OR_temp10"], 2),
          fmt(c["dev"], 2), fmt(c["dev_nula"], 2), fmt(c["G"], 2), fmt(c["G_tinta"], 2), pv(c["pG_tinta"]),
          fmt(c["temp_media"][0], 1), fmt(c["temp_media"][1], 1)]
    E += [pct(q, 1) for q in c["pred"].values()]
    cm = c["cm"]
    E += [fila("**defecto**", str(cm["VP"]), str(cm["FN"])), fila("**sin defecto**", str(cm["FP"]), str(cm["VN"])),
          pct(cm["exactitud"], 1), pct(cm["sensibilidad"], 1), pct(cm["especificidad"], 1)]
    p = c["pois"]
    E += [f"{c['s0']} reclamos en {c['d0']} días", f"{c['s1']} reclamos en {c['d1']} días",
          fmt(p["l0"], 3), fmt(p["l1"], 3), fmt(p["RR"], 2), fmt(p["beta0"], 4), fmt(p["beta1"], 4), fmt(p["se"], 4),
          fmt(p["z"], 2), fmt(p["ic"][0], 2), fmt(p["ic"][1], 2), fmt(p["G"], 2), fmt(c["var0"], 2),
          fmt(c["var1"], 2), fmt(c["pdev"], 2), fmt(c["x2"], 2), fmt(c["phi"], 2),
          fmt(c["raiz_phi"], 2), fmt(c["se_q"], 4), fmt(c["z_q"], 2), f"{c['pgl']} grados de libertad",
          f"medias {fmt(p['l0'], 2)} y {fmt(p['l1'], 2)}"]
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
