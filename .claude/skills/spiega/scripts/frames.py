"""Estrae N fotogrammi da un mp4 e li mette in immagini a griglia (contact sheet).

Uso: python frames.py <video.mp4> [N=9 | auto]
  auto -> secondo l'impegno scritto nel piano.md accanto al video ("**Impegno**: ..."):
          veloce 12, normale 18, approfondito uno ogni 5 s (se manca: normale).
Scrive <video>_frames.png accanto al video (oltre 12 fotogrammi: anche <video>_frames_2.png, _3, ...,
12 per foglio, cosi' restano leggibili) e stampa i percorsi. Guardali TUTTI.
Ogni riquadro ha il timestamp in basso a destra: il verificatore lo usa per
indicare DOVE c'è un problema.
"""
import re
import sys
from pathlib import Path

import av
from PIL import Image, ImageDraw

PER_FOGLIO = 12


def quanti_auto(video: Path, durata: float) -> int:
    piano = video.parent / "piano.md"
    testo = piano.read_text(encoding="utf8") if piano.exists() else ""
    m = re.search(r"\*{0,2}\s*Impegno\s*\*{0,2}\s*[:：]\s*\*{0,2}\s*`?(veloce|normale|approfondito)", testo, re.I)
    liv = m.group(1).lower() if m else "normale"
    if liv == "veloce":
        return 12
    if liv == "normale":
        return 18
    return max(18, round(durata / 5))


def main() -> None:
    video = Path(sys.argv[1])
    arg = sys.argv[2] if len(sys.argv) > 2 else "9"
    with av.open(str(video)) as c:
        s0 = c.streams.video[0]
        durata0 = float(s0.duration * s0.time_base) if s0.duration else float(c.duration / av.time_base)
    n = quanti_auto(video, durata0) if arg == "auto" else int(arg)
    with av.open(str(video)) as c:
        s = c.streams.video[0]
        durata = float(s.duration * s.time_base) if s.duration else float(c.duration / av.time_base)
        tempi = [durata * (i + 0.5) / n for i in range(n)]
        frames, i = [], 0
        for fr in c.decode(video=0):
            if i < n and fr.time is not None and fr.time >= tempi[i]:
                frames.append((fr.time, fr.to_image()))
                i += 1
        if not frames:
            sys.exit("nessun fotogramma letto")

    # fogli vecchi di un render precedente: via, cosi' non si guardano fotogrammi superati
    for vecchio in video.parent.glob(video.stem + "_frames_*.png"):
        vecchio.unlink()
    w, h = frames[0][1].size
    scala = 640 / w
    tw, th = int(w * scala), int(h * scala)
    cols = 3
    gruppi = [frames[i:i + PER_FOGLIO] for i in range(0, len(frames), PER_FOGLIO)]
    for g, gruppo in enumerate(gruppi, start=1):
        rows = (len(gruppo) + cols - 1) // cols
        foglio = Image.new("RGB", (cols * tw, rows * th), "black")
        d = ImageDraw.Draw(foglio)
        for k, (t, img) in enumerate(gruppo):
            x, y = (k % cols) * tw, (k // cols) * th
            foglio.paste(img.resize((tw, th)), (x, y))
            # timestamp in basso a destra: non copre l'etichetta di sezione (in alto a sx)
            d.rectangle([x + tw - 72, y + th - 22, x + tw - 1, y + th - 1], fill="black")
            d.text((x + tw - 67, y + th - 18), f"t={t:5.1f}s", fill="yellow")
            d.rectangle([x, y, x + tw - 1, y + th - 1], outline="grey")
        nome = video.stem + ("_frames.png" if g == 1 else f"_frames_{g}.png")
        out = video.with_name(nome)
        foglio.save(out)
        print(f"{out}  (foglio {g}/{len(gruppi)}: t = {gruppo[0][0]:.1f}-{gruppo[-1][0]:.1f} s)")
    print(f"durata {durata:.1f}s, {len(frames)} fotogrammi in {len(gruppi)} fogli: guardali tutti")


if __name__ == "__main__":
    main()
