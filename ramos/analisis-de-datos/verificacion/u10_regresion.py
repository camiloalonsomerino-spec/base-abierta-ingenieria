"""Unidad 10 · Regresión lineal múltiple y diagnóstico.

Recalcula todas las cifras de la unidad desde los datos (con las fórmulas matriciales y con statsmodels,
y exige que coincidan), genera el gráfico de residuos del caso en `unidades/figuras/` y el CSV del
ejemplo en `datos/`, ejecuta el cuaderno `notebooks/u10_regresion.ipynb`, compara la pieza del caso con
`caso_estampa_sur_datos.py` y, con --revisar, busca cada cifra en el .md.

    python u10_regresion.py            # imprime los resultados
    python u10_regresion.py --revisar  # además los busca en el .md
"""
from pathlib import Path
import importlib.util, io, json, os, sys, contextlib, warnings

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
DATOS = RAMO / "datos"
FIG = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "10-regresion-multiple.md"
CUADERNO = RAMO / "notebooks" / "u10_regresion.ipynb"


def fmt(x, dec=1):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fp(p, dec=3):
    return "p < 0,001" if p < 0.001 else f"p = {fmt(p, dec)}"


def mco(X, y):
    """Mínimos cuadrados con las fórmulas de la unidad. X ya trae la columna de unos."""
    n, k = X.shape                       # k = p + 1
    XtX, Xty = X.T @ X, X.T @ y
    inv = np.linalg.inv(XtX)
    b = inv @ Xty
    yhat = X @ b
    e = y - yhat
    sce = float(e @ e)
    sct = float(((y - y.mean()) ** 2).sum())
    scr = sct - sce
    gl_e = n - k
    mce = sce / gl_e
    se = np.sqrt(mce * np.diag(inv))
    t = b / se
    p = 2 * stats.t.sf(np.abs(t), gl_e)
    F = (scr / (k - 1)) / mce
    tc = float(stats.t.ppf(0.975, gl_e))
    return {"n": n, "k": k, "XtX": XtX, "Xty": Xty, "inv": inv, "b": b, "yhat": yhat, "e": e, "SCE": sce, "SCT": sct,
            "SCR": scr, "glE": gl_e, "MCE": mce, "se": se, "t": t, "p": p, "F": F, "pF": float(stats.f.sf(F, k - 1, gl_e)),
            "R2": scr / sct, "R2a": 1 - (sce / gl_e) / (sct / (n - 1)), "tc": tc,
            "ic": np.c_[b - tc * se, b + tc * se], "h": np.einsum("ij,jk,ik->i", X, inv, X)}


def prediccion(M, x0):
    x0 = np.asarray(x0, float)
    y0 = float(x0 @ M["b"])
    h0 = float(x0 @ M["inv"] @ x0)
    a_media = M["tc"] * np.sqrt(M["MCE"] * h0)
    a_pred = M["tc"] * np.sqrt(M["MCE"] * (1 + h0))
    return {"y0": y0, "h0": h0, "ic": (y0 - a_media, y0 + a_media), "ip": (y0 - a_pred, y0 + a_pred),
            "a_media": a_media, "a_pred": a_pred}


def igual_sm(M, mod):
    assert np.allclose(M["b"], mod.params.values) and np.allclose(M["se"], mod.bse.values)
    assert abs(M["R2"] - mod.rsquared) < 1e-12 and abs(M["F"] - mod.fvalue) < 1e-8


# ---------------------------------------------------------------- datos (originales; pasados por herramientas/colisiones.py)

# Ejemplo · ferretería de Los Ángeles: minutos de despacho de 8 pedidos según bultos y km al cliente
EJ = pd.DataFrame({"bultos": [2, 5, 3, 8, 4, 6, 1, 7], "km": [4, 6, 10, 3, 8, 12, 7, 9],
                   "minutos": [20, 27, 35, 28, 30, 44, 23, 39]})
EJ_X0 = [1, 5, 8]          # un pedido nuevo: 5 bultos a 8 km

# 10.1 y 10.6 · reparto en Temuco: costo del viaje (miles de $) según km y paradas
E1 = pd.DataFrame({"km": [12, 25, 8, 30, 18, 22], "paradas": [3, 5, 2, 4, 6, 3], "costo": [14, 26, 10, 27, 24, 21]})
E6_X0 = [1, 20, 4]

# 10.2 · consumo eléctrico de una planta: n = 25, p = 3
E2 = {"n": 25, "p": 3, "SCT": 840.0, "SCE": 210.0}

# 10.3 · precio de departamentos en Concepción (millones de $), n = 40, p = 3
E3 = {"n": 40, "coef": {"constante": (35.6, 12.4), "m²": (1.82, 0.21), "distancia": (-3.40, 1.05), "antigüedad": (-0.26, 0.19)}}

# 10.4 · días de entrega = 1,6 + 0,012·km + 1,3·(courier B) − 0,9·(express)
E4 = {"b": [1.6, 0.012, 1.3, -0.9], "x0": [1, 300, 1, 1]}

# 10.5 · heladería: ventas diarias (litros), precio por litro ($) y temperatura máxima (°C)
E5 = pd.DataFrame({"temp": [18, 22, 25, 28, 30, 33, 20, 27], "precio": [1800, 1900, 2000, 2100, 2200, 2300, 2000, 1900],
                   "litros": [40, 55, 71, 82, 92, 101, 42, 86]})

# 10.7 · consumo mensual (kWh) de 10 locales según superficie (m²) y equipos de frío
E7 = pd.DataFrame({"sup": [82, 96, 108, 123, 137, 148, 163, 171, 192, 207], "equipos": [3, 4, 4, 5, 5, 6, 6, 7, 8, 8],
                   "kwh": [1255, 1348, 1527, 1586, 1763, 1838, 1994, 2057, 2334, 2378]})

# 10.8 · gasto anual de mantención (miles de $) de 12 camiones según kilometraje (miles de km)
E8 = pd.DataFrame({"km": [20, 35, 50, 60, 75, 90, 100, 120, 140, 160, 180, 200],
                   "gasto": [455, 590, 680, 820, 860, 1110, 1010, 1390, 1290, 1790, 1500, 2190]})

# 10.9 · horas de capacitación y piezas por hora de 10 operarios
E9 = pd.DataFrame({"horas": [2, 3, 4, 5, 6, 7, 8, 9, 10, 30], "piezas": [41, 43, 44, 47, 48, 50, 51, 53, 55, 52]})

# 10.10 · los datos del ejemplo de la unidad 9 (impresión 3D)
E10 = {("PLA", "horizontal"): [44, 48, 46], ("PLA", "vertical"): [31, 28, 31],
       ("PETG", "horizontal"): [51, 54, 51], ("PETG", "vertical"): [45, 44, 43]}

CASO_X0 = {"precio": 11_500, "publicidad": 100_000}


def cargar_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_datos.py")
    caso = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caso)
    return caso


def matriz(df, cols):
    return np.column_stack([np.ones(len(df))] + [df[c].to_numpy(float) for c in cols])


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # Ejemplo
    X = matriz(EJ, ["bultos", "km"]); y = EJ.minutos.to_numpy(float)
    M = mco(X, y)
    mod = smf.ols("minutos ~ bultos + km", data=EJ).fit()
    igual_sm(M, mod)
    P = prediccion(M, EJ_X0)
    sf = mod.get_prediction(pd.DataFrame({"bultos": [EJ_X0[1]], "km": [EJ_X0[2]]})).summary_frame(0.05)
    assert abs(sf.mean_ci_lower[0] - P["ic"][0]) < 1e-9 and abs(sf.obs_ci_upper[0] - P["ip"][1]) < 1e-9
    r12 = float(np.corrcoef(EJ.bultos, EJ.km)[0, 1])
    # residuos ortogonales a las columnas de X (segundo camino)
    assert np.allclose(X.T @ M["e"], 0)
    R["ej"] = {"M": M, "P": P, "r12": r12, "vif": 1 / (1 - r12 ** 2), "sh": stats.shapiro(M["e"]),
               "hmax": float(M["h"].max()), "hmax_i": int(M["h"].argmax()) + 1, "corte_h": 2 * M["k"] / M["n"],
               "r_std": M["e"] / np.sqrt(M["MCE"])}

    # 10.1
    X1 = matriz(E1, ["km", "paradas"]); y1 = E1.costo.to_numpy(float)
    M1 = mco(X1, y1)
    inv_red = np.round(M1["inv"], 5)
    b_red = inv_red @ M1["Xty"]
    # la inversa redondeada a 5 decimales ya mueve el coeficiente de km (X'y tiene números grandes)
    assert round(b_red[1], 2) != round(M1["b"][1], 2)
    R["e1"] = {"M": M1, "inv_red": inv_red, "b_red": b_red}

    # 10.2
    e = dict(E2)
    e["SCR"] = e["SCT"] - e["SCE"]; e["glE"] = e["n"] - e["p"] - 1
    e["MCR"] = e["SCR"] / e["p"]; e["MCE"] = e["SCE"] / e["glE"]; e["F"] = e["MCR"] / e["MCE"]
    e["pF"] = float(stats.f.sf(e["F"], e["p"], e["glE"])); e["Fc"] = float(stats.f.ppf(0.95, e["p"], e["glE"]))
    e["R2"] = e["SCR"] / e["SCT"]; e["R2a"] = 1 - e["MCE"] / (e["SCT"] / (e["n"] - 1))
    R["e2"] = e

    # 10.3
    gl3 = E3["n"] - 3 - 1
    tc3 = float(stats.t.ppf(0.975, gl3))
    R["e3"] = {"gl": gl3, "tc": tc3, "fil": {k: {"t": b / s, "p": float(2 * stats.t.sf(abs(b / s), gl3)), "ic": (b - tc3 * s, b + tc3 * s)}
                                             for k, (b, s) in E3["coef"].items()}}

    # 10.4
    R["e4"] = {"y0": float(np.dot(E4["b"], E4["x0"]))}

    # 10.5
    s5 = smf.ols("litros ~ precio", data=E5).fit()
    m5 = smf.ols("litros ~ precio + temp", data=E5).fit()
    R["e5"] = {"simple": s5, "mult": m5, "r": float(np.corrcoef(E5.precio, E5.temp)[0, 1]),
               "sesgo": float(s5.params["precio"] - m5.params["precio"])}

    # 10.6 (con el modelo del 10.1)
    R["e6"] = prediccion(M1, E6_X0)
    R["e6"]["tc"] = M1["tc"]

    # 10.7
    m7 = smf.ols("kwh ~ sup + equipos", data=E7).fit()
    X7 = m7.model.exog
    vif7 = [variance_inflation_factor(X7, i) for i in (1, 2)]
    r7 = float(np.corrcoef(E7.sup, E7.equipos)[0, 1])
    assert abs(vif7[0] - 1 / (1 - r7 ** 2)) < 1e-9
    solo_eq = smf.ols("kwh ~ equipos", data=E7).fit()
    solo_sup = smf.ols("kwh ~ sup", data=E7).fit()
    R["e7"] = {"m": m7, "vif": vif7, "r": r7, "solo_eq": solo_eq, "solo_sup": solo_sup}

    # 10.8
    m8 = smf.ols("gasto ~ km", data=E8).fit()
    bp8 = het_breuschpagan(m8.resid, m8.model.exog)
    E8l = E8.assign(lgasto=np.log(E8.gasto))
    m8l = smf.ols("lgasto ~ km", data=E8l).fit()
    bp8l = het_breuschpagan(m8l.resid, m8l.model.exog)
    hc3 = m8.get_robustcov_results(cov_type="HC3")
    R["e8"] = {"m": m8, "bp": bp8, "ml": m8l, "bpl": bp8l, "se_hc3": float(hc3.bse[1]),
               "pct": float(np.exp(m8l.params["km"] * 10) - 1)}

    # 10.9
    m9 = smf.ols("piezas ~ horas", data=E9).fit()
    inf9 = m9.get_influence()
    h9 = inf9.hat_matrix_diag
    # segundo camino: palanca en regresión simple, h = 1/n + (x - x̄)²/Sxx
    xx = E9.horas.to_numpy(float)
    assert np.allclose(h9, 1 / len(xx) + (xx - xx.mean()) ** 2 / ((xx - xx.mean()) ** 2).sum())
    m9b = smf.ols("piezas ~ horas", data=E9.iloc[:-1]).fit()
    R["e9"] = {"m": m9, "h": h9, "cook": inf9.cooks_distance[0], "rst": inf9.resid_studentized_external, "sin": m9b,
               "corte_h": 2 * 2 / len(E9), "corte_c": 4 / len(E9)}

    # 10.10
    df10 = pd.DataFrame([{"material": i, "orientacion": j, "y": v} for (i, j), vs in E10.items() for v in vs])
    df10["petg"] = (df10.material == "PETG").astype(float)
    df10["vert"] = (df10.orientacion == "vertical").astype(float)
    df10["pv"] = df10.petg * df10.vert
    M10 = mco(matriz(df10, ["petg", "vert", "pv"]), df10.y.to_numpy(float))
    M10r = mco(matriz(df10, ["petg", "vert"]), df10.y.to_numpy(float))
    F_parcial = (M10r["SCE"] - M10["SCE"]) / (M10["MCE"])
    an = sm.stats.anova_lm(smf.ols("y ~ C(material) * C(orientacion)", data=df10).fit(), typ=2)
    assert abs(F_parcial - an.loc["C(material):C(orientacion)", "F"]) < 1e-9
    assert abs(M10["SCR"] - an["sum_sq"].iloc[:3].sum()) < 1e-9
    R["e10"] = {"M": M10, "Mr": M10r, "F": F_parcial, "p": float(stats.f.sf(F_parcial, 1, M10["glE"]))}

    # Caso · ventas semanales (datos/ventas.csv)
    v = pd.read_csv(DATOS / "ventas.csv")
    Xc = matriz(v, ["precio", "publicidad"]); yc = v.unidades.to_numpy(float)
    Mc = mco(Xc, yc)
    modc = smf.ols("unidades ~ precio + publicidad", data=v).fit()
    igual_sm(Mc, modc)
    Pc = prediccion(Mc, [1, CASO_X0["precio"], CASO_X0["publicidad"]])
    infc = modc.get_influence()
    cook = infc.cooks_distance[0]
    i_cook = int(cook.argmax())
    sin_c = smf.ols("unidades ~ precio + publicidad", data=v.drop(index=i_cook)).fit()
    glm = smf.glm("unidades ~ precio + publicidad", data=v, family=sm.families.Gaussian()).fit()
    assert np.allclose(glm.params.values, modc.params.values) and abs(glm.deviance - Mc["SCE"]) < 1e-6
    simple = smf.ols("unidades ~ precio", data=v).fit()
    rst = infc.resid_studentized_external
    R["caso"] = {"v": v, "M": Mc, "mod": modc, "P": Pc, "sh": stats.shapiro(modc.resid), "bp": het_breuschpagan(modc.resid, modc.model.exog),
                 "dw": float(durbin_watson(modc.resid)), "r12": float(np.corrcoef(v.precio, v.publicidad)[0, 1]),
                 "vif": float(variance_inflation_factor(modc.model.exog, 1)), "h": infc.hat_matrix_diag, "cook": cook, "i_cook": i_cook,
                 "rst": rst, "i_rst": int(np.abs(rst).argmax()), "sin": sin_c, "glm": glm, "simple": simple,
                 "corte_h": 2 * 3 / len(v), "corte_c": 4 / len(v),
                 "pub10": float(modc.params["publicidad"] * 10_000), "precio1000": float(modc.params["precio"] * 1_000),
                 "margen_eq": float(10_000 / (modc.params["publicidad"] * 10_000))}
    return R


# ---------------------------------------------------------------- CSV, figura, cuaderno, cadena

def escribir_csv():
    EJ.to_csv(DATOS / "u10_ejemplo.csv", index=False, encoding="utf-8")


def graficos(R):
    FIG.mkdir(parents=True, exist_ok=True)
    c = R["caso"]; mod = c["mod"]
    fig, ax = plt.subplots(1, 3, figsize=(9.6, 3.0), dpi=150)
    ax[0].scatter(mod.fittedvalues, mod.resid, color="#2B2F33", s=14); ax[0].axhline(0, color="#E2622A", lw=1)
    ax[0].set_xlabel("unidades ajustadas"); ax[0].set_ylabel("residuo (unidades)"); ax[0].set_title("Frente a ajustados", fontsize=10)
    (osm, osr), (pend, inter, _) = stats.probplot(mod.resid, dist="norm")
    ax[1].scatter(osm, osr, color="#2B2F33", s=14); ax[1].plot(osm, pend * np.array(osm) + inter, color="#E2622A", lw=1)
    ax[1].set_xlabel("cuantil normal teórico"); ax[1].set_ylabel("residuo ordenado"); ax[1].set_title("Cuantil-cuantil", fontsize=10)
    ax[2].plot(c["v"].semana, mod.resid, color="#2B2F33", marker="o", ms=3, lw=0.8); ax[2].axhline(0, color="#E2622A", lw=1)
    ax[2].set_xlabel("semana"); ax[2].set_ylabel("residuo"); ax[2].set_title("En el tiempo", fontsize=10)
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / "u10_residuos_caso.png"); plt.close(fig)


def ejecutar_cuaderno():
    nb = json.loads(CUADERNO.read_text(encoding="utf-8"))
    ns = {"__name__": "__cuaderno__"}
    previo = os.getcwd(); os.chdir(CUADERNO.parent)
    try:
        with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for celda in nb["cells"]:
                if celda["cell_type"] == "code":
                    exec("".join(celda["source"]), ns)
    finally:
        os.chdir(previo); plt.close("all")
    return ns


def comparar_cuaderno(R, ns):
    ok = np.allclose(ns["beta_ejemplo"], R["ej"]["M"]["b"])
    ok &= np.allclose(ns["modelo_caso"].params.values, R["caso"]["M"]["b"])
    pc = ns["prediccion_caso"]
    ok &= abs(pc.obs_ci_lower.iloc[0] - R["caso"]["P"]["ip"][0]) < 1e-9 and abs(pc["mean"].iloc[0] - R["caso"]["P"]["y0"]) < 1e-9
    ok &= abs(ns["vif_caso"] - R["caso"]["vif"]) < 1e-9
    print("CUADERNO:", "OK, reproduce el ejemplo y el caso" if ok else "NO coincide")
    return bool(ok)


def cadena(R):
    caso = cargar_caso()
    D = caso.generar()
    C = caso.calcular(D)["u10"]
    v = R["caso"]["v"]
    ok = np.allclose(D["ventas"][["precio", "publicidad", "unidades"]].values, v[["precio", "publicidad", "unidades"]].values)
    b = R["caso"]["mod"].params
    ok &= abs(C["coef"]["Intercept"] - b["Intercept"]) < 1e-5 and abs(C["coef"]["precio"] - b["precio"]) < 1e-6
    ok &= abs(C["coef"]["publicidad"] - b["publicidad"]) < 1e-6
    ok &= abs(C["r2"] - R["caso"]["M"]["R2"]) < 1e-12 and abs(C["r2_aj"] - R["caso"]["M"]["R2a"]) < 1e-12
    print("CADENA:", "OK, la pieza del caso calza con caso_estampa_sur_datos.py" if ok else "NO calza")
    return bool(ok)


# ---------------------------------------------------------------- impresión y revisión

def imprimir(R):
    M = R["ej"]["M"]; P = R["ej"]["P"]
    print("== Ejemplo")
    print("  XtX", M["XtX"].tolist(), "Xty", M["Xty"].tolist())
    print("  inv", [[fmt(x, 5) for x in fila] for fila in M["inv"]])
    print("  b", [fmt(x, 4) for x in M["b"]], "se", [fmt(x, 4) for x in M["se"]], "t", [fmt(x, 2) for x in M["t"]], "p", [fp(x) for x in M["p"]])
    print("  yhat", [fmt(x, 2) for x in M["yhat"]], "e", [fmt(x, 2) for x in M["e"]])
    print("  SCE", fmt(M["SCE"], 3), "SCT", fmt(M["SCT"], 3), "SCR", fmt(M["SCR"], 3), "MCE", fmt(M["MCE"], 4), "F", fmt(M["F"], 2), fp(M["pF"]),
          "R2", fmt(M["R2"], 4), "R2a", fmt(M["R2a"], 4), "tc", fmt(M["tc"], 3), "ic", [[fmt(a, 2), fmt(b, 2)] for a, b in M["ic"]])
    print("  pred", fmt(P["y0"], 2), "h0", fmt(P["h0"], 4), "IC", fmt(P["ic"][0], 2), fmt(P["ic"][1], 2), "IP", fmt(P["ip"][0], 2), fmt(P["ip"][1], 2))
    e = R["ej"]; print("  r12", fmt(e["r12"], 3), "VIF", fmt(e["vif"], 3), "Shapiro", fp(e["sh"].pvalue), "hmax", fmt(e["hmax"], 3), e["hmax_i"], "corte", fmt(e["corte_h"], 2),
                      "rstd", [fmt(x, 2) for x in e["r_std"]])
    M1 = R["e1"]["M"]
    print("== 10.1 XtX", M1["XtX"].tolist(), "Xty", M1["Xty"].tolist(), "inv red", R["e1"]["inv_red"].tolist())
    print("  b", [fmt(x, 3) for x in M1["b"]], "b con inversa redondeada", [fmt(x, 3) for x in R["e1"]["b_red"]], "R2", fmt(M1["R2"], 4), "MCE", fmt(M1["MCE"], 4))
    e = R["e2"]; print("== 10.2", {k: fmt(v, 4) if isinstance(v, float) else v for k, v in e.items()}, fp(e["pF"]))
    e = R["e3"]; print("== 10.3 gl", e["gl"], "tc", fmt(e["tc"], 3), {k: (fmt(v["t"], 2), fp(v["p"]), fmt(v["ic"][0], 2), fmt(v["ic"][1], 2)) for k, v in e["fil"].items()})
    print("== 10.4", fmt(R["e4"]["y0"], 1))
    e = R["e5"]; print("== 10.5 simple", {k: fmt(v, 4) for k, v in e["simple"].params.items()}, fp(e["simple"].pvalues["precio"]),
                      "mult", {k: fmt(v, 4) for k, v in e["mult"].params.items()}, {k: fp(v) for k, v in e["mult"].pvalues.items()}, "r", fmt(e["r"], 3),
                      "R2 mult", fmt(e["mult"].rsquared, 3), "R2 simple", fmt(e["simple"].rsquared, 3))
    e = R["e6"]; print("== 10.6 y0", fmt(e["y0"], 2), "h0", fmt(e["h0"], 4), "tc", fmt(e["tc"], 3), "IC", fmt(e["ic"][0], 2), fmt(e["ic"][1], 2), "IP", fmt(e["ip"][0], 2), fmt(e["ip"][1], 2))
    e = R["e7"]; m = e["m"]
    print("== 10.7", {k: fmt(v, 2) for k, v in m.params.items()}, "se", {k: fmt(v, 2) for k, v in m.bse.items()}, {k: fp(v) for k, v in m.pvalues.items()},
          "F", fmt(m.fvalue, 1), fp(m.f_pvalue), "R2", fmt(m.rsquared, 3), "r", fmt(e["r"], 3), "VIF", [fmt(x, 1) for x in e["vif"]],
          "solo eq", {k: fmt(v, 2) for k, v in e["solo_eq"].params.items()}, fp(e["solo_eq"].pvalues["equipos"]), "R2", fmt(e["solo_eq"].rsquared, 3),
          "solo sup R2", fmt(e["solo_sup"].rsquared, 3), {k: fmt(v, 2) for k, v in e["solo_sup"].params.items()})
    e = R["e8"]; print("== 10.8", {k: fmt(v, 3) for k, v in e["m"].params.items()}, "se", fmt(e["m"].bse["km"], 3), "HC3", fmt(e["se_hc3"], 3), "BP", fmt(e["bp"][0], 2), fp(e["bp"][1]),
                      "log", {k: fmt(v, 5) for k, v in e["ml"].params.items()}, "BP log", fmt(e["bpl"][0], 2), fp(e["bpl"][1]), "pct10", fmt(100 * e["pct"], 1))
    e = R["e9"]; print("== 10.9", {k: fmt(v, 3) for k, v in e["m"].params.items()}, "h10", fmt(e["h"][-1], 3), "cook10", fmt(e["cook"][-1], 1), "rst10", fmt(e["rst"][-1], 1),
                      "cortes", fmt(e["corte_h"], 2), fmt(e["corte_c"], 2), "sin", {k: fmt(v, 3) for k, v in e["sin"].params.items()}, "R2", fmt(e["m"].rsquared, 3), fmt(e["sin"].rsquared, 3),
                      "cook max otros", fmt(e["cook"][:-1].max(), 2), "h max otros", fmt(e["h"][:-1].max(), 3))
    e = R["e10"]; print("== 10.10 b", [fmt(x, 0) for x in e["M"]["b"]], "SCR", fmt(e["M"]["SCR"], 0), "SCE", fmt(e["M"]["SCE"], 0), "F", fmt(e["M"]["F"], 2), "R2", fmt(e["M"]["R2"], 4),
                       "SCE red", fmt(e["Mr"]["SCE"], 0), "Fparcial", fmt(e["F"], 2), fp(e["p"]), "MCE", fmt(e["M"]["MCE"], 2))
    c = R["caso"]; M = c["M"]; P = c["P"]
    print("== Caso b", [fmt(x, 6) for x in M["b"]], "se", [fmt(x, 6) for x in M["se"]], "t", [fmt(x, 2) for x in M["t"]], "p", [fp(x) for x in M["p"]])
    print("  ic", [[fmt(a, 5), fmt(b, 5)] for a, b in M["ic"]], "SCR", fmt(M["SCR"], 0), "SCE", fmt(M["SCE"], 0), "SCT", fmt(M["SCT"], 0), "MCE", fmt(M["MCE"], 1),
          "s", fmt(np.sqrt(M["MCE"]), 1), "F", fmt(M["F"], 2), fp(M["pF"]), "R2", fmt(M["R2"], 3), "R2a", fmt(M["R2a"], 3), "tc", fmt(M["tc"], 3))
    print("  pred", fmt(P["y0"], 1), "h0", fmt(P["h0"], 4), "IC", fmt(P["ic"][0], 1), fmt(P["ic"][1], 1), "IP", fmt(P["ip"][0], 1), fmt(P["ip"][1], 1))
    print("  Shapiro", fmt(c["sh"].statistic, 3), fp(c["sh"].pvalue), "BP", fmt(c["bp"][0], 2), fp(c["bp"][1]), "DW", fmt(c["dw"], 2), "r12", fmt(c["r12"], 3), "VIF", fmt(c["vif"], 2))
    print("  hmax", fmt(c["h"].max(), 3), int(c["h"].argmax()) + 1, "corte h", fmt(c["corte_h"], 2), "cook max", fmt(c["cook"].max(), 2), "semana", c["i_cook"] + 1, "corte c", fmt(c["corte_c"], 2),
          "rst max", fmt(c["rst"][c["i_rst"]], 2), "semana", c["i_rst"] + 1, "n cook>4/n", int((c["cook"] > c["corte_c"]).sum()))
    print("  sin semana cook:", {k: fmt(v, 5) for k, v in c["sin"].params.items()}, "R2", fmt(c["sin"].rsquared, 3))
    print("  simple", {k: fmt(v, 4) for k, v in c["simple"].params.items()}, "pub10", fmt(c["pub10"], 2), "precio1000", fmt(c["precio1000"], 2), "margen", fmt(c["margen_eq"], 0))


def fila(*c):
    return "| " + " | ".join(c) + " |"


def esperados(R):
    e = []
    M = R["ej"]["M"]; P = R["ej"]["P"]
    e += [fila(str(i + 1), str(r.bultos), str(r.km), str(r.minutos)) for i, r in EJ.iterrows()]
    e += [fmt(x, 5) for x in M["inv"].ravel()]
    e += [fmt(x, 3) for x in M["b"]] + [fmt(x, 3) for x in M["se"]] + [fmt(x, 2) for x in M["t"]]
    e += [fmt(M["SCE"], 2), fmt(M["SCT"], 1), fmt(M["SCR"], 2), fmt(M["MCE"], 3), fmt(M["F"], 2), fp(M["pF"]), fmt(M["R2"], 3), fmt(M["R2a"], 3), fmt(M["tc"], 3)]
    e += [fmt(v, 2) for ab in M["ic"][1:] for v in ab]
    e += [fmt(P["y0"], 2), fmt(P["h0"], 4), fmt(P["ic"][0], 2), fmt(P["ic"][1], 2), fmt(P["ip"][0], 2), fmt(P["ip"][1], 2)]
    e += [fmt(R["ej"]["r12"], 2), fmt(R["ej"]["vif"], 2), fmt(R["ej"]["hmax"], 2), fmt(R["ej"]["corte_h"], 2)]
    e += [fmt(x, 2) for x in M["yhat"]] + [fmt(x, 2) for x in M["e"]]
    # 10.1
    x = R["e1"]
    e += [fila(str(r.km), str(r.paradas), str(r.costo)) for _, r in E1.iterrows()]
    e += [fmt(v, 5) for v in x["inv_red"].ravel()] + [fmt(v, 0) for v in x["M"]["Xty"]] + [fmt(v, 2) for v in x["M"]["b"]]
    e += [fmt(v, 0) for v in x["M"]["XtX"].ravel()] + [fmt(x["b_red"][1], 2), fmt(x["M"]["R2"], 3)]
    # 10.2
    x = R["e2"]
    e += [fmt(x["SCR"], 0), fmt(x["MCR"], 0), fmt(x["MCE"], 0), fmt(x["F"], 0), fmt(x["Fc"], 2), fmt(x["R2"], 2), fmt(x["R2a"], 3)]
    # 10.3
    x = R["e3"]
    e += [fmt(x["tc"], 3)] + [fmt(v["t"], 2) for v in x["fil"].values()] + [fmt(c, 2) for v in x["fil"].values() for c in v["ic"]]
    e += [fp(x["fil"]["antigüedad"]["p"]), fp(x["fil"]["distancia"]["p"]), fp(x["fil"]["constante"]["p"])]
    # 10.4
    e += [fmt(R["e4"]["y0"], 1)]
    # 10.5
    x = R["e5"]
    e += [fila(str(r.temp), fmt(r.precio, 0), str(r.litros)) for _, r in E5.iterrows()]
    e += [fmt(x["simple"].params["precio"], 4), fmt(x["mult"].params["precio"], 4), fmt(x["mult"].params["temp"], 2), fmt(x["r"], 2),
          fp(x["mult"].pvalues["precio"]), fp(x["simple"].pvalues["precio"])]
    # 10.6
    x = R["e6"]
    e += [fmt(x["y0"], 2), fmt(x["h0"], 4), fmt(x["tc"], 3), fmt(x["ic"][0], 2), fmt(x["ic"][1], 2), fmt(x["ip"][0], 2), fmt(x["ip"][1], 2), fmt(R["e1"]["M"]["MCE"], 4)]
    # 10.7
    x = R["e7"]; m = x["m"]
    e += [fila(str(r.sup), str(r.equipos), fmt(r.kwh, 0)) for _, r in E7.iterrows()]
    e += [fmt(m.params["sup"], 2), fmt(m.params["equipos"], 2), fp(m.pvalues["sup"]), fp(m.pvalues["equipos"]), fp(m.f_pvalue), fmt(x["r"], 3), fmt(x["vif"][0], 1),
          fmt(x["solo_eq"].params["equipos"], 2), fp(x["solo_eq"].pvalues["equipos"]), fmt(m.bse["equipos"], 2), fmt(m.rsquared, 3)]
    # 10.8
    x = R["e8"]
    e += [fila(fmt(a, 0), fmt(b, 0)) for a, b in zip(E8.km, E8.gasto)]
    e += [fmt(x["m"].params["km"], 3), fmt(x["bp"][0], 2), fp(x["bp"][1]), fmt(x["bpl"][0], 2), fp(x["bpl"][1]), fmt(x["ml"].params["km"], 5),
          fmt(100 * x["pct"], 1), fmt(x["m"].bse["km"], 3), fmt(x["se_hc3"], 3)]
    # 10.9
    x = R["e9"]
    e += [fmt(x["m"].params["horas"], 3), fmt(x["sin"].params["horas"], 3), fmt(x["h"][-1], 3), fmt(x["cook"][-1], 1), fmt(x["rst"][-1], 1),
          fmt(x["corte_h"], 2), fmt(x["corte_c"], 2), fmt(x["m"].rsquared, 3), fmt(x["sin"].rsquared, 3), fmt(x["sin"].params["Intercept"], 2), fmt(x["m"].params["Intercept"], 2)]
    # 10.10
    x = R["e10"]
    e += [fmt(x["M"]["SCR"], 0), fmt(x["M"]["F"], 2), fmt(x["M"]["R2"], 3), fmt(x["Mr"]["SCE"], 0), fmt(x["F"], 2), fp(x["p"])]
    # caso
    c = R["caso"]; M = c["M"]; P = c["P"]
    e += [fmt(M["b"][0], 2), fmt(M["b"][1], 4), fmt(M["b"][2], 5), fmt(M["se"][0], 2), fmt(M["se"][1], 5), fmt(M["se"][2], 6)]
    e += [fmt(x, 2) for x in M["t"]] + [fmt(M["F"], 2), fp(M["pF"]), fmt(M["R2"], 3), fmt(M["R2a"], 3), fmt(M["SCR"], 0), fmt(M["SCE"], 0), fmt(M["SCT"], 0),
                                         fmt(M["MCE"], 1), fmt(np.sqrt(M["MCE"]), 1), fmt(M["tc"], 3)]
    e += [fmt(M["ic"][1][0], 4), fmt(M["ic"][1][1], 4), fmt(M["ic"][2][0], 5), fmt(M["ic"][2][1], 5)]
    e += [fmt(P["y0"], 1), fmt(P["h0"], 4), fmt(P["ic"][0], 1), fmt(P["ic"][1], 1), fmt(P["ip"][0], 1), fmt(P["ip"][1], 1)]
    e += [fmt(c["sh"].pvalue, 2), fmt(c["bp"][1], 2), fmt(c["dw"], 2), fmt(c["r12"], 2), fmt(c["vif"], 2), fmt(c["h"].max(), 2), fmt(c["corte_h"], 2),
          fmt(c["cook"].max(), 2), fmt(c["corte_c"], 2), fmt(c["rst"][c["i_rst"]], 2), f"semana {c['i_cook'] + 1}", f"semana {c['i_rst'] + 1}"]
    e += [fmt(c["sin"].params["precio"], 4), fmt(c["sin"].params["publicidad"], 5), fmt(c["simple"].params["precio"], 4), fmt(c["pub10"], 2), fmt(c["precio1000"], 1),
          "$" + fmt(c["margen_eq"], 0)]
    e += [fmt(np.sqrt(R["ej"]["M"]["MCE"]), 2), fmt(c["v"].precio.min(), 0), fmt(c["v"].precio.max(), 0), fmt(c["v"].publicidad.min(), 0),
          fmt(c["v"].publicidad.max(), 0), fmt(M["SCR"] / 2, 0), fmt(100 * (1 - 0.975) * 40, 0)]
    # afirmaciones en palabras
    assert np.abs(R["ej"]["r_std"]).max() < 2                                   # «ningún residuo estandarizado pasa de 2»
    assert R["e9"]["sin"].params["horas"] / R["e9"]["m"].params["horas"] > 5    # «la pendiente sube más de cinco veces»
    assert round(-R["e5"]["mult"].params["precio"] * 100) == 4                  # «subir $100 baja unos 4 litros»
    return e


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    escribir_csv()
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
