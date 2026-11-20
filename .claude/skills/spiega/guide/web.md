# Manuale delle pagine interattive Doll (HTML)

**Leggilo tutto prima di scrivere una pagina.** Vale per qualunque AI (Claude, ChatGPT/Codex, altre). Le regole
sono controllate da `scripts/controllo_pagina.py` e dal verificatore: una pagina che non passa si rifà.

**Quando si fa**: solo se l'utente la chiede, e solo per argomenti **pratici** (esercizi con parametri, circuiti,
simulazioni, dati di laboratorio, algoritmi). Mai per teoremi, dimostrazioni o concetti teorici: lì si fa il
video. La pagina si aggiunge al video, non lo sostituisce (vedi SKILL.md, «Cosa consegni»).

Una pagina è un file HTML **autosufficiente** (offline, si apre con doppio clic) con cui lo studente *gioca*:
slider, punti da trascinare, simulazioni in tempo reale, e un **percorso guidato** (`Doll.guida`) di 3–10 passi
secondo l'impegno (vedi «Livelli di impegno» qui sotto)
che racconta l'idea come farebbe il video. Template pronti in `templates/web/` (12 + il simulatore Falstad).

## 1. Lo scopo
Come per i video: alla fine chi la usa deve poter dire **perché** la cosa è vera, avendolo visto succedere
*e avendolo provato lui*. In `piano.md` l'esperto scrive:
- **Frase wow**: cosa capirà ("cambiando R la risonanza non si sposta, si allarga solo il picco");
- **Gesto / esplorazione**: cosa si muove nella vista e cosa deve provare lo studente (quale slider, quale
  trascinamento, cosa osservare);
- i **passi della guida** (quanti ne chiede il livello di impegno), ciascuno con didascalia ≤ 12 parole e lo
  stato completo che imposta;
- i valori iniziali (= i dati dell'esercizio) e gli intervalli dei controlli.

Vale anche `guide/didattica.md`. Nella pagina si traduce così:
- la guida segue **prevedi → osserva → spiega**: almeno un passo pone la domanda ("Prima di muovere R: la
  risonanza si sposta?") e il passo dopo mostra la risposta;
- l'ultimo passo è **"Prova tu"**: un compito preciso (portare una grandezza a un bersaglio, trovare un valore)
  con una lettura che conferma subito quando è raggiunto (✓), cioè feedback immediato: usa
  `const b = Doll.bersaglio(pannello, {testo, verifica: () => ..., ok})`, `b.mostra(true)` solo in quel passo
  e `b.mostra(false)` negli altri;
- etichette accanto agli oggetti, un'idea per passo, colori per ruolo uguali a video e dispensa.

### Livelli di impegno (da `**Impegno**:` in `piano.md`, SKILL.md «Livelli di impegno»)
| | Veloce | Normale | Approfondito |
|---|---|---|---|
| Passi della guida | 3 | 4–6 | 6–10 |
| Viste | una | una, o due collegate | anche più viste collegate (l'oggetto + un grafico che si traccia + …) |
| "Prova tu" | 1 compito | 1–2 compiti | 3 compiti di difficoltà crescente, ciascuno con il suo ✓ |
| Casi | il caso dell'esercizio | + il caso limite o il controesempio | + tutti i casi notevoli (limiti, controesempi, regimi diversi), ognuno uno stato della pagina |
Le regole di qualità del §2 valgono **identiche** in tutti i livelli: Veloce vuol dire meno passi, non una
pagina più povera. Regola di serietà: la pagina deve far capire *tutto* quello che il livello promette.

## 2. Principi (obbligatori)
1. **La vista fa vedere, il pannello fa provare.** Nella vista (`#vista`) il disegno vivo; nel pannello
   (`#pannello`) i controlli e le letture numeriche. Niente paragrafi né dimostrazioni scritte nella vista.
2. **Ogni passo della guida cambia la vista.** Un passo che cambia solo la didascalia è una slide (vietato):
   ogni passo imposta parametri, evidenzia un oggetto, avvia o ferma un'animazione.
3. **Un'idea per passo**, nell'ordine degli atti dei video: l'oggetto, il meccanismo, la conclusione, il
   controesempio (o il caso limite), cosa provare da soli.
4. **Esempio concreto e numeri veri**: valori verificati in `piano.md`, unità nelle letture.
5. **Il controesempio è uno stato della pagina**: lo stesso disegno con un'ipotesi tolta (uno slider o una
   scelta che la toglie), così si vede dove si rompe.
6. **Fisica vera**: simulazioni dalle equazioni del moto con integratori stabili, non animazioni "a occhio".
7. **Il disegno riempie la vista.** L'oggetto principale occupa almeno il 70% della larghezza o dell'altezza
   di `#vista`. Vietati due diagrammini in mezzo al bianco. Se servono due viste collegate (l'oggetto e un
   grafico), ognuna occupa metà della vista, a tutta altezza, con assi e caratteri leggibili.
8. **Si vede l'oggetto vero, non solo lo schema.** La funzione, il circuito, il corpo, il campo devono essere
   disegnati davvero, con i numeri veri: la curva, la superficie o la mappa di colore della funzione, il
   circuito con le correnti, il blocco sul piano. Lo schema (frecce, segni, segmenti) si **sovrappone**
   all'oggetto, non lo sostituisce. Un quadrato con quattro segni e due frecce non insegna niente.
9. **Manipolazione diretta.** Il gesto principale si fa **con il mouse sulla vista**: trascini il punto, il
   vertice, la carica, il cursore sul grafico, e tutto il resto segue in tempo reale. Gli slider del
   pannello servono solo per i parametri secondari. Per le scelte discrete (caso regolare o controesempio)
   usa bottoni a schede ben visibili, non menu a tendina. Il cursore cambia (`grab`) sopra ciò che si trascina.
10. **Si muove.** Ogni cambio di stato è animato (300–600 ms, con interpolazione: l'oggetto *va* nella nuova
    posizione, i numeri scorrono). C'è almeno un'animazione con Play che mostra il fenomeno da sola (il
    parametro che scende verso il limite, la simulazione che evolve). Una pagina dove nulla si muove senza
    clic è una slide.
11. **Il fenomeno lascia una traccia.** Se l'idea è un andamento (converge, cresce, oscilla, si sposta), mentre
    il parametro cambia si disegna la sua storia: la curva dell'errore in funzione di δ che si traccia,
    la traiettoria che resta, i valori passati sbiaditi. Un numero che cambia in una tabella non fa vedere
    una convergenza.
12. **La lettura chiave sta nella vista, grande.** Il numero che conta (R, la corrente, l'energia) è scritto
    accanto all'oggetto, ad almeno 24 px, nel colore del suo ruolo. Il pannello ha al massimo 4 letture,
    ciascuna con l'unità; niente righe piene di "?". Le differenze si mostrano come lunghezze o barre
    colorate (la distanza tra R e il valore limite è un segmento che si accorcia), non come numeri sparsi.
13. **Prevedere è un'azione.** Il passo di previsione offre 2–3 bottoni di risposta ("sì", "no", "dipende");
    la scelta viene ricordata e il passo dopo dice subito se era giusta, accanto alla risposta che si vede.
14. **Leggibile e curata.** Etichette nella vista ≥ 14 px, nessuna sovrapposizione, niente titoletti dentro la
    vista ("Il quadrato [0, δ]²"): le etichette nominano gli oggetti, accanto a loro. Ombre, gradienti e
    decorazioni no; spazi regolari e allineati sì. Deve funzionare anche sul telefono.

### Pagina bocciata: un esempio da non ripetere
La prima pagina di Schwarz (2026-11-10) aveva tutti i difetti di sopra: il quadrato e una retta numerica
piccoli in mezzo al bianco; la funzione mai disegnata; tutto si comandava da menu a tendina e slider, senza
toccare la vista; nessuna animazione; il passo di previsione era un testo con `R = ?`; le letture erano una
tabella di numeri e di "?"; la convergenza (R che si avvicina alle miste) era un punto su una retta invece di
una curva che si disegna. Passava `controllo_pagina.py` ma era brutta e non insegnava: **il controllo
automatico non basta**, conta l'autovalutazione del §8.

### Il livello a cui puntare
Le "explorable explanations": una figura grande e viva che si tocca, il testo ridotto a una riga, il
fenomeno che si vede succedere sotto la mano. Riferimenti da cui prendere spunto (senza copiarne il codice o
l'aspetto): gli articoli interattivi di Red Blob Games, le spiegazioni di Bret Victor e Nicky Case,
gli articoli di Distill, le simulazioni PhET. Prima di scrivere il codice chiediti: *se tolgo tutto il
testo, chi trascina la cosa capisce lo stesso?*

## 3. Struttura della pagina
```html
<head> ... <!-- doll:lib jsxgraph plotly three wavedrom 3dmol --> </head>   (solo quelle che servono; KaTeX è sempre incluso)
<header class="doll-top"><h1>Titolo</h1><div class="doll-dati">$formula$</div></header>
<main class="doll-main">
  <section class="doll-vista" id="vista"> ... </section>     ← il disegno
  <aside class="doll-pannello" id="pannello"></aside>        ← controlli e letture
</main>
<footer class="doll-didascalia" id="didascalia"></footer>    ← didascalia + navigazione della guida
<script> ... Doll.guida([...]); Doll.pronto(); </script>
```
API in `kit/web/doll.js` (leggi il commento in testa): `Doll.slider`, `scelta`, `bottone`, `interruttore`,
`lettura`, `bersaglio` (il "Prova tu" con ✓), `titoletto`, `didascalia`, `animazione` (Play/Pausa), `guida`, `stati`, `canvas`, `pronto`,
`col` (palette), `ruolo` (colori per ruolo).

## 4. Colori e testo
- Tema chiaro del kit (`doll.css`), uguale in tutte le pagine.
- Colori **per ruolo**, con lo stesso significato dei video: `Doll.ruolo.oggetto`, `.x`, `.y`, `.errore`, `.rif`
  (riferimento, valore limite), `.contro` (controesempio), `.forza`, `.peso`, `.velocita`, `.accelerazione`,
  `.campo`, `.energiaK`, `.energiaU`, `.corpo`, `.tenue`; altrimenti `Doll.col`. Non inventare colori.
- Titolo 2–5 parole; didascalie ≤ 12 parole; formule tra `$...$` (KaTeX). Nelle stringhe di didascalie, guida e
  letture (vanno in innerHTML) scrivi `\lt` e `\gt` invece di `<` e `>`.
- Lingua di `piano.md` (di solito italiano).

## 5. Librerie (tutte in locale, niente CDN, niente fetch)
| Nome nel marcatore | Per cosa |
|---|---|
| `jsxgraph` | geometria e grafici 2D con punti trascinabili, slider, curve dipendenti (analisi, geometria, circuiti 2D) |
| `plotly` | grafici scientifici, superfici e curve di livello 3D, istogrammi, grafici che si aggiornano |
| `three` | scene 3D libere (`THREE`, `THREE.OrbitControls`, `THREE.CSS2DRenderer` per le etichette) |
| `wavedrom` | diagrammi temporali digitali |
| `3dmol` | molecole e reticoli 3D |
| `digitaljs` | circuiti logici simulati e interattivi (vedi `templates/web/digitale_sim.html`, se presente) |
| canvas 2D (nessuna libreria) | simulazioni veloci: campi, onde, quantistica, particelle |

## 6. Repertorio per materia
| Materia / idea | Pagina |
|---|---|
| funzioni, limiti, derivate, Taylor, serie | `grafico_2d.html`: punto trascinabile, tangente o polinomio che segue, slider su n o ε |
| funzioni di 2 variabili, curve di livello, gradiente | `superficie_3d.html` (Plotly) |
| campi elettrici, cariche, potenziale, Gauss | `campo_2d.html`: cariche trascinabili, linee di campo, flusso |
| onde, interferenza, battimenti, linee di trasmissione | `onde_1d.html` |
| meccanica: molle, pendoli, urti, orbite | `simulazione_meccanica.html` (RK4), energia letta dal vivo |
| corpo rigido, vettori in 3D, onde EM | `scena_3d.html` (three.js) |
| circuiti in alternata, fasori, risonanza, potenze | `circuito_ac.html`; circuiti grandi o attivi: link Falstad (`circuito_falstad.md`) |
| elettronica digitale | `digitale.html` (WaveDrom), `digitale_sim.html` (DigitalJS, se presente) |
| quantistica 1D: buche, tunnel, pacchetti | `quantistica_1d.html` (Crank-Nicolson) |
| laboratorio, statistica, fit, limite centrale | `statistica.html` |
| chimica: molecole, VSEPR, reticoli | `molecola.html` (3Dmol) |
| informatica: algoritmi passo per passo | `algoritmo.html` (codice evidenziato e stato delle variabili) |

## 7. Vietato (motivi di rifacimento)
- **Pagina-presentazione**: passi della guida che cambiano solo il testo; vista statica; paragrafi o
  dimostrazioni scritti nella vista.
- **Pagina vuota o piccola**: disegno che occupa meno di metà della vista; diagrammi astratti senza l'oggetto
  vero; tutto comandato da menu e slider senza poter toccare la vista; nessuna animazione (§2, punti 7–12).
- Fare la pagina al posto del video, senza che l'utente l'abbia chiesta, o per un teorema o un concetto teorico.
- Risorse da internet (CDN, immagini remote, `fetch`): tutto deve stare nel file. Unica eccezione: il link al
  simulatore Falstad, come bottone "Apri nel simulatore".
- Simulazioni instabili o non fisiche (energia che cresce da sola, passo d'integrazione troppo grande).
- Numeri non presenti nella soluzione verificata.
- Lavorare fuori dalla cartella `progetto/` dell'argomento.

## 8. Procedura
1. Leggi `piano.md`, questo manuale, il template indicato (commento in testa) e `kit/web/doll.js`.
2. Copia il template in `"$P/pagina.html"` e adattalo.
3. Build e controlli:
   ```bash
   .venv/bin/python .claude/skills/spiega/scripts/web_build.py "$P/pagina.html"
   .venv/bin/python .claude/skills/spiega/scripts/web_check.py "$P/interattivo.html"
   .venv/bin/python .claude/skills/spiega/scripts/web_check.py "$P/interattivo.html" --mobile
   .venv/bin/python .claude/skills/spiega/scripts/controllo_pagina.py "$P"
   ```
   `web_check.py` deve dare `"errori": []` e produce `interattivo_frames.png` (uno scatto per passo): guardalo.
   `controllo_pagina.py` deve dire `OK`.
4. **Autovalutazione** (obbligatoria, sugli scatti di `interattivo_frames.png`). Rispondi per iscritto, sì o no,
   nella risposta finale:
   - In ogni scatto il disegno occupa la maggior parte della vista, e c'è più disegno che bianco?
   - Si vede l'oggetto vero (curva, superficie, circuito, corpo), con lo schema sopra?
   - Il gesto principale si fa trascinando nella vista? Che cosa si trascina?
   - Cosa si muove da solo (Play, transizioni)? Il fenomeno lascia una traccia?
   - La lettura chiave è grande e accanto all'oggetto?
   - Tolto il testo, la pagina fa ancora capire l'idea?
   - La metteresti accanto agli esempi del «livello a cui puntare» senza vergognarti?
   Anche un solo "no" vuol dire rifare quella parte prima di consegnare.
5. Consegna: `"$P/interattivo.html"`; alla fine `pubblica.py` la porta nella cartella dell'argomento.

## 9. Regole tecniche
- Slider: `s.set(v, true)` sposta lo slider senza richiamare `onInput` (utile quando un altro controllo lo aggiorna).
- Ogni passo della guida imposta lo stato **completo** (non dipende dal passo prima): così il controllo
  fotografa ogni passo correttamente.
- Simulazioni: RK4 o Crank-Nicolson, fluide a 60 fps, griglie modeste.
- Gestisci il ridimensionamento (`ResizeObserver` è già in `Doll.canvas`); sul telefono niente scorrimento
  orizzontale.
- Circuiti grandi o con componenti attivi: genera un link al simulatore Falstad (`templates/web/circuito_falstad.md`).
