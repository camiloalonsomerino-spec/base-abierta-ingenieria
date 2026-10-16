"""Unidad 8 · Duración, convexidad e inmunización.

Recalcula todas las cifras de la unidad desde los datos y, con --revisar, comprueba que cada
resultado aparezca escrito tal cual en el .md. La pieza del caso integrador se toma de
caso_valentina.py y se compara con lo que este script recalcula por su cuenta.

    py -3 -P u08_duracion.py            # imprime los resultados
    py -3 -P u08_duracion.py --revisar  # además los busca en el .md
"""
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))  # con -P la carpeta del script no entra sola
import caso_valentina as caso  # noqa: E402


# ---------------------------------------------------------------- herramientas

def fmt(x, dec=2):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=2):
    return fmt(100 * x, dec) + " %"


def clp(x):
    return "$" + fmt(x, 0)


def bullet(vn, c, n):
    cup = vn * c
    return [cup] * (n - 1) + [cup + vn]


def precio(flujos, y):
    return sum(f / (1 + y) ** t for t, f in enumerate(flujos, start=1))


def medidas(flujos, y):
    """Precio, duración de Macaulay, modificada y convexidad (en períodos) de flujos en t = 1, 2, …"""
    p = precio(flujos, y)
    tabla = [{"t": t, "f": f, "fd": 1 / (1 + y) ** t, "vp": f / (1 + y) ** t,
              "peso": f / (1 + y) ** t / p, "tvp": t * f / (1 + y) ** t,
              "cvp": t * (t + 1) * f / (1 + y) ** (t + 2)} for t, f in enumerate(flujos, start=1)]
    d = sum(r["tvp"] for r in tabla) / p
    conv = sum(r["cvp"] for r in tabla) / p
    return {"p": p, "tabla": tabla, "d": d, "dmod": d / (1 + y), "conv": conv,
            "suma_tvp": sum(r["tvp"] for r in tabla), "suma_cvp": sum(r["cvp"] for r in tabla)}


def aproximar(m, dy, y, flujos):
    """Cambio % del precio por duración, por duración más convexidad, y el exacto."""
    solo_d = -m["dmod"] * dy
    con_c = solo_d + 0.5 * m["conv"] * dy ** 2
    exacto = precio(flujos, y + dy) / m["p"] - 1
    return {"dy": dy, "solo_d": solo_d, "con_c": con_c, "exacto": exacto,
            "p_d": m["p"] * (1 + solo_d), "p_c": m["p"] * (1 + con_c), "p_exacto": precio(flujos, y + dy)}


def valor_en_H(posiciones, H, r_reinv, r_desc=None):
    """Valor en H de una cartera comprada hoy si la tasa salta justo después de comprar.
    posiciones: lista de (unidades, flujos por unidad en t = 1, 2, …). Lo que llega antes de H se
    reinvierte a r_reinv hasta H; lo que llega después de H se descuenta a r_desc (por defecto,
    la misma tasa: cambio paralelo)."""
    r_desc = r_reinv if r_desc is None else r_desc
    total = 0.0
    for u, fl in posiciones:
        for t, f in enumerate(fl, start=1):
            total += u * (f * (1 + r_reinv) ** (H - t) if t <= H else f / (1 + r_desc) ** (t - H))
    return total


def inmunizar(pasivo, H, y, fl_a, fl_b):
    """Pesos de dos instrumentos que calzan VP y duración con un pasivo único en H."""
    ma, mb = medidas(fl_a, y), medidas(fl_b, y)
    vp_pas = pasivo / (1 + y) ** H
    w_b = (H - ma["d"]) / (mb["d"] - ma["d"])
    monto_a, monto_b = (1 - w_b) * vp_pas, w_b * vp_pas
    pos = [(monto_a / ma["p"], fl_a), (monto_b / mb["p"], fl_b)]
    return {"ma": ma, "mb": mb, "vp_pas": vp_pas, "w_a": 1 - w_b, "w_b": w_b, "monto_a": monto_a, "monto_b": monto_b,
            "pos": pos, "d_cartera": (1 - w_b) * ma["d"] + w_b * mb["d"],
            "conv_cartera": (1 - w_b) * ma["conv"] + w_b * mb["conv"], "conv_pasivo": H * (H + 1) / (1 + y) ** 2}


def cero(n, vn=100):
    return [0.0] * (n - 1) + [vn]


# ---------------------------------------------------------------- datos de la unidad
# Todos los datos son originales de esta base. Personas, emisores y tasas son ficticios.

# Ejemplo resuelto · pie de un departamento en verde, a 4 años
EJ = dict(pasivo=18_400_000, H=4, y=0.053, c=0.062, n=6, n_cero=2, choque=0.01)
# 8.1 · bullet a 3 años
E1 = dict(c=0.074, n=3, y=0.061, dy=0.005)
# 8.2 · cero cupón y perpetuidad
E2 = dict(n=7, y_cero=0.048, y_perp=0.065, dy=0.01)
# 8.3 · duración de una cartera (montos en millones de pesos)
E3 = dict(montos=(40, 25, 35), d=(2.3, 5.8, 8.6), H=5)
# 8.5 · cupón semestral
E5 = dict(vn=2_500, c_sem=0.0225, semestres=8, y_anual=0.051, y_anual2=0.059)
# 8.6 · convexidad
E6 = dict(c=0.045, n=8, y=0.068, dy=0.02)
# 8.7 · bala contra pesas (bullet contra barbell), ceros con igual duración
E7 = dict(monto=10_000_000, y=0.055, n_bala=5, n_corto=1, n_largo=9, dy=0.02)
# 8.8 y 8.9 · inmunizar un pago a 6 años
E8 = dict(pasivo=45_000_000, H=6, y=0.047, n_cero=3, c=0.05, n=10, choque=0.01)
E9 = dict(r_corta=0.037, r_larga=0.057)


# ---------------------------------------------------------------- resultados

def resultados():
    R = {}
    # ---- ejemplo resuelto
    e = EJ
    flb = bullet(100, e["c"], e["n"])
    flc = cero(e["n_cero"])
    inm = inmunizar(e["pasivo"], e["H"], e["y"], flc, flb)
    mb = inm["mb"]
    ap = {s: aproximar(mb, s * e["choque"], e["y"], flb) for s in (1, -1)}
    prueba = {}
    for nombre, pos in (("inmunizada", inm["pos"]),
                        ("todo_bono", [(inm["vp_pas"] / mb["p"], flb)]),
                        ("todo_cero", [(inm["vp_pas"] / inm["ma"]["p"], flc)])):
        prueba[nombre] = {s: valor_en_H(pos, e["H"], e["y"] + s * e["choque"]) for s in (0, 1, -1)}
    R["ej"] = {**inm, "ap": ap, "prueba": prueba, "nom_bono": inm["monto_b"] / mb["p"] * 100,
               "nom_cero": inm["monto_a"] / inm["ma"]["p"] * 100}
    # ---- 8.1
    e = E1
    fl = bullet(100, e["c"], e["n"])
    m = medidas(fl, e["y"])
    R["e1"] = {"m": m, "ap": aproximar(m, e["dy"], e["y"], fl)}
    # ---- 8.2
    e = E2
    fl = cero(e["n"])
    m = medidas(fl, e["y_cero"])
    d_perp = (1 + e["y_perp"]) / e["y_perp"]
    R["e2"] = {"m": m, "ap": aproximar(m, e["dy"], e["y_cero"], fl),
               "d_perp": d_perp, "dmod_perp": 1 / e["y_perp"], "est_perp": -e["dy"] / e["y_perp"],
               "exacto_perp": e["y_perp"] / (e["y_perp"] + e["dy"]) - 1}
    # ---- 8.3
    e = E3
    tot = sum(e["montos"])
    d = sum(mo * di for mo, di in zip(e["montos"], e["d"])) / tot
    mover = (d - e["H"]) * tot / (e["d"][2] - e["d"][0])          # millones que pasan de C a A
    R["e3"] = {"tot": tot, "pesos": [mo / tot for mo in e["montos"]], "d": d, "mover": mover,
               "nuevo_a": e["montos"][0] + mover, "nuevo_c": e["montos"][2] - mover}
    # ---- 8.5 semestral
    e = E5
    ys, ys2 = (1 + e["y_anual"]) ** 0.5 - 1, (1 + e["y_anual2"]) ** 0.5 - 1
    fl = bullet(e["vn"], e["c_sem"], e["semestres"])
    m = medidas(fl, ys)
    R["e5"] = {"ys": ys, "ys2": ys2, "dys": ys2 - ys, "m": m, "d_anios": m["d"] / 2,
               "ap": aproximar(m, ys2 - ys, ys, fl)}
    # ---- 8.6 convexidad
    e = E6
    fl = bullet(100, e["c"], e["n"])
    m = medidas(fl, e["y"])
    R["e6"] = {"m": m, "ap": {s: aproximar(m, s * e["dy"], e["y"], fl) for s in (1, -1)}}
    # ---- 8.7 bala contra pesas
    e = E7
    y = e["y"]
    w_largo = (e["n_bala"] - e["n_corto"]) / (e["n_largo"] - e["n_corto"])
    conv = lambda n: n * (n + 1) / (1 + y) ** 2
    def valor(dy):
        b = e["monto"] * ((1 + y) / (1 + y + dy)) ** e["n_bala"]
        p = e["monto"] * ((1 - w_largo) * ((1 + y) / (1 + y + dy)) ** e["n_corto"]
                          + w_largo * ((1 + y) / (1 + y + dy)) ** e["n_largo"])
        return b, p
    R["e7"] = {"w_largo": w_largo, "conv_bala": conv(e["n_bala"]),
               "conv_pesas": (1 - w_largo) * conv(e["n_corto"]) + w_largo * conv(e["n_largo"]),
               "dmod": e["n_bala"] / (1 + y),
               "valores": {s: valor(s * e["dy"]) for s in (1, -1)}}
    # ---- 8.8 inmunizar a 6 años
    e = E8
    flc, flb = cero(e["n_cero"]), bullet(100, e["c"], e["n"])
    inm = inmunizar(e["pasivo"], e["H"], e["y"], flc, flb)
    R["e8"] = {**inm, "prueba": {s: valor_en_H(inm["pos"], e["H"], e["y"] + s * e["choque"]) for s in (0, 1, -1)}}
    # ---- 8.9 un año después y la curva que se tuerce
    H1 = e["H"] - 1
    ua, ub = inm["pos"][0][0], inm["pos"][1][0]
    flc1, flb1 = flc[1:], flb[1:]                       # lo que queda en t = 1 (cobrado el cupón del año 1)
    ma1, mb1 = medidas(flc1, e["y"]), medidas(flb1, e["y"])
    va, vb = ua * ma1["p"], ub * mb1["p"]
    cupon_1 = ub * flb[0]
    d1 = (va * ma1["d"] + vb * mb1["d"]) / (va + vb)    # sin contar el cupón cobrado, que es caja (D = 0)
    tot1 = va + vb + cupon_1
    d1_con_caja = (va * ma1["d"] + vb * mb1["d"]) / tot1
    wb_nuevo = (H1 - ma1["d"]) / (mb1["d"] - ma1["d"])
    torcida = valor_en_H(inm["pos"], e["H"], E9["r_corta"], E9["r_larga"])
    R["e9"] = {"d_cero1": ma1["d"], "d_bono1": mb1["d"], "va": va, "vb": vb, "cupon_1": cupon_1, "tot1": tot1,
               "d1": d1, "d1_con_caja": d1_con_caja, "wb_nuevo": wb_nuevo, "wb_antes": vb / (va + vb),
               "vp_pas1": e["pasivo"] / (1 + e["y"]) ** H1,
               "monto_b_nuevo": wb_nuevo * tot1, "monto_a_nuevo": (1 - wb_nuevo) * tot1,
               "torcida": torcida, "falta": e["pasivo"] - torcida}
    # ---- caso integrador · lo recalcula este script y lo compara con el del caso
    C = caso.calcular()
    u7, u8 = C["u7"], C["u8"]
    y = u7["ytm"]
    flb = u7["flujos"]
    H = caso.U5["anio_saldo"]
    pas = caso.U5["saldo_maquina"]
    inm = inmunizar(pas, H, y, [100.0], flb)          # cero a 1 año contra el bono de la unidad 7
    prueba = {s: valor_en_H(inm["pos"], H, y + s * 0.01) for s in (0, 1, -1)}
    todo_bono = {s: valor_en_H([(inm["vp_pas"] / inm["mb"]["p"], flb)], H, y + s * 0.01) for s in (0, 1, -1)}
    todo_cero = {s: valor_en_H([(inm["vp_pas"] / 100 * (1 + y), [100.0])], H, y + s * 0.01) for s in (0, 1, -1)}
    R["caso"] = {**inm, "y": y, "prueba": prueba, "todo_bono": todo_bono, "todo_cero": todo_cero,
                 "ap": {s: aproximar(inm["mb"], s * 0.01, y, flb) for s in (1, -1)},
                 "nom_bono": inm["monto_b"] / inm["mb"]["p"] * 100, "cobro_cero": inm["monto_a"] * (1 + y),
                 "u8": u8}
    return R


def imprimir(R):
    e = R["ej"]; mb = e["mb"]
    print("== Ejemplo")
    print(f"   VP pasivo {clp(e['vp_pas'])} | bono P {fmt(mb['p'],4)} D {fmt(mb['d'],4)} Dmod {fmt(mb['dmod'],4)} C {fmt(mb['conv'],4)} Σt·VP {fmt(mb['suma_tvp'])} Σcvp {fmt(mb['suma_cvp'])}")
    for r in mb["tabla"]:
        print(f"     t{r['t']} f {fmt(r['f'],1)} fd {fmt(r['fd'],6)} vp {fmt(r['vp'],4)} peso {pct(r['peso'],1)} tvp {fmt(r['tvp'],4)} cvp {fmt(r['cvp'],4)}")
    print(f"   cero P {fmt(e['ma']['p'],4)} | w bono {pct(e['w_b'],2)} w cero {pct(e['w_a'],2)} montos bono {clp(e['monto_b'])} cero {clp(e['monto_a'])} nom bono {clp(e['nom_bono'])} nom cero {clp(e['nom_cero'])}")
    print(f"   D cartera {fmt(e['d_cartera'],4)} conv cartera {fmt(e['conv_cartera'],3)} conv pasivo {fmt(e['conv_pasivo'],3)}")
    for s, a in e["ap"].items():
        print(f"   choque {s:+}: solo D {pct(a['solo_d'],3)} con C {pct(a['con_c'],3)} exacto {pct(a['exacto'],3)} | P {fmt(a['p_d'])} {fmt(a['p_c'])} {fmt(a['p_exacto'])}")
    for k, v in e["prueba"].items():
        print(f"   {k}: " + " ".join(f"{s:+} {clp(x)} ({clp(x - EJ['pasivo'])})" for s, x in v.items()))
    e = R["e1"]; m = e["m"]; a = e["ap"]
    print(f"== 8.1 P {fmt(m['p'],4)} D {fmt(m['d'],4)} Dmod {fmt(m['dmod'],4)} Σtvp {fmt(m['suma_tvp'],4)} | est {pct(a['solo_d'],3)} P {fmt(a['p_d'])} exacto {pct(a['exacto'],3)} P {fmt(a['p_exacto'])}")
    for r in m["tabla"]:
        print(f"     t{r['t']} fd {fmt(r['fd'],6)} vp {fmt(r['vp'],4)} tvp {fmt(r['tvp'],4)}")
    e = R["e2"]; m = e["m"]; a = e["ap"]
    print(f"== 8.2 cero P {fmt(m['p'],4)} D {fmt(m['d'],4)} Dmod {fmt(m['dmod'],4)} est {pct(a['solo_d'],2)} exacto {pct(a['exacto'],2)} | perp D {fmt(e['d_perp'],2)} Dmod {fmt(e['dmod_perp'],2)} est {pct(e['est_perp'],2)} exacto {pct(e['exacto_perp'],2)}")
    e = R["e3"]; print(f"== 8.3 tot {e['tot']} pesos {[pct(p,0) for p in e['pesos']]} D {fmt(e['d'],2)} mover {fmt(e['mover'],2)} A {fmt(e['nuevo_a'],2)} C {fmt(e['nuevo_c'],2)}")
    e = R["e5"]; m = e["m"]; a = e["ap"]
    print(f"== 8.5 ys {pct(e['ys'],4)} ys2 {pct(e['ys2'],4)} dys {pct(e['dys'],4)} P {fmt(m['p'])} D sem {fmt(m['d'],4)} D años {fmt(e['d_anios'],4)} Dmod sem {fmt(m['dmod'],4)} Σtvp {fmt(m['suma_tvp'])} | est {pct(a['solo_d'],3)} P {fmt(a['p_d'])} exacto {pct(a['exacto'],3)} P {fmt(a['p_exacto'])}")
    e = R["e6"]; m = e["m"]
    print(f"== 8.6 P {fmt(m['p'],4)} D {fmt(m['d'],4)} Dmod {fmt(m['dmod'],4)} C {fmt(m['conv'],4)}")
    for s, a in e["ap"].items():
        print(f"     {s:+}: solo D {pct(a['solo_d'],2)} con C {pct(a['con_c'],2)} exacto {pct(a['exacto'],2)} | P {fmt(a['p_d'])} {fmt(a['p_c'])} {fmt(a['p_exacto'])}")
    e = R["e7"]
    print(f"== 8.7 w largo {pct(e['w_largo'],0)} Dmod {fmt(e['dmod'],4)} conv bala {fmt(e['conv_bala'],2)} pesas {fmt(e['conv_pesas'],2)}", {s: (clp(b), clp(p), clp(p - b)) for s, (b, p) in e["valores"].items()})
    e = R["e8"]
    print(f"== 8.8 VP pas {clp(e['vp_pas'])} bono P {fmt(e['mb']['p'],4)} D {fmt(e['mb']['d'],4)} conv {fmt(e['mb']['conv'],3)} cero P {fmt(e['ma']['p'],4)} w bono {pct(e['w_b'])} w cero {pct(e['w_a'])} montos {clp(e['monto_b'])} {clp(e['monto_a'])} conv cart {fmt(e['conv_cartera'],2)} conv pas {fmt(e['conv_pasivo'],2)}")
    print("     prueba", {s: (clp(v), clp(v - E8['pasivo'])) for s, v in e["prueba"].items()})
    e = R["e9"]
    print(f"== 8.9 D cero1 {fmt(e['d_cero1'],2)} D bono1 {fmt(e['d_bono1'],4)} va {clp(e['va'])} vb {clp(e['vb'])} cupón {clp(e['cupon_1'])} tot {clp(e['tot1'])} vp pas1 {clp(e['vp_pas1'])} D1 {fmt(e['d1'],4)} D1 con caja {fmt(e['d1_con_caja'],4)} wb antes {pct(e['wb_antes'])} wb nuevo {pct(e['wb_nuevo'])} montos {clp(e['monto_b_nuevo'])} {clp(e['monto_a_nuevo'])} | torcida {clp(e['torcida'])} falta {clp(e['falta'])}")
    c = R["caso"]
    print(f"== caso y {pct(c['y'],3)} D {fmt(c['mb']['d'],4)} Dmod {fmt(c['mb']['dmod'],4)} C {fmt(c['mb']['conv'],4)} VP pas {clp(c['vp_pas'])} w {pct(c['w_b'],2)} montos {clp(c['monto_b'])} {clp(c['monto_a'])} nom bono {clp(c['nom_bono'])} cobro cero {clp(c['cobro_cero'])}")
    for r in c["mb"]["tabla"]:
        print(f"     t{r['t']} fd {fmt(r['fd'],6)} vp {fmt(r['vp'],4)} peso {pct(r['peso'],1)} tvp {fmt(r['tvp'],4)} cvp {fmt(r['cvp'],4)}")
    print(f"   Σtvp {fmt(c['mb']['suma_tvp'],4)} Σcvp {fmt(c['mb']['suma_cvp'],4)} conv cart {fmt(c['conv_cartera'],3)} conv pas {fmt(c['conv_pasivo'],3)}")
    for k in ("prueba", "todo_bono", "todo_cero"):
        print(f"   {k}: " + " ".join(f"{s:+} {clp(x)} ({clp(x - caso.U5['saldo_maquina'])})" for s, x in c[k].items()))
    for s, a in c["ap"].items():
        print(f"   bono {s:+}: solo D {pct(a['solo_d'],3)} con C {pct(a['con_c'],3)} exacto {pct(a['exacto'],3)}")


# ---------------------------------------------------------------- revisión contra el texto

def esperados(R):
    x = []
    e = R["ej"]; mb = e["mb"]
    x += [clp(e["vp_pas"]), fmt(mb["p"]), fmt(mb["d"], 4), fmt(mb["dmod"], 4), fmt(mb["conv"], 2), fmt(mb["suma_tvp"]),
          pct(e["w_b"]), pct(e["w_a"]), clp(e["monto_b"]), clp(e["monto_a"]), fmt(e["ma"]["p"]),
          fmt(e["conv_cartera"], 2), fmt(e["conv_pasivo"], 2)]
    x += [fmt(r["vp"]) for r in mb["tabla"]] + [fmt(r["tvp"]) for r in mb["tabla"]]
    for a in e["ap"].values():
        x += [pct(abs(a["solo_d"])), pct(abs(a["con_c"])), pct(abs(a["exacto"]))]
    for v in e["prueba"].values():
        x += [clp(z) for z in v.values()] + [clp(abs(z - EJ["pasivo"])) for s, z in v.items() if s]
    e = R["e1"]; m = e["m"]; a = e["ap"]
    x += [fmt(m["p"]), fmt(m["d"], 4), fmt(m["dmod"], 4), pct(-a["solo_d"], 3), fmt(a["p_d"]), pct(-a["exacto"], 3), fmt(a["p_exacto"])]
    x += [fmt(r["vp"]) for r in m["tabla"]] + [fmt(r["tvp"]) for r in m["tabla"]]
    e = R["e2"]; m = e["m"]; a = e["ap"]
    x += [fmt(m["p"]), fmt(m["dmod"], 4), pct(-a["solo_d"]), pct(-a["exacto"]), fmt(e["d_perp"]), fmt(e["dmod_perp"]),
          pct(-e["est_perp"]), pct(-e["exacto_perp"])]
    e = R["e3"]; x += [fmt(e["d"], 2), fmt(e["mover"], 2), fmt(e["nuevo_a"], 2), fmt(e["nuevo_c"], 2)]
    e = R["e5"]; m = e["m"]; a = e["ap"]
    x += [pct(e["ys"], 4), pct(e["ys2"], 4), fmt(100 * e["dys"], 4), fmt(m["p"]), fmt(m["d"], 4), fmt(e["d_anios"], 4), fmt(m["dmod"], 4),
          pct(-a["solo_d"]), fmt(a["p_d"]), pct(-a["exacto"]), fmt(a["p_exacto"])]
    e = R["e6"]; m = e["m"]
    x += [fmt(m["p"]), fmt(m["d"], 4), fmt(m["dmod"], 4), fmt(m["conv"], 2)]
    for a in e["ap"].values():
        x += [pct(abs(a["solo_d"])), pct(abs(a["con_c"])), pct(abs(a["exacto"])), fmt(a["p_d"]), fmt(a["p_c"]), fmt(a["p_exacto"])]
    e = R["e7"]; x += [fmt(e["dmod"], 4), fmt(e["conv_bala"], 2), fmt(e["conv_pesas"], 2)]
    for b, p in e["valores"].values():
        x += [clp(b), clp(p), clp(p - b)]
    e = R["e8"]
    x += [clp(e["vp_pas"]), fmt(e["mb"]["p"]), fmt(e["mb"]["d"], 4), fmt(e["ma"]["p"]), pct(e["w_b"]), pct(e["w_a"]),
          clp(e["monto_b"]), clp(e["monto_a"]), fmt(e["conv_cartera"], 2), fmt(e["conv_pasivo"], 2)]
    x += [clp(v) for v in e["prueba"].values()] + [clp(v - E8["pasivo"]) for s, v in e["prueba"].items() if s]
    e = R["e9"]
    x += [fmt(e["d_bono1"], 4), clp(e["va"]), clp(e["vb"]), clp(e["cupon_1"]), clp(e["tot1"]), fmt(e["d1"], 4),
          pct(e["wb_antes"]), pct(e["wb_nuevo"]), clp(e["monto_b_nuevo"]), clp(e["monto_a_nuevo"]),
          clp(e["torcida"]), clp(e["falta"]), clp(e["vb"] - e["monto_b_nuevo"]), clp(e["monto_a_nuevo"] - e["va"])]
    c = R["caso"]
    x += [pct(c["y"]), fmt(c["mb"]["d"], 4), fmt(c["mb"]["dmod"], 4), fmt(c["mb"]["conv"], 2), clp(c["vp_pas"]),
          pct(c["w_b"]), pct(c["w_a"]), clp(c["monto_b"]), clp(c["monto_a"]), clp(c["nom_bono"]), clp(c["cobro_cero"]),
          fmt(c["mb"]["suma_tvp"], 4), fmt(c["conv_cartera"], 2), fmt(c["conv_pasivo"], 2)]
    x += [fmt(r["vp"], 4) for r in c["mb"]["tabla"]] + [fmt(r["tvp"], 4) for r in c["mb"]["tabla"]]
    for k in ("prueba", "todo_bono", "todo_cero"):
        x += [clp(v) for v in c[k].values()]
    for a in c["ap"].values():
        x += [pct(abs(a["solo_d"])), pct(abs(a["exacto"]))]
    return x


def comparar_con_caso(R):
    """Lo que este script recalcula tiene que coincidir con el script del caso."""
    c, u8 = R["caso"], R["caso"]["u8"]
    pares = [(c["mb"]["d"], u8["duracion"]), (c["mb"]["dmod"], u8["duracion_mod"]), (c["mb"]["conv"], u8["convexidad"]),
             (c["vp_pas"], u8["vp_pasivo"]), (c["w_b"], u8["peso_bono"]), (c["monto_b"], u8["monto_bono"]),
             (c["monto_a"], u8["monto_cero"]), (c["prueba"][0], u8["en_H_sin_cambio"]),
             (c["prueba"][1], u8["en_H_sube_1pp"]), (c["prueba"][-1], u8["en_H_baja_1pp"])]
    for a, b in pares:
        assert abs(a - b) < 1e-6 * max(1, abs(b)), (a, b)


if __name__ == "__main__":
    R = resultados()
    comparar_con_caso(R)
    imprimir(R)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "08-duracion-e-inmunizacion.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".").replace("\\,\\%", " %")
        faltan = [x for x in esperados(R) if x not in md]
        print("\nREVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
