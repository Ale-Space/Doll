---
name: spiega
description: Spiega VISIVAMENTE qualsiasi esercizio, teorema o concetto della triennale di Ingegneria Fisica (analisi, algebra lineare, fisica, elettromagnetismo, elettrotecnica, elettronica, quantistica, stato solido, chimica, informatica, laboratorio...) con un video Manim e la spiegazione in chat; su richiesta anche una dispensa PDF che insegna come si risolve e perché, e (solo per argomenti pratici) una pagina interattiva. Accetta foto, PDF o testo ("spiegami il teorema di Rolle"). Usala quando l'utente chiede di capire, visualizzare o farsi spiegare un esercizio, un teorema o un concetto, o quando scrive /spiega o $spiega.
---

# Spiega: video + spiegazione in chat (PDF e pagina su richiesta)

Funziona con **Claude Code** e con **Codex** (ChatGPT). Percorsi relativi alla root della repo.
`SK=.claude/skills/spiega` · Python: `.venv/bin/python`. `$SK` e `$P` sono segnaposto: nei comandi scrivi i
percorsi veri (tra virgolette).

## Cosa consegni
**Di base: il video e la spiegazione in chat.** Il PDF e la pagina interattiva si fanno **solo se l'utente li
chiede** in questa richiesta.

| | Quando | Cosa |
|---|---|---|
| **Video** | sempre (è la base) | video Manim senza voce che fa vedere *perché*; dura quanto serve per capire tutto, secondo il livello di impegno (da 20 s a 3 min, vedi sotto). Unica eccezione: esercizi di solo calcolo senza niente da vedere (`Mezzo scelto: nessuno`): allora solo chat, e offri il PDF. |
| **Chat** | sempre | la spiegazione breve, con il collegamento ai momenti del video e i percorsi dei file. |
| **Dispensa PDF** | solo se richiesta ("con il PDF", "fammi la dispensa", "anche il PDF") | come si risolve *per bene*: metodo generale, soluzione passo per passo con i perché, errori tipici, esercizi per allenarsi con soluzione. Per un teorema: enunciato, ipotesi e controesempi, intuizione, dimostrazione, esempio, uso negli esercizi. |
| **Pagina interattiva** | solo se richiesta esplicitamente ("fammi una pagina", "fammi giocare con i parametri") **e** solo per argomenti pratici | HTML offline da esplorare: esercizi con parametri, circuiti, simulazioni, dati di laboratorio, algoritmi. **Mai per teoremi, dimostrazioni o concetti teorici**: se l'utente la chiede per uno di questi, digli che per la teoria si fa il video e chiedi se vuole comunque la pagina. La pagina si aggiunge al video, non lo sostituisce. |

Annota al punto 1 cosa ha chiesto (`PDF: sì/no`, `pagina: sì/no`) e passalo all'esperto. Non aggiungere PDF o pagina
di tua iniziativa: al massimo, a fine risposta, offrili in una riga.

## Livelli di impegno (valgono per video, PDF, pagina e chat)
**Regola di serietà, per tutti i livelli.** Lo scopo è che l'utente capisca *tutto*, con chiarezza e senza
errori, non finire presto. Il video dura quanto serve, entro i limiti del livello; non si taglia un passaggio
per accorciare: se serve a capire, si mostra. Ogni idea del ragionamento ha il suo momento nel video, con il suo
gesto visivo e il tempo per guardarlo. Tra "più corto" e "più chiaro" vince sempre "più chiaro". Restano
valide tutte le regole di sempre: numeri verificati, stile e colori del kit, movimento (mai slide ferme),
controesempio, domanda di previsione, mai montare video.

**Come si sceglie** (al punto 1 della procedura):
| Livello | Parole dell'utente | Uso tipico |
|---|---|---|
| **Veloce** | "veloce", "al volo", "rapido" | ripasso, domanda al volo |
| **Normale** (predefinito) | nessuna indicazione | quasi tutto |
| **Approfondito** | "approfondito", "impegnativo", "fatto bene", "per bene", "dettagliato", "completo" | teoremi lunghi, dimostrazioni, argomenti difficili |

"Per l'esame" / "da esame" indica il **livello di spiegazione** (base | da esame, vedi `esperti/COMUNE.md`): è
un'altra cosa. Se però l'utente non ha detto niente sull'impegno, "per l'esame" vale anche come impegno
Approfondito. Nel dubbio vale Normale. Il livello va scritto in `piano.md` come `**Impegno**: normale` (o
`veloce`, `approfondito`): lo leggono gli agenti, `controllo_stile.py` (durate e didascalie) e `render.sh`
(risoluzione del finale).

| | Veloce | Normale | Approfondito |
|---|---|---|---|
| **Video: durata** | 20–45 s | 45 s – 1:30 | 1:30 – 3:00 |
| **Video: contenuto** | l'idea centrale: un gesto + il controesempio | tutti i passaggi chiave, ciascuno con il suo gesto, + il controesempio | tutta la dimostrazione o la soluzione, passo per passo: ogni ipotesi è un oggetto, un controesempio per ogni ipotesi importante, riepilogo finale |
| **Video: struttura** | gli atti di `guide/manim.md` §3 | gli atti, con il meccanismo diviso in 3–6 passi | a **capitoli** (l'oggetto, un capitolo per passo, controesempi, riepilogo), nome del capitolo piccolo in alto a sinistra |
| **Video: testo** | didascalie ≤ 8 parole | didascalie ≤ 10 parole; la formula chiave accanto all'oggetto quando è il punto | didascalie ≤ 12 parole; la formula del passaggio accanto all'oggetto che la fa vedere, una per volta; mai paragrafi |
| **Video: render finale** | 720p | 720p | 1080p (automatico) |
| **PDF** (se richiesto) | 1–2 pagine: idea, metodo, risultato, 2 esercizi | 3–5 pagine: struttura completa di `esperti/COMUNE.md` | 6–12 pagine: dimostrazione completa con tutti i perché, ogni ipotesi con il suo controesempio, più esempi svolti, collegamenti con altri teoremi, 6–8 esercizi dal facile al tipo d'esame con soluzione svolta, un fotogramma per capitolo |
| **Pagina** (se richiesta, solo pratica) | 3 passi della guida, 1 "Prova tu" | 4–6 passi, 1–2 "Prova tu" | 6–10 passi anche con più viste collegate, 3 "Prova tu" di difficoltà crescente |
| **Squadra** | fai tutto tu, senza subagenti | esperto → costruttore → verificatore | esperto → costruttore → verificatore |
| **Copione** | essenziale (vedi sotto) | completo | completo, e l'esperto lo ricontrolla prima di consegnarlo: ogni passaggio della dimostrazione ha il suo momento nel video? |
| **Verifica dei numeri** | SymPy/SciPy | SymPy/SciPy | due metodi indipendenti per ogni risultato chiave |
| **Fotogrammi da guardare** | 12 | 18 | uno ogni 5 s (≈ 20–36) |
| **Giri del verificatore** | nessuno | fino a 2 | fino a 3 |
| **Chat** | 5–8 righe: idea, risultato, "nel video guarda…" | struttura completa del §7 | struttura completa + indice dei capitoli del video con i minuti ("1:10 → secondo Lagrange") |
| **Controllo automatico** | `OK` obbligatorio | `OK` obbligatorio | `OK` obbligatorio |

## Dove vanno i file
Nel Finder la repo mostra solo le materie: gli strumenti (`.claude/`, `.venv/`, `README.md`, ...) sono nascosti.
Ogni argomento ha la sua cartella:
```
Analisi 2/
└── Capitolo 3 - Calcolo differenziale/
    └── Teorema di Schwarz/
        ├── Teorema di Schwarz.mp4     # il video
        ├── Teorema di Schwarz.pdf     # la dispensa (se richiesta)
        ├── Teorema di Schwarz.html    # la pagina interattiva (se richiesta)
        └── progetto/                  # i sorgenti: scena.py, pagina.html, dispensa.tex, piano.md, figure/, input
```
- **Materia**: il nome del corso Polito, scritto così (crea la cartella se non c'è): 1° anno `Analisi 1`,
  `Chimica`, `Informatica`, `Algebra lineare e geometria`, `Fisica 1`, `Laboratorio di fisica`; 2° anno
  `Analisi 2`, `Fisica 2`, `Elettrotecnica`, `Dispositivi elettronici`, `Metodi avanzati e fisica quantistica`,
  `Circuiti elettronici`, `Metodi matematici`; 3° anno `Elettromagnetismo applicato`, `Fisica dello stato solido`,
  `Elettronica applicata`, `Fisica dei sistemi complessi`, `Fisica e materiali per tecnologie avanzate`,
  `Fisica nucleare`, `Elettronica dei sistemi digitali`, `Misure`, `Nanoscienze`.
- **Capitolo**: `Capitolo N - Titolo` se il materiale dell'utente indica il capitolo (es. "Teorema 3.1.21" e
  intestazione "3 Calcolo differenziale" → `Capitolo 3 - Calcolo differenziale`); altrimenti il nome del grande
  argomento (es. `Integrali multipli`). **Prima guarda con `ls` le cartelle che esistono e riusale**: niente
  doppioni con nomi diversi. Nel dubbio sul capitolo, chiedi.
- **Argomento**: nome leggibile in italiano (`Teorema di Schwarz`, `Circuito RLC serie`). Se la cartella
  esiste già, è una revisione: lavora nel suo `progetto/`.
- In questa guida **`$P`** è la cartella `progetto/` dell'argomento. **I nomi contengono spazi: scrivi sempre
  i percorsi tra virgolette** (`"$P/scena.py"`).
- Durante il lavoro tutto sta in `$P`. Alla fine `pubblica.py` porta fuori solo video, dispensa e pagina, con il
  nome dell'argomento, e cancella bozze, fotogrammi e anteprime.
- Nella root della repo non creare file o cartelle che non siano materie.

## Squadra
Gli agenti sono in `.claude/agents/*.md` (per Codex anche in `.codex/agents/*.toml`, con il trattino
basso al posto del trattino: `esperto_analisi`).
- **Esperti** (contenuto didattico, soluzione verificata, scelta del mezzo, dispensa):
  | Argomento | Esperto |
  |---|---|
  | Analisi I e II, Metodi matematici (complessi, Fourier, Laplace, EDO) | `esperto-analisi` |
  | Algebra lineare e geometria | `esperto-algebra` |
  | Fisica I, termodinamica, meccanica lagrangiana/hamiltoniana | `esperto-meccanica` |
  | Fisica II, ottica, Elettromagnetismo applicato | `esperto-elettromagnetismo` |
  | Elettrotecnica, Circuiti elettronici, Elettronica applicata, Elettronica digitale | `esperto-circuiti` |
  | Quantistica, Stato solido, Dispositivi (fisica), Nanoscienze, Materiali, Fisica nucleare | `esperto-quantistica` |
  | Laboratorio di fisica, Misure, Sistemi complessi | `esperto-statistica` |
  | Chimica | `esperto-chimica` |
  | Informatica (C) | `esperto-informatica` |
- **Costruttori**: `costruttore-video` (Manim), `costruttore-web` (pagina interattiva).
- **Revisore**: `verificatore`.

**Come si lanciano.** Claude Code: strumento Agent con `subagent_type` = nome dell'agente. Codex: avvia
l'agente personalizzato con quel nome (`esperto_analisi`, ...) e aspetta il suo risultato. **Se i
subagenti non sono disponibili** (o il tipo non esiste): leggi il file `.claude/agents/<nome>.md` e fai
tu quel ruolo, in sequenza. Passa sempre a ogni agente solo i percorsi e la richiesta, non le tue conclusioni.

**Livello Veloce**: fai tutto tu senza subagenti e salta il verificatore. La cartella, il manuale,
`controllo_stile.py` e `pubblica.py` restano obbligatori. In `piano.md` bastano Tipo/Impegno, Testo,
Soluzione verificata, Mezzo scelto e Specifica della visualizzazione (per un video: il copione completo);
metodo, errori tipici ed esercizi si possono omettere.

## Procedura

### 1. Capisci la richiesta
- Scegli materia, capitolo e argomento (vedi «Dove vanno i file») e crea `$P` con `mkdir -p`.
- **Foto**: guardala. **PDF**: `.venv/bin/python $SK/scripts/pdf_pagine.py <file.pdf> "$P/pagine"` e
  guarda le pagine. Salva in `$P/` una copia dell'input.
- Più esercizi nella foto → chiedi quale (uno per volta). Dati illeggibili → chiedi.
- Scegli l'esperto dalla tabella (argomento a cavallo di due corsi: quello del corso indicato
  dall'utente, altrimenti quello del concetto principale).
- Annota le preferenze dell'utente: **impegno** (veloce | normale | approfondito, vedi «Livelli di impegno»;
  di base normale), **PDF sì/no** e **pagina sì/no** (di base no e no, vedi «Cosa consegni»), lingua del testo
  a schermo (default: italiano), livello di spiegazione (base / da esame), se vuole il codice MATLAB.

### 2. Esperto → `piano.md` (+ `dispensa.tex` se il PDF è richiesto)
Lancia l'esperto con: la richiesta dell'utente (testuale, più i percorsi delle immagini), il percorso
completo di `$P`, le preferenze del punto 1, scritte esplicitamente così:
`Impegno: normale · PDF: no · pagina: no · Livello: da esame · Lingua: italiano`. Se `piano.md` comincia con
`DOMANDA:`, fai la domanda all'utente e fermati. Controlla che `piano.md` riporti `**Impegno**:` uguale a
quello che hai passato e che il copione abbia la durata del livello: se no, rimandalo all'esperto.

### 3. Costruttore → visualizzazione
In base a "Mezzo scelto" in `piano.md`:
- `video` → `costruttore-video`; `video+web` (solo se l'utente ha chiesto la pagina) → `costruttore-video` e
  `costruttore-web` **in parallelo**;
- `nessuno` → salta al punto 4.
- Se `piano.md` dice `web` o `video+web` ma l'utente non ha chiesto la pagina, è un errore dell'esperto:
  correggi in `video` e fai solo il video.
- Passa al costruttore il percorso di `$P` e l'impegno (lo legge anche da `piano.md`).
- Video: prima di andare avanti `.venv/bin/python $SK/scripts/controllo_stile.py "$P"` deve dire `OK` (misura
  `finale.mp4` se c'è, altrimenti `bozza.mp4`, con i limiti del livello scritto in `piano.md`)
  (se no, rimanda al costruttore con l'elenco degli errori).
- Pagina: allo stesso modo `.venv/bin/python $SK/scripts/controllo_pagina.py "$P"` deve dire `OK`.

### 4. Figure e PDF (solo se il PDF è richiesto; altrimenti salta al punto 5)
- Fotogrammi per la dispensa (nomi `f1.png`, `f2.png`, ... come li cita `dispensa.tex`):
  - video: `.venv/bin/python $SK/scripts/figure.py video "$P/bozza.mp4" <t1,t2,t3> "$P/figure"`
    (i timestamp dei momenti chiave li dà il costruttore);
  - web: `.venv/bin/python $SK/scripts/figure.py web "$P/interattivo.html" "$P/figure"`.
- **Abbina figure e didascalie**: `figure.py` stampa, per ogni `fN.png`, il momento o il passo della guida
  che contiene. L'esperto ha scritto `dispensa.tex` prima che la visualizzazione esistesse: controlla
  ogni `\dollfotogrammi`/`\dollfigura` e correggi i nomi dei file (o le didascalie) finché ogni
  immagine mostra quello che dice la sua didascalia. Allinea anche i tempi in `\momento{m:ss}` a quelli
  dati dal costruttore.
- Compila: `$SK/scripts/pdf_build.sh "$P"` → `dispensa.pdf` e `dispensa_pagine.png`.
  Se fallisce, leggi l'errore, correggi `dispensa.tex`, ricompila.

### 5. Verifica indipendente (non nel livello Veloce)
Lancia `verificatore` con il percorso completo di `$P` e l'impegno.
- `DA_CORREGGERE`: applica le correzioni (tu, o rimandandole al costruttore/esperto che ha fatto quel
  pezzo), rifai bozza/pagina/PDF, verifica di nuovo. Al massimo **2 giri** (Normale) o **3 giri** (Approfondito).
- `OK` con problemi minori: correggi subito quelli veloci, senza un altro giro.

### 6. Finale
- Video: `$SK/scripts/render.sh "$P/scena.py" finale` (con impegno Approfondito fa da solo il 1080p),
  `controllo_stile.py "$P"` (deve dire `OK`), poi `.venv/bin/python $SK/scripts/frames.py "$P/finale.mp4" 12`
  e guarda tutti i fogli `finale_frames*.png` (Approfondito: `frames.py "$P/finale.mp4" auto`, uno ogni 5 s).
  Se hai cambiato la scena dopo l'estrazione delle figure, rigenera le figure dal finale e ricompila il PDF.
- **Pubblica**: `.venv/bin/python $SK/scripts/pubblica.py "$P"`. Sposta `finale.mp4`, `dispensa.pdf` e
  `interattivo.html` (quelli che esistono: senza PDF esce solo il video) nella cartella dell'argomento con il suo nome, cancella i file di lavoro e stampa i
  percorsi dei risultati.
- Apri i risultati con `open` sui percorsi stampati.

### 7. Risposta in chat (nella lingua dell'utente)
Lunghezza secondo l'impegno: **Veloce** 5–8 righe (idea, risultato, "nel video guarda…", file); **Normale** la
struttura qui sotto; **Approfondito** la struttura qui sotto più l'**indice dei capitoli del video** con i
minuti ("0:00 l'oggetto · 0:25 primo Lagrange · 1:10 secondo Lagrange · …"), presi dai tempi del finale.
Segue `$SK/guide/didattica.md`: l'idea prima dei passaggi, i dettagli nel PDF se c'è. Senza PDF, le
soluzioni delle domande di verifica le dai solo se l'utente le chiede (così resta il recupero attivo); chiudi
offrendo in una riga la dispensa PDF.
**Esercizio**: 0. Obiettivo in una riga ("Qui impari a…") · 1. Esercizio (in breve) · 2. Idea chiave · 3. Soluzione
passo per passo, ogni passo con il suo perché (sintetica: i dettagli sono nel PDF) · 4. Risultato · 5. Il
preconcetto da evitare, in una riga · 6. Nella visualizzazione: "a ~10 s guarda..." / "passo 3 della guida: ..."
· 7. **Verifica te stesso**: 2–3 domande brevi, senza risposta (le soluzioni sono nel PDF) · 8. File.
**Teorema o concetto**: 0. Obiettivo · 1. Enunciato con ipotesi · 2. Idea intuitiva · 3. Perché servono le ipotesi
(controesempi in una riga) e il preconcetto da smontare · 4. Idea della dimostrazione · 5. Come si usa negli
esercizi · 6. Nella visualizzazione · 7. **Verifica te stesso** (2–3 domande) e il ripasso consigliato (tra 2
giorni e tra una settimana) · 8. File.

## Regole generali
- **Didattica**: `$SK/guide/didattica.md` vale per tutto (piano, video, pagina, dispensa, chat).
- **Nessun numero non verificato** (SymPy, SciPy o calcolo numerico indipendente), né nella
  visualizzazione né nella dispensa né in chat.
- La visualizzazione **mostra**, non spiega: niente catene di passaggi algebrici né paragrafi a schermo.
  Dal livello Normale in su una formula chiave può comparire accanto all'oggetto che la fa vedere (una per
  volta, vedi `guide/manim.md` §7); le derivazioni complete stanno nella dispensa e in chat.
- **Serietà**: qualunque sia il livello, il lavoro deve essere corretto, chiaro e completo per quel livello;
  non si accorcia per fare prima (vedi «Livelli di impegno»).
- Testo a schermo nella lingua scelta (default italiano); in `MathTex` niente lettere accentate.
- **Video**: il manuale `$SK/guide/manim.md` è vincolante per chiunque scriva la scena (Claude, Codex o altri);
  esempi di riferimento in `$SK/esempi/`. `controllo_stile.py` deve dire `OK` sulla bozza e sul finale.
- **Mai montare video** (tagliare, concatenare, incollare mp4) e mai lavorare fuori da `$P`: per cambiare un
  video si modifica `scena.py` e si rifà il render completo.
- **Pagine**: il manuale `$SK/guide/web.md` è vincolante; `controllo_pagina.py` deve dire `OK`.
- Guide: `$SK/guide/manim.md`, `$SK/guide/web.md`; regole del contenuto: `$SK/esperti/COMUNE.md`.
- Strumenti installati: Manim + LaTeX, SymPy/SciPy/NumPy/matplotlib, Chrome headless (Playwright),
  TeX Live completo (circuitikz, pgfplots), MATLAB R2026a (solo se serve o se richiesto).
