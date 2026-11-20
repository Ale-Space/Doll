"""TEMPLATE FOURIER (Metodi matematici): la serie di Fourier di un'onda quadra.

Esempio: f(x) = 1 su (0, π), -1 su (-π, 0), periodo 2π (dispari).
  f(x) = (4/π) Σ_{k dispari} sin(kx)/k
Cosa si vede (≈32 s, niente passaggi: i coefficienti si calcolano in chat):
  1. l'onda quadra tratteggiata;
  2. sotto, le armoniche dispari sin(kx)/k che entrano una alla volta;
     sopra, la somma parziale S_N che si avvicina all'onda (ValueTracker su K,
     N = 2K - 1 = armonica più alta);
  3. lo zoom vicino al salto: il picco di Gibbs (≈ 1,18, cioè +9% del salto)
     si stringe verso il salto ma NON si abbassa al crescere di N.

Per un'altra funzione periodica cambia solo `termine(k, x)` (il k-esimo addendo),
`KS` (quali k entrano) e `f_vera`. Coefficienti esatti con SymPy:
  sp.integrate(f*sp.sin(k*x), (x, -sp.pi, sp.pi)) / sp.pi
Onda triangolare: coefficienti ~1/k² -> converge molto più in fretta, niente Gibbs
(fallo vedere confrontando le due velocità). Dente di sega: tutte le armoniche, segno alterno.

Altre idee (Metodi matematici / Segnali):
  - TRASFORMATA DI FOURIER, dualità tempo/frequenza: due Axes affiancati, a sinistra
    un impulso rettangolare di larghezza T (ValueTracker su T), a destra il suo spettro
    T·sinc(ωT/2). Si stringe l'impulso -> lo spettro si allarga (e si abbassa).
    Stessa cosa con la gaussiana: resta gaussiana, σ_t·σ_ω = costante.
  - CONVOLUZIONE come finestra che scorre: g(t - τ) ribaltata scorre su f(τ)
    (ValueTracker su t), area del prodotto ombreggiata e, sotto, il punto
    (t, (f*g)(t)) che traccia la curva risultato (TracedPath).
  - LAPLACE: il piano s con poli (×) e zeri (o); a destra la risposta nel tempo
    e^{σt}cos(ωt). Si sposta un polo (ValueTracker su σ): a sinistra dell'asse
    immaginario la risposta si smorza, a destra esplode, sull'asse oscilla.
  - CAMPIONAMENTO / ALIASING: una sinusoide di frequenza f e i campioni (Dot) a
    frequenza f_s fissa; f cresce oltre f_s/2 e la sinusoide "ricostruita" dai
    campioni (in un altro colore) rallenta e torna indietro: f_alias = |f - f_s|.
"""
from doll_kit import *  # noqa: F401  (render.sh mette kit/ nel PYTHONPATH)
import numpy as np

TITOLO = "Serie di Fourier: onda quadra"
KS = [1, 3, 5, 7, 9, 11]            # armoniche mostrate una alla volta
K_MAX = 40                           # poi la somma arriva fino a N = 2*K_MAX - 1
GIBBS = 1.1790                       # (2/π) Si(π), verificato con SymPy
COLORI = [BLUE_C, GREEN_C, RED_C, PURPLE_B, TEAL_C, ORANGE]


def termine(k, x):
    return 4 / np.pi * np.sin(k * x) / k


def somma(K, x):
    """S_N con le prime K armoniche dispari (N = 2K - 1)."""
    return sum(termine(2 * j + 1, x) for j in range(K))


def f_vera(x):
    return np.sign(np.sin(x))


class Esercizio(Scene):
    def construct(self):
        tit = titolo(self, TITOLO)
        dat = dati(self, r"f(x)=\begin{cases} 1 & 0<x<\pi \\ -1 & -\pi<x<0 \end{cases}",
                   font_size=30)

        # ---------- assi: sopra la somma, sotto le armoniche ----------
        ax = Axes(x_range=[-2 * PI, 2 * PI, PI], y_range=[-1.5, 1.5, 1],
                  x_length=11.5, y_length=2.6, tips=False,
                  axis_config={"stroke_opacity": 0.6}).move_to(UP * 1.15)
        ax_h = Axes(x_range=[-2 * PI, 2 * PI, PI], y_range=[-1.4, 1.4, 1],
                    x_length=11.5, y_length=1.9, tips=False,
                    axis_config={"stroke_opacity": 0.4}).move_to(DOWN * 1.95)
        et_pi = VGroup(*[MathTex(s, font_size=30, color=C_TENUE).next_to(ax.c2p(v, 0), DR, buff=0.06)
                         for s, v in [(r"-\pi", -PI), (r"\pi", PI)]])

        vertici = []
        for a in range(-2, 2):  # onda quadra come un'unica spezzata
            y = 1 if a % 2 == 0 else -1
            vertici += [ax.c2p(a * PI, -y), ax.c2p(a * PI, y), ax.c2p((a + 1) * PI, y)]
        vertici.append(ax.c2p(2 * PI, 1))
        quadra = DashedVMobject(VMobject().set_points_as_corners(vertici).set_stroke(C_TENUE, 2),
                                num_dashes=160)

        did = cambia_didascalia(self, None, "Sopra: l'onda quadra da costruire")
        self.play(Create(ax), FadeIn(et_pi), Create(quadra), run_time=1.2)

        # ---------- somma parziale che cresce ----------
        K = ValueTracker(1)
        def curva_somma():
            k = max(1, int(round(K.get_value())))
            passo = 0.012 if k > 8 else 0.03
            return ax.plot(lambda x: somma(k, x), x_range=[-2 * PI, 2 * PI, passo],
                           use_smoothing=False, color=C_ACCENTO, stroke_width=3.5)
        S = always_redraw(curva_somma)
        lettura = always_redraw(lambda: MathTex(
            rf"S_N,\ N = {2 * max(1, int(round(K.get_value()))) - 1}",
            font_size=34, color=C_ACCENTO).next_to(ax, UP, buff=0.05).align_to(ax, LEFT)
            .add_background_rectangle(opacity=0.8, buff=0.06))

        # armoniche sotto: entrano una alla volta, le vecchie si attenuano
        armoniche = [ax_h.plot(lambda x, k=k: termine(k, x), x_range=[-2 * PI, 2 * PI, 0.02],
                               color=COLORI[i % len(COLORI)], stroke_width=3)
                     for i, k in enumerate(KS)]
        et_arm = [MathTex(rf"+\ \frac{{4}}{{\pi}}\cdot\frac{{\sin {k}x}}{{{k}}}" if k > 1
                          else r"\frac{4}{\pi}\sin x",
                          font_size=36, color=COLORI[i % len(COLORI)])
                  .next_to(ax_h, UP, buff=0.02).align_to(ax_h, LEFT)
                  .add_background_rectangle(opacity=0.85, buff=0.05)
                  for i, k in enumerate(KS)]

        self.play(Create(ax_h), run_time=0.6)
        did = cambia_didascalia(self, did, "Sotto: le armoniche dispari, una per volta")
        self.play(Create(armoniche[0]), FadeIn(et_arm[0]), run_time=0.8)
        self.play(FadeIn(S), FadeIn(lettura), run_time=0.6)
        self.bring_to_front(tit, dat, did)
        self.wait(0.6)
        for i in range(1, len(KS)):
            self.play(armoniche[i - 1].animate.set_stroke(opacity=0.25),
                      FadeOut(et_arm[i - 1]), Create(armoniche[i]), FadeIn(et_arm[i]),
                      K.animate.set_value(i + 1), run_time=0.9 if i < 3 else 0.6)
            self.wait(0.35)
            if i == 1:
                did = cambia_didascalia(self, did, "Ogni armonica corregge la somma sopra")
        self.wait(0.4)

        did = cambia_didascalia(self, did, "Più armoniche: la somma aderisce all'onda")
        self.play(armoniche[-1].animate.set_stroke(opacity=0.25), FadeOut(et_arm[-1]),
                  K.animate.set_value(12), run_time=1.5, rate_func=linear)
        self.wait(0.6)

        # ---------- Gibbs: zoom vicino al salto in x = 0 ----------
        X0, X1, Y0, Y1 = -0.15, 0.85, 0.55, 1.3
        riquadro = Rectangle(width=ax.c2p(X1, 0)[0] - ax.c2p(X0, 0)[0],
                             height=ax.c2p(0, Y1)[1] - ax.c2p(0, Y0)[1],
                             color=C_ACCENTO, stroke_width=2)
        riquadro.move_to((ax.c2p(X0, Y0) + ax.c2p(X1, Y1)) / 2)
        self.play(FadeOut(VGroup(*armoniche)), FadeOut(ax_h), Create(riquadro), run_time=0.8)

        az = Axes(x_range=[X0, X1, 1], y_range=[Y0, Y1, 1], x_length=6.0, y_length=2.1,
                  tips=False, axis_config={"stroke_opacity": 0.0}).move_to(DOWN * 1.95 + LEFT * 2.4)
        cornice = SurroundingRectangle(az, color=C_ACCENTO, buff=0, stroke_width=2)
        ponti = VGroup(DashedLine(riquadro.get_corner(DL), cornice.get_corner(UL)),
                       DashedLine(riquadro.get_corner(DR), cornice.get_corner(UR))).set_stroke(C_ACCENTO, 1.5, 0.6)
        salto = Line(az.c2p(0, Y0), az.c2p(0, 1), color=C_TENUE)
        uno = DashedLine(az.c2p(0, 1), az.c2p(X1, 1), color=C_TENUE, dash_length=0.08)
        picco = DashedLine(az.c2p(0, GIBBS), az.c2p(X1, GIBBS), color=C_C, dash_length=0.08)
        def curva_zoom():
            k = max(1, int(round(K.get_value())))
            return az.plot(lambda x: np.clip(somma(k, x), Y0, Y1), x_range=[0.0, X1, 0.002],
                           use_smoothing=False, color=C_ACCENTO, stroke_width=3.5)
        Sz = always_redraw(curva_zoom)
        e_uno = MathTex("1", font_size=28, color=C_TENUE).next_to(uno, RIGHT, buff=0.1)
        e_picco = MathTex(r"1{,}18", font_size=28, color=C_C).next_to(picco, RIGHT, buff=0.1)
        e_gibbs = Text("+9% del salto", font_size=26, color=C_C)
        e_gibbs.next_to(e_picco, RIGHT, buff=0.25)

        did = cambia_didascalia(self, did, "Zoom sul salto in x = 0")
        self.play(Create(cornice), Create(ponti), Create(salto), Create(uno), FadeIn(e_uno),
                  FadeIn(Sz), run_time=0.9)
        self.play(Create(picco), FadeIn(e_picco), FadeIn(e_gibbs), run_time=0.8)
        self.bring_to_front(tit, dat, did)
        did = cambia_didascalia(self, did, "Il picco si stringe ma non si abbassa", colore=C_ACCENTO)
        self.play(K.animate.set_value(K_MAX), run_time=4, rate_func=linear)
        self.wait(1)

        risultato_angolo(self, r"f(x) = \frac{4}{\pi}\sum_{n=0}^{\infty}\frac{\sin\big((2n+1)x\big)}{2n+1}",
                         did, posizione=RIGHT * 3.9 + DOWN * 2.35)
