#!/usr/bin/env python3
"""Ultimo passo della skill: mette in vista solo i risultati e ripulisce la cartella di lavoro.

Uso:  .venv/bin/python .claude/skills/spiega/scripts/pubblica.py "<Materia>/<Capitolo>/<Argomento>/progetto"

Struttura di ogni argomento:
    Analisi 2/Capitolo 3 - Calcolo differenziale/Teorema di Schwarz/
        Teorema di Schwarz.mp4      <- finale.mp4
        Teorema di Schwarz.pdf      <- dispensa.pdf
        Teorema di Schwarz.html     <- interattivo.html (se c'e' una pagina interattiva)
        progetto/                   <- sorgenti: scena.py, pagina.html, dispensa.tex, piano.md, figure/, ...

I risultati vengono SPOSTATI accanto a progetto/ con il nome dell'argomento (sovrascrivendo la
versione precedente). Poi da progetto/ si cancellano i file di lavoro che si possono rigenerare:
bozze, fotogrammi, anteprime, log, e la cache di Manim nella cartella temporanea.
"""
import hashlib
import os
import shutil
import sys
from pathlib import Path

RISULTATI = {"finale.mp4": ".mp4", "dispensa.pdf": ".pdf", "interattivo.html": ".html"}
DA_CANCELLARE_FILE = ["bozza.mp4", "bozza_frames.png", "finale_frames.png", "dispensa_pagine.png",
                      "interattivo_frames.png", "render_bozza.log", "render_finale.log", ".DS_Store"]
DA_CANCELLARE_CARTELLE = ["media", "pagine", "__pycache__"]


def main():
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    prog = Path(sys.argv[1]).resolve()
    if prog.name != "progetto" or not prog.is_dir():
        sys.exit(f"ERRORE: mi aspetto la cartella 'progetto' di un argomento, non {prog}")
    arg = prog.parent
    nome = arg.name

    spostati = []
    for sorgente, est in RISULTATI.items():
        s = prog / sorgente
        if s.exists():
            dest = arg / f"{nome}{est}"
            if dest.exists():
                dest.unlink()
            shutil.move(str(s), str(dest))
            spostati.append(dest)

    for n in DA_CANCELLARE_FILE:
        (prog / n).unlink(missing_ok=True)
    for extra in list(prog.glob("bozza_frames_*.png")) + list(prog.glob("finale_frames_*.png")):
        extra.unlink(missing_ok=True)   # fogli in piu' di frames.py (video lunghi)
    for n in DA_CANCELLARE_CARTELLE:
        shutil.rmtree(prog / n, ignore_errors=True)
    (arg / ".DS_Store").unlink(missing_ok=True)
    # cache di Manim fuori dal progetto (stesso nome che usa render.sh): via anche quella,
    # cosi' cancellando la cartella dell'argomento non resta nulla in giro
    cache = Path(os.environ.get("TMPDIR", "/tmp")) / "doll-manim" / hashlib.sha1(str(prog).encode()).hexdigest()[:16]
    shutil.rmtree(cache, ignore_errors=True)

    if not spostati:
        print(f"(nessun risultato nuovo in {prog}: ho solo ripulito)")
    for p in spostati:
        print(p)


if __name__ == "__main__":
    main()
