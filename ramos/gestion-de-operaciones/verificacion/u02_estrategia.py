"""Unidad 2 · Estrategia de operaciones.

La unidad es conceptual, pero sus cifras (márgenes por segmento, puntajes ponderados, costos de un
compromiso) se recalculan acá desde los datos. Con --revisar, comprueba que cada resultado aparezca
escrito tal cual en el .md.

    python u02_estrategia.py            # imprime los resultados
    python u02_estrategia.py --revisar  # además los busca en el .md
"""
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))           # con -P el directorio del script no entra solo
import caso_estampa_sur as caso          # noqa: E402  (fuente única del caso integrador)

# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    """Número a la chilena: coma decimal, punto de miles, signo menos tipográfico."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".").replace("-", "−")


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def segmentos(datos):
    """datos: {segmento: (volumen, precio, costo variable unitario)} → margen, contribución y participaciones."""
    filas = {s: {"vol": v, "precio": p, "cv": c, "margen": p - c, "margen_pct": (p - c) / p, "contrib": v * (p - c)}
             for s, (v, p, c) in datos.items()}
    tv = sum(f["vol"] for f in filas.values())
    tc = sum(f["contrib"] for f in filas.values())
    for f in filas.values():
        f["part_vol"] = f["vol"] / tv
        f["part_contrib"] = f["contrib"] / tc
    return filas, tc


def puntaje(pesos, notas):
    return sum(pesos[k] * notas[k] for k in pesos)


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Ejemplo resuelto · Lavandería Reloncaví, Puerto Montt: (kg al mes, CLP por kg, costo variable CLP por kg)
EJ_SEG = {"clínicas": (18_000, 1_450, 1_020), "hoteles": (32_000, 980, 830)}
EJ_PESOS = {
    "clínicas": {"costo": 0.15, "calidad": 0.40, "entrega": 0.30, "flexibilidad": 0.15},
    "hoteles":  {"costo": 0.50, "calidad": 0.15, "entrega": 0.20, "flexibilidad": 0.15},
}
EJ_NOTAS = {  # de 1 a 5
    "A túnel continuo": {"costo": 5, "calidad": 3, "entrega": 4, "flexibilidad": 2},
    "B celdas de lavado": {"costo": 3, "calidad": 5, "entrega": 4, "flexibilidad": 5},
}

# Ejercicio 2.5 · maestranza de Talcahuano: (órdenes al mes, precio prom., costo variable prom.) y horas de torno CNC por orden
E5 = {"minería": (40, 1_850_000, 1_240_000), "pesca": (65, 920_000, 700_000), "particulares": (150, 210_000, 150_000)}
E5_HORAS = {"minería": 30, "pesca": 12, "particulares": 3}

# Ejercicio 2.6 · envases plásticos: eliminar la inspección final
E6 = {"envases": 48_000, "ahorro": 1_350_000, "fuga_antes": 0.008, "fuga_despues": 0.025, "costo_fuga": 1_500,
      "prob_perder": 0.10, "margen_cliente": 4_200_000}

# Ejercicio 2.7 · licitación de mantención para una faena: notas de 1 a 10 y calificadores
E7_PESOS = {"precio": 0.35, "calidad": 0.30, "rapidez": 0.20, "flexibilidad": 0.15}
E7 = {
    "P": ({"precio": 9, "calidad": 6, "rapidez": 7, "flexibilidad": 6}, True, 6),
    "Q": ({"precio": 7, "calidad": 8, "rapidez": 8, "flexibilidad": 7}, True, 3),
    "R": ({"precio": 6, "calidad": 9, "rapidez": 7, "flexibilidad": 8}, True, 4),
    "S": ({"precio": 10, "calidad": 5, "rapidez": 6, "flexibilidad": 9}, False, 2),
}   # (notas, acreditación de seguridad, horas de respuesta)
E7_TOPE_H = 4

# Ejercicio 2.9 · muebles de cocina en Chillán: línea mixta o planta dentro de la planta (CLP al mes)
E9 = {"costo_hora": 45_000,
      "mixta": {"cambios": 60, "h_cambio": 2.5, "fijo_extra": 0, "plazo": 15},
      "enfocada": {"cambios": 50, "h_cambio": 1.0, "fijo_extra": 4_900_000, "plazo": 8},
      "margen_pedido": 140_000, "pedidos_extra": 6}

# Caso integrador · Estampa Sur: segmentos de clientes (participación en unidades, precio, costo variable, tamaño de pedido)
CASO_SEG = {"colegios y clubes": (0.40, 4_800, 3_150, 180), "empresas": (0.40, 4_500, 3_050, 300),
            "marcas locales": (0.20, 5_900, 3_600, 60)}
CASO_PRECIO_U1 = 4_900          # precio promedio que usa la unidad 1


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    seg, tc = segmentos(EJ_SEG)
    pj = {alt: {s: puntaje(EJ_PESOS[s], n) for s in EJ_PESOS} for alt, n in EJ_NOTAS.items()}
    comb = {alt: sum(seg[s]["part_contrib"] * v for s, v in d.items()) for alt, d in pj.items()}
    # participación de las clínicas en la que A y B empatan: s·Ac + (1−s)·Ah = s·Bc + (1−s)·Bh
    a, b = pj["A túnel continuo"], pj["B celdas de lavado"]
    s_emp = (b["hoteles"] - a["hoteles"]) / ((a["clínicas"] - a["hoteles"]) - (b["clínicas"] - b["hoteles"]))
    R["ej"] = {"seg": seg, "total": tc, "puntajes": pj, "combinado": comb, "empate": s_emp}

    seg5, tc5 = segmentos({k: v for k, v in E5.items()})
    for s, f in seg5.items():
        f["horas"] = E5_HORAS[s] * f["vol"]
        f["por_hora"] = f["margen"] / E5_HORAS[s]
    R["e5"] = (seg5, tc5, sum(f["horas"] for f in seg5.values()))

    extra = E6["envases"] * (E6["fuga_despues"] - E6["fuga_antes"])
    costo_extra = extra * E6["costo_fuga"]
    riesgo = E6["prob_perder"] * E6["margen_cliente"]
    R["e6"] = {"defectos_extra": extra, "costo_extra": costo_extra, "neto": E6["ahorro"] - costo_extra,
               "riesgo": riesgo, "neto_con_riesgo": E6["ahorro"] - costo_extra - riesgo,
               "costo_fuga_equilibrio": E6["ahorro"] / extra}

    p7 = {k: puntaje(E7_PESOS, n) for k, (n, _, _) in E7.items()}
    pasan = [k for k, (_, acr, h) in E7.items() if acr and h <= E7_TOPE_H]
    gana_sin = max(p7, key=p7.get)
    gana_con = max(pasan, key=p7.get)
    nq, nr = E7["Q"][0], E7["R"][0]
    # pasar δ de peso desde precio a calidad: Q + δ(nq_cal − nq_pre) = R + δ(nr_cal − nr_pre)
    delta = (p7["Q"] - p7["R"]) / ((nr["calidad"] - nr["precio"]) - (nq["calidad"] - nq["precio"]))
    R["e7"] = {"puntajes": p7, "pasan": pasan, "gana_sin": gana_sin, "gana_con": gana_con, "delta": delta,
               "peso_precio": E7_PESOS["precio"] - delta, "peso_calidad": E7_PESOS["calidad"] + delta}

    r9 = {}
    for k in ("mixta", "enfocada"):
        d = E9[k]
        h = d["cambios"] * d["h_cambio"]
        r9[k] = {"horas": h, "costo_cambios": h * E9["costo_hora"], "total": h * E9["costo_hora"] + d["fijo_extra"]}
    dif = r9["enfocada"]["total"] - r9["mixta"]["total"]
    ganancia = E9["margen_pedido"] * E9["pedidos_extra"]
    R["e9"] = {"r": r9, "dif": dif, "ganancia": ganancia, "neto": ganancia - dif,
               "pedidos_equilibrio": dif / E9["margen_pedido"]}

    C = caso.calcular()
    demanda = C["u4"]["pronostico_redondeado"][0]
    datos = {s: (part * demanda, p, c) for s, (part, p, c, _) in CASO_SEG.items()}
    segc, tcc = segmentos(datos)
    pedidos = {s: segc[s]["vol"] / CASO_SEG[s][3] for s in CASO_SEG}
    tp = sum(pedidos.values())
    precio_prom = sum(part * p for part, p, _, _ in CASO_SEG.values())
    R["caso"] = {"demanda": demanda, "seg": segc, "total": tcc, "pedidos": pedidos,
                 "part_pedidos": {s: v / tp for s, v in pedidos.items()}, "total_pedidos": tp,
                 "precio_prom": precio_prom, "calza_u1": abs(precio_prom - CASO_PRECIO_U1) < 1e-9}
    return R


def imprimir(R):
    ej = R["ej"]
    print("== Ejemplo · Lavandería Reloncaví")
    for s, f in ej["seg"].items():
        print("  ", s, f)
    print("   contribución total", ej["total"])
    print("   puntajes", ej["puntajes"])
    print("   combinado", ej["combinado"], "| empate con participación de clínicas", ej["empate"])
    seg5, tc5, h5 = R["e5"]
    print("== 2.5 total", tc5, "horas", h5)
    for s, f in seg5.items():
        print("  ", s, f)
    print("== 2.6", R["e6"])
    print("== 2.7", R["e7"])
    print("== 2.9", R["e9"])
    c = R["caso"]
    print("== Caso · demanda", c["demanda"], "precio promedio", c["precio_prom"], "calza con U1:", c["calza_u1"])
    for s, f in c["seg"].items():
        print("  ", s, f, "pedidos", round(c["pedidos"][s], 2), "part. pedidos", round(c["part_pedidos"][s], 4))
    print("   contribución total", c["total"], "pedidos", c["total_pedidos"])


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    """Cadenas que el .md tiene que contener tal cual."""
    e = []
    ej = R["ej"]
    for f in ej["seg"].values():
        e += [fmt(f["margen"], 0), fmt(f["contrib"], 0), pct(f["part_vol"]), pct(f["part_contrib"]), pct(f["margen_pct"])]
    e += [fmt(ej["total"], 0)]
    for d in ej["puntajes"].values():
        e += [fmt(v, 2) for v in d.values()]
    e += [fmt(v, 2) for v in ej["combinado"].values()]
    e += [pct(ej["empate"])]
    seg5, tc5, h5 = R["e5"]
    for f in seg5.values():
        e += [fmt(f["margen"], 0), fmt(f["contrib"], 0), pct(f["part_contrib"]), pct(f["part_vol"]), fmt(f["por_hora"], 0)]
    e += [fmt(tc5, 0), fmt(h5, 0)]
    e6 = R["e6"]
    e += [fmt(e6["defectos_extra"], 0), fmt(e6["costo_extra"], 0), fmt(e6["neto"], 0), fmt(e6["riesgo"], 0),
          fmt(e6["neto_con_riesgo"], 0), fmt(e6["costo_fuga_equilibrio"], 0)]
    e7 = R["e7"]
    e += [fmt(v, 2) for v in e7["puntajes"].values()]
    e += [fmt(e7["peso_precio"], 2), fmt(e7["peso_calidad"], 2)]
    e9 = R["e9"]
    for v in e9["r"].values():
        e += [fmt(v["horas"], 0) + " h", fmt(v["costo_cambios"], 0), fmt(v["total"], 0)]
    e += [fmt(e9["dif"], 0), fmt(e9["ganancia"], 0), fmt(e9["neto"], 0), fmt(e9["pedidos_equilibrio"], 2)]
    c = R["caso"]
    for s, f in c["seg"].items():
        e += [fmt(f["vol"], 0), fmt(f["margen"], 0), fmt(f["contrib"], 0), pct(f["part_contrib"]),
              fmt(c["pedidos"][s], 1), pct(c["part_pedidos"][s])]
    e += [fmt(c["total"], 0), fmt(c["total_pedidos"], 1), fmt(c["demanda"], 0)]
    return e


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if "--revisar" in sys.argv:
        md = (AQUI.parent / "unidades" / "02-estrategia-de-operaciones.md").read_text(encoding="utf-8")
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
