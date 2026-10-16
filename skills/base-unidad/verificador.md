# El verificador de una unidad

Un script `ramos/<ramo>/verificacion/uNN_<tema>.py` por unidad. Su trabajo es que **ninguna cifra del
texto quede sin respaldo**.

## Qué hace

1. Declara todos los datos de la unidad (ejemplo, diez ejercicios, caso) en un solo lugar.
2. Recalcula cada resultado desde esos datos. Nada se copia del texto al script.
3. Si la unidad usa el caso integrador, lo importa y compara su pieza; imprime
   `CADENA: OK, …` o falla con código 1.
4. Con `--revisar`, formatea cada resultado como aparece en el texto y lo busca en el `.md`; imprime
   `REVISIÓN: OK, todas las cifras están en el texto` o la lista de las que faltan, con código 1.
5. Cuando hay un segundo camino (comprobar un valor futuro capitalizando su valor presente, la tabla
   de amortización contra la fórmula del saldo, un óptimo contra fuerza bruta), lo usa con `assert`.

## Plantilla

```python
"""Unidad N · <Título>. Recalcula todas las cifras; con --revisar las busca en el .md."""
from pathlib import Path
import importlib.util, sys

sys.stdout.reconfigure(encoding="utf-8")

def fmt(x, dec=1):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def pct(x, dec=1):
    return fmt(100 * x, dec) + " %"

def pesos(x):
    return "$" + fmt(x, 0)

# --- datos (originales; pasados por herramientas/colisiones.py)
EJEMPLO = {...}

def resultados():
    R = {}
    ...
    return R

def esperados(R):
    """Cadenas que el .md tiene que contener tal cual."""
    return [...]

def cadena(R):
    spec = importlib.util.spec_from_file_location("caso", Path(__file__).with_name("<caso>.py"))
    caso = importlib.util.module_from_spec(spec); spec.loader.exec_module(caso)
    C = caso.calcular()   # si el caso necesita datos (por ejemplo calcular(generar())), pásalos
    ok = abs(C["uN"]["<clave>"] - R["caso"]["<clave>"]) < 1e-6
    print("CADENA:", "OK, la pieza del caso calza" if ok else "NO calza")
    return ok

if __name__ == "__main__":
    R = resultados()
    # imprimir R ...
    if not cadena(R):
        sys.exit(1)
    if "--revisar" in sys.argv:
        md = (Path(__file__).parents[1] / "unidades" / "NN-<tema>.md").read_text(encoding="utf-8")
        md = md.replace("{,}", ",").replace("{.}", ".")
        faltan = [x for x in esperados(R) if x not in md]
        print("REVISIÓN:", "OK, todas las cifras están en el texto" if not faltan else f"faltan {len(faltan)}: {faltan}")
        sys.exit(1 if faltan else 0)
```

## Tablas generadas

Cuando una tabla es larga (registro MRP, tabla de amortización, eventos de una simulación, retornos
mensuales), el script la genera en Markdown y la revisión exige que esté **completa** en el texto, fila
por fila. Así la tabla del PDF nunca difiere de la calculada.

## Datos aleatorios

Si un ejercicio usa datos simulados, el script fija la semilla, imprime los datos y el `.md` los
muestra tal cual. Nadie tiene que creerle a un número que no puede ver.
