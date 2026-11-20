"""TEMPLATE MECCANISMO (fisica 1, meccanica razionale): simulazione VERA dalla Lagrangiana.

Per sistemi con molle, pendoli, carrelli, aste, dischi: tutto ciò che ha
equazioni del moto. Claude scrive SOLO:
  1. la Lagrangiana in SymPy (coordinate generalizzate, T - V),
  2. la geometria: dallo stato q alle posizioni dei pezzi sullo schermo,
  3. i parametri e le condizioni iniziali dell'esercizio.
Il kit (fisica_kit.py) ricava le equazioni, integra con solve_ivp, disegna nello stile Doll
(sfondo nero, molle, cerniere, tratteggi) e traccia i grafici live.

Esempio: carroponte. Carrello di massa M su una rotaia, legato al muro da una
molla k; dal carrello pende un pendolo (massa m, lunghezza L).
Coordinate: x (spostamento del carrello), theta (angolo del pendolo).

Unità: i parametri fisici restano quelli dell'esercizio (SI). Lo schermo usa
SCALA unità Manim per metro: sceglila in modo che il meccanismo riempia la metà
sinistra dello schermo (il pezzo più lungo ≈ 3 unità).
Durata: 15-30 s. Testo nella lingua dell'utente.
"""
from doll_kit import fit, titolo  # noqa: F401  (render.sh mette kit/ nel PYTHONPATH)
from fisica_kit import *
import numpy as np
import sympy as sp

# ---------------- 1. parametri dell'esercizio ----------------
M_, m_, k_, L_, g_ = 2.0, 1.0, 20.0, 2.0, 9.81   # SI: kg, kg, N/m, m, m/s²
X0, TH0 = 0.0, np.radians(50)          # condizioni iniziali
DURATA = 14.0

# ---------------- 2. modello: Lagrangiana ----------------
t = sp.symbols("t")
M, m, k, L, g = sp.symbols("M m k L g", positive=True)
x, th = sp.Function("x")(t), sp.Function("theta")(t)
xd, thd = sp.diff(x, t), sp.diff(th, t)
T = sp.Rational(1, 2) * (M + m) * xd**2 + m * L * xd * thd * sp.cos(th) + sp.Rational(1, 2) * m * L**2 * thd**2
V = sp.Rational(1, 2) * k * x**2 - m * g * L * sp.cos(th)
rhs = equazioni_lagrange(T - V, [x, th], t, parametri={M: M_, m: m_, k: k_, L: L_, g: g_},
                         smorzamento={x: 0.15, th: 0.05})

# ---------------- 3. geometria (schermo) ----------------
SCALA = 1.5          # unità Manim per metro
Y_ROTAIA = 1.55
X_MURO = -6.6
X_RIPOSO = -3.3
W_C, H_C, R_RUOTA = 1.3, 0.55, 0.13
Y_C = Y_ROTAIA + 2 * R_RUOTA + H_C / 2


class Esercizio(Scene):
    def construct(self):
        stile_libro(self)
        tit = titolo(self, "Carrello, molla e pendolo")
        sim = Simulazione(rhs, [X0, TH0, 0.0, 0.0], DURATA)

        def centro_carrello():
            return np.array([X_RIPOSO + SCALA * sim.q()[0], Y_C, 0])

        def perno():
            return centro_carrello()

        def pallina():
            xx, tt = sim.q()
            return perno() + SCALA * L_ * np.array([np.sin(tt), -np.cos(tt), 0])

        # vincoli fissi
        # rotaia sospesa (una trave, non un pavimento: il pendolo le passa davanti)
        rotaia = Rectangle(width=1.0 - X_MURO, height=0.1, fill_color=ASTA, fill_opacity=1,
                           stroke_color=INCHIOSTRO, stroke_width=2).move_to([(X_MURO + 1.0) / 2, Y_ROTAIA - 0.05, 0])
        parete = muro(X_MURO, Y_ROTAIA - 0.6, Y_C + 0.8)
        self.add(rotaia, parete)

        # pezzi mobili
        car = always_redraw(lambda: carrello(centro_carrello(), W_C, H_C, R_RUOTA))
        mol = always_redraw(lambda: molla([X_MURO, Y_C], centro_carrello() + LEFT * W_C / 2, spire=10))
        filo = always_redraw(lambda: asta(perno(), pallina(), larghezza=0.12))
        bob = always_redraw(lambda: massa(pallina(), r=0.34))
        cern = always_redraw(lambda: cerniera(perno()))
        trail = scia(pallina, durata=1.0)
        et = VGroup(
            etichetta("M", lambda: centro_carrello(), offset=UP * 0.62),
            etichetta("k", lambda: (np.array([X_MURO, Y_C, 0]) + centro_carrello() + LEFT * W_C / 2) / 2, offset=UP * 0.45),
            etichetta("m", pallina, offset=UR * 0.45),
            etichetta("L", lambda: (perno() + pallina()) / 2, offset=LEFT * 0.35),
        )
        gfreccia = freccia_g([0.6, 3.0])

        head = intestazione(sim, extra=lambda: rf"\theta = {np.degrees(sim.q()[1]):.0f}^\circ")

        # grafici live: x(t) e theta(t)
        g1 = grafico_live(sim, [(lambda y: y[0], BLU, "x")], posizione=[4.3, 1.2], larghezza=4.4, altezza=2.0)
        g2 = grafico_live(sim, [(lambda y: np.degrees(y[1]), ROSSO, r"\theta")], posizione=[4.3, -1.5],
                          larghezza=4.4, altezza=2.0)

        self.add(trail)
        self.play(FadeIn(VGroup(car, mol, filo, bob, cern)), FadeIn(et), FadeIn(gfreccia),
                  FadeIn(head), run_time=0.8)
        self.play(FadeIn(g1), FadeIn(g2), run_time=0.5)

        did = didascalia_libro("Lasciato a 50°: il pendolo trascina il carrello")
        self.play(FadeIn(did), run_time=0.3)
        sim.avanza(self, 4.0)
        self.play(FadeOut(did), run_time=0.2)
        did = didascalia_libro("La molla richiama: l'energia va avanti e indietro")
        self.play(FadeIn(did), run_time=0.3)
        sim.avanza(self, 5.0)
        self.play(FadeOut(did), run_time=0.2)
        did = didascalia_libro("Al rallentatore: due oscillazioni accoppiate")
        self.play(FadeIn(did), run_time=0.3)
        sim.avanza(self, 2.0, velocita=0.5)
        sim.avanza(self, DURATA - sim.t.get_value())
        self.wait(0.5)
