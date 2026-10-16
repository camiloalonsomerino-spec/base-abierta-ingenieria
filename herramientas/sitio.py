"""Arma el sitio web estático de la base en `docs/` (GitHub Pages lo publica desde ahí).

    python herramientas/sitio.py

Usa el mismo motor de Markdown, fórmulas y montos en pesos que `md_a_pdf.py`, así la página y el PDF
dicen lo mismo. Las unidades y los README pasan a HTML; las figuras se copian; los PDF, scripts y datos se
enlazan al repositorio en GitHub para no duplicarlos.
"""
from pathlib import Path
import base64, html, re, shutil, sys

import markdown

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_a_pdf import frontmatter, proteger_math, devolver_math, MATHJAX  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "docs"
REPO = "https://github.com/camiloalonsomerino-spec/base-abierta-ingenieria"
LOGO = base64.b64encode((RAIZ / "herramientas" / "marca" / "cm-imagotipo.svg").read_bytes()).decode()

CSS = """
:root { --tinta:#2B2F33; --suave:#5F656B; --linea:#D6D3CE; --papel:#F2F1EF; --acento:#E2622A; --fondo:#FFFFFF; --enlace:#1F5F99; }
@media (prefers-color-scheme: dark) {
  :root { --tinta:#E6E4E1; --suave:#A9ADB1; --linea:#3A3F44; --papel:#24282C; --fondo:#181B1E; --enlace:#7FB3E6; }
  header.cm img { filter: invert(1) hue-rotate(180deg); }
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin:0; background:var(--fondo); color:var(--tinta);
       font:16px/1.6 "Segoe UI", system-ui, -apple-system, Roboto, sans-serif; }
main, header.cm, nav.migas, footer.cm { max-width: 860px; margin: 0 auto; padding: 0 16px; }
header.cm { display:flex; justify-content:space-between; align-items:flex-end; gap:12px; padding-top:18px;
            padding-bottom:10px; border-bottom:2.5px solid var(--acento); }
header.cm img { height:40px; }
header.cm .ramo { font-size:12px; color:var(--suave); text-align:right; letter-spacing:.04em; text-transform:uppercase; }
nav.migas { font-size:14px; margin-top:10px; color:var(--suave); }
a { color:var(--enlace); }
h1, h2, h3 { font-family: Cambria, Georgia, "Times New Roman", serif; line-height:1.25; }
h1 { font-size:30px; margin:18px 0 10px; }
h2 { font-size:22px; margin:30px 0 10px; padding-top:8px; border-top:1px solid var(--linea); }
h3 { font-size:18px; margin:22px 0 8px; }
hr { border:0; border-top:1px solid var(--linea); }
.tabla { overflow-x:auto; }
table { border-collapse:collapse; width:100%; margin:10px 0 14px; font-size:14.5px; font-variant-numeric:tabular-nums; }
th, td { border-bottom:1px solid var(--linea); padding:6px 9px; text-align:left; vertical-align:top; }
th { background:var(--papel); font-weight:600; }
blockquote { margin:12px 0; padding:10px 14px; background:var(--papel); border-left:3px solid var(--acento); }
blockquote p { margin:0; }
pre { background:var(--papel); border:1px solid var(--linea); padding:10px 12px; font-size:13.5px; line-height:1.45; overflow-x:auto; }
pre code { background:none; padding:0; }
code { font-family:"Cascadia Mono", Consolas, monospace; font-size:.9em; background:var(--papel); padding:0 3px; }
img { max-width:100%; height:auto; display:block; margin:10px auto; background:#fff; }
mjx-container[display="true"] { overflow-x:auto; overflow-y:hidden; }
.descargas { display:flex; flex-wrap:wrap; gap:8px 16px; margin:8px 0 4px; font-size:15px; }
footer.cm { margin-top:40px; padding-top:10px; padding-bottom:30px; border-top:1px solid var(--linea); font-size:13px; color:var(--suave); }
"""


def blob(ruta: Path):
    """URL de GitHub para ver un archivo del repositorio."""
    return f"{REPO}/blob/main/{ruta.relative_to(RAIZ).as_posix()}"


def destino_html(ruta: Path):
    """Dónde queda en docs/ la página de un .md del repositorio (None si no se publica como página)."""
    rel = ruta.relative_to(RAIZ)
    if rel.as_posix() == "README.md":
        return DOCS / "index.html"
    if len(rel.parts) == 3 and rel.parts[0] == "ramos" and rel.parts[2] == "README.md":
        return DOCS / rel.parts[1] / "index.html"
    if len(rel.parts) == 4 and rel.parts[0] == "ramos" and rel.parts[2] == "unidades":
        return DOCS / rel.parts[1] / (ruta.stem + ".html")
    return None


def reescribir_enlaces(html_txt, origen: Path, destino: Path):
    """Los enlaces relativos del .md apuntan a otra página del sitio, a una figura copiada o a GitHub."""
    def cambiar(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"^(https?:|mailto:|#|data:)", url):
            return m.group(0)
        camino, _, ancla = url.partition("#")
        real = (origen.parent / camino).resolve()
        pagina = destino_html(real) if real.suffix == ".md" else None
        if pagina:
            nuevo = Path(_relativa(pagina, destino.parent)).as_posix()
        elif real.suffix == ".pdf":
            nuevo = f"{REPO}/raw/main/{real.relative_to(RAIZ).as_posix()}"
        elif "figuras" in real.parts and real.parent.name == "figuras":
            nuevo = Path(_relativa(destino.parent / "figuras" / real.name, destino.parent)).as_posix()
        else:
            nuevo = blob(real) if real.exists() else url
        return f'{attr}="{nuevo}{"#" + ancla if ancla else ""}"'
    return re.sub(r'(href|src)="([^"]+)"', cambiar, html_txt)


def _relativa(a: Path, desde: Path):
    import os
    return os.path.relpath(a, desde)


def pagina(md: Path, migas: list, extra=""):
    datos, cuerpo = frontmatter(md.read_text(encoding="utf-8"))
    cuerpo, guardadas = proteger_math(cuerpo)
    contenido = markdown.markdown(cuerpo, extensions=["tables", "fenced_code", "sane_lists"])
    contenido = devolver_math(contenido, guardadas)
    contenido = contenido.replace("<table>", '<div class="tabla"><table>').replace("</table>", "</table></div>")
    destino = destino_html(md)
    contenido = reescribir_enlaces(contenido, md, destino)
    if extra:
        contenido = re.sub(r"(</h1>)", r"\1" + extra, contenido, count=1)
    titulo = re.search(r"<h1>(.*?)</h1>", contenido)
    titulo = re.sub("<[^>]+>", "", titulo.group(1)) if titulo else "Base abierta de ingeniería"
    ramo = html.escape(datos.get("ramo", ""))
    nav = " · ".join(f'<a href="{u}">{html.escape(t)}</a>' if u else html.escape(t) for t, u in migas)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titulo)} · Base abierta de ingeniería</title>
<meta name="description" content="Ramos de Ingeniería Civil Industrial reescritos de cero, con ejercicios con pauta y cifras verificadas.">
<script>MathJax = {{ svg: {{ fontCache: 'global' }}, options: {{ enableMenu: false }} }};</script>
<script defer src="{MATHJAX}"></script>
<style>{CSS}</style></head><body>
<header class="cm"><a href="{_relativa(DOCS / 'index.html', destino.parent).replace(chr(92), '/')}"><img src="data:image/svg+xml;base64,{LOGO}" alt="Camilo Merino"></a>
<div class="ramo">Base abierta de ingeniería<br>{ramo}</div></header>
<nav class="migas">{nav}</nav>
<main>{contenido}</main>
<footer class="cm">Base abierta de ingeniería · Camilo Merino · textos en
<a href="https://creativecommons.org/licenses/by/4.0/deed.es">CC BY 4.0</a>, código en MIT ·
<a href="{REPO}">repositorio en GitHub</a>{f" · <a href='{blob(md)}'>ver el Markdown</a>" if md.name != "README.md" else ""}</footer>
</body></html>
""", encoding="utf-8")
    return destino


def construir():
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    n = 0
    pagina(RAIZ / "README.md", [("Inicio", None)])
    for ramo in sorted((RAIZ / "ramos").iterdir()):
        if not (ramo / "README.md").exists():
            continue
        nombre = (ramo / "README.md").read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
        extra = (f'<div class="descargas"><a href="{blob(ramo / "tutor" / "contexto.md")}">Contexto para el tutor de IA</a>'
                 f'<a href="{REPO}/tree/main/ramos/{ramo.name}">Archivos del ramo en GitHub</a></div>')
        pagina(ramo / "README.md", [("Inicio", "../index.html"), (nombre, None)], extra)
        figs = ramo / "unidades" / "figuras"
        if figs.exists():
            shutil.copytree(figs, DOCS / ramo.name / "figuras")
        for md in sorted((ramo / "unidades").glob("*.md")):
            pdf = ramo / "pdf" / (md.stem + ".pdf")
            extra = (f'<div class="descargas"><a href="{REPO}/raw/main/{pdf.relative_to(RAIZ).as_posix()}">Descargar PDF</a>'
                     f'<a href="{REPO}/tree/main/ramos/{ramo.name}/verificacion">Verificadores</a></div>') if pdf.exists() else ""
            pagina(md, [("Inicio", "../index.html"), (nombre, "index.html"), (md.stem[:2].lstrip("0"), None)], extra)
            n += 1
    return n


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    n = construir()
    total = sum(f.stat().st_size for f in DOCS.rglob("*") if f.is_file())
    print(f"sitio: {n} unidades en {DOCS} ({total / 1e6:.1f} MB)")
