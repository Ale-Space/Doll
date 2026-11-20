# Circuiti con un simulatore vero: Falstad CircuitJS

`circuito_ac.html` va bene per **un solo anello** in regime sinusoidale (RLC serie, fasori, risonanza),
dove tutto si calcola in forma chiusa. Quando il circuito è "vero" conviene dare all'utente un link a
**CircuitJS** di Paul Falstad, che risolve la rete nodo per nodo a ogni passo temporale e mostra
correnti animate, tensioni a colori e oscilloscopi.

**Usalo per:** reti a più maglie/nodi (sovrapposizione, Thévenin/Norton da verificare), transitori
RC/RL/RLC con interruttori, amplificatori operazionali (invertente, non invertente, integratore,
derivatore, comparatore, Schmitt), diodi e raddrizzatori, transistori BJT/MOSFET, porte logiche e
flip-flop, filtri (con l'oscilloscopio e la FFT).
**Non usarlo per:** fasori e diagrammi vettoriali, curve teoriche |H(jω)|, percorsi guidati Doll:
lì resta la pagina interattiva offline. Le due cose si combinano bene: pagina Doll per la teoria,
link Falstad "prova tu" in chat.

**Serve internet**: il simulatore gira sul sito di Falstad (la pagina non è offline e non va inserita
in `interattivo.html`; il link va messo in chat o in un `<a href>` della pagina).

## Come si fa il link

1. Scrivi il circuito in un file `.txt` (formato sotto), per esempio `$P/circuito.txt`.
2. `.venv/bin/python .claude/skills/spiega/scripts/falstad_link.py "$P/circuito.txt"`
   stampa `https://www.falstad.com/circuit/circuitjs.html?cct=<testo codificato con urllib.parse.quote>`
   (`--open` lo apre anche nel browser). Le righe che iniziano con `#` vengono tolte dallo script.
3. Controlla il link come fa `web_check.py` (Playwright, `channel="chrome"`, attesa ~8 s, screenshot):
   nessun `alert`, il circuito disegnato è quello voluto, l'oscilloscopio mostra la curva attesa.

## Formato testo (export "File → Export As Text")

Una riga per oggetto, campi separati da spazi. **Anche `+` è un separatore**: niente `1e+3`, scrivi
`1000` o `1e3`. Coordinate in pixel sulla griglia (usa multipli di **16**); i due estremi `x1 y1 x2 y2`
sono i due terminali; estremi con le stesse coordinate sono collegati. L'ordine delle righe-elemento
(da 0, contando solo gli elementi) è l'**indice** usato da oscilloscopi, slider e suggerimenti.

**Intestazione** (prima riga):
`$ flags passo velocità corrente scala_tensione potenza [passo_min]`
es. `$ 1 0.000005 10.20027730826997 50 5 50`
- `flags`: 1 = mostra i pallini di corrente (+2 griglia fine, +4 nasconde i colori di tensione,
  +8 mostra la potenza, +16 nasconde i valori, +64 passo adattativo);
- `passo` = Δt della simulazione in s (5 µs va bene per costanti di tempo da ~1 ms in su);
- `velocità` (10.2 ≈ quella predefinita), `corrente` = velocità dei pallini (0–100),
  `scala_tensione` = volt per il colore pieno, `potenza` = luminosità della potenza.

**Elementi** (`tipo x1 y1 x2 y2 flags parametri...`):

| riga | elemento | parametri |
|---|---|---|
| `w x1 y1 x2 y2 0` | filo | — |
| `r ... 0 R` | resistore | R in Ω |
| `c ... 0 C V0` | condensatore | C in F, tensione iniziale V0 |
| `l ... 0 L I0` | induttore | L in H, corrente iniziale I0 |
| `v ... 0 forma f Vmax bias fase duty` | generatore di tensione (bipolo) | `forma`: 0 DC, 1 sinusoide, 2 onda quadra, 3 triangolare, 4 dente di sega, 5 impulsi; `f` in Hz, `Vmax` = valore DC o ampiezza, `bias` = offset, `fase` in rad, `duty` (0.5). Il **+** è l'estremo `x2 y2` |
| `R x1 y1 x2 y2 0 forma f Vmax bias fase duty` | "rail": generatore riferito a massa con un solo terminale | come `v` |
| `g x1 y1 x2 y2 0` | massa | collegata in `x1 y1`, `x2 y2` dà solo il verso del simbolo |
| `s ... 0 pos false` | interruttore | `pos` 0 = chiuso, 1 = aperto; `false` = non a pulsante |
| `S x1 y1 x2 y2 0 pos false 0 2` | deviatore (SPDT) | perno in `x1 y1`, le due uscite a ±16 px trasversali a `x2 y2`; `pos` 0 = prima uscita |
| `a x1 y1 x2 y2 0 Vmax Vmin GBW 0 0 guadagno` | operazionale | ingressi a `x1`, ±16 px in verticale: **−** sopra (`y1−16`), **+** sotto (`y1+16`); uscita in `x2 y2`. flags 1 scambia gli ingressi. Valori tipici `15 -15 1000000 0 0 100000` |
| `d ... 2 default` | diodo | modello |
| `t ...` / `f ...` | BJT / MOSFET | (crea il circuito nell'editor e copia l'export) |
| `O x1 y1 x2 y2 1` | uscita: scrive la tensione del nodo `x1 y1` | — |

**Righe speciali:**
- `o idx velocità 0 4099 scalaV scalaI 0 2 idx2 valore2` — oscilloscopio con **due tracce**:
  la tensione dell'elemento `idx` e la grandezza `valore2` (0 = tensione, 3 = corrente) dell'elemento
  `idx2`. Forma semplice a una traccia: `o idx velocità 0 2 scalaV scalaI 0`.
  `velocità` = passi per pixel (64: ~0,1 s di finestra con passo 5 µs; 16 per segnali a 100 Hz).
- `& idx 0 min max Etichetta` — slider sul primo parametro dell'elemento `idx` (R, C, L, ...);
  l'etichetta è una parola sola (accenti ammessi).
- `h 2 idxR idxC` — scrive "RC = ..." sotto l'oscilloscopio (`h 1 idxL idxC` per LC).

Fonte del formato: sorgenti di CircuitJS1 (github.com/pfalstad/circuitjs1, `ts/CircuitLoader.ts`,
`ts/*Elm.ts`, `ts/ScopeSerializer.ts`, `ts/Adjustable.ts`) ed esempi in `ts/public/circuits/`.
In caso di dubbio: disegna il circuito nell'editor, "File → Export As Text", e copia le righe.

## Esempi verificati (aperti in Chrome headless, 11/2026)

### 1. Carica di un condensatore (RC con deviatore)
5 V, R = 1 kΩ, C = 10 µF, τ = RC = 10 ms. Si apre in carica; un clic sul deviatore scarica C su R.
L'oscilloscopio mostra v_C (sale a 5 V) e i_C (parte da 5 mA e decade); slider per R e C.
```
$ 1 0.000005 10.20027730826997 50 5 50
v 96 336 96 64 0 0 40 5 0 0 0.5
S 256 144 256 64 0 0 false 0 2
w 96 64 240 64 0
w 272 64 400 64 0
w 400 64 400 336 0
r 256 144 256 240 0 1000
c 256 240 256 336 0 0.00001 0
w 96 336 256 336 0
w 256 336 400 336 0
o 6 64 0 4099 5 0.01 0 2 6 3
h 2 5 6
& 5 0 100 10000 Resistenza
& 6 0 0.000001 0.0001 Capacità
```

### 2. Partitore di tensione
9 V su R1 = 2 kΩ e R2 = 1 kΩ: V_out = 9 · 1/(2+1) = 3 V (il simulatore scrive "3 V"). Slider R1, R2.
```
$ 1 0.000005 10.20027730826997 50 5 50
v 112 336 112 64 0 0 40 9 0 0 0.5
w 112 64 240 64 0
r 240 64 240 192 0 2000
r 240 192 240 336 0 1000
w 112 336 240 336 0
O 240 192 336 192 1
g 112 336 112 384 0
& 2 0 100 10000 R1
& 3 0 100 10000 R2
```
Link: `https://www.falstad.com/circuit/circuitjs.html?cct=%24%201%200.000005%2010.20027730826997%2050%205%2050%0Av%20112%20336%20112%2064%200%200%2040%209%200%200%200.5%0Aw%20112%2064%20240%2064%200%0Ar%20240%2064%20240%20192%200%202000%0Ar%20240%20192%20240%20336%200%201000%0Aw%20112%20336%20240%20336%200%0AO%20240%20192%20336%20192%201%0Ag%20112%20336%20112%20384%200%0A%26%202%200%20100%2010000%20R1%0A%26%203%200%20100%2010000%20R2%0A`

### 3. Amplificatore invertente
Sinusoide 1 V, 100 Hz; R1 = 1 kΩ, Rf = 10 kΩ: G = −Rf/R1 = −10, uscita 10 V di picco in
controfase (alimentazione ±15 V, quindi niente saturazione). Oscilloscopio: uscita e ingresso.
Slider su Rf (sopra 15 kΩ l'uscita satura a ±15 V).
```
$ 1 0.000005 10.20027730826997 50 5 50
v 96 256 96 112 0 1 100 1 0 0 0.5
g 96 256 96 304 0
r 96 112 192 112 0 1000
r 192 144 336 144 0 10000
w 336 144 336 192 0
w 192 112 192 144 0
w 192 144 192 176 0
w 96 256 192 256 0
w 192 208 192 256 0
a 192 192 336 192 0 15 -15 1000000 0 0 100000
O 336 192 400 192 0
o 10 16 0 4099 10 0.05 0 2 0 0
& 3 0 1000 100000 Rf
```

## Errori tipici
- Un estremo che non coincide esattamente con un altro (es. 240 contro 241) lascia il circuito aperto:
  il simulatore non dà errore, semplicemente non scorre corrente.
- Indici di `o`, `&`, `h` sbagliati dopo aver aggiunto o tolto una riga: ricontali.
- Δt troppo grande rispetto a τ o al periodo: curve spezzate. Δt ≲ τ/100 e ≲ T/200.
- Un circuito senza massa (`g`) funziona lo stesso, ma le tensioni sono riferite a un nodo arbitrario.
