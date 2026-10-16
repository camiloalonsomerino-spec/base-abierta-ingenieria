"""Busca si los datos de un ejercicio aparecen en el material privado del curso.

    python herramientas/colisiones.py <carpeta-texto-del-material> 3.400.000 0,8 36 ...
    python herramientas/colisiones.py <carpeta> --archivo datos.txt   (un número por línea)

Un número que aparece en el material no está prohibido (12 meses o 1.000 son de todos), pero una
combinación de varios que aparecen juntos en un mismo archivo delata un ejercicio copiado. Por eso
el informe agrupa por archivo y avisa cuando un archivo contiene tres o más de los datos.
"""
from pathlib import Path
import os, re, sys

sys.stdout.reconfigure(encoding="utf-8")


def normal(n):
    """3.400.000 · 3400000 · 3,4 · 3.4 → misma forma comparable."""
    n = n.strip()
    if re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", n):
        n = n.replace(".", "").replace(",", ".")
    else:
        n = n.replace(",", ".")
    try:
        x = float(n)
    except ValueError:
        return None
    return f"{x:.6g}"


def numeros_de(texto):
    return {normal(m) for m in re.findall(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?", texto)} - {None}


if __name__ == "__main__":
    carpeta = Path(sys.argv[1]).resolve()
    if os.name == "nt":  # rutas de más de 260 caracteres
        carpeta = Path("\\\\?\\" + str(carpeta))
    args = sys.argv[2:]
    if args[:1] == ["--archivo"]:
        args = Path(args[1]).read_text(encoding="utf-8").split()
    # Un entero chico (menos de 100) aparece en cualquier fecha o porcentaje: no distingue nada.
    distintivo = lambda a: normal(a) and not (float(normal(a)).is_integer() and float(normal(a)) < 100)
    buscados = {normal(a): a for a in args if distintivo(a)}
    por_archivo, umbral = {}, {}
    for f in sorted(carpeta.glob("*.txt")):
        # Las tablas de distribuciones (z, t, F, chi², Tukey, KS) traen casi todos los decimales.
        if re.search(r"(?i)tabla|table|critical.values", f.name):
            continue
        todos = numeros_de(f.read_text(encoding="utf-8", errors="ignore"))
        presentes = todos & set(buscados)
        if presentes:
            por_archivo[f.name] = sorted(buscados[p] for p in presentes)
            # Un archivo con muchos números distintos (una matriz de datos, un capítulo de libro)
            # coincide por azar: ahí se exigen cinco coincidencias en vez de tres.
            umbral[f.name] = 5 if len(todos) > 100 else 3
    alertas = {f: v for f, v in por_archivo.items() if len(v) >= umbral[f]}
    for f, v in sorted(alertas.items(), key=lambda kv: -len(kv[1])):
        print(f"ALERTA {len(v)} datos juntos en {f}: {', '.join(v)}")
    sueltos = sorted({x for v in por_archivo.values() for x in v})
    print(f"\n{len(buscados)} datos revisados · {len(sueltos)} aparecen en algún archivo · {len(alertas)} archivos con 3 o más")
    sys.exit(1 if alertas else 0)
