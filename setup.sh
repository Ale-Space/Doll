#!/usr/bin/env bash
# Setup per la skill spiega (macOS, Apple Silicon o Intel).
# Uso: ./setup.sh     (dalla root della repo)
set -euo pipefail
cd "$(dirname "$0")"

say() { printf '\n\033[1;33m==> %s\033[0m\n' "$*"; }

command -v brew >/dev/null || { echo "Serve Homebrew: https://brew.sh"; exit 1; }

say "Python 3.12"
command -v python3.12 >/dev/null || brew install python@3.12
PY="$(command -v python3.12)"

say "LaTeX + dvisvgm (servono a MathTex)"
# dvisvgm da Homebrew porta con sé anche una TeX Live completa: niente sudo, niente tlmgr.
command -v dvisvgm >/dev/null || brew install dvisvgm
# Se hai solo BasicTeX, verifica che i pacchetti di Manim ci siano:
kpsewhich standalone.cls >/dev/null || { echo "Manca standalone.cls: esegui 'brew install texlive'"; exit 1; }

say "Ambiente virtuale .venv con Manim"
[ -d .venv ] || "$PY" -m venv .venv
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q "manim>=0.19" sympy scipy numpy matplotlib pymunk shapely pymupdf playwright
# manim-physics dichiara manim<0.19 ma funziona con le versioni nuove: --no-deps
.venv/bin/python -m pip install -q --no-deps manim-physics
# schemi e analisi esatta dei circuiti (scripts/schema_circuito.py), dinamica dei qubit (templates/quantistica.py)
# (python -m pip: funziona anche se la cartella del venv e' stata spostata)
.venv/bin/python -m pip install -q lcapy schemdraw qutip

say "Chrome (per il controllo automatico delle pagine interattive)"
[ -d "/Applications/Google Chrome.app" ] || echo "ATTENZIONE: installa Google Chrome, serve a web_check.py"
command -v latexmk >/dev/null || echo "ATTENZIONE: manca latexmk (dispense PDF): brew install texlive"

say "Versioni per Codex"
.venv/bin/python .claude/skills/spiega/scripts/sync_codex.py >/dev/null && echo "OK: .agents/ e .codex/ aggiornati"

say "Test di render"
TMP="$(mktemp -d)"
cat > "$TMP/prova.py" <<'EOF'
from manim import *
from manim_physics import *
class Prova(Scene):
    def construct(self):
        self.play(Write(MathTex(r"\int_0^1 x^2\,dx = \tfrac{1}{3}")))
EOF
( cd "$TMP" && "$OLDPWD/.venv/bin/manim" -ql --disable_caching prova.py Prova >/dev/null 2>&1 ) \
  && echo "OK: Manim + LaTeX funzionano" \
  || { echo "ERRORE nel render di prova. Lancia a mano: .venv/bin/manim -ql $TMP/prova.py Prova"; exit 1; }
rm -rf "$TMP"

say "Fatto"
echo "Apri Claude Code (claude) o Codex (codex) in questa cartella e scrivi, per esempio:"
echo "   /spiega il teorema di Lagrange      (Claude Code)"
echo "   \$spiega il teorema di Lagrange      (Codex)"
echo "oppure allega la foto di un esercizio e scrivi /spiega"
