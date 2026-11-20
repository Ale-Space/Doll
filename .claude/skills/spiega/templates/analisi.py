"""TEMPLATE ANALISI: funzioni, derivate, integrali, limiti, serie, ottimizzazione.

Esempio: area sotto y = x^2 su [0, 2].
Cosa si vede (≈25 s, niente passaggi: quelli vanno in chat):
  1. il grafico;
  2. i rettangoli di Riemann che si infittiscono e la somma che tende all'integrale;
  3. l'estremo b che si sposta e l'area A(b) che cresce.

Altri esercizi: derivata = retta tangente che scorre (ValueTracker su x0) con la
pendenza letta in diretta; limite = punto che si avvicina; massimo/minimo = punto
che scorre e tangente orizzontale dove f' = 0; serie = somme parziali che si accumulano.
"""
from doll_kit import *  # noqa: F401  (render.sh mette kit/ nel PYTHONPATH)

TITOLO = "Area sotto una parabola"


def f(x):
    return x ** 2


A_, B_ = 0, 2
VALORE = 8 / 3


class Esercizio(Scene):
    def construct(self):
        tit = titolo(self, TITOLO)
        dati(self, r"f(x) = x^2, \quad x \in [0, 2]")

        ax = Axes(x_range=[0, 2.5, 0.5], y_range=[0, 4.5, 1], x_length=7.5, y_length=5,
                  axis_config={"include_numbers": True, "font_size": 26}).shift(LEFT * 1.6 + DOWN * 0.3)
        grafico = ax.plot(f, x_range=[0, 2.2], color=C_A)
        self.play(Create(ax), Create(grafico), run_time=1.2)

        # Somme di Riemann che si infittiscono
        n = ValueTracker(4)
        rett = always_redraw(lambda: ax.get_riemann_rectangles(
            grafico, x_range=[A_, B_], dx=(B_ - A_) / int(n.get_value()), color=[C_B, C_A],
            fill_opacity=0.6, stroke_width=0.5))
        def somma():
            k = int(n.get_value()); dx = (B_ - A_) / k
            return sum(f(A_ + i * dx) * dx for i in range(k))
        lettura = always_redraw(lambda: VGroup(
            MathTex(rf"n = {int(n.get_value())}", font_size=36),
            MathTex(rf"\textstyle\sum = {somma():.3f}", font_size=36),
            MathTex(rf"\int = {VALORE:.3f}", font_size=36, color=C_ACCENTO),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(RIGHT * 4.7 + UP * 0.2))
        did = cambia_didascalia(self, None, "Rettangoli più fitti e più sottili...")
        self.play(FadeIn(rett), FadeIn(lettura))
        self.play(n.animate.set_value(60), run_time=4, rate_func=linear)
        did = cambia_didascalia(self, did, "...the sum approaches the integral")
        self.wait(1)

        # L'estremo superiore che si sposta
        self.play(FadeOut(rett), FadeOut(lettura))
        b = ValueTracker(0.3)
        area = always_redraw(lambda: ax.get_area(grafico, x_range=[A_, b.get_value()], color=C_B, opacity=0.6))
        linea = always_redraw(lambda: ax.get_vertical_line(ax.i2gp(b.get_value(), grafico), color=C_ACCENTO))
        val = always_redraw(lambda: MathTex(
            rf"A(b) = {b.get_value() ** 3 / 3:.2f}", font_size=38).move_to(RIGHT * 4.6 + UP * 0.6))
        did = cambia_didascalia(self, did, "Sposto b: l'area cresce come b³/3")
        self.play(FadeIn(area), FadeIn(linea), FadeIn(val))
        self.play(b.animate.set_value(B_), run_time=3.5)
        self.wait(0.5)

        risultato_angolo(self, r"\int_0^2 x^2\,dx = \frac{8}{3} \approx 2{,}67", did,
                         posizione=RIGHT * 4.6 + DOWN * 1.2)
