"""Arma los .md de las unidades 11 y 12 desde su plantilla, con las tablas que genera cada verificador.

    python armar_u11_u12.py 11
    python armar_u11_u12.py 12

Marcas de la plantilla: @@T:clave@@ pone la tabla `clave` de tablas(R) del verificador;
@@OPL:archivo@@ pone el archivo de modelos/ tal cual. Las unidades 11 y 12 NO se corrigen a mano:
se corrige la plantilla o el verificador y se vuelve a armar.
"""
from pathlib import Path
import importlib.util, re, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
BASE = AQUI.parents[1]   # ramos/topicos-de-optimizacion

UNIDADES = {"11": ("u11_heuristicas", "u11_plantilla.md", "11-heuristicas.md"),
            "12": ("u12_metaheuristicas", "u12_plantilla.md", "12-metaheuristicas.md")}


def cargar(nombre):
    spec = importlib.util.spec_from_file_location(nombre, BASE / "verificacion" / f"{nombre}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def armar(n):
    mod, plantilla, salida = UNIDADES[n]
    m = cargar(mod)
    R = m.resultados()
    m.dibujar(R)
    T = m.tablas(R)
    s = (AQUI / plantilla).read_text(encoding="utf-8")
    s = re.sub(r"@@T:(\w+)@@", lambda x: T[x.group(1)].strip(), s)
    s = re.sub(r"@@OPL:([\w.]+)@@", lambda x: (BASE / "modelos" / x.group(1)).read_text(encoding="utf-8").rstrip(), s)
    assert "@@" not in s, re.findall(r"@@[^@]+@@", s)
    (BASE / "unidades" / salida).write_text(s, encoding="utf-8")
    print("armada:", salida)


if __name__ == "__main__":
    for n in sys.argv[1:] or ["11", "12"]:
        armar(n)
