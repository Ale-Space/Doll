"""Anteprima di una dispensa PDF: tutte le pagine in un'unica immagine a griglia.

Uso: .venv/bin/python pdf_anteprima.py <dispensa.pdf> [--pagine]
Scrive <nome>_pagine.png accanto al PDF (griglia, 2 colonne fino a 4 pagine, poi 3)
e lo stampa. Con --pagine scrive anche pagine/pagina_N.png a 150 dpi, leggibili
nel dettaglio con Read (formule, margini, schemi).
"""
import sys
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pdf = Path(sys.argv[1]).resolve()
    singole = "--pagine" in sys.argv
    larg = 820  # larghezza di ogni pagina nella griglia (px)
    pagine = []
    if singole:  # via le pagine di una compilazione precedente
        for vecchia in (pdf.parent / "pagine").glob("pagina_*.png"):
            vecchia.unlink()
    with pymupdf.open(pdf) as doc:
        for i, p in enumerate(doc, start=1):
            zoom = larg / p.rect.width
            pix = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
            pagine.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
            if singole:
                dst = pdf.parent / "pagine" / f"pagina_{i}.png"
                dst.parent.mkdir(exist_ok=True)
                p.get_pixmap(dpi=150).save(dst)
                print(dst)
    n = len(pagine)
    cols = n if n <= 2 else (2 if n <= 4 else 3)
    righe = (n + cols - 1) // cols
    w, h = pagine[0].size
    m = 24
    foglio = Image.new("RGB", (cols * (w + m) + m, righe * (h + m + 18) + m), (200, 199, 194))
    d = ImageDraw.Draw(foglio)
    for k, im in enumerate(pagine):
        x = m + (k % cols) * (w + m)
        y = m + (k // cols) * (h + m + 18)
        d.text((x, y), f"pagina {k + 1}/{n}", fill=(40, 40, 40))
        foglio.paste(im, (x, y + 16))
    dst = pdf.with_name(pdf.stem + "_pagine.png")
    foglio.save(dst)
    print(f"{dst}  ({n} pagine)")


if __name__ == "__main__":
    main()
