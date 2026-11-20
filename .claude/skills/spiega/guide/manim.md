# Manuale dei video Doll (Manim)

**Leggilo tutto prima di scrivere una scena.** Vale per qualunque AI (Claude, ChatGPT/Codex, altre): lo
scopo è che ogni video abbia lo stesso stile e la stessa qualità, chiunque lo scriva. Ciò che qui è una
regola viene controllato da `scripts/controllo_stile.py` e dal verificatore: se non la rispetti, il video
viene rifatto.

Esempi di riferimento da aprire e imitare (sono il livello richiesto):
- `templates/teorema.py`: il punto di partenza per un teorema in 2D (Lagrange e il controesempio |x|), con
  tutti gli atti; semplice e leggero da renderizzare.
- `esempi/schwarz.py`: teorema di Schwarz. Superficie 3D, barre, mappe di colore, il quadrato che Lagrange
  "schiaccia" su un punto, lo zoom che uniforma il colore, il controesempio.
- `esempi/c1_differenziabile.py`: C¹ ⇒ differenziabile. Percorso asse per asse sulla superficie, zoom
  isometrico, numeri dal vivo, controesempio ρ² sin(1/ρ).
- `esempi/teorema_zeri.py`: teorema degli zeri in 2D. La bisezione stringe gli estremi su c; lo stesso gesto su
  una curva con un salto si stringe sul salto (fatto da un'altra AI seguendo questo manuale).
- `esempi/pendolo_energia.py`: energia nel pendolo. Moto, barre K e U che si scambiano con la somma ferma su E₀,
  poi lo stesso moto con attrito e l'energia persa che cresce (fatto da un'altra AI seguendo questo manuale).
- `templates/fisica.py`, `templates/meccanismo.py`, `templates/fasori.py`: fisica (forze, simulazione dalla
  Lagrangiana, fasori).

Questi esempi durano 20–45 s: sono il livello **Veloce**. Per Normale e Approfondito si mantiene la stessa
qualità di ogni singolo gesto, ma i gesti sono di più: uno per ogni idea del ragionamento (§2.8, §3).

**Livello di impegno.** In `piano.md` c'è `**Impegno**: veloce | normale | approfondito` (SKILL.md, «Livelli di
impegno»). Decide durata, struttura, testo ammesso e controlli: leggilo prima di tutto. Senza indicazione vale
`normale`. Regola di serietà: il video dura quanto serve perché si capisca **tutto** entro il limite del livello;
non si taglia un passaggio per accorciare. Tra "più corto" e "più chiaro" vince "più chiaro".

---

## 1. Lo scopo: il "wow, ecco perché"

Il video non spiega a parole: **fa vedere perché la cosa è vera**. Chi lo guarda senza audio, alla fine,
deve poter dire in una frase che cosa ha visto succedere e perché questo dimostra il risultato.

Prima di scrivere il codice devi avere, in `piano.md` (vedi §4):
- la **frase wow**: cosa capirà chi guarda ("R è un numero solo: per righe e per colonne è lo stesso");
- il **gesto visivo**: la trasformazione che lo fa vedere (il quadrato che collassa su un punto, lo
  zoom che schiaccia la superficie sul piano, l'angolo che cresce finché il blocco scivola). Nel livello Veloce
  è uno solo; in Normale e Approfondito c'è un gesto principale che regge tutto il video e **un gesto per
  ogni passaggio** del ragionamento (nel piano: la tabella "passaggio → gesto", §4).

Se non riesci a dire il gesto visivo in una riga, non sei pronto per scrivere la scena.

Vale anche `guide/didattica.md`: nel video si traduce così.
- **Pre-addestramento** (atto 1): si nominano le parti con le etichette *prima* di muoverle.
- **Prevedi → osserva**: prima del gesto principale una didascalia-domanda ("Zoomando, l'errore sparisce?"),
  circa 1 s di pausa con l'oggetto fermo ma visibile, poi la risposta che si vede.
- **Segnalazione**: ciò che si muove è nel colore del suo ruolo o lampeggia (`Indicate`, `Flash`); ciò che
  distrae si attenua (opacità 0,3–0,5).
- **Contiguità e coerenza**: etichette accanto agli oggetti; nessuna decorazione; nessun testo che ripete ciò
  che si vede già.
- **Il controesempio smonta il preconcetto** scritto nel piano.

## 2. I principi (tutti obbligatori)

1. **Mostra, non scrivere.** La dimostrazione si vede negli oggetti che si muovono. Niente catene di
   passaggi algebrici, niente elenchi, niente schermate di formule. Veloce: nessuna formula della
   dimostrazione. Normale e Approfondito: la **formula chiave** di un passaggio può comparire *accanto
   all'oggetto che la fa vedere*, una per volta, mentre l'oggetto si muove (`formula_chiave(...)` del kit,
   §7): è l'etichetta matematica del gesto, non la spiegazione al posto del gesto. Le derivazioni complete
   vanno nella dispensa e in chat.
2. **Un gesto alla volta.** In ogni momento si muove una cosa sola, quella di cui parla la didascalia.
   Gli occhi devono sapere dove guardare.
3. **Ogni ipotesi è un oggetto.** "D aperto" è il quadratino che sta dentro il dominio; "f_x continua" è il
   colore che diventa uniforme zoomando; "attrito statico ≤ μN" è la freccia dell'attrito che arriva al suo
   massimo. Se un'ipotesi conta, deve vedersi dove conta.
4. **Esempio concreto, numeri veri.** Si lavora su un esempio preciso scelto perché il fenomeno si veda bene
   (punti ben separati, effetti visibili, nessun caso degenere), con valori verificati in `piano.md`. Mai
   un disegno "generico" con lettere e basta.
5. **Il controesempio usa lo stesso gesto.** Si ripete la stessa trasformazione togliendo un'ipotesi, e si
   vede *dove* si rompe (lo zoom non uniforma più il colore; il blocco non si ferma più). Non è un elenco di
   valori: è la stessa scena che va storta.
6. **Il movimento porta il significato.** Zoom, scorrimento, deformazione, collasso, crescita: un
   ValueTracker che varia un parametro vale più di dieci formule. Le scene ferme sono vietate (§9).
7. **Stesso stile sempre.** Sfondo nero di Manim, palette semantica del kit (§6), impaginazione fissa (§5).
   Mai colori o sfondi propri.
8. **La durata giusta per il livello, mai di meno di quanto serve.**
   | Impegno | Durata | Cosa deve esserci |
   |---|---|---|
   | Veloce | 20–45 s | l'idea centrale: un gesto + il controesempio |
   | Normale | 45 s – 1:30 | tutti i passaggi chiave, ciascuno con il suo gesto, + il controesempio |
   | Approfondito | 1:30 – 3:00 | tutta la dimostrazione o soluzione a capitoli: ogni ipotesi un oggetto, un controesempio per ogni ipotesi importante, riepilogo |
   Il tempo in più serve a **mostrare più passaggi**, non a fare pause più lunghe o a ripetere: ogni secondo
   ha qualcosa che si muove e che insegna. Meglio un gesto chiaro e lento che tre confusi e veloci.

## 3. Struttura fissa (atti)

Ogni video di teorema segue questi atti, in quest'ordine. Gli esercizi usano 0, 1, 2 e 5.

| Atto | Durata | Cosa succede |
|---|---|---|
| 0. Apertura | ≈ 2–3 s | `titolo(...)` (3–5 parole) e `dati(...)` con l'enunciato in una formula, in alto a destra |
| 1. L'oggetto | 3–8 s | compare l'esempio concreto (grafico, superficie, corpo, circuito) e gli elementi in gioco (punti, vertici, forze) |
| 2. Il meccanismo | 10–20 s | il gesto visivo, in 2–4 passi; ogni passo = un movimento + una didascalia |
| 3. La conclusione | 3–6 s | il passaggio che chiude (limite, zoom, configurazione finale) e una didascalia-slogan in giallo (`colore=C_ACCENTO`) |
| 4. Controesempio | 6–12 s | stesso gesto senza un'ipotesi: si vede cosa si rompe (solo se il teorema ha un'ipotesi essenziale) |
| 5. Risultato | ≈ 2 s | `risultato_angolo(...)`: il risultato in un riquadro, sopra la scena ancora visibile |

Le durate della tabella sono quelle del livello **Veloce**. Negli altri livelli:
- **Normale**: stessi atti; l'atto 2 si divide in **3–6 passi**, uno per passaggio del ragionamento (10–20 s
  ciascuno), ognuno con il suo gesto, la sua didascalia e, se serve, la sua formula chiave; dopo l'atto 3 una
  breve conclusione che rimette insieme i passi (l'oggetto torna intero, i pezzi visti si illuminano in ordine).
- **Approfondito**: il video è diviso in **capitoli** (5–9), ciascuno di 15–30 s, segnalati da `capitolo(...)`
  del kit (nome di 2–4 parole, piccolo, sotto il titolo; la scena non si ferma):
  1. l'oggetto e le ipotesi (ogni ipotesi diventa un oggetto visibile: il dominio aperto, la continuità…);
  2. … uno o più capitoli per i passaggi della dimostrazione o della soluzione, nell'ordine del libro;
  3. la conclusione (il passaggio che chiude, con lo slogan in giallo);
  4. i controesempi: uno per ogni ipotesi importante, ciascuno con lo stesso gesto che va storto;
  5. il riepilogo (15–20 s): la scena si ricompone e i passaggi si riaccendono in ordine con il loro nome,
     poi il risultato nel riquadro.
  Ogni capitolo comincia da dove finisce il precedente (stessa scena che continua), mai da uno schermo vuoto.

Tra un atto (o capitolo) e l'altro: transizione morbida (camera che si muove, `FadeOut` di ciò che non serve,
oggetti che si trasformano), mai uno schermo vuoto per più di mezzo secondo.

## 4. Il copione (in `piano.md`, prima del codice)

L'esperto lo scrive nella sezione "Specifica della visualizzazione"; il costruttore lo segue. Formato:

```
**Impegno**: veloce | normale | approfondito
**Frase wow**: ...
**Gesto visivo**: ...
**Domanda di previsione**: la didascalia-domanda posta prima del gesto (≤ 8 parole)
**Esempio concreto**: funzione/sistema e valori (tutti verificati sopra)
**Passaggi → gesti** (normale e approfondito): una riga per ogni passaggio del ragionamento
| Passaggio (dalla soluzione) | Gesto che lo fa vedere | Formula chiave a schermo (facoltativa) |
|---|---|---|
| ... | ... | ... |
**Capitoli** (solo approfondito): elenco numerato con nome (2–4 parole) e intervallo di tempo
**Copione**
| t (s) | Cosa si vede | Cosa si muove | Didascalia (≤ 8 / 10 / 12 parole) |
|---|---|---|---|
| 0–3 | titolo, enunciato | - | - |
| 3–8 | ... | ... | ... |
**Risultato nel riquadro**: ...
**Durata**: ... s (dentro i limiti del livello, §2.8)
```
Il copione è completo: ogni passaggio della soluzione verificata compare nella tabella "Passaggi → gesti" e ha
almeno una riga nel copione. Se un passaggio non ha un gesto, va trovato (repertorio §10) prima del codice; se
proprio non si può mostrare, il copione dice esplicitamente che resta alla dispensa e alla chat.

## 5. Lo schermo

```
┌──────────────────────────────────────────────────────────────┐
│ titolo (kit)                          dati / enunciato (kit)  │  y ≈ 3,3
│                                                              │
│        VISUALIZZAZIONE (centro, o sinistra se c'è il         │
│        pannello)                       │ pannello valori      │
│                                        │ (opzionale, a destra)│
│                                                              │
│                 didascalia (kit, in basso)                   │  y ≈ -3,3
└──────────────────────────────────────────────────────────────┘
```
- Zona sicura |x| ≤ 6,6, |y| ≤ 3,6. La visualizzazione occupa almeno metà schermo.
- **Pannello valori** (facoltativo): a destra, senza cornice, al massimo 4 righe di grandezze con numeri
  che cambiano dal vivo (`numero_vivo`) o barre. Niente frasi, niente formule della dimostrazione (la formula
  chiave dei livelli Normale e Approfondito va accanto all'oggetto, non nel pannello: §7).
- Due viste affiancate sono ammesse quando si confrontano due cose (due ordini, due grafici collegati), ma
  sono **scene vive**, non schede con un titolo dentro un riquadro.
- **Al massimo due copie grandi** dello stesso oggetto affiancate. Se servono tre pezzi (totale = parte +
  parte, come nella sovrapposizione degli effetti): il totale in alto e le due parti sotto, oppure le parti
  una alla volta accanto al totale. Dopo lo `scale` le etichette devono restare leggibili (mai sotto 20 punti:
  se rimpiccioliscono troppo, cambia disposizione invece di rimpicciolire).
- Ogni numero mostrato ha il suo nome accanto (`I_3 = 2,50 A`, non `= 2,50 A`).
- Etichette sugli oggetti (P, ξ, x = δ, F, v), vicine e senza sovrapposizioni.

## 6. Palette e caratteri (dal kit: `from doll_kit import *`)

Colori **solo** dalle costanti del kit: `doll_kit` e, per i pezzi meccanici, `fisica_kit` (`INCHIOSTRO`, `ASTA`,
`ROSA`, ...: hanno già lo stile Doll). Mai `"#rrggbb"` nella scena, mai `background_color`.

| Ruolo | Costante | Uso |
|---|---|---|
| oggetto principale | `C_OGGETTO` (superfici: `**SUPERFICIE`) | grafico, curva, superficie |
| direzione/variabile 1 | `C_X` | asse x, tratto "cambia solo x", lettura per righe |
| direzione/variabile 2 | `C_Y` | asse y, seconda lettura |
| errore / ciò che sparisce | `C_ERRORE` | errore, resto, stacco, differenza |
| riferimento / accento | `C_RIF` (= `C_ACCENTO`) | piano o retta tangente, valore limite, punto chiave, slogan |
| punti | `C_PUNTO` | punti e loro etichette |
| segni | `C_PIU`, `C_MENO` | vertici con segno, contributi |
| controesempio | `C_CONTRO` | ciò che va storto |
| fisica | `C_FORZA`, `C_PESO`, `C_VELOCITA`, `C_ACCELERAZIONE`, `C_CAMPO`, `C_ENERGIA_K`, `C_ENERGIA_U`, `C_CORPO` | vettori e grandezze fisiche |
| testo secondario | `C_TENUE` | note ("scala z ingrandita"), assi |

Lo stesso colore vuol dire sempre la stessa cosa in tutto il video. Mappe di colore: solo `mappa`,
`immagine_mappa`, `barra_colori` (scala fissa: −1 blu, 0 scuro, +1 arancio).

Caratteri: titolo e didascalie dal kit; etichette 26–36; pannello 22–32; mai sotto 20. `Text` per le parole
(con accenti), `MathTex` per le formule.

## 7. Testo ammesso
- titolo (3–5 parole) e dati/enunciato in una formula;
- didascalie che dicono **dove guardare** o **cosa sta succedendo** ("Lagrange in y: due lati diventano uno"),
  con `cambia_didascalia`: al massimo **8 parole** (Veloce), **10** (Normale), **12** (Approfondito);
- etichette sugli oggetti e numeri che cambiano dal vivo;
- Normale e Approfondito: la **formula chiave** del passaggio con `formula_chiave(...)`: una riga, accanto
  all'oggetto che la fa vedere, nel colore del suo ruolo, **una sola alla volta**, mentre l'oggetto si muove
  (es. accanto al segmento a quota η: `\varphi(\delta)-\varphi(0)=\delta\,\varphi'(\eta)`);
- Approfondito: il nome del capitolo con `capitolo(...)` (2–4 parole, piccolo, in alto a sinistra);
- il risultato nel riquadro finale.

Vietati in tutti i livelli: paragrafi, elenchi, schermate di solo testo, catene di uguaglianze, più formule
insieme, formule lontane dall'oggetto (in una colonna a lato), titoletti grandi dentro la scena ("Il
quadratino", "Lo stesso numero"). In Veloce anche le formule della dimostrazione.

## 8. Movimento e ritmo
- Comparse 0,4–0,9 s; il gesto principale 2,5–4,5 s con `rate_func=smooth` (o `linear` per il tempo fisico);
  in Normale e Approfondito i gesti dei passaggi chiave possono durare 4–8 s: lenti, da seguire con gli occhi.
- Dopo ogni passo una pausa di lettura di 0,7–1,5 s (`self.wait`, mai oltre 2,5 s); dopo una formula chiave
  o la conclusione di un capitolo 1,5–2 s, con qualcosa che continua a muoversi piano (un punto che pulsa,
  la tangente che oscilla) invece di un fermo immagine.
- Video lunghi: il ritmo resta vivo. Ogni capitolo ha almeno un movimento lungo; niente capitolo fatto solo
  di comparse e didascalie.
- Una didascalia cambia quando cambia ciò che si muove, non prima: se dice "1,25 A e 1,25 A", quei numeri
  devono essere già a schermo (o comparire nello stesso `self.play`).
- Camera: movimenti di circa 1 s, pochi e motivati (passare dal 3D alla vista dall'alto, avvicinarsi).
- Nessun tratto fermo oltre 3 s; il video deve muoversi per più di metà del tempo (lo misura il controllo:
  sotto il 48% boccia, sotto il 55% avvisa). Per alzarlo: pause di lettura più corte (0,6–0,9 s); il gesto
  continua mentre cambia la didascalia (passa le due animazioni nello stesso `self.play`); il gesto principale
  più lungo e lento invece di tanti passi brevi con pause.
- Gli oggetti nascono e si trasformano (`Create`, `Transform`, `ReplacementTransform`, ValueTracker), non
  appaiono e spariscono a blocchi.

## 9. Vietato (motivi di rifacimento)
- **Video-presentazione**: schede o riquadri con un titolo e formule dentro, oggetti fermi e didascalie che
  raccontano. (È l'errore tipico: un quadrato disegnato a sinistra e una colonna di formule a destra.)
- Formule della dimostrazione a schermo in Veloce; in Normale e Approfondito formule fuori dalle regole del §7
  (più di una alla volta, catene di uguaglianze, colonne di formule lontane dall'oggetto).
- Un passaggio della soluzione saltato o tirato via per stare nei tempi (serietà: se serve, si mostra).
- Allungare il video con pause, ripetizioni o rallentamenti senza contenuto per raggiungere la durata.
- `RoundedRectangle` o cornici attorno ai pannelli; colori `"#..."`; sfondi diversi dal nero; un secondo stile
  nello stesso video.
- **Montare video**: tagliare, concatenare o incollare mp4 (av, ffmpeg, moviepy). Un video si modifica solo
  cambiando `scena.py` e rifacendo il render completo. (Gli script della skill, come `frames.py` e
  `controllo_stile.py`, leggono i video e vanno usati; il divieto riguarda la scena e il montaggio.)
- Lavorare fuori dalla cartella `progetto/` dell'argomento (niente cartelle temporanee tue; la cache di Manim la
  gestisce `render.sh` da solo).
- Numeri non presenti nella soluzione verificata.

## 10. Repertorio dei gesti visivi

### Analisi
| Idea | Gesto |
|---|---|
| derivata, retta tangente | la tangente scorre lungo il grafico (ValueTracker su x₀), pendenza dal vivo |
| valor medio (Lagrange, Rolle) | secante fissa; la tangente scorre finché è parallela; in 2D: percorso **asse per asse** (tratti paralleli agli assi, lungo le righe della griglia) |
| limite, continuità, ε–δ | la fascia ε disegnata **sul grafico**; l'intorno δ che si stringe; il grafico entra (o non entra) nella fascia |
| differenziabilità | **zoom isometrico** λ(f(P+u/λ) − f(P)): il grafico si schiaccia sul piano tangente; l'errore (rosso) sparisce più in fretta di ρ |
| continuità di una funzione di 2 variabili (o della sua derivata) | **mappa di colore** sul dominio e zoom sul punto: continua = colore che si uniforma; omogenea di grado 0 = lo zoom non cambia nulla |
| derivate parziali, direzionali | tagli della superficie con piani x = cost., y = cost.; la curva-taglio e la sua tangente |
| gradiente, curve di livello | curve di livello sulla superficie e sotto; frecce ortogonali alle curve |
| moltiplicatori di Lagrange | curve di livello che si muovono finché toccano il vincolo: tangenza, gradienti paralleli |
| integrale | rettangoli di Riemann che si infittiscono; integrali doppi: colonnine o fette che riempiono il volume |
| successioni e serie | punti che si accumulano su una retta; somme parziali come segmenti uno dopo l'altro |
| teoremi del confronto | due grafici che "schiacciano" il terzo |
| campi vettoriali, Green, Stokes | piccole circolazioni sui quadratini che si cancellano all'interno; resta il bordo |
| EDO | campo di direzioni e soluzioni che scorrono; dipendenza dal dato iniziale |
| Fourier, complessi | `templates/fourier.py`, `templates/complessi.py` |

### Fisica
| Idea | Gesto |
|---|---|
| forze, equilibrio, attrito | diagramma di corpo libero **sul corpo**, frecce con scala fissa (`freccia_fisica`); un parametro varia (angolo, forza) e si vedono le configurazioni (fermo → limite → scivola) |
| cinematica | traiettoria tracciata (`TracedPath`), vettori v e a che viaggiano con il corpo; grafici x(t), v(t) che si disegnano dal vivo a lato |
| energia | il moto e, a lato, barre K e U che si scambiano con la somma costante |
| oscillazioni, sistemi con molle e pendoli | simulazione vera dalla Lagrangiana (`templates/meccanismo.py` + `fisica_kit`), grafici dal vivo |
| urti, quantità di moto | prima e dopo; i vettori p si sommano testa-coda e la somma resta uguale |
| corpo rigido, rotolamento | velocità dei punti del disco come frecce; il punto di contatto è fermo |
| campi elettrici e magnetici, Gauss | linee di campo; superficie che si deforma con il flusso che resta uguale |
| onde | sovrapposizione e interferenza dal vivo; una costante (λ, f) che varia |
| reti elettriche in continua | correnti come puntini che scorrono (velocità ∝ corrente), potenziali dei nodi visibili, la rete che si richiude nell'equivalente di Thévenin (`templates/circuito.py` + `kit/circuiti_kit.py`) |
| sovrapposizione degli effetti | la rete si sdoppia: in ogni copia resta acceso un generatore (valori come `ValueTracker` condivisi; spento = 0); le correnti parziali si sommano nel totale; girando un generatore cambia solo il suo pezzo |
| circuiti in alternata | fasori che ruotano e proiezioni che tracciano le sinusoidi (`templates/fasori.py`) |
| qubit, spin | sfera di Bloch con il vettore che precede o ruota, P₁ dal vivo (`templates/quantistica.py`, dinamica da QuTiP) |
| termodinamica | ciclo nel piano pV con l'area (lavoro) che si colora mentre il punto lo percorre |

Fisica: preferisci la soluzione analitica animata con un ValueTracker, o la simulazione vera del kit; scala
fissa delle frecce dichiarata nel codice; grandezze con unità nelle etichette.

## 11. Procedura
1. Leggi `piano.md` (copione), questo manuale, l'esempio di riferimento più vicino, il template indicato e
   `kit/doll_kit.py`.
2. Copia il template (per un teorema `templates/teorema.py`) in `"$P/scena.py"` (classe sempre `Esercizio`)
   e scrivi la scena seguendo il copione.
3. Bozza e fotogrammi:
   ```bash
   .claude/skills/spiega/scripts/render.sh "$P/scena.py" bozza
   .venv/bin/python .claude/skills/spiega/scripts/frames.py "$P/bozza.mp4" auto
   .venv/bin/python .claude/skills/spiega/scripts/controllo_stile.py "$P"
   ```
   `frames.py ... auto` sceglie quanti fotogrammi in base all'impegno di `piano.md` (12 Veloce, 18 Normale,
   uno ogni 5 s Approfondito) e, se sono più di 12, li divide in più fogli `bozza_frames.png`,
   `bozza_frames_2.png`, …: guardali **tutti**.
   Se il render fallisce: leggi l'errore, correggi, riprova (al massimo 3 volte). Le scene lunghe si
   scrivono e si provano un capitolo alla volta (commentando i successivi), poi si fa il render intero.
4. Guarda i fogli dei fotogrammi e fai il **test muto**: coprendo le didascalie, si capisce dai soli oggetti
   cosa succede? Ogni didascalia (e ogni formula chiave) corrisponde a ciò che si vede in quel fotogramma?
   Niente sovrapposizioni, niente testo tagliato. Normale e Approfondito: ogni riga della tabella "Passaggi →
   gesti" si vede davvero nel video?
5. `controllo_stile.py` deve dire `OK`. Gli `ERRORE` vanno corretti tutti; gli `AVVISO` si correggono se si
   può, altrimenti si scrive il motivo nella risposta (es. una didascalia di 11 parole più chiara di una di 10).
6. Finale (dopo la verifica): `render.sh "$P/scena.py" finale` (720p; con `**Impegno**: approfondito` in
   `piano.md` fa da solo il 1080p; `FINALE_HD=1` lo forza), di nuovo `controllo_stile.py "$P"` e uno sguardo a
   `frames.py "$P/finale.mp4" auto`.

**Modificare un video esistente**: si cambia `scena.py` e si rifà il render completo. Se `scena.py` manca o
non corrisponde al video, si riscrive la scena intera seguendo questo manuale.

## 12. Regole tecniche di Manim (errori frequenti)
- `Scene` per tutto ciò che è 2D (grafici, mappe di colore, meccanismi); `ThreeDScene` solo per superfici e
  oggetti 3D (più lenta e con regole sue, sotto).
- Formule: `MathTex(r"...")`. Testo con accenti: `Text("...")`. **Mai lettere accentate dentro MathTex/Tex**,
  e mai il meno tipografico "−" dentro MathTex (usa "-").
- Nei `Text` puoi usare Unicode (θ, μ, λ, ², →, −); nei `MathTex` i comandi LaTeX. Virgola decimale: `0{,}4`
  in MathTex, `virgola(x)` per i Text.
- Concatenazione di stringhe: `r"\quad" r"V_1"` diventa `\quadV_1`. Metti uno spazio: `r"\quad "`.
- f-string con LaTeX: graffe doppie, `rf"\frac{{a}}{{b}} = {x:.2f}"`.
- Oggetti che dipendono da un parametro: `ValueTracker` + `always_redraw(lambda: ...)` o `add_updater`.
- Numeri che cambiano dal vivo: `numero_vivo(...)` del kit (evita le "immagini fantasma" in ThreeDScene).
- Dopo oggetti grandi (piani, griglie): `self.bring_to_front(titolo, dati, didascalia)`.
- Trasformazioni lineari: `M(t) = (1-t)I + tA` con un ValueTracker (le frecce restano frecce).
- **3D** (`ThreeDScene`):
  - testo fisso sullo schermo: le funzioni del kit lo fanno da sole; per i tuoi `fisso(self, m)` e poi `FadeIn`;
  - etichette che seguono un punto 3D: `orientato(self, m)` e poi `FadeIn(m)`;
  - per spostare la scena non usare `frame_center` (sposta anche il testo fisso): somma un offset ai punti;
  - quando la direzione degli assi conta, camera con `theta = -90°` (x orizzontale, y in profondità) e
    `phi` 50–65°; disegna gli assi;
  - gli oggetti non `shade_in_3d` vengono disegnati sopra le superfici: per una base sotto una superficie
    `m.set_shade_in_3d(True)` e `m.z_index_group = VectorizedPoint(<punto lontano dietro>)`;
  - `Surface` con `resolution` 8–18; niente `Line3D`/`Arrow3D` dentro `always_redraw`;
  - camera: `self.move_camera(phi=..., theta=..., run_time=1, added_anims=[...])`.
- Mappe di colore animate: `immagine_mappa(...)` e in un updater `m.pixel_array = mappa(...)`.
- Frecce di forza: scala fissa (es. 1 N → 0,07 unità), controlla che non escano dallo schermo.
- 3D è lento da renderizzare: obiettivo bozza sotto i 2 minuti.
- Niente `self.wait()` più lunghi di 2,5 s.
