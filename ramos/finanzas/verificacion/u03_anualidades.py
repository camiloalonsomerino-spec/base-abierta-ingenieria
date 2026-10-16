"""Unidad 3 · Anualidades, perpetuidades y gradientes.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto queda sin respaldo.

    py -3 -P u03_anualidades.py            # imprime los resultados
    py -3 -P u03_anualidades.py --revisar  # además los busca en el .md

Todos los datos son originales de esta base. No vienen de ningún libro ni curso.
"""
from pathlib import Path
import importlib.util, sys

sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- herramientas

def fmt(x, dec=0):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=2):
    return fmt(100 * x, dec) + " %"


def a_vp(i, n):
    """Factor de valor presente de una anualidad vencida: (1 − (1+i)^−n) / i."""
    return (1 - (1 + i) ** -n) / i


def s_vf(i, n):
    """Factor de valor futuro de una anualidad vencida: ((1+i)^n − 1) / i. Ojo con el −1."""
    return ((1 + i) ** n - 1) / i


def s_vf_sin_menos_uno(i, n):
    """El error del Control 1: (1+i)^n / i."""
    return (1 + i) ** n / i


def vp_flujos(flujos, i):
    """flujos: {t: monto}."""
    return sum(f / (1 + i) ** t for t, f in flujos.items())


def tir(flujos_lista, lo=-0.5, hi=1.0):
    van = lambda r: sum(f / (1 + r) ** t for t, f in enumerate(flujos_lista))
    for _ in range(300):
        mid = (lo + hi) / 2
        if van(lo) * van(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def vp_geometrica(a1, g, i, n):
    """VP, un periodo antes del primer pago, de n pagos que parten en a1 y crecen a g."""
    if abs(i - g) < 1e-15:
        return n * a1 / (1 + i)
    return a1 / (i - g) * (1 - ((1 + g) / (1 + i)) ** n)


def vp_aritmetica(a1, G, i, n):
    """VP, un periodo antes del primer pago, de a1, a1+G, ..., a1+(n−1)G."""
    return a1 * a_vp(i, n) + G / i * (a_vp(i, n) - n / (1 + i) ** n)


# ---------------------------------------------------------------- datos

# Ejemplo resuelto · Ignacia ahorra para el pie de un auto: dos tramos de depósitos a fin de mes
EJ = {"tramo1": (150_000, 18), "tramo2": (230_000, 30), "i": 0.0065}
# 3.1 · notebook: contado o 12 cuotas vencidas; costo de oportunidad mensual
E1 = {"contado": 1_290_000, "cuota": 118_000, "n": 12, "i": 0.009}
# 3.2 · ahorro mensual parejo
E2 = {"A": 95_000, "n": 30, "i": 0.0045}
# 3.3 · jardín infantil: 11 mensualidades al inicio de cada mes, o un pago anual al contado
E3 = {"A": 210_000, "n": 11, "i": 0.006, "pago_anual": 2_240_000}
# 3.4 · comente del −1
E4 = {"A": 100_000, "n": 24, "i": 0.005}
# 3.5 · sillón: «compra hoy, primera cuota en el mes 4»
E5 = {"cuota": 45_900, "n": 10, "primera": 4, "i": 0.019, "contado": 380_000}
# 3.6 · beca a perpetuidad
E6 = {"beca": 3_600_000, "i": 0.052, "g": 0.02, "primera_diferida": 3}
# 3.7 · arriendo anual de un local que crece cada año
E7 = {"a1": 7_200_000, "g": 0.035, "i": 0.07, "n": 8, "primera_diferida": 3}
# 3.8 · ahorro para los estudios de un hijo, dos tramos con cambio de tasa
E8 = {"A1": 60_000, "n1": 48, "i1": 0.004, "A2": 90_000, "n2": 72, "i2": 0.005}
# 3.9 · comente: gradiente con g = i
E9 = {"a1": 1_000_000, "i": 0.06, "n": 10}
# 3.10 · depósitos que suben un monto fijo cada mes (gradiente aritmética)
E10 = {"a1": 42_000, "G": 3_500, "n": 24, "i": 0.0062}

# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # ejemplo resuelto
    (A1, n1), (A2, n2), i = EJ["tramo1"], EJ["tramo2"], EJ["i"]
    n = n1 + n2
    vf1_en_18 = A1 * s_vf(i, n1)
    vf1_en_48 = vf1_en_18 * (1 + i) ** n2
    vf2_en_48 = A2 * s_vf(i, n2)
    total = vf1_en_48 + vf2_en_48
    aportado = A1 * n1 + A2 * n2
    # comprobación por VP: VP del tramo 1 en 0, VP del tramo 2 en 0 (diferido 18), todo capitalizado a 48
    vp1 = A1 * a_vp(i, n1)
    vp2 = A2 * a_vp(i, n2) / (1 + i) ** n1
    comp = (vp1 + vp2) * (1 + i) ** n
    # comprobación flujo a flujo
    flujo = sum((A1 if t <= n1 else A2) * (1 + i) ** (n - t) for t in range(1, n + 1))
    # el error: sin −1
    mal1 = A1 * s_vf_sin_menos_uno(i, n1) * (1 + i) ** n2
    mal2 = A2 * s_vf_sin_menos_uno(i, n2)
    R["ej"] = dict(s1=s_vf(i, n1), s2=s_vf(i, n2), cap=(1 + i) ** n2, vf1_en_18=vf1_en_18, vf1_en_48=vf1_en_48,
                   vf2_en_48=vf2_en_48, total=total, aportado=aportado, interes=total - aportado,
                   vp1=vp1, vp2=vp2, vp_total=vp1 + vp2, cap48=(1 + i) ** n, comp=comp, flujo=flujo,
                   mal=mal1 + mal2, mal1=mal1, mal2=mal2, exceso=mal1 + mal2 - total)

    e = E1
    vp = e["cuota"] * a_vp(e["i"], e["n"])
    R["e1"] = dict(factor=a_vp(e["i"], e["n"]), vp=vp, dif=e["contado"] - vp, nominal=e["cuota"] * e["n"],
                   tir=tir([-e["contado"]] + [e["cuota"]] * e["n"]))

    e = E2
    vf = e["A"] * s_vf(e["i"], e["n"])
    R["e2"] = dict(factor=s_vf(e["i"], e["n"]), vf=vf, aportado=e["A"] * e["n"], interes=vf - e["A"] * e["n"],
                   vp=e["A"] * a_vp(e["i"], e["n"]), comp=e["A"] * a_vp(e["i"], e["n"]) * (1 + e["i"]) ** e["n"],
                   mal=e["A"] * s_vf_sin_menos_uno(e["i"], e["n"]))

    e = E3
    venc = e["A"] * a_vp(e["i"], e["n"])
    ant = venc * (1 + e["i"])
    R["e3"] = dict(vencida=venc, anticipada=ant, dif_pago=e["pago_anual"] - ant,
                   nominal=e["A"] * e["n"], ahorro_nominal=e["A"] * e["n"] - e["pago_anual"],
                   tir=tir([-(e["pago_anual"] - e["A"])] + [e["A"]] * (e["n"] - 1)))

    e = E4
    bien = e["A"] * s_vf(e["i"], e["n"])
    mal = e["A"] * s_vf_sin_menos_uno(e["i"], e["n"])
    R["e4"] = dict(bien=bien, mal=mal, dif=mal - bien, a_sobre_i=e["A"] / e["i"], veces=mal / bien,
                   aportado=e["A"] * e["n"])

    e = E5
    en_3 = e["cuota"] * a_vp(e["i"], e["n"])
    vp = en_3 / (1 + e["i"]) ** (e["primera"] - 1)
    vp_mal = en_3 / (1 + e["i"]) ** e["primera"]
    R["e5"] = dict(en_3=en_3, vp=vp, vp_mal=vp_mal, dif=e["contado"] - vp, nominal=e["cuota"] * e["n"],
                   vp_sin_diferir=en_3)

    e = E6
    plana = e["beca"] / e["i"]
    crec = e["beca"] / (e["i"] - e["g"])
    dif_en_2 = plana
    dif = plana / (1 + e["i"]) ** (e["primera_diferida"] - 1)
    R["e6"] = dict(plana=plana, crec=crec, dif=dif, extra_crec=crec - plana, ahorro_dif=plana - dif)

    e = E7
    vp = vp_geometrica(e["a1"], e["g"], e["i"], e["n"])
    vp_dif = vp / (1 + e["i"]) ** (e["primera_diferida"] - 1)
    flujo = sum(e["a1"] * (1 + e["g"]) ** (t - 1) / (1 + e["i"]) ** t for t in range(1, e["n"] + 1))
    ultimo = e["a1"] * (1 + e["g"]) ** (e["n"] - 1)
    sin_crec = e["a1"] * a_vp(e["i"], e["n"])
    R["e7"] = dict(vp=vp, flujo=flujo, vp_dif=vp_dif, ultimo=ultimo, sin_crec=sin_crec,
                   igual=vp_geometrica(e["a1"], e["i"], e["i"], e["n"]))

    e = E8
    t1_en_48 = e["A1"] * s_vf(e["i1"], e["n1"])
    t1_en_120 = t1_en_48 * (1 + e["i2"]) ** e["n2"]
    t2 = e["A2"] * s_vf(e["i2"], e["n2"])
    aport = e["A1"] * e["n1"] + e["A2"] * e["n2"]
    # error típico: una sola tasa (0,5 %) para los 120 meses
    una_tasa = e["A1"] * s_vf(e["i2"], e["n1"]) * (1 + e["i2"]) ** e["n2"] + t2
    R["e8"] = dict(t1_en_48=t1_en_48, cap=(1 + e["i2"]) ** e["n2"], t1_en_120=t1_en_120, t2=t2,
                   total=t1_en_120 + t2, aportado=aport, interes=t1_en_120 + t2 - aport, una_tasa=una_tasa)

    e = E9
    R["e9"] = dict(vp=vp_geometrica(e["a1"], e["i"], e["i"], e["n"]),
                   flujo=sum(e["a1"] * (1 + e["i"]) ** (t - 1) / (1 + e["i"]) ** t for t in range(1, e["n"] + 1)),
                   cada=e["a1"] / (1 + e["i"]))

    e = E10
    vp = vp_aritmetica(e["a1"], e["G"], e["i"], e["n"])
    vf = vp * (1 + e["i"]) ** e["n"]
    flujo = sum((e["a1"] + (t - 1) * e["G"]) * (1 + e["i"]) ** (e["n"] - t) for t in range(1, e["n"] + 1))
    aport = sum(e["a1"] + (t - 1) * e["G"] for t in range(1, e["n"] + 1))
    eq = vf / s_vf(e["i"], e["n"])
    R["e10"] = dict(vp=vp, vf=vf, flujo=flujo, aportado=aport, interes=vf - aport, equivalente=eq,
                    ultimo=e["a1"] + (e["n"] - 1) * e["G"], promedio=aport / e["n"],
                    a_n=a_vp(e["i"], e["n"]), parte_base=e["a1"] * a_vp(e["i"], e["n"]),
                    parte_g=e["G"] / e["i"] * (a_vp(e["i"], e["n"]) - e["n"] / (1 + e["i"]) ** e["n"]))
    return R


def caso():
    spec = importlib.util.spec_from_file_location("caso", Path(__file__).with_name("caso_valentina.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    C = m.calcular()
    i, n = m.U1["tasa_mensual"], m.U1["meses"]
    u3 = C["u3"]
    # recálculo propio, independiente del script
    meta = m.U3["precio_depto"] * m.U3["pie"]
    vf_hoy = m.U1["ahorro_hoy"] * (1 + i) ** n
    falta = meta - vf_hoy
    dep = falta / s_vf(i, n)
    propio = dict(meta=meta, vf_hoy=vf_hoy, falta=falta, dep=dep)
    # la pieza del error: el depósito si se olvida el −1, y cuánto junta con él
    dep_mal = falta / s_vf_sin_menos_uno(i, n)
    junta_mal = vf_hoy + dep_mal * s_vf(i, n)
    extra = dict(factor=s_vf(i, n), dep_mal=dep_mal, junta_mal=junta_mal, le_falta=meta - junta_mal,
                 interes=meta - u3["aportado"], vp_dep=dep * a_vp(i, n), n=n, i=i, a36=a_vp(i, n), cap36=(1 + i) ** n,
                 base=m.U1["ahorro_hoy"] + dep * a_vp(i, n),
                 ahorro_hoy=m.U1["ahorro_hoy"], precio=m.U3["precio_depto"])
    return u3, propio, extra


# ---------------------------------------------------------------- impresión

def imprimir(R, u3, propio, extra):
    for k, d in R.items():
        print(f"== {k}")
        for kk, v in d.items():
            print(f"   {kk}: {v:,.6f}" if isinstance(v, float) else f"   {kk}: {v}")
    print("== caso (script)")
    for k, v in u3.items():
        print(f"   {k}: {v:,.4f}")
    print("== caso (propio)", {k: round(v, 4) for k, v in propio.items()})
    print("== caso (extra)", {k: round(v, 6) for k, v in extra.items()})


def esperados(R, u3, extra):
    """Cadenas que el .md tiene que contener tal cual (después de normalizar {,} y {.})."""
    p = lambda x: fmt(x)            # pesos, sin decimales
    e = []
    j = R["ej"]
    e += [fmt(j["s1"], 4), fmt(j["s2"], 4), p(j["vf1_en_18"]), p(j["vf1_en_48"]), p(j["vf2_en_48"]),
          p(j["total"]), p(j["aportado"]), p(j["interes"]), p(j["vp1"]), p(j["vp2"]), p(j["vp_total"]),
          p(j["comp"]), p(j["mal"]), p(j["exceso"]), fmt(j["cap"], 4), fmt(j["cap48"], 4)]
    j = R["e1"]; e += [fmt(j["factor"], 4), p(j["vp"]), p(abs(j["dif"])), pct(j["tir"])]
    j = R["e2"]; e += [fmt(j["factor"], 4), p(j["vf"]), p(j["interes"]), p(j["vp"]), p(j["comp"]), p(j["mal"])]
    j = R["e3"]; e += [p(j["vencida"]), p(j["anticipada"]), p(abs(j["dif_pago"])), pct(j["tir"])]
    j = R["e4"]; e += [p(j["bien"]), p(j["mal"]), p(j["dif"]), p(j["a_sobre_i"]), fmt(j["veces"], 1)]
    j = R["e5"]; e += [p(j["en_3"]), p(j["vp"]), p(j["vp_mal"]), p(abs(j["dif"]))]
    j = R["e6"]; e += [p(j["plana"]), p(j["crec"]), p(j["dif"]), p(j["extra_crec"])]
    j = R["e7"]; e += [p(j["vp"]), p(j["vp_dif"]), p(j["ultimo"]), p(j["sin_crec"]), p(j["igual"])]
    j = R["e8"]; e += [p(j["t1_en_48"]), p(j["t1_en_120"]), p(j["t2"]), p(j["total"]), p(j["aportado"]),
                       p(j["interes"]), p(j["una_tasa"]), fmt(j["cap"], 4)]
    j = R["e9"]; e += [p(j["vp"]), p(j["cada"])]
    j = R["e10"]; e += [p(j["vp"]), p(j["vf"]), p(j["aportado"]), p(j["interes"]), p(j["equivalente"]),
                        p(j["parte_base"]), p(j["parte_g"]), fmt(j["a_n"], 4)]
    e += [p(u3["meta_pie"]), p(u3["vf_ahorro_hoy"]), p(u3["falta"]), p(u3["deposito_mensual"]),
          p(u3["aportado"]), p(extra["interes"]), p(extra["dep_mal"]), p(extra["junta_mal"]),
          fmt(extra["factor"], 4), fmt(extra["a36"], 4), fmt(extra["cap36"], 4), p(extra["vp_dep"]), p(extra["base"])]
    return e


if __name__ == "__main__":
    R = resultados()
    u3, propio, extra = caso()
    imprimir(R, u3, propio, extra)
    # comprobaciones internas: cada cifra por dos caminos
    chequeos = {
        "ejemplo: VP capitalizado = VF": abs(R["ej"]["comp"] - R["ej"]["total"]) < 1e-6,
        "ejemplo: flujo a flujo = VF": abs(R["ej"]["flujo"] - R["ej"]["total"]) < 1e-6,
        "3.2: VP capitalizado = VF": abs(R["e2"]["comp"] - R["e2"]["vf"]) < 1e-6,
        "3.4: el exceso es A/i": abs(R["e4"]["dif"] - R["e4"]["a_sobre_i"]) < 1e-6,
        "3.7: fórmula = flujo a flujo": abs(R["e7"]["vp"] - R["e7"]["flujo"]) < 1e-6,
        "3.9: fórmula = flujo a flujo": abs(R["e9"]["vp"] - R["e9"]["flujo"]) < 1e-6,
        "3.10: fórmula = flujo a flujo": abs(R["e10"]["vf"] - R["e10"]["flujo"]) < 1e-6,
        "caso: recálculo propio = script": all(abs(propio[a] - u3[b]) < 1e-6 for a, b in
                                               [("meta", "meta_pie"), ("vf_hoy", "vf_ahorro_hoy"),
                                                ("falta", "falta"), ("dep", "deposito_mensual")]),
        "caso: comprobación por VP = meta": abs(u3["comprobacion_vp"] - u3["meta_pie"]) < 1e-4,
    }
    print("\nCHEQUEOS:")
    for k, v in chequeos.items():
        print(f"   {'OK ' if v else 'MAL'} {k}")
    if not all(chequeos.values()):
        sys.exit(1)
    print("CADENA: OK, la pieza del caso calza con caso_valentina.py")
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "03-anualidades.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".").replace("\\$", "$").replace("\\ \\%", " %")
        faltan = [x for x in esperados(R, u3, extra) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
