"""Kit per animazioni di meccanica, nello stile unico dei video Doll (sfondo nero, guide/manim.md).

Tratto chiaro, aste grigie, cerniere, molle a spirale, terreno tratteggiato, sfere sfumate,
scia che svanisce e grafico in diretta.

Flusso (Claude scrive solo i punti 1 e 2):
  1. MODELLO: coordinate generalizzate + Lagrangiana in SymPy
        t = sp.symbols("t"); x, th = sp.Function("x")(t), sp.Function("theta")(t)
        L = T - V
        rhs = equazioni_lagrange(L, [x, th], t, parametri={...}, smorzamento={x: 0.1})
  2. GEOMETRIA: una funzione stato -> posizioni dei pezzi sullo schermo
  3. sim = Simulazione(rhs, y0=[x0, th0, v0, w0], durata=12)
     poi ogni oggetto è always_redraw(lambda: ... sim.q() ...) e
     sim.avanza(scene, secondi) fa scorrere il tempo (rate_func lineare).

Il testo nel video è nella lingua dell'utente (italiano di default).
"""
from __future__ import annotations

import numpy as np
import sympy as sp
from manim import *
from scipy.integrate import solve_ivp

# ---------------------------------------------------------------- palette
INCHIOSTRO = "#E6E6E6"   # tratto e testo (chiaro su sfondo nero)
ASTA = "#8C939C"         # aste, blocchi, rotaie
ROSA = "#D98A82"         # masse principali
ROSA_SCURO = "#B5655D"   # scia delle masse
GRIGIO_MASSA = "#4A4F57"
BLU = BLUE_C             # stessi colori della palette del kit (doll_kit)
ROSSO = RED_C
VERDE = GREEN_C
ORO = GOLD_C


def stile_libro(scene: Scene) -> None:
    """Testo chiaro di default (lo sfondo resta quello nero di Manim). Chiamalo per primo in construct().
    Il nome resta "stile_libro" per compatibilita' con le scene esistenti."""
    for cls in (Text, MathTex, Tex):
        cls.set_default(color=INCHIOSTRO)


# ---------------------------------------------------------------- modello
def equazioni_lagrange(L, q: list, t, parametri: dict | None = None,
                       smorzamento: dict | None = None, forze: dict | None = None):
    """Dalla Lagrangiana L(q, q', t) alla funzione rhs(t, y) per solve_ivp.

    q:           lista di sp.Function(...)(t)  (coordinate generalizzate)
    parametri:   {simbolo: valore}  per sostituire m, k, g, ...
    smorzamento: {q_i: c}  aggiunge la forza generalizzata -c * q_i'
    forze:       {q_i: espressione}  forze generalizzate non conservative extra (in t, q, q')
    y = [q_1..q_n, q_1'..q_n']
    """
    parametri = parametri or {}
    n = len(q)
    qd = [sp.diff(qi, t) for qi in q]
    qdd = [sp.diff(qi, t, 2) for qi in q]
    eqs = []
    for i in range(n):
        e = sp.diff(sp.diff(L, qd[i]), t) - sp.diff(L, q[i])
        Q = 0
        if smorzamento and q[i] in smorzamento:
            Q += -smorzamento[q[i]] * qd[i]
        if forze and q[i] in forze:
            Q += forze[q[i]]
        eqs.append(sp.expand(e - Q))
    # simboli piatti al posto delle funzioni
    Qs = sp.symbols(f"q0:{n}")
    Vs = sp.symbols(f"v0:{n}")
    As = sp.symbols(f"a0:{n}")
    sost = {}
    for i in range(n):
        sost[qdd[i]] = As[i]
    for i in range(n):
        sost[qd[i]] = Vs[i]
    for i in range(n):
        sost[q[i]] = Qs[i]
    eqs = [e.subs(sost).subs(parametri) for e in eqs]
    M, b = sp.linear_eq_to_matrix(eqs, As)  # M a = b
    fM = sp.lambdify((t, *Qs, *Vs), M, "numpy")
    fb = sp.lambdify((t, *Qs, *Vs), b, "numpy")

    def rhs(tt, y):
        args = (tt, *y)
        a = np.linalg.solve(np.array(fM(*args), dtype=float), np.array(fb(*args), dtype=float).ravel())
        return np.concatenate([y[n:], a])

    rhs.n = n
    return rhs


class Simulazione:
    """Integra una volta sola (dense output) e poi si legge lo stato al tempo sim.t."""

    def __init__(self, rhs, y0, durata: float, max_step: float = 0.005):
        self.n = len(y0) // 2
        self.durata = durata
        self.sol = solve_ivp(rhs, (0, durata), np.array(y0, dtype=float), dense_output=True,
                             rtol=1e-9, atol=1e-9, max_step=max_step)
        if not self.sol.success:
            raise RuntimeError(f"solve_ivp fallito: {self.sol.message}")
        self.t = ValueTracker(0.0)
        self._griglia = np.linspace(0, durata, int(durata * 120) + 1)
        self._campioni = self.sol.sol(self._griglia)

    def y(self, tt: float | None = None) -> np.ndarray:
        tt = self.t.get_value() if tt is None else tt
        return self.sol.sol(min(max(tt, 0.0), self.durata))

    def q(self, tt=None) -> np.ndarray:
        return self.y(tt)[: self.n]

    def qd(self, tt=None) -> np.ndarray:
        return self.y(tt)[self.n:]

    def avanza(self, scene: Scene, secondi: float, velocita: float = 1.0) -> None:
        """Fa scorrere il tempo simulato di `secondi` (velocita=0.5 -> rallentatore)."""
        fine = min(self.t.get_value() + secondi, self.durata)
        scene.play(self.t.animate.set_value(fine), run_time=(fine - self.t.get_value()) / velocita,
                   rate_func=linear)

    def serie(self, f) -> tuple[np.ndarray, np.ndarray]:
        """Valori di f(y) sulla griglia di campionamento (per i grafici)."""
        return self._griglia, np.array([f(self._campioni[:, i]) for i in range(len(self._griglia))])


# ---------------------------------------------------------------- disegno
def _p(P) -> np.ndarray:
    P = np.asarray(P, dtype=float)
    return np.array([P[0], P[1], 0.0]) if P.shape[0] == 2 else P


def asta(A, B, larghezza: float = 0.22, colore=ASTA) -> VMobject:
    """Asta rigida con estremità arrotondate tra A e B."""
    A, B = _p(A), _p(B)
    d = B - A
    lun = max(np.linalg.norm(d), 1e-6)
    r = RoundedRectangle(width=lun + larghezza, height=larghezza, corner_radius=larghezza / 2,
                         fill_color=colore, fill_opacity=1, stroke_color=INCHIOSTRO, stroke_width=2)
    r.rotate(np.arctan2(d[1], d[0])).move_to((A + B) / 2)
    return r


def cerniera(P, r: float = 0.075) -> Circle:
    return Circle(radius=r, fill_color=BLACK, fill_opacity=1, stroke_color=INCHIOSTRO,
                  stroke_width=2).move_to(_p(P))


def massa(P, r: float = 0.35, colore=ROSA) -> VGroup:
    """Sfera 'lucida': cerchio pieno + riflesso chiaro in alto a sinistra."""
    P = _p(P)
    corpo = Circle(radius=r, fill_color=colore, fill_opacity=1, stroke_color=INCHIOSTRO, stroke_width=1.5)
    corpo.set_sheen(-0.2, DR)
    riflesso = Circle(radius=r * 0.28, fill_color=WHITE, fill_opacity=0.55, stroke_width=0)
    riflesso.move_to(P + np.array([-0.35 * r, 0.38 * r, 0]))
    return VGroup(corpo.move_to(P), riflesso)


def blocco(centro, w: float = 1.0, h: float = 0.6, colore=ASTA, angolo: float = 0.0) -> Rectangle:
    b = Rectangle(width=w, height=h, fill_color=colore, fill_opacity=1, stroke_color=INCHIOSTRO, stroke_width=2)
    return b.rotate(angolo).move_to(_p(centro))


def carrello(centro, w: float = 1.4, h: float = 0.6, r_ruota: float = 0.14) -> VGroup:
    c = _p(centro)
    corpo = blocco(c, w, h)
    ruote = VGroup(*[Circle(radius=r_ruota, fill_color=GRIGIO_MASSA, fill_opacity=1, stroke_color=INCHIOSTRO,
                            stroke_width=1.5).move_to(c + np.array([dx, -h / 2 - r_ruota, 0]))
                     for dx in (-w / 3, w / 3)])
    return VGroup(corpo, ruote)


def molla(A, B, spire: int = 9, raggio: float = 0.16, tratto_finale: float = 0.18) -> VMobject:
    """Molla a spirale (vista di lato, con gli anelli) tra A e B."""
    A, B = _p(A), _p(B)
    d = B - A
    lun = max(np.linalg.norm(d), 1e-6)
    u = d / lun
    n = np.array([-u[1], u[0], 0.0])
    tf = min(tratto_finale, lun * 0.2)
    L_attiva = lun - 2 * tf
    s = np.linspace(0, 1, spire * 24 + 1)
    th = 2 * np.pi * spire * s
    anello = raggio * 0.55
    lungo = tf + s * L_attiva - anello * np.cos(th) + anello
    lungo = np.clip(lungo, tf * 0.5, lun - tf * 0.5)
    lato = raggio * np.sin(th)
    punti = [A, A + u * tf] + [A + u * a + n * b for a, b in zip(lungo, lato)] + [B - u * tf, B]
    m = VMobject(stroke_color=INCHIOSTRO, stroke_width=2)
    m.set_points_as_corners(punti)
    return m


def molla_zigzag(A, B, denti: int = 10, ampiezza: float = 0.15) -> VMobject:
    A, B = _p(A), _p(B)
    d = B - A
    lun = max(np.linalg.norm(d), 1e-6)
    u, n = d / lun, np.array([-d[1], d[0], 0.0]) / lun
    tf = lun * 0.1
    punti = [A, A + u * tf]
    for i in range(1, 2 * denti):
        punti.append(A + u * (tf + (lun - 2 * tf) * i / (2 * denti)) + n * ampiezza * (1 if i % 2 else -1))
    punti += [B - u * tf, B]
    m = VMobject(stroke_color=INCHIOSTRO, stroke_width=2)
    m.set_points_as_corners(punti)
    return m


def tratteggio(A, B, lato=DOWN, passo: float = 0.18, lunghezza: float = 0.18) -> VGroup:
    """Linea di vincolo con tratteggio obliquo (terreno, muro, soffitto)."""
    A, B = _p(A), _p(B)
    d = B - A
    lun = np.linalg.norm(d)
    u = d / lun
    v = _p(lato) / np.linalg.norm(_p(lato))
    linea = Line(A, B, color=INCHIOSTRO, stroke_width=3)
    tratti = VGroup(*[Line(A + u * s, A + u * s + (v + u * 0.8) * lunghezza / np.linalg.norm(v + u * 0.8),
                           color=INCHIOSTRO, stroke_width=1.5)
                      for s in np.arange(0, lun, passo)])
    return VGroup(linea, tratti)


def terreno(x0: float, x1: float, y: float) -> VGroup:
    return tratteggio([x0, y], [x1, y], lato=DOWN)


def muro(x: float, y0: float, y1: float, lato=LEFT) -> VGroup:
    return tratteggio([x, y0], [x, y1], lato=lato)


def soffitto(x0: float, x1: float, y: float) -> VGroup:
    return tratteggio([x0, y], [x1, y], lato=UP)


def freccia_g(P, lunghezza: float = 0.7) -> VGroup:
    P = _p(P)
    a = Arrow(P, P + DOWN * lunghezza, buff=0, color=INCHIOSTRO, stroke_width=3,
              max_tip_length_to_length_ratio=0.3)
    return VGroup(a, MathTex("g", font_size=34).next_to(a, RIGHT, buff=0.12))


def freccia_forza(P, vettore, colore=ROSSO, scala: float = 0.1, etichetta: str | None = None) -> VGroup:
    P, v = _p(P), _p(vettore) * scala
    g = VGroup()
    if np.linalg.norm(v) > 1e-3:
        g.add(Arrow(P, P + v, buff=0, color=colore, stroke_width=4, max_tip_length_to_length_ratio=0.25))
        if etichetta:
            g.add(MathTex(etichetta, color=colore, font_size=30).next_to(P + v, normalize(v), buff=0.1))
    return g


def scia(punto_func, colore=ROSA_SCURO, durata: float = 1.2, spessore: float = 2.5) -> TracedPath:
    """Scia che svanisce dietro a un punto in movimento (come nelle animazioni dei libri)."""
    return TracedPath(punto_func, stroke_color=colore, stroke_width=spessore, dissipating_time=durata)


def etichetta(testo_latex: str, P_func, offset=UR * 0.3, size: int = 32, colore=INCHIOSTRO) -> Mobject:
    """Etichetta MathTex che segue un punto (es. 'm', 'k', 'L')."""
    return always_redraw(lambda: MathTex(testo_latex, font_size=size, color=colore).move_to(_p(P_func()) + offset))


# ---------------------------------------------------------------- testo e grafici
def intestazione(sim: Simulazione, extra=None, size: int = 34) -> Mobject:
    """'t = 1.60 s   ψ = -12°' in alto al centro. extra: lambda -> stringa LaTeX aggiuntiva."""
    def crea():
        s = rf"t = {sim.t.get_value():.2f}\,\mathrm{{s}}"
        if extra is not None:
            s += r"\qquad " + extra()
        return MathTex(s, font_size=size).to_edge(UP, buff=0.3)
    return always_redraw(crea)


def titolo_libro(testo: str, size: int = 26) -> Text:
    return Text(testo, font_size=size, color=GREY_D).to_corner(UL, buff=0.3)


def didascalia_libro(testo: str, size: int = 26) -> Text:
    t = Text(testo, font_size=size, color=INCHIOSTRO)
    if t.width > 12:
        t.scale_to_fit_width(12)
    return t.to_edge(DOWN, buff=0.3)


def grafico_live(sim: Simulazione, curve: list, posizione, larghezza: float = 4.2, altezza: float = 1.6,
                 y_range=None) -> VGroup:
    """Grafico che si disegna mentre scorre il tempo.

    curve: lista di (funzione y -> valore, colore, etichetta LaTeX)
    Restituisce un VGroup da aggiungere alla scena (assi fissi + curve che crescono).
    """
    tt = sim._griglia
    valori = [np.array([f(sim._campioni[:, i]) for i in range(len(tt))]) for f, _, _ in curve]
    if y_range is None:
        lo = min(v.min() for v in valori); hi = max(v.max() for v in valori)
        pad = 0.1 * (hi - lo + 1e-9)
        y_range = [lo - pad, hi + pad]
    ax = Axes(x_range=[0, sim.durata, sim.durata], y_range=[y_range[0], y_range[1], y_range[1] - y_range[0]],
              x_length=larghezza, y_length=altezza, tips=False,
              axis_config={"color": INCHIOSTRO, "stroke_width": 1.5, "include_ticks": False})
    ax.move_to(_p(posizione))
    lab_t = MathTex("t", font_size=32).next_to(ax.x_axis.get_end(), RIGHT, buff=0.1)
    legenda = VGroup(*[MathTex(e, color=c, font_size=36) for _, c, e in curve]).arrange(DOWN, buff=0.08)
    legenda.next_to(ax.y_axis, LEFT, buff=0.15)

    def curva(k):
        def crea():
            i = int(np.searchsorted(tt, sim.t.get_value()))
            i = max(i, 1)
            pts = [ax.c2p(tt[j], valori[k][j]) for j in range(0, i + 1)]
            m = VMobject(stroke_color=curve[k][1], stroke_width=2.5)
            m.set_points_as_corners(pts if len(pts) > 1 else pts * 2)
            punta = Dot(pts[-1], radius=0.045, color=curve[k][1])
            return VGroup(m, punta)
        return always_redraw(crea)

    return VGroup(ax, lab_t, legenda, *[curva(k) for k in range(len(curve))])
