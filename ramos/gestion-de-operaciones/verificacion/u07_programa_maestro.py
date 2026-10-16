"""Unidad 7 · Programa maestro.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba
que cada resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto
queda sin respaldo.

    python u07_programa_maestro.py            # imprime los resultados
    python u07_programa_maestro.py --revisar  # además los busca en el .md
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


def num(x):
    """Entero si lo es; si no, con los decimales justos (máximo 3)."""
    for dec in (0, 1, 2, 3):
        if abs(round(x, dec) - x) < 1e-9:
            return fmt(x, dec)
    return fmt(x, 2)


def necesidades_brutas(plan_mensual, mezcla, semanas_mes=4):
    """NB_i = plan del mes · fracción del producto / semanas del mes."""
    return [m * mezcla / semanas_mes for m in plan_mensual for _ in range(semanas_mes)]


def corte_y_ajuste(nb, lote, inv_inicial=0, pedido_en_curso=0, varios_lotes=True):
    """Método de corte y ajuste.
    NN_i = NB_i − IE_i − PC_i. Si NN_i < 0 no se fabrica e IE_{i+1} = |NN_i|.
    Si NN_i ≥ 0 se lanza un lote (o los que hagan falta, si varios_lotes) e IE_{i+1} = MPS_i − NN_i.
    IE_1 es el inventario inicial y el pedido en curso llega en la semana 1."""
    filas, ie = [], inv_inicial
    for i, n in enumerate(nb):
        pc = pedido_en_curso if i == 0 else 0
        nn = n - ie - pc
        if nn < 0:
            mps, sig = 0, -nn
        else:
            k = max(1, ceil(nn / lote - 1e-9)) if varios_lotes else 1
            mps = k * lote
            sig = mps - nn
        filas.append({"sem": i + 1, "NB": n, "IE": ie, "PC": pc, "NN": nn, "MPS": mps})
        ie = sig
    return filas


def mps_con_dpp(inv0, lote, pron, ped, congelamiento=1, stock_seg=0):
    """Programa maestro con balance proyectado disponible (BPD) y disponible para promesa (DPP).
    Dentro del congelamiento se descuentan solo los pedidos; después, el mayor entre pronóstico y pedidos.
    Se lanza un lote (o varios) cuando el BPD caería bajo el stock de seguridad."""
    bpd, mps, disp = [], [], inv0
    for t in range(len(pron)):
        dem = ped[t] if t < congelamiento else max(pron[t], ped[t])
        q = 0
        while disp + q - dem < stock_seg:
            q += lote
        disp = disp + q - dem
        bpd.append(disp)
        mps.append(q)
    return bpd, mps, dpp(inv0, mps, ped)


def dpp(inv0, mps, ped):
    """DPP por semana: en la semana 1 y en cada semana con lote, lo disponible menos los pedidos
    hasta el próximo lote. Si sale negativo, se cubre con el DPP de semanas anteriores."""
    T = len(mps)
    claves = [t for t in range(T) if t == 0 or mps[t] > 0]
    d = [0] * T
    for j, t in enumerate(claves):
        fin = claves[j + 1] if j + 1 < len(claves) else T
        d[t] = (inv0 if t == 0 else 0) + mps[t] - sum(ped[t:fin])
    crudo = list(d)
    for j in range(len(claves) - 1, 0, -1):
        t = claves[j]
        if d[t] < 0:
            d[claves[j - 1]] += d[t]
            d[t] = 0
    acum, s = [], 0
    for x in d:
        s += x
        acum.append(s)
    return {"crudo": crudo, "dpp": d, "acum": acum}


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Ejemplo A · mermeladas: producción de julio y agosto del plan mixto de la unidad 6
EJ_A = {"plan": [6300, 6600],
        "productos": {"frutilla": {"mezcla": 0.60, "lote": 1750, "ii": 210, "pc": 0},
                      "mora": {"mezcla": 0.40, "lote": 1150, "ii": 90, "pc": 1150}}}
# Ejemplo B · mermelada de damasco, DPP con una semana de congelamiento
EJ_B = {"inv0": 640, "lote": 1000, "congel": 1,
        "pron": [520, 540, 560, 590, 570, 610, 630, 600],
        "ped": [610, 470, 380, 240, 150, 70, 30, 0]}

# 7.1 · quesería: plan de la familia (hormas) y mezcla
E1 = {"plan": [4360, 4920, 5240], "mezcla": {"gauda": 0.50, "mantecoso": 0.30, "chanco": 0.20}}
# 7.2 · molino, sacos de harina: sin inventario ni pedido en curso
E2 = {"plan": [1640, 1840], "mezcla": 1.0, "lote": 1000, "ii": 0, "pc": 0}
# 7.3 · colchones de una plaza
E3 = {"plan": [1120, 1260], "mezcla": 1.0, "lote": 600, "ii": 140, "pc": 600}
# 7.4 · DPP con el programa ya fijado (estufas compactas)
E4 = {"inv0": 85, "mps": [0, 200, 0, 200, 0, 200], "ped": [70, 95, 60, 110, 45, 30]}
# 7.5 y 7.9 · estufas a pellet: MPS con DPP
E5 = {"inv0": 150, "lote": 150, "pron": [60, 65, 70, 80, 85, 95, 100, 90, 75, 70],
      "ped": [72, 58, 49, 41, 30, 22, 15, 8, 5, 0]}
E9 = {"congel": 1, "stock_seg": 30}
# 7.6 y 7.10 · dos productos, tres meses
E6 = {"plan": [3280, 3560, 3920],
      "productos": {"P": {"mezcla": 0.55, "lote": 1000, "ii": 120, "pc": 1000},
                    "Q": {"mezcla": 0.45, "lote": 900, "ii": 440, "pc": 0}}}
E10 = {"horas_lote": {"P": 14, "Q": 11}, "capacidad": 20}
# 7.7 · necesidades mayores que el lote
E7 = {"plan": [3040, 3400], "mezcla": 1.0, "lote": 500, "ii": 300, "pc": 0}
# 7.8 · DPP con préstamo
E8 = {"inv0": 40, "mps": [0, 120, 0, 120, 120, 0], "ped": [35, 60, 55, 90, 135, 15]}

# Caso integrador: pedidos ya comprometidos de poleras básicas (para el DPP)
CASO_PEDIDOS = {"poleras básicas": [540, 610, 480, 300, 150, 80, 0, 0]}


# ---------------------------------------------------------------- 7.10 · nivelar la carga

def nivelar(mps_por_producto, horas_lote, lotes, cap):
    """Adelanta lotes de semanas sobrecargadas a la semana previa más cercana con holgura.
    Devuelve la carga original, la nivelada y las unidades·semana de inventario extra."""
    T = len(next(iter(mps_por_producto.values())))
    plan = {p: list(v) for p, v in mps_por_producto.items()}
    carga = lambda: [sum(plan[p][t] / lotes[p] * horas_lote[p] for p in plan) for t in range(T)]
    original = carga()
    movidos, extra = [], 0
    for t in range(T):
        while carga()[t] > cap:
            # se adelanta el lote más chico en horas que quepa antes
            opciones = sorted((horas_lote[p], p) for p in plan if plan[p][t] > 0)
            hecho = False
            for h, p in opciones:
                for s in range(t - 1, -1, -1):
                    if carga()[s] + h <= cap:
                        plan[p][t] -= lotes[p]
                        plan[p][s] += lotes[p]
                        movidos.append((p, t + 1, s + 1))
                        extra += lotes[p] * (t - s)
                        hecho = True
                        break
                if hecho:
                    break
            if not hecho:
                raise RuntimeError("no hay holgura antes de la semana sobrecargada")
    return original, carga(), movidos, extra, plan


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    R["ejA"] = {p: corte_y_ajuste(necesidades_brutas(EJ_A["plan"], d["mezcla"]), d["lote"], d["ii"], d["pc"])
                for p, d in EJ_A["productos"].items()}
    R["ejB"] = mps_con_dpp(EJ_B["inv0"], EJ_B["lote"], EJ_B["pron"], EJ_B["ped"], EJ_B["congel"])

    R["e1"] = {p: [m * f / 4 for m in E1["plan"]] for p, f in E1["mezcla"].items()}
    R["e2"] = corte_y_ajuste(necesidades_brutas(E2["plan"], 1), E2["lote"], E2["ii"], E2["pc"])
    R["e3"] = corte_y_ajuste(necesidades_brutas(E3["plan"], 1), E3["lote"], E3["ii"], E3["pc"])
    R["e4"] = dpp(E4["inv0"], E4["mps"], E4["ped"])
    R["e5"] = mps_con_dpp(E5["inv0"], 150, E5["pron"], E5["ped"], 1)
    R["e9"] = mps_con_dpp(E5["inv0"], 150, E5["pron"], E5["ped"], E9["congel"], E9["stock_seg"])
    ss = E9["stock_seg"]  # menor stock de seguridad que vuelve a mover algún lote
    while mps_con_dpp(E5["inv0"], 150, E5["pron"], E5["ped"], 1, ss)[1] == R["e9"][1]:
        ss += 1
    R["e9_umbral"] = (ss, mps_con_dpp(E5["inv0"], 150, E5["pron"], E5["ped"], 1, ss))
    R["e6"] = {p: corte_y_ajuste(necesidades_brutas(E6["plan"], d["mezcla"]), d["lote"], d["ii"], d["pc"])
               for p, d in E6["productos"].items()}
    nb7 = necesidades_brutas(E7["plan"], 1)
    R["e7_un_lote"] = corte_y_ajuste(nb7, E7["lote"], E7["ii"], E7["pc"], varios_lotes=False)
    R["e7"] = corte_y_ajuste(nb7, E7["lote"], E7["ii"], E7["pc"])
    R["e8"] = dpp(E8["inv0"], E8["mps"], E8["ped"])
    lotes6 = {p: d["lote"] for p, d in E6["productos"].items()}
    R["e10"] = nivelar({p: [f["MPS"] for f in R["e6"][p]] for p in R["e6"]}, E10["horas_lote"], lotes6,
                       E10["capacidad"])

    # Caso integrador: se recalcula con la función de esta unidad y se compara con caso_estampa_sur.py
    C = caso.calcular()
    meses = [C["u6"]["plan"][0]["produccion"], C["u6"]["plan"][1]["produccion"]]
    propio = {p: corte_y_ajuste(necesidades_brutas(meses, d["mezcla"]), d["lote"],
                                caso.U7["inventario_inicial"][p], caso.U7["pedido_en_curso"][p])
              for p, d in caso.PRODUCTOS.items()}
    for p in propio:
        for a, b in zip(propio[p], C["u7"][p]):
            assert a["MPS"] == b["MPS"] and abs(a["NN"] - b["NN"]) < 1e-9, f"no calza el caso en {p}"
    assert all(C["u7"][p][5]["MPS"] > 0 for p in caso.PRODUCTOS), "la semana 6 no tiene un lote de cada producto"
    pb = [f["MPS"] for f in C["u7"]["poleras básicas"]]
    ii_pb = caso.U7["inventario_inicial"]["poleras básicas"] + caso.U7["pedido_en_curso"]["poleras básicas"]
    R["caso"] = {"C": C, "meses": meses, "dpp": dpp(ii_pb, pb, CASO_PEDIDOS["poleras básicas"]),
                 "totales": {p: sum(f["MPS"] for f in C["u7"][p]) for p in caso.PRODUCTOS},
                 "por_semana": [sum(C["u7"][p][s]["MPS"] for p in caso.PRODUCTOS) for s in range(8)],
                 "inv_final": {p: C["u7"][p][-1]["MPS"] - C["u7"][p][-1]["NN"] if C["u7"][p][-1]["NN"] >= 0
                               else -C["u7"][p][-1]["NN"] for p in caso.PRODUCTOS}}
    return R


# ---------------------------------------------------------------- impresión

def tabla(filas):
    for k in ("NB", "IE", "PC", "NN", "MPS"):
        print(f"   {k:4}", " | ".join(num(f[k]) for f in filas))


def imprimir(R):
    for p, f in R["ejA"].items():
        print("== Ejemplo A ·", p)
        tabla(f)
    bpd, mps, d = R["ejB"]
    print("== Ejemplo B · BPD", bpd, "MPS", mps)
    print("   DPP", d)
    print("== 7.1", {p: [num(x) for x in v] for p, v in R["e1"].items()})
    for k in ("e2", "e3", "e7_un_lote", "e7"):
        print("==", k)
        tabla(R[k])
    print("== 7.4", R["e4"])
    for k in ("e5", "e9"):
        bpd, mps, d = R[k]
        print("==", k, "BPD", bpd, "suma", sum(bpd), "MPS", mps, "lotes", sum(1 for x in mps if x), "\n   DPP", d)
    for p, f in R["e6"].items():
        print("== 7.6 ·", p)
        tabla(f)
        print("   por mes:", [sum(x["MPS"] for x in f[m * 4:(m + 1) * 4]) for m in range(3)])
    print("== 7.8", R["e8"])
    orig, niv, mov, extra, plan = R["e10"]
    print("== 7.10 carga", [num(x) for x in orig], "→", [num(x) for x in niv], "movidos", mov, "extra", extra)
    print("   ", plan)
    cs = R["caso"]
    C = cs["C"]
    print("== Caso · meses", cs["meses"])
    for p, filas in C["u7"].items():
        print("  ", p)
        tabla(filas)
    print("   totales", cs["totales"], "por semana", cs["por_semana"], "inv final", cs["inv_final"])
    print("   DPP poleras básicas", cs["dpp"])


# ---------------------------------------------------------------- revisión contra el texto

def filas_md(filas):
    """Las filas NN e IE y MPS como se escriben en las tablas del .md."""
    return [" | ".join(num(f[k]) for f in filas) for k in ("IE", "NN", "MPS")]


def esperados(R):
    e = []
    tot_a = 0
    for p, f in R["ejA"].items():
        e += filas_md(f)
        ult = f[-1]
        e += [fmt(sum(x["MPS"] for x in f)), fmt(ult["MPS"] - ult["NN"] if ult["NN"] >= 0 else -ult["NN"])]
        tot_a += sum(x["MPS"] for x in f)
    e += [fmt(tot_a), fmt(sum(EJ_A["plan"]))]
    bpd, mps, d = R["ejB"]
    e += [" | ".join(num(x) for x in bpd), " | ".join(num(x) for x in d["acum"])]
    e += [num(x) for x in d["dpp"] if x]
    for v in R["e1"].values():
        e += [num(x) for x in v]
    for k in ("e2", "e3", "e7"):
        e += filas_md(R[k])
    e += [" | ".join(num(f["IE"]) for f in R["e7_un_lote"])]
    e += [" | ".join(num(x) for x in R["e4"]["dpp"]), " | ".join(num(x) for x in R["e4"]["acum"])]
    for k in ("e5", "e9"):
        bpd, mps, d = R[k]
        e += [" | ".join(num(x) for x in bpd), " | ".join(num(x) for x in mps),
              " | ".join(num(x) for x in d["dpp"]), " | ".join(num(x) for x in d["acum"])]
    s5, s9 = sum(R["e5"][0]), sum(R["e9"][0])
    umbral, (bpd_u, mps_u, _) = R["e9_umbral"]
    e += [f"{fmt(s5)} unidades-semana", f"{fmt(s9)} unidades-semana", f"{fmt(s9 - s5)} unidades-semana",
          f"stock de seguridad de {umbral}", " | ".join(num(x) for x in mps_u)]
    for p, f in R["e6"].items():
        e += filas_md(f)
        e += [" · ".join(fmt(sum(x["MPS"] for x in f[m * 4:(m + 1) * 4])) for m in range(3))]
        e += [", ".join(fmt(pm * E6["productos"][p]["mezcla"]) for pm in E6["plan"][:2])]
    e += [" | ".join(num(x) for x in R["e8"]["crudo"]), " | ".join(num(x) for x in R["e8"]["dpp"]),
          " | ".join(num(x) for x in R["e8"]["acum"])]
    orig, niv, mov, extra, plan = R["e10"]
    e += [" | ".join(num(x) for x in orig), " | ".join(num(x) for x in niv), f"{fmt(extra)} unidades-semana"]
    cs = R["caso"]
    for filas in cs["C"]["u7"].values():
        e += filas_md(filas)
    e += [" | ".join(num(x) for x in cs["por_semana"])]
    e += [" | ".join(num(x) for x in cs["dpp"]["crudo"]), " | ".join(num(x) for x in cs["dpp"]["dpp"]),
          " | ".join(num(x) for x in cs["dpp"]["acum"])]
    e += [fmt(v) for v in cs["totales"].values()]
    e += [f"{fmt(cs['C']['u9'][5]['estampado_h'])} horas de estampado", fmt(cs["por_semana"][5])]
    inv = caso.U7["inventario_inicial"]
    assert sum(inv.values()) == caso.U6["inventario_inicial"], "el inventario del MPS no calza con el del plan"
    e += [" + ".join(fmt(v) for v in inv.values()) + f" = {fmt(sum(inv.values()))}",
          f"{fmt(cs['meses'][0])} prendas en el mes 1 y {fmt(cs['meses'][1])} en el mes 2"]
    return [x for x in e if x]


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "07-programa-maestro.md").read_text(encoding="utf-8")
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
