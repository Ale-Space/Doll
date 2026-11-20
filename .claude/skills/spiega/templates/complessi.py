"""TEMPLATE ANALISI COMPLESSA: mappa conforme + integrale lungo una curva chiusa.

Esempio: w = e^z sul rettangolo -1 <= Re z <= 1, -1,2 <= Im z <= 1,2,
poi f(z) = 1/(1 + z^2) integrata lungo una curva che gira attorno al polo z = i.
Cosa si vede (≈33 s, niente passaggi: i conti vanno in chat):
  1. la griglia del piano z; due rette evidenziate che si incrociano ad angolo retto;
  2. la griglia si deforma con continuità nella sua immagine:
        g_t(z) = (1 - t) z + t f(z),  t: 0 -> 1   (ValueTracker su t)
     ogni linea è campionata fitta e trasformata punto per punto. Nota: g_t è
     olomorfa, quindi anche le griglie intermedie sono conformi dove g_t' != 0;
     il quadratino dell'angolo retto resta retto per tutta l'animazione;
  3. con e^z: le verticali diventano cerchi, le orizzontali raggi;
  4. i poli ±i, una curva chiusa γ attorno a i; l'integrale calcolato in diretta
     (numericamente, sulla curva disegnata) resta π mentre γ si deforma;
  5. il residuo nel polo interno e il risultato 2πi·Res.

Per un'altra mappa cambia `F` (vettorializzata con numpy), il dominio e, se serve,
la scala U. Attenzione ai punti critici (F' = 0, es. z = 0 per z^2): lì l'angolo
NON si conserva (con z^2 raddoppia: fallo vedere come controesempio!).
  - z^2 sul primo quadrante: rette -> parabole, il quadrante diventa un semipiano;
  - 1/z: rette -> cerchi per l'origine (evita una griglia che passa per 0);
  - Joukowski z + 1/z: cerchi centrati in 0 -> ellissi; il cerchio unitario -> segmento [-2, 2];
    un cerchio spostato -> profilo alare.

Altre idee:
  - RADICI DELL'UNITÀ: il cerchio unitario, z^n = 1; un punto e^{iθ} con ValueTracker
    su θ e il punto z^n che gira n volte più veloce; si accendono le n radici quando z^n = 1.
  - FORMULA DI EULERO: e^{iθ} come punto che ruota; a destra cos θ e sin θ tracciati
    come proiezioni (stesso meccanismo di fasori.py).
  - MÖBIUS (az + b)/(cz + d): griglia polare (cerchi e raggi) che si trasforma;
    rette e cerchi restano rette o cerchi; il disco unitario va nel semipiano.
  - RESIDUI PER INTEGRALI REALI: ∫ dx/(1+x^2) = π. Il segmento [-R, R] più la
    semicirconferenza di raggio R; R cresce (ValueTracker) e il contributo dell'arco,
    calcolato in diretta, tende a 0, mentre il totale resta π (= 2πi·Res in i).
"""
from doll_kit import *  # noqa: F401  (render.sh mette kit/ nel PYTHONPATH)
import numpy as np

TITOLO = "Mappe conformi e residui"


def F(z):
    return np.exp(z)


F_TEX = r"w = e^{z}"
XS = np.linspace(-1, 1, 9)          # rette verticali Re z = c
YS = np.linspace(-1.2, 1.2, 9)      # rette orizzontali Im z = c
Z0 = 0.5 + 0.6j                     # incrocio evidenziato (deve stare sulla griglia)
H = 1e-6                            # per la derivata numerica

# seconda parte: f con i suoi poli e i residui (verificati con SymPy)
def f_int(z):
    return 1 / (1 + z ** 2)


F_INT_TEX = r"f(z) = \frac{1}{1+z^2}"
POLI = [1j, -1j]
RES_TEX = r"\mathrm{Res}_{z=i} f = \frac{1}{2i}"

U = 0.95                            # unità del piano complesso (in unità Manim)
O = np.array([-2.2, -0.3, 0.0])     # dove sta lo 0 del piano grande


def p(w: complex, o=O, u=U) -> np.ndarray:
    return o + u * np.array([w.real, w.imag, 0.0])


def fmt_c(w: complex) -> str:
    """Numero complesso in LaTeX con la virgola decimale, parti nulle omesse."""
    def n(x):
        return f"{x:.2f}".replace(".", "{,}")
    re_, im_ = (0.0 if abs(w.real) < 5e-3 else w.real), (0.0 if abs(w.imag) < 5e-3 else w.imag)
    if im_ == 0:
        return n(re_)
    if re_ == 0:
        return n(im_) + "\\,i"
    return n(re_) + (" + " if im_ > 0 else " - ") + n(abs(im_)) + "\\,i"


class Esercizio(Scene):
    def construct(self):
        tit = titolo(self, TITOLO)
        dat = dati(self, F_TEX)

        # ---------- piano di sfondo (fisso) ----------
        sfondo = NumberPlane(x_range=[-2, 3.5, 1], y_range=[-3, 3, 1], x_length=5.5 * U, y_length=6 * U,
                             background_line_style={"stroke_opacity": 0.12},
                             axis_config={"stroke_opacity": 0.45})
        sfondo.shift(O - sfondo.c2p(0, 0))
        e_re = MathTex(r"\mathrm{Re}", font_size=30, color=C_TENUE).next_to(sfondo.c2p(3.5, 0), DOWN, buff=0.1).shift(LEFT * 0.35)
        e_im = MathTex(r"\mathrm{Im}", font_size=30, color=C_TENUE).next_to(sfondo.c2p(0, 3), RIGHT, buff=0.1).shift(DOWN * 0.2)
        self.play(FadeIn(sfondo), FadeIn(e_re), FadeIn(e_im), run_time=0.6)

        # ---------- griglia che si deforma ----------
        t = ValueTracker(0)
        s_ = np.linspace(0, 1, 90)
        linee_z = ([(XS[i] + 1j * (YS[0] + (YS[-1] - YS[0]) * s_), C_A) for i in range(len(XS))] +
                   [((XS[0] + (XS[-1] - XS[0]) * s_) + 1j * YS[j], C_B) for j in range(len(YS))])

        def g(z):
            return (1 - t.get_value()) * z + t.get_value() * F(z)

        def linea(zs, col, w=2.5, op=0.9):
            ws = g(zs)
            return VMobject().set_points_smoothly([p(complex(c)) for c in ws]).set_stroke(col, w, op)

        griglia = always_redraw(lambda: VGroup(*[linea(zs, c) for zs, c in linee_z]))

        # le due rette per Z0 e il quadratino dell'angolo retto
        r_v = Z0.real + 1j * (YS[0] + (YS[-1] - YS[0]) * s_)
        r_h = (XS[0] + (XS[-1] - XS[0]) * s_) + 1j * Z0.imag
        evid = always_redraw(lambda: VGroup(linea(r_v, C_A, 6, 1), linea(r_h, C_B, 6, 1)))

        def quadratino():
            dg = (g(Z0 + H) - g(Z0)) / H            # g_t'(Z0)
            u1 = dg / abs(dg)                        # direzione dell'immagine di "1"
            u2 = 1j * u1                             # immagine di "i": ruotata di 90°
            L = 0.28 / U
            q0 = g(Z0)
            sq = VMobject().set_points_as_corners([p(q0 + L * u1), p(q0 + L * (u1 + u2)), p(q0 + L * u2)])
            return VGroup(sq.set_stroke(C_ACCENTO, 4), Dot(p(q0), radius=0.06, color=C_ACCENTO))
        quad = always_redraw(quadratino)

        # piccolo promemoria del piano z, a destra
        UZ, OZ = 0.7, np.array([4.7, -0.6, 0.0])
        rif = VGroup(*[VMobject().set_points_smoothly([p(complex(c), OZ, UZ) for c in zs]).set_stroke(col, 1.8, 0.8)
                       for zs, col in linee_z])
        for zs, col in [(r_v, C_A), (r_h, C_B)]:
            rif.add(VMobject().set_points_smoothly([p(complex(c), OZ, UZ) for c in zs]).set_stroke(col, 4.5))
        rif.add(Dot(p(Z0, OZ, UZ), radius=0.06, color=C_ACCENTO))
        e_rif = Text("piano z", font_size=24, color=C_TENUE).next_to(rif, UP, buff=0.2)
        e_grande = always_redraw(lambda: Text("piano z" if t.get_value() < 0.5 else "piano w", font_size=26,
                                              color=C_TENUE).move_to(O + np.array([-1.5, 2.3, 0])))

        did = cambia_didascalia(self, None, "La griglia del piano z")
        self.play(Create(griglia), FadeIn(e_grande), run_time=1.5)
        self.bring_to_front(tit, dat, did)
        did = cambia_didascalia(self, did, "Due rette che si incrociano ad angolo retto")
        self.play(FadeIn(evid), Create(quad), run_time=0.8)
        self.wait(0.8)
        self.play(FadeIn(rif), FadeIn(e_rif), run_time=0.6)

        did = cambia_didascalia(self, did, "Applico la mappa: la griglia si deforma")
        self.play(t.animate.set_value(1), run_time=4.5, rate_func=smooth)
        did = cambia_didascalia(self, did, "Verticali → cerchi, orizzontali → raggi")
        self.wait(2)
        did = cambia_didascalia(self, did, "L'angolo resta retto: la mappa è conforme", colore=C_ACCENTO)
        self.play(Indicate(quad, color=C_ACCENTO, scale_factor=1.4), run_time=1)
        self.wait(1)

        # ---------- seconda parte: integrale lungo una curva chiusa ----------
        self.play(FadeOut(griglia), FadeOut(evid), FadeOut(quad), FadeOut(rif), FadeOut(e_rif),
                  FadeOut(e_grande), run_time=0.6)
        nuovi = MathTex(F_INT_TEX, font_size=36)
        fit(nuovi, max_w=5.5, max_h=2.4).to_corner(UR, buff=0.3)
        nuovi.add_background_rectangle(opacity=0.85, buff=0.15)
        self.play(Transform(dat, nuovi), run_time=0.6)

        croci = VGroup(*[Cross(scale_factor=0.12, stroke_width=5, stroke_color=C_C).move_to(p(z)) for z in POLI])
        e_poli = VGroup(MathTex("i", font_size=36, color=C_C).move_to(p(POLI[0]) + LEFT * 0.8),
                        MathTex("-i", font_size=36, color=C_C).next_to(p(POLI[1]), LEFT, buff=0.2))
        did = cambia_didascalia(self, did, "Due poli: z = i e z = −i")
        self.play(FadeIn(croci), FadeIn(e_poli), run_time=0.7)

        s = ValueTracker(0)
        TH = np.linspace(0, TAU, 600, endpoint=False)
        C_BLOB, C_PICC = 0.3 + 1.0j, POLI[0]
        def gamma():
            sv = s.get_value()
            blob = C_BLOB + (1.0 + 0.3 * np.cos(3 * TH)) * np.exp(1j * TH)
            cerchio = C_PICC + 0.35 * np.exp(1j * TH)
            return (1 - sv) * blob + sv * cerchio
        def curva():
            zs = gamma()
            c = VMobject().set_points_smoothly([p(complex(z)) for z in zs[::6]] + [p(complex(zs[0]))])
            c.set_stroke(C_ACCENTO, 4)
            k = 150  # freccina del verso (antiorario) a un quarto di giro
            a = Arrow(p(complex(zs[k])), p(complex(zs[k + 25])), buff=0, color=C_ACCENTO, stroke_width=4,
                      max_tip_length_to_length_ratio=0.9, tip_length=0.25)
            return VGroup(c, a)
        def integrale():
            zs = gamma()
            dz = np.roll(zs, -1) - zs
            zm = (zs + np.roll(zs, -1)) / 2
            return complex(np.sum(f_int(zm) * dz))   # regola del punto medio su curva chiusa
        gam = always_redraw(curva)
        e_gam = always_redraw(lambda: MathTex(r"\gamma", font_size=36, color=C_ACCENTO)
                              .move_to(p(complex(gamma()[40])) + RIGHT * 0.35 + UP * 0.1))
        lettura = always_redraw(lambda: MathTex(
            rf"\oint_\gamma f\,dz \approx {fmt_c(integrale())}", font_size=40)
            .move_to(RIGHT * 3.6 + UP * 0.9).add_background_rectangle(opacity=0.85, buff=0.1))

        did = cambia_didascalia(self, did, "Integro f lungo la curva chiusa γ")
        punto = Dot(color=WHITE, radius=0.07)
        self.play(Create(gam), FadeIn(e_gam), run_time=1.2)
        percorso = gam[0].copy()
        self.play(MoveAlongPath(punto, percorso), FadeIn(lettura), run_time=1.6, rate_func=linear)
        self.remove(punto)
        self.bring_to_front(tit, dat, did)

        did = cambia_didascalia(self, did, "La curva cambia, l'integrale no")
        self.play(s.animate.set_value(1), run_time=3)
        self.play(s.animate.set_value(0.4), run_time=1.5)
        e_res = MathTex(RES_TEX, font_size=34, color=C_C).move_to(RIGHT * 3.6 + DOWN * 0.4)
        e_res.add_background_rectangle(opacity=0.85, buff=0.1)
        did = cambia_didascalia(self, did, "Conta solo il polo dentro γ: il residuo")
        self.play(FadeIn(e_res), Indicate(croci[0], color=C_C, scale_factor=1.6), run_time=1)
        self.wait(1)

        risultato_angolo(self, r"\oint_\gamma \frac{dz}{1+z^2} = 2\pi i\cdot\frac{1}{2i} = \pi", did,
                         posizione=RIGHT * 3.6 + DOWN * 2.0)
