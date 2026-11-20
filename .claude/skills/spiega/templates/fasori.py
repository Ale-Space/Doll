"""TEMPLATE FASORI (Elettrotecnica / Fisica II): RLC serie in regime sinusoidale.

Esempio: R = 10 Ω, L = 50 mH, C = 100 µF, V_m = 10 V (ampiezza), f = 50 Hz.
  X_L = ωL = 15,71 Ω, X_C = 1/(ωC) = 31,83 Ω, |Z| = 18,97 Ω,
  φ = arg Z = arctan((X_L - X_C)/R) = -58,2°  (I in anticipo su V: capacitivo)
  risonanza f_0 = 1/(2π√(LC)) = 71,2 Hz: X_L = X_C, V_L = V_C = 22,4 V, I = 1 A.
Cosa si vede (≈38 s, niente passaggi: i conti vanno in chat):
  1. a sinistra i fasori V_R, V_L, V_C, V (dall'origine) e I (altra scala) che
     ruotano insieme; a destra le loro proiezioni verticali tracciano le sinusoidi
     (storia campionata frame per frame: si vede la curva "uscire" dalla freccia);
  2. la somma testa-coda tratteggiata: V = V_R + V_L + V_C;
  3. l'arco φ tra I e V;
  4. f sale fino a f_0 (ValueTracker): V_L e V_C diventano uguali e opposti,
     V = V_R, φ -> 0.
La velocità di rotazione sullo schermo è fissa (un giro ogni PERIODO_VIS s):
il tempo è "normalizzato al periodo", anche quando f cambia.

Per un altro circuito cambia `tensioni(f)`: restituisce i fasori complessi (in V)
dei componenti e del totale. Conti esatti con SymPy prima di scrivere i numeri.
Scala: K volt -> unità; controlla che il fasore più lungo (anche alla fine) stia
nel cerchio di raggio ~2,2 attorno a OP.

Altre idee:
  - TRIFASE: tre fasori a 120° che ruotano, a destra le tre sinusoidi; la somma
    (stella equilibrata) resta 0; tensioni concatenate V_12 = V_1 - V_2 (√3 volte,
    +30°) disegnate testa-coda. Squilibrio: un carico cambia e il centro stella si sposta.
  - TRIANGOLO DELLE POTENZE: P sull'asse reale, Q verticale, S ipotenusa;
    ValueTracker su φ (o su un condensatore di rifasamento): Q si accorcia,
    cos φ letto in diretta verso 0,9.
  - FILTRO RC: ValueTracker su f; a sinistra V_C e V_R (sempre a 90° tra loro,
    la punta di V_R corre su una semicirconferenza: il "cerchio di Thales"),
    a destra il diagramma di Bode |H| e fase che si disegnano col punto che scorre;
    a f = 1/(2πRC) modulo 1/√2 e fase -45°.
  - FISICA II, corrente alternata: stesso meccanismo per un solo componente
    (L: corrente in ritardo di 90°, C: in anticipo), oppure la potenza istantanea
    p(t) = v(t)i(t) tracciata come terza curva, con valor medio tratteggiato.
"""
from doll_kit import *  # noqa: F401  (render.sh mette kit/ nel PYTHONPATH)
import numpy as np

TITOLO = "Fasori nel circuito RLC"
R_, L_, C_, VM = 10.0, 50e-3, 100e-6, 10.0
F_INIZIO = 50.0
F0 = 1 / (2 * np.pi * np.sqrt(L_ * C_))      # 71,18 Hz (verificato con SymPy)

K = 0.088          # unità Manim per volt
KI = 1.5           # unità Manim per ampere (I ha la sua scala)
OP = np.array([-4.1, -0.5, 0.0])   # origine del diagramma dei fasori
X0, X1 = -1.3, 6.4                 # finestra delle sinusoidi (X0 = "adesso")
PERIODO_VIS = 4.0                  # secondi per giro sullo schermo
OMEGA_VIS = TAU / PERIODO_VIS
VEL = 1.1                          # unità/s con cui le curve scorrono a destra


def corrente(f):
    w = 2 * np.pi * f
    Z = R_ + 1j * (w * L_ - 1 / (w * C_))
    return VM / Z


def tensioni(f):
    """Fasori (complessi, in volt) con V come riferimento di fase."""
    w = 2 * np.pi * f
    I = corrente(f)
    return {"V_R": R_ * I, "V_L": 1j * w * L_ * I, "V_C": -1j / (w * C_) * I, "V": VM + 0j}


COL = {"V_R": GREEN_C, "V_L": BLUE_C, "V_C": RED_C, "V": YELLOW, "I": WHITE}
SPESSORE = {"V_R": 4, "V_L": 4, "V_C": 4, "V": 6}


def virgola(x, cifre=1):
    return f"{x:.{cifre}f}".replace(".", "{,}")


class Esercizio(Scene):
    def construct(self):
        tit = titolo(self, TITOLO)
        dat = dati(self, r"R = 10\,\Omega,\quad L = 50\,\mathrm{mH} \\ C = 100\,\mu\mathrm{F},\quad V_m = 10\,\mathrm{V}",
                   font_size=32)

        f = ValueTracker(F_INIZIO)
        orologio = ValueTracker(0.0)      # tempo "visivo" (s)
        vel = ValueTracker(0.0)           # 0 = fermo, 1 = ruota
        orologio.add_updater(lambda m, dt: m.increment_value(dt * vel.get_value()))
        self.add(orologio)

        def theta():
            return OMEGA_VIS * orologio.get_value()

        def punta(z: complex, scala=K) -> np.ndarray:
            w = z * np.exp(1j * theta())
            return OP + scala * np.array([w.real, w.imag, 0.0])

        # ---------- assi ----------
        cerchio = Circle(radius=VM * K, color=C_TENUE, stroke_width=1.5, stroke_opacity=0.5).move_to(OP)
        assi_f = VGroup(Line(OP + LEFT * 2.3, OP + RIGHT * 2.3), Line(OP + DOWN * 2.3, OP + UP * 2.3)).set_stroke(C_TENUE, 1.5, 0.5)
        # asse senza freccia e senza "t": la curva esce da X0 e scorre a destra, quindi
        # verso destra ci sono istanti PASSATI (una freccia "t ->" farebbe leggere male gli anticipi)
        asse_t = Line(np.array([X0, OP[1], 0]), np.array([X1 + 0.1, OP[1], 0]), stroke_width=2, color=C_TENUE)
        asse_v = Line(np.array([X0, OP[1] - 2.3, 0]), np.array([X0, OP[1] + 2.3, 0]), stroke_width=1.5, color=C_TENUE)
        self.play(Create(assi_f), Create(cerchio), Create(asse_t), Create(asse_v), run_time=1)

        # ---------- fasori ----------
        def freccia(nome):
            z = tensioni(f.get_value())[nome]
            a, b = OP, punta(z)
            if np.linalg.norm(b - a) < 0.05:
                return VMobject()
            return Arrow(a, b, buff=0, color=COL[nome], stroke_width=SPESSORE[nome],
                         max_tip_length_to_length_ratio=0.25, tip_length=0.22)
        def etichetta(nome):
            z = tensioni(f.get_value())[nome]
            b = punta(z)
            d = (b - OP) / (np.linalg.norm(b - OP) + 1e-9)
            perp = np.array([-d[1], d[0], 0.0])
            lato = {"V_R": -0.25, "V": 0.25}.get(nome, 0.0)  # V_R e V possono coincidere
            return MathTex(nome, font_size=30, color=COL[nome]).move_to(b + 0.3 * d + lato * perp)
        nomi = ["V_R", "V_L", "V_C", "V"]
        frecce = VGroup(*[always_redraw(lambda n=n: freccia(n)) for n in nomi])
        etichette = VGroup(*[always_redraw(lambda n=n: etichetta(n)) for n in nomi])
        frecciaI = always_redraw(lambda: Arrow(OP, punta(corrente(f.get_value()), KI), buff=0, color=COL["I"],
                                               stroke_width=2.5, max_tip_length_to_length_ratio=0.15, tip_length=0.18))
        etI = always_redraw(lambda: MathTex("I", font_size=30, color=COL["I"]).next_to(
            punta(corrente(f.get_value()), KI), normalize(punta(corrente(f.get_value()), KI) - OP), buff=0.12))

        did = cambia_didascalia(self, None, "Ogni tensione è una freccia: un fasore")
        self.play(*[GrowArrow(a) for a in frecce], FadeIn(etichette), run_time=1.2)
        self.play(GrowArrow(frecciaI), FadeIn(etI), run_time=0.6)
        self.bring_to_front(tit, dat, did)

        # ---------- proiezioni e sinusoidi ----------
        storia = {n: [] for n in nomi}
        def proiezione_y(n):
            return punta(tensioni(f.get_value())[n])[1]
        def aggiorna_tracce(m):
            tau = orologio.get_value()
            nuove = VGroup()
            for n in nomi:
                h = storia[n]
                if not h or tau - h[-1][0] > 1e-3:
                    h.append((tau, proiezione_y(n)))
                while h and X0 + VEL * (tau - h[0][0]) > X1:
                    h.pop(0)
                if len(h) >= 2:
                    pts = [np.array([X0 + VEL * (tau - a), y, 0]) for a, y in reversed(h)]
                    nuove.add(VMobject().set_points_smoothly(pts).set_stroke(COL[n], SPESSORE[n] - 1))
            m.become(nuove)
        tracce = VGroup()
        tracce.add_updater(aggiorna_tracce)
        proiez = always_redraw(lambda: VGroup(*[
            Line(punta(tensioni(f.get_value())[n]), np.array([X0, proiezione_y(n), 0]),
                 stroke_width=1.2, color=COL[n], stroke_opacity=0.45)
            for n in nomi]))
        self.add(tracce)
        self.play(FadeIn(proiez), run_time=0.4)
        did = cambia_didascalia(self, did, "Ruotano: l'altezza della punta traccia la sinusoide")
        self.play(vel.animate.set_value(1), run_time=1)
        self.wait(2.5)
        self.wait(2)

        # ---------- somma testa-coda ----------
        def catena():
            tv = tensioni(f.get_value())
            a = punta(0)
            b = punta(tv["V_R"])
            c = punta(tv["V_R"] + tv["V_L"])
            d = punta(tv["V_R"] + tv["V_L"] + tv["V_C"])
            return VGroup(DashedLine(b, c, color=COL["V_L"], dash_length=0.08, stroke_width=2.5),
                          DashedLine(c, d, color=COL["V_C"], dash_length=0.08, stroke_width=2.5))
        cat = always_redraw(catena)
        did = cambia_didascalia(self, did, "Testa-coda: le tre frecce sommate danno V")
        self.play(FadeIn(cat), run_time=0.6)
        self.wait(2.5)

        # ---------- sfasamento φ ----------
        def arco():
            phi = np.angle(corrente(f.get_value()))  # = -arg Z  (V ha fase 0)
            if abs(phi) < 0.02:
                return VMobject()
            return Arc(radius=0.55, start_angle=theta(), angle=phi, arc_center=OP, color=C_ACCENTO, stroke_width=4)
        arc = always_redraw(arco)
        def lettura():
            phi_deg = np.degrees(np.angle(tensioni(f.get_value())["V"] / corrente(f.get_value())))  # arg Z
            phi_deg = 0.0 if abs(phi_deg) < 0.05 else phi_deg
            return VGroup(
                MathTex(rf"f = {virgola(f.get_value())}\ \mathrm{{Hz}}", font_size=34),
                MathTex(rf"\varphi = {virgola(phi_deg)}^\circ", font_size=34, color=C_ACCENTO),
            ).arrange(RIGHT, buff=0.5).move_to(np.array([-3.9, 2.45, 0])).add_background_rectangle(opacity=0.85, buff=0.1)
        lett = always_redraw(lettura)
        did = cambia_didascalia(self, did, "I in anticipo su V: carico capacitivo")
        self.play(FadeIn(arc), FadeIn(lett), run_time=0.6)
        self.bring_to_front(tit, dat, did)
        self.wait(2.5)

        # ---------- verso la risonanza ----------
        did = cambia_didascalia(self, did, "Aumento f fino alla risonanza")
        self.play(f.animate.set_value(F0), run_time=5, rate_func=smooth)
        did = cambia_didascalia(self, did, "Le frecce di L e C si annullano", colore=C_ACCENTO)
        self.wait(2.5)
        did = cambia_didascalia(self, did, "Risonanza: tutta la tensione è su R, φ = 0")
        self.wait(2.5)

        risultato_angolo(self, r"f_0 = \frac{1}{2\pi\sqrt{LC}} \approx 71{,}2\ \mathrm{Hz}"
                               r"\qquad \varphi(50\ \mathrm{Hz}) \approx -58{,}2^\circ", did, attesa=2.5)
