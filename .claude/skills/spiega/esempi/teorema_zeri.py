"""Teorema degli zeri (Bolzano). Gesto: la bisezione; stessi passi sulla curva continua e su quella che salta.
f = x^3 - x - 1 su [1, 2]; c = 1,3247. g = f (x <= 1,2), f + 1 (x > 1,2).  Vedi piano.md."""
from doll_kit import *  # noqa: F401,F403
import numpy as np


def f(x):
    return x ** 3 - x - 1


XJ = 1.2


def g(x):
    return f(x) + (1.0 if x > XJ else 0.0)


def passi_bisezione(F, a, b, n):
    """Lista dei passi (m, segno, 'sx'|'dx') e intervallo finale dopo n passi."""
    out = []
    for _ in range(n):
        m = (a + b) / 2
        if F(m) < 0:
            out.append((m, -1, "sx"))
            a = m
        else:
            out.append((m, 1, "dx"))
            b = m
    return out, a, b


C_ROOT = 1.3247179572447460


class Esercizio(Scene):
    def bisezione(self, ax, F, did, ta, tb, n_lenti, n_veloci, testi):
        passi, _, _ = passi_bisezione(F, 1.0, 2.0, n_lenti + n_veloci)
        for k, (m, s, lato) in enumerate(passi[:n_lenti]):
            col = C_PIU if s > 0 else C_MENO
            pm = Dot(ax.c2p(m, F(m)), color=WHITE, radius=0.09)
            guida = DashedLine(ax.c2p(m, 0), ax.c2p(m, F(m)), color=C_TENUE, dash_length=0.08)
            self.play(FadeIn(pm), Create(guida), run_time=0.4)
            self.play(pm.animate.set_color(col), run_time=0.3)
            tr = ta if lato == "sx" else tb
            self.play(tr.animate.set_value(m), FadeOut(pm), FadeOut(guida), run_time=0.8, rate_func=smooth)
            if k == 0:
                did = cambia_didascalia(self, did, testi[0])
        # passi veloci
        _, a7, b7 = passi_bisezione(F, 1.0, 2.0, n_lenti + n_veloci)
        did = cambia_didascalia(self, did, testi[1])
        self.play(ta.animate.set_value(a7), tb.animate.set_value(b7), run_time=2.4, rate_func=smooth)
        return did

    def construct(self):
        # ---------------- ATTO 0 ----------------
        tit = titolo(self, "Teorema degli zeri")
        d = dati(self, r"f\in C([a, b]),\ f(a)f(b)<0\ \Rightarrow\ \exists c:\ f(c)=0", font_size=30, max_w=6.2)

        # ---------------- ATTO 1: l'oggetto ----------------
        ax = Axes(x_range=[0.85, 2.15, 0.5], y_range=[-2, 6.5, 2], x_length=7.2, y_length=4.7,
                  axis_config={"color": C_TENUE, "include_ticks": False}).shift(LEFT * 1.6 + DOWN * 0.15)
        lab = ax.get_axis_labels(MathTex("x", font_size=28, color=C_TENUE), MathTex("y", font_size=28, color=C_TENUE))
        graf = ax.plot(f, x_range=[1.0, 2.0], color=C_OGGETTO, stroke_width=4)
        PA = Dot(ax.c2p(1, f(1)), color=C_MENO, radius=0.1)
        PB = Dot(ax.c2p(2, f(2)), color=C_PIU, radius=0.1)
        la = MathTex("a", font_size=30).next_to(PA, DL, buff=0.08)
        lb = MathTex("b", font_size=30).next_to(PB, UL, buff=0.08)
        self.play(Create(ax), FadeIn(lab), Create(graf), run_time=1.2)
        self.play(FadeIn(PA), FadeIn(PB), FadeIn(la), FadeIn(lb), run_time=0.5)
        did = cambia_didascalia(self, None, "Senza stacchi, attraversa l'asse")
        tp = ValueTracker(1.0)
        punto = always_redraw(lambda: Dot(ax.c2p(tp.get_value(), f(tp.get_value())), color=WHITE, radius=0.09))
        self.add(punto)
        self.play(tp.animate.set_value(2.0), run_time=2.4, rate_func=smooth)
        self.play(FadeOut(punto), run_time=0.2)
        self.remove(punto)

        # ---------------- ATTO 2: bisezione ----------------
        ta, tb = ValueTracker(1.0), ValueTracker(2.0)
        F_ = f
        bar = always_redraw(lambda: Line(ax.c2p(ta.get_value(), 0), ax.c2p(tb.get_value(), 0), color=C_X, stroke_width=9))
        ea = always_redraw(lambda: VGroup(
            DashedLine(ax.c2p(ta.get_value(), 0), ax.c2p(ta.get_value(), F_(ta.get_value())), color=C_MENO, stroke_width=2, dash_length=0.08),
            Dot(ax.c2p(ta.get_value(), F_(ta.get_value())), color=C_MENO, radius=0.1)))
        eb = always_redraw(lambda: VGroup(
            DashedLine(ax.c2p(tb.get_value(), 0), ax.c2p(tb.get_value(), F_(tb.get_value())), color=C_PIU, stroke_width=2, dash_length=0.08),
            Dot(ax.c2p(tb.get_value(), F_(tb.get_value())), color=C_PIU, radius=0.1)))
        XP = 3.45
        e1 = Text("valore a sinistra", font_size=22, color=C_MENO).move_to([XP, 1.2, 0], aligned_edge=LEFT)
        v1 = numero_vivo(self, lambda: virgola(F_(ta.get_value()), 3), [XP, 0.75, 0], colore=C_MENO, size=30)
        e2 = Text("valore a destra", font_size=22, color=C_PIU).move_to([XP, 0.05, 0], aligned_edge=LEFT)
        v2 = numero_vivo(self, lambda: virgola(F_(tb.get_value()), 3), [XP, -0.4, 0], colore=C_PIU, size=30)
        e3 = Text("ampiezza", font_size=22, color=C_X).move_to([XP, -1.1, 0], aligned_edge=LEFT)
        v3 = numero_vivo(self, lambda: virgola(tb.get_value() - ta.get_value(), 3), [XP, -1.55, 0], colore=C_X, size=30)
        self.remove(la, lb)
        self.play(FadeOut(PA), FadeOut(PB), FadeOut(la), FadeOut(lb), FadeIn(bar), FadeIn(ea), FadeIn(eb),
                  FadeIn(e1), FadeIn(e2), FadeIn(e3), run_time=0.5)
        self.add(v1, v2, v3)
        did = cambia_didascalia(self, did, "Tieni la metà dove il segno cambia")
        did = self.bisezione(ax, f, did, ta, tb, 4, 3, ["Il segno cambia sempre in una metà",
                                                        "Gli estremi si stringono su un punto"])
        # ---------------- ATTO 3: conclusione ----------------
        pc = Dot(ax.c2p(C_ROOT, 0), color=C_RIF, radius=0.12)
        lc = MathTex("c", font_size=32, color=C_RIF).next_to(pc, DOWN, buff=0.15)
        self.play(FadeIn(pc, scale=2.0), FadeIn(lc), run_time=0.6)
        did = cambia_didascalia(self, did, "Entrambi i valori vanno a 0: f(c) = 0", colore=C_ACCENTO)
        self.wait(1.1)

        # ---------------- ATTO 4: controesempio ----------------
        for v in (v1, v2, v3):
            v.clear_updaters()
        self.play(*[FadeOut(m) for m in (graf, bar, ea, eb, pc, lc, did, v1, v2, v3)], run_time=0.5)
        self.remove(bar, ea, eb, v1, v2, v3)
        F_ = g
        graf_s = ax.plot(g, x_range=[1.0, XJ], color=C_CONTRO, stroke_width=4)
        graf_d = ax.plot(g, x_range=[XJ + 1e-6, 2.0], color=C_CONTRO, stroke_width=4)
        pieno = Dot(ax.c2p(XJ, f(XJ)), color=C_CONTRO, radius=0.09)
        vuoto = Circle(radius=0.09, color=C_CONTRO, stroke_width=3, fill_color=BLACK, fill_opacity=1).move_to(ax.c2p(XJ, f(XJ) + 1))
        ta.set_value(1.0)
        tb.set_value(2.0)
        bar = always_redraw(lambda: Line(ax.c2p(ta.get_value(), 0), ax.c2p(tb.get_value(), 0), color=C_X, stroke_width=9))
        ea = always_redraw(lambda: VGroup(
            DashedLine(ax.c2p(ta.get_value(), 0), ax.c2p(ta.get_value(), g(ta.get_value())), color=C_MENO, stroke_width=2, dash_length=0.08),
            Dot(ax.c2p(ta.get_value(), g(ta.get_value())), color=C_MENO, radius=0.1)))
        eb = always_redraw(lambda: VGroup(
            DashedLine(ax.c2p(tb.get_value(), 0), ax.c2p(tb.get_value(), g(tb.get_value())), color=C_PIU, stroke_width=2, dash_length=0.08),
            Dot(ax.c2p(tb.get_value(), g(tb.get_value())), color=C_PIU, radius=0.1)))
        v1 = numero_vivo(self, lambda: virgola(g(ta.get_value()), 3), [XP, 0.75, 0], colore=C_MENO, size=30)
        v2 = numero_vivo(self, lambda: virgola(g(tb.get_value()), 3), [XP, -0.4, 0], colore=C_PIU, size=30)
        v3 = numero_vivo(self, lambda: virgola(tb.get_value() - ta.get_value(), 3), [XP, -1.55, 0], colore=C_X, size=30)
        self.play(Create(graf_s), Create(graf_d), FadeIn(pieno), FadeIn(vuoto), FadeIn(bar), FadeIn(ea), FadeIn(eb), run_time=1.0)
        self.add(v1, v2, v3)
        did = cambia_didascalia(self, None, "Stessa prova, ma la curva salta")
        did = self.bisezione(ax, g, did, ta, tb, 4, 3, ["Stessa regola: tieni la metà che cambia segno",
                                                        "Si stringono sul salto, non sull'asse"])
        self.wait(0.1)
        did = cambia_didascalia(self, did, "I valori restano lontani da 0: nessuno zero", colore=C_CONTRO)
        self.wait(1.1)
        for v in (v1, v2, v3):
            v.clear_updaters()

        # ---------------- ATTO 5: risultato ----------------
        risultato_angolo(self, r"f\ \text{continua su }[a, b],\ f(a)f(b)<0\ \Rightarrow\ \exists\, c:\ f(c)=0",
                         vecchia_didascalia=did, attesa=2.0)
