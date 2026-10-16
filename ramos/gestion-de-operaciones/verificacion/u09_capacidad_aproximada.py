"""Unidad 9 · Capacidad aproximada (RCCP).

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado (y cada fila de cada plan de capacidad) aparezca escrito tal cual en el .md.

    python u09_capacidad_aproximada.py            # imprime los resultados y las tablas
    python u09_capacidad_aproximada.py --revisar  # además los busca en el .md
"""
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))   # con -P la carpeta del script no entra sola
import caso_estampa_sur as caso

# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    if s.startswith("-"):
        s = "−" + s[1:] if s.strip("-0,.") else s[1:]     # signo menos tipográfico; −0,0 se escribe 0,0
    return s


def lista_capacidad(rutas, ldm=None):
    """rutas: {item: [(operación, centro, tiempo h, aprovechamiento), ...]} en el orden de la ruta.
    ldm: {padre: [(hijo, cantidad), ...]}. El hijo lo consume la PRIMERA operación del padre.
    Devuelve, por ítem, las filas (op, centro, bruto, neto, t, carga) para 1 unidad del producto final
    y la carga total por centro. Se recorre la ruta desde la última operación hacia la primera:
    neto_i = bruto_i / a_i ; bruto de la operación anterior = neto_i."""
    ldm = ldm or {}
    filas, carga = {}, {}

    def recorrer(item, salida):
        bruto, out = salida, []
        for op, ct, t, a in reversed(rutas[item]):
            neto = bruto / a
            out.append((op, ct, bruto, neto, t, neto * t))
            carga[ct] = carga.get(ct, 0) + neto * t
            bruto = neto
        out.reverse()
        filas[item] = out
        for hijo, q in ldm.get(item, []):
            recorrer(hijo, q * out[0][3])          # la primera operación del padre consume al hijo

    return recorrer, filas, carga


def factores(producto, rutas, ldm=None):
    recorrer, filas, carga = lista_capacidad(rutas, ldm)
    recorrer(producto, 1.0)
    return filas, carga


def plan(mps_por_prod, factor_por_prod, capacidad):
    """Plan de capacidad de un centro: carga = Σ factor × MPS, desviación = capacidad − carga."""
    n = len(next(iter(mps_por_prod.values())))
    cargas = {p: [round(factor_por_prod[p], 3) * m for m in mps] for p, mps in mps_por_prod.items()}
    total = [sum(cargas[p][t] for p in cargas) for t in range(n)]
    cap = capacidad if isinstance(capacidad, list) else [capacidad] * n
    dev = [c - x for c, x in zip(cap, total)]
    acum, s = [], 0
    for d in dev:
        s += d
        acum.append(s)
    return {"cargas": cargas, "total": total, "cap": cap, "dev": dev, "acum": acum}


def fila(rotulo, valores, dec=1):
    return f"| {rotulo} | " + " | ".join(fmt(v, dec) for v in valores) + " |"


def filas_plan(p, dec=1):
    return [fila("Plan de capacidad", p["total"], dec), fila("Capacidad disponible", p["cap"], dec),
            fila("Desviación", p["dev"], dec), fila("Desv. acumulada", p["acum"], dec)]


def r3(x):
    return fmt(x, 3)


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Ejemplo resuelto · Fierros del Laja (Los Ángeles): parrilla (con 2 rejillas) y brasero
EJ_RUTAS = {
    "Parrilla": [("O1", "Soldadura", 0.40, 0.96), ("O2", "Pintura", 0.24, 0.98)],
    "Rejilla":  [("O3", "Corte", 0.08, 0.94), ("O4", "Soldadura", 0.14, 0.97)],
    "Brasero":  [("O5", "Corte", 0.22, 0.96), ("O6", "Soldadura", 0.30, 0.92), ("O7", "Pintura", 0.20, 0.98)],
}
EJ_LDM = {"Parrilla": [("Rejilla", 2)]}
HORAS_SEMANA = 40                                   # 8 h × 5 días por persona
EJ_PERSONAS = {"Corte": [2] * 6, "Soldadura": [5] * 6, "Pintura": [2, 2, 2, 2, 1, 1]}   # pintura: vacaciones en 5 y 6
EJ_MPS = {"Parrilla": [0, 230, 260, 0, 310, 240], "Brasero": [210, 0, 190, 250, 0, 270]}

# 9.1 · taller de cerámica: aprovechamiento de cada operación, en orden
E1_OPS = [("Moldeado", 0.93), ("Primera cocción", 0.89), ("Esmaltado", 0.96), ("Segunda cocción", 0.97)]
E1_BUENAS = 1200
# 9.2 · capacidad estándar y efectiva
E2_COSTURA = dict(personas=7, horas_dia=8.5, dias=5)
E2_INYECCION = dict(maquinas=3, turnos=2, horas_turno=8, dias=6, utilizacion=0.91, eficiencia=0.87)
# 9.3 · tabla de picar (sin componentes)
E3_RUTAS = {"Tabla": [("O1", "Corte", 0.05, 0.97), ("O2", "Cepillado", 0.07, 0.96), ("O3", "Lijado y aceite", 0.09, 0.99)]}
# 9.4 · un centro, factor dado
E4_FACTOR, E4_MPS, E4_PERSONAS = 0.62, [310, 0, 420, 280, 0, 390], 4
# 9.5 · velador con dos cajones
E5_RUTAS = {
    "Velador": [("O1", "Armado", 0.35, 0.97), ("O2", "Barnizado", 0.28, 0.96)],
    "Cajón":   [("O3", "Corte", 0.06, 0.93), ("O4", "Armado", 0.09, 0.98)],
}
E5_LDM = {"Velador": [("Cajón", 2)]}
# 9.6 · dos productos y dos centros con factores dados (h por unidad)
E6_FACT = {"X": {"CT-A": 0.45, "CT-B": 0.20}, "Y": {"CT-A": 0.30, "CT-B": 0.55}}
E6_MPS = {"X": [200, 0, 260, 0, 240], "Y": [0, 170, 140, 210, 0]}
E6_CAP = {"CT-A": 120, "CT-B": 80}
# 9.7 · perfil de recursos: el componente W se fabrica la semana anterior al producto Z
E7_MPS = [0, 240, 0, 300, 260]
E7_FACT_W, E7_CAP = 0.35, 80                         # h de CT1 por unidad de Z (vía W), capacidad de CT1
# 9.8 y 9.9 · horas extra y subcontrato
E8_PLAN, E8_CAP = [210, 260, 190, 280], 200
E8_TOPE_EXTRA, E8_C_EXTRA, E8_C_SUB = 0.20, 9_000, 14_000
# 9.10 · embotelladora de aceite de oliva: aprovechamiento mínimo del llenado
E10_RUTA = [("O1", "Llenado", 0.010, 0.91), ("O2", "Taponado", 0.004, 0.98), ("O3", "Etiquetado", 0.006, 0.99)]
E10_MPS, E10_PERSONAS = 14_600, 4


# ---------------------------------------------------------------- resultados

def plan_ejemplo(rutas=EJ_RUTAS):
    fac = {p: factores(p, rutas, EJ_LDM)[1] for p in ("Parrilla", "Brasero")}
    planes = {ct: plan(EJ_MPS, {p: fac[p].get(ct, 0) for p in fac}, [n * HORAS_SEMANA for n in EJ_PERSONAS[ct]])
              for ct in EJ_PERSONAS}
    return fac, planes


def resultados():
    R = {}
    filas_p, _ = factores("Parrilla", EJ_RUTAS, EJ_LDM)
    filas_b, _ = factores("Brasero", EJ_RUTAS, EJ_LDM)
    fac, planes = plan_ejemplo()
    R["ej"] = {"filas_p": filas_p, "filas_b": filas_b, "fac": fac, "planes": planes}

    # 9.1
    x, etapas = E1_BUENAS, []
    for nombre, a in reversed(E1_OPS):
        x = x / a
        etapas.append((nombre, x))
    etapas.reverse()
    total_a = 1
    for _, a in E1_OPS:
        total_a *= a
    R["e1"] = {"etapas": etapas, "ingresar": etapas[0][1], "rend_total": total_a}
    # 9.2
    c = E2_COSTURA; i = E2_INYECCION
    R["e2"] = {"costura": c["personas"] * c["horas_dia"] * c["dias"],
               "iny_diseno": i["maquinas"] * i["turnos"] * i["horas_turno"] * i["dias"],
               "iny_efectiva": i["maquinas"] * i["turnos"] * i["horas_turno"] * i["dias"] * i["utilizacion"] * i["eficiencia"]}
    # 9.3
    f3, c3 = factores("Tabla", E3_RUTAS)
    R["e3"] = {"filas": f3, "carga": c3, "total": sum(c3.values())}
    # 9.4
    R["e4"] = plan({"P": E4_MPS}, {"P": E4_FACTOR}, E4_PERSONAS * HORAS_SEMANA)
    # 9.5
    f5, c5 = factores("Velador", E5_RUTAS, E5_LDM)
    R["e5"] = {"filas": f5, "carga": c5}
    # 9.6
    R["e6"] = {ct: plan(E6_MPS, {p: E6_FACT[p][ct] for p in E6_FACT}, E6_CAP[ct]) for ct in E6_CAP}
    # 9.7
    lista = plan({"Z": E7_MPS}, {"Z": E7_FACT_W}, E7_CAP)
    adelantado = E7_MPS[1:] + [0]                      # la carga de W cae una semana antes
    perfil = plan({"Z": adelantado}, {"Z": E7_FACT_W}, E7_CAP)
    R["e7"] = {"lista": lista, "perfil": perfil}
    # 9.8 · sin mover trabajo: extra hasta el tope, el resto se subcontrata
    tope = E8_TOPE_EXTRA * E8_CAP
    p8 = plan({"P": E8_PLAN}, {"P": 1}, E8_CAP)
    extra = [min(max(0, -d), tope) for d in p8["dev"]]
    sub = [max(0, -d) - e for d, e in zip(p8["dev"], extra)]
    R["e8"] = {"plan": p8, "tope": tope, "extra": extra, "sub": sub,
               "c_extra": sum(extra) * E8_C_EXTRA, "c_sub": sum(sub) * E8_C_SUB,
               "c_total": sum(extra) * E8_C_EXTRA + sum(sub) * E8_C_SUB}
    # 9.9 · se puede adelantar trabajo (producir antes y guardar): óptimo por programación lineal pequeña,
    # resuelto por fuerza bruta en pasos de 1 h. x_t = horas extra en t; y_t = subcontrato en t.
    # Factibilidad: para cada t, Σ_{s≤t}(cap + x_s + y_s) ≥ Σ_{s≤t} carga_s  (lo de antes puede cubrir lo de después).
    n = len(E8_PLAN)
    mejor = None
    from itertools import product as prod
    rango = range(0, int(tope) + 1)
    for xs in prod(rango, repeat=n):
        acum_ok, s, faltan_sub = True, 0, []
        # subcontrato mínimo necesario dado xs: se cubre al final de cada semana lo que falte
        y, s = [0] * n, 0
        for t in range(n):
            s += E8_CAP + xs[t] - E8_PLAN[t] + y[t]
            if s < 0:
                y[t] += -s
                s = 0
        c = sum(xs) * E8_C_EXTRA + sum(y) * E8_C_SUB
        if mejor is None or c < mejor[0] or (c == mejor[0] and sum(xs) < sum(mejor[1])):
            mejor = (c, xs, y)
    R["e9"] = {"costo": mejor[0], "extra": list(mejor[1]), "sub": mejor[2], "horas": sum(mejor[1]) + sum(mejor[2]),
               "ahorro": R["e8"]["c_total"] - mejor[0]}
    # 9.10 · carga del llenado = MPS · t1 / (a1·a2·a3); se despeja a1 para que quepa en la capacidad
    (o1, _, t1, a1), (_, _, _, a2), (_, _, _, a3) = E10_RUTA
    cap10 = E10_PERSONAS * HORAS_SEMANA
    carga10 = E10_MPS * t1 / (a1 * a2 * a3)
    f10, c10 = factores("Aceite", {"Aceite": E10_RUTA})
    R["e10"] = {"carga": carga10, "cap": cap10, "deficit": carga10 - cap10,
                "a1_min": E10_MPS * t1 / (cap10 * a2 * a3), "a3_min": E10_MPS * t1 / (cap10 * a1 * a2),
                "botellas_llenado": E10_MPS / (a1 * a2 * a3), "cargas": c10}

    # caso integrador
    C = caso.calcular()
    cap = {"estampado": C["u3"]["capacidad_efectiva_h"], "planchado": caso.U9["capacidad_planchado_h"]}
    est = [c["estampado_h"] for c in C["u9"]]
    pla = [c["planchado_h"] for c in C["u9"]]
    def desv(carga, c):
        dev = [c - x for x in carga]; acum, s = [], 0
        for d in dev:
            s += d; acum.append(s)
        return {"total": carga, "cap": [c] * len(carga), "dev": dev, "acum": acum}
    mps = {p: [f["MPS"] for f in C["u7"][p]] for p in caso.PRODUCTOS}
    lote_h = {p: (d["lote"] * d["est_s"] / 3600, d["lote"] * d["pla_s"] / 3600) for p, d in caso.PRODUCTOS.items()}
    # propuestas para la semana 6 (no cambian el caso: se discuten)
    props = {}
    for p in ("gorros", "bolsas"):
        e5, p5 = est[4] + lote_h[p][0], pla[4] + lote_h[p][1]
        e6, p6 = est[5] - lote_h[p][0], pla[5] - lote_h[p][1]
        props[p] = {"sem5": (e5, p5), "sem6": (e6, p6), "holgura_pla6": cap["planchado"] - p6}
    R["caso"] = {"mps": mps, "lote_h": lote_h, "cap": cap,
                 "estampado": desv(est, cap["estampado"]), "planchado": desv(pla, cap["planchado"]),
                 "props": props, "extra_sem6": pla[5] - cap["planchado"]}
    return R


# ---------------------------------------------------------------- impresión

def imprimir(R):
    ej = R["ej"]
    print("== Ejemplo · lista de capacidad")
    for k in ("filas_p", "filas_b"):
        for item, fl in ej[k].items():
            for f in fl:
                print(f"   {item:9} {f[0]} {f[1]:10} bruto {r3(f[2])} neto {r3(f[3])} t {f[4]} carga {r3(f[5])}")
    for p, c in ej["fac"].items():
        print("   factor", p, {k: r3(v) for k, v in c.items()}, "total", r3(sum(c.values())))
    for ct, p in ej["planes"].items():
        print(f"== Ejemplo · plan {ct}")
        for prod, v in p["cargas"].items():
            print("   ", fila(f"Carga {prod}", v))
        print("\n".join("    " + x for x in filas_plan(p)))
    print("== 9.1", [(n, fmt(x, 1)) for n, x in R["e1"]["etapas"]], "rend", fmt(R["e1"]["rend_total"], 4))
    print("== 9.2", {k: fmt(v, 1) for k, v in R["e2"].items()})
    print("== 9.3", {k: r3(v) for k, v in R["e3"]["carga"].items()}, "total", r3(R["e3"]["total"]))
    for f in R["e3"]["filas"]["Tabla"]:
        print("    ", f[0], f[1], r3(f[2]), r3(f[3]), r3(f[5]))
    print("== 9.4"); print("   ", fila("Carga", R["e4"]["total"])); print("\n".join("    " + x for x in filas_plan(R["e4"])))
    print("== 9.5", {k: r3(v) for k, v in R["e5"]["carga"].items()}, "total", r3(sum(R["e5"]["carga"].values())))
    for item, fl in R["e5"]["filas"].items():
        for f in fl:
            print("    ", item, f[0], f[1], r3(f[2]), r3(f[3]), r3(f[5]))
    for ct, p in R["e6"].items():
        print("== 9.6", ct)
        for prod, v in p["cargas"].items():
            print("   ", fila(f"Carga {prod}", v))
        print("\n".join("    " + x for x in filas_plan(p)))
    for k, p in R["e7"].items():
        print("== 9.7", k); print("\n".join("    " + x for x in filas_plan(p)))
    e8 = R["e8"]
    print("== 9.8"); print("\n".join("    " + x for x in filas_plan(e8["plan"])))
    print("    extra", e8["extra"], "sub", e8["sub"], "costos", fmt(e8["c_extra"], 0), fmt(e8["c_sub"], 0), fmt(e8["c_total"], 0))
    print("== 9.9", {k: (fmt(v, 0) if isinstance(v, (int, float)) else v) for k, v in R["e9"].items()})
    print("== 9.10", {k: (fmt(v, 3) if isinstance(v, float) else v) for k, v in R["e10"].items()})
    c = R["caso"]
    print("== caso · lotes (h est, h pla)", {p: (fmt(a), fmt(b)) for p, (a, b) in c["lote_h"].items()})
    for p, v in c["mps"].items():
        print("   MPS", p, v)
    for ct in ("estampado", "planchado"):
        print("== caso", ct); print("\n".join("    " + x for x in filas_plan(c[ct], 0)))
    print("   propuestas", c["props"], "extra sem 6", c["extra_sem6"])


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    e = []
    ej = R["ej"]
    for k in ("filas_p", "filas_b"):
        for fl in ej[k].values():
            for f in fl:
                e += [r3(f[3]), r3(f[5])]
    for c in ej["fac"].values():
        e += [r3(v) for v in c.values()]          # el total por producto no se publica: no cuadra con las partes redondeadas
    perdidas = [a - b for (_, a), (_, b) in zip(R["e1"]["etapas"], R["e1"]["etapas"][1:] + [("", E1_BUENAS)])]
    e += [f"se pierden {round(max(perdidas))} piezas"]
    for p in ej["planes"].values():
        e += [fila(f"Carga {prod}", v) for prod, v in p["cargas"].items()] + filas_plan(p)
    e += [fmt(x, 1) for _, x in R["e1"]["etapas"]] + [fmt(R["e1"]["rend_total"], 4)]
    e += [fmt(v, 1) + " h" for v in R["e2"].values()]
    e += [r3(v) for v in R["e3"]["carga"].values()] + [r3(R["e3"]["total"])]
    e += [fila("Carga", R["e4"]["total"])] + filas_plan(R["e4"])
    e += [r3(v) for v in R["e5"]["carga"].values()] + [r3(sum(R["e5"]["carga"].values()))]
    for p in R["e6"].values():
        e += [fila(f"Carga {prod}", v) for prod, v in p["cargas"].items()] + filas_plan(p)
    for p in R["e7"].values():
        e += filas_plan(p)
    e8 = R["e8"]
    e += filas_plan(e8["plan"]) + [f"${fmt(x, 0)}" for x in (e8["c_extra"], e8["c_sub"], e8["c_total"])]
    e9 = R["e9"]
    e += [f"${fmt(e9['costo'], 0)}", f"${fmt(e9['ahorro'], 0)}"]
    e10 = R["e10"]
    e += [fmt(e10["carga"], 1) + " h", fmt(e10["deficit"], 1) + " h", fmt(e10["a1_min"], 3), fmt(e10["a3_min"], 3),
          fmt(e10["botellas_llenado"], 0)]
    c = R["caso"]
    for ct in ("estampado", "planchado"):
        e += filas_plan(c[ct], 0)
    for v in c["props"].values():
        e += [fmt(v["sem5"][0], 0) + " h", fmt(v["sem5"][1], 0) + " h", fmt(v["sem6"][0], 0) + " h", fmt(v["sem6"][1], 0) + " h"]
    return e


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "09-capacidad-aproximada.md").read_text(encoding="utf-8")
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
