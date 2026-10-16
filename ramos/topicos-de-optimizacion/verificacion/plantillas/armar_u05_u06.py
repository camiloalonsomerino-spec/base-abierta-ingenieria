"""Arma el .md de las unidades 5 y 6 desde su plantilla, poniendo las tablas que genera el verificador.

    python armar_u05_u06.py 5
    python armar_u05_u06.py 6

Marcas de la plantilla: @@T:clave@@ (una tabla de tablas(R) del verificador) y @@OPL:archivo@@ (el código
de modelos/). Las unidades 5 y 6 NO se corrigen a mano: se corrige la plantilla o el verificador y se
vuelve a armar.
"""
from pathlib import Path
import importlib.util, re, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parents[1]                       # ramos/topicos-de-optimizacion
UNIDADES = {"5": ("u05_ramificacion", "u05_plantilla.md", "05-ramificacion-y-acotamiento.md"),
            "6": ("u06_planos_cortantes", "u06_plantilla.md", "06-planos-cortantes.md")}


def cargar(nombre):
    sys.path.insert(0, str(RAMO / "verificacion"))
    spec = importlib.util.spec_from_file_location(nombre, RAMO / "verificacion" / f"{nombre}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def armar(n):
    script, plantilla, destino = UNIDADES[n]
    m = cargar(script)
    R = m.resultados()
    m.dibujar(R)
    T = m.tablas(R)
    s = (AQUI / plantilla).read_text(encoding="utf-8")
    s = re.sub(r"@@T:(\w+)@@", lambda x: T[x.group(1)], s)
    s = re.sub(r"@@OPL:([\w.]+)@@", lambda x: (RAMO / "modelos" / x.group(1)).read_text(encoding="utf-8").rstrip(), s)
    assert "@@" not in s, re.findall(r"@@[^@]+@@", s)
    (RAMO / "unidades" / destino).write_text(s, encoding="utf-8")
    print("armada:", RAMO / "unidades" / destino)


if __name__ == "__main__":
    armar(sys.argv[1])
