#!/usr/bin/env bash
# Uso: render.sh <scena.py> [bozza|finale]
#   bozza  -> 480p15, veloce (per il verificatore)
#   finale -> 720p30; 1080p da solo se piano.md accanto alla scena dice "**Impegno**: approfondito"
#             (FINALE_HD=1 lo forza, FINALE_HD=0 lo esclude)
# Stampa sull'ultima riga il percorso dell'mp4 prodotto.
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCENA="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
MODO="${2:-bozza}"
OUT_DIR="$(dirname "$SCENA")"

# Trova il venv: variabile DOLL_VENV, poi la repo, poi ~/.doll-venv
for cand in "${DOLL_VENV:-}" "$SKILL_DIR/../../../.venv" "$HOME/.doll-venv"; do
  if [ -n "$cand" ] && [ -x "$cand/bin/python" ]; then VENV="$cand"; break; fi
done
[ -n "${VENV:-}" ] || { echo "ERRORE: venv con manim non trovato. Esegui setup.sh" >&2; exit 2; }

export PYTHONPATH="$SKILL_DIR/kit:${PYTHONPATH:-}"
export PATH="/opt/homebrew/bin:/Library/TeX/texbin:$PATH"
if [ -z "${FINALE_HD:-}" ] && [ -f "$OUT_DIR/piano.md" ] && \
   grep -Eiq 'Impegno[*[:space:]]*[:：][*[:space:]`]*approfondito' "$OUT_DIR/piano.md"; then
  FINALE_HD=1   # impegno approfondito: il finale e' in 1080p
fi
[ "${FINALE_HD:-0}" = 1 ] && [ "$MODO" = finale ] && MODO_HD=1
case "$MODO" in
  bozza)  Q="-ql" ;;
  finale) Q="-qm" ;;   # 720p30: buon compromesso qualità/tempo sull'M1
  *) echo "modo sconosciuto: $MODO" >&2; exit 2 ;;
esac
[ "${MODO_HD:-0}" = 1 ] && Q="-qh"

cd "$OUT_DIR"
LOG="$OUT_DIR/render_$MODO.log"
# La cache di Manim (media/) sta fuori dal progetto, in una cartella temporanea per ogni progetto:
# così in progetto/ restano solo i sorgenti.
CACHE="${TMPDIR:-/tmp}/doll-manim/$(printf '%s' "$OUT_DIR" | shasum | cut -c1-16)"
rm -rf "$CACHE/videos"   # così sotto c'è solo il video di QUESTO render
if ! "$VENV/bin/python" -m manim $Q --disable_caching --media_dir "$CACHE" "$SCENA" Esercizio >"$LOG" 2>&1; then
  echo "RENDER FALLITO. Ultime righe del log ($LOG):" >&2
  grep -v '^\s*$' "$LOG" | tail -40 >&2
  exit 1
fi
MP4="$(find "$CACHE/videos" -name 'Esercizio.mp4' -not -path '*partial*' | head -1)"
DEST="$OUT_DIR/$MODO.mp4"
cp "$MP4" "$DEST"
echo "$DEST"
