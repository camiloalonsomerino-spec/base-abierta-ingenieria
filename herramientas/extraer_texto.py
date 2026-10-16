"""Extrae el texto de PDF, DOCX y XLSX/XLS de una carpeta a un .txt por archivo (para la ingeniería inversa, en privado).

    python extraer_texto.py <carpeta del material> <carpeta de salida> [--excluir REGEX] [--max-mb 30]

El nombre de salida es la ruta relativa con «__» en vez de separadores. En Windows lee con el prefijo
\\\\?\\ para que las rutas de más de 260 caracteres no fallen.
"""
import argparse, os, re, sys, pathlib

sys.stdout.reconfigure(encoding="utf-8")


def largo(p):
    """Ruta absoluta con prefijo de ruta larga en Windows."""
    s = str(pathlib.Path(p).resolve())
    return pathlib.Path("\\\\?\\" + s) if os.name == "nt" and not s.startswith("\\\\?\\") else pathlib.Path(s)


def texto_de(f, ext):
    txt = []
    if ext == ".pdf":
        import fitz
        with fitz.open(f) as d:
            for i, p in enumerate(d, 1):
                txt.append(f"--- pág {i} ---\n" + p.get_text())
    elif ext == ".docx":
        import docx
        d = docx.Document(f)
        txt += [p.text for p in d.paragraphs if p.text.strip()]
        for t in d.tables:
            for r in t.rows:
                txt.append(" | ".join(c.text.strip() for c in r.cells))
    elif ext == ".xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(f, data_only=True)
        for ws in wb.worksheets:
            txt.append(f"=== hoja {ws.title} ===")
            for row in ws.iter_rows(values_only=True):
                vals = [str(v) for v in row if v is not None]
                if vals:
                    txt.append(" | ".join(vals))
    elif ext == ".xls":
        import xlrd
        wb = xlrd.open_workbook(f)
        for ws in wb.sheets():
            txt.append(f"=== hoja {ws.name} ===")
            for r in range(ws.nrows):
                vals = [str(v) for v in ws.row_values(r) if str(v).strip()]
                if vals:
                    txt.append(" | ".join(vals))
    elif ext == ".pptx":
        from pptx import Presentation
        for i, s in enumerate(Presentation(f).slides, 1):
            txt.append(f"--- lámina {i} ---")
            for sh in s.shapes:
                if sh.has_text_frame and sh.text_frame.text.strip():
                    txt.append(sh.text_frame.text)
    elif ext == ".ipynb":
        import json
        nb = json.loads(pathlib.Path(f).read_text(encoding="utf-8", errors="ignore"))
        for c in nb.get("cells", []):
            txt.append(f"=== celda {c.get('cell_type')} ===")
            txt.append("".join(c.get("source", [])))
    elif ext in (".csv", ".txt"):
        lineas = pathlib.Path(f).read_text(encoding="utf-8", errors="ignore").splitlines()
        txt += lineas[:200] + ([f"... ({len(lineas)} líneas en total)"] if len(lineas) > 200 else [])
    return "\n".join(txt)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--excluir", default=None, help="regex sobre la ruta relativa")
    ap.add_argument("--max-mb", type=float, default=30)
    a = ap.parse_args()
    src, out = largo(a.src), largo(a.out)
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for raiz, _, archivos in os.walk(src):
        for nombre in sorted(archivos):
            f = pathlib.Path(raiz) / nombre
            ext = f.suffix.lower()
            if ext not in (".pdf", ".docx", ".xlsx", ".xls", ".pptx", ".ipynb", ".csv"):
                continue
            rel = os.path.relpath(f, src).replace("\\", "/")
            if a.excluir and re.search(a.excluir, rel):
                continue
            if f.stat().st_size > a.max_mb * 1_048_576:
                continue
            try:
                t = texto_de(f, ext)
            except Exception as e:
                t = f"(error: {e})"
            destino = rel.replace("/", "__")
            if len(destino) > 140:
                destino = destino[:130] + "_" + str(sum(map(ord, rel)) % 10**6)
            (out / (destino + ".txt")).write_text(t, encoding="utf-8")
            n += 1
    print(f"{n} archivos extraídos en {out}")
