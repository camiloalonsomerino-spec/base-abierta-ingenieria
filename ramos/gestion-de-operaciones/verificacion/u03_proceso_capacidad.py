"""Unidad 3 · Proceso y capacidad.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba
que cada resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto
queda sin respaldo.

    python u03_proceso_capacidad.py            # imprime los resultados
    python u03_proceso_capacidad.py --revisar  # además los busca en el .md
"""
from math import ceil
from pathlib import Path
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

AQUI = Path(__file__).resolve().parent

# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".").replace("-", "−")


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def capacidad(dias, turnos, horas, tasa=1):
    """Capacidad de diseño = horas disponibles × tasa de diseño."""
    return dias * turnos * horas * tasa


def utilizacion(real, diseno):
    return real / diseno


def eficiencia(real, efectiva):
    return real / efectiva


def linea(etapas):
    """etapas: {nombre: (segundos o minutos por unidad, estaciones en paralelo)}.
    Devuelve la tasa de cada etapa (unidades por hora si el tiempo está en s → ×3600; acá se
    entrega por unidad de tiempo base), el cuello de botella y el tiempo de rendimiento sin espera."""
    tasas = {e: m / t for e, (t, m) in etapas.items()}
    cuello = min(tasas, key=tasas.get)
    rendimiento = sum(t for t, _ in etapas.values())
    return tasas, cuello, rendimiento


def vme(ramas):
    """ramas: lista de (probabilidad, resultado). Valor monetario esperado."""
    assert abs(sum(p for p, _ in ramas) - 1) < 1e-9
    return sum(p * r for p, r in ramas)


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Ejemplo resuelto · Mermeladas del Laja, línea de envasado (segundos por frasco, estaciones)
EJ_ETAPAS = {"Lavado": (3.0, 1), "Llenado": (7.2, 2), "Tapado": (3.2, 1), "Etiquetado": (4.0, 1)}
EJ_OPERA = dict(dias=6, turnos=2, horas=8)
EJ_DEMANDA = 72_000          # frascos por semana del contrato
EJ_EFECTIVA = 78_000         # frascos por semana
EJ_REAL = 64_740             # frascos la semana pasada
# Árbol (millones de pesos, horizonte 4 años, sin descontar)
EJ_P_ALTA = 0.4
EJ_ARBOL = {
    "comprar": {"costo": 60, "alta": 55, "baja": 14},
    "arrendar": {"costo": 8, "alta": 22, "baja": 6},
    "esperar": {"alta": 16, "baja": 12, "costo_despues": 68},
}
EJ_ANIOS = 4

# 3.1 · empanadas congeladas: unidades por turno, horas del turno, contenido de trabajo (s)
E1 = dict(unidades=2_250, horas=7.5, contenido_s=50, unidades_b=2_700)
# 3.2 · lavandería industrial (kg)
E2 = dict(dias=6, turnos=2, horas=7, tasa=250, efectiva=18_500, real=15_910)
# 3.4 · lavado de autos (minutos por auto, puestos en paralelo)
E4 = {"Prelavado": (4, 1), "Lavado": (6, 2), "Secado": (5, 1), "Aspirado": (8, 2)}
E4_HORAS_DIA = 8
# 3.5 · planta de jugos (litros por semana)
E5 = dict(efectiva=30_000, ef_l1=0.82, ef_l2=0.76, ef_capacitado=0.88, demanda=70_000)
# 3.6 · plegadora CNC (minutos)
E6 = dict(prep=40, corrida=1.5, lotes=(60, 120), minutos_semana=40 * 60)
# 3.7 · catering (minutos)
E7 = dict(picar=12, cocer=20, armar=8, empacar=5, espera=15)
# 3.8 · clínica dental, tres estados, 3 años (millones de pesos)
E8_P = {"alta": 0.3, "media": 0.5, "baja": 0.2}
E8 = {"Segundo sillón": (18, {"alta": 20, "media": 12, "baja": 5}),
      "Ampliar horario": (4, {"alta": 14, "media": 10, "baja": 6}),
      "No hacer nada": (0, {"alta": 9, "media": 8, "baja": 6})}
E8_ANIOS = 3
# 3.9 · planta de pellets (toneladas por hora)
E9 = {"Secado": 2.0, "Prensado": 1.6, "Enfriado": 2.4, "Ensacado": 1.8}
E9_HORAS, E9_DEMANDA = 120, 230
E9_PRENSA_EXTRA, E9_ENSACADORA_EXTRA = 0.8, 1.2
# 3.10 · cervecería, decisión en dos etapas, 3 años (millones de pesos)
E10 = dict(costo_ahora=30, crece_A=30, no_A=9, crece_B1=12, no_B=10, costo_despues=32, anios=3)
E10_P = 0.5

# Caso integrador · Estampa Sur (U3 sale de caso_estampa_sur.json)
CASO_ARBOL = {  # pesos por año, horizonte 3 años
    "Comprar nueva": (9_500_000, {"gana": 7_800_000, "pierde": 3_100_000}),
    "Comprar usada": (5_200_000, {"gana": 6_200_000, "pierde": 2_600_000}),
    "No comprar": (0, {"gana": 3_400_000, "pierde": 2_400_000}),
}
CASO_P_GANA, CASO_ANIOS = 0.35, 3


def leer_caso():
    C = json.loads((AQUI / "caso_estampa_sur.json").read_text(encoding="utf-8"))
    return C["u3"], C["u9"]


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # ejemplo
    tasas_s, cuello, rend = linea(EJ_ETAPAS)
    tasas_h = {e: 3600 * t for e, t in tasas_s.items()}
    horas = capacidad(**EJ_OPERA)
    diseno = horas * tasas_h[cuello]
    takt = horas * 3600 / EJ_DEMANDA
    R["ej"] = dict(tasas_h=tasas_h, cuello=cuello, ciclo=1 / tasas_s[cuello], rend=rend, horas=horas,
                   diseno=diseno, takt=takt, U=utilizacion(EJ_REAL, diseno), E=eficiencia(EJ_REAL, EJ_EFECTIVA),
                   E_necesaria=EJ_DEMANDA / EJ_EFECTIVA, faltan=EJ_DEMANDA - EJ_REAL)
    a = EJ_ARBOL
    p, q, n = EJ_P_ALTA, 1 - EJ_P_ALTA, EJ_ANIOS
    comprar = vme([(p, n * a["comprar"]["alta"]), (q, n * a["comprar"]["baja"])]) - a["comprar"]["costo"]
    arrendar = vme([(p, n * a["arrendar"]["alta"]), (q, n * a["arrendar"]["baja"])]) - a["arrendar"]["costo"]
    alta_compra_despues = -a["esperar"]["costo_despues"] + (n - 1) * a["comprar"]["alta"]
    alta_sigue = (n - 1) * a["esperar"]["alta"]
    alta_esperar = a["esperar"]["alta"] + max(alta_compra_despues, alta_sigue)
    baja_esperar = n * a["esperar"]["baja"]
    esperar = vme([(p, alta_esperar), (q, baja_esperar)])
    R["ej_arbol"] = dict(comprar=comprar, arrendar=arrendar, esperar=esperar,
                         alta_compra_despues=alta_compra_despues, alta_sigue=alta_sigue,
                         alta_esperar=alta_esperar, baja_esperar=baja_esperar,
                         comprar_alta=n * a["comprar"]["alta"] - a["comprar"]["costo"],
                         comprar_baja=n * a["comprar"]["baja"] - a["comprar"]["costo"],
                         arrendar_alta=n * a["arrendar"]["alta"] - a["arrendar"]["costo"],
                         arrendar_baja=n * a["arrendar"]["baja"] - a["arrendar"]["costo"])

    # 3.1
    takt1 = E1["horas"] * 3600 / E1["unidades"]
    takt1b = E1["horas"] * 3600 / E1["unidades_b"]
    R["e1"] = dict(takt=takt1, est=E1["contenido_s"] / takt1, est_min=ceil(E1["contenido_s"] / takt1),
                   takt_b=takt1b, est_b=E1["contenido_s"] / takt1b)
    # 3.2
    d2 = capacidad(E2["dias"], E2["turnos"], E2["horas"], E2["tasa"])
    R["e2"] = dict(horas=capacidad(E2["dias"], E2["turnos"], E2["horas"]), diseno=d2,
                   U=utilizacion(E2["real"], d2), E=eficiencia(E2["real"], E2["efectiva"]))
    # 3.4
    t4, c4, r4 = linea(E4)
    t4h = {e: 60 * t for e, t in t4.items()}
    E4b = dict(E4); E4b["Secado"] = (5, 2)
    t4b, c4b, _ = linea(E4b)
    t4bh = {e: 60 * t for e, t in t4b.items()}
    R["e4"] = dict(tasas=t4h, cuello=c4, rend=r4, dia=t4h[c4] * E4_HORAS_DIA,
                   tasas_b=t4bh, nueva=min(t4bh.values()), alza=min(t4bh.values()) / t4h[c4] - 1)
    # 3.5
    l1 = E5["efectiva"] * E5["ef_l1"]; l2 = E5["efectiva"] * E5["ef_l2"]
    cap = E5["efectiva"] * E5["ef_capacitado"]
    R["e5"] = dict(l1=l1, l2=l2, total=l1 + l2, total_cap=2 * cap, por_linea=cap,
                   lineas=E5["demanda"] / cap, lineas_min=ceil(E5["demanda"] / cap))
    # 3.6
    r6 = {}
    for lote in E6["lotes"]:
        op = E6["prep"] + E6["corrida"] * lote
        r6[lote] = dict(op=op, por_pieza=op / lote, semana=E6["minutos_semana"] / (op / lote))
    a, b = E6["lotes"]
    R["e6"] = dict(lotes=r6, alza=r6[b]["semana"] / r6[a]["semana"] - 1)
    # 3.7
    serie = E7["picar"] + E7["cocer"] + E7["armar"] + E7["empacar"]
    paralelo = max(E7["picar"], E7["cocer"]) + E7["armar"] + E7["empacar"]
    R["e7"] = dict(serie=serie, paralelo=paralelo, baja=1 - paralelo / serie, con_espera=paralelo + E7["espera"])
    # 3.8
    R["e8"] = {alt: E8_ANIOS * vme([(E8_P[s], v[s]) for s in E8_P]) - costo for alt, (costo, v) in E8.items()}
    R["e8_anual"] = {alt: vme([(E8_P[s], v[s]) for s in E8_P]) for alt, (costo, v) in E8.items()}
    # 3.9
    cap9 = {k: v * E9_HORAS for k, v in E9.items()}
    e9b = dict(E9); e9b["Prensado"] += E9_PRENSA_EXTRA
    e9c = dict(e9b); e9c["Ensacado"] += E9_ENSACADORA_EXTRA
    tasa_dem = E9_DEMANDA / E9_HORAS
    R["e9"] = dict(cap=cap9, actual=min(cap9.values()), cuello=min(E9, key=E9.get),
                   con_prensa=min(e9b.values()) * E9_HORAS, cuello_b=min(e9b, key=e9b.get),
                   con_ambas=min(e9c.values()) * E9_HORAS, cuello_c=min(e9c, key=e9c.get),
                   tasa_dem=tasa_dem, util={k: tasa_dem / v for k, v in e9c.items()})
    # 3.10
    e = E10
    def A(p):
        return p * e["anios"] * e["crece_A"] + (1 - p) * e["anios"] * e["no_A"] - e["costo_ahora"]
    crece_compra = -e["costo_despues"] + (e["anios"] - 1) * e["crece_A"]
    crece_sigue = (e["anios"] - 1) * e["crece_B1"]
    crece_B = e["crece_B1"] + max(crece_compra, crece_sigue)
    no_B = e["anios"] * e["no_B"]
    def B(p):
        return p * crece_B + (1 - p) * no_B
    # A(p) = a0 + a1 p ; B(p) = b0 + b1 p → indiferencia
    a0, a1 = A(0), A(1) - A(0)
    b0, b1 = B(0), B(1) - B(0)
    p_ind = (b0 - a0) / (a1 - b1)
    R["e10"] = dict(A=A(E10_P), B=B(E10_P), crece_compra=crece_compra, crece_sigue=crece_sigue,
                    crece_B=crece_B, no_B=no_B, a0=a0, a1=a1, b0=b0, b1=b1, p_ind=p_ind,
                    A07=A(0.7), B07=B(0.7))

    # caso
    u3, u9 = leer_caso()
    assert u3["capacidad_diseno_h"] == 45 and u3["capacidad_efectiva_h"] == 40
    sem6 = next(f for f in u9 if f["sem"] == 6)
    esperada = u3["capacidad_efectiva_h"] * u3["eficiencia"]
    caso_vme = {alt: CASO_ANIOS * vme([(CASO_P_GANA, v["gana"]), (1 - CASO_P_GANA, v["pierde"])]) - costo
                for alt, (costo, v) in CASO_ARBOL.items()}
    # probabilidad desde la que cada máquina le gana a no comprar (lineal en p)
    def dif(alt, base):
        (c1, v1), (c2, v2) = CASO_ARBOL[alt], CASO_ARBOL[base]
        pendiente = CASO_ANIOS * ((v1["gana"] - v2["gana"]) - (v1["pierde"] - v2["pierde"]))
        corte = CASO_ANIOS * (v1["pierde"] - v2["pierde"]) - (c1 - c2)
        return -corte / pendiente
    R["caso"] = dict(diseno=u3["capacidad_diseno_h"], efectiva=u3["capacidad_efectiva_h"],
                     real=34, U=u3["utilizacion"], E=u3["eficiencia"], esperada=esperada,
                     carga6=sem6["estampado_h"], holgura=45 - 34, vme=caso_vme,
                     p_usada=dif("Comprar usada", "No comprar"), p_nueva=dif("Comprar nueva", "No comprar"),
                     p_nueva_usada=dif("Comprar nueva", "Comprar usada"))
    return R


def imprimir(R):
    ej = R["ej"]
    print("== Ejemplo · línea de envasado")
    print("   tasas por hora", {k: round(v, 1) for k, v in ej["tasas_h"].items()}, "cuello", ej["cuello"],
          "ciclo", ej["ciclo"], "s · rendimiento", ej["rend"], "s")
    print("   horas", ej["horas"], "diseño", ej["diseno"], "takt", ej["takt"], "s")
    print("   U", pct(ej["U"]), "E", pct(ej["E"]), "E necesaria", pct(ej["E_necesaria"]), "faltan", ej["faltan"])
    print("   árbol", {k: round(v, 2) for k, v in R["ej_arbol"].items()})
    print("== 3.1", R["e1"])
    print("== 3.2", R["e2"], pct(R["e2"]["U"]), pct(R["e2"]["E"]))
    print("== 3.4", R["e4"])
    print("== 3.5", R["e5"])
    print("== 3.6", R["e6"])
    print("== 3.7", R["e7"])
    print("== 3.8", R["e8"], "anual", R["e8_anual"])
    print("== 3.9", R["e9"])
    print("== 3.10", {k: round(v, 4) for k, v in R["e10"].items()})
    print("== caso", R["caso"])


# ---------------------------------------------------------------- revisión contra el texto

def como_se_lee(md):
    """Deja las fórmulas como se ven impresas: 74{,}9\\ \\% → 74,9 %, \\text{ h} → h, sin los $."""
    md = re.sub(r"\\text\{([^}]*)\}", r"\1", md)
    md = re.sub(r"\{(\d[\d.]*)\}", r"\1", md)          # ${72.000} / … (número que abre una fórmula)
    return md.replace("{,}", ",").replace("\\ \\%", " %").replace("\\%", "%").replace("$", "")


def esperados(R):
    """Cadenas que el .md tiene que contener tal cual."""
    ej, ar = R["ej"], R["ej_arbol"]
    e = [fmt(v, 0) + " frascos/h" for v in ej["tasas_h"].values()]
    e += [fmt(ej["rend"]) + " s", fmt(ej["diseno"], 0), fmt(ej["takt"]) + " s",
          pct(ej["U"]), pct(ej["E"]), pct(ej["E_necesaria"]), fmt(ej["faltan"], 0)]
    e += [fmt(ar[k]) for k in ("comprar", "arrendar", "esperar")]
    e += [fmt(ar[k], 0) for k in ("alta_compra_despues", "alta_sigue", "alta_esperar", "baja_esperar",
                                  "comprar_alta", "comprar_baja", "arrendar_alta", "arrendar_baja")]
    e1 = R["e1"]; e += [fmt(e1["takt"], 0) + " s", fmt(e1["est"], 2), fmt(e1["takt_b"], 0) + " s"]
    e2 = R["e2"]; e += [fmt(e2["diseno"], 0) + " kg", pct(e2["U"]), pct(e2["E"])]
    e4 = R["e4"]; e += [fmt(v, 0) + " autos/h" for v in e4["tasas"].values()]
    e += [f"{e4['rend']} min", fmt(e4["dia"], 0) + " autos", pct(e4["alza"], 0)]
    e5 = R["e5"]; e += [fmt(e5[k], 0) + " L" for k in ("l1", "l2", "total", "total_cap", "por_linea")]
    e += [fmt(e5["lineas"], 2)]
    for lote, v in R["e6"]["lotes"].items():
        e += [fmt(v["op"], 0) + " min", fmt(v["por_pieza"], 2) + " min", fmt(v["semana"], 0) + " piezas"]
    e += [pct(R["e6"]["alza"])]
    e7 = R["e7"]; e += [f"{e7['serie']} min", f"{e7['paralelo']} min", pct(e7["baja"]), f"{e7['con_espera']} min"]
    e += [fmt(v) for v in R["e8"].values()] + [fmt(v, 1) for v in R["e8_anual"].values()]
    e9 = R["e9"]; e += [fmt(e9["actual"], 0) + " t", fmt(e9["con_prensa"], 0) + " t", fmt(e9["con_ambas"], 0) + " t"]
    e += [pct(v) for v in e9["util"].values()] + [fmt(e9["tasa_dem"], 2)]
    e10 = R["e10"]; e += [fmt(e10[k]) for k in ("A", "B", "A07", "B07")] + [fmt(e10["p_ind"], 2)]
    e += [fmt(e10[k], 0) for k in ("crece_compra", "crece_sigue", "crece_B", "no_B")]
    c = R["caso"]; e += [pct(c["U"]), pct(c["E"]), fmt(c["esperada"], 0) + " h", fmt(c["carga6"], 0) + " h"]
    e += [fmt(v, 0) for v in c["vme"].values()] + [fmt(c[k], 2) for k in ("p_usada", "p_nueva", "p_nueva_usada")]
    e += [fmt(c["vme"]["No comprar"] - c["vme"]["Comprar usada"], 0), f"{c['holgura']} horas de holgura",
          fmt(c["efectiva"] * 0.01) + " horas"]
    return e


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if "--revisar" in sys.argv:
        md = como_se_lee((AQUI.parent / "unidades" / "03-proceso-y-capacidad.md").read_text(encoding="utf-8"))
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
