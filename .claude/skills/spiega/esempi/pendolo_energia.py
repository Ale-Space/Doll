"""Pendolo semplice: scambio K/U, conservazione dell'energia e effetto dell'attrito (m=1 kg, L=1,5 m, 40 gradi)."""
from doll_kit import *  # noqa: F401
from fisica_kit import Simulazione, equazioni_lagrange
import numpy as np
import sympy as sp
from scipy.special import ellipk

# ---- parametri (verificati in piano.md) ----
M_, L_, G_ = 1.0, 1.5, 9.81
TH0 = np.radians(-40)                      # lasciato a sinistra
C_ATTR = 0.45                              # coppia d'attrito viscoso, N m s
E0 = M_ * G_ * L_ * (1 - np.cos(np.radians(40)))          # 3,443 J
T_PER = 4 * np.sqrt(L_ / G_) * ellipk(np.sin(np.radians(40) / 2) ** 2)   # 2,534 s

# ---- modello: Lagrangiana L = T - V ----
t = sp.symbols("t")
m, L, g = sp.symbols("m L g", positive=True)
th = sp.Function("theta")(t)
Lag = sp.Rational(1, 2) * m * L**2 * sp.diff(th, t) ** 2 + m * g * L * sp.cos(th)
par = {m: M_, L: L_, g: G_}
rhs0 = equazioni_lagrange(Lag, [th], t, parametri=par)
rhs1 = equazioni_lagrange(Lag, [th], t, parametri=par, smorzamento={th: C_ATTR})

# ---- schermo ----
SCALA = 1.6
PERNO = np.array([-3.2, 2.0, 0.0])
Y_FONDO = PERNO[1] - SCALA * L_            # quota di riferimento (U = 0)
BASE = -1.9                                # base delle barre
K_E = 0.6                                  # unità per joule
XB = (2.6, 4.0, 5.4)                       # barre K, U, K+U


class Esercizio(Scene):
    def construct(self):
        titolo(self, "Pendolo: energia che passa")
        dati(self, r"m = 1\,\mathrm{kg},\; L = 1{,}5\,\mathrm{m},\; \theta_0 = 40^\circ", max_w=6.2)

        sim1 = Simulazione(rhs0, [TH0, 0.0], 3 * T_PER)
        sim2 = Simulazione(rhs1, [TH0, 0.0], 10.0)
        cur = [sim1]

        def stato():
            q, w = cur[0].y()
            return q, w

        def bob_pos():
            q, _ = stato()
            return PERNO + SCALA * L_ * np.array([np.sin(q), -np.cos(q), 0])

        def U():
            q, _ = stato(); return M_ * G_ * L_ * (1 - np.cos(q))

        def K():
            _, w = stato(); return 0.5 * M_ * L_**2 * w**2

        # --- pendolo ---
        sostegno = Line(PERNO + LEFT * 0.6, PERNO + RIGHT * 0.6, color=C_CORPO, stroke_width=6)
        livello = DashedLine([-5.9, Y_FONDO, 0], [-0.9, Y_FONDO, 0], color=C_TENUE, stroke_width=2)
        verticale = DashedLine(PERNO, [PERNO[0], Y_FONDO, 0], color=C_TENUE, stroke_width=2)
        filo = always_redraw(lambda: Line(PERNO, bob_pos(), color=C_CORPO, stroke_width=4))
        bob = always_redraw(lambda: Circle(0.22, color=C_OGGETTO, fill_opacity=1).move_to(bob_pos()))
        arco = Angle(Line(PERNO, [PERNO[0], Y_FONDO, 0]), Line(PERNO, PERNO + SCALA * L_ * np.array([np.sin(TH0), -np.cos(TH0), 0])),
                     radius=0.9, color=C_ACCENTO, other_angle=True)
        lab_arco = MathTex(r"40^\circ", font_size=30, color=C_ACCENTO).move_to(PERNO + np.array([-0.55, -1.25, 0]))
        quota = always_redraw(lambda: VGroup(
            Line([-5.9, Y_FONDO, 0], [-5.9, bob_pos()[1], 0], color=C_ENERGIA_U, stroke_width=6),
            MathTex("h", font_size=32, color=C_ENERGIA_U).move_to([-6.25, (Y_FONDO + bob_pos()[1]) / 2, 0])))
        vel = always_redraw(lambda: freccia_fisica(
            bob_pos(), stato()[1] * L_ * np.array([np.cos(stato()[0]), np.sin(stato()[0])]),
            colore=C_VELOCITA, scala=0.5))

        # --- barre ---
        def barra(x, base, h, col):
            h = max(h, 1e-4)
            return Rectangle(width=0.9, height=h, fill_color=col, fill_opacity=0.9, stroke_width=0
                             ).move_to([x, base + h / 2, 0])

        bar_k = always_redraw(lambda: barra(XB[0], BASE, K() * K_E, C_ENERGIA_K))
        bar_u = always_redraw(lambda: barra(XB[1], BASE, U() * K_E, C_ENERGIA_U))
        bar_tu = always_redraw(lambda: barra(XB[2], BASE, U() * K_E, C_ENERGIA_U))
        bar_tk = always_redraw(lambda: barra(XB[2], BASE + U() * K_E, K() * K_E, C_ENERGIA_K))
        perso = always_redraw(lambda: barra(XB[2], BASE + (U() + K()) * K_E, max(E0 - U() - K(), 0) * K_E, C_ERRORE)
                              .set_fill(opacity=0.35))
        y0 = BASE + E0 * K_E
        riga_e0 = DashedLine([XB[0] - 0.7, y0, 0], [XB[2] + 0.7, y0, 0], color=C_RIF, stroke_width=3)
        base_barre = Line([XB[0] - 0.7, BASE, 0], [XB[2] + 0.7, BASE, 0], color=C_TENUE, stroke_width=2)
        et = VGroup(MathTex("K", font_size=34, color=C_ENERGIA_K).move_to([XB[0], BASE - 0.32, 0]),
                    MathTex("U", font_size=34, color=C_ENERGIA_U).move_to([XB[1], BASE - 0.32, 0]),
                    MathTex("K+U", font_size=34).move_to([XB[2], BASE - 0.32, 0]),
                    MathTex("E_0", font_size=30, color=C_RIF).move_to([XB[0] - 1.05, y0, 0]))
        num = numero_vivo(self, lambda: "K + U = " + virgola(U() + K()) + " J", [XB[1], 0.75, 0],
                          colore=WHITE, size=26, allinea=ORIGIN)
        lab_perso = Text("persa", font_size=22, color=C_ERRORE).move_to([XB[2] + 1.0, y0 - 0.2, 0])

        # --- atto 1: l'oggetto ---
        self.play(FadeIn(sostegno), FadeIn(livello), FadeIn(verticale), FadeIn(filo), FadeIn(bob), run_time=0.8)
        self.play(Create(arco), FadeIn(lab_arco), FadeIn(quota), run_time=0.7)
        self.play(FadeIn(bar_k), FadeIn(bar_u), FadeIn(bar_tu), FadeIn(bar_tk), FadeIn(perso), FadeIn(base_barre),
                  FadeIn(riga_e0), FadeIn(et), FadeIn(num), run_time=0.8)
        did = cambia_didascalia(self, None, "Lasciato a 40°: tutta energia potenziale")
        self.wait(1.0)
        # --- atto 2: senza attrito ---
        self.play(FadeOut(arco), FadeOut(lab_arco), FadeIn(vel), run_time=0.4)
        did = cambia_didascalia(self, did, "Scende: U cala, K cresce")
        sim1.avanza(self, T_PER / 2)
        did = cambia_didascalia(self, did, "La somma K + U resta costante", colore=C_ACCENTO)
        sim1.avanza(self, sim1.durata - sim1.t.get_value())
        # --- atto 4: stessa partenza, con attrito (la sim 2 parte dallo stato in cui finisce la 1) ---
        did = cambia_didascalia(self, did, "Con attrito: la somma scende", colore=C_CONTRO)
        cur[0] = sim2
        self.add(lab_perso)
        sim2.avanza(self, 7.0)
        did = cambia_didascalia(self, did, "Energia persa: diventa calore", colore=C_CONTRO)
        sim2.avanza(self, sim2.durata - sim2.t.get_value())
        num.clear_updaters()
        risultato_angolo(self, r"E_0 = mgL(1-\cos 40^\circ) = 3{,}44\,\mathrm{J}", did)
