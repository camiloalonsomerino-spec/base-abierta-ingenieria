"""Caso integrador de Finanzas · Valentina, dueña de Estampa Sur.

Una sola fuente para la cadena de cálculo del ramo. Cada unidad toma de acá sus datos de partida y
sus resultados; una cifra se cambia en un solo lugar y los verificadores lo notan.

    python caso_valentina.py          # imprime la cadena
    python caso_valentina.py --json   # la deja en caso_valentina.json

Todo es ficticio y original de esta base: personas, empresas, bonos, tasas y precios. Las tasas
no describen el mercado chileno de ninguna fecha.
"""
from math import log, sqrt
from pathlib import Path
from statistics import fmean
import json, random, sys

sys.stdout.reconfigure(encoding="utf-8")

# ------------------------------------------------------------------ datos
U1 = {"ahorro_hoy": 3_460_000, "tasa_mensual": 0.0055, "meses": 36}
U2 = {"banco_a_nominal": 0.066, "banco_a_cap": 12, "banco_b_efectiva": 0.0675, "inflacion": 0.034}
U3 = {"precio_depto": 98_400_000, "pie": 0.20}
U4 = {"tasa_anual_efectiva": 0.046, "anios": 20, "anios_alt": 25, "gastos_operacionales": 1_150_000}
U5 = {"pie_maquina": 5_550_000, "saldo_maquina": 8_750_000, "anio_saldo": 3,
      "flujos": [3_900_000, 4_200_000, 4_450_000, 4_450_000, 4_450_000], "residual": 1_800_000, "tasa": 0.12}
U6 = {"precios_cero": [95.42, 90.63, 85.77, 80.94, 76.18]}          # por cada 100 de nominal, plazos 1 a 5 años
U7 = {"cupon": 0.059, "plazo": 4, "nominal": 100}                      # bono ficticio «Eléctrica Andina»
U9 = {"dividendo_1": 86.40, "g": 0.032, "k_analistas": 0.11, "utilidad_por_accion": 118.00}
U10 = {"riqueza": 5_000_000, "escenarios": [(0.45, 0.28), (0.35, 0.06), (0.20, -0.22)], "deposito": 0.053}
U11 = {"E": {"Textil Andes": 0.134, "Fondo IPSA": 0.098}, "sigma": {"Textil Andes": 0.26, "Fondo IPSA": 0.175},
       "rho": 0.42, "aversion": 4}
U12 = {"meses": 12, "semilla": 2027, "beta_real": 1.30, "premio_mercado": 0.061, "beta_proyecto": 1.15}


# ------------------------------------------------------------------ cálculo
def vf(p, i, n): return p * (1 + i) ** n
def factor_vf_anualidad(i, n): return ((1 + i) ** n - 1) / i     # ojo con el −1
def factor_vp_anualidad(i, n): return (1 - (1 + i) ** -n) / i


def tir(flujos, lo=-0.9, hi=1.0):
    van = lambda r: sum(f / (1 + r) ** t for t, f in enumerate(flujos))
    for _ in range(200):
        mid = (lo + hi) / 2
        if van(lo) * van(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def precio_bono(flujos, tasas):
    return sum(f / (1 + r) ** t for t, (f, r) in enumerate(zip(flujos, tasas), start=1))


def calcular():
    C = {}
    # U1 · valor del dinero
    a, i, n = U1["ahorro_hoy"], U1["tasa_mensual"], U1["meses"]
    C["u1"] = {"vf_compuesto": vf(a, i, n), "vf_simple": a * (1 + i * n)}
    # U2 · tasas
    tea_a = (1 + U2["banco_a_nominal"] / U2["banco_a_cap"]) ** U2["banco_a_cap"] - 1
    real_a = (1 + tea_a) / (1 + U2["inflacion"]) - 1
    C["u2"] = {"tea_a": tea_a, "tea_b": U2["banco_b_efectiva"], "mensual_b": (1 + U2["banco_b_efectiva"]) ** (1 / 12) - 1,
               "real_a": real_a, "real_b": (1 + U2["banco_b_efectiva"]) / (1 + U2["inflacion"]) - 1}
    # U3 · ahorro para el pie
    meta = U3["precio_depto"] * U3["pie"]
    falta = meta - C["u1"]["vf_compuesto"]
    deposito = falta / factor_vf_anualidad(i, n)
    C["u3"] = {"meta_pie": meta, "vf_ahorro_hoy": C["u1"]["vf_compuesto"], "falta": falta, "deposito_mensual": deposito,
               "aportado": a + deposito * n, "comprobacion_vp": (a + deposito * factor_vp_anualidad(i, n)) * (1 + i) ** n}
    # U4 · hipotecario
    credito = U3["precio_depto"] - meta
    im = (1 + U4["tasa_anual_efectiva"]) ** (1 / 12) - 1
    def cuota(nm): return credito / factor_vp_anualidad(im, nm)
    c20, c25 = cuota(12 * U4["anios"]), cuota(12 * U4["anios_alt"])
    saldo, tabla = credito, []
    for m in range(1, 4):
        interes = saldo * im
        amort = c20 - interes
        saldo -= amort
        tabla.append({"mes": m, "cuota": c20, "interes": interes, "amortizacion": amort, "saldo": saldo})
    flujos_cae = [credito - U4["gastos_operacionales"]] + [-c20] * (12 * U4["anios"])
    cae_m = tir(flujos_cae, 0, 0.05)
    C["u4"] = {"credito": credito, "tasa_mensual": im, "cuota_20": c20, "cuota_25": c25,
               "interes_total_20": c20 * 240 - credito, "interes_total_25": c25 * 300 - credito,
               "tabla": tabla, "cae": 12 * cae_m,                # como la publica la norma: TIR mensual × 12
               "cae_efectiva": (1 + cae_m) ** 12 - 1}
    # U5 · segunda máquina de Estampa Sur
    fl = [-U5["pie_maquina"]] + list(U5["flujos"])
    fl[U5["anio_saldo"]] -= U5["saldo_maquina"]
    fl[-1] += U5["residual"]
    r = U5["tasa"]
    van = sum(f / (1 + r) ** t for t, f in enumerate(fl))
    C["u5"] = {"flujos": fl, "van": van, "tir": tir(fl), "vp_saldo": U5["saldo_maquina"] / (1 + r) ** U5["anio_saldo"]}
    # U6 · estructura de tasas
    spot = [(100 / p) ** (1 / t) - 1 for t, p in enumerate(U6["precios_cero"], start=1)]
    fwd = [(1 + spot[t]) ** (t + 1) / (1 + spot[t - 1]) ** t - 1 for t in range(1, len(spot))]
    C["u6"] = {"spot": spot, "forward_1_anio": fwd}
    # U7 · bono a 4 años con cupón 5,9 %
    cup = U7["cupon"] * U7["nominal"]
    flujos_b = [cup] * (U7["plazo"] - 1) + [cup + U7["nominal"]]
    precio = precio_bono(flujos_b, spot)
    ytm = tir([-precio] + flujos_b)
    C["u7"] = {"flujos": flujos_b, "precio": precio, "ytm": ytm, "sobre_la_par": precio > U7["nominal"]}
    # U8 · inmunizar el saldo de la máquina (a la YTM del bono, curva plana)
    y = ytm
    dur_b = sum(t * f / (1 + y) ** t for t, f in enumerate(flujos_b, start=1)) / precio
    dmod_b = dur_b / (1 + y)
    conv_b = sum(t * (t + 1) * f / (1 + y) ** (t + 2) for t, f in enumerate(flujos_b, start=1)) / precio
    H = U5["anio_saldo"]
    vp_pasivo = U5["saldo_maquina"] / (1 + y) ** H
    w_bono = (H - 1) / (dur_b - 1)           # mezcla con un cero a 1 año (duración 1)
    def valor_futuro_en_H(dy):
        yy = y + dy
        monto_cero = (1 - w_bono) * vp_pasivo * (1 + y)       # cobra el cero en t = 1 y reinvierte
        cero_en_H = monto_cero * (1 + yy) ** (H - 1)
        unidades = w_bono * vp_pasivo / precio
        bono_en_H = unidades * (sum(f * (1 + yy) ** (H - t) for t, f in enumerate(flujos_b[:H], start=1))
                                + sum(f / (1 + yy) ** (t - H) for t, f in enumerate(flujos_b, start=1) if t > H))
        return cero_en_H + bono_en_H
    C["u8"] = {"y": y, "duracion": dur_b, "duracion_mod": dmod_b, "convexidad": conv_b, "vp_pasivo": vp_pasivo,
               "peso_bono": w_bono, "monto_bono": w_bono * vp_pasivo, "monto_cero": (1 - w_bono) * vp_pasivo,
               "en_H_sin_cambio": valor_futuro_en_H(0), "en_H_sube_1pp": valor_futuro_en_H(0.01),
               "en_H_baja_1pp": valor_futuro_en_H(-0.01)}
    # U9 · Textil Andes
    p0 = U9["dividendo_1"] / (U9["k_analistas"] - U9["g"])
    sin_crec = U9["utilidad_por_accion"] / U9["k_analistas"]
    C["u9"] = {"precio_gordon": p0, "valor_sin_crecimiento": sin_crec, "pvgo": p0 - sin_crec,
               "payout": U9["dividendo_1"] / U9["utilidad_por_accion"]}
    # U10 · utilidad logarítmica
    W = U10["riqueza"]
    er = sum(p * x for p, x in U10["escenarios"])
    var = sum(p * (x - er) ** 2 for p, x in U10["escenarios"])
    eu = sum(p * log(W * (1 + x)) for p, x in U10["escenarios"])
    ec = __import__("math").exp(eu)
    C["u10"] = {"retorno_esperado": er, "desviacion": sqrt(var), "equivalente_cierto": ec,
                "premio_riesgo": W * (1 + er) - ec, "con_deposito": W * (1 + U10["deposito"]),
                "elige": "riesgosa" if ec > W * (1 + U10["deposito"]) else "depósito"}
    # U11 · portafolio
    e1, e2 = U11["E"]["Textil Andes"], U11["E"]["Fondo IPSA"]
    s1, s2 = U11["sigma"]["Textil Andes"], U11["sigma"]["Fondo IPSA"]
    cov = U11["rho"] * s1 * s2
    w_min = (s2 ** 2 - cov) / (s1 ** 2 + s2 ** 2 - 2 * cov)
    rf = spot[0]
    a1, a2 = e1 - rf, e2 - rf
    w_tan = (a1 * s2 ** 2 - a2 * cov) / (a1 * s2 ** 2 + a2 * s1 ** 2 - (a1 + a2) * cov)
    e_t = w_tan * e1 + (1 - w_tan) * e2
    s_t = sqrt(w_tan ** 2 * s1 ** 2 + (1 - w_tan) ** 2 * s2 ** 2 + 2 * w_tan * (1 - w_tan) * cov)
    y_opt = (e_t - rf) / (U11["aversion"] * s_t ** 2)
    C["u11"] = {"rf": rf, "cov": cov, "w_min_var": w_min,
                "e_min_var": w_min * e1 + (1 - w_min) * e2,
                "s_min_var": sqrt(w_min ** 2 * s1 ** 2 + (1 - w_min) ** 2 * s2 ** 2 + 2 * w_min * (1 - w_min) * cov),
                "w_tangente": w_tan, "e_tangente": e_t, "s_tangente": s_t, "sharpe": (e_t - rf) / s_t,
                "fraccion_riesgosa": y_opt}
    # U12 · beta por regresión y CAPM
    rnd = random.Random(U12["semilla"])
    rm = [round(rnd.gauss(0.008, 0.045), 4) for _ in range(U12["meses"])]
    ri = [round(0.001 + U12["beta_real"] * x + rnd.gauss(0, 0.03), 4) for x in rm]
    mx, mi = fmean(rm), fmean(ri)
    beta = sum((x - mx) * (z - mi) for x, z in zip(rm, ri)) / sum((x - mx) ** 2 for x in rm)
    k_capm = rf + beta * U12["premio_mercado"]
    p_capm = U9["dividendo_1"] / (k_capm - U9["g"])
    k_proy = rf + U12["beta_proyecto"] * U12["premio_mercado"]
    van_proy = sum(f / (1 + k_proy) ** t for t, f in enumerate(fl))
    C["u12"] = {"rm": rm, "ri": ri, "beta": beta, "alfa": mi - beta * mx, "k_capm": k_capm,
                "precio_con_capm": p_capm, "k_proyecto": k_proy, "van_proyecto_capm": van_proy}
    return C


def imprimir(C):
    for u, d in C.items():
        print(f"== {u}")
        for k, v in d.items():
            if isinstance(v, float):
                v = round(v, 6)
            elif isinstance(v, list) and v and isinstance(v[0], float):
                v = [round(x, 6) for x in v]
            print(f"   {k}: {v}")


if __name__ == "__main__":
    C = calcular()
    imprimir(C)
    if "--json" in sys.argv:
        Path(__file__).with_suffix(".json").write_text(json.dumps(C, ensure_ascii=False, indent=1), encoding="utf-8")
