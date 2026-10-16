"""Unidad 4 · Pronósticos.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba
que cada resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto
queda sin respaldo. La pieza del caso integrador sale de caso_estampa_sur.py.

    python u04_pronosticos.py            # imprime los resultados
    python u04_pronosticos.py --revisar  # además los busca en el .md
"""
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import caso_estampa_sur as caso  # noqa: E402

# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s.replace("-", "−")


def pct(x, dec=1):
    """x ya viene en porcentaje (no en fracción)."""
    return fmt(x, dec) + " %"


# Convención de índices: D[t] y F[t] con t = 1..n (posición 0 sin uso). F[t] es el pronóstico
# del período t hecho al cierre de t−1. F[n+1] es el pronóstico del período siguiente.

def serie(lista):
    return [None] + list(lista)


def ingenuo(D):
    n = len(D) - 1
    return [None, None] + [D[t - 1] for t in range(2, n + 2)]


def promedio_movil(D, k):
    n = len(D) - 1
    return [None] * (k + 1) + [sum(D[t - k:t]) / k for t in range(k + 1, n + 2)]


def promedio_movil_ponderado(D, pesos):
    """pesos[0] es el del período más reciente."""
    k, n = len(pesos), len(D) - 1
    return [None] * (k + 1) + [sum(w * D[t - 1 - i] for i, w in enumerate(pesos)) for t in range(k + 1, n + 2)]


def suavizamiento(D, alfa, f1):
    """F[t+1] = F[t] + α (D[t] − F[t])."""
    n = len(D) - 1
    F = [None, f1]
    for t in range(1, n + 1):
        F.append(F[t] + alfa * (D[t] - F[t]))
    return F


def holt(D, alfa, beta):
    """Misma inicialización que el caso: nivel = D1, tendencia = D2 − D1.
    Devuelve F (F[2] en adelante), niveles, tendencias y el estado final."""
    n = len(D) - 1
    L, T = {1: D[1]}, {1: D[2] - D[1]}
    F = [None, None]
    for t in range(2, n + 1):
        F.append(L[t - 1] + T[t - 1])
        L[t] = alfa * D[t] + (1 - alfa) * (L[t - 1] + T[t - 1])
        T[t] = beta * (L[t] - L[t - 1]) + (1 - beta) * T[t - 1]
    F.append(L[n] + T[n])
    return F, L, T


def holt_futuro(L, T, n, k):
    return [L[n] + h * T[n] for h in range(1, k + 1)]


def errores(D, F, desde, hasta):
    """MAD, MSE, MAPE (%), suma de errores (RSFE), sesgo medio y señal de rastreo."""
    e = [D[t] - F[t] for t in range(desde, hasta + 1)]
    n = len(e)
    mad = sum(abs(x) for x in e) / n
    return {
        "e": e,
        "MAD": mad,
        "MSE": sum(x * x for x in e) / n,
        "MAPE": 100 * sum(abs(D[t] - F[t]) / D[t] for t in range(desde, hasta + 1)) / n,
        "RSFE": sum(e),
        "sesgo": sum(e) / n,
        "TS": sum(e) / mad,
    }


def senal_rastreo_corrida(D, F, desde, hasta):
    """Señal de rastreo período a período, con MAD acumulado desde 'desde'."""
    filas, suma, suma_abs = [], 0, 0
    for i, t in enumerate(range(desde, hasta + 1), start=1):
        e = D[t] - F[t]
        suma += e
        suma_abs += abs(e)
        mad = suma_abs / i
        filas.append((t, D[t], F[t], e, suma, mad, suma / mad if mad else None))
    return filas


def regresion(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum(a * b for a, b in zip(x, y))
    sxx = sum(a * a for a in x)
    b = (sxy - n * mx * my) / (sxx - n * mx * mx)
    a = my - b * mx
    yhat = [a + b * v for v in x]
    sse = sum((v - h) ** 2 for v, h in zip(y, yhat))
    sst = sum((v - my) ** 2 for v in y)
    r2 = 1 - sse / sst
    r = (1 if b >= 0 else -1) * r2 ** 0.5
    mad = sum(abs(v - h) for v, h in zip(y, yhat)) / n
    return {"n": n, "mx": mx, "my": my, "sxy": sxy, "sxx": sxx, "a": a, "b": b,
            "sse": sse, "sst": sst, "r2": r2, "r": r, "mad": mad, "yhat": yhat}


def indices_estacionales(tabla):
    """tabla: lista de años, cada uno con L estaciones. Índice = promedio de la estación / promedio general."""
    L = len(tabla[0])
    prom_est = [sum(año[s] for año in tabla) / len(tabla) for s in range(L)]
    prom_general = sum(prom_est) / L
    return prom_est, prom_general, [p / prom_general for p in prom_est]


def winter(D, L, alfa, beta, gamma):
    """Convención de las láminas del curso: F1 = D1, T1 = 0 y S = 1 en la temporada anterior.
    FITS[t] = (F[t−1] + T[t−1]) · S[t−L]; futuro: (F[n] + p·T[n]) · S[n−L+p]."""
    n = len(D) - 1
    S = {t: 1.0 for t in range(1 - L, 1)}
    F, T = {1: D[1]}, {1: 0.0}
    S[1] = gamma * D[1] / F[1] + (1 - gamma) * S[1 - L]
    FITS = {}
    for t in range(2, n + 1):
        FITS[t] = (F[t - 1] + T[t - 1]) * S[t - L]
        F[t] = alfa * D[t] / S[t - L] + (1 - alfa) * (F[t - 1] + T[t - 1])
        T[t] = beta * (F[t] - F[t - 1]) + (1 - beta) * T[t - 1]
        S[t] = gamma * D[t] / F[t] + (1 - gamma) * S[t - L]
    futuro = [(F[n] + p * T[n]) * S[n - L + p] for p in range(1, L + 1)]
    return F, T, S, FITS, futuro


def winter_desde_primer_año(D, L, alfa, beta, gamma):
    """Variante: índices iniciales = primer año / su promedio; nivel = promedio del primer año;
    tendencia = 0. Corre desde t = L+1."""
    n = len(D) - 1
    prom1 = sum(D[1:L + 1]) / L
    S = {t: D[t] / prom1 for t in range(1, L + 1)}
    F, T = {L: prom1}, {L: 0.0}
    FITS = {}
    for t in range(L + 1, n + 1):
        FITS[t] = (F[t - 1] + T[t - 1]) * S[t - L]
        F[t] = alfa * D[t] / S[t - L] + (1 - alfa) * (F[t - 1] + T[t - 1])
        T[t] = beta * (F[t] - F[t - 1]) + (1 - beta) * T[t - 1]
        S[t] = gamma * D[t] / F[t] + (1 - gamma) * S[t - L]
    futuro = [(F[n] + p * T[n]) * S[n - L + p] for p in range(1, L + 1)]
    return F, T, S, FITS, futuro


def mad_dict(D, FITS, desde, hasta):
    return sum(abs(D[t] - FITS[t]) for t in range(desde, hasta + 1)) / (hasta - desde + 1)


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Sección 6 · ejemplo de Holt: socios de un gimnasio de Los Ángeles (fin de mes)
HOLT_EJ = serie([520, 548, 571, 590, 622, 641])
HOLT_EJ_A, HOLT_EJ_B = 0.4, 0.3

# Ejemplo resuelto · bidones de 20 L despachados por semana, distribuidora de agua en Chillán
EJEMPLO = serie([412, 398, 431, 405, 446, 420, 389, 437, 452, 418, 441, 463])
PESOS_EJ = [0.6, 0.3, 0.1]          # más reciente primero
ALFAS_EJ = [0.2, 0.5]
VENTANA_EJ = (4, 12)                # semanas en que todos los métodos tienen pronóstico

# 4.1 · ferretería de Talca, cajas de tornillos por semana
E1 = serie([64, 71, 58, 67, 75, 62, 69, 73])
# 4.2 · lavandería industrial de Puerto Montt, kilos lavados por semana (cientos)
E2 = serie([236, 251, 244, 262, 270, 259, 281, 288])
PESOS_E2 = [0.7, 0.2, 0.1]
# 4.3 · farmacia de Coyhaique, cajas de un analgésico por mes; pronóstico inicial del mes 1 = 150
E3 = serie([152, 147, 160, 171, 158, 166, 179, 172])
E3_F1 = 150
ALFAS_E3 = [0.1, 0.4]
# 4.4 · panadería de Linares, kilos de pan por día: demanda real y pronóstico usado
E4_D = serie([318, 296, 335, 342, 327, 351])
E4_F = serie([305, 310, 312, 320, 330, 333])
# 4.5 · instaladora de paneles solares de Rancagua, kits instalados por mes
E5 = serie([34, 38, 41, 47, 50, 55, 58, 63, 68, 71])
E5_A, E5_B = 0.4, 0.2
# 4.6 · internet rural en la Araucanía, clientes con contrato (cientos), 2018 a 2025
E6_AÑOS = list(range(2018, 2026))
E6 = [23, 27, 32, 34, 40, 43, 49, 52]
# 4.7 · cadena de lavado de autos, ocho locales en el mismo mes:
#       flujo vehicular frente al local (miles de vehículos por día) y autos lavados en el mes
E7_X = [4.2, 6.8, 3.5, 8.1, 5.6, 7.3, 2.9, 6.1]
E7_Y = [1240, 1580, 1010, 1890, 1330, 1790, 820, 1600]
E7_NUEVOS = [5.0, 11.0]
# 4.8 · visitas trimestrales a un parque nacional de Los Lagos (cientos); T1 = verano
E8 = [[142, 61, 38, 97], [155, 66, 41, 104], [168, 70, 45, 111]]
E8_ANUAL = 410
# 4.9 · pastelería en línea de Concepción, pedidos por día (campaña desde el día 8)
E9 = serie([52, 49, 55, 50, 53, 51, 48, 66, 69, 64, 70, 67, 72, 68])
E9_ALFA = 0.2
E9_REJILLA = [round(0.1 * i, 1) for i in range(1, 10)]
# 4.10 · cooperativa de leña certificada de Aysén, m³ vendidos por trimestre (3 años)
E10 = serie([410, 820, 960, 380, 450, 890, 1030, 420, 480, 950, 1110, 450])
E10_L = 4
E10_A, E10_B, E10_G = 0.2, 0.2, 0.7

# Caso integrador: historia y parámetros desde caso_estampa_sur.py (no se copian acá)
CASO = serie(caso.HISTORIA)


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}

    # Holt, ejemplo de la sección 6
    F, L, T = holt(HOLT_EJ, HOLT_EJ_A, HOLT_EJ_B)
    n = len(HOLT_EJ) - 1
    R["holt_ej"] = {"F": F, "L": L, "T": T, "futuro": holt_futuro(L, T, n, 2),
                    "err": errores(HOLT_EJ, F, 3, n)}

    # Ejemplo resuelto
    D = EJEMPLO
    a, b = VENTANA_EJ
    metodos = {
        "Ingenuo": ingenuo(D),
        "PM3": promedio_movil(D, 3),
        "PMP3": promedio_movil_ponderado(D, PESOS_EJ),
        "SE α = 0,2": suavizamiento(D, 0.2, D[1]),
        "SE α = 0,5": suavizamiento(D, 0.5, D[1]),
    }
    R["ej"] = {m: {"F": F, "err": errores(D, F, a, b)} for m, F in metodos.items()}

    # 4.1
    R["e1"] = {}
    for nom, F in {"Ingenuo": ingenuo(E1), "PM3": promedio_movil(E1, 3), "PM4": promedio_movil(E1, 4)}.items():
        R["e1"][nom] = {"F": F, "err": errores(E1, F, 5, 8)}
    # 4.2
    R["e2"] = {}
    for nom, F in {"PM3": promedio_movil(E2, 3), "PMP3": promedio_movil_ponderado(E2, PESOS_E2)}.items():
        R["e2"][nom] = {"F": F, "err": errores(E2, F, 4, 8)}
    # 4.3
    R["e3"] = {al: {"F": (F := suavizamiento(E3, al, E3_F1)), "err": errores(E3, F, 1, 8)} for al in ALFAS_E3}
    # 4.4
    R["e4"] = errores(E4_D, E4_F, 1, 6)
    # 4.5
    F, L, T = holt(E5, E5_A, E5_B)
    S = suavizamiento(E5, E5_A, E5[1])
    R["e5"] = {"F": F, "L": L, "T": T, "futuro": holt_futuro(L, T, 10, 3),
               "err_holt": errores(E5, F, 3, 10), "S": S, "err_se": errores(E5, S, 3, 10)}
    # 4.6
    x6 = list(range(1, len(E6) + 1))
    reg6 = regresion(x6, E6)
    reg6["p2026"] = reg6["a"] + reg6["b"] * 9
    reg6["p2027"] = reg6["a"] + reg6["b"] * 10
    R["e6"] = reg6
    # 4.7
    reg7 = regresion(E7_X, E7_Y)
    reg7["nuevos"] = [reg7["a"] + reg7["b"] * v for v in E7_NUEVOS]
    R["e7"] = reg7
    # 4.8
    prom_est, prom_gen, idx = indices_estacionales(E8)
    base = E8_ANUAL / 4
    R["e8"] = {"prom_est": prom_est, "prom_gen": prom_gen, "idx": idx, "base": base,
               "pron": [base * i for i in idx], "suma_idx": sum(idx),
               "desest_a3": [v / i for v, i in zip(E8[2], idx)],
               "prom_años": [sum(a) / 4 for a in E8]}
    # 4.9
    F9 = suavizamiento(E9, E9_ALFA, E9[1])
    corrida = senal_rastreo_corrida(E9, F9, 2, 14)
    primer = next(f for f in corrida if f[6] is not None and abs(f[6]) > 4)
    rejilla = {al: errores(E9, suavizamiento(E9, al, E9[1]), 2, 14)["MAD"] for al in E9_REJILLA}
    mejor = min(rejilla, key=rejilla.get)
    R["e9"] = {"F": F9, "corrida": corrida, "primer": primer, "rejilla": rejilla, "mejor": mejor,
               "F_mejor_15": suavizamiento(E9, mejor, E9[1])[15], "F_02_15": F9[15]}
    # 4.10
    F, T, S, FITS, fut = winter(E10, E10_L, E10_A, E10_B, E10_G)
    F2, T2, S2, FITS2, fut2 = winter_desde_primer_año(E10, E10_L, E10_A, E10_B, E10_G)
    R["e10"] = {"F": F, "T": T, "S": S, "FITS": FITS, "futuro": fut,
                "mad_2_4": mad_dict(E10, FITS, 2, 4), "mad_5_12": mad_dict(E10, FITS, 5, 12),
                "prom_año1": sum(E10[1:5]) / 4, "v_FITS": FITS2, "v_futuro": fut2, "v_mad_5_12": mad_dict(E10, FITS2, 5, 12)}

    # Caso integrador
    filas_c, mad_c, nivel_c, tend_c, futuro_c = caso.holt(caso.HISTORIA, caso.ALFA, caso.BETA)
    Fc, Lc, Tc = holt(CASO, caso.ALFA, caso.BETA)
    # control cruzado: mi Holt y el del caso tienen que dar lo mismo
    assert all(abs(Fc[t] - p) < 1e-9 for t, _, p, _ in filas_c)
    assert abs(Lc[24] - nivel_c) < 1e-9 and abs(Tc[24] - tend_c) < 1e-9
    Sc = suavizamiento(CASO, caso.ALFA, CASO[1])
    C = caso.calcular()
    R["caso"] = {"filas": filas_c, "L": Lc, "T": Tc, "mad": mad_c, "nivel": nivel_c, "tend": tend_c,
                 "futuro": futuro_c, "redondeado": C["u4"]["pronostico_redondeado"],
                 "err_holt_2_24": errores(CASO, Fc, 2, 24), "err_holt_3_24": errores(CASO, Fc, 3, 24),
                 "err_se_3_24": errores(CASO, Sc, 3, 24), "se_25": Sc[25],
                 "err_holt_2_12": errores(CASO, Fc, 2, 12), "err_holt_13_24": errores(CASO, Fc, 13, 24),
                 "pendiente_media": (CASO[24] - CASO[1]) / 23,
                 "u5_demanda_anual": C["u5"]["demanda_anual"]}
    return R


def imprimir(R):
    h = R["holt_ej"]
    print("== Sección 6 · Holt gimnasio")
    for t in range(1, len(HOLT_EJ)):
        print(f"   t={t} D={HOLT_EJ[t]} F={'' if h['F'][t] is None else fmt(h['F'][t])} L={fmt(h['L'][t])} T={fmt(h['T'][t])}")
    print("   futuro", [fmt(x) for x in h["futuro"]], "MAD 3-6", fmt(h["err"]["MAD"]))

    print("== Ejemplo resuelto · bidones")
    for m, v in R["ej"].items():
        print(f"   {m:10} F4..F13 {[fmt(v['F'][t]) for t in range(4, 14)]}")
        e = v["err"]
        print(f"              e {[fmt(x) for x in e['e']]}")
        print(f"              MAD {fmt(e['MAD'])} MSE {fmt(e['MSE'])} MAPE {pct(e['MAPE'])} RSFE {fmt(e['RSFE'])} TS {fmt(e['TS'], 2)}")
    print("   SE F1..F3", {m: [fmt(R['ej'][m]['F'][t]) for t in (1, 2, 3)] for m in ("SE α = 0,2", "SE α = 0,5")})

    print("== 4.1")
    for m, v in R["e1"].items():
        print(f"   {m} F5..F9 {[fmt(v['F'][t]) for t in range(5, 10)]} MAD {fmt(v['err']['MAD'])}")
    print("== 4.2")
    for m, v in R["e2"].items():
        print(f"   {m} F4..F9 {[fmt(v['F'][t]) for t in range(4, 10)]} MAD {fmt(v['err']['MAD'])} TS {fmt(v['err']['TS'], 2)}")
    print("== 4.3")
    for al, v in R["e3"].items():
        print(f"   α={al} F1..F9 {[fmt(v['F'][t]) for t in range(1, 10)]} MAD {fmt(v['err']['MAD'])} TS {fmt(v['err']['TS'], 2)}")
    e = R["e4"]
    print("== 4.4 e", e["e"], "MAD", fmt(e["MAD"]), "MSE", fmt(e["MSE"]), "MAPE", pct(e["MAPE"]), "RSFE", e["RSFE"], "sesgo", fmt(e["sesgo"]), "TS", fmt(e["TS"], 2))
    v = R["e5"]
    print("== 4.5 Holt")
    for t in range(1, 11):
        print(f"   t={t} D={E5[t]} F={'' if v['F'][t] is None else fmt(v['F'][t], 2)} L={fmt(v['L'][t], 2)} T={fmt(v['T'][t], 2)} SE={fmt(v['S'][t], 2)}")
    print("   futuro", [fmt(x, 1) for x in v["futuro"]], "MAD Holt 3-10", fmt(v["err_holt"]["MAD"], 2), "TS", fmt(v["err_holt"]["TS"], 2),
          "| MAD SE", fmt(v["err_se"]["MAD"], 2), "TS SE", fmt(v["err_se"]["TS"], 2), "SE F11", fmt(v["S"][11], 1))
    r = R["e6"]
    print("== 4.6", {k: (fmt(r[k], 4) if isinstance(r[k], float) else r[k]) for k in ("n", "mx", "my", "sxy", "sxx", "a", "b", "sse", "sst", "r2", "mad", "p2026", "p2027")})
    print("   ajuste", [fmt(x, 2) for x in r["yhat"]])
    r = R["e7"]
    print("== 4.7", {k: (fmt(r[k], 4) if isinstance(r[k], float) else r[k]) for k in ("n", "mx", "my", "sxy", "sxx", "a", "b", "sse", "sst", "r2", "r", "mad")}, "nuevos", [fmt(x, 0) for x in r["nuevos"]])
    r = R["e8"]
    print("== 4.8 prom est", [fmt(x, 2) for x in r["prom_est"]], "prom gen", fmt(r["prom_gen"], 2), "idx", [fmt(x, 3) for x in r["idx"]],
          "suma", fmt(r["suma_idx"], 3), "base", fmt(r["base"], 1), "pron", [fmt(x, 1) for x in r["pron"]], "desest año 3", [fmt(x, 1) for x in r["desest_a3"]],
          "promedio por año", [fmt(x, 1) for x in r["prom_años"]])
    r = R["e9"]
    print("== 4.9 corrida (t, D, F, e, RSFE, MAD, TS)")
    for f in r["corrida"]:
        print("    ", f[0], f[1], fmt(f[2], 2), fmt(f[3], 2), fmt(f[4], 2), fmt(f[5], 2), "" if f[6] is None else fmt(f[6], 2))
    print("   primer |TS|>4: día", r["primer"][0], "TS", fmt(r["primer"][6], 2))
    print("   rejilla", {fmt(k): fmt(v, 2) for k, v in r["rejilla"].items()}, "mejor α", r["mejor"], "F15 mejor", fmt(r["F_mejor_15"], 1), "F15 α=0,2", fmt(r["F_02_15"], 1))
    r = R["e10"]
    print("== 4.10 Winter")
    for t in range(1, 13):
        print(f"   t={t} D={E10[t]} F={fmt(r['F'][t], 1)} T={fmt(r['T'][t], 2)} S={fmt(r['S'][t], 3)} FITS={'' if t not in r['FITS'] else fmt(r['FITS'][t], 1)}")
    print("   futuro", [fmt(x, 1) for x in r["futuro"]], "MAD 2-4", fmt(r["mad_2_4"], 1), "MAD 5-12", fmt(r["mad_5_12"], 1),
          "promedio año 1", fmt(r["prom_año1"], 1), "razón", fmt(r["mad_5_12"] / r["v_mad_5_12"], 2))
    print("   variante FITS", {t: fmt(x, 1) for t, x in r["v_FITS"].items()}, "futuro", [fmt(x, 1) for x in r["v_futuro"]], "MAD 5-12", fmt(r["v_mad_5_12"], 1))
    c = R["caso"]
    print("== Caso · Holt Estampa Sur")
    for (t, d, p, ae) in c["filas"]:
        print(f"   t={t} D={d} F={fmt(p, 1)} |e|={fmt(ae, 1)} L={fmt(c['L'][t], 1)} T={fmt(c['T'][t], 1)}")
    print("   MAD 2-24", fmt(c["mad"]), "MAD 3-24", fmt(c["err_holt_3_24"]["MAD"]), "TS 2-24", fmt(c["err_holt_2_24"]["TS"], 2),
          "MAPE 2-24", pct(c["err_holt_2_24"]["MAPE"]), "| SE α=0,3 MAD 3-24", fmt(c["err_se_3_24"]["MAD"]), "TS", fmt(c["err_se_3_24"]["TS"], 2), "SE F25", fmt(c["se_25"], 0))
    print("   Holt meses 2-12: MAD", fmt(c["err_holt_2_12"]["MAD"]), "TS", fmt(c["err_holt_2_12"]["TS"], 2),
          "| meses 13-24: MAD", fmt(c["err_holt_13_24"]["MAD"]), "TS", fmt(c["err_holt_13_24"]["TS"], 2),
          "| pendiente media", fmt(c["pendiente_media"]))
    print("   nivel", fmt(c["nivel"]), "tendencia", fmt(c["tend"]), "futuro", [fmt(x, 0) for x in c["futuro"]], "→", [fmt(x, 0) for x in c["redondeado"]],
          "| U5 demanda anual", fmt(c["u5_demanda_anual"], 0))


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    """Cadenas que el .md tiene que contener tal cual."""
    e = []
    h = R["holt_ej"]
    e += [fmt(x) for x in h["futuro"]] + [fmt(h["L"][6]), fmt(h["T"][6])]
    for m, v in R["ej"].items():
        er = v["err"]
        e += [fmt(er["MAD"]), fmt(er["MSE"]), pct(er["MAPE"]), fmt(er["TS"], 2), fmt(v["F"][13])]
    for v in R["e1"].values():
        e += [fmt(v["err"]["MAD"]), fmt(v["F"][9])]
    for v in R["e2"].values():
        e += [fmt(v["err"]["MAD"]), fmt(v["F"][9])]
    for v in R["e3"].values():
        e += [fmt(v["err"]["MAD"]), fmt(v["F"][9])]
    r = R["e4"]
    e += [fmt(r["MAD"]), fmt(r["MSE"]), pct(r["MAPE"]), fmt(r["TS"], 2)]
    v = R["e5"]
    e += [fmt(x, 1) for x in v["futuro"]] + [fmt(v["err_holt"]["MAD"], 2), fmt(v["err_se"]["MAD"], 2)]
    r = R["e6"]
    e += [fmt(r["a"], 2), fmt(r["b"], 2), fmt(r["r2"], 3), fmt(r["p2026"], 1), fmt(r["p2027"], 1)]
    r = R["e7"]
    e += [fmt(r["a"], 1), fmt(r["b"], 1), fmt(r["r"], 3), fmt(r["r2"], 3)] + [fmt(x, 0) for x in r["nuevos"]]
    r = R["e8"]
    e += [fmt(x, 3) for x in r["idx"]] + [fmt(x, 1) for x in r["pron"]] + [fmt(r["prom_gen"], 2)]
    e += [fmt(x, 1) for x in r["desest_a3"]] + [fmt(x, 1) for x in r["prom_años"]] + [fmt(r["base"], 1)]
    r = R["e9"]
    e += [f"día {r['primer'][0]}", fmt(r["primer"][6], 2), fmt(r["rejilla"][r["mejor"]], 2), fmt(r["mejor"]), fmt(r["F_mejor_15"], 1)]
    r = R["e10"]
    e += [fmt(x, 1) for x in r["futuro"]] + [fmt(r["mad_5_12"], 1), fmt(r["v_mad_5_12"], 1)] + [fmt(x, 1) for x in r["v_futuro"]]
    e += [fmt(r["mad_2_4"], 1), fmt(r["prom_año1"], 1), fmt(max(r["T"].values()), 2)]
    c = R["caso"]
    e += [fmt(c["mad"]), fmt(c["nivel"]), fmt(c["tend"]), fmt(c["err_holt_3_24"]["MAD"]), fmt(c["err_se_3_24"]["MAD"]),
          fmt(c["err_holt_2_24"]["TS"], 2), pct(c["err_holt_2_24"]["MAPE"]), fmt(c["err_se_3_24"]["TS"], 2),
          fmt(c["err_holt_2_12"]["MAD"]), fmt(c["err_holt_2_12"]["TS"], 2),
          fmt(c["err_holt_13_24"]["MAD"]), fmt(c["err_holt_13_24"]["TS"], 2), fmt(c["pendiente_media"])]
    e += [fmt(x, 0) for x in c["futuro"]] + [fmt(x, 0) for x in c["redondeado"]] + [fmt(c["u5_demanda_anual"], 0)]
    return e


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "04-pronosticos.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",")  # en LaTeX la coma decimal va como {,}
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
