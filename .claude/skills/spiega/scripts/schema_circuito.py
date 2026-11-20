#!/usr/bin/env python3
"""Schema di un circuito (SVG/PDF, stile europeo) e analisi ESATTA da una netlist in formato lcapy.

Uso:
  .venv/bin/python schema_circuito.py "<netlist>" [--svg out.svg] [--pdf out.pdf] [--png out.png]
                                      [--analisi] [--thevenin A B] [--json] [--senza-nodi]
                                      [--motore auto|schemdraw|lcapy]
  La netlist si passa come stringa, oppure con  -f circuito.net  (o "-" per lo stdin).

NETLIST (formato lcapy, simile a SPICE): un componente per riga, oppure separati da ";".
  R1 1 2 2        resistore da 2 Ω tra i nodi 1 e 2   (anche simbolico: "R1 1 2 R")
  L1 2 3 10e-3    induttore (H)       C1 3 0 1e-6   condensatore (F)
  V1 1 0 10       generatore di tensione: + sul PRIMO nodo (1), - sul secondo
  I1 3 0 2        generatore di corrente: la freccia punta verso il PRIMO nodo (2 A entrano nel nodo 3)
  W 2 4           filo;  E/F/G/H generatori pilotati (sintassi lcapy: E1 3 0 1 2 5 = 5*(V1-V2))
  Il nodo 0 è la massa (obbligatorio per i potenziali). Valori: numeri (anche 2.2e3), simboli, {espressioni}.
  Generatori in alternata: "V1 1 0 ac 10" (fasore); il risultato resta in funzione di omega_0.

DISEGNO (--svg / --pdf / --png):
  motore "schemdraw" (default se il circuito è "a scala"): disegno automatico, nessun suggerimento da dare.
    A scala = i componenti tra nodi diversi da 0 formano una catena (1-2-3-...), tutti gli altri vanno
    da un nodo della catena a 0 (verticali, verso la barra di massa). È il caso tipico degli esercizi
    serie-parallelo, partitori, reti a scala, circuiti per Thevenin.
  motore "lcapy" (circuitikz via LaTeX, stile europeo): per QUALSIASI circuito (ponti, maglie, generatori
    pilotati), ma servono i suggerimenti di disegno lcapy dopo il componente, separati da ";" sulla
    stessa riga:  "R1 1 2 2; right",  "R2 2 0 3; down",  "W 0 0_2; right"  (right/left/up/down,
    anche "right=1.5"). Nodi "0_1", "0_2", ... sono punti diversi del disegno ma lo stesso nodo 0 (vale per
    ogni nodo: "2_a" = nodo 2). Con la netlist su una riga sola i suggerimenti vanno messi dopo ";" come
    elementi a sé: "R1 1 2 2; right; R2 2 0 3; down" (una parola minuscola = suggerimento del precedente).
  "auto" (default): schemdraw se il circuito è a scala, altrimenti lcapy se ci sono suggerimenti,
  altrimenti errore con l'indicazione di cosa aggiungere.
  Nomi dei nodi sul disegno (servono per leggere l'analisi); --senza-nodi li toglie.
  Nel disegno lcapy (europeo) il generatore di tensione è il cerchio con la linea, senza "+": il + è
  il primo nodo della riga. Esempio completo con i suggerimenti: il ponte di Wheatstone qui sotto.

ANALISI (--analisi, --thevenin A B): calcolo simbolico con lcapy/SymPy (frazioni esatte, niente
  arrotondamenti), più il valore decimale. Stampa:
  - potenziale di ogni nodo rispetto a 0;
  - per ogni componente X (nodi a b): V_X = V(a) - V(b), I_X = corrente DENTRO X da a verso b,
    P_X = V_X * I_X potenza ASSORBITA (convenzione degli utilizzatori: negativa = erogata);
  - Thevenin tra A e B: V_th = V(A) - V(B) a vuoto, R_th (o Z_th(s)), I_Norton = V_th / R_th.
  Circuiti in continua: numeri. Con L e C in continua vale il regime (L corto, C aperto).
  Altrimenti (ac, simboli) stampa le espressioni di lcapy. --json: stessa cosa in JSON.

Esempi:
  schema_circuito.py "V1 1 0 10; R1 1 2 2; R2 2 0 3" --svg partitore.svg --analisi --thevenin 2 0
  schema_circuito.py -f ponte.net --motore lcapy --pdf ponte.pdf
Ponte di Wheatstone (non a scala, motore lcapy):
  V1 1 0 12; down=2
  W 1 1_2; right
  R1 1_2 2 4; down
  R2 2 0_2 6; down
  W 0 0_2; right
  W 1_2 1_3; right=2
  R3 1_3 3 3; down
  R4 3 0_3 6; down
  W 0_2 0_3; right=2
  R5 2 3 5; right=2
  -> V(2) = 348/47 V, V(3) = 368/47 V, Thevenin tra 2 e 3: V_th = -20/47 V, R_th = 110/47 Ω (verificati a mano).
Nelle pagine: <img src="...svg"> o incolla il contenuto SVG; nelle dispense: \\includegraphics del PDF.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

DUE_TERMINALI = set("RLCVIWZ")
UNITA = {"R": "Ω", "L": "H", "C": "F", "V": "V", "I": "A", "Z": "Ω"}
PREFISSI = [(1e9, "G"), (1e6, "M"), (1e3, "k"), (1, ""), (1e-3, "m"), (1e-6, "µ"), (1e-9, "n"), (1e-12, "p")]
PAROLE_CHIAVE = {"dc", "ac", "step", "s"}


# ----------------------------------------------------------------------------- netlist
class Componente:
    def __init__(self, riga: str):
        self.riga = riga.strip()
        self.suggerimenti: list[str] = []
        t = self.riga.split()
        self.nome = t[0]
        self.tipo = self.nome[0].upper()
        if self.tipo in DUE_TERMINALI:
            self.nodi = t[1:3]
            self.valore = " ".join(t[3:])
        else:                                   # pilotati e altro: lasciati a lcapy
            self.nodi = t[1:5] if self.tipo in "EG" else t[1:3]
            self.valore = " ".join(t[len(self.nodi) + 1:])

    def lcapy(self) -> str:
        return self.riga + ("; " + ", ".join(self.suggerimenti) if self.suggerimenti else "")


def leggi_netlist(testo: str) -> list[Componente]:
    """Componenti separati da a-capo o ';'. Un pezzo che inizia in minuscolo è un suggerimento di disegno."""
    comp: list[Componente] = []
    for riga in testo.splitlines():
        riga = riga.split("#")[0].strip() if not riga.lstrip().startswith("#") else ""
        for pezzo in (p.strip() for p in riga.split(";")):
            if not pezzo:
                continue
            if re.match(r"^[A-Za-z][A-Za-z0-9_]*\s+\S+\s+\S+", pezzo) and pezzo[0].isupper():
                comp.append(Componente(pezzo))
            elif comp:
                comp[-1].suggerimenti += [s.strip() for s in pezzo.split(",") if s.strip()]
            else:
                sys.exit(f"Netlist: '{pezzo}' non è un componente (es. 'R1 1 2 10').")
    if not comp:
        sys.exit("Netlist vuota.")
    return comp


def circuito_lcapy(comp: list[Componente]):
    from lcapy import Circuit
    return Circuit("\n".join(c.lcapy() for c in comp))


# ----------------------------------------------------------------------------- etichette
def pedice(nome: str) -> str:
    m = re.match(r"^([A-Za-z])_?(.*)$", nome)
    lettera, resto = m.group(1), m.group(2)
    return f"${lettera}_{{{resto}}}$" if resto else f"${lettera}$"


def numero_si(x: float, unita: str) -> str:
    """Valore con prefisso SI e virgola decimale, in mathtext: 2200 -> $2{,}2\\,\\mathrm{k\\Omega}$."""
    u = {"Ω": r"\Omega"}.get(unita, unita)
    f, p = next(((f, p) for f, p in PREFISSI if abs(x) >= f * 0.9999), (1, "")) if x else (1, "")
    s = f"{x / f:.3g}".replace(".", "{,}")
    p = {"µ": r"\mu "}.get(p, p)
    return rf"${s}\,\mathrm{{{p}{u}}}$"


def etichetta(c: Componente) -> str:
    if c.tipo == "W":
        return ""
    val = [t for t in c.valore.split() if t.lower() not in PAROLE_CHIAVE]
    testo = pedice(c.nome)
    if not val:
        return testo
    v = val[0].strip("{}")
    try:
        return testo + "\n" + numero_si(float(v), UNITA.get(c.tipo, ""))
    except ValueError:
        return testo + "\n" + (pedice(v) if re.match(r"^[A-Za-z]\w*$", v) else f"${v}$")


# ----------------------------------------------------------------------------- disegno: rete a scala
def catena_a_scala(comp: list[Componente]):
    """Se il circuito è a scala restituisce (ordine dei nodi, serie per coppia, derivazioni per nodo)."""
    if any(c.tipo not in DUE_TERMINALI for c in comp):
        return None
    serie, derivazioni, adiacenti = {}, {}, {}
    for c in comp:
        a, b = c.nodi
        if a == b:
            return None
        if "0" in (a, b):
            n = b if a == "0" else a
            derivazioni.setdefault(n, []).append(c)
            adiacenti.setdefault(n, set())
        else:
            k = frozenset((a, b))
            if k in serie:                       # due componenti in parallelo tra nodi interni
                return None
            serie[k] = c
            adiacenti.setdefault(a, set()).add(b)
            adiacenti.setdefault(b, set()).add(a)
    if not adiacenti:
        return None
    if any(len(v) > 2 for v in adiacenti.values()):
        return None
    estremi = [n for n, v in adiacenti.items() if len(v) <= 1]
    if not estremi:                              # anello di serie: non è una scala
        return None
    # parte dall'estremo con un generatore (sorgente a sinistra), altrimenti dal primo
    def ha_generatore(n):
        return any(c.tipo in "VI" for c in derivazioni.get(n, []))
    estremi.sort(key=lambda n: (not ha_generatore(n), n))
    ordine, prec = [estremi[0]], None
    while True:
        succ = [m for m in adiacenti[ordine[-1]] if m != prec]
        if not succ:
            break
        prec = ordine[-1]
        ordine.append(succ[0])
    if len(ordine) != len(adiacenti):            # pezzi scollegati
        return None
    return ordine, serie, derivazioni


def disegna_schemdraw(comp, scala, uscite: dict, nodi: bool) -> None:
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["mathtext.fontset"] = "cm"
    import schemdraw
    import schemdraw.elements as elm
    elm.style(elm.STYLE_IEC)                     # resistori a rettangolo (norma IEC/europea)
    ordine, serie, derivazioni = scala
    H, L, PASSO = 3.0, 3.0, 2.4
    d = schemdraw.Drawing(show=False)
    d.config(unit=L, fontsize=13, lw=1.4)

    def elemento(c: Componente):
        # V: cerchio semplice; i segni + e - li mettiamo noi dritti (quelli di SourceV ruotano col componente)
        return {"R": elm.Resistor, "Z": elm.Resistor, "L": elm.Inductor2, "C": elm.Capacitor,
                "V": elm.Source, "I": elm.SourceI, "W": elm.Line}[c.tipo]()

    def posa(e, a, b, et):
        """Mette e da a a b con i metodi di direzione (.to() su SourceV va nel verso sbagliato)."""
        e = e.at(a)
        if a[0] == b[0]:
            e = (e.down() if a[1] > b[1] else e.up()).length(abs(a[1] - b[1]))
            loc = "bottom"                       # etichetta a destra dei componenti verticali
        else:
            e = (e.right() if b[0] > a[0] else e.left()).length(abs(b[0] - a[0]))
            loc = "top"                          # sopra (schemdraw tiene dritte le etichette)
        e = e.label(et, loc=loc, ofst=0.25) if et else e
        if isinstance(e, elm.Source) and not isinstance(e, elm.SourceI):
            import numpy as np
            A, B = np.array(a, float), np.array(b, float)
            m, u = (A + B) / 2, (B - A) / np.linalg.norm(B - A)
            m = m - 0.1          # elm.Label sposta il testo di ~(+0,1; +0,1): lo si compensa
            d.add(elm.Label().right().at(tuple(m + 0.27 * u)).label("+", fontsize=16, loc="center", halign="center", valign="center", ofst=0))  # + alla fine
            d.add(elm.Label().right().at(tuple(m - 0.27 * u)).label("−", fontsize=16, loc="center", halign="center", valign="center", ofst=0))
        return e

    alto, basso = [], []                         # punti delle barre: (x, ha_componente)
    x, nodo_x = 0.0, {}
    for k, n in enumerate(ordine):
        xs = []
        for j, c in enumerate(derivazioni.get(n, [])):
            if j:
                x += PASSO
            # verticale tra il nodo n (in alto) e 0 (in basso). Generatori: si disegnano dal secondo nodo al
            # primo, perche' in schemdraw il "+" di V e la punta della freccia di I stanno alla FINE
            # (lcapy: V ha il + sul primo nodo, I spinge la corrente nel primo nodo)
            dal_nodo = (c.nodi[0] == n) != (c.tipo in "VI")
            inizio, fine = ((x, H), (x, 0)) if dal_nodo else ((x, 0), (x, H))
            d += posa(elemento(c), inizio, fine, etichetta(c))
            xs.append(x)
        if not xs:
            xs = [x]
        nodo_x[n] = (xs[0], xs[-1])
        for xx in xs:
            alto.append((xx, bool(derivazioni.get(n))))
            if derivazioni.get(n):
                basso.append((xx, True))
        if k + 1 < len(ordine):
            c = serie[frozenset((n, ordine[k + 1]))]
            e = elemento(c)
            avanti = (c.nodi[0] == n) != (c.tipo in "VI")   # da sinistra a destra? (generatori: vedi sopra)
            a, b = (xs[-1], H), (xs[-1] + L, H)
            d += posa(e, a if avanti else b, b if avanti else a, etichetta(c))
            x = xs[-1] + L
    # barre: in alto i fili tra le derivazioni dello stesso nodo, in basso la massa
    for n in ordine:
        x0, x1 = nodo_x[n]
        if x1 > x0:
            d += elm.Line().at((x0, H)).to((x1, H))
    # estremi senza derivazione: morsetti aperti (porta), con il morsetto di massa sotto
    morsetti = [nodo_x[n][0] for n in (ordine[0], ordine[-1]) if not derivazioni.get(n)]
    xb = sorted({p for p, _ in basso} | set(morsetti))
    if len(xb) > 1:
        d += elm.Line().at((xb[0], 0)).to((xb[-1], 0))
    for xm in morsetti:
        d += elm.Dot(open=True).at((xm, H))
        d += elm.Dot(open=True).at((xm, 0))
    # pallini nei nodi dove si incontrano almeno 3 conduttori
    xt = sorted({p for p, _ in alto})
    for i, (xx, deriv) in enumerate(sorted(set(alto))):
        if xx in morsetti:
            continue
        gradi = (i > 0) + (i < len(xt) - 1) + deriv
        if gradi >= 3:
            d += elm.Dot().at((xx, H))
    for i, xx in enumerate(xb):
        if xx in morsetti:
            continue
        if (i > 0) + (i < len(xb) - 1) + 1 >= 3:
            d += elm.Dot().at((xx, 0))
    if xb:
        d += elm.Ground().at((xb[0], 0))
    if nodi:
        for n in ordine:
            d += elm.Label().at((nodo_x[n][0] - 0.3, H + 0.3)).label(n, fontsize=13, color="#2b6cb0")
        if xb:
            d += elm.Label().at((xb[-1] + 0.35, -0.05)).label("0", fontsize=13, color="#2b6cb0")
    for fmt, p in uscite.items():
        d.save(str(p), dpi=200) if fmt == "png" else d.save(str(p))


def disegna_lcapy(comp, uscite: dict, nodi: bool) -> None:
    import os
    import tempfile
    os.environ["PATH"] = "/opt/homebrew/bin:/Library/TeX/texbin:" + os.environ.get("PATH", "")
    cct = circuito_lcapy(comp)
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / "schema.pdf"
        cct.draw(str(pdf), style="european", draw_nodes="connections",
                 label_nodes="primary" if nodi else False, label_values=True, label_ids=True)
        import pymupdf
        doc = pymupdf.open(str(pdf))
        for fmt, p in uscite.items():
            if fmt == "pdf":
                Path(p).write_bytes(pdf.read_bytes())
            elif fmt == "svg":
                Path(p).write_text(doc[0].get_svg_image(text_as_path=True))
            elif fmt == "png":
                doc[0].get_pixmap(dpi=200).save(str(p))


# ----------------------------------------------------------------------------- analisi
def num(e):
    try:
        return float(e)
    except (TypeError, ValueError):
        return None


def valore(q):
    """(esatto, decimale) di una grandezza lcapy: in continua un numero (o un'espressione nei simboli),
    altrimenti l'espressione di lcapy (fasore o trasformata) e decimale None."""
    import sympy as sp
    if getattr(q, "is_dc", False):
        dc = q.dc
        e = sp.simplify(sp.sympify(dc.sympy if hasattr(dc, "sympy") else dc))
        if e.is_number:
            e = sp.nsimplify(e, rational=True)
        SIMBOLI[str(e)] = e                    # per rifare i conti con gli stessi simboli (con le ipotesi di lcapy)
        return str(e), num(e)
    return str(q), None


SIMBOLI: dict = {}


def expr(testo):
    import sympy as sp
    return SIMBOLI.get(testo, sp.sympify(testo))


def fmt(esatto, dec, unita):
    if dec is None:
        return f"{esatto} {unita}"
    d = f"{dec:.6g}"
    return f"{esatto} {unita}" if esatto in (d, f"{dec:g}") else f"{esatto} = {d} {unita}"


def analisi(comp, thevenin, come_json: bool) -> None:
    import sympy as sp
    cct = circuito_lcapy(comp)
    if not any("0" in c.nodi for c in comp):
        sys.exit("Manca il nodo 0 (massa): serve per i potenziali.")
    nodi = sorted({n for c in comp for n in c.nodi if n != "0" and "_" not in n}, key=lambda s: (len(s), s))
    out = {"nodi": {}, "componenti": {}, "thevenin": None}
    for n in nodi:
        out["nodi"][n] = valore(cct[n].V)
    for c in comp:
        if c.tipo == "W":
            continue
        el = cct[c.nome]
        v, i = valore(el.V), valore(el.I)
        p = (None, None)
        if getattr(el.V, "is_dc", False) and getattr(el.I, "is_dc", False):
            pe = sp.simplify(expr(v[0]) * expr(i[0]))
            p = (str(pe), num(pe))
        out["componenti"][c.nome] = {"nodi": c.nodi, "V": v, "I": i, "P_assorbita": p}
    if thevenin:
        a, b = thevenin
        T = cct.thevenin(a, b)
        vth = valore(T.Voc)
        Z = T.Z
        zs = sp.sympify(Z.sympy if hasattr(Z, "sympy") else str(Z))
        s = next((x for x in zs.free_symbols if x.name == "s"), None)
        if s is not None:                       # c'e' L o C: impedenza in s, in continua Z(0)
            rexpr = sp.simplify(sp.limit(zs, s, 0))
            rth = (f"Z(s) = {sp.simplify(zs)}; in continua R_th = Z(0) = {rexpr}", num(rexpr))
        else:
            rexpr = sp.simplify(zs)
            if rexpr.is_number:
                rexpr = sp.nsimplify(rexpr, rational=True)
            rth = (str(rexpr), num(rexpr))
        inor = (None, None)
        if getattr(T.Voc, "is_dc", False) and rexpr != 0 and rexpr.is_finite is not False:
            ie = sp.simplify(expr(vth[0]) / rexpr)
            inor = (str(ie), num(ie))
        out["thevenin"] = {"tra": [a, b], "V_th": vth, "R_th": rth, "I_norton": inor}
    if come_json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    print("POTENZIALI DEI NODI (rispetto al nodo 0)")
    for n, (e, d) in out["nodi"].items():
        print(f"  V({n}) = {fmt(e, d, 'V')}")
    print("COMPONENTI  (V = V(a) - V(b); I dentro il componente da a verso b; P assorbita = V*I)")
    for nome, r in out["componenti"].items():
        a, b = (n.split("_")[0] or n for n in r["nodi"][:2])   # "0_2" e' il nodo 0
        riga = f"  {nome} [{a}->{b}]:  V = {fmt(*r['V'], 'V')},  I = {fmt(*r['I'], 'A')}"
        if r["P_assorbita"][0] is not None:
            riga += f",  P = {fmt(*r['P_assorbita'], 'W')}"
        print(riga)
    if out["thevenin"]:
        t = out["thevenin"]
        print(f"THEVENIN tra {t['tra'][0]} e {t['tra'][1]}")
        print(f"  V_th = {fmt(*t['V_th'], 'V')}")
        print(f"  R_th = {fmt(*t['R_th'], 'Ω')}")
        if t["I_norton"][0] is not None:
            print(f"  I_N  = V_th/R_th = {fmt(*t['I_norton'], 'A')}")


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("netlist", nargs="?", help="netlist (componenti separati da a-capo o ';')")
    ap.add_argument("-f", "--file", help="file con la netlist ('-' = stdin)")
    ap.add_argument("--svg"); ap.add_argument("--pdf"); ap.add_argument("--png")
    ap.add_argument("--analisi", action="store_true")
    ap.add_argument("--thevenin", nargs=2, metavar=("A", "B"))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--senza-nodi", action="store_true")
    ap.add_argument("--motore", choices=["auto", "schemdraw", "lcapy"], default="auto")
    a = ap.parse_args()
    if a.file:
        testo = sys.stdin.read() if a.file == "-" else Path(a.file).read_text(encoding="utf-8")
    elif a.netlist:
        testo = a.netlist
    else:
        ap.print_help()
        sys.exit(2)
    comp = leggi_netlist(testo)
    uscite = {k: Path(v).resolve() for k, v in (("svg", a.svg), ("pdf", a.pdf), ("png", a.png)) if v}
    if uscite:
        scala = catena_a_scala(comp)
        suggeriti = any(c.suggerimenti for c in comp)
        motore = a.motore
        if motore == "auto":
            motore = "schemdraw" if scala and not suggeriti else "lcapy" if suggeriti else None
        if motore is None:
            sys.exit("Il circuito non è a scala: per disegnarlo aggiungi i suggerimenti lcapy dopo ogni "
                     "componente (es. 'R1 1 2 2; right' 'R2 2 0 3; down') e rilancia (motore lcapy).")
        if motore == "schemdraw":
            if not scala:
                sys.exit("schemdraw disegna solo circuiti a scala con componenti a due terminali: usa --motore lcapy.")
            disegna_schemdraw(comp, scala, uscite, not a.senza_nodi)
        else:
            disegna_lcapy(comp, uscite, not a.senza_nodi)
        for p in uscite.values():
            print(f"schema ({motore}): {p}")
    if a.analisi or a.thevenin:
        analisi(comp, a.thevenin, a.json)
    if not uscite and not (a.analisi or a.thevenin):
        print("Niente da fare: aggiungi --svg/--pdf/--png e/o --analisi, --thevenin A B.")


if __name__ == "__main__":
    main()
