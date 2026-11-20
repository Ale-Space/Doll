#!/usr/bin/env python3
"""Controllo automatico di una pagina interattiva con Chrome headless.

Uso:  web_check.py <interattivo.html> [--mobile]

- apre la pagina a 1280x800, raccoglie errori JavaScript e della console;
- aspetta window.dollPronto (Doll.pronto());
- fotografa lo stato iniziale e ogni stato registrato con Doll.stati / Doll.guida;
- prova anche Play per 1,5 s se c'e' un'animazione;
- salva <nome>_frames.png (griglia) accanto alla pagina e stampa un riepilogo.
Esce con codice 1 se ci sono errori JavaScript.
"""
import io
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright


def griglia(immagini, etichette, dst, colonne=3, larg=640):
    scal = [im.resize((larg, int(im.height * larg / im.width))) for im in immagini]
    h = max(im.height for im in scal)
    righe = (len(scal) + colonne - 1) // colonne
    out = Image.new("RGB", (colonne * larg, righe * (h + 26)), "white")
    d = ImageDraw.Draw(out)
    for i, (im, et) in enumerate(zip(scal, etichette)):
        x, y = (i % colonne) * larg, (i // colonne) * (h + 26)
        out.paste(im, (x, y + 26))
        d.text((x + 8, y + 6), et, fill="black")
    out.save(dst)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pagina = Path(sys.argv[1]).resolve()
    mobile = "--mobile" in sys.argv
    errori, foto, nomi = [], [], []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        pg = b.new_page(viewport={"width": 390, "height": 844} if mobile else {"width": 1280, "height": 800},
                        device_scale_factor=1)
        pg.on("pageerror", lambda e: errori.append(f"pageerror: {e}"))
        pg.on("console", lambda m: m.type == "error" and errori.append(f"console: {m.text}"))
        pg.goto(pagina.as_uri())
        try:
            pg.wait_for_function("window.dollPronto === true", timeout=15000)
        except Exception:
            errori.append("Doll.pronto() non e' mai stato chiamato entro 15 s")
        pg.wait_for_timeout(800)
        shot = lambda: Image.open(io.BytesIO(pg.screenshot(full_page=False))).convert("RGB")
        foto.append(shot()); nomi.append("iniziale")
        n = pg.evaluate("(window.dollStati || []).length")
        nomi_stati = pg.evaluate("(window.dollStati || []).map(s => s.nome)")
        for i in range(n):
            try:
                pg.evaluate(f"window.dollStati[{i}].applica()")
            except Exception as e:
                errori.append(f"stato {i}: {e}")
            pg.wait_for_timeout(700)
            foto.append(shot()); nomi.append(f"stato {i + 1}: {nomi_stati[i]}")
        # Play, se c'e'
        play = pg.locator("button.doll-btn.primario:visible", has_text="Play")
        if play.count():
            play.first.click(); pg.wait_for_timeout(1500)
            foto.append(shot()); nomi.append("dopo 1,5 s di Play")
        b.close()
    dst = pagina.with_name(pagina.stem + ("_mobile" if mobile else "") + "_frames.png")
    griglia(foto, nomi, dst)
    print(json.dumps({"pagina": str(pagina), "stati": n, "errori": errori, "frames": str(dst)}, ensure_ascii=False, indent=1))
    sys.exit(1 if errori else 0)


if __name__ == "__main__":
    main()
