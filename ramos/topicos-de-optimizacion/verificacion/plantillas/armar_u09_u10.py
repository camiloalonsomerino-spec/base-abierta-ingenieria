"""Arma el .md de las unidades 9 y 10 desde su plantilla, poniendo las tablas que genera el verificador.

    python armar_u09_u10.py 9
    python armar_u09_u10.py 10

Marcas de la plantilla: @@T:clave@@ (una tabla de tablas(R) del verificador), @@OPL:archivo@@ (el código
de modelos/) y @@SALIDA@@ (lo que imprime OPL al correr el caso). Las unidades 9 y 10 NO se corrigen a
mano: se corrige la plantilla o el verificador y se vuelve a armar.
"""
from pathlib import Path
import importlib.util, re, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAMO = AQUI.parents[1]                       # ramos/topicos-de-optimizacion
UNIDADES = {"9": ("u09_transporte", "u09_plantilla.md", "09-transporte.md"),
            "10": ("u10_asignacion", "u10_plantilla.md", "10-asignacion.md")}


def cargar(nombre):
    spec = importlib.util.spec_from_file_location(nombre, RAMO / "verificacion" / f"{nombre}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def armar(n):
    script, plantilla, destino = UNIDADES[n]
    m = cargar(script)
    R = m.resultados()
    m.figura(R)
    m.comparar_con_opl(R)
    T = m.tablas(R)
    s = (AQUI / plantilla).read_text(encoding="utf-8")
    s = re.sub(r"@@T:(\w+)@@", lambda x: T[x.group(1)], s)
    s = re.sub(r"@@OPL:([\w.]+)@@", lambda x: (RAMO / "modelos" / x.group(1)).read_text(encoding="utf-8").rstrip(), s)
    s = s.replace("@@SALIDA@@", "\n".join(m.SALIDA_CASO))
    assert "@@" not in s, re.findall(r"@@[^@]+@@", s)
    (RAMO / "unidades" / destino).write_text(s, encoding="utf-8")
    print("armada:", RAMO / "unidades" / destino)


if __name__ == "__main__":
    armar(sys.argv[1])
