"""Convierte una unidad en Markdown a un PDF con la marca CM.

    python herramientas/md_a_pdf.py ramos/gestion-de-operaciones/unidades/10-programacion-de-operaciones.md

Deja el PDF en la carpeta `pdf/` del ramo, con el mismo nombre. Necesita Python 3.9 o más, el paquete
`markdown` (pip install markdown) y Chrome, Edge o Chromium instalado. Las fórmulas van en LaTeX entre
$...$ o $$...$$ y las dibuja MathJax antes de imprimir.
"""
from pathlib import Path
import argparse, base64, html, os, re, shutil, subprocess, sys, tempfile, time

import markdown

AQUI = Path(__file__).resolve().parent
MATHJAX = "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js"

CSS = """
@page { size: A4; margin: 18mm 17mm 18mm 17mm; }
:root { --tinta:#2B2F33; --suave:#5F656B; --linea:#D6D3CE; --papel:#F2F1EF; --acento:#E2622A; }
* { box-sizing: border-box; }
body { margin:0; color:var(--tinta); font:10.5pt/1.55 "Segoe UI", system-ui, -apple-system, Roboto, sans-serif;
       -webkit-print-color-adjust:exact; print-color-adjust:exact; }
header.cm { display:flex; justify-content:space-between; align-items:flex-end; gap:12px;
            border-bottom:2.5px solid var(--acento); padding-bottom:8px; margin-bottom:18px; }
header.cm img { height:38px; }
header.cm .ramo { font-size:8.5pt; color:var(--suave); text-align:right; letter-spacing:.04em; text-transform:uppercase; }
h1, h2, h3 { font-family: Cambria, Georgia, "Times New Roman", serif; color:var(--tinta); line-height:1.2; break-after:avoid; }
h1 { font-size:21pt; margin:0 0 10px; }
h2 { font-size:14.5pt; margin:22px 0 8px; padding-top:6px; border-top:1px solid var(--linea); }
h3 { font-size:12pt; margin:16px 0 6px; }
p, li { orphans:3; widows:3; }
hr { display:none; }
table { border-collapse:collapse; width:100%; margin:8px 0 12px; font-size:9.3pt; font-variant-numeric:tabular-nums; break-inside:avoid; }
th, td { border-bottom:1px solid var(--linea); padding:4px 7px; text-align:left; vertical-align:top; }
th { background:var(--papel); font-weight:600; }
blockquote { margin:10px 0; padding:8px 12px; background:var(--papel); border-left:3px solid var(--acento); break-inside:avoid; }
blockquote p { margin:0; }
pre { background:var(--papel); border:1px solid var(--linea); padding:8px 10px; font-size:8.6pt; line-height:1.4; white-space:pre-wrap; break-inside:avoid; }
pre code { background:none; padding:0; }
img { max-width:100%; display:block; margin:8px auto; break-inside:avoid; }
code { font-family:"Cascadia Mono", Consolas, monospace; font-size:9pt; background:var(--papel); padding:0 3px; }
mjx-container[display="true"] { margin:8px 0 !important; }
footer.cm { margin-top:26px; padding-top:8px; border-top:1px solid var(--linea); font-size:8pt; color:var(--suave); }
"""


def frontmatter(texto):
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return {}, texto
    datos = {}
    for linea in m.group(1).splitlines():
        if ":" in linea:
            k, v = linea.split(":", 1)
            datos[k.strip()] = v.strip()
    return datos, texto[m.end():]


def proteger_math(texto):
    """Saca las fórmulas antes de Markdown (que se come _ y \\) y las devuelve después."""
    guardadas = []

    def guardar(m, display):
        guardadas.append((m.group(1), display))
        return f"@@MATH{len(guardadas) - 1}@@"

    # Montos en pesos con punto de miles ($36.000) y \$ escrito a mano no son fórmulas.
    texto = re.sub(r"\\\$|\$(?=\d{1,3}(?:\.\d{3})+(?:,\d+)?(?!\d))", "&#36;", texto)
    texto = re.sub(r"\$\$(.+?)\$\$", lambda m: guardar(m, True), texto, flags=re.S)
    texto = re.sub(r"(?<![\\$])\$(?!\s)(.+?)(?<!\s)\$", lambda m: guardar(m, False), texto)
    return texto, guardadas


def devolver_math(html_txt, guardadas):
    def poner(m):
        tex, display = guardadas[int(m.group(1))]
        tex = html.escape(tex, quote=False)
        return f"\\[{tex}\\]" if display else f"\\({tex}\\)"
    return re.sub(r"@@MATH(\d+)@@", poner, html_txt)


def armar_html(md_path):
    datos, cuerpo = frontmatter(md_path.read_text(encoding="utf-8"))
    cuerpo, guardadas = proteger_math(cuerpo)
    contenido = markdown.markdown(cuerpo, extensions=["tables", "fenced_code", "sane_lists"])
    contenido = devolver_math(contenido, guardadas)
    logo = base64.b64encode((AQUI / "marca" / "cm-imagotipo.svg").read_bytes()).decode()
    ramo = html.escape(datos.get("ramo", ""))
    version = html.escape(datos.get("version", ""))
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<base href="{md_path.resolve().parent.as_uri()}/">
<title>{ramo} · unidad {html.escape(datos.get('unidad', ''))}</title>
<script>MathJax = {{ svg: {{ fontCache: 'global' }}, options: {{ enableMenu: false }} }};</script>
<script src="{MATHJAX}"></script>
<style>{CSS}</style></head><body>
<header class="cm"><img src="data:image/svg+xml;base64,{logo}" alt="Camilo Merino">
<div class="ramo">Base abierta de ingeniería<br>{ramo}</div></header>
{contenido}
<footer class="cm">Base abierta de ingeniería · Camilo Merino · {ramo} · versión {version}.
Ejercicios y datos originales; las cifras se verifican con el script de la unidad.</footer>
</body></html>"""


def navegador():
    candidatos = [
        os.environ.get("CHROME"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser"),
    ]
    for c in candidatos:
        if c and Path(c).exists():
            return c
    sys.exit("No encontré Chrome, Edge ni Chromium. Define la variable CHROME con la ruta.")


def imprimir(html_path, pdf_path, tope=40):
    # Un perfil por proceso: dos renders en paralelo con el mismo perfil se bloquean.
    perfil = Path(tempfile.gettempdir()) / f"base-abierta-render-{os.getpid()}"
    tmp = Path(tempfile.gettempdir()) / f"base-abierta-{os.getpid()}.pdf"
    tmp.unlink(missing_ok=True)
    subprocess.Popen([navegador(), "--headless=new", "--disable-gpu", f"--user-data-dir={perfil}",
                      "--no-pdf-header-footer", "--virtual-time-budget=25000",
                      f"--print-to-pdf={tmp}", html_path.as_uri()],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    limite, previo, iguales = time.time() + tope, -1, 0
    while time.time() < limite:
        if tmp.exists():
            largo = tmp.stat().st_size
            iguales = iguales + 1 if largo > 0 and largo == previo else 0
            previo = largo
            if iguales >= 2:
                pdf_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(tmp), pdf_path)
                shutil.rmtree(perfil, ignore_errors=True)
                return
        time.sleep(0.5)
    sys.exit("El PDF no se generó a tiempo; el anterior quedó intacto.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("md", type=Path)
    ap.add_argument("--pdf", type=Path, help="destino (por defecto, la carpeta pdf/ del ramo)")
    a = ap.parse_args()
    md = a.md.resolve()
    pdf = a.pdf or md.parents[1] / "pdf" / (md.stem + ".pdf")
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(armar_html(md))
        html_tmp = Path(f.name)
    imprimir(html_tmp, pdf.resolve())
    html_tmp.unlink(missing_ok=True)
    print(f"PDF: {pdf}")
