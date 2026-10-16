"""Unidad 1 · Investigación de operaciones y modelos.

Recalcula todas las cifras de la unidad desde los datos, corre los modelos OPL de `modelos/` (si hay
CPLEX) y exige que coincidan con el mismo modelo resuelto en Python (scipy, HiGHS). Con --revisar
busca cada resultado, escrito como en el texto, dentro del .md.

    python u01_modelos.py            # imprime los resultados
    python u01_modelos.py --revisar  # además los busca en el .md
"""
from fractions import Fraction
from itertools import product
from pathlib import Path
import importlib.util, random, sys

import numpy as np
from scipy.optimize import linprog

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402

MODELOS = RAMO / "modelos"


# ---------------------------------------------------------------- formato chileno

def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x, 0)


def num(x):
    """Entero si lo es; si no, con un decimal."""
    if abs(x) < 1e-9:
        return "0"
    return fmt(round(x), 0) if abs(x - round(x)) < 1e-9 else fmt(x, 1)


# ---------------------------------------------------------------- solver libre

def lp_max(c, A=None, b=None, Aeq=None, beq=None, bounds=None):
    """Máximo de c·x. Devuelve x, z y los duales (positivos para ≤ en un máximo)."""
    r = linprog([-v for v in c], A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq,
                bounds=bounds or [(0, None)] * len(c), method="highs")
    assert r.status == 0, r.message
    duales = list(-r.ineqlin.marginals) if A else []
    return list(r.x), -r.fun, duales


def lp_min(c, A=None, b=None, Aeq=None, beq=None, bounds=None):
    r = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq,
                bounds=bounds or [(0, None)] * len(c), method="highs")
    assert r.status == 0, r.message
    return list(r.x), r.fun


def igual(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1, abs(a), abs(b))


def contra_opl(nombre, mod, dat, esperado):
    """Corre el .mod y compara cada clave impresa con el valor de Python."""
    r = correr(MODELOS / mod, MODELOS / dat if dat else None)
    if r is None:
        print(f"   OPL {nombre}: sin CPLEX, se usa solo Python")
        return True
    distintos = {k: (v, r["valores"].get(k)) for k, v in esperado.items()
                 if not isinstance(r["valores"].get(k), float) or not igual(r["valores"][k], v, 1e-6)}
    print(f"   OPL {nombre}:", "coincide con Python" if not distintos else f"NO coincide {distintos}")
    return not distintos


# ---------------------------------------------------------------- datos (originales)

# Ejemplo resuelto · heladería Nieve del Sur (Pucón), una semana
EJ = {"helados": ["vainilla", "frambuesa", "maqui"],
      "precio": [17_800, 21_500, 25_700], "costo": [8_600, 10_900, 14_300],   # CLP por litro
      "past": [5, 7, 6], "env": [4, 3, 5],                                    # minutos por litro
      "horas_past": 40, "horas_env": 27, "min_vainilla": 60, "tope_maqui": 60}

# 1.1 florería: clásico y silvestre
E1 = {"margen": [5_400, 4_700], "rosas": [6, 3], "silv": [0, 8], "foll": [4, 2],
      "disp": {"rosas": 174, "silv": 184, "foll": 156}, "min_clasico": 5}

# 1.3 miel en frascos de 500 g y de 1 kg
E3 = {"margen": [2_900, 5_300], "kg": [0.5, 1.0], "min": [2, 3], "miel_kg": 236, "horas": 13,
      "min_chicos": 90, "max_grandes": 140}

# 1.5 alimento para gallinas, por tonelada de mezcla
E5 = {"ing": ["maíz", "soya", "conchuela"], "costo": [310, 565, 135],
      "prot": [0.09, 0.47, 0.0], "calcio": [0.0, 0.0, 0.38],
      "total": 1_000, "prot_min": 0.177, "ca_min": 0.0342, "ca_max": 0.0418}

# 1.6 cervecería: lager y stout, en hectolitros por mes
E6 = {"margen": [48_000, 66_000], "malta": [18, 30], "tanque": [6, 3],
      "malta_disp": 2_700, "tanque_disp": 480, "plan": [50, 60]}

# 1.7 frases a restricciones: precios para la del ingreso promedio
E7 = {"precio": [1_040, 1_560, 1_330], "promedio_min": 1_250, "tope_c": 0.35}

# 1.8 canastas (modelo corregido)
E8 = {"margen": [3_100, 6_400], "kg": [4, 9], "min": [6, 10], "verduras": 1_800, "horas": 38}

# 1.9 carro de sándwiches: tres modelos del mismo negocio
E9 = {"precio": 4_600, "costo": 2_350, "demanda": 142, "plancha": 170, "pendiente": 25,
      "escenarios": [(85, 0.35), (125, 0.40), (165, 0.25)]}

# 1.10 cooperativa de pescadores
E10 = {"esp": ["reineta", "merluza"], "proc": ["fresco", "ahumado", "congelado"],
       "captura": [4_200, 5_800], "capacidad": [3_400, 2_600, 3_100],
       "rend": [[1.00, 0.52, 0.46], [1.00, 0.41, 0.43]],
       "precio": [[3_250, 14_200, 9_650], [2_150, 11_300, 7_300]],
       "costo": [160, 1_850, 870]}

# Caso integrador: los datos tal como los muestra la unidad (se comparan con el script del caso)
CASO_TEXTO = {"productos": ["poleras básicas", "polerones", "poleras estampado doble", "bolsas", "gorros"],
              "margen": [1_380, 3_940, 2_270, 960, 1_170], "est": [30, 90, 110, 20, 30],
              "pla": [20, 50, 30, 40, 15], "tinta": [12, 25, 22, 8, 6],
              "demanda": [1_450, 520, 380, 860, 690], "horas_est": 40, "horas_pla": 18, "tinta_g": 29_500}


# ---------------------------------------------------------------- cálculo

def ejemplo():
    d = EJ
    margen = [p - c for p, c in zip(d["precio"], d["costo"])]
    cap = [d["horas_past"] * 60, d["horas_env"] * 60]
    bounds = [(d["min_vainilla"], None), (0, None), (0, d["tope_maqui"])]
    x, z, du = lp_max(margen, [d["past"], d["env"]], cap, bounds=bounds)
    uso = [float(np.dot(d["past"], x)), float(np.dot(d["env"], x))]
    # análisis de rentabilidad: contrato primero, luego el de mayor margen por litro hasta donde alcance
    g = [d["min_vainilla"], 0.0, 0.0]
    resto = [cap[0] - d["past"][0] * g[0], cap[1] - d["env"][0] * g[0]]
    for i in sorted(range(3), key=lambda i: -margen[i]):
        q = min(resto[0] / d["past"][i], resto[1] / d["env"][i])
        if i == 2:
            q = min(q, d["tope_maqui"] - g[2])
        g[i] += q
        resto = [resto[0] - d["past"][i] * q, resto[1] - d["env"][i] * q]
    zg = float(np.dot(margen, g))
    ok = contra_opl("heladería", "u01_heladeria.mod", "u01_heladeria.dat",
                    {"z": z, "x_vainilla": x[0], "x_frambuesa": x[1], "x_maqui": x[2],
                     "holgura_pasteurizacion": cap[0] - uso[0], "holgura_envasado": cap[1] - uso[1],
                     "dual_pasteurizacion": du[0], "dual_envasado": du[1]})
    uso_por = [(d["past"][i] * x[i], d["env"][i] * x[i]) for i in range(3)]
    libre_frambuesa = cap[0] - d["past"][0] * d["min_vainilla"] - d["past"][2] * d["tope_maqui"]
    return {"margen": margen, "cap": cap, "x": x, "z": z, "uso": uso, "duales": du, "uso_por": uso_por,
            "libre_frambuesa": libre_frambuesa,
            "codicioso": g, "z_codicioso": zg, "resto_codicioso": resto, "brecha": z - zg, "opl": ok}


def ej1():
    d = E1
    A = [d["rosas"], d["silv"], d["foll"]]
    b = [d["disp"]["rosas"], d["disp"]["silv"], d["disp"]["foll"]]
    x, z, _ = lp_max(d["margen"], A, b, bounds=[(d["min_clasico"], None), (0, None)])
    mejor = max(((c, s) for c in range(0, 31) for s in range(0, 61)
                 if c >= d["min_clasico"] and all(a[0] * c + a[1] * s <= bb for a, bb in zip(A, b))),
                key=lambda cs: d["margen"][0] * cs[0] + d["margen"][1] * cs[1])
    z_ent = d["margen"][0] * mejor[0] + d["margen"][1] * mejor[1]
    redondeo = (int(x[0]), int(x[1]))
    return {"x": x, "z": z, "entero": mejor, "z_entero": z_ent, "redondeo": redondeo,
            "z_redondeo": d["margen"][0] * redondeo[0] + d["margen"][1] * redondeo[1]}


def ej3():
    d = E3
    cap = d["horas"] * 60
    x, z, du = lp_max(d["margen"], [d["kg"], d["min"]], [d["miel_kg"], cap],
                      bounds=[(d["min_chicos"], None), (0, d["max_grandes"])])
    miel = float(np.dot(d["kg"], x))
    return {"cap_min": cap, "x": x, "z": z, "miel_usada": miel, "holgura_miel": d["miel_kg"] - miel,
            "margen_kg": [m / k for m, k in zip(d["margen"], d["kg"])],
            "margen_min": [m / k for m, k in zip(d["margen"], d["min"])]}


def ej5():
    d = E5
    T = d["total"]
    A = [[-p for p in d["prot"]], [-c for c in d["calcio"]], d["calcio"]]
    b = [-d["prot_min"] * T, -d["ca_min"] * T, d["ca_max"] * T]
    x, z = lp_min(d["costo"], A, b, Aeq=[[1, 1, 1]], beq=[T])
    return {"x": x, "z": z, "prot_kg": float(np.dot(d["prot"], x)), "ca_kg": float(np.dot(d["calcio"], x)),
            "prot_min_kg": d["prot_min"] * T, "ca_min_kg": d["ca_min"] * T, "ca_max_kg": d["ca_max"] * T,
            "conchuela_min": d["ca_min"] * T / d["calcio"][2], "conchuela_max": d["ca_max"] * T / d["calcio"][2]}


def ej6():
    d = E6
    A = [d["malta"], d["tanque"]]
    b = [d["malta_disp"], d["tanque_disp"]]
    x, z, du = lp_max(d["margen"], A, b)
    stout = min(d["malta_disp"] / d["malta"][1], d["tanque_disp"] / d["tanque"][1])
    lager_resto = min((d["malta_disp"] - d["malta"][1] * stout) / d["malta"][0],
                      (d["tanque_disp"] - d["tanque"][1] * stout) / d["tanque"][0])
    g = [lager_resto, stout]
    zg = float(np.dot(d["margen"], g))
    plan = d["plan"]
    uso_plan = [float(np.dot(a, plan)) for a in A]
    zp = float(np.dot(d["margen"], plan))
    assert all(u <= bb for u, bb in zip(uso_plan, b))
    assert igual(zp, z) and igual(x[0], plan[0]) and igual(x[1], plan[1])
    return {"codicioso": g, "z_codicioso": zg, "uso_codicioso": [float(np.dot(a, g)) for a in A],
            "plan": plan, "uso_plan": uso_plan, "z_plan": zp, "brecha": zp - zg,
            "por_malta": [m / k for m, k in zip(d["margen"], d["malta"])],
            "por_tanque": [m / k for m, k in zip(d["margen"], d["tanque"])]}


def ej7():
    """Cada frase en su forma lineal; se prueba contra la frase original en puntos al azar."""
    p, pm, k = E7["precio"], E7["promedio_min"], E7["tope_c"]
    coef_prom = [v - pm for v in p]
    rnd = random.Random(7)
    for _ in range(20_000):
        a, b_, c = (rnd.uniform(0.1, 500) for _ in range(3))
        assert ((b_ >= a / 3) == (a - 3 * b_ <= 0))
        assert ((c <= k * (a + b_ + c)) == (-k * a - k * b_ + (1 - k) * c <= 1e-9))
        prom = (p[0] * a + p[1] * b_ + p[2] * c) / (a + b_ + c)
        assert ((prom >= pm) == (coef_prom[0] * a + coef_prom[1] * b_ + coef_prom[2] * c >= -1e-9))
    return {"coef_promedio": coef_prom}


def ej8():
    d = E8
    cap = d["horas"] * 60
    x, z, du = lp_max(d["margen"], [d["kg"], d["min"]], [d["verduras"], cap])
    xm, zm, _ = lp_max(d["margen"], [d["kg"], d["min"]], [d["verduras"], d["horas"]])  # error de unidades
    ok = contra_opl("canastas", "u01_e08_canastas.mod", None,
                    {"z": z, "x_chica": x[0], "x_grande": x[1], "dual_verduras": du[0], "dual_armado": du[1]})
    return {"cap_min": cap, "x": x, "z": z, "x_mal": xm, "z_mal": zm, "opl": ok}


def ej9():
    d = E9
    a = {"q": min(d["demanda"], d["plancha"])}
    a["util"] = (d["precio"] - d["costo"]) * a["q"]
    # precio que baja con la cantidad: p = alfa − beta·q, que pasa por (130, 4.500)
    beta = d["pendiente"]
    alfa = d["precio"] + beta * d["demanda"]
    q_b = Fraction(alfa - d["costo"], 2 * beta)
    assert q_b.denominator == 1 and q_b <= d["plancha"]
    q_b = int(q_b)
    p_b = alfa - beta * q_b
    b = {"alfa": alfa, "q": q_b, "p": p_b, "util": (p_b - d["costo"]) * q_b}
    # demanda incierta: utilidad esperada de cada cantidad
    esc = d["escenarios"]
    media = sum(D * pr for D, pr in esc)

    def esperada(q):
        ventas = sum(pr * min(q, D) for D, pr in esc)
        return ventas, d["precio"] * ventas - d["costo"] * q

    tabla = {q: esperada(q) for q in sorted({D for D, _ in esc} | {round(media)})}
    # el mismo problema como PL por escenarios: max Σ p_s·precio·v_s − costo·q, v_s ≤ q, v_s ≤ D_s
    n = len(esc)
    c = [-d["costo"]] + [pr * d["precio"] for _, pr in esc]
    A = [[-1] + [1 if j == s else 0 for j in range(n)] for s in range(n)]
    bnd = [(0, d["plancha"])] + [(0, D) for D, _ in esc]
    x, z, _ = lp_max(c, A, [0] * n, bounds=bnd)
    razon = Fraction(d["precio"] - d["costo"], d["precio"])
    return {"a": a, "b": b, "media": media, "tabla": tabla, "q_esto": x[0], "z_esto": z, "razon": razon}


def ej10():
    d = E10
    nE, nP = len(d["esp"]), len(d["proc"])
    m = [[d["precio"][e][p] * d["rend"][e][p] - d["costo"][p] for p in range(nP)] for e in range(nE)]
    c = [m[e][p] for e in range(nE) for p in range(nP)]
    A, b = [], []
    for e in range(nE):
        A.append([1 if ee == e else 0 for ee in range(nE) for _ in range(nP)]); b.append(d["captura"][e])
    for p in range(nP):
        A.append([1 if pp == p else 0 for _ in range(nE) for pp in range(nP)]); b.append(d["capacidad"][p])
    x, z, du = lp_max(c, A, b)
    X = [[x[e * nP + p] for p in range(nP)] for e in range(nE)]
    esperado = {"z": z}
    for e in range(nE):
        for p in range(nP):
            esperado[f"x_{d['esp'][e]}_{d['proc'][p]}"] = X[e][p]
    for e in range(nE):
        esperado[f"dual_{d['esp'][e]}"] = du[e]
    for p in range(nP):
        esperado[f"dual_{d['proc'][p]}"] = du[nE + p]
    ok = contra_opl("cooperativa", "u01_e10_cooperativa.mod", "u01_e10_cooperativa.dat", esperado)
    sobra = [d["captura"][e] - sum(X[e]) for e in range(nE)]
    return {"m": m, "X": X, "z": z, "duales": du, "sobra": sobra, "opl": ok}


def caso():
    d = CASO_TEXTO
    cap = {"est": d["horas_est"] * 3600, "pla": d["horas_pla"] * 3600, "tinta": d["tinta_g"]}
    dem = d["demanda"]
    necesita = {"est": float(np.dot(d["est"], dem)), "pla": float(np.dot(d["pla"], dem)),
                "tinta": float(np.dot(d["tinta"], dem))}
    margen_todo = float(np.dot(d["margen"], dem))
    por_est = [m / s for m, s in zip(d["margen"], d["est"])]
    por_pla = [m / s for m, s in zip(d["margen"], d["pla"])]
    por_tinta = [m / g for m, g in zip(d["margen"], d["tinta"])]
    return {"cap": cap, "necesita": necesita, "margen_todo": margen_todo,
            "por_est": por_est, "por_pla": por_pla, "por_tinta": por_tinta}


def resultados():
    R = {"ej": ejemplo(), "e1": ej1(), "e3": ej3(), "e5": ej5(), "e6": ej6(), "e7": ej7(), "e8": ej8(),
         "e9": ej9(), "e10": ej10(), "caso": caso()}
    return R


def imprimir(R):
    for k, v in R.items():
        print(f"== {k}")
        for kk, vv in v.items():
            if isinstance(vv, (list, tuple)):
                vv = [round(x, 4) if isinstance(x, float) else x for x in vv]
            elif isinstance(vv, float):
                vv = round(vv, 4)
            print(f"   {kk}: {vv}")


# ---------------------------------------------------------------- cadena con el caso

def cadena():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_lp.py")
    c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
    d = CASO_TEXTO
    pares = [(d["productos"], c.PRODUCTOS), (d["margen"], c.MARGEN), (d["est"], c.SEG_EST),
             (d["pla"], c.SEG_PLA), (d["tinta"], c.TINTA_G), (d["demanda"], c.DEMANDA_MAX),
             (d["horas_est"] * 3600, c.CAP["estampado_s"]), (d["horas_pla"] * 3600, c.CAP["planchado_s"]),
             (d["tinta_g"], c.CAP["tinta_g"])]
    ok = all(a == b for a, b in pares)
    print("CADENA:", "OK, los datos de la unidad son los del script del caso" if ok else "NO calza")
    return ok


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    e = []
    ej = R["ej"]
    e += [pesos(m) for m in ej["margen"]] + [fmt(v) for v in ej["cap"]]
    e += [fmt(v) + " L" for v in ej["x"]] + [pesos(ej["z"])]
    e += [fmt(ej["codicioso"][1], 1) + " L", pesos(ej["z_codicioso"]), pesos(ej["brecha"])]
    e += [f"| {fmt(a)} min | {fmt(b)} min |" for a, b in ej["uso_por"]]
    e += [f"{fmt(ej['libre_frambuesa'])} minutos", f"{fmt(ej['resto_codicioso'][1])} minutos ociosos"]
    e1 = R["e1"]
    e += [fmt(e1["x"][0], 1), pesos(e1["z"]), pesos(e1["z_entero"]), pesos(e1["z_redondeo"])]
    e += [f"({e1['entero'][0]}, {e1['entero'][1]})", f"({e1['redondeo'][0]}, {e1['redondeo'][1]})"]
    e += [f"2x_C + x_S \\le {fmt(E1['disp']['rosas'] / 3)}", f"2x_C + x_S \\le {fmt(E1['disp']['foll'] / 2)}"]
    e3 = R["e3"]
    e += [fmt(e3["cap_min"]) + " min", f"({fmt(e3['x'][0])}, {fmt(e3['x'][1])})", pesos(e3["z"]),
          num(e3["miel_usada"]) + " kg", num(e3["holgura_miel"]) + " kg"]
    e += [pesos(v) for v in e3["margen_kg"] + e3["margen_min"]]
    e5 = R["e5"]
    e += [fmt(v) + " kg" for v in e5["x"]] + [pesos(e5["z"]), fmt(e5["conchuela_min"]), fmt(e5["conchuela_max"])]
    e6 = R["e6"]
    e += [pesos(e6["z_codicioso"]), pesos(e6["z_plan"]), pesos(e6["brecha"]),
          fmt(e6["uso_plan"][0]) + " kg", fmt(e6["uso_plan"][1]) + " días-tanque",
          fmt(E6["tanque_disp"] - e6["uso_codicioso"][1]) + " días-tanque ociosos",
          pesos(e6["por_malta"][0]), pesos(e6["por_malta"][1]), pesos(e6["por_tanque"][0]), pesos(e6["por_tanque"][1])]
    a, b, c = R["e7"]["coef_promedio"]
    e += [f"{a}x_A + {b}x_B + {c}x_C \\ge 0"]
    e8 = R["e8"]
    e += [f"({fmt(e8['x'][0])}, {fmt(e8['x'][1])})", pesos(e8["z"]), num(e8["x_mal"][1])]
    e9 = R["e9"]
    e += [pesos(e9["a"]["util"]), pesos(e9["b"]["alfa"]), f"q^* = {e9['b']['q']}", pesos(e9["b"]["p"]),
          pesos(e9["b"]["util"]), fmt(e9["media"])]
    e += [pesos(u) for _, u in e9["tabla"].values()] + [num(v) for v, _ in e9["tabla"].values()]
    e += [pesos(e9["z_esto"]), f"{e9['razon'].numerator}/{e9['razon'].denominator}"]
    e10 = R["e10"]
    e += [pesos(v) for fila in e10["m"] for v in fila] + [pesos(e10["z"])]
    e += [fmt(v) for fila in e10["X"] for v in fila if v > 0]
    c = R["caso"]
    e += [fmt(v) for v in c["cap"].values()] + [fmt(v) for v in c["necesita"].values()] + [pesos(c["margen_todo"])]
    e += [fmt(v, 1) for v in c["por_est"] + c["por_pla"]] + [fmt(v, 0) for v in c["por_tinta"]]
    return e


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if not all(R[k]["opl"] for k in ("ej", "e8", "e10")):
        print("OPL y Python no coinciden")
        sys.exit(1)
    if not cadena():
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (RAMO / "unidades" / "01-investigacion-de-operaciones.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".").replace("\\$", "$")
        faltan = [x for x in esperados(R) if x not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
