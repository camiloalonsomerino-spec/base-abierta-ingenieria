"""Unidad 3 · Cardinalidad, participación, entidades débiles y jerarquías.

Recalcula todas las cifras de la unidad; con --revisar las busca en el .md.

1. Los modelos (ejemplo, ejercicios y caso) están escritos como datos en mer.py; de ahí salen las
   tablas de relaciones con sus pares (mín, máx) que el .md tiene que traer fila por fila.
2. Recalcula los ejercicios con datos de ejemplares (3.5) y la trampa de conexión (sección 6 y 3.7).
3. Corre sql/u03_cardinalidad.sql sobre datos/estampa_sur.db (solo lectura) y exige que cada consulta
   y su tabla de resultado estén en el .md.
4. CADENA: la base del archivo es la que genera el script del caso, y ningún par medido contradice el
   par declarado en el diagrama.
5. Dibuja unidades/figuras/u03_veterinaria.svg y u03_estampa_sur.svg.

    python u03_cardinalidad.py            # imprime resultados y dibuja las figuras
    python u03_cardinalidad.py --revisar  # además revisa el .md
"""
from pathlib import Path
from itertools import product
import importlib.util, sqlite3, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
sys.path.insert(0, str(AQUI))
import mer  # noqa: E402
from mer import N  # noqa: E402

MD = RAMO / "unidades" / "03-cardinalidad-y-jerarquias.md"
SQL = RAMO / "sql" / "u03_cardinalidad.sql"
DB = RAMO / "datos" / "estampa_sur.db"
FIG = RAMO / "unidades" / "figuras"

# ---------------------------------------------------------------- datos (originales)
# Sección 6 · trampa de conexión con una ternaria mínima (laboratorio, vacuna, sede)
TERNARIA_MINI = [("L1", "V1", "S1"), ("L1", "V2", "S2"), ("L2", "V1", "S2")]

# 3.5 · centro cultural de Valdivia: pares declarados y ejemplares de INSCRIBE (alumno, taller)
E35 = {"alumnos": ["A1", "A2", "A3", "A4", "A5", "A6", "A7"], "talleres": ["T1", "T2", "T3", "T4"],
       "declarado": {"talleres_por_alumno": (1, 2), "alumnos_por_taller": (2, 15)},
       "pares": [("A1", "T1"), ("A1", "T2"), ("A2", "T1"), ("A3", "T2"), ("A3", "T3"), ("A3", "T4"),
                 ("A4", "T3"), ("A5", "T1"), ("A6", "T2")]}

# 3.7 · agricultores, ferias y productos (precio por kilo en pesos)
E37 = [("Rosa", "Chillán", "papas", 700), ("Rosa", "San Carlos", "frutillas", 2800),
       ("Luis", "Chillán", "frutillas", 2600), ("Luis", "San Carlos", "papas", 750),
       ("Rosa", "Chillán", "porotos verdes", 1900)]

# Qué par del diagrama mide cada consulta: (relación, entidad cuyo par se mide)
MIDE = {"c1_productos_por_pedido": ("detalle", "producto"), "c2_pedidos_por_producto": ("detalle", "pedido"),
        "c3_proveedores_por_producto": ("suministra", "proveedor"),
        "c4_productos_por_proveedor": ("suministra", "producto"),
        "c5_pedidos_por_cliente": ("hace", "pedido"), "e38_clientes_por_tienda": ("atiende", "cliente"),
        "e38_ordenes_por_producto": ("programa", "orden_produccion")}


# ---------------------------------------------------------------- cálculos
def recomponer(trios):
    """Proyecta una ternaria en sus tres binarias y vuelve a juntarlas (trampa de conexión)."""
    ab = {(a, b) for a, b, _ in trios}
    bc = {(b, c) for _, b, c in trios}
    ac = {(a, c) for a, _, c in trios}
    A_ = sorted({t[0] for t in trios}); B_ = sorted({t[1] for t in trios}); C_ = sorted({t[2] for t in trios})
    junto = {(a, b, c) for a, b, c in product(A_, B_, C_) if (a, b) in ab and (b, c) in bc and (a, c) in ac}
    falsas = sorted(junto - set(trios))
    return {"binarias": (len(ab), len(bc), len(ac)), "recompuestas": len(junto), "falsas": falsas}


def e35():
    d = E35
    por_alumno = {a: sum(1 for x, _ in d["pares"] if x == a) for a in d["alumnos"]}
    por_taller = {t: sum(1 for _, y in d["pares"] if y == t) for t in d["talleres"]}
    ma = (min(por_alumno.values()), max(por_alumno.values()))
    mt = (min(por_taller.values()), max(por_taller.values()))
    lo, hi = d["declarado"]["talleres_por_alumno"]
    lo2, hi2 = d["declarado"]["alumnos_por_taller"]
    viol = [f"{a} en {n} talleres" for a, n in por_alumno.items() if not lo <= n <= hi]
    viol += [f"{t} con {n} alumno" + ("s" if n != 1 else "") for t, n in por_taller.items() if not lo2 <= n <= hi2]
    return {"por_alumno": por_alumno, "por_taller": por_taller, "medido_alumno": ma, "medido_taller": mt,
            "violaciones": viol}


def e37():
    r = recomponer([(a, f, p) for a, f, p, _ in E37])
    # con la entidad OFERTA (una fila por trío) no se pierde nada: cada precio queda con su trío
    return {**r, "ofertas": len(E37)}


def caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_bd.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def base_en_memoria(m):
    """La base del caso reconstruida en memoria desde el script (sin tocar datos/estampa_sur.db)."""
    con = sqlite3.connect(":memory:")
    con.executescript(m.ESQUEMA)
    clientes, pedidos, detalle, ordenes = m.generar()
    con.executemany("INSERT INTO tienda VALUES (?,?,?)", m.TIENDAS)
    con.executemany("INSERT INTO producto VALUES (?,?,?,?,?)", m.PRODUCTOS)
    con.executemany("INSERT INTO proveedor VALUES (?,?,?)", m.PROVEEDORES)
    con.executemany("INSERT INTO suministra VALUES (?,?,?)", m.SUMINISTRA)
    con.executemany("INSERT INTO cliente VALUES (?,?,?,?)", clientes)
    con.executemany("INSERT INTO pedido VALUES (?,?,?,?)", pedidos)
    con.executemany("INSERT INTO detalle_pedido VALUES (?,?,?,?)", detalle)
    con.executemany("INSERT INTO orden_produccion VALUES (?,?,?,?)", ordenes)
    return con


def abrir_caso():
    if not DB.exists():
        sys.exit("Falta datos/estampa_sur.db: corre verificacion/caso_estampa_sur_bd.py")
    return sqlite3.connect(DB.as_uri() + "?mode=ro", uri=True)


def resultados():
    R = {"mini": recomponer(TERNARIA_MINI), "e35": e35(), "e37": e37()}
    assert R["mini"]["recompuestas"] == 4 and R["mini"]["falsas"] == [("L1", "V1", "S2")]
    con = abrir_caso()
    R["bloques"] = mer.bloques(SQL)
    R["sql"] = mer.correr(con, R["bloques"])
    con.close()
    return R


def cadena(R):
    m = caso()
    mem = base_en_memoria(m)
    con = abrir_caso()
    tablas = ["tienda", "producto", "proveedor", "suministra", "cliente", "pedido", "detalle_pedido", "orden_produccion"]
    iguales = all(sorted(con.execute(f"SELECT * FROM {t}").fetchall()) == sorted(mem.execute(f"SELECT * FROM {t}").fetchall())
                  for t in tablas)
    filas = sum(con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in tablas)
    # las mismas consultas sobre la base reconstruida dan lo mismo
    iguales &= mer.correr(mem, R["bloques"]) == R["sql"]
    # ningún par medido contradice el declarado
    modelo = mer.estampa_sur()
    lados = {(r["nombre"], e): p for r in modelo["relaciones"] for e, p in r["lados"]}
    contradice = []
    for q, (rel, ent) in MIDE.items():
        lo, hi = R["sql"][q][1][0]
        dlo, dhi = lados[(rel, ent)]
        if lo < dlo or (dhi != N and hi > dhi):
            contradice.append(q)
    con.close()
    ok = iguales and not contradice
    print("CADENA:", f"OK, la base del archivo es la del script ({len(tablas)} tablas, {filas} filas) y ningún par "
          f"medido contradice el diagrama ({len(MIDE)} pares medidos)" if ok else f"NO calza {contradice}")
    return ok


# ---------------------------------------------------------------- figuras
def fig_veterinaria():
    g = mer.Chen(1100, 650, nota="Pares (mín,máx) junto a cada entidad: cuántos de ESA entidad por uno del otro lado")
    g.entidad("personal", 160, 80, "PERSONAL")
    g.entidad("sede", 590, 80, "SEDE")
    g.relacion("trabaja_en", 375, 80, "TRABAJA_EN", tipo="1:N")
    g.entidad("tecnico", 75, 270, "TÉCNICO")
    g.entidad("veterinario", 250, 270, "VETERINARIO")
    g.es_un("isa", 160, 175, "personal", ["tecnico", "veterinario"], "disjunta, parcial")
    g.relacion("dirige", 440, 200, "DIRIGE", tipo="1:1")
    g.entidad("tutor", 95, 505, "TUTOR")
    g.relacion("pertenece", 265, 505, "PERTENECE", identificadora=True, tipo="1:N")
    g.entidad("mascota", 430, 505, "MASCOTA", debil=True)
    g.relacion("recibe", 590, 505, "RECIBE", tipo="1:N")
    g.entidad("atencion", 750, 505, "ATENCIÓN")
    g.relacion("realiza", 520, 370, "REALIZA", tipo="1:N")
    g.relacion("aplica", 900, 410, "APLICA", tipo="N:M")
    g.entidad("vacuna", 900, 290, "VACUNA")
    g.relacion("provee", 900, 170, "PROVEE", tipo="1:N:N", tipo_dx=42)
    g.entidad("laboratorio", 1020, 80, "LABORATORIO", w=140)
    # pares
    g.unir("sede", "trabaja_en", "sede", (1, 1))
    g.unir("personal", "trabaja_en", "personal", (1, N))
    g.unir("veterinario", "dirige", "veterinario", (1, 1))
    g.unir("sede", "dirige", "sede", (0, 1), lado=-1)
    g.unir("tutor", "pertenece", "tutor", (1, 1))
    g.unir("mascota", "pertenece", "mascota", (1, N))
    g.unir("mascota", "recibe", "mascota", (1, 1))
    g.unir("atencion", "recibe", "atencion", (0, N))
    g.unir("veterinario", "realiza", "veterinario", (1, 1), lado=-1)
    g.unir("atencion", "realiza", "atencion", (0, N))
    g.unir("atencion", "aplica", "atencion", (0, N), lado=-1)
    g.unir("vacuna", "aplica", "vacuna", (0, N))
    g.unir("laboratorio", "provee", "laboratorio", (0, 1))
    g.unir("vacuna", "provee", "vacuna", (0, N))
    g.unir("sede", "provee", "sede", (0, N))
    # atributos
    g.atributo("a_rut", 70, 25, "rut", "personal", "clave")
    g.atributo("a_ingreso", 255, 25, "fecha_ingreso", "personal")
    g.atributo("a_cod", 700, 30, "cod_sede", "sede", "clave")
    g.atributo("a_turno", 75, 345, "turno", "tecnico")
    g.atributo("a_col", 250, 345, "colegiatura", "veterinario")
    g.atributo("a_ruttu", 70, 435, "rut_tutor", "tutor", "clave")
    g.atributo("a_tel", 190, 440, "telefono", "tutor", "multi")
    g.atributo("a_dir", 95, 575, "direccion", "tutor")
    g.atributo("a_calle", 40, 620, "calle", "a_dir")
    g.atributo("a_num", 125, 620, "numero", "a_dir")
    g.atributo("a_com", 210, 620, "comuna", "a_dir")
    g.atributo("a_nom", 380, 580, "nombre", "mascota", "parcial")
    g.atributo("a_esp", 480, 580, "especie", "mascota")
    g.atributo("a_numat", 710, 580, "num_atencion", "atencion", "clave")
    g.atributo("a_fecha", 820, 580, "fecha", "atencion")
    g.atributo("a_lote", 1030, 410, "lote", "aplica")
    g.atributo("a_codv", 1030, 290, "cod_vacuna", "vacuna", "clave")
    g.atributo("a_precio", 775, 225, "precio", "provee")
    g.atributo("a_rutlab", 1020, 25, "rut_lab", "laboratorio", "clave")
    return g.svg()


def fig_estampa_sur():
    g = mer.Chen(1100, 560, nota="Estampa Sur · pares (mín,máx) junto a cada entidad: cuántos de ESA entidad por uno del otro lado")
    g.entidad("tienda", 90, 90, "TIENDA")
    g.relacion("atiende", 265, 90, "ATIENDE", tipo="1:N")
    g.entidad("cliente", 450, 90, "CLIENTE")
    g.relacion("hace", 630, 90, "HACE", tipo="1:N")
    g.entidad("pedido", 820, 90, "PEDIDO")
    g.relacion("detalle", 820, 225, "DETALLE", tipo="N:M", tipo_dx=-38)
    g.entidad("producto", 820, 360, "PRODUCTO")
    g.relacion("suministra", 600, 360, "SUMINISTRA", tipo="N:M", tipo_dx=-45)
    g.entidad("proveedor", 390, 360, "PROVEEDOR")
    g.relacion("programa", 820, 470, "PROGRAMA", tipo="1:N")
    g.entidad("orden", 1000, 470, "ORDEN_PRODUCCION", w=170)
    for k, x in (("colegio", 210), ("club", 340), ("empresa", 470), ("persona", 600)):
        g.entidad(k, x, 250, k.upper(), w=110)
    g.es_un("isa", 450, 170, "cliente", ["colegio", "club", "empresa", "persona"], "disjunta, total (tipo)")
    g.unir("tienda", "atiende", "tienda", (1, 1))
    g.unir("cliente", "atiende", "cliente", (0, N))
    g.unir("cliente", "hace", "cliente", (1, 1))
    g.unir("pedido", "hace", "pedido", (0, N))
    g.unir("pedido", "detalle", "pedido", (0, N))
    g.unir("producto", "detalle", "producto", (1, N))
    g.unir("proveedor", "suministra", "proveedor", (1, N))
    g.unir("producto", "suministra", "producto", (0, N))
    g.unir("producto", "programa", "producto", (1, 1))
    g.unir("orden", "programa", "orden", (0, N), lado=-1)
    g.atributo("k_t", 90, 30, "id_tienda", "tienda", "clave")
    g.atributo("k_c", 450, 30, "id_cliente", "cliente", "clave")
    g.atributo("k_p", 820, 30, "id_pedido", "pedido", "clave")
    g.atributo("k_pr", 960, 330, "id_producto", "producto", "clave")
    g.atributo("k_pv", 390, 425, "id_proveedor", "proveedor", "clave")
    g.atributo("k_o", 1000, 530, "id_orden", "orden", "clave")
    g.atributo("cant", 975, 200, "cantidad", "detalle")
    g.atributo("pu", 975, 250, "precio_unit", "detalle")
    g.atributo("cu", 600, 425, "costo_unidad", "suministra")
    return g.svg()


# ---------------------------------------------------------------- revisión
def esperados(R):
    s = []
    for f in (mer.veterinaria, mer.estampa_sur, mer.feria, mer.consultorio, mer.liga):
        s += mer.filas_relaciones(f())
    mi = R["mini"]
    s += [f"{mi['recompuestas']} tríos", "(L1, V1, S2)"]
    e = R["e35"]
    s += [f"talleres por alumno medido: {mer.par(e['medido_alumno'])}", f"alumnos por taller medido: {mer.par(e['medido_taller'])}"]
    s += e["violaciones"]
    s += [f"| {a} | {n} |" for a, n in e["por_alumno"].items()] + [f"| {t} | {n} |" for t, n in e["por_taller"].items()]
    e = R["e37"]
    s += [f"{e['recompuestas']} tríos", f"{len(e['falsas'])} falsos"] + [f"({a}, {f}, {p})" for a, f, p in e["falsas"]]
    s += [mer.fmt(p) for *_, p in E37]
    s += ["u03_veterinaria.svg", "u03_estampa_sur.svg"]
    return s


if __name__ == "__main__":
    R = resultados()
    print("== trampa de conexión (sección 6):", R["mini"])
    print("== 3.5:", R["e35"])
    print("== 3.7:", R["e37"])
    for k, v in R["sql"].items():
        print(f"== {k}: {v}")
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "u03_veterinaria.svg").write_text(fig_veterinaria(), encoding="utf-8")
    (FIG / "u03_estampa_sur.svg").write_text(fig_estampa_sur(), encoding="utf-8")
    print("FIGURAS: u03_veterinaria.svg y u03_estampa_sur.svg")
    if not cadena(R):
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        md_plano = " ".join(md_n.split())
        faltan = [x for x in esperados(R) if x not in md_plano]
        faltan += mer.revisar_sql(md, R["bloques"], R["sql"])
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
