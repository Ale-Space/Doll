# Guida didattica Doll

**Vale per tutto ciò che produciamo**: copione, video, pagina interattiva, dispensa, risposta in chat. La
leggono gli esperti (che progettano), i costruttori (che realizzano) e il verificatore (che controlla).
Non sono gusti: sono i risultati più solidi della ricerca sull'apprendimento. Fonti principali: Mayer,
*Multimedia Learning* (principi multimediali); Sweller e Renkl (carico cognitivo, esempi svolti che si
ritirano); Chi (auto-spiegazione); White e Gunstone, Crouch e Mazur (prevedi → osserva → spiega); Posner e
Hestenes (preconcetti e cambiamento concettuale); Fyfe (dal concreto all'astratto); Roediger e Karpicke,
Dunlosky et al. 2013 (recupero attivo, pratica distanziata e mescolata); Kalyuga (inversione dell'esperienza).

## I principi

| # | Principio | Cosa vuol dire | Perché funziona |
|---|---|---|---|
| 1 | **Obiettivo esplicito** | si dice all'inizio cosa si saprà *fare* alla fine ("saprai calcolare l'equivalente di Thévenin e capire perché il carico non se ne accorge") | lo studente sa a cosa fare attenzione |
| 2 | **Prerequisiti richiamati** | 1–3 cose da sapere già, richiamate in una riga ciascuna | il nuovo si aggancia al vecchio; se manca un pezzo lo si vede subito |
| 3 | **Prevedi, osserva, spiega** | prima di mostrare la risposta si pone una domanda di previsione ("zoomando, l'errore sparisce?"), poi la si fa vedere, poi la si spiega | prevedere costringe a usare il proprio modello mentale; se sbagli, il conflitto fa ricordare |
| 4 | **Dal concreto all'astratto** | prima un esempio con numeri veri e un disegno, poi il caso generale, poi la formula | l'astratto ha senso solo dopo averlo visto succedere |
| 5 | **Un'idea alla volta** (carico cognitivo) | un passo per volta (segmentazione), si evidenzia ciò che conta (segnalazione), l'etichetta sta accanto all'oggetto (contiguità), niente decorazioni (coerenza), niente testo che ripete ciò che si vede (ridondanza) | la memoria di lavoro tiene pochi elementi: ciò che è superfluo ruba posto a ciò che serve |
| 6 | **Esempi svolti che si ritirano** | un esempio svolto completo, poi uno da completare (alcuni passi lasciati a te), poi esercizi liberi | si impara prima guardando, poi facendo: il passaggio graduale evita il salto nel vuoto |
| 7 | **Il perché di ogni passo** (auto-spiegazione) | ogni passo ha il suo perché; negli esercizi si chiede "perché si può fare?" | chi si spiega i passi capisce il metodo, non solo il risultato |
| 8 | **Il preconcetto smontato** | si nomina l'errore tipico ("se f_x non è continua allora f non è differenziabile") e lo si smonta con un controesempio che si vede | un preconcetto ignorato resta: va mostrato che fallisce |
| 9 | **Rappresentazioni collegate** | figura, formula e parole dicono la stessa cosa, con lo stesso colore per la stessa grandezza in video, pagina e dispensa | due canali (visivo e verbale) collegati si rinforzano |
| 10 | **Recupero attivo e ripasso** | domande di autoverifica con la risposta *altrove* (in fondo), esercizi di tipi mescolati, un ripasso fissato a 2 giorni e a 1 settimana | richiamare dalla memoria consolida molto più che rileggere |
| 11 | **Feedback immediato** | nella pagina una lettura dice subito se il bersaglio è raggiunto; nelle risposte si spiega anche l'errore più probabile | correggere subito impedisce di fissare l'errore |
| 12 | **Livello giusto** | base: più passi e più "perché"; da esame o "veloce": meno impalcature, più esercizi | ciò che aiuta un principiante rallenta chi sa già |
| 13 | **Lingua chiara e del corso** | frasi brevi; ogni termine definito al primo uso; la notazione e i nomi del libro/corso dell'utente (es. ∂_x∂_y f come nei suoi appunti) | lo studente deve riconoscere a lezione e all'esame ciò che ha visto |

## Come si applica

### Nel piano (l'esperto, prima di tutto)
In `piano.md` ci sono sempre: **Obiettivo** (una frase, "saprai…"), **Prerequisiti** (1–3), **Preconcetto da
smontare** (l'errore tipico più importante e il controesempio che lo smonta), **Domanda di previsione** (quella
che il video o la pagina pone prima della rivelazione) e, negli esercizi per allenarsi, un esercizio **da
completare**, uno **base** e uno **da esame** (meglio se di un tipo diverso: pratica mescolata). Il formato è
in `esperti/COMUNE.md`.

### Nel video (`guide/manim.md`)
- Atto 1 (l'oggetto) = **pre-addestramento**: si nominano le parti (etichette) *prima* di muoverle.
- Prima del gesto principale, la **domanda di previsione** come didascalia ("Zoomando, l'errore sparisce?"),
  una pausa di circa 1 s, poi la risposta che si vede.
- **Segnalazione**: ciò che si muove ha il colore del suo ruolo o lampeggia (`Indicate`, `Flash`); il resto si
  attenua (`set_opacity` 0,3–0,5) se distrae.
- **Contiguità**: etichette e numeri accanto all'oggetto, mai in una legenda lontana.
- Il **controesempio** smonta il preconcetto scritto nel piano.

### Nella pagina interattiva (`guide/web.md`)
- La guida segue *prevedi → osserva → spiega*: un passo chiede la previsione ("Prima di muovere lo slider:
  cosa farà la corrente?"), il successivo la mostra.
- L'ultimo passo è **"Prova tu"**: un compito preciso (portare un valore a un bersaglio) con una lettura che
  conferma subito quando è raggiunto (feedback immediato).

### Nella dispensa (`templates/pdf/*.tex`)
Ordine: titolo → **obiettivi** (con i prerequisiti) → **prova a prevedere** → testo/enunciato → idea → metodo →
**esempio svolto** (passi con il perché) → **preconcetto** smontato → errori tipici → cosa guardare nel video →
**esercizio da completare** → esercizi (base, da esame) → **verifica te stesso** (3–5 domande, soluzioni in
fondo) → **ripasso** (2 domande da rifare tra 2 giorni e tra 1 settimana). Ambienti pronti in `doll.sty`:
`obiettivi`, `previsione`, `preconcetto`, `autoverifica` (con `\soluzione{...}`), `ripasso`, `\vuoto`.

### Nella risposta in chat (`SKILL.md` §7)
Obiettivo in una riga; l'idea chiave prima dei passaggi; i passi brevi con il loro perché; il preconcetto in una
riga; "nel video guarda…"; alla fine 2–3 **domande di verifica** (le soluzioni sono nella dispensa) e il ripasso
consigliato. Niente muri di testo: i dettagli stanno nel PDF.

## Checklist (per chi costruisce e per il verificatore)
- [ ] L'obiettivo è esplicito e il prodotto lo raggiunge.
- [ ] Prima della risposta c'è una domanda di previsione (video, pagina, dispensa).
- [ ] Prima l'esempio concreto, poi la regola generale.
- [ ] Un'idea per volta; etichette accanto agli oggetti; nessuna decorazione o testo ridondante.
- [ ] Il preconcetto principale è nominato e smontato da un controesempio che si vede.
- [ ] Esempio svolto → esercizio da completare → esercizi liberi; ogni passo ha il suo perché.
- [ ] Domande di autoverifica con le soluzioni lontane; ripasso fissato.
- [ ] Stessa notazione e stessi colori in video, pagina e dispensa; notazione del corso dell'utente.
