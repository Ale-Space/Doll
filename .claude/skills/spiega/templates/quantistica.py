"""TEMPLATE QUANTISTICA (Fisica moderna, Meccanica quantistica, Quantum computing): il qubit sulla sfera
di Bloch, con la dinamica calcolata da QuTiP (sesolve) e la freccia che si muove dal vivo.

Frase wow: lo stato ruota SEMPRE attorno al campo efficace; arriva a |1> solo se quel campo è
           perpendicolare a z, cioè in risonanza.
Gesto visivo: la freccia di Bloch che gira attorno a un asse (tratteggiato); cambia solo l'asse.
Esempio concreto: spin di un elettrone in B = 0,1 T (gamma/2pi = 28,0 GHz/T).
  1. Larmor: H = (hbar w0/2) sigma_z, f0 = w0/2pi = 2,80 GHz, periodo 0,357 ns.
     Stato iniziale a theta = 60 gradi (phi = 0): P1 = sin^2(theta/2) = 0,25 COSTANTE, la freccia precede
     attorno a z (1,5 giri = 0,536 ns).
  2. Rabi, nel sistema rotante a w0, campo risonante lungo x: H = (hbar/2)(Delta sigma_z + Omega sigma_x),
     Omega/2pi = 10 MHz, Delta = 0. Da |0>: P1(t) = sin^2(Omega t/2); impulso pi a t = 50 ns: P1 = 1.
     Si prosegue fino a 100 ns (di nuovo |0>).
  3. Controesempio, fuori risonanza Delta = Omega: asse efficace inclinato di 45 gradi,
     Omega' = sqrt(Omega^2 + Delta^2) = sqrt(2) Omega, P1 max = Omega^2/Omega'^2 = 0,5 a t = 35,4 ns
     (due giri: 0 -> 141,4 ns).
Numeri verificati (QuTiP 5.3.1, sesolve, confronto con le formule sopra: errore massimo < 1e-6;
lo stampa `python quantistica.py`).
Convenzioni: |0> = polo nord (autostato +1 di sigma_z, basis(2, 0) di QuTiP), vettore di Bloch
(<sx>, <sy>, <sz>), P1 = (1 - <sz>)/2. Tempi in ns, pulsazioni in rad/ns, hbar = 1.

Atti: 0 titolo e H; 1 sfera, assi, |0> e |1>, la freccia; 2 Larmor (P1 ferma), poi sistema rotante e
Rabi (P1 sale); 3 impulso pi: slogan; 4 fuori risonanza: stesso gesto, non arriva a |1>; 5 risultato.
Pannello a destra (fisso): t dal vivo, P1 dal vivo e il grafico P1(t) che si disegna.

COME ADATTARLO
- Un altro hamiltoniano: cambia `traiettoria(H, psi0, T)` nelle FASI (qualunque Qobj 2x2 di QuTiP);
  il resto (freccia, scia, asse, grafico) segue da solo. Asse efficace: versore di (Omega, 0, Delta).
- Decoerenza (T1, T2): usa qutip.mesolve con c_ops=[sqrt(1/T1)*destroy(2), sqrt(1/(2*T2))*sigmaz()]:
  la freccia si accorcia verso il centro (stato misto). Nota: in QuTiP destroy(2) porta |1> -> |0>,
  cioè dal polo sud al nord con la convenzione di qui.
- Altre idee: porte logiche come rotazioni (H, X, S, T: la freccia salta tra i poli e l'equatore),
  eco di spin (impulso pi a metà: le scie di spin con Delta diversi si riallineano), Ramsey (pi/2,
  attesa, pi/2: frange in P1 al variare di Delta), misura (la freccia "cade" su un polo con probabilità P1).
Render:  .claude/skills/spiega/scripts/render.sh "$P/scena.py" bozza   (ThreeDScene: bozza ~1-2 min)
"""
from doll_kit import *  # noqa: F401,F403  (render.sh mette kit/ nel PYTHONPATH)
import numpy as np
import qutip as qt

TITOLO = "Qubit sulla sfera di Bloch"

# ---------------------------------------------------------------- fisica (QuTiP)
F0 = 2.80                         # GHz: elettrone in B = 0,1 T
W0 = 2 * np.pi * F0               # rad/ns
OM = 2 * np.pi * 0.010            # Omega: 10 MHz di Rabi, in rad/ns
TH0 = np.radians(60)              # stato iniziale della precessione
SX, SY, SZ = qt.sigmax(), qt.sigmay(), qt.sigmaz()


def traiettoria(H, psi0, T, n=900):
    """Vettore di Bloch (n, 3) e tempi (n,) da sesolve: (<sx>, <sy>, <sz>)."""
    t = np.linspace(0, T, n)
    r = qt.sesolve(H, psi0, t, e_ops=[SX, SY, SZ], options={"atol": 1e-10, "rtol": 1e-8})
    return t, np.column_stack([np.real(e) for e in r.expect])


ZERO = qt.basis(2, 0)
PSI_L = (np.cos(TH0 / 2) * qt.basis(2, 0) + np.sin(TH0 / 2) * qt.basis(2, 1)).unit()
T_L = 1.5 / F0                                     # 1,5 giri di Larmor: 0,536 ns
T_R = 2 * np.pi / OM                               # un ciclo di Rabi: 100 ns
OMP = np.sqrt(2) * OM                              # Omega' fuori risonanza (Delta = Omega)
T_D = 2 * 2 * np.pi / OMP                          # due cicli: 141,4 ns
FASI = {
    "larmor": traiettoria(0.5 * W0 * SZ, PSI_L, T_L),
    "rabi": traiettoria(0.5 * OM * SX, ZERO, T_R),
    "fuori": traiettoria(0.5 * (OM * SZ + OM * SX), ZERO, T_D),
}
ASSE = {"larmor": np.array([0, 0, 1.0]), "rabi": np.array([1.0, 0, 0]),
        "fuori": np.array([1.0, 0, 1.0]) / np.sqrt(2)}


def verifica():
    """Confronto QuTiP / formule chiuse (per il docstring)."""
    t, v = FASI["larmor"]
    e1 = np.max(np.abs((1 - v[:, 2]) / 2 - np.sin(TH0 / 2) ** 2))
    t, v = FASI["rabi"]
    e2 = np.max(np.abs((1 - v[:, 2]) / 2 - np.sin(OM * t / 2) ** 2))
    t, v = FASI["fuori"]
    e3 = np.max(np.abs((1 - v[:, 2]) / 2 - 0.5 * np.sin(OMP * t / 2) ** 2))
    print(f"errore max P1: Larmor {e1:.1e}, Rabi {e2:.1e}, fuori risonanza {e3:.1e}")
    print(f"P1 Larmor = {np.sin(TH0 / 2) ** 2:.4f};  impulso pi a {np.pi / OM:.2f} ns;  "
          f"fuori risonanza max {0.5:.2f} a {np.pi / OMP:.2f} ns;  T_L = {T_L:.4f} ns")


# ---------------------------------------------------------------- impaginazione
R = 2.25                                           # raggio della sfera sullo schermo
PHI, THETA = 68 * DEGREES, -128 * DEGREES          # camera: x verso chi guarda (a sinistra), y a destra
DESTRA = np.array([-np.sin(THETA), np.cos(THETA), 0.0])   # direzione "destra dello schermo" nel mondo
O = -1.55 * DESTRA                                 # centro della sfera: un po' a sinistra (pannello a destra)
GX0, GX1, GY0, GY1 = 3.55, 6.35, -2.55, -0.75      # riquadro del grafico P1(t) (coordinate dello schermo)


def W(v):
    """Punto del mondo per un vettore di Bloch v (|v| <= 1)."""
    return O + R * np.asarray(v, dtype=float)


class Esercizio(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=PHI, theta=THETA)
        stato = {"fase": "larmor", "da": None, "storia": []}
        tt = ValueTracker(0.0)                     # tempo fisico (ns) della fase corrente
        mix = ValueTracker(1.0)                    # 0 -> 1: passaggio da stato["da"] al polo nord

        def vettore():
            if stato["da"] is not None and mix.get_value() < 1:        # passaggio morbido (geodetica)
                a, b, s = stato["da"], np.array([0, 0, 1.0]), mix.get_value()
                om = np.arccos(np.clip(a @ b, -1, 1))
                return a if om < 1e-6 else (np.sin((1 - s) * om) * a + np.sin(s * om) * b) / np.sin(om)
            t, v = FASI[stato["fase"]]
            x = tt.get_value()
            return np.array([np.interp(x, t, v[:, k]) for k in range(3)])

        def p1():
            return (1 - vettore()[2]) / 2

        # ---------------- ATTO 0: apertura ----------------
        tit = titolo(self, TITOLO)
        dat = dati(self, r"H = \frac{\hbar\omega_0}{2}\,\sigma_z \qquad P_1 = \frac{1 - \langle\sigma_z\rangle}{2}",
                   font_size=32)

        # ---------------- ATTO 1: la sfera e lo stato ----------------
        sfera = Sphere(center=O, radius=R, resolution=(24, 12), fill_opacity=0.10, checkerboard_colors=False,
                       fill_color=C_OGGETTO, stroke_color=C_OGGETTO, stroke_width=0.4, stroke_opacity=0.35)
        u = np.linspace(0, TAU, 120)
        equatore = curva([W((np.cos(a), np.sin(a), 0)) for a in u], colore=C_TENUE, spessore=1.5)
        meridiano = curva([W((np.sin(a), 0, np.cos(a))) for a in u], colore=C_TENUE, spessore=1.2)
        assi = VGroup(*[DashedLine(W(-1.18 * e), W(1.18 * e), color=C_TENUE, stroke_width=1.5, dash_length=0.1)
                        for e in np.eye(3)])
        nomi = VGroup(*[self.orientato_(MathTex(n, font_size=30, color=C_TENUE)).move_to(W(1.3 * e))
                        for n, e in zip("xyz", np.eye(3))])
        ket0 = self.orientato_(MathTex(r"|0\rangle", font_size=36)).move_to(W((0, 0, 1)) + np.array([0, 0, 0.75]) + 0.55 * DESTRA)
        ket1 = self.orientato_(MathTex(r"|1\rangle", font_size=36)).move_to(W((0, 0, -1)) + np.array([0, 0, -0.45]) + 0.55 * DESTRA)
        did = cambia_didascalia(self, None, "Lo stato del qubit è una freccia")
        self.play(FadeIn(sfera), Create(equatore), Create(meridiano), Create(assi), run_time=1.0)
        self.play(FadeIn(nomi), FadeIn(ket0), FadeIn(ket1), run_time=0.6)

        freccia = Line(W((0, 0, 0)), W(vettore()), color=C_RIF, stroke_width=6)
        freccia.add_updater(lambda m: m.put_start_and_end_on(W((0, 0, 0)), W(vettore())))
        punta = Dot3D(W(vettore()), radius=0.09, color=C_RIF)
        punta.add_updater(lambda m: m.move_to(W(vettore())))
        # altezza della punta: e' lei che da' P1 (tratteggio fino all'asse z)
        altezza = always_redraw(lambda: DashedLine(W(vettore()), W((0, 0, vettore()[2])), color=C_Y,
                                                   stroke_width=2.5, dash_length=0.08))
        piede = Dot3D(W((0, 0, vettore()[2])), radius=0.06, color=C_Y)
        piede.add_updater(lambda m: m.move_to(W((0, 0, vettore()[2]))))
        scia = VMobject(stroke_color=C_RIF, stroke_width=2.5, stroke_opacity=0.55)

        def agg_scia(m):
            stato["storia"].append(W(vettore()))
            pts = stato["storia"][-500:]
            if len(pts) > 1:
                m.set_points_as_corners(np.array(pts))
        scia.add_updater(agg_scia)
        self.play(Create(freccia), FadeIn(punta), run_time=0.8)
        self.add(scia, altezza, piede)

        # ---------------- pannello: t, P1 e il grafico P1(t) (fissi sullo schermo) ----------------
        def testo_t():
            x = tt.get_value()
            return "t = " + (virgola(x, 3) if stato["fase"] == "larmor" else virgola(x, 1)) + " ns"
        n_t = numero_vivo(self, testo_t, np.array([GX0, 0.55, 0]), colore=C_TENUE, size=24)
        n_p = numero_vivo(self, lambda: "P₁ = " + virgola(p1(), 2), np.array([GX0, 0.0, 0]), colore=C_Y, size=30)
        cornice = VGroup(Line([GX0, GY0, 0], [GX1, GY0, 0]), Line([GX0, GY0, 0], [GX0, GY1 + 0.15, 0]),
                         DashedLine([GX0, GY1, 0], [GX1, GY1, 0], dash_length=0.06)).set_stroke(C_TENUE, 1.5)
        et_g = VGroup(Text("1", font_size=20, color=C_TENUE).next_to([GX0, GY1, 0], LEFT, buff=0.1),
                      Text("0", font_size=20, color=C_TENUE).next_to([GX0, GY0, 0], LEFT, buff=0.1),
                      Text("t", font_size=22, color=C_TENUE, slant=ITALIC).next_to([GX1, GY0, 0], DOWN, buff=0.1),
                      Text("P₁", font_size=22, color=C_Y).next_to([GX0, GY1 + 0.15, 0], UP, buff=0.08))
        grafico = VMobject(stroke_color=C_Y, stroke_width=3)
        punti_g = []

        def agg_grafico(m):
            t, _ = FASI[stato["fase"]]
            x = GX0 + (GX1 - GX0) * tt.get_value() / t[-1]
            if not punti_g or x > punti_g[-1][0] + 1e-3 or x < punti_g[-1][0] - 1e-3:
                punti_g.append(np.array([x, GY0 + (GY1 - GY0) * p1(), 0]))
            if len(punti_g) > 1:
                m.set_points_as_corners(np.array(punti_g))
        self.add_fixed_in_frame_mobjects(cornice, et_g, grafico)
        self.remove(cornice, et_g, grafico)
        self.play(FadeIn(n_t), FadeIn(n_p), Create(cornice), FadeIn(et_g), run_time=0.6)
        grafico.add_updater(agg_grafico)
        self.add(grafico)
        self.add(tt)

        def asse_tratteggiato(fase, colore):
            e = ASSE[fase]
            return VGroup(DashedLine(W(-1.4 * e), W(1.4 * e), color=colore, stroke_width=4, dash_length=0.14))

        # ---------------- ATTO 2a: precessione di Larmor ----------------
        campo = asse_tratteggiato("larmor", C_CAMPO)
        lab_b = self.orientato_(MathTex(r"\vec B", font_size=34, color=C_CAMPO)).move_to(W((0, 0, 1.45)) - 0.45 * DESTRA)
        did = cambia_didascalia(self, did, "Campo lungo z: la freccia precede")
        self.play(Create(campo), FadeIn(lab_b), run_time=0.6)
        self.play(tt.animate.set_value(T_L * 0.55), run_time=2.6, rate_func=linear)
        did = cambia_didascalia(self, did, "L'altezza non cambia: P₁ resta 0,25")
        self.play(tt.animate.set_value(T_L), run_time=2.2, rate_func=linear)

        # ---------------- ATTO 2b: sistema rotante, risonanza: Rabi ----------------
        stato["da"] = vettore()
        mix.set_value(0.0)
        self.add(mix)
        nuovo = asse_tratteggiato("rabi", C_CAMPO)
        lab_b1 = self.orientato_(MathTex(r"\vec B_1", font_size=34, color=C_CAMPO)).move_to(W((1.5, 0, 0)) + np.array([0, 0, 0.3]))
        did = cambia_didascalia(self, did, "Sistema rotante: campo risonante lungo x")
        stato["storia"].clear()
        self.play(mix.animate.set_value(1.0), ReplacementTransform(campo, nuovo), ReplacementTransform(lab_b, lab_b1),
                  run_time=1.2, rate_func=smooth)
        campo, lab_b = nuovo, lab_b1
        stato.update(fase="rabi", da=None, storia=[])
        tt.set_value(0.0)
        punti_g.clear()
        did = cambia_didascalia(self, did, "Ruota attorno a x: scende verso |1⟩")
        self.play(tt.animate.set_value(T_R * 0.5), run_time=3.2, rate_func=linear)

        # ---------------- ATTO 3: impulso pi ----------------
        did = cambia_didascalia(self, did, "Impulso π: |0⟩ diventa |1⟩", colore=C_ACCENTO)
        self.play(Indicate(punta, color=C_ACCENTO, scale_factor=1.6), run_time=0.9)
        self.play(tt.animate.set_value(T_R), run_time=2.6, rate_func=linear)

        # ---------------- ATTO 4: fuori risonanza (stesso gesto, asse inclinato) ----------------
        nuovo = asse_tratteggiato("fuori", C_CONTRO)
        lab_n = self.orientato_(MathTex(r"\Omega'", font_size=34, color=C_CONTRO)).move_to(W(1.55 * ASSE["fuori"]))
        did = cambia_didascalia(self, did, "Fuori risonanza: l'asse si inclina")
        stato.update(fase="fuori", storia=[])
        tt.set_value(0.0)
        punti_g.clear()
        self.play(ReplacementTransform(campo, nuovo), ReplacementTransform(lab_b, lab_n), run_time=0.9)
        campo = nuovo
        self.play(tt.animate.set_value(T_D * 0.5), run_time=3.0, rate_func=linear)
        did = cambia_didascalia(self, did, "Non arriva mai a |1⟩: massimo 0,5", colore=C_CONTRO)
        self.play(tt.animate.set_value(T_D), run_time=3.0, rate_func=linear)

        # ---------------- ATTO 5: risultato ----------------
        for m in (freccia, punta, piede, scia, grafico):
            m.clear_updaters()
        risultato_angolo(self, r"P_1(t) = \frac{\Omega^2}{\Omega^2+\Delta^2}\,"
                               r"\sin^2\!\left(\frac{\sqrt{\Omega^2+\Delta^2}}{2}\,t\right)", did, attesa=2.2,
                         posizione=RIGHT * 3.85 + UP * 1.8)   # in alto a destra: non copre la sfera

    def orientato_(self, m):
        """Etichetta 3D sempre rivolta alla camera (kit: orientato)."""
        return orientato(self, m)


if __name__ == "__main__":
    verifica()
