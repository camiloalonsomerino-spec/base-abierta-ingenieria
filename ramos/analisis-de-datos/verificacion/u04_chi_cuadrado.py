"""Unidad 4 · Tablas de contingencia y chi-cuadrado.

Recalcula todas las cifras de la unidad desde los datos, a mano (esperados, aportes, residuos,
V de Cramér, probabilidades hipergeométricas) y con scipy o statsmodels, y exige que los dos caminos
coincidan. Deja la tabla del ejemplo en datos/u04_ejemplo.csv, dibuja las figuras en
unidades/figuras/, ejecuta el cuaderno notebooks/u04_chi_cuadrado.ipynb y compara la pieza del caso
con el script del caso.

    python u04_chi_cuadrado.py            # imprime los resultados
    python u04_chi_cuadrado.py --revisar  # además busca cada cifra en el .md
"""
from math import comb
from pathlib import Path
import importlib.util, json, os, sys

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.contingency_tables import Table

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
DATOS, FIG, NB = RAMO / "datos", RAMO / "unidades" / "figuras", RAMO / "notebooks"
MD = RAMO / "unidades" / "04-chi-cuadrado.md"
CUADERNO = NB / "u04_chi_cuadrado.ipynb"


# ---------------------------------------------------------------- formato a la chilena

def fmt(x, dec=1):
    s = f"{x:,.{dec}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return "0" + s[2:] if s.startswith("-0") and set(s[1:]) <= set("0,") else s


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def pv(p, dec=3):
    return "< 0,001" if p < 0.001 else fmt(p, dec)


def fila(*celdas):
    return "| " + " | ".join(celdas) + " |"


# ---------------------------------------------------------------- la prueba, a mano

def chi_cuadrado(obs, yates=False):
    """Prueba de independencia (u homogeneidad) a mano; la confirma scipy y statsmodels."""
    O = np.asarray(obs, float)
    n = O.sum()
    fi, fj = O.sum(axis=1), O.sum(axis=0)
    E = np.outer(fi, fj) / n
    if yates:
        dif = np.maximum(np.abs(O - E) - 0.5, 0)
        contrib = dif ** 2 / E
    else:
        contrib = (O - E) ** 2 / E
    chi2 = contrib.sum()
    gl = (O.shape[0] - 1) * (O.shape[1] - 1)
    p = stats.chi2.sf(chi2, gl)
    V = np.sqrt(((O - E) ** 2 / E).sum() / (n * (min(O.shape) - 1)))
    pearson = (O - E) / np.sqrt(E)
    ajustado = (O - E) / np.sqrt(E * np.outer(1 - fi / n, 1 - fj / n))
    sc = stats.chi2_contingency(O, correction=yates)
    assert abs(sc.statistic - chi2) < 1e-9 and abs(sc.pvalue - p) < 1e-12 and sc.dof == gl
    assert np.allclose(sc.expected_freq, E)
    if not yates:
        t = Table(O)
        assert np.allclose(t.standardized_resids, ajustado) and np.allclose(t.resid_pearson, pearson)
    return {"O": O, "n": n, "fi": fi, "fj": fj, "E": E, "contrib": contrib, "chi2": chi2, "gl": gl, "p": p,
            "crit": stats.chi2.ppf(0.95, gl), "V": V, "pearson": pearson, "ajustado": ajustado,
            "emin": E.min(), "bajo5": int((E < 5).sum())}


def fisher_a_mano(t):
    """Prueba exacta de Fisher bilateral: suma las tablas con márgenes fijos tan o menos probables."""
    (a, b), (c, d) = t
    f1, c1, n = a + b, a + c, a + b + c + d
    probs = {k: comb(c1, k) * comb(n - c1, f1 - k) / comb(n, f1) for k in range(max(0, f1 + c1 - n), min(f1, c1) + 1)}
    p_obs = probs[a]
    p = sum(v for v in probs.values() if v <= p_obs * (1 + 1e-7))
    assert abs(p - stats.fisher_exact(t).pvalue) < 1e-12
    return {"probs": probs, "p_obs": p_obs, "p": p, "total": comb(n, f1)}


# ---------------------------------------------------------------- datos (originales de esta base)
# Pasados por herramientas/colisiones.py contra el material del curso el 16-10-2026: sin alertas.

# Ejemplo · cafetería de Chillán: tipo de pedido según franja horaria (un día de pedidos)
EJ_FILAS, EJ_COLS = ["mañana", "tarde"], ["para llevar", "para servir", "delivery"]
EJ = [[46, 28, 16], [31, 42, 37]]

E1 = {"filas": ["mensual", "anual"], "cols": ["mañana", "tarde", "noche"], "t": [[34, 51, 45], [26, 22, 42]]}
E2 = {"filas": ["con capacitación", "sin capacitación"], "t": [[7, 78], [19, 76]]}   # accidente sí / no
E3 = {"chi2": 11.8, "r": 3, "c": 4, "n": 420}
E4 = {"A": {"chi2": 9.6, "n": 200, "dim": (2, 2)}, "B": {"chi2": 48.0, "n": 5000, "dim": (3, 3)}}
E5 = {"filas": ["18 a 34", "35 a 54", "55 o más"], "cols": ["efectivo", "débito", "crédito"],
      "t": [[18, 96, 46], [25, 88, 67], [52, 61, 47]]}
E6 = {"filas": ["particular", "empresa"], "cols": ["mantención", "frenos", "motor", "eléctrico"],
      "t": [[48, 22, 9, 3], [30, 14, 12, 2]]}
E7 = {"filas": ["centro A", "centro B", "centro C"], "cols": ["menos de 5 min", "5 a 15 min", "más de 15 min"],
      "t": [[54, 44, 22], [51, 63, 36], [34, 52, 44]]}
E8 = {"piloto": [[18, 12], [12, 18]], "factor": 10}
E9 = {"urbana": [[180, 20], [46, 4]], "rural": [[30, 20], [130, 70]]}   # filas: empresa A, B · columnas: a tiempo, atrasado
E10 = [[1, 9], [5, 3]]   # filas: proveedor nuevo, antiguo · columnas: lote rechazado, aceptado


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
    R["ej"] = chi_cuadrado(EJ)
    R["e1"] = chi_cuadrado(E1["t"])
    R["e2"] = chi_cuadrado(E2["t"])
    R["e2_y"] = chi_cuadrado(E2["t"], yates=True)
    t = np.array(E2["t"])
    p1, p2 = t[0, 0] / t[0].sum(), t[1, 0] / t[1].sum()
    pb = t[:, 0].sum() / t.sum()
    z = (p1 - p2) / np.sqrt(pb * (1 - pb) * (1 / t[0].sum() + 1 / t[1].sum()))
    assert abs(z ** 2 - R["e2"]["chi2"]) < 1e-9          # z² = χ² sin Yates
    R["e2_z"] = {"p1": p1, "p2": p2, "z": z}
    assert np.allclose(np.abs(R["e2"]["ajustado"]), abs(z))   # en 2 × 2, |residuo ajustado| = |z|
    gl3 = (E3["r"] - 1) * (E3["c"] - 1)
    R["e3"] = {"gl": gl3, "crit": stats.chi2.ppf(0.95, gl3), "p": stats.chi2.sf(E3["chi2"], gl3),
               "V": np.sqrt(E3["chi2"] / (E3["n"] * (min(E3["r"], E3["c"]) - 1)))}
    R["e4"] = {}
    for k, v in E4.items():
        gl = (v["dim"][0] - 1) * (v["dim"][1] - 1)
        R["e4"][k] = {"gl": gl, "p": stats.chi2.sf(v["chi2"], gl), "V": np.sqrt(v["chi2"] / (v["n"] * (min(v["dim"]) - 1)))}
    R["e5"] = chi_cuadrado(E5["t"])
    R["e6"] = chi_cuadrado(E6["t"])
    t6 = np.array(E6["t"])
    R["e6_c"] = chi_cuadrado(np.c_[t6[:, :2], t6[:, 2] + t6[:, 3]])
    R["e7"] = chi_cuadrado(E7["t"])
    R["e8a"] = chi_cuadrado(E8["piloto"])
    R["e8b"] = chi_cuadrado(np.array(E8["piloto"]) * E8["factor"])
    assert abs(R["e8b"]["chi2"] - E8["factor"] * R["e8a"]["chi2"]) < 1e-9
    R["e8a_y"] = chi_cuadrado(E8["piloto"], yates=True)
    # 4.9 · paradoja de Simpson
    R["e9"] = {}
    for zona, tz in E9.items():
        tz = np.array(tz)
        R["e9"][zona] = {"tasas": tz[:, 0] / tz.sum(axis=1), "chi": chi_cuadrado(tz), "fisher": fisher_a_mano(tz.tolist())}
    agg = np.array(E9["urbana"]) + np.array(E9["rural"])
    R["e9"]["total"] = {"tasas": agg[:, 0] / agg.sum(axis=1), "chi": chi_cuadrado(agg), "t": agg}
    R["e9_pesos"] = {"A_urbana": E9["urbana"][0][0] + E9["urbana"][0][1], "B_rural": sum(E9["rural"][1])}
    # 4.10 · Fisher a mano
    R["e10"] = fisher_a_mano(E10)
    R["e10_chi"] = chi_cuadrado(E10)
    R["e10_y"] = chi_cuadrado(E10, yates=True)

    # caso
    caso, D = cargar_caso()
    rc = D["reclamos_canal"]
    R["caso_canales"] = list(rc.canal)
    R["caso_tipos"] = ["talla", "color", "atraso"]
    R["caso"] = chi_cuadrado(rc[R["caso_tipos"]].values)
    aj = np.abs(R["caso"]["ajustado"])
    assert (aj > 2).sum() == 4 and (aj > 3).sum() == 3     # lo que dice el texto del caso
    R["_caso_mod"], R["_D"] = caso, D
    return R


# ---------------------------------------------------------------- datos del ejemplo, figuras y cuaderno

def escribir_datos():
    df = pd.DataFrame(EJ, columns=["llevar", "servir", "delivery"])
    df.insert(0, "franja", EJ_FILAS)
    df.to_csv(DATOS / "u04_ejemplo.csv", index=False, encoding="utf-8")


AZUL, NARANJA, AGUA, TINTA, SUAVE, LINEA = "#2a78d6", "#eb6834", "#1baf7a", "#2B2F33", "#52514e", "#D6D3CE"


def estilo(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(LINEA)
    ax.tick_params(colors=SUAVE, labelsize=8)
    ax.title.set_color(TINTA)


def barras_fila(ax, O, filas, cols, titulo):
    O = np.asarray(O, float)
    prop = O / O.sum(axis=1, keepdims=True)
    izq = np.zeros(len(filas))
    for j, (col, color) in enumerate(zip(cols, (AZUL, NARANJA, AGUA))):
        ax.barh(range(len(filas)), prop[:, j], left=izq + 0.002, height=.6, color=color, label=col, edgecolor="white", linewidth=1.5)
        for i in range(len(filas)):
            ax.text(izq[i] + prop[i, j] / 2, i, pct(prop[i, j], 0), ha="center", va="center", fontsize=8, color="white")
        izq += prop[:, j]
    ax.set_yticks(range(len(filas)), [f"{f} (n = {int(O[i].sum())})" for i, f in enumerate(filas)])
    ax.invert_yaxis(); ax.set_xlim(0, 1.005); ax.set_xticks([])
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="lower center", bbox_to_anchor=(.5, -.28))
    ax.set_title(titulo); estilo(ax); ax.spines["bottom"].set_visible(False)


def figuras(R):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    plt.rcParams.update({"font.family": "Segoe UI", "font.size": 9, "axes.titlesize": 10})
    FIG.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 2.3))
    barras_fila(ax, EJ, EJ_FILAS, EJ_COLS, "Tipo de pedido según franja (porcentaje de cada fila)")
    fig.tight_layout(); fig.savefig(FIG / "u04_ejemplo.png", dpi=170); plt.close(fig)

    c = R["caso"]
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 2.9), gridspec_kw={"width_ratios": [1.25, 1]})
    barras_fila(axs[0], c["O"], R["caso_canales"], R["caso_tipos"], "Tipo de reclamo por canal (% de cada fila)")
    ax = axs[1]
    cmap = LinearSegmentedColormap.from_list("div", [AZUL, "#f0efec", NARANJA])
    A = c["ajustado"]
    ax.imshow(A, cmap=cmap, vmin=-4, vmax=4)
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            ax.text(j, i, fmt(A[i, j], 2), ha="center", va="center", fontsize=9, color=TINTA,
                    fontweight="bold" if abs(A[i, j]) > 2 else "normal")
    ax.set_xticks(range(3), R["caso_tipos"]); ax.set_yticks(range(3), R["caso_canales"])
    ax.set_title("Residuos ajustados (|r| > 2 en negrita)")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(colors=SUAVE, labelsize=8, length=0); ax.title.set_color(TINTA)
    fig.tight_layout(); fig.savefig(FIG / "u04_caso.png", dpi=170); plt.close(fig)


def ejecutar_cuaderno():
    nb = json.loads(CUADERNO.read_text(encoding="utf-8"))
    import matplotlib, warnings
    matplotlib.use("Agg")
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
    pares = [("ej_chi2", R["ej"]["chi2"]), ("ej_p", R["ej"]["p"]), ("ej_V", R["ej"]["V"]),
             ("caso_chi2", R["caso"]["chi2"]), ("caso_p", R["caso"]["p"]), ("caso_gl", R["caso"]["gl"]),
             ("caso_V", R["caso"]["V"])]
    malos = [k for k, v in pares if abs(RES[k] - v) > 1e-9]
    if not np.allclose(RES["caso_ajustados"], R["caso"]["ajustado"]):
        malos.append("caso_ajustados")
    print("CUADERNO:", "OK, reproduce el ejemplo y el caso" if not malos else f"difiere en {malos}")
    return not malos


def cadena(R):
    caso, D = R["_caso_mod"], R["_D"]
    C = caso.calcular(D)["u4"]
    c = R["caso"]
    ok = (abs(C["chi2"] - c["chi2"]) < 1e-9 and C["gl"] == c["gl"] and abs(C["p"] - c["p"]) < 1e-12
          and abs(C["v_cramer"] - c["V"]) < 1e-12)
    print("CADENA:", "OK, la pieza u4 del caso calza (χ², gl, p y V de Cramér)" if ok else "NO calza")
    return ok


# ---------------------------------------------------------------- impresión

def mostrar(nombre, q, dec_e=2):
    print(f"== {nombre}: χ² {fmt(q['chi2'], 2)} gl {q['gl']} crit {fmt(q['crit'], 2)} p {fmt(q['p'], 4)} V {fmt(q['V'], 3)} emin {fmt(q['emin'], 2)} (<5: {q['bajo5']})")
    print("     E", [[fmt(v, dec_e) for v in f] for f in q["E"]])
    print("     aportes", [[fmt(v, 2) for v in f] for f in q["contrib"]])
    print("     ajustados", [[fmt(v, 2) for v in f] for f in q["ajustado"]])


def imprimir(R):
    for k in ("ej", "e1", "e2", "e2_y", "e5", "e6", "e6_c", "e7", "e8a", "e8a_y", "e8b", "e10_chi", "e10_y", "caso"):
        mostrar(k, R[k])
    print("== 4.2 z", R["e2_z"])
    print("== 4.3", {k: fmt(v, 4) for k, v in R["e3"].items()})
    print("== 4.4", {k: {kk: fmt(vv, 4) for kk, vv in v.items()} for k, v in R["e4"].items()})
    for z, q in R["e9"].items():
        print(f"== 4.9 {z}: tasas {[pct(t, 1) for t in q['tasas']]} χ² {fmt(q['chi']['chi2'], 2)} p {fmt(q['chi']['p'], 3)} emin {fmt(q['chi']['emin'], 2)}"
              + (f" Fisher {fmt(q['fisher']['p'], 3)}" if "fisher" in q else ""))
    f = R["e10"]
    print("== 4.10 Fisher", {k: fmt(v, 4) for k, v in f["probs"].items()}, "p obs", fmt(f["p_obs"], 4), "p", fmt(f["p"], 3), "C", f["total"])
    c = R["caso"]
    print("== caso pearson", [[fmt(v, 2) for v in f_] for f_ in c["pearson"]])
    print("   % fila", [[pct(v, 1) for v in f_] for f_ in c["O"] / c["fi"][:, None]], "% total col", [pct(v, 1) for v in c["fj"] / c["n"]])


# ---------------------------------------------------------------- revisión contra el texto

def tabla_esperados(q, filas, dec=2):
    return [fila(f, *(fmt(v, dec) for v in row)) for f, row in zip(filas, q["E"])]


def esperados(R):
    E = []
    q = R["ej"]
    E += [fila(f, *map(str, row), str(int(sum(row)))) for f, row in zip(EJ_FILAS, EJ)]
    E += [fila("Total", *(str(int(v)) for v in q["fj"]), str(int(q["n"])))]
    E += [fila(f, *(f"{fmt(o, 0)} · {fmt(e, 2)}" for o, e in zip(oo, ee))) for f, oo, ee in zip(EJ_FILAS, q["O"], q["E"])]
    E += [fila(f, *(fmt(v, 2) for v in row)) for f, row in zip(EJ_FILAS, q["contrib"])]
    E += [fila(f, *(fmt(v, 2) for v in row)) for f, row in zip(EJ_FILAS, q["ajustado"])]
    E += [fmt(q["chi2"], 2), fmt(q["crit"], 2), fmt(q["p"], 4), fmt(q["V"], 3)]
    # 4.1
    q = R["e1"]
    E += [fila(f, *map(str, row)) for f, row in zip(E1["filas"], E1["t"])]
    E += tabla_esperados(q, E1["filas"]) + [fmt(q["chi2"], 2), fmt(q["crit"], 2), fmt(q["p"], 3), fmt(q["V"], 3)]
    # 4.2
    q, qy, z = R["e2"], R["e2_y"], R["e2_z"]
    E += [fila(f, *map(str, row)) for f, row in zip(E2["filas"], E2["t"])]
    E += [fmt(v, 2) for v in q["E"].ravel()]
    E += [fmt(q["chi2"], 2), fmt(q["p"], 3), fmt(qy["chi2"], 2), fmt(qy["p"], 3), fmt(q["V"], 3),
          pct(z["p1"], 1), pct(z["p2"], 1), fmt(z["z"], 2)]
    # 4.3, 4.4
    q = R["e3"]; E += [fmt(q["crit"], 2), fmt(q["p"], 3), fmt(q["V"], 3)]
    E += [fmt(R["e4"]["A"]["V"], 3), fmt(R["e4"]["A"]["p"], 4), fmt(R["e4"]["B"]["V"], 3)]
    # 4.5
    q = R["e5"]
    E += [fila(f, *map(str, row)) for f, row in zip(E5["filas"], E5["t"])]
    E += tabla_esperados(q, E5["filas"])
    E += [fila(f, *(fmt(v, 2) for v in row)) for f, row in zip(E5["filas"], q["ajustado"])]
    E += [fmt(q["chi2"], 2), fmt(q["V"], 3)]
    # 4.6
    q, qc = R["e6"], R["e6_c"]
    E += [fila(f, *map(str, row)) for f, row in zip(E6["filas"], E6["t"])]
    E += tabla_esperados(q, E6["filas"])
    E += [fmt(qc["chi2"], 2), fmt(qc["p"], 3), fmt(qc["emin"], 2), fmt(q["chi2"], 2), fmt(q["p"], 3)]
    # 4.7
    q = R["e7"]
    E += [fila(f, *map(str, row)) for f, row in zip(E7["filas"], E7["t"])]
    E += [fila(f, *(pct(v, 1) for v in row / row.sum())) for f, row in zip(E7["filas"], q["O"])]
    E += [fmt(q["chi2"], 2), fmt(q["p"], 3), fmt(q["V"], 3)]
    E += [fila(f, *(fmt(v, 2) for v in row)) for f, row in zip(E7["filas"], q["ajustado"])]
    # 4.8
    E += [fmt(R["e8a"]["chi2"], 2), fmt(R["e8a"]["p"], 3), fmt(R["e8b"]["chi2"], 2), fmt(R["e8a"]["V"], 3),
          fmt(R["e8a_y"]["chi2"], 2), fmt(R["e8a_y"]["p"], 3)]
    # 4.9
    for zona in ("urbana", "rural"):
        t = E9[zona]
        E.append(fila(zona, *(f"{a}/{a + b}" for a, b in t), *(pct(x, 1) for x in R["e9"][zona]["tasas"])))
    tt = R["e9"]["total"]["t"]
    E.append(fila("total", *(f"{a}/{a + b}" for a, b in tt), *(pct(x, 1) for x in R["e9"]["total"]["tasas"])))
    E += [fmt(R["e9"]["urbana"]["fisher"]["p"], 3), fmt(R["e9"]["urbana"]["chi"]["emin"], 2),
          fmt(R["e9"]["rural"]["chi"]["chi2"], 2), fmt(R["e9"]["rural"]["chi"]["p"], 3),
          fmt(R["e9"]["total"]["chi"]["chi2"], 2), fmt(R["e9"]["total"]["chi"]["p"], 4)]
    # 4.10
    f = R["e10"]
    E += [fila(str(k), fmt(v, 4)) for k, v in f["probs"].items()]
    E += [fmt(f["total"], 0), fmt(f["p"], 3), fmt(R["e10_chi"]["chi2"], 2), fmt(R["e10_chi"]["p"], 3),
          fmt(R["e10_y"]["chi2"], 2), fmt(R["e10_y"]["p"], 3), fmt(R["e10_chi"]["emin"], 2)]
    # caso
    c = R["caso"]
    E += [fila(k, *map(str, row), str(int(sum(row)))) for k, row in zip(R["caso_canales"], c["O"].astype(int).tolist())]
    E += [fila("Total", *(str(int(v)) for v in c["fj"]), str(int(c["n"])))]
    E += tabla_esperados(c, R["caso_canales"])
    E += [fila(k, *(pct(v, 1) for v in row / row.sum())) for k, row in zip(R["caso_canales"], c["O"])]
    E += [fila("todos", *(pct(v, 1) for v in c["fj"] / c["n"]))]
    E += [fila(k, *(fmt(v, 2) for v in row)) for k, row in zip(R["caso_canales"], c["contrib"])]
    E += [fila(k, *(fmt(v, 2) for v in row)) for k, row in zip(R["caso_canales"], c["pearson"])]
    E += [fila(k, *(fmt(v, 2) for v in row)) for k, row in zip(R["caso_canales"], c["ajustado"])]
    E += [fmt(c["chi2"], 2), str(c["gl"]), fmt(c["crit"], 2), "p < 0,001", fmt(c["V"], 3), fmt(c["emin"], 2)]
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
        md = MD.read_text(encoding="utf-8").replace("{,}", ",").replace("{.}", ".").replace("\\ \\%", " %")
        faltan = [x for x in esperados(R) if x not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        ok = ok and not faltan
    sys.exit(0 if ok else 1)
