#!/usr/bin/env python3
"""Rende una pagina interattiva AUTOSUFFICIENTE (un solo file .html, funziona offline).

Uso:  web_build.py <sorgente.html> [uscita.html]     (default: interattivo.html nella stessa cartella)

Nel sorgente metti, dentro <head>, un marcatore con le librerie da includere:
    <!-- doll:lib katex jsxgraph plotly three wavedrom 3dmol digitaljs -->
Il marcatore viene sostituito con le librerie (inline) + doll.css + doll.js.
KaTeX e doll vengono sempre inclusi.
"""
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent / "kit" / "web"
LIB = KIT / "lib"
LIBRERIE = {
    "katex": (["katex.inline.min.css"], ["katex.min.js", "auto-render.min.js"]),
    "jsxgraph": (["jsxgraph.css"], ["jsxgraphcore.js"]),
    "plotly": ([], ["plotly.min.js"]),
    "three": ([], ["three-bundle.min.js"]),  # window.THREE (+ THREE.OrbitControls, CSS2DRenderer)
    "wavedrom": ([], ["wavedrom-skin-default.js", "wavedrom.min.js"]),
    "3dmol": ([], ["3Dmol-min.js"]),
    "digitaljs": ([], ["digitaljs.js"]),  # window.digitaljs (simulatore logico; CSS incluso nel JS, ~2,5 MB)
}


def blocco(nomi):
    css, js = [], []
    for n in ["katex"] + [n for n in nomi if n != "katex"]:
        if n not in LIBRERIE:
            sys.exit(f"Libreria sconosciuta: {n}. Disponibili: {', '.join(LIBRERIE)}")
        c, j = LIBRERIE[n]
        css += [LIB / f for f in c]
        js += [LIB / f for f in j]
    mancanti = [p.name for p in css + js if not p.is_file()]
    if mancanti:
        sys.exit(f"Librerie web mancanti in {LIB}: {', '.join(mancanti)}. Consulta il README.")
    css.append(KIT / "doll.css")
    js.append(KIT / "doll.js")
    out = [f"<style>/* {p.name} */\n{p.read_text()}\n</style>" for p in css]
    # </script> dentro una libreria chiuderebbe il tag: lo spezziamo
    out += [f"<script>/* {p.name} */\n{p.read_text().replace('</script', '<\\/script')}\n</script>" for p in js]
    return "\n".join(out)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1]).resolve()
    dst = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src.parent / "interattivo.html"
    html = src.read_text()
    m = re.search(r"<!--\s*doll:lib([^>]*)-->", html)
    if not m:
        sys.exit("Manca il marcatore <!-- doll:lib ... --> nel <head>")
    html = html[: m.start()] + blocco(m.group(1).split()) + html[m.end():]
    dst.write_text(html)
    print(f"{dst}  ({dst.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
