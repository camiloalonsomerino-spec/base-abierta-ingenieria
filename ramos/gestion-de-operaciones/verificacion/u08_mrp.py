"""Unidad 8 · MRP.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado (y cada fila de cada registro MRP) aparezca escrito tal cual en el .md.

    python u08_mrp.py            # imprime los resultados y las tablas en Markdown
    python u08_mrp.py --revisar  # además los busca en el .md
"""
from math import ceil, sqrt
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))   # con -P la carpeta del script no entra sola
import caso_estampa_sur as caso

# ---------------------------------------------------------------- herramientas

def fmt(x, dec=0):
    """Número a la chilena: coma decimal, punto de miles."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def lote(neto, politica):
    """Tamaño de la recepción planeada para cubrir un neto positivo."""
    tipo = politica[0]
    if tipo == "L4L":
        return neto
    if tipo in ("FOQ", "MULT"):          # el menor múltiplo de Q (o de m) que cubre el neto
        q = politica[1]
        return ceil(round(neto / q, 9)) * q
    raise ValueError(politica)


def mrp(brutos, inicial, plazo, politica, ss=0, rp=None):
    """Registro MRP por semanas 1..n.
    RN_t = max(0, RB_t + SS − D_{t−1} − RP_t); Rec_t = lote(RN_t); D_t = D_{t−1} + RP_t + Rec_t − RB_t;
    Lib_{t−L} = Rec_t. Una liberación que cae antes de la semana 1 queda en 'vencidas'."""
    n = len(brutos)
    rp = rp or [0] * n
    d, filas, lib, vencidas = inicial, [], [0] * n, []
    for t in range(n):
        neto = max(0, round(brutos[t] + ss - d - rp[t], 9))
        rec = lote(neto, politica) if neto > 0 else 0
        d = round(d + rp[t] + rec - brutos[t], 9)
        if rec:
            if t - plazo >= 0:
                lib[t - plazo] += rec
            else:
                vencidas.append((t - plazo + 1, rec))   # semana (≤ 0) en que debió liberarse
        filas.append({"RB": brutos[t], "RP": rp[t], "D": d, "RN": neto, "Rec": rec})
    for f, l in zip(filas, lib):
        f["Lib"] = l
    return {"filas": filas, "vencidas": vencidas, "lib": lib, "rec": [f["Rec"] for f in filas],
            "disp": [f["D"] for f in filas], "pedidos": sum(1 for f in filas if f["Rec"])}


ROTULOS = [("RB", "RB"), ("RP", "RP"), ("D", "Disp."), ("RN", "RN"), ("Rec", "Rec. pl."), ("Lib", "Lib. pl.")]


def filas_md(reg, dec=0):
    """Filas Markdown del registro (sin encabezado). Ceros en blanco salvo el disponible."""
    out = []
    for clave, rot in ROTULOS:
        celdas = []
        for f in reg["filas"]:
            v = f[clave]
            celdas.append(fmt(v, dec) if (v or clave == "D") else "")
        out.append(f"| {rot} | " + " | ".join(celdas) + " |")
    return out


def tabla_md(reg, dec=0):
    n = len(reg["filas"])
    cab = "| Sem. | " + " | ".join(str(i) for i in range(1, n + 1)) + " |"
    sep = "|---|" + "---|" * n
    return "\n".join([cab, sep] + filas_md(reg, dec))


def costo(reg, s, h):
    """Costo de pedir (S por pedido) más mantener (H por unidad y semana sobre el disponible al cierre)."""
    pedir = reg["pedidos"] * s
    mantener = sum(reg["disp"]) * h
    return pedir, mantener, pedir + mantener


def ppb(netos, s, h):
    """Balance de periodo parcial: cada pedido cubre las semanas cuyo costo de mantener acumulado
    (en unidades-periodo) queda más cerca de EPP = S/H. Empates: se queda el lote más chico."""
    epp = s / h
    n, t, lotes, pasos = len(netos), 0, [0] * len(netos), []
    while t < n:
        if netos[t] == 0:
            t += 1
            continue
        mejor, acum, opciones = None, 0, []
        for k in range(t, n):
            acum += netos[k] * (k - t)
            opciones.append((k, acum))
            if mejor is None or abs(acum - epp) < abs(mejor[1] - epp):
                mejor = (k, acum)
            if acum > epp:
                break
        k = mejor[0]
        lotes[t] = sum(netos[t:k + 1])
        pasos.append((t + 1, opciones, k + 1, lotes[t]))
        t = k + 1
    return lotes, pasos, epp


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. No vienen de ningún libro ni curso.

# Ejemplo resuelto · Mermeladas del Itata, caja de regalo (armado dentro de la semana)
EJ_MPS = [0, 140, 0, 210, 95, 0, 170, 130]          # cajas que se arman cada semana
EJ_FRASCO = dict(por=3, inicial=380, plazo=1, politica=("L4L",), rp=[0, 300, 0, 0, 0, 0, 0, 0])
EJ_TAPA = dict(por=1, inicial=450, plazo=2, politica=("MULT", 500), ss=50)     # hija del frasco
EJ_ESTUCHE = dict(por=1, inicial=220, plazo=2, politica=("FOQ", 400))

# 8.1 · kit de riego: explosión con inventario de líneas armadas
E1_KITS, E1_LINEAS_BODEGA = 250, 140
# 8.2 y 8.3 · cajas de cartón para arándanos
E2_RB = [0, 340, 260, 0, 410, 380, 0, 290]
E2 = dict(inicial=450, plazo=1, rp=[0, 200, 0, 0, 0, 0, 0, 0])
E3_Q = 800
# 8.4 · pegamento por silla, tarros de 4 kg
E4_MPS = [220, 0, 310, 190, 0, 260]
E4 = dict(por=0.06, inicial=14, plazo=1, politica=("MULT", 4))
# 8.5 · mesa plegable: mesa (padre) → patas ×4 y tablero ×1
E5_MESA_RB = [0, 0, 130, 110, 0, 140, 125, 75]
E5_MESA = dict(inicial=60, plazo=1, politica=("L4L",))
E5_PATA = dict(por=4, inicial=300, plazo=2, politica=("FOQ", 600))
E5_TABLERO = dict(por=1, inicial=40, plazo=1, politica=("L4L",))
# 8.6 · stock de seguridad, recepción programada y liberación vencida
E6_RB = [95, 130, 60, 140, 0, 110]
E6 = dict(inicial=120, plazo=2, politica=("L4L",), ss=40, rp=[0, 0, 250, 0, 0, 0])
# 8.7 · perno común a escritorio y cajonera (código de nivel más bajo)
E7_ESC_LIB = [0, 45, 0, 60, 35, 50]                 # liberaciones de armado de escritorios
E7_CAJ = dict(por=1, inicial=30, plazo=1, politica=("L4L",))
E7_PERNO = dict(por_esc=6, por_caj=4, inicial=400, plazo=1, politica=("MULT", 250))
# 8.8 · costo de lote a lote frente a cantidad fija (EOQ redondeado a la centena)
E8_RB = [0, 260, 340, 0, 310, 280, 0, 360]
E8 = dict(inicial=0, plazo=1, s=120_000, h=150)
# 8.9 · silla de terraza: respaldo (fabricado) ← listón; pata; listón común a dos niveles
E9_MPS = [0, 115, 0, 140, 95, 0, 135, 105]
E9_MPS_CAMBIO = (4, 175)                             # la semana 4 sube a 175 sillas
E9_RESP = dict(por=1, inicial=80, plazo=1, politica=("L4L",))
E9_PATA = dict(por=4, inicial=600, plazo=2, politica=("FOQ", 1200))
E9_LISTON = dict(por_silla=3, por_resp=5, inicial=900, plazo=2, politica=("MULT", 50), ss=100)
# 8.10 · balance de periodo parcial (el inventario inicial cubre la semana 1, plazo 1)
E10_RB = [210, 45, 130, 0, 95, 140, 30, 175]
E10 = dict(inicial=210, s=90_000, h=400)


# ---------------------------------------------------------------- resultados

def escala(v, por):
    return [round(x * por, 9) for x in v]


def silla(mps):
    resp = mrp(escala(mps, E9_RESP["por"]), E9_RESP["inicial"], E9_RESP["plazo"], E9_RESP["politica"])
    pata = mrp(escala(mps, E9_PATA["por"]), E9_PATA["inicial"], E9_PATA["plazo"], E9_PATA["politica"])
    rb_l = [E9_LISTON["por_silla"] * m + E9_LISTON["por_resp"] * r for m, r in zip(mps, resp["lib"])]
    listón = mrp(rb_l, E9_LISTON["inicial"], E9_LISTON["plazo"], E9_LISTON["politica"], ss=E9_LISTON["ss"])
    return resp, pata, listón


def resultados():
    R = {}
    # ejemplo
    fr = mrp(escala(EJ_MPS, EJ_FRASCO["por"]), EJ_FRASCO["inicial"], EJ_FRASCO["plazo"], EJ_FRASCO["politica"], rp=EJ_FRASCO["rp"])
    ta = mrp(escala(fr["lib"], EJ_TAPA["por"]), EJ_TAPA["inicial"], EJ_TAPA["plazo"], EJ_TAPA["politica"], ss=EJ_TAPA["ss"])
    es = mrp(escala(EJ_MPS, EJ_ESTUCHE["por"]), EJ_ESTUCHE["inicial"], EJ_ESTUCHE["plazo"], EJ_ESTUCHE["politica"])
    R["ej"] = {"frasco": fr, "tapa": ta, "estuche": es}

    # 8.1
    lineas = 4 * E1_KITS - E1_LINEAS_BODEGA
    R["e1"] = {"programador": E1_KITS, "lineas_brutas": 4 * E1_KITS, "lineas_a_armar": lineas,
               "goteros": 12 * lineas, "conectores": 2 * E1_KITS + lineas, "tapones": lineas, "mangueras": lineas,
               "conectores_sin_inv": 2 * E1_KITS + 4 * E1_KITS}
    # 8.2 y 8.3
    R["e2"] = mrp(E2_RB, E2["inicial"], E2["plazo"], ("L4L",), rp=E2["rp"])
    R["e3"] = mrp(E2_RB, E2["inicial"], E2["plazo"], ("FOQ", E3_Q), rp=E2["rp"])
    # 8.4
    R["e4"] = mrp(escala(E4_MPS, E4["por"]), E4["inicial"], E4["plazo"], E4["politica"])
    # 8.5
    me = mrp(E5_MESA_RB, E5_MESA["inicial"], E5_MESA["plazo"], E5_MESA["politica"])
    pa = mrp(escala(me["lib"], E5_PATA["por"]), E5_PATA["inicial"], E5_PATA["plazo"], E5_PATA["politica"])
    tb = mrp(escala(me["lib"], E5_TABLERO["por"]), E5_TABLERO["inicial"], E5_TABLERO["plazo"], E5_TABLERO["politica"])
    R["e5"] = {"mesa": me, "pata": pa, "tablero": tb}
    # 8.6
    R["e6"] = mrp(E6_RB, E6["inicial"], E6["plazo"], E6["politica"], ss=E6["ss"], rp=E6["rp"])
    R["e6_sin_ss"] = mrp(E6_RB, E6["inicial"], E6["plazo"], E6["politica"], ss=0, rp=E6["rp"])
    # 8.7
    cj = mrp(E7_ESC_LIB, E7_CAJ["inicial"], E7_CAJ["plazo"], E7_CAJ["politica"])
    rb_p = [E7_PERNO["por_esc"] * e + E7_PERNO["por_caj"] * c for e, c in zip(E7_ESC_LIB, cj["lib"])]
    pe = mrp(rb_p, E7_PERNO["inicial"], E7_PERNO["plazo"], E7_PERNO["politica"])
    R["e7"] = {"cajonera": cj, "perno": pe}
    # 8.8
    d_sem = sum(E8_RB) / len(E8_RB)
    q_eoq = sqrt(2 * d_sem * E8["s"] / E8["h"])
    q = round(q_eoq, -2)
    l4l = mrp(E8_RB, E8["inicial"], E8["plazo"], ("L4L",))
    foq = mrp(E8_RB, E8["inicial"], E8["plazo"], ("FOQ", q))
    R["e8"] = {"d_sem": d_sem, "eoq": q_eoq, "q": q, "l4l": l4l, "foq": foq,
               "c_l4l": costo(l4l, E8["s"], E8["h"]), "c_foq": costo(foq, E8["s"], E8["h"])}
    # 8.9
    base = silla(E9_MPS)
    mps2 = list(E9_MPS); mps2[E9_MPS_CAMBIO[0] - 1] = E9_MPS_CAMBIO[1]
    cambio = silla(mps2)
    R["e9"] = {"base": base, "cambio": cambio}
    # 8.10
    l4l10 = mrp(E10_RB, E10["inicial"], 1, ("L4L",))
    netos = [f["RN"] for f in l4l10["filas"]]
    lotes, pasos, epp = ppb(netos, E10["s"], E10["h"])
    rec_ppb = lotes
    # registro con esos lotes: disponible al cierre
    d, disp = E10["inicial"], []
    for r, b in zip(rec_ppb, E10_RB):
        d = d + r - b
        disp.append(d)
    ped = sum(1 for x in rec_ppb if x)
    c_ppb = (ped * E10["s"], sum(disp) * E10["h"], ped * E10["s"] + sum(disp) * E10["h"])
    R["e10"] = {"lotes": lotes, "pasos": pasos, "epp": epp, "disp": disp, "costo_ppb": c_ppb,
                "costo_l4l": costo(l4l10, E10["s"], E10["h"]), "lib": rec_ppb[1:] + [0], "netos": netos,
                "l4l": l4l10}

    # caso integrador (lo calcula caso_estampa_sur.py; acá solo se arma el registro completo)
    C = caso.calcular()
    mps_pb = [f["MPS"] for f in C["u7"]["poleras básicas"]]
    regs = {}
    for comp, d in caso.LDM.items():
        brutos = [x * d["por_unidad"] for x in mps_pb]
        pol = ("FOQ", C["u5"]["EOQ_redondeado"]) if d["politica"] == "cantidad fija" else \
              ("MULT", int(d["politica"].split()[-1])) if d["politica"].startswith("múltiplos") else ("L4L",)
        regs[comp] = mrp(brutos, d["inventario"], d["plazo"], pol)
        # control cruzado: el mismo resultado que el script del caso
        ref = C["u8"][comp]
        for f, g in zip(regs[comp]["filas"], ref):
            assert abs(f["Rec"] - g["recepcion_planeada"]) < 1e-6 and abs(f["Lib"] - g["liberacion"]) < 1e-6 \
                and abs(f["D"] - g["disponible"]) < 1e-6, comp
    R["caso"] = {"mps": mps_pb, "regs": regs, "foq": C["u5"]["EOQ_redondeado"], "eoq": C["u5"]["EOQ"]}
    return R


# ---------------------------------------------------------------- impresión

def imprimir(R):
    def bloque(titulo, reg, dec=0):
        print(f"\n### {titulo}  (pedidos {reg['pedidos']}, vencidas {reg['vencidas']}, suma disp {fmt(sum(reg['disp']), dec)})")
        print(tabla_md(reg, dec))

    for k, v in R["ej"].items():
        bloque(f"ejemplo · {k}", v)
    print("\n== 8.1", R["e1"])
    bloque("8.2 lote a lote", R["e2"]); bloque("8.3 FOQ 800", R["e3"])
    bloque("8.4 pegamento (kg)", R["e4"], 1)
    for k, v in R["e5"].items():
        bloque(f"8.5 {k}", v)
    bloque("8.6 con SS", R["e6"]); bloque("8.6 sin SS", R["e6_sin_ss"])
    for k, v in R["e7"].items():
        bloque(f"8.7 {k}", v)
    e8 = R["e8"]
    print(f"\n== 8.8 demanda semanal {fmt(e8['d_sem'],1)} EOQ {fmt(e8['eoq'],1)} → Q {fmt(e8['q'])}")
    print("   costo L4L", [fmt(x) for x in e8["c_l4l"]], "FOQ", [fmt(x) for x in e8["c_foq"]])
    bloque("8.8 L4L", e8["l4l"]); bloque("8.8 FOQ", e8["foq"])
    for nombre in ("base", "cambio"):
        for k, v in zip(("respaldo", "pata", "listón"), R["e9"][nombre]):
            bloque(f"8.9 {nombre} · {k}", v)
    e10 = R["e10"]
    print(f"\n== 8.10 EPP {fmt(e10['epp'])} lotes {e10['lotes']} disp {e10['disp']}")
    for p in e10["pasos"]:
        print("   ", p)
    print("   costo PPB", [fmt(x) for x in e10["costo_ppb"]], "L4L", [fmt(x) for x in e10["costo_l4l"]])
    for comp, reg in R["caso"]["regs"].items():
        bloque(f"caso · {comp}", reg, 1 if "tinta" in comp else 0)


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    e = []
    for v in R["ej"].values():
        e += filas_md(v)
    e1 = R["e1"]
    e += [fmt(e1[k]) for k in ("lineas_a_armar", "goteros", "conectores", "conectores_sin_inv")]
    e += filas_md(R["e2"]) + filas_md(R["e3"]) + filas_md(R["e4"], 1)
    for v in R["e5"].values():
        e += filas_md(v)
    e += filas_md(R["e6"]) + filas_md(R["e6_sin_ss"])
    for v in R["e7"].values():
        e += filas_md(v)
    e8 = R["e8"]
    e += [fmt(e8["d_sem"], 1), fmt(e8["eoq"], 1), fmt(e8["q"])] + [f"${fmt(x)}" for x in e8["c_l4l"] + e8["c_foq"]]
    e += filas_md(e8["l4l"]) + filas_md(e8["foq"])
    for regs in R["e9"].values():
        for v in regs:
            e += filas_md(v)
    e10 = R["e10"]
    e += [fmt(e10["epp"])] + [f"${fmt(x)}" for x in e10["costo_ppb"] + e10["costo_l4l"]]
    e += [f"**{fmt(x)}**" for x in e10["lotes"] if x] + [f"{fmt(sum(e10['disp']))} unidades-semana"]
    e += [f"${fmt(e10['costo_l4l'][2] - e10['costo_ppb'][2])}"]
    e += [f"suma del disponible es {fmt(sum(R['e2']['disp']))}", f"sube a {fmt(sum(R['e3']['disp']))}",
          f"{fmt(sum(e8['foq']['disp']))} unidades-semana"]
    for comp, reg in R["caso"]["regs"].items():
        e += filas_md(reg, 1 if "tinta" in comp else 0)
    e += [fmt(R["caso"]["foq"]), fmt(R["caso"]["eoq"], 1)]
    return e


if __name__ == "__main__":
    R = resultados()
    imprimir(R)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "08-mrp.md").read_text(encoding="utf-8")
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
