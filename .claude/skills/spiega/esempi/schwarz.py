"""ESEMPIO DI RIFERIMENTO: teorema di Schwarz (Analisi II). Il livello richiesto per un video di teorema.

Frase wow: R e' un numero solo; letto per righe e per colonne da' le due miste, e con le miste continue
           i due valori sono costretti a coincidere.
Gesto visivo: Lagrange "schiaccia" il quadratino su un punto, in due modi diversi.
Atti:
  1. superficie sul quadrato, vertici con segni, il quarto vertice che manca il piano (= delta^2 R);
     barre: per righe e per colonne il tratto rosso e' lo stesso;
  2. vista dall'alto, mappa di colore della mista: due lati -> un segmento -> un punto, nei due ordini;
     i due punti stanno sulla stessa curva di livello (stesso colore = R);
  3. delta -> 0: il colore si uniforma, R tende a entrambe le miste;
  4. controesempio xy(x^2-y^2)/(x^2+y^2): la mista dipende solo dalla direzione, lo zoom non cambia nulla;
     ogni ordine legge un asse diverso (+1 e -1), R = 0;
  5. risultato.
Numeri (verificati con SymPy): f = 3x/4 + y/4 + xy/2 + x^2y/2 - x^3y^2/2 + x^5y^3/5, f_xy = 1/2 + x - 3x^2y + 3x^4y^2;
  delta = 1: R = 7/10, (xi, eta) = (0,3065; 0,3924), (xi', eta') = (0,6790; 0,4326); R -> 1/2 per delta -> 0.
  Controesempio: mista (x^6 + 9x^4y^2 - 9x^2y^4 - y^6)/rho^6, +1 su y=0, -1 su x=0, estremi +-sqrt(2); R = 0;
  punti di Lagrange sulla bisettrice a delta*sqrt(sqrt5 - 2).
Durata circa 45 s.
"""
from manim import *
from doll_kit import *
from scipy.optimize import brentq
from contourpy import contour_generator


# ------------------------------------ funzione liscia --------------------------------------------
def f(x, y): return 0.75*x + 0.25*y + 0.5*x*y + 0.5*x**2*y - 0.5*x**3*y**2 + 0.2*x**5*y**3
def fx(x, y): return 0.75 + 0.5*y + x*y - 1.5*x**2*y**2 + x**4*y**3
def fy(x, y): return 0.25 + 0.5*x + 0.5*x**2 - x**3*y + 0.6*x**5*y**2
def fxy(x, y): return 0.5 + x - 3*x**2*y + 3*x**4*y**2


GRIGLIA = np.linspace(0, 1, 201)


def radice(fun):
    v = fun(GRIGLIA)
    i = np.where(np.sign(v[:-1]) * np.sign(v[1:]) < 0)[0]
    return brentq(fun, GRIGLIA[i[0]], GRIGLIA[i[0] + 1])


def valore_R(d):
    return (f(d, d) - f(0, d) - f(d, 0) + f(0, 0)) / d**2


def punti(d):
    """Punti di Lagrange in coordinate relative (0..1) del quadrato di lato d."""
    R = valore_R(d)
    e = radice(lambda u: (fy(d, u*d) - fy(0, u*d)) / d - R)
    a = radice(lambda u: fxy(u*d, e*d) - R)
    a2 = radice(lambda u: (fx(u*d, d) - fx(u*d, 0)) / d - R)
    e2 = radice(lambda u: fxy(a2*d, u*d) - R)
    return a, e, a2, e2


def g_mista(x, y):
    """Mista del controesempio: omogenea di grado 0, dipende solo dalla direzione."""
    r2 = x*x + y*y
    return (x**6 + 9*x**4*y**2 - 9*x**2*y**4 - y**6) / r2**3


C_ERR = C_ERRORE


class Esercizio(ThreeDScene):
    def fisso(self, *ms):
        fisso(self, *ms)

    def orientato(self, m):
        return orientato(self, m)

    def construct(self):
        tit, did, d = self.parte_numero()
        did, d = self.parte_lagrange(tit, did, d)
        self.parte_controesempio(tit, did, d)

    # ------------------------------------- 1: il numero R -------------------------------------
    def parte_numero(self):
        self.set_camera_orientation(phi=58 * DEGREES, theta=-90 * DEGREES)
        KXY, KZ = 3.0, 1.45
        OX, OZ = -3.05, -1.35

        def W(a, b, c=0.0):
            return np.array([(a - 0.5) * KXY + OX, (b - 0.5) * KXY, c * KZ + OZ])

        tit = titolo(self, "Teorema di Schwarz")
        d = dati(self, r"f\in C^2\ \Rightarrow\ \partial_x\partial_y f=\partial_y\partial_x f", font_size=34)

        patch = Surface(lambda a, b: W(a, b, f(a, b)), u_range=[0, 1], v_range=[0, 1], resolution=(14, 14),
                        fill_opacity=0.82, stroke_width=0.4, **SUPERFICIE)
        base = Polygon(W(0, 0), W(1, 0), W(1, 1), W(0, 1), color=GREY_B, stroke_width=2.5,
                       fill_color=GREY_E, fill_opacity=0.5)
        base.set_shade_in_3d(True)     # altrimenti verrebbe disegnato sopra la superficie
        base.z_index_group = VectorizedPoint(W(0.5, 3.0, -3.0))    # sempre dietro a tutte le facce
        vertici = [(0, 0, C_PIU, "+"), (1, 1, C_PIU, "+"), (1, 0, C_MENO, "−"), (0, 1, C_MENO, "−")]
        pil = VGroup(*[DashedLine(W(a, b), W(a, b, f(a, b)), color=GREY_B, stroke_width=2, dash_length=0.1)
                       for a, b, *_ in vertici])

        def punto(p, colore, r=0.085):
            return self.orientato(Dot(p, radius=r, color=colore))

        pall = [punto(W(a, b, f(a, b)), c) for a, b, c, _ in vertici]

        def segno(a, b, c, s):
            est = np.array([(a - 0.5) * 0.85, 0, 0.32])
            return self.orientato(Text(s, font_size=38, color=c, weight=BOLD)).move_to(W(a, b, f(a, b)) + est)

        segni = [segno(*v) for v in vertici]

        def assi_lab(testo, p, c):
            return self.orientato(MathTex(testo, font_size=30, color=c)).move_to(p)

        lx = assi_lab("x", W(0.5, 0) + DOWN * 0.42 + IN * 0.1, C_X)
        ly = assi_lab("y", W(0, 0.5) + LEFT * 0.42, C_Y)

        self.play(FadeIn(base), FadeIn(patch), FadeIn(lx), FadeIn(ly), run_time=0.7)
        self.play(*[Create(p) for p in pil], *[FadeIn(p) for p in pall], *[FadeIn(s) for s in segni], run_time=0.7)
        did = cambia_didascalia(self, None, "Quattro vertici del quadrato, segni alternati")
        nuova = MathTex(r"R=\frac{f(\delta,\delta)-f(0,\delta)-f(\delta,0)+f(0,0)}{\delta^2}", font_size=32)
        fit(nuova, max_w=6.0).to_corner(UR, buff=0.3)
        nuova.add_background_rectangle(opacity=0.85, buff=0.15)
        self.fisso(nuova)
        self.play(FadeOut(d), FadeIn(nuova), run_time=0.5)
        d = nuova
        self.wait(0.4)

        # ---- piano per tre vertici e stacco del quarto ----
        z_piano = f(1, 0) + f(0, 1) - f(0, 0)
        piano = Polygon(W(0, 0, f(0, 0)), W(1, 0, f(1, 0)), W(1, 1, z_piano), W(0, 1, f(0, 1)),
                        color=C_RIF, stroke_width=2, fill_color=C_RIF, fill_opacity=0.32)
        stacco = Line(W(1, 1, z_piano), W(1, 1, f(1, 1)), color=C_ERR, stroke_width=9)
        p_q = punto(W(1, 1, z_piano), C_RIF, 0.07)
        l_st = self.orientato(MathTex(r"\delta^2 R", font_size=34, color=C_ERR)).move_to(
            W(1, 1, 0.5 * (z_piano + f(1, 1))) + RIGHT * 0.58)
        did = cambia_didascalia(self, did, "Il quarto vertice manca il piano: è δ²R")
        self.play(FadeIn(piano), FadeIn(p_q), Create(stacco), FadeIn(l_st), run_time=0.8)
        self.wait(1.0)

        # ---- le due letture ----
        def bordo(fun, colore):
            t = np.linspace(0, 1, 30)
            return curva(np.array([fun(a) for a in t]), colore, 7)

        r1, r0 = f(1, 1) - f(0, 1), f(1, 0) - f(0, 0)
        s1, s0 = f(1, 1) - f(1, 0), f(0, 1) - f(0, 0)
        S = 1.75
        X0 = 1.75
        H = 0.3

        def barra(xi, lung, y, colore):
            return Rectangle(width=lung, height=H, stroke_width=0, fill_color=colore, fill_opacity=1) \
                .move_to([xi + lung / 2, y, 0])

        Y1, Y0, Y3, Y2 = 1.35, 0.9, -0.75, -1.2
        ini_c = X0 + (r0 - s0) * S
        xr = X0 + r0 * S                     # il tratto rosso comincia qui per entrambi

        b_r1, b_r0, e_r = barra(X0, r1 * S, Y1, C_X), barra(X0, r0 * S, Y0, C_X), barra(xr, (r1 - r0) * S, Y0, C_ERR)
        l_r1 = MathTex(r"y=\delta", font_size=26, color=C_X).next_to(b_r1, LEFT, buff=0.1)
        l_r0 = MathTex(r"y=0", font_size=26, color=C_X).next_to(b_r0, LEFT, buff=0.1)
        hd1 = Text("salita in x", font_size=25, color=C_X).move_to([2.15, Y1 + 0.5, 0])
        eq1 = MathTex(r"R\approx\partial_y\partial_x f", font_size=30, color=C_ERR).next_to(b_r1, RIGHT, buff=0.12).shift(DOWN * 0.22)

        b_s1, b_s0, e_s = barra(ini_c, s1 * S, Y3, C_Y), barra(ini_c, s0 * S, Y2, C_Y), barra(xr, (s1 - s0) * S, Y2, C_ERR)
        l_s1 = MathTex(r"x=\delta", font_size=26, color=C_Y).next_to(b_s1, LEFT, buff=0.1)
        l_s0 = MathTex(r"x=0", font_size=26, color=C_Y).next_to(b_s0, LEFT, buff=0.1)
        hd2 = Text("salita in y", font_size=25, color=C_Y).move_to([2.15, Y3 + 0.5, 0])
        eq2 = MathTex(r"R\approx\partial_x\partial_y f", font_size=30, color=C_ERR).next_to(b_s1, RIGHT, buff=0.12).shift(DOWN * 0.22)

        guide = VGroup(*[DashedLine([x_, Y0 - 0.15, 0], [x_, Y3 + 0.15, 0], color=C_ERR, stroke_width=1.8, dash_length=0.08)
                         for x_ in (xr, xr + (r1 - r0) * S)])
        tutto = [b_r1, b_r0, e_r, l_r1, l_r0, hd1, eq1, b_s1, b_s0, e_s, l_s1, l_s0, hd2, eq2, guide]
        self.fisso(*tutto)

        bx = VGroup(bordo(lambda t: W(t, 0, f(t, 0)), C_X), bordo(lambda t: W(t, 1, f(t, 1)), C_X))
        by = VGroup(bordo(lambda t: W(0, t, f(0, t)), C_Y), bordo(lambda t: W(1, t, f(1, t)), C_Y))

        did = cambia_didascalia(self, did, "Per righe: salita in x, sopra meno sotto")
        self.play(FadeOut(piano), FadeOut(p_q), Create(bx), FadeIn(hd1), FadeIn(l_r1), FadeIn(l_r0),
                  GrowFromEdge(b_r1, LEFT), GrowFromEdge(b_r0, LEFT), run_time=0.8)
        self.play(GrowFromEdge(e_r, LEFT), FadeIn(eq1), run_time=0.5)
        self.wait(0.7)

        did = cambia_didascalia(self, did, "Per colonne: salita in y, destra meno sinistra")
        self.play(FadeOut(bx), Create(by), FadeIn(hd2), FadeIn(l_s1), FadeIn(l_s0),
                  GrowFromEdge(b_s1, LEFT), GrowFromEdge(b_s0, LEFT), run_time=0.8)
        self.play(GrowFromEdge(e_s, LEFT), FadeIn(eq2), run_time=0.5)
        self.play(Create(guide), run_time=0.4)
        did = cambia_didascalia(self, did, "Due letture, un solo numero R", colore=C_ACCENTO)
        self.wait(1.0)

        # ---- passaggio alla vista dall'alto ----
        via = [m for m in self.mobjects if m not in (tit, d, base, did)]
        self.move_camera(phi=0, theta=-90 * DEGREES, run_time=1.0,
                         added_anims=[FadeOut(m) for m in via] + [FadeOut(did)])
        self.remove(*via, did)
        self.base = base
        return tit, None, d

    # ------------------------------------- 2-3: Lagrange e continuita' -------------------------
    def parte_lagrange(self, tit, did, d):
        L = 3.3
        YC = 0.05
        CL, CR = np.array([-3.35, YC, 0]), np.array([3.35, YC, 0])

        def Q(C, a, b):
            return C + np.array([(a - 0.5) * L, (b - 0.5) * L, 0])

        h_ini = mappa(fxy, 0, 1, 0, 1)
        h_l, h_r = immagine_mappa(h_ini, L, CL), immagine_mappa(h_ini, L, CR)
        bordo_l, bordo_r = Square(L, color=WHITE, stroke_width=2).move_to(CL), Square(L, color=WHITE, stroke_width=2).move_to(CR)

        def etichette_q(C):
            return VGroup(MathTex("O", font_size=26).next_to(Q(C, 0, 0), DL, buff=0.08),
                          MathTex(r"\delta", font_size=26).next_to(Q(C, 1, 0), DOWN, buff=0.1),
                          MathTex(r"\delta", font_size=26).next_to(Q(C, 0, 1), LEFT, buff=0.1))

        et_l, et_r = etichette_q(CL), etichette_q(CR)
        hd_l = MathTex(r"\text{prima }y,\text{ poi }x:\ \partial_x\partial_y f", font_size=28, color=C_Y).move_to(CL + UP * (L / 2 + 0.33))
        hd_r = MathTex(r"\text{prima }x,\text{ poi }y:\ \partial_y\partial_x f", font_size=28, color=C_X).move_to(CR + UP * (L / 2 + 0.33))

        # ---- barra dei colori al centro ----
        V0, V1 = 0.0, 1.6
        HB = 2.9
        CB = np.array([-0.5, YC, 0])
        bar = barra_colori(V0, V1, HB, CB)
        Yb = lambda v: CB[1] + (v - 0.5 * (V0 + V1)) / (V1 - V0) * HB
        tacche = VGroup()
        for v, s in ((0.0, "0"), (0.5, "0{,}5"), (1.5, "1{,}5")):
            tacche.add(Line([CB[0] - 0.22, Yb(v), 0], [CB[0] - 0.15, Yb(v), 0], color=WHITE, stroke_width=2))
            tacche.add(MathTex(s, font_size=22).next_to([CB[0] - 0.22, Yb(v), 0], LEFT, buff=0.05))
        nb = Text("colore = mista", font_size=20, color=GREY_B).move_to([0, YC + L / 2 + 0.33, 0])

        self.play(FadeOut(self.base), FadeIn(bordo_l), FadeIn(h_l), FadeIn(et_l), FadeIn(hd_l),
                  FadeIn(h_r), FadeIn(bordo_r), FadeIn(et_r), FadeIn(hd_r),
                  FadeIn(bar), FadeIn(tacche), FadeIn(nb), run_time=0.7)

        R0 = valore_R(1.0)
        A, E, A2, E2 = punti(1.0)

        def marcatore(R, testo):
            y = Yb(R)
            tr = Triangle(color=WHITE, fill_opacity=1, stroke_width=0).scale(0.09).rotate(PI / 2).move_to([CB[0] + 0.26, y, 0])
            return VGroup(tr, testo.next_to(tr, RIGHT, buff=0.08))

        mk = marcatore(R0, Text("R = " + virgola(R0), font_size=22))
        self.play(FadeIn(mk), run_time=0.3)

        def segni(C):
            g = VGroup()
            for a, b, s, c in ((0, 0, "+", C_PIU), (1, 1, "+", C_PIU), (1, 0, "−", C_MENO), (0, 1, "−", C_MENO)):
                dentro = np.array([(0.5 - a), (0.5 - b), 0]) * 0.48
                g.add(Circle(0.17, color=c, stroke_width=2, fill_color=BLACK, fill_opacity=0.82).move_to(Q(C, a, b) + dentro))
                g.add(Text(s, font_size=26, color=c, weight=BOLD).move_to(Q(C, a, b) + dentro))
            return g

        s_l, s_r = segni(CL), segni(CR)

        def colpo(a, b):
            return Line(a, b, color=WHITE, stroke_width=7)

        def punto_finale(C, a, b):
            return Dot(Q(C, a, b), radius=0.1, color=WHITE, stroke_color=BLACK, stroke_width=2)

        def guide_tick(C, a, b, ta, tb):
            g = VGroup(DashedLine(Q(C, a, 0), Q(C, a, b), color=WHITE, stroke_width=1.6, dash_length=0.08),
                       DashedLine(Q(C, 0, b), Q(C, a, b), color=WHITE, stroke_width=1.6, dash_length=0.08))
            lab = VGroup(MathTex(ta, font_size=28).next_to(Q(C, a, 0), DOWN, buff=0.1),
                         MathTex(tb, font_size=28).next_to(Q(C, 0, b), LEFT, buff=0.1))
            return g, lab

        # ---- sinistra: righe -> segmento orizzontale -> punto ----
        top, bot = colpo(Q(CL, 0, 1), Q(CL, 1, 1)), colpo(Q(CL, 0, 0), Q(CL, 1, 0))
        did = cambia_didascalia(self, did, "Lagrange in y: due lati diventano uno")
        self.play(FadeIn(s_l), Create(top), Create(bot), run_time=0.5)
        self.wait(0.35)
        self.play(FadeOut(s_l), top.animate.put_start_and_end_on(Q(CL, 0, E), Q(CL, 1, E)),
                  bot.animate.put_start_and_end_on(Q(CL, 0, E), Q(CL, 1, E)), run_time=0.9)
        self.remove(bot)
        l1 = MathTex(r"\partial_y f", font_size=30).next_to(Q(CL, 0.5, E), UP, buff=0.1)
        l1.add_background_rectangle(opacity=0.7, buff=0.04)
        g1, t1 = guide_tick(CL, 0.0, E, "", r"\eta")
        self.play(FadeIn(l1), FadeIn(t1[1]), run_time=0.3)
        self.wait(0.3)
        did = cambia_didascalia(self, did, "Lagrange in x: il segmento diventa un punto")
        p1 = punto_finale(CL, A, E)
        g1, t1b = guide_tick(CL, A, E, r"\xi", r"\eta")
        self.play(FadeOut(l1), ReplacementTransform(top, p1), run_time=0.9)
        eq_l = MathTex(r"R=\partial_x\partial_y f(\xi,\eta)", font_size=32).move_to(CL + DOWN * (L / 2 + 0.8))
        self.play(FadeIn(g1), FadeIn(t1b[0]), FadeIn(eq_l), run_time=0.4)
        self.remove(t1[1]); self.add(t1b[1])
        self.wait(0.3)

        # ---- destra: colonne -> segmento verticale -> punto ----
        sin, des = colpo(Q(CR, 0, 0), Q(CR, 0, 1)), colpo(Q(CR, 1, 0), Q(CR, 1, 1))
        did = cambia_didascalia(self, did, "L'altro ordine: i lati verticali, poi un punto")
        self.play(FadeIn(s_r), Create(sin), Create(des), run_time=0.45)
        self.wait(0.25)
        self.play(FadeOut(s_r), sin.animate.put_start_and_end_on(Q(CR, A2, 0), Q(CR, A2, 1)),
                  des.animate.put_start_and_end_on(Q(CR, A2, 0), Q(CR, A2, 1)), run_time=0.85)
        self.remove(des)
        p2 = punto_finale(CR, A2, E2)
        g2, t2 = guide_tick(CR, A2, E2, r"\xi'", r"\eta'")
        self.play(FadeIn(t2[0]), run_time=0.2)
        self.wait(0.35)
        self.play(ReplacementTransform(sin, p2), run_time=0.85)
        eq_r = MathTex(r"R=\partial_y\partial_x f(\xi',\eta')", font_size=32).move_to(CR + DOWN * (L / 2 + 0.8))
        self.play(FadeIn(g2), FadeIn(t2[1]), FadeIn(eq_r), run_time=0.4)

        # ---- curva di livello: i due punti hanno lo stesso colore ----
        gx = np.linspace(0, 1, 300)
        XX, YY = np.meshgrid(gx, gx)
        linee = contour_generator(x=gx, y=gx, z=fxy(XX, YY)).lines(R0)

        def livello(C):
            g = VGroup()
            for ln in linee:
                pts = np.array([Q(C, a, b) for a, b in ln])
                m = curva(pts[::4], WHITE, 2.4)
                g.add(DashedVMobject(m, num_dashes=max(10, len(pts) // 14)))
            return g

        lv_l, lv_r = livello(CL), livello(CR)
        did = cambia_didascalia(self, did, "Due punti diversi, stesso colore: è R")
        self.play(Create(lv_l), Create(lv_r), run_time=0.8)
        self.bring_to_front(p1, p2)
        self.wait(0.9)

        # ---- zoom: delta -> 0 ----
        self.play(*[FadeOut(m) for m in (lv_l, lv_r, g1, g2, t1b, t2)], run_time=0.3)
        self.remove(t1b[1], t1[1])
        T = ValueTracker(0.0)
        dd = lambda: float(np.exp(T.get_value()))

        def agg_mappa(m, _=0):
            D = dd()
            m.pixel_array = mappa(fxy, 0, D, 0, D)

        h_l.add_updater(agg_mappa)
        h_r.add_updater(agg_mappa)

        p1.add_updater(lambda m: m.move_to(Q(CL, *punti(dd())[:2])))
        p2.add_updater(lambda m: m.move_to(Q(CR, *punti(dd())[2:])))
        self.remove(mk)
        mk2 = always_redraw(lambda: marcatore(valore_R(dd()), Text("R = " + virgola(valore_R(dd())), font_size=22)))
        ld = always_redraw(lambda: Text("δ = " + virgola(dd()), font_size=25).move_to([0, YC - L / 2 - 0.8, 0]))
        self.add(mk2, ld)

        eq_l2 = MathTex(r"R\to\partial_x\partial_y f(O)", font_size=32).move_to(eq_l)
        eq_r2 = MathTex(r"R\to\partial_y\partial_x f(O)", font_size=32).move_to(eq_r)
        did = cambia_didascalia(self, did, "δ → 0: il colore si uniforma")
        self.play(FadeOut(eq_l), FadeOut(eq_r), FadeIn(eq_l2), FadeIn(eq_r2), run_time=0.3)
        self.play(T.animate.set_value(np.log(0.02)), run_time=3.2, rate_func=smooth)
        did = cambia_didascalia(self, did, "Un solo R, un solo limite: le miste coincidono", colore=C_ACCENTO)
        self.wait(1.0)

        for m in self.mobjects:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tit], run_time=0.45)
        self.remove(*[m for m in self.mobjects if m is not tit])
        return None, None

    # ------------------------------------- 4: controesempio ------------------------------------
    def parte_controesempio(self, tit, did, d):
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)
        LQ = 4.8
        C = np.array([-3.05, -0.02, 0])
        d = dati(self, r"f=\frac{xy(x^2-y^2)}{x^2+y^2},\quad f(O)=0", font_size=32)

        def S(a, b):
            return C + np.array([a * LQ / 2, b * LQ / 2, 0])

        h = immagine_mappa(mappa(g_mista, -1, 1, -1, 1), LQ, C)
        bordo = Square(LQ, color=WHITE, stroke_width=2).move_to(C)
        VB, HB, CB = np.sqrt(2.0), 3.2, np.array([6.05, 0.0, 0])      # la mista arriva a +-sqrt(2) a 22,5 gradi dagli assi
        bar = barra_colori(-VB, VB, HB, CB)
        tac = VGroup()
        for v, t in ((1, "+1"), (0, "0"), (-1, "-1")):
            y = CB[1] + v / (2 * VB) * HB
            tac.add(Line([CB[0] - 0.22, y, 0], [CB[0] - 0.15, y, 0], color=WHITE, stroke_width=2))
            tac.add(MathTex(t, font_size=22).next_to([CB[0] - 0.22, y, 0], LEFT, buff=0.05))
        nb = Text("colore =\nmista", font_size=18, color=GREY_B, line_spacing=0.8).next_to(bar, UP, buff=0.12)

        self.play(FadeIn(h), FadeIn(bordo), FadeIn(bar), FadeIn(tac), FadeIn(nb), run_time=0.6)
        did = cambia_didascalia(self, None, "Mista discontinua in O: dipende solo dalla direzione")
        self.wait(0.9)

        L = ValueTracker(0.0)
        zoom = lambda: float(np.exp(L.get_value()))

        def agg(m, _=0):
            z = zoom()
            m.pixel_array = mappa(g_mista, -1 / z, 1 / z, -1 / z, 1 / z)

        h.add_updater(agg)
        XP = 0.15
        lz = always_redraw(lambda: Text("zoom ×" + f"{zoom():.0f}", font_size=28).move_to([XP, 1.75, 0], aligned_edge=LEFT))
        self.add(lz)
        did = cambia_didascalia(self, did, "Zoom: la figura non cambia mai")
        self.play(L.animate.set_value(np.log(1000.0)), run_time=2.4, rate_func=smooth)
        h.clear_updaters()
        lz.clear_updaters()
        self.wait(0.3)

        COL_P, COL_M = C_MAPPA_PIU, C_MAPPA_MENO

        def asse(a, b, colore):
            return VGroup(Line(a, b, color=BLACK, stroke_width=10), Line(a, b, color=colore, stroke_width=5))

        ax_x, ax_y = asse(S(-1, 0), S(1, 0), COL_P), asse(S(0, -1), S(0, 1), COL_M)
        q1 = MathTex(r"\partial_x\partial_y f(O)=+1", font_size=34, color=COL_P).move_to([XP, 0.85, 0], aligned_edge=LEFT)
        q1b = Text("si legge sull'asse x", font_size=22, color=COL_P).next_to(q1, DOWN, buff=0.1, aligned_edge=LEFT)
        q2 = MathTex(r"\partial_y\partial_x f(O)=-1", font_size=34, color=COL_M).move_to([XP, -0.4, 0], aligned_edge=LEFT)
        q2b = Text("si legge sull'asse y", font_size=22, color=COL_M).next_to(q2, DOWN, buff=0.1, aligned_edge=LEFT)
        o = Dot(S(0, 0), radius=0.09, color=WHITE, stroke_color=BLACK, stroke_width=2)
        l_o = MathTex("O", font_size=26).next_to(o, DL, buff=0.05)
        l_o.add_background_rectangle(opacity=0.55, buff=0.02)
        did = cambia_didascalia(self, did, "Cambiare ordine vuol dire cambiare asse")
        self.play(Create(ax_x), FadeIn(q1), FadeIn(q1b), run_time=0.6)
        self.play(Create(ax_y), FadeIn(o), FadeIn(l_o), FadeIn(q2), FadeIn(q2b), run_time=0.6)
        self.wait(0.9)

        q = Square(0.62 * LQ / 2, color=WHITE, stroke_width=3).move_to(S(0.31, 0.31))
        P_D = 0.48586827 * 0.62
        pt = Dot(S(P_D, P_D), radius=0.09, color=WHITE, stroke_color=BLACK, stroke_width=2)
        diag = DashedLine(S(0, 0), S(0.62, 0.62), color=WHITE, stroke_width=1.8, dash_length=0.08)
        q3 = MathTex(r"R=0", font_size=34).move_to([XP, -1.65, 0], aligned_edge=LEFT)
        q3b = Text("nel quadratino, per ogni δ", font_size=22).next_to(q3, DOWN, buff=0.1, aligned_edge=LEFT)
        did = cambia_didascalia(self, did, "R = 0: lontano da +1 e da −1")
        self.play(Create(q), Create(diag), FadeIn(pt), FadeIn(q3), FadeIn(q3b), run_time=0.7)
        self.wait(0.9)
        risultato_angolo(self, r"\partial_x\partial_y f,\ \partial_y\partial_x f\ \text{continue}\ \Rightarrow\ "
                               r"\partial_x\partial_y f=\partial_y\partial_x f",
                         vecchia_didascalia=did, attesa=1.7)
