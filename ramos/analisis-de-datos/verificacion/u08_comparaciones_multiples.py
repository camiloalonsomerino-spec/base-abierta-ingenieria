"""Unidad 8 · Comparaciones múltiples.

Recalcula todas las cifras de la unidad desde los datos (a mano, con la distribución del rango
studentizado, la t de Student y la de Dunnett, y con statsmodels y scipy, y exige que coincidan),
genera los gráficos de `unidades/figuras/` y el CSV del ejemplo en `datos/`, ejecuta el cuaderno
`notebooks/u08_comparaciones_multiples.ipynb`, compara la pieza del caso con
`caso_estampa_sur_datos.py` y, con --revisar, busca cada cifra en el .md.

    python u08_comparaciones_multiples.py            # imprime los resultados
    python u08_comparaciones_multiples.py --revisar  # además los busca en el .md
"""
from pathlib import Path
from itertools import combinations
import importlib.util, io, json, os, sys, contextlib

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
DATOS = RAMO / "datos"
FIG = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "08-comparaciones-multiples.md"
CUADERNO = RAMO / "notebooks" / "u08_comparaciones_multiples.ipynb"
ALFA = 0.05


# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    s = f"{x:,.{dec}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s[1:] if s.startswith("-") and float(s.replace(".", "").replace(",", ".")) == 0 else s


def fp(p, dec=3):
    return "p < 0,001" if p < 0.001 else f"p = {fmt(p, dec)}"


def pv(p, dec=3):
    """Valor p en una celda de tabla: «< 0,001» o la cifra."""
    return "< 0,001" if p < 0.001 else fmt(p, dec)


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def comparar(G, alfa=ALFA):
    """Todas las comparaciones de pares de un ANOVA de un factor: sin corregir, Bonferroni, Tukey(-Kramer) y Scheffé.
    Usa el CME del ANOVA. Devuelve la tabla y los valores críticos."""
    nombres = list(G)
    k = len(G)
    n = {g: len(v) for g, v in G.items()}
    m = {g: float(np.mean(v)) for g, v in G.items()}
    N = sum(n.values())
    gle = N - k
    sce = sum(float(((np.asarray(v, float) - m[g]) ** 2).sum()) for g, v in G.items())
    mce = sce / gle
    gm = sum(float(np.sum(v)) for v in G.values()) / N
    sctr = sum(n[g] * (m[g] - gm) ** 2 for g in G)
    F = (sctr / (k - 1)) / mce
    pares = list(combinations(nombres, 2))
    mm = len(pares)
    q = float(stats.studentized_range.ppf(1 - alfa, k, gle))
    tb = float(stats.t.ppf(1 - alfa / (2 * mm), gle))
    t0 = float(stats.t.ppf(1 - alfa / 2, gle))
    sch = float(np.sqrt((k - 1) * stats.f.ppf(1 - alfa, k - 1, gle)))
    filas = []
    for a, b in pares:
        d = m[b] - m[a]
        ee = np.sqrt(mce * (1 / n[a] + 1 / n[b]))
        t = d / ee
        p0 = float(2 * stats.t.sf(abs(t), gle))
        qs = abs(d) / np.sqrt(mce / 2 * (1 / n[a] + 1 / n[b]))     # Tukey-Kramer; con n iguales es |d|/√(CME/n)
        pt = float(stats.studentized_range.sf(qs, k, gle))
        hsd = q * np.sqrt(mce / 2 * (1 / n[a] + 1 / n[b]))
        filas.append({"a": a, "b": b, "d": d, "ee": ee, "t": t, "p0": p0, "pb": min(1.0, mm * p0), "q": qs, "pt": pt,
                      "hsd": hsd, "ic_t": (d - hsd, d + hsd), "dmin_b": tb * ee, "ic_b": (d - tb * ee, d + tb * ee),
                      "dmin_s": sch * ee, "ps": float(stats.f.sf(t ** 2 / (k - 1), k - 1, gle))})
    return {"k": k, "n": n, "m": m, "N": N, "gle": gle, "mce": mce, "F": F, "pF": float(stats.f.sf(F, k - 1, gle)),
            "m_pares": mm, "q": q, "tb": tb, "t0": t0, "sch": sch, "filas": filas}


def coincide_tukey(C, G):
    """La tabla a mano coincide con pairwise_tukeyhsd de statsmodels."""
    y = np.concatenate([np.asarray(v, float) for v in G.values()])
    lab = np.concatenate([[g] * len(v) for g, v in G.items()])
    tk = pairwise_tukeyhsd(y, lab, alpha=ALFA)
    datos = {(r[0], r[1]): r for r in tk.summary().data[1:]}
    for f in C["filas"]:
        if (f["a"], f["b"]) in datos:
            r = datos[(f["a"], f["b"])]; sg = 1
        else:
            r = datos[(f["b"], f["a"])]; sg = -1
        assert abs(sg * f["d"] - r[2]) < 1e-3
        assert abs(f["pt"] - r[3]) < 1e-3, (f["a"], f["b"], f["pt"], r[3])
        assert abs(sg * (f["ic_t"][0] if sg == 1 else f["ic_t"][1]) - r[4]) < 1e-3
        assert (f["pt"] < ALFA) == bool(r[6])
    return tk


def dunnett(G, control):
    otros = [g for g in G if g != control]
    r = stats.dunnett(*[np.asarray(G[g], float) for g in otros], control=np.asarray(G[control], float), rng=np.random.default_rng(1))
    ic = r.confidence_interval(1 - ALFA)
    C = comparar(G)
    out = {}
    for i, g in enumerate(otros):
        d = float(np.mean(G[g]) - np.mean(G[control]))
        ee = float(np.sqrt(C["mce"] * (1 / len(G[g]) + 1 / len(G[control]))))
        crit = float((ic.high[i] - ic.low[i]) / 2 / ee)
        assert abs(r.statistic[i] - d / ee) < 1e-9
        out[g] = {"d": d, "ee": ee, "t": float(r.statistic[i]), "p": float(r.pvalue[i]), "crit": crit,
                  "ic": (float(ic.low[i]), float(ic.high[i]))}
    crits = [v["crit"] for v in out.values()]
    assert max(crits) - min(crits) < 1e-6
    for v in out.values():
        assert (abs(v["t"]) > v["crit"]) == (v["p"] < ALFA)
    return out


def letras(C):
    """Letras de agrupamiento (medias ordenadas de menor a mayor; misma letra = no difieren según Tukey)."""
    orden = sorted(C["m"], key=C["m"].get)
    dif = {}
    for f in C["filas"]:
        dif[(f["a"], f["b"])] = dif[(f["b"], f["a"])] = f["pt"] < ALFA
    bloques = []
    for i in range(len(orden)):
        j = i
        while j + 1 < len(orden) and not any(dif[(orden[x], orden[j + 1])] for x in range(i, j + 1)):
            j += 1
        if not any(b[0] <= i and j <= b[1] for b in bloques):
            bloques.append((i, j))
    L = {g: "" for g in orden}
    for li, (i, j) in enumerate(bloques):
        for x in range(i, j + 1):
            L[orden[x]] += "abcdefgh"[li]
    # comprobación: dos grupos comparten letra si y solo si Tukey no los separa
    for a, b in combinations(orden, 2):
        assert (len(set(L[a]) & set(L[b])) > 0) == (not dif[(a, b)])
    return orden, L


def fila_de(C, a, b):
    for f in C["filas"]:
        if (f["a"], f["b"]) == (a, b):
            return f
    raise KeyError((a, b))


# ---------------------------------------------------------------- datos (originales; pasados por herramientas/colisiones.py)

# Ejemplo resuelto · cosecha de arándanos en Ñuble: kg por hora de un cosechero con el capacho actual
# (control) y tres capachos nuevos; 20 cosecheros asignados al azar, 5 por capacho
EJ = {"actual": [9.83, 10.42, 9.47, 10.11, 10.17], "liviano": [10.94, 11.58, 10.71, 11.33, 11.44],
      "arnés": [10.27, 11.03, 10.12, 10.79, 10.64], "doble": [10.53, 11.12, 9.97, 10.92, 10.90]}
EJ_CONTROL = "actual"

# 8.1 · número de grupos
E1_K = [3, 5, 7]

# 8.2 · cuatro mezclas de sustrato para almácigos: gramos por bandeja, n = 6 por mezcla, CME y gl del ANOVA
E2 = {"medias": {"A": 15.2, "B": 17.9, "C": 16.1, "D": 19.0}, "n": 6, "MCE": 2.4, "glE": 20}

# 8.3 · tiempo de pago (s) en tres versiones de la página de una tienda en línea, 8 compras por versión
E3 = {"V1": [186, 169, 203, 181, 163, 197, 192, 175], "V2": [157, 175, 145, 168, 151, 163, 179, 156],
      "V3": [181, 197, 174, 205, 188, 169, 211, 193]}

# 8.4 · seis valores p sin corregir de un estudio de comparaciones
E4 = [0.003, 0.006, 0.012, 0.030, 0.200, 0.640]

# 8.5 · los datos del ejercicio 7.5 (horas hasta responder un reclamo según canal, desbalanceado)
E5 = {"correo": [26, 31, 28, 35], "formulario web": [22, 18, 25, 20, 24, 23], "teléfono": [15, 19, 14, 17, 20]}

# 8.6 · resistencia (MPa) de uniones de tableros: adhesivo actual (control) y tres nuevos, 6 probetas cada uno
E6 = {"actual": [8.42, 9.07, 8.71, 8.93, 8.18, 8.84], "A1": [9.03, 9.58, 9.31, 8.82, 9.47, 9.41],
      "A2": [8.62, 9.19, 8.48, 9.04, 8.87, 8.73], "A3": [9.38, 9.93, 9.61, 9.24, 10.08, 9.66]}
E6_CONTROL = "actual"

# 8.7 · contraste con los datos resumidos de 8.2: mezclas con compost (B, D) contra sin compost (A, C)
E7_C = {"A": -0.5, "B": 0.5, "C": -0.5, "D": 0.5}

# 8.8 · minutos para armar un mueble con cuatro versiones del instructivo, 5 personas por versión
E8 = {"V1": [41, 47, 44, 38, 45], "V2": [44, 41, 47, 40, 45], "V3": [44, 50, 47, 53, 47], "V4": [48, 45, 51, 47, 51]}
E8_C = {"V1": -0.5, "V2": -0.5, "V3": 0.5, "V4": 0.5}

# 8.9 · simulación: k = 5 grupos con la misma media, n = 8, σ = 1
E9 = {"k": 5, "n": 8, "rep": 20_000, "semilla": 708}

# 8.10 · tamaño de muestra para que el HSD de Tukey sea a lo más 1,0 con σ ≈ 1,2 y k = 4
E10 = {"k": 4, "sigma": 1.2, "hsd": 1.0}


# ---------------------------------------------------------------- caso

def cargar_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_datos.py")
    caso = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caso)
    return caso


TINTAS = ["agua", "descarga", "plastisol"]       # el orden alfabético que usa la salida de Tukey


# ---------------------------------------------------------------- resultados

def contraste(medias, coef, n, mce, gle, k):
    L = sum(coef[g] * medias[g] for g in coef)
    ee = float(np.sqrt(mce * sum(c ** 2 for c in coef.values()) / n))
    t = L / ee
    return {"L": L, "ee": ee, "t": t, "t0": float(stats.t.ppf(1 - ALFA / 2, gle)), "p0": float(2 * stats.t.sf(abs(t), gle)),
            "sch": float(np.sqrt((k - 1) * stats.f.ppf(1 - ALFA, k - 1, gle))),
            "ps": float(stats.f.sf(t ** 2 / (k - 1), k - 1, gle))}


def resultados():
    R = {}
    # Ejemplo
    C = comparar(EJ)
    assert abs(stats.f_oneway(*EJ.values()).statistic - C["F"]) < 1e-9
    tk = coincide_tukey(C, EJ)
    D = dunnett(EJ, EJ_CONTROL)
    orden, L = letras(C)
    df = pd.DataFrame([{"capacho": g, "kg_hora": y} for g, v in EJ.items() for y in v])
    R["ej"] = {"C": C, "D": D, "orden": orden, "L": L, "df": df, "tk": tk,
               "sig0": sum(f["p0"] < ALFA for f in C["filas"]), "sigb": sum(f["pb"] < ALFA for f in C["filas"]),
               "sigt": sum(f["pt"] < ALFA for f in C["filas"]), "sigd": sum(v["p"] < ALFA for v in D.values()),
               "hsd_n": C["q"] * np.sqrt(C["mce"] / 5)}

    # 8.1
    R["e1"] = {k: {"m": k * (k - 1) // 2, "alfa_b": ALFA / (k * (k - 1) // 2),
                   "fwer": 1 - (1 - ALFA) ** (k * (k - 1) // 2),
                   "fwer_b": 1 - (1 - ALFA / (k * (k - 1) // 2)) ** (k * (k - 1) // 2)} for k in E1_K}

    # 8.2 · Tukey desde el resumen
    me, n2, mce2, gl2 = E2["medias"], E2["n"], E2["MCE"], E2["glE"]
    q2 = float(stats.studentized_range.ppf(1 - ALFA, len(me), gl2))
    hsd2 = q2 * np.sqrt(mce2 / n2)
    pares2 = {(a, b): me[b] - me[a] for a, b in combinations(me, 2)}
    C2 = {"m": me, "filas": [{"a": a, "b": b, "pt": float(stats.studentized_range.sf(abs(d) / np.sqrt(mce2 / n2), len(me), gl2))}
                             for (a, b), d in pares2.items()]}
    for f in C2["filas"]:
        assert (f["pt"] < ALFA) == (abs(pares2[(f["a"], f["b"])]) > hsd2)
    orden2, L2 = letras(C2)
    R["e2"] = {"q": q2, "hsd": hsd2, "pares": pares2, "sig": {k: abs(v) > hsd2 for k, v in pares2.items()},
               "orden": orden2, "L": L2, "ee": float(np.sqrt(mce2 / n2))}

    # 8.3
    C3 = comparar(E3)
    tk3 = coincide_tukey(C3, E3)
    R["e3"] = {"C": C3, "tk": tk3}

    # 8.4 · Bonferroni y Holm
    m4 = len(E4)
    bonf = [min(1.0, m4 * p) for p in E4]
    orden4 = sorted(range(m4), key=lambda i: E4[i])
    holm = [0.0] * m4
    acum = 0.0
    for r, i in enumerate(orden4):
        acum = max(acum, min(1.0, (m4 - r) * E4[i]))
        holm[i] = acum
    from statsmodels.stats.multitest import multipletests
    assert np.allclose(multipletests(E4, method="bonferroni")[1], bonf)
    assert np.allclose(multipletests(E4, method="holm")[1], holm)
    R["e4"] = {"bonf": bonf, "holm": holm, "nb": sum(p < ALFA for p in bonf), "nh": sum(p < ALFA for p in holm)}

    # 8.5 · Tukey-Kramer
    C5 = comparar(E5)
    coincide_tukey(C5, E5)
    R["e5"] = {"C": C5}

    # 8.6 · Dunnett frente a Tukey y Bonferroni con 3 comparaciones
    C6 = comparar(E6)
    coincide_tukey(C6, E6)
    D6 = dunnett(E6, E6_CONTROL)
    tb3 = float(stats.t.ppf(1 - ALFA / (2 * 3), C6["gle"]))
    ee6 = D6["A1"]["ee"]
    R["e6"] = {"C": C6, "D": D6, "tb3": tb3, "ee": ee6,
               "dmin": {"Dunnett": D6["A1"]["crit"] * ee6, "Bonferroni (3)": tb3 * ee6,
                        "Tukey": C6["q"] * np.sqrt(C6["mce"] / 6), "sin corregir": C6["t0"] * ee6},
               "pb3": {g: min(1.0, 3 * 2 * float(stats.t.sf(abs(v["t"]), C6["gle"]))) for g, v in D6.items()}}

    # 8.7 · contraste de Scheffé con el resumen de 8.2
    k2 = len(me)
    c7 = contraste(me, E7_C, n2, mce2, gl2, k2)
    ee_par = float(np.sqrt(mce2 * 2 / n2))
    R["e7"] = {"c": c7, "ee_par": ee_par, "dmin_s": c7["sch"] * ee_par, "dmin_t": hsd2,
               "dmin_b": float(stats.t.ppf(1 - ALFA / 12, gl2)) * ee_par}

    # 8.8 · F significativo y ningún par según Tukey; el contraste de Scheffé sí
    C8 = comparar(E8)
    coincide_tukey(C8, E8)
    assert C8["pF"] < ALFA and all(f["pt"] >= ALFA for f in C8["filas"])
    c8 = contraste(C8["m"], E8_C, 5, C8["mce"], C8["gle"], C8["k"])
    assert c8["ps"] < ALFA
    # el F es el máximo de los contrastes de Scheffé: F(k−1) = t² del contraste óptimo
    medias8 = np.array([C8["m"][g] for g in E8]); gm8 = medias8.mean()
    copt = medias8 - gm8
    Lopt = float(copt @ medias8); eeopt = float(np.sqrt(C8["mce"] * (copt ** 2).sum() / 5))
    assert abs((Lopt / eeopt) ** 2 / (C8["k"] - 1) - C8["F"]) < 1e-9
    R["e8"] = {"C": C8, "c": c8}

    # 8.9 · simulación de la tasa de error por familia
    rng = np.random.default_rng(E9["semilla"])
    k9, n9, rep = E9["k"], E9["n"], E9["rep"]
    Y = rng.normal(0, 1, size=(rep, k9, n9))
    medias = Y.mean(axis=2)
    gle9 = k9 * (n9 - 1)
    mce9 = ((Y - medias[:, :, None]) ** 2).sum(axis=(1, 2)) / gle9
    m9 = k9 * (k9 - 1) // 2
    ii, jj = np.triu_indices(k9, 1)
    dif = np.abs(medias[:, ii] - medias[:, jj])
    tst = dif / np.sqrt(mce9[:, None] * 2 / n9)
    t0 = stats.t.ppf(1 - ALFA / 2, gle9)
    tb = stats.t.ppf(1 - ALFA / (2 * m9), gle9)
    q9 = stats.studentized_range.ppf(1 - ALFA, k9, gle9)
    rango = (medias.max(axis=1) - medias.min(axis=1)) / np.sqrt(mce9 / n9)
    Fsim = (n9 * ((medias - medias.mean(axis=1, keepdims=True)) ** 2).sum(axis=1) / (k9 - 1)) / mce9
    R["e9"] = {"m": m9, "sin": float((tst > t0).any(axis=1).mean()), "bonf": float((tst > tb).any(axis=1).mean()),
               "tukey": float((rango > q9).mean()), "F": float((Fsim > stats.f.ppf(1 - ALFA, k9 - 1, gle9)).mean()),
               "teo_indep": 1 - (1 - ALFA) ** m9, "gle": gle9}
    # el máximo de las t de pares es el rango studentizado dividido por √2: Tukey = «mirar el par más distante»
    assert np.allclose(tst.max(axis=1) * np.sqrt(2), rango)

    # 8.10 · tamaño de muestra
    tabla10 = []
    n = 2
    while True:
        gle10 = E10["k"] * (n - 1)
        q10 = float(stats.studentized_range.ppf(1 - ALFA, E10["k"], gle10))
        h = q10 * E10["sigma"] / np.sqrt(n)
        tabla10.append((n, gle10, q10, h))
        if h <= E10["hsd"]:
            break
        n += 1
    R["e10"] = {"tabla": tabla10, "n": tabla10[-1][0]}

    # Caso · Tukey, Bonferroni y Dunnett con las tintas
    s = pd.read_csv(DATOS / "secado.csv")
    G = {t: list(s[s.tinta == t].secado_min) for t in TINTAS}
    Cc = comparar(G)
    tkc = coincide_tukey(Cc, G)
    Dc = dunnett({"plastisol": G["plastisol"], "agua": G["agua"], "descarga": G["descarga"]}, "plastisol")
    orden_c, Lc = letras(Cc)
    R["caso"] = {"s": s, "G": G, "C": Cc, "tk": tkc, "D": Dc, "orden": orden_c, "L": Lc,
                 "hsd": Cc["q"] * np.sqrt(Cc["mce"] / 10)}
    return R


# ---------------------------------------------------------------- CSV, figuras y cuaderno

def escribir_csv(R):
    R["ej"]["df"].to_csv(DATOS / "u08_ejemplo.csv", index=False, encoding="utf-8")


COL = ["#2B2F33", "#E2622A", "#5F8FB4", "#8A8F94"]


def grafico_intervalos(C, D, archivo, titulo, unidad, control=None):
    filas = C["filas"]
    fig, ax = plt.subplots(figsize=(6.6, 0.55 * len(filas) + 1.3), dpi=150)
    for i, f in enumerate(filas):
        y = len(filas) - 1 - i
        ax.plot(f["ic_b"], [y + 0.15] * 2, color=COL[2], lw=2.2, solid_capstyle="butt", label="Bonferroni" if i == 0 else None)
        ax.plot(f["ic_t"], [y - 0.05] * 2, color=COL[0], lw=2.2, solid_capstyle="butt", label="Tukey" if i == 0 else None)
        ax.plot(f["d"], y - 0.05, "o", color=COL[0], ms=4)
        if D is not None and control in (f["a"], f["b"]):
            g = f["b"] if f["a"] == control else f["a"]
            sg = 1 if f["a"] == control else -1
            lo, hi = D[g]["ic"]
            ic = (lo, hi) if sg == 1 else (-hi, -lo)
            ax.plot(ic, [y - 0.25] * 2, color=COL[1], lw=2.2, solid_capstyle="butt",
                    label="Dunnett" if not any(l.get_label() == "Dunnett" for l in ax.lines) else None)
    ax.axvline(0, color=COL[3], lw=1, ls="--")
    ax.set_yticks(range(len(filas)))
    ax.set_yticklabels([f"{f['b']} − {f['a']}" for f in filas][::-1])
    ax.set_xlabel(f"diferencia de medias ({unidad})")
    ax.set_title(titulo, fontsize=9.5)
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / archivo); plt.close(fig)


def graficos(R):
    FIG.mkdir(parents=True, exist_ok=True)
    e = R["ej"]
    grafico_intervalos(e["C"], e["D"], "u08_intervalos_ejemplo.png",
                       "Ejemplo: intervalos simultáneos al 95 % (si cruzan el 0, el par no difiere)", "kg/h", EJ_CONTROL)
    c = R["caso"]
    grafico_intervalos(c["C"], None, "u08_intervalos_caso.png",
                       "Caso: intervalos simultáneos al 95 % para las diferencias de secado", "min")
    fig, ax = plt.subplots(figsize=(6.0, 3.0), dpi=150)
    mm = np.arange(1, 46)
    ax.plot(mm, 1 - (1 - ALFA) ** mm, color=COL[1], lw=2, label="sin corregir (cada prueba al 5 %)")
    ax.plot(mm, 1 - (1 - ALFA / mm) ** mm, color=COL[2], lw=2, label="Bonferroni (cada prueba al 5 %/m)")
    for k in (3, 5, 7, 10):
        m = k * (k - 1) // 2
        ax.plot(m, 1 - (1 - ALFA) ** m, "o", color=COL[1], ms=4)
        ax.annotate(f"k = {k}", (m, 1 - (1 - ALFA) ** m), xytext=(4, -12), textcoords="offset points", fontsize=8)
    ax.set_xlabel("número de comparaciones m"); ax.set_ylabel("P(al menos una falsa alarma)")
    ax.set_ylim(0, 1); ax.legend(fontsize=8, frameon=False)
    ax.spines[["top", "right"]].set_visible(False); ax.grid(axis="y", color="#D6D3CE", lw=0.6)
    ax.set_title("Tasa de error por familia (pruebas independientes)", fontsize=9.5)
    fig.tight_layout(); fig.savefig(FIG / "u08_fwer.png"); plt.close(fig)


def ejecutar_cuaderno():
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
    ok = True
    for tk, C in ((ns["tukey_ejemplo"], R["ej"]["C"]), (ns["tukey_caso"], R["caso"]["C"])):
        ps = sorted(float(r[3]) for r in tk.summary().data[1:])
        ok &= np.allclose(ps, sorted(round(f["pt"], 4) for f in C["filas"]), atol=1e-4)
    ok &= np.allclose(sorted(ns["bonferroni_ejemplo"]), sorted(f["pb"] for f in R["ej"]["C"]["filas"]))
    ok &= np.allclose(sorted(ns["dunnett_ejemplo"].pvalue), sorted(v["p"] for v in R["ej"]["D"].values()), atol=1e-3)
    ok &= np.allclose(sorted(ns["bonferroni_caso"]), sorted(f["pb"] for f in R["caso"]["C"]["filas"]))
    print("CUADERNO:", "OK, reproduce el ejemplo y el caso" if ok else "NO coincide")
    return bool(ok)


def cadena(R):
    caso = cargar_caso()
    D = caso.generar()
    C = caso.calcular(D)
    s = R["caso"]["s"]
    ok = np.allclose(D["secado"].secado_min.values, s.secado_min.values) and (D["secado"].tinta.values == s.tinta.values).all()
    # la salida de Tukey del script del caso, fila por fila
    for fila in C["u8"]["tukey"]:
        a, b, d, p, lo, hi, rej = fila
        f = fila_de(R["caso"]["C"], a, b)
        ok &= abs(float(d) - round(f["d"], 4)) < 1e-9
        ok &= abs(float(p) - round(f["pt"], 4)) < 1e-9
        ok &= abs(float(lo) - round(f["ic_t"][0], 4)) < 1e-9 and abs(float(hi) - round(f["ic_t"][1], 4)) < 1e-9
        ok &= (rej == "True") == (f["pt"] < ALFA)
    ok &= abs(C["u7"]["F_tinta"] - R["caso"]["C"]["F"]) < 1e-9
    print("CADENA:", "OK, la pieza del caso calza con caso_estampa_sur_datos.py" if ok else "NO calza")
    return bool(ok)


# ---------------------------------------------------------------- impresión y revisión

def fila(*c):
    return "| " + " | ".join(c) + " |"


def imprimir_C(nombre, C):
    print(f"== {nombre}: medias {{{', '.join(f'{g}: {fmt(v, 3)}' for g, v in C['m'].items())}}} CME {fmt(C['mce'], 4)} glE {C['gle']} F {fmt(C['F'], 3)} {fp(C['pF'])}")
    print(f"   q {fmt(C['q'], 3)} tB {fmt(C['tb'], 3)} t0 {fmt(C['t0'], 3)} Scheffé {fmt(C['sch'], 3)} m {C['m_pares']}")
    for f in C["filas"]:
        print(f"   {f['b']} − {f['a']}: d {fmt(f['d'], 3)} ee {fmt(f['ee'], 4)} t {fmt(f['t'], 3)} p0 {pv(f['p0'], 4)} pB {pv(f['pb'], 3)} "
              f"q {fmt(f['q'], 3)} pT {pv(f['pt'], 4)} HSD {fmt(f['hsd'], 3)} ICT [{fmt(f['ic_t'][0], 3)}; {fmt(f['ic_t'][1], 3)}] "
              f"dminB {fmt(f['dmin_b'], 3)} ICB [{fmt(f['ic_b'][0], 3)}; {fmt(f['ic_b'][1], 3)}] dminS {fmt(f['dmin_s'], 3)} pS {pv(f['ps'], 3)}")


def imprimir(R):
    e = R["ej"]
    imprimir_C("Ejemplo", e["C"])
    print("   Dunnett", {g: (fmt(v["d"], 2), fmt(v["t"], 3), pv(v["p"], 4), fmt(v["crit"], 3), fmt(v["ic"][0], 3), fmt(v["ic"][1], 3)) for g, v in e["D"].items()})
    print("   letras", e["L"], "orden", e["orden"], "significativos: sin", e["sig0"], "B", e["sigb"], "T", e["sigt"], "D", e["sigd"], "HSD", fmt(e["hsd_n"], 3))
    print("== 8.1", {k: (v["m"], fmt(v["alfa_b"], 4), pct(v["fwer"]), pct(v["fwer_b"], 2)) for k, v in R["e1"].items()})
    x = R["e2"]
    print("== 8.2 q", fmt(x["q"], 3), "ee", fmt(x["ee"], 4), "HSD", fmt(x["hsd"], 3), {f"{b}−{a}": (fmt(d, 1), x["sig"][(a, b)]) for (a, b), d in x["pares"].items()}, x["L"])
    imprimir_C("8.3", R["e3"]["C"])
    print(R["e3"]["tk"])
    x = R["e4"]
    print("== 8.4 bonf", [fmt(p, 3) for p in x["bonf"]], "holm", [fmt(p, 3) for p in x["holm"]], x["nb"], x["nh"])
    imprimir_C("8.5", R["e5"]["C"])
    x = R["e6"]
    imprimir_C("8.6", x["C"])
    print("   Dunnett", {g: (fmt(v["d"], 3), fmt(v["t"], 3), pv(v["p"], 4), fmt(v["crit"], 3)) for g, v in x["D"].items()}, "tB3", fmt(x["tb3"], 3),
          "ee", fmt(x["ee"], 4), "dmin", {k: fmt(v, 3) for k, v in x["dmin"].items()}, "pB3", {g: pv(p, 4) for g, p in x["pb3"].items()})
    x = R["e7"]; c = x["c"]
    print("== 8.7 L", fmt(c["L"], 2), "ee", fmt(c["ee"], 4), "t", fmt(c["t"], 3), "t0", fmt(c["t0"], 3), "Scheffé", fmt(c["sch"], 3), fp(c["p0"]), fp(c["ps"]),
          "ee par", fmt(x["ee_par"], 4), "dmin S", fmt(x["dmin_s"], 3), "T", fmt(x["dmin_t"], 3), "B", fmt(x["dmin_b"], 3))
    x = R["e8"]
    imprimir_C("8.8", x["C"])
    c = x["c"]; print("   contraste L", fmt(c["L"], 2), "ee", fmt(c["ee"], 4), "t", fmt(c["t"], 3), "Scheffé", fmt(c["sch"], 3), fp(c["ps"]), "t0", fp(c["p0"]))
    x = R["e9"]
    print("== 8.9", {k: (pct(v, 1) if isinstance(v, float) else v) for k, v in x.items()})
    print("== 8.10", [(n, g, fmt(q, 3), fmt(h, 3)) for n, g, q, h in R["e10"]["tabla"]], "n", R["e10"]["n"])
    c = R["caso"]
    imprimir_C("Caso", c["C"])
    print(c["tk"])
    print("   Dunnett vs plastisol", {g: (fmt(v["d"], 2), fmt(v["t"], 3), pv(v["p"], 4), fmt(v["crit"], 3)) for g, v in c["D"].items()}, "letras", c["L"], "HSD", fmt(c["hsd"], 3))


def esperados(R):
    e = []
    # ejemplo
    E = R["ej"]; C = E["C"]
    e += [fila(g, *(fmt(y, 2) for y in v), fmt(C["m"][g], 3)) for g, v in EJ.items()]
    e += [fmt(C["mce"], 4), fmt(C["F"], 2), fp(C["pF"]), fmt(C["q"], 3), fmt(E["hsd_n"], 3), fmt(C["tb"], 3), fmt(C["t0"], 3)]
    for f in C["filas"]:
        e.append(fila(f"{f['b']} − {f['a']}", fmt(f["d"], 2), fmt(f["t"], 2), pv(f["p0"]), pv(f["pb"]), fmt(f["q"], 2), pv(f["pt"])))
        e.append(fila(f"{f['b']} − {f['a']}", fmt(f["ic_t"][0], 2), fmt(f["ic_t"][1], 2), fmt(f["ic_b"][0], 2), fmt(f["ic_b"][1], 2)))
    e += [fmt(f["dmin_b"], 3) for f in C["filas"][:1]] + [fmt(C["filas"][0]["ee"], 4)]
    for g, v in E["D"].items():
        e.append(fila(g, fmt(v["d"], 2), fmt(v["t"], 2), pv(v["p"]), fmt(v["ic"][0], 2), fmt(v["ic"][1], 2)))
    e += [fmt(E["D"]["liviano"]["crit"], 3), fmt(E["D"]["liviano"]["crit"] * E["D"]["liviano"]["ee"], 3)]
    e += [fila(g, fmt(C["m"][g], 2), E["L"][g]) for g in E["orden"]]
    # 8.1
    for k, v in R["e1"].items():
        e.append(fila(str(k), str(v["m"]), fmt(v["alfa_b"], 4), pct(v["fwer"]), pct(v["fwer_b"], 2)))
    # 8.2
    x = R["e2"]
    e += [fmt(x["q"], 3), fmt(x["hsd"], 2), fmt(x["ee"], 4)]
    e += [fila(g, fmt(E2["medias"][g], 1), x["L"][g]) for g in x["orden"]]
    # 8.3
    x = R["e3"]["C"]
    e += [fila(g, *map(str, v)) for g, v in E3.items()]
    e += [fmt(x["mce"], 4), fmt(x["q"], 3)]
    e += [fila(f["a"], f["b"], fmt(f["d"], 4), fmt(f["pt"], 4), fmt(f["ic_t"][0], 4), fmt(f["ic_t"][1], 4), str(f["pt"] < ALFA)) for f in x["filas"]]
    # 8.4
    x = R["e4"]
    e += [fila(fmt(p, 3), fmt(b, 3), fmt(h, 3)) for p, b, h in zip(E4, x["bonf"], x["holm"])]
    # 8.5
    x = R["e5"]["C"]
    e += [fmt(x["mce"], 3), fmt(x["q"], 3)]
    e += [fila(f"{f['b']} − {f['a']}", fmt(f["d"], 0), fmt(f["hsd"], 2), pv(f["pt"], 4), pv(f["pb"], 4)) for f in x["filas"]]
    # 8.6
    x = R["e6"]
    e += [fila(g, *(fmt(y, 2) for y in v)) for g, v in E6.items()]
    e += [fmt(x["C"]["mce"], 4), fmt(x["ee"], 4)]
    e += [fila(g, fmt(v["d"], 3), fmt(v["t"], 2), pv(v["p"]), pv(x["pb3"][g]), pv(fila_de(x["C"], "actual", g)["pt"] if g != "actual" else 0)) for g, v in x["D"].items()]
    e += [fila(k, fmt(v, 3)) for k, v in x["dmin"].items()]
    # 8.7
    x = R["e7"]; c = x["c"]
    e += [fmt(c["L"], 2), fmt(c["ee"], 4), fmt(c["t"], 2), fmt(c["sch"], 3), fmt(c["t0"], 3), fmt(x["ee_par"], 4),
          fmt(x["dmin_s"], 2), fmt(x["dmin_t"], 2), fmt(x["dmin_b"], 2)]
    # 8.8
    x = R["e8"]; C8 = x["C"]; c = x["c"]
    e += [fila(g, *map(str, v)) for g, v in E8.items()]
    e += [fmt(C8["F"], 2), fp(C8["pF"]), fmt(C8["mce"], 3)]
    e += [fila(f"{f['b']} − {f['a']}", fmt(f["d"], 1), pv(f["pt"])) for f in C8["filas"]]
    e += [fmt(c["L"], 1), fmt(c["ee"], 3), fmt(c["t"], 2), fmt(c["sch"], 3), fp(c["ps"])]
    # 8.9
    x = R["e9"]
    e += [pct(x["sin"]), pct(x["bonf"]), pct(x["tukey"]), pct(x["F"]), pct(x["teo_indep"])]
    # 8.10
    e += [fila(str(n), str(g), fmt(q, 3), fmt(h, 3)) for n, g, q, h in R["e10"]["tabla"][-3:]]
    # caso
    c = R["caso"]; Cc = c["C"]
    e += [fmt(Cc["mce"], 3), fmt(Cc["q"], 3), fmt(c["hsd"], 3), fmt(Cc["tb"], 3), fmt(Cc["filas"][0]["ee"], 4),
          fmt(Cc["filas"][0]["dmin_b"], 3)]
    for f in Cc["filas"]:
        e.append(fila(f["a"], f["b"], fmt(f["d"], 4), fmt(f["pt"], 4), fmt(f["ic_t"][0], 4), fmt(f["ic_t"][1], 4), str(f["pt"] < ALFA)))
        e.append(fila(f"{f['b']} − {f['a']}", fmt(f["d"], 2), fmt(f["t"], 2), pv(f["p0"]), pv(f["pb"]), pv(f["pt"])))
    e += [fp(v["p"]) for v in c["D"].values()]
    e += [fmt(c["D"]["agua"]["crit"], 3)]
    e += [fila(g, fmt(Cc["m"][g], 2), c["L"][g]) for g in c["orden"]]
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
