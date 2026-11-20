#!/usr/bin/env python3
"""Rende la skill usabile anche da Codex (ChatGPT). Da rilanciare dopo ogni modifica agli agenti.

Uso:  .venv/bin/python .claude/skills/spiega/scripts/sync_codex.py     (dalla root della repo)

- .agents/skills/spiega  -> link simbolico a .claude/skills/spiega (Codex segue i link);
- .claude/agents/<nome>.md -> .codex/agents/<nome_con_underscore>.toml
  (name, description, developer_instructions = il testo dell'agente).
Una sola fonte di verità: si modificano SOLO i file in .claude/.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / ".claude" / "agents"
DST = ROOT / ".codex" / "agents"
NOTA = ("Nota per Codex: dove il testo dice 'subagente' o 'Agent tool', usa gli agenti personalizzati di "
        "Codex con lo stesso nome ma con il trattino basso (es. esperto_analisi). I percorsi sono relativi "
        "alla root della repo.\n\n")


def toml_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    link = ROOT / ".agents" / "skills" / "spiega"
    link.parent.mkdir(parents=True, exist_ok=True)
    if not link.exists():
        link.symlink_to(Path("../../.claude/skills/spiega"))
    DST.mkdir(parents=True, exist_ok=True)
    for vecchio in DST.glob("*.toml"):
        vecchio.unlink()
    for md in sorted(SRC.glob("*.md")):
        testo = md.read_text()
        m = re.match(r"---\n(.*?)\n---\n(.*)", testo, re.S)
        if not m:
            sys.exit(f"{md}: manca l'intestazione YAML")
        meta = dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M))
        corpo = NOTA + m.group(2).strip() + "\n"
        if "'''" in corpo:
            sys.exit(f"{md}: contiene ''' (non ammesso nelle stringhe TOML letterali)")
        nome = meta["name"].replace("-", "_")
        (DST / f"{nome}.toml").write_text(
            f"name = {toml_str(nome)}\n"
            f"description = {toml_str(meta['description'])}\n"
            f"developer_instructions = '''\n{corpo}'''\n")
        print(f"{md.name} -> .codex/agents/{nome}.toml")
    print(f"skill: {link.relative_to(ROOT)} -> {link.readlink()}")


if __name__ == "__main__":
    main()
