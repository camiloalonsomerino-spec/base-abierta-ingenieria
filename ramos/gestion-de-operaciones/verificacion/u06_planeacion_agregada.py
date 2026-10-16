"""Unidad 6 · Planeación agregada.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba
que cada resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto
queda sin respaldo.

    python u06_planeacion_agregada.py            # imprime los resultados
    python u06_planeacion_agregada.py --revisar  # además los busca en el .md

El ejercicio 6.10 se comprueba con scipy (programación lineal) si está instalado; si no,
se usa solo el método de transporte paso a paso.
"""
from math import ceil
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
import caso_estampa_sur as caso  # noqa: E402

# ---------------------------------------------------------------- herramientas

def fmt(x, dec=0):
    """Número a la chilena: coma decimal, punto de miles y signo menos tipográfico (−)."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".").replace("-", "−")


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def clp(x):
    """Monto en pesos como va en el .md: $36.000; bajo mil, con barra ($600 escrito \\$600)
    para que md_a_pdf no lo tome por fórmula."""
    x = round(x)
    return ("$" if abs(x) >= 1000 else "\\$") + fmt(x)


def techo(x):
    """Redondeo hacia arriba que no se tropieza con 17,000000001."""
    return ceil(x - 1e-9)


def costo_cambio(w_nuevo, w_viejo, c):
    if w_nuevo > w_viejo:
        return (w_nuevo - w_viejo) * c["contratar"]
    return (w_viejo - w_nuevo) * c.get("despedir", 0)


def persecucion(D, dias, r, w0, i0, c):
    """Contrata y despide cada mes. Trabajadores = techo(demanda neta / (r · días)).
    La demanda neta descuenta el inventario que dejó el redondeo del mes anterior."""
    filas, w_prev, inv, total = [], w0, i0, 0
    for d, n in zip(D, dias):
        neto = max(0, d - inv)
        teo = neto / (r * n)
        w = techo(teo)
        prod = w * r * n
        inv = inv + prod - d
        f = {"D": d, "n": n, "neto": neto, "teo": teo, "W": w,
             "contrata": max(0, w - w_prev), "despide": max(0, w_prev - w),
             "c_cambio": costo_cambio(w, w_prev, c), "P": prod, "I": inv,
             "sueldos": w * n * c["dia"], "mantener": max(inv, 0) * c.get("mantener", 0)}
        f["total"] = f["c_cambio"] + f["sueldos"] + f["mantener"]
        total += f["total"]
        filas.append(f)
        w_prev = w
    return filas, total


def w_nivelada_sin_faltantes(D, dias, r, i0):
    """Máximo de los trabajadores acumulados: techo(max_t (ΣD − I0) / (r · Σdías))."""
    acum_d = acum_n = 0
    ratios = []
    for d, n in zip(D, dias):
        acum_d += d
        acum_n += n
        ratios.append((acum_d - i0) / (r * acum_n))
    return techo(max(ratios)), ratios


def w_nivelada_con_faltantes(D, dias, r, i0):
    """Promedio del horizonte, hacia arriba: techo((ΣD − I0) / (r · Σdías))."""
    prom = (sum(D) - i0) / (r * sum(dias))
    return techo(prom), prom


def dotacion_fija(D, dias, r, w, w0, i0, c, k=None, tope_he=0.0, subcontrata=False):
    """Dotación fija w todo el horizonte. Lo que falta cada mes se cubre con horas extra
    (hasta tope_he de la producción regular) y luego con subcontratación si se permite.
    Lo que no se cubre queda como faltante (pedido atrasado) y se arrastra."""
    filas, inv = [], i0
    total = cambio = costo_cambio(w, w0, c)
    for d, n in zip(D, dias):
        reg = w * r * n
        falta = max(0, d - inv - reg)
        he = min(falta, tope_he * reg)
        sub = (falta - he) if subcontrata else 0
        inv = inv + reg + he + sub - d
        f = {"D": d, "n": n, "reg": reg, "he": he, "sub": sub, "P": reg + he + sub, "I": inv,
             "sueldos": w * n * c["dia"],
             "c_he": he * k * c["hora_extra"] if he else 0,
             "c_sub": sub * c.get("sub", 0),
             "mantener": max(inv, 0) * c.get("mantener", 0),
             "faltante": max(-inv, 0) * c.get("faltante", 0),
             "dias_amort": inv / (w * r) if w else 0}
        f["total"] = f["sueldos"] + f["c_he"] + f["c_sub"] + f["mantener"] + f["faltante"]
        total += f["total"]
        filas.append(f)
    return filas, cambio, total


def suma(filas, clave):
    return sum(f[clave] for f in filas)


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Ejemplo resuelto · fábrica de mermeladas de Ñuble (cajas de 12 frascos)
EJ = {
    "meses": ["Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
    "D": [5340, 5870, 7690, 8120, 5960, 4870],
    "dias": [21, 22, 18, 21, 20, 21],
    "hh": 0.4, "horas_dia": 8, "w0": 15, "i0": 300,
    "c": {"contratar": 420_000, "despedir": 680_000, "dia": 29_200, "mantener": 180,
          "faltante": 1_120, "hora_extra": 5_400, "sub": 2_380},
    "tope_he": 0.15, "rango_w": range(12, 21),
}
EJ["r"] = EJ["horas_dia"] / EJ["hh"]          # 20 cajas por trabajador y día

# 6.1 y 6.2 · ensamble de bicicletas eléctricas (8 por trabajador y día)
E1 = {"D": [2310, 2640, 3170, 2230], "dias": [21, 20, 22, 19], "r": 8, "w0": 15, "i0": 0,
      "c": {"contratar": 380_000, "despedir": 540_000, "dia": 31_000, "mantener": 950}}

# 6.3 · planta de hielo en bolsas, producción constante
E3 = {"D": [7750, 9150, 11600, 12900, 11300, 8700], "P": 10_200, "i0": 500,
      "mantener": 60, "faltante": 210, "meses": ["Oct", "Nov", "Dic", "Ene", "Feb", "Mar"]}

# 6.5, 6.6 y 6.8 · fábrica de ventanas de PVC (jornada de 9 h, 1,5 HH por ventana → 6 por día)
E5 = {"D": [1620, 1930, 2170, 1720, 1240, 1390], "dias": [22, 20, 21, 22, 21, 19],
      "r": 6, "w0": 14, "i0": 0,
      "c": {"contratar": 510_000, "despedir": 760_000, "dia": 34_000, "mantener": 2_600,
            "faltante": 7_900}}

# 6.7 · imprenta de cuadernos (9 h por día, 0,05 HH por cuaderno → 180 por día)
E7 = {"D": [28_400, 41_900, 46_300, 23_700], "dias": [21, 22, 20, 22], "r": 180, "hh": 0.05,
      "w": 9, "i0": 1_200, "tope_he": 0.25,
      "c": {"contratar": 0, "dia": 30_600, "hora_extra": 6_300, "sub": 260, "mantener": 35}}

# 6.9 · planta de agua purificada en bidones (8 h por día, 0,02 HH por bidón → 400 por día)
E9 = {"D": [118_000, 126_500, 141_200, 152_800, 137_400, 129_900],
      "dias": [22, 21, 21, 22, 20, 22], "r": 400, "hh": 0.02, "w0": 15, "i0": 2_000,
      "tope_he": 0.25, "w0_b": 17, "rango_w": range(12, 20),
      "c": {"contratar": 465_000, "despedir": 655_000, "dia": 27_500, "hora_extra": 5_180,
            "mantener": 12, "faltante": 40}}

# 6.10 · planta de detergente, método de transporte (costos por caja)
E10 = {"D": [3750, 4900, 5600], "i0": 200,
       "cap": {"R": 4150, "H": 600, "S": 1000},
       "costo": {"R": 2000, "H": 3000, "S": 3400}, "mantener": 250}


# ---------------------------------------------------------------- 6.10 · transporte

def transporte_voraz(p):
    """Mes a mes, llena la demanda con la celda disponible más barata (sin pedidos atrasados).
    La celda (fuente del mes t, demanda del mes s) cuesta costo de la fuente + (s − t) · mantener."""
    T = len(p["D"])
    restante = {("I0", 0): p["i0"]}
    for t in range(T):
        for f in "RHS":
            restante[(f, t)] = p["cap"][f]
    asign = []
    for s in range(T):
        falta = p["D"][s]
        while falta > 0:
            opciones = [(0 + s * p["mantener"], key) if key[0] == "I0" else
                        (p["costo"][key[0]] + (s - key[1]) * p["mantener"], key)
                        for key, q in restante.items() if q > 0 and key[1] <= s]
            costo, key = min(opciones, key=lambda o: (o[0], o[1][1], "RHSI".index(o[1][0][0])))
            q = min(falta, restante[key])
            restante[key] -= q
            falta -= q
            asign.append((key, s, q, costo))
    total = sum(q * c for _, _, q, c in asign)
    return asign, total


def transporte_lp(p):
    try:
        from scipy.optimize import linprog
    except ImportError:
        return None
    T = len(p["D"])
    fuentes = [("I0", 0, p["i0"], 0)] + [(f, t, p["cap"][f], p["costo"][f]) for t in range(T) for f in "RHS"]
    var, cost = [], []
    for i, (f, t, cap, c) in enumerate(fuentes):
        for s in range(T):
            if s >= t:
                var.append((i, s))
                cost.append(c + (s - t) * p["mantener"] if f != "I0" else s * p["mantener"])
    A_eq = [[1 if v[1] == s else 0 for v in var] for s in range(T)]
    A_ub = [[1 if v[0] == i else 0 for v in var] for i in range(len(fuentes))]
    res = linprog(cost, A_ub=A_ub, b_ub=[f[2] for f in fuentes], A_eq=A_eq, b_eq=p["D"],
                  bounds=(0, None), method="highs")
    return res.fun


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    e = EJ
    R["ej_pers"] = persecucion(e["D"], e["dias"], e["r"], e["w0"], e["i0"], e["c"])
    ws, ratios = w_nivelada_sin_faltantes(e["D"], e["dias"], e["r"], e["i0"])
    R["ej_sin"] = (ws, ratios, dotacion_fija(e["D"], e["dias"], e["r"], ws, e["w0"], e["i0"], e["c"], e["hh"]))
    wc, prom = w_nivelada_con_faltantes(e["D"], e["dias"], e["r"], e["i0"])
    R["ej_con"] = (wc, prom, dotacion_fija(e["D"], e["dias"], e["r"], wc, e["w0"], e["i0"], e["c"], e["hh"]))
    mix = {w: dotacion_fija(e["D"], e["dias"], e["r"], w, e["w0"], e["i0"], e["c"], e["hh"],
                            e["tope_he"], True) for w in e["rango_w"]}
    wm = min(mix, key=lambda w: mix[w][2])
    R["ej_mix"] = (wm, mix)

    # 6.1 y 6.2
    p = E1
    R["e1"] = persecucion(p["D"], p["dias"], p["r"], p["w0"], p["i0"], p["c"])
    w2, rat2 = w_nivelada_sin_faltantes(p["D"], p["dias"], p["r"], p["i0"])
    R["e2"] = (w2, rat2, dotacion_fija(p["D"], p["dias"], p["r"], w2, p["w0"], p["i0"], p["c"], 1))

    # 6.3
    inv, filas = E3["i0"], []
    for d in E3["D"]:
        inv = inv + E3["P"] - d
        filas.append((d, inv, max(inv, 0) * E3["mantener"], max(-inv, 0) * E3["faltante"]))
    R["e3"] = filas

    # 6.5, 6.6 y 6.8
    p = E5
    R["e5_pers"] = persecucion(p["D"], p["dias"], p["r"], p["w0"], p["i0"], p["c"])
    w5, rat5 = w_nivelada_sin_faltantes(p["D"], p["dias"], p["r"], p["i0"])
    R["e5_sin"] = (w5, rat5, dotacion_fija(p["D"], p["dias"], p["r"], w5, p["w0"], p["i0"], p["c"], 1))
    w6, prom6 = w_nivelada_con_faltantes(p["D"], p["dias"], p["r"], p["i0"])
    R["e6_con"] = (w6, prom6, dotacion_fija(p["D"], p["dias"], p["r"], w6, p["w0"], p["i0"], p["c"], 1))
    # 6.8: costo de despido que iguala persecución y nivelada con faltantes
    pers_f, pers_t = R["e5_pers"]
    con_f, con_cambio, con_t = R["e6_con"][2]
    desp_pers = suma(pers_f, "despide")
    desp_con = max(0, p["w0"] - R["e6_con"][0])
    base_pers = pers_t - desp_pers * p["c"]["despedir"]
    base_con = con_t - desp_con * p["c"]["despedir"]
    R["e8"] = {"despidos_pers": desp_pers, "despidos_con": desp_con, "base_pers": base_pers, "base_con": base_con,
               "despido_equilibrio": (base_con - base_pers) / (desp_pers - desp_con),
               "diferencia": con_t - pers_t}

    # 6.7
    p = E7
    R["e7"] = dotacion_fija(p["D"], p["dias"], p["r"], p["w"], p["w"], p["i0"], p["c"], p["hh"],
                            p["tope_he"], True)

    # 6.9
    p = E9
    tabla9 = {w: dotacion_fija(p["D"], p["dias"], p["r"], w, p["w0"], p["i0"], p["c"], p["hh"], p["tope_he"])
              for w in p["rango_w"]}
    w9 = min(tabla9, key=lambda w: tabla9[w][2])
    tabla9b = {w: dotacion_fija(p["D"], p["dias"], p["r"], w, p["w0_b"], p["i0"], p["c"], p["hh"], p["tope_he"])
               for w in p["rango_w"]}
    w9b = min(tabla9b, key=lambda w: tabla9b[w][2])
    R["e9"] = (w9, tabla9, w9b, tabla9b)

    # 6.10
    R["e10"] = (transporte_voraz(E10), transporte_lp(E10))

    # Caso integrador: se reconstruye la búsqueda de dotación y se compara con caso_estampa_sur.py
    C = caso.calcular()
    u6 = caso.U6
    dem = C["u4"]["pronostico_redondeado"]
    cap_mes = [d * u6["horas_dia"] / u6["hh_por_unidad"] for d in u6["dias"]]
    tabla_caso = {}
    for w in range(2, 10):
        inv, costo, falt_max = u6["inventario_inicial"], 0, 0
        cambio = costo_cambio(w, u6["trabajadores_iniciales"],
                              {"contratar": u6["costo_contratar"], "despedir": u6["costo_despedir"]})
        for d, cap in zip(dem, cap_mes):
            reg = round(w * cap)
            extra = min(max(0, d - inv - reg), round(u6["tope_extra"] * reg))
            inv = inv + reg + extra - d
            costo += (w * cap * u6["hh_por_unidad"] * u6["salario_hora"]
                      + extra * u6["hh_por_unidad"] * u6["hora_extra"]
                      + max(inv, 0) * u6["costo_mantener"] + max(-inv, 0) * u6["costo_faltante"])
            falt_max = max(falt_max, -inv)
        tabla_caso[w] = (costo + cambio, falt_max)
    w_mejor = min(tabla_caso, key=lambda w: tabla_caso[w][0])
    assert w_mejor == C["u6"]["trabajadores"], "la búsqueda no calza con caso_estampa_sur.py"
    assert round(tabla_caso[w_mejor][0]) == round(C["u6"]["costo_total"]), "el costo no calza con el caso"
    R["caso"] = {"C": C, "dem": dem, "tabla": tabla_caso, "cap_trab": [round(x) for x in cap_mes],
                 "unid_trab_dia": u6["horas_dia"] / u6["hh_por_unidad"]}
    return R


# ---------------------------------------------------------------- impresión

def imprimir(R):
    e = EJ
    pf, pt = R["ej_pers"]
    print("== Ejemplo · persecución")
    for m, f in zip(e["meses"], pf):
        print(f"   {m} neto {f['neto']} teo {fmt(f['teo'], 2)} W {f['W']} +{f['contrata']} -{f['despide']} "
              f"P {f['P']} I {f['I']} cambio {clp(f['c_cambio'])} sueldos {clp(f['sueldos'])} mant {clp(f['mantener'])}")
    print("   total", clp(pt), "| contrata", suma(pf, "contrata"), "despide", suma(pf, "despide"))
    for nombre, clave in (("sin faltantes", "ej_sin"), ("con faltantes", "ej_con")):
        w, aux, (filas, cambio, total) = R[clave]
        print(f"== Ejemplo · nivelada {nombre}: W = {w} ({aux if isinstance(aux, float) else [fmt(x, 2) for x in aux]}) cambio {clp(cambio)}")
        for m, f in zip(e["meses"], filas):
            print(f"   {m} P {f['P']} I {f['I']} sueldos {clp(f['sueldos'])} mant {clp(f['mantener'])} falt {clp(f['faltante'])} días amort {fmt(f['dias_amort'], 1)}")
        print("   total", clp(total), "| sueldos", clp(suma(filas, "sueldos")), "mant", clp(suma(filas, "mantener")),
              "falt", clp(suma(filas, "faltante")))
    wm, mix = R["ej_mix"]
    print("== Ejemplo · mixta (dotación fija + HE 15 % + subcontratación)")
    for w, (filas, cambio, total) in mix.items():
        print(f"   W {w}: {clp(total)}  HE {suma(filas, 'he')} sub {suma(filas, 'sub')}")
    filas, cambio, total = mix[wm]
    print("   mejor", wm)
    for m, f in zip(e["meses"], filas):
        print(f"   {m} reg {f['reg']} HE {fmt(f['he'])} sub {fmt(f['sub'])} I {fmt(f['I'])} sueldos {clp(f['sueldos'])} "
              f"cHE {clp(f['c_he'])} csub {clp(f['c_sub'])} mant {clp(f['mantener'])} total {clp(f['total'])}")
    print("   totales: sueldos", clp(suma(filas, "sueldos")), "HE", clp(suma(filas, "c_he")), "sub", clp(suma(filas, "c_sub")),
          "mant", clp(suma(filas, "mantener")), "TOTAL", clp(total))

    f1, t1 = R["e1"]
    print("== 6.1")
    for f in f1:
        print(f"   teo {fmt(f['teo'], 2)} W {f['W']} +{f['contrata']} -{f['despide']} P {f['P']} I {f['I']} total {clp(f['total'])}")
    print("   total", clp(t1))
    w2, rat2, (f2, c2, t2) = R["e2"]
    print("== 6.2 W", w2, [fmt(x, 2) for x in rat2], "cambio", clp(c2))
    for f in f2:
        print(f"   P {f['P']} I {f['I']} días {fmt(f['dias_amort'], 1)} total {clp(f['total'])}")
    print("   total", clp(t2), "sueldos", clp(suma(f2, "sueldos")), "mant", clp(suma(f2, "mantener")))
    print("== 6.3")
    for m, (d, inv, cm, cf) in zip(E3["meses"], R["e3"]):
        print(f"   {m} D {d} I {inv} mant {clp(cm)} falt {clp(cf)}")
    print("   mant", clp(sum(x[2] for x in R["e3"])), "falt", clp(sum(x[3] for x in R["e3"])),
          "total", clp(sum(x[2] + x[3] for x in R["e3"])))
    f5, t5 = R["e5_pers"]
    print("== 6.5 persecución")
    for f in f5:
        print(f"   teo {fmt(f['teo'], 2)} W {f['W']} +{f['contrata']} -{f['despide']} P {f['P']} I {f['I']} cambio {clp(f['c_cambio'])} sueldos {clp(f['sueldos'])} mant {clp(f['mantener'])}")
    print("   total", clp(t5), "cambios", clp(suma(f5, "c_cambio")), "sueldos", clp(suma(f5, "sueldos")), "mant", clp(suma(f5, "mantener")))
    for nombre, clave in (("6.5 nivelada sin faltantes", "e5_sin"), ("6.6 nivelada con faltantes", "e6_con")):
        w, aux, (filas, cambio, total) = R[clave]
        print(f"== {nombre}: W {w} {aux if isinstance(aux, float) else [fmt(x, 2) for x in aux]} cambio {clp(cambio)}")
        for f in filas:
            print(f"   P {f['P']} I {f['I']} mant {clp(f['mantener'])} falt {clp(f['faltante'])} días {fmt(f['dias_amort'], 1)}")
        print("   total", clp(total), "sueldos", clp(suma(filas, "sueldos")), "mant", clp(suma(filas, "mantener")), "falt", clp(suma(filas, "faltante")))
    print("== 6.8", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in R["e8"].items()})
    f7, c7, t7 = R["e7"]
    print("== 6.7")
    for f in f7:
        print(f"   reg {f['reg']} HE {fmt(f['he'])} sub {fmt(f['sub'])} I {fmt(f['I'])} sueldos {clp(f['sueldos'])} cHE {clp(f['c_he'])} csub {clp(f['c_sub'])} mant {clp(f['mantener'])}")
    print("   total", clp(t7), "HE", fmt(suma(f7, "he")), "sub", fmt(suma(f7, "sub")))
    w9, t9, w9b, t9b = R["e9"]
    print("== 6.9")
    for w in t9:
        f, c, t = t9[w]
        print(f"   W {w}: {clp(t)} (falt máx {fmt(max(max(-x['I'], 0) for x in f))}, HE {fmt(suma(f, 'he'))}) | partiendo con 17: {clp(t9b[w][2])}")
    print("   mejor", w9, "| partiendo con 17", w9b)
    f, c, t = t9[w9]
    for x in f:
        print(f"   reg {x['reg']} HE {fmt(x['he'])} I {fmt(x['I'])} total {clp(x['total'])}")
    (asign, tot), lp = R["e10"]
    print("== 6.10 voraz", clp(tot), "| LP", lp)
    for a in asign:
        print("     ", a)
    cs = R["caso"]
    C = cs["C"]
    print("== Caso: dotación", C["u6"]["trabajadores"], "costo", clp(C["u6"]["costo_total"]))
    for w, (t, fm) in cs["tabla"].items():
        print(f"   W {w}: {clp(t)} faltante máx {fmt(fm)}")
    for f in C["u6"]["plan"]:
        print("     ", {k: round(v) for k, v in f.items()})


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    """Cadenas que el .md tiene que contener tal cual."""
    e = []
    pf, pt = R["ej_pers"]
    e += [clp(pt)] + [fmt(f["teo"], 2) for f in pf] + [fmt(f["I"]) for f in pf]
    for clave in ("ej_sin", "ej_con"):
        w, aux, (filas, cambio, total) = R[clave]
        e += [clp(total), f"{w} trabajadores"] + [fmt(f["I"]) for f in filas]
    ws, ratios, _ = R["ej_sin"]
    e += [fmt(x, 2) for x in ratios]
    e += [fmt(R["ej_con"][1], 2)]
    wm, mix = R["ej_mix"]
    filas, cambio, total = mix[wm]
    e += [clp(total), clp(suma(filas, "c_he")), clp(suma(filas, "c_sub"))]
    e += [fmt(f["he"]) for f in filas if f["he"]] + [fmt(f["sub"]) for f in filas if f["sub"]]
    e += [clp(mix[w][2]) for w in (wm - 1, wm + 1)]
    e += [fmt(suma(pf, k)) for k in ("c_cambio", "sueldos", "mantener")]
    e += [clp(R["ej_con"][2][2] - total)]

    f1, t1 = R["e1"]
    e += [clp(t1)] + [fmt(f["teo"], 2) for f in f1]
    w2, rat2, (f2, c2, t2) = R["e2"]
    e += [clp(t2 - t1), clp(suma(f2, "sueldos")), clp(suma(f2, "mantener"))]
    e += [clp(t2)] + [fmt(x, 2) for x in rat2] + [fmt(f["dias_amort"], 1) for f in f2]
    e += [clp(sum(x[2] for x in R["e3"])), clp(sum(x[3] for x in R["e3"])), clp(sum(x[2] + x[3] for x in R["e3"]))]
    e += [fmt(x[1]) for x in R["e3"]]
    e += [clp(R["e5_pers"][1]), clp(R["e5_sin"][2][2]), clp(R["e6_con"][2][2])]
    e += [fmt(R["e6_con"][1], 2)] + [fmt(x, 2) for x in R["e5_sin"][1]]
    e += [clp(R["e8"]["despido_equilibrio"]), clp(R["e8"]["diferencia"])]
    f7, c7, t7 = R["e7"]
    e += [clp(t7), fmt(suma(f7, "he")), fmt(suma(f7, "sub"))]
    w9, t9, w9b, t9b = R["e9"]
    e += [clp(t9[w9][2]), clp(t9b[w9b][2]), f"{w9} trabajadores", f"{w9b} trabajadores"]
    (asign, tot), lp = R["e10"]
    e += [clp(tot)]
    if lp is not None:
        assert abs(lp - tot) < 0.5, f"el método voraz ({tot}) no llegó al óptimo de la PL ({lp})"
    cs = R["caso"]
    C = cs["C"]
    e += [clp(C["u6"]["costo_total"]), clp(cs["tabla"][3][0]), clp(cs["tabla"][5][0])]
    # filas de las tablas
    e += [fmt(f["sueldos"]) for f in pf] + [fmt(f["c_cambio"]) for f in pf]
    e += [fmt(f["total"]) for f in f1] + [fmt(f["I"]) for f in f1] + [fmt(f["I"]) for f in f2]
    for f in R["e5_pers"][0]:
        e += [fmt(f["teo"], 2), fmt(f["I"])]
    e += [fmt(f["I"]) for f in R["e5_sin"][2][0]] + [fmt(f["I"]) for f in R["e6_con"][2][0]]
    e += [clp(t9[w][2]) for w in range(12, 18)] + [clp(t9b[w][2]) for w in range(12, 18)]
    e += [f"{fmt(q)} · {clp(c)}" for _, _, q, c in asign]
    plan = C["u6"]["plan"]
    e += [clp(suma(plan, "sueldos")), clp(suma(plan, "costo_extra")), clp(suma(plan, "faltante")),
          clp(cs["tabla"][5][0] - C["u6"]["costo_total"]), fmt(cs["tabla"][3][1])]
    e += [fmt(f["produccion"]) for f in C["u6"]["plan"]] + [fmt(f["extra"]) for f in C["u6"]["plan"]]
    return e


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "06-planeacion-agregada.md").read_text(encoding="utf-8")
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
