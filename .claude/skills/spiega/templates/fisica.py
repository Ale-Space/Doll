"""TEMPLATE FISICA 2D: dinamica, piani inclinati, forze, moto, energia, oscillazioni.

Esempio: blocco su piano inclinato con attrito. Per quali angoli scivola?
Cosa si vede (≈25 s, niente passaggi: quelli vanno in chat): un ValueTracker
sull'angolo, le forze che si aggiornano da sole e le diverse CONFIGURAZIONI
FISICHE (fermo -> limite -> scivola).

Per pendoli, molle, urti, campi E/B, onde e ottica c'è anche manim_physics
(from manim_physics import *): Pendulum, SpaceScene, ElectricField, Charge, ...
Per moti semplici è più affidabile la soluzione analitica + ValueTracker (come qui).
"""
from doll_kit import *  # noqa: F401  (render.sh mette kit/ nel PYTHONPATH)
import numpy as np

MU = 0.4      # coefficiente di attrito statico
M, G = 2.0, 9.81
ANG_CRIT = np.degrees(np.arctan(MU))  # ≈ 21.8°


class Esercizio(Scene):
    def construct(self):
        tit = titolo(self, "Quando scivola il blocco?")
        dati(self, r"m = 2\,\mathrm{kg}, \quad \mu_s = 0{,}4")

        theta = ValueTracker(10)
        s = ValueTracker(0)  # quanto è scivolato il blocco lungo il piano
        O = np.array([-5.0, -2.4, 0])  # vertice del piano
        L = 7.0

        def dir_piano():
            t = np.radians(theta.get_value())
            return np.array([np.cos(t), np.sin(t), 0])

        def normale():
            t = np.radians(theta.get_value())
            return np.array([-np.sin(t), np.cos(t), 0])

        def centro_blocco():
            return O + dir_piano() * (L * 0.62 - s.get_value()) + normale() * 0.4

        piano = always_redraw(lambda: Polygon(
            O, O + np.array([L * np.cos(np.radians(theta.get_value())), 0, 0]),
            O + dir_piano() * L, color=C_TENUE, fill_opacity=0.25, stroke_width=3))
        arco = always_redraw(lambda: Angle(Line(O, O + RIGHT), Line(O, O + dir_piano()), radius=0.9, color=C_ACCENTO))
        lab_t = always_redraw(lambda: MathTex(rf"\theta = {theta.get_value():.1f}^\circ", font_size=32,
                                              color=C_ACCENTO).move_to(O + np.array([1.6, -0.4, 0])))
        blocco = always_redraw(lambda: Square(0.8, color=C_A, fill_opacity=0.8)
                               .rotate(np.radians(theta.get_value())).move_to(centro_blocco()))

        K = 0.07  # scala: 1 N -> 0.07 unità (le frecce non devono uscire dalla scena)
        def freccia(vec, col):
            return Arrow(centro_blocco(), centro_blocco() + vec * K, buff=0, color=col,
                         stroke_width=5, max_tip_length_to_length_ratio=0.15)

        def p_par():
            t = np.radians(theta.get_value()); return -dir_piano() * M * G * np.sin(t)

        def attrito():
            t = np.radians(theta.get_value())
            f = min(M * G * np.sin(t), MU * M * G * np.cos(t))
            return dir_piano() * f

        f_peso = always_redraw(lambda: freccia(np.array([0, -M * G, 0]), WHITE))
        f_par = always_redraw(lambda: freccia(p_par(), C_C))
        f_att = always_redraw(lambda: freccia(attrito(), C_B))

        legenda = VGroup(
            MathTex(r"mg", color=WHITE, font_size=30),
            MathTex(r"mg\sin\theta", color=C_C, font_size=30),
            MathTex(r"F_a", color=C_B, font_size=30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_corner(UR, buff=0.5).shift(DOWN * 1.1)

        def stato():
            ok = theta.get_value() <= ANG_CRIT
            t = Text("FERMO" if ok else "SCIVOLA", font_size=34, weight=BOLD,
                     color=C_B if ok else C_C).next_to(legenda, DOWN, buff=0.5)
            return t.align_to(legenda, RIGHT)
        lab_stato = always_redraw(stato)

        self.play(FadeIn(piano), FadeIn(arco), FadeIn(lab_t), FadeIn(blocco))
        self.play(FadeIn(f_peso), FadeIn(f_par), FadeIn(f_att), FadeIn(legenda), FadeIn(lab_stato))
        did = cambia_didascalia(self, None, "Angolo piccolo: l'attrito (verde) tiene")
        self.wait(1.2)
        did = cambia_didascalia(self, did, "Aumento θ: la spinta rossa cresce")
        self.play(theta.animate.set_value(ANG_CRIT), run_time=4, rate_func=linear)
        did = cambia_didascalia(self, did, f"θ ≈ {ANG_CRIT:.1f}°: il limite, tan θ = μ", colore=C_ACCENTO)
        self.wait(1.2)
        did = cambia_didascalia(self, did, "Oltre θc l'attrito non basta")
        self.play(theta.animate.set_value(35), run_time=3, rate_func=linear)
        did = cambia_didascalia(self, did, "Il blocco scivola e accelera")
        self.play(s.animate.set_value(2.9), run_time=2.5, rate_func=rush_into)  # s ∝ t²
        self.wait(1.5)

        risultato_angolo(self, rf"\theta_c = \arctan\mu_s \approx {ANG_CRIT:.1f}^\circ", did)
