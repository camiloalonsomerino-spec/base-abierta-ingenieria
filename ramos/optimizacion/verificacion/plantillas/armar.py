"""Arma el .md de una unidad desde su plantilla, poniendo las tablas que genera el verificador.

    python armar.py 9 "[08-metodo-simplex]"     # unidad 9; el segundo argumento es la línea requiere
    python armar.py 10 "[09-simplex-casos-especiales]"

Las unidades 9 y 10 NO se corrigen a mano: se corrige la plantilla o el verificador y se vuelve a armar.
"""
from pathlib import Path
import importlib.util, re, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parents[2]   # ramos/optimizacion
AQUI = Path(__file__).resolve().parent


def cargar(nombre):
    spec = importlib.util.spec_from_file_location(nombre, BASE / "verificacion" / f"{nombre}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def todas(m, res):
    trozos, fase = [], None
    for k, t in enumerate(res["tablas"]):
        et = t["etiqueta"]
        rot = f"**Tabla {k}" + (f" · {et.lower()}" if et and et != "Gran M" else "") + ".**"
        trozos += [rot, m.tabla_md(t), m.paso_md(t)]
    return "\n\n".join(trozos)


def opl(nombre):
    return (BASE / "modelos" / nombre).read_text(encoding="utf-8").rstrip()


def u09(req):
    m = cargar("u09_dos_fases")
    R = m.resultados()
    m.figura(R)
    s = (AQUI / "u09_plantilla.md").read_text(encoding="utf-8")
    s = s.replace("@@REQ@@", req)
    s = re.sub(r"@@OPL:([\w.]+)@@", lambda x: opl(x.group(1)), s)
    s = re.sub(r"@@ALL:(\w+)@@", lambda x: todas(m, R[x.group(1)]), s)
    s = re.sub(r"@@E8:(\w)@@", lambda x: m.tabla_md(R["e8_tablas"][x.group(1)]), s)
    s = re.sub(r"@@E9:(\d+)@@", lambda x: m.tabla_md(R["e9"][int(x.group(1))]["tablas"][-1]), s)
    s = s.replace("@@OTRA@@", m.tabla_md(R["e2_otra"]))
    assert "@@" not in s, re.findall(r"@@[^@]+@@", s)
    (BASE / "unidades" / "09-simplex-casos-especiales.md").write_text(s, encoding="utf-8")


def u10(req):
    m = cargar("u10_dualidad")
    R = m.resultados()
    s = (AQUI / "u10_plantilla.md").read_text(encoding="utf-8")
    s = s.replace("@@REQ@@", req)
    s = re.sub(r"@@OPL:([\w.]+)@@", lambda x: opl(x.group(1)), s)
    s = re.sub(r"@@ALL:(\w+)@@", lambda x: todas(m.u09, R[x.group(1)]), s)
    s = re.sub(r"@@FIN:(\w+)@@", lambda x: m.tabla_md(R[x.group(1)]["tablas"][-1]), s)
    assert "@@" not in s, re.findall(r"@@[^@]+@@", s)
    (BASE / "unidades" / "10-dualidad.md").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1] == "9":
        u09(sys.argv[2])
    else:
        u10(sys.argv[2])
