"""Herramientas de las unidades 3 y 4 de Bases de Datos.

Un modelo entidad-relación escrito como datos, las reglas de paso al modelo relacional, la lectura del
esquema real de una base SQLite (PRAGMA), la ejecución de los scripts de `sql/` con su revisión en el
.md, y los dibujos SVG: notación de Chen para el modelo conceptual y tablas con claves para el
relacional.

Convención de cardinalidad de la base («mirar al frente»): el par (mín, máx) escrito junto a una
entidad E en una relación dice cuántos ejemplares de E se relacionan con UN ejemplar de la otra
entidad (en una ternaria, con un par de ejemplares de las otras dos).
"""
from pathlib import Path
import html, math, re, sqlite3

N = "N"
TINTA, SUAVE, LINEA, PAPEL, ACENTO = "#2B2F33", "#5F656B", "#D6D3CE", "#F2F1EF", "#E2622A"


# =============================================================== formato chileno
def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def valor(v):
    """Cómo se escribe un valor de una fila de resultado en el .md."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return str(int(v))
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if abs(v - round(v)) < 1e-9:
            return valor(int(round(v)))
        return fmt(v, 2)
    return str(v)


def par(p):
    return f"({p[0]},{p[1]})"


# =============================================================== el modelo como datos
def A(nombre, tipo, nulo=False, unico=False):
    """Atributo simple."""
    return {"clase": "simple", "nombre": nombre, "tipo": tipo, "nulo": nulo, "unico": unico}


def C(nombre, partes):
    """Atributo compuesto: se guarda en sus partes."""
    return {"clase": "compuesto", "nombre": nombre, "partes": partes}


def M(nombre, tipo, tabla):
    """Atributo multivaluado: va a una tabla propia."""
    return {"clase": "multi", "nombre": nombre, "tipo": tipo, "tabla": tabla}


def D(nombre):
    """Atributo derivado: se calcula, no se guarda."""
    return {"clase": "derivado", "nombre": nombre}


def muchos(p):
    """El máximo de un par es «muchos» si es N o un número mayor que 1."""
    return p[1] == N or p[1] > 1


def tipo_binaria(p1, p2):
    """Tipo de correspondencia escrito con el «1» primero cuando hay uno."""
    a, b = ("N" if muchos(p1) else "1"), ("N" if muchos(p2) else "1")
    if a == b == "N":
        return "N:M"
    return f"{a}:{b}"


def filas_relaciones(mer, mayus=True):
    """Filas «| relación | entidades | par | par | tipo |» de la tabla de relaciones de una unidad."""
    filas = []
    vista = {"atencion": "ATENCIÓN", "tecnico": "TÉCNICO", "medico": "MÉDICO", "arbitro": "ÁRBITRO",
             "orden_produccion": "ORDEN_PRODUCCIÓN"}
    nom = (lambda s: vista.get(s, s.upper())) if mayus else (lambda s: s)
    for e in mer["entidades"].values():
        if e.get("debil_de"):
            dueño, rel, p_dueño, p_debil = e["debil_de"]
            filas.append(f"| {nom(rel)} (identificadora) | {nom(dueño)} — {nom(e['nombre'])} | "
                         f"{par(p_dueño)} junto a {nom(dueño)} | {par(p_debil)} junto a {nom(e['nombre'])} | "
                         f"{tipo_binaria(p_dueño, p_debil)} |")
    for r in mer["relaciones"]:
        (e1, p1), (e2, p2) = r["lados"][:2]
        if len(r["lados"]) == 2:
            filas.append(f"| {nom(r['nombre'])} | {nom(e1)} — {nom(e2)} | {par(p1)} junto a {nom(e1)} | "
                         f"{par(p2)} junto a {nom(e2)} | {tipo_binaria(p1, p2)} |")
        else:
            e3, p3 = r["lados"][2]
            t = ":".join("N" if muchos(p) else "1" for _, p in r["lados"])
            filas.append(f"| {nom(r['nombre'])} (ternaria) | {nom(e1)} — {nom(e2)} — {nom(e3)} | "
                         f"{par(p1)} junto a {nom(e1)} | {par(p2)} junto a {nom(e2)}; {par(p3)} junto a {nom(e3)} | {t} |")
    return filas


# =============================================================== reglas de paso al relacional
REGLAS = {
    "R1": "entidad fuerte", "R2": "entidad débil", "R3": "relación 1:N", "R4": "relación 1:1",
    "R5": "relación N:M", "R6": "atributo multivaluado", "R7": "relación ternaria", "R8": "jerarquía",
}


def _cols_de(atributos, forzar_nulo=False):
    cols, unicos = [], []
    for a in atributos:
        if a["clase"] == "simple":
            cols.append([a["nombre"], a["tipo"], not (a["nulo"] or forzar_nulo)])
            if a.get("unico"):
                unicos.append((a["nombre"],))
        elif a["clase"] == "compuesto":
            for p in a["partes"]:
                cols.append([p["nombre"], p["tipo"], not (p["nulo"] or forzar_nulo)])
    return cols, unicos


def mapear(mer):
    """Aplica las reglas R1 a R8. Devuelve {tabla: {...}} en orden de creación y las notas de origen."""
    ents = mer["entidades"]
    jer = {j["super"]: j for j in mer.get("jerarquias", [])}
    sub_de = {s: j for j in mer.get("jerarquias", []) for s in j["subtipos"]}
    T = {}

    def tabla(nombre, origen):
        T[nombre] = {"nombre": nombre, "cols": [], "pk": [], "fks": [], "unicos": [], "origen": origen,
                     "origen_fk": []}
        return T[nombre]

    def destino(entidad):
        """Tabla a la que apunta una referencia a la entidad (en la estrategia C, el supertipo)."""
        j = sub_de.get(entidad)
        if j and j["estrategia"] == "C":
            return j["super"]
        if entidad in jer and jer[entidad]["estrategia"] == "B":
            raise ValueError(f"con la estrategia B no existe la tabla {entidad}: no se le puede apuntar")
        return entidad

    def tipo_col(t, col):
        return next(c[1] for c in T[t]["cols"] if c[0] == col)

    def agregar_fk(t, ref, nombres, nonull, regla, unico=False):
        ref_t = destino(ref)
        refcols = T[ref_t]["pk"]
        nombres = nombres or list(refcols)
        for n, rc in zip(nombres, refcols):
            if not any(c[0] == n for c in T[t]["cols"]):
                T[t]["cols"].append([n, tipo_col(ref_t, rc), nonull])
        T[t]["fks"].append((tuple(nombres), ref_t, tuple(refcols)))
        T[t]["origen_fk"].append(regla)
        if unico:
            T[t]["unicos"].append(tuple(nombres))
        return nombres

    # R1 · entidades fuertes (y R8: supertipos y subtipos según la estrategia)
    for e in ents.values():
        if e.get("debil_de") or e["nombre"] in sub_de:
            continue
        j = jer.get(e["nombre"])
        if j and j["estrategia"] == "B":
            for s, attrs in j["subtipos"].items():
                t = tabla(s, f"R8 (B) subtipo {s} con los atributos de {e['nombre']}")
                c1, u1 = _cols_de(e["atributos"]); c2, u2 = _cols_de(attrs)
                t["cols"], t["pk"], t["unicos"] = c1 + c2, list(e["clave"]), u1 + u2
            continue
        t = tabla(e["nombre"], "R1 entidad fuerte")
        t["cols"], t["unicos"] = _cols_de(e["atributos"])
        t["pk"] = list(e["clave"])
        if j and j["estrategia"] == "C":
            d = j["discriminador"]
            t["cols"].append([d["nombre"], d["tipo"], j["total"]])
            for s, attrs in j["subtipos"].items():
                c, u = _cols_de(attrs, forzar_nulo=True)
                t["cols"] += c; t["unicos"] += u
            t["origen"] = f"R1 entidad fuerte + R8 (C) una sola tabla con {d['nombre']}"
    for j in mer.get("jerarquias", []):
        if j["estrategia"] == "A":
            for s, attrs in j["subtipos"].items():
                t = tabla(s, f"R8 (A) subtipo de {j['super']}")
                for k in T[j["super"]]["pk"]:
                    t["cols"].append([k, tipo_col(j["super"], k), True])
                t["pk"] = list(T[j["super"]]["pk"])
                c, u = _cols_de(attrs)
                t["cols"] += c; t["unicos"] += u
                T[s]["fks"].append((tuple(t["pk"]), j["super"], tuple(T[j["super"]]["pk"])))
                T[s]["origen_fk"].append(f"R8 (A) el subtipo apunta a {j['super']}")
    # R2 · entidades débiles (después de sus dueños)
    pendientes = [e for e in ents.values() if e.get("debil_de")]
    while pendientes:
        for e in list(pendientes):
            dueño = e["debil_de"][0]
            if destino(dueño) not in T:
                continue
            t = tabla(e["nombre"], f"R2 entidad débil de {dueño}")
            nombres = agregar_fk(e["nombre"], dueño, e.get("columnas_dueño"), True,
                                 f"R2 identifica a {e['nombre']} dentro de {dueño}")
            c, u = _cols_de(e["atributos"])
            t["cols"] += c; t["unicos"] += u
            t["pk"] = list(nombres) + list(e["clave"])
            pendientes.remove(e)
    # R6 · multivaluados
    for e in ents.values():
        for a in e["atributos"]:
            if a["clase"] == "multi":
                t = tabla(a["tabla"], f"R6 atributo multivaluado {a['nombre']} de {e['nombre']}")
                nombres = agregar_fk(a["tabla"], e["nombre"], None, True, f"R6 dueño del valor ({e['nombre']})")
                t["cols"].append([a["nombre"], a["tipo"], True])
                t["pk"] = list(nombres) + [a["nombre"]]
    # R3, R4, R5, R7 · relaciones
    for r in mer["relaciones"]:
        lados = r["lados"]
        colsrel = r.get("columnas", {})
        attrs = r.get("atributos", [])
        if len(lados) == 3:
            t = tabla(r["tabla"], f"R7 relación ternaria {r['nombre']}")
            pk = []
            for e, p in lados:
                nombres = agregar_fk(r["tabla"], e, colsrel.get(e), True, f"R7 {r['nombre']}")
                if muchos(p):
                    pk += nombres
            c, u = _cols_de(attrs)
            t["cols"] += c; t["pk"] = pk
            continue
        (e1, p1), (e2, p2) = lados
        if muchos(p1) and muchos(p2):
            t = tabla(r["tabla"], f"R5 relación N:M {r['nombre']}")
            n1 = agregar_fk(r["tabla"], e1, colsrel.get(e1), True, f"R5 {r['nombre']}")
            n2 = agregar_fk(r["tabla"], e2, colsrel.get(e2), True, f"R5 {r['nombre']}")
            c, u = _cols_de(attrs)
            t["cols"] += c
            t["pk"] = n1 + n2 + list(r.get("clave_extra", []))
            continue
        if not muchos(p1) and muchos(p2):      # cada e2 tiene a lo más un e1: la FK va en e2
            lado, ref, nonull, regla = e2, e1, p1[0] >= 1, "R3"
        elif muchos(p1) and not muchos(p2):
            lado, ref, nonull, regla = e1, e2, p2[0] >= 1, "R3"
        else:                                   # 1:1: la FK va del lado con participación total
            regla = "R4"
            if r.get("fk_en"):
                lado = r["fk_en"]
            elif p1[0] >= 1:
                lado = e2
            elif p2[0] >= 1:
                lado = e1
            else:
                lado = e2
            ref = e1 if lado == e2 else e2
            nonull = (p1 if lado == e2 else p2)[0] >= 1
        t_lado = destino(lado)
        agregar_fk(t_lado, ref, colsrel.get(ref), nonull, f"{regla} {r['nombre']}", unico=(regla == "R4"))
        c, u = _cols_de(attrs, forzar_nulo=not nonull)
        T[t_lado]["cols"] += c
    return T


def orden_creacion(T):
    """Orden topológico (primero las tablas a las que se apunta). Devuelve (orden, ciclos)."""
    orden, hechas, ciclo = [], set(), []
    restantes = list(T)
    while restantes:
        avanzó = False
        for t in list(restantes):
            refs = {ref for _, ref, _ in T[t]["fks"] if ref != t}
            if refs <= hechas:
                orden.append(t); hechas.add(t); restantes.remove(t); avanzó = True
        if not avanzó:
            ciclo = list(restantes)
            orden += restantes
            break
    return orden, ciclo


def linea(t):
    """`tabla(col PK, col FK→ref, col?, ...)`: la notación textual de la base."""
    fk_de = {}
    for cols, ref, _ in t["fks"]:
        for c in cols:
            fk_de.setdefault(c, ref)
    unicos1 = {u[0] for u in t["unicos"] if len(u) == 1}
    partes = []
    for nombre, _, nonull in t["cols"]:
        s = nombre + ("" if nonull or nombre in t["pk"] else "?")
        if nombre in t["pk"]:
            s += " PK"
        if nombre in fk_de:
            s += f" FK→{fk_de[nombre]}"
        if nombre in unicos1:
            s += " UNIQUE"
        partes.append(s)
    return f"{t['nombre']}({', '.join(partes)})"


def normal(T):
    """Forma comparable de un esquema: columnas con tipo y NOT NULL, PK, FK y UNIQUE."""
    out = {}
    for n, t in T.items():
        pk = set(t["pk"])
        out[n] = {
            "cols": {(c[0], c[1].upper(), bool(c[2]) or c[0] in pk) for c in t["cols"]},
            "pk": frozenset(pk),
            "fks": {(cols, ref, rc) for cols, ref, rc in t["fks"]},
            "unicos": {frozenset(u) for u in t["unicos"]},
        }
    return out


def leer_esquema(con):
    """El esquema real de una base SQLite, en la misma forma que mapear()."""
    T = {}
    for (n,) in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid"):
        info = con.execute(f"PRAGMA table_info({n})").fetchall()
        pk = [r[1] for r in sorted((r for r in info if r[5] > 0), key=lambda r: r[5])]
        cols = [[r[1], r[2], bool(r[3]) or r[5] > 0] for r in info]
        fk = {}
        for r in con.execute(f"PRAGMA foreign_key_list({n})"):
            fk.setdefault(r[0], []).append((r[3], r[2], r[4]))
        fks = []
        for filas in fk.values():
            ref = filas[0][1]
            to = [f[2] for f in filas]
            if any(x is None for x in to):
                to = [r[1] for r in sorted((r for r in con.execute(f"PRAGMA table_info({ref})") if r[5] > 0), key=lambda r: r[5])]
            fks.append((tuple(f[0] for f in filas), ref, tuple(to)))
        unicos = []
        for r in con.execute(f"PRAGMA index_list({n})"):
            if r[2] and r[3] == "u":
                unicos.append(tuple(x[2] for x in con.execute(f"PRAGMA index_info({r[1]})")))
        T[n] = {"nombre": n, "cols": cols, "pk": pk, "fks": fks, "unicos": unicos}
    return T


def comparar(derivado, real, tablas=None):
    """Lista de diferencias entre dos esquemas (vacía si coinciden)."""
    a, b = normal(derivado), normal(real)
    if tablas is not None:
        b = {k: v for k, v in b.items() if k in tablas}
    dif = []
    if set(a) != set(b):
        dif.append(f"tablas: sobran {sorted(set(a) - set(b))}, faltan {sorted(set(b) - set(a))}")
    for n in sorted(set(a) & set(b)):
        for k in ("cols", "pk", "fks", "unicos"):
            if a[n][k] != b[n][k]:
                dif.append(f"{n}.{k}: derivado {sorted(map(str, a[n][k]))} · real {sorted(map(str, b[n][k]))}")
    return dif


def resumen(T):
    return {"tablas": len(T), "columnas": sum(len(t["cols"]) for t in T.values()),
            "fks": sum(len(t["fks"]) for t in T.values())}


# =============================================================== scripts SQL y su revisión en el .md
def bloques(ruta):
    """Parte un archivo .sql en bloques marcados con «-- @clase nombre». Clases: crear, datos,
    consulta, error."""
    out, actual = [], None
    for ln in Path(ruta).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^-- @(crear|datos|consulta|error) (\S+)", ln)
        if m:
            actual = {"clase": m.group(1), "nombre": m.group(2), "lineas": []}
            out.append(actual)
        elif actual is not None:
            actual["lineas"].append(ln)
    for b in out:
        while b["lineas"] and (not b["lineas"][-1].strip() or b["lineas"][-1].startswith("--")):
            b["lineas"].pop()
        b["sql"] = "\n".join(b["lineas"]).strip()
    return out


def correr(con, bs):
    """Ejecuta los bloques en orden. Devuelve {nombre: resultado}: (encabezado, filas) o mensaje."""
    res = {}
    for b in bs:
        if b["clase"] in ("crear", "datos"):
            con.executescript(b["sql"])
        elif b["clase"] == "consulta":
            cur = con.execute(b["sql"])
            res[b["nombre"]] = ([d[0] for d in cur.description], cur.fetchall())
        else:
            try:
                con.execute(b["sql"])
            except sqlite3.Error as e:
                res[b["nombre"]] = str(e)
            else:
                raise AssertionError(f"el bloque {b['nombre']} debía fallar y no falló")
    return res


def _plano(s):
    return " ".join(s.split())


def tabla_md(encabezado, filas):
    out = ["| " + " | ".join(encabezado) + " |", "|" + "---|" * len(encabezado)]
    out += ["| " + " | ".join(valor(v) for v in f) + " |" for f in filas]
    return out


def revisar_sql(md, bs, res, exigir_crear=True):
    """Cada consulta en el .md con su tabla de resultado justo después; cada error con su mensaje;
    cada bloque «crear» tal cual. Devuelve la lista de faltantes."""
    faltan = []
    plano = _plano(md)
    # bloques de código del .md con su posición
    codigos = [(m.start(), m.end(), _plano(m.group(1))) for m in re.finditer(r"```sql\n(.*?)```", md, re.S)]
    usados = {}   # una consulta repetida se busca en su siguiente aparición
    for b in bs:
        if b["clase"] == "datos":
            continue
        if b["clase"] == "crear" and not exigir_crear:
            continue
        q = _plano(b["sql"])
        if q not in plano:
            faltan.append(f"SQL de {b['nombre']}")
            continue
        if b["clase"] == "error":
            if _plano(res[b["nombre"]]) not in plano:
                faltan.append(f"mensaje de {b['nombre']}: {res[b['nombre']]}")
        if b["clase"] != "consulta":
            continue
        usados.setdefault(q, 0)
        cands = [e for s, e, c in codigos if q in c]
        fin = cands[usados[q]] if usados[q] < len(cands) else None
        usados[q] += 1
        if fin is None:
            faltan.append(f"{b['nombre']}: la consulta no está en un bloque ```sql")
            continue
        resto = md[fin:].splitlines()
        tab = []
        for ln in resto[1:]:
            if ln.startswith("|"):
                tab.append(ln.strip())
            elif tab:
                break
            elif ln.strip() and not ln.startswith(("Resultado", "*Resultado", "**Resultado")):
                break
        enc, filas = res[b["nombre"]]
        esperado = tabla_md(enc, filas)
        if [t.replace(" ", "") for t in tab] != [t.replace(" ", "") for t in esperado]:
            faltan.append(f"tabla de {b['nombre']}: esperaba {esperado}, hay {tab}")
    return faltan


# =============================================================== dibujos SVG
def _t(s):
    return html.escape(str(s), quote=False)


class Chen:
    """Diagrama entidad-relación en notación de Chen, con pares (mín, máx) junto a cada entidad."""

    def __init__(self, ancho, alto, nota=None):
        self.ancho, self.alto, self.nota = ancho, alto, nota
        self.formas, self.capas = {}, {"lineas": [], "formas": [], "textos": []}

    # --- formas
    def entidad(self, k, x, y, texto=None, debil=False, w=None):
        texto = texto or k.upper()
        w = w or max(110, 9 * len(texto) + 24)
        self.formas[k] = ("rect", x, y, w / 2, 20)
        s = f'<rect x="{x - w / 2:.1f}" y="{y - 20}" width="{w:.1f}" height="40" fill="white" stroke="{TINTA}" stroke-width="1.4"/>'
        if debil:
            s += f'<rect x="{x - w / 2 + 4:.1f}" y="{y - 16}" width="{w - 8:.1f}" height="32" fill="none" stroke="{TINTA}" stroke-width="1.1"/>'
        s += f'<text x="{x}" y="{y + 4.5}" text-anchor="middle" font-weight="600">{_t(texto)}</text>'
        self.capas["formas"].append(s)

    def relacion(self, k, x, y, texto=None, identificadora=False, tipo=None, w=None, tipo_dx=0):
        texto = texto or k.upper()
        hw = (w or max(118, 8.2 * len(texto) + 46)) / 2
        hh = 27
        self.formas[k] = ("rombo", x, y, hw, hh)
        pts = f"{x - hw:.1f},{y} {x},{y - hh} {x + hw:.1f},{y} {x},{y + hh}"
        s = f'<polygon points="{pts}" fill="{PAPEL}" stroke="{TINTA}" stroke-width="1.3"/>'
        if identificadora:
            f = 0.8
            pts2 = f"{x - hw * f:.1f},{y} {x},{y - hh * f:.1f} {x + hw * f:.1f},{y} {x},{y + hh * f:.1f}"
            s += f'<polygon points="{pts2}" fill="none" stroke="{TINTA}" stroke-width="1.1"/>'
        s += f'<text x="{x}" y="{y + 4}" text-anchor="middle" font-size="11">{_t(texto)}</text>'
        if tipo:
            s += f'<text x="{x + tipo_dx}" y="{y + hh + 13}" text-anchor="middle" font-size="10.5" fill="{ACENTO}" font-weight="600">{_t(tipo)}</text>'
        self.capas["formas"].append(s)

    def atributo(self, k, x, y, texto, dueño, clase="simple"):
        rx = max(34, 3.6 * len(texto) + 12)
        ry = 13
        self.formas[k] = ("elipse", x, y, rx, ry)
        guion = ' stroke-dasharray="4 3"' if clase == "derivado" else ""
        s = f'<ellipse cx="{x}" cy="{y}" rx="{rx:.1f}" ry="{ry}" fill="white" stroke="{SUAVE}" stroke-width="1"{guion}/>'
        if clase == "multi":
            s += f'<ellipse cx="{x}" cy="{y}" rx="{rx - 3.5:.1f}" ry="{ry - 3.5}" fill="none" stroke="{SUAVE}" stroke-width="0.9"/>'
        s += f'<text x="{x}" y="{y + 3.8}" text-anchor="middle" font-size="10.5" fill="{TINTA}">{_t(texto)}</text>'
        if clase in ("clave", "parcial"):
            lw = 5.6 * len(texto)
            dash = ' stroke-dasharray="3 2"' if clase == "parcial" else ""
            s += f'<line x1="{x - lw / 2:.1f}" y1="{y + 6}" x2="{x + lw / 2:.1f}" y2="{y + 6}" stroke="{TINTA}" stroke-width="1"{dash}/>'
        self.capas["formas"].append(s)
        if dueño:
            self.unir(dueño, k, color=SUAVE, grosor=0.9)

    def es_un(self, k, x, y, superk, subs, texto):
        h = 34
        self.formas[k] = ("elipse", x, y, 22, 18)
        pts = f"{x},{y - h / 2} {x - 22},{y + h / 2} {x + 22},{y + h / 2}"
        self.capas["formas"].append(
            f'<polygon points="{pts}" fill="{PAPEL}" stroke="{TINTA}" stroke-width="1.3"/>'
            f'<text x="{x}" y="{y + 11}" text-anchor="middle" font-size="9">es un</text>'
            f'<text x="{x + 30}" y="{y + 4}" font-size="10.5" fill="{ACENTO}" font-weight="600">{_t(texto)}</text>')
        self.unir(superk, k)
        for s in subs:
            self.unir(k, s)

    # --- líneas
    def _borde(self, k, hacia):
        f, x, y, a, b = self.formas[k]
        dx, dy = hacia[0] - x, hacia[1] - y
        if abs(dx) < 1e-9 and abs(dy) < 1e-9:
            return x, y
        if f == "rect":
            t = min(a / abs(dx) if dx else math.inf, b / abs(dy) if dy else math.inf)
        elif f == "rombo":
            t = 1 / (abs(dx) / a + abs(dy) / b)
        else:
            t = 1 / math.sqrt((dx / a) ** 2 + (dy / b) ** 2)
        return x + t * dx, y + t * dy

    def unir(self, k1, k2, par_cerca=None, par=None, color=None, grosor=1.3, lado=1):
        c1, c2 = self.formas[k1][1:3], self.formas[k2][1:3]
        p1, p2 = self._borde(k1, c2), self._borde(k2, c1)
        self.capas["lineas"].append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" '
                                    f'stroke="{color or TINTA}" stroke-width="{grosor}"/>')
        if par is not None:
            a, b = (p1, p2) if par_cerca == k1 else (p2, p1)
            L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
            ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            d = min(22, L / 2)
            mx, my = a[0] + ux * d, a[1] + uy * d
            nx, ny = -uy * lado, ux * lado
            tx, ty = mx + nx * 11, my + ny * 11
            txt = f"({par[0]},{par[1]})"
            w = 6.4 * len(txt) + 6
            self.capas["textos"].append(
                f'<rect x="{tx - w / 2:.1f}" y="{ty - 8:.1f}" width="{w:.1f}" height="15" rx="2" fill="white" fill-opacity="0.9"/>'
                f'<text x="{tx:.1f}" y="{ty + 3.8:.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{ACENTO}">{_t(txt)}</text>')

    def svg(self):
        s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.ancho} {self.alto}" width="{self.ancho}" '
             f'height="{self.alto}" font-family="Segoe UI, sans-serif" font-size="12" fill="{TINTA}">',
             f'<rect width="{self.ancho}" height="{self.alto}" fill="white"/>']
        s += self.capas["lineas"] + self.capas["formas"] + self.capas["textos"]
        if self.nota:
            s.append(f'<text x="{self.ancho / 2}" y="{self.alto - 8}" text-anchor="middle" font-size="10.5" fill="{SUAVE}">{_t(self.nota)}</text>')
        s.append("</svg>")
        return "\n".join(s)


def svg_tablas(T, pos, ancho, alto, w=180, nota=None):
    """Esquema relacional: una caja por tabla (PK y FK marcadas) y una flecha por clave foránea."""
    FILA, CAB = 17, 24
    geo = {}
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}" '
         f'font-family="Segoe UI, sans-serif" font-size="11" fill="{TINTA}">',
         f'<rect width="{ancho}" height="{alto}" fill="white"/>',
         f'<defs><marker id="fl" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{ACENTO}"/></marker></defs>']
    cajas = []
    for n, (x, y) in pos.items():
        t = T[n]
        h = CAB + FILA * len(t["cols"]) + 4
        filas = {c[0]: y + CAB + FILA * i + FILA / 2 + 2 for i, c in enumerate(t["cols"])}
        geo[n] = (x, y, w, h, filas)
        fkcols = {c for cols, _, _ in t["fks"] for c in cols}
        c = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="white" stroke="{TINTA}" stroke-width="1.3"/>',
             f'<rect x="{x}" y="{y}" width="{w}" height="{CAB}" rx="3" fill="{PAPEL}" stroke="{TINTA}" stroke-width="1.3"/>',
             f'<text x="{x + 8}" y="{y + 16}" font-weight="700" font-size="12">{_t(n)}</text>']
        for i, col in enumerate(t["cols"]):
            yy = y + CAB + FILA * i + FILA / 2 + 6
            marca = " ".join(m for m, ok in (("PK", col[0] in t["pk"]), ("FK", col[0] in fkcols)) if ok)
            peso = ' font-weight="700"' if col[0] in t["pk"] else ""
            nul = "" if col[2] or col[0] in t["pk"] else "?"
            c.append(f'<text x="{x + 8}" y="{yy}" font-family="Consolas, monospace" font-size="10.5"{peso}>{_t(col[0] + nul)}</text>')
            if marca:
                c.append(f'<text x="{x + w - 8}" y="{yy}" text-anchor="end" font-size="9.5" font-weight="700" fill="{ACENTO}">{marca}</text>')
        cajas.append("".join(c))
    flechas = []
    for n, t in T.items():
        if n not in geo:
            continue
        for cols, ref, rcols in t["fks"]:
            if ref not in geo:
                continue
            x1, y1, w1, _, f1 = geo[n]
            x2, y2, w2, _, f2 = geo[ref]
            ya, yb = f1[cols[0]], f2[rcols[0]]
            if abs(x1 - x2) < 1:                      # misma columna: se sale y se vuelve por la izquierda
                xa, xb = x1, x2
                d = f"M{xa},{ya} C{xa - 34},{ya} {xb - 34},{yb} {xb - 1},{yb}"
            elif x2 < x1:
                xa, xb = x1, x2 + w2
                m = (xa - xb) / 2
                d = f"M{xa},{ya} C{xa - m},{ya} {xb + m},{yb} {xb + 1},{yb}"
            else:
                xa, xb = x1 + w1, x2
                m = (xb - xa) / 2
                d = f"M{xa},{ya} C{xa + m},{ya} {xb - m},{yb} {xb - 1},{yb}"
            flechas.append(f'<path d="{d}" fill="none" stroke="{ACENTO}" stroke-width="1.3" marker-end="url(#fl)"/>'
                           f'<circle cx="{xa}" cy="{ya}" r="2.6" fill="{ACENTO}"/>')
    s += cajas + flechas
    if nota:
        s.append(f'<text x="{ancho / 2}" y="{alto - 8}" text-anchor="middle" font-size="10.5" fill="{SUAVE}">{_t(nota)}</text>')
    s.append("</svg>")
    return "\n".join(s)


# =============================================================== los dos modelos de las unidades 3 y 4
def veterinaria(estrategia="A"):
    """Ejemplo resuelto de las unidades 3 y 4: clínica veterinaria Patitas del Sur (Puerto Montt)."""
    return {
        "entidades": {
            "sede": {"nombre": "sede", "clave": ["cod_sede"], "atributos": [
                A("cod_sede", "VARCHAR(3)"), A("nombre", "VARCHAR(30)"), A("direccion", "VARCHAR(60)")]},
            "personal": {"nombre": "personal", "clave": ["rut"], "atributos": [
                A("rut", "VARCHAR(12)"), A("nombre", "VARCHAR(60)"), A("fecha_ingreso", "DATE")]},
            "veterinario": {"nombre": "veterinario", "clave": [], "atributos": []},
            "tecnico": {"nombre": "tecnico", "clave": [], "atributos": []},
            "tutor": {"nombre": "tutor", "clave": ["rut_tutor"], "atributos": [
                A("rut_tutor", "VARCHAR(12)"), A("nombre", "VARCHAR(60)"),
                C("direccion", [A("calle", "VARCHAR(40)"), A("numero", "INTEGER"), A("comuna", "VARCHAR(30)")]),
                M("telefono", "VARCHAR(16)", "telefono_tutor")]},
            "mascota": {"nombre": "mascota", "clave": ["nombre"], "debil_de": ("tutor", "pertenece", (1, 1), (1, N)),
                        "atributos": [A("nombre", "VARCHAR(30)"), A("especie", "VARCHAR(20)"),
                                      A("fecha_nac", "DATE", nulo=True)]},
            "atencion": {"nombre": "atencion", "clave": ["num_atencion"], "atributos": [
                A("num_atencion", "INTEGER"), A("fecha", "DATE"), A("motivo", "VARCHAR(80)")]},
            "vacuna": {"nombre": "vacuna", "clave": ["cod_vacuna"], "atributos": [
                A("cod_vacuna", "VARCHAR(3)"), A("nombre", "VARCHAR(40)")]},
            "laboratorio": {"nombre": "laboratorio", "clave": ["rut_lab"], "atributos": [
                A("rut_lab", "VARCHAR(12)"), A("nombre", "VARCHAR(40)")]},
        },
        "jerarquias": [{"super": "personal", "disjunta": True, "total": False, "estrategia": estrategia,
                        "discriminador": A("tipo", "VARCHAR(12)"),
                        "subtipos": {"veterinario": [A("colegiatura", "VARCHAR(10)")],
                                     "tecnico": [A("turno", "VARCHAR(6)")]}}],
        "relaciones": [
            {"nombre": "trabaja_en", "lados": [("sede", (1, 1)), ("personal", (1, N))]},
            {"nombre": "dirige", "lados": [("veterinario", (1, 1)), ("sede", (0, 1))],
             "columnas": {"veterinario": ["rut_director"]}},
            {"nombre": "recibe", "lados": [("mascota", (1, 1)), ("atencion", (0, N))],
             "columnas": {"mascota": ["rut_tutor", "nombre_mascota"]}},
            {"nombre": "realiza", "lados": [("veterinario", (1, 1)), ("atencion", (0, N))],
             "columnas": {"veterinario": ["rut_veterinario"]}},
            {"nombre": "aplica", "tabla": "aplica", "lados": [("atencion", (0, N)), ("vacuna", (0, N))],
             "atributos": [A("lote", "VARCHAR(12)")]},
            {"nombre": "provee", "tabla": "provee",
             "lados": [("laboratorio", (0, 1)), ("vacuna", (0, N)), ("sede", (0, N))],
             "atributos": [A("precio", "INTEGER")]},
        ],
    }


def estampa_sur():
    """El caso integrador: el modelo entidad-relación de la base de Estampa Sur."""
    return {
        "entidades": {
            "tienda": {"nombre": "tienda", "clave": ["id_tienda"], "atributos": [
                A("id_tienda", "INTEGER"), A("nombre", "VARCHAR(40)", unico=True), A("comuna", "VARCHAR(40)")]},
            "producto": {"nombre": "producto", "clave": ["id_producto"], "atributos": [
                A("id_producto", "INTEGER"), A("nombre", "VARCHAR(40)", unico=True), A("precio", "INTEGER"),
                A("costo_var", "INTEGER"), A("seg_estampado", "INTEGER")]},
            "proveedor": {"nombre": "proveedor", "clave": ["id_proveedor"], "atributos": [
                A("id_proveedor", "INTEGER"), A("nombre", "VARCHAR(40)"), A("rubro", "VARCHAR(30)")]},
            "cliente": {"nombre": "cliente", "clave": ["id_cliente"], "atributos": [
                A("id_cliente", "INTEGER"), A("nombre", "VARCHAR(60)")]},
            "colegio": {"nombre": "colegio", "clave": [], "atributos": []},
            "club": {"nombre": "club", "clave": [], "atributos": []},
            "empresa": {"nombre": "empresa", "clave": [], "atributos": []},
            "persona": {"nombre": "persona", "clave": [], "atributos": []},
            "pedido": {"nombre": "pedido", "clave": ["id_pedido"], "atributos": [
                A("id_pedido", "INTEGER"), A("fecha", "DATE"), A("estado", "VARCHAR(12)")]},
            "orden_produccion": {"nombre": "orden_produccion", "clave": ["id_orden"], "atributos": [
                A("id_orden", "INTEGER"), A("semana", "INTEGER"), A("lote", "INTEGER")]},
        },
        "jerarquias": [{"super": "cliente", "disjunta": True, "total": True, "estrategia": "C",
                        "discriminador": A("tipo", "VARCHAR(12)"),
                        "subtipos": {"colegio": [], "club": [], "empresa": [], "persona": []}}],
        "relaciones": [
            {"nombre": "atiende", "lados": [("tienda", (1, 1)), ("cliente", (0, N))]},
            {"nombre": "hace", "lados": [("cliente", (1, 1)), ("pedido", (0, N))]},
            {"nombre": "detalle", "tabla": "detalle_pedido", "lados": [("pedido", (0, N)), ("producto", (1, N))],
             "atributos": [A("cantidad", "INTEGER"), A("precio_unit", "INTEGER")]},
            {"nombre": "suministra", "tabla": "suministra", "lados": [("proveedor", (1, N)), ("producto", (0, N))],
             "atributos": [A("costo_unidad", "INTEGER")]},
            {"nombre": "programa", "lados": [("producto", (1, 1)), ("orden_produccion", (0, N))]},
        ],
    }


# =============================================================== modelos de los ejercicios (unidades 3 y 4)
def feria():
    """Ejercicios 3.1 y 4.1: feria libre de Chillán."""
    return {
        "entidades": {
            "feriante": {"nombre": "feriante", "clave": ["rut_feriante"], "atributos": [
                A("rut_feriante", "VARCHAR(12)"), A("nombre", "VARCHAR(60)"), A("telefono", "VARCHAR(16)")]},
            "puesto": {"nombre": "puesto", "clave": ["id_puesto"], "atributos": [
                A("id_puesto", "INTEGER"), A("pasillo", "VARCHAR(2)"), A("metros", "INTEGER")]},
            "patente": {"nombre": "patente", "clave": ["num_patente"], "atributos": [
                A("num_patente", "INTEGER"), A("vence", "DATE")]},
            "producto": {"nombre": "producto", "clave": ["id_producto"], "atributos": [
                A("id_producto", "INTEGER"), A("nombre", "VARCHAR(40)")]},
        },
        "relaciones": [
            {"nombre": "arrienda", "lados": [("feriante", (0, 1)), ("puesto", (1, 2))]},
            {"nombre": "tiene", "lados": [("feriante", (1, 1)), ("patente", (0, 1))]},
            {"nombre": "vende", "tabla": "vende", "lados": [("puesto", (1, N)), ("producto", (0, N))]},
        ],
    }


def consultorio():
    """Ejercicios 3.2, 4.4 y 4.6: Cesfam de Los Ángeles."""
    return {
        "entidades": {
            "sector": {"nombre": "sector", "clave": ["id_sector"], "atributos": [
                A("id_sector", "INTEGER"), A("nombre", "VARCHAR(30)")]},
            "paciente": {"nombre": "paciente", "clave": ["rut_paciente"], "atributos": [
                A("rut_paciente", "VARCHAR(12)"), A("nombre", "VARCHAR(60)")]},
            "medico": {"nombre": "medico", "clave": ["rut_medico"], "atributos": [
                A("rut_medico", "VARCHAR(12)"), A("nombre", "VARCHAR(60)")]},
        },
        "relaciones": [
            {"nombre": "inscrito", "lados": [("sector", (1, 1)), ("paciente", (0, N))]},
            {"nombre": "trabaja", "lados": [("sector", (1, 1)), ("medico", (1, N))]},
            {"nombre": "jefe", "lados": [("medico", (1, 1)), ("sector", (0, 1))],
             "columnas": {"medico": ["rut_jefe"]}},
        ],
    }


def liga():
    """Ejercicios 3.9 y 4.9: liga de básquetbol juvenil de Temuco."""
    return {
        "entidades": {
            "club": {"nombre": "club", "clave": ["cod_club"], "atributos": [
                A("cod_club", "VARCHAR(4)"), A("nombre", "VARCHAR(40)"), A("comuna", "VARCHAR(30)")]},
            "equipo": {"nombre": "equipo", "clave": ["categoria"], "debil_de": ("club", "inscribe", (1, 1), (1, N)),
                       "atributos": [A("categoria", "VARCHAR(6)")]},
            "entrenador": {"nombre": "entrenador", "clave": ["rut_entrenador"], "atributos": [
                A("rut_entrenador", "VARCHAR(12)"), A("nombre", "VARCHAR(60)")]},
            "jugador": {"nombre": "jugador", "clave": ["rut_jugador"], "atributos": [
                A("rut_jugador", "VARCHAR(12)"), A("nombre", "VARCHAR(60)"), A("fecha_nac", "DATE")]},
            "partido": {"nombre": "partido", "clave": ["num_partido"], "atributos": [
                A("num_partido", "INTEGER"), A("fecha", "DATE"), A("cancha", "VARCHAR(40)")]},
            "arbitro": {"nombre": "arbitro", "clave": ["rut_arbitro"], "atributos": [
                A("rut_arbitro", "VARCHAR(12)"), A("nombre", "VARCHAR(60)")]},
        },
        "relaciones": [
            {"nombre": "juega_en", "lados": [("equipo", (1, 1)), ("jugador", (5, N))],
             "atributos": [A("numero_camiseta", "INTEGER")]},
            {"nombre": "entrena", "lados": [("entrenador", (1, 1)), ("equipo", (1, 2))]},
            {"nombre": "local", "lados": [("equipo", (1, 1)), ("partido", (0, N))],
             "columnas": {"equipo": ["club_local", "categoria_local"]}},
            {"nombre": "visita", "lados": [("equipo", (1, 1)), ("partido", (0, N))],
             "columnas": {"equipo": ["club_visita", "categoria_visita"]}},
            {"nombre": "arbitra", "tabla": "arbitra", "lados": [("arbitro", (2, 3)), ("partido", (0, N))],
             "atributos": [A("rol", "VARCHAR(10)")]},
        ],
    }
