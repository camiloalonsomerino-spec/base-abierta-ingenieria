"""Unidad 7 · Redes y árbol de expansión mínima. Recalcula todas las cifras; con --revisar las busca en el .md.

Este script:

1. declara los datos del ejemplo, de los diez ejercicios y toma la red del caso integrador;
2. corre Kruskal y Prim paso a paso (con la regla de desempate que dice la unidad) y genera sus tablas
   en Markdown; con --tablas las imprime para pegarlas en el .md;
3. compara cada árbol con el de networkx y con el programa entero (restricciones de subconjuntos,
   resuelto con scipy milp) y, en los grafos chicos, con la enumeración de todos los árboles;
4. corre los modelos OPL de modelos/u07_*.mod con herramientas/opl.py (si hay CPLEX) y exige que el
   objetivo y cada x coincidan con Python;
5. dibuja las figuras SVG en unidades/figuras/;
6. compara la pieza del caso con caso_estampa_sur_red.py (CADENA) y, con --revisar, busca cada cifra
   y cada fila de tabla en el .md.

    python u07_arbol_minimo.py            # imprime los resultados
    python u07_arbol_minimo.py --tablas   # además imprime las tablas en Markdown
    python u07_arbol_minimo.py --revisar  # además busca todo en el .md
"""
from itertools import combinations
from pathlib import Path
import importlib.util, math, sys

import networkx as nx
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
FIGURAS = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "07-arbol-de-expansion-minima.md"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402


# ---------------------------------------------------------------- formato chileno
def fmt(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(x):
    return "$" + fmt(x, 0)


def caso():
    spec = importlib.util.spec_from_file_location("caso", AQUI / "caso_estampa_sur_red.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- datos (originales; pasados por colisiones.py)
EJEMPLO = {  # agua potable rural: metros de tubería entre el estanque y cinco sectores
    "nodos": ["Estanque", "Alto", "Bajo", "Capilla", "Escuela", "Feria"],
    "aristas": [("Estanque", "Alto", 430), ("Estanque", "Bajo", 385), ("Alto", "Bajo", 245),
                ("Alto", "Capilla", 515), ("Bajo", "Capilla", 465), ("Bajo", "Escuela", 610),
                ("Capilla", "Escuela", 335), ("Capilla", "Feria", 295), ("Escuela", "Feria", 405),
                ("Alto", "Feria", 645)],
    "precio_metro": 8_400,
}
E71 = {"nodos": [1, 2, 3, 4, 5, 6, 7],
       "aristas": [(1, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5), (5, 6), (4, 6)],
       "nueva": (6, 7),
       "T1": [(1, 2), (2, 3), (3, 5), (5, 6), (4, 6), (6, 7)],
       "T2": [(1, 2), (1, 3), (2, 3), (4, 5), (5, 6), (6, 7)]}
E72 = {"nodos": ["P", "Q", "R", "S", "T"],
       "aristas": [("P", "Q", 6), ("P", "R", 9), ("Q", "R", 4), ("Q", "S", 7), ("R", "S", 5), ("R", "T", 8), ("S", "T", 3)]}
E73 = {"nodos": ["A", "B", "C", "D", "E", "F", "G"],   # parque eólico, cientos de metros de cable
       "aristas": [("A", "B", 12), ("A", "C", 9), ("B", "C", 7), ("B", "D", 14), ("C", "D", 10), ("C", "E", 11),
                   ("D", "E", 6), ("D", "F", 8), ("E", "F", 13), ("E", "G", 9), ("F", "G", 5), ("B", "F", 15)]}
E74 = {"nodos": ["K", "L", "M", "N", "O", "P"],         # camping, metros de cable
       "aristas": [("K", "L", 35), ("K", "M", 50), ("K", "N", 60), ("L", "M", 25), ("L", "O", 70), ("M", "N", 30),
                   ("M", "O", 45), ("N", "P", 40), ("O", "P", 20), ("M", "P", 55)],
       "inicio": "K", "obligada": ("K", "N"), "prohibida": ("N", "P")}
E75 = {"nodos": ["1", "2", "3", "4"],
       "aristas": [("1", "2", 5), ("1", "3", 6), ("2", "3", 4), ("2", "4", 9), ("3", "4", 8)]}
E78 = {"nodos": ["U", "V", "W", "X", "Y", "Z"],         # calidad de señal (0 a 100)
       "aristas": [("U", "V", 72), ("U", "W", 65), ("V", "W", 80), ("V", "X", 58), ("W", "X", 77), ("W", "Y", 61),
                   ("X", "Y", 84), ("X", "Z", 69), ("Y", "Z", 74), ("V", "Z", 50)]}
E79 = {"cae": ("Lagos", "Valle"), "nueva": "Bosque",
       "nuevas": [("Bosque", "Lagos", 6), ("Bosque", "Valle", 11), ("Bosque", "Puerto", 9)]}
E710 = {"nodos": ["Central", "A", "B", "C", "D", "E"],  # metros de cable; la central tiene 2 puertos
        "aristas": [("Central", "C", 35), ("Central", "D", 85), ("Central", "E", 175), ("A", "B", 265),
                    ("A", "C", 280), ("A", "D", 205), ("B", "E", 95), ("C", "D", 110)],
        "centro": "Central", "puertos": 2}


def red_caso():
    m = caso()
    return {"nodos": list(m.NODOS), "aristas": [(a, b, d) for (a, b), d in m.CAMINOS.items()]}


# ---------------------------------------------------------------- algoritmos paso a paso
def abrev(n):
    n = str(n)
    return n[:3] if len(n) > 3 else n


def camino_en_bosque(arbol, a, b):
    """Camino de a a b en el bosque (lista de aristas (u, v, w)); None si no están conectados."""
    G = nx.Graph()
    G.add_weighted_edges_from(arbol)
    if a not in G or b not in G or not nx.has_path(G, a, b):
        return None
    return nx.shortest_path(G, a, b)


def kruskal(nodos, aristas, maximo=False, obligadas=()):
    """Ordena por peso (en empate, el orden de la lista de datos) y agrega lo que no cierra ciclo."""
    orden = sorted(range(len(aristas)), key=lambda k: ((-1 if maximo else 1) * aristas[k][2], k))
    arbol, pasos, total = [], [], 0
    for e in obligadas:
        arbol.append(e); total += e[2]
        pasos.append({"arista": e, "accion": "obligada", "ciclo": None, "total": total})
    for k in orden:
        a, b, w = aristas[k]
        if len(arbol) == len(nodos) - 1:
            break
        if any({a, b} == {x, y} for x, y, _ in obligadas):
            continue
        c = camino_en_bosque(arbol, a, b)
        if c is None:
            arbol.append((a, b, w)); total += w
            pasos.append({"arista": (a, b, w), "accion": "entra", "ciclo": None, "total": total})
        else:
            pasos.append({"arista": (a, b, w), "accion": "descarta", "ciclo": c + [a], "total": total})
    sin_evaluar = [aristas[k] for k in orden if aristas[k] not in [p["arista"] for p in pasos]
                   and not any({aristas[k][0], aristas[k][1]} == {x, y} for x, y, _ in obligadas)]
    return {"pasos": pasos, "arbol": arbol, "total": total, "sin_evaluar": sin_evaluar}


def prim(nodos, aristas, inicio):
    """Etiqueta de cada nodo fuera del árbol = arista más barata que lo une al árbol. Entra la menor;
    en empate, el nodo que aparece primero en la lista de nodos. Una etiqueta cambia solo si baja."""
    INF = math.inf
    et = {n: (INF, None) for n in nodos}
    dentro, filas, arbol, total = [inicio], [], [], 0
    def actualizar(v):
        for a, b, w in aristas:
            for x, y in ((a, b), (b, a)):
                if x == v and y not in dentro and w < et[y][0]:
                    et[y] = (w, v)
    actualizar(inicio)
    filas.append({"entra": inicio, "arista": None, "et": dict(et), "dentro": list(dentro)})
    while len(dentro) < len(nodos):
        fuera = [n for n in nodos if n not in dentro]
        k = min(fuera, key=lambda n: (et[n][0], nodos.index(n)))
        w, desde = et[k]
        dentro.append(k); arbol.append((desde, k, w)); total += w
        actualizar(k)
        filas.append({"entra": k, "arista": (desde, k, w), "et": dict(et), "dentro": list(dentro)})
    return {"filas": filas, "arbol": arbol, "total": total}


def todos_los_arboles(nodos, aristas):
    """Lista de (peso, conjunto de aristas) de TODOS los árboles de expansión (solo grafos chicos)."""
    res = []
    for comb in combinations(aristas, len(nodos) - 1):
        G = nx.Graph(); G.add_nodes_from(nodos); G.add_weighted_edges_from(comb)
        if nx.is_tree(G):
            res.append((sum(w for *_, w in comb), comb, G))
    return res


def milp_arbol(nodos, aristas, sin_ciclos=True, grado=None):
    """Programa entero del árbol mínimo: Σx = n−1 y Σ_{e ⊆ S} x_e ≤ |S|−1 para todo S con |S| ≥ 3."""
    m = len(aristas)
    c = np.array([w for *_, w in aristas], dtype=float)
    filas, li, ls = [np.ones(m)], [len(nodos) - 1], [len(nodos) - 1]
    if sin_ciclos:
        for k in range(3, len(nodos) + 1):
            for S in combinations(nodos, k):
                S = set(S)
                filas.append(np.array([1.0 if a in S and b in S else 0.0 for a, b, _ in aristas]))
                li.append(-np.inf); ls.append(len(S) - 1)
    if grado:
        centro, tope = grado
        filas.append(np.array([1.0 if centro in (a, b) else 0.0 for a, b, _ in aristas]))
        li.append(-np.inf); ls.append(tope)
    r = milp(c, constraints=LinearConstraint(np.array(filas), li, ls), integrality=np.ones(m), bounds=Bounds(0, 1))
    assert r.status == 0, r.message
    x = [int(round(v)) for v in r.x]
    return {"z": r.fun, "x": x, "arbol": [e for e, v in zip(aristas, x) if v]}


def nx_mst(nodos, aristas, maximo=False):
    G = nx.Graph(); G.add_nodes_from(nodos); G.add_weighted_edges_from(aristas)
    T = (nx.maximum_spanning_tree if maximo else nx.minimum_spanning_tree)(G)
    return sum(d["weight"] for *_, d in T.edges(data=True)), T


def mismo_arbol(a1, a2):
    return {frozenset((a, b)) for a, b, *_ in a1} == {frozenset((a, b)) for a, b, *_ in a2}


# ---------------------------------------------------------------- tablas en Markdown
def guion(*ns):
    return "–".join(str(n) for n in ns)


def tabla_kruskal(K, unidad=""):
    filas = ["| Paso | Arista | Peso | ¿Sus extremos ya están conectados? | Acción | Acumulado |",
             "|---|---|---|---|---|---|"]
    for k, p in enumerate(K["pasos"], 1):
        a, b, w = p["arista"]
        if p["accion"] == "entra":
            q, acc = "no", "entra"
        elif p["accion"] == "obligada":
            q, acc = "(obligada)", "entra primero"
        else:
            q, acc = "sí: cerraría el ciclo " + guion(*p["ciclo"]), "se descarta"
        filas.append(f"| {k} | {guion(a, b)} | {fmt(w)}{unidad} | {q} | {acc} | {fmt(p['total'])}{unidad} |")
    return filas


def tabla_prim(P, nodos, inicio):
    otros = [n for n in nodos if n != inicio]
    filas = ["| Paso | Entra al árbol | " + " | ".join(str(n) for n in otros) + " |",
             "|---|---|" + "---|" * len(otros)]
    for k, f in enumerate(P["filas"]):
        if f["arista"] is None:
            entra = f"{f['entra']} (inicio)"
        else:
            d, n, w = f["arista"]
            entra = f"{n} ({guion(d, n)}, {fmt(w)})"
        celdas = []
        for n in otros:
            if n == f["entra"]:
                celdas.append("**entra**")
            elif n in f["dentro"]:
                celdas.append("✓")
            elif f["et"][n][0] == math.inf:
                celdas.append("∞")
            else:
                w, d = f["et"][n]
                celdas.append(f"[{fmt(w)}, {abrev(d)}]")
        filas.append(f"| {k} | {entra} | " + " | ".join(celdas) + " |")
    return filas


def tabla_matriz(nodos, aristas):
    w = {}
    for a, b, p in aristas:
        w[(a, b)] = w[(b, a)] = p
    filas = ["| | " + " | ".join(map(str, nodos)) + " |", "|---|" + "---|" * len(nodos)]
    for i in nodos:
        celdas = ["0" if i == j else (fmt(w[(i, j)]) if (i, j) in w else "—") for j in nodos]
        filas.append(f"| **{i}** | " + " | ".join(celdas) + " |")
    return filas


# ---------------------------------------------------------------- figuras SVG
TINTA, SUAVE, LINEA, ACENTO, PAPEL, CLARO = "#2B2F33", "#5F656B", "#B9B5AE", "#E2622A", "#F2F1EF", "#FCE3D6"


def _caja(n):
    return 8.2 * len(str(n)) + 20, 26


def _borde(c, hacia, n):
    (x, y), (hx, hy) = c, hacia
    w, h = _caja(n)
    dx, dy = hx - x, hy - y
    if dx == 0 and dy == 0:
        return x, y
    t = min((w / 2 + 3) / abs(dx) if dx else math.inf, (h / 2 + 3) / abs(dy) if dy else math.inf)
    return x + dx * t, y + dy * t


def svg_red(archivo, pos, aristas, *, dirigido=False, destacadas=(), etiqueta=None, curva=None,
            lado_s=None, punteadas=(), nota=None, ancho=640, alto=440):
    etiqueta, curva = etiqueta or {}, curva or {}
    dest = {frozenset(e) if not dirigido else tuple(e) for e in destacadas}
    punt = {tuple(e) for e in punteadas}
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}" '
         f'font-family="Segoe UI, sans-serif" font-size="12">',
         f'<rect width="{ancho}" height="{alto}" fill="white"/>',
         '<defs>'
         f'<marker id="f0" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{SUAVE}"/></marker>'
         f'<marker id="f1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{ACENTO}"/></marker>'
         '</defs>']
    textos = []
    for a, b in aristas:
        clave = (a, b) if dirigido else frozenset((a, b))
        es = clave in dest
        color, grosor = (ACENTO, 3.6) if es else (LINEA, 1.6)
        guiones = ' stroke-dasharray="6 4"' if (a, b) in punt else ""
        marca = f' marker-end="url(#{"f1" if es else "f0"})"' if dirigido else ""
        pa, pb = pos[a], pos[b]
        if (a, b) in curva or (b, a) in curva:
            cx, cy = curva.get((a, b), curva.get((b, a)))
            p0, p1 = _borde(pa, (cx, cy), a), _borde(pb, (cx, cy), b)
            s.append(f'<path d="M{p0[0]:.1f},{p0[1]:.1f} Q{cx},{cy} {p1[0]:.1f},{p1[1]:.1f}" fill="none" '
                     f'stroke="{color}" stroke-width="{grosor}"{guiones}{marca}/>')
            mx, my = 0.25 * p0[0] + 0.5 * cx + 0.25 * p1[0], 0.25 * p0[1] + 0.5 * cy + 0.25 * p1[1]
        else:
            p0, p1 = _borde(pa, pb, a), _borde(pb, pa, b)
            s.append(f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" '
                     f'stroke="{color}" stroke-width="{grosor}"{guiones}{marca}/>')
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        t = etiqueta.get((a, b), etiqueta.get((b, a)))
        if t is not None:
            w = 7.0 * len(str(t)) + 8
            textos.append(f'<rect x="{mx - w / 2:.1f}" y="{my - 9:.1f}" width="{w:.1f}" height="17" rx="3" fill="white" '
                          f'stroke="{ACENTO if es else LINEA}" stroke-width="0.8"/>'
                          f'<text x="{mx:.1f}" y="{my + 4:.1f}" text-anchor="middle" fill="{ACENTO if es else TINTA}" '
                          f'font-weight="{600 if es else 400}">{t}</text>')
    s += textos
    for n, (x, y) in pos.items():
        w, h = _caja(n)
        relleno = CLARO if lado_s and n in lado_s else PAPEL
        s.append(f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w:.1f}" height="{h}" rx="13" fill="{relleno}" '
                 f'stroke="{TINTA}" stroke-width="1.3"/>'
                 f'<text x="{x}" y="{y + 4.5:.1f}" text-anchor="middle" fill="{TINTA}" font-weight="600">{n}</text>')
    if nota:
        s.append(f'<text x="{ancho / 2}" y="{alto - 10}" text-anchor="middle" fill="{SUAVE}" font-size="11">{nota}</text>')
    s.append("</svg>")
    FIGURAS.mkdir(parents=True, exist_ok=True)
    (FIGURAS / archivo).write_text("\n".join(s), encoding="utf-8")


POS_CASO = {"Costa": (90, 60), "Puerto": (300, 50), "Lagos": (530, 110), "Taller": (110, 220),
            "Centro": (300, 190), "Cruce": (330, 330), "Valle": (540, 270), "Cerro": (520, 400)}
CURVA_CASO = {("Cerro", "Costa"): (20, 470)}


def figuras(R):
    E = EJEMPLO
    pos = {"Estanque": (90, 200), "Alto": (260, 70), "Bajo": (260, 300), "Capilla": (450, 190),
           "Escuela": (580, 330), "Feria": (590, 70)}
    svg_red("u07_ejemplo_agua.svg", pos, [(a, b) for a, b, _ in E["aristas"]],
            destacadas=[(a, b) for a, b, _ in R["ejemplo"]["kruskal"]["arbol"]],
            etiqueta={(a, b): f"{w} m" for a, b, w in E["aristas"]}, curva={("Alto", "Feria"): (420, 10)},
            nota="En naranjo, el árbol de expansión mínima: 1.725 m de tubería", ancho=680, alto=400)
    C = red_caso()
    svg_red("u07_caso_red.svg", POS_CASO, [(a, b) for a, b, _ in C["aristas"]],
            destacadas=[(a, b) for a, b, _ in R["caso"]["kruskal"]["arbol"]],
            etiqueta={(a, b): f"{w}" for a, b, w in C["aristas"]}, curva=CURVA_CASO,
            nota="Estampa Sur: los 14 caminos posibles (km); en naranjo, los 7 enlaces del árbol mínimo, 56 km",
            ancho=640, alto=480)
    pos71 = {1: (80, 120), 2: (230, 50), 3: (230, 200), 4: (400, 50), 5: (400, 200), 6: (550, 125), 7: (620, 230)}
    svg_red("u07_e01_grafo.svg", pos71, list(E71["aristas"]),
            nota="Ejercicio 7.1: siete nodos y ocho aristas (el nodo 7 no tiene aristas)", ancho=680, alto=280)


# ---------------------------------------------------------------- resultados
def resultados():
    R = {}
    E = EJEMPLO
    K, P = kruskal(E["nodos"], E["aristas"]), prim(E["nodos"], E["aristas"], "Estanque")
    R["ejemplo"] = {"kruskal": K, "prim": P, "costo": K["total"] * E["precio_metro"]}
    C = red_caso()
    R["caso"] = {"kruskal": kruskal(C["nodos"], C["aristas"]), "prim": prim(C["nodos"], C["aristas"], "Taller")}
    # 7.1 · conceptos
    G = nx.Graph(); G.add_nodes_from(E71["nodos"]); G.add_edges_from(E71["aristas"])
    G2 = G.copy(); G2.add_edge(*E71["nueva"])
    def es_arbol(T):
        H = nx.Graph(); H.add_nodes_from(E71["nodos"]); H.add_edges_from(T); return nx.is_tree(H), nx.number_connected_components(H)
    R["e71"] = {"n": G.number_of_nodes(), "m": G.number_of_edges(), "grados": dict(G.degree()),
                "componentes": nx.number_connected_components(G), "m2": G2.number_of_edges(),
                "sobran": G2.number_of_edges() - (len(E71["nodos"]) - 1), "T1": es_arbol(E71["T1"]), "T2": es_arbol(E71["T2"]),
                "ciclos_T2": nx.cycle_basis(nx.Graph(E71["T2"]))}
    assert sum(R["e71"]["grados"].values()) == 2 * R["e71"]["m"]
    # 7.2 · representación
    nod, ar = E72["nodos"], E72["aristas"]
    inc = [[(1 if a == n else (-1 if b == n else 0)) for a, b, _ in ar] for n in nod]
    assert all(sum(col) == 0 for col in zip(*inc))
    R["e72"] = {"m": len(ar), "vacias": len(nod) * (len(nod) - 1) - 2 * len(ar), "densidad": len(ar) / math.comb(len(nod), 2),
                "grados": {n: sum(1 for a, b, _ in ar if n in (a, b)) for n in nod}, "incidencia": inc,
                "vecinos": {n: [(b if a == n else a, w) for a, b, w in ar if n in (a, b)] for n in nod}}
    # 7.3 y 7.4
    R["e73"] = kruskal(E73["nodos"], E73["aristas"])
    R["e74"] = prim(E74["nodos"], E74["aristas"], E74["inicio"])
    # 7.5 · cuatro nodos: con y sin las restricciones de ciclos
    R["e75"] = {"kruskal": kruskal(E75["nodos"], E75["aristas"]), "con": milp_arbol(E75["nodos"], E75["aristas"]),
                "sin": milp_arbol(E75["nodos"], E75["aristas"], sin_ciclos=False),
                "subconjuntos3": [S for S in combinations(E75["nodos"], 3)]}
    # 7.6 · sensibilidad sobre la red del 7.3: umbrales por barrido
    base = R["e73"]["total"]
    arbol73 = {frozenset((a, b)) for a, b, _ in R["e73"]["arbol"]}
    def entra_si(arista, valores):
        """Mayor valor (entero) del peso de una arista fuera del árbol con el que entra a algún árbol mínimo
        y el valor por debajo del cual entra a todos (cambio estricto)."""
        out = {}
        for v in valores:
            ar2 = [(a, b, v if {a, b} == set(arista) else w) for a, b, w in E73["aristas"]]
            arboles = todos_los_arboles(E73["nodos"], ar2)
            mn = min(p for p, *_ in arboles)
            minimos = [comb for p, comb, _ in arboles if p == mn]
            out[v] = (mn, any(any({a, b} == set(arista) for a, b, _ in comb) for comb in minimos),
                      all(any({a, b} == set(arista) for a, b, _ in comb) for comb in minimos))
        return out
    s_EG, s_BD = entra_si(("E", "G"), range(5, 12)), entra_si(("B", "D"), range(8, 16))
    s_CD, s_AC = entra_si(("C", "D"), range(8, 15)), entra_si(("A", "C"), range(8, 15))
    R["e76"] = {"EG": s_EG, "BD": s_BD, "CD": s_CD, "AC": s_AC, "base": base}
    # umbrales: E-G entra a todos con < 8 y a alguno con 8; B-D con < 10 (10 empata); C-D sale con > 11; A-C con > 12
    assert s_EG[7][2] and s_EG[8][1] and not s_EG[8][2] and not s_EG[9][1]
    assert s_BD[9][2] and s_BD[10][1] and not s_BD[10][2] and not s_BD[11][1]
    assert s_CD[11][1] and not s_CD[11][2] and not s_CD[12][1] and s_CD[10][2]
    assert s_AC[12][1] and not s_AC[12][2] and not s_AC[13][1]
    R["e76"]["EG_nuevo"] = s_EG[7][0]; R["e76"]["CD_sube"] = s_CD[12][0]
    # 7.7 · obligada y prohibida en la red del 7.4
    ob = next(e for e in E74["aristas"] if {e[0], e[1]} == set(E74["obligada"]))
    K_ob = kruskal(E74["nodos"], E74["aristas"], obligadas=[ob])
    sin = [e for e in E74["aristas"] if {e[0], e[1]} != set(E74["prohibida"])]
    K_pr = kruskal(E74["nodos"], sin)
    tod = todos_los_arboles(E74["nodos"], E74["aristas"])
    assert K_ob["total"] == min(p for p, comb, _ in tod if ob in comb)
    assert K_pr["total"] == nx_mst(E74["nodos"], sin)[0]
    R["e77"] = {"obligada": K_ob, "prohibida": K_pr, "extra_ob": K_ob["total"] - R["e74"]["total"],
                "extra_pr": K_pr["total"] - R["e74"]["total"]}
    # 7.8 · máximo árbol y cuello de botella
    Kmax = kruskal(E78["nodos"], E78["aristas"], maximo=True)
    tod = todos_los_arboles(E78["nodos"], E78["aristas"])
    assert Kmax["total"] == max(p for p, *_ in tod) == nx_mst(E78["nodos"], E78["aristas"], maximo=True)[0]
    mejor_min = max(min(w for *_, w in comb) for _, comb, _ in tod)
    R["e78"] = {"kruskal": Kmax, "mas_debil": min(w for *_, w in Kmax["arbol"]), "mejor_min": mejor_min,
                "maximo_U": max(w for a, b, w in E78["aristas"] if "U" in (a, b))}
    assert R["e78"]["mas_debil"] == mejor_min == R["e78"]["maximo_U"]
    # 7.9 · el caso: cae un enlace y llega una tienda nueva
    arbol = R["caso"]["kruskal"]["arbol"]
    cae = next(e for e in arbol if {e[0], e[1]} == set(E79["cae"]))
    resto = [e for e in arbol if e is not cae]
    Gr = nx.Graph(); Gr.add_nodes_from(C["nodos"]); Gr.add_weighted_edges_from(resto)
    lado = nx.node_connected_component(Gr, E79["cae"][0])
    cruzan = sorted([e for e in C["aristas"] if (e[0] in lado) != (e[1] in lado) and e is not cae
                     and {e[0], e[1]} != set(E79["cae"])], key=lambda e: e[2])
    sin_cae = [e for e in C["aristas"] if {e[0], e[1]} != set(E79["cae"])]
    assert R["caso"]["kruskal"]["total"] - cae[2] + cruzan[0][2] == nx_mst(C["nodos"], sin_cae)[0]
    nodos9 = C["nodos"] + [E79["nueva"]]
    K_nuevo = kruskal(nodos9, C["aristas"] + E79["nuevas"])
    K_solo_arbol = kruskal(nodos9, arbol + E79["nuevas"])
    assert K_nuevo["total"] == K_solo_arbol["total"] == nx_mst(nodos9, C["aristas"] + E79["nuevas"])[0]
    R["e79"] = {"lado": sorted(lado), "cruzan": cruzan, "reemplazo": cruzan[0], "total_cae": R["caso"]["kruskal"]["total"] - cae[2] + cruzan[0][2],
                "nuevo": K_nuevo, "solo_arbol": K_solo_arbol}
    # 7.10 · grado máximo en la central: programa entero contra Kruskal con tope
    E = E710
    K0 = kruskal(E["nodos"], E["aristas"])
    grado0 = sum(1 for a, b, _ in K0["arbol"] if E["centro"] in (a, b))
    # Kruskal que se salta las aristas que pasarían el tope de puertos
    arbol, total, pasos = [], 0, []
    for a, b, w in sorted(E["aristas"], key=lambda e: e[2]):
        if len(arbol) == len(E["nodos"]) - 1: break
        g = sum(1 for x, y, _ in arbol if E["centro"] in (x, y))
        if camino_en_bosque(arbol, a, b) is not None:
            pasos.append(((a, b, w), "ciclo")); continue
        if E["centro"] in (a, b) and g >= E["puertos"]:
            pasos.append(((a, b, w), "tope")); continue
        arbol.append((a, b, w)); total += w; pasos.append(((a, b, w), "entra"))
    opt = milp_arbol(E["nodos"], E["aristas"], grado=(E["centro"], E["puertos"]))
    tod = todos_los_arboles(E["nodos"], E["aristas"])
    assert opt["z"] == min(p for p, comb, G in tod if G.degree(E["centro"]) <= E["puertos"])
    R["e710"] = {"mst": K0["total"], "grado_mst": grado0, "voraz": total, "voraz_arbol": arbol, "voraz_pasos": pasos,
                 "opt": opt["z"], "opt_arbol": opt["arbol"]}
    assert total > opt["z"] > K0["total"]
    # comprobaciones de todos los árboles contra networkx y el programa entero
    for nombre, nod, ar, T in [("ejemplo", EJEMPLO["nodos"], EJEMPLO["aristas"], R["ejemplo"]["kruskal"]),
                               ("caso", C["nodos"], C["aristas"], R["caso"]["kruskal"]),
                               ("e73", E73["nodos"], E73["aristas"], R["e73"]), ("e74", E74["nodos"], E74["aristas"], R["e74"]),
                               ("e75", E75["nodos"], E75["aristas"], R["e75"]["kruskal"])]:
        z_nx, Tnx = nx_mst(nod, ar)
        assert T["total"] == z_nx == milp_arbol(nod, ar)["z"], nombre
        tod = todos_los_arboles(nod, ar)
        minimos = [comb for p, comb, _ in tod if p == T["total"]]
        assert len(minimos) == 1 and mismo_arbol(minimos[0], T["arbol"]), (nombre, "el árbol mínimo no es único")
    assert R["ejemplo"]["prim"]["total"] == R["ejemplo"]["kruskal"]["total"]
    assert R["caso"]["prim"]["total"] == R["caso"]["kruskal"]["total"]
    assert mismo_arbol(R["caso"]["prim"]["arbol"], R["caso"]["kruskal"]["arbol"])
    return R


# ---------------------------------------------------------------- OPL
def dat_arbol(nodos, aristas, extra=""):
    lin = ["Nodos = {" + ", ".join(f'"{n}"' for n in nodos) + "};", "Aristas = {"]
    lin += [f'  <"{a}", "{b}", {w}>' + ("," if k < len(aristas) - 1 else "") for k, (a, b, w) in enumerate(aristas)]
    lin.append("};")
    return "\n".join(lin) + ("\n" + extra if extra else "") + "\n"


def escribir_dats():
    C = red_caso()
    cab = "// Unidad 7 · {}\n// Base abierta de ingeniería. Lo genera verificacion/u07_arbol_minimo.py.\n\n"
    (MODELOS / "u07_arbol_minimo.dat").write_text(
        cab.format("caso integrador: los 14 caminos posibles de Estampa Sur, en km") + dat_arbol(C["nodos"], C["aristas"]), encoding="utf-8")
    (MODELOS / "u07_e05_cuatro_nodos.dat").write_text(
        cab.format("ejercicio 7.5: cuatro nodos") + dat_arbol(E75["nodos"], E75["aristas"]), encoding="utf-8")
    (MODELOS / "u07_e10_grado.dat").write_text(
        cab.format("ejercicio 7.10: la central tiene dos puertos libres (metros de cable)")
        + dat_arbol(E710["nodos"], E710["aristas"], f'centro = "{E710["centro"]}";\npuertos = {E710["puertos"]};'), encoding="utf-8")


def comparar_con_opl(R):
    C = red_caso()
    corridas = [("u07_arbol_minimo.mod", "u07_arbol_minimo.dat", C["aristas"], R["caso"]["kruskal"]["arbol"], R["caso"]["kruskal"]["total"]),
                ("u07_arbol_minimo.mod", "u07_e05_cuatro_nodos.dat", E75["aristas"], R["e75"]["kruskal"]["arbol"], R["e75"]["kruskal"]["total"]),
                ("u07_e10_grado.mod", "u07_e10_grado.dat", E710["aristas"], R["e710"]["opt_arbol"], R["e710"]["opt"])]
    salida = {}
    for mod, dat, aristas, arbol, z in corridas:
        r = correr(MODELOS / mod, MODELOS / dat)
        if r is None:
            print("OPL: oplrun no está instalado; se comparan solo las cifras de Python")
            return None
        assert r["codigo"] == 0 and r["objetivo"] is not None, (mod, dat, r["salida"][-400:])
        assert abs(r["objetivo"] - z) < 1e-6, (dat, r["objetivo"], z)
        en = {frozenset((a, b)) for a, b, _ in arbol}
        for a, b, _ in aristas:
            assert abs(r["valores"][f"x[{a},{b}]"] - (1 if frozenset((a, b)) in en else 0)) < 1e-6, (dat, a, b)
        salida[dat] = [l.strip() for l in r["salida"].splitlines() if l.strip().startswith(("largo =", "x["))]
    print(f"OPL: {len(corridas)} corridas con oplrun; objetivo y cada x coinciden con Kruskal y el programa entero de Python")
    return salida


# ---------------------------------------------------------------- cadena y revisión
def cadena(R):
    C = caso().calcular()["u7"]
    T = R["caso"]["kruskal"]
    ok = T["total"] == C["mst_km"] and sorted(sorted([a, b]) for a, b, _ in T["arbol"]) == C["mst_aristas"]
    ok &= R["caso"]["prim"]["total"] == C["mst_km"]
    print("CADENA:", "OK, Kruskal y Prim dan los 56 km y las 7 aristas del caso" if ok else "NO calza")
    return ok


def tablas(R):
    E, C = EJEMPLO, red_caso()
    return {
        "ejemplo_matriz": tabla_matriz(E["nodos"], E["aristas"]),
        "ejemplo_kruskal": tabla_kruskal(R["ejemplo"]["kruskal"], " m"),
        "ejemplo_prim": tabla_prim(R["ejemplo"]["prim"], E["nodos"], "Estanque"),
        "caso_kruskal": tabla_kruskal(R["caso"]["kruskal"], " km"),
        "caso_prim": tabla_prim(R["caso"]["prim"], C["nodos"], "Taller"),
        "e72_matriz": tabla_matriz(E72["nodos"], E72["aristas"]),
        "e73_matriz": tabla_matriz(E73["nodos"], E73["aristas"]),
        "e73_kruskal": tabla_kruskal(R["e73"]),
        "e74_matriz": tabla_matriz(E74["nodos"], E74["aristas"]),
        "e74_prim": tabla_prim(R["e74"], E74["nodos"], E74["inicio"]),
        "e77_obligada": tabla_kruskal(R["e77"]["obligada"]),
        "e78_kruskal": tabla_kruskal(R["e78"]["kruskal"]),
        "e79_nuevo": tabla_kruskal(R["e79"]["solo_arbol"], " km"),
    }


def esperados(R):
    s = []
    E = R["ejemplo"]
    s += [fmt(E["kruskal"]["total"]) + " m", pesos(E["costo"]), pesos(EJEMPLO["precio_metro"])]
    c = R["caso"]["kruskal"]
    s += [f"{c['total']} km"] + [f"{guion(a, b)} ({w})" for a, b, w in c["sin_evaluar"]]
    n = len(red_caso()["nodos"])
    s += [f"{sum(math.comb(n, k) for k in range(3, n + 1))} restricciones", f"{2 ** n - 1} subconjuntos"]
    e = R["e71"]
    s += [f"{e['n']} nodos", f"{e['m']} aristas", f"{e['componentes']} componentes", f"{e['m2']} aristas", f"sacar {e['sobran']}"]
    s += [" · ".join(f"{n}: {g}" for n, g in e["grados"].items())]
    e = R["e72"]
    s += [f"{e['vacias']} celdas", fmt(100 * e["densidad"]) + " %"]
    s += ["| **" + n + "** | " + " | ".join(str(v).replace("-", "−") for v in fila) + " |" for n, fila in zip(E72["nodos"], e["incidencia"])]
    s += [f"{n}: " + ", ".join(f"{v} ({w})" for v, w in e["vecinos"][n]) for n in E72["nodos"]]
    s += [f"{R['e73']['total']} cientos de metros", fmt(R["e73"]["total"] * 100) + " m", f"{R['e74']['total']} m"]
    e = R["e75"]
    s += [f"costo {fmt(e['con']['z'])}", f"costo {fmt(e['sin']['z'])}"]
    e = R["e76"]
    s += [f"baja a {e['EG_nuevo']}", f"sube a {e['CD_sube']}"]
    e = R["e77"]
    s += [f"{e['obligada']['total']} m", f"{e['extra_ob']} m más", f"{e['prohibida']['total']} m", f"{e['extra_pr']} m más"]
    e = R["e78"]
    s += [f"total {e['kruskal']['total']}", f"la más débil vale {e['mas_debil']}"]
    e = R["e79"]
    r = e["reemplazo"]
    s += [f"{guion(r[0], r[1])} ({r[2]} km)", f"{e['total_cae']} km", f"{e['nuevo']['total']} km"]
    e = R["e710"]
    s += [f"{e['mst']} m", f"{e['voraz']} m", f"{int(e['opt'])} m", f"grado {e['grado_mst']}",
          f"{int(e['opt'] - e['mst'])} m más que el árbol sin tope", f"{int(e['voraz'] - e['opt'])} m menos"]
    return s


def codigo_en_md(md):
    faltan = []
    for f in ["u07_arbol_minimo.mod", "u07_e10_grado.mod"]:
        for linea in (MODELOS / f).read_text(encoding="utf-8").splitlines():
            if linea.strip() and linea.rstrip() not in md:
                faltan.append(f"{f}: {linea.strip()}")
    return faltan


if __name__ == "__main__":
    R = resultados()
    print("ejemplo:", R["ejemplo"]["kruskal"]["total"], "m ·", pesos(R["ejemplo"]["costo"]))
    print("caso:", R["caso"]["kruskal"]["total"], "km ·", R["caso"]["kruskal"]["arbol"])
    for k in ["e71", "e72", "e75", "e76", "e78", "e79", "e710"]:
        print(f"== {k}")
        for kk, vv in R[k].items():
            if kk not in ("kruskal", "nuevo", "solo_arbol"):
                print(f"   {kk}: {vv}")
    for k in ["e73", "e74"]:
        print(f"== {k}: total {R[k]['total']} · {R[k]['arbol']}")
    print("== e77:", R["e77"]["obligada"]["total"], R["e77"]["prohibida"]["total"], R["e77"]["prohibida"]["arbol"])
    figuras(R)
    escribir_dats()
    print("figuras: u07_ejemplo_agua.svg, u07_caso_red.svg, u07_e01_grafo.svg · .dat escritos en modelos/")
    if not cadena(R):
        sys.exit(1)
    salida_opl = comparar_con_opl(R)
    T = tablas(R)
    if "--tablas" in sys.argv:
        for k, filas in T.items():
            print(f"\n<!-- {k} -->"); print("\n".join(filas))
        if salida_opl:
            for k, ls in salida_opl.items():
                print(f"\n<!-- salida OPL {k} -->"); print("\n".join(ls))
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        md_plano = " ".join(md_n.split())
        faltan = [x for x in esperados(R) if x not in md_n and x not in md_plano]
        lineas = set(l.rstrip() for l in md.splitlines())
        faltan += [f"tabla {k}: {f}" for k, filas in T.items() for f in filas[2:] if f not in lineas]
        faltan += codigo_en_md(md)
        if salida_opl:
            faltan += [f"salida OPL: {l}" for l in salida_opl["u07_arbol_minimo.dat"] if l not in lineas]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
