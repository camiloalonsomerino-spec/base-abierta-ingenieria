"""Unidad 2 · Modelo entidad-relación. Revisa cada diagrama, dibuja los SVG y, con --revisar, busca en
el .md cada respuesta, cada sentencia SQL y cada fila de resultado.

1. Cada diagrama de la unidad (ejemplo, ejercicios y caso) se declara una sola vez como datos: entidades,
   atributos (con su tipo y su dueño) y relaciones (con sus participantes y roles). De esos datos salen
   el SVG en notación de Chen y los conteos que cita el texto.
2. Revisa la forma: cada atributo tiene un dueño que existe, cada entidad fuerte tiene clave, cada
   relación une entidades que existen, la que repite una entidad lleva roles, el grado es el número de
   participantes y los nombres siguen las reglas de la sección 6.
3. Recalcula los ejercicios con números: pares repetidos (2.6) y combinaciones falsas de tres binarias (2.9).
4. CADENA: arma en memoria la base del caso con el esquema del script del caso y exige que el diagrama
   calce con datos/esquema.sql: cada entidad es una tabla, cada atributo almacenado es una columna, cada
   atributo derivado NO es columna, cada clave es la clave primaria, cada rombo es una clave foránea o una
   tabla con dos claves foráneas, y no sobra ninguna columna.
5. Corre sql/u02_mer.sql sobre esa base.

    python u02_mer.py            # revisa, dibuja e imprime
    python u02_mer.py --revisar  # además busca todo en el .md
"""
from pathlib import Path
from itertools import product
import html, importlib.util, re, sqlite3, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
SQL = RAMO / "sql"
FIG = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "02-modelo-entidad-relacion.md"

TINTA, SUAVE, ACENTO, PAPEL, LINEA = "#2B2F33", "#5F656B", "#E2622A", "#FBEDE6", "#8A8F94"

# =============================================================================== diagramas
# E: entidad -> (x, y) · A: (dueño, nombre, tipo, x, y); tipo: simple, clave, comp, multi, deriv;
# el dueño de un componente es "entidad.atributo" · R: (nombre, x, y, participantes, vías, roles)
ESCUELA = {
    "W": 1000, "H": 620,
    "E": {"alumno": (330, 300), "curso": (760, 270), "profesor": (760, 75), "prestamo": (760, 440),
          "instrumento": (760, 570)},
    "A": [("alumno", "matricula", "clave", 175, 235), ("alumno", "nombre", "comp", 160, 320),
          ("alumno.nombre", "nombres", "simple", 60, 275), ("alumno.nombre", "apellidos", "simple", 70, 370),
          ("alumno", "fecha_nac", "simple", 195, 405), ("alumno", "edad", "deriv", 285, 430),
          ("alumno", "telefono", "multi", 460, 345),
          ("alumno", "direccion", "comp", 400, 455), ("alumno.direccion", "calle", "simple", 305, 530),
          ("alumno.direccion", "numero", "simple", 405, 555), ("alumno.direccion", "comuna", "simple", 505, 530),
          ("curso", "codigo_curso", "clave", 905, 225), ("curso", "nombre", "simple", 915, 270),
          ("curso", "dia", "simple", 905, 315), ("curso", "hora", "simple", 845, 350),
          ("profesor", "codigo", "clave", 615, 45), ("profesor", "nombre", "simple", 905, 45),
          ("profesor", "especialidad", "simple", 905, 100),
          ("se_inscribe_en", "fecha_inscripcion", "simple", 495, 195), ("se_inscribe_en", "nota_final", "simple", 655, 195),
          ("prestamo", "n_prestamo", "clave", 905, 400), ("prestamo", "fecha_salida", "simple", 915, 445),
          ("prestamo", "fecha_devolucion", "simple", 900, 490),
          ("instrumento", "n_inventario", "clave", 600, 580), ("instrumento", "tipo", "simple", 905, 550),
          ("instrumento", "estado", "simple", 900, 597)],
    "R": [("dicta", 760, 172, ["profesor", "curso"], None, None),
          ("se_inscribe_en", 575, 270, ["alumno", "curso"], None, None),
          ("pide", 575, 440, ["alumno", "prestamo"], None, None),
          ("lleva", 760, 505, ["prestamo", "instrumento"], None, None),
          ("es_tutor_de", 330, 130, ["alumno", "alumno"], [[(285, 300), (285, 130)], [(375, 300), (375, 130)]],
           ["tutor", "tutorado"])],
}
GIMNASIO = {
    "W": 900, "H": 325, "DY": -75,
    "E": {"socio": (230, 200), "plan": (230, 340), "clase": (620, 200), "instructor": (620, 340)},
    "A": [("socio", "id_socio", "clave", 90, 130), ("socio", "nombre", "simple", 230, 110),
          ("socio", "telefono", "multi", 370, 120), ("socio", "fecha_nac", "simple", 75, 200),
          ("socio", "edad", "deriv", 80, 265),
          ("plan", "cod_plan", "clave", 90, 340), ("plan", "nombre", "simple", 145, 385), ("plan", "precio_mensual", "simple", 330, 385),
          ("clase", "cod_clase", "clave", 620, 110), ("clase", "disciplina", "simple", 770, 155), ("clase", "horario", "simple", 775, 220),
          ("instructor", "rut", "clave", 775, 320), ("instructor", "nombre", "simple", 770, 375),
          ("contrata", "fecha_inicio", "simple", 380, 270)],
    "R": [("contrata", 230, 270, ["socio", "plan"], None, None),
          ("reserva", 425, 200, ["socio", "clase"], None, None),
          ("dicta", 620, 270, ["instructor", "clase"], None, None)],
}

BANCO = {
    "W": 1000, "H": 560,
    "E": {"empresa": (150, 300), "donacion": (400, 300), "reparto": (660, 300), "organizacion": (660, 470),
          "voluntario": (660, 120)},
    "A": [("empresa", "rut", "clave", 80, 215), ("empresa", "razon_social", "simple", 200, 200),
          ("empresa", "contacto", "comp", 150, 400), ("empresa.contacto", "nombre_contacto", "simple", 85, 470),
          ("empresa.contacto", "telefono_contacto", "simple", 235, 480),
          ("donacion", "n_donacion", "clave", 340, 210), ("donacion", "fecha", "simple", 445, 210),
          ("donacion", "kilos", "simple", 400, 395),
          ("reparto", "n_reparto", "clave", 830, 260), ("reparto", "fecha", "simple", 840, 305),
          ("reparto", "kilos_entregados", "simple", 830, 350),
          ("organizacion", "cod_org", "clave", 520, 420), ("organizacion", "nombre", "simple", 510, 480),
          ("organizacion", "personas", "simple", 560, 535),
          ("organizacion", "direccion", "comp", 830, 470), ("organizacion.direccion", "calle", "simple", 950, 420),
          ("organizacion.direccion", "numero", "simple", 955, 475), ("organizacion.direccion", "comuna", "simple", 920, 530),
          ("voluntario", "rut", "clave", 520, 60), ("voluntario", "nombre", "simple", 660, 30),
          ("voluntario", "telefono", "multi", 815, 85)],
    "R": [("dona", 275, 300, ["empresa", "donacion"], None, None),
          ("sale_de", 530, 300, ["reparto", "donacion"], None, None),
          ("llega_a", 660, 385, ["reparto", "organizacion"], None, None),
          ("realiza", 660, 210, ["voluntario", "reparto"], None, None)],
}

ERRORES = {   # el diagrama con errores del ejercicio 2.7 (a propósito)
    "W": 960, "H": 305, "DY": -75,
    "E": {"Alumnos": (200, 200), "clase": (480, 200), "instructor": (760, 200), "vehiculo": (760, 330)},
    "A": [("Alumnos", "rut", "clave", 70, 130), ("Alumnos", "nombre", "simple", 200, 105),
          ("Alumnos", "telefonos", "simple", 330, 120), ("Alumnos", "fecha_nac", "simple", 70, 230),
          ("Alumnos", "edad", "simple", 140, 290),
          ("clase", "fecha", "simple", 430, 110), ("clase", "hora", "simple", 540, 110),
          ("instructor", "rut_instructor", "clave", 760, 110), ("instructor", "nombre", "simple", 870, 160),
          ("vehiculo", "patente", "clave", 600, 340), ("vehiculo", "modelo", "simple", 680, 370),
          ("vehiculo", "rut_instructor", "simple", 870, 330)],
    "R": [("alumno_clase", 340, 200, ["Alumnos", "clase"], None, None),
          ("imparte", 620, 200, ["instructor", "clase"], None, None)],
}

LIGA = {
    "W": 1100, "H": 720,
    "E": {"jugadora": (300, 330), "club": (300, 600), "partido": (720, 330), "gimnasio": (800, 600),
          "arbitro": (720, 90)},
    "A": [("jugadora", "rut", "clave", 165, 255), ("jugadora", "nombre", "comp", 300, 225),
          ("jugadora.nombre", "nombres", "simple", 220, 165), ("jugadora.nombre", "apellidos", "simple", 380, 165),
          ("jugadora", "fecha_nac", "simple", 140, 320), ("jugadora", "categoria", "deriv", 150, 385),
          ("jugadora", "telefono", "multi", 440, 250),
          ("club", "cod_club", "clave", 150, 560), ("club", "nombre", "simple", 145, 620),
          ("club", "comuna", "simple", 200, 680), ("club", "colores", "multi", 330, 690),
          ("partido", "n_partido", "clave", 880, 280), ("partido", "fecha", "simple", 900, 330),
          ("partido", "hora", "simple", 880, 380), ("partido", "puntos_local", "deriv", 610, 230),
          ("partido", "puntos_visita", "deriv", 840, 230),
          ("gimnasio", "nombre", "clave", 655, 665), ("gimnasio", "capacidad", "simple", 800, 690),
          ("gimnasio", "direccion", "comp", 950, 600), ("gimnasio.direccion", "calle", "simple", 1045, 545),
          ("gimnasio.direccion", "numero", "simple", 1050, 615), ("gimnasio.direccion", "comuna", "simple", 1000, 680),
          ("arbitro", "rut", "clave", 590, 50), ("arbitro", "nombre", "simple", 860, 60),
          ("juega_en", "desde", "simple", 165, 470), ("anota", "puntos", "simple", 510, 390)],
    "R": [("juega_en", 300, 470, ["jugadora", "club"], None, None),
          ("anota", 510, 330, ["jugadora", "partido"], None, None),
          ("es_local", 470, 470, ["club", "partido"], None, None),
          ("es_visita", 620, 470, ["club", "partido"], None, None),
          ("se_juega_en", 800, 470, ["partido", "gimnasio"], None, None),
          ("dirige", 720, 200, ["arbitro", "partido"], None, None),
          ("es_mentora_de", 300, 85, ["jugadora", "jugadora"], [[(255, 330), (255, 85)], [(345, 330), (345, 85)]],
           ["mentora", "aprendiz"])],
}

CASO = {
    "W": 1120, "H": 640,
    "E": {"tienda": (90, 330), "cliente": (330, 330), "pedido": (580, 330), "producto": (880, 330),
          "proveedor": (880, 80), "orden_produccion": (880, 560)},
    "A": [("tienda", "id_tienda", "clave", 70, 240), ("tienda", "nombre", "simple", 160, 260),
          ("tienda", "comuna", "simple", 90, 420),
          ("cliente", "id_cliente", "clave", 290, 240), ("cliente", "nombre", "simple", 390, 255),
          ("cliente", "tipo", "simple", 330, 420),
          ("pedido", "id_pedido", "clave", 535, 240), ("pedido", "fecha", "simple", 630, 250),
          ("pedido", "estado", "simple", 545, 420), ("pedido", "total", "deriv", 610, 470),
          ("incluye", "cantidad", "simple", 690, 420), ("incluye", "precio_unit", "simple", 760, 470),
          ("producto", "id_producto", "clave", 1030, 250), ("producto", "nombre", "simple", 1045, 300),
          ("producto", "precio", "simple", 1050, 350), ("producto", "costo_var", "simple", 1040, 400),
          ("producto", "seg_estampado", "simple", 1010, 450), ("producto", "margen_unit", "deriv", 760, 250),
          ("proveedor", "id_proveedor", "clave", 720, 55), ("proveedor", "nombre", "simple", 1030, 55),
          ("proveedor", "rubro", "simple", 1030, 110),
          ("suministra", "costo_unidad", "simple", 1030, 200),
          ("orden_produccion", "id_orden", "clave", 690, 600), ("orden_produccion", "semana", "simple", 1050, 545),
          ("orden_produccion", "lote", "simple", 1050, 600), ("orden_produccion", "horas_estampado", "deriv", 1000, 495)],
    "R": [("atiende", 210, 330, ["tienda", "cliente"], None, None),
          ("hace", 455, 330, ["cliente", "pedido"], None, None),
          ("incluye", 730, 330, ["pedido", "producto"], None, None),
          ("suministra", 880, 200, ["proveedor", "producto"], None, None),
          ("fabrica", 880, 450, ["orden_produccion", "producto"], None, None)],
}
# El caso en la base: entidad -> tabla, relación -> cómo se guarda (unidad 4 lo justifica)
CASO_TABLA_REL = {"incluye": "detalle_pedido", "suministra": "suministra"}
CASO_DERIVADOS = {"pedido.total": "SUM(cantidad * precio_unit) de sus líneas",
                  "producto.margen_unit": "precio - costo_var",
                  "orden_produccion.horas_estampado": "lote * seg_estampado / 3600"}

SIMBOLOS = {   # la leyenda de la notación
    "W": 960, "H": 250,
    "E": {"entidad": (90, 70)},
    "A": [("entidad", "atributo", "simple", 250, 40), ("entidad", "clave", "clave", 250, 100),
          ("entidad", "compuesto", "comp", 90, 170), ("entidad.compuesto", "parte_1", "simple", 40, 225),
          ("entidad.compuesto", "parte_2", "simple", 145, 225)],
    "R": [],
    "EXTRA": True,
}


# =============================================================================== modelo
def modelo(D):
    """Lo que el diagrama dice, sin posiciones."""
    M = {"entidades": list(D["E"]), "atributos": {}, "relaciones": {}}
    for dueno, n, t, _, _ in D["A"]:
        M["atributos"].setdefault(dueno, []).append((n, t))
    for n, _, _, partes, _, roles in D["R"]:
        M["relaciones"][n] = {"partes": partes, "roles": roles, "grado": len(set(partes)),   # unaria si repite la entidad
                              "atributos": [a for a, _ in M["atributos"].get(n, [])]}
    return M


NOMBRE_OK = re.compile(r"^[a-z][a-z0-9_]*$")


def revisar_forma(D, nombre, estricto=True):
    """Devuelve la lista de problemas de forma. Un diagrama correcto devuelve []."""
    M, prob = modelo(D), []
    nodos = set(M["entidades"]) | set(M["relaciones"])
    compuestos = {f"{d}.{n}" for d, ats in M["atributos"].items() for n, t in ats if t == "comp"}
    for dueno, ats in M["atributos"].items():
        if dueno not in nodos and dueno not in compuestos:
            prob.append(f"{nombre}: el atributo de «{dueno}» no tiene dueño")
        for n, t in ats:
            if not NOMBRE_OK.match(n):
                prob.append(f"{nombre}: nombre de atributo «{n}»")
            if t == "comp" and not M["atributos"].get(f"{dueno}.{n}"):
                prob.append(f"{nombre}: el compuesto «{n}» no tiene partes")
    for e in M["entidades"]:
        if not NOMBRE_OK.match(e):
            prob.append(f"{nombre}: nombre de entidad «{e}»")
        if e.endswith("s") and e not in ("pais",):
            prob.append(f"{nombre}: entidad en plural «{e}»")
        if not any(t == "clave" for _, t in M["atributos"].get(e, [])):
            prob.append(f"{nombre}: la entidad «{e}» no tiene clave")
    claves = {n: e for e in M["entidades"] for n, t in M["atributos"].get(e, []) if t == "clave"}
    for e in M["entidades"]:
        for n, t in M["atributos"].get(e, []):
            if t != "clave" and n != "nombre" and n in claves and claves[n] != e:
                prob.append(f"{nombre}: «{e}.{n}» es la clave de «{claves[n]}»: eso es una relación, no un atributo")
    for r, d in M["relaciones"].items():
        if any(p not in M["entidades"] for p in d["partes"]):
            prob.append(f"{nombre}: la relación «{r}» une algo que no es entidad")
        if len(set(d["partes"])) < len(d["partes"]) and not d["roles"]:
            prob.append(f"{nombre}: la relación «{r}» repite una entidad y no tiene roles")
        if any(p in r.split("_") for p in M["entidades"]):
            prob.append(f"{nombre}: la relación «{r}» se llama como sus entidades, no con un verbo")
    return prob


def conteos(D):
    M = modelo(D)
    tipos = {}
    for ats in M["atributos"].values():
        for _, t in ats:
            tipos[t] = tipos.get(t, 0) + 1
    grados = {}
    for d in M["relaciones"].values():
        grados[d["grado"]] = grados.get(d["grado"], 0) + 1
    return {"entidades": len(M["entidades"]), "relaciones": len(M["relaciones"]), "tipos": tipos, "grados": grados}


# =============================================================================== dibujo (Chen)
def ancho_texto(t, tam=12.5):
    return sum(0.62 if c not in "il.,:;|'" else 0.3 for c in t) * tam


def svg(D, archivo, titulo):
    W, H = D["W"], D["H"]
    pos, forma = {}, {}
    for e, (x, y) in D["E"].items():
        pos[e] = (x, y)
    for n, x, y, *_ in D["R"]:
        pos[n] = (x, y)
    for dueno, n, t, x, y in D["A"]:
        pos[f"{dueno}.{n}"] = (x, y)
    lineas, figuras, textos = [], [], []
    esc = html.escape
    # líneas de atributos
    for dueno, n, t, x, y in D["A"]:
        x0, y0 = pos[dueno]
        lineas.append(f'<line x1="{x0}" y1="{y0}" x2="{x}" y2="{y}" stroke="{LINEA}" stroke-width="1.2"/>')
    # líneas de relaciones (con vías opcionales) y roles
    for n, x, y, partes, vias, roles in D["R"]:
        for k, p in enumerate(partes):
            pts = [pos[p]] + (vias[k] if vias and vias[k] else []) + [(x, y)]
            lineas.append('<polyline points="' + " ".join(f"{a},{b}" for a, b in pts) +
                          f'" fill="none" stroke="{TINTA}" stroke-width="1.6"/>')
            if roles:
                a, b = pts[-2] if len(pts) > 2 else pts[0]
                c, d = pts[-3] if len(pts) > 3 else pts[-1]
                mx, my = (a + c) / 2, (b + d) / 2
                lado = -1 if k == 0 else 1
                textos.append(f'<text x="{mx + lado * 6}" y="{my}" text-anchor="{"end" if lado < 0 else "start"}" '
                              f'font-size="11.5" font-style="italic" fill="{ACENTO}">{esc(roles[k])}</text>')
    # atributos
    for dueno, n, t, x, y in D["A"]:
        rx, ry = max(30, ancho_texto(n) / 2 + 13), 15
        trazo = f'stroke="{TINTA}" stroke-width="1.2"'
        if t == "deriv":
            trazo += ' stroke-dasharray="5 3"'
        figuras.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx:.1f}" ry="{ry}" fill="white" {trazo}/>')
        if t == "multi":
            figuras.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx - 4:.1f}" ry="{ry - 4}" fill="none" {trazo}/>')
        figuras.append(f'<text x="{x}" y="{y + 4.3}" text-anchor="middle" font-size="12.5" fill="{TINTA}">{esc(n)}</text>')
        if t == "clave":   # subrayado dibujado: no depende del visor
            m = ancho_texto(n) / 2
            figuras.append(f'<line x1="{x - m:.1f}" y1="{y + 7}" x2="{x + m:.1f}" y2="{y + 7}" stroke="{TINTA}" stroke-width="1"/>')
    # relaciones
    for n, x, y, *_ in D["R"]:
        hw, hh = max(48, ancho_texto(n) / 2 + 26), 24
        figuras.append(f'<polygon points="{x - hw},{y} {x},{y - hh} {x + hw},{y} {x},{y + hh}" fill="{PAPEL}" '
                       f'stroke="{TINTA}" stroke-width="1.5"/>')
        figuras.append(f'<text x="{x}" y="{y + 4.3}" text-anchor="middle" font-size="12.5" fill="{TINTA}">{esc(n)}</text>')
    # entidades
    for e, (x, y) in D["E"].items():
        w, h = ancho_texto(e, 13.5) + 28, 34
        figuras.append(f'<rect x="{x - w / 2:.1f}" y="{y - h / 2}" width="{w:.1f}" height="{h}" fill="white" '
                       f'stroke="{TINTA}" stroke-width="1.8"/>')
        figuras.append(f'<text x="{x}" y="{y + 4.8}" text-anchor="middle" font-size="13.5" font-weight="bold" fill="{TINTA}">{esc(e)}</text>')
    extra = []
    if D.get("EXTRA"):
        # piezas sueltas de la leyenda: multivaluado, derivado, relación y rótulos
        extra += [f'<ellipse cx="620" cy="40" rx="52" ry="15" fill="white" stroke="{TINTA}" stroke-width="1.2"/>',
                  f'<ellipse cx="620" cy="40" rx="48" ry="11" fill="none" stroke="{TINTA}" stroke-width="1.2"/>',
                  f'<text x="620" y="44.3" text-anchor="middle" font-size="12.5" fill="{TINTA}">multivaluado</text>',
                  f'<ellipse cx="620" cy="100" rx="44" ry="15" fill="white" stroke="{TINTA}" stroke-width="1.2" stroke-dasharray="5 3"/>',
                  f'<text x="620" y="104.3" text-anchor="middle" font-size="12.5" fill="{TINTA}">derivado</text>',
                  f'<polygon points="568,180 620,156 672,180 620,204" fill="{PAPEL}" stroke="{TINTA}" stroke-width="1.5"/>',
                  f'<text x="620" y="184.3" text-anchor="middle" font-size="12.5" fill="{TINTA}">relación</text>']
        notas = [(315, 44, "simple: un solo valor"), (315, 104, "clave: identifica (subrayada)"),
                 (210, 175, "compuesto: se divide en partes"), (690, 44, "varios valores (doble óvalo)"),
                 (690, 104, "se calcula, no se guarda (punteado)"), (690, 184, "rombo con un verbo; une entidades")]
        extra += [f'<text x="{x}" y="{y}" font-size="11.5" fill="{SUAVE}">{esc(t)}</text>' for x, y, t in notas]
        extra.append(f'<text x="30" y="35" font-size="11.5" fill="{SUAVE}">entidad (rectángulo)</text>')
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="Segoe UI, Arial, sans-serif" role="img" aria-label="{esc(titulo)}">',
           f'<rect width="{W}" height="{H}" fill="white"/>', f'<g transform="translate(0,{D.get("DY", 0)})">']
    out += lineas + figuras + textos + extra + ["</g>", "</svg>"]
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / archivo).write_text("\n".join(out), encoding="utf-8")
    return archivo


FIGURAS = {"u02_simbolos.svg": (SIMBOLOS, "Notación de Chen: entidad, atributos y relación"),
           "u02_ejemplo_escuela.svg": (ESCUELA, "Diagrama entidad-relación de la escuela de música"),
           "u02_e04_gimnasio.svg": (GIMNASIO, "Diagrama del gimnasio del ejercicio 2.4"),
           "u02_e05_banco.svg": (BANCO, "Diagrama del banco de alimentos, pauta 2.5"),
           "u02_e07_errores.svg": (ERRORES, "Diagrama con seis errores del ejercicio 2.7"),
           "u02_e10_liga.svg": (LIGA, "Diagrama de la liga de básquetbol, pauta 2.10"),
           "u02_caso_estampa_sur.svg": (CASO, "Diagrama entidad-relación de Estampa Sur")}


# =============================================================================== ejercicios con respuesta fija
E21 = [("emprendedor", "entidad"), ("RUT", "atributo clave de emprendedor"), ("rubro", "atributo de emprendedor"),
       ("stand", "entidad"), ("número del stand", "atributo clave de stand"), ("metros cuadrados", "atributo de stand"),
       ("enchufe", "atributo de stand"), ("arrienda", "relación entre emprendedor y stand"),
       ("valor cobrado", "atributo de la relación arrienda")]
E22 = [("rut", "simple; clave candidata"), ("n_ficha", "simple; clave candidata"),
       ("nombre", "compuesto (nombres, apellido paterno, apellido materno)"), ("fecha_nac", "simple"),
       ("edad", "derivado (de fecha_nac)"), ("direccion", "compuesto (calle, número, comuna)"),
       ("alergias", "multivaluado"), ("telefonos", "multivaluado"), ("sector", "simple")]
E23 = [("a", "juega_en", ["jugador", "equipo"], None), ("b", "recomienda_a", ["socio", "socio"], ["recomienda", "recomendado"]),
       ("c", "dirige", ["arbitro", "partido"], None), ("d", "entrena", ["entrenador", "equipo", "temporada"], None),
       ("e", "es_filial_de", ["club", "club"], ["filial", "matriz"]), ("f", "se_lesiona_en", ["jugador", "partido"], None)]
E28 = [("Clientes", "cliente"), ("Fecha de Nacimiento", "fecha_nacimiento"), ("order", "pedido"),
       ("cliente_producto", "compra"), ("Tel1, Tel2, Tel3", "telefono"), ("NombreCompletoDelCliente", "nombre"),
       ("desc", "descripcion"), ("cód_región", "cod_region")]
# 2.7 · los seis errores: (elemento, lo que el verificador detecta solo o None si lo juzga quien lee)
E27 = [("`Alumnos`", "entidad en plural"), ("`telefonos`", None), ("`edad`", None), ("`clase` no tiene clave", "no tiene clave"),
       ("`alumno_clase`", "no con un verbo"), ("`rut_instructor` dibujado como atributo", "eso es una relación")]
E26_ATENCIONES = [("Rosa Venegas", "Dra. Fuentealba", "2026-05-04"), ("Hugo Toro", "Dr. Saavedra", "2026-05-04"),
                  ("Rosa Venegas", "Dra. Fuentealba", "2026-06-15"), ("Elena Lagos", "Dra. Fuentealba", "2026-06-15"),
                  ("Rosa Venegas", "Dr. Saavedra", "2026-07-02"), ("Hugo Toro", "Dr. Saavedra", "2026-08-20")]
E26_INSCRIPCIONES = [("Ana", "guitarra"), ("Ana", "coro"), ("Luis", "guitarra"), ("Marta", "coro")]
E29 = [("Rojas", "matemática", "Ana"), ("Rojas", "lenguaje", "Bruno"), ("Muñoz", "matemática", "Bruno"),
       ("Muñoz", "ciencias", "Ana"), ("Vera", "lenguaje", "Ana")]
E29_TARIFA = {("Rojas", "matemática", "Ana"): 14000, ("Rojas", "lenguaje", "Bruno"): 12500,
              ("Muñoz", "matemática", "Bruno"): 15500, ("Muñoz", "ciencias", "Ana"): 13000,
              ("Vera", "lenguaje", "Ana"): 11500}


def ejercicios():
    X = {}
    X["e03"] = [(k, n, len(set(p)), r) for k, n, p, r in E23]
    assert all((len(set(p)) < len(p)) == (r is not None) for _, _, p, r in E23)
    # 2.6 · si la atención fuera una relación paciente-médico, cada par cabría una sola vez
    pares = [(p, m) for p, m, _ in E26_ATENCIONES]
    X["e06"] = {"atenciones": len(pares), "pares": len(set(pares)), "perdidas": len(pares) - len(set(pares)),
                "repetidos": sorted({x for x in pares if pares.count(x) > 1}),
                "inscripciones": len(E26_INSCRIPCIONES), "pares_insc": len(set(E26_INSCRIPCIONES))}
    # 2.9 · tres binarias: proyectar y volver a juntar
    TA = {(t, a) for t, a, e in E29}
    AE = {(a, e) for t, a, e in E29}
    TE = {(t, e) for t, a, e in E29}
    T = {t for t, _, _ in E29}; A = {a for _, a, _ in E29}; Es = {e for _, _, e in E29}
    junta = {(t, a, e) for t, a, e in product(T, A, Es) if (t, a) in TA and (a, e) in AE and (t, e) in TE}
    falsas = sorted(junta - set(E29))
    assert set(E29) <= junta
    X["e09"] = {"reales": len(E29), "TA": len(TA), "AE": len(AE), "TE": len(TE), "junta": len(junta),
                "falsas": falsas, "n_falsas": len(falsas)}
    # formas de los diagramas de ejercicios
    X["gimnasio"] = conteos(GIMNASIO)
    X["banco"] = conteos(BANCO)
    X["liga"] = conteos(LIGA)
    X["errores"] = revisar_forma(ERRORES, "2.7")
    for _, pista in E27:   # cada error de forma de la pauta lo encuentra el verificador
        assert pista is None or any(pista in p for p in X["errores"]), pista
    X["escuela"] = conteos(ESCUELA)
    return X


# =============================================================================== caso
def modulo_caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_bd.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def base_del_caso(m):
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
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
    con.commit()
    return con


def sentencias(texto):
    out, buf = [], []
    for linea in texto.splitlines():
        s = linea.strip()
        if not buf and (not s or s.startswith("--")):
            continue
        buf.append(linea.rstrip())
        if s.endswith(";"):
            out.append("\n".join(buf).strip()); buf = []
    return out


def fila_md(f):
    return "| " + " | ".join("NULL" if v is None else str(v) for v in f) + " |"


def caso():
    m = modulo_caso()
    con = base_del_caso(m)
    M = modelo(CASO)
    tablas = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]
    cols = {t: {r[1]: r[5] for r in con.execute(f"PRAGMA table_info({t})")} for t in tablas}
    fks = {t: [(r[3], r[2]) for r in con.execute(f"PRAGMA foreign_key_list({t})")] for t in tablas}
    prob = revisar_forma(CASO, "caso")
    usadas = {t: set() for t in tablas}
    # entidades y atributos
    for e in M["entidades"]:
        if e not in cols:
            prob.append(f"la entidad {e} no es tabla"); continue
        for n, t in M["atributos"].get(e, []):
            if t == "deriv":
                if n in cols[e]:
                    prob.append(f"{e}.{n} es derivado pero está guardado")
                if f"{e}.{n}" not in CASO_DERIVADOS:
                    prob.append(f"{e}.{n} sin regla de cálculo")
                continue
            if n not in cols[e]:
                prob.append(f"{e}.{n} no es columna"); continue
            usadas[e].add(n)
            if (t == "clave") != bool(cols[e][n]):
                prob.append(f"{e}.{n}: la clave del diagrama no es la clave primaria")
    # relaciones: una clave foránea entre las dos tablas, o una tabla con claves foráneas a las dos
    forma_rel = {}
    for r, d in M["relaciones"].items():
        a, b = d["partes"]
        if r in CASO_TABLA_REL:
            t = CASO_TABLA_REL[r]
            destinos = {dest for _, dest in fks[t]}
            ok = {a, b} <= destinos
            for n in d["atributos"]:
                ok &= n in cols[t]
                usadas[t].add(n)
            usadas[t] |= {c for c, _ in fks[t]}
            forma_rel[r] = t
        else:
            hay = [(t, c) for t in (a, b) for c, dest in fks[t] if dest == ({a, b} - {t}).pop()]
            ok = len(hay) == 1 and not d["atributos"]
            if ok:
                usadas[hay[0][0]].add(hay[0][1])
                forma_rel[r] = f"{hay[0][0]}.{hay[0][1]}"
        if not ok:
            prob.append(f"la relación {r} no calza con las claves foráneas")
    sobran = [f"{t}.{c}" for t in tablas for c in cols[t] if c not in usadas[t]]
    prob += [f"columna sin lugar en el diagrama: {s}" for s in sobran]
    # derivados: se calculan desde la base (ejemplos que cita el texto)
    pol = con.execute("SELECT precio - costo_var FROM producto WHERE nombre = 'polerones'").fetchone()[0]
    tot1 = con.execute("SELECT SUM(cantidad * precio_unit) FROM detalle_pedido WHERE id_pedido = 1").fetchone()[0]
    horas6 = con.execute("SELECT SUM(o.lote * p.seg_estampado) / 3600.0 FROM orden_produccion o "
                         "JOIN producto p ON p.id_producto = o.id_producto WHERE o.semana = 6").fetchone()[0]
    # el script SQL de la unidad
    res = []
    for q in sentencias((SQL / "u02_mer.sql").read_text(encoding="utf-8")):
        cur = con.execute(q)
        res.append({"sql": q, "cols": [d[0] for d in cur.description], "filas": cur.fetchall()})
    n_fk = sum(len(v) for v in fks.values())
    assert len(res[1]["filas"]) == n_fk
    con.close()
    C = conteos(CASO)
    C.update({"tablas": len(tablas), "columnas": sum(len(c) for c in cols.values()), "fks": n_fk,
              "forma_rel": forma_rel, "prob": prob, "margen_polerones": pol, "total_pedido_1": tot1,
              "horas_s6": horas6, "sql": res,
              "atributos_guardados": sum(1 for ats in M["atributos"].values() for _, t in ats if t != "deriv"),
              "derivados": sum(1 for ats in M["atributos"].values() for _, t in ats if t == "deriv")})
    return C


def cadena(C):
    import json
    J = json.loads((AQUI / "caso_estampa_sur_bd.json").read_text(encoding="utf-8"))
    ok = not C["prob"] and C["tablas"] == len(J["tablas"]) == C["entidades"] + len(CASO_TABLA_REL)
    ok &= abs(C["horas_s6"] - sum(r[2] for r in J["u11_produccion_semana_6"])) < 1e-9
    print("CADENA:", "OK, el diagrama calza con datos/esquema.sql: 6 entidades + 2 relaciones con tabla = "
          "8 tablas; cada atributo guardado es columna, cada derivado no lo es, cada rombo es una clave foránea"
          if ok else f"NO calza: {C['prob']}")
    return ok


# =============================================================================== lo que el .md tiene que decir
def esperados(X, C):
    s = []
    s += [f"| {a} | {b} |" for a, b in E21]
    s += [f"| `{a}` | {b} |" for a, b in E22]
    s += [f"| ({k}) `{n}` | {g} |" for k, n, g, _ in X["e03"]]
    s += [f"| {a} | `{b}` |" for a, b in E28]
    e = X["e06"]; s += [f"{e['atenciones']} atenciones", f"{e['pares']} pares distintos", f"se perderían {e['perdidas']}"]
    e = X["e09"]; s += [f"{e['junta']} combinaciones", f"{e['n_falsas']} son falsas"]
    s += [f"({t}, {a}, {p})" for t, a, p in e["falsas"]]
    s += [f"${v // 1000}.{v % 1000:03d}" for v in E29_TARIFA.values()]
    s += ["| " + e for e, _ in E27]
    g = X["escuela"]; s += [f"{g['entidades']} entidades y {g['relaciones']} relaciones ({g['grados'][2]} binarias y {g['grados'][1]} unaria)"]
    g = X["gimnasio"]; s += [f"{g['entidades']} entidades y {g['relaciones']} relaciones"]
    b = X["banco"]; s += [f"{b['entidades']} entidades y {b['relaciones']} relaciones"]
    l = X["liga"]; s += [f"{l['entidades']} entidades y {l['relaciones']} relaciones",
                         f"{l['grados'].get(2, 0)} binarias", f"{l['grados'].get(1, 0)} unaria"]
    s += [f"{C['entidades']} entidades", f"{C['relaciones']} relaciones", f"{C['tablas']} tablas",
          f"{C['atributos_guardados']} atributos guardados", f"{C['derivados']} derivados",
          f"{C['fks']} claves foráneas", f"${C['margen_polerones'] // 1000}.{C['margen_polerones'] % 1000:03d}",
          f"{C['horas_s6']:.0f} horas"]
    tot = C["total_pedido_1"]; s.append(f"${tot // 1000}.{tot % 1000:03d}")
    s += [f"`{v}`" for v in C["forma_rel"].values()]
    return s


def sql_en_md(md, res):
    plano = " ".join(md.split())
    lineas = set(l.strip() for l in md.splitlines())
    faltan = []
    for r in res:
        if " ".join(r["sql"].split()) not in plano:
            faltan.append(f"sentencia: {r['sql'][:60]}")
        if "| " + " | ".join(r["cols"]) + " |" not in lineas:
            faltan.append(f"encabezado: {r['cols']}")
        faltan += [f"fila: {fila_md(f)}" for f in r["filas"] if fila_md(f) not in lineas]
    return faltan


if __name__ == "__main__":
    for nombre, D in (("ejemplo", ESCUELA), ("2.4", GIMNASIO), ("2.5", BANCO), ("2.10", LIGA), ("caso", CASO)):
        p = revisar_forma(D, nombre)
        assert not p, p
        print(f"== {nombre}: {conteos(D)}")
    X = ejercicios()
    for k, v in X.items():
        print(f"== {k}: {v}")
    C = caso()
    print("== caso:", {k: v for k, v in C.items() if k != "sql"})
    for r in C["sql"]:
        print("  ", r["sql"].splitlines()[0])
        print("| " + " | ".join(r["cols"]) + " |")
        for f in r["filas"]:
            print(fila_md(f))
    for archivo, (D, titulo) in FIGURAS.items():
        svg(D, archivo, titulo)
    print("figuras:", ", ".join(FIGURAS))
    if not cadena(C):
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = " ".join(md.replace("{,}", ",").replace("{.}", ".").split())
        faltan = [x for x in esperados(X, C) if " ".join(x.split()) not in md_n]
        faltan += sql_en_md(md, C["sql"])
        faltan += [f"figura {f}" for f in FIGURAS if f"figuras/{f}" not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
