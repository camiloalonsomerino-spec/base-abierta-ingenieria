"""Caso integrador de Contabilidad y Costos · el mes de marzo de Estampa Sur.

El mismo taller ficticio de los otros ramos. Un solo mes, coherente de punta a punta: produce 5.590
prendas y vende 5.300 (plan y mezcla de Gestión de Operaciones), con los márgenes de contribución de
Optimización y la segunda máquina de Finanzas (pie y saldo a 3 años). Todo es ficticio, salvo la tasa
de IVA (19 %).

    python caso_estampa_sur_contable.py          # imprime la cadena
    python caso_estampa_sur_contable.py --json   # la deja en caso_estampa_sur_contable.json

Decisiones declaradas:
- Los costos por prenda usan precios ESTÁNDAR (polera lisa básica a $2.400, tinta a $16.500 el kg).
  La unidad 7 mide cuánto se aparta el costo real de las poleras lisas (FIFO o precio promedio) cuando
  la compra de marzo llega a $2.450: esa diferencia es una variación de precio.
- El estado de resultados (unidad 8) usa costeo por absorción, como pide la norma; la unidad 10 lo
  compara con el costeo variable.
"""
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import json, sys

sys.stdout.reconfigure(encoding="utf-8")
IVA = 0.19


def peso(x):
    """Redondeo a peso como en una factura: la mitad sube (Python, por defecto, redondea al par)."""
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

# ------------------------------------------------------------------ productos (Operaciones y Optimización)
PRODUCTOS = ["poleras básicas", "polerones", "poleras estampado doble", "bolsas", "gorros"]
PRECIO = [3_990, 9_890, 6_290, 2_490, 3_190]          # neto por unidad
MARGEN = [1_380, 3_940, 2_270, 960, 1_170]           # margen de contribución (Optimización)
PRENDA_LISA = [2_400, 5_400, 3_600, 1_350, 1_880]    # costo estándar de la prenda lisa
TINTA_G = [12, 25, 22, 8, 6]                         # gramos por unidad (Optimización)
SEG_EST = [30, 90, 110, 20, 30]                      # segundos de estampado (Operaciones)
TINTA_KG = 16_500                                    # estándar
PRODUCIDAS = [2_236, 839, 838, 1_006, 671]           # 5.590 = plan agregado, mes 1 (Operaciones)
VENDIDAS = [2_120, 795, 795, 954, 636]               # 5.300

# ------------------------------------------------------------------ U1 · balance al 1 de marzo
BALANCE_INICIAL = {
    "activo": {"Banco": 4_270_000, "Clientes": 1_180_000,
               "Poleras lisas básicas": 900 * 2_400, "Tinta": 12 * TINTA_KG,
               "Arriendo pagado por anticipado": 580_000,           # marzo, pagado en febrero
               "Maquinaria": 9_840_000, "Depreciación acumulada": -2_460_000},
    "pasivo": {"Proveedores": 1_340_000},
}

# ------------------------------------------------------------------ operaciones de marzo
COMPRA_POLERAS = {"unidades": 2_100, "precio": 2_450}               # a crédito
MAQUINA = {"neto": 14_300_000, "pie": 5_550_000}                     # Finanzas U5: saldo 8.750.000 a 3 años
PRESTAMO = {"monto": 6_400_000, "tasa_mensual": 0.0115, "cuotas": 24}
CONTADO_VENTAS = 0.60
SUELDOS = 2_880_000                                                  # 4 personas (Operaciones)
ARRIENDO_TRIMESTRE = 1_740_000                                       # abril a junio, pagado en marzo
SEGURO_ANUAL = 948_000
OTROS_FIJOS = 436_000                                                # administración: luz, internet y mantención (todos con IVA)
CONSUMO_POLERAS = [(1_100, "semana 2"), (1_136, "semana 4")]         # = poleras básicas producidas
TINTA_SOBRANTE_KG = 5                                                # se compra lo que falta y queda este stock

MAQUINAS = {
    "pulpo 6 (inicial)": {"costo": 9_840_000, "residual": 0, "vida_meses": 96},
    "segunda máquina": {"costo": 14_300_000, "residual": 1_800_000, "vida_meses": 60},   # residual de Finanzas
}


def calcular():
    C = {}
    a, p = BALANCE_INICIAL["activo"], BALANCE_INICIAL["pasivo"]
    C["u1"] = {"total_activo": sum(a.values()), "total_pasivo": sum(p.values()),
               "capital": sum(a.values()) - sum(p.values())}

    # materiales que exige la producción
    tinta_kg = sum(q * g for q, g in zip(PRODUCIDAS, TINTA_G)) / 1000
    compra_tinta_kg = tinta_kg - 12 + TINTA_SOBRANTE_KG
    otras_lisas = sum(q * c for q, c in zip(PRODUCIDAS[1:], PRENDA_LISA[1:]))
    ventas = sum(q * pr for q, pr in zip(VENDIDAS, PRECIO))

    # U2 y U3 · asientos (montos netos; el IVA va aparte)
    filas, ivad, ivac = [], 0.0, 0.0
    def asiento(n, glosa, debe, haber):
        assert abs(sum(debe.values()) - sum(haber.values())) < 1e-6, n
        filas.append({"n": n, "glosa": glosa, "debe": {k: round(v, 2) for k, v in debe.items()},
                      "haber": {k: round(v, 2) for k, v in haber.items()}})
    iva = lambda neto: peso(neto * IVA)        # cada documento se redondea a peso
    n1 = COMPRA_POLERAS["unidades"] * COMPRA_POLERAS["precio"]; ivac += iva(n1)
    asiento(1, "Compra de poleras lisas básicas a crédito", {"Poleras lisas básicas": n1, "IVA crédito fiscal": iva(n1)},
            {"Proveedores": n1 + iva(n1)})
    n2 = otras_lisas; ivac += iva(n2)
    asiento(2, "Compra de las otras prendas lisas a crédito", {"Otras prendas lisas": n2, "IVA crédito fiscal": iva(n2)},
            {"Proveedores": n2 + iva(n2)})
    n3 = peso(compra_tinta_kg * TINTA_KG); ivac += iva(n3)
    asiento(3, "Compra de tinta al contado", {"Tinta": n3, "IVA crédito fiscal": iva(n3)}, {"Banco": n3 + iva(n3)})
    n4 = MAQUINA["neto"]; ivac += iva(n4)
    asiento(4, "Compra de la segunda máquina", {"Maquinaria": n4, "IVA crédito fiscal": iva(n4)},
            {"Banco": MAQUINA["pie"] + iva(n4), "Documentos por pagar a largo plazo": n4 - MAQUINA["pie"]})
    asiento(5, "Préstamo bancario", {"Banco": PRESTAMO["monto"]}, {"Préstamo bancario": PRESTAMO["monto"]})
    ivad += iva(ventas)
    asiento(6, "Ventas del mes", {"Banco": peso((ventas + iva(ventas)) * CONTADO_VENTAS),
                                  "Clientes": (ventas + iva(ventas)) - peso((ventas + iva(ventas)) * CONTADO_VENTAS)},
            {"Ventas": ventas, "IVA débito fiscal": iva(ventas)})
    asiento(7, "Pago de sueldos", {"Sueldos": SUELDOS}, {"Banco": SUELDOS})
    asiento(8, "Arriendo de abril a junio pagado por anticipado", {"Arriendo pagado por anticipado": ARRIENDO_TRIMESTRE},
            {"Banco": ARRIENDO_TRIMESTRE})
    ivac += iva(SEGURO_ANUAL)
    asiento(9, "Seguro anual pagado al contado", {"Seguro pagado por anticipado": SEGURO_ANUAL,
                                                   "IVA crédito fiscal": iva(SEGURO_ANUAL)},
            {"Banco": SEGURO_ANUAL + iva(SEGURO_ANUAL)})
    asiento(10, "Pago a proveedores del saldo inicial", {"Proveedores": 1_340_000}, {"Banco": 1_340_000})
    asiento(11, "Cobro a clientes del saldo inicial", {"Banco": 1_180_000}, {"Clientes": 1_180_000})
    ivac += iva(OTROS_FIJOS)
    asiento(12, "Otros gastos fijos de administración", {"Gastos de administración": OTROS_FIJOS,
                                                          "IVA crédito fiscal": iva(OTROS_FIJOS)},
            {"Banco": OTROS_FIJOS + iva(OTROS_FIJOS)})
    C["u2"] = {"asientos": filas, "ventas_netas": ventas, "compra_tinta_kg": compra_tinta_kg, "otras_prendas_lisas": n2}
    C["u3"] = {"debito": ivad, "credito": ivac, "a_pagar": ivad - ivac if ivad > ivac else 0,
               "remanente": ivac - ivad if ivac > ivad else 0}

    # U4 · depreciación lineal mensual
    dep = {k: (m["costo"] - m["residual"]) / m["vida_meses"] for k, m in MAQUINAS.items()}
    C["u4"] = {"depreciacion_mensual": dep, "total_mes": sum(dep.values())}

    # U5 · ajustes: arriendo de marzo (del saldo inicial) y un mes de seguro
    C["u5"] = {"arriendo_devengado": 580_000, "seguro_devengado": SEGURO_ANUAL / 12,
               "arriendo_anticipado_al_31": ARRIENDO_TRIMESTRE, "seguro_anticipado_al_31": SEGURO_ANUAL * 11 / 12}

    # U6 · préstamo francés: interés del mes 1 se devenga al cierre
    i, n, P = PRESTAMO["tasa_mensual"], PRESTAMO["cuotas"], PRESTAMO["monto"]
    cuota = P * i / (1 - (1 + i) ** -n)
    C["u6"] = {"cuota": cuota, "interes_mes_1": P * i, "amortizacion_mes_1": cuota - P * i,
               "saldo_tras_cuota_1": P - (cuota - P * i), "interes_total": cuota * n - P}

    # U7 · tarjeta de poleras lisas básicas: FIFO y precio promedio ponderado
    lotes = [[900, 2_400], [COMPRA_POLERAS["unidades"], COMPRA_POLERAS["precio"]]]
    costo_fifo = 0
    for q, _ in CONSUMO_POLERAS:
        resta = q
        while resta:
            t = min(resta, lotes[0][0]); costo_fifo += t * lotes[0][1]; lotes[0][0] -= t; resta -= t
            if lotes[0][0] == 0: lotes.pop(0)
    consumo = sum(q for q, _ in CONSUMO_POLERAS)
    assert consumo == PRODUCIDAS[0]
    ppp = (900 * 2_400 + n1) / (900 + COMPRA_POLERAS["unidades"])
    C["u7"] = {"consumo": consumo, "costo_fifo": costo_fifo, "saldo_fifo": sum(q * c for q, c in lotes),
               "ppp": ppp, "costo_ppp": consumo * ppp, "saldo_ppp": (3_000 - consumo) * ppp,
               "costo_estandar": consumo * 2_400, "variacion_fifo": costo_fifo - consumo * 2_400,
               "variacion_ppp": consumo * ppp - consumo * 2_400}

    # U9 · clasificación y costo variable estándar por prenda
    cv = [pr - m for pr, m in zip(PRECIO, MARGEN)]
    otros_var = [c - pl - g * TINTA_KG / 1000 for c, pl, g in zip(cv, PRENDA_LISA, TINTA_G)]
    cif_fijos = SUELDOS + C["u4"]["total_mes"] + C["u5"]["seguro_devengado"] + C["u5"]["arriendo_devengado"]
    C["u9"] = {"costo_variable": cv, "otros_variables": otros_var, "cif_fijos_mes": cif_fijos,
               "gastos_admin": OTROS_FIJOS, "gasto_financiero": C["u6"]["interes_mes_1"]}

    # U11 · tasa de CIF fijo por segundo de estampado
    seg_total = sum(q * s for q, s in zip(PRODUCIDAS, SEG_EST))
    tasa = cif_fijos / seg_total
    cif_u = [tasa * s for s in SEG_EST]
    costo_abs = [c + x for c, x in zip(cv, cif_u)]
    C["u11"] = {"segundos_estampado_mes": seg_total, "tasa_por_segundo": tasa, "cif_por_prenda": cif_u,
                "costo_absorcion_por_prenda": costo_abs}

    # U10 · absorción contra variable (resultado operacional)
    cv_vendido = sum(q * c for q, c in zip(VENDIDAS, cv))
    abs_vendido = sum(q * c for q, c in zip(VENDIDAS, costo_abs))
    inv_final = [pq - vq for pq, vq in zip(PRODUCIDAS, VENDIDAS)]
    r_var = ventas - cv_vendido - cif_fijos - OTROS_FIJOS
    r_abs = ventas - abs_vendido - OTROS_FIJOS
    C["u10"] = {"resultado_variable": r_var, "resultado_absorcion": r_abs, "diferencia": r_abs - r_var,
                "inventario_final": inv_final, "cif_en_inventario": sum(q * x for q, x in zip(inv_final, cif_u))}
    assert abs((r_abs - r_var) - C["u10"]["cif_en_inventario"]) < 1e-6

    # U8 · estado de resultados (absorción) y razones con el balance inicial
    margen_bruto = ventas - abs_vendido
    r_op = margen_bruto - OTROS_FIJOS
    uai = r_op - C["u6"]["interes_mes_1"]
    C["u8"] = {"ventas": ventas, "costo_ventas": abs_vendido, "margen_bruto": margen_bruto,
               "resultado_operacional": r_op, "gastos_financieros": C["u6"]["interes_mes_1"],
               "utilidad_antes_impuesto": uai, "margen_neto": uai / ventas, "margen_bruto_pct": margen_bruto / ventas}

    # U12 · costo-volumen-utilidad con la mezcla de ventas
    q_tot = sum(VENDIDAS)
    mezcla = [q / q_tot for q in VENDIDAS]
    mcp = sum(m * mg for m, mg in zip(mezcla, MARGEN))
    fijos_op = cif_fijos + OTROS_FIJOS
    pe = fijos_op / mcp
    C["u12"] = {"mezcla": mezcla, "margen_ponderado": mcp, "costos_fijos_operacionales": fijos_op,
                "equilibrio_unidades": pe, "equilibrio_por_producto": [pe * m for m in mezcla],
                "equilibrio_pesos": pe * sum(m * pr for m, pr in zip(mezcla, PRECIO)),
                "margen_seguridad": (q_tot - pe) / q_tot,
                "apalancamiento_operativo": (q_tot * mcp) / (q_tot * mcp - fijos_op)}
    return C


if __name__ == "__main__":
    C = calcular()
    for k, v in C.items():
        if k == "u2":
            print(f"== u2: {len(v['asientos'])} asientos cuadrados · ventas {v['ventas_netas']:,.0f} · tinta comprada {v['compra_tinta_kg']:.2f} kg · otras lisas {v['otras_prendas_lisas']:,.0f}")
            continue
        print(f"== {k}")
        for kk, vv in v.items():
            if isinstance(vv, float): vv = round(vv, 4)
            if isinstance(vv, list): vv = [round(x, 4) if isinstance(x, float) else x for x in vv]
            if isinstance(vv, dict): vv = {a: round(b, 4) for a, b in vv.items()}
            print(f"   {kk}: {vv}")
    if "--json" in sys.argv:
        Path(__file__).with_suffix(".json").write_text(json.dumps(C, ensure_ascii=False, indent=1), encoding="utf-8")
