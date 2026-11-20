"""Converte le pagine di un PDF in PNG, così Claude le può leggere come immagini.

Uso: .venv/bin/python pdf_pagine.py <file.pdf> <cartella_output> [dpi=130]
Stampa i percorsi delle immagini, una per riga.
"""
import sys
from pathlib import Path

import pymupdf


def main() -> None:
    pdf, out = Path(sys.argv[1]), Path(sys.argv[2])
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 130
    out.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(pdf) as doc:
        for i, pagina in enumerate(doc, start=1):
            dest = out / f"pagina_{i}.png"
            pagina.get_pixmap(dpi=dpi).save(dest)
            print(dest)


if __name__ == "__main__":
    main()
