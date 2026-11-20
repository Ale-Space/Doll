#!/usr/bin/env python3
"""Crea il link a Falstad CircuitJS per un circuito scritto nel formato testo di CircuitJS.

Uso:  falstad_link.py <circuito.txt> [--open]

- legge il file (una riga per elemento, prima riga "$ ..."; vedi templates/web/circuito_falstad.md);
- toglie righe vuote e commenti ("#" a inizio riga: NON fanno parte del formato, li togliamo noi);
- stampa  https://www.falstad.com/circuit/circuitjs.html?cct=<testo codificato con urllib.parse.quote>
- con --open apre il link nel browser predefinito.

Attenzione: CircuitJS separa i campi anche sul carattere "+", quindi niente "1e+3": scrivi 1000 o 1e3.
Serve internet (il simulatore gira sul sito di Falstad).
"""
import sys
import webbrowser
from pathlib import Path
from urllib.parse import quote

BASE = "https://www.falstad.com/circuit/circuitjs.html"


def link(testo: str) -> str:
    righe = [r.strip() for r in testo.splitlines()]
    righe = [r for r in righe if r and not r.startswith("#")]
    if not righe or not righe[0].startswith("$"):
        sys.exit("La prima riga deve essere l'intestazione '$ flags timestep velocita corrente tensione potenza'")
    for r in righe:
        if "e+" in r.lower():
            sys.exit(f"Esponente con '+' non ammesso (CircuitJS lo tratta come separatore): {r}")
    # safe="" codifica anche "$", "/", "&": il link resta valido in ogni contesto (markdown, HTML, terminale)
    return f"{BASE}?cct={quote(chr(10).join(righe) + chr(10), safe='')}"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    url = link(Path(args[0]).read_text(encoding="utf-8"))
    print(url)
    if "--open" in sys.argv:
        webbrowser.open(url)


if __name__ == "__main__":
    main()
