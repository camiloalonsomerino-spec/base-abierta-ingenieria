"""Unidad 4 · Del modelo entidad-relación al modelo relacional.

Recalcula todas las cifras de la unidad; con --revisar las busca en el .md.

1. Aplica las reglas R1 a R8 (mer.mapear) a cada diagrama de la unidad: el ejemplo, los ejercicios y
   el caso. Las tablas derivadas, en notación `tabla(col PK, col FK→ref, col?)`, tienen que estar en el .md.
2. Corre sql/u04_mer_a_relacional.sql en una base en memoria y exige que el esquema derivado del
   diagrama coincida con el que crea el script (columnas con tipo, NOT NULL, PK, FK y UNIQUE), que cada
   consulta esté en el .md con su resultado y cada error con su mensaje.
3. CADENA: el esquema derivado del diagrama de Estampa Sur (unidad 3) coincide con el del script del caso
   y con datos/esquema.sql; corre sql/u04_caso_estampa_sur.sql en una copia en memoria de la base.
4. Recalcula el costo de las estrategias de jerarquía del ejercicio 4.7 y lo confirma en SQLite.
5. Dibuja unidades/figuras/u04_veterinaria.svg y u04_estampa_sur.svg.

    python u04_mer_a_relacional.py            # imprime resultados y dibuja las figuras
    python u04_mer_a_relacional.py --revisar  # además revisa el .md
"""
from pathlib import Path
import importlib.util, sqlite3, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
sys.path.insert(0, str(AQUI))
import mer  # noqa: E402
from mer import A, C, M, D, N  # noqa: E402

MD = RAMO / "unidades" / "04-mer-a-relacional.md"
SQL = RAMO / "sql" / "u04_mer_a_relacional.sql"
SQL_CASO = RAMO / "sql" / "u04_caso_estampa_sur.sql"
DB = RAMO / "datos" / "estampa_sur.db"
ESQUEMA_SQL = RAMO / "datos" / "esquema.sql"
FIG = RAMO / "unidades" / "figuras"

VET = ["sede", "personal", "veterinario", "tecnico", "tutor", "telefono_tutor", "mascota", "atencion",
       "vacuna", "aplica", "laboratorio", "provee"]


# ---------------------------------------------------------------- modelos de los ejercicios (originales)
def club_montana():
    """4.2 · club de montaña de Coyhaique."""
    return {"entidades": {"socio": {"nombre": "socio", "clave": ["rut"], "atributos": [
        A("rut", "VARCHAR(12)"), A("nombre", "VARCHAR(60)"),
        C("direccion", [A("calle", "VARCHAR(40)"), A("numero", "INTEGER"), A("comuna", "VARCHAR(30)")]),
        M("correo", "VARCHAR(60)", "correo_socio"), A("fecha_nac", "DATE"), D("edad")]}},
        "relaciones": []}


def futbolito():
    """4.3 · liga de futbolito de Valparaíso."""
    return {"entidades": {
        "equipo": {"nombre": "equipo", "clave": ["id_equipo"], "atributos": [A("id_equipo", "INTEGER"), A("nombre", "VARCHAR(40)")]},
        "jugador": {"nombre": "jugador", "clave": ["id_jugador"], "atributos": [
            A("id_jugador", "INTEGER"), A("nombre", "VARCHAR(60)"), A("fecha_nac", "DATE")]},
        "partido": {"nombre": "partido", "clave": ["id_partido"], "atributos": [
            A("id_partido", "INTEGER"), A("fecha", "DATE"), A("cancha", "VARCHAR(40)")]}},
        "relaciones": [
            {"nombre": "juega_en", "lados": [("equipo", (1, 1)), ("jugador", (1, N))],
             "atributos": [A("numero_camiseta", "INTEGER")]},
            {"nombre": "local", "lados": [("equipo", (1, 1)), ("partido", (0, N))], "columnas": {"equipo": ["id_local"]}},
            {"nombre": "visita", "lados": [("equipo", (1, 1)), ("partido", (0, N))], "columnas": {"equipo": ["id_visita"]}},
            {"nombre": "participa", "tabla": "participa", "lados": [("jugador", (0, N)), ("partido", (0, N))],
             "atributos": [A("goles", "INTEGER"), A("minutos", "INTEGER")]}]}


def cooperativa():
    """4.5 · créditos y cuotas (la cuota es débil)."""
    return {"entidades": {
        "credito": {"nombre": "credito", "clave": ["num_credito"], "atributos": [
            A("num_credito", "INTEGER"), A("monto", "INTEGER"), A("plazo", "INTEGER")]},
        "cuota": {"nombre": "cuota", "clave": ["numero"], "debil_de": ("credito", "tiene", (1, 1), (1, N)),
                  "atributos": [A("numero", "INTEGER"), A("vence", "DATE"), A("monto", "INTEGER")]}},
        "relaciones": []}


def ferias_nuble(par_feria):
    """4.8 · la ternaria LLEVA con dos reglas distintas para la feria."""
    ent = lambda n: {"nombre": n, "clave": [f"id_{n}"], "atributos": [A(f"id_{n}", "INTEGER"), A("nombre", "VARCHAR(40)")]}
    return {"entidades": {n: ent(n) for n in ("agricultor", "feria", "producto")},
            "relaciones": [{"nombre": "lleva", "tabla": "lleva",
                            "lados": [("agricultor", (0, N)), ("feria", par_feria), ("producto", (0, N))],
                            "atributos": [A("precio_kg", "INTEGER")]}]}


EJERCICIOS = {"4.1": mer.feria, "4.2": club_montana, "4.3": futbolito, "4.4": mer.consultorio,
              "4.5": cooperativa, "4.8a": lambda: ferias_nuble((0, N)), "4.8b": lambda: ferias_nuble((0, 1)),
              "4.9": mer.liga}

# 4.7 · centro deportivo de Rancagua: cuántas personas hay de cada clase
E47 = {"personas": 54, "socios": 43, "monitores": 8, "ambos": 3,
       "attrs_socio": ["fecha_alta", "plan"], "attrs_monitor": ["certificacion", "valor_hora"]}


# ---------------------------------------------------------------- de las tablas al diagrama (4.10)
def inverso(T):
    """Lee un esquema y dice de qué construcción del diagrama sale cada tabla y cada clave foránea."""
    out = []
    for n, t in T.items():
        pk = set(t["pk"])
        fkcols = {c for cols, _, _ in t["fks"] for c in cols}
        nn = {c[0] for c in t["cols"] if c[2]}
        unicos = {frozenset(u) for u in t["unicos"]}
        ident = [f for f in t["fks"] if set(f[0]) < pk and not (pk - set(f[0])) <= fkcols]
        if len(t["fks"]) >= 2 and pk and pk <= fkcols:
            refs = [r for _, r, _ in t["fks"]]
            extra = [c[0] for c in t["cols"] if c[0] not in fkcols]
            clase = "relación N:M" if len(refs) == 2 else "relación ternaria"
            out.append(f"{n}: {clase} entre {' y '.join(refs)}" + (f", con atributos {', '.join(extra)}" if extra else ""))
            continue
        if ident:
            cols, ref, _ = ident[0]
            out.append(f"{n}: entidad débil de {ref}, clave parcial {', '.join(sorted(pk - set(cols)))}")
        else:
            out.append(f"{n}: entidad fuerte")
        for cols, ref, _ in t["fks"]:
            if ident and cols == ident[0][0]:
                continue
            uno = frozenset(cols) in unicos
            mn = 1 if set(cols) <= nn else 0
            out.append(f"{n} → {ref}: {'1:1' if uno else '1:N'}, ({mn},1) junto a {ref.upper()}")
    return out


# ---------------------------------------------------------------- cálculos
def e47():
    d = E47
    solo_s, solo_m = d["socios"] - d["ambos"], d["monitores"] - d["ambos"]
    ninguno = d["personas"] - (d["socios"] + d["monitores"] - d["ambos"])
    nulos_s = len(d["attrs_socio"]) * (d["personas"] - d["socios"])
    nulos_m = len(d["attrs_monitor"]) * (d["personas"] - d["monitores"])
    R = {"solo_socio": solo_s, "solo_monitor": solo_m, "ninguno": ninguno,
         "A_tablas": 3, "A_filas": d["personas"] + d["socios"] + d["monitores"], "A_nulos": 0,
         "C_tablas": 1, "C_filas": d["personas"], "C_nulos_socio": nulos_s, "C_nulos_monitor": nulos_m,
         "C_nulos": nulos_s + nulos_m, "B_filas": d["socios"] + d["monitores"], "B_repetidas": d["ambos"],
         "B_sin_lugar": ninguno}
    # segundo camino: construir la tabla única en SQLite y contar los nulos con SQL
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE persona_c (rut INTEGER PRIMARY KEY, es_socio INTEGER NOT NULL, es_monitor INTEGER NOT NULL,"
                " fecha_alta DATE, plan VARCHAR(10), certificacion VARCHAR(20), valor_hora INTEGER)")
    filas = []
    for i in range(d["personas"]):
        s = i < d["socios"]
        m = d["socios"] - d["ambos"] <= i < d["socios"] - d["ambos"] + d["monitores"]
        filas.append((i, int(s), int(m), "2026-03-01" if s else None, "mensual" if s else None,
                      "nivel 1" if m else None, 9000 if m else None))
    con.executemany("INSERT INTO persona_c VALUES (?,?,?,?,?,?,?)", filas)
    q = con.execute("SELECT SUM(es_socio), SUM(es_monitor), SUM(es_socio * es_monitor), COUNT(*) - COUNT(fecha_alta) + "
                    "COUNT(*) - COUNT(plan) + COUNT(*) - COUNT(certificacion) + COUNT(*) - COUNT(valor_hora) FROM persona_c").fetchone()
    assert q == (d["socios"], d["monitores"], d["ambos"], R["C_nulos"]), q
    return R


def caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_bd.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def copia_caso(m):
    con = sqlite3.connect(":memory:", isolation_level=None)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(m.ESQUEMA)
    clientes, pedidos, detalle, ordenes = m.generar()
    for t, filas in (("tienda", m.TIENDAS), ("producto", m.PRODUCTOS), ("proveedor", m.PROVEEDORES),
                     ("suministra", m.SUMINISTRA), ("cliente", clientes), ("pedido", pedidos),
                     ("detalle_pedido", detalle), ("orden_produccion", ordenes)):
        con.executemany(f"INSERT INTO {t} VALUES ({','.join('?' * len(filas[0]))})", filas)
    return con


def resultados():
    R = {}
    # el ejemplo: derivado del diagrama contra el script
    con = sqlite3.connect(":memory:", isolation_level=None)
    con.execute("PRAGMA foreign_keys = ON")
    R["bloques"] = mer.bloques(SQL)
    R["sql"] = mer.correr(con, R["bloques"])
    real = mer.leer_esquema(con)
    R["vet"] = mer.mapear(mer.veterinaria("A"))
    R["dif_vet"] = mer.comparar(R["vet"], real, tablas=VET)
    R["vet_C"] = mer.mapear(mer.veterinaria("C"))
    pc = dict(real["personal_una_tabla"]); pc["nombre"] = "personal"
    R["dif_vet_C"] = mer.comparar({"personal": R["vet_C"]["personal"]}, {"personal": pc})
    R["coop"] = mer.mapear(cooperativa())
    R["dif_coop"] = mer.comparar(R["coop"], real, tablas=["credito", "cuota"])
    try:
        mer.mapear(mer.veterinaria("B"))
        R["vet_B"] = "se pudo"
    except ValueError as e:
        R["vet_B"] = str(e)
    R["orden_vet"] = mer.orden_creacion(R["vet"])
    # ejercicios
    R["ej"] = {k: mer.mapear(f()) for k, f in EJERCICIOS.items()}
    R["e47"] = e47()
    bib = ["socio", "carnet", "autor", "libro", "escribe", "ejemplar", "prestamo"]
    R["e410"] = inverso({k: real[k] for k in bib})
    con.close()
    return R


def cadena(R):
    m = caso()
    derivado = mer.mapear(mer.estampa_sur())
    mem = sqlite3.connect(":memory:"); mem.executescript(m.ESQUEMA)
    dif_script = mer.comparar(derivado, mer.leer_esquema(mem))
    arch = sqlite3.connect(":memory:"); arch.executescript(ESQUEMA_SQL.read_text(encoding="utf-8"))
    dif_archivo = mer.comparar(derivado, mer.leer_esquema(arch))
    texto_igual = ESQUEMA_SQL.read_text(encoding="utf-8") == m.ESQUEMA.strip() + "\n"
    # el orden del script es un orden válido de creación (cada tabla después de las que referencia)
    real = mer.leer_esquema(mem)
    vistas, orden_ok = set(), True
    for t in real:
        orden_ok &= {ref for _, ref, _ in real[t]["fks"]} <= vistas
        vistas.add(t)
    R["caso"] = derivado
    R["orden_script"] = list(real)
    R["orden_caso"] = mer.orden_creacion(derivado)
    # consultas del caso: las dos primeras sobre el archivo (solo lectura) y todo sobre una copia en memoria
    bs = mer.bloques(SQL_CASO)
    copia = copia_caso(m)
    R["bloques_caso"], R["sql_caso"] = bs, mer.correr(copia, bs)
    ro = sqlite3.connect(DB.as_uri() + "?mode=ro", uri=True)
    iguales = all(ro.execute(b["sql"]).fetchall() == R["sql_caso"][b["nombre"]][1] for b in bs[:2])
    ro.close()
    ok = not dif_script and not dif_archivo and texto_igual and orden_ok and iguales
    s = mer.resumen(derivado)
    print("ESQUEMA:", f"OK, las {s['tablas']} tablas derivadas del diagrama coinciden con el script y con datos/esquema.sql "
          f"({s['columnas']} columnas con tipo y NOT NULL, {s['tablas']} claves primarias, {s['fks']} claves foráneas, UNIQUE)"
          if ok else f"NO calza: {dif_script} {dif_archivo} texto={texto_igual} orden={orden_ok} consultas={iguales}")
    print("CADENA:", "OK, el diagrama de la unidad 3 da el esquema del caso" if ok else "NO calza")
    return ok


# ---------------------------------------------------------------- figuras
def fig_veterinaria(T):
    x = lambda k: 30 + 220 * k
    pos = {"tecnico": (x(0), 20), "personal": (x(1), 20), "sede": (x(2), 20), "provee": (x(3), 20),
           "laboratorio": (x(4), 20), "veterinario": (x(1), 200), "atencion": (x(2), 200), "aplica": (x(3), 200),
           "vacuna": (x(4), 200), "telefono_tutor": (x(0), 375), "tutor": (x(1), 375), "mascota": (x(2), 375)}
    return mer.svg_tablas(T, pos, 1120, 520, w=180,
                          nota="Clínica veterinaria · 12 tablas · cada flecha va de la clave foránea a la clave primaria")


def fig_estampa_sur(T):
    x = lambda k: 20 + 250 * k
    pos = {"tienda": (x(0), 20), "cliente": (x(1), 20), "pedido": (x(2), 20), "detalle_pedido": (x(3), 20),
           "proveedor": (x(0), 190), "suministra": (x(1), 190), "producto": (x(2), 190), "orden_produccion": (x(3), 190)}
    return mer.svg_tablas(T, pos, 980, 345, w=190,
                          nota="Estampa Sur · las 8 tablas del script con sus 7 claves foráneas")


# ---------------------------------------------------------------- revisión
def esperados(R):
    s = []
    for T in [R["vet"], R["caso"]] + list(R["ej"].values()):
        s += [mer.linea(t) for t in T.values()]
    s.append(mer.linea(R["vet_C"]["personal"]))
    for clave, T in (("vet", R["vet"]), ("caso", R["caso"]), ("4.1", R["ej"]["4.1"]), ("4.9", R["ej"]["4.9"])):
        r = mer.resumen(T)
        s += [f"{r['tablas']} tablas", f"{r['fks']} claves foráneas"]
    s.append(f"{mer.resumen(R['caso'])['columnas']} columnas")
    s.append(", ".join(R["orden_script"]))
    e = R["e47"]
    s += [f"{e['A_filas']} filas", f"{e['C_nulos_socio']} nulos", f"{e['C_nulos_monitor']} nulos", f"{e['C_nulos']} celdas nulas",
          f"{e['B_filas']} filas", f"{e['ninguno']} personas", f"{e['solo_socio']} solo socios", f"{e['solo_monitor']} solo monitores"]
    s += R["e410"]
    s += ["u04_veterinaria.svg", "u04_estampa_sur.svg"]
    return s


if __name__ == "__main__":
    R = resultados()
    for T, nombre in ((R["vet"], "ejemplo"),):
        print(f"== {nombre} ({mer.resumen(T)})")
        for t in T.values():
            print("  ", mer.linea(t), "·", t["origen"], t["origen_fk"])
    print("== estrategia C:", mer.linea(R["vet_C"]["personal"]))
    print("== estrategia B:", R["vet_B"])
    print("== orden de creación del ejemplo:", R["orden_vet"])
    for k, T in R["ej"].items():
        print(f"== {k} ({mer.resumen(T)})")
        for t in T.values():
            print("  ", mer.linea(t))
    print("== 4.7:", R["e47"])
    print("== 4.10:"); [print("  ", l) for l in R["e410"]]
    for k, v in R["sql"].items():
        print(f"== {k}: {v}")
    dif = R["dif_vet"] + R["dif_vet_C"] + R["dif_coop"]
    print("EJEMPLO:", "OK, las 12 tablas del script son las que salen del diagrama (y la tabla única y las cuotas)" if not dif else f"NO calza: {dif}")
    FIG.mkdir(parents=True, exist_ok=True)
    ok = cadena(R)
    for k, v in R["sql_caso"].items():
        print(f"== {k}: {v}")
    (FIG / "u04_veterinaria.svg").write_text(fig_veterinaria(R["vet"]), encoding="utf-8")
    (FIG / "u04_estampa_sur.svg").write_text(fig_estampa_sur(R["caso"]), encoding="utf-8")
    print("FIGURAS: u04_veterinaria.svg y u04_estampa_sur.svg")
    if dif or not ok:
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = " ".join(md.replace("{,}", ",").replace("{.}", ".").split())
        faltan = [x for x in esperados(R) if x not in md_n]
        faltan += mer.revisar_sql(md, R["bloques"], R["sql"])
        faltan += mer.revisar_sql(md, R["bloques_caso"], R["sql_caso"])
        faltan += [f"datos {b['nombre']}" for b in R["bloques_caso"] if b["clase"] == "datos"
                   and " ".join(b["sql"].split()) not in md_n]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
