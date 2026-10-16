"""Unidad 8 · Ruta más corta y flujo máximo. Recalcula todas las cifras; con --revisar las busca en el .md.

Este script:

1. declara los datos del ejemplo, de los diez ejercicios y toma la red del caso integrador;
2. corre Dijkstra (etiquetas temporales y permanentes), Bellman-Ford y Ford-Fulkerson paso a paso, con
   la regla de desempate y de elección de caminos que dice la unidad, y genera sus tablas en Markdown;
3. compara cada resultado con networkx, con el programa lineal o entero (scipy) y, para el flujo
   máximo, con la enumeración de todos los cortes;
4. corre los modelos OPL de modelos/u08_*.mod con herramientas/opl.py (si hay CPLEX) y exige que
   coincidan con Python (objetivo, ruta y, en el flujo máximo, los precios sombra del corte mínimo);
5. dibuja las figuras SVG en unidades/figuras/;
6. compara la pieza del caso con caso_estampa_sur_red.py (CADENA) y, con --revisar, busca cada cifra y
   cada fila de tabla en el .md.

    python u08_ruta_y_flujo.py            # imprime los resultados
    python u08_ruta_y_flujo.py --tablas   # además imprime las tablas en Markdown
    python u08_ruta_y_flujo.py --revisar  # además busca todo en el .md
"""
from itertools import combinations
from pathlib import Path
import importlib.util, math, sys

import networkx as nx
import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parent
MODELOS = RAMO / "modelos"
FIGURAS = RAMO / "unidades" / "figuras"
MD = RAMO / "unidades" / "08-ruta-mas-corta-y-flujo-maximo.md"
sys.path.insert(0, str(RAMO.parents[1] / "herramientas"))
from opl import correr  # noqa: E402

INF = math.inf


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
EJEMPLO = {  # festival: senderos de un sentido; metros y personas por minuto
    "nodos": ["s", "a", "b", "c", "d", "t"],
    "arcos": [("s", "a", 210, 35), ("s", "b", 330, 30), ("a", "b", 85, 20), ("a", "c", 310, 20),
              ("b", "d", 140, 40), ("c", "t", 265, 30), ("d", "t", 195, 30)],
}
E81 = {"nodos": ["1", "2", "3", "4", "5", "6", "7"],   # minutos, red no dirigida
       "aristas": [("1", "2", 7), ("1", "3", 4), ("2", "3", 2), ("2", "4", 6), ("3", "4", 9), ("3", "5", 5),
                   ("4", "5", 3), ("4", "6", 4), ("5", "6", 8), ("5", "7", 11), ("6", "7", 5)]}
E82 = {"nodos": ["s", "1", "2", "3", "t"],
       "arcos": [("s", "1", 4), ("s", "2", 2), ("2", "1", 1), ("1", "3", 5), ("2", "3", 8), ("3", "t", 3), ("1", "t", 10)]}
E83 = {"nodos": ["F", "1", "2", "3", "4", "E"],         # litros por segundo
       "arcos": [("F", "1", 18), ("F", "2", 14), ("1", "3", 10), ("1", "2", 6), ("2", "4", 15), ("3", "E", 12),
                 ("4", "3", 5), ("4", "E", 10)],
       "cortes": [["F"], ["F", "1"], ["F", "1", "3"], ["F", "1", "2", "4"]],
       "tope_nodo": ("4", 9)}
E85 = {"nodos": ["s", "a", "b", "t"],
       "arcos": [("s", "a", 4), ("s", "b", 6), ("b", "a", -3), ("a", "t", 5), ("b", "t", 9)], "suma": 3}
E86 = {"nodos": ["P1", "P2", "A", "B", "D", "C"],       # camiones de áridos por día
       "arcos": [("P1", "A", 25), ("P1", "B", 20), ("P2", "B", 15), ("P2", "D", 25), ("A", "C", 30),
                 ("B", "A", 10), ("B", "D", 15), ("D", "C", 30)],
       "produccion": {"P1": 40, "P2": 35}}
E88 = {"nodos": ["K", "A", "B", "C", "D", "E"],         # km de camino; K es el cuartel
       "aristas": [("K", "A", 4), ("K", "B", 6), ("A", "B", 3), ("A", "C", 8), ("B", "C", 5), ("B", "D", 9),
                   ("C", "D", 2), ("C", "E", 8), ("D", "E", 10)],
       "millones_km": 180}
E89 = {"nodos": ["s", "a", "b", "c", "d", "t"],         # cajas por minuto en cintas
       "arcos": [("s", "a", 20), ("s", "c", 20), ("a", "b", 18), ("a", "d", 10), ("b", "c", 12), ("b", "t", 19),
                 ("c", "d", 11), ("d", "t", 13)],
       "ampliacion": 5}
E810 = {"nodos": ["s", "a", "b", "c", "t"],             # minutos y peaje en pesos
        "arcos": [("s", "a", 8, 3450), ("a", "t", 12, 5850), ("s", "b", 15, 950), ("b", "t", 25, 2150),
                  ("s", "c", 18, 2650), ("c", "t", 16, 2750), ("a", "b", 4, 650)],
        "presupuesto": 6200}


def red_caso():
    m = caso()
    return {"nodos": list(m.NODOS), "aristas": [(a, b, d) for (a, b), d in m.CAMINOS.items()],
            "arcos": [(a, b, u) for (a, b), u in m.CAPACIDAD_DIARIA.items()]}


# ---------------------------------------------------------------- algoritmos
def ab(n):
    n = str(n)
    return n[:3] if len(n) > 3 else n


def dijkstra(nodos, arcos, s, dirigido=True):
    """Etiqueta [d, pred]. Se fija la temporal menor (empate: orden de la lista de nodos); una etiqueta
    cambia solo si baja estrictamente. Devuelve filas para la tabla."""
    ady = {n: [] for n in nodos}
    for a, b, w, *_ in arcos:
        ady[a].append((b, w))
        if not dirigido:
            ady[b].append((a, w))
    et = {n: (INF, None) for n in nodos}
    et[s] = (0, s)
    perm, filas = [], []
    while len(perm) < len(nodos):
        temp = [n for n in nodos if n not in perm and et[n][0] < INF]
        if not temp:
            break
        k = min(temp, key=lambda n: (et[n][0], nodos.index(n)))
        perm.append(k)
        for v, w in ady[k]:
            if v not in perm and et[k][0] + w < et[v][0]:
                et[v] = (et[k][0] + w, k)
        filas.append({"fija": k, "d": et[k][0], "et": dict(et), "perm": list(perm)})
    return {"d": {n: et[n][0] for n in nodos}, "pred": {n: et[n][1] for n in nodos}, "filas": filas, "orden": perm}


def ruta(pred, s, t):
    r = [t]
    while r[-1] != s:
        r.append(pred[r[-1]])
    return r[::-1]


def bellman_ford(nodos, arcos, s):
    d = {n: INF for n in nodos}; d[s] = 0; pred = {s: s}
    rondas = []
    for _ in range(len(nodos) - 1):
        cambio = False
        for a, b, w, *_ in arcos:
            if d[a] + w < d[b]:
                d[b] = d[a] + w; pred[b] = a; cambio = True
        rondas.append(dict(d))
        if not cambio:
            break
    assert all(d[a] + w >= d[b] for a, b, w, *_ in arcos), "ciclo negativo"
    return d, pred, rondas


def ford_fulkerson(nodos, arcos, s, t, modo="profundidad"):
    """arcos: (i, j, cap). modo «profundidad»: primer camino de una búsqueda en profundidad visitando
    los vecinos en el orden de la lista de nodos; «anchura»: el de menos arcos (Edmonds y Karp)."""
    cap = {(i, j): u for i, j, u in arcos}
    f = {k: 0 for k in cap}
    def residual(v, w):
        r = cap[(v, w)] - f[(v, w)] if (v, w) in cap else 0
        if r > 0:
            return r, +1
        if (w, v) in cap and f[(w, v)] > 0:
            return f[(w, v)], -1
        return 0, 0
    iters = []
    while True:
        if modo == "profundidad":
            vis, cam = {s}, [s]
            def dfs(v):
                if v == t:
                    return True
                for w in nodos:
                    if w not in vis and residual(v, w)[0] > 0:
                        vis.add(w); cam.append(w)
                        if dfs(w):
                            return True
                        cam.pop()
                return False
            if not dfs(s):
                break
        else:
            pred, cola = {s: None}, [s]
            while cola:
                v = cola.pop(0)
                for w in nodos:
                    if w not in pred and residual(v, w)[0] > 0:
                        pred[w] = v; cola.append(w)
            if t not in pred:
                break
            cam = [t]
            while cam[-1] != s:
                cam.append(pred[cam[-1]])
            cam = cam[::-1]
        res = [residual(a, b) for a, b in zip(cam, cam[1:])]
        cuello = min(r for r, _ in res)
        for (a, b), (r, sg) in zip(zip(cam, cam[1:]), res):
            if sg > 0:
                f[(a, b)] += cuello
            else:
                f[(b, a)] -= cuello
        iters.append({"camino": list(cam), "res": res, "cuello": cuello, "total": sum(it["cuello"] for it in iters) + cuello})
    # corte: lo alcanzable desde s en la red residual final
    S, pila = {s}, [s]
    while pila:
        v = pila.pop()
        for w in nodos:
            if w not in S and residual(v, w)[0] > 0:
                S.add(w); pila.append(w)
    corte = [(i, j, u) for (i, j), u in cap.items() if i in S and j not in S]
    valor = iters[-1]["total"] if iters else 0
    assert sum(u for *_, u in corte) == valor
    assert all(f[(i, j)] == 0 for (i, j) in cap if j in S and i not in S)
    return {"iters": iters, "flujo": f, "valor": valor, "S": [n for n in nodos if n in S], "corte": corte}


def todos_los_cortes(nodos, arcos, s, t):
    medio = [n for n in nodos if n not in (s, t)]
    out = []
    for k in range(len(medio) + 1):
        for sub in combinations(medio, k):
            S = {s, *sub}
            out.append((sum(u for i, j, u in arcos if i in S and j not in S), [n for n in nodos if n in S]))
    return out


def nx_flujo(arcos, s, t):
    G = nx.DiGraph()
    for i, j, u in arcos:
        G.add_edge(i, j, capacity=u)
    return nx.maximum_flow_value(G, s, t)


def lp_ruta(nodos, arcos, s, t, entero=True):
    c = [w for _, _, w, *_ in arcos]
    A = [[(1 if a == n else 0) - (1 if b == n else 0) for a, b, *_ in arcos] for n in nodos]
    b = [1 if n == s else (-1 if n == t else 0) for n in nodos]
    if entero:
        r = milp(c, constraints=LinearConstraint(A, b, b), integrality=np.ones(len(c)), bounds=Bounds(0, 1))
    else:
        r = linprog(c, A_eq=A, b_eq=b, bounds=[(0, None)] * len(c), method="highs")
    return r.fun, list(r.x)


def lp_flujo(nodos, arcos, s, t):
    """max F con balance y capacidades; devuelve F y el precio sombra de cada capacidad (convención OPL)."""
    m = len(arcos)
    c = [0] * m + [-1]
    A_eq, b_eq = [], []
    for n in nodos:
        fila = [(1 if a == n else 0) - (1 if b == n else 0) for a, b, _ in arcos]
        fila.append(-1 if n == s else (1 if n == t else 0))
        A_eq.append(fila); b_eq.append(0)
    A_ub = [[1 if k == j else 0 for k in range(m)] + [0] for j in range(m)]
    b_ub = [u for *_, u in arcos]
    r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * (m + 1), method="highs")
    assert r.status == 0
    return -r.fun, [-v for v in r.ineqlin.marginals]


# ---------------------------------------------------------------- tablas
def tabla_dijkstra(D, nodos, s):
    otros = [n for n in nodos if n != s]
    filas = ["| Iteración | Se fija | " + " | ".join(otros) + " |", "|---|---|" + "---|" * len(otros)]
    for k, f in enumerate(D["filas"]):
        celdas = []
        for n in otros:
            d, p = f["et"][n]
            if n == f["fija"]:
                celdas.append(f"**[{fmt(d)}, {ab(p)}]**")
            elif n in f["perm"]:
                celdas.append("✓")
            elif d == INF:
                celdas.append("∞")
            else:
                celdas.append(f"[{fmt(d)}, {ab(p)}]")
        filas.append(f"| {k} | {f['fija']} ({fmt(f['d'])}) | " + " | ".join(celdas) + " |")
    return filas


def tabla_ff(F):
    filas = ["| Iteración | Camino aumentante | Capacidad residual de cada tramo | Cuello | Flujo acumulado |",
             "|---|---|---|---|---|"]
    for k, it in enumerate(F["iters"], 1):
        cam = it["camino"]
        tramos = []
        for (a, b), (r, sg) in zip(zip(cam, cam[1:]), it["res"]):
            tramos.append(f"{a}→{b} {r}" + (" (hacia atrás)" if sg < 0 else ""))
        filas.append(f"| {k} | {'–'.join(cam)} | {', '.join(tramos)} | {it['cuello']} | {it['total']} |")
    return filas


def tabla_arcos(F, arcos):
    filas = ["| Arco | Capacidad | Flujo | Capacidad que sobra |", "|---|---|---|---|"]
    for i, j, u in arcos:
        x = F["flujo"][(i, j)]
        filas.append(f"| {i}→{j} | {u} | {x} | {u - x} |")
    return filas


# ---------------------------------------------------------------- figuras SVG
TINTA, SUAVE, LINEA, ACENTO, PAPEL, CLARO = "#2B2F33", "#5F656B", "#B9B5AE", "#E2622A", "#F2F1EF", "#FCE3D6"


def _caja(t):
    return 7.6 * len(str(t)) + 20, 26


def _borde(c, hacia, t):
    (x, y), (hx, hy) = c, hacia
    w, h = _caja(t)
    dx, dy = hx - x, hy - y
    if dx == 0 and dy == 0:
        return x, y
    k = min((w / 2 + 3) / abs(dx) if dx else INF, (h / 2 + 3) / abs(dy) if dy else INF)
    return x + dx * k, y + dy * k


def svg_red(archivo, pos, aristas, *, dirigido=False, destacadas=(), etiqueta=None, curva=None, texto=None,
            lado_s=None, punteadas=(), nota=None, ancho=640, alto=440):
    etiqueta, curva, texto = etiqueta or {}, curva or {}, texto or {}
    dest = {tuple(e) if dirigido else frozenset(e) for e in destacadas}
    punt = {tuple(e) for e in punteadas}
    pares = {(a, b) for a, b in aristas}
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}" '
         f'font-family="Segoe UI, sans-serif" font-size="12">', f'<rect width="{ancho}" height="{alto}" fill="white"/>',
         '<defs>'
         f'<marker id="f0" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{SUAVE}"/></marker>'
         f'<marker id="f1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{ACENTO}"/></marker>'
         '</defs>']
    txt = lambda n: texto.get(n, str(n))
    textos = []
    for a, b in aristas:
        es = (tuple((a, b)) if dirigido else frozenset((a, b))) in dest
        color, grosor = (ACENTO, 3.4) if es else (LINEA, 1.6)
        guiones = ' stroke-dasharray="6 4"' if (a, b) in punt else ""
        marca = f' marker-end="url(#{"f1" if es else "f0"})"' if dirigido else ""
        pa, pb = pos[a], pos[b]
        ctrl = curva.get((a, b), curva.get((b, a)) if not dirigido else None)
        if ctrl is None and dirigido and (b, a) in pares:   # par de arcos opuestos: se separan
            mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
            dx, dy = pb[0] - pa[0], pb[1] - pa[1]; L = math.hypot(dx, dy)
            ctrl = (mx - 28 * dy / L, my + 28 * dx / L)
        if ctrl is not None:
            cx, cy = ctrl
            p0, p1 = _borde(pa, (cx, cy), txt(a)), _borde(pb, (cx, cy), txt(b))
            s.append(f'<path d="M{p0[0]:.1f},{p0[1]:.1f} Q{cx:.1f},{cy:.1f} {p1[0]:.1f},{p1[1]:.1f}" fill="none" '
                     f'stroke="{color}" stroke-width="{grosor}"{guiones}{marca}/>')
            mx, my = 0.25 * p0[0] + 0.5 * cx + 0.25 * p1[0], 0.25 * p0[1] + 0.5 * cy + 0.25 * p1[1]
        else:
            p0, p1 = _borde(pa, pb, txt(a)), _borde(pb, pa, txt(b))
            s.append(f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" '
                     f'stroke="{color}" stroke-width="{grosor}"{guiones}{marca}/>')
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        t = etiqueta.get((a, b), etiqueta.get((b, a)) if not dirigido else None)
        if t is not None:
            w = 6.8 * len(str(t)) + 8
            textos.append(f'<rect x="{mx - w / 2:.1f}" y="{my - 9:.1f}" width="{w:.1f}" height="17" rx="3" fill="white" '
                          f'stroke="{ACENTO if es else LINEA}" stroke-width="0.8"/>'
                          f'<text x="{mx:.1f}" y="{my + 4:.1f}" text-anchor="middle" fill="{ACENTO if es else TINTA}" '
                          f'font-weight="{600 if es else 400}">{t}</text>')
    s += textos
    for n, (x, y) in pos.items():
        w, h = _caja(txt(n))
        relleno = CLARO if lado_s and n in lado_s else PAPEL
        s.append(f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w:.1f}" height="{h}" rx="13" fill="{relleno}" '
                 f'stroke="{TINTA}" stroke-width="1.3"/><text x="{x}" y="{y + 4.5:.1f}" text-anchor="middle" '
                 f'fill="{TINTA}" font-weight="600">{txt(n)}</text>')
    if nota:
        s.append(f'<text x="{ancho / 2}" y="{alto - 10}" text-anchor="middle" fill="{SUAVE}" font-size="11">{nota}</text>')
    s.append("</svg>")
    FIGURAS.mkdir(parents=True, exist_ok=True)
    (FIGURAS / archivo).write_text("\n".join(s), encoding="utf-8")


POS_EJ = {"s": (70, 190), "a": (240, 80), "b": (240, 300), "c": (450, 80), "d": (450, 300), "t": (610, 190)}
POS_CASO = {"Costa": (90, 60), "Puerto": (300, 50), "Lagos": (530, 110), "Taller": (110, 220),
            "Centro": (300, 190), "Cruce": (330, 330), "Valle": (540, 270), "Cerro": (520, 400)}


def figuras(R):
    E = EJEMPLO
    arcos = [(a, b) for a, b, *_ in E["arcos"]]
    svg_red("u08_ejemplo_red.svg", POS_EJ, arcos, dirigido=True,
            destacadas=list(zip(R["ej_ruta"], R["ej_ruta"][1:])),
            etiqueta={(a, b): f"{m} m · {u}" for a, b, m, u in E["arcos"]},
            nota="Senderos de un sentido: metros · personas por minuto; en naranjo, la ruta más corta (630 m)", alto=380)
    # red residual después de las iteraciones 1 y 2
    F = R["ej_ff"]
    f2 = {(a, b): 0 for a, b, *_ in E["arcos"]}
    for it in F["iters"][:2]:
        for a, b in zip(it["camino"], it["camino"][1:]):
            f2[(a, b)] += it["cuello"]
    res_arcos, etq, atras = [], {}, []
    for a, b, _, u in E["arcos"]:
        if u - f2[(a, b)] > 0:
            res_arcos.append((a, b)); etq[(a, b)] = str(u - f2[(a, b)])
        if f2[(a, b)] > 0:
            res_arcos.append((b, a)); etq[(b, a)] = str(f2[(a, b)]); atras.append((b, a))
    it3 = F["iters"][2]["camino"]
    svg_red("u08_ejemplo_residual.svg", POS_EJ, res_arcos, dirigido=True, etiqueta=etq, punteadas=atras,
            destacadas=list(zip(it3, it3[1:])),
            nota="Red residual tras las iteraciones 1 y 2 (punteado: hacia atrás); en naranjo, el camino de la iteración 3",
            alto=380)
    svg_red("u08_ejemplo_flujo.svg", POS_EJ, arcos, dirigido=True, lado_s=set(F["S"]),
            destacadas=[(i, j) for i, j, _ in F["corte"]],
            etiqueta={(a, b): f"{F['flujo'][(a, b)]}/{u}" for a, b, _, u in E["arcos"]},
            nota="Flujo final (flujo/capacidad): 50 por minuto; nodos sombreados = lado S; en naranjo, el corte mínimo",
            alto=380)
    C = red_caso()
    D = R["caso_dijkstra"]
    arbol = [(D["pred"][n], n) for n in C["nodos"] if n != "Taller"]
    svg_red("u08_caso_dijkstra.svg", POS_CASO, [(a, b) for a, b, _ in C["aristas"]],
            destacadas=arbol, etiqueta={(a, b): str(w) for a, b, w in C["aristas"]},
            texto={n: f"{n} · {D['d'][n]}" for n in C["nodos"]}, curva={("Cerro", "Costa"): (20, 470)},
            nota="Distancia más corta desde el taller (km) junto a cada nombre; en naranjo, el árbol de rutas más cortas",
            alto=480)
    Fc = R["caso_ff"]
    svg_red("u08_caso_flujo.svg", POS_CASO, [(a, b) for a, b, _ in C["arcos"]], dirigido=True,
            lado_s=set(Fc["S"]), destacadas=[(i, j) for i, j, _ in Fc["corte"]],
            etiqueta={(a, b): f"{Fc['flujo'][(a, b)]}/{u}" for a, b, u in C["arcos"]},
            nota="Cajas por día (flujo/capacidad); en naranjo, el corte mínimo: los tres tramos que llegan a Cerro",
            alto=480)


# ---------------------------------------------------------------- resultados
def resultados():
    R = {}
    E = EJEMPLO
    D = dijkstra(E["nodos"], [(a, b, m) for a, b, m, _ in E["arcos"]], "s")
    R["ej_dijkstra"], R["ej_ruta"] = D, ruta(D["pred"], "s", "t")
    arcos_cap = [(a, b, u) for a, b, _, u in E["arcos"]]
    R["ej_ff"] = ford_fulkerson(E["nodos"], arcos_cap, "s", "t")
    R["ej_ek"] = ford_fulkerson(E["nodos"], arcos_cap, "s", "t", modo="anchura")
    cortes = todos_los_cortes(E["nodos"], arcos_cap, "s", "t")
    minimo = min(c for c, _ in cortes)
    assert R["ej_ff"]["valor"] == R["ej_ek"]["valor"] == minimo == nx_flujo(arcos_cap, "s", "t")
    assert [S for c, S in cortes if c == minimo] == [R["ej_ff"]["S"]], "el corte mínimo del ejemplo no es único"
    assert any(sg < 0 for it in R["ej_ff"]["iters"] for _, sg in it["res"])
    R["ej_cortes"] = {"n": len(cortes)}
    G = nx.DiGraph(); G.add_weighted_edges_from([(a, b, m) for a, b, m, _ in E["arcos"]])
    assert D["d"]["t"] == nx.dijkstra_path_length(G, "s", "t")
    # caso
    C = red_caso()
    Dc = dijkstra(C["nodos"], C["aristas"], "Taller", dirigido=False)
    R["caso_dijkstra"], R["caso_ruta"] = Dc, ruta(Dc["pred"], "Taller", "Cerro")
    arcos2 = C["aristas"] + [(b, a, w) for a, b, w in C["aristas"]]
    z, x = lp_ruta(C["nodos"], arcos2, "Taller", "Cerro")
    assert z == Dc["d"]["Cerro"]
    R["caso_ruta_lp"] = [(a, b) for (a, b, _), v in zip(arcos2, x) if v > 0.5]
    R["caso_ff"] = ford_fulkerson(C["nodos"], C["arcos"], "Taller", "Cerro", modo="anchura")
    R["caso_dfs"] = ford_fulkerson(C["nodos"], C["arcos"], "Taller", "Cerro")
    cortes = todos_los_cortes(C["nodos"], C["arcos"], "Taller", "Cerro")
    minimo = min(c for c, _ in cortes)
    assert [S for c, S in cortes if c == minimo] == [R["caso_ff"]["S"]], "corte mínimo del caso no único"
    assert R["caso_ff"]["valor"] == R["caso_dfs"]["valor"] == minimo == nx_flujo(C["arcos"], "Taller", "Cerro")
    R["caso_lp"] = lp_flujo(C["nodos"], C["arcos"], "Taller", "Cerro")
    R["caso_n_cortes"] = len(cortes)
    R["caso_salida_taller"] = sum(u for a, b, u in C["arcos"] if a == "Taller")
    R["caso_llegada_cerro"] = sum(u for a, b, u in C["arcos"] if b == "Cerro")
    R["caso_suma_dist"] = sum(Dc["d"].values())
    # 8.1
    D1 = dijkstra(E81["nodos"], E81["aristas"], "1", dirigido=False)
    G = nx.Graph(); G.add_weighted_edges_from(E81["aristas"])
    assert all(D1["d"][n] == nx.dijkstra_path_length(G, "1", n) for n in E81["nodos"])
    R["e81"] = {"D": D1, "rutas": {n: ruta(D1["pred"], "1", n) for n in E81["nodos"]},
                "n_rutas_4": len(list(nx.all_shortest_paths(G, "1", "4", weight="weight")))}
    # 8.2
    D2 = dijkstra(E82["nodos"], E82["arcos"], "s")
    z, x = lp_ruta(E82["nodos"], E82["arcos"], "s", "t")
    zr, xr = lp_ruta(E82["nodos"], E82["arcos"], "s", "t", entero=False)
    assert z == zr == D2["d"]["t"] and all(abs(v - round(v)) < 1e-9 for v in xr)
    R["e82"] = {"D": D2, "z": z, "ruta": ruta(D2["pred"], "s", "t")}
    # 8.3 y 8.4
    F3 = ford_fulkerson(E83["nodos"], E83["arcos"], "F", "E", modo="anchura")
    cortes = todos_los_cortes(E83["nodos"], E83["arcos"], "F", "E")
    minimo = min(c for c, _ in cortes)
    assert F3["valor"] == minimo == nx_flujo(E83["arcos"], "F", "E")
    capS = lambda S: sum(u for i, j, u in E83["arcos"] if i in S and j not in S)
    R["e83"] = F3
    R["e84"] = {"pedidos": [(S, capS(S)) for S in E83["cortes"]], "n": len(cortes), "minimo": minimo,
                "S_min": [S for c, S in cortes if c == minimo]}
    assert len(R["e84"]["S_min"]) == 1
    # 8.5
    arcos5 = E85["arcos"]
    D5 = dijkstra(E85["nodos"], arcos5, "s")
    d_bf, pred_bf, rondas = bellman_ford(E85["nodos"], arcos5, "s")
    D5s = dijkstra(E85["nodos"], [(a, b, w + E85["suma"]) for a, b, w in arcos5], "s")
    ruta_s = ruta(D5s["pred"], "s", "t")
    costo_real = sum(w for a, b, w in arcos5 for x, y in zip(ruta_s, ruta_s[1:]) if (a, b) == (x, y))
    assert D5["d"]["t"] > d_bf["t"]
    R["e85"] = {"D": D5, "bf": d_bf, "ruta_bf": ruta(pred_bf, "s", "t"), "rondas": rondas, "ruta_suma": ruta_s,
                "costo_real_suma": costo_real, "dij_ruta": ruta(D5["pred"], "s", "t")}
    # 8.6 superfuente
    arcos6 = [("S", p, u) for p, u in E86["produccion"].items()] + E86["arcos"]
    nod6 = ["S"] + E86["nodos"]
    F6 = ford_fulkerson(nod6, arcos6, "S", "C", modo="anchura")
    cortes = todos_los_cortes(nod6, arcos6, "S", "C")
    mn = min(c for c, _ in cortes)
    assert F6["valor"] == mn == nx_flujo(arcos6, "S", "C")
    R["e86"] = {"F": F6, "S_min": [S for c, S in cortes if c == mn],
                "aporte": {p: F6["flujo"][("S", p)] for p in E86["produccion"]},
                "sin_tope": nx_flujo([("S", p, 10**6) for p in E86["produccion"]] + E86["arcos"], "S", "C")}
    # 8.7 capacidad en un nodo
    n4, tope = E83["tope_nodo"]
    arcos7 = [(i if i != n4 else n4 + "s", j if j != n4 else n4 + "e", u) for i, j, u in E83["arcos"]] + [(n4 + "e", n4 + "s", tope)]
    nod7 = [m for n in E83["nodos"] for m in ((n4 + "e", n4 + "s") if n == n4 else (n,))]
    F7 = ford_fulkerson(nod7, arcos7, "F", "E", modo="anchura")
    cortes = todos_los_cortes(nod7, arcos7, "F", "E")
    mn = min(c for c, _ in cortes)
    assert F7["valor"] == mn == nx_flujo(arcos7, "F", "E")
    R["e87"] = {"F": F7, "S_min": [S for c, S in cortes if c == mn], "antes": F3["flujo"][("4", "3")] + F3["flujo"][("4", "E")]}
    # 8.8 árbol de rutas más cortas contra árbol mínimo
    D8 = dijkstra(E88["nodos"], E88["aristas"], "K", dirigido=False)
    spt = [(D8["pred"][n], n) for n in E88["nodos"] if n != "K"]
    w8 = {frozenset((a, b)): w for a, b, w in E88["aristas"]}
    km_spt = sum(w8[frozenset(e)] for e in spt)
    G = nx.Graph(); G.add_weighted_edges_from(E88["aristas"])
    T = nx.minimum_spanning_tree(G)
    km_mst = sum(d["weight"] for *_, d in T.edges(data=True))
    d_mst = nx.single_source_dijkstra_path_length(T, "K")
    assert all(len(list(nx.all_shortest_paths(G, "K", n, weight="weight"))) == 1 for n in E88["nodos"])
    R["e88"] = {"D": D8, "spt": spt, "km_spt": km_spt, "mst": sorted(tuple(sorted(e)) for e in T.edges()), "km_mst": km_mst,
                "d_mst": {n: d_mst[n] for n in E88["nodos"]}, "extra_km": km_spt - km_mst,
                "extra_millones": (km_spt - km_mst) * E88["millones_km"],
                "ahorro": {n: d_mst[n] - D8["d"][n] for n in E88["nodos"]}}
    # 8.9 dos cortes mínimos
    F9 = ford_fulkerson(E89["nodos"], E89["arcos"], "s", "t", modo="anchura")
    cortes = todos_los_cortes(E89["nodos"], E89["arcos"], "s", "t")
    mn = min(c for c, _ in cortes)
    S_min = [S for c, S in cortes if c == mn]
    assert F9["valor"] == mn and len(S_min) == 2
    k = E89["ampliacion"]
    def con(amp):
        return nx_flujo([(i, j, u + (k if (i, j) in amp else 0)) for i, j, u in E89["arcos"]], "s", "t")
    uno = {(i, j): con({(i, j)}) for i, j, _ in E89["arcos"]}
    assert all(v == mn for v in uno.values())
    dos = {(e1, e2): con({e1, e2}) for e1, e2 in combinations([(i, j) for i, j, _ in E89["arcos"]], 2)}
    mejor = max(dos.values())
    R["e89"] = {"F": F9, "S_min": S_min, "arcos_min": [[(i, j, u) for i, j, u in E89["arcos"] if i in S and j not in S] for S in S_min],
                "mejor_par": mejor, "pares_mejores": sorted([p for p, v in dos.items() if v == mejor]),
                "pares_que_suben": sorted([p for p, v in dos.items() if v > mn])}
    # 8.10 ruta con presupuesto
    arcos10 = E810["arcos"]
    c = [w for _, _, w, _ in arcos10]
    A = [[(1 if a == n else 0) - (1 if b == n else 0) for a, b, *_ in arcos10] for n in E810["nodos"]]
    bb = [1 if n == "s" else (-1 if n == "t" else 0) for n in E810["nodos"]]
    peaje = [p for *_, p in arcos10]
    ent = milp(c, constraints=[LinearConstraint(A, bb, bb), LinearConstraint([peaje], -np.inf, E810["presupuesto"])],
               integrality=np.ones(len(c)), bounds=Bounds(0, 1))
    rel = linprog(c, A_ub=[peaje], b_ub=[E810["presupuesto"]], A_eq=A, b_eq=bb, bounds=[(0, 1)] * len(c), method="highs")
    D10 = dijkstra(E810["nodos"], [(a, b, w) for a, b, w, _ in arcos10], "s")
    G = nx.DiGraph(); G.add_edges_from([(a, b) for a, b, *_ in arcos10])
    caminos = []
    for p in nx.all_simple_paths(G, "s", "t"):
        tramos = [next(x for x in arcos10 if (x[0], x[1]) == (a, b)) for a, b in zip(p, p[1:])]
        caminos.append(("–".join(p), sum(x[2] for x in tramos), sum(x[3] for x in tramos)))
    caminos.sort(key=lambda r: r[1])
    factibles = [r for r in caminos if r[2] <= E810["presupuesto"]]
    assert ent.fun == factibles[0][1] and rel.fun < ent.fun
    R["e810"] = {"caminos": caminos, "entero": ent.fun, "ruta": [(a, b) for (a, b, *_), v in zip(arcos10, ent.x) if v > 0.5],
                 "relajado": rel.fun, "x_rel": {f"{a}{b}": v for (a, b, *_), v in zip(arcos10, rel.x) if v > 1e-9},
                 "peaje_rel": float(np.dot(peaje, rel.x)), "dijkstra": D10["d"]["t"], "dij_ruta": ruta(D10["pred"], "s", "t")}
    return R


# ---------------------------------------------------------------- OPL
def escribir_dats():
    C = red_caso()
    cab = "// Unidad 8 · {}\n// Base abierta de ingeniería. Lo genera verificacion/u08_ruta_y_flujo.py.\n\n"
    nod = lambda ns: "Nodos = {" + ", ".join(f'"{n}"' for n in ns) + "};\n"
    tuplas = lambda nombre, xs: nombre + " = {\n" + ",\n".join("  <" + ", ".join(f'"{v}"' if isinstance(v, str) else str(v) for v in x) + ">" for x in xs) + "\n};\n"
    (MODELOS / "u08_ruta_mas_corta.dat").write_text(cab.format("caso: caminos de doble sentido, en km")
        + nod(C["nodos"]) + 'origen = "Taller";\ndestino = "Cerro";\n' + tuplas("Caminos", C["aristas"]), encoding="utf-8")
    (MODELOS / "u08_flujo_maximo.dat").write_text(cab.format("caso: cajas por día que admite cada tramo")
        + nod(C["nodos"]) + 'fuente = "Taller";\nsumidero = "Cerro";\n' + tuplas("Arcos", C["arcos"]), encoding="utf-8")
    (MODELOS / "u08_festival.dat").write_text(cab.format("ejemplo: senderos de un sentido, personas por minuto")
        + nod(EJEMPLO["nodos"]) + 'fuente = "s";\nsumidero = "t";\n' + tuplas("Arcos", [(a, b, u) for a, b, _, u in EJEMPLO["arcos"]]), encoding="utf-8")
    (MODELOS / "u08_e10_presupuesto.dat").write_text(cab.format("ejercicio 8.10: minutos y peaje en pesos")
        + nod(E810["nodos"]) + f'origen = "s";\ndestino = "t";\npresupuesto = {E810["presupuesto"]};\n' + tuplas("Arcos", E810["arcos"]), encoding="utf-8")


def comparar_con_opl(R):
    C = red_caso()
    sal = {}
    r = correr(MODELOS / "u08_ruta_mas_corta.mod", MODELOS / "u08_ruta_mas_corta.dat")
    if r is None:
        print("OPL: oplrun no está instalado; se comparan solo las cifras de Python")
        return None
    assert r["codigo"] == 0 and abs(r["objetivo"] - R["caso_dijkstra"]["d"]["Cerro"]) < 1e-6, r["salida"][-300:]
    usados = sorted(k for k, v in r["valores"].items() if k.startswith("x[") and v > 0.5)
    assert usados == sorted(f"x[{a},{b}]" for a, b in zip(R["caso_ruta"], R["caso_ruta"][1:])), usados
    sal["ruta"] = [l.strip() for l in r["salida"].splitlines() if l.strip().startswith(("km =", "x["))]
    for dat, nodos, arcos, F, fu, su in [("u08_flujo_maximo.dat", C["nodos"], C["arcos"], R["caso_ff"], "Taller", "Cerro"),
                                         ("u08_festival.dat", EJEMPLO["nodos"], [(a, b, u) for a, b, _, u in EJEMPLO["arcos"]], R["ej_ff"], "s", "t")]:
        r = correr(MODELOS / "u08_flujo_maximo.mod", MODELOS / dat)
        assert r["codigo"] == 0 and abs(r["objetivo"] - F["valor"]) < 1e-6
        en_corte = {(i, j) for i, j, _ in F["corte"]}
        z_lp, duales = lp_flujo(nodos, arcos, fu, su)
        for (i, j, _), dl in zip(arcos, duales):
            esperado = 1 if (i, j) in en_corte else 0
            assert abs(r["valores"][f"dual[{i},{j}]"] - esperado) < 1e-6, (dat, i, j)
            assert abs(dl - esperado) < 1e-6, (dat, i, j, "HiGHS")
        # el flujo de OPL cumple balance y capacidades (puede ser otro óptimo alternativo)
        for n in nodos:
            bal = sum(r["valores"][f"x[{i},{j}]"] for i, j, _ in arcos if i == n) - sum(r["valores"][f"x[{i},{j}]"] for i, j, _ in arcos if j == n)
            esperado = F["valor"] if n == fu else (-F["valor"] if n == su else 0)
            assert abs(bal - esperado) < 1e-6, (dat, n, bal)
        sal[dat] = [l.strip() for l in r["salida"].splitlines() if l.strip().startswith(("flujo =", "x[", "dual["))]
    r = correr(MODELOS / "u08_e10_presupuesto.mod", MODELOS / "u08_e10_presupuesto.dat")
    assert abs(r["objetivo"] - R["e810"]["entero"]) < 1e-6
    r2 = correr(MODELOS / "u08_e10_relajacion.mod", MODELOS / "u08_e10_presupuesto.dat")
    assert abs(r2["objetivo"] - R["e810"]["relajado"]) < 1e-6
    sal["e10"] = [l.strip() for l in r["salida"].splitlines() if l.strip().startswith(("minutos =", "x["))]
    sal["e10rel"] = [l.strip() for l in r2["salida"].splitlines() if l.strip().startswith(("minutos =", "x[", "peaje ="))]
    print("OPL: 5 corridas con oplrun; ruta, flujo máximo, precios sombra del corte y ruta con presupuesto coinciden con Python")
    return sal


# ---------------------------------------------------------------- cadena y revisión
def cadena(R):
    C = caso().calcular()["u8"]
    ok = all(R["caso_dijkstra"]["d"][n] == v for n, v in C["dijkstra"].items())
    ok &= R["caso_ruta"] == C["camino_a_Cerro"]
    ok &= R["caso_ff"]["valor"] == C["flujo_max_a_Cerro"] == C["corte_min_valor"]
    ok &= abs(R["caso_lp"][0] - C["flujo_max_a_Cerro"]) < 1e-6
    print("CADENA:", "OK, Dijkstra, la ruta a Cerro (23 km) y el flujo máximo (55 cajas = corte mínimo) calzan con el caso" if ok else "NO calza")
    return ok


def tablas(R):
    E, C = EJEMPLO, red_caso()
    return {
        "ej_dijkstra": tabla_dijkstra(R["ej_dijkstra"], E["nodos"], "s"),
        "ej_ff": tabla_ff(R["ej_ff"]),
        "ej_arcos": tabla_arcos(R["ej_ff"], [(a, b, u) for a, b, _, u in E["arcos"]]),
        "caso_dijkstra": tabla_dijkstra(R["caso_dijkstra"], C["nodos"], "Taller"),
        "caso_ff": tabla_ff(R["caso_ff"]),
        "caso_arcos": tabla_arcos(R["caso_ff"], C["arcos"]),
        "e81": tabla_dijkstra(R["e81"]["D"], E81["nodos"], "1"),
        "e82": tabla_dijkstra(R["e82"]["D"], E82["nodos"], "s"),
        "e83": tabla_ff(R["e83"]),
        "e83_arcos": tabla_arcos(R["e83"], E83["arcos"]),
        "e85": tabla_dijkstra(R["e85"]["D"], E85["nodos"], "s"),
        "e86": tabla_ff(R["e86"]["F"]),
        "e87": tabla_ff(R["e87"]["F"]),
        "e88": tabla_dijkstra(R["e88"]["D"], E88["nodos"], "K"),
        "e89": tabla_ff(R["e89"]["F"]),
    }


def esperados(R):
    s = []
    s += [f"{R['ej_dijkstra']['d']['t']} m", "–".join(R["ej_ruta"]), f"{R['ej_ff']['valor']} personas por minuto",
          "{" + ", ".join(R["ej_ff"]["S"]) + "}", f"{len(R['ej_ff']['iters'])} iteraciones", f"{len(R['ej_ek']['iters'])} iteraciones",
          f"{R['ej_cortes']['n']} cortes"]
    s += [f"{len(R['caso_dfs']['iters'])} iteraciones", f"{R['caso_n_cortes']} cortes", f"{R['caso_salida_taller']} cajas",
          f"{R['caso_suma_dist']} km", f"{R['caso_ff']['valor']} cajas por día"]
    e = R["e81"]
    s += [f"{n}: " + "–".join(e["rutas"][n]) + f" ({e['D']['d'][n]} min)" for n in E81["nodos"][1:]]
    s += [f"{e['n_rutas_4']} rutas más cortas"]
    s += [f"costo {R['e82']['z']:.0f}", "–".join(R["e82"]["ruta"])]
    s += [f"{R['e83']['valor']} L/s"] + tabla_arcos(R["e83"], E83["arcos"])[2:]
    s += [f"| {{{', '.join(S)}}} | {c} |" for S, c in R["e84"]["pedidos"]]
    s += [f"{R['e84']['n']} cortes"]
    e = R["e85"]
    s += [f"d(t) = {e['D']['d']['t']}", f"d(t) = {e['bf']['t']}", "–".join(e["ruta_bf"]), f"costo real {e['costo_real_suma']}"]
    e = R["e86"]
    s += [f"{e['F']['valor']} camiones por día", f"{e['sin_tope']} camiones"]
    e = R["e87"]
    s += [f"{e['F']['valor']} L/s", f"{e['antes']} L/s"]
    e = R["e88"]
    s += [f"{e['km_spt']} km", f"{e['km_mst']} km", f"{e['extra_km']} km más", f"${e['extra_millones']} millones"]
    e = R["e89"]
    s += [f"{e['F']['valor']} cajas por minuto", f"{e['mejor_par']} cajas"]
    e = R["e810"]
    s += [f"{e['entero']:.0f} minutos", f"{e['relajado']:.0f} minutos", f"{e['dijkstra']} minutos", pesos(e["peaje_rel"])]
    s += [f"| {c} | {m} | {pesos(p)} |" for c, m, p in e["caminos"]]
    return s


def codigo_en_md(md):
    faltan = []
    for f in ["u08_ruta_mas_corta.mod", "u08_flujo_maximo.mod", "u08_e10_presupuesto.mod"]:
        for linea in (MODELOS / f).read_text(encoding="utf-8").splitlines():
            if linea.strip() and linea.rstrip() not in md:
                faltan.append(f"{f}: {linea.strip()}")
    return faltan


if __name__ == "__main__":
    R = resultados()
    print("ejemplo: Dijkstra", R["ej_dijkstra"]["d"], R["ej_ruta"])
    print("ejemplo: FF", R["ej_ff"]["valor"], [(it["camino"], it["cuello"]) for it in R["ej_ff"]["iters"]], R["ej_ff"]["S"])
    print("ejemplo: EK", [(it["camino"], it["cuello"]) for it in R["ej_ek"]["iters"]])
    print("caso: Dijkstra", R["caso_dijkstra"]["d"], R["caso_ruta"], "orden", R["caso_dijkstra"]["orden"])
    print("caso: FF anchura", [(it["camino"], it["cuello"]) for it in R["caso_ff"]["iters"]], R["caso_ff"]["S"])
    print("caso: FF profundidad", len(R["caso_dfs"]["iters"]), "iteraciones")
    print("caso: LP", R["caso_lp"], "cortes", R["caso_n_cortes"], "suma dist", R["caso_suma_dist"])
    for k in ["e81", "e82", "e84", "e85", "e86", "e87", "e88", "e89", "e810"]:
        print(f"== {k}")
        for kk, vv in R[k].items():
            if kk not in ("D", "F"):
                print(f"   {kk}: {vv}")
    print("== e83", R["e83"]["valor"], R["e83"]["S"], R["e86"]["F"]["valor"], R["e86"]["F"]["S"], R["e87"]["F"]["S"], R["e89"]["F"]["S"])
    figuras(R)
    escribir_dats()
    if not cadena(R):
        sys.exit(1)
    sal = comparar_con_opl(R)
    T = tablas(R)
    if "--tablas" in sys.argv:
        for k, filas in T.items():
            print(f"\n<!-- {k} -->"); print("\n".join(filas))
        for k, ls in (sal or {}).items():
            print(f"\n<!-- salida OPL {k} -->"); print("\n".join(ls))
    if "--revisar" in sys.argv:
        md = MD.read_text(encoding="utf-8")
        md_n = md.replace("{,}", ",").replace("{.}", ".")
        md_plano = " ".join(md_n.split())
        faltan = [x for x in esperados(R) if x not in md_n and x not in md_plano]
        lineas = set(l.rstrip() for l in md.splitlines())
        faltan += [f"tabla {k}: {f}" for k, filas in T.items() for f in filas[2:] if f not in lineas]
        faltan += codigo_en_md(md)
        for k in ("ruta", "u08_flujo_maximo.dat", "e10", "e10rel"):
            faltan += [f"salida OPL {k}: {l}" for l in (sal or {}).get(k, []) if l not in lineas]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
