#!/usr/bin/env bash
# Uso: pdf_build.sh <cartella> [--pagine]
#   Compila <cartella>/dispensa.tex con latexmk -pdf (pdflatex), nella cartella stessa.
#   kit/pdf e' nel TEXINPUTS, quindi \usepackage{doll} funziona da qualsiasi cartella.
#   Se va a buon fine:
#     - cancella i file ausiliari (.aux .log .out .fls .fdb_latexmk ...);
#     - scrive <cartella>/dispensa_pagine.png (griglia delle pagine, per controllarle con Read);
#       con --pagine anche <cartella>/pagine/pagina_N.png in alta risoluzione;
#     - segnala le righe "Overfull \hbox" (testo che esce dal margine);
#     - stampa sull'ultima riga il percorso del PDF.
#   Se fallisce: stampa le righe di errore "!" del .log con un po' di contesto, lascia
#   dispensa.log nella cartella ed esce con codice 1.
set -uo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
[ $# -ge 1 ] || { sed -n '2,13p' "$0" >&2; exit 2; }
DIR="$(cd "$1" && pwd)" || exit 2
PAGINE="${2:-}"
[ -f "$DIR/dispensa.tex" ] || { echo "ERRORE: manca $DIR/dispensa.tex" >&2; exit 2; }

for cand in "${DOLL_VENV:-}" "$SKILL_DIR/../../../.venv" "$HOME/.doll-venv"; do
  if [ -n "$cand" ] && [ -x "$cand/bin/python" ]; then VENV="$cand"; break; fi
done

export PATH="/opt/homebrew/bin:/Library/TeX/texbin:$PATH"
# "//" = cerca anche nelle sottocartelle; il ":" finale aggiunge i percorsi standard di TeX
export TEXINPUTS=".:$SKILL_DIR/kit/pdf//:${TEXINPUTS:-}"

cd "$DIR"
INIZIO=$(date +%s)
if ! latexmk -pdf -interaction=nonstopmode -halt-on-error -silent dispensa.tex >/dev/null 2>&1; then
  echo "COMPILAZIONE FALLITA. Errori da $DIR/dispensa.log:" >&2
  if grep -q '^!' dispensa.log 2>/dev/null; then
    grep -n -A7 '^!' dispensa.log | head -60 >&2
  else
    tail -30 dispensa.log >&2 2>/dev/null || echo "(nessun log: latexmk/pdflatex non trovati?)" >&2
  fi
  rm -f dispensa.aux dispensa.out dispensa.fls dispensa.fdb_latexmk dispensa.toc
  exit 1
fi
FINE=$(date +%s)

# testo che esce dal margine (> 1pt): da sistemare
OVER=$(grep -E '^Overfull \\hbox \(([1-9][0-9]*\.|[1-9])' dispensa.log | sort | uniq -c || true)
[ -n "$OVER" ] && { echo "ATTENZIONE: righe che escono dal margine (numero di riga del .tex):"; echo "$OVER"; }
UNDEF=$(grep -E "Reference .* undefined|Citation .* undefined" dispensa.log | head -5 || true)
[ -n "$UNDEF" ] && { echo "ATTENZIONE: riferimenti non definiti:"; echo "$UNDEF"; }

# didattica (guide/didattica.md): i riquadri che non devono mancare
MANCA=""
for amb in obiettivi previsione preconcetto autoverifica ripasso; do
  grep -q "begin{$amb}" dispensa.tex || MANCA="$MANCA $amb"
done
grep -q '\\vuoto' dispensa.tex || MANCA="$MANCA esercizio-da-completare(\\vuoto)"
[ -n "$MANCA" ] && echo "ATTENZIONE didattica: mancano i riquadri:$MANCA (vedi guide/didattica.md)"

latexmk -c dispensa.tex >/dev/null 2>&1
rm -f dispensa.synctex.gz

if [ -n "${VENV:-}" ]; then
  "$VENV/bin/python" "$SKILL_DIR/scripts/pdf_anteprima.py" "$DIR/dispensa.pdf" $PAGINE || echo "(anteprima non riuscita)"
else
  echo "(venv non trovato: niente anteprima PNG)"
fi
echo "compilato in $((FINE - INIZIO)) s"
echo "$DIR/dispensa.pdf"
