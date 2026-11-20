"""C1 => differenziabile, ma differenziabile non implica C1 (Analisi II).

Idea unica: lo ZOOM isometrico attorno al punto.
- differenziabile  = zoomando, le ALTEZZE si schiacciano sul piano tangente;
- C1               = zoomando, anche le PENDENZE vicine tendono a quelle in P.
Parte A: percorso a L + Lagrange: le pendenze controllano le altezze.
Parte B: f = rho^2 sin(1/rho): le altezze si schiacciano, le pendenze restano +-1.
"""
from manim import *
from doll_kit import *
from scipy.optimize import brentq

# ---------------------------- PARTE A: funzione liscia, P nell'origine ---------------------------
def f(x, y): return 0.9 * np.sin(0.8 * x + 0.9) * np.cos(0.7 * y - 0.8)
def fx(x, y): return 0.72 * np.cos(0.8 * x + 0.9) * np.cos(0.7 * y - 0.8)
def fy(x, y): return -0.63 * np.sin(0.8 * x + 0.9) * np.sin(0.7 * y - 0.8)

F0, FX0, FY0 = f(0, 0), fx(0, 0), fy(0, 0)
U, V = 1.6, 1.6               # Q in coordinate di zoom: sullo schermo resta fermo
LATO = 2.4
LUNGA = 0.62                 # semi-lunghezza dei segmenti tangenti

C_X, C_Y, C_ERR, C_PIANO = BLUE_B, GREEN_C, RED_C, YELLOW


def g(u, v, lam):
    """Zoom isometrico di fattore lam attorno a P (che resta nell'origine)."""
    return lam * (f(u / lam, v / lam) - F0)


def piano_z(u, v):
    return FX0 * u + FY0 * v


def stato(lam):
    """Punti di Lagrange sui due tratti del percorso a L e grandezze lette nel pannello."""
    h, k = U / lam, V / lam
    d1 = f(h, 0) - F0
    d2 = f(h, k) - f(h, 0)
    def rad(fun):
        try:
            return brentq(fun, 0.0, 1.0)
        except ValueError:
            return 0.5
    th1 = rad(lambda t: fx(t * h, 0) * h - d1)
    th2 = rad(lambda t: fy(h, t * k) * k - d2)
    err = f(h, k) - F0 - FX0 * h - FY0 * k
    return dict(th1=th1, th2=th2, p1=fx(th1 * h, 0), p2=fy(h, th2 * k), err_rho=abs(err) / np.hypot(h, k))


def virgola(x, cifre=3):
    return f"{x:.{cifre}f}".replace(".", ",").replace("-", "−")


# ---------------------------- PARTE B: controesempio ---------------------------------------------
def rho2sin(r):
    return r * r * np.sin(1 / r)


def z_zoom(u, lam):
    return u * u / lam * np.sin(lam / np.abs(u))


def fx_zoom(u, lam):
    x = u / lam
    return 2 * x * np.sin(1 / np.abs(x)) - np.sign(x) * np.cos(1 / np.abs(x))


UMAX = 0.6
K = 4.6                       # unita' per unita' (sinistra: scala uguale su x e z, le pendenze sono vere)
KY = 1.25                     # scala verticale del grafico di f_x
O_L = np.array([-3.35, 0.0, 0])
O_R = np.array([3.5, 0.0, 0])


def SL(u, z): return O_L + np.array([u * K, z * K, 0])
def SR(u, y): return O_R + np.array([u * K, y * KY, 0])


def griglia(lam, n=2400):
    """Punti uniformi nella fase lam/u (6 per radiante) da UMAX fino a uc; piu' dentro e' sotto il pixel."""
    f0 = lam / UMAX
    fasi = np.linspace(f0, f0 + n / 6.0, n)
    return lam / fasi


def curva(punti, colore, spessore=3.0):
    m = VMobject(stroke_color=colore, stroke_width=spessore)
    m.set_points_as_corners(punti)
    return m


def grafico_z(lam):
    u = griglia(lam)
    pts = [SL(a, z_zoom(a, lam)) for a in u] + [SL(0, 0)]
    return VGroup(curva(np.array(pts), BLUE_B),
                  curva(np.array([p * [1, 1, 1] + [2 * (O_L[0] - p[0]), 0, 0] for p in pts]), BLUE_B))


def inviluppi(lam):
    u = np.linspace(-UMAX, UMAX, 81)
    su = DashedVMobject(curva(np.array([SL(a, a * a / lam) for a in u]), GREY_B, 2), num_dashes=46)
    giu = DashedVMobject(curva(np.array([SL(a, -a * a / lam) for a in u]), GREY_B, 2), num_dashes=46)
    return VGroup(su, giu)


def grafico_fx(lam):
    u = griglia(lam)
    pts = np.array([SR(a, fx_zoom(a, lam)) for a in u])
    neg = np.array([SR(-a, fx_zoom(-a, lam)) for a in u])
    uc = u[-1]
    banda = Polygon(SR(-uc, -1.0), SR(uc, -1.0), SR(uc, 1.0), SR(-uc, 1.0),
                    stroke_width=0, fill_color=ORANGE, fill_opacity=1)
    return VGroup(curva(pts, ORANGE, 2.2), curva(neg, ORANGE, 2.2), banda)


def tangente(u, lam):
    """Segmento tangente al grafico schiacciato: la scala e' uguale su x e z, quindi la pendenza e' vera."""
    p = fx_zoom(u, lam)
    d = np.array([1, p, 0]) / np.hypot(1, p) * 0.95
    c = SL(u, z_zoom(u, lam))
    return Line(c - d, c + d, color=YELLOW, stroke_width=5)


class Esercizio(ThreeDScene):
    def construct(self):
        tit = self.parte_a()
        self.parte_b(tit)

    # ---------------------------------------- A ----------------------------------------
    def parte_a(self):
        theta = -90 * DEGREES      # x orizzontale sullo schermo, y in profondita': il percorso e' una L
        destra = np.array([-np.sin(theta), np.cos(theta), 0])
        OFF = -1.95 * destra       # frame_center sposta anche il testo fisso: si sposta il mondo
        self.set_camera_orientation(phi=52 * DEGREES, theta=theta)

        def W(a, b, c):
            return np.array([a, b, c]) + OFF

        tit = titolo(self, "C¹ e differenziabilità")
        d = dati(self, r"f_x,\ f_y\ \text{continue}\ \Rightarrow\ f\ \text{differenziabile}", font_size=32)

        def superficie(lam):
            return Surface(lambda a, b: W(a, b, g(a, b, lam)),
                           u_range=[-LATO, LATO], v_range=[-LATO, LATO], resolution=(18, 18),
                           fill_opacity=0.72, checkerboard_colors=[BLUE_D, BLUE_E],
                           stroke_color=BLUE_A, stroke_width=0.35)

        piano = Surface(lambda a, b: W(a, b, piano_z(a, b)),
                        u_range=[-LATO, LATO], v_range=[-LATO, LATO], resolution=(10, 10),
                        fill_opacity=0.26, checkerboard_colors=[C_PIANO, C_PIANO],
                        stroke_color=C_PIANO, stroke_width=0.3)

        def curva_sup(fun, n=40, colore=WHITE, sp=5):
            t = np.linspace(0, 1, n)
            return curva(np.array([fun(a) for a in t]), colore, sp)

        def tratto1(lam): return curva_sup(lambda t: W(t * U, 0, g(t * U, 0, lam)), colore=C_X)
        def tratto2(lam): return curva_sup(lambda t: W(U, t * V, g(U, t * V, lam)), colore=C_Y)

        def tang1(lam):
            s = stato(lam)
            a = s["th1"] * U
            c = W(a, 0, g(a, 0, lam))
            w = np.array([1, 0, s["p1"]]); w = w / np.linalg.norm(w) * LUNGA
            return Line(c - w, c + w, color=WHITE, stroke_width=6)

        def tang2(lam):
            s = stato(lam)
            b = s["th2"] * V
            c = W(U, b, g(U, b, lam))
            w = np.array([0, 1, s["p2"]]); w = w / np.linalg.norm(w) * LUNGA
            return Line(c - w, c + w, color=WHITE, stroke_width=6)

        def rif1(lam):
            """Stessa posizione di tang1, ma con la pendenza in P."""
            s = stato(lam)
            a = s["th1"] * U
            c = W(a, 0, g(a, 0, lam))
            w = np.array([1, 0, FX0]); w = w / np.linalg.norm(w) * LUNGA
            return Line(c - w, c + w, color=C_PIANO, stroke_width=3)

        def rif2(lam):
            s = stato(lam)
            b = s["th2"] * V
            c = W(U, b, g(U, b, lam))
            w = np.array([0, 1, FY0]); w = w / np.linalg.norm(w) * LUNGA
            return Line(c - w, c + w, color=C_PIANO, stroke_width=3)

        def gap(lam):
            return Line(W(U, V, piano_z(U, V)), W(U, V, g(U, V, lam)),
                        color=C_ERR, stroke_width=8)

        def punto(colore, r=0.075):
            m = Dot(radius=r, color=colore)
            self.renderer.camera.add_fixed_orientation_mobjects(m)
            return m

        def etichetta(tex, colore=WHITE, size=32):
            m = MathTex(tex, font_size=size, color=colore)
            self.renderer.camera.add_fixed_orientation_mobjects(m)
            return m

        surf = superficie(1.0)
        P = punto(YELLOW).move_to(W(0, 0, 0))
        Q = punto(WHITE).move_to(W(U, V, g(U, V, 1.0)))
        lP = etichetta("P").move_to(W(-0.28, -0.05, 0.42))
        lQ = etichetta("Q").move_to(Q.get_center() + OUT * 0.30 + destra * 0.34)
        diag = curva_sup(lambda t: W(t * U, t * V, g(t * U, t * V, 1.0)), colore=GREY_A, sp=3.5)

        self.play(FadeIn(surf), run_time=0.8)
        self.play(FadeIn(P), FadeIn(lP), FadeIn(Q), FadeIn(lQ), Create(diag), run_time=0.8)
        did = cambia_didascalia(self, None, "Da P a Q: quanto si sale?")
        self.wait(1.0)

        t1, t2 = tratto1(1.0), tratto2(1.0)
        o_ax = W(-3.0, -2.45, -0.9)
        ax_x = Arrow(o_ax, o_ax + RIGHT * 1.0, buff=0, color=C_X, stroke_width=4, tip_length=0.2)
        ax_y = Arrow(o_ax, o_ax + UP * 1.0, buff=0, color=C_Y, stroke_width=4, tip_length=0.2)
        l_ax_x = etichetta("x", C_X, 34).move_to(o_ax + RIGHT * 1.28)
        l_ax_y = etichetta("y", C_Y, 34).move_to(o_ax + UP * 1.28)
        A = punto(WHITE).move_to(W(U, 0, g(U, 0, 1.0)))
        lA = etichetta("A").move_to(A.get_center() + OUT * 0.30 + destra * 0.34)

        def scritta(testo, colore):
            m = Text(testo, font_size=24, color=colore)
            m.add_background_rectangle(opacity=0.8, buff=0.07)
            self.renderer.camera.add_fixed_orientation_mobjects(m)
            return m

        s_x = scritta("cambia solo x", C_X).move_to(W(U / 2, -0.72, g(U / 2, 0, 1.0)))
        s_y = scritta("cambia solo y", C_Y).move_to(W(U + 1.5, V / 2, g(U, V / 2, 1.0)))
        did = cambia_didascalia(self, did, "Asse per asse: prima cambia solo x, poi solo y")
        self.play(FadeIn(ax_x), FadeIn(ax_y), FadeIn(l_ax_x), FadeIn(l_ax_y), FadeOut(diag), run_time=0.5)
        self.play(Create(t1), FadeIn(s_x), run_time=0.8)
        self.play(FadeIn(A), FadeIn(lA), run_time=0.25)
        self.play(Create(t2), FadeIn(s_y), run_time=0.8)
        self.wait(1.1)
        self.play(FadeOut(s_x), FadeOut(s_y), run_time=0.3)

        ta, tb, ra, rb = tang1(1.0), tang2(1.0), rif1(1.0), rif2(1.0)
        s0 = stato(1.0)
        l1 = etichetta(r"\xi_1", WHITE, 36).move_to(ta.get_center() + OUT * 0.5)
        l2 = etichetta(r"\xi_2", WHITE, 36).move_to(tb.get_center() + OUT * 0.28 + destra * 0.5)
        did = cambia_didascalia(self, did, "Lagrange: in ξ la tangente ha la pendenza media")
        self.play(Create(ta), Create(tb), FadeIn(l1), FadeIn(l2), run_time=0.8)
        self.wait(1.0)

        er = gap(1.0)
        did = cambia_didascalia(self, did, "Piano tangente in P: il tratto rosso è l'errore")
        self.play(FadeIn(piano), Create(er), Create(ra), Create(rb), run_time=0.9)

        # ---- pannello ----
        X0, X1, X2 = 2.05, 3.75, 4.95
        righe = [1.15, 0.3, -0.55]
        lab = VGroup(
            MathTex(r"f_x(\xi_1)", font_size=32, color=C_X).move_to([X0, righe[0], 0], aligned_edge=LEFT),
            MathTex(r"f_y(\xi_2)", font_size=32, color=C_Y).move_to([X0, righe[1], 0], aligned_edge=LEFT),
            MathTex(r"\mathrm{errore}/\rho", font_size=32, color=C_ERR).move_to([X0, righe[2], 0], aligned_edge=LEFT),
            MathTex(r"\to\ f_x(P)=" + virgola(FX0).replace(",", "{,}"), font_size=28, color=C_PIANO)
            .move_to([X2, righe[0], 0], aligned_edge=LEFT),
            MathTex(r"\to\ f_y(P)=" + virgola(FY0).replace(",", "{,}").replace("−", "-"), font_size=28, color=C_PIANO)
            .move_to([X2, righe[1], 0], aligned_edge=LEFT),
            MathTex(r"\to\ 0", font_size=28, color=C_PIANO).move_to([X2, righe[2], 0], aligned_edge=LEFT),
        )
        fit(lab, max_w=4.75)
        lab.move_to([4.35, 0.3, 0])
        X1 = lab[3].get_left()[0] - 1.0

        T = ValueTracker(0.0)
        lam = lambda: float(np.exp(T.get_value()))

        def vivo(fun, y, colore):
            g_ = VGroup()
            def upd(m, dt):
                # dt == 0 e' la chiamata prima dell'animazione: Manim congela li' la lista degli oggetti,
                # e un figlio creato ora resterebbe disegnato per tutta l'animazione (immagine fantasma)
                if dt == 0:
                    return
                t = Text(fun(), font_size=25, color=colore).move_to([X1, y, 0], aligned_edge=LEFT)
                m.submobjects = [t]
                self.renderer.camera.add_fixed_in_frame_mobjects(t)
            g_.add_updater(upd, call_updater=False)
            upd(g_, 1.0)
            return g_

        n1 = vivo(lambda: virgola(stato(lam())["p1"]), lab[0].get_center()[1], C_X)
        n2 = vivo(lambda: virgola(stato(lam())["p2"]), lab[1].get_center()[1], C_Y)
        n3 = vivo(lambda: virgola(stato(lam())["err_rho"]), lab[2].get_center()[1], C_ERR)
        nz = vivo(lambda: "zoom ×" + virgola(lam(), 1), lab[0].get_center()[1] + 0.85, WHITE)
        self.add_fixed_in_frame_mobjects(lab)
        self.remove(lab)
        self.play(FadeIn(lab), run_time=0.4)
        self.add(n1, n2, n3, nz)
        self.wait(0.5)

        # ---- zoom ----
        did = cambia_didascalia(self, did, "Zoom su P: pendenze in ξ → pendenze in P")
        surf.add_updater(lambda m: m.become(superficie(lam())))
        t1.add_updater(lambda m: m.become(tratto1(lam())))
        t2.add_updater(lambda m: m.become(tratto2(lam())))
        ta.add_updater(lambda m: m.become(tang1(lam())))
        tb.add_updater(lambda m: m.become(tang2(lam())))
        ra.add_updater(lambda m: m.become(rif1(lam())))
        rb.add_updater(lambda m: m.become(rif2(lam())))
        er.add_updater(lambda m: m.become(gap(lam())))
        Q.add_updater(lambda m: m.move_to(W(U, V, g(U, V, lam()))))
        A.add_updater(lambda m: m.move_to(W(U, 0, g(U, 0, lam()))))
        lA.add_updater(lambda m: m.move_to(A.get_center() + OUT * 0.30 + destra * 0.34))
        lQ.add_updater(lambda m: m.move_to(Q.get_center() + OUT * 0.30 + destra * 0.34))
        l1.add_updater(lambda m: m.move_to(ta.get_center() + OUT * 0.5))
        l2.add_updater(lambda m: m.move_to(tb.get_center() + OUT * 0.28 + destra * 0.5))
        for n in (n1, n2, n3, nz):
            n.submobjects = []
        self.play(T.animate.set_value(np.log(60.0)), run_time=3.9, rate_func=smooth)
        did = cambia_didascalia(self, did, "Derivate continue: l'errore sparisce più in fretta di ρ")
        self.wait(1.4)

        for m in self.mobjects:
            m.clear_updaters()
        pulisci(self, tit)
        return tit

    # ---------------------------------------- B ----------------------------------------
    def parte_b(self, tit):
        WXY, WZ = 10.0, 26.0     # z ingrandita: gli anelli sono alti rho^2
        self.set_camera_orientation(phi=60 * DEGREES, theta=-72 * DEGREES)

        def pt(s, a):
            r = 1 / s
            return np.array([WXY * r * np.cos(a), WXY * r * np.sin(a), WZ * rho2sin(r)])

        surf = Surface(pt, u_range=[1 / 0.31, 1 / 0.02], v_range=[0, TAU], resolution=(84, 36),
                       fill_opacity=0.95, checkerboard_colors=[BLUE_D, BLUE_E],
                       stroke_color=BLUE_E, stroke_width=0.25)
        def centro(t, a):
            return np.array([WXY * t * np.cos(a), WXY * t * np.sin(a), WZ * rho2sin(t)])

        tappo = Surface(centro, u_range=[1e-4, 0.02], v_range=[0, TAU], resolution=(2, 36),
                        fill_opacity=0.95, checkerboard_colors=[BLUE_D, BLUE_E],
                        stroke_color=BLUE_E, stroke_width=0.25)
        surf = VGroup(surf, tappo)
        r = np.append(np.linspace(0.31, 0.02, 900), 1e-5)
        fetta = VGroup(
            curva(np.array([[WXY * a, 0, WZ * rho2sin(a)] for a in r]), YELLOW, 4),
            curva(np.array([[-WXY * a, 0, WZ * rho2sin(a)] for a in r]), YELLOW, 4),
        )
        nota = Text("scala z ingrandita", font_size=21, color=GREY_B).to_corner(DR, buff=0.4).shift(UP * 0.55)
        self.add_fixed_in_frame_mobjects(nota)
        self.remove(nota)
        self.play(FadeIn(surf), FadeIn(nota), run_time=0.6)
        d = dati(self, r"f=\rho^2\sin\frac{1}{\rho},\quad f(O)=0,\quad \rho=\sqrt{x^2+y^2}", font_size=32, max_w=6.4)
        did = cambia_didascalia(self, None, "Onde sempre più fitte, schiacciate verso O")
        self.wait(0.9)
        did = cambia_didascalia(self, did, "Dipende solo da ρ: tutti i tagli sono uguali")
        self.play(Create(fetta), run_time=1.0)
        self.wait(0.4)
        self.move_camera(phi=88 * DEGREES, theta=-90 * DEGREES, run_time=1.0)
        self.play(FadeOut(surf), FadeOut(fetta), FadeOut(did), FadeOut(nota), run_time=0.4)
        self.remove(surf, fetta, did, nota)
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)

        # ---- due grafici affiancati ----
        def assi(O, kx, ky_max, etich):
            ax = VGroup(
                Line(O + LEFT * (UMAX * K + 0.15), O + RIGHT * (UMAX * K + 0.2), color=GREY_B, stroke_width=2),
                Line(O + DOWN * ky_max, O + UP * ky_max, color=GREY_B, stroke_width=2),
            )
            xl = MathTex("x", font_size=26, color=GREY_B).next_to(ax[0], RIGHT, buff=0.06)
            return VGroup(ax, xl)

        ax_L = assi(O_L, K, 1.95, "z")
        ax_R = assi(O_R, K, 1.75, "f_x")
        tl = MathTex(r"z=f(x,0)", r"\quad |f|\le\rho^2", font_size=30)
        tl[0].set_color(BLUE_B); tl[1].set_color(GREY_B)
        tl.move_to(O_L + UP * 2.32)
        tr = MathTex(r"f_x(x,0)", font_size=30, color=ORANGE).move_to(O_R + UP * 2.32)
        uno = VGroup(*[DashedLine(SR(-UMAX, s), SR(UMAX, s), color=GREY_C, stroke_width=1.5, dash_length=0.1) for s in (1, -1)])
        lu = VGroup(MathTex("+1", font_size=24, color=GREY_B).next_to(uno[0], RIGHT, buff=0.04),
                    MathTex("-1", font_size=24, color=GREY_B).next_to(uno[1], RIGHT, buff=0.04))
        lu.shift(LEFT * 0.0)

        L = ValueTracker(1.0)
        S = ValueTracker(1 / 0.55)      # x = 1/s: la fase avanza a velocita' costante
        xr = lambda: 1 / S.get_value()

        g_z = always_redraw(lambda: grafico_z(L.get_value()))
        g_e = always_redraw(lambda: inviluppi(L.get_value()))
        g_f = always_redraw(lambda: grafico_fx(L.get_value()))
        tang = always_redraw(lambda: tangente(xr() * L.get_value(), L.get_value()))
        dl = always_redraw(lambda: Dot(SL(xr() * L.get_value(), z_zoom(xr() * L.get_value(), L.get_value())),
                                       radius=0.07, color=YELLOW))
        dr = always_redraw(lambda: Dot(SR(xr() * L.get_value(), fx_zoom(xr() * L.get_value(), L.get_value())),
                                       radius=0.075, color=YELLOW))
        lett = always_redraw(lambda: Text("pendenza = " + virgola(fx_zoom(xr() * L.get_value(), L.get_value()), 2),
                                          font_size=25, color=YELLOW).move_to(O_L + DOWN * 2.28))
        lzoom = always_redraw(lambda: Text("zoom ×" + virgola(L.get_value(), 1), font_size=23, color=WHITE)
                              .move_to(O_R + DOWN * 2.28))

        self.play(FadeIn(ax_L), FadeIn(ax_R), FadeIn(tl), FadeIn(tr), FadeIn(uno), FadeIn(lu),
                  FadeIn(g_z), FadeIn(g_e), FadeIn(g_f), run_time=0.7)
        self.add(tang, dl, dr, lett, lzoom)
        did = cambia_didascalia(self, None, "Vicino a O l'altezza sparisce, la pendenza no")
        self.play(S.animate.set_value(34.0), run_time=4.0, rate_func=linear)

        # ---- zoom ----
        did = cambia_didascalia(self, did, "Zoom: ogni taglio si schiaccia, differenziabile!")
        self.play(L.animate.set_value(11.0), run_time=3.4, rate_func=smooth)
        did = cambia_didascalia(self, did, "Stessa pendenza di prima: le onde restano ripide")
        self.wait(1.1)

        # ---- O ----
        o_r = Dot(SR(0, 0), radius=0.1, color=WHITE, stroke_color=BLACK, stroke_width=2)
        l_o = MathTex(r"f_x(O)=0", font_size=28).next_to(o_r, UP, buff=0.13).shift(RIGHT * 0.75 + UP * 0.2)
        fondo = BackgroundRectangle(l_o, fill_opacity=0.85, buff=0.06)
        did = cambia_didascalia(self, did, "In O vale 0, attorno oscilla tra −1 e +1")
        self.play(FadeIn(o_r), FadeIn(fondo), FadeIn(l_o), run_time=0.5)
        self.wait(1.1)
        did = cambia_didascalia(self, did, "Le pendenze controllano le altezze, non viceversa", colore=C_ACCENTO)
        self.wait(1.5)

        risultato_angolo(self, r"C^1 \Rightarrow \text{differenziabile} \qquad \text{differenziabile} \not\Rightarrow C^1",
                         vecchia_didascalia=did, attesa=2.2)
