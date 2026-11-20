# Doll — istruzioni per Codex

Questa repo contiene una skill che **spiega visivamente** esercizi, teoremi e concetti della triennale
di Ingegneria Fisica: di base un video Manim e la spiegazione in chat; la dispensa PDF solo se l'utente la
chiede; la pagina interattiva solo se la chiede e solo per argomenti pratici (mai per la teoria).

- La skill è `spiega` (`.agents/skills/spiega`, link a `.claude/skills/spiega`). Si invoca con
  `$spiega ...` o scegliendola da `/skills`; seguila alla lettera: leggi `.claude/skills/spiega/SKILL.md`.
- Gli agenti (esperti per materia, costruttori, verificatore) sono in `.codex/agents/*.toml`, con il
  trattino basso nel nome (`esperto_analisi`, `costruttore_web`, `verificatore`, ...). La skill dice
  quando avviarli: è un'istruzione esplicita a delegare.
- Python: sempre `.venv/bin/python` (Manim, SymPy, SciPy, Playwright, matplotlib sono lì).
- I risultati vanno in `<Materia>/<Capitolo>/<Argomento>/`, i sorgenti nella sua sottocartella `progetto/`
  (vedi «Dove vanno i file» in SKILL.md; non versionati). Nella root niente altri file.

## Regole che valgono sempre (anche senza subagenti)
- Se gli agenti personalizzati non partono, svolgi tu i ruoli **in sequenza**, leggendo per intero
  `.claude/agents/<ruolo>.md` (esperto, costruttore, verificatore): è la fonte; i `.toml` ne sono copie.
  Non saltare il copione né la verifica.
- Per modificare i file usa lo strumento di modifica, non `sed -i` (su macOS senza suffisso fallisce in silenzio).
- **Video**: prima di scrivere `scena.py` leggi tutto `.claude/skills/spiega/guide/manim.md` e l'esempio più
  vicino in `.claude/skills/spiega/esempi/`. Usa solo il kit (`from doll_kit import *`) e i suoi colori.
  `.venv/bin/python .claude/skills/spiega/scripts/controllo_stile.py "<progetto>"` deve dire `OK` prima della
  consegna: un video che non passa non si consegna.
- **Pagine interattive**: leggi tutto `.claude/skills/spiega/guide/web.md`; `controllo_pagina.py "<progetto>"` deve
  dire `OK` prima della consegna.
- **Mai montare video** (av, ffmpeg, moviepy) e mai lavorare in cartelle temporanee: tutto in `progetto/`;
  per cambiare un video si modifica `scena.py` e si rifà il render completo.
- Alla fine della procedura (normale o veloce), dopo il render finale e i controlli:
  `.venv/bin/python .claude/skills/spiega/scripts/pubblica.py "<progetto>"`. Figure e PDF solo se l'utente ha chiesto il PDF.
- **Non fare la pagina web al posto del video**, né quando non è stata chiesta, né per teoremi o concetti teorici.
- **Livello di impegno** (SKILL.md, «Livelli di impegno»): `veloce` | `normale` (predefinito) | `approfondito`,
  scritto in `piano.md` come `**Impegno**: ...`. Decide durata del video (20–45 s / 45–90 s / 90–180 s), capitoli,
  formule ammesse, pagine del PDF, passi della pagina, giri del verificatore. Il lavoro deve essere corretto e
  completo per il livello: **non accorciare** un passaggio necessario per fare prima.
- Claude Code usa gli stessi file: la skill in `.claude/skills/spiega`, gli agenti in `.claude/agents`.

## Permessi
Il render (Manim, LaTeX) e il controllo delle pagine (Chrome headless) avviano programmi esterni e
scrivono cache fuori dalla repo. Se un comando fallisce per la sandbox, chiedi all'utente di approvarlo
o di avviare Codex con permessi di scrittura più ampi; non aggirare la sandbox in altri modi.

## Manutenzione
I file sorgente sono **solo** in `.claude/`. Dopo aver modificato un agente in `.claude/agents/`,
rigenera le versioni per Codex: `.venv/bin/python .claude/skills/spiega/scripts/sync_codex.py`.
