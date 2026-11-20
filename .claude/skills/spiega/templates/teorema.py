"""TEMPLATE TEOREMA: la struttura in atti di guide/manim.md §3, con un esempio completo.

Esempio: teorema di Lagrange (valor medio) e il controesempio |x - 1| + 1.
  f(x) = x³/6 - x/2 + 1 su [a, b] = [-0,5; 2,5]
  pendenza della secante m = (f(b) - f(a)) / (b - a) = 0,375
  f'(x) = x²/2 - 1/2 = m  =>  c = sqrt(2m + 1) = 1,3229 (unico in (a, b))
  controesempio g(x) = |x - 1| + 1 su [0, 2]: secante orizzontale, ma g' vale -1 o +1, mai 0.

Gli atti (adatta i contenuti, tieni la struttura):
  0 apertura      titolo + enunciato in una formula
  1 l'oggetto     la curva concreta, A e B
  2 il meccanismo la secante ferma; la tangente SCORRE e la sua pendenza cambia dal vivo
  3 conclusione   in c la tangente diventa parallela (stesso colore della secante): slogan
  4 controesempio stesso gesto su una curva con uno spigolo: la pendenza salta, nessun c
  5 risultato     riquadro finale
Gesto visivo: la tangente che scorre fino a diventare parallela alla secante.
Per un altro teorema: cambia esempio, gesto e didascalie (repertorio in guide/manim.md §10), non la struttura.
"""
from doll_kit import *  # noqa: F401,F403  (render.sh mette kit/ nel PYTHONPATH)
import numpy as np


def f(x):
    return x ** 3 / 6 - x / 2 + 1


def df(x):
    return x ** 2 / 2 - 0.5


A_, B_ = -0.5, 2.5
M = (f(B_) - f(A_)) / (B_ - A_)          # 0,375
C_ = np.sqrt(2 * M + 1)                  # 1,3229


def g(x):
    return np.abs(x - 1) + 1


def dg(x):
    return np.sign(x - 1)


A2, B2 = 0.0, 2.0
L_TAN = 1.5                               # semi-lunghezza della tangente sullo schermo


class Esercizio(Scene):
    def construct(self):
        # ---------------- ATTO 0: apertura ----------------
        tit = titolo(self, "Teorema di Lagrange")
        d = dati(self, r"\exists\, c\in(a,b):\ f'(c)=\frac{f(b)-f(a)}{b-a}")

        # ---------------- ATTO 1: l'oggetto ----------------
        ax = Axes(x_range=[-1, 3, 1], y_range=[0, 3, 1], x_length=7.2, y_length=4.4,
                  axis_config={"color": C_TENUE, "include_ticks": False}).shift(LEFT * 1.6 + DOWN * 0.35)
        assi_lab = ax.get_axis_labels(MathTex("x", font_size=28, color=C_TENUE), MathTex("y", font_size=28, color=C_TENUE))
        graf = ax.plot(f, x_range=[A_ - 0.3, B_ + 0.15], color=C_OGGETTO, stroke_width=4)
        PA, PB = Dot(ax.c2p(A_, f(A_)), color=C_PUNTO), Dot(ax.c2p(B_, f(B_)), color=C_PUNTO)
        la = MathTex("A", font_size=32).next_to(PA, UL, buff=0.08)
        lb = MathTex("B", font_size=32).next_to(PB, UL, buff=0.08)
        self.play(Create(ax), FadeIn(assi_lab), Create(graf), run_time=1.0)
        self.play(FadeIn(PA), FadeIn(PB), FadeIn(la), FadeIn(lb), run_time=0.5)
        did = cambia_didascalia(self, None, "Una curva liscia da A a B")
        self.wait(0.6)

        sec = Line(ax.c2p(A_ - 0.4, f(A_) - 0.4 * M), ax.c2p(B_ + 0.3, f(B_) + 0.3 * M),
                   color=C_RIF, stroke_width=4)
        did = cambia_didascalia(self, did, "La secante: la pendenza media")
        self.play(Create(sec), run_time=0.8)
        self.wait(0.6)

        # ---------------- ATTO 2: il meccanismo ----------------
        x0 = ValueTracker(A_ + 0.08)

        def retta(fun, dfun, x, colore):
            """Tangente di lunghezza FISSA sullo schermo: anche quando e' ripida non esce dal grafico."""
            P = ax.c2p(x, fun(x))
            dirz = ax.c2p(x + 1, fun(x) + dfun(x)) - P
            dirz = dirz / np.linalg.norm(dirz) * L_TAN
            return Line(P - dirz, P + dirz, color=colore, stroke_width=5)

        tan = always_redraw(lambda: retta(f, df, x0.get_value(), C_X))
        pt = always_redraw(lambda: Dot(ax.c2p(x0.get_value(), f(x0.get_value())), color=C_X, radius=0.09))

        # pannello valori (a destra, senza cornice, numeri dal vivo)
        XP = 3.4
        e1 = Text("pendenza media", font_size=24, color=C_RIF).move_to([XP, 1.3, 0], aligned_edge=LEFT)
        v1 = Text(virgola(M, 3), font_size=30, color=C_RIF).move_to([XP, 0.85, 0], aligned_edge=LEFT)
        e2 = Text("pendenza tangente", font_size=24, color=C_X).move_to([XP, 0.15, 0], aligned_edge=LEFT)
        v2 = numero_vivo(self, lambda: virgola(df(x0.get_value()), 3), [XP, -0.3, 0], colore=C_X, size=30)
        self.play(FadeIn(e1), FadeIn(v1), FadeIn(e2), FadeIn(tan), FadeIn(pt), run_time=0.5)
        self.add(v2)
        did = cambia_didascalia(self, did, "La tangente scorre lungo la curva")
        self.play(x0.animate.set_value(B_ - 0.08), run_time=3.2, rate_func=smooth)
        did = cambia_didascalia(self, did, "Cerchiamo dove ha la pendenza media")
        self.play(x0.animate.set_value(C_), run_time=2.2, rate_func=smooth)

        # ---------------- ATTO 3: conclusione ----------------
        tan_c = retta(f, df, C_, C_RIF)
        guida = DashedLine(ax.c2p(C_, 0), ax.c2p(C_, f(C_)), color=C_TENUE, dash_length=0.08)
        lc = MathTex("c", font_size=32, color=C_RIF).next_to(ax.c2p(C_, 0), DOWN, buff=0.12)
        self.remove(tan)
        self.play(FadeIn(tan_c), Create(guida), FadeIn(lc), run_time=0.6)
        did = cambia_didascalia(self, did, "In c tangente e secante sono parallele", colore=C_ACCENTO)
        self.wait(1.4)

        # ---------------- ATTO 4: controesempio ----------------
        v2.clear_updaters()
        self.play(*[FadeOut(m) for m in (graf, PA, PB, la, lb, sec, tan_c, pt, guida, lc, v1, v2, did)], run_time=0.5)
        graf2 = ax.plot(g, x_range=[A2 - 0.2, B2 + 0.2], color=C_CONTRO, stroke_width=4)
        Q1, Q2 = Dot(ax.c2p(A2, g(A2)), color=C_PUNTO), Dot(ax.c2p(B2, g(B2)), color=C_PUNTO)
        sec2 = Line(ax.c2p(A2 - 0.5, g(A2)), ax.c2p(B2 + 0.5, g(B2)), color=C_RIF, stroke_width=4)
        v1b = Text(virgola(0.0, 3), font_size=30, color=C_RIF).move_to([XP, 0.85, 0], aligned_edge=LEFT)
        self.play(Create(graf2), FadeIn(Q1), FadeIn(Q2), Create(sec2), FadeIn(v1b), run_time=0.9)
        did = cambia_didascalia(self, None, "Con uno spigolo: stessa prova")
        x1 = ValueTracker(A2 + 0.1)
        tan2 = always_redraw(lambda: retta(g, dg, x1.get_value(), C_X))
        pt2 = always_redraw(lambda: Dot(ax.c2p(x1.get_value(), g(x1.get_value())), color=C_X, radius=0.09))
        v2b = numero_vivo(self, lambda: virgola(dg(x1.get_value()), 3), [XP, -0.3, 0], colore=C_X, size=30)
        self.play(FadeIn(tan2), FadeIn(pt2), run_time=0.3)
        self.add(v2b)
        self.play(x1.animate.set_value(B2 - 0.1), run_time=3.0, rate_func=linear)
        did = cambia_didascalia(self, did, "La pendenza salta da −1 a +1: nessun c", colore=C_CONTRO)
        self.wait(1.4)
        v2b.clear_updaters()

        # ---------------- ATTO 5: risultato ----------------
        risultato_angolo(self, r"f\ \text{continua in } [a,b],\ \text{derivabile in } (a,b)"
                               r"\ \Rightarrow\ \exists\, c:\ f'(c)=\frac{f(b)-f(a)}{b-a}",
                         vecchia_didascalia=did, attesa=2.0)
