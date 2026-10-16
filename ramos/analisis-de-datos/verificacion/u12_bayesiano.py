"""Unidad 12 · Inferencia bayesiana.

Recalcula todas las cifras de la unidad desde los datos, a mano (fórmulas de las conjugadas y
aproximación normal) y con scipy.stats (cuantiles exactos), y exige que los dos caminos coincidan.
Comprueba cada posteriori conjugada contra una grilla numérica (priori × verosimilitud normalizada).
Deja los datos del ejemplo en datos/u12_*.csv, dibuja las figuras en unidades/figuras/, ejecuta el
cuaderno notebooks/u12_bayesiano.ipynb y compara la pieza del caso con el script del caso.

    python u12_bayesiano.py            # imprime los resultados
    python u12_bayesiano.py --revisar  # además busca cada cifra en el .md
"""
from pathlib import Path
from math import sqrt
import contextlib, importlib.util, io, json, os, shutil, subprocess, sys, warnings

import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
DATOS, FIG, NB = RAMO / "datos", RAMO / "unidades" / "figuras", RAMO / "notebooks"
MD = RAMO / "unidades" / "12-inferencia-bayesiana.md"
CUADERNO = NB / "u12_bayesiano.ipynb"
SEMILLA = 1212  # Monte Carlo del caso (comparar dos proveedores)


# ---------------------------------------------------------------- formato a la chilena

def fmt(x, dec=1):
    s = f"{x:,.{dec}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return "0" + s[2:] if s.startswith("-0") and set(s[1:]) <= set("0,") else s


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def pesos(x):
    return "$" + fmt(x, 0)


def fila(*celdas):
    return "| " + " | ".join(celdas) + " |"


def cerca(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


# ---------------------------------------------------------------- fórmulas a mano

def beta_post(a, b, x, n):
    """Beta(a, b) a priori, x éxitos en n: posteriori y sus resúmenes a mano."""
    A, B = a + x, b + n - x
    media = A / (A + B)
    moda = (A - 1) / (A + B - 2)
    var = A * B / ((A + B) ** 2 * (A + B + 1))
    de = sqrt(var)
    return {"A": A, "B": B, "media": media, "moda": moda, "var": var, "de": de,
            "ic_aprox": (media - 1.96 * de, media + 1.96 * de)}


def beta_exacto(A, B, umbral=None, nivel=0.95):
    d = stats.beta(A, B)
    r = {"ic": (d.ppf((1 - nivel) / 2), d.ppf(1 - (1 - nivel) / 2))}
    if umbral is not None:
        r["p_sobre"] = d.sf(umbral)
    return r


def grilla_beta(a, b, x, n, puntos=200_001):
    """Segundo camino: priori × verosimilitud binomial en una grilla, normalizada."""
    t = np.linspace(0, 1, puntos)[1:-1]
    logp = stats.beta.logpdf(t, a, b) + x * np.log(t) + (n - x) * np.log1p(-t)
    w = np.exp(logp - logp.max()); w /= w.sum()
    return float((t * w).sum())


def normal_post(mu0, s0, sigma, n, xbar):
    """Normal-normal con σ conocida: precisiones, pesos y posteriori."""
    tau0, taud = 1 / s0 ** 2, n / sigma ** 2
    taun = tau0 + taud
    mun = (tau0 * mu0 + taud * xbar) / taun
    sn = sqrt(1 / taun)
    return {"tau0": tau0, "taud": taud, "taun": taun, "mun": mun, "var_n": 1 / taun, "sn": sn,
            "peso_datos": taud / taun, "peso_priori": tau0 / taun,
            "ic": (mun - 1.96 * sn, mun + 1.96 * sn),
            "ic_frec": (xbar - 1.96 * sigma / sqrt(n), xbar + 1.96 * sigma / sqrt(n)),
            "ee_frec": sigma / sqrt(n)}


def grilla_normal(mu0, s0, sigma, n, xbar):
    t = np.linspace(mu0 - 12 * s0, mu0 + 12 * s0, 400_001)
    logp = stats.norm.logpdf(t, mu0, s0) + stats.norm.logpdf(xbar, t, sigma / sqrt(n))
    w = np.exp(logp - logp.max()); w /= w.sum()
    m = float((t * w).sum())
    return m, float(sqrt(((t - m) ** 2 * w).sum()))


def discreta(valores, priori, x, n):
    ver = [stats.binom.pmf(x, n, v) for v in valores]
    conj = [p * l for p, l in zip(priori, ver)]
    g = sum(conj)
    post = [c / g for c in conj]
    return {"ver": ver, "conj": conj, "g": g, "post": post, "bayes": sum(v * p for v, p in zip(valores, post))}


# ---------------------------------------------------------------- datos (originales de esta base)

# Ejemplo A · cervecería: botellas con baja carbonatación. Priori de la historia: ~5 % con fuerza 60.
EJ_A = {"a": 3, "b": 57, "x": 9, "n": 120, "umbral": 0.08}
EJ_A_BAJAS = [7, 19, 33, 41, 58, 66, 87, 95, 112]   # números de botella con baja carbonatación
# Ejemplo B · llenado de botellas de 330 ml: priori de meses anteriores, σ del fabricante de la llenadora
EJ_B = {"mu0": 331.0, "s0": 0.8, "sigma": 1.8, "umbral": 330.0}
EJ_B_VOL = [331.2, 327.9, 330.4, 328.6, 332.1, 329.0, 326.8, 330.9,
            329.7, 328.3, 331.5, 330.2, 327.4, 329.9, 330.6, 329.1]

# 12.1 · lector de códigos: tasa de error 1 %, 4 % u 8 %
E1 = {"valores": [0.01, 0.04, 0.08], "priori": [0.45, 0.35, 0.20], "x": 3, "n": 40}
# 12.2 · priori por media y fuerza
E2 = {"media": 0.15, "fuerza": 40, "x": 11, "n": 50}
# 12.3 · media, moda y varianza
E3 = {"a": 2, "b": 2, "x": 7, "n": 20}
# 12.4 · tiempo de atención en caja (min)
E4 = {"mu0": 6.0, "s0": 0.5, "sigma": 2.0, "n": 25, "xbar": 6.8}
# 12.5 · conversión de una tienda nueva, priori plana
E5 = {"a": 1, "b": 1, "x": 3, "n": 40, "umbral": 0.05}
# 12.6 · sensibilidad a la priori
E6 = {"prioris": [(1, 1), (4, 36), (40, 360)], "x": 9, "n": 60, "umbral": 0.12}
# 12.7 · sacos de harina de 25 kg
E7 = {"mu0": 25.2, "s0": 0.15, "sigma": 0.4, "n": 12, "xbar": 25.05, "umbral": 25.0}
# 12.8 · camiones por hora en un andén: Gamma(α, β) con β tasa
E8 = {"alfa": 6, "beta": 2, "horas": 8, "total": 31, "umbral": 4.0}
# 12.9 · actualización en dos lotes y tamaño de muestra
E9 = {"a": 2, "b": 48, "lotes": [(4, 100), (7, 150)], "ancho": 0.04}
# 12.10 · factor de Bayes y decisión con pérdidas
E10 = {"a": 3, "b": 47, "x": 6, "n": 150, "corte": 0.05, "costo_aceptar_malo": 1_200_000,
       "costo_rechazar_bueno": 300_000}


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
    # --- ejemplo A
    a, b, x, n = EJ_A["a"], EJ_A["b"], EJ_A["x"], EJ_A["n"]
    assert len(EJ_A_BAJAS) == x
    pa = beta_post(a, b, x, n)
    ex = beta_exacto(pa["A"], pa["B"], EJ_A["umbral"])
    assert cerca(grilla_beta(a, b, x, n), pa["media"], 1e-6)
    pu = beta_post(1, 1, x, n); exu = beta_exacto(pu["A"], pu["B"], EJ_A["umbral"])
    ph = x / n; ee = sqrt(ph * (1 - ph) / n)
    R["ejA"] = {**pa, **ex, "media_priori": a / (a + b), "ph": ph, "ic_wald": (ph - 1.96 * ee, ph + 1.96 * ee),
                "plana": {**pu, **exu}, "peso_datos": n / (a + b + n),
                "p_sobre_priori": stats.beta(a, b).sf(EJ_A["umbral"])}
    # --- ejemplo B
    vol = EJ_B_VOL; nb = len(vol); xbar = float(np.mean(vol))
    pb = normal_post(EJ_B["mu0"], EJ_B["s0"], EJ_B["sigma"], nb, xbar)
    gm, gs = grilla_normal(EJ_B["mu0"], EJ_B["s0"], EJ_B["sigma"], nb, xbar)
    assert cerca(gm, pb["mun"], 1e-7) and cerca(gs, pb["sn"], 1e-5)
    p_bajo = stats.norm(pb["mun"], pb["sn"]).cdf(EJ_B["umbral"])
    ic_sc = stats.norm(pb["mun"], pb["sn"]).interval(0.95)
    assert cerca(ic_sc[0], pb["ic"][0], 1e-4) and cerca(ic_sc[1], pb["ic"][1], 1e-4)
    R["ejB"] = {**pb, "n": nb, "xbar": xbar, "s": float(np.std(vol, ddof=1)), "p_bajo": p_bajo,
                "z_bajo": (EJ_B["umbral"] - pb["mun"]) / pb["sn"], "p_bajo_priori": stats.norm(EJ_B["mu0"], EJ_B["s0"]).cdf(EJ_B["umbral"])}

    # --- ejercicios
    R["e1"] = discreta(E1["valores"], E1["priori"], E1["x"], E1["n"])
    a2 = E2["media"] * E2["fuerza"]; b2 = E2["fuerza"] - a2
    R["e2"] = {"a": a2, "b": b2, **beta_post(a2, b2, E2["x"], E2["n"]), "ph": E2["x"] / E2["n"]}
    R["e3"] = {**beta_post(E3["a"], E3["b"], E3["x"], E3["n"]), "ph": E3["x"] / E3["n"]}
    R["e4"] = normal_post(E4["mu0"], E4["s0"], E4["sigma"], E4["n"], E4["xbar"])
    p5 = beta_post(E5["a"], E5["b"], E5["x"], E5["n"])
    ex5 = beta_exacto(p5["A"], p5["B"], E5["umbral"])
    ph5 = E5["x"] / E5["n"]; ee5 = sqrt(ph5 * (1 - ph5) / E5["n"])
    R["e5"] = {**p5, **ex5, "ph": ph5, "ic_wald": (ph5 - 1.96 * ee5, ph5 + 1.96 * ee5)}
    R["e6"] = []
    for (aa, bb) in E6["prioris"]:
        q = beta_post(aa, bb, E6["x"], E6["n"])
        R["e6"].append({"a": aa, "b": bb, "media_pri": aa / (aa + bb), **q,
                        **beta_exacto(q["A"], q["B"], E6["umbral"]), "peso_datos": E6["n"] / (aa + bb + E6["n"])})
    p7 = normal_post(E7["mu0"], E7["s0"], E7["sigma"], E7["n"], E7["xbar"])
    R["e7"] = {**p7, "p_bajo": stats.norm(p7["mun"], p7["sn"]).cdf(E7["umbral"]),
               "p_bajo_priori": stats.norm(E7["mu0"], E7["s0"]).cdf(E7["umbral"])}
    A8, B8 = E8["alfa"] + E8["total"], E8["beta"] + E8["horas"]
    g8 = stats.gamma(A8, scale=1 / B8)
    t = np.linspace(1e-6, 15, 600_001)
    logp = stats.gamma.logpdf(t, E8["alfa"], scale=1 / E8["beta"]) + stats.poisson.logpmf(E8["total"], E8["horas"] * t)
    w = np.exp(logp - logp.max()); w /= w.sum()
    assert cerca(float((t * w).sum()), A8 / B8, 1e-6)
    R["e8"] = {"A": A8, "B": B8, "media_pri": E8["alfa"] / E8["beta"], "media": A8 / B8, "de": sqrt(A8) / B8,
               "ic": g8.interval(0.95), "p_sobre": g8.sf(E8["umbral"]), "mle": E8["total"] / E8["horas"],
               "p_sobre_pri": stats.gamma(E8["alfa"], scale=1 / E8["beta"]).sf(E8["umbral"])}
    a9, b9 = E9["a"], E9["b"]; pasos = []
    for (xx, nn) in E9["lotes"]:
        a9, b9 = a9 + xx, b9 + nn - xx
        pasos.append((a9, b9, a9 / (a9 + b9)))
    xt = sum(l[0] for l in E9["lotes"]); nt = sum(l[1] for l in E9["lotes"])
    junto = beta_post(E9["a"], E9["b"], xt, nt)
    assert (junto["A"], junto["B"]) == (a9, b9)
    ex9 = beta_exacto(a9, b9)
    th = junto["media"]
    # ancho 2 · 1,96 · √(θ(1−θ)/(a+b+N+1)) ≤ ancho  →  a + b + N + 1 ≥ θ(1−θ)(2·1,96/ancho)²
    tot = th * (1 - th) * (2 * 1.96 / E9["ancho"]) ** 2
    N_total = int(np.ceil(tot - 1 - E9["a"] - E9["b"]))
    R["e9"] = {"pasos": pasos, **junto, **ex9, "ancho_actual": ex9["ic"][1] - ex9["ic"][0],
               "ancho_aprox": 2 * 1.96 * junto["de"], "N_total": N_total, "N_mas": N_total - nt,
               "xt": xt, "nt": nt}
    p10 = beta_post(E10["a"], E10["b"], E10["x"], E10["n"])
    pri = stats.beta(E10["a"], E10["b"]); post = stats.beta(p10["A"], p10["B"])
    P0_pri, P0_post = pri.cdf(E10["corte"]), post.cdf(E10["corte"])
    odds_pri, odds_post = P0_pri / (1 - P0_pri), P0_post / (1 - P0_post)
    perd_acep = (1 - P0_post) * E10["costo_aceptar_malo"]
    perd_rech = P0_post * E10["costo_rechazar_bueno"]
    corte_p1 = E10["costo_rechazar_bueno"] / (E10["costo_rechazar_bueno"] + E10["costo_aceptar_malo"])
    R["e10"] = {**p10, "P0_pri": P0_pri, "P1_pri": 1 - P0_pri, "P0_post": P0_post, "P1_post": 1 - P0_post,
                "odds_pri": odds_pri, "odds_post": odds_post, "BF01": odds_post / odds_pri,
                "BF10": odds_pri / odds_post, "perd_acep": perd_acep, "perd_rech": perd_rech,
                "corte_p1": corte_p1, "ph": E10["x"] / E10["n"]}

    # --- caso
    caso, D = cargar_caso()
    d = D["defectos"].set_index("proveedor")
    k, nn = int(d.loc["Algodones Sur", "defectuosas"]), int(d.loc["Algodones Sur", "revisadas"])
    a0, b0 = 4, 76
    pc = beta_post(a0, b0, k, nn)
    exc = beta_exacto(pc["A"], pc["B"], 0.06)
    assert cerca(grilla_beta(a0, b0, k, nn), pc["media"], 1e-6)
    pu = beta_post(1, 1, k, nn); exu = beta_exacto(pu["A"], pu["B"], 0.06)
    ph = k / nn; ee = sqrt(ph * (1 - ph) / nn)
    kt, nt_ = int(d.loc["Telas Norte", "defectuosas"]), int(d.loc["Telas Norte", "revisadas"])
    ptn = beta_post(a0, b0, kt, nt_); extn = beta_exacto(ptn["A"], ptn["B"], 0.06)
    rng = np.random.default_rng(SEMILLA)
    m = 400_000
    sim_as = rng.beta(pc["A"], pc["B"], m); sim_tn = rng.beta(ptn["A"], ptn["B"], m)
    p_mc = float((sim_as > sim_tn).mean())
    # segundo camino: P(θ_AS > θ_TN) = ∫ f_AS(t) F_TN(t) dt, por integración numérica
    tt = np.linspace(0, 0.25, 500_001)
    p_int = float(np.trapezoid(stats.beta.pdf(tt, pc["A"], pc["B"]) * stats.beta.cdf(tt, ptn["A"], ptn["B"]), tt))
    assert abs(p_mc - p_int) < 0.002
    dif = sim_as - sim_tn
    R["caso"] = {**pc, **exc, "a0": a0, "b0": b0, "k": k, "n": nn, "media_pri": a0 / (a0 + b0),
                 "p_sobre_pri": stats.beta(a0, b0).sf(0.06), "ph": ph,
                 "ic_wald": (ph - 1.96 * ee, ph + 1.96 * ee), "plana": {**pu, **exu},
                 "peso_datos": nn / (a0 + b0 + nn), "tn": {**ptn, **extn, "k": kt, "n": nt_},
                 "p_as_mayor": p_int, "p_as_mayor_mc": p_mc,
                 "dif_ic": (float(np.quantile(dif, 0.025)), float(np.quantile(dif, 0.975)))}
    R["caso"]["p_homog_u3"] = caso.calcular(D)["u3"]["p_homog"]   # la prueba de la unidad 3, para contrastar
    R["_caso_mod"], R["_D"] = caso, D
    return R


# ---------------------------------------------------------------- datos del ejemplo, figuras y cuaderno

def escribir_datos():
    pd.DataFrame({"botella": range(1, EJ_A["n"] + 1),
                  "baja_carbonatacion": [1 if i in EJ_A_BAJAS else 0 for i in range(1, EJ_A["n"] + 1)]}) \
        .to_csv(DATOS / "u12_ejemplo_botellas.csv", index=False, encoding="utf-8")
    pd.DataFrame({"botella": range(1, len(EJ_B_VOL) + 1), "volumen_ml": EJ_B_VOL}) \
        .to_csv(DATOS / "u12_ejemplo_llenado.csv", index=False, encoding="utf-8")


AZUL, NARANJA, VERDE, TINTA, SUAVE, LINEA = "#2a78d6", "#eb6834", "#3a9a6a", "#2B2F33", "#52514e", "#D6D3CE"


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

    # ejemplo: priori, verosimilitud y posteriori (A) y normal-normal (B)
    e = R["ejA"]; b = R["ejB"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.1))
    t = np.linspace(0.0005, 0.2, 600)
    a1.plot(t, stats.beta.pdf(t, EJ_A["a"], EJ_A["b"]), color=SUAVE, ls="--", lw=1.6, label="priori Beta(3, 57)")
    a1.plot(t, stats.beta.pdf(t, EJ_A["x"] + 1, EJ_A["n"] - EJ_A["x"] + 1), color=AZUL, lw=1.6, label="verosimilitud (9 de 120)")
    a1.plot(t, stats.beta.pdf(t, e["A"], e["B"]), color=NARANJA, lw=2.2, label="posteriori Beta(12, 168)")
    a1.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.04))
    a1.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(pc))
    a1.set_xlabel("proporción con baja carbonatación"); a1.set_yticks([])
    a1.set_title("A · Beta-binomial", fontsize=9.5, loc="left"); a1.legend(frameon=False, fontsize=7); estilo(a1)
    m = np.linspace(326, 334, 600)
    a2.plot(m, stats.norm.pdf(m, EJ_B["mu0"], EJ_B["s0"]), color=SUAVE, ls="--", lw=1.6, label="priori N(331; 0,8²)")
    a2.plot(m, stats.norm.pdf(m, b["xbar"], b["ee_frec"]), color=AZUL, lw=1.6, label="verosimilitud de x̄")
    a2.plot(m, stats.norm.pdf(m, b["mun"], b["sn"]), color=NARANJA, lw=2.2, label="posteriori")
    a2.axvline(EJ_B["umbral"], color=TINTA, lw=.8, ls=":")
    a2.set_xlabel("volumen medio de llenado (ml)"); a2.set_yticks([])
    a2.set_title("B · Normal-normal", fontsize=9.5, loc="left"); a2.legend(frameon=False, fontsize=7); estilo(a2)
    fig.tight_layout(); fig.savefig(FIG / "u12_ejemplo.png", dpi=170); plt.close(fig)

    # caso: posteriori de Algodones Sur y de Telas Norte
    c = R["caso"]
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    t = np.linspace(0.01, 0.12, 800)
    ax.plot(t, stats.beta.pdf(t, c["a0"], c["b0"]), color=SUAVE, ls="--", lw=1.4, label="priori Beta(4, 76)")
    ax.plot(t, stats.beta.pdf(t, c["tn"]["A"], c["tn"]["B"]), color=AZUL, lw=1.8, label="posteriori Telas Norte")
    y = stats.beta.pdf(t, c["A"], c["B"])
    ax.plot(t, y, color=NARANJA, lw=2.2, label="posteriori Algodones Sur")
    sel = t >= 0.06
    ax.fill_between(t[sel], y[sel], color=NARANJA, alpha=.25, label=f"P(θ > 6 %) = {pct(c['p_sobre'], 1)}")
    for v in c["ic"]:
        ax.axvline(v, color=NARANJA, lw=.8, ls=":")
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.02))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(pc))
    ax.set_xlabel("tasa de prendas defectuosas"); ax.set_yticks([])
    ax.set_title("Estampa Sur · tasa de defecto por proveedor", fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=7.5); estilo(ax)
    fig.tight_layout(); fig.savefig(FIG / "u12_caso.png", dpi=170); plt.close(fig)


def ejecutar_cuaderno():
    """Ejecuta el cuaderno (nbconvert si está; si no, exec de sus celdas) y devuelve su RES."""
    nb = json.loads(CUADERNO.read_text(encoding="utf-8"))
    import matplotlib
    matplotlib.use("Agg")
    jup = shutil.which("jupyter")
    if jup:
        subprocess.run([jup, "nbconvert", "--to", "notebook", "--execute", "--stdout", str(CUADERNO)],
                       check=True, cwd=NB, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    previo = Path.cwd()
    os.chdir(NB)
    try:
        ns = {"__name__": "__cuaderno__"}
        with contextlib.redirect_stdout(io.StringIO()):
            for celda in nb["cells"]:
                if celda["cell_type"] == "code":
                    exec("".join(celda["source"]), ns)
    finally:
        os.chdir(previo)
    return ns["RES"]


def comparar_cuaderno(R, RES):
    a, b, c = R["ejA"], R["ejB"], R["caso"]
    pares = [("ej_media", a["media"]), ("ej_ic_inf", a["ic"][0]), ("ej_ic_sup", a["ic"][1]),
             ("ej_p_sobre", a["p_sobre"]), ("ej_mun", b["mun"]), ("ej_sn", b["sn"]), ("ej_p_bajo", b["p_bajo"]),
             ("caso_media", c["media"]), ("caso_ic_inf", c["ic"][0]), ("caso_ic_sup", c["ic"][1]),
             ("caso_p_sobre", c["p_sobre"])]
    malos = [k for k, v in pares if not cerca(RES[k], v, 1e-6)]
    if abs(RES["caso_p_as_mayor"] - c["p_as_mayor"]) > 0.002:
        malos.append("caso_p_as_mayor")
    print("CUADERNO:", "OK, reproduce el ejemplo y el caso" if not malos else f"difiere en {malos}")
    return not malos


def cadena(R):
    caso, D = R["_caso_mod"], R["_D"]
    C = caso.calcular(D)["u12"]
    c = R["caso"]
    ok = (list(C["priori"]) == [c["a0"], c["b0"]] and list(C["posteriori"]) == [c["A"], c["B"]]
          and cerca(C["media_post"], c["media"], 1e-12) and cerca(C["ic95"][0], c["ic"][0], 1e-12)
          and cerca(C["ic95"][1], c["ic"][1], 1e-12) and cerca(C["prob_sobre_6pct"], c["p_sobre"], 1e-12))
    J = json.loads((AQUI / "caso_estampa_sur_datos.json").read_text(encoding="utf-8"))["u12"]
    ok = ok and cerca(J["media_post"], c["media"], 1e-12) and cerca(J["prob_sobre_6pct"], c["p_sobre"], 1e-12)
    print("CADENA:", f"OK, la pieza u12 del caso calza (Beta({c['A']}, {c['B']}), media {pct(c['media'], 2)}, "
          f"P(θ > 6 %) = {pct(c['p_sobre'], 1)})" if ok else "NO calza")
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
    E += [", ".join(str(i) for i in EJ_A_BAJAS), "Beta(12, 168)", "Beta(10, 112)",
          pct(a["media_priori"], 1), pct(a["ph"], 1), fmt(a["media"], 4), pct(a["media"], 2), fmt(a["moda"], 4),
          pct(a["moda"], 2), fmt(a["var"] * 1e4, 3), fmt(a["de"], 4), pct(a["ic_aprox"][0], 2), pct(a["ic_aprox"][1], 2),
          pct(a["ic"][0], 2), pct(a["ic"][1], 2), pct(a["p_sobre"], 1), pct(a["p_sobre_priori"], 1),
          pct(a["ic_wald"][0], 2), pct(a["ic_wald"][1], 2), pct(a["plana"]["media"], 2),
          pct(a["plana"]["ic"][0], 2), pct(a["plana"]["ic"][1], 2), pct(a["plana"]["p_sobre"], 1),
          pct(a["peso_datos"], 0)]
    b = R["ejB"]
    E += ["; ".join(fmt(v, 1) for v in EJ_B_VOL), fmt(b["xbar"], 1), fmt(b["s"], 2), fmt(b["tau0"], 4),
          fmt(b["taud"], 4), fmt(b["taun"], 4), fmt(b["mun"], 2), fmt(b["var_n"], 4), fmt(b["sn"], 3),
          pct(b["peso_datos"], 1), pct(b["peso_priori"], 1), fmt(b["ic"][0], 2), fmt(b["ic"][1], 2),
          fmt(b["ic_frec"][0], 2), fmt(b["ic_frec"][1], 2), fmt(b["ee_frec"], 2), fmt(b["z_bajo"], 2),
          pct(b["p_bajo"], 1), pct(b["p_bajo_priori"], 1)]
    e1 = R["e1"]
    for v, p0, l, c_, p in zip(E1["valores"], E1["priori"], e1["ver"], e1["conj"], e1["post"]):
        E.append(fila(fmt(v, 2), fmt(p0, 2), fmt(l, 4), fmt(c_, 4), fmt(p, 3)))
    E += [fmt(e1["g"], 4), pct(e1["bayes"], 2)]
    e2 = R["e2"]
    E += [f"Beta({fmt(e2['a'], 0)}, {fmt(e2['b'], 0)})", f"Beta({fmt(e2['A'], 0)}, {fmt(e2['B'], 0)})",
          pct(e2["media"], 1), pct(e2["ph"], 1)]
    e3 = R["e3"]
    E += [f"Beta({e3['A']}, {e3['B']})", fmt(e3["media"], 3), fmt(e3["moda"], 3), fmt(e3["var"], 4), fmt(e3["de"], 3),
          fmt(e3["ph"], 2)]
    e4 = R["e4"]
    E += [fmt(e4["tau0"], 2), fmt(e4["taud"], 2), fmt(e4["taun"], 2), fmt(e4["mun"], 2), fmt(e4["sn"], 3),
          pct(e4["peso_datos"], 1), fmt(e4["ic"][0], 2), fmt(e4["ic"][1], 2)]
    e5 = R["e5"]
    E += [f"Beta({e5['A']}, {e5['B']})", pct(e5["media"], 2), pct(e5["ic"][0], 2), pct(e5["ic"][1], 2),
          pct(e5["ic_aprox"][0], 2), pct(e5["ic_aprox"][1], 2), pct(e5["ic_wald"][0], 2), pct(e5["ic_wald"][1], 2),
          pct(e5["p_sobre"], 1)]
    for q in R["e6"]:
        E.append(fila(f"Beta({q['a']}, {q['b']})", pct(q["media_pri"], 1), f"Beta({q['A']}, {q['B']})",
                      pct(q["media"], 2), f"{pct(q['ic'][0], 1)} a {pct(q['ic'][1], 1)}", pct(q["p_sobre"], 1),
                      pct(q["peso_datos"], 0)))
    e7 = R["e7"]
    E += [fmt(e7["mun"], 3), fmt(e7["sn"], 3), pct(e7["peso_datos"], 1), fmt(e7["ic"][0], 2), fmt(e7["ic"][1], 2),
          fmt(e7["ic_frec"][0], 2), fmt(e7["ic_frec"][1], 2), pct(e7["p_bajo"], 1), pct(e7["p_bajo_priori"], 1)]
    e8 = R["e8"]
    E += [f"Gamma({e8['A']}, {e8['B']})", fmt(e8["media_pri"], 1), fmt(e8["media"], 2), fmt(e8["de"], 3),
          fmt(e8["ic"][0], 2), fmt(e8["ic"][1], 2), pct(e8["p_sobre"], 1), fmt(e8["mle"], 3), pct(e8["p_sobre_pri"], 1)]
    e9 = R["e9"]
    E += [f"Beta({p[0]}, {p[1]})" for p in e9["pasos"]] + [pct(p[2], 2) for p in e9["pasos"]]
    E += [pct(e9["ic"][0], 2), pct(e9["ic"][1], 2), fmt(100 * e9["ancho_actual"], 2), fmt(100 * e9["ancho_aprox"], 2),
          fmt(e9["N_total"], 0), fmt(e9["N_mas"], 0), f"{e9['xt']} de {e9['nt']}"]
    e10 = R["e10"]
    E += [f"Beta({e10['A']}, {e10['B']})", fmt(e10["P0_pri"], 3), fmt(e10["P1_pri"], 3), fmt(e10["P0_post"], 3),
          fmt(e10["P1_post"], 3), fmt(e10["odds_pri"], 3), fmt(e10["odds_post"], 3), fmt(e10["BF01"], 2),
          pesos(e10["perd_acep"]), pesos(e10["perd_rech"]), fmt(e10["corte_p1"], 2)]
    c = R["caso"]
    E += [f"{c['k']}/{c['n']}", f"Beta({c['A']}, {c['B']})", pct(c["media_pri"], 1), pct(c["p_sobre_pri"], 1),
          f"{c['A']}/{c['A'] + c['B']}", pct(c["media"], 2), pct(c["moda"], 2), fmt(c["de"] * 100, 2),
          pct(c["ic"][0], 2), pct(c["ic"][1], 2), pct(c["ic_aprox"][0], 2), pct(c["ic_aprox"][1], 2),
          pct(c["p_sobre"], 1), pct(c["ph"], 2), pct(c["ic_wald"][0], 2), pct(c["ic_wald"][1], 2),
          f"Beta({c['plana']['A']}, {c['plana']['B']})", pct(c["plana"]["media"], 2), pct(c["plana"]["p_sobre"], 1),
          pct(c["peso_datos"], 1), f"{c['tn']['k']}/{c['tn']['n']}", f"Beta({c['tn']['A']}, {c['tn']['B']})",
          pct(c["tn"]["media"], 2), pct(c["tn"]["p_sobre"], 1), pct(c["p_as_mayor"], 1),
          f"{fmt(100 * c['dif_ic'][0], 1)} y {fmt(100 * c['dif_ic'][1], 1)}", f"p = {fmt(c['p_homog_u3'], 3)}"]
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
