"""Revisión mecánica del PDF de una guía (paso 7 de la skill guias-estudio).

    python revisar_pdf.py <guia.pdf> [--png N]

Dice cuántas páginas y enlaces internos tiene, y si quedó LaTeX en crudo (MathJax no cargó).
Con --png N deja la página N como PNG en la carpeta temporal, para mirarla con Read: el lector de PDF de Claude Code no renderiza en este equipo (falta pdftoppm).
Código de salida 1 si encuentra LaTeX crudo.
"""
import argparse
import os
import re
import sys
import tempfile

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("Falta PyMuPDF: pip install pymupdf")

CRUDO = re.compile(r"\\(frac|sum|int|sqrt|left|right|cdot|times|begin|end)\b|\\\(|\\\[")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--png", type=int, default=0, help="página (desde 1) a exportar como PNG")
    a = ap.parse_args()

    ruta = a.pdf
    if os.name == "nt" and len(os.path.abspath(ruta)) >= 260:
        ruta = "\\\\?\\" + os.path.abspath(ruta)  # rutas largas de OneDrive
    doc = fitz.open(ruta)

    enlaces = 0
    crudas = []
    for i, pag in enumerate(doc, 1):
        enlaces += sum(1 for l in pag.get_links() if l.get("kind") in (fitz.LINK_GOTO, fitz.LINK_NAMED))
        if CRUDO.search(pag.get_text()):
            crudas.append(i)

    kb = os.path.getsize(ruta) // 1024
    print(f"páginas: {doc.page_count} · enlaces internos: {enlaces} · {kb} KB")
    if crudas:
        print(f"LaTeX EN CRUDO en páginas {crudas}: MathJax no cargó; vuelve a renderizar.")
    else:
        print("sin LaTeX en crudo")

    if a.png:
        n = min(max(a.png, 1), doc.page_count)
        salida = os.path.join(tempfile.gettempdir(), f"revisar-guia-p{n}.png")
        doc[n - 1].get_pixmap(dpi=110).save(salida)
        print(f"PNG: {salida}")
    return 1 if crudas else 0


if __name__ == "__main__":
    sys.exit(main())
