"""Unidad 7 · Modelo lineal y ANOVA de un factor.

Recalcula todas las cifras de la unidad desde los datos (a mano, con las fórmulas de la tabla ANOVA y
con la forma matricial, y con scipy y statsmodels, y exige que coincidan), genera los gráficos de
`unidades/figuras/` y el CSV del ejemplo en `datos/`, ejecuta el cuaderno
`notebooks/u07_anova_un_factor.ipynb`, compara la pieza del caso con `caso_estampa_sur_datos.py` y,
con --revisar, busca cada cifra en el .md.

    python u07_anova_un_factor.py            # imprime los resultados
    python u07_anova_un_factor.py --revisar  # además los busca en el .md
"""
from pathlib import Path
import importlib.util, io, json, os, sys, contextlib

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
MD = RAMO / "unidades" / "07-anova-un-factor.md"
CUADERNO = RAMO / "notebooks" / "u07_anova_un_factor.ipynb"


# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    s = f"{x:,.{dec}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s[1:] if s.startswith("-") and float(s.replace(".", "").replace(",", ".")) == 0 else s


def fp(p, dec=3):
    """Valor p como se escribe en el texto: «p < 0,001» o «p = 0,467»."""
    return "p < 0,001" if p < 0.001 else f"p = {fmt(p, dec)}"


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def anova1_mano(G):
    """ANOVA de un factor con las fórmulas de la tabla. G = {nivel: lista de datos}."""
    k = len(G)
    n = {g: len(v) for g, v in G.items()}
    N = sum(n.values())
    m = {g: float(np.mean(v)) for g, v in G.items()}
    tot = {g: float(np.sum(v)) for g, v in G.items()}
    gm = sum(tot.values()) / N
    sctr = sum(n[g] * (m[g] - gm) ** 2 for g in G)
    sce_g = {g: float(sum((y - m[g]) ** 2 for y in v)) for g, v in G.items()}
    sce = sum(sce_g.values())
    sct = sum((y - gm) ** 2 for v in G.values() for y in v)
    assert abs(sct - (sctr + sce)) < 1e-8, "SCT = SCTrat + SCE"
    gl = {"tr": k - 1, "e": N - k, "t": N - 1}
    cm = {"tr": sctr / gl["tr"], "e": sce / gl["e"]}
    F = cm["tr"] / cm["e"]
    return {"k": k, "n": n, "N": N, "m": m, "tot": tot, "gm": gm, "sctr": sctr, "sce": sce, "sce_g": sce_g,
            "sct": sct, "gl": gl, "cm": cm, "F": F, "p": float(stats.f.sf(F, gl["tr"], gl["e"])),
            "Fcrit": float(stats.f.ppf(0.95, gl["tr"], gl["e"])), "R2": sctr / sct,
            "var": {g: float(np.var(v, ddof=1)) for g, v in G.items()}}


def coincide_scipy(T, G):
    f = stats.f_oneway(*G.values())
    assert abs(f.statistic - T["F"]) < 1e-9 and abs(f.pvalue - T["p"]) < 1e-12


def matricial(G, ref):
    """Forma matricial con codificación de referencia: columna de unos y una ficticia por nivel no referencia."""
    otros = [g for g in G if g != ref]
    filas = [(g, y) for g, v in G.items() for y in v]
    X = np.array([[1.0] + [1.0 if g == o else 0.0 for o in otros] for g, _ in filas])
    y = np.array([y for _, y in filas], float)
    XtX, Xty = X.T @ X, X.T @ y
    beta = np.linalg.solve(XtX, Xty)
    return {"X": X, "y": y, "XtX": XtX, "Xty": Xty, "beta": beta, "otros": otros}


def a_df(G, nf="grupo", ny="y"):
    return pd.DataFrame([{nf: g, ny: y} for g, v in G.items() for y in v])


# ---------------------------------------------------------------- datos (originales; pasados por herramientas/colisiones.py)

# Ejemplo resuelto · reparto en bicicleta en Valdivia: minutos por entrega con tres tipos de bicicleta,
# 5 entregas comparables (misma zona y franja) asignadas al azar a cada tipo
EJ = {"mecánica": [28, 31, 26, 30, 25], "eléctrica": [22, 24, 21, 25, 23], "de carga": [27, 29, 32, 26, 31]}
EJ_REF = "mecánica"

# 7.1 · papas en Chiloé: tabla incompleta (4 variedades, 6 surcos cada una), kg por surco
E1 = {"k": 4, "n": 6, "SCTrat": 42.6, "SCT": 118.2}

# 7.2 · humedad de la harina (%) de tres proveedores de una panadería, 4 sacos por proveedor
E2 = {"Molino Norte": [13.2, 13.8, 13.5, 13.1], "Molino Centro": [14.1, 14.6, 14.0, 14.5], "Molino Sur": [13.4, 13.9, 13.6, 13.7]}

# 7.3 · espera (min) en tres locales de una cadena de farmacias: n y medias
E3 = {"Centro": (4, 12.0), "Mall": (3, 9.0), "Barrio": (3, 15.0)}

# 7.4 · tasa de error por familia si se hacen todas las pruebas t entre k grupos, α = 0,05
E4_K = [3, 4, 5, 8]

# 7.5 · horas hasta responder un reclamo según canal (desbalanceado)
E5 = {"correo": [26, 31, 28, 35], "formulario web": [22, 18, 25, 20, 24, 23], "teléfono": [15, 19, 14, 17, 20]}

# 7.6 · gramos de bolsas de 1 kg en tres envasadoras (Levene a mano)
E6 = {"E1": [1002, 998, 1001, 1000, 999], "E2": [1006, 993, 1003, 995, 1008], "E3": [1001, 1000, 1003, 999, 1002]}

# 7.7 · tiempo de carga de una app (s) en tres servidores: medias y desviación común; dos tamaños de muestra
E7 = {"medias": [2.10, 2.16, 2.22], "s": 0.30, "n": [5, 400]}

# 7.8 · cajas por turno en cuatro plantas de una conservera: resumen (n, media, desviación estándar)
E8 = {"Planta 1": (8, 412, 14), "Planta 2": (6, 398, 11), "Planta 3": (7, 425, 16), "Planta 4": (9, 405, 12)}

# 7.9 · intensidad de color (unidades del colorímetro) en 5 lotes de pigmento elegidos al azar, 4 medidas por lote
E9 = {"L1": [52.1, 51.4, 52.8, 51.9], "L2": [49.8, 50.6, 50.1, 49.5], "L3": [53.4, 54.1, 52.9, 53.6],
      "L4": [50.9, 51.3, 50.2, 51.0], "L5": [52.6, 51.8, 52.3, 53.1]}

# 7.10 · horas de duración de baterías de dos proveedores: dos grupos con t y con ANOVA
E10 = {"P": [7.24, 6.81, 7.53, 7.02, 6.95, 7.38], "Q": [6.52, 6.87, 6.31, 6.74, 6.63, 6.18, 6.79]}


# ---------------------------------------------------------------- caso

def cargar_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_datos.py")
    caso = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caso)
    return caso


TINTAS = ["plastisol", "agua", "descarga"]


# ---------------------------------------------------------------- resultados

def fwer(m, a=0.05):
    return 1 - (1 - a) ** m


def resultados():
    R = {}
    # Ejemplo
    T = anova1_mano(EJ)
    coincide_scipy(T, EJ)
    df = a_df(EJ, "bicicleta", "minutos")
    mod = smf.ols(f"minutos ~ C(bicicleta, Treatment(reference='{EJ_REF}'))", data=df).fit()
    tab = sm.stats.anova_lm(mod, typ=1)
    assert abs(tab["F"].iloc[0] - T["F"]) < 1e-9 and abs(tab["sum_sq"].iloc[1] - T["sce"]) < 1e-9
    M = matricial(EJ, EJ_REF)
    assert abs(M["beta"][0] - mod.params.iloc[0]) < 1e-9
    for o, b in zip(M["otros"], M["beta"][1:]):       # statsmodels ordena los niveles alfabéticamente
        assert abs(mod.params[f"C(bicicleta, Treatment(reference='{EJ_REF}'))[T.{o}]"] - b) < 1e-9
    assert np.allclose(M["beta"], [T["m"][EJ_REF]] + [T["m"][o] - T["m"][EJ_REF] for o in M["otros"]])
    res = M["y"] - M["X"] @ M["beta"]
    assert abs(res @ res - T["sce"]) < 1e-9
    media_medias = float(np.mean(list(T["m"].values())))
    efectos = {g: T["m"][g] - media_medias for g in EJ}
    # codificación de efectos (suma cero) con statsmodels: el intercepto es la media de las medias
    mod_sum = smf.ols("minutos ~ C(bicicleta, Sum)", data=df).fit()
    assert abs(mod_sum.params.iloc[0] - media_medias) < 1e-9
    sh = stats.shapiro(res)
    lev = stats.levene(*EJ.values())
    bar = stats.bartlett(*[np.asarray(v, float) for v in EJ.values()])
    R["ej"] = {"T": T, "M": M, "df": df, "efectos": efectos, "mm": media_medias, "sh": sh, "lev": lev, "bar": bar,
               "fwer3": fwer(3), "resid": res, "tab": tab}

    # 7.1
    k, n = E1["k"], E1["n"]
    N = k * n
    sce = E1["SCT"] - E1["SCTrat"]
    gl = {"tr": k - 1, "e": N - k, "t": N - 1}
    cm = {"tr": E1["SCTrat"] / gl["tr"], "e": sce / gl["e"]}
    F = cm["tr"] / cm["e"]
    R["e1"] = {"sce": sce, "gl": gl, "cm": cm, "F": F, "p": float(stats.f.sf(F, gl["tr"], gl["e"])),
               "Fcrit": float(stats.f.ppf(0.95, gl["tr"], gl["e"])), "R2": E1["SCTrat"] / E1["SCT"]}

    # 7.2
    T2 = anova1_mano(E2)
    coincide_scipy(T2, E2)
    R["e2"] = T2

    # 7.3
    filas = [(g, m) for g, (nn, m) in E3.items() for _ in range(nn)]
    def beta_ref(ref):
        otros = [g for g in E3 if g != ref]
        X = np.array([[1.0] + [1.0 if g == o else 0.0 for o in otros] for g, _ in filas])
        y = np.array([m for _, m in filas])
        return X, np.linalg.solve(X.T @ X, X.T @ y), otros
    X3, b3c, _ = beta_ref("Centro")
    _, b3m, _ = beta_ref("Mall")
    X3full = np.c_[X3, np.array([1.0 if g == "Mall" else 0.0 for g, _ in filas])]
    X3full = np.array([[1.0, g == "Centro", g == "Mall", g == "Barrio"] for g, _ in filas], float)
    rango = int(np.linalg.matrix_rank(X3full.T @ X3full))
    mm3 = float(np.mean([m for _, m in E3.values()]))
    R["e3"] = {"XtX": X3.T @ X3, "b_centro": b3c, "b_mall": b3m, "rango": rango, "mm": mm3,
               "efectos": {g: m - mm3 for g, (_, m) in E3.items()}}

    # 7.4
    R["e4"] = {k_: (k_ * (k_ - 1) // 2, fwer(k_ * (k_ - 1) // 2)) for k_ in E4_K}

    # 7.5
    T5 = anova1_mano(E5)
    coincide_scipy(T5, E5)
    M5 = matricial(E5, "correo")
    R["e5"] = {"T": T5, "M": M5}

    # 7.6 · Levene (centrado en la mediana, la versión de Brown y Forsythe que scipy usa por omisión)
    med = {g: float(np.median(v)) for g, v in E6.items()}
    dev = {g: [abs(y - med[g]) for y in v] for g, v in E6.items()}
    T6 = anova1_mano(dev)
    lev6 = stats.levene(*E6.values())
    assert abs(lev6.statistic - T6["F"]) < 1e-9, "Levene es un ANOVA de las desviaciones absolutas"
    bar6 = stats.bartlett(*[np.asarray(v, float) for v in E6.values()])
    T6y = anova1_mano(E6)
    welch6 = anova_oneway(list(E6.values()), use_var="unequal")
    R["e6"] = {"med": med, "dev": dev, "T": T6, "lev": lev6, "bar": bar6, "Ty": T6y, "welch": welch6,
               "s": {g: float(np.std(v, ddof=1)) for g, v in E6.items()}}

    # 7.7
    out7 = {}
    mm7 = float(np.mean(E7["medias"]))
    for nn in E7["n"]:
        k7 = len(E7["medias"])
        sctr = nn * sum((m - mm7) ** 2 for m in E7["medias"])
        sce7 = k7 * (nn - 1) * E7["s"] ** 2
        F7 = (sctr / (k7 - 1)) / E7["s"] ** 2
        out7[nn] = {"sctr": sctr, "sce": sce7, "F": F7, "p": float(stats.f.sf(F7, k7 - 1, k7 * nn - k7)),
                    "eta2": sctr / (sctr + sce7), "gle": k7 * nn - k7}
    R["e7"] = out7

    # 7.8 · ANOVA desde el resumen
    n8 = {g: v[0] for g, v in E8.items()}
    m8 = {g: v[1] for g, v in E8.items()}
    s8 = {g: v[2] for g, v in E8.items()}
    N8 = sum(n8.values())
    gm8 = sum(n8[g] * m8[g] for g in E8) / N8
    sctr8 = sum(n8[g] * (m8[g] - gm8) ** 2 for g in E8)
    sce8 = sum((n8[g] - 1) * s8[g] ** 2 for g in E8)
    gl8 = {"tr": len(E8) - 1, "e": N8 - len(E8)}
    F8 = (sctr8 / gl8["tr"]) / (sce8 / gl8["e"])
    # segundo camino: datos sintéticos con esas medias y desviaciones exactas dan el mismo F
    sint = {}
    for g in E8:
        z = np.arange(n8[g], dtype=float); z = (z - z.mean()) / z.std(ddof=1)
        sint[g] = m8[g] + s8[g] * z
    assert abs(stats.f_oneway(*sint.values()).statistic - F8) < 1e-9
    R["e8"] = {"N": N8, "gm": gm8, "sctr": sctr8, "sce": sce8, "gl": gl8, "cmtr": sctr8 / gl8["tr"], "cme": sce8 / gl8["e"],
               "F": F8, "p": float(stats.f.sf(F8, gl8["tr"], gl8["e"])), "R2": sctr8 / (sctr8 + sce8)}

    # 7.9 · efectos aleatorios
    T9 = anova1_mano(E9)
    coincide_scipy(T9, E9)
    n9 = len(E9["L1"])
    s2a = (T9["cm"]["tr"] - T9["cm"]["e"]) / n9
    R["e9"] = {"T": T9, "s2a": s2a, "s2": T9["cm"]["e"], "icc": s2a / (s2a + T9["cm"]["e"]),
               "sd_total": float(np.sqrt(s2a + T9["cm"]["e"])), "sd_dentro": float(np.sqrt(T9["cm"]["e"])),
               "sd_entre": float(np.sqrt(s2a))}

    # 7.10 · dos grupos: t combinada = raíz de F
    T10 = anova1_mano(E10)
    t10 = stats.ttest_ind(E10["P"], E10["Q"], equal_var=True)
    assert abs(t10.statistic ** 2 - T10["F"]) < 1e-9 and abs(t10.pvalue - T10["p"]) < 1e-12
    w10 = stats.ttest_ind(E10["P"], E10["Q"], equal_var=False)
    mod10 = smf.ols("y ~ C(grupo, Treatment(reference='Q'))", data=a_df(E10)).fit()
    assert abs(abs(mod10.tvalues.iloc[1]) - abs(t10.statistic)) < 1e-9
    R["e10"] = {"T": T10, "t": t10, "w": w10, "beta": mod10.params.values, "ee": float(mod10.bse.iloc[1])}

    # Caso · secado según tinta (un factor; la temperatura queda en el error)
    s = pd.read_csv(DATOS / "secado.csv")
    G = {t: list(s[s.tinta == t].secado_min) for t in TINTAS}
    Tc = anova1_mano(G)
    coincide_scipy(Tc, G)
    modc = smf.ols("secado_min ~ C(tinta)", data=s).fit()
    tabc = sm.stats.anova_lm(modc, typ=1)
    assert abs(tabc["F"].iloc[0] - Tc["F"]) < 1e-9
    levc = stats.levene(*[G[t] for t in TINTAS])
    barc = stats.bartlett(*[G[t] for t in TINTAS])
    shc = stats.shapiro(modc.resid)
    res_temp = {c: float(modc.resid[s.temperatura == c].mean()) for c in ["150 °C", "170 °C"]}
    R["caso"] = {"s": s, "G": G, "T": Tc, "mod": modc, "lev": levc, "bar": barc, "sh": shc, "params": modc.params,
                 "res_temp": res_temp, "fwer3": fwer(3)}
    return R


# ---------------------------------------------------------------- CSV, figuras y cuaderno

def escribir_csv(R):
    R["ej"]["df"].to_csv(DATOS / "u07_ejemplo.csv", index=False, encoding="utf-8")


COL = ["#2B2F33", "#E2622A", "#5F8FB4"]


def graficos(R):
    FIG.mkdir(parents=True, exist_ok=True)
    T = R["ej"]["T"]
    fig, ax = plt.subplots(figsize=(6.0, 3.3), dpi=150)
    for i, (g, v) in enumerate(EJ.items()):
        x = np.full(len(v), i) + np.linspace(-0.12, 0.12, len(v))
        ax.scatter(x, v, color=COL[i], s=22, zorder=3)
        ax.hlines(T["m"][g], i - 0.3, i + 0.3, color=COL[i], lw=2.2)
        ax.annotate(f"media {fmt(T['m'][g], 0)}", (i + 0.32, T["m"][g]), va="center", fontsize=8, color=COL[i])
    ax.axhline(T["gm"], color="#8A8F94", lw=1, ls="--")
    ax.annotate(f"media global {fmt(T['gm'], 2)}", (2.35, T["gm"] + 0.3), fontsize=8, color="#5F656B")
    ax.set_xticks(range(len(EJ))); ax.set_xticklabels(list(EJ))
    ax.set_xlim(-0.5, 2.9)
    ax.set_ylabel("minutos por entrega")
    ax.set_title("Ejemplo: la distancia entre medias contra la dispersión dentro de cada grupo", fontsize=9.5)
    ax.spines[["top", "right"]].set_visible(False); ax.grid(axis="y", color="#D6D3CE", lw=0.6)
    fig.tight_layout(); fig.savefig(FIG / "u07_ejemplo.png"); plt.close(fig)

    c = R["caso"]; s = c["s"]
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.1), dpi=150)
    ax[0].boxplot([c["G"][t] for t in TINTAS], tick_labels=TINTAS, widths=0.5,
                  medianprops={"color": COL[1], "lw": 2}, boxprops={"color": COL[0]}, whiskerprops={"color": COL[0]},
                  capprops={"color": COL[0]})
    ax[0].set_ylabel("secado (min)"); ax[0].set_title("Secado según tinta (10 prendas por tinta)", fontsize=9.5)
    for j, temp in enumerate(["150 °C", "170 °C"]):
        r = c["mod"].resid[s.temperatura == temp]
        xs = [TINTAS.index(t) + (-0.12 if j == 0 else 0.12) for t in s.tinta[s.temperatura == temp]]
        ax[1].scatter(xs, r, s=16, color=COL[1 + j], label=temp)
    ax[1].axhline(0, color="#8A8F94", lw=1)
    ax[1].set_xticks(range(3)); ax[1].set_xticklabels(TINTAS)
    ax[1].set_ylabel("residuo (min)"); ax[1].set_title("Residuos del modelo de un factor", fontsize=9.5)
    ax[1].legend(fontsize=8, frameon=False, title="temperatura", title_fontsize=8)
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / "u07_caso.png"); plt.close(fig)


def ejecutar_cuaderno():
    """Ejecuta las celdas de código del cuaderno con exec (no hace falta Jupyter) y devuelve su espacio de nombres."""
    nb = json.loads(CUADERNO.read_text(encoding="utf-8"))
    ns = {"__name__": "__cuaderno__"}
    previo = os.getcwd()
    os.chdir(CUADERNO.parent)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            for celda in nb["cells"]:
                if celda["cell_type"] == "code":
                    exec("".join(celda["source"]), ns)
    finally:
        os.chdir(previo)
        plt.close("all")
    return ns


def comparar_cuaderno(R, ns):
    T, Tc = R["ej"]["T"], R["caso"]["T"]
    ok = abs(ns["tabla_ejemplo"]["F"].iloc[0] - T["F"]) < 1e-9
    ok &= np.allclose(ns["beta_ejemplo"], R["ej"]["M"]["beta"])
    ok &= abs(ns["tabla_caso"]["F"].iloc[0] - Tc["F"]) < 1e-9
    ok &= abs(ns["levene_caso"].pvalue - R["caso"]["lev"].pvalue) < 1e-12
    ok &= abs(ns["shapiro_caso"].pvalue - R["caso"]["sh"].pvalue) < 1e-12
    print("CUADERNO:", "OK, reproduce el ejemplo y el caso" if ok else "NO coincide")
    return bool(ok)


def cadena(R):
    caso = cargar_caso()
    D = caso.generar()                    # en memoria: no reescribe los CSV
    C = caso.calcular(D)["u7"]
    s = R["caso"]["s"]
    ok = np.allclose(D["secado"].secado_min.values, s.secado_min.values) and (D["secado"].tinta.values == s.tinta.values).all()
    Tc = R["caso"]["T"]
    ok &= abs(C["F_tinta"] - Tc["F"]) < 1e-9
    ok &= abs(C["p_tinta"] - Tc["p"]) < 1e-12
    ok &= all(abs(C["medias"][t] - Tc["m"][t]) < 1e-9 for t in TINTAS)
    print("CADENA:", "OK, la pieza del caso calza con caso_estampa_sur_datos.py" if ok else "NO calza")
    return bool(ok)


# ---------------------------------------------------------------- impresión y revisión

def fila(*c):
    return "| " + " | ".join(c) + " |"


def imprimir_T(nombre, T, d=2):
    print(f"== {nombre}: n {T['n']} medias {[fmt(v, 3) for v in T['m'].values()]} totales {[fmt(v, 1) for v in T['tot'].values()]} gm {fmt(T['gm'], 4)}")
    print(f"   SCTrat {fmt(T['sctr'], 4)} SCE {fmt(T['sce'], 4)} SCT {fmt(T['sct'], 4)} SCE_g {[fmt(v, 3) for v in T['sce_g'].values()]} gl {T['gl']}")
    print(f"   CM {fmt(T['cm']['tr'], 4)} / {fmt(T['cm']['e'], 4)} F {fmt(T['F'], 3)} {fp(T['p'])} ({T['p']:.6f}) Fcrit {fmt(T['Fcrit'], 3)} R2 {fmt(T['R2'], 3)} var {[fmt(v, 3) for v in T['var'].values()]}")


def imprimir(R):
    e = R["ej"]
    imprimir_T("Ejemplo", e["T"])
    M = e["M"]
    print("   XtX", M["XtX"].tolist(), "Xty", M["Xty"].tolist(), "beta", [fmt(b, 3) for b in M["beta"]])
    print("   efectos", {k: fmt(v, 3) for k, v in e["efectos"].items()}, "media de medias", fmt(e["mm"], 3))
    print("   Shapiro", fmt(e["sh"].statistic, 3), fp(e["sh"].pvalue), "Levene", fmt(e["lev"].statistic, 3), fp(e["lev"].pvalue),
          "Bartlett", fmt(e["bar"].statistic, 3), fp(e["bar"].pvalue), "FWER3", pct(e["fwer3"]))
    x = R["e1"]
    print("== 7.1", "SCE", fmt(x["sce"], 1), x["gl"], "CM", fmt(x["cm"]["tr"], 2), fmt(x["cm"]["e"], 2), "F", fmt(x["F"], 2), fp(x["p"]), "Fcrit", fmt(x["Fcrit"], 2), "R2", fmt(x["R2"], 3))
    imprimir_T("7.2", R["e2"])
    x = R["e3"]
    print("== 7.3 XtX", x["XtX"].tolist(), "b centro", [fmt(b, 1) for b in x["b_centro"]], "b mall", [fmt(b, 1) for b in x["b_mall"]], "rango", x["rango"], "mm", x["mm"], x["efectos"])
    print("== 7.4", {k: (m, pct(f)) for k, (m, f) in R["e4"].items()})
    imprimir_T("7.5", R["e5"]["T"])
    M = R["e5"]["M"]; print("   XtX", M["XtX"].tolist(), "Xty", M["Xty"].tolist(), "beta", [fmt(b, 3) for b in M["beta"]])
    x = R["e6"]
    print("== 7.6 med", x["med"], "dev", x["dev"], "s", {k: fmt(v, 3) for k, v in x["s"].items()})
    imprimir_T("7.6 desv", x["T"])
    print("   Levene", fmt(x["lev"].statistic, 3), fp(x["lev"].pvalue), "Bartlett", fmt(x["bar"].statistic, 3), fp(x["bar"].pvalue),
          "ANOVA clásico F", fmt(x["Ty"]["F"], 3), fp(x["Ty"]["p"]), "Welch F", fmt(x["welch"].statistic, 3), "gl2", fmt(x["welch"].df[1], 2), fp(x["welch"].pvalue))
    for nn, v in R["e7"].items():
        print(f"== 7.7 n={nn}: SCTrat {fmt(v['sctr'], 4)} SCE {fmt(v['sce'], 2)} F {fmt(v['F'], 2)} {fp(v['p'])} eta2 {fmt(v['eta2'], 3)} glE {v['gle']}")
    x = R["e8"]
    print("== 7.8 N", x["N"], "gm", fmt(x["gm"], 3), "SCTrat", fmt(x["sctr"], 1), "SCE", fmt(x["sce"], 1), "CM", fmt(x["cmtr"], 1), fmt(x["cme"], 2), "F", fmt(x["F"], 2), fp(x["p"]), "R2", fmt(x["R2"], 3))
    x = R["e9"]
    imprimir_T("7.9", x["T"])
    print("   s2a", fmt(x["s2a"], 4), "s2", fmt(x["s2"], 4), "ICC", fmt(x["icc"], 3), "sd entre", fmt(x["sd_entre"], 3), "dentro", fmt(x["sd_dentro"], 3), "total", fmt(x["sd_total"], 3))
    x = R["e10"]
    imprimir_T("7.10", x["T"])
    print("   t", fmt(x["t"].statistic, 3), fp(x["t"].pvalue), "t2", fmt(x["t"].statistic ** 2, 3), "Welch", fmt(x["w"].statistic, 3), fp(x["w"].pvalue), "beta", [fmt(b, 3) for b in x["beta"]], "ee", fmt(x["ee"], 4))
    c = R["caso"]
    imprimir_T("Caso", c["T"])
    print("   Levene", fmt(c["lev"].statistic, 3), fp(c["lev"].pvalue), "Bartlett", fmt(c["bar"].statistic, 3), fp(c["bar"].pvalue),
          "Shapiro", fmt(c["sh"].statistic, 3), fp(c["sh"].pvalue), "params", {k: fmt(v, 2) for k, v in c["params"].items()},
          "res temp", {k: fmt(v, 2) for k, v in c["res_temp"].items()})


def esperados(R):
    e = []
    T = R["ej"]["T"]; M = R["ej"]["M"]; ej = R["ej"]
    for g, v in EJ.items():
        e.append(fila(g, *map(str, v), fmt(T["tot"][g], 0), fmt(T["m"][g], 0)))
    e += [fmt(T["gm"], 3), fmt(T["sctr"], 2), fmt(T["sce"], 0), fmt(T["sct"], 2), fmt(T["cm"]["tr"], 2), fmt(T["cm"]["e"], 3),
          fmt(T["F"], 2), fmt(T["Fcrit"], 2), fmt(T["p"], 4), fmt(T["R2"], 3)]
    e += [fmt(v, 0) for v in T["sce_g"].values()]
    e += [fmt(v, 3) for v in ej["efectos"].values()]
    e += [fmt(b, 0) for b in M["beta"]]
    e += [fmt(ej["sh"].pvalue, 3), fmt(ej["lev"].pvalue, 2), fmt(ej["bar"].pvalue, 2), pct(ej["fwer3"])]
    # 7.1
    x = R["e1"]
    e += [fmt(x["sce"], 1), fmt(x["cm"]["tr"], 2), fmt(x["cm"]["e"], 2), fmt(x["F"], 2), fp(x["p"]), fmt(x["Fcrit"], 2), fmt(x["R2"], 3)]
    # 7.2
    T2 = R["e2"]
    e += [fila(g, *(fmt(y, 1) for y in v)) for g, v in E2.items()]
    e += [fmt(v, 3) for v in T2["m"].values()] + [fmt(T2["gm"], 3), fmt(T2["sctr"], 3), fmt(T2["sce"], 3), fmt(T2["sct"], 3),
                                                   fmt(T2["F"], 2), fp(T2["p"]), fmt(T2["Fcrit"], 2), fmt(T2["R2"], 3)]
    # 7.3
    x = R["e3"]
    e += [fmt(b, 0) for b in x["b_centro"]] + [fmt(b, 0) for b in x["b_mall"]]
    # 7.4
    e += [pct(f) for _, f in R["e4"].values()]
    # 7.5
    T5 = R["e5"]["T"]; M5 = R["e5"]["M"]
    e += [fila(g, *map(str, v)) for g, v in E5.items()]
    e += [fmt(T5["gm"], 3), fmt(T5["sctr"], 2), fmt(T5["sce"], 2), fmt(T5["sct"], 2), fmt(T5["F"], 2), fp(T5["p"]), fmt(T5["R2"], 3)]
    e += [fmt(b, 0) for b in M5["beta"]] + [fmt(v, 0) for v in M5["Xty"]]
    # 7.6
    x = R["e6"]
    e += [fila(g, *map(str, v)) for g, v in E6.items()]
    e += [fmt(x["T"]["F"], 2), fp(x["lev"].pvalue), fmt(x["bar"].pvalue, 3), fmt(x["Ty"]["F"], 2), fp(x["Ty"]["p"]),
          fmt(x["welch"].statistic, 2), fmt(x["welch"].df[1], 2), fp(x["welch"].pvalue)]
    e += [fmt(v, 2) for v in x["T"]["m"].values()] + [fmt(v, 2) for v in x["s"].values()]
    # 7.7
    for v in R["e7"].values():
        e += [fmt(v["F"], 2), fp(v["p"]), fmt(v["eta2"], 3)]
    # 7.8
    x = R["e8"]
    e += [fila(g, str(a), str(b), str(c)) for g, (a, b, c) in E8.items()]
    e += [fmt(x["gm"], 2), fmt(x["sctr"], 1), fmt(x["sce"], 0), fmt(x["F"], 2), fp(x["p"]), fmt(x["R2"], 3)]
    # 7.9
    x = R["e9"]
    e += [fila(g, *(fmt(y, 1) for y in v)) for g, v in E9.items()]
    e += [fmt(x["T"]["cm"]["tr"], 3), fmt(x["T"]["cm"]["e"], 4), fmt(x["T"]["F"], 2), fmt(x["s2a"], 3), fmt(x["icc"], 3),
          fmt(x["sd_entre"], 2), fmt(x["sd_dentro"], 2), fmt(x["sd_total"], 2)]
    # 7.10
    x = R["e10"]
    e += [fila(g, *(fmt(y, 2) for y in v)) for g, v in E10.items()]
    e += [fmt(x["t"].statistic, 3), fmt(x["T"]["F"], 2), fp(x["t"].pvalue), fmt(x["w"].statistic, 3), fp(x["w"].pvalue),
          fmt(x["beta"][1], 3), fmt(x["ee"], 4), fmt(x["T"]["cm"]["e"], 4)]
    # caso
    c = R["caso"]; Tc = c["T"]
    e += [fila(t, fmt(Tc["m"][t], 2), fmt(Tc["var"][t], 3)) for t in TINTAS]
    e += [fmt(Tc["sctr"], 2), fmt(Tc["sce"], 2), fmt(Tc["sct"], 2), fmt(Tc["cm"]["tr"], 2), fmt(Tc["cm"]["e"], 3), fmt(Tc["F"], 2),
          fmt(Tc["Fcrit"], 2), fmt(Tc["R2"], 3), fmt(Tc["gm"], 2)]
    e += [fmt(c["lev"].pvalue, 2), fmt(c["bar"].pvalue, 2), fmt(c["sh"].pvalue, 3)]
    e += [fmt(v, 2) for v in c["params"].values]
    e += [fmt(v, 2) for v in c["res_temp"].values()]
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
