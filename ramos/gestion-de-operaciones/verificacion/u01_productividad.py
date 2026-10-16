"""Unidad 1 · Introducción y productividad.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba
que cada resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto
queda sin respaldo.

    python u01_productividad.py            # imprime los resultados
    python u01_productividad.py --revisar  # además los busca en el .md
"""
from math import ceil
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))           # con -P el directorio del script no entra solo
import caso_estampa_sur as caso          # noqa: E402  (fuente única del caso integrador)

# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".").replace("-", "−")


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def var(p1, p0):
    """Variación porcentual (valor final − valor inicial) / valor inicial."""
    return (p1 - p0) / p0


def empresa(d):
    """Indicadores de productividad de una empresa en un período (pesos y horas del mes)."""
    hh = d["personas"] * d["horas"]
    ventas = d["unidades"] * d["precio"]
    rem = d["personas"] * d["sueldo"] if "sueldo" in d else d["remuneraciones"]
    insumos = d["insumos"]
    va = ventas - insumos
    utilidad = ventas - rem - insumos
    r = {"hh": hh, "ventas": ventas, "rem": rem, "insumos": insumos, "va": va, "utilidad": utilidad,
         "va_adicion": utilidad + rem,
         "fisica": d["unidades"] / hh, "economica": va / hh,
         "parcial_trabajo": va / d["personas"],
         "multifactorial": ventas / (rem + insumos)}
    if "activo" in d:
        r["parcial_capital"] = va / d["activo"]
    return r


def curvas(prod, costo_fijo, costo_trabajador):
    """prod: producción total con 0, 1, 2… trabajadores → filas de producto y costos."""
    filas = []
    for n, q in enumerate(prod):
        if n == 0:
            filas.append({"n": 0, "q": q, "pmg": None, "pme": None, "cf": costo_fijo, "cv": 0, "ct": costo_fijo,
                          "cmg": None, "cfme": None, "cvme": None, "ctme": None})
            continue
        cv = n * costo_trabajador
        ct = costo_fijo + cv
        filas.append({"n": n, "q": q, "pmg": q - prod[n - 1], "pme": q / n, "cf": costo_fijo, "cv": cv, "ct": ct,
                      "cmg": costo_trabajador / (q - prod[n - 1]), "cfme": costo_fijo / q, "cvme": cv / q,
                      "ctme": ct / q})
    return filas


def multifactorial(unidades, costos):
    return unidades / sum(costos.values())


def localizacion(sitios, q):
    """sitios: {nombre: (costo fijo, costo variable unitario)} → costo total con volumen q."""
    return {s: cf + cv * q for s, (cf, cv) in sitios.items()}


def indiferencia(a, b):
    """Volumen en que dos sitios cuestan lo mismo: (CF_b − CF_a) / (cv_a − cv_b)."""
    (cfa, cva), (cfb, cvb) = a, b
    return (cfb - cfa) / (cva - cvb)


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Ejemplo resuelto · Frutos del Itata, planta de mermeladas en Coelemu (un mes)
EJ_2025 = {"personas": 14, "horas": 176, "unidades": 36_960, "precio": 2_900, "sueldo": 690_000,
           "insumos": 71_500_000, "activo": 150_000_000}
EJ_2026 = {"personas": 13, "horas": 176, "unidades": 41_184, "precio": 2_900, "sueldo": 720_000,
           "insumos": 80_900_000, "activo": 185_000_000}

# Sección 4 · cocina de empanadas congeladas: un horno arrendado y cocineros por día
EMP_PROD = [0, 120, 300, 420, 480]
EMP_CF, EMP_CV = 30_000, 28_000            # CLP por día: arriendo del horno, costo de un cocinero

# Sección 5 · costo de mano de obra por unidad en dos talleres
MO_TALLER = {"Temuco": (52_000, 130), "Tacna": (21_000, 42)}   # (CLP por persona y día, unidades por persona y día)
# Sección 5 · dos sitios para una bodega de despacho
LOC_EJ = {"Penco": (30_000_000, 2_500), "Lota": (22_000_000, 3_300)}

# Ejercicio 1.1 · lavandería industrial (kg lavados, personas, horas por persona en la semana)
E1 = {"s1": (3_150, 5, 45), "s2": (3_360, 6, 42)}
# Ejercicio 1.2 · fábrica de cajas de cartón, un mes (CLP)
E2_CAJAS = 12_600
E2_COSTOS = {"mano de obra": 1_890_000, "materiales": 4_410_000, "energía": 630_000, "arriendo de máquinas": 1_050_000}
E2_ALZA_MAT = 0.10
# Ejercicio 1.4 · taller de costura: prendas por día con 0 a 5 costureras
E4_PROD = [0, 35, 80, 110, 128, 136]
# Ejercicio 1.5 · taller de bolsas reutilizables: dos configuraciones (CLP por día)
E5_MAQ, E5_TRAB = 18_000, 32_000
E5_CONF = {"una máquina": (1, [0, 50, 120, 160, 180]), "dos máquinas": (2, [0, 60, 150, 220, 260])}
E5_META = 150
# Ejercicio 1.6 · dos fábricas de muebles de Ñuble, un mes
E6 = {
    "A": {"personas": 18, "horas": 176, "unidades": 1_320, "precio": 64_000, "sueldo": 720_000,
          "insumos": 41_500_000, "activo": 240_000_000},
    "B": {"personas": 11, "horas": 168, "unidades": 1_050, "precio": 61_000, "sueldo": 850_000,
          "insumos": 33_800_000, "activo": 410_000_000},
}
# Ejercicio 1.7 · conservera: 38 personas, 42 h semanales, 48 semanas; productividad 12,5 u/HH
E7 = {"personas": 38, "h_sem": 42, "semanas": 48, "prod": 12.5, "h_sem_nueva": 40, "alza": 0.05}
# Ejercicio 1.8 · envasado de miel: un turno de 8 h con 5 personas
E8 = {"frascos": 1_800, "personas": 5, "horas": 8, "defectos": 0.06, "precio": 3_500, "precio_seg": 0.60,
      "defectos_mejora": 0.02}
# Ejercicio 1.9 · tres comunas para una planta (CF anual CLP, costo variable CLP por unidad)
E9 = {"Chillán": (42_000_000, 6_800), "Los Ángeles": (58_000_000, 5_600), "Coronel": (85_000_000, 4_300)}
E9_Q, E9_ALZA = 18_000, 0.20
# Ejercicio 1.10 · envasado de vino: situación actual (A) y llenadora automática (B), un mes
E10_PRECIO, E10_MAT = 1_300, 620     # CLP por botella: tarifa de envasado, materiales por botella
E10 = {
    "A": {"personas": 12, "horas": 180, "botellas": 54_000, "sueldo": 780_000, "energia": 1_900_000, "capital": 2_400_000},
    "B": {"personas": 8, "horas": 180, "botellas": 60_000, "sueldo": 780_000, "energia": 3_100_000, "capital": 9_800_000},
}

# Caso integrador · Estampa Sur, marzo (21 días hábiles). Lo que no viene del script del caso es propio de esta unidad.
CASO = {"dias": 21, "horas_dia": 8, "unidades": 5_600, "unidades_anio_anterior": 4_872,
        "precio": 4_900, "tinta_kg": 16_500, "energia_arriendo": 1_250_000}


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    R["ej"] = {"2025": empresa(EJ_2025), "2026": empresa(EJ_2026)}
    a, b = R["ej"]["2025"], R["ej"]["2026"]
    R["ej_var"] = {k: var(b[k], a[k]) for k in ("fisica", "economica", "parcial_trabajo", "parcial_capital", "multifactorial")}
    R["ej_insumo_u"] = (EJ_2025["insumos"] / EJ_2025["unidades"], EJ_2026["insumos"] / EJ_2026["unidades"])

    R["emp"] = curvas(EMP_PROD, EMP_CF, EMP_CV)
    R["mo_taller"] = {t: s / u for t, (s, u) in MO_TALLER.items()}
    R["loc_ej"] = indiferencia(LOC_EJ["Lota"], LOC_EJ["Penco"])

    p = {k: q / (n * h) for k, (q, n, h) in E1.items()}
    R["e1"] = (p, var(p["s2"], p["s1"]))

    mf0 = multifactorial(E2_CAJAS, E2_COSTOS)
    c1 = dict(E2_COSTOS); c1["materiales"] *= 1 + E2_ALZA_MAT
    mf1 = multifactorial(E2_CAJAS, c1)
    R["e2"] = (mf0 * 1000, mf1 * 1000, var(mf1, mf0), sum(E2_COSTOS.values()), sum(c1.values()))

    R["e4"] = curvas(E4_PROD, 0, 0)

    R["e5"] = {}
    for nombre, (maq, prod) in E5_CONF.items():
        filas = curvas(prod, maq * E5_MAQ, E5_TRAB)
        meta = next(f for f in filas if f["n"] > 0 and f["q"] >= E5_META)
        minimo = min((f for f in filas if f["n"] > 0), key=lambda f: f["ctme"])
        R["e5"][nombre] = (filas, meta, minimo)

    R["e6"] = {k: empresa(v) for k, v in E6.items()}

    hh0 = E7["personas"] * E7["h_sem"] * E7["semanas"]
    q0 = E7["prod"] * hh0
    q1 = q0 * (1 + E7["alza"])
    n_exacto = q1 / (E7["prod"] * E7["h_sem_nueva"] * E7["semanas"])
    p_necesaria = q1 / (E7["personas"] * E7["h_sem_nueva"] * E7["semanas"])
    n_solo_jornada = E7["personas"] * E7["h_sem"] / E7["h_sem_nueva"]
    R["e7"] = {"hh0": hh0, "q0": q0, "q1": q1, "n_exacto": n_exacto, "n": ceil(n_exacto),
               "p_necesaria": p_necesaria, "var_p": var(p_necesaria, E7["prod"]),
               "n_solo_jornada": n_solo_jornada}

    hh8 = E8["personas"] * E8["horas"]
    def ventas8(tasa):
        malos = E8["frascos"] * tasa
        return (E8["frascos"] - malos) * E8["precio"] + malos * E8["precio"] * E8["precio_seg"], malos
    v_sin = E8["frascos"] * E8["precio"]
    v_con, malos = ventas8(E8["defectos"])
    v_mej, malos_mej = ventas8(E8["defectos_mejora"])
    R["e8"] = {"hh": hh8, "malos": malos, "sin": v_sin / hh8, "con": v_con / hh8, "perdida": var(v_con, v_sin),
               "mejora": v_mej / hh8, "var_mejora": var(v_mej, v_con), "malos_mej": malos_mej,
               "v_sin": v_sin, "v_con": v_con, "v_mej": v_mej}

    R["e9"] = {"ct": localizacion(E9, E9_Q), "ct_alza": localizacion(E9, E9_Q * (1 + E9_ALZA)),
               "q_alza": E9_Q * (1 + E9_ALZA),
               "ind": {("Chillán", "Los Ángeles"): indiferencia(E9["Chillán"], E9["Los Ángeles"]),
                       ("Los Ángeles", "Coronel"): indiferencia(E9["Los Ángeles"], E9["Coronel"]),
                       ("Chillán", "Coronel"): indiferencia(E9["Chillán"], E9["Coronel"])}}

    R["e10"] = {}
    for k, d in E10.items():
        hh = d["personas"] * d["horas"]
        mo = d["personas"] * d["sueldo"]
        mat = d["botellas"] * E10_MAT
        costos = mo + mat + d["energia"] + d["capital"]
        ventas = d["botellas"] * E10_PRECIO
        R["e10"][k] = {"hh": hh, "pmo": d["botellas"] / hh, "mo": mo, "mat": mat, "costos": costos,
                       "ventas": ventas, "mf": ventas / costos, "utilidad": ventas - costos,
                       "fijos": mo + d["energia"] + d["capital"]}
    A, B = R["e10"]["A"], R["e10"]["B"]
    margen = E10_PRECIO - E10_MAT
    R["e10_var"] = {"pmo": var(B["pmo"], A["pmo"]), "mf": var(B["mf"], A["mf"]),
                    "q_equilibrio": (A["utilidad"] + B["fijos"]) / margen}

    # Caso integrador
    C = caso.calcular()
    u6 = caso.U6
    personas = u6["trabajadores_iniciales"]
    hh = personas * CASO["horas_dia"] * CASO["dias"]
    hh_u = hh / CASO["unidades"]
    prenda = caso.U5["precio"]
    tinta_u = caso.LDM["tinta (kg)"]["por_unidad"]
    mo = hh * u6["salario_hora"]
    prendas = CASO["unidades"] * prenda
    tinta_kg = CASO["unidades"] * tinta_u
    tinta = tinta_kg * CASO["tinta_kg"]
    insumos = prendas + tinta + CASO["energia_arriendo"]
    ventas = CASO["unidades"] * CASO["precio"]
    va = ventas - insumos
    fisica = CASO["unidades"] / hh
    fisica0 = CASO["unidades_anio_anterior"] / hh
    pron = C["u4"]["pronostico_redondeado"][0]
    dias_m1 = u6["dias"][0]
    hh_nec = pron * hh_u
    hh_disp = personas * u6["horas_dia"] * dias_m1
    R["caso"] = {"personas": personas, "hh": hh, "hh_u": hh_u, "fisica": fisica, "fisica0": fisica0,
                 "var": var(fisica, fisica0), "mo": mo, "prendas": prendas, "tinta_kg": tinta_kg, "tinta": tinta,
                 "insumos": insumos, "ventas": ventas, "va": va, "utilidad": ventas - mo - insumos,
                 "economica": va / hh, "mf": ventas / (mo + insumos), "pron": pron, "dias_m1": dias_m1,
                 "hh_nec": hh_nec, "hh_disp": hh_disp, "falta": hh_nec - hh_disp,
                 "falta_pct": (hh_nec - hh_disp) / hh_disp,
                 "coincide_u6": abs(hh_u - u6["hh_por_unidad"]) < 1e-12}
    return R


def imprimir(R):
    print("== Ejemplo resuelto · Frutos del Itata")
    for k, v in R["ej"].items():
        print("  ", k, {x: round(y, 4) for x, y in v.items()})
    print("   variaciones", {k: pct(v) for k, v in R["ej_var"].items()}, "insumo por frasco", R["ej_insumo_u"])
    print("== Sección 4 · empanadas")
    for f in R["emp"]:
        print("    ", f)
    print("== Sección 5 · MO por unidad", R["mo_taller"], "| indiferencia Penco-Lota", R["loc_ej"])
    print("== 1.1", R["e1"])
    print("== 1.2", R["e2"])
    print("== 1.4"); [print("    ", f["n"], f["q"], f["pmg"], f["pme"]) for f in R["e4"]]
    print("== 1.5")
    for k, (filas, meta, minimo) in R["e5"].items():
        print("  ", k)
        for f in filas:
            print("      ", f)
        print("     meta:", meta["n"], meta["q"], meta["ct"], meta["ctme"], "| mínimo CTMe:", minimo["n"], minimo["ctme"])
    print("== 1.6")
    for k, v in R["e6"].items():
        print("  ", k, {x: round(y, 4) for x, y in v.items()})
    print("== 1.7", R["e7"])
    print("== 1.8", R["e8"])
    print("== 1.9", R["e9"])
    print("== 1.10", R["e10"], R["e10_var"])
    print("== Caso", R["caso"])


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    """Cadenas que el .md tiene que contener tal cual."""
    e = []
    for v in R["ej"].values():
        e += [fmt(v["hh"], 0), fmt(v["ventas"], 0), fmt(v["va"], 0), fmt(v["utilidad"], 0), fmt(v["fisica"], 1),
              fmt(v["economica"], 0), fmt(v["parcial_trabajo"], 0), fmt(v["parcial_capital"], 3), fmt(v["multifactorial"], 3)]
    e += [pct(R["ej_var"]["fisica"]), pct(R["ej_var"]["economica"]), pct(R["ej_var"]["parcial_capital"]), pct(R["ej_var"]["multifactorial"])]
    e += [fmt(x, 0) for x in R["ej_insumo_u"]]
    for f in R["emp"][1:]:
        e += [fmt(f["pme"], 0), fmt(f["ctme"], 1), fmt(f["cmg"], 1)]
    e += [fmt(x, 0) for x in R["mo_taller"].values()]
    e += [fmt(R["loc_ej"], 0)]
    p, v = R["e1"]
    e += [fmt(p["s1"], 2), fmt(p["s2"], 2), pct(v)]
    e += [fmt(R["e2"][0], 3), fmt(R["e2"][1], 3), pct(R["e2"][2]), fmt(R["e2"][4], 0)]
    for f in R["e4"][1:]:
        e += [fmt(f["pme"], 1)]
    for filas, meta, minimo in R["e5"].values():
        e += [fmt(meta["ct"], 0), fmt(meta["ctme"], 1), fmt(minimo["ctme"], 1)]
    for v in R["e6"].values():
        e += [fmt(v["va"], 0), fmt(v["fisica"], 2), fmt(v["economica"], 0), fmt(v["parcial_trabajo"], 0), fmt(v["parcial_capital"], 3)]
    e7 = R["e7"]
    e += [fmt(e7["q0"], 0), fmt(e7["q1"], 0), fmt(e7["n_exacto"], 2), f"{e7['n']} personas", fmt(e7["p_necesaria"], 2), pct(e7["var_p"])]
    e8 = R["e8"]
    e += [fmt(e8["sin"], 0), fmt(e8["con"], 0), pct(e8["perdida"]), fmt(e8["mejora"], 0), pct(e8["var_mejora"])]
    e += [fmt(x, 0) for x in R["e9"]["ct"].values()] + [fmt(x, 0) for x in R["e9"]["ct_alza"].values()]
    e += [fmt(x, 0) for x in R["e9"]["ind"].values()]
    for v in R["e10"].values():
        e += [fmt(v["pmo"], 2), fmt(v["mf"], 3), fmt(v["utilidad"], 0), fmt(v["costos"], 0)]
    e += [pct(R["e10_var"]["pmo"]), pct(R["e10_var"]["mf"]), fmt(ceil(R["e10_var"]["q_equilibrio"]), 0)]
    c = R["caso"]
    e += [fmt(c["hh"], 0), fmt(c["fisica"], 2), fmt(c["fisica0"], 2), pct(c["var"]), fmt(c["hh_u"], 2), fmt(c["mo"], 0),
          fmt(c["insumos"], 0), fmt(c["ventas"], 0), fmt(c["va"], 0), fmt(c["utilidad"], 0), fmt(c["economica"], 0),
          fmt(c["mf"], 3), fmt(c["hh_nec"], 0), fmt(c["hh_disp"], 0), fmt(c["falta"], 0), pct(c["falta_pct"])]
    return e


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    print("\nEl estándar de HH por unidad del caso calza con la unidad 6:", "SÍ" if R["caso"]["coincide_u6"] else "NO")
    if "--revisar" in sys.argv:
        md = (AQUI.parent / "unidades" / "01-introduccion-y-productividad.md").read_text(encoding="utf-8")
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
