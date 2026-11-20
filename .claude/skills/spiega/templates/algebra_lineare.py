"""TEMPLATE ALGEBRA LINEARE: la matrice come trasformazione del piano.

Esempio: autovalori e autovettori di una matrice 2x2. Funziona per QUALSIASI
matrice 2x2 con autovalori reali: cambia solo A qui sotto.

Cosa si vede (≈30 s, niente passaggi algebrici: quelli vanno in chat):
  1. il piano con una "rosa" di vettori;
  2. A deforma il piano: quasi tutti i vettori cambiano direzione;
  3. si evidenziano le rette degli autovettori: lì i vettori restano sulla
     loro retta e vengono solo allungati di λ.

Altri esercizi di algebra lineare: tieni il meccanismo M(t) = (1-t)I + tA e
cambia cosa evidenzi (determinante = area del quadrato unitario, nucleo = retta
che collassa nell'origine, sistema = intersezione di rette, ...).

Matrici 3x3 / endomorfismi di spazi di matrici o polinomi:
  - lavora nelle COORDINATE rispetto alla base data (es. (a, b, c) per S^{2,2}) e
    dillo nella prima didascalia ("ogni matrice è un punto (a, b, c)");
  - ThreeDScene + ThreeDAxes, stesso meccanismo M(t); camera che ruota piano
    (self.begin_ambient_camera_rotation(rate=0.1));
  - autovalori/autovettori ESATTI con SymPy (sp.Matrix(A).eigenvects()), non con
    np.linalg.eig: con una matrice non diagonalizzabile numpy dà due rette quasi
    coincidenti invece di una;
  - non diagonalizzabile: mostra che per λ con molteplicità algebrica 2 c'è una sola retta.

Coniche e forme quadratiche (qui il meccanismo M(t) non serve: usa Axes):
  - curve di livello f(x,y) = k con un ValueTracker su k (ellissi che si stringono
    fino a un punto, iperboli che passano per le rette asintotiche, insieme vuoto);
  - rotazione sugli assi principali (autovettori della parte quadratica): la
    conica ruota finché il termine misto xy sparisce;
  - completamento dei quadrati: le rette dove i quadrati si annullano.
  Disegno: ax.plot_implicit_curve(lambda x, y: f(x, y) - k, color=...)
  (oppure ParametricFunction per le ellissi).
"""
from doll_kit import *  # noqa: F401  (render.sh mette kit/ nel PYTHONPATH)
import numpy as np

A = np.array([[2.0, 1.0],
              [1.0, 2.0]])
TITOLO = "Autovettori di A"


def fmt(x: float) -> str:
    return f"{x:.0f}" if abs(x - round(x)) < 1e-9 else f"{x:.2f}".replace(".", "{,}")


def fmt_vec(v: np.ndarray) -> str:
    """Autovettore 'pulito': scala in modo che la componente più piccola non nulla valga ±1."""
    nz = [abs(c) for c in v if abs(c) > 1e-9]
    w = v / min(nz)
    if w[0] < 0 or (abs(w[0]) < 1e-9 and w[1] < 0):
        w = -w
    return rf"({fmt(w[0])},\ {fmt(w[1])})"


class Esercizio(Scene):
    def construct(self):
        vals, vecs = np.linalg.eig(A)
        if np.iscomplexobj(vals) and np.any(np.abs(np.imag(vals)) > 1e-9):
            raise ValueError("Autovalori complessi: nessuna retta invariante. Mostra la rotazione/scala invece degli autovettori.")
        vals, vecs = np.real(vals), np.real(vecs)
        ordine = np.argsort(-np.abs(vals))
        vals, vecs = vals[ordine], vecs[:, ordine]

        L0 = min(1.6, 3.0 / max(1.0, np.max(np.abs(vals))))  # lunghezza iniziale delle frecce
        t = ValueTracker(0)
        def M():
            return (1 - t.get_value()) * np.eye(2) + t.get_value() * A
        def img(v):  # immagine di un vettore 2D come punto 3D di Manim
            w = M() @ v
            return np.array([w[0], w[1], 0.0])

        # ---------- titolo e dati ----------
        tit = titolo(self, TITOLO)
        mat = dati(self, rf"A = \begin{{pmatrix}} {fmt(A[0,0])} & {fmt(A[0,1])} \\ {fmt(A[1,0])} & {fmt(A[1,1])} \end{{pmatrix}}")

        # ---------- piano che si deforma ----------
        fantasma = NumberPlane(x_range=[-9, 9, 1], y_range=[-6, 6, 1],
                               background_line_style={"stroke_opacity": 0.15},
                               axis_config={"stroke_opacity": 0.25})
        base = NumberPlane(x_range=[-9, 9, 1], y_range=[-6, 6, 1],
                           background_line_style={"stroke_color": BLUE_D, "stroke_opacity": 0.6})
        piano = base.copy()
        piano.add_updater(lambda m: m.become(base.copy().apply_matrix(M())))
        self.add(fantasma)
        self.play(Create(piano), run_time=1)
        self.bring_to_front(tit, mat)

        # rosa di vettori
        N = 16
        dirs = [L0 * np.array([np.cos(a), np.sin(a)]) for a in np.linspace(0, TAU, N, endpoint=False)]
        def freccia(v, col, w=3, op=1.0):
            fine = img(v)
            if np.linalg.norm(fine) < 1e-3:  # λ = 0: il vettore collassa nell'origine
                return Dot(ORIGIN, radius=0.07, color=col).set_opacity(op)
            a = Arrow(ORIGIN, fine, buff=0, color=col, stroke_width=w,
                      max_tip_length_to_length_ratio=0.18, tip_length=0.18)
            a.set_stroke(opacity=op)
            a.tip.set_fill(opacity=op).set_stroke(opacity=op)  # anche la punta si attenua
            return a
        opacita_rosa = ValueTracker(1.0)
        rosa = VGroup(*[always_redraw(lambda v=v: freccia(v, C_ACCENTO, 3, opacita_rosa.get_value()))
                        for v in dirs])
        did = cambia_didascalia(self, None, "Ogni freccia è un vettore del piano")
        self.play(LaggedStart(*[GrowArrow(f) for f in rosa], lag_ratio=0.05), run_time=1.2)
        self.bring_to_front(tit, mat, did)

        did = cambia_didascalia(self, did, "Applico A: il piano si deforma")
        self.play(t.animate.set_value(1), run_time=3)
        did = cambia_didascalia(self, did, "Quasi ogni freccia cambia direzione...")
        self.wait(1.5)
        self.play(t.animate.set_value(0), run_time=1.5)

        # ---------- rette degli autovettori ----------
        colori = [C_B, C_C]
        rette, frecce_auto, etichette = VGroup(), VGroup(), VGroup()
        for k in range(2):
            v = vecs[:, k] / np.linalg.norm(vecs[:, k]) * L0
            d = np.array([v[0], v[1], 0.0]) / L0
            rette.add(DashedLine(-9 * d, 9 * d, color=colori[k], stroke_width=3, dash_length=0.15))
            frecce_auto.add(always_redraw(lambda v=v, c=colori[k]: freccia(v, c, 7)))
            lam = vals[k]
            def etichetta(v=v, c=colori[k], lam=lam, k=k):
                e = MathTex(rf"\times {fmt(lam)}", color=c, font_size=44)
                p = img(v)
                direz = p / (np.linalg.norm(p) + 1e-9)
                e.move_to(p + direz * 0.45 + np.array([-direz[1], direz[0], 0]) * 0.35)
                return e.add_background_rectangle(opacity=0.8, buff=0.06)
            etichette.add(always_redraw(etichetta))

        did = cambia_didascalia(self, did, "...except those on the dashed lines")
        self.play(opacita_rosa.animate.set_value(0.25), Create(rette), run_time=1)
        self.play(*[GrowArrow(f) for f in frecce_auto], run_time=0.8)
        self.bring_to_front(tit, mat, did)
        self.wait(0.5)

        self.play(t.animate.set_value(1), run_time=3)
        self.play(FadeIn(etichette), run_time=0.5)
        self.bring_to_front(tit, mat, did)
        did = cambia_didascalia(self, did, "Lì A allunga soltanto: il fattore è λ", colore=C_ACCENTO)
        self.wait(2)

        # ---------- risultato ----------
        r = (rf"\lambda_1 = {fmt(vals[0])},\ \vec v_1 = {fmt_vec(vecs[:, 0])}"
             rf"\qquad \lambda_2 = {fmt(vals[1])},\ \vec v_2 = {fmt_vec(vecs[:, 1])}")
        risultato_angolo(self, r, did)
