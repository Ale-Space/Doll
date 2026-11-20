"""Kit per CIRCUITI ELETTRICI animati (Elettrotecnica): schema IEC, risolutore esatto, correnti che scorrono.

Stile dei video Doll (guide/manim.md): sfondo nero, palette di doll_kit, Scene 2D. Va usato INSIEME a doll_kit:
    from doll_kit import *
    from circuiti_kit import *
Esempio completo, da copiare: templates/circuito.py (due maglie, legge dei nodi, Thévenin).

=====================================================================================================
1. DESCRIVERE IL CIRCUITO (su una griglia; 1 cella = `passo` unità Manim, di solito 1,1-1,5)
=====================================================================================================
    c = Circuito()
    c.nodo("0", (2, 0), massa=True)          # nodo di riferimento (potenziale 0), con il simbolo di massa
    c.nodo("A", (0, 3), etichetta="A")       # etichetta: nome scritto vicino al nodo (facoltativa)
    c.nodo("B", (2, 3), etichetta="B")
    c.generatore("V1", "0", "A", 10, via=[(0, 0)])   # da "0" verso "A" il potenziale SALE di 10 V
    c.resistore("R1", "A", "B", 2)
    c.resistore("RL", "B", "0", 6, via=[(4, 3), (4, 0)])

  * Un RAMO va da un nodo `a` a un nodo `b` passando per i punti `via` (gli angoli del filo). I tratti devono
    essere orizzontali o verticali (fili ad angolo retto: il kit lo controlla). Il componente sta a metà del
    tratto più lungo (o del tratto `su=k`, 0 = il primo da `a`); il filo da `a` al componente ha il potenziale
    di `a`, quello dopo il componente il potenziale di `b`.
  * OGNI tratto di filo appartiene a UN SOLO ramo: dove si incontrano tre o più fili metti un nodo (il kit
    disegna il pallino da solo). Così i puntini su ogni filo sono la corrente vera di quel filo.
  * Verso di riferimento: la corrente I di un ramo è positiva se va da `a` a `b` DENTRO il ramo.
      resistore(n, a, b, R)          V_a - V_b = R I                       (convenzione degli utilizzatori)
      generatore(n, a, b, E)         V_b - V_a = E: il "+" è dalla parte di b; I > 0 = eroga (convenzione dei
                                     generatori). Simbolo IEC: cerchio con la linea lungo il filo, "+" vicino a b.
      generatore_corrente(n, a, b, J)  spinge J da a verso b (freccia accanto). Simbolo IEC: cerchio con la
                                     linea perpendicolare al filo.
      condensatore(n, a, b, C)       in continua è aperto (I = 0); vedi i transitori.
      induttore(n, a, b, L)          in continua è un corto circuito.
      interruttore(n, a, b, chiuso=True)   chiuso = corto, aperto = ramo tolto; .chiuso si cambia in scena.
      filo(n, a, b)                  corto circuito di cui interessa la corrente.
  * `valore` può essere un numero o un ValueTracker (o una funzione senza argomenti): il disegno si aggiorna
    dal vivo (es. un carico che varia). `etichetta=r"R_L"` sostituisce l'etichetta automatica (nome + valore);
    `etichetta=""` la toglie. `lato=UP/DOWN/LEFT/RIGHT` dice da che parte scriverla (default: verso l'esterno).

=====================================================================================================
2. RISOLVERE (analisi nodale modificata, MNA)
=====================================================================================================
    s = c.risolvi_esatto()        # SymPy, frazioni esatte: s.V["B"], s.I["R1"], s.v("R1") = V_a - V_b
    s.verifica()                  # controlla Kirchhoff ai nodi e Tellegen (somma delle potenze = 0)
    s = c.risolvi()               # float (numpy), veloce: lo usa il disegno a ogni fotogramma
    Vth, Rth = c.thevenin("B", "0", togli=["RL"])          # esatti: V a vuoto e R con i generatori spenti
    c.risolvi_esatto(valori={"RL": sp.Symbol("R_L")})      # anche simbolico
  Non serve lcapy (il kit usa solo SymPy). Se lo installi puoi usarlo per un controllo incrociato in piano.md.

  TRANSITORI DEL 1° ORDINE (un solo C o L; stesso schema, l'interruttore dice la configurazione dopo t = 0):
    c.rami["S"].chiuso = True
    tr = c.transitorio("C1", x0=0)    # x0 = v_C(0-) (o i_L(0-)), continuità
    tr.tau, tr.x0, tr.xinf             # esatti (SymPy);  tr.espressione() = x(t) con sp.Symbol("t")
    tr.x(t)                            # float;  tr.risolvi(t) = soluzione di TUTTA la rete all'istante t
  (il condensatore viene sostituito da un generatore di tensione v_C(t), l'induttore da uno di corrente i_L(t)).
  In scena:  t = ValueTracker(0);  d = DisegnoCircuito(c, soluzione=lambda: tr.risolvi(t.get_value()), vmin=0, vmax=E)
  con l'interruttore ancora aperto (c.rami["S"].chiuso = False dopo aver creato tr): finché t = 0 la rete è quella
  di prima con v_C = x0; poi d.interruttore_anima(self, "S", chiuso=True) e self.play(t.animate.set_value(5 * tau),
  rate_func=linear): i puntini rallentano e si fermano, le armature cambiano colore. Il tempo del video non è quello
  fisico: scegli la durata del play (4-6 s per 5 τ) e k_correnti adatto a correnti in mA (es. 150).

=====================================================================================================
3. DISEGNARE E ANIMARE
=====================================================================================================
    d = DisegnoCircuito(c, passo=1.4, origine=[-4, -2, 0])     # origine = dove va il punto (0, 0) della griglia
    d.mostra(self)                  # comparsa: fili che si tracciano, componenti, etichette (≈ 1,5 s)
    d.avvia_correnti(self)          # i PUNTINI partono (e da qui scorrono sempre, anche durante wait e play)
    d.accendi_potenziali(self)      # i fili si colorano con il potenziale (e i resistori sfumano)
    self.add(d.freccia_corrente("R1", dove=0.8, lato=UP))   # freccia nel verso VERO + valore dal vivo
    self.add(d.tensione("R1", lato=DOWN))                   # freccia della tensione, punta al morsetto più alto
    self.add(d.scala_potenziali(["A", "B", "0"], centro=[4.5, 0, 0], altezza=4))  # la "scala" dei potenziali
    self.play(d.animate.scale(0.7).move_to(LEFT * 3.3))     # tutto (puntini, frecce) segue il disegno
    d.pezzi("V1", "R1")             # i mobject di quei rami (per Transform, Indicate); copia: d.pezzi(...).copy()
    d.riquadro("V1", "R1")          # rettangolo tratteggiato attorno a quei rami
    d.interruttore_anima(self, "S", chiuso=True)   # la levetta ruota (e c.rami["S"].chiuso cambia)
  ATTENZIONE: pezzi() e VGroup(...) sono contenitori nuovi. Dopo un play su di essi chiama d.consolida(self) (lo
  fanno già mostra/avvia_correnti); per far sparire pezzi COPIATI usa un FadeOut per ciascuno (FadeOut di un
  contenitore toglie il contenitore, non i figli già in scena). Esempio completo dell'atto Thévenin nel template.
  Numeri nel pannello: numero_vivo(self, lambda: virgola(d.sol().I["RL"]) + " A", posizione) di doll_kit.

  CORRENTI: un puntino ogni ~0,35 celle; velocità = `k_correnti` celle/s per ampere (default 0,45: scegli k
  perché la corrente più grande vada a 0,6-1,2 celle/s), verso = segno di I. A corrente nulla i puntini si
  fermano. La quantità di puntini che entra in un nodo al secondo è quella che esce: si VEDE la legge dei nodi.

  POTENZIALI: colore del filo, non "altezze". Motivo: lo schema resta quello del libro (piano, ad angoli retti,
  leggibile), si vede tutto insieme senza muovere la camera, si combina con i puntini e con la scala laterale;
  le altezze in 3D deformano lo schema e si coprono a vicenda. La scala di colore è la metà positiva della mappa
  del kit (`colori_mappa`): scuro = potenziale basso, arancio, chiaro = alto ("più chiaro = più in alto"). La
  scala è FISSA per tutto il video (vmin, vmax): stesso colore = stesso potenziale anche fra due disegni. Nei
  resistori il colore sfuma da un capo all'altro: la caduta di tensione si vede. `scala_potenziali` aggiunge la
  barra con i nodi segnati alla loro quota (è la versione "altezze", fuori dallo schema).

Colori (solo da doll_kit): fili C_FILO (= C_TENUE) prima dei potenziali; componenti C_COMPONENTE (= C_TESTO);
corrente C_CORRENTE (= C_X); tensione C_TENSIONE (= C_Y). Le etichette dei componenti sono MathTex, i numeri
dal vivo Text (veloci): virgola decimale sempre.
"""
from __future__ import annotations

import numpy as _np
import sympy as _sp
from manim import *

from doll_kit import (C_TESTO, C_TENUE, C_X, C_Y, C_RIF, C_PUNTO, colori_mappa, barra_colori, virgola)

# ------------------------------------------------------------------ palette dei circuiti (derivata da doll_kit)
C_FILO = C_TENUE            # filo "spento" (prima di mostrare i potenziali)
C_COMPONENTE = C_TESTO      # simboli dei componenti ed etichette
C_CORRENTE = C_X            # puntini e frecce di corrente
C_TENSIONE = C_Y            # frecce e valori di tensione
C_NODO = C_PUNTO
C_SFONDO = BLACK           # = lo sfondo nero di Manim: riempie i simboli perché il filo non si veda dentro
MAPPA_BASSO, MAPPA_ALTO = 0.35, 1.55   # valori della mappa del kit usati per vmin e vmax


def colore_potenziale(v: float, vmin: float, vmax: float) -> ManimColor:
    """Colore del potenziale v sulla scala fissa [vmin, vmax] (metà positiva della mappa del kit)."""
    u = 0.0 if vmax == vmin else (float(v) - vmin) / (vmax - vmin)
    u = min(max(u, 0.0), 1.0)
    r, g, b, _ = colori_mappa(_np.array([[MAPPA_BASSO + u * (MAPPA_ALTO - MAPPA_BASSO)]]))[0, 0]
    return ManimColor.from_rgb((int(r), int(g), int(b)))


# ======================================================================================== descrizione
class Ramo:
    def __init__(self, nome, tipo, a, b, valore=None, via=(), su=None, etichetta=None, lato=None, chiuso=True):
        self.nome, self.tipo, self.a, self.b, self.valore = nome, tipo, a, b, valore
        self.via, self.su, self.etichetta, self.lato, self.chiuso = list(via), su, etichetta, lato, chiuso

    def num(self) -> float:
        v = self.valore
        if hasattr(v, "get_value"):
            return float(v.get_value())
        if callable(v):
            return float(v())
        return float(v)

    def esatto(self):
        v = self.valore
        if hasattr(v, "get_value") or callable(v):
            v = self.num()
        if isinstance(v, _sp.Basic):
            return v
        return _sp.nsimplify(v, rational=True)


_UNITA = {"R": r"\Omega", "V": r"V", "I": r"A", "C": r"F", "L": r"H"}


def _tex_num(x) -> str:
    """Numero per MathTex con la virgola decimale: 2.5 -> 2{,}5."""
    x = float(x)
    s = f"{x:.0f}" if abs(x - round(x)) < 1e-9 else f"{x:.3g}"
    return s.replace(".", "{,}").replace("-", "-")


def _tex_si(x, unita: str) -> str:
    r"""Valore con prefisso SI per MathTex: 1000 Ohm -> 1\,\mathrm{k}\Omega, 1e-4 F -> 100\,\mu\mathrm{F}."""
    x = float(x)
    for fatt, pre in ((1e3, r"\mathrm{k}"), (1, ""), (1e-3, r"\mathrm{m}"), (1e-6, r"\mu "), (1e-9, r"\mathrm{n}")):
        if abs(x) >= fatt * 0.999 or fatt == 1e-9 or x == 0:
            u = r"\Omega" if unita == r"\Omega" else rf"\mathrm{{{unita}}}"
            return rf"{_tex_num(x / fatt)}\,{pre}{u}"
    return _tex_num(x)


def _tex_nome(nome: str) -> str:
    return nome[0] + (f"_{{{nome[1:]}}}" if len(nome) > 1 else "")


class Soluzione:
    """V: potenziali dei nodi; I: correnti dei rami (da a verso b). Float o SymPy."""

    def __init__(self, circ, V, I):
        self.circ, self.V, self.I = circ, V, I

    def v(self, nome):
        """Tensione del ramo V_a - V_b."""
        r = self.circ.rami[nome]
        return self.V[r.a] - self.V[r.b]

    def potenza_assorbita(self, nome):
        return self.v(nome) * self.I[nome]

    def verifica(self, tol=1e-9):
        """Kirchhoff ai nodi e Tellegen. Solleva AssertionError se qualcosa non torna."""
        c = self.circ
        for n in c.nodi:
            s = 0
            for r in c.rami.values():
                if r.a == n:
                    s += self.I[r.nome]
                if r.b == n:
                    s -= self.I[r.nome]
            s = _sp.simplify(s) if isinstance(s, _sp.Basic) else s
            assert abs(complex(s)) < tol, f"Kirchhoff al nodo {n}: {s}"
        t = sum(self.potenza_assorbita(n) for n in c.rami)
        t = _sp.simplify(t) if isinstance(t, _sp.Basic) else t
        assert abs(complex(t)) < tol, f"Tellegen: somma delle potenze = {t}"
        return True


class Circuito:
    def __init__(self):
        self.nodi: dict[str, dict] = {}
        self.rami: dict[str, Ramo] = {}
        self.massa = None
        self._cache = {}

    # ---------------------------------------------------------------- costruzione
    def nodo(self, nome, punto, massa=False, etichetta=None, lato_etichetta=UL):
        self.nodi[nome] = dict(punto=_np.array([*punto[:2], 0.0], dtype=float), etichetta=etichetta,
                               lato=_np.array(lato_etichetta, dtype=float), massa=massa)
        if massa or self.massa is None:
            self.massa = nome
        return self

    def ramo(self, nome, tipo, a, b, valore=None, **kw):
        assert a in self.nodi and b in self.nodi, f"{nome}: nodi {a}, {b} non definiti (prima c.nodo(...))"
        r = Ramo(nome, tipo, a, b, valore, **kw)
        pts = [self.nodi[a]["punto"], *[_np.array([*p[:2], 0.0], float) for p in r.via], self.nodi[b]["punto"]]
        for p, q in zip(pts, pts[1:]):
            assert abs(p[0] - q[0]) < 1e-9 or abs(p[1] - q[1]) < 1e-9, \
                f"{nome}: il tratto {p[:2]} -> {q[:2]} non è orizzontale né verticale"
        self.rami[nome] = r
        return r

    def resistore(self, nome, a, b, R, **kw):
        return self.ramo(nome, "R", a, b, R, **kw)

    def generatore(self, nome, a, b, E, **kw):
        return self.ramo(nome, "V", a, b, E, **kw)

    def generatore_corrente(self, nome, a, b, J, **kw):
        return self.ramo(nome, "I", a, b, J, **kw)

    def condensatore(self, nome, a, b, C, **kw):
        return self.ramo(nome, "C", a, b, C, **kw)

    def induttore(self, nome, a, b, L, **kw):
        return self.ramo(nome, "L", a, b, L, **kw)

    def interruttore(self, nome, a, b, chiuso=True, **kw):
        return self.ramo(nome, "S", a, b, None, chiuso=chiuso, **kw)

    def filo(self, nome, a, b, **kw):
        kw.setdefault("etichetta", "")
        return self.ramo(nome, "W", a, b, None, **kw)

    # ---------------------------------------------------------------- MNA
    def _tipo_efficace(self, r, sost, spenti, togli):
        """("R", R) | ("V", E) | ("I", J) | ("aperto", None) per il ramo r nella configurazione richiesta."""
        if r.nome in togli:
            return "aperto", None
        if r.nome in sost:
            return sost[r.nome]
        t = r.tipo
        if t == "R":
            return "R", None
        if t == "V":
            return ("V", 0) if spenti else ("V", None)
        if t == "I":
            return ("aperto", None) if spenti else ("I", None)
        if t == "C":
            return "aperto", None
        if t in ("L", "W"):
            return "V", 0
        if t == "S":
            return ("V", 0) if r.chiuso else ("aperto", None)
        raise ValueError(t)

    def _mna(self, esatto=False, valori=None, sost=None, spenti=False, togli=(), extra=()):
        valori, sost = valori or {}, sost or {}
        nodi = [n for n in self.nodi if n != self.massa]
        ix = {n: i for i, n in enumerate(nodi)}
        rami = list(self.rami.values()) + list(extra)
        eff = [self._tipo_efficace(r, sost, spenti, togli) if not isinstance(r, tuple) else r[1] for r in rami]
        vk = [i for i, (k, _) in enumerate(eff) if k == "V"]
        nv = len(nodi) + len(vk)
        if esatto:
            A, z = _sp.zeros(nv, nv), _sp.zeros(nv, 1)
        else:
            A, z = _np.zeros((nv, nv)), _np.zeros(nv)

        def val(r, dato):
            if dato is not None:
                return dato
            if r.nome in valori:
                return valori[r.nome]
            return r.esatto() if esatto else r.num()

        def nodi_di(r):
            return (r.a, r.b) if not isinstance(r, tuple) else r[0]

        for i, (r, (k, dato)) in enumerate(zip(rami, eff)):
            a, b = nodi_di(r)
            ia, ib = ix.get(a), ix.get(b)
            if k == "R":
                g = 1 / val(r, dato)
                for p, q, s in ((ia, ia, 1), (ib, ib, 1), (ia, ib, -1), (ib, ia, -1)):
                    if p is not None and q is not None:
                        A[p, q] += s * g
            elif k == "I":
                J = val(r, dato)
                if ia is not None:
                    z[ia] -= J
                if ib is not None:
                    z[ib] += J
            elif k == "V":
                kk = len(nodi) + vk.index(i)
                E = val(r, dato)
                if ia is not None:
                    A[ia, kk] += 1
                    A[kk, ia] -= 1
                if ib is not None:
                    A[ib, kk] -= 1
                    A[kk, ib] += 1
                z[kk] = E
        if esatto:
            x = A.LUsolve(z)
            x = [_sp.nsimplify(_sp.simplify(xi)) for xi in x]
        else:
            try:
                x = _np.linalg.solve(A, z)
            except _np.linalg.LinAlgError:
                x = _np.linalg.lstsq(A, z, rcond=None)[0]   # nodi isolati (interruttore aperto): potenziale 0
        V = {n: x[ix[n]] for n in nodi}
        V[self.massa] = _sp.Integer(0) if esatto else 0.0
        I = {}
        for i, (r, (k, dato)) in enumerate(zip(rami, eff)):
            if isinstance(r, tuple):
                continue
            if k == "R":
                I[r.nome] = (V[r.a] - V[r.b]) / val(r, dato)
            elif k == "I":
                I[r.nome] = val(r, dato)
            elif k == "V":
                I[r.nome] = x[len(nodi) + vk.index(i)]
            else:
                I[r.nome] = _sp.Integer(0) if esatto else 0.0
            if esatto:
                I[r.nome] = _sp.nsimplify(_sp.simplify(I[r.nome]))
        return Soluzione(self, V, I)

    def risolvi(self, sost=None) -> Soluzione:
        """Soluzione numerica (float) con i valori ATTUALI (ValueTracker letti ora). Con cache."""
        chiave = (tuple((r.nome, r.num() if r.valore is not None else None, r.chiuso) for r in self.rami.values()),
                  tuple(sorted((k, v) for k, v in (sost or {}).items())))
        s = self._cache.get(chiave)
        if s is None:
            if len(self._cache) > 2000:
                self._cache.clear()
            s = self._cache[chiave] = self._mna(esatto=False, sost=sost)
        return s

    def risolvi_esatto(self, valori=None, sost=None) -> Soluzione:
        """Soluzione esatta (SymPy). valori = {nome_ramo: valore o simbolo} sostituisce i valori del ramo."""
        return self._mna(esatto=True, valori=valori, sost=sost)

    def thevenin(self, a, b, togli=(), esatto=True):
        """(V_th, R_th) visti dai nodi a, b dopo aver tolto i rami `togli` (il carico).

        V_th = V_a - V_b a vuoto; R_th = tensione su una corrente di prova di 1 A con i generatori spenti.
        """
        s0 = self._mna(esatto=esatto, togli=togli)
        vth = s0.V[a] - s0.V[b]
        prova = ((b, a), ("I", 1))      # 1 A iniettato nel nodo a
        s1 = self._mna(esatto=esatto, togli=togli, spenti=True, extra=[prova])
        rth = s1.V[a] - s1.V[b]
        if esatto:
            vth, rth = _sp.nsimplify(_sp.simplify(vth)), _sp.nsimplify(_sp.simplify(rth))
        return vth, rth

    def transitorio(self, nome, x0=0):
        return Transitorio(self, nome, x0)


class Transitorio:
    """Transitorio del 1° ordine di un solo condensatore (x = v_C) o induttore (x = i_L), da a verso b.

    x(t) = x(∞) + (x0 - x(∞)) e^{-t/τ},  τ = R_eq C  oppure  L / R_eq  (R_eq vista dai morsetti, generatori spenti).
    """

    def __init__(self, circ, nome, x0=0):
        self.c, self.nome = circ, nome
        r = circ.rami[nome]
        assert r.tipo in ("C", "L"), "il transitorio è per un condensatore o un induttore"
        self.tipo = r.tipo
        self.x0 = _sp.nsimplify(x0, rational=True)
        s = circ._mna(esatto=True)                      # regime: C aperto, L corto
        self.xinf = _sp.nsimplify(s.v(nome) if r.tipo == "C" else s.I[nome])
        prova = ((r.b, r.a), ("I", 1))
        s1 = circ._mna(esatto=True, spenti=True, togli=[nome], extra=[prova])
        self.Req = _sp.nsimplify(_sp.simplify(s1.V[r.a] - s1.V[r.b]))
        self.tau = _sp.nsimplify(self.Req * r.esatto() if r.tipo == "C" else r.esatto() / self.Req)
        self._f = (float(self.xinf), float(self.x0), float(self.tau))

    def espressione(self, t=None):
        t = t if t is not None else _sp.Symbol("t", nonnegative=True)
        return self.xinf + (self.x0 - self.xinf) * _sp.exp(-t / self.tau)

    def x(self, t: float) -> float:
        xi, x0, tau = self._f
        return xi + (x0 - xi) * _np.exp(-max(t, 0.0) / tau)

    def risolvi(self, t: float) -> Soluzione:
        """Tutta la rete all'istante t (C -> generatore di tensione v_C(t), L -> generatore di corrente i_L(t))."""
        x = round(self.x(t), 12)
        sost = {self.nome: ("V", -x)} if self.tipo == "C" else {self.nome: ("I", x)}
        return self.c.risolvi(sost=sost)


# ======================================================================================== simboli IEC
def _simbolo(r: Ramo, p: float):
    """(VGroup del simbolo disegnato lungo +x centrato in 0, mezza lunghezza occupata sul filo, parti utili)."""
    sw = 4
    if r.tipo == "R":
        corpo = Rectangle(width=0.62 * p, height=0.22 * p, stroke_color=C_COMPONENTE, stroke_width=sw)
        corpo.set_fill(C_SFONDO, opacity=1)
        return VGroup(corpo), 0.31 * p, dict(corpo=corpo)
    if r.tipo in ("V", "I"):
        rr = 0.24 * p
        cerchio = Circle(radius=rr, stroke_color=C_COMPONENTE, stroke_width=sw).set_fill(C_SFONDO, opacity=1)
        if r.tipo == "V":
            linea = Line(LEFT * rr, RIGHT * rr, stroke_color=C_COMPONENTE, stroke_width=sw)
            return VGroup(cerchio, linea), rr, dict()
        linea = Line(DOWN * rr, UP * rr, stroke_color=C_COMPONENTE, stroke_width=sw)
        return VGroup(cerchio, linea), rr, dict()
    if r.tipo == "C":
        g = 0.07 * p
        pa = Line(LEFT * g + DOWN * 0.22 * p, LEFT * g + UP * 0.22 * p, stroke_width=6, stroke_color=C_COMPONENTE)
        pb = Line(RIGHT * g + DOWN * 0.22 * p, RIGHT * g + UP * 0.22 * p, stroke_width=6, stroke_color=C_COMPONENTE)
        return VGroup(pa, pb), g, dict(armatura_a=pa, armatura_b=pb)
    if r.tipo == "L":
        n, rr = 4, 0.08 * p
        archi = VGroup(*[Arc(radius=rr, start_angle=PI, angle=-PI, stroke_color=C_COMPONENTE, stroke_width=sw)
                         .move_arc_center_to(RIGHT * (-n * rr + rr + 2 * rr * k)) for k in range(n)])
        return archi, n * rr, dict()
    if r.tipo == "S":
        h = 0.27 * p
        ta = Circle(radius=0.045 * p, stroke_color=C_COMPONENTE, stroke_width=3).set_fill(C_SFONDO, 1).move_to(LEFT * h)
        tb = Circle(radius=0.045 * p, stroke_color=C_COMPONENTE, stroke_width=3).set_fill(C_SFONDO, 1).move_to(RIGHT * h)
        ang = 0 if r.chiuso else 30 * DEGREES
        leva = Line(LEFT * h, LEFT * h + 2 * h * _np.array([_np.cos(ang), _np.sin(ang), 0]),
                    stroke_color=C_COMPONENTE, stroke_width=sw)
        return VGroup(leva, ta, tb), h, dict(leva=leva, perno=ta)
    if r.tipo == "W":
        return VGroup(), 0.0, dict()
    raise ValueError(r.tipo)


def _massa(p: float) -> VGroup:
    g = VGroup(Line(ORIGIN, DOWN * 0.22 * p))
    for k, w in enumerate((0.42, 0.27, 0.12)):
        y = -0.22 * p - k * 0.08 * p
        g.add(Line([-w * p / 2, y, 0], [w * p / 2, y, 0]))
    return g.set_stroke(C_COMPONENTE, 4)


# ======================================================================================== disegno
class DisegnoCircuito(VGroup):
    """Lo schema (un VGroup: si sposta e si scala con .animate) + i livelli vivi (puntini, frecce, numeri)."""

    def __init__(self, circ: Circuito, passo=1.4, origine=ORIGIN, soluzione=None, vmin=None, vmax=None,
                 k_correnti=0.45, size_etichette=32, **kw):
        super().__init__(**kw)
        self.c, self.passo0, self.k = circ, passo, k_correnti
        self.sol = soluzione or circ.risolvi
        s = self.sol()
        pot = [float(v) for v in s.V.values()]
        self.vmin = min(pot) if vmin is None else vmin
        self.vmax = max(pot) if vmax is None else vmax
        self.mix = ValueTracker(0.0)            # 0 = fili grigi, 1 = colore del potenziale
        self.orologio = ValueTracker(0.0)       # tempo dei puntini (s)
        self.velocita = ValueTracker(0.0)       # 0 = puntini fermi, 1 = scorrono
        self.orologio.add_updater(lambda m, dt: m.increment_value(dt * self.velocita.get_value()))
        o = _np.array([*origine[:2], 0.0]) if len(origine) >= 2 else _np.zeros(3)
        self.ancora0 = VectorizedPoint(o)
        self.ancora1 = VectorizedPoint(o + RIGHT * passo)
        self.add(self.ancora0, self.ancora1)
        self.size = size_etichette
        self.percorsi, self.fili, self.simboli, self.etichette, self.rami_m, self.parti = {}, {}, {}, {}, {}, {}
        self.nodi_m, self.massa_m = {}, VGroup()
        self._costruisci()

    # ---------------------------------------------------------------- geometria
    def scala(self) -> float:
        return float(_np.linalg.norm(self.ancora1.get_center() - self.ancora0.get_center())) / self.passo0

    def p(self, g) -> _np.ndarray:
        """Punto della griglia -> schermo (segue gli spostamenti del disegno)."""
        o, u = self.ancora0.get_center(), self.ancora1.get_center()
        ex = u - o
        ey = _np.array([-ex[1], ex[0], 0.0])
        return o + ex * g[0] + ey * g[1]

    def _percorso(self, r: Ramo):
        pts = [self.c.nodi[r.a]["punto"], *[_np.array([*q[:2], 0.0], float) for q in r.via], self.c.nodi[r.b]["punto"]]
        lun = [float(_np.linalg.norm(q - p)) for p, q in zip(pts, pts[1:])]
        su = r.su if r.su is not None else int(_np.argmax(lun))
        cum = _np.concatenate([[0.0], _np.cumsum(lun)])
        centro_s = cum[su] + lun[su] / 2
        return dict(pts=pts, lun=lun, cum=cum, L=cum[-1], su=su, s_c=centro_s,
                    dir=(pts[su + 1] - pts[su]) / max(lun[su], 1e-9))

    def _punto_s(self, P, s):
        """Punto (in griglia) a distanza s lungo il percorso, e direzione locale."""
        s = min(max(s, 0.0), P["L"])
        k = int(min(_np.searchsorted(P["cum"], s, side="right") - 1, len(P["lun"]) - 1))
        d = (P["pts"][k + 1] - P["pts"][k]) / max(P["lun"][k], 1e-9)
        return P["pts"][k] + d * (s - P["cum"][k]), d

    def _spezza(self, P, s0, s1):
        """Polilinea (griglia) tra le ascisse s0 < s1."""
        pts = [self._punto_s(P, s0)[0]]
        for k, c in enumerate(P["cum"][1:-1], start=1):
            if s0 < c < s1:
                pts.append(P["pts"][k])
        pts.append(self._punto_s(P, s1)[0])
        return pts

    def _centro_circuito(self):
        pts = _np.array([n["punto"] for n in self.c.nodi.values()])
        return (pts.min(0) + pts.max(0)) / 2

    def _lato(self, r: Ramo, P):
        if r.lato is not None:
            return _np.array(r.lato, float)
        d = P["dir"]
        perp = _np.array([-d[1], d[0], 0.0])
        cen = self._punto_s(P, P["s_c"])[0]
        verso = cen - self._centro_circuito()
        if abs(_np.dot(verso, perp)) < 1e-6:
            return _np.abs(perp) * (RIGHT + UP)
        return perp if _np.dot(verso, perp) > 0 else -perp

    # ---------------------------------------------------------------- costruzione dello schema
    def _costruisci(self):
        p = self.passo0
        c = self.c
        tutti_fili, tutti_simboli, tutte_et = VGroup(), VGroup(), VGroup()
        for r in c.rami.values():
            P = self._percorso(r)
            self.percorsi[r.nome] = P
            simb, h, parti = _simbolo(r, p)
            h_g = h / p
            P["h"] = h_g
            fa = self._filo(self._spezza(P, 0, P["s_c"] - h_g), r.a)
            fb = self._filo(self._spezza(P, P["s_c"] + h_g, P["L"]), r.b)
            centro_g, d = self._punto_s(P, P["s_c"])
            simb.rotate(_np.arctan2(d[1], d[0]), about_point=ORIGIN).shift(self.p(centro_g))
            lato = self._lato(r, P)
            P["lato"] = lato
            if r.tipo == "V":       # il "+" dalla parte di b, sul lato opposto all'etichetta
                piu = MathTex("+", font_size=self.size - 4, color=C_COMPONENTE)
                piu.move_to(self.p(centro_g + d * (h_g + 0.12) - lato * 0.2))
                simb.add(piu)
            if r.tipo == "I":       # freccia del verso, sul lato opposto all'etichetta
                q = centro_g - lato * 0.42
                simb.add(Arrow(self.p(q - d * 0.22), self.p(q + d * 0.22), buff=0, stroke_width=4,
                               color=C_COMPONENTE, max_tip_length_to_length_ratio=0.4, tip_length=0.14 * p))
            if r.tipo == "R":
                corpo = parti["corpo"]
                corpo.set_sheen_direction(_np.array([d[0], d[1], 0.0]))
                corpo.add_updater(lambda m, r=r: self._colora_resistore(m, r))
            if r.tipo == "C":
                for chiave, nodo in (("armatura_a", r.a), ("armatura_b", r.b)):
                    parti[chiave].add_updater(lambda m, n=nodo: m.set_stroke(color=self._colore_nodo(n)))
            et = self._etichetta(r, centro_g, lato, h_g)
            self.fili[r.nome] = (fa, fb)
            self.simboli[r.nome], self.etichette[r.nome], self.parti[r.nome] = simb, et, parti
            self.rami_m[r.nome] = VGroup(fa, fb, simb, et)
            tutti_fili.add(fa, fb)
            tutti_simboli.add(simb)
            tutte_et.add(et)
        # nodi: pallino dove si incontrano 3 o più rami; etichette; massa
        nodi_g = VGroup()
        for n, info in c.nodi.items():
            grado = sum((r.a == n) + (r.b == n) for r in c.rami.values())
            g = VGroup()
            if grado >= 3:
                pal = Dot(self.p(info["punto"]), radius=0.075 * p, color=C_FILO)
                pal.add_updater(lambda m, n=n: m.set_color(self._colore_nodo(n)))
                g.add(pal)
            if info["etichetta"]:
                g.add(MathTex(info["etichetta"], font_size=self.size, color=C_NODO)
                      .next_to(self.p(info["punto"]), info["lato"], buff=0.08))
            if info["massa"]:
                self.massa_m = _massa(p).shift(self.p(info["punto"]))
                g.add(self.massa_m)
            self.nodi_m[n] = g
            nodi_g.add(g)
        self.add(tutti_fili, tutti_simboli, tutte_et, nodi_g)
        self._gruppi = (tutti_fili, tutti_simboli, tutte_et, nodi_g)

    def _filo(self, pts_g, nodo):
        m = VMobject(stroke_color=C_FILO, stroke_width=5)
        m.set_points_as_corners([self.p(q) for q in pts_g])
        m.add_updater(lambda mm, n=nodo: mm.set_stroke(color=self._colore_nodo(n)))
        return m

    def _etichetta(self, r: Ramo, centro_g, lato, h_g):
        if r.etichetta == "":
            return VGroup()
        if r.etichetta is not None:
            tex = r.etichetta
        elif r.tipo in _UNITA and r.valore is not None and not (hasattr(r.valore, "get_value") or callable(r.valore)):
            tex = _tex_nome(r.nome) + " = " + _tex_si(r.num(), _UNITA[r.tipo])
        else:
            tex = _tex_nome(r.nome)
        m = MathTex(tex, font_size=self.size, color=C_COMPONENTE)
        larg = {"R": 0.17, "V": 0.3, "I": 0.3, "C": 0.27, "L": 0.15, "S": 0.25}.get(r.tipo, 0.15)
        m.next_to(self.p(centro_g + lato * larg), lato, buff=0.12)
        return m

    # ---------------------------------------------------------------- colori dal vivo
    def _colore_nodo(self, n):
        v = float(self.sol().V[n])
        return interpolate_color(C_FILO, colore_potenziale(v, self.vmin, self.vmax), self.mix.get_value())

    def _colora_resistore(self, m, r):
        """Riempimento sfumato dal potenziale di a a quello di b. Cambia solo il colore, mai l'opacità
        (così FadeIn/FadeOut funzionano anche mentre l'updater gira)."""
        if self.mix.get_value() <= 1e-3:
            m.set_fill(C_SFONDO)
            return
        m.set_fill([self._colore_nodo(r.a), self._colore_nodo(r.b)])

    # ---------------------------------------------------------------- comparsa e gesti
    def mostra(self, scene, run_time=1.6):
        """Comparsa: i fili si tracciano, poi i componenti e le etichette."""
        fili, simboli, et, nodi = self._gruppi
        scene.play(LaggedStart(Create(fili, lag_ratio=0.05), FadeIn(simboli, lag_ratio=0.1),
                               FadeIn(VGroup(et, nodi)), lag_ratio=0.35), run_time=run_time)
        self.consolida(scene)

    def consolida(self, scene):
        """Dopo play su pezzi del disegno: toglie i gruppi provvisori e aggiunge il disegno intero (una volta)."""
        fam = set(self.get_family())
        for m in list(scene.mobjects):
            if m is not self and set(m.get_family()) <= fam:
                scene.remove(m)
        scene.add(self)
        if self.orologio not in scene.mobjects:
            scene.add(self.orologio)

    def accendi_potenziali(self, scene, *anim, run_time=1.2):
        """I fili prendono il colore del loro potenziale (scala fissa vmin..vmax)."""
        scene.play(self.mix.animate.set_value(1.0), *anim, run_time=run_time)

    def avvia_correnti(self, scene, *anim, run_time=0.8):
        """Compaiono i puntini e cominciano a scorrere (verso e velocità dalle correnti)."""
        punti = self.correnti()
        scene.add(self.orologio)
        scene.play(FadeIn(punti), self.velocita.animate.set_value(1.0), *anim, run_time=run_time)
        return punti

    def correnti(self, spaziatura=0.36, raggio=None):
        """VGroup dei puntini (si aggiorna da solo). Velocità = k_correnti celle/s per ampere."""
        if hasattr(self, "_punti"):
            return self._punti
        raggio = raggio if raggio is not None else 0.04 * self.passo0
        stato = {n: 0.0 for n in self.c.rami}
        ult = [self.orologio.get_value()]
        gruppi = {}
        for n, P in self.percorsi.items():
            if P["L"] < 1e-6:
                continue
            nn = max(int(round(P["L"] / spaziatura)), 1)
            gruppi[n] = (nn, P["L"] / nn, VGroup(*[Dot(radius=raggio, color=C_CORRENTE) for _ in range(nn)]))
        tutti = VGroup(*[g[2] for g in gruppi.values()])
        tutti.set_z_index(3)

        def agg(m):
            t = self.orologio.get_value()
            dt, ult[0] = t - ult[0], t
            sol = self.sol()
            sc = self.scala()
            for n, (nn, d, g) in gruppi.items():
                stato[n] = (stato[n] + self.k * float(sol.I[n]) * dt) % d
                P = self.percorsi[n]
                buco = self.c.rami[n].tipo == "C"      # fra le armature non passa nessun puntino
                for j, dot in enumerate(g):
                    sj = stato[n] + j * d
                    q, _ = self._punto_s(P, sj)
                    dot.move_to(self.p(q))
                    dot.set(width=2 * raggio * sc)
                    if buco:
                        dot.set_opacity(0.0 if abs(sj - P["s_c"]) < P["h"] + 0.06 else 1.0)

        tutti.add_updater(agg)
        agg(tutti)
        self._punti = tutti
        return tutti

    def ferma_correnti(self, scene, run_time=0.6):
        scene.play(self.velocita.animate.set_value(0.0), run_time=run_time)

    # ---------------------------------------------------------------- livelli vivi: frecce e numeri
    def _testo_vivo(self, tex, fn_testo, fn_pos, colore, size):
        """MathTex fisso (nome) + Text dal vivo (numero), riposizionati a ogni fotogramma."""
        nome = MathTex(tex, font_size=size, color=colore) if tex else VGroup()
        h0 = nome.height if tex else 0.0
        t = Text(fn_testo(), font_size=size * 0.9, color=colore)
        g = VGroup(nome, t)
        base = size

        def agg(m):
            sc = self.scala()
            nuovo = Text(fn_testo(), font_size=base * 0.9 * sc, color=colore)
            m.submobjects[1].become(nuovo)
            if tex:
                m.submobjects[0].scale_to_fit_height(h0 * sc)
                m.submobjects[1].next_to(m.submobjects[0], RIGHT, buff=0.1 * sc)
            m.move_to(fn_pos(m))

        g.add_updater(agg)
        agg(g)
        g.set_z_index(4)
        return g

    def _pos_lato(self, ancora_g, lato, dist):
        """Funzione che piazza un mobject accanto al punto di griglia, dalla parte `lato`."""
        def f(m):
            P = self.p(ancora_g)
            off = _np.array(lato, float) * (dist * self.scala() * self.passo0)
            return P + off + _np.array(lato, float) * _np.array([m.width / 2, m.height / 2, 0])
        return f

    def freccia_corrente(self, nome, dove=0.5, lato=None, tex=None, reale=True, cifre=2, valore=True, prefisso=""):
        """Punta di freccia sul filo del ramo `nome` (dove = frazione del percorso da a verso b) + valore dal vivo.

        reale=True: la freccia segue il verso VERO (e il numero è |I|); reale=False: verso di riferimento a -> b e
        numero con segno. tex = nome della corrente (es. r"I_1"); valore=False per non scrivere il numero.
        prefisso="m" scrive i milliampere (correnti piccole: transitori con R in kΩ).
        """
        fatt = {"": 1.0, "m": 1e3, "µ": 1e6}[prefisso]
        P = self.percorsi[nome]
        s = dove * P["L"]
        q, d = self._punto_s(P, s)
        if lato is None:
            lato = P["lato"]
        lato = _np.array(lato, float)
        tex = tex if tex is not None else "I_{" + nome[1:] + "}" if len(nome) > 1 else "I"

        def segno():
            i = float(self.sol().I[nome])
            return 1.0 if (not reale or i >= 0) else -1.0

        def punta():
            sc = self.scala() * self.passo0
            dd = d * segno()
            c0 = self.p(q)
            ex = _np.array([dd[0], dd[1], 0.0])
            ey = _np.array([-ex[1], ex[0], 0.0])
            L = 0.13 * sc
            return Polygon(c0 + ex * L, c0 - ex * L + ey * L * 0.85, c0 - ex * L - ey * L * 0.85,
                           stroke_width=0, fill_color=C_CORRENTE, fill_opacity=1)

        frec = always_redraw(punta)
        frec.set_z_index(4)
        g = VGroup(frec)
        if valore or tex:
            def testo():
                i = float(self.sol().I[nome])
                i = (abs(i) if reale else i) * fatt
                return ("= " if tex else "") + virgola(0.0 if abs(i) < 0.5 * 10 ** -cifre else i, cifre) + f" {prefisso}A"
            g.add(self._testo_vivo(tex, testo if valore else (lambda: ""), self._pos_lato(q, lato, 0.12),
                                   C_CORRENTE, self.size))
        return g

    def tensione(self, nome, lato=None, tex=None, cifre=1, prefisso=""):
        """Freccia della tensione accanto al componente: la punta indica il morsetto a potenziale più alto
        (convenzione italiana), etichetta con il valore |V_a - V_b| dal vivo."""
        P = self.percorsi[nome]
        r = self.c.rami[nome]
        centro_g, d = self._punto_s(P, P["s_c"])
        lato = _np.array(P["lato"] if lato is None else lato, float)
        mezzo = max(P["h"] + 0.08, 0.3)

        def freccia():
            v = float(self.sol().v(nome))
            sgn = 1.0 if v >= 0 else -1.0        # v = V_a - V_b > 0: a più alto, la punta verso a
            q = centro_g + lato * 0.3
            alto, basso = self.p(q - d * mezzo * sgn), self.p(q + d * mezzo * sgn)   # d va da a verso b
            return Arrow(basso, alto, buff=0, color=C_TENSIONE, stroke_width=4, tip_length=0.16 * self.scala() * self.passo0,
                         max_tip_length_to_length_ratio=0.35)

        fr = always_redraw(freccia)
        fr.set_z_index(4)

        fatt = {"": 1.0, "m": 1e3, "k": 1e-3}[prefisso]

        def testo():
            v = abs(float(self.sol().v(nome))) * fatt
            return ("= " if tex else "") + virgola(v, cifre) + f" {prefisso}V"
        et = self._testo_vivo(tex or "", testo, self._pos_lato(centro_g + lato * 0.3, lato, 0.1), C_TENSIONE,
                              self.size)
        return VGroup(fr, et)

    def potenziale(self, nodo, lato=UR, cifre=1, dist=0.12):
        """Valore dal vivo del potenziale di un nodo, scritto accanto al nodo."""
        q = self.c.nodi[nodo]["punto"]
        return self._testo_vivo("", lambda: virgola(float(self.sol().V[nodo]), cifre) + " V",
                                self._pos_lato(q, lato, dist), C_TESTO, self.size)

    def scala_potenziali(self, nodi, centro, altezza=4.0, cifre=1, unita="V", size=26):
        """Barra di colore verticale (vmin in basso, vmax in alto) con i nodi segnati alla loro quota, dal vivo."""
        centro = _np.array([*centro[:2], 0.0])
        bar = barra_colori(MAPPA_BASSO, MAPPA_ALTO, altezza, centro)
        y0, y1 = centro[1] - altezza / 2, centro[1] + altezza / 2
        tacche = VGroup(
            Text(virgola(self.vmin, 0) + " " + unita, font_size=size - 4, color=C_TENUE).next_to([centro[0], y0, 0], DOWN, buff=0.12),
            Text(virgola(self.vmax, 0) + " " + unita, font_size=size - 4, color=C_TENUE).next_to([centro[0], y1, 0], UP, buff=0.12))
        tit = Text("potenziale", font_size=size - 4, color=C_TENUE).rotate(PI / 2).next_to(bar, RIGHT, buff=0.15)

        def quota(n):
            v = float(self.sol().V[n])
            u = (v - self.vmin) / ((self.vmax - self.vmin) or 1.0)
            return y0 + min(max(u, 0.0), 1.0) * altezza

        def marcatore(n):
            y = quota(n)
            x = centro[0] - 0.15 - 0.03
            tri = Triangle(fill_color=C_TESTO, fill_opacity=1, stroke_width=0).scale(0.09).rotate(-PI / 2)
            tri.move_to([x - 0.06, y, 0])
            etich = self.c.nodi[n]["etichetta"] or n
            t = Text(f"{etich}  " + virgola(float(self.sol().V[n]), cifre) + " " + unita, font_size=size, color=C_TESTO)
            t.next_to(tri, LEFT, buff=0.1)
            return VGroup(tri, t)

        segni = VGroup(*[always_redraw(lambda n=n: marcatore(n)) for n in nodi])
        return Group(bar, tacche, tit, segni)

    # ---------------------------------------------------------------- pezzi, riquadri, interruttori
    def pezzi(self, *nomi, nodi=()):
        """VGroup con i mobject dei rami (fili + simbolo + etichetta) e, se chiesti, dei nodi."""
        return VGroup(*[self.rami_m[n] for n in nomi], *[self.nodi_m[n] for n in nodi])

    def riquadro(self, *nomi, griglia=None, colore=C_RIF, buff=0.25):
        """Rettangolo tratteggiato attorno ai rami (es. 'il resto della rete' per Thévenin).

        griglia=((x0, y0), (x1, y1)): rettangolo dato in celle (meglio: lo stesso riquadro si ritrova identico in
        un altro disegno con la stessa griglia, e i fili del carico lo attraversano dove sono i morsetti).
        È fermo: crealo DOPO aver spostato il disegno.
        """
        if griglia is not None:
            (x0, y0), (x1, y1) = griglia
            box = Polygon(*[self.p(q) for q in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))], color=colore, stroke_width=3)
        else:
            box = SurroundingRectangle(self.pezzi(*nomi), buff=buff, color=colore, stroke_width=3)
        return DashedVMobject(box, num_dashes=70)

    def interruttore_anima(self, scene, nome, *anim, chiuso=True, run_time=0.5):
        """La levetta ruota fino a chiudere (o aprire) il contatto; aggiorna anche il circuito."""
        r = self.c.rami[nome]
        parti = self.parti[nome]
        if r.chiuso == chiuso:
            return
        ang = -30 * DEGREES if chiuso else 30 * DEGREES   # la levetta è disegnata aperta a +30° (riferimento del ramo)
        scene.play(Rotate(parti["leva"], ang, about_point=parti["perno"].get_center()), *anim, run_time=run_time)
        r.chiuso = chiuso
