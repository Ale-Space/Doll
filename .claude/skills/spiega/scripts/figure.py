#!/usr/bin/env python3
"""Estrae le figure per la dispensa PDF da un video Manim o da una pagina interattiva Doll.

Uso:
  .venv/bin/python figure.py video <video.mp4> <t1,t2,...> <cartella> [--inizio N]
      salva un PNG per ogni istante (in secondi, es. 3,12.5,24): f1.png, f2.png, ...
  .venv/bin/python figure.py web <interattivo.html> <cartella> [--inizio N] [--intera]
      apre la pagina con Chrome headless, aspetta Doll.pronto(), applica uno dopo l'altro
      gli stati registrati (window.dollStati, cioe' Doll.stati / Doll.guida) e salva un PNG
      per stato: f1.png, f2.png, ... Di default fotografa solo la vista (.doll-vista), che
      e' la parte utile in un PDF; con --intera fotografa tutta la finestra.

--inizio N  numera da fN.png (es. --inizio 4 se f1-f3 vengono gia' dal video).
Stampa una riga per file: percorso, istante o nome dello stato (utile per le didascalie).
Nel .tex:  \\dollfigura{figure/f1.png}{...}  o  \\dollfotogrammi{figure/f1.png :: ...}{...}{...}
"""
import sys
from pathlib import Path


def opzione(nome, default=None):
    if nome in sys.argv:
        i = sys.argv.index(nome)
        val = sys.argv[i + 1]
        del sys.argv[i:i + 2]
        return val
    return default


def da_video(video: Path, tempi: list[float], out: Path, inizio: int) -> None:
    import av

    with av.open(str(video)) as c:
        s = c.streams.video[0]
        durata = float(s.duration * s.time_base) if s.duration else float(c.duration / av.time_base)
        for k, t in enumerate(tempi):
            t = min(max(t, 0.0), max(durata - 0.05, 0.0))
            # salta al keyframe precedente, poi decodifica fino all'istante richiesto
            c.seek(int(t / s.time_base), stream=s, backward=True, any_frame=False)
            img, t_letto = None, None
            for fr in c.decode(s):
                if fr.time is None:
                    continue
                img, t_letto = fr.to_image(), fr.time
                if fr.time >= t - 0.5 / float(s.average_rate or 30):
                    break
            if img is None:
                sys.exit(f"nessun fotogramma letto a t={t}")
            dst = out / f"f{inizio + k}.png"
            img.save(dst)
            print(f"{dst}  t={t_letto:.2f}s  ({img.width}x{img.height})")


# testo della didascalia del passo (Doll.guida la scrive in #didascalia), con le formule
# KaTeX riportate al loro sorgente TeX tra $...$: si incolla cosi' com'e' nel .tex
TESTO_DIDASCALIA = """(() => {
  const d = document.getElementById('didascalia'); if (!d) return '';
  const c = d.cloneNode(true);
  c.querySelectorAll('button, .passo').forEach(e => e.remove());
  c.querySelectorAll('.katex').forEach(k => {
    const a = k.querySelector('annotation');
    k.replaceWith(a ? '$' + a.textContent.trim() + '$' : k.textContent);
  });
  return c.textContent.replace(/\\s+/g, ' ').trim();
})()"""


def da_web(pagina: Path, out: Path, inizio: int, intera: bool) -> None:
    from playwright.sync_api import sync_playwright

    errori = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        # scala 2: immagini nitide anche stampate
        pg = b.new_page(viewport={"width": 1280, "height": 800}, device_scale_factor=2)
        pg.on("pageerror", lambda e: errori.append(str(e)))
        pg.goto(pagina.as_uri())
        try:
            pg.wait_for_function("window.dollPronto === true", timeout=15000)
        except Exception:
            print("ATTENZIONE: Doll.pronto() non e' mai stato chiamato entro 15 s", file=sys.stderr)
        pg.wait_for_timeout(800)
        nomi = pg.evaluate("(window.dollStati || []).map(s => s.nome)")
        if not nomi:
            print("ATTENZIONE: nessuno stato registrato (Doll.stati / Doll.guida): salvo solo lo stato iniziale",
                  file=sys.stderr)
        vista = None if intera else pg.locator(".doll-vista").first
        if vista is not None and not vista.count():
            vista = None

        def foto(dst):
            (vista.screenshot(path=str(dst)) if vista is not None else pg.screenshot(path=str(dst)))

        if not nomi:
            dst = out / f"f{inizio}.png"
            foto(dst)
            print(f"{dst}  stato iniziale")
        for k, nome in enumerate(nomi):
            pg.evaluate(f"window.dollStati[{k}].applica()")
            pg.wait_for_timeout(700)
            dst = out / f"f{inizio + k}.png"
            foto(dst)
            # il testo della didascalia del passo, se c'e' (Doll.guida lo scrive in #didascalia)
            testo = pg.evaluate(TESTO_DIDASCALIA)
            print(f"{dst}  stato {k + 1}: {nome}" + (f"  | {testo}" if testo else ""))
        b.close()
    if errori:
        print("ERRORI JavaScript nella pagina:\n  " + "\n  ".join(errori), file=sys.stderr)
        sys.exit(1)


def main() -> None:
    inizio = int(opzione("--inizio", "1"))
    intera = "--intera" in sys.argv
    if intera:
        sys.argv.remove("--intera")
    if len(sys.argv) < 4 or sys.argv[1] not in ("video", "web"):
        sys.exit(__doc__)
    modo = sys.argv[1]
    if modo == "video":
        if len(sys.argv) < 5:
            sys.exit(__doc__)
        video, out = Path(sys.argv[2]), Path(sys.argv[4])
        tempi = [float(x.replace(" ", "")) for x in sys.argv[3].split(",") if x.strip()]
        out.mkdir(parents=True, exist_ok=True)
        da_video(video, tempi, out, inizio)
    else:
        pagina, out = Path(sys.argv[2]).resolve(), Path(sys.argv[3])
        out.mkdir(parents=True, exist_ok=True)
        da_web(pagina, out, inizio, intera)


if __name__ == "__main__":
    main()
