"""Unidad 11 · Física de la fábrica.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba
que cada resultado aparezca escrito tal cual en el .md. Las tablas de eventos de las
simulaciones salen de acá (con los números aleatorios fijos que trae el enunciado).

    python u11_fisica_fabrica.py            # imprime los resultados y las tablas de eventos
    python u11_fisica_fabrica.py --revisar  # además los busca en el .md
"""
from math import sqrt
from pathlib import Path
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


def little(wip=None, th=None, ct=None):
    """WIP = TH × CT: entrega la que falta."""
    if wip is None:
        return th * ct
    if th is None:
        return wip / ct
    return wip / th


def casos_linea(tiempos, w):
    """Mejor caso, peor caso y peor caso práctico (Hopp y Spearman) para una línea de estaciones
    simples con tiempos `tiempos` (horas) y w trabajos en la línea. Devuelve {caso: (TH, CT)}."""
    t0 = sum(tiempos)
    rb = 1 / max(tiempos)
    w0 = rb * t0
    mejor = (w / t0, t0) if w <= w0 else (rb, w / rb)
    peor = (1 / t0, w * t0)
    pwc = (w / (w0 + w - 1) * rb, t0 + (w - 1) / rb)
    return {"rb": rb, "T0": t0, "W0": w0, "mejor": mejor, "peor": peor, "pwc": pwc}


def kingman(ca, ce, u, te):
    """Tiempo en cola aproximado (VUT): V · U · T."""
    return (ca ** 2 + ce ** 2) / 2 * (u / (1 - u)) * te


def salida_cv2(u, ca, ce):
    """Ecuación de enlace: variabilidad de las salidas de una estación de un servidor."""
    return u ** 2 * ce ** 2 + (1 - u ** 2) * ca ** 2


def cv_distribucion(dist):
    """dist: {valor: probabilidad} → media, desviación estándar, coeficiente de variación."""
    m = sum(v * p for v, p in dist.items())
    var = sum(p * (v - m) ** 2 for v, p in dist.items())
    return m, sqrt(var), sqrt(var) / m


def montecarlo(dist, aleatorios):
    """Convierte números aleatorios de dos dígitos (00-99) en valores, con intervalos acumulados."""
    tramos, acum = [], 0
    for v, p in dist.items():
        lo = round(acum * 100)
        acum += p
        tramos.append((lo, round(acum * 100) - 1, v))
    salida = []
    for r in aleatorios:
        salida.append(next(v for lo, hi, v in tramos if lo <= r <= hi))
    return tramos, salida


def simular(entre_llegadas, servicios):
    """Fila de un servidor, FCFS, avance al próximo evento. Si coinciden una salida y una llegada,
    se procesa primero la salida. El reloj parte en 0 y termina con la última salida."""
    llegadas, t = [], 0
    for x in entre_llegadas:
        t += x
        llegadas.append(t)
    n = len(llegadas)
    eventos = [(llegadas[i], 1, i) for i in range(n)]       # 1 = llegada
    cola, ocupado, fin_servicio = [], None, None
    filas, esperas, inicio = [], [0] * n, [0] * n
    atendidos, reloj_prev, area_cola, tiempo_en = 0, 0, 0, {}
    pendientes = sorted(eventos)
    while pendientes or ocupado is not None:
        prox_llegada = pendientes[0][0] if pendientes else None
        if ocupado is not None and (prox_llegada is None or fin_servicio <= prox_llegada):
            ahora, tipo = fin_servicio, "sale"
        else:
            ahora, tipo = prox_llegada, "llega"
        dt = ahora - reloj_prev
        area_cola += len(cola) * dt
        tiempo_en[len(cola)] = tiempo_en.get(len(cola), 0) + dt
        reloj_prev = ahora
        entra = None
        if tipo == "sale":
            atendidos += 1
            evento = f"Sale C{ocupado + 1}"
            ocupado = None
            if cola:
                j = cola.pop(0)
                ocupado, inicio[j] = j, ahora
                esperas[j] = ahora - llegadas[j]
                fin_servicio = ahora + servicios[j]
                entra = (j, esperas[j])
        else:
            _, _, i = pendientes.pop(0)
            evento = f"Llega C{i + 1}"
            if ocupado is None:
                ocupado, inicio[i] = i, ahora
                fin_servicio = ahora + servicios[i]
                entra = (i, 0)
            else:
                cola.append(i)
        filas.append((ahora, evento, 0 if ocupado is None else 1, len(cola), entra, atendidos))
    T = reloj_prev
    total_serv = sum(servicios)
    est = {
        "llegadas": llegadas, "inicio": inicio, "fin": [inicio[i] + servicios[i] for i in range(n)],
        "esperas": esperas, "T": T, "u": total_serv / T, "Wq": sum(esperas) / n, "Wq_max": max(esperas),
        "en_espera": sum(e > 0 for e in esperas), "P": {k: v / T for k, v in sorted(tiempo_en.items())},
        "Lq": area_cola / T, "lam": n / T, "W": (sum(esperas) + total_serv) / n,
        "L": (sum(esperas) + total_serv) / T,
    }
    est["little_q"] = est["lam"] * est["Wq"]
    return filas, est


def tabla_eventos(filas):
    """La tabla de eventos en Markdown, como va en el .md."""
    lin = ["| Reloj | Evento | Servidor | En cola | Entra a atención (esperó) | Atendidos |",
           "|---|---|---|---|---|---|"]
    for ahora, ev, srv, cola, entra, at in filas:
        e = f"C{entra[0] + 1} ({entra[1]})" if entra else "—"
        lin.append(f"| {ahora} | {ev} | {srv} | {cola} | {e} | {at} |")
    return "\n".join(lin)


def flow_shop_liberado(seq, tiempos):
    """Dos máquinas en serie; todas las órdenes liberadas en t = 0. Devuelve por orden:
    (inicio M1, fin M1, inicio M2, fin M2)."""
    libre1 = libre2 = 0
    filas = {}
    for o in seq:
        a, b = tiempos[o]
        i1, f1 = libre1, libre1 + a
        i2 = max(f1, libre2)
        f2 = i2 + b
        libre1, libre2 = f1, f2
        filas[o] = (i1, f1, i2, f2)
    return filas


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Sección 3 · línea de sillas: corte, armado, lijado y barnizado (minutos, una estación cada una)
SILLAS = [20, 30, 25, 15]
SILLAS_W = 6
# Sección 4 · utilizaciones para la tabla de congestión
UTILS = [0.5, 0.8, 0.9, 0.95]

# Ejemplo resuelto · mesón de despacho de una ferretería (minutos)
EJ_LLEGADA = {1: 0.10, 2: 0.20, 3: 0.30, 4: 0.25, 5: 0.15}
EJ_SERVICIO = {1: 0.15, 2: 0.30, 3: 0.35, 4: 0.20}
EJ_ALEAT_LLEGADA = [47, 8, 21, 83, 5, 66, 92, 31]
EJ_ALEAT_SERVICIO = [71, 88, 54, 19, 93, 37, 60, 8]

# 11.1 · packing de arándanos: TH (cajas/h), WIP (cajas), meta de CT (h)
E1 = dict(th=450, wip=1_350, ct_meta=2)
# 11.2 · oficina municipal de licencias: personas adentro, minutos adentro, personas en espera, horas
E2 = dict(L=18, W_min=45, Lq=12, horas=8)
# 11.3 · una máquina con te = 12 min y llegadas por hora
E3_TE, E3_LLEGADAS = 12, [3, 4, 4.5, 4.8]
# 11.4 · coeficientes de variación (media, desviación) en minutos
E4 = {"Torno": (10, 4), "Soldadura": (20, 18), "Pintura": (15, 24)}
# 11.5 · simulación con tiempos dados (minutos)
E5_ENTRE = [3, 5, 1, 2, 6, 2]
E5_SERV = [4, 6, 3, 5, 2, 4]
# 11.6 · centro de mecanizado: ta, te (min), ca, ce; variantes
E6 = dict(ta=12, te=10, ca=1.0, ce=0.5, ce_falla=1.5, te_mejor=9)
# 11.7 · línea de tres estaciones (min), WIP a evaluar, TH observado con w = 10 (por hora)
E7 = [12, 20, 16]
E7_W = [2, 5, 10]
E7_TH_OBS = 2.1
# 11.8 · línea de tres etapas: WIP por etapa (unidades) y TH (unidades/h); meta de CT (h)
E8_WIP = {"Picado": 60, "Embutido": 120, "Empaque": 20}
E8_TH, E8_META = 40, 3
# 11.9 · romana de camiones de un packing (minutos)
E9_LLEGADA = {4: 0.15, 6: 0.25, 8: 0.35, 10: 0.25}
E9_SERVICIO = {5: 0.30, 7: 0.45, 9: 0.25}
E9_ALEAT_LLEGADA = [58, 3, 91, 27, 44, 76, 15, 62, 89, 35]
E9_ALEAT_SERVICIO = [22, 67, 81, 49, 5, 93, 38, 71, 56, 14]
# 11.10 · dos estaciones en serie (minutos)
E10 = dict(ta=10, ca=1.0, te1=8, ce1=1.2, te2=9, ce2=0.6, ce1_mejor=0.6, te2_mejor=8)

# Caso integrador · semana 6 de Estampa Sur (sale de la sección 11 de la unidad 10)
CASO = {
    "OP-61": (6, 4), "OP-62": (9, 5), "OP-63": (11, 3), "OP-64": (3, 6), "OP-65": (4, 2),
}  # (estampado h, planchado h)
CASO_SEQ = {"Johnson": ["OP-64", "OP-62", "OP-61", "OP-63", "OP-65"],
            "EDD": ["OP-64", "OP-61", "OP-63", "OP-62", "OP-65"]}
CASO_PLANCHADO_DISPONIBLE = 18     # h por semana (unidad 9: una persona media jornada)


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # sección 3
    s = casos_linea([t / 60 for t in SILLAS], SILLAS_W)
    R["sillas"] = s
    R["congestion"] = {u: u / (1 - u) for u in UTILS}

    # ejemplo
    tr_a, ea = montecarlo(EJ_LLEGADA, EJ_ALEAT_LLEGADA)
    tr_s, es = montecarlo(EJ_SERVICIO, EJ_ALEAT_SERVICIO)
    filas, est = simular(ea, es)
    ma, sa, ca = cv_distribucion(EJ_LLEGADA)
    me, se, ce = cv_distribucion(EJ_SERVICIO)
    u = me / ma
    wq = kingman(ca, ce, u, me)
    R["ej"] = dict(tramos_a=tr_a, tramos_s=tr_s, entre=ea, serv=es, filas=filas, est=est,
                   ma=ma, sa=sa, ca=ca, me=me, se=se, ce=ce, u=u, wq_k=wq, lq_k=wq / ma)

    # 11.1
    ct = little(wip=E1["wip"], th=E1["th"])
    R["e1"] = dict(ct=ct, wip_meta=little(th=E1["th"], ct=E1["ct_meta"]))
    # 11.2
    W = E2["W_min"] / 60
    th = little(wip=E2["L"], ct=W)
    wq = E2["Lq"] / th
    R["e2"] = dict(th=th, dia=th * E2["horas"], wq_min=wq * 60, serv_min=E2["W_min"] - wq * 60,
                   en_atencion=E2["L"] - E2["Lq"])
    # 11.3
    R["e3"] = []
    for lam in E3_LLEGADAS:
        u3 = lam * E3_TE / 60
        R["e3"].append((lam, u3, u3 / (1 - u3), kingman(1, 1, u3, E3_TE)))
    # 11.4
    R["e4"] = {k: (sd / m, (sd / m) ** 2) for k, (m, sd) in E4.items()}
    # 11.5
    f5, s5 = simular(E5_ENTRE, E5_SERV)
    R["e5"] = dict(filas=f5, est=s5)
    # 11.6
    e = E6
    u6 = e["te"] / e["ta"]
    base = kingman(e["ca"], e["ce"], u6, e["te"])
    falla = kingman(e["ca"], e["ce_falla"], u6, e["te"])
    u6b = e["te_mejor"] / e["ta"]
    rapido = kingman(e["ca"], e["ce"], u6b, e["te_mejor"])
    def ct_wip(cq, te):
        ct = cq + te
        return ct, ct / e["ta"]
    R["e6"] = dict(u=u6, V=(e["ca"] ** 2 + e["ce"] ** 2) / 2, U=u6 / (1 - u6), cq=base,
                   ct=ct_wip(base, e["te"])[0], wip=ct_wip(base, e["te"])[1],
                   cq_falla=falla, ct_falla=ct_wip(falla, e["te"])[0], wip_falla=ct_wip(falla, e["te"])[1],
                   V_falla=(e["ca"] ** 2 + e["ce_falla"] ** 2) / 2,
                   u_b=u6b, U_b=u6b / (1 - u6b), cq_rapido=rapido, ct_rapido=ct_wip(rapido, e["te_mejor"])[0],
                   wip_rapido=ct_wip(rapido, e["te_mejor"])[1], baja_cola=1 - rapido / base)
    # 11.7
    R["e7"] = {w: casos_linea([t / 60 for t in E7], w) for w in E7_W}
    R["e7_obs_ct"] = 10 / E7_TH_OBS
    # 11.8
    R["e8"] = dict(ct={k: v / E8_TH for k, v in E8_WIP.items()}, total=sum(E8_WIP.values()) / E8_TH,
                   wip_meta=E8_TH * E8_META, wip_total=sum(E8_WIP.values()))
    # 11.9
    tr9a, ea9 = montecarlo(E9_LLEGADA, E9_ALEAT_LLEGADA)
    tr9s, es9 = montecarlo(E9_SERVICIO, E9_ALEAT_SERVICIO)
    f9, s9 = simular(ea9, es9)
    ma9, sa9, ca9 = cv_distribucion(E9_LLEGADA)
    me9, se9, ce9 = cv_distribucion(E9_SERVICIO)
    u9 = me9 / ma9
    R["e9"] = dict(tramos_a=tr9a, tramos_s=tr9s, entre=ea9, serv=es9, filas=f9, est=s9, ma=ma9, ca=ca9,
                   me=me9, ce=ce9, u=u9, wq_k=kingman(ca9, ce9, u9, me9))
    # 11.10
    e = E10
    def linea2(ce1, te2):
        u1, u2 = e["te1"] / e["ta"], te2 / e["ta"]
        q1 = kingman(e["ca"], ce1, u1, e["te1"])
        cd2 = salida_cv2(u1, e["ca"], ce1)
        q2 = kingman(sqrt(cd2), e["ce2"], u2, te2)
        ct = q1 + e["te1"] + q2 + te2
        return dict(u1=u1, u2=u2, q1=q1, cd2=cd2, q2=q2, ct=ct, wip=ct / e["ta"])
    R["e10"] = {"base": linea2(e["ce1"], e["te2"]), "A": linea2(e["ce1_mejor"], e["te2"]),
                "B": linea2(e["ce1"], e["te2_mejor"])}

    # caso
    caso = {}
    for regla, seq in CASO_SEQ.items():
        f = flow_shop_liberado(seq, CASO)
        M = max(v[3] for v in f.values())
        C = {o: v[3] for o, v in f.items()}
        espera_pl = {o: v[2] - v[1] for o, v in f.items()}
        ct_desde_inicio = {o: v[3] - v[0] for o, v in f.items()}
        espera_est = {o: v[0] for o, v in f.items()}          # liberadas en t = 0
        n = len(seq)
        caso[regla] = dict(filas=f, M=M, C=C, ct=sum(C.values()) / n, th=n / M, wip=sum(C.values()) / M,
                           espera_est=espera_est, esp_est_prom=sum(espera_est.values()) / n,
                           cola_est=sum(espera_est.values()) / M,
                           espera_pl=espera_pl, esp_prom=sum(espera_pl.values()) / n,
                           cola_pl=sum(espera_pl.values()) / M,
                           ct2=sum(ct_desde_inicio.values()) / n, wip2=sum(ct_desde_inicio.values()) / M,
                           u_est=sum(a for a, _ in CASO.values()) / M, u_pl=sum(b for _, b in CASO.values()) / M)
        assert abs(caso[regla]["wip"] - caso[regla]["th"] * caso[regla]["ct"]) < 1e-12
    R["caso"] = caso
    R["caso_u_pl_sem"] = sum(b for _, b in CASO.values()) / CASO_PLANCHADO_DISPONIBLE
    return R


def imprimir(R):
    s = R["sillas"]
    print("== Sección 3 · sillas", {k: (tuple(round(x, 3) for x in v) if isinstance(v, tuple) else round(v, 3)) for k, v in s.items()})
    print("== Congestión", {u: round(v, 2) for u, v in R["congestion"].items()})
    ej = R["ej"]
    print("== Ejemplo · tramos llegada", ej["tramos_a"], "servicio", ej["tramos_s"])
    print("   entre llegadas", ej["entre"], "servicios", ej["serv"])
    print(tabla_eventos(ej["filas"]))
    print("  ", {k: v for k, v in ej["est"].items()})
    print("   ta", ej["ma"], "sa", round(ej["sa"], 3), "ca", round(ej["ca"], 3), "te", ej["me"], "se", round(ej["se"], 3),
          "ce", round(ej["ce"], 3), "u", round(ej["u"], 4), "Wq Kingman", round(ej["wq_k"], 2), "Lq", round(ej["lq_k"], 2))
    print("== 11.1", R["e1"])
    print("== 11.2", R["e2"])
    print("== 11.3", [(l, round(u, 2), round(f, 2), round(q, 1)) for l, u, f, q in R["e3"]])
    print("== 11.4", {k: (round(c, 2), round(c2, 2)) for k, (c, c2) in R["e4"].items()})
    print("== 11.5"); print(tabla_eventos(R["e5"]["filas"])); print("  ", R["e5"]["est"])
    print("== 11.6", {k: round(v, 3) for k, v in R["e6"].items()})
    for w, c in R["e7"].items():
        print("== 11.7 w =", w, {k: (tuple(round(x, 3) for x in v) if isinstance(v, tuple) else round(v, 3)) for k, v in c.items()})
    print("   CT observado", round(R["e7_obs_ct"], 3))
    print("== 11.8", R["e8"])
    e9 = R["e9"]
    print("== 11.9 tramos", e9["tramos_a"], e9["tramos_s"], "entre", e9["entre"], "serv", e9["serv"])
    print(tabla_eventos(e9["filas"])); print("  ", e9["est"])
    print("   ta", e9["ma"], "ca", round(e9["ca"], 3), "te", e9["me"], "ce", round(e9["ce"], 3), "u", round(e9["u"], 4), "Wq K", round(e9["wq_k"], 2))
    for k, v in R["e10"].items():
        print("== 11.10", k, {a: round(b, 3) for a, b in v.items()})
    for regla, c in R["caso"].items():
        print(f"== caso {regla}: M {c['M']} C {c['C']} CT {c['ct']} TH {round(c['th'], 4)} WIP {round(c['wip'], 3)}")
        print("    filas", c["filas"])
        print("    espera estampado", c["espera_est"], "prom", c["esp_est_prom"], "cola", round(c["cola_est"], 3))
        print("    espera planchado", c["espera_pl"], "prom", c["esp_prom"], "cola", round(c["cola_pl"], 3),
              "| liberando al iniciar: CT", c["ct2"], "WIP", round(c["wip2"], 3), "| u est", round(c["u_est"], 3), "u pl", round(c["u_pl"], 3))
    print("   planchado contra 18 h:", round(R["caso_u_pl_sem"], 4))


# ---------------------------------------------------------------- revisión contra el texto

def como_se_lee(md):
    """Deja las fórmulas como se ven impresas: 74{,}9\\ \\% → 74,9 %, \\text{ h} → h, sin los $."""
    md = re.sub(r"\\text\{([^}]*)\}", r"\1", md)
    md = re.sub(r"\{(\d[\d.]*)\}", r"\1", md)
    return md.replace("{,}", ",").replace("\\ \\%", " %").replace("\\%", "%").replace("$", "")


def esperados(R, md_crudo):
    e = []
    s = R["sillas"]
    e += [fmt(s["T0"]) + " h", fmt(s["W0"], 0) + " sillas"]
    for caso in ("mejor", "peor", "pwc"):
        th, ct = s[caso]
        e += [fmt(th, 2) + " sillas/h", fmt(ct) + " h"]
    e += [fmt(v, 0) if abs(v - round(v)) < 1e-9 else fmt(v) for v in R["congestion"].values()]
    ej = R["ej"]; st = ej["est"]
    e += [pct(st["u"]), fmt(st["Wq"]) + " min", f"{st['Wq_max']} min", fmt(st["Lq"], 2), fmt(st["lam"], 3),
          fmt(st["little_q"], 2), f"{st['T']} min", fmt(ej["ma"], 2) + " min", fmt(ej["me"], 1) + " min",
          fmt(ej["ca"], 2), fmt(ej["ce"], 2), pct(ej["u"]), fmt(ej["wq_k"]) + " min", fmt(ej["lq_k"], 2)]
    e += [pct(p) for p in st["P"].values()]
    e += [fmt((ej["ca"] ** 2 + ej["ce"] ** 2) / 2, 2), fmt(ej["u"] / (1 - ej["u"]), 2), fmt(ej["sa"], 2), fmt(ej["se"], 2),
          f"{st['en_espera']} de los 8 clientes", fmt(st["Wq"], 3)]
    e1 = R["e1"]; e += [fmt(e1["ct"], 0) + " h", fmt(e1["wip_meta"], 0) + " cajas"]
    e2 = R["e2"]; e += [fmt(e2["th"], 0) + " personas/h", fmt(e2["dia"], 0) + " personas", fmt(e2["wq_min"], 0) + " min",
                        fmt(e2["serv_min"], 0) + " min"]
    for lam, u, f, q in R["e3"]:
        e += [pct(u, 0), fmt(f), fmt(q, 0) + " min"]
    for c, c2 in R["e4"].values():
        e += [fmt(c, 2), fmt(c2, 2)]
    st5 = R["e5"]["est"]
    e += [pct(st5["u"]), fmt(st5["Wq"]) + " min", f"{st5['Wq_max']} min", fmt(st5["Lq"], 2), fmt(st5["little_q"], 2)]
    e += [pct(p) for p in st5["P"].values()]
    e6 = R["e6"]
    e += [fmt(e6["u"], 3), fmt(e6["V"], 3), fmt(e6["U"], 0), fmt(e6["cq"], 2) + " min", fmt(e6["ct"], 2) + " min",
          fmt(e6["wip"], 2) + " piezas", fmt(e6["V_falla"], 3), fmt(e6["cq_falla"], 2) + " min", fmt(e6["ct_falla"], 2) + " min",
          fmt(e6["wip_falla"], 2) + " piezas", fmt(e6["U_b"], 0), fmt(e6["cq_rapido"], 2) + " min", fmt(e6["ct_rapido"], 2) + " min",
          fmt(e6["wip_rapido"], 2) + " piezas", pct(e6["baja_cola"], 0)]
    for w, c in R["e7"].items():
        for caso in ("mejor", "peor", "pwc"):
            th, ct = c[caso]
            e += [fmt(th, 2), fmt(ct, 2)]
    e += [fmt(R["e7"][2]["W0"], 1), fmt(R["e7_obs_ct"], 2) + " h"]
    e8 = R["e8"]; e += [fmt(v) + " h" for v in e8["ct"].values()] + [fmt(e8["total"], 0) + " h", fmt(e8["wip_meta"], 0) + " unidades"]
    e9 = R["e9"]; st9 = e9["est"]
    e += [pct(st9["u"]), fmt(st9["Wq"]) + " min", f"{st9['Wq_max']} min", fmt(st9["Lq"], 2), fmt(st9["little_q"], 2),
          f"{st9['T']} min", fmt(e9["ma"], 1) + " min", fmt(e9["me"], 1) + " min", fmt(e9["ca"], 2), fmt(e9["ce"], 2),
          pct(e9["u"]), fmt(e9["wq_k"]) + " min"]
    for k, v in R["e10"].items():
        e += [fmt(v["q1"], 2), fmt(v["q2"], 2), fmt(v["ct"], 2) + " min", fmt(v["wip"], 2)]
    e += [fmt(R["e10"]["base"]["cd2"], 4), fmt(R["e10"]["A"]["cd2"], 4)]
    for regla, c in R["caso"].items():
        e += [f"{c['M']} h", fmt(c["ct"]) + " h", fmt(c["th"], 3), fmt(c["wip"], 2), fmt(c["esp_prom"]) + " h",
              fmt(c["cola_pl"], 2), fmt(c["ct2"]) + " h", fmt(c["wip2"], 2), pct(c["u_est"]), pct(c["u_pl"]),
              fmt(c["esp_est_prom"]) + " h", fmt(c["cola_est"], 2)]
    e += [fmt(R["caso_u_pl_sem"], 2)]
    # las tablas de eventos tienen que estar copiadas tal cual
    faltan_tablas = [n for n, f in (("ejemplo", ej["filas"]), ("11.5", R["e5"]["filas"]), ("11.9", e9["filas"]))
                     if tabla_eventos(f) not in md_crudo]
    return e, faltan_tablas


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if "--revisar" in sys.argv:
        crudo = (AQUI.parent / "unidades" / "11-fisica-de-la-fabrica.md").read_text(encoding="utf-8")
        md = como_se_lee(crudo)
        cadenas, tablas = esperados(R, crudo)
        faltan = [x for x in cadenas if x not in md] + [f"tabla de eventos {t}" for t in tablas]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
