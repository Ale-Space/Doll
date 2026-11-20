# Doll

Doll è un progetto didattico per studiare matematica, fisica e altre materie di ingegneria. La skill `spiega` per Codex e Claude Code parte da un esercizio, un teorema o un concetto e prepara una spiegazione guidata. Quando il tema si presta a una rappresentazione visiva, genera anche un video con Manim. Su richiesta può produrre una dispensa LaTeX o, per esercizi e simulazioni, una pagina interattiva.

## Installazione su macOS

Con [Homebrew](https://brew.sh/) e Codex o Claude Code già installati:

```bash
git clone https://github.com/Ale-Space/Doll.git
cd Doll
./setup.sh
```

Lo script prepara Python 3.12, Manim e LaTeX e prova a renderizzare una formula. Per verificare le pagine serve anche Google Chrome. Il setup è pensato per macOS.

## 1. Come si usa

Apri la cartella clonata in Codex o Claude Code e prova uno di questi comandi.

| Strumento | Esempio |
|---|---|
| Codex | `$spiega il teorema di Schwarz` |
| Claude Code | `/spiega il teorema di Schwarz` |

La repository include [quattro scene Manim di esempio](.claude/skills/spiega/esempi), oltre a guide, script e template.

### Dipendenze per le pagine interattive

I template sono inclusi. Per assemblare una pagina offline occorre predisporre le librerie JavaScript e CSS in `.claude/skills/spiega/kit/web/lib/`. Consulta [l’elenco delle versioni](.claude/skills/spiega/kit/web/lib/VERSIONI.txt) e i [nomi dei file attesi](.claude/skills/spiega/scripts/web_build.py). KaTeX serve a tutte le pagine. Le altre librerie dipendono dal template. I bundle di terze parti vanno procurati separatamente e la clonazione da sola è sufficiente per iniziare con i video dopo il setup.

### Tre livelli di impegno (valgono per video, PDF, pagina e chat)
Lo scopo è capire **tutto**, con chiarezza, non finire presto: il video dura quanto serve.

| Livello | Come lo chiedi | Video | PDF (se lo chiedi) | Pagina (se la chiedi) | Squadra |
|---|---|---|---|---|---|
| **Veloce** | "veloce" | 20–45 s: l'idea centrale e il controesempio | 1–2 pagine | 3 passi, 1 "Prova tu" | fa tutto da solo, senza revisore |
| **Normale** | niente (è il predefinito) | 45 s – 1:30: tutti i passaggi chiave, ciascuno con il suo gesto | 3–5 pagine | 4–6 passi | esperto, costruttore, revisore (2 giri) |
| **Approfondito** | "approfondito", "impegnativo", "fatto bene", "per l'esame" | 1:30 – 3:00, a capitoli: tutta la dimostrazione, ogni ipotesi e i controesempi, riepilogo; 1080p | 6–12 pagine con dimostrazione completa e 6–8 esercizi svolti | 6–10 passi, 3 "Prova tu" | esperto, costruttore, revisore (3 giri), numeri verificati due volte |

- Vuoi anche la dispensa? Scrivi "con il PDF". Vuoi giocare con i parametri di un esercizio pratico? "fammi
  anche una pagina". Esempio: `/spiega il teorema di Schwarz approfondito con il PDF`.

## 2. Dove trovi i risultati

Nel Finder vedi **solo le materie e questo README**: gli strumenti sono nascosti (Cmd+Maiusc+. per vederli).

```
Analisi 2/
└── Capitolo 3 - Calcolo differenziale/
    └── Derivate continue e differenziabilità/
        ├── Derivate continue e differenziabilità.mp4    ← il video
        ├── Derivate continue e differenziabilità.pdf    ← la dispensa (se l'hai chiesta)
        └── progetto/                                    ← i sorgenti (scena.py, dispensa.tex, piano.md, figure/)
```
- **Materia** = il corso; **Capitolo** = `Capitolo N - Titolo` del tuo libro (o il grande argomento);
  **Argomento** = il nome del teorema o dell'esercizio. Le cartelle esistenti vengono riusate.
- Per buttare un argomento basta cancellare la sua cartella: non resta nulla in giro.
- Per modificare un video si chiede la modifica: l'agente cambia `progetto/scena.py` e rifà il render
  (non monta mai pezzi di video).

## 3. Come funziona (il percorso di una richiesta)

```
foto / PDF / testo
 1. CAPIRE        il coordinatore sceglie materia, capitolo, argomento e l'esperto giusto
 2. ESPERTO       risolve da zero, verifica ogni numero, scrive il COPIONE del video
                  (frase wow, gesto visivo, esempio concreto, tabella secondo per secondo)
                  e, se li hai chiesti, la dispensa e la specifica della pagina
 3. COSTRUTTORE   realizza il copione seguendo il manuale di stile → bozza + fotogrammi
 4. CONTROLLO     controllo_stile.py: boccia da solo i video fermi, troppo lunghi, fuori stile
 5. REVISORE      rifà i conti, guarda fotogrammi (e PDF/pagina se ci sono); al massimo 2 giri
 6. FINALE        render 720p, nuovo controllo, pubblica.py (risultati in vista, file di lavoro via)
 7. CHAT          la spiegazione, con "a 0:16 guarda…"
```

## 4. I moduli (dove sta cosa)

| Modulo | File | Cosa fa |
|---|---|---|
| Coordinatore | `.claude/skills/spiega/SKILL.md` | la procedura, le cartelle, le regole generali |
| **Guida didattica** | `guide/didattica.md` | i principi per insegnare bene, validi per piano, video, pagina, dispensa e chat |
| Esperti (9) | `.claude/agents/esperto-*.md`, `esperti/COMUNE.md` | il contenuto: metodo d'esame, errori tipici, verifica, copione, dispensa |
| Costruttori (2) | `.claude/agents/costruttore-video.md`, `costruttore-web.md` | scrivono la scena o la pagina |
| Revisore | `.claude/agents/verificatore.md` | controllo indipendente: conti, stile, dispensa |
| **Manuale dei video** | `guide/manim.md` | principi, struttura in atti, schermo, palette, ritmo, divieti, repertorio dei gesti di analisi e fisica |
| **Manuale delle pagine** | `guide/web.md` | principi, struttura, colori per ruolo, repertorio per materia, divieti delle pagine interattive |
| Esempi di riferimento | `esempi/schwarz.py`, `esempi/c1_differenziabile.py`, `esempi/teorema_zeri.py`, `esempi/pendolo_energia.py` | il livello di qualità richiesto (gli ultimi due fatti da un'altra AI con il solo manuale) |
| Template | `templates/` | video: `teorema.py` (struttura in atti), `analisi.py`, `algebra_lineare.py`, `fisica.py`, `meccanismo.py`, `circuito.py`, `quantistica.py`, `fourier.py`, `complessi.py`, `fasori.py`; 13 pagine web (con `digitale_sim.html`); 2 dispense |
| Kit | `kit/doll_kit.py`, `kit/fisica_kit.py`, `kit/circuiti_kit.py`, `kit/web/`, `kit/pdf/doll.sty` | palette e pezzi pronti (numeri dal vivo, mappe di colore, frecce fisiche, molle, pendoli, circuiti IEC con risolutore esatto e correnti che scorrono), integrazione con librerie web offline, stile PDF |
| Script | `scripts/` | `render.sh`, `frames.py`, `controllo_stile.py` (video), `controllo_pagina.py` (pagine), `pubblica.py`, `web_build.py`, `web_check.py`, `pdf_build.sh`, `figure.py`, `schema_circuito.py` (lcapy + schemdraw), `falstad_link.py`, `sync_codex.py` |
| Ponte Codex | `AGENTS.md`, `.agents/`, `.codex/agents/*.toml` | gli stessi file per ChatGPT (generati da `.claude/`) |

## 5. Come insegna (guida didattica)

Tutto segue `guide/didattica.md`, basata sui risultati più solidi della ricerca sull'apprendimento (Mayer,
Sweller, Renkl, Chi, Roediger e Karpicke, Dunlosky):

| Principio | Dove lo trovi |
|---|---|
| **Obiettivo esplicito** e prerequisiti richiamati | apertura della dispensa ("Cosa saprai fare"), prima riga della chat |
| **Prevedi → osserva → spiega** | una domanda prima della risposta: didascalia-domanda nel video, passo della guida nella pagina, riquadro "Prova a prevedere" nel PDF |
| **Dal concreto all'astratto** | prima l'esempio con numeri veri, poi la regola |
| **Un'idea alla volta** | un gesto per volta, etichette accanto agli oggetti, niente decorazioni |
| **Esempi svolti che si ritirano** | esempio svolto → esercizio da completare → esercizi liberi (base, da esame) |
| **Il perché di ogni passo** | ogni passo della soluzione ha il suo "perché" |
| **Il preconcetto smontato** | riquadro "Il preconcetto da smontare" e controesempio che si vede nel video |
| **Recupero attivo e ripasso** | "Verifica te stesso" (soluzioni in fondo), ripasso tra 2 giorni e tra una settimana, domande finali in chat |
| **Feedback immediato** | "Prova tu" nella pagina: una lettura conferma subito quando hai fatto giusto |
| **Livello e notazione del corso** | più passi per il livello base, meno per quello d'esame; la notazione dei tuoi appunti |

I controlli automatici avvisano se manca qualcosa (previsione, obiettivo, preconcetto, autoverifica, ripasso).

## 6. Lo stile dei video (uguale con qualunque AI)

- **Mostra, non scrive**: la dimostrazione si vede negli oggetti che si muovono; niente paragrafi né catene di
  formule. Da Normale in su, la formula chiave di un passaggio può comparire accanto all'oggetto, una alla volta.
- **Un gesto visivo** per ogni idea (lo zoom che schiaccia la superficie, il quadrato che collassa su un punto,
  l'angolo che cresce finché il blocco scivola) e il **controesempio con lo stesso gesto**.
- **Struttura fissa**: apertura, oggetto, meccanismo, conclusione, controesempio, risultato; nel livello
  Approfondito divisa in capitoli con un riepilogo finale. Durata secondo il livello (da 20 s a 3 min).
- **Stesso aspetto**: sfondo nero, palette semantica del kit (lo stesso colore vuol dire sempre la stessa cosa).
- **Controllo automatico** (`controllo_stile.py`): niente colori o sfondi propri, niente schede, didascalie
  brevi, durata giusta per il livello (anche troppo corta: vuol dire che manca qualche passaggio) e soprattutto **movimento** (i video-presentazione si muovono il 23–40% del tempo e
  vengono bocciati; quelli buoni il 55–65%).

## 7. Materie, strumenti e stato

Si fa **sempre il video** (niente visualizzazione solo per il calcolo puro). La **pagina interattiva** si
aggiunge solo se la chiedi e solo per gli argomenti pratici ("cosa succede se cambio X"): le pagine elencate
qui sotto valgono in quel caso.

| Materie | Esperto | Strumenti oggi | Cosa fa vedere | Stato |
|---|---|---|---|---|
| Analisi I e II, Metodi matematici | `esperto-analisi` | video Manim (manuale + esempi), JSXGraph, Plotly | teoremi con costruzione, zoom, mappe di colore, superfici, Fourier, mappe complesse | **collaudato** (Schwarz, C¹, Lagrange, teorema degli zeri) |
| Algebra lineare e geometria | `esperto-algebra` | video Manim, three.js | il piano/lo spazio che si deforma, autovettori, coniche | template pronto |
| Fisica I | `esperto-meccanica` | video Manim + `fisica_kit` (simulazione dalla Lagrangiana), pagina di simulazione | forze, piano inclinato, molle, pendoli, carrelli, energia | **collaudato** (meccanismi, energia nel pendolo) |
| Fisica II, Elettromagnetismo applicato | `esperto-elettromagnetismo` | pagine: campi 2D, onde, scena 3D | linee di campo, Gauss, onde | template pronti e controllo automatico superato; da collaudare su un esercizio |
| Elettrotecnica, Circuiti, Elettronica | `esperto-circuiti` | **video dei circuiti** (`circuiti_kit`: correnti che scorrono, potenziali a colori, Thévenin che si richiude), video dei fasori, pagina AC, Falstad (link), `schema_circuito.py` (numeri esatti e schemi europei), circuitikz nel PDF | reti in continua, Thévenin/Norton, fasori, RLC, risonanza, potenze | **collaudato** (Thévenin, sovrapposizione degli effetti) |
| Elettronica digitale, Misure | `esperto-circuiti`, `esperto-statistica` | **DigitalJS** (`digitale_sim.html`: reti logiche simulate e cliccabili), WaveDrom | contatori, registri, FSM, flip-flop, forme d'onda | **collaudato** (contatore a 2 bit) |
| Quantistica, Stato solido, Dispositivi, Nanoscienze, Nucleare | `esperto-quantistica` | **video della sfera di Bloch** (dinamica da QuTiP), pagine: Schrödinger 1D, reticoli 3D (3Dmol) | qubit, Larmor, Rabi, tunnel, buche, bande, reticoli | **collaudato** (Bloch, Rabi); pagine da collaudare |
| Laboratorio, Sistemi complessi | `esperto-statistica` | pagina statistica, matplotlib, MATLAB (se richiesto) | limite centrale, fit e χ², analisi dei tuoi dati | da collaudare |
| Chimica | `esperto-chimica` | molecole 3D (3Dmol) | VSEPR, angoli, polarità | da collaudare |
| Informatica | `esperto-informatica` | pagina algoritmi | algoritmi passo per passo con il codice evidenziato | da collaudare |

### Strumenti (ricerca del 10/11/2026)
Il kit integra lcapy, schemdraw e QuTiP. I template per circuiti logici richiedono anche il bundle DigitalJS. Da aggiungere quando serviranno:

| Materia | Strumento | Perché | Priorità |
|---|---|---|---|
| Ottica | Ray Optics Simulator | ray tracing fisico di lenti, specchi, prismi da scene JSON | alta |
| Quantistica (pacchetti 2D/3D) | qmsolve | autostati e pacchetti d'onda animati | media |
| Elettronica | ngspice + python-control | curve dei dispositivi, Bode e Nyquist da modelli reali | media |
| Fisica II / EM | scikit-fem, scikit-rf | campi calcolati su geometrie vere, carta di Smith | media |
| Stato solido | ASE + seekpath | reticoli e zona di Brillouin corretti (poi 3Dmol) | media |
| Fisica I (urti, più corpi) | Planck.js / pymunk | contatti e vincoli robusti | media-bassa |

## 8. Limiti onesti
- Falstad e gli applet esterni richiedono internet. Le pagine assemblate con le librerie locali funzionano offline.
- Niente render fotorealistici (Blender non c'è): il 3D è Manim o three.js.
- Argomenti senza niente da vedere (nomenclatura, sintassi del C, stechiometria pura): solo chat (e dispensa se la chiedi).
- Le pagine interattive vanno ancora migliorate: per ora solo su richiesta e solo per esercizi pratici.
- Nessuna AI è perfetta: il manuale e il controllo riducono molto gli errori, il revisore ne trova altri,
  ma un video va sempre guardato.

## 9. Manutenzione
- Si modificano **solo** i file in `.claude/`. Dopo aver cambiato un agente:
  `.venv/bin/python .claude/skills/spiega/scripts/sync_codex.py` (rigenera `.codex/` e `.agents/`).
- Se un video viene male, non si corregge solo quel video: si migliora il manuale, il kit o il controllo,
  così l'errore non si ripete.
- Installazione su un altro Mac: `./setup.sh` (Python 3.12, LaTeX, Manim, Playwright; serve Google Chrome).

## Licenza

Il codice di Doll è pubblicato senza una licenza di riuso esplicita. Le librerie esterne sono soggette alle rispettive licenze.
