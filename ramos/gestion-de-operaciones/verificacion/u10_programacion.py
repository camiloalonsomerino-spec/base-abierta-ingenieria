"""Unidad 10 · Programación de operaciones.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba
que cada resultado aparezca escrito tal cual en el .md. Así ninguna cifra del texto
queda sin respaldo.

    python u10_programacion.py            # imprime los resultados
    python u10_programacion.py --revisar  # además los busca en el .md
"""
from itertools import permutations
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- herramientas

def fmt(x, dec=1):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"


def evaluar(seq, trabajos):
    """Secuencia en una máquina → filas y los indicadores de Heizer."""
    t, filas = 0, []
    for j in seq:
        p, d = trabajos[j]
        t += p
        filas.append((j, p, t, d, max(0, t - d)))
    n = len(seq)
    suma_p = sum(f[1] for f in filas)
    suma_f = sum(f[2] for f in filas)
    atrasos = [f[4] for f in filas]
    return {
        "filas": filas,
        "flujo_total": suma_f,
        "flujo_prom": suma_f / n,
        "utilizacion": suma_p / suma_f,
        "en_sistema": suma_f / suma_p,
        "atraso_prom": sum(atrasos) / n,
        "atraso_max": max(atrasos),
        "atrasados": sum(a > 0 for a in atrasos),
    }


def reglas_estaticas(trabajos, orden_llegada):
    return {
        "FCFS": list(orden_llegada),
        "SPT": sorted(orden_llegada, key=lambda j: (trabajos[j][0], orden_llegada.index(j))),
        "EDD": sorted(orden_llegada, key=lambda j: (trabajos[j][1], orden_llegada.index(j))),
        "LPT": sorted(orden_llegada, key=lambda j: (-trabajos[j][0], orden_llegada.index(j))),
        "Holgura": sorted(orden_llegada, key=lambda j: (trabajos[j][1] - trabajos[j][0], orden_llegada.index(j))),
    }


def razon_critica_dinamica(trabajos, orden_llegada, hoy=0):
    """Recalcula RC = (entrega − hoy) / proceso después de cada trabajo terminado."""
    pend, seq, pasos = list(orden_llegada), [], []
    while pend:
        rc = {j: (trabajos[j][1] - hoy) / trabajos[j][0] for j in pend}
        elegido = min(pend, key=lambda j: (rc[j], orden_llegada.index(j)))
        pasos.append((hoy, {j: round(rc[j], 2) for j in pend}, elegido))
        seq.append(elegido)
        pend.remove(elegido)
        hoy += trabajos[elegido][0]
    return seq, pasos


def johnson(tiempos):
    """tiempos: {trabajo: (m1, m2)} → secuencia de Johnson (empates: M1 antes que M2, luego nombre)."""
    pend = dict(tiempos)
    inicio, fin = [], []
    while pend:
        j, (a, b) = min(pend.items(), key=lambda kv: (min(kv[1]), 0 if kv[1][0] <= kv[1][1] else 1, kv[0]))
        if a <= b:
            inicio.append(j)
        else:
            fin.insert(0, j)
        del pend[j]
    return inicio + fin


def flow_shop(seq, tiempos):
    """Taller en serie (todas las máquinas en el mismo orden) → fin de cada trabajo en cada máquina."""
    m = len(next(iter(tiempos.values())))
    fin_maq = [0] * m
    tabla = []
    for j in seq:
        fila, prev = [], 0
        for k in range(m):
            ini = max(fin_maq[k], prev)
            prev = ini + tiempos[j][k]
            fin_maq[k] = prev
            fila.append((ini, prev))
        tabla.append((j, fila))
    return tabla, fin_maq[-1]


def ocio_ultima(tabla):
    """Tiempo ocioso de la última máquina antes y entre trabajos."""
    t, ocio = 0, 0
    for _, fila in tabla:
        ini, fin = fila[-1]
        ocio += ini - t
        t = fin
    return ocio


def cds(tiempos):
    """Campbell, Dudek y Smith: m−1 problemas ficticios de dos máquinas resueltos con Johnson."""
    m = len(next(iter(tiempos.values())))
    candidatos = []
    for k in range(1, m):
        fict = {j: (sum(t[:k]), sum(t[m - k:])) for j, t in tiempos.items()}
        seq = johnson(fict)
        _, mk = flow_shop(seq, tiempos)
        candidatos.append((k, fict, seq, mk))
    return candidatos


def optimo_fuerza_bruta(tiempos):
    mejor = None
    for seq in permutations(sorted(tiempos)):
        _, mk = flow_shop(seq, tiempos)
        if mejor is None or mk < mejor[1]:
            mejor = (seq, mk)
    return mejor


def asignacion_optima(costos):
    """Fuerza bruta (n ≤ 6): mínimo costo total de asignar filas a columnas."""
    filas = list(costos)
    cols = list(next(iter(costos.values())))
    mejor = None
    for perm in permutations(cols):
        c = sum(costos[f][col] for f, col in zip(filas, perm))
        if mejor is None or c < mejor[0]:
            mejor = (c, dict(zip(filas, perm)))
    return mejor


def jackson(trabajos):
    """trabajos: {j: (tA, tB, ruta)} con ruta en {'A','B','AB','BA'}.
    Orden en A: AB (Johnson), luego A, luego BA (Johnson con B como primera).
    Orden en B: BA (Johnson), luego B, luego AB (Johnson)."""
    ab = johnson({j: (a, b) for j, (a, b, r) in trabajos.items() if r == "AB"})
    ba = johnson({j: (b, a) for j, (a, b, r) in trabajos.items() if r == "BA"})
    solo_a = sorted(j for j, (_, _, r) in trabajos.items() if r == "A")
    solo_b = sorted(j for j, (_, _, r) in trabajos.items() if r == "B")
    orden_a = ab + solo_a + ba
    orden_b = ba + solo_b + ab
    # simulación: cada máquina procesa en su orden; una operación espera a la anterior del mismo trabajo
    fin = {}
    libre = {"A": 0, "B": 0}
    cola = {"A": list(orden_a), "B": list(orden_b)}
    ruta = {j: r for j, (_, _, r) in trabajos.items()}
    dur = {j: {"A": a, "B": b} for j, (a, b, _) in trabajos.items()}
    hecho = set()
    while cola["A"] or cola["B"]:
        avanzó = False
        for maq in ("A", "B"):
            if not cola[maq]:
                continue
            j = cola[maq][0]
            r = ruta[j]
            pos = r.index(maq)
            if pos == 1 and (j, r[0]) not in hecho:
                continue
            listo = fin.get((j, r[0]), 0) if pos == 1 else 0
            ini = max(libre[maq], listo)
            fin[(j, maq)] = ini + dur[j][maq]
            libre[maq] = fin[(j, maq)]
            hecho.add((j, maq))
            cola[maq].pop(0)
            avanzó = True
        if not avanzó:
            raise RuntimeError("bloqueo: revisar el orden de Jackson")
    return orden_a, orden_b, max(libre.values()), fin


def control_entradas_salidas(plan_in, real_in, plan_out, real_out, cola_inicial):
    filas, acum_in, acum_out, cola = [], 0, 0, cola_inicial
    for pi, ri, po, ro in zip(plan_in, real_in, plan_out, real_out):
        acum_in += ri - pi
        acum_out += ro - po
        cola += ri - ro
        filas.append((pi, ri, acum_in, po, ro, acum_out, cola))
    return filas


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Ejemplo resuelto · Estampa Sur, máquina de estampado (días de trabajo, día de entrega)
EJEMPLO = {
    "Poleras club": (4, 10),
    "Bolsas feria": (7, 9),
    "Uniformes colegio": (3, 6),
    "Gorros evento": (8, 27),
    "Delantales cocina": (5, 14),
    "Banderas": (2, 20),
}
EJEMPLO_LLEGADA = list(EJEMPLO)

# Ejemplo Johnson · Estampa Sur, estampado → planchado y doblado (horas)
JOHNSON_EJ = {"J1": (4, 6), "J2": (8, 3), "J3": (2, 5), "J4": (6, 7), "J5": (9, 4), "J6": (5, 8)}

# Ejercicio 10.1 · laboratorio dental, un horno de cerámica (días, entrega)
E1 = {"Corona": (3, 5), "Puente": (6, 8), "Carilla": (1, 4), "Prótesis": (4, 13)}
# Ejercicio 10.3 · mueblería, corte → lijado (horas)
E3 = {"Mesa": (6, 2), "Silla": (2, 4), "Repisa": (3, 5), "Velador": (7, 6), "Banco": (4, 1)}
# Ejercicio 10.4 · razón crítica en el día 12 (días de trabajo restantes, día de entrega)
E4 = {"P1": (4, 20), "P2": (6, 15), "P3": (2, 13), "P4": (5, 27)}
E4_HOY = 12
# Ejercicio 10.5 · imprenta digital, una impresora (días, entrega)
E5 = {"Afiches": (5, 7), "Folletos": (2, 11), "Libros": (9, 16), "Tarjetas": (1, 3), "Calendarios": (6, 18), "Revistas": (4, 22)}
# Ejercicio 10.6 · Johnson con empates, cocina industrial: preparación → horneado (min)
E6 = {"K1": (30, 30), "K2": (20, 45), "K3": (40, 20), "K4": (25, 25), "K5": (35, 50)}
# Ejercicio 10.7 · laboratorio clínico, A = centrífuga, B = analizador (min) y ruta
E7 = {
    "M1": (15, 25, "AB"), "M2": (30, 10, "AB"), "M3": (20, 0, "A"),
    "M4": (10, 20, "BA"), "M5": (25, 15, "BA"), "M6": (0, 30, "B"), "M7": (10, 35, "AB"),
}
# Ejercicio 10.8 · control de entradas y salidas del centro de soldadura (horas estándar)
E8 = dict(plan_in=[200, 200, 220, 220], real_in=[190, 230, 240, 210],
          plan_out=[200, 210, 220, 220], real_out=[195, 200, 205, 200], cola_inicial=60)
# Ejercicio 10.9 · CDS, cuatro órdenes por cuatro estaciones (horas)
E9 = {"O1": (6, 4, 7, 3), "O2": (3, 8, 2, 6), "O3": (7, 3, 5, 8), "O4": (2, 6, 4, 5)}
# Ejercicio 10.10 · asignación, cuatro técnicos y cuatro reparaciones (horas)
E10 = {
    "Ana":   {"Bomba": 9, "Motor": 7, "Tablero": 11, "Válvula": 6},
    "Beto":  {"Bomba": 8, "Motor": 10, "Tablero": 7, "Válvula": 9},
    "Carla": {"Bomba": 6, "Motor": 8, "Tablero": 9, "Válvula": 10},
    "Diego": {"Bomba": 10, "Motor": 6, "Tablero": 8, "Válvula": 7},
}

# Caso integrador · órdenes que liberó el MRP de Estampa Sur para la semana 6 (horas)
CASO_ORDENES = {
    "OP-61 poleras básicas": (6, 4, 16),
    "OP-62 polerones": (9, 5, 30),
    "OP-63 poleras estampado doble": (11, 3, 24),
    "OP-64 bolsas": (3, 6, 12),
    "OP-65 gorros": (4, 2, 34),
}  # (estampado h, planchado h, entrega en h desde el lunes 8:00)


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    R["ej"] = {r: evaluar(s, EJEMPLO) for r, s in reglas_estaticas(EJEMPLO, EJEMPLO_LLEGADA).items()}
    seq_rc, pasos_rc = razon_critica_dinamica(EJEMPLO, EJEMPLO_LLEGADA)
    R["ej"]["Razón crítica"] = evaluar(seq_rc, EJEMPLO)
    R["ej_rc_pasos"] = pasos_rc

    sj = johnson(JOHNSON_EJ)
    tabla, mk = flow_shop(sj, JOHNSON_EJ)
    R["johnson_ej"] = (sj, tabla, mk, ocio_ultima(tabla))
    tabla_fifo, mk_fifo = flow_shop(sorted(JOHNSON_EJ), JOHNSON_EJ)
    R["johnson_ej_fifo"] = mk_fifo

    R["e1"] = {r: evaluar(s, E1) for r, s in reglas_estaticas(E1, list(E1)).items() if r in ("FCFS", "SPT", "EDD", "LPT")}
    s3 = johnson(E3); t3, mk3 = flow_shop(s3, E3)
    R["e3"] = (s3, t3, mk3, ocio_ultima(t3))
    R["e4"] = {j: round((d - E4_HOY) / p, 2) for j, (p, d) in E4.items()}

    R["e5"] = {r: evaluar(s, E5) for r, s in reglas_estaticas(E5, list(E5)).items()}
    s5, _ = razon_critica_dinamica(E5, list(E5))
    R["e5"]["Razón crítica"] = evaluar(s5, E5)

    s6 = johnson(E6); t6, mk6 = flow_shop(s6, E6)
    R["e6"] = (s6, t6, mk6, ocio_ultima(t6), optimo_fuerza_bruta(E6)[1])

    R["e7"] = jackson(E7)
    R["e8"] = control_entradas_salidas(**E8)
    R["e9"] = (cds(E9), optimo_fuerza_bruta(E9))
    R["e10"] = asignacion_optima(E10)

    est = {o: (a, b) for o, (a, b, _) in CASO_ORDENES.items()}
    entrega = {o: d for o, (_, _, d) in CASO_ORDENES.items()}
    sc = johnson(est); tc, mkc = flow_shop(sc, est)
    seq_edd = sorted(CASO_ORDENES, key=lambda o: entrega[o])
    te, mke = flow_shop(seq_edd, est)
    atraso = lambda tabla: {o: max(0, fila[-1][1] - entrega[o]) for o, fila in tabla}
    R["caso"] = {"johnson": (sc, tc, mkc, atraso(tc)), "edd": (seq_edd, te, mke, atraso(te))}
    return R


def imprimir(R):
    print("== Ejemplo resuelto: reglas en una máquina")
    for r, v in R["ej"].items():
        print(f"{r:14} {[f[0] for f in v['filas']]}")
        for f in v["filas"]:
            print("     ", f)
        print(f"     flujo total {v['flujo_total']} | prom {fmt(v['flujo_prom'])} | util {pct(v['utilizacion'])} | "
              f"en sistema {fmt(v['en_sistema'], 2)} | atraso prom {fmt(v['atraso_prom'])} | máx {v['atraso_max']} | atrasados {v['atrasados']}")
    print("   pasos razón crítica:")
    for hoy, rc, el in R["ej_rc_pasos"]:
        print(f"     día {hoy}: {rc} → {el}")
    sj, tabla, mk, ocio = R["johnson_ej"]
    print("== Johnson ejemplo", sj, "makespan", mk, "ocio M2", ocio, "| orden J1..J6 daría", R["johnson_ej_fifo"])
    for j, fila in tabla:
        print("     ", j, fila)
    print("== 10.1"); [print(f"   {r:6} {[f[0] for f in v['filas']]} prom {fmt(v['flujo_prom'])} util {pct(v['utilizacion'])} sist {fmt(v['en_sistema'],2)} atraso {fmt(v['atraso_prom'])} máx {v['atraso_max']}") for r, v in R["e1"].items()]
    s3, t3, mk3, o3 = R["e3"]; print("== 10.3", s3, "makespan", mk3, "ocio lijado", o3); [print("     ", j, f) for j, f in t3]
    print("== 10.4 RC día 12", R["e4"])
    print("== 10.5"); [print(f"   {r:14} {[f[0] for f in v['filas']]} prom {fmt(v['flujo_prom'])} util {pct(v['utilizacion'])} sist {fmt(v['en_sistema'],2)} atraso {fmt(v['atraso_prom'])} máx {v['atraso_max']} n {v['atrasados']}") for r, v in R["e5"].items()]
    s6, t6, mk6, o6, opt6 = R["e6"]; print("== 10.6", s6, "makespan", mk6, "ocio horno", o6, "óptimo", opt6); [print("     ", j, f) for j, f in t6]
    oa, ob, mk7, fin7 = R["e7"]; print("== 10.7 orden A", oa, "orden B", ob, "makespan", mk7); print("     ", fin7)
    print("== 10.8"); [print("     ", f) for f in R["e8"]]
    cand, opt9 = R["e9"]; print("== 10.9"); [print(f"   k={k} {fict} → {seq} makespan {mk}") for k, fict, seq, mk in cand]; print("   óptimo", opt9)
    print("== 10.10", R["e10"])
    for nombre, (seq, tabla, mk, atr) in R["caso"].items():
        print(f"== caso {nombre}: {seq} makespan {mk} atrasos {atr}")
        for j, f in tabla:
            print("     ", j, f)


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    """Cadenas que el .md tiene que contener tal cual."""
    e = []
    for r, v in R["ej"].items():
        e += [fmt(v["flujo_prom"]) + " d", pct(v["utilizacion"]), fmt(v["en_sistema"], 2), fmt(v["atraso_prom"]) + " d"]
    sj, _, mk, ocio = R["johnson_ej"]
    e += [" → ".join(sj), f"{mk} h"]
    e += [" → ".join(R["e3"][0]), f"{R['e3'][2]} h"]
    e += [fmt(x, 2) for x in R["e4"].values()]
    e += [" → ".join(R["e6"][0]), f"{R['e6'][2]} min"]
    e += [f"{R['e7'][2]} min"]
    e += [f"{R['e9'][1][1]} h"]
    e += [f"{R['e10'][0]} h"]
    e += [f"{R['caso']['johnson'][2]} h", f"{R['caso']['edd'][2]} h"]
    return e


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    # la semana 6 tiene que ser la misma que deja el caso integrador (unidades 7 y 9)
    import importlib.util
    spec = importlib.util.spec_from_file_location("caso", Path(__file__).with_name("caso_estampa_sur.py"))
    caso = importlib.util.module_from_spec(spec); spec.loader.exec_module(caso)
    semana6 = caso.calcular()["u10"]
    nombres = {o: o.split(" ", 1)[1] for o in CASO_ORDENES}
    distintas = [o for o, (a, b, _) in CASO_ORDENES.items()
                 if (semana6[nombres[o]]["est_h"], semana6[nombres[o]]["pla_h"]) != (a, b)]
    print("\nCADENA:", "OK, la semana 6 calza con el caso integrador" if not distintas else f"NO calza: {distintas}")
    if distintas:
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "10-programacion-de-operaciones.md").read_text(encoding="utf-8")
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
