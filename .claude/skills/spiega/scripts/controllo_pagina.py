#!/usr/bin/env python3
"""Controllo automatico delle pagine interattive Doll (regole di guide/web.md).

Uso:  .venv/bin/python .claude/skills/spiega/scripts/controllo_pagina.py "<cartella progetto>"

Serve interattivo.html (prodotto da web_build.py). Controlla:
  1. pagina.html - usa il kit (Doll.guida, Doll.pronto), niente risorse esterne (internet), colori dai ruoli;
  2. piano.md    - frase wow e gesto/esplorazione (come per i video);
  3. la pagina   - in Chrome headless: nessun errore JavaScript; la guida ha i passi del livello di impegno
                   (veloce 3-4, normale 3-6, approfondito 4-10); ogni passo CAMBIA la
                   vista (un passo che cambia solo la didascalia e' una slide); didascalie brevi; c'e' almeno un
                   controllo da usare; Play (se c'e') fa muovere qualcosa; sul telefono niente scorrimento
                   orizzontale.
Stampa ERRORE/AVVISO e l'esito; esce con codice 1 se c'e' almeno un ERRORE.
"""
import io
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# passi della guida per livello di impegno ("**Impegno**: ..." in piano.md; se manca: normale).
# Il minimo e' tollerante (3) per tutti; il massimo cresce con l'impegno (guide/web.md §1).
PASSI_PER_LIVELLO = {"veloce": (3, 4), "normale": (3, 6), "approfondito": (4, 10)}
PASSI_MIN, PASSI_MAX = PASSI_PER_LIVELLO["normale"]
PAROLE_AVVISO, PAROLE_ERRORE = 12, 16


def leggi_impegno(testo):
    m = re.search(r"\*{0,2}\s*Impegno\s*\*{0,2}\s*[:：]\s*\*{0,2}\s*`?(veloce|normale|approfondito)", testo or "", re.I)
    return m.group(1).lower() if m else "normale"
CAMBIO_MIN = 0.004          # frazione di pixel della vista che deve cambiare tra due passi


def statico(html, err, avv):
    if "Doll.guida(" not in html:
        err.append("pagina.html: manca Doll.guida([...]): il percorso guidato e' obbligatorio.")
    if "Doll.pronto(" not in html:
        err.append("pagina.html: manca Doll.pronto() (il controllo non sa quando la pagina e' pronta).")
    esterni = [u for u in re.findall(r"""(?:src|href)\s*=\s*["'](https?://[^"']+)""", html) if "falstad.com" not in u]
    if esterni:
        err.append(f"pagina.html: risorse da internet ({esterni[0][:60]}...): la pagina deve funzionare offline.")
    if re.search(r"\bfetch\s*\(|XMLHttpRequest", html):
        err.append("pagina.html: usa fetch/XMLHttpRequest: niente caricamenti, tutto nel file.")
    colori = set(re.findall(r"#[0-9a-fA-F]{6}\b", re.sub(r"<!--.*?-->", "", html, flags=re.S)))
    if len(colori) > 4:
        avv.append(f"pagina.html: {len(colori)} colori scritti a mano: usa Doll.ruolo / Doll.col (guide/web.md §4).")


def piano(testo, err):
    if "frase wow" not in testo.lower():
        err.append("piano.md: manca \"Frase wow\" (cosa capira' chi usa la pagina).")


def dinamico(pagina, err, avv):
    from playwright.sync_api import sync_playwright
    misure = {}
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        js = []
        pg = b.new_page(viewport={"width": 1280, "height": 800}, device_scale_factor=1)
        pg.on("pageerror", lambda e: js.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and js.append(m.text))
        pg.goto(pagina.as_uri())
        try:
            pg.wait_for_function("window.dollPronto === true", timeout=15000)
        except Exception:
            err.append("la pagina non chiama Doll.pronto() entro 15 s.")
        pg.wait_for_timeout(600)
        vista = pg.locator("#vista")
        if not vista.count():
            err.append("manca section#vista (la zona del disegno).")
            b.close()
            return misure

        def foto():
            return np.asarray(Image.open(io.BytesIO(vista.screenshot())).convert("L"), dtype=np.int16)

        stati = pg.evaluate("(window.dollStati || []).map(s => s.nome)")
        passi = [i for i, n in enumerate(stati) if n.startswith("passo ")]
        misure["passi"] = len(passi)
        if not PASSI_MIN <= len(passi) <= PASSI_MAX:
            err.append(f"la guida ha {len(passi)} passi (con questo impegno servono {PASSI_MIN}-{PASSI_MAX}).")
        prec = None
        didascalie = []
        for k, i in enumerate(passi):
            pg.evaluate(f"window.dollStati[{i}].applica()")
            pg.wait_for_timeout(700)
            testo = pg.evaluate("(document.querySelector('#didascalia .testo, #didascalia span:not(.passo)') || {}).textContent || ''")
            didascalie.append(testo)
            n = len([w for w in testo.split() if any(c.isalpha() for c in w)])
            if n > PAROLE_ERRORE:
                err.append(f"passo {k + 1}: didascalia di {n} parole (max {PAROLE_AVVISO}): \"{testo.strip()[:70]}\"")
            elif n > PAROLE_AVVISO:
                avv.append(f"passo {k + 1}: didascalia di {n} parole (meglio <= {PAROLE_AVVISO}).")
            img = foto()
            if prec is not None and img.shape == prec.shape:
                cambio = float((np.abs(img - prec) > 10).mean())
                if cambio < CAMBIO_MIN:
                    err.append(f"passo {k + 1}: la vista non cambia rispetto al passo prima ({cambio:.2%}): "
                               "ogni passo deve far vedere qualcosa di nuovo, non solo cambiare la didascalia.")
            prec = img
        if didascalie and not any("?" in t for t in didascalie):
            avv.append("nessun passo della guida pone una domanda di previsione (guide/didattica.md: prevedi, osserva, spiega).")
        if didascalie and "prova" not in didascalie[-1].lower():
            avv.append("l'ultimo passo della guida non e' un \"Prova tu\" con un compito e un riscontro immediato.")
        parole = pg.evaluate("(document.querySelector('#vista').innerText || '').split(/\\s+/).filter(w => /[a-zA-Zàèéìòù]/.test(w)).length")
        misure["parole_vista"] = parole
        if parole > 60:
            err.append(f"nella vista ci sono {parole} parole: niente paragrafi o dimostrazioni scritte nel disegno "
                       "(i passaggi vanno nella dispensa).")
        elif parole > 35:
            avv.append(f"nella vista ci sono {parole} parole: tieni solo etichette brevi.")
        n_ctrl = pg.evaluate("document.querySelectorAll('#pannello input, #pannello select').length")
        misure["controlli"] = n_ctrl
        if n_ctrl == 0 and not pg.evaluate("!!document.querySelector('#vista [draggable], #vista .jxgbox, #vista canvas')"):
            avv.append("nessun controllo nel pannello (slider, scelte): la pagina e' da esplorare, non solo da sfogliare.")
        # Play: su una pagina appena aperta (nei passi della guida puo' essere fermo apposta)
        pp = b.new_page(viewport={"width": 1280, "height": 800}, device_scale_factor=1)
        pp.goto(pagina.as_uri())
        try:
            pp.wait_for_function("window.dollPronto === true", timeout=15000)
        except Exception:
            pass
        pp.wait_for_timeout(500)
        play = pp.locator("#pannello button.doll-btn.primario", has_text="Play")
        if play.count():
            vv = pp.locator("#vista")
            f0 = np.asarray(Image.open(io.BytesIO(vv.screenshot())).convert("L"), dtype=np.int16)
            play.first.click()
            pp.wait_for_timeout(1800)
            f1 = np.asarray(Image.open(io.BytesIO(vv.screenshot())).convert("L"), dtype=np.int16)
            if f0.shape == f1.shape and float((np.abs(f1 - f0) > 10).mean()) < 0.001:
                err.append("Play non fa muovere niente nella vista.")
        for e in js:
            err.append(f"errore JavaScript: {e[:120]}")
        tel = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
        tel.goto(pagina.as_uri())
        try:
            tel.wait_for_function("window.dollPronto === true", timeout=15000)
        except Exception:
            pass
        if tel.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2"):
            err.append("sul telefono la pagina scorre in orizzontale (qualcosa e' piu' largo dello schermo).")
        b.close()
    return misure


def main():
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    p = Path(sys.argv[1]).resolve()
    err, avv = [], []
    sorg = p / "pagina.html"
    if sorg.exists():
        statico(sorg.read_text(encoding="utf8"), err, avv)
    else:
        err.append("manca pagina.html (il sorgente della pagina).")
    global PASSI_MIN, PASSI_MAX
    if (p / "piano.md").exists():
        testo_piano = (p / "piano.md").read_text(encoding="utf8")
        piano(testo_piano, err)
        PASSI_MIN, PASSI_MAX = PASSI_PER_LIVELLO[leggi_impegno(testo_piano)]
    else:
        avv.append("manca piano.md: normale solo per i progetti vecchi.")
    pagina = p / "interattivo.html"
    misure = {}
    if pagina.exists():
        misure = dinamico(pagina, err, avv)
    else:
        err.append("manca interattivo.html: esegui prima web_build.py.")
    print(f"CONTROLLO PAGINA: {p}")
    if misure:
        print(f"  passi della guida: {misure.get('passi')}, controlli: {misure.get('controlli')}, parole nella vista: {misure.get('parole_vista')}")
    for e in err:
        print("ERRORE:", e)
    for a in avv:
        print("AVVISO:", a)
    print("ESITO:", "DA_CORREGGERE" if err else "OK")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
