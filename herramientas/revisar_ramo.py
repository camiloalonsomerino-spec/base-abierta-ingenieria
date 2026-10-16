"""Corre el verificador de cada unidad de un ramo con --revisar y resume.

    python herramientas/revisar_ramo.py ramos/gestion-de-operaciones

Termina con código 1 si alguna unidad no cuadra, así sirve de candado antes de publicar.
"""
from pathlib import Path
import subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")

ramo = Path(sys.argv[1]).resolve()
scripts = sorted((ramo / "verificacion").glob("u[0-9][0-9]_*.py"))
unidades = sorted((ramo / "unidades").glob("[0-9][0-9]-*.md"))
fallas = []
for s in scripts:
    r = subprocess.run([sys.executable, "-P", str(s), "--revisar"], capture_output=True, text=True,
                       encoding="utf-8", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    ultima = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:] or ["(sin salida)"]
    estado = "OK " if r.returncode == 0 else "FALLA"
    if r.returncode:
        fallas.append(s.name)
    print(f"{estado}  {s.name:38} {ultima[0][:90]}")
sin_script = [u.name for u in unidades if not any(s.name.startswith("u" + u.name[:2]) for s in scripts)]
if sin_script:
    print("\nUnidades sin verificador:", ", ".join(sin_script))
print(f"\n{len(scripts)} verificadores · {len(fallas)} con falla")
sys.exit(1 if fallas or sin_script else 0)
