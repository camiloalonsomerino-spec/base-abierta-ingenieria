"""Unidad 4 · Créditos y tablas de amortización.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto queda sin respaldo.

    py -3 -P u04_creditos.py            # imprime los resultados
    py -3 -P u04_creditos.py --revisar  # además los busca en el .md

Todos los datos son originales de esta base. No vienen de ningún libro ni curso. Las tasas no
describen el mercado chileno de ninguna fecha.
"""
from math import log, ceil
from pathlib import Path
import importlib.util, sys

sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- herramientas

def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=2):
    return fmt(100 * x, dec) + " %"


def a_vp(i, n):
    return (1 - (1 + i) ** -n) / i


def cuota(P, i, n):
    """Cuota fija (sistema francés): P · i / (1 − (1+i)^−n)."""
    return P / a_vp(i, n)


def tabla_francesa(P, i, n, filas=None):
    c, saldo, t = cuota(P, i, n), P, []
    for m in range(1, n + 1):
        interes = saldo * i
        amort = c - interes
        saldo -= amort
        t.append(dict(mes=m, cuota=c, interes=interes, amort=amort, saldo=saldo))
    return t if filas is None else [t[k - 1] for k in filas]


def tabla_alemana(P, i, n):
    amort, saldo, t = P / n, P, []
    for m in range(1, n + 1):
        interes = saldo * i
        saldo -= amort
        t.append(dict(mes=m, cuota=amort + interes, interes=interes, amort=amort, saldo=saldo))
    return t


def tir(flujos, lo=0.0, hi=0.2):
    van = lambda r: sum(f / (1 + r) ** t for t, f in enumerate(flujos))
    for _ in range(300):
        mid = (lo + hi) / 2
        if van(lo) * van(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def meses_para_pagar(P, i, A):
    """n que resuelve P = A · (1 − (1+i)^−n) / i. Si A ≤ P·i, la deuda no baja nunca."""
    if A <= P * i:
        return float("inf")
    return -log(1 - P * i / A) / log(1 + i)


def mensual_de_efectiva(r):
    return (1 + r) ** (1 / 12) - 1


# ---------------------------------------------------------------- datos

# Ejemplo resuelto · crédito de consumo para un viaje
EJ = {"P": 3_800_000, "i": 0.0142, "n": 18, "gastos": 96_000, "seguro": 3_200}
# 4.1 · crédito automotriz
E1 = {"P": 9_500_000, "i": 0.011, "n": 36}
# 4.2 y 4.3 · compra en cuotas en una tienda (francés y alemán)
E2 = {"P": 1_750_000, "i": 0.021, "n": 10}
# 4.5 · tarjeta de crédito
E5 = {"deuda": 850_000, "i": 0.032, "pago": 60_000, "pago_bajo": 40_000, "meses_minimo": 12}
# 4.6 · hipotecario en pesos con prepago
E6 = {"P": 42_000_000, "i": 0.0042, "n": 180, "pagadas": 60, "prepago": 6_500_000, "comision_meses": 1}
# 4.7 · refinanciar un crédito de consumo
E7 = {"P": 4_200_000, "i": 0.019, "n": 36, "pagadas": 6, "i_nueva": 0.013, "gastos": 120_000}
# 4.8 · CAE de un crédito de consumo con gastos y seguro
E8 = {"P": 2_900_000, "i": 0.016, "n": 24, "gastos": 85_000, "seguro": 4_100}
# 4.9 · comente: menor tasa no es menor costo
E9 = {"P": 2_400_000, "n": 12, "A": {"i": 0.0155, "gastos": 0}, "B": {"i": 0.0145, "gastos": 165_000}}
# 4.10 · el departamento más caro que permite la renta (en UF; UF supuesta)
E10 = {"renta": 2_300_000, "tope": 0.25, "uf": 39_800, "tasa_anual": 0.043, "anios": 25, "anios_alt": 30, "pie": 0.20}


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    e = EJ
    c = cuota(e["P"], e["i"], e["n"])
    t = tabla_francesa(e["P"], e["i"], e["n"])
    al = tabla_alemana(e["P"], e["i"], e["n"])
    liquido = e["P"] - e["gastos"]
    m = tir([liquido] + [-(c + e["seguro"])] * e["n"])
    m_sin_seguro = tir([liquido] + [-c] * e["n"])
    R["ej"] = dict(factor=a_vp(e["i"], e["n"]), cuota=c, total=c * e["n"], interes=c * e["n"] - e["P"],
                   f1=t[0], f2=t[1], f3=t[2], f18=t[-1], saldo_6=t[5]["saldo"],
                   saldo_6_vp=c * a_vp(e["i"], e["n"] - 6),
                   al_c1=al[0]["cuota"], al_c18=al[-1]["cuota"], al_amort=al[0]["amort"],
                   al_interes=sum(f["interes"] for f in al), al_total=sum(f["cuota"] for f in al),
                   liquido=liquido, cuota_seguro=c + e["seguro"], tir_m=m, cae=12 * m, efectiva_cae=(1 + m) ** 12 - 1,
                   tasa_nominal=12 * e["i"], tasa_efectiva=(1 + e["i"]) ** 12 - 1,
                   tir_m_sin_seguro=m_sin_seguro, cae_sin_seguro=12 * m_sin_seguro,
                   amort_crece=t[1]["amort"] / t[0]["amort"])

    e = E1
    c = cuota(e["P"], e["i"], e["n"])
    R["e1"] = dict(cuota=c, total=c * e["n"], interes=c * e["n"] - e["P"], f1_interes=e["P"] * e["i"])

    e = E2
    t = tabla_francesa(e["P"], e["i"], e["n"])
    al = tabla_alemana(e["P"], e["i"], e["n"])
    c = t[0]["cuota"]
    R["e2"] = dict(cuota=c, f1=t[0], f2=t[1], saldo_2_vp=c * a_vp(e["i"], e["n"] - 2),
                   interes_total=c * e["n"] - e["P"], ultimo_interes=t[-1]["interes"])
    R["e3"] = dict(amort=al[0]["amort"], c1=al[0]["cuota"], c2=al[1]["cuota"], c10=al[-1]["cuota"],
                   interes_total=sum(f["interes"] for f in al), baja=al[0]["cuota"] - al[1]["cuota"],
                   formula=e["i"] * e["P"] * (e["n"] + 1) / 2)

    e = E5
    interes_mes = e["deuda"] * e["i"]
    n = meses_para_pagar(e["deuda"], e["i"], e["pago"])
    n_ent = ceil(n)
    # el último pago es parcial: saldo después de n_ent − 1 pagos, capitalizado un mes
    saldo = e["deuda"]
    for _ in range(n_ent - 1):
        saldo = saldo * (1 + e["i"]) - e["pago"]
    ultimo = saldo * (1 + e["i"])
    total = e["pago"] * (n_ent - 1) + ultimo
    n_bajo = meses_para_pagar(e["deuda"], e["i"], e["pago_bajo"])
    R["e5"] = dict(interes_mes=interes_mes, pagado_minimo=interes_mes * e["meses_minimo"], n=n, n_ent=n_ent,
                   ultimo=ultimo, total=total, interes_total=total - e["deuda"], n_bajo=n_bajo,
                   n_bajo_ent=ceil(n_bajo), efectiva=(1 + e["i"]) ** 12 - 1)

    e = E6
    c = cuota(e["P"], e["i"], e["n"])
    resto = e["n"] - e["pagadas"]
    saldo = c * a_vp(e["i"], resto)
    saldo_tabla = tabla_francesa(e["P"], e["i"], e["n"])[e["pagadas"] - 1]["saldo"]
    comision = e["prepago"] * e["i"] * e["comision_meses"]
    nuevo = saldo - e["prepago"]
    c_nueva = cuota(nuevo, e["i"], resto)
    n_nuevo = meses_para_pagar(nuevo, e["i"], c)
    pagar_sin = c * resto
    R["e6"] = dict(cuota=c, saldo=saldo, saldo_tabla=saldo_tabla, comision=comision, nuevo=nuevo,
                   c_nueva=c_nueva, baja=c - c_nueva, n_nuevo=n_nuevo, n_nuevo_ent=ceil(n_nuevo),
                   ahorro_a=pagar_sin - c_nueva * resto - e["prepago"] - comision,
                   meses_menos=resto - n_nuevo,
                   ahorro_b=pagar_sin - c * n_nuevo - e["prepago"] - comision)

    e = E7
    c = cuota(e["P"], e["i"], e["n"])
    resto = e["n"] - e["pagadas"]
    saldo = c * a_vp(e["i"], resto)
    nuevo = saldo + e["gastos"]
    c_nueva = cuota(nuevo, e["i_nueva"], resto)
    ahorro = c - c_nueva
    R["e7"] = dict(cuota=c, saldo=saldo, nuevo=nuevo, c_nueva=c_nueva, ahorro=ahorro, ahorro_total=ahorro * resto,
                   vp_ahorro=ahorro * a_vp(e["i_nueva"], resto),
                   tir_m=tir([saldo] + [-c_nueva] * resto),
                   c_sin_gastos=cuota(saldo, e["i_nueva"], resto))

    e = E8
    c = cuota(e["P"], e["i"], e["n"])
    liquido = e["P"] - e["gastos"]
    m = tir([liquido] + [-(c + e["seguro"])] * e["n"])
    R["e8"] = dict(cuota=c, liquido=liquido, pago=c + e["seguro"], tir_m=m, cae=12 * m, efectiva_cae=(1 + m) ** 12 - 1,
                   nominal=12 * e["i"], efectiva=(1 + e["i"]) ** 12 - 1)

    e = E9
    out = {}
    for k in ("A", "B"):
        d = e[k]
        c = cuota(e["P"], d["i"], e["n"])
        m = tir([e["P"] - d["gastos"]] + [-c] * e["n"])
        out[k] = dict(cuota=c, tir_m=m, cae=12 * m, total=c * e["n"] + d["gastos"])
    R["e9"] = out

    e = E10
    div_pesos = e["renta"] * e["tope"]
    div_uf = div_pesos / e["uf"]
    im = mensual_de_efectiva(e["tasa_anual"])
    cred = div_uf * a_vp(im, 12 * e["anios"])
    precio = cred / (1 - e["pie"])
    cred_alt = div_uf * a_vp(im, 12 * e["anios_alt"])
    precio_alt = cred_alt / (1 - e["pie"])
    R["e10"] = dict(div_pesos=div_pesos, div_uf=div_uf, im=im, im_mal=e["tasa_anual"] / 12, cred=cred, precio=precio,
                    pie_uf=precio * e["pie"], precio_pesos=precio * e["uf"], cred_alt=cred_alt, precio_alt=precio_alt,
                    gana=precio_alt - precio, interes_25=div_uf * 12 * e["anios"] - cred,
                    interes_30=div_uf * 12 * e["anios_alt"] - cred_alt)
    return R


def caso():
    spec = importlib.util.spec_from_file_location("caso", Path(__file__).with_name("caso_valentina.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    C = m.calcular()
    u4 = C["u4"]
    # recálculo propio
    P = m.U3["precio_depto"] * (1 - m.U3["pie"])
    im = mensual_de_efectiva(m.U4["tasa_anual_efectiva"])
    c20 = cuota(P, im, 240)
    c25 = cuota(P, im, 300)
    t = tabla_francesa(P, im, 240)
    gastos = m.U4["gastos_operacionales"]
    cae_m = tir([P - gastos] + [-c20] * 240, 0, 0.05)
    propio = dict(P=P, im=im, c20=c20, c25=c25, cae=12 * cae_m)
    extra = dict(cae_legal=12 * cae_m, cae_m=cae_m, renta_20=4 * c20, renta_25=4 * c25,
                 dif_interes=u4["interes_total_25"] - u4["interes_total_20"], baja_cuota=c20 - c25,
                 total_20=c20 * 240, total_25=c25 * 300, saldo_60=c20 * a_vp(im, 180),
                 im_mal=m.U4["tasa_anual_efectiva"] / 12, c20_mal=cuota(P, m.U4["tasa_anual_efectiva"] / 12, 240),
                 liquido=P - gastos, gastos=gastos, ultima=t[-1])
    return u4, propio, extra


def imprimir(R, u4, propio, extra):
    def show(v, ind="   "):
        if isinstance(v, dict):
            return "{" + ", ".join(f"{k}: {round(x, 6) if isinstance(x, float) else x}" for k, x in v.items()) + "}"
        return f"{v:,.6f}" if isinstance(v, float) else str(v)
    for k, d in R.items():
        print(f"== {k}")
        for kk, v in d.items():
            print(f"   {kk}: {show(v)}")
    print("== caso (script)")
    for k, v in u4.items():
        print(f"   {k}: {v}")
    print("== caso (propio)", {k: round(v, 8) for k, v in propio.items()})
    print("== caso (extra)", {k: (round(v, 6) if isinstance(v, float) else v) for k, v in extra.items()})


def esperados(R, u4, extra):
    p = lambda x: fmt(x)
    e = []
    j = R["ej"]
    e += [fmt(j["factor"], 4), p(j["cuota"]), p(j["total"]), p(j["interes"]), p(j["saldo_6"]),
          p(j["al_c1"]), p(j["al_c18"]), p(j["al_amort"]), p(j["al_interes"]), p(j["liquido"]), p(j["cuota_seguro"]),
          pct(j["tir_m"], 3), pct(j["cae"]), pct(j["efectiva_cae"]), pct(j["tasa_nominal"]), pct(j["tasa_efectiva"]),
          pct(j["cae_sin_seguro"]), fmt(j["amort_crece"], 4)]
    for f in ("f1", "f2", "f3", "f18"):
        e += [p(j[f]["interes"]), p(j[f]["amort"]), p(j[f]["saldo"] if abs(j[f]["saldo"]) > 1 else 0)]
    j = R["e1"]; e += [p(j["cuota"]), p(j["total"]), p(j["interes"]), p(j["f1_interes"])]
    j = R["e2"]; e += [p(j["cuota"]), p(j["saldo_2_vp"]), p(j["interes_total"])]
    for f in ("f1", "f2"):
        e += [p(j[f]["interes"]), p(j[f]["amort"]), p(j[f]["saldo"])]
    j = R["e3"]; e += [p(j["amort"]), p(j["c1"]), p(j["c2"]), p(j["c10"]), p(j["interes_total"]), p(j["baja"])]
    j = R["e5"]; e += [p(j["interes_mes"]), p(j["pagado_minimo"]), fmt(j["n"], 1), str(j["n_ent"]), p(j["ultimo"]),
                       p(j["total"]), p(j["interes_total"]), fmt(j["n_bajo"], 1), pct(j["efectiva"], 1)]
    j = R["e6"]; e += [p(j["cuota"]), p(j["saldo"]), p(j["comision"]), p(j["nuevo"]), p(j["c_nueva"]), p(j["baja"]),
                       fmt(j["n_nuevo"], 1), p(j["ahorro_a"]), p(j["ahorro_b"]), fmt(j["meses_menos"], 1)]
    j = R["e7"]; e += [p(j["cuota"]), p(j["saldo"]), p(j["nuevo"]), p(j["c_nueva"]), p(j["ahorro"]),
                       p(j["ahorro_total"]), p(j["vp_ahorro"]), pct(j["tir_m"], 3)]
    j = R["e8"]; e += [p(j["cuota"]), p(j["liquido"]), p(j["pago"]), pct(j["tir_m"], 3), pct(j["cae"]),
                       pct(j["efectiva_cae"]), pct(j["nominal"]), pct(j["efectiva"])]
    for k in ("A", "B"):
        j = R["e9"][k]; e += [p(j["cuota"]), pct(j["cae"]), p(j["total"])]
    j = R["e10"]; e += [p(j["div_pesos"]), fmt(j["div_uf"], 2), pct(j["im"], 4), fmt(j["cred"], 1), fmt(j["precio"], 1),
                        p(j["precio_pesos"]), fmt(j["cred_alt"], 1), fmt(j["precio_alt"], 1), fmt(j["gana"], 1),
                        fmt(j["interes_25"], 1), fmt(j["interes_30"], 1)]
    e += [p(u4["credito"]), pct(u4["tasa_mensual"], 4), p(u4["cuota_20"]), p(u4["cuota_25"]),
          p(u4["interes_total_20"]), p(u4["interes_total_25"]), pct(u4["cae"])]
    for f in u4["tabla"]:
        e += [p(f["interes"]), p(f["amortizacion"]), p(f["saldo"])]
    e += [pct(extra["cae_legal"]), p(extra["renta_20"]), p(extra["renta_25"]), p(extra["dif_interes"]),
          p(extra["baja_cuota"]), p(extra["total_20"]), p(extra["total_25"]), p(extra["saldo_60"]),
          p(extra["c20_mal"]), p(extra["liquido"]), pct(extra["cae_m"], 3), pct(extra["im_mal"], 4)]
    e += [fmt(R["e10"]["pie_uf"], 1), pct(R["e10"]["im_mal"], 4), p(R["e7"]["c_sin_gastos"])]
    return e


if __name__ == "__main__":
    R = resultados()
    u4, propio, extra = caso()
    imprimir(R, u4, propio, extra)
    j = R["ej"]
    chequeos = {
        "ejemplo: el saldo final es cero": abs(j["f18"]["saldo"]) < 1e-6,
        "ejemplo: saldo del mes 6 = VP de las 12 cuotas que faltan": abs(j["saldo_6"] - j["saldo_6_vp"]) < 1e-6,
        "4.2: saldo del mes 2 = VP de las 8 cuotas que faltan": abs(R["e2"]["f2"]["saldo"] - R["e2"]["saldo_2_vp"]) < 1e-6,
        "4.3: interés alemán = i·P·(n+1)/2": abs(R["e3"]["interes_total"] - R["e3"]["formula"]) < 1e-6,
        "4.6: saldo por fórmula = saldo de la tabla": abs(R["e6"]["saldo"] - R["e6"]["saldo_tabla"]) < 1e-6,
        "caso: recálculo propio = script": all(abs(propio[a] - u4[b]) < 1e-6 for a, b in
                                               [("P", "credito"), ("im", "tasa_mensual"), ("c20", "cuota_20"),
                                                ("c25", "cuota_25"), ("cae", "cae")]),
        "caso: la tabla del script calza con la propia": all(abs(f["saldo"] - g["saldo"]) < 1e-6 for f, g in
                                                             zip(u4["tabla"], tabla_francesa(propio["P"], propio["im"], 240, [1, 2, 3]))),
        "caso: el hipotecario termina en cero": abs(extra["ultima"]["saldo"]) < 1e-4,
    }
    print("\nCHEQUEOS:")
    for k, v in chequeos.items():
        print(f"   {'OK ' if v else 'MAL'} {k}")
    if not all(chequeos.values()):
        sys.exit(1)
    print("CADENA: OK, la pieza del caso calza con caso_valentina.py")
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "04-creditos-y-amortizacion.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".").replace("\\$", "$").replace("\\ \\%", " %")
        faltan = [x for x in esperados(R, u4, extra) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
