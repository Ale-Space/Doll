#!/usr/bin/env python3
"""Controllo automatico dello stile dei video Doll (regole di guide/manim.md).

Uso:  .venv/bin/python .claude/skills/spiega/scripts/controllo_stile.py "<cartella progetto>"

Controlla:
  1. scena.py  - classe Esercizio, kit importato, nessun colore/sfondo proprio, niente schede o elenchi,
                 didascalie brevi, niente pause lunghe, niente montaggio di video;
  2. piano.md  - il copione (frase wow, gesto visivo, tabella secondo per secondo);
  3. il video  - finale.mp4 (o bozza.mp4): durata, tratti fermi e frazione di tempo in movimento. Un
                 video-presentazione (oggetti fermi, compaiono scritte) si muove poco e viene bocciato.
I limiti dipendono dall'impegno scritto in piano.md ("**Impegno**: veloce | normale | approfondito";
se manca vale normale): vedi LIVELLI qui sotto e SKILL.md, «Livelli di impegno».
Stampa ERRORE/AVVISO e l'esito; esce con codice 1 se c'e' almeno un ERRORE.
Vale per qualunque AI: un video che non passa questo controllo non si consegna.
"""
import re
import sys
from pathlib import Path

import numpy as np

# soglie del movimento tarate su 3 video buoni (in movimento 55-65% del tempo) e 2 video-presentazione
# (23-40%): e' la frazione di tempo in movimento che li separa; l'area che cambia no (un grafico 2D con una
# retta che scorre cambia poca superficie ma e' un buon video). Valgono per tutti i livelli: un video lungo
# deve muoversi quanto uno corto.
FERMO_MAX = 3.0          # secondi consecutivi senza nulla che cambi
MOVIMENTO_MIN = 0.48     # frazione del tempo in cui qualcosa si muove: sotto e' una presentazione
MOVIMENTO_BUONO = 0.55   # sotto questa soglia: avviso (meno pause, piu' gesto)
WAIT_MAX = 2.5

# limiti per livello di impegno: durata ammessa (sotto/sopra = ERRORE), durata ideale (fuori = AVVISO),
# parole delle didascalie (avviso, errore), parole di un Text, MathTex oltre i quali avvisare, formule chiave
LIVELLI = {
    "veloce":       dict(ammessa=(15, 50),  ideale=(20, 45),  parole=(8, 10),  text=12, mathtex=30, formule=False),
    "normale":      dict(ammessa=(35, 100), ideale=(45, 90),  parole=(10, 12), text=14, mathtex=45, formule=True),
    "approfondito": dict(ammessa=(75, 200), ideale=(90, 180), parole=(12, 14), text=16, mathtex=80, formule=True),
}
PREDEFINITO = "normale"


def leggi_impegno(piano_testo):
    """Livello di impegno da piano.md; None se non c'e'."""
    m = re.search(r"\*{0,2}\s*Impegno\s*\*{0,2}\s*[:：]\s*\*{0,2}\s*`?(veloce|normale|approfondito)",
                  piano_testo or "", re.I)
    return m.group(1).lower() if m else None


def controlla_scena(testo, err, avv, liv, nome_liv):
    parole_avviso, parole_errore = liv["parole"]
    if not re.search(r"class\s+Esercizio\s*\(", testo):
        err.append("scena.py: manca la classe Esercizio (render.sh renderizza solo quella).")
    if not re.search(r"from\s+doll_kit\s+import", testo):
        err.append("scena.py: non importa il kit (from doll_kit import *): palette e funzioni del kit sono obbligatorie.")
    colori = sorted(set(re.findall(r"""["']#[0-9A-Fa-f]{3,8}["']""", testo)))
    if colori:
        err.append(f"scena.py: colori propri {', '.join(colori[:6])}: usa solo le costanti del kit (manuale §6).")
    if "background_color" in testo:
        err.append("scena.py: cambia lo sfondo: lo sfondo e' sempre quello nero di Manim (manuale §6).")
    for vietato, perche in (("RoundedRectangle", "schede/cornici da presentazione"),
                            ("BulletedList", "elenchi a schermo"), ("Paragraph(", "paragrafi a schermo")):
        if vietato in testo:
            err.append(f"scena.py: usa {vietato.rstrip('(')} ({perche}): vietato (manuale §9).")
    if re.search(r"^\s*(import|from)\s+(av|moviepy|ffmpeg|subprocess|imageio)\b", testo, re.M) or "ffmpeg" in testo:
        err.append("scena.py: tocca file video o processi esterni: vietato montare video (manuale §9).")
    if not re.search(r"\btitolo\s*\(", testo):
        err.append("scena.py: manca titolo(...) del kit (atto 0).")
    if not re.search(r"\brisultato_angolo\s*\(", testo):
        avv.append("scena.py: manca risultato_angolo(...): il risultato finale nel riquadro (atto 5).")
    # didascalie: cambia_didascalia(self, vecchia, "testo") e didascalia("testo")
    for m in re.finditer(r"""(?:cambia_didascalia\s*\([^,]*,[^,]*,|didascalia(?:_libro)?\s*\()\s*(?:r|f|rf)?(["'])(.+?)\1""", testo):
        frase = m.group(2)
        n = len([w for w in frase.split() if any(c.isalpha() for c in w)])   # i simboli (→, −1) non contano
        if n > parole_errore:
            err.append(f"didascalia di {n} parole (impegno {nome_liv}: max {parole_avviso}): \"{frase}\"")
        elif n > parole_avviso:
            avv.append(f"didascalia di {n} parole (impegno {nome_liv}: meglio <= {parole_avviso}): \"{frase}\"")
    for m in re.finditer(r"""\bText\s*\(\s*(?:r|f|rf)?(["'])(.+?)\1""", testo):
        if len(m.group(2).split()) > liv["text"]:
            err.append(f"Text con {len(m.group(2).split())} parole: niente frasi lunghe a schermo: \"{m.group(2)[:60]}...\"")
    for m in re.finditer(r"self\.wait\(\s*([0-9.]+)", testo):
        if float(m.group(1)) > WAIT_MAX:
            err.append(f"self.wait({m.group(1)}): pausa oltre {WAIT_MAX} s (manuale §8).")
    n_tex = len(re.findall(r"\bMathTex\s*\(", testo))
    if n_tex > liv["mathtex"]:
        avv.append(f"scena.py: {n_tex} MathTex: troppe formule? Il video mostra, non scrive (manuale §2).")
    if re.search(r"\bformula_chiave\s*\(", testo) and not liv["formule"]:
        err.append("scena.py: formula_chiave(...) con impegno veloce: nel livello veloce niente formule della "
                   "dimostrazione (manuale §7).")
    if nome_liv == "approfondito" and not re.search(r"\bcapitolo\s*\(", testo):
        avv.append("scena.py: impegno approfondito senza capitolo(...): il video lungo va diviso in capitoli "
                   "(manuale §3).")


def controlla_piano(testo, err, avv, nome_liv):
    for voce in ("Frase wow", "Gesto visivo"):
        if voce.lower() not in testo.lower():
            err.append(f"piano.md: manca \"{voce}\" nel copione (manuale §4).")
    if not re.search(r"\|\s*t\s*\(s\)\s*\|", testo):
        err.append("piano.md: manca la tabella del copione (| t (s) | Cosa si vede | Cosa si muove | Didascalia |).")
    for voce in ("Domanda di previsione", "Obiettivo", "Preconcetto"):
        if voce.lower() not in testo.lower():
            avv.append(f"piano.md: manca \"{voce}\" (guide/didattica.md).")
    basso = testo.lower()
    if nome_liv in ("normale", "approfondito") and not re.search(r"passaggi\s*(→|->|-)\s*gesti", basso):
        err.append(f"piano.md: impegno {nome_liv} senza la tabella \"Passaggi → gesti\" (manuale §4): ogni "
                   "passaggio della soluzione deve avere il suo gesto nel video.")
    if nome_liv == "approfondito" and "capitoli" not in basso:
        err.append("piano.md: impegno approfondito senza l'elenco dei \"Capitoli\" (manuale §3, §4).")


def misura_video(path):
    import av
    campioni, prossimo, passo = [], 0.0, 0.2
    with av.open(str(path)) as c:
        for fr in c.decode(video=0):
            if fr.time is None or fr.time < prossimo:
                continue
            g = np.asarray(fr.to_image().convert("L").resize((192, 108)), dtype=np.float32)
            campioni.append((fr.time, g))
            prossimo += passo
    durata = campioni[-1][0] if campioni else 0.0
    aree, fermo, fermo_max, t_fermo = [], 0.0, 0.0, 0.0
    for (ta, a), (tb, b) in zip(campioni, campioni[1:]):
        area = float((np.abs(a - b) > 12).mean())
        aree.append(area)
        if area < 0.002:
            fermo += tb - ta
            if fermo > fermo_max:
                fermo_max, t_fermo = fermo, tb
        else:
            fermo = 0.0
    aree = np.array(aree) if aree else np.zeros(1)
    return dict(durata=durata, fermo_max=fermo_max, t_fermo=t_fermo,
                movimento=float((aree >= 0.002).mean()), grande=float((aree > 0.03).mean()))


def controlla_video(p, err, avv, liv, nome_liv):
    v = next((p / n for n in ("finale.mp4", "bozza.mp4") if (p / n).exists()), None)
    if v is None:
        avv.append("nessun video (finale.mp4 o bozza.mp4) da misurare: rifai il controllo dopo il render.")
        return None
    m = misura_video(v)
    d = m["durata"]
    (a0, a1), (i0, i1) = liv["ammessa"], liv["ideale"]
    if d < a0:
        err.append(f"{v.name}: dura {d:.1f} s, troppo poco per l'impegno {nome_liv} (ammesso {a0}-{a1} s, ideale "
                   f"{i0}-{i1}): manca qualche passaggio? Ogni passaggio deve avere il suo gesto (manuale §2.8).")
    elif d > a1:
        err.append(f"{v.name}: dura {d:.1f} s, troppo per l'impegno {nome_liv} (ammesso {a0}-{a1} s, ideale "
                   f"{i0}-{i1}).")
    elif not i0 <= d <= i1:
        avv.append(f"{v.name}: dura {d:.1f} s (impegno {nome_liv}: ideale {i0}-{i1} s).")
    if m["fermo_max"] > FERMO_MAX:
        err.append(f"{v.name}: fermo per {m['fermo_max']:.1f} s di fila (fino a t = {m['t_fermo']:.1f} s; max {FERMO_MAX:.0f} s).")
    if m["movimento"] < MOVIMENTO_MIN:
        err.append(f"{v.name}: si muove solo il {m['movimento']:.0%} del tempo (min {MOVIMENTO_MIN:.0%}): "
                   "sembra una presentazione. Serve un gesto visivo che si muove (manuale §2, §9).")
    elif m["movimento"] < MOVIMENTO_BUONO:
        avv.append(f"{v.name}: si muove il {m['movimento']:.0%} del tempo: accorcia le pause o allunga il gesto "
                   f"principale (meglio oltre il {MOVIMENTO_BUONO:.0%}).")
    return v.name, m


def main():
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    p = Path(sys.argv[1]).resolve()
    err, avv = [], []
    piano = p / "piano.md"
    testo_piano = piano.read_text(encoding="utf8") if piano.exists() else ""
    nome_liv = leggi_impegno(testo_piano)
    if nome_liv is None:
        nome_liv = PREDEFINITO
        if piano.exists():
            avv.append(f"piano.md: manca \"**Impegno**: veloce | normale | approfondito\": uso {PREDEFINITO}.")
    liv = LIVELLI[nome_liv]
    scena = p / "scena.py"
    if not scena.exists():
        err.append("manca scena.py.")
    else:
        controlla_scena(scena.read_text(encoding="utf8"), err, avv, liv, nome_liv)
    if piano.exists():
        controlla_piano(testo_piano, err, avv, nome_liv)
    else:
        avv.append("manca piano.md (con il copione): normale solo per i progetti vecchi.")
    misura = controlla_video(p, err, avv, liv, nome_liv)

    print(f"CONTROLLO STILE: {p}")
    print(f"  impegno: {nome_liv} (durata ideale {liv['ideale'][0]}-{liv['ideale'][1]} s, didascalie <= "
          f"{liv['parole'][0]} parole)")
    if misura:
        nome, m = misura
        print(f"  {nome}: {m['durata']:.1f} s, in movimento {m['movimento']:.0%}, fermo max {m['fermo_max']:.1f} s")
    for e in err:
        print("ERRORE:", e)
    for a in avv:
        print("AVVISO:", a)
    print("ESITO:", "DA_CORREGGERE" if err else "OK")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
