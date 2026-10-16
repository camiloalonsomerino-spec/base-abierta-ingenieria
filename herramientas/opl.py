"""Corre un modelo OPL con oplrun y devuelve el objetivo y lo que imprime.

    from opl import correr
    r = correr("modelos/u04_mezcla.mod", "modelos/u04_mezcla.dat")
    if r is None:      # no hay CPLEX instalado: el verificador sigue con su modelo en Python
        ...
    else:
        r["objetivo"], r["salida"], r["valores"]

Los modelos de la base imprimen sus resultados en un bloque `execute` con líneas `clave = valor`;
esas líneas llegan en `valores` como números. Así el verificador compara el resultado de OPL con el
del solver libre de Python sin depender de la licencia de CPLEX.

La ruta de oplrun se toma de la variable OPLRUN o de la instalación por defecto de CPLEX Studio.
"""
from pathlib import Path
import os, re, shutil, subprocess

CANDIDATOS = [
    os.environ.get("OPLRUN"),
    shutil.which("oplrun"),
    *sorted(map(str, Path(r"C:\Program Files\IBM\ILOG").glob(r"CPLEX_Studio*\opl\bin\x64_win64\oplrun.exe")), reverse=True),
    *sorted(map(str, Path("/opt/ibm/ILOG").glob("CPLEX_Studio*/opl/bin/x86-64_linux/oplrun")), reverse=True),
    *sorted(map(str, Path("/Applications").glob("CPLEX_Studio*/opl/bin/*/oplrun")), reverse=True),
]


def oplrun():
    for c in CANDIDATOS:
        if c and Path(c).exists():
            return c
    return None


def _numero(s):
    s = s.strip()
    try:
        return float(s)
    except ValueError:
        return s


def correr(mod, dat=None, tope=120):
    """None si no hay oplrun; si lo hay, un dict con objetivo, salida y valores impresos."""
    exe = oplrun()
    if exe is None:
        return None
    args = [exe, str(mod)] + ([str(dat)] if dat else [])
    p = subprocess.run(args, capture_output=True, text=True, timeout=tope, encoding="utf-8", errors="replace")
    salida = p.stdout + p.stderr
    m = re.search(r"OBJECTIVE:\s*(-?[\d.eE+-]+)", salida)
    valores = {}
    for linea in salida.splitlines():
        mm = re.match(r"^\s*([A-Za-z_][\w\[\]., ]*?)\s*=\s*(.+?)\s*$", linea)
        if mm:
            valores[mm.group(1).strip()] = _numero(mm.group(2))
    return {"objetivo": float(m.group(1)) if m else None, "salida": salida, "valores": valores,
            "codigo": p.returncode}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print("oplrun:", oplrun() or "no instalado")
    if len(sys.argv) > 1:
        r = correr(*sys.argv[1:3])
        print(r and {k: v for k, v in r.items() if k != "salida"})
